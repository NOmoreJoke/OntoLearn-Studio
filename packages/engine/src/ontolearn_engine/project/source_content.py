"""Private bounded source content in the existing immutable JobStore blob cache.

Content identities are not broker proofs, project grants or commit authority.
No public transport, parser, worker wiring, source upload or new writer exists
here. The limits below are private candidate limits pending wire acceptance.
"""

import base64
import binascii
import hashlib

from ontolearn_engine.storage import Hook, canonical, digest

CHUNK_BYTES = 65536
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_CHUNKS = MAX_SOURCE_BYTES // CHUNK_BYTES
MAX_BLOB_BYTES = 262144
CHUNK_KEYS = {"kind", "version", "ordinal", "byteLength", "sha256", "data"}
MANIFEST_KEYS = {"kind", "version", "totalBytes", "sha256", "chunks"}
MEMBER_KEYS = {"ordinal", "ref", "byteLength", "sha256"}


class SourceContentFault(ValueError):
    """Fixed private categories; never carries bytes, paths or raw exceptions."""

    def __init__(self, category):
        super().__init__("Invalid source content")
        self.category = category


def require(value, category="shape"):
    if not value:
        raise SourceContentFault(category)


def integer(value, maximum):
    return type(value) is int and 0 <= value <= maximum


def hash_ref(value):
    return (
        isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    )


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def encode_chunk(raw, ordinal):
    require(type(raw) is bytes and 1 <= len(raw) <= CHUNK_BYTES, "length")
    require(integer(ordinal, MAX_CHUNKS - 1))
    payload = {
        "kind": "source-chunk",
        "version": 1,
        "ordinal": ordinal,
        "byteLength": len(raw),
        "sha256": sha256(raw),
        "data": base64.b64encode(raw).decode("ascii"),
    }
    require(len(canonical(payload).encode("utf-8")) <= MAX_BLOB_BYTES, "length")
    return payload


def decode_chunk(payload):
    require(isinstance(payload, dict) and set(payload) == CHUNK_KEYS)
    require(payload["kind"] == "source-chunk" and type(payload["version"]) is int)
    require(payload["version"] == 1 and integer(payload["ordinal"], MAX_CHUNKS - 1))
    require(integer(payload["byteLength"], CHUNK_BYTES) and payload["byteLength"] > 0, "length")
    require(hash_ref(payload["sha256"]) and isinstance(payload["data"], str))
    # Bound before base64 allocation. Canonical encoding also excludes ignored
    # whitespace, non-ASCII, excess padding and alternate nonzero pad bits.
    require(len(payload["data"]) <= 4 * ((CHUNK_BYTES + 2) // 3), "length")
    try:
        raw = base64.b64decode(payload["data"], validate=True)
    except (ValueError, binascii.Error):
        raise SourceContentFault("encoding") from None
    require(base64.b64encode(raw).decode("ascii") == payload["data"], "encoding")
    require(len(raw) == payload["byteLength"], "length")
    require(sha256(raw) == payload["sha256"], "digest")
    return raw


def check_manifest(value):
    require(isinstance(value, dict) and set(value) == MANIFEST_KEYS)
    require(value["kind"] == "source-content" and type(value["version"]) is int)
    require(value["version"] == 1 and hash_ref(value["sha256"]))
    total = value["totalBytes"]
    require(integer(total, MAX_SOURCE_BYTES), "length")
    chunks = value["chunks"]
    count = (total + CHUNK_BYTES - 1) // CHUNK_BYTES
    require(isinstance(chunks, list) and len(chunks) == count, "length")
    refs = set()
    for ordinal, member in enumerate(chunks):
        require(isinstance(member, dict) and set(member) == MEMBER_KEYS)
        require(type(member["ordinal"]) is int and member["ordinal"] == ordinal)
        require(hash_ref(member["ref"]) and hash_ref(member["sha256"]))
        require(member["ref"] not in refs)
        refs.add(member["ref"])
        expected = min(CHUNK_BYTES, total - ordinal * CHUNK_BYTES)
        require(type(member["byteLength"]) is int and member["byteLength"] == expected, "length")
    require(len(canonical(value).encode("utf-8")) <= MAX_BLOB_BYTES, "length")


def plan_content(raw):
    """Pure deterministic typed payloads over exact bytes, without authority."""
    require(type(raw) is bytes and len(raw) <= MAX_SOURCE_BYTES, "length")
    payloads = [
        encode_chunk(raw[start : start + CHUNK_BYTES], ordinal)
        for ordinal, start in enumerate(range(0, len(raw), CHUNK_BYTES))
    ]
    manifest = {
        "kind": "source-content",
        "version": 1,
        "totalBytes": len(raw),
        "sha256": sha256(raw),
        "chunks": [
            {key: payload[key] for key in ("ordinal", "byteLength", "sha256")}
            | {"ref": digest(payload)}
            for payload in payloads
        ],
    }
    check_manifest(manifest)
    return manifest, payloads


def intern_content(store, project, raw, hook: Hook = lambda _: None):
    """Atomically intern cache material, not a formal project operation.

    Uses the original coordinator-owned blob API/connection and outer SQLite
    transaction. It does not allocate a grant, Job, claim, CAS or receipt. A
    caller must separately prove actual broker scope and user confirmation
    before any parser/Job/Store use; this private function cannot do that.
    """
    store._project(project)
    manifest, payloads = plan_content(raw)
    with store._transaction(hook):
        for payload, member in zip(payloads, manifest["chunks"], strict=True):
            require(store.put_blob(project, payload) == member["ref"], "digest")
            # INSERT OR IGNORE is not validation of a preexisting cache row.
            require(canonical(store.blob(project, member["ref"])) == canonical(payload), "digest")
            hook(f"source_chunk:{payload['ordinal']}")
        ref = store.put_blob(project, manifest)
        require(ref == digest(manifest), "digest")
        require(canonical(store.blob(project, ref)) == canonical(manifest), "digest")
        hook("source_manifest")
    return ref


def read_content(store, project, ref):
    """Read one consistent exact snapshot; verify all bytes before returning."""
    require(hash_ref(ref))
    store._project(project)
    with store._read():
        manifest = store.blob(project, ref)
        check_manifest(manifest)
        require(digest(manifest) == ref, "digest")
        chunks = []
        for member in manifest["chunks"]:
            payload = store.blob(project, member["ref"])
            raw = decode_chunk(payload)
            require(digest(payload) == member["ref"], "digest")
            require(
                all(payload[key] == member[key] for key in ("ordinal", "byteLength", "sha256")),
                "digest",
            )
            chunks.append(raw)
        raw = b"".join(chunks)
        require(len(raw) == manifest["totalBytes"], "length")
        require(sha256(raw) == manifest["sha256"], "digest")
        return raw
