"""No-window B1 real app-resource executable parity, receiver and raw metrics."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--packaged", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
executable = args.packaged.resolve(strict=True)
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
environment = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
environment["PATH"] = "/usr/bin:/bin"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(runtime, *arguments):
    command = (
        [sys.executable, "-m", "ontolearn_engine.semantic_probe"]
        if runtime == "source"
        else [str(executable), "--semantic-probe"]
    )
    start = time.perf_counter_ns()
    result = subprocess.run(
        [*command, *arguments],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=90,
        cwd=root,
    )
    return {
        "result": json.loads(result.stdout),
        "stderr": result.stderr,
        "processElapsedNs": time.perf_counter_ns() - start,
    }


hits = []


class Receiver(BaseHTTPRequestHandler):
    def do_GET(self):
        hits.append("synthetic-probe")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Receiver)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
endpoint = f"http://127.0.0.1:{server.server_port}/synthetic"
try:
    with urllib.request.urlopen(endpoint, timeout=5) as response:
        assert response.status == 200
    assert len(hits) == 1  # Positive calibration proves the receiver is reachable.
    results = {}
    measurements = []
    for runtime in ("source", "packaged"):
        results[runtime] = {
            "suite": run(runtime),
            "network": run(runtime, "--mode", "reject", "--endpoint", endpoint),
            "startupTrials": [run(runtime, "--mode", "startup") for _ in range(3)],
        }
        assert len(hits) == 1, "A denied library request reached the receiver"
        for scale in (1, 10):
            for trial in range(3):
                value = run(
                    runtime, "--mode", "measure", "--scale", str(scale), "--trial", str(trial)
                )
                value.update({"runtime": runtime, "scale": scale, "trial": trial})
                measurements.append(value)
                (output / f"{runtime}-{scale}x-{trial}.json").write_text(
                    json.dumps(value, ensure_ascii=False, indent=2) + "\n"
                )
        (output / f"{runtime}-semantic.json").write_text(
            json.dumps(results[runtime], ensure_ascii=False, indent=2) + "\n"
        )
    assert results["source"]["suite"]["result"] == results["packaged"]["suite"]["result"]
    assert results["source"]["network"]["result"] == results["packaged"]["network"]["result"]
    for scale in (1, 10):
        observations = [item["result"] for item in measurements if item["scale"] == scale]
        for field in ("inputSha256", "querySha256", "snapshotId", "result", "expected", "seed"):
            assert all(
                value["s1"][field] == observations[0]["s1"][field] for value in observations
            ), field
        assert all(value["result"] == observations[0]["result"] for value in observations)
    network = {
        "receiver": "controlled test-only loopback HTTP receiver, not a product service",
        "positiveCalibrationHits": 1,
        "deniedRequestHits": len(hits) - 1,
        "perRuntimeCases": len(results["source"]["network"]["result"]),
        "audit": "entry gates zero socket/DNS/urllib attempts; forced library JSON-LD "
        "path reached urllib.Request and guard denied it before socket I/O",
    }
    (output / "network.json").write_text(json.dumps(network, indent=2) + "\n")
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)

# Existing real health remains unchanged; no semantic product capability is advertised.
health = subprocess.run(
    [str(executable)],
    env=environment,
    input=json.dumps({"id": "I05-cli-health", "method": "health", "protocolVersion": 1}) + "\n",
    capture_output=True,
    text=True,
    timeout=15,
    check=True,
)
health_value = json.loads(health.stdout)
assert health_value["ok"] and health_value["result"]["capabilities"] == ["health"]
package = executable.parent
inventory = package / "_internal/i05-inventory"
metadata = json.loads((inventory / "manifest.json").read_text())
assert metadata["uvLockSha256"] == sha(root / "uv.lock")
for item in metadata["packages"]:
    for file in item["licenseFiles"]:
        assert sha(inventory / file["path"]) == file["sha256"]
native = json.loads((inventory / "native-runtime/provenance.json").read_text())
assert metadata["nativeLicenseProvenanceMatched"] is True
assert sha(inventory / "native-runtime/upstream-PYTHON.json.raw") == native["metadataSha256"]
for item in native["licenseFiles"]:
    assert sha(inventory / "native-runtime" / item["path"]) == item["sha256"]
assert sha(inventory / "CPython-LICENSE.txt") == metadata["pythonLicenseSha256"]
resources = [p for p in package.rglob("*") if p.is_file()]
assert any("pyshacl/assets" in p.as_posix() for p in resources)
assert any(p.name == "invalidation-v2.json" for p in resources)
app = next((p for p in executable.parents if p.suffix == ".app"), None)
app_files = [p for p in app.rglob("*") if p.is_file()] if app else []
manifest = {
    "host": platform.platform(),
    "machine": platform.machine(),
    "device": {k: v for k, v in platform.uname()._asdict().items() if k != "node"},
    "python": platform.python_version(),
    "executableSha256": sha(executable),
    "uvLockSha256": sha(root / "uv.lock"),
    "engineDirectoryBytes": sum(p.stat().st_size for p in resources),
    "appDirectoryBytes": sum(p.stat().st_size for p in app_files),
    "fileCount": len(resources),
    "health": health_value,
    "files": [
        {"path": str(p.relative_to(package)), "bytes": p.stat().st_size, "sha256": sha(p)}
        for p in sorted(resources)
    ],
    "inventory": metadata,
    "measurements": len(measurements),
    "network": network,
    "limits": "current macOS arm64 unsigned development app-resource executable; "
    "PATH excludes development Python; no Electron launch, clean-device, "
    "signing, target-platform or production claim",
}
if platform.system() == "Darwin":
    specs = subprocess.run(
        ["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string", "hw.memsize", "hw.ncpu"],
        capture_output=True,
        text=True,
        check=True,
    )
    chip, memory, cpus = specs.stdout.strip().splitlines()
    manifest["hardware"] = {
        "chip": chip,
        "physicalMemoryBytes": int(memory),
        "logicalCpus": int(cpus),
    }
(output / "package-manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
)
if platform.system() == "Darwin":
    binaries = [executable, *package.rglob("*.dylib"), *package.rglob("*.so")]
    linkage = subprocess.run(
        ["/usr/bin/otool", "-L", *map(str, binaries)], capture_output=True, text=True, check=True
    )
    (output / "dynamic-linkage.txt").write_text(linkage.stdout)
archive = subprocess.run(
    [str(Path(sys.executable).parent / "pyi-archive_viewer"), "-l", "-r", str(executable)],
    capture_output=True,
    text=True,
    check=True,
    timeout=60,
)
assert "ontolearn_engine.semantic" in archive.stdout
assert "pyshacl.validator" in archive.stdout
(output / "pyinstaller-imports.txt").write_text(archive.stdout)
print(
    json.dumps(
        {
            "parity": True,
            "measurements": len(measurements),
            "network": network,
            "engineBytes": manifest["engineDirectoryBytes"],
            "appBytes": manifest["appDirectoryBytes"],
        },
        ensure_ascii=False,
    )
)
