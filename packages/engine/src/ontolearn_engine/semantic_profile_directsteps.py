"""Bounded direct-witness data, capture index and local DAG checks.

No reasoner, graph, ProfileValue, source authority or Job is constructed here.
Logical tickets describe work and live references, not CPython/RSS capacity.
"""

from dataclasses import dataclass

from .quality.rule_profile import TermInput

VERSION = "i05-direct-rdfs-steps/1"
BUDGET_VERSION = "i05-direct-steps-budget/1"
MAX_BYTES = 8_388_608
MAX_CANDIDATES = 250_000
MAX_STEPS = 100_000
MAX_WORK = 581_671_040
MAX_OBJECTS = 270_635_588
MAX_SCALAR = 50_331_776
RULES = (
    "rdfs9-type-via-subclass",
    "rdfs11-subclass-transitive",
    "rdfs2-domain",
    "rdfs3-range",
)
_STAGES = ("entry", "capture", "link", "encode", "restore", "roots", "receipt", "cleanup")
_DOMAINS = ("work", "scan_copy", "objects", "scalar")
_REASONS = (
    "DIRECT_STEPS_INVALID",
    "DIRECT_STEPS_LIMIT",
    "DIRECT_STEPS_REUSED",
    "DIRECT_STEPS_INTERNAL",
)
_CLASSES = ("input", "resource", "expectation", "internal")
_RDF_TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
_SUBCLASS = "<http://www.w3.org/2000/01/rdf-schema#subClassOf>"
_DOMAIN = "<http://www.w3.org/2000/01/rdf-schema#domain>"
_RANGE = "<http://www.w3.org/2000/01/rdf-schema#range>"
_XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"
_LANG_STRING = "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
_EVENT_OBJECTS = 16
_EVENT_SCALAR = 128
_EVENT_WORK = 16


class DirectStepsFailure(ValueError):
    """Finite fields only, with no incoming value, path or exception string."""

    def __init__(
        self, reason="DIRECT_STEPS_INVALID", classification=None, *, stage="entry", domain=None
    ):
        if type(reason) is not str or reason not in _REASONS:
            reason = "DIRECT_STEPS_INTERNAL"
        inferred = _CLASSES[_REASONS.index(reason)]
        if classification is not None and (
            type(classification) is not str or classification != inferred
        ):
            reason, inferred = "DIRECT_STEPS_INTERNAL", "internal"
        self.reason, self.classification = reason, inferred
        self.stage = stage if type(stage) is str and stage in _STAGES else "entry"
        self.domain = domain if type(domain) is str and domain in _DOMAINS else None
        super().__init__(reason)


def _require(condition, ledger=None):
    if not condition:
        raise DirectStepsFailure(stage="entry" if ledger is None else ledger.stage)


@dataclass(frozen=True, slots=True)
class DirectStepsReceipt:
    usage: tuple
    retained: tuple
    peaks: tuple
    caps: tuple
    events: tuple
    candidates: int
    steps: int
    key_bytes: int
    carrier_bytes: int
    version: str = BUDGET_VERSION
    retention_owner: str = "receiving caller; carrier/view/diagnostic references remain live"


