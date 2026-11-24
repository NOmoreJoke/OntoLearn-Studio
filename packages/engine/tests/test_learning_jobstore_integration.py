"""G.0/E.5 inputs through approved I04 preview, stdio worker and SQLite.

These are infrastructure probes, not product mapping/behavior/scenario or
learning-tool adapters. test.atomic stays unavailable in product mode. All
projects, processes and databases are local to this test; no GUI is started.
"""

import asyncio
import os
import signal
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from ontolearn_engine import coordinator as coordinator_module
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.learning.baselines import read_json, store_seed_plan
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import canonical, digest
from test_resident_runtime import Session, prepare

ROOT = Path(__file__).resolve().parents[3]
INTERNAL_PROJECT = "t09-fixture-probe"


@pytest.fixture(autouse=True)
def source_engine_only(monkeypatch):
    # Do not inherit a package probe pointing at another worktree's binary.
    monkeypatch.delenv("ONTOLEARN_TEST_ENGINE", raising=False)


def assert_seed_state(actual, plan):
    """Full persisted content, not a count/revision-only assertion."""
    assert actual == {
        "mappingState": {},
        "definitions": sorted(
            [
                {"layer": d["layer"], "id": d["id"], "payload": canonical(d["value"])}
                for d in plan["definitions"]
            ],
            key=lambda d: (d["layer"], d["id"]),
        ),
        "facts": sorted(
            [
                f | {"owner": None, "source_row": None, "managed_value": None}
                for f in plan["manual"]
            ],
            key=lambda f: f["id"],
        ),
    }


def fixture_preview(database, baseline, parameters=None):
    store = JobStore(database, contract=CONTRACT)
    try:
        store.create_project(INTERNAL_PROJECT)
        project = store.public_project(INTERNAL_PROJECT)
        before_state = store.state(INTERNAL_PROJECT)
        before_project = store.project_get(project)
        assert CONTRACT.validate("result_project.get", before_project)
        plan = store_seed_plan(ROOT, baseline)
        request = prepare(store, project, "test.atomic", parameters or {}, plan=plan)
        # prepare_plan runs the real Store commit under rollback-only savepoint.
        # Confirmation metadata is intentionally retained, but no formal change.
        assert store.project_get(project) == before_project
        assert store.state(INTERNAL_PROJECT) == before_state
        assert list(store._db.execute("SELECT * FROM commits")) == []
        assert list(store._db.execute("SELECT * FROM commit_evidence")) == []
        assert store.operation_get(project, request["operationId"]) is None
        return project, request, plan, before_project, before_state
    finally:
        store.close()


@pytest.mark.parametrize("baseline", ["G-base", "G-map-empty", "G-behavior", "E.5"])
def test_full_fixture_real_preview_worker_commit_receipt_and_reopen(tmp_path, baseline):
    database = tmp_path / "fixture-job.sqlite"
    project, request, plan, before_project, _ = fixture_preview(database, baseline)
    session = Session(database, [project])
    try:
        job = session.call("job.create", request)
        assert CONTRACT.validate("job", job)
        final = session.terminal(project, job["jobId"])
        assert final["state"] == "succeeded", final
        marker = session.call(
            "operation.get", {"projectId": project, "operationId": request["operationId"]}
        )
        expected_plan = {
            "base": 0,
            **{
                key: plan.get(key)
                for key in ("definitions", "manual", "edits", "remove", "mapping")
            },
        }
        assert marker == {
            "projectId": project,
            "operationId": request["operationId"],
            "jobId": job["jobId"],
            "projectRevision": 1,
            "beforeSnapshotId": before_project["inputSnapshotId"],
            "afterSnapshotId": session.call("project.get", {"projectId": project})[
                "inputSnapshotId"
            ],
            "planHash": digest(expected_plan),
        }
        assert final["commitProgress"]["marker"] == {
            key: marker[key]
            for key in ("projectRevision", "beforeSnapshotId", "afterSnapshotId", "planHash")
        }
        result = session.call(
            "result.get", {"projectId": project, "resultId": final["resultRef"]["resultId"]}
        )
        assert result["kind"] == "receipt" and result["state"] == "historical"
        assert result["inputSnapshotId"] == before_project["inputSnapshotId"]
        binding = {
            key: result[key]
            for key in ("projectId", "resultId", "inputSnapshotId", "scope", "parametersHash")
        } | {"order": "ordinal+rowId:asc"}
        page = session.call("result.page", {"binding": binding, "pageSize": 1, "cursor": None})
        assert [row["cells"] for row in page["rows"]] == [
            [
                "commit.receipt.v1",
                request["operationId"],
                1,
                marker["beforeSnapshotId"],
                marker["afterSnapshotId"],
                marker["planHash"],
            ]
        ]
        assert page["nextCursor"] is None
        # Retrying the same accepted operation returns its immutable original result.
        assert session.call("job.create", request) == final
        assert session.call("project.get", {"projectId": project})["projectRevision"] == 1
    finally:
        session.close()
    reopened = JobStore(database, contract=CONTRACT)
    try:
        assert_seed_state(reopened.state(INTERNAL_PROJECT), plan)
        project_dto = reopened.project_get(project)
        assert CONTRACT.validate("result_project.get", project_dto)
        assert project_dto["dependencyVector"] == {
            **{d["layer"] + ":" + d["id"]: 1 for d in plan["definitions"]},
            **({"facts:asserted": 1} if plan["manual"] else {}),
        }
        assert reopened.load_snapshot(marker["beforeSnapshotId"])["state"] == {
            "mappingState": {},
            "definitions": [],
            "facts": [],
        }
        assert_seed_state(reopened.load_snapshot(marker["afterSnapshotId"])["state"], plan)
        assert reopened.operation_get(project, request["operationId"]) == marker
    finally:
        reopened.close()


