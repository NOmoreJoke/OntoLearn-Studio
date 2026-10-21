"""Bounded data-only profile material. These records confer no producer authority.

Only exact raw syntax records are accepted; this module never parses a profile
value, compiles a rule, matches a graph, opens a source or authenticates a Job.
"""

import hashlib
import json
from dataclasses import dataclass

from .quality.rule_firing import Comparison, RuleSpec, Triple, Variable
from .quality.rule_profile import PROFILE, SourceRecord, TermInput

MATERIAL_VERSION = "i05-profile-material/1"
DEFINITION_VERSION = "profile-rule-definition/1"
CAPTURE_BUDGET_VERSION = "i05-profile-capture-budget/1"
MAX_BYTES = 8_388_608
MAX_TEXT = 1_048_576
_BASE = 3 * MAX_BYTES
_WORK = ("traversal", "scan_copy", "hash")
_LIVE = ("scalar", "objects")
_RECORDS = (
    (SourceRecord, ("reference", "digest", "revision", "text")),
    (TermInput, ("kind", "lexical_form", "datatype_iri", "language_raw", "source")),
    (Variable, ("name",)),
    (Triple, ("subject", "predicate", "object")),
    (Comparison, ("left", "operator", "right")),
    (
        RuleSpec,
        (
            "rule_id",
            "when",
            "comparisons",
            "heads",
            "source",
            "revision",
            "definition_digest",
            "policy",
        ),
    ),
)


class MaterialFailure(ValueError):
    """Safe finite local failure; never stores input, foreign errors or paths."""

    def __init__(self, reason="MATERIAL_INVALID", *, domain=None, stage=0):
        self.reason = (
            reason
            if type(reason) is str
            and reason
            in (
                "MATERIAL_INVALID",
                "MATERIAL_LIMIT",
                "MATERIAL_MISMATCH",
                "MATERIAL_INTERNAL",
                "MATERIAL_LEDGER_REUSED",
            )
            else "MATERIAL_INTERNAL"
        )
        self.domain = domain if type(domain) is str and domain in _WORK + _LIVE else None
        self.stage = stage if type(stage) is int and 0 <= stage <= 8 else 0
        super().__init__(self.reason)


