"""Complete query payload atomicity/authentication and explicit old catalog compatibility."""

import json
import sqlite3
from copy import deepcopy

import pytest
from ontolearn_engine.job_store import (
    JOB3_HASH,
    QUERY_PAYLOAD_SCHEMA,
    JobFault,
    JobStore,
    _job_object_name,
)
from ontolearn_engine.resources import CONTRACT, LIMITS, semantic_identity
from ontolearn_engine.storage import canonical, digest
from test_query_asserted_jobs import (
    prepare_database,
    read_complete,
    run_query,
    uid,
)


@pytest.fixture
def real_bundle(tmp_path):
    database, project, _, params = prepare_database(tmp_path)
    terminal = run_query(database, project, params)
    metadata, payload, rows = read_complete(database, project, terminal)
    return database, project, params, terminal, metadata, {"payload": payload, "rows": rows}


def accepted(store, params):
    job = store.create_job(
        params["projectId"],
        uid(),
        "query.execute",
        params["input"],
        None,
        semantic_identity(),
        LIMITS,
    )
    store.start_job(job["jobId"])
    return job


@pytest.mark.parametrize(
    "phase",
    ["query_rows_published", "query_payload_published", "mid_job_terminal", "before_commit"],
)
def test_payload_rows_and_terminal_rollback_together(real_bundle, phase):
    database, project, params, _, _, output = real_bundle
    store = JobStore(database, contract=CONTRACT)
    try:
        job = accepted(store, params)
        before = list(store._db.iterdump())

        def hook(value):
            if value == phase:
                raise RuntimeError("injected query publication boundary")

        with pytest.raises(RuntimeError, match="injected query"):
            store.finish_query_job(job["jobId"], output, hook=hook)
        assert list(store._db.iterdump()) == before
        assert not store._db.in_transaction
        assert store.get_job(project, job["jobId"])["state"] == "running"
        finished = store.finish_query_job(job["jobId"], output)
        assert finished["state"] == "succeeded"
        assert (
            store.semantic_result(project, finished["resultRef"]["resultId"])[1]
            == output["payload"]
        )
    finally:
        store.close()


def test_after_commit_delivery_failure_keeps_durable_success(real_bundle):
    database, project, params, _, _, output = real_bundle
    store = JobStore(database, contract=CONTRACT)
    try:
        job = accepted(store, params)

        def hook(phase):
            if phase == "after_commit":
                raise RuntimeError("delivery failed after commit")

        with pytest.raises(RuntimeError, match="delivery failed"):
            store.finish_query_job(job["jobId"], output, hook=hook)
        final = store.get_job(project, job["jobId"])
        assert final["state"] == "succeeded"
        assert store.finish_query_job(job["jobId"], output) == final
        assert store.cancel_job(project, job["jobId"])["disposition"] == "alreadyTerminal"
    finally:
        store.close()
    reopened = JobStore(database, contract=CONTRACT)
    try:
        assert (
            reopened.semantic_result(project, final["resultRef"]["resultId"])[1]
            == output["payload"]
        )
    finally:
        reopened.close()


@pytest.mark.parametrize(
    "field,value",
    [
        ("kind", "reasoning"),
        ("inputSnapshotId", "0" * 64),
        ("inputProjectRevision", 99),
        ("definitionId", "other"),
        ("scope", "asserted+derived"),
        ("queryText", "ASK {}"),
        ("executionSemanticsVersion", "wrong"),
        ("inputSelection", "historical"),
        ("selectedResultIds", ["aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"]),
    ],
)
def test_publication_rejects_complete_binding_mismatch_without_writes(real_bundle, field, value):
    database, _, params, _, _, output = real_bundle
    store = JobStore(database, contract=CONTRACT)
    try:
        job = accepted(store, params)
        changed = deepcopy(output)
        changed["payload"][field] = value
        before = list(store._db.iterdump())
        with pytest.raises(JobFault, match="INVALID_STATE"):
            store.finish_query_job(job["jobId"], changed)
        assert list(store._db.iterdump()) == before
    finally:
        store.close()


def test_rows_only_provenance_and_projection_cannot_bypass_complete_publication(real_bundle):
    database, _, params, _, _, output = real_bundle
    store = JobStore(database, contract=CONTRACT)
    try:
        job = accepted(store, params)
        before = list(store._db.iterdump())
        with pytest.raises(JobFault, match="INVALID_STATE"):
            store.finish_read_job(job["jobId"], output["rows"], kind="query")
        changed = deepcopy(output)
        changed["payload"]["provenance"]["factViewSha256"] = "0" * 64
        with pytest.raises(JobFault, match="INVALID_STATE"):
            store.finish_query_job(job["jobId"], changed)
        changed = deepcopy(output)
        changed["rows"][-1]["cells"][1] = "different"
        with pytest.raises(JobFault, match="INVALID_STATE"):
            store.finish_query_job(job["jobId"], changed)
        assert list(store._db.iterdump()) == before
    finally:
        store.close()


