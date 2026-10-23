"""Finite helper definitions. Not run in the SOURCE-only window.

The authenticated-material double does not attest real Store authentication,
physical cost, owned worker or IPC. This file contains no real Store/worker
integration case; a future separate supplier/runtime ticket would be required.
"""

import json
from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
from ontolearn_engine.job_store import JobFault, JobStore, fault
from ontolearn_engine.project.query_presentation import describe, rows_page, text_page, typed_cell
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest

ROOT = Path(__file__).resolve().parents[3]
DATA = json.loads((ROOT / "packages/contracts/v2/fixtures.json").read_text())["queryConsumer"]
S = DATA["samples"]
LIMITS = DATA["service"][0]["case"]["limits"]


class Ticket:
    """Explicit test-only prepaid scope; no physical-cost grant or release claim."""

    def __init__(self):
        self.fees, self.values = [], []

    def check(self, store):
        pass

    def pay(self, stage, **fees):
        self.fees.append((stage, fees))

    def deliver(self, value):
        self.values.append(value)
        return value


class MaterialDouble:
    contract = CONTRACT
    _cursor = JobStore._cursor

    def __init__(self):
        self.metadata = deepcopy(S["descriptor"]["metadata"])
        self.payload = {
            "queryText": S["draft"]["sparql"],
            "inputProjectRevision": 1,
            "inputSelection": "current",
            "query": {"type": "SELECT", "variables": ["s"], "rows": [["<urn:s>"], ["<urn:s>"]]},
        }
        self.context = {
            "snapshot": {
                "state": {
                    "definitions": [
                        {"id": "Q1", "layer": "query", "payload": canonical(S["storedDefinition"])}
                    ]
                }
            }
        }
        self.records = {}
        self._db = SimpleNamespace(execute=self.execute)
        self.now = 1000

    def _valid(self, name, value):
        if not CONTRACT.validate(name, value):
            fault("INVALID_REQUEST", field="params")

    def _read(self):
        return nullcontext()

    def _transaction(self):
        return nullcontext()

    def semantic_result(self, project, result):
        assert project == self.metadata["projectId"] and result == self.metadata["resultId"]
        return self.metadata, self.payload

    def job_context(self, job):
        assert job == self.metadata["jobId"]
        return self.context

    def now_ms(self):
        return self.now

    def execute(self, statement, params):
        assert statement == "SELECT * FROM job_cursors WHERE id=?"
        return SimpleNamespace(fetchone=lambda: self.records.get(params[0]))

    def _new_cursor(self, kind, binding, size, position):
        exact = (kind, canonical(binding), size, canonical(position))
        for token, row in self.records.items():
            if row["exact"] == exact:
                return token
        token = "00000000-0000-4000-8000-" + str(len(self.records) + 80).zfill(12)
        self.records[token] = {
            "id": token,
            "kind": kind,
            "binding": canonical(binding),
            "size": size,
            "position": canonical(position),
            "expires": 2000,
            "exact": exact,
        }
        return token


def header(store, ticket=None):
    return describe(
        store,
        {"projectId": store.metadata["projectId"], "resultId": store.metadata["resultId"]},
        LIMITS,
        ticket or Ticket(),
    )


def params(store, descriptor=None, size=2):
    return {"binding": (descriptor or header(store))["identity"], "pageSize": size, "cursor": None}


@pytest.mark.parametrize("case", DATA["service"], ids=lambda c: c["name"])
def test_seven_service_policies_use_actual_cursor_or_projection(case):
    store, ticket = MaterialDouble(), Ticket()
    spec, name = case["case"], case["name"]
    if "L2 valid stored" in name:
        store.payload["query"]["variables"] = ["v" * 129]
        with pytest.raises(JobFault) as error:
            header(store, ticket)
    else:
        store.payload["query"]["rows"] = deepcopy(spec["rawRows"])
        if "ASK rows" in name:
            store.payload["query"] = {"type": "ASK", "value": False}
        desc = header(store, ticket)
        request = params(store, desc, case["request"]["params"]["pageSize"])
        original = spec["cursorRecord"]
        if case["request"]["params"]["cursor"] is not None:
            token = original["id"]
            position = (
                {"nextUtf8Byte": 0} if original["kind"] == "query-text-v1" else original["position"]
            )
            store.records[token] = {
                "kind": original["kind"],
                "binding": canonical(desc["identity"]),
                "size": original["size"],
                "position": canonical(position),
                "expires": original["expires"],
            }
            request["cursor"] = token
        with pytest.raises(JobFault) as error:
            rows_page(store, request, spec["limits"], ticket)
    assert error.value.code == case["expectedCode"]
    assert error.value.params == case["expectedParams"]
    assert CONTRACT.matches_query_consumer_response(case["request"], case["response"])


