"""Real-library regressions for finite semantics and denied external I/O."""

import socket
import urllib.request

import pytest
from ontolearn_engine.semantic import Rule, check_shapes, parse_turtle, query, reason
from ontolearn_engine.semantic_offline import SemanticError, offline
from ontolearn_engine.semantic_samples import (
    EX,
    NEXT,
    PREFIX,
    RISK,
    SHAPES,
    execute_case,
    rejection_cases,
    suite,
)
from ontolearn_engine.storage_probe import fixture
from rdflib import RDF, RDFS, SH, XSD, BNode, Graph, Literal, URIRef, Variable


def test_complete_g2_suite():
    assert suite()["baseline"] == "I05-G2-v1"


@pytest.mark.parametrize("name,code,case", rejection_cases("http://127.0.0.1:9/deny"))
def test_explicit_rejection(name, code, case):
    with pytest.raises(SemanticError) as error:
        execute_case(case)
    assert error.value.code == code, name


@pytest.mark.parametrize(
    "action",
    [
        lambda: socket.socket(),
        lambda: socket.getaddrinfo("example.invalid", 80),
        lambda: urllib.request.urlopen("http://127.0.0.1:9/deny"),
    ],
)
def test_io_backstop_and_scope(action):
    with offline(), pytest.raises(SemanticError, match="EXTERNAL_ACCESS_DENIED"):
        action()
    # Context restored: unrelated task can create a local socket after the guard exits.
    with socket.socket() as sock:
        assert sock.fileno() >= 0


def test_scope_is_context_local():
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as executor, offline():
        assert executor.submit(lambda: socket.socket().close()).result() is None
        with pytest.raises(SemanticError):
            socket.socket()


@pytest.mark.parametrize(
    "text",
    [
        "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
        "DESCRIBE <urn:s>",
        "INSERT DATA { <urn:s> <urn:p> <urn:o> }",
        "DELETE WHERE { ?s ?p ?o }",
        "LOAD <http://127.0.0.1:9/deny>",
        "SELECT (RAND() AS ?r) WHERE {}",
        "SELECT (NOW() AS ?r) WHERE {}",
        "SELECT (<urn:custom>() AS ?r) WHERE {}",
    ],
)
def test_non_readonly_or_nondeterministic(text):
    with pytest.raises(SemanticError):
        query(Graph(), text)


def test_literals_with_network_words_are_data():
    graph = parse_turtle('<urn:s> <urn:p> "SERVICE FROM owl:imports"@zh .')
    assert query(graph, "SELECT ?o WHERE { <urn:s> <urn:p> ?o }")["rows"] == [
        ['"SERVICE FROM owl:imports"@zh']
    ]


@pytest.mark.parametrize(
    "text,code",
    [
        (
            "@prefix owl: <http://www.w3.org/2002/07/owl#> . <urn:s> owl:sameAs <urn:o> .",
            "UNSUPPORTED_OWL",
        ),
        (
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . "
            "<urn:s> rdfs:subPropertyOf <urn:o> .",
            "UNSUPPORTED_RDFS",
        ),
        ('[] <urn:p> "x" .', "UNSUPPORTED_BLANK_NODE"),
        ('<urn:s> <urn:p> ("x") .', "UNSUPPORTED_BLANK_NODE"),
    ],
)
def test_unsupported_rdf_not_silently_dropped(text, code):
    with pytest.raises(SemanticError, match=code):
        parse_turtle(text)


def test_rdfs_closure_domain_range_cycle_and_proof():
    graph = parse_turtle("""@prefix : <urn:test:> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        :A rdfs:subClassOf :B . :B rdfs:subClassOf :C . :C rdfs:subClassOf :A .
        :x a :A; :p :y . :p rdfs:domain :D; rdfs:range :E .""")
    result = reason(graph)
    ns = "urn:test:"
    expected = {
        (f"<{ns}{s}>", RDF.type.n3(), f"<{ns}{o}>")
        for s, o in (("x", "B"), ("x", "C"), ("x", "D"), ("y", "E"))
    }
    hierarchy = {
        (f"<{ns}{s}>", RDFS.subClassOf.n3(), f"<{ns}{o}>") for s in "ABC" for o in "ABC"
    } - {
        (f"<{ns}{s}>", RDFS.subClassOf.n3(), f"<{ns}{o}>")
        for s, o in (("A", "B"), ("B", "C"), ("C", "A"))
    }
    assert set(result["rdfs"]) == expected | hierarchy
    assert all(row["basis"] for row in result["rdfsEvidence"])


