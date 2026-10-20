"""Real S2 SQLite evidence, faults, fencing and immutable pagination; no GUI."""

import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.storage import digest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "storage_contract", ROOT / "packages/contracts/python/contract_v2.py"
)
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
IMPL = {
    "engineVersion": "0.1.0",
    "executionSemanticsVersion": "test-v1",
    "dependencyLockHash": "a" * 64,
}
LIMITS = {
    "startupMs": 10000,
    "handshakeMs": 5000,
    "requestMs": 5000,
    "heartbeatMs": 10000,
    "cancelGraceMs": 5000,
    "totalMs": 120000,
    "maxFrameBytes": 262144,
    "maxQueuedJobs": 32,
    "maxConcurrentJobs": 2,
    "maxPageItems": 100,
    "maxPageBytes": 131072,
    "maxWorkerMemoryBytes": 536870912,
}


def uid():
    return str(uuid4())


def row(i, cells=None):
    return {"rowId": uid(), "ordinal": i, "cells": cells if cells is not None else [i]}


@pytest.fixture
def store(tmp_path):
    s = JobStore(tmp_path / "test.sqlite", contract=CONTRACT)
    s.create_project("legacy-project")
    s.project = s.public_project("legacy-project")
    yield s
    s.close()


def create(s, capability="test.read", parameters=None, plan=None, operation=None, project=None):
    project = project or s.project
    snap = s.project_get(project)
    input_ = {
        "inputSnapshotId": snap["inputSnapshotId"],
        "scope": "scenario" if capability == "test.rounds" else "asserted",
        "definitionId": "probe",
        "parametersHash": s.put_blob(project, parameters if parameters is not None else {}),
        "derivedResultIds": [],
        "preparedPlanRef": None,
    }
    confirm = None
    if capability == "test.atomic":
        prepared = s.prepare_plan(
            project, snap["projectRevision"], plan or {}, actor=uid(), permission="write"
        )
        input_["preparedPlanRef"] = prepared["preparedPlanRef"]
        confirm = prepared["confirmationRef"]
    return s.create_job(project, operation or uid(), capability, input_, confirm, IMPL, LIMITS)


def test_input_fingerprint_global_claim_and_mapping(store):
    s = store
    job = create(s, parameters={"workMs": 1})
    assert s.public_project("legacy-project") == s.project
    assert s._project(s.project) == "legacy-project"
    assert CONTRACT.validate("job", job)
    assert (
        s.create_job(
            s.project, job["operationId"], job["capability"], job["input"], None, IMPL, LIMITS
        )
        == job
    )
    for change in [
        {"definitionId": "other"},
        {"parametersHash": s.put_blob(s.project, {"workMs": 2})},
    ]:
        with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
            s.create_job(
                s.project,
                job["operationId"],
                job["capability"],
                {**job["input"], **change},
                None,
                IMPL,
                LIMITS,
            )
    s.create_project("second")
    second = s.public_project("second")
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        create(s, operation=job["operationId"], project=second)
    with pytest.raises(JobFault, match="NOT_FOUND"):
        s.get_job(second, job["jobId"])
    assert s._db.execute("SELECT count(*) FROM operation_claims").fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        s._db.execute("UPDATE jobs SET context='{}' WHERE id=?", (job["jobId"],))


@pytest.mark.parametrize(
    "parameters",
    [
        [],
        {"arbitrary": True},
        {"workMs": True},
        {"workMs": 10001},
        {"maxRounds": 0},
        {"events": ["a", "a"]},
        {"events": [1]},
        {"rows": [{"cells": ["bad"]}]},
        {"allocateBytes": 2147483649},
    ],
)
def test_test_parameter_bounds_have_no_claim(store, parameters):
    with pytest.raises(JobFault, match="INVALID_REQUEST"):
        create(store, parameters=parameters)
    assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0


