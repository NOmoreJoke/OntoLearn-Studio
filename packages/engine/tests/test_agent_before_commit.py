"""``project.agent.before_commit`` over the real owned business3 runtime.

Covers the before-agent snapshot contract: recoverable checkpoint minting with
a full project.restore rollback, the domainRevision CAS guard, idempotent
same-operationId replay without duplicate snapshots, identity conflicts, and
the PRD §11.2 rule that agent-completed learning work never counts as an
independent transfer success even after a genuinely passing task check. The
full-assistance marking itself is only *staged* by before_commit and lands
inside the linked ChangeSet's commit transaction: an unsubmitted, failed or
superseded ChangeSet leaves every attempt independent (B05). The public
manual-only ``project.checkpoint.create`` contract stays untouched (guarded
by test_b1b_project_restore.py in the same required run).
"""

import json
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import learning_agent
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest

ROOT = Path(__file__).resolve().parents[3]
G_BASE = json.loads(
    (ROOT / "tests/fixtures/product-baselines/G-base.json").read_text(encoding="utf-8")
)
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
IMPL = {
    "engineVersion": "0.1.0",
    "executionSemanticsVersion": "changeset-v1",
    "dependencyLockHash": "a" * 64,
}
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
# The frozen course target beyond G-base: Person modelled as a class, the
# assignedTo object property, one individual and one assignment assertion.
LESSON_TRIPLES = [
    {
        "subject": "urn:ontolearn:learning:Person",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#Class>",
    },
    {
        "subject": "urn:ontolearn:learning:assignedTo",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#ObjectProperty>",
    },
    {
        "subject": "urn:ontolearn:learning:person/L01",
        "predicate": RDF_TYPE,
        "object": "<urn:ontolearn:learning:Person>",
    },
    {
        "subject": "urn:ontolearn:learning:equipment/001",
        "predicate": "urn:ontolearn:learning:assignedTo",
        "object": "<urn:ontolearn:learning:person/L01>",
    },
]


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
    store = JobStore(tmp_path / "agent.sqlite", contract=CONTRACT, target_format=3)
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
                "name": "Agent 项目",
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


def g_base_and_lesson_plan():
    ontology = [
        {"subject": t["subject"], "predicate": t["predicate"], "object": t["object"]}
        for t in G_BASE["ontology"]
    ]
    facts = list(G_BASE["facts"]) + LESSON_TRIPLES
    manual = [
        {
            "id": digest([t["subject"], t["predicate"], t["object"]]),
            "subject": t["subject"],
            "predicate": t["predicate"],
            "object": t["object"],
        }
        for t in facts
    ]
    return {
        "definitions": [
            {
                "layer": "ontology",
                "id": "G",
                "value": {
                    "triples": ontology,
                    "singleValuedPredicates": [],
                    "references": [],
                },
            }
        ],
        "manual": manual,
    }


def commit_plan(actor, store, project, plan, operation=None):
    host = {"host_client_id": actor.host_client_id, "engine_session_id": actor.session}
    base = store.project_get(project)["projectRevision"]
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
        operation or uid(),
        {
            "inputSnapshotId": confirmed["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "changeset",
            "parametersHash": confirmed["parametersHash"],
            "derivedResultIds": [],
            "preparedPlanRef": confirmed["preparedPlanRef"],
        },
        confirmed["confirmationRef"],
        IMPL,
        LIMITS,
        **host,
    )
    store.start_job(job["jobId"])
    done = store.commit_job(job["jobId"])
    assert done["state"] == "succeeded", done


def before_commit(actor, project, operation, base_revision, *, full, task_ids=None, label=None):
    params = {
        "projectId": project,
        "operationId": operation,
        "baseRevision": base_revision,
        "recordFullAssistance": full,
        "label": label,
    }
    if task_ids is not None:
        params["taskIds"] = task_ids
    return exchange(actor, "project.agent.before_commit", params)


def read_restore_document(actor, project, preview):

    hashes, cursor = [], None
    while True:
        page = ok(
            exchange(
                actor,
                "project.restore.page",
                {"projectId": project, "previewRef": preview["previewRef"], "cursor": cursor},
            )
        )
        for segment in page["segments"]:
            hashes.append(segment["sha256"])
        cursor = page["nextCursor"]
        if cursor is None:
            assert page["complete"]
            break
    return hashes