def test_no_rule_or_rdfs_feedback_and_asserted_match_allowed():
    graph = parse_turtle(fixture(1))
    graph.add((EX.HighRiskEquipment, RDFS.subClassOf, EX.NeedsInspection))
    result = reason(graph, (RISK, NEXT))
    assert result["rules"] == [
        ("<urn:case:0:equipment/001>", RDF.type.n3(), EX.HighRiskEquipment.n3())
    ]
    assert result["rdfs"] == []
    graph.add((URIRef("urn:case:0:equipment/002"), RDF.type, EX.HighRiskEquipment))
    assert ("<urn:case:0:equipment/002>", RDF.type.n3(), EX.NeedsInspection.n3()) in reason(
        graph, (RISK, NEXT)
    )["rules"]


def test_multiple_matches_preserve_all_rule_evidence_and_inputs_unchanged():
    graph = parse_turtle(fixture(1))
    equipment = URIRef("urn:case:0:equipment/001")
    for triple in (
        (equipment, EX.alarm, EX.A04),
        (EX.A04, EX.level, Literal("High")),
        (EX.A04, EX.status, Literal("Open")),
    ):
        graph.add(triple)
    before = set(graph)
    result = reason(graph, (RISK,))
    assert len(result["rules"]) == 1
    assert {row["inputs"][1][2] for row in result["evidence"]} == {
        "<urn:case:0:alarm/A01>",
        EX.A04.n3(),
    }
    assert set(graph) == before


def test_rule_repeated_variable_and_unbound_output():
    s, o = Variable("s"), Variable("o")
    rule = Rule("same", ((s, EX.p, s),), (s, RDF.type, EX.Self))
    graph = parse_turtle("<urn:a> <urn:ontolearn:p> <urn:b> . <urn:c> <urn:ontolearn:p> <urn:c> .")
    assert reason(graph, (rule,))["rules"] == [("<urn:c>", RDF.type.n3(), EX.Self.n3())]
    with pytest.raises(SemanticError, match="UNBOUND_RULE_VARIABLE"):
        reason(graph, (Rule("bad", ((s, EX.p, s),), (o, RDF.type, EX.Self)),))


@pytest.mark.parametrize(
    "constraint,value,expected",
    [
        ("sh:datatype xsd:integer", '"oops"', "DatatypeConstraintComponent"),
        ("sh:maxCount 1", "1, 2", "MaxCountConstraintComponent"),
        ('sh:in ("ok" "good")', '"bad"', "InConstraintComponent"),
        ("sh:minInclusive 2", "1", "MinInclusiveConstraintComponent"),
        ("sh:maxInclusive 2", "3", "MaxInclusiveConstraintComponent"),
    ],
)
def test_real_supported_shacl(constraint, value, expected):
    data = parse_turtle(PREFIX + f":x a :Equipment; :name {value} .")
    shape = parse_turtle(
        PREFIX
        + f""":S a sh:NodeShape; sh:targetClass :Equipment;
        sh:property :P . :P a sh:PropertyShape; sh:path :name; {constraint} .""",
        shapes=True,
    )
    result = check_shapes(data, shape)
    assert result == {
        "conforms": False,
        "violations": [
            {
                "focus": EX.x.n3(),
                "path": EX.name.n3(),
                "constraint": f"<http://www.w3.org/ns/shacl#{expected}>",
                "sourceShape": EX.P.n3(),
                "value": None
                if expected == "MaxCountConstraintComponent"
                else next(data.objects(EX.x, EX.name)).n3(),
                "severity": SH.Violation.n3(),
            }
        ],
    }


