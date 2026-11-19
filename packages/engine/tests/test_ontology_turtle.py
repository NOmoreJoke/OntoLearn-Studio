"""FR-203 Turtle export round-trip over the real owned business3 runtime.

Covers the fixed golden sample, export -> import check -> ChangeSet commit into
a fresh blank project -> re-export byte stability, tombstone skipping, the
never-mixed uncommitted draft boundary and the whole-batch rejection of
out-of-scope OWL constructs. No GUI, no worker, no second Store writer.
"""

import json
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest

ROOT = Path(__file__).resolve().parents[3]
GOLDEN = (
    ROOT / "packages/engine/tests/fixtures/ontology_turtle/g_base_export_golden.ttl"
).read_text(encoding="utf-8")
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


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "turtle.sqlite", contract=CONTRACT, target_format=3)
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
                "name": "Turtle 项目",
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


def commit_plan(actor, store, project, plan):
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
        IMPL,
        LIMITS,
        **host,
    )
    store.start_job(job["jobId"])
    done = store.commit_job(job["jobId"])
    assert done["state"] == "succeeded", done


def g_base_plan():
    ontology = [
        {"subject": t["subject"], "predicate": t["predicate"], "object": t["object"]}
        for t in G_BASE["ontology"]
    ]
    manual = [
        {
            "id": digest([t["subject"], t["predicate"], t["object"]]),
            "subject": t["subject"],
            "predicate": t["predicate"],
            "object": t["object"],
        }
        for t in G_BASE["facts"]
    ]
    constraint = {
        "schemaVersion": 1,
        "kind": "constraint",
        "id": "name-required",
        "revision": 1,
        "label": "设备名称必填",
        "enabled": True,
        "targetClass": "urn:ontolearn:learning:Equipment",
        "path": "urn:ontolearn:learning:name",
        "template": "required",
        "parameters": {},
    }
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
            },
            {"layer": "constraint", "id": "name-required", "value": constraint},
        ],
        "manual": manual,
    }


def import_check(actor, project, turtle, fmt="turtle"):
    return ok(
        exchange(
            actor,
            "project.ontology.import.check",
            {
                "projectId": project,
                "baseUri": "urn:ontolearn:import:",
                "turtleText": turtle,
                "format": fmt,
            },
        )
    )


def test_golden_round_trip_is_byte_stable(owned):
    actor, store = owned
    source = open_blank(actor)
    commit_plan(actor, store, source, g_base_plan())
    exported = ok(exchange(actor, "project.ontology.export", {"projectId": source}))
    assert exported["status"] == "ok", exported
    assert exported["turtle"] == GOLDEN
    assert exported["tripleCount"] == 34
    assert exported["projectRevision"] == 1

    # The check plans a legal ChangeSet; committing it into a fresh blank
    # project and re-exporting reproduces the exact same bytes.
    checked = import_check(actor, source, exported["turtle"])
    assert checked["status"] == "ok", checked
    assert checked["summary"]["tripleCount"] == 34
    assert checked["summary"]["definitionCount"] == 2
    assert checked["summary"]["manualFactCount"] == 18
    assert checked["summary"]["baseRevision"] == 1
    constraint = checked["plan"]["definitions"][-1]
    assert constraint["layer"] == "constraint" and constraint["id"] == "name-required"
    assert constraint["value"]["template"] == "required"
    assert constraint["value"]["targetClass"] == "urn:ontolearn:learning:Equipment"

    target = open_blank(actor)
    commit_plan(actor, store, target, checked["plan"])
    reexported = ok(exchange(actor, "project.ontology.export", {"projectId": target}))
    assert reexported["status"] == "ok", reexported
    assert reexported["turtle"] == exported["turtle"]
    assert reexported["tripleCount"] == exported["tripleCount"]
    # Graph isomorphism beyond bytes: identical canonical N3 triple sets.
    from ontolearn_engine.project.ontology_turtle import parse_export_turtle

    left = parse_export_turtle(exported["turtle"], "urn:ontolearn:export:")
    right = parse_export_turtle(reexported["turtle"], "urn:ontolearn:export:")
    assert len(left) == len(right) == 34
    assert {(str(s), str(p), str(o)) for s, p, o in left} == {
        (str(s), str(p), str(o)) for s, p, o in right
    }
    # Deterministic export of the same committed state after reselecting the
    # source project (selection switched to the target while committing).
    ok(exchange(actor, "project.open", {"projectId": source}))
    again = ok(exchange(actor, "project.ontology.export", {"projectId": source}))
    assert again["turtle"] == exported["turtle"]
    assert again["inputSnapshotId"] == exported["inputSnapshotId"]