def test_confirmation_bound_full_plan_and_preview_rollback(store):
    s = store
    plan = {"definitions": [{"layer": "rule", "id": "new", "value": {"enabled": True}}]}
    old = s.state("legacy-project")
    job = create(s, "test.atomic", plan=plan)
    assert s.revision("legacy-project") == 0
    assert s.state("legacy-project") == old
    assert s.marker("legacy-project", job["operationId"]) is None
    for bad in [
        {**job["input"], "preparedPlanRef": "0" * 64},
        {**job["input"], "definitionId": "different"},
    ]:
        with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
            s.create_job(
                s.project,
                job["operationId"],
                "test.atomic",
                bad,
                job["confirmationRef"],
                IMPL,
                LIMITS,
            )
    s.start_job(job["jobId"])
    success = s.commit_job(job["jobId"])
    assert success["state"] == "succeeded"
    assert s.revision("legacy-project") == 1
    marker = s.operation_get(s.project, job["operationId"])
    assert CONTRACT.validate("commitMarker", marker)
    assert marker["planHash"] == digest(s.job_context(job["jobId"])["plan"])
    result = s.result_get(s.project, success["resultRef"]["resultId"])
    assert result["state"] == "historical" and result["kind"] == "receipt"
    assert s.cancel_job(s.project, job["jobId"])["disposition"] == "alreadyTerminal"


PHASES = [
    "before",
    "mid_data",
    "mid_ownership",
    "mid_invalidation",
    "mid_marker",
    "mid_job_terminal",
    "before_commit",
    "after_commit",
]


@pytest.mark.parametrize("mode", ["changeset", "mapping"])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("failure", ["exception", "disk", "cancel", "exit"])
def test_atomic_job_fault_reconcile_matrix(store, mode, phase, failure):
    s = store
    fact = {"subject": "urn:probe", "predicate": "urn:name", "object": '"real"'}
    fact["id"] = digest([fact["subject"], fact["predicate"], fact["object"]])
    plan = (
        {"mapping": {"id": "M1", "rows": [{"row": "1", "facts": [fact]}]}}
        if mode == "mapping"
        else {"manual": [fact]}
    )
    job = create(s, "test.atomic", plan=plan)
    s.start_job(job["jobId"])
    path = s.path
    project = s.project
    s.close()
    if failure == "exit":
        code = """
import importlib.util,os,sys
from ontolearn_engine.job_store import JobStore
spec=importlib.util.spec_from_file_location('c',sys.argv[1])
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
s=JobStore(sys.argv[2],contract=c)
def hook(stage):
 if stage==sys.argv[4]: os._exit(73)
s.commit_job(sys.argv[3],hook)
"""
        process = subprocess.run(
            [
                sys.executable,
                "-c",
                code,
                str(ROOT / "packages/contracts/python/contract_v2.py"),
                str(path),
                job["jobId"],
                phase,
            ],
            capture_output=True,
            timeout=15,
        )
        assert process.returncode == 73, process.stderr
    else:
        s = JobStore(path, contract=CONTRACT)
        exception = {"exception": RuntimeError, "disk": OSError, "cancel": KeyboardInterrupt}[
            failure
        ]

        def hook(stage):
            if stage == phase:
                raise exception("not returned across protocol")

        with pytest.raises(exception):
            s.commit_job(job["jobId"], hook)
        s.close()
    reopened = JobStore(path, contract=CONTRACT)
    reopened.reconcile_jobs()
    saved = reopened.get_job(project, job["jobId"])
    marker = reopened.operation_get(project, job["operationId"])
    if phase == "after_commit":
        assert saved["state"] == "succeeded" and marker is not None
        assert reopened.revision("legacy-project") == 1
        assert reopened.state("legacy-project")["facts"]
    else:
        assert saved["state"] == "failed" and marker is None
        assert reopened.revision("legacy-project") == 0
        assert reopened.state("legacy-project")["facts"] == []
    reopened.close()
    # Fixture owns the closed original; make repeated close harmless here only.
    store.close = lambda: None


def test_lease_fences_old_coordinator_and_recovery_never_replays(store):
    s = store
    job = create(s)
    with pytest.raises(JobFault, match="STORAGE_BUSY"):
        JobStore(s.path, contract=CONTRACT)
    s.start_job(job["jobId"])
    path, project = s.path, s.project
    s.close()
    recovered = JobStore(path, contract=CONTRACT)
    assert recovered.reconcile_jobs()[0]["state"] == "failed"
    assert recovered.get_job(project, job["jobId"])["stateVersion"] == 3
    assert recovered.reconcile_jobs() == []
    recovered.close()
    store.close = lambda: None


def run_rounds(s, count=2, pending=True):
    job = create(
        s,
        "test.rounds",
        parameters={
            "maxRounds": count,
            "events": ["a"] if pending else ["a", "b"],
            "consumePerRound": 0 if pending else 2,
        },
    )
    s.start_job(job["jobId"])
    config = s.job_context(job["jobId"])["runConfig"]
    s.start_job_run(job["jobId"], config)
    for _n in range(count):
        state = {
            "pendingEvents": ["a"] if pending else [],
            "consumedEvents": [] if pending else ["a", "b"],
            "inputEvents": ["a"] if pending else ["a", "b"],
        }
        s.commit_job_round(job["jobId"], state)
    return job, state