def test_before_agent_checkpoint_and_full_restore_rollback(owned):
    actor, store = owned
    project = open_blank(actor)
    commit_plan(actor, store, project, g_base_and_lesson_plan())
    revision = store.revision(store._project(project))

    marked = ok(before_commit(actor, project, uid(), revision, full=False, label="代做之前"))
    assert marked["agentBeforeCommitVersion"] == 1
    assert marked["reason"] == "before-agent"
    assert marked["domainRevision"] == revision
    assert marked["assistanceUpdatedTaskIds"] == []
    listing = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    top = listing["items"][0]
    assert top["checkpointRef"] == marked["checkpointRef"]
    assert top["reason"] == "before-agent" and top["label"] == "代做之前"

    # A later committed ChangeSet moves the domain head past the snapshot.
    commit_plan(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": digest(["urn:x:later", "urn:x:p", '"after"']),
                    "subject": "urn:x:later",
                    "predicate": "urn:x:p",
                    "object": '"after"',
                }
            ]
        },
    )
    assert store.revision(store._project(project)) == revision + 1

    # Full restore rolls the project back to the before-agent checkpoint.
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
    confirmation = ok(
        exchange(
            actor,
            "project.restore.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
                "readSegmentHashes": read_restore_document(actor, project, preview),
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
    # The compensating restore appends a new domain revision whose content
    # equals the before-agent snapshot: the later ChangeSet is rolled back.
    assert restored["domainRevision"] > revision
    facts = store.state(store._project(project))["facts"]
    assert all(fact["subject"] != "urn:x:later" for fact in facts)
    assert len(facts) == len(G_BASE["facts"]) + len(LESSON_TRIPLES)


def test_base_revision_cas_guard(owned):
    actor, _ = owned
    project = open_blank(actor)
    denied(
        before_commit(actor, project, uid(), 99, full=False),
        "REVISION_CONFLICT",
    )
    current = ok(exchange(actor, "project.get", {"projectId": project}))["projectRevision"]
    result = ok(before_commit(actor, project, uid(), current, full=False))
    assert result["domainRevision"] == current
    denied(before_commit(actor, project, uid(), current + 1, full=False), "REVISION_CONFLICT")


def test_same_operation_replay_is_idempotent(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    operation = uid()
    first = ok(before_commit(actor, project, operation, revision, full=False, label="幂等"))
    after_first = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    second = ok(before_commit(actor, project, operation, revision, full=False, label="幂等"))
    assert first == second
    # The mixed ledger (creation operation, genesis, one before-agent entry)
    # is byte-identical after replay: no duplicate snapshot was minted.
    after_second = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    assert after_second == after_first
    assert [item["reason"] for item in after_second["items"]] == [
        "before-agent",
        "operation",
        "genesis",
    ]
    # Cross-parameter reuse of the same operationId is an identity conflict.
    denied(
        before_commit(actor, project, operation, revision, full=True, label="幂等"),
        "IDENTITY_CONFLICT",
    )


def test_operation_id_belongs_to_its_project(owned):
    actor, _ = owned
    first = open_blank(actor)
    revision = 0
    operation = uid()
    claimed = ok(before_commit(actor, first, operation, revision, full=False))
    assert claimed["projectId"] == first
    second = open_blank(actor)
    denied(
        before_commit(actor, second, operation, 0, full=False),
        "IDENTITY_CONFLICT",
    )


def task_view(actor, project, task_id):
    reading = ok(exchange(actor, "project.learning.read", {"projectId": project}))
    return next(item for item in reading["tasks"] if item["taskId"] == task_id)


def start_attempt(actor, project, task_id):
    started = ok(
        exchange(
            actor,
            "project.learning.attempt.start",
            {"projectId": project, "taskId": task_id, "operationId": uid()},
        )
    )
    assert started["learningState"]["assistance"] == "independent"


def test_full_assistance_never_counts_as_independent_transfer(owned):
    actor, store = owned
    project = open_blank(actor)
    commit_plan(actor, store, project, g_base_and_lesson_plan())
    start_attempt(actor, project, "business-ontology")

    # The before-agent call only stages the marking: no attempt is touched
    # until the linked ChangeSet actually commits (B05).
    revision = store.revision(store._project(project))
    changeset_op = uid()
    marked = ok(
        before_commit(
            actor,
            project,
            learning_agent.derive_before_commit_op(changeset_op),
            revision,
            full=True,
            task_ids=["business-ontology"],
            label="Agent 完整代做",
        )
    )
    assert marked["assistanceUpdatedTaskIds"] == []
    staged = task_view(actor, project, "business-ontology")
    assert staged["assistance"] == "independent"

    commit_plan(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": digest(
                        [
                            "urn:ontolearn:learning:Person",
                            "http://www.w3.org/2000/01/rdf-schema#comment",
                            '"Agent 完整代做"',
                        ]
                    ),
                    "subject": "urn:ontolearn:learning:Person",
                    "predicate": "http://www.w3.org/2000/01/rdf-schema#comment",
                    "object": '"Agent 完整代做"',
                }
            ]
        },
        operation=changeset_op,
    )
    marked_task = task_view(actor, project, "business-ontology")
    assert marked_task["assistance"] == "agent-full-assistance"
    assert marked_task["checkStatus"] == "rerun-required"
    assert marked_task["independentTransferSuccess"] is False
    assert marked_task["operationComplete"] is False

    # A genuinely passing check afterwards still never mints an independent
    # transfer success (PRD §11.2: Agent 完整代做不计入独立迁移成功).
    checked = ok(
        exchange(
            actor,
            "project.learning.task.check",
            {"projectId": project, "taskId": "business-ontology", "operationId": uid()},
        )
    )
    assert checked["checkStatus"] == "passed", checked["feedback"]
    assert checked["operationComplete"] is True
    assert checked["independentTransferSuccess"] is False
    assert checked["assistance"] == "agent-full-assistance"