@pytest.mark.parametrize(
    "extra",
    [
        ":P sh:path [sh:inversePath :name] .",
        ':P sh:in _:a . _:a rdf:first "x"; rdf:rest _:a .',
        ':P sh:in _:a . _:a rdf:first "x", "y"; rdf:rest rdf:nil .',
        ":P sh:minCount -1 .",
        ":P sh:datatype <urn:unknown> .",
        ":Other sh:path :name .",
        ":S sh:property [ sh:path :name; sh:minCount 1 ] .",
    ],
)
def test_malformed_shapes_rejected(extra):
    base = (
        PREFIX
        + "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . "
        + (":S a sh:NodeShape; sh:targetClass :Equipment; sh:property :P . :P sh:path :name . ")
    )
    shapes = parse_turtle(base + extra, shapes=True)
    with pytest.raises(SemanticError):
        check_shapes(parse_turtle(fixture(1)), shapes)


def test_scope_excludes_schema_subclass_and_other_data():
    # Caller chooses an asserted-only scope; no schema or derived classes are injected.
    data = parse_turtle(PREFIX + ":pump a :CriticalPump . :equipment a :Equipment .")
    result = check_shapes(data, parse_turtle(SHAPES, shapes=True))
    assert [v["focus"] for v in result["violations"]] == [EX.equipment.n3()]


def test_blank_nodes_not_allowed_in_fact_or_ontology_graph():
    graph = Graph()
    graph.add((BNode(), EX.name, Literal("x")))
    with pytest.raises(SemanticError):
        reason(graph)


def test_typed_literal_preservation():
    graph = parse_turtle(PREFIX + ':a :p "中文"@zh; :n "001"; :i 1; :b true .')
    assert set(graph.objects(EX.a, EX.n)) == {Literal("001")}
    assert set(graph.objects(EX.a, EX.i)) == {Literal(1)}
    assert set(graph.objects(EX.a, EX.b)) == {Literal(True)}
    assert set(graph.objects(EX.a, EX.p)) == {Literal("中文", lang="zh")}
    assert Literal(1).datatype == XSD.integer


@pytest.mark.parametrize(
    "function", ["SAMPLE(?o)", "GROUP_CONCAT(?o)", "SUM(?o)", "AVG(?o)", "MIN(?o)", "MAX(?o)"]
)
def test_unstable_aggregates_are_explicitly_rejected(function):
    with pytest.raises(SemanticError, match="UNSUPPORTED_QUERY_FUNCTION"):
        query(Graph(), f"SELECT ({function} AS ?value) WHERE {{ ?s ?p ?o }}")


def test_count_is_a_deterministic_supported_aggregate():
    graph = parse_turtle('<urn:s> <urn:p> "a", "b" .')
    assert query(graph, "SELECT (COUNT(?o) AS ?n) WHERE { ?s ?p ?o }")["rows"] == [
        ['"2"^^<http://www.w3.org/2001/XMLSchema#integer>']
    ]


def test_limit_is_explicitly_unsupported_and_complete_results_stable():
    graph = parse_turtle('<urn:s> <urn:p> "b", "a" .')
    with pytest.raises(SemanticError, match="QUERY_SLICE_UNSUPPORTED"):
        query(graph, "SELECT ?o WHERE { ?s ?p ?o } LIMIT 1")
    with pytest.raises(SemanticError, match="QUERY_SLICE_UNSUPPORTED"):
        query(graph, "SELECT ?o WHERE { ?s ?p ?o } ORDER BY ?o LIMIT 1")
    assert query(graph, "SELECT ?o WHERE { ?s ?p ?o }")["rows"] == [['"a"'], ['"b"']]


def test_numeric_value_order_ties_have_canonical_datatype_order():
    graph = parse_turtle(PREFIX + ':s :p "1"^^xsd:integer, "1.0"^^xsd:decimal, "1.0"^^xsd:double .')
    rows = sorted([[v.n3()] for v in graph.objects(EX.s, EX.p)])
    assert query(graph, "SELECT ?o WHERE { ?s ?p ?o } ORDER BY ?o")["rows"] == rows
    assert query(graph, "SELECT ?o WHERE { ?s ?p ?o } ORDER BY DESC(?o)")["rows"] == rows


