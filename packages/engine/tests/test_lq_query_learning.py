"""Lq query-task learning: real persisted Q-01/Q-02 checks through the ledger.

Every query runs through the real JobStore + Coordinator worker path and
publishes a real resultId/query payload; the check derives its evidence from
the persisted operation claims, never from UI assertions. Attempts isolate
their evidence windows by claim rowid, and passing ``query`` never mints a
guided-stage checkpoint.
"""

import asyncio
import json
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.learning.baselines import read_json
from ontolearn_engine.resources import CONTRACT, LIMITS, semantic_identity
from ontolearn_engine.storage import digest

ROOT = Path(__file__).resolve().parents[3]

A01 = "urn:ontolearn:learning:alarm/A01"
STATUS = "urn:ontolearn:learning:status"
EQUIPMENT_002 = "urn:ontolearn:learning:equipment/002"
ASSIGNED_TO = "urn:ontolearn:learning:assignedTo"
WORKER_TIMEOUT = 30

UNCLOSED_HIGH = (
    "PREFIX l: <urn:ontolearn:learning:>\n"
    "SELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . "
    '?alarm l:level "High" ; l:status "Open" . } ORDER BY ?alarm'
)
# The classic mistake: only the level filter, so A02 leaks into the rows.
UNCLOSED_HIGH_MISSING_STATUS = (
    "PREFIX l: <urn:ontolearn:learning:>\n"
    "SELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . "
    '?alarm l:level "High" . } ORDER BY ?alarm'
)


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


@pytest.fixture
def owned(tmp_path):
    store = JobStore(tmp_path / "lq.sqlite", contract=CONTRACT, target_format=3)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    yield actor, store
    actor.mainline.close()
    store.close()


def open_blank(actor, name="Lq 查询学习项目"):
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


def g_base_plan(query_text=UNCLOSED_HIGH):
    """The executable G-base seed: ontology triples, facts, managed query.

    Unlike the learning fixture importer this payload shape is accepted by the
    real query executor (no fixtureVersions keys on the ontology definition).
    """
    data = read_json(ROOT / "tests/fixtures/product-baselines/G-base.json")
    definitions = [
        {
            "layer": "ontology",
            "id": "G-base.ontology",
            "value": {
                "triples": data["ontology"],
                "singleValuedPredicates": data["singleValuedPredicates"],
            },
        },
        {
            "layer": "query",
            "id": "unclosed-high",
            "value": {
                "text": query_text,
                "references": [],
                "descriptor": {
                    "version": 1,
                    "name": "未闭环高危告警",
                    "description": "查询未闭环高危告警",
                    "scope": "asserted",
                    "capabilityQuestion": "哪些设备存在未闭环高危告警？",
                    "source": "editor",
                },
            },
        },
    ]
    manual = [
        {"id": digest([t["subject"], t["predicate"], t["object"]]), **t} for t in data["facts"]
    ]
    return {"definitions": definitions, "manual": manual}


def seeded(actor, store, name="Lq 查询学习项目", query_text=UNCLOSED_HIGH):
    """A selected blank project whose domain state is exactly G-base."""
    project = open_blank(actor, name)
    internal = store._project(project)
    plan = g_base_plan(query_text)
    store.commit(internal, store.revision(internal), uid(), uid(), **plan)
    return project


def commit_query_definition(store, project, text=UNCLOSED_HIGH):
    """Replace the managed unclosed-high definition with a new text."""
    internal = store._project(project)
    return store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        definitions=[
            {
                "layer": "query",
                "id": "unclosed-high",
                "value": {
                    "text": text,
                    "references": [],
                    "descriptor": {
                        "version": 1,
                        "name": "未闭环高危告警",
                        "description": "查询未闭环高危告警",
                        "scope": "asserted",
                        "capabilityQuestion": "哪些设备存在未闭环高危告警？",
                        "source": "editor",
                    },
                },
            }
        ],
    )


def fact_id(subject, predicate, obj):
    return digest([subject, predicate, obj])


def current_fact(store, project, subject, predicate):
    return next(
        fact
        for fact in store.state(store._project(project))["facts"]
        if fact["subject"] == subject and fact["predicate"] == predicate
    )


def set_a01_status(store, project, obj):
    """Real Store edit of the A01 status fact (single atomic commit)."""
    internal = store._project(project)
    old = current_fact(store, project, A01, STATUS)
    return store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        edits={old["id"]: obj},
    )


def add_extra_fact(
    store, project, subject=EQUIPMENT_002, obj="<urn:ontolearn:learning:person/L01>"
):
    internal = store._project(project)
    return store.commit(
        internal,
        store.revision(internal),
        uid(),
        uid(),
        manual=[
            {
                "id": fact_id(subject, ASSIGNED_TO, obj),
                "subject": subject,
                "predicate": ASSIGNED_TO,
                "object": obj,
            }
        ],
    )


