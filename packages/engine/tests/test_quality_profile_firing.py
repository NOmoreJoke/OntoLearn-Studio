"""Given-binding atomicity, complete occurrences, source and tamper witnesses."""

from dataclasses import replace

import pytest
from ontolearn_engine.quality.rule_firing import (
    BindingMatch,
    Catalog,
    Comparison,
    CompiledPlan,
    RuleSpec,
    Triple,
    Variable,
    check_firing_group,
    compile_rules,
    evaluate_bound_batch,
)
from ontolearn_engine.quality.rule_profile import (
    RDF,
    Budget,
    InputLocation,
    ProfileFailure,
    SourceRecord,
    TermInput,
)
from test_quality_profile_terms import fixture, term


def iri(s):
    return TermInput("iri", s)


def example(comparisons=None, heads=None, when=None):
    data = fixture("firing-cases.json")
    cat = Catalog(**{k: tuple(v) for k, v in data["catalog"].items()})
    definition = data["definition"]

    def raw(item):
        payload = dict(item)
        if payload.get("source") is not None:
            payload["source"] = SourceRecord(**payload["source"])
        return TermInput(**payload)

    def operand(item):
        if type(item) is str:
            return Variable(item) if item.startswith("?") else iri(item)
        return term(item["type"], item["lexical"])

    def pattern(row):
        return Triple(*(operand(item) for item in row))

    spec = RuleSpec(
        definition["rule_id"],
        tuple(pattern(row) for row in definition["when"]) if when is None else when,
        tuple(
            Comparison(operand(row[0]), row[1], operand(row[2]))
            for row in definition["comparisons"]
        )
        if comparisons is None
        else comparisons,
        tuple(pattern(row) for row in definition["heads"]) if heads is None else heads,
        SourceRecord(**definition["source"]),
        definition["revision"],
        definition["definition_digest"],
        definition["policy"],
    )
    match = BindingMatch(
        definition["rule_id"],
        tuple((name, raw(item)) for name, item in data["input_binding"]),
        tuple(
            Triple(raw(row["subject"]), raw(row["predicate"]), raw(row["object"]))
            for row in (data["input_when"] if when is None else data["input_when"] * len(when))
        ),
        tuple(
            tuple(row)
            for row in (
                data["input_proof_leaves"]
                if when is None
                else data["input_proof_leaves"] * len(when)
            )
        ),
    )
    return spec, cat, match


def execute(spec=None, match=None, limits=None):
    r, c, m = example()
    b = Budget(limits)
    p = compile_rules((spec or r,), c, b)
    return p, b, evaluate_bound_batch(p, (match or m,), b)


def test_complete_duplicate_heads_and_basis_fixture():
    p, b, batch = execute()
    expected = fixture("firing-cases.json")["expected"]
    group = batch.firings[0]
    assert [h.index for h in group.heads] == expected["head_indices"]
    assert [c.index for c in group.comparisons] == expected["comparison_indices"]
    assert group.basis == tuple(expected["basis"])
    assert len(batch.facts) == expected["unique_facts"]
    assert len(group.heads) == 2 and group.heads[0].triple == group.heads[1].triple
    assert group.comparisons[0].left.value.numerator == 2
    assert group.comparisons[0].right.value.numerator == 1
    assert group.source.reference == "fixture:firing-cases"
    import json
    from dataclasses import asdict
    from hashlib import sha256

    assert json.loads(json.dumps(asdict(group))) == expected["firing"]
    assert json.loads(json.dumps([asdict(t) for t in batch.facts])) == expected["facts"]
    assert batch.profile == expected["profile"]
    assert batch.digest == sha256(batch.payload).hexdigest()
    assert check_firing_group(p, group, b)


def test_duplicate_when_positions_and_distinct_firings_survive():
    r, c, m = example(when=(Triple(Variable("?s"), iri("urn:value"), Variable("?v")),) * 2)
    other = replace(
        m,
        bindings=(("?s", iri("urn:b")), ("?v", term("integer", "2"))),
        when=(Triple(iri("urn:b"), iri("urn:value"), term("integer", "2")),) * 2,
    )
    b = Budget()
    p = compile_rules((r,), c, b)
    result = evaluate_bound_batch(p, (other, m), b)
    assert len(result.firings) == 2
    assert result.firings[0].bindings[0][1] == iri("urn:a")
    assert len(result.firings[0].when) == 2
    assert len(result.firings[0].proof_leaves) == 2
    assert result.firings[0].basis == ("fact:1",)
    # Different bindings can produce exactly the same output; retain both firings.
    constant = replace(r, heads=(Triple(iri("urn:fixed"), iri("urn:out"), term("integer", "2")),))
    b = Budget()
    p = compile_rules((constant,), c, b)
    result = evaluate_bound_batch(p, (m, other), b)
    assert len(result.firings) == 2 and len(result.facts) == 1


