"""Static file audit only. Never imports or executes the probe or its tests."""

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PREFIX = ROOT / "docs/reviews/I05/source-package-probe-source"
PACKAGE = ROOT / "packages/engine/src/ontolearn_engine"
SOURCE = "6891a5842302859a531cf82767c5a482417bc274"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    probe = PACKAGE / "semantic_source_package_probe.py"
    tree = ast.parse(probe.read_bytes())
    values = {
        item.targets[0].id: ast.literal_eval(item.value)
        for item in tree.body
        if isinstance(item, ast.Assign)
        and len(item.targets) == 1
        and isinstance(item.targets[0], ast.Name)
        and item.targets[0].id in (
            "SUPPLIER_PINS", "MANIFEST_BYTES", "MANIFEST_SHA256", "LOCK_BYTES", "LOCK_SHA256"
        )
    }
    supplier = json.loads((PREFIX / "supplier-adoption.json").read_bytes())["modules"]
    assert len(supplier) == len(values["SUPPLIER_PINS"]) == 22
    for module, relative, size, digest in values["SUPPLIER_PINS"]:
        row = next(item for item in supplier if item["module"] == module)
        raw = (PACKAGE / relative).read_bytes()
        assert row["path"] == str((PACKAGE / relative).relative_to(ROOT))
        assert (len(raw), sha(raw)) == (size, digest) == (row["bytes"], row["sha256"])
        assert raw == subprocess.check_output(["git", "show", SOURCE + ":" + row["path"]], cwd=ROOT)
        ast.parse(raw)
    resources = json.loads((PREFIX / "T01-resource-adoption.json").read_bytes())["files"]
    assert len(resources) == 4
    for row in resources:
        raw = (ROOT / row["path"]).read_bytes()
        assert (len(raw), sha(raw)) == (row["bytes"], row["sha256"])
        assert raw == subprocess.check_output(["git", "show", SOURCE + ":" + row["path"]], cwd=ROOT)
    manifest_raw = (PACKAGE / "probe_inputs/i05-source-package-parity-manifest.json").read_bytes()
    assert (len(manifest_raw), sha(manifest_raw)) == (
        values["MANIFEST_BYTES"], values["MANIFEST_SHA256"]
    )
    manifest = json.loads(manifest_raw)
    input_raw = (PACKAGE / "probe_inputs/i05-source-package-parity-inputs.json").read_bytes()
    assert (len(input_raw), sha(input_raw)) == (
        manifest["inputAsset"]["bytes"], manifest["inputAsset"]["sha256"]
    )
    inputs = json.loads(input_raw)
    assert len(inputs["observations"]) == 417 and len(inputs["datasets"]) == 320
    assert manifest["caseSets"]["full-v1"] == [item["id"] for item in inputs["observations"]]
    families = {}
    for observation in inputs["observations"]:
        raw = json.dumps(
            inputs["datasets"][observation["datasetId"]], ensure_ascii=True,
            sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("ascii")
        assert sha(raw) == observation["projectionSha256"]
        families[observation["family"]] = families.get(observation["family"], 0) + 1
    assert families == manifest["counts"]["families"]
    parsed = []
    for path in (probe, ROOT / "packages/engine/tests/test_semantic_source_package_probe.py",
                 ROOT / "scripts/generate-i05-source-package-inputs.py"):
        raw = path.read_bytes()
        node = ast.parse(raw)
        names = [item.name for item in ast.walk(node) if isinstance(item, ast.FunctionDef)
                 and item.name.startswith("test_")]
        assert len(names) == len(set(names))
        parsed.append({"path": str(path.relative_to(ROOT)), "bytes": len(raw),
                       "sha256": sha(raw), "testFunctions": len(names)})
    agents = (ROOT / "AGENTS.md").read_bytes()
    assert (len(agents), sha(agents)) == (
        15852, "78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759"
    )
    staged_agents = subprocess.check_output(["git", "diff", "--cached", "--", "AGENTS.md"], cwd=ROOT)
    assert not staged_agents
    target = sys.argv[1] if len(sys.argv) == 2 else "HEAD"
    assert len(sys.argv) in (1, 2), "one fixed Git ref only"
    target = subprocess.check_output(
        ["git", "rev-parse", "--verify", target + "^{commit}"], cwd=ROOT, text=True
    ).strip()
    base = "5f910b52c69d86a1076b2032e5d3c63e715947f3"
    diff_checks = {}
    for label, args in (
        ("baseToFixedCandidate", [base, target]),
        ("baseToCurrentTracked", [base, "--", ".", ":(exclude)AGENTS.md"]),
        ("staged", ["--cached"]),
        ("unstaged", ["--", ".", ":(exclude)AGENTS.md"]),
    ):
        result = subprocess.run(["git", "diff", "--check", *args],
                                cwd=ROOT, capture_output=True)
        diff_checks[label] = {"exit": result.returncode,
                              "stdout": result.stdout.decode("utf-8"),
                              "stderr": result.stderr.decode("utf-8")}
        assert result.returncode == 0, label + " whitespace failure"
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0")
    untracked_checks = []
    for name in filter(None, untracked):
        assert name.startswith((
            "docs/iterations/I05/source-package-probe/",
            "docs/reviews/I05/source-package-probe-source/",
        )), "untracked path outside this source-only document scope"
        result = subprocess.run(["git", "diff", "--no-index", "--check", "/dev/null", name],
                                cwd=ROOT, capture_output=True)
        assert result.returncode in (0, 1) and not result.stdout and not result.stderr, (
            "untracked whitespace failure: " + name
        )
        untracked_checks.append(name)
    required_lock = subprocess.check_output(["git", "show", SOURCE + ":uv.lock"], cwd=ROOT)
    assert (len(required_lock), sha(required_lock)) == (values["LOCK_BYTES"], values["LOCK_SHA256"])
    actual_lock = (ROOT / "uv.lock").read_bytes()
    print(json.dumps({
        "format": "i05-source-only-static-audit/1", "cwd": str(ROOT),
        "sourceCopies": 22, "resourceCopies": 4, "observations": 417, "datasets": 320,
        "projectionHashesChecked": 417, "parsedNewSources": parsed,
        "inputBytes": len(input_raw), "inputSha256": sha(input_raw),
        "manifestBytes": len(manifest_raw), "manifestSha256": sha(manifest_raw),
        "currentLock": {"bytes": len(actual_lock), "sha256": sha(actual_lock),
                        "adopted": False},
        "requiredLock": {"bytes": len(required_lock), "sha256": sha(required_lock)},
        "agentsProtected": True, "fixedCandidateRef": target,
        "diffChecks": diff_checks, "untrackedTextFilesChecked": untracked_checks,
        "productImported": False, "probeExecuted": False, "testsExecuted": False,
        "runtimeOrBuildPassed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
