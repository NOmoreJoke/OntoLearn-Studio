"""Admission and negotiated budgets use the same real JobStore, never a mock."""

from uuid import uuid4

from ontolearn_engine.coordinator import Coordinator
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT


def test_queue_full_never_claims_new_operation_but_existing_claim_is_idempotent(tmp_path):
    store = JobStore(tmp_path / "bounds.sqlite", contract=CONTRACT)
    try:
        store.create_project("bounds")
        project = store.public_project("bounds")
        coordinator = Coordinator(
            store,
            test_mode=True,
            allowed_projects={project},
            limits={"maxQueuedJobs": 1, "maxPageItems": 1},
        )

        def call(method, params):
            return coordinator.request(
                {
                    "kind": "request",
                    "protocolVersion": 2,
                    "id": str(uuid4()),
                    "engineSessionId": coordinator.session,
                    "method": method,
                    "params": params,
                }
            )

        assert call("hello", {"supportedVersions": [2], "clientId": str(uuid4())})["ok"]
        params = {
            "projectId": project,
            "operationId": str(uuid4()),
            "capability": "test.read",
            "input": {
                "inputSnapshotId": store.project_get(project)["inputSnapshotId"],
                "scope": "asserted",
                "definitionId": "probe",
                "parametersHash": store.put_blob(project, {}),
                "derivedResultIds": [],
                "preparedPlanRef": None,
            },
            "confirmationRef": None,
        }
        first = call("job.create", params)
        assert first["ok"]
        second = call("job.create", params)
        assert second["result"]["jobId"] == first["result"]["jobId"]
        next_operation = str(uuid4())
        assert (
            call("job.create", params | {"operationId": next_operation})["error"]["code"]
            == "QUEUE_FULL"
        )
        assert not store.has_operation_claim(next_operation)
        page = call(
            "job.list",
            {
                "projectId": project,
                "filter": "all",
                "pageSize": 2,
                "listSnapshotId": None,
                "cursor": None,
            },
        )
        assert page["error"]["code"] == "RESOURCE_LIMIT"
        assert page["error"]["params"] == {"resource": "page"}
        assert store._db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
    finally:
        store.close()
