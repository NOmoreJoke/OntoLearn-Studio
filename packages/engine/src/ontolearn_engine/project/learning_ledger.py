"""T01 learning ledger: app_learning/app_assistance through "learning.record".

Every mutation runs inside one outer Store transaction (the caller's named
host owns authorization and budgets). The ledger never registers a capability,
never derives assistance from UI assertions and never rolls back committed
domain data: stale inputs are projected as "stale", not repaired. Downstream
tasks without an approved tool stay "pending-dependency"; nothing fabricates a
pass.
"""

import json
from copy import deepcopy
from uuid import uuid4

from ontolearn_engine.learning.baselines import read_json
from ontolearn_engine.learning.service import Attempt, Context
from ontolearn_engine.project import applications, format3
from ontolearn_engine.project.applications import RESTORE_WITHDRAWN
from ontolearn_engine.storage import Conflict

METHODS = frozenset(
    {
        "project.learning.read",
        "project.learning.attempt.start",
        "project.learning.hint.record",
        "project.learning.observation.record",
        "project.learning.task.check",
    }
)

# A persisted status in this set proves a real check executed against the
# bound snapshot; only then can a later domain edit project "stale".
EXECUTED_CHECK_STATUSES = frozenset(
    {"passed", "needs-repair", "failed", "tool-not-successful", "missing-evidence"}
)
ATTEMPT_PAYLOAD_VERSION = 1
PAYLOAD_KEYS = {
    "ledgerAttemptVersion",
    "taskId",
    "activationEpoch",
    "manifestSha256",
    "courseVersion",
    "glossaryVersion",
    "checksVersion",
    "courseExtensionVersion",
    "rootSnapshotRef",
    "boundSnapshotRef",
    "boundDomainRevision",
    "assistance",
    "maxHintLevel",
    "operationComplete",
    "independentTransferSuccess",
    "checkStatus",
    "lastFeedback",
    "evidenceIds",
    "observations",
    "completedGuidedStages",
    "guidedStageCheckpointRef",
    "lastOperationId",
}
GUIDED_STAGE_TASK = "business-ontology"
QUERY_TASK = "query"
# Tasks whose checks run against real persisted tool evidence in this build.
WIRED_TASKS = frozenset({GUIDED_STAGE_TASK, QUERY_TASK})
GUIDED_STAGE_LABEL = "完成引导阶段：业务本体建模"
HINT_EVENT_KIND = "hint.revealed"


def fault(code, **params):
    from ontolearn_engine.job_store import fault as job_fault

    job_fault(code, **params)


def _input_version(revision, snapshot_ref):
    return f"rev-{revision}:{snapshot_ref}"


def initial_payload(service, task_id, epoch, root_snapshot_ref, domain_revision):
    return {
        "ledgerAttemptVersion": ATTEMPT_PAYLOAD_VERSION,
        "taskId": task_id,
        "activationEpoch": epoch,
        "manifestSha256": service.manifest_sha256,
        "courseVersion": service.course_version,
        "glossaryVersion": service.glossary_version,
        "checksVersion": service.checks_version,
        "courseExtensionVersion": service.course_extension_version,
        "rootSnapshotRef": root_snapshot_ref,
        "boundSnapshotRef": None,
        "boundDomainRevision": None,
        "assistance": "independent",
        "maxHintLevel": 0,
        "operationComplete": False,
        "independentTransferSuccess": False,
        "checkStatus": "not-checked",
        "lastFeedback": None,
        "evidenceIds": [],
        "observations": {"openedReadingIds": [], "answeredAssessments": []},
        "completedGuidedStages": [],
        "guidedStageCheckpointRef": None,
        "lastOperationId": None,
    }


