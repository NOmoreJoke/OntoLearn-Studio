"""Private, read-only staged evidence binding; no IPC or completion authority.

The T01/T00 owner supplies a consistent persisted view and trusted learning plan.
Canonical jobs/results/pages reuse the approved contract, never a parallel schema.
Domain payload comparison and durable assistance remain separate responsibilities.
"""

from contextlib import AbstractContextManager
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Protocol

from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical

from .service import Context

SIGNATURE = (
    "kind",
    "definitionId",
    "scope",
    "parametersHash",
    "dependencyVector",
    "definitionSetDigests",
    "implementation",
)


class StageBindingError(ValueError):
    """Private fixed reasons only; callers map through their approved error shell."""


@dataclass(frozen=True)
class StageSlot:
    stage_id: str
    ledger_ordinal: int
    input_ledger_ordinal: int
    input_version: str
    input_snapshot_id: str
    input_project_revision: int
    expected_signature: dict
    expected_capability: str
    historical_selection: bool
    allow_same_snapshot: bool = False


@dataclass(frozen=True)
class StagePlan:
    plan_id: str
    plan_version: int
    context: Context  # Aggregate terminal context; stages retain their actual input version.
    attempt_epoch: int
    root_input_version: str
    root_snapshot_id: str
    terminal_snapshot_id: str
    slots: tuple[StageSlot, ...]


@dataclass(frozen=True)
class FetchedPage:
    request_cursor: str | None
    response: dict


@dataclass(frozen=True)
class StoredStage:
    """Owner-joined ledger record, not metadata inferred from a domain result ID."""

    plan_id: str
    plan_version: int
    context: Context  # Actual stage input context, never relabelled to terminal.
    attempt_epoch: int
    root_snapshot_id: str
    stage_id: str
    ledger_ordinal: int
    completion_receipt_id: str
    job: dict
    result: dict
    pages: tuple[FetchedPage, ...]


@dataclass(frozen=True)
class StageCompletion:
    """Immutable owner ledger row captured when the stage really completed.

    Never reconstructed from today's stale result by the binding validator.
    """

    receipt_id: str
    plan_id: str
    plan_version: int
    context: Context
    attempt_epoch: int
    root_snapshot_id: str
    stage_id: str
    input_ledger_ordinal: int
    ledger_ordinal: int
    result: dict


@dataclass(frozen=True)
class StageRef:
    stage_id: str
    result_id: str


class EvidenceView(Protocol):
    def plan(self, context: Context) -> StagePlan | None: ...

    def result(self, result_id: str) -> StoredStage | None: ...

    def completion(self, receipt_id: str) -> StageCompletion | None: ...

    def ancestor(self, project_id: str, before_snapshot: str, after_snapshot: str) -> bool: ...


class StageReader(Protocol):
    def view(self, context: Context) -> AbstractContextManager[EvidenceView]: ...

    def current_plan(self, context: Context) -> StagePlan | None: ...


@dataclass(frozen=True)
class BoundStage:
    stage_id: str
    context: Context
    result: dict  # Current canonical metadata, including its actual stale state.
    completion: StageCompletion
    rows: tuple[dict, ...]


@dataclass(frozen=True)
class StageReceipt:
    """Binding verified only: intentionally contains no passed/completion flags."""

    plan: StagePlan
    stages: tuple[BoundStage, ...]


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise StageBindingError(reason)


def _safe_integer(value: object) -> bool:
    return type(value) is int and 0 <= value <= 9007199254740991


