"""E.2 orchestration only. Real inference/behavior/atomic storage are required ports.

This module performs no persistence and never registers a product capability.
Test ports are orchestration probes, not integrated domain execution evidence.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from .model import (
    Definition,
    Event,
    Metrics,
    State,
    event_catalog,
    json_object,
    metrics,
    resource_stage,
)


class Cancelled(Exception):
    pass


class ScenarioFailure(Exception):
    """Restricted internal error; no source value/path/exception text is exposed."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class Context:
    round: int
    phase: str


@dataclass(frozen=True)
class Inference:
    input_state: State
    rule_version: str
    snapshot: str
    context: Context


@dataclass(frozen=True)
class Plan:
    action_count: int
    payload: str
    trace: tuple[tuple[str, str, int], ...]


@dataclass(frozen=True)
class Execution:
    state: State
    action_count: int
    generated: tuple[Event, ...] = ()


@dataclass(frozen=True)
class Checkpoint:
    definition_digest: str
    round: int
    state: State
    events: tuple[Event, ...]
    consumed: tuple[str, ...]
    completed: tuple[str, ...]


@dataclass(frozen=True)
class Round:
    checkpoint: Checkpoint
    input_events: tuple[str, ...]
    created: tuple[str, ...]
    resource_completed: tuple[str, ...]
    backlog: tuple[str, ...]
    metrics: Metrics
    before_inference: Inference
    end_inference: Inference
    trace: tuple[tuple[str, str, int], ...]
    frozen_plan: str


@dataclass(frozen=True)
class Result:
    definition: Definition
    status: str
    checkpoint: Checkpoint
    rounds: tuple[Round, ...]
    pending: tuple[Event, ...]
    error_code: str | None = None

    @property
    def has_unprocessed_events(self) -> bool:
        return bool(self.pending)


class Ports(Protocol):
    def apply_events(
        self, state: State, events: tuple[Event, ...], context: Context, check: Callable
    ) -> State: ...

    def infer(
        self, state: State, definition: Definition, context: Context, check: Callable
    ) -> Inference: ...

    def plan(
        self,
        state: State,
        inference: Inference,
        events: tuple[Event, ...],
        context: Context,
        check: Callable,
    ) -> Plan:
        """Freeze all conditions; validate conflicts and stable E.1 order before returning."""
        ...

    def execute(self, state: State, plan: Plan, context: Context, check: Callable) -> Execution:
        """Check cancellation between actions; perform exactly the frozen plan."""
        ...

    def commit(self, record: Round, check: Callable) -> None:
        """Owner atomically checks cancel/job identity and persists the full round.

        Return only after durable success. On uncertain acknowledgment reconcile by
        operationId; do not throw after a successful commit or replay side effects.
        """
        ...


def _inference(
    value: Inference, state: State, definition: Definition, context: Context
) -> Inference:
    if (
        value.input_state != state
        or value.rule_version != definition.rule_version
        or value.context != context
        or not value.snapshot
    ):
        raise ScenarioFailure("INFERENCE_IDENTITY")
    return value


def _initial(definition: Definition) -> Checkpoint:
    return Checkpoint(
        definition.digest,
        0,
        definition.initial,
        tuple(event_catalog(definition.events).values()),
        definition.initial_consumed,
        (),
    )


def _validate_resume(definition: Definition, checkpoint: Checkpoint) -> None:
    if checkpoint.definition_digest != definition.digest or type(checkpoint.round) is not int:
        raise ValueError("Snapshot belongs to another input/configuration")
    if not 0 <= checkpoint.round <= definition.max_rounds:
        raise ValueError("Invalid snapshot round")
    catalog = event_catalog(checkpoint.events)
    if not set(checkpoint.consumed) <= set(catalog) or len(set(checkpoint.consumed)) != len(
        checkpoint.consumed
    ):
        raise ValueError("Invalid snapshot consumption")
    for identity, event in event_catalog(definition.events).items():
        if catalog.get(identity) != event:
            raise ValueError("Snapshot input mismatch")
    initial = set(definition.initial_consumed)
    if any(
        catalog[identity].round > checkpoint.round
        for identity in set(checkpoint.consumed) - initial
    ):
        raise ValueError("Snapshot consumed a future event")
    if any(
        event.round <= checkpoint.round and event.id not in checkpoint.consumed
        for event in catalog.values()
    ):
        raise ValueError("Snapshot lost committed event consumption")
    if len(set(checkpoint.completed)) != len(checkpoint.completed):
        raise ValueError("Duplicate completion history")
    if not set(checkpoint.completed) <= {
        identity for _, identity, _ in checkpoint.state.created_orders
    }:
        raise ValueError("Unknown completed order")
    if not set(definition.initial_consumed) <= set(checkpoint.consumed):
        raise ValueError("Snapshot lost initial consumption")


