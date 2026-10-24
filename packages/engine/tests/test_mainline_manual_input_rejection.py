"""Canonical caller rejection stays resumable; unknown faults retain the real host."""

import asyncio
import base64
import json
import os
import sys
from copy import deepcopy

import pytest
from ontolearn_engine import rdf_snapshot
from ontolearn_engine.project import domain_changesets
from ontolearn_engine.project.transactions import ProjectTransactions
from ontolearn_engine.storage import Store, canonical, digest
from rdflib.exceptions import ParserError
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
R02_SYNTAX_CASES = [
    (family, value)
    for family in ("manual", "edit")
    for value in ('"abc', '"设备编号', '"abc"^^', '""^^', '"""abc')
]
URLSPLIT_INPUT_CASES = [
    pytest.param(family, value, id=f"urlsplit-{family}-{index}")
    for family in ("manual", "edit")
    for index, value in enumerate(
        ("<http://[>", "<http://]>", "<http://[invalid]>", "<http://example.com／path>")
    )
]
MANUAL_IRI_FIELD_CASES = [
    pytest.param(field, value, id=f"manual-iri-{field}-{index}")
    for field in ("subject", "predicate")
    for index, value in enumerate(
        ("http://[", "http://]", "http://[invalid]", "http://example.com／path")
    )
]


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


@pytest.mark.parametrize(
    ("family", "value"),
    [
        ("manual", ALIAS),
        ("manual", "泵站A"),
        ("edit", ALIAS),
        ("edit", "泵站A"),
        ("manual", "[]"),
        ("manual", '"x"^^<../relative>'),
        ("edit", '"x"^^<../relative>'),
        ("manual", r'"x"^^<urn:\U00110000>'),
        ("edit", r'"x"^^<urn:\U00110000>'),
    ]
    + R02_SYNTAX_CASES
    + URLSPLIT_INPUT_CASES
    + MANUAL_IRI_FIELD_CASES,
)
def test_real_stdio_rejection_readback_and_canonical_confirm_job_marker(tmp_path, family, value):
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
        session, wire = None, []

        async def call(method, params):
            request = {
                "kind": "request",
                "id": uid(),
                "protocolVersion": 2 if method == "hello" else 3,
                "engineSessionId": session,
                "method": method,
                "params": params,
            }
            wire.append({"sent": request})
            process.stdin.write((json.dumps(request, ensure_ascii=False) + "\n").encode())
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
            assert response["ok"], canonical(response)
            return response["result"]

        async def commit(request):
            ready = await ok("changeset.preview", request)
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
            expected = (
                next(iter(request["plan"]["edits"].values()))
                if "edits" in request["plan"]
                else request["plan"]["manual"][0]["object"]
            )
            assert document[0]["after"]["object"] == expected
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
            return job, marker

        try:
            hello = await ok("hello", {"supportedVersions": [3], "clientId": uid()})
            session = hello["engineSessionId"]
            project = (
                await ok(
                    "project.create",
                    {
                        "requestVersion": 1,
                        "operationId": uid(),
                        "name": "同宿主规范输入",
                        "initialization": {"kind": "blank"},
                    },
                )
            )["projectId"]
            await commit(change(project))
            base = 1
            params = {"projectId": project, "editor": "ontology"}
            before = await ok("project.read", params)
            refused = await call("changeset.preview", input_change(project, family, value, base))
            current = await call("project.get", {"projectId": project})
            after_error = await call("project.read", params)
            (tmp_path / "stdio-rejection-trace.json").write_text(
                json.dumps(
                    {
                        "before": before,
                        "refused": refused,
                        "current": current,
                        "afterError": after_error,
                    },
                    ensure_ascii=False,
                )
            )
            assert_rejected(refused)
            assert current["ok"] and current["result"]["projectRevision"] == base
            assert after_error["ok"] and after_error["result"] == before
            expected = '"changed"' if family == "edit" else '"next"'
            valid = (
                input_change(project, "edit", expected, base)
                if family == "edit"
                else change(project, expected, base)
            )
            job, marker = await commit(valid)
            after = await ok("project.read", params)
            assert after["domain"]["projectRevision"] == base + 1
            facts = {item["id"]: item for item in after["domain"]["state"]["facts"]}
            original = before["domain"]["state"]["facts"][0]
            assert original["id"] == fact(PLAIN)["id"]
            if family != "edit":
                added = {**fact(expected), "owner": None, "source_row": None, "managed_value": None}
                assert facts == {original["id"]: original, added["id"]: added}
            else:
                assert facts == {original["id"]: {**original, "object": expected}}
            assert session == hello["engineSessionId"]
            (tmp_path / "stdio-recovery-trace.json").write_text(
                json.dumps({"job": job, "marker": marker, "after": after}, ensure_ascii=False)
            )
        finally:
            process.stdin.close()
            forced = False
            try:
                await asyncio.wait_for(process.wait(), 10)
            finally:
                if process.returncode is None:
                    forced = True
                    process.kill()
                    await process.wait()
                (tmp_path / "stdio-wire.json").write_text(json.dumps(wire, ensure_ascii=False))
                (tmp_path / "stdio.stderr.txt").write_bytes(await process.stderr.read())
                (tmp_path / "stdio-exit.json").write_text(
                    json.dumps({"returnCode": process.returncode, "forcedKill": forced})
                )
        assert process.returncode == 0 and not forced

    asyncio.run(run())