@pytest.mark.parametrize("count", [0, 1, 2])
def test_select_zero_columns_preserves_empty_binding_cardinality(count):
    store, ticket = MaterialDouble(), Ticket()
    store.payload["query"] = {"type": "SELECT", "variables": [], "rows": [[] for _ in range(count)]}
    desc = header(store, ticket)
    assert desc["query"] == {"kind": "SELECT", "columns": [], "rowCount": count}
    page = rows_page(store, params(store, desc), LIMITS, ticket)
    assert [r["cells"] for r in page["rows"]] == [[] for _ in range(count)]
    assert page["nextCursor"] is None


@pytest.mark.parametrize("value", [False, True])
def test_ask_boolean_is_not_select_empty(value):
    store = MaterialDouble()
    store.payload["query"] = {"type": "ASK", "value": value}
    assert header(store)["query"] == {"kind": "ASK", "value": value}
    with pytest.raises(JobFault) as error:
        rows_page(store, params(store), LIMITS, Ticket())
    assert error.value.code == "INVALID_STATE"


@pytest.mark.parametrize("name", ["x" * 128, "😀" * 128])
def test_column_name_l2_counts_scalars_not_utf16(name):
    store = MaterialDouble()
    store.payload["query"]["variables"] = [name]
    assert header(store)["query"]["columns"][0]["name"] == name


@pytest.mark.parametrize(
    "name,code",
    [
        ("x" * 129, "UNSUPPORTED_CAPABILITY"),
        ("😀" * 129, "UNSUPPORTED_CAPABILITY"),
        ("\ud800", "INVALID_STATE"),
    ],
)
def test_column_name_over_policy_or_invalid_scalar(name, code):
    store = MaterialDouble()
    store.payload["query"]["variables"] = [name]
    with pytest.raises(JobFault) as error:
        header(store)
    assert error.value.code == code


@pytest.mark.parametrize("text", ["x" * 65536, "😀" * 65536])
def test_executed_text_l2_boundary_manifest(text):
    store = MaterialDouble()
    store.payload["queryText"] = text
    desc = header(store)
    assert desc["executedText"]["unicodeScalars"] == 65536
    assert desc["executedText"]["sha256"] == __import__("hashlib").sha256(text.encode()).hexdigest()


@pytest.mark.parametrize(
    "text,code",
    [
        ("x" * 65537, "UNSUPPORTED_CAPABILITY"),
        ("😀" * 65537, "UNSUPPORTED_CAPABILITY"),
        ("\udfff", "INVALID_STATE"),
    ],
)
def test_executed_text_over_policy_or_invalid_scalar(text, code):
    store = MaterialDouble()
    store.payload["queryText"] = text
    with pytest.raises(JobFault) as error:
        header(store)
    assert error.value.code == code


def test_text_pages_scalar_boundaries_retry_and_independent_row_lane():
    store, ticket = MaterialDouble(), Ticket()
    store.payload["queryText"] = "😀éabc"
    desc = header(store)
    request = {"binding": desc["identity"], "maxUtf8Bytes": 4, "cursor": None}
    first = text_page(store, request, LIMITS, ticket)
    assert first["text"] == "😀" and first["utf8Length"] == 4
    assert text_page(store, request, LIMITS, ticket) == first
    request["cursor"] = first["nextCursor"]
    rest = text_page(store, request, LIMITS, ticket)
    assert rest["startUtf8Byte"] == 4
    assert rows_page(store, params(store, desc), LIMITS, ticket)["rows"][0]["index"] == 0
    with pytest.raises(JobFault) as error:
        rows_page(store, {**params(store, desc), "cursor": first["nextCursor"]}, LIMITS, ticket)
    assert error.value.code == "CURSOR_MISMATCH"