class DirectStepsLedger:
    """One finite pool. Fee-event bookkeeping is charged to this same pool."""

    def __init__(self, *, overrides=()):
        _require(type(overrides) is tuple and len(overrides) <= 4)
        for pos, pair in enumerate(overrides):
            _require(type(pair) is tuple and len(pair) == 2)
            name, count = pair
            _require(type(name) is str and name in _DOMAINS)
            _require(type(count) is int and count >= 0)
            for previous in range(pos):
                _require(name != overrides[previous][0])
        self.overrides = overrides
        self.state, self.stage = "new", "entry"
        self.used = self.live = self.peaks = self.caps = None
        self._events = None
        self._receipt_taken = False
        self.candidates = self.steps = self.key_bytes = self.carrier_bytes = 0
        self.last_action = self.last_domain = None
        self.last_count = 0
        self._cleanup_objects = self._cleanup_scalar = 0
        self._data_objects = self._data_scalar = self._cleanup_credit = 0

    def begin(self, *, stage="capture"):
        if self.state != "new":
            raise DirectStepsFailure("DIRECT_STEPS_REUSED", stage=self.stage)
        self.state = "running"
        _require(type(stage) is str and stage in _STAGES, self)
        obj, scalar = MAX_OBJECTS, MAX_SCALAR
        for name, count in self.overrides:
            if name == "objects":
                obj = min(obj, count)
            elif name == "scalar":
                scalar = min(scalar, count)
        # Open both fixed control reservations before any counter/container.
        if obj < 128 or scalar < 128:
            raise DirectStepsFailure(
                "DIRECT_STEPS_LIMIT", stage="entry", domain="objects" if obj < 128 else "scalar"
            )
        self.stage = stage
        self.caps = {
            "work": MAX_WORK,
            "scan_copy": MAX_WORK,
            "objects": MAX_OBJECTS,
            "scalar": MAX_SCALAR,
        }
        for name, count in self.overrides:
            self.caps[name] = min(self.caps[name], count)
        self.used = {"work": 0, "scan_copy": 0}
        self.live = {"objects": 128, "scalar": 128}
        self.peaks = {"objects": 128, "scalar": 128}
        # This single fixed begin record is included in the 128 control block.
        self._events = [("begin", "objects", 128, stage, 0, 0, 0, 0, 0, 128, 0, 128)]

    @property
    def usage(self):
        return self.used

    @property
    def events(self):
        # Diagnostic reference, not an unmetered tuple copy or authorization.
        return self._events

    def _running(self):
        if self.state != "running" or self._receipt_taken:
            raise DirectStepsFailure("DIRECT_STEPS_REUSED", stage=self.stage)

    def _apply(self, action, domain, count):
        self._running()
        _require(type(domain) is str and domain in _DOMAINS, self)
        _require(type(count) is int and count >= 0, self)
        self.last_action, self.last_domain, self.last_count = action, domain, count
        w, scan = self.used["work"], self.used["scan_copy"]
        obj, scalar = self.live["objects"], self.live["scalar"]
        multiplier = 3 if action == "reserve" else 1
        nw, ns = w + multiplier * _EVENT_WORK, scan
        no, nl = obj + multiplier * _EVENT_OBJECTS, scalar + multiplier * _EVENT_SCALAR
        if action == "debit":
            _require(domain in ("work", "scan_copy"), self)
            nw += count
            if domain == "scan_copy":
                ns += count
        elif action == "reserve":
            _require(domain in ("objects", "scalar"), self)
            if domain == "objects":
                no += count
            else:
                nl += count
        elif action == "release":
            _require(domain in ("objects", "scalar"), self)
            _require(count <= self.live[domain] - 128, self)
            if domain == "objects":
                no -= count
            else:
                nl -= count
        else:
            raise DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage=self.stage)
        for name, value in (("work", nw), ("scan_copy", ns), ("objects", no), ("scalar", nl)):
            if value > self.caps[name]:
                raise DirectStepsFailure("DIRECT_STEPS_LIMIT", stage=self.stage, domain=name)
        # Before append, all of its own record/slot/scalar work is prepaid.
        if action == "reserve":
            self._cleanup_credit += 2
            if domain == "objects":
                self._data_objects += count
            else:
                self._data_scalar += count
        self.used["work"], self.used["scan_copy"] = nw, ns
        self.live["objects"], self.live["scalar"] = no, nl
        self.peaks["objects"] = max(self.peaks["objects"], no)
        self.peaks["scalar"] = max(self.peaks["scalar"], nl)
        self._events.append(
            (action, domain, count, self.stage, w, nw, scan, ns, obj, no, scalar, nl)
        )

    def debit(self, domain, count=1):
        self._apply("debit", domain, count)

    charge = debit

    def reserve(self, domain, count=1):
        self._apply("reserve", domain, count)

    def release(self, domain, count=1):
        self._running()
        _require(type(domain) is str and domain in ("objects", "scalar"), self)
        self.discard(
            objects=count if domain == "objects" else 0,
            scalar=count if domain == "scalar" else 0,
            action="release",
        )

    def enter(self, stage):
        self._running()
        _require(type(stage) is str and stage in _STAGES, self)
        self.debit("work", 1)
        self.stage = stage

    def consume_key(self, count):
        self._running()
        _require(type(count) is int and count >= 0, self)
        if self.key_bytes + count > MAX_BYTES:
            raise DirectStepsFailure("DIRECT_STEPS_LIMIT", stage=self.stage, domain="work")
        self.debit("work", count + 1)
        self.key_bytes += count

    def note_carrier(self, count):
        self._running()
        _require(type(count) is int and 0 <= count <= MAX_BYTES, self)
        self.debit("work", 1)
        self.carrier_bytes = max(self.carrier_bytes, count)

    def discard(self, *, objects=0, scalar=0, action="discard"):
        """After real drop, append the cleanup event paid by prior reserve.

        Two future cleanup records per reservation cover split temporary/final
        lifetimes. Neither pool exhaustion nor terminal state needs a new fee
        before dropping references. Fee records remain paid live diagnostics.
        """
        if self.live is None:
            return
        if type(objects) is not int or type(scalar) is not int or objects < 0 or scalar < 0:
            raise DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage="cleanup")
        if objects > self._data_objects or scalar > self._data_scalar:
            raise DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage="cleanup")
        for domain, count in (("objects", objects), ("scalar", scalar)):
            if not count:
                continue
            if self._cleanup_credit < 1:
                raise DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage="cleanup")
            w, scan = self.used["work"], self.used["scan_copy"]
            obj, held_scalar = self.live["objects"], self.live["scalar"]
            self._cleanup_credit -= 1
            self.live[domain] -= count
            if domain == "objects":
                self._data_objects -= count
                self._cleanup_objects += count
            else:
                self._data_scalar -= count
                self._cleanup_scalar += count
            self._events.append(
                (
                    action,
                    domain,
                    count,
                    self.stage,
                    w,
                    w,
                    scan,
                    scan,
                    obj,
                    self.live["objects"],
                    held_scalar,
                    self.live["scalar"],
                )
            )

    def receipt(self):
        self._running()
        self.enter("receipt")
        count = len(self._events)
        self.debit("work", count + 64)
        self.debit("scan_copy", 8 * (count + 8))
        self.reserve("objects", count + 96)
        self.reserve("scalar", 1024)
        result = DirectStepsReceipt(
            tuple(self.used.items()),
            tuple(self.live.items()),
            tuple(self.peaks.items()),
            tuple(self.caps.items()),
            tuple(self._events),
            self.candidates,
            self.steps,
            self.key_bytes,
            self.carrier_bytes,
        )
        self._receipt_taken = True
        return result

    def completed(self):
        if self.state != "running":
            raise DirectStepsFailure("DIRECT_STEPS_REUSED", stage=self.stage)
        self.state = "completed"

    transferred = completed

    def failed(self):
        if self.state == "running":
            self.state = "failed"


