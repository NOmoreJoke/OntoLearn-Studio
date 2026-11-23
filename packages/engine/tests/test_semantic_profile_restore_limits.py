"""Independent boundary inputs for whole restore costs and atomic failure."""

import copy
import gc
import os
from dataclasses import fields, replace
from pathlib import Path
from unittest.mock import patch

import pytest
import test_semantic_profile_restore as support
from ontolearn_engine import semantic, semantic_execution
from ontolearn_engine import semantic_profile_restore as restore
from ontolearn_engine import semantic_profile_restore_budget as resources
from ontolearn_engine.quality import rule_terms
from ontolearn_engine.quality.rule_firing import RuleSpec, Triple, Variable
from ontolearn_engine.quality.rule_profile import (
    Budget,
    ProfileFailure,
    ProfileLimits,
    SourceRecord,
    TermInput,
)
from ontolearn_engine.quality.rule_terms import parse_value
from ontolearn_engine.semantic_profile_restore import ChildAllocation
from ontolearn_engine.semantic_profile_restore_budget import RestoreFailure, RestoreLedger

CUMULATIVE = (
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
LIVE = ("scalar", "objects", "trie_nodes", "trie_slots", "opaque_scalar", "opaque_objects")


@pytest.fixture(scope="module")
def captured():
    # Same repeated SourceRecord, two real operand keys: an actual branch/split.
    return support.repeated_source_capture(different_values=True)


@pytest.mark.parametrize("domain", CUMULATIVE)
def test_each_actual_cumulative_domain_exact_and_one_short(captured, domain):
    _, baseline = support.restore_capture(captured)
    required = dict(baseline.usage)[domain]
    assert required > 0, (domain, baseline.usage)
    exact = RestoreLedger(overrides=((domain, required),))
    _, exact = support.restore_capture(captured, ledger=exact)
    assert dict(exact.usage)[domain] == required
    short = RestoreLedger(overrides=((domain, required - 1),))
    with pytest.raises(RestoreFailure) as caught:
        support.restore_capture(captured, ledger=short)
    assert caught.value.classification == "resource"
    assert short.state == "failed"
    assert dict(short.usage)[domain] <= required - 1
    assert not any(value for _, value in short.live)


@pytest.mark.parametrize("domain", LIVE)
def test_live_tickets_exact_peak_and_one_short_are_released(captured, domain):
    _, baseline = support.restore_capture(captured)
    required = dict(baseline.peaks)[domain]
    assert required > 0, (domain, baseline.peaks)
    exact = RestoreLedger(overrides=((domain, required),))
    support.restore_capture(captured, ledger=exact)
    assert dict(exact.peaks)[domain] == required
    short = RestoreLedger(overrides=((domain, required - 1),))
    with pytest.raises(RestoreFailure) as caught:
        support.restore_capture(captured, ledger=short)
    assert caught.value.classification == "resource"
    assert short.state == "failed"
    assert not any(value for _, value in short.live)


def test_failed_ledger_does_not_refund_or_allow_retry(captured):
    ledger = RestoreLedger(overrides=(("wire", 0),))
    with pytest.raises(RestoreFailure):
        support.restore_capture(captured, ledger=ledger)
    spent, peaks, slots = ledger.usage, ledger.peaks, ledger.slot_states
    with pytest.raises(RestoreFailure):
        support.restore_capture(captured, ledger=ledger)
    assert ledger.state == "failed"
    assert ledger.usage == spent and ledger.peaks == peaks and ledger.slot_states == slots
    assert not any(value for _, value in ledger.live)
    # A new ledger is a separate pure operation, not persistent retry authority.
    result, fresh = support.restore_capture(captured)
    assert fresh.state == "success" and result.formal_authority is False


def test_success_ledger_also_cannot_be_reused(captured):
    _, ledger = support.restore_capture(captured)
    spent, peaks = ledger.usage, ledger.peaks
    with pytest.raises(RestoreFailure):
        support.restore_capture(captured, ledger=ledger)
    assert ledger.usage == spent and ledger.peaks == peaks


def test_ledger_overrides_never_grant_extra_budget(captured):
    _, original = support.restore_capture(captured)
    for bad in (
        (("wire", dict(original.caps)["wire"] + 1),),
        (("wire", True),),
        (("wire", -1),),
        (("unknown-domain", 1),),
        (("wire", 0), ("wire", 0)),
    ):
        with pytest.raises(RestoreFailure):
            support.restore_capture(captured, ledger=RestoreLedger(overrides=bad))


def minimal_many_rules(count):
    triple = Triple(Variable("?x"), TermInput("iri", "u:p"), Variable("?v"))
    rules = tuple(
        RuleSpec(str(index), (triple,), (), (triple,)) for index in reversed(range(count))
    )
    return f"<u:p> a <{support.OWL}ObjectProperty> .", rules


@pytest.mark.parametrize("count", [1, 2, 100])
def test_actual_divmod_or_original_resource_failure_is_recorded_explicitly(count):
    text, rules = minimal_many_rules(count)
    try:
        capture = support.capture_case(text=text, rules=rules, label=f"allocator-{count}")
    except semantic_execution.ProfileExecutionFault as error:
        # N100's original I_i=2621 may already reject the smallest legal rule.
        # A negative original call is not a fabricated successful restore witness.
        assert count == 100
        assert error.diagnostic["classification"] == "resource"
        evidence = os.environ.get("I05_RESTORE_EVIDENCE_DIR")
        if evidence:
            path = Path(evidence) / "allocator-100-original-failure.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(
                support.canonical(
                    {
                        "originalProductionSuccess": False,
                        "restorationAttempted": False,
                        "rules": support.signature(rules),
                        "text": text,
                        "error": error.error,
                        "diagnostic": error.diagnostic,
                    }
                )
            )
        return
    children = capture.native["mechanismBatches"]
    assert [item["ruleId"] for item in children] == sorted(spec.rule_id for spec in rules)
    assert [item["definitionOrdinal"] for item in children] == [
        next(i for i, spec in enumerate(rules) if spec.rule_id == item["ruleId"])
        for item in children
    ]
    for name, total in semantic._PROFILE_POOLS.items():
        assert sum(getattr(item["limits"], name) for item in children) == total
        assert [getattr(item["limits"], name) for item in children] == [
            total // count + (position < total % count) for position in range(count)
        ]
    assert sum(item["limits"].firings for item in children) == 1024
    support.exec_restore(capture, f"allocator-{count}")


