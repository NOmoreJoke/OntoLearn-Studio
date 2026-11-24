"""Complete private plan expectations, not real G.3 integration acceptance."""

import copy
import json
from pathlib import Path

import pytest
from ontolearn_engine.behavior import BehaviorError, plan_behaviors, prepare_events

CORPUS_PATH = Path(__file__).parents[3] / "tests/fixtures/behavior/counterexamples.json"
CORPUS = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in CORPUS["cases"]}


def request(case="B-06"):
    return copy.deepcopy(CASES[case]["request"])


def reasoning(prepared, facts=None):
    result = prepared.reasoning_input
    result.pop("state")
    return {**result, "version": "derived-v1", "status": "current", "facts": facts or []}


def execute(req, facts=None):
    prepared = prepare_events(req)
    return plan_behaviors(prepared, reasoning(prepared, facts))


def event(identity="test-event", sequence=0):
    return {
        "id": identity,
        "type": "test",
        "sequence": sequence,
        "version": "1",
        "payload": {},
        "edits": [],
    }


def definition(identity, actions, priority=0, conditions=None):
    return {
        "id": identity,
        "name": identity,
        "description": "fixture",
        "effect": "internal",
        "version": "1",
        "enabled": True,
        "priority": priority,
        "trigger": {"event_type": "test"},
        "conditions": conditions or [{"op": "always"}],
        "actions": actions,
    }


def write(value):
    return {"kind": "set", "subject": "W-test", "property": "status", "value": value}


def bare(actions=None):
    req = request()
    req["events"] = [event()]
    req["behaviors"] = [definition("test", actions or [write("S1")])]
    return req


@pytest.mark.parametrize("case", list(CASES))
def test_complete_private_counterexamples(case):
    fixture = CASES[case]
    req, expected = request(case), fixture["expected"]
    original = copy.deepcopy(req)
    prepared = prepare_events(req)
    derived = reasoning(prepared, fixture["reasoning_facts"])
    assert prepared.document["after_events"] == expected["after_events"]
    if expected["error"]:
        with pytest.raises(BehaviorError, match=expected["error"]) as caught:
            plan_behaviors(prepared, derived)
        error = caught.value
        assert error.reason == expected["error"]
        assert error.evidence["decisions"] == expected["decisions"]
        assert error.evidence["executed_actions"] == []
        assert "candidate" not in error.evidence
        assert error.evidence["conflict"] == expected["conflict"]
        assert error.evidence["intents"] == expected["failed_intents"]
        assert error.evidence["event_trace"] == [
            {"event_id": e["id"], "reason": "event_applied"}
            for e in sorted(req["events"], key=lambda e: (e["sequence"], e["id"]))
        ]
    else:
        result = plan_behaviors(prepared, derived)
        assert result["candidate"] == expected["candidate"]
        assert result["frozen"] == expected["frozen"]
        assert result["decisions"] == expected["decisions"]
        assert result["action_trace"] == expected["action_trace"]
        assert result["diff"] == expected["diff"]
        assert result["before"] == req["state"]
        assert result["scope"] == req["scope"]
        assert result["base_revision"] == req["base_revision"]
        assert result["behavior_version"] == req["behavior_version"]
        assert result["assertion_version"] == req["assertion_version"]
        assert result["reasoning_version"] == "derived-v1"
        assert result["committed"] is False
        assert result["consumption"]["instances"] == [
            {"event_id": e, "behavior_id": b} for e, b in expected["triggered_instances"]
        ]
        assert result["event_trace"] == [
            {"event_id": e["id"], "reason": "event_applied"}
            for e in sorted(req["events"], key=lambda e: (e["sequence"], e["id"]))
        ]
        # Whole plan deterministic across independent restored inputs.
        assert result == execute(req, fixture["reasoning_facts"])
    assert req == original


def test_b04_stale_snapshot_is_rejected_and_relabelled_old_facts_would_trip_probe():
    req = request("B-04")
    previous = copy.deepcopy(req)
    previous["events"] = []
    previous_prepared = prepare_events(previous)
    old = reasoning(
        previous_prepared,
        [{"subject": "001", "property": "rdf:type", "value": "HighRiskEquipment"}],
    )
    prepared = prepare_events(req)
    with pytest.raises(BehaviorError, match="stale_reasoning"):
        plan_behaviors(prepared, old)
    fresh = reasoning(prepared)
    assert plan_behaviors(prepared, fresh)["candidate"]["notifications"] == []
    # Sensitivity control only: lying about provenance is outside a pure planner's
    # trust boundary. Real T05 recomputation is still required by B-04 acceptance.
    forged = reasoning(prepared, old["facts"])
    assert [
        n["behavior_id"] for n in plan_behaviors(prepared, forged)["candidate"]["notifications"]
    ] == ["B-probe"]