@pytest.mark.parametrize(
    "column,content", [("payload", "{}"), ("payload_hash", "0" * 64), ("rows_hash", "0" * 64)]
)
def test_reopened_internal_reader_authenticates_stored_bytes(real_bundle, column, content):
    database, project, _, terminal, _, _ = real_bundle
    result_id = terminal["resultRef"]["resultId"]
    con = sqlite3.connect(database)
    try:
        trigger = con.execute(
            "SELECT sql FROM sqlite_master WHERE name='immutable_query_payloads_UPDATE'"
        ).fetchone()[0]
        con.execute("DROP TRIGGER immutable_query_payloads_UPDATE")
        con.execute(f"UPDATE query_payloads SET {column}=? WHERE result=?", (content, result_id))
        con.execute(trigger)
        con.commit()
    finally:
        con.close()
    store = JobStore(database, contract=CONTRACT)
    try:
        before = list(store._db.iterdump())
        with pytest.raises(JobFault, match="INVALID_STATE"):
            store.semantic_result(project, result_id)
        assert list(store._db.iterdump()) == before
    finally:
        store.close()


def test_eviction_is_explicit_and_clears_both_cached_payloads(real_bundle):
    database, project, _, terminal, _, _ = real_bundle
    identity = terminal["resultRef"]["resultId"]
    store = JobStore(database, contract=CONTRACT)
    try:
        assert identity not in store.collect_cache()  # Current pointer remains authoritative.
        status = next(
            r
            for r in store.state("query-project")["facts"]
            if r["subject"] == "urn:A01" and r["predicate"] == "urn:status"
        )
        store.commit("query-project", 1, uid(), uid(), edits={status["id"]: '"Closed"'})
        assert identity in store.collect_cache()
        assert store.result_get(project, identity)["payloadStatus"] == "evicted"
        assert (
            store._db.execute(
                "SELECT payload FROM query_payloads WHERE result=?", (identity,)
            ).fetchone()[0]
            is None
        )
        with pytest.raises(JobFault, match="PAYLOAD_EVICTED"):
            store.semantic_result(project, identity)
    finally:
        store.close()
    store = JobStore(database, contract=CONTRACT)
    try:
        with pytest.raises(JobFault, match="PAYLOAD_EVICTED"):
            store.semantic_result(project, identity)
    finally:
        store.close()


def remove_extension(connection):
    for sql in QUERY_PAYLOAD_SCHEMA:
        name = _job_object_name(sql)
        if sql.startswith("CREATE TRIGGER"):
            connection.execute("DROP TRIGGER " + name)
    for sql in reversed(QUERY_PAYLOAD_SCHEMA):
        if sql.startswith("CREATE TABLE"):
            connection.execute("DROP TABLE " + _job_object_name(sql))


@pytest.mark.parametrize("version", [2, 3])
def test_old_queryless_catalog_migration_rollback_and_reopen(tmp_path, version):
    from test_job_store import create

    path = tmp_path / "legacy.sqlite"
    store = JobStore(path, contract=CONTRACT, target_format=version)
    store.create_project("legacy")
    store.project = store.public_project("legacy")
    job = create(store)
    store.start_job(job["jobId"])
    final = store.finish_read_job(job["jobId"], [])
    original = store.get_job(store.project, job["jobId"])
    public = store.project
    marker = list(store._db.execute("SELECT * FROM job_format")) if version == 3 else None
    assert marker is None or marker[0][2] == JOB3_HASH
    remove_extension(store._db)
    before = list(store._db.iterdump())
    store.close()

    def hook(phase):
        if phase == "query_payload_ddl:query_payloads":
            raise RuntimeError("extension migration failure")

    with pytest.raises(RuntimeError, match="extension migration failure"):
        JobStore(path, contract=CONTRACT, target_format=version, job_migration_hook=hook)
    con = sqlite3.connect(path)
    try:
        assert list(con.iterdump()) == before
    finally:
        con.close()
    store = JobStore(path, contract=CONTRACT, target_format=version)
    try:
        assert store.get_job(public, job["jobId"]) == original == final
        assert len(store.result_get(public, final["resultRef"]["resultId"])) == 17
        assert (
            store._db.execute("SELECT source_format FROM query_payload_format").fetchone()[0]
            == version
        )
        if marker is not None:
            assert [tuple(r) for r in store._db.execute("SELECT * FROM job_format")] == [
                tuple(r) for r in marker
            ]
    finally:
        store.close()


