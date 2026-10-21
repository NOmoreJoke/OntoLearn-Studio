"""Private Store-ready acceptance on synthetic databases only; no business3/Job-ready."""

import hashlib
import os
import sqlite3
import subprocess
import sys

import pytest
from ontolearn_engine.project import format3
from ontolearn_engine.project.format3 import Format3Fault, logical_hash
from ontolearn_engine.storage import FORMAT_VERSION, SCHEMA, Conflict, Store, canonical, digest
from test_storage import make_legacy

IMPL = {
    "executionSemanticsVersion": "format3-test",
    "engineVersion": "test",
    "dependencyLockHash": "test",
}
MIGRATION_PHASES = (
    [
        "before_backup",
        "after_backup",
        "before",
        "v1_created",
        "mapping_state_created",
        "mapping_state_backfilled",
        "commit_evidence_created",
        "immutable_triggers_created",
        "current_results_copied",
        "current_results_replaced",
        "migration_mid",
        "format_version_updated",
    ]
    + ["format3_ddl:" + name for name, _ in format3.TABLES + format3.TRIGGERS]
    + [
        "format3_catalog",
        "format3_project",
        "format3_validated",
        "format3_version",
        "before_commit",
        "after_commit",
    ]
)


def fact(subject="urn:test/1", value='"human"'):
    return {
        "id": digest([subject, "urn:name", value]),
        "subject": subject,
        "predicate": "urn:name",
        "object": value,
    }


def synthetic(path, version=2):
    if version == 0:
        con = sqlite3.connect(path)
        con.execute("PRAGMA user_version=0")
        con.close()
        return
    if version == 1:
        make_legacy(path)  # approved real fixture: revision1, facts, no old commit evidence
        return
    store = Store(path)
    store.create_project("p")
    store.commit(
        "p",
        0,
        "initial",
        "j0",
        manual=[fact()],
        mapping={"id": "m", "rows": [{"row": "1", "facts": [fact("urn:mapped/1", '"source"')]}]},
        definitions=[{"layer": "rule", "id": "r", "value": {"enabled": True}}],
    )
    managed = next(r["id"] for r in store.state("p")["facts"] if r["owner"])
    store.commit("p", 1, "edit", "j1", edits={managed: '"edited"'})
    store.commit("p", 2, "delete", "j2", remove=[managed])
    snap = store.snapshot("p")
    store.publish("p", snap, ["facts:asserted"], "query", ["cached"], IMPL)
    run = store.start_run("p", snap, {"maxRounds": 2}, IMPL)
    store.commit_round(run, 1, {"facts": ["frozen"]}, "round-one", "jr")
    store.close()


def frozen(path):
    con = sqlite3.connect(path)
    result = {
        "dump": logical_hash(con),
        "format": con.execute("PRAGMA user_version").fetchone()[0],
        "snapshots": con.execute("SELECT * FROM snapshots").fetchall()
        if con.execute("SELECT 1 FROM sqlite_master WHERE name='snapshots'").fetchone()
        else [],
    }
    con.close()
    return result


def test_explicit_gate_backup_and_full_domain_history(tmp_path):
    path, backup = tmp_path / "p.db", tmp_path / "before.db"
    synthetic(path)
    before = frozen(path)
    with pytest.raises(Format3Fault) as error:
        Store(path, target_format=3)
    assert error.value.category == "backupRequired"
    assert frozen(path) == before
    store = Store(path, target_format=3, backup_path=backup)
    assert FORMAT_VERSION == 2 and store.actual_format == 3
    assert frozen(backup) == before
    assert frozen(path)["snapshots"] == before["snapshots"]  # genesis snapshot already existed
    checkpoint = store.project_checkpoint("p")
    assert checkpoint["domainRevision"] == 3 and checkpoint["operationSequence"] == 3
    assert checkpoint["application"]["metadata"]["name"] is None
    assert checkpoint["historyCoverage"]["legacyDomainOperations"] == 3
    assert store.project_receipt("p", "initial")["status"] == "legacy-not-recorded"
    proof = store._db.execute("SELECT * FROM app_format").fetchone()
    assert proof["source_format"] == 2
    assert proof["backup_hash"] == hashlib.sha256(backup.read_bytes()).hexdigest()
    saved = list(store._db.execute("SELECT * FROM commits"))
    store.close()
    with pytest.raises(ValueError, match="Unsupported future project format"):
        Store(path)
    reopened = Store(path, target_format=3)
    assert [tuple(r) for r in reopened._db.execute("SELECT * FROM commits")] == [
        tuple(r) for r in saved
    ]
    assert frozen(backup) == before
    reopened.close()


