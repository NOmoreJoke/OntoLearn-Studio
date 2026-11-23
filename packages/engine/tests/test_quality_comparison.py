"""Presentation-algorithm observations are fixtures, never engine execution evidence."""

import copy

import pytest
from ontolearn_engine.quality import DefinitionError
from ontolearn_engine.quality.comparison import (
    compare_derivations,
    compare_statements,
    validate_trace,
)

TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RISK = ["urn:equipment:001", TYPE, "<urn:HighRiskEquipment>"]


def trace(alarm="A01"):
    return [
        {
            "id": "equipment",
            "kind": "asserted",
            "statement": ["urn:equipment:001", TYPE, "<urn:Equipment>"],
            "inputs": [],
            "ruleId": None,
        },
        {
            "id": "alarm",
            "kind": "asserted",
            "statement": [f"urn:alarm:{alarm}", "urn:status", '"Open"'],
            "inputs": [],
            "ruleId": None,
        },
        {
            "id": "risk",
            "kind": "rule",
            "statement": RISK,
            "inputs": ["equipment", "alarm"],
            "ruleId": "R-risk",
        },
    ]


def test_equal_counts_do_not_hide_missing_and_unexpected_rows():
    actual = [["urn:equipment:002", TYPE, "<urn:HighRiskEquipment>"]]
    assert compare_statements([RISK], actual) == {
        "missing": [tuple(RISK)],
        "unexpected": [tuple(actual[0])],
        "matched": [],
    }


def test_diff_withdraws_only_derived_statement_and_shows_changed_supports():
    assert compare_derivations(trace(), []) == {
        "added": [],
        "withdrawn": [tuple(RISK)],
        "changed": [],
        "unchanged": [],
    }
    assert compare_derivations(trace(), trace("A04")) == {
        "added": [],
        "withdrawn": [],
        "changed": [tuple(RISK)],
        "unchanged": [],
    }
    # This tests supplied evidence comparison, not the G R-02/R-03 executor.


def test_support_order_and_trace_id_renaming_are_not_semantic_changes():
    current = trace()
    for node in current:
        node["id"] = "new-" + node["id"]
        node["inputs"] = ["new-" + item for item in reversed(node["inputs"])]
    assert compare_derivations(trace(), current)["unchanged"] == [tuple(RISK)]


def test_multiple_supports_survive_and_one_withdrawn_support_is_visible():
    current = trace()
    second_alarm = copy.deepcopy(current[1])
    second_alarm.update(id="alarm2", statement=["urn:alarm:A04", "urn:status", '"Open"'])
    second_risk = copy.deepcopy(current[2])
    second_risk.update(id="risk2", inputs=["equipment", "alarm2"])
    current.extend([second_alarm, second_risk])
    assert compare_derivations(trace(), current)["changed"] == [tuple(RISK)]
    assert compare_derivations(current, trace("A04"))["withdrawn"] == []
    assert compare_derivations(current, trace("A04"))["changed"] == [tuple(RISK)]


@pytest.mark.parametrize(
    "case,code",
    [
        ("missing", "MISSING_TRACE_NODE"),
        ("cycle", "CYCLIC_TRACE"),
        ("duplicate", "DUPLICATE_TRACE_NODE"),
        ("leaf", "INVALID_TRACE_LEAF"),
        ("no-input", "MISSING_TRACE_INPUT"),
        ("rule-id", "INVALID_TEXT"),
    ],
)
def test_broken_trace_is_not_treated_as_valid_explanation(case, code):
    nodes = trace()
    if case == "missing":
        nodes[-1]["inputs"].append("unknown")
    elif case == "cycle":
        nodes[-1]["inputs"].append("risk")
    elif case == "duplicate":
        nodes.append(copy.deepcopy(nodes[-1]))
    elif case == "leaf":
        nodes[0]["inputs"] = ["alarm"]
    elif case == "no-input":
        nodes[-1]["inputs"] = []
    elif case == "rule-id":
        nodes[-1]["ruleId"] = None
    with pytest.raises(DefinitionError, match=code):
        validate_trace(nodes)


def test_validated_trace_copies_input():
    nodes = trace()
    result = validate_trace(nodes)
    result["risk"]["inputs"].clear()
    assert nodes[-1]["inputs"] == ["equipment", "alarm"]
