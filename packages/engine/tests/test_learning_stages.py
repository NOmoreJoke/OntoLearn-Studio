"""Synthetic owner ledger tests, not domain execution or approved public stage DTOs."""

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from ontolearn_engine.learning.baselines import read_json
from ontolearn_engine.learning.service import Context
from ontolearn_engine.learning.stages import (
    SIGNATURE,
    FetchedPage,
    StageBindingError,
    StageCompletion,
    StagePlan,
    StageRef,
    StageSlot,
    StoredStage,
    bind_stages,
    require_current,
)
from ontolearn_engine.resources import CONTRACT

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = read_json(ROOT / "packages/contracts/v2/fixtures.json")["cases"]
PROJECT = "00000000-0000-4000-8000-000000000001"
H0, H1, H2 = "0" * 64, "1" * 64, "2" * 64
CONTEXT = Context(PROJECT, "query", "attempt-1", "closed-input")


def uid(number):
    return f"00000000-0000-4000-8000-{number:012d}"


def result_stage(ordinal, snapshot, version, historical):
    result = deepcopy(next(c["value"] for c in FIXTURES if c["schema"] == "result" and c["valid"]))
    result.update(
        resultId=uid(10 + ordinal),
        jobId=uid(20 + ordinal),
        inputSnapshotId=snapshot,
        inputProjectRevision=ordinal + 1,
        state="historical" if historical else "current",
        historicalSelectionRequired=historical,
        staleReason=[],
    )
    job = deepcopy(
        next(
            c["value"]
            for c in FIXTURES
            if c["schema"] == "job" and c["valid"] and c["value"]["state"] == "succeeded"
        )
    )
    job.update(
        jobId=result["jobId"],
        operationId=uid(30 + ordinal),
        capability="query.execute",
        commitProgress={"mode": "none"},
        resultRef={"resultId": result["resultId"], "inputSnapshotId": snapshot},
        **{
            key: deepcopy(result[key])
            for key in (
                "inputSnapshotId",
                "dependencyVector",
                "definitionSetDigests",
                "parametersHash",
                "scope",
                "implementation",
            )
        },
    )
    job["input"].update(
        inputSnapshotId=snapshot,
        scope=result["scope"],
        definitionId=result["definitionId"],
        parametersHash=result["parametersHash"],
    )
    page = {
        "binding": {
            key: result[key]
            for key in ("projectId", "resultId", "inputSnapshotId", "scope", "parametersHash")
        }
        | {"order": "ordinal+rowId:asc"},
        "rows": [{"rowId": uid(40 + ordinal), "ordinal": 0, "cells": ["unit-only payload"]}],
        "nextCursor": None,
    }
    assert CONTRACT.validate("result", result)
    assert CONTRACT.validate("job", job)
    assert CONTRACT.validate("result_result.page", page)
    slot = StageSlot(
        "open-query" if ordinal == 0 else "closed-query",
        ordinal * 2 + 1,
        ordinal * 2,
        version,
        snapshot,
        result["inputProjectRevision"],
        {key: deepcopy(result[key]) for key in SIGNATURE},
        "query.execute",
        historical,
    )
    stored = StoredStage(
        "unit-plan",
        1,
        replace(CONTEXT, input_version=version),
        1,
        H0,
        slot.stage_id,
        slot.ledger_ordinal,
        uid(60 + ordinal),
        job,
        result,
        (FetchedPage(None, page),),
    )
    return slot, stored


class SyntheticReader:
    """Unit-only owner; no production database, capability or ledger implementation."""

    def __init__(self):
        first, a = result_stage(0, H1, "open-input", True)
        last, b = result_stage(1, H2, "closed-input", False)
        self.binding = StagePlan("unit-plan", 1, CONTEXT, 1, "root-input", H0, H2, (first, last))
        self.records = {a.result["resultId"]: a, b.result["resultId"]: b}
        self.completions = {}
        for slot, stored in [(first, a), (last, b)]:
            original = deepcopy(stored.result)
            original.update(state="current", staleReason=[], historicalSelectionRequired=False)
            self.completions[stored.completion_receipt_id] = StageCompletion(
                stored.completion_receipt_id,
                stored.plan_id,
                stored.plan_version,
                stored.context,
                stored.attempt_epoch,
                stored.root_snapshot_id,
                stored.stage_id,
                slot.input_ledger_ordinal,
                slot.ledger_ordinal,
                original,
            )

        self.refs = (
            StageRef(first.stage_id, a.result["resultId"]),
            StageRef(last.stage_id, b.result["resultId"]),
        )
        self.edges = {(H0, H1), (H0, H2), (H1, H2)}
        self.after_read = lambda: None

    @contextmanager
    def view(self, _context):
        yield self
        self.after_read()

    def plan(self, _context):
        return self.binding

    def current_plan(self, _context):
        return self.binding

    def result(self, result_id):
        return self.records.get(result_id)

    def completion(self, receipt_id):
        return self.completions.get(receipt_id)

    def ancestor(self, _project, before, after):
        return before == after or (before, after) in self.edges

    def mutate(self, function, index=0):
        ref = self.refs[index]
        self.records[ref.result_id] = function(deepcopy(self.records[ref.result_id]))


