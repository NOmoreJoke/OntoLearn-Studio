"""Self-contained codec/manifest/compiler tests; actual T09 data is a separate probe."""

import copy
import hashlib
import json
from pathlib import Path

import pytest
from ontolearn_engine.behavior import BehaviorError, plan_behaviors, prepare_events
from ontolearn_engine.behavior.baseline_adapter import (
    DATA,
    OWL,
    RDF_TYPE,
    XSD_BOOLEAN,
    BaselineBundle,
    adapt_case,
    compile_behavior,
    compile_event,
    decode_fact,
    decode_value,
    encode_value,
    load_bundle,
    model_state,
    project_candidate,
)

NS = "urn:test:baseline:"


def triple(subject, predicate, obj):
    return {"subject": subject, "predicate": predicate, "object": obj}


def model():
    ontology = [
        triple(NS + value, RDF_TYPE, "<" + OWL + "Class>")
        for value in ("WorkOrder", "TestObject", "Notification")
    ]
    ontology += [
        triple(NS + prop, RDF_TYPE, "<" + OWL + "DatatypeProperty>")
        for prop in ("P", "workOrderStatus")
    ]
    ontology += [triple(NS + "notificationEvent", RDF_TYPE, "<" + OWL + "ObjectProperty>")]
    return {
        "id": "G-behavior",
        "fixtureVersion": "unit-1",
        "inputVersion": "base-1",
        "ruleVersion": "rule-1",
        "behaviorVersion": "behavior-1",
        "semanticsVersion": "E-1",
        "ontology": ontology,
        "facts": [
            triple(NS + "T1", RDF_TYPE, "<" + NS + "TestObject>"),
            triple(NS + "T1", NS + "P", '"false"^^<' + XSD_BOOLEAN + ">"),
            triple(NS + "W-test", RDF_TYPE, "<" + NS + "WorkOrder>"),
            triple(NS + "W-test", NS + "workOrderStatus", '"待处理"'),
        ],
        "singleValuedPredicates": [NS + "P", NS + "workOrderStatus"],
        "behaviors": [
            {
                "id": "X",
                "version": 1,
                "enabled": True,
                "priority": 0,
                "trigger": {"eventId": "E1"},
                "conditions": [],
                "actions": [
                    {"kind": "update-attribute", "target": "T1", "property": "P", "value": True}
                ],
            }
        ],
        "initialState": {
            "orders": [{"id": "W-test", "status": "待处理"}],
            "pendingEvents": [],
            "consumedEvents": [],
            "triggeredInstances": [],
        },
        "constraints": [],
        "rules": [],
        "queries": [],
        "mappings": [],
        "scenario": {},
    }


def case():
    return {
        "id": "B-unit",
        "baseline": "G-behavior",
        "baselineVersion": "unit-1",
        "inputVersion": "case-1",
        "ruleVersion": "rule-1",
        "behaviorVersion": "behavior-1",
        "semanticsVersion": "E-1",
        "setup": [],
        "steps": [
            {
                "op": "run-round",
                "capacity": 0,
                "events": [{"id": "E1", "type": "test", "payload": {}}],
            }
        ],
        "expected": {"facts": "POISON: expected is never an actual result"},
    }


def bundle(source_model=None, source_case=None):
    data = {
        "manifest": {"version": "unit-1"},
        "G-behavior.json": source_model or model(),
        "G-base.json": source_model or model(),
        "cases.json": {"cases": [source_case or case()]},
        "conventions.json": {"namespace": NS},
    }
    return BaselineBundle(json.dumps(data, ensure_ascii=False), "unit-only-not-a-real-manifest")


def derive(prepared):
    data = prepared.reasoning_input
    data.pop("state")
    return {**data, "version": "manual-unit-input", "status": "current", "facts": []}


@pytest.mark.parametrize(
    "value",
    [
        '"001"',
        '"false"',
        '"泵\\n站"',
        '"true"^^<' + XSD_BOOLEAN + ">",
        '"false"^^<' + XSD_BOOLEAN + ">",
        "<urn:test:object>",
    ],
)
def test_fixed_value_codec_round_trips_exact_string_boolean_and_iri(value):
    decoded = decode_value(value)
    assert encode_value(decoded, "relation" if value.startswith("<") else "literal") == value