@pytest.mark.parametrize(
    "rule",
    [
        Rule("bad", ((123, EX.p, EX.y),), (EX.x, RDF.type, EX.C)),
        Rule("bad", ((EX.x, EX.p, EX.y),), (EX.x, RDF.type, None)),
    ],
)
def test_invalid_term_never_reaches_rdflib_assertion(rule):
    with pytest.raises(SemanticError, match="INVALID_RULE"):
        reason(Graph(), (rule,))


def test_unpaired_unicode_is_a_safe_input_error():
    with pytest.raises(SemanticError, match="INVALID_UNICODE"):
        query(Graph(), "\ud800")


def test_annotations_do_not_participate_in_reasoning():
    graph = parse_turtle("""@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        rdfs:label rdfs:domain <urn:D> . <urn:x> rdfs:label "hi" .""")
    s = Variable("s")
    rule = Rule("labels", ((s, RDFS.label, Literal("hi")),), (s, RDF.type, EX.D))
    result = reason(graph, (rule,))
    assert result["rdfs"] == []
    assert result["rules"] == []


@pytest.mark.parametrize(
    "rule",
    [
        Rule([], (), ()),
        Rule("invalid", None, ()),
        Rule("invalid", ((),), ()),
        Rule("schema", ((Variable("s"), EX.p, EX.y),), (EX.A, RDFS.subClassOf, EX.B)),
        Rule("predicate", ((Variable("s"), Variable("p"), EX.y),), (EX.A, Variable("p"), EX.B)),
    ],
)
def test_invalid_rule_is_rejected_even_with_empty_graph(rule):
    with pytest.raises(SemanticError):
        reason(Graph(), (rule,))


def test_query_execution_failure_has_safe_code():
    with pytest.raises(SemanticError, match="QUERY_FAILED"):
        query(Graph(), 'SELECT (REGEX("private-value", "(") AS ?x) WHERE {}')


@pytest.mark.parametrize(
    "value", ['"NaN"^^xsd:double', '"INF"^^xsd:double', '"private-invalid-int"^^xsd:integer']
)
def test_invalid_literals_fail_without_raw_diagnostics(value, capsys, caplog):
    with pytest.raises(SemanticError, match="UNSUPPORTED_LITERAL"):
        parse_turtle(PREFIX + f":s :p {value} .")
    assert capsys.readouterr().err == ""
    assert "private-invalid-int" not in caplog.text


def test_shacl_rejects_mixed_ontology_scope():
    data = parse_turtle(
        PREFIX
        + """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        :CriticalPump rdfs:subClassOf :Equipment . :pump a :CriticalPump ."""
    )
    with pytest.raises(SemanticError, match="ASSERTED_SCOPE_REQUIRED"):
        check_shapes(data, parse_turtle(SHAPES, shapes=True))


def test_shacl_identifies_same_path_same_component_constraints():
    data = parse_turtle(PREFIX + ':x a :Equipment; :name "a", "b", "c" .')
    shapes = parse_turtle(
        PREFIX
        + """
        :S a sh:NodeShape; sh:targetClass :Equipment; sh:property :P1, :P2 .
        :P1 sh:path :name; sh:maxCount 1 . :P2 sh:path :name; sh:maxCount 2 .""",
        shapes=True,
    )
    violations = check_shapes(data, shapes)["violations"]
    assert {v["sourceShape"] for v in violations} == {EX.P1.n3(), EX.P2.n3()}
    assert len(violations) == 2


def test_expansion_has_cumulative_work_limit(monkeypatch):
    from ontolearn_engine import semantic

    monkeypatch.setattr(semantic, "MAX_WORK", 2)
    graph = parse_turtle("""@prefix : <urn:t:> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        :A rdfs:subClassOf :B . :B rdfs:subClassOf :C . :x a :A . :y a :A .""")
    with pytest.raises(SemanticError, match="WORK_LIMIT"):
        reason(graph)