def _active(ledger):
    _require(type(ledger) is DirectStepsLedger)
    ledger._running()


def _triple(key, ledger):
    _require(type(key) is tuple and len(key) == 3, ledger)
    ledger.debit("work", 4)
    for value in key:
        _require(type(value) is str and len(value) <= MAX_BYTES, ledger)
    return key


def _parts(parts, ledger, *, tag=b""):
    """Length-prefixed UTF8 with a prepaid worst-case buffer overlap."""
    _active(ledger)
    _require(type(parts) is tuple and len(parts) <= 4, ledger)
    ledger.debit("work", len(parts) + 1)
    chars = 0
    for value in parts:
        _require(type(value) is str and len(value) <= MAX_BYTES, ledger)
        chars += len(value)
    upper = len(tag) + 8 * len(parts) + 4 * chars
    if upper > 4 * MAX_BYTES + 64:
        raise DirectStepsFailure("DIRECT_STEPS_LIMIT", stage=ledger.stage, domain="scalar")
    ledger.debit("scan_copy", 2 * upper + 32)
    ledger.reserve("objects", 8)
    ledger.reserve("scalar", 3 * upper + 128)
    out = data = result = None
    error = None
    try:
        size = len(tag) + 8 * len(parts)
        for value in parts:
            for character in value:
                point = ord(character)
                _require(not 0xD800 <= point <= 0xDFFF, ledger)
                size += 1 if point < 128 else 2 if point < 2048 else 3 if point < 65536 else 4
        if size > MAX_BYTES:
            raise DirectStepsFailure("DIRECT_STEPS_LIMIT", stage=ledger.stage, domain="scalar")
        ledger.consume_key(size)
        out = bytearray(tag)
        for value in parts:
            data = value.encode("utf-8", errors="strict")
            if len(out) + len(data) + 8 > MAX_BYTES:
                raise DirectStepsFailure("DIRECT_STEPS_LIMIT", stage=ledger.stage, domain="scalar")
            out.extend(len(data).to_bytes(8, "big"))
            out.extend(data)
            data = None
        result = bytes(out)
    except DirectStepsFailure as exc:
        error = DirectStepsFailure(exc.reason, stage=exc.stage, domain=exc.domain)
    except Exception:
        error = DirectStepsFailure(stage=ledger.stage)
    finally:
        out = data = value = None
        retained = 0 if result is None else len(result)
        ledger.discard(objects=8, scalar=3 * upper + 128 - retained)
    if error is not None:
        raise error
    return result


def encode_triple_key(key, ledger):
    """Three 8-byte unsigned lengths followed by exact original UTF8 bytes."""
    _active(ledger)
    return _parts(_triple(key, ledger), ledger)


def _term_identity(term, ledger):
    _require(type(term) is TermInput, ledger)
    ledger.debit("work", 8)
    _require(type(term.kind) is str and type(term.lexical_form) is str, ledger)
    _require(term.datatype_iri is None or type(term.datatype_iri) is str, ledger)
    _require(term.language_raw is None or type(term.language_raw) is str, ledger)
    if term.kind == "iri":
        _require(term.datatype_iri is None and term.language_raw is None, ledger)
        return _parts((term.lexical_form,), ledger, tag=b"\x01")
    _require(term.kind == "literal", ledger)
    language = term.language_raw
    effective = (
        term.datatype_iri
        if term.datatype_iri is not None
        else (_LANG_STRING if language is not None else _XSD_STRING)
    )
    _require(type(effective) is str, ledger)
    lowered = None
    if language is not None:
        # Unicode casefold is not RDF identity; existing identity uses lower().
        ledger.debit("scan_copy", 8 * len(language) + 1)
        ledger.reserve("scalar", 4 * len(language))
        lowered = language.lower()
    core = result = None
    try:
        core = _parts((term.lexical_form, effective), ledger, tag=b"\x02")
        if lowered is None:
            ledger.debit("scan_copy", 2 * len(core) + 1)
            ledger.reserve("scalar", len(core) + 1)
            ledger.consume_key(len(core) + 1)
            result = core + b"\x00"
        else:
            extra = _parts((lowered,), ledger, tag=b"\x01")
            try:
                ledger.debit("scan_copy", len(core) + len(extra))
                ledger.reserve("scalar", len(core) + len(extra))
                ledger.consume_key(len(core) + len(extra))
                result = core + extra
            finally:
                n = 0 if extra is None else len(extra)
                extra = None
                ledger.discard(scalar=n)
        return result
    finally:
        n = 0 if core is None else len(core)
        core = lowered = None
        ledger.discard(scalar=n + (0 if language is None else 4 * len(language)))


