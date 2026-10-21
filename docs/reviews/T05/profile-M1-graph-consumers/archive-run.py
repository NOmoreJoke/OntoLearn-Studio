"""Freeze completed run originals, including failures, without product imports."""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

tag, artifact_name, candidate = sys.argv[1:]
base = Path(__file__).parent
artifact = Path(artifact_name)
archive = base / (tag + "-originals.zip")
assert not archive.exists()
entries, cases = [], []
with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
    for directory, prefix in ((base / "commands" / tag, "command"), (artifact, "observations")):
        for path in sorted(directory.rglob("*")) if directory.exists() else ():
            if not path.is_file():
                continue
            raw = path.read_bytes()
            name = prefix + "/" + str(path.relative_to(directory))
            bundle.writestr(name, raw)
            entries.append(
                {"member": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            )
            if path.name == "observation.json":
                row = json.loads(raw)
                cases.append(
                    {
                        "id": row["id"],
                        "kind": row["kind"],
                        "assertion": row["assertion"],
                        "actual": row["actual"],
                        "expected": row["expected"],
                        "member": name,
                        "sha256": hashlib.sha256(raw).hexdigest(),
                    }
                )
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    for row in entries:
        raw = bundle.read(row["member"])
        assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
summary = {
    "tag": tag,
    "candidate": candidate,
    "actualDirectory": str(artifact.resolve()),
    "archive": archive.name,
    "archiveBytes": archive.stat().st_size,
    "archiveSha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "memberCount": len(entries),
    "caseCount": len(cases),
    "allMemberBytesSha256AndCrcVerified": True,
    "scope": "No formal Job/Store/worker/selected, no directsteps, no original83 coverage claim",
}
(base / (tag + "-original-members.json")).write_text(
    json.dumps({"summary": summary, "members": entries}, ensure_ascii=False, indent=2) + "\n"
)
(base / (tag + "-actual-index.json")).write_text(
    json.dumps({"summary": summary, "cases": cases}, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