def test_duplicate_rows_keep_actual_order_distinct_index_keys():
    store, ticket = MaterialDouble(), Ticket()
    desc = header(store)
    page = rows_page(store, params(store, desc), LIMITS, ticket)
    a, b = page["rows"]
    assert a["cells"] == b["cells"] and a["index"] == 0 and b["index"] == 1
    assert a["rowKey"] != b["rowKey"]
    assert a["rowKey"] == digest(
        [desc["identity"]["resultId"], desc["identity"]["payloadSha256"], 0]
    )


@pytest.mark.parametrize(
    "raw,kind,subkind",
    [
        ("<urn:s>", "iri", None),
        ('"https://example.invalid/"', "literal", "plain"),
        ('"bonjour"@fr', "literal", "language"),
        ('"s"^^<http://www.w3.org/2001/XMLSchema#string>', "literal", "datatype"),
    ],
)
def test_typed_term_keeps_original_rdf_kind_and_n3(raw, kind, subkind):
    result = typed_cell(raw, Ticket())
    assert result["kind"] == kind and result["n3"] == raw
    if subkind:
        assert result["literalType"]["kind"] == subkind
    assert typed_cell(None, Ticket()) is None


def test_changed_binding_does_not_reconstruct_from_evidence_leaves():
    store = MaterialDouble()
    p = params(store)
    p["binding"]["payloadSha256"] = "b" * 64
    with pytest.raises(JobFault) as error:
        rows_page(store, p, LIMITS, Ticket())
    assert error.value.code == "IDENTITY_CONFLICT"


@pytest.mark.parametrize(
    "now,expected", [(1999, None), (2000, "CURSOR_EXPIRED"), (2001, "CURSOR_EXPIRED")]
)
def test_cursor_exact_expiry_boundary(now, expected):
    store = MaterialDouble()
    binding = header(store)["identity"]
    token = store._new_cursor("query-rows-v1", binding, 1, {"nextIndex": 0})
    store.now = now
    if expected:
        with pytest.raises(JobFault) as error:
            rows_page(store, {"binding": binding, "pageSize": 1, "cursor": token}, LIMITS, Ticket())
        assert error.value.code == expected
    else:
        assert (
            rows_page(
                store, {"binding": binding, "pageSize": 1, "cursor": token}, LIMITS, Ticket()
            )["rows"][0]["index"]
            == 0
        )


def test_cursor_wrong_binding_precedes_expiry_and_text_bad_scalar_position():
    store = MaterialDouble()
    desc = header(store)
    token = store._new_cursor("query-rows-v1", desc["identity"], 2, {"nextIndex": 0})
    store.records[token]["binding"] = canonical(
        {**desc["identity"], "jobId": "00000000-0000-4000-8000-000000000099"}
    )
    store.now = 2000
    with pytest.raises(JobFault) as error:
        rows_page(store, {**params(store, desc), "cursor": token}, LIMITS, Ticket())
    assert error.value.code == "CURSOR_MISMATCH"
    store = MaterialDouble()
    store.payload["queryText"] = "😀x"
    desc = header(store)
    token = store._new_cursor("query-text-v1", desc["identity"], 4, {"nextUtf8Byte": 1})
    with pytest.raises(JobFault) as error:
        text_page(
            store,
            {"binding": desc["identity"], "maxUtf8Bytes": 4, "cursor": token},
            LIMITS,
            Ticket(),
        )
    assert error.value.code == "INVALID_STATE"


def test_no_normalization_or_truncation_and_complete_text_hash():
    import hashlib

    for original in ("é😀e\u0301", "e\u0301😀é"):
        store = MaterialDouble()
        store.payload["queryText"] = original
        desc = header(store)
        cursor = None
        parts = []
        offset = 0
        for _ in range(16):
            page = text_page(
                store,
                {"binding": desc["identity"], "maxUtf8Bytes": 4, "cursor": cursor},
                LIMITS,
                Ticket(),
            )
            assert page["startUtf8Byte"] == offset
            parts.append(page["text"])
            offset += page["utf8Length"]
            cursor = page["nextCursor"]
            if cursor is None:
                break
        assert cursor is None and "".join(parts) == original
        assert hashlib.sha256("".join(parts).encode()).hexdigest() == desc["executedText"]["sha256"]


