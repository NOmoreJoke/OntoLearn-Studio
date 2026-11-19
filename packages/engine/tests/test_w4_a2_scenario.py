"""T07 ``project.scenario.*`` over the real w4a2_runtime business3 runtime (W4-A2).

Covers all eleven wire methods: create/copy binding real project versions,
cursor-paginated listing, run execution with exact ``beforeRunCheckpointRef``
parity against ``project.run.before_commit``, Appendix E determinism (seeded
random.Random replays), per-round atomic commit boundaries, cancel retaining
committed rounds, explicit resume validation (config/input/checkpoint parity,
no implicit resume, no blind replay), 2-10 run comparison with the fixed
metrics, restricted run deletion, isolated baseline restore, and zero mutation
of formal project facts.
"""

import json
import random

import pytest
from ontolearn_engine.scenario import service as scenario_service
from test_w4_a2_harness import (
    before_run,
    create_scenario,
    denied,
    exchange,
    ok,
    prepared_project,
    runtime,
    scenario_configuration,
    uid,
)


@pytest.fixture
def w4a2_runtime(tmp_path):
    with runtime(tmp_path) as pair:
        yield pair


def run_scenario(
    actor, project, revision, snapshot_id, scenario_id, *, run_id=None, operation=None
):
    operation = operation or uid()
    marked = ok(before_run(actor, project, operation, revision, domain="scenario"))
    return marked, exchange(
        actor,
        "project.scenario.run",
        {
            "projectId": project,
            "scenarioId": scenario_id,
            "projectVersion": revision,
            "inputSnapshotId": snapshot_id,
            "operationId": operation,
            "runId": run_id or uid(),
        },
    )


def resume_scenario(
    actor, project, revision, snapshot_id, scenario_id, source_run_id, checkpoint_ref
):
    operation = uid()
    marked = ok(before_run(actor, project, operation, revision, domain="scenario"))
    return marked, exchange(
        actor,
        "project.scenario.resume",
        {
            "projectId": project,
            "scenarioId": scenario_id,
            "projectVersion": revision,
            "inputSnapshotId": snapshot_id,
            "sourceRunId": source_run_id,
            "checkpointRef": checkpoint_ref,
            "operationId": operation,
            "runId": uid(),
        },
    )


def cancel_run(actor, project, scenario_id, run_id, operation=None):
    return exchange(
        actor,
        "project.scenario.cancel",
        {
            "projectId": project,
            "scenarioId": scenario_id,
            "runId": run_id,
            "operationId": operation or uid(),
        },
    )


def read_run(actor, project, scenario_id, run_id, *, offset=0, limit=50):
    return exchange(
        actor,
        "project.scenario.run.read",
        {
            "projectId": project,
            "scenarioId": scenario_id,
            "runId": run_id,
            "roundOffset": offset,
            "limit": limit,
        },
    )


def delete_run(actor, project, scenario_id, run_id, operation=None):
    return exchange(
        actor,
        "project.scenario.run.delete",
        {
            "projectId": project,
            "scenarioId": scenario_id,
            "runId": run_id,
            "operationId": operation or uid(),
        },
    )


def sid(created):
    return created["scenario"]["identity"]["scenarioId"]


def created_scenario(w4a2_runtime, *, configuration=None):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    response = create_scenario(actor, project, revision, snapshot_id, configuration=configuration)
    return actor, store, project, (revision, snapshot_id), ok(response)


