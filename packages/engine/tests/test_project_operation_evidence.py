"""Real JobStore3 facts and independent ledgers; no dispatch/permission proof.

FaultConnection is a controlled driver fault seam on a real SQLite connection.
Its injected errors are not evidence of an OS disk fault. Fixtures use original
writers and validators; the oracle only serializes full actual SQL rows.
"""

import json
import sqlite3
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace

import pytest
import test_project_changeset_service as changesets
from ontolearn_engine import storage
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import operation_evidence as core
from ontolearn_engine.project.project_host import ReadLimits
from test_job_store import CONTRACT, IMPL, create, uid
from test_project_host_read_services import corrupt_immutable

CAPS = {
    "maxEvidenceBytes": 67108864,
    "maxSelectorBytes": 262144,
    "maxReturnBytes": 131072,
    "readerLimits": ReadLimits(),
}


def encoded(value):
    """Independent canonical oracle, never the subject's cost/measure helper."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def origin():
    return {"hostClientId": uid(), "engineSessionId": uid()}


def create_intent(name='项目汉😀"\\\n'):
    return {
        "projectCreateCoreVersion": 1,
        "request": {
            "requestVersion": 1,
            "operationId": uid(),
            "initialization": {"kind": "blank"},
            "name": name,
        },
        "origin": {**origin(), "permission": "library.create"},
        "readerLimits": ReadLimits(),
    }


def create_project(owner):
    intent = create_intent()
    result = owner.commit(None, None, intent["request"]["operationId"], None, creation=intent)
    return intent, result


def create_selector(intent):
    return {
        "resolutionVersion": 1,
        "kind": "project.create",
        "operationId": intent["request"]["operationId"],
        "expectedRequest": deepcopy(intent["request"]),
        "originalOrigin": {k: intent["origin"][k] for k in ("hostClientId", "engineSessionId")},
    }


def job_selector(job):
    return {
        "resolutionVersion": 1,
        "kind": "job",
        "operationId": job["operationId"],
        "projectId": job["projectId"],
        "jobId": job["jobId"],
        "expectedRequest": {
            "projectId": job["projectId"],
            "operationId": job["operationId"],
            "capability": job["capability"],
            "input": deepcopy(job["input"]),
            "confirmationRef": job["confirmationRef"],
        },
        "issuedImplementation": deepcopy(job["implementation"]),
        "issuedLimits": deepcopy(job["limits"]),
        "originalOrigin": origin(),
    }


def read(owner, selector, **limits):
    return core.read_operation_evidence(owner, selector, **(CAPS | limits))


def expect_fault(reason, call):
    with pytest.raises(core.EvidenceFault) as raised:
        call()
    assert raised.value.reason == str(raised.value) == reason
    return raised.value


@pytest.fixture
def audit(monkeypatch, tmp_path):
    ledgers = []
    by_gate = {}

    def collect(gate, event, **facts):
        key = id(gate)
        if key not in by_gate:
            # Retain actual gate to prevent id reuse during this test.
            by_gate[key] = (gate, [])
            ledgers.append(by_gate[key][1])
        by_gate[key][1].append({"event": event, **facts})

    monkeypatch.setattr(core._MeteredGate, "_audit", collect)
    yield ledgers
    path = tmp_path / "operation-evidence-audit.json"
    path.write_text(json.dumps(ledgers, ensure_ascii=False, indent=2) + "\n")
    print(f"audit-ledger={path}")


@pytest.fixture
def owner(tmp_path):
    store = JobStore(tmp_path / "facts.sqlite", contract=CONTRACT, target_format=3)
    yield store
    store.close()


WRITE_ACTIONS = {
    getattr(sqlite3, name)
    for name in (
        "SQLITE_INSERT",
        "SQLITE_UPDATE",
        "SQLITE_DELETE",
        "SQLITE_CREATE_INDEX",
        "SQLITE_CREATE_TABLE",
        "SQLITE_CREATE_TEMP_INDEX",
        "SQLITE_CREATE_TEMP_TABLE",
        "SQLITE_CREATE_TEMP_TRIGGER",
        "SQLITE_CREATE_TEMP_VIEW",
        "SQLITE_CREATE_TRIGGER",
        "SQLITE_CREATE_VIEW",
        "SQLITE_DROP_INDEX",
        "SQLITE_DROP_TABLE",
        "SQLITE_DROP_TEMP_INDEX",
        "SQLITE_DROP_TEMP_TABLE",
        "SQLITE_DROP_TEMP_TRIGGER",
        "SQLITE_DROP_TEMP_VIEW",
        "SQLITE_DROP_TRIGGER",
        "SQLITE_DROP_VIEW",
        "SQLITE_ALTER_TABLE",
        "SQLITE_REINDEX",
        "SQLITE_ANALYZE",
        "SQLITE_ATTACH",
        "SQLITE_DETACH",
    )
}


@contextmanager
def readonly(owner):
    db = owner._db
    before = "\n".join(db.iterdump())
    rejected, trace = [], []

    def authorizer(action, first, second, _database, _trigger):
        readonly_pragma = first in {
            "encoding",
            "table_info",
            "user_version",
            "integrity_check",
            "foreign_key_check",
        } and (first == "table_info" or second is None)
        if action in WRITE_ACTIONS or action == sqlite3.SQLITE_PRAGMA and not readonly_pragma:
            rejected.append((action, first, second))
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    db.set_authorizer(authorizer)
    db.set_trace_callback(trace.append)
    try:
        yield trace
    finally:
        db.set_trace_callback(None)
        db.set_authorizer(None)
        assert rejected == []
        assert "\n".join(db.iterdump()) == before
        assert not db.in_transaction


def verify_charges(owner, ledger):
    """Price all actual charged full rows, including SQLite schema rows."""
    charged = [x for x in ledger if x["event"] == "charged"]
    keys = [(x["table"], x["rowid"]) for x in charged]
    assert len(keys) == len(set(keys))
    total = 0
    encoding = owner._db.execute("PRAGMA encoding").fetchone()[0].upper()
    for charge in charged:
        table = charge["table"].replace('"', '""')
        row = owner._db.execute(
            f'SELECT * FROM "{table}" WHERE rowid=?', (charge["rowid"],)
        ).fetchone()
        assert row is not None
        actual = len(encoded(dict(row)))
        assert charge["bytes"] == actual, (charge, dict(row), actual)
        total += actual
        assert charge["total"] == total
        probe_index = next(
            i
            for i, item in enumerate(ledger)
            if item["event"] == "probe-reserved"
            and (item["table"], item["rowid"]) == (charge["table"], charge["rowid"])
        )
        assert probe_index < ledger.index(charge)
        probe_work = 128
        for value in dict(row).values():
            if isinstance(value, str):
                probe_work += 256 + (
                    160 * (len(value.encode("utf-8")) + 1)
                    if encoding == "UTF-8"
                    else 16 * (len(value) + 1) ** 2
                )
            else:
                assert value is None or type(value) is int
                probe_work += 64
        assert ledger[probe_index]["work"] == probe_work
    return total


def verify_ledger(owner, ledger):
    total = verify_charges(owner, ledger)
    summary = ledger[-1]
    assert ledger[0]["event"] == "begin" and summary["event"] == "rollback"
    assert summary["evidence"] == total > 0
    assert summary["probe"] == sum(x["work"] for x in ledger if x["event"] == "probe-reserved")
    queries = [x for x in ledger if x["event"] == "query"]
    assert [x["query"] for x in queries] == list(range(1, len(queries) + 1))
    assert summary["queries"] == len(queries) + 2
    work = 0
    for query in queries:
        expected = 128 + (
            query["bodyCost"]
            if query["bodyCost"] is not None
            else 128 * query["numericColumns"] * query["rows"]
        )
        assert query["reservedWork"] == expected
        work += expected
        assert query["readWork"] == work
    assert summary["readWork"] == work
    return summary


@pytest.mark.parametrize("encoding", ["UTF-8", "UTF-16le", "UTF-16be"])
@pytest.mark.parametrize("variant", ["ordinary", "rounds-null", "rounds-empty"])
def test_real_encoded_ordinary_accepted_job(tmp_path, monkeypatch, audit, encoding, variant):
    original_connect = sqlite3.connect
    connections = []

    def connect(*args, **kwargs):
        db = original_connect(*args, **kwargs)
        db.execute(f"PRAGMA encoding='{encoding}'")
        connections.append(db)
        return db

    # Set encoding before the original writer's first real DDL, without adding
    # a bootstrap table or replacing the owner's actual connection.
    monkeypatch.setattr(storage.sqlite3, "connect", connect)
    owner = JobStore(tmp_path / "encoded.sqlite", contract=CONTRACT, target_format=3)
    try:
        _, project = create_project(owner)
        capability = "test.read" if variant == "ordinary" else "test.rounds"
        parameters = {"workMs": 1} if variant == "ordinary" else {"maxRounds": 2}
        job = create(owner, capability, project=project["projectId"], parameters=parameters)
        if variant == "rounds-empty":
            owner.start_job(job["jobId"])
            owner.start_job_run(job["jobId"], owner.job_context(job["jobId"])["runConfig"])
        expected = owner.get_job(job["projectId"], job["jobId"])
        selected = job_selector(job)
        assert owner._db.execute("PRAGMA encoding").fetchone()[0].upper() == encoding.upper()
        count = len(connections)
        with readonly(owner) as trace:
            result = read(owner, selected)
        assert len(connections) == count
        assert result == {
            "evidenceVersion": 1,
            "kind": "job",
            "operationId": job["operationId"],
            "finding": "job-record",
            "job": expected,
            "originEvidence": "not-recorded",
        }
        assert trace[0] == "BEGIN" and trace[-1] == "ROLLBACK"
        assert trace.count("BEGIN") == trace.count("ROLLBACK") == 1
        verify_ledger(owner, audit[-1])
    finally:
        owner.close()


@pytest.mark.parametrize(
    "opened_run,state",
    [(False, state) for state in ["queued", "running", "cancelling", "failed", "cancelled"]]
    + [(True, state) for state in ["running", "cancelling", "failed", "cancelled"]],
)
def test_rounds_run_null_and_real_zero_rounds(owner, audit, state, opened_run):
    _, project = create_project(owner)
    job = create(owner, "test.rounds", project=project["projectId"], parameters={"maxRounds": 2})
    identity = job["jobId"]
    if state != "queued":
        owner.start_job(identity)
    if opened_run:
        owner.start_job_run(identity, owner.job_context(identity)["runConfig"])
    if state in {"cancelling", "cancelled"}:
        owner.cancel_job(job["projectId"], identity)
    if state == "cancelled":
        owner.cancelled_job(identity)
    if state == "failed":
        owner.fail_job(
            identity,
            {
                "code": "INTERNAL_ERROR",
                "messageKey": "engine.internal",
                "params": {},
                "retryable": False,
            },
        )
    expected = owner.get_job(job["projectId"], identity)
    assert expected["state"] == state
    assert expected["commitProgress"]["committedProgress"] is None
    assert (
        owner._db.execute("SELECT count(*) FROM rounds WHERE job=?", (identity,)).fetchone()[0] == 0
    )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == "job-record" and result["job"] == expected
    assert result["originEvidence"] == "not-recorded"
    verify_ledger(owner, audit[-1])


def test_real_create_survives_later_history(owner, audit):
    intent, created = create_project(owner)
    project = created["projectId"]
    owner.apply_application(
        project,
        uid(),
        {"type": "metadata", "expectedVersion": 1, "patch": {"name": "later"}},
        actor=uid(),
        permission="write",
    )
    owner.commit(
        project,
        0,
        uid(),
        "domain-job",
        definitions=[{"layer": "rule", "id": "r", "value": {"enabled": True}}],
    )
    with readonly(owner):
        result = read(owner, create_selector(intent))
    assert result == {
        "evidenceVersion": 1,
        "kind": "project.create",
        "operationId": intent["request"]["operationId"],
        "finding": "create-record",
        "createResult": created,
    }
    verify_ledger(owner, audit[-1])


def test_unknown_claim_is_no_evidence_and_outer_transaction_is_untouched(owner, audit):
    intent = create_intent()
    selected = create_selector(intent)
    with readonly(owner):
        assert read(owner, selected) == {
            "evidenceVersion": 1,
            "kind": "project.create",
            "operationId": selected["operationId"],
            "finding": "no-evidence",
        }
    verify_ledger(owner, audit[-1])
    owner._db.execute("BEGIN")
    trace = []
    owner._db.set_trace_callback(trace.append)
    try:
        expect_fault("state", lambda: read(owner, selected))
        assert owner._db.in_transaction and trace == []
    finally:
        owner._db.set_trace_callback(None)
        owner._db.execute("ROLLBACK")


@pytest.mark.parametrize(
    "field", ["jobId", "definitionId", "implementation", "limits", "projectId"]
)
def test_original_identity_mismatch_is_not_other_operation_content(owner, audit, field):
    _, project = create_project(owner)
    job = create(owner, project=project["projectId"])
    selected = job_selector(job)
    if field == "jobId":
        selected["jobId"] = uid()
    elif field == "definitionId":
        selected["expectedRequest"]["input"]["definitionId"] = "other"
    elif field == "implementation":
        selected["issuedImplementation"]["executionSemanticsVersion"] = "other-v1"
    elif field == "limits":
        selected["issuedLimits"]["requestMs"] += 1
    else:
        _, other = create_project(owner)
        selected["projectId"] = selected["expectedRequest"]["projectId"] = other["projectId"]
    with readonly(owner):
        expect_fault("identity-conflict", lambda: read(owner, selected))
    verify_ledger(owner, audit[-1])


@pytest.mark.parametrize("dimension", ["evidence", "selector", "return", "probe", "query", "read"])
def test_independent_exact_budget_boundaries(owner, audit, monkeypatch, dimension):
    _, project = create_project(owner)
    job = create(owner, project=project["projectId"])
    selected = job_selector(job)
    result = read(owner, selected)
    summary = verify_ledger(owner, audit[-1])
    parameter = {
        "evidence": "maxEvidenceBytes",
        "selector": "maxSelectorBytes",
        "return": "maxReturnBytes",
    }
    constant = {"probe": "MAX_PROBE_WORK", "query": "MAX_QUERY_COUNT", "read": "MAX_READ_WORK"}
    exact = {
        "evidence": summary["evidence"],
        "selector": len(encoded(selected)),
        "return": len(encoded(result)),
        "probe": summary["probe"],
        "query": summary["queries"],
        "read": summary["readWork"],
    }[dimension]
    for delta in (-1, 0, 1):
        kwargs = {}
        if dimension in parameter:
            kwargs[parameter[dimension]] = exact + delta
        else:
            monkeypatch.setattr(core, constant[dimension], exact + delta)
        with readonly(owner):
            if delta < 0:
                expect_fault(
                    "resource-limit", lambda current=kwargs: read(owner, selected, **current)
                )
            else:
                assert read(owner, selected, **kwargs) == result
        if dimension != "selector" or delta >= 0:
            assert audit[-1][-1]["event"] == "rollback"


@pytest.mark.parametrize("argument", ["maxEvidenceBytes", "maxSelectorBytes", "maxReturnBytes"])
@pytest.mark.parametrize("value", [True, False, 0, -1, float("inf"), 9007199254740992])
def test_invalid_explicit_limits_before_any_database_query(owner, audit, argument, value):
    trace = []
    owner._db.set_trace_callback(trace.append)
    try:
        expect_fault(
            "invalid-input",
            lambda: read(owner, create_selector(create_intent()), **{argument: value}),
        )
        assert trace == [] and audit == []
    finally:
        owner._db.set_trace_callback(None)


class FaultCursor:
    def __init__(self, cursor, connection):
        self.cursor, self.connection = cursor, connection

    def _fetch(self, method, *args):
        if self.connection.stage == method:
            raise self.connection.error
        return getattr(self.cursor, method)(*args)

    def fetchone(self):
        return self._fetch("fetchone")

    def fetchall(self):
        return self._fetch("fetchall")

    def fetchmany(self, size=1):
        return self._fetch("fetchmany", size)

    def __iter__(self):
        return iter(self.cursor)


class FaultConnection(sqlite3.Connection):
    stage = None
    target = None
    error = None

    def execute(self, sql, parameters=()):
        if sql == self.target and self.stage == "execute":
            raise self.error
        cursor = super().execute(sql, parameters)
        return FaultCursor(cursor, self) if sql == self.target and self.stage else cursor


@pytest.mark.parametrize("stage", ["execute", "fetchone", "fetchall", "fetchmany", "iterator"])
@pytest.mark.parametrize(
    "code,reason",
    [
        (sqlite3.SQLITE_BUSY, "storage-busy"),
        (sqlite3.SQLITE_LOCKED, "storage-busy"),
        (sqlite3.SQLITE_IOERR, "storage-failure"),
    ],
)
def test_controlled_real_driver_faults_cross_old_validator_boundary(
    tmp_path, monkeypatch, audit, stage, code, reason
):
    original_connect = sqlite3.connect

    def connect(*args, **kwargs):
        return original_connect(*args, **kwargs, factory=FaultConnection)

    monkeypatch.setattr(storage.sqlite3, "connect", connect)
    owner = JobStore(tmp_path / "fault.sqlite", contract=CONTRACT, target_format=3)
    try:
        intent, _ = create_project(owner)
        selected = create_selector(intent)
        db = owner._db
        db.target = (
            "SELECT * FROM app_format"
            if stage == "fetchall"
            else "SELECT sql FROM sqlite_master WHERE name=?"
        )
        db.error = sqlite3.OperationalError("secret SQL/path must not escape")
        db.error.sqlite_errorcode = code
        db.stage = "fetchone" if stage == "iterator" else stage
        if stage in {"iterator", "fetchmany"}:

            def faulting_catalog(view):
                cursor = view._db.execute(db.target, ("projects",))
                if stage == "iterator":
                    list(cursor)
                else:
                    cursor.fetchmany(1)

            monkeypatch.setattr(core, "_catalog", faulting_catalog)
        with readonly(owner):
            failure = expect_fault(reason, lambda: read(owner, selected))
        assert "secret" not in str(failure)
        assert audit[-1][-1]["event"] == "rollback"
    finally:
        owner.close()


def test_frozen_reader_limits_can_only_tighten(owner, audit):
    intent, _ = create_project(owner)
    with readonly(owner):
        expect_fault(
            "resource-limit",
            lambda: read(
                owner,
                create_selector(intent),
                readerLimits=replace(ReadLimits(), validation_rows=1),
            ),
        )


def finished(owner, capability, project_id=None):
    if project_id is None:
        _, project = create_project(owner)
        project_id = project["projectId"]
    job = create(
        owner,
        capability,
        project=project_id,
        parameters={"maxRounds": 1} if capability == "test.rounds" else None,
    )
    identity = job["jobId"]
    owner.start_job(identity)
    if capability == "test.read":
        owner.finish_read_job(
            identity,
            [
                {"rowId": uid(), "ordinal": 0, "cells": ["汉😀", 1]},
                {"rowId": uid(), "ordinal": 1, "cells": ["other", 2]},
            ],
        )
    elif capability == "test.atomic":
        owner.commit_job(identity)
    else:
        owner.start_job_run(identity, owner.job_context(identity)["runConfig"])
        owner.commit_job_round(
            identity, {"pendingEvents": [], "consumedEvents": [], "inputEvents": []}
        )
        owner.finish_job_run(identity, pending_events=[], event_consumption=[])
    return job, owner.get_job(job["projectId"], identity)


@pytest.mark.parametrize("capability", ["test.read", "test.atomic", "test.rounds"])
def test_real_success_and_evicted_payload_keep_original_facts(owner, audit, capability):
    job, expected = finished(owner, capability)
    selected = job_selector(job)
    with readonly(owner):
        result = read(owner, selected)
    assert result["finding"] == "job-record" and result["job"] == expected
    verify_ledger(owner, audit[-1])
    result_id = expected["resultRef"]["resultId"]
    # The real cache writer, rather than a fake successful DTO.
    if capability != "test.atomic":
        finished(owner, capability, job["projectId"])
    assert result_id in owner.collect_cache()
    assert (
        owner._db.execute("SELECT payload FROM results WHERE id=?", (result_id,)).fetchone()[0]
        is None
    )
    with readonly(owner):
        assert read(owner, selected) == result
    verify_ledger(owner, audit[-1])
    assert (
        owner._db.execute("SELECT payload FROM results WHERE id=?", (result_id,)).fetchone()[0]
        is None
    )


@pytest.mark.parametrize(
    "damage", ["receipt-bool", "summary-bool", "audit-bool", "duplicate-ordinal", "duplicate-rowid"]
)
def test_actual_result_payload_corruption_is_incomplete(owner, audit, damage):
    capability = (
        "test.atomic"
        if damage == "receipt-bool"
        else "test.read"
        if damage.startswith("duplicate")
        else "test.rounds"
    )
    job, success = finished(owner, capability)
    result_id = success["resultRef"]["resultId"]
    payload = json.loads(
        owner._db.execute("SELECT payload FROM results WHERE id=?", (result_id,)).fetchone()[0]
    )
    if damage == "receipt-bool":
        assert payload[0]["cells"][2] == 1
        payload[0]["cells"][2] = True
    elif damage == "summary-bool":
        assert payload[0]["cells"][2] == 1
        payload[0]["cells"][2] = True
    elif damage == "audit-bool":
        cells = payload[1]["cells"]
        position = next(i for i, value in enumerate(cells) if type(value) is int and value == 1)
        cells[position] = True
    elif damage == "duplicate-ordinal":
        payload[1]["ordinal"] = payload[0]["ordinal"]
    else:
        payload[1]["rowId"] = payload[0]["rowId"]
    with corrupt_immutable(owner, "results"):
        owner._db.execute(
            "UPDATE results SET payload=? WHERE id=?", (encoded(payload).decode(), result_id)
        )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == "incomplete-evidence"
    assert set(result) == {"evidenceVersion", "kind", "operationId", "finding"}
    verify_ledger(owner, audit[-1])


@pytest.mark.parametrize(
    "field",
    [
        "project",
        "snapshot",
        "kind",
        "dependencies",
        "implementation",
        "cache_key",
        "manifests",
        "projection",
        "job",
    ],
)
def test_actual_result_metadata_cross_check_all_original_material(owner, audit, field):
    job, success = finished(owner, "test.read")
    other_job, other_success = finished(owner, "test.read")
    result_id = success["resultRef"]["resultId"]
    table = "job_results" if field in {"manifests", "projection", "job"} else "results"
    if field == "project":
        value = owner._project(other_job["projectId"])
    elif field == "snapshot":
        value = other_job["inputSnapshotId"]
    elif field == "kind":
        value = "query"
    elif field == "dependencies":
        value = encoded({"wrong": 1}).decode()
    elif field == "implementation":
        value = encoded({**IMPL, "executionSemanticsVersion": "changed-v1"}).decode()
    elif field == "cache_key":
        value = "0" * 64
    elif field == "job":
        value = other_success["jobId"]
    else:
        value = encoded({"wrong": 1}).decode()
    with corrupt_immutable(owner, table):
        owner._db.execute(f'UPDATE "{table}" SET "{field}"=? WHERE id=?', (value, result_id))
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == "incomplete-evidence"
    verify_ledger(owner, audit[-1])


def test_missing_actual_blob_is_incomplete_not_no_evidence(owner, audit):
    _, project = create_project(owner)
    job = create(owner, project=project["projectId"])
    with corrupt_immutable(owner, "job_blobs"):
        owner._db.execute(
            "DELETE FROM job_blobs WHERE project=? AND ref=?",
            (job["projectId"], job["parametersHash"]),
        )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result == {
        "evidenceVersion": 1,
        "kind": "job",
        "operationId": job["operationId"],
        "finding": "incomplete-evidence",
    }
    verify_ledger(owner, audit[-1])


@pytest.mark.parametrize(
    "damage", ["unknown-key", "version-bool", "operation-disagreement", "nul", "surrogate", "nan"]
)
def test_malformed_selector_rejected_before_read_or_deepcopy(owner, audit, damage):
    selected = create_selector(create_intent())
    if damage == "unknown-key":
        selected["unknown"] = True
    elif damage == "version-bool":
        selected["resolutionVersion"] = True
    elif damage == "operation-disagreement":
        selected["expectedRequest"]["operationId"] = uid()
    else:
        selected["expectedRequest"]["name"] = {
            "nul": "\x00",
            "surrogate": "\ud800",
            "nan": float("nan"),
        }[damage]
    trace = []
    owner._db.set_trace_callback(trace.append)
    try:
        expect_fault("invalid-input", lambda: read(owner, selected))
        assert trace == [] and audit == []
    finally:
        owner._db.set_trace_callback(None)


def test_unknown_sql_template_fails_closed_and_cancellation_releases_snapshot(
    owner, audit, monkeypatch
):
    intent, _ = create_project(owner)
    original = core._catalog

    def unknown(view):
        view._db.execute("SELECT context FROM operation_claims")

    monkeypatch.setattr(core, "_catalog", unknown)
    with readonly(owner):
        expect_fault("unsupported-profile", lambda: read(owner, create_selector(intent)))
    assert audit[-1][-1]["event"] == "rollback"
    monkeypatch.setattr(core, "_catalog", original)

    def cancel(_view):
        raise KeyboardInterrupt("fixture cancel")

    monkeypatch.setattr(core, "_catalog", cancel)
    with readonly(owner), pytest.raises(KeyboardInterrupt):
        read(owner, create_selector(intent))
    assert audit[-1][-1]["event"] == "rollback"


def test_gate_complete_typed_row_unicode_and_distinct_pk_fees(owner, audit):
    _, project = create_project(owner)
    raw = 'ASCII汉😀"\\' + "".join(chr(i) for i in range(1, 32))
    first = owner.put_blob(project["projectId"], {"first": True})
    second = owner.put_blob(project["projectId"], {"second": True})
    with corrupt_immutable(owner, "job_blobs"):
        owner._db.execute(
            "UPDATE job_blobs SET payload=? WHERE project=?", (raw, project["projectId"])
        )
    gate = core._MeteredGate(owner._db, CAPS["maxEvidenceBytes"], ReadLimits())
    gate.encoding = owner._db.execute("PRAGMA encoding").fetchone()[0].upper()
    rows = owner._db.execute(
        "SELECT rowid,* FROM job_blobs WHERE ref IN (?,?)", (first, second)
    ).fetchall()
    assert len(rows) == 2
    expected = []
    for row in rows:
        full = {k: row[k] for k in row.keys() if k != "rowid"}
        expected.append(len(encoded(full)))
        assert gate._cost("job_blobs", row["rowid"]) == expected[-1]
        assert gate._cost("job_blobs", row["rowid"]) == expected[-1]
    assert gate.evidence == verify_charges(owner, audit[-1])
    schema = [x for x in audit[-1] if x["event"] == "charged" and x["table"] == "sqlite_master"]
    assert schema and gate.evidence == sum(expected) + sum(x["bytes"] for x in schema)
    assert len([x for x in audit[-1] if x["event"] == "charged" and x["table"] == "job_blobs"]) == 2


def test_low_evidence_budget_refuses_before_schema_body_materialization(owner, audit):
    intent, _ = create_project(owner)
    with readonly(owner):
        expect_fault(
            "resource-limit", lambda: read(owner, create_selector(intent), maxEvidenceBytes=1)
        )
    ledger = audit[-1]
    assert ledger[-1]["event"] == "rollback" and ledger[-1]["evidence"] == 0
    assert not [x for x in ledger if x["event"] in {"charged", "verified-row"}]
    sql = [x["sql"] for x in ledger if x["event"] == "query"]
    assert not any(x.startswith("SELECT *") or x.startswith("SELECT sql FROM") for x in sql)


@pytest.mark.parametrize(
    "encoding,length", [("UTF-8", 20 * 1024 * 1024), ("UTF-16le", 1000000), ("UTF-16be", 1000000)]
)
def test_large_real_text_probe_refuses_before_expensive_fee_sql(
    tmp_path, monkeypatch, audit, encoding, length
):
    original_connect = sqlite3.connect

    def connect(*args, **kwargs):
        db = original_connect(*args, **kwargs)
        db.execute(f"PRAGMA encoding='{encoding}'")
        return db

    monkeypatch.setattr(storage.sqlite3, "connect", connect)
    owner = JobStore(tmp_path / "large.sqlite", contract=CONTRACT, target_format=3)
    try:
        _, project = create_project(owner)
        ref = owner.put_blob(project["projectId"], "small original writer material")
        # Controlled persisted corruption beyond the original frame writer's
        # bound. This proves the low-level gate's refusal order, not a normal
        # accepted Job or a supported 20MiB public blob write.
        with corrupt_immutable(owner, "job_blobs"):
            owner._db.execute(
                "UPDATE job_blobs SET payload=? WHERE ref=?", (encoded("x" * length).decode(), ref)
            )
        rowid = owner._db.execute("SELECT rowid FROM job_blobs WHERE ref=?", (ref,)).fetchone()[0]
        gate = core._MeteredGate(owner._db, CAPS["maxEvidenceBytes"], ReadLimits())
        gate.encoding = owner._db.execute("PRAGMA encoding").fetchone()[0].upper()
        expect_fault("resource-limit", lambda: gate._cost("job_blobs", rowid))
        queries = [x["sql"] for x in audit[-1] if x["event"] == "query"]
        assert not any(
            'FROM "job_blobs"' in sql
            and ("replace(" in sql or "WITH RECURSIVE" in sql or sql.startswith("SELECT *"))
            for sql in queries
        )
        assert gate.evidence == verify_charges(owner, audit[-1])
        assert all(x["table"] == "sqlite_master" for x in audit[-1] if x["event"] == "charged")
        assert gate.probe == sum(x["work"] for x in audit[-1] if x["event"] == "probe-reserved")
    finally:
        owner.close()


def test_actual_close_and_reopen_preserves_same_original_facts(tmp_path, audit):
    path = tmp_path / "reopened.sqlite"
    owner = JobStore(path, contract=CONTRACT, target_format=3)
    job, expected = finished(owner, "test.atomic")
    selected = job_selector(job)
    with readonly(owner):
        before = read(owner, selected)
    assert before["job"] == expected
    owner.close()
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    try:
        with readonly(reopened):
            assert read(reopened, selected) == before
        verify_ledger(reopened, audit[-1])
    finally:
        reopened.close()


def test_cleanup_failure_keeps_first_reason_and_does_not_claim_release(
    tmp_path, monkeypatch, audit
):
    original_connect = sqlite3.connect

    def connect(*args, **kwargs):
        return original_connect(*args, **kwargs, factory=FaultConnection)

    monkeypatch.setattr(storage.sqlite3, "connect", connect)
    owner = JobStore(tmp_path / "cleanup.sqlite", contract=CONTRACT, target_format=3)
    try:
        intent, _ = create_project(owner)
        db = owner._db
        db.target, db.stage = "ROLLBACK", "execute"
        db.error = sqlite3.OperationalError("controlled rollback I/O seam")
        db.error.sqlite_errorcode = sqlite3.SQLITE_IOERR
        failure = expect_fault(
            "resource-limit", lambda: read(owner, create_selector(intent), maxEvidenceBytes=1)
        )
        assert failure.cleanup_failed is True
        assert db.in_transaction
        assert audit[-1][0]["event"] == "begin"
        assert not any(x["event"] == "rollback" for x in audit[-1])
    finally:
        owner._db.stage = None
        if owner._db.in_transaction:
            owner._db.execute("ROLLBACK")
        owner.close()


def accepted_changeset(owner, *, succeeded=False, multi_segment=False):
    intent, project = create_project(owner)
    owner.project = project["projectId"]
    owner.host = intent["origin"]["hostClientId"]
    owner.session = intent["origin"]["engineSessionId"]
    plan = {"definitions": [changesets.definition("first")]}
    if multi_segment:
        plan = {
            "definitions": [
                changesets.definition("x" * 20000, "a"),
                changesets.definition("y" * 20000, "b"),
            ]
        }
    ready = changesets.preview(owner, plan)
    assert ready["status"] == "ready"
    token, _document, delivered = changesets.pages(owner, ready, page_size=1)
    assert delivered[-1]["complete"] is True
    confirmed = owner.confirm_changeset(
        owner.project, ready["previewHash"], token, **changesets.host(owner)
    )
    job = changesets.create(owner, confirmed)
    if succeeded:
        owner.start_job(job["jobId"])
        job = owner.commit_job(job["jobId"])
    context = owner.job_context(job["jobId"])
    envelope = context["plan"]
    assert context["implementation"] == job["implementation"] == changesets.IMPL
    assert context["limits"] == job["limits"] == changesets.LIMITS
    selected = job_selector(job)
    selected["originalOrigin"] = {key: envelope[key] for key in ("hostClientId", "engineSessionId")}
    assert selected["originalOrigin"] == {
        "hostClientId": owner.host,
        "engineSessionId": owner.session,
    }
    return job, selected, envelope, confirmed, delivered


def verify_changeset_material_charged(owner, ledger, job, envelope):
    verify_ledger(owner, ledger)
    blobs = set()
    details = set()
    for item in ledger:
        if item["event"] != "charged":
            continue
        if item["table"] == "job_blobs":
            row = owner._db.execute(
                "SELECT project,ref FROM job_blobs WHERE rowid=?", (item["rowid"],)
            ).fetchone()
            blobs.add(tuple(row))
        elif item["table"] == "job_details":
            row = owner._db.execute(
                "SELECT project,id FROM job_details WHERE rowid=?", (item["rowid"],)
            ).fetchone()
            details.add(tuple(row))
    assert {(job["projectId"], ref) for ref in envelope["segmentBlobRefs"]} <= blobs
    assert (job["projectId"], envelope["parametersHash"]) in blobs
    assert (job["projectId"], job["confirmationRef"]) in details


@pytest.mark.parametrize("succeeded", [False, True])
def test_real_changeset_queued_and_succeeded_have_recorded_original_origin(owner, audit, succeeded):
    job, selected, envelope, _confirmed, _pages = accepted_changeset(owner, succeeded=succeeded)
    assert job["state"] == ("succeeded" if succeeded else "queued")
    with readonly(owner):
        result = read(owner, selected)
    assert result == {
        "evidenceVersion": 1,
        "kind": "job",
        "operationId": job["operationId"],
        "finding": "job-record",
        "job": job,
        "originEvidence": "recorded",
    }
    verify_changeset_material_charged(owner, audit[-1], job, envelope)


@pytest.mark.parametrize("field", ["hostClientId", "engineSessionId"])
def test_changeset_selector_original_origin_mismatch_is_identity_conflict(owner, audit, field):
    job, selected, _envelope, _confirmed, _pages = accepted_changeset(owner)
    selected["originalOrigin"][field] = uid()
    with readonly(owner):
        expect_fault("identity-conflict", lambda: read(owner, selected))
    verify_ledger(owner, audit[-1])
    assert owner.get_job(job["projectId"], job["jobId"])["state"] == "queued"


@pytest.mark.parametrize(
    "damage", ["detail-host", "detail-session", "detail-request-hash", "last-segment"]
)
def test_changeset_actual_confirmation_detail_and_last_segment_damage(owner, audit, damage):
    job, selected, envelope, confirmed, delivered = accepted_changeset(owner, multi_segment=True)
    assert len(envelope["segmentBlobRefs"]) >= 2 and len(delivered) >= 2
    # Establish that exactly these complete original records pass first.
    with readonly(owner):
        assert read(owner, selected)["finding"] == "job-record"
    verify_changeset_material_charged(owner, audit[-1], job, envelope)
    if damage == "last-segment":
        table, key = "job_blobs", envelope["segmentBlobRefs"][-1]
        payload = json.loads(
            owner._db.execute(
                "SELECT payload FROM job_blobs WHERE project=? AND ref=?", (job["projectId"], key)
            ).fetchone()[0]
        )
        assert "dataBase64" in payload
        payload["dataBase64"] = "AAAA"
        sql = "UPDATE job_blobs SET payload=? WHERE project=? AND ref=?"
    else:
        table, key = "job_details", confirmed["confirmationRef"]
        payload = json.loads(
            owner._db.execute(
                "SELECT payload FROM job_details WHERE project=? AND id=?", (job["projectId"], key)
            ).fetchone()[0]
        )
        field = {
            "detail-host": "hostClientId",
            "detail-session": "engineSessionId",
            "detail-request-hash": "requestHash",
        }[damage]
        payload[field] = "0" * 64 if field == "requestHash" else uid()
        sql = "UPDATE job_details SET payload=? WHERE project=? AND id=?"
    with corrupt_immutable(owner, table):
        owner._db.execute(sql, (encoded(payload).decode(), job["projectId"], key))
    with readonly(owner):
        result = read(owner, selected)
    assert result == {
        "evidenceVersion": 1,
        "kind": "job",
        "operationId": job["operationId"],
        "finding": "incomplete-evidence",
    }
    verify_ledger(owner, audit[-1])


@pytest.mark.parametrize("succeeded", [False, True])
def test_changeset_original_acceptance_survives_later_base_and_history(owner, audit, succeeded):
    job, selected, envelope, _confirmed, _pages = accepted_changeset(owner, succeeded=succeeded)
    original_base = envelope["preview"]["base"]
    later, _ready, _confirmed = changesets.commit(
        owner, {"definitions": [changesets.definition("later", "other")]}
    )
    assert later["state"] == "succeeded"
    assert owner.project_get(job["projectId"])["projectRevision"] > original_base
    with readonly(owner):
        result = read(owner, selected)
    assert result == {
        "evidenceVersion": 1,
        "kind": "job",
        "operationId": job["operationId"],
        "finding": "job-record",
        "job": job,
        "originEvidence": "recorded",
    }
    verify_changeset_material_charged(owner, audit[-1], job, envelope)


@pytest.mark.parametrize("actual", [0, 2, 4])
def test_actual_header_rechecked_before_any_business_evidence(owner, audit, actual):
    intent, _ = create_project(owner)
    owner._db.execute(f"PRAGMA user_version={actual}")
    try:
        with readonly(owner):
            expect_fault("state", lambda: read(owner, create_selector(intent)))
        assert [x["sql"] for x in audit[-1] if x["event"] == "query"] == ["PRAGMA user_version"]
        assert audit[-1][-1]["event"] == "rollback"
    finally:
        owner._db.execute("PRAGMA user_version=3")


@pytest.mark.parametrize("value", [1.5, 1.0, -0.5])
def test_original_successful_result_allows_finite_safe_fractional_cells(owner, audit, value):
    _, project = create_project(owner)
    job = create(owner, project=project["projectId"])
    owner.start_job(job["jobId"])
    expected = owner.finish_read_job(
        job["jobId"], [{"rowId": uid(), "ordinal": 0, "cells": [value]}]
    )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == "job-record" and result["job"] == expected
    verify_ledger(owner, audit[-1])


def test_queued_job_checks_later_current_checkpoint_in_complete_history(owner, audit):
    _, project = create_project(owner)
    job = create(owner, project=project["projectId"])
    owner.apply_application(
        project["projectId"],
        uid(),
        {"type": "metadata", "expectedVersion": 1, "patch": {"name": "later"}},
        actor=uid(),
        permission="write",
    )
    with readonly(owner):
        assert read(owner, job_selector(job))["finding"] == "job-record"
    checkpoint = owner._db.execute(
        "SELECT checkpoint FROM app_projects WHERE project=?", (project["projectId"],)
    ).fetchone()[0]
    with corrupt_immutable(owner, "app_checkpoints"):
        owner._db.execute(
            "UPDATE app_checkpoints SET payload=? WHERE id=?", ('{"corrupt":true}', checkpoint)
        )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == "incomplete-evidence"
    verify_ledger(owner, audit[-1])


@pytest.mark.parametrize(
    "created,expected", [("wrong text", "incomplete-evidence"), (None, "job-record")]
)
def test_original_nullable_integer_column_enforces_type_without_forbidding_null(
    owner, audit, created, expected
):
    job, _success = finished(owner, "test.read")
    with corrupt_immutable(owner, "job_results"):
        owner._db.execute("UPDATE job_results SET created=? WHERE job=?", (created, job["jobId"]))
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == expected
    verify_ledger(owner, audit[-1])


def test_same_cancel_object_survives_rollback_driver_failure(tmp_path, monkeypatch, audit):
    original_connect = sqlite3.connect

    def connect(*args, **kwargs):
        return original_connect(*args, **kwargs, factory=FaultConnection)

    monkeypatch.setattr(storage.sqlite3, "connect", connect)
    owner = JobStore(tmp_path / "cancel-cleanup.sqlite", contract=CONTRACT, target_format=3)
    cancellation = KeyboardInterrupt("controlled same-object cancellation")
    try:
        intent, _ = create_project(owner)
        before = "\n".join(owner._db.iterdump())

        def cancel(_view):
            raise cancellation

        monkeypatch.setattr(core, "_catalog", cancel)
        owner._db.target, owner._db.stage = "ROLLBACK", "execute"
        owner._db.error = sqlite3.OperationalError("controlled cleanup I/O seam")
        owner._db.error.sqlite_errorcode = sqlite3.SQLITE_IOERR
        with pytest.raises(KeyboardInterrupt) as raised:
            read(owner, create_selector(intent))
        assert raised.value is cancellation and cancellation.cleanup_failed is True
        assert owner._db.in_transaction
        assert not any(x["event"] == "rollback" for x in audit[-1])
        owner._db.stage = None
        owner._db.execute("ROLLBACK")
        assert "\n".join(owner._db.iterdump()) == before
    finally:
        owner._db.stage = None
        if owner._db.in_transaction:
            owner._db.execute("ROLLBACK")
        owner.close()


def running_rounds(owner, project_id=None):
    if project_id is None:
        _, project = create_project(owner)
        project_id = project["projectId"]
    job = create(
        owner,
        "test.rounds",
        project=project_id,
        parameters={"maxRounds": 2, "events": ["a", "b"], "consumePerRound": 1},
    )
    owner.start_job(job["jobId"])
    run = owner.start_job_run(job["jobId"], owner.job_context(job["jobId"])["runConfig"])
    owner.commit_job_round(
        job["jobId"], {"pendingEvents": ["b"], "consumedEvents": ["a"], "inputEvents": ["a", "b"]}
    )
    return job, run


@pytest.mark.parametrize("state", ["failed", "cancelled"])
@pytest.mark.parametrize("damage", [None, "jobId", "round-bool"])
def test_partial_round_terminal_is_exact_after_failure_or_cancellation(owner, audit, state, damage):
    job, run = running_rounds(owner)
    if state == "failed":
        owner.fail_job(
            job["jobId"],
            {
                "code": "INTERNAL_ERROR",
                "messageKey": "engine.internal",
                "params": {},
                "retryable": False,
            },
        )
    else:
        owner.cancel_job(job["projectId"], job["jobId"])
        owner.cancelled_job(job["jobId"])
    expected = owner.get_job(job["projectId"], job["jobId"])
    assert expected["state"] == state
    assert expected["commitProgress"]["committedProgress"]["lastCommittedRound"] == 1
    terminal = json.loads(
        owner._db.execute("SELECT evidence FROM run_terminal WHERE run=?", (run,)).fetchone()[0]
    )
    assert terminal == {
        "jobId": job["jobId"],
        "committedProgress": expected["commitProgress"]["committedProgress"],
    }
    if damage is not None:
        if damage == "jobId":
            terminal["jobId"] = uid()
        else:
            terminal["committedProgress"]["lastCommittedRound"] = True
        with corrupt_immutable(owner, "run_terminal"):
            owner._db.execute(
                "UPDATE run_terminal SET evidence=? WHERE run=?", (encoded(terminal).decode(), run)
            )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == ("job-record" if damage is None else "incomplete-evidence")
    if damage is None:
        assert result["job"] == expected
    verify_ledger(owner, audit[-1])


@pytest.mark.parametrize("kind", ["null-run-orphan", "same-job-cross-run"])
def test_reverse_round_job_relation_cannot_hide_orphan_or_cross_run(owner, audit, kind):
    if kind == "null-run-orphan":
        _, project = create_project(owner)
        target = create(
            owner, "test.rounds", project=project["projectId"], parameters={"maxRounds": 2}
        )
        assert (
            owner._db.execute("SELECT run FROM jobs WHERE id=?", (target["jobId"],)).fetchone()[0]
            is None
        )
    else:
        target, _target_run = running_rounds(owner)
    _other, other_run = running_rounds(owner, target["projectId"])
    with readonly(owner):
        assert read(owner, job_selector(target))["finding"] == "job-record"
    with corrupt_immutable(owner, "rounds"):
        owner._db.execute("UPDATE rounds SET job=? WHERE run=?", (target["jobId"], other_run))
    with readonly(owner):
        result = read(owner, job_selector(target))
    assert result["finding"] == "incomplete-evidence"
    verify_ledger(owner, audit[-1])


@pytest.mark.parametrize("field", ["config", "parametersHash"])
def test_success_consumption_self_hashed_blob_still_must_match_original_material(
    owner, audit, field
):
    job, success = finished(owner, "test.rounds")
    run = owner._db.execute("SELECT run FROM jobs WHERE id=?", (job["jobId"],)).fetchone()[0]
    terminal = json.loads(
        owner._db.execute("SELECT evidence FROM run_terminal WHERE run=?", (run,)).fetchone()[0]
    )
    wrong = deepcopy(owner.blob(job["projectId"], terminal["eventConsumptionRef"]))
    if field == "config":
        wrong["config"]["maxRounds"] += 1
    else:
        wrong["parametersHash"] = "f" * 64
    # A genuine content-addressed blob from the original writer, with all refs
    # changed consistently. Rejection therefore needs the original relationship
    # check rather than merely a corrupted blob hash or broken summary pointer.
    ref = owner.put_blob(job["projectId"], wrong)
    assert owner.blob(job["projectId"], ref) == wrong
    terminal["eventConsumptionRef"] = ref
    with corrupt_immutable(owner, "run_terminal"):
        owner._db.execute(
            "UPDATE run_terminal SET evidence=? WHERE run=?", (encoded(terminal).decode(), run)
        )
    result_id = success["resultRef"]["resultId"]
    payload = json.loads(
        owner._db.execute("SELECT payload FROM results WHERE id=?", (result_id,)).fetchone()[0]
    )
    assert payload[0]["cells"][0] == "run.summary.v1"
    payload[0]["cells"][-1] = ref
    with corrupt_immutable(owner, "results"):
        owner._db.execute(
            "UPDATE results SET payload=? WHERE id=?", (encoded(payload).decode(), result_id)
        )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == "incomplete-evidence"
    verify_ledger(owner, audit[-1])


def test_corrupt_schema_probe_shape_has_finite_incomplete_result(owner, audit):
    _, project = create_project(owner)
    job = create(owner, project=project["projectId"])
    db = owner._db
    sql = db.execute("SELECT sql FROM sqlite_master WHERE name='jobs'").fetchone()[0]
    # Controlled persisted-schema corruption, outside the normal writer; this
    # tests the new preflight schema fee route, not a legitimate DDL migration.
    db.execute("PRAGMA writable_schema=ON")
    db.execute("UPDATE sqlite_master SET sql=? WHERE name='jobs'", (sql + "\0",))
    db.execute("PRAGMA writable_schema=OFF")
    try:
        with readonly(owner):
            result = read(owner, job_selector(job))
        assert result == {
            "evidenceVersion": 1,
            "kind": "job",
            "operationId": job["operationId"],
            "finding": "incomplete-evidence",
        }
        verify_ledger(owner, audit[-1])
    finally:
        db.execute("PRAGMA writable_schema=ON")
        db.execute("UPDATE sqlite_master SET sql=? WHERE name='jobs'", (sql,))
        db.execute("PRAGMA writable_schema=OFF")


def test_hash_consistent_bad_context_container_is_incomplete(owner, audit):
    _, project = create_project(owner)
    job = create(owner, project=project["projectId"])
    context = owner.job_context(job["jobId"])
    context.pop("job")
    context["manifests"] = []
    fingerprint = storage.digest(context)
    with corrupt_immutable(owner, "jobs"), corrupt_immutable(owner, "operation_claims"):
        owner._db.execute(
            "UPDATE jobs SET context=?,fingerprint=? WHERE id=?",
            (encoded(context).decode(), fingerprint, job["jobId"]),
        )
        owner._db.execute(
            "UPDATE operation_claims SET fingerprint=? WHERE operation=?",
            (fingerprint, job["operationId"]),
        )
    with readonly(owner):
        result = read(owner, job_selector(job))
    assert result["finding"] == "incomplete-evidence"
    verify_ledger(owner, audit[-1])