@pytest.mark.parametrize(
    "value",
    [
        '"1"^^<' + XSD_BOOLEAN + ">",
        '"FALSE"^^<' + XSD_BOOLEAN + ">",
        '"x"@en',
        '"1"^^<urn:unknown:datatype>',
        "1",
        "false",
        '"\\ud800"',
    ],
)
def test_unknown_or_lossy_literals_are_rejected(value):
    with pytest.raises(BehaviorError):
        decode_value(value)


def test_adaptation_never_uses_expected_and_preserves_assertions_and_boolean_condition():
    adapted = adapt_case(
        bundle(), "B-unit", {"project_id": "p", "scenario_id": "s", "mode": "sample"}, "r"
    )
    request = adapted["request"]
    prepared = prepare_events(request)
    result = plan_behaviors(prepared, derive(prepared))
    projected = project_candidate(result, model(), NS)
    expected = model()["facts"]
    expected = [f for f in expected if f["predicate"] != NS + "P"] + [
        triple(NS + "T1", NS + "P", '"true"^^<' + XSD_BOOLEAN + ">")
    ]
    assert {json.dumps(f, sort_keys=True) for f in projected["facts"]} == {
        json.dumps(f, sort_keys=True) for f in expected
    }
    assert projected["orders"] == [{"id": "W-test", "status": "待处理"}]
    assert projected["actionTrace"] == [{"eventId": "E1", "behaviorId": "X", "actionIndex": 1}]
    assert projected["committed"] is False
    assert adapted["source"]["product_runtime"] == "not-executed"
    assert "POISON" not in json.dumps(adapted)


def test_event_identity_compiles_stably_and_addfacts_are_not_flattened_into_payload():
    _, schema, _ = model_state(model())
    source = {
        "id": "E1",
        "type": "add",
        "payload": {"addFacts": [triple(NS + "new", NS + "P", '"false"^^<' + XSD_BOOLEAN + ">")]},
    }
    compiled = compile_event(source, 0, NS, schema)
    assert compiled["edits"] == [
        {"kind": "declare", "object": NS + "E1"},
        {"kind": "declare", "object": NS + "new"},
        {"kind": "set", "subject": NS + "new", "property": NS + "P", "value": False},
    ]
    assert compiled["payload"] == {}
    assert compile_event(copy.deepcopy(source), 0, NS, schema) == compiled
    source["payload"]["http"] = "https://example.invalid"
    with pytest.raises(BehaviorError, match="invalid_shape"):
        compile_event(source, 0, NS, schema)


def test_local_order_identifier_with_colon_is_namespaced_and_keeps_one_create_action():
    _, schema, _ = model_state(model())
    source = {
        "id": "B",
        "version": 1,
        "enabled": True,
        "priority": 0,
        "trigger": {"eventId": "E1"},
        "conditions": [],
        "actions": [
            {
                "kind": "create-individual",
                "class": NS + "WorkOrder",
                "id": "W:{eventId}",
                "properties": {"workOrderStatus": "待处理"},
            }
        ],
    }
    compiled = compile_behavior(source, NS, schema)
    assert compiled["actions"] == [
        {
            "kind": "create",
            "object": {"event_template": NS + "W:{eventId}"},
            "initial": [
                {"property": RDF_TYPE, "value": NS + "WorkOrder"},
                {"property": NS + "workOrderStatus", "value": "待处理"},
            ],
        }
    ]
    assert compiled["conditions"] == [{"op": "always"}]
    del source["conditions"]
    with pytest.raises(BehaviorError, match="missing_field"):
        compile_behavior(source, NS, schema)


@pytest.mark.parametrize("kind", ["resource", "agent"])
def test_cases_requiring_real_resource_or_agent_are_explicitly_pending(kind):
    source = case()
    if kind == "resource":
        source["steps"][0]["capacity"] = 1
    else:
        source["steps"] = [{"op": "invoke-behavior-tool", "injectedFailure": "failed"}]
    with pytest.raises(BehaviorError, match="pending_round_executor"):
        adapt_case(bundle(source_case=source), "B-unit", {}, "r")


