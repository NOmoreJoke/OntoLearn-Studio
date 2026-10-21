"""RDF 1.1 string identity across the existing finite semantic boundaries.

Simple literal syntax and explicit xsd:string with the same lexical form denote
one RDF term. This does not merge different numeric lexical forms or languages.
The complete rule oracle preserves both emit traces despite result-set dedup.
"""

import json

import pytest
from ontolearn_engine.semantic import Rule, check_shapes, parse_turtle, query, reason
from ontolearn_engine.semantic_execution import _term
from ontolearn_engine.semantic_offline import SemanticError
from ontolearn_engine.semantic_query import prepare_lexical_query
from ontolearn_engine.semantic_scopes import prepare_validation_scope, project_validation_scope
from rdflib import RDF, SH, XSD, BNode, Graph, Literal, URIRef, Variable
from rdflib.collection import Collection
from rdflib.plugins.sparql import operators
from rdflib.plugins.sparql.parserutils import Expr

S, P, C, SHAPE, PROPERTY = map(URIRef, ("urn:s", "urn:p", "urn:C", "urn:Shape", "urn:Property"))
SUBJECTS = tuple(map(URIRef, ("urn:both", "urn:plain", "urn:typed")))
STRING = str(XSD.string)
LEXICALS = ("", "x", 'quote" slash\\', "line\nnext", "你好")
TRUE = '"true"^^<http://www.w3.org/2001/XMLSchema#boolean>'


def wire(value):
    return json.loads(json.dumps(value))


def triple(s, p, o):
    return [s.n3(), p.n3(), o.n3()]


def raw_data(form, lexical="x", *, typed=False):
    graph = Graph()
    if form in {"plain", "both"}:
        graph.add((S, P, Literal(lexical, normalize=False)))
    if form in {"typed", "both"}:
        graph.add((S, P, Literal(lexical, datatype=XSD.string, normalize=False)))
    if typed:
        graph.add((S, RDF.type, C))
    return graph


def shapes(*, allowed=None, count=None, datatype=None):
    graph = Graph()
    graph.add((SHAPE, RDF.type, SH.NodeShape))
    graph.add((SHAPE, SH.targetClass, C))
    graph.add((SHAPE, SH.property, PROPERTY))
    graph.add((PROPERTY, SH.path, P))
    if allowed is not None:
        head = BNode()
        Collection(graph, head, allowed)
        graph.add((PROPERTY, SH["in"], head))
    if count is not None:
        predicate, value = count
        graph.add((PROPERTY, predicate, Literal(value)))
    if datatype is not None:
        graph.add((PROPERTY, SH.datatype, datatype))
    return graph


def violation(component, value=None):
    return {
        "conforms": False,
        "violations": [
            {
                "focus": S.n3(),
                "path": P.n3(),
                "constraint": SH[component].n3(),
                "sourceShape": PROPERTY.n3(),
                "value": value,
                "severity": SH.Violation.n3(),
            }
        ],
    }


@pytest.mark.parametrize("lexical", LEXICALS)
def test_turtle_string_aliases_are_one_term_with_preserved_lexical_form(lexical):
    plain = Literal(lexical, normalize=False)
    explicit = Literal(lexical, datatype=XSD.string, normalize=False)
    text = f"<urn:s> <urn:p> {plain.n3()}, {explicit.n3()} ."
    actual = parse_turtle(text)
    assert set(actual) == {(S, P, plain)}
    assert actual.value(S, P).n3() == plain.n3()


@pytest.mark.parametrize("form", ("plain", "typed", "both"))
def test_raw_graph_query_frontdoor_uses_one_string_term_without_mutating_input(form):
    graph = raw_data(form)
    original = set(graph)
    assert query(graph, "SELECT DISTINCT ?v WHERE { <urn:s> <urn:p> ?v }") == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [['"x"']],
    }
    assert set(graph) == original