def test_tombstones_are_skipped_and_drafts_never_leak(owned):
    actor, store = owned
    project = open_blank(actor)
    internal = store._project(project)
    keep = {
        "id": digest(["urn:x:a", "urn:x:p", '"keep"']),
        "subject": "urn:x:a",
        "predicate": "urn:x:p",
        "object": '"keep"',
    }
    drop = {
        "id": digest(["urn:x:a", "urn:x:q", '"drop"']),
        "subject": "urn:x:a",
        "predicate": "urn:x:q",
        "object": '"drop"',
    }
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=[{"layer": "mapping", "id": "M1", "value": {}}],
        mapping={"id": "M1", "rows": [{"row": "r1", "facts": [keep, drop]}]},
    )
    # Managed deletion of an owned fact leaves a tombstone (object NULL).
    store.commit(internal, store.revision(internal), uid(), uid(), remove=[drop["id"]])
    tombstones = [fact for fact in store.state(internal)["facts"] if fact["object"] is None]
    assert len(tombstones) == 1
    # An uncommitted editor draft holds content the export must never mix in.
    store.apply_application(
        project,
        uid(),
        {
            "type": "draft.save",
            "editor": "renderer",
            "expectedGeneration": 0,
            "boundDomainRevision": store.revision(internal),
            "content": {"secret": '<urn:x:draft> <urn:x:p> "draft-only" .'},
        },
        actor=actor.host_client_id,
        permission="write",
    )
    exported = ok(exchange(actor, "project.ontology.export", {"projectId": project}))
    assert exported["status"] == "ok", exported
    assert exported["tripleCount"] == 1
    assert '"keep"' in exported["turtle"]
    assert '"drop"' not in exported["turtle"]
    assert "draft-only" not in exported["turtle"]
    assert "urn:x:draft" not in exported["turtle"]


@pytest.mark.parametrize(
    "construct",
    [
        "http://www.w3.org/2002/07/owl#equivalentClass",
        "http://www.w3.org/2002/07/owl#Restriction",
        "http://www.w3.org/2002/07/owl#propertyChainAxiom",
    ],
)
def test_unsupported_owl_rejects_whole_export(owned, construct):
    actor, store = owned
    project = open_blank(actor)
    plan = {
        "definitions": [
            {
                "layer": "ontology",
                "id": "bad",
                "value": {
                    "triples": [
                        {"subject": "urn:x:keep", "predicate": "urn:x:p", "object": '"fine"'},
                        {
                            "subject": "urn:x:bad",
                            "predicate": construct,
                            "object": "<urn:x:other>",
                        },
                    ],
                    "singleValuedPredicates": [],
                    "references": [],
                },
            }
        ],
        "manual": [],
    }
    commit_plan(actor, store, project, plan)
    rejected = ok(exchange(actor, "project.ontology.export", {"projectId": project}))
    assert rejected["status"] == "rejected", rejected
    assert set(rejected) == {"status", "reasons"}
    codes = {item["code"] for item in rejected["reasons"]}
    assert codes == {"UNSUPPORTED_OWL"}
    for item in rejected["reasons"]:
        assert set(item) == {"code", "field", "detail"}
        assert item["field"] == "owlExpression"
        assert construct in item["detail"]
    # Whole-batch rejection: no partial Turtle is ever produced.
    assert "turtle" not in rejected
    assert '"fine"' not in rejected


