"""Structured terms, exact lexical validation and RDF term identity."""

import re
from dataclasses import dataclass
from weakref import ref

from .rule_calendar import parse_calendar
from .rule_numbers import parse_number
from .rule_profile import (
    NUMERIC,
    RDF,
    XSD,
    ProfileFailure,
    SourceRecord,
    TermInput,
    account_input,
    check_location,
    encode_input,
    fail,
    fingerprint,
    internal,
    require_budget,
    utf8_size,
)

GRANDFATHERED = frozenset(
    (
        "en-GB-oed i-ami i-bnn i-default i-enochian i-hak i-klingon i-lux "
        "i-mingo i-navajo i-pwn i-tao i-tay i-tsu sgn-BE-FR sgn-BE-NL sgn-CH-DE "
        "art-lojban cel-gaulish no-bok no-nyn zh-guoyu zh-hakka zh-min zh-min-nan zh-xiang"
    )
    .lower()
    .split()
)
LANGTAG = re.compile(
    r"(?:(?:[a-z]{2,3}(?:-[a-z]{3}){0,3}|[a-z]{4}|[a-z]{5,8})"
    r"(?:-[a-z]{4})?(?:-(?:[a-z]{2}|[0-9]{3}))?"
    r"(?:-(?:[a-z0-9]{5,8}|[0-9][a-z0-9]{3}))*"
    r"(?:-[0-9a-wy-z](?:-[a-z0-9]{2,8})+)*"
    r"(?:-x(?:-[a-z0-9]{1,8})+)?|x(?:-[a-z0-9]{1,8})+)",
    re.ASCII | re.IGNORECASE,
)
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:", re.ASCII)


@dataclass(frozen=True, slots=True, weakref_slot=True)
class ProfileValue:
    term: TermInput
    domain: str
    value: object
    language: str = ""


_ISSUED_VALUES = {}


def _signed_value(term, domain, value, language, budget):
    result = ProfileValue(term, domain, value, language)
    digest = fingerprint(encode_input(result, budget), budget)
    key = id(result)

    def expire(reference):
        if _ISSUED_VALUES.get(key, (None,))[0] is reference:
            _ISSUED_VALUES.pop(key, None)

    _ISSUED_VALUES[key] = (ref(result, expire), digest)
    return result


def check_value(value, budget):
    require_budget(budget)
    if type(value) is not ProfileValue:
        internal()
    issued = _ISSUED_VALUES.get(id(value))
    if issued is None or issued[0]() is not value:
        internal()
    try:
        digest = fingerprint(encode_input(value, budget), budget)
    except ProfileFailure as exc:
        if exc.classification == "resource":
            raise
        internal()
    if digest != issued[1]:
        internal()


def iri_minimum(text, budget, location=None, lexical=False):
    require_budget(budget)
    if type(lexical) is not bool:
        internal(location)
    utf8_size(text, budget, budget.limits.term_bytes if lexical else 16384, location)
    budget.debit(len(text), location=location)
    if not SCHEME.match(text) or any(c.isspace() or c in '<>"{}|^`\\' for c in text):
        fail(location=location)
    return text


def parse_value(term, location, budget):
    require_budget(budget)
    check_location(location, budget)
    if type(term) is not TermInput:
        fail(location=location)
    try:
        account_input(term, budget)
    except ProfileFailure as exc:
        fail(exc.reason, location, exc.classification)
    text = term.lexical_form
    utf8_size(text, budget, budget.limits.term_bytes, location)
    if term.source is not None:
        if type(term.source) is not SourceRecord:
            fail(location=location)
        for s in (
            term.source.reference,
            term.source.digest,
            term.source.revision,
            term.source.text,
        ):
            if s is not None:
                utf8_size(s, budget, budget.limits.source_bytes, location)
    if term.kind == "iri":
        if term.datatype_iri is not None or term.language_raw is not None:
            fail(location=location)
        return _signed_value(
            term, "I", iri_minimum(text, budget, location, lexical=True), "", budget
        )
    if term.kind != "literal":
        fail(location=location)
    datatype = (
        term.datatype_iri
        if term.datatype_iri is not None
        else (RDF + "langString" if term.language_raw is not None else XSD + "string")
    )
    iri_minimum(datatype, budget, location)
    lang = term.language_raw
    if lang is not None:
        utf8_size(lang, budget, budget.limits.term_bytes, location)
        budget.debit(4 * len(lang), location=location)
        if datatype != RDF + "langString":
            fail(location=location)
        if lang.lower() not in GRANDFATHERED and not LANGTAG.fullmatch(lang):
            fail("INVALID_LITERAL_LEXICAL", location)
        return _signed_value(term, "L", text, lang.lower(), budget)
    if datatype == RDF + "langString":
        fail(location=location)
    if datatype == XSD + "string":
        budget.debit(len(text), location=location)
        if any(ord(c) == 0 or ord(c) in (0xFFFE, 0xFFFF) for c in text):
            fail("INVALID_LITERAL_LEXICAL", location)
        return _signed_value(term, "S", text, "", budget)
    if datatype == XSD + "boolean":
        if text not in ("true", "false", "1", "0"):
            fail("INVALID_LITERAL_LEXICAL", location)
        return _signed_value(term, "B", text in ("true", "1"), "", budget)
    if datatype in NUMERIC:
        return _signed_value(term, "N", parse_number(text, datatype, budget, location), "", budget)
    if datatype in (XSD + "date", XSD + "dateTime"):
        value = parse_calendar(text, datatype, budget, location)
        return _signed_value(
            term,
            ("T" if value.is_datetime else "D") + ("z" if value.explicit_offset else "l"),
            value,
            "",
            budget,
        )
    fail("UNSUPPORTED_LITERAL_DATATYPE", location)


def term_key(value, budget):
    check_value(value, budget)
    term = value.term
    lang = value.language
    datatype = term.datatype_iri or (RDF + "langString" if lang else XSD + "string")
    for s in (term.lexical_form, datatype, lang):
        utf8_size(s, budget)
    return (
        ("iri", term.lexical_form, "", "")
        if term.kind == "iri"
        else ("literal", term.lexical_form, datatype, lang)
    )
