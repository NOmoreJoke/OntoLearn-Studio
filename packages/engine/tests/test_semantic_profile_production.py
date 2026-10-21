"""Real material -> unique actual computation; no mocked producer result."""

import hashlib
import json
from dataclasses import replace
from unittest.mock import patch

import pytest
from ontolearn_engine import semantic, semantic_execution
from ontolearn_engine.quality import rule_firing
from ontolearn_engine.quality.rule_firing import Triple, Variable
from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput
from ontolearn_engine.resources import CONTRACT, ROOT
from ontolearn_engine.semantic_profile_input import (
    CaptureLedger,
    MaterialFailure,
    prepare_profile_material,
)
from ontolearn_engine.semantic_profile_production import execute_admitted_profile_job
from ontolearn_engine.semantic_profile_restore import RestoreExpectation, restore_profile_batches
from ontolearn_engine.semantic_profile_restore_budget import RestoreLedger
from test_semantic_profile_restore import canonical, iri, project, rule, signature, turtle

SCHEMA = json.loads((ROOT / "v2/schema.json").read_bytes())


def execute(material, ledger=None):
    return execute_admitted_profile_job(
        material, error_catalog=CONTRACT.ERROR_CATALOG, error_schema=SCHEMA, ledger=ledger
    )


def test_real_occurrence_capture_once_and_complete_raw_outputs():
    specs = (rule("z"), rule("a"))
    material = prepare_profile_material(turtle(), specs, disabled_rule_ids=("z",))
    with (
        patch.object(semantic, "_profile_reason", wraps=semantic._profile_reason) as reason_call,
        patch.object(
            semantic, "_profile_definitions", wraps=semantic._profile_definitions
        ) as definitions,
        patch.object(semantic, "_profile_catalog", wraps=semantic._profile_catalog) as catalog,
        patch.object(rule_firing, "compile_rules", wraps=rule_firing.compile_rules) as compile_call,
        patch.object(
            rule_firing, "evaluate_bound_batch", wraps=rule_firing.evaluate_bound_batch
        ) as evaluate,
    ):
        produced = execute(material)
    assert reason_call.call_count == definitions.call_count == catalog.call_count == 1
    assert compile_call.call_count == 2
    assert evaluate.call_count == 1
    assert [s.rule_id for _, s in produced.actual_definitions] == ["a", "z"]
    assert produced.original_allocation.rule_ids == ("z", "a")
    assert produced.original_allocation.disabled_rule_ids == ("z",)
    for slot, call in zip(
        produced.original_allocation.children, compile_call.call_args_list, strict=True
    ):
        assert slot.limits is call.args[2].limits
    assert produced.actual_catalog is produced.native_result["catalog"]
    assert produced.payload_json == canonical(produced.wire["payload"])
    assert produced.rows_json == canonical(produced.wire["rows"])
    assert produced.source_encoded == material.source_preimage
    assert produced.definitions_encoded == material.definitions_preimage
    assert produced.catalog_json == canonical(project(produced.actual_catalog))
    assert not hasattr(produced, "formal_authority")


@pytest.mark.parametrize("kind", ["text", "structured", "disabled", "dummy", "empty", "multihead"])
def test_actual_outputs_keep_false_true_disabled_dummy_empty_and_head_order(kind):
    specs, disabled, records = (rule(),), (), None
    text = turtle()
    if kind == "structured":
        source = SourceRecord("row:1", "raw-digest", "v1", "原文")
        records = (
            (
                iri("urn:value"),
                iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                iri("http://www.w3.org/2002/07/owl#DatatypeProperty"),
            ),
            (
                iri("urn:out"),
                iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                iri("http://www.w3.org/2002/07/owl#DatatypeProperty"),
            ),
            (
                iri("urn:s"),
                iri("urn:value"),
                TermInput(
                    "literal", "2", "http://www.w3.org/2001/XMLSchema#integer", source=source
                ),
            ),
        )
        text = None
    elif kind == "disabled":
        disabled = ("r",)
    elif kind == "dummy":
        specs = ()
    elif kind == "empty":
        specs = (rule(predicate="urn:unmatched"),)
        text += "<urn:unmatched> a <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n"
    elif kind == "multihead":
        specs = (
            replace(
                rule(),
                heads=(
                    rule().heads[0],
                    Triple(Variable("?s"), iri("urn:out"), TermInput("literal", "second")),
                ),
            ),
        )
    material = prepare_profile_material(text, specs, records=records, disabled_rule_ids=disabled)
    produced = execute(material)
    if records is None:
        old = semantic_execution.execute_profile(
            text,
            specs,
            disabled_rule_ids=disabled,
            error_catalog=CONTRACT.ERROR_CATALOG,
            error_schema=SCHEMA,
        )
    else:
        old = semantic_execution.execute_profile_records(
            records,
            specs,
            disabled_rule_ids=disabled,
            error_catalog=CONTRACT.ERROR_CATALOG,
            error_schema=SCHEMA,
        )
    assert produced.wire == old
    children = produced.native_result["mechanismBatches"]
    assert len(children) == max(1, len(specs))
    if kind == "disabled":
        assert children[0]["batch"] is None and children[0]["originalMatches"] is None
    elif kind == "dummy":
        assert children[0]["ruleId"] is None and children[0]["definitionOrdinal"] is None
    elif kind == "empty":
        assert children[0]["batch"].firings == ()
    elif kind == "multihead":
        assert [
            head.triple.object.lexical_form for head in children[0]["batch"].firings[0].heads
        ] == ["ok", "second"]
    elif kind == "text":
        assert len(children[0]["originalMatches"]) == 2
        assert len(children[0]["batch"].firings) == 1


