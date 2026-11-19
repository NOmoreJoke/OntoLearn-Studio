"""T06 behavior wire services: isolated sample runs over the owned Store.

Three ``business3`` methods (selected-project authority, named-bridge exposure)
backed by :mod:`ontolearn_engine.behavior.planner` over an isolated working
copy. Formal asserted project facts are NEVER mutated: every durable record is
appended under ``w4:behavior:*`` namespaced ``job_details`` keys inside
ordinary Store transactions. ``job_details`` is append-only evidence (immutable
by SQL trigger), so state transitions mint new rows - a scope commit, a run record, a separate
cancelled marker, an operation claim and a run-index row - and readers fold
them. No key ever collides with ``run_before_commit``'s own primary keys.

All eleven frozen interface rules (interface-freeze.md §T06) are enforced here:
trigger binding, condition lowering against the real frozen snapshot catalog,
catalog-checked action cardinality, reserved event payload key rejection,
host-supplied real input versions, tagged-union diff projection, the
completed/candidate/failed/cancelled lifecycle, dynamic freshness, cancel terminal
persistence and the strict public error projection. Private planner evidence,
raw exceptions, OS paths and stack traces never cross the wire.
"""

import json
import re
import sqlite3

from ontolearn_engine.behavior import working_copy as copy
from ontolearn_engine.behavior.planner import BehaviorError, plan_behaviors, prepare_events
from ontolearn_engine.project.ontology_turtle import resolve_active
from ontolearn_engine.project.run_before_commit import lookup_receipt
from ontolearn_engine.storage import canonical, digest

METHODS = frozenset(
    {
        "project.behavior.run",
        "project.behavior.read",
        "project.behavior.cancel",
    }
)

RDF_TYPE = copy.RDF_TYPE
OWL = "http://www.w3.org/2002/07/owl#"
OWL_CLASS = OWL + "Class"
OWL_DATATYPE_PROPERTY = OWL + "DatatypeProperty"
OWL_OBJECT_PROPERTY = OWL + "ObjectProperty"
OWL_FUNCTIONAL_PROPERTY = OWL + "FunctionalProperty"
# Mirror of the frozen TS BehaviorAdapterContract.event.reservedPayloadKeys.
RESERVED_PAYLOAD_KEYS = ("__proto__", "constructor", "prototype")
SCOPE_PREFIX = "w4:behavior:scope:"
RUN_PREFIX = "w4:behavior:run:"
OP_PREFIX = "w4:behavior:op:"
RUNIDX_PREFIX = "w4:behavior:runidx:"
CANCELLED_PREFIX = "w4:behavior:cancelled:"
RESULT_SCAN_CAP = 400
TERMINAL_STATES = ("failed", "cancelled")
# Wire iri-shaped values must keep a scheme so projected facts stay encodable.
_IRI_SHAPE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s<>\"{}|^`\\]+$")
# Frozen normative projection of private planner reasons onto the public
# BehaviorPublicError allowlist (behavior.ts projectBehaviorError).
CONFLICT_REASONS = frozenset({"competing_write", "event_identity_conflict", "stale_reasoning"})
UNAVAILABLE_REASONS = frozenset(
    {"unavailable_condition", "unavailable_action", "formal_data_forbidden"}
)
INVALID_INPUT_REASONS = frozenset(
    {
        "invalid_shape",
        "invalid_text",
        "invalid_property",
        "invalid_object",
        "invalid_class",
        "invalid_scalar",
        "invalid_expression",
        "duplicate_behavior_id",
        "duplicate_identity",
        "missing_condition",
        "missing_trigger",
        "missing_action",
        "missing_event_field",
        "cardinality_action_mismatch",
    }
)
PUBLIC_ERROR_KEYS = {
    "conflict": "behavior.conflict",
    "invalid_input": "behavior.invalidInput",
    "unavailable": "behavior.unavailable",
    "execution_failed": "behavior.executionFailed",
    "cancel_failed": "behavior.cancelFailed",
}


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


