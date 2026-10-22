"""Record a permitted reviewer command in this reviewer's isolated runtime."""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

root = Path.cwd().resolve()
match = re.fullmatch(r"T04-s1-(zcode|minimax)-r3-5070004", root.name)
if not match or len(sys.argv) < 3 or not re.fullmatch(r"[a-z0-9-]+", sys.argv[1]):
    raise SystemExit(
        "Use this script only in the assigned review tree with a unique label and argv."
    )
reviewer = match[1]
runtime = root / "test-results" / "t04-review-runtime" / reviewer
for folder in ("raw", "metadata", "tmp", "cache/npm", "cache/uv"):
    (runtime / folder).mkdir(parents=True, exist_ok=True)
label, argv = sys.argv[1], sys.argv[2:]
raw = runtime / "raw" / f"{label}.log"
if raw.exists():
    raise SystemExit("Preserve prior evidence; choose a new label.")
env = os.environ.copy()
env.update(
    {
        "npm_config_cache": str(runtime / "cache/npm"),
        "UV_CACHE_DIR": str(runtime / "cache/uv"),
        "TMPDIR": str(runtime / "tmp"),
    }
)
started = datetime.now(UTC).isoformat()
with raw.open("xb") as output:
    result = subprocess.run(argv, cwd=root, env=env, stdout=output, stderr=subprocess.STDOUT)
payload = raw.read_bytes()
receipt = {
    "reviewer": reviewer,
    "label": label,
    "argv": argv,
    "cwd": str(root),
    "startedAt": started,
    "finishedAt": datetime.now(UTC).isoformat(),
    "exitCode": result.returncode,
    "raw": str(raw),
    "rawBytes": len(payload),
    "rawSHA256": hashlib.sha256(payload).hexdigest(),
}
(runtime / "metadata" / f"{label}.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt))
raise SystemExit(result.returncode if result.returncode >= 0 else 128 - result.returncode)
