"""Selected real payload stays selected; projection never regenerates inference."""

import copy
import json

import pytest
from ontolearn_engine import semantic_scopes
from ontolearn_engine.semantic import Rule, check_shapes, parse_turtle
from ontolearn_engine.semantic_offline import SemanticError
from ontolearn_engine.semantic_samples import EX, NEXT, PREFIX, RISK, SHAPES
from ontolearn_engine.semantic_scopes import prepare_validation_scope, project_validation_scope
from rdflib import RDF, RDFS, XSD, Graph, Literal, URIRef, Variable


def case(rules=(RISK,)):
    facts = parse_turtle(
        PREFIX + ':unit a :CriticalPump; :alarm :alert . :alert :level "High"; :status "Open" .'
    )
    ontology = parse_turtle(
        PREFIX
        + """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        :CriticalPump rdfs:subClassOf :Pump . :Pump rdfs:subClassOf :Equipment ."""
    )
    generated = prepare_validation_scope(facts, ontology, include_derived=True, rules=rules)
    return facts, ontology, generated


def project(facts, ontology, generated, payload=None, rules=(RISK,)):
    return project_validation_scope(
        facts,
        ontology,
        include_derived=True,
        reasoning_result=generated.reasoning_result if payload is None else payload,
        reasoning_source=generated.provenance["reasoningSource"],
        rules=rules,
    )


@pytest.mark.parametrize("serialized", [False, True])
def test_actual_selected_output_projects_without_recalculation_and_keeps_original(
    serialized, monkeypatch
):
    facts, ontology, generated = case()
    original_facts, original_ontology = set(facts), set(ontology)
    payload = generated.reasoning_result
    if serialized:
        payload = json.loads(json.dumps(payload))
    original_payload = copy.deepcopy(payload)

    def forbidden(*args, **kwargs):
        raise AssertionError("selected result must not be replaced by fresh inference")

    monkeypatch.setattr(semantic_scopes, "reason", forbidden)
    selected = project(facts, ontology, generated, payload)
    assert selected.reasoning_result is payload
    assert payload == original_payload
    assert set(selected.facts) == set(generated.facts)
    assert set(selected.ontology) == set(generated.ontology)
    assert selected.provenance == generated.provenance
    assert set(facts) == original_facts and set(ontology) == original_ontology
    # The returned display provenance cannot rewrite the retained selected payload.
    selected.provenance["selectedFacts"][-1]["sources"].clear()
    selected.provenance["derivedAxioms"][0]["source"]["basis"].clear()
    selected.provenance["warnings"].append("display-only")
    assert payload == original_payload


def test_explicit_older_rule_plan_and_output_are_not_replaced_by_current_rule_result(monkeypatch):
    facts, ontology, older = case(rules=())
    current = prepare_validation_scope(facts, ontology, include_derived=True, rules=(RISK,))
    assert (EX.unit, RDF.type, EX.HighRiskEquipment) in current.facts
    assert (EX.unit, RDF.type, EX.HighRiskEquipment) not in older.facts
    payload = json.loads(json.dumps(older.reasoning_result))
    monkeypatch.setattr(
        semantic_scopes, "reason", lambda *a, **kw: pytest.fail("recomputed selection")
    )
    selected = project(facts, ontology, older, payload, rules=())
    assert (EX.unit, RDF.type, EX.HighRiskEquipment) not in selected.facts
    assert selected.reasoning_result is payload
    assert selected.provenance["selectedRuleIds"] == []
    assert len(check_shapes(selected.facts, parse_turtle(SHAPES, shapes=True))["violations"]) == 1


@pytest.mark.parametrize("layer", ["facts", "ontology", "rules", "version"])
def test_declared_producer_context_must_match_complete_inputs_including_unused_facts(layer):
    facts, ontology, generated = case()
    source = dict(generated.provenance["reasoningSource"])
    rules = (RISK,)
    if layer == "facts":
        facts.add((EX.unused, EX.name, Literal("unrelated new fact")))
    elif layer == "ontology":
        ontology.add((EX.unused, RDFS.subClassOf, EX.Equipment))
    elif layer == "rules":
        rules = ()
    else:
        source["executionSemanticsVersion"] = "foreign-producer"
    with pytest.raises(SemanticError, match="^REASONING_SOURCE_MISMATCH$"):
        project_validation_scope(
            facts,
            ontology,
            include_derived=True,
            reasoning_result=generated.reasoning_result,
            reasoning_source=source,
            rules=rules,
        )


