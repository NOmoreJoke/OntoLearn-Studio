"""Named whole-project checkpoint and restore services over the owned Store3.

No renderer DTO, second writer or lifecycle bypass: every mutation still goes
through the single Store transaction, the immutable mixed ledger and the
application claim/confirmation machinery in applications.py.
"""

import base64
import hashlib
import json

from ontolearn_engine.project import format3
from ontolearn_engine.project.applications import (
    hash_ref,
    uuid_ref,
)
from ontolearn_engine.project.domain_changesets import MAX_DOCUMENT, SEGMENT_BYTES
from ontolearn_engine.storage import Conflict, canonical, digest

METHODS = frozenset(
    {
        "project.checkpoint.list",
        "project.checkpoint.create",
        "project.restore.preview",
        "project.restore.page",
        "project.restore.confirm",
        "project.restore.apply",
        "project.restore.operation.get",
    }
)
PREVIEW_VERSION = "restorePreviewVersion"
RECEIPT_VERSION = "restoreConfirmationReceiptVersion"
CURSOR_KIND = "restore-checkpoint-list-v1"
COVERAGE = ["metadata", "drafts", "learningCurrent", "assistanceAudit"]
PRESERVED = [
    "historical-runs",
    "jobs-and-results",
    "assistance-audit",
    "operation-evidence",
    "checkpoints",
]
CHECKPOINT_REASONS = (
    "genesis",
    "manual",
    "before-run",
    "guided-stage",
    "before-agent",
    "restore",
    "operation",
)
MAX_LIST_PAGE = 50
PREVIEW_TTL_MS = 600000


def require(condition, category="state"):
    if not condition:
        raise Conflict("Invalid checkpoint request", category=category)


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


def _public(store, public):
    from ontolearn_engine.project.management import public_internal

    require(uuid_ref(public), "input")
    return public_internal(store, public)


def _active(store, internal):
    from ontolearn_engine.project.management import active

    active(store, internal)


def _change_type(store, project, operation):
    """Authoritative change identity from the immutable operation ledger."""
    row = store._db.execute(
        "SELECT kind FROM app_operations WHERE project=? AND operation=?", (project, operation)
    ).fetchone()
    if row is None:
        return None, None
    if row[0] in {"legacy-domain", "domain"}:
        return row[0], None
    from ontolearn_engine.project.project_lifecycle import creation_context

    creation = creation_context(store, project, operation)
    if creation is not None:
        return row[0], None
    from ontolearn_engine.project.applications import claim_context

    context = claim_context(store, project, operation)
    change = context["plan"]["change"]
    return row[0], change


def _reason(store, project, operation):
    """Map one ledger operation onto the fixed wire reason vocabulary."""
    if operation is None:
        return "genesis", None
    kind, change = _change_type(store, project, operation)
    if change is not None and change["type"] == "checkpoint.create":
        return change["reason"], change["label"]
    if change is not None and change["type"] == "project.restore":
        return "restore", None
    return "operation", None


def _item(store, public, internal, cp, current_ref):
    state = store._project_snapshot(cp["domainSnapshotRef"], internal)["state"]
    legacy = format3.history_coverage(store, internal)["legacyDomainOperations"]
    operation = None
    row = store._db.execute(
        "SELECT operation FROM app_operations WHERE project=? AND sequence=?",
        (internal, cp["operationSequence"]),
    ).fetchone()
    if row is not None:
        operation = row[0]
    elif cp["operationSequence"] != legacy:
        fault("STORAGE_FAILURE")
    reason, label = _reason(store, internal, operation)
    kind = None
    if operation is not None:
        row = store._db.execute(
            "SELECT kind FROM app_operations WHERE project=? AND operation=?",
            (internal, operation),
        ).fetchone()
        kind = row[0] if row is not None else None
    application = cp["application"]
    return {
        "checkpointRef": digest(cp),
        "operationSequence": cp["operationSequence"],
        "domainRevision": cp["domainRevision"],
        "domainSnapshotRef": cp["domainSnapshotRef"],
        "metadataVersion": application["metadataVersion"],
        "reason": reason,
        "label": label,
        "operationId": operation,
        "operationKind": kind,
        "counts": {
            "definitions": len(state["definitions"]),
            "facts": len(state["facts"]),
            "drafts": len(application["drafts"]),
            "learning": len(application["learningCurrent"]),
        },
        "coverage": list(COVERAGE),
        "preserved": list(PRESERVED),
        "isCurrent": digest(cp) == current_ref,
    }


