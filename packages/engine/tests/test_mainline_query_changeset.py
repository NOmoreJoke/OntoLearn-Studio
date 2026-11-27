"""Real mainline Query ChangeSets; definitions only until the parent runs them.

The shared owned fixture supplies the actual Coordinator, contract and Store.
All new managed writes use full Diff delivery, confirmation and a real Job.
"""

import base64
import json
from copy import deepcopy

import pytest
from ontolearn_engine.storage import canonical, digest
from test_job_store import create as create_legacy_job
from test_mainline_dispatch import (
    confirmed_job,
    create,
    drain_owned_changesets,
    exchange,
    uid,
)
from test_mainline_dispatch import owned as owned


def query(text="ASK { }", *, identity="Q1", name="已保存查询"):
    return {
        "layer": "query",
        "id": identity,
        "value": {
            "text": text,
            "references": [],
            "descriptor": {
                "version": 1,
                "name": name,
                "description": "通过真实 ChangeSet 保存",
                "scope": "asserted",
                "capabilityQuestion": "是否有匹配结果",
                "source": "editor",
            },
        },
    }


def change(project, base, definition):
    return {
        "projectId": project,
        "baseRevision": base,
        "intent": "change",
        "plan": {"definitions": [definition]},
    }


def load(actor, project, identity="Q1", selection=None):
    return exchange(
        actor,
        "query.definition.load",
        {
            "projectId": project,
            "definitionId": identity,
            "selection": selection or {"kind": "current"},
        },
    )


def diff_pages(actor, project, ready):
    cursor, segments = None, []
    while True:
        reply = exchange(
            actor,
            "changeset.diff.page",
            {
                "projectId": project,
                "previewHash": ready["previewHash"],
                "documentKind": "diff",
                "pageSize": 1,
                "cursor": cursor,
            },
        )
        assert reply["ok"], reply
        page = reply["result"]
        segments.extend(page["segments"])
        cursor = page["nextCursor"]
        if page["complete"]:
            break
    raw = b"".join(base64.b64decode(item["dataBase64"]) for item in segments)
    document = json.loads(raw)
    assert digest(document) == ready["manifest"]["documentHash"]
    assert len(raw) == ready["manifest"]["totalBytes"]
    return cursor, document


def dump(store):
    return "\n".join(store._db.iterdump())


def test_managed_query_full_diff_confirm_job_load_and_undo(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    original = store.state(store._project(project))
    definition = query()
    # Inspect the complete public Diff, including the actual persisted payload.
    preview = exchange(actor, "changeset.preview", change(project, 0, definition))
    assert preview["ok"] and preview["result"]["status"] == "ready", preview
    _, document = diff_pages(actor, project, preview["result"])
    touched = next(item for item in document if item["resource"] == ["definition", "query", "Q1"])
    assert touched["before"] is None
    assert json.loads(touched["after"]["payload"]) == definition["value"]
    assert store.revision(store._project(project)) == 0
    assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0

    accepted = confirmed_job(actor, project, change(project, 0, definition))
    drain_owned_changesets(actor)
    terminal = store.get_job(project, accepted["jobId"])
    assert terminal["state"] == "succeeded"
    assert store.operation_get(project, accepted["operationId"])["jobId"] == accepted["jobId"]
    loaded = load(actor, project)
    assert loaded["ok"], loaded
    record = loaded["result"]
    assert record["kind"] == "managed" and record["definitionVersion"] == 1
    assert record["draft"] == {
        key: item for key, item in definition["value"]["descriptor"].items() if key != "version"
    } | {"sparql": definition["value"]["text"]}
    assert record["definitionSha256"] == digest(definition["value"])
    assert record["descriptorSha256"] == digest(definition["value"]["descriptor"])
    historical = record["inputSnapshotId"]

    undone = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 1,
            "intent": "undo",
            "targetOperationId": accepted["operationId"],
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, undone["jobId"])["state"] == "succeeded"
    assert store.state(store._project(project)) == original
    missing = load(actor, project)
    assert not missing["ok"] and missing["error"]["code"] == "INVALID_REQUEST"
    history = load(actor, project, selection={"kind": "historical", "snapshotId": historical})
    assert history["ok"] and history["result"]["draft"] == record["draft"]
    assert history["result"]["inputSnapshotId"] == historical
    # Retry observes the original accepted Job after Undo; it cannot write again.
    assert store.get_job(project, accepted["jobId"]) == terminal
    assert store.revision(store._project(project)) == 2


@pytest.mark.parametrize("references", [None, []])
def test_managed_update_then_undo_restores_real_legacy_definition(owned, references):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    legacy = {"text": "ASK { }\n"}
    if references is not None:
        legacy["references"] = references
    # Explicit historical fixture via the existing accepted test.atomic helper:
    # its Store plan, confirmation and Job are real; the public new-query input
    # below still rejects legacy definitions. No claimed production legacy grant.
    seed = create_legacy_job(
        store,
        capability="test.atomic",
        project=project,
        plan={
            "definitions": [{"layer": "query", "id": "Q1", "value": legacy}],
        },
    )
    store.start_job(seed["jobId"])
    assert store.commit_job(seed["jobId"])["state"] == "succeeded"
    old = load(actor, project)
    assert old["ok"] and old["result"]["kind"] == "legacy", old
    assert old["result"]["text"] == legacy["text"]
    accepted = confirmed_job(actor, project, change(project, 1, query("ASK { ?s ?p ?o }")))
    drain_owned_changesets(actor)
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    assert load(actor, project)["result"]["kind"] == "managed"
    undone = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 2,
            "intent": "undo",
            "targetOperationId": accepted["operationId"],
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, undone["jobId"])["state"] == "succeeded"
    restored = load(actor, project)
    assert restored["ok"] and restored["result"]["kind"] == "legacy", restored
    assert restored["result"]["text"] == legacy["text"]
    raw = next(
        item["payload"]
        for item in store.state(store._project(project))["definitions"]
        if item["layer"] == "query" and item["id"] == "Q1"
    )
    assert raw == canonical(legacy)