@pytest.mark.parametrize("target", [True, 1, 4, "3", None])
def test_explicit_target_is_strict(tmp_path, target):
    with pytest.raises(ValueError):
        Store(tmp_path / "unused.db", target_format=target)
    assert not (tmp_path / "unused.db").exists()


@pytest.mark.parametrize("version", [0, 1, 2])
def test_backup_never_overwrites_and_source_change_rejects(tmp_path, version):
    path, backup = tmp_path / "p.db", tmp_path / "backup.db"
    synthetic(path, version)
    baseline = frozen(path)
    backup.write_bytes(b"keep")
    with pytest.raises(Format3Fault) as err:
        Store(path, target_format=3, backup_path=backup)
    assert err.value.category == "backupExists" and backup.read_bytes() == b"keep"
    assert frozen(path) == baseline
    backup.unlink()  # own synthetic destination, to test a distinct migration attempt

    def hook(phase):
        if phase == "after_backup":
            con = sqlite3.connect(path)
            con.execute("CREATE TABLE changed_after_backup(value TEXT)")
            con.close()

    with pytest.raises(Format3Fault) as err:
        Store(path, hook, target_format=3, backup_path=backup)
    assert err.value.category == "sourceChanged"
    assert frozen(backup) == baseline
    assert frozen(path)["format"] == version


@pytest.mark.parametrize("version", [0, 1, 2])
@pytest.mark.parametrize("phase", MIGRATION_PHASES)
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_migration_atomic_faults(tmp_path, version, phase, failure):
    # Skip stages absent from the actual original format; do not invent passed hooks.
    if phase in {"before_backup", "after_backup"}:
        pass
    elif phase == "v1_created" and version != 0:
        pytest.skip("only format0 creates v1")
    elif phase in MIGRATION_PHASES[4:12] and version == 2:
        pytest.skip("format2 already has v2 tables")
    elif phase == "format3_project" and version == 0:
        pytest.skip("empty format0 has no projects")
    path, backup = tmp_path / "p.db", tmp_path / "backup.db"
    synthetic(path, version)
    before = frozen(path)
    if failure == "exit":
        script = """
import os,sys
from ontolearn_engine.storage import Store
def hook(p):
    if p == sys.argv[3]: os._exit(79)
Store(sys.argv[1],hook,target_format=3,backup_path=sys.argv[2])
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), str(backup), phase],
            capture_output=True,
            timeout=15,
        )
        assert result.returncode == 79, result.stderr.decode()
    else:
        error = {"exception": RuntimeError, "cancel": KeyboardInterrupt, "disk": OSError}[failure]

        def hook(p):
            if p == phase:
                raise error("injected")

        with pytest.raises(error):
            Store(path, hook, target_format=3, backup_path=backup)
    if phase == "after_commit":
        assert frozen(path)["format"] == 3
        store = Store(path, target_format=3)
        store.close()
    else:
        assert frozen(path) == before
    if backup.exists():
        assert frozen(backup) == before
    # Failure/exit must release the lifetime lease. Never unlink leased inode.
    lease = format3.acquire_lease(path)
    lease.close()


@pytest.mark.parametrize(
    "phase",
    [
        "mid_marker",
        "format3_sequence",
        "format3_checkpoint",
        "format3_receipt",
        "before_commit",
        "after_commit",
    ],
)
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_domain_receipt_checkpoint_atomic(tmp_path, phase, failure):
    path = tmp_path / "p.db"
    store = Store(path, target_format=3)
    store.create_project("p")
    before = frozen(path)
    store.close()
    if failure == "exit":
        script = """
import os,sys
from ontolearn_engine.storage import Store
s=Store(sys.argv[1],target_format=3)
def hook(p):
    if p == sys.argv[2]: os._exit(79)
