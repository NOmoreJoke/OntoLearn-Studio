"""Occurrence, prefix, preallocation, serialization and one-call limit probes."""

from dataclasses import FrozenInstanceError, fields, replace

import pytest
from ontolearn_engine.quality.rule_comparator import compare_values
from ontolearn_engine.quality.rule_firing import compile_rules, evaluate_bound_batch
from ontolearn_engine.quality.rule_numbers import mul, power10, shift
from ontolearn_engine.quality.rule_profile import (
    Budget,
    ProfileFailure,
    ProfileLimits,
    SourceRecord,
    TermInput,
    account_input,
    encode_output,
    text_compare,
)
from ontolearn_engine.quality.rule_terms import parse_value
from test_quality_profile_firing import example
from test_quality_profile_terms import term


@pytest.mark.parametrize("f", fields(ProfileLimits()))
def test_limits_frozen_and_never_raised(f):
    with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
        ProfileLimits(**{f.name: f.default + 1})
    with pytest.raises(FrozenInstanceError):
        setattr(ProfileLimits(), f.name, 0)
    if f.name in (
        "work",
        "input_bytes",
        "output_bytes",
        "trace_items",
        "firings",
        "head_occurrences",
    ):
        b = Budget(ProfileLimits(**{f.name: 2}))
        b.debit(1, f.name)
        b.debit(1, f.name)
        with pytest.raises(ProfileFailure):
            b.debit(1, f.name)
    else:
        b = Budget(ProfileLimits(**{f.name: 2}))
        b.bound(1, f.name)
        b.bound(2, f.name)
        with pytest.raises(ProfileFailure):
            b.bound(3, f.name)


def test_aliases_are_charged_per_occurrence():
    item = term("string", "same object")
    a, b = Budget(), Budget()
    account_input((item,), a)
    account_input((item, item), b)
    assert dict(b.usage)["input_bytes"] > dict(a.usage)["input_bytes"] * 1.9
    assert dict(b.usage)["work"] > dict(a.usage)["work"]


def test_prefix_comparison_and_term_key_work_are_not_constant():
    with pytest.raises(ProfileFailure, match="WORK_LIMIT"):
        text_compare("a" * 1000 + "b", "a" * 1000 + "c", Budget(ProfileLimits(work=100)))
    left = parse_value(term("string", "a" * 500), None, Budget())
    right = parse_value(term("string", "a" * 499 + "b"), None, Budget())
    with pytest.raises(ProfileFailure, match="WORK_LIMIT"):
        compare_values(left, "lt", right, Budget(ProfileLimits(work=100)))


def test_arithmetic_fails_before_expensive_allocation():
    b = Budget(ProfileLimits(temporary_bits=64))
    for operation in [
        lambda: mul(1 << 63, 1 << 63, b),
        lambda: shift(1, 10000000, b),
        lambda: power10(10000000, b),
    ]:
        before = b.usage
        with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
            operation()
        assert b.usage == before


def test_source_term_digit_boundaries_and_no_global_lift():
    for caps, source in [
        (ProfileLimits(term_bytes=3), TermInput("literal", "abcd")),
        (
            ProfileLimits(source_bytes=3),
            TermInput("literal", "a", source=SourceRecord(text="abcd")),
        ),
        (ProfileLimits(digits=3), term("integer", "1234")),
    ]:
        with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
            parse_value(source, None, Budget(caps))
    assert (
        parse_value(TermInput("literal", "abc"), None, Budget(ProfileLimits(term_bytes=3))).value
        == "abc"
    )


def test_streaming_serialization_does_not_build_then_measure(monkeypatch):
    import json

    monkeypatch.setattr(json, "dumps", lambda *a, **k: pytest.fail("whole json allocation"))
    with pytest.raises(ProfileFailure, match="RULE_EVIDENCE_RESULT_LIMIT"):
        encode_output(("a" * 10000,), Budget(ProfileLimits(output_bytes=10)))
    payload = encode_output(("abc",), Budget())
    assert encode_output(("abc",), Budget(ProfileLimits(output_bytes=len(payload)))) == payload
    with pytest.raises(ProfileFailure):
        encode_output(("abc",), Budget(ProfileLimits(output_bytes=len(payload) - 1)))


