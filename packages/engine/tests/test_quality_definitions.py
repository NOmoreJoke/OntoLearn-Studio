"""Real validation/planning tests; do not pretend that a semantic engine executed."""

import copy
import json
from pathlib import Path

import pytest
from ontolearn_engine.quality import DefinitionError, build_plan, validate_definition

FIXTURE = json.loads((Path(__file__).parents[3] / "tests/fixtures/quality/g-base.json").read_text())
CONTEXT = {
    "projectId": "p1",
    "inputSnapshotId": "snapshot1",
    "projectRevision": 0,
    "dependencyVector": {"facts:asserted": 0, "ontology:core": 0, "rule:R-risk": 0},
}


def rule():
    return copy.deepcopy(FIXTURE["definitions"][1])


def constraint():
    return copy.deepcopy(FIXTURE["definitions"][0])


def plan(definitions, **kwargs):
    return build_plan(
        definitions,
        context=CONTEXT,
        catalog=kwargs.pop("catalog", FIXTURE["catalog"]),
        validation_scope=kwargs.pop("validation_scope", "asserted"),
        **kwargs,
    )


@pytest.mark.parametrize(
    ("template", "parameters"),
    [
        ("required", {}),
        ("datatype", {"datatype": "http://www.w3.org/2001/XMLSchema#integer"}),
        ("maxCount", {"maxCount": 0}),
        ("allowedValues", {"values": ['"High"', '"Low"']}),
        ("numericRange", {"minInclusive": "-0.5", "maxInclusive": "10"}),
        ("numericRange", {"minInclusive": None, "maxInclusive": "10"}),
    ],
)
def test_constraint_templates_roundtrip(template, parameters):
    value = constraint() | {"template": template, "parameters": parameters}
    frozen = validate_definition(value)
    assert frozen.payload() == value
    value["parameters"]["unexpected"] = True
    assert "unexpected" not in frozen.payload()["parameters"]


@pytest.mark.parametrize(
    ("template", "parameters", "code"),
    [
        ("required", {"code": "run()"}, "INVALID_FIELDS"),
        ("sparql", {}, "UNSUPPORTED_TEMPLATE"),
        ("maxCount", {"maxCount": True}, "INVALID_INTEGER"),
        ("maxCount", {"maxCount": -1}, "INVALID_INTEGER"),
        ("datatype", {"datatype": []}, "UNSUPPORTED_DATATYPE"),
        ("allowedValues", {"values": ['"High"', '"High"']}, "DUPLICATE_VALUE"),
        ("allowedValues", {"values": ["_:blank"]}, "INVALID_TERM"),
        ("numericRange", {"minInclusive": "2", "maxInclusive": "1"}, "REVERSED_RANGE"),
        ("numericRange", {"minInclusive": None, "maxInclusive": None}, "EMPTY_RANGE"),
        ("numericRange", {"minInclusive": "NaN", "maxInclusive": None}, "INVALID_NUMBER"),
        ("numericRange", {"minInclusive": "1e99999", "maxInclusive": None}, "INVALID_NUMBER"),
    ],
)
def test_rejects_unsupported_and_invalid_constraints(template, parameters, code):
    with pytest.raises(DefinitionError) as caught:
        validate_definition(constraint() | {"template": template, "parameters": parameters})
    assert caught.value.code == code
    assert str(caught.value) == code


def test_rule_conjunction_comparisons_multiple_outputs_and_enable_version():
    value = rule()
    value["revision"] = 2
    value["enabled"] = False
    value["conclusions"].append(
        {"kind": "property", "subject": "?e", "path": "urn:tag", "object": '"inspect"'}
    )
    assert validate_definition(value).payload() == value
    for comparison in ("eq", "ne", "lt", "le", "gt", "ge"):
        value["conditions"][-1]["operator"] = comparison
        assert validate_definition(value).payload()["conditions"][-1]["operator"] == comparison


@pytest.mark.parametrize("bad_kind", ["not", "aggregate", "code", "recursive", "or"])
def test_rule_rejects_non_p0_conditions(bad_kind):
    value = rule()
    value["conditions"].append({"kind": bad_kind})
    with pytest.raises(DefinitionError, match="UNSUPPORTED_PATTERN"):
        validate_definition(value)


def test_rule_variables_must_be_grounded_in_input_and_comparisons_are_order_independent():
    value = rule()
    value["conditions"] = list(reversed(value["conditions"]))
    validate_definition(value)
    value["conclusions"][0]["subject"] = "?missing"
    with pytest.raises(DefinitionError, match="UNBOUND_VARIABLE"):
        validate_definition(value)
    value = rule()
    value["conditions"][-1]["left"] = "?missing"
    with pytest.raises(DefinitionError) as caught:
        validate_definition(value)
    assert caught.value.path == ("conditions", 6, "left")


