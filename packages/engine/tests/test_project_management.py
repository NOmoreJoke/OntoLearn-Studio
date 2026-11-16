"""Real Store3 management transactions, immutable replay and protocol fencing."""

from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.project import format3, management
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import Conflict, canonical, digest
from test_mainline_dispatch import drain_owned_changesets, exchange


def uid():
    return str(uuid4())


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "management.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    created = exchange(
        actor,
        "project.create",
        {
            "requestVersion": 1,
            "operationId": uid(),
            "name": "source",
            "initialization": {"kind": "blank"},
        },
    )
    assert created["ok"], created
    yield actor, store, created["result"]["projectId"]
    actor.mainline.close()
    store.close()


def preview(actor, project, action):
    # Restore deliberately uses library-level state, while ordinary actions use
    # the selected project's named state method.
    internal = management.public_internal(actor.store, project)
    cp = actor.store.project_checkpoint(internal)
    life = management.lifecycle(actor.store, internal)
    reply = exchange(
        actor,
        "project.management.preview",
        {
            "projectId": project,
            "action": action,
            "expectedCheckpointRef": digest(cp),
            "expectedLifecycleVersion": life["version"],
        },
    )
    assert reply["ok"], reply
    return reply["result"]


def prepare(actor, project, action):
    viewed = preview(actor, project, action)
    assert viewed["documentHash"] == digest({"action": action, "document": viewed["document"]})
    reply = exchange(
        actor,
        "project.management.confirm",
        {
            "projectId": project,
            "previewRef": viewed["previewRef"],
            "documentHash": viewed["documentHash"],
        },
    )
    assert reply["ok"], reply
    return {
        "projectId": project,
        "operationId": uid(),
        "confirmationRef": reply["result"]["confirmationRef"],
        "documentHash": viewed["documentHash"],
    }


def apply(actor, project, action):
    request = prepare(actor, project, action)
    response = exchange(actor, "project.management.apply", request)
    assert response["ok"], canonical(response)
    return request, response["result"]


def changeset_request(project, base=0):
    return {
        "projectId": project,
        "baseRevision": base,
        "intent": "change",
        "plan": {
            "manual": [
                {
                    "id": digest(["urn:life:s", "urn:life:p", '"value"']),
                    "subject": "urn:life:s",
                    "predicate": "urn:life:p",
                    "object": '"value"',
                }
            ]
        },
    }


def changeset_page(actor, project, ready):
    return exchange(
        actor,
        "changeset.diff.page",
        {
            "projectId": project,
            "previewHash": ready["previewHash"],
            "documentKind": "diff",
            "pageSize": 16,
            "cursor": None,
        },
    )