def test_non_representable_payload_rejects_whole_export(owned):
    actor, store = owned
    project = open_blank(actor)
    internal = store._project(project)
    # Legacy opaque ontology payloads predate the triples contract; they can
    # only enter through the original Store writer, never a formal ChangeSet.
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=[{"layer": "ontology", "id": "legacy", "value": {"classes": ["Equipment"]}}],
    )
    rejected = ok(exchange(actor, "project.ontology.export", {"projectId": project}))
    assert rejected["status"] == "rejected", rejected
    assert {item["code"] for item in rejected["reasons"]} == {"UNSUPPORTED_RDFS"}
    assert "turtle" not in rejected


def test_export_of_empty_project_is_legal_zero_triples(owned):
    actor, _ = owned
    project = open_blank(actor)
    exported = ok(exchange(actor, "project.ontology.export", {"projectId": project}))
    assert exported["status"] == "ok", exported
    assert exported["tripleCount"] == 0
    assert exported["projectRevision"] == 0
    checked = import_check(actor, project, exported["turtle"])
    assert checked["status"] == "ok", checked
    assert checked["plan"]["definitions"] == []
    assert checked["plan"]["manual"] == []


def test_export_requires_the_selected_project(owned):
    actor, _ = owned
    first = open_blank(actor)
    # project.create auto-selects the newly created project, so the first one
    # is no longer the authorized selection for the export route.
    ok(
        exchange(
            actor,
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": "另一切片",
                "initialization": {"kind": "blank"},
            },
        )
    )
    denied = exchange(actor, "project.ontology.export", {"projectId": first})
    assert not denied["ok"] and denied["error"]["code"] == "PERMISSION_DENIED", denied


def test_golden_document_parses_with_plain_rdflib():
    from rdflib import Graph

    graph = Graph().parse(data=GOLDEN, format="turtle")
    assert len(graph) == 34
    # Canonical Turtle never depends on label identity: two fresh parses agree.
    again = Graph().parse(data=GOLDEN, format="turtle")
    assert {str(t) for t in graph} == {str(t) for t in again}
    assert canonical([str(term) for term in sorted(map(str, graph))])


def allowed_values_plan():
    """Two coexisting allowedValues templates (multi- and single-value lists)."""
    constraint = {
        "schemaVersion": 1,
        "kind": "constraint",
        "id": "level-allowed",
        "revision": 1,
        "label": "等级允许值",
        "enabled": True,
        "targetClass": "urn:x:Equipment",
        "path": "urn:x:level",
        "template": "allowedValues",
        "parameters": {"values": ['"High"', '"Low"']},
    }
    single = {
        "schemaVersion": 1,
        "kind": "constraint",
        "id": "state-allowed",
        "revision": 1,
        "label": "状态允许值",
        "enabled": True,
        "targetClass": "urn:x:Equipment",
        "path": "urn:x:state",
        "template": "allowedValues",
        "parameters": {"values": ['"Medium"']},
    }
    return {
        "definitions": [
            {
                "layer": "ontology",
                "id": "E",
                "value": {
                    "triples": [
                        {
                            "subject": "urn:x:Equipment",
                            "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                            "object": "<http://www.w3.org/2002/07/owl#Class>",
                        }
                    ],
                    "singleValuedPredicates": [],
                    "references": [],
                },
            },
            {"layer": "constraint", "id": "level-allowed", "value": constraint},
            {"layer": "constraint", "id": "state-allowed", "value": single},
        ],
        "manual": [
            {
                "id": digest(["urn:x:e1", "urn:x:level", '"High"']),
                "subject": "urn:x:e1",
                "predicate": "urn:x:level",
                "object": '"High"',
            }
        ],
    }


