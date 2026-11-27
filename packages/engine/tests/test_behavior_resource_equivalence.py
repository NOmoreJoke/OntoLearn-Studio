"""Observable ordering, complete results and isolation survive resource optimization."""

import copy
import json

import pytest
from ontolearn_engine.behavior import BehaviorError, plan_behaviors, prepare_events
from test_behavior_planner import bare, definition, event, execute, reasoning


def write(subject, value, prop="status", kind="set"):
    return {"kind": kind, "subject": subject, "property": prop, "value": value}


def request(groups):
    req = bare()
    req["state"] = {"objects": ["X", "Y", "Z"], "facts": [], "notifications": []}
    req["schema"] = {
        "status": {"kind": "literal", "cardinality": "one"},
        "tags": {"kind": "literal", "cardinality": "many"},
        "link": {"kind": "relation", "cardinality": "many"},
    }
    req["behaviors"] = [definition(identity, actions) for identity, actions in groups]
    return req


def conflict(req):
    original = copy.deepcopy(req)
    with pytest.raises(BehaviorError, match="competing_write") as caught:
        execute(req)
    error = caught.value
    assert error.location == "behavior.intents"
    assert error.evidence["stage"] == "conflict_check"
    assert error.evidence["executed_actions"] == []
    assert error.evidence["committed"] is False
    assert "candidate" not in error.evidence
    assert "consumption" not in error.evidence
    assert req == original
    return error.evidence


def test_first_conflict_uses_global_left_then_right_not_first_closed_slot():
    req = request(
        [
            ("A", [write("X", "x1"), write("Y", "y1")]),
            ("B", [write("Y", "y2")]),
            ("C", [write("X", "x2")]),
        ]
    )
    evidence = conflict(req)
    assert evidence["conflict_slot"] == {"subject": "X", "property": "status"}
    assert evidence["conflict"] == [evidence["intents"][0], evidence["intents"][3]]
    assert [d["behavior_id"] for d in evidence["decisions"]] == ["A", "B", "C"]
    assert [i["action"] for i in evidence["intents"]] == [
        write("X", "x1"),
        write("Y", "y1"),
        write("Y", "y2"),
        write("X", "x2"),
    ]


@pytest.mark.parametrize(
    ("values", "peer", "left_index"),
    [(["x", "x", "y"], "x", 2), (["x", "y"], "y", 0)],
)
def test_internal_overwrite_and_duplicate_writes_keep_earliest_actual_conflict(
    values, peer, left_index
):
    req = request([("A", [write("X", value) for value in values]), ("B", [write("X", peer)])])
    evidence = conflict(req)
    assert evidence["conflict"] == [
        evidence["intents"][left_index],
        evidence["intents"][-1],
    ]
    assert len(evidence["intents"]) == len(values) + 1


@pytest.mark.parametrize(("left", "right"), [(False, 0), (True, 1), (1, 1.0)])
def test_competition_preserves_json_types(left, right):
    evidence = conflict(request([("A", [write("X", left)]), ("B", [write("X", right)])]))
    actual = [json.dumps(i["action"]["value"]) for i in evidence["conflict"]]
    assert actual == [json.dumps(left), json.dumps(right)]


def test_compound_create_all_initial_writes_compete_and_remain_one_intent():
    create_a = {
        "kind": "create",
        "object": "NEW",
        "initial": [{"property": "status", "value": value} for value in ["x", "x", "y"]],
    }
    create_b = {
        "kind": "create",
        "object": "NEW",
        "initial": [{"property": "status", "value": "x"}],
    }
    evidence = conflict(request([("A", [create_a]), ("B", [create_b])]))
    assert evidence["conflict_slot"] == {"subject": "NEW", "property": "status"}
    assert (
        evidence["intents"]
        == evidence["conflict"]
        == [
            {"event_id": "test-event", "behavior_id": "A", "action_index": 0, "action": create_a},
            {"event_id": "test-event", "behavior_id": "B", "action_index": 0, "action": create_b},
        ]
    )


