"""B1b whole-project checkpoint/restore service over the real owned runtime.

Covers FR-004/FR-804 restore semantics: segmented full-read confirmation, mixed
intervening operations, CAS rejections, lost-ACK idempotency and the
immutability boundary. No DTO construction stands in for an integrated
producer (learning rows are exercised at the pure-effects boundary).
"""

import base64
import json
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import applications, format3
from ontolearn_engine.project.transactions import ProjectFault, ProjectTransactions
from ontolearn_engine.resources import CONTRACT, REGISTRY_HASH
from ontolearn_engine.storage import Conflict, canonical, digest

IMPL = {
    "executionSemanticsVersion": "b1b-test",
    "engineVersion": "test",
    "dependencyLockHash": "synthetic",
}


def uid():
    return str(uuid4())


def frame(actor, method, params):
    return {
        "kind": "request",
        "id": uid(),
        "protocolVersion": 2 if method == "hello" else 3,
        "engineSessionId": None if method == "hello" else actor.session,
        "method": method,
        "params": params,
    }


def exchange(actor, method, params):
    request = frame(actor, method, params)
    response = actor.request(request)
    actor.finish_query_reply(request["id"], emitted=True)
    return response


def ok(response):
    assert response["ok"], response
    return response["result"]


def denied(response, code):
    assert not response["ok"] and response["error"]["code"] == code, response
    return response["error"]


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "b1b.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    yield actor, store
    actor.mainline.close()
    store.close()


