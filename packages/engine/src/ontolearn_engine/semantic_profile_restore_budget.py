"""Private restore debit domains, strict wire reader and deterministic key index.

Logical byte/field/limb tickets are not CPU time or Python/OS memory estimates.
No persistent producer authority, filesystem, pickle or ProfileValue constructor.
"""

from contextlib import contextmanager
from hashlib import sha256
from json.decoder import scanstring

RESTORE_BUDGET_VERSION = "i05-profile-restore-budget/1"
RESTORE_CACHE_VERSION = "i05-profile-restore-term-key/1"
KEY_HEADER = b"I05RTK1\x00"
KEY_SEPARATOR = b"I05RKEY1" + b"\x00" * 24
MAX_WIRE_BYTES = 8_388_608
MAX_PREIMAGE_BYTES = 16_777_216
MAX_JSON_DEPTH = 35
MAX_PV_OCCURRENCES = 131_072
MAX_FIRINGS = 1_024

# Only these fixed literal keys may enter a dict. Positional schemas are owned
# by semantic_profile_restore, not inferred from an untrusted recordType.
JSON_KEYS = (
    "format",
    "implementation",
    "reasoning",
    "inputDigest",
    "inputDigestDomain",
    "sourceDigest",
    "definitionsDigest",
    "executionSemanticsVersion",
    "engineVersion",
    "dependencyLockHash",
    "formatVersion",
    "semanticsVersion",
    "profile",
    "rdfs",
    "rules",
    "warnings",
    "evidence",
    "rdfsEvidence",
    "firingGroups",
    "mechanismBatches",
    "definitions",
    "catalog",
    "proofLeaves",
    "termSources",
    "graphBudget",
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
    "classes",
    "object_properties",
    "data_properties",
    "bindings",
    "proof_leaves",
    "index",
    "result",
    "triple",
    "basis",
    "firings",
    "facts",
    "payload",
    "input_bytes",
    "term_bytes",
    "source_bytes",
    "digits",
    "integer_bits",
    "temporary_bits",
    "variables",
    "head_occurrences",
    "trace_items",
    "output_bytes",
    "work",
    "domain",
    "value",
    "language",
    "numerator",
    "denominator",
    "negative_zero",
    "day",
    "second",
    "explicit_offset",
    "is_datetime",
    "section",
    "side",
    "span",
    "rule",
    "firingIndex",
    "headIndex",
    "inputs",
    "term",
    "ordinal",
    "ruleId",
    "definitionOrdinal",
    "disabled",
    "planDigest",
    "batch",
    "originalMatches",
    "limits",
    "budgetLimits",
    "budgetUsage",
    "version",
    "triples",
    "inputTermBytes",
    "sidecarScalarBytes",
    "sidecarTermBytes",
    "entryLimits",
    "entryUsage",
    "usage",
    "integerHex",
    "encoding",
    "bytes",
)
_STAGES = ("entry",) + tuple("A" + str(i) for i in range(1, 17))
_REASONS = (
    "RESTORE_INPUT_INVALID",
    "RESTORE_EXPECTATION_MISSING",
    "RESTORE_EXPECTATION_MISMATCH",
    "RESTORE_LIMIT",
    "RESTORE_INTERNAL",
    "RESTORE_LEDGER_REUSED",
)
_CLASSES = ("input", "expectation", "resource", "internal")
_WORK_DOMAINS = (
    "wire",
    "schema",
    "traversal",
    "integer",
    "copy",
    "cache_query",
    "cache_split",
    "cache_alloc",
    "rule",
    "pv_compare",
    "hash",
)
_LIVE_DOMAINS = (
    "scalar",
    "objects",
    "trie_nodes",
    "trie_slots",
    "opaque_scalar",
    "opaque_objects",
)
_DOMAINS = _WORK_DOMAINS + _LIVE_DOMAINS


class RestoreFailure(Exception):
    """Finite local fields only; never uses an input value as its message."""

    def __init__(
        self,
        reason="RESTORE_INPUT_INVALID",
        classification="input",
        *,
        stage="entry",
        slot=None,
        domain=None,
    ):
        if (
            type(reason) is not str
            or reason not in _REASONS
            or type(classification) is not str
            or classification not in _CLASSES
            or type(stage) is not str
            or stage not in _STAGES
            or (slot is not None and (type(slot) is not int or not 0 <= slot < 100))
            or (domain is not None and (type(domain) is not str or domain not in _DOMAINS))
        ):
            reason, classification, stage, slot, domain = (
                "RESTORE_INTERNAL",
                "internal",
                "entry",
                None,
                None,
            )
        self.reason = reason
        self.classification = classification
        self.stage = stage
        self.slot = slot
        self.domain = domain
        super().__init__(reason)


