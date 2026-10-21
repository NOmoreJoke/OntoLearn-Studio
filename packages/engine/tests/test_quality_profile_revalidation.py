"""Real canonical API tests; outer allocator and restore are not implemented."""

import importlib.util
import json
import pickle
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest
from ontolearn_engine.quality import rule_revalidation as revalidation
from ontolearn_engine.quality.rule_firing import (
    BindingMatch,
    Catalog,
    Comparison,
    RuleSpec,
    Triple,
    Variable,
    check_firing_group,
    compile_rules,
    evaluate_bound_batch,
)
from ontolearn_engine.quality.rule_profile import (
    PROFILE,
    XSD,
    Budget,
    ProfileFailure,
    ProfileLimits,
    SourceRecord,
    TermInput,
    encode_output,
    fingerprint,
)
from ontolearn_engine.quality.rule_terms import ProfileValue, parse_value

FIXTURE = (
    Path(__file__).resolve().parents[3]
    / "tests/fixtures/quality/profile-revalidation-v1/cases.json"
)
CASES = json.loads(FIXTURE.read_text())


def iri(text):
    return TermInput("iri", text)


def literal(text, datatype=None, source=None):
    return TermInput("literal", text, datatype, source=source)


def program(*, long_source=False, comparison=False):
    case = CASES["longSource"]
    source = SourceRecord(text="a" * 40000) if long_source else None
    obj = Variable("?v") if comparison else literal(case["whenObject"])
    spec = RuleSpec(
        "r",
        (Triple(Variable("?x"), iri("urn:p"), obj),),
        (Comparison(Variable("?v"), "eq", literal("2", XSD + "integer")),) if comparison else (),
        (Triple(Variable("?x"), iri("urn:q"), literal("ok")),),
        source,
    )
    matches = []
    values = CASES["orderedMatches"]["values"] if comparison else ["v", "v"]
    for index, value in enumerate(values, 1):
        subject = iri(f"urn:s{index}")
        term = literal(value, XSD + "integer") if comparison else literal(value)
        pairs = (("?x", subject), ("?v", term)) if comparison else (("?x", subject),)
        matches.append(
            BindingMatch("r", pairs, (Triple(subject, iri("urn:p"), term),), ((f"f{index}",),))
        )
    return (spec,), Catalog(data_properties=("urn:p", "urn:q")), tuple(matches)


def produce(definitions, catalog, matches, limits=None):
    budget = Budget(limits)
    batch = evaluate_bound_batch(compile_rules(definitions, catalog, budget), matches, budget)
    return batch, budget


def recheck(inputs, batch, limits=None, disabled=False):
    return revalidation.check_firing_batch(
        *inputs, batch, limits=limits or ProfileLimits(), disabled=disabled
    )


def capture_pools(monkeypatch):
    original = revalidation._Resources
    seen = []

    def observing(limits, control):
        pools = original(limits, control)
        seen.append(pools)
        return pools

    monkeypatch.setattr(revalidation, "_Resources", observing)
    return seen


def test_long_source_old_success_old_group_failure_new_success(monkeypatch):
    inputs = program(long_source=True)
    batch, production = produce(*inputs)
    assert batch.facts == tuple(
        Triple(iri(s), iri(p), literal(o)) for s, p, o in CASES["longSource"]["expectedFacts"]
    )
    assert tuple(f.source.text for f in batch.firings) == ("a" * 40000,) * 2
    old_budget = Budget()
    old_plan = compile_rules(inputs[0], inputs[1], old_budget)
    with pytest.raises(ProfileFailure) as old:
        for group in batch.firings:
            check_firing_group(old_plan, group, old_budget)
    assert (old.value.reason, old.value.classification) == ("RULE_INPUT_BUDGET", "resource")
    seen = capture_pools(monkeypatch)
    assert recheck(inputs, batch) == "batch-consistent"
    pools = seen[0]
    assert pools.replay.usage == production.usage
    for pool in (pools.replay, pools.saved_encoding, pools.saved_issuance):
        assert pool.limits == ProfileLimits()
    assert pools.replay is not pools.saved_encoding
    assert pools.saved_encoding is not pools.saved_issuance
    usage = [dict(p.usage) for p in (pools.replay, pools.saved_encoding, pools.saved_issuance)]
    assert sum(u["input_bytes"] for u in usage) <= 2 * ProfileLimits().input_bytes
    assert sum(u["output_bytes"] for u in usage) <= 2 * ProfileLimits().output_bytes
    assert sum(u["work"] for u in usage) + pools.control.used <= (
        3 * ProfileLimits().work + pools.control.limit
    )


