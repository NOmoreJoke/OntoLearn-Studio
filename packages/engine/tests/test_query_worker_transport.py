"""Finite protocol counterexamples plus real owned-worker cancellation/publication fences."""

import asyncio
import hashlib
import io
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest
from ontolearn_engine import worker
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.protocol import ProtocolFault
from ontolearn_engine.resources import CONTRACT, LIMITS, semantic_identity
from test_query_asserted_jobs import prepare_database


def stream_bytes(output=None, *, limits=None):
    limits = limits or LIMITS
    frame, maximum = worker.query_transport_limits(limits)
    encoded = worker.query_encode(output or {"payload": {"text": "泵😀"}, "rows": []}, maximum)
    pieces = worker.query_parts(encoded, frame)
    messages = [{"type": "query.chunk", "index": i, "text": p} for i, p in enumerate(pieces)]
    messages += [
        {
            "type": "query.done",
            "parts": len(pieces),
            "bytes": len(encoded),
            "sha256": hashlib.sha256(encoded).hexdigest(),
        },
        {"type": "complete"},
    ]
    return messages


def wire(messages):
    return b"".join(
        json.dumps(m, ensure_ascii=False, separators=(",", ":")).encode() + b"\n" for m in messages
    )


class Stream:
    def __init__(self, chunks):
        self.chunks = list(chunks)

    async def read(self, maximum):
        await asyncio.sleep(0)
        if not self.chunks:
            return b""
        chunk = self.chunks.pop(0)
        if len(chunk) > maximum:
            self.chunks.insert(0, chunk[maximum:])
        return chunk[:maximum]


class Process:
    def __init__(self, chunks, code=0):
        self.stdout = Stream(chunks)
        self.returncode = code
        self.stdin = self
        self.pid = 123  # Pure fake transport; never signalled/sampled while already exited.

    def write(self, _raw):
        pass

    async def drain(self):
        pass

    def close(self):
        pass

    async def wait(self):
        return self.returncode


def receive(chunks, *, limits=None):
    return asyncio.run(
        Coordinator._query_output(None, Process(chunks), {"limits": limits or LIMITS})
    )


@pytest.mark.parametrize("width", [1, 7, 16384])
def test_private_output_split_utf8_preserves_complete_canonical_material(width):
    output = {"payload": {"text": "泵😀" * 40}, "rows": []}
    raw = wire(stream_bytes(output))
    assert receive([raw[i : i + width] for i in range(0, len(raw), width)]) == output


@pytest.mark.parametrize(
    "case",
    [
        "sequence",
        "digest",
        "bytes",
        "parts",
        "duplicate-done",
        "duplicate-complete",
        "post-terminal-frame",
        "post-terminal-garbage",
        "incomplete-tail",
        "missing-complete",
        "missing-done",
        "error-mixed",
    ],
)
def test_private_output_rejects_every_incomplete_or_late_stream(case):
    messages = stream_bytes()
    suffix = b""
    if case == "sequence":
        messages[0]["index"] = 1
    elif case == "digest":
        messages[-2]["sha256"] = "0" * 64
    elif case == "bytes":
        messages[-2]["bytes"] += 1
    elif case == "parts":
        messages[-2]["parts"] = True
    elif case == "duplicate-done":
        messages.insert(-1, deepcopy(messages[-2]))
    elif case == "duplicate-complete":
        messages.append({"type": "complete"})
    elif case == "post-terminal-frame":
        messages.append({"type": "query.chunk", "index": 1, "text": "x"})
    elif case == "post-terminal-garbage":
        suffix = b"not-json\n"
    elif case == "incomplete-tail":
        suffix = b"{"
    elif case == "missing-complete":
        messages.pop()
    elif case == "missing-done":
        messages.pop(-2)
    else:
        messages.insert(1, {"type": "query.error", "error": {}})
    with pytest.raises(ProtocolFault):
        receive([wire(messages), suffix])


def test_private_output_cumulative_bound_is_checked_before_append():
    limits = {**LIMITS, "maxWorkerMemoryBytes": 4096}
    encoded = worker.query_encode({"payload": {"text": "x" * 5000}, "rows": []}, 8192)
    pieces = worker.query_parts(encoded, LIMITS["maxFrameBytes"])
    with pytest.raises(ProtocolFault):
        receive([wire([{"type": "query.chunk", "index": 0, "text": pieces[0]}])], limits=limits)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
        b'{"a":9007199254740992}',
        b'{"a":"\\ud800"}',
        b'{ "a":1}',
        b"[" * 33 + b"0" + b"]" * 33,
    ],
)
def test_private_decoder_rejects_duplicates_noncanonical_nonfinite_surrogates_and_depth(raw):
    with pytest.raises(ProtocolFault):
        worker.query_decode(raw, 65536)


