"""Main-process-only ``project.run.before_commit`` internal service (W4-A1).

The direct Stage 1 twin of ``project.agent.before_commit``: before an isolated
behavior/scenario run enters execution, the trusted host registers a durable
``before-run`` checkpoint through the ordinary application ledger. One outer
Store transaction performs the whole contract - idempotent replay of the same
``operationId`` bound to ``(projectId, domain, baseRevision, label)```, the
domainRevision CAS guard, and a real recoverable ``before-run`` checkpoint.
The public ``project.checkpoint.create`` wire method keeps minting ``manual``
checkpoints only (guarded by test_b1b_project_restore.py).
"""

import json

from ontolearn_engine.project.ontology_turtle import resolve_active
from ontolearn_engine.storage import canonical, digest

METHODS = frozenset({"project.run.before_commit"})
RECEIPT_VERSION = "runBeforeCommitReceiptVersion"
CHANGE = {"type": "checkpoint.create", "reason": "before-run"}
# The discriminating isolated-run domains share IsolatedRunScope (interface
# freeze §T07); they ride the request envelope, never the frozen checkpoint
# change shape (a checkpoint only freezes evidence, see applications.check_change).
DOMAINS = frozenset({"behavior", "scenario"})


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


def before_commit(store, project, params, origin):
    operation = params["operationId"]
    label = params["label"]
    base_revision = params["baseRevision"]
    domain = params["domain"]
    request = {
        "runBeforeCommitVersion": 1,
        "projectId": project,
        "operationId": operation,
        "domain": domain,
        "baseRevision": base_revision,
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
            # Replay reconciles by the exact original binding tuple; any
            # conflicting parameter reuse is a deterministic rejection.
            result = _persisted_result(store, project, operation, request_hash)
            store._valid("result_project.run.before_commit", result)
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
        cp = store.project_checkpoint(internal, receipt["afterCheckpointRef"])
        result = {
            "runBeforeCommitVersion": 1,
            "projectId": project,
            "operationId": operation,
            "checkpointRef": receipt["afterCheckpointRef"],
            "reason": "before-run",
            "domainRevision": cp["domainRevision"],
        }
        store._valid("result_project.run.before_commit", result)
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (
                operation,
                project,
                canonical({RECEIPT_VERSION: 1, "requestHash": request_hash, "result": result}),
            ),
        )
        return result


def lookup_receipt(store, project, operation, domain, base_revision):
    """W4-A2 read-only lookup: verify a persisted ``before-run`` receipt.

    ``project.behavior.run`` / ``project.scenario.run`` / ``project.scenario.resume``
    call this inside their own Store transaction before execution. The persisted
    ``requestHash`` pins ``{runBeforeCommitVersion, projectId, operationId, domain,
    baseRevision, label}``; the engine reconciles the host binding ``label: null``
    exactly. A missing receipt, a drifted tuple, a wrong isolated-run domain or a
    ``domainRevision`` that no longer equals the supplied base revision all fail
    closed deterministically. The persisted ``checkpointRef`` is returned verbatim;
    it is never minted or repaired here.
    """
    if domain not in DOMAINS:
        fault("IDENTITY_CONFLICT")
    expected = digest(
        {
            "runBeforeCommitVersion": 1,
            "projectId": project,
            "operationId": operation,
            "domain": domain,
            "baseRevision": base_revision,
            "label": None,
        }
    )
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (operation, project)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    try:
        envelope = json.loads(row[0])
        result = envelope["result"]
    except (ValueError, TypeError, KeyError, IndexError):
        fault("IDENTITY_CONFLICT")
    if (
        not isinstance(envelope, dict)
        or envelope.get(RECEIPT_VERSION) != 1
        or envelope.get("requestHash") != expected
        or not isinstance(result, dict)
        or result.get("runBeforeCommitVersion") != 1
        or result.get("projectId") != project
        or result.get("operationId") != operation
        or result.get("reason") != "before-run"
        or result.get("domainRevision") != base_revision
        or not isinstance(result.get("checkpointRef"), str)
        or not result["checkpointRef"]
    ):
        fault("IDENTITY_CONFLICT")
    return result["checkpointRef"]


def dispatch(store, method, params, origin):
    store._valid("params_project.run.before_commit", params)
    return before_commit(store, params["projectId"], params, origin)
