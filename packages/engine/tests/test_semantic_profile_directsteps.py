"""Independent pure inputs -> actual explanation production -> strict restoration.

Expected finite witnesses below were worked out before the new implementation.
They do not enter production. Helper fault cases are explicitly not graph runs.
"""

import copy
import gc
import hashlib
import json
import os
from dataclasses import MISSING, FrozenInstanceError, fields, replace
from pathlib import Path
from unittest.mock import patch

import pytest
from ontolearn_engine import semantic, semantic_execution
from ontolearn_engine import semantic_profile_directsteps as direct
from ontolearn_engine import semantic_profile_production as production
from ontolearn_engine import semantic_profile_restore as restore
from ontolearn_engine.quality import rule_terms
from ontolearn_engine.quality.rule_firing import RuleSpec, Triple, Variable
from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION, ROOT, semantic_identity
from ontolearn_engine.semantic_profile_input import (
    CaptureLedger,
    MaterialFailure,
    prepare_profile_material,
)
from ontolearn_engine.semantic_profile_restore_budget import RestoreFailure, RestoreLedger
from test_semantic_profile_restore import canonical, signature, thaw_view

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
XSD = "http://www.w3.org/2001/XMLSchema#"
OWL = "http://www.w3.org/2002/07/owl#"
TYPE = RDF + "type"
SUB = RDFS + "subClassOf"
DOMAIN = RDFS + "domain"
RANGE = RDFS + "range"
SCHEMA = json.loads((ROOT / "v2/schema.json").read_bytes())
D_DOMAINS = ("work", "scan_copy", "objects", "scalar")


@pytest.fixture(autouse=True)
def actual_fee_observer(monkeypatch, request):
    """Optional raw fee metadata export; wrappers never supply a result or fee."""
    directory = os.environ.get("I05_DIRECTSTEPS_FEE_EVIDENCE_DIR")
    if not directory:
        yield
        return
    destination = Path(directory)
    destination.mkdir(parents=True, exist_ok=True)
    name = hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:24]
    path = destination / (name + ".jsonl")
    sequence = 0

    def record(ledger, method):
        nonlocal sequence
        sequence += 1
        events = getattr(ledger, "events", None)
        packet = {
            "test": request.node.nodeid,
            "pid": os.getpid(),
            "sequence": sequence,
            "observedAfterActualMethod": method,
            "state": ledger.state,
            "usage": ledger.used,
            "retained": ledger.live,
            "peaks": ledger.peaks,
            "caps": ledger.caps,
            "eventsAvailable": type(events) in (tuple, list),
            "events": events,
            "containsNativeOrInput": False,
        }
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(packet, ensure_ascii=False, separators=(",", ":")) + "\n")

    def observer(name, original):
        def observed(ledger, *args, **kwargs):
            outcome = original(ledger, *args, **kwargs)
            record(ledger, name)
            return outcome

        return observed

    for name in ("completed", "transferred", "failed", "receipt"):
        original = getattr(direct.DirectStepsLedger, name)
        monkeypatch.setattr(direct.DirectStepsLedger, name, observer(name, original))
    yield


def iri(value, source=None):
    return TermInput("iri", value, source=source)


def key(subject, predicate, object_):
    return tuple("<" + value + ">" for value in (subject, predicate, object_))


def records(rows):
    return tuple(tuple(iri(value) for value in row) for row in rows)


def leaf_reference(triple_key):
    raw = ("i05-profile-proof-leaf/1\0" + "\0".join(triple_key)).encode()
    return "i05-proof:" + hashlib.sha256(raw).hexdigest()


def leaf(triple_key):
    return {"kind": "leaf", "reference": leaf_reference(triple_key)}


def step(ordinal, rule, result, premises, depth):
    return {
        "ordinal": ordinal,
        "rule": rule,
        "result": result,
        "premises": premises,
        "depth": depth,
    }


def carrier(*steps):
    return {"format": "i05-direct-rdfs-steps/1", "steps": steps}


def four_branch_case(name):
    if name == "type":
        rows = (("urn:x", TYPE, "urn:A"), ("urn:A", SUB, "urn:B"))
        expected = carrier(
            step(
                0,
                "rdfs9-type-via-subclass",
                key("urn:x", TYPE, "urn:B"),
                tuple(leaf(key(*row)) for row in rows),
                1,
            )
        )
    elif name == "domain-depth2":
        rows = (("urn:p", DOMAIN, "urn:A"), ("urn:x", "urn:p", "urn:y"), ("urn:A", SUB, "urn:B"))
        expected = carrier(
            step(
                0,
                "rdfs2-domain",
                key("urn:x", TYPE, "urn:A"),
                (leaf(key(*rows[0])), leaf(key(*rows[1]))),
                1,
            ),
            step(
                1,
                "rdfs9-type-via-subclass",
                key("urn:x", TYPE, "urn:B"),
                ({"kind": "step", "ordinal": 0}, leaf(key(*rows[2]))),
                2,
            ),
        )
    elif name == "range":
        rows = (("urn:p", RANGE, "urn:C"), ("urn:x", "urn:p", "urn:y"))
        expected = carrier(
            step(
                0,
                "rdfs3-range",
                key("urn:y", TYPE, "urn:C"),
                tuple(leaf(key(*row)) for row in rows),
                1,
            )
        )
    else:
        assert name == "subclass"
        rows = (("urn:A", SUB, "urn:B"), ("urn:B", SUB, "urn:C"))
        expected = carrier(
            step(
                0,
                "rdfs11-subclass-transitive",
                key("urn:A", SUB, "urn:C"),
                tuple(leaf(key(*row)) for row in rows),
                1,
            )
        )
    return records(rows), expected


