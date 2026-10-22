"""Real committed asserted queries through production Session and its owned worker."""

import json
import os
import sys
from copy import deepcopy
from uuid import uuid4

import pytest
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT, semantic_identity
from ontolearn_engine.storage import digest
from test_resident_runtime import Session

QUERY = 'SELECT ?alarm WHERE { ?alarm <urn:level> "High" ; <urn:status> "Open" . }'


def uid():
    return str(uuid4())


def fact(subject, predicate, value):
    return {
        "id": digest([subject, predicate, value]),
        "subject": subject,
        "predicate": predicate,
        "object": value,
    }


def prepare_database(tmp_path, text=QUERY, *, closed=False, target_format=2):
    database = tmp_path / "query.sqlite"
    store = JobStore(database, contract=CONTRACT, target_format=target_format)
    store.create_project("query-project")
    store.create_project("other-project")
    project = store.public_project("query-project")
    other = store.public_project("other-project")
    facts = []
    for alarm, level, status in [
        ("A01", "High", "Closed" if closed else "Open"),
        ("A02", "High", "Closed"),
        ("A03", "Low", "Open"),
    ]:
        facts.extend(
            [
                fact("urn:" + alarm, "urn:level", '"' + level + '"'),
                fact("urn:" + alarm, "urn:status", '"' + status + '"'),
            ]
        )
    facts.extend(
        [
            fact("urn:terms", "urn:iri", "<urn:object>"),
            fact("urn:terms", "urn:lang", '"泵站"@zh'),
            fact("urn:terms", "urn:typed", '"7"^^<http://www.w3.org/2001/XMLSchema#integer>'),
        ]
    )
    store.commit(
        "query-project",
        0,
        uid(),
        uid(),
        manual=facts,
        definitions=[{"layer": "query", "id": "Q1", "value": {"text": text}}],
    )
    params = query_parameters(store, project)
    store.close()
    return database, project, other, params