def rule_fixture():
    graph = Graph()
    for subject in SUBJECTS:
        graph.add((subject, P, Literal("x")))
    # Independent Graph construction bypasses the Turtle normalization under test.
    graph.add((SUBJECTS[0], P, Literal("x", datatype=XSD.string, normalize=False)))
    graph.remove((SUBJECTS[2], P, Literal("x")))
    graph.add((SUBJECTS[2], P, Literal("x", datatype=XSD.string, normalize=False)))
    u = Variable("s")
    plain, explicit = Literal("x"), Literal("x", datatype=XSD.string, normalize=False)
    rules = (
        Rule("01-match-plain", ((u, P, plain),), (u, URIRef("urn:plain-match"), URIRef("urn:yes"))),
        Rule(
            "02-match-typed", ((u, P, explicit),), (u, URIRef("urn:typed-match"), URIRef("urn:yes"))
        ),
        Rule("03-emit-plain", ((SUBJECTS[0], P, plain),), (SUBJECTS[0], URIRef("urn:emit"), plain)),
        Rule(
            "04-emit-typed",
            ((SUBJECTS[0], P, explicit),),
            (SUBJECTS[0], URIRef("urn:emit"), explicit),
        ),
    )
    records = []
    for identity, predicate in [
        ("01-match-plain", "urn:plain-match"),
        ("02-match-typed", "urn:typed-match"),
    ]:
        for subject in SUBJECTS:
            fact = triple(subject, P, plain)
            records.append(
                {
                    "rule": identity,
                    "result": triple(subject, URIRef(predicate), URIRef("urn:yes")),
                    "inputs": [fact],
                    "basis": [fact],
                }
            )
    fact = triple(SUBJECTS[0], P, plain)
    emitted = triple(SUBJECTS[0], URIRef("urn:emit"), plain)
    for identity in ("03-emit-plain", "04-emit-typed"):
        records.append({"rule": identity, "result": emitted, "inputs": [fact], "basis": [fact]})
    expected = {
        "rdfs": [],
        "rdfsEvidence": [],
        "warnings": [],
        "rules": sorted({tuple(record["result"]) for record in records}),
        "evidence": records,
    }
    return graph, rules, wire(expected)


def test_complete_rule_output_has_seven_terms_and_eight_distinct_match_traces():
    graph, rules, expected = rule_fixture()
    original = set(graph)
    constants = tuple((r.when, r.then) for r in rules)
    actual = wire(reason(graph, rules))
    assert actual == expected
    assert len(actual["rules"]) == 7 and len(actual["evidence"]) == 8
    assert set(graph) == original and tuple((r.when, r.then) for r in rules) == constants


@pytest.mark.parametrize("form", ("plain", "typed", "both"))
@pytest.mark.parametrize("token", ('"x"', f'"x"^^<{STRING}>'))
def test_bgp_and_values_constants_match_both_string_spellings(form, token):
    graph = raw_data(form)
    assert query(graph, f"ASK {{ <urn:s> <urn:p> {token} }}") == {"type": "ASK", "value": True}
    assert query(graph, f"SELECT ?s WHERE {{ VALUES ?v {{ {token} }} ?s <urn:p> ?v }}") == {
        "type": "SELECT",
        "variables": ["s"],
        "rows": [["<urn:s>"]],
    }
    assert query(
        graph, f"SELECT (sameTerm(?v, {token}) AS ?same) WHERE {{ <urn:s> <urn:p> ?v }}"
    ) == {
        "type": "SELECT",
        "variables": ["same"],
        "rows": [[TRUE]],
    }


def test_values_distinct_count_and_same_term_share_string_identity():
    graph = Graph()
    values = f'VALUES ?v {{ "x" "x"^^<{STRING}> }}'
    assert query(graph, f"SELECT DISTINCT ?v WHERE {{ {values} }}") == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [['"x"']],
    }
    assert query(graph, f"SELECT (COUNT(DISTINCT ?v) AS ?count) WHERE {{ {values} }}") == {
        "type": "SELECT",
        "variables": ["count"],
        "rows": [['"1"^^<http://www.w3.org/2001/XMLSchema#integer>']],
    }
    assert query(graph, f'ASK {{ FILTER(sameTerm("x", "x"^^<{STRING}>)) }}') == {
        "type": "ASK",
        "value": True,
    }