def test_disabled_rules_still_occupy_their_original_allocation_slot():
    capture = support.capture_case(
        rules=(support.rule("z"), support.rule("a")), disabled=("z",), label="disabled-slot"
    )
    children = capture.native["mechanismBatches"]
    assert [item["ruleId"] for item in children] == ["a", "z"]
    assert [item["disabled"] for item in children] == [False, True]
    assert [item["limits"].firings for item in children] == [512, 512]
    support.exec_restore(capture, "disabled-slot")


@pytest.mark.parametrize("field", [field.name for field in fields(ProfileLimits)])
def test_saved_or_captured_limits_cannot_mint_a_new_allocation(captured, field):
    payload = copy.deepcopy(captured.payload)
    child = payload["reasoning"]["mechanismBatches"][0]
    value = int(child["limits"][field]["integerHex"], 16)
    child["limits"][field] = {"integerHex": hex(max(0, value - 1))}
    child["budgetLimits"][field] = child["limits"][field]
    support.assert_rejected(captured, payload=payload)
    original = captured.allocation.children[0]
    changed = ChildAllocation(
        original.rule_id,
        original.definition_ordinal,
        replace(original.limits, **{field: max(0, getattr(original.limits, field) - 1)}),
    )
    allocation = replace(captured.allocation, children=(changed,))
    support.assert_rejected(captured, allocation=allocation)


def test_missing_extra_or_wrong_child_slot_and_original_ids_are_rejected(captured):
    original = captured.allocation
    for allocation in (
        replace(original, children=()),
        replace(original, children=original.children * 2),
        replace(original, rule_ids=("fake",)),
        replace(original, rule_ids=("r", "r")),
        replace(original, disabled_rule_ids=("r",)),
        replace(original, budget_version="mechanism-budget/0"),
    ):
        support.assert_rejected(captured, allocation=allocation)