def encode_identity_key(records, ledger):
    """Raw RDF identity, distinct from numeric equality and raw lexical source."""
    _active(ledger)
    _require(type(records) is tuple and len(records) == 3, ledger)
    ledger.debit("work", 4)
    for term in records:
        _require(type(term) is TermInput, ledger)
    ledger.reserve("objects", 8)
    parts = []
    out = data = result = None
    held = 0
    try:
        for term in records:
            data = _term_identity(term, ledger)
            held += len(data)
            parts.append(data)
        size = 24 + held
        if size > MAX_BYTES:
            raise DirectStepsFailure("DIRECT_STEPS_LIMIT", stage=ledger.stage, domain="scalar")
        ledger.debit("scan_copy", 3 * size)
        ledger.reserve("scalar", 3 * size)
        ledger.consume_key(size)
        out = bytearray()
        for data in parts:
            out.extend(len(data).to_bytes(8, "big"))
            out.extend(data)
        result = bytes(out)
        return result
    finally:
        size = 0 if out is None else len(out)
        parts = out = data = term = None
        ledger.discard(
            objects=8,
            scalar=held + (0 if size == 0 else 3 * size - (0 if result is None else len(result))),
        )


class _ByteIndex:
    """Exact binary trie; no native hash table for untrusted dynamic keys."""

    def __init__(self, ledger):
        _active(ledger)
        ledger.reserve("objects", 4)
        self.ledger = ledger
        self.root = [None, None, None]
        self.nodes = 1

    def get(self, key):
        _require(type(key) is bytes and len(key) <= MAX_BYTES, self.ledger)
        self.ledger.consume_key(len(key))
        self.ledger.debit("work", 16 * len(key) + 4)
        self.ledger.debit("scan_copy", 2 * len(key))
        node = self.root
        for byte in key:
            for shift in range(7, -1, -1):
                node = node[(byte >> shift) & 1]
                if node is None:
                    return None
        return node[2]

    def put(self, key, value):
        _require(type(key) is bytes and len(key) <= MAX_BYTES, self.ledger)
        self.ledger.consume_key(len(key))
        self.ledger.debit("work", 16 * len(key) + 4)
        self.ledger.debit("scan_copy", 2 * len(key))
        upper = 8 * len(key)
        # Node lists and their zeroed slots are prepaid before the first one.
        self.ledger.debit("work", 4 * upper)
        self.ledger.reserve("objects", 4 * upper)
        node = self.root
        created = 0
        try:
            for byte in key:
                for shift in range(7, -1, -1):
                    side = (byte >> shift) & 1
                    child = node[side]
                    if child is None:
                        child = [None, None, None]
                        node[side] = child
                        self.nodes += 1
                        created += 1
                    node = child
            _require(node[2] is None or node[2] is value, self.ledger)
            node[2] = value
        finally:
            node = child = None
            self.ledger.discard(objects=4 * (upper - created))

    def drop(self):
        count = self.nodes
        self.root = None
        self.nodes = 0
        self.ledger.discard(objects=4 * count)


@dataclass(slots=True)
class _Seed:
    key: tuple
    reference: str | None = None


@dataclass(slots=True)
class _Step:
    ordinal: int
    rule: str
    result: tuple
    left: object
    right: object
    depth: int


