"""Independent I04 lifecycle regressions with actual SQLite and child processes.

ROOT_SOURCE_PATH is an optional development-only worktree path. It lets this
independent test worktree inspect the integration source with its own venv/DB;
normal CI imports the installed package without it. No Electron/UI is started.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

if os.environ.get("ROOT_SOURCE_PATH"):
    sys.path.insert(0, str(Path(os.environ["ROOT_SOURCE_PATH"]) / "packages/engine/src"))

import ontolearn_engine.coordinator as runtime  # noqa: E402
from ontolearn_engine.job_store import JobStore  # noqa: E402
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
