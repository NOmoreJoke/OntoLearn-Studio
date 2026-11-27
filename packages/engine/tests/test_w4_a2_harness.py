"""Shared W4-A2 test harness: owned business3 runtime with real project material.

Builds a real project whose ontology catalog (OWL class/property declarations)
and asserted facts ride the ordinary ChangeSet machinery, then drives the
behavior/scenario/report wire methods through the full coordinator dispatch
path. No mock Store, no stubbed planner: the same single writer the desktop
main process owns.
"""

from contextlib import contextmanager
from uuid import uuid4

from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
OWL = "http://www.w3.org/2002/07/owl#"
XSD_INTEGER = "http://www.w3.org/2001/XMLSchema#integer"

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


@contextmanager
def runtime(tmp_path):
    """Owned business3 runtime factory; each test file wraps its own fixture."""
    store = JobStore(tmp_path / "w4a2.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    try:
        assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        yield actor, store
    finally:
        actor.mainline.close()
        store.close()


def open_blank(actor, name="行为沙盘项目"):
    created = ok(
        exchange(
            actor,
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": name,
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


ONTOLOGY_TRIPLES = [
    {"subject": "urn:test:Equipment", "predicate": RDF_TYPE, "object": "<" + OWL + "Class>"},
    {"subject": "urn:test:WorkOrder", "predicate": RDF_TYPE, "object": "<" + OWL + "Class>"},
    {
        "subject": "urn:test:status",
        "predicate": RDF_TYPE,
        "object": "<" + OWL + "DatatypeProperty>",
    },
    {
        "subject": "urn:test:level",
        "predicate": RDF_TYPE,
        "object": "<" + OWL + "DatatypeProperty>",
    },
    {
        "subject": "urn:test:status",
        "predicate": RDF_TYPE,
        "object": "<" + OWL + "FunctionalProperty>",
    },
    {
        "subject": "urn:test:level",
        "predicate": RDF_TYPE,
        "object": "<" + OWL + "FunctionalProperty>",
    },
    {
        "subject": "urn:test:equipment",
        "predicate": RDF_TYPE,
        "object": "<" + OWL + "ObjectProperty>",
    },
]

FORMAL_FACTS = [
    {
        "id": digest(["urn:test:eq1", RDF_TYPE, "<urn:test:Equipment>"]),
        "subject": "urn:test:eq1",
        "predicate": RDF_TYPE,
        "object": "<urn:test:Equipment>",
    },
    {
        "id": digest(["urn:test:eq1", "urn:test:status", '"在线"']),
        "subject": "urn:test:eq1",
        "predicate": "urn:test:status",
        "object": '"在线"',
    },
    {
        "id": digest(["urn:test:wo1", RDF_TYPE, "<urn:test:WorkOrder>"]),
        "subject": "urn:test:wo1",
        "predicate": RDF_TYPE,
        "object": "<urn:test:WorkOrder>",
    },
    {
        "id": digest(["urn:test:wo1", "urn:test:equipment", "<urn:test:eq1>"]),
        "subject": "urn:test:wo1",
        "predicate": "urn:test:equipment",
        "object": "<urn:test:eq1>",
    },
    {
        "id": digest(["urn:test:wo1", "urn:test:level", f'"2"^^<{XSD_INTEGER}>']),
        "subject": "urn:test:wo1",
        "predicate": "urn:test:level",
        "object": f'"2"^^<{XSD_INTEGER}>',
    },
    {
        "id": digest(["urn:test:wo1", "urn:test:status", '"待处理"']),
        "subject": "urn:test:wo1",
        "predicate": "urn:test:status",
        "object": '"待处理"',
    },
    {
        "id": digest(["urn:test:wo2", "urn:test:status", '"待处理"']),
        "subject": "urn:test:wo2",
        "predicate": "urn:test:status",
        "object": '"待处理"',
    },
]


def commit_changeset(actor, store, project, plan):
    """Ordinary preview -> diff -> confirm -> commit over the real Store."""
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


def prepared_project(actor, store):
    """A project with a real ontology catalog and asserted formal facts."""
    project = open_blank(actor)
    commit_changeset(
        actor,
        store,
        project,
        {
            "definitions": [
                {
                    "layer": "ontology",
                    "id": "w4a2-catalog",
                    "value": {"triples": ONTOLOGY_TRIPLES},
                }
            ],
            "manual": FORMAL_FACTS,
        },
    )
    internal = store._project(project)
    return project, store.revision(internal), digest(store._snapshot_projection(internal))


def binding(project, revision, snapshot_id, *, behavior_version="bv-1", scope_id=None):
    return {
        "projectId": project,
        "baseRevision": revision,
        "inputSnapshotId": snapshot_id,
        "behaviorVersion": behavior_version,
        "scopeId": scope_id or uid(),
        "requestId": uid(),
    }


def before_run(actor, project, operation, base_revision, *, domain):
    return exchange(
        actor,
        "project.run.before_commit",
        {
            "projectId": project,
            "operationId": operation,
            "domain": domain,
            "baseRevision": base_revision,
            "label": None,
        },
    )


def value(kind, raw):
    return {"kind": kind, "value": raw}


def expression_value(kind, raw):
    return {"kind": "value", "value": value(kind, raw)}


def sample_draft(**overrides):
    draft = {
        "id": "urn:test:behavior:escalate",
        "name": "升级工单",
        "description": "测试行为",
        "effect": "修改隔离副本",
        "trigger": {"eventType": "alarm.raised"},
        "enabled": True,
        "priority": 1,
        "version": 1,
        "conditions": [
            {
                "op": "type",
                "subject": {"kind": "eventField", "field": "equipmentId"},
                "classId": "urn:test:Equipment",
            }
        ],
        "actions": [
            {
                "kind": "set",
                "subject": {"kind": "eventField", "field": "equipmentId"},
                "property": "urn:test:level",
                "value": expression_value("number", 5),
            }
        ],
    }
    draft.update(overrides)
    return draft


def sample_event(**overrides):
    event = {
        "id": "urn:test:event:1",
        "type": "alarm.raised",
        "sequence": 0,
        "version": 1,
        "payload": {"equipmentId": "urn:test:eq1"},
        "edits": [{"kind": "declare", "object": "urn:test:eq1"}],
    }
    event.update(overrides)
    return event


def run_behavior(
    actor,
    project,
    revision,
    snapshot_id,
    *,
    draft=None,
    events=None,
    operation=None,
    bind=None,
    scope_id=None,
    behavior_version="bv-1",
):
    operation = operation or uid()
    bind = bind or binding(
        project, revision, snapshot_id, behavior_version=behavior_version, scope_id=scope_id
    )
    return exchange(
        actor,
        "project.behavior.run",
        {
            "projectId": project,
            "operationId": operation,
            "runId": uid(),
            "scope": "sample",
            "binding": bind,
            "draft": draft or sample_draft(),
            "events": events or [sample_event()],
        },
    )


def scenario_configuration(**overrides):
    configuration = {
        "name": "基础沙盘",
        "maxRounds": 2,
        "capacity": {"mode": "direct", "direct": 1},
        "events": [
            {"id": "E1", "round": 1, "sequence": 1, "payload": {"kind": "工单"}},
            {"id": "E2", "round": 2, "sequence": 2, "payload": {"kind": "工单"}},
        ],
        "initialEdits": [],
        "parameters": {"站点": "一号"},
        "source": "人工假设",
        "assumptions": ["产能恒定"],
        "ruleVersion": "r1",
        "behaviorVersion": "b1",
    }
    configuration.update(overrides)
    return configuration


def create_scenario(actor, project, revision, snapshot_id, *, configuration=None, operation=None):
    return exchange(
        actor,
        "project.scenario.create",
        {
            "projectId": project,
            "projectVersion": revision,
            "inputSnapshotId": snapshot_id,
            "operationId": operation or uid(),
            "configuration": configuration or scenario_configuration(),
        },
    )
