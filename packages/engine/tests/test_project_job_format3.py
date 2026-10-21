"""Synthetic two-layer migration; no public3 handshake or non-Job activation."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from ontolearn_engine.job_store import (
    JOB3_CATALOG,
    JOB3_SCHEMA,
    JobFault,
    JobStore,
    _job_object_name,
)
from ontolearn_engine.project.format3 import Format3Fault, logical_hash
from ontolearn_engine.storage import Store, canonical, digest
from test_job_store import CONTRACT, create, uid

NEW_PHASES = (
    ["job3_before"]
    + ["job3_ddl:" + _job_object_name(sql) for sql in JOB3_SCHEMA + JOB3_CATALOG]
    + ["job3_identity", "job3_catalog", "job3_validated", "job3_before_commit", "job3_after_commit"]
)
OLD_PHASES = (
    [
        "job3_before",
        "job3_claims_renamed",
        "job3_claims_created",
        "job3_claims_copied",
        "job3_claims_dropped",
        "job3_claims_trigger:immutable_operation_claims_UPDATE",
        "job3_claims_trigger:immutable_operation_claims_DELETE",
        "job3_claims_swapped",
    ]
    + ["job3_ddl:" + _job_object_name(sql) for sql in JOB3_CATALOG]
    + ["job3_identity", "job3_catalog", "job3_validated", "job3_before_commit", "job3_after_commit"]
)


def frozen(path):
    con = sqlite3.connect(path)
    result = logical_hash(con)
    con.close()
    return result


def source(path, kind):
    if kind == "new":
        store = Store(path, target_format=3)
        store.create_project("p")
        store.close()
        return None
    store = JobStore(path, contract=CONTRACT)
    store.create_project("p")
    store.project = store.public_project("p")
    read = create(store)
    store.start_job(read["jobId"])
    store.finish_read_job(read["jobId"], [])
    atomic = create(
        store,
        "test.atomic",
        plan={"definitions": [{"layer": "rule", "id": "r", "value": {"enabled": True}}]},
    )
    store.start_job(atomic["jobId"])
    store.commit_job(atomic["jobId"])
    queued = create(store)
    result = {
        "public": store.project,
        "read": read,
        "atomic": atomic,
        "queued": queued,
        "claims": [
            tuple(r)
            for r in store._db.execute(
                "SELECT operation,project,job,fingerprint FROM operation_claims ORDER BY operation"
            )
        ],
        "snapshots": [tuple(r) for r in store._db.execute("SELECT * FROM snapshots ORDER BY id")],
        "jobs": [tuple(r) for r in store._db.execute("SELECT * FROM jobs ORDER BY id")],
    }
    store.close()
    # Two stages deliberately have separate atomic boundaries. Failure of Job
    # migration must preserve this valid Store3 plus the entire old Job layer.
    Store(path, target_format=3, backup_path=path.with_suffix(".backup")).close()
    return result


@pytest.mark.parametrize(
    "kind,phase",
    [(k, p) for k, phases in (("new", NEW_PHASES), ("v2", OLD_PHASES)) for p in phases],
)
@pytest.mark.parametrize("failure", ["exception", "cancel", "disk", "exit"])
def test_job3_second_layer_atomic(tmp_path, kind, phase, failure):
    path = tmp_path / "p.db"
    source(path, kind)
    before = frozen(path)
    if failure == "exit":
        script = """
import os,sys
from ontolearn_engine.job_store import JobStore
from test_job_store import CONTRACT
def hook(p):
    if p==sys.argv[2]: os._exit(79)
JobStore(sys.argv[1],contract=CONTRACT,target_format=3,job_migration_hook=hook)
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), phase],
            env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)},
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
            JobStore(path, contract=CONTRACT, target_format=3, job_migration_hook=hook)
    if phase != "job3_after_commit":
        assert frozen(path) == before
    # Construction failure always releases the same one OS lease; reopening
    # either resumes the old complete layer or reads the complete new one.
    store = JobStore(path, contract=CONTRACT, target_format=3)
    assert store.actual_format == 3
    store._validate_job3()
    assert store._project(store.public_project("p")) == "p"
    store.close()


def test_old_claim_identity_jobs_and_retry_preserved(tmp_path):
    path = tmp_path / "p.db"
    old = source(path, "v2")
    store = JobStore(path, contract=CONTRACT, target_format=3)
    assert store.public_project("p") == old["public"]
    assert store.project_get(old["public"])["formatVersion"] == 3
    assert [
        tuple(r)
        for r in store._db.execute(
            "SELECT operation,project,job,fingerprint FROM operation_claims ORDER BY operation"
        )
    ] == old["claims"]
    assert [tuple(r) for r in store._db.execute("SELECT * FROM jobs ORDER BY id")] == old["jobs"]
    assert [tuple(r) for r in store._db.execute("SELECT * FROM snapshots ORDER BY id")] == old[
        "snapshots"
    ]
    for job in (old["read"], old["atomic"], old["queued"]):
        current = store.get_job(old["public"], job["jobId"])
        assert (
            store.create_job(
                old["public"],
                job["operationId"],
                job["capability"],
                job["input"],
                job["confirmationRef"],
                job["implementation"],
                job["limits"],
            )
            == current
        )
    assert all(
        tuple(r) == ("job", None)
        for r in store._db.execute("SELECT kind,context FROM operation_claims")
    )
    with pytest.raises(sqlite3.IntegrityError):
        store._db.execute("UPDATE operation_claims SET fingerprint='changed'")
    saved = frozen(path)
    store.close()
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    reopened._db.execute("PRAGMA query_only=ON")
    reopened._validate_job3()
    assert frozen(path) == saved
    reopened.close()