def produce(raw_records, rules=(), *, disabled=(), direct_ledger=None):
    material = prepare_profile_material(
        rules=rules, records=raw_records, disabled_rule_ids=disabled
    )
    ledger = direct.DirectStepsLedger() if direct_ledger is None else direct_ledger
    result = production.execute_profile_explanation(
        material,
        error_catalog=CONTRACT.ERROR_CATALOG,
        error_schema=SCHEMA,
        ledger=CaptureLedger(),
        direct_ledger=ledger,
    )
    return result, ledger


def expectation(produced):
    payload = produced.wire["payload"]
    return restore.ExplanationRestoreExpectation(
        payload_digest=hashlib.sha256(produced.payload_json).hexdigest(),
        rows_digest=hashlib.sha256(produced.rows_json).hexdigest(),
        input_digest=payload["inputDigest"],
        input_domain=payload["inputDigestDomain"],
        source_digest=payload["sourceDigest"],
        definitions_digest=payload["definitionsDigest"],
        catalog_digest=hashlib.sha256(produced.catalog_json).hexdigest(),
        implementation=tuple(sorted(payload["implementation"].items())),
        input_preimage=produced.material.input_preimage,
        source_preimage=produced.material.source_preimage,
    )


def receive(produced, *, direct_ledger=None, expected=None, wire=None):
    ledger = direct.DirectStepsLedger() if direct_ledger is None else direct_ledger
    payload, rows = (produced.payload_json, produced.rows_json) if wire is None else wire
    result = restore.restore_profile_explanation_result(
        payload,
        rows,
        expected=expectation(produced) if expected is None else expected,
        allocation=produced.original_allocation,
        ledger=RestoreLedger(),
        direct_ledger=ledger,
    )
    return result, ledger


def rebound(produced, payload):
    raw = canonical(payload)
    text = raw.decode()
    rows = canonical([[text[index : index + 8192]] for index in range(0, len(text), 8192)])
    return (raw, rows), replace(
        expectation(produced),
        payload_digest=hashlib.sha256(raw).hexdigest(),
        rows_digest=hashlib.sha256(rows).hexdigest(),
    )


def assert_event_chain(ledger):
    previous = None
    for event in ledger.events:
        assert type(event) is tuple and len(event) == 12
        assert event[4] <= event[5] and event[6] <= event[7]
        if previous is not None:
            assert (previous[5], previous[7], previous[9], previous[11]) == (
                event[4],
                event[6],
                event[8],
                event[10],
            )
        previous = event


def assert_finite(error):
    assert error.__cause__ is None and error.__context__ is None
    assert not hasattr(error, "partial_result")
    assert not hasattr(error, "directSteps")


@pytest.fixture(scope="module")
def produced():
    return produce(four_branch_case("domain-depth2")[0])[0]


@pytest.mark.parametrize("name", ["type", "domain-depth2", "range", "subclass"])
def test_actual_four_branches_ordered_premises_depth_and_fullview(name):
    raw, expected_steps = four_branch_case(name)
    with patch.object(semantic, "_profile_reason", wraps=semantic._profile_reason) as reason:
        computed, ledger = produce(raw)
    assert reason.call_count == 1
    assert signature(computed.native_result["directSteps"]) == signature(expected_steps)
    assert computed.version == "i05-profile-explanation-computation/1"
    assert computed.wire["payload"]["format"] == "i05-reasoning-result/3"
    assert computed.native_result["formatVersion"] == "i05-reasoning-result/3"
    assert computed.native_result["semanticsVersion"] == "i05-finite-8"
    assert computed.wire["payload"]["implementation"] == semantic_identity(
        profile=True, explanation=True
    )
    assert len(computed.wire["payload"]) == 7 and len(computed.native_result) == 16
    assert all(len(child) == 11 for child in computed.native_result["mechanismBatches"])
    assert ledger.state == "completed"
    assert dict(computed.direct_receipt.usage) == ledger.used
    assert dict(computed.direct_receipt.peaks) == ledger.peaks
    assert dict(computed.direct_receipt.retained) == ledger.live
    assert_event_chain(ledger)
    expected_wire = computed.wire["payload"]["reasoning"]["directSteps"]
    assert expected_wire["steps"][0]["ordinal"] == {"integerHex": "0x0"}
    assert expected_wire["steps"][0]["depth"] == {"integerHex": "0x1"}

    def forbidden(*args, **kwargs):
        raise AssertionError("restore must not reason or match")

    with (
        patch.object(semantic, "_profile_reason", forbidden),
        patch.object(semantic, "_finite_matches", forbidden),
    ):
        view, received = receive(computed)
    assert signature(thaw_view(view.projection.payload)) == signature(
        {**computed.wire["payload"], "reasoning": computed.native_result}
    )
    assert view.rows_json is computed.rows_json
    assert view.projection.version == "i05-profile-explanation-projection/1"
    assert view.version == "i05-profile-explanation-restored/1"
    assert received.state == "completed"
    assert dict(view.direct_receipt.usage) == received.used
    assert dict(view.direct_receipt.peaks) == received.peaks
    assert dict(view.direct_receipt.retained) == received.live
    assert_event_chain(received)
    assert dict(view.direct_receipt.retained)["objects"] > 0
    assert not view.batches.formal_authority and not view.batches.aggregate_recomputed


