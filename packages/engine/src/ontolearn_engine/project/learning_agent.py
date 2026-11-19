"""Main-process-only ``project.agent.before_commit`` internal service.

One outer Store transaction performs the whole contract: idempotent replay of
the same operationId, the domainRevision CAS guard, a real recoverable
``before-agent`` checkpoint through the ordinary application ledger, and -
when full assistance is requested - the *pending* PRD §11.2 learning-ledger
marking stored in the same receipt envelope. The assistance rows themselves
are only written when the linked ChangeSet actually commits
(``apply_pending_assistance`` runs inside that commit transaction), so a
failed, cancelled or superseded ChangeSet never pollutes learning attempts.
The public ``project.checkpoint.create`` wire method keeps minting ``manual``
checkpoints only; this path is registered for the desktop main process and has
no renderer, preload or ordinary read entry.
"""

import hashlib
import json
from copy import deepcopy
from uuid import uuid4

from ontolearn_engine.project.ontology_turtle import resolve_active
from ontolearn_engine.storage import canonical, digest

METHODS = frozenset({"project.agent.before_commit"})
BEFORE_AGENT_EVENT_KIND = "agent.full-assistance"
RECEIPT_VERSION = "agentBeforeCommitReceiptVersion"
PENDING_KEY = "pendingAssistance"
CHANGE = {"type": "checkpoint.create", "reason": "before-agent"}


def derive_before_commit_op(operation_id):
    """Deterministic before-agent operation id for one ChangeSet operation.

    Byte-identical to ``deriveBeforeCommitOp`` in
    ``apps/desktop/src/main/agent/host-composition.ts``: SHA-256 of
    ``"before-agent:" + operationId`` laid out as an 8-4-4-4-12 UUID with the
    version nibble pinned to '4' and the variant nibble to '8'.
    """
    hexdigest = hashlib.sha256(("before-agent:" + operation_id).encode("utf-8")).hexdigest()
    return (
        f"{hexdigest[0:8]}-{hexdigest[8:12]}-4{hexdigest[13:16]}"
        f"-8{hexdigest[17:20]}-{hexdigest[20:32]}"
    )


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


def _claim_change(store, project, operation):
    row = store._db.execute(
        "SELECT kind,project,context FROM operation_claims WHERE operation=?", (operation,)
    ).fetchone()
    if row is None or row["kind"] != "application" or row["project"] != project:
        return None
    try:
        context = json.loads(row["context"]) if row["context"] else None
    except (ValueError, TypeError):
        return None
    change = context.get("request", {}).get("change") if isinstance(context, dict) else None
    return change if isinstance(change, dict) else None


def _persisted_result(store, project, operation, request_hash):
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (operation, project)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    try:
        envelope = json.loads(row[0])
        result = envelope["result"]
    except (ValueError, TypeError, KeyError):
        fault("INVALID_STATE")
    if (
        not isinstance(envelope, dict)
        or envelope.get(RECEIPT_VERSION) != 1
        or envelope.get("requestHash") != request_hash
        or not isinstance(result, dict)
        or result.get("operationId") != operation
        or result.get("projectId") != project
    ):
        fault("IDENTITY_CONFLICT")
    return result


def _full_assistance_targets(store, project, host, task_ids):
    """Live, not-yet-complete attempts for an explicit task id list only.

    A missing ``taskIds`` never scans the whole course (B05): without explicit
    targets there is nothing to attribute. Order is preserved and duplicates
    collapse to their first occurrence.
    """
    from ontolearn_engine.project import format3, learning_ledger

    if task_ids is None:
        return []
    service = host.bare_service()
    for task_id in task_ids:
        if task_id not in service.tasks:
            fault("INVALID_REQUEST", field="params")
    records = learning_ledger._records(format3.application_state(store, store._project(project)))
    targets, seen = [], set()
    for task_id in task_ids:
        if task_id in seen:
            continue
        seen.add(task_id)
        record = learning_ledger._current(records, task_id)
        if record is None or record["withdrawn"] or record["payload"]["operationComplete"]:
            continue
        targets.append(record)
    return targets


