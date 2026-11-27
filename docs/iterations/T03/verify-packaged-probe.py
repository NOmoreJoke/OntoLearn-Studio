"""Verify only the fixed T03 CLI probe inside an already built application directory."""

import hashlib
import json
import platform
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[3]
engine = root / "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine"
expected = json.loads((root / "docs/reviews/T03/project-probe-first.json").read_text())
result = subprocess.run(
    [str(engine), "--mapping-probe"], input=b"", capture_output=True, timeout=30, check=False
)
(root / "docs/reviews/T03/product-package-probe-first-stdout.json").write_bytes(result.stdout)
(root / "docs/reviews/T03/product-package-probe-first-stderr.txt").write_bytes(result.stderr)
if result.returncode != 0 or result.stderr:
    raise RuntimeError(f"PACKAGED_PROBE_FAILED_EXIT_{result.returncode}")
if json.loads(result.stdout) != expected:
    raise RuntimeError("PACKAGED_PROBE_RESULT_MISMATCH")
invalid = subprocess.run(
    [str(engine), "--mapping-probe", "untrusted-input.xlsx"],
    input=b"",
    capture_output=True,
    timeout=10,
    check=False,
)
if (
    invalid.returncode != 2
    or invalid.stdout
    or invalid.stderr != b"MAPPING_PROBE_INVALID_ARGUMENTS\n"
):
    raise RuntimeError("PACKAGED_PROBE_ARGUMENT_REFUSAL_FAILED")
internal = engine.parent / "_internal"
license_evidence = json.loads(
    (root / "docs/reviews/T03/project-dependency-verification.json").read_text()
)
licenses = {}
for _name, record in license_evidence["licenseFiles"].items():
    for relative, expected_sha in record["files"].items():
        actual = hashlib.sha256((internal / relative).read_bytes()).hexdigest()
        if actual != expected_sha:
            raise RuntimeError("PACKAGED_LICENSE_MISMATCH")
        licenses[relative] = actual
source_lock = hashlib.sha256((root / "uv.lock").read_bytes()).hexdigest()
packaged_lock = hashlib.sha256((internal / "provenance/uv.lock").read_bytes()).hexdigest()
if source_lock != packaged_lock:
    raise RuntimeError("PACKAGED_LOCK_MISMATCH")
evidence = {
    "scope": "actual unsigned macOS development app resources CLI, not GUI or target platforms",
    "command": [str(engine), "--mapping-probe"],
    "exitCode": result.returncode,
    "expectedAndPackagedResultsEqual": True,
    "cases": expected["cases"],
    "versions": expected["versions"],
    "executableSha256": hashlib.sha256(engine.read_bytes()).hexdigest(),
    "sourceAndPackagedLockSha256": source_lock,
    "licenseFiles": licenses,
    "extraArgumentsRefused": True,
    "platform": platform.platform(),
    "architecture": platform.machine(),
    "guiStarted": False,
    "businessCapabilityEnabled": False,
    "targetCleanDeviceAcceptance": False,
}
(root / "docs/reviews/T03/product-package-verification.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps(evidence, ensure_ascii=False))