s.commit('p',0,'op','job',hook=hook)
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), phase], capture_output=True, timeout=15
        )
        assert result.returncode == 79, result.stderr.decode()
    else:
        store = Store(path, target_format=3)
        error = {"exception": RuntimeError, "cancel": KeyboardInterrupt, "disk": OSError}[failure]

        def hook(p):
            if p == phase:
                raise error("injected")

        with pytest.raises(error):
            store.commit("p", 0, "op", "job", hook=hook)
        store.close()
    store = Store(path, target_format=3)
    if phase == "after_commit":
        marker = store.marker("p", "op")
        receipt = store.project_receipt("p", "op")
        assert receipt["operationSequence"] == 1 and receipt["domainAfterRevision"] == 1
        current = frozen(path)
        assert store.commit("p", 0, "op", "job") == marker
        assert frozen(path) == current
        with pytest.raises(Conflict):
            store.commit("p", 0, "op", "different-job")
        assert store.vector("p") == {}  # domain no-op still advances revision/sequence
    else:
        assert frozen(path) == before
    store.close()


@pytest.mark.parametrize(
    "mutation",
    [
        "DROP TABLE app_drafts",
        "DROP TABLE definition_retirements",
        "DROP TRIGGER immutable_snapshots_UPDATE",
        "DROP TRIGGER immutable_app_receipts_DELETE",
        "UPDATE app_projects SET operation_sequence=77",
        "UPDATE app_projects SET metadata_version=1",
        "UPDATE app_projects SET metadata='{}'",
        "INSERT INTO app_learning VALUES('p','a',0,'course','task','not-json')",
        "PRAGMA user_version=4",
    ],
)
def test_corruption_refuses_without_repair(tmp_path, mutation):
    path = tmp_path / "p.db"
    store = Store(path, target_format=3)
    store.create_project("p")
    store.close()
    con = sqlite3.connect(path)
    con.execute(mutation)
    con.commit()
    con.close()
    before = frozen(path)
    with pytest.raises(ValueError):
        Store(path, target_format=3)
    assert frozen(path) == before


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-application",
        "extra",
        "sequence",
        "bool-version",
        "wrong-domain-row",
        "bad-metadata",
        "bad-learning",
    ],
)
def test_forged_checkpoints_rejected(tmp_path, mutation):
    store = Store(tmp_path / "p.db", target_format=3)
    store.create_project("p")
    value = store.project_checkpoint("p")
    domain = value["domainSnapshotRef"]
    if mutation == "missing-application":
        del value["application"]
    elif mutation == "extra":
        value["unknown"] = True
    elif mutation == "sequence":
        value["operationSequence"] = 123
    elif mutation == "bool-version":
        value["checkpointVersion"] = True
    elif mutation == "wrong-domain-row":
        domain = "missing"
    elif mutation == "bad-metadata":
        value["application"]["metadata"]["name"] = 42
    elif mutation == "bad-learning":
        value["application"]["learningCurrent"] = [
            {"attempt": "a", "record_version": 0, "course": "c", "task": "t", "payload": "broken"}
        ]
    identity = digest(value)
    store._db.execute("PRAGMA foreign_keys=OFF")  # inject a corrupt fixture, never product repair
    if mutation == "wrong-domain-row":
        # Same identity already exists; a separate forged unknown field avoids PK collision.
        value["unknown"] = True
        identity = digest(value)
    store._db.execute(
        "INSERT INTO app_checkpoints VALUES(?,?,?,?)", (identity, "p", domain, canonical(value))
    )
    with pytest.raises(Format3Fault):
        store.project_checkpoint("p", identity)
    with pytest.raises(Format3Fault):
        format3.validate(store)
    store.close()


def test_same_writer_lease_lifetime_and_readonly_reopen(tmp_path):
    path = tmp_path / "p.db"
    store = Store(path, target_format=3)
    store.create_project("p")
    with pytest.raises(Format3Fault) as err:
        Store(path, target_format=3)
    assert err.value.category == "leaseBusy"
    store.close()
    reopened = Store(path, target_format=3)
    before = frozen(path)
    # Same schema open issues no DDL/writes: all read APIs work under SQLite query_only.
    reopened._db.execute("PRAGMA query_only=ON")
    format3.validate(reopened)
    reopened.project_checkpoint("p")
    assert frozen(path) == before
    reopened.close()


