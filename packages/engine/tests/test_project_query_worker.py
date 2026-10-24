"""Real finite query worker definitions, for the separately authorized test run.

Fixture writes use the existing Store writer; accepted immutable requests use
JobStore's real prepare branch. No executor, process, guard or network function
is replaced. This file does not establish production dispatcher/IPC authority.
Cancellation at the running notification is deterministic; it does not claim a
long native SPARQL evaluation can be interrupted at an arbitrary instruction.
"""

import asyncio
import hashlib
import json
import subprocess
from copy import deepcopy
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import Coordinator, worker_command
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.process_environment import worker_environment
from ontolearn_engine.resources import CONTRACT, LIMITS, semantic_identity
from ontolearn_engine.storage import digest
from ontolearn_engine.worker import (
    query_decode,
    query_encode,
    query_parts,
    query_transport_limits,
    worker_owner_arguments,
)

INTERNAL = "query-worker-fixture"
SELECT = "SELECT ?s ?v WHERE { ?s <urn:label> ?v } ORDER BY ?s"
ASK = 'ASK { <urn:a> <urn:label> "甲" }'
WORKER_TIMEOUT = 20


def uid():
    return str(uuid4())


def fact(subject, value):
    return {
        "id": digest([subject, "urn:label", value]),
        "subject": subject,
        "predicate": "urn:label",
        "object": value,
    }


@pytest.fixture
def store(tmp_path):
    value = JobStore(tmp_path / "query-worker.sqlite", contract=CONTRACT)
    value.create_project(INTERNAL)
    value.project = value.public_project(INTERNAL)
    yield value
    value.close()


def seed(store, text=SELECT):
    # Explicit writer fixture, not a new production import/seed API.
    store.commit(
        INTERNAL,
        store.revision(INTERNAL),
        uid(),
        uid(),
        definitions=[
            {
                "layer": "query",
                "id": "Q1",
                "value": {
                    "text": text,
                    "references": [],
                    "descriptor": {
                        "version": 1,
                        "name": "有限查询",
                        "description": "worker fixture",
                        "scope": "asserted",
                        "capabilityQuestion": "Which labels?",
                        "source": "editor",
                    },
                },
            }
        ],
        manual=[fact("urn:a", '"甲"'), fact("urn:b", '"beta"@en')],
    )
    return store.project_get(store.project)["inputSnapshotId"]