def test_managed_query_references_use_existing_actual_definition_families(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    definition = query()
    definition["value"]["references"] = [{"layer": "ontology", "id": "onto"}]
    ontology = {
        "layer": "ontology",
        "id": "onto",
        "value": {"triples": [{"subject": "urn:s", "predicate": "urn:p", "object": '"v"'}]},
    }
    accepted = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 0,
            "intent": "change",
            "plan": {"definitions": [ontology, definition]},
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, accepted["jobId"])["state"] == "succeeded"
    loaded = load(actor, project)
    assert loaded["ok"] and loaded["result"]["definitionSha256"] == digest(definition["value"])
    undone = confirmed_job(
        actor,
        project,
        {
            "projectId": project,
            "baseRevision": 1,
            "intent": "undo",
            "targetOperationId": accepted["operationId"],
        },
    )
    drain_owned_changesets(actor)
    assert store.get_job(project, undone["jobId"])["state"] == "succeeded"
    assert store.state(store._project(project))["definitions"] == []


@pytest.mark.parametrize(
    "invalid",
    [
        {"version": True},
        {"version": 2},
        {"source": "automatic"},
        {"scope": "current-asserted"},
        {"name": " name "},
        {"name": ""},
        {"description": "x" * 4097},
        {"capabilityQuestion": "x" * 4097},
        {"sparql": "ASK { }"},
    ],
)
def test_invalid_managed_descriptor_cannot_create_preview_or_job(owned, invalid):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    definition = query()
    definition["value"]["descriptor"].update(invalid)
    before = dump(store)
    refused = exchange(actor, "changeset.preview", change(project, 0, definition))
    assert not refused["ok"] and refused["error"]["code"] == "INVALID_REQUEST", refused
    assert dump(store) == before


@pytest.mark.parametrize(
    "payload",
    [
        {"text": "ASK { }"},
        {"text": "ASK { }", "references": []},
        {"text": "ASK { }\n", "references": [], "descriptor": query()["value"]["descriptor"]},
        {"text": "ASK { }", "descriptor": query()["value"]["descriptor"]},
        {**query()["value"], "extra": None},
        {**query()["value"], "references": "ontology:onto"},
        {**query()["value"], "references": [{"layer": "unknown", "id": "onto"}]},
        {**query()["value"], "references": [{"layer": "ontology", "id": "onto", "extra": 1}]},
    ],
)
def test_new_query_input_is_closed_managed_and_reference_list_is_strict(owned, payload):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    before = dump(store)
    refused = exchange(
        actor,
        "changeset.preview",
        change(
            project,
            0,
            {"layer": "query", "id": "Q1", "value": deepcopy(payload)},
        ),
    )
    assert not refused["ok"] and refused["error"]["code"] == "INVALID_REQUEST", refused
    assert dump(store) == before


def test_old_base_and_confirmation_without_complete_diff_cannot_write_query(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    preview = exchange(actor, "changeset.preview", change(project, 0, query()))
    assert preview["ok"] and preview["result"]["status"] == "ready", preview
    before = dump(store)
    no_diff = exchange(
        actor,
        "changeset.confirm",
        {
            "projectId": project,
            "previewHash": preview["result"]["previewHash"],
            "completionCursor": uid(),
        },
    )
    assert not no_diff["ok"] and no_diff["error"]["code"] == "CURSOR_MISMATCH", no_diff
    assert dump(store) == before
    cursor, _ = diff_pages(actor, project, preview["result"])
    other = confirmed_job(actor, project, change(project, 0, query(identity="Q2")))
    drain_owned_changesets(actor)
    assert store.get_job(project, other["jobId"])["state"] == "succeeded"
    before = dump(store)
    stale_confirm = exchange(
        actor,
        "changeset.confirm",
        {
            "projectId": project,
            "previewHash": preview["result"]["previewHash"],
            "completionCursor": cursor,
        },
    )
    assert not stale_confirm["ok"] and stale_confirm["error"]["code"] == "REVISION_CONFLICT"
    assert dump(store) == before
    stale_preview = exchange(actor, "changeset.preview", change(project, 0, query()))
    assert not stale_preview["ok"] and stale_preview["error"]["code"] == "REVISION_CONFLICT"
    assert dump(store) == before


def test_later_query_edit_blocks_undo_without_overwriting_it(owned):
    actor, store = owned
    created, _ = create(actor)
    project = created["projectId"]
    first = confirmed_job(actor, project, change(project, 0, query()))
    drain_owned_changesets(actor)
    second = confirmed_job(actor, project, change(project, 1, query("ASK { ?s ?p ?o }")))
    drain_owned_changesets(actor)
    assert store.get_job(project, second["jobId"])["state"] == "succeeded"
    before = store.state(store._project(project))
    undo = exchange(
        actor,
        "changeset.preview",
        {
            "projectId": project,
            "baseRevision": 2,
            "intent": "undo",
            "targetOperationId": first["operationId"],
        },
    )
    assert undo["ok"] and undo["result"]["status"] == "conflict", undo
    assert undo["result"]["impactComplete"] is True
    assert store.state(store._project(project)) == before
    current = load(actor, project)
    assert current["ok"] and current["result"]["draft"]["sparql"] == "ASK { ?s ?p ?o }"
