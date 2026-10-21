"""Capture one authorized D1 command without overwriting earlier attempts."""

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[3]
label, *command = sys.argv[1:]
if not label or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in label):
    raise SystemExit("invalid evidence label")
if not command:
    raise SystemExit("missing command")
stdout_path = EVIDENCE / f"{label}.stdout.txt"
stderr_path = EVIDENCE / f"{label}.stderr.txt"
record_path = EVIDENCE / f"{label}.command.json"
if any(path.exists() for path in (stdout_path, stderr_path, record_path)):
    raise SystemExit("existing evidence must not be overwritten")
started = datetime.datetime.now(datetime.UTC).isoformat()
timer = time.monotonic()
environment = os.environ.copy()
environment.update(
    {
        "UV_CACHE_DIR": str(ROOT / "build/d1-uv-cache"),
        "UV_LINK_MODE": "copy",
        "UV_PYTHON_DOWNLOADS": "never",
        "PYTHONUTF8": "1",
        "CI": "1",
        "ELECTRON_SKIP_BINARY_DOWNLOAD": "1",
    }
)
with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
    result = subprocess.run(command, cwd=ROOT, env=environment, stdout=stdout, stderr=stderr)
record = {
    "command": command,
    "cwd": str(ROOT),
    "startedAtUtc": started,
    "durationSeconds": round(time.monotonic() - timer, 3),
    "exitCode": result.returncode,
    "controlledEnvironment": {
        key: environment[key]
        for key in (
            "UV_CACHE_DIR",
            "UV_LINK_MODE",
            "UV_PYTHON_DOWNLOADS",
            "PYTHONUTF8",
            "CI",
            "ELECTRON_SKIP_BINARY_DOWNLOAD",
        )
    },
    "stdout": stdout_path.name,
    "stderr": stderr_path.name,
}
record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, ensure_ascii=False))
print(stdout_path.read_text(encoding="utf-8", errors="replace")[-16000:])
print(stderr_path.read_text(encoding="utf-8", errors="replace")[-6000:])
raise SystemExit(result.returncode)