def reject(
    reason="RESTORE_INPUT_INVALID", classification="input", *, stage="entry", slot=None, domain=None
):
    raise RestoreFailure(reason, classification, stage=stage, slot=slot, domain=domain)


def _integer(value, minimum=0, maximum=None):
    return type(value) is int and value >= minimum and (maximum is None or value <= maximum)


class RestoreLedger:
    """One debit-only logical operation; lower-only test limits, no reset API."""

    def __init__(self, *, overrides=()):
        if type(overrides) is not tuple or len(overrides) > len(_DOMAINS):
            reject()
        checked = []
        for pair in overrides:
            if (
                type(pair) is not tuple
                or len(pair) != 2
                or type(pair[0]) is not str
                or pair[0] not in _DOMAINS
                or not _integer(pair[1])
            ):
                reject()
            if any(pair[0] == name for name, _ in checked):
                reject()
            checked.append(pair)
        self._overrides = tuple(checked)
        self._state = "new"
        self._caps = {}
        self._used = dict.fromkeys(_WORK_DOMAINS, 0)
        self._live = dict.fromkeys(_LIVE_DOMAINS, 0)
        self._peaks = dict.fromkeys(_LIVE_DOMAINS, 0)
        self._prepaid = []
        self._slots = []
        self._opaque_active = False
        self._json_nodes = 0
        self._json_depth = 0
        self._key_total = 0
        self._key_occurrences = 0
        self._cache_roots = 0
        self._B = self._Q = self._N = self._J = self._S = 0

    def begin(self, B, Q, N):
        if self._state != "new":
            reject("RESTORE_LEDGER_REUSED", "expectation")
        self._state = "running"
        if not (
            _integer(B, 0, MAX_WIRE_BYTES)
            and _integer(Q, 0, MAX_PREIMAGE_BYTES)
            and _integer(N, 1, 100)
        ):
            reject("RESTORE_LIMIT", "resource")
        self._B, self._Q, self._N = B, Q, N
        self._J = B + Q
        self._S = B + 64 * MAX_PV_OCCURRENCES
        M, U, J, S = MAX_PV_OCCURRENCES, MAX_PV_OCCURRENCES, self._J, self._S
        caps = {
            "wire": 6 * (B + Q),
            "schema": 4096 * (B + Q + J),
            "traversal": 512 * J + 64 * M + 65536 * N,
            "integer": 2048 * (B + Q),
            "copy": 64 * (B + Q + S) + 65536 * M + 65536 * N,
            "cache_query": 257 * (S + M),
            "cache_split": 512 * U,
            "cache_alloc": 320 * (2 * U + N) + 64 * U + 16 * M,
            "rule": (MAX_FIRINGS + 2 * N + 1) * (101 * B + N) + 65536 * N,
            "pv_compare": 1048576 * M,
            "hash": 32 * B + 8 * Q + S + 32 * M + 65536 * N,
            "scalar": 16 * (B + Q + S + 65536 * M + 65536 * N) + 4096,
            "objects": 8 * J + 16 * M + 2048 * N + 4096,
            "trie_nodes": 2 * U + N,
            "trie_slots": 256 * (2 * U + N),
            "opaque_scalar": 8 * (262144 + 262144) + 2**29,
            "opaque_objects": 8 * (262144 + 262144) + 4096,
        }
        for name, limit in self._overrides:
            if limit > caps[name]:
                reject("RESTORE_EXPECTATION_MISMATCH", "expectation", domain=name)
            caps[name] = limit
        self._caps = caps
        self._slots = ["new"] * N
        # All raw blobs and fixed context already exist at entry; they still
        # consume logical holding reservations throughout this operation.
        self.reserve("scalar", B + Q)
        self.charge("traversal", 17 * N)
        self.reserve("objects", 17 * N)

    def _running(self):
        if self._state != "running":
            reject("RESTORE_LEDGER_REUSED", "expectation")

    def limit(self, domain):
        if type(domain) is not str or domain not in self._caps:
            reject("RESTORE_INTERNAL", "internal")
        return self._caps[domain]

    def charge(self, domain, amount=1, *, stage="entry"):
        self._running()
        if type(domain) is not str or domain not in _WORK_DOMAINS or not _integer(amount):
            reject("RESTORE_INTERNAL", "internal")
        used = self._used[domain] + amount
        if used > self._caps[domain]:
            reject("RESTORE_LIMIT", "resource", stage=stage, domain=domain)
        self._used[domain] = used

    def visit(self, amount=1, *, stage="A2"):
        self.charge("traversal", amount, stage=stage)

    def reserve(self, domain, amount=1, *, stage="entry"):
        self._running()
        if type(domain) is not str or domain not in _LIVE_DOMAINS or not _integer(amount):
            reject("RESTORE_INTERNAL", "internal")
        live = self._live[domain] + amount
        if live > self._caps[domain]:
            reject("RESTORE_LIMIT", "resource", stage=stage, domain=domain)
        self._live[domain] = live
        self._peaks[domain] = max(self._peaks[domain], live)

    def release(self, domain, amount=1):
        # Cleanup is legal even after a resource failure or terminal status.
        if (
            type(domain) is not str
            or domain not in _LIVE_DOMAINS
            or not _integer(amount)
            or amount > self._live[domain]
        ):
            reject("RESTORE_INTERNAL", "internal")
        self._live[domain] -= amount

    def prepay(self, stage):
        self._running()
        if type(stage) is not str or stage not in _STAGES[1:]:
            reject("RESTORE_INTERNAL", "internal")
        if stage in self._prepaid:
            return
        self.charge("traversal", 32 * self._J, stage=stage)
        # Encoder sorting has only fixed native literal keys; no arbitrary
        # caller comparison. Reserve its fixed-key comparisons as well.
        self.charge("schema", 128 * self._J, stage=stage)
        self.charge("copy", 4 * (self._B + self._Q + self._S), stage=stage)
        self._prepaid.append(stage)

    @contextmanager
    def opaque(self):
        self._running()
        if self._opaque_active:
            reject("RESTORE_INTERNAL", "internal")
        # Reserve the declared full source-derived peak, not the override:
        # a lower test limit must fail rather than shrink the reservation.
        scalar = 8 * (262144 + 262144) + 2**29
        objects = 8 * (262144 + 262144) + 4096
        self.reserve("opaque_scalar", scalar)
        try:
            self.reserve("opaque_objects", objects)
        except BaseException:
            self.release("opaque_scalar", scalar)
            raise
        self._opaque_active = True
        try:
            yield
        finally:
            self._opaque_active = False
            self.release("opaque_objects", objects)
            self.release("opaque_scalar", scalar)

    def start_slot(self, slot):
        self._running()
        if not _integer(slot, 0, self._N - 1) or self._slots[slot] != "new":
            reject("RESTORE_LEDGER_REUSED", "expectation")
        self.charge("traversal", 1)
        self._slots[slot] = "running"

    def complete_slot(self, slot):
        self._running()
        if not _integer(slot, 0, self._N - 1) or self._slots[slot] != "running":
            reject("RESTORE_INTERNAL", "internal")
        self.charge("traversal", 1)
        self._slots[slot] = "success"

    def finish(self, success):
        if type(success) is not bool:
            reject("RESTORE_INTERNAL", "internal")
        if self._state not in ("new", "running"):
            reject("RESTORE_LEDGER_REUSED", "expectation")
        if success and (self._state != "running" or any(s != "success" for s in self._slots)):
            reject("RESTORE_INTERNAL", "internal")
        self._state = "success" if success else "failed"
        if not success:
            self._slots = ["failed"] * len(self._slots)

    def cleanup(self):
        """After the owner actually drops temporaries or transfers the result."""
        if self._opaque_active:
            reject("RESTORE_INTERNAL", "internal")
        for name in _LIVE_DOMAINS:
            self._live[name] = 0

    def record_key(self, length):
        self._running()
        if not _integer(length, 1):
            reject("RESTORE_INTERNAL", "internal")
        if self._key_occurrences + 1 > MAX_PV_OCCURRENCES or self._key_total + length > self._S:
            reject("RESTORE_LIMIT", "resource", stage="A4", domain="cache_query")
        self._key_occurrences += 1
        self._key_total += length

    def new_cache(self):
        self._running()
        if self._cache_roots >= self._N:
            reject("RESTORE_LIMIT", "resource", stage="A4", domain="trie_nodes")
        self._cache_roots += 1

    @property
    def B(self):
        return self._B

    @property
    def Q(self):
        return self._Q

    @property
    def N(self):
        return self._N

    @property
    def J(self):
        return self._J

    @property
    def S(self):
        return self._S

    @property
    def state(self):
        return self._state

    @property
    def caps(self):
        return tuple((name, self._caps[name]) for name in _DOMAINS if name in self._caps)

    @property
    def usage(self):
        return tuple(self._used.items())

    @property
    def live(self):
        return tuple(self._live.items())

    @property
    def peaks(self):
        return tuple(self._peaks.items())

    @property
    def slot_states(self):
        return tuple(self._slots)

    @property
    def json_nodes(self):
        return self._json_nodes

    @property
    def json_depth(self):
        return self._json_depth


