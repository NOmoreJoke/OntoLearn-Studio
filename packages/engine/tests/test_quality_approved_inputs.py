"""Approved T09 immutable *inputs* adapted to private plans, never executed results.

No T09 service/Store helper is imported. Expected fields remain acceptance oracles
and are never copied into an actual result, Store, trace, or current-result view.
"""

import hashlib
import json
from pathlib import Path

import pytest
from ontolearn_engine.quality import build_plan, validate_definition
from ontolearn_engine.quality.planning import validate_statement

ROOT = Path(__file__).parents[3]
BUNDLE = ROOT / "tests/fixtures/quality/approved-T09-873c8c0"
MANIFEST_SHA = "aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e"
MANIFEST = json.loads((BUNDLE / "manifest.json").read_bytes())
BASE = json.loads((BUNDLE / "tests/fixtures/product-baselines/G-base.json").read_bytes())
CASES = json.loads((BUNDLE / "tests/fixtures/product-baselines/cases.json").read_bytes())["cases"]
TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
OWL = "http://www.w3.org/2002/07/owl#"


def test_manifest_and_prd_are_exact_approved_source_bytes():
    assert hashlib.sha256((BUNDLE / "manifest.json").read_bytes()).hexdigest() == MANIFEST_SHA
    assert MANIFEST["version"] == "prd-v0.6-learning-1"
    assert len(MANIFEST["files"]) == 17
    assert (
        hashlib.sha256((ROOT / MANIFEST["source"]["path"]).read_bytes()).hexdigest()
        == (MANIFEST["source"]["sha256"])
    )


@pytest.mark.parametrize("relative,sha", list(MANIFEST["files"].items()))
def test_every_copied_input_matches_fixed_873_bytes(relative, sha):
    assert hashlib.sha256((BUNDLE / relative).read_bytes()).hexdigest() == sha


def catalog(ontology):
    result = {"classes": [], "properties": []}
    for triple in ontology:
        validate_statement([triple["subject"], triple["predicate"], triple["object"]])
        if triple["predicate"] != TYPE:
            continue
        if triple["object"] == f"<{OWL}Class>":
            result["classes"].append(triple["subject"])
        elif triple["object"] in (f"<{OWL}ObjectProperty>", f"<{OWL}DatatypeProperty>"):
            result["properties"].append(triple["subject"])
    return result


def pattern(triple):
    if triple["predicate"] == TYPE:
        assert triple["object"].startswith("<") and triple["object"].endswith(">")
        return {"kind": "type", "subject": triple["subject"], "class": triple["object"][1:-1]}
    return {
        "kind": "property",
        "subject": triple["subject"],
        "path": triple["predicate"],
        "object": triple["object"],
    }


def rule(source):
    # Explicit test-only structural adapter; not a production persistence format.
    return {
        "schemaVersion": 1,
        "kind": "rule",
        "id": source["id"],
        "label": source["id"],
        "revision": source["version"],
        "enabled": source["enabled"],
        "conditions": [pattern(value) for value in source["conditions"]],
        "conclusions": [pattern(value) for value in source["conclusions"]],
    }


def constraint(source):
    assert source["minCount"] == 1
    assert source["scope"] == "current-asserted"
    assert source["includeInferred"] is False
    return {
        "schemaVersion": 1,
        "kind": "constraint",
        "id": source["id"],
        "label": source["id"],
        "revision": 1,
        "enabled": True,
        "targetClass": source["targetClass"],
        "path": source["path"],
        "template": "required",
        "parameters": {},
    }


def context(case_id):
    # Synthetic unit-test context, not a Store snapshot or claimed real project.
    return {
        "projectId": "unit-t05-approved-input-plan",
        "inputSnapshotId": "input:" + case_id,
        "projectRevision": 0,
        "dependencyVector": {"facts:asserted": 0, "ontology:core": 0, "rule:R-risk": 0},
    }


def test_approved_base_validates_without_changing_alarm_join_or_string_identity():
    definitions = [constraint(value) for value in BASE["constraints"]]
    definitions += [rule(value) for value in BASE["rules"]]
    for definition in definitions:
        assert validate_definition(definition).payload() == definition
    assert definitions[-1]["conditions"] == [
        {"kind": "type", "subject": "?equipment", "class": "urn:ontolearn:learning:Equipment"},
        {
            "kind": "property",
            "subject": "?equipment",
            "path": "urn:ontolearn:learning:alarm",
            "object": "?alarm",
        },
        {
            "kind": "property",
            "subject": "?alarm",
            "path": "urn:ontolearn:learning:level",
            "object": '"High"',
        },
        {
            "kind": "property",
            "subject": "?alarm",
            "path": "urn:ontolearn:learning:status",
            "object": '"Open"',
        },
    ]
    for fact in BASE["facts"]:
        validate_statement([fact["subject"], fact["predicate"], fact["object"]])
    plan = build_plan(
        definitions,
        context=context("G-base"),
        catalog=catalog(BASE["ontology"]),
        validation_scope="asserted",
    )
    assert plan["executionState"] == "not-executed"
    assert "actual" not in plan
    assert any(fact["subject"].endswith("equipment/001") for fact in BASE["facts"])


@pytest.mark.parametrize("case_id", ["R-05", "R-06"])
def test_approved_save_orders_produce_same_unexecuted_plan_and_chain_warning(case_id):
    case = next(value for value in CASES if value["id"] == case_id)
    ontology = list(BASE["ontology"])
    rules = [rule(value) for value in BASE["rules"]]
    orders = []
    for step in case["steps"]:
        if step["op"] == "add-ontology":
            ontology += step["triples"]
        elif step["op"] == "save-enabled-rule":
            rules.append(rule(step["rule"]))
        elif step["op"] == "run-save-orders":
            orders = step["orders"]
    by_id = {value["id"]: value for value in rules}
    plans = [
        build_plan(
            [by_id[key] for key in order],
            context=context(case_id),
            catalog=catalog(ontology),
            validation_scope="asserted",
        )
        for order in orders
    ]
    assert plans and all(value == plans[0] for value in plans)
    assert {value["id"] for value in plans[0]["definitions"] if value["enabled"]} == {
        "R-risk",
        "R-next",
    }
    assert any(
        warning["producerRuleId"] == "R-risk"
        and warning["consumerRuleId"] == "R-next"
        and warning["message"] == "当前版本不支持规则链"
        for warning in plans[0]["warnings"]
    )
    assert all(plan["executionState"] == "not-executed" for plan in plans)
    assert case["status"] == "input-and-expectation-prepared-runtime-pending"


def test_all_g2_quality_cases_retain_runtime_pending_and_no_actual_results():
    ids = {"V-01", "R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "O-01"}
    selected = [case for case in CASES if case["id"] in ids]
    assert {case["id"] for case in selected} == ids
    for case in selected:
        assert case["baseline"] == "G-base"
        assert case["status"] == "input-and-expectation-prepared-runtime-pending"
        assert "actual" not in case
        assert case["failurePath"]["toolUnavailable"] == "pending-dependency"
