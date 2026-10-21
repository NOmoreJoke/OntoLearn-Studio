"""Real text caller plus canonical adapter routes; private location stays private."""

import json
from dataclasses import replace

import pytest
from ontolearn_engine.quality.rule_firing import Comparison, Variable
from ontolearn_engine.quality.rule_profile import XSD, TermInput
from ontolearn_engine.semantic_error_adapter import (
    ErrorContext,
    Origin,
    Producer,
    SemanticErrorAdapter,
    Stage,
)
from ontolearn_engine.semantic_execution import ProfileExecutionFault, execute_profile
from ontolearn_engine.semantic_profile_probe import _construct_case
from test_semantic_profile_integration import FIXTURES, ROOT


@pytest.fixture
def errors():
    root = ROOT / "packages/contracts/v2"
    return {
        "error_catalog": json.loads((root / "errors.json").read_bytes()),
        "error_schema": json.loads((root / "schema.json").read_bytes()),
    }


@pytest.mark.parametrize(
    ("reason", "code", "params"),
    [
        ("RULE_COMPARISON_TYPE_MISMATCH", "SEMANTIC_INPUT_INVALID", {"field": "rule"}),
        ("RULE_INPUT_BUDGET", "RESOURCE_LIMIT", {"resource": "semanticInput"}),
        ("RULE_POLICY_UNSUPPORTED", "UNSUPPORTED_CAPABILITY", {}),
    ],
)
def test_precise_new_adapter_routes_and_negative_contexts(errors, reason, code, params):
    adapter = SemanticErrorAdapter(**errors)
    result = adapter.adapt(
        producer=Producer.REASON,
        reason=reason,
        context=ErrorContext(Stage.RULE, Origin.VERIFIED_USER_INPUT),
    )
    assert result["code"] == code and result["params"] == params
    assert set(result) == {"code", "messageKey", "params", "retryable"}
    for origin in (Origin.TRUSTED_INTERNAL, Origin.UNKNOWN):
        assert (
            adapter.adapt(
                producer=Producer.REASON, reason=reason, context=ErrorContext(Stage.RULE, origin)
            )["code"]
            == "INTERNAL_ERROR"
        )
    assert (
        adapter.adapt(
            producer=Producer.TURTLE,
            reason=reason,
            context=ErrorContext(Stage.SYNTAX, Origin.VERIFIED_USER_INPUT),
        )["code"]
        == "INTERNAL_ERROR"
    )


def test_actual_late_comparison_reports_rule_location_and_no_raw_error(errors):
    fixture = json.loads((FIXTURES / "firing-cases.json").read_bytes())
    text, rules = _construct_case(fixture)
    mismatch = Comparison(Variable("?v"), "eq", TermInput("literal", "true", XSD + "boolean"))
    spec = replace(rules[0], comparisons=(mismatch,))
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile(text, (spec,), **errors)
    error = caught.value
    assert error.error["code"] == "SEMANTIC_INPUT_INVALID"
    assert error.error["params"] == {"field": "rule"}
    assert error.diagnostic["reason"] == "RULE_COMPARISON_TYPE_MISMATCH"
    assert error.diagnostic["location"]["section"] == "comparison"
    assert error.diagnostic["location"]["index"] == 0
    assert error.diagnostic["ruleId"] == spec.rule_id
    assert "true" not in json.dumps(error.error)
    assert str(error) == "SEMANTIC_EXECUTION_FAILED"


def test_unknown_canary_fails_closed_and_never_copies_reason(errors):
    adapter = SemanticErrorAdapter(**errors)
    canary = "CANARY_private_input"
    error = adapter.adapt(
        producer=Producer.REASON,
        reason=canary,
        context=ErrorContext(Stage.RULE, Origin.VERIFIED_USER_INPUT),
    )
    assert error["code"] == "INTERNAL_ERROR"
    assert canary not in json.dumps(error)


def test_real_caller_serialization_failure_returns_no_partial_result(errors, monkeypatch):
    from ontolearn_engine import semantic_execution

    text, rules = _construct_case(json.loads((FIXTURES / "firing-cases.json").read_bytes()))
    monkeypatch.setattr(semantic_execution, "MAX_OUTPUT_BYTES", 64)
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile(text, rules, **errors)
    assert caught.value.error["code"] == "RESOURCE_LIMIT"
    assert caught.value.error["params"] == {"resource": "semanticResult"}


