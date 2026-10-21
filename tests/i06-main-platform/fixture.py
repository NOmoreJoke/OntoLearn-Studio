"""Independent Linux synthetic fixture; real coordinator owns and runs every test.read worker."""

import json
import os
import selectors
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT, IMPLEMENTATION


class Client:
    def __init__(self, database, project, directory):
        environment = {key: os.environ[key] for key in ("HOME", "LANG") if key in os.environ}
        environment.update(
            ONTOLEARN_DB_PATH=str(database),
            ONTOLEARN_ALLOWED_PROJECTS=json.dumps([project]),
            ONTOLEARN_TEST_MODE="1",
        )
        self.errors = (directory / "prepare-coordinator.stderr.log").open("wb")
        self.child = subprocess.Popen(
            [sys.executable, "-I", "-m", "ontolearn_engine"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self.errors,
            env=environment,
        )
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.child.stdout, selectors.EVENT_READ)
        self.session = None
        try:
            hello = self.request("hello", {"supportedVersions": [2], "clientId": str(uuid4())})
        except Exception:
            self.close()
            raise
        self.session = hello["engineSessionId"]
        self.hello = hello

    def request(self, method, parameters):
        identity = str(uuid4())
        request = {
            "kind": "request",
            "id": identity,
            "protocolVersion": 2,
            "engineSessionId": self.session,
            "method": method,
            "params": parameters,
        }
        self.child.stdin.write(json.dumps(request).encode() + b"\n")
        self.child.stdin.flush()
        if not self.selector.select(10):
            raise RuntimeError("PREPARE_RPC_DEADLINE")
        response = json.loads(self.child.stdout.readline())
        if response.get("id") != identity or not response.get("ok"):
            raise RuntimeError("PREPARE_RPC_REJECTED")
        return response["result"]

    def close(self):
        self.child.stdin.close()
        self.child.wait(timeout=10)
        self.selector.close()
        self.errors.close()


def prepare(directory, mode):
    directory.mkdir(parents=True, exist_ok=False)
    database = directory / "engine.sqlite"
    store = JobStore(database, contract=CONTRACT)
    try:
        store.create_project("i06-main-synthetic")
        project = store.public_project("i06-main-synthetic")
        snapshot = store.project_get(project)
        rows = [
            {
                "rowId": str(uuid4()),
                "ordinal": 854736291 + index,
                "cells": [
                    "I06_FINITE_FIELDS",
                    f"PUBLIC_VALUE_{index}",
                    f"PRIVATE_VALUE_SENTINEL_{index}",
                    f"PRIVATE_DERIVED_SENTINEL_{index}",
                ],
            }
            for index in range(3)
        ]
        parameters = store.put_blob(project, {"rows": rows, "workMs": 10000})
        input_ = {
            "inputSnapshotId": snapshot["inputSnapshotId"],
            "scope": "asserted",
            "definitionId": "i06-material-probe",
            "parametersHash": parameters,
            "derivedResultIds": [],
            "preparedPlanRef": None,
        }
        plan = store.prepare_plan(
            project,
            snapshot["projectRevision"],
            {
                "definitions": [
                    {"layer": "rule", "id": "i06-main-local-save", "value": {"synthetic": True}}
                ]
            },
            actor=str(uuid4()),
            permission="write",
        )
        atomic = {
            "projectId": project,
            "operationId": str(uuid4()),
            "capability": "test.atomic",
            "input": {
                **input_,
                "definitionId": "i06-main-local-save",
                "parametersHash": store.put_blob(
                    project, {"workMs": 10000 if mode == "audit-save" else 1000}
                ),
                "preparedPlanRef": plan["preparedPlanRef"],
            },
            "confirmationRef": plan["confirmationRef"],
        }
    finally:
        store.close()
    fixture = {"projectId": project, "jobIds": [], "databasePath": str(database)}
    evidence = {
        "projectId": project,
        "input": input_,
        "atomic": atomic,
        "implementation": IMPLEMENTATION,
    }
    if mode in {"fields", "audit-save"}:
        client = Client(database, project, directory)
        try:
            job = client.request(
                "job.create",
                {
                    "projectId": project,
                    "operationId": str(uuid4()),
                    "capability": "test.read",
                    "input": input_,
                    "confirmationRef": None,
                },
            )
            deadline = time.monotonic() + 25
            while True:
                current = client.request("job.get", {"projectId": project, "jobId": job["jobId"]})
                if current["state"] == "succeeded":
                    break
                if current["state"] not in {"queued", "running"} or time.monotonic() > deadline:
                    raise RuntimeError("PREPARE_REAL_WORKER_FAILED")
                time.sleep(0.03)
            fixture["jobIds"] = [job["jobId"]]
            fixture["modelFieldPolicy"] = "i06-finite-probe-v1"
            evidence.update(firstJob=current, hello=client.hello)
        finally:
            client.close()  # Release writer lease before the real app starts.
        second = {
            **fixture,
            "startRequests": [
                {
                    "projectId": project,
                    "operationId": str(uuid4()),
                    "capability": "test.read",
                    "input": input_,
                    "confirmationRef": None,
                }
            ],
        }
        (directory / "second-fixture.json").write_text(json.dumps(second) + "\n")
        if mode == "audit-save":
            fixture["startRequests"] = [atomic]
    elif mode == "atomic":
        fixture["startRequests"] = [atomic]
    else:
        raise RuntimeError("UNKNOWN_PRIVATE_FIXTURE_MODE")
    (directory / "fixture.json").write_text(json.dumps(fixture) + "\n")
    (directory / "fixture-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    prepare(Path(sys.argv[1]), sys.argv[2])