@pytest.mark.parametrize(
    "field,value", [("revision", True), ("enabled", "yes"), ("schemaVersion", 2)]
)
def test_metadata_is_strict(field, value):
    with pytest.raises(DefinitionError):
        validate_definition(rule() | {field: value})
    with pytest.raises(DefinitionError, match="INVALID_FIELDS"):
        validate_definition(rule() | {"script": "run()"})


def test_empty_project_can_plan_without_claiming_execution():
    result = plan([])
    assert result["executionState"] == "not-executed"
    assert result["definitions"] == []
    assert result["warnings"] == []
    assert result["stages"][1:4] == [
        "rdfs-closure-from-asserted",
        "evaluate-all-enabled-rules-against-frozen-asserted-plus-rdfs",
        "collect-rule-outputs-without-rule-or-rdfs-refeeding",
    ]


def test_r05_r06_enabled_rules_remain_saved_and_plan_order_does_not_change():
    next_rule = FIXTURE["cases"][5]["steps"][1]["saveEnabledRule"]
    catalog = copy.deepcopy(FIXTURE["catalog"])
    catalog["classes"].append(next_rule["conclusions"][0]["class"])
    forward = plan([rule(), next_rule], catalog=catalog)
    backward = plan([next_rule, rule()], catalog=catalog)
    assert forward == backward
    assert len(forward["definitions"]) == 2
    assert {
        "code": "RULE_CHAIN_UNSUPPORTED",
        "producerRuleId": "R-risk",
        "consumerRuleId": "R-next",
        "certainty": "potential",
        "message": "当前版本不支持规则链",
    } in forward["warnings"]
    assert all(item["enabled"] for item in forward["definitions"])
    # A plan has no inferred result payload; fixtures are not executed here.
    assert "actual" not in forward


def test_plan_rejects_unknown_references_schema_outputs_duplicates_and_scope():
    value = rule()
    value["conclusions"][0]["class"] = "urn:missing"
    with pytest.raises(DefinitionError, match="UNRESOLVED_REFERENCE"):
        plan([value])
    with pytest.raises(DefinitionError, match="DUPLICATE_DEFINITION"):
        plan([rule(), rule()])
    with pytest.raises(DefinitionError, match="UNSUPPORTED_SCOPE"):
        plan([], validation_scope="historical-unlabelled")
    value = rule()
    value["conclusions"] = [
        {
            "kind": "property",
            "subject": "?e",
            "path": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            "object": "<urn:class>",
        }
    ]
    with pytest.raises(DefinitionError, match="UNSUPPORTED_SCHEMA_CONCLUSION"):
        plan([value])


def test_context_is_frozen_and_wrong_dependencies_are_rejected():
    context = copy.deepcopy(CONTEXT)
    result = build_plan(
        [], context=context, catalog=FIXTURE["catalog"], validation_scope="asserted"
    )
    context["dependencyVector"]["facts:asserted"] = 9
    assert result["context"]["dependencyVector"]["facts:asserted"] == 0
    context["dependencyVector"] = {"invented:key": 0}
    with pytest.raises(DefinitionError, match="INVALID_DEPENDENCIES"):
        build_plan([], context=context, catalog=FIXTURE["catalog"], validation_scope="asserted")


def test_invalid_literal_does_not_log_raw_value_or_exception(caplog, capsys):
    value = constraint() | {
        "template": "allowedValues",
        "parameters": {
            "values": ['"SYNTHETIC_INVALID_LITERAL"^^<http://www.w3.org/2001/XMLSchema#integer>']
        },
    }
    with pytest.raises(DefinitionError, match="INVALID_LITERAL"):
        validate_definition(value)
    assert caplog.text == ""
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""
    # Filtering ends after the parser call, rather than disabling the global logger.
    import logging

    logging.getLogger("rdflib.term").warning("safe synthetic marker")
    assert "safe synthetic marker" in caplog.text


@pytest.mark.parametrize("field", ["id", "label"])
def test_lone_surrogates_are_safe_errors_before_serialization(field):
    with pytest.raises(DefinitionError, match="INVALID_TEXT"):
        validate_definition(rule() | {field: "\ud800"})


@pytest.mark.parametrize("category", ["rule", "constraint", "ontology", "facts"])
def test_dependency_key_surrogate_is_rejected_before_plan_hashing(category):
    context = CONTEXT | {"dependencyVector": {category + ":\ud800": 0}}
    with pytest.raises(DefinitionError) as caught:
        build_plan([], context=context, catalog=FIXTURE["catalog"], validation_scope="asserted")
    assert caught.value.code == "INVALID_TEXT"
    assert caught.value.path == ("context", "dependencyVector")


@pytest.mark.parametrize(
    "datatype",
    [
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString",
        "http://www.w3.org/2001/XMLSchema#int",
        "http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
        "http://www.w3.org/2001/XMLSchema#float",
    ],
)
def test_common_datatype_templates_are_not_silently_narrowed(datatype):
    value = constraint() | {"template": "datatype", "parameters": {"datatype": datatype}}
    assert validate_definition(value).payload() == value