def rejects(reader, reason, refs=None):
    with pytest.raises(StageBindingError, match=reason):
        bind_stages(reader, CONTEXT, refs if refs is not None else reader.refs)


def test_historical_open_and_current_closed_keep_actual_versions_not_terminal_relabels():
    reader = SyntheticReader()
    receipt = bind_stages(reader, CONTEXT, reader.refs)
    assert [s.context.input_version for s in receipt.stages] == ["open-input", "closed-input"]
    assert [s.result["inputSnapshotId"] for s in receipt.stages] == [H1, H2]
    assert [s.result["state"] for s in receipt.stages] == ["historical", "current"]
    assert not hasattr(receipt, "operation_complete")
    assert not hasattr(receipt, "independent_transfer_success")
    # A binding receipt is not a domain oracle: wrong payload stays wrong for its later comparator.
    assert receipt.stages[0].rows[0]["cells"] == ["unit-only payload"]
    assert receipt.stages[0].rows[0]["cells"] != ["expected A01"]
    receipt.stages[0].result["definitionId"] = "caller mutation"
    assert reader.records[reader.refs[0].result_id].result["definitionId"] == "Q1"


@pytest.mark.parametrize(
    "field,value",
    [
        ("project_id", uid(99)),
        ("task_id", "quality"),
        ("attempt_id", "old-attempt"),
        ("input_version", "closed-input"),
    ],
)
def test_cannot_relabel_stage_to_wrong_attempt_or_terminal_input(field, value):
    reader = SyntheticReader()
    reader.mutate(lambda s: replace(s, context=replace(s.context, **{field: value})))
    rejects(reader, "persisted-stage-binding-mismatch")


@pytest.mark.parametrize(
    "field,value",
    [
        ("plan_id", "other-plan"),
        ("plan_version", 2),
        ("attempt_epoch", 2),
        ("root_snapshot_id", "f" * 64),
        ("stage_id", "closed-query"),
        ("ledger_ordinal", 2),
    ],
)
def test_result_must_have_actual_persisted_stage_ledger_join(field, value):
    reader = SyntheticReader()
    reader.mutate(lambda s: replace(s, **{field: value}))
    rejects(reader, "persisted-stage-binding-mismatch")


@pytest.mark.parametrize(
    "key,value",
    [
        ("kind", "validation"),
        ("definitionId", "another-query"),
        ("scope", "scenario"),
        ("parametersHash", "f" * 64),
        ("dependencyVector", {"facts:asserted": 2}),
        ("definitionSetDigests", {}),
        (
            "implementation",
            {
                "executionSemanticsVersion": "other",
                "engineVersion": "0.1.0",
                "dependencyLockHash": "a" * 64,
            },
        ),
        ("inputSnapshotId", H2),
        ("inputProjectRevision", 9),
    ],
)
def test_same_snapshot_other_query_definition_scope_parameters_or_versions_are_rejected(key, value):
    reader = SyntheticReader()

    def wrong(stored):
        stored.result[key] = value
        if key == "inputSnapshotId":
            stored.job["inputSnapshotId"] = value
            stored.job["input"]["inputSnapshotId"] = value
            stored.job["resultRef"]["inputSnapshotId"] = value
        return stored

    reader.mutate(wrong)
    rejects(reader, "result-input-or-selection-mismatch")


@pytest.mark.parametrize("state", ["queued", "running", "cancelling", "failed", "cancelled"])
def test_result_exists_but_job_not_succeeded_cannot_bind(state):
    reader = SyntheticReader()

    # Use genuine canonical negative jobs where available; malformed variants also fail closed.
    def wrong(stored):
        template = next(
            c["value"]
            for c in FIXTURES
            if c["schema"] == "job" and c["valid"] and c["value"]["state"] == state
        )
        for key in ["state", "stateVersion", "resultRef", "error", "updatedAtMs", "finishedAtMs"]:
            stored.job[key] = deepcopy(template[key])
        assert CONTRACT.validate("job", stored.job)
        return stored

    reader.mutate(wrong)
    with pytest.raises(StageBindingError):
        bind_stages(reader, CONTEXT, reader.refs)