class _DirectStepsCapture:
    """Private occurrence observer, never a source of permission or new leaves."""

    def __init__(self, ledger):
        _require(type(ledger) is DirectStepsLedger)
        if ledger.state == "new":
            ledger.begin(stage="capture")
        _active(ledger)
        ledger.reserve("objects", 8)
        self.ledger = ledger
        self.index = _ByteIndex(ledger)
        self.steps = []
        self.seeds = []
        self.candidate_live = 0
        self.finished = False
        self._owned_objects = 8
        self._owned_scalar = 0

    def candidate(self, rule):
        try:
            _active(self.ledger)
            _require(type(rule) is str and rule in RULES, self.ledger)
            if self.ledger.candidates >= MAX_CANDIDATES:
                raise DirectStepsFailure(
                    "DIRECT_STEPS_LIMIT", stage=self.ledger.stage, domain="work"
                )
            self.ledger.debit("work", 8)
            self.ledger.reserve("objects", 4)
            self.ledger.candidates += 1
            self.candidate_live += 1
        except DirectStepsFailure:
            self.drop()
            self.ledger.failed()
            raise

    def end_candidates(self, count):
        try:
            _require(type(count) is int and 0 <= count <= self.candidate_live, self.ledger)
            self.ledger.release("objects", 4 * count)
            self.candidate_live -= count
        except DirectStepsFailure:
            self.drop()
            self.ledger.failed()
            raise

    def _reference(self, key):
        encoded = encode_triple_key(key, self.ledger)
        try:
            result = self.index.get(encoded)
            if result is None:
                self.ledger.reserve("objects", 4)
                self.ledger.reserve("scalar", 4 * len(encoded))
                result = _Seed(key)
                self._owned_objects += 4
                self._owned_scalar += 4 * len(encoded)
                self.seeds.append(result)
                self.index.put(encoded, result)
            return result
        finally:
            n = len(encoded)
            encoded = None
            self.ledger.discard(scalar=n)

    def insert(self, result_key, premise_keys, rule):
        encoded = None
        try:
            _active(self.ledger)
            _require(not self.finished, self.ledger)
            _triple(result_key, self.ledger)
            _require(type(premise_keys) is tuple and len(premise_keys) == 2, self.ledger)
            _require(type(rule) is str and rule in RULES, self.ledger)
            _triple(premise_keys[0], self.ledger)
            _triple(premise_keys[1], self.ledger)
            if len(self.steps) >= MAX_STEPS:
                raise DirectStepsFailure(
                    "DIRECT_STEPS_LIMIT", stage=self.ledger.stage, domain="work"
                )
            encoded = encode_triple_key(result_key, self.ledger)
            _require(self.index.get(encoded) is None, self.ledger)
            left = self._reference(premise_keys[0])
            right = self._reference(premise_keys[1])
            self.ledger.debit("work", 32)
            self.ledger.reserve("objects", 12)
            self.ledger.reserve("scalar", 4 * len(encoded))
            ordinal = len(self.steps)
            depth = 1 + max(
                left.depth if type(left) is _Step else 0, right.depth if type(right) is _Step else 0
            )
            step = _Step(ordinal, rule, result_key, left, right, depth)
            self._owned_objects += 12
            self._owned_scalar += 4 * len(encoded)
            self.steps.append(step)
            self.index.put(encoded, step)
            self.ledger.steps += 1
        except DirectStepsFailure:
            self.drop()
            self.ledger.failed()
            raise
        finally:
            n = 0 if encoded is None else len(encoded)
            encoded = left = right = step = None
            self.ledger.discard(scalar=n)

    def link_seed(self, key, reference):
        encoded = None
        try:
            _active(self.ledger)
            _require(not self.finished, self.ledger)
            _triple(key, self.ledger)
            _leaf_id(reference, self.ledger)
            self.ledger.enter("link")
            encoded = encode_triple_key(key, self.ledger)
            value = self.index.get(encoded)
            if value is None:
                # A seed may never be a premise of an accepted new step.
                value = self._reference(key)
            _require(type(value) is _Seed and value.reference is None, self.ledger)
            self.ledger.debit("scan_copy", 4 * len(reference) + 1)
            self.ledger.reserve("scalar", 4 * len(reference))
            self._owned_scalar += 4 * len(reference)
            value.reference = reference
        except DirectStepsFailure:
            self.drop()
            self.ledger.failed()
            raise
        finally:
            n = 0 if encoded is None else len(encoded)
            encoded = value = None
            self.ledger.discard(scalar=n)

    def finish(self):
        result = output = item = refs = None
        try:
            _active(self.ledger)
            _require(not self.finished and self.candidate_live == 0, self.ledger)
            _require(len(self.steps) <= MAX_STEPS - len(self.seeds), self.ledger)
            self.ledger.enter("encode")
            self.ledger.debit("work", len(self.seeds) + 16 * len(self.steps) + 4)
            for seed in self.seeds:
                _require(type(seed.reference) is str, self.ledger)
            self.ledger.reserve("objects", 48 * len(self.steps) + 16)
            # The carrier still references original result strings and leaf IDs
            # after drop() removes the private capture. Give it its own holding.
            self.ledger.reserve("scalar", self._owned_scalar)
            output = [None] * len(self.steps)
            for pos, item in enumerate(self.steps):
                refs = tuple(
                    {"kind": "step", "ordinal": ref.ordinal}
                    if type(ref) is _Step
                    else {"kind": "leaf", "reference": ref.reference}
                    for ref in (item.left, item.right)
                )
                output[pos] = {
                    "ordinal": item.ordinal,
                    "rule": item.rule,
                    "result": item.result,
                    "premises": refs,
                    "depth": item.depth,
                }
            result = {"format": VERSION, "steps": tuple(output)}
            self.finished = True
            return result
        except DirectStepsFailure:
            self.drop()
            self.ledger.failed()
            raise
        finally:
            output = item = refs = seed = None

    def drop(self):
        # Each private reference actually dies before its reserved holding drops.
        if getattr(self, "index", None) is not None:
            self.index.drop()
        self.index = self.steps = self.seeds = None
        held = getattr(self, "candidate_live", 0)
        self.candidate_live = 0
        obj = getattr(self, "_owned_objects", 0) + 4 * held
        scalar = getattr(self, "_owned_scalar", 0)
        self._owned_objects = self._owned_scalar = 0
        if getattr(self, "ledger", None) is not None:
            self.ledger.discard(objects=obj, scalar=scalar)


@dataclass(slots=True)
class _SeedGroup:
    identity: bytes
    seen: bool = False
    leaf: object = None


@dataclass(slots=True)
class _Leaf:
    reference: str
    key: tuple
    ordinal: int
    dp: tuple


@dataclass(slots=True)
class _ValidatedStep:
    ordinal: int
    result: tuple
    depth: int
    dp: tuple


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    seed_count: int
    step_count: int
    max_depth: int


def _object(value, keys, ledger):
    _require(type(value) is dict and len(value) == len(keys), ledger)
    ledger.debit("work", len(keys) * len(keys) + 2)
    ledger.debit("scan_copy", 64 * len(keys) * len(keys) + 1)
    for key in value:
        _require(type(key) is str and key in keys, ledger)
    return value


def _sequence(value, ledger, *, bound=MAX_STEPS, tuple_only=False):
    _require(
        type(value) is tuple if tuple_only else type(value) is tuple or type(value) is list, ledger
    )
    _require(len(value) <= bound, ledger)
    ledger.debit("work", len(value) + 1)
    return value


def _integer(value, ledger, *, maximum=MAX_STEPS):
    _require(type(value) is int and 0 <= value <= maximum, ledger)
    ledger.debit("work", 1)
    return value


def _equal_strings(left, right, ledger):
    _require(type(left) is str and type(right) is str, ledger)
    ledger.debit("scan_copy", 4 * (len(left) + len(right)) + 1)
    return left == right


