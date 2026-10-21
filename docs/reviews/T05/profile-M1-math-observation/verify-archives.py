"""Verify preserved archive bytes and every original member against frozen indices."""

import hashlib
import json
import zipfile
from pathlib import Path

base = Path(__file__).parent
results = []
for tag in ("first-full", "p2-full", "final-full"):
    manifest = json.loads((base / f"{tag}-archive-members.json").read_text())
    expected = manifest["summary"]
    archive = base / expected["archive"]
    digest = hashlib.file_digest(archive.open("rb"), "sha256").hexdigest()
    assert archive.stat().st_size == expected["archiveBytes"]
    assert digest == expected["archiveSha256"]
    members = {row["member"]: row for row in manifest["members"]}
    with zipfile.ZipFile(archive) as bundle:
        assert len(bundle.infolist()) == len(members) == expected["archiveMembers"]
        assert set(bundle.namelist()) == members.keys()
        for name, row in members.items():
            raw = bundle.read(name)  # ZipFile also verifies CRC during read.
            assert len(raw) == row["bytes"]
            assert hashlib.sha256(raw).hexdigest() == row["sha256"]
    results.append(
        {
            "archive": archive.name,
            "bytes": archive.stat().st_size,
            "sha256": digest,
            "members": len(members),
            "allMemberBytesSha256AndCrcVerified": True,
        }
    )
print(json.dumps(results, ensure_ascii=False, indent=2))