def test_owner_and_memory_guard_precede_semantic_body_and_are_closed(monkeypatch):
    events = []

    class Owner:
        def __init__(self, *_args):
            events.append("owner")

        def close(self):
            events.append("owner-close")

    class Guard:
        def close(self):
            events.append("guard-close")

    class Bootstrap(io.BytesIO):
        def readline(self, *args):
            events.append("bootstrap-read")
            return super().readline(*args)

    def guard(_maximum):
        events.append("guard")
        return Guard()

    def body(_header):
        assert events == ["owner", "bootstrap-read", "guard"]
        events.append("semantic-body-and-import")

    monkeypatch.setattr(worker, "_OwnerMonitor", Owner)
    monkeypatch.setattr(worker, "_owner_arguments", lambda _: (999, 0))
    monkeypatch.setattr(worker, "install_memory_guard", guard)
    monkeypatch.setattr(worker, "_query", body)
    monkeypatch.setattr(
        worker.sys,
        "stdin",
        SimpleNamespace(
            buffer=Bootstrap(b'{"capability":"query.execute","memoryBytes":536870912}\n')
        ),
    )
    worker.run()
    assert events == [
        "owner",
        "bootstrap-read",
        "guard",
        "semantic-body-and-import",
        "guard-close",
        "owner-close",
    ]


