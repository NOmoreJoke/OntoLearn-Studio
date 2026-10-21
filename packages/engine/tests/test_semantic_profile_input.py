"""Actual data material, before computation; no saved expected supplies input."""

import hashlib
import json
from dataclasses import FrozenInstanceError, replace

import pytest
from ontolearn_engine.quality.rule_profile import SourceRecord, TermInput
from ontolearn_engine.semantic_profile_input import (
    CaptureLedger,
    MaterialFailure,
    ProfileInputLayer,
    decode_rule_definitions,
    decode_selected_material,
    prepare_profile_material,
    prepare_selected_material,
)
from test_semantic_profile_restore import canonical, project, rule, turtle


def test_text_material_original_utf8_source_and_definition():
    text = turtle(padding="# 原样\n")
    spec = rule(source=SourceRecord("", None, "修订", ""))
    material = prepare_profile_material(
        text,
        (spec,),
        source_reference="",
        source_revision="修订",
    )
    assert material.input_preimage == text.encode("utf-8")
    assert material.source_preimage == canonical(project(material.source))
    assert material.definitions_preimage == canonical(project((spec,)))
    assert material.source.reference == ""
    assert material.source.revision == "修订"
    assert material.source.text == text
    body = json.loads(material.definition_material)
    assert body["version"] == "profile-rule-definition/1"
    assert body["rules"][0]["enabled"] is True
    assert {k: v for k, v in body["rules"][0].items() if k != "enabled"} == {
        k: v for k, v in project(spec).items() if k != "recordType"
    }
    with pytest.raises(FrozenInstanceError):
        material.input_preimage = b"changed"


def test_structured_order_none_empty_language_and_source():
    source = SourceRecord("", "原摘要", None, "")
    first = (
        TermInput("iri", "urn:s", source=source),
        TermInput("iri", "urn:p"),
        TermInput("literal", "原文", language_raw="ZH-cn", source=source),
    )
    second = (TermInput("iri", "urn:t"), TermInput("iri", "urn:p"), TermInput("literal", ""))
    records = (first, second)
    material = prepare_profile_material(records=records)
    assert material.records is records
    assert material.input_preimage == canonical(project(records))
    assert material.source_preimage == canonical(
        project(tuple(t.source for r in records for t in r))
    )
    assert material.records[0][2].language_raw == "ZH-cn"
    assert material.source[0] is source


def test_disabled_definition_ordinal_and_empty_rules_not_guessed():
    specs = (rule("z"), rule("a"))
    material = prepare_profile_material(turtle(), specs, disabled_rule_ids=("z",))
    body = json.loads(material.definition_material)
    assert [r["rule_id"] for r in body["rules"]] == ["z", "a"]
    assert [r["enabled"] for r in body["rules"]] == [False, True]
    assert body["disabledRuleIds"] == ["z"]
    empty = prepare_profile_material(turtle(), ())
    assert empty.rules == ()
    assert json.loads(empty.definitions_preimage) == []


@pytest.mark.parametrize("text_length", [65536, 65537])
def test_turtle_source_text_gate_is_original_byte_gate(text_length):
    material = prepare_profile_material("#" + "x" * (text_length - 1))
    assert len(material.input_preimage) == text_length
    assert material.source.text == (material.text if text_length == 65536 else None)


def test_consumer_has_own_nonempty_or_empty_layered_u_and_d():
    row = ((TermInput("iri", "urn:a"), TermInput("iri", "urn:p"), TermInput("literal", "x")),)
    material = prepare_selected_material(
        row,
        (),
        {"text": "SELECT * WHERE {?s ?p ?o}"},
        parser_identity=("actual-owner-parser", "1"),
    )
    assert json.loads(material.input_preimage)["assertedRecords"]["input"] == project(row)
    assert json.loads(material.input_preimage)["ontologyRecords"]["input"] == []
    assert json.loads(material.source_preimage) == {
        "assertedRecords": [None, None, None],
        "ontologyRecords": [],
    }
    assert material.asserted_records.content is row
    assert material.parser_identity == ("actual-owner-parser", "1")
    empty = prepare_selected_material(
        (), (), {"turtle": "", "enabled": False}, parser_identity=("actual-owner-parser", "1")
    )
    assert 0 < len(empty.input_preimage) <= 8_388_608
    assert json.loads(empty.definition_material)["definition"] == {"turtle": "", "enabled": False}