def open_blank(actor):
    created = ok(
        exchange(
            actor,
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": "B1b 项目",
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


def domain_commit(store, project, enabled, job=None):
    """One real domain operation through the original Store ledger."""
    internal = store._project(project)
    return store.commit(
        internal,
        store.revision(internal),
        uid(),
        job or uid(),
        definitions=[{"layer": "rule", "id": "r", "value": {"enabled": enabled}}],
    )


def apply_change(store, project, change, prepared=None):
    return store.apply_application(
        project,
        uid(),
        prepared["change"] if prepared else change,
        actor=store.actor,
        permission="write",
        **(
            {
                "prepared_plan_ref": prepared["preparedPlanRef"],
                "confirmation_ref": prepared["confirmationRef"],
            }
            if prepared
            else {}
        ),
    )


def read_document(actor, project, preview):
    """Page through every segment, verifying continuity like the renderer."""
    text, hashes, cursor = "", [], None
    pages = 0
    while True:
        page = ok(
            exchange(
                actor,
                "project.restore.page",
                {"projectId": project, "previewRef": preview["previewRef"], "cursor": cursor},
            )
        )
        assert page["documentHash"] == preview["documentHash"]
        for segment in page["segments"]:
            assert segment["sha256"] not in hashes
            hashes.append(segment["sha256"])
            text += base64.b64decode(segment["dataBase64"]).decode("utf-8")
        pages += 1
        cursor = page["nextCursor"]
        if cursor is None:
            assert page["complete"]
            break
        assert pages <= 64
    assert len(hashes) == preview["manifest"]["segmentCount"]
    return json.loads(text), hashes


def preview_restore(actor, project, target):
    state = ok(exchange(actor, "project.management.read", {"projectId": project}))
    return ok(
        exchange(
            actor,
            "project.restore.preview",
            {
                "projectId": project,
                "targetCheckpointRef": target,
                "expectedCheckpointRef": state["checkpointRef"],
                "expectedLifecycleVersion": state["lifecycle"]["version"],
            },
        )
    ), state


def test_checkpoint_list_reasons_and_manual_creation(owned):
    actor, store = owned
    project = open_blank(actor)
    domain_commit(store, project, True)
    store.actor = actor.host_client_id
    listing = ok(
        exchange(
            actor,
            "project.checkpoint.list",
            {"projectId": project, "pageSize": 50, "cursor": None},
        )
    )
    assert [item["reason"] for item in listing["items"]][0] == "operation"
    genesis = listing["items"][-1]
    assert genesis["reason"] == "genesis" and genesis["isCurrent"] is False

    checkpoint_operation = uid()
    created = ok(
        exchange(
            actor,
            "project.checkpoint.create",
            {"projectId": project, "operationId": checkpoint_operation, "label": "导入映射之前"},
        )
    )
    assert created["reason"] == "manual" and created["label"] == "导入映射之前"
    # The persisted receipt carries flat CAS evidence lists, never a nested [[]].
    persisted = store.project_receipt(store._project(project), checkpoint_operation)
    assert persisted["applicationBeforeCAS"] == []
    assert persisted["applicationAfterCAS"] == []
    listing = ok(
        exchange(
            actor,
            "project.checkpoint.list",
            {"projectId": project, "pageSize": 1, "cursor": None},
        )
    )
    top = listing["items"][0]
    assert top["checkpointRef"] == created["checkpointRef"]
    assert top["reason"] == "manual" and top["isCurrent"] is True
    assert top["coverage"] == ["metadata", "drafts", "learningCurrent", "assistanceAudit"]
    assert "historical-runs" in top["preserved"]
    assert listing["nextCursor"] is not None
    second = ok(
        exchange(
            actor,
            "project.checkpoint.list",
            {"projectId": project, "pageSize": 50, "cursor": listing["nextCursor"]},
        )
    )
    assert second["items"][0]["reason"] == "operation" and second["offset"] == 1


@pytest.mark.parametrize("reason", ["before-run", "guided-stage", "before-agent"])
def test_internal_checkpoint_reasons_exist_but_wire_only_mints_manual(owned, reason):
    actor, store = owned
    project = open_blank(actor)
    store.actor = actor.host_client_id
    receipt = store.apply_application(
        project,
        uid(),
        {"type": "checkpoint.create", "reason": reason, "label": None},
        actor=actor.host_client_id,
        permission="write",
    )
    listing = ok(
        exchange(
            actor,
            "project.checkpoint.list",
            {"projectId": project, "pageSize": 50, "cursor": None},
        )
    )
    top = listing["items"][0]
    assert top["reason"] == reason and top["operationKind"] == "application"
    assert receipt["operationKind"] == "application"


def test_restore_full_flow_with_mixed_intervening_operations(owned):
    actor, store = owned
    project = open_blank(actor)
    store.actor = actor.host_client_id
    domain_commit(store, project, True)
    published = store.publish(
        store._project(project),
        store.snapshot(store._project(project)),
        ["rule:r"],
        "query",
        ["v1"],
        IMPL,
    )
    checkpoint = ok(
        exchange(
            actor,
            "project.checkpoint.create",
            {"projectId": project, "operationId": uid(), "label": "CP1"},
        )
    )
    target = checkpoint["checkpointRef"]

    # Mixed intervening operations: application rename + mode, draft, domain.
    internal = store._project(project)
    state = store.project_checkpoint(internal)
    apply_change(
        store,
        project,
        {
            "type": "metadata",
            "expectedVersion": state["application"]["metadataVersion"],
            "patch": {"name": "改名后", "mode": "assisted"},
        },
    )
    apply_change(
        store,
        project,
        {
            "type": "draft.save",
            "editor": "query-workspace-v1",
            "expectedGeneration": 0,
            "boundDomainRevision": store.revision(internal),
            "content": {"draft": True},
        },
    )
    combined = {
        "type": "draft.save",
        "editor": "other",
        "expectedGeneration": 0,
        "boundDomainRevision": store.revision(internal) + 1,
        "content": {"later": True},
        "domain": {
            "base": store.revision(internal),
            "plan": {"definitions": [{"layer": "rule", "id": "r", "value": {"enabled": False}}]},
        },
    }
    prepared = store.prepare_application(
        project, combined, actor=actor.host_client_id, permission="write"
    )
    apply_change(store, project, combined, prepared)
    assert store.result(published)["stale"]

    preview, state = preview_restore(actor, project, target)
    assert preview["domainWillRestore"] is True
    # The target checkpoint operation itself is the boundary, not overwritten.
    assert preview["interveningOperationCount"] == 3
    document, hashes = read_document(actor, project, preview)
    assert document["domainWillRestore"] is True and document["domainDiff"]
    kinds = sorted(
        (item["operationKind"], item["changeType"]) for item in document["interveningOperations"]
    )
    assert kinds == sorted(
        [
            ("application", "metadata"),
            ("application", "draft.save"),
            ("combined", "draft.save"),
        ]
    )
    assert document["metadata"]["after"]["name"] == "B1b 项目"  # CP1 predates the rename
    assert document["metadata"]["before"]["name"] == "改名后"
    assert document["metadata"]["before"]["mode"] == "assisted"
    assert {draft["editor"] for draft in document["drafts"]} == {"query-workspace-v1", "other"}

    # A wrong, partial or unordered reading never mints write authority.
    assert preview["manifest"]["segmentCount"] >= 1
    partial = hashes[:1] if preview["manifest"]["segmentCount"] > 1 else ["0" * 64]
    denied(
        exchange(
            actor,
            "project.restore.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
                "readSegmentHashes": partial,
            },
        ),
        "CURSOR_MISMATCH",
    )
    confirmation = ok(
        exchange(
            actor,
            "project.restore.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
                "readSegmentHashes": hashes,
            },
        )
    )
    operation = uid()
    result = ok(
        exchange(
            actor,
            "project.restore.apply",
            {
                "projectId": project,
                "operationId": operation,
                "confirmationRef": confirmation["confirmationRef"],
                "documentHash": preview["documentHash"],
            },
        )
    )
    assert result["restoredFromCheckpointRef"] == target
    assert result["checkpointRef"] != target
    assert result["operationSequence"] > preview["currentOperationSequence"]
    # The persisted receipt's CAS evidence is a flat list of dicts, never a
    # nested [[{...}]] wrapper, for both sides of the restore transition.
    restore_receipt = store.project_receipt(store._project(project), operation)
    for cas in (restore_receipt["applicationBeforeCAS"], restore_receipt["applicationAfterCAS"]):
        assert isinstance(cas, list) and cas, cas
        assert all(isinstance(item, dict) for item in cas)

    head = store.project_checkpoint(store._project(project))
    assert head["application"]["metadata"]["name"] == "B1b 项目"
    assert head["application"]["metadata"]["mode"] == "guided"
    drafts = {row["editor"]: row for row in head["application"]["drafts"]}
    assert drafts["query-workspace-v1"]["present"] == 0  # CP1 had no draft
    assert drafts["other"]["present"] == 0
    assert json.loads(store.state(store._project(project))["definitions"][0]["payload"]) == {
        "enabled": True
    }
    assert store._db.execute("SELECT count(*) FROM app_checkpoints").fetchone()[0] > 3
    # FR-006: the old current result is invalidated by the domain compensation.
    stale = store.result(published)
    assert stale["state"] != "current" and stale["stale"]
    # Lost ACK: the same operation replays its original durable receipt.
    replay = ok(
        exchange(
            actor,
            "project.restore.apply",
            {
                "projectId": project,
                "operationId": operation,
                "confirmationRef": confirmation["confirmationRef"],
                "documentHash": preview["documentHash"],
            },
        )
    )
    assert replay["receiptHash"] == result["receiptHash"]
    state = ok(
        exchange(
            actor,
            "project.restore.operation.get",
            {
                "projectId": project,
                "operationId": operation,
                "requestHash": result["requestHash"],
            },
        )
    )
    assert state["state"] == "applied" and state["result"]["requestHash"] == result["requestHash"]
    unknown = ok(
        exchange(
            actor,
            "project.restore.operation.get",
            {"projectId": project, "operationId": uid(), "requestHash": result["requestHash"]},
        )
    )
    assert unknown["state"] == "not-found" and unknown["result"] is None


