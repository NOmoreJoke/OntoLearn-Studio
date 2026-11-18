"""W3a Sub-batch 1: FR-504/505 quality, two reasoning modes and real B3 checks.

Property sections use stdlib ``random.Random`` with fixed seeds (hypothesis is
not in the offline lockfile): permutation/save-order invariance, round-trip
persistence of the five SHACL templates and the six-operator controlled rules,
idempotency plus stale/retraction isolation. The integration section drives
the real JobStore + Coordinator worker path and the T01 learning ledger for
V-01 / R-01 / R-05 / LX-01, transfer-repair and transfer-classify, including
the FR-004 guard: passing these tasks never mints a guided-stage checkpoint.
"""

import asyncio
import base64
import json
import random
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore, payload_from_rows
from ontolearn_engine.learning.baselines import read_json
from ontolearn_engine.project.mainline import READ_LIMITS
from ontolearn_engine.quality.definitions import (
    DefinitionError,
    compile_constraint_turtle,
    validate_definition,
)
from ontolearn_engine.resources import CONTRACT, LIMITS, semantic_identity
from ontolearn_engine.semantic_execution import execute_request
from ontolearn_engine.storage import digest

ROOT = Path(__file__).resolve().parents[3]
WORKER_TIMEOUT = 60

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
L = "urn:ontolearn:learning:"
G_BASE = read_json(ROOT / "tests/fixtures/product-baselines/G-base.json")
TRANSFER = read_json(ROOT / "content/learning/transfer-inputs.json")

NAME_REQUIRED = {
    "schemaVersion": 1,
    "kind": "constraint",
    "id": "name-required",
    "revision": 1,
    "label": "设备名称必填",
    "enabled": True,
    "targetClass": L + "Equipment",
    "path": L + "name",
    "template": "required",
    "parameters": {},
}
R_RISK_WHEN = [
    ["?equipment", f"<{RDF_TYPE}>", "<urn:ontolearn:learning:Equipment>"],
    ["?equipment", f"<{L}alarm>", "?alarm"],
    ["?alarm", f"<{L}level>", '"High"'],
    ["?alarm", f"<{L}status>", '"Open"'],
]
R_RISK_THEN = ["?equipment", f"<{RDF_TYPE}>", "<urn:ontolearn:learning:HighRiskEquipment>"]


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
    store = JobStore(tmp_path / "w3a.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    yield actor, store
    actor.mainline.close()
    store.close()


def open_blank(actor, name="W3a 质量学习项目"):
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


def fact_rows(facts):
    return [{"id": digest([t["subject"], t["predicate"], t["object"]]), **t} for t in facts]


def commit_state(store, project, *, definitions=(), manual=(), edits=None):
    internal = store._project(project)
    return store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=list(definitions),
        manual=fact_rows(manual),
        edits=edits,
    )


