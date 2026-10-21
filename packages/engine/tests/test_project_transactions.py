"""T01 real SQLite acceptance; no second store or business/UI integration claim."""

import json
import os
import subprocess
import sys
from dataclasses import replace

import pytest
from ontolearn_engine.project import ProjectFault, ProjectTransactions
from ontolearn_engine.storage import Conflict, Store, canonical, digest

IMPL = {
    "executionSemanticsVersion": "t01-test-v1",
    "engineVersion": "0.1.0",
    "dependencyLockHash": "test-lock",
}
PHASES = [
    "before",
    "mid_data",
    "mid_ownership",
    "mid_invalidation",
    "mid_marker",
    "before_commit",
    "after_commit",
]


def fact(value='"泵站A"', subject="urn:equipment/001"):
    return {
        "id": digest([subject, "urn:name", value]),
        "subject": subject,
        "predicate": "urn:name",
        "object": value,
    }


def full_fact(f):
    return {**f, "owner": None, "source_row": None, "managed_value": None}


def definition(value="旧规则", identity="risk"):
    return {"layer": "rule", "id": identity, "value": {"label": value}}


def dump(store):
    return "\n".join(store._db.iterdump())


@pytest.fixture
def db(tmp_path):
    store = Store(tmp_path / "project.db")
    store.create_project("p")
    store.create_project("other")
    store.commit("p", 0, "initial", "initial-job", manual=[fact()], definitions=[definition()])
    yield store
    store.close()


def preview_edit(service, db):
    return service.preview(
        "p",
        db.revision("p"),
        {"edits": {fact()["id"]: '"新名称"'}, "definitions": [definition("新规则")]},
    )


def apply(service, preview, op="change", hook=lambda _: None):
    return service.commit(preview, op, op + "-job", confirmed_preview=preview.identity, hook=hook)


def test_preview_full_diff_is_immutable_and_zero_persistent_writes(db):
    service = ProjectTransactions(db)
    plan = {"edits": {fact()["id"]: '"新名称"'}, "definitions": [definition("新规则")]}
    before = dump(db)
    preview = service.preview("p", 1, plan)
    assert dump(db) == before
    assert preview.base == 1
    assert preview.diff == [
        {
            "resource": ["definition", "rule", "risk"],
            "before": {"layer": "rule", "id": "risk", "payload": canonical({"label": "旧规则"})},
            "after": {"layer": "rule", "id": "risk", "payload": canonical({"label": "新规则"})},
        },
        {
            "resource": ["fact", fact()["id"]],
            "before": full_fact(fact()),
            "after": {**full_fact(fact()), "object": '"新名称"'},
        },
    ]
    assert preview.summary == "新增 0 项，修改 2 项，移除 0 项"
    identity = preview.identity
    plan["edits"].clear()
    preview.diff.clear()
    assert preview.identity == identity
    assert len(preview.diff) == 2
    marker = apply(service, preview)
    assert marker["fingerprint"] == service._fingerprint(preview)
    assert db.state("p") == json.loads(preview.after_json)
    assert db.load_snapshot(marker["before_snapshot"])["state"] == json.loads(preview.before_json)
    assert db.load_snapshot(marker["after_snapshot"])["state"] == json.loads(preview.after_json)


def test_a01_old_diff_rejected_even_when_formal_state_returns_to_same_value(db):
    service = ProjectTransactions(db)
    preview = preview_edit(service, db)
    db.commit("p", 1, "other-edit", "j", edits={fact()["id"]: '"中间值"'})
    db.commit("p", 2, "back", "j2", edits={fact()["id"]: fact()["object"]})
    before = dump(db)
    with pytest.raises(Conflict):
        apply(service, preview)
    assert dump(db) == before
    assert service.reconcile(preview, "change", "change-job") == {
        "status": "uncommitted",
        "marker": None,
    }