def _list(store, public, params, host):
    internal = _public(store, public)
    _active(store, internal)
    cursor = params["cursor"]
    page_size = params["pageSize"]
    below = None if cursor is None else host.take_cursor(cursor, public)["belowSequence"]
    current_ref = store._db.execute(
        "SELECT checkpoint FROM app_projects WHERE project=?", (internal,)
    ).fetchone()[0]
    # Checkpoint rows carry no sequence column; recover it from the verified
    # ledger head map instead of trusting any denormalized field.
    total = store._db.execute(
        "SELECT count(*) FROM app_checkpoints WHERE project=?", (internal,)
    ).fetchone()[0]
    _, checkpoints, _ = format3._history(store, internal)
    rows = sorted(checkpoints.values(), key=lambda cp: cp["operationSequence"], reverse=True)
    start = (
        0
        if below is None
        else next((i for i, cp in enumerate(rows) if cp["operationSequence"] < below), len(rows))
    )
    window = rows[start : start + page_size]
    more = start + page_size < len(rows)
    next_below = window[-1]["operationSequence"] if len(window) == page_size and more else None
    items = [_item(store, public, internal, cp, current_ref) for cp in window]
    next_cursor = (
        host.hold_cursor(public, {"belowSequence": next_below}) if next_below is not None else None
    )
    result = {
        "checkpointListVersion": 1,
        "projectId": public,
        "items": items,
        "total": total,
        "offset": start,
        "nextCursor": next_cursor,
    }
    store._valid("result_project.checkpoint.list", result)
    return result


def _create(store, public, params, origin):
    internal = _public(store, public)
    _active(store, internal)
    operation = params["operationId"]
    require(uuid_ref(operation), "input")
    label = params["label"]
    require(
        label is None
        or (isinstance(label, str) and bool(label) and len(label.encode("utf-8")) <= 256),
        "input",
    )
    # Wire callers can only mint explicit manual checkpoints. The other three
    # reasons belong to their still-unintegrated real triggers (T07/T08/I06).
    change = {"type": "checkpoint.create", "reason": "manual", "label": label}
    receipt = store.apply_application(
        public,
        operation,
        change,
        actor=origin["hostClientId"],
        permission="write",
    )
    cp = store.project_checkpoint(internal, receipt["afterCheckpointRef"])
    result = {
        "checkpointCreateVersion": 1,
        "projectId": public,
        "operationId": operation,
        "operationSequence": receipt["operationSequence"],
        "checkpointRef": receipt["afterCheckpointRef"],
        "reason": "manual",
        "label": label,
        "domainRevision": cp["domainRevision"],
        "metadataVersion": cp["application"]["metadataVersion"],
    }
    store._valid("result_project.checkpoint.create", result)
    return result


