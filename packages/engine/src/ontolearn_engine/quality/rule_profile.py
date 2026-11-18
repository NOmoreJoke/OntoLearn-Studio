"""Private, bounded profile data and accounting; no execution/transport capability."""

import sys
from dataclasses import dataclass, fields
from hashlib import sha256

PROFILE = "OntoLearn-rule-comparison-profile/1"
BUDGET_VERSION = "mechanism-budget/1"
PINS = ("RDF-20140225", "SHACL-20170720", "SPARQL-20130321", "XSD-20120405")
XSD = "http://www.w3.org/2001/XMLSchema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
NUMERIC = tuple(
    XSD + s for s in ("integer", "int", "nonNegativeInteger", "decimal", "float", "double")
)
OPS = ("eq", "ne", "lt", "le", "gt", "ge")


@dataclass(frozen=True, slots=True)
class InputLocation:
    section: str | None = None
    index: int | None = None
    side: str | None = None
    span: tuple[int, int] | None = None


def _location_shape(location):
    if location is None:
        return True
    if type(location) is not InputLocation:
        return False
    if location.section is not None and type(location.section) is not str:
        return False
    if location.side is not None and type(location.side) is not str:
        return False
    if location.section not in (None, "when", "comparison", "head") or location.side not in (
        None,
        "left",
        "right",
    ):
        return False
    if location.index is not None and type(location.index) is not int:
        return False
    return location.span is None or (
        type(location.span) is tuple
        and len(location.span) == 2
        and all(type(n) is int for n in location.span)
    )


