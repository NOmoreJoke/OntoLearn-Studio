"""``project.run.before_commit`` over the real owned business3 runtime (W4-A1).

Covers the Stage 1 before-run snapshot contract: durable ``before-run``
checkpoint minting through the ordinary application ledger, idempotent replay
of one ``operationId`` bound to ``(projectId, domain, baseRevision, label)``,
deterministic conflict rejection on any parameter drift, the domainRevision
CAS guard, cross-project operation binding, and the untouched public
``project.checkpoint.create`` manual-only contract (full regression in
test_b1b_project_restore.py).
"""

import json
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT

LIMITS = {
    "startupMs": 10000,
    "handshakeMs": 5000,
    "requestMs": 5000,
    "heartbeatMs": 10000,
    "cancelGraceMs": 5000,
    "totalMs": 120000,
    "maxFrameBytes": 262144,
    "maxQueuedJobs": 32,
    "maxConcurrentJobs": 2,
    "maxPageItems": 100,
    "maxPageBytes": 131072,
    "maxWorkerMemoryBytes": 536870912,
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
    store = JobStore(tmp_path / "run.sqlite", contract=CONTRACT, target_format=3)
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
                "name": "运行前项目",
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


def before_run(actor, project, operation, base_revision, *, domain, label=None):
    return exchange(
        actor,
        "project.run.before_commit",
        {
            "projectId": project,
            "operationId": operation,
            "domain": domain,
            "baseRevision": base_revision,
            "label": label,
        },
    )


def commit_manual_fact(actor, store, project):
    from ontolearn_engine.storage import digest

    host = {"host_client_id": actor.host_client_id, "engine_session_id": actor.session}
    base = store.project_get(project)["projectRevision"]
    plan = {
        "manual": [
            {
                "id": digest(["urn:x:run", "urn:x:p", '"v"']),
                "subject": "urn:x:run",
                "predicate": "urn:x:p",
                "object": '"v"',
            }
        ]
    }
    ready = store.preview_changeset(
        project,
        base,
        {"projectId": project, "baseRevision": base, "intent": "change", "plan": plan},
        limits=LIMITS,
        **host,
    )
    assert ready["status"] == "ready", ready
    token = None
    while True:
        page = store.changeset_diff_page(
            project,
            ready["previewHash"],
            ready["manifest"]["documentKind"],
            200,
            token,
            limits=LIMITS,
            **host,
        )
        token = page["nextCursor"]
        if page["complete"]:
            break
    confirmed = store.confirm_changeset(project, ready["previewHash"], token, **host)
    job = store.create_changeset_job(
        project,
        uid(),
        {
            "inputSnapshotId": confirmed["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmed["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmed["preparedPlanRef"],
        },
        confirmed["confirmationRef"],
        {
            "engineVersion": "0.1.0",
            "executionSemanticsVersion": "changeset-v1",
            "dependencyLockHash": "a" * 64,
        },
        LIMITS,
        **host,
    )
    store.start_job(job["jobId"])
    done = store.commit_job(job["jobId"])
    assert done["state"] == "succeeded", done


def test_before_run_checkpoint_mints_durable_receipt(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    marked = ok(before_run(actor, project, uid(), revision, domain="behavior", label="沙盘运行前"))
    assert marked["runBeforeCommitVersion"] == 1
    assert marked["reason"] == "before-run"
    assert marked["domainRevision"] == revision
    assert marked["checkpointRef"]
    listing = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    top = listing["items"][0]
    assert top["checkpointRef"] == marked["checkpointRef"]
    assert top["reason"] == "before-run" and top["label"] == "沙盘运行前"


def test_idempotent_replay_returns_existing_receipt(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    operation = uid()
    first = ok(before_run(actor, project, operation, revision, domain="scenario"))
    before_listing = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    second = ok(before_run(actor, project, operation, revision, domain="scenario", label=None))
    assert second == first
    after_listing = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    assert after_listing == before_listing  # no duplicate snapshot on replay


@pytest.mark.parametrize(
    "mutation",
    [
        {"domain": "behavior"},
        {"baseRevision": 99},
        {"label": "不同标签"},
    ],
)
def test_conflicting_replay_rejects_deterministically(owned, mutation):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="scenario", label="原标签"))
    request = {
        "projectId": project,
        "operationId": operation,
        "domain": "scenario",
        "baseRevision": revision,
        "label": "原标签",
    }
    request.update(mutation)
    denied(exchange(actor, "project.run.before_commit", request), "IDENTITY_CONFLICT")


def test_base_revision_cas_guard(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    denied(before_run(actor, project, uid(), revision + 1, domain="behavior"), "REVISION_CONFLICT")
    ok(before_run(actor, project, uid(), revision, domain="behavior"))
    commit_manual_fact(actor, store, project)
    denied(before_run(actor, project, uid(), revision, domain="behavior"), "REVISION_CONFLICT")


def test_operation_id_is_bound_to_its_project(owned):
    actor, _ = owned
    first = open_blank(actor)
    operation = uid()
    claimed = ok(before_run(actor, first, operation, 0, domain="behavior"))
    assert claimed["projectId"] == first
    second = open_blank(actor)
    denied(before_run(actor, second, operation, 0, domain="behavior"), "IDENTITY_CONFLICT")


def store_revision(actor, project):
    return actor.store.revision(actor.store._project(project))


def test_wire_checkpoint_create_still_mints_manual_only(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    ok(before_run(actor, project, uid(), revision, domain="behavior"))
    created = ok(
        exchange(
            actor,
            "project.checkpoint.create",
            {"projectId": project, "operationId": uid(), "label": "手动"},
        )
    )
    assert created["reason"] == "manual"
    listing = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    assert [item["reason"] for item in listing["items"]][:3] == [
        "manual",
        "before-run",
        "operation",
    ]


def test_restored_before_run_checkpoint_rolls_domain_back(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    marked = ok(before_run(actor, project, uid(), revision, domain="behavior", label="回滚锚点"))
    commit_manual_fact(actor, store, project)
    state = ok(exchange(actor, "project.management.read", {"projectId": project}))
    preview = ok(
        exchange(
            actor,
            "project.restore.preview",
            {
                "projectId": project,
                "targetCheckpointRef": marked["checkpointRef"],
                "expectedCheckpointRef": state["checkpointRef"],
                "expectedLifecycleVersion": state["lifecycle"]["version"],
            },
        )
    )
    hashes, cursor = [], None
    while True:
        page = ok(
            exchange(
                actor,
                "project.restore.page",
                {"projectId": project, "previewRef": preview["previewRef"], "cursor": cursor},
            )
        )
        hashes.extend(segment["sha256"] for segment in page["segments"])
        cursor = page["nextCursor"]
        if cursor is None:
            assert page["complete"]
            break
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
    restored = ok(
        exchange(
            actor,
            "project.restore.apply",
            {
                "projectId": project,
                "operationId": uid(),
                "confirmationRef": confirmation["confirmationRef"],
                "documentHash": preview["documentHash"],
            },
        )
    )
    assert restored["restoredFromCheckpointRef"] == marked["checkpointRef"]
    facts = store.state(store._project(project))["facts"]
    assert all(fact["subject"] != "urn:x:run" for fact in facts)
    assert json.loads(json.dumps(restored))["domainRevision"] > revision


def test_receipt_persists_across_reopen(owned, tmp_path):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    operation = uid()
    first = ok(before_run(actor, project, operation, revision, domain="behavior"))
    actor.mainline.close()
    store.close()
    reopened_store = JobStore(tmp_path / "run.sqlite", contract=CONTRACT, target_format=3)
    reopened = Coordinator(reopened_store, profile="business3", _ready=_JOB_READY)
    try:
        assert exchange(reopened, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        ok(exchange(reopened, "project.open", {"projectId": project}))
        replay = ok(before_run(reopened, project, operation, revision, domain="behavior"))
        assert replay == first
    finally:
        reopened.mainline.close()
        reopened_store.close()
    assert Path(str(tmp_path / "run.sqlite")).exists()