def _document(items):
    raw = canonical(items).encode("utf-8")
    if len(raw) > MAX_DOCUMENT:
        fault("RESOURCE_LIMIT", resource="page")
    pieces = [raw[i : i + SEGMENT_BYTES] for i in range(0, len(raw), SEGMENT_BYTES)]
    segments, values = [], []
    for index, data in enumerate(pieces):
        descriptor = {
            "ordinal": index,
            "byteOffset": index * SEGMENT_BYTES,
            "rawByteLength": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        segments.append(descriptor)
        values.append({**descriptor, "dataBase64": base64.b64encode(data).decode("ascii")})
    manifest = {
        "documentKind": "restore-impact",
        "documentHash": hashlib.sha256(raw).hexdigest(),
        "totalBytes": len(raw),
        "segmentCount": len(segments),
        "segments": segments,
    }
    return manifest, values


def _intern_blob(store, project, value):
    ref = store.put_blob(project, value)
    if ref != digest(value) or store.blob(project, ref) != value:
        fault("INVALID_STATE")
    return ref


def _verify_document(store, project, envelope):
    manifest, expected = _document(json.loads(envelope["document"]))
    if (
        manifest != envelope["manifest"]
        or [digest(v) for v in expected] != envelope["segmentBlobRefs"]
    ):
        fault("INVALID_STATE")
    for ref, value in zip(envelope["segmentBlobRefs"], expected, strict=True):
        if store.blob(project, ref) != value:
            fault("INVALID_STATE")
    return manifest


def _envelope(store, project, preview_ref, host_client_id, engine_session_id):
    row = store._db.execute(
        "SELECT * FROM job_details WHERE project=? AND id=?", (project, preview_ref)
    ).fetchone()
    if row is None:
        fault("NOT_FOUND", resource="preview")
    value = format3._json(row["payload"])
    if (
        not isinstance(value, dict)
        or value.get(PREVIEW_VERSION) != 1
        or digest(value) != preview_ref
    ):
        fault("INVALID_STATE")
    if (value["hostClientId"], value["engineSessionId"]) != (host_client_id, engine_session_id):
        fault("IDENTITY_CONFLICT")
    return value


def _current_binding(store, internal, public, envelope):
    from ontolearn_engine.project.management import lifecycle

    version = lifecycle(store, internal)["version"]
    if version != envelope["lifecycleVersion"]:
        fault("REVISION_CONFLICT", expected=envelope["lifecycleVersion"], actual=version)
    current = store.project_checkpoint(internal)
    if digest(current) != envelope["expectedCheckpointRef"]:
        # The head moved: report the integer sequence axis, never raw hashes.
        fault(
            "REVISION_CONFLICT",
            expected=envelope["expectedOperationSequence"],
            actual=current["operationSequence"],
        )
    return current


def _intervening(store, internal, target_sequence, current_sequence):
    operations = []
    after = target_sequence
    while after is not None and after < current_sequence:
        page = store.project_operations(
            internal,
            after_sequence=after,
            through_sequence=current_sequence,
            limit=100,
        )
        for item in page["items"]:
            kind, change = _change_type(store, internal, item["operationId"])
            operations.append(
                {
                    "sequence": item["sequence"],
                    "operationId": item["operationId"],
                    "operationKind": item["operationKind"],
                    "changeType": (
                        change["type"]
                        if change is not None
                        else ("domain" if item["operationKind"] == "domain" else "create")
                    ),
                }
            )
        after = page["nextSequence"]
    return operations


def _restore_preview(store, public, params, host, origin):
    internal = _public(store, public)
    _active(store, internal)
    from ontolearn_engine.project.management import lifecycle

    target_ref = params["targetCheckpointRef"]
    current = store.project_checkpoint(internal)
    if params["expectedCheckpointRef"] != digest(current):
        # Same precedent as management preview: a stale head ref is a state
        # mismatch; integer revision axes keep REVISION_CONFLICT precise.
        fault("INVALID_STATE")
    if lifecycle(store, internal)["version"] != params["expectedLifecycleVersion"]:
        fault(
            "REVISION_CONFLICT",
            expected=params["expectedLifecycleVersion"],
            actual=lifecycle(store, internal)["version"],
        )
    # project_checkpoint only resolves identities verified by the immutable
    # ledger: cross-project, future or forged refs raise before any document
    # is built.
    target = store.project_checkpoint(internal, target_ref)
    if digest(target) == digest(current):
        fault("INVALID_REQUEST", field="params")
    domain_preview = None
    if target["domainSnapshotRef"] != current["domainSnapshotRef"]:
        from ontolearn_engine.project.transactions import ProjectTransactions

        domain_preview = ProjectTransactions(store).preview(
            internal,
            current["domainRevision"],
            {"compensate": {"kind": "restore", "snapshotRef": target["domainSnapshotRef"]}},
        )
    before_drafts = {row["editor"]: row for row in current["application"]["drafts"]}
    target_drafts = {row["editor"]: row for row in target["application"]["drafts"]}
    drafts = [
        {
            "editor": editor,
            "before": before_drafts.get(editor),
            "after": target_drafts.get(editor),
        }
        for editor in sorted(before_drafts.keys() | target_drafts.keys())
    ]
    before_learning = {row["attempt"]: row for row in current["application"]["learningCurrent"]}
    target_learning = {row["attempt"]: row for row in target["application"]["learningCurrent"]}
    learning = []
    for attempt in sorted(before_learning.keys() | target_learning.keys()):
        restored = target_learning.get(attempt)
        learning.append(
            {
                "attempt": attempt,
                "before": before_learning.get(attempt),
                "after": restored,
                "withdrawnByRestore": restored is None,
            }
        )
    operations = _intervening(
        store, internal, target["operationSequence"], current["operationSequence"]
    )
    document = {
        "restoreImpactVersion": 1,
        "projectId": public,
        "targetCheckpointRef": target_ref,
        "target": {
            "operationSequence": target["operationSequence"],
            "domainRevision": target["domainRevision"],
            "domainSnapshotRef": target["domainSnapshotRef"],
            "metadataVersion": target["application"]["metadataVersion"],
        },
        "current": {
            "checkpointRef": digest(current),
            "operationSequence": current["operationSequence"],
            "domainRevision": current["domainRevision"],
            "metadataVersion": current["application"]["metadataVersion"],
        },
        "domainWillRestore": domain_preview is not None,
        "domainDiff": domain_preview.diff if domain_preview is not None else [],
        "metadata": {
            "before": current["application"]["metadata"],
            "after": target["application"]["metadata"],
        },
        "drafts": drafts,
        "learning": learning,
        "interveningOperations": operations,
        "coverage": list(COVERAGE),
        "preserved": list(PRESERVED),
    }
    manifest, segments = _document(document)
    with store._transaction():
        blob_refs = [_intern_blob(store, public, segment) for segment in segments]
        envelope = {
            PREVIEW_VERSION: 1,
            "projectId": public,
            "hostClientId": origin["hostClientId"],
            "engineSessionId": origin["engineSessionId"],
            "lifecycleVersion": params["expectedLifecycleVersion"],
            "expectedCheckpointRef": digest(current),
            "expectedOperationSequence": current["operationSequence"],
            "expectedMetadataVersion": current["application"]["metadataVersion"],
            "expectedDomainRevision": current["domainRevision"],
            "targetCheckpointRef": target_ref,
            "document": canonical(document),
            "manifest": manifest,
            "segmentBlobRefs": blob_refs,
        }
        preview_ref = digest(envelope)
        store._db.execute(
            "INSERT OR IGNORE INTO job_details VALUES(?,?,?)",
            (preview_ref, public, canonical(envelope)),
        )
    host.hold_preview(preview_ref, public)
    result = {
        "restorePreviewVersion": 1,
        "previewRef": preview_ref,
        "projectId": public,
        "documentHash": manifest["documentHash"],
        "manifest": manifest,
        "targetCheckpointRef": target_ref,
        "targetOperationSequence": target["operationSequence"],
        "targetDomainRevision": target["domainRevision"],
        "currentCheckpointRef": digest(current),
        "currentOperationSequence": current["operationSequence"],
        "interveningOperationCount": len(operations),
        "domainWillRestore": domain_preview is not None,
        "expiresAtMs": store.now_ms() + PREVIEW_TTL_MS,
    }
    store._valid("result_project.restore.preview", result)
    return result


def _restore_page(store, public, params, origin):
    internal = _public(store, public)
    envelope = _envelope(
        store, public, params["previewRef"], origin["hostClientId"], origin["engineSessionId"]
    )
    _current_binding(store, internal, public, envelope)
    manifest = _verify_document(store, public, envelope)
    cursor = params["cursor"]
    offset = 0
    if cursor is not None:
        require(isinstance(cursor, str) and cursor.isdigit() and len(cursor) <= 10, "input")
        offset = int(cursor)
    if offset >= manifest["totalBytes"] and manifest["totalBytes"] > 0:
        fault("CURSOR_MISMATCH")
    values = [store.blob(public, ref) for ref in envelope["segmentBlobRefs"]]
    chosen = []
    for value in values:
        if value["byteOffset"] < offset:
            continue
        chosen.append(value)
        if len(chosen) >= MAX_LIST_PAGE:
            break
    end = offset + sum(value["rawByteLength"] for value in chosen)
    result = {
        "restorePageVersion": 1,
        "projectId": public,
        "previewRef": params["previewRef"],
        "documentHash": manifest["documentHash"],
        "segments": chosen,
        "nextCursor": str(end) if end < manifest["totalBytes"] else None,
        "complete": end >= manifest["totalBytes"],
    }
    store._valid("result_project.restore.page", result)
    return result


def _restore_confirm(store, public, params, origin):
    internal = _public(store, public)
    _active(store, internal)
    envelope = _envelope(
        store, public, params["previewRef"], origin["hostClientId"], origin["engineSessionId"]
    )
    _current_binding(store, internal, public, envelope)
    manifest = _verify_document(store, public, envelope)
    if params["documentHash"] != manifest["documentHash"]:
        fault("IDENTITY_CONFLICT")
    read = params["readSegmentHashes"]
    expected = [segment["sha256"] for segment in manifest["segments"]]
    if read != expected:
        # Incomplete or reordered reading can never mint write authority.
        fault("CURSOR_MISMATCH")
    change = {
        "type": "project.restore",
        "checkpointRef": envelope["targetCheckpointRef"],
        "expectedCheckpointRef": envelope["expectedCheckpointRef"],
        "expectedMetadataVersion": envelope["expectedMetadataVersion"],
        "expectedOperationSequence": envelope["expectedOperationSequence"],
    }
    prepared = store.prepare_application(
        public, change, actor=origin["hostClientId"], permission="write"
    )
    request = {
        "projectId": public,
        "previewRef": params["previewRef"],
        "documentHash": manifest["documentHash"],
        "readSegmentHashes": read,
    }
    receipt = {
        RECEIPT_VERSION: 1,
        "request": request,
        "requestHash": digest(request),
        "hostClientId": origin["hostClientId"],
        "engineSessionId": origin["engineSessionId"],
        "result": {
            "preparedPlanRef": prepared["preparedPlanRef"],
            "confirmationRef": prepared["confirmationRef"],
            "documentHash": manifest["documentHash"],
            "previewRef": params["previewRef"],
            "targetCheckpointRef": envelope["targetCheckpointRef"],
        },
    }
    with store._transaction():
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (prepared["confirmationRef"], public, canonical(receipt)),
        )
    result = {
        "restoreConfirmationVersion": 1,
        "projectId": public,
        "previewRef": params["previewRef"],
        "documentHash": manifest["documentHash"],
        "preparedPlanRef": prepared["preparedPlanRef"],
        "confirmationRef": prepared["confirmationRef"],
        "expiresAtMs": store.now_ms() + PREVIEW_TTL_MS,
    }
    store._valid("result_project.restore.confirm", result)
    return result