def accept(store, snapshot, selection="current", operation=None):
    input_ = {
        "inputSnapshotId": snapshot,
        "scope": "asserted",
        "definitionId": "Q1",
        "parametersHash": store.put_blob(store.project, {"inputSelection": selection}),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    return store.create_job(
        store.project,
        operation or uid(),
        "query.execute",
        input_,
        None,
        semantic_identity(),
        LIMITS,
    )


def wire(request):
    # A deliberately smaller legal private transport frame forces fragmentation.
    frame, maximum = query_transport_limits({**LIMITS, "maxFrameBytes": 4096})
    raw = query_encode(request, maximum)
    pieces = query_parts(raw, frame)
    header = {
        "capability": "query.execute",
        "memoryBytes": LIMITS["maxWorkerMemoryBytes"],
        "frameBytes": frame,
        "byteLimit": maximum,
        "parts": len(pieces),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    messages = [header, *({"index": i, "text": text} for i, text in enumerate(pieces))]
    return messages, frame, maximum


def encoded_messages(messages, frame):
    return b"".join(query_encode(message, frame) + b"\n" for message in messages)


def run_worker(raw):
    process = subprocess.Popen(
        [*worker_command(), *worker_owner_arguments()],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=worker_environment(),
    )
    try:
        stdout, stderr = process.communicate(raw, timeout=WORKER_TIMEOUT)
        assert type(process.returncode) is int
        # 73/74/75 are failures here, never swallowed as a skipped query test.
        return process.returncode, stdout, stderr
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()


def output_frames(raw, frame):
    assert raw and raw.endswith(b"\n")
    lines = raw.split(b"\n")[:-1]
    assert all(line and len(line) <= frame for line in lines)
    return [json.loads(line.decode("utf-8")) for line in lines]


def decode_success(raw, frame, maximum):
    frames = output_frames(raw, frame)
    assert frames[-1] == {"type": "complete"}
    done = frames[-2]
    assert set(done) == {"type", "parts", "bytes", "sha256"}
    assert done["type"] == "query.done"
    chunks = frames[:-2]
    assert chunks
    for index, chunk in enumerate(chunks):
        assert set(chunk) == {"type", "index", "text"}
        assert chunk["type"] == "query.chunk" and type(chunk["index"]) is int
        assert chunk["index"] == index and chunk["text"]
        assert len(chunk["text"]) <= (frame - 256) // 12
    encoded = "".join(chunk["text"] for chunk in chunks).encode("utf-8")
    assert type(done["parts"]) is int and done["parts"] == len(chunks)
    assert type(done["bytes"]) is int and done["bytes"] == len(encoded)
    assert done["sha256"] == hashlib.sha256(encoded).hexdigest()
    output = query_decode(encoded, maximum)
    assert set(output) == {"payload", "rows"}
    return output


def test_real_worker_fragmented_select_uses_accepted_snapshot_and_publishes(store):
    text = SELECT + "\n#" + "snapshot-原文 " * 160 + "end"
    snapshot = seed(store, text)
    job = accept(store, snapshot)
    accepted = deepcopy(store.job_context(job["jobId"])["queryRequest"])
    # Change the live project after acceptance. The child receives no DB path;
    # it must execute the original immutable material, not re-select live data.
    store.commit(
        INTERNAL, store.revision(INTERNAL), uid(), uid(), manual=[fact("urn:c", '"later"')]
    )
    messages, frame, maximum = wire(accepted)
    assert len(messages) > 2
    code, stdout, stderr = run_worker(encoded_messages(messages, frame))
    assert code == 0 and stderr == b""
    output = decode_success(stdout, frame, maximum)
    payload = output["payload"]
    assert payload["query"] == {
        "type": "SELECT",
        "variables": ["s", "v"],
        "rows": [["<urn:a>", '"甲"'], ["<urn:b>", '"beta"@en']],
    }
    assert payload["inputSnapshotId"] == snapshot
    assert payload["inputSelection"] == "current" and payload["queryText"] == text
    assert payload["inputProjectRevision"] == accepted["snapshot"]["projectRevision"]
    assert store.job_context(job["jobId"])["queryRequest"] == accepted
    store.start_job(job["jobId"])
    terminal = store.finish_query_job(job["jobId"], output)
    assert terminal["state"] == "succeeded" and terminal["error"] is None
    metadata, saved = store.semantic_result(store.project, terminal["resultRef"]["resultId"])
    assert saved == payload and metadata["inputSnapshotId"] == snapshot
    assert terminal["resultRef"]["inputSnapshotId"] == snapshot


async def execute_job(store, job, *, emit=lambda _: None, on_actor=lambda _: None):
    actor = Coordinator(store, test_mode=True, allowed_projects={store.project}, emit=emit)
    actor.version = 2
    actor.session = uid()
    actor.subscriptions[uid()] = {
        "projectId": store.project,
        "jobId": job["jobId"],
        "stateVersion": job["stateVersion"],
        "seq": 0,
    }
    try:
        on_actor(actor)
        actor.queued.append(job["jobId"])
        await actor.tick()
        await asyncio.wait_for(asyncio.gather(*tuple(actor.tasks)), timeout=WORKER_TIMEOUT)
        assert actor.active == {} and not actor.queued
        return store.get_job(store.project, job["jobId"])
    finally:
        await actor.stop()


@pytest.mark.parametrize("value", [True, False])
def test_real_coordinator_ask_true_and_false_keep_boolean(store, value):
    text = ASK if value else 'ASK { <urn:missing> <urn:label> "甲" }'
    snapshot = seed(store, text)
    terminal = asyncio.run(execute_job(store, accept(store, snapshot)))
    assert terminal["state"] == "succeeded" and terminal["error"] is None
    metadata, payload = store.semantic_result(store.project, terminal["resultRef"]["resultId"])
    assert payload["query"] == {"type": "ASK", "value": value}
    assert type(payload["query"]["value"]) is bool
    assert payload["queryText"] == text and metadata["inputSnapshotId"] == snapshot


def test_historical_input_is_explicit_and_current_cannot_accept_old_snapshot(store):
    old = seed(store, ASK)
    # Persisted old snapshot is supplied by the real prior writer, not forged.
    store.commit(
        INTERNAL,
        store.revision(INTERNAL),
        uid(),
        uid(),
        definitions=[
            {
                "layer": "query",
                "id": "Q1",
                "value": {
                    "text": "ASK { <urn:missing> ?p ?o }",
                    "references": [],
                },
            }
        ],
    )
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        accept(store, old, "current")
    job = accept(store, old, "historical")
    terminal = asyncio.run(execute_job(store, job))
    assert terminal["state"] == "succeeded", terminal
    _, payload = store.semantic_result(store.project, terminal["resultRef"]["resultId"])
    assert payload["query"] == {"type": "ASK", "value": True}
    assert payload["queryText"] == ASK and payload["inputSelection"] == "historical"
    assert payload["inputSnapshotId"] == old
    # Exact retry returns the original accepted Job, never another worker input.
    retry = store.create_job(
        store.project,
        job["operationId"],
        job["capability"],
        job["input"],
        None,
        job["implementation"],
        job["limits"],
    )
    assert retry == terminal


@pytest.mark.parametrize(
    "text,code,params",
    [
        (
            "SELECT * WHERE { SERVICE <https://example.invalid/sparql> { ?s ?p ?o } }",
            "NETWORK_FORBIDDEN",
            {},
        ),
        (
            "SELECT * FROM <https://example.invalid/data> WHERE { ?s ?p ?o }",
            "NETWORK_FORBIDDEN",
            {},
        ),
        (
            "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
            "UNSUPPORTED_CONSTRUCT",
            {"construct": "sparqlForm"},
        ),
        (
            "SELECT ?s WHERE { ?s ?p ?o } LIMIT 1",
            "UNSUPPORTED_CONSTRUCT",
            {"construct": "querySlice"},
        ),
        ("SELECT WHERE {", "SEMANTIC_INPUT_INVALID", {"field": "query"}),
    ],
)
def test_real_worker_refusal_is_safe_error_frame_and_failed_job(store, text, code, params):
    snapshot = seed(store, text)
    job = accept(store, snapshot)
    request = store.job_context(job["jobId"])["queryRequest"]
    messages, frame, _ = wire(request)
    exit_code, stdout, stderr = run_worker(encoded_messages(messages, frame))
    assert exit_code == 0 and stderr == b""
    frames = output_frames(stdout, frame)
    assert len(frames) == 2 and frames[1] == {"type": "complete"}
    assert set(frames[0]) == {"type", "error"} and frames[0]["type"] == "query.error"
    error = frames[0]["error"]
    assert CONTRACT.validate("error", error)
    assert error["code"] == code and error["params"] == params
    assert text.encode("utf-8") not in stdout
    terminal = asyncio.run(execute_job(store, job))
    assert terminal["state"] == "failed" and terminal["resultRef"] is None
    assert terminal["error"] == error


@pytest.mark.parametrize("damage", ["digest", "index", "truncated", "trailing", "scope"])
def test_real_worker_malformed_input_exits_without_result_or_raw_error(store, damage):
    job = accept(store, seed(store))
    request = deepcopy(store.job_context(job["jobId"])["queryRequest"])
    if damage == "scope":
        request["input"]["scope"] = "asserted+derived"
    messages, frame, _ = wire(request)
    if damage == "digest":
        messages[0]["sha256"] = "0" * 64
    elif damage == "index":
        messages[1]["index"] = 1
    raw = encoded_messages(messages, frame)
    if damage == "truncated":
        raw = raw[: raw.find(b"\n") + 1]
    elif damage == "trailing":
        raw += b"x"
    code, stdout, stderr = run_worker(raw)
    assert code == 76 and stdout == b"" and stderr == b""
    # A direct malformed transport probe is not a fabricated Job terminal.
    assert store.get_job(store.project, job["jobId"])["state"] == "queued"
    assert store.get_job(store.project, job["jobId"])["resultRef"] is None


def test_query_cancel_at_running_notification_has_no_result_or_late_success(store):
    job = accept(store, seed(store))
    decisions = []
    states = []

    def observe(message):
        if message["event"] != "job.state":
            return
        states.append(message["data"]["state"])
        if message["data"]["state"] == "running":
            decisions.append(store.cancel_job(store.project, job["jobId"]))

    terminal = asyncio.run(execute_job(store, job, emit=observe))
    assert len(decisions) == 1 and decisions[0]["disposition"] == "accepted"
    assert decisions[0]["state"] == "cancelling"
    assert states == ["running", "cancelled"]
    assert terminal["state"] == "cancelled"
    assert terminal["resultRef"] is None and terminal["error"] is None
    assert store.cancel_job(store.project, job["jobId"])["disposition"] == "alreadyTerminal"
    assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 0


def test_queued_query_cancel_is_terminal_without_entering_worker(store):
    job = accept(store, seed(store))
    decision = store.cancel_job(store.project, job["jobId"])
    assert decision["disposition"] == "accepted" and decision["state"] == "queued"
    terminal = store.get_job(store.project, job["jobId"])
    assert terminal["state"] == "cancelled" and terminal["error"] is None
    assert terminal["resultRef"] is None
    assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 0


def test_query_cancel_after_owned_child_input_before_reconciliation_reaps_child(store):
    job = accept(store, seed(store))
    owner = []
    children = []
    decisions = []

    def observe(message):
        if (
            message["event"] == "job.progress"
            and message["data"]["progress"]["stage"] == "computing"
        ):
            # The actual launch and full input send have completed. Cancellation
            # precedes reading/reconciliation even if finite evaluation is fast.
            child = owner[0].active[job["jobId"]]["process"]
            assert child is not None and type(child.pid) is int and child.pid > 0
            children.append(child)
            decisions.append(store.cancel_job(store.project, job["jobId"]))

    terminal = asyncio.run(execute_job(store, job, emit=observe, on_actor=owner.append))
    assert len(children) == len(decisions) == 1
    assert decisions[0]["disposition"] == "accepted"
    assert type(children[0].returncode) is int  # Exact owned handle has been reaped.
    assert terminal["state"] == "cancelled" and terminal["error"] is None
    assert terminal["resultRef"] is None
    assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 0