def query_parameters(store, project, *, snapshot=None, selection="current", definition="Q1"):
    return {
        "projectId": project,
        "operationId": uid(),
        "capability": "query.execute",
        "input": {
            "inputSnapshotId": snapshot or store.project_get(project)["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": definition,
            "parametersHash": store.put_blob(project, {"inputSelection": selection}),
            "derivedResultIds": [],
            "preparedPlanRef": None,
        },
        "confirmationRef": None,
    }


def run_query(database, project, params):
    session = Session(database, [project], test_mode=False)
    try:
        accepted = session.call("job.create", params)
        assert accepted["capability"] == "query.execute", accepted
        terminal = session.terminal(project, accepted["jobId"], timeout=15)
        assert terminal["state"] == "succeeded", terminal
        assert session.call("job.create", params) == terminal
        assert (
            session.call("job.cancel", {"projectId": project, "jobId": terminal["jobId"]})[
                "disposition"
            ]
            == "alreadyTerminal"
        )
        assert session.call("health", {})["status"] == "ok"
        return terminal
    finally:
        session.close()


def read_complete(database, project, terminal):
    store = JobStore(database, contract=CONTRACT)
    try:
        identity = terminal["resultRef"]["resultId"]
        metadata, payload = store.semantic_result(project, identity)
        rows = store.result(identity)["payload"]
        return metadata, payload, rows
    finally:
        store.close()


@pytest.mark.parametrize(
    "text,closed,expected",
    [
        (QUERY, False, {"type": "SELECT", "variables": ["alarm"], "rows": [["<urn:A01>"]]}),
        (QUERY, True, {"type": "SELECT", "variables": ["alarm"], "rows": []}),
        ('ASK { <urn:A01> <urn:status> "Open" }', False, {"type": "ASK", "value": True}),
        ('ASK { <urn:A01> <urn:status> "Missing" }', False, {"type": "ASK", "value": False}),
        (
            "SELECT ?iri ?lang ?typed ?missing WHERE { <urn:terms> <urn:iri> ?iri ; "
            "<urn:lang> ?lang ; <urn:typed> ?typed . "
            "OPTIONAL { <urn:terms> <urn:missing> ?missing } }",
            False,
            {
                "type": "SELECT",
                "variables": ["iri", "lang", "typed", "missing"],
                "rows": [
                    [
                        "<urn:object>",
                        '"泵站"@zh',
                        '"7"^^<http://www.w3.org/2001/XMLSchema#integer>',
                        None,
                    ]
                ],
            },
        ),
    ],
)
def test_real_session_full_query_and_reopened_payload(tmp_path, text, closed, expected):
    database, project, _, params = prepare_database(tmp_path, text, closed=closed)
    terminal = run_query(database, project, params)
    metadata, payload, rows = read_complete(database, project, terminal)
    assert terminal["implementation"] == semantic_identity()
    assert terminal["implementation"]["executionSemanticsVersion"] == "i05-finite-6"
    assert len(metadata) == 17 and CONTRACT.validate("result", metadata)
    assert payload["query"] == expected
    assert payload["queryText"] == text
    assert payload["scope"] == "asserted"
    assert payload["inputSelection"] == "current"
    assert payload["inputSnapshotId"] == params["input"]["inputSnapshotId"]
    assert payload["selectedResultIds"] == []
    assert payload["provenance"]["scope"] == "asserted"
    assert rows[0]["cells"] == ["columns", "path", "value", "part", "parts"]
    store = JobStore(database, contract=CONTRACT)
    try:
        assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
        assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 1
        binding = {
            k: metadata[k]
            for k in ("projectId", "resultId", "inputSnapshotId", "scope", "parametersHash")
        }
        binding["order"] = "ordinal+rowId:asc"
        first = store.result_page(binding, 1, None)
        assert CONTRACT.validate("page", first)
    finally:
        store.close()


def test_original_operation_retry_keeps_original_snapshot_after_current_moves(tmp_path):
    database, project, _, params = prepare_database(tmp_path)
    original = run_query(database, project, params)
    store = JobStore(database, contract=CONTRACT)
    try:
        state = store.state("query-project")
        record = next(
            f
            for f in state["facts"]
            if f["subject"] == "urn:A01" and f["predicate"] == "urn:status"
        )
        store.commit("query-project", 1, uid(), uid(), edits={record["id"]: '"Closed"'})
        historical = query_parameters(
            store, project, snapshot=params["input"]["inputSnapshotId"], selection="historical"
        )
        stale_current = {**deepcopy(params), "operationId": uid()}
        new_current = query_parameters(store, project)
    finally:
        store.close()
    session = Session(database, [project], test_mode=False)
    try:
        assert session.call("job.create", params) == original
        assert session.call("job.create", stale_current)["code"] == "IDENTITY_CONFLICT"
        history_job = session.call("job.create", historical)
        history_job = session.terminal(project, history_job["jobId"], timeout=15)
        assert history_job["state"] == "succeeded"
        current_job = session.call("job.create", new_current)
        current_job = session.terminal(project, current_job["jobId"], timeout=15)
        assert current_job["state"] == "succeeded"
    finally:
        session.close()
    _, previous, _ = read_complete(database, project, history_job)
    _, current, _ = read_complete(database, project, current_job)
    assert previous["query"]["rows"] == [["<urn:A01>"]]
    assert previous["inputSelection"] == "historical"
    assert current["query"]["rows"] == []
    assert previous["inputSnapshotId"] != current["inputSnapshotId"]
    store = JobStore(database, contract=CONTRACT)
    try:
        assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 3
        assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 3
    finally:
        store.close()


def test_public_admission_is_committed_asserted_explicit_and_project_authorized(tmp_path):
    database, project, other, good = prepare_database(tmp_path)
    store = JobStore(database, contract=CONTRACT)
    invalid = []
    try:
        for parameters in (
            {},
            {"inputSelection": "unknown"},
            {"inputSelection": "current", "graph": []},
        ):
            p = deepcopy(good)
            p["operationId"] = uid()
            p["input"]["parametersHash"] = store.put_blob(project, parameters)
            invalid.append(p)
        for field, value in [
            ("definitionId", "uncommitted-draft"),
            ("definitionId", "missing"),
            ("scope", "asserted+derived"),
            ("derivedResultIds", [uid()]),
            ("preparedPlanRef", "a" * 64),
        ]:
            p = deepcopy(good)
            p["operationId"] = uid()
            p["input"][field] = value
            invalid.append(p)
    finally:
        store.close()
    session = Session(database, [project], test_mode=False)
    try:
        for p in invalid:
            answer = session.call("job.create", p)
            assert "jobId" not in answer and CONTRACT.validate("error", answer), answer
        assert (
            session.call("job.create", {**good, "projectId": other})["code"] == "PERMISSION_DENIED"
        )
        assert (
            session.call("job.create", {**good, "capability": "reasoning.execute"})["code"]
            == "UNSUPPORTED_CAPABILITY"
        )
    finally:
        session.close()
    store = JobStore(database, contract=CONTRACT)
    try:
        assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
        assert store._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 0
        assert CONTRACT.REGISTRY["capabilities"]["query.execute"]["runtimeDataScopes"] == [
            "asserted"
        ]
        assert "query.execute" not in CONTRACT.REGISTRY["v2Runtime"]
        assert "semantic.start" not in CONTRACT.REGISTRY["v2Runtime"]
    finally:
        store.close()


def test_explicit_business3_real_query_and_reopened_complete_payload(tmp_path, monkeypatch):
    from test_project_changeset_stdio import Session as Business3Session

    monkeypatch.delenv("ONTOLEARN_TEST_ENGINE", raising=False)
    assert "ONTOLEARN_TEST_ENGINE" not in os.environ
    database, project, _, params = prepare_database(tmp_path, target_format=3)
    session = Business3Session(database, project, version=3)
    command = [sys.executable, "-I", "-m", "ontolearn_engine", "--t01-internal-profile=business3"]
    try:
        assert session.process.args == command
        assert session.hello["selectedVersion"] == 3
        assert session.call("project.get", {"projectId": project})["formatVersion"] == 3
        accepted = session.call("job.create", params)
        assert accepted["capability"] == "query.execute"
        terminal = session.terminal(accepted)
        assert terminal["state"] == "succeeded", terminal
        assert terminal["implementation"] == semantic_identity()
        assert session.call("job.create", params) == terminal
    finally:
        session.close()
    assert session.process.returncode == 0
    (tmp_path / "business3-query-stdio-receipt.json").write_text(
        json.dumps(
            {
                "argv": session.process.args,
                "pid": session.process.pid,
                "pythonExecutable": sys.executable,
                "pythonPrefix": sys.prefix,
                "engineOverridePresent": "ONTOLEARN_TEST_ENGINE" in os.environ,
                "protocolVersion": 3,
                "testMode": False,
                "actualExit": session.process.returncode,
                "stdinHex": b"".join(session.sent).hex(),
                "stdoutHex": b"".join(session.output).hex(),
                "stderr": "Existing Session.close asserted original stderr bytes empty.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    reopened = JobStore(database, contract=CONTRACT, target_format=3)
    try:
        assert reopened.actual_format == 3
        assert reopened.get_job(project, terminal["jobId"]) == terminal
        metadata, payload = reopened.semantic_result(project, terminal["resultRef"]["resultId"])
        assert len(metadata) == 17 and CONTRACT.validate("result", metadata)
        assert payload["query"] == {
            "type": "SELECT",
            "variables": ["alarm"],
            "rows": [["<urn:A01>"]],
        }
        assert payload["queryText"] == QUERY
        assert payload["inputSnapshotId"] == params["input"]["inputSnapshotId"]
        assert payload["inputSelection"] == "current" and payload["scope"] == "asserted"
        assert (
            reopened._db.execute("SELECT source_format FROM query_payload_format").fetchone()[0]
            == 3
        )
        assert reopened._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
        assert reopened._db.execute("SELECT count(*) FROM query_payloads").fetchone()[0] == 1
    finally:
        reopened.close()
