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
import hashlib
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


def run_semantic(
    store, project, capability, definition="quality-reasoning", scope="asserted", derived=None
):
    """Real JobStore + worker execution of one semantic job."""
    snapshot_id = store.project_get(project)["inputSnapshotId"]
    input_ = {
        "inputSnapshotId": snapshot_id,
        "scope": scope,
        "definitionId": definition,
        "parametersHash": store.put_blob(project, {"inputSelection": "current"}),
        "derivedResultIds": list(derived or []),
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


def run_semantic_expect_failure(
    store, project, capability, definition="quality-reasoning", scope="asserted"
):
    """Real execution expected to end in the failed state (broken shapes)."""
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

    return asyncio.run(drive())


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
        "subject": L + "NeedsInspection",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#Class>",
    },
    {
        "subject": L + "score",
        "predicate": RDF_TYPE,
        "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>",
    },
    {
        "subject": L + "tag",
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

# A chained formal rule consuming the comparison rules' Flagged outputs: the
# planner flags the chain and the one-stage engine never re-feeds rule rows,
# so NeedsInspection must never appear in any closure or validation.
FORMAL_R_FLAG_NEXT = {
    "layer": "rule",
    "id": "R-flag-next",
    "value": {
        "schemaVersion": 1,
        "kind": "rule",
        "id": "R-flag-next",
        "revision": 1,
        "label": "链式巡检",
        "enabled": True,
        "conditions": [{"kind": "type", "subject": "?e", "class": L + "Flagged"}],
        "conclusions": [{"kind": "type", "subject": "?e", "class": L + "NeedsInspection"}],
    },
}

PERMUTATION_SCORE_RANGE = {
    "schemaVersion": 1,
    "kind": "constraint",
    "id": "score-range",
    "revision": 1,
    "label": "分数范围",
    "enabled": True,
    "targetClass": L + "Equipment",
    "path": L + "score",
    "template": "numericRange",
    "parameters": {"minInclusive": "2", "maxInclusive": "3"},
}

# B2-06 property-chain discriminator: the comparison rules derive Flagged
# types, and this required shape on Flagged/tag must see none of them in the
# asserted scope and every one of them in the asserted+derived scope.
PERMUTATION_FLAGGED_TAG_REQUIRED = {
    "schemaVersion": 1,
    "kind": "constraint",
    "id": "flagged-tag-required",
    "revision": 1,
    "label": "标记必填",
    "enabled": True,
    "targetClass": L + "Flagged",
    "path": L + "tag",
    "template": "required",
    "parameters": {},
}


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
    # The chained R-flag-next rule and the score-range constraint extend the
    # same invariance to the rule-chain warning and the real SHACL projection.
    operators = [["eq", "ne", "lt", "le"], ["gt", "ge", "eq", "ne"], ["le", "gt", "lt", "ge"]][
        seed % 3
    ]
    thresholds = [rng.choice([1, 2, 3]) for _ in operators]
    items = [
        {
            "layer": "ontology",
            "id": "perm.ontology",
            "value": {"triples": list(PERMUTATION_ONTOLOGY), "singleValuedPredicates": []},
        },
        FORMAL_R_FLAG_NEXT,
        {"layer": "constraint", "id": "score-range", "value": dict(PERMUTATION_SCORE_RANGE)},
        {
            "layer": "constraint",
            "id": "flagged-tag-required",
            "value": dict(PERMUTATION_FLAGGED_TAG_REQUIRED),
        },
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
        return payload["reasoning"], payload["reasoning"]["warnings"]

    body_a, warnings_a = outcome(first)
    body_b, warnings_b = outcome(second)
    assert body_a["rules"] == body_b["rules"]
    assert warnings_a == warnings_b
    # The static rule chain is flagged identically on both sides and the
    # blocked NeedsInspection derivations never enter the one-stage closure.
    assert any(text.startswith("RULE_CHAIN_UNSUPPORTED:R-flag-next") for text in warnings_a)
    assert all(t[2] != f"<{L}NeedsInspection>" for t in body_a["rules"])
    # The controlled comparison rules actually fired on the score facts.
    assert body_a["rules"], "controlled comparison rules must derive at least one triple"
    flagged = {tuple(t) for t in body_a["rules"]}
    assert all(t[2] == "<urn:ontolearn:learning:Flagged>" for t in flagged)

    # Real end-to-end chain on a deterministic seed sample (5 of 50): the
    # persisted reasoning result plus a real asserted+derived validation
    # execute must stay byte-identical across independently permuted saves.
    if seed % 10 == 0:

        def real_chain(project):
            reasoning = run_semantic(store, project, "reasoning.execute")
            body = result_payload(store, reasoning)["reasoning"]
            validation = run_semantic(
                store,
                project,
                "validation.execute",
                definition="score-range",
                scope="asserted+derived",
                derived=[reasoning["resultRef"]["resultId"]],
            )
            report = result_payload(store, validation)["report"]
            traces = [
                (entry["rule"], entry["result"], entry["inputs"]) for entry in body["evidence"]
            ]
            # B2-06 property chain: the same reasoning result must keep the
            # flagged-tag-required shape conforming over asserted facts alone
            # while every derived Flagged focus violates it in derived scope.
            result_id = reasoning["resultRef"]["resultId"]
            asserted_flagged_report = result_payload(
                store,
                run_semantic(
                    store, project, "validation.execute", definition="flagged-tag-required"
                ),
            )["report"]
            derived_flagged_report = result_payload(
                store,
                run_semantic(
                    store,
                    project,
                    "validation.execute",
                    definition="flagged-tag-required",
                    scope="asserted+derived",
                    derived=[result_id],
                ),
            )["report"]
            return (
                traces,
                list(body["warnings"]),
                report,
                asserted_flagged_report,
                derived_flagged_report,
                body,
            )

        (
            traces_a,
            runtime_warnings_a,
            report_a,
            asserted_flagged_a,
            derived_flagged_a,
            body_a,
        ) = real_chain(first)
        (
            traces_b,
            runtime_warnings_b,
            report_b,
            asserted_flagged_b,
            derived_flagged_b,
            body_b,
        ) = real_chain(second)
        assert traces_a == traces_b
        assert runtime_warnings_a == runtime_warnings_b
        assert report_a["conforms"] == report_b["conforms"]
        assert report_a["violations"] == report_b["violations"]
        assert not report_a["conforms"], "score 1 is outside [2, 3] in every permutation"
        assert any(
            text.startswith("RULE_CHAIN_UNSUPPORTED:R-flag-next") for text in runtime_warnings_a
        )
        # No NeedsInspection anywhere in the real evidence: not as a conclusion
        # (t[1][2]), not from the chained rule (t[0]) and not in any input.
        assert all(
            t[1][2] != f"<{L}NeedsInspection>"
            and t[0] != "R-flag-next"
            and all(triple[2] != f"<{L}NeedsInspection>" for triple in t[2])
            for t in traces_a
        )
        # B2-06: asserted scope has zero Flagged assertions (conforms), while
        # the derived scope must flag exactly the derived Flagged focuses.
        assert asserted_flagged_a["conforms"] is True
        assert asserted_flagged_a["violations"] == []
        assert derived_flagged_a["conforms"] is False
        assert {row["focus"] for row in derived_flagged_a["violations"]} == {
            triple[0] for triple in body_a["rules"]
        }
        assert asserted_flagged_b["conforms"] is True
        assert derived_flagged_b["conforms"] is False
        assert {row["focus"] for row in derived_flagged_b["violations"]} == {
            triple[0] for triple in body_b["rules"]
        }


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

    # LX-01 steps 1-2: domain/range axioms plus the assignedTo prerequisite
    # state (person/L01, equipment/001) WITHOUT the repair facts, the second
    # constraint, then the pre-repair reasoning and its asserted SHACL check.
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
            {
                "layer": "constraint",
                "id": "assigned-to-required",
                "value": dict(ASSIGNED_TO_REQUIRED),
            },
        ],
        manual=list(LX_PREREQ_FACTS),
    )
    run_semantic(store, project, "reasoning.execute")  # Step 1: pre-repair reasoning.
    before = result_payload(
        store,
        run_semantic(store, project, "validation.execute", definition="assigned-to-required"),
    )["report"]  # Step 2: pre-repair SHACL measures exactly two violations.
    assert not before["conforms"]
    assert {row["focus"] for row in before["violations"]} == {
        f"<{L}equipment/002>",
        f"<{L}equipment/003>",
    }

    # LX-01 steps 3-4: commit the repair facts, re-run reasoning and the same
    # asserted-scope validation on the repaired snapshot.
    commit_state(store, project, manual=list(LX_REPAIR_FACTS))
    run_semantic(store, project, "reasoning.execute")  # Step 3: repaired reasoning.
    after = result_payload(
        store,
        run_semantic(store, project, "validation.execute", definition="assigned-to-required"),
    )["report"]  # Step 4: repaired SHACL conforms with zero violations.
    assert after["conforms"] is True and after["violations"] == []

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


ASSIGNED_TO_REQUIRED = {
    "schemaVersion": 1,
    "kind": "constraint",
    "id": "assigned-to-required",
    "revision": 1,
    "label": "设备负责人必填",
    "enabled": True,
    "targetClass": L + "Equipment",
    "path": L + "assignedTo",
    "template": "required",
    "parameters": {},
}


