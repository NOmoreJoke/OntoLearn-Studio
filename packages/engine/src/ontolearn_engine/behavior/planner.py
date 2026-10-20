"""Appendix E.1 planning over isolated JSON values, never a mutable authority.

prepare_events -> approved reasoning owner -> plan_behaviors -> transaction owner.
The last two arrows are deliberately not implemented here. A returned plan is not
committed, and binding checks do not establish that a reasoner actually ran.
"""

import hashlib
import json
import math
from dataclasses import dataclass
from itertools import combinations


class BehaviorError(ValueError):
    """Private stable reason and safe structural location; no raw input in errors."""

    def __init__(self, reason: str, location: str, evidence: dict | None = None):
        self.reason = reason
        self.location = location
        self.evidence = evidence or {}
        super().__init__(f"{reason}: {location}")


def _fail(reason, location, evidence=None):
    raise BehaviorError(reason, location, evidence)


def _json(value):
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
    except (TypeError, ValueError, RecursionError):
        _fail("invalid_json", "input")


def _hash(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _shape(value, required, optional=(), location="input"):
    if type(value) is not dict or set(value) - set(required) - set(optional):
        _fail("invalid_shape", location)
    if set(required) - set(value):
        _fail("missing_field", location)


def _text(value, location):
    if type(value) is not str or not value.strip():
        _fail("invalid_text", location)
    return value


def _list(value, location):
    if type(value) is not list:
        _fail("invalid_list", location)
    return value


def _integer(value, location, minimum=None):
    if type(value) is not int or (minimum is not None and value < minimum):
        _fail("invalid_integer", location)
    return value


def _scalar(value, location):
    if type(value) not in (str, bool, int, float) or (
        type(value) is float and not math.isfinite(value)
    ):
        _fail("invalid_scalar", location)
    return value


def _unique_texts(values, location):
    _list(values, location)
    for value in values:
        _text(value, location)
    if len(set(values)) != len(values):
        _fail("duplicate_identity", location)


def _schema(schema, classes):
    if type(schema) is not dict or not schema:
        _fail("invalid_schema", "schema")
    _unique_texts(classes, "classes")
    for name, spec in schema.items():
        _text(name, "schema.property")
        _shape(spec, ("kind", "cardinality"), location="schema.property")
        if spec["kind"] not in ("literal", "relation", "class") or spec["cardinality"] not in (
            "one",
            "many",
        ):
            _fail("invalid_schema", "schema.property")


def _fact(fact, state, schema, classes):
    _shape(fact, ("subject", "property", "value"), location="fact")
    _text(fact["subject"], "fact.subject")
    if fact["subject"] not in state["objects"]:
        _fail("invalid_object", "fact.subject")
    prop = fact["property"]
    if type(prop) is not str or prop not in schema:
        _fail("invalid_property", "fact.property")
    value = _scalar(fact["value"], "fact.value")
    kind = schema[prop]["kind"]
    if kind == "relation" and (type(value) is not str or value not in state["objects"]):
        _fail("invalid_object", "fact.value")
    if kind == "class" and (type(value) is not str or value not in classes):
        _fail("invalid_class", "fact.value")


def _normalize(state):
    state["objects"].sort()
    state["facts"].sort(key=_json)
    # Notifications retain execution order; they are internal records, not messages.
    return state


def _state(state, schema, classes):
    _shape(state, ("objects", "facts", "notifications"), location="state")
    _unique_texts(state["objects"], "state.objects")
    _list(state["facts"], "state.facts")
    keys = set()
    single = set()
    for fact in state["facts"]:
        _fact(fact, state, schema, classes)
        key = _json(fact)
        if key in keys:
            _fail("duplicate_fact", "state.facts")
        keys.add(key)
        slot = (fact["subject"], fact["property"])
        if schema[fact["property"]]["cardinality"] == "one":
            if slot in single:
                _fail("cardinality_violation", "state.facts")
            single.add(slot)
    ids = set(state["objects"])
    for record in _list(state["notifications"], "state.notifications"):
        _shape(record, ("id", "event_id", "behavior_id", "action_index", "message"))
        for name in ("id", "event_id", "behavior_id", "message"):
            _text(record[name], "notification." + name)
        _integer(record["action_index"], "notification.action_index", 0)
        if record["id"] in ids:
            _fail("duplicate_identity", "notification.id")
        ids.add(record["id"])
    return _normalize(state)


def _put(state, fact, schema, classes, *, append):
    _fact(fact, state, schema, classes)
    many = schema[fact["property"]]["cardinality"] == "many"
    if append != many:
        _fail("cardinality_action_mismatch", "action")
    if not many:
        state["facts"] = [
            f
            for f in state["facts"]
            if (f["subject"], f["property"]) != (fact["subject"], fact["property"])
        ]
    if _json(fact) not in {_json(f) for f in state["facts"]}:
        state["facts"].append(fact)


def _edit(state, edit, schema, classes):
    if type(edit) is not dict or type(edit.get("kind")) is not str:
        _fail("invalid_action", "event.edit")
    kind = edit["kind"]
    if kind == "create":
        _shape(edit, ("kind", "object"))
        obj = _text(edit["object"], "edit.object")
        if obj in state["objects"] or obj in {n["id"] for n in state["notifications"]}:
            _fail("duplicate_identity", "edit.object")
        state["objects"].append(obj)
    elif kind == "delete_object":
        _shape(edit, ("kind", "object"))
        if edit["object"] not in state["objects"]:
            _fail("invalid_object", "edit.object")
        state["objects"].remove(edit["object"])
        state["facts"] = [
            f
            for f in state["facts"]
            if f["subject"] != edit["object"]
            and not (schema[f["property"]]["kind"] == "relation" and f["value"] == edit["object"])
        ]
    elif kind in ("set", "add", "remove"):
        _shape(edit, ("kind", "subject", "property", "value"))
        fact = {k: edit[k] for k in ("subject", "property", "value")}
        if kind == "remove":
            _fact(fact, state, schema, classes)
            state["facts"] = [f for f in state["facts"] if _json(f) != _json(fact)]
        else:
            _put(state, fact, schema, classes, append=kind == "add")
    else:
        _fail("unavailable_action", "event.edit.kind")


@dataclass(frozen=True)
class PreparedRound:
    """Immutable serialized private handoff. Read properties return detached values."""

    _document: str

    @property
    def document(self):
        return json.loads(self._document)

    @property
    def binding(self):
        return _hash(self.document)

    @property
    def reasoning_input(self):
        doc = self.document
        return {
            "binding": self.binding,
            "assertion_digest": _hash(doc["after_events"]),
            "ontology_version": doc["request"]["ontology_version"],
            "rules_version": doc["request"]["rules_version"],
            "state": doc["after_events"],
        }


def prepare_events(request: dict) -> PreparedRound:
    """Validate, copy, canonicalize and apply event payloads; never infer or commit."""
    request = json.loads(_json(request))
    _shape(
        request,
        (
            "scope",
            "run_id",
            "round",
            "base_revision",
            "assertion_version",
            "ontology_version",
            "rules_version",
            "behavior_version",
            "classes",
            "schema",
            "state",
            "events",
            "consumption",
            "behaviors",
        ),
    )
    scope = request["scope"]
    _shape(scope, ("project_id", "scenario_id", "mode"), location="scope")
    _text(scope["project_id"], "scope.project_id")
    _text(scope["scenario_id"], "scope.scenario_id")
    if scope["mode"] not in ("sample", "scenario"):
        _fail("formal_data_forbidden", "scope.mode")
    for name in (
        "run_id",
        "base_revision",
        "assertion_version",
        "ontology_version",
        "rules_version",
        "behavior_version",
    ):
        _text(request[name], name)
    _integer(request["round"], "round", 1)
    if request["round"] > 1000:
        _fail("round_limit", "round")
    _schema(request["schema"], request["classes"])
    _state(request["state"], request["schema"], request["classes"])
    _list(request["behaviors"], "behaviors")
    # Scoped ledger is part of the transaction owner's snapshot, never a global cache.
    ledger = request["consumption"]
    _shape(ledger, ("scope", "events", "instances"), location="consumption")
    if _json(ledger["scope"]) != _json(scope):
        _fail("consumption_scope_mismatch", "consumption.scope")
    consumed = {}
    for record in _list(ledger["events"], "consumed_events"):
        _shape(record, ("event_id", "fingerprint"))
        event_id = _text(record["event_id"], "consumed.event_id")
        fingerprint = _text(record["fingerprint"], "consumed.fingerprint")
        if event_id in consumed:
            _fail("duplicate_identity", "consumed_events")
        consumed[event_id] = fingerprint
    instances = set()
    for pair in _list(ledger["instances"], "consumed_instances"):
        _shape(pair, ("event_id", "behavior_id"))
        key = (
            _text(pair["event_id"], "instance.event_id"),
            _text(pair["behavior_id"], "instance.behavior_id"),
        )
        if key in instances or key[0] not in consumed:
            _fail("invalid_consumption", "consumed_instances")
        instances.add(key)
    events = _list(request["events"], "events")
    for event in events:
        _shape(event, ("id", "type", "sequence", "version", "payload", "edits"))
        for name in ("id", "type", "version"):
            _text(event[name], "event." + name)
        _integer(event["sequence"], "event.sequence", 0)
        if type(event["payload"]) is not dict:
            _fail("invalid_shape", "event.payload")
        for name, value in event["payload"].items():
            _text(name, "event.payload.key")
            _scalar(value, "event.payload.value")
        _list(event["edits"], "event.edits")
    events.sort(key=lambda e: (e["sequence"], e["id"]))
    state = json.loads(_json(request["state"]))
    seen = dict(consumed)
    accepted, event_trace = [], []
    for event in events:
        fingerprint = _hash({k: v for k, v in event.items() if k != "sequence"})
        if event["id"] in seen:
            if seen[event["id"]] != fingerprint:
                _fail("event_identity_conflict", "event.id")
            event_trace.append({"event_id": event["id"], "reason": "duplicate_event"})
            continue
        seen[event["id"]] = fingerprint
        for edit in event["edits"]:
            _edit(state, edit, request["schema"], request["classes"])
        accepted.append({"event": event, "fingerprint": fingerprint})
        event_trace.append({"event_id": event["id"], "reason": "event_applied"})
    _state(state, request["schema"], request["classes"])
    return PreparedRound(
        _json(
            {
                "request": request,
                "after_events": state,
                "accepted": accepted,
                "event_trace": event_trace,
            }
        )
    )


def _expression(value, location):
    if type(value) is dict:
        if len(value) != 1 or next(iter(value)) not in ("event_field", "event_id", "instance_id"):
            _fail("invalid_expression", location)
        key = next(iter(value))
        if key == "event_id":
            if value[key] is not True:
                _fail("invalid_expression", location)
        else:
            _text(value[key], location)
    else:
        _scalar(value, location)


def _resolve(value, event, behavior_id, scope):
    if type(value) is not dict:
        return value
    key = next(iter(value))
    if key == "event_id":
        return event["id"]
    if key == "instance_id":
        return value[key] + ":" + _hash([scope, event["id"], behavior_id])
    if value[key] not in event["payload"]:
        _fail("missing_event_field", "event.payload")
    return event["payload"][value[key]]


def _definitions(behaviors):
    ids = set()
    for behavior in behaviors:
        _shape(
            behavior,
            (
                "id",
                "name",
                "description",
                "effect",
                "version",
                "enabled",
                "priority",
                "trigger",
                "conditions",
                "actions",
            ),
        )
        for name in ("id", "name", "description", "effect", "version"):
            _text(behavior[name], "behavior." + name)
        if behavior["id"] in ids:
            _fail("duplicate_behavior_id", "behavior.id")
        ids.add(behavior["id"])
        if type(behavior["enabled"]) is not bool:
            _fail("invalid_boolean", "behavior.enabled")
        _integer(behavior["priority"], "behavior.priority")
        trigger = behavior["trigger"]
        _shape(trigger, (), ("event_type", "event_id"), "behavior.trigger")
        if not trigger:
            _fail("missing_trigger", "behavior.trigger")
        for value in trigger.values():
            _text(value, "behavior.trigger")
        if not _list(behavior["conditions"], "behavior.conditions"):
            _fail("missing_condition", "behavior.conditions")
        for condition in behavior["conditions"]:
            if condition == {"op": "always"}:
                continue
            _shape(condition, ("op", "subject", "property", "value"))
            if condition["op"] != "has":
                _fail("unavailable_condition", "condition.op")
            _text(condition["property"], "condition.property")
            for name in ("subject", "value"):
                _expression(condition[name], "condition." + name)
        if not _list(behavior["actions"], "behavior.actions"):
            _fail("missing_action", "behavior.actions")
        for action in behavior["actions"]:
            if type(action) is not dict:
                _fail("invalid_action", "behavior.action")
            kind = action.get("kind")
            if kind == "create":
                fields = ("object",)
            elif kind in ("set", "add"):
                fields = ("subject", "property", "value")
            elif kind == "notify":
                fields = ("message",)
            else:
                _fail("unavailable_action", "behavior.action.kind")
            _shape(action, ("kind", *fields))
            for name in fields:
                if name == "property":
                    _text(action[name], "action.property")
                else:
                    _expression(action[name], "action." + name)


def _static_references(behaviors, state, schema, classes):
    """Reject visible configuration mistakes even with no matching events.

    Payload-dependent identities can only be validated when an instance resolves.
    Instances may use their own preceding creates, never an earlier peer action.
    """

    def check(fact, objects):
        prop = fact["property"]
        if prop not in schema:
            _fail("invalid_property", "definition.property")
        subject, value = fact["subject"], fact["value"]
        if type(subject) is not dict:
            _text(subject, "definition.subject")
            if subject not in objects:
                _fail("invalid_object", "definition.subject")
        if type(value) is not dict:
            kind = schema[prop]["kind"]
            if kind == "relation" and (type(value) is not str or value not in objects):
                _fail("invalid_object", "definition.value")
            if kind == "class" and (type(value) is not str or value not in classes):
                _fail("invalid_class", "definition.value")

    for behavior in behaviors:
        for condition in behavior["conditions"]:
            if condition != {"op": "always"}:
                check(condition, state["objects"])
        objects = list(state["objects"])
        for action in behavior["actions"]:
            kind = action["kind"]
            if kind == "create" and type(action["object"]) is not dict:
                _text(action["object"], "definition.object")
                # Existence is an execution-time check: an already-consumed
                # constant create must remain a no-op on duplicate delivery.
                if action["object"] not in objects:
                    objects.append(action["object"])
            elif kind in ("set", "add"):
                check(action, objects)
                many = schema[action["property"]]["cardinality"] == "many"
                if (kind == "add") != many:
                    _fail("cardinality_action_mismatch", "definition.action")
            elif kind == "notify" and type(action["message"]) is not dict:
                _text(action["message"], "definition.message")


def _difference(before, after):
    def items(state):
        return (
            {_json(["object", obj]) for obj in state["objects"]}
            | {_json(["fact", fact]) for fact in state["facts"]}
            | {_json(["notification", record]) for record in state["notifications"]}
        )

    old, new = items(before), items(after)
    return {
        "removed": [json.loads(x) for x in sorted(old - new)],
        "added": [json.loads(x) for x in sorted(new - old)],
    }


def plan_behaviors(prepared: PreparedRound, reasoning: dict) -> dict:
    """Freeze conditions, collect all intents, reject conflicts, return a detached plan.

    Errors never return partial candidates. The caller retains the original Store
    snapshot; no database rollback, resource stage or current-result publication
    occurs here. Only the approved adapter may supply the reasoning facts.
    """
    doc = prepared.document
    request = doc["request"]
    schema, classes, scope = request["schema"], request["classes"], request["scope"]
    reasoning = json.loads(_json(reasoning))
    _shape(
        reasoning,
        (
            "binding",
            "assertion_digest",
            "ontology_version",
            "rules_version",
            "version",
            "status",
            "facts",
        ),
        location="reasoning",
    )
    expected = prepared.reasoning_input
    if reasoning["status"] != "current" or any(
        reasoning[k] != expected[k]
        for k in ("binding", "assertion_digest", "ontology_version", "rules_version")
    ):
        _fail("stale_reasoning", "reasoning")
    _text(reasoning["version"], "reasoning.version")
    frozen = json.loads(_json(doc["after_events"]))
    for fact in _list(reasoning["facts"], "reasoning.facts"):
        _fact(fact, frozen, schema, classes)
        if _json(fact) not in {_json(f) for f in frozen["facts"]}:
            frozen["facts"].append(fact)
    # Single-valued reasoning contradictions cannot silently pick a condition value.
    _state(frozen, schema, classes)
    _definitions(request["behaviors"])
    _static_references(request["behaviors"], frozen, schema, classes)
    decisions, instances = [], []
    facts = {_json(fact) for fact in frozen["facts"]}
    behaviors = sorted(request["behaviors"], key=lambda b: (-b["priority"], b["id"]))
    for behavior in behaviors:
        for item in doc["accepted"]:
            event = item["event"]
            decision = {
                "event_id": event["id"],
                "behavior_id": behavior["id"],
                "assertion_version": request["assertion_version"],
                "reasoning_version": reasoning["version"],
                "conditions": [],
            }
            trigger = behavior["trigger"]
            if not behavior["enabled"]:
                reason = "disabled"
            elif any(
                event[{"event_type": "type", "event_id": "id"}[k]] != v for k, v in trigger.items()
            ):
                reason = "event_mismatch"
            else:
                for index, condition in enumerate(behavior["conditions"]):
                    if condition == {"op": "always"}:
                        satisfied, source = True, "explicit_always"
                    else:
                        fact = {
                            k: _resolve(condition[k], event, behavior["id"], scope)
                            for k in ("subject", "property", "value")
                        }
                        _fact(fact, frozen, schema, classes)
                        satisfied = _json(fact) in facts
                        source = "frozen_snapshot" if satisfied else "not_recorded_in_snapshot"
                    decision["conditions"].append(
                        {"index": index, "satisfied": satisfied, "reason": source}
                    )
                reason = (
                    "triggered"
                    if all(c["satisfied"] for c in decision["conditions"])
                    else "condition_not_satisfied"
                )
            decision["reason"] = reason
            decisions.append(decision)
            if reason == "triggered":
                instances.append((event, behavior))
    # Explicit Appendix E.1 key; event sequence is subordinate to behavior priority/ID.
    instances.sort(
        key=lambda pair: (-pair[1]["priority"], pair[1]["id"], pair[0]["sequence"], pair[0]["id"])
    )
    if sum(len(b["actions"]) for _, b in instances) > 1000:
        _fail("action_limit", "behavior.actions")
    # Resolve and validate action shapes against a separate per-instance scratch
    # so creates may be referenced later in the same instance, never a peer's create.
    intents = []
    for event, behavior in instances:
        scratch = json.loads(_json(doc["after_events"]))
        for index, template in enumerate(behavior["actions"]):
            action = {k: _resolve(v, event, behavior["id"], scope) for k, v in template.items()}
            intent = {
                "event_id": event["id"],
                "behavior_id": behavior["id"],
                "action_index": index,
                "action": action,
            }
            if action["kind"] == "notify":
                _text(action["message"], "action.message")
                intent["notification_id"] = "notification:" + _hash(
                    [scope, event["id"], behavior["id"], index]
                )
            else:
                _edit(scratch, action, schema, classes)
            intents.append(intent)
    writes = [i for i in intents if i["action"]["kind"] == "set"]
    for left, right in combinations(writes, 2):
        if (left["event_id"], left["behavior_id"]) == (right["event_id"], right["behavior_id"]):
            continue
        a, b = left["action"], right["action"]
        if (a["subject"], a["property"]) == (b["subject"], b["property"]) and (
            _json(a["value"]) != _json(b["value"])
        ):
            _fail(
                "competing_write",
                "behavior.intents",
                {
                    "event_trace": doc["event_trace"],
                    "decisions": decisions,
                    "intents": intents,
                    "conflict": [left, right],
                    "executed_actions": [],
                },
            )
    candidate = json.loads(_json(doc["after_events"]))
    trace = []
    for intent in intents:
        action = intent["action"]
        prior = _json(candidate)
        if action["kind"] == "notify":
            record = {
                "id": intent["notification_id"],
                "event_id": intent["event_id"],
                "behavior_id": intent["behavior_id"],
                "action_index": intent["action_index"],
                "message": action["message"],
            }
            if record["id"] in candidate["objects"] or any(
                n["id"] == record["id"] for n in candidate["notifications"]
            ):
                _fail("duplicate_identity", "notification.id")
            candidate["notifications"].append(record)
        else:
            _edit(candidate, action, schema, classes)
        _normalize(candidate)
        trace.append({**intent, "effect": "unchanged" if prior == _json(candidate) else "changed"})
    _state(candidate, schema, classes)
    consumed_events = request["consumption"]["events"] + [
        {"event_id": item["event"]["id"], "fingerprint": item["fingerprint"]}
        for item in doc["accepted"]
    ]
    consumed_instances = request["consumption"]["instances"] + [
        {"event_id": event["id"], "behavior_id": behavior["id"]} for event, behavior in instances
    ]
    return {
        "kind": "behavior_plan",
        "semantics_version": "E.1-private-v1",
        "committed": False,
        "scope": scope,
        "run_id": request["run_id"],
        "round": request["round"],
        "base_revision": request["base_revision"],
        "binding": prepared.binding,
        "assertion_version": request["assertion_version"],
        "reasoning_version": reasoning["version"],
        "behavior_version": request["behavior_version"],
        "before": request["state"],
        "after_events": doc["after_events"],
        "frozen": frozen,
        "event_trace": doc["event_trace"],
        "decisions": decisions,
        "action_trace": trace,
        "candidate": candidate,
        "consumption": {"scope": scope, "events": consumed_events, "instances": consumed_instances},
        "diff": _difference(request["state"], candidate),
    }
