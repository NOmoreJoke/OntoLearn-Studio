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
        input=json.dumps(
            {
                "kind": "request",
                "id": "00000000-0000-4000-8000-000000000011",
                "method": "hello",
                "protocolVersion": 2,
                "engineSessionId": None,
                "params": {
                    "supportedVersions": [2],
                    "clientId": "00000000-0000-4000-8000-000000000012",
                },
            }
        )
        + "\n",
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    hello = json.loads(result.stdout)["result"]
    assert "health" in hello["capabilities"] and hello["selectedVersion"] == 2
    assert all(not name.startswith("test.") for name in hello["capabilities"])


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


@pytest.mark.parametrize("drift", ["tombstone", "edited"])
def test_reserved_fact_identity_conflict_is_locatable_without_blocking_other_values(db, drift):
    original = fact()
    if drift == "tombstone":
        db.commit("p", 1, "drift", "job", remove=[original["id"]])
    else:
        db.commit("p", 1, "drift", "job", edits={original["id"]: '"人工值"'})
    before, vector = db.state("p"), db.vector("p")
    with pytest.raises(Conflict, match="Ownership conflict") as error:
        db.commit("p", 2, "other-owner", "job", mapping=mapped(owner="M2"))
    for location in ("urn:equipment/001", "urn:name", "other=M1", "row=001", original["id"]):
        assert location in str(error.value)
    assert db.revision("p") == 2
    assert db.state("p") == before
    assert db.vector("p") == vector
    assert db.marker("p", "other-owner") is None
    # A reserved identity is not a blanket reservation of a multi-valued SP slot.
    db.commit("p", 2, "distinct-owner", "job", mapping=mapped('"另一值"', owner="M2"))
    assert {r["owner"] for r in db.state("p")["facts"]} == {"M1", "M2"}


def test_round_evidence_cannot_become_project_input_or_claim_legacy_replayability(db):
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    project_input = db.snapshot("p")
    run = db.start_run("p", project_input, config, IMPL)
    round_input = db.commit_round(run, 1, {"orders": ["W001"]}, "round-shape", "job")
    counts = {
        table: db._db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("runs", "results", "snapshots")
    }
    for start in (True, False):
        with pytest.raises(ValueError, match="Project state snapshot"):
            if start:
                db.start_run("p", round_input, config, IMPL)
            else:
                db.publish("p", round_input, ["facts:asserted"], "q", [], IMPL)
    assert counts == {
        table: db._db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in counts
    }
    # Existing immutable records from the earlier spike remain viewable, but honest.
    db._db.execute(
        "INSERT INTO runs VALUES(?,?,?,?,?)",
        ("legacy-round-input", "p", round_input, json.dumps(config), json.dumps(IMPL)),
    )
    history = db.history("legacy-round-input")
    assert history["snapshot"] == round_input and history["replayable"] is False
    assert db.history(run)["replayable"] is True
    assert db.load_snapshot(round_input)["state"] == {"orders": ["W001"]}


@pytest.mark.parametrize(
    "replacement",
    [
        {"projectRevision": None},
        {"projectRevision": True},
        {"projectRevision": -1},
        {"dependencyVector": None},
        {"dependencyVector": {"facts:asserted": True}},
        {"dependencyVector": {"facts:asserted": -1}},
        {"dependencyVector": {"unknown:x": 1}},
        {"state": {}},
        {"state": {"definitions": [], "facts": [], "mappingState": None}},
    ],
)
def test_project_input_shape_is_rejected_for_new_and_legacy_runs(db, replacement):
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    payload = db.load_snapshot(db.snapshot("p")) | replacement
    with db._transaction():
        bad = db._snapshot(payload)
    with pytest.raises(ValueError):
        db.start_run("p", bad, config, IMPL)
    with pytest.raises(ValueError):
        db.publish("p", bad, ["facts:asserted"], "q", [], IMPL)
    db._db.execute(
        "INSERT INTO runs VALUES(?,?,?,?,?)",
        ("legacy-malformed", "p", bad, json.dumps(config), json.dumps(IMPL)),
    )
    assert db.history("legacy-malformed")["replayable"] is False