@pytest.mark.parametrize("payload", [None, {}, [], {"rdfs": []}])
def test_missing_or_incomplete_selected_payload_is_not_recomputed(payload):
    facts, ontology, generated = case()
    with pytest.raises(SemanticError, match="^REASONING_RESULT_INVALID$"):
        project_validation_scope(
            facts,
            ontology,
            include_derived=True,
            reasoning_result=payload,
            reasoning_source=generated.provenance["reasoningSource"],
            rules=(RISK,),
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-rdfs-evidence",
        "missing-rule-evidence",
        "missing-rdfs-row",
        "missing-rule-row",
        "extra-rdfs-row",
        "extra-rule-row",
        "duplicate-rdfs",
        "duplicate-evidence",
        "unknown-rule",
        "wrong-rule-binding",
        "foreign-rdfs-basis",
        "wrong-rule-basis",
        "rule-output-axiom",
        "wrong-rdfs-role",
        "wrong-warning",
        "extra-field",
        "bad-term",
    ],
)
def test_corrupt_selected_payload_is_rejected_without_partial_projection(mutation):
    facts, ontology, generated = case(rules=(RISK, NEXT))
    payload = json.loads(json.dumps(generated.reasoning_result))
    if mutation == "missing-rdfs-evidence":
        payload["rdfsEvidence"].pop()
    elif mutation == "missing-rule-evidence":
        payload["evidence"].clear()
    elif mutation == "missing-rdfs-row":
        payload["rdfs"].pop()
    elif mutation == "missing-rule-row":
        payload["rules"].clear()
    elif mutation == "extra-rdfs-row":
        payload["rdfs"].append([EX.foreign.n3(), RDF.type.n3(), EX.Equipment.n3()])
    elif mutation == "extra-rule-row":
        payload["rules"].append([EX.foreign.n3(), RDF.type.n3(), EX.HighRiskEquipment.n3()])
    elif mutation == "duplicate-rdfs":
        payload["rdfs"].append(payload["rdfs"][0])
    elif mutation == "duplicate-evidence":
        payload["evidence"].append(copy.deepcopy(payload["evidence"][0]))
    elif mutation == "unknown-rule":
        payload["evidence"][0]["rule"] = "unknown-rule"
    elif mutation == "wrong-rule-binding":
        payload["evidence"][0]["inputs"][0][0] = EX.foreign.n3()
    elif mutation == "foreign-rdfs-basis":
        payload["rdfsEvidence"][0]["basis"][0][0] = EX.foreign.n3()
    elif mutation == "wrong-rule-basis":
        payload["evidence"][0]["basis"].pop()
    elif mutation == "rule-output-axiom":
        row = [EX.Pump.n3(), RDFS.subClassOf.n3(), EX.foreign.n3()]
        payload["rules"][0] = row
        payload["evidence"][0]["result"] = row
    elif mutation == "wrong-rdfs-role":
        old = payload["rdfs"][0]
        row = [EX.foreign.n3(), EX.name.n3(), '"unexpected-domain-property"']
        payload["rdfs"][0] = row
        next(e for e in payload["rdfsEvidence"] if e["result"] == old)["result"] = row
    elif mutation == "wrong-warning":
        payload["warnings"].clear()
    elif mutation == "extra-field":
        payload["private"] = "not part of original finite output"
    else:
        payload["rdfs"][0][0] = "[<urn:graph>]"
    original_payload = copy.deepcopy(payload)
    original_facts, original_ontology = set(facts), set(ontology)
    with pytest.raises(SemanticError) as error:
        project(facts, ontology, generated, payload, rules=(RISK, NEXT))
    assert error.value.code == "REASONING_RESULT_INVALID"
    assert str(error.value) == "REASONING_RESULT_INVALID"
    assert payload == original_payload
    assert set(facts) == original_facts and set(ontology) == original_ontology


