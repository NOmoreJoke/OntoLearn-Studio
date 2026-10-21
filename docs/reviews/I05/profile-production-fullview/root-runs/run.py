import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

label = sys.argv[1]
argv = sys.argv[2:]
here = Path(__file__).resolve().parent
r = {
    "argv": argv,
    "cwd": os.getcwd(),
    "gitHead": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "supervisorPython": sys.executable,
    "start": datetime.datetime.now(datetime.UTC).isoformat(),
    "timeoutSeconds": 600,
    "environment": {
        name: os.environ[name]
        for name in ("UV_CACHE_DIR", "I05_RESTORE_EVIDENCE_DIR")
        if name in os.environ
    },
}
start = time.monotonic()
timeout = False
try:
    p = subprocess.run(argv, capture_output=True, timeout=600)
    out, err, code = p.stdout, p.stderr, p.returncode
except subprocess.TimeoutExpired as e:
    out, err, code = e.stdout or b"", e.stderr or b"", None
    timeout = True
(here / (label + ".stdout.txt")).write_bytes(out)
(here / (label + ".stderr.txt")).write_bytes(err)
r.update(
    end=datetime.datetime.now(datetime.UTC).isoformat(),
    elapsedSeconds=time.monotonic() - start,
    exitCode=code,
    timeout=timeout,
)
(here / (label + ".json")).write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(r, ensure_ascii=False))
print(out[-6000:].decode(errors="replace"))
print(err[-3000:].decode(errors="replace"))
sys.exit(1 if timeout else code)
