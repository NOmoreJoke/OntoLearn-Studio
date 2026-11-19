"""Scenario RDF stages and the adapter for the frozen scalar wire configuration."""

import json
from collections import Counter
from dataclasses import dataclass, replace

from ontolearn_engine.behavior import baseline_adapter
from ontolearn_engine.behavior import service as behavior
from ontolearn_engine.behavior import working_copy as rdf
from ontolearn_engine.behavior.planner import plan_behaviors, prepare_events
from ontolearn_engine.rdf_snapshot import iri
from ontolearn_engine.scenario.model import Alert, State, WorkOrder, create_order
from ontolearn_engine.scenario.runner import Execution, Inference, Plan
from ontolearn_engine.semantic_execution import _term
from ontolearn_engine.storage import canonical, digest

DEFAULT_NAMESPACE = "urn:ontolearn:learning:"
EMPTY_LEDGER = {"events": [], "instances": []}
PENDING = "待处理"
COMPLETED = "已完成"


@dataclass(frozen=True)
class RdfInference(Inference):
    facts: tuple[dict, ...]


def _array(encoded):
    value = json.loads(encoded)
    if value == {}:
        return []
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError("Expected an array of isolated definitions or edits")
    return value


def _items(encoded):
    return json.loads(encoded).get("items", [])


def configured_items(parameters, key):
    return {"items": _array(parameters.get(key, "[]"))}