class _HostileMeta(type):
    def __eq__(cls, other):
        raise AssertionError("foreign equality")

    def __hash__(cls):
        raise AssertionError("foreign class hash")


class _Hostile(metaclass=_HostileMeta):
    def __len__(self):
        raise AssertionError("foreign len")

    def __iter__(self):
        raise AssertionError("foreign iter")

    def __hash__(self):
        raise AssertionError("foreign hash")


@pytest.mark.parametrize("position", ["term", "source", "rule", "disabled", "identity"])
def test_nested_foreign_rejected_before_foreign_hooks(position):
    value = _Hostile()
    kwargs = {}
    if position == "term":
        spec = rule()
        kwargs["rules"] = (replace(spec, heads=(replace(spec.heads[0], object=value),)),)
    elif position == "source":
        kwargs["rules"] = (rule(source=SourceRecord(text=value)),)
    elif position == "rule":
        kwargs["rules"] = (value,)
    elif position == "disabled":
        kwargs.update(rules=(rule(),), disabled_rule_ids=(value,))
    else:
        kwargs["parser_identity"] = (value, "1")
    with pytest.raises(MaterialFailure) as error:
        prepare_profile_material(turtle(), **kwargs)
    assert error.value.reason == "MATERIAL_INVALID"
    assert error.value.__context__ is None


@pytest.mark.parametrize("value", ["\ud800", "x" * 1048577])
def test_unicode_and_input_bound_are_finite(value):
    with pytest.raises(MaterialFailure):
        prepare_profile_material(value)


def test_lower_only_budget_precedes_work_and_cannot_be_reset():
    ledger = CaptureLedger(overrides=(("objects", 63),))
    with pytest.raises(MaterialFailure) as error:
        prepare_profile_material(turtle(), ledger=ledger)
    assert error.value.reason == "MATERIAL_LIMIT"
    assert ledger.state == "failed"
    with pytest.raises(MaterialFailure) as reused:
        prepare_profile_material(turtle(), ledger=ledger)
    assert reused.value.reason == "MATERIAL_LEDGER_REUSED"


def test_material_operation_receipt_keeps_actual_live_responsibility():
    material = prepare_profile_material(turtle(), (rule(),))
    assert dict(material.capture_receipt.retained)["scalar"] > 0
    assert dict(material.capture_receipt.retained)["objects"] > 0
    assert "remain live" in material.capture_receipt.retention_owner
    assert all(
        used <= bound
        for used, bound in zip(
            material.capture_receipt.stage_visits,
            material.capture_receipt.stage_bounds,
            strict=True,
        )
    )


def test_rule_definition_strict_roundtrip_all_fields_and_enabled():
    specs = (rule("z", source=SourceRecord("", None, "v1", "原文")), rule("a"))
    material = prepare_profile_material(turtle(), specs, disabled_rule_ids=("z",))
    decoded = decode_rule_definitions(material.definition_material)
    assert decoded.rules == specs
    assert decoded.disabled_rule_ids == ("z",)
    assert decoded.definitions_preimage == material.definitions_preimage
    assert decoded.definition_material == material.definition_material


@pytest.mark.parametrize(
    "mutation", ["duplicate", "unknown", "number", "tail", "enabled", "surrogate"]
)
def test_rule_definition_malformed_last_field_finite(mutation):
    material = prepare_profile_material(turtle(), (rule(),))
    raw = material.definition_material
    if mutation == "duplicate":
        raw = raw[:-1] + b',"version":"profile-rule-definition/1"}'
    elif mutation == "unknown":
        raw = raw[:-1] + b',"surprise":null}'
    elif mutation == "number":
        raw = raw.replace(b'"enabled":true', b'"enabled":1')
    elif mutation == "tail":
        raw += b" "
    elif mutation == "enabled":
        raw = raw.replace(b'"enabled":true', b'"enabled":false')
    else:
        raw = raw.replace(b'"policy":', b'"policy":"\\ud800","revision":')
    with pytest.raises(MaterialFailure) as error:
        decode_rule_definitions(raw)
    assert error.value.__context__ is None