def _same_key(left, right, ledger):
    _triple(left, ledger)
    _triple(right, ledger)
    for pos in range(3):
        if not _equal_strings(left[pos], right[pos], ledger):
            return False
    return True


def _template(rule, left, right, result, ledger):
    """Four fixed local comparisons, never candidate generation or closure."""
    _triple(left, ledger)
    _triple(right, ledger)
    _triple(result, ledger)
    _require(type(rule) is str and rule in RULES, ledger)
    ledger.debit("work", 32)
    ledger.reserve("objects", 12)
    expected = None
    try:
        if rule == RULES[0]:
            _require(_equal_strings(left[1], _RDF_TYPE, ledger), ledger)
            _require(_equal_strings(right[1], _SUBCLASS, ledger), ledger)
            _require(_equal_strings(left[2], right[0], ledger), ledger)
            expected = (left[0], _RDF_TYPE, right[2])
        elif rule == RULES[1]:
            _require(_equal_strings(left[1], _SUBCLASS, ledger), ledger)
            _require(_equal_strings(right[1], _SUBCLASS, ledger), ledger)
            _require(_equal_strings(left[2], right[0], ledger), ledger)
            expected = (left[0], _SUBCLASS, right[2])
        elif rule == RULES[2]:
            _require(_equal_strings(left[1], _DOMAIN, ledger), ledger)
            _require(_equal_strings(left[0], right[1], ledger), ledger)
            expected = (right[0], _RDF_TYPE, left[2])
        else:
            _require(_equal_strings(left[1], _RANGE, ledger), ledger)
            _require(_equal_strings(left[0], right[1], ledger), ledger)
            # Original range inserts only URIRef subjects, not literal N3.
            ledger.debit("scan_copy", 4 * len(right[2]) + 2)
            _require(right[2].startswith("<") and right[2].endswith(">"), ledger)
            expected = (right[2], _RDF_TYPE, left[2])
        _require(_same_key(expected, result, ledger), ledger)
    finally:
        expected = None
        ledger.discard(objects=12)


def _union(left, right, ledger):
    """Sorted ordinal DP union; charges every read/copy, not exponential paths."""
    _require(type(left) is tuple and type(right) is tuple, ledger)
    count = len(left) + len(right)
    ledger.debit("work", 8 * count + 16)
    ledger.debit("scan_copy", 24 * count + 16)
    reservation = 3 * count + 8
    ledger.reserve("objects", reservation)
    builder = result = None
    try:
        builder = [None] * count
        i = j = used = 0
        while i < len(left) or j < len(right):
            if j == len(right) or i < len(left) and left[i] < right[j]:
                item = left[i]
                i += 1
            elif i == len(left) or right[j] < left[i]:
                item = right[j]
                j += 1
            else:
                item = left[i]
                i += 1
                j += 1
            builder[used] = item
            used += 1
        result = tuple(builder[:used])
        return result
    finally:
        retained = 0 if result is None else len(result) + 1
        builder = item = None
        ledger.discard(objects=reservation - retained)


def _lookup(index, key, ledger):
    encoded = encode_triple_key(key, ledger)
    try:
        return index.get(encoded)
    finally:
        count = len(encoded)
        encoded = None
        ledger.discard(scalar=count)


def _put_key(index, key, value, ledger):
    encoded = encode_triple_key(key, ledger)
    try:
        index.put(encoded, value)
    finally:
        count = len(encoded)
        encoded = None
        ledger.discard(scalar=count)


def _leaf_id(reference, ledger):
    _require(type(reference) is str and len(reference) == 74, ledger)
    ledger.debit("scan_copy", 4 * len(reference) + 128)
    _require(reference.startswith("i05-proof:"), ledger)
    for pos in range(10, 74):
        char = reference[pos]
        _require("0" <= char <= "9" or "a" <= char <= "f", ledger)
    return reference


def _reference_key(reference, ledger):
    _leaf_id(reference, ledger)
    return _parts((reference,), ledger, tag=b"R")


def _lookup_reference(index, reference, ledger):
    encoded = _reference_key(reference, ledger)
    try:
        return index.get(encoded)
    finally:
        count = len(encoded)
        encoded = None
        ledger.discard(scalar=count)


def _put_reference(index, reference, value, ledger):
    encoded = _reference_key(reference, ledger)
    try:
        index.put(encoded, value)
    finally:
        count = len(encoded)
        encoded = None
        ledger.discard(scalar=count)


