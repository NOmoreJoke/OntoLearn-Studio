"""RDF and planner projections shared by the isolated sample and sandbox owners."""

from itertools import chain

from rdflib import Literal, URIRef

from ontolearn_engine import semantic
from ontolearn_engine.quality.rule_profile import PROFILE
from ontolearn_engine.rdf_snapshot import iri
from ontolearn_engine.semantic_execution import _definitions, _formal_specs, _graph, _rules, _term
from ontolearn_engine.storage import canonical, digest

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


def triple(subject, predicate, obj):
    return {"subject": subject, "predicate": predicate, "object": obj}


def sorted_facts(facts):
    return sorted({canonical(fact): fact for fact in facts}.values(), key=canonical)


def asserted_facts(state):
    return sorted_facts(
        triple(fact["subject"], fact["predicate"], fact["object"])
        for fact in state["facts"]
        if fact["object"] is not None
    )


def _controlled_rule(value):
    # The versioned baseline format is another encoding of the legacy one-head
    # controlled language. Both project and scenario rules use the same compiler.
    if "conditions" not in value or value.get("kind") == "rule":
        return value
    if value["inputScope"] != "asserted-plus-rdfs" or value["outputReentry"] is not False:
        raise ValueError("Unsupported isolated rule scope")
    conclusions = value["conclusions"]
    if len(conclusions) != 1:
        raise ValueError("Unsupported isolated rule conclusion count")

    def pattern(entry):
        predicate = entry["predicate"]
        return [
            entry["subject"],
            predicate if predicate.startswith("?") else iri(predicate).n3(),
            entry["object"],
        ]

    return {
        "enabled": value["enabled"],
        "when": [pattern(entry) for entry in value["conditions"]],
        "then": pattern(conclusions[0]),
    }


class Reasoner:
    """Compile the frozen project catalog with the same rule engines as reasoning.execute."""

    def __init__(self, state, configured_rules=()):
        definitions = _definitions({"state": state})
        self.ontology_version = digest(
            [record for record in state["definitions"] if record["layer"] == "ontology"]
        )
        self.ontology = _graph(
            fact
            for (layer, _), value in sorted(definitions.items())
            if layer == "ontology"
            for fact in value["triples"]
            if (fact["predicate"], fact["object"])
            != (
                RDF_TYPE,
                "<http://www.w3.org/2002/07/owl#FunctionalProperty>",
            )  # Cardinality metadata belongs to the planner, not the RDFS graph.
        )
        saved_rules = [
            (identity, value)
            for (layer, identity), value in sorted(definitions.items())
            if layer == "rule"
        ]
        self.rules_version = digest([saved_rules, configured_rules])
        for identity, value in saved_rules:
            definitions["rule", identity] = _controlled_rule(value)
        for rule in configured_rules:
            key = ("rule", rule["id"])
            value = _controlled_rule(rule)
            if key in definitions and definitions[key] != value:
                raise ValueError("Conflicting isolated rule definition")
            definitions[key] = value
        legacy = _rules(definitions)
        specs, formal = _formal_specs(definitions)
        self.rules = specs if formal else legacy
        self.profile = PROFILE if formal else None

    def infer(self, facts):
        graph = _graph(facts) + self.ontology
        output = semantic.reason(graph, self.rules, profile=self.profile)
        asserted = set(map(semantic._key, graph))
        inferred = sorted_facts(
            triple(sub[1:-1], prop[1:-1], obj)
            for sub, prop, obj in set(map(tuple, output["rdfs"] + output["rules"])) - asserted
        )
        version = digest(
            [
                self.ontology_version,
                self.rules_version,
                self.profile or semantic.SEMANTICS_VERSION,
                facts,
                inferred,
            ]
        )
        return inferred, version


