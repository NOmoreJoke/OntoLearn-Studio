"""Real selected-owner draft CAS and immutable receipt projection; SOURCE only."""

import json

import pytest
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest
from test_mainline_dispatch import (
    confirmed_job,
    create,
    drain_owned_changesets,
    exchange,
    uid,
)
from test_mainline_dispatch import owned as owned


def request(project, *, generation=0, revision=0, content=None, operation=None):
    return {
        "projectId": project,
        "operationId": operation or uid(),
        "editor": "query",
        "expectedGeneration": generation,
        "boundDomainRevision": revision,
        "contentJson": canonical(content),
    }


def read(actor, project):
    response = exchange(actor, "project.read", {"projectId": project, "editor": "query"})
    assert response["ok"], response
    return response["result"]


def save(actor, params):
    response = exchange(actor, "project.draft.save", params)
    assert response["ok"], response
    assert CONTRACT.validate_business3("result_project.draft.save", response["result"])
    return response["result"]


def dump(store):
    return "\n".join(store._db.iterdump())


def advance_domain(actor, project, revision):
    triple = ["urn:draft:subject", "urn:draft:predicate", '"new domain"']
    accepted = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": revision,
            "intent": "change",
            "plan": {
                "manual": [
                    {
                        "id": digest(triple),
                        "subject": triple[0],
                        "predicate": triple[1],
                        "object": triple[2],
                    }
                ]
            },
        },
    )
    drain_owned_changesets(actor)
    return accepted


