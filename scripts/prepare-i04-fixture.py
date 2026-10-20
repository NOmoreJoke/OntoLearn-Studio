"""Prepare isolated, synthetic SQLite evidence for the explicit I04 desktop harness."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION, LIMITS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--background-rounds", type=int, default=100)
    args = parser.parse_args()
    if not 1 <= args.background_rounds <= 100:
        parser.error("background-rounds must be within the fixture workload limit")
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    database = directory / "engine.sqlite"
    with_store = JobStore(database, contract=CONTRACT)
    try:
        with_store.create_project("i04-synthetic-native")
        project = with_store.public_project("i04-synthetic-native")
        snap = with_store.project_get(project)
        confirmed = with_store.prepare_plan(
            project,
            snap["projectRevision"],
            {"definitions": [{"layer": "ontology", "id": "native-committed", "value": {}}]},
            actor=str(uuid4()),
            permission="write",
        )
        input_ = {
            "inputSnapshotId": snap["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "native-commit",
            "parametersHash": with_store.put_blob(project, {}),
            "derivedResultIds": [],
            "preparedPlanRef": confirmed["preparedPlanRef"],
        }
        job = with_store.create_job(
            project,
            str(uuid4()),
            "test.atomic",
            input_,
            confirmed["confirmationRef"],
            IMPLEMENTATION,
            LIMITS,
        )
        with_store.start_job(job["jobId"])
        # This is the actual S1 commit + receipt + job terminal transaction.
        job = with_store.commit_job(job["jobId"])
        background_input = {
            "inputSnapshotId": with_store.project_get(project)["inputSnapshotId"],
            "scope": "scenario",
            "definitionId": "native-background",
            "parametersHash": with_store.put_blob(
                project,
                {
                    "workMs": 500,
                    "maxRounds": args.background_rounds,
                    "generatePerRound": 1,
                    "consumePerRound": 0,
                },
            ),
            "derivedResultIds": [],
            "preparedPlanRef": None,
        }
        failure_input = {
            "inputSnapshotId": with_store.project_get(project)["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "native-safe-error",
            "parametersHash": with_store.put_blob(project, {"failRound": 1}),
            "derivedResultIds": [],
            "preparedPlanRef": None,
        }
        fixture = {
            "projectId": project,
            "jobIds": [job["jobId"]],
            "databasePath": str(database),
            "startRequests": [
                {
                    "projectId": project,
                    "operationId": str(uuid4()),
                    "capability": "test.rounds",
                    "input": background_input,
                    "confirmationRef": None,
                },
                {
                    "projectId": project,
                    "operationId": str(uuid4()),
                    "capability": "test.read",
                    "input": failure_input,
                    "confirmationRef": None,
                },
            ],
        }
        target = directory / "fixture.json"
        target.write_text(json.dumps(fixture, indent=2) + "\n")
        print(target, flush=True)
    finally:
        with_store.close()


if __name__ == "__main__":
    main()
