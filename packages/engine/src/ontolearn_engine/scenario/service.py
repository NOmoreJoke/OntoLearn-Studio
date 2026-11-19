"""T07 scenario wire services: isolated sandbox runs over the owned Store.

Eleven ``business3`` methods (selected-project authority, named-bridge exposure)
backed by :mod:`ontolearn_engine.scenario.model` / :mod:`ontolearn_engine.scenario.runner`
and durable namespaced SQLite storage. ``job_details`` is append-only evidence
(immutable by SQL trigger): every write mints a new row - a definition, an
operation claim, a run claim, one terminal checkpoint row carrying the whole
committed-round history (atomic run checkpointing: every round boundary is
all-or-nothing, and a crash leaves the durable running claim for cancel/resume
reconciliation), and tombstone markers for restricted deletion/isolated
restore. Readers fold the rows; no key ever collides with ``run_before_commit``'s
own primary keys, and formal asserted project facts and project checkpoints
are NEVER modified by any scenario operation.
"""

import json
from dataclasses import asdict, replace
from uuid import uuid4

from ontolearn_engine import __version__
from ontolearn_engine.project.ontology_turtle import resolve_active
from ontolearn_engine.project.run_before_commit import lookup_receipt
from ontolearn_engine.resources import REGISTRY_HASH
from ontolearn_engine.scenario import runner as scenario_runner
from ontolearn_engine.scenario.model import (
    SEMANTICS,
    Alert,
    Capacity,
    Definition,
    Event,
    State,
    WorkOrder,
    create_order,
)
from ontolearn_engine.scenario.runner import Checkpoint, Inference
from ontolearn_engine.storage import canonical, digest

METHODS = frozenset(
    {
        "project.scenario.create",
        "project.scenario.copy",
        "project.scenario.list",
        "project.scenario.read",
        "project.scenario.run.read",
        "project.scenario.run",
        "project.scenario.cancel",
        "project.scenario.resume",
        "project.scenario.compare",
        "project.scenario.run.delete",
        "project.scenario.restore",
    }
)

DEF_PREFIX = "w4:scenario:def:"
RUN_PREFIX = "w4:scenario:run:"
TERMINAL_PREFIX = "w4:scenario:terminal:"
TOMBSTONE_PREFIX = "w4:scenario:tombstone:"
OP_PREFIX = "w4:scenario:op:"
MAX_RUNS_PER_SCENARIO = 50
ACTIVE_STATES = ("queued", "running", "cancelling")
RESULT_SCAN_CAP = 400


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


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
    import sqlite3

    try:
        store._db.execute(
            "INSERT INTO job_details VALUES(?,?,?)",
            (identity, project, canonical(record)),
        )
    except sqlite3.IntegrityError:
        fault("IDENTITY_CONFLICT")


def indexed_scenarios(store, project):
    """Scenario ids of the project (bounded constant-prefix scan, key order)."""
    rows = store._db.execute(
        "SELECT id FROM job_details WHERE project=? AND id>=? AND id<? ORDER BY id LIMIT ?",
        (project, "w4:scenario:def:", "w4:scenario:def:\uffff", RESULT_SCAN_CAP),
    ).fetchall()
    return [row["id"][len(DEF_PREFIX) :] for row in rows]


def indexed_run_ids(store, project):
    """All run ids of the project (bounded constant-prefix scan, rowid order)."""
    rows = store._db.execute(
        "SELECT id FROM job_details WHERE project=? AND id>=? AND id<? ORDER BY rowid LIMIT ?",
        (project, "w4:scenario:run:", "w4:scenario:run:\uffff", RESULT_SCAN_CAP),
    ).fetchall()
    return [row["id"][len(RUN_PREFIX) :] for row in rows]


def _tombstoned(store, project, run_id):
    return _read_detail(store, project, TOMBSTONE_PREFIX + run_id) is not None


def load_run(store, project, run_id):
    """Folded run record (claim + terminal checkpoint) or None when absent.

    Deleted (tombstoned) runs read as absent; their evidence rows stay intact.
    """
    claim = _read_detail(store, project, RUN_PREFIX + run_id)
    if claim is None or _tombstoned(store, project, run_id):
        return None
    terminal = _read_detail(store, project, TERMINAL_PREFIX + run_id)
    if terminal is None:
        return claim
    return {
        **claim,
        "status": terminal["status"],
        "rounds": terminal["rounds"],
        "lastCommittedRound": terminal["lastCommittedRound"],
        "checkpoint": terminal["checkpoint"],
        "pendingEvents": terminal["pendingEvents"],
        "error": terminal["error"],
    }


