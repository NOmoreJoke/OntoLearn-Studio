"""Independent I04 lifecycle regressions with actual SQLite and child processes.

ROOT_SOURCE_PATH is an optional development-only worktree path. It lets this
independent test worktree inspect the integration source with its own venv/DB;
normal CI imports the installed package without it. No Electron/UI is started.
"""

import asyncio
import ctypes
import errno
import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import pytest

if os.environ.get("ROOT_SOURCE_PATH"):
    sys.path.insert(0, str(Path(os.environ["ROOT_SOURCE_PATH"]) / "packages/engine/src"))

import ontolearn_engine.coordinator as runtime  # noqa: E402
from ontolearn_engine.job_store import JobStore  # noqa: E402
from ontolearn_engine.memory_guard import MemoryGuardUnavailable  # noqa: E402
from ontolearn_engine.protocol import JsonlReader, ProtocolFault  # noqa: E402
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION, LIMITS  # noqa: E402


def uid():
    return str(uuid4())


@pytest.fixture
def store(tmp_path):
    service = JobStore(tmp_path / "lifecycle.sqlite", contract=CONTRACT)
    service.create_project("lifecycle-main")
    yield service
    service.close()


def create(
    store, capability="test.read", parameters=None, total_ms=1000, internal="lifecycle-main"
):
    project = store.public_project(internal)
    snapshot = store.project_get(project)
    input_ = {
        "inputSnapshotId": snapshot["inputSnapshotId"],
        "scope": "scenario" if capability == "test.rounds" else "asserted",
        "definitionId": "probe",
        "parametersHash": store.put_blob(project, parameters or {}),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    return store.create_job(
        project, uid(), capability, input_, None, IMPLEMENTATION, {**LIMITS, "totalMs": total_ms}
    )


def command(monkeypatch, source):
    monkeypatch.setattr(runtime, "worker_command", lambda: [sys.executable, "-I", "-c", source])


def launch(coordinator, job):
    identity = job["jobId"]
    active = {"project": job["projectId"], "process": None}
    coordinator.active[identity] = active
    task = asyncio.create_task(
        coordinator.execute(identity, coordinator.store.job_context(identity), active)
    )
    return task, active


def assert_no_success(store, job):
    actual = store.get_job(job["projectId"], job["jobId"])
    assert actual["state"] in {"failed", "cancelled"}
    assert actual["resultRef"] is None
    assert store.operation_get(job["projectId"], job["operationId"]) is None
    assert store._db.execute("SELECT count(*) FROM results").fetchone()[0] == 0
    return actual


def test_huge_integer_is_session_fatal_and_reader_stays_terminal():
    reader = JsonlReader()
    with pytest.raises(ProtocolFault):
        reader.feed(b"1" + b"0" * 400 + b"\n")
    assert reader.terminal
    assert len(reader.buffer) == 0
    assert reader.feed(b"{}\n") == []


def test_actual_worker_has_no_inherited_credentials_or_coordinator_authority(store, monkeypatch):
    excluded = (
        "OPENAI_API_KEY",
        "UNRECOGNIZED_VENDOR_SECRET",
        "HTTPS_PROXY",
        "PYTHONPATH",
        "ONTOLEARN_DB_PATH",
        "ONTOLEARN_ALLOWED_PROJECTS",
        "ONTOLEARN_TEST_MODE",
    )
    for key in excluded:
        monkeypatch.setenv(key, "i04-synthetic-sentinel")
    command(
        monkeypatch,
        "import os,sys;sys.stdin.readline();"
        f"assert not set({excluded!r}).intersection(os.environ);"
        'print(\'{"type":"ready","rows":[]}\');'
        'print(\'{"type":"complete"}\',flush=True)',
    )
    job = create(store)
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)

    async def run():
        task, active = launch(coordinator, job)
        await asyncio.wait_for(task, 3)
        assert active["process"].returncode == 0

    asyncio.run(run())
    assert store.get_job(job["projectId"], job["jobId"])["state"] == "succeeded"


def test_complete_waiting_for_worker_exit_cannot_extend_total(store, monkeypatch):
    command(
        monkeypatch,
        "import sys,time;sys.stdin.readline();"
        'print(\'{"type":"ready","rows":[]}\');'
        'print(\'{"type":"complete"}\',flush=True);time.sleep(5)',
    )
    job = create(store, total_ms=200)
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)

    async def run():
        task, active = launch(coordinator, job)
        await asyncio.wait_for(task, 3)
        assert active["process"].returncode is not None

    asyncio.run(run())
    result = assert_no_success(store, job)
    assert result["state"] == "failed"
    assert result["error"] == runtime.safe_error("TIMEOUT", {"phase": "total"})


