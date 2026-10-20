"""Real round/job transaction failures and F6 immutable multi-page evidence.

The subprocess is the sole writer; recovery opens a fresh leased connection only
once that process has exited. No worker may publish a DB result or terminal.
"""

import json
import subprocess
import sys
from uuid import uuid4

import pytest
from ontolearn_engine.job_store import JobFault, JobStore
from test_job_store import CONTRACT, ROOT, create, page_binding, run_rounds

PHASES = ["before", "mid_data", "mid_marker", "mid_job_progress", "before_commit", "after_commit"]
CHILD = r"""
import importlib.util,json,os,sqlite3,sys
from ontolearn_engine.job_store import JobStore
spec=importlib.util.spec_from_file_location('contract',sys.argv[2])
contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
path,project,identity,phase,failure,previous=sys.argv[1],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],int(sys.argv[7])
s=JobStore(path,contract=contract)
s.start_job(identity)
run=s.start_job_run(identity,s.job_context(identity)['runConfig'])
first={'pendingEvents':['b'],'consumedEvents':['a'],'inputEvents':['a','b']}
second={'pendingEvents':[],'consumedEvents':['a','b'],'inputEvents':['a','b']}
if previous:s.commit_job_round(identity,first)
def hook(stage):
 if stage!=phase:return
 if failure=='exit':os._exit(92)
 if failure=='cancel':raise KeyboardInterrupt()
 if failure=='disk':
  # Real SQLite READONLY at this precise stage, not a text-matched OSError.
  s._db.execute('PRAGMA query_only=ON')
  s._db.execute('UPDATE projects SET revision=revision')
  raise AssertionError('read-only guard did not fail')
 raise RuntimeError('test fault')
try:s.commit_job_round(identity,second if previous else first,hook)
except (Exception,KeyboardInterrupt) as error:
 if failure=='disk':
  assert isinstance(error,sqlite3.OperationalError)
  assert error.sqlite_errorcode & 0xff == sqlite3.SQLITE_READONLY
 s._db.execute('PRAGMA query_only=OFF')
 if failure=='cancel':
  decision=s.cancel_job(project,identity)
  assert decision['state']=='cancelling'
 print(json.dumps({'failure':failure,'phase':phase}),flush=True)
else:raise AssertionError('fault was not reached')
s.close()
"""


@pytest.fixture
def db(tmp_path):
    store = JobStore(tmp_path / "round-faults.sqlite", contract=CONTRACT)
    store.create_project("round-project")
    store.project = store.public_project("round-project")
    yield store
    if not store._lease.closed:
        store.close()