def test_restore_rejects_stale_forged_same_and_cross_project_targets(owned):
    actor, store = owned
    project = open_blank(actor)
    other = open_blank(actor)
    ok(exchange(actor, "project.open", {"projectId": project}))
    store.actor = actor.host_client_id
    domain_commit(store, project, True)
    checkpoint = ok(
        exchange(
            actor,
            "project.checkpoint.create",
            {"projectId": project, "operationId": uid(), "label": None},
        )
    )
    target = checkpoint["checkpointRef"]
    # Advance past the target so it is a legal restore source, not the head.
    head_state = store.project_checkpoint(store._project(project))
    apply_change(
        store,
        project,
        {
            "type": "metadata",
            "expectedVersion": head_state["application"]["metadataVersion"],
            "patch": {"name": "越过检查点"},
        },
    )

    # A foreign project's real checkpoint ref, read from its own ledger: only
    # the selected project may be listed, so no wire route exposes it.
    foreign = store._db.execute(
        "SELECT checkpoint FROM app_projects WHERE project=?", (store._project(other),)
    ).fetchone()[0]
    preview_state = ok(exchange(actor, "project.management.read", {"projectId": project}))
    base = {
        "expectedCheckpointRef": preview_state["checkpointRef"],
        "expectedLifecycleVersion": preview_state["lifecycle"]["version"],
    }
    denied(
        exchange(
            actor,
            "project.restore.preview",
            {"projectId": project, "targetCheckpointRef": "0" * 64, **base},
        ),
        "NOT_FOUND",
    )
    denied(
        exchange(
            actor,
            "project.restore.preview",
            {"projectId": project, "targetCheckpointRef": foreign, **base},
        ),
        "NOT_FOUND",
    )
    denied(
        exchange(
            actor,
            "project.restore.preview",
            {"projectId": project, "targetCheckpointRef": base["expectedCheckpointRef"], **base},
        ),
        "INVALID_REQUEST",
    )
    denied(
        exchange(
            actor,
            "project.restore.preview",
            {
                "projectId": project,
                "targetCheckpointRef": target,
                "expectedCheckpointRef": "1" * 64,
                "expectedLifecycleVersion": 0,
            },
        ),
        # Management-preview precedent: a stale head ref is a state mismatch;
        # integer axes (lifecycle/sequence) carry the precise REVISION_CONFLICT.
        "INVALID_STATE",
    )

    # A preview that has been overtaken by a later write cannot be confirmed.
    preview = ok(
        exchange(
            actor,
            "project.restore.preview",
            {"projectId": project, "targetCheckpointRef": target, **base},
        )
    )
    document, hashes = read_document(actor, project, preview)
    overtaken = store.project_checkpoint(store._project(project))
    apply_change(
        store,
        project,
        {
            "type": "metadata",
            "expectedVersion": overtaken["application"]["metadataVersion"],
            "patch": {"name": "抢先"},
        },
    )
    denied(
        exchange(
            actor,
            "project.restore.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
                "readSegmentHashes": hashes,
            },
        ),
        "REVISION_CONFLICT",
    )


