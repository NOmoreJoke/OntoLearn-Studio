"""Synthetic ports verify T07 orchestration, never real T05/T06/Store acceptance."""

import json
from dataclasses import replace
from pathlib import Path

import pytest
from ontolearn_engine.scenario.model import (
    Alert,
    Capacity,
    Definition,
    Event,
    State,
    WorkOrder,
    copy_scenario,
    create_order,
    metrics,
    resource_stage,
)
from ontolearn_engine.scenario.runner import (
    Context,
    Execution,
    Inference,
    Plan,
    ScenarioFailure,
    run,
)

FIXTURE = json.loads(
    (Path(__file__).parents[3] / "tests/fixtures/scenario/e5.json").read_text(encoding="utf-8")
)


def definition(capacity=3, **kwargs):
    return Definition(
        "project-1",
        "engine-1",
        "lock-1",
        "P1",
        "S1",
        "V1",
        "R1",
        "B1",
        4,
        Capacity(direct=capacity),
        tuple(Event(**event) for event in FIXTURE["events"]),
        **kwargs,
    )


class ProbePorts:
    """In-process synthetic stages. commit captures values; it is not a Store."""

    def __init__(self):
        self.calls = []
        self.saved = []
        self.stage = ""
        self.stop = False
        self.fail = None
        self.plan_count = None
        self.generated = ()
        self.current_events = ()

    def enter(self, stage, check):
        self.calls.append(stage)
        self.stage = stage
        check()
        if self.fail == stage:
            raise RuntimeError("private business input must not escape")

    def apply_events(self, state, events, context, check):
        self.enter("events", check)
        self.current_events = events
        return state

    def infer(self, state, definition, context, check):
        self.enter("infer", check)
        return Inference(state, definition.rule_version, "synthetic-inference-probe", context)

    def plan(self, state, inference, events, context, check):
        self.enter("plan", check)
        assert inference.input_state == state
        return Plan(
            self.plan_count if self.plan_count is not None else len(events),
            "{}",
            tuple((events[0].id, "synthetic-B", index + 1) for index in range(self.plan_count))
            if self.plan_count is not None and type(self.plan_count) is int and self.plan_count >= 0
            else tuple((event.id, "synthetic-B", 1) for event in events),
        )

    def execute(self, state, plan, context, check):
        self.enter("execute", check)
        number = context.round
        for event in self.current_events:
            state = create_order(state, event.id, number)
        return Execution(state, plan.action_count, self.generated)

    def commit(self, record, check):
        self.enter("commit", check)
        self.saved.append(record)


def expected(result):
    return [
        {
            "round": r.checkpoint.round,
            "created": list(r.created),
            "completed": list(r.resource_completed),
            "backlog": list(r.backlog),
            "metrics": {
                "backlog": r.metrics.backlog,
                "completed": r.metrics.completed,
                "open_high_alerts": r.metrics.open_high_alerts,
            },
        }
        for r in result.rounds
    ]


@pytest.mark.parametrize("capacity", [3, 4])
def test_e5_complete_sets_and_two_independent_replays(capacity):
    d = definition(capacity)
    original = d.digest
    runs = [run(d, ProbePorts()) for _ in range(3)]
    for result in runs:
        assert result.status == "succeeded"
        assert expected(result) == FIXTURE["expected"][str(capacity)]
        assert result.checkpoint.consumed == tuple(f"E{i:03}" for i in range(1, 17))
        assert [o.id for o in result.checkpoint.state.orders] == [f"W{i:03}" for i in range(1, 17)]
        assert not result.has_unprocessed_events
    assert runs[0] == runs[1] == runs[2]
    assert d.digest == original and d.initial == State()


def test_exact_stage_order_and_same_round_completion():
    p = ProbePorts()
    result = run(replace(definition(), max_rounds=1), p)
    assert p.calls == ["infer", "events", "infer", "plan", "execute", "infer", "commit"]
    assert result.rounds[0].created == ("W001", "W002", "W003", "W004")
    assert result.rounds[0].resource_completed == ("W001", "W002", "W003")
    assert result.has_unprocessed_events
    assert [e.id for e in result.pending] == [f"E{i:03}" for i in range(5, 17)]


