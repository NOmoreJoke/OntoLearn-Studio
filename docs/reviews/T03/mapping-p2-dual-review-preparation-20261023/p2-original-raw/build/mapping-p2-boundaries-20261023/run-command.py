"""Fixed local validation actions for the isolated T03 P2 candidate."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "build/mapping-p2-boundaries-20261023"
ACTIONS = {
    "npm-ci": ["npm", "ci", "--ignore-scripts", "--cache", str(BASE / "cache/npm")],
    "uv-sync": ["uv", "sync", "--frozen", "--python", "/Users/kyle/.local/bin/python3.12"],
    "ruff-check": ["uv", "run", "--frozen", "ruff", "check", "packages/engine/src/ontolearn_engine/mapping/probe.py", "packages/engine/tests/test_mapping_entrypoint.py"],
    "ruff-format": ["uv", "run", "--frozen", "ruff", "format", "--check", "packages/engine/src/ontolearn_engine/mapping/probe.py", "packages/engine/tests/test_mapping_entrypoint.py"],
    "targeted": ["uv", "run", "--frozen", "pytest", "-q", "packages/engine/tests/test_mapping_entrypoint.py"],
    "verify-package": ["uv", "run", "--frozen", "python", "docs/reviews/T03/mapping-p2-boundaries-20261023/verify-packaged-boundaries.py"],
    "check": ["npm", "run", "check"],
    "sources": ["npm", "run", "verify:sources"],
    "electron-install": ["node", "node_modules/electron/install.js"],
    "package": ["npm", "run", "package:dir"],
    "source-probe": [str(ROOT / ".venv/bin/python"), "packages/engine/entrypoint.py", "--mapping-probe"],
    "source-probe-optimized": [str(ROOT / ".venv/bin/python"), "-O", "packages/engine/entrypoint.py", "--mapping-probe"],
    "package-probe": [str(ROOT / "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine"), "--mapping-probe"],
    "package-reject-path": [str(ROOT / "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine"), "--mapping-probe", "untrusted-input.xlsx"],
    "package-reject-script": [str(ROOT / "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine"), "--mapping-probe", "--script"],
    "package-reject-url": [str(ROOT / "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine"), "--mapping-probe", "https://example.invalid/"],
}
if len(sys.argv) != 2 or sys.argv[1] not in ACTIONS:
    raise SystemExit("fixed action required")
action = sys.argv[1]
run = BASE / "commands" / (datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + action + "-" + uuid.uuid4().hex[:8])
run.mkdir(parents=True, exist_ok=False)
(run / "tmp").mkdir()
env = os.environ.copy()
env.update({"UV_CACHE_DIR": str(BASE / "cache/uv"), "UV_LINK_MODE": "copy", "npm_config_cache": str(BASE / "cache/npm"), "TMPDIR": str(run / "tmp"), "ELECTRON_CACHE": str(BASE / "cache/electron"), "ELECTRON_BUILDER_CACHE": str(BASE / "cache/electron-builder"), "CSC_IDENTITY_AUTO_DISCOVERY": "false"})
env.pop("I02_HMR", None)
def identity(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
clock = time.monotonic()
with (run / "stdout.bin").open("xb") as out, (run / "stderr.bin").open("xb") as err:
    process = subprocess.Popen(ACTIONS[action], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
    before = {"action": action, "argv": ACTIONS[action], "cwd": str(ROOT), "startUtc": start, "ownedPid": process.pid, "driver": identity(Path(__file__)), "headAtStart": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(), "productAtStart": [identity(ROOT / n) for n in ("packages/engine/src/ontolearn_engine/mapping/probe.py", "packages/engine/tests/test_mapping_entrypoint.py", "docs/reviews/T03/mapping-p2-boundaries-20261023/fixed-probe-v2-expected.json", "packages/engine/entrypoint.py", "uv.lock")]}
    (run / "start.json").write_text(json.dumps(before, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"action": action, "ownedPid": process.pid, "run": str(run)}, ensure_ascii=False), flush=True)
    code = process.wait()
result = {**before, "endUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "launcherElapsedSeconds": time.monotonic() - clock, "exitCode": code, "stdout": identity(run / "stdout.bin"), "stderr": identity(run / "stderr.bin"), "noGuiRequested": True, "streamMode": "separate captured stdout/stderr", "runtimeCandidate": "HEAD303 plus explicit two authorized product paths until candidate commit"}
(run / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"action": action, "exitCode": code, "receipt": str(run / "result.json")}, ensure_ascii=False), flush=True)
raise SystemExit(code)