@pytest.mark.parametrize("reverse", [False, True])
def test_same_round_first_witness_is_ordered_input_key_not_raw_order_and_duplicates_are_charged(
    monkeypatch, reverse
):
    rows = (
        ("urn:x", TYPE, "urn:B"),
        ("urn:B", SUB, "urn:Z"),
        ("urn:x", TYPE, "urn:A"),
        ("urn:A", SUB, "urn:Z"),
    )
    if reverse:
        rows = tuple(reversed(rows))
    calls = []
    original = direct._DirectStepsCapture.candidate

    def observe(capture, rule):
        calls.append(rule)
        return original(capture, rule)

    monkeypatch.setattr(direct._DirectStepsCapture, "candidate", observe)
    computed, _ = produce(records(rows))
    expected = carrier(
        step(
            0,
            "rdfs9-type-via-subclass",
            key("urn:x", TYPE, "urn:Z"),
            (leaf(key("urn:x", TYPE, "urn:A")), leaf(key("urn:A", SUB, "urn:Z"))),
            1,
        )
    )
    assert signature(computed.native_result["directSteps"]) == signature(expected)
    # Two competitors in the first round, both revisited in the terminal round.
    assert calls == ["rdfs9-type-via-subclass"] * 4
    assert len(computed.native_result["rdfsEvidence"]) == 1
    assert computed.native_result["rdfsEvidence"][0]["proofLeaves"] == tuple(
        sorted(
            (
                leaf_reference(key("urn:x", TYPE, "urn:A")),
                leaf_reference(key("urn:A", SUB, "urn:Z")),
            )
        )
    )


def test_no_new_rdfs_is_explicit_empty_carrier_and_raw_aliases_are_not_rewritten():
    source_a, source_b = SourceRecord("", None, "", "raw a"), SourceRecord(None, "", None, "raw b")
    raw = records(
        (("urn:p", TYPE, OWL + "DatatypeProperty"), ("urn:q", TYPE, OWL + "DatatypeProperty"))
    ) + tuple(
        (iri("urn:x"), iri(predicate), value)
        for predicate, value in (
            ("urn:p", TermInput("literal", "same", source=source_a)),
            ("urn:p", TermInput("literal", "same", XSD + "string", source=source_b)),
            ("urn:p", TermInput("literal", "Word", language_raw="EN-us", source=source_a)),
            ("urn:p", TermInput("literal", "Word", language_raw="en-US", source=source_b)),
            ("urn:q", TermInput("literal", "01", XSD + "integer", source=source_a)),
            ("urn:q", TermInput("literal", "1", XSD + "integer", source=source_b)),
        )
    )
    computed, _ = produce(raw)
    assert signature(computed.native_result["directSteps"]) == signature(carrier())
    assert len(computed.native_result["proofLeaves"]) == 6
    values = tuple(item["value"] for item in computed.native_result["termSources"])
    assert signature(values) == signature(tuple(term for row in raw for term in row))
    view, _ = receive(computed)
    assert signature(thaw_view(view.projection.payload)["reasoning"]) == signature(
        computed.native_result
    )
    with pytest.raises(FrozenInstanceError):
        view.projection.payload.entries = ()
    with pytest.raises(TypeError):
        view.projection.payload["reasoning"]["directSteps"] = None


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "missing-step",
        "extra-step",
        "extra-leaf",
        "extra",
        "bool-depth",
        "depth",
        "ordinal",
        "self-ref",
        "forward-ref",
        "last-ref",
        "last-result",
        "rule",
        "premise-order",
        "last-leaf-union",
        "last-source",
    ],
)
def test_last_step_and_original_tail_fields_reject_atomic_rebound_wire(produced, mutation):
    payload = copy.deepcopy(produced.wire["payload"])
    reasoning = payload["reasoning"]
    data = reasoning["directSteps"]
    last = data["steps"][-1]
    if mutation == "missing":
        del reasoning["directSteps"]
    elif mutation == "missing-step":
        data["steps"].pop()
    elif mutation == "extra-step":
        extra = copy.deepcopy(last)
        extra["ordinal"] = {"integerHex": "0x2"}
        data["steps"].append(extra)
    elif mutation == "extra-leaf":
        fake = key("urn:unasserted", TYPE, "urn:A")
        reasoning["proofLeaves"].append({"reference": leaf_reference(fake), "triple": list(fake)})
    elif mutation == "extra":
        data["unrecognized"] = None
    elif mutation == "bool-depth":
        last["depth"] = True
    elif mutation == "depth":
        last["depth"] = {"integerHex": "0x1"}
    elif mutation == "ordinal":
        last["ordinal"] = {"integerHex": "0x0"}
    elif mutation in ("self-ref", "forward-ref"):
        last["premises"][0] = {
            "kind": "step",
            "ordinal": {"integerHex": "0x1" if mutation == "self-ref" else "0x2"},
        }
    elif mutation == "last-ref":
        last["premises"][-1]["reference"] = "i05-proof:" + "0" * 64
    elif mutation == "last-result":
        last["result"][-1] = "<urn:other>"
    elif mutation == "rule":
        last["rule"] = "rdfs2-domain"
    elif mutation == "premise-order":
        data["steps"][0]["premises"].reverse()
    elif mutation == "last-leaf-union":
        reasoning["rdfsEvidence"][-1]["proofLeaves"].pop()
    else:
        reasoning["termSources"][-1]["value"]["source"] = {
            "recordType": "SourceRecord",
            "reference": "forged",
            "digest": None,
            "revision": None,
            "text": None,
        }
    wire, expected = rebound(produced, payload)
    ledger = direct.DirectStepsLedger()
    with pytest.raises((direct.DirectStepsFailure, RestoreFailure)) as caught:
        receive(produced, direct_ledger=ledger, expected=expected, wire=wire)
    assert_finite(caught.value)
    assert ledger.state == "failed"