def test_trashed_project_cannot_create_checkpoints_or_restore(owned):
    actor, store = owned
    project = open_blank(actor)
    state = ok(exchange(actor, "project.management.read", {"projectId": project}))
    preview = ok(
        exchange(
            actor,
            "project.management.preview",
            {
                "projectId": project,
                "action": {"kind": "trash"},
                "expectedCheckpointRef": state["checkpointRef"],
                "expectedLifecycleVersion": state["lifecycle"]["version"],
            },
        )
    )
    confirmation = ok(
        exchange(
            actor,
            "project.management.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
            },
        )
    )
    ok(
        exchange(
            actor,
            "project.management.apply",
            {
                "projectId": project,
                "operationId": uid(),
                "confirmationRef": confirmation["confirmationRef"],
                "documentHash": preview["documentHash"],
            },
        )
    )
    denied(
        exchange(
            actor,
            "project.checkpoint.create",
            {"projectId": project, "operationId": uid(), "label": None},
        ),
        # Selection fencing rejects a trashed project before any state work.
        "PERMISSION_DENIED",
    )
    target = preview["document"]["checkpointRef"]
    denied(
        exchange(
            actor,
            "project.restore.preview",
            {
                "projectId": project,
                "targetCheckpointRef": target,
                "expectedCheckpointRef": target,
                "expectedLifecycleVersion": 1,
            },
        ),
        "PERMISSION_DENIED",
    )


