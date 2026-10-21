"""A standalone actual engine session cannot accept the main-only bridge method."""

import importlib.util
import json
import selectors
import sys
from pathlib import Path
from uuid import uuid4

from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT

spec = importlib.util.spec_from_file_location(
    "i06_main_fixture", Path(__file__).with_name("fixture.py")
)
sys.dont_write_bytecode = True
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Client = module.Client

directory = Path(sys.argv[1])
directory.mkdir(parents=True, exist_ok=False)
database = directory / "engine.sqlite"
store = JobStore(database, contract=CONTRACT)
store.create_project("i06-main-method-negative")
project = store.public_project("i06-main-method-negative")
store.close()
client = Client(database, project, directory)
try:
    if "getModelAccessStatus" in client.hello["capabilities"]:
        raise RuntimeError("MAIN_METHOD_IN_ENGINE_CAPABILITIES")
    raw = {
        "kind": "request",
        "id": str(uuid4()),
        "protocolVersion": 2,
        "engineSessionId": client.session,
        "method": "getModelAccessStatus",
        "params": {},
    }
    client.child.stdin.write(json.dumps(raw).encode() + b"\n")
    client.child.stdin.flush()
    # Keep stdin open: EOF must not be the reason for termination.
    client.child.wait(timeout=8)
    if client.child.returncode != 0:
        raise RuntimeError("MAIN_METHOD_REJECTION_CRASHED_ENGINE")
    selector = selectors.DefaultSelector()
    selector.register(client.child.stdout, selectors.EVENT_READ)
    stdout = client.child.stdout.read()
    selector.close()
    if stdout:
        raise RuntimeError("MAIN_METHOD_RECEIVED_ENGINE_RESPONSE")
    if (directory / "prepare-coordinator.stderr.log").read_bytes():
        raise RuntimeError("MAIN_METHOD_REJECTION_EMITTED_UNEXPECTED_DIAGNOSTIC")
    result = {
        "result": "passed",
        "mainMethod": raw["method"],
        "stdinKeptOpenUntilExit": True,
        "exitCode": client.child.returncode,
        "additionalStdoutBytes": len(stdout),
        "advertisedCapabilities": client.hello["capabilities"],
    }
    Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n")
finally:
    client.close()