def test_full_lx01_lesson_flow_fits_page_budget_after_request_dedup(owned):
    """End-to-end R7 regression: the whole Lesson 04 single-project flow
    (V-01 -> R-01 -> R-05 -> LX-01 with both constraints, needs-repair,
    remove person/L02 rdf:type, re-run incl. asserted+derived, passed) stays
    inside the mainline page/work budgets once semantic job contexts stop
    duplicating the full semanticRequest and formal reasoning payloads stop
    persisting proofLeaves."""
    actor, store = owned
    project = open_blank(actor, "LX 全流程瘦身")
    semantic_jobs = []

    def ontology_layer(triples):
        return {
            "layer": "ontology",
            "id": "G-base.ontology",
            "value": {
                "triples": triples,
                "singleValuedPredicates": G_BASE["singleValuedPredicates"],
            },
        }

    def quality_run(*, scope="asserted", constraint_id=None):
        """One real prepare -> reasoning -> per-enabled-constraint validation chain."""
        params = {
            "projectId": project,
            "operationId": uid(),
            "selection": {"kind": "current"},
            "validationScope": scope,
        }
        if constraint_id is not None:
            params["constraintId"] = constraint_id
        prepared = learning(actor, "project.quality.prepare", params)
        reasoning = _run_semantic_job(
            actor, store, project, "reasoning.execute", prepared["reasoningInput"]
        )
        semantic_jobs.append(reasoning)
        validations = []
        for validation_input in prepared["validationInputs"]:
            filled = dict(validation_input)
            if scope == "asserted+derived":
                filled["derivedResultIds"] = [reasoning["resultRef"]["resultId"]]
            validation = _run_semantic_job(actor, store, project, "validation.execute", filled)
            semantic_jobs.append(validation)
            validations.append(validation)
        return reasoning, validations

    def report_of(job):
        return result_payload(store, job)["report"]

    # Step 1: G-base plus the name-required constraint and the formal R-risk.
    commit_state(
        store,
        project,
        definitions=[
            ontology_layer(list(G_BASE["ontology"])),
            FORMAL_R_RISK,
            {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
        ],
        manual=list(G_BASE["facts"]),
    )

    # V-01: remove 003's name, validate, restore, validate again.
    name_003 = _fact_id(store, project, L + "equipment/003", L + "name")
    internal = store._project(project)
    store.commit(internal, store.revision(internal), uid(), uid(), remove=[name_003])
    _, broken = quality_run()
    assert not report_of(broken[0])["conforms"]
    assert {row["focus"] for row in report_of(broken[0])["violations"]} == {f"<{L}equipment/003>"}
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
    _, repaired = quality_run()
    assert report_of(repaired[0])["conforms"]

    # R-05: NeedsInspection class plus the chained formal R-next rule.
    commit_state(
        store,
        project,
        definitions=[
            ontology_layer([*G_BASE["ontology"], LX_PREREQ_ONTOLOGY[0], LX_PREREQ_ONTOLOGY[4]]),
            FORMAL_R_NEXT,
        ],
    )
    chained, _ = quality_run()
    body = result_payload(store, chained)["reasoning"]
    assert any(text.startswith("RULE_CHAIN_UNSUPPORTED:R-next") for text in body["warnings"])
    assert all(t[2] != f"<{L}NeedsInspection>" for t in body["rules"])

    # LX-01 prerequisites: domain/range axioms, the second constraint and the
    # person/L01 fixture leave equipment/002 and /003 without an assigned owner.
    commit_state(
        store,
        project,
        definitions=[
            ontology_layer([*G_BASE["ontology"], *LX_PREREQ_ONTOLOGY]),
            {
                "layer": "constraint",
                "id": "assigned-to-required",
                "value": dict(ASSIGNED_TO_REQUIRED),
            },
        ],
        manual=list(LX_PREREQ_FACTS),
    )
    _, prereq = quality_run()
    by_definition = {job["input"]["definitionId"]: report_of(job) for job in prereq}
    assert by_definition["name-required"]["conforms"] is True
    assert not by_definition["assigned-to-required"]["conforms"]
    assert {row["focus"] for row in by_definition["assigned-to-required"]["violations"]} == {
        f"<{L}equipment/002>",
        f"<{L}equipment/003>",
    }

    # LX-01 failure state: repair facts plus the extra asserted person/L02.
    commit_state(
        store,
        project,
        manual=[
            *LX_REPAIR_FACTS,
            {
                "subject": L + "person/L02",
                "predicate": RDF_TYPE,
                "object": f"<{L}Person>",
            },
        ],
    )
    failure_reasoning, failure_validations = quality_run()
    assert all(report_of(job)["conforms"] for job in failure_validations)
    origins = {
        f"{L}person/L01": "asserted",
        f"{L}person/L02": "derived",
    }
    first = check_task(actor, "quality", selected_origins=origins)
    assert first["checkStatus"] == "needs-repair"
    assert "这样步骤 4 就没有可区分的推导了" in ";".join(first["feedback"]["repairs"])

    # LX-01 repair: remove person/L02 rdf:type (the E2E revision-13->14 edit).
    l02_type = _fact_id(store, project, L + "person/L02", RDF_TYPE)
    revision_before = store.project_get(project)["projectRevision"]
    internal = store._project(project)
    store.commit(internal, store.revision(internal), uid(), uid(), remove=[l02_type])
    assert store.project_get(project)["projectRevision"] == revision_before + 1

    final_reasoning, final_validations = quality_run()
    assert all(report_of(job)["conforms"] for job in final_validations)
    # Full-coverage cohort read: every enabled constraint has an available
    # succeeded asserted result, so the aggregate conforms and hides nothing.
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["reasoning"] is not None and state["validation"] is not None
    assert state["validation"]["conforms"] is True
    assert state["validation"]["unverifiedConstraintIds"] == []
    assert state["validation"]["checkedConstraintIds"] == ["assigned-to-required", "name-required"]
    assert state["validation"]["failedConstraintIds"] == []
    assert state["snapshotsAligned"] is True

    # At least one asserted+derived validation.execute on the second constraint
    # (name-required stays asserted-scope so V-01's frozen expectation holds).
    derived_reasoning, derived_validations = quality_run(
        scope="asserted+derived", constraint_id="assigned-to-required"
    )
    assert [job["input"]["definitionId"] for job in derived_validations] == ["assigned-to-required"]
    assert all(report_of(job)["conforms"] for job in derived_validations)
    assert all(job["input"]["scope"] == "asserted+derived" for job in derived_validations)
    # Single-constraint derived cohort read: name-required is uncovered by the
    # newest terminal cohort, so the read must refuse a "符合约束" verdict.
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["validation"]["conforms"] is None
    assert state["validation"]["unverifiedConstraintIds"] == ["name-required"]
    assert state["validation"]["checkedConstraintIds"] == ["assigned-to-required"]
    assert state["snapshotsAligned"] is True

    second = check_task(actor, "quality", selected_origins=origins)
    assert second["checkStatus"] == "passed", second.get("feedback")
    assert second["operationComplete"] is True

    # Every semantic job context stores the request digest, never the request.
    for job in semantic_jobs:
        context = store.job_context(job["jobId"])
        assert "semanticRequest" not in context, job["jobId"]
        sha = context["semanticRequestSha256"]
        assert isinstance(sha, str) and len(sha) == 64, job["jobId"]

    # Formal reasoning payloads carry the five plain keys, never proofLeaves;
    # the final rdfs closure still derives person/L02's Person type.
    for job in semantic_jobs:
        if job["capability"] != "reasoning.execute":
            continue
        body = result_payload(store, job)["reasoning"]
        assert "proofLeaves" not in body, job["jobId"]
        assert {
            "semanticsVersion",
            "rdfs",
            "rules",
            "warnings",
            "evidence",
            "rdfsEvidence",
        } <= set(body)
    final_body = result_payload(store, derived_reasoning)["reasoning"]
    assert (f"<{L}person/L02>", f"<{RDF_TYPE}>", f"<{L}Person>") in {
        tuple(triple) for triple in final_body["rdfs"]
    }

    # The real issuer-side page/work measurement over the same admission the
    # product preview path uses: the deduplicated contexts must fit 85% of the
    # validation page budget that R6's Test 9 overflowed at revision 14.
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
    assert decoded_bytes + plan_bytes < int(0.85 * READ_LIMITS.validation_bytes)
    assert 2 * scan_bytes + (decoded_bytes + plan_bytes) * repeats < READ_LIMITS.validation_work

    # Anti-gaming falsification: the persisted digest is the digest of the
    # genuinely rebuilt worker request, and tampering with it is rejected —
    # the assertions above cannot pass against a trivially keyed placeholder.
    from ontolearn_engine.job_store import JobFault

    validation = derived_validations[0]
    context = store.job_context(validation["jobId"])
    rebuilt = store.worker_semantic_request(validation, context)
    assert context["semanticRequestSha256"] == digest(rebuilt)
    tampered = dict(context, semanticRequestSha256="0" * 64)
    with pytest.raises(JobFault, match="INVALID_STATE"):
        store.worker_semantic_request(validation, tampered)


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

    # LX-01 steps 1-2: domain/range axioms, the second constraint and the
    # pre-repair assignedTo state, then pre-repair reasoning + SHACL.
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
            {
                "layer": "constraint",
                "id": "assigned-to-required",
                "value": dict(ASSIGNED_TO_REQUIRED),
            },
        ],
        manual=list(LX_PREREQ_FACTS),
    )
    run_semantic(store, project, "reasoning.execute")
    run_semantic(store, project, "validation.execute", definition="assigned-to-required")

    # LX-01 failure state: repair facts plus the extra asserted person/L02.
    commit_state(
        store,
        project,
        manual=[*LX_REPAIR_FACTS],
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

    # Repair LX-01 and re-run reasoning plus the repaired SHACL check; the
    # second check stays on the same auto-initialized attempt and must still
    # see the earlier real runs (steps 1-2) inside its open window.
    l02_type = _fact_id(store, project, L + "person/L02", RDF_TYPE)
    internal = store._project(project)
    store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        remove=[l02_type],
    )
    run_semantic(store, project, "reasoning.execute")  # Step 3: repaired reasoning.
    repaired = result_payload(
        store,
        run_semantic(store, project, "validation.execute", definition="assigned-to-required"),
    )["report"]  # Step 4: repaired SHACL conforms.
    assert repaired["conforms"] is True and repaired["violations"] == []
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


# --------------------------------------------------------------------------
# 7. R8a regressions: B2-01 derived replay matrix, B2-02/F1/F6 strict quality
#    aggregation, B2-03/04 negative learning paths, B2-05 in-memory rule
#    sample evaluation, B2-06/N1 template, operator and proof-leaf checks.
# --------------------------------------------------------------------------