def test_original_false_matches_and_binding_order_are_preserved(monkeypatch):
    inputs = program(comparison=True)
    batch, production = produce(*inputs)
    assert batch.facts == (Triple(iri("urn:s2"), iri("urn:q"), literal("ok")),)
    assert batch.firings[0].bindings == (
        ("?v", literal("2", XSD + "integer")),
        ("?x", iri("urn:s2")),
    )
    assert tuple(k for k, _ in inputs[2][0].bindings) == ("?x", "?v")
    seen = capture_pools(monkeypatch)
    assert recheck(inputs, batch) == "batch-consistent"
    assert seen[0].replay.usage == production.usage
    # Caller provenance is a precondition: true-only input can be consistent,
    # but cannot be used to claim that the original false inputs were retained.
    assert recheck((inputs[0], inputs[1], (inputs[2][1],)), batch) == "batch-consistent"


@pytest.mark.parametrize("two_rules", (False, True))
def test_multihead_duplicates_source_proofs_and_full_fact_set(two_rules, monkeypatch):
    source = SourceRecord("source:1", "d" * 64, "r1", "same source, retained per occurrence")
    s, v = Variable("?s"), Variable("?v")
    when = Triple(s, iri("urn:in"), v)
    head1, head2 = (
        Triple(iri("urn:fixed"), iri("urn:q1"), v),
        Triple(iri("urn:fixed"), iri("urn:q2"), v),
    )
    spec = RuleSpec(
        "r",
        (when, when),
        (
            Comparison(v, "gt", literal("1", XSD + "integer")),
            Comparison(v, "le", literal("3", XSD + "decimal")),
        ),
        (head1, head1, head2),
        source,
        "r1",
        "d" * 64,
    )
    specs = (spec, replace(spec, rule_id="r2", heads=(head2,))) if two_rules else (spec,)
    matches = []
    for rule in specs:
        for subject, lex in (("f0", "0"), ("z", "3"), ("f4", "4"), ("a", "2")):
            term = literal(lex, XSD + "integer", source)
            triple = Triple(iri("urn:" + subject), iri("urn:in"), term)
            matches.append(
                BindingMatch(
                    rule.rule_id,
                    (("?v", term), ("?s", iri("urn:" + subject))),
                    (triple, triple),
                    ((subject + ":1", subject + ":1"), (subject + ":2",)),
                )
            )
    inputs = (specs, Catalog(data_properties=("urn:in", "urn:q1", "urn:q2")), tuple(matches))
    limits = replace(
        ProfileLimits(),
        firings=4 if two_rules else 2,
        head_occurrences=8 if two_rules else 6,
        heads=3,
        when=2,
        comparisons=2,
        bindings=len(matches),
        variables=2,
    )
    batch, production = produce(*inputs, limits)
    assert batch.facts == tuple(
        Triple(iri("urn:fixed"), iri(prop), literal(lex, XSD + "integer", source))
        for prop in ("urn:q1", "urn:q2")
        for lex in ("2", "3")
    )
    assert tuple((f.rule_id, f.bindings[0]) for f in batch.firings) == tuple(
        (rule.rule_id, ("?s", iri("urn:" + subject))) for rule in specs for subject in ("a", "z")
    )
    for firing in batch.firings:
        subject = firing.bindings[0][1].lexical_form.removeprefix("urn:")
        assert firing.source == source
        assert firing.revision == "r1"
        assert firing.definition_digest == "d" * 64
        assert firing.proof_leaves == ((subject + ":1", subject + ":1"), (subject + ":2",))
        assert firing.basis == (subject + ":1", subject + ":2")
        assert tuple(c.index for c in firing.comparisons) == (0, 1)
        assert all(c.result is True for c in firing.comparisons)
        assert tuple(h.index for h in firing.heads) == (
            (0, 1, 2) if firing.rule_id == "r" else (0,)
        )
    seen = capture_pools(monkeypatch)
    assert recheck(inputs, batch, limits) == "batch-consistent"
    assert seen[0].replay.usage == production.usage
    # Four unique facts are legal with F_i=2; facts use head_occurrences.
    assert len(batch.facts) == 4


