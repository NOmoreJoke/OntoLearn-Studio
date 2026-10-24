"""SOURCE definitions only; runtime requires a separate ticket.

Finite in-memory doubles test consumption/fences, never attest a physical issuer,
SQLite read bound, accepted worker, IPC bridge or production permission.
"""

import json
from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project.query_definitions import (
    ProjectGetReadTicket,
    QueryDispatchAuthority,
    QueryRead,
    QueryReadBudget,
    draft,
    load,
    query_read,
)
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = json.loads((ROOT / "packages/contracts/v2/fixtures.json").read_text(encoding="utf-8"))
BINDINGS = json.loads(
    (ROOT / "packages/contracts/v2/binding-regressions.json").read_text(encoding="utf-8")
)
SAMPLES = FIXTURES["queryConsumer"]["samples"]
SHAPES = [c for c in FIXTURES["cases"] if c["name"].startswith("query consumer ")]


@pytest.mark.parametrize("case", SHAPES, ids=lambda c: c["name"])
def test_query_shape_corpus(case):
    assert CONTRACT.validate(case["schema"], case["value"]) is case["valid"]


@pytest.mark.parametrize("case", BINDINGS["queryConsumer"], ids=lambda c: c["name"])
def test_query_binding_corpus(case):
    q, r = case["request"], case["response"]
    if q["method"] == "job.create":
        actual = CONTRACT.matches_response(q, r)
    else:
        actual = CONTRACT.matches_query_consumer_response(q, r, case["binding"])
    assert actual is case["valid"]


@pytest.mark.parametrize("case", FIXTURES["queryConsumer"]["service"], ids=lambda c: c["name"])
def test_service_error_wire_association_is_separate(case):
    assert CONTRACT.matches_query_consumer_response(case["request"], case["response"]) is True
    assert case["response"]["error"]["code"] == case["expectedCode"]
    assert case["response"]["error"]["params"] == case["expectedParams"]


class Budget(QueryReadBudget):
    def __init__(self):
        self.calls, self.holding = [], []
        self.during = None

    def reserve_store(self, stage, request):
        self.calls.append((stage, deepcopy(request)))
        if self.during:
            self.during()

    def reserve(self, stage, *, bytes_, objects, work):
        self.calls.append((stage, bytes_, objects, work))

    def handoff(self, value):
        self.holding.append(value)


class StoreDouble:
    """Logical pure-read supplier; the SELECT handle does not execute SQLite."""

    contract = CONTRACT
    project = SAMPLES["managed"]["projectId"]

    def __init__(self):
        self.calls = []
        self.result = deepcopy(
            next(
                c["response"]["result"]
                for c in FIXTURES["responses"]
                if c["name"] == "matching project.get"
            )
        )
        definition = deepcopy(SAMPLES["storedDefinition"])
        self.snapshot_value = {
            "project": "internal",
            "projectRevision": 1,
            "state": {
                "definitions": [{"id": "Q1", "layer": "query", "payload": json.dumps(definition)}],
                "facts": [],
                "mappingState": {},
            },
            "dependencyVector": {"query:Q1": 1},
        }
        self.result.update(
            projectId=self.project,
            projectRevision=1,
            inputSnapshotId=digest(self.snapshot_value),
            dependencyVector=deepcopy(self.snapshot_value["dependencyVector"]),
        )
        self.snapshot_present = False
        self._db = SimpleNamespace(execute=self._snapshot_select)

    def _snapshot_select(self, statement, arguments):
        assert statement == "SELECT 1 FROM snapshots WHERE id=?"
        assert arguments == (digest(self.snapshot_value),)
        self.calls.append("snapshot SELECT")
        return SimpleNamespace(fetchone=lambda: (1,) if self.snapshot_present else None)

    def _snapshot_projection(self, internal):
        assert internal == "internal"
        self.calls.append("pure current projection")
        return deepcopy(self.snapshot_value)

    def _read(self):
        return nullcontext()

    def _valid(self, name, value):
        if not CONTRACT.validate(name, value):
            from ontolearn_engine.job_store import fault

            fault("INVALID_REQUEST", field="params")

    def _project(self, identity):
        assert identity == self.project
        self.calls.append("project")
        return "internal"

    def _project_snapshot(self, identity, project):
        assert project == "internal" and identity == digest(self.snapshot_value)
        self.calls.append("historical snapshot")
        return self.snapshot_value

    def snapshot(self, internal):
        raise AssertionError("query read must never call the old write-style snapshot")

    def project_get(self, project):
        assert project == self.project
        self.calls.append("original project_get")
        return deepcopy(self.result)