def test_zero_match_bad_constant_and_unbound_have_real_locations():
    r, c, _ = example(comparisons=(Comparison(Variable("?v"), "eq", term("integer", "broken")),))
    with pytest.raises(ProfileFailure) as e:
        compile_rules((r,), c, Budget())
    assert (e.value.reason, e.value.location) == (
        "INVALID_LITERAL_LEXICAL",
        InputLocation("comparison", 0, "right"),
    )
    r = replace(r, comparisons=(Comparison(Variable("?missing"), "eq", term("integer", "1")),))
    with pytest.raises(ProfileFailure) as e:
        compile_rules((r,), c, Budget())
    assert e.value.reason == "UNBOUND_RULE_VARIABLE"
    assert e.value.location == InputLocation("comparison", 0, "left")


def test_false_does_not_hide_later_comparison_type_failure():
    r, c, m = example(
        comparisons=(
            Comparison(Variable("?v"), "lt", term("integer", "1")),
            Comparison(Variable("?v"), "eq", term("string", "x")),
        )
    )
    b = Budget()
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure) as e:
        evaluate_bound_batch(p, (m,), b)
    assert (e.value.reason, e.value.location) == (
        "RULE_COMPARISON_TYPE_MISMATCH",
        InputLocation("comparison", 1),
    )


def test_false_and_zero_match_are_successful_empty_batches():
    r, c, m = example(comparisons=(Comparison(Variable("?v"), "lt", term("integer", "1")),))
    b = Budget()
    p = compile_rules((r,), c, b)
    assert evaluate_bound_batch(p, (m,), b).firings == ()
    b = Budget()
    p = compile_rules((r,), c, b)
    assert evaluate_bound_batch(p, (), b).facts == ()


def test_later_head_and_binding_failure_have_no_partial_return():
    r, c, m = example(
        heads=(
            Triple(Variable("?s"), iri("urn:out"), Variable("?v")),
            Triple(Variable("?v"), iri("urn:out"), term("integer", "1")),
        )
    )
    b = Budget()
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure) as e:
        evaluate_bound_batch(p, (m,), b)
    assert (e.value.reason, e.value.location) == ("INVALID_RULE", InputLocation("head", 1))
    r, c, m = example()
    b = Budget()
    p = compile_rules((r,), c, b)
    corrupt = replace(m, bindings=(("?s", iri("urn:a")), ("?v", term("integer", "broken"))))
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        evaluate_bound_batch(p, (m, corrupt), b)


@pytest.mark.parametrize(
    "change",
    [
        lambda g: replace(g, heads=g.heads[:1]),
        lambda g: replace(g, comparisons=()),
        lambda g: replace(g, basis=("threshold-is-not-basis",)),
        lambda g: replace(g, policy="unknown"),
        lambda g: replace(g, revision="changed"),
        lambda g: replace(g, bindings=()),
    ],
)
def test_group_consistency_rejects_missing_or_changed_parts(change):
    p, b, batch = execute()
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        check_firing_group(p, change(batch.firings[0]), b)


def test_no_caller_marker_can_bypass_prevalidation_or_reuse_budget():
    r, c, m = example()
    b = Budget()
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        CompiledPlan((), c, "forged", b)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        evaluate_bound_batch(p, (m,), Budget())
    object.__setattr__(p, "digest", "tampered")
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        evaluate_bound_batch(p, (), b)


def test_duplicate_exact_match_is_internal_and_schema_outputs_rejected():
    r, c, m = example()
    b = Budget()
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        evaluate_bound_batch(p, (m, m), b)
    bad = replace(r, heads=(Triple(iri("urn:C"), iri(RDF + "type"), iri("urn:C")),))
    with pytest.raises(ProfileFailure, match="UNSUPPORTED_RULE_OUTPUT"):
        compile_rules((bad,), c, Budget())


@pytest.mark.parametrize(
    "corruption",
    [
        lambda m: replace(m, rule_id=False),
        lambda m: replace(m, bindings=None),
        lambda m: replace(m, proof_leaves=(("fact:1", object()),)),
        lambda m: replace(m, when=()),
    ],
)
def test_corrupt_trusted_bindings_remain_safe_internal(corruption):
    r, c, m = example()
    b = Budget()
    p = compile_rules((r,), c, b)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        evaluate_bound_batch(p, (corruption(m),), b)