def _records(state):
    """Parse app_learning rows once; withdrawn rows keep only their tombstone."""
    out = []
    for row in state["learningCurrent"]:
        payload = json.loads(row["payload"])
        withdrawn = isinstance(payload, dict) and payload.get("status") == RESTORE_WITHDRAWN
        if not withdrawn and (not isinstance(payload, dict) or set(payload) != PAYLOAD_KEYS):
            raise Conflict("Learning record payload changed", category="state")
        out.append(
            {
                "attempt": row["attempt"],
                "recordVersion": row["record_version"],
                "course": row["course"],
                "task": row["task"],
                "payload": payload,
                "withdrawn": withdrawn,
            }
        )
    return out


def _current(records, task_id):
    live = [
        record
        for record in records
        if not record["withdrawn"] and record["payload"]["taskId"] == task_id
    ]
    if not live:
        return None
    return max(live, key=lambda record: record["payload"]["activationEpoch"])


def _next_epoch(records):
    """Creation ordinal over every row, withdrawn ones included.

    app_learning is append-only and a project restore only rewrites payloads,
    so counting all rows yields a number strictly greater than the epoch of
    every earlier attempt — even ones whose payload became a withdraw marker.
    """
    return len(records) + 1


def _reducer_attempt(record, context):
    payload = record["payload"]
    return Attempt(
        context=context,
        max_hint=payload["maxHintLevel"],
        assistance=payload["assistance"],
        operation_complete=payload["operationComplete"],
        independent_transfer_success=payload["independentTransferSuccess"],
        check_status=payload["checkStatus"],
        evidence_ids=tuple(payload["evidenceIds"]),
    )


def _public_readings(service, task_id):
    """Mounted material verbatim except the local answer key stays engine-side."""
    readings = []
    for reading in service.readings_for(task_id):
        view = {
            key: deepcopy(reading[key])
            for key in ("id", "title", "sourceRef", "optional", "summary", "content")
        }
        assessment = reading.get("selfAssessment")
        if assessment is not None:
            view["selfAssessment"] = [
                {
                    "question": item["question"],
                    "options": [
                        {"id": option["id"], "text": option["text"]} for option in item["options"]
                    ],
                }
                for item in assessment
            ]
        readings.append(view)
    return readings


def _revealed_hints(service, task, max_hint_level):
    revealed = []
    for level in range(1, max_hint_level + 1):
        hint = task["hints"][level - 1]
        revealed.append({"level": level, "kind": hint["kind"], "text": hint["text"]})
    return revealed


def _task_view(service, task, records, snapshot_ref, revision):
    task_id = task["id"]
    rows = [
        record
        for record in records
        if (
            record["payload"]["taskId"] == task_id
            if not record["withdrawn"]
            else record["task"] == task_id
        )
    ]
    withdrawn_count = sum(record["withdrawn"] for record in rows)
    current = _current(records, task_id)
    view = {
        "taskId": task_id,
        "module": task["module"],
        "goal": task["goal"],
        "instructions": task["instructions"],
        "steps": deepcopy(task.get("steps", [])),
        "completionCondition": task["completionCondition"],
        "commonErrors": deepcopy(task["commonErrors"]),
        "knowledgePoints": deepcopy(task["knowledgePoints"]),
        "transfer": bool(task["transfer"]),
        "next": task["next"],
        "checks": list(task["checks"]),
        "readings": _public_readings(service, task_id),
        "attemptCount": len(rows) - withdrawn_count,
        "withdrawnAttemptCount": withdrawn_count,
        "attemptId": None,
        "attemptActivationEpoch": None,
        "recordVersion": None,
        "assistance": "independent",
        "maxHintLevel": 0,
        "revealedHints": [],
        "operationComplete": False,
        "independentTransferSuccess": False,
        "checkStatus": "not-checked",
        "staleInput": False,
        "lastFeedback": None,
        "observations": {"openedReadingIds": [], "answeredAssessments": []},
        "completedGuidedStages": [],
        "guidedStageCheckpointRef": None,
        "rootSnapshotRef": None,
        "boundSnapshotRef": None,
        "boundDomainRevision": None,
        "inputVersion": _input_version(revision, snapshot_ref),
    }
    if current is None:
        return view
    payload = current["payload"]
    stale = (
        payload["checkStatus"] in EXECUTED_CHECK_STATUSES
        and payload["boundSnapshotRef"] is not None
        and payload["boundSnapshotRef"] != snapshot_ref
    )
    view.update(
        attemptId=current["attempt"],
        attemptActivationEpoch=payload["activationEpoch"],
        recordVersion=current["recordVersion"],
        assistance=payload["assistance"],
        maxHintLevel=payload["maxHintLevel"],
        revealedHints=_revealed_hints(service, task, payload["maxHintLevel"]),
        operationComplete=payload["operationComplete"],
        independentTransferSuccess=payload["independentTransferSuccess"],
        checkStatus="stale" if stale else payload["checkStatus"],
        staleInput=stale,
        lastFeedback=deepcopy(payload["lastFeedback"]),
        observations=deepcopy(payload["observations"]),
        completedGuidedStages=list(payload["completedGuidedStages"]),
        guidedStageCheckpointRef=payload["guidedStageCheckpointRef"],
        rootSnapshotRef=payload["rootSnapshotRef"],
        boundSnapshotRef=payload["boundSnapshotRef"],
        boundDomainRevision=payload["boundDomainRevision"],
    )
    return view


