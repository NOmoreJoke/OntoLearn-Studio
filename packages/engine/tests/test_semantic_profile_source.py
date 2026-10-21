"""Actual lexical/source sidecar and strict non-network RDF IRI boundary."""

import hashlib
import json
from dataclasses import replace

import pytest
from ontolearn_engine.quality.rule_firing import Comparison, Variable
from ontolearn_engine.quality.rule_profile import XSD, SourceRecord
from ontolearn_engine.semantic_offline import SemanticError
from ontolearn_engine.semantic_turtle import parse_profile_graph, validate_profile_iri
from test_semantic_profile_integration import FIXTURES, compute, fixed_case


def test_original_numeric_and_language_occurrences_are_retained():
    text = '<urn:s> <urn:p> 0002, +2 ; <urn:q> "x"@EN-us, "x"@en-US .'
    source = SourceRecord(
        "fixture:actual-text", hashlib.sha256(text.encode()).hexdigest(), "1", text
    )
    graph, context = parse_profile_graph(text, base_uri="urn:test:", source=source)
    occurrences = context.occurrences
    assert {item.value.lexical_form for item in occurrences} >= {"0002", "+2", "x"}
    languages = {
        item.value.language_raw for item in occurrences if item.value.language_raw is not None
    }
    assert languages == {"EN-us", "en-US"}
    assert all(item.span is None for item in occurrences)
    assert all(item.value.source == source for item in occurrences)
    context.validate_graph(graph)


@pytest.mark.parametrize(
    "text",
    [
        "https://example.test/ns#Class",
        "urn:a:b",
        "https://例子.测试/路径?q=值#片段",
        "file:/local#fragment",
        "https://a/ ",
    ],
)
def test_valid_absolute_iri_keeps_full_identity(text):
    assert validate_profile_iri(text) == text


@pytest.mark.parametrize(
    "text",
    [
        "relative/path",
        "https://a/%G0",
        "https://a/%",
        "https://a/a b",
        "http://[bad]/",
        "urn:\\bad",
        "urn:a\u0000",
        "https://a/#a#b",
    ],
)
def test_invalid_iri_is_rejected_without_network(text):
    with pytest.raises(SemanticError):
        validate_profile_iri(text)


@pytest.mark.parametrize(
    "case", json.loads((FIXTURES / "calendar-oracles.json").read_bytes())["cases"]
)
def test_profile_calendar_original_lexical_reaches_true_graph_match(case):
    _, _, _, rules = fixed_case()
    text = (
        "<urn:value> a <http://www.w3.org/2002/07/owl#DatatypeProperty> . "
        '<urn:out> a <http://www.w3.org/2002/07/owl#DatatypeProperty> . <urn:a> <urn:value> "'
        + case["lexical"]
        + '"^^<'
        + XSD
        + case["type"]
        + "> ."
    )
    graph, context = parse_profile_graph(text, base_uri="urn:test:")
    spec = replace(rules[0], comparisons=(Comparison(Variable("?v"), "eq", Variable("?v")),))
    (firing,) = compute(graph, context, (spec,))["firingGroups"]
    value = firing.comparisons[0].left.value
    assert value.day == case["day"]
    assert [value.second.numerator, value.second.denominator] == case["second"]
    assert firing.when[0].object.lexical_form == case["lexical"]


def test_issued_context_rejects_mutated_graph():
    from rdflib import URIRef

    _, graph, context, rules = fixed_case()
    graph.add((URIRef("urn:forged"), URIRef("urn:value"), URIRef("urn:value")))
    with pytest.raises(SemanticError):
        compute(graph, context, rules)


@pytest.mark.parametrize(
    "case", json.loads((FIXTURES / "numeric-oracles.json").read_bytes())["valid"]
)
def test_fixed_ieee_oracle_through_actual_graph(case):
    import math
    import struct

    from ontolearn_engine.quality.rule_profile import TermInput
    from test_semantic_profile_integration import _comparison_graph

    term = TermInput("literal", case["lexical"], XSD + case["type"])
    graph, context, rules = _comparison_graph(term, term, "eq")
    (group,) = compute(graph, context, rules)["firingGroups"]
    actual = group.comparisons[0].left.value
    # Decode the fixed independently authored IEEE bits; no tested comparator,
    # rounding routine or actual output supplies an expected result.
    if "ieee" in case:
        (expected,) = struct.unpack(
            ">f" if case["type"] == "float" else ">d", bytes.fromhex(case["ieee"])
        )
        assert (actual.numerator, actual.denominator) == expected.as_integer_ratio()
        assert actual.negative_zero is (expected == 0 and math.copysign(1, expected) < 0)
    else:
        assert (actual.numerator, actual.denominator) == (
            int(case["numerator"]),
            int(case["denominator"]),
        )


@pytest.mark.parametrize("target", ["lexical", "source"])
def test_nested_context_value_mutation_cannot_rewrite_real_graph(target):
    from ontolearn_engine.semantic import ProfileReasonError

    _, graph, context, rules = fixed_case()
    term = next(
        item.value
        for item in context.occurrences
        if item.value.kind == "literal" and item.value.lexical_form == "2"
    )
    if target == "lexical":
        object.__setattr__(term, "lexical_form", "9")
    else:
        object.__setattr__(term.source, "digest", "changed")
    with pytest.raises(ProfileReasonError) as caught:
        compute(graph, context, rules)
    assert caught.value.code == "PROFILE_CONTEXT_INVALID"
    assert caught.value.classification == "internal"
    assert caught.value.rule_id is None


def test_legal_nbsp_iri_reaches_actual_entry_validation_join_and_head():
    from ontolearn_engine.semantic_profile_probe import _construct_case

    fixture = json.loads((FIXTURES / "firing-cases.json").read_bytes())
    text, rules = _construct_case(fixture)
    text = text.replace("urn:a", "urn:a\u00a0")
    graph, context = parse_profile_graph(text, base_uri="urn:test:")
    result = compute(graph, context, rules)
    assert result["firingGroups"]
    assert any("\u00a0" in term for record in result["proofLeaves"] for term in record["triple"])
    assert result["graphBudget"]["entryUsage"]["input_bytes"] > 0