@pytest.mark.parametrize(
    "field,value",
    [
        ("format", "i05-reasoning-result/2"),
        ("semanticsVersion", "i05-finite-7"),
        ("formatVersion", "i05-reasoning-result/2"),
        ("direct-format", "i05-direct-rdfs-steps/2"),
        ("identity", "i05-finite-7"),
    ],
)
def test_versions_are_explicit_not_guessed_from_keys(produced, field, value):
    payload = copy.deepcopy(produced.wire["payload"])
    if field == "format":
        payload["format"] = value
    elif field == "identity":
        payload["implementation"]["executionSemanticsVersion"] = value
    elif field == "direct-format":
        payload["reasoning"]["directSteps"]["format"] = value
    else:
        payload["reasoning"][field] = value
    wire, expected = rebound(produced, payload)
    with pytest.raises((direct.DirectStepsFailure, RestoreFailure)):
        receive(produced, expected=expected, wire=wire)


def test_old_defaults_keep_old_bytes_and_old_reader_rejects_new_field(produced):
    material = prepare_profile_material(records=four_branch_case("domain-depth2")[0])
    old = production.execute_admitted_profile_job(
        material, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=SCHEMA
    )
    assert (
        old.wire["payload"]["format"]
        == old.native_result["formatVersion"]
        == "i05-reasoning-result/2"
    )
    assert old.native_result["semanticsVersion"] == "i05-finite-7"
    assert "directSteps" not in old.native_result and len(old.native_result) == 15
    old_facade = semantic_execution.execute_profile_records(
        material.records, material.rules, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=SCHEMA
    )
    assert old.wire == old_facade
    assert old.payload_json == canonical(old_facade["payload"])
    assert old.rows_json == canonical(old_facade["rows"])
    normalized = dict(produced.native_result)
    normalized.pop("directSteps")
    normalized["formatVersion"] = "i05-reasoning-result/2"
    normalized["semanticsVersion"] = "i05-finite-7"
    assert signature(normalized) == signature(old.native_result)
    assert semantic_identity(profile=True)["executionSemanticsVersion"] == "i05-finite-7"
    old_expected = restore.RestoreExpectation(
        **{
            f.name: getattr(expectation(produced), f.name)
            for f in fields(restore.RestoreExpectation)
            if f.init and f.default is MISSING
        }
    )
    with pytest.raises(RestoreFailure):
        restore.restore_profile_result(
            produced.payload_json,
            produced.rows_json,
            expected=old_expected,
            allocation=produced.original_allocation,
            ledger=RestoreLedger(),
        )
    changed = copy.deepcopy(old.wire["payload"])
    changed["reasoning"]["directSteps"] = {"format": "i05-direct-rdfs-steps/1", "steps": []}
    raw = canonical(changed)
    text = raw.decode()
    rows = canonical([[text[i : i + 8192]] for i in range(0, len(text), 8192)])
    # Bind the old input to its actual original context, not the new result.
    old_expected = restore.RestoreExpectation(
        hashlib.sha256(raw).hexdigest(),
        hashlib.sha256(rows).hexdigest(),
        old.wire["payload"]["inputDigest"],
        old.wire["payload"]["inputDigestDomain"],
        old.wire["payload"]["sourceDigest"],
        old.wire["payload"]["definitionsDigest"],
        hashlib.sha256(old.catalog_json).hexdigest(),
        tuple(sorted(old.wire["payload"]["implementation"].items())),
        material.input_preimage,
        material.source_preimage,
    )
    with pytest.raises(RestoreFailure):
        restore.restore_profile_result(
            raw,
            rows,
            expected=old_expected,
            allocation=old.original_allocation,
            ledger=RestoreLedger(),
        )


def test_turtle_explanation_is_not_implicitly_upgraded():
    material = prepare_profile_material("<urn:x> <urn:p> <urn:y> .")
    with patch.object(semantic, "_profile_reason", wraps=semantic._profile_reason) as reason:
        with pytest.raises((direct.DirectStepsFailure, MaterialFailure)) as caught:
            production.execute_profile_explanation(
                material,
                error_catalog=CONTRACT.ERROR_CATALOG,
                error_schema=SCHEMA,
                ledger=CaptureLedger(),
                direct_ledger=direct.DirectStepsLedger(),
            )
    assert reason.call_count == 0
    assert_finite(caught.value)