@pytest.mark.parametrize("implementation", [None, [], 42, "engine"])
def test_publish_provenance_shape_has_stable_validation_error(db, implementation):
    with pytest.raises(ValueError, match="provenance"):
        db.publish("p", db.snapshot("p"), ["facts:asserted"], "q", [], implementation)
    assert db._db.execute("SELECT COUNT(*) FROM results").fetchone()[0] == 0


def test_g_map_empty_fixed_two_row_prepared_collection_is_exact_and_repeatable(tmp_path):
    from storage_baselines import g_definitions

    store = Store(tmp_path / "two-row.db")
    store.create_project("G-map-empty")
    store.commit("G-map-empty", 0, "definitions", "job", definitions=g_definitions())
    rows = [("001", "泵站A"), ("002", "泵站B")]
    plan = {
        "id": "fixed-csv",
        "rows": [
            {
                "row": key,
                "facts": [
                    fact(f"urn:equipment/{key}", f'"{name}"'),
                    fact(f"urn:equipment/{key}", "<urn:Equipment>", "urn:type"),
                ],
            }
            for key, name in rows
        ],
    }
    store.commit("G-map-empty", 1, "map", "job", mapping=plan)
    expected = {
        (f"urn:equipment/{key}", predicate, value, "fixed-csv", key)
        for key, name in rows
        for predicate, value in (("urn:name", f'"{name}"'), ("urn:type", "<urn:Equipment>"))
    }
    facts = store.state("G-map-empty")["facts"]
    assert {
        (r["subject"], r["predicate"], r["object"], r["owner"], r["source_row"]) for r in facts
    } == expected
    vector = store.vector("G-map-empty")
    store.commit("G-map-empty", 2, "repeat", "job", mapping=plan)
    assert store.state("G-map-empty")["facts"] == facts
    assert store.vector("G-map-empty") == vector
    store.close()


def test_incomplete_round_state_is_rejected_and_legacy_evidence_not_replayable(db):
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    run = db.start_run("p", db.snapshot("p"), config, IMPL)
    with pytest.raises(ValueError, match="round state"):
        db.commit_round(run, 1, None, "bad-state", "job")
    assert db.progress(run) is None
    with db._transaction():
        saved = db._snapshot({"project": "p", "run": run, "round": 1, "state": None})
        db._db.execute("INSERT INTO rounds VALUES(?,?,?,?,?)", (run, 1, saved, "legacy", "job"))
    assert db.history(run)["rounds"][0]["snapshot"] == saved
    assert db.history(run)["replayable"] is False


@pytest.mark.parametrize("field", ["config", "implementation"])
def test_legacy_nonobject_run_configuration_is_not_claimed_replayable(db, field):
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    values = {"config": config, "implementation": IMPL}
    values[field] = None
    db._db.execute(
        "INSERT INTO runs VALUES(?,?,?,?,?)",
        (
            "legacy-nonobject",
            "p",
            db.snapshot("p"),
            json.dumps(values["config"]),
            json.dumps(values["implementation"]),
        ),
    )
    assert db.history("legacy-nonobject")["replayable"] is False


