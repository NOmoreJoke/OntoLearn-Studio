"""Owned synthetic Store fixture only; production reader never opens SQLite directly."""

import json
import sys
import time
from pathlib import Path
from uuid import uuid4

from ontolearn_engine import worker
from ontolearn_engine.job_store import JobFault, JobStore
from ontolearn_engine.resources import CONTRACT

action, database, raw = sys.argv[1:]
data = json.loads(raw)
for attempt in range(40):
    try:
        store = JobStore(database, contract=CONTRACT)
        break
    except JobFault as error:
        if action not in {"collect", "inspect"} or error.code != "STORAGE_BUSY" or attempt == 39:
            raise
        # Only used after the test has explicitly stopped its owned coordinator.
        time.sleep(0.05)
try:
    if action == "prepare":
        for name in ("i06-primary", "i06-other"):
            store.create_project(name)
        project = store.public_project("i06-primary")
        other = store.public_project("i06-other")
        snapshot = store.project_get(project)
        parameters = store.put_blob(project, {"rows": data})
        extra_parameters = store.put_blob(
            project,
            {
                "rows": [
                    {
                        "rowId": str(uuid4()),
                        "ordinal": 0,
                        "cells": ["OTHER_SYNTHETIC_SCOPE"],
                    }
                ]
            },
        )
        plan = store.prepare_plan(
            project,
            snapshot["projectRevision"],
            {
                "definitions": [
                    {
                        "layer": "rule",
                        "id": "i06-local-save",
                        "value": {"synthetic": True},
                    }
                ]
            },
            actor=str(uuid4()),
            permission="write",
        )
        print(
            json.dumps(
                {
                    "projectId": project,
                    "otherProjectId": other,
                    "workerFile": str(Path(worker.__file__).resolve()),
                    "extraParametersHash": extra_parameters,
                    "atomicConfirmationRef": plan["confirmationRef"],
                    "atomicPreparedPlanRef": plan["preparedPlanRef"],
                    "input": {
                        "inputSnapshotId": snapshot["inputSnapshotId"],
                        "scope": "asserted",
                        "definitionId": "i06-material-probe",
                        "parametersHash": parameters,
                        "derivedResultIds": [],
                        "preparedPlanRef": None,
                    },
                }
            )
        )
    elif action == "collect":
        print(json.dumps({"evicted": store.collect_cache()}))
    elif action == "inspect":
        internal = store._project(data["projectId"])
        print(
            json.dumps(
                {
                    "revision": store.revision(internal),
                    "snapshot": store.load_snapshot(store.snapshot(internal)),
                }
            )
        )
    else:
        raise ValueError("INVALID_FIXTURE_ACTION")
finally:
    store.close()