def test_pending_assistance_never_lands_without_the_linked_changeset(owned):
    actor, store = owned
    project = open_blank(actor)
    commit_plan(actor, store, project, g_base_and_lesson_plan())
    for task_id in ("business-ontology", "transfer-repair", "transfer-classify"):
        start_attempt(actor, project, task_id)

    revision = store.revision(store._project(project))
    changeset_op = uid()
    marked = ok(
        before_commit(
            actor,
            project,
            learning_agent.derive_before_commit_op(changeset_op),
            revision,
            full=True,
            task_ids=["business-ontology", "transfer-repair"],
        )
    )
    assert marked["assistanceUpdatedTaskIds"] == []
    # No ChangeSet was submitted at all: every attempt stays independent.
    for task_id in ("business-ontology", "transfer-repair", "transfer-classify"):
        assert task_view(actor, project, task_id)["assistance"] == "independent"

    # A different (user) ChangeSet commits first and moves the domain head:
    # the staged marking is bound to the original baseRevision and never lands.
    commit_plan(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": digest(["urn:x:user", "urn:x:p", '"manual"']),
                    "subject": "urn:x:user",
                    "predicate": "urn:x:p",
                    "object": '"manual"',
                }
            ]
        },
    )
    for task_id in ("business-ontology", "transfer-repair", "transfer-classify"):
        assert task_view(actor, project, task_id)["assistance"] == "independent"


def test_targeted_assistance_marks_only_named_attempts_and_persists(owned, tmp_path):
    actor, store = owned
    project = open_blank(actor)
    commit_plan(actor, store, project, g_base_and_lesson_plan())
    for task_id in ("business-ontology", "transfer-repair", "transfer-classify"):
        start_attempt(actor, project, task_id)

    revision = store.revision(store._project(project))
    changeset_op = uid()
    marked = ok(
        before_commit(
            actor,
            project,
            learning_agent.derive_before_commit_op(changeset_op),
            revision,
            full=True,
            task_ids=["business-ontology", "transfer-repair"],
            label="Agent 完整代做",
        )
    )
    assert marked["assistanceUpdatedTaskIds"] == []

    commit_plan(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": digest(
                        [
                            "urn:ontolearn:learning:Person",
                            "http://www.w3.org/2000/01/rdf-schema#comment",
                            '"Agent 完整代做"',
                        ]
                    ),
                    "subject": "urn:ontolearn:learning:Person",
                    "predicate": "http://www.w3.org/2000/01/rdf-schema#comment",
                    "object": '"Agent 完整代做"',
                }
            ]
        },
        operation=changeset_op,
    )
    for task_id in ("business-ontology", "transfer-repair"):
        task = task_view(actor, project, task_id)
        assert task["assistance"] == "agent-full-assistance", task_id
        assert task["independentTransferSuccess"] is False
        assert task["operationComplete"] is False
        assert task["checkStatus"] == "rerun-required"
    # The untargeted transfer-classify attempt is strictly untouched.
    untouched = task_view(actor, project, "transfer-classify")
    assert untouched["assistance"] == "independent"
    assert untouched["operationComplete"] is False

    # Close the SQLite file and reopen: the marking is fully persisted.
    actor.mainline.close()
    store.close()
    reopened_store = JobStore(tmp_path / "agent.sqlite", contract=CONTRACT, target_format=3)
    reopened = Coordinator(reopened_store, profile="business3", _ready=_JOB_READY)
    try:
        assert exchange(reopened, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        ok(exchange(reopened, "project.open", {"projectId": project}))
        for task_id in ("business-ontology", "transfer-repair"):
            task = next(
                item
                for item in ok(exchange(reopened, "project.learning.read", {"projectId": project}))[
                    "tasks"
                ]
                if item["taskId"] == task_id
            )
            assert task["assistance"] == "agent-full-assistance", task_id
            assert task["independentTransferSuccess"] is False
        classify = next(
            item
            for item in ok(exchange(reopened, "project.learning.read", {"projectId": project}))[
                "tasks"
            ]
            if item["taskId"] == "transfer-classify"
        )
        assert classify["assistance"] == "independent"
    finally:
        reopened.mainline.close()
        reopened_store.close()


def test_full_assistance_without_live_attempts_still_snapshots(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    result = ok(
        before_commit(actor, project, uid(), revision, full=True, task_ids=None, label="尚无尝试")
    )
    assert result["assistanceUpdatedTaskIds"] == []
    listing = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 10, "cursor": None}
        )
    )
    assert listing["items"][0]["reason"] == "before-agent"


def test_unknown_task_id_is_rejected(owned):
    actor, _ = owned
    project = open_blank(actor)
    denied(
        before_commit(actor, project, uid(), 0, full=True, task_ids=["not-a-task"]),
        "INVALID_REQUEST",
    )


def test_wire_checkpoint_create_still_mints_manual_only(owned):
    actor, store = owned
    project = open_blank(actor)
    revision = store.revision(store._project(project))
    ok(before_commit(actor, project, uid(), revision, full=False))
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
    assert [item["reason"] for item in listing["items"]] == [
        "manual",
        "before-agent",
        "operation",
        "genesis",
    ]