@pytest.mark.parametrize(
    "field,record",
    [
        ("facts", None),
        ("facts", {}),
        (
            "facts",
            {
                "id": "x",
                "subject": "urn:s",
                "predicate": "urn:p",
                "object": None,
                "owner": None,
                "source_row": None,
                "managed_value": None,
            },
        ),
        (
            "facts",
            {
                "id": "x",
                "subject": "urn:s",
                "predicate": "urn:p",
                "object": '"x"',
                "owner": "M1",
                "source_row": None,
                "managed_value": '"x"',
            },
        ),
        ("definitions", None),
        ("definitions", {}),
        ("definitions", {"layer": [], "id": "one", "payload": "{}"}),
        ("definitions", {"layer": "rule", "id": "one", "payload": "not json"}),
        ("definitions", {"layer": "rule", "id": "one", "payload": '{"value":NaN}'}),
        ("definitions", {"layer": "rule", "id": "one", "payload": '{"references":[null]}'}),
    ],
)
def test_incomplete_snapshot_records_are_rejected_and_legacy_history_honest(db, field, record):
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    payload = db.load_snapshot(db.snapshot("p"))
    payload["state"][field] = [record]
    with db._transaction():
        bad = db._snapshot(payload)
    with pytest.raises(ValueError):
        db.start_run("p", bad, config, IMPL)
    with pytest.raises(ValueError):
        db.publish("p", bad, ["rule:risk"], "q", [], IMPL)
    db._db.execute(
        "INSERT INTO runs VALUES(?,?,?,?,?)",
        ("legacy-record", "p", bad, json.dumps(config), json.dumps(IMPL)),
    )
    assert db.history("legacy-record")["replayable"] is False


@pytest.mark.parametrize(
    "status",
    [
        None,
        {},
        {"generatedVersion": True, "stale": []},
        {"generatedVersion": -2, "stale": []},
        {"generatedVersion": 1, "stale": [None]},
        {
            "generatedVersion": 1,
            "stale": [
                {
                    "code": "MAPPING_INPUT_CHANGED",
                    "dependency": "mapping:M1",
                    "before": True,
                    "after": 2,
                }
            ],
        },
    ],
)
def test_incomplete_snapshot_mapping_state_is_not_replayable(db, status):
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    payload = db.load_snapshot(db.snapshot("p"))
    payload["state"]["mappingState"] = {"M1": status}
    with db._transaction():
        bad = db._snapshot(payload)
    with pytest.raises(ValueError):
        db.start_run("p", bad, config, IMPL)
    db._db.execute(
        "INSERT INTO runs VALUES(?,?,?,?,?)",
        ("legacy-status", "p", bad, json.dumps(config), json.dumps(IMPL)),
    )
    assert db.history("legacy-status")["replayable"] is False


@pytest.mark.parametrize("value", [None, '"人工值"'])
def test_valid_edited_identity_and_tombstone_remain_usable_project_inputs(db, value):
    config = {
        "maxRounds": 4,
        "events": [],
        "parameters": {},
        "ruleVersions": {},
        "behaviorVersions": {},
    }
    key = fact()["id"]
    changes = {"remove": [key]} if value is None else {"edits": {key: value}}
    db.commit("p", 1, "drift-input", "job", **changes)
    snap = db.snapshot("p")
    run = db.start_run("p", snap, config, IMPL)
    assert db.history(run)["replayable"] is True
    result = db.publish("p", snap, ["facts:asserted"], "q", [], IMPL)
    assert db.result(result)["state"] == "current"
    assert db.state("p")["facts"][0]["id"] == key