def test_rules_can_read_original_ontology_and_output_existing_assertion_with_two_sources():
    facts = parse_turtle(PREFIX + ":unit a :Equipment .")
    ontology = Graph()
    ontology.add((EX.C, RDFS.subClassOf, EX.Equipment))
    rule = Rule(
        "ontology-condition",
        ((EX.C, RDFS.subClassOf, EX.Equipment),),
        (EX.unit, RDF.type, EX.Equipment),
    )
    generated = prepare_validation_scope(facts, ontology, include_derived=True, rules=(rule,))
    selected = project(
        facts,
        ontology,
        generated,
        json.loads(json.dumps(generated.reasoning_result)),
        rules=(rule,),
    )
    assert set(selected.facts) == set(facts)
    assert selected.provenance["selectedFacts"][0]["sources"] == [
        {"kind": "asserted"},
        {
            "kind": "rule",
            "rule": rule.id,
            "inputs": [(EX.C.n3(), RDFS.subClassOf.n3(), EX.Equipment.n3())],
            "basis": [(EX.C.n3(), RDFS.subClassOf.n3(), EX.Equipment.n3())],
        },
    ]


def test_multiple_legitimate_matches_for_one_result_keep_all_evidence():
    facts = parse_turtle(PREFIX + ":unit :alarm :a, :b .")
    rule = Rule("two", ((EX.unit, EX.alarm, Variable("alarm")),), (EX.unit, RDF.type, EX.Equipment))
    generated = prepare_validation_scope(facts, Graph(), include_derived=True, rules=(rule,))
    selected = project(facts, Graph(), generated, rules=(rule,))
    assert len(selected.reasoning_result["evidence"]) == 2
    record = next(
        row for row in selected.provenance["selectedFacts"] if row["triple"][1] == RDF.type.n3()
    )
    assert len(record["sources"]) == 2


@pytest.mark.parametrize("with_source", [False, True])
def test_asserted_selection_rejects_unselected_payload_or_context(with_source):
    facts, ontology, generated = case()
    with pytest.raises(SemanticError, match="^UNSELECTED_REASONING_PRESENT$"):
        project_validation_scope(
            facts,
            ontology,
            include_derived=False,
            reasoning_result=None if with_source else generated.reasoning_result,
            reasoning_source=generated.provenance["reasoningSource"] if with_source else None,
        )


def test_projection_has_a_cumulative_budget_and_never_mutates_selected_payload(monkeypatch):
    facts, ontology, generated = case()
    original = copy.deepcopy(generated.reasoning_result)
    monkeypatch.setattr(semantic_scopes, "MAX_PROJECTION_ITEMS", 2)
    with pytest.raises(SemanticError, match="^WORK_LIMIT$"):
        project(facts, ontology, generated)
    assert generated.reasoning_result == original


@pytest.mark.parametrize("value", ["中文名称", 'line\n"quoted"\\tail', "多行\n名称"])
def test_real_rule_literal_outputs_round_trip_canonical_n3(value):
    facts = parse_turtle(PREFIX + ":unit a :Equipment .")
    rule = Rule("literal", ((EX.unit, RDF.type, EX.Equipment),), (EX.unit, EX.name, Literal(value)))
    generated = prepare_validation_scope(facts, Graph(), include_derived=True, rules=(rule,))
    selected = project(
        facts, Graph(), generated, json.loads(json.dumps(generated.reasoning_result)), rules=(rule,)
    )
    assert (EX.unit, EX.name, Literal(value)) in selected.facts