@pytest.mark.parametrize("pending", [False, True])
def test_f6_summary_real_rounds_terminal_result_page(store, pending):
    job, state = run_rounds(store, pending=pending)
    saved = store.finish_job_run(
        job["jobId"],
        pending_events=state["pendingEvents"],
        event_consumption=state["consumedEvents"],
    )
    progress = saved["commitProgress"]["committedProgress"]
    assert progress["lastCommittedRound"] == 2
    result = store.result_get(store.project, saved["resultRef"]["resultId"])
    binding = page_binding(result)
    page = store.result_page(binding, 1, None)
    cells = page["rows"][0]["cells"]
    assert cells[:7] == [
        "run.summary.v1",
        progress["runId"],
        2,
        progress["snapshotRef"],
        True,
        pending,
        int(pending),
    ]
    assert page["nextCursor"] is None
    assert store.history(progress["runId"])["terminal"]["status"] == "succeeded"
    assert store.cancel_job(store.project, job["jobId"])["state"] == "succeeded"


def test_last_round_without_final_evidence_is_failed_not_success(store):
    job, _ = run_rounds(store)
    project, path = store.project, store.path
    store.close()
    s = JobStore(path, contract=CONTRACT)
    recovered = s.reconcile_jobs()[0]
    assert recovered["state"] == "failed" and recovered["resultRef"] is None
    assert recovered["commitProgress"]["committedProgress"]["lastCommittedRound"] == 2
    assert s.get_job(project, job["jobId"]) == recovered
    assert s._db.execute("SELECT count(*) FROM results").fetchone()[0] == 0
    s.close()
    store.close = lambda: None


@pytest.mark.parametrize("rounds", [0, 1])
def test_cancel_preserves_rounds_zero_null_and_cancel_snapshot(store, rounds):
    job = create(store, "test.rounds", parameters={"maxRounds": 2})
    store.start_job(job["jobId"])
    store.start_job_run(job["jobId"], store.job_context(job["jobId"])["runConfig"])
    if rounds:
        store.commit_job_round(
            job["jobId"], {"pendingEvents": [], "consumedEvents": [], "inputEvents": []}
        )
    cancel = store.cancel_job(store.project, job["jobId"])
    assert cancel["state"] == "cancelling"
    cancelled = store.cancelled_job(job["jobId"])
    assert cancelled["state"] == "cancelled" and cancelled["resultRef"] is None
    progress = cancelled["commitProgress"]["committedProgress"]
    assert (progress["lastCommittedRound"] if progress else 0) == rounds
    assert cancel["state"] == "cancelling"  # Immutable response decision snapshot.
    with pytest.raises(JobFault, match="INVALID_STATE"):
        store.commit_job_round(job["jobId"], {})


def page_binding(result):
    return {
        k: result[k]
        for k in ("projectId", "resultId", "inputSnapshotId", "scope", "parametersHash")
    } | {"order": "ordinal+rowId:asc"}


def read_result(s, rows, parameters=None):
    job = create(s, parameters=parameters)
    s.start_job(job["jobId"])
    saved = s.finish_read_job(job["jobId"], rows)
    return s.result_get(s.project, saved["resultRef"]["resultId"])


def test_stable_result_pages_bindings_restarts_expiry_eviction(store):
    store.now_ms = lambda: 1000
    result = read_result(store, [row(i) for i in range(5)])
    binding = page_binding(result)
    first = store.result_page(binding, 2, None)
    second = store.result_page(binding, 2, first["nextCursor"])
    assert [r["ordinal"] for r in second["rows"]] == [2, 3]
    assert store.result_page(binding, 2, first["nextCursor"])["rows"] == second["rows"]
    for bad_binding, size, cursor in [
        ({**binding, "parametersHash": "b" * 64}, 2, first["nextCursor"]),
        (binding, 3, first["nextCursor"]),
        (binding, 2, uid()),
    ]:
        with pytest.raises(JobFault, match="CURSOR_MISMATCH"):
            store.result_page(bad_binding, size, cursor)
    store.now_ms = lambda: 61000
    with pytest.raises(JobFault, match="CURSOR_EXPIRED"):
        store.result_page(binding, 2, first["nextCursor"])
    # Publish another immutable result with same complete identity; old payload is reclaimable.
    newer = read_result(store, [])
    assert newer["resultId"] != result["resultId"]
    store.collect_cache()
    with pytest.raises(JobFault, match="PAYLOAD_EVICTED"):
        store.result_page(binding, 2, None)
    assert store.result_page(page_binding(newer), 2, None)["rows"] == []