class _PublicBehaviorError(Exception):
    """Internal carrier of an already-projected public behavior error."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _project_reason(reason: object, phase: str = "run") -> dict:
    if reason in CONFLICT_REASONS:
        code = "conflict"
    elif reason in UNAVAILABLE_REASONS:
        code = "unavailable"
    elif reason in INVALID_INPUT_REASONS:
        code = "invalid_input"
    else:
        code = "cancel_failed" if phase == "cancel" else "execution_failed"
    return {"code": code, "messageKey": PUBLIC_ERROR_KEYS[code]}


def _public_fail(code: str):
    raise _PublicBehaviorError(code)


def _public_error(code):
    return {"code": code, "messageKey": PUBLIC_ERROR_KEYS[code]}


def _read_detail(store, project, identity):
    row = store._db.execute(
        "SELECT payload FROM job_details WHERE id=? AND project=?", (identity, project)
    ).fetchone()
    if row is None:
        return None
    try:
        record = json.loads(row[0])
    except (ValueError, TypeError):
        fault("INVALID_STATE")
    if not isinstance(record, dict) or record.get("projectId") != project:
        fault("INVALID_STATE")
    return record


def _insert_detail(store, project, identity, record):
    """Append-only evidence write; a duplicate key is a deterministic conflict."""
    try:
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (identity, project, canonical(record)),
        )
    except sqlite3.IntegrityError:
        fault("IDENTITY_CONFLICT")


def _index_run(store, project, run_id):
    """Append-only project run index; rowid order is the scope takeover order."""
    _insert_detail(
        store,
        project,
        RUNIDX_PREFIX + run_id,
        {"recordVersion": 1, "projectId": project, "runId": run_id},
    )


def indexed_runs(store, project):
    """Read-only accessor: run ids newest-first (bounded constant-prefix scan)."""
    rows = store._db.execute(
        "SELECT id FROM job_details WHERE project=? AND id>=? AND id<? ORDER BY rowid DESC LIMIT ?",
        (project, "w4:behavior:runidx:", "w4:behavior:runidx:\uffff", RESULT_SCAN_CAP),
    ).fetchall()
    return [row["id"][len(RUNIDX_PREFIX) :] for row in rows]


def load_run(store, project, run_id):
    """Folded run record (run row + optional cancelled marker) or None."""
    record = _read_detail(store, project, RUN_PREFIX + run_id)
    if record is None:
        return None
    if _read_detail(store, project, CANCELLED_PREFIX + run_id) is not None:
        record = {**record, "state": "cancelled"}
    return record


def _scope_replaced(store, project, run_id, scope_id):
    """True when a newer indexed run took over the same isolated scope.

    Only the fixed-constant-prefix index scan and exact-primary-key reads are
    used; no wire identifier ever enters a SQL statement or a scan bound.
    """
    for other in indexed_runs(store, project):
        if other == run_id:
            return False  # This run is still the newest takeover of its scope.
        record = _read_detail(store, project, RUN_PREFIX + other)
        if record is not None and record.get("binding", {}).get("scopeId") == scope_id:
            return True
    return False


# --- real snapshot material -----------------------------------------------------------


def _ontology_material(state):
    """Classes and property schema derived from the real frozen ontology catalog."""
    classes = set()
    schema = {RDF_TYPE: {"kind": "class", "cardinality": "many"}}
    functional = set()
    for record in state["definitions"]:
        if record["layer"] != "ontology":
            continue
        try:
            payload = json.loads(record["payload"])
            triples = payload["triples"] if isinstance(payload, dict) else None
            if isinstance(payload, dict):
                cardinality = payload.get("singleValuedPredicates", [])
                if not isinstance(cardinality, list) or any(
                    not isinstance(prop, str) for prop in cardinality
                ):
                    fault("INVALID_STATE")
                functional.update(cardinality)
        except (ValueError, TypeError):
            fault("INVALID_STATE")
        if not isinstance(triples, list):
            continue
        for triple in triples:
            if not isinstance(triple, dict) or triple.get("predicate") != RDF_TYPE:
                continue
            subject, obj = triple.get("subject"), triple.get("object")
            if not isinstance(subject, str) or not isinstance(obj, str):
                continue
            if obj in ("<" + OWL_CLASS + ">", "<http://www.w3.org/2000/01/rdf-schema#Class>"):
                classes.add(subject)
            elif obj == "<" + OWL_DATATYPE_PROPERTY + ">":
                schema.setdefault(subject, {"kind": "literal", "cardinality": "many"})
            elif obj == "<" + OWL_OBJECT_PROPERTY + ">":
                schema.setdefault(subject, {"kind": "relation", "cardinality": "many"})
            elif obj == "<" + OWL_FUNCTIONAL_PROPERTY + ">":
                functional.add(subject)
    for prop in functional:
        if prop in schema:
            schema[prop]["cardinality"] = "one"
    return sorted(classes), schema


# --- wire -> planner lowering ---------------------------------------------------------


def _planner_scalar(tagged):
    kind, value = tagged["kind"], tagged["value"]
    if kind in ("string", "iri"):
        return value
    return value  # boolean stays bool, number keeps its parsed JSON type


def _lower_expression(expression):
    kind = expression["kind"]
    if kind == "value":
        return _planner_scalar(expression["value"])
    if kind == "eventField":
        return {"event_field": expression["field"]}
    if kind == "eventId":
        return {"event_id": True}
    if kind == "instanceId":
        prefix = expression["prefix"]
        if _IRI_SHAPE.match(prefix) is None:
            # Generated instance ids must stay valid projected IRI values.
            _public_fail("invalid_input")
        return {"instance_id": prefix}
    return {"event_template": expression["template"]}


def _lower_condition(condition, classes):
    op = condition["op"]
    if op == "always":
        return {"op": "always"}
    if op in ("has", "equals"):
        return {
            "op": "has",
            "subject": _lower_expression(condition["subject"]),
            "property": condition["property"],
            "value": _lower_expression(condition["value"]),
        }
    if op == "type":
        # B-01/B-02: rdf:type checks verified against the real frozen snapshot
        # catalog; a class outside the catalog is deterministically unavailable.
        if condition["classId"] not in classes:
            _public_fail("unavailable")
        return {
            "op": "has",
            "subject": _lower_expression(condition["subject"]),
            "property": RDF_TYPE,
            # Class-kind facts carry the plain class IRI as their scalar.
            "value": condition["classId"],
        }
    # The private planner has no wildcard value predicate: exists -> unavailable.
    _public_fail("unavailable")


def _lower_initial(fields):
    return [
        {"property": field["property"], "value": _lower_expression(field["value"])}
        for field in fields
    ]


def _lower_action(action, schema, classes):
    kind = action["kind"]
    if kind == "create":
        class_id = action.get("classId")
        initial = list(action.get("initial", []))
        if class_id is not None:
            if class_id not in classes:
                _public_fail("invalid_input")
            for field in initial:
                if field["property"] == RDF_TYPE:
                    value = field["value"]
                    if value["kind"] != "iri" or value["value"] != class_id:
                        # Conflicting explicit type initialization rejects.
                        _public_fail("invalid_input")
            initial = [
                {
                    "property": RDF_TYPE,
                    "value": {"kind": "value", "value": {"kind": "iri", "value": class_id}},
                }
            ] + initial
        return {
            "kind": "create",
            "object": _lower_expression(action["object"]),
            "initial": _lower_initial(initial),
        }
    if kind in ("set", "add"):
        prop = action["property"]
        spec = schema.get(prop)
        if spec is None:
            _public_fail("invalid_input")
        if spec["cardinality"] != ("one" if kind == "set" else "many"):
            # set is single-valued overwrite only; add requires declared many.
            _public_fail("invalid_input")
        return {
            "kind": kind,
            "subject": _lower_expression(action["subject"]),
            "property": prop,
            "value": _lower_expression(action["value"]),
        }
    notify = {"kind": "notify", "message": _lower_expression(action["message"])}
    if "id" in action:
        notify["id"] = _lower_expression(action["id"])
    return notify


def _lower_edit(edit):
    kind = edit["kind"]
    if kind == "create":
        return {
            "kind": "create",
            "object": edit["object"],
            "initial": [
                {"property": field["property"], "value": _planner_scalar(field["value"])}
                for field in edit.get("initial", [])
            ],
        }
    if kind in ("delete_object", "declare"):
        return {"kind": kind, "object": edit["object"]}
    return {
        "kind": kind,
        "subject": edit["subject"],
        "property": edit["property"],
        "value": _planner_scalar(edit["value"]),
    }


def _lower_event(event):
    if set(RESERVED_PAYLOAD_KEYS) & set(event["payload"]):
        # Reserved own keys reject the whole event before any planning.
        _public_fail("invalid_input")
    return {
        "id": event["id"],
        "type": event["type"],
        "sequence": event["sequence"],
        "version": str(event["version"]),
        "payload": dict(event["payload"]),
        "edits": [_lower_edit(edit) for edit in event["edits"]],
    }


def _lower_draft(draft, schema, classes, event_ids):
    trigger_source = draft["trigger"]
    event_type = trigger_source["eventType"].strip()
    if not event_type:
        _public_fail("invalid_input")
    trigger = {"event_type": event_type}
    if "eventId" in trigger_source:
        event_id = trigger_source["eventId"]
        if not event_id.strip() or event_id not in event_ids:
            # Unbound trigger event IDs reject deterministically.
            _public_fail("invalid_input")
        trigger["event_id"] = event_id
    if not draft["conditions"]:
        # A non-empty AND list is required.
        _public_fail("invalid_input")
    return {
        "id": draft["id"],
        "name": draft["name"],
        "description": draft["description"],
        "effect": draft["effect"],
        "version": str(draft["version"]),
        "enabled": draft["enabled"],
        "priority": draft["priority"],
        "trigger": trigger,
        "conditions": [_lower_condition(condition, classes) for condition in draft["conditions"]],
        "actions": [_lower_action(action, schema, classes) for action in draft["actions"]],
    }


# --- planner -> wire projection -------------------------------------------------------


def _wire_value(value, prop_kind):
    if prop_kind in ("relation", "class"):
        return {"kind": "iri", "value": value}
    if type(value) is bool:
        return {"kind": "boolean", "value": value}
    if type(value) in (int, float):
        return {"kind": "number", "value": value}
    return {"kind": "string", "value": value}


def _wire_diff_item(item, schema):
    kind = item[0]
    if kind == "object":
        return {"kind": "object", "objectId": item[1]}
    if kind == "fact":
        fact = item[1]
        prop_kind = schema.get(fact["property"], {"kind": "literal"})["kind"]
        return {
            "kind": "fact",
            "fact": {
                "subject": fact["subject"],
                "property": fact["property"],
                "value": _wire_value(fact["value"], prop_kind),
            },
        }
    record = item[1]
    return {
        "kind": "notification",
        "notification": {
            "id": record["id"],
            "eventId": record["event_id"],
            "behaviorId": record["behavior_id"],
            "message": record["message"],
        },
    }


def _wire_diff(diff, schema):
    return {
        "added": [_wire_diff_item(item, schema) for item in diff["added"]],
        "removed": [_wire_diff_item(item, schema) for item in diff["removed"]],
    }


def _wire_conditions(decisions):
    return [
        {
            "eventId": decision["event_id"],
            "behaviorId": decision["behavior_id"],
            "triggered": decision["reason"] == "triggered",
            "reason": decision["reason"],
            "conditions": decision["conditions"],
        }
        for decision in decisions
    ]


def _store_actions(plan):
    return [
        {
            "eventId": trace["event_id"],
            "behaviorId": trace["behavior_id"],
            "index": trace["action_index"],
            "kind": trace["action"]["kind"],
            "effect": trace["effect"],
        }
        for trace in plan["action_trace"]
    ]


def _store_notifications(records):
    return [
        {
            "id": record["id"],
            "eventId": record["event_id"],
            "behaviorId": record["behavior_id"],
            "message": record["message"],
        }
        for record in records
    ]


_ACTION_STATE_COMPLETED = {"changed": "applied", "unchanged": "deduplicated"}
_ACTION_STATE_CANDIDATE = {"changed": "planned", "unchanged": "deduplicated"}
_ACTION_STATE_TERMINAL = {"changed": "rolled_back", "unchanged": "skipped"}


def _wire_actions(actions, mapping):
    return [
        {
            "eventId": action["eventId"],
            "behaviorId": action["behaviorId"],
            "index": action["index"],
            "kind": action["kind"],
            "state": mapping[action["effect"]],
        }
        for action in actions
    ]


def _wire_notifications(notifications, state):
    return [{**record, "state": state} for record in notifications]


def _freshness(store, internal, record, passed_binding):
    """Dynamic freshness against the live project revision, snapshot and scope."""
    if passed_binding["behaviorVersion"] != record["binding"]["behaviorVersion"]:
        return "stale", "behavior-version-changed"
    if store.revision(internal) != record["binding"]["baseRevision"]:
        return "stale", "project-revision-changed"
    if digest(store._snapshot_projection(internal)) != record["binding"]["inputSnapshotId"]:
        return "stale", "snapshot-changed"
    if _scope_replaced(store, record["projectId"], record["runId"], record["binding"]["scopeId"]):
        return "stale", "scope-replaced"
    if record["state"] in TERMINAL_STATES:
        return "historical", None
    return "current", None


def _reply_dto(store, internal, record, passed_binding):
    freshness, stale_reason = _freshness(store, internal, record, passed_binding)
    versions = record["versions"]
    base = {
        "projectId": record["projectId"],
        "operationId": record["operationId"],
        "runId": record["runId"],
        "binding": record["binding"],
        "scope": "sample",
        "freshness": freshness,
        "staleReason": stale_reason,
        "assertionVersion": versions["assertionVersion"],
        "inferenceVersion": versions["inferenceVersion"],
        "semanticsVersion": versions["semanticsVersion"],
        "conditions": record["conditions"],
    }
    state = record["state"]
    if state == "completed":
        return {
            **base,
            "state": "completed",
            "committed": True,
            "error": None,
            "actions": _wire_actions(record["actions"], _ACTION_STATE_COMPLETED),
            "diff": record["diff"],
            "notifications": _wire_notifications(record["notifications"], "recorded"),
        }
    if state == "candidate":
        return {
            **base,
            "state": "candidate",
            "committed": False,
            "error": None,
            "actions": _wire_actions(record["actions"], _ACTION_STATE_CANDIDATE),
            "diff": record["diff"],
            "notifications": _wire_notifications(record["notifications"], "candidate"),
        }
    if state == "failed":
        return {
            **base,
            "state": "failed",
            "committed": False,
            "error": record["error"],
            "actions": _wire_actions(record["actions"], _ACTION_STATE_TERMINAL),
            "diff": {"added": [], "removed": []},
            "notifications": _wire_notifications(record["notifications"], "discarded"),
        }
    return {
        **base,
        "state": "cancelled",
        "committed": False,
        "error": None,
        "actions": _wire_actions(record["actions"], _ACTION_STATE_TERMINAL),
        "diff": {"added": [], "removed": []},
        "notifications": _wire_notifications(record["notifications"], "discarded"),
    }


def _failed_record(project, operation, run_id, binding, versions, public_error):
    return {
        "recordVersion": 1,
        "projectId": project,
        "operationId": operation,
        "runId": run_id,
        "binding": binding,
        "state": "failed",
        "versions": versions,
        "conditions": [],
        "actions": [],
        "notifications": [],
        "diff": {"added": [], "removed": []},
        "error": public_error,
    }


def _scope_prefix(binding):
    identity = digest([binding["projectId"], binding["baseRevision"], binding["inputSnapshotId"]])
    return f"{SCOPE_PREFIX}{binding['scopeId']}:{identity}:"


def _latest_scope(store, project, prefix):
    row = store._db.execute(
        "SELECT id FROM job_details WHERE project=? AND id>=? AND id<? ORDER BY rowid DESC LIMIT 1",
        (project, prefix, prefix + "\uffff"),
    ).fetchone()
    return _read_detail(store, project, row["id"]) if row else None


def scope_commit(store, project, run):
    return _read_detail(store, project, _scope_prefix(run["binding"]) + run["runId"])


def _plan_record(state, params, versions, prior):
    project, binding = params["projectId"], params["binding"]
    classes, schema = _ontology_material(state)
    reasoner = copy.Reasoner(state)
    versions.update(ontologyVersion=reasoner.ontology_version, rulesVersion=reasoner.rules_version)
    isolated = prior["isolated"] if prior else {}
    assertions = isolated.get("assertedFacts", copy.asserted_facts(state))
    frozen_state, _ = copy.planner_state(
        assertions,
        schema,
        classes,
        objects=isolated.get("objects", ()),
        notifications=isolated.get("plannerNotifications", ()),
    )
    events = [_lower_event(event) for event in params["events"]]
    behavior = _lower_draft(params["draft"], schema, classes, {event["id"] for event in events})
    scope = {"project_id": project, "scenario_id": binding["scopeId"], "mode": "sample"}
    prepared = prepare_events(
        copy.plan_request(
            scope,
            params["runId"],
            1,
            binding["baseRevision"],
            versions,
            classes,
            schema,
            frozen_state,
            [behavior],
            events,
            isolated.get("consumption", {"events": [], "instances": []}),
        )
    )
    after_events = prepared.reasoning_input["state"]
    event_facts = copy.apply_planner_delta(assertions, frozen_state, after_events, schema, classes)
    inferred, version = reasoner.infer(event_facts)
    versions["inferenceVersion"] = version
    projection, proofs = copy.planner_state([], schema, classes, inferred=inferred)
    # The planner's conditions use the frozen reasoning input, never action output.
    plan = plan_behaviors(
        prepared,
        copy.reasoning_input(prepared, version, proofs),
        inferred_objects=projection["objects"],
    )
    candidate = plan["candidate"]
    asserted = copy.apply_planner_delta(event_facts, after_events, candidate, schema, classes)
    end_inferred = inferred if asserted == event_facts else reasoner.infer(asserted)[0]
    actions = _store_actions(plan)
    notifications = _store_notifications(
        record for kind, record in plan["diff"]["added"] if kind == "notification"
    )
    duplicate_ids = [
        item["event_id"] for item in plan["event_trace"] if item["reason"] == "duplicate_event"
    ]
    prior_actions = isolated.get("executedActions", [])
    wire_actions = actions + [
        {**entry, "effect": "unchanged"}
        for entry in prior_actions
        if entry["eventId"] in duplicate_ids
    ]
    consumption = plan["consumption"]
    namespaces = sorted(
        {name.removesuffix("WorkOrder") for name in classes if name.endswith("WorkOrder")}
    )
    orders = [
        {key: value for key, value in item.items() if key != "iri"}
        for namespace in namespaces
        for item in copy.work_orders(asserted, namespace)
    ]
    return {
        "state": "completed",
        "committed": True,
        "eventIds": [event["id"] for event in params["events"]],
        "eventTrace": plan["event_trace"],
        "draft": params["draft"],
        "events": events,
        "versions": {**versions, "semanticsVersion": plan["semantics_version"]},
        "conditions": _wire_conditions(plan["decisions"]),
        "actions": wire_actions,
        "notifications": notifications,
        "diff": _wire_diff(plan["diff"], schema),
        "isolated": {
            "assertedFacts": asserted,
            "facts": copy.sorted_facts([*asserted, *end_inferred]),
            "behaviorBeforeInference": inferred,
            "objects": candidate["objects"],
            "notifications": _store_notifications(candidate["notifications"]),
            "plannerNotifications": candidate["notifications"],
            "actionTrace": copy.action_trace(plan),
            "executedActions": prior_actions + actions,
            "orders": orders,
            "consumption": consumption,
            "eventOrigins": {
                **isolated.get("eventOrigins", {}),
                **{
                    item["event_id"]: params["runId"]
                    for item in plan["event_trace"]
                    if item["reason"] == "event_applied"
                },
            },
            "consumedEvents": [entry["event_id"] for entry in consumption["events"]],
            "triggeredInstances": [
                [entry["event_id"], entry["behavior_id"]] for entry in consumption["instances"]
            ],
        },
        "error": None,
    }


def _run(store, params, origin):
    project, binding = params["projectId"], params["binding"]
    operation, run_id = params["operationId"], params["runId"]
    fingerprint = digest(
        {key: params[key] for key in ("runId", "scope", "binding", "draft", "events")}
    )
    internal = resolve_active(store, project)
    with store._transaction():
        # Fail-closed before-run receipt reconciliation for this exact operation.
        lookup_receipt(store, project, operation, "behavior", binding["baseRevision"])
        op_record = _read_detail(store, project, OP_PREFIX + operation)
        if op_record is not None:
            if op_record.get("requestHash") != fingerprint or op_record.get("runId") != run_id:
                fault("IDENTITY_CONFLICT")
            record = load_run(store, project, run_id)
            if record is None:
                fault("IDENTITY_CONFLICT")
            return _reply_dto(store, internal, record, binding)
        if _read_detail(store, project, RUN_PREFIX + run_id) is not None:
            fault("IDENTITY_CONFLICT")
        if store.revision(internal) != binding["baseRevision"]:
            fault(
                "REVISION_CONFLICT",
                expected=binding["baseRevision"],
                actual=store.revision(internal),
            )
        state = store.state(internal)
        if digest(store._snapshot_projection(internal)) != binding["inputSnapshotId"]:
            fault("IDENTITY_CONFLICT")
        versions = {
            "assertionVersion": binding["inputSnapshotId"],
            "behaviorVersion": binding["behaviorVersion"],
            "inferenceVersion": None,
            "semanticsVersion": "E.1-private-v2",
        }
        prefix = _scope_prefix(binding)
        prior = _latest_scope(store, project, prefix)
        try:
            result = _plan_record(state, params, versions, prior)
        except _PublicBehaviorError as error:
            result = _failed_record(
                project, operation, run_id, binding, versions, _public_error(error.code)
            )
        except BehaviorError as error:
            result = _failed_record(
                project, operation, run_id, binding, versions, _project_reason(error.reason)
            )
        except Exception:
            result = _failed_record(
                project, operation, run_id, binding, versions, _project_reason(None)
            )
        record = {
            **result,
            "recordVersion": 1,
            "projectId": project,
            "operationId": operation,
            "runId": run_id,
            "binding": binding,
            "eventIds": [event["id"] for event in params["events"]],
        }
        if record["state"] == "completed":
            _insert_detail(
                store,
                project,
                prefix + run_id,
                {
                    "projectId": project,
                    "runId": run_id,
                    "binding": binding,
                    "isolated": record["isolated"],
                },
            )
        _insert_detail(store, project, RUN_PREFIX + run_id, record)
        _index_run(store, project, run_id)
        _insert_detail(
            store,
            project,
            OP_PREFIX + operation,
            {
                "recordVersion": 1,
                "projectId": project,
                "operationId": operation,
                "runId": run_id,
                "requestHash": fingerprint,
            },
        )
        reply = _reply_dto(store, internal, record, binding)
        store._valid("result_project.behavior.run", reply)
        return reply


def _reconcile_read(store, params):
    """Reconcile the original binding and runId without redelivering events."""
    project, run_id = params["projectId"], params["runId"]
    binding = params["binding"]
    record = load_run(store, project, run_id)
    if record is None:
        # The frozen error catalog's NOT_FOUND resource vocabulary is fixed;
        # isolated runs reconcile under their owning operation identity.
        fault("NOT_FOUND", resource="operation")
    if record["operationId"] != params["operationId"]:
        fault("IDENTITY_CONFLICT")
    persisted = record["binding"]
    for key in ("projectId", "baseRevision", "inputSnapshotId", "scopeId", "requestId"):
        if binding[key] != persisted[key]:
            fault("IDENTITY_CONFLICT")
    return record


def _read(store, params, origin):
    project = params["projectId"]
    internal = resolve_active(store, project)
    with store._read():
        record = _reconcile_read(store, params)
        return _reply_dto(store, internal, record, params["binding"])


def _cancel(store, params, origin):
    project, run_id = params["projectId"], params["runId"]
    binding = params["binding"]
    internal = resolve_active(store, project)
    with store._transaction():
        record = _reconcile_read(store, params)
        if record["state"] == "cancelled":
            # Durable terminal state already persisted; idempotent replay.
            return _reply_dto(store, internal, record, binding)
        if record["state"] != "candidate":
            # Cancelling a completed or failed run maps to the fixed
            # cancel_failed public projection.
            fault("INVALID_STATE")
        # The terminal cancelled marker is appended (immutable evidence) and is
        # durable BEFORE the reply is returned; still bound to the original
        # operation, run and request.
        _insert_detail(
            store,
            project,
            CANCELLED_PREFIX + run_id,
            {
                "recordVersion": 1,
                "projectId": project,
                "operationId": record["operationId"],
                "runId": run_id,
                "state": "cancelled",
            },
        )
        record = {**record, "state": "cancelled"}
        return _reply_dto(store, internal, record, binding)


def dispatch(store, method, params, origin):
    store._valid("params_" + method, params)
    if method == "project.behavior.run":
        result = _run(store, params, origin)
    elif method == "project.behavior.read":
        result = _read(store, params, origin)
    else:
        result = _cancel(store, params, origin)
    store._valid("result_" + method, result)
    return result
