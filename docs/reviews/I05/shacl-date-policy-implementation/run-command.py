"""Capture one authorized command without replacing raw output or first failure."""

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parents[4]
label, *argv = sys.argv[1:]
assert label and "/" not in label and argv
out = Path(__file__).parent / "runs" / label
out.mkdir(parents=True, exist_ok=False)
start = datetime.datetime.now(datetime.UTC).isoformat()
tick = time.monotonic()
with (out / "stdout.raw").open("wb") as stdout, (out / "stderr.raw").open("wb") as stderr:
    result = subprocess.run(argv, cwd=root, stdout=stdout, stderr=stderr, check=False)
record = {
    "argv": argv,
    "cwd": str(root),
    "startUTC": start,
    "endUTC": datetime.datetime.now(datetime.UTC).isoformat(),
    "elapsedSeconds": time.monotonic() - tick,
    "exitCode": result.returncode,
    "environment": {
        k: os.environ[k]
        for k in [
            "PATH",
            "UV_LINK_MODE",
            "UV_NO_SYNC",
            "PYTHONHASHSEED",
            "I05_SHACL_DATE_EVIDENCE_DIR",
            "I05_SHACL_INTEGER_EVIDENCE_DIR",
        ]
        if k in os.environ
    },
}
(out / "command.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(
    json.dumps(
        {"run": label, "exitCode": result.returncode, "elapsedSeconds": record["elapsedSeconds"]}
    )
)
sys.exit(result.returncode)