def test_strict_entry_does_not_call_foreign_object_protocols(captured):
    class Foreign:
        def __iter__(self):
            raise AssertionError("must not iterate foreign input")

        def __bytes__(self):
            raise AssertionError("must not convert foreign input")

        def __fspath__(self):
            raise AssertionError("must not inspect a foreign path")

    foreign = Foreign()
    for expected, allocation, wire in (
        (foreign, captured.allocation, None),
        (captured.expected, foreign, None),
        (captured.expected, captured.allocation, (foreign, captured.rows_json)),
    ):
        support.assert_rejected(captured, expected=expected, allocation=allocation, wire=wire)
    with pytest.raises(RestoreFailure):
        restore.restore_profile_batches(
            captured.payload_json,
            captured.rows_json,
            expected=captured.expected,
            allocation=captured.allocation,
            ledger=foreign,
        )


def test_nested_allocation_foreign_protocols_are_rejected_without_callbacks(captured):
    calls = []

    class Foreign:
        def __len__(self):
            calls.append("len")
            return 1

        def __iter__(self):
            calls.append("iter")
            return iter(("r",))

        def __eq__(self, other):
            calls.append("eq")
            return True

    class ForeignTuple(tuple):
        __len__ = Foreign.__len__
        __iter__ = Foreign.__iter__

    foreign = Foreign()
    for field in ("rule_ids", "disabled_rule_ids", "children"):
        for value in (foreign, ForeignTuple(("r",)), (foreign,)):
            allocation = replace(captured.allocation, **{field: value})
            support.assert_rejected(captured, allocation=allocation)
            assert calls == [], (field, calls)
    child = replace(captured.allocation.children[0], rule_id=foreign)
    support.assert_rejected(captured, allocation=replace(captured.allocation, children=(child,)))
    assert calls == []


@pytest.mark.parametrize("short", [False, True])
def test_encoder_live_block_is_reserved_before_delegate(monkeypatch, short):
    value = ["a" * 200000, "\0" * 40000, "中" * 1000]
    expected = support.canonical(value)
    bound = len(expected)
    ledger = RestoreLedger(overrides=(("scalar", bound + 8 * bound + 64 - short),))
    ledger.begin(bound, 0, 1)
    calls = []
    original = semantic_execution._profile_json_bytes

    def encoder(safe):
        calls.append(True)
        return original(safe)

    monkeypatch.setattr(semantic_execution, "_profile_json_bytes", encoder)
    try:
        if short:
            with pytest.raises(RestoreFailure) as caught:
                resources.canonical_bytes(value, ledger, stage="A11", bound=bound)
            assert caught.value.classification == "resource"
            assert calls == []
        else:
            result = resources.canonical_bytes(value, ledger, stage="A11", bound=bound)
            assert result == expected and calls == [True]
            assert dict(ledger.live)["scalar"] == bound + len(result)
            resources.release_bytes(result, ledger)
    finally:
        ledger.cleanup()
        ledger.finish(False)


@pytest.mark.parametrize("fault", ["constructor", "usage", "peaks"])
def test_receipt_failure_drops_native_locals_from_public_traceback(captured, monkeypatch, fault):
    calls = []

    def fail(*_args):
        calls.append(fault)
        raise MemoryError("injected receipt allocation failure")

    if fault == "constructor":
        monkeypatch.setattr(restore, "RestoredBatchSet", fail)
    else:
        monkeypatch.setattr(RestoreLedger, fault, property(fail))
    ledger = RestoreLedger()
    with pytest.raises(RestoreFailure) as caught:
        support.restore_capture(captured, ledger=ledger)
    assert calls == [fault]
    assert caught.value.reason == "RESTORE_INTERNAL"
    assert caught.value.__context__ is None and caught.value.__cause__ is None
    assert ledger.state == "failed" and not any(value for _, value in ledger.live)
    public_frames = []
    traceback = caught.value.__traceback__
    while traceback is not None:
        # Both public APIs now share this exact operation frame. Checking only
        # the thin compatibility wrapper would miss retained decoded values.
        if traceback.tb_frame.f_code.co_name == "_restore_operation":
            public_frames.append(traceback.tb_frame)
        traceback = traceback.tb_next
    assert len(public_frames) == 1
    for name in (
        "children",
        "parse_usage",
        "caps",
        "outcome",
        "decoder",
        "projection",
        "inner_batches",
        "retention",
    ):
        assert public_frames[0].f_locals[name] is None, (fault, name)