def load_definition(store, project, scenario_id):
    row = _read_detail(store, project, DEF_PREFIX + scenario_id)
    return row


def _op_replay(store, project, operation, params):
    """Idempotent operation claim; conflicting reuse rejects deterministically."""
    fingerprint = digest(params)
    row = _read_detail(store, project, OP_PREFIX + operation)
    if row is None:
        return None, fingerprint
    if row.get("requestHash") != fingerprint:
        fault("IDENTITY_CONFLICT")
    return row, fingerprint


def _op_claim(store, project, operation, fingerprint, payload):
    _insert_detail(
        store,
        project,
        OP_PREFIX + operation,
        {
            "recordVersion": 1,
            "projectId": project,
            "operationId": operation,
            "requestHash": fingerprint,
            **payload,
        },
    )


# --- definition (de)serialization -----------------------------------------------------


def _state_from_dict(data):
    return State(
        orders=tuple(WorkOrder(**order) for order in data["orders"]),
        alerts=tuple(Alert(**alert) for alert in data["alerts"]),
        assertions=data["assertions"],
        order_sequence=data["order_sequence"],
        created_orders=tuple((entry[0], entry[1], entry[2]) for entry in data["created_orders"]),
    )


def _checkpoint_from_dict(data):
    return Checkpoint(
        data["definition_digest"],
        data["round"],
        _state_from_dict(data["state"]),
        tuple(Event(**event) for event in data["events"]),
        tuple(data["consumed"]),
        tuple(data["completed"]),
    )


def _definition_from_dict(data):
    return Definition(
        project_id=data["project_id"],
        engine_version=data["engine_version"],
        dependency_lock_hash=data["dependency_lock_hash"],
        project_version=data["project_version"],
        scenario_id=data["scenario_id"],
        input_version=data["input_version"],
        rule_version=data["rule_version"],
        behavior_version=data["behavior_version"],
        max_rounds=data["max_rounds"],
        capacity=Capacity(
            direct=data["capacity"]["direct"],
            people=data["capacity"]["people"],
            per_person=data["capacity"]["per_person"],
        ),
        events=tuple(Event(**event) for event in data["events"]),
        initial=_state_from_dict(data["initial"]),
        rules=data["rules"],
        behaviors=data["behaviors"],
        parameters=data["parameters"],
        source=data["source"],
        assumptions=tuple(data["assumptions"]),
        semantics=data["semantics"],
        initial_consumed=tuple(data["initial_consumed"]),
    )


def _capacity(configuration):
    source = configuration["capacity"]
    if source["mode"] == "direct":
        return Capacity(direct=source["direct"])
    return Capacity(people=source["people"], per_person=source["perPerson"])


def _build_definition(store, internal, project, scenario_id, configuration, params):
    snapshot = store._snapshot_projection(internal)
    input_version = digest(snapshot["state"])
    try:
        definition = Definition(
            project_id=project,
            engine_version=__version__,
            dependency_lock_hash=REGISTRY_HASH,
            project_version=str(params["projectVersion"]),
            scenario_id=scenario_id,
            input_version=input_version,
            rule_version=configuration["ruleVersion"],
            behavior_version=configuration["behaviorVersion"],
            max_rounds=configuration["maxRounds"],
            capacity=_capacity(configuration),
            events=tuple(
                Event(
                    event["id"],
                    event["round"],
                    event["sequence"],
                    canonical(event["payload"]),
                )
                for event in configuration["events"]
            ),
            parameters=canonical(configuration["parameters"]),
            source=configuration["source"],
            assumptions=tuple(configuration["assumptions"]),
        )
    except ValueError:
        fault("INVALID_REQUEST", field="params")
    return definition, input_version


def _identity(project, scenario_id, params, input_version, configuration_digest, configuration):
    return {
        "projectId": project,
        "scenarioId": scenario_id,
        "projectVersion": params["projectVersion"],
        "inputSnapshotId": params["inputSnapshotId"],
        "inputVersion": input_version,
        "engineVersion": __version__,
        "dependencyLockHash": REGISTRY_HASH,
        "ruleVersion": configuration["ruleVersion"],
        "behaviorVersion": configuration["behaviorVersion"],
        "configurationDigest": configuration_digest,
        "semantics": SEMANTICS,
    }


