"""Independent IEEE bit-field/rational oracles, including double rounding."""

from fractions import Fraction

import pytest
from ontolearn_engine.quality.rule_comparator import compare_values
from ontolearn_engine.quality.rule_profile import Budget, ProfileFailure
from test_quality_profile_terms import fixture, value


def bit_fraction(bits, width):
    raw = int(bits, 16)
    precision, exponent_bits, bias = (24, 8, 127) if width == 32 else (53, 11, 1023)
    sign = -1 if raw >> (width - 1) else 1
    exponent = (raw >> (precision - 1)) & ((1 << exponent_bits) - 1)
    fraction = raw & ((1 << (precision - 1)) - 1)
    significand = fraction if exponent == 0 else fraction + (1 << (precision - 1))
    shift = (1 - bias if exponent == 0 else exponent - bias) - (precision - 1)
    return sign * significand * (Fraction(2) ** shift), bool(sign < 0 and significand == 0)


@pytest.mark.parametrize("case", fixture("numeric-oracles.json")["valid"])
def test_exact_numeric_oracles(case):
    number = value(case["type"], case["lexical"]).value
    if "ieee" in case:
        expected, negative_zero = bit_fraction(case["ieee"], 32 if case["type"] == "float" else 64)
    else:
        expected = Fraction(int(case["numerator"]), int(case["denominator"]))
        negative_zero = False
    assert Fraction(number.numerator, number.denominator) == expected
    assert number.negative_zero == negative_zero


@pytest.mark.parametrize("case", fixture("numeric-oracles.json")["nonfinite"])
def test_nonfinite_distinct_from_invalid_and_underflow(case):
    with pytest.raises(ProfileFailure, match="UNSUPPORTED_NONFINITE_LITERAL"):
        value(case["type"], case["lexical"])


def test_no_lossy_mixed_numeric_promotion():
    b = Budget()
    a, d, f = (value(t, "0.1") for t in ("decimal", "double", "float"))
    assert compare_values(a, "lt", d, b)
    assert compare_values(d, "lt", f, b)
    assert not compare_values(
        value("integer", "9007199254740993"), "eq", value("double", "9007199254740993"), b
    )
    assert compare_values(value("float", "-0"), "eq", value("decimal", "0"), b)


def test_4096_digits_do_not_change_global_int_policy():
    import sys

    before = sys.get_int_max_str_digits()
    number = value("integer", "1" * 4096).value
    assert number.numerator % 1000000000 == 111111111
    assert sys.get_int_max_str_digits() == before