def test_trace_units_include_all_occurrences_and_references():
    r, c, m = example()
    b = Budget(ProfileLimits(trace_items=22))
    p = compile_rules((r,), c, b)
    result = evaluate_bound_batch(p, (m,), b)
    assert result.firings and dict(b.usage)["trace_items"] == 22
    b = Budget(ProfileLimits(trace_items=21))
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure, match="RULE_EVIDENCE_RESULT_LIMIT"):
        evaluate_bound_batch(p, (m,), b)
    b = Budget(ProfileLimits(trace_items=20))
    p = compile_rules((r,), c, b)
    aliases = replace(m, proof_leaves=(("same-leaf",) * 21,))
    with pytest.raises(ProfileFailure, match="RULE_EVIDENCE_RESULT_LIMIT"):
        evaluate_bound_batch(p, (aliases,), b)


def test_output_limit_and_one_call_budget_cannot_publish_partial_or_reset():
    r, c, m = example()
    b = Budget(ProfileLimits(output_bytes=1))
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure, match="RULE_EVIDENCE_RESULT_LIMIT"):
        evaluate_bound_batch(p, (m,), b)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        evaluate_bound_batch(p, (m,), b)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        b.debit(-1)
    with pytest.raises(AttributeError):
        b.limits = ProfileLimits()


@pytest.mark.parametrize("name", ["rules", "when", "comparisons", "heads", "variables"])
def test_actual_compile_structural_caps(name):
    from ontolearn_engine.quality.rule_firing import Comparison, Variable

    r, c, _ = example()
    if name == "rules":
        definitions = (r, replace(r, rule_id="r2"))
    else:
        if name == "when":
            r = replace(r, when=r.when * 2)
        elif name == "comparisons":
            r = replace(
                r, comparisons=(Comparison(Variable("?v"), "gt", term("integer", "1")),) * 2
            )
        elif name == "heads":
            pass
        definitions = (r,)
    with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
        compile_rules(definitions, c, Budget(ProfileLimits(**{name: 1})))
    assert compile_rules(definitions, c, Budget(ProfileLimits(**{name: 2}))).rules


def test_actual_batch_binding_firing_and_head_caps():
    from ontolearn_engine.quality.rule_firing import Triple
    from test_quality_profile_firing import iri

    r, c, m = example()
    other = replace(
        m,
        bindings=(("?s", iri("urn:b")), ("?v", term("integer", "2"))),
        when=(Triple(iri("urn:b"), iri("urn:value"), term("integer", "2")),),
    )
    for name, cap in [("bindings", 1), ("firings", 1), ("head_occurrences", 3)]:
        b = Budget(ProfileLimits(**{name: cap}))
        p = compile_rules((r,), c, b)
        with pytest.raises(ProfileFailure):
            evaluate_bound_batch(p, (m, other), b)
        b = Budget(ProfileLimits(**{name: cap + 1}))
        p = compile_rules((r,), c, b)
        assert len(evaluate_bound_batch(p, (m, other), b).firings) == 2


def test_late_final_output_failure_returns_no_batch():
    r, c, m = example()
    b = Budget()
    p = compile_rules((r,), c, b)
    result = evaluate_bound_batch(p, (m,), b)
    size = len(result.payload)
    b = Budget(ProfileLimits(output_bytes=size))
    p = compile_rules((r,), c, b)
    assert evaluate_bound_batch(p, (m,), b).payload == result.payload
    b = Budget(ProfileLimits(output_bytes=size - 1))
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure, match="RULE_EVIDENCE_RESULT_LIMIT"):
        evaluate_bound_batch(p, (m,), b)
    assert dict(b.usage)["output_bytes"] <= size - 1


def test_catalog_total_input_precedes_iri_scan_and_sort(monkeypatch):
    from ontolearn_engine.quality import rule_firing
    from ontolearn_engine.quality.rule_firing import Catalog

    def forbidden(*a, **k):
        pytest.fail("catalog scan before total-input gate")

    monkeypatch.setattr(rule_firing, "iri_minimum", forbidden)
    cat = Catalog(classes=("urn:same",) * 1000)
    with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
        compile_rules((), cat, Budget(ProfileLimits(input_bytes=128)))


