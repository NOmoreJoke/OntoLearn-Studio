"""Owner-only independent dependency setup; no product/check/package execution."""

import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

role = sys.argv[1]
assert role in ("zcode", "minimax")
owner = Path.cwd()
assert owner.name == "T03-mapping-p2-boundaries"
tree = owner.parent / f"T03-mapping-P2-{role}-review-da1795"
session = tree / "build/review-session"
for name in ("env-cache", "tmp", "scratch", "raw", "reports", "metadata"):
    (session / name).mkdir(parents=True, exist_ok=True)
raw_dir = session / "raw/setup-1"
raw_dir.mkdir(exist_ok=False)
agents = (owner / "AGENTS.md").read_bytes()
assert len(agents) == 15147
assert hashlib.sha256(agents).hexdigest() == (
    "de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4"
)
(tree / "AGENTS.md").write_bytes(agents)
changes = {
    "npm_config_cache": str(session / "env-cache/npm"),
    "UV_CACHE_DIR": str(session / "env-cache/uv"),
    "UV_PROJECT_ENVIRONMENT": str(tree / ".venv"),
    "UV_LINK_MODE": "copy",
    "ELECTRON_CACHE": str(session / "env-cache/electron"),
    "ELECTRON_BUILDER_CACHE": str(session / "env-cache/electron-builder"),
    "XDG_CACHE_HOME": str(session / "env-cache/xdg"),
    "PLAYWRIGHT_BROWSERS_PATH": str(session / "env-cache/playwright"),
    "TMPDIR": str(session / "tmp"),
    "I02_EVIDENCE": str(session / "raw/c1-evidence.json"),
}
cleared = [
    "PYTHONPATH", "ROOT_SOURCE_PATH", "I04_TEST_FIXTURE", "I04_NATIVE_ISOLATED",
    "I02_HMR", "I02_NATIVE", "ENGINE_PATH", "PACKAGE_PATH",
]
environment = dict(os.environ)
for key in cleared:
    environment.pop(key, None)
environment.update(changes)
shell = "#!/bin/sh\n" + "\n".join(f"unset {key}" for key in cleared) + "\n"
shell += "\n".join(f"export {key}={shlex.quote(value)}" for key, value in changes.items())
(session / "environment.sh").write_text(shell + "\n")
records = []
commands = [
    ["npm", "ci", "--ignore-scripts"],
    ["uv", "sync", "--frozen", "--python", "/Users/kyle/.local/bin/python3.12",
     "--no-managed-python", "--link-mode", "copy"],
    ["node", "node_modules/electron/install.js"],
]
for index, argv in enumerate(commands, 1):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out = raw_dir / f"{index:02d}.stdout"
    err = raw_dir / f"{index:02d}.stderr"
    with out.open("xb") as stdout, err.open("xb") as stderr:
        result = subprocess.run(argv, cwd=tree, env=environment,
                                stdout=stdout, stderr=stderr, check=False)
    row = {"argv": argv, "cwd": str(tree), "startedUtc": start,
           "endedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "exitCode": result.returncode}
    for key, path in (("stdout", out), ("stderr", err)):
        data = path.read_bytes()
        row[key] = {"path": str(path), "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()}
    records.append(row)
    (raw_dir / "commands.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps({"role": role, "argv": argv, "exitCode": result.returncode}), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
python_link = tree / ".venv/bin/python"
receipt = {"format": "T03-fresh-review-environment-setup/1", "role": role,
           "tree": str(tree), "setupStartingHead": subprocess.check_output(
               ["git", "rev-parse", "HEAD"], cwd=tree).decode().strip(),
           "environmentChanges": changes, "clearedEnvironmentKeys": cleared,
           "commands": records, "nodeModulesIsSymlink": (tree / "node_modules").is_symlink(),
           "venvIsSymlink": (tree / ".venv").is_symlink(),
           "basePythonIsSymlink": python_link.is_symlink(),
           "basePythonResolved": str(python_link.resolve()),
           "actualTask": None, "actualSettings": None, "lease": None,
           "productExecuted": False, "checkExecuted": False, "packageExecuted": False,
           "note": "Fresh owned mutable dependencies/caches, no shared runtime copy; setup is not runtime acceptance."}
(session / "metadata/setup-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"role": role, "setup": "complete", "productExecuted": False}), flush=True)
