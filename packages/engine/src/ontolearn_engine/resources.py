"""Load the single contract source, both from checkout and explicit frozen resources."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = (
    Path(sys._MEIPASS) / "contracts"
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parents[3] / "contracts"
)
SPEC = importlib.util.spec_from_file_location(
    "ontolearn_contract_v2", ROOT / "python/contract_v2.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("CONTRACT_UNAVAILABLE")
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
REGISTRY_BYTES = (ROOT / "v2/registry.json").read_bytes()
REGISTRY_HASH = hashlib.sha256(REGISTRY_BYTES).hexdigest()
LOCK_FILE = (
    Path(sys._MEIPASS) / "provenance/uv.lock"
    if getattr(sys, "frozen", False)
    else ROOT.parents[1] / "uv.lock"
)
IMPLEMENTATION = {
    "executionSemanticsVersion": "i04-infrastructure-v1",
    "engineVersion": "0.1.0",
    "dependencyLockHash": hashlib.sha256(LOCK_FILE.read_bytes()).hexdigest(),
}
LIMITS = {
    "startupMs": 10000,
    "handshakeMs": 5000,
    "requestMs": 5000,
    "totalMs": 120000,
    "heartbeatMs": 10000,
    "cancelGraceMs": 5000,
    "maxFrameBytes": 262144,
    "maxQueuedJobs": 32,
    "maxConcurrentJobs": 2,
    "maxPageItems": 200,
    "maxPageBytes": 131072,
    "maxWorkerMemoryBytes": 536870912,
}


def resource_manifest() -> dict:
    paths = [ROOT / "python/contract_v2.py", *sorted((ROOT / "v2").glob("*.json"))]
    return {
        "registryHash": REGISTRY_HASH,
        "resources": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths
        },
        "implementation": IMPLEMENTATION,
        "frozen": bool(getattr(sys, "frozen", False)),
    }


def safe_error(code: str, params: dict | None = None) -> dict:
    definition = CONTRACT.ERROR_CATALOG["codes"].get(code)
    if definition is None:
        code = "INTERNAL_ERROR"
        definition = CONTRACT.ERROR_CATALOG["codes"][code]
        params = {}
    value = {
        "code": code,
        "messageKey": definition["messageKey"],
        "params": params or {},
        "retryable": definition["retryable"],
    }
    if not CONTRACT.validate("error", value):
        return safe_error("INTERNAL_ERROR")
    return value


def main() -> None:
    print(json.dumps(resource_manifest(), separators=(",", ":")), flush=True)