def test_allowed_values_constraints_export_and_round_trip(owned):
    # B02: sh:in value lists serialize as blank-node rdf lists; the export
    # self-check must accept them (graph isomorphism, not BNode string ids)
    # and the whole document must survive export -> check -> commit -> export.
    actor, store = owned
    source = open_blank(actor)
    commit_plan(actor, store, source, allowed_values_plan())
    exported = ok(exchange(actor, "project.ontology.export", {"projectId": source}))
    assert exported["status"] == "ok", exported
    assert "sh:in" in exported["turtle"]
    assert exported["tripleCount"] == 20

    checked = import_check(actor, source, exported["turtle"])
    assert checked["status"] == "ok", checked
    assert checked["summary"]["tripleCount"] == exported["tripleCount"]
    constraints = [d for d in checked["plan"]["definitions"] if d["layer"] == "constraint"]
    assert {d["id"] for d in constraints} == {"level-allowed", "state-allowed"}
    values = {d["id"]: d["value"]["parameters"]["values"] for d in constraints}
    assert values["level-allowed"] == ['"High"', '"Low"']
    assert values["state-allowed"] == ['"Medium"']

    target = open_blank(actor)
    commit_plan(actor, store, target, checked["plan"])
    reexported = ok(exchange(actor, "project.ontology.export", {"projectId": target}))
    assert reexported["status"] == "ok", reexported
    assert reexported["turtle"] == exported["turtle"]
    assert reexported["tripleCount"] == exported["tripleCount"] == 20


def test_disabled_constraint_round_trip_stays_deactivated(owned):
    # B04: enabled=False must survive the Turtle round-trip through the
    # standard SHACL 1.0 sh:deactivated construct instead of being re-enabled.
    actor, store = owned
    source = open_blank(actor)
    constraint = {
        "schemaVersion": 1,
        "kind": "constraint",
        "id": "name-required",
        "revision": 1,
        "label": "设备名称必填",
        "enabled": False,
        "targetClass": "urn:x:Equipment",
        "path": "urn:x:name",
        "template": "required",
        "parameters": {},
    }
    plan = {
        "definitions": [
            {
                "layer": "ontology",
                "id": "E",
                "value": {
                    "triples": [
                        {
                            "subject": "urn:x:Equipment",
                            "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                            "object": "<http://www.w3.org/2002/07/owl#Class>",
                        }
                    ],
                    "singleValuedPredicates": [],
                    "references": [],
                },
            },
            {"layer": "constraint", "id": "name-required", "value": constraint},
        ],
        "manual": [],
    }
    commit_plan(actor, store, source, plan)
    exported = ok(exchange(actor, "project.ontology.export", {"projectId": source}))
    assert exported["status"] == "ok", exported
    assert "sh:deactivated true" in exported["turtle"]

    checked = import_check(actor, source, exported["turtle"])
    assert checked["status"] == "ok", checked
    imported_constraint = next(
        d for d in checked["plan"]["definitions"] if d["layer"] == "constraint"
    )
    assert imported_constraint["value"]["enabled"] is False

    target = open_blank(actor)
    commit_plan(actor, store, target, checked["plan"])
    # The re-imported constraint stays disabled: quality.prepare prepares zero
    # validation inputs for it and never re-enables the constraint.
    prepared = ok(
        exchange(
            actor,
            "project.quality.prepare",
            {
                "projectId": target,
                "operationId": uid(),
                "selection": {"kind": "current"},
            },
        )
    )
    assert prepared["validationInputs"] == []
    assert prepared["validationInput"] is None
    reexported = ok(exchange(actor, "project.ontology.export", {"projectId": target}))
    assert reexported["status"] == "ok", reexported
    assert reexported["turtle"] == exported["turtle"]
    assert "sh:deactivated true" in reexported["turtle"]


def test_standalone_structural_axiom_lands_in_definition_layer(owned):
    # B11: an rdfs:subClassOf axiom is a schema statement on its own; without
    # any same-batch rdf:type declaration it must still join the definition
    # layer (with its annotations), never the manual fact layer.
    actor, store = owned
    project = open_blank(actor)
    turtle = (
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "<urn:x:Pump> rdfs:subClassOf <urn:x:Equipment> ;\n"
        '    rdfs:label "泵" .\n'
    )
    checked = import_check(actor, project, turtle)
    assert checked["status"] == "ok", checked
    assert checked["summary"]["definitionCount"] == 1
    assert checked["summary"]["manualFactCount"] == 0
    assert checked["summary"]["tripleCount"] == 2
    commit_plan(actor, store, project, checked["plan"])
    exported = ok(exchange(actor, "project.ontology.export", {"projectId": project}))
    assert exported["status"] == "ok", exported
    assert exported["tripleCount"] == 2
    assert "subClassOf" in exported["turtle"]
    assert '"泵"' in exported["turtle"]