@pytest.mark.parametrize("phase", ["produce", "restore", "roots"])
@pytest.mark.parametrize("domain", D_DOMAINS)
def test_each_actual_direct_pool_exact_and_one_short(produced, phase, domain):
    view = None

    def operation(ledger):
        if phase == "produce":
            return produce(produced.material.records, direct_ledger=ledger)[0]
        if phase == "restore":
            return receive(produced, direct_ledger=ledger)[0]
        return restore.explanation_roots(view, (key("urn:x", TYPE, "urn:B"),), direct_ledger=ledger)

    if phase == "roots":
        view = receive(produced)[0]
    baseline = direct.DirectStepsLedger()
    operation(baseline)
    required = baseline.used[domain] if domain in ("work", "scan_copy") else baseline.peaks[domain]
    assert required > 0
    exact = direct.DirectStepsLedger(overrides=((domain, required),))
    operation(exact)
    short = direct.DirectStepsLedger(overrides=((domain, required - 1),))
    with pytest.raises(direct.DirectStepsFailure) as caught:
        operation(short)
    assert caught.value.reason == "DIRECT_STEPS_LIMIT" and caught.value.domain == domain
    assert short.state == "failed"
    assert_finite(caught.value)
    prior = dict(short.used)
    with pytest.raises(direct.DirectStepsFailure) as reused:
        operation(short)
    assert reused.value.reason == "DIRECT_STEPS_REUSED"
    assert short.used == prior


@pytest.mark.parametrize("limit", [0, 127])
def test_direct_control_budget_rejects_before_counter_allocation(limit):
    ledger = direct.DirectStepsLedger(overrides=(("objects", limit),))
    with pytest.raises(direct.DirectStepsFailure) as caught:
        ledger.begin()
    assert caught.value.reason == "DIRECT_STEPS_LIMIT"
    assert ledger.used is ledger.live is ledger.peaks is ledger.caps is None


def test_control_128_exact_and_scan_work_are_separate_real_domains():
    limited = direct.DirectStepsLedger(overrides=(("objects", 128),))
    limited.begin()
    assert limited.live["objects"] == limited.peaks["objects"] == 128
    with pytest.raises(direct.DirectStepsFailure):
        limited.reserve("objects", 1)
    ledger = direct.DirectStepsLedger()
    ledger.begin()
    before_work, before_scan = ledger.used["work"], ledger.used["scan_copy"]
    ledger.debit("scan_copy", 13)
    assert ledger.used["work"] >= before_work + 13
    assert ledger.used["scan_copy"] == before_scan + 13
    assert ledger.events
    assert_event_chain(ledger)
    for event in ledger.events:
        assert type(event) is tuple and len(event) == 12
        assert event[4] <= event[5] and event[6] <= event[7]
        assert 0 <= event[9] <= ledger.caps["objects"]
        assert 0 <= event[11] <= ledger.caps["scalar"]


def test_identity_encoding_keeps_rdf_aliases_and_lexical_distinctions():
    ledger = direct.DirectStepsLedger()
    ledger.begin(stage="restore")

    def encoded(value):
        return direct.encode_identity_key((iri("urn:x"), iri("urn:p"), value), ledger)

    assert encoded(TermInput("literal", "same")) == encoded(
        TermInput("literal", "same", XSD + "string")
    )
    assert encoded(TermInput("literal", "Word", language_raw="EN-us")) == encoded(
        TermInput("literal", "Word", language_raw="en-US")
    )
    assert encoded(TermInput("literal", "01", XSD + "integer")) != encoded(
        TermInput("literal", "1", XSD + "integer")
    )
    assert encoded(iri("urn:same")) != encoded(TermInput("literal", "urn:same"))
    original = ("<urn:α>", "<urn:p>", '"a\\"b"')
    expected = b"".join(len(part.encode()).to_bytes(8, "big") + part.encode() for part in original)
    assert direct.encode_triple_key(original, ledger) == expected


def test_helper_duplicate_insert_is_not_a_real_late_shorter_graph_and_never_publishes_prefix():
    ledger = direct.DirectStepsLedger()
    capture = direct._DirectStepsCapture(ledger)
    rule = "rdfs9-type-via-subclass"
    capture.candidate(rule)
    capture.insert(
        key("urn:x", TYPE, "urn:B"),
        (key("urn:x", TYPE, "urn:A"), key("urn:A", SUB, "urn:B")),
        rule,
    )
    capture.end_candidates(1)
    capture.candidate(rule)
    capture.insert(
        key("urn:x", TYPE, "urn:C"),
        (key("urn:x", TYPE, "urn:B"), key("urn:B", SUB, "urn:C")),
        rule,
    )
    capture.end_candidates(1)
    # A deliberately supplied helper sequence, never called a closure result:
    # existing x:C follows step x:B (depth 2), whereas the two supplied seeds
    # below would give depth 1. Real complete batch closure cannot do this.
    before = dict(ledger.used)
    capture.candidate(rule)
    with pytest.raises(direct.DirectStepsFailure) as caught:
        capture.insert(
            key("urn:x", TYPE, "urn:C"),
            (key("urn:x", TYPE, "urn:A"), key("urn:A", SUB, "urn:C")),
            rule,
        )
    assert caught.value.reason == "DIRECT_STEPS_INVALID"
    assert ledger.state == "failed"
    assert all(ledger.used[name] >= spent for name, spent in before.items())
    with pytest.raises(direct.DirectStepsFailure):
        capture.finish()


def test_helper_unresolved_seed_cannot_escape_as_carrier():
    ledger = direct.DirectStepsLedger()
    capture = direct._DirectStepsCapture(ledger)
    rule = "rdfs9-type-via-subclass"
    capture.candidate(rule)
    capture.insert(
        key("urn:x", TYPE, "urn:B"), (key("urn:x", TYPE, "urn:A"), key("urn:A", SUB, "urn:B")), rule
    )
    capture.end_candidates(1)
    with pytest.raises(direct.DirectStepsFailure) as caught:
        capture.finish()
    assert caught.value.reason == "DIRECT_STEPS_INVALID"
    assert ledger.state == "failed"