class TestColdSnapshotProjection:
    def test_write_token_cannot_be_reused_after_its_scope_or_by_another_store(self, tmp_path):
        store = Store(tmp_path / "token.sqlite")
        other = Store(tmp_path / "foreign-token.sqlite")
        try:
            store.create_project("p")
            identity = digest(store._snapshot_projection("p"))
            with store._snapshot_writer() as expired:
                pass
            trace = []
            with store._read():
                store._db.set_trace_callback(trace.append)
                with pytest.raises(Conflict, match="Snapshot write scope required"):
                    store._materialize_snapshot(identity, "p", _write_scope=expired)
                store._db.set_trace_callback(None)
            with other._snapshot_writer() as foreign:
                with store._read():
                    store._db.set_trace_callback(trace.append)
                    with pytest.raises(Conflict, match="Snapshot write scope required"):
                        store._materialize_snapshot(identity, "p", _write_scope=foreign)
                    store._db.set_trace_callback(None)
            assert trace == []
            assert store._db.execute("SELECT count(*) FROM snapshots").fetchone()[0] == 0
        finally:
            other.close()
            store.close()

    def test_projection_is_pure_and_not_a_claim_of_persistent_evidence(self, tmp_path):
        store = Store(tmp_path / "projection.sqlite")
        try:
            store.create_project("p")
            before = "\n".join(store._db.iterdump())
            trace = []
            store._db.set_trace_callback(trace.append)
            payload = store._snapshot_projection("p")
            identity = digest(payload)
            assert payload == {
                "project": "p",
                "projectRevision": 0,
                "dependencyVector": {},
                "state": {"definitions": [], "facts": [], "mappingState": {}},
            }
            assert store._snapshot_projection("p") == payload
            with pytest.raises(KeyError, match="Missing replay input snapshot"):
                store.load_snapshot(identity)
            with pytest.raises(KeyError, match="Missing replay input snapshot"):
                store._project_snapshot(identity, "p")
            assert "\n".join(store._db.iterdump()) == before
            assert not any("BEGIN IMMEDIATE" in sql.upper() for sql in trace)
            assert not any(sql.lstrip().upper().startswith("INSERT") for sql in trace)
            store._db.set_trace_callback(None)
            with store._snapshot_writer() as writer:
                assert store._materialize_snapshot(identity, "p", _write_scope=writer) == payload
            assert store.load_snapshot(identity) == payload
            assert store.snapshot("p") == identity  # Original explicit write API/hash is unchanged.
        finally:
            store.close()

    @pytest.mark.parametrize("writer", ["publish", "start_run"])
    def test_normal_writer_materializes_cold_input_and_keeps_history(self, tmp_path, writer):
        path = tmp_path / "consume.sqlite"
        store = Store(path)
        store.create_project("p")
        payload = store._snapshot_projection("p")
        identity = digest(payload)
        if writer == "publish":
            result = store.publish("p", identity, ["facts:asserted"], "query", [], IMPL)
            assert store.result(result)["snapshot"] == identity
        else:
            config = {
                "parameters": {},
                "events": [],
                "ruleVersions": {},
                "behaviorVersions": {},
                "maxRounds": 1,
            }
            run = store.start_run("p", identity, config, IMPL)
            assert (
                store._db.execute("SELECT snapshot FROM runs WHERE id=?", (run,)).fetchone()[0]
                == identity
            )
            assert store.history(run)["replayable"] is True
        assert store.load_snapshot(identity) == payload
        store.commit("p", 0, "advance", "domain-job", manual=[fact()])
        assert digest(store._snapshot_projection("p")) != identity
        assert store._project_snapshot(identity, "p") == payload
        store.close()
        reopened = Store(path)
        try:
            assert reopened.load_snapshot(identity) == payload
            assert reopened._project_snapshot(identity, "p") == payload
            if writer == "start_run":
                assert reopened.history(run)["replayable"] is True
        finally:
            reopened.close()

    @pytest.mark.parametrize("writer", ["publish", "start_run"])
    def test_missing_noncurrent_identity_cannot_be_replaced_with_current(self, tmp_path, writer):
        store = Store(tmp_path / "mismatch.sqlite")
        try:
            store.create_project("p")
            store.create_project("other")
            foreign = digest(store._snapshot_projection("other"))
            before = "\n".join(store._db.iterdump())
            with pytest.raises(Conflict, match="Current snapshot identity changed") as caught:
                if writer == "publish":
                    store.publish("p", foreign, ["facts:asserted"], "query", [], IMPL)
                else:
                    store.start_run("p", foreign, {}, IMPL)
            assert caught.value.category == "identity"
            assert "\n".join(store._db.iterdump()) == before
            with pytest.raises(KeyError, match="Missing replay input snapshot"):
                store.load_snapshot(foreign)
        finally:
            store.close()