INPUT_CASES = [
    ("manual", "泵站A"),
    ("edit", "泵站A"),
    ("edit", ALIAS),
    ("manual", "[]"),
    ("manual", '"x"^^<../relative>'),
    ("edit", '"x"^^<../relative>'),
    ("manual", r'"x"^^<urn:\U00110000>'),
    ("edit", r'"x"^^<urn:\U00110000>'),
    ("manual", '"one", "two"'),
    ("manual", "<urn:missing"),
    ("manual", "<urn:bad space>"),
]


def input_change(project, family, value, base):
    request = change(project, value, base)
    if family == "edit":
        request["plan"] = {"edits": {fact(PLAIN)["id"]: value}}
    elif family in {"subject", "predicate"}:
        record = fact(PLAIN)
        record[family] = value
        record["id"] = digest([record["subject"], record["predicate"], record["object"]])
        request["plan"] = {"manual": [record]}
    return request


@pytest.mark.parametrize(
    ("family", "value"),
    INPUT_CASES + R02_SYNTAX_CASES + URLSPLIT_INPUT_CASES + MANUAL_IRI_FIELD_CASES,
)
def test_known_caller_objects_reject_then_same_host_reads_and_commits(
    owned, tmp_path, family, value
):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    confirmed_job(actor, project, change(project))
    drain_owned_changesets(actor)
    host, connection = actor.mainline, store._db
    lease = store._format3_lease
    identities = (host.owner_id, host.host, host.session, host.generation)
    selected = host.selected
    before = read(actor, project)
    database = "\n".join(connection.iterdump())
    request = input_change(project, family, value, 1)
    original = deepcopy(request)
    refused = exchange(actor, "changeset.preview", request)
    # Preserve the real post-error read responses even on the RED baseline.
    current = exchange(actor, "project.get", {"projectId": project})
    after_error = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    trace = {
        "inputFamily": family,
        "request": original,
        "before": before,
        "refused": refused,
        "current": current,
        "afterError": after_error,
        "held": host.hold,
        "unknown": [key for key, item in host.replies.items() if item.unknown],
    }
    path = tmp_path / "typed-rejection-trace.json"
    path.write_text(json.dumps(trace, ensure_ascii=False))
    assert_rejected(refused)
    assert current["ok"] and current["result"]["projectRevision"] == 1, canonical(current)
    assert after_error["ok"] and after_error["result"] == before, canonical(after_error)
    assert request == original and "\n".join(connection.iterdump()) == database
    assert actor.mainline is host and store._db is connection and host.selected is selected
    assert store._format3_lease is lease
    assert (host.owner_id, host.host, host.session, host.generation) == identities
    assert not host.hold and host.replies == {}
    valid = (
        change(project, '"next"', 1)
        if family != "edit"
        else input_change(project, "edit", '"next"', 1)
    )
    accepted = confirmed_job(actor, project, valid)
    drain_owned_changesets(actor)
    job = store.get_job(project, accepted["jobId"])
    marker = exchange(
        actor, "operation.get", {"projectId": project, "operationId": accepted["operationId"]}
    )
    assert job["state"] == "succeeded" and marker["ok"]
    assert marker["result"]["jobId"] == accepted["jobId"]
    after = read(actor, project)
    assert after["domain"]["projectRevision"] == 2
    if family == "edit":
        expected = deepcopy(before["domain"]["state"]["facts"])
        expected[0]["object"] = '"next"'
        assert after["domain"]["state"]["facts"] == expected
    else:
        facts = {item["id"]: item for item in after["domain"]["state"]["facts"]}
        original_fact = before["domain"]["state"]["facts"][0]
        added = {**fact('"next"'), "owner": None, "source_row": None, "managed_value": None}
        assert facts == {original_fact["id"]: original_fact, added["id"]: added}
    trace.update({"accepted": accepted, "job": job, "marker": marker, "after": after})
    path.write_text(json.dumps(trace, ensure_ascii=False))