def test_b2_01_derived_replay_matrix(owned):
    """Five-path matrix: accepted derived jobs survive pointer replacement,
    staleness, cache eviction and pre-R7 contexts without losing authority."""
    from ontolearn_engine.job_store import JobFault

    actor, store = owned
    project = open_blank(actor, "B2-01 矩阵")
    seed_quality(store, project)
    reasoning1 = run_semantic(store, project, "reasoning.execute")
    source_id = reasoning1["resultRef"]["resultId"]
    derived_input = {
        "inputSnapshotId": reasoning1["inputSnapshotId"],
        "scope": "asserted+derived",
        "definitionId": "name-required",
        "parametersHash": store.put_blob(project, {"inputSelection": "current"}),
        "derivedResultIds": [source_id],
        "preparedPlanRef": None,
    }
    operation = uid()
    validation1 = store.create_job(
        project, operation, "validation.execute", derived_input, None, semantic_identity(), LIMITS
    )
    context = store.job_context(validation1["jobId"])
    assert context["semanticRequestSha256"] == digest(
        store.worker_semantic_request(validation1, context)
    )

    # (1) A newer same-snapshot reasoning replaces the job_current pointer: the
    # source turns historical yet the accepted request still rebuilds byte
    # for byte (only immutable provenance is bound into the request).
    run_semantic(store, project, "reasoning.execute")
    assert store.result_get(project, source_id)["state"] == "historical"
    rebuilt = store.worker_semantic_request(validation1, context)
    assert digest(rebuilt) == context["semanticRequestSha256"]

    # (2) A domain commit marks the source reasoning stale; the deterministic
    # rebuild stays identical, so worker dispatch and finish keep working.
    commit_state(
        store,
        project,
        manual=[
            {
                "subject": L + "equipment/001",
                "predicate": L + "name",
                "object": '"泵站A改"',
            }
        ],
    )
    assert store.result_get(project, source_id)["state"] == "stale"
    assert (
        digest(store.worker_semantic_request(validation1, context))
        == context["semanticRequestSha256"]
    )

    # (3) Terminal operationId idempotent replay after replacement + expiry.
    replayed = store.create_job(
        project,
        operation,
        "validation.execute",
        derived_input,
        None,
        semantic_identity(),
        LIMITS,
    )
    assert replayed["jobId"] == validation1["jobId"]
    assert replayed["state"] == "queued"

    # (4) collect_cache() evicts the unpinned stale source; the replay stays
    # authoritative with no digest re-verification fault.
    assert source_id in store.collect_cache()
    assert store.result_get(project, source_id)["payloadStatus"] == "evicted"
    replayed_again = store.create_job(
        project,
        operation,
        "validation.execute",
        derived_input,
        None,
        semantic_identity(),
        LIMITS,
    )
    assert replayed_again["jobId"] == validation1["jobId"]

    # (5) Worker dispatch after eviction fails fast with PAYLOAD_EVICTED.
    with pytest.raises(JobFault) as caught:
        store.worker_semantic_request(validation1, context)
    assert caught.value.code == "PAYLOAD_EVICTED"
    assert caught.value.params == {"resultId": source_id}

    # (6) Pre-R7 contexts stored the full semanticRequest document instead of
    # its digest; their replay re-verifies the request itself while the
    # derived source payload lasts and stays authoritative once it is evicted.
    reasoning3 = run_semantic(store, project, "reasoning.execute")
    legacy_source = reasoning3["resultRef"]["resultId"]
    legacy_input = {
        "inputSnapshotId": reasoning3["inputSnapshotId"],
        "scope": "asserted+derived",
        "definitionId": "name-required",
        "parametersHash": store.put_blob(project, {"inputSelection": "current"}),
        "derivedResultIds": [legacy_source],
        "preparedPlanRef": None,
    }
    legacy_operation = uid()
    legacy = store.create_job(
        project,
        legacy_operation,
        "validation.execute",
        legacy_input,
        None,
        semantic_identity(),
        LIMITS,
    )
    legacy_context = store.job_context(legacy["jobId"])
    legacy_request = store.worker_semantic_request(legacy, legacy_context)
    legacy_job_id, legacy_row_operation = uid(), uid()
    legacy_dto = json.loads(json.dumps(legacy))
    legacy_dto["jobId"] = legacy_job_id
    legacy_dto["operationId"] = legacy_row_operation
    stored_context = {key: value for key, value in legacy_context.items() if key != "job"}
    del stored_context["semanticRequestSha256"]
    stored_context["semanticRequest"] = legacy_request
    fingerprint = digest(stored_context)
    store._db.execute(
        "INSERT INTO jobs VALUES(?,?,?,?,?,?,NULL)",
        (
            legacy_job_id,
            project,
            legacy_row_operation,
            json.dumps(legacy_dto),
            json.dumps(stored_context),
            fingerprint,
        ),
    )
    store._db.execute(
        "INSERT INTO operation_claims VALUES(?,?,?,?,?,NULL)",
        (legacy_row_operation, project, legacy_job_id, fingerprint, "job"),
    )
    legacy_replay = store.create_job(
        project,
        legacy_row_operation,
        "validation.execute",
        legacy_input,
        None,
        semantic_identity(),
        LIMITS,
    )
    assert legacy_replay["jobId"] == legacy_job_id
    # Replace the current pointer so the legacy source becomes evictable.
    run_semantic(store, project, "reasoning.execute")
    store.collect_cache()
    assert store.result_get(project, legacy_source)["payloadStatus"] == "evicted"
    legacy_replay_evicted = store.create_job(
        project,
        legacy_row_operation,
        "validation.execute",
        legacy_input,
        None,
        semantic_identity(),
        LIMITS,
    )
    assert legacy_replay_evicted["jobId"] == legacy_job_id


def test_quality_read_aggregation_strictness_matrix(owned):
    """B2-02/F1/F6: anchored cohorts, strict conforms, snapshotsAligned, and
    definition revision projection in project.quality.read."""
    actor, store = owned
    project = open_blank(actor, "聚合矩阵")
    seed_quality(store, project)
    internal = store._project(project)

    # Empty project: no validation evidence at all.
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["validation"] is None and state["reasoning"] is None
    assert state["snapshotsAligned"] is None
    # F1: revision projection uses the stored formal revision when present.
    assert state["constraints"][0]["revision"] == 1
    legacy_revision = store.vector(internal).get("rule:R-risk", 0)
    assert state["rules"][0]["revision"] == legacy_revision

    # Single-constraint full coverage projects the single definitionId.
    run_semantic(store, project, "reasoning.execute")
    run_semantic(store, project, "validation.execute", definition="name-required")
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["validation"]["conforms"] is True
    assert state["validation"]["checkedConstraintIds"] == ["name-required"]
    assert state["validation"]["unverifiedConstraintIds"] == []
    assert state["validation"]["failedConstraintIds"] == []
    assert state["validation"]["definitionId"] == "name-required"
    assert state["validation"]["inputProjectRevision"] == store.revision(internal)
    assert state["snapshotsAligned"] is True

    # Enable a second constraint on a new snapshot, then run only one
    # derived-scope check: the anchored cohort never mixes with the earlier
    # asserted run on the older snapshot and name-required stays unverified.
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "constraint",
                "id": "assigned-to-required",
                "value": dict(ASSIGNED_TO_REQUIRED),
            }
        ],
        manual=list(LX_PREREQ_FACTS),
    )
    reasoning = run_semantic(store, project, "reasoning.execute")
    run_semantic(
        store,
        project,
        "validation.execute",
        definition="assigned-to-required",
        scope="asserted+derived",
        derived=[reasoning["resultRef"]["resultId"]],
    )
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["validation"]["conforms"] is None
    assert state["validation"]["scope"] == "asserted+derived"
    assert state["validation"]["checkedConstraintIds"] == ["assigned-to-required"]
    assert state["validation"]["unverifiedConstraintIds"] == ["name-required"]
    assert state["validation"]["definitionId"] == "partial-constraints"

    # Complete the assignedTo repair so both enabled constraints conform, then
    # run the full asserted cohort over both constraints on the newest
    # snapshot: the aggregate restores with the all-enabled projection.
    commit_state(store, project, manual=list(LX_REPAIR_FACTS))
    run_semantic(store, project, "validation.execute", definition="name-required")
    run_semantic(store, project, "validation.execute", definition="assigned-to-required")
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["validation"]["conforms"] is True
    assert state["validation"]["definitionId"] == "all-enabled-constraints"
    assert state["validation"]["checkedConstraintIds"] == [
        "assigned-to-required",
        "name-required",
    ]
    # The reasoning result lags one commit behind: alignment flips to False.
    assert state["snapshotsAligned"] is False

    # A commit that only reruns validation leaves the reasoning result one
    # snapshot behind: snapshotsAligned flips to False, reasoning goes stale.
    commit_state(
        store,
        project,
        manual=[{"subject": L + "equipment/001", "predicate": L + "name", "object": '"泵站甲"'}],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["snapshotsAligned"] is False
    assert state["reasoning"]["state"] == "stale"


def test_quality_read_failed_cohorts_and_finding_definition_ids(owned):
    """Failed validation jobs surface failedConstraintIds with conforms None,
    and every finding carries the constraint identity that produced it."""
    actor, store = owned

    # A broken Turtle constraint fails its real validation job.
    project = open_blank(actor, "失败约束")
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "G-base.ontology",
                "value": {
                    "triples": list(G_BASE["ontology"]),
                    "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                },
            },
            {
                "layer": "rule",
                "id": "R-risk",
                "value": {"enabled": True, "when": R_RISK_WHEN, "then": R_RISK_THEN},
            },
            {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
            {
                "layer": "constraint",
                "id": "broken-shape",
                "value": {"enabled": True, "turtle": "@prefix sh: <<<< not turtle"},
            },
        ],
        manual=list(G_BASE["facts"]),
    )
    run_semantic(store, project, "validation.execute", definition="name-required")
    broken = run_semantic_expect_failure(
        store, project, "validation.execute", definition="broken-shape"
    )
    assert broken["state"] == "failed"
    state = learning(actor, "project.quality.read", {"projectId": project})
    assert state["validation"]["conforms"] is None
    assert state["validation"]["failedConstraintIds"] == ["broken-shape"]
    assert state["validation"]["unverifiedConstraintIds"] == ["broken-shape"]
    assert state["validation"]["checkedConstraintIds"] == ["name-required"]
    assert state["validation"]["findings"] == []

    # Violations carry their producing constraint id with click-to-locate targets.
    report_project = open_blank(actor, "违规定位")
    seed_quality(store, report_project)
    name_003 = _fact_id(store, report_project, L + "equipment/003", L + "name")
    internal = store._project(report_project)
    store.commit(internal, store.revision(internal), uid(), uid(), remove=[name_003])
    run_semantic(store, report_project, "validation.execute", definition="name-required")
    state = learning(actor, "project.quality.read", {"projectId": report_project})
    assert state["validation"]["conforms"] is False
    finding = state["validation"]["findings"][0]
    assert finding["definitionId"] == "name-required"
    assert finding["targets"] == {
        "subject": f"<{L}equipment/003>",
        "predicate": f"<{L}name>",
        "object": None,
    }


def _lx_prereq_commit(store, project):
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
            {
                "layer": "constraint",
                "id": "assigned-to-required",
                "value": dict(ASSIGNED_TO_REQUIRED),
            },
        ],
        manual=list(LX_PREREQ_FACTS),
    )


def _run_v01_steps(store, project):
    """The V-01 prerequisite: name removed, validated, restored, validated."""
    name_003 = _fact_id(store, project, L + "equipment/003", L + "name")
    internal = store._project(project)
    store.commit(internal, store.revision(internal), uid(), uid(), remove=[name_003])
    run_semantic(store, project, "validation.execute", definition="name-required")
    commit_state(
        store,
        project,
        manual=[{"subject": L + "equipment/003", "predicate": L + "name", "object": '"备用泵C"'}],
    )
    run_semantic(store, project, "validation.execute", definition="name-required")