@pytest.mark.parametrize(
    "change",
    ["wrong-job", "wrong-project", "wrong-result-ref", "wrong-job-input", "wrong-capability"],
)
def test_actual_job_and_result_must_match(change):
    reader = SyntheticReader()

    def wrong(s):
        if change == "wrong-job":
            s.job["jobId"] = uid(99)
        elif change == "wrong-project":
            s.job["projectId"] = uid(99)
        elif change == "wrong-result-ref":
            s.job["resultRef"]["resultId"] = uid(99)
        elif change == "wrong-capability":
            s.job["capability"] = "validation.execute"
            assert CONTRACT.validate("job", s.job)
        else:
            s.job["input"]["definitionId"] = "wrong"
        return s

    reader.mutate(wrong)
    with pytest.raises(StageBindingError):
        bind_stages(reader, CONTEXT, reader.refs)


@pytest.mark.parametrize("change", ["evicted", "historical-terminal", "stale-terminal"])
def test_history_is_explicit_not_a_way_to_rename_stale_or_current(change):
    reader = SyntheticReader()

    def wrong(s):
        if change == "stale-terminal":
            s.result["state"] = "stale"
            s.result["staleReason"] = [
                {"code": "FACTS_CHANGED", "dependency": "facts:asserted", "before": 1, "after": 2}
            ]
            s.result["historicalSelectionRequired"] = False
        elif change == "evicted":
            s.result["payloadStatus"] = "evicted"
        elif change == "historical-terminal":
            s.result["state"] = "historical"
            s.result["historicalSelectionRequired"] = True
        else:
            s.result["state"] = "current"
            s.result["historicalSelectionRequired"] = False
        assert CONTRACT.validate("result", s.result)
        return s

    reader.mutate(wrong, 1 if change != "evicted" else 0)
    rejects(
        reader,
        "stage-payload-unavailable" if change == "evicted" else "unavailable-or-wrong-history",
    )


@pytest.mark.parametrize(
    "change",
    ["missing", "wrong-binding", "missing-last", "wrong-cursor", "duplicate-row", "reordered-row"],
)
def test_full_canonical_page_chain_is_required(change):
    reader = SyntheticReader()

    def wrong(s):
        if change == "missing":
            return replace(s, pages=())
        page = s.pages[0].response
        if change == "wrong-binding":
            page["binding"]["inputSnapshotId"] = H2
        elif change == "missing-last":
            page["nextCursor"] = uid(80)
        elif change == "wrong-cursor":
            return replace(s, pages=(FetchedPage(uid(80), page),))
        elif change == "duplicate-row":
            page["rows"].append(deepcopy(page["rows"][0]))
        else:
            row = deepcopy(page["rows"][0])
            row.update(rowId=uid(80), ordinal=1)
            page["rows"].insert(0, row)
        return s

    reader.mutate(wrong)
    with pytest.raises(StageBindingError):
        bind_stages(reader, CONTEXT, reader.refs)


def test_complete_multiple_pages_keep_actual_row_order_and_empty_terminal_results():
    reader = SyntheticReader()

    def pages(s):
        first = s.pages[0].response
        first["nextCursor"] = uid(80)
        second = deepcopy(first)
        second["nextCursor"] = None
        second["rows"][0].update(rowId=uid(81), ordinal=1)
        return replace(s, pages=(FetchedPage(None, first), FetchedPage(uid(80), second)))

    reader.mutate(pages)
    reader.mutate(
        lambda s: replace(s, pages=(FetchedPage(None, s.pages[0].response | {"rows": []}),)), 1
    )
    receipt = bind_stages(reader, CONTEXT, reader.refs)
    assert [row["ordinal"] for row in receipt.stages[0].rows] == [0, 1]
    assert receipt.stages[1].rows == ()