def accept_query(store, project, selection="current", snapshot=None, definition="unclosed-high"):
    if snapshot is None:
        snapshot = store.project_get(project)["inputSnapshotId"]
    input_ = {
        "inputSnapshotId": snapshot,
        "scope": "asserted",
        "definitionId": definition,
        "parametersHash": store.put_blob(project, {"inputSelection": selection}),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    return store.create_job(
        project, uid(), "query.execute", input_, None, semantic_identity(), LIMITS
    )


async def run_job(store, project, job):
    actor = Coordinator(
        store,
        profile="business3",
        _ready=_JOB_READY,
        test_mode=True,
        allowed_projects={project},
        emit=lambda _message: None,
    )
    actor.version = 3
    actor.session = uid()
    actor.subscriptions[uid()] = {
        "projectId": project,
        "jobId": job["jobId"],
        "stateVersion": job["stateVersion"],
        "seq": 0,
    }
    try:
        actor.queued.append(job["jobId"])
        await actor.tick()
        await asyncio.wait_for(asyncio.gather(*tuple(actor.tasks)), timeout=WORKER_TIMEOUT)
        assert actor.active == {} and not actor.queued
        return store.get_job(project, job["jobId"])
    finally:
        await actor.stop()


def run_query(store, project, selection="current", snapshot=None, definition="unclosed-high"):
    job = accept_query(store, project, selection, snapshot, definition)
    terminal = asyncio.run(run_job(store, project, job))
    assert terminal["state"] == "succeeded", terminal
    return terminal


def learning(actor, method, params):
    return ok(exchange(actor, method, params))


def read_state(actor, project):
    return learning(actor, "project.learning.read", {"projectId": project})


def task_view(state, task_id):
    return next(item for item in state["tasks"] if item["taskId"] == task_id)


def start_attempt(actor, project, task_id="query"):
    return learning(
        actor,
        "project.learning.attempt.start",
        {"projectId": project, "operationId": uid(), "taskId": task_id},
    )


def check(actor, project, task_id="query"):
    return learning(
        actor,
        "project.learning.task.check",
        {"projectId": project, "operationId": uid(), "taskId": task_id},
    )


def attempt_payload(store, project, attempt):
    from ontolearn_engine.project import format3

    row = next(
        r
        for r in format3.application_state(store, store._project(project))["learningCurrent"]
        if r["attempt"] == attempt
    )
    return json.loads(row["payload"])


def guided_checkpoints(actor, project):
    listing = ok(
        exchange(
            actor, "project.checkpoint.list", {"projectId": project, "pageSize": 50, "cursor": None}
        )
    )
    return [item for item in listing["items"] if item["reason"] == "guided-stage"]


def test_no_query_without_attempt_is_tool_not_successful(owned):
    actor, store = owned
    project = seeded(actor, store)
    result = check(actor, project)
    assert result["checkStatus"] == "tool-not-successful"
    assert result["operationComplete"] is False
    assert any("Q-01" in repair for repair in result["feedback"]["repairs"])
    assert any("Q-02" in repair for repair in result["feedback"]["repairs"])


def test_wrong_sparql_returning_a01_and_a02_needs_repair(owned):
    actor, store = owned
    project = seeded(actor, store, query_text=UNCLOSED_HIGH_MISSING_STATUS)
    start_attempt(actor, project)
    run_query(store, project)
    result = check(actor, project)
    assert result["checkStatus"] == "needs-repair"
    assert result["operationComplete"] is False
    assert any("Q-01" in repair for repair in result["feedback"]["repairs"])
    assert "Q-01" not in result["feedback"]["completed"]


def test_historical_selection_does_not_satisfy_q01(owned):
    actor, store = owned
    project = seeded(actor, store)
    start_attempt(actor, project)
    run_query(store, project, selection="historical")
    result = check(actor, project)
    assert result["checkStatus"] == "tool-not-successful"
    assert result["operationComplete"] is False
    assert result["feedback"]["completed"] == []


def test_q01_alone_completes_only_q01(owned):
    actor, store = owned
    project = seeded(actor, store)
    start_attempt(actor, project)
    run_query(store, project)
    result = check(actor, project)
    assert result["feedback"]["completed"] == ["Q-01"]
    assert any("Q-02" in repair for repair in result["feedback"]["repairs"])
    assert result["operationComplete"] is False
    # The Q-01 baseline query itself is the visible Q-02 mismatch evidence:
    # the learner has not moved A01 to Closed yet.
    assert result["checkStatus"] == "needs-repair"


def test_full_q01_q02_flow_passes_independently_without_guided_checkpoint(owned):
    actor, store = owned
    project = seeded(actor, store)
    attempt = start_attempt(actor, project)["attemptId"]
    run_query(store, project)
    set_a01_status(store, project, '"Closed"')
    run_query(store, project)
    result = check(actor, project)
    assert result["checkStatus"] == "passed"
    assert result["feedback"]["completed"] == ["Q-01", "Q-02"]
    assert result["operationComplete"] is True
    assert result["assistance"] == "independent"
    assert result["guidedStageCheckpointRef"] is None
    assert guided_checkpoints(actor, project) == []
    payload = attempt_payload(store, project, attempt)
    assert payload["operationComplete"] is True
    assert payload["assistance"] == "independent"
    assert payload["guidedStageCheckpointRef"] is None
    # Both evidence ids are real published result identities.
    for identity in result["evidenceIds"]:
        metadata, _ = store.semantic_result(project, identity)
        assert metadata["resultId"] == identity


def test_wrong_fact_then_query_reports_needs_repair(owned):
    actor, store = owned
    project = seeded(actor, store)
    start_attempt(actor, project)
    run_query(store, project)
    # The learner edits the wrong alarm (A02 instead of A01) and queries it.
    internal = store._project(project)
    old = current_fact(store, project, "urn:ontolearn:learning:alarm/A02", STATUS)
    store.commit(internal, store.revision(internal), uid(), uid(), edits={old["id"]: '"Open"'})
    run_query(store, project)
    result = check(actor, project)
    assert result["checkStatus"] == "needs-repair"
    assert result["operationComplete"] is False
    assert "Q-02" not in result["feedback"]["completed"]


def test_extra_fact_after_pass_projects_stale_and_recheck_fails(owned):
    actor, store = owned
    project = seeded(actor, store)
    start_attempt(actor, project)
    run_query(store, project)
    set_a01_status(store, project, '"Closed"')
    run_query(store, project)
    assert check(actor, project)["checkStatus"] == "passed"
    add_extra_fact(store, project)
    state = read_state(actor, project)
    view = task_view(state, "query")
    assert view["staleInput"] is True
    assert view["checkStatus"] == "stale"
    # A re-check without re-running Q-02 against the new state cannot pass.
    again = check(actor, project)
    assert again["checkStatus"] == "tool-not-successful"
    assert again["operationComplete"] is False
    assert "Q-02" not in again["feedback"]["completed"]


def test_new_attempt_isolates_old_query_evidence(owned):
    actor, store = owned
    project = seeded(actor, store)
    start_attempt(actor, project)
    run_query(store, project)
    set_a01_status(store, project, '"Closed"')
    run_query(store, project)
    assert check(actor, project)["checkStatus"] == "passed"
    restarted = start_attempt(actor, project)
    isolated = check(actor, project)
    assert isolated["checkStatus"] == "tool-not-successful"
    assert isolated["feedback"]["completed"] == []
    assert isolated["attemptId"] == restarted["attemptId"]
    # The full loop must run again inside the new attempt window.
    set_a01_status(store, project, '"Open"')
    run_query(store, project)
    set_a01_status(store, project, '"Closed"')
    run_query(store, project)
    final = check(actor, project)
    assert final["checkStatus"] == "passed"
    assert final["operationComplete"] is True
    assert final["attemptId"] == restarted["attemptId"]


def test_readings_and_assessments_never_change_completion_or_assistance(owned):
    actor, store = owned
    project = seeded(actor, store)
    start_attempt(actor, project)
    course = json.loads((ROOT / "content/learning/course.json").read_text(encoding="utf-8"))
    task = next(item for item in course["tasks"] if item["id"] == "query")
    reading = task["readings"][0]
    assert [item["answerKey"] for item in reading["selfAssessment"]] == ["b", "b"]
    opened = learning(
        actor,
        "project.learning.observation.record",
        {
            "projectId": project,
            "operationId": uid(),
            "taskId": "query",
            "observation": {"kind": "reading-opened", "readingId": reading["id"]},
        },
    )
    assert opened["assessmentOutcome"] is None
    for index, item in enumerate(reading["selfAssessment"]):
        answered = learning(
            actor,
            "project.learning.observation.record",
            {
                "projectId": project,
                "operationId": uid(),
                "taskId": "query",
                "observation": {
                    "kind": "self-assessment-answered",
                    "readingId": reading["id"],
                    "questionIndex": index,
                    "selectedOptionId": item["answerKey"],
                },
            },
        )
        assert answered["assessmentOutcome"]["correct"] is True
    view = task_view(read_state(actor, project), "query")
    assert view["operationComplete"] is False
    assert view["assistance"] == "independent"
    assert view["observations"]["openedReadingIds"] == [reading["id"]]
    assert len(view["observations"]["answeredAssessments"]) == 2


def test_hint_levels_progress_from_partial_to_full_demonstration(owned):
    actor, store = owned
    project = seeded(actor, store)
    start_attempt(actor, project)
    for level in (1, 2, 3):
        reply = learning(
            actor,
            "project.learning.hint.record",
            {"projectId": project, "operationId": uid(), "taskId": "query", "level": level},
        )
        assert reply["revealedHint"]["level"] == level
        assert reply["record"]["assistance"] == "partial-hints"
        assert reply["record"]["maxHintLevel"] == level
    full = learning(
        actor,
        "project.learning.hint.record",
        {"projectId": project, "operationId": uid(), "taskId": "query", "level": 4},
    )
    assert full["record"]["assistance"] == "full-demonstration"
    assert full["record"]["maxHintLevel"] == 4
    view = task_view(read_state(actor, project), "query")
    assert [hint["level"] for hint in view["revealedHints"]] == [1, 2, 3, 4]
    assert view["operationComplete"] is False
