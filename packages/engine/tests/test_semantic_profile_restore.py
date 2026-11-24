"""Actual production -> saved bytes -> fresh exec -> canonical batch checking.

The capture transport is a test-only trusted precondition, never a producer
authorization. Rebound-wire adversarial cases deliberately break that premise
to reach the strict decoder; they do not prove the origin of the modified data.
"""

import copy
import hashlib
import importlib.util
import json
import os
import pickle
import subprocess
import sys
import time
from dataclasses import dataclass, fields, is_dataclass, replace
from pathlib import Path
from unittest.mock import patch

import pytest
from ontolearn_engine import semantic, semantic_execution
from ontolearn_engine import semantic_profile_restore as restore
from ontolearn_engine.quality import rule_terms
from ontolearn_engine.quality.rule_firing import Comparison, RuleSpec, Triple, Variable
from ontolearn_engine.quality.rule_profile import (
    XSD,
    Budget,
    ProfileFailure,
    ProfileLimits,
    SourceRecord,
    TermInput,
)
from ontolearn_engine.resources import CONTRACT, ROOT, semantic_identity
from ontolearn_engine.semantic_profile_input import prepare_profile_material
from ontolearn_engine.semantic_profile_production import execute_admitted_profile_job
from ontolearn_engine.semantic_profile_restore import (
    ChildAllocation,
    OriginalAllocation,
    RestoreExpectation,
    restore_profile_batches,
)
from ontolearn_engine.semantic_profile_restore_budget import RestoreFailure, RestoreLedger