@pytest.mark.parametrize("text", CASES["unicodeIris"])
def test_same_dbb_unicode_production_and_recheck(text):
    subject, prop, output = iri(text), iri(text + "/p"), iri(text + "/q")
    spec = RuleSpec(
        "unicode",
        (Triple(Variable("?x"), prop, subject),),
        (Comparison(subject, "eq", subject),),
        (Triple(Variable("?x"), output, subject),),
    )
    match = BindingMatch(
        "unicode", (("?x", subject),), (Triple(subject, prop, subject),), (("f",),)
    )
    inputs = (
        (spec,),
        Catalog(object_properties=(prop.lexical_form, output.lexical_form)),
        (match,),
    )
    batch, _ = produce(*inputs)
    assert batch.facts == (Triple(subject, output, subject),)
    assert recheck(inputs, batch) == "batch-consistent"


def test_tight_original_limits_copy_and_exact_usage(monkeypatch):
    inputs = program(comparison=True)
    _, baseline = produce(*inputs)
    used = dict(baseline.usage)
    limits = replace(
        ProfileLimits(),
        work=used["work"],
        input_bytes=used["input_bytes"],
        output_bytes=used["output_bytes"],
        firings=used["firings"],
        head_occurrences=used["head_occurrences"],
        trace_items=used["trace_items"],
        bindings=3,
        rules=1,
        comparisons=1,
        heads=1,
        when=1,
        variables=2,
    )
    batch, production = produce(*inputs, limits)
    seen = capture_pools(monkeypatch)
    assert recheck(inputs, batch, limits) == "batch-consistent"
    assert seen[0].replay.usage == production.usage
    assert seen[0].replay.limits == limits
    assert seen[0].replay.limits is not limits


@pytest.mark.parametrize("disabled", (True, False))
def test_absent_empty_definition_is_compile_only(disabled, monkeypatch):
    seen = capture_pools(monkeypatch)
    assert recheck(((), Catalog(), ()), None, disabled=disabled) == "definition-only"
    assert dict(seen[0].replay.usage)["output_bytes"] == 0
    assert dict(seen[0].saved_encoding.usage)["work"] == 0
    assert dict(seen[0].saved_issuance.usage)["work"] == 0


def test_disabled_nonempty_definition_only_and_definition_validation():
    inputs = program()
    assert recheck((inputs[0], inputs[1], ()), None, disabled=True) == "definition-only"
    invalid = replace(inputs[0][0], heads=())
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(((invalid,), inputs[1], ()), None, disabled=True)


def test_actual_empty_batches_still_replay_and_validate():
    inputs = program()
    for current in [((), Catalog(), ()), (inputs[0], inputs[1], ())]:
        batch, _ = produce(*current)
        assert batch.firings == batch.facts == ()
        assert recheck(current, batch) == "batch-consistent"
    false_inputs = program(comparison=True)
    false_inputs = (false_inputs[0], false_inputs[1], (false_inputs[2][0], false_inputs[2][2]))
    batch, _ = produce(*false_inputs)
    assert batch.firings == ()
    assert recheck(false_inputs, batch) == "batch-consistent"