@pytest.mark.parametrize("mode", ["stale-preview", "worker-failure", "product-mode"])
def test_fixture_plan_failure_has_no_partial_seed_or_false_product_success(tmp_path, mode):
    database = tmp_path / "fixture-negative.sqlite"
    project, request, _, _, unchanged = fixture_preview(
        database, "G-behavior", {"failRound": 1} if mode == "worker-failure" else {}
    )
    if mode == "stale-preview":
        store = JobStore(database, contract=CONTRACT)
        try:
            triple = {
                "subject": "urn:ontolearn:learning:equipment/001",
                "predicate": "urn:ontolearn:learning:name",
                "object": '"用户保留名称"',
            }
            fact = triple | {"id": digest(list(triple.values()))}
            store.commit(INTERNAL_PROJECT, 0, "human-edit", "human-edit-job", manual=[fact])
            unchanged = store.state(INTERNAL_PROJECT)
        finally:
            store.close()
    session = Session(database, [project], test_mode=mode != "product-mode")
    try:
        accepted = session.call("job.create", request)
        if mode == "product-mode":
            assert accepted["code"] == "UNSUPPORTED_CAPABILITY"
        else:
            terminal = session.terminal(project, accepted["jobId"])
            assert terminal["state"] == "failed"
            assert terminal["error"]["code"] == (
                "REVISION_CONFLICT" if mode == "stale-preview" else "INTERNAL_ERROR"
            )
            assert terminal["resultRef"] is None
            assert terminal["commitProgress"]["marker"] is None
        assert (
            session.call(
                "operation.get", {"projectId": project, "operationId": request["operationId"]}
            )
            is None
        )
    finally:
        session.close()
    reopened = JobStore(database, contract=CONTRACT)
    try:
        assert reopened.state(INTERNAL_PROJECT) == unchanged
        assert reopened.revision(INTERNAL_PROJECT) == (1 if mode == "stale-preview" else 0)
        assert list(reopened._db.execute("SELECT * FROM results")) == []

    finally:
        reopened.close()