def _confirmation_receipt(store, public, confirmation):
    require(uuid_ref(confirmation), "input")
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE project=? AND id=?", (public, confirmation)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    value = format3._json(row[0])
    if (
        not isinstance(value, dict)
        or value.get(RECEIPT_VERSION) != 1
        or value["result"]["confirmationRef"] != confirmation
    ):
        fault("INVALID_STATE")
    return value


def _restore_result(store, public, operation, receipt, confirmation_receipt):
    internal = _public(store, public)
    after = store.project_checkpoint(internal, receipt["afterCheckpointRef"])
    result = {
        "restoreResultVersion": 1,
        "projectId": public,
        "operationId": operation,
        "requestHash": digest(
            {
                "projectId": public,
                "operationId": operation,
                "confirmationRef": confirmation_receipt["result"]["confirmationRef"],
                "documentHash": confirmation_receipt["result"]["documentHash"],
            }
        ),
        "receiptHash": digest(receipt),
        "checkpointRef": receipt["afterCheckpointRef"],
        "operationSequence": receipt["operationSequence"],
        "domainRevision": after["domainRevision"],
        "metadataVersion": after["application"]["metadataVersion"],
        "restoredFromCheckpointRef": confirmation_receipt["result"]["targetCheckpointRef"],
        "coverage": list(COVERAGE),
        "preserved": list(PRESERVED),
    }
    store._valid("result_project.restore.apply", result)
    return result