def test_actual_save_receipt_current_read_and_reopen(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    content = {"kind": "query-draft", "sparql": "ASK { }", "annotations": ["草稿", None]}
    params = request(project, content=content)
    result = save(actor, params)
    assert result == {
        "draftSaveVersion": 1,
        "projectId": project,
        "operationId": params["operationId"],
        "operationSequence": 2,
        "editor": "query",
        "generation": 1,
        "boundDomainRevision": 0,
        "contentHash": digest(content),
        "afterCheckpointRef": result["afterCheckpointRef"],
    }
    raw = store._db.execute(
        "SELECT context FROM operation_claims WHERE operation=?", (params["operationId"],)
    ).fetchone()[0]
    context = json.loads(raw)
    assert context["request"]["authorization"]["actor"] == actor.host_client_id
    assert context["request"]["authorization"]["permission"] == "write"
    assert context["plan"]["domain"] is None
    current = read(actor, project)
    assert current["domain"]["projectRevision"] == 0
    assert current["workspace"]["draft"]["generation"] == 1
    assert current["workspace"]["draft"]["contentJson"] == canonical(content)
    assert current["workspace"]["checkpointRef"] == result["afterCheckpointRef"]
    assert current["domain"]["state"] == {
        "definitions": [],
        "facts": [],
        "mappingState": {},
    }
    actor.mainline.close()
    store.close()
    reopened = JobStore(store.path, contract=CONTRACT, target_format=3)
    next_actor = Coordinator(reopened, profile="business3", _ready=_JOB_READY)
    try:
        assert exchange(next_actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
        assert exchange(next_actor, "project.open", {"projectId": project})["ok"]
        restored = read(next_actor, project)
        assert restored["workspace"]["draft"] == current["workspace"]["draft"]
        assert restored["workspace"]["checkpointRef"] == result["afterCheckpointRef"]
    finally:
        next_actor.mainline.close()
        reopened.close()


def test_original_operation_retry_returns_original_checkpoint_after_descendants(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    first_request = request(project, content={"text": "original"})
    first = save(actor, first_request)
    second = save(actor, request(project, generation=1, content={"text": "later"}))
    assert second["generation"] == 2
    advanced = advance_domain(actor, project, 0)
    assert store.get_job(project, advanced["jobId"])["state"] == "succeeded"
    before = dump(store)
    retried = save(actor, first_request)
    assert retried == first
    assert retried["generation"] == 1 and retried["boundDomainRevision"] == 0
    assert dump(store) == before
    current = read(actor, project)
    assert current["domain"]["projectRevision"] == 1
    assert current["workspace"]["draft"]["generation"] == 2
    assert current["workspace"]["draft"]["contentJson"] == canonical({"text": "later"})
    assert current["workspace"]["checkpointRef"] != first["afterCheckpointRef"]


def test_old_generation_and_old_domain_reject_without_any_persistent_effect(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    save(actor, request(project, content={"text": "first"}))
    before = dump(store)
    old_cas = exchange(actor, "project.draft.save", request(project, content={"text": "stale"}))
    assert not old_cas["ok"] and old_cas["error"]["code"] == "INVALID_STATE", old_cas
    assert dump(store) == before
    assert actor.mainline.enabled() and not actor.mainline.hold
    assert actor.mainline.replies == {}
    job = advance_domain(actor, project, 0)
    assert store.get_job(project, job["jobId"])["state"] == "succeeded"
    before = dump(store)
    old_domain = exchange(
        actor,
        "project.draft.save",
        request(
            project,
            generation=1,
            revision=0,
            content={"text": "old domain"},
        ),
    )
    assert not old_domain["ok"] and old_domain["error"]["code"] == "REVISION_CONFLICT"
    assert old_domain["error"]["params"] == {"expected": 0, "actual": 1}
    assert dump(store) == before
    saved = save(actor, request(project, generation=1, revision=1, content={"text": "fresh"}))
    assert saved["generation"] == 2 and saved["boundDomainRevision"] == 1


def test_cross_project_save_denies_before_sql_and_never_changes_selection(owned):
    actor, store = owned
    first, _ = create(actor)
    second, _ = create(actor)
    before = dump(store)
    trace = []
    store._db.set_trace_callback(trace.append)
    try:
        rejected = exchange(actor, "project.draft.save", request(first["projectId"], content=[]))
    finally:
        store._db.set_trace_callback(None)
    assert not rejected["ok"] and rejected["error"]["code"] == "PERMISSION_DENIED"
    assert trace == [] and dump(store) == before
    assert actor.mainline.selected == second["projectId"]


@pytest.mark.parametrize(
    "content_json",
    [
        "not json",
        '{"x": 1}',
        '{"x":1,"x":2}',
        "NaN",
        "Infinity",
        '"\\ud800"',
        pytest.param('"' + "x" * 65535 + '"', id="oversized-ascii-json"),
        pytest.param('"' + "中" * 21845 + '"', id="oversized-utf8-json"),
    ],
)
def test_invalid_noncanonical_or_oversized_json_never_becomes_a_draft(owned, content_json):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    params = request(project)
    params["contentJson"] = content_json
    before = dump(store)
    refused = exchange(actor, "project.draft.save", params)
    assert not refused["ok"] and refused["error"]["code"] == "INVALID_REQUEST", refused
    assert dump(store) == before


@pytest.mark.parametrize("content", [None, True, 1, "草稿", [], {"domain": {"type": "restore"}}])
def test_arbitrary_pure_json_remains_draft_data_without_domain_dispatch(owned, content):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    result = save(actor, request(project, content=content))
    assert result["contentHash"] == digest(content)
    current = read(actor, project)
    assert current["workspace"]["draft"]["contentJson"] == canonical(content)
    assert current["domain"]["projectRevision"] == 0
    assert current["domain"]["state"]["definitions"] == []
    assert current["domain"]["state"]["facts"] == []


def test_operation_cannot_rebind_content_or_cross_public_project(owned):
    actor, store = owned
    first, _ = create(actor)
    params = request(first["projectId"], content={"text": "original"})
    save(actor, params)
    before = dump(store)
    rebound = exchange(
        actor,
        "project.draft.save",
        {
            **params,
            "contentJson": canonical({"text": "changed"}),
        },
    )
    assert not rebound["ok"] and rebound["error"]["code"] == "IDENTITY_CONFLICT"
    assert dump(store) == before
    second, _ = create(actor)
    before = dump(store)
    foreign = exchange(actor, "project.draft.save", {**params, "projectId": second["projectId"]})
    assert not foreign["ok"] and foreign["error"]["code"] == "IDENTITY_CONFLICT"
    assert dump(store) == before