def seed_quality(store, project, *, extra_ontology=(), extra_facts=(), rules=None):
    """G-base plus the legacy R-risk rule and the formal name-required template."""
    ontology = [*G_BASE["ontology"], *extra_ontology]
    definitions = [
        {
            "layer": "ontology",
            "id": "G-base.ontology",
            "value": {
                "triples": ontology,
                "singleValuedPredicates": G_BASE["singleValuedPredicates"],
            },
        },
        {
            "layer": "rule",
            "id": "R-risk",
            "value": {"enabled": True, "when": R_RISK_WHEN, "then": R_RISK_THEN},
        },
        {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
    ]
    for rule in rules or ():
        definitions.append(rule)
    commit_state(
        store,
        project,
        definitions=definitions,
        manual=[*G_BASE["facts"], *extra_facts],
    )


def snapshot_of(store, project):
    internal = store._project(project)
    snapshot = store._snapshot_projection(internal)
    return snapshot, digest(snapshot)


def request_input(snapshot_id, definition="quality-reasoning", scope="asserted"):
    return {
        "inputSnapshotId": snapshot_id,
        "scope": scope,
        "definitionId": definition,
        "parametersHash": "0" * 64,
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }


def run_semantic(store, project, capability, definition="quality-reasoning", scope="asserted"):
    """Real JobStore + worker execution of one semantic job."""
    snapshot_id = store.project_get(project)["inputSnapshotId"]
    input_ = {
        "inputSnapshotId": snapshot_id,
        "scope": scope,
        "definitionId": definition,
        "parametersHash": store.put_blob(project, {"inputSelection": "current"}),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    job = store.create_job(project, uid(), capability, input_, None, semantic_identity(), LIMITS)

    async def drive():
        actor = Coordinator(
            store,
            profile="business3",
            _ready=_JOB_READY,
            test_mode=True,
            allowed_projects={project},
            emit=lambda _message: None,
        )
        actor.version = 3
        actor.session = uid()
        actor.subscriptions[uid()] = {
            "projectId": project,
            "jobId": job["jobId"],
            "stateVersion": job["stateVersion"],
            "seq": 0,
        }
        try:
            actor.queued.append(job["jobId"])
            await actor.tick()
            await asyncio.wait_for(asyncio.gather(*tuple(actor.tasks)), timeout=WORKER_TIMEOUT)
            return store.get_job(project, job["jobId"])
        finally:
            await actor.stop()

    terminal = asyncio.run(drive())
    assert terminal["state"] == "succeeded", terminal.get("error") or terminal
    return terminal


def result_payload(store, job):
    rows = store.result(job["resultRef"]["resultId"])["payload"]
    return payload_from_rows(rows)


# --------------------------------------------------------------------------
# 1. Permutation / save-order invariance (property, fixed seeds).
# --------------------------------------------------------------------------

FORMAL_OPERATOR_RULES = []


def _operator_rule(index, operator, threshold):
    return {
        "layer": "rule",
        "id": f"CMP-{index:02d}-{operator}",
        "value": {
            "schemaVersion": 1,
            "kind": "rule",
            "id": f"CMP-{index:02d}-{operator}",
            "revision": 1,
            "label": f"分数规则 {operator}",
            "enabled": True,
            "conditions": [
                {
                    "kind": "property",
                    "subject": "?e",
                    "path": L + "score",
                    "object": "?v",
                },
                {
                    "kind": "compare",
                    "left": "?v",
                    "operator": operator,
                    "right": f'"{threshold}"^^<http://www.w3.org/2001/XMLSchema#integer>',
                },
            ],
            "conclusions": [
                {"kind": "type", "subject": "?e", "class": L + "Flagged"},
            ],
        },
    }


PERMUTATION_ONTOLOGY = [
    {
        "subject": L + "Equipment",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#Class>",
    },
    {
        "subject": L + "Flagged",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#Class>",
    },
    {
        "subject": L + "score",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>",
    },
]
PERMUTATION_FACTS = [
    item
    for index, value in enumerate([1, 2, 3], start=1)
    for item in (
        {
            "subject": L + f"e/{index}",
            "predicate": RDF_TYPE,
            "object": "<urn:ontolearn:learning:Equipment>",
        },
        {
            "subject": L + f"e/{index}",
            "predicate": L + "score",
            "object": f'"{value}"^^<http://www.w3.org/2001/XMLSchema#integer>',
        },
    )
]


def _permuted_project(store, actor, rng, items, facts):
    """Save the fixed definitions/facts in one freshly permuted order."""
    project = open_blank(actor, f"排列 {rng.randint(0, 10**9)}")
    items = [dict(item) for item in items]
    facts = list(facts)
    # Permute definition save order and fact save order independently.
    rng.shuffle(items)
    rng.shuffle(facts)
    # Split the facts across separate commits in random chunks.
    chunks = []
    remaining = list(facts)
    while remaining:
        take = rng.randint(1, max(1, len(remaining)))
        chunks.append(remaining[:take])
        remaining = remaining[take:]
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=items,
        manual=fact_rows(chunks[0]),
    )
    for chunk in chunks[1:]:
        commit_state(store, project, manual=chunk)
    return project


@pytest.mark.parametrize("seed", range(50))
def test_save_order_permutation_produces_identical_derived_and_findings(owned, seed):
    """Property: permuting assertion & rule save order never changes results."""
    actor, store = owned
    rng = random.Random(20261115 + seed)
    # One fixed payload set per seed; both projects save the SAME definitions
    # and facts, only in independently permuted orders/chunks. Four controlled
    # rules fit the audited per-rule input budget; the operator subset rotates
    # by seed so all six operators get exercised across the property cases.
    operators = [["eq", "ne", "lt", "le"], ["gt", "ge", "eq", "ne"], ["le", "gt", "lt", "ge"]][
        seed % 3
    ]
    thresholds = [rng.choice([1, 2, 3]) for _ in operators]
    items = [
        {
            "layer": "ontology",
            "id": "perm.ontology",
            "value": {"triples": list(PERMUTATION_ONTOLOGY), "singleValuedPredicates": []},
        }
    ] + [
        _operator_rule(index, operator, thresholds[index])
        for index, operator in enumerate(operators)
    ]
    facts = list(PERMUTATION_FACTS)
    first = _permuted_project(store, actor, rng, items, facts)
    second = _permuted_project(store, actor, rng, items, facts)

    def outcome(project):
        snapshot, snapshot_id = snapshot_of(store, project)
        out = execute_request(
            {
                "snapshot": snapshot,
                "capability": "reasoning.execute",
                "input": request_input(snapshot_id),
                "parameters": {"inputSelection": "current"},
                "selected": None,
            },
            error_catalog=CONTRACT.ERROR_CATALOG,
            error_schema=CONTRACT.DOCUMENT,
        )
        payload = out["payload"]
        return payload["reasoning"]["rules"], payload["reasoning"]["warnings"]

    rules_a, warnings_a = outcome(first)
    rules_b, warnings_b = outcome(second)
    assert rules_a == rules_b
    assert warnings_a == warnings_b
    # The controlled comparison rules actually fired on the score facts.
    assert rules_a, "controlled comparison rules must derive at least one triple"
    flagged = {tuple(t) for t in rules_a}
    assert all(t[2] == "<urn:ontolearn:learning:Flagged>" for t in flagged)


# --------------------------------------------------------------------------
# 2. Round-trip persistence: 5 SHACL templates + 6-op/multi-head rules.
# --------------------------------------------------------------------------

TEMPLATE_CASES = [
    ("required", {}),
    ("datatype", {"datatype": "http://www.w3.org/2001/XMLSchema#integer"}),
    ("maxCount", {"maxCount": 2}),
    (
        "allowedValues",
        {"values": ['"a"', '"b"', '"c"']},
    ),
    ("numericRange", {"minInclusive": "1", "maxInclusive": "9"}),
]


def _rule_value(rule_id, operator=None, multi=False):
    conditions = [
        {"kind": "property", "subject": "?e", "path": L + "score", "object": "?v"},
    ]
    if operator is not None:
        conditions.append(
            {
                "kind": "compare",
                "left": "?v",
                "operator": operator,
                "right": '"3"^^<http://www.w3.org/2001/XMLSchema#integer>',
            }
        )
    conclusions = [{"kind": "type", "subject": "?e", "class": L + "Flagged"}]
    if multi:
        conclusions.append(
            {
                "kind": "property",
                "subject": "?e",
                "path": L + "reviewed",
                "object": '"true"^^<http://www.w3.org/2001/XMLSchema#boolean>',
            }
        )
    return {
        "schemaVersion": 1,
        "kind": "rule",
        "id": rule_id,
        "revision": 1,
        "label": "roundtrip",
        "enabled": True,
        "conditions": conditions,
        "conclusions": conclusions,
    }


@pytest.mark.parametrize("seed", range(50))
def test_template_and_rule_roundtrip_with_delete_restore(owned, seed):
    """Property: serialize → Store.commit → reload identical; delete restores."""
    actor, store = owned
    rng = random.Random(4003117 + seed)
    project = open_blank(actor, "往返")
    template, parameters = TEMPLATE_CASES[seed % len(TEMPLATE_CASES)]
    constraint = {
        "schemaVersion": 1,
        "kind": "constraint",
        "id": "tpl",
        "revision": rng.randint(1, 9),
        "label": "模板往返",
        "enabled": True,
        "targetClass": L + "Equipment",
        "path": L + "score",
        "template": template,
        "parameters": parameters,
    }
    operator = ["eq", "ne", "lt", "le", "gt", "ge"][seed % 6]
    rule_value = _rule_value("rt-rule", operator=operator, multi=rng.random() < 0.5)
    rule = {"layer": "rule", "id": "rt-rule", "value": rule_value}

    seed_quality(store, project)
    commit_state(
        store,
        project,
        definitions=[
            {"layer": "constraint", "id": "tpl", "value": constraint},
            rule,
        ],
    )

    def stored(layer, identity):
        return next(
            json.loads(d["payload"])
            for d in store.state(store._project(project))["definitions"]
            if d["layer"] == layer and d["id"] == identity
        )

    # Canonical validation and exact reload identity.
    assert validate_definition(constraint).payload() == constraint
    assert validate_definition(rule_value).payload() == rule_value
    assert stored("constraint", "tpl") == constraint
    assert stored("rule", "rt-rule") == rule_value
    # Every template compiles to a real parseable SHACL document.
    shapes_text = compile_constraint_turtle(constraint)
    assert "sh:" in shapes_text and constraint["targetClass"] in shapes_text

    # Delete both: the stored payload set returns to the pre-roundtrip state.
    before = sorted(
        (d["layer"], d["id"])
        for d in store.state(store._project(project))["definitions"]
        if "tpl" != d["id"] != "rt-rule"
    )
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        remove_definitions=[
            {"layer": "constraint", "id": "tpl"},
            {"layer": "rule", "id": "rt-rule"},
        ],
    )
    after = sorted((d["layer"], d["id"]) for d in store.state(internal)["definitions"])
    assert after == before