def test_cancel_while_worker_exit_waits_remains_cancelled(store, monkeypatch):
    command(
        monkeypatch,
        "import sys,time;sys.stdin.readline();"
        'print(\'{"type":"ready","rows":[]}\');'
        'print(\'{"type":"complete"}\',flush=True);time.sleep(5)',
    )
    job = create(store, total_ms=5000)
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)

    async def run():
        task, active = launch(coordinator, job)
        await asyncio.sleep(0.1)
        decision = store.cancel_job(job["projectId"], job["jobId"])
        assert decision["disposition"] == "accepted"
        await asyncio.wait_for(task, 2)
        assert active["process"].returncode is not None
        assert decision["state"] == "cancelling"

    asyncio.run(run())
    assert assert_no_success(store, job)["state"] == "cancelled"


def job_rounds(store, job):
    run = store._db.execute("SELECT run FROM jobs WHERE id=?", (job["jobId"],)).fetchone()[0]
    if run is None:
        return []
    return [
        row[0]
        for row in store._db.execute(
            "SELECT number FROM rounds WHERE run=? ORDER BY number", (run,)
        )
    ]


async def park(hook_entered, settled):
    hook_entered.set()
    try:
        await asyncio.Future()
    finally:
        settled.set()


class GateClock:
    """A monotonic-clock proxy bound ONLY to the coordinator module under
    test (monkeypatch of runtime.time): the deadline and controlled() read
    it, while asyncio, the Store and the real worker keep the real clock.
    Advancing the offset after the hook is entered makes the ORIGINAL total
    deadline arrive deterministically without touching any product budget."""

    def __init__(self, real):
        self._real = real
        self.offset = 0.0

    def monotonic(self):
        return self._real.monotonic() + self.offset

    def __getattr__(self, name):
        return getattr(self._real, name)


def real_user_cancel(store, job):
    decision = store.cancel_job(job["projectId"], job["jobId"])
    assert decision["disposition"] == "accepted"
    assert decision["state"] == "cancelling"


def test_test_schedule_is_refused_in_production(store, monkeypatch):
    async def never(*_args):
        await asyncio.Future()

    with pytest.raises(ValueError):
        runtime.Coordinator(store, _test_schedule={"after_round_commit": never})
    with pytest.raises(ValueError):
        runtime.Coordinator(store, test_mode=True, _test_schedule={"unexpected": never})
    with pytest.raises(ValueError):
        runtime.Coordinator(store, test_mode=True, _test_schedule={"after_round_commit": object()})
    assert runtime.Coordinator(store, test_mode=True, emit=lambda _: None)._test_schedule is None
    monkeypatch.delenv("ONTOLEARN_TEST_MODE", raising=False)
    with pytest.raises(ValueError):
        asyncio.run(runtime.serve(_test_schedule={"before_worker": never}))


def test_round_gate_blocks_the_next_round_in_the_same_chunk_until_released(store, monkeypatch):
    # Controlled-fixture role: this worker is NOT ontolearn_engine.worker; it
    # exists to make the round messages observable per feed() result so the
    # gate is provably blocking the next in-chunk message, not merely a later
    # pipe read. Real-worker park/release is covered separately below.
    recorded = []
    real_reader = runtime.JsonlReader

    class RecordingReader(real_reader):
        def feed(self, chunk):
            messages = super().feed(chunk)
            recorded.append(messages)
            return messages

    monkeypatch.setattr(runtime, "JsonlReader", RecordingReader)
    command(
        monkeypatch,
        "import sys;sys.stdin.readline();sys.stdout.write("
        '\'{"type":"round","round":1,"state":{"pendingEvents":[],'
        '"consumedEvents":[],"inputEvents":[]}}\\n\''
        '\'{"type":"round","round":2,"state":{"pendingEvents":[],'
        '"consumedEvents":[],"inputEvents":[]}}\\n\''
        '\'{"type":"complete"}\\n\');sys.stdout.flush()',
    )
    job = create(store, "test.rounds", {"maxRounds": 2}, total_ms=5000)
    holder = {"entered": []}

    async def run():
        gate = asyncio.Event()

        async def after_round(coordinator, job_view, round_number):
            # job_view may be a stale DTO: only its identity is used here.
            holder["entered"].append(round_number)
            await gate.wait()

        coordinator = runtime.Coordinator(
            store,
            test_mode=True,
            emit=lambda _: None,
            _test_schedule={"after_round_commit": after_round},
        )
        task, _ = launch(coordinator, job)
        for _ in range(150):
            if holder["entered"]:
                break
            await asyncio.sleep(0.02)
        assert holder["entered"] == [1]
        assert job_rounds(store, job) == [1]
        assert store.get_job(job["projectId"], job["jobId"])["state"] == "running"
        gate.set()
        await asyncio.wait_for(task, 3)

    asyncio.run(run())
    # Round 1 AND round 2 really arrived inside ONE feed() result (extra
    # trailing messages in that result are fine): the gate held the next
    # in-chunk message itself, not a later pipe read.
    assert any(
        messages[i].get("type") == "round"
        and messages[i].get("round") == 1
        and messages[i + 1].get("type") == "round"
        and messages[i + 1].get("round") == 2
        for messages in recorded
        for i in range(len(messages) - 1)
    )
    assert store.get_job(job["projectId"], job["jobId"])["state"] == "succeeded"
    assert job_rounds(store, job) == [1, 2]


