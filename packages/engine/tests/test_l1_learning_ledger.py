"""L1 learning ledger: T01 rows, closed-whitelist ontology checks, FR-004 checkpoint.

Covers learning.record CAS/audit semantics, observation isolation, copy-current
exclusions, whole-project restore withdrawal with strictly increasing epochs,
the real persisted ontology-model comparison and the guided-stage checkpoint.
"""

import base64
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.learning.baselines import read_json, store_seed_plan
from ontolearn_engine.project import format3
from ontolearn_engine.project.applications import RESTORE_WITHDRAWN
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import Conflict, digest

ROOT = Path(__file__).resolve().parents[3]

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
PERSON = "urn:ontolearn:learning:Person"
ASSIGNED_TO = "urn:ontolearn:learning:assignedTo"
PERSON_L01 = "urn:ontolearn:learning:person/L01"
EQUIPMENT_001 = "urn:ontolearn:learning:equipment/001"
OWL_CLASS = "<http://www.w3.org/2002/07/owl#Class>"
RDFS_CLASS = "<http://www.w3.org/2000/01/rdf-schema#Class>"
OWL_OBJECT_PROPERTY = "<http://www.w3.org/2002/07/owl#ObjectProperty>"
OWL_DATATYPE_PROPERTY = "<http://www.w3.org/2002/07/owl#DatatypeProperty>"
PERSON_REF = "<urn:ontolearn:learning:Person>"
PERSON_L01_REF = "<urn:ontolearn:learning:person/L01>"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
RDFS_DOMAIN = "http://www.w3.org/2000/01/rdf-schema#domain"
DEVIATION_PERSON_AS_CLASS = "当前练习把具体人员建成了类：类回答‘是哪一类’，个体回答‘是哪一个’。"
DEVIATION_ASSIGNED_TO_DATATYPE = "人员是另一个对象，应使用对象属性。"

PASSING_ONTOLOGY = [
    (PERSON, RDF_TYPE, OWL_CLASS),
    (ASSIGNED_TO, RDF_TYPE, OWL_OBJECT_PROPERTY),
]
PASSING_FACTS = [
    (PERSON_L01, RDF_TYPE, PERSON_REF),
    (EQUIPMENT_001, ASSIGNED_TO, PERSON_L01_REF),
]


def uid():
    return str(uuid4())


def frame(actor, method, params):
    return {
        "kind": "request",
        "id": uid(),
        "protocolVersion": 2 if method == "hello" else 3,
        "engineSessionId": None if method == "hello" else actor.session,
        "method": method,
        "params": params,
    }


def exchange(actor, method, params):
    request = frame(actor, method, params)
    response = actor.request(request)
    actor.finish_query_reply(request["id"], emitted=True)
    return response


def ok(response):
    assert response["ok"], response
    return response["result"]


def denied(response, code):
    assert not response["ok"] and response["error"]["code"] == code, response
    return response["error"]


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "l1.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    yield actor, store
    actor.mainline.close()
    store.close()


@pytest.fixture
def store(tmp_path):
    s = JobStore(tmp_path / "p.db", contract=CONTRACT, target_format=3)
    s.create_project("p")
    s.project = s.public_project("p")
    s.actor = uid()
    yield s
    s.close()


def open_blank(actor, name="L1 学习项目"):
    created = ok(
        exchange(
            actor,
            "project.create",
            {
                "requestVersion": 1,
                "operationId": uid(),
                "name": name,
                "initialization": {"kind": "blank"},
            },
        )
    )
    project = created["projectId"]
    ok(exchange(actor, "project.open", {"projectId": project}))
    return project


def seeded(actor, store, name="L1 学习项目"):
    """A selected blank project whose domain state is exactly G-base."""
    project = open_blank(actor, name)
    internal = store._project(project)
    plan = store_seed_plan(ROOT, "G-base")
    store.commit(internal, store.revision(internal), uid(), uid(), **plan)
    return project


def commit_domain(store, project, triples=(), facts=(), replace_ontology=None):
    internal = store._project(project)
    definitions = []
    if replace_ontology is not None:
        definitions.append(replace_ontology)
    if triples:
        definitions.append(
            {
                "layer": "ontology",
                "id": "learning-additions",
                "value": {
                    "triples": [{"subject": s, "predicate": p, "object": o} for s, p, o in triples]
                },
            }
        )
    manual = [
        {"id": digest([s, p, o]), "subject": s, "predicate": p, "object": o} for s, p, o in facts
    ]
    return store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=definitions or None,
        manual=manual or None,
    )