def check_location(location, budget):
    require_budget(budget)
    if not _location_shape(location):
        fail()
    if location is None:
        return
    numbers = (() if location.index is None else (location.index,)) + (location.span or ())
    for number in numbers:
        budget.bits(number)
        budget.debit(max(1, (number.bit_length() + 31) // 32))
        if number < 0:
            fail()
    if location.span is not None and location.span[0] > location.span[1]:
        fail()


@dataclass(frozen=True, slots=True)
class SourceRecord:
    reference: str | None = None
    digest: str | None = None
    revision: str | None = None
    text: str | None = None


@dataclass(frozen=True, slots=True)
class TermInput:
    kind: str
    lexical_form: str
    datatype_iri: str | None = None
    language_raw: str | None = None
    source: SourceRecord | None = None


class ProfileFailure(Exception):
    """Safe local fields only. Traceback is never serialized by this module."""

    def __init__(self, reason, location=None, classification="input"):
        if (
            type(reason) is not str
            or type(classification) is not str
            or not _location_shape(location)
        ):
            reason, location, classification = "INTERNAL_ERROR", None, "internal"
        super().__init__(reason)
        self._safe = (reason, location, classification)

    @property
    def reason(self):
        return self._safe[0]

    @property
    def location(self):
        return self._safe[1]

    @property
    def classification(self):
        return self._safe[2]


def fail(reason="INVALID_RULE", location=None, classification="input"):
    raise ProfileFailure(reason, location, classification)


def internal(location=None):
    fail("INTERNAL_ERROR", location, "internal")


@dataclass(frozen=True, slots=True)
class ProfileLimits:
    input_bytes: int = 262144
    term_bytes: int = 16384
    source_bytes: int = 65536
    digits: int = 4096
    integer_bits: int = 16384
    temporary_bits: int = 32768
    rules: int = 100
    when: int = 16
    comparisons: int = 32
    heads: int = 16
    variables: int = 64
    bindings: int = 1024
    firings: int = 1024
    head_occurrences: int = 16384
    trace_items: int = 8192
    output_bytes: int = 262144
    work: int = 16777216

    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if type(v) is not int or not 0 <= v <= f.default:
                fail("RULE_INPUT_BUDGET", classification="resource")


class Budget:
    """Per-call debit-only counters. No public reset or limit replacement API.

    Trace units: each firing, binding pair, when/comparison/head occurrence,
    every proof-leaf occurrence and each retained basis reference = one unit.
    Each retained term/operand reference is an additional unit.
    Aliases are traversed and charged per occurrence, never by object identity.
    """

    __slots__ = ("_limits", "_used", "_phase")

    def __init__(self, limits=None):
        if limits is not None and type(limits) is not ProfileLimits:
            fail("RULE_INPUT_BUDGET", classification="resource")
        self._limits = limits or ProfileLimits()
        self._used = dict.fromkeys(
            ("work", "input_bytes", "output_bytes", "trace_items", "firings", "head_occurrences"), 0
        )
        self._phase = "new"

    @property
    def limits(self):
        return self._limits

    @property
    def usage(self):
        return tuple(self._used.items())

    def debit(self, amount=1, counter="work", location=None):
        if (
            type(amount) is not int
            or amount < 0
            or type(counter) is not str
            or counter not in self._used
        ):
            internal(location)
        value = self._used[counter] + amount
        if value > getattr(self.limits, counter):
            reason = {"work": "WORK_LIMIT", "input_bytes": "RULE_INPUT_BUDGET"}.get(
                counter, "RULE_EVIDENCE_RESULT_LIMIT"
            )
            fail(reason, location, "resource")
        self._used[counter] = value

    def bound(self, value, name, location=None):
        if (
            type(value) is not int
            or type(name) is not str
            or name not in ProfileLimits.__dataclass_fields__
        ):
            internal(location)
        if value > getattr(self.limits, name):
            fail("RULE_INPUT_BUDGET", location, "resource")

    def bits(self, value, temporary=False, location=None):
        if type(value) is not int or type(temporary) is not bool:
            internal(location)
        self.bound(value.bit_length(), "temporary_bits" if temporary else "integer_bits", location)

    def start(self, phase):
        if type(phase) is not str or phase not in ("compile", "evaluate"):
            internal()
        expected = "new" if phase == "compile" else "compile"
        if self._phase != expected:
            internal()
        self._phase = phase


def require_budget(budget):
    if type(budget) is not Budget:
        internal()


def utf8_size(text, budget, cap=None, location=None):
    require_budget(budget)
    check_location(location, budget)
    if cap is not None and type(cap) is not int:
        internal(location)
    if type(text) is not str:
        fail(location=location)
    # Precharge before scanning, including long common-prefix strings.
    budget.debit(len(text), location=location)
    n = 0
    for c in text:
        k = ord(c)
        if 0xD800 <= k <= 0xDFFF:
            fail(location=location)
        n += 1 if k < 128 else 2 if k < 2048 else 3 if k < 65536 else 4
        if cap is not None and n > cap:
            fail("RULE_INPUT_BUDGET", location, "resource")
    budget.debit(n, location=location)
    return n


def text_compare(a, b, budget):
    require_budget(budget)
    if type(a) is not str or type(b) is not str:
        internal()
    budget.debit(len(a) + len(b) + 1)
    return (a > b) - (a < b)


def tuple_compare(a, b, budget):
    require_budget(budget)
    if type(a) is not tuple or type(b) is not tuple:
        internal()
    for x, y in zip(a, b, strict=False):
        if type(x) is str and type(y) is str:
            c = text_compare(x, y, budget)
        elif type(x) is tuple and type(y) is tuple:
            c = tuple_compare(x, y, budget)
        elif type(x) is int and type(y) is int:
            budget.bits(x, temporary=True)
            budget.bits(y, temporary=True)
            budget.debit(max(1, (x.bit_length() + 31) // 32) + max(1, (y.bit_length() + 31) // 32))
            c = (x > y) - (x < y)
        elif type(x) is bool and type(y) is bool:
            budget.debit()
            c = (x > y) - (x < y)
        else:
            internal()
        if c:
            return c
    return (len(a) > len(b)) - (len(a) < len(b))


def _walk(value, budget, output, sink, depth=0):
    """Streaming canonical private encoding, precharged before every append.

    Integers use hex strings (no process-global decimal conversion policy).
    Fixed class names and field names are encoded as well as their values.
    No json.dumps, arbitrary repr/iterators, callbacks or alias exemption.
    """
    if depth > 32:
        fail("RULE_INPUT_BUDGET", classification="resource")

    def emit(data):
        budget.debit(len(data))
        budget.debit(len(data), "output_bytes" if output else "input_bytes")
        if sink is not None:
            sink.extend(data)

    t = type(value)
    if type(t) is not type:
        fail()
    if t is str:
        utf8_size(value, budget)
        emit(b'"')
        for c in value:
            k = ord(c)
            data = f"\\u{k:04x}".encode() if k < 32 or c in '\\"' else c.encode("utf-8")
            emit(data)
        emit(b'"')
    elif value is None or t is bool:
        emit(b"null" if value is None else b"true" if value else b"false")
    elif t is int:
        budget.bits(value)
        budget.debit(max(1, value.bit_length() // 4 + 2))
        emit(("i" + hex(value) + ";").encode())
    elif t in (tuple, list):
        budget.debit(len(value))
        emit(b"(" if t is tuple else b"[")
        for item in value:
            _walk(item, budget, output, sink, depth + 1)
            emit(b",")
        emit(b")" if t is tuple else b"]")
    else:
        # Identify actual approved record classes without reflecting input metadata.
        tag = None
        records = (
            ("rule_profile", ("InputLocation", "SourceRecord", "TermInput", "ProfileLimits")),
            ("rule_numbers", ("Number",)),
            ("rule_calendar", ("Calendar",)),
            ("rule_terms", ("ProfileValue",)),
            (
                "rule_firing",
                (
                    "Variable",
                    "Triple",
                    "Comparison",
                    "RuleSpec",
                    "Catalog",
                    "BindingMatch",
                    "_CompiledRule",
                    "ComparisonEvidence",
                    "HeadEvidence",
                    "PreparedFiring",
                ),
            ),
        )
        for owner, names in records:
            module = sys.modules.get(__package__ + "." + owner)
            if module is None:
                continue
            for name in names:
                budget.debit()
                if t is module.__dict__.get(name):
                    tag = name
                    break
            if tag is not None:
                break
        if tag is None:
            fail()
        emit(b"{")
        _walk(tag, budget, output, sink, depth + 1)
        for f in fields(value):
            _walk(f.name, budget, output, sink, depth + 1)
            _walk(getattr(value, f.name), budget, output, sink, depth + 1)
        emit(b"}")


def account_input(value, budget):
    require_budget(budget)
    _walk(value, budget, False, None)


def encode_input(value, budget):
    require_budget(budget)
    sink = bytearray()
    _walk(value, budget, False, sink)
    return bytes(sink)


def encode_output(value, budget):
    require_budget(budget)
    sink = bytearray()
    _walk(value, budget, True, sink)
    return bytes(sink)


def fingerprint(data, budget=None):
    if type(data) is not bytes:
        internal()
    require_budget(budget)
    budget.bound(len(data), "input_bytes")
    budget.debit(max(1, len(data)))
    return sha256(data).hexdigest()