def test_empty_and_control_row_fit_but_original_complete_long_row_does_not():
    limits = {**LIMITS, "maxPageBytes": 3072}
    store = MaterialDouble()
    store.payload["query"]["rows"] = []
    assert rows_page(store, params(store), limits, Ticket())["rows"] == []
    store.payload["query"]["rows"] = [["<urn:s>"]]
    assert len(rows_page(store, params(store), limits, Ticket())["rows"]) == 1
    store.payload["query"]["rows"] = [["<urn:" + "x" * 1024 + ">"]]
    with pytest.raises(JobFault) as error:
        rows_page(store, params(store), limits, Ticket())
    assert error.value.code == "RESOURCE_LIMIT" and error.value.params == {"resource": "page"}


def test_graph_cleanup_preserves_first_and_does_not_hide_first_close_failure(monkeypatch):
    import rdflib

    close_failure = MemoryError("finite injected close failure")

    def fail_close(self, *args, **kwargs):
        raise close_failure

    monkeypatch.setattr(rdflib.Graph, "close", fail_close)
    with pytest.raises(JobFault) as error:
        typed_cell("not a valid RDF term", Ticket())
    assert error.value.code == "INVALID_STATE"
    with pytest.raises(MemoryError) as error:
        typed_cell("<urn:s>", Ticket())
    assert error.value is close_failure


def test_room_uses_explicit_store_and_pays_before_its_encoder():
    from ontolearn_engine.project.query_presentation import _room

    store, ticket = MaterialDouble(), Ticket()
    seen = []

    def encoded(value):
        assert ticket.fees[-1][0] == "page encode"
        seen.append(value)
        return CONTRACT.encoded_size(value)

    store.contract = SimpleNamespace(encoded_size=encoded)
    value = {"finite": "explicit Store encoder"}
    _room(store, value, LIMITS, ticket)
    assert seen == [value]


def test_2400_page_accepts_complete_400_scalar_iri_without_fake_2048_floor():
    store, ticket = MaterialDouble(), Ticket()
    raw = "<urn:" + "x" * 394 + ">"
    assert len(raw) == 400
    store.payload["query"]["rows"] = [[raw]]
    limits = {**LIMITS, "maxPageBytes": 2400}
    desc = describe(
        store,
        {"projectId": store.metadata["projectId"], "resultId": store.metadata["resultId"]},
        limits,
        ticket,
    )
    page = rows_page(store, params(store, desc), limits, ticket)
    assert page["rows"][0]["cells"][0] == {"kind": "iri", "iri": raw[1:-1], "n3": raw}
    assert page["nextCursor"] is None
    assert CONTRACT.encoded_size(desc) <= 2400
    assert CONTRACT.encoded_size(page) <= 2400
    assert (
        CONTRACT.encoded_size(page | {"nextCursor": "00000000-0000-4000-8000-000000000001"}) <= 2400
    )


class RowsBudgetTicket(Ticket):
    """Atomic test book, not a production issuer or physical-memory proof."""

    def __init__(self, store, *, candidate_caps=None, caps=None, initial=(0, 0, 0)):
        super().__init__()
        self.store = store
        self.active = True
        self.candidate_caps = candidate_caps
        self.caps = caps
        self.used = list(initial)
        self.candidate_used = [0, 0, 0]
        self.attempts = []
        self.rejections = []
        self.pay_after_rejection = []
        self.reject_error = JobFault("RESOURCE_LIMIT", {"resource": "memory"})
        self.on_reject = None
        self.checks = 0

    def check(self, store):
        self.checks += 1
        assert store is self.store
        if not self.active:
            fault("PERMISSION_DENIED")

    def pay(self, stage, **fees):
        self.check(self.store)
        charge = [fees.get(key, 0) for key in ("bytes_", "objects", "work")]
        self.attempts.append((stage, tuple(charge)))
        if self.rejections:
            self.pay_after_rejection.append(stage)
        candidate = stage == "rows candidate admission"
        rejected = self.caps is not None and any(
            old + amount > cap
            for old, amount, cap in zip(self.used, charge, self.caps, strict=True)
        )
        if candidate and self.candidate_caps is not None:
            rejected |= any(
                old + amount > cap
                for old, amount, cap in zip(
                    self.candidate_used, charge, self.candidate_caps, strict=True
                )
            )
        if rejected:
            self.rejections.append((stage, tuple(self.used), tuple(self.candidate_used)))
            if self.on_reject:
                self.on_reject()
            raise self.reject_error
        self.used = [old + amount for old, amount in zip(self.used, charge, strict=True)]
        if candidate:
            self.candidate_used = [
                old + amount for old, amount in zip(self.candidate_used, charge, strict=True)
            ]
        super().pay(stage, **fees)
        self.check(self.store)