@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("error_type", [RuntimeError, OSError, KeyboardInterrupt])
def test_a02_atomic_failure_cancel_and_storage_error_full_database(db, phase, error_type):
    service = ProjectTransactions(db)
    snapshot = db.snapshot("p")
    result = db.publish("p", snapshot, ["facts:asserted", "rule:risk"], "query", ["旧结果"], IMPL)
    before = dump(db)
    preview = preview_edit(service, db)

    def fail(point):
        if point == phase:
            raise error_type("injected")

    with pytest.raises(error_type):
        apply(service, preview, hook=fail)
    reopened = Store(db.path)
    try:
        if phase == "after_commit":
            marker = reopened.marker("p", "change")
            assert marker["revision"] == 2
            assert reopened.state("p") == json.loads(preview.after_json)
            assert reopened.result(result)["stale"]
            assert reopened.load_snapshot(snapshot)["state"] == json.loads(preview.before_json)
        else:
            assert dump(reopened) == before
            assert reopened.marker("p", "change") is None
    finally:
        reopened.close()


@pytest.mark.parametrize("phase", PHASES)
def test_g6_real_process_exit_reopens_at_last_commit(db, phase):
    service = ProjectTransactions(db)
    preview = preview_edit(service, db)
    before = dump(db)
    code = r"""
import os,sys
from ontolearn_engine.project import ProjectTransactions
from ontolearn_engine.storage import Store
s=Store(sys.argv[1]); service=ProjectTransactions(s)
f=s.state("p")["facts"][0]
p=service.preview("p",1,{"edits":{f["id"]:'"新名称"'},"definitions":[
    {"layer":"rule","id":"risk","value":{"label":"新规则"}}]})
def hook(point):
    if point==sys.argv[2]: os._exit(73)
service.commit(p,"change","change-job",confirmed_preview=p.identity,hook=hook)
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(db.path), phase],
        env={**os.environ},
        capture_output=True,
        timeout=15,
    )
    assert result.returncode == 73, result.stderr
    reopened = Store(db.path)
    try:
        if phase == "after_commit":
            assert reopened.revision("p") == 2
            assert reopened.state("p") == json.loads(preview.after_json)
            assert reopened.marker("p", "change")["job"] == "change-job"
        else:
            assert dump(reopened) == before
    finally:
        reopened.close()


def test_lost_response_reconciles_without_new_write_and_exact_retry_is_idempotent(db, monkeypatch):
    service = ProjectTransactions(db)
    preview = preview_edit(service, db)

    def fail(point):
        if point == "after_commit":
            raise ConnectionError("delivery lost")

    with pytest.raises(ConnectionError):
        apply(service, preview, hook=fail)
    before = dump(db)
    original = db.commit
    calls = []

    def tracked(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(db, "commit", tracked)
    recovered = service.reconcile(preview, "change", "change-job")
    assert recovered["status"] == "committed"
    assert apply(service, preview) == recovered["marker"]
    assert calls == []
    assert dump(db) == before
    with pytest.raises(Conflict):
        service.reconcile(preview, "change", "wrong-job")
    with pytest.raises(Conflict):
        service.reconcile(replace(preview, base=9), "change", "change-job")
    assert dump(db) == before


def test_confirmation_binds_exact_preview_and_restore_intent(db):
    service = ProjectTransactions(db)
    preview = preview_edit(service, db)
    before = dump(db)
    with pytest.raises(ProjectFault, match="CONFIRMATION_MISMATCH"):
        service.commit(preview, "op", "job", confirmed_preview="wrong")
    assert replace(preview, intent="restore", target="x").identity != preview.identity
    assert dump(db) == before


def test_preview_and_confirm_structure_reference_errors_rollback_everything(db):
    service = ProjectTransactions(db)
    before = dump(db)
    invalid = {
        "definitions": [
            {
                "layer": "rule",
                "id": "bad",
                "value": {"references": [{"layer": "rule", "id": "missing"}]},
            }
        ],
        "manual": [fact(subject="urn:extra")],
    }
    with pytest.raises((ValueError, Conflict)):
        service.preview("p", 1, invalid)
    assert dump(db) == before
    valid = preview_edit(service, db)
    forged = replace(valid, after_json=canonical({"not": "actual state"}))
    with pytest.raises(ProjectFault, match="PREVIEW_RESULT_MISMATCH"):
        apply(service, forged)
    assert dump(db) == before


def test_undo_preserves_unrelated_edit_full_state_versions_and_original_history(db):
    service = ProjectTransactions(db)
    target = preview_edit(service, db)
    marker = apply(service, target)
    original_after = db.load_snapshot(marker["after_snapshot"])
    unrelated = fact(subject="urn:unrelated")
    db.commit("p", 2, "later", "later-job", manual=[unrelated])
    undo = service.preview_undo("p", "change")
    assert undo.intent == "undo" and undo.target == "change"
    assert {tuple(item["resource"]) for item in undo.diff} == {
        ("definition", "rule", "risk"),
        ("fact", fact()["id"]),
    }
    apply(service, undo, "undo")
    assert db.state("p") == {
        "definitions": [{"layer": "rule", "id": "risk", "payload": canonical({"label": "旧规则"})}],
        "facts": sorted([full_fact(fact()), full_fact(unrelated)], key=lambda x: x["id"]),
        "mappingState": {},
    }
    assert db.vector("p") == {"facts:asserted": 4, "rule:risk": 3}
    assert db.revision("p") == 4
    assert db.marker("p", "change") == marker
    assert db.load_snapshot(marker["after_snapshot"]) == original_after
    assert db.state("other") == {"definitions": [], "facts": [], "mappingState": {}}


def test_undo_same_record_conflict_and_later_reference_pause_without_partial_change(db):
    service = ProjectTransactions(db)
    apply(service, preview_edit(service, db))
    db.commit("p", 2, "later", "j", edits={fact()["id"]: '"后续编辑"'})
    before = dump(db)
    with pytest.raises(ProjectFault, match="UNDO_CONFLICT") as error:
        service.preview_undo("p", "change")
    assert error.value.resources == ("fact:" + fact()["id"],)
    assert dump(db) == before
    added = service.preview("p", 3, {"definitions": [definition(identity="new")]})
    apply(service, added, "add")
    db.commit(
        "p",
        4,
        "ref",
        "j2",
        definitions=[
            {
                "layer": "query",
                "id": "dependent",
                "value": {"references": [{"layer": "rule", "id": "new"}]},
            }
        ],
    )
    before = dump(db)
    with pytest.raises((Conflict, ValueError)):
        service.preview_undo("p", "add")
    assert dump(db) == before


def test_restore_has_separate_confirmed_overwrite_list_new_revision_and_immutable_history(db):
    service = ProjectTransactions(db)
    checkpoint = service.checkpoint("p", "manual")
    original = db.load_snapshot(checkpoint["snapshotRef"])
    apply(service, preview_edit(service, db))
    extra = fact(subject="urn:extra")
    db.commit("p", 2, "later", "j", manual=[extra], definitions=[definition(identity="new")])
    preview = service.preview_restore("p", checkpoint["snapshotRef"])
    assert preview.intent == "restore"
    assert preview.target == checkpoint["snapshotRef"]
    assert preview.overwritten_operations == ("change", "later")
    assert preview.identity != replace(preview, overwritten_operations=()).identity
    apply(service, preview, "restore")
    assert db.state("p") == original["state"]
    assert db.revision("p") == 4
    assert db.load_snapshot(checkpoint["snapshotRef"]) == original
    assert [r[0] for r in db._db.execute("SELECT operation FROM commits ORDER BY revision")] == [
        "initial",
        "change",
        "later",
        "restore",
    ]
    assert "rule:new" not in db.vector("p")


def test_restore_cross_project_wrong_snapshot_and_stale_confirmation_are_rejected(db):
    service = ProjectTransactions(db)
    other = db.snapshot("other")
    with pytest.raises(Conflict):
        service.preview_restore("p", other)
    checkpoint = service.checkpoint("p", "before-agent")
    apply(service, preview_edit(service, db))
    restore = service.preview_restore("p", checkpoint["snapshotRef"])
    db.commit("p", 2, "later", "j")
    before = dump(db)
    with pytest.raises(Conflict):
        apply(service, restore, "restore")
    assert dump(db) == before


def test_undo_added_or_removed_manual_facts_and_definitions(db):
    service = ProjectTransactions(db)
    before = db.state("p")
    plan = {"remove": [fact()["id"]], "remove_definitions": [{"layer": "rule", "id": "risk"}]}
    apply(service, service.preview("p", 1, plan), "remove")
    undo = service.preview_undo("p", "remove")
    apply(service, undo, "undo-remove")
    assert db.state("p") == before
    extra = fact(subject="urn:extra")
    plan = {"manual": [extra], "definitions": [definition(identity="extra")]}
    apply(service, service.preview("p", 3, plan), "add")
    apply(service, service.preview_undo("p", "add"), "undo-add")
    assert db.state("p") == before


def test_deleted_edited_legacy_id_restore_requires_store_handoff(db):
    service = ProjectTransactions(db)
    db.commit("p", 1, "edit", "j", edits={fact()["id"]: '"人工编辑"'})
    snapshot = db.snapshot("p")
    db.commit("p", 2, "delete", "j2", remove=[fact()["id"]])
    before = dump(db)
    for preview in [
        lambda: service.preview_restore("p", snapshot),
        lambda: service.preview_undo("p", "delete"),
    ]:
        with pytest.raises(ProjectFault, match="RESTORE_REQUIRES_STORE_SUPPORT"):
            preview()
        assert dump(db) == before


def test_first_mapping_undo_does_not_silently_leave_mapping_state(db):
    service = ProjectTransactions(db)
    mapped = fact(subject="urn:mapped")
    plan = {"mapping": {"id": "M1", "rows": [{"row": "001", "facts": [mapped]}]}}
    preview = service.preview("p", 1, plan)
    apply(service, preview, "mapping")
    before = dump(db)
    with pytest.raises(ProjectFault, match="RESTORE_REQUIRES_STORE_SUPPORT") as error:
        service.preview_undo("p", "mapping")
    assert "mappingState:M1" in error.value.resources
    assert dump(db) == before
    assert db.state("p")["facts"] == sorted(
        [
            full_fact(fact()),
            {**mapped, "owner": "M1", "source_row": "001", "managed_value": mapped["object"]},
        ],
        key=lambda f: f["id"],
    )


def test_cache_reclaims_payload_without_deleting_history_drafts_or_asserted_facts(db):
    snapshot = db.snapshot("p")
    first = db.publish("p", snapshot, ["facts:asserted"], "query", ["old"], IMPL)
    pinned = db.publish("p", snapshot, ["facts:asserted"], "report", ["pinned"], IMPL)
    db.pin_result(pinned, "report-1")
    current = db.publish("p", snapshot, ["facts:asserted"], "query", ["new"], IMPL)
    run = db.start_run("p", snapshot, {"maxRounds": 1}, IMPL)
    db.commit_round(run, 1, {"state": "complete"}, "round-op", "round-job")
    db.finish_run(run, "succeeded", {"done": True})
    history = db.history(run)
    state, vector = db.state("p"), db.vector("p")
    markers = [dict(r) for r in db._db.execute("SELECT * FROM commits")]
    snapshots = [dict(r) for r in db._db.execute("SELECT * FROM snapshots ORDER BY id")]
    assert db.collect_cache() == [first]
    assert db.result(first)["payload"] is None
    assert db.result(pinned)["payload"] == ["pinned"]
    assert db.result(current)["payload"] == ["new"]
    assert db.history(run) == history
    assert db.state("p") == state
    assert db.vector("p") == vector
    assert [dict(r) for r in db._db.execute("SELECT * FROM commits")] == markers
    assert [dict(r) for r in db._db.execute("SELECT * FROM snapshots ORDER BY id")] == snapshots


def test_domain_dependency_invalidation_and_old_result_never_replaces_new_current(db):
    service = ProjectTransactions(db)
    old_snapshot = db.snapshot("p")
    old_result = db.publish(
        "p", old_snapshot, ["facts:asserted", "rule:risk"], "query", ["old"], IMPL
    )
    apply(service, preview_edit(service, db))
    expected_stale = [
        {"code": "FACTS_CHANGED", "dependency": "facts:asserted", "before": 1, "after": 2},
        {"code": "RULE_CHANGED", "dependency": "rule:risk", "before": 1, "after": 2},
    ]
    assert db.result(old_result)["stale"] == expected_stale
    new_snapshot = db.snapshot("p")
    current = db.publish("p", new_snapshot, ["facts:asserted", "rule:risk"], "query", ["new"], IMPL)
    late = db.publish("p", old_snapshot, ["facts:asserted", "rule:risk"], "query", ["late"], IMPL)
    assert db.current("p", "query", IMPL)["id"] == current
    assert db.result(late)["stale"] == expected_stale
    assert db.result(late)["state"] == "stale"
    before = db.state("p")
    db.commit("p", 2, "model", "j", definitions=[{"layer": "model", "id": "local", "value": {}}])
    assert db.result(current)["stale"] == []
    assert db.state("p")["facts"] == before["facts"]


@pytest.mark.parametrize("reason", ["before-agent", "before-run", "guided-stage", "manual"])
def test_checkpoint_node_preserves_complete_current_state(reason, db):
    service = ProjectTransactions(db)
    state, vector = db.state("p"), db.vector("p")
    checkpoint = service.checkpoint("p", reason)
    assert checkpoint["reason"] == reason
    assert db.load_snapshot(checkpoint["snapshotRef"]) == {
        "project": "p",
        "projectRevision": 1,
        "dependencyVector": vector,
        "state": state,
    }
    assert db.revision("p") == 1


def test_managed_tombstone_restore_explicitly_refuses_loss_of_owner_and_manual_conflict(db):
    service = ProjectTransactions(db)
    mapped = fact(subject="urn:mapped")
    db.commit("p", 1, "map", "j", mapping={"id": "M1", "rows": [{"row": "001", "facts": [mapped]}]})
    db.commit("p", 2, "manual-delete", "j2", remove=[mapped["id"]])
    target = db.snapshot("p")
    db.commit("p", 3, "manual-restore", "j3", edits={mapped["id"]: mapped["object"]})
    before = dump(db)
    with pytest.raises(ProjectFault, match="RESTORE_REQUIRES_STORE_SUPPORT"):
        service.preview_restore("p", target)
    assert dump(db) == before


@pytest.mark.parametrize(
    "mutation",
    [
        {"after_json": '{"wrong":"state"}'},
        {"before_json": '{"wrong":"state"}'},
        {"intent": "restore"},
        {"target": "wrong"},
        {"overwritten_operations": ("wrong",)},
    ],
)
def test_completed_operation_rejects_changed_preview_evidence_and_intent(db, mutation):
    service = ProjectTransactions(db)
    preview = preview_edit(service, db)
    apply(service, preview)
    before = dump(db)
    with pytest.raises(Conflict):
        apply(service, replace(preview, **mutation))
    assert dump(db) == before


def test_legacy_store_plan_hash_unchanged_when_preview_identity_omitted(db):
    marker = db.marker("p", "initial")
    plan = {
        "base": 0,
        "definitions": [definition()],
        "manual": [fact()],
        "edits": None,
        "remove": None,
        "mapping": None,
    }
    assert marker["fingerprint"] == digest(plan)
    assert "preview_identity" not in json.loads(marker["plan"])
    before = dump(db)
    assert (
        db.commit("p", 0, "initial", "initial-job", manual=[fact()], definitions=[definition()])
        == marker
    )
    assert dump(db) == before