@pytest.mark.parametrize("form", ("plain", "typed", "both"))
@pytest.mark.parametrize("member_typed", (False, True))
def test_shacl_in_accepts_same_string_term_both_directions(form, member_typed):
    graph = raw_data(form, typed=True)
    allowed = Literal("x", datatype=XSD.string if member_typed else None, normalize=False)
    shape = shapes(allowed=[allowed])
    original, original_shapes = set(graph), set(shape)
    assert check_shapes(graph, shape) == {"conforms": True, "violations": []}
    assert set(graph) == original and set(shape) == original_shapes


def test_shacl_in_still_reports_complete_identity_for_different_string_lexical():
    graph = raw_data("typed", typed=True)
    assert check_shapes(graph, shapes(allowed=[Literal("other")])) == violation(
        "InConstraintComponent", '"x"'
    )


@pytest.mark.parametrize("form", ("plain", "typed", "both"))
def test_shacl_count_and_datatype_count_one_abstract_string_value(form):
    graph = raw_data(form, typed=True)
    assert check_shapes(graph, shapes(count=(SH.maxCount, 1))) == {
        "conforms": True,
        "violations": [],
    }
    assert check_shapes(graph, shapes(count=(SH.minCount, 2))) == violation(
        "MinCountConstraintComponent"
    )
    assert check_shapes(graph, shapes(datatype=XSD.string)) == {"conforms": True, "violations": []}


def test_selected_derived_string_aliases_keep_both_sources_but_one_value_node():
    graph = raw_data("plain", typed=True)
    fact = triple(S, P, Literal("x"))
    rules = tuple(
        Rule(identity, ((S, P, Literal("x")),), (S, P, output))
        for identity, output in [
            ("emit-plain", Literal("x")),
            ("emit-typed", Literal("x", datatype=XSD.string, normalize=False)),
        ]
    )
    original = set(graph)
    scope = prepare_validation_scope(graph, Graph(), include_derived=True, rules=rules)
    expected = {
        "rdfs": [],
        "rdfsEvidence": [],
        "rules": [fact],
        "warnings": ["RULE_CHAIN_UNSUPPORTED:emit-plain", "RULE_CHAIN_UNSUPPORTED:emit-typed"],
        "evidence": [
            {"rule": r.id, "result": fact, "inputs": [fact], "basis": [fact]} for r in rules
        ],
    }
    assert wire(scope.reasoning_result) == expected
    payload = wire(scope.reasoning_result)
    selected = project_validation_scope(
        graph,
        Graph(),
        include_derived=True,
        rules=rules,
        reasoning_result=payload,
        reasoning_source=scope.provenance["reasoningSource"],
    )
    assert selected.reasoning_result is payload and wire(payload) == expected
    assert set(selected.facts) == {(S, P, Literal("x")), (S, RDF.type, C)}
    entry = next(e for e in selected.provenance["selectedFacts"] if wire(e["triple"]) == fact)
    assert wire(entry["sources"]) == [{"kind": "asserted"}] + [
        {"kind": "rule", "rule": r.id, "inputs": [fact], "basis": [fact]} for r in rules
    ]
    assert check_shapes(selected.facts, shapes(count=(SH.maxCount, 1))) == {
        "conforms": True,
        "violations": [],
    }
    assert check_shapes(selected.facts, shapes(count=(SH.minCount, 2))) == violation(
        "MinCountConstraintComponent"
    )
    assert set(graph) == original


@pytest.mark.parametrize("lexical", LEXICALS)
def test_strict_term_decoder_accepts_explicit_string_then_uses_shared_identity(lexical):
    plain = Literal(lexical, normalize=False)
    assert _term(plain.n3()) == plain
    assert _term(Literal(lexical, datatype=XSD.string, normalize=False).n3()) == plain


