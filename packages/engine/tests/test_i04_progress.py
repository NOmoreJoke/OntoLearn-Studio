"""Actual bounded coordinator/worker/SQLite phases, plus raw stdio late subscription.

No worker/store substitutes, synthetic terminal DTOs or Electron windows. Progress
is an unknown-total execution hint; durable state/version remains JobStore-owned.
"""

import asyncio
import time
from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
from test_resident_runtime import Session, prepare


def request(coordinator, method, params):
    response = coordinator.request(
        {
            "kind": "request",
            "protocolVersion": 2,
            "id": str(uuid4()),
            "engineSessionId": coordinator.session,
            "method": method,
            "params": params,
        }
    )
    assert response["ok"], response
    return response["result"]


def start(store, emitted):
    project = store.public_project("progress")
    coordinator = Coordinator(
        store, test_mode=True, allowed_projects={project}, emit=emitted.append
    )
    request(coordinator, "hello", {"supportedVersions": [2], "clientId": str(uuid4())})
    return coordinator, project


def assert_route(events, job, subscription, session):
    binding = {
        "engineSessionId": session,
        "projectId": job["projectId"],
        "jobId": job["jobId"],
        "subscriptionId": subscription["subscriptionId"],
        "lastSeq": subscription["seq"],
        "stateVersion": job["stateVersion"],
        "state": job["state"],
    }
    for event in events:
        assert CONTRACT.validate("notification", event)
        assert event["seq"] == binding["lastSeq"] + 1
        assert CONTRACT.accepts_job_event(event, binding)
        binding["lastSeq"] = event["seq"]
        if event["event"] == "job.state":
            binding["state"] = event["data"]["state"]
            binding["stateVersion"] = event["data"]["stateVersion"]
        else:
            assert event["data"]["stateVersion"] == binding["stateVersion"]
            assert event["data"]["progress"]["completed"] is None
            assert event["data"]["progress"]["total"] is None
    return binding


@pytest.fixture
def store(tmp_path):
    service = JobStore(tmp_path / "progress.sqlite", contract=CONTRACT)
    service.create_project("progress")
    yield service
    if not service._lease.closed:
        service.close()


def test_queued_snapshot_precedes_response_without_consuming_its_first_sequence(store):
    emitted = []
    coordinator, project = start(store, emitted)
    job = request(coordinator, "job.create", prepare(store, project, "test.read", {}))
    subscription = request(
        coordinator, "job.subscribe", {"projectId": project, "jobId": job["jobId"]}
    )
    # Coordinator.request emits the hint synchronously before the serve adapter
    # writes its response. That response must still describe the seq=0 baseline.
    assert subscription["seq"] == 0
    assert len(emitted) == 1
    assert emitted[0]["seq"] == 1
    assert emitted[0]["data"]["progress"] == {
        "stage": "queued",
        "completed": None,
        "total": None,
    }
    assert_route(emitted, job, subscription, coordinator.session)
    assert store.get_job(project, job["jobId"]) == job
    assert coordinator.active == {}
    request(coordinator, "job.cancel", {"projectId": project, "jobId": job["jobId"]})
    terminal = store.get_job(project, job["jobId"])
    assert terminal["state"] == "cancelled"
    count = len(emitted)
    later = request(coordinator, "job.subscribe", {"projectId": project, "jobId": job["jobId"]})
    assert later["seq"] == 0
    assert len(emitted) == count


@pytest.mark.parametrize("capability", ["test.read", "test.atomic", "test.rounds"])
def test_real_worker_phases_share_sequence_and_do_not_increment_durable_version(store, capability):
    emitted = []
    coordinator, project = start(store, emitted)
    params = prepare(
        store,
        project,
        capability,
        {"workMs": 100, "maxRounds": 3},
        plan={"definitions": [{"layer": "rule", "id": "phase-rule", "value": {"enabled": True}}]}
        if capability == "test.atomic"
        else None,
    )
    job = request(coordinator, "job.create", params)
    subscription = request(
        coordinator, "job.subscribe", {"projectId": project, "jobId": job["jobId"]}
    )

    async def run():
        await coordinator.tick()
        await asyncio.wait_for(asyncio.gather(*coordinator.tasks), 5)

    asyncio.run(run())
    final = store.get_job(project, job["jobId"])
    assert final["state"] == "succeeded"
    assert final["stateVersion"] == (6 if capability == "test.rounds" else 3)
    binding = assert_route(emitted, job, subscription, coordinator.session)
    assert binding["state"] == "succeeded"
    phases = [e["data"]["progress"]["stage"] for e in emitted if e["event"] == "job.progress"]
    assert phases == (
        ["queued", "loading", "computing"]
        + (["committing", "computing"] * 3 if capability == "test.rounds" else [])
        + ["reconciling", "committing"]
    )
    assert emitted[-1]["event"] == "job.state"
    assert emitted[-1]["data"] == final
    assert coordinator.active == {}
    count = len(emitted)
    request(coordinator, "job.subscribe", {"projectId": project, "jobId": job["jobId"]})
    assert len(emitted) == count
    if capability == "test.atomic":
        marker = store.operation_get(project, job["operationId"])
        assert marker["projectRevision"] == store.project_get(project)["projectRevision"] == 1
        assert marker["afterSnapshotId"] == store.project_get(project)["inputSnapshotId"]
    if capability == "test.rounds":
        assert final["commitProgress"]["committedProgress"]["lastCommittedRound"] == 3