def test_prepared_digest_available_when_original_revision_unknown():
    r, c, m = example()
    r = replace(r, revision=None, definition_digest=None, source=None)
    b = Budget()
    p = compile_rules((r,), c, b)
    g = evaluate_bound_batch(p, (m,), b).firings[0]
    assert g.revision is None and g.source is None
    assert len(g.definition_digest) == 64 and g.definition_digest == p.rules[0].prepared_digest


@pytest.mark.parametrize(
    "left,op,right",
    [
        (iri("urn:a"), "lt", iri("urn:b")),
        (term("boolean", "true"), "le", term("boolean", "false")),
        (term("string", "x"), "ne", term("integer", "1")),
    ],
)
def test_static_constant_pair_invalid_even_with_zero_matches(left, op, right):
    r, c, _ = example(comparisons=(Comparison(left, op, right),))
    with pytest.raises(ProfileFailure) as e:
        compile_rules((r,), c, Budget())
    assert e.value.reason == "RULE_COMPARISON_TYPE_MISMATCH"
    assert e.value.location == InputLocation("comparison", 0)


def test_static_constant_false_is_valid_and_produces_no_firing():
    r, c, m = example(comparisons=(Comparison(term("integer", "1"), "gt", term("integer", "2")),))
    b = Budget()
    p = compile_rules((r,), c, b)
    assert evaluate_bound_batch(p, (m,), b).firings == ()


@pytest.mark.parametrize(
    "predicate",
    [
        "http://www.w3.org/2000/01/rdf-schema#subClassOf",
        "http://www.w3.org/2002/07/owl#equivalentClass",
        "http://www.w3.org/ns/shacl#path",
        RDF + "Property",
    ],
)
def test_catalog_cannot_reclassify_schema_predicate(predicate):
    r, c, _ = example(heads=(Triple(Variable("?s"), iri(predicate), iri("urn:C")),))
    c = replace(c, object_properties=c.object_properties + (predicate,))
    with pytest.raises(ProfileFailure, match="UNSUPPORTED_RULE_OUTPUT"):
        compile_rules((r,), c, Budget())


def test_catalog_cannot_reclassify_schema_type_declaration():
    schema = "http://www.w3.org/2000/01/rdf-schema#Class"
    r, c, _ = example(heads=(Triple(Variable("?s"), iri(RDF + "type"), iri(schema)),))
    c = replace(c, classes=c.classes + (schema,))
    with pytest.raises(ProfileFailure, match="UNSUPPORTED_RULE_OUTPUT"):
        compile_rules((r,), c, Budget())


def test_copied_seal_and_public_digest_do_not_issue_a_plan():
    from ontolearn_engine.quality.rule_profile import encode_input, fingerprint

    r, c, _ = example()
    b = Budget()
    p = compile_rules((r,), c, b)
    broken = replace(
        p.rules[0].spec,
        comparisons=(Comparison(term("integer", "broken"), "eq", term("integer", "1")),),
    )
    rules = (replace(p.rules[0], spec=broken),)
    digest = fingerprint(encode_input((rules, c), b), b)
    forged = CompiledPlan(rules, c, digest, b, p._seal)
    with pytest.raises(ProfileFailure, match="INTERNAL_ERROR"):
        evaluate_bound_batch(forged, (), b)


@pytest.mark.parametrize("alias", ["simple-string", "source"])
def test_full_payload_stable_for_alias_and_source_representatives(alias):
    r, c, m = example(
        heads=(Triple(iri("urn:fixed"), iri("urn:out"), Variable("?v")),), comparisons=()
    )
    simple = TermInput("literal", "x", source=SourceRecord(text='"x"'))
    explicit = (
        TermInput(
            "literal",
            "x",
            "http://www.w3.org/2001/XMLSchema#string",
            source=SourceRecord(text='"x"^^xsd:string'),
        )
        if alias == "simple-string"
        else replace(simple, source=SourceRecord(text="alternate actual example source"))
    )

    def supplied(subject, t, leaf):
        return replace(
            m,
            bindings=(("?s", iri(subject)), ("?v", t)),
            when=(Triple(iri(subject), iri("urn:value"), t),),
            proof_leaves=((leaf,),),
        )

    a, z = supplied("urn:a", simple, "fact:a"), supplied("urn:z", explicit, "fact:z")
    outputs = []
    for matches in [(a, z), (z, a)]:
        b = Budget()
        p = compile_rules((r,), c, b)
        outputs.append(evaluate_bound_batch(p, matches, b))
    assert outputs[0] == outputs[1]
    assert outputs[0].payload == outputs[1].payload and outputs[0].digest == outputs[1].digest
    assert outputs[0].facts[0].object == simple
    assert [g.heads[0].triple.object for g in outputs[0].firings] == [simple, explicit]
    assert [g.basis for g in outputs[0].firings] == [("fact:a",), ("fact:z",)]