@pytest.mark.parametrize("stage", ["events", "infer", "plan", "execute", "commit"])
def test_failure_retains_previous_round_and_redacts_exception(stage):
    p = ProbePorts()
    base_commit = p.commit

    def commit(record, check):
        base_commit(record, check)
        p.fail = stage

    p.commit = commit
    result = run(definition(), p)
    assert result.status == "failed" and result.error_code == "SCENARIO_STAGE_FAILED"
    assert result.checkpoint.round == 1
    assert len(p.saved) == 1 and len(result.rounds) == 1
    assert result.checkpoint.consumed == ("E001", "E002", "E003", "E004")
    assert result.checkpoint.state == p.saved[0].checkpoint.state


@pytest.mark.parametrize("stage", ["events", "infer", "plan", "execute", "commit"])
def test_cancel_at_each_uncommitted_stage_has_zero_effect(stage):
    p = ProbePorts()
    result = run(definition(), p, cancelled=lambda: p.stage == stage)
    assert result.status == "cancelled"
    assert not p.saved and not result.rounds and result.checkpoint.round == 0
    assert result.checkpoint.consumed == () and result.checkpoint.state == State()


def test_cancel_after_commit_preserves_durable_round():
    p = ProbePorts()
    base_commit = p.commit

    def commit(record, check):
        base_commit(record, check)
        p.stop = True

    p.commit = commit
    result = run(definition(), p, cancelled=lambda: p.stop)
    assert result.status == "cancelled" and result.checkpoint.round == 1
    assert result.rounds == tuple(p.saved)
    assert result.checkpoint.consumed == ("E001", "E002", "E003", "E004")


def test_conflict_never_executes_or_commits():
    p = ProbePorts()

    def conflict(*_):
        raise ScenarioFailure("BEHAVIOR_CONFLICT")

    p.plan = conflict
    result = run(definition(), p)
    assert result.status == "failed" and result.error_code == "BEHAVIOR_CONFLICT"
    assert not p.saved and "execute" not in p.calls


@pytest.mark.parametrize("count,ok", [(1000, True), (1001, False), (-1, False), (True, False)])
def test_action_bound_before_execution(count, ok):
    p = ProbePorts()
    p.plan_count = count
    result = run(replace(definition(), max_rounds=1), p)
    assert (result.status == "succeeded") == ok
    if not ok:
        assert result.error_code == "ACTION_LIMIT" and "execute" not in p.calls


def test_generated_event_only_next_round_and_max_limit_retains_it():
    p = ProbePorts()
    p.generated = (Event("next", 2, 20),)
    result = run(replace(definition(), max_rounds=1), p)
    assert result.rounds[0].input_events == ("E001", "E002", "E003", "E004")
    assert result.pending[-1].id == "next" and result.pending[-1].round == 2
    p = ProbePorts()
    p.generated = (Event("wrong", 1, 20),)
    result = run(definition(), p)
    assert result.error_code == "GENERATED_EVENT_ROUND" and not p.saved


def test_resume_retains_consumption_and_independent_replay_resets():
    d = definition()
    p = ProbePorts()
    base_commit = p.commit

    def commit(record, check):
        base_commit(record, check)
        p.stop = True

    p.commit = commit
    first = run(d, p, cancelled=lambda: p.stop)
    resumed_ports = ProbePorts()
    resumed = run(d, resumed_ports, resume=first.checkpoint)
    assert resumed.status == "succeeded" and resumed.rounds[0].checkpoint.round == 2
    assert expected(first) + expected(resumed) == FIXTURE["expected"]["3"]
    assert resumed.checkpoint == run(d, ProbePorts()).checkpoint
    with pytest.raises(ValueError):
        run(replace(d, input_version="V2"), ProbePorts(), resume=first.checkpoint)
    assert run(d, ProbePorts()).rounds[0].input_events == first.rounds[0].input_events


def test_duplicate_events_and_invalid_initial_consumption():
    d = definition()
    result = run(replace(d, events=(*d.events, d.events[0])), ProbePorts())
    assert expected(result) == FIXTURE["expected"]["3"]
    with pytest.raises(ValueError):
        replace(d, events=(*d.events, replace(d.events[0], payload='{"changed":true}')))
    with pytest.raises(ValueError):
        replace(d, initial_consumed=("unknown",))
    result = run(replace(d, initial_consumed=("E001",)), ProbePorts())
    assert "E001" not in result.rounds[0].input_events