def read_projection(store, project, service):
    internal = store._project(project)
    checkpoint = store.project_checkpoint(internal)
    state = format3.application_state(store, internal)
    records = _records(state)
    snapshot_ref = checkpoint["domainSnapshotRef"]
    revision = checkpoint["domainRevision"]
    return {
        "learningReadVersion": 1,
        "projectId": project,
        "domainRevision": revision,
        "domainSnapshotRef": snapshot_ref,
        "inputVersion": _input_version(revision, snapshot_ref),
        "templateRef": checkpoint["application"]["metadata"]["templateRef"],
        "withdrawnAttemptCount": sum(record["withdrawn"] for record in records),
        "tasks": [
            _task_view(service, task, records, snapshot_ref, revision)
            for task in service.course["tasks"]
        ],
        "courseMeta": {
            "courseVersion": service.course_version,
            "glossaryVersion": service.glossary_version,
            "checksVersion": service.checks_version,
            "courseExtensionVersion": service.course_extension_version,
            "manifestSha256": service.manifest_sha256,
            "case": service.course["case"],
            "businessQuestion": service.course["businessQuestion"],
            "firstTask": service.course["firstTask"],
        },
        "glossary": deepcopy(service.glossary["entries"]),
    }


def _task_state(store, project, service, task_id):
    internal = store._project(project)
    checkpoint = store.project_checkpoint(internal)
    records = _records(format3.application_state(store, internal))
    task = service.tasks[task_id]
    view = _task_view(
        service, task, records, checkpoint["domainSnapshotRef"], checkpoint["domainRevision"]
    )
    return view, checkpoint


def _record_view(record):
    payload = record["payload"]
    return {
        "attemptId": record["attempt"],
        "recordVersion": record["recordVersion"],
        "course": record["course"],
        "task": record["task"],
        "activationEpoch": payload["activationEpoch"],
        "assistance": payload["assistance"],
        "maxHintLevel": payload["maxHintLevel"],
        "operationComplete": payload["operationComplete"],
        "independentTransferSuccess": payload["independentTransferSuccess"],
        "checkStatus": payload["checkStatus"],
        "guidedStageCheckpointRef": payload["guidedStageCheckpointRef"],
    }


def _write_record(store, project, operation, record, payload, assistance_event, origin):
    change = {
        "type": "learning.record",
        "attempt": record["attempt"],
        "course": record["course"],
        "task": record["task"],
        "expectedRecordVersion": record["recordVersion"],
        "payload": payload,
        "assistanceEvent": assistance_event,
    }
    return store.apply_application(
        project, operation, change, actor=origin["hostClientId"], permission="write"
    )