def test_roundtrip_rejects_incomplete_formal_definitions(owned):
    """The strict complete schema: {"layer": "rule", "id": "x", "value": {}} fails
    at the formal ChangeSet gate (Store.commit stays the opaque importer)."""
    from ontolearn_engine.job_store import JobFault
    from ontolearn_engine.resources import LIMITS as RESOURCE_LIMITS

    actor, store = owned
    project = open_blank(actor, "不完整")
    seed_quality(store, project)
    store._project(project)
    host_pair = {"host_client_id": uid(), "engine_session_id": uid()}

    def preview(plan):
        base = store.project_get(project)["projectRevision"]
        return store.preview_changeset(
            project,
            base,
            {"projectId": project, "baseRevision": base, "intent": "change", "plan": plan},
            limits=RESOURCE_LIMITS,
            **host_pair,
        )

    # Incomplete / opaque rule values are rejected atomically by the gate.
    with pytest.raises(JobFault):
        preview({"definitions": [{"layer": "rule", "id": "x", "value": {}}]})
    # A complete FR-505 rule previews cleanly.
    ready = preview(
        {"definitions": [{"layer": "rule", "id": "rt-rule", "value": _rule_value("rt-rule", "ge")}]}
    )
    assert ready["status"] == "ready"
    # The pure editor language rejects the same partial payloads.
    with pytest.raises(DefinitionError):
        validate_definition({})
    with pytest.raises(DefinitionError):
        validate_definition(
            {
                "schemaVersion": 1,
                "kind": "rule",
                "id": "x",
                "revision": 1,
                "label": "l",
                "enabled": True,
                "conditions": [],
                "conclusions": [],
            }
        )