def test_exact_native_classes_and_exact_bytes_are_required(captured):
    class ForeignBytes(bytes):
        pass

    class ForeignExpectation(type(captured.expected)):
        pass

    class ForeignAllocation(type(captured.allocation)):
        pass

    for blob in (
        bytearray(captured.payload_json),
        memoryview(captured.payload_json),
        ForeignBytes(captured.payload_json),
    ):
        support.assert_rejected(captured, wire=(blob, captured.rows_json))
    support.assert_rejected(
        captured,
        expected=ForeignExpectation(
            **{
                field.name: getattr(captured.expected, field.name)
                for field in fields(captured.expected)
            }
        ),
    )
    support.assert_rejected(
        captured,
        allocation=ForeignAllocation(
            **{
                field.name: getattr(captured.allocation, field.name)
                for field in fields(captured.allocation)
            }
        ),
    )
    original = captured.allocation.children[0]
    polluted = copy.copy(original.limits)
    object.__setattr__(polluted, "work", True)
    support.assert_rejected(
        captured,
        allocation=replace(
            captured.allocation,
            children=(ChildAllocation(original.rule_id, original.definition_ordinal, polluted),),
        ),
    )


def test_final_child_checker_failure_publishes_no_prefix_and_cleans_live_refs():
    capture = support.capture_case(rules=(support.rule("a"), support.rule("z")), label="last-slot")
    calls = []
    original = restore.check_firing_batch

    def fail_last(*args, **kwargs):
        calls.append(kwargs["limits"])
        if len(calls) == 2:
            raise ProfileFailure("WORK_LIMIT", classification="resource")
        return original(*args, **kwargs)

    ledger = RestoreLedger()
    with (
        patch.object(restore, "check_firing_batch", fail_last),
        pytest.raises(RestoreFailure) as caught,
    ):
        support.restore_capture(capture, ledger=ledger)
    assert len(calls) == 2
    assert caught.value.classification == "resource"
    assert ledger.state == "failed"
    assert not any(value for _, value in ledger.live)
    assert not hasattr(caught.value, "partial_result")
    assert dict(ledger.usage)["wire"] > 0


@pytest.mark.parametrize(
    "raw",
    [
        b"1",
        b"-0",
        b"1e3",
        b"NaN",
        b"Infinity",
        b'{"source":null,"source":null}',
        b'{"unknown-key":null}',
        b'"\\ud800"',
        b'"\\udc00"',
        b'"\\ud800a"',
        b"\xff",
        b"[" * 36 + b"null" + b"]" * 36,
    ],
)
def test_reader_rejects_invalid_tokens_before_building_native_records(raw):
    ledger = RestoreLedger()
    ledger.begin(len(raw), 0, 1)
    try:
        with pytest.raises(RestoreFailure):
            resources.read_json(raw, ledger, label="payload")
    finally:
        ledger.cleanup()
        ledger.finish(False)
    assert not any(value for _, value in ledger.live)


@pytest.mark.parametrize(
    "text",
    ["0x00", "-0x0", "+0x1", "0X1", "0xA", "0x", "0x1" + "0" * 8192],
    ids=["0x00", "-0x0", "+0x1", "0X1", "0xA", "0x", "0x1-plus-8192-zeros"],
)
def test_integer_hex_shape_and_bit_gate_reject_before_unbounded_conversion(text):
    ledger = RestoreLedger()
    ledger.begin(max(100, len(text)), 0, 1)
    try:
        with pytest.raises(RestoreFailure):
            resources.hex_integer(text, ledger)
    finally:
        ledger.cleanup()
        ledger.finish(False)


def test_integer_hex_exact_32768bit_boundary_and_bytes_bound():
    value = (1 << 32768) - 1
    ledger = RestoreLedger()
    ledger.begin(40000, 0, 1)
    try:
        assert resources.hex_integer(hex(value), ledger) == value
        assert resources.hex_integer(hex(-value), ledger) == -value
        assert resources.hex_bytes("00ff", ledger, maximum=2) == b"\0\xff"
        with pytest.raises(RestoreFailure):
            resources.hex_bytes("00ff", ledger, maximum=1)
    finally:
        ledger.cleanup()
        ledger.finish(False)


def test_entire_B_gate_precedes_wire_decode(captured):
    raw = b" " * 8388609
    error, _ledger = support.assert_rejected(captured, wire=(raw, b"[]"))
    assert error.classification == "resource"