def _auto_init(store, project, service, task_id, origin):
    """First write inside the caller's transaction when no attempt exists yet."""
    internal = store._project(project)
    checkpoint = store.project_checkpoint(internal)
    records = _records(format3.application_state(store, internal))
    attempt_id, operation = str(uuid4()), str(uuid4())
    payload = initial_payload(
        service,
        task_id,
        _next_epoch(records),
        checkpoint["domainSnapshotRef"],
        checkpoint["domainRevision"],
    )
    payload["lastOperationId"] = operation
    change = {
        "type": "learning.record",
        "attempt": attempt_id,
        "course": service.course_version,
        "task": task_id,
        "expectedRecordVersion": None,
        "payload": payload,
        "assistanceEvent": None,
    }
    store.apply_application(
        project, operation, change, actor=origin["hostClientId"], permission="write"
    )
    return {
        "attempt": attempt_id,
        "recordVersion": 1,
        "course": service.course_version,
        "task": task_id,
        "payload": payload,
        "withdrawn": False,
    }


def _claimed_change(store, internal, operation):
    context = applications.claim_context(store, internal, operation)
    change = context["request"]["change"]
    if not isinstance(change, dict) or change.get("type") != "learning.record":
        fault("IDENTITY_CONFLICT")
    return change


def _row_version(store, internal, attempt):
    row = store._db.execute(
        "SELECT record_version FROM app_learning WHERE project=? AND attempt=?",
        (internal, attempt),
    ).fetchone()
    if row is None:
        fault("INVALID_STATE")
    return row[0]


def _require_task(service, task_id):
    if task_id not in service.tasks:
        fault("INVALID_REQUEST", field="params")


def start_attempt(store, project, params, service, origin):
    task_id = params["taskId"]
    _require_task(service, task_id)
    operation = params["operationId"]
    with store._transaction():
        internal = store._project(project)
        if store.has_operation_claim(operation):
            change = _claimed_change(store, internal, operation)
            if change["task"] != task_id:
                fault("IDENTITY_CONFLICT")
            task_view, _ = _task_state(store, project, service, task_id)
            return {
                "learningAttemptStartVersion": 1,
                "projectId": project,
                "operationId": operation,
                "taskId": task_id,
                "attemptId": change["attempt"],
                "activationEpoch": change["payload"]["activationEpoch"],
                "recordVersion": _row_version(store, internal, change["attempt"]),
                "inputVersion": task_view["inputVersion"],
                "rootSnapshotRef": change["payload"]["rootSnapshotRef"],
                "operationSequence": None,
                "afterCheckpointRef": None,
                "replayed": True,
                "learningState": task_view,
            }
        checkpoint = store.project_checkpoint(internal)
        records = _records(format3.application_state(store, internal))
        attempt_id = str(uuid4())
        payload = initial_payload(
            service,
            task_id,
            _next_epoch(records),
            checkpoint["domainSnapshotRef"],
            checkpoint["domainRevision"],
        )
        payload["lastOperationId"] = operation
        change = {
            "type": "learning.record",
            "attempt": attempt_id,
            "course": service.course_version,
            "task": task_id,
            "expectedRecordVersion": None,
            "payload": payload,
            "assistanceEvent": None,
        }
        receipt = store.apply_application(
            project, operation, change, actor=origin["hostClientId"], permission="write"
        )
        task_view, _ = _task_state(store, project, service, task_id)
        return {
            "learningAttemptStartVersion": 1,
            "projectId": project,
            "operationId": operation,
            "taskId": task_id,
            "attemptId": attempt_id,
            "activationEpoch": payload["activationEpoch"],
            "recordVersion": _row_version(store, internal, attempt_id),
            "inputVersion": _input_version(
                checkpoint["domainRevision"], checkpoint["domainSnapshotRef"]
            ),
            "rootSnapshotRef": payload["rootSnapshotRef"],
            "operationSequence": receipt["operationSequence"],
            "afterCheckpointRef": receipt["afterCheckpointRef"],
            "replayed": False,
            "learningState": task_view,
        }


