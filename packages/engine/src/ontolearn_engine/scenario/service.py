"""T07 scenario wire services: isolated sandbox runs over the owned Store.

Eleven ``business3`` methods (selected-project authority, named-bridge exposure)
backed by :mod:`ontolearn_engine.scenario.model` / :mod:`ontolearn_engine.scenario.runner`
and durable namespaced SQLite storage. ``job_details`` is append-only evidence
(immutable by SQL trigger): every write mints a new row - a definition, an
operation claim, a run claim, committed round rows, a terminal checkpoint,
and tombstone markers for restricted deletion/isolated
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
)
from ontolearn_engine.scenario.runner import Checkpoint
from ontolearn_engine.scenario.working_copy import ScenarioCopy, configured_items
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
    if identity.startswith(TERMINAL_PREFIX) and record.get("roundLedger") is True:
        claim = _read_detail(store, project, RUN_PREFIX + record["runId"])
        rounds = _round_entries(store, project, claim)
        return {
            **record,
            "rounds": rounds,
            "checkpoint": rounds[-1]["checkpoint"] if rounds else claim["checkpoint"],
        }
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
        "SELECT id FROM job_details WHERE project=? AND id>=? AND id<? "
        "AND instr(substr(id, ?), ':')=0 ORDER BY rowid LIMIT ?",
        (project, RUN_PREFIX, RUN_PREFIX + "\uffff", len(RUN_PREFIX) + 1, RESULT_SCAN_CAP),
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
    state = store.state(internal)
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
            rules=canonical(configured_items(configuration["parameters"], "rules")),
            behaviors=canonical(configured_items(configuration["parameters"], "behaviors")),
            parameters=canonical(configuration["parameters"]),
            source=configuration["source"],
            assumptions=tuple(configuration["assumptions"]),
        )
        initial = ScenarioCopy(state, definition, configuration).initial(
            configuration["initialEdits"]
        )
        definition = replace(definition, initial=initial)
    except (ValueError, TypeError, KeyError):
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


def _round_prefix(run_id):
    return f"{RUN_PREFIX}{run_id}:round:"


def _round_entries(store, project, claim):
    prefix = _round_prefix(claim["runId"])
    rows = store._db.execute(
        "SELECT payload FROM job_details WHERE project=? AND id>=? AND id<? ORDER BY id",
        (project, prefix, prefix + "\uffff"),
    )
    definition = _definition_row(store, project, claim["scenarioId"])["definition"]
    events = scenario_runner.event_catalog(tuple(Event(**item) for item in definition["events"]))
    events = [asdict(event) for event in events.values()]
    rounds = []
    for row in rows:
        entry = json.loads(row["payload"])["entry"]
        checkpoint = entry["checkpoint"]
        checkpoint["events"] = [*events, *checkpoint.pop("generatedEvents")]
        state = checkpoint["state"]
        data = json.loads(state["assertions"])
        state["assertions"] = canonical({**data, "facts": entry["evidence"]["facts"]})
        if digest(checkpoint) != entry["round"]["checkpointRef"]:
            fault("INVALID_STATE")
        rounds.append(entry)
    return rounds


class _WirePorts(ScenarioCopy):
    """Append each successful round through the execution transaction."""

    def __init__(self, store, project, run_id, state, definition, configuration):
        super().__init__(state, definition, configuration)
        self.store, self.project, self.run_id = store, project, run_id
        self.rounds = []
        self.original_events = {event.id for event in definition.events}

    def commit(self, record, check):
        check()
        checkpoint = asdict(record.checkpoint)
        checkpoint_ref = digest(checkpoint)
        evidence = self.round_evidence(record)
        entry = {
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
                "behaviorTrace": evidence["actionTrace"],
                "beforeInference": record.before_inference.snapshot,
                "endInference": record.end_inference.snapshot,
                "checkpointRef": checkpoint_ref,
            },
            "checkpoint": checkpoint,
            "evidence": evidence,
            "planDigest": self.plan_digest(record.frozen_plan),
        }
        stored_state = dict(checkpoint["state"])
        data = json.loads(stored_state["assertions"])
        del data["facts"]
        stored_state["assertions"] = canonical(data)
        stored_checkpoint = {
            **{key: value for key, value in checkpoint.items() if key != "events"},
            "state": stored_state,
            "generatedEvents": [
                event for event in checkpoint["events"] if event["id"] not in self.original_events
            ],
        }
        with self.store._transaction():
            check()
            _insert_detail(
                self.store,
                self.project,
                f"{_round_prefix(self.run_id)}{record.checkpoint.round:04}",
                {
                    "projectId": self.project,
                    "runId": self.run_id,
                    "entry": {**entry, "checkpoint": stored_checkpoint},
                },
            )
        self.rounds.append(entry)


def _pending_ids(checkpoint_data):
    consumed = set(checkpoint_data["consumed"])
    return [event["id"] for event in checkpoint_data["events"] if event["id"] not in consumed]


def _run_dto(record, *, round_offset=None, limit=MAX_RUNS_PER_SCENARIO):
    rounds = [entry["round"] for entry in record["rounds"]]
    last = record["lastCommittedRound"]
    if round_offset is None:
        # Contract semantics: rounds[i].number == roundOffset + i + 1, so a
        # resumed run's page naturally starts at its first committed round.
        round_offset = rounds[0]["number"] - 1 if rounds else last
    # Paging is by round number (this run may start at a resumed round).
    rounds = [entry for entry in rounds if entry["number"] > round_offset][:limit]
    return {
        "runId": record["runId"],
        "identity": record["identity"],
        "scope": {"mode": "scenario", "scopeId": record["scenarioId"]},
        "status": record["status"],
        "lastCommittedRound": last,
        "rounds": rounds,
        "roundOffset": round_offset,
        "pendingEvents": record.get("pendingEvents", []),
        "checkpointRef": digest(record["checkpoint"]) if record["checkpoint"] is not None else None,
        "resumeAvailable": (record["status"] in ("cancelled", "failed") and bool(record["rounds"])),
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


def _execute_run(store, project, record, definition, resume, ports):
    """Finalize a run from its committed round ledger."""
    run_id = record["runId"]

    def cancelled():
        with store._read():
            return (
                _tombstoned(store, project, run_id)
                or _read_detail(store, project, TERMINAL_PREFIX + run_id) is not None
            )

    # The named request pre-pays one final material admission for execution.
    # Round savepoints are appended in that transaction and are published with
    # the terminal result, including the successful prefix of a failed run.
    with store._transaction():
        result = scenario_runner.run(
            definition,
            ports,
            cancelled=cancelled,
            resume=resume,
            finalize_resources=ports.finalize_resources,
        )
        claim = _read_detail(store, project, RUN_PREFIX + record["runId"])
        if claim is None or claim.get("status") not in ("running", "queued"):
            fault("INVALID_STATE")
        if _read_detail(store, project, TERMINAL_PREFIX + run_id) is not None:
            return _run_row(store, project, run_id)
        if _tombstoned(store, project, run_id):
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
                "roundLedger": True,
                "lastCommittedRound": row["lastCommittedRound"],
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
        identity = definition_row["identity"]
        if (
            identity["projectVersion"] != params["projectVersion"]
            or identity["inputSnapshotId"] != params["inputSnapshotId"]
        ):
            fault("IDENTITY_CONFLICT")
        try:
            ports = _WirePorts(
                store,
                project,
                run_id,
                store.state(internal),
                definition,
                definition_row["configuration"],
            )
        except (ValueError, TypeError, KeyError):
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
            checkpoint = matches[0]["checkpoint"]
            if digest(checkpoint) != params["checkpointRef"]:
                fault("IDENTITY_CONFLICT")
            resume_checkpoint = _checkpoint_from_dict(checkpoint)
            try:
                scenario_runner._validate_resume(definition, resume_checkpoint)
                saved_inference = matches[0].get("evidence", {}).get("inferred")
                if saved_inference is not None and (
                    ports.reasoner.infer(ports.read(resume_checkpoint.state)["facts"])
                    != (saved_inference, matches[0]["round"]["endInference"])
                ):
                    fault("IDENTITY_CONFLICT")
            except ValueError:
                fault("IDENTITY_CONFLICT")
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
            "lastCommittedRound": resume_checkpoint.round if resume_checkpoint else 0,
            "checkpoint": asdict(resume_checkpoint) if resume_checkpoint else None,
            "pendingEvents": (
                _pending_ids(asdict(resume_checkpoint))
                if resume_checkpoint
                else [event["id"] for event in definition_row["definition"]["events"]]
            ),
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
    row = _execute_run(store, project, record, definition, resume_checkpoint, ports)
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