def test_lx01_negative_paths_require_real_step_runs(owned):
    actor, store = owned
    origins = {
        "urn:ontolearn:learning:person/L01": "asserted",
        "urn:ontolearn:learning:person/L02": "derived",
    }

    # (a) Skipping both SHACL steps (pre-repair validation and the repaired
    # re-validation) fails LX-01 even though both reasonings really ran.
    skipped = open_blank(actor, "跳过 SHACL")
    seed_quality(store, skipped)
    _run_v01_steps(store, skipped)
    _lx_prereq_commit(store, skipped)
    run_semantic(store, skipped, "reasoning.execute")  # Step 1 only.
    commit_state(store, skipped, manual=list(LX_REPAIR_FACTS))
    run_semantic(store, skipped, "reasoning.execute")  # Step 3 only, no steps 2/4.
    result = check_task(actor, "quality", selected_origins=origins)
    assert result["checkStatus"] == "needs-repair"
    assert "请完整完成 LX-01 步骤 1–4" in ";".join(result["feedback"]["repairs"])

    # (b) Missing the 003 repair (only 002 assignedTo person/L02 committed)
    # fails the exact repair-set check before the step checks matter.
    partial = open_blank(actor, "漏修 003")
    seed_quality(store, partial)
    _run_v01_steps(store, partial)
    _lx_prereq_commit(store, partial)
    run_semantic(store, partial, "reasoning.execute")  # Step 1.
    run_semantic(store, partial, "validation.execute", definition="assigned-to-required")  # Step 2.
    commit_state(
        store,
        partial,
        manual=[
            {
                "subject": L + "equipment/002",
                "predicate": L + "assignedTo",
                "object": "<urn:ontolearn:learning:person/L02>",
            }
        ],
    )
    run_semantic(store, partial, "reasoning.execute")  # Step 3.
    run_semantic(store, partial, "validation.execute", definition="assigned-to-required")  # Step 4.
    result = check_task(actor, "quality", selected_origins=origins)
    assert result["checkStatus"] == "needs-repair"
    assert "需要修复：修复集合必须恰好是" in ";".join(result["feedback"]["repairs"])