def test_approved_old_reader_rejects_actual3(tmp_path):
    path = tmp_path / "p.db"
    store = Store(path, target_format=3)
    store.close()
    base = "5f910b52c69d86a1076b2032e5d3c63e715947f3"
    old = subprocess.check_output(
        ["git", "show", base + ":packages/engine/src/ontolearn_engine/storage.py"]
    )
    module = tmp_path / "approved_storage.py"
    module.write_bytes(old)
    code = """
import sys
from approved_storage import Store
try: Store(sys.argv[1])
except ValueError as e:
    assert str(e)=='Unsupported future project format'
    sys.exit(0)
sys.exit(1)
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(path)],
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize("version", [1, 2])
def test_populated_legacy_partial_history_is_honest(tmp_path, version):
    path = tmp_path / "legacy.db"
    make_legacy(path)
    if version == 2:
        Store(path).close()
    before = frozen(path)
    store = Store(path, target_format=3, backup_path=tmp_path / "backup.db")
    initial = store.project_checkpoint("p")
    assert initial["domainRevision"] == 1 and initial["operationSequence"] == 0
    assert initial["historyCoverage"] == {
        "legacyDomainOperations": 0,
        "legacyDomainRevision": 1,
        "legacyHistory": "partial",
        "applicationHistory": "from-format3",
    }
    assert frozen(tmp_path / "backup.db") == before
    store.commit("p", 1, "first-recorded", "job")
    assert store.project_receipt("p", "first-recorded")["operationSequence"] == 1
    assert store.project_checkpoint("p")["domainRevision"] == 2
    store.close()
    reopened = Store(path, target_format=3)
    assert reopened.project_checkpoint("p")["historyCoverage"] == initial["historyCoverage"]
    reopened.close()


def test_existing_source_detected_after_lease_not_before_stat(tmp_path, monkeypatch):
    path = tmp_path / "race.db"
    acquire = format3.acquire_lease

    def preceding_writer(p):
        lease = acquire(p)
        old = Store(p)
        old.create_project("p")
        old.commit("p", 0, "old", "old-job")
        old.close()
        lease.close()
        return acquire(p)

    monkeypatch.setattr(format3, "acquire_lease", preceding_writer)
    with pytest.raises(Format3Fault) as error:
        Store(path, target_format=3)
    assert error.value.category == "backupRequired" and frozen(path)["format"] == 2
    assert (
        not sqlite3.connect(path)
        .execute("SELECT 1 FROM sqlite_master WHERE name='app_format'")
        .fetchone()
    )


@pytest.mark.parametrize("kind", ["legacy", "phantom"])
def test_forged_receipt_cannot_prove_checkpoint_source(tmp_path, kind):
    path = tmp_path / "p.db"
    old = Store(path)
    old.create_project("p")
    old.commit("p", 0, "old", "old-job")
    old.close()
    store = Store(path, target_format=3, backup_path=tmp_path / "before.db")
    value = store.project_checkpoint("p")
    genesis = digest(value)
    value["operationSequence"] = 0 if kind == "legacy" else 2
    identity = digest(value)
    store._db.execute(
        "INSERT INTO app_checkpoints VALUES(?,?,?,?)",
        (identity, "p", value["domainSnapshotRef"], canonical(value)),
    )
    operation = "old"
    if kind == "phantom":
        operation = "phantom"
        store._db.execute("INSERT INTO app_operations VALUES('p',2,'phantom','domain','fake',1)")
    store._db.execute(
        "INSERT INTO app_receipts VALUES(?,?,?)",
        (
            "p",
            operation,
            canonical({"beforeCheckpointRef": identity, "afterCheckpointRef": genesis}),
        ),
    )
    with pytest.raises(Format3Fault):
        store.project_checkpoint("p", identity)
    with pytest.raises(Format3Fault):
        format3.validate(store)
    store.close()


@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_older_v1_without_optional_retirement_table_migrates_atomically(tmp_path, failure):
    path = tmp_path / "old.db"
    make_legacy(path)
    con = sqlite3.connect(path)
    con.execute("DROP TABLE definition_retirements")
    con.close()
    original = frozen(path)
    backup = tmp_path / "first-backup.db"
    if failure == "exit":
        script = """import os,sys