def test_version_mismatch_is_rejected():
    source = case()
    source["behaviorVersion"] = "different"
    with pytest.raises(BehaviorError, match="fixture_version_mismatch"):
        adapt_case(bundle(source_case=source), "B-unit", {}, "r")


def test_literal_cannot_be_used_for_a_relation_or_class():
    _, schema, _ = model_state(model())
    with pytest.raises(BehaviorError, match="invalid_fixture_object_kind"):
        decode_fact(triple(NS + "T1", RDF_TYPE, '"TestObject"'), schema)


def write_bundle(root: Path):
    root.mkdir()
    files = {
        DATA + "G-base.json": model(),
        DATA + "G-behavior.json": model(),
        DATA + "cases.json": {"cases": [case()]},
        DATA + "conventions.json": {"namespace": NS},
    }
    digests = {}
    for name, value in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        digests[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    source = root / "source.md"
    source.write_text("synthetic test source", encoding="utf-8")
    manifest = {
        "version": "unit-1",
        "source": {"path": "source.md", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "files": digests,
    }
    target = root / DATA / "manifest.json"
    target.write_text(json.dumps(manifest), encoding="utf-8")
    return target, manifest


def test_manifest_hash_and_every_file_are_verified(tmp_path):
    root = tmp_path / "root"
    path, _ = write_bundle(root)
    pin = hashlib.sha256(path.read_bytes()).hexdigest()
    assert load_bundle(root, pin).document["cases.json"] == {"cases": [case()]}
    with pytest.raises(BehaviorError, match="fixture_manifest_mismatch"):
        load_bundle(root, "0" * 64)
    (root / DATA / "cases.json").write_text("tampered", encoding="utf-8")
    with pytest.raises(BehaviorError, match="fixture_file_mismatch"):
        load_bundle(root, pin)


def test_manifest_cannot_escape_its_readonly_root(tmp_path):
    root = tmp_path / "root"
    path, manifest = write_bundle(root)
    manifest["source"]["path"] = "../outside.md"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BehaviorError, match="invalid_fixture_path"):
        load_bundle(root, hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.mark.parametrize("kind", ["notify", "create"])
@pytest.mark.parametrize("identity", ["bad id", "bad>id"])
def test_expanded_rdf_subjects_are_validated_before_projection(kind, identity):
    source = model()
    source["behaviors"][0]["id"] = identity
    if kind == "notify":
        action = {"kind": "notify", "id": "N:{eventId}:{behaviorId}", "event": "{eventId}"}
    else:
        action = {
            "kind": "create-individual",
            "id": "W:{eventId}:{behaviorId}",
            "class": NS + "WorkOrder",
            "properties": {"workOrderStatus": "待处理"},
        }
    source["behaviors"][0]["actions"] = [action]
    adapted = adapt_case(
        bundle(source_model=source),
        "B-unit",
        {"project_id": "p", "scenario_id": "s", "mode": "sample"},
        "r",
    )
    prepared = prepare_events(adapted["request"])
    plan = plan_behaviors(prepared, derive(prepared))
    before = copy.deepcopy(plan)
    with pytest.raises(BehaviorError, match="invalid_fixture_iri: baseline.iri"):
        project_candidate(plan, source, NS)
    assert plan == before
    assert plan["committed"] is False


def test_notification_event_iri_is_validated_in_projection():
    source = model()
    source["behaviors"][0]["actions"] = [
        {"kind": "notify", "id": "N:{eventId}", "event": "{eventId}"}
    ]
    adapted = adapt_case(
        bundle(source_model=source),
        "B-unit",
        {"project_id": "p", "scenario_id": "s", "mode": "sample"},
        "r",
    )
    prepared = prepare_events(adapted["request"])
    plan = plan_behaviors(prepared, derive(prepared))
    plan["candidate"]["notifications"][0]["event_id"] = "bad event"
    with pytest.raises(BehaviorError, match="invalid_fixture_iri: baseline.iri"):
        project_candidate(plan, source, NS)