def _evidence(configuration):
    return {
        "maxRounds": configuration["maxRounds"],
        "capacity": configuration["capacity"],
        "source": configuration["source"],
        "assumptions": list(configuration["assumptions"]),
        "parameters": configuration["parameters"],
    }


# --- wire ports -----------------------------------------------------------------------


class _WirePorts:
    """Fixed Stage 1 scenario stages over the isolated copy and Store rounds.

    ``apply_events`` projects alerts from real event payloads; ``execute`` mints
    E.3 stable work orders; ``plan`` is the frozen zero-action behavior stage
    (the configuration records behavior identity by version only). ``commit``
    freezes each finished round into the run's checkpoint collection, which the
    owner persists through one atomic Store transaction (atomic run
    checkpointing: every round boundary is all-or-nothing and a crash leaves
    the durable running claim for cancel/resume reconciliation).
    """

    def __init__(self, store, project, run_id):
        self.store, self.project, self.run_id = store, project, run_id
        self.current_events = ()
        self.rounds = []

    def apply_events(self, state, events, context, check):
        check()
        self.current_events = events
        alerts = []
        for event in events:
            try:
                payload = json.loads(event.payload)
            except ValueError:
                fault("INVALID_STATE")
            if isinstance(payload, dict) and all(
                key in payload for key in ("alarmId", "level", "status")
            ):
                alerts.append(
                    Alert(
                        str(payload["alarmId"]),
                        str(payload["level"]),
                        str(payload["status"]),
                    )
                )
        if alerts:
            return replace(state, alerts=(*state.alerts, *alerts))
        return state

    def infer(self, state, definition, context, check):
        check()
        return Inference(state, definition.rule_version, digest(asdict(state)), context)

    def plan(self, state, inference, events, context, check):
        check()
        return scenario_runner.Plan(0, "{}", ())

    def execute(self, state, plan, context, check):
        check()
        for event in self.current_events:
            state = create_order(state, event.id, context.round)
        return scenario_runner.Execution(state, plan.action_count)

    def commit(self, record, check):
        check()
        checkpoint_ref = digest(asdict(record.checkpoint))
        self.rounds.append(
            {
                "round": {
                    "number": record.checkpoint.round,
                    "created": list(record.created),
                    "resourceCompleted": list(record.resource_completed),
                    "backlog": list(record.backlog),
                    "metrics": {
                        "backlog": record.metrics.backlog,
                        "completed": record.metrics.completed,
                        "openHighAlerts": record.metrics.open_high_alerts,
                    },
                    "inputEvents": list(record.input_events),
                    "behaviorTrace": [
                        {
                            "eventId": event_id,
                            "behaviorId": behavior_id,
                            "actionIndex": action_index,
                        }
                        for event_id, behavior_id, action_index in record.trace
                    ],
                    "beforeInference": record.before_inference.snapshot,
                    "endInference": record.end_inference.snapshot,
                    "checkpointRef": checkpoint_ref,
                },
                "checkpoint": asdict(record.checkpoint),
            }
        )


def _pending_ids(checkpoint_data):
    consumed = set(checkpoint_data["consumed"])
    return [event["id"] for event in checkpoint_data["events"] if event["id"] not in consumed]


def _run_dto(record, *, round_offset=None, limit=MAX_RUNS_PER_SCENARIO):
    rounds = [entry["round"] for entry in record["rounds"]]
    if round_offset is None:
        # Contract semantics: rounds[i].number == roundOffset + i + 1, so a
        # resumed run's page naturally starts at its first committed round.
        round_offset = rounds[0]["number"] - 1 if rounds else 0
    # Paging is by round number (this run may start at a resumed round).
    rounds = [entry for entry in rounds if entry["number"] > round_offset][:limit]
    last = record["lastCommittedRound"]
    return {
        "runId": record["runId"],
        "identity": record["identity"],
        "scope": {"mode": "scenario", "scopeId": record["scenarioId"]},
        "status": record["status"],
        "lastCommittedRound": last,
        "rounds": rounds,
        "roundOffset": round_offset,
        "pendingEvents": record.get("pendingEvents", []),
        "checkpointRef": record["rounds"][-1]["round"]["checkpointRef"] if last else None,
        "resumeAvailable": record["status"] in ("cancelled", "failed") and last > 0,
        "replayAvailable": True,
        "replayUnavailableReason": None,
        "evidence": record["evidence"],
        "error": record.get("error"),
    }