def changeset_job(project, confirmation):
    return {
        "projectId": project,
        "operationId": uid(),
        "capability": "changeset.commit",
        "confirmationRef": confirmation["confirmationRef"],
        "input": {
            "inputSnapshotId": confirmation["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmation["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmation["preparedPlanRef"],
        },
    }


def test_changeset_preview_cannot_regain_authority_after_trash_restore(owned):
    actor, store, project = owned
    request = changeset_request(project)
    old = exchange(actor, "changeset.preview", request)
    assert old["ok"], old
    old = old["result"]
    page = changeset_page(actor, project, old)
    assert page["ok"] and page["result"]["complete"], page
    confirm = {
        "projectId": project,
        "previewHash": old["previewHash"],
        "completionCursor": page["result"]["nextCursor"],
    }
    apply(actor, project, {"kind": "trash"})
    assert store._db.execute("SELECT count(*) FROM job_cursors").fetchone()[0] == 0
    apply(actor, project, {"kind": "restore-trash"})
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    assert not exchange(actor, "changeset.confirm", confirm)["ok"]
    assert not changeset_page(actor, project, old)["ok"]
    fresh = exchange(actor, "changeset.preview", request)
    assert fresh["ok"], fresh
    fresh = fresh["result"]
    assert fresh["previewHash"] == old["previewHash"]
    assert fresh["preparedPlanRef"] != old["preparedPlanRef"]
    # A fresh identical preview is allowed, but the old completion token is not.
    assert not exchange(actor, "changeset.confirm", confirm)["ok"]
    page = changeset_page(actor, project, fresh)
    assert page["ok"], page
    confirmed = exchange(
        actor,
        "changeset.confirm",
        {
            **confirm,
            "completionCursor": page["result"]["nextCursor"],
        },
    )
    assert confirmed["ok"], confirmed
    job = exchange(actor, "job.create", changeset_job(project, confirmed["result"]))
    assert job["ok"], job
    drain_owned_changesets(actor)
    assert store.get_job(project, job["result"]["jobId"])["state"] == "succeeded"
    assert store.revision(project) == 1


def test_terminal_changeset_history_survives_trashed_restart(owned):
    actor, store, project = owned
    ready = exchange(actor, "changeset.preview", changeset_request(project))["result"]
    page = changeset_page(actor, project, ready)["result"]
    confirmation = exchange(
        actor,
        "changeset.confirm",
        {
            "projectId": project,
            "previewHash": ready["previewHash"],
            "completionCursor": page["nextCursor"],
        },
    )["result"]
    request = changeset_job(project, confirmation)
    queued = exchange(actor, "job.create", request)
    assert queued["ok"], queued
    drain_owned_changesets(actor)
    terminal = store.get_job(project, queued["result"]["jobId"])
    assert terminal["state"] == "succeeded"
    listing = store.job_list(project, "all", 10, None, None)
    assert listing["jobs"] == [terminal]
    apply(actor, project, {"kind": "trash"})
    assert store._db.execute("SELECT count(*) FROM job_lists").fetchone()[0] == 0
    saved = [tuple(row) for row in store._db.execute("SELECT * FROM jobs")]
    actor.mainline.close()
    store.close()
    reopened = JobStore(store.path, contract=CONTRACT, target_format=3)
    try:
        assert reopened.reconcile_jobs() == []
        assert [tuple(row) for row in reopened._db.execute("SELECT * FROM jobs")] == saved
        reopened._validate_job3()
        assert reopened._db.execute("SELECT count(*) FROM job_results").fetchone()[0] == 1
        with pytest.raises(JobFault, match="PERMISSION_DENIED"):
            reopened.get_job(project, terminal["jobId"])
    finally:
        reopened.close()


def test_undo_impact_document_is_bound_to_lifecycle(owned):
    actor, store, project = owned
    operation = uid()
    # A non-ChangeSet historical operation has a genuine unsupported impact.
    store.commit(project, 0, operation, uid(), **changeset_request(project)["plan"])
    request = {
        "projectId": project,
        "baseRevision": 1,
        "intent": "undo",
        "targetOperationId": operation,
    }
    old = exchange(actor, "changeset.preview", request)
    assert old["ok"] and old["result"]["status"] == "conflict", old
    old = old["result"]
    page_request = {
        "projectId": project,
        "previewHash": old["previewHash"],
        "documentKind": "undo-impact",
        "pageSize": 16,
        "cursor": None,
    }
    assert exchange(actor, "changeset.diff.page", page_request)["ok"]
    apply(actor, project, {"kind": "trash"})
    apply(actor, project, {"kind": "restore-trash"})
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    assert not exchange(actor, "changeset.diff.page", page_request)["ok"]
    new = exchange(actor, "changeset.preview", request)
    assert new["ok"] and new["result"]["status"] == "conflict", new
    assert new["result"]["previewHash"] != old["previewHash"]
    assert exchange(
        actor,
        "changeset.diff.page",
        {
            **page_request,
            "previewHash": new["result"]["previewHash"],
        },
    )["ok"]


def test_metadata_copy_trash_restore_and_receipt(owned):
    actor, store, project = owned
    before = store.project_get(project)
    request, result = apply(actor, project, {"kind": "rename", "name": "renamed"})
    assert result["domainRevision"] == 0 and result["metadataVersion"] == 2
    assert store.project_get(project) == before
    assert exchange(actor, "project.management.apply", request)["result"] == result
    _, archived = apply(actor, project, {"kind": "archive", "archived": True})
    assert exchange(actor, "project.get", {"projectId": project})["ok"]
    _, copied = apply(actor, project, {"kind": "copy-current", "name": "copy"})
    target = copied["targetProjectId"]
    assert target != project and copied["domainRevision"] == copied["operationSequence"] == 1
    assert store.project_checkpoint(target)["application"]["metadata"]["archived"] is False
    deletion, deleted = apply(actor, project, {"kind": "trash"})
    assert deleted["lifecycleState"] == "trashed"
    assert not exchange(actor, "project.open", {"projectId": project})["ok"]
    catalog = exchange(actor, "project.catalog", {"pageSize": 10, "cursor": None})
    assert catalog["ok"], catalog
    assert project not in {item["projectId"] for item in catalog["result"]["items"]}
    receipt = exchange(
        actor,
        "project.management.operation.get",
        {
            "projectId": project,
            "operationId": deletion["operationId"],
            "requestHash": digest(deletion),
        },
    )
    assert receipt["result"] == {"state": "applied", "result": deleted}
    _, restored = apply(actor, project, {"kind": "restore-trash"})
    assert restored["lifecycleVersion"] == 2
    # Old selected authority remains fenced after delete/restore ABA.
    assert not exchange(actor, "project.management.read", {"projectId": project})["ok"]
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    state = exchange(actor, "project.management.read", {"projectId": project})
    assert state["result"]["metadata"]["archived"] is True
    format3.validate(store)
    store._validate_job3()


def test_copy_preserves_ownership_drift_retirement_and_independent_reopen(owned):
    actor, store, project = owned
    fact = {
        "id": digest(["urn:s", "urn:p", '"old"']),
        "subject": "urn:s",
        "predicate": "urn:p",
        "object": '"old"',
    }
    tombstone = {
        "id": digest(["urn:s2", "urn:p", '"gone"']),
        "subject": "urn:s2",
        "predicate": "urn:p",
        "object": '"gone"',
    }
    store.commit(
        project,
        0,
        uid(),
        uid(),
        definitions=[
            {"layer": "mapping", "id": "M", "value": {}},
            {"layer": "query", "id": "retired", "value": {}},
        ],
        mapping={"id": "M", "rows": [{"row": "row1", "facts": [fact, tombstone]}]},
    )
    store.commit(
        project,
        1,
        uid(),
        uid(),
        edits={fact["id"]: '"edited"'},
        definitions=[{"layer": "mapping", "id": "M", "value": {"sourceVersion": 2}}],
        remove=[tombstone["id"]],
        remove_definitions=[{"layer": "query", "id": "retired"}],
    )
    seed = store.state(project)
    assert seed["mappingState"]["M"]["stale"]
    counters = list(
        store._db.execute(
            "SELECT key,version FROM versions WHERE project=? ORDER BY key", (project,)
        )
    )
    _, copied = apply(actor, project, {"kind": "copy-current", "name": "copy ownership"})
    target = copied["targetProjectId"]
    assert store.state(target) == seed == store.state(project)
    assert [
        tuple(r)
        for r in store._db.execute(
            "SELECT key,version FROM versions WHERE project=? ORDER BY key", (target,)
        )
    ] == [tuple(r) for r in counters]
    assert store.retirement_control(target) == store.retirement_control(project)
    store.commit(project, 2, uid(), uid(), edits={fact["id"]: '"source later"'})
    assert store.state(target) == seed
    # Replay reads the persisted copy seed, not mutable source current controls.
    format3.validate(store)
    assert store.project_checkpoint(target)["domainRevision"] == 1
    assert (
        store._db.execute("SELECT count(*) FROM jobs WHERE project=?", (target,)).fetchone()[0] == 0
    )
    actor.mainline.close()
    store.close()
    reopened = JobStore(store.path, contract=CONTRACT, target_format=3)
    try:
        assert reopened.state(target) == seed
        format3.validate(reopened)
        reopened._validate_job3()
    finally:
        reopened.close()


def test_old_confirmation_and_unknown_draft_are_rejected(owned):
    actor, store, project = owned
    old = prepare(actor, project, {"kind": "rename", "name": "old"})
    apply(actor, project, {"kind": "set-mode", "mode": "assisted"})
    response = exchange(actor, "project.management.apply", old)
    assert not response["ok"]
    store.apply_application(
        project,
        uid(),
        {
            "type": "draft.save",
            "editor": "unknown",
            "expectedGeneration": 0,
            "boundDomainRevision": 0,
            "content": {"a": 1},
        },
        actor=uid(),
        permission="write",
    )
    reply = exchange(
        actor,
        "project.management.preview",
        {
            "projectId": project,
            "action": {"kind": "copy-current", "name": "cannot copy"},
            "expectedCheckpointRef": digest(store.project_checkpoint(project)),
            "expectedLifecycleVersion": 0,
        },
    )
    assert not reply["ok"]
    assert reply["error"]["code"] == "INVALID_STATE"


def query_content():
    return {
        "version": 1,
        "definitionId": "draft-query",
        "draft": {
            "name": "draft",
            "description": "",
            "sparql": "SELECT ?s WHERE { ?s ?p ?o }",
            "scope": "asserted",
            "capabilityQuestion": "",
            "source": "editor",
        },
    }


def test_known_query_draft_rebinds_and_stale_draft_requires_explicit_rebase(owned):
    actor, store, project = owned
    store.apply_application(
        project,
        uid(),
        {
            "type": "draft.save",
            "editor": "query-workspace-v1",
            "expectedGeneration": 0,
            "boundDomainRevision": 0,
            "content": query_content(),
        },
        actor=uid(),
        permission="write",
    )
    _, copied = apply(actor, project, {"kind": "copy-current", "name": "with draft"})
    draft = store.project_checkpoint(copied["targetProjectId"])["application"]["drafts"][0]
    assert draft["generation"] == draft["bound_revision"] == 1
    assert draft["payload"] == canonical(query_content()) and draft["content_hash"] == digest(
        query_content()
    )
    store.commit(
        project, 0, uid(), uid(), definitions=[{"layer": "query", "id": "new", "value": {}}]
    )
    reply = exchange(
        actor,
        "project.management.preview",
        {
            "projectId": project,
            "action": {"kind": "copy-current", "name": "stale"},
            "expectedCheckpointRef": digest(store.project_checkpoint(project)),
            "expectedLifecycleVersion": 0,
        },
    )
    assert not reply["ok"] and reply["error"]["code"] == "INVALID_STATE"


def test_trash_revokes_prior_persistent_confirmation_but_preserves_historical_proof(owned):
    actor, store, project = owned
    actor_id = uid()
    change = {"type": "metadata", "expectedVersion": 1, "patch": {"name": "confirmed"}}
    prepared = store.prepare_application(project, change, actor=actor_id, permission="write")
    operation = uid()
    old_receipt = store.apply_application(
        project,
        operation,
        change,
        actor=actor_id,
        permission="write",
        prepared_plan_ref=prepared["preparedPlanRef"],
        confirmation_ref=prepared["confirmationRef"],
    )
    pending_change = {
        "type": "metadata",
        "expectedVersion": 2,
        "patch": {"name": "must not revive"},
    }
    pending = store.prepare_application(project, pending_change, actor=actor_id, permission="write")
    apply(actor, project, {"kind": "trash"})
    format3.validate(store)
    store._validate_job3()
    apply(actor, project, {"kind": "restore-trash"})
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    with pytest.raises(Conflict):
        store.apply_application(
            project,
            uid(),
            pending_change,
            actor=actor_id,
            permission="write",
            prepared_plan_ref=pending["preparedPlanRef"],
            confirmation_ref=pending["confirmationRef"],
        )
    # This is historical exact operation replay, not a new use of the revoked grant.
    assert (
        store.apply_application(
            project,
            operation,
            change,
            actor=actor_id,
            permission="write",
            prepared_plan_ref=prepared["preparedPlanRef"],
            confirmation_ref=prepared["confirmationRef"],
        )
        == old_receipt
    )
    format3.validate(store)


def test_management_cursor_binding_expiry_and_old_selection(owned):
    actor, store, project = owned
    apply(actor, project, {"kind": "copy-current", "name": "second"})
    first = exchange(
        actor, "project.management.catalog", {"state": "active", "pageSize": 1, "cursor": None}
    )
    assert first["ok"] and first["result"]["nextCursor"]
    token = first["result"]["nextCursor"]
    bad = exchange(
        actor, "project.management.catalog", {"state": "archived", "pageSize": 1, "cursor": token}
    )
    assert not bad["ok"] and bad["error"]["code"] == "CURSOR_MISMATCH"
    second = exchange(
        actor, "project.management.catalog", {"state": "active", "pageSize": 1, "cursor": token}
    )
    assert second["ok"] and second["result"]["offset"] == 1
    replay = exchange(
        actor, "project.management.catalog", {"state": "active", "pageSize": 1, "cursor": token}
    )
    assert not replay["ok"]
    pending = prepare(actor, project, {"kind": "rename", "name": "late"})
    target = second["result"]["items"][0]["projectId"]
    if target == project:
        target = first["result"]["items"][0]["projectId"]
    assert exchange(actor, "project.open", {"projectId": target})["ok"]
    denied = exchange(actor, "project.management.apply", pending)
    assert not denied["ok"] and denied["error"]["code"] == "PERMISSION_DENIED"
    assert exchange(actor, "project.open", {"projectId": project})["ok"]
    pending = prepare(actor, project, {"kind": "rename", "name": "expired"})
    store.now_ms = lambda: 9999999999999
    denied = exchange(actor, "project.management.apply", pending)
    assert not denied["ok"]


def test_library_status_and_trash_reject_unfinished_jobs(owned):
    actor, store, project = owned
    from test_mainline_dispatch import confirmed_job

    confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 0,
            "intent": "change",
            "plan": {
                "manual": [
                    {
                        "id": digest(["urn:pending", "urn:p", '"value"']),
                        "subject": "urn:pending",
                        "predicate": "urn:p",
                        "object": '"value"',
                    }
                ]
            },
        },
    )
    status = exchange(actor, "project.library.status", {})
    assert status["ok"] and status["result"]["activeJobs"] == 1
    params = prepare(actor, project, {"kind": "trash"})
    denied = exchange(actor, "project.management.apply", params)
    assert not denied["ok"] and denied["error"]["code"] == "INVALID_STATE"
    assert management.lifecycle(store, project) == {"state": "active", "version": 0}


