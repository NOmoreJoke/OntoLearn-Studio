"""Schema1 upgrade, actual crash boundaries, and selected-file identity checks."""

import json
import os
import sqlite3
import subprocess
import sys
from uuid import uuid4

import pytest
from ontolearn_engine.__main__ import startup_arguments
from ontolearn_engine.coordinator import _JOB_READY, Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import format3, management_schema
from ontolearn_engine.project.format3 import Format3Fault, logical_hash
from ontolearn_engine.resources import CONTRACT
from test_mainline_dispatch import exchange


def uid():
    return str(uuid4())


def history_rows(db):
    return {
        table: sorted(tuple(row) for row in db.execute(f"SELECT * FROM {table}"))
        for table in (
            "snapshots",
            "app_checkpoints",
            "app_operations",
            "app_receipts",
            "commits",
            "commit_evidence",
            "app_origins",
        )
    }


def schema1_fixture(path):
    """Construct the unchanged v1 catalog, then independently validate it.

    The separate local acceptance also opens genuine pinned pre-B1 source.
    This deterministic fixture has no Git/network dependency in clean CI.
    """
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.create_project("legacy")
    public = store.public_project("legacy")
    store.apply_application(
        public,
        uid(),
        {
            "type": "metadata",
            "expectedVersion": 0,
            "patch": {"name": "existing", "mode": "assisted"},
        },
        actor=uid(),
        permission="write",
    )
    old = json.loads(store._db.execute("SELECT payload FROM schema_migrations").fetchone()[0])[
        "oldCatalog"
    ]
    with store._transaction():
        for name, _ in management_schema.TRIGGERS:
            store._db.execute(f"DROP TRIGGER {name}")
        for table in ("project_lifecycle", "management_receipts", "schema_migrations"):
            store._db.execute(f"DROP TABLE {table}")
        for action in ("UPDATE", "DELETE"):
            store._db.execute(f"DROP TRIGGER immutable_app_format_{action}")
        store._db.execute("DROP TABLE app_format")
        store._db.execute(format3.TABLES[0][1])
        store._db.execute(
            "INSERT INTO app_format VALUES(?,?,?,?,?,?)",
            tuple(
                old[key]
                for key in (
                    "singleton",
                    "schema_version",
                    "schema_hash",
                    "migration_id",
                    "source_format",
                    "backup_hash",
                )
            ),
        )
        for name, sql in format3.TRIGGERS:
            if name.startswith("immutable_app_format_"):
                store._db.execute(sql)
        format3._validate(store, catalog_version=1)
    store.close()
    return old


def frozen(path):
    with sqlite3.connect(path) as db:
        return logical_hash(db)


def test_schema1_requires_real_backup_preserves_old_evidence(tmp_path):
    path = tmp_path / "old.sqlite"
    old = schema1_fixture(path)
    before = frozen(path)
    with sqlite3.connect(path) as db:
        history = history_rows(db)
    with pytest.raises(Format3Fault) as error:
        JobStore(path, contract=CONTRACT, target_format=3)
    assert error.value.category == "backupRequired"
    assert frozen(path) == before
    backup = tmp_path / "backup.sqlite"
    store = JobStore(path, contract=CONTRACT, target_format=3, backup_path=backup)
    assert frozen(backup) == before
    current = dict(store._db.execute("SELECT * FROM app_format").fetchone())
    assert current == {**old, "schema_version": 2, "schema_hash": management_schema.schema_hash()}
    proof = json.loads(store._db.execute("SELECT payload FROM schema_migrations").fetchone()[0])
    assert proof["oldCatalog"] == old and proof["sourceLogicalHash"] == before
    assert history_rows(store._db) == history
    format3.validate(store)
    store._validate_job3()
    # The prior strict catalog gate rejects the extension before any jobs are
    # migrated. Real old-source process acceptance is recorded separately.
    with pytest.raises(Format3Fault):
        format3._validate(store, catalog_version=1)
    store.close()
    extra = tmp_path / "unnecessary.sqlite"
    store = JobStore(path, contract=CONTRACT, target_format=3, backup_path=extra)
    store.close()
    assert not extra.exists()