def test_round_gate_parks_and_releases_the_real_worker(store, monkeypatch):
    actual_worker(monkeypatch)
    job = create(store, "test.rounds", {"workMs": 50, "maxRounds": 2}, total_ms=5000)
    holder = {"entered": []}

    async def run():
        gate = asyncio.Event()

        async def after_round(coordinator, job_view, round_number):
            holder["entered"].append(round_number)
            await gate.wait()

        coordinator = runtime.Coordinator(
            store,
            test_mode=True,
            emit=lambda _: None,
            _test_schedule={"after_round_commit": after_round},
        )
        task, _ = launch(coordinator, job)
        for _ in range(150):
            if holder["entered"]:
                break
            await asyncio.sleep(0.02)
        assert holder["entered"] == [1]
        assert job_rounds(store, job) == [1]
        gate.set()
        await asyncio.wait_for(task, 5)

    asyncio.run(run())
    assert store.get_job(job["projectId"], job["jobId"])["state"] == "succeeded"
    assert job_rounds(store, job) == [1, 2]


def test_after_round_gate_cancel_is_bounded_and_leaves_nothing_behind(store, monkeypatch):
    actual_worker(monkeypatch)
    job = create(store, "test.rounds", {"workMs": 50, "maxRounds": 2}, total_ms=5000)
    hook_entered = asyncio.Event()
    hook_settled = asyncio.Event()

    async def run():
        async def after_round(coordinator, job_view, round_number):
            await park(hook_entered, hook_settled)

        coordinator = runtime.Coordinator(
            store,
            test_mode=True,
            emit=lambda _: None,
            _test_schedule={"after_round_commit": after_round},
        )
        task, active = launch(coordinator, job)
        await asyncio.wait_for(hook_entered.wait(), 3)
        assert job_rounds(store, job) == [1]
        # A REAL user cancellation: controlled() observes the cancelling
        # state and settles the gated wait through its own cleanup.
        real_user_cancel(store, job)
        await asyncio.wait_for(task, 3)
        assert hook_settled.is_set()
        assert active["process"].returncode is not None
        pending = [item for item in asyncio.all_tasks() if item is not asyncio.current_task()]
        assert pending == []

    asyncio.run(run())
    assert job_rounds(store, job) == [1]
    assert assert_no_success(store, job)["state"] == "cancelled"


@pytest.mark.parametrize("cancel", [True, False])
def test_before_worker_gate_cancel_and_timeout(store, monkeypatch, cancel):
    actual_worker(monkeypatch)
    job = create(store, "test.rounds", {"workMs": 50, "maxRounds": 2}, total_ms=5000)
    hook_entered = asyncio.Event()
    hook_settled = asyncio.Event()
    clock = GateClock(runtime.time)
    monkeypatch.setattr(runtime, "time", clock)

    async def run():
        async def before_worker(coordinator, job_view):
            await park(hook_entered, hook_settled)

        coordinator = runtime.Coordinator(
            store,
            test_mode=True,
            emit=lambda _: None,
            _test_schedule={"before_worker": before_worker},
        )
        task, active = launch(coordinator, job)
        await asyncio.wait_for(hook_entered.wait(), 3)
        if cancel:
            real_user_cancel(store, job)
            await asyncio.wait_for(task, 3)
        else:
            # Deterministic original-deadline expiry: with the gate entered,
            # advance ONLY this coordinator's monotonic clock past the real
            # 5s total; controlled() then raises the production TIMEOUT.
            clock.offset = 6.0
            await asyncio.wait_for(task, 5)
        assert hook_settled.is_set()
        # The worker was never launched while the gate held.
        assert active["process"] is None
        pending = [item for item in asyncio.all_tasks() if item is not asyncio.current_task()]
        assert pending == []

    asyncio.run(run())
    result = assert_no_success(store, job)
    if cancel:
        assert result["state"] == "cancelled"
    else:
        assert result["error"] == runtime.safe_error("TIMEOUT", {"phase": "total"})
    assert job_rounds(store, job) == []