def originals():
    store, budget = StoreDouble(), Budget()
    authority = SimpleNamespace(read_scope=lambda *args: nullcontext(budget))
    book = SimpleNamespace(owner_id="owner", authority=authority, require_owner=lambda owner: None)
    actor = SimpleNamespace(
        store=store, session="session", ordinary=book, _authorize=lambda request: None
    )
    read = QueryRead(
        actor, authority, actor.session, store, store.project, budget, book, book.owner_id
    )
    return actor, store, budget, read


class BridgeDouble(QueryDispatchAuthority):
    """Explicit synthetic external authority; not a production implementation."""

    def __init__(self):
        self.valid = True
        self.finishes = []
        self.fail_finish = None

    def take(self, actor, request):
        raise AssertionError("this test directly constructs its explicit fake ticket")

    def check(self, ticket, actor, store):
        if not self.valid or actor is not ticket.read.actor or store is not ticket.read.store:
            from ontolearn_engine.job_store import fault

            fault("PERMISSION_DENIED")

    def finish(self, ticket, *, emitted, failure=None):
        if self.fail_finish:
            raise self.fail_finish
        if not any(t is ticket for t, _, _ in self.finishes):
            self.finishes.append((ticket, emitted, failure))


def base_ticket():
    actor, store, budget, read = originals()
    bridge = BridgeDouble()
    actor.query_dispatch = bridge
    ticket = ProjectGetReadTicket(
        bridge, read, "request", store.project, 1, store.result["inputSnapshotId"], "owner", 1, 1
    )
    return actor, store, budget, bridge, ticket


def test_missing_read_scope_denies_before_store_and_holding():
    actor, store, budget, _ = originals()
    actor.ordinary.authority.read_scope = lambda *args: None
    with pytest.raises(JobFault) as error:
        with query_read(actor, "query.definition.load", {"projectId": store.project}):
            pytest.fail("missing authority entered")
    assert error.value.code == "PERMISSION_DENIED"
    assert store.calls == [] and budget.calls == [] and budget.holding == []


@pytest.mark.parametrize("change", ["store", "session", "authority", "inactive"])
def test_read_originals_are_not_caller_values(change):
    actor, store, _, read = originals()
    if change == "store":
        actor.store = object()
    elif change == "session":
        actor.session = "other"
    elif change == "authority":
        actor.ordinary.authority = object()
    else:
        read.active = False
    with pytest.raises(JobFault):
        read.check(store)


def test_reserve_callback_revocation_prevents_original_get():
    actor, store, budget, bridge, ticket = base_ticket()
    budget.during = lambda: setattr(bridge, "valid", False)
    with pytest.raises(JobFault):
        JobStore.query_project_get(store, store.project, actor=actor, ticket=ticket)
    assert "original project_get" not in store.calls
    assert not ticket.used


def test_valid_base_ticket_calls_pure_get_once_and_hands_off_original_reply():
    actor, store, budget, bridge, ticket = base_ticket()
    result = JobStore.query_project_get(store, store.project, actor=actor, ticket=ticket)
    assert result == store.result and result is not store.result
    assert store.calls == ["original project_get"]
    assert ticket.used and not ticket.finished and budget.holding == [result]
    assert result is budget.holding[0]
    with pytest.raises(JobFault):
        JobStore.query_project_get(store, store.project, actor=actor, ticket=ticket)
    assert store.calls == ["original project_get"] and budget.holding == [result]
    ticket.finish(emitted=True)
    ticket.finish(emitted=True)
    assert bridge.finishes == [(ticket, True, None)]