def single_row_admission():
    # Independent sum of the original four charges for one exact <urn:s> cell.
    # row-bound=(0,0,129); typed=(8640,288,1136); N3=(4992,1248,1472).
    return (
        13632 + 4 * LIMITS["maxPageBytes"] + 4096,
        1792,
        2737 + 8 * LIMITS["maxPageBytes"] + 4096,
    )


@pytest.mark.parametrize("dimension", [0, 1, 2], ids=["bytes", "objects", "work"])
@pytest.mark.parametrize("delta", [-1, 0, 1], ids=["minus-one", "exact", "plus-one"])
def test_rows_atomic_candidate_three_dimensions_before_graph(monkeypatch, dimension, delta):
    import rdflib

    store = MaterialDouble()
    store.payload["query"]["rows"] = [["<urn:s>"]]
    request = params(store, size=1)
    fee = single_row_admission()
    caps = [10**12, 10**12, 10**12]
    caps[dimension] = fee[dimension] + delta
    ticket = RowsBudgetTicket(store, candidate_caps=caps)
    constructed = []
    original = rdflib.Graph

    def graph(*args, **kwargs):
        constructed.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(rdflib, "Graph", graph)
    if delta < 0:
        with pytest.raises(JobFault) as error:
            rows_page(store, request, LIMITS, ticket)
        assert error.value is ticket.reject_error
        assert constructed == [] and ticket.values == [] and store.records == {}
        assert ticket.candidate_used == [0, 0, 0]
        assert tuple(ticket.used) == ticket.rejections[0][1]
    else:
        page = rows_page(store, request, LIMITS, ticket)
        assert page["rows"][0]["cells"] == [{"kind": "iri", "iri": "urn:s", "n3": "<urn:s>"}]
        assert page["nextCursor"] is None and len(constructed) == 1
        assert ticket.candidate_used == list(fee)
    assert ticket.attempts[-1] == ("rows candidate admission", fee)
    assert ticket.pay_after_rejection == []
    # Local individual consumption never charges the original book a second time.
    assert not any(
        stage in {"typed row", "N3 projection", "row bound", "page encode"}
        for stage, _ in ticket.fees
    )
    assert sum(stage == "rows final prepaid" for stage, _ in ticket.fees) == 1


@pytest.mark.parametrize("dimension", [0, 1, 2], ids=["bytes", "objects", "work"])
def test_rows_prefix_survives_next_admission_without_final_pay_or_refund(dimension):
    store = MaterialDouble()
    request = params(store)
    fee = single_row_admission()
    caps = [10**12, 10**12, 10**12]
    caps[dimension] = fee[dimension]
    ticket = RowsBudgetTicket(store, candidate_caps=caps)
    page = rows_page(store, request, LIMITS, ticket)
    assert [row["index"] for row in page["rows"]] == [0]
    assert ticket.values == [page] and ticket.pay_after_rejection == []
    assert tuple(ticket.used) == ticket.rejections[0][1]
    assert ticket.candidate_used == list(fee)
    cursor = store.records[page["nextCursor"]]
    assert cursor["kind"] == "query-rows-v1" and cursor["size"] == 2
    assert json.loads(cursor["position"]) == {"nextIndex": 1}
    assert json.loads(cursor["binding"]) == request["binding"]
    assert ticket.attempts[-1] == ("rows candidate admission", fee)