def test_after_round_gate_is_bounded_by_the_original_total_deadline(store, monkeypatch):
    actual_worker(monkeypatch)
    job = create(store, "test.rounds", {"workMs": 50, "maxRounds": 2}, total_ms=5000)
    hook_entered = asyncio.Event()
    hook_settled = asyncio.Event()
    clock = GateClock(runtime.time)
    monkeypatch.setattr(runtime, "time", clock)

    async def run():
        async def after_round(coordinator, job_view, round_number):
            await park(hook_entered, hook_settled)

        coordinator = runtime.Coordinator(
            store,
            test_mode=True,
            emit=lambda _: None,
            _test_schedule={"after_round_commit": after_round},
        )
        task, active = launch(coordinator, job)
        await asyncio.wait_for(hook_entered.wait(), 3)
        # Real round-1 is committed and read back BEFORE the deadline moves;
        # then only this coordinator's monotonic clock advances past the real
        # 5s total, so the production deadline — not a test timeout — fires.
        assert job_rounds(store, job) == [1]
        clock.offset = 6.0
        await asyncio.wait_for(task, 5)
        assert hook_settled.is_set()
        assert active["process"].returncode is not None
        pending = [item for item in asyncio.all_tasks() if item is not asyncio.current_task()]
        assert pending == []

    asyncio.run(run())
    result = assert_no_success(store, job)
    assert result["error"] == runtime.safe_error("TIMEOUT", {"phase": "total"})
    assert job_rounds(store, job) == [1]


def test_real_cancel_after_round1_in_same_chunk_finalizes_cancelled(store, monkeypatch):
    # Default path, NO _test_schedule injection: the worker really emits
    # round1 AND round2 in one flushed write (a RecordingReader witness
    # asserts both messages really arrived in ONE feed() result), the
    # coordinator commits the real round-1, and a real user cancel
    # linearizes in the yield after that commit — before the same-chunk
    # round-2 message is consumed. The accepted cancel must finalize as
    # cancelled (not misclassify the next normal write as INVALID_STATE
    # failure), keep the committed history exactly [1], leave the project
    # revision at its baseline, and let the job stateVersion keep its real
    # progression.
    recorded = []
    real_reader = runtime.JsonlReader

    class RecordingReader(real_reader):
        def feed(self, chunk):
            messages = super().feed(chunk)
            recorded.append(messages)
            return messages

    monkeypatch.setattr(runtime, "JsonlReader", RecordingReader)
    command(
        monkeypatch,
        "import sys,time;sys.stdin.readline();sys.stdout.write("
        '\'{"type":"round","round":1,"state":{"pendingEvents":[],'
        '"consumedEvents":[],"inputEvents":[]}}\\n\''
        '\'{"type":"round","round":2,"state":{"pendingEvents":[],'
        '"consumedEvents":[],"inputEvents":[]}}\\n\');sys.stdout.flush();time.sleep(30)',
    )
    job = create(store, "test.rounds", {"maxRounds": 2}, total_ms=5000)
    project = store.public_project("lifecycle-main")
    revision_before = store.project_get(project)["projectRevision"]
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)
    observed = {
        "runningStateVersion": None,
        "cancelDecision": None,
        "cancellingStateVersion": None,
        "round1": None,
    }

    async def run():
        task, active = launch(coordinator, job)
        guard = None
        try:

            async def canceller():
                # sleep(0) spin with an in-budget bound: resumes inside the
                # coordinator's post-commit yield, so the cancel lands
                # strictly before round 2 is consumed; the bound turns a
                # never-started worker into a fixture failure, not a hang.
                deadline = time.monotonic() + 4
                while job_rounds(store, job) != [1]:
                    assert time.monotonic() < deadline, "round 1 never committed"
                    await asyncio.sleep(0)
                running = store.get_job(job["projectId"], job["jobId"])
                assert running["state"] == "running"
                observed["runningStateVersion"] = running["stateVersion"]
                observed["round1"] = running["commitProgress"]["committedProgress"]
                decision = store.cancel_job(job["projectId"], job["jobId"])
                assert decision["disposition"] == "accepted"
                assert decision["state"] == "cancelling"
                observed["cancelDecision"] = decision
                cancelling = store.get_job(job["projectId"], job["jobId"])
                assert cancelling["state"] == "cancelling"
                # The decision snapshot's version is exactly the durable
                # cancelling readback, and both are strictly past running.
                assert decision["stateVersion"] == cancelling["stateVersion"]
                assert cancelling["stateVersion"] > running["stateVersion"]
                observed["cancellingStateVersion"] = cancelling["stateVersion"]

            guard = asyncio.create_task(canceller())
            await asyncio.wait_for(task, 5)
            await asyncio.wait_for(guard, 3)
            # ALL acceptance assertions run BEFORE the fixture fallback in the
            # finally: SUT outcome, then the complete persisted-final state,
            # then the feed witness — the fallback can never stand in for
            # them.
            assert observed["cancelDecision"] is not None
            assert active["process"].returncode is not None
            pending = [item for item in asyncio.all_tasks() if item is not asyncio.current_task()]
            assert pending == []
            final = assert_no_success(store, job)
            assert final["state"] == "cancelled"
            assert final["error"] is None
            assert job_rounds(store, job) == [1]
            # Three separate persisted boundaries: project revision stays at
            # its baseline; the committed round history is exactly [1] with
            # the SAME round-1 progress snapshot the running state held; the
            # job stateVersion keeps its real progression past both the
            # running and the durable cancelling versions.
            assert store.project_get(project)["projectRevision"] == revision_before
            assert observed["round1"] is not None
            assert final["commitProgress"]["committedProgress"] == observed["round1"]
            assert final["stateVersion"] > observed["cancellingStateVersion"]
            # Feed witness: round1 and round2 really arrived in ONE feed()
            # result (extra trailing messages fine) — the cancel linearized
            # inside that same chunk, not across separate reads.
            assert any(
                messages[i].get("type") == "round"
                and messages[i].get("round") == 1
                and messages[i + 1].get("type") == "round"
                and messages[i + 1].get("round") == 2
                for messages in recorded
                for i in range(len(messages) - 1)
            )
        finally:
            # Fixture fallback ONLY — never counted as SUT success above.
            # Snapshot the CURRENT owned handle and kill it FIRST (before any
            # await that could throw and skip the kill); every settlement
            # step then runs in its own finally so one failure cannot skip
            # the rest, and any cleanup failure re-raises as a test failure.
            child = active["process"]
            if child is not None and child.returncode is None:
                child.kill()
            try:
                if guard is not None and not guard.done():
                    guard.cancel()
                    await asyncio.wait_for(asyncio.gather(guard, return_exceptions=True), 3)
            finally:
                try:
                    if not task.done():
                        task.cancel()
                    await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), 5)
                finally:
                    if child is not None:
                        await asyncio.wait_for(child.wait(), 3)

    asyncio.run(run())


