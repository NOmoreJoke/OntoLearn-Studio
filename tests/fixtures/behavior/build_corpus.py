"""Author pure-algorithm counterexamples from PRD; never imports the planner.

This is T06 private corpus, not T09's G.0 or proof of a real reasoner/round.
Generated expectations are explicit scenario facts, decisions and action order.
"""

import copy
import hashlib
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def fact(subject, prop, value):
    return {"subject": subject, "property": prop, "value": value}


def edit(kind, subject, prop, value):
    return {"kind": kind, **fact(subject, prop, value)}


def field(name):
    return {"event_field": name}


def condition(subject, prop, value):
    return {"op": "has", **fact(subject, prop, value)}


def behavior(identity, trigger, actions, conditions=None):
    return {
        "id": identity,
        "name": identity,
        "description": "PRD G.3 私有算法反例",
        "effect": "内部状态计划",
        "version": "1",
        "enabled": True,
        "priority": 0,
        "trigger": trigger,
        "conditions": conditions or [{"op": "always"}],
        "actions": actions,
    }


def event(identity, kind, sequence=0, payload=None, edits=None):
    return {
        "id": identity,
        "type": kind,
        "sequence": sequence,
        "version": "1",
        "payload": payload or {},
        "edits": edits or [],
    }


scope = {"project_id": "private-fixture", "scenario_id": "case", "mode": "sample"}
base = {
    "objects": ["001", "002", "003", "A01", "A02", "A03", "T1", "W-other", "W-test"],
    "facts": [
        fact("001", "rdf:type", "Equipment"),
        fact("002", "rdf:type", "Equipment"),
        fact("003", "rdf:type", "Equipment"),
        fact("A01", "equipment", "001"),
        fact("A01", "level", "High"),
        fact("A01", "status", "Open"),
        fact("A02", "equipment", "002"),
        fact("A02", "level", "High"),
        fact("A02", "status", "Closed"),
        fact("A03", "equipment", "003"),
        fact("A03", "level", "Low"),
        fact("A03", "status", "Open"),
        fact("T1", "rdf:type", "TestObject"),
        fact("T1", "P", False),
        fact("W-test", "rdf:type", "WorkOrder"),
        fact("W-test", "status", "待处理"),
        fact("W-other", "rdf:type", "WorkOrder"),
        fact("W-other", "status", "待处理"),
    ],
    "notifications": [],
}
notify = {"kind": "notify", "message": "通知"}
behaviors = [
    behavior("B-a", {"event_type": "工单竞争触发"}, [edit("set", "W-test", "status", "S-a")]),
    behavior("B-b", {"event_type": "工单竞争触发"}, [edit("set", "W-test", "status", "S-b")]),
    behavior(
        "B-multi",
        {"event_type": "多目标触发"},
        [edit("set", field("target"), "status", field("value")), notify],
    ),
    behavior(
        "B-probe",
        {"event_id": "E-probe"},
        [notify],
        [condition("001", "rdf:type", "HighRiskEquipment")],
    ),
    behavior(
        "B-risk",
        {"event_type": "new_alarm"},
        [
            {"kind": "create", "object": {"instance_id": "W"}},
            edit("add", {"instance_id": "W"}, "rdf:type", "WorkOrder"),
            edit("set", {"instance_id": "W"}, "status", "待处理"),
            edit("set", {"instance_id": "W"}, "eventId", {"event_id": True}),
        ],
        [
            condition(field("alarm"), "level", "High"),
            condition(field("alarm"), "status", "Open"),
            condition(field("equipment"), "rdf:type", "HighRiskEquipment"),
        ],
    ),
    behavior("X", {"event_id": "E-B06"}, [edit("set", "T1", "P", True)]),
    behavior("Y", {"event_id": "E-B06"}, [notify], [condition("T1", "P", False)]),
]
request = {
    "scope": scope,
    "run_id": "run-1",
    "round": 1,
    "base_revision": "revision-1",
    "assertion_version": "post-events-v1",
    "ontology_version": "ontology-v1",
    "rules_version": "rules-v1",
    "behavior_version": "behaviors-v1",
    "classes": ["Equipment", "HighRiskEquipment", "TestObject", "WorkOrder"],
    "schema": {
        "rdf:type": {"kind": "class", "cardinality": "many"},
        "equipment": {"kind": "relation", "cardinality": "one"},
        **{
            p: {"kind": "literal", "cardinality": "one"}
            for p in ["level", "status", "P", "eventId"]
        },
    },
    "state": base,
    "events": [],
    "consumption": {"scope": scope, "events": [], "instances": []},
    "behaviors": behaviors,
}


def normalized(state):
    state["objects"].sort()
    state["facts"].sort(key=canonical)
    return state


def changed(state, subject, prop, value):
    state["facts"] = [f for f in state["facts"] if (f["subject"], f["property"]) != (subject, prop)]
    state["facts"].append(fact(subject, prop, value))