def test_transfer_checks_reject_wrong_constraint_and_derived_scope(owned):
    actor, store = owned
    repair_data = TRANSFER["repair"]

    # (a) A differently named (otherwise identical) required constraint never
    # matches the frozen transfer-repair evidence: the tool stays unavailable.
    renamed = open_blank(actor, "错约束")
    commit_state(
        store,
        renamed,
        definitions=[
            {
                "layer": "ontology",
                "id": "transfer.ontology",
                "value": {"triples": repair_data["ontology"], "singleValuedPredicates": []},
            },
            {
                "layer": "constraint",
                "id": "equipment-name",
                "value": {**NAME_REQUIRED, "id": "equipment-name"},
            },
        ],
        manual=repair_data["facts"],
    )
    run_semantic(store, renamed, "validation.execute", definition="equipment-name")
    commit_state(
        store,
        renamed,
        manual=[{"subject": L + "equipment/102", "predicate": L + "name", "object": '"供水泵"'}],
    )
    run_semantic(store, renamed, "validation.execute", definition="equipment-name")
    result = check_task(actor, "transfer-repair")
    assert result["checkStatus"] == "tool-not-successful"
    assert result["operationComplete"] is False

    # (b) asserted+derived scoped runs cannot pose as the frozen
    # current-asserted expectation even with the right constraint.
    derived_scope = open_blank(actor, "派生范围")
    commit_state(
        store,
        derived_scope,
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
    reasoning = run_semantic(store, derived_scope, "reasoning.execute")
    run_semantic(
        store,
        derived_scope,
        "validation.execute",
        definition="name-required",
        scope="asserted+derived",
        derived=[reasoning["resultRef"]["resultId"]],
    )
    commit_state(
        store,
        derived_scope,
        manual=[{"subject": L + "equipment/102", "predicate": L + "name", "object": '"供水泵"'}],
    )
    reasoning2 = run_semantic(store, derived_scope, "reasoning.execute")
    run_semantic(
        store,
        derived_scope,
        "validation.execute",
        definition="name-required",
        scope="asserted+derived",
        derived=[reasoning2["resultRef"]["resultId"]],
    )
    result = check_task(actor, "transfer-repair")
    assert result["checkStatus"] == "needs-repair"
    assert result["operationComplete"] is False


def test_transfer_classify_rejects_manual_derived_assertion(owned):
    actor, store = owned
    classify = TRANSFER["classification"]
    project = open_blank(actor, "手工断言")
    commit_state(
        store,
        project,
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
        manual=[
            *classify["facts"],
            {
                "subject": L + "equipment/201",
                "predicate": RDF_TYPE,
                "object": f"<{L}HighRiskEquipment>",
            },
        ],
    )
    run_semantic(store, project, "reasoning.execute")
    result = check_task(actor, "transfer-classify", selected_origins=["asserted", "derived"])
    assert result["checkStatus"] == "needs-repair"
    assert result["operationComplete"] is False


SAMPLE_ONTOLOGY = [
    [item["subject"], item["predicate"], item["object"]] for item in G_BASE["ontology"]
] + [
    [L + "Person", RDF_TYPE, "<http://www.w3.org/2000/01/rdf-schema#Class>"],
    [L + "NeedsInspection", RDF_TYPE, "<http://www.w3.org/2002/07/owl#Class>"],
    [L + "assignedTo", "http://www.w3.org/2000/01/rdf-schema#domain", f"<{L}Equipment>"],
    [L + "assignedTo", "http://www.w3.org/2000/01/rdf-schema#range", f"<{L}Person>"],
]
SAMPLE_INPUT = [
    [L + "equipment/001", RDF_TYPE, f"<{L}Equipment>"],
    [L + "equipment/001", L + "alarm", f"<{L}alarm/X1>"],
    [L + "alarm/X1", L + "level", '"High"'],
    [L + "alarm/X1", L + "status", '"Open"'],
    [L + "equipment/002", RDF_TYPE, f"<{L}Equipment>"],
    [L + "equipment/002", L + "alarm", f"<{L}alarm/X2>"],
    [L + "alarm/X2", L + "level", '"High"'],
    [L + "alarm/X2", L + "status", '"Open"'],
    [L + "equipment/002", L + "assignedTo", f"<{L}person/L02>"],
]
SAMPLE_R_RISK = {
    "id": "R-risk",
    "label": "高风险设备",
    "enabled": True,
    "conditions": [
        {"kind": "type", "subject": "?e", "class": L + "Equipment"},
        {"kind": "property", "subject": "?e", "path": L + "alarm", "object": "?a"},
        {"kind": "property", "subject": "?a", "path": L + "level", "object": '"High"'},
        {"kind": "property", "subject": "?a", "path": L + "status", "object": '"Open"'},
    ],
    "conclusions": [{"kind": "type", "subject": "?e", "class": L + "HighRiskEquipment"}],
}
SAMPLE_R_NEXT = {
    "id": "R-next",
    "label": "需要巡检",
    "enabled": True,
    "conditions": [{"kind": "type", "subject": "?e", "class": L + "HighRiskEquipment"}],
    "conclusions": [{"kind": "type", "subject": "?e", "class": L + "NeedsInspection"}],
}
SAMPLE_DERIVED_1 = [L + "equipment/001", RDF_TYPE, f"<{L}HighRiskEquipment>"]
SAMPLE_DERIVED_2 = [L + "equipment/002", RDF_TYPE, f"<{L}HighRiskEquipment>"]
SAMPLE_EXPECTED = [SAMPLE_DERIVED_1, SAMPLE_DERIVED_2]


def _rule_test(actor, project, **overrides):
    request = {
        "ontologyTriples": list(SAMPLE_ONTOLOGY),
        "inputTriples": list(SAMPLE_INPUT),
        "rules": [dict(SAMPLE_R_RISK)],
        "expectedOutputs": [list(triple) for triple in SAMPLE_EXPECTED],
    }
    request.update(overrides)
    state = learning(actor, "project.quality.read", {"projectId": project, "ruleTest": request})
    return state["ruleTestResult"]


def test_project_quality_read_rule_test_matrix(owned):
    actor, store = owned
    project = open_blank(actor, "样本测试")
    seed_quality(store, project)
    revision_before = store.project_get(project)["projectRevision"]
    jobs_before = store._db.execute("SELECT count(*) FROM jobs").fetchone()[0]

    # RDFS-triggering rule sample: rule outputs and RDFS outputs are reported
    # separately, and the sample matches the expected closure exactly.
    sample = _rule_test(actor, project)
    assert sample["valid"] is True
    assert sample["matchesExpected"] is True
    assert sample["actualOutputs"] == SAMPLE_EXPECTED
    assert sample["missingOutputs"] == [] and sample["unexpectedOutputs"] == []
    assert sample["diagnostics"] == []
    assert [L + "person/L02", RDF_TYPE, f"<{L}Person>"] in sample["rdfsOutputs"]
    assert sample["ruleTraces"] and sample["ruleTraces"][0]["rule"] == "R-risk"

    # Static rule chain detection warns RULE_CHAIN_UNSUPPORTED for the consumer.
    chained = _rule_test(actor, project, rules=[dict(SAMPLE_R_RISK), dict(SAMPLE_R_NEXT)])
    assert chained["valid"] is True
    assert any(text.startswith("RULE_CHAIN_UNSUPPORTED:R-next") for text in chained["warnings"])
    assert all(t[2] != f"<{L}NeedsInspection>" for t in chained["actualOutputs"])

    # Order- and duplicate-independent expected comparison.
    reordered = _rule_test(
        actor,
        project,
        expectedOutputs=[
            list(SAMPLE_DERIVED_2),
            list(SAMPLE_DERIVED_1),
            list(SAMPLE_DERIVED_1),
        ],
    )
    assert reordered["matchesExpected"] is True
    assert reordered["expectedOutputs"] == SAMPLE_EXPECTED

    # A wrong expectation reports precise missing/unexpected deltas.
    mismatched = _rule_test(
        actor,
        project,
        expectedOutputs=[[L + "equipment/001", RDF_TYPE, f"<{L}Flagged>"]],
    )
    assert mismatched["valid"] is True and mismatched["matchesExpected"] is False
    assert mismatched["missingOutputs"] == [[L + "equipment/001", RDF_TYPE, f"<{L}Flagged>"]]
    assert mismatched["unexpectedOutputs"] == SAMPLE_EXPECTED

    # Structurally invalid statements converge into precise diagnostics.
    invalid = _rule_test(
        actor,
        project,
        inputTriples=[*SAMPLE_INPUT, [L + "equipment/009", L + "name", "裸字符串"]],
    )
    assert invalid["valid"] is False and invalid["matchesExpected"] is False
    assert len(invalid["diagnostics"]) == 1
    diagnostic = invalid["diagnostics"][0]
    assert diagnostic["stage"] == "input"
    assert diagnostic["index"] == 9
    assert diagnostic["ruleId"] is None
    assert diagnostic["field"] == "2"
    assert diagnostic["code"] in {"INVALID_TERM", "NON_CANONICAL_TERM", "INVALID_TEXT"}

    # An unbound conclusion variable pinpoints the offending rule slot.
    unbound = _rule_test(
        actor,
        project,
        rules=[
            {
                **SAMPLE_R_RISK,
                "conclusions": [
                    {"kind": "type", "subject": "?never_bound", "class": L + "HighRiskEquipment"}
                ],
            }
        ],
    )
    assert unbound["valid"] is False
    assert [(d["stage"], d["index"], d["ruleId"], d["code"]) for d in unbound["diagnostics"]] == [
        ("rule", 0, "R-risk", "UNBOUND_VARIABLE")
    ]

    # The sample stays pure memory work: no revision bump, no persisted rows.
    assert store.project_get(project)["projectRevision"] == revision_before
    assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == jobs_before


def test_each_fr504_template_executes_real_shacl_pass_and_fail_cases(owned):
    """B2-06: all five templates compile to parseable SHACL and really pass /
    fail through validation.execute; all six comparison operators separate
    the (1,2),(2,2),(3,2) score facts through real reasoning.execute."""
    from rdflib import Graph

    actor, store = owned

    def equipment_type(index):
        return {
            "subject": L + f"e/{index}",
            "predicate": RDF_TYPE,
            "object": f"<{L}Equipment>",
        }

    def name_fact(index, value):
        return {"subject": L + f"e/{index}", "predicate": L + "name", "object": value}

    def score_fact(index, value):
        return {
            "subject": L + f"e/{index}",
            "predicate": L + "score",
            "object": f'"{value}"^^<http://www.w3.org/2001/XMLSchema#integer>',
        }

    tpl_ontology = [
        PERMUTATION_ONTOLOGY[0],  # Equipment owl:Class
        PERMUTATION_ONTOLOGY[3],  # score owl:DatatypeProperty
        {
            "subject": L + "name",
            "predicate": RDF_TYPE,
            "object": "<http://www.w3.org/2002/07/owl#DatatypeProperty>",
        },
    ]
    template_cases = [
        # (template, parameters, path, passing facts, failing facts)
        ("required", {}, L + "name", [name_fact(1, '"泵A"')], []),
        (
            "datatype",
            {"datatype": "http://www.w3.org/2001/XMLSchema#integer"},
            L + "score",
            [score_fact(1, 5)],
            [{"subject": L + "e/1", "predicate": L + "score", "object": '"五"'}],
        ),
        (
            "maxCount",
            {"maxCount": 2},
            L + "name",
            [name_fact(1, '"泵A"')],
            [name_fact(1, '"泵A"'), name_fact(1, '"泵B"'), name_fact(1, '"泵C"')],
        ),
        (
            "allowedValues",
            {"values": ['"a"', '"b"', '"c"']},
            L + "name",
            [name_fact(1, '"a"')],
            [name_fact(1, '"z"')],
        ),
        (
            "numericRange",
            {"minInclusive": "2", "maxInclusive": "9"},
            L + "score",
            [score_fact(1, 5)],
            [score_fact(1, 10)],
        ),
    ]
    for template, parameters, path, passing, failing in template_cases:
        constraint = {
            "schemaVersion": 1,
            "kind": "constraint",
            "id": "tpl",
            "revision": 1,
            "label": template,
            "enabled": True,
            "targetClass": L + "Equipment",
            "path": path,
            "template": template,
            "parameters": parameters,
        }
        turtle_text = compile_constraint_turtle(constraint)
        shapes = Graph()
        shapes.parse(data=turtle_text, format="turtle")
        assert len(shapes) >= 2, template
        outcomes = []
        for index, facts in enumerate((passing, failing)):
            project = open_blank(actor, f"{template}-{index}")
            commit_state(
                store,
                project,
                definitions=[
                    {
                        "layer": "ontology",
                        "id": "tpl.ontology",
                        "value": {"triples": list(tpl_ontology), "singleValuedPredicates": []},
                    },
                    {"layer": "constraint", "id": "tpl", "value": constraint},
                ],
                manual=[equipment_type(1), *facts]
                + ([equipment_type(2), equipment_type(3)] if len(facts) > 2 else []),
            )
            report = result_payload(
                store,
                run_semantic(store, project, "validation.execute", definition="tpl"),
            )["report"]
            outcomes.append(report["conforms"])
        assert outcomes == [True, False], (template, outcomes)

    # numericRange lower bound: score 1 below minInclusive 2 must fail too.
    lower = open_blank(actor, "下界")
    constraint = {
        "schemaVersion": 1,
        "kind": "constraint",
        "id": "tpl",
        "revision": 1,
        "label": "lower",
        "enabled": True,
        "targetClass": L + "Equipment",
        "path": L + "score",
        "template": "numericRange",
        "parameters": {"minInclusive": "2", "maxInclusive": "9"},
    }
    commit_state(
        store,
        lower,
        definitions=[
            {
                "layer": "ontology",
                "id": "tpl.ontology",
                "value": {"triples": list(tpl_ontology), "singleValuedPredicates": []},
            },
            {"layer": "constraint", "id": "tpl", "value": constraint},
        ],
        manual=[equipment_type(1), score_fact(1, 1)],
    )
    report = result_payload(
        store, run_semantic(store, lower, "validation.execute", definition="tpl")
    )["report"]
    assert report["conforms"] is False

    expected_flagged = {
        "eq": ["e/2"],
        "ne": ["e/1", "e/3"],
        "lt": ["e/1"],
        "le": ["e/1", "e/2"],
        "gt": ["e/3"],
        "ge": ["e/2", "e/3"],
    }
    for operator, flagged in expected_flagged.items():
        project = open_blank(actor, f"运算符 {operator}")
        commit_state(
            store,
            project,
            definitions=[
                {
                    "layer": "ontology",
                    "id": "cmp.ontology",
                    "value": {"triples": list(PERMUTATION_ONTOLOGY), "singleValuedPredicates": []},
                },
                _operator_rule(0, operator, 2),
            ],
            manual=list(PERMUTATION_FACTS),
        )
        body = result_payload(store, run_semantic(store, project, "reasoning.execute"))["reasoning"]
        assert sorted(t[0] for t in body["rules"]) == sorted(f"<{L}{item}>" for item in flagged), (
            operator
        )
        assert all(t[2] == f"<{L}Flagged>" for t in body["rules"])


def test_formal_proof_leaves_omitted_matches_explicit_oracle_and_rejects_bad_leaf(owned):
    """B2-N1: omitting proofLeaves re-derives the same audited projection as
    explicit leaves, and a tampered explicit leaf reference is still rejected."""
    from ontolearn_engine import semantic
    from ontolearn_engine.semantic_execution import (
        _definitions,
        _formal_specs,
        _graph,
        execute_request,
    )
    from ontolearn_engine.semantic_formal import project_formal_validation_scope
    from ontolearn_engine.semantic_offline import SemanticError
    from rdflib import Graph

    actor, store = owned
    project = open_blank(actor, "证明叶子")
    commit_state(
        store,
        project,
        definitions=[
            {
                "layer": "ontology",
                "id": "G-base.ontology",
                "value": {
                    "triples": list(G_BASE["ontology"]),
                    "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                },
            },
            FORMAL_R_RISK,
            {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
        ],
        manual=list(G_BASE["facts"]),
    )
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
    assert "proofLeaves" not in payload["reasoning"]

    definitions = _definitions(snapshot)
    facts = _graph(snapshot["state"]["facts"])
    ontology = _graph(
        [
            triple
            for (layer, _identity), value in sorted(definitions.items())
            if layer == "ontology"
            for triple in value["triples"]
        ]
    )
    specs, has_formal = _formal_specs(definitions)
    assert has_formal and specs
    selected = {
        "metadata": {
            "resultId": "0" * 32,
            "kind": "reasoning",
            "inputSnapshotId": snapshot_id,
        },
        "payload": {
            "kind": "reasoning",
            "source": payload["source"],
            "inputSnapshotId": snapshot_id,
            "reasoning": payload["reasoning"],
        },
    }
    omitted = project_formal_validation_scope(facts, ontology, specs=specs, selected=selected)

    original_keys = sorted({semantic._key(triple) for triple in (*facts, *ontology)})
    leaves = [
        {
            "reference": "i05-proof:"
            + hashlib.sha256(
                ("i05-profile-proof-leaf/1\0" + "\0".join(key)).encode("utf-8")
            ).hexdigest(),
            "triple": list(key),
        }
        for key in original_keys
    ]
    explicit = {
        "metadata": selected["metadata"],
        "payload": {
            **selected["payload"],
            "reasoning": {**payload["reasoning"], "proofLeaves": leaves},
        },
    }
    explicit_view = project_formal_validation_scope(facts, ontology, specs=specs, selected=explicit)
    assert sorted(semantic._key(t) for t in omitted.facts) == sorted(
        semantic._key(t) for t in explicit_view.facts
    )
    assert sorted(semantic._key(t) for t in omitted.ontology) == sorted(
        semantic._key(t) for t in explicit_view.ontology
    )
    assert omitted.provenance == explicit_view.provenance

    tampered = [dict(leaf) for leaf in leaves]
    tampered[0] = {**tampered[0], "reference": "i05-proof:" + "0" * 64}
    with pytest.raises(SemanticError):
        project_formal_validation_scope(
            facts,
            ontology,
            specs=specs,
            selected={
                "metadata": selected["metadata"],
                "payload": {
                    **selected["payload"],
                    "reasoning": {**payload["reasoning"], "proofLeaves": tampered},
                },
            },
        )
    assert len(Graph().parse(data=compile_constraint_turtle(NAME_REQUIRED), format="turtle")) >= 2


# --------------------------------------------------------------------------
# 8. R9a regressions: B2-01 legacy 17-key contexts, B2-02 prepare-batch
#    partial rounds, B2-03/04 look-alike and historical-selection rejections,
#    B2-05 diagnostic truncation, B2-06 dual-save-order FR-505 evidence.
# --------------------------------------------------------------------------


def _drive_existing(store, project, job):
    """Drive one already-created queued job through the real worker loop."""

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


def _quality_operation_id(operation_id, suffix):
    """The deterministic chain operation id (mirrors the TS mainline host)."""
    hex_ = hashlib.sha256(f"{operation_id}:{suffix}".encode()).hexdigest()
    variant = format((int(hex_[16], 16) & 0x3) | 0x8, "x")
    return f"{hex_[:8]}-{hex_[8:12]}-4{hex_[13:16]}-{variant}{hex_[17:20]}-{hex_[20:32]}"


def test_fr505_risk_next_dual_save_order_produces_identical_evidence(owned):
    """B2-06/FR-505: [R-risk, R-next] vs [R-next, R-risk] save orders must
    produce identical rule conclusions, evidence and warnings — the blocked
    chain never yields NeedsInspection and R-risk keeps its alarm input."""
    actor, store = owned
    outcomes = []
    for name, order in (
        ("顺序甲", [FORMAL_R_RISK, FORMAL_R_NEXT]),
        ("顺序乙", [FORMAL_R_NEXT, FORMAL_R_RISK]),
    ):
        project = open_blank(actor, name)
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
                            LX_PREREQ_ONTOLOGY[0],
                            LX_PREREQ_ONTOLOGY[4],
                        ],
                        "singleValuedPredicates": G_BASE["singleValuedPredicates"],
                    },
                },
                *order,
                {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
            ],
            manual=list(G_BASE["facts"]),
        )
        body = result_payload(store, run_semantic(store, project, "reasoning.execute"))["reasoning"]
        outcomes.append(
            (
                body["rules"],
                [
                    {"rule": entry["rule"], "result": entry["result"], "inputs": entry["inputs"]}
                    for entry in body["evidence"]
                ],
                body["warnings"],
            )
        )
    rules_a, traces_a, warnings_a = outcomes[0]
    rules_b, traces_b, warnings_b = outcomes[1]
    assert rules_a == rules_b
    assert traces_a == traces_b
    assert warnings_a == warnings_b
    assert any(text.startswith("RULE_CHAIN_UNSUPPORTED:R-next") for text in warnings_a)
    assert all(triple[2] != f"<{L}NeedsInspection>" for triple in rules_a)
    # Both sides carry the same R-risk evidence with the alarm/A01 input.
    risk_traces = [trace for trace in traces_a if trace["rule"] == "R-risk"]
    assert risk_traces
    assert all(
        any(
            triple == [f"<{L}equipment/001>", f"<{L}alarm>", f"<{L}alarm/A01>"]
            for triple in trace["inputs"]
        )
        for trace in risk_traces
    )