def test_course_revision_binds_to_manifest_sha_without_changing_the_seeded_plan(tmp_path):
    """The offline course revision must not alter Appendix G fixture identity.

    Learning attempts bind manifest SHA + courseVersion + courseExtensionVersion,
    so a course revision changes the bound SHA only, never the seeded store plan.
    """
    from ontolearn_engine.learning.baselines import file_digest, verify

    result = verify(ROOT)
    assert result["version"] == "prd-v0.6-learning-1"
    assert result["courseVersion"] == "offline-course-2"
    assert result["courseExtensionVersion"] == "ext-1"
    manifest_sha = file_digest(ROOT / "tests/fixtures/product-baselines/manifest.json")
    assert result["manifestSha256"] == manifest_sha

    plan = store_seed_plan(ROOT, "G-base")
    baseline = read_json(ROOT / "tests/fixtures/product-baselines/G-base.json")
    assert len(plan["manual"]) == len(baseline["facts"]) == 18
    assert {fact["subject"] for fact in plan["manual"]} == {
        fact["subject"] for fact in baseline["facts"]
    }
    assert any(definition["layer"] == "scenario" for definition in plan["definitions"])
    assert all("expected" not in definition["value"] for definition in plan["definitions"])


def test_signal_worker_avoids_popen_poll_race_on_posix(monkeypatch, caplog):
    if os.name != "posix":
        pytest.skip("POSIX asyncio child-watcher race only applies on POSIX")

    def forbidden_poll(self):
        raise AssertionError("Popen.poll must not run from _signal_worker on POSIX")

    monkeypatch.setattr(subprocess.Popen, "poll", forbidden_poll)
    kill_calls = []
    real_kill = os.kill

    def tracking_kill(pid, sig):
        kill_calls.append((pid, sig))
        return real_kill(pid, sig)

    monkeypatch.setattr(coordinator_module, "os", SimpleNamespace(name="posix", kill=tracking_kill))

    # Guard invalid pid <= 0 without touching the process table.
    coordinator_module._signal_worker(SimpleNamespace(returncode=None, pid=0), force=True)
    coordinator_module._signal_worker(SimpleNamespace(returncode=None, pid=None), force=False)
    assert kill_calls == []

    # 1) Exited unreaped child (EOF on closed stdout pipe guarantees exit before signalling):
    # signalling via os.kill must not call Popen.poll or reap the child's real exit status 76.
    zombie = subprocess.Popen(
        [sys.executable, "-c", "import os; os._exit(76)"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert zombie.stdout.read() == b""
        coordinator_module._signal_worker(
            SimpleNamespace(returncode=None, pid=zombie.pid), force=True
        )
        assert kill_calls[-1] == (zombie.pid, signal.SIGKILL)
        assert zombie.wait() == 76
    finally:
        zombie.stdout.close()
        if zombie.returncode is None:
            try:
                real_kill(zombie.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            zombie.wait()

    # 2) Live asyncio worker: terminate via os.kill without asyncio child-watcher warnings.
    async def exercise():
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-c",
            "import sys, time; sys.stdout.write('r\\n'); sys.stdout.flush(); time.sleep(30)",
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        assert await proc.stdout.readline() == b"r\n"
        coordinator_module._signal_worker(proc, force=False)
        returncode = await proc.wait()
        # Once returncode is known, _signal_worker becomes a strict no-op.
        before_noop = len(kill_calls)
        coordinator_module._signal_worker(proc, force=True)
        assert len(kill_calls) == before_noop
        return returncode

    with caplog.at_level("WARNING", logger="asyncio"):
        returncode = asyncio.run(exercise())
    assert returncode == -signal.SIGTERM
    assert len(kill_calls) == 2
    assert "Unknown child process pid" not in caplog.text


def test_signal_worker_non_posix_dispatches_terminate_and_kill(monkeypatch):
    monkeypatch.setattr(coordinator_module, "os", SimpleNamespace(name="nt", kill=os.kill))
    events = []

    class DummyProcess:
        def __init__(self, returncode=None, *, raise_lookup=False):
            self.returncode = returncode
            self.raise_lookup = raise_lookup

        def terminate(self):
            events.append("terminate")
            if self.raise_lookup:
                raise ProcessLookupError

        def kill(self):
            events.append("kill")
            if self.raise_lookup:
                raise ProcessLookupError

    coordinator_module._signal_worker(DummyProcess(returncode=0), force=True)
    coordinator_module._signal_worker(DummyProcess(), force=False)
    coordinator_module._signal_worker(DummyProcess(), force=True)
    coordinator_module._signal_worker(DummyProcess(raise_lookup=True), force=False)
    coordinator_module._signal_worker(DummyProcess(raise_lookup=True), force=True)
    assert events == ["terminate", "kill", "terminate", "kill"]