def test_fifo_is_creation_round_then_sequence_then_id_not_input_order():
    state = State(
        orders=(
            WorkOrder("z", "ez", 1, 1),
            WorkOrder("c", "ec", 0, 4),
            WorkOrder("b", "eb", 0, 2),
            WorkOrder("a", "ea", 0, 2),
        )
    )
    result, completed = resource_stage(state, Capacity(people=1, per_person=3))
    assert completed == ("a", "b", "c")
    assert [o.id for o in result.orders if o.status != "completed"] == ["z"]
    assert state.orders[0].status == "pending"


def test_metrics_count_actual_state_not_recurrence_and_exclude_initial_completed():
    state = State(
        alerts=(Alert("a", "High", "Open"), Alert("b", "High", "Closed"), Alert("c", "Low", "Open"))
    )
    assert metrics(state, ("W1", "W1")) == type(metrics(state, ()))(0, 1, 1)
    d = replace(definition(), initial=State(orders=(WorkOrder("W001", "old", 0, 1, "completed"),)))
    result = run(d, ProbePorts())
    assert result.rounds[-1].metrics.completed == 12


@pytest.mark.parametrize(
    "capacity",
    [
        lambda: Capacity(),
        lambda: Capacity(direct=True),
        lambda: Capacity(direct=-1),
        lambda: Capacity(direct=1, people=2),
        lambda: Capacity(people=2),
    ],
)
def test_capacity_validation(capacity):
    with pytest.raises(ValueError):
        capacity()


@pytest.mark.parametrize("rounds", [0, 1001, True])
def test_max_round_bounds(rounds):
    with pytest.raises(ValueError):
        replace(definition(), max_rounds=rounds)


def test_wrong_inference_identity_cannot_feed_behavior():
    p = ProbePorts()
    p.infer = lambda state, d, context, check: Inference(state, "wrong", "snapshot", context)
    result = run(definition(), p)
    assert result.error_code == "INFERENCE_IDENTITY" and not p.saved


def test_copy_is_explicit_and_does_not_change_source():
    source = definition()
    copied = copy_scenario(source, "new", "V2")
    assert source.scenario_id == "S1" and copied.initial == source.initial
    assert copied.digest != source.digest
    with pytest.raises(ValueError):
        copy_scenario(source, source.scenario_id, "V2")


def test_deleted_order_id_and_event_identity_are_never_reused():
    state = create_order(create_order(State(), "E1", 1), "E2", 1)
    deleted = replace(state, orders=(state.orders[0],))
    assert create_order(deleted, "E2", 2) == deleted
    next_state = create_order(deleted, "E3", 2)
    assert [order.id for order in next_state.orders] == ["W001", "W003"]
    assert next_state.order_sequence == 3
    empty = replace(next_state, orders=())
    assert create_order(empty, "E4", 3).orders[0].id == "W004"


def test_resume_rejects_future_consumption_and_lost_committed_consumption():
    d = definition()
    p = ProbePorts()
    p.commit = lambda record, check: (check(), setattr(p, "stop", True))
    first = run(d, p, cancelled=lambda: p.stop)
    checkpoint = first.checkpoint
    with pytest.raises(ValueError, match="future event"):
        run(d, ProbePorts(), resume=replace(checkpoint, consumed=(*checkpoint.consumed, "E005")))
    with pytest.raises(ValueError, match="lost committed"):
        run(d, ProbePorts(), resume=replace(checkpoint, consumed=checkpoint.consumed[:-1]))


@pytest.mark.parametrize("inference_call", [1, 2, 3])
def test_cancel_separately_initial_event_and_end_inference(inference_call):
    p = ProbePorts()
    infer = p.infer
    count = 0

    def inference(state, d, context, check):
        nonlocal count
        count += 1
        result = infer(state, d, context, check)
        if count == inference_call:
            p.stop = True
        return result

    p.infer = inference
    result = run(definition(), p, cancelled=lambda: p.stop)
    assert result.status == "cancelled" and not p.saved
    assert result.checkpoint.round == 0 and result.checkpoint.consumed == ()


@pytest.mark.parametrize("field", ["project_id", "engine_version", "dependency_lock_hash"])
def test_resume_and_replay_isolate_project_and_implementation_identity(field):
    d = definition()
    checkpoint = run(d, ProbePorts()).checkpoint
    with pytest.raises(ValueError, match="another input"):
        run(replace(d, **{field: "different"}), ProbePorts(), resume=checkpoint)
    with pytest.raises(ValueError, match="versions required"):
        replace(d, **{field: ""})


