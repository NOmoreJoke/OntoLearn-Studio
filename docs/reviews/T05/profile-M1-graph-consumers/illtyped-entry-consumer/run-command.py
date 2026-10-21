"""Run an exact argv with separate streams and immutable per-attempt metadata."""

import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

tag, cwd, *argv = sys.argv[1:]
out = Path(__file__).parent / "commands" / tag
out.mkdir(parents=True, exist_ok=False)
record = {
    "argv": argv,
    "cwd": str(Path(cwd).resolve()),
    "startedUtc": datetime.datetime.now(datetime.UTC).isoformat(),
    "environment": {
        k: os.environ[k]
        for k in [
            "UV_CACHE_DIR",
            "npm_config_cache",
            "UV_PROJECT_ENVIRONMENT",
            "M1_GRAPH_OBSERVATION_DIR",
            "M1_ILLTYPED_OBSERVATION_DIR",
            "PYTHONHASHSEED",
            "PYTEST_ADDOPTS",
        ]
        if k in os.environ
    },
}
(out / "invocation.json").write_text(json.dumps(record, indent=2) + "\n")
with (out / "stdout.raw").open("wb") as stdout, (out / "stderr.raw").open("wb") as stderr:
    result = subprocess.run(argv, cwd=cwd, stdout=stdout, stderr=stderr, check=False)
record["exit"] = result.returncode
record["finishedUtc"] = datetime.datetime.now(datetime.UTC).isoformat()
record["streams"] = {}
for name in ["stdout.raw", "stderr.raw"]:
    raw = (out / name).read_bytes()
    record["streams"][name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
(out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"tag": tag, "exit": result.returncode, "record": str(out)}, ensure_ascii=False))
sys.exit(result.returncode)
