"""Canonical caller rejection stays resumable; unknown faults retain the real host."""

import asyncio
import base64
import json
import os
import sys
from copy import deepcopy

import pytest
from ontolearn_engine.project import domain_changesets
from ontolearn_engine.project.transactions import ProjectTransactions
from ontolearn_engine.storage import Store, digest
from test_mainline_dispatch import (
    confirmed_job,
    create,
    drain_owned_changesets,
    exchange,
    uid,
)
from test_mainline_dispatch import owned as owned

ALIAS = '"typed string"^^<http://www.w3.org/2001/XMLSchema#string>'
PLAIN = '"typed string"'


def fact(value):
    triple = ["urn:manual-rejection:subject", "urn:manual-rejection:predicate", value]
    return dict(
        zip(("id", "subject", "predicate", "object"), [digest(triple), *triple], strict=True)
    )


def change(project, value=PLAIN, base=0):
    return {
        "projectId": project,
        "baseRevision": base,
        "intent": "change",
        "plan": {"manual": [fact(value)]},
    }


def read(actor, project):
    reply = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert reply["ok"], reply
    return reply["result"]


def assert_rejected(reply):
    assert not reply["ok"] and "result" not in reply, reply
    assert reply["error"]["code"] == "INVALID_REQUEST", reply
    assert reply["error"]["messageKey"] == "protocol.invalidRequest", reply
    assert reply["error"]["params"] == {"field": "params"}, reply
    assert ALIAS not in json.dumps(reply, ensure_ascii=False)


def test_noncanonical_manual_rejected_without_mutation_then_same_owner_commits(owned, tmp_path):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    host = actor.mainline
    identities = (host.owner_id, host.host, host.session, host.generation)
    before = read(actor, project)
    database = "\n".join(store._db.iterdump())
    request = change(project, ALIAS)
    original = deepcopy(request)
    with pytest.raises(ValueError, match="Canonical RDF object required"):
        Store._fact(request["plan"]["manual"][0])
    refused = exchange(actor, "changeset.preview", request)
    assert_rejected(refused)
    assert request == original  # No caller normalization, new host or new selection.
    assert read(actor, project) == before
    assert "\n".join(store._db.iterdump()) == database
    assert actor.mainline is host and not host.hold and host.replies == {}
    assert (host.owner_id, host.host, host.session, host.generation) == identities
    accepted = confirmed_job(actor, project, change(project))
    drain_owned_changesets(actor)
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    assert store.operation_get(project, accepted["operationId"])["jobId"] == accepted["jobId"]
    after = read(actor, project)
    assert after["domain"]["projectRevision"] == 1
    assert after["domain"]["state"]["facts"] == [
        {**fact(PLAIN), "owner": None, "source_row": None, "managed_value": None}
    ]
    (tmp_path / "coordinator-trace.json").write_text(
        json.dumps({"before": before, "refused": refused, "canonicalJob": accepted, "after": after})
    )


def test_original_fact_id_survives_edit_and_undo(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    confirmed_job(actor, project, change(project))
    drain_owned_changesets(actor)
    original_id = fact(PLAIN)["id"]
    edited = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 1,
            "intent": "change",
            "plan": {"edits": {original_id: '"changed"'}},
        },
    )
    drain_owned_changesets(actor)
    current = read(actor, project)["domain"]["state"]["facts"]
    assert current[0]["id"] == original_id and current[0]["object"] == '"changed"'
    assert current[0]["id"] != fact('"changed"')["id"]
    undone = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 2,
            "intent": "undo",
            "targetOperationId": edited["operationId"],
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, undone["jobId"])["state"] == "succeeded"
    restored = read(actor, project)["domain"]["state"]["facts"]
    assert restored[0]["id"] == original_id and restored[0]["object"] == PLAIN


@pytest.mark.parametrize("failure", ["term", "preview", "sqlite-integrity", "snapshot-integrity"])
def test_non_input_failures_keep_original_unknown_and_hold(owned, monkeypatch, failure, tmp_path):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    before = read(actor, project)
    host = actor.mainline
    corrupt_reads = []

    def unexpected(*args, **kwargs):
        # Even identical text must not classify an exception by its message.
        raise ValueError("Canonical RDF object required; derive ID from term(value).n3()")

    if failure == "term":
        monkeypatch.setattr(domain_changesets, "term", unexpected)
    elif failure == "preview":
        monkeypatch.setattr(ProjectTransactions, "preview", unexpected)
    elif failure == "sqlite-integrity":
        store._db.execute(
            "CREATE TRIGGER reject_fixture_fact BEFORE INSERT ON facts "
            "BEGIN SELECT RAISE(ABORT, 'private fixture constraint'); END"
        )
    else:
        # Seed only this owned fixture's corrupt row, then restore the exact SQL
        # guard before any receiver call. This is not physical SQLite qualification.
        trigger = store._db.execute(
            "SELECT sql FROM sqlite_master WHERE name='immutable_snapshots_UPDATE'"
        ).fetchone()[0]
        store._db.execute("DROP TRIGGER immutable_snapshots_UPDATE")
        try:
            store._db.execute(
                "UPDATE snapshots SET payload='{}' WHERE id=?", (before["inputSnapshotId"],)
            )
        finally:
            store._db.execute(trigger)
        with pytest.raises(ValueError, match="Snapshot integrity failure"):
            store.load_snapshot(before["inputSnapshotId"])
        original_load = store.load_snapshot

        def observe_corrupt_read(identity):
            try:
                return original_load(identity)
            except ValueError:
                corrupt_reads.append(identity)
                raise

        monkeypatch.setattr(store, "load_snapshot", observe_corrupt_read)
    database = "\n".join(store._db.iterdump())
    refused = exchange(actor, "changeset.preview", change(project))
    assert not refused["ok"] and refused["error"]["code"] == "INTERNAL_ERROR", refused
    assert host.hold and actor.mainline is host
    if failure == "snapshot-integrity":
        assert before["inputSnapshotId"] in corrupt_reads
    unknown = dict(host.replies)
    assert len(unknown) == 1 and all(item.unknown for item in unknown.values())
    assert "\n".join(store._db.iterdump()) == database
    for request in (
        ("project.read", {"projectId": project, "editor": "ontology"}),
        ("changeset.preview", change(project, ALIAS)),
    ):
        denied = exchange(actor, *request)
        assert not denied["ok"] and denied["error"]["code"] == "STORAGE_FAILURE", denied
    assert host.hold and all(host.replies[key] is value for key, value in unknown.items())
    assert all(item.unknown for item in unknown.values())
    (tmp_path / "unknown-trace.json").write_text(
        json.dumps(
            {
                "fault": failure,
                "refused": refused,
                "held": host.hold,
                "unknownIds": list(unknown),
                "corruptSnapshotReads": corrupt_reads,
            }
        )
    )