def learning(actor, method, params):
    return ok(exchange(actor, method, params))


def read_state(actor, project):
    return learning(actor, "project.learning.read", {"projectId": project})


def task_view(state, task_id):
    view = next(item for item in state["tasks"] if item["taskId"] == task_id)
    assert view["taskId"] == task_id
    return view


def start_attempt(actor, project, task_id, operation=None):
    return learning(
        actor,
        "project.learning.attempt.start",
        {
            "projectId": project,
            "operationId": operation or uid(),
            "taskId": task_id,
        },
    )


def record_hint(actor, project, task_id, level, operation=None):
    return learning(
        actor,
        "project.learning.hint.record",
        {
            "projectId": project,
            "operationId": operation or uid(),
            "taskId": task_id,
            "level": level,
        },
    )


def record_observation(actor, project, task_id, observation, operation=None):
    return learning(
        actor,
        "project.learning.observation.record",
        {
            "projectId": project,
            "operationId": operation or uid(),
            "taskId": task_id,
            "observation": observation,
        },
    )


def check_task(actor, project, task_id, operation=None):
    return learning(
        actor,
        "project.learning.task.check",
        {
            "projectId": project,
            "operationId": operation or uid(),
            "taskId": task_id,
        },
    )


def rows(store, project):
    return format3.application_state(store, store._project(project))


def attempt_payload(store, project, attempt):
    row = next(r for r in rows(store, project)["learningCurrent"] if r["attempt"] == attempt)
    return json.loads(row["payload"]), row


# --- learning.record application semantics ----------------------------------


def record_change(attempt, payload, expected=None, event=None):
    return {
        "type": "learning.record",
        "attempt": attempt,
        "course": "offline-course-2",
        "task": "business-ontology",
        "expectedRecordVersion": expected,
        "payload": payload,
        "assistanceEvent": event,
    }


def apply(store, change, operation=None):
    return store.apply_application(
        store.project, operation or uid(), change, actor=store.actor, permission="write"
    )


def logical(path):
    return format3.logical_hash(sqlite3.connect(path))


def test_learning_record_cas_conflict_is_rejected_without_side_effect(store):
    attempt = uid()
    first = apply(store, record_change(attempt, {"v": 1}))
    assert first["operationKind"] == "application"
    payload, row = attempt_payload(store, store.project, attempt)
    assert payload == {"v": 1} and row["record_version"] == 1
    before = logical(store.path)
    with pytest.raises(Conflict, match="Learning record version changed"):
        apply(store, record_change(attempt, {"v": 2}, expected=2))
    with pytest.raises(Conflict):
        apply(store, record_change(attempt, {"v": 2}, expected=None))
    assert logical(store.path) == before
    second = apply(store, record_change(attempt, {"v": 2}, expected=1))
    assert second["applicationAfterCAS"] == [
        {"scope": "learning", "identity": attempt, "version": 2}
    ]
    assert attempt_payload(store, store.project, attempt)[1]["record_version"] == 2


def test_assistance_audit_is_immutable_write_then_read_and_unique(store):
    attempt = uid()
    event = {"eventId": uid(), "payload": {"kind": "hint.revealed", "level": 1}}
    apply(store, record_change(attempt, {"v": 1}, event=event))
    state = rows(store, store.project)
    assert len(state["assistanceAudit"]) == 1
    audit = state["assistanceAudit"][0]
    assert audit["sequence"] == 1 and audit["attempt"] == attempt
    assert audit["event_id"] == event["eventId"]
    assert json.loads(audit["payload"]) == event["payload"]
    second_event = {"eventId": uid(), "payload": {"kind": "hint.revealed", "level": 2}}
    apply(store, record_change(attempt, {"v": 2}, expected=1, event=second_event))
    assert [row["sequence"] for row in rows(store, store.project)["assistanceAudit"]] == [1, 2]
    before = logical(store.path)
    with pytest.raises(Conflict):
        # A replayed eventId is rejected rather than silently deduplicated.
        apply(store, record_change(attempt, {"v": 3}, expected=2, event=second_event))
    assert logical(store.path) == before
    with pytest.raises(sqlite3.DatabaseError, match="immutable application evidence"):
        store._db.execute(
            "UPDATE app_assistance SET payload='{}' WHERE project=? AND sequence=1",
            (store._project(store.project),),
        )
    store._db.rollback()