def utf8(raw, ledger, *, label="input"):
    """Prepaid UTF8 check; returned text owns a four-byte-per-raw-byte ticket."""
    if type(raw) is not bytes or type(ledger) is not RestoreLedger:
        reject()
    if type(label) is not str or label not in ("payload", "rows", "input", "source"):
        reject("RESTORE_INTERNAL", "internal")
    ledger.charge("wire", len(raw), stage="A1")
    ledger.charge("copy", len(raw), stage="A1")
    ledger.reserve("scalar", 4 * len(raw), stage="A1")
    ledger.reserve("objects", 1, stage="A1")
    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        ledger.release("objects", 1)
        ledger.release("scalar", 4 * len(raw))
        reject(stage="A1")


def release_utf8(raw, ledger):
    ledger.release("objects", 1)
    ledger.release("scalar", 4 * len(raw))


class _Reader:
    """Two passes: no value-string/container construction before lexical gates."""

    def __init__(self, text, ledger, build, label):
        self.text, self.ledger, self.build = text, ledger, build
        self.label = label
        self.pos, self.length = 0, len(text)

    def bad(self):
        reject(stage="A1")

    def space(self):
        while self.pos < self.length and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def node(self, depth):
        if depth > MAX_JSON_DEPTH:
            reject("RESTORE_LIMIT", "resource", stage="A1", domain="traversal")
        if not self.build:
            if self.ledger._json_nodes + 1 > self.ledger.J:
                reject("RESTORE_LIMIT", "resource", stage="A1", domain="traversal")
            self.ledger._json_nodes += 1
            self.ledger._json_depth = max(self.ledger._json_depth, depth)
        else:
            self.ledger.visit(stage="A1")
            self.ledger.reserve("objects", 1, stage="A1")

    def string(self, key=False, field=None):
        self.pos += 1
        start = self.pos
        decoded_bytes = 0
        decoded_chars = 0
        maximum = None
        character_limit = MAX_WIRE_BYTES // 6
        if key:
            maximum = 64
        elif self.label == "rows":
            character_limit = 8192
        elif field in ("reference", "digest", "revision", "text"):
            maximum = 65536
        elif field in (
            "lexical_form",
            "datatype_iri",
            "language_raw",
            "name",
            "rule_id",
            "ruleId",
            "domain",
            "language",
        ):
            maximum = 16384
        elif field == "integerHex":
            maximum = 8195
        elif field == "bytes":
            maximum = 524288
        elif field == "recordType":
            maximum = 64
        while self.pos < self.length:
            c = self.text[self.pos]
            if c == '"':
                end = self.pos
                self.pos += 1
                if (
                    maximum is not None and decoded_bytes > maximum
                ) or decoded_chars > character_limit:
                    reject("RESTORE_LIMIT", "resource", stage="A1", domain="copy")
                if not self.build and not key:
                    return None
                if self.build and not key:
                    # scanstring may allocate now, after the token-length and
                    # Unicode gates completed. UTF8 escape output <= token bytes.
                    self.ledger.charge("copy", end - start, stage="A1")
                    self.ledger.reserve("scalar", 4 * (end - start), stage="A1")
                try:
                    value, stop = scanstring(self.text, start, True)
                except (ValueError, OverflowError):
                    self.bad()
                if stop != self.pos:
                    self.bad()
                return value
            if ord(c) < 32:
                self.bad()
            if c == "\\":
                self.pos += 1
                if self.pos >= self.length:
                    self.bad()
                escape = self.text[self.pos]
                if escape in '"\\/bfnrt':
                    decoded_bytes += 1
                    decoded_chars += 1
                    self.pos += 1
                    continue
                if escape != "u":
                    self.bad()
                code = self.hex4(self.pos + 1)
                self.pos += 5
                if 0xD800 <= code <= 0xDBFF:
                    if self.text[self.pos : self.pos + 2] != "\\u":
                        self.bad()
                    low = self.hex4(self.pos + 2)
                    if not 0xDC00 <= low <= 0xDFFF:
                        self.bad()
                    self.pos += 6
                    code = 0x10000 + ((code - 0xD800) << 10) + low - 0xDC00
                elif 0xDC00 <= code <= 0xDFFF:
                    self.bad()
                decoded_bytes += _width(code)
            else:
                code = ord(c)
                if 0xD800 <= code <= 0xDFFF:
                    self.bad()
                decoded_bytes += _width(code)
                self.pos += 1
            decoded_chars += 1
            if (maximum is not None and decoded_bytes > maximum) or decoded_chars > character_limit:
                reject("RESTORE_LIMIT", "resource", stage="A1", domain="copy")
        self.bad()

    def hex4(self, start):
        if start + 4 > self.length:
            self.bad()
        self.ledger.charge("copy", 4, stage="A1")
        value = 0
        for i in range(start, start + 4):
            c = self.text[i]
            if "0" <= c <= "9":
                digit = ord(c) - 48
            elif "a" <= c <= "f":
                digit = ord(c) - 87
            elif "A" <= c <= "F":
                digit = ord(c) - 55
            else:
                self.bad()
            value = value * 16 + digit
        return value

    def fixed_key(self, value):
        for known in JSON_KEYS:
            self.ledger.charge("schema", len(value) + len(known) + 1, stage="A1")
            if value == known:
                return known
        self.bad()

    def value(self, depth=0, field=None):
        self.space()
        self.node(depth)
        if self.pos >= self.length:
            self.bad()
        c = self.text[self.pos]
        if c == '"':
            return self.string(field=field)
        if c == "{":
            return self.object(depth)
        if c == "[":
            return self.array(depth)
        for token, result in (("null", None), ("true", True), ("false", False)):
            if self.text.startswith(token, self.pos):
                self.pos += len(token)
                return result
        # Native number tokens, including NaN/Infinity, are never in this wire.
        self.bad()

    def object(self, depth):
        self.pos += 1
        self.space()
        keys = []
        result = {} if self.build else None
        if self.pos < self.length and self.text[self.pos] == "}":
            self.pos += 1
            return result
        while True:
            self.space()
            if self.pos >= self.length or self.text[self.pos] != '"' or len(keys) >= 32:
                self.bad()
            self.node(depth + 1)
            key = self.fixed_key(self.string(key=True))
            for prior in keys:
                self.ledger.charge("schema", len(key) + len(prior) + 1, stage="A1")
                if key == prior:
                    self.bad()
            keys.append(key)
            self.space()
            if self.pos >= self.length or self.text[self.pos] != ":":
                self.bad()
            self.pos += 1
            item = self.value(depth + 1, field=key)
            if self.build:
                self.ledger.visit(1, stage="A1")
                self.ledger.reserve("objects", 1, stage="A1")
                result[key] = item
            self.space()
            if self.pos >= self.length:
                self.bad()
            delimiter = self.text[self.pos]
            self.pos += 1
            if delimiter == "}":
                return result
            if delimiter != ",":
                self.bad()

    def array(self, depth):
        self.pos += 1
        self.space()
        result = [] if self.build else None
        if self.pos < self.length and self.text[self.pos] == "]":
            self.pos += 1
            return result
        while True:
            item = self.value(depth + 1)
            if self.build:
                self.ledger.visit(stage="A1")
                self.ledger.reserve("objects", 1, stage="A1")
                result.append(item)
            self.space()
            if self.pos >= self.length:
                self.bad()
            delimiter = self.text[self.pos]
            self.pos += 1
            if delimiter == "]":
                return result
            if delimiter != ",":
                self.bad()

    def read(self):
        result = self.value()
        self.space()
        if self.pos != self.length:
            self.bad()
        return result


