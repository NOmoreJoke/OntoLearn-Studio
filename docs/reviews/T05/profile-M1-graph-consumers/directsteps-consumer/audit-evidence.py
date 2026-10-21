"""Read-only source/original-byte closure, no product imports or inference."""

import gzip
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()


def load(path):
    return json.loads(path.read_bytes())


def fingerprint(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def save(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


controlled = load(HERE / "controlled146.json")
candidate = controlled["candidate"]
assert len(controlled["files"]) == 146
assert sum(r["role"] == "read-only" for r in controlled["files"]) == 145
for row in controlled["files"]:
    raw = (ROOT / row["path"]).read_bytes()
    assert fingerprint(raw) == {k: row[k] for k in ("bytes", "sha256")}
    assert raw == subprocess.check_output(["git", "show", f"{candidate}:{row['path']}"])
    assert raw == subprocess.check_output(
        ["git", "show", f"{row['sourceRef']}:{row['path']}"], cwd=row["sourceTree"]
    )
original = (HERE / "original-test.py.raw").read_bytes()
test = ROOT / "packages/engine/tests/test_profile_M1_graph_consumers.py"
assert len(original) == 28706 and test.read_bytes().startswith(original)
frozen = load(HERE / "frozen-old254.json")
assert len(frozen["files"]) == 254
for row in frozen["files"]:
    raw = (ROOT / row["path"]).read_bytes()
    assert fingerprint(raw) == {k: row[k] for k in ("bytes", "sha256")}
    assert raw == subprocess.check_output(["git", "show", f"{frozen['start']}:{row['path']}"])

commands = []
for directory in sorted((HERE / "commands").iterdir()):
    invocation, result = load(directory / "invocation.json"), load(directory / "result.json")
    assert invocation["argv"] == result["argv"]
    assert invocation["cwd"] == result["cwd"] == str(ROOT)
    for name, expected in result["streams"].items():
        assert fingerprint((directory / name).read_bytes()) == expected
    commands.append({"tag": directory.name, "result": result})
save("command-ledger.json", {"allOriginalStreamsVerified": True, "commands": commands})

archives, final = [], None
for path in sorted(HERE.glob("*-original-members.json")):
    manifest = load(path)
    summary = manifest["summary"]
    archive = HERE / summary["archive"]
    assert fingerprint(archive.read_bytes()) == {
        "bytes": summary["archiveBytes"],
        "sha256": summary["archiveSha256"],
    }
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert len(bundle.namelist()) == summary["memberCount"] == len(manifest["members"])
        for row in manifest["members"]:
            raw = bundle.read(row["member"])
            assert fingerprint(raw) == {k: row[k] for k in ("bytes", "sha256")}
        if summary["tag"] == "direct-normal":
            assert summary["candidate"] == candidate
            final = [
                json.loads(bundle.read(n))
                for n in bundle.namelist()
                if n.endswith("/observation.json")
            ]
    archives.append(summary)
save("archive-ledger.json", {"allBytesShaAndCrcVerified": True, "archives": archives})
storage = load(HERE / "index-storage.json")
for row in storage["indexes"]:
    compressed = HERE / row["fullIndexLosslessGzip"]["path"]
    assert fingerprint(compressed.read_bytes()) == {
        k: row["fullIndexLosslessGzip"][k] for k in ("bytes", "sha256")
    }
    digest, size = hashlib.sha256(), 0
    with gzip.open(compressed, "rb") as reader:
        while chunk := reader.read(1_048_576):
            digest.update(chunk)
            size += len(chunk)
    assert {"bytes": size, "sha256": digest.hexdigest()} == row["fullIndexOriginalBytes"]
assert final is not None and len(final) == 18
assert all(o["testSourceSha256"] == fingerprint(test.read_bytes())["sha256"] for o in final)
matched = [o["id"] for o in final if o["assertion"] == "pass"]
pending = [o["id"] for o in final if o["assertion"] == "observed-pending-not-normative-pass"]
assert len(matched) == 16 and set(pending) == {"C-inclusive-date-entry", "C-illtyped-entry"}
assert all(o["assertion"] != "fail" for o in final)
direct = [o for o in final if o["kind"] == "direct-graph-consumer"]
assert len(direct) == 3
vectors = []
for observation in direct:
    actual = observation["actual"]
    assert actual["fullPayloadEqual"] and actual["fullChildrenEqual"]
    assert len(actual["operations"]) == 3 and len(actual["boundaries"]) == 24
    for row in actual["boundaries"]:
        if row["offset"] == 0:
            assert row["returned"] and row["failure"] is None
        else:
            assert not row["returned"] and row["failure"]["reason"] == "DIRECT_STEPS_LIMIT"
            assert row["failure"]["classification"] == "resource"
            assert row["failure"]["domain"] == row["domain"]
            assert row["reuse"]["failure"]["reason"] == "DIRECT_STEPS_REUSED"
        vectors.append(
            {
                "case": observation["id"],
                "phase": row["phase"],
                "domain": row["domain"],
                "cap": row["cap"],
                "offset": row["offset"],
                "failure": row["failure"],
            }
        )
save(
    "budget-vector-index.json",
    {
        "candidate": candidate,
        "vectors": vectors,
        "exactSuccesses": 36,
        "oneShortRefusals": 36,
        "failedReuseRefusals": 36,
    },
)
save(
    "audit-result.json",
    {
        "candidate": candidate,
        "controlled": 146,
        "readonly": 145,
        "originalTestPrefix": 28706,
        "frozenOldProcess": 254,
        "matched": matched,
        "pending": pending,
        "archives": archives,
        "allMemberBytesShaAndCrcVerified": True,
    },
)
print(
    json.dumps(
        {
            "candidate": candidate,
            "controlled": 146,
            "readonly": 145,
            "oldFrozen": 254,
            "matched": 16,
            "pending": 2,
            "exactD": 36,
            "oneShortD": 36,
            "failedReuseD": 36,
        }
    )
)
