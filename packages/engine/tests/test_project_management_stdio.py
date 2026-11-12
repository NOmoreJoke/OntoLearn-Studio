"""Actual business3 processes: commit succeeds, original response is never emitted."""

import json
import os
import queue
import sqlite3
import subprocess
import sys
import threading
from uuid import uuid4

import pytest
from ontolearn_engine.project.format3 import logical_hash
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest

DROP_APPLY_EMISSION = """
import os
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.__main__ import main
original = Coordinator._emit
def emit(value):
    if value.get('method') == 'project.management.apply' and value.get('ok') is True:
        os._exit(73)
    original(value)
Coordinator._emit = staticmethod(emit)
main()
"""


def uid():
    return str(uuid4())


class Stdio:
    def __init__(self, path, *, drop=False):
        env = os.environ | {"ONTOLEARN_DB_PATH": str(path)}
        env.pop("ONTOLEARN_TEST_MODE", None)
        env.pop("ONTOLEARN_ALLOWED_PROJECTS", None)
        command = [sys.executable, "-I"]
        command += ["-c", DROP_APPLY_EMISSION] if drop else ["-m", "ontolearn_engine"]
        self.process = subprocess.Popen(
            command + ["--t01-internal-profile=business3"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.frames = queue.Queue()
        self.session = None

        def read():
            try:
                for line in self.process.stdout:
                    self.frames.put(json.loads(line))
            finally:
                self.frames.put(None)

        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        hello = self.rpc("hello", {"supportedVersions": [3], "clientId": uid()})
        self.session = hello["engineSessionId"]

    def send(self, method, params):
        identity = uid()
        request = {
            "kind": "request",
            "id": identity,
            "protocolVersion": 2 if method == "hello" else 3,
            "engineSessionId": self.session,
            "method": method,
            "params": params,
        }
        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        self.process.stdin.flush()
        return identity

    def rpc(self, method, params):
        identity = self.send(method, params)
        response = self.frames.get(timeout=10)
        assert response is not None and response.get("id") == identity, response
        assert CONTRACT.validate_business3("response", response), response
        assert response["ok"], response
        return response["result"]

    def close(self):
        if not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            code = self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
            raise
        self.reader.join(timeout=2)
        assert not self.reader.is_alive()
        stderr = self.process.stderr.read()
        self.process.stdout.close()
        self.process.stderr.close()
        return code, stderr


def database_hash(path):
    with sqlite3.connect(path) as db:
        return logical_hash(db)


@pytest.mark.parametrize(
    "action",
    [
        {"kind": "rename", "name": "saved without reply"},
        {"kind": "copy-current", "name": "exactly one copy"},
        {"kind": "trash"},
    ],
)
def test_after_commit_unemitted_reply_recovers_read_only_in_new_process(tmp_path, action):
    path = tmp_path / "stdio.sqlite"
    first = Stdio(path, drop=True)
    try:
        created = first.rpc(
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": "source",
                "initialization": {"kind": "blank"},
            },
        )
        project = created["projectId"]
        state = first.rpc("project.management.read", {"projectId": project})
        preview = first.rpc(
            "project.management.preview",
            {
                "projectId": project,
                "action": action,
                "expectedCheckpointRef": state["checkpointRef"],
                "expectedLifecycleVersion": state["lifecycle"]["version"],
            },
        )
        confirmed = first.rpc(
            "project.management.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
            },
        )
        request = {
            "projectId": project,
            "operationId": uid(),
            "confirmationRef": confirmed["confirmationRef"],
            "documentHash": preview["documentHash"],
        }
        first.send("project.management.apply", request)
        assert first.process.wait(timeout=10) == 73
        # EOF rather than a successful reply: the test has no target project id.
        assert first.frames.get(timeout=2) is None
    finally:
        code, stderr = first.close()
    assert code == 73 and stderr == b""
    before = database_hash(path)
    second = Stdio(path)
    try:
        original_session = first.session
        assert second.session != original_session
        answer = second.rpc(
            "project.management.operation.get",
            {
                "projectId": project,
                "operationId": request["operationId"],
                "requestHash": digest(request),
            },
        )
        assert answer["state"] == "applied"
        result = answer["result"]
        assert result["kind"] == action["kind"] and result["requestHash"] == digest(request)
        assert result["operationId"] == request["operationId"]
        assert (
            second.rpc(
                "project.management.operation.get",
                {
                    "projectId": project,
                    "operationId": request["operationId"],
                    "requestHash": digest(request),
                },
            )
            == answer
        )
    finally:
        code, stderr = second.close()
    assert code == 0 and stderr == b""
    assert database_hash(path) == before
    with sqlite3.connect(path) as db:
        assert (
            db.execute(
                "SELECT count(*) FROM management_receipts WHERE operation=?",
                (request["operationId"],),
            ).fetchone()[0]
            == 1
        )
        assert db.execute("SELECT count(*) FROM projects").fetchone()[0] == (
            2 if action["kind"] == "copy-current" else 1
        )
        if action["kind"] == "trash":
            assert result["lifecycleState"] == "trashed" and result["lifecycleVersion"] == 1