def test_actual_producer_can_supply_original_pure_restore_context():
    produced = execute(prepare_profile_material(turtle(), (rule(),)))

    def sha(raw):
        return hashlib.sha256(raw).hexdigest()

    payload = produced.wire["payload"]
    expected = RestoreExpectation(
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
    restored = restore_profile_batches(
        produced.payload_json,
        produced.rows_json,
        expected=expected,
        allocation=produced.original_allocation,
        ledger=RestoreLedger(),
    )
    assert restored.formal_authority is False
    assert signature(restored.children[0].batch) == signature(
        produced.native_result["mechanismBatches"][0]["batch"]
    )


@pytest.mark.parametrize(
    "field", ["input_preimage", "source_preimage", "definitions_preimage", "definition_material"]
)
def test_preimage_mismatch_rejected_before_unique_reason(field):
    material = prepare_profile_material(turtle(), (rule(),))
    changed = replace(material, **{field: getattr(material, field) + b" "})
    with patch.object(semantic, "_profile_reason", wraps=semantic._profile_reason) as reason_call:
        with pytest.raises(MaterialFailure) as error:
            execute(changed)
    assert error.value.reason == "MATERIAL_MISMATCH"
    assert reason_call.call_count == 0
    assert error.value.__context__ is None


def test_capture_c_failure_before_core_has_no_returned_half_record():
    material = prepare_profile_material(turtle(), (rule(),))
    ledger = CaptureLedger(overrides=(("objects", 63),))
    with patch.object(semantic, "_profile_reason", wraps=semantic._profile_reason) as reason_call:
        with pytest.raises(MaterialFailure) as error:
            execute(material, ledger)
    assert reason_call.call_count == 0
    assert error.value.reason == "MATERIAL_LIMIT"
    assert ledger.state == "failed"


def test_returned_record_reports_live_references_and_complete_stage_limits():
    produced = execute(prepare_profile_material(turtle(), (rule(),)))
    assert produced.native_result["mechanismBatches"][0]["batch"] is not None
    assert dict(produced.capture_receipt.retained)["scalar"] > 0
    assert all(
        a <= b
        for a, b in zip(
            produced.capture_receipt.stage_visits,
            produced.capture_receipt.stage_bounds,
            strict=True,
        )
    )


def test_fake_actual_parser_identity_rejected_before_core():
    material = replace(
        prepare_profile_material(turtle(), (rule(),)), parser_identity=("fake", "v999")
    )
    with patch.object(semantic, "_profile_reason", wraps=semantic._profile_reason) as call:
        with pytest.raises(MaterialFailure):
            execute(material)
    assert call.call_count == 0


@pytest.mark.parametrize("domain", ["traversal", "scan_copy", "hash", "scalar", "objects"])
def test_each_c_domain_exact_boundary_and_one_less(domain):
    material = prepare_profile_material(turtle(), (rule(),))
    result = execute(material)
    receipt = result.capture_receipt
    required = dict(
        receipt.usage if domain in ("traversal", "scan_copy", "hash") else receipt.peaks
    )[domain]
    assert execute(material, CaptureLedger(overrides=((domain, required),))).wire == result.wire
    ledger = CaptureLedger(overrides=((domain, required - 1),))
    with pytest.raises(MaterialFailure) as failure:
        execute(material, ledger)
    assert failure.value.reason == "MATERIAL_LIMIT"
    assert failure.value.domain == domain
    assert ledger.state == "failed"
    assert failure.value.__context__ is None
    frame = failure.value.__traceback__
    while frame:
        if frame.tb_frame.f_code.co_name == "execute_admitted_profile_job":
            locals_ = frame.tb_frame.f_locals
            assert all(
                locals_[name] is None
                for name in (
                    "capture",
                    "checked",
                    "catalog_json",
                    "allocation",
                    "receipt",
                    "outcome",
                    "encoded_source",
                    "actual",
                    "supplied",
                    "value",
                )
            )
        frame = frame.tb_next