class CaptureLedger:
    """Single operation, eight stages, lower-only limits and actual live tickets.

    Preparation uses A=24MiB, a conservative lower bound of the approved
    Q+D+24MiB. Production can fix actual Q/D from the exact material first.
    Successful return transfers live responsibility; it does not free objects.
    """

    def __init__(self, *, overrides=()):
        if type(overrides) is not tuple or len(overrides) > 5:
            raise MaterialFailure()
        # Keep the caller-owned exact tuple: bounded constructor validation
        # needs no new checked-list/tuple before the control budget opens.
        for position, pair in enumerate(overrides):
            if type(pair) is not tuple or len(pair) != 2:
                raise MaterialFailure()
            name, value = pair
            if type(name) is not str or name not in _WORK + _LIVE or type(value) is not int:
                raise MaterialFailure()
            if value < 0:
                raise MaterialFailure()
            for previous in range(position):
                if name == overrides[previous][0]:
                    raise MaterialFailure()
        self.overrides = overrides
        self.state = "new"
        self.caps = self.used = self.live = self.peaks = None
        self.stage = 0
        self.stage_visits = self.stage_bounds = None

    def begin(self, *, Q=0, D=0, N=0):
        if self.state != "new":
            raise MaterialFailure("MATERIAL_LEDGER_REUSED")
        self.state = "running"
        if type(Q) is not int or type(D) is not int or type(N) is not int:
            raise MaterialFailure()
        if not (0 <= Q <= 2 * MAX_BYTES and 0 <= D <= MAX_BYTES and 0 <= N <= 100):
            raise MaterialFailure("MATERIAL_LIMIT")
        A = Q + D + _BASE
        # Admit the fixed 64-unit control block BEFORE allocating any counters
        # or stage arrays. The already-validated <=5 override tuple is caller
        # owned. This opens the control ticket directly; initializing live/peak
        # at 64 below records that prior reservation, not a later reimbursement.
        control_limit = 8 * A + 2048 * N + 4096
        for name, value in self.overrides:
            if name == "objects":
                control_limit = min(value, control_limit)
        if control_limit < 64:
            raise MaterialFailure("MATERIAL_LIMIT", domain="objects", stage=0)
        self.caps = {
            "traversal": 128 * A + 65536 * N,
            "scan_copy": 64 * A + 65536 * N,
            "hash": 16 * A + 65536 * N,
            "scalar": 16 * A + 131072 * N,
            "objects": 8 * A + 2048 * N + 4096,
        }
        for name, value in self.overrides:
            self.caps[name] = min(value, self.caps[name])
        self.used = dict.fromkeys(_WORK, 0)
        self.live = {"scalar": 0, "objects": 64}
        self.peaks = {"scalar": 0, "objects": 64}
        self.stage_visits = [0] * 8
        self.stage_bounds = [0] * 8

    def enter(self, stage, J):
        if self.state != "running" or type(stage) is not int or not 1 <= stage <= 8:
            raise MaterialFailure("MATERIAL_INTERNAL")
        if type(J) is not int or J < 1 or J > 6 * MAX_BYTES:
            raise MaterialFailure("MATERIAL_INTERNAL")
        if self.stage_bounds[stage - 1]:
            raise MaterialFailure("MATERIAL_LEDGER_REUSED", stage=stage)
        self.stage = stage
        self.stage_bounds[stage - 1] = 16 * J

    def debit(self, domain, count):
        if (
            self.state != "running"
            or type(domain) is not str
            or domain not in _WORK
            or type(count) is not int
            or count < 0
        ):
            raise MaterialFailure("MATERIAL_INTERNAL")
        if self.used[domain] + count > self.caps[domain]:
            raise MaterialFailure("MATERIAL_LIMIT", domain=domain, stage=self.stage)
        if domain == "traversal":
            pos = self.stage - 1
            if pos < 0 or self.stage_visits[pos] + count > self.stage_bounds[pos]:
                raise MaterialFailure("MATERIAL_LIMIT", domain=domain, stage=self.stage)
            self.stage_visits[pos] += count
        self.used[domain] += count

    def reserve(self, domain, count):
        if (
            self.state != "running"
            or type(domain) is not str
            or domain not in _LIVE
            or type(count) is not int
            or count < 0
        ):
            raise MaterialFailure("MATERIAL_INTERNAL")
        if self.live[domain] + count > self.caps[domain]:
            raise MaterialFailure("MATERIAL_LIMIT", domain=domain, stage=self.stage)
        self.live[domain] += count
        self.peaks[domain] = max(self.peaks[domain], self.live[domain])

    def release(self, domain, count):
        if (
            type(domain) is not str
            or domain not in _LIVE
            or type(count) is not int
            or count < 0
            or count > self.live[domain]
        ):
            raise MaterialFailure("MATERIAL_INTERNAL")
        self.live[domain] -= count

    def receipt(self):
        self.debit("traversal", 64)
        self.reserve("objects", 64)
        self.reserve("scalar", 1024)
        return CaptureReceipt(
            tuple(self.used.items()),
            tuple(self.live.items()),
            tuple(self.peaks.items()),
            tuple(self.caps.items()),
            tuple(self.stage_visits),
            tuple(self.stage_bounds),
        )

    def transferred(self):
        if self.state != "running":
            raise MaterialFailure("MATERIAL_LEDGER_REUSED")
        self.state = "transferred"

    def failed(self):
        # Only callers which have actually dropped all internally-owned values
        # may terminate here. Work remains charged; no live-zero/GC claim.
        if self.state == "running":
            self.state = "failed"


@dataclass(frozen=True, slots=True)
class CaptureReceipt:
    usage: tuple
    retained: tuple
    peaks: tuple
    caps: tuple
    stage_visits: tuple
    stage_bounds: tuple
    version: str = CAPTURE_BUDGET_VERSION
    retention_owner: str = "receiving caller; raw/native references remain live"


@dataclass(frozen=True, slots=True)
class ProfileMaterial:
    text: str | None
    records: tuple | None
    rules: tuple[RuleSpec, ...]
    disabled_rule_ids: tuple[str, ...]
    source: SourceRecord | tuple
    input_domain: str
    input_preimage: bytes
    source_preimage: bytes
    definitions_preimage: bytes
    definition_material: bytes
    parser_identity: tuple[str, str]
    capture_receipt: CaptureReceipt
    version: str = MATERIAL_VERSION


@dataclass(frozen=True, slots=True)
class ProfileInputLayer:
    input_domain: str
    content: bytes | tuple
    source: SourceRecord | None
    parser_identity: tuple[str, str]


@dataclass(frozen=True, slots=True)
class SelectedMaterial:
    asserted_records: ProfileInputLayer
    ontology_records: ProfileInputLayer
    input_preimage: bytes
    source_preimage: bytes
    definition_material: bytes
    parser_identity: tuple[str, str]
    capture_receipt: CaptureReceipt
    version: str = "i05-selected-material/1"


def _require(condition):
    if not condition:
        raise MaterialFailure()