@pytest.mark.parametrize("cancel", [True, False])
def test_late_cancel_during_failure_cleanup_keeps_original_error(store, monkeypatch, cancel):
    # The worker commits a real round-1, then emits a real failure frame and
    # stays alive. The coordinator observes the failure and enters its real
    # generic cleanup: process.kill() on the OWNED child, then a real
    # await process.wait(). A test-local pass-through wrapper around that
    # same child's wait records the cleanup phase and (cancel branch only)
    # holds the gate until the real user cancel is durably accepted — this
    # hold is TEST SCHEDULING to fix the interleaving deterministically, not
    # a claim of OS-natural delay; the real kill call, the real wait call
    # and the real returncode are all preserved. A cancel arriving at that
    # point (after the error was observed, during the real cleanup await)
    # must NOT rewrite the original INTERNAL_ERROR; the no-cancel control
    # proves the error equality is not incidental.
    command(
        monkeypatch,
        "import sys,time;sys.stdin.readline();sys.stdout.write("
        '\'{"type":"round","round":1,"state":{"pendingEvents":[],'
        '"consumedEvents":[],"inputEvents":[]}}\\n\''
        '\'{"type":"failure"}\\n\');sys.stdout.flush();time.sleep(30)',
    )
    job = create(store, "test.rounds", {"maxRounds": 2}, total_ms=5000)
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)
    observed = {"cleanupEntered": False, "cancelDecision": None}

    async def run():
        task, active = launch(coordinator, job)
        guard = None
        release_cleanup = asyncio.Event()
        cleanup_entered = asyncio.Event()
        # One try/finally covering EVERYTHING after launch (observation,
        # wrapping, assertions): a launch-observation failure still settles
        # the launched task in the finally.
        try:
            # Wait until the OWNED child exists (in-budget bound; a worker
            # that never launches is a fixture failure, not a hang), then
            # wrap ITS wait (pass-through to the real coroutine; only the
            # gate in front is test scheduling).
            deadline = time.monotonic() + 4
            while active["process"] is None:
                assert time.monotonic() < deadline, "owned worker never launched"
                await asyncio.sleep(0)
            child = active["process"]
            real_wait = child.wait

            async def gated_wait():
                cleanup_entered.set()
                observed["cleanupEntered"] = True
                if cancel:
                    await release_cleanup.wait()
                return await real_wait()

            child.wait = gated_wait

            async def late_cancel():
                await asyncio.wait_for(cleanup_entered.wait(), 3)
                decision = store.cancel_job(job["projectId"], job["jobId"])
                assert decision["disposition"] == "accepted"
                assert decision["state"] == "cancelling"
                # Read back the durable cancelling state BEFORE releasing the
                # cleanup gate, and prove the decision snapshot is exactly it.
                cancelling = store.get_job(job["projectId"], job["jobId"])
                assert cancelling["state"] == "cancelling"
                assert decision["stateVersion"] == cancelling["stateVersion"]
                observed["cancelDecision"] = decision
                release_cleanup.set()

            guard = asyncio.create_task(late_cancel()) if cancel else None
            await asyncio.wait_for(task, 5)
            if guard is not None:
                await asyncio.wait_for(guard, 3)
            # ALL acceptance assertions run BEFORE the fixture fallback in the
            # finally — the fallback can never stand in for them.
            assert observed["cleanupEntered"] is True
            if cancel:
                assert observed["cancelDecision"]["disposition"] == "accepted"
                assert observed["cancelDecision"]["state"] == "cancelling"
                assert release_cleanup.is_set()
            assert child.returncode is not None
            pending = [item for item in asyncio.all_tasks() if item is not asyncio.current_task()]
            assert pending == []
            result = assert_no_success(store, job)
            assert result["state"] == "failed"
            assert result["error"] == runtime.safe_error("INTERNAL_ERROR")
            assert job_rounds(store, job) == [1]
        finally:
            # Fixture fallback ONLY — never counted as SUT success above.
            # Release the gates and snapshot the CURRENT owned handle FIRST
            # (before any await that could throw and skip the kill); kill the
            # handle only while alive; every settlement step then runs in its
            # own finally so one failure cannot skip the rest, and any cleanup
            # failure re-raises as a test failure.
            release_cleanup.set()
            cleanup_entered.set()
            child = active["process"]
            if child is not None and child.returncode is None:
                child.kill()
            try:
                if guard is not None and not guard.done():
                    guard.cancel()
                    await asyncio.wait_for(asyncio.gather(guard, return_exceptions=True), 3)
            finally:
                try:
                    if not task.done():
                        task.cancel()
                    await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), 5)
                finally:
                    if child is not None:
                        await asyncio.wait_for(child.wait(), 3)

    asyncio.run(run())


