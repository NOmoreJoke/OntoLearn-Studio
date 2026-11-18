"""Lexical/source/term identity witnesses for the adopted private profile."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from ontolearn_engine.quality.rule_profile import (
    RDF,
    XSD,
    Budget,
    InputLocation,
    ProfileFailure,
    SourceRecord,
    TermInput,
)
from ontolearn_engine.quality.rule_terms import GRANDFATHERED, parse_value, term_key

FIXTURES = Path(__file__).resolve().parents[3] / "tests/fixtures/quality/profile-v1"


def fixture(name):
    return json.loads((FIXTURES / name).read_text())


def term(kind, text, language=None):
    return TermInput("literal", text, (RDF if kind == "langString" else XSD) + kind, language)


def value(kind, text, language=None, budget=None):
    return parse_value(term(kind, text, language), None, budget or Budget())


@pytest.mark.parametrize("case", fixture("lexical.json")["valid"])
def test_lexical_positive(case):
    v = value(case["type"], case["lexical"], case.get("language"))
    assert v.term.lexical_form == case["lexical"]


@pytest.mark.parametrize("case", fixture("lexical.json")["invalid"])
def test_lexical_negative(case):
    loc = InputLocation("comparison", 7, "right")
    with pytest.raises(ProfileFailure) as caught:
        parse_value(term(case["type"], case["lexical"]), loc, Budget())
    assert (caught.value.reason, caught.value.location) == (case["reason"], loc)
    assert str(caught.value) == case["reason"]
    assert case["lexical"] not in caught.value.args or case["lexical"] == ""


@pytest.mark.parametrize(
    "label", fixture("lexical.json")["valid_languages"] + sorted(GRANDFATHERED)
)
def test_all_language_branches(label):
    assert value("langString", "\0\ufffe", label).language == label.lower()


@pytest.mark.parametrize("label", fixture("lexical.json")["invalid_languages"])
def test_bad_languages(label):
    with pytest.raises(ProfileFailure, match="INVALID_LITERAL_LEXICAL"):
        value("langString", "hello", label)


def test_source_spelling_and_abstract_term_are_separate():
    budget = Budget()
    source = SourceRecord("example", "given-digest", "r7", '"a"@EN')
    raw = TermInput("literal", "a", None, "EN", source)
    parsed = parse_value(raw, None, budget)
    assert parsed.term is raw and parsed.term.source is source
    assert term_key(parsed, budget) == term_key(value("langString", "a", "en"), budget)
    simple = parse_value(TermInput("literal", "a"), None, budget)
    assert term_key(simple, budget) == term_key(value("string", "a"), budget)
    assert term_key(value("integer", "01"), budget) != term_key(value("integer", "1"), budget)
    with pytest.raises(FrozenInstanceError):
        raw.lexical_form = "changed"


@pytest.mark.parametrize(
    "bad",
    [
        TermInput("literal", "a", ""),
        TermInput("literal", "a", RDF + "langString"),
        TermInput("literal", "a", XSD + "string", "en"),
        TermInput("literal", "\ud800"),
        TermInput("blank", "x"),
        TermInput("iri", "relative"),
        TermInput("iri", "urn:has space"),
    ],
)
def test_structural_inputs_never_become_values(bad):
    with pytest.raises(ProfileFailure, match="INVALID_RULE"):
        parse_value(bad, None, Budget())


def test_unsupported_datatype_and_missing_locations_are_explicit():
    with pytest.raises(ProfileFailure) as caught:
        parse_value(TermInput("literal", "x", "urn:unknown"), None, Budget())
    assert caught.value.reason == "UNSUPPORTED_LITERAL_DATATYPE"
    assert caught.value.location is None
    with pytest.raises(AttributeError):
        caught.value.reason = "other"


@pytest.mark.parametrize("field", ["section", "side"])
def test_location_exact_type_gate_never_calls_equality_hook(field):
    calls = []

    class Probe:
        def __eq__(self, other):
            calls.append("eq")
            return False

    loc = InputLocation(**{field: Probe()})
    with pytest.raises(ProfileFailure, match="INVALID_RULE"):
        parse_value(term("integer", "1"), loc, Budget())
    assert calls == []


def test_unissued_and_corrupt_value_cannot_execute_boolean_hooks():
    from ontolearn_engine.quality.rule_comparator import compare_values
    from ontolearn_engine.quality.rule_terms import ProfileValue

    calls = []

    class Probe:
        def __gt__(self, other):
            calls.append("gt")
            return True

        def __lt__(self, other):
            calls.append("lt")
            return False

    bad = ProfileValue(term("boolean", "true"), "B", Probe())
    good = value("boolean", "true")
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        compare_values(bad, "eq", good, Budget())
    object.__setattr__(good, "value", Probe())
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        compare_values(good, "eq", good, Budget())
    assert calls == []


def test_typed_fingerprints_separate_integer_string_and_record_tuple():
    from ontolearn_engine.quality.rule_profile import encode_input

    b = Budget()
    assert encode_input(1, b) != encode_input("0x1", b)
    assert encode_input((1,), b) != encode_input([1], b)
    source = SourceRecord()
    as_tuple = ("SourceRecord", "reference", None, "digest", None, "revision", None, "text", None)
    assert encode_input(source, b) != encode_input(as_tuple, b)


@pytest.mark.parametrize("case", ["operator", "location", "module-name"])
def test_remaining_direct_entry_hook_cases_are_inert(case):
    from ontolearn_engine.quality.rule_comparator import compare_values
    from ontolearn_engine.quality.rule_profile import account_input

    calls = []

    class Probe:
        def __eq__(self, other):
            calls.append("eq")
            return False

        def __hash__(self):
            calls.append("hash")
            return 0

    good = value("string", "x")
    with pytest.raises(ProfileFailure) as caught:
        if case == "operator":
            compare_values(good, Probe(), good, Budget())
        elif case == "location":
            compare_values(good, "invalid", good, Budget(), InputLocation(section=Probe()))
        else:

            class Foreign:
                pass

            Foreign.__module__ = Probe()
            account_input(Foreign(), Budget())
    assert caught.value.reason in ("INTERNAL_ERROR", "INVALID_RULE")
    assert caught.value.location is None
    assert calls == []