@pytest.mark.parametrize(
    "mutation",
    [
        "DROP TABLE job_blobs",
        "DROP TRIGGER immutable_operation_claims_UPDATE",
        "DROP TRIGGER immutable_job_context",
        "UPDATE job_format SET schema_hash='bad'",
    ],
)
def test_job3_corruption_never_repairs(tmp_path, mutation):
    path = tmp_path / "p.db"
    source(path, "v2")
    store = JobStore(path, contract=CONTRACT, target_format=3)
    store.close()
    con = sqlite3.connect(path)
    if mutation.startswith("UPDATE job_format"):
        con.execute("DROP TRIGGER immutable_job_format_UPDATE")
    con.execute(mutation)
    con.commit()
    con.close()
    before = frozen(path)
    with pytest.raises(Format3Fault):
        JobStore(path, contract=CONTRACT, target_format=3)
    assert frozen(path) == before


def test_partial_old_layer_rejected_without_if_not_exists_repair(tmp_path):
    path = tmp_path / "p.db"
    source(path, "v2")
    con = sqlite3.connect(path)
    con.execute("DROP TRIGGER immutable_operation_claims_DELETE")
    con.close()
    before = frozen(path)
    with pytest.raises(Format3Fault):
        JobStore(path, contract=CONTRACT, target_format=3)
    assert frozen(path) == before
    con = sqlite3.connect(path)
    assert con.execute("PRAGMA user_version").fetchone()[0] == 3
    assert con.execute("SELECT 1 FROM sqlite_master WHERE name='job_format'").fetchone() is None
    con.close()


def test_exactly_one_lease_and_creation_identity_atomic(tmp_path):
    path = tmp_path / "p.db"
    old = JobStore(path, contract=CONTRACT)
    old.create_project("p")
    with pytest.raises(Format3Fault) as error:
        JobStore(path, contract=CONTRACT, target_format=3, backup_path=tmp_path / "backup.db")
    assert error.value.category == "leaseBusy" and not (tmp_path / "backup.db").exists()
    old.close()
    store = JobStore(path, contract=CONTRACT, target_format=3, backup_path=tmp_path / "backup.db")
    assert store._lease is None and store._format3_lease is not None
    store.create_project("new-project")
    public = store.public_project("new-project")
    assert store._project(public) == "new-project"
    with pytest.raises(JobFault, match="STORAGE_BUSY"):
        JobStore(path, contract=CONTRACT)
    store.close()
    with pytest.raises(ValueError, match="Unsupported future project format"):
        JobStore(path, contract=CONTRACT)
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    assert reopened.public_project("new-project") == public
    reopened.close()


def test_new_jobs_and_application_kind_collision_are_distinct(tmp_path):
    store = JobStore(tmp_path / "p.db", contract=CONTRACT, target_format=3)
    store.create_project("p")
    store.project = store.public_project("p")
    job = create(store)
    assert (
        store._db.execute(
            "SELECT kind FROM operation_claims WHERE operation=?", (job["operationId"],)
        ).fetchone()[0]
        == "job"
    )
    operation = uid()
    context = {"synthetic": "not-a-published-application"}
    store._db.execute(
        "INSERT INTO operation_claims VALUES(?,?,NULL,?,'application',?)",
        (operation, store.project, digest(context), canonical(context)),
    )
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        create(store, operation=operation)
    # A kind column is not proof of a complete application adapter/receipt.
    with pytest.raises(Format3Fault):
        store._validate_job3()
    store.close()


@pytest.mark.parametrize("target", [True, 2.0, 4, "3", None])
def test_job_target_validation_precedes_side_effects(tmp_path, target):
    with pytest.raises(ValueError):
        JobStore(tmp_path / "absent.db", contract=CONTRACT, target_format=target)
    assert list(tmp_path.iterdir()) == []


def test_v2_coordinator_cannot_announce_private3_session(tmp_path):
    from ontolearn_engine.coordinator import Coordinator, ServiceFault

    store = JobStore(tmp_path / "p.db", contract=CONTRACT, target_format=3)
    with pytest.raises(ServiceFault) as error:
        Coordinator(store)
    assert error.value.error["code"] == "INVALID_STATE"
    store.close()