def test_list_snapshot_fixed_members_and_dtos(store):
    store.now_ms = lambda: 1000
    original = [create(store) for _ in range(3)]
    first = store.job_list(store.project, "active", 1, None, None)
    listed = first["jobs"]
    store.cancel_job(store.project, original[0]["jobId"])
    create(store)
    current = first
    while current["nextCursor"]:
        current = store.job_list(
            store.project, "active", 1, first["binding"]["listSnapshotId"], current["nextCursor"]
        )
        listed.extend(current["jobs"])
    assert [j["jobId"] for j in listed] == sorted(j["jobId"] for j in original)
    assert {j["state"] for j in listed} == {"queued"}
    with pytest.raises(JobFault, match="CURSOR_MISMATCH"):
        store.job_list(
            store.project, "all", 1, first["binding"]["listSnapshotId"], first["nextCursor"]
        )


def test_definition_set_first_addition_invalidates_same_transaction(store):
    result = read_result(store, [])
    assert result["definitionSetDigests"]["rule"] == digest([])
    store.commit(
        "legacy-project",
        0,
        "internal-commit",
        "internal-job",
        definitions=[{"layer": "rule", "id": "first", "value": {"enabled": False}}],
    )
    changed = store.result_get(store.project, result["resultId"])
    assert changed["state"] == "stale"
    assert changed["staleReason"] == [
        {"code": "RULE_CHANGED", "dependency": "rule:first", "before": 0, "after": 1}
    ]
    assert (
        store.result_current(
            store.project, "test", "probe", "asserted", result["parametersHash"], IMPL
        )
        is None
    )


def test_old_revision_completion_historical_even_no_dependency_changes(store):
    job = create(store)
    store.start_job(job["jobId"])
    store.commit(
        "legacy-project",
        0,
        "model-change",
        "internal",
        definitions=[{"layer": "model", "id": "m", "value": {"temperature": 0}}],
    )
    saved = store.finish_read_job(job["jobId"], [])
    result = store.result_get(store.project, saved["resultRef"]["resultId"])
    assert result["state"] == "historical" and result["staleReason"] == []


def test_internal_kind_does_not_silently_change_identity(store):
    snapshot = store.snapshot("legacy-project")
    for kind in ["query ", "Query", "unknown-kind"]:
        rid = store.publish("legacy-project", snapshot, ["facts:asserted"], kind, [], IMPL)
        assert store.result(rid)["kind"] == kind
        with pytest.raises(JobFault, match="NOT_FOUND"):
            store.result_get(store.project, rid)
    assert {r[0] for r in store._db.execute("SELECT kind FROM results")} == {
        "query ",
        "Query",
        "unknown-kind",
    }


def test_result_page_byte_budget_and_duplicate_rows(store):
    result = read_result(store, [row(i, ["中" * 8192] * 4) for i in range(3)])
    first = store.result_page(page_binding(result), 200, None)
    assert len(first["rows"]) == 1 and first["nextCursor"]
    assert CONTRACT.encoded_size(first) <= 131072
    too_big = read_result(store, [row(0, ["中" * 8192] * 6)])
    with pytest.raises(JobFault, match="RESOURCE_LIMIT"):
        store.result_page(page_binding(too_big), 1, None)
    job = create(store)
    store.start_job(job["jobId"])
    r = row(0)
    with pytest.raises(JobFault, match="INVALID_REQUEST"):
        store.finish_read_job(job["jobId"], [r, r])


def test_pin_report_all_or_none_idempotent_and_evicted(store):
    a = read_result(store, [row(0)], parameters={"workMs": 1})
    b = read_result(store, [row(0)], parameters={"workMs": 2})
    report = uid()
    store.pin_report(store.project, [a["resultId"], b["resultId"]], report)
    store.pin_report(store.project, [b["resultId"], a["resultId"]], report)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.pin_report(store.project, [a["resultId"]], report)
    assert store._db.execute("SELECT count(*) FROM result_pins").fetchone()[0] == 2
    assert store.collect_cache() == []


