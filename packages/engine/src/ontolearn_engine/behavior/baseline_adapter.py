"""Read-only T09 fixed-data adapter, never an execution/Store/IPC authority.

Only the published fixture DSL and string/boolean RDF lexical subset are decoded.
Full RDF semantics, actual inference and atomic rounds remain approved adapters.
No T09 Python implementation or expected result is executed by this module.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from ontolearn_engine.rdf_snapshot import iri

from .planner import _edit, _fail, _hash, _json, _list, _shape, _state, _text

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
OWL = "http://www.w3.org/2002/07/owl#"
XSD_BOOLEAN = "http://www.w3.org/2001/XMLSchema#boolean"
ADAPTER_VERSION = "T09-fixture-to-T06-v1"
DATA = "tests/fixtures/product-baselines/"


def _iri(value):
    _text(value, "baseline.iri")
    try:
        iri(value)
    except ValueError:
        _fail("invalid_fixture_iri", "baseline.iri")
    return value


def _read(root, relative):
    if type(relative) is not str or Path(relative).is_absolute():
        _fail("invalid_fixture_path", "manifest.path")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        _fail("invalid_fixture_path", "manifest.path")
    try:
        return path.read_bytes()
    except OSError:
        _fail("fixture_unavailable", "manifest.file")


def _parse(data):
    try:
        return json.loads(data)
    except (ValueError, UnicodeError, RecursionError):
        _fail("invalid_fixture_json", "manifest.file")


def _bytes_hash(data):
    import hashlib

    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class BaselineBundle:
    """Verified byte snapshot. JSON access returns detached input values."""

    _document: str
    manifest_sha256: str

    @property
    def document(self):
        return json.loads(self._document)


def load_bundle(root: str | Path, manifest_sha256: str) -> BaselineBundle:
    """Verify the caller-pinned manifest, source PRD and every declared file.

    Uses the verified byte buffers for parsing, preventing a second read from
    silently substituting different contents. Does not write or import data code.
    The pinned hash is provenance, not approval of a product runtime or new path.
    """
    root = Path(root).resolve()
    manifest_bytes = _read(root, DATA + "manifest.json")
    if _bytes_hash(manifest_bytes) != manifest_sha256:
        _fail("fixture_manifest_mismatch", "manifest")
    manifest = _parse(manifest_bytes)
    _shape(manifest, ("version", "source", "files"), location="manifest")
    _text(manifest["version"], "manifest.version")
    _shape(manifest["source"], ("path", "sha256"), location="manifest.source")
    if _bytes_hash(_read(root, manifest["source"]["path"])) != manifest["source"]["sha256"]:
        _fail("fixture_source_mismatch", "manifest.source")
    if type(manifest["files"]) is not dict:
        _fail("invalid_fixture_manifest", "manifest.files")
    buffers = {}
    for relative, expected in manifest["files"].items():
        content = _read(root, relative)
        if _bytes_hash(content) != expected:
            _fail("fixture_file_mismatch", "manifest.file")
        buffers[relative] = content
    required = [
        DATA + name for name in ("G-base.json", "G-behavior.json", "cases.json", "conventions.json")
    ]
    if any(relative not in buffers for relative in required):
        _fail("missing_fixture_file", "manifest.files")
    document = {
        "manifest": manifest,
        **{relative.removeprefix(DATA): _parse(buffers[relative]) for relative in required},
    }
    return BaselineBundle(_json(document), manifest_sha256)


def decode_value(value):
    """Exact fixed-fixture string/boolean/IRI syntax, not a general RDF parser."""
    _text(value, "fixture.object")
    if value.startswith("<") and value.endswith(">"):
        return _iri(value[1:-1])
    suffix = "^^<" + XSD_BOOLEAN + ">"
    if value.endswith(suffix):
        lexical = _parse(value[: -len(suffix)])
        if lexical not in ("true", "false"):
            _fail("unsupported_fixture_literal", "fixture.object")
        return lexical == "true"
    result = _parse(value)
    if type(result) is not str:
        _fail("unsupported_fixture_literal", "fixture.object")
    try:
        result.encode("utf-8")
    except UnicodeError:
        _fail("unsupported_fixture_literal", "fixture.object")
    return result


def encode_value(value, kind):
    if kind in ("class", "relation"):
        return "<" + _iri(value) + ">"
    if type(value) is bool:
        return ('"true"' if value else '"false"') + "^^<" + XSD_BOOLEAN + ">"
    if type(value) is str:
        return json.dumps(value, ensure_ascii=False)
    _fail("unsupported_fixture_literal", "fixture.value")


def _entity(value, namespace):
    _text(value, "fixture.identity")
    if value == "{payload.target}":
        return {"event_field": "target"}
    # W:E-B01 is an explicitly local identifier in T09 conventions, even though
    # a generic URL parser would consider W a URI scheme.
    full = (
        value if value.startswith((namespace, "urn:", "http://", "https://")) else namespace + value
    )
    if "{" in full or "}" in full:
        return {"event_template": full}
    return _iri(full)


def _property(value, namespace):
    result = _entity(value, namespace)
    if type(result) is not str:
        _fail("invalid_fixture_property", "fixture.property")
    return result


def model_state(model):
    """Decode the actual asserted facts, never copying expected/inferred into them."""
    _shape(
        model,
        (
            "id",
            "fixtureVersion",
            "inputVersion",
            "ruleVersion",
            "behaviorVersion",
            "semanticsVersion",
            "ontology",
            "facts",
            "behaviors",
            "singleValuedPredicates",
            "initialState",
            "constraints",
            "rules",
            "queries",
            "mappings",
            "scenario",
        ),
        location="fixture.model",
    )
    classes, schema = set(), {RDF_TYPE: {"kind": "class", "cardinality": "many"}}
    singles = _list(model["singleValuedPredicates"], "fixture.singleValuedPredicates")
    for triple in _list(model["ontology"], "fixture.ontology"):
        _shape(triple, ("subject", "predicate", "object"), location="fixture.ontology")
        _iri(triple["subject"])
        _iri(triple["predicate"])
        if triple["predicate"] != RDF_TYPE:
            continue
        value = decode_value(triple["object"])
        if value == OWL + "Class":
            classes.add(triple["subject"])
        elif value in (OWL + "DatatypeProperty", OWL + "ObjectProperty"):
            schema[triple["subject"]] = {
                "kind": "literal" if value == OWL + "DatatypeProperty" else "relation",
                "cardinality": "one" if triple["subject"] in singles else "many",
            }
        else:
            _fail("unsupported_fixture_ontology", "fixture.ontology")
    if any(prop not in schema for prop in singles):
        _fail("invalid_fixture_property", "fixture.singleValuedPredicates")
    state = {"objects": [], "facts": [], "notifications": []}
    objects = set()
    for triple in _list(model["facts"], "fixture.facts"):
        fact = decode_fact(triple, schema)
        objects.add(fact["subject"])
        if schema[fact["property"]]["kind"] == "relation":
            objects.add(fact["value"])
        state["facts"].append(fact)
    state["objects"] = sorted(objects)
    return _state(state, schema, sorted(classes)), schema, sorted(classes)


def decode_fact(triple, schema):
    _shape(triple, ("subject", "predicate", "object"), location="fixture.fact")
    prop = _iri(triple["predicate"])
    if prop not in schema:
        _fail("invalid_fixture_property", "fixture.fact")
    value = decode_value(triple["object"])
    if schema[prop]["kind"] in ("relation", "class"):
        if not triple["object"].startswith("<"):
            _fail("invalid_fixture_object_kind", "fixture.fact")
    elif triple["object"].startswith("<"):
        _fail("invalid_fixture_object_kind", "fixture.fact")
    return {"subject": _iri(triple["subject"]), "property": prop, "value": value}


def _condition(source, namespace):
    if type(source) is not dict:
        _fail("invalid_fixture_condition", "fixture.condition")
    if set(source) == {"eventAlarmLevel"}:
        subject, prop, value = (
            {"event_field": "alarmId"},
            namespace + "level",
            source["eventAlarmLevel"],
        )
    elif set(source) == {"eventAlarmStatus"}:
        subject, prop, value = (
            {"event_field": "alarmId"},
            namespace + "status",
            source["eventAlarmStatus"],
        )
    elif set(source) == {"eventEquipmentType"}:
        subject, prop, value = (
            {"event_field": "equipmentId"},
            RDF_TYPE,
            source["eventEquipmentType"],
        )
    elif set(source) == {"target", "type"}:
        subject, prop, value = _entity(source["target"], namespace), RDF_TYPE, source["type"]
    else:
        _shape(source, ("target", "property", "equals"), location="fixture.condition")
        subject = _entity(source["target"], namespace)
        prop, value = _property(source["property"], namespace), source["equals"]
    return {"op": "has", "subject": subject, "property": prop, "value": value}


def compile_behavior(source, namespace, schema):
    _shape(source, ("id", "version", "enabled", "priority", "trigger", "conditions", "actions"))
    _shape(source["trigger"], (), ("eventId", "eventType"), "fixture.trigger")
    trigger = {
        {"eventId": "event_id", "eventType": "event_type"}[key]: value
        for key, value in source["trigger"].items()
    }
    actions = []
    for action in _list(source["actions"], "fixture.actions"):
        kind = action.get("kind") if type(action) is dict else None
        if kind == "create-individual":
            _shape(action, ("kind", "class", "id", "properties"))
            if type(action["properties"]) is not dict:
                _fail("invalid_fixture_properties", "fixture.action")
            initial = [{"property": RDF_TYPE, "value": action["class"]}]
            initial += [
                {"property": _property(prop, namespace), "value": value}
                for prop, value in action["properties"].items()
            ]
            actions.append(
                {"kind": "create", "object": _entity(action["id"], namespace), "initial": initial}
            )
        elif kind == "update-attribute":
            _shape(action, ("kind", "target", "property", "value"))
            value = (
                {"event_field": "value"}
                if action["value"] == "{payload.value}"
                else action["value"]
            )
            actions.append(
                {
                    "kind": "set",
                    "subject": _entity(action["target"], namespace),
                    "property": _property(action["property"], namespace),
                    "value": value,
                }
            )
        elif kind == "add-relation":
            _shape(action, ("kind", "subject", "predicate", "object"))
            prop = _property(action["predicate"], namespace)
            if prop not in schema or schema[prop]["kind"] != "relation":
                _fail("invalid_fixture_property", "fixture.action")
            actions.append(
                {
                    "kind": "set" if schema[prop]["cardinality"] == "one" else "add",
                    "subject": _entity(action["subject"], namespace),
                    "property": prop,
                    "value": _entity(action["object"], namespace),
                }
            )
        elif kind == "notify":
            _shape(action, ("kind", "id", "event"))
            # The core always binds records to the current trigger event. A fixed
            # event association is only valid under that exact eventId trigger.
            if action["event"] != "{eventId}" and action["event"] != source["trigger"].get(
                "eventId"
            ):
                _fail("invalid_fixture_event_binding", "fixture.action")
            actions.append(
                {
                    "kind": "notify",
                    "id": _entity(action["id"], namespace),
                    "message": "固定案例内部通知",
                }
            )
        else:
            _fail("unavailable_fixture_action", "fixture.action")
    conditions = [
        _condition(value, namespace) for value in _list(source["conditions"], "conditions")
    ]
    return {
        "id": source["id"],
        "name": source["id"],
        "description": "T09 固定输入适配",
        "effect": "按固定行为定义生成内部动作计划",
        "version": str(source["version"]),
        "enabled": source["enabled"],
        "priority": source["priority"],
        "trigger": trigger,
        "conditions": conditions or [{"op": "always"}],
        "actions": actions,
    }


def compile_event(source, sequence, namespace, schema):
    _shape(source, ("id", "type", "payload"), location="fixture.event")
    _text(source["id"], "fixture.event.id")
    if "{" in source["id"] or "}" in source["id"]:
        _fail("invalid_fixture_event_identity", "fixture.event.id")
    payload = source["payload"]
    _shape(
        payload,
        (),
        (
            "addFacts",
            "removeAlarm",
            "alarmId",
            "equipmentId",
            "level",
            "status",
            "orderId",
            "target",
            "value",
        ),
        "fixture.event.payload",
    )
    fields = {
        key: value for key, value in payload.items() if key not in ("addFacts", "removeAlarm")
    }
    for name, prefix in (("alarmId", "alarm/"), ("equipmentId", "equipment/"), ("target", "")):
        if name in fields:
            fields[name] = _entity(prefix + _text(fields[name], "fixture.event.payload"), namespace)
    additions = [
        decode_fact(f, schema) for f in _list(payload.get("addFacts", []), "event.addFacts")
    ]
    # Idempotent declarations are stable across repetitions and prior graph state;
    # they do not add invented rdf:type assertions or count as behavior actions.
    objects = {_entity(source["id"], namespace)}
    for fact in additions:
        objects.add(fact["subject"])
        if schema[fact["property"]]["kind"] == "relation":
            objects.add(fact["value"])
    edits = [{"kind": "declare", "object": obj} for obj in sorted(objects)]
    if "removeAlarm" in payload:
        edits.append(
            {
                "kind": "delete_object",
                "object": _entity(
                    "alarm/" + _text(payload["removeAlarm"], "event.removeAlarm"), namespace
                ),
            }
        )
    edits += [
        {"kind": "set" if schema[f["property"]]["cardinality"] == "one" else "add", **f}
        for f in additions
    ]
    return {
        "id": source["id"],
        "type": source["type"],
        "sequence": sequence,
        "version": "T09-event-v1",
        "payload": fields,
        "edits": edits,
    }


def adapt_case(bundle: BaselineBundle, case_id: str, scope: dict, run_id: str) -> dict:
    """Compile one fixed capacity-zero case. No inference, resources or commit."""
    data = bundle.document
    matches = [case for case in data["cases.json"]["cases"] if case["id"] == case_id]
    if len(matches) != 1:
        _fail("unknown_fixture_case", "case.id")
    case = matches[0]
    if case["baseline"] not in ("G-base", "G-behavior"):
        _fail("unsupported_fixture_case", "case.baseline")
    model = data[case["baseline"] + ".json"]
    namespace = _iri(data["conventions.json"]["namespace"])
    for key in ("baselineVersion", "ruleVersion", "behaviorVersion", "semanticsVersion"):
        model_key = "fixtureVersion" if key == "baselineVersion" else key
        if case[key] != model[model_key]:
            _fail("fixture_version_mismatch", "case.version")
    if model["fixtureVersion"] != data["manifest"]["version"]:
        _fail("fixture_version_mismatch", "model.version")
    state, schema, classes = model_state(model)
    behaviors = model["behaviors"]
    for step in case["setup"]:
        if step.get("op") == "remove-alarm":
            _shape(step, ("op", "id"))
            _edit(
                state,
                {"kind": "delete_object", "object": _entity("alarm/" + step["id"], namespace)},
                schema,
                classes,
            )
        elif step.get("op") == "replace-behavior":
            _shape(step, ("op", "definition"))
            definition = step["definition"]
            if not any(b["id"] == definition["id"] for b in behaviors):
                _fail("unknown_fixture_behavior", "case.setup")
            behaviors = [definition if b["id"] == definition["id"] else b for b in behaviors]
        else:
            _fail("unsupported_fixture_setup", "case.setup")
    rounds = [step for step in case["steps"] if step["op"] == "run-round"]
    if len(rounds) != 1 or rounds[0]["capacity"] != 0:
        _fail("pending_round_executor", "case.steps")
    if any(
        step["op"] not in ("run-round", "resubmit-event", "prime-current-inference")
        for step in case["steps"]
    ):
        _fail("pending_round_executor", "case.steps")
    events = [
        compile_event(source, index, namespace, schema)
        for index, source in enumerate(rounds[0]["events"])
    ]
    repeated = [
        compile_event(step["event"], 0, namespace, schema)
        for step in case["steps"]
        if step["op"] == "resubmit-event"
    ]
    request = {
        "scope": scope,
        "run_id": run_id,
        "round": 1,
        "base_revision": model["inputVersion"],
        "assertion_version": case["inputVersion"],
        "ontology_version": _hash(model["ontology"]),
        "rules_version": case["ruleVersion"],
        "behavior_version": case["behaviorVersion"],
        "classes": classes,
        "schema": schema,
        "state": state,
        "behaviors": [compile_behavior(b, namespace, schema) for b in behaviors],
        "events": events,
        "consumption": {"scope": scope, "events": [], "instances": []},
    }
    return {
        "request": request,
        "repeat_events": repeated,
        "namespace": namespace,
        "source": {
            "manifest_sha256": bundle.manifest_sha256,
            "fixture_version": data["manifest"]["version"],
            "case_id": case_id,
            "adapter_version": ADAPTER_VERSION,
            "product_runtime": "not-executed",
        },
    }


def project_candidate(plan, model, namespace, prior_order_ids=None):
    """Whole asserted candidate projection; remains explicitly uncommitted.

    Notify materializes its two RDF statements here as one logical action. This
    is not a second writable graph; only the transaction owner may persist it.
    """
    candidate = plan["candidate"]
    _, schema, _ = model_state(model)
    facts = [
        {
            "subject": f["subject"],
            "predicate": f["property"],
            "object": encode_value(f["value"], schema[f["property"]]["kind"]),
        }
        for f in candidate["facts"]
    ]
    notifications = []
    for record in candidate["notifications"]:
        facts.extend(
            [
                {
                    "subject": record["id"],
                    "predicate": RDF_TYPE,
                    "object": "<" + namespace + "Notification>",
                },
                {
                    "subject": record["id"],
                    "predicate": namespace + "notificationEvent",
                    "object": "<" + _entity(record["event_id"], namespace) + ">",
                },
            ]
        )
        notifications.append(
            {
                "id": record["id"].removeprefix(namespace),
                "eventId": record["event_id"],
                "behaviorId": record["behavior_id"],
            }
        )
    orders = {
        f["subject"]
        for f in candidate["facts"]
        if f["property"] == RDF_TYPE and f["value"] == namespace + "WorkOrder"
    }
    if prior_order_ids is None:
        prior_order_ids = [order["id"] for order in model["initialState"]["orders"]]
    order_sequence = [_entity(identity, namespace) for identity in prior_order_ids]
    order_sequence += [
        t["action"]["object"]
        for t in plan["action_trace"]
        if t["action"]["kind"] == "create" and t["action"]["object"] in orders
    ]
    if set(order_sequence) != orders or len(order_sequence) != len(orders):
        _fail("invalid_fixture_order_projection", "projection.orders")
    projected_orders = []
    for identity in order_sequence:
        states = [
            f["value"]
            for f in candidate["facts"]
            if f["subject"] == identity and f["property"] == namespace + "workOrderStatus"
        ]
        if len(states) != 1:
            _fail("invalid_fixture_order_projection", "projection.orders")
        record = {"id": identity.removeprefix(namespace), "status": states[0]}
        events = [
            f["subject"]
            for f in candidate["facts"]
            if f["property"] == namespace + "eventOrder" and f["value"] == identity
        ]
        if len(events) > 1:
            _fail("invalid_fixture_order_projection", "projection.orders")
        if events:
            record["eventId"] = events[0].removeprefix(namespace)
        projected_orders.append(record)
    return {
        "committed": False,
        "facts": sorted(facts, key=_json),
        "orders": projected_orders,
        "notifications": notifications,
        "actionTrace": [
            {
                "eventId": t["event_id"],
                "behaviorId": t["behavior_id"],
                "actionIndex": t["action_index"] + 1,
            }
            for t in plan["action_trace"]
        ],
        "consumedEvents": [e["event_id"] for e in plan["consumption"]["events"]],
        "triggeredInstances": [
            [e["event_id"], e["behavior_id"]] for e in plan["consumption"]["instances"]
        ],
    }
