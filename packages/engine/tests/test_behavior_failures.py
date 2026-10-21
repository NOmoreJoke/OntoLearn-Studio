"""Failure explanations must identify attempted work without publishing a candidate."""

import copy
import json
from pathlib import Path

import pytest
from ontolearn_engine.behavior import BehaviorError, plan_behaviors, prepare_events

CORPUS = json.loads(
    (Path(__file__).parents[3] / "tests/fixtures/behavior/counterexamples.json").read_text()
)


def write(value, subject="W-test"):
    return {"kind": "set", "subject": subject, "property": "status", "value": value}


def request(actions=None):
    req = copy.deepcopy(CORPUS["cases"][0]["request"])
    req["events"] = [
        {"id": "E1", "type": "test", "sequence": 0, "version": "1", "payload": {}, "edits": []}
    ]
    req["behaviors"] = [
        {
            "id": "A",
            "name": "A",
            "description": "Failure explanation",
            "effect": "Internal",
            "version": "1",
            "enabled": True,
            "priority": 0,
            "trigger": {"event_type": "test"},
            "conditions": [{"op": "always"}],
            "actions": actions or [write("S1")],
        }
    ]
    return req


def run(req):
    prepared = prepare_events(req)
    derived = prepared.reasoning_input
    derived.pop("state")
    return plan_behaviors(
        prepared, {**derived, "version": "derived-1", "status": "current", "facts": []}
    )


def decision(behavior="A"):
    return {
        "event_id": "E1",
        "behavior_id": behavior,
        "assertion_version": "post-events-v1",
        "reasoning_version": "derived-1",
        "conditions": [{"index": 0, "satisfied": True, "reason": "explicit_always"}],
        "reason": "triggered",
    }


def failed(req, reason):
    before = copy.deepcopy(req)
    with pytest.raises(BehaviorError, match=reason) as caught:
        run(req)
    assert req == before  # includes the actual original state and consumption ledger
    evidence = caught.value.evidence
    assert evidence["committed"] is False
    assert "candidate" not in evidence
    assert "consumption" not in evidence
    # Structural exception text cannot contain domain values or payloads.
    assert str(caught.value) == f"{caught.value.reason}: {caught.value.location}"
    return evidence


def test_event_edit_failure_retains_discarded_prefix_and_source_position():
    req = request()
    req["events"][0]["edits"] = [write("event-one")]
    req["events"].append(
        {
            **copy.deepcopy(req["events"][0]),
            "id": "E2",
            "sequence": 1,
            "edits": [write("event-two"), write("private-value", "unknown")],
        }
    )
    evidence = failed(req, "invalid_object")
    assert evidence == {
        "stage": "event_preparation",
        "event_index": 1,
        "event_sequence": 1,
        "event_id": "E2",
        "edit_index": 1,
        "event_trace": [{"event_id": "E1", "reason": "event_applied"}],
        "discarded_event_edits": [
            {"event_id": "E1", "edit_index": 0},
            {"event_id": "E2", "edit_index": 0},
        ],
        "committed": False,
    }


def test_event_identity_conflict_retains_prefix_without_returning_state():
    req = request()
    req["events"][0]["edits"] = [write("event-one")]
    req["events"].append({**copy.deepcopy(req["events"][0]), "sequence": 1, "version": "2"})
    assert failed(req, "event_identity_conflict") == {
        "stage": "event_preparation",
        "event_index": 1,
        "event_sequence": 1,
        "event_id": "E1",
        "event_trace": [{"event_id": "E1", "reason": "event_applied"}],
        "discarded_event_edits": [{"event_id": "E1", "edit_index": 0}],
        "committed": False,
    }


def test_condition_failure_distinguishes_completed_and_partial_decisions():
    req = request()
    peer = {**copy.deepcopy(req["behaviors"][0]), "id": "B"}
    peer["conditions"].append(
        {"op": "has", "subject": {"event_field": "missing"}, "property": "status", "value": "Open"}
    )
    req["behaviors"].append(peer)
    evidence = failed(req, "missing_event_field")
    assert evidence["stage"] == "condition_evaluation"
    assert (evidence["event_id"], evidence["behavior_id"], evidence["condition_index"]) == (
        "E1",
        "B",
        1,
    )
    assert evidence["decisions"] == [decision()]
    assert evidence["partial_decision"] == {
        "event_id": "E1",
        "behavior_id": "B",
        "assertion_version": "post-events-v1",
        "reasoning_version": "derived-1",
        "conditions": [{"index": 0, "satisfied": True, "reason": "explicit_always"}],
    }
    assert evidence["executed_actions"] == []
    assert "intents" not in evidence


def test_invalid_dynamic_action_has_exact_instance_and_resolved_prefix():
    req = request([write("S1"), write("private-value", {"event_field": "target"})])
    req["events"][0]["payload"] = {"target": "not-an-object"}
    prepared = prepare_events(req)
    evidence = failed(req, "invalid_object")
    assert evidence == {
        "scope": req["scope"],
        "run_id": req["run_id"],
        "round": 1,
        "binding": prepared.binding,
        "assertion_version": "post-events-v1",
        "reasoning_version": "derived-1",
        "behavior_version": "behaviors-v1",
        "committed": False,
        "executed_actions": [],
        "stage": "intent_validation",
        "event_id": "E1",
        "behavior_id": "A",
        "action_index": 1,
        "event_trace": [{"event_id": "E1", "reason": "event_applied"}],
        "decisions": [decision()],
        "intents": [
            {"event_id": "E1", "behavior_id": "A", "action_index": 0, "action": write("S1")}
        ],
    }