def record_hint(store, project, params, service, origin):
    task_id = params["taskId"]
    _require_task(service, task_id)
    level = params["level"]
    operation = params["operationId"]
    with store._transaction():
        internal = store._project(project)
        if store.has_operation_claim(operation):
            change = _claimed_change(store, internal, operation)
            event = change["assistanceEvent"]
            if change["task"] != task_id or event is None:
                fault("IDENTITY_CONFLICT")
            task_view, _ = _task_state(store, project, service, task_id)
            hint = service.tasks[task_id]["hints"][event["payload"]["level"] - 1]
            record = _current(_records(format3.application_state(store, internal)), task_id)
            if record is None:
                fault("INVALID_STATE")
            return {
                "learningHintRecordVersion": 1,
                "projectId": project,
                "operationId": operation,
                "taskId": task_id,
                "attemptId": change["attempt"],
                "recordVersion": _row_version(store, internal, change["attempt"]),
                "assistanceEventId": event["eventId"],
                "level": event["payload"]["level"],
                "revealedHint": {
                    "level": event["payload"]["level"],
                    "kind": hint["kind"],
                    "text": hint["text"],
                },
                "record": _record_view(record),
                "learningState": task_view,
            }
        records = _records(format3.application_state(store, internal))
        current = _current(records, task_id)
        if current is None:
            current = _auto_init(store, project, service, task_id, origin)
        checkpoint = store.project_checkpoint(internal)
        context = Context(
            project,
            task_id,
            current["attempt"],
            _input_version(checkpoint["domainRevision"], checkpoint["domainSnapshotRef"]),
        )
        updated, _text = service.hint(_reducer_attempt(current, context), level)
        payload = deepcopy(current["payload"])
        payload.update(
            maxHintLevel=updated.max_hint,
            assistance=updated.assistance,
            independentTransferSuccess=False,
            lastOperationId=operation,
        )
        event_id = str(uuid4())
        _write_record(
            store,
            project,
            operation,
            current,
            payload,
            {
                "eventId": event_id,
                "payload": {
                    "kind": HINT_EVENT_KIND,
                    "level": level,
                    "taskId": task_id,
                    "operationId": operation,
                },
            },
            origin,
        )
        hint = service.tasks[task_id]["hints"][level - 1]
        current = {
            **current,
            "recordVersion": _row_version(store, internal, current["attempt"]),
            "payload": payload,
        }
        task_view, _ = _task_state(store, project, service, task_id)
        return {
            "learningHintRecordVersion": 1,
            "projectId": project,
            "operationId": operation,
            "taskId": task_id,
            "attemptId": current["attempt"],
            "recordVersion": current["recordVersion"],
            "assistanceEventId": event_id,
            "level": level,
            "revealedHint": {"level": level, "kind": hint["kind"], "text": hint["text"]},
            "record": _record_view(current),
            "learningState": task_view,
        }


def _validate_observation(service, task_id, observation):
    if not isinstance(observation, dict):
        fault("INVALID_REQUEST", field="params")
    kind = observation.get("kind")
    readings = {reading["id"]: reading for reading in service.readings_for(task_id)}
    if kind == "reading-opened":
        if set(observation) != {"kind", "readingId"} or observation["readingId"] not in readings:
            fault("INVALID_REQUEST", field="params")
        return None
    if kind == "self-assessment-answered":
        expected = {"kind", "readingId", "questionIndex", "selectedOptionId"}
        if set(observation) != expected or observation["readingId"] not in readings:
            fault("INVALID_REQUEST", field="params")
        reading = readings[observation["readingId"]]
        assessment = reading.get("selfAssessment")
        index = observation["questionIndex"]
        if (
            not isinstance(assessment, list)
            or type(index) is not int
            or not 0 <= index < len(assessment)
        ):
            fault("INVALID_REQUEST", field="params")
        item = assessment[index]
        options = {option["id"] for option in item["options"]}
        if observation["selectedOptionId"] not in options:
            fault("INVALID_REQUEST", field="params")
        return {
            "correct": observation["selectedOptionId"] == item["answerKey"],
            "explanation": item["explanation"],
        }
    fault("INVALID_REQUEST", field="params")