def test_roots_retain_every_real_rule_head_occurrence_and_do_not_feed_rule_chains():
    raw = records(
        (
            ("urn:p", TYPE, OWL + "ObjectProperty"),
            ("urn:out", TYPE, OWL + "ObjectProperty"),
            ("urn:x", "urn:p", "urn:y"),
        )
    )
    when = Triple(Variable("?s"), iri("urn:p"), Variable("?o"))
    head = Triple(Variable("?s"), iri("urn:out"), Variable("?o"))
    rule = RuleSpec(
        "fixture:r", (when,), (), (head, head), source=SourceRecord("fixture:rule", "", "v1", None)
    )
    computed, _ = produce(raw, (rule,))
    assert len(computed.wire["payload"]) == 7 and len(computed.native_result) == 16
    assert len(computed.native_result["mechanismBatches"]) == 1
    assert len(computed.native_result["mechanismBatches"][0]) == 11
    assert len(computed.native_result["firingGroups"]) == 1
    assert len(computed.native_result["firingGroups"][0].heads) == 2
    assert computed.native_result["directSteps"] == carrier()
    view, _ = receive(computed)
    roots = restore.explanation_roots(
        view, (key("urn:x", "urn:out", "urn:y"),), direct_ledger=direct.DirectStepsLedger()
    )
    assert signature(roots) == signature(
        (
            {"kind": "ruleHead", "firingIndex": 0, "headIndex": 0},
            {"kind": "ruleHead", "firingIndex": 0, "headIndex": 1},
        )
    )
    assert (
        restore.explanation_roots(
            view, (key("urn:absent", TYPE, "urn:none"),), direct_ledger=direct.DirectStepsLedger()
        )
        == ()
    )
    assert not hasattr(view, "scope") and not hasattr(view, "permission")


@pytest.mark.parametrize(
    "where", ["producer-receipt", "producer-record", "restore-record", "last-child"]
)
def test_late_faults_keep_finite_error_and_no_new_native_values_in_public_traceback(
    monkeypatch, where
):
    raw = records(
        (
            ("urn:p", TYPE, OWL + "ObjectProperty"),
            ("urn:out", TYPE, OWL + "ObjectProperty"),
            ("urn:x", "urn:p", "urn:y"),
        )
    )
    spec = RuleSpec(
        "a",
        (Triple(Variable("?s"), iri("urn:p"), Variable("?o")),),
        (),
        (Triple(Variable("?s"), iri("urn:out"), Variable("?o")),),
    )
    computed = produce(raw, (spec, replace(spec, rule_id="z")))[0]
    gc.collect()
    previous = set(rule_terms._ISSUED_VALUES)

    def fail(*args, **kwargs):
        raise MemoryError("controlled new explanation publication failure")

    if where == "producer-receipt":
        # This explicit fault replaces the metadata observer for this method.
        monkeypatch.setattr(direct.DirectStepsLedger, "receipt", fail)
    elif where == "producer-record":
        monkeypatch.setattr(production, "ProfileExplanationComputation", fail)
    elif where == "restore-record":
        monkeypatch.setattr(restore, "RestoredExplanationResult", fail)
    else:
        calls = []
        original = restore.check_firing_batch

        def fail_last(*args, **kwargs):
            calls.append(1)
            result = original(*args, **kwargs)
            if len(calls) == 2:
                raise MemoryError("controlled last completed child failure")
            return result

        monkeypatch.setattr(restore, "check_firing_batch", fail_last)
    ledger = direct.DirectStepsLedger()
    with pytest.raises((direct.DirectStepsFailure, MaterialFailure, RestoreFailure)) as caught:
        if where.startswith("producer"):
            produce(raw, (spec,), direct_ledger=ledger)
        else:
            receive(computed, direct_ledger=ledger)
    assert_finite(caught.value)
    assert ledger.state == "failed"
    tb = caught.value.__traceback__
    while tb is not None:
        frame = tb.tb_frame
        if frame.f_globals.get("__name__", "").startswith("ontolearn_engine.semantic_profile_"):
            for value in frame.f_locals.values():
                assert not (type(value) is dict and "mechanismBatches" in value)
                assert type(value).__name__ not in (
                    "ProfileExplanationComputation",
                    "RestoredExplanationResult",
                )
        tb = tb.tb_next
    gc.collect()
    assert not (set(rule_terms._ISSUED_VALUES) - previous)


def test_explanation_identity_is_exact_explicit_and_does_not_mutate_infrastructure():
    original = dict(IMPLEMENTATION)
    legacy = semantic_identity()
    old = semantic_identity(profile=True)
    new = semantic_identity(profile=True, explanation=True)
    assert legacy["executionSemanticsVersion"] == "i05-finite-6"
    assert old["executionSemanticsVersion"] == "i05-finite-7"
    assert new == {**old, "executionSemanticsVersion": "i05-finite-8"}
    assert IMPLEMENTATION == original
    for kwargs in (
        {"explanation": True},
        {"profile": True, "explanation": 1},
        {"profile": 1, "explanation": True},
    ):
        with pytest.raises(ValueError):
            semantic_identity(**kwargs)