def before_commit(store, project, params, host, origin):
    operation = params["operationId"]
    label = params["label"]
    base_revision = params["baseRevision"]
    task_ids = params.get("taskIds")
    request = {
        "agentBeforeCommitVersion": 1,
        "projectId": project,
        "operationId": operation,
        "baseRevision": base_revision,
        "recordFullAssistance": params["recordFullAssistance"],
        "taskIds": task_ids,
        "label": label,
    }
    request_hash = digest(request)
    internal = resolve_active(store, project)
    with store._transaction():
        if store.has_operation_claim(operation):
            change = _claim_change(store, project, operation)
            if (
                change is None
                or change.get("type") != CHANGE["type"]
                or change.get("reason") != CHANGE["reason"]
            ):
                fault("IDENTITY_CONFLICT")
            result = _persisted_result(store, project, operation, request_hash)
            store._valid("result_project.agent.before_commit", result)
            return result
        if store._occupied_operation_evidence(operation):
            fault("IDENTITY_CONFLICT")
        revision = store.revision(internal)
        if revision != base_revision:
            fault("REVISION_CONFLICT", expected=base_revision, actual=revision)
        receipt = store.apply_application(
            project,
            operation,
            {**CHANGE, "label": label},
            actor=origin["hostClientId"],
            permission="write",
        )
        # Full assistance is only *staged* here, in the same job_details
        # envelope: the app_learning rows are written by apply_pending_assistance
        # inside the linked ChangeSet's commit transaction, so an uncommitted,
        # failed or superseded ChangeSet leaves every attempt untouched (B05).
        pending = None
        if params["recordFullAssistance"]:
            targets = _full_assistance_targets(store, project, host, task_ids)
            if targets:
                pending = {
                    "baseRevision": base_revision,
                    "origin": {"hostClientId": origin["hostClientId"]},
                    "targets": [
                        {"taskId": record["payload"]["taskId"], "attempt": record["attempt"]}
                        for record in targets
                    ],
                    "applied": False,
                }
        result = {
            "agentBeforeCommitVersion": 1,
            "projectId": project,
            "operationId": operation,
            "checkpointRef": receipt["afterCheckpointRef"],
            "reason": "before-agent",
            "domainRevision": base_revision,
            "assistanceUpdatedTaskIds": [],
        }
        store._valid("result_project.agent.before_commit", result)
        envelope = {RECEIPT_VERSION: 1, "requestHash": request_hash, "result": result}
        if pending is not None:
            envelope[PENDING_KEY] = pending
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (operation, project, canonical(envelope)),
        )
        return result


def apply_pending_assistance(store, project, changeset_op, base_revision):
    """Apply the staged full-assistance marking for one committed ChangeSet.

    Runs inside the caller's ChangeSet commit transaction (same live-or-die
    boundary as the domain marker). No record, an already-applied staging, or
    a baseRevision mismatch means there is nothing to do - never an error and
    never a marking. job_details is insert-only evidence, so the applied flag
    is a separate immutable marker row instead of an envelope update.
    """
    from ontolearn_engine.project import format3, learning_ledger

    before_op = derive_before_commit_op(changeset_op)
    applied_id = before_op + ":agent-assistance-applied"
    if (
        store._db.execute(
            "SELECT 1 FROM job_details WHERE id=? AND project=?", (applied_id, project)
        ).fetchone()
        is not None
    ):
        return
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (before_op, project)
    ).fetchone()
    if row is None:
        return
    try:
        envelope = json.loads(row[0])
    except (ValueError, TypeError):
        return
    if not isinstance(envelope, dict) or envelope.get(RECEIPT_VERSION) != 1:
        return
    pending = envelope.get(PENDING_KEY)
    if not isinstance(pending, dict) or pending.get("applied") is True:
        return
    if pending.get("baseRevision") != base_revision:
        return
    origin = pending.get("origin")
    if not isinstance(origin, dict) or not isinstance(origin.get("hostClientId"), str):
        return
    targets = pending.get("targets")
    if not isinstance(targets, list) or any(
        not isinstance(target, dict)
        or not isinstance(target.get("taskId"), str)
        or not isinstance(target.get("attempt"), str)
        for target in targets
    ):
        return
    records = learning_ledger._records(format3.application_state(store, store._project(project)))
    live = {record["attempt"]: record for record in records if not record["withdrawn"]}
    inner_operation = changeset_op + ":agent-assistance"
    for target in targets:
        # Re-check each staged target against the current live ledger: only
        # the exact (taskId, attempt) pair that is still present, not
        # withdrawn and not completed gets marked.
        record = live.get(target["attempt"])
        if record is None or record["payload"]["taskId"] != target["taskId"]:
            continue
        if record["withdrawn"] or record["payload"]["operationComplete"]:
            continue
        payload = deepcopy(record["payload"])
        payload.update(
            assistance="agent-full-assistance",
            operationComplete=False,
            independentTransferSuccess=False,
            checkStatus="rerun-required",
            evidenceIds=[],
        )
        payload["lastOperationId"] = inner_operation
        learning_ledger._write_record(
            store,
            project,
            str(uuid4()),
            record,
            payload,
            {
                "eventId": str(uuid4()),
                "payload": {
                    "kind": BEFORE_AGENT_EVENT_KIND,
                    "taskId": payload["taskId"],
                    "operationId": changeset_op,
                },
            },
            origin,
        )
    store._db.execute(
        "INSERT INTO job_details VALUES(?,?,?)",
        (
            applied_id,
            project,
            canonical({"kind": "agent-assistance-applied", "operationId": changeset_op}),
        ),
    )


def dispatch(store, method, params, host, origin):
    store._valid("params_project.agent.before_commit", params)
    return before_commit(store, params["projectId"], params, host, origin)