@pytest.mark.parametrize(
    "failure",
    ["parser-value", "parser-exception", "parser-config", "parser-assertion", "parser-index", "n3"],
)
def test_new_input_boundary_keeps_unclassified_parser_and_n3_unknown(
    owned, monkeypatch, tmp_path, failure
):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    before = read(actor, project)
    database = "\n".join(store._db.iterdump())
    calls = []

    def unexpected(*args, **kwargs):
        calls.append(True)
        error = {
            "parser-value": ValueError,
            "parser-exception": Exception,
            "parser-config": ParserError,
            "parser-assertion": AssertionError,
            "parser-index": IndexError,
            "n3": ValueError,
        }[failure]
        raise error("Unsupported S1 RDF object")

    if failure == "n3":

        class UnknownTerm:
            n3 = staticmethod(unexpected)

        monkeypatch.setattr(domain_changesets, "term", lambda _: UnknownTerm())
    else:
        monkeypatch.setattr(rdf_snapshot.Graph, "parse", unexpected)
    host = actor.mainline
    refused = exchange(actor, "changeset.preview", change(project))
    assert calls and not refused["ok"] and refused["error"]["code"] == "INTERNAL_ERROR"
    assert host.hold and actor.mainline is host
    unknown = dict(host.replies)
    assert len(unknown) == 1 and all(item.unknown for item in unknown.values())
    after_error = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert not after_error["ok"] and after_error["error"]["code"] == "STORAGE_FAILURE"
    assert all(host.replies[key] is item for key, item in unknown.items())
    assert "\n".join(store._db.iterdump()) == database
    (tmp_path / "parser-unknown-trace.json").write_text(
        json.dumps(
            {
                "failure": failure,
                "before": before,
                "refused": refused,
                "afterError": after_error,
                "held": host.hold,
                "unknown": list(unknown),
            }
        )
    )