def record_observation(store, project, params, service, origin):
    task_id = params["taskId"]
    _require_task(service, task_id)
    operation = params["operationId"]
    observation = params["observation"]
    outcome = _validate_observation(service, task_id, observation)
    with store._transaction():
        internal = store._project(project)
        if store.has_operation_claim(operation):
            change = _claimed_change(store, internal, operation)
            if change["task"] != task_id:
                fault("IDENTITY_CONFLICT")
            task_view, _ = _task_state(store, project, service, task_id)
            return {
                "learningObservationRecordVersion": 1,
                "projectId": project,
                "operationId": operation,
                "taskId": task_id,
                "attemptId": change["attempt"],
                "recordVersion": _row_version(store, internal, change["attempt"]),
                "observation": observation,
                "assessmentOutcome": outcome,
                "learningState": task_view,
            }
        records = _records(format3.application_state(store, internal))
        current = _current(records, task_id)
        if current is None:
            current = _auto_init(store, project, service, task_id, origin)
        payload = deepcopy(current["payload"])
        observations = payload["observations"]
        if observation["kind"] == "reading-opened":
            if observation["readingId"] not in observations["openedReadingIds"]:
                observations["openedReadingIds"].append(observation["readingId"])
        else:
            # Observations never touch completion or assistance attribution.
            observations["answeredAssessments"].append(
                {
                    "readingId": observation["readingId"],
                    "questionIndex": observation["questionIndex"],
                    "selectedOptionId": observation["selectedOptionId"],
                    "correct": outcome["correct"],
                }
            )
        payload["lastOperationId"] = operation
        _write_record(store, project, operation, current, payload, None, origin)
        current = {
            **current,
            "recordVersion": _row_version(store, internal, current["attempt"]),
            "payload": payload,
        }
        task_view, _ = _task_state(store, project, service, task_id)
        return {
            "learningObservationRecordVersion": 1,
            "projectId": project,
            "operationId": operation,
            "taskId": task_id,
            "attemptId": current["attempt"],
            "recordVersion": current["recordVersion"],
            "observation": observation,
            "assessmentOutcome": outcome,
            "learningState": task_view,
        }


def _state_triples(state):
    from ontolearn_engine.rdf_snapshot import term

    triples = set()
    for definition in state["definitions"]:
        if definition["layer"] != "ontology":
            continue
        payload = json.loads(definition["payload"])
        if not isinstance(payload, dict):
            continue
        for triple in payload.get("triples", []):
            triples.add((triple["subject"], triple["predicate"], term(triple["object"]).n3()))
    for fact in state["facts"]:
        if fact["object"] is not None:
            triples.add((fact["subject"], fact["predicate"], term(fact["object"]).n3()))
    return triples


def baseline_triples(root):
    from ontolearn_engine.rdf_snapshot import term

    data = read_json(root / "tests/fixtures/product-baselines/G-base.json")
    triples = set()
    for triple in data["ontology"]:
        triples.add((triple["subject"], triple["predicate"], term(triple["object"]).n3()))
    for triple in data["facts"]:
        triples.add((triple["subject"], triple["predicate"], term(triple["object"]).n3()))
    return triples