def test_rows_failed_pay_rechecks_original_revocation_before_prefix():
    store = MaterialDouble()
    ticket = RowsBudgetTicket(store, candidate_caps=single_row_admission())
    ticket.on_reject = lambda: setattr(ticket, "active", False)
    with pytest.raises(JobFault) as error:
        rows_page(store, params(store), LIMITS, ticket)
    assert error.value.code == "PERMISSION_DENIED"
    assert len(ticket.rejections) == 1 and ticket.values == [] and store.records == {}
    assert tuple(ticket.used) == ticket.rejections[0][1]


@pytest.mark.parametrize(
    "failure",
    [
        JobFault("RESOURCE_LIMIT", {"resource": "page"}),
        JobFault("RESOURCE_LIMIT", {"resource": "frame"}),
        JobFault("INVALID_STATE"),
        JobFault("PERMISSION_DENIED"),
    ],
)
def test_rows_admission_does_not_swallow_other_original_errors(failure):
    store = MaterialDouble()
    ticket = RowsBudgetTicket(store, candidate_caps=single_row_admission())
    ticket.reject_error = failure
    with pytest.raises(JobFault) as error:
        rows_page(store, params(store), LIMITS, ticket)
    assert error.value is failure and ticket.values == [] and store.records == {}


def test_rows_preserves_real_cursor_capacity_error_after_valid_prefix():
    store = MaterialDouble()
    ticket = RowsBudgetTicket(store, candidate_caps=single_row_admission())
    failure = JobFault("RESOURCE_LIMIT", {"resource": "page"})

    def full(*args, **kwargs):
        raise failure

    store._new_cursor = full
    with pytest.raises(JobFault) as error:
        rows_page(store, params(store), LIMITS, ticket)
    assert error.value is failure and ticket.values == []
    assert ticket.pay_after_rejection == []


def test_rows_graph_close_revocation_is_checked_before_retention(monkeypatch):
    import rdflib

    store = MaterialDouble()
    ticket = RowsBudgetTicket(store)
    original = rdflib.Graph.close

    def close(graph, *args, **kwargs):
        result = original(graph, *args, **kwargs)
        ticket.active = False
        return result

    monkeypatch.setattr(rdflib.Graph, "close", close)
    with pytest.raises(JobFault) as error:
        rows_page(store, params(store), LIMITS, ticket)
    assert error.value.code == "PERMISSION_DENIED"
    assert ticket.values == [] and store.records == {}


@pytest.mark.parametrize("raw", ["<urn:s>", "not an RDF term"])
def test_rows_graph_close_keeps_original_first_cause(monkeypatch, raw):
    import rdflib

    store = MaterialDouble()
    store.payload["query"]["rows"] = [[raw]]
    ticket = RowsBudgetTicket(store)
    failure = MemoryError("original finite close cause")

    def close(*args, **kwargs):
        raise failure

    monkeypatch.setattr(rdflib.Graph, "close", close)
    with pytest.raises((MemoryError, JobFault)) as error:
        rows_page(store, params(store), LIMITS, ticket)
    if raw == "<urn:s>":
        assert error.value is failure
    else:
        assert isinstance(error.value, JobFault) and error.value.code == "INVALID_STATE"
    assert ticket.values == [] and store.records == {}


def test_rows_encoder_callback_revocation_and_final_delivery_recheck():
    store = MaterialDouble()
    request = params(store)
    ticket = RowsBudgetTicket(store)

    def encoded(value):
        if value.get("kind") == "rows":
            ticket.active = False
        return CONTRACT.encoded_size(value)

    store.contract = SimpleNamespace(validate=CONTRACT.validate, encoded_size=encoded)
    with pytest.raises(JobFault) as error:
        rows_page(store, request, LIMITS, ticket)
    assert error.value.code == "PERMISSION_DENIED" and ticket.values == []

    store = MaterialDouble()
    ticket = RowsBudgetTicket(store)

    def deliver(value):
        ticket.active = False
        return value

    ticket.deliver = deliver
    with pytest.raises(JobFault) as error:
        rows_page(store, params(store), LIMITS, ticket)
    assert error.value.code == "PERMISSION_DENIED"


def test_rows_final_schema_failure_is_not_capacity_short_page():
    store = MaterialDouble()
    request = params(store)
    ticket = RowsBudgetTicket(store)
    store.contract = SimpleNamespace(
        validate=lambda name, value: (
            name != "result_query.result.rowsPage" and CONTRACT.validate(name, value)
        ),
        encoded_size=CONTRACT.encoded_size,
    )
    with pytest.raises(JobFault) as error:
        rows_page(store, request, LIMITS, ticket)
    assert error.value.code == "INVALID_STATE" and ticket.values == []