@pytest.mark.parametrize(
    ("site", "error_type"),
    [("call", error) for error in (Exception, AssertionError, IndexError, TypeError)]
    + [("scheme", ValueError)],
)
def test_urlsplit_noncontract_failures_keep_unknown_and_hold(
    owned, monkeypatch, tmp_path, site, error_type
):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    confirmed_job(actor, project, change(project))
    drain_owned_changesets(actor)
    database = list(store._db.iterdump())
    host = actor.mainline
    called = []
    original_urlsplit = rdf_snapshot.urlsplit

    def unexpected(value):
        if value != "http://[":
            return original_urlsplit(value)
        called.append(value)
        if site == "scheme":

            class BrokenResult:
                @property
                def scheme(self):
                    raise error_type("Invalid IPv6 URL")

            return BrokenResult()
        raise error_type("Invalid IPv6 URL")

    monkeypatch.setattr(rdf_snapshot, "urlsplit", unexpected)
    refused = exchange(actor, "changeset.preview", change(project, "<http://[>", 1))
    assert called == ["http://["]
    assert not refused["ok"] and refused["error"]["code"] == "INTERNAL_ERROR"
    assert actor.mainline is host and host.hold
    unknown = dict(host.replies)
    assert len(unknown) == 1 and all(item.unknown for item in unknown.values())
    after_error = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert not after_error["ok"] and after_error["error"]["code"] == "STORAGE_FAILURE"
    assert all(host.replies[key] is item for key, item in unknown.items())
    assert list(store._db.iterdump()) == database
    (tmp_path / "urlsplit-unknown-trace.json").write_text(
        json.dumps(
            {
                "site": site,
                "errorType": error_type.__name__,
                "called": called,
                "refused": refused,
                "afterError": after_error,
                "held": host.hold,
                "unknown": list(unknown),
            }
        )
    )


@pytest.mark.parametrize("field", ["subject", "predicate"])
@pytest.mark.parametrize("error_type", [ValueError, AssertionError, IndexError])
def test_manual_iri_preflight_does_not_classify_unknown_failures(
    owned, monkeypatch, tmp_path, field, error_type
):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    confirmed_job(actor, project, change(project))
    drain_owned_changesets(actor)
    database = list(store._db.iterdump())
    host = actor.mainline
    original = domain_changesets.iri
    called = []

    def unexpected(value):
        if value == "http://[":
            called.append(value)
            raise error_type("Absolute stable IRI required")
        return original(value)

    monkeypatch.setattr(domain_changesets, "iri", unexpected)
    request = input_change(project, field, "http://[", 1)
    refused = exchange(actor, "changeset.preview", request)
    assert called == ["http://["]
    assert not refused["ok"] and refused["error"]["code"] == "INTERNAL_ERROR"
    assert actor.mainline is host and host.hold
    unknown = dict(host.replies)
    assert len(unknown) == 1 and all(item.unknown for item in unknown.values())
    after_error = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert not after_error["ok"] and after_error["error"]["code"] == "STORAGE_FAILURE"
    assert all(host.replies[key] is item for key, item in unknown.items())
    assert list(store._db.iterdump()) == database
    (tmp_path / "manual-iri-unknown-trace.json").write_text(
        json.dumps(
            {
                "field": field,
                "errorType": error_type.__name__,
                "request": request,
                "called": called,
                "refused": refused,
                "afterError": after_error,
                "held": host.hold,
                "unknown": list(unknown),
            }
        )
    )


def test_reserved_original_identity_is_controlled_ownership_conflict(owned, tmp_path):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    confirmed_job(actor, project, change(project))
    drain_owned_changesets(actor)
    edited = confirmed_job(actor, project, input_change(project, "edit", '"B"', 1))
    drain_owned_changesets(actor)
    assert store.get_job(project, edited["jobId"])["state"] == "succeeded"
    before = read(actor, project)
    host = actor.mainline
    before_dump = list(store._db.iterdump())
    before_details = store._db.execute("SELECT count(*) FROM job_details").fetchone()[0]
    refused = exchange(actor, "changeset.preview", change(project, PLAIN, 2))
    assert not refused["ok"] and refused["error"]["code"] == "OWNERSHIP_CONFLICT", refused
    detail_ref = refused["error"]["params"]["detailRef"]
    detail = store.detail_get(project, detail_ref)
    assert detail["ownershipDetailVersion"] == 1 and detail["kind"] == "manual-ownership-conflict"
    assert detail["projectId"] == project and detail["detailRef"] == detail_ref
    after_dump = list(store._db.iterdump())
    diagnostic_rows = ('INSERT INTO "job_details"', 'INSERT INTO "job_blobs"')
    assert [line for line in before_dump if not line.startswith(diagnostic_rows)] == [
        line for line in after_dump if not line.startswith(diagnostic_rows)
    ]
    assert set(before_dump).issubset(set(after_dump))
    assert store._db.execute("SELECT count(*) FROM job_details").fetchone()[0] == before_details + 1
    assert actor.mainline is host and not host.hold and host.replies == {}
    assert read(actor, project) == before
    accepted = confirmed_job(actor, project, input_change(project, "edit", '"C"', 2))
    drain_owned_changesets(actor)
    marker = exchange(
        actor, "operation.get", {"projectId": project, "operationId": accepted["operationId"]}
    )
    assert marker["ok"] and marker["result"]["jobId"] == accepted["jobId"]
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    after = read(actor, project)
    assert after["domain"]["projectRevision"] == 3
    assert after["domain"]["state"]["facts"][0]["id"] == fact(PLAIN)["id"]
    assert after["domain"]["state"]["facts"][0]["object"] == '"C"'
    (tmp_path / "ownership-trace.json").write_text(
        json.dumps(
            {
                "before": before,
                "refused": refused,
                "detailRef": detail_ref,
                "accepted": accepted,
                "marker": marker,
                "after": after,
            }
        )
    )