@pytest.mark.parametrize("length", [12, 65537])
def test_consumer_raw_turtle_and_structured_layer_roundtrip(length):
    content = ("#原文\r\n" + "x" * length).encode("utf-8")
    source = SourceRecord(
        "source:file",
        hashlib.sha256(content).hexdigest(),
        "",
        content.decode("utf-8") if len(content) <= 65536 else None,
    )
    layer = ProfileInputLayer("utf8-turtle", content, source, ("actual-turtle-parser", "1"))
    row = ((TermInput("iri", "urn:a"), TermInput("iri", "urn:p"), TermInput("literal", "x")),)
    material = prepare_selected_material(
        layer,
        row,
        {"text": "SELECT * WHERE {?s ?p ?o}"},
        parser_identity=("actual-snapshot-owner", "1"),
    )
    decoded = decode_selected_material(
        material.input_preimage,
        material.source_preimage,
        material.definition_material,
        parser_identity=("actual-snapshot-owner", "1"),
    )
    assert decoded.asserted_records.content == content
    assert decoded.asserted_records.source == source
    assert decoded.asserted_records.parser_identity == ("actual-turtle-parser", "1")
    assert decoded.ontology_records.content == row
    assert decoded.input_preimage == material.input_preimage
    assert decoded.source_preimage == material.source_preimage
    assert decoded.definition_material == material.definition_material


@pytest.mark.parametrize(
    "definition",
    [
        {"query": "x"},
        {"text": "x", "enabled": True},
        {"turtle": "x"},
        {"turtle": "x", "enabled": None},
    ],
)
def test_consumer_d_exact_actual_query_or_constraint_body(definition):
    with pytest.raises(MaterialFailure):
        prepare_selected_material((), (), definition, parser_identity=("owner", "1"))


def test_material_failure_and_ledger_domain_do_not_compare_foreign():
    hostile = _Hostile()
    error = MaterialFailure(hostile, domain=hostile)
    assert error.reason == "MATERIAL_INTERNAL" and error.domain is None
    ledger = CaptureLedger()
    ledger.begin()
    for method in (ledger.debit, ledger.reserve, ledger.release):
        with pytest.raises(MaterialFailure):
            method(hostile, 1)


def test_escaped_wide_string_rejected_before_encoder_delegate():
    from unittest.mock import patch

    from ontolearn_engine.semantic_profile_input import MAX_BYTES, _encode

    ledger = CaptureLedger()
    ledger.begin()
    ledger.enter(1, MAX_BYTES)
    value = "\0" * (MAX_BYTES - 4) + "😀"
    with patch("ontolearn_engine.semantic_profile_input.json.JSONEncoder.iterencode") as encode:
        with pytest.raises(MaterialFailure):
            _encode(value, ledger)
    assert encode.call_count == 0


@pytest.mark.parametrize("limit", [0, 63])
def test_control_budget_rejects_before_allocating_counter_containers(limit):
    overrides = (("objects", limit),)
    ledger = CaptureLedger(overrides=overrides)
    assert ledger.overrides is overrides
    with pytest.raises(MaterialFailure) as caught:
        prepare_profile_material(turtle(), ledger=ledger)
    assert caught.value.domain == "objects" and caught.value.stage == 0
    assert ledger.caps is ledger.used is ledger.live is ledger.peaks is None
    assert ledger.stage_visits is ledger.stage_bounds is None
    assert ledger.state == "failed"
    with pytest.raises(MaterialFailure) as reused:
        ledger.begin()
    assert reused.value.reason == "MATERIAL_LEDGER_REUSED"


def test_control_budget_exact_64_opens_ticket_without_extra_capacity():
    ledger = CaptureLedger(overrides=(("objects", 64),))
    ledger.begin()
    assert ledger.caps["objects"] == ledger.live["objects"] == ledger.peaks["objects"] == 64
    with pytest.raises(MaterialFailure):
        ledger.reserve("objects", 1)
    assert ledger.live["objects"] == 64
