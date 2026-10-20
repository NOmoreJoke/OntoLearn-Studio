"""Real Python coordinator/isolated worker/SQLite integration; no Electron windows."""

import json
import os
import queue
import sqlite3
import subprocess
import sys
import threading
import time
from uuid import uuid4

import pytest
from ontolearn_engine.resources import CONTRACT


class Session:
    def __init__(self, database, projects, test_mode=True):
        env = os.environ | {
            "ONTOLEARN_DB_PATH": str(database),
            "ONTOLEARN_ALLOWED_PROJECTS": json.dumps(projects),
        }
        if test_mode:
            env["ONTOLEARN_TEST_MODE"] = "1"
        else:
            env.pop("ONTOLEARN_TEST_MODE", None)
        command = (
            [os.environ["ONTOLEARN_TEST_ENGINE"]]
            if os.environ.get("ONTOLEARN_TEST_ENGINE")
            else [sys.executable, "-I", "-m", "ontolearn_engine"]
        )
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.inbox = queue.Queue()
        self.notifications = []
        self.session = None

        def read():
            for line in self.process.stdout:
                self.inbox.put(json.loads(line))

        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        hello = self.call("hello", {"supportedVersions": [2], "clientId": str(uuid4())})
        self.session = hello["engineSessionId"]

    def call(self, method, params):
        request = {
            "kind": "request",
            "id": str(uuid4()),
            "protocolVersion": 2,
            "engineSessionId": None if method == "hello" else self.session,
            "method": method,
            "params": params,
        }
        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            value = self.inbox.get(timeout=max(0.01, deadline - time.monotonic()))
            assert CONTRACT.validate(
                "notification" if value["kind"] == "notification" else "response", value
            )
            if value["kind"] == "notification":
                self.notifications.append(value)
                continue
            assert value["id"] == request["id"] and value["method"] == method
            if not value["ok"]:
                return value["error"]
            return value["result"]
        raise AssertionError("request deadline")

    def job(self, project, identity):
        return self.call("job.get", {"projectId": project, "jobId": identity})

    def terminal(self, project, identity, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = self.job(project, identity)
            if job["state"] in {"failed", "cancelled", "succeeded"}:
                return job
            time.sleep(0.02)
        raise AssertionError("job deadline")

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            self.process.wait(timeout=8)
        assert self.process.stderr.read() == b""
        self.process.stdout.close()
        self.process.stderr.close()


@pytest.fixture
def prepared(tmp_path):
    from ontolearn_engine.job_store import JobStore

    database = tmp_path / "runtime.sqlite"
    store = JobStore(database, contract=CONTRACT)
    store.create_project("first")
    store.create_project("second")
    projects = [store.public_project(p) for p in ["first", "second"]]
    yield database, store, projects
    if not store._lease.closed:
        store.close()


def prepare(store, project, capability, parameters, plan=None):
    input_ = {
        "inputSnapshotId": store.project_get(project)["inputSnapshotId"],
        "scope": "scenario" if capability == "test.rounds" else "asserted",
        "definitionId": "infrastructure-probe",
        "parametersHash": store.put_blob(project, parameters),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    confirmation = None
    if plan is not None:
        confirmation_record = store.prepare_plan(
            project,
            store.project_get(project)["projectRevision"],
            plan,
            actor=str(uuid4()),
            permission="write",
        )
        input_["preparedPlanRef"] = confirmation_record["preparedPlanRef"]
        confirmation = confirmation_record["confirmationRef"]
    return {
        "projectId": project,
        "operationId": str(uuid4()),
        "capability": capability,
        "input": input_,
        "confirmationRef": confirmation,
    }


def test_real_health_reuses_pid_and_rejects_test_capability_in_product_mode(prepared):
    database, store, projects = prepared
    params = prepare(store, projects[0], "test.read", {})
    store.close()
    session = Session(database, projects, test_mode=False)
    try:
        pid = session.process.pid
        for _ in range(5):
            assert session.call("health", {}) == {"status": "ok", "engineVersion": "0.1.0"}
        assert session.process.pid == pid
        assert session.call("job.create", params)["code"] == "UNSUPPORTED_CAPABILITY"
    finally:
        session.close()


def test_busy_worker_cancel_ping_and_other_worker_crash_isolation(prepared):
    database, store, projects = prepared
    busy = prepare(store, projects[0], "test.read", {"workMs": 2000})
    crash = prepare(store, projects[1], "test.read", {"crashRound": 1})
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", busy)
        other = session.call("job.create", crash)
        started = time.monotonic()
        nonce = str(uuid4())
        assert session.call("session.ping", {"nonce": nonce}) == {"nonce": nonce}
        assert time.monotonic() - started < 1.5
        decision = session.call("job.cancel", {"projectId": projects[0], "jobId": job["jobId"]})
        assert decision["disposition"] in {"accepted", "alreadyRequested"}
        assert session.terminal(projects[0], job["jobId"])["state"] == "cancelled"
        assert session.terminal(projects[1], other["jobId"])["state"] == "failed"
        assert session.call("health", {})["status"] == "ok"
    finally:
        session.close()


@pytest.mark.parametrize("generate,expected", [(0, 0), (1, 3)])
def test_real_rounds_summary_stable_paging_and_no_formal_changes(prepared, generate, expected):
    database, store, projects = prepared
    request = prepare(
        store,
        projects[0],
        "test.rounds",
        {"maxRounds": 3, "consumePerRound": 0, "generatePerRound": generate},
    )
    revision = store.project_get(projects[0])["projectRevision"]
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        job = session.terminal(projects[0], job["jobId"])
        assert job["state"] == "succeeded", job
        assert job["commitProgress"]["committedProgress"]["lastCommittedRound"] == 3
        result = session.call(
            "result.get", {"projectId": projects[0], "resultId": job["resultRef"]["resultId"]}
        )
        binding = {
            "projectId": projects[0],
            "resultId": result["resultId"],
            "inputSnapshotId": result["inputSnapshotId"],
            "scope": result["scope"],
            "parametersHash": result["parametersHash"],
            "order": "ordinal+rowId:asc",
        }
        page = session.call("result.page", {"binding": binding, "pageSize": 1, "cursor": None})
        cells = page["rows"][0]["cells"]
        assert cells[0] == "run.summary.v1" and cells[6] == expected and cells[5] is (expected > 0)
        cursor = page["nextCursor"]
        assert cursor is not None
        rows = []
        while cursor:
            next_page = session.call(
                "result.page", {"binding": binding, "pageSize": 1, "cursor": cursor}
            )
            assert (
                session.call("result.page", {"binding": binding, "pageSize": 1, "cursor": cursor})
                == next_page
            )
            rows.extend(next_page["rows"])
            cursor = next_page["nextCursor"]
        progress = job["commitProgress"]["committedProgress"]
        assert [row["ordinal"] for row in rows] == [1, 2, 3]
        assert all(
            row["cells"][0] == "run.round.v1"
            and row["cells"][1] == progress["runId"]
            and row["cells"][5] == job["jobId"]
            for row in rows
        )
        assert len({row["cells"][3] for row in rows}) == 3
        assert (
            session.call("project.get", {"projectId": projects[0]})["projectRevision"] == revision
        )
        newer = session.call("job.create", {**request, "operationId": str(uuid4())})
        assert session.terminal(projects[0], newer["jobId"])["state"] == "succeeded"
    finally:
        session.close()

    from ontolearn_engine.job_store import JobStore

    reopened = JobStore(database, contract=CONTRACT)
    try:
        history_before = reopened.history(progress["runId"])
        assert result["resultId"] in reopened.collect_cache()
        assert reopened.history(progress["runId"]) == history_before
    finally:
        reopened.close()
    restored = Session(database, projects)
    try:
        assert restored.job(projects[0], job["jobId"]) == job
        metadata = restored.call(
            "result.get", {"projectId": projects[0], "resultId": result["resultId"]}
        )
        assert metadata["payloadStatus"] == "evicted"
        for cursor in (None, page["nextCursor"]):
            unavailable = restored.call(
                "result.page", {"binding": binding, "pageSize": 1, "cursor": cursor}
            )
            assert unavailable["code"] == "PAYLOAD_EVICTED"
        assert restored.call("job.create", request)["jobId"] == job["jobId"]
    finally:
        restored.close()


def test_real_atomic_completion_cancel_does_not_rewrite_commit(prepared):
    database, store, projects = prepared
    request = prepare(
        store,
        projects[0],
        "test.atomic",
        {},
        {"definitions": [{"layer": "ontology", "id": "probe", "value": {}}]},
    )
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        job = session.terminal(projects[0], job["jobId"])
        assert job["state"] == "succeeded", job
        marker = session.call(
            "operation.get", {"projectId": projects[0], "operationId": request["operationId"]}
        )
        assert marker is not None
        decision = session.call("job.cancel", {"projectId": projects[0], "jobId": job["jobId"]})
        assert decision["disposition"] == "alreadyTerminal" and decision["state"] == "succeeded"
        assert (
            session.call(
                "operation.get", {"projectId": projects[0], "operationId": request["operationId"]}
            )
            == marker
        )
    finally:
        session.close()


@pytest.mark.parametrize("mutation", ["missing", "malformed", "wrong-run", "wrong-snapshot"])
def test_real_worker_summary_corruption_is_safe_at_runtime_read_boundary(prepared, mutation):
    database, store, projects = prepared
    request = prepare(store, projects[0], "test.rounds", {"maxRounds": 2})
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        job = session.terminal(projects[0], job["jobId"])
        assert job["state"] == "succeeded"
        result = session.call(
            "result.get", {"projectId": projects[0], "resultId": job["resultRef"]["resultId"]}
        )
        binding = {
            key: result[key]
            for key in ("projectId", "resultId", "inputSnapshotId", "scope", "parametersHash")
        } | {"order": "ordinal+rowId:asc"}
        # Explicit physical fault injection into this synthetic DB only. The workload,
        # terminal and result were produced by the actual worker and Store first.
        with sqlite3.connect(database) as connection:
            payload = json.loads(
                connection.execute(
                    "SELECT payload FROM results WHERE id=?", (result["resultId"],)
                ).fetchone()[0]
            )
            if mutation == "missing":
                payload = []
            elif mutation == "malformed":
                payload[0]["cells"] = ["invalid-summary"]
            else:
                payload[0]["cells"][1 if mutation == "wrong-run" else 3] = "0" * 64
            connection.execute(
                "UPDATE results SET payload=? WHERE id=?",
                (json.dumps(payload), result["resultId"]),
            )
        assert session.call("result.page", {"binding": binding, "pageSize": 1, "cursor": None}) == {
            "code": "INVALID_STATE",
            "messageKey": "protocol.invalidState",
            "params": {},
            "retryable": False,
        }
        assert session.job(projects[0], job["jobId"]) == job
        assert session.call("health", {})["status"] == "ok"
    finally:
        session.close()


def test_coordinator_kill_reconciles_partial_round_without_replay(prepared):
    database, store, projects = prepared
    request = prepare(store, projects[0], "test.rounds", {"maxRounds": 20, "workMs": 150})
    store.close()
    first = Session(database, projects)
    job = first.call("job.create", request)
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        value = first.job(projects[0], job["jobId"])
        if value["commitProgress"]["committedProgress"]:
            break
        time.sleep(0.02)
    else:
        raise AssertionError("no real round committed")
    first.process.kill()
    first.process.wait(timeout=5)
    first.process.stdin.close()
    first.close()
    restored = Session(database, projects)
    try:
        after = restored.job(projects[0], job["jobId"])
        assert after["state"] == "failed" and after["resultRef"] is None
        assert (
            after["commitProgress"]["committedProgress"]
            == value["commitProgress"]["committedProgress"]
        )
        assert restored.call("job.create", request)["jobId"] == job["jobId"]
        assert restored.job(projects[0], job["jobId"])["state"] == "failed"
    finally:
        restored.close()


@pytest.mark.parametrize("wait_for_round", [False, True])
def test_real_round_cancel_preserves_exact_last_committed_boundary(prepared, wait_for_round):
    database, store, projects = prepared
    request = prepare(store, projects[0], "test.rounds", {"maxRounds": 20, "workMs": 500})
    store.close()
    session = Session(database, projects)
    try:
        job = session.call("job.create", request)
        if wait_for_round:
            deadline = time.monotonic() + 6
            while time.monotonic() < deadline:
                previous = session.job(projects[0], job["jobId"])
                if previous["commitProgress"]["committedProgress"]:
                    break
                time.sleep(0.02)
            else:
                raise AssertionError("no actual committed round before cancellation")
        decision = session.call("job.cancel", {"projectId": projects[0], "jobId": job["jobId"]})
        assert decision["disposition"] == "accepted"
        assert decision["state"] in {"queued", "cancelling"}
        final = session.terminal(projects[0], job["jobId"])
        assert final["state"] == "cancelled" and final["resultRef"] is None
        progress = final["commitProgress"]["committedProgress"]
        if wait_for_round:
            assert progress is not None
            assert (
                progress["lastCommittedRound"]
                >= previous["commitProgress"]["committedProgress"]["lastCommittedRound"]
            )
            assert progress["lastCommittedRound"] < 20
        else:
            assert progress is None
        assert session.call("project.get", {"projectId": projects[0]})["projectRevision"] == 0
        assert decision["state"] in {"queued", "cancelling"}  # Original response remains immutable.
    finally:
        session.close()
