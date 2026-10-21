"""Acceptance regressions for RDF term identity at public semantic boundaries.

These tests deliberately preserve noncanonical lexical forms in independently
constructed data. Parsing both sides with the same broken normalizer must not
make an incorrect sh:in result or SPARQL match look correct.
"""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
import rdflib
from ontolearn_engine.semantic import Rule, check_shapes, parse_turtle, query, reason
from ontolearn_engine.semantic_offline import SemanticError
from pyparsing import ParserElement
from rdflib import RDF, SH, XSD, Graph, Literal, URIRef, Variable
from rdflib.collection import Collection
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.plugins.sparql import parser as sparql_parser
from rdflib.term import _toPythonMapping

S, P, Q, C = map(URIRef, ("urn:s", "urn:p", "urn:q", "urn:C"))


def typed(lexical, datatype):
    return f'"{lexical}"^^<{datatype}>'


NUMBERS = [
    ("01", "01", XSD.integer),
    ("+01", "+01", XSD.integer),
    ("-0", "-0", XSD.integer),
    ("000", "000", XSD.integer),
    ("1.00", "1.00", XSD.decimal),
    ("+01.00", "+01.00", XSD.decimal),
    ("-0.00", "-0.00", XSD.decimal),
    (".50", ".50", XSD.decimal),
    ("-.00", "-.00", XSD.decimal),
    ("1e0", "1e0", XSD.double),
    ("+01E+00", "+01E+00", XSD.double),
    ("-0.0e0", "-0.0e0", XSD.double),
    (typed("01", XSD.integer), "01", XSD.integer),
    (typed("+01", XSD.int), "+01", XSD.int),
    (typed("-0", XSD.integer), "-0", XSD.integer),
    (typed("1.00", XSD.decimal), "1.00", XSD.decimal),
    (typed("-0.00", XSD.decimal), "-0.00", XSD.decimal),
    (typed("1e0", XSD.double), "1e0", XSD.double),
    (typed("+01E+00", XSD.double), "+01E+00", XSD.double),
    (typed("-0.0E0", XSD.double), "-0.0E0", XSD.double),
    (typed("01.0", XSD.float), "01.0", XSD.float),
]


@pytest.mark.parametrize("token,lexical,datatype", NUMBERS)
def test_turtle_preserves_numeric_term_lexical_form(token, lexical, datatype):
    graph = parse_turtle(f"<urn:s> <urn:p> {token} .")
    assert len(graph) == 1
    value = graph.value(S, P)
    assert type(value) is Literal
    assert str(value) == lexical and value.datatype == datatype
    assert value.n3() == typed(lexical, datatype)


@pytest.mark.parametrize(
    "token,lexical,datatype,language",
    [
        ("true", "true", XSD.boolean, None),
        ("false", "false", XSD.boolean, None),
        (typed("1", XSD.boolean), "1", XSD.boolean, None),
        (typed("0", XSD.boolean), "0", XSD.boolean, None),
        (typed("2026-10-21", XSD.date), "2026-10-21", XSD.date, None),
        (typed("2026-10-21T12:00:00Z", XSD.dateTime), "2026-10-21T12:00:00Z", XSD.dateTime, None),
        (typed("你好", XSD.string), "你好", XSD.string, None),
        ('"你好"@zh-CN', "你好", None, "zh-CN"),
        ('"ordinary"', "ordinary", None, None),
    ],
)
def test_turtle_keeps_other_whitelisted_terms(token, lexical, datatype, language):
    value = parse_turtle(f"<urn:s> <urn:p> {token} .").value(S, P)
    assert str(value) == lexical
    assert value.datatype == datatype and value.language == language
    if datatype == XSD.boolean:
        assert type(value.toPython()) is bool


@pytest.mark.parametrize(
    "token,code",
    [
        ("1e999", "UNSUPPORTED_NONFINITE_LITERAL"),
        (typed("NaN", XSD.double), "UNSUPPORTED_NONFINITE_LITERAL"),
        (typed("not-an-integer", XSD.integer), "INVALID_LITERAL_LEXICAL"),
    ],
)
def test_preserving_lexical_forms_keeps_invalid_and_nonfinite_literal_guards(token, code):
    with pytest.raises(SemanticError) as error:
        parse_turtle(f"<urn:s> <urn:p> {token} .")
    assert error.value.code == code


def data_graph(lexical, datatype):
    graph = Graph()
    graph.add((S, RDF.type, C))
    graph.add((S, P, Literal(lexical, datatype=datatype, normalize=False)))
    return graph