def notification(event_id, behavior_id, index):
    return {
        "id": "notification:" + digest([scope, event_id, behavior_id, index]),
        "event_id": event_id,
        "behavior_id": behavior_id,
        "action_index": index,
        "message": "通知",
    }


def alarm(identity, alarm_id, equipment, level):
    return event(
        identity,
        "new_alarm",
        payload={"alarm": alarm_id, "equipment": equipment},
        edits=[
            {"kind": "create", "object": alarm_id},
            edit("set", alarm_id, "equipment", equipment),
            edit("set", alarm_id, "level", level),
            edit("set", alarm_id, "status", "Open"),
        ],
    )


cases = []
for identity in ["B-01", "B-02", "B-03", "B-04", "B-05", "B-06", "B-09", "B-10", "B-11"]:
    req = copy.deepcopy(request)
    req["scope"]["scenario_id"] = identity
    # scope object aliases are intentional only in this authoring script.
    # Expected action IDs below use this exact case scope.
    scope = req["scope"]
    req["consumption"]["scope"] = copy.deepcopy(scope)
    triggered = []
    false_conditions = {}
    error = None
    if identity in ("B-01", "B-03"):
        alarm_id = "A04" if identity == "B-01" else "A06"
        req["events"] = [alarm("E-" + identity.replace("-", ""), alarm_id, "001", "High")]
        triggered = [(req["events"][0]["id"], "B-risk")]
    elif identity == "B-02":
        req["events"] = [alarm("E-B02", "A05", "003", "Low")]
        false_conditions[("E-B02", "B-risk")] = [False, True, False]
    elif identity == "B-04":
        req["events"] = [
            event("E-probe", "probe", 1),
            event("E-del", "delete", 0, edits=[{"kind": "delete_object", "object": "A01"}]),
        ]
        false_conditions[("E-probe", "B-probe")] = [False]
    elif identity == "B-05":
        req["events"] = [event("E-B05", "工单竞争触发")]
        triggered = [("E-B05", "B-a"), ("E-B05", "B-b")]
        error = "competing_write"
    elif identity == "B-06":
        req["events"] = [event("E-B06", "freeze")]
        triggered = [("E-B06", "X"), ("E-B06", "Y")]
    elif identity == "B-09":
        req["events"] = [
            event("E-M1", "多目标触发", 0, {"target": "W-test", "value": "S1"}),
            event("E-M2", "多目标触发", 1, {"target": "W-test", "value": "S2"}),
        ]
        triggered = [("E-M1", "B-multi"), ("E-M2", "B-multi")]
        error = "competing_write"
    elif identity == "B-10":
        req["events"] = [
            event("E-M4", "多目标触发", 0, {"target": "W-other", "value": "S4"}),
            event("E-M3", "多目标触发", 1, {"target": "W-test", "value": "S3"}),
        ]
        triggered = [("E-M4", "B-multi"), ("E-M3", "B-multi")]
    elif identity == "B-11":
        req["events"] = [
            event("E-M5", "多目标触发", 0, {"target": "W-test", "value": "S1"}),
            event("E-M6", "多目标触发", 1, {"target": "W-test", "value": "S1"}),
        ]
        triggered = [("E-M5", "B-multi"), ("E-M6", "B-multi")]
    if identity == "B-03":
        req["state"]["objects"].remove("A01")
        req["state"]["facts"] = [f for f in req["state"]["facts"] if f["subject"] != "A01"]
    normalized(req["state"])
    # Explicit event effects for these fixtures, not a general event interpreter.
    after_events = copy.deepcopy(req["state"])
    if identity in ("B-01", "B-02", "B-03"):
        ev = req["events"][0]
        after_events["objects"].append(ev["payload"]["alarm"])
        after_events["facts"].extend(
            {k: e[k] for k in ("subject", "property", "value")} for e in ev["edits"][1:]
        )
    if identity == "B-04":
        after_events["objects"].remove("A01")
        after_events["facts"] = [f for f in after_events["facts"] if f["subject"] != "A01"]
    normalized(after_events)
    derived = [] if identity == "B-04" else [fact("001", "rdf:type", "HighRiskEquipment")]
    frozen = copy.deepcopy(after_events)
    frozen["facts"].extend(derived)
    normalized(frozen)
    candidate = copy.deepcopy(after_events)
    trace = []
    if identity in ("B-01", "B-03"):
        ev_id = req["events"][0]["id"]
        work_id = "W:" + digest([scope, ev_id, "B-risk"])
        candidate["objects"].append(work_id)
        candidate["facts"].extend(
            [
                fact(work_id, "rdf:type", "WorkOrder"),
                fact(work_id, "status", "待处理"),
                fact(work_id, "eventId", ev_id),
            ]
        )
        actions = [
            {"kind": "create", "object": work_id},
            edit("add", work_id, "rdf:type", "WorkOrder"),
            edit("set", work_id, "status", "待处理"),
            edit("set", work_id, "eventId", ev_id),
        ]
        trace = [
            {
                "event_id": ev_id,
                "behavior_id": "B-risk",
                "action_index": i,
                "action": action,
                "effect": "changed",
            }
            for i, action in enumerate(actions)
        ]
    elif identity == "B-06":
        changed(candidate, "T1", "P", True)
        record = notification("E-B06", "Y", 0)
        candidate["notifications"] = [record]
        trace = [
            {
                "event_id": "E-B06",
                "behavior_id": "X",
                "action_index": 0,
                "action": edit("set", "T1", "P", True),
                "effect": "changed",
            },
            {
                "event_id": "E-B06",
                "behavior_id": "Y",
                "action_index": 0,
                "action": notify,
                "notification_id": record["id"],
                "effect": "changed",
            },
        ]
    elif identity in ("B-10", "B-11"):
        for i, ev in enumerate(req["events"]):
            payload = ev["payload"]
            changed(candidate, payload["target"], "status", payload["value"])
            record = notification(ev["id"], "B-multi", 1)
            candidate["notifications"].append(record)
            trace.extend(
                [
                    {
                        "event_id": ev["id"],
                        "behavior_id": "B-multi",
                        "action_index": 0,
                        "action": edit("set", payload["target"], "status", payload["value"]),
                        "effect": "unchanged" if identity == "B-11" and i == 1 else "changed",
                    },
                    {
                        "event_id": ev["id"],
                        "behavior_id": "B-multi",
                        "action_index": 1,
                        "action": notify,
                        "notification_id": record["id"],
                        "effect": "changed",
                    },
                ]
            )
    normalized(candidate)
    decisions = []
    for bid in ["B-a", "B-b", "B-multi", "B-probe", "B-risk", "X", "Y"]:
        for ev in sorted(req["events"], key=lambda e: (e["sequence"], e["id"])):
            key = (ev["id"], bid)
            checks = []
            if key in triggered:
                checks = [True] * (3 if bid == "B-risk" else 1)
                reason = "triggered"
            elif key in false_conditions:
                checks = false_conditions[key]
                reason = "condition_not_satisfied"
            else:
                reason = "event_mismatch"
            decisions.append(
                {
                    "event_id": ev["id"],
                    "behavior_id": bid,
                    "assertion_version": "post-events-v1",
                    "reasoning_version": "derived-v1",
                    "reason": reason,
                    "conditions": [
                        {
                            "index": i,
                            "satisfied": yes,
                            "reason": (
                                "not_recorded_in_snapshot"
                                if not yes
                                else "frozen_snapshot"
                                if bid in ("B-risk", "B-probe", "Y")
                                else "explicit_always"
                            ),
                        }
                        for i, yes in enumerate(checks)
                    ],
                }
            )
    failed_intents = []
    if identity == "B-05":
        failed_intents = [
            {
                "event_id": "E-B05",
                "behavior_id": "B-a",
                "action_index": 0,
                "action": edit("set", "W-test", "status", "S-a"),
            },
            {
                "event_id": "E-B05",
                "behavior_id": "B-b",
                "action_index": 0,
                "action": edit("set", "W-test", "status", "S-b"),
            },
        ]
    elif identity == "B-09":
        for ev in req["events"]:
            record = notification(ev["id"], "B-multi", 1)
            failed_intents.extend(
                [
                    {
                        "event_id": ev["id"],
                        "behavior_id": "B-multi",
                        "action_index": 0,
                        "action": edit("set", "W-test", "status", ev["payload"]["value"]),
                    },
                    {
                        "event_id": ev["id"],
                        "behavior_id": "B-multi",
                        "action_index": 1,
                        "action": notify,
                        "notification_id": record["id"],
                    },
                ]
            )

    def state_items(state):
        return (
            {canonical(["object", obj]) for obj in state["objects"]}
            | {canonical(["fact", f]) for f in state["facts"]}
            | {canonical(["notification", n]) for n in state["notifications"]}
        )

    added = state_items(candidate) - state_items(req["state"])
    removed = state_items(req["state"]) - state_items(candidate)
    diff = {
        "added": [json.loads(x) for x in sorted(added)],
        "removed": [json.loads(x) for x in sorted(removed)],
    }

    cases.append(
        {
            "id": identity,
            "request": req,
            "reasoning_facts": derived,
            "expected": {
                "error": error,
                "failed_intents": failed_intents,
                "conflict": (
                    [failed_intents[0], failed_intents[1 if identity == "B-05" else 2]]
                    if error
                    else []
                ),
                "diff": None if error else diff,
                "after_events": after_events,
                "frozen": frozen,
                "candidate": None if error else candidate,
                "decisions": decisions,
                "action_trace": trace,
                "triggered_instances": [list(pair) for pair in triggered],
            },
        }
    )

output = {
    "format": "T06-private-counterexamples-v1",
    "baseline_version": "PRD-V0.6-private-1",
    "boundary": "Manual derived inputs, no real reasoning/resource/Store/Agent/UI evidence",
    "cases": cases,
}
Path(__file__).with_name("counterexamples.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2) + "\n"
)
