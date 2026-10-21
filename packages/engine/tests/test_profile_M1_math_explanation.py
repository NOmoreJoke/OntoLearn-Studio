"""Real component observations; source operands and assertion-only goldens stay separate.

No fake Job/origin/Store/worker, comparator calls, numeric parser or new codec.
False rules have no typed trace: separately labelled real eq-self operations
observe their operands. Errors publish no result. These are component claims.
"""

import base64
import hashlib
import json
import os
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path

import pytest
from ontolearn_engine.quality.rule_calendar import Calendar
from ontolearn_engine.quality.rule_firing import Comparison, RuleSpec, Triple, Variable
from ontolearn_engine.quality.rule_numbers import Number
from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput
from ontolearn_engine.resources import CONTRACT, ROOT
from ontolearn_engine.semantic_profile_input import CaptureLedger, prepare_profile_material
from ontolearn_engine.semantic_profile_production import execute_admitted_profile_job
from ontolearn_engine.semantic_profile_restore import (
    ReadonlyObject,
    ReadonlySequence,
    RestoreExpectation,
    restore_profile_result,
)
from ontolearn_engine.semantic_profile_restore_budget import RestoreLedger

REPO = Path(__file__).resolve().parents[3]
FIXTURE = REPO / "tests/fixtures/quality/profile-M1-math-inputs.json"
GOLDENS = REPO / "docs/reviews/T05/profile-M1-math-explanation-input-contract"
SOURCE_BYTES = FIXTURE.read_bytes()
SOURCE_SHA = hashlib.sha256(SOURCE_BYTES).hexdigest()
INPUTS = json.loads(SOURCE_BYTES)
SCHEMA = json.loads((ROOT / "v2/schema.json").read_bytes())
TEST_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
XSD = "http://www.w3.org/2001/XMLSchema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
OWL = "http://www.w3.org/2002/07/owl#"
OPS = ("eq", "ne", "lt", "le", "gt", "ge")
CASES = [
    (family, index, row)
    for family, rows in INPUTS.items()
    if isinstance(rows, list)
    for index, row in enumerate(rows)
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def signature(value):
    """Lossless structural observation, not mathematical evaluation/decoding."""
    kind = type(value)
    if value is None or kind in (bool, str):
        return {"type": kind.__name__, "value": value}
    if kind is int:
        return {"type": "int", "value": str(value)}
    if kind is bytes:
        return {"type": "bytes", "base64": base64.b64encode(value).decode("ascii")}
    if kind in (tuple, list):
        return {"type": kind.__name__, "items": [signature(v) for v in value]}
    if kind is dict:
        return {"type": "dict", "fields": {k: signature(v) for k, v in value.items()}}
    assert is_dataclass(value), kind
    return {
        "type": kind.__module__ + "." + kind.__name__,
        "fields": {f.name: signature(getattr(value, f.name)) for f in fields(value)},
    }


def thaw(value):
    if type(value) is ReadonlyObject:
        return {k: thaw(v) for k, v in value.entries}
    if type(value) is ReadonlySequence:
        items = [thaw(v) for v in value.items]
        return tuple(items) if value.native_kind == "tuple" else items
    return value


def mathematical_value(value):
    if type(value) is Number:
        assert type(value.numerator) is int and type(value.denominator) is int
        assert type(value.negative_zero) is bool
        return {
            "recordType": "Number",
            "numerator": str(value.numerator),
            "denominator": str(value.denominator),
            "negative_zero": value.negative_zero,
        }
    if type(value) is Calendar:
        assert type(value.day) is int
        assert type(value.explicit_offset) is type(value.is_datetime) is bool
        return {
            "recordType": "Calendar",
            "day": value.day,
            "second": mathematical_value(value.second),
            "explicit_offset": value.explicit_offset,
            "is_datetime": value.is_datetime,
        }
    assert type(value) in (str, bool)
    return {"recordType": type(value).__name__, "value": value}


def profile_value(value):
    return {
        "domain": value.domain,
        "language": value.language,
        "term": asdict(value.term),
        "value": mathematical_value(value.value),
    }


def source(pointer, *, definition=False):
    return SourceRecord(
        reference=(
            "packages/engine/tests/test_profile_M1_math_explanation.py#_operation/"
            if definition
            else "tests/fixtures/quality/profile-M1-math-inputs.json#"
        )
        + pointer,
        digest=TEST_SHA if definition else SOURCE_SHA,
        revision="sha256:" + (TEST_SHA if definition else SOURCE_SHA),
        text=None,  # No invented preimport token or byte span.
    )


def term(raw, pointer):
    return TermInput(
        raw["kind"],
        raw["lexical_form"],
        raw.get("datatype_iri"),
        raw.get("language_raw"),
        source(pointer),
    )


def iri(text):
    return TermInput("iri", text)


def ledger_observation(ledger):
    names = ("state", "caps", "usage", "used", "live", "peaks", "stage")
    return {name: signature(getattr(ledger, name)) for name in names if hasattr(ledger, name)}


def _operation(left, operator, right, label, directory):
    """Inputs only. No golden argument, file access, allocation or encoded payload injection."""
    records = (
        (iri("urn:m1:anchor"), iri(RDF + "type"), iri(OWL + "DatatypeProperty")),
        (iri("urn:m1:out"), iri(RDF + "type"), iri(OWL + "DatatypeProperty")),
        (iri("urn:m1:s"), iri("urn:m1:anchor"), TermInput("literal", "anchor")),
    )
    spec = RuleSpec(
        "m1",
        (Triple(Variable("?s"), iri("urn:m1:anchor"), Variable("?anchor")),),
        (Comparison(left, operator, right),),
        (Triple(Variable("?s"), iri("urn:m1:out"), TermInput("literal", "matched")),),
        source(label, definition=True),
        revision="sha256:" + TEST_SHA,
    )
    result = {"label": label, "sourceDefinition": signature(spec), "records": signature(records)}
    material_ledger, production_ledger, restore_ledger = (
        CaptureLedger(),
        CaptureLedger(),
        RestoreLedger(),
    )
    produced = restored = material = None
    stage = "material"
    try:
        material = prepare_profile_material(rules=(spec,), records=records, ledger=material_ledger)
        stage = "production"
        produced = execute_admitted_profile_job(
            material,
            error_catalog=CONTRACT.ERROR_CATALOG,
            error_schema=SCHEMA,
            ledger=production_ledger,
        )
        payload = produced.wire["payload"]
        context = RestoreExpectation(
            sha(produced.payload_json),
            sha(produced.rows_json),
            payload["inputDigest"],
            payload["inputDigestDomain"],
            payload["sourceDigest"],
            payload["definitionsDigest"],
            sha(produced.catalog_json),
            tuple(sorted(payload["implementation"].items())),
            produced.material.input_preimage,
            produced.material.source_preimage,
        )
        stage = "restore"
        restored = restore_profile_result(
            produced.payload_json,
            produced.rows_json,
            expected=context,
            allocation=produced.original_allocation,
            ledger=restore_ledger,
        )
    except Exception as error:  # Preserve every actual finite/unexpected component failure.
        diagnostic = getattr(error, "diagnostic", None)
        result.update(
            status="error",
            stage=stage,
            exceptionType=type(error).__name__,
            diagnostic=diagnostic,
            reason=(diagnostic or {}).get("reason", getattr(error, "reason", None)),
            publicError=getattr(error, "error", None),
        )
    else:
        child = produced.native_result["mechanismBatches"][0]
        batch = child["batch"]
        firing = batch.firings[0] if batch.firings else None
        comparison = firing.comparisons[0] if firing else None
        result.update(
            status="success",
            accepted=bool(batch.firings),
            comparison=(
                None
                if comparison is None
                else {
                    "left": profile_value(comparison.left),
                    "operator": comparison.operator,
                    "right": profile_value(comparison.right),
                    "result": comparison.result,
                }
            ),
            originalMatches=signature(child["originalMatches"]),
            originalMatchCount=len(child["originalMatches"]),
            nativeBatch=signature(batch),
            restoredBatch=signature(restored.batches.children[0].batch),
            originalAllocation=signature(produced.original_allocation),
            originalL={k: signature(child[k]) for k in ("limits", "budgetLimits", "budgetUsage")},
            originalLimitValues=asdict(child["limits"]),
            originalUsageValues=child["budgetUsage"],
            materialReceipt=signature(material.capture_receipt),
            productionReceipt=signature(produced.capture_receipt),
            rReceipt=signature(restored.batches),
            retention=signature(restored.retention),
            logicalRetention=dict(restored.retention),
            restoreLive=dict(restore_ledger.live),
            formalAuthority=restored.batches.formal_authority,
            outerFields=[k for k, _ in restored.projection.payload.entries],
            reasoningFields=[k for k, _ in restored.projection.payload["reasoning"].entries],
            childFields=[
                k
                for k, _ in restored.projection.payload["reasoning"]["mechanismBatches"]
                .items[0]
                .entries
            ],
            actualNative=signature({**payload, "reasoning": produced.native_result}),
            restoredFullview=signature(thaw(restored.projection.payload)),
            sourcePreimageEqual=produced.source_encoded == material.source_preimage,
            definitionsPreimageEqual=produced.definitions_encoded == material.definitions_preimage,
            retentionMeaning=(
                "Returned references remain held; "
                "R live=0 proves neither physical release nor H lease"
            ),
        )
    finally:
        result["ledgers"] = {
            "materialC": ledger_observation(material_ledger),
            "productionC": ledger_observation(production_ledger),
            "restoreR": ledger_observation(restore_ledger),
        }
        result["producedResultReturned"] = produced is not None
        result["restoredResultReturned"] = restored is not None
        if directory is not None and produced is not None:
            for name, raw in (
                ("payload", produced.payload_json),
                ("rows", produced.rows_json),
                ("input-preimage", produced.material.input_preimage),
                ("source-preimage", produced.source_encoded),
                ("definitions-preimage", produced.definitions_encoded),
            ):
                (directory / f"{label}.{name}.raw").write_bytes(raw)
    return result


def _observe(family, index, row, directory):
    pointer = f"/{family}/{index}"
    if "input" in row:
        left = right = term(row["input"], pointer + "/input")
        return {"main": _operation(left, "eq", right, "main", directory)}
    left, right = term(row["left"], pointer + "/left"), term(row["right"], pointer + "/right")
    return {
        "main": _operation(left, row["operator"], right, "main", directory),
        "leftOperandSeparateEqSelf": _operation(left, "eq", left, "left", directory),
        "rightOperandSeparateEqSelf": _operation(right, "eq", right, "right", directory),
    }


@pytest.fixture(scope="session")
def assertion_goldens():
    """Loaded by assertions only, never passed to any input/production helper."""
    return {
        "domain": json.loads((GOLDENS / "domain-operator-goldens.json").read_bytes()),
        "number": json.loads((GOLDENS / "number-goldens.json").read_bytes()),
        "calendar": json.loads((GOLDENS / "calendar-goldens.json").read_bytes()),
        "term": json.loads((GOLDENS / "term-error-goldens.json").read_bytes()),
    }


def _expected(family, row, goldens):
    """Select independent authored fields only; no numeric or calendar calculation."""

    def find(rows, identity):
        return next(c for c in rows if c["id"] == identity)

    if family == "domainComparisonCases":
        c = find(goldens["domain"]["nineDomainCells"], row["id"])
        expected = dict(c["expected"])
        for side in ("left", "right"):
            domain = c[side + "Domain"]
            expected[side + "Domain"] = domain
            if domain == "N":
                expected[side + "Number"] = find(goldens["number"]["vectors"], "two-integer")[
                    "expected"
                ]["Number"]
            if domain in ("Dz", "Dl", "Tz", "Tl"):
                expected[side + "Calendar"] = find(goldens["calendar"]["vectors"], domain)[
                    "expectedCalendar"
                ]
        return expected
    if family == "numericComparisonCases":
        c = find(goldens["domain"]["numericPairRelationCells"], row["id"])
        return {
            "boolean": c["expectedBoolean"],
            "leftNumber": c["leftNumber"],
            "rightNumber": c["rightNumber"],
        }
    if family == "numberDecodeCases":
        return find(goldens["number"]["vectors"], row["id"])["expected"]
    if family == "calendarDecodeCases":
        c = find(goldens["calendar"]["vectors"], row["id"])
        return {"Calendar": c["expectedCalendar"], "domain": c["expectedDomain"]}
    if family == "mixedNumericComparisonCases":
        relation = next(
            c
            for c in goldens["number"]["mixedRelations"]
            if (c["leftId"], c["rightId"]) == (row["leftNumberCaseId"], row["rightNumberCaseId"])
        )
        return {
            "boolean": relation["sixBooleans"][OPS.index(row["operator"])],
            "leftNumber": find(goldens["number"]["vectors"], row["leftNumberCaseId"])["expected"][
                "Number"
            ],
            "rightNumber": find(goldens["number"]["vectors"], row["rightNumberCaseId"])["expected"][
                "Number"
            ],
        }
    if family == "signedZeroComparisonCases":
        dtype = row["id"].split("/")[0]
        return {
            "boolean": goldens["number"]["zeroComparison"]["allSignedZeros"][
                OPS.index(row["operator"])
            ],
            "leftNumber": find(goldens["number"]["vectors"], "negative-zero-" + dtype)["expected"][
                "Number"
            ],
            "rightNumber": {"numerator": "0", "denominator": "1", "negative_zero": False},
        }
    if family == "termComparisonCases":
        c = find(goldens["term"]["semantics"], row["termCaseId"])
        op = row["operator"]
        if "allReasons" in c:
            return {"reason": c["allReasons"]}
        if "sixBooleans" in c:
            return {"boolean": c["sixBooleans"][OPS.index(op)]}
        return {"boolean": c[op]} if op in ("eq", "ne") else {"reason": c["orderedReasons"]}
    if family == "errorOperandCases":
        return {"reason": find(goldens["term"]["lexicalAndSupportErrors"], row["id"])["reason"]}
    assert family == "languageAbnfInputs"
    assert row["input"]["language_raw"] in goldens["term"]["languageBoundary"]["acceptedAbnfOnly"]
    return {"boolean": True}


def _check_component(op):
    assert op["status"] == "success", op
    assert op["originalMatchCount"] == 1
    assert len(op["outerFields"]) == 7 and len(op["reasoningFields"]) == 15
    assert len(op["childFields"]) == 11
    assert op["actualNative"] == op["restoredFullview"]
    assert op["nativeBatch"] == op["restoredBatch"]
    assert op["formalAuthority"] is False
    assert op["sourcePreimageEqual"] and op["definitionsPreimageEqual"]
    for name, used in op["originalUsageValues"].items():
        assert 0 <= used <= op["originalLimitValues"][name]
    assert op["ledgers"]["restoreR"]["state"]["value"] == "success"
    assert not any(op["restoreLive"].values())
    assert op["logicalRetention"]["scalar"] > 0


def _check_raw(pv, raw, pointer):
    t = pv["term"]
    assert {k: t[k] for k in ("kind", "lexical_form", "datatype_iri", "language_raw")} == {
        "kind": raw["kind"],
        "lexical_form": raw["lexical_form"],
        "datatype_iri": raw.get("datatype_iri"),
        "language_raw": raw.get("language_raw"),
    }
    assert t["source"] == asdict(source(pointer))
    if pv["domain"] in ("I", "S", "L"):
        assert pv["value"] == {"recordType": "str", "value": raw["lexical_form"]}
    if pv["domain"] == "L":
        assert pv["language"] == raw["language_raw"].lower()
    if pv["domain"] == "B":
        assert pv["value"] == {
            "recordType": "bool",
            "value": {"true": True, "1": True, "false": False, "0": False}[raw["lexical_form"]],
        }


def _check_number(pv, value):
    assert pv["domain"] == "N"
    assert pv["value"] == {"recordType": "Number", **value}


def _assert_case(family, index, row, actual, expected):
    main = actual["main"]
    if "reason" in expected:
        assert main["status"] == "error", main
        assert not main["producedResultReturned"] and not main["restoredResultReturned"]
        assert main["reason"] == expected["reason"], main
        if "input" in row:
            return  # Invalid operand has only its actual error, never an invented typed value.
    else:
        _check_component(main)
        assert main["accepted"] is expected.get("boolean", True)
        if main["comparison"] is not None:
            assert main["comparison"]["result"] is main["accepted"]
    operands = (
        [("main", "input")]
        if "input" in row
        else [("leftOperandSeparateEqSelf", "left"), ("rightOperandSeparateEqSelf", "right")]
    )
    for operation_name, input_name in operands:
        op = actual[operation_name]
        _check_component(op)
        assert op["accepted"] is True
        pv = op["comparison"]["left"]
        _check_raw(pv, row[input_name], f"/{family}/{index}/{input_name}")
        if input_name + "Domain" in expected:
            assert pv["domain"] == expected[input_name + "Domain"]
        if "Number" in expected:
            _check_number(pv, expected["Number"])
        if input_name + "Number" in expected:
            _check_number(pv, expected[input_name + "Number"])
        calendar = expected.get("Calendar", expected.get(input_name + "Calendar"))
        if calendar is not None:
            value = dict(calendar)
            value["second"] = {"recordType": "Number", **value["second"]}
            assert pv["domain"] == expected.get("domain", expected.get(input_name + "Domain"))
            assert pv["value"] == {"recordType": "Calendar", **value}


@pytest.mark.parametrize("family,index,row", CASES, ids=[f"{f}-{r['id']}" for f, _, r in CASES])
def test_math_observation(family, index, row, assertion_goldens):
    """Complete per-ID actuals are saved before any expected-field assertion."""
    directory = None
    if os.environ.get("M1_OBSERVATION_DIR"):
        key = sha((family + "/" + row["id"]).encode())
        directory = Path(os.environ["M1_OBSERVATION_DIR"]) / key
        directory.mkdir(parents=True, exist_ok=False)
    observation = {
        "family": family,
        "id": row["id"],
        "fixtureIndex": index,
        "sourceSha256": SOURCE_SHA,
        "input": row,
    }
    try:
        observation["actual"] = _observe(family, index, row, directory)
        observation["expected"] = _expected(family, row, assertion_goldens)
        _assert_case(family, index, row, observation["actual"], observation["expected"])
        observation["assertion"] = "pass"
    finally:
        if directory is not None:
            observation.setdefault("assertion", "failure; actual preserved, no golden mutation")
            (directory / "observation.json").write_text(
                json.dumps(observation, ensure_ascii=False, indent=2) + "\n"
            )


def test_independent_input_corpus_keeps_all_original_ids():
    assert len(CASES) == 1331
    assert SOURCE_BYTES == (GOLDENS / "math-operand-inputs.json").read_bytes()
    for family, rows in INPUTS.items():
        if isinstance(rows, list):
            assert len({r["id"] for r in rows}) == len(rows), family
            for row in rows:
                assert not {"expected", "Number", "Calendar", "boolean", "reason"} & row.keys()
