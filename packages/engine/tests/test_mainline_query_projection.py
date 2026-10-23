"""Source-only tests for the adopted pure query projection.

These definitions have not run. The real JobStore exercises SQLite and the
existing writer; the explicit authority/budget doubles do not attest a production
issuer, physical holding, executor, worker, IPC or permission grant.
"""

from contextlib import nullcontext
from copy import deepcopy
from types import SimpleNamespace
from uuid import uuid4

import pytest
from ontolearn_engine import resources
from ontolearn_engine.job_store import JobFault, JobStore, fault
from ontolearn_engine.project.query_definitions import (
    ProjectGetReadTicket,
    QueryDispatchAuthority,
    QueryRead,
    QueryReadBudget,
    query_read,
)
from ontolearn_engine.resources import CONTRACT, LIMITS
from ontolearn_engine.storage import canonical, digest

INTERNAL = "mainline-query"
DEFINITION = {
    "text": "SELECT ?s WHERE { ?s ?p ?o }",
    "references": [],
    "descriptor": {
        "version": 1,
        "name": "Query",
        "description": "projection fixture",
        "scope": "asserted",
        "capabilityQuestion": "Which s?",
        "source": "editor",
    },
}
IMPLEMENTATION = {
    "engineVersion": "0.1.0",
    "executionSemanticsVersion": "i05-finite-6",
    "dependencyLockHash": "a" * 64,
}


class Budget(QueryReadBudget):
    """A visibly synthetic prepaid test scope, never production capacity."""

    def __init__(self):
        self.calls = []
        self.values = []
        self.on_store = None
        self.block_stage = None

    def reserve_store(self, stage, request):
        self.calls.append((stage, deepcopy(request)))
        if self.on_store is not None:
            self.on_store()

    def reserve(self, stage, *, bytes_, objects, work):
        self.calls.append((stage, bytes_, objects, work))
        if stage == self.block_stage:
            fault("RESOURCE_LIMIT", resource="memory")

    def handoff(self, value):
        self.values.append(value)


class Issuer(QueryDispatchAuthority):
    """Explicit test authority for exact ticket checks; not an installed issuer."""

    def __init__(self):
        self.generation = 1
        self.valid = True
        self.finished = []

    def take(self, actor, request):
        raise AssertionError("this fixture supplies its explicit ticket directly")

    def check(self, ticket, actor, store):
        if (
            not self.valid
            or actor is not ticket.read.actor
            or store is not ticket.read.store
            or ticket.generation != self.generation
        ):
            fault("PERMISSION_DENIED")

    def finish(self, ticket, *, emitted, failure=None):
        self.finished.append((ticket, emitted, failure))


@pytest.fixture
def store(tmp_path):
    value = JobStore(tmp_path / "projection.sqlite", contract=CONTRACT)
    value.create_project(INTERNAL)
    value.project = value.public_project(INTERNAL)
    # Explicit cold legacy fixture: definition/version rows exist before any
    # snapshot or operation history. Setup is not a new product writer API.
    with value._transaction():
        value._db.execute(
            "INSERT INTO definitions VALUES(?,?,?,?)",
            (INTERNAL, "query", "Q1", canonical(DEFINITION)),
        )
        value._db.execute("INSERT INTO versions VALUES(?,?,?)", (INTERNAL, "query:Q1", 1))
    assert value._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 0
    yield value
    value.close()


def context(store):
    budget = Budget()
    authority = SimpleNamespace(read_scope=lambda *args: nullcontext(budget))
    owner = str(uuid4())
    book = SimpleNamespace(owner_id=owner, authority=authority, require_owner=lambda _: None)

    def authorize(params):
        if params != {"projectId": store.project}:
            fault("PERMISSION_DENIED")

    actor = SimpleNamespace(
        store=store,
        session="original-session",
        ordinary=book,
        _authorize=authorize,
    )
    read = QueryRead(actor, authority, actor.session, store, store.project, budget, book, owner)
    return actor, budget, read


def params(store, selection=None):
    return {
        "projectId": store.project,
        "definitionId": "Q1",
        "selection": selection or {"kind": "current"},
    }


def load(store, actor, request):
    with query_read(actor, "query.definition.load", request) as ticket:
        return store.load_query_definition(request, ticket=ticket)


def project_ticket(store, actor, read):
    snapshot = store._snapshot_projection(INTERNAL)  # Fixture binding only.
    issuer = Issuer()
    actor.query_dispatch = issuer
    ticket = ProjectGetReadTicket(
        issuer,
        read,
        "fixed-request",
        store.project,
        snapshot["projectRevision"],
        digest(snapshot),
        actor.ordinary.owner_id,
        1,
        1,
    )
    return issuer, ticket


