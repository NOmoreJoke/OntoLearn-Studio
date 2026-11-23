"""Validate FR505 extension inputs; these tests deliberately never run inference."""

import json
import operator
import re
from pathlib import Path

import pytest
from ontolearn_engine.quality import build_plan, validate_definition
from ontolearn_engine.quality.planning import validate_statement

FIXTURE = json.loads(
    (Path(__file__).parents[3] / "tests/fixtures/quality/fr505-extension-cases.json").read_text(
        encoding="utf-8"
    )
)


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["id"])
def test_extension_input_and_plan_are_well_formed_without_filling_actual(case):
    for rule in case["rules"]:
        assert validate_definition(rule).payload() == rule
    for index, statement in enumerate(case["inputTriples"]):
        validate_statement(statement, ("inputTriples", index))
    for index, statement in enumerate(case["expectedRuleOutputs"]):
        validate_statement(statement, ("expectedRuleOutputs", index))
    context = {
        "projectId": "unit-fr505-proposal",
        "inputSnapshotId": case["id"],
        "projectRevision": 0,
        "dependencyVector": {"facts:asserted": 0, "ontology:core": 0},
    }
    forward = build_plan(
        case["rules"], context=context, catalog=FIXTURE["catalog"], validation_scope="asserted"
    )
    reverse = build_plan(
        list(reversed(case["rules"])),
        context=context,
        catalog=FIXTURE["catalog"],
        validation_scope="asserted",
    )
    assert forward == reverse
    assert forward["executionState"] == "not-executed"
    assert "actual" not in forward
    assert case["runtimeStatus"] == "pending-approved-executor"
    assert "actual" not in case
    # Expected facts never enter the plan (even a plan is not runtime evidence).
    assert "expectedRuleOutputs" not in forward


def integer_operands(case):
    pattern = re.compile(r'"([123])"\^\^<http://www.w3.org/2001/XMLSchema#integer>')
    scores = [t[2] for t in case["inputTriples"] if t[1].endswith("comparison-test:score")]
    assert len(scores) == 1
    left = pattern.fullmatch(scores[0])
    right = pattern.fullmatch(case["rules"][0]["conditions"][-1]["right"])
    assert left is not None and right is not None
    return int(left[1]), int(right[1])


def test_comparison_cells_distinguish_all_six_operators_without_running_rules():
    cases = [case for case in FIXTURE["cases"] if case["category"] == "integer-comparison"]
    signatures = {}
    for op in ("eq", "ne", "lt", "le", "gt", "ge"):
        values = [case for case in cases if case["operator"] == op]
        assert sorted(integer_operands(case) for case in values) == [(1, 2), (2, 2), (3, 2)]
        signatures[op] = tuple(
            case["expectedCondition"] for case in sorted(values, key=integer_operands)
        )
    assert signatures == {
        "eq": (False, True, False),
        "ne": (True, False, True),
        "lt": (True, False, False),
        "le": (True, True, False),
        "gt": (False, False, True),
        "ge": (False, True, True),
    }
    assert len(set(signatures.values())) == 6
    # Every replacement by a different operator has at least one distinguishing
    # input cell. This is input coverage, not an execution test of a product operator.
    for name, signature in signatures.items():
        for other, other_signature in signatures.items():
            if name != other:
                assert any(a != b for a, b in zip(signature, other_signature, strict=True))


@pytest.mark.parametrize(
    "case",
    [c for c in FIXTURE["cases"] if c["category"] == "integer-comparison"],
    ids=lambda case: case["id"],
)
def test_scalar_expectation_math_is_correct_not_engine_execution(case):
    # Reference arithmetic only checks the fixture oracle; it does not bind graph
    # variables, evaluate rules, construct actual outputs, or certify a runtime.
    reference = {
        "eq": operator.eq,
        "ne": operator.ne,
        "lt": operator.lt,
        "le": operator.le,
        "gt": operator.gt,
        "ge": operator.ge,
    }
    left, right = integer_operands(case)
    assert reference[case["operator"]](left, right) is case["expectedCondition"]


def test_join_counterexample_keeps_both_alarms_bound_to_one_rule_variable():
    case = next(case for case in FIXTURE["cases"] if case["id"] == "JOIN-NO-CROSS-ALARM")
    properties = [c for c in case["rules"][0]["conditions"] if c["kind"] == "property"]
    assert properties == [
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
    assert case["expectedRuleOutputs"] == []


def test_multiconclusion_definition_is_one_rule_not_separate_rules():
    case = next(case for case in FIXTURE["cases"] if case["id"] == "MULTI-OUTPUT-ONE-FIRING")
    assert [rule["id"] for rule in case["rules"]] == ["R-risk-multi"]
    assert case["rules"][0]["conclusions"] == [
        {
            "kind": "type",
            "subject": "?equipment",
            "class": "urn:ontolearn:learning:HighRiskEquipment",
        },
        {
            "kind": "property",
            "subject": "?equipment",
            "path": "urn:ontolearn:quality:comparison-test:derivedLabel",
            "object": '"needs-review"',
        },
    ]


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["id"])
def test_expected_evidence_references_inputs_and_enabled_rule_without_claiming_actual(case):
    input_set = {tuple(statement) for statement in case["inputTriples"]}
    enabled = {rule["id"] for rule in case["rules"] if rule["enabled"]}
    outputs = set()
    for firing in case["expectedFirings"]:
        assert firing["ruleId"] in enabled
        assert firing["inputStatements"]
        for statement in firing["inputStatements"]:
            assert tuple(statement) in input_set
        outputs.update(tuple(statement) for statement in firing["outputStatements"])
    assert outputs == {tuple(statement) for statement in case["expectedRuleOutputs"]}
    # All this proves is internally consistent acceptance input, never inference truth.


def test_shared_ontology_is_explicit_and_matches_controlled_catalog():
    rdf_type = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    owl = "http://www.w3.org/2002/07/owl#"
    classes, properties = set(), set()
    for statement in FIXTURE["ontologyTriples"]:
        validate_statement(statement)
        subject, predicate, value = statement
        if predicate == rdf_type and value == f"<{owl}Class>":
            classes.add(subject)
        elif predicate == rdf_type and value in (
            f"<{owl}ObjectProperty>",
            f"<{owl}DatatypeProperty>",
        ):
            properties.add(subject)
    assert classes == set(FIXTURE["catalog"]["classes"])
    assert properties == set(FIXTURE["catalog"]["properties"])