def _planner_fact(fact, schema, classes, *, derived=False):
    prop = fact["predicate"]
    if prop not in schema:
        return None
    obj = _term(fact["object"])
    kind = schema[prop]["kind"]
    if kind == "class" and derived and str(obj) not in classes:
        return None  # RDFS may derive built-in types outside the behavior catalog.
    if kind in ("class", "relation") and isinstance(obj, URIRef):
        value = str(obj)
    elif kind == "literal" and isinstance(obj, Literal) and not obj.language:
        value = obj.value
    else:
        raise ValueError("Unsupported planner RDF value")
    if type(value) not in (str, bool, int, float):
        raise ValueError("Unsupported planner RDF scalar")
    return {"subject": fact["subject"], "property": prop, "value": value}


def planner_state(facts, schema, classes, *, objects=(), notifications=(), inferred=()):
    projected = [_planner_fact(fact, schema, classes) for fact in facts]
    proofs = [_planner_fact(fact, schema, classes, derived=True) for fact in inferred]
    objects = set(objects)
    for fact in chain(facts, inferred):
        objects.add(fact["subject"])
        if fact["predicate"] != RDF_TYPE and fact["object"].startswith("<"):
            objects.add(fact["object"][1:-1])
    return (
        {
            "objects": sorted(objects),
            "facts": sorted_facts(fact for fact in projected if fact is not None),
            "notifications": list(notifications),
        },
        sorted_facts(fact for fact in proofs if fact is not None),
    )


def apply_planner_delta(facts, before, after, schema, classes):
    """Preserve original RDF spelling and facts outside the planner vocabulary."""
    remaining = {canonical(fact) for fact in after["facts"]}
    previous = {canonical(fact) for fact in before["facts"]}
    deleted = set(before["objects"]) - set(after["objects"])
    deleted_iris = {f"<{obj}>" for obj in deleted}
    saved = []
    for fact in facts:
        if fact["subject"] in deleted or fact["object"] in deleted_iris:
            continue
        projected = _planner_fact(fact, schema, classes)
        if projected is None or canonical(projected) in remaining:
            saved.append(fact)
    for fact in after["facts"]:
        if canonical(fact) in previous:
            continue
        kind = schema[fact["property"]]["kind"]
        obj = iri(fact["value"]) if kind in ("class", "relation") else Literal(fact["value"])
        saved.append(triple(fact["subject"], fact["property"], obj.n3()))
    return sorted_facts(saved)


def work_orders(facts, namespace):
    """Read the E.3 projection from actual RDF assertions."""
    orders, status, events = set(), {}, {}
    for fact in facts:
        subject, prop, obj = fact["subject"], fact["predicate"], fact["object"]
        if (prop, obj) == (RDF_TYPE, f"<{namespace}WorkOrder>"):
            orders.add(subject)
        elif prop == namespace + "workOrderStatus":
            status.setdefault(subject, []).append(str(_term(obj)))
        elif prop == namespace + "eventOrder" and obj.startswith("<"):
            events.setdefault(obj[1:-1], []).append(subject.removeprefix(namespace))
    return [
        {
            "id": identity.removeprefix(namespace),
            "iri": identity,
            "status": status[identity][0],
            "eventId": events[identity][0],
        }
        for identity in sorted(orders)
        if len(status.get(identity, ())) == len(events.get(identity, ())) == 1
    ]


def action_trace(plan):
    return [
        {
            "eventId": item["event_id"],
            "behaviorId": item["behavior_id"],
            "actionIndex": item["action_index"] + 1,
        }
        for item in plan["action_trace"]
    ]


def reasoning_input(prepared, version, facts):
    inputs = prepared.reasoning_input
    return {
        **{key: value for key, value in inputs.items() if key != "state"},
        "version": version,
        "status": "current",
        "facts": facts,
    }


def plan_request(
    scope,
    run_id,
    round_number,
    revision,
    versions,
    classes,
    schema,
    state,
    behaviors,
    events,
    ledger,
):
    return {
        "scope": scope,
        "run_id": run_id,
        "round": round_number,
        "base_revision": str(revision),
        "assertion_version": versions["assertionVersion"],
        "ontology_version": versions["ontologyVersion"],
        "rules_version": versions["rulesVersion"],
        "behavior_version": versions["behaviorVersion"],
        "classes": classes,
        "schema": schema,
        "state": state,
        "behaviors": behaviors,
        "events": events,
        "consumption": {"scope": scope, **ledger},
    }