def prepare_params(store, record):
    return {
        "projectId": store.project,
        "operationId": str(uuid4()),
        "definitionBinding": {
            key: record[key]
            for key in (
                "definitionId",
                "definitionVersion",
                "definitionSha256",
                "descriptorVersion",
                "descriptorSha256",
            )
        },
        "visibleDraft": deepcopy(record["draft"]),
        "selection": {"kind": "current"},
    }


def dump(store):
    return "\n".join(store._db.iterdump())


def test_current_definition_and_query_get_share_cold_digest_without_write_sql(store):
    actor, budget, read = context(store)
    issuer, ticket = project_ticket(store, actor, read)
    before = dump(store)
    trace = []
    store._db.execute("PRAGMA query_only=ON")
    store._db.set_trace_callback(trace.append)
    try:
        record = load(store, actor, params(store))
        project = store.query_project_get(store.project, actor=actor, ticket=ticket)
    finally:
        store._db.set_trace_callback(None)
        store._db.execute("PRAGMA query_only=OFF")
    assert record["kind"] == "managed"
    assert record["definitionSha256"] == digest(DEFINITION)
    assert record["inputSnapshotId"] == project["inputSnapshotId"] == ticket.snapshot
    assert record["baseProjectRevision"] == project["projectRevision"] == 0
    assert record["definitionVersion"] == 1
    assert CONTRACT.validate("result_query.definition.load", record)
    assert dump(store) == before
    assert store._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 0
    assert ticket.used and not ticket.finished and issuer.finished == []
    assert budget.values == [record, project]
    assert not any("BEGIN IMMEDIATE" in sql.upper() for sql in trace)
    assert not any(
        sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
        for sql in trace
    )


def test_missing_dispatch_ticket_denies_before_any_store_sql(store):
    actor, _, _ = context(store)
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        with pytest.raises(JobFault, match="PERMISSION_DENIED"):
            store.query_project_get(store.project, actor=actor, ticket=None)
    finally:
        store._db.set_trace_callback(None)
    assert trace == []


@pytest.mark.parametrize("mutation", ["revoked", "generation", "session", "replayed"])
def test_dispatch_originals_generation_and_single_use_fence_before_sql(store, mutation):
    actor, budget, read = context(store)
    issuer, ticket = project_ticket(store, actor, read)
    if mutation == "revoked":
        budget.on_store = lambda: setattr(issuer, "valid", False)
    elif mutation == "generation":
        issuer.generation += 1
    elif mutation == "session":
        actor.session = "successor-session"
    else:
        ticket.consume(actor, store, store.project)
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        with pytest.raises(JobFault, match="PERMISSION_DENIED"):
            store.query_project_get(store.project, actor=actor, ticket=ticket)
    finally:
        store._db.set_trace_callback(None)
    assert trace == [] and budget.values == []


def test_current_reply_keeps_fixed_revision_and_snapshot_fence(store):
    actor, budget, read = context(store)
    _, ticket = project_ticket(store, actor, read)
    ticket.snapshot = "f" * 64
    before = dump(store)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.query_project_get(store.project, actor=actor, ticket=ticket)
    assert ticket.used and budget.values == [] and dump(store) == before


def test_missing_read_scope_is_not_replaced_with_a_default_grant(store):
    actor, budget, _ = context(store)
    actor.ordinary.authority.read_scope = lambda *args: None
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        with pytest.raises(JobFault, match="PERMISSION_DENIED"):
            load(store, actor, params(store))
    finally:
        store._db.set_trace_callback(None)
    assert trace == [] and budget.calls == [] and budget.values == []


def test_historical_missing_row_never_substitutes_current_projection(store):
    actor, _, _ = context(store)
    current = load(store, actor, params(store))
    before = dump(store)
    with pytest.raises(KeyError, match="Missing replay input snapshot"):
        load(
            store,
            actor,
            params(store, {"kind": "historical", "snapshotId": current["inputSnapshotId"]}),
        )
    assert dump(store) == before
    identity = store.snapshot(INTERNAL)  # Explicit normal writer, outside the read.
    historical = load(store, actor, params(store, {"kind": "historical", "snapshotId": identity}))
    assert historical == current


def test_corrupt_existing_current_row_is_rejected_without_repair(store):
    actor, budget, read = context(store)
    _, ticket = project_ticket(store, actor, read)
    store._db.execute("INSERT INTO snapshots VALUES(?,?)", (ticket.snapshot, "{}"))
    before = dump(store)
    with pytest.raises(ValueError, match="Snapshot integrity failure"):
        load(store, actor, params(store))
    with pytest.raises(ValueError, match="Snapshot integrity failure"):
        store.query_project_get(store.project, actor=actor, ticket=ticket)
    assert dump(store) == before and budget.values == []


def test_read_ticket_cannot_be_reused_for_another_project(store):
    actor, _, read = context(store)
    other = str(uuid4())
    request = params(store)
    request["projectId"] = other
    before = dump(store)
    with pytest.raises(JobFault, match="PERMISSION_DENIED"):
        store.load_query_definition(request, ticket=read)
    assert dump(store) == before


