"""Exact bounded rational arithmetic and direct IEEE binary rounding."""

import re
from dataclasses import dataclass

from .rule_profile import NUMERIC, XSD, check_location, fail, internal, require_budget

INTEGER = re.compile(r"[+-]?[0-9]+", re.ASCII)
DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", re.ASCII)
FLOAT = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", re.ASCII)


@dataclass(frozen=True, slots=True)
class Number:
    numerator: int
    denominator: int = 1
    negative_zero: bool = False


def check_ints(budget, *values):
    require_budget(budget)
    for value in values:
        if type(value) is not int:
            internal()
        budget.bits(value, temporary=True)


def check_number(value, budget):
    if type(value) is not Number:
        internal()
    check_ints(budget, value.numerator, value.denominator)
    if type(value.negative_zero) is not bool or value.denominator <= 0:
        internal()
    budget.bits(value.numerator)
    budget.bits(value.denominator)


def limbs(n):
    if type(n) is not int:
        internal()
    return max(1, (n.bit_length() + 31) // 32)


def mul(a, b, budget):
    check_ints(budget, a, b)
    budget.bound(a.bit_length() + b.bit_length(), "temporary_bits")
    budget.debit(limbs(a) * limbs(b))
    return a * b


def shift(a, n, budget):
    check_ints(budget, a, n)
    if n < 0:
        internal()
    budget.bound(a.bit_length() + n, "temporary_bits")
    budget.debit(max(1, (a.bit_length() + n + 31) // 32))
    return a << n


def add(a, b, budget):
    check_ints(budget, a, b)
    budget.bound(max(a.bit_length(), b.bit_length()) + 1, "temporary_bits")
    budget.debit(limbs(a) + limbs(b))
    return a + b


def divide(a, b, budget):
    check_ints(budget, a, b)
    if b <= 0:
        internal()
    budget.debit(limbs(a) * limbs(b))
    return divmod(a, b)


def rational(n, d, budget, negative_zero=False):
    check_ints(budget, n, d)
    if type(negative_zero) is not bool:
        internal()
    if d <= 0:
        fail("INTERNAL_ERROR", classification="internal")
    a, b = abs(n), d
    while b:
        _, r = divide(a, b, budget)
        a, b = b, r
    qn, _ = divide(n, a, budget)
    qd, _ = divide(d, a, budget)
    budget.bits(qn)
    budget.bits(qd)
    return Number(qn, qd, negative_zero and n == 0)


def digits(text, budget, location=None):
    require_budget(budget)
    check_location(location, budget)
    if type(text) is not str:
        internal(location)
    budget.bound(len(text), "digits", location)
    budget.debit(4 * len(text), location=location)
    if text and (not text.isascii() or not text.isdigit()):
        internal(location)
    n = 0
    for start in range(0, len(text), 9):
        piece = text[start : start + 9]
        n = add(mul(n, 10 ** len(piece), budget), int(piece), budget)
    budget.bits(n, location=location)
    return n


def power10(n, budget):
    check_ints(budget, n)
    if n < 0:
        internal()
    # 3322/1000 is a strict upper bound on log2(10).
    budget.bound((n * 3322 + 999) // 1000 + 1, "temporary_bits")
    result, base = 1, 10
    while n:
        budget.debit()
        if n & 1:
            result = mul(result, base, budget)
        n >>= 1
        if n:
            base = mul(base, base, budget)
    return result


def compare_numbers(a, b, budget):
    check_number(a, budget)
    check_number(b, budget)
    left = mul(a.numerator, b.denominator, budget)
    right = mul(b.numerator, a.denominator, budget)
    budget.debit(limbs(left) + limbs(right))
    return (left > right) - (left < right)


def _quantize(n, d, negative, width, budget):
    precision, emin, emax = (24, -126, 127) if width == 32 else (53, -1022, 1023)
    if not n:
        return Number(0, 1, negative)
    e = n.bit_length() - d.bit_length()
    if (n < shift(d, e, budget)) if e >= 0 else (shift(n, -e, budget) < d):
        e -= 1
    k = max(e, emin) - precision + 1
    sn, sd = (n, shift(d, k, budget)) if k >= 0 else (shift(n, -k, budget), d)
    q, r = divide(sn, sd, budget)
    twice = shift(r, 1, budget)
    budget.debit(limbs(sd) + limbs(twice))
    if twice > sd or (twice == sd and q & 1):
        q = add(q, 1, budget)
    if q and q.bit_length() - 1 + k > emax:
        fail("UNSUPPORTED_NONFINITE_LITERAL")
    num, den = (shift(q, k, budget), 1) if k >= 0 else (q, shift(1, -k, budget))
    return rational(-num if negative else num, den, budget, negative)


def parse_number(text, datatype, budget, location=None):
    require_budget(budget)
    check_location(location, budget)
    if type(text) is not str or type(datatype) is not str:
        internal(location)
    if datatype not in NUMERIC:
        fail("UNSUPPORTED_LITERAL_DATATYPE", location)
    # Conservative precharge for regex, sign/parts copies and zero/exponent scans.
    budget.debit(12 * len(text), location=location)
    name = datatype.removeprefix(XSD)
    if name in ("integer", "int", "nonNegativeInteger"):
        if not INTEGER.fullmatch(text):
            fail("INVALID_LITERAL_LEXICAL", location)
        n = digits(text.lstrip("+-"), budget, location)
        if text.startswith("-"):
            n = -n
        if (name == "int" and not -2147483648 <= n <= 2147483647) or (
            name == "nonNegativeInteger" and n < 0
        ):
            fail("INVALID_LITERAL_LEXICAL", location)
        return Number(n)
    if name in ("float", "double") and text in ("INF", "+INF", "-INF", "NaN"):
        fail("UNSUPPORTED_NONFINITE_LITERAL", location)
    if not (DECIMAL if name == "decimal" else FLOAT).fullmatch(text):
        fail("INVALID_LITERAL_LEXICAL", location)
    raw = text.lstrip("+-")
    negative = text.startswith("-")
    parts = re.split("[eE]", raw)
    mantissa = parts[0]
    integral, _, fraction = mantissa.partition(".")
    coefficient_text = integral + fraction
    budget.bound(len(coefficient_text), "digits", location)
    exponent_text = parts[1] if len(parts) == 2 else "0"
    exp_digits = exponent_text.lstrip("+-")
    budget.bound(len(exp_digits), "digits", location)
    budget.debit(len(exp_digits), location=location)
    trimmed = exp_digits.lstrip("0") or "0"
    exponent = (1000000 if len(trimmed) > 6 else int(trimmed)) * (
        -1 if exponent_text.startswith("-") else 1
    )
    coefficient = digits(coefficient_text, budget, location)
    if name in ("float", "double"):
        if not coefficient:
            return Number(0, 1, negative)
        order = len(coefficient_text.lstrip("0")) - 1 + exponent - len(fraction)
        upper, lower = (50, -61) if name == "float" else (400, -401)
        if order >= upper:
            fail("UNSUPPORTED_NONFINITE_LITERAL", location)
        if order <= lower:
            return Number(0, 1, negative)
    power = exponent - len(fraction)
    n, d = (
        (mul(coefficient, power10(power, budget), budget), 1)
        if power >= 0
        else (coefficient, power10(-power, budget))
    )
    if name == "decimal":
        return rational(-n if negative else n, d, budget)
    try:
        return _quantize(n, d, negative, 32 if name == "float" else 64, budget)
    except Exception as exc:
        from .rule_profile import ProfileFailure

        if isinstance(exc, ProfileFailure) and exc.location is None:
            fail(exc.reason, location, exc.classification)
        raise