# --------------------------------------------------------------------------
# 3. Idempotency & stale/retraction isolation.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("seed", range(50))
def test_reasoning_validation_idempotent_and_stale_reasons_set(owned, seed):
    rng = random.Random(6004119 + seed)
    actor, store = owned
    project = open_blank(actor, f"幂等-{seed}")
    seed_quality(store, project)

    first_reasoning = run_semantic(store, project, "reasoning.execute")
    second_reasoning = run_semantic(store, project, "reasoning.execute")
    first_validation = run_semantic(
        store, project, "validation.execute", definition="name-required"
    )
    second_validation = run_semantic(
        store, project, "validation.execute", definition="name-required"
    )
    # Idempotency: identical snapshot inputs produce identical payload content
    # (row ids differ by design; the payload projection is the fixed contract).
    assert result_payload(store, first_reasoning) == result_payload(store, second_reasoning)
    assert result_payload(store, first_validation) == result_payload(store, second_validation)

    def stale_reason(job):
        return store.result_get(project, job["resultRef"]["resultId"])["staleReason"]

    assert stale_reason(first_reasoning) == []
    assert stale_reason(first_validation) == []

    # FACTS_CHANGED: retracting one randomized equipment name invalidates results.
    victim = rng.choice(["001", "002", "003"])
    retracted_name = _fact_id(store, project, L + f"equipment/{victim}", L + "name")
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        remove=[retracted_name],
    )
    reasons = {row["code"] for row in stale_reason(first_reasoning)}
    assert reasons == {"FACTS_CHANGED"}
    reasons_validation = {row["code"] for row in stale_reason(first_validation)}
    assert reasons_validation == {"FACTS_CHANGED"}

    # Retracted facts never leak into current findings: after retraction the
    # fresh validation report contains exactly the retracted equipment's
    # violation, and no run against the current snapshot keeps the literal.
    after_retraction = run_semantic(
        store, project, "validation.execute", definition="name-required"
    )
    report = result_payload(store, after_retraction)["report"]
    assert not report["conforms"]
    focuses = {row["focus"] for row in report["violations"]}
    assert focuses == {f"<urn:ontolearn:learning:equipment/{victim}>"}
    serialized = json.dumps(result_payload(store, after_retraction))
    assert {"001": "泵站A", "002": "泵站B", "003": "备用泵C"}[victim] not in serialized

    # RULE_CHANGED and VALIDATION_DEFINITION_CHANGED after definition edits.
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "rule",
                "id": "R-risk",
                "value": {"enabled": False, "when": R_RISK_WHEN, "then": R_RISK_THEN},
            }
        ],
    )
    assert {row["code"] for row in stale_reason(first_reasoning)} >= {"RULE_CHANGED"}
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "constraint",
                "id": "name-required",
                "value": {**NAME_REQUIRED, "revision": 2},
            }
        ],
    )
    assert {row["code"] for row in stale_reason(first_validation)} >= {
        "VALIDATION_DEFINITION_CHANGED"
    }


