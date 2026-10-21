"""Full compensation via the same real Store.commit; no schema migration."""

import json
import os
import subprocess
import sys
from copy import deepcopy

import pytest
from ontolearn_engine.project import ProjectFault, ProjectTransactions
from ontolearn_engine.storage import Conflict, Store, digest
from test_project_transactions import PHASES, apply, definition, dump, fact
from test_project_transactions import db as db


def test_restore_current_mapping_rebinds_new_generation_and_preserves_manual_drift(db):
    service = ProjectTransactions(db)
    original = fact(subject="urn:mapped")
    db.commit(
        "p", 1, "map", "j", mapping={"id": "M", "rows": [{"row": "001", "facts": [original]}]}
    )
    target = db.snapshot("p")
    expected = db.state("p")
    db.commit("p", 2, "edit", "j2", edits={original["id"]: '"人工漂移"'})
    apply(service, service.preview_restore("p", target), "restore")
    restored = db.state("p")
    assert restored["facts"] == expected["facts"]
    assert restored["definitions"] == expected["definitions"]
    assert restored["mappingState"] == {"M": {"generatedVersion": 3, "stale": []}}
    assert db.vector("p")["mapping:M"] == 3
    assert db.load_snapshot(target)["state"] == expected


def test_same_mapping_content_history_counter_rebinds_without_false_domain_change(db):
    service = ProjectTransactions(db)
    original = fact(subject="urn:mapped")
    db.commit(
        "p", 1, "map", "j", mapping={"id": "M", "rows": [{"row": "001", "facts": [original]}]}
    )
    target = db.snapshot("p")
    db.commit("p", 2, "map-away", "j2", mapping={"id": "M", "rows": []})
    db.commit(
        "p", 3, "map-back", "j3", mapping={"id": "M", "rows": [{"row": "001", "facts": [original]}]}
    )
    before = db.vector("p")
    apply(service, service.preview_restore("p", target), "restore")
    assert db.vector("p") == before
    assert db.mapping_status("p", "M") == {"generatedVersion": 3, "stale": []}


def test_empty_mapping_first_generation_undo_removes_state_without_faking_empty_rows(db):
    service = ProjectTransactions(db)
    initial = db.state("p")
    db.commit("p", 1, "empty-map", "j", mapping={"id": "M", "rows": []})
    assert db.mapping_status("p", "M") == {"generatedVersion": 0, "stale": []}
    apply(service, service.preview_undo("p", "empty-map"), "undo")
    assert db.state("p") == initial
    assert db.mapping_status("p", "M") is None


def test_undo_preserves_unrelated_mapping_generation_and_manual_source_values(db):
    service = ProjectTransactions(db)
    first, other = fact(subject="urn:m1"), fact(subject="urn:m2")
    db.commit("p", 1, "m1", "j", mapping={"id": "M1", "rows": [{"row": "001", "facts": [first]}]})
    db.commit("p", 2, "m2", "j2", mapping={"id": "M2", "rows": [{"row": "002", "facts": [other]}]})
    db.commit("p", 3, "m1-edit", "j3", edits={first["id"]: '"人工值"'})
    target_after = db.state("p")
    db.commit("p", 4, "m2-edit", "j4", edits={other["id"]: '"别处人工值"'})
    unrelated = deepcopy(db.mapping_status("p", "M2"))
    apply(service, service.preview_undo("p", "m1-edit"), "undo-m1")
    final = db.state("p")
    assert next(f for f in final["facts"] if f["id"] == first["id"]) == {
        **first,
        "owner": "M1",
        "source_row": "001",
        "managed_value": first["object"],
    }
    assert next(f for f in final["facts"] if f["id"] == other["id"])["object"] == '"别处人工值"'
    assert db.mapping_status("p", "M2") == unrelated
    assert db.mapping_status("p", "M1")["stale"] == []
    assert db.load_snapshot(db.marker("p", "m1-edit")["after_snapshot"])["state"] == target_after


def test_undo_rejects_aba_even_when_current_record_equals_target_after(db):
    service = ProjectTransactions(db)
    db.commit("p", 1, "target", "j", edits={fact()["id"]: '"目标"'})
    db.commit("p", 2, "away", "j2", edits={fact()["id"]: '"后来"'})
    db.commit("p", 3, "back", "j3", edits={fact()["id"]: '"目标"'})
    before = dump(db)
    with pytest.raises(ProjectFault, match="UNDO_CONFLICT"):
        service.preview_undo("p", "target")
    assert dump(db) == before


