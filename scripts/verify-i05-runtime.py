"""Portable real bundled semantic CLI/stdio verification; never starts Electron."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    executable = args.release.resolve(strict=True)
    if executable.is_dir():
        matches = [
            p
            for name in ("ontolearn-engine", "ontolearn-engine.exe")
            for p in executable.rglob(name)
            if p.is_file() and p.parent.name == "engine"
        ]
        assert len(matches) == 1
        executable = matches[0]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    results = {}
    for runtime, command in [
        ("source", [sys.executable, "-I", "-m", "ontolearn_engine.semantic_probe"]),
        ("packaged", [str(executable), "--semantic-probe"]),
    ]:
        process = subprocess.run([*command, "--mode", "suite"], capture_output=True, timeout=60)
        (output / f"{runtime}-suite.stdout").write_bytes(process.stdout)
        (output / f"{runtime}-suite.stderr").write_bytes(process.stderr)
        assert process.returncode == 0 and process.stderr == b""
        results[runtime] = json.loads(process.stdout)
    assert results["source"] == results["packaged"]
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "packages/engine/tests/test_semantic_runtime.py::test_actual_stdio_source_or_packaged_jobs_persist_all_three_semantic_outputs",
            "packages/engine/tests/test_semantic_lexical_runtime.py::test_actual_stdio_source_or_packaged_lexical_identity",
        ],
        env=os.environ | {"ONTOLEARN_TEST_ENGINE": str(executable)},
        capture_output=True,
        timeout=60,
    )
    (output / "real-stdio.stdout").write_bytes(process.stdout)
    (output / "real-stdio.stderr").write_bytes(process.stderr)
    assert process.returncode == 0
    inventory = executable.parent / "_internal/i05-inventory"
    manifest = json.loads((inventory / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["uvLockSha256"] == sha(Path("uv.lock"))
    assert sha(inventory / "CPython-LICENSE.txt") == manifest["pythonLicenseSha256"]
    for package in manifest["packages"]:
        for license_ in package["licenseFiles"]:
            assert sha(inventory / license_["path"]) == license_["sha256"]
    if manifest["nativeLicenseProvenanceMatched"]:
        provenance = json.loads(
            (inventory / "native-runtime/provenance.json").read_text(encoding="utf-8")
        )
        assert (
            sha(inventory / "native-runtime/upstream-PYTHON.json.raw")
            == provenance["metadataSha256"]
        )
        for license_ in provenance["licenseFiles"]:
            assert sha(inventory / "native-runtime" / license_["path"]) == license_["sha256"]
    summary = {
        "status": "passed",
        "executableSha256": sha(executable),
        "suiteFullOutputParity": True,
        "realStdioExit": process.returncode,
        "nativeLicenseProvenanceMatched": manifest["nativeLicenseProvenanceMatched"],
        "nativeLicenseScope": manifest["nativeLicenseScope"],
        "limits": (
            "Actual bundled CLI/stdio; no Electron, signing, clean-device "
            "or target-platform claim. "
            "Unmatched native runtime remains pending."
        ),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
