"""Real formal ChangeSet stdio, with explicitly identified scheduler injection.

Only this test's processes/database are controlled. No Electron or test worker.
Raw wire is retained per session, including assertion failures and stderr.
"""

import base64
import hashlib
import json
import os
import queue
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest


def uid():
    return str(uuid4())


def fact(value='"A"', subject="urn:asset:A"):
    predicate = "urn:name"
    return {
        "id": digest([subject, predicate, value]),
        "subject": subject,
        "predicate": predicate,
        "object": value,
    }


def ontology(identity, *, references=()):
    return {
        "layer": "ontology",
        "id": identity,
        "value": {
            "triples": [],
            "singleValuedPredicates": [],
            "references": [{"layer": "ontology", "id": ref} for ref in references],
        },
    }


@pytest.fixture
def database(tmp_path):
    path, project = tmp_path / "formal.sqlite", uid()
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.create_project(project)
    store.close()
    return path, project


# Only the real execute_changeset sleep(0) yield is extended, while the ordinary
# stdio dispatcher keeps running. This is a scheduler mechanism fixture, not an
# assertion that the OS naturally delivers cancel before a very short commit.
GATED_CLI = r"""
import asyncio,inspect,sys
from pathlib import Path
gate=Path(sys.argv.pop(1)); original=asyncio.sleep
async def controlled(delay,*args,**kwargs):
    caller=inspect.currentframe().f_back.f_code.co_name
    if delay==0 and caller=='execute_changeset':
        gate.with_suffix('.waiting').touch()
        while not gate.exists():
            await original(.001)
    return await original(delay,*args,**kwargs)
asyncio.sleep=controlled
from ontolearn_engine.__main__ import main
main()
"""