def test_typed_noops_have_exact_effect_and_full_sorted_state():
    actions = [
        write("X", 1),
        write("X", 1.0),
        write("X", False),
        write("X", False),
        write("X", False, "tags", "add"),
        write("X", 0, "tags", "add"),
        write("X", 0, "tags", "add"),
    ]
    req = request([("A", actions)])
    req["state"]["facts"] = [
        {"subject": "X", "property": "status", "value": 1},
        {"subject": "X", "property": "tags", "value": False},
    ]
    plan = execute(req)
    assert plan["action_trace"] == [
        {
            "event_id": "test-event",
            "behavior_id": "A",
            "action_index": index,
            "action": action,
            "effect": effect,
        }
        for index, (action, effect) in enumerate(
            zip(
                actions,
                [
                    "unchanged",
                    "changed",
                    "changed",
                    "unchanged",
                    "unchanged",
                    "changed",
                    "unchanged",
                ],
                strict=True,
            )
        )
    ]
    expected_facts = [
        {"subject": "X", "property": "status", "value": False},
        {"subject": "X", "property": "tags", "value": 0},
        {"subject": "X", "property": "tags", "value": False},
    ]
    assert json.dumps(plan["candidate"]["facts"], sort_keys=True) == json.dumps(
        expected_facts, sort_keys=True
    )
    assert plan["candidate"]["objects"] == ["X", "Y", "Z"]
    assert plan["candidate"]["notifications"] == []
    assert plan["diff"] == {
        "removed": [["fact", {"subject": "X", "property": "status", "value": 1}]],
        "added": [["fact", expected_facts[0]], ["fact", expected_facts[1]]],
    }


def test_ordered_initial_overwrite_preserves_trace_and_later_noop():
    create = {
        "kind": "create",
        "object": "NEW",
        "initial": [
            {"property": "status", "value": "FIRST"},
            {"property": "status", "value": "SECOND"},
        ],
    }
    req = request([("A", [create, write("NEW", "SECOND")])])
    plan = execute(req)
    assert plan["candidate"] == {
        "objects": ["NEW", "X", "Y", "Z"],
        "facts": [{"subject": "NEW", "property": "status", "value": "SECOND"}],
        "notifications": [],
    }
    assert [t["effect"] for t in plan["action_trace"]] == ["changed", "unchanged"]
    assert plan["action_trace"][0]["action"] == create


def test_event_delete_removes_outgoing_and_relation_incoming_before_redeclare():
    req = request([("A", [{"kind": "notify", "message": "done"}])])
    req["state"]["facts"] = [
        {"subject": "X", "property": "link", "value": "Y"},
        {"subject": "Y", "property": "link", "value": "Z"},
        {"subject": "Z", "property": "link", "value": "Y"},
        {"subject": "Y", "property": "tags", "value": "old"},
    ]
    req["events"][0]["edits"] = [
        {"kind": "delete_object", "object": "Y"},
        {"kind": "declare", "object": "Y"},
        {"kind": "declare", "object": "Y"},
        write("Y", "new"),
        write("X", "Y", "link", "add"),
    ]
    expected = {
        "objects": ["X", "Y", "Z"],
        "facts": [
            {"subject": "X", "property": "link", "value": "Y"},
            {"subject": "Y", "property": "status", "value": "new"},
        ],
        "notifications": [],
    }
    plan = execute(req)
    assert plan["after_events"] == expected
    assert plan["frozen"] == expected
    assert plan["candidate"]["facts"] == expected["facts"]
    assert plan["event_trace"] == [{"event_id": "test-event", "reason": "event_applied"}]