def test_probe_rejects_extra_arguments_before_product_work(capsys):
    from ontolearn_engine.semantic_profile_probe import main

    assert main(["https://canary.invalid/private"]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == "PROFILE_PROBE_ARGUMENTS_INVALID\n"


def test_actual_graph_work_failure_is_resource_not_rule_syntax(errors, monkeypatch):
    from ontolearn_engine import semantic

    text, rules = _construct_case(json.loads((FIXTURES / "firing-cases.json").read_bytes()))
    monkeypatch.setattr(semantic, "MAX_WORK", 0)
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile(text, rules, **errors)
    assert caught.value.error["code"] == "RESOURCE_LIMIT"
    assert caught.value.error["params"] == {"resource": "semanticWork"}
    assert caught.value.diagnostic["ruleId"] is None
    assert caught.value.diagnostic["reason"] == "WORK_LIMIT"


@pytest.mark.parametrize("field", ["source_reference", "source_revision"])
def test_actual_metadata_unicode_failure_is_safe_input(errors, field):
    text, rules = _construct_case(json.loads((FIXTURES / "firing-cases.json").read_bytes()))
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile(text, rules, **{field: "\ud800"}, **errors)
    assert caught.value.diagnostic["reason"] == "INVALID_UNICODE"
    assert caught.value.error["code"] == "SEMANTIC_INPUT_INVALID"
    assert caught.value.diagnostic["ruleId"] is None
    assert "\\ud800" not in json.dumps(caught.value.error)


@pytest.mark.parametrize(
    "text,reason",
    [
        (
            "<urn:p> a <http://www.w3.org/2002/07/owl#ObjectProperty>, "
            "<http://www.w3.org/2002/07/owl#DatatypeProperty> .",
            "INVALID_ONTOLOGY_CATALOG",
        ),
        (
            '<urn:s> <urn:p> "x"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString> .',
            "RDF_TERM_INVALID",
        ),
    ],
)
def test_real_graph_input_errors_never_claim_a_rule(errors, text, reason):
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile(text, **errors)
    assert caught.value.error["code"] == "SEMANTIC_INPUT_INVALID"
    assert caught.value.error["params"] == {"field": "syntax"}
    assert caught.value.diagnostic["ruleId"] is None
    assert caught.value.diagnostic["location"] is None
    assert caught.value.diagnostic["reason"] == reason


def test_actual_rdfs_expansion_limit_uses_rule_stage(monkeypatch, errors):
    from ontolearn_engine import semantic

    monkeypatch.setattr(semantic, "MAX_TRIPLES", 2)
    text = (
        "<urn:Child> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:Parent> . "
        "<urn:s> a <urn:Child> ."
    )
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile(text, **errors)
    assert caught.value.error["code"] == "RESOURCE_LIMIT"
    assert caught.value.diagnostic["reason"] == "RDFS_RESULT_LIMIT"
    assert caught.value.diagnostic["ruleId"] is None


def test_raw_record_input_projection_limit_is_resource(errors):
    from ontolearn_engine.quality.rule_profile import SourceRecord
    from ontolearn_engine.semantic_execution import execute_profile_records

    source = SourceRecord(text="x" * 65536)
    records = tuple(
        (
            TermInput("iri", f"urn:s:{index}", source=source),
            TermInput("iri", "urn:p", source=source),
            TermInput("literal", "x", source=source),
        )
        for index in range(9)
    )
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile_records(records, **errors)
    assert caught.value.error["code"] == "RESOURCE_LIMIT"
    assert caught.value.error["params"] == {"resource": "semanticInput"}
    assert caught.value.diagnostic["reason"] == "GRAPH_INPUT_LIMIT"
    assert caught.value.diagnostic["classification"] == "resource"


@pytest.mark.parametrize("value", [TermInput("wrong", "x"), "not-a-TermInput"])
def test_raw_record_bad_shape_is_user_input_not_issued_context_corruption(errors, value):
    from ontolearn_engine.semantic_execution import execute_profile_records

    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile_records(
            ((TermInput("iri", "urn:s"), TermInput("iri", "urn:p"), value),), **errors
        )
    assert caught.value.error["code"] == "SEMANTIC_INPUT_INVALID"
    assert caught.value.diagnostic["reason"] == "RDF_TERM_INVALID"
    assert caught.value.diagnostic["ruleId"] is None


@pytest.mark.parametrize("disabled", [42, ("r", "r"), ("\ud800",)])
def test_disabled_input_has_same_actual_rule_boundary_for_text_and_records(errors, disabled):
    from ontolearn_engine.semantic_execution import execute_profile_records

    failures = []
    for invoke, data in ((execute_profile, ""), (execute_profile_records, ())):
        with pytest.raises(ProfileExecutionFault) as caught:
            invoke(data, disabled_rule_ids=disabled, **errors)
        failures.append(caught.value)
    assert failures[0].error == failures[1].error
    assert failures[0].error["code"] == "SEMANTIC_INPUT_INVALID"
    assert failures[0].error["params"] == {"field": "rule"}
    assert failures[0].diagnostic == failures[1].diagnostic


@pytest.mark.parametrize("missing_source", [False, True])
def test_raw_records_missing_native_slot_is_input_error(errors, missing_source):
    from ontolearn_engine.quality.rule_profile import SourceRecord
    from ontolearn_engine.semantic_execution import execute_profile_records

    value = (
        TermInput("literal", "x", source=object.__new__(SourceRecord))
        if missing_source
        else object.__new__(TermInput)
    )
    with pytest.raises(ProfileExecutionFault) as caught:
        execute_profile_records(
            ((TermInput("iri", "urn:s"), TermInput("iri", "urn:p"), value),), **errors
        )
    assert caught.value.error["code"] == "SEMANTIC_INPUT_INVALID"
    assert caught.value.diagnostic["reason"] == "RDF_TERM_INVALID"