@pytest.mark.parametrize("value", ['"x"^^<../relative>', r'"x"^^<urn:\U00110000>'])
def test_vendor_source_errors_have_dedicated_input_type(value):
    from importlib.metadata import version

    assert version("rdflib") == "7.6.0+ontolearn.fr201.2"
    with pytest.raises(rdf_snapshot.TermInputError):
        rdf_snapshot.term(value)


@pytest.mark.parametrize("site", ["join", "int", "group"])
@pytest.mark.parametrize(
    "error_type", [ValueError, Exception, ParserError, AssertionError, IndexError]
)
def test_same_bad_vendor_input_does_not_hide_internal_failures(
    owned, monkeypatch, tmp_path, site, error_type
):
    from rdflib.plugins.parsers import notation3

    actor, store = owned
    project = create(actor)[0]["projectId"]
    value = '"x"^^<../relative>' if site == "join" else r'"x"^^<urn:\U00110000>'
    called = []

    def broken(*args, **kwargs):
        called.append(site)
        raise error_type("private injected source failure")

    if site == "join":
        monkeypatch.setattr(notation3, "join", broken)
    elif site == "int":
        monkeypatch.setattr(notation3, "int", broken, raising=False)
    else:
        original = notation3.unicodeEscape8

        class Match:
            group = staticmethod(broken)

        class Regex:
            def sub(self, callback, text):
                return original.sub(lambda _: callback(Match()), text)

        monkeypatch.setattr(notation3, "unicodeEscape8", Regex())
    database = list(store._db.iterdump())
    host = actor.mainline
    refused = exchange(actor, "changeset.preview", change(project, value))
    assert called and not refused["ok"] and refused["error"]["code"] == "INTERNAL_ERROR", refused
    assert actor.mainline is host and host.hold
    unknown = dict(host.replies)
    assert len(unknown) == 1 and all(item.unknown for item in unknown.values())
    after = exchange(actor, "project.read", {"projectId": project, "editor": "ontology"})
    assert not after["ok"] and after["error"]["code"] == "STORAGE_FAILURE"
    assert list(store._db.iterdump()) == database
    (tmp_path / "vendor-internal-fault-trace.json").write_text(
        json.dumps(
            {
                "site": site,
                "exceptionType": error_type.__name__,
                "called": called,
                "refused": refused,
                "afterError": after,
                "unknown": list(unknown),
                "held": host.hold,
            }
        )
    )


