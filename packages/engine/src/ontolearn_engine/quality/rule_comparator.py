"""Approved nine-domain / six-numeric comparator, independent of FILTER."""

from .rule_calendar import compare_calendar
from .rule_numbers import compare_numbers
from .rule_profile import (
    OPS,
    ProfileFailure,
    check_location,
    fail,
    internal,
    require_budget,
    text_compare,
)
from .rule_terms import check_value


def compare_values(left, op, right, budget, location=None):
    try:
        return _compare_values(left, op, right, budget, location)
    except ProfileFailure:
        raise
    except Exception:
        internal(location)


def _compare_values(left, op, right, budget, location=None):
    require_budget(budget)
    check_location(location, budget)
    if type(op) is not str:
        internal(location)
    check_value(left, budget)
    check_value(right, budget)
    budget.debit(location=location)
    domain = left.domain
    if op not in OPS:
        fail(location=location)
    if domain != right.domain or (
        domain == "L" and text_compare(left.language, right.language, budget)
    ):
        fail("RULE_COMPARISON_TYPE_MISMATCH", location)
    if domain in ("I", "B") and op not in ("eq", "ne"):
        fail("RULE_COMPARISON_TYPE_MISMATCH", location)
    if domain == "N":
        c = compare_numbers(left.value, right.value, budget)
    elif domain in ("Dz", "Dl", "Tz", "Tl"):
        c = compare_calendar(left.value, right.value, budget)
    elif domain in ("I", "S", "L"):
        c = text_compare(left.value, right.value, budget)
    elif domain == "B":
        c = (left.value > right.value) - (left.value < right.value)
    else:
        fail("INTERNAL_ERROR", location, "internal")
    return {"eq": c == 0, "ne": c != 0, "lt": c < 0, "le": c <= 0, "gt": c > 0, "ge": c >= 0}[op]