def test_b2_01_legacy_seventeen_key_contexts_replay_and_reject_tampering(owned):
    """B2-01: real succeeded derived jobs whose contexts froze the pre-R8a
    17-key selected metadata (full semanticRequest, R7 digest without a
    version stamp) replay idempotently across current/historical/stale and
    evicted source states, while tampered digests and R8+ stamped mismatches
    stay hard INVALID_STATE rejections."""
    from ontolearn_engine.job_store import JobFault, _normalize_legacy_selected_request

    actor, store = owned
    project = open_blank(actor, "B2-01 十七键")
    seed_quality(store, project)

    def legacy_round():
        """One real succeeded derived validation plus its frozen legacy forms."""
        reasoning = run_semantic(store, project, "reasoning.execute")
        source_id = reasoning["resultRef"]["resultId"]
        derived_input = {
            "inputSnapshotId": reasoning["inputSnapshotId"],
            "scope": "asserted+derived",
            "definitionId": "name-required",
            "parametersHash": store.put_blob(project, {"inputSelection": "current"}),
            "derivedResultIds": [source_id],
            "preparedPlanRef": None,
        }
        job = store.create_job(
            project,
            uid(),
            "validation.execute",
            derived_input,
            None,
            semantic_identity(),
            LIMITS,
        )
        terminal = _drive_existing(store, project, job)
        context = store.job_context(terminal["jobId"])
        expected = store.worker_semantic_request(terminal, context)
        assert context["semanticRequestVersion"] == 2
        live = store.result_get(project, source_id)
        assert live["state"] == "current"
        # The exact pre-R8a document: the 17-key result_get metadata form.
        legacy_request = {
            **expected,
            "selected": {
                "metadata": {**expected["selected"]["metadata"], **dict(live)},
                "payload": expected["selected"]["payload"],
            },
        }
        return derived_input, terminal, context, expected, legacy_request, source_id

    def insert_legacy_row(template, stored_context):
        legacy_job_id, legacy_operation = uid(), uid()
        dto = json.loads(json.dumps(template))
        dto["jobId"] = legacy_job_id
        dto["operationId"] = legacy_operation
        fingerprint = digest(stored_context)
        store._db.execute(
            "INSERT INTO jobs VALUES(?,?,?,?,?,?,NULL)",
            (
                legacy_job_id,
                project,
                legacy_operation,
                json.dumps(dto),
                json.dumps(stored_context),
                fingerprint,
            ),
        )
        store._db.execute(
            "INSERT INTO operation_claims VALUES(?,?,?,?,?,NULL)",
            (legacy_operation, project, legacy_job_id, fingerprint, "job"),
        )
        return legacy_job_id, legacy_operation

    def replay(operation, derived_input):
        return store.create_job(
            project,
            operation,
            "validation.execute",
            derived_input,
            None,
            semantic_identity(),
            LIMITS,
        )

    # (1) Pre-R7 full semanticRequest context: replay while the source
    # reasoning is current, then historical (pointer replaced), then stale
    # (domain commit) — always the same accepted job, byte-verified through
    # the 13-key normalization.
    (
        derived_input1,
        terminal1,
        context1,
        expected1,
        legacy_request1,
        source1,
    ) = legacy_round()
    stored1 = {
        key: value
        for key, value in context1.items()
        if key not in ("job", "semanticRequestSha256", "semanticRequestVersion")
    }
    stored1["semanticRequest"] = legacy_request1
    legacy_job1, legacy_operation1 = insert_legacy_row(terminal1, stored1)
    assert replay(legacy_operation1, derived_input1)["jobId"] == legacy_job1
    # The exact comparison _accepted_job runs: the deterministic rebuild
    # equals the normalized legacy document (pre-R7 rows predate the worker
    # digest path, so the replay gate is the authoritative check for them).
    rebuilt1 = store.prepare_semantic_request(
        project,
        "validation.execute",
        derived_input1,
        stored1["parameters"],
        stored1["snapshot"],
        terminal1["implementation"],
        None,
        live=False,
    )
    assert _normalize_legacy_selected_request(stored1["semanticRequest"]) == rebuilt1
    run_semantic(store, project, "reasoning.execute")
    assert store.result_get(project, source1)["state"] == "historical"
    assert replay(legacy_operation1, derived_input1)["jobId"] == legacy_job1
    commit_state(
        store,
        project,
        manual=[{"subject": L + "equipment/001", "predicate": L + "name", "object": '"泵站甲"'}],
    )
    assert store.result_get(project, source1)["state"] == "stale"
    assert replay(legacy_operation1, derived_input1)["jobId"] == legacy_job1

    # (2) R7 digest context without any version stamp: the polymorphic
    # matcher accepts the frozen 17-key digest across all three availability
    # states, and stays authoritative after the stale source is evicted.
    (
        derived_input2,
        terminal2,
        context2,
        expected2,
        legacy_request2,
        source2,
    ) = legacy_round()
    stored2 = {
        key: value
        for key, value in context2.items()
        if key not in ("job", "semanticRequestVersion")
    }
    stored2["semanticRequestSha256"] = digest(legacy_request2)
    legacy_job2, legacy_operation2 = insert_legacy_row(terminal2, stored2)
    assert store.result_get(project, source2)["state"] == "current"
    assert replay(legacy_operation2, derived_input2)["jobId"] == legacy_job2
    rebuilt2 = store.worker_semantic_request(store.get_job(project, legacy_job2), stored2)
    assert digest(rebuilt2) != stored2["semanticRequestSha256"]
    run_semantic(store, project, "reasoning.execute")
    assert store.result_get(project, source2)["state"] == "historical"
    assert replay(legacy_operation2, derived_input2)["jobId"] == legacy_job2
    commit_state(
        store,
        project,
        manual=[{"subject": L + "equipment/002", "predicate": L + "name", "object": '"泵站乙"'}],
    )
    assert store.result_get(project, source2)["state"] == "stale"
    assert replay(legacy_operation2, derived_input2)["jobId"] == legacy_job2
    assert source2 in store.collect_cache()
    assert store.result_get(project, source2)["payloadStatus"] == "evicted"
    assert replay(legacy_operation2, derived_input2)["jobId"] == legacy_job2

    # (3) Tampering stays rejected: a wrong recorded digest is INVALID_STATE,
    # and an R8+ version-stamped context never downgrades to legacy matching.
    (
        derived_input3,
        terminal3,
        context3,
        expected3,
        legacy_request3,
        source3,
    ) = legacy_round()
    tampered = {
        key: value
        for key, value in context3.items()
        if key not in ("job", "semanticRequestVersion")
    }
    tampered["semanticRequestSha256"] = "0" * 64
    tampered_job, tampered_operation = insert_legacy_row(terminal3, tampered)
    with pytest.raises(JobFault, match="INVALID_STATE"):
        replay(tampered_operation, derived_input3)
    downgraded = {
        key: value
        for key, value in context3.items()
        if key not in ("job", "semanticRequestVersion")
    }
    downgraded["semanticRequestSha256"] = digest(legacy_request3)
    downgraded["semanticRequestVersion"] = 2
    with pytest.raises(JobFault, match="INVALID_STATE"):
        store.worker_semantic_request(terminal3, downgraded)

    # (4) The true 17-key result_get form digest-matches through the
    # polymorphic matcher, and the pure projection rejects non-legacy shapes.
    live17 = dict(store.result_get(project, source3))
    true17 = {
        **expected3,
        "selected": {"metadata": live17, "payload": expected3["selected"]["payload"]},
    }
    stamped = {
        key: value
        for key, value in context3.items()
        if key not in ("job", "semanticRequestVersion")
    }
    stamped["semanticRequestSha256"] = digest(true17)
    assert store._matches_semantic_request_digest(project, derived_input3, expected3, stamped)
    query_shaped = {
        "snapshot": context3["snapshot"],
        "selected": {"metadata": dict(live17), "payload": expected3["selected"]["payload"]},
    }
    normalized = _normalize_legacy_selected_request(query_shaped)
    assert normalized == {
        **query_shaped,
        "selected": {
            "metadata": expected3["selected"]["metadata"],
            "payload": expected3["selected"]["payload"],
        },
    }
    evicted_doc = {
        "selected": {
            "metadata": {**live17, "payloadStatus": "evicted"},
            "payload": expected3["selected"]["payload"],
        }
    }
    assert _normalize_legacy_selected_request(evicted_doc) == evicted_doc
    evil_doc = {
        "selected": {
            "metadata": {**live17, "evil": True},
            "payload": expected3["selected"]["payload"],
        }
    }
    assert _normalize_legacy_selected_request(evil_doc) == evil_doc