def test_restore_retirement_preserves_forward_version_ledger(db):
    service = ProjectTransactions(db)
    snapshot = db.snapshot("p")
    db.commit("p", 1, "r2", "j", definitions=[definition("v2")])
    db.commit("p", 2, "retire", "j2", remove_definitions=[{"layer": "rule", "id": "risk"}])
    assert "rule:risk" not in db.vector("p")
    apply(service, service.preview_restore("p", snapshot), "restore")
    assert db.vector("p")["rule:risk"] == 4
    assert db.state("p")["definitions"] == db.load_snapshot(snapshot)["state"]["definitions"]
    assert db._db.execute("SELECT * FROM definition_retirements WHERE project='p'").fetchall() == []


def test_undo_merge_detects_duplicate_statement_ownership_and_rolls_back(db):
    service = ProjectTransactions(db)
    db.commit("p", 1, "edit", "j", edits={fact()["id"]: '"B"'})
    db.commit("p", 2, "delete", "j2", remove=[fact()["id"]])
    db.commit("p", 3, "other-identity", "j3", manual=[fact('"B"')])
    before = dump(db)
    with pytest.raises(Conflict):
        service.preview_undo("p", "delete")
    assert dump(db) == before


def test_restore_rejects_self_made_hash_valid_snapshot_without_formal_provenance(db):
    service = ProjectTransactions(db)
    original = db.load_snapshot(db.snapshot("p"))
    forged = deepcopy(original)
    forged["state"]["facts"][0]["id"] = "a" * 64
    reference = db._snapshot(
        forged
    )  # Deliberately bypass trusted capture as hostile internal input.
    assert digest(db.load_snapshot(reference)) == reference
    before = dump(db)
    with pytest.raises(Conflict):
        service.preview_restore("p", reference)
    assert dump(db) == before


@pytest.mark.parametrize(
    "selector",
    [
        {},
        {"kind": "other"},
        {"kind": "undo", "operation": "missing", "state": {}},
        {"kind": "undo", "operation": None},
        {"kind": "restore", "snapshotRef": False},
        [],
    ],
)
def test_compensation_selector_strict_and_atomic(db, selector):
    before = dump(db)
    with pytest.raises(ValueError):
        db.commit("p", 1, "bad", "j", compensate=selector)
    assert dump(db) == before


@pytest.mark.parametrize(
    "ordinary",
    [
        {"manual": []},
        {"definitions": []},
        {"edits": {}},
        {"remove": []},
        {"remove_definitions": []},
        {"mapping": {"id": "M", "rows": []}},
    ],
)
def test_compensation_cannot_mix_with_regular_write_plan(db, ordinary):
    snapshot = db.snapshot("p")
    before = dump(db)
    with pytest.raises(ValueError):
        db.commit(
            "p", 1, "bad", "j", compensate={"kind": "restore", "snapshotRef": snapshot}, **ordinary
        )
    assert dump(db) == before


def test_operation_pages_have_fixed_revision_upper_bound_and_exact_evidence(db):
    for index in range(2, 6):
        db.commit("p", index - 1, f"operation-{index}", f"job-{index}")
    first = db.operation_list("p", limit=2)
    assert [m["operation"] for m in first["operations"]] == ["initial", "operation-2"]
    assert first["throughRevision"] == 5 and first["nextAfterRevision"] == 2
    db.commit("p", 5, "new-after-page", "j")
    second = db.operation_list("p", after_revision=2, through_revision=5, limit=2)
    third = db.operation_list("p", after_revision=4, through_revision=5, limit=2)
    assert [m["operation"] for m in second["operations"] + third["operations"]] == [
        "operation-3",
        "operation-4",
        "operation-5",
    ]
    assert third["nextAfterRevision"] is None
    all_markers = first["operations"] + second["operations"] + third["operations"]
    assert all_markers == [
        db.marker("p", op)
        for op in ["initial", "operation-2", "operation-3", "operation-4", "operation-5"]
    ]
    assert db.operation_list("other")["operations"] == []


@pytest.mark.parametrize(
    "args",
    [
        {"after_revision": True},
        {"after_revision": -1},
        {"through_revision": 3},
        {"after_revision": 1, "through_revision": 0},
        {"limit": 0},
        {"limit": 201},
    ],
)
def test_operation_page_bad_bounds_rejected_without_writes(db, args):
    before = dump(db)
    with pytest.raises(ValueError):
        db.operation_list("p", **args)
    assert dump(db) == before