def test_legacy_derived_dto_domain_is_retained_without_new_execution(real_bundle):
    # A stored legacy DTO fixture, not an execution/semantic-provenance claim.
    database, project, _, terminal, _, _ = real_bundle
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    try:
        saved = con.execute("SELECT * FROM jobs WHERE id=?", (terminal["jobId"],)).fetchone()
        context, dto = json.loads(saved["context"]), json.loads(saved["dto"])
        context.pop("queryRequest")
        context["input"]["scope"] = dto["input"]["scope"] = dto["scope"] = "asserted+derived"
        fingerprint = digest(context)
        result = con.execute(
            "SELECT * FROM job_results WHERE job=?", (terminal["jobId"],)
        ).fetchone()
        projection = json.loads(result["projection"])
        projection["scope"] = "asserted+derived"
        triggers = [
            tuple(r)
            for r in con.execute(
                "SELECT name,sql FROM sqlite_master WHERE name IN "
                "('immutable_job_context','immutable_operation_claims_UPDATE','immutable_job_results_UPDATE')"
            )
        ]
        for name, _ in triggers:
            con.execute("DROP TRIGGER " + name)
        con.execute(
            "UPDATE jobs SET dto=?,context=?,fingerprint=? WHERE id=?",
            (canonical(dto), canonical(context), fingerprint, terminal["jobId"]),
        )
        con.execute(
            "UPDATE operation_claims SET fingerprint=? WHERE job=?",
            (fingerprint, terminal["jobId"]),
        )
        con.execute(
            "UPDATE job_results SET projection=? WHERE job=?",
            (canonical(projection), terminal["jobId"]),
        )
        for _, sql in triggers:
            con.execute(sql)
        remove_extension(con)
        con.commit()
    finally:
        con.close()
    store = JobStore(database, contract=CONTRACT)
    try:
        old = store.get_job(project, terminal["jobId"])
        metadata = store.result_get(project, terminal["resultRef"]["resultId"])
        assert old["scope"] == metadata["scope"] == "asserted+derived"
        assert CONTRACT.validate("job", old) and CONTRACT.validate("result", metadata)
        with pytest.raises(JobFault, match="UNSUPPORTED_CAPABILITY"):
            store.semantic_result(project, metadata["resultId"])
        assert store._db.execute("SELECT job FROM query_legacy_jobs").fetchone()[0] == old["jobId"]
    finally:
        store.close()


def test_partial_catalog_is_rejected_without_repair(tmp_path):
    path = tmp_path / "partial.sqlite"
    store = JobStore(path, contract=CONTRACT)
    remove_extension(store._db)
    store._db.execute("CREATE TABLE query_payloads(unrelated TEXT)")
    before = list(store._db.iterdump())
    store.close()
    with pytest.raises(JobFault, match="INVALID_STATE"):
        JobStore(path, contract=CONTRACT)
    con = sqlite3.connect(path)
    try:
        assert list(con.iterdump()) == before
    finally:
        con.close()


@pytest.mark.parametrize("case", ["producer", "parameters", "manifests", "rows"])
def test_internal_reader_rejects_producer_and_metadata_projection_mismatch(real_bundle, case):
    database, project, params, terminal, _, output = real_bundle
    store = JobStore(database, contract=CONTRACT)
    try:
        identity = terminal["resultRef"]["resultId"]
        if case == "rows":
            changed = deepcopy(output["rows"])
            changed[-1]["cells"][1] = "different"
            store._db.execute(
                "UPDATE results SET payload=? WHERE id=?", (canonical(changed), identity)
            )
        else:
            trigger = store._db.execute(
                "SELECT sql FROM sqlite_master WHERE name='immutable_job_results_UPDATE'"
            ).fetchone()[0]
            store._db.execute("DROP TRIGGER immutable_job_results_UPDATE")
            if case == "producer":
                other = accepted(store, params)
                store._db.execute(
                    "UPDATE job_results SET job=? WHERE id=?", (other["jobId"], identity)
                )
            elif case == "parameters":
                projection = {"definitionId": "Q1", "scope": "asserted", "parametersHash": "0" * 64}
                store._db.execute(
                    "UPDATE job_results SET projection=? WHERE id=?",
                    (canonical(projection), identity),
                )
            else:
                store._db.execute(
                    "UPDATE job_results SET manifests=? WHERE id=?",
                    (canonical({"query": []}), identity),
                )
            store._db.execute(trigger)
        before = list(store._db.iterdump())
        with pytest.raises(JobFault, match="INVALID_STATE"):
            store.semantic_result(project, identity)
        assert list(store._db.iterdump()) == before
    finally:
        store.close()


def test_runtime_registry_annotations_preserve_existing_contract_validation():
    entry = CONTRACT.REGISTRY["capabilities"]["query.execute"]
    assert entry["implementation"] == "runtime-asserted-only"
    assert entry["dataScopes"] == ["asserted", "asserted+derived"]
    assert entry["runtimeDataScopes"] == ["asserted"]
    assert entry["plannedDataScopes"] == ["asserted+derived"]
    # The existing registry consumer resolves canonical schema references; these
    # status annotations do not add request fields or relax a strict wire schema.
    for capability in CONTRACT.REGISTRY["capabilities"].values():
        for key in ("paramsSchema", "resultSchema"):
            assert capability[key].startswith("#/$defs/")
            assert capability[key].split("/")[-1] in CONTRACT.DOCUMENT["$defs"]
    assert "query.execute" not in CONTRACT.REGISTRY["v2Runtime"]
    assert "semantic.start" not in CONTRACT.REGISTRY["v2Runtime"]
