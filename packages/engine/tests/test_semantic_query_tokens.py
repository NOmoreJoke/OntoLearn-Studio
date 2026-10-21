"""Adjacent signed tokens differ from explicit unary computation in SPARQL."""

import pytest
from ontolearn_engine.semantic import query
from ontolearn_engine.semantic_offline import SemanticError
from rdflib import XSD, Graph

SIGNED = [
    ("+01", XSD.integer),
    ("-01", XSD.integer),
    ("+00", XSD.integer),
    ("-00", XSD.integer),
    ("+01.00", XSD.decimal),
    ("-01.00", XSD.decimal),
    ("+.00", XSD.decimal),
    ("-.00", XSD.decimal),
    ("+01e+00", XSD.double),
    ("-01E+00", XSD.double),
    ("+0E+00", XSD.double),
    ("-0e0", XSD.double),
]


@pytest.mark.parametrize("token,datatype", SIGNED)
@pytest.mark.parametrize("form", ["bind", "projection"])
def test_adjacent_signed_expression_is_an_exact_numeric_token(token, datatype, form):
    text = (
        f"SELECT ?v WHERE {{ BIND({token} AS ?v) }}"
        if form == "bind"
        else f"SELECT ({token} AS ?v) WHERE {{}}"
    )
    assert query(Graph(), text) == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [[f'"{token}"^^<{datatype}>']],
    }


@pytest.mark.parametrize("token,datatype", SIGNED)
def test_str_and_sameterm_expose_signed_token_identity(token, datatype):
    assert query(Graph(), f"SELECT (STR({token}) AS ?v) WHERE {{}}") == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [[f'"{token}"']],
    }
    assert query(Graph(), f'ASK {{ FILTER(sameTerm({token}, "{token}"^^<{datatype}>)) }}') == {
        "type": "ASK",
        "value": True,
    }


@pytest.mark.parametrize("sign,expected", [("+", "1"), ("-", "-1")])
@pytest.mark.parametrize("separator", [" ", "\n", "\t", "# comment\n"])
def test_separated_sign_is_a_unary_operation_and_is_invalid_as_graph_constant(
    sign, expected, separator
):
    expression = sign + separator + "01"
    assert query(Graph(), f"SELECT (STR({expression}) AS ?v) WHERE {{}}") == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [[f'"{expected}"']],
    }
    with pytest.raises(SemanticError) as error:
        query(Graph(), f"ASK {{ <urn:s> <urn:p> {expression} }}")
    assert error.value.code == "INVALID_QUERY"


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("-(01)", "-1"),
        ("+(01)", "1"),
        ("01-01", "0"),
        ("01+-01", "0"),
        ("01--01", "2"),
        ("01*-01", "-1"),
        ("ABS(-01)", "1"),
        ("IF(true, +01, -01)", "+01"),
    ],
)
def test_explicit_unary_arithmetic_and_nested_signed_tokens(expression, expected):
    assert query(Graph(), f"SELECT (STR({expression}) AS ?v) WHERE {{}}") == {
        "type": "SELECT",
        "variables": ["v"],
        "rows": [[f'"{expected}"']],
    }