PHASES = [
    "before_backup",
    "after_backup",
    "before",
    "management_schema_ddl:management_receipts",
    "management_schema_ddl:project_lifecycle",
    "management_schema_ddl:schema_migrations",
    "management_schema_receipt",
    "management_schema_validated",
    "before_commit",
    "after_commit",
]


@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("crash", [False, True])
def test_upgrade_crash_rollback_is_all_or_nothing(tmp_path, phase, crash):
    path = tmp_path / "old.sqlite"
    schema1_fixture(path)
    before = frozen(path)
    backup = tmp_path / "backup.sqlite"
    if crash:
        script = """
import os,sys
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
def hook(phase):
 if phase == sys.argv[3]: os._exit(71)
JobStore(sys.argv[1],contract=CONTRACT,target_format=3,backup_path=sys.argv[2],migration_hook=hook)
"""
        completed = subprocess.run(
            [sys.executable, "-c", script, str(path), str(backup), phase],
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 71, completed.stderr
    else:

        def hook(current):
            if current == phase:
                raise RuntimeError("injected migration failure")

        with pytest.raises(RuntimeError):
            JobStore(
                path, contract=CONTRACT, target_format=3, backup_path=backup, migration_hook=hook
            )
    with sqlite3.connect(path) as db:
        version = db.execute("SELECT schema_version FROM app_format").fetchone()[0]
    if phase == "after_commit":
        assert version == 2
    else:
        assert version == 1 and frozen(path) == before
    # A successful reopen cannot need the failed process or a repair branch.
    store = JobStore(
        path, contract=CONTRACT, target_format=3, backup_path=tmp_path / "retry-backup.sqlite"
    )
    format3.validate(store)
    store.close()


def test_upgrade_source_change_after_backup_rolls_back_without_overwrite(tmp_path):
    path = tmp_path / "old.sqlite"
    schema1_fixture(path)
    backup = tmp_path / "backup.sqlite"

    def hook(phase):
        if phase == "after_backup":
            with sqlite3.connect(path) as other:
                other.execute("CREATE TABLE concurrent_change(value TEXT)")

    with pytest.raises(Format3Fault) as error:
        JobStore(path, contract=CONTRACT, target_format=3, backup_path=backup, migration_hook=hook)
    assert error.value.category == "sourceChanged"
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT schema_version FROM app_format").fetchone()[0] == 1
        assert db.execute(
            "SELECT name FROM sqlite_master WHERE name='concurrent_change'"
        ).fetchone()


def file_identity(path):
    observed = path.lstat()
    return f"{observed.st_dev}:{observed.st_ino}"


def test_selected_file_identity_and_no_unnecessary_backup(tmp_path):
    path = (tmp_path / "selected.sqlite").resolve()
    path.touch(exist_ok=False)
    identity = file_identity(path)
    args = ["--t01-internal-profile=business3", f"--b1-library-file-identity={identity}"]
    assert startup_arguments(args, include_identity=True) == ("business3", None, identity, False)
    backup = tmp_path / "unused.sqlite"
    store = JobStore(
        path, contract=CONTRACT, target_format=3, file_identity=identity, backup_path=backup
    )
    assert store.actual_format == 3 and not backup.exists()
    store.close()
    replacement = tmp_path / "replacement.sqlite"
    replacement.touch()
    os.replace(replacement, path)
    before = path.read_bytes()
    with pytest.raises(Format3Fault):
        JobStore(path, contract=CONTRACT, target_format=3, file_identity=identity)
    assert path.read_bytes() == before


def test_selected_identity_rejects_aliases_and_rechecks_connection(tmp_path, monkeypatch):
    path = (tmp_path / "selected.sqlite").resolve()
    path.touch()
    identity = file_identity(path)
    alias = tmp_path / "hardlink.sqlite"
    try:
        os.link(path, alias)
    except OSError:
        pytest.skip("hard links unavailable on this filesystem")
    with pytest.raises(Format3Fault):
        JobStore(path, contract=CONTRACT, target_format=3, file_identity=identity)
    alias.unlink()
    link = tmp_path / "symlink.sqlite"
    try:
        link.symlink_to(path)
    except OSError:
        pass
    else:
        with pytest.raises(Format3Fault):
            JobStore(link, contract=CONTRACT, target_format=3, file_identity=identity)
    connect = sqlite3.connect

    def substituted(*args, **kwargs):
        db = connect(*args, **kwargs)
        replacement = tmp_path / "replacement.sqlite"
        replacement.touch()
        try:
            os.replace(replacement, path)
        except PermissionError:
            db.close()
            pytest.skip("platform prevents replacing an open database")
        return db

    monkeypatch.setattr(sqlite3, "connect", substituted)
    with pytest.raises(Format3Fault):
        JobStore(path, contract=CONTRACT, target_format=3, file_identity=identity)
    assert path.read_bytes() == b""


def test_open_existing_flag_never_initializes_empty_or_truncated_library(tmp_path):
    path = (tmp_path / "existing.sqlite").resolve()
    path.touch()
    identity = file_identity(path)
    arguments = [
        "--t01-internal-profile=business3",
        f"--b1-library-file-identity={identity}",
        "--b1-library-require-existing=1",
    ]
    assert startup_arguments(arguments, include_identity=True) == (
        "business3",
        None,
        identity,
        True,
    )
    with pytest.raises(Format3Fault):
        JobStore(
            path,
            contract=CONTRACT,
            target_format=3,
            file_identity=identity,
            require_existing_format=True,
        )
    assert path.read_bytes() == b""

    store = JobStore(path, contract=CONTRACT, target_format=3, file_identity=identity)
    store.close()
    opened = JobStore(
        path,
        contract=CONTRACT,
        target_format=3,
        file_identity=identity,
        require_existing_format=True,
    )
    opened.close()
    # In-place truncation preserves dev/ino; the open-existing contract still
    # rejects it before any new catalog or backup can be written.
    path.write_bytes(b"")
    assert file_identity(path) == identity
    with pytest.raises(Format3Fault):
        JobStore(
            path,
            contract=CONTRACT,
            target_format=3,
            file_identity=identity,
            require_existing_format=True,
        )
    assert path.read_bytes() == b""


@pytest.mark.parametrize("admission", ["read", "write", "rpc"])
def test_selected_library_changed_path_fences_new_admission(tmp_path, admission):
    path = (tmp_path / "selected.sqlite").resolve()
    path.touch()
    identity = file_identity(path)
    store = JobStore(path, contract=CONTRACT, target_format=3, file_identity=identity)
    actor = Coordinator(store, profile="business3", _ready=_JOB_READY)
    assert exchange(actor, "hello", {"supportedVersions": [3], "clientId": uid()})["ok"]
    original = tmp_path / "original.sqlite"
    try:
        try:
            path.rename(original)
        except PermissionError:
            pytest.skip("platform lifetime guard prevents replacing selected library")
        path.touch()
        replacement = path.read_bytes()
        if admission == "rpc":
            rejected = exchange(actor, "project.catalog", {"pageSize": 10, "cursor": None})
            assert not rejected["ok"], rejected
            assert rejected["error"]["code"] == "STORAGE_FAILURE"
            assert exchange(actor, "health", {})["ok"]
            assert exchange(actor, "session.ping", {"nonce": uid()})["ok"]
        else:
            scope = store._read if admission == "read" else store._transaction
            with pytest.raises(Format3Fault), scope():
                pytest.fail("changed library was admitted")
        assert path.read_bytes() == replacement
        path.unlink()
        original.rename(path)
        # Restoring the name does not revive a failed binding.
        with pytest.raises(Format3Fault), store._read():
            pytest.fail("failed binding was revived")
    finally:
        actor.mainline.close()
        store.close()
