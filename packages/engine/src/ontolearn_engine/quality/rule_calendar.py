"""Independent proleptic Gregorian days and exact seconds, no datetime/TZ."""

import re
from dataclasses import dataclass

from .rule_numbers import (
    Number,
    add,
    check_ints,
    check_number,
    compare_numbers,
    digits,
    divide,
    mul,
    power10,
    rational,
)
from .rule_profile import XSD, check_location, fail, internal, require_budget

YEAR = r"(-?(?:[1-9][0-9]{3,}|0[0-9]{3}))"
DATE = YEAR + r"-([0-9]{2})-([0-9]{2})"
TZ = r"(Z|[+-][0-9]{2}:[0-9]{2})?"
DATE_RE = re.compile(DATE + TZ, re.ASCII)
TIME_RE = re.compile(DATE + r"T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?" + TZ, re.ASCII)


@dataclass(frozen=True, slots=True)
class Calendar:
    day: int
    second: Number
    explicit_offset: bool
    is_datetime: bool


def day_serial(year, month, day, budget):
    check_ints(budget, year, month, day)
    ya = add(year, -int(month <= 2), budget)
    era, yoe = divide(ya, 400, budget)
    mp = month + (-3 if month > 2 else 9)
    doy = (153 * mp + 2) // 5 + day - 1
    serial = add(mul(era, 146097, budget), yoe * 365 + yoe // 4 - yoe // 100 + doy, budget)
    budget.bits(serial)
    return serial


def parse_calendar(text, datatype, budget, location=None):
    require_budget(budget)
    check_location(location, budget)
    if type(text) is not str or type(datatype) is not str:
        internal(location)
    if datatype not in (XSD + "date", XSD + "dateTime"):
        fail("UNSUPPORTED_LITERAL_DATATYPE", location)
    # Regex and bounded field/slice scans/copies are prepaid, separately from bigint work.
    budget.debit(8 * len(text), location=location)
    is_time = datatype == XSD + "dateTime"
    match = (TIME_RE if is_time else DATE_RE).fullmatch(text)
    if not match:
        fail("INVALID_LITERAL_LEXICAL", location)
    parts = match.groups()
    year_text, mo, dy = parts[:3]
    year = digits(year_text.lstrip("-"), budget, location) * (
        -1 if year_text.startswith("-") else 1
    )
    month, day = int(mo), int(dy)
    leap = divide(year, 4, budget)[1] == 0 and (
        divide(year, 100, budget)[1] != 0 or divide(year, 400, budget)[1] == 0
    )
    days = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if not 1 <= month <= 12 or not 1 <= day <= days[month - 1]:
        fail("INVALID_LITERAL_LEXICAL", location)
    serial = day_serial(year, month, day, budget)
    if is_time:
        hh, mm, ss = map(int, parts[3:6])
        frac = parts[6] or ""
        budget.bound(len(frac), "digits", location)
        f = digits(frac, budget, location) if frac else 0
        if hh > 24 or mm > 59 or ss > 59 or (hh == 24 and (mm or ss or f)):
            fail("INVALID_LITERAL_LEXICAL", location)
        den = power10(len(frac), budget)
        second = add(mul(hh * 3600 + mm * 60 + ss, den, budget), f, budget)
        tz = parts[7]
    else:
        den, second, tz = 1, 0, parts[3]
    if tz and tz != "Z":
        th, tm = int(tz[1:3]), int(tz[4:6])
        if th > 14 or tm > 59 or (th == 14 and tm):
            fail("INVALID_LITERAL_LEXICAL", location)
        offset = (th * 60 + tm) * 60 * (-1 if tz[0] == "-" else 1)
        second = add(second, -mul(offset, den, budget), budget)
    carry, second = divide(second, mul(86400, den, budget), budget)
    serial = add(serial, carry, budget)
    budget.bits(serial)
    return Calendar(serial, rational(second, den, budget), tz is not None, is_time)


def compare_calendar(a, b, budget):
    require_budget(budget)
    for item in (a, b):
        if type(item) is not Calendar:
            internal()
        check_ints(budget, item.day)
        check_number(item.second, budget)
        if type(item.explicit_offset) is not bool or type(item.is_datetime) is not bool:
            internal()
    if a.explicit_offset != b.explicit_offset or a.is_datetime != b.is_datetime:
        fail("RULE_COMPARISON_TYPE_MISMATCH")
    budget.debit(max(1, (a.day.bit_length() + b.day.bit_length() + 31) // 32))
    return (a.day > b.day) - (a.day < b.day) or compare_numbers(a.second, b.second, budget)