def test_rows_default_200_bounded_book_reads_all_243_five_cell_values_and_retries():
    from itertools import product

    from ontolearn_engine.resources import LIMITS as RUNTIME_LIMITS

    limits = RUNTIME_LIMITS
    assert limits["maxPageItems"] == 200

    equipment = [f"urn:ontolearn:learning:equipment/{number:03}" for number in (1, 2, 3)]
    expected = [[f"<{iri}>" for iri in row] for row in product(equipment, repeat=5)]
    store = MaterialDouble()
    store.payload["query"] = {
        "type": "SELECT",
        "variables": ["a", "b", "c", "d", "e"],
        "rows": expected,
    }
    desc = header(store)
    request = params(store, desc, size=200)
    all_rows, cursors = [], set()
    # Same production caps/initial reserve formula, but this remains a material
    # double: no claim of Store authentication, physical RSS, IPC or real worker.
    initial = (
        4096 + 4 * 262144 + 32 * 1572864 + 2048 * 4096 + 32768,
        128 + 128 + 32 * 4096 + 4096,
        4096 + 3 * 67108864,
    )
    caps = (134217728 - 8388608, 1048576, 536870912)
    for _ in range(243):
        ticket = RowsBudgetTicket(store, caps=caps, initial=initial)
        page = rows_page(store, request, limits, ticket)
        assert 0 < len(page["rows"]) <= 200
        assert CONTRACT.encoded_size(page) <= limits["maxPageBytes"]
        assert CONTRACT.encoded_size(page) + 1024 <= limits["maxFrameBytes"]
        assert (
            rows_page(store, request, limits, RowsBudgetTicket(store, caps=caps, initial=initial))
            == page
        )
        assert [row["index"] for row in page["rows"]] == list(
            range(len(all_rows), len(all_rows) + len(page["rows"]))
        )
        for row in page["rows"]:
            assert row["rowKey"] == digest(
                [desc["identity"]["resultId"], desc["identity"]["payloadSha256"], row["index"]]
            )
            assert row["cells"] == [
                {"kind": "iri", "iri": raw[1:-1], "n3": raw} for raw in expected[row["index"]]
            ]
        all_rows.extend(page["rows"])
        if page["nextCursor"] is None:
            break
        assert page["nextCursor"] not in cursors
        cursors.add(page["nextCursor"])
        record = store.records[page["nextCursor"]]
        assert record["size"] == 200 and json.loads(record["binding"]) == request["binding"]
        request = {**request, "cursor": page["nextCursor"]}
    assert len(all_rows) == 243 and len(cursors) > 0
    assert [row["index"] for row in all_rows] == list(range(243))
    assert len({row["rowKey"] for row in all_rows}) == 243


@pytest.mark.parametrize("dimension", [0, 1, 2], ids=["bytes", "objects", "work"])
@pytest.mark.parametrize("delta", [-1, 0, 1], ids=["minus-one", "exact", "plus-one"])
def test_rows_empty_final_three_dimensional_reservation_boundary(dimension, delta):
    store = MaterialDouble()
    store.payload["query"]["rows"] = []
    request = params(store)
    observed = Ticket()
    rows_page(store, request, LIMITS, observed)
    final_fee = (
        20 * LIMITS["maxPageBytes"] + 69632,
        4352 + 8 * LIMITS["maxPageItems"],
        72 * LIMITS["maxPageBytes"] + 69632,
    )
    base = [0, 0, 0]
    for stage, fee in observed.fees:
        if stage == "rows final prepaid":
            assert tuple(fee[k] for k in ("bytes_", "objects", "work")) == final_fee
        else:
            for i, key in enumerate(("bytes_", "objects", "work")):
                base[i] += fee.get(key, 0)
    caps = [10**12, 10**12, 10**12]
    caps[dimension] = base[dimension] + final_fee[dimension] + delta
    ticket = RowsBudgetTicket(store, caps=caps)
    if delta < 0:
        with pytest.raises(JobFault) as error:
            rows_page(store, request, LIMITS, ticket)
        assert error.value is ticket.reject_error
        assert ticket.rejections[0][0] == "rows final prepaid" and ticket.values == []
        assert tuple(ticket.used) == ticket.rejections[0][1]
    else:
        page = rows_page(store, request, LIMITS, ticket)
        assert page["rows"] == [] and page["nextCursor"] is None
        assert ticket.values == [page]
    assert ticket.pay_after_rejection == [] and store.records == {}