def read_json(raw, ledger, *, label="payload"):
    if type(raw) is not bytes or type(ledger) is not RestoreLedger:
        reject()
    text = utf8(raw, ledger, label=label)
    ledger.reserve("objects", 4096, stage="A1")
    ledger.reserve("scalar", 16384, stage="A1")
    try:
        ledger.charge("wire", len(raw), stage="A1")
        _Reader(text, ledger, False, label).read()
        ledger.charge("wire", len(raw), stage="A1")
        return _Reader(text, ledger, True, label).read()
    finally:
        ledger.release("scalar", 16384)
        ledger.release("objects", 4096)
        release_utf8(raw, ledger)


def _width(code):
    if code < 0x80:
        return 1
    if code < 0x800:
        return 2
    if code < 0x10000:
        return 3
    return 4


def canonical_bytes(value, ledger, *, stage, bound=MAX_WIRE_BYTES):
    """Prepay one stage, then delegate the fixed existing canonical writer."""
    if type(ledger) is not RestoreLedger or not _integer(bound, 0, MAX_WIRE_BYTES):
        reject("RESTORE_INTERNAL", "internal")
    bound = min(bound, ledger.B + ledger.Q)
    ledger.prepay(stage)
    ledger.reserve("scalar", 2 * bound, stage=stage)
    ledger.reserve("objects", 4, stage=stage)
    try:
        from ontolearn_engine.semantic_execution import _profile_json_bytes

        with ledger.opaque():
            result = _profile_json_bytes(value)
        if len(result) > bound:
            reject("RESTORE_LIMIT", "resource", stage=stage, domain="copy")
        # Transfer just the returned buffer; its caller drops it or cleanup owns
        # its logical ticket. The temporary full bound is no longer live.
        ledger.release("scalar", 2 * bound - len(result))
        ledger.release("objects", 3)
        return result
    except BaseException:
        ledger.release("scalar", 2 * bound)
        ledger.release("objects", 4)
        raise