from ontolearn_engine.storage import Store
def hook(p):
    if p=='format3_domain_retirements': os._exit(79)
Store(sys.argv[1],hook,target_format=3,backup_path=sys.argv[2])
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), str(backup)], capture_output=True, timeout=15
        )
        assert result.returncode == 79, result.stderr.decode()
    else:
        error = {"exception": RuntimeError, "cancel": KeyboardInterrupt, "disk": OSError}[failure]

        def hook(phase):
            if phase == "format3_domain_retirements":
                raise error("injected")

        with pytest.raises(error):
            Store(path, hook, target_format=3, backup_path=backup)
    assert frozen(path) == original and frozen(backup) == original
    store = Store(path, target_format=3, backup_path=tmp_path / "second-backup.db")
    assert store._has_retirements() and store.actual_format == 3
    store.close()


@pytest.mark.parametrize("start", [format3.MAX_VERSION - 1, format3.MAX_VERSION])
def test_domain_revision_limit_never_publishes_unreadable_store(tmp_path, start):
    path = tmp_path / "limit.db"
    make_legacy(path)
    con = sqlite3.connect(path)
    con.execute("UPDATE projects SET revision=?", (start,))
    con.commit()
    con.close()
    store = Store(path, target_format=3, backup_path=tmp_path / "before.db")
    if start < format3.MAX_VERSION:
        marker = store.commit("p", start, "last", "job")
        committed = frozen(path)
        assert store.project_receipt("p", "last")["domainAfterRevision"] == format3.MAX_VERSION
        assert store.commit("p", start, "last", "job") == marker
        assert frozen(path) == committed
    before = frozen(path)
    with pytest.raises(Conflict):
        store.commit("p", format3.MAX_VERSION, "over-limit", "job2")
    assert frozen(path) == before
    assert store.project_checkpoint("p")["domainRevision"] == format3.MAX_VERSION
    store.close()
    reopened = Store(path, target_format=3)
    assert reopened.project_checkpoint("p")["domainRevision"] == format3.MAX_VERSION
    assert frozen(path) == before
    reopened.close()


DOMAIN_V2_PHASES = [
    "format3_v2_ddl:" + name
    for name in (
        "mapping_state",
        "commit_evidence",
        "immutable_commit_evidence_UPDATE",
        "immutable_commit_evidence_DELETE",
        "migration_log",
        "current_results_v2",
        "drop_current_results",
        "rename_current_results",
    )
] + ["format3_v2_backfill:migration_log"]
DOMAIN_DDL_CASES = [(0, "format3_v1_ddl:" + str(i)) for i in range(len(SCHEMA))] + [
    (version, phase) for version in (0, 1) for phase in DOMAIN_V2_PHASES
]


@pytest.mark.parametrize("version,phase", DOMAIN_DDL_CASES)
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_migration_individual_domain_ddl(tmp_path, version, phase, failure):
    path, backup = tmp_path / "p.db", tmp_path / "backup.db"
    synthetic(path, version)
    before = frozen(path)
    if failure == "exit":
        script = """import os,sys
from ontolearn_engine.storage import Store
def hook(p):
    if p==sys.argv[3]: os._exit(79)
Store(sys.argv[1],hook,target_format=3,backup_path=sys.argv[2])
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), str(backup), phase],
            capture_output=True,
            timeout=15,
        )
        assert result.returncode == 79, result.stderr.decode()
    else:
        error = {"exception": RuntimeError, "cancel": KeyboardInterrupt, "disk": OSError}[failure]

        def hook(p):
            if p == phase:
                raise error("injected")

        with pytest.raises(error):
            Store(path, hook, target_format=3, backup_path=backup)
    assert frozen(path) == before and frozen(backup) == before
    # No partial2/3 or lost immutable history, including real process death.
    assert frozen(path)["format"] == version
    lease = format3.acquire_lease(path)
    lease.close()