def test_rows_every_local_spend_delegates_original_checks_and_never_overdraws(monkeypatch):
    from ontolearn_engine.project import query_presentation

    store = MaterialDouble()
    request = params(store, size=1)
    ticket = RowsBudgetTicket(store)
    local = []
    original = query_presentation._RowsPrepaid.pay

    def pay(prepaid, stage, **fees):
        before = ticket.checks
        original(prepaid, stage, **fees)
        assert ticket.checks >= before + 2
        local.append(stage)

    monkeypatch.setattr(query_presentation._RowsPrepaid, "pay", pay)
    page = rows_page(store, request, LIMITS, ticket)
    assert len(page["rows"]) == 1
    assert local == [
        "rows cursor validation delivery",
        "row bound",
        "typed row",
        "N3 projection",
        "page encode",
        "page encode",
    ]
    assert [stage for stage, _ in ticket.fees if stage.startswith("rows ")] == [
        "rows final prepaid",
        "rows candidate admission",
    ]

    def overdraw(prepaid, stage, **fees):
        if stage == "typed row":
            return original(prepaid, stage, objects=10**12)
        return original(prepaid, stage, **fees)

    store = MaterialDouble()
    request = params(store, size=1)
    ticket = RowsBudgetTicket(store)
    monkeypatch.setattr(query_presentation._RowsPrepaid, "pay", overdraw)
    with pytest.raises(JobFault) as error:
        rows_page(store, request, LIMITS, ticket)
    assert error.value.code == "INVALID_STATE" and ticket.values == []
    assert not ticket.rejections


def test_rows_pure_encoder_short_page_keeps_error_kind_and_final_frame_check():
    store = MaterialDouble()
    store.payload["query"]["rows"] = [["<urn:" + "x" * 394 + ">"] for _ in range(2)]
    request = params(store)
    limits = {**LIMITS, "maxPageBytes": 2400}
    page = rows_page(store, request, limits, RowsBudgetTicket(store))
    assert len(page["rows"]) == 1 and page["nextCursor"] is not None
    assert CONTRACT.encoded_size(page) <= 2400
    with pytest.raises(JobFault) as error:
        rows_page(store, request, {**LIMITS, "maxFrameBytes": 1024}, RowsBudgetTicket(store))
    assert error.value.code == "RESOURCE_LIMIT" and error.value.params == {"resource": "frame"}


@pytest.mark.parametrize("with_prefix", [False, True])
def test_rows_raw_lower_bound_keeps_page_kind_without_typed_n3_admission(monkeypatch, with_prefix):
    import rdflib

    store = MaterialDouble()
    raw = "<urn:" + "x" * 2043 + ">"
    assert len(raw) == 2049
    too_large = [raw] * 64
    store.payload["query"] = {
        "type": "SELECT",
        "variables": [f"v{i}" for i in range(64)],
        "rows": [[None] * 64, too_large] if with_prefix else [too_large],
    }
    request = params(store, size=2)
    ticket = RowsBudgetTicket(store)

    def forbidden(*args, **kwargs):
        raise AssertionError("raw lower-bound refusal must not build a Graph")

    monkeypatch.setattr(rdflib, "Graph", forbidden)
    if with_prefix:
        page = rows_page(store, request, LIMITS, ticket)
        assert len(page["rows"]) == 1 and page["rows"][0]["cells"] == [None] * 64
        assert page["nextCursor"] is not None
    else:
        with pytest.raises(JobFault) as error:
            rows_page(store, request, LIMITS, ticket)
        assert error.value.code == "RESOURCE_LIMIT" and error.value.params == {"resource": "page"}
        assert ticket.values == [] and store.records == {}
    assert ticket.attempts[-1] == ("rows candidate admission", (0, 0, 192))
    assert ticket.pay_after_rejection == []