@pytest.mark.parametrize("previous", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("failure", ["exception", "disk", "cancel", "exit"])
def test_round_job_progress_atomic_fault_matrix_fences_and_preserves_previous_round(
    db, previous, phase, failure
):
    job = create(
        db, "test.rounds", parameters={"maxRounds": 2, "events": ["a", "b"], "consumePerRound": 1}
    )
    path, project = db.path, db.project
    formal_before = db.state("round-project")
    revision_before = db.revision("round-project")
    db.close()
    process = subprocess.run(
        [
            sys.executable,
            "-c",
            CHILD,
            str(path),
            str(ROOT / "packages/contracts/python/contract_v2.py"),
            project,
            job["jobId"],
            phase,
            failure,
            str(previous),
        ],
        capture_output=True,
        timeout=15,
    )
    assert process.returncode == (92 if failure == "exit" else 0), process.stderr.decode()
    assert process.stderr == b""
    # The subprocess exit is observed before reacquiring the OS lease and the
    # SQLite writer sequence. Recovery cannot race an old DB writer.
    reopened = JobStore(path, contract=CONTRACT)
    try:
        with pytest.raises(JobFault, match="STORAGE_BUSY"):
            JobStore(path, contract=CONTRACT)
        recovered = reopened.reconcile_jobs()
        assert len(recovered) == 1
        saved = recovered[0]
        assert saved["state"] == ("cancelled" if failure == "cancel" else "failed")
        assert saved["resultRef"] is None and saved["state"] != "succeeded"
        expected = previous + (phase == "after_commit")
        progress = saved["commitProgress"]["committedProgress"]
        if not expected:
            assert progress is None
        else:
            assert progress["lastCommittedRound"] == expected
            snapshot = reopened.load_snapshot(progress["snapshotRef"])
            assert snapshot["round"] == expected
            assert snapshot["state"] == {
                "pendingEvents": ["b"] if expected == 1 else [],
                "consumedEvents": ["a"] if expected == 1 else ["a", "b"],
                "inputEvents": ["a", "b"],
            }
        run = reopened._db.execute("SELECT run FROM jobs WHERE id=?", (job["jobId"],)).fetchone()[0]
        history = reopened.history(run)
        assert [r["number"] for r in history["rounds"]] == list(range(1, expected + 1))
        assert history["terminal"]["status"] == saved["state"]
        assert history["committedProgress"] == progress
        assert saved["stateVersion"] == 3 + expected + (failure == "cancel")
        assert reopened._db.execute("SELECT count(*) FROM results").fetchone()[0] == 0
        assert reopened.state("round-project") == formal_before
        assert reopened.revision("round-project") == revision_before
        assert reopened.reconcile_jobs() == []  # No replay or second terminal.
        assert reopened.get_job(project, job["jobId"]) == saved
    finally:
        reopened.close()


def finish_rounds(store, *, count=3, pending=True):
    job, state = run_rounds(store, count=count, pending=pending)
    job = store.finish_job_run(
        job["jobId"],
        pending_events=state["pendingEvents"],
        event_consumption=state["consumedEvents"],
    )
    return job, store.result_get(store.project, job["resultRef"]["resultId"])


def test_scenario_actual_multi_page_round_audit_summary_only_first_non_cursor_page(db):
    job, result = finish_rounds(db, count=4)
    binding = page_binding(result)
    first = db.result_page(binding, 1, None)
    assert first["rows"][0]["cells"][0] == "run.summary.v1"
    assert first["nextCursor"]
    progress = job["commitProgress"]["committedProgress"]
    history = db.history(progress["runId"])
    pages = []
    cursor = first["nextCursor"]
    while cursor:
        page = db.result_page(binding, 1, cursor)
        assert db.result_page(binding, 1, cursor) == page
        pages.extend(page["rows"])
        cursor = page["nextCursor"]
    assert [r["ordinal"] for r in pages] == [1, 2, 3, 4]
    assert [r["cells"] for r in pages] == [
        [
            "run.round.v1",
            progress["runId"],
            r["number"],
            r["snapshot"],
            r["operation"],
            job["jobId"],
        ]
        for r in history["rounds"]
    ]
    assert all(row["cells"][0] != "run.summary.v1" for row in pages)
    assert len({r["rowId"] for r in [*first["rows"], *pages]}) == 5


@pytest.mark.parametrize(
    "mutation",
    ["duplicate-summary", "wrong-round-job", "wrong-snapshot", "missing-round", "wrong-operation"],
)
def test_scenario_round_audit_is_unavailable_if_not_equal_to_true_persistent_evidence(db, mutation):
    job, result = finish_rounds(db)
    payload = db.result(result["resultId"])["payload"]
    if mutation == "duplicate-summary":
        payload[1]["cells"] = list(payload[0]["cells"])
    elif mutation == "missing-round":
        payload.pop()
    else:
        index = {"wrong-round-job": 5, "wrong-snapshot": 3, "wrong-operation": 4}[mutation]
        payload[1]["cells"][index] = "0" * 64 if mutation == "wrong-snapshot" else str(uuid4())
    db._db.execute(
        "UPDATE results SET payload=? WHERE id=?", (json.dumps(payload), result["resultId"])
    )
    with pytest.raises(JobFault, match="INVALID_STATE"):
        db.result_page(page_binding(result), 1, None)
    assert db.get_job(db.project, job["jobId"])["state"] == "succeeded"
    assert len(db.history(job["commitProgress"]["committedProgress"]["runId"])["rounds"]) == 3


def test_original_scenario_binding_survives_new_result_and_collection(
    db,
):
    first_job, first = finish_rounds(db)
    original_job = db.get_job(db.project, first_job["jobId"])
    original_progress = first_job["commitProgress"]["committedProgress"]
    original_history = db.history(original_progress["runId"])
    first_page = db.result_page(page_binding(first), 1, None)
    second_job, second = finish_rounds(db)
    assert first["resultId"] != second["resultId"] and first_job["jobId"] != second_job["jobId"]
    # All other public input fields agree; a cursor still cannot switch result IDs.
    assert {k: first[k] for k in ("inputSnapshotId", "scope", "parametersHash")} == {
        k: second[k] for k in ("inputSnapshotId", "scope", "parametersHash")
    }
    with pytest.raises(JobFault, match="CURSOR_MISMATCH"):
        db.result_page(page_binding(second), 1, first_page["nextCursor"])
    original_audit = db.result_page(page_binding(first), 1, first_page["nextCursor"])
    assert original_audit["rows"][0]["cells"][1] == original_progress["runId"]
    assert first["resultId"] in db.collect_cache()
    metadata = db.result_get(db.project, first["resultId"])
    assert metadata["payloadStatus"] == "evicted" and metadata["state"] == "historical"
    assert metadata["jobId"] == first_job["jobId"]
    with pytest.raises(JobFault, match="PAYLOAD_EVICTED"):
        db.result_page(page_binding(first), 1, first_page["nextCursor"])
    assert db.get_job(db.project, first_job["jobId"]) == original_job
    assert db.history(original_progress["runId"]) == original_history
    assert db.result_page(page_binding(second), 1, None)["rows"][0]["cells"][0] == "run.summary.v1"


def test_scenario_payload_from_another_real_job_cannot_rebind_original_result(db):
    first_job, first = finish_rounds(db)
    _, second = finish_rounds(db)
    second_payload = db.result(second["resultId"])["payload"]
    db._db.execute(
        "UPDATE results SET payload=? WHERE id=?", (json.dumps(second_payload), first["resultId"])
    )
    with pytest.raises(JobFault, match="INVALID_STATE"):
        db.result_page(page_binding(first), 1, None)
    # Original resultRef is immutable service evidence, not whichever result is current.
    assert db.get_job(db.project, first_job["jobId"])["resultRef"]["resultId"] == first["resultId"]


def test_last_round_without_terminal_differs_from_complete_finish_and_cancel(db):
    job, state = run_rounds(db, count=2)
    before = db.get_job(db.project, job["jobId"])
    assert before["state"] == "running" and before["resultRef"] is None
    run = before["commitProgress"]["committedProgress"]["runId"]
    assert db.history(run)["terminal"] is None
    complete = db.finish_job_run(
        job["jobId"],
        pending_events=state["pendingEvents"],
        event_consumption=state["consumedEvents"],
    )
    history = db.history(run)
    answer = db.cancel_job(db.project, job["jobId"])
    assert answer["disposition"] == "alreadyTerminal" and answer["state"] == "succeeded"
    assert db.get_job(db.project, job["jobId"]) == complete
    assert db.history(run) == history
    assert history["terminal"]["status"] == "succeeded"
    assert db.result_page(
        page_binding(db.result_get(db.project, complete["resultRef"]["resultId"])), 1, None
    )["nextCursor"]


def test_original_result_rejects_job_result_ref_rebound_to_another_real_result(db):
    first_job, first = finish_rounds(db)
    second_job, _ = finish_rounds(db)
    dto = db.get_job(db.project, first_job["jobId"])
    dto["resultRef"] = second_job["resultRef"]
    # Deliberate corrupted mutable projection: the immutable original result/run
    # records remain intact and cannot silently bind the other real result.
    db._db.execute("UPDATE jobs SET dto=? WHERE id=?", (json.dumps(dto), first_job["jobId"]))
    with pytest.raises(JobFault, match="INVALID_STATE"):
        db.result_page(page_binding(first), 1, None)