def test_prepare_uses_pure_current_input_without_materializing_it(store, monkeypatch):
    """Wiring-only validator double; does not attest the missing real executor."""
    actor, budget, _ = context(store)
    record = load(store, actor, params(store))
    request = prepare_params(store, record)
    observed = []
    monkeypatch.setattr(
        resources, "semantic_identity", lambda: deepcopy(IMPLEMENTATION), raising=False
    )

    def validate(project, input_, parameters, snapshot, implementation, confirmation, *, live):
        observed.append((project, deepcopy(input_), deepcopy(parameters), deepcopy(snapshot), live))
        assert implementation == IMPLEMENTATION and confirmation is None and not live

    monkeypatch.setattr(store, "prepare_query_request", validate)
    with query_read(actor, "query.execution.prepare", request) as ticket:
        result = store.prepare_query_execution_input(
            request,
            IMPLEMENTATION,
            LIMITS,
            "b" * 64,
            ticket=ticket,
        )
    assert len(observed) == 1 and observed[0][4] is False
    assert digest(observed[0][3]) == record["inputSnapshotId"]
    assert result["input"]["inputSnapshotId"] == record["inputSnapshotId"]
    assert store.blob(store.project, result["input"]["parametersHash"]) == {
        "inputSelection": "current"
    }
    assert store._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 0
    assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
    assert CONTRACT.validate("result_query.execution.prepare", result)
    assert result is budget.values[-1]


@pytest.mark.parametrize("failure", ["stale-binding", "budget"])
def test_failed_prepare_keeps_snapshot_blob_job_and_claim_state_unchanged(store, failure):
    actor, budget, _ = context(store)
    record = load(store, actor, params(store))
    request = prepare_params(store, record)
    if failure == "stale-binding":
        request["definitionBinding"]["definitionSha256"] = "f" * 64
    else:
        budget.block_stage = "parameters blob"
    before = dump(store)
    with pytest.raises(
        JobFault, match="IDENTITY_CONFLICT" if failure == "stale-binding" else "RESOURCE_LIMIT"
    ):
        with query_read(actor, "query.execution.prepare", request) as ticket:
            store.prepare_query_execution_input(
                request, IMPLEMENTATION, LIMITS, "b" * 64, ticket=ticket
            )
    assert dump(store) == before


def test_original_normal_writer_materializes_cold_digest_on_acceptance_only(store):
    """Real existing infrastructure acceptance, not query executor validation."""
    actor, _, _ = context(store)
    record = load(store, actor, params(store))
    input_ = {
        "inputSnapshotId": record["inputSnapshotId"],
        "scope": "asserted",
        "definitionId": "probe",
        "derivedResultIds": [],
        "parametersHash": store.put_blob(store.project, {}),
        "preparedPlanRef": None,
    }
    assert store._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 0
    job = store.create_job(
        store.project, str(uuid4()), "test.read", input_, None, IMPLEMENTATION, LIMITS
    )
    assert job["inputSnapshotId"] == record["inputSnapshotId"]
    assert (
        store.load_snapshot(record["inputSnapshotId"])
        == store.job_context(job["jobId"])["snapshot"]
    )
    assert store._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 1


def test_original_normal_writer_rolls_cold_snapshot_back_with_rejected_job(store):
    actor, _, _ = context(store)
    record = load(store, actor, params(store))
    input_ = {
        "inputSnapshotId": record["inputSnapshotId"],
        "scope": "asserted",
        "definitionId": "probe",
        "derivedResultIds": [],
        "parametersHash": store.put_blob(store.project, {}),
        "preparedPlanRef": None,
    }
    before = dump(store)

    def reject(phase):
        if phase == "before_commit":
            raise RuntimeError("actual acceptance rollback")

    with pytest.raises(RuntimeError, match="actual acceptance rollback"):
        store.create_job(
            store.project,
            str(uuid4()),
            "test.read",
            input_,
            None,
            IMPLEMENTATION,
            LIMITS,
            _acceptance_hook=reject,
        )
    assert dump(store) == before
    assert store._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 0
    assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
    assert store._db.execute("SELECT count(*) FROM operation_claims").fetchone()[0] == 0


def test_prepare_cannot_borrow_another_projects_read_scope_before_claim_sql(store):
    actor, _, read = context(store)
    record = load(store, actor, params(store))
    request = prepare_params(store, record)
    request["projectId"] = str(uuid4())
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        with pytest.raises(JobFault, match="PERMISSION_DENIED"):
            store.prepare_query_execution_input(
                request,
                IMPLEMENTATION,
                LIMITS,
                "b" * 64,
                ticket=read,
            )
    finally:
        store._db.set_trace_callback(None)
    assert trace == []