class Session:
    def __init__(self, path, project, *, version=3, gate=None, executable=None):
        self.project = project
        self.trace_directory = Path(path).parent / "changeset-stdio-traces"
        self.version = version
        self.session = None
        self.client = uid()
        self.sent = []
        self.output = []
        self.notifications = []
        self.queue = queue.Queue()
        command = [str(executable)] if executable else [sys.executable, "-I"]
        if executable:
            assert gate is None
        elif gate is None:
            command += ["-m", "ontolearn_engine"]
        else:
            command += ["-c", GATED_CLI, str(gate)]
        if version == 3:
            command += ["--t01-internal-profile=business3"]
        environment = os.environ | {
            "ONTOLEARN_DB_PATH": str(path),
            "ONTOLEARN_ALLOWED_PROJECTS": json.dumps([project]),
            "ONTOLEARN_TEST_MODE": "0",
        }
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )

        def read():
            while line := self.process.stdout.readline():
                self.output.append(line)
                self.queue.put(line)
            self.queue.put(None)

        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        try:
            self.hello = self.call(
                "hello", {"supportedVersions": [version], "clientId": self.client}
            )
            assert self.hello["selectedVersion"] == version
            if version == 3:
                # Business3 authority comes from this actual session's explicit
                # selected-project open, not the legacy allowed-projects env.
                opened = self.call("project.open", {"projectId": project})
                assert opened["projectId"] == project
        except BaseException:
            self.close()
            raise

    def exchange(self, method, params, *, expect_closed=False):
        request = {
            "kind": "request",
            "protocolVersion": 2 if method == "hello" else self.version,
            "id": uid(),
            "engineSessionId": None if method == "hello" else self.session,
            "method": method,
            "params": params,
        }
        payload = json.dumps(request, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
        self.sent.append(payload)
        self.process.stdin.write(payload)
        self.process.stdin.flush()
        while True:
            line = self.queue.get(timeout=12)
            if line is None and expect_closed:
                return None
            assert line is not None, "formal engine ended before its response"
            assert line.endswith(b"\n") and len(line) <= 262145
            value = json.loads(line)
            validate = CONTRACT.validate_business3 if self.version == 3 else CONTRACT.validate
            assert validate("envelope", value), value
            if value["kind"] == "notification":
                self.notifications.append(value)
                continue
            assert value["id"] == request["id"] and value["method"] == method
            if method == "hello" and value["ok"]:
                self.session = value["engineSessionId"]
            else:
                assert value["engineSessionId"] == self.session
            return value

    def call(self, method, params):
        response = self.exchange(method, params)
        assert response["ok"], response
        return response["result"]

    def preview(self, plan, *, base=None):
        if base is None:
            base = self.call("project.get", {"projectId": self.project})["projectRevision"]
        return self.call(
            "changeset.preview",
            {"projectId": self.project, "baseRevision": base, "intent": "change", "plan": plan},
        )

    def document(self, preview):
        cursor, pages, raw = None, [], bytearray()
        for _ in range(1024):
            page = self.call(
                "changeset.diff.page",
                {
                    "projectId": self.project,
                    "previewHash": preview["previewHash"],
                    "documentKind": preview["manifest"]["documentKind"],
                    "pageSize": 200,
                    "cursor": cursor,
                },
            )
            pages.append(page)
            for segment in page["segments"]:
                data = base64.b64decode(segment["dataBase64"], validate=True)
                assert segment["byteOffset"] == len(raw)
                assert len(data) == segment["rawByteLength"]
                assert hashlib.sha256(data).hexdigest() == segment["sha256"]
                raw.extend(data)
            cursor = page["nextCursor"]
            if page["complete"]:
                break
        else:
            pytest.fail("formal Diff did not terminate within its finite budget")
        assert len(raw) == preview["manifest"]["totalBytes"]
        assert hashlib.sha256(raw).hexdigest() == preview["manifest"]["documentHash"]
        return json.loads(raw), cursor, pages

    def prepare(self, preview):
        assert preview["status"] == "ready", preview
        document, completion, _ = self.document(preview)
        confirmation = self.call(
            "changeset.confirm",
            {
                "projectId": self.project,
                "previewHash": preview["previewHash"],
                "completionCursor": completion,
            },
        )
        return document, confirmation

    def submit(self, preview):
        document, confirmation = self.prepare(preview)
        request = {
            "projectId": self.project,
            "operationId": uid(),
            "capability": "changeset.commit",
            "input": {
                "inputSnapshotId": confirmation["inputSnapshotId"],
                "scope": "asserted",
                "definitionId": "changeset",
                "parametersHash": confirmation["parametersHash"],
                "derivedResultIds": [],
                "preparedPlanRef": confirmation["preparedPlanRef"],
            },
            "confirmationRef": confirmation["confirmationRef"],
        }
        accepted = self.call("job.create", request)
        assert accepted["capability"] == "changeset.commit"
        assert accepted["commitProgress"]["mode"] == "atomic"
        return request, accepted, document

    def terminal(self, job):
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            current = self.call("job.get", {"projectId": self.project, "jobId": job["jobId"]})
            if current["state"] in {"succeeded", "failed", "cancelled"}:
                return current
            time.sleep(0.005)
        pytest.fail("formal ChangeSet did not reach its actual terminal state")

    def close(self):
        if not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=12)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)
            raise
        finally:
            self.reader.join(timeout=2)
            stderr = self.process.stderr.read()
            directory = self.trace_directory
            directory.mkdir(exist_ok=True)

            def raw(data):
                return {
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "base64": base64.b64encode(data).decode(),
                }

            record = {
                "command": self.process.args,
                "testMode": False,
                "returncode": self.process.returncode,
                "stdin": raw(b"".join(self.sent)),
                "stdout": raw(b"".join(self.output)),
                "stderr": raw(stderr),
            }
            (directory / f"{uid()}.json").write_text(
                json.dumps(record, indent=2) + "\n", encoding="utf-8"
            )
        assert self.process.returncode == 0 and stderr == b"", record