@pytest.mark.parametrize("capacity", [3, 4])
def test_approved_t09_e5_resource_metric_projection_and_replays(capacity):
    """Approved input bytes; only T07 projection, never full RDF/behavior acceptance."""
    import hashlib

    fixture_dir = Path(__file__).parents[3] / "tests/fixtures/scenario"
    manifest_bytes = (fixture_dir / "t09-manifest.json").read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest() == (
        "aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e"
    )
    manifest = json.loads(manifest_bytes)
    fixture_bytes = (fixture_dir / "t09-e5.json").read_bytes()
    assert (
        hashlib.sha256(fixture_bytes).hexdigest()
        == manifest["files"]["tests/fixtures/product-baselines/E.5.json"]
    )
    fixed = json.loads(fixture_bytes)
    d = replace(
        definition(capacity),
        input_version=fixed["inputVersion"],
        rule_version=fixed["ruleVersion"],
        behavior_version=fixed["behaviorVersion"],
        events=tuple(
            Event(event["id"], event["round"], event["inputSequence"], json.dumps(event["payload"]))
            for event in fixed["events"]
        ),
        rules=json.dumps({"rules": fixed["rules"]}),
        behaviors=json.dumps({"behaviors": fixed["behaviors"]}),
    )

    class AlertProjectionProbe(ProbePorts):
        def apply_events(self, state, events, context, check):
            state = super().apply_events(state, events, context, check)
            # Projection of fixed event fields only; not a substitute for actual RDF application.
            alerts = tuple(
                Alert(payload["alarmId"], payload["level"], payload["status"])
                for payload in (json.loads(event.payload) for event in events)
            )
            return replace(state, alerts=(*state.alerts, *alerts))

    results = [run(d, AlertProjectionProbe()) for _ in range(3)]
    assert results[0] == results[1] == results[2]
    for result in results:
        assert result.status == "succeeded" and not result.pending
        for actual, expected_round in zip(
            result.rounds, fixed["expected"][str(capacity)], strict=True
        ):
            assert actual.checkpoint.round == expected_round["round"]
            assert list(actual.created) == expected_round["created"]
            assert list(actual.resource_completed) == expected_round["completed"]
            assert list(actual.backlog) == expected_round["backlog"]
            assert actual.metrics.backlog == expected_round["backlogCount"]
            assert actual.metrics.completed == expected_round["completedCount"]
            # Completing a work order does not close its alarm.
            assert actual.metrics.open_high_alerts == expected_round["unclosedHighAlarmCount"]
            assert list(actual.checkpoint.consumed) == expected_round["consumedEvents"]
            assert [
                (order.id, order.event_id, order.created_round, order.status)
                for order in actual.checkpoint.state.orders
            ] == [
                (
                    order["id"],
                    order["eventId"],
                    order["createdRound"],
                    "completed" if order["status"] == "已完成" else "pending",
                )
                for order in expected_round["orders"]
            ]
            future = [
                event.id
                for event in actual.checkpoint.events
                if event.id not in actual.checkpoint.consumed
            ]
            assert future == expected_round["scheduledFutureEvents"]


def test_context_is_explicit_and_inference_phase_cannot_be_reused():
    p = ProbePorts()
    infer = p.infer
    contexts = []

    def inference(state, d, context, check):
        contexts.append(context)
        return infer(state, d, context, check)

    p.infer = inference
    result = run(replace(definition(), max_rounds=1), p)
    assert result.status == "succeeded"
    assert contexts == [Context(0, "initial"), Context(1, "before"), Context(1, "end")]
    assert result.rounds[0].frozen_plan == "{}"
    assert result.rounds[0].trace == tuple((f"E{i:03}", "synthetic-B", 1) for i in range(1, 5))
    p = ProbePorts()
    p.infer = lambda state, d, context, check: Inference(
        state, d.rule_version, "old", Context(0, "initial")
    )
    assert run(definition(), p).error_code == "INFERENCE_IDENTITY"


def test_missing_action_trace_cannot_execute_or_commit():
    p = ProbePorts()
    p.plan = lambda *args: Plan(1, "{}", ())
    result = run(definition(), p)
    assert result.error_code == "ACTION_TRACE" and "execute" not in p.calls and not p.saved
