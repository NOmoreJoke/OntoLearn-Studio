"""Packaged Lq query-learning runner with owned process cleanup; no
process-name-wide killing.

The process-ownership machinery (Windows Job Object, Linux subreaper/pidfd,
macOS observed BSD incarnation evidence) is imported from the B1a packaged
runner so every runner keeps one shared, already-reviewed implementation. This
script only owns the Lq query-course acceptance: it launches the packaged
desktop through Playwright against
``tests/e2e/lq-query-learning.spec.ts`` with ``ONTOLEARN_PACKAGED_EXECUTABLE``,
verifies owned process cleanup, and writes a JSON summary next to the output.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

B1A_RUNNER = Path(__file__).resolve().parent / "run-b1a-packaged-lifecycle.py"

EXPECTED_LQ_TESTS = 1


def load_b1a_module():
    spec = importlib.util.spec_from_file_location("ontolearn_b1a_packaged_runner", B1A_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("B1a packaged runner unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _collect_tests(suites: list[dict[str, object]]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for suite in suites:
        for spec in suite.get("specs", []):
            if not isinstance(spec, dict):
                continue
            title = str(spec.get("title", ""))
            for test_item in spec.get("tests", []):
                if isinstance(test_item, dict):
                    found.append((title, str(test_item.get("status", "unknown"))))
        nested = suite.get("suites", [])
        if isinstance(nested, list) and nested:
            found.extend(_collect_tests(nested))
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    release, output = args.release.resolve(strict=True), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    b1a = load_b1a_module()
    names = {
        "darwin": "OntoLearn Studio",
        "win32": "OntoLearn Studio.exe",
        "linux": "@ontolearndesktop",
    }
    candidates = []
    for asar in release.rglob("app.asar"):
        resources = asar.parent
        executable = (
            resources.parent / "MacOS" / names[sys.platform]
            if sys.platform == "darwin"
            else resources.parent / names[sys.platform]
        )
        if executable.is_file():
            candidates.append((executable, asar))
    if len(candidates) != 1:
        raise RuntimeError("Expected one packaged desktop; found " + str(len(candidates)))
    executable, asar = candidates[0]
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node runtime unavailable")
    env = os.environ.copy()
    for key in ("ELECTRON_RUN_AS_NODE", "ELECTRON_RENDERER_URL", "I04_TEST_FIXTURE"):
        env.pop(key, None)
    if sys.platform == "linux" and env.get("B1A_NATIVE_ISOLATED") != "1":
        raise RuntimeError("Linux packaged runs require the dedicated native display lane")
    command = [
        node,
        str(Path("node_modules/@playwright/test/cli.js").resolve(strict=True)),
        "test",
        "tests/e2e/lq-query-learning.spec.ts",
        "--workers=1",
        "--reporter=list,github,json",
        "--output=" + str(output / "test-results"),
    ]
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
        "spec": "tests/e2e/lq-query-learning.spec.ts",
        "nativePickerRequired": sys.platform == "linux",
    }
    (output / "launch.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    outcome = b1a.run_owned(command, env, output, executable, timeout=900)
    primary, cleanup = outcome["primary"], outcome["cleanup"]
    summary = {
        "primary": primary,
        "cleanupComplete": cleanup.get("complete"),
        "hadResidual": cleanup.get("hadResidual"),
        "expected": EXPECTED_LQ_TESTS,
    }
    if primary.get("kind") != "exit" or primary.get("exitCode") != 0:
        (output / "summary.json").write_text(
            json.dumps({**summary, "status": "failed"}, indent=2) + "\n", encoding="utf-8"
        )
        raise SystemExit(primary.get("exitCode") or 1)
    if not cleanup["complete"] or cleanup.get("hadResidual"):
        (output / "summary.json").write_text(
            json.dumps({**summary, "status": "cleanup-unproven"}, indent=2) + "\n", encoding="utf-8"
        )
        raise RuntimeError("Lq packaged tests left live processes or cleanup is unproven")
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    stats = report["stats"]
    summary["stats"] = stats
    summary["tests"] = sorted(
        _collect_tests(report.get("suites", []))
        or ((result["title"], result["status"]) for result in report.get("tests", []))
    )
    if (
        stats["expected"] != EXPECTED_LQ_TESTS
        or stats["unexpected"] != 0
        or stats["flaky"] != 0
        or stats["skipped"] != 0
    ):
        summary["status"] = "incomplete"
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError("Incomplete Lq packaged acceptance")
    summary["status"] = "passed"
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