@pytest.mark.parametrize("change", ["issuer", "project", "owner", "generation", "foreign_store"])
def test_base_foreign_binding_cannot_widen_ordinary(change):
    actor, store, _, _, ticket = base_ticket()
    target = store
    if change == "issuer":
        actor.query_dispatch = BridgeDouble()
    elif change == "project":
        ticket.project = "other"
    elif change == "owner":
        ticket.owner_id = "other"
    elif change == "generation":
        ticket.generation = -1
    else:
        target = StoreDouble()
    with pytest.raises(JobFault):
        JobStore.query_project_get(target, store.project, actor=actor, ticket=ticket)
    assert "original project_get" not in target.calls


def test_late_reply_and_failed_emit_keep_actual_terminal_responsibility():
    actor, store, _, bridge, ticket = base_ticket()
    ticket.consume(actor, store, store.project)
    store.result["projectRevision"] = 2
    with pytest.raises(JobFault):
        ticket.reply(store, store.result)
    first = RuntimeError("actual emit failed")
    bridge.fail_finish = first
    with pytest.raises(RuntimeError) as error:
        ticket.finish(emitted=False, failure=first)
    assert error.value is first and not ticket.finished
    bridge.fail_finish = None
    ticket.finish(emitted=False, failure=first)
    assert bridge.finishes == [(ticket, False, first)] and ticket.finished


@pytest.mark.parametrize("persisted", [False, True])
def test_current_load_uses_pure_projection_select_and_original_handoff(persisted):
    _, store, budget, read = originals()
    store.snapshot_present = persisted
    before = deepcopy(store.snapshot_value)
    result = load(store, deepcopy(SAMPLES["params"]["query.definition.load"]), read)
    assert result["kind"] == "managed"
    assert result["inputSnapshotId"] == digest(before)
    assert result["definitionSha256"] == digest(SAMPLES["storedDefinition"])
    assert result is budget.holding[-1] and len(budget.holding) == 1
    assert store.calls == ["project", "pure current projection", "snapshot SELECT"] + (
        ["historical snapshot"] if persisted else []
    )
    assert store.snapshot_value == before


def test_current_load_corrupt_existing_snapshot_denies_before_handoff():
    _, store, budget, read = originals()
    store.snapshot_present = True
    store._project_snapshot = lambda *args: {"corrupt": "persisted fixture"}
    with pytest.raises(JobFault) as error:
        load(store, deepcopy(SAMPLES["params"]["query.definition.load"]), read)
    assert error.value.code == "INVALID_STATE"
    assert budget.holding == []
    assert store.calls == ["project", "pure current projection", "snapshot SELECT"]


def test_historical_load_uses_legal_hash_and_actual_record_descriptor():
    _, store, budget, read = originals()
    params = deepcopy(SAMPLES["params"]["query.definition.load"])
    params["selection"] = {"kind": "historical", "snapshotId": digest(store.snapshot_value)}
    result = load(store, params, read)
    assert result["kind"] == "managed"
    assert result["definitionSha256"] == digest(SAMPLES["storedDefinition"])
    assert result["inputSnapshotId"] == digest(store.snapshot_value)
    assert result is budget.holding[-1]


def test_draft_d1_is_utf16_not_presentation_scalars_and_trims_fixed_edges():
    value = deepcopy(SAMPLES["draft"])
    value["name"] = "😀" * 64
    assert draft(value)["name"] == value["name"]
    value["name"] += "x"
    with pytest.raises(JobFault):
        draft(value)
    value["name"] = "\x1c Query\ufeff"
    assert draft(value)["name"] == "Query"
    value["sparql"] = "\ud800"
    with pytest.raises(JobFault):
        draft(value)


def test_authority_callback_session_swap_is_rechecked_before_read():
    actor, store, _, read = originals()
    actor.ordinary.require_owner = lambda owner: setattr(actor, "session", "successor")
    with pytest.raises(JobFault):
        read.check(store)
    assert store.calls == []