def test_real_worker_failure_removes_phase_cache_and_never_publishes_terminal_progress(store):
    emitted = []
    coordinator, project = start(store, emitted)
    job = request(coordinator, "job.create", prepare(store, project, "test.read", {"failRound": 1}))
    subscription = request(
        coordinator, "job.subscribe", {"projectId": project, "jobId": job["jobId"]}
    )

    async def run():
        await coordinator.tick()
        await asyncio.wait_for(asyncio.gather(*coordinator.tasks), 5)

    asyncio.run(run())
    assert_route(emitted, job, subscription, coordinator.session)
    final = store.get_job(project, job["jobId"])
    assert final["state"] == "failed"
    assert final["stateVersion"] == 3
    assert final["error"]["code"] == "INTERNAL_ERROR"
    assert coordinator.active == {}
    assert emitted[-1]["event"] == "job.state"
    count = len(emitted)
    request(coordinator, "job.subscribe", {"projectId": project, "jobId": job["jobId"]})
    assert len(emitted) == count


def test_raw_stdio_late_subscription_cancel_and_other_job_remain_isolated(store):
    project = store.public_project("progress")
    slow = prepare(store, project, "test.read", {"workMs": 2000})
    other = prepare(store, project, "test.read", {"workMs": 300})
    database = store.path
    store.close()
    session = Session(database, [project])
    try:
        first = session.call("job.create", slow)
        second = session.call("job.create", other)
        old = session.call("job.subscribe", {"projectId": project, "jobId": first["jobId"]})
        second_sub = session.call("job.subscribe", {"projectId": project, "jobId": second["jobId"]})
        deadline = time.monotonic() + 5
        while not any(
            e["subscriptionId"] == old["subscriptionId"]
            and e["event"] == "job.progress"
            and e["data"]["progress"]["stage"] == "computing"
            for e in session.notifications
        ):
            assert time.monotonic() < deadline
            session.call("session.ping", {"nonce": str(uuid4())})
            time.sleep(0.01)
        session.call(
            "job.unsubscribe",
            {
                "projectId": project,
                "jobId": first["jobId"],
                "subscriptionId": old["subscriptionId"],
            },
        )
        old_count = sum(e["subscriptionId"] == old["subscriptionId"] for e in session.notifications)
        first_current = session.job(project, first["jobId"])
        assert first_current["state"] == "running"
        fresh = session.call("job.subscribe", {"projectId": project, "jobId": first["jobId"]})
        assert fresh["seq"] == 0
        assert fresh["stateVersion"] == first_current["stateVersion"] == 2
        early = [e for e in session.notifications if e["subscriptionId"] == fresh["subscriptionId"]]
        # Session.call has already parsed this actual wire frame while awaiting
        # the response. It cannot be a synthetic post-response progress event.
        assert len(early) == 1
        assert early[0]["seq"] == 1
        assert early[0]["data"]["progress"] == {
            "stage": "computing",
            "completed": None,
            "total": None,
        }
        for _ in range(3):
            nonce = str(uuid4())
            assert session.call("session.ping", {"nonce": nonce}) == {"nonce": nonce}
            time.sleep(0.01)
        assert (
            len(
                [e for e in session.notifications if e["subscriptionId"] == fresh["subscriptionId"]]
            )
            == 1
        )  # No periodic same-stage stdout broadcast.
        other_final = session.terminal(project, second["jobId"])
        assert other_final["state"] == "succeeded"
        decision = session.call("job.cancel", {"projectId": project, "jobId": first["jobId"]})
        assert decision["disposition"] == "accepted"
        assert decision["state"] == "cancelling"
        cancelled = session.terminal(project, first["jobId"])
        assert cancelled["state"] == "cancelled"
        assert cancelled["stateVersion"] == 4
        assert session.job(project, second["jobId"]) == other_final
        assert (
            sum(e["subscriptionId"] == old["subscriptionId"] for e in session.notifications)
            == old_count
        )
        fresh_events = [
            e for e in session.notifications if e["subscriptionId"] == fresh["subscriptionId"]
        ]
        assert_route(fresh_events, first_current, fresh, session.session)
        assert [
            e["data"]["progress"]["stage"] for e in fresh_events if e["event"] == "job.progress"
        ] == ["computing", "reconciling"]
        assert fresh_events[-1]["event"] == "job.state"
        assert fresh_events[-1]["data"] == cancelled
        second_events = [
            e for e in session.notifications if e["subscriptionId"] == second_sub["subscriptionId"]
        ]
        assert all(e["jobId"] == second["jobId"] for e in second_events)
        assert all(
            e["data"]["stateVersion"] == 2 for e in second_events if e["event"] == "job.progress"
        )
        count = len(session.notifications)
        terminal_subscription = session.call(
            "job.subscribe", {"projectId": project, "jobId": first["jobId"]}
        )
        assert terminal_subscription["seq"] == 0
        assert len(session.notifications) == count
        assert session.call("health", {})["status"] == "ok"
    finally:
        session.close()