def test_b2_02_prepare_batch_partial_rounds_never_read_compliant(owned):
    """B2-02/N2: a prepare-batch round that is still partial — only one
    constraint finished while another runs or was never enqueued, or the chain
    never got past its reasoning phase — must read conforms None with the
    missing constraints unverified, never as a completed compliant check;
    direct-call same-snapshot running rounds block older evidence too, and
    constraintVersions exposes every checked constraint's version."""
    actor, store = owned
    project = open_blank(actor, "B2-02 批次")
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
            {
                "layer": "rule",
                "id": "R-risk",
                "value": {"enabled": True, "when": R_RISK_WHEN, "then": R_RISK_THEN},
            },
            {"layer": "constraint", "id": "name-required", "value": dict(NAME_REQUIRED)},
            {
                "layer": "constraint",
                "id": "assigned-to-required",
                "value": dict(ASSIGNED_TO_REQUIRED),
            },
        ],
        manual=[*G_BASE["facts"], *LX_PREREQ_FACTS],
    )
    internal = store._project(project)

    def prepare_round():
        return learning(
            actor,
            "project.quality.prepare",
            {
                "projectId": project,
                "operationId": uid(),
                "selection": {"kind": "current"},
                "validationScope": "asserted",
            },
        )

    def validation_index(prepared, definition_id):
        return next(
            index
            for index, item in enumerate(prepared["validationInputs"])
            if item["definitionId"] == definition_id
        )

    def run_round(prepared, *, skip=(), running=()):
        """Create the batch's jobs with the manifest-derived operation ids."""
        reasoning = store.create_job(
            project,
            _quality_operation_id(prepared["operationId"], "reasoning"),
            "reasoning.execute",
            prepared["reasoningInput"],
            None,
            semantic_identity(),
            LIMITS,
        )
        _drive_existing(store, project, reasoning)
        for index, validation_input in enumerate(prepared["validationInputs"]):
            if index in skip:
                continue
            job = store.create_job(
                project,
                _quality_operation_id(prepared["operationId"], f"validation:{index}"),
                "validation.execute",
                validation_input,
                None,
                semantic_identity(),
                LIMITS,
            )
            if index in running:
                store.start_job(job["jobId"])
            else:
                _drive_existing(store, project, job)

    def read_state():
        return learning(actor, "project.quality.read", {"projectId": project})

    # A complete earlier round: both constraints really ran and finished.
    run_round(prepare_round())
    state = read_state()
    assert state["validation"]["conforms"] is False  # assigned-to-required 违规
    assert state["validation"]["checkedConstraintIds"] == [
        "assigned-to-required",
        "name-required",
    ]
    assert state["validation"]["unverifiedConstraintIds"] == []
    vector = store.vector(internal)
    assert state["validation"]["constraintVersions"] == [
        {
            "definitionId": "assigned-to-required",
            "version": vector.get("constraint:assigned-to-required", 0),
        },
        {"definitionId": "name-required", "version": vector.get("constraint:name-required", 0)},
    ]

    # Scenario 1: this round finished name-required while assigned-to-required
    # is still running: no verdict, the running constraint is unverified.
    partial = prepare_round()
    assigned_index = validation_index(partial, "assigned-to-required")
    run_round(partial, running={assigned_index})
    state = read_state()
    assert state["validation"]["conforms"] is None
    assert state["validation"]["checkedConstraintIds"] == ["name-required"]
    assert state["validation"]["unverifiedConstraintIds"] == ["assigned-to-required"]
    assert state["validation"]["failedConstraintIds"] == []

    # Scenario 2: assigned-to-required never enqueued at all: the batch plan
    # still keeps it unverified — no fake compliance from the finished one.
    unqueued = prepare_round()
    run_round(unqueued, skip={validation_index(unqueued, "assigned-to-required")})
    state = read_state()
    assert state["validation"]["conforms"] is None
    assert state["validation"]["checkedConstraintIds"] == ["name-required"]
    assert state["validation"]["unverifiedConstraintIds"] == ["assigned-to-required"]

    # Scenario 3: the chain never got past its queued reasoning phase: every
    # planned constraint is unverified and the previous same-snapshot round's
    # successes never masquerade as this round's completion.
    stalled = prepare_round()
    store.create_job(
        project,
        _quality_operation_id(stalled["operationId"], "reasoning"),
        "reasoning.execute",
        stalled["reasoningInput"],
        None,
        semantic_identity(),
        LIMITS,
    )
    state = read_state()
    assert state["validation"]["conforms"] is None
    assert state["validation"]["checkedConstraintIds"] == []
    assert state["validation"]["unverifiedConstraintIds"] == [
        "assigned-to-required",
        "name-required",
    ]
    assert state["validation"]["definitionId"] == "partial-constraints"

    # Scenario 4 (direct calls, no prepare manifest): a same-snapshot rerun
    # left running anchors the read; the older terminal evidence of the very
    # same constraint must not join the cohort as if this round finished.
    snapshot_id = store.project_get(project)["inputSnapshotId"]
    direct_input = {
        "inputSnapshotId": snapshot_id,
        "scope": "asserted",
        "definitionId": "name-required",
        "parametersHash": store.put_blob(project, {"inputSelection": "current"}),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    direct_done = store.create_job(
        project, uid(), "validation.execute", direct_input, None, semantic_identity(), LIMITS
    )
    _drive_existing(store, project, direct_done)
    direct_running = store.create_job(
        project, uid(), "validation.execute", direct_input, None, semantic_identity(), LIMITS
    )
    store.start_job(direct_running["jobId"])
    state = read_state()
    assert state["validation"]["conforms"] is None
    assert state["validation"]["checkedConstraintIds"] == []
    assert state["validation"]["unverifiedConstraintIds"] == [
        "assigned-to-required",
        "name-required",
    ]


def test_b2_03_other_equipment_lookalike_rejected(owned):
    """B2-03: a Turtle shape that mentions Equipment only in a comment while
    targeting OtherEquipment produces the same two violations, yet the strict
    per-snapshot SHACL-graph verification refuses it as the Step-2 shape."""
    actor, store = owned
    origins = {
        "urn:ontolearn:learning:person/L01": "asserted",
        "urn:ontolearn:learning:person/L02": "derived",
    }
    project = open_blank(actor, "B2-03 替身")
    seed_quality(store, project)
    _run_v01_steps(store, project)
    other_turtle = compile_constraint_turtle(
        {**ASSIGNED_TO_REQUIRED, "targetClass": L + "OtherEquipment"}
    )
    sabotaged = other_turtle + "\n# <urn:ontolearn:learning:Equipment> 注释冒充\n"
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
            {
                "layer": "constraint",
                "id": "assigned-to-required",
                "value": {"enabled": True, "turtle": sabotaged},
            },
        ],
        manual=[
            *LX_PREREQ_FACTS,
            {
                "subject": L + "equipment/002",
                "predicate": RDF_TYPE,
                "object": f"<{L}OtherEquipment>",
            },
            {
                "subject": L + "equipment/003",
                "predicate": RDF_TYPE,
                "object": f"<{L}OtherEquipment>",
            },
        ],
    )
    run_semantic(store, project, "reasoning.execute")  # Step 1.
    before = result_payload(
        store,
        run_semantic(store, project, "validation.execute", definition="assigned-to-required"),
    )["report"]
    assert not before["conforms"]
    assert {row["focus"] for row in before["violations"]} == {
        f"<{L}equipment/002>",
        f"<{L}equipment/003>",
    }
    commit_state(store, project, manual=list(LX_REPAIR_FACTS))
    run_semantic(store, project, "reasoning.execute")  # Step 3.
    after = result_payload(
        store,
        run_semantic(store, project, "validation.execute", definition="assigned-to-required"),
    )["report"]
    assert after["conforms"] is True and after["violations"] == []
    result = check_task(actor, "quality", selected_origins=origins)
    assert result["checkStatus"] == "needs-repair"
    assert "请完整完成 LX-01 步骤 1–4" in ";".join(result["feedback"]["repairs"])


def test_b2_03_extra_repair_fact_rejected(owned):
    """B2-03: zero-tolerance repair diff — one extra non-assignedTo fact
    (person/L99 a Person) alongside the two repairs fails LX-01."""
    actor, store = owned
    origins = {
        "urn:ontolearn:learning:person/L01": "asserted",
        "urn:ontolearn:learning:person/L02": "derived",
    }
    project = open_blank(actor, "B2-03 额外事实")
    seed_quality(store, project)
    _run_v01_steps(store, project)
    _lx_prereq_commit(store, project)
    run_semantic(store, project, "reasoning.execute")
    run_semantic(store, project, "validation.execute", definition="assigned-to-required")
    commit_state(
        store,
        project,
        manual=[
            *LX_REPAIR_FACTS,
            {
                "subject": L + "person/L99",
                "predicate": RDF_TYPE,
                "object": f"<{L}Person>",
            },
        ],
    )
    run_semantic(store, project, "reasoning.execute")
    run_semantic(store, project, "validation.execute", definition="assigned-to-required")
    result = check_task(actor, "quality", selected_origins=origins)
    assert result["checkStatus"] == "needs-repair"
    assert "修复集合必须恰好是" in ";".join(result["feedback"]["repairs"])