def _run_result(project, operation, row, *, source_run=None, resumed_from=None):
    run_dto = _run_dto(row)
    if source_run is not None:
        return {
            "projectId": project,
            "operationId": operation,
            "sourceRunId": source_run,
            "resumedFrom": resumed_from,
            "run": run_dto,
            "beforeRunCheckpointRef": row["beforeRunCheckpointRef"],
        }
    return {
        "projectId": project,
        "operationId": operation,
        "run": run_dto,
        "beforeRunCheckpointRef": row["beforeRunCheckpointRef"],
    }


def _cas_snapshot(store, internal, params):
    if store.revision(internal) != params["projectVersion"]:
        fault(
            "REVISION_CONFLICT",
            expected=params["projectVersion"],
            actual=store.revision(internal),
        )
    if digest(store._snapshot_projection(internal)) != params["inputSnapshotId"]:
        fault("IDENTITY_CONFLICT")


def _definition_row(store, project, scenario_id):
    row = load_definition(store, project, scenario_id)
    if row is None:
        # The frozen error catalog's NOT_FOUND resource vocabulary is fixed;
        # isolated scenarios reconcile under their owning operation identity.
        fault("NOT_FOUND", resource="operation")
    return row


def _run_row(store, project, run_id):
    row = load_run(store, project, run_id)
    if row is None:
        fault("NOT_FOUND", resource="operation")
    return row


def _scenario_run_rows(store, project, scenario_id):
    rows = []
    for run_id in indexed_run_ids(store, project):
        record = load_run(store, project, run_id)
        if record is not None and record["scenarioId"] == scenario_id:
            rows.append(record)
    return rows


# --- method handlers ------------------------------------------------------------------


def _create(store, params, origin):
    project = params["projectId"]
    configuration = params["configuration"]
    operation = params["operationId"]
    internal = resolve_active(store, project)
    configuration_digest = digest({"scenarioConfigurationVersion": 1, **configuration})
    with store._transaction():
        replay, fingerprint = _op_replay(store, project, operation, params)
        if replay is not None:
            return replay["result"]
        _cas_snapshot(store, internal, params)
        scenario_id = str(uuid4())
        definition, input_version = _build_definition(
            store, internal, project, scenario_id, configuration, params
        )
        result = {
            "projectId": project,
            "operationId": operation,
            "scenario": {
                "identity": _identity(
                    project,
                    scenario_id,
                    params,
                    input_version,
                    configuration_digest,
                    configuration,
                ),
                "configuration": configuration,
            },
        }
        _insert_detail(
            store,
            project,
            DEF_PREFIX + scenario_id,
            {
                "recordVersion": 1,
                "projectId": project,
                "scenarioId": scenario_id,
                "operationId": operation,
                "definition": asdict(definition),
                "definitionDigest": definition.digest,
                "identity": result["scenario"]["identity"],
                "configuration": configuration,
                "copiedFrom": None,
            },
        )
        _op_claim(
            store,
            project,
            operation,
            fingerprint,
            {"kind": "scenario.create", "scenarioId": scenario_id, "result": result},
        )
        return result


def _copy(store, params, origin):
    project = params["projectId"]
    operation = params["operationId"]
    internal = resolve_active(store, project)
    with store._transaction():
        replay, fingerprint = _op_replay(store, project, operation, params)
        if replay is not None:
            return replay["result"]
        _cas_snapshot(store, internal, params)
        source = _definition_row(store, project, params["scenarioId"])
        scenario_id = str(uuid4())
        configuration = {**source["configuration"], "name": params["name"]}
        definition, input_version = _build_definition(
            store, internal, project, scenario_id, configuration, params
        )
        configuration_digest = digest({"scenarioConfigurationVersion": 1, **configuration})
        result = {
            "projectId": project,
            "operationId": operation,
            "sourceScenarioId": params["scenarioId"],
            "scenario": {
                "identity": _identity(
                    project,
                    scenario_id,
                    params,
                    input_version,
                    configuration_digest,
                    configuration,
                ),
                "configuration": configuration,
            },
        }
        _insert_detail(
            store,
            project,
            DEF_PREFIX + scenario_id,
            {
                "recordVersion": 1,
                "projectId": project,
                "scenarioId": scenario_id,
                "operationId": operation,
                "definition": asdict(definition),
                "definitionDigest": definition.digest,
                "identity": result["scenario"]["identity"],
                "configuration": configuration,
                "copiedFrom": params["scenarioId"],
            },
        )
        _op_claim(
            store,
            project,
            operation,
            fingerprint,
            {"kind": "scenario.copy", "scenarioId": scenario_id, "result": result},
        )
        return result