def test_formal_cli_commit_selective_undo_and_exact_operation_reopen(database):
    path, project = database
    session = Session(path, project)
    try:
        assert "changeset.preview" in session.hello["capabilities"]
        preview = session.preview(
            {
                "definitions": [ontology("Asset"), ontology("Pump", references=["Asset"])],
                "manual": [fact()],
            }
        )
        assert preview["status"] == "ready"
        assert session.call("project.get", {"projectId": project})["projectRevision"] == 0
        first, accepted, document = session.submit(preview)
        assert document and session.terminal(accepted)["state"] == "succeeded"
        assert session.call("job.create", first)["jobId"] == accepted["jobId"]
        other_fact = fact('"B"', "urn:asset:B")
        second, other, _ = session.submit(session.preview({"manual": [other_fact]}))
        assert session.terminal(other)["state"] == "succeeded"
        undo = session.call(
            "changeset.preview",
            {
                "projectId": project,
                "baseRevision": 2,
                "intent": "undo",
                "targetOperationId": first["operationId"],
            },
        )
        undone, undo_job, _ = session.submit(undo)
        completed = session.terminal(undo_job)
        assert completed["state"] == "succeeded"
        assert session.call("project.get", {"projectId": project})["projectRevision"] == 3
        marker = session.call(
            "operation.get", {"projectId": project, "operationId": undone["operationId"]}
        )
        assert marker["jobId"] == undo_job["jobId"] and marker["projectRevision"] == 3
        result = session.call(
            "result.get", {"projectId": project, "resultId": completed["resultRef"]["resultId"]}
        )
        assert result["kind"] == "receipt"
        assert result["inputSnapshotId"] == undone["input"]["inputSnapshotId"]
        binding = {
            "projectId": project,
            "resultId": completed["resultRef"]["resultId"],
            "inputSnapshotId": undone["input"]["inputSnapshotId"],
            "scope": "asserted",
            "parametersHash": undone["input"]["parametersHash"],
            "order": "ordinal+rowId:asc",
        }
        page = session.call("result.page", {"binding": binding, "pageSize": 200, "cursor": None})
        assert page["binding"] == binding and page["nextCursor"] is None
        assert len(page["rows"]) == 1
        assert str(UUID(page["rows"][0]["rowId"])) == page["rows"][0]["rowId"]
        assert page["rows"][0]["ordinal"] == 0
        assert page["rows"][0]["cells"] == [
            "commit.receipt.v1",
            undone["operationId"],
            3,
            marker["beforeSnapshotId"],
            marker["afterSnapshotId"],
            marker["planHash"],
        ]
        assert (
            session.call("job.cancel", {"projectId": project, "jobId": undo_job["jobId"]})[
                "disposition"
            ]
            == "alreadyTerminal"
        )
    finally:
        session.close()
    session = Session(path, project)
    try:
        for original, job in [(first, accepted), (second, other), (undone, undo_job)]:
            assert session.call("job.create", original)["jobId"] == job["jobId"]
            assert (
                session.call(
                    "operation.get", {"projectId": project, "operationId": original["operationId"]}
                )["jobId"]
                == job["jobId"]
            )
    finally:
        session.close()
    store = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        state = store.state(store._project(project))
        assert state["definitions"] == []
        assert state["facts"] == [
            {**other_fact, "owner": None, "source_row": None, "managed_value": None}
        ]
        assert store.project_checkpoint(store._project(project))["operationSequence"] == 3
    finally:
        store.close()
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT count(*) FROM operation_claims").fetchone()[0] == 3
        assert connection.execute("SELECT count(*) FROM app_receipts").fetchone()[0] == 3


def test_actual_dispatcher_cancel_before_formal_commit_gate(database, tmp_path):
    path, project = database
    gate = tmp_path / "release"
    session = Session(path, project, gate=gate)
    try:
        request, accepted, _ = session.submit(session.preview({"manual": [fact()]}))
        deadline = time.monotonic() + 5
        while not gate.with_suffix(".waiting").exists() and time.monotonic() < deadline:
            time.sleep(0.002)
        assert gate.with_suffix(".waiting").exists()
        assert (
            session.call("job.get", {"projectId": project, "jobId": accepted["jobId"]})["state"]
            == "running"
        )
        subscription = session.call(
            "job.subscribe", {"projectId": project, "jobId": accepted["jobId"]}
        )
        assert subscription["jobId"] == accepted["jobId"] and subscription["seq"] == 0
        session.call("job.cancel", {"projectId": project, "jobId": accepted["jobId"]})
        assert (
            session.call("job.get", {"projectId": project, "jobId": accepted["jobId"]})["state"]
            == "cancelling"
        )
        gate.touch()
        assert session.terminal(accepted)["state"] == "cancelled"
        assert session.notifications
        assert session.call(
            "job.unsubscribe",
            {
                "projectId": project,
                "jobId": accepted["jobId"],
                "subscriptionId": subscription["subscriptionId"],
            },
        ) == {"subscriptionId": subscription["subscriptionId"], "unsubscribed": True}
        assert (
            session.call(
                "operation.get", {"projectId": project, "operationId": request["operationId"]}
            )
            is None
        )
        assert session.call("project.get", {"projectId": project})["projectRevision"] == 0
    finally:
        gate.touch()
        session.close()
    store = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        assert store.state(store._project(project))["facts"] == []
        assert store.project_checkpoint(store._project(project))["operationSequence"] == 0
    finally:
        store.close()