@pytest.mark.parametrize(
    "overrides", [(("unknown", 1),), (("work", True),), (("work", -1),), (("work", 1), ("work", 2))]
)
def test_direct_overrides_do_not_accept_unknown_bool_negative_or_duplicate(overrides):
    with pytest.raises(direct.DirectStepsFailure) as caught:
        direct.DirectStepsLedger(overrides=overrides)
    assert caught.value.reason == "DIRECT_STEPS_INVALID"


def test_direct_caps_match_fixed_contract_without_an_extra_wallet():
    ledger = direct.DirectStepsLedger()
    ledger.begin()
    assert ledger.caps == {
        "work": 581671040,
        "scan_copy": 581671040,
        "objects": 270635588,
        "scalar": 50331776,
    }
    assert ledger.usage is ledger.used
    assert set(ledger.used) == {"work", "scan_copy"}
    assert set(ledger.live) == {"objects", "scalar"}
    receipt = ledger.receipt()
    assert dict(receipt.usage) == ledger.used
    assert dict(receipt.retained) == ledger.live
    ledger.completed()
    before = dict(ledger.used)
    with pytest.raises(direct.DirectStepsFailure) as caught:
        ledger.begin()
    assert caught.value.reason == "DIRECT_STEPS_REUSED"
    assert ledger.used == before


def test_sort_witness_can_differ_from_candidate_generation_rule_order(monkeypatch):
    # The subclass loop emits its candidate before the separate domain loop.
    # Sorting compares premise[0] <urn:a> against <urn:x>, so domain wins.
    rows = (
        ("urn:x", TYPE, "urn:B"),
        ("urn:B", SUB, "urn:A"),
        ("urn:a", DOMAIN, "urn:A"),
        ("urn:x", "urn:a", "urn:y"),
    )
    calls = []
    original = direct._DirectStepsCapture.candidate

    def observe(capture, rule):
        calls.append(rule)
        return original(capture, rule)

    monkeypatch.setattr(direct._DirectStepsCapture, "candidate", observe)
    computed, _ = produce(records(rows))
    assert calls == ["rdfs9-type-via-subclass", "rdfs2-domain"] * 2
    expected = carrier(
        step(
            0,
            "rdfs2-domain",
            key("urn:x", TYPE, "urn:A"),
            (leaf(key(*rows[2])), leaf(key(*rows[3]))),
            1,
        )
    )
    assert signature(computed.native_result["directSteps"]) == signature(expected)
    assert computed.native_result["rdfsEvidence"][0]["proofLeaves"] == tuple(
        sorted((leaf_reference(key(*rows[2])), leaf_reference(key(*rows[3]))))
    )


def test_range_literal_guard_keeps_no_fabricated_direct_result():
    raw = (
        (iri("urn:p"), iri(RANGE), iri("urn:C")),
        (iri("urn:x"), iri("urn:p"), TermInput("literal", "not an IRI", XSD + "string")),
    )
    computed, _ = produce(raw)
    assert computed.native_result["directSteps"] == carrier()
    assert computed.native_result["rdfs"] == []
    assert len(computed.native_result["proofLeaves"]) == 2
    receive(computed)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", "i05-profile-restore-schema/1"),
        ("direct_budget_version", "i05-direct-steps-budget/0"),
        ("budget_version", "i05-profile-restore-budget/0"),
        ("cache_version", "i05-profile-restore-term-key/0"),
    ],
)
def test_exact_explanation_expectation_does_not_upgrade_other_versions(produced, field, value):
    with pytest.raises((direct.DirectStepsFailure, RestoreFailure)) as caught:
        receive(produced, expected=replace(expectation(produced), **{field: value}))
    assert_finite(caught.value)


@pytest.mark.parametrize(
    "where",
    [
        "input_preimage",
        "definition_material",
        "source_preimage",
        "definitions_preimage",
        "bytes-input_preimage",
        "bytes-definition_material",
        "nested-source",
        "nested-term-source",
    ],
)
def test_exact_material_rejects_nested_foreign_protocols_before_len_eq_or_reason(where):
    callbacks = []

    class ForeignMeta(type):
        def __eq__(cls, other):
            callbacks.append("class-eq")
            raise AssertionError("foreign metaclass equality must not run")

    class Foreign(metaclass=ForeignMeta):
        def __len__(self):
            callbacks.append("len")
            raise AssertionError("foreign length must not run")

        def __eq__(self, other):
            callbacks.append("eq")
            raise AssertionError("foreign equality must not run")

    class ForeignBytes(bytes):
        def __len__(self):
            callbacks.append("bytes-len")
            raise AssertionError("bytes subclass length must not run")

        def __eq__(self, other):
            callbacks.append("bytes-eq")
            raise AssertionError("bytes subclass equality must not run")

    material = prepare_profile_material(records=four_branch_case("type")[0])
    if where.startswith("bytes-"):
        changed = replace(material, **{where.removeprefix("bytes-"): ForeignBytes(b"foreign")})
    elif where == "nested-source":
        changed = replace(material, source=(Foreign(),))
    elif where == "nested-term-source":
        first = material.records[0]
        changed_row = (replace(first[0], source=Foreign()), first[1], first[2])
        changed = replace(material, records=(changed_row,) + material.records[1:])
    else:
        changed = replace(material, **{where: Foreign()})
    assert type(changed) is type(material)
    ledger = direct.DirectStepsLedger()
    with patch.object(semantic, "_profile_reason", wraps=semantic._profile_reason) as reason:
        with pytest.raises((direct.DirectStepsFailure, MaterialFailure)) as caught:
            production.execute_profile_explanation(
                changed,
                error_catalog=CONTRACT.ERROR_CATALOG,
                error_schema=SCHEMA,
                ledger=CaptureLedger(),
                direct_ledger=ledger,
            )
    assert callbacks == []
    assert reason.call_count == 0 and ledger.state == "failed"
    assert_finite(caught.value)