def test_audit_row_lands_after_its_learning_row_in_one_change(store):
    fresh = uid()
    event = {"eventId": uid(), "payload": {"kind": "hint.revealed", "level": 1}}
    # A brand-new attempt may carry its first assistance event in the same
    # change: the commit writes the app_learning row before app_assistance.
    apply(store, record_change(fresh, {"v": 1}, event=event))
    audit = rows(store, store.project)["assistanceAudit"]
    assert [row["attempt"] for row in audit] == [fresh]
    # An event for a stale version of a missing attempt is a plain CAS fault.
    with pytest.raises(Conflict, match="Learning record version changed"):
        apply(store, record_change(uid(), {"v": 1}, expected=3, event=event))


# --- projection, attempts, hints, observations ------------------------------


def test_read_projection_shape_size_and_zero_hint_leak(owned):
    actor, store = owned
    project = seeded(actor, store)
    state = read_state(actor, project)
    assert [item["taskId"] for item in state["tasks"]] == [
        "business-ontology",
        "mapping",
        "query",
        "quality",
        "behavior",
        "scenario",
        "transfer-repair",
        "transfer-classify",
        "report",
    ]
    internal = store._project(project)
    checkpoint = store.project_checkpoint(internal)
    expected_version = f"rev-{checkpoint['domainRevision']}:{checkpoint['domainSnapshotRef']}"
    assert state["inputVersion"] == expected_version
    assert state["domainSnapshotRef"] == checkpoint["domainSnapshotRef"]
    assert state["templateRef"] is None
    ontology = task_view(state, "business-ontology")
    assert ontology["checkStatus"] == "not-checked" and ontology["revealedHints"] == []
    assert ontology["maxHintLevel"] == 0 and ontology["attemptId"] is None
    assert [reading["id"] for reading in ontology["readings"]] == ["business-question"]
    # The local answer key never leaves the engine with the reading material.
    raw = json.dumps(ontology["readings"], ensure_ascii=False)
    assert "answerKey" not in raw and "answer" not in raw
    assert len(state["glossary"]) == 27
    assert state["courseMeta"]["case"] == "设备运维"
    assert state["courseMeta"]["firstTask"] == "business-ontology"
    assert len(state["courseMeta"]["manifestSha256"]) == 64
    # 256 KiB frame budget: the full read must stay far below it.
    assert len(json.dumps(state, ensure_ascii=False).encode("utf-8")) <= 122880


def test_attempt_start_allocates_epoch_and_replays_idempotently(owned):
    actor, store = owned
    project = seeded(actor, store)
    operation = uid()
    first = start_attempt(actor, project, "business-ontology", operation)
    assert first["replayed"] is False and first["activationEpoch"] == 1
    assert first["recordVersion"] == 1 and first["attemptId"] != operation
    payload, _row = attempt_payload(store, project, first["attemptId"])
    assert payload["assistance"] == "independent"
    assert payload["checkStatus"] == "not-checked" and payload["maxHintLevel"] == 0
    assert payload["completedGuidedStages"] == [] and payload["guidedStageCheckpointRef"] is None
    assert payload["rootSnapshotRef"] == first["rootSnapshotRef"]
    second = start_attempt(actor, project, "business-ontology", operation)
    assert second["replayed"] is True and second["attemptId"] == first["attemptId"]
    assert len(rows(store, project)["learningCurrent"]) == 1
    # A second fresh attempt strictly increases the creation epoch.
    later = start_attempt(actor, project, "business-ontology")
    assert later["activationEpoch"] == 2


def test_hint_level_four_persists_full_demonstration_and_replays(owned):
    actor, store = owned
    project = seeded(actor, store)
    operation = uid()
    first = record_hint(actor, project, "business-ontology", 4, operation)
    assert first["level"] == 4 and first["revealedHint"]["level"] == 4
    payload, _row = attempt_payload(store, project, first["attemptId"])
    assert payload["assistance"] == "full-demonstration"
    assert payload["maxHintLevel"] == 4 and payload["independentTransferSuccess"] is False
    state = read_state(actor, project)
    ontology = task_view(state, "business-ontology")
    assert [hint["level"] for hint in ontology["revealedHints"]] == [1, 2, 3, 4]
    assert ontology["assistance"] == "full-demonstration"
    replay = record_hint(actor, project, "business-ontology", 4, operation)
    assert replay["assistanceEventId"] == first["assistanceEventId"]
    audit = rows(store, project)["assistanceAudit"]
    assert len(audit) == 1 and audit[0]["event_id"] == first["assistanceEventId"]
    assert json.loads(audit[0]["payload"])["kind"] == "hint.revealed"
    # Lower levels never downgrade the persisted maximum.
    partial = record_hint(actor, project, "business-ontology", 2)
    payload, _row = attempt_payload(store, project, partial["attemptId"])
    assert payload["maxHintLevel"] == 4 and payload["assistance"] == "full-demonstration"