def test_restore_effects_learning_withdraw_keeps_rows_and_audit(owned):
    """Pure-effects boundary: the learning producer itself is still T07-gated."""
    actor, store = owned
    open_blank(actor)
    target = {
        "project": "p",
        "domainRevision": 1,
        "domainSnapshotRef": "0" * 64,
        "operationSequence": 1,
        "application": {
            "metadataVersion": 0,
            "metadata": format3.metadata("created"),
            "drafts": [],
            "learningCurrent": [
                {
                    "attempt": "kept",
                    "record_version": 3,
                    "course": "c",
                    "task": "t",
                    "payload": canonical({"progress": "early"}),
                }
            ],
            "assistanceAudit": [
                {"sequence": 1, "attempt": "kept", "event_id": "e1", "payload": "{}"}
            ],
        },
    }
    before = {
        "metadataVersion": 2,
        "metadata": format3.metadata("created"),
        "drafts": [],
        "learningCurrent": [
            dict(
                target["application"]["learningCurrent"][0],
                payload=canonical({"progress": "late"}),
            ),
            {
                "attempt": "post-cp",
                "record_version": 0,
                "course": "c2",
                "task": "t2",
                "payload": canonical({"progress": "new"}),
            },
        ],
        "assistanceAudit": target["application"]["assistanceAudit"],
    }
    change = {
        "type": "project.restore",
        "checkpointRef": digest(target),
        "expectedCheckpointRef": "2" * 64,
        "expectedMetadataVersion": 2,
        "expectedOperationSequence": 3,
    }
    after, old_cas, new_cas = applications._restore_effects("p", change, before, target, 1)
    learning = {row["attempt"]: row for row in after["learningCurrent"]}
    assert json.loads(learning["kept"]["payload"]) == {"progress": "early"}
    assert learning["kept"]["record_version"] == 4 and learning["post-cp"]["record_version"] == 1
    assert json.loads(learning["post-cp"]["payload"]) == {
        "status": "withdrawn-by-project-restore",
        "restoredToCheckpointRef": change["checkpointRef"],
    }
    # FK/audit invariants: every audited attempt keeps its row, audit is frozen.
    assert set(learning) == {"kept", "post-cp"}
    assert after["assistanceAudit"] == before["assistanceAudit"]
    assert after["metadataVersion"] == 3
    assert old_cas != new_cas and len(old_cas) == len(new_cas) == 3
    # A forged target naming an attempt that never existed in the live rows
    # would mean fabricated future history; the effects boundary rejects it.
    ghost = dict(target["application"]["learningCurrent"][0], attempt="ghost")
    forged = {
        **target,
        "application": {**target["application"], "learningCurrent": [ghost]},
    }
    with pytest.raises(Conflict):
        applications._restore_effects(
            "p", {**change, "checkpointRef": digest(forged)}, before, forged, 1
        )


def test_forged_restore_plan_cannot_attach_wrong_domain(owned):
    actor, store = owned
    project = open_blank(actor)
    store.actor = actor.host_client_id
    domain_commit(store, project, True)
    apply_change(
        store,
        project,
        {
            "type": "draft.save",
            "editor": "q",
            "expectedGeneration": 0,
            "boundDomainRevision": 1,
            "content": "d",
        },
    )
    current = store.project_checkpoint(store._project(project))
    head_ref = store._db.execute(
        "SELECT checkpoint FROM app_projects WHERE project=?", (store._project(project),)
    ).fetchone()[0]
    change = {
        "type": "project.restore",
        "checkpointRef": head_ref,
        "expectedCheckpointRef": digest(current),
        "expectedMetadataVersion": current["application"]["metadataVersion"],
        "expectedOperationSequence": current["operationSequence"],
    }
    # The head-equality guard rejects the meaningless self-restore outright.
    with pytest.raises(Conflict):
        applications.construct_plan(store, store._project(project), change)
    # A forged equal-snapshot plan that smuggles a domain branch cannot enter
    # the ledger: confirmation binding rejects it before any state write.
    forged = {
        "applicationPlanVersion": 1,
        "project": store._project(project),
        "change": {**change, "domain": {"base": current["domainRevision"], "plan": {}}},
        "domain": None,
        "before": current["application"],
        "after": current["application"],
        "beforeCAS": [],
        "afterCAS": [],
    }
    operation = uid()
    context = {
        "applicationContextVersion": 1,
        "projectId": project,
        "project": store._project(project),
        "operationId": operation,
        "request": {
            "change": forged["change"],
            "authorization": {
                "actor": actor.host_client_id,
                "permission": "write",
                "preparedPlanRef": None,
                "confirmationRef": None,
            },
        },
        "plan": forged,
    }
    store._db.execute(
        "INSERT INTO operation_claims VALUES(?,?,NULL,?,'application',?)",
        (operation, project, digest(context), canonical(context)),
    )
    before = format3.logical_hash(store._db)
    from ontolearn_engine.storage import Store

    with pytest.raises((Conflict, format3.Format3Fault)):
        Store.commit(store, store._project(project), None, operation, None, application=context)
    assert format3.logical_hash(store._db) == before