def _list(store, params, origin):
    project = params["projectId"]
    resolve_active(store, project)
    identifiers = [
        value
        for value in indexed_scenarios(store, project)
        if params["cursor"] is None or value > params["cursor"]
    ]
    page = identifiers[: params["limit"]]
    items = []
    for scenario_id in page:
        record = _definition_row(store, project, scenario_id)
        items.append({"identity": record["identity"], "configuration": record["configuration"]})
    more = len(identifiers) > len(page)
    return {
        "projectId": project,
        "items": items,
        "nextCursor": page[-1] if more and page else None,
    }


def _read_scenario(store, params, origin):
    project = params["projectId"]
    resolve_active(store, project)
    with store._read():
        definition = _definition_row(store, project, params["scenarioId"])
        runs = _scenario_run_rows(store, project, params["scenarioId"])[:MAX_RUNS_PER_SCENARIO]
        return {
            "projectId": project,
            "scenario": {
                "identity": definition["identity"],
                "configuration": definition["configuration"],
            },
            "runs": [
                {
                    "runId": record["runId"],
                    "status": record["status"],
                    "lastCommittedRound": record["lastCommittedRound"],
                }
                for record in runs
            ],
        }


def _execute_run(store, project, record, definition, resume):
    """Claimed run execution; the finished rounds persist through one atomic
    run checkpoint transaction (every round boundary all-or-nothing)."""
    ports = _WirePorts(store, project, record["runId"])
    result = scenario_runner.run(
        definition,
        ports,
        cancelled=lambda: False,
        resume=resume,
    )
    with store._transaction():
        claim = _read_detail(store, project, RUN_PREFIX + record["runId"])
        if claim is None or claim.get("status") not in ("running", "queued"):
            fault("INVALID_STATE")
        if _read_detail(store, project, TERMINAL_PREFIX + record["runId"]) is not None:
            fault("INVALID_STATE")
        row = {
            **claim,
            "status": result.status,
            "rounds": ports.rounds,
            "lastCommittedRound": result.checkpoint.round,
            "checkpoint": asdict(result.checkpoint) if result.checkpoint.round else None,
            "pendingEvents": [event.id for event in result.pending],
            "error": "execution_failed" if result.status == "failed" else None,
        }
        _insert_detail(
            store,
            project,
            TERMINAL_PREFIX + record["runId"],
            {
                "recordVersion": 1,
                "projectId": project,
                "runId": record["runId"],
                "status": row["status"],
                "rounds": row["rounds"],
                "lastCommittedRound": row["lastCommittedRound"],
                "checkpoint": row["checkpoint"],
                "pendingEvents": row["pendingEvents"],
                "error": row["error"],
            },
        )
        return row