def run(
    definition: Definition,
    ports: Ports,
    *,
    cancelled: Callable[[], bool] = lambda: False,
    resume: Checkpoint | None = None,
    finalize_resources: Callable[[State], State] = lambda state: state,
) -> Result:
    """Independent replay starts at original consumption; resume is always explicit.

    Each call needs a new persisted run/job from the owner. Resumed committed history
    belongs to the source run and is not copied or rewritten by this pure service.
    """
    checkpoint = resume if resume is not None else _initial(definition)
    _validate_resume(definition, checkpoint)
    history: list[Round] = []

    def check() -> None:
        if cancelled():
            raise Cancelled

    def result(status: str, code: str | None = None) -> Result:
        pending = tuple(
            event for event in checkpoint.events if event.id not in set(checkpoint.consumed)
        )
        return Result(definition, status, checkpoint, tuple(history), pending, code)

    try:
        check()
        # Even an empty initial scene must receive actual behavior-before inference.
        initial_context = Context(checkpoint.round, "initial")
        _inference(
            ports.infer(checkpoint.state, definition, initial_context, check),
            checkpoint.state,
            definition,
            initial_context,
        )
        check()
        for number in range(checkpoint.round + 1, definition.max_rounds + 1):
            catalog = event_catalog(checkpoint.events)
            events = tuple(
                sorted(
                    (
                        event
                        for event in catalog.values()
                        if event.round <= number and event.id not in set(checkpoint.consumed)
                    ),
                    key=lambda event: (event.sequence, event.id),
                )
            )
            check()
            applied = ports.apply_events(checkpoint.state, events, Context(number, "events"), check)
            check()
            before_context = Context(number, "before")
            before = _inference(
                ports.infer(applied, definition, before_context, check),
                applied,
                definition,
                before_context,
            )
            check()
            plan = ports.plan(applied, before, events, Context(number, "behavior"), check)
            if type(plan.action_count) is not int or not 0 <= plan.action_count <= 1000:
                raise ScenarioFailure("ACTION_LIMIT")
            json_object(plan.payload)
            if len(plan.trace) != plan.action_count or len(set(plan.trace)) != len(plan.trace):
                raise ScenarioFailure("ACTION_TRACE")
            for event_id, behavior_id, action_index in plan.trace:
                if (
                    event_id not in {event.id for event in events}
                    or not behavior_id
                    or type(action_index) is not int
                    or action_index < 1
                ):
                    raise ScenarioFailure("ACTION_TRACE")
            check()
            executed = ports.execute(applied, plan, Context(number, "behavior"), check)
            if type(executed.action_count) is not int or executed.action_count != plan.action_count:
                raise ScenarioFailure("ACTION_COUNT")
            check()
            for event in executed.generated:
                if event.round != number + 1:
                    raise ScenarioFailure("GENERATED_EVENT_ROUND")
            # Keep the complete catalog, including consumed payloads, to detect ID reuse.
            combined = event_catalog((*checkpoint.events, *executed.generated))
            state, completed_now = resource_stage(executed.state, definition.capacity)
            state = finalize_resources(state)
            check()
            end_context = Context(number, "end")
            end = _inference(
                ports.infer(state, definition, end_context, check), state, definition, end_context
            )
            check()
            previous_completed = {o.id for o in checkpoint.state.orders if o.status == "completed"}
            completed = tuple(
                dict.fromkeys(
                    (
                        *checkpoint.completed,
                        *(
                            o.id
                            for o in state.orders
                            if o.status == "completed" and o.id not in previous_completed
                        ),
                    )
                )
            )
            next_checkpoint = Checkpoint(
                definition.digest,
                number,
                state,
                tuple(combined.values()),
                (*checkpoint.consumed, *(event.id for event in events)),
                completed,
            )
            old_ids = {o.id for o in checkpoint.state.orders}
            backlog = tuple(
                o.id
                for o in sorted(state.orders, key=lambda o: (o.created_round, o.sequence, o.id))
                if o.status != "completed"
            )
            record = Round(
                next_checkpoint,
                tuple(event.id for event in events),
                tuple(o.id for o in state.orders if o.id not in old_ids),
                completed_now,
                backlog,
                metrics(state, completed),
                before,
                end,
                plan.trace,
                plan.payload,
            )
            check()
            ports.commit(record, check)
            # No cancellation checkpoint here: a durable commit must stay visible.
            checkpoint = next_checkpoint
            history.append(record)
        check()
        return result("succeeded")
    except Cancelled:
        return result("cancelled")
    except ScenarioFailure as error:
        return result("failed", error.code)
    except Exception:
        return result("failed", "SCENARIO_STAGE_FAILED")
