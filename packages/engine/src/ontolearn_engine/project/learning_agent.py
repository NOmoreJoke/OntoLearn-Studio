"""Main-process-only ``project.agent.before_commit`` internal service.

One outer Store transaction performs the whole contract: idempotent replay of
the same operationId, the domainRevision CAS guard, a real recoverable
``before-agent`` checkpoint through the ordinary application ledger, and -
when full assistance is requested - the PRD §11.2 learning-ledger marking that
keeps ``independentTransferSuccess`` false for agent-completed work. The
public ``project.checkpoint.create`` wire method keeps minting ``manual``
checkpoints only; this path is registered for the desktop main process and has
no renderer, preload or ordinary read entry.
"""

import json
from copy import deepcopy
from uuid import uuid4

from ontolearn_engine.project.ontology_turtle import resolve_active
from ontolearn_engine.storage import canonical, digest

METHODS = frozenset({"project.agent.before_commit"})
BEFORE_AGENT_EVENT_KIND = "agent.full-assistance"
RECEIPT_VERSION = "agentBeforeCommitReceiptVersion"
CHANGE = {"type": "checkpoint.create", "reason": "before-agent"}


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
    """Current-epoch live, not-yet-complete attempts: explicit list or all tasks."""
    from ontolearn_engine.project import format3, learning_ledger

    service = host.bare_service()
    records = learning_ledger._records(format3.application_state(store, store._project(project)))
    scope = [task["id"] for task in service.course["tasks"]]
    if task_ids is not None:
        for task_id in task_ids:
            if task_id not in service.tasks:
                fault("INVALID_REQUEST", field="params")
        scope = task_ids
    targets = []
    for task_id in scope:
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
        updated = []
        if params["recordFullAssistance"]:
            from ontolearn_engine.project import learning_ledger

            for record in _full_assistance_targets(store, project, host, task_ids):
                payload = deepcopy(record["payload"])
                payload.update(
                    assistance="agent-full-assistance",
                    operationComplete=False,
                    independentTransferSuccess=False,
                    checkStatus="rerun-required",
                    evidenceIds=[],
                )
                inner = str(uuid4())
                payload["lastOperationId"] = operation + ":agent-assistance"
                learning_ledger._write_record(
                    store,
                    project,
                    inner,
                    record,
                    payload,
                    {
                        "eventId": str(uuid4()),
                        "payload": {
                            "kind": BEFORE_AGENT_EVENT_KIND,
                            "taskId": payload["taskId"],
                            "operationId": operation,
                        },
                    },
                    origin,
                )
                updated.append(payload["taskId"])
        result = {
            "agentBeforeCommitVersion": 1,
            "projectId": project,
            "operationId": operation,
            "checkpointRef": receipt["afterCheckpointRef"],
            "reason": "before-agent",
            "domainRevision": base_revision,
            "assistanceUpdatedTaskIds": updated,
        }
        store._valid("result_project.agent.before_commit", result)
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (
                operation,
                project,
                canonical({RECEIPT_VERSION: 1, "requestHash": request_hash, "result": result}),
            ),
        )
        return result


def dispatch(store, method, params, host, origin):
    store._valid("params_project.agent.before_commit", params)
    return before_commit(store, params["projectId"], params, host, origin)