# --------------------------------------------------------------------------
# 4. Real B3 learning checks and ledger isolation.
# --------------------------------------------------------------------------


def learning(actor, method, params):
    return ok(exchange(actor, method, params))


def task_view(state, task_id):
    return next(item for item in state["tasks"] if item["taskId"] == task_id)


def check_task(actor, task_id, selected_origins=None):
    params = {"projectId": actor.mainline.selected, "operationId": uid(), "taskId": task_id}
    if selected_origins is not None:
        params["selectedOrigins"] = selected_origins
    return learning(actor, "project.learning.task.check", params)


LX_PREREQ_ONTOLOGY = [
    {
        "subject": L + "Person",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2000/01/rdf-schema#Class>",
    },
    {
        "subject": L + "assignedTo",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#ObjectProperty>",
    },
    {
        "subject": L + "assignedTo",
        "predicate": "http://www.w3.org/2000/01/rdf-schema#domain",
        "object": "<urn:ontolearn:learning:Equipment>",
    },
    {
        "subject": L + "assignedTo",
        "predicate": "http://www.w3.org/2000/01/rdf-schema#range",
        "object": "<urn:ontolearn:learning:Person>",
    },
    {
        "subject": L + "NeedsInspection",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#Class>",
    },
]
LX_PREREQ_FACTS = [
    {
        "subject": L + "person/L01",
        "predicate": RDF_TYPE,
        "object": "<urn:ontolearn:learning:Person>",
    },
    {
        "subject": L + "equipment/001",
        "predicate": L + "assignedTo",
        "object": "<urn:ontolearn:learning:person/L01>",
    },
]
LX_REPAIR_FACTS = [
    {
        "subject": L + "equipment/002",
        "predicate": L + "assignedTo",
        "object": "<urn:ontolearn:learning:person/L02>",
    },
    {
        "subject": L + "equipment/003",
        "predicate": L + "assignedTo",
        "object": "<urn:ontolearn:learning:person/L01>",
    },
]
R_NEXT = {
    "layer": "rule",
    "id": "R-next",
    "value": {
        "enabled": True,
        "when": [["?equipment", f"<{RDF_TYPE}>", "<urn:ontolearn:learning:HighRiskEquipment>"]],
        "then": ["?equipment", f"<{RDF_TYPE}>", "<urn:ontolearn:learning:NeedsInspection>"],
    },
}


def _fact_id(store, project, subject, predicate):
    return next(
        fact["id"]
        for fact in store.state(store._project(project))["facts"]
        if fact["subject"] == subject and fact["predicate"] == predicate
    )


def test_quality_task_checks_pass_and_isolate_guided_stage(owned):
    actor, store = owned
    project = open_blank(actor, "B3 质量")
    seed_quality(store, project)

    # R-01: pure G-base reasoning (exact i05-finite-6 results).
    run_semantic(store, project, "reasoning.execute")

    # V-01: remove 003's name, validate, restore, validate again.
    name_003 = _fact_id(store, project, L + "equipment/003", L + "name")
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        remove=[name_003],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")
    commit_state(
        store,
        project,
        manual=[
            {
                "subject": L + "equipment/003",
                "predicate": L + "name",
                "object": '"备用泵C"',
            }
        ],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")

    # R-05: add the NeedsInspection class plus the chained R-next rule.
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "G-base.ontology",
                "value": {
                    "triples": [
                        *G_BASE["ontology"],
                        *LX_PREREQ_ONTOLOGY[:1],
                        LX_PREREQ_ONTOLOGY[4],
                    ],
                    "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                },
            },
            R_NEXT,
        ],
    )
    run_semantic(store, project, "reasoning.execute")

    # LX-01: domain/range axioms, business-ontology prerequisites, repair, re-run.
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "G-base.ontology",
                "value": {
                    "triples": [*G_BASE["ontology"], *LX_PREREQ_ONTOLOGY],
                    "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                },
            },
        ],
        manual=[*LX_PREREQ_FACTS, *LX_REPAIR_FACTS],
    )
    run_semantic(store, project, "reasoning.execute")

    result = check_task(
        actor,
        "quality",
        selected_origins={
            "urn:ontolearn:learning:person/L01": "asserted",
            "urn:ontolearn:learning:person/L02": "derived",
        },
    )
    assert result["checkStatus"] == "passed", result["feedback"]
    assert result["operationComplete"] is True
    state = result["learningState"]
    assert state["taskId"] == "quality"
    assert state["completedGuidedStages"] == []
    assert state["guidedStageCheckpointRef"] is None
    # FR-004: only business-ontology mints the guided-stage checkpoint.
    checkpoints = learning(
        actor, "project.checkpoint.list", {"projectId": project, "cursor": None, "pageSize": 50}
    )
    guided = [item for item in checkpoints["items"] if item.get("reason") == "guided-stage"]
    assert guided == []