@pytest.mark.parametrize(
    "change", ["missing-stage", "unknown-stage", "reordered", "duplicate-result", "missing-result"]
)
def test_exact_stage_refs_cannot_be_missing_repeated_or_reordered(change):
    reader = SyntheticReader()
    refs = reader.refs
    if change == "missing-stage":
        refs = refs[:1]
    elif change == "unknown-stage":
        refs = (replace(refs[0], stage_id="unknown"), refs[1])
    elif change == "reordered":
        refs = refs[::-1]
    elif change == "duplicate-result":
        refs = (refs[0], replace(refs[1], result_id=refs[0].result_id))
    else:
        refs = (replace(refs[0], result_id=uid(99)), refs[1])
    with pytest.raises(StageBindingError):
        bind_stages(reader, CONTEXT, refs)


def test_ancestry_not_project_revision_numbers_rejects_sibling_branch_mix():
    reader = SyntheticReader()
    reader.edges.remove((H1, H2))
    rejects(reader, "stage-lineage-mismatch")


def test_same_snapshot_requires_explicit_trusted_plan_permission():
    reader = SyntheticReader()
    reader.binding = replace(reader.binding, root_snapshot_id=H1)
    for identity, stored in reader.records.items():
        reader.records[identity] = replace(stored, root_snapshot_id=H1)
    for identity, completed in reader.completions.items():
        reader.completions[identity] = replace(completed, root_snapshot_id=H1)
    rejects(reader, "stage-lineage-mismatch")
    first, last = reader.binding.slots
    reader.binding = replace(reader.binding, slots=(replace(first, allow_same_snapshot=True), last))
    assert bind_stages(reader, CONTEXT, reader.refs).plan.root_snapshot_id == H1


def test_terminal_drift_during_read_or_after_receipt_requires_new_validation():
    reader = SyntheticReader()
    reader.after_read = lambda: setattr(reader, "binding", replace(reader.binding, attempt_epoch=2))
    rejects(reader, "attempt-or-terminal-changed")
    reader = SyntheticReader()
    receipt = bind_stages(reader, CONTEXT, reader.refs)
    reader.binding = replace(reader.binding, context=replace(CONTEXT, input_version="later"))
    with pytest.raises(StageBindingError):
        require_current(reader, receipt)


@pytest.mark.parametrize(
    "change", ["no-plan", "wrong-terminal", "duplicate-slots", "wrong-ledger-order"]
)
def test_trusted_plan_itself_must_be_complete_and_unambiguous(change):
    reader = SyntheticReader()
    first, last = reader.binding.slots
    if change == "no-plan":
        reader.binding = None
    elif change == "wrong-terminal":
        reader.binding = replace(reader.binding, terminal_snapshot_id=H1)
    elif change == "duplicate-slots":
        reader.binding = replace(reader.binding, slots=(first, first))
    else:
        reader.binding = replace(reader.binding, slots=(first, replace(last, ledger_ordinal=0)))
    with pytest.raises(StageBindingError):
        bind_stages(reader, CONTEXT, reader.refs)


@pytest.mark.parametrize("field", ["plan_version", "attempt_epoch", "ledger_ordinal"])
def test_bool_cannot_alias_integer_ledger_bindings(field):
    reader = SyntheticReader()
    reader.mutate(lambda s: replace(s, **{field: True}))
    rejects(reader, "persisted-stage-binding-mismatch")


def test_current_plan_drift_uses_strict_json_values_not_python_numeric_aliases():
    reader = SyntheticReader()
    receipt = bind_stages(reader, CONTEXT, reader.refs)
    reader.binding = replace(reader.binding, attempt_epoch=True)
    with pytest.raises(StageBindingError):
        require_current(reader, receipt)


def validation_reader(reader):
    ctx = replace(CONTEXT, task_id="quality", input_version="repaired-input")
    slots = []
    refs = []
    for i, ref in enumerate(reader.refs):
        stored = reader.records[ref.result_id]
        slot = reader.binding.slots[i]
        stage_id = "name-removed" if i == 0 else "name-repaired"
        version = "missing-name-input" if i == 0 else "repaired-input"
        context = replace(ctx, input_version=version)
        selected = {
            "kind": "validation",
            "definitionId": "name-required",
            "parametersHash": "c" * 64,
            "dependencyVector": {"facts:asserted": 1, "constraint:name-required": 1},
            "definitionSetDigests": {"ontology": "a" * 64, "constraint": "b" * 64},
        }
        stored.result.update(deepcopy(selected))
        stored.job["capability"] = "validation.execute"
        stored.job.update({k: deepcopy(v) for k, v in selected.items() if k in stored.job})
        stored.job["input"].update(definitionId="name-required", parametersHash="c" * 64)
        page = stored.pages[0].response
        page["binding"]["parametersHash"] = "c" * 64
        page["rows"] = (
            [{"rowId": uid(90), "ordinal": 0, "cells": ["003", "name-required", "minCount"]}]
            if i == 0
            else []
        )
        reader.records[ref.result_id] = replace(stored, context=context, stage_id=stage_id)
        completion = reader.completions[stored.completion_receipt_id]
        completion.result.update(deepcopy(selected))
        reader.completions[stored.completion_receipt_id] = replace(
            completion, context=context, stage_id=stage_id
        )
        slots.append(
            replace(
                slot,
                stage_id=stage_id,
                input_version=version,
                expected_capability="validation.execute",
                expected_signature={k: deepcopy(stored.result[k]) for k in SIGNATURE},
            )
        )
        refs.append(replace(ref, stage_id=stage_id))
        assert CONTRACT.validate("job", stored.job)
        assert CONTRACT.validate("result", stored.result)
    reader.binding = replace(reader.binding, context=ctx, slots=tuple(slots))
    reader.refs = tuple(refs)
    return ctx