@pytest.mark.parametrize("identity", [{}, [], False, 0, None])
def test_invalid_delete_identity_keeps_domain_error_not_hash_type_error(identity):
    req = request([("A", [write("X", "new")])])
    req["events"][0]["edits"] = [{"kind": "delete_object", "object": identity}]
    original = copy.deepcopy(req)
    with pytest.raises(BehaviorError, match="invalid_object") as caught:
        execute(req)
    assert caught.value.location == "edit.object"
    assert caught.value.evidence == {
        "stage": "event_preparation",
        "event_index": 0,
        "event_sequence": 0,
        "event_id": "test-event",
        "edit_index": 0,
        "event_trace": [],
        "discarded_event_edits": [],
        "committed": False,
    }
    assert req == original


def test_complete_decision_matrix_and_result_containers_are_independent():
    req = request(
        [(identity, [{"kind": "notify", "message": identity}]) for identity in ["A", "B", "C", "D"]]
    )
    req["state"]["facts"] = [{"subject": "X", "property": "status", "value": "on"}]
    req["behaviors"][1]["enabled"] = False
    req["behaviors"][2]["trigger"] = {"event_type": "never"}
    req["behaviors"][3]["conditions"] = [
        {"op": "has", "subject": "X", "property": "status", "value": "off"}
    ]
    req["events"] = [event("E2", 2), event("E0", 0), event("E1", 1)]
    original = copy.deepcopy(req)
    prepared = prepare_events(req)
    plan = plan_behaviors(prepared, reasoning(prepared))
    expected = []
    for identity, reason, conditions in [
        ("A", "triggered", [{"index": 0, "satisfied": True, "reason": "explicit_always"}]),
        ("B", "disabled", []),
        ("C", "event_mismatch", []),
        (
            "D",
            "condition_not_satisfied",
            [{"index": 0, "satisfied": False, "reason": "not_recorded_in_snapshot"}],
        ),
    ]:
        for ev in ["E0", "E1", "E2"]:
            expected.append(
                {
                    "event_id": ev,
                    "behavior_id": identity,
                    "assertion_version": "post-events-v1",
                    "reasoning_version": "derived-v1",
                    "conditions": copy.deepcopy(conditions),
                    "reason": reason,
                }
            )
    assert plan["decisions"] == expected
    assert [(t["behavior_id"], t["event_id"]) for t in plan["action_trace"]] == [
        ("A", "E0"),
        ("A", "E1"),
        ("A", "E2"),
    ]
    plan["decisions"][3]["conditions"].append({"local": "mutation"})
    assert plan["decisions"][4]["conditions"] == []
    assert plan["decisions"][6]["conditions"] == []
    plan["decisions"][0]["conditions"][0]["reason"] = "local"
    assert plan["decisions"][1]["conditions"][0]["reason"] == "explicit_always"
    plan["before"]["facts"][0]["value"] = "local"
    assert plan["after_events"]["facts"][0]["value"] == "on"
    plan["candidate"]["facts"][0]["value"] = "local"
    assert plan["frozen"]["facts"][0]["value"] == "on"
    assert prepared.document["after_events"]["facts"][0]["value"] == "on"
    assert req == original


def test_candidate_failure_keeps_discarded_notification_prefix_and_no_partial_state():
    actions = [
        {"kind": "notify", "id": "N", "message": "first"},
        {"kind": "create", "object": "N"},
    ]
    req = request([("A", actions)])
    original = copy.deepcopy(req)
    with pytest.raises(BehaviorError, match="duplicate_identity") as caught:
        execute(req)
    error = caught.value
    assert error.location == "edit.object"
    assert error.evidence["stage"] == "candidate_simulation"
    assert error.evidence["action_index"] == 1
    assert error.evidence["discarded_actions"] == [
        {
            "event_id": "test-event",
            "behavior_id": "A",
            "action_index": 0,
            "action": actions[0],
            "notification_id": "N",
            "effect": "changed",
        }
    ]
    assert error.evidence["executed_actions"] == []
    assert error.evidence["committed"] is False
    assert "candidate" not in error.evidence
    assert "consumption" not in error.evidence
    assert req == original