@pytest.mark.parametrize(
    "case", ("enabled-missing", "disabled-with-batch", "disabled-with-matches")
)
def test_missing_or_fake_batch_is_not_definition_success(case):
    inputs = program()
    batch, _ = produce(*inputs)
    selected = None if case != "disabled-with-batch" else batch
    matches = inputs[2] if case == "disabled-with-matches" else ()
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck((inputs[0], inputs[1], matches), selected, disabled=case != "enabled-missing")


@pytest.mark.parametrize("field", [f.name for f in fields(ProfileLimits)])
@pytest.mark.parametrize("bad", (True, -1, "1", None))
def test_all_limit_fields_are_checked_before_pool_construction(field, bad):
    forged = ProfileLimits()
    object.__setattr__(forged, field, bad)
    with pytest.raises(ProfileFailure) as caught:
        recheck(((), Catalog(), ()), None, forged)
    assert caught.value.reason == "RULE_INPUT_BUDGET"
    assert caught.value.classification == "resource"


@pytest.mark.parametrize("field", [f.name for f in fields(ProfileLimits)])
def test_limit_fields_cannot_exceed_fixed_defaults(field):
    forged = ProfileLimits()
    object.__setattr__(forged, field, getattr(forged, field) + 1)
    with pytest.raises(ProfileFailure) as caught:
        recheck(((), Catalog(), ()), None, forged)
    assert caught.value.reason == "RULE_INPUT_BUDGET"


@pytest.mark.parametrize("limits", (None, {}, (), 1))
def test_limits_exact_type(limits):
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        revalidation.check_firing_batch((), Catalog(), (), None, limits=limits, disabled=False)


@pytest.mark.parametrize("disabled", (None, 0, 1, "false"))
def test_disabled_exact_bool(disabled):
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(((), Catalog(), ()), None, disabled=disabled)


@pytest.mark.parametrize("counter", ("work", "input_bytes", "output_bytes"))
def test_replay_resource_failure_propagates(counter):
    inputs = program()
    batch, _ = produce(*inputs)
    with pytest.raises(ProfileFailure) as caught:
        recheck(inputs, batch, replace(ProfileLimits(), **{counter: 0}))
    assert caught.value.classification == "resource"


def test_corrupt_saved_encoding_exhaustion_is_bounded(monkeypatch):
    inputs = program()
    batch, _ = produce(*inputs)
    corrupt = replace(batch.firings[-1], source=SourceRecord(text="private" * 100000))
    saved = replace(batch, firings=batch.firings[:-1] + (corrupt,))
    seen = capture_pools(monkeypatch)
    with pytest.raises(ProfileFailure) as caught:
        recheck(inputs, saved)
    assert caught.value.classification == "resource"
    assert dict(seen[0].saved_encoding.usage)["output_bytes"] > 0
    assert dict(seen[0].saved_issuance.usage)["work"] == 0
    assert "private" not in str(caught.value)


@pytest.mark.parametrize("phase", ("issuance", "control"))
def test_dependency_fault_resource_propagation_is_not_natural_success_case(monkeypatch, phase):
    inputs = program(comparison=True)
    batch, _ = produce(*inputs)
    if phase == "issuance":
        original = revalidation.check_value

        def exhaust(value, budget):
            budget.debit(budget.limits.work - dict(budget.usage)["work"] + 1)
            original(value, budget)

        monkeypatch.setattr(revalidation, "check_value", exhaust)
    else:
        original = revalidation._Control.same

        def exhaust(self, left, right):
            self.debit(self.limit - self.used + 1)
            original(self, left, right)

        monkeypatch.setattr(revalidation._Control, "same", exhaust)
    with pytest.raises(ProfileFailure) as caught:
        recheck(inputs, batch)
    assert (caught.value.reason, caught.value.classification) == ("WORK_LIMIT", "resource")