def test_observations_never_touch_completion_or_assistance(owned):
    actor, store = owned
    project = seeded(actor, store)
    course = read_json(ROOT / "content/learning/course.json")
    reading = next(
        r for t in course["tasks"] if t["id"] == "business-ontology" for r in t["readings"]
    )
    question = reading["selfAssessment"][0]
    right = record_observation(
        actor,
        project,
        "business-ontology",
        {
            "kind": "self-assessment-answered",
            "readingId": reading["id"],
            "questionIndex": 0,
            "selectedOptionId": question["answerKey"],
        },
    )
    assert right["assessmentOutcome"]["correct"] is True
    assert right["assessmentOutcome"]["explanation"] == question["explanation"]
    wrong_option = next(o["id"] for o in question["options"] if o["id"] != question["answerKey"])
    wrong = record_observation(
        actor,
        project,
        "business-ontology",
        {
            "kind": "self-assessment-answered",
            "readingId": reading["id"],
            "questionIndex": 0,
            "selectedOptionId": wrong_option,
        },
    )
    assert wrong["assessmentOutcome"]["correct"] is False
    opened = record_observation(
        actor,
        project,
        "business-ontology",
        {"kind": "reading-opened", "readingId": reading["id"]},
    )
    assert opened["assessmentOutcome"] is None
    state = read_state(actor, project)
    ontology = task_view(state, "business-ontology")
    assert ontology["observations"]["openedReadingIds"] == [reading["id"]]
    assert len(ontology["observations"]["answeredAssessments"]) == 2
    assert ontology["observations"]["answeredAssessments"][0]["correct"] is True
    assert ontology["operationComplete"] is False and ontology["assistance"] == "independent"
    assert ontology["maxHintLevel"] == 0 and ontology["checkStatus"] == "not-checked"
    assert rows(store, project)["assistanceAudit"] == []
    denied(
        exchange(
            actor,
            "project.learning.observation.record",
            {
                "projectId": project,
                "operationId": uid(),
                "taskId": "business-ontology",
                "observation": {"kind": "reading-opened", "readingId": "not-mounted"},
            },
        ),
        "INVALID_REQUEST",
    )


# --- real ontology-model checks ---------------------------------------------


def test_unwired_tasks_stay_pending_dependency(owned):
    actor, store = owned
    project = seeded(actor, store)
    result = check_task(actor, project, "mapping")
    assert result["checkStatus"] == "pending-dependency"
    assert result["operationComplete"] is False
    assert any("等待批准的实际工具接入" in repair for repair in result["feedback"]["repairs"])
    payload, _row = attempt_payload(store, project, result["attemptId"])
    assert payload["checkStatus"] == "pending-dependency"


