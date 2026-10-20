"""Published pagination range and bounded session identity lifetime."""

from uuid import uuid4

import pytest
from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.protocol import ProtocolFault
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION, LIMITS


def call(coordinator, method, params):
    return coordinator.request(
        {
            "kind": "request",
            "id": str(uuid4()),
            "protocolVersion": 2,
            "engineSessionId": coordinator.session,
            "method": method,
            "params": params,
        }
    )


def hello(coordinator):
    return call(coordinator, "hello", {"supportedVersions": [2], "clientId": str(uuid4())})


def test_default_result_page_supports_published_two_hundred_row_range(tmp_path):
    store = JobStore(tmp_path / "page-limits.sqlite", contract=CONTRACT)
    try:
        store.create_project("pagination")
        project = store.public_project("pagination")
        job = store.create_job(
            project,
            str(uuid4()),
            "test.read",
            {
                "inputSnapshotId": store.project_get(project)["inputSnapshotId"],
                "scope": "asserted",
                "definitionId": "page-boundary",
                "parametersHash": store.put_blob(project, {}),
                "derivedResultIds": [],
                "preparedPlanRef": None,
            },
            None,
            IMPLEMENTATION,
            LIMITS,
        )
        store.start_job(job["jobId"])
        rows = [{"rowId": str(uuid4()), "ordinal": i, "cells": [i]} for i in range(210)]
        job = store.finish_read_job(job["jobId"], rows)
        result = store.result_get(project, job["resultRef"]["resultId"])
        binding = {
            "projectId": project,
            "resultId": result["resultId"],
            "inputSnapshotId": result["inputSnapshotId"],
            "scope": result["scope"],
            "parametersHash": result["parametersHash"],
            "order": "ordinal+rowId:asc",
        }
        coordinator = Coordinator(store, allowed_projects={project})
        assert hello(coordinator)["result"]["limits"]["maxPageItems"] == 200
        first = call(
            coordinator, "result.page", {"binding": binding, "pageSize": 200, "cursor": None}
        )
        assert first["ok"] and first["result"]["rows"] == rows[:200]
        token = first["result"]["nextCursor"]
        assert token is not None
        second = call(
            coordinator, "result.page", {"binding": binding, "pageSize": 200, "cursor": token}
        )
        assert second["ok"] and second["result"]["rows"] == rows[200:]
        assert second["result"]["nextCursor"] is None
        assert (
            call(coordinator, "result.page", {"binding": binding, "pageSize": 201, "cursor": None})[
                "error"
            ]["code"]
            == "INVALID_REQUEST"
        )
        limited = Coordinator(store, allowed_projects={project}, limits={"maxPageItems": 100})
        assert hello(limited)["result"]["limits"]["maxPageItems"] == 100
        assert call(limited, "result.page", {"binding": binding, "pageSize": 101, "cursor": None})[
            "error"
        ] == {
            "code": "RESOURCE_LIMIT",
            "messageKey": "resource.limitExceeded",
            "params": {"resource": "page"},
            "retryable": False,
        }
    finally:
        store.close()


def test_session_keeps_all_request_identities_until_its_explicit_budget():
    coordinator = Coordinator(None)
    assert hello(coordinator)["ok"]
    session = coordinator.session
    # The handshake consumes one of 65536 identity slots. No eviction can make
    # an earlier request replay valid within the same session.
    for _ in range(65535):
        assert call(coordinator, "session.ping", {"nonce": str(uuid4())})["ok"]
    assert len(coordinator.seen) == 65536 and coordinator.session == session
    with pytest.raises(ProtocolFault):
        call(coordinator, "session.ping", {"nonce": str(uuid4())})
    assert len(coordinator.seen) == 65536


def test_request_replay_is_rejected_before_session_budget():
    coordinator = Coordinator(None)
    assert hello(coordinator)["ok"]
    identity = next(iter(coordinator.seen))
    with pytest.raises(ProtocolFault):
        coordinator.request({"id": identity, "method": "health"})
    assert len(coordinator.seen) == 1
