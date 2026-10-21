"""Audit fixed source and the single new capture without product imports."""

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()


def load(path):
    return json.loads(path.read_bytes())


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


controlled = load(HERE / "controlled146.json")
candidate = controlled["candidate"]
assert len(controlled["files"]) == 146
assert sum(r["role"] == "read-only" for r in controlled["files"]) == 145
for row in controlled["files"]:
    raw = (ROOT / row["path"]).read_bytes()
    assert identity(raw) == {k: row[k] for k in ("bytes", "sha256")}
    assert raw == subprocess.check_output(["git", "show", f"{candidate}:{row['path']}"])
    assert raw == subprocess.check_output(
        ["git", "show", f"{row['sourceRef']}:{row['path']}"], cwd=row["sourceTree"]
    )
original = (HERE / "original-test.py.raw").read_bytes()
test = ROOT / "packages/engine/tests/test_profile_M1_graph_consumers.py"
assert len(original) == 48273 and test.read_bytes().startswith(original)
frozen = load(HERE / "frozen-old393.json")
assert len(frozen["files"]) == 393
for row in frozen["files"]:
    raw = (ROOT / row["path"]).read_bytes()
    assert identity(raw) == {k: row[k] for k in ("bytes", "sha256")}
    assert raw == subprocess.check_output(["git", "show", f"{frozen['start']}:{row['path']}"])
commands = []
for directory in sorted((HERE / "commands").iterdir()):
    invocation, result = load(directory / "invocation.json"), load(directory / "result.json")
    assert invocation["argv"] == result["argv"]
    assert invocation["cwd"] == result["cwd"] == str(ROOT)
    for name, expected in result["streams"].items():
        assert identity((directory / name).read_bytes()) == expected
    commands.append({"tag": directory.name, "result": result})
save("command-ledger.json", {"allRawStreamsVerified": True, "commands": commands})
normal = load(HERE / "commands/entry-normal/result.json")
assert normal["exit"] == 0
assert "M1_GRAPH_OBSERVATION_DIR" not in normal["environment"]
assert "M1_ILLTYPED_OBSERVATION_DIR" in normal["environment"]
members = load(HERE / "entry-normal-original-members.json")
summary = members["summary"]
assert summary["candidate"] == candidate and summary["caseCount"] == 1
assert identity((HERE / summary["archive"]).read_bytes()) == {
    "bytes": summary["archiveBytes"],
    "sha256": summary["archiveSha256"],
}
with zipfile.ZipFile(HERE / summary["archive"]) as bundle:
    assert bundle.testzip() is None
    assert len(bundle.namelist()) == summary["memberCount"] == len(members["members"])
    observations = []
    for row in members["members"]:
        raw = bundle.read(row["member"])
        assert identity(raw) == {k: row[k] for k in ("bytes", "sha256")}
        if row["member"].endswith("/observation.json"):
            observations.append(json.loads(raw))
    (observation,) = observations
    assert observation["assertion"] == "pass"
    assert observation["testSourceSha256"] == identity(test.read_bytes())["sha256"]
    semantic = ROOT / "packages/engine/src/ontolearn_engine/semantic.py"
    assert observation["semanticSourceSha256"] == identity(semantic.read_bytes())["sha256"]
    stages = observation["actual"]["stages"]
    assert [s["actual"]["validatorRuns"] for s in stages] == [0, 1, 0, 0]
    assert [s["actual"]["status"] for s in stages] == ["error", "success", "error", "error"]
    assert stages[1]["actual"]["result"]["report"]["conforms"] is False
    for stage in stages:
        state = stage["actual"]["globalState"]
        assert state["normalizationUnchanged"] and state["converterKeysUnchanged"]
        assert state["converterIdentitiesUnchanged"]
save(
    "audit-result.json",
    {
        "candidate": candidate,
        "controlled": 146,
        "readonly": 145,
        "frozenOldProcess": 393,
        "originalTestPrefix": 48273,
        "newCapturedCases": 1,
        "newRealReports": 1,
        "stageValidatorRuns": [0, 1, 0, 0],
        "archive": summary,
        "allMemberBytesShaAndCrcVerified": True,
        "oldGraphPersistentCaptureNotEnabled": True,
    },
)
print(
    json.dumps(
        {
            "candidate": candidate,
            "readonly": 145,
            "frozenOldProcess": 393,
            "newCapturedCases": 1,
            "stageValidatorRuns": [0, 1, 0, 0],
        }
    )
)
