"""Real SQLite/CLI stdio; explicitly marked subprocess injections are not OS faults."""

import json
import os
import queue
import sqlite3
import subprocess
import sys
import threading
import time

import pytest
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT, REGISTRY_HASH
from ontolearn_engine.storage import Store
from test_job_store import uid
from test_project_startup_contract import request
from test_storage import make_legacy

PROFILE = "--t01-internal-profile=business3"


def environment(path, projects=()):
    return os.environ | {
        "ONTOLEARN_DB_PATH": str(path),
        "ONTOLEARN_ALLOWED_PROJECTS": json.dumps(list(projects)),
        "ONTOLEARN_TEST_MODE": "1",
    }


def run_cli(path, arguments=(PROFILE,), payload=b"", env=None, script=None):
    command = [sys.executable, "-I"] + (["-c", script] if script else ["-m", "ontolearn_engine"])
    return subprocess.run(
        command + list(arguments),
        input=payload,
        capture_output=True,
        timeout=12,
        env=env or environment(path),
    )


def diagnosis(result, code):
    assert result.returncode == 1 and result.stderr == b""
    assert (
        result.stdout.endswith(b"\n")
        and result.stdout.count(b"\n") == 1
        and b"\r" not in result.stdout
    )
    value = json.loads(result.stdout)
    assert value["error"]["code"] == code
    assert CONTRACT.validate_startup_failure(value, len(result.stdout) - 1, REGISTRY_HASH)
    return value


@pytest.mark.parametrize("source", ["new", "0", "1", "2", "3"])
def test_actual_migration_and_three_reopen(tmp_path, source):
    path, backup = tmp_path / "db", tmp_path / "backup"
    if source == "0":
        with sqlite3.connect(path) as db:
            db.execute("PRAGMA user_version=0")
    elif source == "1":
        make_legacy(path)
    elif source in {"2", "3"}:
        existing = JobStore(path, contract=CONTRACT, target_format=int(source))
        existing.close()
    before = path.read_bytes() if path.exists() else None
    arguments = [PROFILE, f"--t01-internal-backup={backup}"]
    result = run_cli(path, arguments, json.dumps(request()).encode() + b"\n")
    assert result.returncode == 0 and result.stderr == b""
    hello = json.loads(result.stdout)
    assert hello["protocolVersion"] == 2 and hello["result"]["selectedVersion"] == 3
    assert hello["result"]["registryHash"] == REGISTRY_HASH
    assert CONTRACT.validate_business3("response", hello)
    if source in {"0", "1", "2"}:
        assert backup.exists()
        with sqlite3.connect(backup) as saved:
            assert saved.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert saved.execute("PRAGMA user_version").fetchone()[0] == int(source)
        assert before is not None
    else:
        assert not backup.exists()
    # A second real process reopens3; no migration backup is needed or replaced.
    result = run_cli(path, payload=json.dumps(request()).encode() + b"\n")
    assert result.returncode == 0 and json.loads(result.stdout)["result"]["selectedVersion"] == 3
    opened = JobStore(path, contract=CONTRACT, target_format=3)
    opened.close()  # Actual process exited and released its lifetime lease.


@pytest.mark.parametrize("target", [2, 3])
def test_real_future_and_default_two_behavior(tmp_path, target):
    path = tmp_path / "future"
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version=4")
    result = run_cli(path, (PROFILE,) if target == 3 else ())
    if target == 3:
        diagnosis(result, "PROJECT_FORMAT_UNSUPPORTED")
    else:
        assert (
            result.returncode == 1
            and result.stdout == b""
            and result.stderr == b"ENGINE_SESSION_FAILED\n"
        )
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 4


def test_real_writer_busy(tmp_path):
    path = tmp_path / "db"
    owner = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        value = diagnosis(run_cli(path), "STORAGE_BUSY")
        assert value["error"]["params"] == {"retryAfterMs": 250}
    finally:
        owner.close()
    assert run_cli(path).returncode == 0


@pytest.mark.parametrize("kind", ["store3", "job3"])
def test_real_bad_structure_never_hello_and_does_not_repair(tmp_path, kind):
    path = tmp_path / "db"
    owner = Store(path, target_format=3)
    owner.close()
    with sqlite3.connect(path) as db:
        if kind == "store3":
            db.execute("DROP TABLE app_format")
        else:
            db.execute("CREATE TABLE jobs(wrong TEXT)")
    for _ in range(2):
        diagnosis(run_cli(path), "STORAGE_FAILURE")
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 3
        if kind == "job3":
            assert db.execute("PRAGMA table_info(jobs)").fetchall()[0][1] == "wrong"