def test_reentrant_consumption_does_not_get_two_original_gets():
    actor, store, budget, bridge, ticket = base_ticket()
    rejected = []

    def reenter():
        try:
            ticket.consume(actor, store, store.project)
        except JobFault as error:
            rejected.append(error.code)

    budget.during = reenter
    ticket.consume(actor, store, store.project)
    assert rejected == ["PERMISSION_DENIED"] and ticket.used
    assert store.calls == []


def test_finish_unknown_retries_same_first_actual_emission_event():
    _, _, _, bridge, ticket = base_ticket()
    first = RuntimeError("finish unknown")
    bridge.fail_finish = first
    with pytest.raises(RuntimeError):
        ticket.finish(emitted=True)
    bridge.fail_finish = None
    ticket.finish(emitted=False, failure=RuntimeError("later owner cleanup"))
    assert bridge.finishes == [(ticket, True, None)]


def test_prepare_exact_existing_claim_reuses_original_job_without_new_blob_or_current_read():
    from ontolearn_engine.project.query_definitions import prepare

    actor, store, budget, read = originals()
    original = deepcopy(SAMPLES["job"])
    snapshot = store.snapshot_value
    original["input"]["inputSnapshotId"] = digest(snapshot)
    original["inputSnapshotId"] = digest(snapshot)
    claim = {"job": original["jobId"]}
    store._transaction = lambda: nullcontext()
    store._db = SimpleNamespace(
        execute=lambda statement, args: SimpleNamespace(fetchone=lambda: claim)
    )
    store.get_job = lambda project, job: deepcopy(original)
    observed = []

    def accepted(row, project, capability, input_, confirmation, implementation, limits):
        observed.append(
            (row, project, capability, deepcopy(input_), confirmation, implementation, limits)
        )
        assert input_ == original["input"] and implementation == original["implementation"]
        return deepcopy(original)

    store._accepted_job = accepted
    store.job_context = lambda job: {"snapshot": snapshot}
    store.blob = lambda project, key: {"inputSelection": "current"}
    store.put_blob = lambda *args: pytest.fail(
        "existing accepted claim must not write a second blob"
    )
    store.prepare_query_request = lambda *args, **kwargs: pytest.fail(
        "existing claim must not rebuild/reexecute"
    )
    result = prepare(
        store,
        deepcopy(SAMPLES["params"]["query.execution.prepare"]),
        {"different": "ignored for original claim"},
        {},
        "b" * 64,
        read,
    )
    assert len(observed) == 1
    assert result["input"] == original["input"]
    assert result["executionIdentity"]["implementation"] == original["implementation"]
    assert result["executionIdentity"]["limits"] == original["limits"]
    assert result is budget.holding[-1]


@pytest.mark.parametrize("stage", ["read_scope", "enter", "reserve"])
@pytest.mark.parametrize("mutation", ["book", "owner"])
def test_scope_callbacks_cannot_adopt_replacement_book_or_owner(stage, mutation):
    actor, store, budget, _ = originals()
    original_book = actor.ordinary
    original_owner = original_book.owner_id
    authority = original_book.authority
    failures = []
    entered = []

    def replace():
        if mutation == "book":
            actor.ordinary = SimpleNamespace(
                owner_id=original_owner, authority=authority, require_owner=lambda owner: None
            )
        else:
            original_book.owner_id = "replacement-owner"

    class Scope:
        def __enter__(self):
            entered.append(True)
            if stage == "enter":
                replace()
            return budget

        def __exit__(self, kind, error, traceback):
            # Explicit fake owner keeps the actual first failure; no fake claim
            # that a context exit releases unknown work/material in production.
            if error is not None:
                failures.append(error)

    def acquire(*args):
        if stage == "read_scope":
            replace()
        return Scope()

    authority.read_scope = acquire
    if stage == "reserve":
        budget.during = replace
    with pytest.raises(JobFault) as error:
        with query_read(actor, "query.definition.load", {"projectId": store.project}):
            pytest.fail("replacement original entered Store consumer")
    assert error.value.code == "PERMISSION_DENIED"
    assert entered == [True] and failures == [error.value]
    assert store.calls == [] and budget.holding == []
    assert len(budget.calls) == (1 if stage == "reserve" else 0)