@pytest.mark.parametrize("reason", ["reservedIdentity", "sameStatement", "singleSlot"])
def test_manual_ownership_detail_full_pages_then_original_id_job(owned, tmp_path, reason):
    actor, store = owned
    project = create(actor)[0]["projectId"]
    initial = change(project)
    if reason == "singleSlot":
        initial["plan"]["definitions"] = [
            {
                "layer": "ontology",
                "id": "single-slot",
                "value": {
                    "triples": [],
                    "singleValuedPredicates": [fact(PLAIN)["predicate"]],
                    "references": [],
                },
            }
        ]
    confirmed_job(actor, project, initial)
    drain_owned_changesets(actor)
    base = 1
    if reason != "singleSlot":
        confirmed_job(actor, project, input_change(project, "edit", '"B"', base))
        drain_owned_changesets(actor)
        base += 1
    before = read(actor, project)
    incoming = PLAIN if reason == "reservedIdentity" else '"B"'
    refused = exchange(actor, "changeset.preview", change(project, incoming, base))
    assert not refused["ok"] and refused["error"]["code"] == "OWNERSHIP_CONFLICT", refused
    ref = refused["error"]["params"]["detailRef"]
    header = store.detail_get(project, ref)
    path = tmp_path / "ownership-detail-trace.json"
    path.write_text(json.dumps({"reason": reason, "refused": refused, "header": header}))
    assert header.get("ownershipDetailVersion") == 1, header
    parts, ordinal, expected_hash = [], 0, None
    pages = []
    while True:
        response = exchange(
            actor,
            "project.ownership.detail",
            {
                "projectId": project,
                "detailRef": ref,
                "documentHash": expected_hash,
                "startOrdinal": ordinal,
                "pageSize": 1,
            },
        )
        assert response["ok"], canonical(response)
        page = response["result"]
        pages.append(page)
        expected_hash = page["manifest"]["documentHash"]
        for segment in page["segments"]:
            raw = base64.b64decode(segment["dataBase64"], validate=True)
            assert len(raw) == segment["rawByteLength"]
            import hashlib

            assert hashlib.sha256(raw).hexdigest() == segment["sha256"]
            parts.append(raw)
        if page["complete"]:
            break
        ordinal = page["nextOrdinal"]
    raw = b"".join(parts)
    assert len(raw) == page["manifest"]["totalBytes"]
    assert hashlib.sha256(raw).hexdigest() == expected_hash
    document = json.loads(raw)
    assert document["reason"] == reason
    existing = before["domain"]["state"]["facts"][0]
    assert document["existing"] == {
        "id": existing["id"],
        "owner": existing["owner"],
        "sourceRow": existing["source_row"],
        "slot": {"subject": existing["subject"], "predicate": existing["predicate"]},
    }
    assert document["incoming"]["id"] == fact(incoming)["id"]
    assert read(actor, project) == before and not actor.mainline.hold
    dump = list(store._db.iterdump())
    repeated = exchange(actor, "changeset.preview", change(project, incoming, base))
    assert repeated["error"]["params"]["detailRef"] == ref
    assert list(store._db.iterdump()) == dump
    accepted = confirmed_job(actor, project, input_change(project, "edit", '"C"', base))
    drain_owned_changesets(actor)
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    marker = exchange(
        actor, "operation.get", {"projectId": project, "operationId": accepted["operationId"]}
    )
    assert marker["ok"] and marker["result"]["jobId"] == accepted["jobId"]
    after = read(actor, project)
    assert after["domain"]["projectRevision"] == base + 1
    assert after["domain"]["state"]["facts"][0]["id"] == fact(PLAIN)["id"]
    path.write_text(
        json.dumps(
            {
                "reason": reason,
                "refused": refused,
                "pages": pages,
                "document": document,
                "accepted": accepted,
                "marker": marker,
                "after": after,
            }
        )
    )