def _historical_validation(store, project, definition):
    """One real succeeded validation run with inputSelection=historical."""
    snapshot_id = store.project_get(project)["inputSnapshotId"]
    input_ = {
        "inputSnapshotId": snapshot_id,
        "scope": "asserted",
        "definitionId": definition,
        "parametersHash": store.put_blob(project, {"inputSelection": "historical"}),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    job = store.create_job(
        project, uid(), "validation.execute", input_, None, semantic_identity(), LIMITS
    )
    return _drive_existing(store, project, job)


def test_b2_04_turtle_comment_and_historical_selection_rejected(owned):
    """B2-04: the strict SHACL graph parse rejects comment-spoofed Turtle
    targets, and historical-selection replays never satisfy V-01 or the
    frozen current-asserted transfer-repair expectation."""
    from ontolearn_engine.project.learning_host import LearningHost

    actor, store = owned

    def snap_of(payload):
        return {
            "state": {
                "definitions": [
                    {
                        "layer": "constraint",
                        "id": "assigned-to-required",
                        "payload": json.dumps(payload),
                    }
                ]
            }
        }

    other_turtle = compile_constraint_turtle(
        {**ASSIGNED_TO_REQUIRED, "targetClass": L + "OtherEquipment"}
    )
    sabotaged = other_turtle + "\n# <urn:ontolearn:learning:Equipment> 注释冒充\n"
    assert not LearningHost._is_constraint_target(
        snap_of({"enabled": True, "turtle": sabotaged}), "assigned-to-required", L + "assignedTo"
    )
    genuine = compile_constraint_turtle(ASSIGNED_TO_REQUIRED)
    assert LearningHost._is_constraint_target(
        snap_of({"enabled": True, "turtle": genuine}), "assigned-to-required", L + "assignedTo"
    )

    # (b) V-01 with only historical-selection runs: the tool stays unavailable
    # and the quality task cannot pass on replayed evidence.
    origins = {
        "urn:ontolearn:learning:person/L01": "asserted",
        "urn:ontolearn:learning:person/L02": "derived",
    }
    project = open_blank(actor, "B2-04 历史选择")
    seed_quality(store, project)
    name_003 = _fact_id(store, project, L + "equipment/003", L + "name")
    internal = store._project(project)
    store.commit(internal, store.revision(internal), uid(), uid(), remove=[name_003])
    _historical_validation(store, project, "name-required")
    commit_state(
        store,
        project,
        manual=[{"subject": L + "equipment/003", "predicate": L + "name", "object": '"备用泵C"'}],
    )
    _historical_validation(store, project, "name-required")
    run_semantic(store, project, "reasoning.execute")
    result = check_task(actor, "quality", selected_origins=origins)
    assert result["checkStatus"] == "tool-not-successful"
    assert result["operationComplete"] is False

    # (c) transfer-repair over two historical-selection runs reads the
    # historical-asserted scope and the frozen expectation rejects it.
    repair_data = TRANSFER["repair"]
    transfer = open_blank(actor, "B2-04 迁移历史")
    commit_state(
        store,
        transfer,
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
    _historical_validation(store, transfer, "name-required")
    commit_state(
        store,
        transfer,
        manual=[{"subject": L + "equipment/102", "predicate": L + "name", "object": '"供水泵"'}],
    )
    _historical_validation(store, transfer, "name-required")
    result = check_task(actor, "transfer-repair")
    assert result["checkStatus"] == "needs-repair"
    assert result["operationComplete"] is False


def test_b2_05_over_limit_diagnostics_truncate_with_exact_count(owned):
    """B2-05: 256 invalid inputs + 1 invalid expected (257 diagnostics) return
    the structured first 256 diagnostics plus omittedDiagnosticCount=1 and a
    DIAGNOSTICS_TRUNCATED marker, never INVALID_STATE."""
    actor, store = owned
    project = open_blank(actor, "诊断截断")
    seed_quality(store, project)
    request = {
        "ontologyTriples": [],
        "inputTriples": [
            [L + f"equipment/{index:03d}", L + "name", "裸字符串"] for index in range(256)
        ],
        "rules": [dict(SAMPLE_R_RISK)],
        "expectedOutputs": [[L + "equipment/999", RDF_TYPE, "不是规范术语"]],
    }
    state = learning(actor, "project.quality.read", {"projectId": project, "ruleTest": request})
    sample = state["ruleTestResult"]
    assert sample["valid"] is False
    assert sample["matchesExpected"] is False
    assert len(sample["diagnostics"]) == 256
    assert all(item["stage"] == "input" for item in sample["diagnostics"])
    assert sample["omittedDiagnosticCount"] == 1
    assert any(text.startswith("DIAGNOSTICS_TRUNCATED:") for text in sample["warnings"])
    assert len(sample["warnings"]) <= 256


def test_v01_survives_subsequent_derived_runs_and_initial_default_scope_mistake(tmp_path):
    """W3A-R1-IMP-2: asserted V-01 repair pair survives accidental initial
    asserted+derived run and later full-project asserted+derived checks, while
    pure derived, mixed-scope, or re-broken V-01 runs still fail strictly."""
    from contextlib import contextmanager
    from types import SimpleNamespace

    from ontolearn_engine.project.learning_host import LearningHost

    origins = {
        "urn:ontolearn:learning:person/L01": "asserted",
        "urn:ontolearn:learning:person/L02": "derived",
    }

    @contextmanager
    def isolated_case(slug):
        store = JobStore(tmp_path / f"{slug}.sqlite", contract=CONTRACT, target_format=3)
        actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
        assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        host = LearningHost(actor.mainline)
        try:
            yield actor, store, host
        finally:
            actor.mainline.close()
            store.close()

    def complete_r05_and_lx01(store, project):
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
                {
                    "layer": "constraint",
                    "id": "assigned-to-required",
                    "value": dict(ASSIGNED_TO_REQUIRED),
                },
            ],
            manual=list(LX_PREREQ_FACTS),
        )
        run_semantic(store, project, "reasoning.execute")
        run_semantic(store, project, "validation.execute", definition="assigned-to-required")
        commit_state(store, project, manual=list(LX_REPAIR_FACTS))
        run_semantic(store, project, "reasoning.execute")
        run_semantic(store, project, "validation.execute", definition="assigned-to-required")

    def run_all_constraints_derived(store, project):
        r_job = run_semantic(store, project, "reasoning.execute")
        rid = r_job["resultRef"]["resultId"]
        run_semantic(
            store,
            project,
            "validation.execute",
            definition="name-required",
            scope="asserted+derived",
            derived=[rid],
        )
        if any(
            d["id"] == "assigned-to-required"
            for d in store.state(store._project(project))["definitions"]
        ):
            run_semantic(
                store,
                project,
                "validation.execute",
                definition="assigned-to-required",
                scope="asserted+derived",
                derived=[rid],
            )
        return r_job

    def v01_evidence(store, host, project):
        internal = store._project(project)
        snap = store.project_get(project)["inputSnapshotId"]
        ctx = SimpleNamespace(attempt_id="probe", project_id=project, task_id="quality")
        return host.b3_evidences(store, project, internal, ctx, snap, 0, None, origins)["V-01"]

    # Scenarios 1 & 2: accidental initial asserted+derived run before asserted
    # broken/repaired pair, followed by full-project asserted+derived checks.
    with isolated_case("p1") as (actor, store, host):
        p1 = open_blank(actor, "V01 首误及后续派生")
        seed_quality(store, p1)
        run_all_constraints_derived(store, p1)
        name_003 = _fact_id(store, p1, L + "equipment/003", L + "name")
        internal1 = store._project(p1)
        store.commit(internal1, store.revision(internal1), uid(), uid(), remove=[name_003])
        run_semantic(store, p1, "validation.execute", definition="name-required", scope="asserted")
        commit_state(
            store,
            p1,
            manual=[
                {"subject": L + "equipment/003", "predicate": L + "name", "object": '"备用泵C"'}
            ],
        )
        run_semantic(store, p1, "validation.execute", definition="name-required", scope="asserted")
        complete_r05_and_lx01(store, p1)
        assert check_task(actor, "quality", selected_origins=origins)["checkStatus"] == "passed"
        run_all_constraints_derived(store, p1)
        assert check_task(actor, "quality", selected_origins=origins)["checkStatus"] == "passed"
        ev1 = v01_evidence(store, host, p1)
        assert ev1.status == "succeeded" and ev1.payload["includeInferred"] is False

    # Scenario 3: pure asserted+derived before/after pair still fails (includeInferred=True).
    with isolated_case("p3") as (actor, store, host):
        p3 = open_blank(actor, "V01 纯派生")
        seed_quality(store, p3)
        name_003_3 = _fact_id(store, p3, L + "equipment/003", L + "name")
        internal3 = store._project(p3)
        store.commit(internal3, store.revision(internal3), uid(), uid(), remove=[name_003_3])
        run_all_constraints_derived(store, p3)
        commit_state(
            store,
            p3,
            manual=[
                {"subject": L + "equipment/003", "predicate": L + "name", "object": '"备用泵C"'}
            ],
        )
        run_all_constraints_derived(store, p3)
        complete_r05_and_lx01(store, p3)
        r3 = check_task(actor, "quality", selected_origins=origins)
        assert r3["checkStatus"] == "needs-repair" and r3["operationComplete"] is False
        assert v01_evidence(store, host, p3).payload["includeInferred"] is True

    # Scenario 4: asserted broken run + only asserted+derived repaired run still fails.
    with isolated_case("p4") as (actor, store, host):
        p4 = open_blank(actor, "V01 混合范围")
        seed_quality(store, p4)
        name_003_4 = _fact_id(store, p4, L + "equipment/003", L + "name")
        internal4 = store._project(p4)
        store.commit(internal4, store.revision(internal4), uid(), uid(), remove=[name_003_4])
        run_semantic(store, p4, "validation.execute", definition="name-required", scope="asserted")
        commit_state(
            store,
            p4,
            manual=[
                {"subject": L + "equipment/003", "predicate": L + "name", "object": '"备用泵C"'}
            ],
        )
        run_all_constraints_derived(store, p4)
        complete_r05_and_lx01(store, p4)
        r4 = check_task(actor, "quality", selected_origins=origins)
        assert r4["checkStatus"] == "needs-repair" and r4["operationComplete"] is False
        assert v01_evidence(store, host, p4).payload["includeInferred"] is True

    # Scenario 5: re-breaking 003 name after passing and running either
    # asserted+derived or asserted fails V-01.
    for idx, scope in enumerate(("asserted+derived", "asserted")):
        with isolated_case(f"p5_{idx}") as (actor, store, _host):
            p5 = open_blank(actor, f"V01 重破坏 {scope}")
            seed_quality(store, p5)
            run_semantic(store, p5, "reasoning.execute")
            name_003_5 = _fact_id(store, p5, L + "equipment/003", L + "name")
            internal5 = store._project(p5)
            store.commit(internal5, store.revision(internal5), uid(), uid(), remove=[name_003_5])
            run_semantic(
                store, p5, "validation.execute", definition="name-required", scope="asserted"
            )
            commit_state(
                store,
                p5,
                manual=[
                    {
                        "subject": L + "equipment/003",
                        "predicate": L + "name",
                        "object": '"备用泵C"',
                    }
                ],
            )
            run_semantic(
                store, p5, "validation.execute", definition="name-required", scope="asserted"
            )
            complete_r05_and_lx01(store, p5)
            assert check_task(actor, "quality", selected_origins=origins)["checkStatus"] == "passed"
            name_rebreak = _fact_id(store, p5, L + "equipment/003", L + "name")
            store.commit(internal5, store.revision(internal5), uid(), uid(), remove=[name_rebreak])
            if scope == "asserted+derived":
                run_all_constraints_derived(store, p5)
            else:
                run_semantic(
                    store, p5, "validation.execute", definition="name-required", scope="asserted"
                )
            r5 = check_task(actor, "quality", selected_origins=origins)
            assert r5["checkStatus"] != "passed" and r5["operationComplete"] is False