def test_direct_helpers_reject_foreign_primitives_and_budget_without_hooks():
    from ontolearn_engine.quality.rule_calendar import parse_calendar
    from ontolearn_engine.quality.rule_numbers import parse_number, rational
    from ontolearn_engine.quality.rule_profile import encode_input, fingerprint, tuple_compare

    calls = []

    class Probe:
        def __getattr__(self, name):
            calls.append(name)
            return lambda *a, **k: 1

        def __eq__(self, other):
            calls.append("eq")
            return False

        def __lt__(self, other):
            calls.append("lt")
            return False

        def __gt__(self, other):
            calls.append("gt")
            return False

    probe = Probe()
    b = Budget()
    operations = [
        lambda: mul(probe, 1, b),
        lambda: rational(1, probe, b),
        lambda: shift(probe, 1, b),
        lambda: power10(probe, b),
        lambda: parse_number(probe, "x", b),
        lambda: parse_calendar(probe, "x", b),
        lambda: text_compare(probe, "a", b),
        lambda: tuple_compare((probe,), (probe,), b),
        lambda: parse_value(term("integer", "1"), None, probe),
        lambda: encode_input("x", probe),
        lambda: fingerprint(probe),
        lambda: b.debit(1, probe),
        lambda: b.bound(1, probe),
    ]
    for operation in operations:
        with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
            operation()
    assert calls == []


@pytest.mark.parametrize("bits", [95, 96, 97])
def test_integer_tuple_comparison_has_real_bit_and_limb_gates(bits):
    from ontolearn_engine.quality.rule_profile import tuple_compare

    a = (1 << (bits - 1)) + 1
    right = a + 1
    b = Budget(ProfileLimits(temporary_bits=96))
    if bits > 96:
        with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
            tuple_compare((a,), (right,), b)
        assert dict(b.usage)["work"] == 0
    else:
        assert tuple_compare((a,), (right,), b) == -1
        assert dict(b.usage)["work"] == 2 * ((bits + 31) // 32)
        with pytest.raises(ProfileFailure, match="WORK_LIMIT"):
            tuple_compare((a,), (right,), Budget(ProfileLimits(work=2 * ((bits + 31) // 32) - 1)))


def test_fingerprint_requires_budget_and_checks_before_hash(monkeypatch):
    from ontolearn_engine.quality import rule_profile

    calls = []
    actual = rule_profile.sha256

    def watched(data):
        calls.append(len(data))
        return actual(data)

    monkeypatch.setattr(rule_profile, "sha256", watched)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        rule_profile.fingerprint(b"x")
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        rule_profile.fingerprint(b"x", object())
    with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
        rule_profile.fingerprint(b"xxxx", Budget(ProfileLimits(input_bytes=3)))
    with pytest.raises(ProfileFailure, match="WORK_LIMIT"):
        rule_profile.fingerprint(b"xxxx", Budget(ProfileLimits(work=3)))
    assert calls == []
    b = Budget(ProfileLimits(input_bytes=4, work=4))
    assert rule_profile.fingerprint(b"xxxx", b) == actual(b"xxxx").hexdigest()
    assert calls == [4] and dict(b.usage)["work"] == 4
    assert dict(b.usage)["input_bytes"] == 0  # encoded bytes already accounted by caller


def test_location_integer_fields_use_same_metered_input_gate():
    from ontolearn_engine.quality.rule_profile import InputLocation

    loc = InputLocation("comparison", 1 << 96)
    with pytest.raises(ProfileFailure, match="RULE_INPUT_BUDGET"):
        parse_value(term("integer", "1"), loc, Budget(ProfileLimits(integer_bits=96)))


def test_empty_fingerprint_has_fixed_minimum_work_before_hash(monkeypatch):
    from ontolearn_engine.quality import rule_profile

    calls = []
    actual = rule_profile.sha256

    def watched(data):
        calls.append(data)
        return actual(data)

    monkeypatch.setattr(rule_profile, "sha256", watched)
    with pytest.raises(ProfileFailure, match="WORK_LIMIT"):
        rule_profile.fingerprint(b"", Budget(ProfileLimits(work=0)))
    assert calls == []
    b = Budget(ProfileLimits(work=1))
    assert rule_profile.fingerprint(b"", b) == actual(b"").hexdigest()
    assert calls == [b""] and dict(b.usage)["work"] == 1
    with pytest.raises(ProfileFailure, match="WORK_LIMIT"):
        rule_profile.fingerprint(b"", b)
    assert calls == [b""]