@pytest.mark.parametrize("phase", PHASES + ["mid_restore", "mid_generation"])
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_compensation_faults_rollback_full_source_evidence_or_preserve_full_commit(
    db, phase, failure
):
    service = ProjectTransactions(db)
    target = db.snapshot("p")
    db.commit("p", 1, "edit", "j", edits={fact()["id"]: '"人工编辑"'})
    db.commit("p", 2, "remove", "j2", remove=[fact()["id"]])
    preview = service.preview_restore("p", target)
    before = dump(db)
    if failure == "exit":
        code = r"""
import os,sys
from ontolearn_engine.project import ProjectTransactions
from ontolearn_engine.storage import Store
s=Store(sys.argv[1]); t=ProjectTransactions(s)
p=t.preview_restore("p",sys.argv[3])
def hook(point):
    if point==sys.argv[2]: os._exit(73)
t.commit(p,"restore","restore-job",confirmed_preview=p.identity,hook=hook)
"""
        process = subprocess.run(
            [sys.executable, "-c", code, str(db.path), phase, target],
            capture_output=True,
            timeout=15,
            env={**os.environ},
        )
        assert process.returncode == 73, process.stderr
    else:
        error = {"exception": RuntimeError, "cancel": KeyboardInterrupt, "disk": OSError}[failure]

        def hook(point):
            if point == phase:
                raise error("injected")

        with pytest.raises(error):
            apply(service, preview, "restore", hook)
    reopened = Store(db.path)
    try:
        if phase == "after_commit":
            marker = reopened.marker("p", "restore")
            assert marker["revision"] == 4
            assert reopened.state("p") == json.loads(preview.after_json)
            assert reopened.load_snapshot(target)["state"] == json.loads(preview.after_json)
        else:
            assert dump(reopened) == before
    finally:
        reopened.close()


@pytest.mark.parametrize("tombstone", [False, True])
def test_undo_checks_retained_content_id_ownership_even_without_duplicate_live_statement(
    db, tombstone
):
    service = ProjectTransactions(db)
    if tombstone:
        # id(A) now says B. Undo restores it alongside a later managed id(B) tombstone.
        db.commit("p", 1, "edit", "j", edits={fact()["id"]: '"B"'})
        db.commit("p", 2, "delete", "j2", remove=[fact()["id"]])
        reserved = fact('"B"')
        db.commit(
            "p", 3, "map", "j3", mapping={"id": "M", "rows": [{"row": "001", "facts": [reserved]}]}
        )
        db.commit("p", 4, "tombstone", "j4", remove=[reserved["id"]])
    else:
        db.commit("p", 1, "edit", "j", edits={fact()["id"]: '"B"'})
        db.commit("p", 2, "delete", "j2", remove=[fact()["id"]])
        other = fact('"C"')
        db.commit("p", 3, "other", "j3", manual=[other])
        db.commit("p", 4, "other-edit", "j4", edits={other["id"]: fact()["object"]})
    before = dump(db)
    with pytest.raises(Conflict):
        service.preview_undo("p", "delete")
    assert dump(db) == before


@pytest.mark.parametrize("originally_retired", [False, True])
def test_restore_retirement_membership_preserves_actual_mapping_rerun_behavior(
    db, originally_retired
):
    service = ProjectTransactions(db)
    mapped = fact(subject="urn:mapped")
    mapping = {"id": "M", "rows": [{"row": "001", "facts": [mapped]}]}
    db.commit("p", 1, "map", "j", mapping=mapping)
    revision = 2
    if originally_retired:
        db.commit(
            "p",
            revision,
            "define-before-target",
            "j2",
            definitions=[{"layer": "mapping", "id": "M", "value": {}}],
        )
        revision += 1
        db.commit(
            "p",
            revision,
            "retire-before-target",
            "j3",
            remove_definitions=[{"layer": "mapping", "id": "M"}],
        )
        revision += 1
    target = db.snapshot("p")
    db.commit(
        "p",
        revision,
        "define-later",
        "j4",
        definitions=[{"layer": "mapping", "id": "M", "value": {}}],
    )
    revision += 1
    db.commit(
        "p", revision, "retire-later", "j5", remove_definitions=[{"layer": "mapping", "id": "M"}]
    )
    revision += 1
    apply(service, service.preview_restore("p", target), "restore")
    revision += 1
    retired = [
        tuple(row)
        for row in db._db.execute(
            "SELECT layer,id FROM definition_retirements WHERE project='p' ORDER BY layer,id"
        )
    ]
    assert retired == ([("mapping", "M")] if originally_retired else [])
    before = dump(db)
    if originally_retired:
        with pytest.raises(Conflict):
            db.commit("p", revision, "rerun", "j6", mapping=mapping)
        assert dump(db) == before
        assert db.mapping_status("p", "M")["stale"]
    else:
        db.commit("p", revision, "rerun", "j6", mapping=mapping)
        assert db.mapping_status("p", "M")["stale"] == []
        assert db.state("p")["facts"] == db.load_snapshot(target)["state"]["facts"]