class ScenarioCopy:
    def __init__(self, state, definition, configuration):
        self.definition = definition
        self.classes, self.schema = behavior._ontology_material(state)
        self.project_facts = rdf.asserted_facts(state)
        self.reasoner = rdf.Reasoner(state, _items(definition.rules))
        self.behaviors = _items(definition.behaviors)
        self.namespace = configuration["parameters"].get("namespace", DEFAULT_NAMESPACE)
        iri(self.namespace + "Alarm")
        self.scope = {
            "project_id": definition.project_id,
            "scenario_id": definition.scenario_id,
            "mode": "scenario",
        }
        self.versions = {
            "assertionVersion": definition.input_version,
            "behaviorVersion": definition.behavior_version,
            "ontologyVersion": self.reasoner.ontology_version,
            "rulesVersion": self.reasoner.rules_version,
        }

    def read(self, state):
        data = json.loads(state.assertions)
        if "facts" in data:
            return data
        # Older E.3 checkpoints had queue and alert state only.
        return {
            "facts": self.project_facts,
            "objects": [],
            "notifications": [],
            "consumption": EMPTY_LEDGER,
            "orderIris": {},
        }

    def initial(self, edits):
        state = State()
        data = self.read(state)
        if edits:
            event = {
                "id": "initial-edits",
                "type": "initial-edits",
                "sequence": 0,
                "version": "1",
                "payload": {},
                "edits": [behavior._lower_edit(edit) for edit in edits],
            }
            data, _ = self.prepare(data, [event], (), 1, "initial")
        orders = rdf.work_orders(data["facts"], self.namespace)
        data["orderIris"] = {order["id"]: order["iri"] for order in orders}
        return State(
            orders=tuple(
                WorkOrder(
                    order["id"], order["eventId"], 0, index, self._order_status(order["status"])
                )
                for index, order in enumerate(orders, 1)
            ),
            alerts=self.alerts(data["facts"]),
            assertions=canonical(data),
        )

    def alerts(self, facts, legacy=()):
        namespace = self.namespace
        alarms, fields = set(), {}
        for fact in facts:
            subject, prop, value = fact["subject"], fact["predicate"], fact["object"]
            if (prop, value) == (rdf.RDF_TYPE, f"<{namespace}Alarm>"):
                alarms.add(subject)
            elif prop in (namespace + "level", namespace + "status"):
                fields.setdefault(subject, {}).setdefault(prop, []).append(str(_term(value)))
        alerts = {alert.id: alert for alert in legacy}
        for key in sorted(alarms):
            record = fields.get(key, {})
            levels, statuses = (
                record.get(namespace + "level", []),
                record.get(namespace + "status", []),
            )
            if len(levels) > 1 or len(statuses) > 1:
                raise ValueError("Ambiguous alarm state")
            severity, status = next(iter(levels), ""), next(iter(statuses), "")
            alerts[key] = Alert(key, severity, status)
        return tuple(alerts.values())

    def _event(self, event, payload):
        namespace = self.namespace
        source = dict(payload)
        event_type = source.pop("type", source.get("kind", "event"))
        version = str(source.pop("version", "1"))
        edits = [behavior._lower_edit(edit) for edit in _array(source.pop("edits", "[]"))]
        adds = _array(source.pop("addFacts", "[]"))
        if set(source) & set(behavior.RESERVED_PAYLOAD_KEYS):
            raise ValueError("Reserved scenario event payload")
        if namespace + "Alarm" in self.classes:
            # Allow either explicit edits or the structured alarm event fields.
            for key, prefix in (
                ("alarmId", "alarm/"),
                ("equipmentId", "equipment/"),
                ("orderId", ""),
            ):
                if key in source:
                    source[key] = (
                        baseline_adapter._entity(source[key], namespace)
                        if key == "orderId"
                        else (
                            source[key]
                            if source[key].startswith(("urn:", "http://", "https://"))
                            else namespace + prefix + source[key]
                        )
                    )
                    iri(source[key])
            if (
                not adds
                and not edits
                and all(key in source for key in ("alarmId", "level", "status"))
            ):
                alarm = source["alarmId"]
                adds = [
                    rdf.triple(alarm, rdf.RDF_TYPE, f"<{namespace}Alarm>"),
                    rdf.triple(alarm, namespace + "level", canonical(source["level"])),
                    rdf.triple(alarm, namespace + "status", canonical(source["status"])),
                ]
                if "equipmentId" in source:
                    adds.append(
                        rdf.triple(source["equipmentId"], namespace + "alarm", f"<{alarm}>")
                    )
        remove_alarm = source.pop("removeAlarm", None)
        if remove_alarm is not None:
            identity = (
                remove_alarm
                if remove_alarm.startswith(("urn:", "http://", "https://"))
                else namespace + "alarm/" + remove_alarm
            )
            edits.append({"kind": "delete_object", "object": identity})
        objects = {baseline_adapter._entity(event.id, namespace)}
        for fact in adds:
            projected = baseline_adapter.decode_fact(fact, self.schema)
            property_ = projected["property"]
            objects.add(projected["subject"])
            if self.schema[property_]["kind"] == "relation":
                objects.add(projected["value"])
            kind = "set" if self.schema[property_]["cardinality"] == "one" else "add"
            edits.append({"kind": kind, **projected})
        return {
            "id": event.id,
            "type": event_type,
            "sequence": event.sequence,
            "version": version,
            "payload": {key: value for key, value in source.items() if value is not None},
            "edits": [{"kind": "declare", "object": obj} for obj in sorted(objects)] + edits,
        }

    def prepare(self, data, events, behaviors, number, run_id):
        state, _ = rdf.planner_state(
            data["facts"],
            self.schema,
            self.classes,
            objects=data["objects"],
            notifications=data["notifications"],
        )
        ledger = {key: data["consumption"][key] for key in EMPTY_LEDGER}
        prepared = prepare_events(
            rdf.plan_request(
                self.scope,
                run_id,
                number,
                self.definition.project_version,
                self.versions,
                self.classes,
                self.schema,
                state,
                list(behaviors),
                events,
                ledger,
            )
        )
        applied = prepared.reasoning_input["state"]
        return {
            **data,
            "facts": rdf.apply_planner_delta(
                data["facts"], state, applied, self.schema, self.classes
            ),
            "objects": applied["objects"],
        }, prepared

    def apply_events(self, state, events, context, check):
        check()
        self.current_events = events
        data = self.read(state)
        payloads = [json.loads(event.payload) for event in events]
        known_alarms = self.namespace + "Alarm" in self.classes
        legacy = {alert.id: alert for alert in state.alerts} if not known_alarms else {}
        for payload in payloads:
            if not known_alarms and all(key in payload for key in ("alarmId", "level", "status")):
                alert = Alert(*(str(payload[key]) for key in ("alarmId", "level", "status")))
                legacy[alert.id] = alert
        inputs = [
            self._event(event, payload) for event, payload in zip(events, payloads, strict=True)
        ]
        event_ids = {event.id for event in self.definition.events} | {event.id for event in events}
        behaviors = [
            behavior._lower_draft(item, self.schema, self.classes, event_ids)
            if "name" in item
            else baseline_adapter.compile_behavior(item, self.namespace, self.schema)
            for item in self.behaviors
        ]
        # Older E.3 payloads can carry arbitrary scalars and need no planner state.
        if behaviors or any(
            edit["kind"] != "declare" for event in inputs for edit in event["edits"]
        ):
            data, self.prepared = self.prepare(data, inputs, behaviors, context.round, self.run_id)
        else:
            self.prepared = None
        return replace(
            state, assertions=canonical(data), alerts=self.alerts(data["facts"], legacy.values())
        )

    def infer(self, state, definition, context, check):
        check()
        facts, version = self.reasoner.infer(self.read(state)["facts"])
        return RdfInference(state, definition.rule_version, version, context, tuple(facts))

    def plan(self, state, inference, events, context, check):
        check()
        if self.prepared is None:
            return Plan(0, "{}", ())
        projection, facts = rdf.planner_state(
            [], self.schema, self.classes, inferred=inference.facts
        )
        planned = plan_behaviors(
            self.prepared,
            rdf.reasoning_input(self.prepared, inference.snapshot, facts),
            inferred_objects=projection["objects"],
        )
        # The next stage consumes exactly this validated candidate and its trace.
        trace = tuple(
            (item["eventId"], item["behaviorId"], item["actionIndex"])
            for item in rdf.action_trace(planned)
        )
        return Plan(len(trace), canonical(planned), trace)

    @staticmethod
    def plan_digest(payload):
        planned = json.loads(payload)
        return digest([planned.get("action_trace", []), planned.get("candidate")])

    @staticmethod
    def _order_status(status):
        return {PENDING: "pending", COMPLETED: "completed"}[status]

    def execute(self, state, plan, context, check):
        check()
        data = self.read(state)
        planned = json.loads(plan.payload)
        if planned:
            candidate = planned["candidate"]
            data["facts"] = rdf.apply_planner_delta(
                data["facts"], planned["after_events"], candidate, self.schema, self.classes
            )
            data["objects"] = candidate["objects"]
            data["notifications"] = candidate["notifications"]
            data["consumption"] = planned["consumption"]
        state = self._sync_orders(state, data, planned, context.round)
        if not self.behaviors:
            for event in self.current_events:
                state = create_order(state, event.id, context.round)
        return Execution(replace(state, assertions=canonical(data)), plan.action_count)

    def _sync_orders(self, state, data, planned, round_number):
        """Reconcile the resource queue with the RDF after events and actions."""
        rdf_orders = {item["iri"]: item for item in rdf.work_orders(data["facts"], self.namespace)}
        existing, identities = [], {}
        for order in state.orders:
            identity = data["orderIris"].get(order.id)
            if identity is None:
                existing.append(order)  # Queues predating RDF and legacy E.3 orders.
                continue
            current = rdf_orders.pop(identity, None)
            if current is None:
                continue  # The RDF no longer contains the linked work order.
            if current["eventId"] != order.event_id:
                raise ValueError("Work order event changed")
            existing.append(replace(order, status=self._order_status(current["status"])))
            identities[order.id] = identity
        state = replace(state, orders=tuple(existing))

        actions = {
            item["action"]["object"]: index
            for index, item in enumerate(planned.get("action_trace", []))
            if item["action"]["kind"] == "create"
        }
        events = {
            event.id.removeprefix(self.namespace): index
            for index, event in enumerate(self.current_events)
        }

        def creation_order(order):
            identity = order["iri"]
            if identity in actions:
                return (1, actions[identity], identity)
            return (0, events.get(order["eventId"], len(events)), identity)

        history = {event_id for event_id, _, _ in state.created_orders}
        for order in sorted(rdf_orders.values(), key=creation_order):
            if order["eventId"] in history:
                raise ValueError("Duplicate work order event")
            entry = WorkOrder(
                order["id"],
                order["eventId"],
                round_number,
                state.order_sequence + 1,
                self._order_status(order["status"]),
            )
            state = replace(state, orders=(*state.orders, entry))
            history.add(order["eventId"])
            identities[order["id"]] = order["iri"]
        data["orderIris"] = identities
        return state

    def finalize_resources(self, state):
        data = self.read(state)
        if not data["orderIris"] and self.namespace + "Alarm" not in self.classes:
            return state
        statuses = {
            data["orderIris"][order.id]: COMPLETED if order.status == "completed" else PENDING
            for order in state.orders
            if order.id in data["orderIris"]
        }
        predicate = self.namespace + "workOrderStatus"
        data["facts"] = rdf.sorted_facts(
            [
                fact
                for fact in data["facts"]
                if fact["predicate"] != predicate or fact["subject"] not in statuses
            ]
            + [
                rdf.triple(identity, predicate, canonical(status))
                for identity, status in statuses.items()
            ]
        )
        alerts = self.alerts(
            data["facts"], () if self.namespace + "Alarm" in self.classes else state.alerts
        )
        return replace(state, assertions=canonical(data), alerts=alerts)

    def round_evidence(self, record):
        checkpoint = record.checkpoint
        data = self.read(checkpoint.state)
        known, consumed = {event.id: event for event in checkpoint.events}, set(checkpoint.consumed)
        pending = sorted(
            (event for event in checkpoint.events if event.id not in consumed),
            key=lambda event: (event.round, event.sequence, event.id),
        )
        orders = [
            {
                "id": order.id,
                "eventId": order.event_id,
                "status": COMPLETED if order.status == "completed" else PENDING,
                "createdRound": order.created_round,
                "createdSequence": known[order.event_id].sequence
                if order.event_id in known
                else order.sequence,
            }
            for order in checkpoint.state.orders
        ]
        orders_per_event = Counter(order["eventId"] for order in orders)
        return {
            "facts": data["facts"],
            "inferred": list(record.end_inference.facts),
            "pendingEvents": [event.id for event in pending if event.round <= checkpoint.round],
            "scheduledFutureEvents": [
                event.id for event in pending if event.round > checkpoint.round
            ],
            "actionTrace": [
                {"eventId": event_id, "behaviorId": behavior_id, "actionIndex": index}
                for event_id, behavior_id, index in record.trace
            ],
            "triggeredInstances": [
                [item["event_id"], item["behavior_id"]] for item in data["consumption"]["instances"]
            ],
            "orders": orders,
            "duplicateOrders": sorted(
                order["id"] for order in orders if orders_per_event[order["eventId"]] > 1
            ),
        }
