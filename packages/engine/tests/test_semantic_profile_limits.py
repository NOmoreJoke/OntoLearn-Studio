"""Fail atomically before unbounded expansion; keep the entire definition gate."""

from dataclasses import replace

import pytest
from ontolearn_engine.quality.rule_firing import Comparison, Variable
from ontolearn_engine.quality.rule_profile import XSD, TermInput
from ontolearn_engine.semantic import ProfileReasonError
from ontolearn_engine.semantic_turtle import bind_profile_disabled_rules
from test_semantic_profile_integration import compute, fixed_case


def test_whole_definition_count_and_duplicate_ids_before_split():
    _, graph, context, rules = fixed_case()
    with pytest.raises(ProfileReasonError, match="INVALID_RULE"):
        compute(graph, context, tuple(replace(rules[0], rule_id=str(n)) for n in range(101)))
    with pytest.raises(ProfileReasonError, match="INVALID_RULE"):
        compute(graph, context, (rules[0], rules[0]))


def test_disabled_bad_constant_is_precompiled_even_without_matching():
    _, graph, context, rules = fixed_case()
    bad = replace(
        rules[0],
        comparisons=(
            Comparison(
                TermInput("literal", "bad", XSD + "integer"),
                "eq",
                TermInput("literal", "0", XSD + "integer"),
            ),
        ),
    )
    context = bind_profile_disabled_rules(context, (bad.rule_id,))
    with pytest.raises(ProfileReasonError) as caught:
        compute(graph, context, (bad,))
    assert caught.value.code == "INVALID_LITERAL_LEXICAL"
    assert caught.value.rule_id == bad.rule_id


def test_later_bad_rule_fails_complete_call():
    _, graph, context, rules = fixed_case()
    bad = replace(rules[0], rule_id="zz", heads=())
    with pytest.raises(ProfileReasonError):
        compute(graph, context, (rules[0], bad))


def test_false_comparison_does_not_hide_later_bad_operand():
    _, graph, context, rules = fixed_case()
    false = Comparison(
        TermInput("literal", "1", XSD + "integer"), "eq", TermInput("literal", "2", XSD + "integer")
    )
    mismatch = Comparison(Variable("?v"), "eq", TermInput("literal", "true", XSD + "boolean"))
    with pytest.raises(ProfileReasonError) as caught:
        compute(graph, context, (replace(rules[0], comparisons=(false, mismatch)),))
    assert caught.value.code == "RULE_COMPARISON_TYPE_MISMATCH"


def test_projection_boundary_is_precharged_and_has_no_partial_return(monkeypatch):
    from ontolearn_engine import semantic_execution
    from ontolearn_engine.semantic_offline import SemanticError

    monkeypatch.setattr(semantic_execution, "MAX_OUTPUT_BYTES", 8)
    with pytest.raises(SemanticError, match="PROJECTION_RESULT_LIMIT"):
        semantic_execution._ProfileProjection().value("123456789")
    assert semantic_execution._profile_json_bytes("123456") == b'"123456"'
    with pytest.raises(SemanticError, match="PROJECTION_RESULT_LIMIT"):
        semantic_execution._profile_json_bytes("1234567")


def test_actual_graph_work_boundary_plus_minus_one(monkeypatch):
    from ontolearn_engine import semantic

    _, graph, context, rules = fixed_case()
    required = compute(graph, context, rules)["graphBudget"]["usage"]["work"]
    monkeypatch.setattr(semantic, "MAX_WORK", required)
    assert compute(graph, context, rules)["graphBudget"]["usage"]["work"] == required
    monkeypatch.setattr(semantic, "MAX_WORK", required - 1)
    with pytest.raises(ProfileReasonError, match="WORK_LIMIT"):
        compute(graph, context, rules)