def test_actual_sqlite_readonly_failure_then_fenced_reconciliation(store):
    job = create(
        store, "test.atomic", plan={"definitions": [{"layer": "rule", "id": "x", "value": {}}]}
    )
    store.start_job(job["jobId"])
    before = store.state("legacy-project")
    store._db.execute("PRAGMA query_only=ON")
    with pytest.raises(sqlite3.OperationalError) as error:
        store.commit_job(job["jobId"])
    assert error.value.sqlite_errorcode & 0xFF == sqlite3.SQLITE_READONLY
    store._db.execute("PRAGMA query_only=OFF")
    assert store.state("legacy-project") == before
    assert store.operation_get(store.project, job["operationId"]) is None
    assert store.reconcile_jobs()[0]["state"] == "failed"


def test_old_base_rejected_without_replaying_confirmed_plan(store):
    job = create(
        store, "test.atomic", plan={"definitions": [{"layer": "rule", "id": "x", "value": {}}]}
    )
    store.start_job(job["jobId"])
    store.commit("legacy-project", 0, "other", "other-job")
    with pytest.raises(JobFault, match="REVISION_CONFLICT") as error:
        store.commit_job(job["jobId"])
    assert error.value.params == {"expected": 0, "actual": 1}
    assert store.operation_get(store.project, job["operationId"]) is None
    assert store.state("legacy-project")["definitions"] == []


@pytest.mark.parametrize(
    "mutation", ["missing", "bad-count", "wrong-run", "wrong-snapshot", "malformed"]
)
def test_summary_unavailable_on_missing_malformed_or_inconsistent_evidence(store, mutation):
    job, state = run_rounds(store)
    saved = store.finish_job_run(
        job["jobId"],
        pending_events=state["pendingEvents"],
        event_consumption=state["consumedEvents"],
    )
    result = store.result_get(store.project, saved["resultRef"]["resultId"])
    payload = store.result(result["resultId"])["payload"]
    if mutation == "missing":
        payload = []
    elif mutation == "malformed":
        payload = [row(0, ["bad"])]
    else:
        payload[0]["cells"][{"bad-count": 6, "wrong-run": 1, "wrong-snapshot": 3}[mutation]] = (
            10 if mutation == "bad-count" else "0" * 64
        )
    store._db.execute(
        "UPDATE results SET payload=? WHERE id=?", (json.dumps(payload), result["resultId"])
    )
    with pytest.raises(JobFault, match="INVALID_STATE"):
        store.result_page(page_binding(result), 10, None)


def test_f6_rejects_fabricated_round_or_final_consumption(store):
    job = create(store, "test.rounds", parameters={"maxRounds": 1, "events": ["a"]})
    store.start_job(job["jobId"])
    context = store.job_context(job["jobId"])
    config = context["runConfig"]
    assert config["parametersRef"] == job["parametersHash"]
    assert store.blob(store.project, config["eventsRef"]) == ["a"]
    assert config["initialSnapshotId"] == job["inputSnapshotId"]
    assert config["semantics"] == "I04-test-rounds-v1"
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.start_job_run(job["jobId"], {**config, "maxRounds": 2})
    store.start_job_run(job["jobId"], config)
    state = {"pendingEvents": [], "consumedEvents": ["a"], "inputEvents": ["a"]}
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.commit_job_round(job["jobId"], {**state, "consumedEvents": []})
    assert store.get_job(store.project, job["jobId"])["commitProgress"]["committedProgress"] is None
    store.commit_job_round(job["jobId"], state)
    with pytest.raises(JobFault, match="IDENTITY_CONFLICT"):
        store.finish_job_run(job["jobId"], pending_events=["invented"], event_consumption=["a"])
    assert store.get_job(store.project, job["jobId"])["state"] == "running"


def test_result_cursor_survives_store_restart_and_exact_repeat(store):
    result = read_result(store, [row(i) for i in range(5)])
    binding = page_binding(result)
    first = store.result_page(binding, 2, None)
    second = store.result_page(binding, 2, first["nextCursor"])
    assert store.result_page(binding, 2, first["nextCursor"]) == second
    path = store.path
    store.close()
    reopened = JobStore(path, contract=CONTRACT)
    assert reopened.result_page(binding, 2, first["nextCursor"]) == second
    reopened.close()
    store.close = lambda: None