def record(definition):
    return {
        "layer": definition["layer"],
        "id": definition["id"],
        "payload": json.dumps(
            definition["value"], sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ),
    }


def test_actual_cli_undo_impact_retains_both_aba_operations(database):
    path, project = database
    session = Session(path, project)
    try:
        original = ontology("Asset")
        changed = ontology("Asset")
        changed["value"]["triples"] = [
            {"subject": "urn:Asset", "predicate": "urn:label", "object": '"changed"'}
        ]
        commits = []
        for definition in [original, changed, original]:
            request, job, _ = session.submit(session.preview({"definitions": [definition]}))
            assert session.terminal(job)["state"] == "succeeded"
            commits.append(request["operationId"])
        conflict = session.call(
            "changeset.preview",
            {
                "projectId": project,
                "baseRevision": 3,
                "intent": "undo",
                "targetOperationId": commits[0],
            },
        )
        assert conflict["status"] == "conflict" and conflict["impactComplete"] is True
        assert "preparedPlanRef" not in conflict and "confirmationRef" not in conflict
        document, completion, _ = session.document(conflict)
        with sqlite3.connect(path) as connection:
            references = {
                operation: connection.execute(
                    "SELECT before_snapshot,after_snapshot FROM commit_evidence WHERE operation=?",
                    (operation,),
                ).fetchone()
                for operation in commits[1:]
            }
        assert document == [
            {
                "reason": "later-edit",
                "resource": ["definition", "ontology", "Asset"],
                "targetOperationId": commits[0],
                "operationId": operation,
                "revision": revision,
                "beforeSnapshotRef": references[operation][0],
                "afterSnapshotRef": references[operation][1],
                "before": record(before),
                "after": record(after),
            }
            for operation, revision, before, after in [
                (commits[1], 2, original, changed),
                (commits[2], 3, changed, original),
            ]
        ]
        response = session.exchange(
            "changeset.confirm",
            {
                "projectId": project,
                "previewHash": conflict["previewHash"],
                "completionCursor": completion,
            },
        )
        assert response["ok"] is False
        assert session.call("project.get", {"projectId": project})["projectRevision"] == 3
    finally:
        session.close()


def test_actual_cli_reference_impact_is_complete_and_not_confirmable(database):
    path, project = database
    session = Session(path, project)
    try:
        first, job, _ = session.submit(session.preview({"definitions": [ontology("Asset")]}))
        assert session.terminal(job)["state"] == "succeeded"
        dependent = ontology("Pump", references=["Asset"])
        _, job, _ = session.submit(session.preview({"definitions": [dependent]}))
        assert session.terminal(job)["state"] == "succeeded"
        conflict = session.call(
            "changeset.preview",
            {
                "projectId": project,
                "baseRevision": 2,
                "intent": "undo",
                "targetOperationId": first["operationId"],
            },
        )
        assert conflict["status"] == "conflict" and conflict["impactComplete"] is True
        assert "preparedPlanRef" not in conflict and "confirmationRef" not in conflict
        document, completion, _ = session.document(conflict)
        assert document == [
            {
                "reason": "reference-block",
                "resource": ["definition", "ontology", "Pump"],
                "target": ["definition", "ontology", "Asset"],
                "definition": record(dependent),
                "targetOperationId": first["operationId"],
            }
        ]
        assert not session.exchange(
            "changeset.confirm",
            {
                "projectId": project,
                "previewHash": conflict["previewHash"],
                "completionCursor": completion,
            },
        )["ok"]
        assert session.call("project.get", {"projectId": project})["projectRevision"] == 2
    finally:
        session.close()


def test_default_protocol_does_not_advertise_or_accept_formal_changesets(database):
    path, project = database
    # The default profile owns format2; a format3 database intentionally refuses
    # startup and cannot be used to test the default protocol's request gate.
    path = path.with_name("legacy.sqlite")
    store = JobStore(path, contract=CONTRACT)
    store.create_project(project)
    store.close()
    session = Session(path, project, version=2)
    try:
        assert "changeset.preview" not in session.hello["capabilities"]
        response = session.exchange(
            "changeset.preview",
            {"projectId": project, "baseRevision": 0, "intent": "change", "plan": {}},
            expect_closed=True,
        )
        # An unknown method cannot be reflected into a valid legacy response.
        # The legacy profile closes its stream without accepting a write.
        assert response is None
    finally:
        session.close()
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT count(*) FROM operation_claims").fetchone()[0] == 0
