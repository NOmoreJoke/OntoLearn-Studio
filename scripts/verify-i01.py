"""Repeatable S1 development + actual app-resource executable acceptance evidence."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from importlib.metadata import distribution
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--packaged", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
executable = args.packaged.resolve(strict=True)
root = Path(__file__).resolve().parents[1]
environment = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
environment["PATH"] = "/usr/bin:/bin"
observations = []
for runtime in ("development", "packaged"):
    for scale in (1, 10):
        for trial in range(3):
            command = (
                [sys.executable, "-m", "ontolearn_engine.storage_probe"]
                if runtime == "development"
                else [str(executable), "--storage-probe"]
            )
            command += ["--scale", str(scale), "--trial", str(trial)]
            start = time.perf_counter_ns()
            result = subprocess.run(
                command, env=environment, capture_output=True, text=True, timeout=60, check=True
            )
            observation = json.loads(result.stdout)
            observation["runtime"] = runtime
            observation["processElapsedNs"] = time.perf_counter_ns() - start
            observation["stderr"] = result.stderr
            assert observation["result"] == observation["expected"]
            assert observation["triples"] == 18 * scale
            observations.append(observation)
            (args.output / f"{runtime}-{scale}x-{trial}.json").write_text(
                json.dumps(observation, ensure_ascii=False, indent=2) + "\n"
            )
for scale in (1, 10):
    group = [r for r in observations if r["scale"] == scale]
    for key in ("inputSha256", "querySha256", "result", "snapshotId"):
        assert all(r[key] == group[0][key] for r in group)
health = subprocess.run(
    [str(executable)],
    env=environment,
    input=json.dumps(
        {
            "id": "I01-packaged-health",
            "method": "health",
            "protocolVersion": 1,
        }
    )
    + "\n",
    capture_output=True,
    text=True,
    timeout=15,
    check=True,
)
health_result = json.loads(health.stdout)
assert health_result["ok"] is True
assert health_result["result"]["capabilities"] == ["health"]
# Package the data contract as well as actual RDFLib plugin/metadata resources.
package_dir = executable.parent
files = [p for p in package_dir.rglob("*") if p.is_file()]
assert any(p.name == "invalidation-v1.json" for p in files)
licenses = []
for name in ("rdflib", "pyparsing"):
    dist = distribution(name)
    license_files = [p for p in dist.files if "LICENSE" in str(p).upper()]
    for path in license_files:
        content = Path(dist.locate_file(path)).read_bytes()
        assert any(p.name == "LICENSE" and p.read_bytes() == content for p in files)
    licenses.append(
        {
            "name": name,
            "version": dist.version,
            "license": dist.metadata.get("License-Expression") or dist.metadata.get("License"),
            "files": [str(p) for p in license_files],
        }
    )
manifest = {
    "host": platform.platform(),
    "machine": platform.machine(),
    "executable": str(executable),
    "executableSha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
    "engineDirectoryBytes": sum(p.stat().st_size for p in files),
    "fileCount": len(files),
    "health": health_result,
    "licenses": licenses,
    "uvLockSha256": hashlib.sha256((root / "uv.lock").read_bytes()).hexdigest(),
    "scope": "current macOS arm64 development machine; app-resource executable, "
    "PATH excludes development Python; no clean-device/install/signing claim",
}
(args.output / "package-manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
)
if platform.system() == "Darwin":
    binaries = [executable, *package_dir.rglob("*.dylib")]
    linkage = subprocess.run(
        ["/usr/bin/otool", "-L", *map(str, binaries)], capture_output=True, text=True, check=True
    )
    (args.output / "dynamic-linkage.txt").write_text(linkage.stdout)
print(
    json.dumps(
        {
            "measurements": len(observations),
            "health": "ok",
            "licenses": licenses,
            "bytes": manifest["engineDirectoryBytes"],
        },
        ensure_ascii=False,
    )
)