def _start_run(store, params, origin, *, source_run=None):
    project = params["projectId"]
    operation, run_id = params["operationId"], params["runId"]
    internal = resolve_active(store, project)
    with store._transaction():
        # Fail-closed before-run receipt reconciliation for this exact operation.
        checkpoint_ref = lookup_receipt(
            store, project, operation, "scenario", params["projectVersion"]
        )
        replay, fingerprint = _op_replay(store, project, operation, params)
        if replay is not None:
            # The claim and the run record were persisted by one transaction;
            # a claimed operation always has its exact durable run to reconcile.
            row = _run_row(store, project, replay["runId"])
            return _run_result(
                project,
                operation,
                row,
                source_run=source_run,
                resumed_from=replay.get("resumedFrom"),
            )
        _cas_snapshot(store, internal, params)
        definition_row = _definition_row(store, project, params["scenarioId"])
        definition = _definition_from_dict(definition_row["definition"])
        if definition.digest != definition_row["definitionDigest"]:
            fault("INVALID_STATE")
        resume_checkpoint = None
        if source_run is not None:
            source = _run_row(store, project, source_run)
            if source["scenarioId"] != params["scenarioId"]:
                fault("IDENTITY_CONFLICT")
            if source["status"] not in ("cancelled", "failed"):
                fault("INVALID_STATE")
            if (
                source["identity"]["configurationDigest"]
                != definition_row["identity"]["configurationDigest"]
                or source["identity"]["projectVersion"] != params["projectVersion"]
            ):
                # Config/input parity: reject mismatched source material.
                fault("IDENTITY_CONFLICT")
            matches = [
                entry
                for entry in source["rounds"]
                if entry["round"]["checkpointRef"] == params["checkpointRef"]
            ]
            if not matches:
                # Unknown checkpoint: no implicit resume, no blind replay.
                fault("IDENTITY_CONFLICT")
            resume_checkpoint = _checkpoint_from_dict(matches[0]["checkpoint"])
        if _read_detail(store, project, RUN_PREFIX + run_id) is not None:
            fault("IDENTITY_CONFLICT")
        record = {
            "recordVersion": 1,
            "projectId": project,
            "scenarioId": params["scenarioId"],
            "runId": run_id,
            "operationId": operation,
            "status": "running",
            "identity": definition_row["identity"],
            "evidence": _evidence(definition_row["configuration"]),
            "beforeRunCheckpointRef": checkpoint_ref,
            "sourceRunId": source_run,
            "resumedFrom": params.get("checkpointRef"),
            "rounds": [],
            "lastCommittedRound": 0,
            "checkpoint": None,
            "pendingEvents": [event["id"] for event in definition_row["definition"]["events"]],
            "error": None,
        }
        _insert_detail(store, project, RUN_PREFIX + run_id, record)
        # The operation claim rides the same transaction as the run record, so
        # a replayed operation always reconciles its exact durable run.
        _op_claim(
            store,
            project,
            operation,
            fingerprint,
            {
                "kind": "scenario.resume" if source_run else "scenario.run",
                "runId": run_id,
                "resumedFrom": params.get("checkpointRef"),
            },
        )
    row = _execute_run(store, project, record, definition, resume_checkpoint)
    return _run_result(
        project, operation, row, source_run=source_run, resumed_from=params.get("checkpointRef")
    )


def _run(store, params, origin):
    return _start_run(store, params, origin)


def _resume(store, params, origin):
    return _start_run(store, params, origin, source_run=params["sourceRunId"])


def _run_read(store, params, origin):
    project = params["projectId"]
    resolve_active(store, project)
    with store._read():
        row = _run_row(store, project, params["runId"])
        if row["scenarioId"] != params["scenarioId"]:
            fault("IDENTITY_CONFLICT")
        return {
            "projectId": project,
            "run": _run_dto(row, round_offset=params["roundOffset"], limit=params["limit"]),
        }


def _cancel(store, params, origin):
    project = params["projectId"]
    resolve_active(store, project)
    with store._transaction():
        row = _run_row(store, project, params["runId"])
        if row["scenarioId"] != params["scenarioId"]:
            fault("IDENTITY_CONFLICT")
        if row["status"] in ("succeeded", "failed"):
            # A terminal outcome can never become cancelled.
            fault("INVALID_STATE")
        if row["status"] != "cancelled":
            # Preserve every already-committed round; only the open tail ends.
            _insert_detail(
                store,
                project,
                TERMINAL_PREFIX + params["runId"],
                {
                    "recordVersion": 1,
                    "projectId": project,
                    "runId": params["runId"],
                    "status": "cancelled",
                    "rounds": row["rounds"],
                    "lastCommittedRound": row["lastCommittedRound"],
                    "checkpoint": row["checkpoint"],
                    "pendingEvents": (
                        _pending_ids(row["checkpoint"])
                        if row["checkpoint"] is not None
                        else row["pendingEvents"]
                    ),
                    "error": None,
                },
            )
            row = _run_row(store, project, params["runId"])
        return {
            "projectId": project,
            "operationId": params["operationId"],
            "run": _run_dto(row),
        }