def shapes_for(token):
    return parse_turtle(
        "@prefix sh: <http://www.w3.org/ns/shacl#> . "
        "<urn:Shape> a sh:NodeShape; sh:targetClass <urn:C>; sh:property <urn:Property> . "
        f"<urn:Property> sh:path <urn:p>; sh:in ({token}) .",
        shapes=True,
    )


NUMERIC_PAIRS = [
    (XSD.integer, "01", "1"),
    (XSD.integer, "-0", "0"),
    (XSD.decimal, "1.00", "1.0"),
    (XSD.decimal, "-0.00", "0.00"),
    (XSD.double, "1e0", "1.0E0"),
    (XSD.double, "-0.0E0", "0.0E0"),
]
TERM_PAIRS = [*NUMERIC_PAIRS, (XSD.boolean, "1", "true")]


@pytest.mark.parametrize("datatype,left,right", TERM_PAIRS)
@pytest.mark.parametrize("shape_side,data_side", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_shacl_in_uses_exact_term_identity_in_both_directions(
    datatype, left, right, shape_side, data_side
):
    lexical = (left, right)
    data_lexical = lexical[data_side]
    actual = check_shapes(
        data_graph(data_lexical, datatype), shapes_for(typed(lexical[shape_side], datatype))
    )
    violations = []
    if shape_side != data_side:
        violations = [
            {
                "focus": "<urn:s>",
                "path": "<urn:p>",
                "constraint": SH.InConstraintComponent.n3(),
                "sourceShape": "<urn:Property>",
                "value": typed(data_lexical, datatype),
                "severity": SH.Violation.n3(),
            }
        ]
    assert actual == {"conforms": shape_side == data_side, "violations": violations}


@pytest.mark.parametrize("datatype,lexical,other", NUMERIC_PAIRS)
def test_shacl_bare_numeric_in_does_not_normalize_allowed_value(datatype, lexical, other):
    for data_lexical in (lexical, other):
        actual = check_shapes(data_graph(data_lexical, datatype), shapes_for(lexical))
        assert actual == {
            "conforms": data_lexical == lexical,
            "violations": []
            if data_lexical == lexical
            else [
                {
                    "focus": "<urn:s>",
                    "path": "<urn:p>",
                    "constraint": SH.InConstraintComponent.n3(),
                    "sourceShape": "<urn:Property>",
                    "value": typed(data_lexical, datatype),
                    "severity": SH.Violation.n3(),
                }
            ],
        }


@pytest.mark.parametrize(
    "datatype,lexical,bound", [(XSD.integer, "01", "1"), (XSD.decimal, "1.00", "1.0")]
)
def test_shacl_numeric_bounds_still_compare_values(datatype, lexical, bound):
    shapes = parse_turtle(
        "@prefix sh: <http://www.w3.org/ns/shacl#> . "
        "<urn:Shape> a sh:NodeShape; sh:targetClass <urn:C>; sh:property <urn:Property> . "
        f"<urn:Property> sh:path <urn:p>; sh:minInclusive {typed(bound, datatype)}; "
        f"sh:maxInclusive {typed(bound, datatype)} .",
        shapes=True,
    )
    assert check_shapes(data_graph(lexical, datatype), shapes) == {
        "conforms": True,
        "violations": [],
    }


def test_turtle_comments_crlf_nested_lists_and_namespace_bindings():
    graph = parse_turtle(
        "@prefix ex: <urn:example:> .\r\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\r\n"
        "ex:s ex:p ( # first lexical integer\r\n"
        " +01 (1.00 1e0 true) [ex:q -0]) .\r\n",
        shapes=True,
    )
    outer = list(Collection(graph, graph.value(URIRef("urn:example:s"), URIRef("urn:example:p"))))
    assert outer[0].n3() == typed("+01", XSD.integer)
    assert [x.n3() for x in Collection(graph, outer[1])] == [
        typed("1.00", XSD.decimal),
        typed("1e0", XSD.double),
        typed("true", XSD.boolean),
    ]
    assert graph.value(outer[2], URIRef("urn:example:q")).n3() == typed("-0", XSD.integer)
    assert dict(graph.namespaces())["ex"] == URIRef("urn:example:")
    assert dict(graph.namespaces())["xsd"] == URIRef(str(XSD))


@pytest.mark.parametrize(
    "suffix",
    [
        "<urn:t> <urn:q> ! .",
        '<urn:t> <urn:q> "x"^^missing:datatype .',
        "<urn:t> <urn:q> (01 .",
    ],
)
def test_turtle_invalid_syntax_preserves_parser_position_after_numeric_comments(suffix):
    text = "<urn:s> <urn:p>\r\n# numeric comment\r\n01 .\r\n" + suffix
    with pytest.raises(BadSyntax) as reference:
        Graph().parse(data=text, format="turtle", publicID="urn:ontolearn:i05:")
    with pytest.raises(SemanticError) as actual:
        parse_turtle(text, shapes=True)
    assert actual.value.code == "INVALID_TURTLE" and str(actual.value) == "INVALID_TURTLE"
    cause = actual.value.__cause__
    while cause is not None and not isinstance(cause, BadSyntax):
        cause = cause.__cause__
    assert isinstance(cause, BadSyntax)
    assert (cause.lines, cause._i, cause._why) == (
        reference.value.lines,
        reference.value._i,
        reference.value._why,
    )


@pytest.mark.parametrize(
    "object_text,code",
    [
        ('"x"^^missing:datatype', "INVALID_TURTLE"),
        ('"x"^^{<urn:a> <urn:b> <urn:c>}', "INVALID_TURTLE"),
        ('"x"^^[<urn:a> <urn:b>]', "INVALID_TURTLE"),
        ("{<urn:a> <urn:b> <urn:c>}", "INVALID_TURTLE"),
        ("1e+", "INVALID_TURTLE"),
        ("01suffix", "INVALID_TURTLE"),
        # The pinned parser silently drops the orphaned .3 token in both C1
        # and the lexical-only adapter. Keep the invalid-syntax regression red
        # until the public text boundary rejects this existing library gap.
        ("1.2.3", "INVALID_TURTLE"),
    ],
)
def test_turtle_lexical_fix_does_not_accept_n3_datatypes_or_invalid_numbers(object_text, code):
    with pytest.raises(SemanticError) as error:
        parse_turtle(f"<urn:s> <urn:p> {object_text} .")
    assert error.value.code == code


def test_same_valued_turtle_terms_do_not_collapse_and_reason_keeps_lexical_evidence():
    graph = parse_turtle("<urn:s> <urn:p> 01, 1, +01, 1.00, 1.0, 1e0, 1.0E0 .")
    expected = {
        typed("01", XSD.integer),
        typed("1", XSD.integer),
        typed("+01", XSD.integer),
        typed("1.00", XSD.decimal),
        typed("1.0", XSD.decimal),
        typed("1e0", XSD.double),
        typed("1.0E0", XSD.double),
    }
    assert {o.n3() for o in graph.objects(S, P)} == expected
    assert len(graph) == 7
    rule = Rule(
        "lexical-copy", ((Variable("s"), P, Variable("v")),), (Variable("s"), Q, Variable("v"))
    )
    result = reason(graph, (rule,))
    assert {tuple(t) for t in result["rules"]} == {
        ("<urn:s>", "<urn:q>", value) for value in expected
    }
    assert {tuple(record["inputs"][0]) for record in result["evidence"]} == {
        ("<urn:s>", "<urn:p>", value) for value in expected
    }


QUERY_TERMS = [
    (XSD.integer, "01", "1"),
    (XSD.decimal, "1.00", "1.0"),
    (XSD.double, "1e0", "1.0E0"),
]


@pytest.mark.parametrize("datatype,left,right", QUERY_TERMS)
@pytest.mark.parametrize("query_side,data_side", [(0, 0), (0, 1), (1, 0), (1, 1)])
@pytest.mark.parametrize("quoted", [False, True])
@pytest.mark.parametrize("form", ["bgp", "values"])
def test_sparql_bgp_and_values_join_keep_exact_terms_in_both_directions(
    datatype, left, right, query_side, data_side, quoted, form
):
    lexical = (left, right)
    token = typed(lexical[query_side], datatype) if quoted else lexical[query_side]
    graph = data_graph(lexical[data_side], datatype)
    expected = {"type": "ASK", "value": query_side == data_side}
    text = (
        f"ASK {{ <urn:s> <urn:p> {token} }}"
        if form == "bgp"
        else f"ASK {{ VALUES ?o {{ {token} }} <urn:s> <urn:p> ?o }}"
    )
    assert query(graph, text) == expected


@pytest.mark.parametrize("datatype,left,right", QUERY_TERMS)
@pytest.mark.parametrize("quoted", [False, True])
def test_sparql_values_result_and_distinct_keep_same_valued_terms(datatype, left, right, quoted):
    tokens = [typed(x, datatype) if quoted else x for x in (left, right)]
    expected = sorted([[typed(left, datatype)], [typed(right, datatype)]])
    assert query(
        Graph(), "SELECT DISTINCT ?o WHERE { VALUES ?o { " + " ".join(tokens) + " } }"
    ) == {"type": "SELECT", "variables": ["o"], "rows": expected}


@pytest.mark.parametrize("datatype,left,right", QUERY_TERMS)
def test_sparql_numeric_filter_compares_values_while_sameterm_compares_terms(datatype, left, right):
    graph = data_graph(left, datatype)
    assert query(graph, f"ASK {{ <urn:s> <urn:p> ?o FILTER(?o = {typed(right, datatype)}) }}") == {
        "type": "ASK",
        "value": True,
    }
    assert query(
        graph, f"ASK {{ <urn:s> <urn:p> ?o FILTER(sameTerm(?o, {typed(right, datatype)})) }}"
    ) == {"type": "ASK", "value": False}


@pytest.mark.parametrize(
    "text,variable,expected",
    [
        ("SELECT ((+01 + 02) AS ?n) WHERE {}", "n", typed("3", XSD.integer)),
        ("SELECT (ABS(-02) AS ?n) WHERE {}", "n", typed("2", XSD.integer)),
        ("SELECT (STR(01) AS ?s) WHERE {}", "s", '"01"'),
        ("SELECT (DATATYPE(01) AS ?type) WHERE {}", "type", XSD.integer.n3()),
        ('SELECT (IF(true, "yes", "no") AS ?s) WHERE {}', "s", '"yes"'),
        ('SELECT (CONCAT("a", "b") AS ?s) WHERE {}', "s", '"ab"'),
        (
            "SELECT (COUNT(?x) AS ?n) WHERE { VALUES ?x { +01 02 } FILTER(?x > 0) }",
            "n",
            typed("2", XSD.integer),
        ),
    ],
)
def test_sparql_ordinary_arithmetic_filter_and_functions_still_work(text, variable, expected):
    assert query(Graph(), text) == {"type": "SELECT", "variables": [variable], "rows": [[expected]]}


def grammar_state():
    roots = [v for v in vars(sparql_parser).values() if isinstance(v, ParserElement)]
    pending, visited = list(roots), {}
    while pending:
        parser = pending.pop()
        if id(parser) in visited:
            continue
        visited[id(parser)] = (
            tuple(map(id, parser.parseAction)),
            frozenset(parser.whiteChars),
            parser.skipWhitespace,
            parser.keepTabs,
            parser.callPreparse,
            tuple(map(id, parser.ignoreExprs)),
        )
        pending.extend(parser.recurse())
    return visited, (
        ParserElement.DEFAULT_WHITE_CHARS,
        ParserElement._packratEnabled,
        ParserElement._left_recursion_enabled,
    )


def test_lexical_operations_do_not_mutate_global_conversion_or_sparql_grammar():
    # Warm only the unrelated global parser; lazy parser caches are not the subject.
    assert str(next(iter(Graph().query("SELECT ?x WHERE { VALUES ?x { 01 } }")))[0]) == "1"
    before = grammar_state(), rdflib.NORMALIZE_LITERALS, dict(_toPythonMapping)
    try:
        parsed = parse_turtle('<urn:s> <urn:p> "01"^^<http://www.w3.org/2001/XMLSchema#integer> .')
        actual = query(Graph(), "SELECT ?x WHERE { VALUES ?x { 01 } }")
        report = check_shapes(data_graph("01", XSD.integer), shapes_for(typed("01", XSD.integer)))
    finally:
        assert (grammar_state(), rdflib.NORMALIZE_LITERALS, dict(_toPythonMapping)) == before
    assert str(parsed.value(S, P)) == "01"
    assert actual == {"type": "SELECT", "variables": ["x"], "rows": [[typed("01", XSD.integer)]]}
    assert report == {"conforms": True, "violations": []}


def test_lexical_query_and_unrelated_global_parser_are_isolated_across_threads():
    barrier = Barrier(2, timeout=10)

    def unrelated():
        values = []
        for _ in range(8):
            barrier.wait()
            values.append(str(next(iter(Graph().query("SELECT ?x WHERE { VALUES ?x { 01 } }")))[0]))
        return values

    def bounded():
        values = []
        for _ in range(8):
            barrier.wait()
            values.append(query(Graph(), "SELECT ?x WHERE { VALUES ?x { 01 } }"))
        return values

    before = grammar_state(), rdflib.NORMALIZE_LITERALS, dict(_toPythonMapping)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            other = pool.submit(unrelated)
            local = pool.submit(bounded)
            other_values, local_values = other.result(timeout=30), local.result(timeout=30)
    finally:
        assert (grammar_state(), rdflib.NORMALIZE_LITERALS, dict(_toPythonMapping)) == before
    assert other_values == ["1"] * 8
    assert (
        local_values
        == [{"type": "SELECT", "variables": ["x"], "rows": [[typed("01", XSD.integer)]]}] * 8
    )