OWL = "http://www.w3.org/2002/07/owl#"
SCHEMA = json.loads((ROOT / "v2/schema.json").read_bytes())
COPY_FIELDS = (
    "ruleId",
    "definitionOrdinal",
    "disabled",
    "definitions",
    "catalog",
    "originalMatches",
    "batch",
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return semantic_execution._profile_json_bytes(value)


def project(value):
    return semantic_execution._ProfileProjection().value(value)


def iri(value):
    return TermInput("iri", value)


def literal(value, type_name="integer", source=None):
    return TermInput("literal", value, XSD + type_name, source=source)


def rule(identity="r", *, comparisons=None, source=None, predicate="urn:value"):
    when = Triple(Variable("?s"), iri(predicate), Variable("?v"))
    return RuleSpec(
        identity,
        (when,),
        (Comparison(Variable("?v"), "gt", literal("1")),) if comparisons is None else comparisons,
        (Triple(Variable("?s"), iri("urn:out"), TermInput("literal", "ok")),),
        source,
        revision="revision:1",
        definition_digest="definition:fixture",
    )


def turtle(values=("1", "2"), *, datatype="integer", padding=""):
    declarations = (
        f"<urn:value> a <{OWL}DatatypeProperty> .\n<urn:out> a <{OWL}DatatypeProperty> .\n"
    )
    facts = "".join(
        f'<urn:s{index}> <urn:value> "{value}"^^<{XSD}{datatype}> .\n'
        for index, value in enumerate(values, 1)
    )
    return declarations + facts + padding


def signature(value):
    """Native exact-type signature; not another engine or typed decoder."""
    kind = type(value)
    if value is None:
        return ["none"]
    if kind is bool:
        return ["bool", value]
    if kind is int:
        return ["int", hex(value)]
    if kind is str:
        return ["str", value]
    if kind is bytes:
        return ["bytes", value.hex()]
    if kind in (tuple, list):
        return [kind.__name__, [signature(item) for item in value]]
    if kind is dict:
        return ["dict", [[name, signature(item)] for name, item in sorted(value.items())]]
    assert is_dataclass(value), kind
    return [
        "record",
        kind.__module__ + "." + kind.__name__,
        [[field.name, signature(getattr(value, field.name))] for field in fields(value)],
    ]


def original_child_signature(child):
    return signature({key: child[key] for key in COPY_FIELDS})


def restored_child_signature(child):
    return signature(
        {
            "ruleId": child.rule_id,
            "definitionOrdinal": child.definition_ordinal,
            "disabled": child.disabled,
            "definitions": child.definitions,
            "catalog": child.catalog,
            "originalMatches": child.original_matches,
            "batch": child.batch,
        }
    )


@dataclass(frozen=True)
class Capture:
    payload: dict
    payload_json: bytes
    rows_json: bytes
    expected: RestoreExpectation
    allocation: OriginalAllocation
    native: dict
    reason_calls: int


def capture_case(*, text=None, rules=None, records=None, disabled=(), label="fixture"):
    """Independently fix witnesses before exactly one real production call."""
    if rules is None:
        rules = (rule(),)
    if records is None:
        text = turtle() if text is None else text
        input_preimage = text.encode("utf-8")
        source = SourceRecord(
            "fixture:" + label,
            sha(input_preimage),
            "source-revision:1",
            text if len(input_preimage) <= 65536 else None,
        )
    else:
        input_preimage = canonical(project(records))
        source = tuple(term.source for triple in records for term in triple)
    source_preimage = canonical(project(source))
    definitions_digest = sha(canonical(project(rules)))
    implementation = tuple(sorted(semantic_identity(profile=True).items()))
    actual_calls = []
    original_reason = semantic._profile_reason

    def observe(*args, **kwargs):
        actual_calls.append(1)
        return original_reason(*args, **kwargs)

    with patch.object(semantic, "_profile_reason", observe):
        if records is None:
            material = prepare_profile_material(
                text,
                rules,
                disabled_rule_ids=disabled,
                source_reference=source.reference,
                source_revision=source.revision,
            )
        else:
            material = prepare_profile_material(
                rules=rules,
                records=records,
                disabled_rule_ids=disabled,
            )
        computation = execute_admitted_profile_job(
            material, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=SCHEMA
        )
    assert actual_calls == [1]
    # The observer counts the actual core; it never supplies capture or L.
    native, result = computation.native_result, computation.wire
    assert material.input_preimage == input_preimage
    assert material.source_preimage == source_preimage
    assert computation.source_encoded == source_preimage
    assert computation.definitions_encoded == canonical(project(rules))
    payload_json, rows_json = canonical(result["payload"]), canonical(result["rows"])
    assert result["jsonPayloadDigest"] == sha(payload_json)
    assert result["rowsDigest"] == sha(rows_json)
    assert result["payload"]["inputDigest"] == sha(input_preimage)
    assert result["payload"]["sourceDigest"] == sha(source_preimage)
    assert result["payload"]["definitionsDigest"] == definitions_digest
    expected = RestoreExpectation(
        payload_digest=sha(payload_json),
        rows_digest=sha(rows_json),
        input_digest=sha(input_preimage),
        input_domain=result["payload"]["inputDigestDomain"],
        source_digest=sha(source_preimage),
        definitions_digest=definitions_digest,
        catalog_digest=sha(canonical(project(native["catalog"]))),
        implementation=implementation,
        input_preimage=input_preimage,
        source_preimage=source_preimage,
    )
    allocation = computation.original_allocation
    assert allocation.rule_ids == tuple(spec.rule_id for spec in rules)
    assert allocation.disabled_rule_ids == tuple(disabled)
    assert tuple(
        (child.rule_id, child.definition_ordinal, child.limits) for child in allocation.children
    ) == tuple(
        (item["ruleId"], item["definitionOrdinal"], item["limits"])
        for item in native["mechanismBatches"]
    )
    return Capture(result["payload"], payload_json, rows_json, expected, allocation, native, 1)


@pytest.fixture(scope="module")
def captured():
    return capture_case()


def restore_capture(
    capture, *, expected=None, allocation=None, ledger=None, wire=None, fullview=False
):
    ledger = RestoreLedger() if ledger is None else ledger
    payload, rows = (capture.payload_json, capture.rows_json) if wire is None else wire
    api = restore.restore_profile_result if fullview else restore_profile_batches
    result = api(
        payload,
        rows,
        expected=capture.expected if expected is None else expected,
        allocation=capture.allocation if allocation is None else allocation,
        ledger=ledger,
    )
    return result, ledger


def rebound_wire(capture, payload):
    """Enemy unit precondition: wire hash rebound, original witnesses untouched."""
    raw = canonical(payload)
    text = raw.decode("utf-8")
    rows = canonical([[text[index : index + 8192]] for index in range(0, len(text), 8192)])
    return (raw, rows), replace(capture.expected, payload_digest=sha(raw), rows_digest=sha(rows))


def assert_rejected(capture, *, payload=None, wire=None, expected=None, allocation=None):
    if payload is not None:
        wire, expected = rebound_wire(capture, payload)
    ledger = RestoreLedger()
    with pytest.raises(RestoreFailure) as caught:
        restore_capture(capture, expected=expected, allocation=allocation, ledger=ledger, wire=wire)
    assert ledger.state == "failed"
    assert not any(value for _, value in ledger.live)
    assert type(caught.value.reason) is str
    return caught.value, ledger


def pack_capture(capture):
    e = capture.expected
    return {
        "payload": capture.payload_json.hex(),
        "rows": capture.rows_json.hex(),
        "expected": {
            field.name: (
                getattr(e, field.name).hex()
                if type(getattr(e, field.name)) is bytes
                else getattr(e, field.name)
            )
            for field in fields(e)
        },
        "allocation": {
            "rule_ids": capture.allocation.rule_ids,
            "disabled_rule_ids": capture.allocation.disabled_rule_ids,
            "budget_version": capture.allocation.budget_version,
            "children": [
                {
                    "rule_id": item.rule_id,
                    "definition_ordinal": item.definition_ordinal,
                    "limits": {
                        field.name: getattr(item.limits, field.name)
                        for field in fields(item.limits)
                    },
                }
                for item in capture.allocation.children
            ],
        },
    }


def unpack_capture(envelope):
    values = envelope["expected"]
    values["implementation"] = tuple(tuple(item) for item in values["implementation"])
    values["input_preimage"] = bytes.fromhex(values["input_preimage"])
    values["source_preimage"] = bytes.fromhex(values["source_preimage"])
    expected = RestoreExpectation(**values)
    original = envelope["allocation"]
    allocation = OriginalAllocation(
        tuple(original["rule_ids"]),
        tuple(original["disabled_rule_ids"]),
        tuple(
            ChildAllocation(
                child["rule_id"], child["definition_ordinal"], ProfileLimits(**child["limits"])
            )
            for child in original["children"]
        ),
        original["budget_version"],
    )
    return bytes.fromhex(envelope["payload"]), bytes.fromhex(envelope["rows"]), expected, allocation


def _child_main():
    # Trusted harness transport permits normal numbers; saved payload/rows do not.
    envelope = json.loads(sys.stdin.buffer.read())
    assert not rule_terms._ISSUED_VALUES
    initial_issued = len(rule_terms._ISSUED_VALUES)
    payload, rows, expected, allocation = unpack_capture(envelope)
    calls = []
    original_check = restore.check_firing_batch

    def observe_check(definitions, catalog, originals, saved, *, limits, disabled):
        calls.append(
            {
                "limits": signature(limits),
                "definitions": signature(definitions),
                "catalog": signature(catalog),
                "original_matches": signature(originals),
                "disabled": disabled,
                "saved_none": saved is None,
            }
        )
        return original_check(
            definitions, catalog, originals, saved, limits=limits, disabled=disabled
        )

    def forbidden(*_args, **_kwargs):
        raise AssertionError("restore must not reason or match")

    ledger = RestoreLedger()
    with (
        patch.object(semantic, "reason", forbidden),
        patch.object(semantic, "_finite_matches", forbidden),
        patch.object(restore, "check_firing_batch", observe_check),
    ):
        api = (
            restore.restore_profile_result if envelope.get("fullview") else restore_profile_batches
        )
        result = api(payload, rows, expected=expected, allocation=allocation, ledger=ledger)
    restored = result.batches if envelope.get("fullview") else result
    for child in restored.children:
        if child.batch is not None:
            for firing in child.batch.firings:
                for comparison in firing.comparisons:
                    rule_terms.check_value(comparison.left, Budget())
                    rule_terms.check_value(comparison.right, Budget())
    response = {
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "argv": sys.argv,
        "initial_issued": initial_issued,
        "children": [restored_child_signature(child) for child in restored.children],
        "facts": [child.fact for child in restored.children],
        "calls": calls,
        "usage": restored.usage,
        "peaks": restored.peaks,
        "parse_usage": restored.parse_usage,
        "ledger_state": ledger.state,
        "live": ledger.live,
        "formal_authority": restored.formal_authority,
        "aggregate_recomputed": restored.aggregate_recomputed,
    }
    if envelope.get("fullview"):
        response["projection"] = signature(thaw_view(result.projection.payload))
        response["rows_hex"] = result.rows_json.hex()
        response["retention"] = result.retention
    sys.stdout.buffer.write(canonical(response))


def exec_restore(capture, label, *, fullview=False):
    argv = [sys.executable, str(Path(__file__).resolve()), "--restore-child"]
    envelope = pack_capture(capture)
    if fullview:
        envelope["fullview"] = True
    raw = canonical(envelope)
    started = time.monotonic()
    process = subprocess.Popen(
        argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(raw, timeout=60)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        stdout, stderr = process.communicate()
    record = {
        "label": label,
        "pid": process.pid,
        "parent_pid": os.getpid(),
        "argv": argv,
        "timeout_seconds": 60,
        "timed_out": timed_out,
        "exit": process.returncode,
        "elapsed_seconds_observed": time.monotonic() - started,
        "stdin_bytes": len(raw),
        "stdin_sha256": sha(raw),
        "stdout_bytes": len(stdout),
        "stdout_sha256": sha(stdout),
        "stderr_bytes": len(stderr),
        "stderr_sha256": sha(stderr),
        "cpu_or_rss_capacity_claim": False,
    }
    evidence = os.environ.get("I05_RESTORE_EVIDENCE_DIR")
    if evidence:
        directory = Path(evidence) / label
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "stdin.json").write_bytes(raw)
        (directory / "stdout.json").write_bytes(stdout)
        (directory / "stderr.txt").write_bytes(stderr)
        (directory / "supervisor.json").write_bytes(canonical(record))
    assert not timed_out, record
    assert process.returncode == 0, stderr.decode("utf-8", errors="replace")
    assert not stderr
    response = json.loads(stdout)
    assert response["pid"] != os.getpid()
    if sys.platform == "win32":
        assert process.pid in (response["pid"], response["ppid"])
    else:
        assert response["pid"] == process.pid
    assert response["initial_issued"] == 0
    assert response["children"] == [
        original_child_signature(child) for child in capture.native["mechanismBatches"]
    ]
    assert response["ledger_state"] == "success"
    assert not any(value for _, value in response["live"])
    assert response["formal_authority"] is False
    assert response["aggregate_recomputed"] is False
    assert len(response["calls"]) == len(capture.allocation.children)
    assert len(response["parse_usage"]) == len(capture.allocation.children)
    for used, allocation in zip(response["parse_usage"], capture.allocation.children, strict=True):
        used = dict(used)
        assert used["work"] <= allocation.limits.work
        assert used["input_bytes"] <= allocation.limits.input_bytes
        assert used["output_bytes"] == 0
    for call, child in zip(response["calls"], capture.native["mechanismBatches"], strict=True):
        assert call["limits"] == signature(child["limits"])
        assert call["definitions"] == signature(child["definitions"])
        assert call["catalog"] == signature(child["catalog"])
        assert call["original_matches"] == signature(
            () if child["disabled"] else child["originalMatches"]
        )
        assert call["disabled"] is child["disabled"]
        assert call["saved_none"] is (child["batch"] is None)
    if fullview:
        original = {**capture.payload, "reasoning": capture.native}
        assert response["projection"] == signature(original)
        assert response["rows_hex"] == capture.rows_json.hex()
        assert dict(response["retention"])["objects"] > 0
    return response


def test_real_saved_json_exec_restores_full_original_ordered_false_and_true(captured):
    native = captured.native["mechanismBatches"][0]
    assert [dict(item.bindings)["?v"].lexical_form for item in native["originalMatches"]] == [
        "1",
        "2",
    ]
    assert len(native["batch"].firings) == 1
    assert dict(native["batch"].firings[0].bindings)["?v"].lexical_form == "2"
    response = exec_restore(captured, "complete-false-true")
    assert response["facts"] == ["batch-consistent"]


@pytest.mark.parametrize("field", ["reference", "digest", "revision", "text"])
def test_source40000_first_succeeds_in_actual_i05_then_saved_exec(field):
    values = {
        "reference": "fixture:large-rule",
        "digest": "metadata-digest",
        "revision": "r1",
        "text": None,
    }
    values[field] = "a" * 40000
    source = SourceRecord(**values)
    capture = capture_case(rules=(rule(comparisons=(), source=source),), label="source40000")
    assert capture.reason_calls == 1
    assert len(capture.native["mechanismBatches"][0]["batch"].firings) == 2
    assert getattr(capture.native["definitions"][0].source, field) == "a" * 40000
    exec_restore(capture, "source40000-" + field)


def repeated_source_capture(*, different_values=False):
    source = SourceRecord("", "", "rev:raw", "same source" * 8)
    property_type = iri(OWL + "DatatypeProperty")
    rdf_type = iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    shared = literal("2", source=source)
    records = (
        (iri("urn:value"), rdf_type, property_type),
        (iri("urn:out"), rdf_type, property_type),
        (iri("urn:s1"), iri("urn:value"), shared),
        (
            iri("urn:s2"),
            iri("urn:value"),
            literal("3", source=source) if different_values else shared,
        ),
    )
    spec = rule(comparisons=(Comparison(Variable("?v"), "eq", Variable("?v")),))
    return capture_case(records=records, rules=(spec,), label="repeated-source")


def test_structured_source_occurrences_and_cache_hits_preserve_all_fields():
    capture = repeated_source_capture()
    assert len(capture.native["termSources"]) == 12
    source_terms = [item["value"] for item in capture.native["termSources"] if item["value"].source]
    assert len(source_terms) == 2
    assert source_terms[0].source == source_terms[1].source
    response = exec_restore(capture, "repeated-source")
    assert dict(response["usage"])["cache_query"] > 0
    assert dict(response["usage"])["pv_compare"] > 0


def domain_capture(domain):
    source = SourceRecord("fixture:raw-source", "", None, "raw source text")
    terms = {
        "I": TermInput("iri", "urn:object", source=source),
        "S": TermInput("literal", "word", source=source),
        "L": TermInput("literal", "word", language_raw="EN-us", source=source),
        "B": literal("true", "boolean", source),
        "N": literal("-0.0", "double", source),
        "Dl": literal("1970-01-01", "date", source),
        "Dz": literal("1970-01-01Z", "date", source),
        "Tl": literal("1970-01-01T00:00:00", "dateTime", source),
        "Tz": literal("1970-01-01T00:00:00Z", "dateTime", source),
    }
    kind = "ObjectProperty" if domain == "I" else "DatatypeProperty"
    rdf_type = iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    records = (
        (iri("urn:value"), rdf_type, iri(OWL + kind)),
        (iri("urn:out"), rdf_type, iri(OWL + "DatatypeProperty")),
        (iri("urn:s"), iri("urn:value"), terms[domain]),
    )
    spec = rule(comparisons=(Comparison(Variable("?v"), "eq", Variable("?v")),))
    return capture_case(records=records, rules=(spec,), label="domain-" + domain)


@pytest.mark.parametrize("domain", ["I", "S", "L", "B", "N", "Dl", "Dz", "Tl", "Tz"])
def test_every_original_profile_value_domain_survives_exec_and_refuses_repair(domain):
    capture = domain_capture(domain)
    operand = capture.native["mechanismBatches"][0]["batch"].firings[0].comparisons[0].left
    assert operand.domain == domain
    assert operand.term.source.digest == ""
    if domain == "L":
        assert operand.term.language_raw == "EN-us" and operand.language == "en-us"
    if domain == "N":
        assert operand.value.negative_zero is True
    exec_restore(capture, "domain-" + domain)
    payload = copy.deepcopy(capture.payload)
    comparison = pv_pair(payload)
    value = comparison["left"]["value"]
    if type(value) is str:
        comparison["left"]["value"] = value + "!"
    elif type(value) is bool:
        comparison["left"]["value"] = not value
    elif domain == "N":
        value["negative_zero"] = False
    else:
        value["explicit_offset"] = not value["explicit_offset"]
    payload["reasoning"]["firingGroups"][0]["comparisons"][0]["left"] = copy.deepcopy(
        comparison["left"]
    )
    assert_rejected(capture, payload=payload)


@pytest.mark.parametrize("mode", ["disabled", "no-matches", "no-definitions"])
def test_disabled_and_two_real_empty_states(mode):
    rules, disabled, text = (rule(),), (), turtle()
    if mode == "disabled":
        disabled = ("r",)
    elif mode == "no-matches":
        text = turtle(values=())
    else:
        rules = ()
    capture = capture_case(text=text, rules=rules, disabled=disabled, label=mode)
    child = capture.native["mechanismBatches"][0]
    if mode == "disabled":
        assert child["batch"] is None and child["originalMatches"] is None
    else:
        assert child["batch"] is not None and child["batch"].firings == ()
        assert child["originalMatches"] == ()
    response = exec_restore(capture, mode)
    assert response["facts"] == ["definition-only" if mode == "disabled" else "batch-consistent"]


@pytest.mark.parametrize("large", [False, True])
def test_turtle_raw_and_empty_graph_source_witnesses_are_required(large):
    text = turtle(values=()) + "# " + "x" * 70000 if large else ""
    capture = capture_case(text=text, rules=(), label="large-text" if large else "empty-text")
    if large:
        assert len(capture.expected.input_preimage) > 65536
    else:
        assert capture.expected.input_preimage == b""
        assert capture.native["termSources"] == ()
    exec_restore(capture, "large-turtle" if large else "empty-source-witness")
    assert_rejected(capture, expected=replace(capture.expected, input_preimage=None))
    assert_rejected(capture, expected=replace(capture.expected, source_preimage=b""))


def test_false_comparison_does_not_hide_later_bad_type_in_original_production():
    false = Comparison(literal("1"), "eq", literal("2"))
    bad = Comparison(Variable("?v"), "eq", literal("true", "boolean"))
    with pytest.raises(semantic_execution.ProfileExecutionFault) as caught:
        capture_case(rules=(rule(comparisons=(false, bad)),))
    assert caught.value.diagnostic["reason"] == "RULE_COMPARISON_TYPE_MISMATCH"


def iter_leaf_paths(value, path=()):
    if type(value) is dict and value:
        for key, item in value.items():
            yield from iter_leaf_paths(item, (*path, key))
    elif type(value) is list and value:
        for index, item in enumerate(value):
            yield from iter_leaf_paths(item, (*path, index))
    else:
        yield path


def at(value, path):
    for key in path:
        value = value[key]
    return value


def changed_leaf(value):
    if value is None:
        return ""
    if type(value) is bool:
        return not value
    if type(value) is str:
        return value + "#changed"
    if type(value) is list:
        return [None]
    raise AssertionError(type(value))


def test_every_saved_leaf_is_bound_to_independent_original_capture(captured):
    # Integrity coverage only; strict-decoder branch coverage is below.
    paths = list(iter_leaf_paths(captured.payload))
    assert len(paths) > 100
    for path in paths:
        payload = copy.deepcopy(captured.payload)
        parent, final = at(payload, path[:-1]), path[-1]
        parent[final] = changed_leaf(parent[final])
        wire, _enemy_expectation = rebound_wire(captured, payload)
        assert_rejected(captured, wire=wire)


def pv_pair(payload):
    return payload["reasoning"]["mechanismBatches"][0]["batch"]["firings"][0]["comparisons"][0]


@pytest.mark.parametrize(
    "path,value",
    [
        (("left", "domain"), "S"),
        (("left", "language"), "EN"),
        (("left", "term", "lexical_form"), "3"),
        (("left", "term", "datatype_iri"), XSD + "string"),
        (("left", "term", "language_raw"), "en"),
        (("left", "value", "numerator", "integerHex"), "0x3"),
        (("left", "value", "denominator", "integerHex"), "0x2"),
        (("left", "value", "negative_zero"), True),
        (("result",), False),
        (("operator",), "ne"),
        (("index", "integerHex"), "0x1"),
    ],
)
def test_rebound_wire_cannot_repair_a_saved_comparison_last_field(captured, path, value):
    payload = copy.deepcopy(captured.payload)
    parent = at(pv_pair(payload), path[:-1])
    parent[path[-1]] = value
    top = payload["reasoning"]["firingGroups"][0]["comparisons"][0]
    at(top, path[:-1])[path[-1]] = value
    assert_rejected(captured, payload=payload)


@pytest.mark.parametrize(
    "field",
    [
        "day",
        "second-numerator",
        "second-denominator",
        "second-negative-zero",
        "explicit_offset",
        "is_datetime",
    ],
)
def test_calendar_saved_native_components_are_all_compared(field):
    spec = rule(comparisons=(Comparison(Variable("?v"), "eq", Variable("?v")),))
    capture = capture_case(
        text=turtle(("1970-01-01T00:00:00Z",), datatype="dateTime"), rules=(spec,)
    )
    payload = copy.deepcopy(capture.payload)
    value = pv_pair(payload)["left"]["value"]
    if field == "day":
        value["day"]["integerHex"] = "0x1"
    elif field.startswith("second-"):
        part = field.removeprefix("second-").replace("-", "_")
        if part == "negative_zero":
            value["second"][part] = True
        else:
            value["second"][part]["integerHex"] = "0x2"
    else:
        value[field] = not value[field]
    payload["reasoning"]["firingGroups"][0]["comparisons"][0]["left"]["value"] = copy.deepcopy(
        value
    )
    assert_rejected(capture, payload=payload)


@pytest.mark.parametrize("target", ["top-only", "batch-only", "head", "basis", "false-tail"])
def test_duplicate_projection_and_complete_false_tail_are_not_ignored(captured, target):
    payload = copy.deepcopy(captured.payload)
    reasoning = payload["reasoning"]
    if target == "top-only":
        reasoning["firingGroups"][0]["comparisons"][0]["left"]["value"]["negative_zero"] = True
    elif target == "batch-only":
        pv_pair(payload)["right"]["value"]["negative_zero"] = True
    elif target == "head":
        reasoning["mechanismBatches"][0]["batch"]["firings"][0]["heads"][0]["index"][
            "integerHex"
        ] = "0x1"
    elif target == "basis":
        reasoning["mechanismBatches"][0]["batch"]["firings"][0]["basis"].append("bad-proof")
    else:
        matches = reasoning["mechanismBatches"][0]["originalMatches"]
        matches.reverse()
        # The original payload binding proves producer order. Rebinding that
        # trusted hash would discard this premise: with only one true firing,
        # 16c can accept a mechanism-equivalent false/true input permutation.
        wire, _enemy_expected = rebound_wire(captured, payload)
        assert_rejected(captured, wire=wire)
        return
    assert_rejected(captured, payload=payload)


@pytest.mark.parametrize(
    "kind",
    [
        "format",
        "semantics",
        "profile",
        "implementation",
        "domain",
        "schema-version",
        "budget-version",
        "cache-version",
    ],
)
def test_version_and_digest_domains_are_not_implicitly_upgraded(captured, kind):
    payload = copy.deepcopy(captured.payload)
    if kind.endswith("-version"):
        field = kind.replace("-", "_")
        assert_rejected(captured, expected=replace(captured.expected, **{field: "legacy"}))
        return
    if kind == "format":
        payload["format"] = "i05-reasoning-result/1"
    elif kind == "semantics":
        payload["reasoning"]["semanticsVersion"] = "i05-finite-6"
    elif kind == "profile":
        payload["reasoning"]["profile"] = "wrong-profile"
    elif kind == "implementation":
        payload["implementation"]["dependencyLockHash"] = "0" * 64
    else:
        payload["inputDigestDomain"] = "unknown-domain"
    assert_rejected(captured, payload=payload)


@pytest.mark.parametrize(
    "malformation",
    [
        "unknown-key",
        "extra-key",
        "missing-key",
        "wrong-tag",
        "wrong-position",
        "int-leading-zero",
        "int-negative-zero",
        "int-uppercase",
        "int-bool",
        "int-too-long",
        "bytes-odd",
        "bytes-uppercase",
        "number",
        "nan",
        "duplicate",
        "surrogate",
        "utf8",
    ],
)
def test_strict_wire_front_door_before_native_construction(captured, malformation):
    payload = copy.deepcopy(captured.payload)
    child = payload["reasoning"]["mechanismBatches"][0]
    if malformation == "unknown-key":
        payload["unknown-input-key"] = None
    elif malformation == "extra-key":
        child["limits"]["text"] = None
    elif malformation == "missing-key":
        del child["limits"]["work"]
    elif malformation == "wrong-tag":
        child["limits"]["recordType"] = "FakeLimits"
    elif malformation == "wrong-position":
        child["limits"] = {
            "recordType": "InputLocation",
            "section": None,
            "index": None,
            "side": None,
            "span": None,
        }
    elif malformation.startswith("int-"):
        replacement = {
            "int-leading-zero": "0x01",
            "int-negative-zero": "-0x0",
            "int-uppercase": "0xA",
            "int-too-long": "0x1" + "0" * 8192,
        }
        child["limits"]["work"] = (
            True if malformation == "int-bool" else {"integerHex": replacement[malformation]}
        )
    elif malformation.startswith("bytes-"):
        child["batch"]["payload"]["bytes"] = "a" if malformation == "bytes-odd" else "AA"
    elif malformation in {"number", "nan"}:
        raw = captured.payload_json.replace(
            b'"format":',
            b'"format":' + (b"1," if malformation == "number" else b"NaN,") + b'"profile":',
            1,
        )
        wire = (raw, captured.rows_json)
        expected = replace(captured.expected, payload_digest=sha(raw))
        assert_rejected(captured, wire=wire, expected=expected)
        return
    elif malformation == "duplicate":
        raw = captured.payload_json.replace(b"{", b'{"format":"i05-reasoning-result/2",', 1)
        assert_rejected(
            captured,
            wire=(raw, captured.rows_json),
            expected=replace(captured.expected, payload_digest=sha(raw)),
        )
        return
    elif malformation == "surrogate":
        raw = captured.payload_json.replace(b'"format":', b'"format":"\\ud800","profile":', 1)
        assert_rejected(
            captured,
            wire=(raw, captured.rows_json),
            expected=replace(captured.expected, payload_digest=sha(raw)),
        )
        return
    elif malformation == "utf8":
        raw = b"\xff" + captured.payload_json
        assert_rejected(
            captured,
            wire=(raw, captured.rows_json),
            expected=replace(captured.expected, payload_digest=sha(raw)),
        )
        return
    assert_rejected(captured, payload=payload)


def test_rows_last_tail_is_required_even_with_rebound_rows_hash(captured):
    rows = json.loads(captured.rows_json)
    rows[-1][0] = rows[-1][0][:-1]
    raw = canonical(rows)
    assert_rejected(
        captured,
        wire=(captured.payload_json, raw),
        expected=replace(captured.expected, rows_digest=sha(raw)),
    )


def test_direct_pickle_and_alias_values_do_not_restore_issuance(captured):
    original = captured.native["mechanismBatches"][0]["batch"].firings[0].comparisons[0].left
    manual = rule_terms.ProfileValue(
        original.term, original.domain, original.value, original.language
    )
    restored_pickle = pickle.loads(pickle.dumps(original))
    for value in (manual, restored_pickle):
        with pytest.raises(ProfileFailure):
            rule_terms.check_value(value, Budget())
    alias_name = "ontolearn_engine.quality._restore_test_alias_terms"
    spec = importlib.util.spec_from_file_location(alias_name, rule_terms.__file__)
    assert spec is not None and spec.loader is not None
    alias = importlib.util.module_from_spec(spec)
    sys.modules[alias_name] = alias
    try:
        spec.loader.exec_module(alias)
        value = alias.ProfileValue(
            original.term, original.domain, original.value, original.language
        )
        with pytest.raises(ProfileFailure):
            rule_terms.check_value(value, Budget())
    finally:
        sys.modules.pop(alias_name)
    for blob in (
        captured.payload,
        original,
        captured.native["mechanismBatches"][0]["batch"],
        pickle.dumps(original),
    ):
        assert_rejected(captured, wire=(blob, captured.rows_json))


def thaw_view(value):
    """Test-only independent signature adapter; product exposes no thaw API."""
    if type(value) is restore.ReadonlyObject:
        return {key: thaw_view(item) for key, item in value.entries}
    if type(value) is restore.ReadonlySequence:
        values = tuple(thaw_view(item) for item in value.items)
        return list(values) if value.native_kind == "list" else values
    return value


@pytest.mark.parametrize("domain", ["I", "S", "L", "B", "N", "Dl", "Dz", "Tl", "Tz"])
def test_fullview_all_fields_and_domains_in_fresh_process(domain):
    exec_restore(domain_capture(domain), "fullview-domain-" + domain, fullview=True)


@pytest.mark.parametrize(
    "mode", ["false-true", "disabled", "no-matches", "no-definitions", "multiple", "multihead"]
)
def test_fullview_original_complete_schema_and_slots(mode):
    rules, disabled, text = (rule(),), (), turtle()
    if mode == "disabled":
        disabled = ("r",)
    elif mode == "no-matches":
        text = turtle(values=())
    elif mode == "no-definitions":
        rules = ()
    elif mode == "multiple":
        rules = (rule("z"), rule("a"))
    elif mode == "multihead":
        spec = rule()
        rules = (
            replace(
                spec,
                heads=spec.heads
                + (Triple(Variable("?s"), iri("urn:out"), TermInput("literal", "second")),),
            ),
        )
    capture = capture_case(text=text, rules=rules, disabled=disabled, label="full-" + mode)
    result, ledger = restore_capture(capture, fullview=True)
    outer = result.projection.payload
    reasoning = outer["reasoning"]
    assert len(outer.entries) == 7 and len(reasoning.entries) == 15
    for child in reasoning["mechanismBatches"].items:
        assert len(child.entries) == 11
    assert signature(thaw_view(outer)) == signature(
        {**capture.payload, "reasoning": capture.native}
    )
    assert result.rows_json is capture.rows_json
    assert ledger.state == "success" and not any(v for _, v in ledger.live)
    assert dict(result.retention)["scalar"] > 0
    exec_restore(capture, "fullview-" + mode, fullview=True)


def test_fullview_is_deeply_readonly_and_retains_canonical_values(captured):
    from dataclasses import FrozenInstanceError

    result, _ = restore_capture(captured, fullview=True)
    outer = result.projection.payload
    reasoning = outer["reasoning"]
    child = reasoning["mechanismBatches"].items[0]
    with pytest.raises(FrozenInstanceError):
        outer.entries = ()
    with pytest.raises(TypeError):
        reasoning["evidence"].items[0]["inputs"] = ()
    with pytest.raises(TypeError):
        child["budgetUsage"].entries[0] = ("work", 0)
    with pytest.raises(FrozenInstanceError):
        child["originalMatches"].items = ()
    batch = result.batches.children[0].batch
    pv = batch.firings[0].comparisons[0].left
    rule_terms.check_value(pv, Budget())
    with pytest.raises(FrozenInstanceError):
        pv.domain = "N"
    with pytest.raises(KeyError):
        outer["unknown"]


if __name__ == "__main__":
    assert sys.argv[1:] == ["--restore-child"]
    _child_main()