def validate_direct_steps(carrier, *, proof_leaves, rdfs, rdfs_evidence, seed_entries, ledger):
    """Validate one supplied witness DAG, not the global first-witness policy.

    The caller has already validated the actual structured records, complete
    native profile and original leaf IDs. Seed entries are independently built
    from those records using the original formatter, never supplied by payload.
    """
    _active(ledger)
    ledger.enter("restore")
    identity = representatives = references = results = evidence = steps_index = None
    groups = leaves = validated = None
    summary = error = None
    owned_objects = owned_scalar = 0
    item = group = leaf = row = step = left = right = dp = None
    seen = None
    try:
        _object(carrier, ("format", "steps"), ledger)
        _require(type(carrier["format"]) is str and carrier["format"] == VERSION, ledger)
        steps = _sequence(carrier["steps"], ledger, tuple_only=True)
        _sequence(proof_leaves, ledger)
        _sequence(rdfs, ledger)
        _sequence(rdfs_evidence, ledger)
        _sequence(seed_entries, ledger, bound=100_000)
        _require(len(steps) == len(rdfs) == len(rdfs_evidence), ledger)
        _require(len(steps) <= MAX_STEPS - len(proof_leaves), ledger)
        ledger.reserve("objects", len(seed_entries) + len(proof_leaves) + len(steps) + 32)
        owned_objects += len(seed_entries) + len(proof_leaves) + len(steps) + 32
        groups, leaves, validated = [], [], []
        identity, representatives = _ByteIndex(ledger), _ByteIndex(ledger)
        references, results = _ByteIndex(ledger), _ByteIndex(ledger)
        evidence, steps_index = _ByteIndex(ledger), _ByteIndex(ledger)
        for item in seed_entries:
            _require(type(item) is tuple and len(item) == 2, ledger)
            identity_bytes, representative = item
            _require(type(identity_bytes) is bytes and len(identity_bytes) <= MAX_BYTES, ledger)
            _triple(representative, ledger)
            ledger.debit("work", 16)
            group = identity.get(identity_bytes)
            if group is None:
                ledger.reserve("objects", 8)
                ledger.reserve("scalar", len(identity_bytes))
                owned_objects += 8
                owned_scalar += len(identity_bytes)
                group = _SeedGroup(identity_bytes)
                groups.append(group)
                identity.put(identity_bytes, group)
            prior = _lookup(representatives, representative, ledger)
            _require(prior is None or prior is group, ledger)
            if prior is None:
                _put_key(representatives, representative, group, ledger)
        for item in proof_leaves:
            _object(item, ("reference", "triple"), ledger)
            key, reference = item["triple"], item["reference"]
            _triple(key, ledger)
            _leaf_id(reference, ledger)
            group = _lookup(representatives, key, ledger)
            _require(type(group) is _SeedGroup and not group.seen, ledger)
            _require(_lookup_reference(references, reference, ledger) is None, ledger)
            ledger.reserve("objects", 12)
            ledger.reserve("scalar", 4 * len(reference) + 128)
            owned_objects += 12
            owned_scalar += 4 * len(reference) + 128
            ordinal = len(leaves)
            leaf = _Leaf(reference, key, ordinal, (ordinal,))
            leaves.append(leaf)
            group.seen = True
            group.leaf = leaf
            _put_reference(references, reference, leaf, ledger)
        ledger.debit("work", len(groups) + 1)
        for group in groups:
            _require(group.seen, ledger)
        for key in rdfs:
            _triple(key, ledger)
            _require(_lookup(results, key, ledger) is None, ledger)
            _require(_lookup(representatives, key, ledger) is None, ledger)
            _put_key(results, key, True, ledger)
        for item in rdfs_evidence:
            _object(item, ("result", "basis", "proofLeaves"), ledger)
            key = item["result"]
            _triple(key, ledger)
            _require(_lookup(results, key, ledger) is True, ledger)
            _require(_lookup(evidence, key, ledger) is None, ledger)
            _sequence(item["basis"], ledger)
            _sequence(item["proofLeaves"], ledger)
            _put_key(evidence, key, item, ledger)
        max_depth = 0
        for pos, step in enumerate(steps):
            _object(step, ("ordinal", "rule", "result", "premises", "depth"), ledger)
            _require(_integer(step["ordinal"], ledger) == pos, ledger)
            depth = _integer(step["depth"], ledger)
            rule, key = step["rule"], step["result"]
            _require(type(rule) is str and rule in RULES, ledger)
            _triple(key, ledger)
            _sequence(step["premises"], ledger, bound=2, tuple_only=True)
            _require(len(step["premises"]) == 2, ledger)
            _require(_lookup(results, key, ledger) is True, ledger)
            _require(_lookup(steps_index, key, ledger) is None, ledger)
            row = _lookup(evidence, key, ledger)
            _require(type(row) is dict, ledger)
            left = right = None
            for side, ref in enumerate(step["premises"]):
                _require(type(ref) is dict and len(ref) == 2, ledger)
                ledger.debit("work", 16)
                ledger.debit("scan_copy", 256)
                for name in ref:
                    _require(type(name) is str and name in ("kind", "reference", "ordinal"), ledger)
                _require("kind" in ref and type(ref["kind"]) is str, ledger)
                if ref["kind"] == "leaf":
                    _object(ref, ("kind", "reference"), ledger)
                    value = _lookup_reference(references, ref["reference"], ledger)
                    _require(type(value) is _Leaf, ledger)
                else:
                    _object(ref, ("kind", "ordinal"), ledger)
                    _require(ref["kind"] == "step", ledger)
                    previous = _integer(ref["ordinal"], ledger)
                    _require(previous < pos, ledger)
                    value = validated[previous]
                if side == 0:
                    left = value
                else:
                    right = value
            left_depth = left.depth if type(left) is _ValidatedStep else 0
            right_depth = right.depth if type(right) is _ValidatedStep else 0
            _require(depth == 1 + max(left_depth, right_depth), ledger)
            _template(
                rule,
                left.result if type(left) is _ValidatedStep else left.key,
                right.result if type(right) is _ValidatedStep else right.key,
                key,
                ledger,
            )
            dp = _union(left.dp, right.dp, ledger)
            owned_objects += len(dp) + 1
            _require(len(row["proofLeaves"]) == len(row["basis"]) == len(dp), ledger)
            # Per-step bounded ordinal masks avoid hash/set or path expansion.
            ledger.debit("work", 8 * len(leaves) + 8 * len(dp) + 16)
            ledger.debit("scan_copy", 2 * len(leaves) + 16 * len(dp))
            ledger.reserve("scalar", 2 * len(leaves))
            ledger.reserve("objects", 4)
            owned_objects += 4
            seen = bytearray(len(leaves))
            for ref in row["proofLeaves"]:
                leaf = _lookup_reference(references, ref, ledger)
                _require(type(leaf) is _Leaf and not seen[leaf.ordinal], ledger)
                seen[leaf.ordinal] = 1
            for index in dp:
                _require(seen[index] == 1, ledger)
                seen[index] = 0
            _require(not any(seen), ledger)
            for basis_key in row["basis"]:
                _triple(basis_key, ledger)
                group = _lookup(representatives, basis_key, ledger)
                _require(type(group) is _SeedGroup, ledger)
                # The saved leaf, not an arbitrary alias, defines the basis.
                candidate = group.leaf
                _require(type(candidate) is _Leaf, ledger)
                _require(_same_key(candidate.key, basis_key, ledger), ledger)
                matched = candidate.ordinal
                _require(not seen[matched], ledger)
                seen[matched] = 1
            for index in dp:
                _require(seen[index] == 1, ledger)
            seen = None
            ledger.discard(scalar=2 * len(leaves))
            ledger.discard(objects=4)
            owned_objects -= 4
            ledger.reserve("objects", 12)
            owned_objects += 12
            item = _ValidatedStep(pos, key, depth, dp)
            validated.append(item)
            _put_key(steps_index, key, item, ledger)
            max_depth = max(max_depth, depth)
        # Equal unique cardinality + every result member checked above gives
        # exact coverage; no enumeration of absent witnesses or closure replay.
        ledger.debit("work", 16)
        ledger.reserve("objects", 8)
        summary = ValidationSummary(len(leaves), len(steps), max_depth)
    except DirectStepsFailure as exc:
        error = DirectStepsFailure(exc.reason, stage=exc.stage, domain=exc.domain)
    except Exception:
        error = DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage=ledger.stage)
    finally:
        for index in (identity, representatives, references, results, evidence, steps_index):
            if index is not None:
                index.drop()
        identity = representatives = references = results = evidence = steps_index = None
        groups = leaves = validated = None
        item = group = leaf = row = step = left = right = dp = None
        seen = index = candidate = matched = value = ref = None
        identity_bytes = representative = key = reference = basis_key = steps = None
        carrier = proof_leaves = rdfs = rdfs_evidence = seed_entries = None
        ledger.discard(objects=owned_objects, scalar=owned_scalar)
        if error is not None:
            summary = None
            ledger.failed()
    if error is not None:
        raise error
    return summary