def digest(data, ledger, *, stage="entry"):
    if type(data) is not bytes or type(ledger) is not RestoreLedger:
        reject("RESTORE_INTERNAL", "internal")
    ledger.charge("hash", len(data), stage=stage)
    ledger.reserve("scalar", 64, stage=stage)
    ledger.reserve("objects", 1, stage=stage)
    return sha256(data).hexdigest()


def hex_integer(text, ledger, *, stage="A2"):
    if type(text) is not str or type(ledger) is not RestoreLedger:
        reject(stage=stage)
    negative = text.startswith("-")
    start = 3 if negative else 2
    if (
        len(text) < start + 1
        or len(text) > start + 8192
        or text[(1 if negative else 0) : start] != "0x"
    ):
        reject(stage=stage)
    h = len(text) - start
    q = (h + 7) // 8
    ledger.charge("integer", q * (q + 1) + 8 * h + 16, stage=stage)
    for position in range(start, len(text)):
        if text[position] not in "0123456789abcdef":
            reject(stage=stage)
    if (h > 1 and text[start] == "0") or (negative and h == 1 and text[start] == "0"):
        reject(stage=stage)
    ledger.reserve("scalar", 4 * 4096, stage=stage)
    ledger.reserve("objects", 3, stage=stage)
    try:
        value = 0
        for position in range(start, len(text), 8):
            piece = text[position : position + 8]
            value = (value << (4 * len(piece))) | int(piece, 16)
        if negative:
            value = -value
        if value.bit_length() > 32768 or hex(value) != text:
            reject(stage=stage)
        size = max(1, (value.bit_length() + 7) // 8)
    except BaseException:
        ledger.release("scalar", 4 * 4096)
        ledger.release("objects", 3)
        raise
    ledger.release("scalar", 4 * 4096 - size)
    ledger.release("objects", 2)
    return value


def hex_bytes(text, ledger, *, maximum, stage="A2"):
    if (
        type(text) is not str
        or type(ledger) is not RestoreLedger
        or not _integer(maximum, 0, 262144)
    ):
        reject(stage=stage)
    if len(text) % 2 or len(text) // 2 > maximum:
        reject("RESTORE_LIMIT", "resource", stage=stage, domain="copy")
    ledger.charge("copy", len(text) + len(text) // 2, stage=stage)
    for c in text:
        if c not in "0123456789abcdef":
            reject(stage=stage)
    size = len(text) // 2
    ledger.reserve("scalar", size, stage=stage)
    ledger.reserve("objects", 1, stage=stage)
    return bytes.fromhex(text)


def _text_size(text, ledger, maximum):
    if type(text) is not str:
        reject(stage="A4")
    ledger.charge("copy", len(text), stage="A4")
    size = 0
    for c in text:
        code = ord(c)
        if 0xD800 <= code <= 0xDFFF:
            reject(stage="A4")
        size += _width(code)
        if size > maximum:
            reject("RESTORE_LIMIT", "resource", stage="A4", domain="copy")
    return size


def term_key(term, ledger):
    """Return a complete versioned key, holding len(key) scalar + one object.

    The caller releases those temporary tickets with release_key after cache
    lookup; a miss independently transfers an ownership reservation to cache.
    """
    from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput

    if type(ledger) is not RestoreLedger or type(term) is not TermInput:
        reject(stage="A4")
    if (
        type(term.kind) is not str
        or type(term.lexical_form) is not str
        or (term.datatype_iri is not None and type(term.datatype_iri) is not str)
        or (term.language_raw is not None and type(term.language_raw) is not str)
    ):
        reject(stage="A4")
    if term.source is not None and type(term.source) is not SourceRecord:
        reject(stage="A4")
    ledger.visit(24, stage="A4")
    ledger.reserve("objects", 8, stage="A4")
    try:
        fields = (term.kind, term.lexical_form, term.datatype_iri, term.language_raw)
        source = term.source
        fields += (
            (None,) * 4
            if source is None
            else (source.reference, source.digest, source.revision, source.text)
        )
        if term.kind not in ("iri", "literal"):
            reject(stage="A4")
        sizes = []
        for i, value in enumerate(fields):
            maximum = 16384 if i < 4 else 65536
            sizes.append(0 if value is None else _text_size(value, ledger, maximum))
        length = 49 + sum(sizes)
        ledger.charge("copy", length + sum(sizes), stage="A4")
        ledger.reserve("scalar", 2 * length, stage="A4")
        ledger.reserve("objects", 2, stage="A4")
        try:
            sink = bytearray(KEY_HEADER)
            sink.append(0 if source is None else 1)
            for value, size in zip(fields, sizes, strict=True):
                sink.append(0 if value is None else 1)
                sink.extend(size.to_bytes(4, "big"))
                if value is not None:
                    sink.extend(value.encode("utf-8", errors="strict"))
            key = bytes(sink)
            if len(key) != length:
                reject("RESTORE_INTERNAL", "internal", stage="A4")
        except BaseException:
            ledger.release("objects", 2)
            ledger.release("scalar", 2 * length)
            raise
        ledger.release("objects", 1)
        ledger.release("scalar", length)
        return key
    finally:
        ledger.release("objects", 8)


def release_bytes(key, ledger):
    if type(key) is not bytes or type(ledger) is not RestoreLedger:
        reject("RESTORE_INTERNAL", "internal")
    ledger.release("objects", 1)
    ledger.release("scalar", len(key))


def release_key(key, ledger):
    release_bytes(key, ledger)


_EMPTY = object()


class _Node:
    """An incoming edge is a view of a retained key, never a bytes slice."""

    __slots__ = ("key", "start", "end", "children", "value", "next")

    def __init__(self, key, start, end, next_node):
        self.key, self.start, self.end = key, start, end
        self.children = []
        self.value = _EMPTY
        self.next = next_node


class TermCache:
    """Per-child strong-value cache with deterministic complete-byte equality.

    Child vectors have at most 256 entries. All resizing is conservatively
    charged for copying the full old vector; no average hash-table assumption.
    """

    def __init__(self, ledger):
        if type(ledger) is not RestoreLedger:
            reject("RESTORE_INTERNAL", "internal")
        ledger.new_cache()
        self.ledger = ledger
        self._head = None
        self._nodes = 0
        self._owned_scalar = 0
        self._owned_objects = 0
        self._closed = False
        self.hits = 0
        self.misses = 0
        self.last_digest = None
        self.root = self._node(b"", 0, 0)

    def _node(self, key, start, end):
        ledger = self.ledger
        ledger.charge("cache_alloc", 320, stage="A4")
        ledger.reserve("trie_nodes", 1, stage="A4")
        try:
            ledger.reserve("trie_slots", 256, stage="A4")
        except BaseException:
            ledger.release("trie_nodes", 1)
            raise
        node = _Node(key, start, end, self._head)
        self._head = node
        self._nodes += 1
        return node

    def _append(self, parent, child):
        if len(parent.children) >= 256:
            reject("RESTORE_INTERNAL", "internal", stage="A4")
        # The <=256 reference copy reserve pays even if Python reuses capacity.
        self.ledger.charge("cache_split", len(parent.children), stage="A4")
        parent.children.append(child)

    def _audit(self, key):
        ledger = self.ledger
        ledger.charge("hash", len(KEY_SEPARATOR) + len(key), stage="A4")
        ledger.reserve("scalar", 64, stage="A4")
        try:
            ledger.reserve("objects", 1, stage="A4")
        except BaseException:
            ledger.release("scalar", 64)
            raise
        try:
            h = sha256(KEY_SEPARATOR)
            h.update(key)
            result = h.hexdigest()
        except BaseException:
            ledger.release("objects", 1)
            ledger.release("scalar", 64)
            raise
        prior = self.last_digest
        self.last_digest = result
        if prior is None:
            self._owned_scalar += 64
            self._owned_objects += 1
        else:
            ledger.release("objects", 1)
            ledger.release("scalar", 64)

    def _new_value(self, key, factory):
        # Reserve the complete value before canonical parse can issue it.
        self.ledger.charge("cache_alloc", 64, stage="A4")
        scalar = len(key) + 65536
        self.ledger.reserve("scalar", scalar, stage="A4")
        try:
            self.ledger.reserve("objects", 16, stage="A4")
        except BaseException:
            self.ledger.release("scalar", scalar)
            raise
        self._owned_scalar += scalar
        self._owned_objects += 16
        value = factory()
        self.misses += 1
        return value

    def get_or_insert(self, key, factory):
        if self._closed or type(key) is not bytes or not key:
            reject("RESTORE_INTERNAL", "internal", stage="A4")
        ledger = self.ledger
        ledger.record_key(len(key))
        ledger.charge("cache_alloc", 16, stage="A4")
        ledger.charge("cache_query", 1, stage="A4")
        self._audit(key)
        node = self.root
        position = 0
        while True:
            if position == len(key):
                if node.value is not _EMPTY:
                    self.hits += 1
                    return node.value
                value = self._new_value(key, factory)
                node.value = value
                return value
            child_index, child = -1, None
            for index, candidate in enumerate(node.children):
                ledger.charge("cache_query", 1, stage="A4")
                if candidate.key[candidate.start] == key[position]:
                    child_index, child = index, candidate
                    break
            if child is None:
                value = self._new_value(key, factory)
                leaf = self._node(key, position, len(key))
                leaf.value = value
                self._append(node, leaf)
                return value
            span = min(len(key) - position, child.end - child.start)
            ledger.charge("cache_query", span, stage="A4")
            matched = 0
            while matched < span and key[position + matched] == child.key[child.start + matched]:
                matched += 1
            if matched == child.end - child.start:
                position += matched
                node = child
                continue
            if not matched:
                reject("RESTORE_INTERNAL", "internal", stage="A4")
            value = self._new_value(key, factory)
            middle = self._node(key, position, position + matched)
            child.start += matched
            self._append(middle, child)
            if position + matched == len(key):
                middle.value = value
            else:
                leaf = self._node(key, position + matched, len(key))
                leaf.value = value
                self._append(middle, leaf)
            node.children[child_index] = middle
            return value

    def clear(self):
        """Drop actual references without spending any potentially exhausted pool.

        The linked allocation chain avoids recursion or an unbounded flat-list
        growth/copy. Its <=2U+N node/edge cleanups are covered by each node's
        prepaid 64 metadata units and each miss's 64 update units.
        """
        if self._closed:
            return
        self.root = None
        current = self._head
        self._head = None
        while current is not None:
            following = current.next
            current.next = None
            current.children.clear()
            current.value = _EMPTY
            current.key = b""
            current = following
        self.last_digest = None
        ledger = self.ledger
        ledger.release("trie_nodes", self._nodes)
        ledger.release("trie_slots", self._nodes * 256)
        ledger.release("scalar", self._owned_scalar)
        ledger.release("objects", self._owned_objects)
        self._nodes = self._owned_scalar = self._owned_objects = 0
        self._closed = True