def test_undo_conflict_detection_survives_restore(owned):
    actor, store = owned
    project = open_blank(actor)
    store.actor = actor.host_client_id
    marker = domain_commit(store, project, False)
    current = store.project_checkpoint(store._project(project))
    genesis = store._db.execute(
        "SELECT checkpoint FROM app_origins WHERE project=?", (store._project(project),)
    ).fetchone()[0]
    restore_change = {
        "type": "project.restore",
        "checkpointRef": genesis,
        "expectedCheckpointRef": digest(current),
        "expectedMetadataVersion": current["application"]["metadataVersion"],
        "expectedOperationSequence": current["operationSequence"],
    }
    prepared = store.prepare_application(
        project, restore_change, actor=actor.host_client_id, permission="write"
    )
    store.apply_application(
        project,
        uid(),
        prepared["change"],
        actor=actor.host_client_id,
        permission="write",
        prepared_plan_ref=prepared["preparedPlanRef"],
        confirmation_ref=prepared["confirmationRef"],
    )
    # The disable was compensated away; undoing it against the restored state
    # reports UNDO_CONFLICT instead of silently replaying.
    with pytest.raises(ProjectFault):
        ProjectTransactions(store).preview_undo(store._project(project), marker["operation"])


def _operation_get_envelopes(project_id, result_project_id):
    """A schema-valid project.restore.operation.get request plus an applied
    project.restore.apply receipt; the envelope keeps projectId nested inside
    `result` and carries no top-level projectId of its own (B1B-007)."""
    operation = uid()
    request_hash = "c" * 64
    request = {
        "kind": "request",
        "protocolVersion": 3,
        "id": uid(),
        "engineSessionId": uid(),
        "method": "project.restore.operation.get",
        "params": {
            "projectId": project_id,
            "operationId": operation,
            "requestHash": request_hash,
        },
    }
    applied = {
        "restoreResultVersion": 1,
        "projectId": result_project_id,
        "operationId": operation,
        "requestHash": request_hash,
        "receiptHash": "d" * 64,
        "checkpointRef": "e" * 64,
        "operationSequence": 2,
        "domainRevision": 7,
        "metadataVersion": 4,
        "restoredFromCheckpointRef": "f" * 64,
        "coverage": ["metadata", "drafts", "learningCurrent", "assistanceAudit"],
        "preserved": [
            "historical-runs",
            "jobs-and-results",
            "assistance-audit",
            "operation-evidence",
            "checkpoints",
        ],
    }

    def response(state, result):
        return {
            "kind": "response",
            "protocolVersion": 3,
            "id": request["id"],
            "engineSessionId": request["engineSessionId"],
            "method": "project.restore.operation.get",
            "ok": True,
            "result": {"state": state, "result": result},
        }

    return request, applied, response


def test_operation_get_envelope_not_found_matches_without_keyerror():
    request, _, response = _operation_get_envelopes(uid(), uid())
    # Before the B1B-007 fix the shared projectId guard raised KeyError here.
    assert (
        CONTRACT.matches_business3_response(request, response("not-found", None), REGISTRY_HASH)
        is True
    )


def test_operation_get_envelope_applied_matches_same_project():
    project = uid()
    request, applied, response = _operation_get_envelopes(project, project)
    assert (
        CONTRACT.matches_business3_response(request, response("applied", applied), REGISTRY_HASH)
        is True
    )


def test_operation_get_envelope_applied_rejects_foreign_project():
    request, applied, response = _operation_get_envelopes(uid(), uid())
    assert (
        CONTRACT.matches_business3_response(request, response("applied", applied), REGISTRY_HASH)
        is False
    )