def _plan_valid(plan: StagePlan, context: Context) -> None:
    _require(plan.context == context, "attempt-context-mismatch")
    _require(
        isinstance(plan.plan_id, str)
        and bool(plan.plan_id.strip())
        and isinstance(plan.root_input_version, str)
        and bool(plan.root_input_version.strip())
        and _safe_integer(plan.plan_version)
        and _safe_integer(plan.attempt_epoch),
        "invalid-plan-identity",
    )
    _require(
        CONTRACT.validate("hash", plan.root_snapshot_id)
        and CONTRACT.validate("hash", plan.terminal_snapshot_id),
        "invalid-plan-snapshot",
    )
    _require(bool(plan.slots), "missing-stage-plan")
    _require(
        len({slot.stage_id for slot in plan.slots}) == len(plan.slots)
        and all(isinstance(slot.stage_id, str) and slot.stage_id for slot in plan.slots),
        "duplicate-or-empty-stage",
    )
    previous = -1
    for slot in plan.slots:
        _require(
            _safe_integer(slot.ledger_ordinal)
            and _safe_integer(slot.input_ledger_ordinal)
            and previous < slot.input_ledger_ordinal < slot.ledger_ordinal,
            "invalid-ledger-order",
        )
        previous = slot.ledger_ordinal
        _require(
            isinstance(slot.input_version, str)
            and bool(slot.input_version)
            and CONTRACT.validate("hash", slot.input_snapshot_id)
            and _safe_integer(slot.input_project_revision)
            and set(slot.expected_signature) == set(SIGNATURE)
            and slot.expected_capability in CONTRACT.REGISTRY["capabilities"]
            and type(slot.historical_selection) is bool
            and type(slot.allow_same_snapshot) is bool,
            "invalid-stage-plan",
        )
    terminal = plan.slots[-1]
    _require(
        terminal.input_version == context.input_version
        and terminal.input_snapshot_id == plan.terminal_snapshot_id
        and not terminal.historical_selection,
        "terminal-stage-mismatch",
    )


def _complete_rows(stage: StoredStage) -> tuple[dict, ...]:
    result = stage.result
    binding = {
        key: result[key]
        for key in ("projectId", "resultId", "inputSnapshotId", "scope", "parametersHash")
    } | {"order": "ordinal+rowId:asc"}
    _require(bool(stage.pages), "missing-payload-pages")
    expected_cursor = None
    cursors, row_ids = set(), set()
    rows = []
    previous_order = None
    for index, fetched in enumerate(stage.pages):
        page = fetched.response
        _require(CONTRACT.validate("result_result.page", page), "invalid-canonical-page")
        _require(
            fetched.request_cursor == expected_cursor and page["binding"] == binding,
            "page-binding-mismatch",
        )
        cursor = page["nextCursor"]
        _require((cursor is None) == (index == len(stage.pages) - 1), "incomplete-page-chain")
        _require(cursor is None or cursor not in cursors, "repeated-page-cursor")
        cursors.add(cursor)
        _require(cursor is None or bool(page["rows"]), "empty-continuation-page")
        for row in page["rows"]:
            order = (row["ordinal"], row["rowId"])
            _require(
                row["rowId"] not in row_ids and (previous_order is None or order > previous_order),
                "duplicate-or-reordered-row",
            )
            previous_order = order
            row_ids.add(row["rowId"])
            rows.append(deepcopy(row))
        expected_cursor = cursor
    return tuple(rows)