def test_lx01_failure_paths_report_fixed_feedback(owned):
    actor, store = owned
    project = open_blank(actor, "LX 失败")
    seed_quality(store, project)
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "G-base.ontology",
                "value": {
                    "triples": [*G_BASE["ontology"], *LX_PREREQ_ONTOLOGY],
                    "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                },
            },
        ],
        manual=[*LX_PREREQ_FACTS, *LX_REPAIR_FACTS],
    )
    # Failure path (a): the learner additionally asserted person/L02 a Person.
    commit_state(
        store,
        project,
        manual=[
            {
                "subject": L + "person/L02",
                "predicate": RDF_TYPE,
                "object": "<urn:ontolearn:learning:Person>",
            },
        ],
    )
    run_semantic(store, project, "reasoning.execute")
    result = check_task(
        actor,
        "quality",
        selected_origins={
            "urn:ontolearn:learning:person/L01": "asserted",
            "urn:ontolearn:learning:person/L02": "derived",
        },
    )
    assert result["checkStatus"] == "needs-repair"
    feedback = ";".join(result["feedback"]["repairs"])
    assert "这样步骤 4 就没有可区分的推导了" in feedback
    assert result["operationComplete"] is False


def test_transfer_repair_and_classify_checks_pass(owned):
    actor, store = owned

    # transfer-repair: fresh independent case from transfer-inputs.json.
    repair_data = TRANSFER["repair"]
    project = open_blank(actor, "迁移修复")
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "transfer.ontology",
                "value": {"triples": repair_data["ontology"], "singleValuedPredicates": []},
            },
            {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
        ],
        manual=repair_data["facts"],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")
    commit_state(
        store,
        project,
        manual=[
            {
                "subject": L + "equipment/102",
                "predicate": L + "name",
                "object": '"供水泵"',
            }
        ],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")
    result = check_task(actor, "transfer-repair")
    assert result["checkStatus"] == "passed", result["feedback"]
    assert result["independentTransferSuccess"] is True

    # transfer-classify: asserted vs derived origins over equipment/201.
    classify = TRANSFER["classification"]
    classify_project = open_blank(actor, "迁移分类")
    commit_state(
        store,
        classify_project,
        definitions=[
            {
                "layer": "ontology",
                "id": "classify.ontology",
                "value": {"triples": classify["ontology"], "singleValuedPredicates": []},
            },
            {
                "layer": "rule",
                "id": "R-risk",
                "value": {"enabled": True, "when": R_RISK_WHEN, "then": R_RISK_THEN},
            },
        ],
        manual=classify["facts"],
    )
    run_semantic(store, classify_project, "reasoning.execute")
    result = check_task(actor, "transfer-classify", selected_origins=["asserted", "derived"])
    assert result["checkStatus"] == "passed", result["feedback"]
    assert result["independentTransferSuccess"] is True


def test_transfer_checks_fail_without_real_runs(owned):
    actor, store = owned
    project = open_blank(actor, "未运行迁移")
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "transfer.ontology",
                "value": {"triples": TRANSFER["repair"]["ontology"], "singleValuedPredicates": []},
            },
            {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
        ],
        manual=TRANSFER["repair"]["facts"],
    )
    result = check_task(actor, "transfer-repair")
    assert result["checkStatus"] in {"tool-not-successful", "needs-repair"}
    assert result["operationComplete"] is False
    assert result["guidedStageCheckpointRef"] is None


# --------------------------------------------------------------------------
# 5. Formal quality workspace methods over the named bridge.
# --------------------------------------------------------------------------


def test_quality_read_and_prepare_over_named_bridge(owned):
    actor, store = owned
    project = open_blank(actor, "质量工作台")
    seed_quality(store, project)
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["qualityReadVersion"] == 1
    assert {item["id"] for item in state["constraints"]} == {"name-required"}
    assert {item["id"] for item in state["rules"]} == {"R-risk"}
    assert state["reasoning"] is None and state["validation"] is None

    run_semantic(store, project, "reasoning.execute")
    run_semantic(store, project, "validation.execute", definition="name-required")
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["reasoning"]["derivation"]["rules"] == [
        [
            "urn:ontolearn:learning:equipment/001",
            RDF_TYPE,
            "<urn:ontolearn:learning:HighRiskEquipment>",
        ]
    ]
    assert state["validation"]["conforms"] is True
    assert state["validation"]["findings"] == []

    prepared = learning(
        actor,
        "project.quality.prepare",
        {
            "projectId": project,
            "operationId": uid(),
            "selection": {"kind": "current"},
        },
    )
    assert prepared["chain"] == ["reasoning.execute", "validation.execute"]
    assert prepared["reasoningInput"]["scope"] == "asserted"
    assert prepared["validationInput"]["definitionId"] == "name-required"