def test_repeated_event_is_noop_and_consumption_is_in_candidate_only():
    req = request("B-01")
    result = execute(req, CASES["B-01"]["reasoning_facts"])
    req["state"] = result["candidate"]
    req["consumption"] = result["consumption"]
    req["round"] = 2
    req["events"][0]["sequence"] = 99  # delivery order is not content identity
    second = execute(req, CASES["B-01"]["reasoning_facts"])
    assert second["candidate"] == result["candidate"]
    assert second["action_trace"] == second["decisions"] == []
    assert second["diff"] == {"added": [], "removed": []}
    assert second["consumption"] == result["consumption"]
    assert second["event_trace"] == [{"event_id": "E-B01", "reason": "duplicate_event"}]
    assert CASES["B-01"]["request"]["consumption"]["events"] == []


@pytest.mark.parametrize(
    "next_events,enabled", [("duplicate", True), ("empty", True), ("empty", False)]
)
def test_constant_create_consumed_or_untriggered_does_not_fail(next_events, enabled):
    req = bare([{"kind": "create", "object": "new"}])
    first = execute(req)
    req["state"] = first["candidate"]
    req["consumption"] = first["consumption"]
    req["behaviors"][0]["enabled"] = enabled
    if next_events == "empty":
        req["events"] = []
    second = execute(req)
    assert second["candidate"] == first["candidate"]
    assert second["consumption"] == first["consumption"]
    assert second["action_trace"] == []


def test_duplicate_id_different_content_rejects_entire_preparation():
    req = bare()
    req["events"] += [copy.deepcopy(req["events"][0])]
    req["events"][1]["version"] = "2"
    original = copy.deepcopy(req)
    with pytest.raises(BehaviorError, match="event_identity_conflict"):
        prepare_events(req)
    assert req == original


def test_same_duplicate_in_one_batch_applied_once():
    req = bare()
    req["events"] *= 2
    plan = execute(req)
    assert plan["event_trace"] == [
        {"event_id": "test-event", "reason": "event_applied"},
        {"event_id": "test-event", "reason": "duplicate_event"},
    ]
    assert len(plan["action_trace"]) == 1
    assert len(plan["consumption"]["events"]) == 1


def test_priority_then_behavior_then_event_sequence_then_event_id_and_internal_order():
    req = bare()
    req["events"] = [event("Z-first", 0), event("B-tied", 1), event("A-tied", 1)]
    req["behaviors"] = [
        definition("A-low", [{"kind": "notify", "message": "one"}], -1),
        definition(
            "Z-high",
            [{"kind": "notify", "message": "one"}, {"kind": "notify", "message": "two"}],
            5,
        ),
        definition("B-high", [{"kind": "notify", "message": "one"}], 5),
    ]
    result = execute(req)
    assert [
        (t["behavior_id"], t["event_id"], t["action_index"]) for t in result["action_trace"]
    ] == [
        ("B-high", "Z-first", 0),
        ("B-high", "A-tied", 0),
        ("B-high", "B-tied", 0),
        ("Z-high", "Z-first", 0),
        ("Z-high", "Z-first", 1),
        ("Z-high", "A-tied", 0),
        ("Z-high", "A-tied", 1),
        ("Z-high", "B-tied", 0),
        ("Z-high", "B-tied", 1),
        ("A-low", "Z-first", 0),
        ("A-low", "A-tied", 0),
        ("A-low", "B-tied", 0),
    ]
    # Storage order is irrelevant; caller sequences govern event order.
    req["events"].reverse()
    req["behaviors"].reverse()
    assert execute(req)["action_trace"] == result["action_trace"]


def test_event_stage_updates_are_not_competing_behavior_writes():
    req = bare([write("S2")])
    req["events"] = [event("later", 2), event("earlier", 1)]
    req["events"][0]["edits"] = [write("event-final")]
    req["events"][1]["edits"] = [write("event-first")]
    plan = execute(req)
    assert {
        f["value"]
        for f in plan["after_events"]["facts"]
        if f["subject"] == "W-test" and f["property"] == "status"
    } == {"event-final"}
    assert {
        f["value"]
        for f in plan["candidate"]["facts"]
        if f["subject"] == "W-test" and f["property"] == "status"
    } == {"S2"}


def test_internal_sequential_writes_allowed_but_any_peer_write_must_match_all_intents():
    req = bare([write("S1"), write("S2")])
    assert [t["action"]["value"] for t in execute(req)["action_trace"]] == ["S1", "S2"]
    req["behaviors"].append(definition("peer", [write("S2")]))
    with pytest.raises(BehaviorError, match="competing_write"):
        execute(req)