@pytest.mark.parametrize("effective", ["same", "removed-first", "overwritten-first"])
def test_single_declaration_preserves_real_home_and_two_existing_locators(
    owned, tmp_path, effective
):
    from test_ontology_metadata_changeset import definition, value

    actor, store = owned
    project = create(actor)[0]["projectId"]
    payload = value()
    request = change(project, '"A"')
    request["plan"]["manual"].append(fact('"B"'))
    request["plan"]["definitions"] = [definition(payload)]
    confirmed_job(actor, project, request)
    drain_owned_changesets(actor)
    before = read(actor, project)
    incoming = deepcopy(payload)
    incoming["singleValuedPredicates"] = [fact(PLAIN)["predicate"]]
    proposed = {
        "projectId": project,
        "baseRevision": 1,
        "intent": "change",
        "plan": {"definitions": [definition(incoming)]},
    }
    expected_id = "Equipment"
    if effective != "same":
        first = {
            "layer": "ontology",
            "id": "A",
            "value": {"triples": [], "singleValuedPredicates": [fact(PLAIN)["predicate"]]},
        }
        last = {**first, "id": "B"}
        proposed["plan"]["definitions"] = [definition(payload), first]
        if effective == "overwritten-first":
            proposed["plan"]["definitions"].append(
                {"layer": "ontology", "id": "A", "value": {"triples": []}}
            )
        proposed["plan"]["definitions"].append(last)
        if effective == "removed-first":
            proposed["plan"]["remove_definitions"] = [{"layer": "ontology", "id": "A"}]
        expected_id = "B"
    database = list(store._db.iterdump())
    refused = exchange(actor, "changeset.preview", proposed)
    if effective == "removed-first":
        # Original Store explicitly rejects changing AND removing the same key
        # before entering declaration validation. Preserve this old UNKNOWN,
        # rather than weakening that guard to make an invalid fixture pass.
        assert not refused["ok"] and refused["error"]["code"] == "INTERNAL_ERROR", refused
        assert actor.mainline.hold and list(store._db.iterdump()) == database
        assert "detailRef" not in refused["error"]["params"]
        (tmp_path / "original-contradictory-plan-trace.json").write_text(
            json.dumps(
                {
                    "originalContradictoryPlan": True,
                    "proposed": proposed,
                    "refused": refused,
                    "held": actor.mainline.hold,
                    "unknown": list(actor.mainline.replies),
                }
            )
        )
        return
    assert not refused["ok"] and refused["error"]["code"] == "OWNERSHIP_CONFLICT", refused
    ref = refused["error"]["params"]["detailRef"]
    header = store.detail_get(project, ref)
    trace = {"before": before, "proposed": proposed, "refused": refused, "header": header}
    path = tmp_path / "declaration-detail-trace.json"
    path.write_text(json.dumps(trace))
    assert header.get("ownershipDetailVersion") == 1, header
    response = exchange(
        actor,
        "project.ownership.detail",
        {
            "projectId": project,
            "detailRef": ref,
            "documentHash": None,
            "startOrdinal": 0,
            "pageSize": 64,
        },
    )
    assert response["ok"] and response["result"]["complete"], response
    document = json.loads(
        b"".join(base64.b64decode(s["dataBase64"]) for s in response["result"]["segments"])
    )
    assert document["kind"] == "single-declaration-conflict"
    assert document["reason"] == "singleDeclaration" and "incoming" not in document
    assert document["declaration"] == {
        "layer": "ontology",
        "id": expected_id,
        "predicate": fact(PLAIN)["predicate"],
    }
    assert {row["id"] for row in document["existing"]} == {fact('"A"')["id"], fact('"B"')["id"]}
    assert read(actor, project) == before and not actor.mainline.hold
    # A real follow-up removes one conflicting value, then the same declaration
    # can be confirmed and committed without changing its complete M/triples.
    confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 1,
            "intent": "change",
            "plan": {"remove": [fact('"B"')["id"]]},
        },
    )
    drain_owned_changesets(actor)
    proposed["baseRevision"] = 2
    accepted = confirmed_job(actor, project, proposed)
    drain_owned_changesets(actor)
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    marker = exchange(
        actor, "operation.get", {"projectId": project, "operationId": accepted["operationId"]}
    )
    assert marker["ok"] and marker["result"]["jobId"] == accepted["jobId"]
    after = read(actor, project)
    assert after["domain"]["projectRevision"] == 3
    persisted = json.loads(
        next(
            d["payload"] for d in after["domain"]["state"]["definitions"] if d["id"] == "Equipment"
        )
    )
    assert persisted == (incoming if effective == "same" else payload)
    trace.update({"document": document, "accepted": accepted, "marker": marker, "after": after})
    path.write_text(json.dumps(trace))