def test_candidate_collision_marks_earlier_actions_discarded_and_never_executed():
    req = request([{"kind": "notify", "message": "one"}, {"kind": "create", "object": "fixed"}])
    req["behaviors"].append({**copy.deepcopy(req["behaviors"][0]), "id": "B"})
    evidence = failed(req, "duplicate_identity")
    assert evidence["stage"] == "candidate_simulation"
    assert (evidence["event_id"], evidence["behavior_id"], evidence["action_index"]) == (
        "E1",
        "B",
        1,
    )
    assert evidence["decisions"] == [decision("A"), decision("B")]
    assert [
        (i["behavior_id"], i["action_index"], i["action"]["kind"]) for i in evidence["intents"]
    ] == [("A", 0, "notify"), ("A", 1, "create"), ("B", 0, "notify"), ("B", 1, "create")]
    assert evidence["discarded_actions"] == [
        {**intent, "effect": "changed"} for intent in evidence["intents"][:3]
    ]
    assert evidence["executed_actions"] == []


def test_limit_explanation_counts_all_instance_actions_even_if_same_value():
    req = request([write("S1")] * 1001)
    evidence = failed(req, "action_limit")
    assert evidence["stage"] == "intent_limit"
    assert evidence["action_count"] == 1001
    assert evidence["action_limit"] == 1000
    assert evidence["decisions"] == [decision()]
    assert evidence["executed_actions"] == []
    assert "intents" not in evidence


def test_static_error_names_definition_and_action_without_claiming_event_failure():
    req = request([write("S1"), write("private-value", "unknown")])
    assert failed(req, "invalid_object") == {
        "stage": "definition_validation",
        "behavior_id": "A",
        "action_index": 1,
        "committed": False,
    }


def test_missing_definition_condition_retains_list_index_and_identity():
    req = request()
    req["behaviors"][0]["conditions"] = []
    assert failed(req, "missing_condition") == {
        "stage": "definition_validation",
        "behavior_index": 0,
        "behavior_id": "A",
        "committed": False,
    }


@pytest.mark.parametrize("target", ["event_id", "payload", "action"])
def test_unpaired_unicode_surrogate_is_structurally_rejected(target):
    req = request()
    if target == "event_id":
        req["events"][0]["id"] = "\ud800"
    elif target == "payload":
        req["events"][0]["payload"] = {"text": "\udc00"}
    else:
        req["behaviors"][0]["actions"][0]["value"] = "\ud800"
    with pytest.raises(BehaviorError, match="invalid_json: input"):
        prepare_events(req)


@pytest.mark.parametrize("target", ["condition", "action"])
def test_invalid_template_retains_definition_and_template_positions(target):
    req = request()
    if target == "condition":
        req["behaviors"][0]["conditions"].append(
            {"op": "eval", "subject": "T1", "property": "P", "value": True}
        )
        reason = "unavailable_condition"
    else:
        req["behaviors"][0]["actions"].append({"kind": "http", "value": "private-value"})
        reason = "unavailable_action"
    assert failed(req, reason) == {
        "stage": "definition_validation",
        "behavior_index": 0,
        "behavior_id": "A",
        target + "_index": 1,
        "committed": False,
    }


@pytest.mark.parametrize(
    "field,value,reason,include_sequence",
    [
        ("sequence", True, "invalid_integer", False),
        ("payload", [], "invalid_shape", True),
        ("payload", {"value": None}, "invalid_scalar", True),
        ("extra", "private-value", "invalid_shape", True),
        ("type", "", "invalid_text", True),
        ("edits", {}, "invalid_list", True),
    ],
)
def test_event_header_or_payload_error_has_original_source_position(
    field, value, reason, include_sequence
):
    req = request()
    second = {**copy.deepcopy(req["events"][0]), "id": "E2", "sequence": 5}
    second[field] = value
    req["events"].append(second)
    expected = {"stage": "event_validation", "committed": False, "event_index": 1, "event_id": "E2"}
    if include_sequence:
        expected["event_sequence"] = 5
    assert failed(req, reason) == expected


def test_edit_failure_source_position_is_not_sorted_execution_position():
    req = request()
    req["events"] = [
        {
            **copy.deepcopy(req["events"][0]),
            "id": "E2",
            "sequence": 10,
            "edits": [write("bad", "unknown")],
        },
        {**copy.deepcopy(req["events"][0]), "sequence": 0, "edits": [write("good")]},
    ]
    assert failed(req, "invalid_object") == {
        "stage": "event_preparation",
        "event_id": "E2",
        "event_index": 0,
        "event_sequence": 10,
        "edit_index": 0,
        "event_trace": [{"event_id": "E1", "reason": "event_applied"}],
        "discarded_event_edits": [{"event_id": "E1", "edit_index": 0}],
        "committed": False,
    }


def test_duplicate_conflict_points_to_original_source_position_after_sort():
    req = request()
    req["events"] = [
        {**copy.deepcopy(req["events"][0]), "sequence": 10, "version": "2"},
        {**copy.deepcopy(req["events"][0]), "sequence": 0},
    ]
    assert failed(req, "event_identity_conflict") == {
        "stage": "event_preparation",
        "event_id": "E1",
        "event_index": 0,
        "event_sequence": 10,
        "event_trace": [{"event_id": "E1", "reason": "event_applied"}],
        "discarded_event_edits": [],
        "committed": False,
    }


def test_invalid_event_identity_is_not_in_failure_metadata_as_validated():
    req = request()
    req["events"][0]["id"] = []
    assert failed(req, "invalid_text") == {
        "stage": "event_validation",
        "event_index": 0,
        "event_sequence": 0,
        "committed": False,
    }