def test_control_debit_boundary_and_aggregate_formula():
    # Pure synthetic slots; not an I05 allocator, retry ledger or persistence test.
    limits = replace(ProfileLimits(), firings=10, output_bytes=2000)
    control = revalidation._Control()
    control.debit()
    control.bind(limits)
    expected = 1 + 10 + 10 * 32 + 4 * 2000 + 2 * 64 + 2 * len(PROFILE) + 4
    assert control.limit == expected
    control.debit(expected - 1)
    with pytest.raises(ProfileFailure) as caught:
        control.debit()
    assert caught.value.reason == "WORK_LIMIT"
    assert 100 * expected == 100 * (2 * 64 + 2 * len(PROFILE) + 5) + 33 * 1000 + 4 * 200000


@pytest.mark.parametrize("field", ("payload", "digest", "profile", "facts", "firings"))
def test_every_saved_connection_edge_is_checked(field):
    inputs = program(comparison=True)
    batch, _ = produce(*inputs)
    changes = {
        "payload": batch.payload[:-1] + b"X",
        "digest": "0" * 64,
        "profile": "X" + batch.profile[1:],
        "facts": (),
        "firings": (),
    }
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(inputs, replace(batch, **{field: changes[field]}))


def recanonicalize(batch):
    budget = Budget()
    payload = encode_output((PROFILE, batch.firings, batch.facts), budget)
    return replace(batch, payload=payload, digest=fingerprint(payload, budget))


@pytest.mark.parametrize(
    "field", ("source", "revision", "definition_digest", "basis", "proof_leaves", "when", "heads")
)
def test_late_group_tamper_even_with_self_consistent_hash_fails(field):
    inputs = program(long_source=False)
    batch, _ = produce(*inputs)
    changes = {
        "source": SourceRecord(text="private raw source"),
        "revision": "other",
        "definition_digest": "other",
        "basis": ("extra",),
        "proof_leaves": (("other",),),
        "when": (),
        "heads": (),
    }
    changed = replace(batch.firings[-1], **{field: changes[field]})
    saved = recanonicalize(replace(batch, firings=batch.firings[:-1] + (changed,)))
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(inputs, saved)


@pytest.mark.parametrize("forgery", ("constructor", "mutated-value", "mutated-term"))
def test_issued_identity_required_after_canonical_equality(forgery, monkeypatch):
    inputs = program(comparison=True)
    batch, _ = produce(*inputs)
    group = batch.firings[0]
    comparison = group.comparisons[0]
    value = comparison.left
    if forgery == "constructor":
        bad = ProfileValue(value.term, value.domain, value.value, value.language)
    elif forgery == "mutated-term":
        bad = parse_value(literal("02", XSD + "integer"), None, Budget())
        object.__setattr__(bad, "term", value.term)
    else:
        bad = parse_value(literal("999", XSD + "integer"), None, Budget())
        object.__setattr__(bad, "value", value.value)
        object.__setattr__(bad, "term", value.term)
    saved_comparison = replace(comparison, left=bad)
    saved_group = replace(group, comparisons=(saved_comparison,))
    saved = replace(batch, firings=(saved_group,))
    assert saved.payload == batch.payload
    # Byte-equivalent records do not possess the original issued fingerprint.
    seen = capture_pools(monkeypatch)
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(inputs, saved)
    assert dict(seen[0].saved_encoding.usage)["output_bytes"] > 0


def test_cross_module_and_deserialized_profile_values_are_not_issued_here(monkeypatch):
    from ontolearn_engine.quality import rule_terms

    inputs = program(comparison=True)
    batch, _ = produce(*inputs)
    comparison = batch.firings[0].comparisons[0]
    name = "ontolearn_engine.quality.revalidation_test_alias_terms"
    spec = importlib.util.spec_from_file_location(name, rule_terms.__file__)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    # Even the alias parser cannot issue through the canonical typed encoder.
    with pytest.raises(ProfileFailure):
        module.parse_value(comparison.left.term, None, Budget())
    original = comparison.left
    foreign = module.ProfileValue(original.term, original.domain, original.value, original.language)
    # A pickle roundtrip is an actual deserialization, not parse issuance.
    restored = pickle.loads(pickle.dumps(comparison.left))
    for unissued in (foreign, restored):
        changed = replace(comparison, left=unissued)
        saved = replace(batch, firings=(replace(batch.firings[0], comparisons=(changed,)),))
        with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
            recheck(inputs, saved)