def test_full_keys_distinguish_none_empty_language_datatype_and_all_source_fields():
    ledger = RestoreLedger()
    ledger.begin(200000, 0, 1)
    variants = (
        TermInput("literal", "x"),
        TermInput("literal", "x", support.XSD + "string"),
        TermInput("literal", "x", language_raw="EN-us"),
        TermInput("literal", "x", language_raw="en-US"),
        TermInput("literal", "x", source=SourceRecord()),
        TermInput("literal", "x", source=SourceRecord(reference="")),
        TermInput("literal", "x", source=SourceRecord(digest="")),
        TermInput("literal", "x", source=SourceRecord(revision="")),
        TermInput("literal", "x", source=SourceRecord(text="")),
    )
    keys = []
    try:
        for term in variants:
            key = resources.term_key(term, ledger)
            keys.append(key)
        assert len(set(keys)) == len(variants)
        assert all(key.startswith(b"I05RTK1\0") for key in keys)
    finally:
        while keys:
            key = keys.pop()
            resources.release_key(key, ledger)
            del key
        ledger.cleanup()
        # This tests a private subdomain, not all original child/API slots.
        ledger.finish(False)


def test_radix_cache_all256_branches_and_long_common_prefix_ignore_audit_collision(monkeypatch):
    ledger = RestoreLedger()
    ledger.begin(8388608, 0, 1)
    cache = resources.TermCache(ledger)
    calls = []

    def make(term):
        calls.append(term)
        return parse_value(term, None, Budget())

    class CollidingHash:
        def __init__(self, _data=b""):
            pass

        def update(self, _data):
            pass

        def hexdigest(self):
            return "0" * 64

    monkeypatch.setattr(resources, "sha256", CollidingHash)
    terms = [
        TermInput("iri", "urn:branch", source=SourceRecord(text="a" * size)) for size in range(256)
    ]
    terms += [
        TermInput("iri", "urn:prefix:" + "a" * 8000 + ending) for ending in ("a", "b", "ba", "bb")
    ]
    values = []
    retained_key_ids = set()
    try:
        for term in terms:
            key = resources.term_key(term, ledger)
            retained_key_ids.add(id(key))
            try:
                values.append(cache.get_or_insert(key, lambda term=term: make(term)))
            finally:
                resources.release_key(key, ledger)
        assert len(calls) == len(terms)
        assert cache.misses == len(terms)
        pending = list(cache.root.children)
        branch_widths = []
        while pending:
            node = pending.pop()
            assert id(node.key) in retained_key_ids
            assert type(node.key) is bytes and 0 <= node.start < node.end <= len(node.key)
            branch_widths.append(len(node.children))
            pending.extend(node.children)
        assert 256 in branch_widths
        for term, expected in zip(terms, values, strict=True):
            key = resources.term_key(term, ledger)
            try:
                assert (
                    cache.get_or_insert(key, lambda: pytest.fail("unexpected cache miss"))
                    is expected
                )
            finally:
                resources.release_key(key, ledger)
        assert len({id(value) for value in values}) == len(terms)
        assert cache.hits == len(terms)
        assert cache.last_digest == "0" * 64
        assert dict(ledger.usage)["cache_split"] > 0
        assert dict(ledger.peaks)["trie_nodes"] <= 2 * len(terms) + 1
    finally:
        values.clear()
        cache.clear()
        ledger.cleanup()
        # This tests a private subdomain, not all original child/API slots.
        ledger.finish(False)
    assert not any(value for _, value in ledger.live)


@pytest.mark.parametrize("domain", CUMULATIVE + LIVE)
def test_fullview_actual_cap_exact_and_one_short(captured, domain):
    _, baseline = support.restore_capture(captured, fullview=True)
    required = dict(baseline.peaks if domain in LIVE else baseline.usage)[domain]
    assert required > 0
    exact = RestoreLedger(overrides=((domain, required),))
    support.restore_capture(captured, ledger=exact, fullview=True)
    short = RestoreLedger(overrides=((domain, required - 1),))
    with pytest.raises(RestoreFailure) as caught:
        support.restore_capture(captured, ledger=short, fullview=True)
    assert caught.value.classification == "resource"
    assert short.state == "failed" and not any(v for _, v in short.live)


