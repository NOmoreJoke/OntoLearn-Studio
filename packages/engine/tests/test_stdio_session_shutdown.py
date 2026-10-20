"""Real session-fatal shutdown with the caller's stdin pipe deliberately open."""

import json
import queue
import subprocess
import sys
import threading
import time
from uuid import uuid4

import pytest
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.process_environment import worker_environment
from ontolearn_engine.resources import CONTRACT
from test_resident_runtime import prepare


class Wire:
    def __init__(self, database, projects):
        self.process = subprocess.Popen(
            [sys.executable, "-I", "-m", "ontolearn_engine"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=worker_environment()
            | {
                "ONTOLEARN_DB_PATH": str(database),
                "ONTOLEARN_ALLOWED_PROJECTS": json.dumps(projects),
                "ONTOLEARN_TEST_MODE": "1",
            },
        )
        self.session = None
        self.count = 0
        self.inbox = queue.Queue()
        self.writer = None

        def read():
            for raw in self.process.stdout:
                self.inbox.put(raw)

        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def frame(self, method, params):
        return {
            "kind": "request",
            "protocolVersion": 2,
            "id": str(uuid4()),
            "engineSessionId": self.session,
            "method": method,
            "params": params,
        }

    def send(self, frame):
        self.process.stdin.write(json.dumps(frame, separators=(",", ":")).encode() + b"\n")
        self.process.stdin.flush()

    def response(self):
        value = json.loads(self.inbox.get(timeout=8))
        assert CONTRACT.validate("response", value)
        assert value["ok"], value
        return value

    def call(self, method, params):
        frame = self.frame(method, params)
        self.send(frame)
        self.count += 1
        answer = self.response()
        assert answer["id"] == frame["id"] and answer["method"] == method
        if method == "hello":
            self.session = answer["result"]["engineSessionId"]
        return answer["result"]

    def hello(self):
        return self.call("hello", {"supportedVersions": [2], "clientId": str(uuid4())})

    def fill_to(self, count):
        remaining = count - self.count
        assert remaining >= 0
        nonce = str(uuid4())
        errors = []

        def write():
            try:
                for _ in range(remaining):
                    frame = self.frame("session.ping", {"nonce": nonce})
                    self.process.stdin.write(
                        json.dumps(frame, separators=(",", ":")).encode() + b"\n"
                    )
                self.process.stdin.flush()
            except Exception as error:
                errors.append(type(error).__name__)

        self.writer = threading.Thread(target=write, daemon=True)
        self.writer.start()
        for _ in range(remaining):
            answer = self.response()
            assert answer["method"] == "session.ping"
            assert answer["engineSessionId"] == self.session
            assert answer["result"] == {"nonce": nonce}
        self.writer.join(timeout=3)
        assert not self.writer.is_alive() and errors == []
        self.count = count

    def assert_closed_safely(self):
        # Closing stdin first would conceal the daemon BufferedReader deadlock.
        assert not self.process.stdin.closed
        self.process.wait(timeout=5)
        assert not self.process.stdin.closed
        self.reader.join(timeout=2)
        assert not self.reader.is_alive()
        assert self.process.returncode == 0
        assert self.inbox.empty()  # No fabricated response for the fatal frame.
        assert self.process.stderr.read() == b""

    def close(self):
        if self.process.poll() is None:
            self.process.kill()
            self.process.wait(timeout=5)
        if self.writer:
            self.writer.join(timeout=2)
        self.reader.join(timeout=2)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            try:
                stream.close()
            except BrokenPipeError:
                pass


@pytest.mark.parametrize(
    "fatal", ["duplicate-id", "unknown-method", "unknown-envelope", "bad-json"]
)
def test_session_fatal_frame_exits_safely_while_parent_stdin_stays_open(tmp_path, fatal):
    wire = Wire(tmp_path / "fatal.sqlite", [])
    try:
        wire.hello()
        frame = wire.frame("health", {})
        wire.send(frame)
        wire.count += 1
        assert wire.response()["id"] == frame["id"]
        if fatal == "unknown-method":
            frame = wire.frame("unknown", {})
        elif fatal == "unknown-envelope":
            frame = {"unknown": True}
        if fatal == "bad-json":
            wire.process.stdin.write(b"not-json\n")
            wire.process.stdin.flush()
        else:
            wire.send(frame)
        wire.assert_closed_safely()
    finally:
        wire.close()


def test_actual_request_budget_closes_cleanly_and_new_session_preserves_committed_history(tmp_path):
    database = tmp_path / "budget.sqlite"
    store = JobStore(database, contract=CONTRACT)
    store.create_project("session-budget")
    project = store.public_project("session-budget")
    atomic = prepare(
        store,
        project,
        "test.atomic",
        {},
        plan={"definitions": [{"layer": "rule", "id": "budget-rule", "value": {"enabled": True}}]},
    )
    slow_parameters = store.put_blob(project, {"workMs": 10000})
    store.close()
    wire = Wire(database, [project])
    try:
        wire.hello()
        old_session = wire.session
        created = wire.call("job.create", atomic)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            final = wire.call("job.get", {"projectId": project, "jobId": created["jobId"]})
            if final["state"] in {"succeeded", "failed", "cancelled"}:
                break
            time.sleep(0.01)
        assert final["state"] == "succeeded"
        marker = wire.call(
            "operation.get", {"projectId": project, "operationId": created["operationId"]}
        )
        assert marker is not None
        receipt = wire.call(
            "result.get", {"projectId": project, "resultId": final["resultRef"]["resultId"]}
        )
        assert receipt["state"] == "historical"
        projection = wire.call("project.get", {"projectId": project})
        wire.fill_to(65534)  # Real accepted requests, never a fabricated seen set.
        busy = wire.call(
            "job.create",
            {
                "projectId": project,
                "operationId": str(uuid4()),
                "capability": "test.read",
                "input": {
                    "inputSnapshotId": projection["inputSnapshotId"],
                    "scope": "asserted",
                    "definitionId": "budget-interruption",
                    "parametersHash": slow_parameters,
                    "derivedResultIds": [],
                    "preparedPlanRef": None,
                },
                "confirmationRef": None,
            },
        )
        assert busy["state"] == "queued"
        wire.call("session.ping", {"nonce": str(uuid4())})
        assert wire.count == 65536
        wire.send(wire.frame("health", {}))  # The 65537th frame is session fatal.
        wire.assert_closed_safely()
        restored = Wire(database, [project])
        try:
            restored.hello()
            assert restored.session != old_session
            assert (
                restored.call("job.get", {"projectId": project, "jobId": final["jobId"]}) == final
            )
            assert (
                restored.call(
                    "operation.get", {"projectId": project, "operationId": created["operationId"]}
                )
                == marker
            )
            assert (
                restored.call(
                    "result.get", {"projectId": project, "resultId": final["resultRef"]["resultId"]}
                )
                == receipt
            )
            assert restored.call("project.get", {"projectId": project}) == projection
            interrupted = restored.call("job.get", {"projectId": project, "jobId": busy["jobId"]})
            assert interrupted["state"] == "failed" and interrupted["resultRef"] is None
            assert interrupted["error"] == {
                "code": "ENGINE_EXITED",
                "messageKey": "engine.exited",
                "params": {},
                "retryable": True,
            }
            assert (
                restored.call(
                    "operation.get", {"projectId": project, "operationId": busy["operationId"]}
                )
                is None
            )
            assert restored.count == 7  # hello and six reads; no create/cancel/write replay.
        finally:
            restored.close()
    finally:
        wire.close()