def test_round_after_complete_in_same_chunk_never_commits(store, monkeypatch):
    command(
        monkeypatch,
        "import sys;sys.stdin.readline();sys.stdout.write("
        '\'{"type":"complete"}\\n\''
        '\'{"type":"round","round":1,"state":{"pendingEvents":[],'
        '"consumedEvents":[],"inputEvents":[]}}\\n\');sys.stdout.flush()',
    )
    job = create(store, "test.rounds", {"maxRounds": 1})
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)

    async def run():
        task, _ = launch(coordinator, job)
        await asyncio.wait_for(task, 3)

    asyncio.run(run())
    result = assert_no_success(store, job)
    assert result["commitProgress"]["committedProgress"] is None
    assert store._db.execute("SELECT count(*) FROM rounds").fetchone()[0] == 0


@pytest.mark.parametrize("cancel", [False, True])
def test_unread_worker_stdin_is_bounded_and_cancellable(store, monkeypatch, cancel):
    command(monkeypatch, "import time;time.sleep(5)")
    rows = [{"rowId": uid(), "ordinal": i, "cells": ["a" * 7000]} for i in range(30)]
    job = create(store, parameters={"rows": rows}, total_ms=5000 if cancel else 200)
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)

    async def run():
        task, active = launch(coordinator, job)
        if cancel:
            await asyncio.sleep(0.1)
            store.cancel_job(job["projectId"], job["jobId"])
        await asyncio.wait_for(task, 3)
        assert active["process"].returncode is not None

    asyncio.run(run())
    result = assert_no_success(store, job)
    if cancel:
        assert result["state"] == "cancelled"
    else:
        assert result["error"] == runtime.safe_error("TIMEOUT", {"phase": "total"})


