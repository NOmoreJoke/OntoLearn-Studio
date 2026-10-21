"""Verify immutable source and completed originals using only stdlib and Git."""

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent


def fingerprint(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


controlled = load(HERE / "controlled145.json")
candidate = controlled["candidate"]
assert len(controlled["files"]) == controlled["readonly"] == 145
for row in controlled["files"]:
    raw = (ROOT / row["path"]).read_bytes()
    assert fingerprint(raw) == {key: row[key] for key in ("bytes", "sha256")}
    assert raw == subprocess.check_output(["git", "show", f"{candidate}:{row['path']}"])

frozen = load(HERE / "frozen-old201.json")
assert len(frozen["files"]) == 201
for row in frozen["files"]:
    raw = (ROOT / row["path"]).read_bytes()
    assert fingerprint(raw) == {key: row[key] for key in ("bytes", "sha256")}
    assert raw == subprocess.check_output(["git", "show", f"{frozen['start']}:{row['path']}"])

commands = []
for directory in sorted((HERE / "commands").iterdir()):
    invocation = load(directory / "invocation.json")
    result = load(directory / "result.json")
    assert invocation["argv"] == result["argv"]
    assert invocation["cwd"] == result["cwd"] == str(ROOT)
    for name, expected in result["streams"].items():
        assert fingerprint((directory / name).read_bytes()) == expected
    commands.append({"tag": directory.name, "exit": result["exit"], "result": result})
save("command-ledger.json", {"allCompletedStreamsVerified": True, "commands": commands})

members = load(HERE / "shape-normal-original-members.json")
summary = members["summary"]
assert summary["candidate"] == candidate and summary["caseCount"] == 15
archive = HERE / summary["archive"]
assert fingerprint(archive.read_bytes()) == {
    "bytes": summary["archiveBytes"],
    "sha256": summary["archiveSha256"],
}
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert len(bundle.namelist()) == len(members["members"]) == summary["memberCount"]
    observations = []
    for row in members["members"]:
        raw = bundle.read(row["member"])
        assert fingerprint(raw) == {key: row[key] for key in ("bytes", "sha256")}
        if row["member"].endswith("/observation.json"):
            observations.append(json.loads(raw))
    assert len(observations) == 15
    test = ROOT / "packages/engine/tests/test_profile_M1_graph_consumers.py"
    assert all(
        o["testSourceSha256"] == fingerprint(test.read_bytes())["sha256"] for o in observations
    )
    matched = [o["id"] for o in observations if o["assertion"] == "pass"]
    pending = [
        o["id"] for o in observations if o["assertion"] == "observed-pending-not-normative-pass"
    ]
    assert len(matched) == 13 and set(pending) == {"C-inclusive-date-entry", "C-illtyped-entry"}
    assert all(o["assertion"] != "fail" for o in observations)
    four = {
        "C-langString",
        "C-inclusive-nni",
        "C-inclusive-dateTime-equal",
        "C-inclusive-dateTime-before",
    }
    closed = []
    for observation in observations:
        if observation["id"] not in four:
            continue
        actual = observation["actual"]
        assert actual["status"] == "success" and actual["validatorRuns"] == 1
        report_prefix = (
            "observations/" + hashlib.sha256(observation["id"].encode()).hexdigest() + "/"
        )
        assert bundle.read(report_prefix + "report.nt")
        assert bundle.read(report_prefix + "report-text.txt")
        closed.append(observation)
    assert len(closed) == 4
    save("four-case-closure.json", {"candidate": candidate, "cases": closed})

save(
    "audit-result.json",
    {
        "candidate": candidate,
        "readonlyVerified": 145,
        "oldProcessFrozen": 201,
        "archive": summary,
        "matched": matched,
        "pending": pending,
        "allMemberBytesShaAndCrcVerified": True,
    },
)
print(
    json.dumps(
        {
            "candidate": candidate,
            "readonly": 145,
            "oldFrozen": 201,
            "matched": 13,
            "pending": 2,
            "members": summary["memberCount"],
        }
    )
)