@pytest.mark.parametrize("field", ("index", "operator", "result", "left", "right"))
def test_comparison_field_tampering_is_complete(field):
    inputs = program(comparison=True)
    batch, _ = produce(*inputs)
    comparison = batch.firings[0].comparisons[0]
    other = parse_value(literal("9", XSD + "integer"), None, Budget())
    replacements = {"index": 1, "operator": "ne", "result": False, "left": other, "right": other}
    changed = replace(comparison, **{field: replacements[field]})
    saved = recanonicalize(
        replace(batch, firings=(replace(batch.firings[0], comparisons=(changed,)),))
    )
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(inputs, saved)


@pytest.mark.parametrize("field", ("firings", "facts"))
@pytest.mark.parametrize("mode", ("duplicate", "extra", "reverse"))
def test_complete_batch_order_and_occurrences(field, mode):
    inputs = program()
    batch, _ = produce(*inputs)
    original = getattr(batch, field)
    changed = original + (original[0],) if mode != "reverse" else tuple(reversed(original))
    if mode == "extra" and field == "facts":
        changed = original + (Triple(iri("urn:extra"), iri("urn:q"), literal("ok")),)
    if mode == "extra" and field == "firings":
        changed = original + (replace(original[0], rule_id="extra"),)
    saved = recanonicalize(replace(batch, **{field: changed}))
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(inputs, saved)


def test_false_comparison_does_not_hide_late_type_error():
    x, v, w = Variable("?x"), Variable("?v"), Variable("?w")
    spec = RuleSpec(
        "late-error",
        (Triple(x, iri("urn:p"), v), Triple(x, iri("urn:p2"), w)),
        (
            Comparison(v, "gt", literal("1", XSD + "integer")),
            Comparison(w, "eq", literal("1", XSD + "integer")),
        ),
        (Triple(x, iri("urn:q"), literal("ok")),),
    )
    catalog = Catalog(data_properties=("urn:p", "urn:p2", "urn:q"))

    def match(subject, first, second):
        terms = iri(subject), literal(first, XSD + "integer"), second
        return BindingMatch(
            spec.rule_id,
            (("?x", terms[0]), ("?v", terms[1]), ("?w", terms[2])),
            (Triple(terms[0], iri("urn:p"), terms[1]), Triple(terms[0], iri("urn:p2"), terms[2])),
            (("f1",), ("f2",)),
        )

    valid = match("urn:valid", "2", literal("1", XSD + "integer"))
    late = match("urn:late", "0", literal("a private string"))
    valid_batch, _ = produce((spec,), catalog, (valid,))
    # The second comparison fails at runtime despite the first returning False.
    with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
        recheck(((spec,), catalog, (valid, late)), valid_batch)


def test_invalid_original_match_and_duplicate_false_are_not_ignored():
    inputs = program(comparison=True)
    batch, _ = produce(*inputs)
    for matches in (
        (inputs[2][0],) + inputs[2],
        inputs[2] + (replace(inputs[2][-1], proof_leaves=((), ())),),
    ):
        with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
            recheck((inputs[0], inputs[1], matches), batch)


def test_exact_top_types_and_foreign_callbacks_remain_inert():
    class Foreign:
        def __getattribute__(self, name):
            raise AssertionError("foreign callback invoked")

    inputs = program()
    batch, _ = produce(*inputs)
    for current, saved in (
        ((list(inputs[0]), inputs[1], inputs[2]), batch),
        ((inputs[0], Foreign(), inputs[2]), batch),
        ((inputs[0], inputs[1], list(inputs[2])), batch),
        (inputs, Foreign()),
    ):
        with pytest.raises(ProfileFailure, match="^INTERNAL_ERROR$"):
            recheck(current, saved)


def test_version_and_no_public_package_export():
    from ontolearn_engine import quality

    assert revalidation.REVALIDATION_BUDGET_VERSION == CASES["revalidationBudget"]
    assert "check_firing_batch" not in quality.__all__