def test_lifecycle_authorization_is_funded_once_per_original_synchronous_reply(owned):
    from ontolearn_engine.job_store import JobFault
    from test_mainline_dispatch import frame

    actor, store, project = owned
    host = actor.mainline
    for _ in range(2):
        request = frame(
            actor, "project.read", {"projectId": project, "editor": "query-workspace-v1"}
        )
        host.begin(request)
        trace = []
        store._db.set_trace_callback(trace.append)
        try:
            for _ in range(500):
                host.authorize({"projectId": project})
            assert sum("SELECT state,version FROM project_lifecycle" in sql for sql in trace) == 1
            assert host.current.lifecycle_checked == (
                project,
                host.generation,
                canonical(host.selected_lifecycle),
            )
            # No old-frame cache is usable after selection generation changes.
            original = host.generation
            host.generation += 1
            try:
                with pytest.raises(JobFault) as error:
                    host.authorize({"projectId": project})
                assert error.value.code == "PERMISSION_DENIED"
            finally:
                host.generation = original
        finally:
            store._db.set_trace_callback(None)
            actor.finish_query_reply(request["id"], emitted=True)
    # The owner lease prevents a second approved writer while the synchronous
    # frame runs. Background tasks tick only after Coordinator.request returns.
    with pytest.raises(format3.Format3Fault) as error:
        JobStore(store.path, contract=CONTRACT, target_format=3)
    assert error.value.category == "leaseBusy"
