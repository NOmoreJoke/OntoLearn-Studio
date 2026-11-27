"""Run Q3 graph/CSP checks against the unique packaged desktop, preserving evidence."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    release = args.release.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    # Names are derived from the checked-in builder productName / package name.
    # A missing or ambiguous package fails; never fall back to development Electron.
    names = {
        "darwin": "OntoLearn Studio",
        "win32": "OntoLearn Studio.exe",
        "linux": "@ontolearndesktop",
    }
    name = names[sys.platform]
    candidates = []
    for asar in release.rglob("app.asar"):
        resources = asar.parent
        executable = (
            resources.parent / "MacOS" / name
            if sys.platform == "darwin"
            else resources.parent / name
        )
        if executable.is_file():
            candidates.append((executable, asar))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one packaged desktop; found {len(candidates)}")
    executable, asar = candidates[0]
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node runtime unavailable")
    command = [
        node,
        str(Path("node_modules/@playwright/test/cli.js").resolve(strict=True)),
        "test",
        "tests/e2e/q3-packaged-graph.spec.ts",
        "--workers=1",
        "--reporter=list,github,json",
        f"--output={output / 'test-results'}",
    ]
    env = os.environ.copy()
    for key in ("ELECTRON_RUN_AS_NODE", "ELECTRON_RENDERER_URL", "I04_TEST_FIXTURE"):
        env.pop(key, None)
    env.update(
        ONTOLEARN_PACKAGED_EXECUTABLE=str(executable),
        PLAYWRIGHT_JSON_OUTPUT_FILE=str(output / "report.json"),
    )
    record = {
        "executable": str(executable),
        "executableSha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "appAsar": str(asar),
        "appAsarSha256": hashlib.sha256(asar.read_bytes()).hexdigest(),
        "platform": sys.platform,
        "command": command,
    }
    (output / "launch.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    try:
        result = subprocess.run(command, env=env, timeout=120)
        (output / "exit.json").write_text(
            json.dumps({"exitCode": result.returncode}) + "\n", encoding="utf-8"
        )
        if result.returncode:
            raise SystemExit(result.returncode)
    except subprocess.TimeoutExpired:
        (output / "exit.json").write_text('{"timeoutSeconds":120}\n', encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