# --------------------------------------------------------------------------
# 6. Regressions: formal reasoning payloads stay inside mainline read limits,
#    and the auto-initialized quality attempt keeps prior runs on rechecks.
# --------------------------------------------------------------------------


def _drain_jobs(actor):
    """Drive the real Coordinator worker loop until queued jobs finish."""

    async def drain():
        await actor.tick()
        await asyncio.wait_for(asyncio.gather(*tuple(actor.tasks)), WORKER_TIMEOUT)

    asyncio.run(drain())


def _committed_changeset(actor, store, project, plan):
    """One real preview → full diff pages → confirm → worker changeset.commit."""
    ready = ok(
        exchange(
            actor,
            "changeset.preview",
            {
                "projectId": project,
                "baseRevision": store.revision(store._project(project)),
                "intent": "change",
                "plan": plan,
            },
        )
    )
    assert ready["status"] == "ready", ready
    cursor, segments = None, []
    while True:
        material = ok(
            exchange(
                actor,
                "changeset.diff.page",
                {
                    "projectId": project,
                    "previewHash": ready["previewHash"],
                    "documentKind": "diff",
                    "pageSize": 1,
                    "cursor": cursor,
                },
            )
        )
        segments.extend(material["segments"])
        cursor = material["nextCursor"]
        if material["complete"]:
            break
    document = b"".join(base64.b64decode(s["dataBase64"]) for s in segments)
    assert digest(json.loads(document)) == ready["manifest"]["documentHash"]
    confirmation = ok(
        exchange(
            actor,
            "changeset.confirm",
            {
                "projectId": project,
                "previewHash": ready["previewHash"],
                "completionCursor": cursor,
            },
        )
    )
    job = ok(
        exchange(
            actor,
            "job.create",
            {
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
            },
        )
    )
    assert job["state"] == "queued", job
    _drain_jobs(actor)
    return store.get_job(project, job["jobId"])


def _run_semantic_job(actor, store, project, capability, input_):
    """Create one semantic job over the real RPC and drain its worker."""
    job = ok(
        exchange(
            actor,
            "job.create",
            {
                "projectId": project,
                "operationId": uid(),
                "capability": capability,
                "input": input_,
                "confirmationRef": None,
            },
        )
    )
    assert job["state"] == "queued", job
    _drain_jobs(actor)
    return store.get_job(project, job["jobId"])


def _formal_rule(rule_id, label, conditions, conclusions):
    return {
        "layer": "rule",
        "id": rule_id,
        "value": {
            "schemaVersion": 1,
            "kind": "rule",
            "id": rule_id,
            "revision": 1,
            "label": label,
            "enabled": True,
            "conditions": conditions,
            "conclusions": conclusions,
        },
    }


FORMAL_R_RISK = _formal_rule(
    "R-risk",
    "高风险设备",
    [
        {"kind": "type", "subject": "?equipment", "class": L + "Equipment"},
        {"kind": "property", "subject": "?equipment", "path": L + "alarm", "object": "?alarm"},
        {"kind": "property", "subject": "?alarm", "path": L + "level", "object": '"High"'},
        {"kind": "property", "subject": "?alarm", "path": L + "status", "object": '"Open"'},
    ],
    [{"kind": "type", "subject": "?equipment", "class": L + "HighRiskEquipment"}],
)
FORMAL_R_NEXT = _formal_rule(
    "R-next",
    "需要巡检",
    [{"kind": "type", "subject": "?equipment", "class": L + "HighRiskEquipment"}],
    [{"kind": "type", "subject": "?equipment", "class": L + "NeedsInspection"}],
)