@pytest.mark.parametrize("task", ["query", "quality"])
def test_explicit_prior_completion_preserves_actual_stale_metadata(task):
    reader = SyntheticReader()
    ctx = validation_reader(reader) if task == "quality" else CONTEXT

    def stale(s):
        s.result.update(
            state="stale",
            historicalSelectionRequired=True,
            staleReason=[
                {"code": "FACTS_CHANGED", "dependency": "facts:asserted", "before": 1, "after": 2}
            ],
        )
        assert CONTRACT.validate("result", s.result)
        return s

    reader.mutate(stale)
    receipt = bind_stages(reader, ctx, reader.refs)
    assert receipt.stages[0].result["state"] == "stale"
    assert receipt.stages[0].completion.result["state"] == "current"
    assert receipt.stages[-1].result["state"] == "current"


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "wrong-stage",
        "posthoc-order",
        "wrong-input-order",
        "wrong-attempt",
        "stale-at-completion",
        "changed-creation-time",
        "wrong-result-id",
    ],
)
def test_completion_is_an_owner_join_not_a_reconstructed_current_label(change):
    reader = SyntheticReader()
    key = reader.records[reader.refs[0].result_id].completion_receipt_id
    c = reader.completions[key]
    if change == "missing":
        del reader.completions[key]
    elif change == "wrong-stage":
        reader.completions[key] = replace(c, stage_id="closed-query")
    elif change == "posthoc-order":
        reader.completions[key] = replace(c, ledger_ordinal=9)
    elif change == "wrong-input-order":
        reader.completions[key] = replace(c, input_ledger_ordinal=9)
    elif change == "wrong-attempt":
        reader.completions[key] = replace(c, context=replace(c.context, attempt_id="other"))
    elif change == "stale-at-completion":
        c.result.update(
            state="stale",
            historicalSelectionRequired=True,
            staleReason=[
                {"code": "FACTS_CHANGED", "dependency": "facts:asserted", "before": 1, "after": 2}
            ],
        )
    elif change == "changed-creation-time":
        c.result["createdAtMs"] += 1
    else:
        c.result["resultId"] = uid(99)
    with pytest.raises(StageBindingError):
        bind_stages(reader, CONTEXT, reader.refs)


def test_completion_receipt_does_not_replace_evicted_payload_or_missing_stage_ledger():
    reader = SyntheticReader()
    reader.records.clear()
    rejects(reader, "stage-result-unavailable")
    reader = SyntheticReader()

    def evicted(s):
        s.result["payloadStatus"] = "evicted"
        return s

    reader.mutate(evicted)
    rejects(reader, "stage-payload-unavailable")