def _attempt_min_claim_rowid(store, project, internal, attempt_id, is_virgin_first_attempt):
    """The operation-claim rowid where this attempt's window opens.

    A virgin first attempt (auto-created by ``check`` itself) opens at 0: the
    learner may already have run the real queries before the first explicit
    check. Otherwise the attempt's creation claim (expectedRecordVersion is
    None) marks the boundary; earlier jobs belong to earlier attempts.
    """
    if is_virgin_first_attempt:
        return 0
    for row in store._db.execute(
        "SELECT rowid,context FROM operation_claims WHERE kind=? AND project=? ORDER BY rowid",
        ("application", project),
    ).fetchall():
        if row["context"] is None:
            continue
        request = json.loads(row["context"]).get("request")
        change = request.get("change") if isinstance(request, dict) else None
        if not isinstance(change, dict):
            continue
        if (
            change.get("type") == "learning.record"
            and change.get("attempt") == attempt_id
            and change.get("expectedRecordVersion") is None
        ):
            return row["rowid"]
    # The creation claim always precedes this point; 0 is the conservative floor.
    return 0


def check_task(store, project, params, host, origin):
    service = host.bare_service()
    task_id = params["taskId"]
    _require_task(service, task_id)
    operation = params["operationId"]
    with store._transaction():
        internal = store._project(project)
        if store.has_operation_claim(operation):
            change = _claimed_change(store, internal, operation)
            if change["task"] != task_id:
                fault("IDENTITY_CONFLICT")
            receipt = format3.receipt_for(store, internal, operation)
            task_view, _ = _task_state(store, project, service, task_id)
            # The persisted attempt row, not the claim snapshot, carries the
            # final payload: later guided-stage bookkeeping bumped it.
            current = _current(_records(format3.application_state(store, internal)), task_id)
            if current is None or current["attempt"] != change["attempt"]:
                fault("INVALID_STATE")
            return _check_result(
                project,
                operation,
                task_id,
                change["attempt"],
                _row_version(store, internal, change["attempt"]),
                task_view["inputVersion"],
                current["payload"],
                receipt["operationSequence"],
                receipt["afterCheckpointRef"],
                task_view,
            )
        records = _records(format3.application_state(store, internal))
        current = _current(records, task_id)
        had_any_task_attempt = any(
            (
                record["payload"]["taskId"] == task_id
                if not record["withdrawn"]
                else record["task"] == task_id
            )
            for record in records
        )
        was_auto_init = current is None
        if current is None:
            current = _auto_init(store, project, service, task_id, origin)
        checkpoint = store.project_checkpoint(internal)
        snapshot_ref = checkpoint["domainSnapshotRef"]
        revision = checkpoint["domainRevision"]
        input_version = _input_version(revision, snapshot_ref)
        context = Context(project, task_id, current["attempt"], input_version)
        attempt = _reducer_attempt(current, context)
        wired = task_id in WIRED_TASKS
        if wired:
            if task_id == GUIDED_STAGE_TASK:
                host.tools.evidence = host.ontology_evidence(
                    context,
                    snapshot_ref,
                    _state_triples(store.state(internal)),
                    host.baseline_triples(),
                    current["payload"]["assistance"],
                )
            else:
                host.tools.evidence_by_check = host.query_evidences(
                    store,
                    project,
                    internal,
                    context,
                    snapshot_ref,
                    _attempt_min_claim_rowid(
                        store,
                        project,
                        internal,
                        current["attempt"],
                        was_auto_init and not had_any_task_attempt,
                    ),
                    current["payload"]["assistance"],
                )
            check_service = host.wired_service()
        else:
            # Real pending dependency: downstream tools are not wired yet.
            check_service = service
        try:
            updated, feedback = check_service.check(attempt)
        finally:
            host.tools.clear()
        payload = deepcopy(current["payload"])
        payload.update(
            assistance=updated.assistance,
            operationComplete=updated.operation_complete,
            independentTransferSuccess=updated.independent_transfer_success,
            checkStatus=updated.check_status,
            evidenceIds=list(updated.evidence_ids),
            lastFeedback={
                "status": feedback.status,
                "completed": list(feedback.completed),
                "repairs": list(feedback.repairs),
                "suggestions": list(feedback.suggestions),
                "knowledgePoints": list(feedback.knowledge_points),
                "evidenceIds": list(feedback.evidence_ids),
            },
            boundSnapshotRef=snapshot_ref,
            boundDomainRevision=revision,
            lastOperationId=operation,
        )
        receipt = _write_record(store, project, operation, current, payload, None, origin)
        guided_ref = payload["guidedStageCheckpointRef"]
        # FR-004 anti-regression: only the guided-stage task itself mints the
        # checkpoint; passing the query task (or any later wired task) never
        # creates a "guided stage complete" checkpoint.
        if (
            task_id == GUIDED_STAGE_TASK
            and updated.check_status == "passed"
            and GUIDED_STAGE_TASK not in payload["completedGuidedStages"]
        ):
            # FR-004: exactly one guided-stage checkpoint per first pass, with
            # every write sharing this single outer transaction.
            current = {
                **current,
                "recordVersion": _row_version(store, internal, current["attempt"]),
                "payload": payload,
            }
            stage_payload = deepcopy(payload)
            stage_payload["completedGuidedStages"] = [
                *payload["completedGuidedStages"],
                GUIDED_STAGE_TASK,
            ]
            stage_payload["lastOperationId"] = operation + ":guided-stage"
            _write_record(store, project, str(uuid4()), current, stage_payload, None, origin)
            checkpoint_receipt = store.apply_application(
                project,
                str(uuid4()),
                {
                    "type": "checkpoint.create",
                    "reason": "guided-stage",
                    "label": GUIDED_STAGE_LABEL,
                },
                actor=origin["hostClientId"],
                permission="write",
            )
            guided_ref = checkpoint_receipt["afterCheckpointRef"]
            current = {
                **current,
                "recordVersion": _row_version(store, internal, current["attempt"]),
                "payload": stage_payload,
            }
            payload = deepcopy(stage_payload)
            payload["guidedStageCheckpointRef"] = guided_ref
            payload["lastOperationId"] = operation + ":guided-checkpoint"
            _write_record(store, project, str(uuid4()), current, payload, None, origin)
            receipt = checkpoint_receipt
        task_view, _ = _task_state(store, project, service, task_id)
        return _check_result(
            project,
            operation,
            task_id,
            current["attempt"],
            _row_version(store, internal, current["attempt"]),
            input_version,
            payload,
            receipt["operationSequence"],
            receipt["afterCheckpointRef"],
            task_view,
        )


