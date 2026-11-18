"""Use approved real Store in temp DBs, without adding a production write channel.

These are opaque-definition persistence/transaction probes, not T01 product
ChangeSet, format3, runtime inference, or SHACL integration evidence.
"""

import copy
import json
from pathlib import Path

import pytest
from ontolearn_engine.quality import validate_definition
from ontolearn_engine.storage import FORMAT_VERSION, Conflict, Store

FIXTURE = json.loads(
    (Path(__file__).parents[3] / "tests/fixtures/quality/store-parameters.json").read_text()
)
PROJECT = FIXTURE["projectId"]


def payloads(state):
    return {(d["layer"], d["id"]): json.loads(d["payload"]) for d in state["definitions"]}


def arguments(name):
    request = copy.deepcopy(FIXTURE[name])
    for item in request["definitions"]:
        validated = validate_definition(item["value"]).payload()
        assert validated["kind"] == item["layer"]
        assert validated["id"] == item["id"]
    return request


def test_five_templates_and_multiconclusion_rule_roundtrip_without_execution(tmp_path):
    assert FORMAT_VERSION == FIXTURE["storeFormat"] == 2
    store = Store(tmp_path / "quality.db")
    store.create_project(PROJECT)
    request = arguments("initialSave")
    try:
        marker = store.commit(PROJECT, **request)
        expected = {(d["layer"], d["id"]): d["value"] for d in request["definitions"]}
        assert payloads(store.state(PROJECT)) == expected
        assert store.revision(PROJECT) == 1
        assert store.marker(PROJECT, request["operation"]) == marker
        assert store.load_snapshot(marker["before_snapshot"])["state"]["definitions"] == []
        assert payloads(store.load_snapshot(marker["after_snapshot"])["state"]) == expected
        assert store.state(PROJECT)["facts"] == []
        # No inferred/SHACL result or expected output is inserted by this probe.
        assert store.vector(PROJECT)["rule:R-risk-multi"] == 1
        assert store.vector(PROJECT)["constraint:name-required"] == 1
    finally:
        store.close()


def test_disable_version_preserves_old_snapshot_and_rejects_old_base(tmp_path):
    path = tmp_path / "quality.db"
    store = Store(path)
    store.create_project(PROJECT)
    try:
        original = store.commit(PROJECT, **arguments("initialSave"))
        historical = store.load_snapshot(original["after_snapshot"])
        store.commit(PROJECT, **arguments("disableSave"))
        assert store.revision(PROJECT) == 2
        now = payloads(store.state(PROJECT))
        old = payloads(historical["state"])
        for layer, identity in (("rule", "R-risk-multi"), ("constraint", "name-required")):
            assert now[layer, identity]["revision"] == 2
            assert now[layer, identity]["enabled"] is False
            assert old[layer, identity]["revision"] == 1
            assert old[layer, identity]["enabled"] is True
            assert store.vector(PROJECT)[f"{layer}:{identity}"] == 2
        stale_request = arguments("disableSave") | {"operation": "old-preview", "job": "old-job"}
        with pytest.raises(Conflict) as caught:
            store.commit(PROJECT, **stale_request)
        assert caught.value.category == "revision"
        assert payloads(store.state(PROJECT)) == now
        assert store.marker(PROJECT, "old-preview") is None
        assert store.load_snapshot(original["after_snapshot"]) == historical
    finally:
        store.close()
    reopened = Store(path)
    try:
        assert reopened.revision(PROJECT) == 2
        assert payloads(reopened.state(PROJECT)) == now
        assert reopened.load_snapshot(original["after_snapshot"]) == historical
    finally:
        reopened.close()


@pytest.mark.parametrize("phase", ["mid_data", "mid_marker", "before_commit"])
def test_interrupted_quality_definition_batch_rolls_back_all_definitions_and_marker(
    tmp_path, phase
):
    path = tmp_path / "quality.db"
    store = Store(path)
    store.create_project(PROJECT)
    before = store.state(PROJECT)
    vector = store.vector(PROJECT)

    def interrupt(stage):
        if stage == phase:
            raise OSError("synthetic write failure")

    try:
        with pytest.raises(OSError, match="synthetic write failure"):
            store.commit(PROJECT, **arguments("initialSave"), hook=interrupt)
        assert store.state(PROJECT) == before
        assert store.vector(PROJECT) == vector
        assert store.revision(PROJECT) == 0
        assert store.marker(PROJECT, "quality-create") is None
    finally:
        store.close()
    reopened = Store(path)
    try:
        assert reopened.state(PROJECT) == before
        assert reopened.revision(PROJECT) == 0
        assert reopened.marker(PROJECT, "quality-create") is None
    finally:
        reopened.close()


def test_postcommit_response_loss_keeps_real_marker_and_same_operation_does_not_repeat(tmp_path):
    store = Store(tmp_path / "quality.db")
    store.create_project(PROJECT)
    request = arguments("initialSave")

    def lose_response(phase):
        if phase == "after_commit":
            raise OSError("synthetic response loss")

    try:
        with pytest.raises(OSError, match="synthetic response loss"):
            store.commit(PROJECT, **request, hook=lose_response)
        marker = store.marker(PROJECT, request["operation"])
        assert marker is not None
        assert store.revision(PROJECT) == 1
        assert store.commit(PROJECT, **request) == marker
        assert store.revision(PROJECT) == 1
        assert payloads(store.state(PROJECT)) == {
            (d["layer"], d["id"]): d["value"] for d in request["definitions"]
        }
    finally:
        store.close()


def test_probe_uses_exact_current_approved_store_source():
    import hashlib

    root = Path(__file__).parents[3]
    assert (
        hashlib.sha256((root / FIXTURE["sourcePath"]).read_bytes()).hexdigest()
        == (FIXTURE["sourceSha256"])
    )