def test_create_binds_real_project_versions(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    result = ok(create_scenario(actor, project, revision, snapshot_id))
    identity = result["scenario"]["identity"]
    assert identity["projectId"] == project
    assert identity["projectVersion"] == revision
    assert identity["inputSnapshotId"] == snapshot_id
    assert identity["semantics"] == "scenario-e2-v1"
    assert identity["engineVersion"] and identity["dependencyLockHash"]
    assert identity["configurationDigest"]
    assert result["scenario"]["configuration"] == scenario_configuration()


def test_create_idempotent_replay_and_conflicting_reuse(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    operation = uid()
    args = {
        "projectId": project,
        "projectVersion": revision,
        "inputSnapshotId": snapshot_id,
        "operationId": operation,
        "configuration": scenario_configuration(),
    }
    first = ok(exchange(actor, "project.scenario.create", args))
    assert ok(exchange(actor, "project.scenario.create", args)) == first
    denied(
        exchange(
            actor,
            "project.scenario.create",
            {
                **args,
                "configuration": scenario_configuration(name="另一个名字"),
            },
        ),
        "IDENTITY_CONFLICT",
    )


def test_create_rejects_moved_revision(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    denied(
        create_scenario(actor, project, revision + 1, snapshot_id),
        "REVISION_CONFLICT",
    )
    denied(
        create_scenario(actor, project, revision, "0" * 64),
        "IDENTITY_CONFLICT",
    )


def test_run_returns_exact_before_run_checkpoint_ref(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    marked, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    result = ok(response)
    assert result["beforeRunCheckpointRef"] == marked["checkpointRef"]
    assert result["run"]["status"] == "succeeded"
    assert result["run"]["identity"]["scenarioId"] == sid(created)


def test_run_without_receipt_fails_closed(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    denied(
        exchange(
            actor,
            "project.scenario.run",
            {
                "projectId": project,
                "scenarioId": sid(created),
                "projectVersion": revision,
                "inputSnapshotId": snapshot_id,
                "operationId": uid(),
                "runId": uid(),
            },
        ),
        "IDENTITY_CONFLICT",
    )
    behavior_receipt = uid()
    ok(before_run(actor, project, behavior_receipt, revision, domain="behavior"))
    denied(
        exchange(
            actor,
            "project.scenario.run",
            {
                "projectId": project,
                "scenarioId": sid(created),
                "projectVersion": revision,
                "inputSnapshotId": snapshot_id,
                "operationId": behavior_receipt,
                "runId": uid(),
            },
        ),
        "IDENTITY_CONFLICT",
    )


def test_run_executes_rounds_with_fixed_metrics(w4a2_runtime):
    configuration = scenario_configuration(
        maxRounds=2,
        capacity={"mode": "direct", "direct": 1},
        events=[
            {"id": "E1", "round": 1, "sequence": 1, "payload": {"kind": "工单"}},
            {"id": "E2", "round": 1, "sequence": 2, "payload": {"kind": "工单"}},
            {
                "id": "A1",
                "round": 2,
                "sequence": 3,
                "payload": {"alarmId": "a1", "level": "High", "status": "Open"},
            },
        ],
    )
    actor, store, project, (revision, snapshot_id), created = created_scenario(
        w4a2_runtime, configuration=configuration
    )
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    result = ok(response)
    run = result["run"]
    assert run["status"] == "succeeded" and run["lastCommittedRound"] == 2
    assert run["pendingEvents"] == [] and run["checkpointRef"]
    assert run["scope"] == {"mode": "scenario", "scopeId": sid(created)}
    first, second = run["rounds"]
    assert first["number"] == 1 and first["inputEvents"] == ["E1", "E2"]
    assert first["created"] == ["W001", "W002"]
    assert first["resourceCompleted"] == ["W001"]
    assert first["metrics"] == {"backlog": 1, "completed": 1, "openHighAlerts": 0}
    assert second["number"] == 2 and second["inputEvents"] == ["A1"]
    assert second["created"] == ["W003"]
    assert second["metrics"]["openHighAlerts"] == 1
    # FIFO completes the oldest pending order first: W002 before W003.
    assert second["resourceCompleted"] == ["W002"]
    assert second["backlog"] == ["W003"]
    assert second["metrics"]["completed"] == 2
    # Formal asserted facts and revision are never touched by scenario runs.
    assert store.state(store._project(project))["facts"]
    assert store.revision(store._project(project)) == revision


def test_run_read_paginates_rounds(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    run = ok(response)["run"]
    page = ok(read_run(actor, project, sid(created), run["runId"], offset=0, limit=1))
    assert [entry["number"] for entry in page["run"]["rounds"]] == [1]
    assert page["run"]["roundOffset"] == 0 and page["run"]["lastCommittedRound"] == 2
    page = ok(read_run(actor, project, sid(created), run["runId"], offset=1, limit=1))
    assert [entry["number"] for entry in page["run"]["rounds"]] == [2]
    page = ok(read_run(actor, project, sid(created), run["runId"], offset=2, limit=5))
    assert page["run"]["rounds"] == []


def test_run_read_rejects_wrong_scenario(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    run = ok(response)["run"]
    denied(
        read_run(actor, project, uid(), run["runId"]),
        "IDENTITY_CONFLICT",
    )
    denied(read_run(actor, project, sid(created), uid()), "NOT_FOUND")


def _make_interrupted_run(store, project, source_run_id, keep_rounds=1, *, cancelled=True):
    """A durable crashed run reusing a real run's committed round checkpoints.

    Append-only evidence rows: a fresh running claim plus, when ``cancelled``,
    the reconciled terminal marker carrying the exact committed rounds the real
    runner produced (what a host observes after a crash + cancel reconciliation).
    """
    claim = scenario_service._read_detail(
        store, project, scenario_service.RUN_PREFIX + source_run_id
    )
    terminal = scenario_service._read_detail(
        store, project, scenario_service.TERMINAL_PREFIX + source_run_id
    )
    rounds = terminal["rounds"][:keep_rounds]
    checkpoint = rounds[-1]["checkpoint"] if rounds else None
    run_id = uid()
    new_claim = {
        **claim,
        "runId": run_id,
        "operationId": uid(),
        "status": "running",
        "sourceRunId": None,
        "resumedFrom": None,
        "rounds": [],
        "lastCommittedRound": 0,
        "checkpoint": None,
        "pendingEvents": claim["pendingEvents"],
        "error": None,
    }
    with store._transaction():
        scenario_service._insert_detail(
            store, project, scenario_service.RUN_PREFIX + run_id, new_claim
        )
        if cancelled:
            scenario_service._insert_detail(
                store,
                project,
                scenario_service.TERMINAL_PREFIX + run_id,
                {
                    "recordVersion": 1,
                    "projectId": project,
                    "runId": run_id,
                    "status": "cancelled",
                    "rounds": rounds,
                    "lastCommittedRound": keep_rounds,
                    "checkpoint": checkpoint,
                    "pendingEvents": (
                        scenario_service._pending_ids(checkpoint)
                        if checkpoint is not None
                        else claim["pendingEvents"]
                    ),
                    "error": None,
                },
            )
    return run_id, scenario_service.load_run(store, project, run_id)


def whole_run_rounds(store, project, run_id):
    return scenario_service.load_run(store, project, run_id)["rounds"]


def test_cancel_preserves_committed_rounds(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    whole = ok(response)["run"]
    run_id, record = _make_interrupted_run(store, project, whole["runId"], keep_rounds=1)
    result = ok(cancel_run(actor, project, sid(created), run_id))
    run = result["run"]
    assert run["status"] == "cancelled"
    assert run["lastCommittedRound"] == 1
    assert [entry["number"] for entry in run["rounds"]] == [1]
    assert run["rounds"][0] == whole["rounds"][0]
    assert run["pendingEvents"] == ["E2"]
    assert run["resumeAvailable"] is True
    replay = ok(cancel_run(actor, project, sid(created), run_id))
    assert replay["run"] == result["run"]
    read = ok(read_run(actor, project, sid(created), run_id))
    assert read["run"]["status"] == "cancelled"


def test_cancel_rejects_terminal_runs(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    run = ok(response)["run"]
    denied(cancel_run(actor, project, sid(created), run["runId"]), "INVALID_STATE")
    denied(cancel_run(actor, project, sid(created), uid()), "NOT_FOUND")


def test_resume_continues_uncommitted_rounds_from_source_checkpoint(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    whole = ok(response)["run"]
    run_id, _ = _make_interrupted_run(store, project, whole["runId"], keep_rounds=1)
    ok(cancel_run(actor, project, sid(created), run_id))
    checkpoint_ref = ok(read_run(actor, project, sid(created), run_id))["run"]["rounds"][0][
        "checkpointRef"
    ]
    marked, response = resume_scenario(
        actor,
        project,
        revision,
        snapshot_id,
        sid(created),
        run_id,
        checkpoint_ref,
    )
    result = ok(response)
    assert result["sourceRunId"] == run_id and result["resumedFrom"] == checkpoint_ref
    assert result["beforeRunCheckpointRef"] == marked["checkpointRef"]
    run = result["run"]
    assert run["status"] == "succeeded"
    assert [entry["number"] for entry in run["rounds"]] == [2]
    # Resuming the real committed checkpoint replays the whole run's tail exactly.
    assert run["rounds"] == whole["rounds"][1:]
    assert run["lastCommittedRound"] == 2 and run["pendingEvents"] == []


def test_resume_rejects_invalid_sources(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    # A succeeded run can never be resumed.
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    succeeded = ok(response)["run"]
    denied(
        resume_scenario(
            actor,
            project,
            revision,
            snapshot_id,
            sid(created),
            succeeded["runId"],
            succeeded["checkpointRef"],
        )[1],
        "INVALID_STATE",
    )
    run_id, _ = _make_interrupted_run(store, project, succeeded["runId"], keep_rounds=1)
    ok(cancel_run(actor, project, sid(created), run_id))
    denied(
        resume_scenario(actor, project, revision, snapshot_id, sid(created), run_id, "0" * 64)[1],
        "IDENTITY_CONFLICT",
    )
    # Implicit resume (same runId) is rejected by the frozen param contract.
    operation = uid()
    ok(before_run(actor, project, operation, revision, domain="scenario"))
    denied(
        exchange(
            actor,
            "project.scenario.resume",
            {
                "projectId": project,
                "scenarioId": sid(created),
                "projectVersion": revision,
                "inputSnapshotId": snapshot_id,
                "sourceRunId": run_id,
                "checkpointRef": "0" * 64,
                "operationId": operation,
                "runId": run_id,
            },
        ),
        "INVALID_REQUEST",
    )


def test_resume_rejects_config_and_input_drift(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    # Source cancelled under a different scenario's configuration.
    other = ok(
        create_scenario(
            actor,
            project,
            revision,
            snapshot_id,
            configuration=scenario_configuration(name="配置漂移源"),
        )
    )
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(other))
    other_run = ok(response)["run"]
    run_id, _ = _make_interrupted_run(store, project, other_run["runId"], keep_rounds=1)
    ok(cancel_run(actor, project, sid(other), run_id))
    checkpoint_ref = ok(read_run(actor, project, sid(other), run_id))["run"]["rounds"][0][
        "checkpointRef"
    ]
    # Cross-scenario resume with a valid checkpoint of another configuration.
    denied(
        resume_scenario(
            actor,
            project,
            revision,
            snapshot_id,
            sid(created),
            run_id,
            checkpoint_ref,
        )[1],
        "IDENTITY_CONFLICT",
    )
    # Input drift: the project revision moved past the source binding.
    from ontolearn_engine.storage import digest as storage_digest
    from test_w4_a2_harness import commit_changeset

    commit_changeset(
        actor,
        store,
        project,
        {
            "manual": [
                {
                    "id": storage_digest(["urn:x:drift", "urn:test:status", '"沙盘漂移"']),
                    "subject": "urn:x:drift",
                    "predicate": "urn:test:status",
                    "object": '"沙盘漂移"',
                }
            ]
        },
    )
    moved = store.revision(store._project(project))
    moved_snapshot = storage_digest(store._snapshot_projection(store._project(project)))
    # Input drift: the source run's binding no longer matches the project input.
    denied(
        resume_scenario(
            actor, project, moved, moved_snapshot, sid(created), run_id, checkpoint_ref
        )[1],
        "IDENTITY_CONFLICT",
    )


def test_compare_two_runs_with_fixed_metrics(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, first = run_scenario(actor, project, revision, snapshot_id, sid(created))
    _, second = run_scenario(actor, project, revision, snapshot_id, sid(created))
    one, two = ok(first)["run"], ok(second)["run"]
    result = ok(
        exchange(
            actor,
            "project.scenario.compare",
            {
                "projectId": project,
                "runs": [
                    {"scenarioId": sid(created), "runId": one["runId"]},
                    {"scenarioId": sid(created), "runId": two["runId"]},
                ],
                "roundOffset": 0,
                "limit": 50,
            },
        )
    )
    assert len(result["runs"]) == 2
    for pick, run in zip((one, two), result["runs"], strict=True):
        assert run["runId"] == pick["runId"]
        assert run["status"] == "succeeded" and run["lastCommittedRound"] == 2
        assert [m["round"] for m in run["metrics"]] == [1, 2]
        assert run["finalMetrics"] == pick["rounds"][-1]["metrics"]
    page = ok(
        exchange(
            actor,
            "project.scenario.compare",
            {
                "projectId": project,
                "runs": [
                    {"scenarioId": sid(created), "runId": one["runId"]},
                    {"scenarioId": sid(created), "runId": two["runId"]},
                ],
                "roundOffset": 1,
                "limit": 1,
            },
        )
    )
    assert [m["round"] for m in page["runs"][0]["metrics"]] == [2]


def test_compare_rejects_non_succeeded_and_unknown_runs(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    whole = ok(response)["run"]
    run_id, _ = _make_interrupted_run(store, project, whole["runId"], keep_rounds=1)
    denied(
        exchange(
            actor,
            "project.scenario.compare",
            {
                "projectId": project,
                "runs": [
                    {"scenarioId": sid(created), "runId": run_id},
                    {"scenarioId": sid(created), "runId": uid()},
                ],
                "roundOffset": 0,
                "limit": 50,
            },
        ),
        "INVALID_STATE",
    )


def test_list_cursor_pagination(w4a2_runtime):
    actor, store = w4a2_runtime
    project, revision, snapshot_id = prepared_project(actor, store)
    ids = []
    for index in range(3):
        result = ok(
            create_scenario(
                actor,
                project,
                revision,
                snapshot_id,
                configuration=scenario_configuration(name=f"沙盘{index}"),
            )
        )
        ids.append(result["scenario"]["identity"]["scenarioId"])
    page = ok(
        exchange(
            actor,
            "project.scenario.list",
            {"projectId": project, "cursor": None, "limit": 2},
        )
    )
    assert len(page["items"]) == 2 and page["nextCursor"]
    rest = ok(
        exchange(
            actor,
            "project.scenario.list",
            {"projectId": project, "cursor": page["nextCursor"], "limit": 2},
        )
    )
    assert len(rest["items"]) == 1 and rest["nextCursor"] is None
    listed = {item["identity"]["scenarioId"] for item in page["items"] + rest["items"]}
    assert listed == set(ids)


def test_copy_binds_source_and_new_identity(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    copied = ok(
        exchange(
            actor,
            "project.scenario.copy",
            {
                "projectId": project,
                "scenarioId": sid(created),
                "projectVersion": revision,
                "inputSnapshotId": snapshot_id,
                "operationId": uid(),
                "name": "复制沙盘",
            },
        )
    )
    assert copied["sourceScenarioId"] == sid(created)
    assert copied["scenario"]["identity"]["scenarioId"] != sid(created)
    assert copied["scenario"]["configuration"]["name"] == "复制沙盘"
    listing = ok(
        exchange(
            actor, "project.scenario.list", {"projectId": project, "cursor": None, "limit": 50}
        )
    )
    assert len(listing["items"]) == 2


def test_read_scenario_lists_runs(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, first = run_scenario(actor, project, revision, snapshot_id, sid(created))
    _, second = run_scenario(actor, project, revision, snapshot_id, sid(created))
    detail = ok(
        exchange(
            actor,
            "project.scenario.read",
            {"projectId": project, "scenarioId": sid(created)},
        )
    )
    assert detail["scenario"]["identity"] == created["scenario"]["identity"]
    runs = {run["runId"]: run for run in detail["runs"]}
    assert set(runs) == {ok(first)["run"]["runId"], ok(second)["run"]["runId"]}
    assert all(run["status"] == "succeeded" for run in runs.values())


def test_run_delete_is_restricted_and_idempotent(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    whole = ok(response)["run"]
    run_id, _ = _make_interrupted_run(
        store, project, whole["runId"], keep_rounds=1, cancelled=False
    )
    denied(delete_run(actor, project, sid(created), run_id), "INVALID_STATE")
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    finished = ok(response)["run"]
    operation = uid()
    result = ok(delete_run(actor, project, sid(created), finished["runId"], operation))
    assert result["deleted"] is True
    assert ok(delete_run(actor, project, sid(created), finished["runId"], operation)) == result
    denied(read_run(actor, project, sid(created), finished["runId"]), "NOT_FOUND")
    denied(delete_run(actor, project, sid(created), uid()), "NOT_FOUND")


def test_restore_returns_isolated_scenario_to_baseline(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    ok(response)
    detail = ok(
        exchange(
            actor,
            "project.scenario.read",
            {"projectId": project, "scenarioId": sid(created)},
        )
    )
    assert detail["runs"]
    internal = store._project(project)
    facts_before = store.state(internal)
    result = ok(
        exchange(
            actor,
            "project.scenario.restore",
            {
                "projectId": project,
                "scenarioId": sid(created),
                "projectVersion": revision,
                "inputSnapshotId": snapshot_id,
                "configurationDigest": created["scenario"]["identity"]["configurationDigest"],
                "operationId": uid(),
            },
        )
    )
    assert result["scenario"]["identity"] == created["scenario"]["identity"]
    detail = ok(
        exchange(
            actor,
            "project.scenario.read",
            {"projectId": project, "scenarioId": sid(created)},
        )
    )
    assert detail["runs"] == []
    assert store.state(internal) == facts_before
    assert store.revision(internal) == revision
    denied(
        exchange(
            actor,
            "project.scenario.restore",
            {
                "projectId": project,
                "scenarioId": sid(created),
                "projectVersion": revision,
                "inputSnapshotId": snapshot_id,
                "configurationDigest": "0" * 64,
                "operationId": uid(),
            },
        ),
        "IDENTITY_CONFLICT",
    )


def test_scenario_operations_never_mutate_formal_facts(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    internal = store._project(project)
    before = store.state(internal)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    finished = ok(response)["run"]
    # A crashed running claim reconciles to cancelled without formal effects.
    crashed, _ = _make_interrupted_run(
        store, project, finished["runId"], keep_rounds=1, cancelled=False
    )
    ok(cancel_run(actor, project, sid(created), crashed))
    marked, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    run = ok(response)["run"]
    ok(delete_run(actor, project, sid(created), run["runId"]))
    assert store.state(internal) == before
    assert store.revision(internal) == revision
    assert marked["domainRevision"] == revision


def test_seeded_property_replay_and_resume_equivalence(w4a2_runtime):
    """Seeded random.Random schedules: replays are identical and resumes match."""
    generator = random.Random(20261120)
    for trial in range(3):
        rounds = generator.randint(1, 4)
        capacity = generator.randint(0, 3)
        events = []
        sequence = 0
        for number in range(1, rounds + 1):
            for _ in range(generator.randint(0, 2)):
                sequence += 1
                events.append(
                    {
                        "id": f"T{trial}-E{sequence}",
                        "round": number,
                        "sequence": sequence,
                        "payload": {"kind": "工单"},
                    }
                )
        configuration = scenario_configuration(
            name=f"属性沙盘{trial}",
            maxRounds=rounds,
            capacity={"mode": "direct", "direct": capacity},
            events=events,
        )
        actor, store = w4a2_runtime
        project, revision, snapshot_id = prepared_project(actor, store)
        created = ok(
            create_scenario(actor, project, revision, snapshot_id, configuration=configuration)
        )
        scenario_id = created["scenario"]["identity"]["scenarioId"]
        _, first = run_scenario(actor, project, revision, snapshot_id, scenario_id)
        _, second = run_scenario(actor, project, revision, snapshot_id, scenario_id)
        one, two = ok(first)["run"], ok(second)["run"]
        assert one["rounds"] == two["rounds"]
        assert one["pendingEvents"] == two["pendingEvents"]
        assert one["status"] == two["status"] == "succeeded"
        # Interrupted-then-resumed replay equals one whole run of the same input.
        interrupted, record = _make_interrupted_run(store, project, one["runId"], keep_rounds=1)
        ok(cancel_run(actor, project, scenario_id, interrupted))
        checkpoint_ref = ok(read_run(actor, project, scenario_id, interrupted))["run"]["rounds"][0][
            "checkpointRef"
        ]
        _, resumed = resume_scenario(
            actor, project, revision, snapshot_id, scenario_id, interrupted, checkpoint_ref
        )
        resumed_run = ok(resumed)["run"]
        assert resumed_run["status"] == "succeeded"
        assert resumed_run["lastCommittedRound"] == rounds
        read = ok(read_run(actor, project, scenario_id, one["runId"]))
        assert [r["number"] for r in resumed_run["rounds"]] == [
            r["number"] for r in read["run"]["rounds"][1:]
        ]
        assert json.dumps(resumed_run["rounds"], sort_keys=True) == json.dumps(
            read["run"]["rounds"][1:], sort_keys=True
        )


def test_before_run_receipt_exact_ref_recorded_on_resume(w4a2_runtime):
    actor, store, project, (revision, snapshot_id), created = created_scenario(w4a2_runtime)
    _, response = run_scenario(actor, project, revision, snapshot_id, sid(created))
    whole = ok(response)["run"]
    run_id, _ = _make_interrupted_run(store, project, whole["runId"], keep_rounds=1)
    ok(cancel_run(actor, project, sid(created), run_id))
    checkpoint_ref = ok(read_run(actor, project, sid(created), run_id))["run"]["rounds"][0][
        "checkpointRef"
    ]
    marked, response = resume_scenario(
        actor,
        project,
        revision,
        snapshot_id,
        sid(created),
        run_id,
        checkpoint_ref,
    )
    result = ok(response)
    assert result["beforeRunCheckpointRef"] == marked["checkpointRef"]
    record = scenario_service.load_run(store, project, result["run"]["runId"])
    assert record["beforeRunCheckpointRef"] == marked["checkpointRef"]
    assert record["sourceRunId"] == run_id and record["resumedFrom"] == checkpoint_ref