def test_multivalue_union_deduplicates_without_losing_other_actions():
    action = {"kind": "add", "subject": "001", "property": "rdf:type", "value": "TestObject"}
    req = bare([action, {"kind": "notify", "message": "one"}])
    req["behaviors"].append(
        definition(
            "peer", [action, {**action, "value": "WorkOrder"}, {"kind": "notify", "message": "two"}]
        )
    )
    plan = execute(req)
    assert [f for f in plan["candidate"]["facts"] if f["subject"] == "001"] == sorted(
        [
            {"subject": "001", "property": "rdf:type", "value": "Equipment"},
            {"subject": "001", "property": "rdf:type", "value": "TestObject"},
            {"subject": "001", "property": "rdf:type", "value": "WorkOrder"},
        ],
        key=lambda x: json.dumps(x, sort_keys=True),
    )
    assert [n["message"] for n in plan["candidate"]["notifications"]] == ["two", "one"]


def test_bool_and_integer_are_different_values_for_conditions_and_conflicts():
    req = bare()
    req["behaviors"][0]["conditions"] = [
        {"op": "has", "subject": "T1", "property": "P", "value": 0}
    ]
    assert execute(req)["decisions"][0]["reason"] == "condition_not_satisfied"
    req = bare([{"kind": "set", "subject": "T1", "property": "P", "value": False}])
    req["behaviors"].append(
        definition("peer", [{"kind": "set", "subject": "T1", "property": "P", "value": 0}])
    )
    with pytest.raises(BehaviorError, match="competing_write"):
        execute(req)


@pytest.mark.parametrize(
    "key", ["binding", "assertion_digest", "ontology_version", "rules_version", "status"]
)
def test_reasoning_must_match_exact_prepared_snapshot(key):
    prepared = prepare_events(bare())
    derived = reasoning(prepared)
    derived[key] = "other"
    with pytest.raises(BehaviorError, match="stale_reasoning"):
        plan_behaviors(prepared, derived)


def test_input_and_returned_values_are_detached():
    req = bare()
    prepared = prepare_events(req)
    binding = prepared.binding
    req["state"]["objects"].clear()
    doc = prepared.document
    doc["after_events"]["facts"].clear()
    plan = plan_behaviors(prepared, reasoning(prepared))
    plan["candidate"]["objects"].clear()
    assert prepared.binding == binding
    assert plan_behaviors(prepared, reasoning(prepared))["candidate"]["objects"]


@pytest.mark.parametrize("mode", ["formal", "production", "", None])
def test_formal_scope_cannot_be_planned(mode):
    req = bare()
    req["scope"]["mode"] = mode
    with pytest.raises(BehaviorError, match="formal_data_forbidden"):
        prepare_events(req)


def test_consumption_cannot_cross_scope():
    req = bare()
    req["consumption"]["scope"] = {**req["scope"], "scenario_id": "other"}
    with pytest.raises(BehaviorError, match="consumption_scope_mismatch"):
        prepare_events(req)


def test_failed_action_does_not_produce_or_mutate_candidate_or_ledger():
    req = bare([write("S1"), {"kind": "set", "subject": "unknown", "property": "P", "value": True}])
    old = copy.deepcopy(req)
    with pytest.raises(BehaviorError, match="invalid_object"):
        execute(req)
    assert req == old


@pytest.mark.parametrize("kind", ["shell", "http", "email", "sql", "emit_event", "delete_object"])
def test_unavailable_behavior_actions_are_rejected(kind):
    req = bare()
    req["behaviors"][0]["actions"] = [{"kind": kind}]
    with pytest.raises(BehaviorError, match="unavailable_action"):
        execute(req)


def test_create_can_be_referenced_in_instance_but_not_by_peer():
    actions = [
        {"kind": "create", "object": "new"},
        {"kind": "set", "subject": "new", "property": "status", "value": "S1"},
    ]
    req = bare(actions)
    assert "new" in execute(req)["candidate"]["objects"]
    req["behaviors"].append(
        definition("peer", [{"kind": "set", "subject": "new", "property": "status", "value": "S1"}])
    )
    with pytest.raises(BehaviorError, match="invalid_object"):
        execute(req)


def test_create_collision_is_a_failed_plan():
    req = bare([{"kind": "create", "object": "new"}])
    req["behaviors"].append(definition("peer", [{"kind": "create", "object": "new"}]))
    with pytest.raises(BehaviorError, match="duplicate_identity"):
        execute(req)