@pytest.mark.parametrize(
    "text",
    [
        '"x" ',
        '"x"^^xsd:string',
        '"x"^^<http://www.w3.org/2001/XMLSchema#string> trailing',
        '"x" . <urn:injected> <urn:p> "y"',
        '"x" # trailing input',
        '<urn:x> . <urn:injected> <urn:p> "y"',
        '"\\u0078"',
    ],
)
def test_strict_term_decoder_does_not_admit_noncanonical_or_injected_terms(text):
    with pytest.raises(SemanticError) as error:
        _term(text)
    assert error.value.code == "RDF_TERM_INVALID"


def test_numeric_and_language_terms_are_not_collapsed_by_string_identity():
    graph = parse_turtle(
        '<urn:s> <urn:p> "01"^^<http://www.w3.org/2001/XMLSchema#integer>, '
        '"1"^^<http://www.w3.org/2001/XMLSchema#integer>, '
        f'"x", "x"^^<{STRING}>, "x"@en, "x"@EN, "x"@en-US .'
    )
    expected = {
        (S, P, Literal("01", datatype=XSD.integer, normalize=False)),
        (S, P, Literal("1", datatype=XSD.integer, normalize=False)),
        (S, P, Literal("x")),
        (S, P, Literal("x", lang="en")),
        (S, P, Literal("x", lang="en-US")),
    }
    assert set(graph) == expected
    assert query(graph, "SELECT DISTINCT ?v WHERE { <urn:s> <urn:p> ?v }") == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [[v.n3()] for v in sorted((t[2] for t in expected), key=lambda t: t.n3())],
    }
    assert query(graph, 'ASK { FILTER(sameTerm("x"@en, "x"@EN)) }') == {
        "type": "ASK",
        "value": True,
    }
    assert query(graph, 'ASK { FILTER(sameTerm("x"@en, "x")) }') == {"type": "ASK", "value": False}
    assert query(graph, 'ASK { FILTER(sameTerm("x"@en, "x"@en-US)) }') == {
        "type": "ASK",
        "value": False,
    }


CONSTRUCTIONS = [
    f'STRDT("x", <{STRING}>)',
    f'STR("x"^^<{STRING}>)',
    f'CONCAT("", "x"^^<{STRING}>)',
    f'SUBSTR(STRDT("xy", <{STRING}>), 1, 1)',
    f'REPLACE(STRDT("a", <{STRING}>), "a", "x")',
    f'LCASE(STRDT("X", <{STRING}>))',
]


@pytest.mark.parametrize("expression", CONSTRUCTIONS)
@pytest.mark.parametrize("form", ("plain", "typed"))
def test_runtime_string_constructions_join_and_compare_as_one_term(expression, form):
    graph = raw_data(form)
    original = set(graph)
    assert query(
        graph,
        'SELECT ?v (sameTerm(?v, "x") AS ?same) WHERE { '
        f"BIND({expression} AS ?v) <urn:s> <urn:p> ?v }}",
    ) == {
        "type": "SELECT",
        "variables": ["v", "same"],
        "rows": [['"x"', TRUE]],
    }
    assert set(graph) == original


@pytest.mark.parametrize("expression", CONSTRUCTIONS)
def test_runtime_string_constructor_union_distinct_uses_shared_identity(expression):
    assert query(
        Graph(),
        f"SELECT DISTINCT ?v WHERE {{ {{ BIND({expression} AS ?v) }} "
        'UNION { BIND("x" AS ?v) } }',
    ) == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [['"x"']],
    }


@pytest.mark.parametrize(
    "value",
    [
        Literal("01", datatype=XSD.integer, normalize=False),
        Literal("1", datatype=XSD.integer, normalize=False),
        Literal("x", lang="en"),
        Literal("x", lang="en-US"),
        Literal("2026-10-21", datatype=XSD.date, normalize=False),
    ],
)
def test_strict_term_decoder_retains_other_accepted_term_identities(value):
    decoded = _term(value.n3())
    assert decoded == value and decoded.n3() == value.n3()
    assert (str(decoded), decoded.datatype, decoded.language) == (
        str(value),
        value.datatype,
        value.language,
    )


