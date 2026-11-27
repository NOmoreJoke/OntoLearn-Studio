"""Complete operator/domain classifications plus independent true/false signatures."""

import pytest
from ontolearn_engine.quality.rule_comparator import compare_values
from ontolearn_engine.quality.rule_profile import OPS, Budget, ProfileFailure, TermInput
from ontolearn_engine.quality.rule_terms import parse_value
from test_quality_profile_terms import fixture, value

MATRIX = fixture("comparison-matrix.json")
ATOMS = [
    ("integer", "1", None),
    ("string", "1", None),
    ("langString", "1", "en"),
    ("iri", "urn:1", None),
    ("boolean", "false", None),
    ("date", "2000-01-01Z", None),
    ("date", "2000-01-01", None),
    ("dateTime", "2000-01-01T00:00:00Z", None),
    ("dateTime", "2000-01-01T00:00:00", None),
]


def atom(i):
    kind, text, lang = ATOMS[i]
    return (
        parse_value(TermInput("iri", text), None, Budget())
        if kind == "iri"
        else value(kind, text, lang)
    )


@pytest.mark.parametrize("i,j,k", [(i, j, k) for i in range(9) for j in range(9) for k in range(6)])
def test_complete_nine_domain_six_operator_table(i, j, k):
    left, right = atom(i), atom(j)
    if MATRIX["cells"][i][j][k] == "E3":
        with pytest.raises(ProfileFailure, match="RULE_COMPARISON_TYPE_MISMATCH"):
            compare_values(left, OPS[k], right, Budget())
    else:
        assert (
            compare_values(left, OPS[k], right, Budget())
            == [True, False, False, True, False, True][k]
        )


@pytest.mark.parametrize(
    "left,right,n,k",
    [
        (a, b, n, k)
        for a in MATRIX["numeric_types"]
        for b in MATRIX["numeric_types"]
        for n in (1, 2, 3)
        for k in range(6)
    ],
)
def test_all_648_numeric_three_point_signatures(left, right, n, k):
    assert (
        compare_values(value(left, str(n)), OPS[k], value(right, "2"), Budget())
        == MATRIX["threshold_two_signatures"][n - 1][k]
    )


@pytest.mark.parametrize("original,replacement", [(a, b) for a in OPS for b in OPS if a != b])
def test_all_30_directed_operator_replacements_are_killed(original, replacement):
    # Execute the mutated operator dispatch, including NE->LT, on all three inputs.
    expected = [row[OPS.index(original)] for row in MATRIX["threshold_two_signatures"]]
    mutant = [
        compare_values(value("integer", str(n)), replacement, value("decimal", "2"), Budget())
        for n in (1, 2, 3)
    ]
    with pytest.raises(AssertionError):
        assert mutant == expected


@pytest.mark.parametrize("op", OPS)
def test_different_language_ne_does_not_turn_true(op):
    with pytest.raises(ProfileFailure, match="RULE_COMPARISON_TYPE_MISMATCH"):
        compare_values(
            value("langString", "x", "en"), op, value("langString", "x", "en-US"), Budget()
        )


def test_unicode_scalar_order_no_normalization():
    b = Budget()
    assert compare_values(value("string", "\U00010000"), "gt", value("string", "\ue000"), b)
    assert not compare_values(value("string", "e\u0301"), "eq", value("string", "\u00e9"), b)
    assert compare_values(value("string", ""), "lt", value("string", "a"), b)
