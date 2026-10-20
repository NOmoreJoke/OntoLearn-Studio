"""Verify bundled raw protocol resources and run the same real-runtime test inputs."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from ontolearn_engine.resources import ROOT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    executable = args.executable.resolve(strict=True)
    if executable.is_dir():
        candidates = [
            path
            for name in ("ontolearn-engine", "ontolearn-engine.exe")
            for path in executable.rglob(name)
            if path.is_file() and path.parent.name == "engine"
        ]
        assert len(candidates) == 1, "Expected exactly one packaged engine in release directory"
        executable = candidates[0]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="i04-bundled-cwd-") as directory:
        manifest_process = subprocess.run(
            [str(executable), "--protocol-resources"],
            cwd=directory,
            capture_output=True,
            timeout=30,
            check=True,
        )
        assert manifest_process.stderr == b""
        manifest = json.loads(manifest_process.stdout)
        expected = {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [ROOT / "python/contract_v2.py", *sorted((ROOT / "v2").glob("*.json"))]
        }
        assert manifest["frozen"] is True
        assert manifest["resources"] == expected
        contract_process = subprocess.run(
            [str(executable), "--contract-probe"],
            cwd=directory,
            capture_output=True,
            timeout=30,
            check=True,
        )
        assert contract_process.stderr == b""
        contract = json.loads(contract_process.stdout)
        assert contract["status"] == "passed"
    (output / "resources.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "common-examples.json").write_text(json.dumps(contract, indent=2) + "\n")
    env = os.environ | {"ONTOLEARN_TEST_ENGINE": str(executable)}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "packages/engine/tests/test_resident_runtime.py",
            "packages/engine/tests/test_worker_parent.py",
            "packages/engine/tests/test_worker_owner_bootstrap.py::test_actual_worker_refuses_work_before_a_valid_owner_is_established",
            "-q",
        ],
        env=env,
        capture_output=True,
        timeout=90,
    )
    (output / "runtime.stdout").write_bytes(result.stdout)
    (output / "runtime.stderr").write_bytes(result.stderr)
    (output / "runtime.exit").write_text(str(result.returncode) + "\n")
    if result.returncode:
        raise SystemExit(result.returncode)
    print(
        json.dumps(
            {
                "status": "passed",
                "executable": str(executable),
                "commonExamples": contract["counts"],
                "runtimeExit": result.returncode,
            }
        )
    )


if __name__ == "__main__":
    main()