def test_restore_then_restore_again_reconstructs_compensation_retirement_history(db):
    service = ProjectTransactions(db)
    first = db.snapshot("p")
    db.commit("p", 1, "new-rule", "j", definitions=[definition(identity="other")])
    second = db.snapshot("p")
    apply(service, service.preview_restore("p", first), "restore-first")
    apply(service, service.preview_restore("p", second), "restore-second")
    assert db.state("p") == db.load_snapshot(second)["state"]
    assert db.vector("p")["rule:other"] == 3


@pytest.mark.parametrize("via_restore", [False, True])
def test_empty_mapping_first_rerun_after_absence_uses_real_ledger_and_is_immediately_current(
    db, via_restore
):
    service = ProjectTransactions(db)
    absent = db.snapshot("p")
    db.commit("p", 1, "empty", "j", mapping={"id": "M", "rows": []})
    preview = (
        service.preview_restore("p", absent) if via_restore else service.preview_undo("p", "empty")
    )
    apply(service, preview, "remove-state")
    assert db.mapping_status("p", "M") is None
    assert "mapping:M" not in db.vector("p")
    for revision in [3, 4]:
        db.commit(
            "p", revision, f"rerun-{revision}", f"job-{revision}", mapping={"id": "M", "rows": []}
        )
        assert db.mapping_status("p", "M") == {"generatedVersion": 1, "stale": []}
        assert db.vector("p")["mapping:M"] == 1


def test_retirement_only_restore_and_undo_show_control_diff_and_bind_confirmation(db):
    service = ProjectTransactions(db)
    target = db.snapshot("p")
    db.commit("p", 1, "define", "j", definitions=[{"layer": "mapping", "id": "M", "value": {}}])
    db.commit("p", 2, "retire", "j2", remove_definitions=[{"layer": "mapping", "id": "M"}])
    before = dump(db)
    restore = service.preview_restore("p", target)
    assert dump(db) == before
    assert restore.before_json == restore.after_json
    assert restore.diff == [
        {"resource": ["definition-status", "mapping", "M"], "before": "已撤回", "after": None}
    ]
    assert restore.summary == "新增 0 项，修改 0 项，移除 1 项"
    apply(service, restore, "restore")
    assert service.reconcile(restore, "restore", "restore-job")["status"] == "committed"
    undo = service.preview_undo("p", "restore")
    assert undo.diff == [
        {"resource": ["definition-status", "mapping", "M"], "before": None, "after": "已撤回"}
    ]
    assert undo.summary == "新增 1 项，修改 0 项，移除 0 项"
    apply(service, undo, "undo-restore")
    assert service.reconcile(undo, "undo-restore", "undo-restore-job")["status"] == "committed"
    with pytest.raises(Conflict):
        db.commit("p", 5, "rerun-blocked", "j3", mapping={"id": "M", "rows": []})


def test_migrated_v1_normal_commit_lost_response_reconciles_without_old_history(tmp_path):
    from test_storage import make_legacy

    path = tmp_path / "legacy.db"
    make_legacy(path)
    store = Store(path)
    service = ProjectTransactions(store)
    try:
        old = store.state("p")["facts"][0]
        preview = service.preview("p", 1, {"edits": {old["id"]: '"新值"'}})

        def hook(point):
            if point == "after_commit":
                raise ConnectionError("lost")

        with pytest.raises(ConnectionError):
            apply(service, preview, "normal", hook)
        before = dump(store)
        marker = store.marker("p", "normal")
        assert marker["revision"] == 2
        assert json.loads(marker["plan"])["preview_control"] == {"before": [], "after": []}
        store.close()
        store = Store(path)
        service = ProjectTransactions(store)
        assert service.reconcile(preview, "normal", "normal-job") == {
            "status": "committed",
            "marker": marker,
        }
        assert apply(service, preview, "normal") == marker
        assert dump(store) == before
        # The new exact before-capture establishes revision 1, without inventing older history.
        undo = service.preview_undo("p", "normal")
        apply(service, undo, "undo-normal")
        assert store.state("p")["facts"][0] == old
    finally:
        store.close()


@pytest.mark.parametrize(
    "control",
    [
        {},
        {"before": [], "after": [], "extra": []},
        {"before": [], "after": None},
        {"before": [["unknown", "x"]], "after": []},
        {"before": [["rule", "x"], ["rule", "x"]], "after": []},
        {"before": [["rule", "z"], ["rule", "a"]], "after": []},
        {"before": [], "after": [["rule", "forged"]]},
    ],
)
def test_preview_control_evidence_is_strict_and_matches_real_transaction(db, control):
    before = dump(db)
    with pytest.raises(ValueError):
        db.commit("p", 1, "bad-control", "job", preview_identity="a" * 64, preview_control=control)
    assert dump(db) == before