@pytest.mark.parametrize("person_class", [OWL_CLASS, RDFS_CLASS])
def test_business_ontology_pass_creates_unique_guided_stage_checkpoint(owned, person_class):
    actor, store = owned
    project = seeded(actor, store)
    commit_domain(
        store,
        project,
        triples=[(PERSON, RDF_TYPE, person_class), (ASSIGNED_TO, RDF_TYPE, OWL_OBJECT_PROPERTY)],
        facts=PASSING_FACTS,
    )
    operation = uid()
    result = check_task(actor, project, "business-ontology", operation)
    assert result["checkStatus"] == "passed" and result["operationComplete"] is True
    head = store.project_checkpoint(store._project(project))
    assert result["evidenceIds"] == [head["domainSnapshotRef"]]
    guided = result["guidedStageCheckpointRef"]
    assert guided is not None and len(guided) == 64
    payload, _row = attempt_payload(store, project, result["attemptId"])
    assert payload["completedGuidedStages"] == ["business-ontology"]
    assert payload["guidedStageCheckpointRef"] == guided
    listing = ok(
        exchange(
            actor,
            "project.checkpoint.list",
            {"projectId": project, "pageSize": 50, "cursor": None},
        )
    )
    # The final guided-checkpoint bookkeeping record lands above it by sequence;
    # the guided-stage evidence itself is addressed by its checkpoint ref.
    guided_item = next(item for item in listing["items"] if item["checkpointRef"] == guided)
    assert guided_item["reason"] == "guided-stage"
    assert guided_item["label"] == "完成引导阶段：业务本体建模"
    # Idempotent replay and a genuine re-check never mint a second checkpoint.
    replay = check_task(actor, project, "business-ontology", operation)
    assert replay["guidedStageCheckpointRef"] == guided and replay["recordVersion"] >= 1
    again = check_task(actor, project, "business-ontology")
    assert again["guidedStageCheckpointRef"] == guided
    stages = [
        item
        for item in ok(
            exchange(
                actor,
                "project.checkpoint.list",
                {"projectId": project, "pageSize": 50, "cursor": None},
            )
        )["items"]
        if item["reason"] == "guided-stage"
    ]
    assert len(stages) == 1
    # The guided checkpoint is previewable like any whole-project restore target.
    state = ok(exchange(actor, "project.management.read", {"projectId": project}))
    preview = ok(
        exchange(
            actor,
            "project.restore.preview",
            {
                "projectId": project,
                "targetCheckpointRef": guided,
                "expectedCheckpointRef": state["checkpointRef"],
                "expectedLifecycleVersion": state["lifecycle"]["version"],
            },
        )
    )
    assert preview["targetCheckpointRef"] == guided


def test_allowed_label_passes_but_extra_predicate_fails(owned):
    actor, store = owned
    project = seeded(actor, store)
    commit_domain(
        store,
        project,
        triples=[
            (PERSON, RDF_TYPE, OWL_CLASS),
            (ASSIGNED_TO, RDF_TYPE, OWL_OBJECT_PROPERTY),
            (PERSON, RDFS_LABEL, '"人员"'),
        ],
        facts=PASSING_FACTS,
    )
    labelled = check_task(actor, project, "business-ontology")
    assert labelled["checkStatus"] == "passed"
    commit_domain(
        store,
        project,
        triples=[(PERSON, RDFS_DOMAIN, f"<{EQUIPMENT_001}>")],
        facts=[],
    )
    extra = check_task(actor, project, "business-ontology")
    assert extra["checkStatus"] == "needs-repair"
    assert any("白名单之外的新增" in repair for repair in extra["feedback"]["repairs"])
    assert extra["operationComplete"] is False


def test_removed_triples_are_rejected(owned):
    actor, store = owned
    project = seeded(actor, store)
    ontology = next(
        d for d in store.state(store._project(project))["definitions"] if d["layer"] == "ontology"
    )
    trimmed = {
        "layer": "ontology",
        "id": ontology["id"],
        "value": {"triples": json.loads(ontology["payload"])["triples"][:9]},
    }
    commit_domain(
        store,
        project,
        triples=[(PERSON, RDF_TYPE, OWL_CLASS), (ASSIGNED_TO, RDF_TYPE, OWL_OBJECT_PROPERTY)],
        facts=PASSING_FACTS,
        replace_ontology=trimmed,
    )
    result = check_task(actor, project, "business-ontology")
    assert result["checkStatus"] == "needs-repair"
    assert any("不能删除既有三元组" in repair for repair in result["feedback"]["repairs"])


def test_person_as_class_deviation_is_diagnosed_without_rollback(owned):
    actor, store = owned
    project = seeded(actor, store)
    commit_domain(
        store,
        project,
        triples=[
            (PERSON, RDF_TYPE, OWL_CLASS),
            (ASSIGNED_TO, RDF_TYPE, OWL_OBJECT_PROPERTY),
            (PERSON_L01, RDF_TYPE, OWL_CLASS),
        ],
        facts=[(EQUIPMENT_001, ASSIGNED_TO, PERSON_L01_REF)],
    )
    result = check_task(actor, project, "business-ontology")
    assert result["checkStatus"] == "needs-repair"
    assert any(DEVIATION_PERSON_AS_CLASS in repair for repair in result["feedback"]["repairs"])
    # The check reports deviations; it never rolls back committed domain data.
    triples = {
        (triple["subject"], triple["predicate"], triple["object"])
        for definition in store.state(store._project(project))["definitions"]
        if definition["layer"] == "ontology"
        for triple in json.loads(definition["payload"])["triples"]
    }
    assert (PERSON_L01, RDF_TYPE, OWL_CLASS) in triples
    assert result["guidedStageCheckpointRef"] is None


