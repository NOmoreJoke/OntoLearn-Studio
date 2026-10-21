"""Native create and stable identifiers preserve declared behavior action counts."""

import copy

import pytest
from ontolearn_engine.behavior import BehaviorError
from test_behavior_planner import bare, definition, event, execute


def create(identity="new", status="S1"):
    return {
        "kind": "create",
        "object": identity,
        "initial": [
            {"property": "rdf:type", "value": "WorkOrder"},
            {"property": "status", "value": status},
        ],
    }


def test_create_initial_fields_are_one_action_with_full_state():
    req = bare([create()])
    original = copy.deepcopy(req["state"])
    plan = execute(req)
    expected = copy.deepcopy(original)
    expected["objects"] = sorted([*expected["objects"], "new"])
    expected["facts"] += [
        {"subject": "new", "property": "rdf:type", "value": "WorkOrder"},
        {"subject": "new", "property": "status", "value": "S1"},
    ]
    assert {tuple(sorted(f.items())) for f in plan["candidate"]["facts"]} == {
        tuple(sorted(f.items())) for f in expected["facts"]
    }
    assert plan["candidate"]["objects"] == expected["objects"]
    assert plan["action_trace"] == [
        {
            "event_id": "test-event",
            "behavior_id": "test",
            "action_index": 0,
            "action": create(),
            "effect": "changed",
        }
    ]
    assert req["state"] == original


def test_create_fields_count_once_rather_than_as_expanded_primitive_actions():
    req = bare([create({"event_template": "W:{eventId}"})])
    req["events"] = [event(str(i), i) for i in range(501)]
    plan = execute(req)
    assert [t["action_index"] for t in plan["action_trace"]] == [0] * 501
    assert [t["action"]["object"] for t in plan["action_trace"]] == [f"W:{i}" for i in range(501)]
    assert len(plan["candidate"]["facts"]) == len(req["state"]["facts"]) + 1002
    req["events"] = [event(str(i), i) for i in range(1001)]
    with pytest.raises(BehaviorError, match="action_limit"):
        execute(req)


def test_create_initial_values_participate_in_cross_instance_competition():
    req = bare([create(status="S1")])
    req["behaviors"].append(definition("peer", [create(status="S2")]))
    with pytest.raises(BehaviorError, match="competing_write") as error:
        execute(req)
    assert error.value.evidence["conflict_slot"] == {"subject": "new", "property": "status"}
    assert [i["action"]["initial"][1]["value"] for i in error.value.evidence["conflict"]] == [
        "S2",
        "S1",  # peer sorts before test
    ]
    assert error.value.evidence["executed_actions"] == []


def test_constant_initialized_create_remains_noop_after_consumption():
    req = bare([create()])
    first = execute(req)
    req["state"], req["consumption"] = first["candidate"], first["consumption"]
    second = execute(req)
    assert second["candidate"] == first["candidate"]
    assert second["consumption"] == first["consumption"]
    assert second["action_trace"] == []


def test_create_field_failure_preserves_initial_index_and_input():
    req = bare([create()])
    req["behaviors"][0]["actions"][0]["initial"][1]["property"] = "unknown"
    original = copy.deepcopy(req)
    with pytest.raises(BehaviorError, match="invalid_property") as error:
        execute(req)
    assert error.value.evidence == {
        "stage": "definition_validation",
        "behavior_id": "test",
        "action_index": 0,
        "initial_index": 1,
        "committed": False,
    }
    assert req == original


def test_event_templates_do_not_reinterpret_inserted_identifier_text():
    req = bare(
        [{"kind": "notify", "message": "one", "id": {"event_template": "N:{eventId}:{behaviorId}"}}]
    )
    req["events"][0]["id"] = "{behaviorId}"
    plan = execute(req)
    assert plan["candidate"]["notifications"][0]["id"] == "N:{behaviorId}:test"


@pytest.mark.parametrize("template", ["{eventId.__class__}", "{payload.value}", "{eventId", "x}"])
def test_arbitrary_template_paths_are_rejected(template):
    req = bare([create({"event_template": template})])
    with pytest.raises(BehaviorError, match="invalid_expression"):
        execute(req)


def test_declaration_is_idempotent_event_input_and_unavailable_as_behavior():
    req = bare([{"kind": "notify", "message": "one"}])
    req["events"] = [event("E1", 0), event("E2", 1)]
    for ev in req["events"]:
        ev["edits"] = [{"kind": "declare", "object": "declared"}]
    plan = execute(req)
    assert plan["candidate"]["objects"].count("declared") == 1
    assert [n["event_id"] for n in plan["candidate"]["notifications"]] == ["E1", "E2"]
    req["behaviors"][0]["actions"] = [{"kind": "declare", "object": "declared"}]
    with pytest.raises(BehaviorError, match="unavailable_action"):
        execute(req)