def _check_result(
    project,
    operation,
    task_id,
    attempt_id,
    record_version,
    input_version,
    payload,
    sequence,
    after_ref,
    task_view,
):
    return {
        "learningTaskCheckVersion": 1,
        "projectId": project,
        "operationId": operation,
        "taskId": task_id,
        "attemptId": attempt_id,
        "recordVersion": record_version,
        "inputVersion": input_version,
        "checkStatus": payload["checkStatus"],
        "operationComplete": payload["operationComplete"],
        "independentTransferSuccess": payload["independentTransferSuccess"],
        "assistance": payload["assistance"],
        "feedback": deepcopy(payload["lastFeedback"]),
        "evidenceIds": list(payload["evidenceIds"]),
        "guidedStageCheckpointRef": payload["guidedStageCheckpointRef"],
        "operationSequence": sequence,
        "afterCheckpointRef": after_ref,
        "learningState": task_view,
    }


def dispatch(store, method, params, host, origin):
    if method == "project.learning.read":
        store._valid("params_project.learning.read", params)
        return read_projection(store, params["projectId"], host.bare_service())
    if method == "project.learning.attempt.start":
        store._valid("params_project.learning.attempt.start", params)
        return start_attempt(store, params["projectId"], params, host.bare_service(), origin)
    if method == "project.learning.hint.record":
        store._valid("params_project.learning.hint.record", params)
        return record_hint(store, params["projectId"], params, host.bare_service(), origin)
    if method == "project.learning.observation.record":
        store._valid("params_project.learning.observation.record", params)
        return record_observation(store, params["projectId"], params, host.bare_service(), origin)
    store._valid("params_project.learning.task.check", params)
    return check_task(store, params["projectId"], params, host, origin)
