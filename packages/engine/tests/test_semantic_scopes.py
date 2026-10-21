"""Real-library scope selection, type preservation and provenance regressions."""

import pytest
from ontolearn_engine.semantic import check_shapes, parse_turtle, reason
from ontolearn_engine.semantic_offline import SemanticError
from ontolearn_engine.semantic_samples import EX, NEXT, PREFIX, RISK, SHAPES, scope_suite
from ontolearn_engine.semantic_scopes import prepare_validation_scope
from rdflib import OWL, RDF, RDFS, Graph, Literal


def test_complete_real_two_scope_sample():
    result = scope_suite()
    assert result["asserted"]["validation"]["conforms"] is True
    assert result["assertedWithSelectedDerived"]["validation"]["conforms"] is False


def test_asserted_only_reports_existing_direct_type_violation():
    data = parse_turtle(PREFIX + ":direct a :Equipment . :other a :CriticalPump .")
    ontology = Graph()
    ontology.add((EX.CriticalPump, RDFS.subClassOf, EX.Equipment))
    selected = prepare_validation_scope(data, ontology, include_derived=False)
    assert check_shapes(selected.facts, parse_turtle(SHAPES, shapes=True)) == {
        "conforms": False,
        "violations": [
            {
                "focus": EX.direct.n3(),
                "path": EX.name.n3(),
                "constraint": "<http://www.w3.org/ns/shacl#MinCountConstraintComponent>",
                "sourceShape": EX.NameProperty.n3(),
                "value": None,
                "severity": "<http://www.w3.org/ns/shacl#Violation>",
            }
        ],
    }
    assert selected.provenance["derivedAxioms"] == []


def test_selected_rules_only_change_selected_derived_facts():
    data = parse_turtle(
        PREFIX + ':unit a :Equipment; :alarm :alert . :alert :level "High"; :status "Open" .'
    )
    without = prepare_validation_scope(data, Graph(), include_derived=True)
    with_rule = prepare_validation_scope(data, Graph(), include_derived=True, rules=(RISK,))
    assert (EX.unit, RDF.type, EX.HighRiskEquipment) not in without.facts
    assert set(with_rule.facts) == set(without.facts) | {(EX.unit, RDF.type, EX.HighRiskEquipment)}
    assert without.provenance["selectedRuleIds"] == []
    assert with_rule.provenance["selectedRuleIds"] == ["R-risk"]
    assert without.provenance["selectedRulesSha256"] != with_rule.provenance["selectedRulesSha256"]
    assert set(data) == set(without.facts)


@pytest.mark.parametrize(
    "triple",
    [
        (EX.A, RDFS.subClassOf, EX.B),
        (EX.p, RDFS.domain, EX.A),
        (EX.p, RDFS.range, EX.B),
        (EX.A, RDF.type, OWL.Class),
    ],
)
def test_misassigned_axioms_are_rejected_not_silently_removed(triple):
    data = Graph()
    data.add(triple)
    with pytest.raises(SemanticError, match="FACT_SCOPE_CONTAINS_AXIOMS"):
        prepare_validation_scope(data, Graph(), include_derived=True)


def test_misassigned_domain_facts_in_ontology_are_rejected():
    ontology = Graph()
    ontology.add((EX.unit, EX.name, Literal("Pump")))
    with pytest.raises(SemanticError, match="ONTOLOGY_SCOPE_CONTAINS_FACTS"):
        prepare_validation_scope(Graph(), ontology, include_derived=False)


@pytest.mark.parametrize(
    "selection,rules,code",
    [("yes", (), "SCOPE_SELECTION_TYPE_INVALID"), (False, (RISK,), "UNSELECTED_RULES_PRESENT")],
)
def test_scope_selection_must_be_explicit_and_no_ignored_rules(selection, rules, code):
    with pytest.raises(SemanticError, match=code):
        prepare_validation_scope(Graph(), Graph(), include_derived=selection, rules=rules)


def test_selected_scope_preserves_rule_chain_warning():
    data = parse_turtle(
        PREFIX + ':unit a :Equipment; :alarm :alert . :alert :level "High"; :status "Open" .'
    )
    selected = prepare_validation_scope(data, Graph(), include_derived=True, rules=(RISK, NEXT))
    assert selected.provenance["warnings"] == ["RULE_CHAIN_UNSUPPORTED:R-next"]
    assert (EX.unit, RDF.type, EX.HighRiskEquipment) in selected.facts
    assert (EX.unit, RDF.type, EX.NeedsInspection) not in selected.facts
    assert (
        prepare_validation_scope(data, Graph(), include_derived=False).provenance["warnings"] == []
    )


def test_domain_range_types_remain_in_selected_scope_and_keep_axiom_basis():
    data = parse_turtle(PREFIX + ":unit :alarm :alert .")
    ontology = Graph()
    ontology.add((EX.alarm, RDFS.domain, EX.Equipment))
    ontology.add((EX.alarm, RDFS.range, EX.Alarm))
    selected = prepare_validation_scope(data, ontology, include_derived=True)
    assert set(selected.facts) == set(data) | {
        (EX.unit, RDF.type, EX.Equipment),
        (EX.alert, RDF.type, EX.Alarm),
    }
    assert set(selected.ontology) == set(ontology)
    source = {row["triple"]: row["sources"] for row in selected.provenance["selectedFacts"]}
    assert source[(EX.unit.n3(), RDF.type.n3(), EX.Equipment.n3())] == [
        {
            "kind": "rdfs",
            "basis": sorted(
                [
                    (EX.alarm.n3(), RDFS.domain.n3(), EX.Equipment.n3()),
                    (EX.unit.n3(), EX.alarm.n3(), EX.alert.n3()),
                ]
            ),
        }
    ]


def test_scope_views_copy_inputs_and_are_isolated_between_calls():
    data = parse_turtle(PREFIX + ':unit a :Equipment; :name "Pump" .')
    ontology = Graph()
    first = prepare_validation_scope(data, ontology, include_derived=False)
    second = prepare_validation_scope(data, ontology, include_derived=False)
    assert first.provenance == second.provenance
    first.facts.remove((EX.unit, EX.name, None))
    assert set(second.facts) == set(data)
    assert (EX.unit, EX.name, Literal("Pump")) in data


def test_complete_reasoning_output_is_preserved_without_rewriting_or_filtering():
    data = parse_turtle(
        PREFIX + ':unit a :CriticalPump; :alarm :alert . :alert :level "High"; :status "Open" .'
    )
    ontology = parse_turtle(
        PREFIX
        + """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        :CriticalPump rdfs:subClassOf :Pump . :Pump rdfs:subClassOf :Equipment ."""
    )
    original_data, original_ontology = set(data), set(ontology)
    combined = Graph()
    for triple in (*data, *ontology):
        combined.add(triple)
    expected = reason(combined, (RISK, NEXT))
    selected = prepare_validation_scope(data, ontology, include_derived=True, rules=(RISK, NEXT))
    assert selected.reasoning_result == expected
    assert selected.reasoning_result["warnings"] == ["RULE_CHAIN_UNSUPPORTED:R-next"]
    assert (EX.CriticalPump.n3(), RDFS.subClassOf.n3(), EX.Equipment.n3()) in expected["rdfs"]
    assert (EX.unit.n3(), RDF.type.n3(), EX.Equipment.n3()) in expected["rdfs"]
    assert set(data) == original_data and set(ontology) == original_ontology
    assert prepare_validation_scope(data, ontology, include_derived=False).reasoning_result is None
