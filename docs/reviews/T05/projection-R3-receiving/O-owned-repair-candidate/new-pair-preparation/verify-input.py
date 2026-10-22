"""Verify only declared inputs; list unknown workspace entries without opening them."""

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def local_path(relative):
    value = Path(relative)
    if value.is_absolute() or not value.parts or any(p in (".", "..") for p in value.parts):
        raise ValueError("invalid declared relative path")
    current = ROOT
    for part in value.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink in declared input")
    if not current.is_file():
        raise ValueError("declared regular input missing")
    return current


def verify_rows(rows):
    if len(rows) != len({row["path"] for row in rows}):
        raise ValueError("duplicate declared input")
    for row in rows:
        data = local_path(row["path"]).read_bytes()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("declared bytes differ: " + row["path"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase", choices=("setup", "setup-policy-overlay", "observe"), required=True
    )
    args = parser.parse_args()
    output = HERE / ("preflight-" + args.phase + ".json")
    if output.exists():
        raise ValueError("observation already exists; preserve first record")
    manifest = json.loads((HERE / "launch-input-manifest.json").read_text())
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != manifest["processRef"] or ROOT != Path(manifest["workspace"]):
        raise ValueError("workspace/process mismatch")
    if sys.version_info[:2] != (3, 12) or Path(sys.executable) != ROOT / ".venv/bin/python":
        raise ValueError("use this workspace Python3.12 interpreter")
    verify_rows(manifest["protectedFiles"])
    verify_rows(manifest["launchInputs"])
    verify_rows(manifest["policyOverlays"])
    historical = manifest["historicalGitAGENTS"]
    old_policy = subprocess.check_output(["git", "show", head + ":AGENTS.md"], cwd=ROOT)
    if (
        len(old_policy) != historical["bytes"]
        or hashlib.sha256(old_policy).hexdigest() != historical["sha256"]
    ):
        raise ValueError("historical Git policy identity changed")
    policy_paths = {row["path"] for row in manifest["policyOverlays"]}
    if policy_paths != {"AGENTS.md"}:
        raise ValueError("unexpected policy overlay")
    changed = set(
        subprocess.check_output(["git", "diff", "--name-only", "-z"], cwd=ROOT)
        .decode()
        .split("\0")[:-1]
    )
    if changed != policy_paths:
        raise ValueError("tracked changes exceed the current policy overlay")
    if subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=ROOT):
        raise ValueError("review inputs must not be staged")
    tracked = set(
        subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "-z", head], cwd=ROOT)
        .decode()
        .split("\0")[:-1]
    )
    declared = {
        r["path"]
        for r in manifest["protectedFiles"] + manifest["launchInputs"] + manifest["policyOverlays"]
    }
    declared.add(str((HERE / "launch-input-manifest.json").relative_to(ROOT)))
    known_dirs = {
        str(parent)
        for relative in tracked | declared
        for parent in Path(relative).parents
        if str(parent) != "."
    }
    unknown = []
    omitted = []
    for current, dirs, files in os.walk(ROOT, followlinks=False):
        folder = Path(current)
        for name in list(dirs):
            relative = str((folder / name).relative_to(ROOT))
            if relative in (".git", ".venv"):
                info = (folder / name).lstat()
                omitted.append({"path": relative, "mode": info.st_mode, "size": info.st_size})
                dirs.remove(name)
            elif relative not in known_dirs:
                info = (folder / name).lstat()
                unknown.append(
                    {
                        "path": relative,
                        "mode": info.st_mode,
                        "size": info.st_size,
                        "mtimeNs": info.st_mtime_ns,
                        "regular": False,
                        "contentOpenedOrHashed": False,
                    }
                )
        for name in files:
            path = folder / name
            relative = str(path.relative_to(ROOT))
            if relative == ".git":
                info = path.lstat()
                omitted.append({"path": relative, "mode": info.st_mode, "size": info.st_size})
                continue
            if relative not in tracked and relative not in declared:
                info = path.lstat()
                unknown.append(
                    {
                        "path": relative,
                        "mode": info.st_mode,
                        "size": info.st_size,
                        "mtimeNs": info.st_mtime_ns,
                        "regular": stat.S_ISREG(info.st_mode),
                        "contentOpenedOrHashed": False,
                    }
                )
    record = {
        "format": "T05-O15-declared-input-static-preflight/1",
        "recordedUtc": datetime.now(UTC).isoformat(),
        "phase": args.phase,
        "workspace": str(ROOT),
        "sourceRef": manifest["sourceRef"],
        "processRef": head,
        "protectedFilesVerified": len(manifest["protectedFiles"]),
        "launchInputsVerified": len(manifest["launchInputs"]),
        "currentPolicyOverlaysVerified": manifest["policyOverlays"],
        "historicalGitPolicy": manifest["historicalGitAGENTS"],
        "onlyUnstagedTrackedChangeIsAuthorizedPolicyOverlay": True,
        "trackedPathMetadataCount": len(tracked),
        "python": {"executable": sys.executable, "version": sys.version},
        "manifestSHA256": hashlib.sha256(
            (HERE / "launch-input-manifest.json").read_bytes()
        ).hexdigest(),
        "unknownOwnWorkspaceEntriesLstatOnly": sorted(unknown, key=lambda x: x["path"]),
        "omittedAdministrativeAndDeclaredOwnEnvironmentRoots": omitted,
        "noWholeFilesystemByteFreezeClaim": True,
        "noActualModelTaskIdentitySettingsTerminalOrVerdictInspected": True,
        "noRepositoryProductOrOracleFunctionExecuted": True,
    }
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps({"phase": args.phase, "exit": 0, "protected": record["protectedFilesVerified"]})
    )


if __name__ == "__main__":
    main()