def _restore_apply(store, public, params, origin):
    internal = _public(store, public)
    confirmation = _confirmation_receipt(store, public, params["confirmationRef"])
    if (
        confirmation["hostClientId"],
        confirmation["engineSessionId"],
    ) != (origin["hostClientId"], origin["engineSessionId"]):
        fault("IDENTITY_CONFLICT")
    if params["documentHash"] != confirmation["result"]["documentHash"]:
        fault("IDENTITY_CONFLICT")
    operation = params["operationId"]
    require(uuid_ref(operation), "input")
    request_hash = digest(
        {
            "projectId": public,
            "operationId": operation,
            "confirmationRef": params["confirmationRef"],
            "documentHash": params["documentHash"],
        }
    )
    _active(store, internal)
    # Exact evidence precedes volatile refs: an acknowledged restore replays its
    # original receipt even after selection or TTL changed.
    existing = _operation_state(store, public, operation, request_hash)
    if existing["state"] == "applied":
        return existing["result"]
    prepared_ref = confirmation["result"]["preparedPlanRef"]
    row = store._db.execute(
        "SELECT payload FROM job_plans WHERE project=? AND ref=?", (public, prepared_ref)
    ).fetchone()
    if row is None:
        fault("IDENTITY_CONFLICT")
    change = json.loads(row[0])["plan"]["change"]
    require(change["type"] == "project.restore", "identity")
    receipt = store.apply_application(
        public,
        operation,
        change,
        actor=origin["hostClientId"],
        permission="write",
        prepared_plan_ref=prepared_ref,
        confirmation_ref=params["confirmationRef"],
    )
    result = _restore_result(store, public, operation, receipt, confirmation)
    return result