def _compare(store, params, origin):
    project = params["projectId"]
    resolve_active(store, project)
    with store._read():
        picks = []
        for pick in params["runs"]:
            row = _run_row(store, project, pick["runId"])
            if row["scenarioId"] != pick["scenarioId"]:
                fault("IDENTITY_CONFLICT")
            if row["status"] != "succeeded":
                fault("INVALID_STATE")
            picks.append(row)
        runs = []
        for row in picks:
            rounds = [entry["round"] for entry in row["rounds"]]
            last = row["lastCommittedRound"]
            metrics = [
                {"round": entry["number"], "values": entry["metrics"]}
                for entry in rounds[params["roundOffset"] : params["roundOffset"] + params["limit"]]
            ]
            final = rounds[last - 1]["metrics"] if last else None
            runs.append(
                {
                    "runId": row["runId"],
                    "identity": row["identity"],
                    "status": "succeeded",
                    "lastCommittedRound": last,
                    "finalMetrics": final,
                    "metrics": metrics,
                }
            )
        return {"projectId": project, "roundOffset": params["roundOffset"], "runs": runs}


def _run_delete(store, params, origin):
    project = params["projectId"]
    resolve_active(store, project)
    with store._transaction():
        replay, fingerprint = _op_replay(store, project, params["operationId"], params)
        if replay is not None:
            return replay["result"]
        row = _run_row(store, project, params["runId"])
        if row["scenarioId"] != params["scenarioId"]:
            fault("IDENTITY_CONFLICT")
        if row["status"] in ACTIVE_STATES:
            # Restricted lifecycle entry: active runs are never deleted.
            fault("INVALID_STATE")
        # Restricted logical deletion: the evidence rows stay immutable.
        _insert_detail(
            store,
            project,
            TOMBSTONE_PREFIX + params["runId"],
            {
                "recordVersion": 1,
                "projectId": project,
                "runId": params["runId"],
                "scenarioId": params["scenarioId"],
                "deleted": True,
            },
        )
        result = {
            "projectId": project,
            "scenarioId": params["scenarioId"],
            "runId": params["runId"],
            "operationId": params["operationId"],
            "deleted": True,
        }
        _op_claim(
            store,
            project,
            params["operationId"],
            fingerprint,
            {"kind": "scenario.run.delete", "result": result},
        )
        return result


def _restore(store, params, origin):
    project = params["projectId"]
    operation = params["operationId"]
    internal = resolve_active(store, project)
    with store._transaction():
        replay, fingerprint = _op_replay(store, project, operation, params)
        if replay is not None:
            return replay["result"]
        _cas_snapshot(store, internal, params)
        definition = _definition_row(store, project, params["scenarioId"])
        if definition["identity"]["configurationDigest"] != params["configurationDigest"]:
            # The selected baseline must be the scenario's current baseline.
            fault("IDENTITY_CONFLICT")
        for record in _scenario_run_rows(store, project, params["scenarioId"]):
            # Isolated runs return to the baseline; formal facts are untouched.
            _insert_detail(
                store,
                project,
                TOMBSTONE_PREFIX + record["runId"],
                {
                    "recordVersion": 1,
                    "projectId": project,
                    "runId": record["runId"],
                    "scenarioId": params["scenarioId"],
                    "deleted": True,
                },
            )
        result = {
            "projectId": project,
            "operationId": operation,
            "configurationDigest": params["configurationDigest"],
            "scenario": {
                "identity": definition["identity"],
                "configuration": definition["configuration"],
            },
        }
        _op_claim(
            store,
            project,
            operation,
            fingerprint,
            {"kind": "scenario.restore", "scenarioId": params["scenarioId"], "result": result},
        )
        return result


_HANDLERS = {
    "project.scenario.create": _create,
    "project.scenario.copy": _copy,
    "project.scenario.list": _list,
    "project.scenario.read": _read_scenario,
    "project.scenario.run.read": _run_read,
    "project.scenario.run": _run,
    "project.scenario.cancel": _cancel,
    "project.scenario.resume": _resume,
    "project.scenario.compare": _compare,
    "project.scenario.run.delete": _run_delete,
    "project.scenario.restore": _restore,
}


def dispatch(store, method, params, origin):
    store._valid("params_" + method, params)
    result = _HANDLERS[method](store, params, origin)
    store._valid("result_" + method, result)
    return result