def test_real_empty_selection_is_not_confused_with_missing_payload(monkeypatch):
    generated = prepare_validation_scope(Graph(), Graph(), include_derived=True)
    monkeypatch.setattr(
        semantic_scopes, "reason", lambda *a, **kw: pytest.fail("recomputed empty selection")
    )
    selected = project(Graph(), Graph(), generated, rules=())
    assert selected.reasoning_result == {
        "rdfs": [],
        "rules": [],
        "warnings": [],
        "evidence": [],
        "rdfsEvidence": [],
    }
    assert len(selected.facts) == len(selected.ontology) == 0


def test_selected_payload_cannot_claim_second_rule_reads_first_rule_output():
    facts, ontology, generated = case(rules=(RISK, NEXT))
    payload = json.loads(json.dumps(generated.reasoning_result))
    risk_output = payload["rules"][0]
    chained_output = [EX.unit.n3(), RDF.type.n3(), EX.NeedsInspection.n3()]
    payload["rules"].append(chained_output)
    payload["evidence"].append(
        {
            "rule": NEXT.id,
            "result": chained_output,
            "inputs": [risk_output],
            "basis": copy.deepcopy(payload["evidence"][0]["basis"]),
        }
    )
    with pytest.raises(SemanticError, match="^REASONING_RESULT_INVALID$"):
        project(facts, ontology, generated, payload, rules=(RISK, NEXT))


@pytest.mark.parametrize(
    "literal",
    [
        Literal("01", datatype=XSD.integer, normalize=False),
        Literal("1.00", datatype=XSD.decimal, normalize=False),
        Literal("true", datatype=XSD.boolean, normalize=False),
        Literal("名称", lang="zh-CN"),
    ],
)
def test_true_non_normalized_lexical_output_is_preserved_without_global_settings(literal):
    import rdflib

    before = rdflib.NORMALIZE_LITERALS
    facts = parse_turtle(PREFIX + ":unit a :Equipment .")
    rule = Rule("lexical", ((EX.unit, RDF.type, EX.Equipment),), (EX.unit, EX.name, literal))
    generated = prepare_validation_scope(facts, Graph(), include_derived=True, rules=(rule,))
    payload = json.loads(json.dumps(generated.reasoning_result))
    selected = project(facts, Graph(), generated, payload, rules=(rule,))
    assert (EX.unit, EX.name, literal) in selected.facts
    assert selected.reasoning_result is payload
    assert payload["rules"][0][2] == literal.n3()
    assert rdflib.NORMALIZE_LITERALS is before


def test_invalid_unicode_in_selected_row_has_only_fixed_safe_error():
    facts, ontology, generated = case()
    payload = json.loads(json.dumps(generated.reasoning_result))
    old = payload["rdfs"][0]
    row = ["<urn:\ud800>", old[1], old[2]]
    payload["rdfs"][0] = row
    next(e for e in payload["rdfsEvidence"] if e["result"] == old)["result"] = row
    with pytest.raises(SemanticError, match="^REASONING_RESULT_INVALID$"):
        project(facts, ontology, generated, payload)


def test_invalid_unicode_in_input_graph_cannot_escape_source_fingerprint():
    facts = Graph()
    facts.add((URIRef("urn:\ud800"), RDF.type, EX.Equipment))
    with pytest.raises(SemanticError, match="^INVALID_UNICODE$"):
        prepare_validation_scope(facts, Graph(), include_derived=False)


@pytest.mark.parametrize("term", ['"x"^^xsd:string', '"x"^^[<urn:graph>]', '"x"^^{<urn:graph>}'])
def test_selected_literal_datatype_cannot_use_general_n3_forms(term):
    facts, ontology, generated = case()
    payload = json.loads(json.dumps(generated.reasoning_result))
    payload["rules"][0][2] = term
    payload["evidence"][0]["result"][2] = term
    with pytest.raises(SemanticError, match="^REASONING_RESULT_INVALID$"):
        project(facts, ontology, generated, payload)


def test_final_projected_view_budget_is_result_capacity(monkeypatch):
    facts, ontology, generated = case()
    monkeypatch.setattr(semantic_scopes, "MAX_TRIPLES", len(facts))
    with pytest.raises(SemanticError, match="^PROJECTION_RESULT_LIMIT$"):
        project(facts, ontology, generated)