def _operation_state(store, public, operation, request_hash):
    internal = _public(store, public)
    row = store._db.execute(
        "SELECT context FROM operation_claims WHERE operation=?", (operation,)
    ).fetchone()
    result = {"state": "not-found", "result": None}
    if row is None:
        occupied = store._db.execute(
            "SELECT 1 FROM app_operations WHERE project=? AND operation=?", (internal, operation)
        ).fetchone()
        if occupied is None:
            return result
        fault("IDENTITY_CONFLICT")
    context = format3._json(row[0])
    if (
        not isinstance(context, dict)
        or "applicationContextVersion" not in context
        or context["plan"]["change"]["type"] != "project.restore"
        or context["projectId"] != public
    ):
        fault("IDENTITY_CONFLICT")
    confirmation = _confirmation_receipt(
        store, public, context["request"]["authorization"]["confirmationRef"]
    )
    expected = digest(
        {
            "projectId": public,
            "operationId": operation,
            "confirmationRef": confirmation["result"]["confirmationRef"],
            "documentHash": confirmation["result"]["documentHash"],
        }
    )
    if request_hash is not None and request_hash != expected:
        fault("IDENTITY_CONFLICT")
    proof = store.project_receipt(internal, operation)
    result["state"] = "applied"
    result["result"] = _restore_result(store, public, operation, proof, confirmation)
    return result


def _restore_operation_get(store, public, params):
    require(uuid_ref(params["operationId"]) and hash_ref(params["requestHash"]), "input")
    result = _operation_state(store, public, params["operationId"], params["requestHash"])
    store._valid("result_project.restore.operation.get", result)
    return result


def dispatch(store, method, params, host, origin):
    """All Store reads/writes stay on the owned connection and its budgets."""
    if method == "project.checkpoint.list":
        store._valid("params_project.checkpoint.list", params)
        return _list(store, params["projectId"], params, host)
    if method == "project.checkpoint.create":
        store._valid("params_project.checkpoint.create", params)
        return _create(store, params["projectId"], params, origin)
    if method == "project.restore.preview":
        store._valid("params_project.restore.preview", params)
        return _restore_preview(store, params["projectId"], params, host, origin)
    if method == "project.restore.page":
        store._valid("params_project.restore.page", params)
        return _restore_page(store, params["projectId"], params, origin)
    if method == "project.restore.confirm":
        store._valid("params_project.restore.confirm", params)
        return _restore_confirm(store, params["projectId"], params, origin)
    if method == "project.restore.apply":
        store._valid("params_project.restore.apply", params)
        return _restore_apply(store, params["projectId"], params, origin)
    if method == "project.restore.operation.get":
        store._valid("params_project.restore.operation.get", params)
        return _restore_operation_get(store, params["projectId"], params)
    fault("PERMISSION_DENIED")