@pytest.mark.parametrize(
    "fault", ["freeze", "last-child", "projection", "batch", "result", "usage", "peaks", "live"]
)
def test_fullview_atomic_failures_drop_all_native_and_traceback_locals(
    captured, monkeypatch, fault
):
    gc.collect()
    original_ids = set(rule_terms._ISSUED_VALUES)
    calls = []
    if fault in ("usage", "peaks", "live"):

        def fail(*args):
            calls.append(fault)
            raise MemoryError("injected fullview receipt failure")

        monkeypatch.setattr(RestoreLedger, fault, property(fail))
    elif fault == "last-child":
        captured = support.capture_case(rules=(support.rule("a"), support.rule("z")))
        original_ids = set(rule_terms._ISSUED_VALUES)
        original = restore.check_firing_batch

        def fail(*args, **kwargs):
            calls.append(fault)
            if len(calls) == 2:
                raise ProfileFailure("WORK_LIMIT", classification="resource")
            return original(*args, **kwargs)

        monkeypatch.setattr(restore, "check_firing_batch", fail)
    elif fault == "freeze":
        original = restore._freeze_native

        def fail(*args, **kwargs):
            calls.append(fault)
            if len(calls) == 8:
                raise MemoryError("mid-freeze")
            return original(*args, **kwargs)

        monkeypatch.setattr(restore, "_freeze_native", fail)
    else:
        name = {
            "projection": "RestoredProfileProjection",
            "batch": "RestoredBatchSet",
            "result": "RestoredProfileResult",
        }[fault]

        def fail(*args, **kwargs):
            calls.append(fault)
            raise MemoryError("injected fullview constructor")

        monkeypatch.setattr(restore, name, fail)
    ledger = RestoreLedger()
    with pytest.raises(RestoreFailure) as caught:
        support.restore_capture(captured, ledger=ledger, fullview=True)
    assert calls
    assert caught.value.__cause__ is None and caught.value.__context__ is None
    assert ledger.state == "failed"
    if fault != "live":
        assert not any(v for _, v in ledger.live)
    tb = caught.value.__traceback__
    frames = []
    while tb:
        if tb.tb_frame.f_code.co_name == "_restore_operation":
            frames.append(tb.tb_frame)
        tb = tb.tb_next
    assert len(frames) == 1
    for name in (
        "children",
        "parse_usage",
        "caps",
        "projection",
        "inner_batches",
        "retention",
        "outcome",
        "decoder",
    ):
        assert frames[0].f_locals[name] is None, (fault, name)
    gc.collect()
    assert not (set(rule_terms._ISSUED_VALUES) - original_ids)


def test_fullview_success_transfers_pv_holding_instead_of_claiming_cleanup_frees_it(captured):
    gc.collect()
    original_ids = set(rule_terms._ISSUED_VALUES)
    result, ledger = support.restore_capture(captured, fullview=True)
    assert not any(v for _, v in ledger.live)
    gc.collect()
    new_ids = set(rule_terms._ISSUED_VALUES) - original_ids
    assert new_ids
    assert dict(result.retention)["scalar"] > 0
    assert dict(result.retention)["objects"] > 2 * ledger.J
    del result
    gc.collect()
    assert not (set(rule_terms._ISSUED_VALUES) - original_ids)


def test_fullview_object_reservation_precedes_freeze_delegate(captured, monkeypatch):
    calls = []
    original_reserve = RestoreLedger.reserve
    original_freeze = restore._freeze_native

    def reserve(self, domain, amount=1, *, stage="entry"):
        if domain == "objects" and stage == "A16" and amount == 2 * self.J:
            raise RestoreFailure("RESTORE_LIMIT", "resource", stage=stage, domain=domain)
        return original_reserve(self, domain, amount, stage=stage)

    def freeze(*args, **kwargs):
        calls.append(1)
        return original_freeze(*args, **kwargs)

    monkeypatch.setattr(RestoreLedger, "reserve", reserve)
    monkeypatch.setattr(restore, "_freeze_native", freeze)
    ledger = RestoreLedger()
    with pytest.raises(RestoreFailure) as caught:
        support.restore_capture(captured, ledger=ledger, fullview=True)
    assert caught.value.classification == "resource"
    assert not calls
    assert ledger.state == "failed" and not any(v for _, v in ledger.live)