def test_assigned_to_datatype_property_deviation(owned):
    actor, store = owned
    project = seeded(actor, store)
    commit_domain(
        store,
        project,
        triples=[
            (PERSON, RDF_TYPE, OWL_CLASS),
            (ASSIGNED_TO, RDF_TYPE, OWL_DATATYPE_PROPERTY),
        ],
        facts=PASSING_FACTS,
    )
    result = check_task(actor, project, "business-ontology")
    assert result["checkStatus"] == "needs-repair"
    assert any(DEVIATION_ASSIGNED_TO_DATATYPE in repair for repair in result["feedback"]["repairs"])


def test_domain_change_after_pass_projects_stale_with_hint_level_preserved(owned):
    actor, store = owned
    project = seeded(actor, store)
    commit_domain(
        store,
        project,
        triples=PASSING_ONTOLOGY,
        facts=PASSING_FACTS,
    )
    record_hint(actor, project, "business-ontology", 2)
    passed = check_task(actor, project, "business-ontology")
    assert passed["checkStatus"] == "passed"
    fresh = read_state(actor, project)
    ontology = task_view(fresh, "business-ontology")
    assert ontology["staleInput"] is False and ontology["checkStatus"] == "passed"
    # Any committed domain edit moves the snapshot; the check goes stale.
    commit_domain(store, project, facts=[(EQUIPMENT_001, RDFS_LABEL, '"泵站A标记"')])
    stale = read_state(actor, project)
    ontology = task_view(stale, "business-ontology")
    assert ontology["staleInput"] is True and ontology["checkStatus"] == "stale"
    assert ontology["maxHintLevel"] == 2
    assert [hint["level"] for hint in ontology["revealedHints"]] == [1, 2]
    assert ontology["assistance"] == "partial-hints"
    assert ontology["completedGuidedStages"] == ["business-ontology"]


# --- copy-current exclusions and whole-project restore ----------------------


def copy_current(actor, store, project, name):
    from ontolearn_engine.project import management

    internal = store._project(project)
    checkpoint = store.project_checkpoint(internal)
    life = management.lifecycle(store, internal)
    viewed = ok(
        exchange(
            actor,
            "project.management.preview",
            {
                "projectId": project,
                "action": {"kind": "copy-current", "name": name},
                "expectedCheckpointRef": digest(checkpoint),
                "expectedLifecycleVersion": life["version"],
            },
        )
    )
    confirmed = ok(
        exchange(
            actor,
            "project.management.confirm",
            {
                "projectId": project,
                "previewRef": viewed["previewRef"],
                "documentHash": viewed["documentHash"],
            },
        )
    )
    return ok(
        exchange(
            actor,
            "project.management.apply",
            {
                "projectId": project,
                "operationId": uid(),
                "confirmationRef": confirmed["confirmationRef"],
                "documentHash": viewed["documentHash"],
            },
        )
    )


def test_copy_current_succeeds_with_learning_and_excludes_it(owned):
    actor, store = owned
    project = seeded(actor, store)
    record_hint(actor, project, "business-ontology", 3)
    copied = copy_current(actor, store, project, "副本")
    target = copied["targetProjectId"]
    assert target != project
    copied_state = rows(store, target)
    assert copied_state["learningCurrent"] == [] and copied_state["assistanceAudit"] == []
    source_state = rows(store, project)
    assert len(source_state["learningCurrent"]) == 1
    assert len(source_state["assistanceAudit"]) == 1


def read_restore_document(actor, project, preview):
    hashes, cursor = [], None
    while True:
        page = ok(
            exchange(
                actor,
                "project.restore.page",
                {"projectId": project, "previewRef": preview["previewRef"], "cursor": cursor},
            )
        )
        for segment in page["segments"]:
            hashes.append(segment["sha256"])
            base64.b64decode(segment["dataBase64"])
        cursor = page["nextCursor"]
        if cursor is None:
            break
    return hashes


