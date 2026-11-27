"""Private immutable scenario values; not an IPC contract or a writable store."""

import hashlib
import json
from dataclasses import asdict, dataclass, replace

SEMANTICS = "scenario-e2-v1"


def canonical(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def json_object(text: str) -> None:
    if not isinstance(text, str) or not isinstance(json.loads(text), dict):
        raise ValueError("Scenario payload must be a JSON object")
    canonical(json.loads(text))


def integer(value: int, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise ValueError("Invalid scenario integer")


@dataclass(frozen=True)
class Capacity:
    direct: int | None = None
    people: int | None = None
    per_person: int | None = None

    def __post_init__(self) -> None:
        direct = self.direct is not None
        product = self.people is not None and self.per_person is not None
        if direct == product or (
            direct and (self.people is not None or self.per_person is not None)
        ):
            raise ValueError("Choose exactly one capacity mode")
        for value in (self.direct, self.people, self.per_person):
            if value is not None:
                integer(value)

    @property
    def count(self) -> int:
        if self.direct is not None:
            return self.direct
        assert self.people is not None and self.per_person is not None
        return self.people * self.per_person


@dataclass(frozen=True)
class Event:
    id: str
    round: int
    sequence: int
    payload: str = "{}"

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Event ID required")
        integer(self.round, 1)
        integer(self.sequence)
        json_object(self.payload)


@dataclass(frozen=True)
class WorkOrder:
    id: str
    event_id: str
    created_round: int
    sequence: int
    status: str = "pending"

    def __post_init__(self) -> None:
        if not self.id or not self.event_id or self.status not in {"pending", "completed"}:
            raise ValueError("Invalid work order")
        integer(self.created_round)
        integer(self.sequence)


@dataclass(frozen=True)
class Alert:
    id: str
    severity: str
    status: str


@dataclass(frozen=True)
class State:
    orders: tuple[WorkOrder, ...] = ()
    alerts: tuple[Alert, ...] = ()
    assertions: str = "{}"
    order_sequence: int = 0
    created_orders: tuple[tuple[str, str, int], ...] = ()

    def __post_init__(self) -> None:
        json_object(self.assertions)
        if not isinstance(self.orders, tuple) or not isinstance(self.alerts, tuple):
            raise ValueError("State collections must be immutable tuples")
        integer(self.order_sequence)
        if not isinstance(self.created_orders, tuple):
            raise ValueError("Immutable order identity history required")
        ledger = {event: (identity, sequence) for event, identity, sequence in self.created_orders}
        if len(ledger) != len(self.created_orders):
            raise ValueError("Duplicate order creation event")
        for order in self.orders:
            entry = (order.id, order.sequence)
            if order.event_id in ledger and ledger[order.event_id] != entry:
                raise ValueError("Order creation identity changed")
            ledger[order.event_id] = entry
        if len({identity for identity, _ in ledger.values()}) != len(ledger):
            raise ValueError("Order ID reused by another event")
        for identity, sequence in ledger.values():
            if not identity:
                raise ValueError("Invalid historical order identity")
            integer(sequence)
        object.__setattr__(
            self,
            "created_orders",
            tuple((event, identity, sequence) for event, (identity, sequence) in ledger.items()),
        )
        object.__setattr__(
            self,
            "order_sequence",
            max(self.order_sequence, *(sequence for _, sequence in ledger.values()), 0),
        )
        for values in (self.orders, self.alerts):
            if len({item.id for item in values}) != len(values):
                raise ValueError("Duplicate scenario identity")


def create_order(state: State, event_id: str, round_number: int) -> State:
    """E.3 stable IDs, independent of run UUID; retries of an event are idempotent."""
    if any(event == event_id for event, _, _ in state.created_orders):
        return state
    sequence = state.order_sequence + 1
    identity = f"W{sequence:03}"
    if any(saved_id == identity for _, saved_id, _ in state.created_orders):
        raise ValueError("Work order identity collision")
    return replace(
        state, orders=(*state.orders, WorkOrder(identity, event_id, round_number, sequence))
    )


def resource_stage(state: State, capacity: Capacity) -> tuple[State, tuple[str, ...]]:
    queue = sorted(
        (order for order in state.orders if order.status != "completed"),
        key=lambda order: (order.created_round, order.sequence, order.id),
    )
    selected = tuple(order.id for order in queue[: capacity.count])
    identities = set(selected)
    return replace(
        state,
        orders=tuple(
            replace(order, status="completed") if order.id in identities else order
            for order in state.orders
        ),
    ), selected


@dataclass(frozen=True)
class Metrics:
    backlog: int
    completed: int
    open_high_alerts: int


def metrics(state: State, completed: tuple[str, ...]) -> Metrics:
    return Metrics(
        sum(order.status != "completed" for order in state.orders),
        len(set(completed)),
        sum(alert.severity == "High" and alert.status != "Closed" for alert in state.alerts),
    )


@dataclass(frozen=True)
class Definition:
    project_id: str
    engine_version: str
    dependency_lock_hash: str
    project_version: str
    scenario_id: str
    input_version: str
    rule_version: str
    behavior_version: str
    max_rounds: int
    capacity: Capacity
    events: tuple[Event, ...]
    initial: State = State()
    rules: str = "{}"
    behaviors: str = "{}"
    parameters: str = "{}"
    source: str = ""
    assumptions: tuple[str, ...] = ()
    semantics: str = SEMANTICS
    initial_consumed: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        integer(self.max_rounds, 1)
        if self.max_rounds > 1000 or self.semantics != SEMANTICS:
            raise ValueError("Unsupported round limit or scenario semantics")
        if not all(
            (
                self.project_id,
                self.engine_version,
                self.dependency_lock_hash,
                self.project_version,
                self.scenario_id,
                self.input_version,
                self.rule_version,
                self.behavior_version,
            )
        ):
            raise ValueError("Scenario versions required")
        for text in (self.rules, self.behaviors, self.parameters):
            json_object(text)
        if not isinstance(self.events, tuple) or not isinstance(self.initial_consumed, tuple):
            raise ValueError("Immutable event inputs required")
        catalog = event_catalog(self.events)
        if len(set(self.initial_consumed)) != len(self.initial_consumed) or not set(
            self.initial_consumed
        ) <= set(catalog):
            raise ValueError("Invalid initial consumption")

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical(asdict(self)).encode()).hexdigest()


def event_catalog(events: tuple[Event, ...]) -> dict[str, Event]:
    catalog: dict[str, Event] = {}
    for event in events:
        if event.id in catalog and event != catalog[event.id]:
            raise ValueError("Event ID reused with different content")
        catalog.setdefault(event.id, event)
    return catalog


def copy_scenario(source: Definition, scenario_id: str, input_version: str) -> Definition:
    if scenario_id == source.scenario_id or not scenario_id or not input_version:
        raise ValueError("New scenario identity required")
    return replace(source, scenario_id=scenario_id, input_version=input_version)