def _text(value, ledger, maximum=MAX_BYTES, *, optional=False):
    if value is None and optional:
        return None
    _require(type(value) is str)
    _require(len(value) <= maximum)
    upper = 4 * len(value)
    ledger.debit("scan_copy", 2 * upper + 1)
    ledger.reserve("scalar", upper)
    data = None
    try:
        data = value.encode("utf-8", errors="strict")
        if len(data) > maximum:
            raise MaterialFailure("MATERIAL_LIMIT", stage=ledger.stage)
    except UnicodeEncodeError:
        raise MaterialFailure() from None
    finally:
        data = None
        ledger.release("scalar", upper)
    # Bound the largest escaped encoder chunk before iterencode allocates it.
    # A valid chunk has <=MAX_BYTES UTF8, hence <=4*MAX_BYTES PEP393
    # storage even when a single astral character widens the whole chunk.
    ledger.debit("traversal", len(value) + 1)
    ledger.debit("scan_copy", 4 * len(value) + 1)
    escaped_bytes = 2
    for character in value:
        point = ord(character)
        escaped_bytes += (
            6
            if point < 32
            else 2
            if point in (34, 92)
            else 1
            if point < 128
            else 2
            if point < 2048
            else 3
            if point < 65536
            else 4
        )
        if escaped_bytes > MAX_BYTES:
            raise MaterialFailure("MATERIAL_LIMIT", stage=ledger.stage)
    # Projected primitive retains its exact source value, without normalization.
    ledger.reserve("scalar", 4 * len(value))
    return value


def _project(value, ledger, depth=0, *, json_data=False):
    if depth > 32:
        raise MaterialFailure("MATERIAL_LIMIT", stage=ledger.stage)
    ledger.debit("traversal", 1)
    kind = type(value)
    if value is None or kind is bool:
        return value
    if kind is str:
        return _text(value, ledger)
    if json_data and kind is bytes:
        _require(len(value) <= MAX_TEXT)
        ledger.debit("scan_copy", 4 * len(value) + 32)
        ledger.reserve("scalar", 8 * len(value))
        ledger.reserve("objects", 5)
        return {"encoding": "hex", "bytes": value.hex()}
    if kind is tuple or kind is list:
        _require(json_data or kind is tuple)
        if len(value) > 300000:
            raise MaterialFailure("MATERIAL_LIMIT", stage=ledger.stage)
        ledger.debit("traversal", len(value))
        ledger.reserve("objects", len(value) + 1)
        return [_project(item, ledger, depth + 1, json_data=json_data) for item in value]
    if kind is dict and json_data:
        _require(len(value) <= 100000)
        ledger.debit("traversal", 2 * len(value))
        key_width = 0
        for key in value:
            _require(type(key) is str)
            _require(len(key) <= MAX_BYTES)
            key_width += 4 * len(key) + 1
        # Prepay hash collision comparisons and key sorting, including the
        # adversarial all-collision case, before inserting into the new dict.
        # Excessively wide definitions fail this existing fixed C budget.
        ledger.debit("traversal", len(value) * len(value))
        ledger.debit("scan_copy", (len(value) + 1) * key_width)
        ledger.debit("hash", key_width)
        ledger.reserve("objects", 2 * len(value) + 1)
        output = {}
        for key, item in value.items():
            _require(type(key) is str)
            output[_text(key, ledger)] = _project(item, ledger, depth + 1, json_data=True)
        return output
    for cls, names in _RECORDS:
        ledger.debit("traversal", 1)
        if kind is cls:
            ledger.debit("traversal", 2 * len(names))
            ledger.reserve("objects", 2 * len(names) + 3)
            output = {"recordType": cls.__name__}
            for name in names:
                item = getattr(value, name)
                # Exact field grammar before recursion/foreign len/hash/iter.
                if cls is SourceRecord:
                    _require(item is None or type(item) is str)
                elif cls is TermInput:
                    if name == "source":
                        _require(item is None or type(item) is SourceRecord)
                    elif name in ("kind", "lexical_form"):
                        _require(type(item) is str)
                    else:
                        _require(item is None or type(item) is str)
                elif cls is Variable:
                    _require(type(item) is str)
                elif cls is Triple:
                    _require(
                        type(item) is TermInput
                        if name == "predicate"
                        else type(item) is TermInput or type(item) is Variable
                    )
                elif cls is Comparison:
                    _require(
                        type(item) is str
                        if name == "operator"
                        else type(item) is TermInput or type(item) is Variable
                    )
                elif cls is RuleSpec:
                    if name in ("when", "comparisons", "heads"):
                        _require(type(item) is tuple)
                        expected = Comparison if name == "comparisons" else Triple
                        ledger.debit("traversal", len(item))
                        _require(all(type(element) is expected for element in item))
                    elif name == "source":
                        _require(item is None or type(item) is SourceRecord)
                    else:
                        _require(item is None or type(item) is str)
                output[name] = _project(item, ledger, depth + 1)
            return output
    raise MaterialFailure()


