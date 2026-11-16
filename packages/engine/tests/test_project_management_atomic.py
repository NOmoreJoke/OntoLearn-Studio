"""Outer Store.commit atomicity, including real process exits, without RPC hooks."""

import json
import sqlite3
import subprocess
import sys
from uuid import uuid4

import pytest
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project import management
from ontolearn_engine.project.format3 import logical_hash
from ontolearn_engine.project.project_host import ReadLimits
from ontolearn_engine.resources import CONTRACT
from ontolearn_engine.storage import digest


def uid():
    return str(uuid4())


def frozen(path):
    with sqlite3.connect(path) as db:
        return logical_hash(db)


@pytest.mark.parametrize(
    "action,phase",
    [
        ({"kind": "rename", "name": "new"}, "application_claim"),
        ({"kind": "rename", "name": "new"}, "management_receipt"),
        ({"kind": "copy-current", "name": "copy"}, "management_copy:projects"),
        ({"kind": "copy-current", "name": "copy"}, "management_copy:operation_claims"),
        ({"kind": "copy-current", "name": "copy"}, "management_copy:app_receipts"),
        ({"kind": "copy-current", "name": "copy"}, "management_validated"),
        ({"kind": "trash"}, "management_receipt"),
        ({"kind": "trash"}, "before_commit"),
        ({"kind": "trash"}, "after_commit"),
    ],
)
@pytest.mark.parametrize("crash", [False, True])
def test_management_outer_transaction_all_or_nothing(tmp_path, action, phase, crash):
    path = tmp_path / "atomic.sqlite"
    store = JobStore(path, contract=CONTRACT, target_format=3)
    project = uid()
    store.create_project(project)
    store.public_project(project)
    document, seed = management.document(store, project, action)
    request = {
        "projectId": project,
        "operationId": uid(),
        "confirmationRef": uid(),
        "documentHash": digest({"action": action, "document": document}),
    }
    core = {
        "request": request,
        "action": action,
        "document": document,
        "seed": seed,
        "origin": {"hostClientId": uid(), "engineSessionId": uid(), "permission": "library.create"},
    }
    before = frozen(path)
    if crash:
        store.close()
        payload = tmp_path / "input.json"
        payload.write_text(json.dumps(core))
        script = """
import json,os,sys
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.project.project_host import ReadLimits
from ontolearn_engine.resources import CONTRACT
value=json.load(open(sys.argv[2]))
value['readerLimits']=ReadLimits()
def hook(phase):
 if phase == sys.argv[3]: os._exit(72)
store=JobStore(sys.argv[1],contract=CONTRACT,target_format=3)
store.commit(None,None,value['request']['operationId'],None,management=value,hook=hook)
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), str(payload), phase],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 72, result.stderr
    else:

        def hook(current):
            if current == phase:
                raise RuntimeError("atomic injection")

        with pytest.raises(RuntimeError):
            store.commit(
                None,
                None,
                request["operationId"],
                None,
                management={**core, "readerLimits": ReadLimits()},
                hook=hook,
            )
        store.close()
    if phase != "after_commit":
        assert frozen(path) == before
    reopened = JobStore(path, contract=CONTRACT, target_format=3)
    answer = management.operation_get(reopened, project, request["operationId"], digest(request))
    assert answer["state"] == ("applied" if phase == "after_commit" else "not-found")
    reopened.close()
