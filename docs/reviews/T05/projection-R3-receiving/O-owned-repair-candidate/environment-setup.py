"""Record only authorized locked, worktree-local environment preparation."""

import hashlib
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent / "environment-setup"
OUT.mkdir(exist_ok=False)
LOCKS = ("package-lock.json", "uv.lock")


def identities():
    return {
        name: {
            "bytes": len((ROOT / name).read_bytes()),
            "sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest(),
        }
        for name in LOCKS
    }


before = identities()


def run(name, argv):
    folder = OUT / name
    folder.mkdir()
    (folder / "tmp").mkdir()
    env = os.environ.copy()
    explicit = {"TMPDIR": str(folder / "tmp"), "PYTHONDONTWRITEBYTECODE": "1"}
    if name == "npm":
        explicit["npm_config_cache"] = str(folder / "cache")
    else:
        explicit.update(
            UV_CACHE_DIR=str(folder / "cache"), UV_PYTHON_DOWNLOADS="never", UV_NO_PROGRESS="1"
        )
    env.update(explicit)
    record = {
        "argv": argv,
        "cwd": str(ROOT),
        "explicitEnvironment": explicit,
        "lockBefore": before,
        "startedUtc": datetime.now(UTC).isoformat(),
        "scope": "exact authorized own worktree locked dependency preparation",
    }
    (folder / "invocation.json").write_text(json.dumps(record, indent=2) + "\n")
    with (folder / "stdout.raw").open("wb") as stdout, (folder / "stderr.raw").open("wb") as stderr:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    record.update(
        exit=completed.returncode,
        finishedUtc=datetime.now(UTC).isoformat(),
        lockAfter=identities(),
    )
    record["streams"] = {
        n: {
            "bytes": len((folder / n).read_bytes()),
            "sha256": hashlib.sha256((folder / n).read_bytes()).hexdigest(),
        }
        for n in ("stdout.raw", "stderr.raw")
    }
    record["locksUnchanged"] = record["lockAfter"] == before
    (folder / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                "setup": name,
                "exit": completed.returncode,
                "locksUnchanged": record["locksUnchanged"],
            }
        ),
        flush=True,
    )
    return record


with ThreadPoolExecutor(max_workers=2) as pool:
    jobs = [
        pool.submit(run, "npm", ["/usr/local/bin/npm", "ci"]),
        pool.submit(
            run,
            "uv",
            [
                "/Users/kyle/.local/bin/uv",
                "sync",
                "--frozen",
                "--python",
                "/opt/homebrew/bin/python3.12",
            ],
        ),
    ]
    results = [job.result() for job in jobs]
(OUT / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
raise SystemExit(0 if all(r["exit"] == 0 and r["locksUnchanged"] for r in results) else 1)