def test_project_restore_withdraws_attempts_and_epoch_increases(owned):
    actor, store = owned
    project = seeded(actor, store)
    checkpoint = ok(
        exchange(
            actor,
            "project.checkpoint.create",
            {"projectId": project, "operationId": uid(), "label": "学习之前"},
        )
    )
    target = checkpoint["checkpointRef"]
    attempt = start_attempt(actor, project, "business-ontology")
    record_hint(actor, project, "business-ontology", 1)
    state = ok(exchange(actor, "project.management.read", {"projectId": project}))
    preview = ok(
        exchange(
            actor,
            "project.restore.preview",
            {
                "projectId": project,
                "targetCheckpointRef": target,
                "expectedCheckpointRef": state["checkpointRef"],
                "expectedLifecycleVersion": state["lifecycle"]["version"],
            },
        )
    )
    hashes = read_restore_document(actor, project, preview)
    confirmation = ok(
        exchange(
            actor,
            "project.restore.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
                "readSegmentHashes": hashes,
            },
        )
    )
    ok(
        exchange(
            actor,
            "project.restore.apply",
            {
                "projectId": project,
                "operationId": uid(),
                "confirmationRef": confirmation["confirmationRef"],
                "documentHash": preview["documentHash"],
            },
        )
    )
    payload, row = attempt_payload(store, project, attempt["attemptId"])
    assert payload == {
        "status": RESTORE_WITHDRAWN,
        "restoredToCheckpointRef": target,
    }
    assert row["record_version"] >= 2
    # The immutable assistance audit survives the restore untouched.
    assert len(rows(store, project)["assistanceAudit"]) == 1
    after = read_state(actor, project)
    ontology = task_view(after, "business-ontology")
    assert ontology["attemptId"] is None and ontology["checkStatus"] == "not-checked"
    assert ontology["withdrawnAttemptCount"] == 1 and ontology["revealedHints"] == []
    assert after["withdrawnAttemptCount"] == 1
    restarted = start_attempt(actor, project, "business-ontology")
    assert restarted["activationEpoch"] > attempt["activationEpoch"]
    assert restarted["activationEpoch"] == 2


def test_learning_record_rejects_domain_plan(store):
    from ontolearn_engine.project import applications

    forged = {
        **record_change(uid(), {"v": 1}),
        "domain": {"base": 0, "plan": {}},
    }
    with pytest.raises(Conflict):
        applications.check_change(forged)
    with pytest.raises(Conflict):
        apply(store, forged)


def test_start_attempt_preserves_assistance_floor_and_guided_stage_checkpoint(owned):
    actor, store = owned
    project = seeded(actor, store)
    record_hint(actor, project, "business-ontology", 4)
    commit_domain(store, project, PASSING_ONTOLOGY, PASSING_FACTS)
    first_pass = check_task(actor, project, "business-ontology")
    assert first_pass["checkStatus"] == "passed"
    assert first_pass["assistance"] == "full-demonstration"
    assert first_pass["guidedStageCheckpointRef"] is not None

    restarted = start_attempt(actor, project, "business-ontology")
    assert restarted["activationEpoch"] == 2
    state = restarted["learningState"]
    assert state["assistance"] == "full-demonstration"
    assert state["maxHintLevel"] == 4
    assert state["independentTransferSuccess"] is False
    assert state["completedGuidedStages"] == ["business-ontology"]
    assert state["guidedStageCheckpointRef"] == first_pass["guidedStageCheckpointRef"]
    assert [hint["level"] for hint in state["revealedHints"]] == [1, 2, 3, 4]

    second_pass = check_task(actor, project, "business-ontology")
    assert second_pass["checkStatus"] == "passed"
    assert second_pass["assistance"] == "full-demonstration"
    assert second_pass["independentTransferSuccess"] is False
    assert second_pass["guidedStageCheckpointRef"] == first_pass["guidedStageCheckpointRef"]
    checkpoints = ok(
        exchange(
            actor,
            "project.checkpoint.list",
            {"projectId": project, "pageSize": 20, "cursor": None},
        )
    )
    guided = [item for item in checkpoints["items"] if item["reason"] == "guided-stage"]
    assert len(guided) == 1