def test_paging_capacity_is_bounded_not_silently_evicted(store):
    store.max_cursor_records = 1
    result = read_result(store, [row(i) for i in range(5)])
    binding = page_binding(result)
    first = store.result_page(binding, 1, None)
    with pytest.raises(JobFault, match="RESOURCE_LIMIT"):
        store.result_page(binding, 1, first["nextCursor"])
    assert store._db.execute("SELECT count(*) FROM job_cursors").fetchone()[0] == 1


def test_ownership_conflict_has_persistent_safe_detail_and_global_claim_probe(store):
    first = {"subject": "urn:probe", "predicate": "urn:name", "object": '"original"'}
    first["id"] = digest([first["subject"], first["predicate"], first["object"]])
    store.commit(
        "legacy-project",
        0,
        "seed",
        "seed-job",
        mapping={"id": "owner", "rows": [{"row": "1", "facts": [first]}]},
    )
    store.commit(
        "legacy-project", 1, "manual", "manual-job", edits={first["id"]: '"private-value"'}
    )
    before = store.state("legacy-project")
    with pytest.raises(JobFault, match="OWNERSHIP_CONFLICT") as error:
        create(store, "test.atomic", plan={"mapping": {"id": "owner", "rows": []}})
    ref = error.value.params["detailRef"]
    assert CONTRACT.validate("id", ref)
    detail = store.detail_get(store.project, ref)
    assert detail == {"category": "ownership", "resource": "plan", "projectId": store.project}
    assert "private-value" not in json.dumps(detail)
    assert store.state("legacy-project") == before
    job = create(store)
    assert store.has_operation_claim(job["operationId"])
    assert not store.has_operation_claim(uid())
    store.create_project("other")
    other = store.public_project("other")
    with pytest.raises(JobFault, match="NOT_FOUND"):
        store.detail_get(other, ref)


def test_s1_conflict_structured_category_without_message_parsing(store):
    from ontolearn_engine.storage import Conflict

    store.commit("legacy-project", 0, "seed", "seed-job")
    with pytest.raises(Conflict) as error:
        store.commit("legacy-project", 0, "different", "different-job")
    assert error.value.category == "revision"
    assert error.value.code == "REVISION_CONFLICT"
    assert error.value.params == {"expected": 0, "actual": 1}
    with pytest.raises(Conflict) as error:
        store.commit("legacy-project", 0, "seed", "different-job")
    assert error.value.category == "identity"
    assert error.value.code == "IDENTITY_CONFLICT"
    assert error.value.params == {}
    assert Conflict("unknown internal text").code == "INTERNAL_ERROR"


def test_queued_cancel_preserves_valid_decision_snapshot_and_durable_terminal(store):
    job = create(store)
    answer = store.cancel_job(store.project, job["jobId"])
    assert answer == {
        "jobId": job["jobId"],
        "disposition": "accepted",
        "state": "queued",
        "stateVersion": 1,
    }
    assert CONTRACT.validate("result_job.cancel", answer)
    saved = store.get_job(store.project, job["jobId"])
    assert saved["state"] == "cancelled" and saved["stateVersion"] == 2
    terminal = store.cancel_job(store.project, job["jobId"])
    assert terminal["disposition"] == "alreadyTerminal" and terminal["state"] == "cancelled"
    assert CONTRACT.validate("result_job.cancel", terminal)
    assert answer["state"] == "queued" and answer["stateVersion"] == 1


def test_round_progress_new_persistent_version_then_cancel_snapshot(store):
    job = create(store, "test.rounds", parameters={"maxRounds": 2, "events": ["a"]})
    running = store.start_job(job["jobId"])
    assert running["stateVersion"] == 2
    store.start_job_run(job["jobId"], store.job_context(job["jobId"])["runConfig"])
    store.commit_job_round(
        job["jobId"], {"pendingEvents": [], "consumedEvents": ["a"], "inputEvents": ["a"]}
    )
    progress = store.get_job(store.project, job["jobId"])
    assert progress["state"] == "running" and progress["stateVersion"] == 3
    assert progress["updatedAtMs"] >= running["updatedAtMs"]
    answer = store.cancel_job(store.project, job["jobId"])
    assert answer["state"] == "cancelling" and answer["stateVersion"] == 4
    assert CONTRACT.validate("result_job.cancel", answer)
    saved = store.cancelled_job(job["jobId"])
    assert saved["stateVersion"] == 5 and saved["state"] == "cancelled"
    assert saved["commitProgress"]["committedProgress"]["lastCommittedRound"] == 1
    assert answer["state"] == "cancelling" and answer["stateVersion"] == 4