def _encode(value, ledger, *, json_data=False):
    """One projection and bounded streaming encoder, ordinary live reservations."""
    start_scalar, start_objects = ledger.live["scalar"], ledger.live["objects"]
    safe = output = encoder = chunk = data = result = None
    try:
        safe = _project(value, ledger, json_data=json_data)
        # Fixed-schema nodes/UTF8 are prepaid before iterencode delegates. The
        # encoder stack/string escaping can hold <=6*MAX_BYTES characters.
        ledger.debit("traversal", 2 * MAX_BYTES)
        ledger.debit("scan_copy", 8 * MAX_BYTES)
        ledger.reserve("scalar", 6 * MAX_BYTES)
        ledger.reserve("objects", MAX_BYTES + 64)
        output = bytearray()
        encoder = json.JSONEncoder(
            ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        for chunk in encoder.iterencode(safe):
            upper = 4 * len(chunk)
            ledger.debit("scan_copy", 2 * upper + 1)
            ledger.reserve("scalar", 4 * len(chunk) + upper)
            try:
                data = chunk.encode("utf-8", errors="strict")
                if len(output) + len(data) > MAX_BYTES:
                    raise MaterialFailure("MATERIAL_LIMIT", stage=ledger.stage)
                ledger.debit("scan_copy", len(data))
                ledger.reserve("scalar", len(data))
                output.extend(data)
            finally:
                data = None
                ledger.release("scalar", 4 * len(chunk) + upper)
                chunk = None
        ledger.debit("scan_copy", len(output))
        ledger.reserve("scalar", len(output))
        result = bytes(output)
        return result
    finally:
        retained = 0 if result is None else len(result)
        safe = output = encoder = chunk = data = None
        ledger.release("scalar", ledger.live["scalar"] - start_scalar - retained)
        ledger.release("objects", ledger.live["objects"] - start_objects)


def _hash(data, ledger):
    _require(type(data) is bytes)
    ledger.debit("hash", len(data))
    ledger.reserve("scalar", 128)
    ledger.reserve("objects", 1)
    return hashlib.sha256(data).hexdigest()


def _records(value, ledger):
    _require(type(value) is tuple)
    _require(len(value) <= 100000)
    ledger.debit("traversal", 4 * len(value) + 1)
    for triple in value:
        _require(type(triple) is tuple and len(triple) == 3)
        _require(all(type(term) is TermInput for term in triple))
    return value


def _identity(identity, ledger):
    _require(type(identity) is tuple and len(identity) == 2)
    ledger.debit("traversal", 3)
    for field in identity:
        _require(type(field) is str and 0 < len(field) <= 16384)
        _text(field, ledger, 16384)
    return identity


def _definitions(rules, disabled, ledger):
    _require(type(rules) is tuple and len(rules) <= 100)
    _require(type(disabled) is tuple and len(disabled) <= len(rules))
    ledger.reserve("objects", 4 * len(rules) + len(disabled) + 4)
    ids = []
    for spec in rules:
        ledger.debit("traversal", len(ids) + 3)
        _require(type(spec) is RuleSpec and type(spec.rule_id) is str)
        _text(spec.rule_id, ledger, 16384)
        ledger.debit("scan_copy", 2 * (len(ids) + 1) * (len(spec.rule_id) + 1))
        _require(spec.rule_id not in ids)
        _require(type(spec.policy) is str and spec.policy == PROFILE)
        ids.append(spec.rule_id)
    for pos, identity in enumerate(disabled):
        _require(type(identity) is str)
        _text(identity, ledger, 16384)
        ledger.debit("traversal", len(ids) + pos + 1)
        ledger.debit("scan_copy", 2 * (len(ids) + pos + 1) * (len(identity) + 1))
        _require(identity in ids and identity not in disabled[:pos])
    raw = _encode(rules, ledger)
    # Reuse the already validated raw projection via the encoder's primitive
    # input, not JSON parse or an alternative rule compiler.
    body = []
    for spec in rules:
        ledger.debit("traversal", len(disabled) + 10)
        ledger.reserve("objects", 24)
        body.append(
            {
                "enabled": spec.rule_id not in disabled,
                "rule_id": spec.rule_id,
                "when": spec.when,
                "comparisons": spec.comparisons,
                "heads": spec.heads,
                "source": spec.source,
                "revision": spec.revision,
                "definition_digest": spec.definition_digest,
                "policy": spec.policy,
            }
        )
    material = _encode(
        {"version": DEFINITION_VERSION, "rules": body, "disabledRuleIds": disabled},
        ledger,
        json_data=True,
    )
    return raw, material


@dataclass(frozen=True, slots=True)
class RuleDefinitions:
    rules: tuple[RuleSpec, ...]
    disabled_rule_ids: tuple[str, ...]
    definitions_preimage: bytes
    definition_material: bytes
    capture_receipt: CaptureReceipt


def _read_syntax_json(data, ledger):
    _require(type(data) is bytes and len(data) <= MAX_BYTES)
    ledger.debit("scan_copy", 8 * len(data) + 1)
    ledger.debit("traversal", 4 * len(data) + 1)
    ledger.reserve("scalar", 12 * len(data))
    ledger.reserve("objects", 8 * len(data) + 64)
    # Bound parser nesting before the opaque standard-library decoder.
    depth, quoted, escaped = 0, False, False
    for char in data:
        if quoted:
            if escaped:
                escaped = False
            elif char == 92:
                escaped = True
            elif char == 34:
                quoted = False
        elif char == 34:
            quoted = True
        elif char in (91, 123):
            depth += 1
            _require(depth <= 32)
        elif char in (93, 125):
            depth -= 1
            _require(depth >= 0)
    _require(depth == 0 and not quoted)

    def number(_):
        raise MaterialFailure()

    allowed = (
        "recordType",
        "reference",
        "digest",
        "revision",
        "text",
        "kind",
        "lexical_form",
        "datatype_iri",
        "language_raw",
        "source",
        "name",
        "subject",
        "predicate",
        "object",
        "left",
        "operator",
        "right",
        "rule_id",
        "when",
        "comparisons",
        "heads",
        "definition_digest",
        "policy",
        "version",
        "rules",
        "disabledRuleIds",
        "enabled",
        "assertedRecords",
        "ontologyRecords",
        "inputDomain",
        "input",
        "parserIdentity",
        "encoding",
        "bytes",
        "references",
        "layer",
        "id",
        "turtle",
        "definition",
    )

    def pairs(items):
        _require(len(items) <= len(allowed))
        ledger.debit("traversal", 48 * len(items) + 1)
        ledger.debit("scan_copy", 1024 * len(items) + 1)
        ledger.reserve("objects", 2 * len(items) + 1)
        output = {}
        for name, value in items:
            _require(type(name) is str and len(name) <= 32)
            _require(name in allowed and name not in output)
            output[name] = value
        return output

    text = data.decode("utf-8", errors="strict")
    return json.loads(
        text, object_pairs_hook=pairs, parse_int=number, parse_float=number, parse_constant=number
    )


def _syntax_native(value, ledger):
    ledger.debit("traversal", 1)
    kind = type(value)
    if value is None or kind is str or kind is bool:
        return value
    if kind is list:
        ledger.debit("traversal", len(value))
        ledger.reserve("objects", 2 * len(value) + 2)
        return tuple(_syntax_native(item, ledger) for item in value)
    _require(kind is dict and "recordType" in value)
    tag = value["recordType"]
    _require(type(tag) is str and len(tag) <= 32)
    for cls, names in _RECORDS:
        ledger.debit("traversal", 1)
        if tag == cls.__name__:
            _require(len(value) == len(names) + 1 and all(n in value for n in names))
            ledger.debit("traversal", 2 * len(names))
            ledger.reserve("objects", 2 * len(names) + 2)
            return cls(**{name: _syntax_native(value[name], ledger) for name in names})
    raise MaterialFailure()


def decode_rule_definitions(data, *, ledger=None):
    """Strict fixed typed syntax codec. No tagged imports or ProfileValues."""
    ledger = CaptureLedger() if ledger is None else ledger
    _require(type(ledger) is CaptureLedger)
    result = error = tree = rules = disabled = raw = canonical = receipt = None
    try:
        _require(type(data) is bytes and len(data) <= MAX_BYTES)
        ledger.begin(D=len(data), N=0)
        ledger.enter(3, MAX_BYTES)
        tree = _read_syntax_json(data, ledger)
        _require(type(tree) is dict and len(tree) == 3)
        _require(all(name in tree for name in ("version", "rules", "disabledRuleIds")))
        _require(type(tree["version"]) is str and tree["version"] == DEFINITION_VERSION)
        entries = tree["rules"]
        _require(type(entries) is list and len(entries) <= 100)

        decoded = []
        names = _RECORDS[-1][1]
        for body in entries:
            ledger.debit("traversal", 32)
            _require(type(body) is dict and len(body) == len(names) + 1)
            _require("enabled" in body and all(n in body for n in names))
            _require(type(body["enabled"]) is bool)
            ledger.reserve("objects", 2 * len(names) + 4)
            decoded.append(RuleSpec(**{name: _syntax_native(body[name], ledger) for name in names}))
        rules = tuple(decoded)
        disabled = _syntax_native(tree["disabledRuleIds"], ledger)
        raw, canonical = _definitions(rules, disabled, ledger)
        for body, spec in zip(entries, rules, strict=True):
            ledger.debit("traversal", len(disabled) + 1)
            _require(body["enabled"] is (spec.rule_id not in disabled))
        ledger.debit("scan_copy", len(data) + len(canonical))
        _require(data == canonical)
        ledger.enter(8, MAX_BYTES)
        receipt = ledger.receipt()
        result = RuleDefinitions(rules, disabled, raw, canonical, receipt)
        ledger.transferred()
    except MaterialFailure as exc:
        error = MaterialFailure(exc.reason, domain=exc.domain, stage=exc.stage)
    except Exception:
        error = MaterialFailure("MATERIAL_INVALID")
    finally:
        tree = rules = disabled = raw = canonical = receipt = None
        # Closures/items are also explicitly dropped before a finite failure.
        entries = decoded = body = spec = None
        if error is not None:
            result = None
            ledger.failed()
    if error is not None:
        raise error
    return result


def _prepare_profile_material(
    text=None,
    rules=(),
    *,
    records=None,
    disabled_rule_ids=(),
    source_reference=None,
    source_revision=None,
    parser_identity=None,
    ledger=None,
    finish=True,
    budget_inputs=(0, 0),
):
    """Fix input/source before computation. No trusted handle or Job is invented."""
    ledger = CaptureLedger() if ledger is None else ledger
    _require(type(ledger) is CaptureLedger)
    material = error = source = original = source_bytes = defs = definitions = receipt = None
    try:
        _require(type(rules) is tuple and len(rules) <= 100)
        ledger.begin(Q=budget_inputs[0], D=budget_inputs[1], N=max(1, len(rules)))
        ledger.enter(1, MAX_BYTES)
        if records is None:
            _require(type(text) is str)
            _text(text, ledger, MAX_TEXT)
            ledger.debit("scan_copy", 8 * len(text))
            ledger.reserve("scalar", 4 * len(text))
            original = text.encode("utf-8", errors="strict")
            _require(len(original) <= MAX_TEXT)
            domain = "utf8-turtle"
            identity = ("semantic_turtle.parse_profile_graph", "i05-finite-7")
        else:
            _require(text is None and source_reference is None and source_revision is None)
            _records(records, ledger)
            original = _encode(records, ledger)
            domain = "profile-structured-records-json/1"
            identity = ("semantic_turtle.profile_graph_from_records", "i05-finite-7")
        parser_identity = _identity(
            identity if parser_identity is None else parser_identity, ledger
        )
        ledger.debit("scan_copy", 4 * sum(len(part) for part in parser_identity) + 1)
        _require(parser_identity == identity)
        ledger.enter(2, MAX_BYTES)
        if records is None:
            _text(source_reference, ledger, 16384, optional=True)
            _text(source_revision, ledger, 16384, optional=True)
            ledger.reserve("objects", 1)
            source = SourceRecord(
                source_reference,
                _hash(original, ledger),
                source_revision,
                text if len(original) <= 65536 else None,
            )
        else:
            ledger.debit("traversal", 4 * len(records))
            ledger.reserve("objects", 3 * len(records) + 1)
            source = tuple(term.source for triple in records for term in triple)
        source_bytes = _encode(source, ledger)
        ledger.enter(3, MAX_BYTES)
        defs, definitions = _definitions(rules, disabled_rule_ids, ledger)
        _require(len(original) + len(source_bytes) <= 2 * MAX_BYTES)
        # The receiving record retains raw syntax/source as well as encoded
        # bytes. Their fixed-schema node/string bound is paid independently of
        # the temporary projected tree which _encode actually dropped.
        retained = len(original) + len(source_bytes) + len(defs)
        ledger.reserve("scalar", 4 * retained)
        ledger.reserve("objects", 2 * retained + 8)
        if finish:
            ledger.enter(8, MAX_BYTES)
            ledger.reserve("objects", 1)
            receipt = ledger.receipt()
        material = ProfileMaterial(
            text,
            records,
            rules,
            disabled_rule_ids,
            source,
            domain,
            original,
            source_bytes,
            defs,
            definitions,
            parser_identity,
            receipt,
        )
        if finish:
            ledger.transferred()
    except MaterialFailure as exc:
        error = MaterialFailure(exc.reason, domain=exc.domain, stage=exc.stage)
    except Exception:
        error = MaterialFailure("MATERIAL_INTERNAL")
    finally:
        source = original = source_bytes = defs = definitions = receipt = None
        if error is not None:
            material = None
            ledger.failed()
    if error is not None:
        raise error
    return material


def prepare_profile_material(
    text=None,
    rules=(),
    *,
    records=None,
    disabled_rule_ids=(),
    source_reference=None,
    source_revision=None,
    parser_identity=None,
    ledger=None,
):
    return _prepare_profile_material(
        text,
        rules,
        records=records,
        disabled_rule_ids=disabled_rule_ids,
        source_reference=source_reference,
        source_revision=source_revision,
        parser_identity=parser_identity,
        ledger=ledger,
    )


def _consumer_definition(value, ledger):
    # Actual fixed 3ef semantic_execution._request consumes these two bodies:
    # query {text,references?}; constraint {turtle,enabled,references?}.
    _require(type(value) is dict and 1 <= len(value) <= 3)
    ledger.debit("traversal", 8 * len(value) + 1)
    for key in value:
        _require(type(key) is str and key in ("text", "turtle", "enabled", "references"))
    if "text" in value:
        _require(len(value) == 1 + ("references" in value) and type(value["text"]) is str)
        kind = "query"
    else:
        _require("turtle" in value and "enabled" in value)
        _require(type(value["turtle"]) is str and type(value["enabled"]) is bool)
        kind = "validation"
    if "references" in value:
        refs = value["references"]
        _require(type(refs) is list or type(refs) is tuple)
        _require(len(refs) <= 100000)
        ledger.debit("traversal", 8 * len(refs))
        for ref in refs:
            _require(type(ref) is dict and len(ref) == 2)
            for key in ref:
                _require(type(key) is str and key in ("layer", "id"))
            _require("layer" in ref and "id" in ref)
            _require(type(ref["layer"]) is str and type(ref["id"]) is str)
    ledger.reserve("objects", 8)
    return {"version": "i05-consumer-definition/1", "kind": kind, "definition": value}


def _selected_layer(value, identity, ledger):
    if type(value) is tuple:
        ledger.reserve("objects", 1)
        value = ProfileInputLayer("profile-structured-records-json/1", value, None, identity)
    _require(type(value) is ProfileInputLayer)
    _require(type(value.input_domain) is str)
    _identity(value.parser_identity, ledger)
    if value.input_domain == "utf8-turtle":
        _require(type(value.content) is bytes and len(value.content) <= MAX_TEXT)
        ledger.debit("scan_copy", 8 * len(value.content) + 1)
        ledger.reserve("scalar", 4 * len(value.content))
        value.content.decode("utf-8", errors="strict")
        ledger.release("scalar", 4 * len(value.content))
    else:
        _require(value.input_domain == "profile-structured-records-json/1" and value.source is None)
        _records(value.content, ledger)
    ledger.reserve("objects", 8)
    return value, {
        "inputDomain": value.input_domain,
        "input": value.content,
        "parserIdentity": value.parser_identity,
    }


def _selected_source(layer, ledger):
    if layer.input_domain == "utf8-turtle":
        source = layer.source
        _require(type(source) is SourceRecord)
        for value in (source.reference, source.digest, source.revision, source.text):
            _text(value, ledger, optional=True)
        digest = _hash(layer.content, ledger)
        ledger.debit("scan_copy", len(digest) + 1)
        _require(type(source.digest) is str and source.digest == digest)
        text = None
        if len(layer.content) <= 65536:
            ledger.debit("scan_copy", 8 * len(layer.content) + 1)
            ledger.reserve("scalar", 4 * len(layer.content))
            text = layer.content.decode("utf-8", errors="strict")
        ledger.debit("scan_copy", 8 * len(layer.content) + 1)
        _require(source.text == text)
        text = None
        return source
    ledger.debit("traversal", 4 * len(layer.content))
    ledger.reserve("objects", 3 * len(layer.content) + 1)
    return tuple(term.source for row in layer.content for term in row)


def _layer_from_json(value, ledger):
    _require(type(value) is dict and len(value) == 3)
    _require(all(key in value for key in ("inputDomain", "input", "parserIdentity")))
    domain, content, identity = value["inputDomain"], value["input"], value["parserIdentity"]
    _require(type(domain) is str and type(identity) is list and len(identity) == 2)
    ledger.debit("traversal", 8)
    ledger.reserve("objects", 3)
    if domain == "utf8-turtle":
        _require(type(content) is dict and len(content) == 2)
        _require("encoding" in content and "bytes" in content)
        _require(type(content["encoding"]) is str and content["encoding"] == "hex")
        raw = content["bytes"]
        _require(type(raw) is str and len(raw) <= 2 * MAX_TEXT)
        ledger.debit("scan_copy", 4 * len(raw) + 1)
        ledger.reserve("scalar", len(raw))
        content = bytes.fromhex(raw)
    else:
        _require(domain == "profile-structured-records-json/1")
        content = _syntax_native(content, ledger)
    return ProfileInputLayer(domain, content, None, tuple(identity))


def _prepare_selected_material(
    asserted_records, ontology_records, definition, *, parser_identity, ledger, encoded=None
):
    _require(type(ledger) is CaptureLedger)
    material = error = source = original = source_bytes = encoded_definition = receipt = None
    asserted = ontology = asserted_body = ontology_body = input_tree = source_tree = (
        definition_tree
    ) = None
    try:
        ledger.begin(N=0)
        ledger.enter(1, MAX_BYTES)
        if encoded is not None:
            input_tree = _read_syntax_json(encoded[0], ledger)
            _require(type(input_tree) is dict and len(input_tree) == 2)
            _require("assertedRecords" in input_tree and "ontologyRecords" in input_tree)
            asserted_records = _layer_from_json(input_tree["assertedRecords"], ledger)
            ontology_records = _layer_from_json(input_tree["ontologyRecords"], ledger)
        _identity(parser_identity, ledger)
        asserted, asserted_body = _selected_layer(asserted_records, parser_identity, ledger)
        ontology, ontology_body = _selected_layer(ontology_records, parser_identity, ledger)
        original = _encode(
            {"assertedRecords": asserted_body, "ontologyRecords": ontology_body},
            ledger,
            json_data=True,
        )
        ledger.enter(2, MAX_BYTES)
        if encoded is not None:
            source_tree = _read_syntax_json(encoded[1], ledger)
            _require(type(source_tree) is dict and len(source_tree) == 2)
            _require("assertedRecords" in source_tree and "ontologyRecords" in source_tree)
            source_asserted = _syntax_native(source_tree["assertedRecords"], ledger)
            source_ontology = _syntax_native(source_tree["ontologyRecords"], ledger)
            ledger.reserve("objects", 2)
            if asserted.input_domain == "utf8-turtle":
                asserted = ProfileInputLayer(
                    asserted.input_domain,
                    asserted.content,
                    source_asserted,
                    asserted.parser_identity,
                )
            if ontology.input_domain == "utf8-turtle":
                ontology = ProfileInputLayer(
                    ontology.input_domain,
                    ontology.content,
                    source_ontology,
                    ontology.parser_identity,
                )
        source = {
            "assertedRecords": _selected_source(asserted, ledger),
            "ontologyRecords": _selected_source(ontology, ledger),
        }
        source_bytes = _encode(source, ledger, json_data=True)
        ledger.enter(3, MAX_BYTES)
        if encoded is not None:
            definition_tree = _read_syntax_json(encoded[2], ledger)
            _require(type(definition_tree) is dict and len(definition_tree) == 3)
            _require(all(k in definition_tree for k in ("version", "kind", "definition")))
            definition = definition_tree["definition"]
        encoded_definition = _encode(
            _consumer_definition(definition, ledger), ledger, json_data=True
        )
        if encoded is not None:
            ledger.enter(4, 3 * MAX_BYTES)
            for actual, supplied in zip(
                (original, source_bytes, encoded_definition), encoded, strict=True
            ):
                ledger.debit("scan_copy", len(actual) + len(supplied) + 1)
                _require(actual == supplied)
        retained = len(original) + len(source_bytes) + len(encoded_definition)
        ledger.reserve("scalar", 4 * retained)
        ledger.reserve("objects", 2 * retained + 8)
        ledger.enter(8, MAX_BYTES)
        ledger.reserve("objects", 1)
        receipt = ledger.receipt()
        material = SelectedMaterial(
            asserted, ontology, original, source_bytes, encoded_definition, parser_identity, receipt
        )
        ledger.transferred()
    except MaterialFailure as exc:
        error = MaterialFailure(exc.reason, domain=exc.domain, stage=exc.stage)
    except Exception:
        error = MaterialFailure("MATERIAL_INVALID")
    finally:
        source = original = source_bytes = encoded_definition = receipt = None
        asserted = ontology = asserted_body = ontology_body = input_tree = source_tree = (
            definition_tree
        ) = None
        source_asserted = source_ontology = actual = supplied = definition = None
        if encoded is not None:
            asserted_records = ontology_records = None
        if error is not None:
            material = None
            ledger.failed()
    if error is not None:
        raise error
    return material


def prepare_selected_material(
    asserted_records, ontology_records, definition, *, parser_identity, ledger=None
):
    """All K carry their own exact raw layers; no graph is computed here."""
    ledger = CaptureLedger() if ledger is None else ledger
    return _prepare_selected_material(
        asserted_records,
        ontology_records,
        definition,
        parser_identity=parser_identity,
        ledger=ledger,
    )


def decode_selected_material(
    input_preimage, source_preimage, definition_material, *, parser_identity, ledger=None
):
    """Strict roundtrip of U/D, without source authority or executing its text."""
    for value in (input_preimage, source_preimage, definition_material):
        _require(type(value) is bytes and len(value) <= MAX_BYTES)
    ledger = CaptureLedger() if ledger is None else ledger
    return _prepare_selected_material(
        None,
        None,
        None,
        parser_identity=parser_identity,
        ledger=ledger,
        encoded=(input_preimage, source_preimage, definition_material),
    )