def test_formal_rule_repeated_quality_runs_stay_within_mainline_read_limits(owned):
    actor, store = owned
    project = open_blank(actor, "读限回归")
    committed = _committed_changeset(
        actor,
        store,
        project,
        {
            "definitions": [
                {
                    "layer": "ontology",
                    "id": "G-base.ontology",
                    "value": {
                        "triples": [*G_BASE["ontology"], *LX_PREREQ_ONTOLOGY],
                        "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                    },
                },
                FORMAL_R_RISK,
                FORMAL_R_NEXT,
                {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
            ],
            "manual": fact_rows([*G_BASE["facts"], *LX_PREREQ_FACTS]),
        },
    )
    assert committed["state"] == "succeeded", committed.get("error") or committed

    for _ in range(10):
        prepared = learning(
            actor,
            "project.quality.prepare",
            {
                "projectId": project,
                "operationId": uid(),
                "selection": {"kind": "current"},
            },
        )
        reasoning = _run_semantic_job(
            actor, store, project, "reasoning.execute", prepared["reasoningInput"]
        )
        assert reasoning["state"] == "succeeded", reasoning.get("error") or reasoning
        validation_input = dict(prepared["validationInput"])
        validation_input["derivedResultIds"] = [reasoning["resultRef"]["resultId"]]
        validation = _run_semantic_job(
            actor, store, project, "validation.execute", validation_input
        )
        assert validation["state"] == "succeeded", validation.get("error") or validation
        state = learning(actor, "project.quality.read", {"projectId": project})
        assert state["reasoning"] is not None and state["validation"] is not None
        assert state["validation"]["conforms"] is True

    # The real issuer-side measurement of prospective material, paid through
    # the same ownership admission the product preview path uses.
    preview_params = {
        "projectId": project,
        "baseRevision": store.revision(store._project(project)),
        "intent": "change",
        "plan": {},
    }
    request = frame(actor, "changeset.preview", preview_params)
    actor.mainline.begin(request)
    proof = actor.mainline.ownership_proof(preview_params, method="changeset.preview")
    total_rows, scan_bytes, decoded_bytes, plan_bytes, repeats = proof.material_profile()
    actor.finish_query_reply(request["id"], emitted=True)
    assert decoded_bytes + plan_bytes < READ_LIMITS.validation_bytes
    assert total_rows < READ_LIMITS.validation_rows
    assert 2 * scan_bytes + (decoded_bytes + plan_bytes) * repeats < READ_LIMITS.validation_work


def test_auto_initialized_quality_attempt_retains_prior_runs_across_recheck(owned):
    actor, store = owned
    project = open_blank(actor, "重查保留")
    seed_quality(store, project)

    # R-01: pure G-base reasoning.
    run_semantic(store, project, "reasoning.execute")

    # V-01: remove 003's name, validate, restore, validate again.
    name_003 = _fact_id(store, project, L + "equipment/003", L + "name")
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        remove=[name_003],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")
    commit_state(
        store,
        project,
        manual=[
            {
                "subject": L + "equipment/003",
                "predicate": L + "name",
                "object": '"备用泵C"',
            }
        ],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")

    # R-05: the NeedsInspection class plus the chained R-next rule.
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "G-base.ontology",
                "value": {
                    "triples": [
                        *G_BASE["ontology"],
                        *LX_PREREQ_ONTOLOGY[:1],
                        LX_PREREQ_ONTOLOGY[4],
                    ],
                    "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                },
            },
            R_NEXT,
        ],
    )
    run_semantic(store, project, "reasoning.execute")

    # LX-01 failure state: domain/range plus the extra asserted person/L02.
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "G-base.ontology",
                "value": {
                    "triples": [*G_BASE["ontology"], *LX_PREREQ_ONTOLOGY],
                    "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                },
            },
        ],
        manual=[*LX_PREREQ_FACTS, *LX_REPAIR_FACTS],
    )
    commit_state(
        store,
        project,
        manual=[
            {
                "subject": L + "person/L02",
                "predicate": RDF_TYPE,
                "object": "<urn:ontolearn:learning:Person>",
            },
        ],
    )
    run_semantic(store, project, "reasoning.execute")

    origins = {
        "urn:ontolearn:learning:person/L01": "asserted",
        "urn:ontolearn:learning:person/L02": "derived",
    }
    first = check_task(actor, "quality", selected_origins=origins)
    assert first["checkStatus"] == "needs-repair"
    attempt = first["attemptId"]

    # Repair LX-01 and re-run reasoning; the second check stays on the same
    # auto-initialized attempt and must still see the earlier real runs.
    l02_type = _fact_id(store, project, L + "person/L02", RDF_TYPE)
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        remove=[l02_type],
    )
    run_semantic(store, project, "reasoning.execute")
    second = check_task(actor, "quality", selected_origins=origins)
    assert second["attemptId"] == attempt
    assert second["checkStatus"] == "passed", second.get("feedback")
    assert second["operationComplete"] is True

    # An explicitly started second attempt still opens an isolated window.
    started = learning(
        actor,
        "project.learning.attempt.start",
        {"projectId": project, "operationId": uid(), "taskId": "quality"},
    )
    assert started["attemptId"] != attempt
    third = check_task(actor, "quality", selected_origins=origins)
    assert third["checkStatus"] == "tool-not-successful"
