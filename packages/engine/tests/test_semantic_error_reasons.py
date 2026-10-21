"""Real branches distinguish adapter failures, unsupported input, work and results."""

import pytest
from ontolearn_engine import semantic
from ontolearn_engine.semantic import Rule, parse_turtle, query, reason
from ontolearn_engine.semantic_offline import SemanticError
from ontolearn_engine.semantic_samples import EX, PREFIX
from rdflib import RDF, Graph, Literal, URIRef, Variable


@pytest.mark.parametrize("value", [None, 12, ["private-input"], {"private": "value"}])
def test_text_type_violation_is_not_a_capacity_error(value):
    with pytest.raises(SemanticError) as error:
        parse_turtle(value)
    assert error.value.code == "TEXT_TYPE_INVALID"
    assert str(error.value) == "TEXT_TYPE_INVALID"


def test_text_and_graph_input_limits_have_their_actual_source(monkeypatch):
    monkeypatch.setattr(semantic, "MAX_TEXT_BYTES", 4)
    with pytest.raises(SemanticError, match="TEXT_INPUT_LIMIT"):
        parse_turtle("longer-than-four")
    graph = Graph()
    for i in range(3):
        graph.add((URIRef(f"urn:{i}"), EX.p, Literal(i)))
    monkeypatch.setattr(semantic, "MAX_TRIPLES", 2)
    with pytest.raises(SemanticError, match="GRAPH_INPUT_LIMIT"):
        reason(graph)


@pytest.mark.parametrize(
    "text,expected",
    [
        ('"not-integer"^^xsd:integer', "INVALID_LITERAL_LEXICAL"),
        ('"valid-string"^^<urn:valid-but-unsupported-datatype>', "UNSUPPORTED_LITERAL_DATATYPE"),
        ('"NaN"^^xsd:double', "UNSUPPORTED_NONFINITE_LITERAL"),
    ],
)
def test_lexical_error_and_valid_unsupported_literal_are_distinct(text, expected, caplog):
    with pytest.raises(SemanticError) as error:
        parse_turtle(PREFIX + f":s :p {text} .")
    assert error.value.code == expected
    assert str(error.value) == expected
    assert "not-integer" not in caplog.text


def test_large_finite_decimal_is_not_mislabeled_nonfinite():
    graph = parse_turtle(PREFIX + ':s :p "' + "9" * 400 + '"^^xsd:decimal .')
    assert next(graph.objects(EX.s, EX.p)).toPython().is_finite()


def test_intermediate_match_budget_is_work_not_final_result(monkeypatch):
    graph = Graph()
    for i in range(3):
        graph.add((URIRef(f"urn:{i}"), EX.p, EX.y))
    rule = Rule("match", ((Variable("s"), EX.p, EX.y),), (Variable("s"), RDF.type, EX.C))
    monkeypatch.setattr(semantic, "MAX_RULE_MATCHES", 2)
    with pytest.raises(SemanticError, match="RULE_MATCH_WORK_LIMIT"):
        reason(graph, (rule,))


def test_final_rule_evidence_budget_is_result_not_intermediate_work(monkeypatch):
    graph = parse_turtle(PREFIX + ":x :p :y .")
    rule = Rule("match", ((EX.x, EX.p, EX.y),), (EX.x, RDF.type, EX.C))
    monkeypatch.setattr(semantic, "MAX_RULE_MATCHES", 1)
    with pytest.raises(SemanticError, match="RULE_EVIDENCE_RESULT_LIMIT"):
        reason(graph, (rule,))


def test_query_cartesian_result_limit_is_final_result(monkeypatch):
    graph = parse_turtle(PREFIX + ":s :p 1,2,3 .")
    monkeypatch.setattr(semantic, "MAX_TRIPLES", 3)
    with pytest.raises(SemanticError, match="QUERY_RESULT_LIMIT"):
        query(graph, "SELECT ?x ?y WHERE { ?s ?p ?x . ?s ?p ?y }")


def test_rdfs_expanded_graph_limit_is_final_result(monkeypatch):
    graph = parse_turtle(
        PREFIX
        + """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        :A rdfs:subClassOf :B . :x a :A . :y a :A ."""
    )
    monkeypatch.setattr(semantic, "MAX_TRIPLES", 3)
    with pytest.raises(SemanticError, match="RDFS_RESULT_LIMIT"):
        reason(graph)


@pytest.mark.parametrize(
    "extra,expected",
    [
        (":S sh:targetClass [] .", "SHAPE_TARGET_CLASS_INVALID"),
        (':P sh:datatype "not-an-IRI" .', "SHAPE_DATATYPE_INVALID"),
        (':P sh:path "not-an-IRI" .', "SHAPE_PATH_INVALID"),
        (":P sh:path [ sh:inversePath :name ] .", "UNSUPPORTED_SHACL_PATH"),
        (":P sh:path [] .", "SHAPE_PATH_UNCLASSIFIED"),
    ],
)
def test_non_iri_template_fields_are_not_all_misclassified_as_paths(extra, expected):
    from ontolearn_engine.semantic import check_shapes

    shapes = parse_turtle(
        PREFIX
        + """
        :S a sh:NodeShape; sh:targetClass :Equipment; sh:property :P .
        :P sh:minCount 1 ."""
        + extra,
        shapes=True,
    )
    with pytest.raises(SemanticError) as error:
        check_shapes(Graph(), shapes)
    assert error.value.code == expected


def test_malformed_rdfs_object_is_not_a_valid_unsupported_rdfs_construct():
    with pytest.raises(SemanticError, match="RDFS_TERM_INVALID"):
        parse_turtle(
            PREFIX
            + """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            :A rdfs:subClassOf "not-a-class-IRI" ."""
        )