@dataclass(frozen=True, slots=True)
class RootRef:
    kind: str
    reference: str | None = None
    ordinal: int | None = None
    firing_index: int | None = None
    head_index: int | None = None


def locate_roots(entries, target_keys, ledger):
    """Locate all already validated refs. No permission filter or new inference."""
    _active(ledger)
    ledger.enter("roots")
    _sequence(entries, ledger, bound=300_000, tuple_only=True)
    _sequence(target_keys, ledger, bound=100_000, tuple_only=True)
    index = None
    output = result = error = None
    held = 0
    try:
        index = _ByteIndex(ledger)
        ledger.reserve("objects", 2 * len(entries) + 16)
        held = 2 * len(entries) + 16
        for entry in entries:
            _require(type(entry) is tuple and len(entry) == 2, ledger)
            key, ref = entry
            _triple(key, ledger)
            _require(type(ref) is RootRef and type(ref.kind) is str, ledger)
            _require(ref.kind in ("leaf", "step", "ruleHead"), ledger)
            ledger.debit("work", 16)
            if ref.kind == "leaf":
                _leaf_id(ref.reference, ledger)
                _require(ref.ordinal is ref.firing_index is ref.head_index is None, ledger)
            elif ref.kind == "step":
                _integer(ref.ordinal, ledger)
                _require(ref.reference is ref.firing_index is ref.head_index is None, ledger)
            else:
                _integer(ref.firing_index, ledger)
                _integer(ref.head_index, ledger)
                _require(ref.reference is ref.ordinal is None, ledger)
            refs = _lookup(index, key, ledger)
            if refs is None:
                refs = []
                _put_key(index, key, refs, ledger)
            ledger.debit("work", 2)
            refs.append(ref)
        ledger.reserve("objects", 16)
        held += 16
        output = []
        for key in target_keys:
            _triple(key, ledger)
            refs = _lookup(index, key, ledger)
            if refs is not None:
                ledger.debit("work", len(refs) + 1)
                ledger.reserve("objects", 2 * len(refs))
                held += 2 * len(refs)
                output.extend(refs)
        ledger.debit("scan_copy", 8 * len(output))
        result = tuple(output)
        return result
    except DirectStepsFailure as exc:
        error = DirectStepsFailure(exc.reason, stage=exc.stage, domain=exc.domain)
    except Exception:
        error = DirectStepsFailure("DIRECT_STEPS_INTERNAL", stage=ledger.stage)
    finally:
        if index is not None:
            index.drop()
        index = output = refs = key = ref = entry = entries = target_keys = None
        kept = 0 if result is None else len(result) + 1
        ledger.discard(objects=held - kept)
        if error is not None:
            ledger.failed()
    if error is not None:
        raise error