def test_actual_memory_guard_supports_normal_worker_and_denies_known_oversize():
    source_path = str(Path(runtime.__file__).resolve().parents[1])
    script = (
        f"import sys;sys.path.insert(0,{source_path!r});"
        "from ontolearn_engine.memory_guard import install_memory_guard,MemoryBudgetExceeded;"
        "g=install_memory_guard(536870912);"
        "g.check_allocation(1024);print(g.mode,flush=True);"
        "\ntry:g.check_allocation(1073741824)"
        "\nexcept MemoryBudgetExceeded:print('rejected',flush=True)"
        "\nfinally:g.close()"
    )
    process = subprocess.run(
        [sys.executable, "-I", "-c", script], capture_output=True, timeout=5, check=False
    )
    assert process.returncode == 0
    expected = {
        "darwin": "darwin-rss-monitor",
        "win32": "windows-job",
        "linux": "linux-rlimit-as",
    }[sys.platform]
    assert process.stdout.decode().splitlines() == [expected, "rejected"]
    assert process.stderr == b""


@pytest.mark.skipif(sys.platform != "darwin", reason="Darwin libproc RSS sampling evidence")
def test_darwin_guard_observes_real_rss_growth_and_stops_only_that_process():
    source_path = str(Path(runtime.__file__).resolve().parents[1])
    script = (
        f"import sys,time,os;sys.path.insert(0,{source_path!r});"
        "from ontolearn_engine.memory_guard import install_memory_guard,resident_bytes;"
        "rss=resident_bytes(os.getpid());g=install_memory_guard(rss+16*1024*1024);"
        "allocation=bytearray(32*1024*1024);"
        "\nfor i in range(0,len(allocation),4096):allocation[i]=1"
        "\ntime.sleep(1);g.close()"
    )
    process = subprocess.run(
        [sys.executable, "-I", "-c", script], capture_output=True, timeout=3, check=False
    )
    assert process.returncode == 74
    assert process.stdout == b"" and process.stderr == b""


def actual_worker(monkeypatch):
    source_path = str(Path(runtime.__file__).resolve().parents[1])
    command(
        monkeypatch,
        f"import sys,runpy;sys.path.insert(0,{source_path!r});"
        "runpy.run_module('ontolearn_engine.worker',run_name='__main__')",
    )


def test_memory_failure_isolated_from_other_project_real_worker(store, monkeypatch):
    actual_worker(monkeypatch)
    store.create_project("lifecycle-other")
    failed = create(store, parameters={"allocateBytes": 1073741824}, total_ms=3000)
    rows = [{"rowId": uid(), "ordinal": 0, "cells": ["survived"]}]
    succeeded = create(store, parameters={"rows": rows}, total_ms=3000, internal="lifecycle-other")
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)

    async def run():
        coordinator.queued.extend([failed["jobId"], succeeded["jobId"]])
        await coordinator.tick()
        await asyncio.wait_for(asyncio.gather(*coordinator.tasks), 4)
        assert not coordinator.active

    asyncio.run(run())
    bad = store.get_job(failed["projectId"], failed["jobId"])
    good = store.get_job(succeeded["projectId"], succeeded["jobId"])
    assert bad["state"] == "failed"
    assert bad["resultRef"] is None
    assert bad["error"] == runtime.safe_error("RESOURCE_LIMIT", {"resource": "memory"})
    assert good["state"] == "succeeded"
    result = store.result_get(good["projectId"], good["resultRef"]["resultId"])
    binding = {
        "projectId": good["projectId"],
        "resultId": result["resultId"],
        "inputSnapshotId": result["inputSnapshotId"],
        "scope": result["scope"],
        "parametersHash": result["parametersHash"],
        "order": "ordinal+rowId:asc",
    }
    assert store.result_page(binding, page_size=100, cursor=None)["rows"] == rows


@pytest.mark.skipif(sys.platform != "darwin", reason="Darwin parent RSS sampler failure")
def test_parent_rss_monitor_unavailable_fails_only_the_target_real_worker(store, monkeypatch):
    actual_worker(monkeypatch)
    store.create_project("lifecycle-other")
    failed = create(store, parameters={"workMs": 1500}, total_ms=4000)
    rows = [{"rowId": uid(), "ordinal": 0, "cells": ["survived"]}]
    succeeded = create(store, parameters={"rows": rows}, total_ms=4000, internal="lifecycle-other")
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)
    native_rss = runtime.resident_bytes
    sampled = set()

    def unavailable_for_target(pid):
        active = coordinator.active.get(failed["jobId"])
        target = active and active.get("process")
        if target is not None and target.pid == pid:
            assert target.returncode is None
            sampled.add(pid)
            raise MemoryGuardUnavailable()
        return native_rss(pid)

    monkeypatch.setattr(runtime, "resident_bytes", unavailable_for_target)

    async def run():
        coordinator.queued.extend([failed["jobId"], succeeded["jobId"]])
        await coordinator.tick()
        await asyncio.wait_for(asyncio.gather(*coordinator.tasks), 6)
        assert not coordinator.active

    asyncio.run(run())
    assert len(sampled) == 1
    bad = store.get_job(failed["projectId"], failed["jobId"])
    good = store.get_job(succeeded["projectId"], succeeded["jobId"])
    assert bad["state"] == "failed" and bad["resultRef"] is None
    assert bad["error"] == runtime.safe_error("INTERNAL_ERROR")
    assert store.operation_get(bad["projectId"], bad["operationId"]) is None
    assert good["state"] == "succeeded" and good["resultRef"] is not None
    result = store.result_get(good["projectId"], good["resultRef"]["resultId"])
    binding = {
        "projectId": good["projectId"],
        "resultId": result["resultId"],
        "inputSnapshotId": result["inputSnapshotId"],
        "scope": result["scope"],
        "parametersHash": result["parametersHash"],
        "order": "ordinal+rowId:asc",
    }
    assert store.result_page(binding, page_size=100, cursor=None)["rows"] == rows


