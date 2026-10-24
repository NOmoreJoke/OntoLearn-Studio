"""Private immutable source cache evidence, not transport/parser authorization."""

import copy
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project import format3
from ontolearn_engine.project import source_content as source
from ontolearn_engine.storage import canonical, digest
from test_job_store import CONTRACT


def logical(path):
    with sqlite3.connect(path) as con:
        return format3.logical_hash(con)


def formal_state(store):
    tables = [
        r[0]
        for r in store._db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name!='job_blobs' ORDER BY name"
        )
    ]
    return {
        table: sorted([tuple(r) for r in store._db.execute(f'SELECT * FROM "{table}"')], key=repr)
        for table in tables
    }


@pytest.fixture(params=[2, 3])
def store(tmp_path, request):
    s = JobStore(tmp_path / "source.sqlite", contract=CONTRACT, target_format=request.param)
    s.create_project("p")
    s.project = s.public_project("p")
    yield s
    s.close()


@pytest.mark.parametrize("length", [0, 1, 65535, 65536, 65537, 131073, source.MAX_SOURCE_BYTES])
def test_exact_binary_snapshot_boundaries_and_reopen(store, length):
    raw = (bytes(range(256)) * ((length + 255) // 256))[:length]
    before = formal_state(store)
    manifest, chunks = source.plan_content(raw)
    ref = source.intern_content(store, store.project, raw)
    assert ref == digest(manifest) and ref != source.sha256(raw)
    assert store.blob(store.project, ref) == manifest
    assert source.read_content(store, store.project, ref) == raw
    assert len(chunks) == (length + source.CHUNK_BYTES - 1) // source.CHUNK_BYTES
    assert all(CONTRACT.encoded_size(c) < source.MAX_BLOB_BYTES for c in chunks)
    assert formal_state(store) == before
    persisted = logical(store.path)
    assert source.intern_content(store, store.project, raw) == ref
    assert logical(store.path) == persisted
    manifest["sha256"] = "0" * 64  # detached return is not authority
    assert source.read_content(store, store.project, ref) == raw
    path, project, target = store.path, store.project, store.actual_format
    store.close()
    reopened = JobStore(path, contract=CONTRACT, target_format=target)
    try:
        assert source.read_content(reopened, project, ref) == raw
        assert formal_state(reopened) == before
    finally:
        reopened.close()


@pytest.mark.parametrize(
    "raw",
    [
        "bytes",
        bytearray(b"x"),
        None,
        pytest.param(b"x" * (source.MAX_SOURCE_BYTES + 1), id="oversized-source-bytes"),
    ],
)
def test_invalid_input_zero_writes(store, raw):
    before = logical(store.path)
    with pytest.raises(source.SourceContentFault):
        source.intern_content(store, store.project, raw)
    assert logical(store.path) == before


@pytest.mark.parametrize(
    "patch",
    [
        {"extra": 1},
        {"kind": "source-content"},
        {"version": True},
        {"ordinal": True},
        {"ordinal": 128},
        {"byteLength": True},
        {"byteLength": 0},
        {"byteLength": 65537},
        {"sha256": "A" * 64},
        {"sha256": "0" * 64},
        {"data": "eB=="},  # same decoded x but noncanonical pad bits
        {"data": "eA==\n"},
        {"data": "eA==="},
        {"data": "\ud800"},
        {"data": "A" * 87385},
    ],
)
def test_strict_chunk_encoding_and_hash(patch):
    payload = source.encode_chunk(b"x", 0)
    with pytest.raises(source.SourceContentFault):
        source.decode_chunk(payload | patch)


@pytest.mark.parametrize(
    "mutation",
    ["extra", "version", "length", "count", "ordinal", "ref", "chunkLength", "wholeHash"],
)
def test_invalid_manifest_or_false_whole_digest_rejected(store, mutation):
    raw = b"x" * 65537
    manifest, chunks = source.plan_content(raw)
    for chunk in chunks:
        store.put_blob(store.project, chunk)
    if mutation == "extra":
        manifest["path"] = "/never-open-this-path"
    elif mutation == "version":
        manifest["version"] = True
    elif mutation == "length":
        manifest["totalBytes"] = True
    elif mutation == "count":
        manifest["chunks"].pop()
    elif mutation == "ordinal":
        manifest["chunks"][0]["ordinal"] = True
    elif mutation == "ref":
        manifest["chunks"][1]["ref"] = manifest["chunks"][0]["ref"]
    elif mutation == "chunkLength":
        manifest["chunks"][0]["byteLength"] = 65535
    else:
        manifest["sha256"] = "0" * 64
    ref = store.put_blob(store.project, manifest)
    before = logical(store.path)
    with pytest.raises(source.SourceContentFault):
        source.read_content(store, store.project, ref)
    assert logical(store.path) == before


def test_member_binding_missing_chunk_and_cross_project(store):
    manifest, chunks = source.plan_content(b"x" * 65537)
    for chunk in chunks:
        store.put_blob(store.project, chunk)
    bad = copy.deepcopy(manifest)
    bad["chunks"][0]["sha256"] = "0" * 64
    ref = store.put_blob(store.project, bad)
    with pytest.raises(source.SourceContentFault):
        source.read_content(store, store.project, ref)
    missing = copy.deepcopy(manifest)
    missing["chunks"][1]["ref"] = "0" * 64
    ref = store.put_blob(store.project, missing)
    with pytest.raises(JobFault, match="NOT_FOUND"):
        source.read_content(store, store.project, ref)
    ref = source.intern_content(store, store.project, b"original")
    store.create_project("second")
    second = store.public_project("second")
    with pytest.raises(JobFault, match="NOT_FOUND"):
        source.read_content(store, second, ref)


@pytest.mark.parametrize("collision", ["chunk", "manifest"])
def test_preexisting_wrong_hash_payload_is_not_silently_reused(store, collision):
    manifest, chunks = source.plan_content(b"exact")
    expected = chunks[0] if collision == "chunk" else manifest
    # Deliberate cache corruption. Its existence must not turn INSERT OR IGNORE
    # into proof; an intern attempt must roll back every new cache member.
    store._db.execute(
        "INSERT INTO job_blobs VALUES(?,?,?)", (store.project, digest(expected), canonical({}))
    )
    before = logical(store.path)
    with pytest.raises(JobFault, match="INVALID_STATE"):
        source.intern_content(store, store.project, b"exact")
    assert logical(store.path) == before


PHASES = [
    "before",
    "source_chunk:0",
    "source_chunk:1",
    "source_chunk:2",
    "source_manifest",
    "before_commit",
    "after_commit",
]


@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_atomic_cache_faults_and_real_process_exit(tmp_path, phase, failure):
    path = tmp_path / "fault.sqlite"
    s = JobStore(path, contract=CONTRACT, target_format=3)
    s.create_project("p")
    project = s.public_project("p")
    formal = formal_state(s)
    before = logical(path)
    raw = b"b" * 131073
    ref = digest(source.plan_content(raw)[0])
    if failure == "exit":
        s.close()
        script = """
import os,sys
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project.source_content import intern_content
from ontolearn_engine.resources import CONTRACT
s=JobStore(sys.argv[1],contract=CONTRACT,target_format=3)
def hook(actual):
 if actual==sys.argv[3]: os._exit(79)
intern_content(s,sys.argv[2],b'b'*131073,hook)
raise AssertionError('fault not reached')
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), project, phase],
            cwd=Path(__file__).resolve().parents[3],
            env={k: v for k, v in os.environ.items() if not k.startswith("ONTOLEARN_")},
            capture_output=True,
            timeout=15,
        )
        assert result.returncode == 79
    else:
        error = {"exception": RuntimeError, "cancel": KeyboardInterrupt, "disk": OSError}[failure]
        seen = []

        def hook(actual):
            if actual == phase:
                seen.append(actual)
                raise error("synthetic fault")

        with pytest.raises(error):
            source.intern_content(s, project, raw, hook)
        assert seen == [phase]
        s.close()
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        assert formal_state(reopened) == formal
        if phase == "after_commit":
            assert source.read_content(reopened, project, ref) == raw
            committed = logical(path)
            assert source.intern_content(reopened, project, raw) == ref
            assert logical(path) == committed
        else:
            assert logical(path) == before
            with pytest.raises(JobFault, match="NOT_FOUND"):
                source.read_content(reopened, project, ref)
    finally:
        reopened.close()
