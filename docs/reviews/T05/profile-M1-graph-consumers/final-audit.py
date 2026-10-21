"""Recheck source identity and completed evidence without importing product code."""

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
CANDIDATE = "2ce39f011282b6fdce5e6870610529cff1458fdd"


def digest(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def git_bytes(ref, path, tree=ROOT):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=tree)


def save(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


old_path = HERE / "controlled145-at-499658.json"
if not old_path.exists():
    old_path.write_bytes((HERE / "controlled145.json").read_bytes())
controlled = json.loads(old_path.read_bytes())
controlled["candidate"] = CANDIDATE
for row in controlled["files"]:
    path = row["path"]
    raw = (ROOT / path).read_bytes()
    assert raw == git_bytes(CANDIDATE, path), path
    if row["readonly"]:
        assert digest(raw) == {key: row[key] for key in ("bytes", "sha256")}, path
        assert raw == git_bytes(controlled["adoption"], path), path
        assert raw == git_bytes(row["sourceRef"], path, row["sourceTree"]), path
    row.update(digest(raw))
    if not row["readonly"]:
        row["candidate"] = CANDIDATE
    row["currentEqualsCandidate"] = True
assert len(controlled["files"]) == 145
assert sum(row["readonly"] for row in controlled["files"]) == 143
assert (ROOT / "AGENTS.md").read_bytes() == git_bytes(controlled["base"], "AGENTS.md")
assert digest((ROOT / "AGENTS.md").read_bytes()) == {
    "bytes": 1056,
    "sha256": "1b3c02916e9bab79f463a61f2818846f01e849014b70251b37c112377443a6fb",
}
delta = subprocess.check_output(
    ["git", "diff", "--name-only", controlled["base"], CANDIDATE], text=True
).splitlines()
assert len(delta) == 136
assert set(delta) <= {row["path"] for row in controlled["files"]}
save("controlled145.json", controlled)

commands = []
for directory in sorted((HERE / "commands").iterdir()):
    invocation = json.loads((directory / "invocation.json").read_bytes())
    if not (directory / "result.json").exists():
        failure = json.loads((directory / "launch-failure.json").read_bytes())
        assert failure["launched"] is False
        commands.append(
            {
                "tag": directory.name,
                "exit": None,
                "launchFailure": failure,
                "files": {
                    path.name: digest(path.read_bytes())
                    for path in sorted(directory.iterdir())
                    if path.is_file()
                },
            }
        )
        continue
    result = json.loads((directory / "result.json").read_bytes())
    assert invocation["argv"] == result["argv"]
    assert invocation["cwd"] == result["cwd"] == str(ROOT)
    for stream, fingerprint in result["streams"].items():
        assert digest((directory / stream).read_bytes()) == fingerprint
    commands.append(
        {
            "tag": directory.name,
            "exit": result["exit"],
            "files": {
                path.name: digest(path.read_bytes())
                for path in sorted(directory.iterdir())
                if path.is_file()
            },
        }
    )
save("command-ledger.json", {"allRawStreamsVerified": True, "commands": commands})

archives = []
for members_path in sorted(HERE.glob("*-original-members.json")):
    members = json.loads(members_path.read_bytes())
    summary = members["summary"]
    archive = HERE / summary["archive"]
    fingerprint = digest(archive.read_bytes())
    assert fingerprint["bytes"] == summary["archiveBytes"]
    assert fingerprint["sha256"] == summary["archiveSha256"]
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert len(bundle.namelist()) == len(members["members"]) == summary["memberCount"]
        for row in members["members"]:
            assert digest(bundle.read(row["member"])) == {
                key: row[key] for key in ("bytes", "sha256")
            }
    archives.append(summary)
save("archive-ledger.json", {"allMembersAndCrcVerified": True, "archives": archives})
print(
    json.dumps(
        {
            "controlled": 145,
            "readonly": 143,
            "delta": len(delta),
            "commands": len(commands),
            "archives": len(archives),
        }
    )
)
