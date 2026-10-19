"""S1 executable acceptance: prepared storage plans, not complete business engines."""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from ontolearn_engine.invalidation import RULES, reasons
from ontolearn_engine.storage import SCHEMA, Conflict, Store, digest
from ontolearn_engine.storage_probe import measure

IMPL = {
    "executionSemanticsVersion": "s1-test-v1",
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


def fact(subject="urn:equipment/001", value='"泵站A"', predicate="urn:name"):
    return {
        "id": digest([subject, predicate, value]),
        "subject": subject,
        "predicate": predicate,
        "object": value,
    }


def mapped(value='"泵站A"', owner="M1"):
    return {"id": owner, "rows": [{"row": "001", "facts": [fact(value=value)]}]}


def apply(store, mode, hook=lambda _: None):
    kwargs = (
        {"mapping": mapped('"new"')}
        if mode == "mapping"
        else {
            "definitions": [{"layer": "rule", "id": "risk", "value": {"enabled": False}}],
            "manual": [fact("urn:manual/001")],
        }
    )
    return store.commit("p", 1, "next", "next-job", hook=hook, **kwargs)


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "project.db"
    store = Store(path)
    store.create_project("p")
    store.commit(
        "p",
        0,
        "initial",
        "initial-job",
        mapping=mapped(),
        definitions=[{"layer": "rule", "id": "risk", "value": {"enabled": True}}],
    )
    yield store
    store.close()


@pytest.mark.parametrize("mode", ["mapping", "changeset"])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("failure", ["cancel", "exception", "disk", "exit"])
def test_atomic_fault_matrix(db, mode, phase, failure):
    snapshot = db.snapshot("p")
    result = db.publish(
        "p", snapshot, ["facts:asserted", "mapping:M1", "rule:risk"], "query", ["old"], IMPL
    )
    before = db.state("p")
    vector = db.vector("p")
    path = db.path
    if failure == "exit":
        # A genuinely separate process exits with an open SQLite transaction.
        code = """
import os,sys
from ontolearn_engine.storage import Store
from test_storage import apply
s=Store(sys.argv[1])
def hook(p):
    if p==sys.argv[3]: os._exit(73)
apply(s,sys.argv[2],hook)
"""
        env = {**os.environ, "PYTHONPATH": str(Path(__file__).parent)}
        process = subprocess.run(
            [sys.executable, "-c", code, str(path), mode, phase],
            env=env,
            capture_output=True,
            timeout=15,
        )
        assert process.returncode == 73, process.stderr
    else:
        error = {"cancel": KeyboardInterrupt, "exception": RuntimeError, "disk": OSError}[failure]

        def hook(point):
            if point == phase:
                raise error("injected")

        with pytest.raises(error):
            apply(db, mode, hook)
    reopened = Store(path)
    if phase == "after_commit":
        assert reopened.revision("p") == 2
        assert reopened.marker("p", "next")["job"] == "next-job"
        assert reopened.result(result)["stale"]
        assert reopened.state("p") != before
        assert reopened.vector("p") != vector
    else:
        assert reopened.revision("p") == 1
        assert reopened.marker("p", "next") is None
        assert reopened.result(result)["stale"] == []
        assert reopened.state("p") == before
        assert reopened.vector("p") == vector
    reopened.close()


def test_real_sqlite_full_rolls_back(db):
    before = db.state("p")
    pages = db._db.execute("PRAGMA page_count").fetchone()[0]
    db._db.execute(f"PRAGMA max_page_count={pages}")
    with pytest.raises(sqlite3.OperationalError, match="full"):
        db.commit(
            "p",
            1,
            "full",
            "full-job",
            manual=[fact("urn:manual")],
            definitions=[{"layer": "rule", "id": "huge", "value": "x" * 1_000_000}],
        )
    assert db.state("p") == before
    assert db.revision("p") == 1
    assert db.marker("p", "full") is None


def test_ownership_idempotence_manual_delete_multi_source_and_old_base(db):
    initial = db.state("p")
    db.commit("p", 1, "same", "same-job", mapping=mapped())
    assert db.state("p") == initial
    assert db.vector("p")["facts:asserted"] == 1  # exact no-op does not stale results
    db.commit("p", 2, "manual", "manual-job", manual=[fact("urn:manual", '"keep"')])
    db.commit("p", 3, "remove-row", "remove-job", mapping={"id": "M1", "rows": []})
    assert [r["subject"] for r in db.state("p")["facts"]] == ["urn:manual"]
    db.commit("p", 4, "restore", "restore-job", mapping=mapped())
    for owner in ("M2", "M3"):
        with pytest.raises(Conflict, match="Ownership"):
            db.commit("p", 5, owner, owner, mapping=mapped(owner=owner))
    db.commit("p", 5, "edit-managed", "edit-job", edits={initial["facts"][0]["id"]: '"human"'})
    with pytest.raises(Conflict, match="Manual drift"):
        db.commit("p", 6, "conflict", "job", mapping=mapped('"source"'))
    with pytest.raises(Conflict, match="Old projectRevision"):
        db.commit("p", 5, "old", "job", mapping=mapped())
    # Deleting a managed statement must retain a tombstone/baseline for rerun conflicts.
    managed_id = initial["facts"][0]["id"]
    db.commit("p", 6, "delete-managed", "delete-job", remove=[managed_id])
    with pytest.raises(Conflict, match="Manual drift"):
        db.commit("p", 7, "deleted-conflict", "job", mapping=mapped())
    assert db.state("p")["facts"][0]["subject"] in {"urn:manual", "urn:equipment/001"}


def test_invalid_plan_rolls_back_and_operation_reconciliation(db):
    before = db.state("p")
    bad = mapped()
    bad["rows"].append(bad["rows"][0])
    with pytest.raises(ValueError, match="duplicate"):
        db.commit("p", 1, "bad", "bad-job", mapping=bad)
    assert db.state("p") == before
    args = ("p", 1, "once", "once-job")
    first = db.commit(*args, manual=[fact("urn:new")])
    assert db.commit(*args, manual=[fact("urn:new")]) == first
    assert db.revision("p") == 2
    with pytest.raises(Conflict, match="reused"):
        db.commit(*args, manual=[fact("urn:other")])
    second_connection = Store(db.path)
    with pytest.raises(Conflict, match="Old"):
        second_connection.commit("p", 1, "racer", "racer-job", manual=[fact("urn:racer")])
    second_connection.close()


@pytest.mark.parametrize("rule", RULES["rules"], ids=lambda r: f"D{r['appendixRow']}")
def test_nine_appendix_d_rows_positive_and_negative(db, rule):
    category = rule["family"]
    key = "facts:asserted" if category == "facts" else f"{category}:one"
    unrelated_key = "query:unrelated" if category == "facts" else f"{category}:other"
    seeds = (
        [{"layer": "query", "id": "unrelated", "value": {}}]
        if category == "facts"
        else [
            {"layer": category, "id": identity, "value": {"initial": True}}
            for identity in ("one", "other")
        ]
    )
    db.commit("p", 1, "declare-dependencies", "job", definitions=seeds)
    snap = db.snapshot("p")
    relevant = db.publish("p", snap, [key], "relevant", [1], IMPL)
    unrelated = db.publish("p", snap, [unrelated_key], "unrelated", [2], IMPL)
    if category == "facts":
        db.commit("p", 2, "change", "job", manual=[fact("urn:other")])
    else:
        db.commit(
            "p",
            2,
            "change",
            "job",
            definitions=[{"layer": category, "id": "one", "value": {"changed": True}}],
        )
    stale = db.result(relevant)["stale"]
    if rule["staleReason"]:
        assert stale == [{"code": rule["staleReason"], "dependency": key, "before": 1, "after": 2}]
    else:
        assert stale == []
    assert db.result(unrelated)["stale"] == []
    assert reasons({key: 1}, {key: 1}) == []


def test_multiple_reasons_late_result_cache_isolation_and_history(db):
    snap = db.snapshot("p")
    old = db.publish("p", snap, ["facts:asserted", "rule:risk"], "inference", ["risk"], IMPL)
    db.pin_result(old, "saved-report")
    db.commit(
        "p",
        1,
        "new-rule",
        "job",
        definitions=[
            {"layer": "rule", "id": "risk", "value": {"enabled": False}},
        ],
        manual=[fact("urn:new")],
    )
    assert {r["code"] for r in db.result(old)["stale"]} == {"FACTS_CHANGED", "RULE_CHANGED"}
    late = db.publish("p", snap, ["facts:asserted", "rule:risk"], "inference", ["late"], IMPL)
    assert db.current("p", "inference", IMPL) is None
    current = db.publish(
        "p", db.snapshot("p"), ["facts:asserted", "rule:risk"], "inference", [], IMPL
    )
    assert db.current("p", "inference", IMPL)["id"] == current
    assert db.current("p", "inference", {**IMPL, "engineVersion": "upgrade"}) is None
    assert db.collect_cache() == [late]
    assert db.result(old)["payload"] == ["risk"]
    assert db.result(late)["payload"] is None
    assert db.result(late)["dependencies"]  # metadata and rerun snapshot still available
    assert db.load_snapshot(snap)["projectRevision"] == 1
    assert len(db.state("p")["facts"]) == 2  # inference replacement never deletes assertions
    for table in ("snapshots", "commits"):
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            db._db.execute(f"DELETE FROM {table}")


def test_scenario_round_cancel_isolation_replay_and_late_publication(db):
    snap = db.snapshot("p")
    original = db.state("p")
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {"capacity": 3},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    run = db.start_run("p", snap, config, IMPL)
    assert db.progress(run) is None
    first = db.commit_round(run, 1, {"orders": ["W001"]}, "round1", "run-job")

    def cancel(phase):
        if phase == "mid_marker":
            raise KeyboardInterrupt()

    with pytest.raises(KeyboardInterrupt):
        db.commit_round(run, 2, {"orders": ["W002"]}, "round2", "run-job", hook=cancel)
    db.finish_run(run, "cancelled", {"reason": "user"})
    history = db.history(run)
    assert history["committedProgress"] == {
        "runId": run,
        "lastCommittedRound": 1,
        "snapshotRef": first,
    }
    assert history["terminal"]["status"] == "cancelled"
    assert history["replayable"] is True
    assert [r["number"] for r in history["rounds"]] == [1]
    assert db.load_snapshot(first)["state"] == {"orders": ["W001"]}
    assert db.state("p") == original
    with pytest.raises(Conflict, match="Terminal"):
        db.commit_round(run, 2, {}, "late-round", "run-job")
    fresh = db.start_run("p", snap, config, IMPL)
    assert db.progress(fresh) is None
    assert db.history(run) == history  # new run cannot mutate prior run
    missing = db.start_run("p", snap, {}, {})
    assert db.history(missing)["replayable"] is False
    db.create_project("other")
    with pytest.raises(Conflict, match="Cross-project"):
        db.start_run("other", snap, config, IMPL)
    db.collect_cache()
    assert db.history(run) == history


@pytest.mark.parametrize(
    "phase", ["before", "mid_data", "mid_marker", "before_commit", "after_commit"]
)
def test_round_process_exit(db, phase):
    snap = db.snapshot("p")
    run = db.start_run("p", snap, {"maxRounds": 4}, IMPL)
    db.commit_round(run, 1, {"n": 1}, "r1", "job")
    code = """
import os,sys
from ontolearn_engine.storage import Store
s=Store(sys.argv[1])
def hook(p):
    if p==sys.argv[3]: os._exit(73)
s.commit_round(sys.argv[2],2,{'n':2},'r2','job',hook)
"""
    process = subprocess.run([sys.executable, "-c", code, str(db.path), run, phase], timeout=15)
    assert process.returncode == 73
    assert db.progress(run)["lastCommittedRound"] == (2 if phase == "after_commit" else 1)


def test_migration_failure_backup_restore_and_future_format(db, tmp_path):
    backup = tmp_path / "backup.db"
    db.backup(backup)
    original = db.state("p")
    copy = sqlite3.connect(backup, isolation_level=None)
    copy.execute("DROP TABLE migration_log")
    copy.execute("DROP TABLE commit_evidence")
    copy.execute("DROP TABLE mapping_state")
    copy.execute("PRAGMA user_version=1")
    copy.close()

    def fail(point):
        if point == "migration_mid":
            raise RuntimeError("migration injected failure")

    with pytest.raises(RuntimeError):
        Store(backup, migration_hook=fail)
    copy = sqlite3.connect(backup)
    assert copy.execute("PRAGMA user_version").fetchone()[0] == 1
    assert (
        copy.execute("SELECT name FROM sqlite_master WHERE name='migration_log'").fetchone() is None
    )
    copy.close()
    restored = Store(backup)
    assert restored.state("p")["facts"] == original["facts"]
    assert restored.state("p")["definitions"] == original["definitions"]
    assert restored.mapping_status("p", "M1")["generatedVersion"] == -1
    assert restored.mapping_status("p", "M1")["stale"]
    assert restored.marker("p", "initial")["job"] == "initial-job"
    restored.close()
    copy = sqlite3.connect(backup)
    copy.execute("PRAGMA user_version=999")
    copy.close()
    with pytest.raises(ValueError, match="future"):
        Store(backup)


def test_schema_cannot_overwrite_history_and_missing_snapshot_is_honest(tmp_path):
    path = tmp_path / "old.db"
    connection = sqlite3.connect(path)
    for statement in SCHEMA:
        connection.execute(statement)
    connection.execute("PRAGMA user_version=1")
    connection.commit()
    connection.close()
    store = Store(path)
    store.create_project("p")
    snap = store.snapshot("p")
    run = store.start_run("p", snap, {}, {})
    assert not store.history(run)["replayable"]
    with pytest.raises(KeyError, match="Missing replay"):
        store.load_snapshot("absent")
    store.finish_run(run, "failed", {"reason": "input_missing"})
    with pytest.raises(sqlite3.IntegrityError):
        store.finish_run(run, "succeeded", {})
    store.close()


def test_fixed_rdflib_query_and_two_independent_scales():
    small = measure(1)
    large = measure(10)
    assert small["result"] == ["urn:case:0:alarm/A01"]
    assert large["result"] == [f"urn:case:{i}:alarm/A01" for i in range(10)]
    assert small["triples"] * 10 == large["triples"]
    assert small["inputSha256"] != large["inputSha256"]
    assert small["querySha256"] == large["querySha256"]
    assert all(v["pythonBytesPeak"] > 0 for v in large["measurement"].values())


def test_full_g_baseline_storage_roundtrip_and_e5_prepared_state_retention(tmp_path):
    from storage_baselines import E5, g_definitions, g_facts

    store = Store(tmp_path / "baseline.db")
    for baseline in ("G-base", "G-map-empty", "G-behavior"):
        store.create_project(baseline)
        behavior = baseline == "G-behavior"
        definitions = g_definitions(behavior)
        facts = [] if baseline == "G-map-empty" else g_facts(behavior)
        store.commit(baseline, 0, "restore", "restore-job", definitions=definitions, manual=facts)
        state = store.load_snapshot(store.snapshot(baseline))["state"]
        expected_definitions = sorted(
            [
                {
                    "layer": d["layer"],
                    "id": d["id"],
                    "payload": json.dumps(
                        d["value"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
                    ),
                }
                for d in definitions
            ],
            key=lambda d: (d["layer"], d["id"]),
        )
        assert state["definitions"] == expected_definitions
        assert [
            {k: f[k] for k in ("id", "subject", "predicate", "object")} for f in state["facts"]
        ] == sorted(facts, key=lambda f: f["id"])
    for capacity in (3, 4):
        sequences = []
        for replay in range(2):
            run = store.start_run(
                "G-base",
                store.snapshot("G-base"),
                {
                    "maxRounds": 4,
                    "parameters": {"capacity": capacity},
                    "events": [{"scope": "prepared expected fixture; not executed"}],
                    "ruleVersions": {},
                    "behaviorVersions": {},
                },
                IMPL,
            )
            for number, state in enumerate(E5[capacity], 1):
                store.commit_round(run, number, state, f"{capacity}-{replay}-{number}", run)
            store.finish_run(run, "succeeded", {"scope": "prepared storage fixture only"})
            sequence = [
                store.load_snapshot(r["snapshot"])["state"] for r in store.history(run)["rounds"]
            ]
            assert sequence == E5[capacity]
            sequences.append(sequence)
        assert sequences[0] == sequences[1]
    store.close()


@pytest.mark.parametrize("mode", ["mapping", "changeset", "round"])
def test_actual_database_full_modes(db, mode):
    before = db.state("p")
    run = db.start_run("p", db.snapshot("p"), {"maxRounds": 4}, IMPL)
    pages = db._db.execute("PRAGMA page_count").fetchone()[0]
    db._db.execute(f"PRAGMA max_page_count={pages}")
    with pytest.raises(sqlite3.OperationalError, match="full"):
        if mode == "mapping":
            db.commit("p", 1, "full-map", "job", mapping=mapped('"' + "x" * 1000000 + '"'))
        elif mode == "changeset":
            db.commit("p", 1, "full-change", "job", manual=[fact(value='"' + "x" * 1000000 + '"')])
        else:
            db.commit_round(run, 1, {"state": "x" * 1000000}, "full-round", "job")
    assert db.state("p") == before
    assert db.revision("p") == 1
    assert db.progress(run) is None


def test_explicit_manual_edits_multivalue_noop_and_single_slot(db):
    base = db.state("p")["facts"][0]
    db.commit("p", 1, "multivalue", "job", mapping=mapped('"second-value"', "M2"))
    assert len(db.state("p")["facts"]) == 2
    db.commit("p", 2, "target-edit", "job", edits={base["id"]: '"human"'})
    values = {r["owner"]: r["object"] for r in db.state("p")["facts"]}
    assert values == {"M1": '"human"', "M2": '"second-value"'}
    db.commit("p", 3, "manual", "job", manual=[fact("urn:manual")])
    before = db.vector("p")
    db.commit("p", 4, "manual-again", "job", manual=[fact("urn:manual")])
    assert db.vector("p") == before
    definition = {
        "layer": "ontology",
        "id": "single",
        "value": {"singleValuedPredicates": ["urn:name"]},
    }
    with pytest.raises(Conflict, match="Single-valued declaration"):
        db.commit("p", 5, "invalid-single", "job", definitions=[definition])
    db.commit("p", 5, "drop-M2", "job", mapping={"id": "M2", "rows": []})
    db.commit("p", 6, "single", "job", definitions=[definition])
    with pytest.raises(Conflict, match="Ownership"):
        db.commit("p", 7, "single-conflict", "job", manual=[fact("urn:manual", '"other"')])


def test_reference_check_and_incomplete_replay_are_explicit(db):
    with pytest.raises(Conflict, match="Unresolved"):
        db.commit(
            "p",
            1,
            "bad-ref",
            "job",
            definitions=[
                {
                    "layer": "rule",
                    "id": "r",
                    "value": {"references": [{"layer": "ontology", "id": "missing"}]},
                }
            ],
        )
    assert db.revision("p") == 1
    run = db.start_run(
        "p",
        db.snapshot("p"),
        {
            "parameters": None,
            "events": None,
            "ruleVersions": None,
            "behaviorVersions": None,
            "maxRounds": None,
        },
        IMPL,
    )
    assert db.history(run)["replayable"] is False
    with pytest.raises(ValueError, match="required"):
        db.commit_round(run, 1, {}, "", "")


def test_old_implementation_cannot_displace_new_current(db):
    snap = db.snapshot("p")
    upgraded = {**IMPL, "engineVersion": "2", "dependencyLockHash": "new-lock"}
    new = db.publish("p", snap, ["facts:asserted"], "query", ["new-engine"], upgraded)
    old = db.publish("p", snap, ["facts:asserted"], "query", ["old-late"], IMPL)
    assert db.current("p", "query", upgraded)["id"] == new
    assert db.current("p", "query", IMPL)["id"] == old
    assert db.result(new)["cache_key"] != db.result(old)["cache_key"]


def test_normalized_snapshot_rebuild_ignores_tombstones_preserves_old_input(db):
    from ontolearn_engine.rdf_snapshot import graph_from_snapshot
    from rdflib import Literal, URIRef

    before = db.snapshot("p")
    identity = db.state("p")["facts"][0]["id"]
    db.commit("p", 1, "edit", "job", edits={identity: '"new"'})
    edited = db.snapshot("p")
    assert (URIRef("urn:equipment/001"), URIRef("urn:name"), Literal("new")) in (
        graph_from_snapshot(db.load_snapshot(edited))
    )
    db.commit("p", 2, "delete", "job", remove=[identity])
    assert len(graph_from_snapshot(db.load_snapshot(db.snapshot("p")))) == 0
    assert list(graph_from_snapshot(db.load_snapshot(before)).objects()) == [Literal("泵站A")]


def test_mapping_source_change_marks_generated_data_stale_and_records_undo_basis(db):
    previous = db.snapshot("p")
    assert db.mapping_status("p", "M1")["stale"] == []
    db.commit(
        "p",
        1,
        "source-change",
        "job",
        definitions=[
            {
                "layer": "mapping",
                "id": "M1",
                "value": {"sourceHash": "new-source", "identity": "id"},
            }
        ],
    )
    assert db.mapping_status("p", "M1")["stale"] == [
        {
            "code": "MAPPING_INPUT_CHANGED",
            "dependency": "mapping:M1",
            "before": 1,
            "after": 2,
        }
    ]
    marker = db.marker("p", "source-change")
    assert marker["before_snapshot"] == previous
    assert db.load_snapshot(marker["after_snapshot"])["projectRevision"] == 2
    db.commit("p", 2, "regenerate", "job", mapping=mapped())
    assert db.mapping_status("p", "M1")["stale"] == []


@pytest.mark.parametrize(
    "object_value", ["<relative>", "<urn:cut", '"x" . <urn:x> <urn:p> "y"', "_:blank"]
)
def test_malformed_or_unstable_fact_is_atomically_rejected(db, object_value):
    before = db.state("p")
    with pytest.raises(ValueError):
        db.commit("p", 1, "bad-rdf", "job", manual=[fact("urn:test", object_value)])
    assert db.state("p") == before
    assert db.marker("p", "bad-rdf") is None


@pytest.mark.parametrize(
    "value", ['"""泵站A"""', '"泵站A"^^<http://www.w3.org/2001/XMLSchema#string>', '"\\u6cf5站A"']
)
def test_rdf_lexical_alias_cannot_bypass_ownership(db, value):
    before = db.state("p")
    with pytest.raises(ValueError, match="Canonical"):
        db.commit("p", 1, "alias-map", "job", mapping=mapped(value, "M2"))
    with pytest.raises(ValueError, match="Canonical"):
        db.commit("p", 1, "alias-manual", "job", manual=[fact(value=value)])
    assert db.state("p") == before


def test_late_snapshot_without_domain_change_stays_history_and_cannot_displace_current(db):
    first_input = db.snapshot("p")
    first = db.publish("p", first_input, ["facts:asserted"], "query", ["old"], IMPL)
    db.commit(
        "p",
        1,
        "model-only",
        "job",
        definitions=[{"layer": "model", "id": "gateway", "value": {"displayName": "new"}}],
    )
    assert db.result(first)["stale"] == []
    assert db.current("p", "query", IMPL)["id"] == first  # no meaningless invalidation
    latest_input = db.snapshot("p")
    latest = db.publish("p", latest_input, ["facts:asserted"], "query", ["new"], IMPL)
    late = db.publish("p", first_input, ["facts:asserted"], "query", ["late"], IMPL)
    assert db.result(late)["stale"] == []  # historical identity is not a staleReason
    assert db.result(late)["state"] == "historical"
    assert db.current("p", "query", IMPL)["id"] == latest
    assert db.result(first)["state"] == "historical"
    assert db.result(latest)["state"] == "current"


@pytest.mark.parametrize(
    "dependencies",
    [[], ["query:unknown"], ["rule:unknown"], ["facts:asserted", "scenario:unknown"], [42]],
)
def test_unregistered_or_empty_dependencies_cannot_be_published(db, dependencies):
    with pytest.raises(ValueError):
        db.publish("p", db.snapshot("p"), dependencies, "query", [1], IMPL)
    assert db.current("p", "query", IMPL) is None


@pytest.mark.parametrize(
    "triple",
    [
        {"subject": "relative", "predicate": "urn:p", "object": '"x"'},
        {"subject": "urn:s", "predicate": "urn:p"},
        {"subject": "urn:s", "predicate": "urn:p", "object": '"""alias"""'},
        {"subject": "urn:s", "predicate": "urn:p", "object": "<relative>"},
    ],
)
def test_invalid_ontology_triples_fail_in_commit_not_later_graph_build(db, triple):
    before = db.state("p")
    with pytest.raises(ValueError):
        db.commit(
            "p",
            1,
            "bad-definition",
            "job",
            definitions=[{"layer": "ontology", "id": "bad", "value": {"triples": [triple]}}],
            manual=[fact("urn:other")],
        )
    assert db.state("p") == before
    assert db.revision("p") == 1
    assert db.marker("p", "bad-definition") is None


def test_valid_ontology_triples_are_normalized_and_rebuilt(db):
    from ontolearn_engine.rdf_snapshot import graph_from_snapshot
    from rdflib import Literal, URIRef

    db.commit(
        "p",
        1,
        "ontology",
        "job",
        definitions=[
            {
                "layer": "ontology",
                "id": "axiom",
                "value": {
                    "triples": [
                        {"subject": "urn:class", "predicate": "urn:label", "object": '"设备"@zh'}
                    ]
                },
            }
        ],
    )
    assert (URIRef("urn:class"), URIRef("urn:label"), Literal("设备", lang="zh")) in (
        graph_from_snapshot(db.load_snapshot(db.snapshot("p")))
    )


def make_legacy(path):
    connection = sqlite3.connect(path)
    for statement in SCHEMA:
        connection.execute(statement)
    connection.execute("INSERT INTO projects VALUES('p',1)")
    f = fact()
    connection.execute(
        "INSERT INTO facts VALUES(?,?,?,?,?,?,?,?)",
        ("p", f["id"], f["subject"], f["predicate"], f["object"], "M1", "001", f["object"]),
    )
    connection.execute("INSERT INTO versions VALUES('p','facts:asserted',1)")
    connection.execute("INSERT INTO versions VALUES('p','mapping:M1',1)")
    connection.execute("PRAGMA user_version=1")
    connection.commit()
    connection.close()


MIGRATION_POINTS = [
    "before",
    "mapping_state_created",
    "mapping_state_backfilled",
    "commit_evidence_created",
    "immutable_triggers_created",
    "current_results_copied",
    "current_results_replaced",
    "migration_mid",
    "format_version_updated",
    "before_commit",
    "after_commit",
]


@pytest.mark.parametrize("point", MIGRATION_POINTS)
@pytest.mark.parametrize("failure", ["exception", "exit"])
def test_migration_each_ddl_commit_and_process_exit_is_recoverable(tmp_path, point, failure):
    path = tmp_path / "legacy.db"
    make_legacy(path)
    initial = sqlite3.connect(path)
    schema = initial.execute("SELECT type,name,sql FROM sqlite_master ORDER BY name").fetchall()
    facts = initial.execute("SELECT * FROM facts").fetchall()
    initial.close()
    if failure == "exception":

        def fail(stage):
            if stage == point:
                raise RuntimeError("migration boundary failure")

        with pytest.raises(RuntimeError):
            Store(path, migration_hook=fail)
    else:
        code = """
import os,sys
from ontolearn_engine.storage import Store
def hook(stage):
    if stage==sys.argv[2]: os._exit(73)
Store(sys.argv[1], migration_hook=hook)
"""
        result = subprocess.run([sys.executable, "-c", code, str(path), point], timeout=15)
        assert result.returncode == 73
    connection = sqlite3.connect(path)
    assert connection.execute("SELECT * FROM facts").fetchall() == facts
    if point == "after_commit":
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
    else:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert (
            connection.execute("SELECT type,name,sql FROM sqlite_master ORDER BY name").fetchall()
            == schema
        )
    connection.close()
    recovered = Store(path)
    assert recovered.revision("p") == 1
    assert recovered.state("p")["facts"][0]["owner"] == "M1"
    assert recovered.mapping_status("p", "M1")["generatedVersion"] == -1
    recovered.close()


def test_current_format_open_does_not_take_writer_lock(db):
    db._db.execute("BEGIN IMMEDIATE")
    reader = None
    try:
        reader = Store(db.path)
        assert reader.revision("p") == 1
        assert reader.state("p")["facts"] == db.state("p")["facts"]
    finally:
        db._db.execute("ROLLBACK")
        if reader:
            reader.close()


def test_concurrent_migration_rereads_version_after_lock(tmp_path):
    import threading

    path = tmp_path / "legacy.db"
    make_legacy(path)
    waiting = threading.Event()
    proceed = threading.Event()
    outcomes = []

    def hook(stage):
        if stage == "before":
            waiting.set()
            assert proceed.wait(10)

    def delayed_opener():
        try:
            delayed = Store(path, migration_hook=hook)
            outcomes.append(delayed.revision("p"))
            delayed.close()
        except BaseException as error:
            outcomes.append(error)

    thread = threading.Thread(target=delayed_opener)
    thread.start()
    assert waiting.wait(10)
    first = Store(path)
    first.close()
    proceed.set()
    thread.join(10)
    assert not thread.is_alive()
    assert outcomes == [1]


@pytest.mark.parametrize("bad", [12345, True, None, ""])
def test_operation_and_job_identity_types_are_checked_before_write(db, bad):
    with pytest.raises(ValueError):
        db.commit("p", 1, bad, "job", manual=[fact("urn:bad")])
    with pytest.raises(ValueError):
        db.commit("p", 1, "operation", bad, manual=[fact("urn:bad")])
    assert db.revision("p") == 1


def test_round_retry_after_ack_loss_is_idempotent_and_cross_run_reuse_is_conflict(db):
    input_id = db.snapshot("p")
    run = db.start_run("p", input_id, {"maxRounds": 4}, IMPL)

    def lost(phase):
        if phase == "after_commit":
            raise OSError("response delivery lost")

    with pytest.raises(OSError):
        db.commit_round(run, 1, {"orders": ["W001"]}, "once-round", "job", hook=lost)
    original = db.progress(run)["snapshotRef"]
    assert db.commit_round(run, 1, {"orders": ["W001"]}, "once-round", "job") == original
    assert len(db.history(run)["rounds"]) == 1
    with pytest.raises(Conflict, match="reused"):
        db.commit_round(run, 1, {"orders": ["different"]}, "once-round", "job")
    other = db.start_run("p", input_id, {"maxRounds": 4}, IMPL)
    with pytest.raises(Conflict, match="reused"):
        db.commit_round(other, 1, {"orders": ["W001"]}, "once-round", "job")
    assert db.progress(other) is None
    db.finish_run(run, "cancelled", {})
    assert db.commit_round(run, 1, {"orders": ["W001"]}, "once-round", "job") == original


def test_tombstone_restore_and_net_zero_change_do_not_spuriously_invalidate(db):
    identity = db.state("p")["facts"][0]["id"]
    db.commit("p", 1, "delete", "job", remove=[identity])
    before = db.vector("p")
    db.commit("p", 2, "delete-again", "job", remove=[identity])
    assert db.vector("p") == before
    db.commit("p", 3, "explicit-restore", "job", edits={identity: '"泵站A"'})
    db.commit("p", 4, "rerun", "job", mapping=mapped())
    assert db.mapping_status("p", "M1")["stale"] == []
    db.commit("p", 5, "manual", "job", manual=[fact("urn:manual")])
    before = db.vector("p")
    result = db.publish("p", db.snapshot("p"), ["facts:asserted"], "query", ["stable"], IMPL)
    db.commit(
        "p",
        6,
        "replace-same",
        "job",
        remove=[fact("urn:manual")["id"]],
        manual=[fact("urn:manual")],
    )
    assert db.vector("p") == before
    assert db.result(result)["stale"] == []


@pytest.mark.parametrize("blocked_module", ["resource", "ontolearn_engine.storage_probe"])
def test_missing_unix_probe_module_cannot_break_health_or_measurement(blocked_module):
    entry = Path(__file__).parents[1] / "entrypoint.py"
    code = """
import importlib.abc,runpy,sys
blocked=sys.argv[2]
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname==blocked:
            raise ModuleNotFoundError(fullname, name=fullname)
sys.meta_path.insert(0,Block())
if sys.argv[2]=='resource':
    from ontolearn_engine.storage_probe import measure
    result=measure(1)
    assert result['rssAvailable'] is False
    assert all(v['processHighWaterRssBytes'] is None for v in result['measurement'].values())
    assert 'RSS unavailable' in result['method']
entry=sys.argv[1]
sys.argv=[entry]
runpy.run_path(entry,run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(entry), blocked_module],
        input=json.dumps({"id": "portable", "method": "health", "protocolVersion": 1}) + "\n",
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    assert json.loads(result.stdout)["result"]["capabilities"] == ["health"]


def test_machine_readable_implementation_and_publication_policy():
    assert RULES["schemaVersion"] == 2
    assert RULES["implementationCompatibility"]["default"] == "isolate"
    assert RULES["implementationCompatibility"]["identityKeys"] == list(IMPL)
    assert RULES["implementationCompatibility"]["staleReason"] is None
    assert RULES["publicationPolicy"]["currentRequiresLatestProjectRevision"] is True
    assert RULES["publicationPolicy"]["staleReason"] is None


@pytest.mark.parametrize(
    "point", ["v1_created", "format_version_updated", "before_commit", "after_commit"]
)
@pytest.mark.parametrize("failure", ["exception", "exit"])
def test_initial_schema_creation_failure_is_atomic_and_retryable(tmp_path, point, failure):
    path = tmp_path / "new.db"
    if failure == "exception":

        def fail(stage):
            if stage == point:
                raise RuntimeError("bootstrap boundary failure")

        with pytest.raises(RuntimeError):
            Store(path, migration_hook=fail)
    else:
        code = """
import os,sys
from ontolearn_engine.storage import Store
def hook(stage):
    if stage==sys.argv[2]: os._exit(73)
Store(sys.argv[1],migration_hook=hook)
"""
        result = subprocess.run([sys.executable, "-c", code, str(path), point], timeout=15)
        assert result.returncode == 73
    connection = sqlite3.connect(path)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == (
        2 if point == "after_commit" else 0
    )
    if point != "after_commit":
        assert connection.execute("SELECT name FROM sqlite_master").fetchall() == []
    connection.close()
    recovered = Store(path)
    recovered.create_project("after-recovery")
    assert recovered.revision("after-recovery") == 0
    recovered.close()


def test_revision_round_and_mapping_identity_shapes_are_rejected(db):
    with pytest.raises(ValueError, match="projectRevision"):
        db.commit("p", True, "bool-revision", "job", manual=[fact("urn:bad")])
    for bad_mapping in ({"id": 123, "rows": []}, {"id": "M", "rows": [{"row": 1, "facts": []}]}):
        with pytest.raises(ValueError):
            db.commit("p", 1, "bad-mapping-id", "job", mapping=bad_mapping)
    run = db.start_run("p", db.snapshot("p"), {"maxRounds": 4}, IMPL)
    with pytest.raises(ValueError, match="Integer round"):
        db.commit_round(run, True, {}, "bool-round", "job")
    assert db.progress(run) is None
    assert db.revision("p") == 1


def test_managed_delete_restore_in_same_plan_preserves_mapping_dependency_version(db):
    identity = db.state("p")["facts"][0]["id"]
    before_state = db.state("p")
    before_vector = db.vector("p")
    result = db.publish("p", db.snapshot("p"), ["mapping:M1"], "query", ["stable"], IMPL)
    db.commit("p", 1, "net-zero-managed", "job", remove=[identity], edits={identity: '"泵站A"'})
    assert db.state("p") == before_state
    assert db.vector("p") == before_vector
    assert db.mapping_status("p", "M1")["stale"] == []
    assert db.result(result)["stale"] == []
    db.commit(
        "p",
        2,
        "real-source-change",
        "job",
        remove=[identity],
        edits={identity: '"泵站A"'},
        definitions=[{"layer": "mapping", "id": "M1", "value": {"sourceHash": "new"}}],
    )
    assert db.vector("p")["mapping:M1"] == before_vector["mapping:M1"] + 1
    assert db.result(result)["stale"][0]["code"] == "MAPPING_INPUT_CHANGED"


def test_registered_empty_mapping_scope_is_valid_but_not_unknown_mapping(db):
    db.commit("p", 1, "empty-source", "job", mapping={"id": "empty", "rows": []})
    result = db.publish("p", db.snapshot("p"), ["mapping:empty"], "empty-view", [], IMPL)
    assert db.result(result)["state"] == "current"
    with pytest.raises(ValueError, match="Unresolved"):
        db.publish("p", db.snapshot("p"), ["mapping:never-declared"], "ghost", [], IMPL)
    db.commit(
        "p",
        2,
        "new-input",
        "job",
        definitions=[{"layer": "mapping", "id": "empty", "value": {"sourceHash": "changed"}}],
    )
    assert db.result(result)["stale"][0]["code"] == "MAPPING_INPUT_CHANGED"