@pytest.mark.parametrize("failure", ["missing", "existing"])
def test_real_backup_refusal_preserves_two(tmp_path, failure):
    path, backup = tmp_path / "db", tmp_path / "backup"
    store = JobStore(path, contract=CONTRACT)
    store.close()
    args = [PROFILE]
    if failure == "existing":
        backup.write_bytes(b"existing-backup-original")
        args.append(f"--t01-internal-backup={backup}")
    diagnosis(run_cli(path, args), "INTERNAL_ERROR")
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 2
    if failure == "existing":
        assert backup.read_bytes() == b"existing-backup-original"


def test_real_allowed_configuration_failure_and_lease_release(tmp_path):
    path = tmp_path / "db"
    env = environment(path)
    env["ONTOLEARN_ALLOWED_PROJECTS"] = "not json"
    diagnosis(run_cli(path, env=env), "INTERNAL_ERROR")
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.close()


def test_injected_reconcile_failure_uses_real_producer_after_real_store(tmp_path):
    path = tmp_path / "db"
    script = """
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project.format3 import Format3Fault
from ontolearn_engine.__main__ import main
def fail(self): raise Format3Fault("structure")
JobStore.reconcile_jobs = fail
main()
"""
    diagnosis(run_cli(path, script=script), "STORAGE_FAILURE")
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.close()


def test_injected_missing_resources_has_no_trusted_diagnosis(tmp_path):
    script = """
import sys
from ontolearn_engine.__main__ import main
class Block:
 def find_spec(self, fullname, *args):
  if fullname == "ontolearn_engine.resources": raise ImportError("private path")
sys.meta_path.insert(0, Block())
main()
"""
    result = run_cli(tmp_path / "db", script=script)
    assert (
        result.returncode == 1
        and result.stdout == b""
        and result.stderr == b"ENGINE_SESSION_FAILED\n"
    )


class Session:
    def __init__(self, path, project):
        self.process = subprocess.Popen(
            [sys.executable, "-I", "-m", "ontolearn_engine", PROFILE],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment(path, [project]),
        )
        self.inbox, self.notifications = queue.Queue(), []

        def read():
            for raw in self.process.stdout:
                self.inbox.put(raw)

        self.thread = threading.Thread(target=read, daemon=True)
        self.thread.start()
        self.session = None
        hello = self.call("hello", {"supportedVersions": [3], "clientId": uid()})
        self.session = hello["engineSessionId"]

    def call(self, method, params):
        q = request(method, params, self.session, 2 if method == "hello" else 3)
        self.process.stdin.write(json.dumps(q).encode() + b"\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            value = json.loads(self.inbox.get(timeout=max(0.01, deadline - time.monotonic())))
            assert CONTRACT.validate_business3("envelope", value)
            if value["kind"] == "notification":
                self.notifications.append(value)
                continue
            assert value["id"] == q["id"]
            assert CONTRACT.matches_business3_response(q, value, REGISTRY_HASH)
            assert value["ok"], value.get("error", value)
            return value["result"]
        raise AssertionError("real CLI timeout")

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=8)
        except BaseException:
            self.process.kill()
            self.process.wait()
            raise
        self.thread.join(timeout=1)
        assert self.process.returncode == 0
        assert self.process.stderr.read() == b""
        self.process.stdout.close()
        self.process.stderr.close()