def _bind_stage(
    plan: StagePlan,
    slot: StageSlot,
    reference: StageRef,
    stored: StoredStage,
    completion: StageCompletion,
):
    actual_context = Context(
        plan.context.project_id, plan.context.task_id, plan.context.attempt_id, slot.input_version
    )
    _require(
        _safe_integer(stored.plan_version)
        and _safe_integer(stored.attempt_epoch)
        and _safe_integer(stored.ledger_ordinal)
        and stored.plan_id == plan.plan_id
        and stored.plan_version == plan.plan_version
        and stored.context == actual_context
        and stored.attempt_epoch == plan.attempt_epoch
        and stored.root_snapshot_id == plan.root_snapshot_id
        and stored.stage_id == slot.stage_id
        and stored.ledger_ordinal == slot.ledger_ordinal,
        "persisted-stage-binding-mismatch",
    )
    result, job = stored.result, stored.job
    _require(
        CONTRACT.validate("result", result) and CONTRACT.validate("job", job),
        "invalid-canonical-result-or-job",
    )
    _require(
        result["resultId"] == reference.result_id
        and result["projectId"] == plan.context.project_id
        and job["projectId"] == plan.context.project_id
        and result["jobId"] == job["jobId"]
        and job["state"] == "succeeded"
        and job["capability"] == slot.expected_capability
        and job["resultRef"]
        == {"resultId": result["resultId"], "inputSnapshotId": result["inputSnapshotId"]},
        "result-job-mismatch",
    )
    _require(
        result["inputSnapshotId"] == slot.input_snapshot_id
        and result["inputProjectRevision"] == slot.input_project_revision
        and all(
            canonical(result[key]) == canonical(slot.expected_signature[key]) for key in SIGNATURE
        ),
        "result-input-or-selection-mismatch",
    )
    _require(
        all(
            canonical(job[key]) == canonical(result[key])
            for key in (
                "inputSnapshotId",
                "scope",
                "parametersHash",
                "dependencyVector",
                "definitionSetDigests",
                "implementation",
            )
        )
        and job["input"]["definitionId"] == result["definitionId"],
        "result-job-input-mismatch",
    )
    _require(result["payloadStatus"] == "available", "stage-payload-unavailable")
    _require(
        CONTRACT.validate("id", completion.receipt_id)
        and completion.receipt_id == stored.completion_receipt_id
        and completion.plan_id == plan.plan_id
        and _safe_integer(completion.plan_version)
        and completion.plan_version == plan.plan_version
        and completion.context == actual_context
        and _safe_integer(completion.attempt_epoch)
        and completion.attempt_epoch == plan.attempt_epoch
        and completion.root_snapshot_id == plan.root_snapshot_id
        and completion.stage_id == slot.stage_id
        and _safe_integer(completion.input_ledger_ordinal)
        and completion.input_ledger_ordinal == slot.input_ledger_ordinal
        and _safe_integer(completion.ledger_ordinal)
        and completion.ledger_ordinal == slot.ledger_ordinal,
        "completion-ledger-mismatch",
    )
    original = completion.result
    _require(CONTRACT.validate("result", original), "invalid-completion-result")
    _require(
        original["state"] == "current"
        and original["staleReason"] == []
        and original["historicalSelectionRequired"] is False
        and original["payloadStatus"] == "available",
        "stage-not-current-at-completion",
    )
    mutable = {"state", "staleReason", "historicalSelectionRequired"}
    _require(
        canonical({k: v for k, v in result.items() if k not in mutable})
        == canonical({k: v for k, v in original.items() if k not in mutable}),
        "completion-result-core-mismatch",
    )
    _require(
        slot.historical_selection
        or (
            result["state"] == "current"
            and result["staleReason"] == []
            and result["historicalSelectionRequired"] is False
        ),
        "unavailable-or-wrong-history",
    )
    return BoundStage(
        slot.stage_id,
        stored.context,
        deepcopy(result),
        deepcopy(completion),
        _complete_rows(stored),
    )


def bind_stages(reader: StageReader, context: Context, refs: tuple[StageRef, ...]) -> StageReceipt:
    """Read trusted plan, verify persisted joins and page chain, then check for drift.

    The caller cannot submit the plan or edit result metadata. A future T01 writer
    must revalidate the receipt in its own CAS transaction before persisting a
    domain check/learning record; this function never grants write authority.
    """
    with reader.view(context) as view:
        source_plan = view.plan(context)
        _require(isinstance(source_plan, StagePlan), "stage-plan-unavailable")
        plan = deepcopy(source_plan)
        _plan_valid(plan, context)
        _require(
            tuple(ref.stage_id for ref in refs) == tuple(slot.stage_id for slot in plan.slots),
            "missing-unknown-or-reordered-stage",
        )
        _require(len({ref.result_id for ref in refs}) == len(refs), "reused-stage-result")
        bound = []
        previous_snapshot = plan.root_snapshot_id
        for slot, reference in zip(plan.slots, refs, strict=True):
            stored = view.result(reference.result_id)
            _require(isinstance(stored, StoredStage), "stage-result-unavailable")
            completion = view.completion(stored.completion_receipt_id)
            _require(isinstance(completion, StageCompletion), "stage-completion-unavailable")
            bound.append(_bind_stage(plan, slot, reference, stored, completion))
            _require(
                (previous_snapshot != slot.input_snapshot_id or slot.allow_same_snapshot)
                and view.ancestor(context.project_id, previous_snapshot, slot.input_snapshot_id)
                and view.ancestor(context.project_id, plan.root_snapshot_id, slot.input_snapshot_id)
                and view.ancestor(
                    context.project_id, slot.input_snapshot_id, plan.terminal_snapshot_id
                ),
                "stage-lineage-mismatch",
            )
            previous_snapshot = slot.input_snapshot_id
        receipt = StageReceipt(plan, tuple(bound))
    require_current(reader, receipt)
    return receipt


def require_current(reader: StageReader, receipt: StageReceipt) -> None:
    """Recheck immediately before use; the owner must make persistence atomic with this check."""
    current = reader.current_plan(receipt.plan.context)
    _require(isinstance(current, StagePlan), "attempt-or-terminal-changed")
    _plan_valid(current, receipt.plan.context)
    _require(
        canonical(asdict(current)) == canonical(asdict(receipt.plan)), "attempt-or-terminal-changed"
    )