def test_project_restore_to_pre_hint_checkpoint_preserves_attempt_assistance_floor(owned):
    actor, store = owned
    project = seeded(actor, store)
    attempt = start_attempt(actor, project, "business-ontology")
    checkpoint = ok(
        exchange(
            actor,
            "project.checkpoint.create",
            {"projectId": project, "operationId": uid(), "label": "已开局未看提示"},
        )
    )
    target = checkpoint["checkpointRef"]
    record_hint(actor, project, "business-ontology", 4)
    state = ok(exchange(actor, "project.management.read", {"projectId": project}))
    preview = ok(
        exchange(
            actor,
            "project.restore.preview",
            {
                "projectId": project,
                "targetCheckpointRef": target,
                "expectedCheckpointRef": state["checkpointRef"],
                "expectedLifecycleVersion": state["lifecycle"]["version"],
            },
        )
    )
    hashes = read_restore_document(actor, project, preview)
    confirmation = ok(
        exchange(
            actor,
            "project.restore.confirm",
            {
                "projectId": project,
                "previewRef": preview["previewRef"],
                "documentHash": preview["documentHash"],
                "readSegmentHashes": hashes,
            },
        )
    )
    ok(
        exchange(
            actor,
            "project.restore.apply",
            {
                "projectId": project,
                "operationId": uid(),
                "confirmationRef": confirmation["confirmationRef"],
                "documentHash": preview["documentHash"],
            },
        )
    )
    payload, _row = attempt_payload(store, project, attempt["attemptId"])
    assert payload["assistance"] == "full-demonstration"
    assert payload["maxHintLevel"] == 4
    assert payload["independentTransferSuccess"] is False
    view = task_view(read_state(actor, project), "business-ontology")
    assert view["assistance"] == "full-demonstration"
    assert view["maxHintLevel"] == 4
    assert view["independentTransferSuccess"] is False


def test_observation_replay_rejects_different_payload_and_returns_persisted_outcome(owned):
    actor, store = owned
    project = seeded(actor, store)
    course = read_json(ROOT / "content/learning/course.json")
    reading = next(
        r
        for t in course["tasks"]
        if t["id"] == "business-ontology"
        for r in t["readings"]
        if r.get("selfAssessment")
    )
    question = reading["selfAssessment"][0]
    wrong_option = next(o["id"] for o in question["options"] if o["id"] != question["answerKey"])
    op = uid()
    first = record_observation(
        actor,
        project,
        "business-ontology",
        {
            "kind": "self-assessment-answered",
            "readingId": reading["id"],
            "questionIndex": 0,
            "selectedOptionId": question["answerKey"],
        },
        operation=op,
    )
    replay = record_observation(
        actor,
        project,
        "business-ontology",
        {
            "kind": "self-assessment-answered",
            "readingId": reading["id"],
            "questionIndex": 0,
            "selectedOptionId": question["answerKey"],
        },
        operation=op,
    )
    assert replay == first
    denied(
        exchange(
            actor,
            "project.learning.observation.record",
            {
                "projectId": project,
                "operationId": op,
                "taskId": "business-ontology",
                "observation": {
                    "kind": "self-assessment-answered",
                    "readingId": reading["id"],
                    "questionIndex": 0,
                    "selectedOptionId": wrong_option,
                },
            },
        ),
        "IDENTITY_CONFLICT",
    )


def test_learning_operation_id_conflict_and_check_replay_receipt(owned):
    actor, store = owned
    project = seeded(actor, store, "项目甲")
    op_start = uid()
    start_attempt(actor, project, "business-ontology", op_start)
    op_hint = uid()
    record_hint(actor, project, "business-ontology", 4, op_hint)

    denied(
        exchange(
            actor,
            "project.learning.hint.record",
            {
                "projectId": project,
                "operationId": op_hint,
                "taskId": "business-ontology",
                "level": 1,
            },
        ),
        "IDENTITY_CONFLICT",
    )
    denied(
        exchange(
            actor,
            "project.learning.hint.record",
            {
                "projectId": project,
                "operationId": op_start,
                "taskId": "business-ontology",
                "level": 1,
            },
        ),
        "IDENTITY_CONFLICT",
    )
    denied(
        exchange(
            actor,
            "project.learning.task.check",
            {"projectId": project, "operationId": op_start, "taskId": "business-ontology"},
        ),
        "IDENTITY_CONFLICT",
    )

    other = seeded(actor, store, "项目乙")
    denied(
        exchange(
            actor,
            "project.learning.hint.record",
            {"projectId": other, "operationId": op_hint, "taskId": "business-ontology", "level": 4},
        ),
        "IDENTITY_CONFLICT",
    )

    ok(exchange(actor, "project.open", {"projectId": project}))
    commit_domain(store, project, PASSING_ONTOLOGY, PASSING_FACTS)
    op_check = uid()
    checked = check_task(actor, project, "business-ontology", op_check)
    assert checked["guidedStageCheckpointRef"] is not None
    replayed = check_task(actor, project, "business-ontology", op_check)
    assert replayed["operationSequence"] == checked["operationSequence"]
    assert replayed["afterCheckpointRef"] == checked["afterCheckpointRef"]
    assert replayed["guidedStageCheckpointRef"] == checked["guidedStageCheckpointRef"]