@pytest.mark.parametrize("frame_limit", [1024, LIMITS["maxFrameBytes"]])
def test_worker_calls_fixed_execute_once_and_emits_full_digested_output(
    tmp_path, monkeypatch, frame_limit
):
    from ontolearn_engine import semantic_execution

    limits = {**LIMITS, "maxFrameBytes": frame_limit}
    database, project, _, params = prepare_database(tmp_path)
    store = JobStore(database, contract=CONTRACT)
    try:
        job = store.create_job(
            project,
            params["operationId"],
            "query.execute",
            params["input"],
            None,
            semantic_identity(),
            limits,
        )
        request = store.job_context(job["jobId"])["queryRequest"]
    finally:
        store.close()
    frame, maximum = worker.query_transport_limits(limits)
    raw = worker.query_encode(request, maximum)
    pieces = worker.query_parts(raw, frame)
    if frame_limit == 1024:
        assert len(pieces) > 1
    header = {
        "capability": "query.execute",
        "memoryBytes": LIMITS["maxWorkerMemoryBytes"],
        "frameBytes": frame,
        "byteLimit": maximum,
        "parts": len(pieces),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    body = wire([{"index": i, "text": p} for i, p in enumerate(pieces)])
    output = io.BytesIO()
    calls = []
    original = semantic_execution.execute_request

    def execute(value, **kwargs):
        calls.append(value)
        return original(value, **kwargs)

    monkeypatch.setattr(semantic_execution, "execute_request", execute)
    monkeypatch.setattr(worker.sys, "stdin", SimpleNamespace(buffer=io.BytesIO(body)))
    monkeypatch.setattr(worker.sys, "stdout", SimpleNamespace(buffer=output))
    worker._query(header)
    assert calls == [request]
    decoded = receive([output.getvalue()], limits=limits)
    assert decoded["payload"]["query"]["rows"] == [["<urn:A01>"]]
    assert (
        decoded["payload"]["queryText"]
        == json.loads(request["snapshot"]["state"]["definitions"][0]["payload"])["text"]
    )


@pytest.mark.parametrize("case", ["sequence", "digest", "bytes", "tail"])
def test_worker_request_rejection_happens_before_execute(tmp_path, monkeypatch, case):
    from ontolearn_engine import semantic_execution

    frame, maximum = worker.query_transport_limits(LIMITS)
    raw = worker.query_encode(
        {"capability": "query.execute", "input": {"scope": "asserted"}, "selected": None}, maximum
    )
    pieces = worker.query_parts(raw, frame)
    messages = [{"index": i, "text": p} for i, p in enumerate(pieces)]
    header = {
        "capability": "query.execute",
        "memoryBytes": LIMITS["maxWorkerMemoryBytes"],
        "frameBytes": frame,
        "byteLimit": maximum,
        "parts": len(pieces),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    if case == "sequence":
        messages[0]["index"] = 1
    elif case == "digest":
        header["sha256"] = "0" * 64
    elif case == "bytes":
        header["bytes"] -= 1
    body = wire(messages) + (b"x" if case == "tail" else b"")
    calls = []
    monkeypatch.setattr(
        semantic_execution, "execute_request", lambda *_a, **_kw: calls.append(True)
    )
    monkeypatch.setattr(worker.sys, "stdin", SimpleNamespace(buffer=io.BytesIO(body)))
    with pytest.raises(ProtocolFault):
        worker._query(header)
    assert calls == []


@pytest.mark.parametrize("code", [71, 76])
def test_nonzero_worker_exit_never_publishes_even_with_complete_frames(tmp_path, monkeypatch, code):
    import ontolearn_engine.coordinator as module

    database, project, _, params = prepare_database(tmp_path)
    store = JobStore(database, contract=CONTRACT)
    coordinator = Coordinator(store, allowed_projects={project}, emit=lambda _: None)
    child = Process([wire(stream_bytes())], code=code)

    async def spawn(*_args, **_kwargs):
        return child

    monkeypatch.setattr(module.asyncio, "create_subprocess_exec", spawn)
    job = coordinator.dispatch("job.create", params)
    active = {"project": project, "process": None, "writing": False}
    coordinator.active[job["jobId"]] = active
    try:
        asyncio.run(coordinator.execute(job["jobId"], store.job_context(job["jobId"]), active))
        assert store.get_job(project, job["jobId"])["state"] == "failed"
        assert store.get_job(project, job["jobId"])["error"]["code"] == "ENGINE_EXITED"
        assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 0
        assert store._db.execute("SELECT count(*) FROM job_results").fetchone()[0] == 0
    finally:
        store.close()


@pytest.mark.parametrize("when", ["running", "before-publish"])
def test_real_owned_query_cancel_fences_before_publication(tmp_path, monkeypatch, when):
    database, project, _, params = prepare_database(tmp_path)
    store = JobStore(database, contract=CONTRACT)
    coordinator = Coordinator(store, allowed_projects={project}, emit=lambda _: None)
    job = coordinator.dispatch("job.create", params)
    original_read = coordinator._query_output
    original_finish = store.finish_query_job

    async def scenario():
        entered, proceed = asyncio.Event(), asyncio.Event()

        async def gated(process, dto):
            entered.set()
            if when == "running":
                await proceed.wait()
            return await original_read(process, dto)

        def finish(identity, output, **kwargs):
            if when == "before-publish":
                coordinator.dispatch("job.cancel", {"projectId": project, "jobId": identity})
            return original_finish(identity, output, **kwargs)

        monkeypatch.setattr(coordinator, "_query_output", gated)
        monkeypatch.setattr(store, "finish_query_job", finish)
        active = {"project": project, "process": None, "writing": False}
        coordinator.active[job["jobId"]] = active
        task = asyncio.create_task(
            coordinator.execute(job["jobId"], store.job_context(job["jobId"]), active)
        )
        await asyncio.wait_for(entered.wait(), 15)
        assert active["process"] is not None  # Actual original create_subprocess_exec path.
        if when == "running":
            answer = coordinator.dispatch(
                "job.cancel", {"projectId": project, "jobId": job["jobId"]}
            )
            assert answer["disposition"] == "accepted" and answer["state"] == "cancelling"
        proceed.set()
        await asyncio.wait_for(task, 15)
        assert active["process"].returncode is not None

    try:
        asyncio.run(scenario())
        final = store.get_job(project, job["jobId"])
        assert final["state"] == "cancelled"
        assert store._db.execute("SELECT count(*) FROM job_results").fetchone()[0] == 0
        assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 0
        # A late bundle cannot change a persisted terminal state or publish rows.
        assert store.finish_query_job(job["jobId"], object()) == final
    finally:
        store.close()


def test_queued_query_cancel_launches_no_worker(tmp_path, monkeypatch):
    import ontolearn_engine.coordinator as module

    database, project, _, params = prepare_database(tmp_path)
    store = JobStore(database, contract=CONTRACT)
    coordinator = Coordinator(store, allowed_projects={project}, emit=lambda _: None)
    calls = []

    async def forbidden(*_a, **_kw):
        calls.append(True)
        raise AssertionError("queued cancellation must not launch")

    monkeypatch.setattr(module.asyncio, "create_subprocess_exec", forbidden)
    try:
        job = coordinator.dispatch("job.create", params)
        coordinator.dispatch("job.cancel", {"projectId": project, "jobId": job["jobId"]})
        asyncio.run(coordinator.tick())
        assert calls == []
        assert store.get_job(project, job["jobId"])["state"] == "cancelled"
        assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 0
    finally:
        store.close()


def test_operation_retry_in_owned_launch_gap_does_not_enqueue_second_worker(tmp_path):
    database, project, _, params = prepare_database(tmp_path)
    store = JobStore(database, contract=CONTRACT)
    coordinator = Coordinator(store, allowed_projects={project}, emit=lambda _: None)
    try:
        job = coordinator.dispatch("job.create", params)
        coordinator.queued.remove(job["jobId"])
        coordinator.active[job["jobId"]] = {"project": project, "process": None, "writing": False}
        # Actual tick has transferred ownership before its async start_job turn.
        assert coordinator.dispatch("job.create", params) == job
        assert job["jobId"] not in coordinator.queued
        assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
    finally:
        store.close()