def test_real_job_receipt_retry_and_restart_bindings(tmp_path):
    path, project = tmp_path / "db", uid()
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.create_project(project)
    snapshot = store.project_get(project)
    params_hash = store.put_blob(project, {})
    prepared = store.prepare_plan(
        project,
        snapshot["projectRevision"],
        {"definitions": [{"layer": "rule", "id": "runtime3", "value": {"enabled": True}}]},
        actor=uid(),
        permission="write",
    )
    store.close()
    operation = uid()
    params = {
        "projectId": project,
        "operationId": operation,
        "capability": "test.atomic",
        "input": {
            "inputSnapshotId": snapshot["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "probe",
            "parametersHash": params_hash,
            "derivedResultIds": [],
            "preparedPlanRef": prepared["preparedPlanRef"],
        },
        "confirmationRef": prepared["confirmationRef"],
    }
    session = Session(path, project)
    try:
        assert session.call("project.get", {"projectId": project})["formatVersion"] == 3
        job = session.call("job.create", params)
        session.call("job.subscribe", {"projectId": project, "jobId": job["jobId"]})
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            current = session.call("job.get", {"projectId": project, "jobId": job["jobId"]})
            if current["state"] in {"succeeded", "failed", "cancelled"}:
                break
            time.sleep(0.01)
        assert current["state"] == "succeeded", current
        assert session.call("job.create", params)["jobId"] == job["jobId"]
        result = session.call(
            "result.get", {"projectId": project, "resultId": current["resultRef"]["resultId"]}
        )
        assert result["inputSnapshotId"] == snapshot["inputSnapshotId"]
        assert any(
            n["event"] == "job.state" and n["data"]["state"] == "succeeded"
            for n in session.notifications
        )
    finally:
        session.close()
    session = Session(path, project)
    try:
        operation_result = session.call(
            "operation.get", {"projectId": project, "operationId": operation}
        )
        assert operation_result["jobId"] == job["jobId"]
        assert session.call("job.create", params)["jobId"] == job["jobId"]
    finally:
        session.close()
    with sqlite3.connect(path) as db:
        assert (
            db.execute(
                "SELECT count(*) FROM operation_claims WHERE operation=?", (operation,)
            ).fetchone()[0]
            == 1
        )


@pytest.mark.parametrize("profile,offered", [(2, [2]), (2, [3]), (3, [2])])
def test_true_default_and_protocol_incompatible_matrix(tmp_path, profile, offered):
    q = request(params={"supportedVersions": offered, "clientId": uid()})
    result = run_cli(
        tmp_path / "db", () if profile == 2 else (PROFILE,), json.dumps(q).encode() + b"\n"
    )
    assert result.returncode == 0 and result.stderr == b""
    value = json.loads(result.stdout)
    if offered == [2] and profile == 2:
        assert value["ok"] and value["result"]["selectedVersion"] == 2
    else:
        assert not value["ok"] and value["engineSessionId"] is None
        assert value["error"]["code"] == "VERSION_INCOMPATIBLE"
        assert value["error"]["params"] == {"supportedVersions": [profile]}


@pytest.mark.parametrize("mode", ["repeat", "unknown-session", "wrong-version", "rejected-first"])
def test_real_same_chunk_terminal_does_not_consume_later_hello(tmp_path, mode):
    first = request()
    if mode == "rejected-first":
        first["params"]["supportedVersions"] = [2]
    second = (
        request()
        if mode in {"repeat", "rejected-first"}
        else request("session.ping", {"nonce": uid()}, uid(), 2 if mode == "wrong-version" else 3)
    )
    payload = b"".join(json.dumps(q).encode() + b"\n" for q in [first, second, request()])
    result = run_cli(tmp_path / "db", payload=payload)
    assert result.returncode == 0 and result.stderr == b""
    lines = result.stdout.splitlines()
    assert len(lines) == 1
    response = json.loads(lines[0])
    assert response["ok"] == (mode != "rejected-first")
    assert response["kind"] == "response"  # Never a new startup diagnosis after protocol input.


def test_actual_default_two_rejects_three_and_ignores_profile_environment(tmp_path):
    path = tmp_path / "three"
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.close()
    rejected = run_cli(path, ())
    assert (
        rejected.returncode == 1
        and rejected.stdout == b""
        and rejected.stderr == b"ENGINE_SESSION_FAILED\n"
    )
    path = tmp_path / "two"
    env = environment(path)
    env["ONTOLEARN_INTERNAL_PROFILE"] = "business3"
    env["ONTOLEARN_TARGET_FORMAT"] = "3"
    env["ONTOLEARN_INTERNAL_BACKUP"] = "/untrusted"
    q = request(params={"supportedVersions": [2], "clientId": uid()})
    result = run_cli(path, (), json.dumps(q).encode() + b"\n", env=env)
    assert result.returncode == 0 and json.loads(result.stdout)["result"]["selectedVersion"] == 2
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 2


def test_actual_reconcile_preserves_commit_and_fails_unfinished(tmp_path):
    from test_job_store import create

    path, project = tmp_path / "db", uid()
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.create_project(project)
    store.project = project
    accepted = create(store)
    committed = create(store, "test.atomic")
    store.start_job(committed["jobId"])
    terminal = store.commit_job(committed["jobId"])
    marker = store.operation_get(project, committed["operationId"])
    revision = store.project_get(project)["projectRevision"]
    store.close()
    session = Session(path, project)
    try:
        failed = session.call("job.get", {"projectId": project, "jobId": accepted["jobId"]})
        assert failed["state"] == "failed" and failed["error"]["code"] == "ENGINE_EXITED"
        assert (
            session.call("job.get", {"projectId": project, "jobId": terminal["jobId"]}) == terminal
        )
        assert (
            session.call(
                "operation.get", {"projectId": project, "operationId": committed["operationId"]}
            )
            == marker
        )
        assert session.call("project.get", {"projectId": project})["projectRevision"] == revision
    finally:
        session.close()


def test_injected_failure_after_ready_never_returns_startup_record(tmp_path):
    script = """
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.__main__ import main
async def fail(self):
 if self.session is not None: raise RuntimeError("not for output")
Coordinator.tick = fail
main()
"""
    result = run_cli(tmp_path / "db", script=script, payload=json.dumps(request()).encode() + b"\n")
    assert result.returncode == 1 and result.stderr == b"ENGINE_SESSION_FAILED\n"
    value = json.loads(result.stdout)
    assert value["kind"] == "response" and value["ok"]