def test_optional_without_filter_leaves_global_true_filter_callback_and_context_untouched():
    graph = Graph()
    graph.add((URIRef("urn:first"), P, URIRef("urn:object")))
    graph.add((URIRef("urn:first"), URIRef("urn:optional"), Literal("present")))
    graph.add((URIRef("urn:second"), P, URIRef("urn:object")))
    original = set(graph)
    singleton = operators.TrueFilter
    attributes = dict(vars(singleton))
    callback = singleton._evalfn
    text = (
        "SELECT ?s ?value WHERE { ?s <urn:p> <urn:object> OPTIONAL { ?s <urn:optional> ?value } }"
    )
    for _ in range(2):
        assert query(graph, text) == {
            "type": "SELECT",
            "variables": ["s", "value"],
            "rows": [["<urn:first>", '"present"'], ["<urn:second>", None]],
        }
        assert operators.TrueFilter is singleton and singleton._evalfn is callback
        # Distinguish absent ctx from ctx=None: even adding an attribute mutates
        # this RDFLib global and can expose it to another prepared query.
        assert vars(singleton).keys() == attributes.keys()
        assert all(vars(singleton)[key] is value for key, value in attributes.items())
    assert set(graph) == original


def expressions(value):
    if isinstance(value, Expr):
        yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from expressions(child)
    elif isinstance(value, list | tuple):
        for child in value:
            yield from expressions(child)


def test_two_prepared_queries_do_not_share_mutable_expressions_or_evaluation_context():
    text = (
        'SELECT (CONCAT("a", "b") AS ?joined) '
        '(COALESCE(?missing, "ok") AS ?fallback) WHERE { '
        "OPTIONAL { <urn:s> <urn:p> ?value } }"
    )
    first = prepare_lexical_query(text)
    second = prepare_lexical_query(text)
    first_expr = list(expressions(first.algebra))
    second_expr = list(expressions(second.algebra))
    assert first_expr and second_expr
    assert {id(expr) for expr in first_expr}.isdisjoint(id(expr) for expr in second_expr)
    assert all(expr is not operators.TrueFilter for expr in first_expr + second_expr)
    before_second = [(expr, dict(vars(expr))) for expr in second_expr]
    # Exercise the actual prepared-query API, including OPTIONAL's synthetic
    # always-true expression, rather than replacing any evaluator callback.
    actual = list(Graph().query(first, use_store_provided=False))
    assert [[term.n3() for term in row] for row in actual] == [['"ab"', '"ok"']]
    for expr, attributes in before_second:
        assert vars(expr).keys() == attributes.keys()
        assert all(vars(expr)[key] is value for key, value in attributes.items())
    assert [
        [term.n3() for term in row] for row in Graph().query(second, use_store_provided=False)
    ] == [['"ab"', '"ok"']]


def test_sparql_filter_expression_error_discards_binding_without_failing_query():
    assert query(Graph(), "SELECT ?s WHERE { VALUES ?s { <urn:s> } FILTER(1/0) }") == {
        "type": "SELECT",
        "variables": ["s"],
        "rows": [],
    }


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1/0", None),
        ('COALESCE(1/0, "ok")', '"ok"'),
        ("COALESCE(?missing, 1/0)", None),
        ('IF(true, "ok", 1/0)', '"ok"'),
        ('IF(false, 1/0, "ok")', '"ok"'),
        ('IF(true, 1/0, "ok")', None),
        ('IF(1/0, "a", "b")', None),
    ],
)
def test_sparql_bind_coalesce_and_if_preserve_expression_error_semantics(expression, expected):
    assert query(
        Graph(),
        f"SELECT ?s ?value WHERE {{ VALUES ?s {{ <urn:s> }} BIND({expression} AS ?value) }}",
    ) == {
        "type": "SELECT",
        "variables": ["s", "value"],
        "rows": [["<urn:s>", expected]],
    }
