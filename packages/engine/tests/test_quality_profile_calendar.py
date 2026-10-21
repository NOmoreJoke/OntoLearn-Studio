"""Exact day/second witnesses, astronomical year and timezone domain guards."""

from fractions import Fraction

import pytest
from ontolearn_engine.quality.rule_comparator import compare_values
from ontolearn_engine.quality.rule_profile import OPS, Budget, ProfileFailure
from test_quality_profile_terms import fixture, value


@pytest.mark.parametrize("case", fixture("calendar-oracles.json")["cases"])
def test_calendar_oracles(case):
    actual = value(case["type"], case["lexical"]).value
    assert actual.day == case["day"]
    assert Fraction(actual.second.numerator, actual.second.denominator) == Fraction(*case["second"])


@pytest.mark.parametrize("year", ["0000", "-0000", "-0400", "2000", "12000"])
def test_leap_years_and_unbounded_calendar(year):
    assert compare_values(
        value("date", year + "-02-29"), "lt", value("date", year + "-03-01"), Budget()
    )


@pytest.mark.parametrize("year", ["-0100", "1900", "2100", "-0001"])
def test_nonleap_centuries_and_negative_year(year):
    with pytest.raises(ProfileFailure, match="INVALID_LITERAL_LEXICAL"):
        value("date", year + "-02-29")


@pytest.mark.parametrize("op", OPS)
@pytest.mark.parametrize(
    "left,right",
    [
        (("date", "2000-01-01"), ("date", "2000-01-01Z")),
        (("date", "2000-01-01Z"), ("dateTime", "2000-01-01T00:00:00Z")),
    ],
)
def test_cross_calendar_domains_always_fail(op, left, right):
    with pytest.raises(ProfileFailure, match="RULE_COMPARISON_TYPE_MISMATCH"):
        compare_values(value(*left), op, value(*right), Budget())


def test_full_fraction_and_offset_normalization():
    b = Budget()
    assert compare_values(
        value("dateTime", "2000-01-01T00:00:00.0000000000000000001Z"),
        "gt",
        value("dateTime", "2000-01-01T00:00:00Z"),
        b,
    )
    assert compare_values(
        value("dateTime", "2000-01-01T01:00:00+01:00"),
        "eq",
        value("dateTime", "2000-01-01T00:00:00-00:00"),
        b,
    )
    assert compare_values(value("date", "-0000-01-01"), "eq", value("date", "0000-01-01"), b)
    assert compare_values(value("date", "-0001-12-31"), "lt", value("date", "0000-01-01"), b)