@pytest.mark.parametrize("before_cells", [["A01"], ["003", "name-required"]])
def test_real_i04_result_stale_after_fact_edit_retains_prior_binding(tmp_path, before_cells):
    # Actual JobStore/read publication/paging/invalidation, with an explicitly synthetic
    # learning ledger. test.read echoes rows; this does not execute SPARQL or SHACL.
    from ontolearn_engine.job_store import JobStore
    from ontolearn_engine.storage import digest
    from test_job_store import page_binding, read_result, row

    store = JobStore(tmp_path / "stage.sqlite", contract=CONTRACT)
    try:
        store.create_project("stage-probe")
        store.project = store.public_project("stage-probe")
        triple = {"subject": "urn:stage:A01", "predicate": "urn:stage:status", "object": '"Open"'}
        fact = triple | {"id": digest(list(triple.values()))}
        store.commit("stage-probe", 0, "seed", "seed-job", manual=[fact])
        original = read_result(store, [row(0, before_cells)])
        assert original["state"] == "current"
        old_snapshot = original["inputSnapshotId"]
        store.commit("stage-probe", 1, "close", "close-job", edits={fact["id"]: '"Closed"'})
        marker = store.marker("stage-probe", "close")
        current = read_result(store, [])
        new_snapshot = current["inputSnapshotId"]
        assert (
            marker["before_snapshot"] == old_snapshot and marker["after_snapshot"] == new_snapshot
        )
        actual_prior = store.result_get(store.project, original["resultId"])
        assert actual_prior["state"] == "stale" and actual_prior["staleReason"]
        ctx = Context(store.project, "stage-infrastructure-probe", "unit-attempt", new_snapshot)
        reader = SyntheticReader()
        slots = []
        records = {}
        completions = {}
        refs = []
        for i, (actual, completed) in enumerate([(actual_prior, original), (current, current)]):
            stage_id = "before-edit" if i == 0 else "after-edit"
            slot = StageSlot(
                stage_id,
                i * 2 + 1,
                i * 2,
                actual["inputSnapshotId"],
                actual["inputSnapshotId"],
                actual["inputProjectRevision"],
                {k: deepcopy(actual[k]) for k in SIGNATURE},
                "test.read",
                i == 0,
                i == 0,
            )
            slots.append(slot)
            stage_ctx = replace(ctx, input_version=actual["inputSnapshotId"])
            receipt_id = uid(100 + i)
            completion = StageCompletion(
                receipt_id,
                "infra-plan",
                1,
                stage_ctx,
                1,
                old_snapshot,
                stage_id,
                slot.input_ledger_ordinal,
                slot.ledger_ordinal,
                deepcopy(completed),
            )
            page = store.result_page(page_binding(actual), 200, None)
            stored = StoredStage(
                "infra-plan",
                1,
                stage_ctx,
                1,
                old_snapshot,
                stage_id,
                slot.ledger_ordinal,
                receipt_id,
                store.get_job(store.project, actual["jobId"]),
                actual,
                (FetchedPage(None, page),),
            )
            records[actual["resultId"]] = stored
            completions[receipt_id] = completion
            refs.append(StageRef(stage_id, actual["resultId"]))
        reader.binding = StagePlan(
            "infra-plan", 1, ctx, 1, old_snapshot, old_snapshot, new_snapshot, tuple(slots)
        )
        reader.records = records
        reader.completions = completions
        reader.edges = {(old_snapshot, new_snapshot)}
        reader.current_plan = lambda _: (
            reader.binding
            if store.project_get(store.project)["inputSnapshotId"] == new_snapshot
            else None
        )
        receipt = bind_stages(reader, ctx, tuple(refs))
        assert receipt.stages[0].result == actual_prior
        assert receipt.stages[0].completion.result == original
        assert [r["cells"] for r in receipt.stages[0].rows] == [before_cells]
        assert receipt.stages[1].rows == ()
        # The canonical record has not been renamed or rewritten by the binder.
        assert store.result_get(store.project, original["resultId"]) == actual_prior
        store.commit("stage-probe", 2, "later", "later-job", edits={fact["id"]: '"Open"'})
        with pytest.raises(StageBindingError, match="attempt-or-terminal-changed"):
            require_current(reader, receipt)
    finally:
        store.close()


@pytest.mark.parametrize("field", ["root_input_version", "plan_id"])
@pytest.mark.parametrize("value", ["", "  ", 1, True, None])
def test_plan_requires_explicit_text_identity_and_root_version(field, value):
    reader = SyntheticReader()
    reader.binding = replace(reader.binding, **{field: value})
    rejects(reader, "invalid-plan-identity")


def test_validation_stage_does_not_accept_same_snapshot_query_result():
    reader = SyntheticReader()
    ctx = validation_reader(reader)
    stored = reader.records[reader.refs[0].result_id]
    stored.result.update(kind="query", definitionId="Q1")
    stored.job["capability"] = "query.execute"
    stored.job["input"]["definitionId"] = "Q1"
    assert CONTRACT.validate("job", stored.job)
    assert CONTRACT.validate("result", stored.result)
    with pytest.raises(
        StageBindingError, match="result-input-or-selection-mismatch|result-job-mismatch"
    ):
        bind_stages(reader, ctx, reader.refs)