@pytest.mark.skipif(sys.platform != "darwin", reason="Actual libproc/child-watcher exit race")
def test_actual_memory_worker_exit_precedes_asyncio_returncode_delivery(store, monkeypatch):
    actual_worker(monkeypatch)
    store.create_project("lifecycle-other")
    failed = create(store, parameters={"allocateBytes": 1073741824}, total_ms=3000)
    succeeded = create(store, parameters={}, total_ms=3000, internal="lifecycle-other")
    coordinator = runtime.Coordinator(store, test_mode=True, emit=lambda _: None)
    native_rss = runtime.resident_bytes
    observations = []
    child = None

    def sample(pid):
        nonlocal child
        active = coordinator.active.get(failed["jobId"])
        target = active and active.get("process")
        if target is None or target.pid != pid:
            return native_rss(pid)
        child = target
        # Hold only parent scheduling until the actual native sample observes
        # the real allocation worker's exit. No substituted syscall or exit code.
        deadline = time.monotonic() + 1
        while time.monotonic() < deadline:
            try:
                native_rss(pid)
            except ProcessLookupError as failure:
                observations.append((failure.errno, ctypes.get_errno(), target.returncode))
                raise
            time.sleep(0.001)
        raise AssertionError("real memory worker did not exit within sampling window")

    monkeypatch.setattr(runtime, "resident_bytes", sample)

    async def run():
        coordinator.queued.extend([failed["jobId"], succeeded["jobId"]])
        await coordinator.tick()
        await asyncio.wait_for(asyncio.gather(*coordinator.tasks), 4)
        assert not coordinator.active

    asyncio.run(run())
    assert observations == [(errno.ESRCH, errno.ESRCH, None)]
    assert child is not None and child.returncode == 74
    bad = store.get_job(failed["projectId"], failed["jobId"])
    assert bad["state"] == "failed" and bad["resultRef"] is None
    assert bad["error"] == runtime.safe_error("RESOURCE_LIMIT", {"resource": "memory"})
    assert store.operation_get(failed["projectId"], failed["operationId"]) is None
    assert store.get_job(succeeded["projectId"], succeeded["jobId"])["state"] == "succeeded"


def test_busy_worker_still_allows_heartbeat_and_cancel(store, monkeypatch):
    actual_worker(monkeypatch)
    job = create(store, parameters={"workMs": 1000}, total_ms=5000)
    coordinator = runtime.Coordinator(
        store, test_mode=True, allowed_projects={job["projectId"]}, emit=lambda _: None
    )
    hello = coordinator.request(
        {
            "kind": "request",
            "protocolVersion": 2,
            "id": uid(),
            "engineSessionId": None,
            "method": "hello",
            "params": {"supportedVersions": [2], "clientId": uid()},
        }
    )
    assert hello["ok"]

    def request(method, params):
        answer = coordinator.request(
            {
                "kind": "request",
                "protocolVersion": 2,
                "id": uid(),
                "engineSessionId": coordinator.session,
                "method": method,
                "params": params,
            }
        )
        assert CONTRACT.validate("response", answer)
        return answer

    async def run():
        task, active = launch(coordinator, job)
        await asyncio.sleep(0.1)
        nonce = uid()
        assert request("session.ping", {"nonce": nonce})["result"] == {"nonce": nonce}
        decision = request("job.cancel", {"projectId": job["projectId"], "jobId": job["jobId"]})
        assert decision["result"]["disposition"] == "accepted"
        assert decision["result"]["state"] == "cancelling"
        await asyncio.wait_for(task, 2)
        assert active["process"].returncode is not None
        assert decision["result"]["state"] == "cancelling"

    asyncio.run(run())
    assert assert_no_success(store, job)["state"] == "cancelled"