def test_real_stdio_rejection_readback_and_canonical_confirm_job_marker(tmp_path):
    async def run():
        env = {**os.environ, "ONTOLEARN_DB_PATH": str(tmp_path / "stdio.sqlite")}
        env.pop("ONTOLEARN_TEST_MODE", None)
        env.pop("ONTOLEARN_ALLOWED_PROJECTS", None)
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "ontolearn_engine",
            "--t01-internal-profile=business3",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        session = None
        wire = []

        async def call(method, params):
            request = {
                "kind": "request",
                "id": uid(),
                "protocolVersion": 2 if method == "hello" else 3,
                "engineSessionId": session,
                "method": method,
                "params": params,
            }
            process.stdin.write((json.dumps(request, ensure_ascii=False) + "\n").encode())
            wire.append({"sent": request})
            await process.stdin.drain()
            while True:
                raw = await asyncio.wait_for(process.stdout.readline(), 10)
                assert raw, f"stdio EOF, exit={process.returncode}"
                response = json.loads(raw)
                wire.append({"received": response})
                if response.get("id") == request["id"]:
                    if session is not None:
                        assert response["engineSessionId"] == session
                    return response

        async def ok(method, params):
            response = await call(method, params)
            assert response["ok"], response
            return response["result"]

        try:
            hello = await ok("hello", {"supportedVersions": [3], "clientId": uid()})
            session = hello["engineSessionId"]
            created = await ok(
                "project.create",
                {
                    "requestVersion": 1,
                    "operationId": uid(),
                    "name": "同宿主规范输入",
                    "initialization": {"kind": "blank"},
                },
            )
            project = created["projectId"]
            read_params = {"projectId": project, "editor": "ontology"}
            before = await ok("project.read", read_params)
            assert_rejected(await call("changeset.preview", change(project, ALIAS)))
            assert await ok("project.read", read_params) == before
            ready = await ok("changeset.preview", change(project))
            assert ready["status"] == "ready"
            cursor, parts = None, []
            while True:
                page = await ok(
                    "changeset.diff.page",
                    {
                        "projectId": project,
                        "previewHash": ready["previewHash"],
                        "documentKind": "diff",
                        "pageSize": 1,
                        "cursor": cursor,
                    },
                )
                parts.extend(page["segments"])
                cursor = page["nextCursor"]
                if page["complete"]:
                    break
            document = json.loads(b"".join(base64.b64decode(p["dataBase64"]) for p in parts))
            assert digest(document) == ready["manifest"]["documentHash"]
            assert document[0]["after"]["object"] == PLAIN
            confirmation = await ok(
                "changeset.confirm",
                {
                    "projectId": project,
                    "previewHash": ready["previewHash"],
                    "completionCursor": cursor,
                },
            )
            operation = uid()
            job = await ok(
                "job.create",
                {
                    "projectId": project,
                    "operationId": operation,
                    "capability": "changeset.commit",
                    "confirmationRef": confirmation["confirmationRef"],
                    "input": {
                        "inputSnapshotId": confirmation["inputSnapshotId"],
                        "scope": "asserted",
                        "definitionId": "changeset",
                        "parametersHash": confirmation["parametersHash"],
                        "derivedResultIds": [],
                        "preparedPlanRef": confirmation["preparedPlanRef"],
                    },
                },
            )
            deadline = asyncio.get_running_loop().time() + 10
            while job["state"] in {"queued", "running", "cancelling"}:
                assert asyncio.get_running_loop().time() < deadline, job
                await asyncio.sleep(0.01)
                job = await ok("job.get", {"projectId": project, "jobId": job["jobId"]})
            assert job["state"] == "succeeded", job
            marker = await ok("operation.get", {"projectId": project, "operationId": operation})
            assert marker["jobId"] == job["jobId"]
            after = await ok("project.read", read_params)
            assert after["domain"]["projectRevision"] == 1
            assert after["domain"]["state"]["facts"][0]["object"] == PLAIN
            assert session == hello["engineSessionId"]
        finally:
            process.stdin.close()
            try:
                await asyncio.wait_for(process.wait(), 10)
            finally:
                if process.returncode is None:
                    process.kill()
                    await process.wait()
                (tmp_path / "stdio-wire.json").write_text(json.dumps(wire, ensure_ascii=False))
        assert process.returncode == 0, (await process.stderr.read()).decode()

    asyncio.run(run())