def test_actual_instance_action_count_limit_even_for_same_value():
    req = bare([write("S1")])
    req["events"] = [event(str(i), i) for i in range(1000)]
    assert len(execute(req)["action_trace"]) == 1000
    req["events"].append(event("last", 1000))
    with pytest.raises(BehaviorError, match="action_limit"):
        execute(req)


@pytest.mark.parametrize(
    "change,reason",
    [
        (
            lambda r: r["behaviors"].append(copy.deepcopy(r["behaviors"][0])),
            "duplicate_behavior_id",
        ),
        (lambda r: r["behaviors"][0].update(conditions=[]), "missing_condition"),
        (lambda r: r["behaviors"][0].update(actions=[]), "missing_action"),
        (lambda r: r["behaviors"][0].update(priority=True), "invalid_integer"),
        (lambda r: r["behaviors"][0].update(trigger={}), "missing_trigger"),
        (lambda r: r.update(round=1001), "round_limit"),
        (lambda r: r["events"][0].update(sequence=True), "invalid_integer"),
        (lambda r: r.update(extra=True), "invalid_shape"),
        (
            lambda r: r["behaviors"][0]["actions"][0].update(value={"eval": "code"}),
            "invalid_expression",
        ),
        (
            lambda r: r["behaviors"][0]["actions"][0].update(value={"event_field": "missing"}),
            "missing_event_field",
        ),
        (
            lambda r: r["behaviors"][0]["actions"][0].update(kind="add"),
            "cardinality_action_mismatch",
        ),
        (
            lambda r: r["state"]["facts"].append(copy.deepcopy(r["state"]["facts"][0])),
            "duplicate_fact",
        ),
    ],
)
def test_definition_and_event_validation(change, reason):
    req = bare()
    change(req)
    with pytest.raises(BehaviorError, match=reason):
        execute(req)


def test_disabled_behavior_is_recorded_without_execution():
    req = bare()
    req["behaviors"][0]["enabled"] = False
    result = execute(req)
    assert result["decisions"] == [
        {
            "event_id": "test-event",
            "behavior_id": "test",
            "assertion_version": "post-events-v1",
            "reasoning_version": "derived-v1",
            "conditions": [],
            "reason": "disabled",
        }
    ]
    assert result["action_trace"] == []
    assert result["consumption"]["instances"] == []


def test_notifications_from_earlier_round_are_preserved_and_scoped_ids_differ():
    req = bare([{"kind": "notify", "message": "one"}])
    first = execute(req)
    req["state"] = first["candidate"]
    req["consumption"] = first["consumption"]
    req["events"] = [event("next-event")]
    second = execute(req)
    assert second["candidate"]["notifications"][:1] == first["candidate"]["notifications"]
    assert [n["event_id"] for n in second["candidate"]["notifications"]] == [
        "test-event",
        "next-event",
    ]
    fresh = bare([{"kind": "notify", "message": "one"}])
    fresh["scope"]["scenario_id"] = "other"
    fresh["consumption"]["scope"] = copy.deepcopy(fresh["scope"])
    assert (
        execute(fresh)["candidate"]["notifications"][0]["id"]
        != first["candidate"]["notifications"][0]["id"]
    )


def test_constant_create_unmatched_event_has_no_side_effect():
    req = bare([{"kind": "create", "object": "new"}])
    first = execute(req)
    req["state"], req["consumption"] = first["candidate"], first["consumption"]
    req["events"] = [{**event("unmatched"), "type": "other"}]
    second = execute(req)
    assert second["candidate"] == first["candidate"]
    assert second["action_trace"] == []
    assert second["decisions"][0]["reason"] == "event_mismatch"


def test_new_event_constant_create_collision_still_rejected():
    req = bare([{"kind": "create", "object": "new"}])
    first = execute(req)
    req["state"], req["consumption"] = first["candidate"], first["consumption"]
    req["events"] = [event("new-matching-event")]
    with pytest.raises(BehaviorError, match="duplicate_identity"):
        execute(req)


def test_multivalue_add_has_complete_nonempty_diff():
    req = bare([{"kind": "add", "subject": "001", "property": "rdf:type", "value": "TestObject"}])
    assert execute(req)["diff"] == {
        "removed": [],
        "added": [["fact", {"subject": "001", "property": "rdf:type", "value": "TestObject"}]],
    }


@pytest.mark.parametrize("location", ["condition", "action"])
def test_static_invalid_property_rejected_without_matching_events(location):
    req = bare()
    req["events"] = []
    if location == "condition":
        req["behaviors"][0]["conditions"] = [
            {"op": "has", "subject": "T1", "property": "unknown", "value": True}
        ]
    else:
        req["behaviors"][0]["actions"][0]["property"] = "unknown"
    with pytest.raises(BehaviorError, match="invalid_property"):
        execute(req)