def test_exact_explanation_expectation_rejects_foreign_domain_without_len_or_eq(produced):
    callbacks = []

    class ForeignDomain:
        def __len__(self):
            callbacks.append("len")
            raise AssertionError("foreign domain length must not run")

        def __eq__(self, other):
            callbacks.append("eq")
            raise AssertionError("foreign domain equality must not run")

    expected = replace(expectation(produced), input_domain=ForeignDomain())
    assert type(expected) is restore.ExplanationRestoreExpectation
    ledger = direct.DirectStepsLedger()
    with pytest.raises((direct.DirectStepsFailure, RestoreFailure)) as caught:
        receive(produced, expected=expected, direct_ledger=ledger)
    assert callbacks == [] and ledger.state == "failed"
    assert_finite(caught.value)


def test_uniform_leaf_rename_with_rebound_envelope_cannot_replace_original_triple_hash(produced):
    payload = copy.deepcopy(produced.wire["payload"])
    first_leaf = payload["reasoning"]["proofLeaves"][0]
    original_id = first_leaf["reference"]
    original_triple = tuple(first_leaf["triple"])
    forged_id = "i05-proof:" + "0" * 64
    assert original_id == leaf_reference(original_triple)
    assert forged_id != leaf_reference(original_triple)
    replacements = []

    def rename(value):
        if type(value) is str:
            if value == original_id:
                replacements.append(1)
                return forged_id
            return value
        if type(value) is list:
            return [rename(item) for item in value]
        if type(value) is dict:
            return {name: rename(item) for name, item in value.items()}
        return value

    payload = rename(payload)
    assert len(replacements) >= 3  # Original leaf, direct premise and RDFS leaf-union refs.
    assert tuple(payload["reasoning"]["proofLeaves"][0]["triple"]) == original_triple
    assert original_id not in canonical(payload).decode()
    wire, expected = rebound(produced, payload)
    assert expected.input_preimage is produced.material.input_preimage
    assert expected.source_preimage is produced.material.source_preimage
    ledger = direct.DirectStepsLedger()
    with pytest.raises((direct.DirectStepsFailure, RestoreFailure)) as caught:
        receive(produced, wire=wire, expected=expected, direct_ledger=ledger)
    assert caught.value.reason in ("DIRECT_STEPS_INVALID", "RESTORE_INPUT_INVALID")
    assert ledger.state == "failed"
    assert_finite(caught.value)


def test_rebound_evidence_cannot_invent_firing_1023_head_15_from_two_typed_heads():
    raw = records(
        (
            ("urn:p", TYPE, OWL + "ObjectProperty"),
            ("urn:out", TYPE, OWL + "ObjectProperty"),
            ("urn:x", "urn:p", "urn:y"),
        )
    )
    when = Triple(Variable("?s"), iri("urn:p"), Variable("?o"))
    head = Triple(Variable("?s"), iri("urn:out"), Variable("?o"))
    rule = RuleSpec("fixture:r", (when,), (), (head, head))
    computed, _ = produce(raw, (rule,))
    assert len(computed.native_result["firingGroups"]) == 1
    assert tuple(item.index for item in computed.native_result["firingGroups"][0].heads) == (0, 1)
    assert len(computed.native_result["evidence"]) == 2
    payload = copy.deepcopy(computed.wire["payload"])
    original_groups = canonical(payload["reasoning"]["firingGroups"])
    payload["reasoning"]["evidence"][0]["firingIndex"] = {"integerHex": "0x3ff"}
    payload["reasoning"]["evidence"][0]["headIndex"] = {"integerHex": "0xf"}
    assert canonical(payload["reasoning"]["firingGroups"]) == original_groups
    wire, expected = rebound(computed, payload)
    ledger = direct.DirectStepsLedger()
    with patch.object(semantic, "_profile_reason", side_effect=AssertionError("no restore reason")):
        with pytest.raises((direct.DirectStepsFailure, RestoreFailure)) as caught:
            receive(computed, wire=wire, expected=expected, direct_ledger=ledger)
    # Reject the complete view, before roots can publish the nonexistent occurrence.
    assert caught.value.reason in ("DIRECT_STEPS_INVALID", "RESTORE_INPUT_INVALID")
    assert ledger.state == "failed"
    assert_finite(caught.value)


def test_private_finite_closure_rejects_foreign_capture_without_candidate_callback():
    callbacks = []

    class ForeignCapture:
        def candidate(self, rule):
            callbacks.append(rule)
            raise AssertionError("foreign capture callback must not run")

    graph = semantic.parse_turtle(
        "<urn:x> <" + TYPE + "> <urn:A> . <urn:A> <" + SUB + "> <urn:B> ."
    )
    with pytest.raises(semantic.ProfileReasonError) as caught:
        semantic._finite_closure(graph, lambda: None, _direct_capture=ForeignCapture())
    assert callbacks == []
    assert caught.value.reason == "INTERNAL_ERROR"
    assert_finite(caught.value)
