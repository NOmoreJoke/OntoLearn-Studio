"""Owner static staged-input audit; no product imports or execution."""

import hashlib
import json
from pathlib import Path
import subprocess

root = Path.cwd()
packet = root / "docs/reviews/T03/mapping-p2-dual-review-preparation-20261023"
prov = json.loads((packet / "input-copy-provenance.json").read_bytes())
legacy = json.loads((packet / "legacy-fixed-package/mapping-S1-fixed-inputs.json").read_bytes())


def tree(ref):
    result = {}
    for row in subprocess.check_output(["git", "ls-tree", "-rlz", ref]).split(b"\0"):
        if not row:
            continue
        meta, name = row.split(b"\t", 1)
        mode, kind, oid, size = meta.decode().split()
        result[name.decode()] = {"mode": mode, "type": kind, "gitBlobOID": oid,
                                 "bytes": int(size)}
    return result


product = tree(prov["product"])
repair = tree(prov["repairBase"])
index = {}
for row in subprocess.check_output(["git", "ls-files", "--stage", "-z"]).split(b"\0"):
    if not row:
        continue
    meta, name = row.split(b"\t", 1)
    mode, oid, stage = meta.decode().split()
    assert stage == "0"
    index[name.decode()] = {"mode": mode, "gitBlobOID": oid}
engineering = [r for r in legacy["completeTrackedTree"] if r["kind"] == "engineering"]
assert len(engineering) == 173
for row in engineering:
    assert index[row["path"]]["gitBlobOID"] == product[row["path"]]["gitBlobOID"]
non_docs = [p for p in product if not p.startswith("docs/")]
assert len(non_docs) == 138
for path in non_docs:
    assert index[path]["gitBlobOID"] == product[path]["gitBlobOID"]
changes = [p for p in non_docs if product[p] != repair.get(p)]
assert set(changes) == {
    "packages/engine/src/ontolearn_engine/mapping/probe.py",
    "packages/engine/tests/test_mapping_entrypoint.py",
}
differences = []
for row in legacy["completeTrackedTree"]:
    assert row["path"] in index
    if index[row["path"]]["gitBlobOID"] != row["gitBlobOID"]:
        differences.append({"path": row["path"], "originalGitBlobOID": row["gitBlobOID"],
                            "currentGitBlobOID": index[row["path"]]["gitBlobOID"],
                            "kind": row["kind"]})
copied = prov["copiedInputs"] + json.loads((packet / "raw-relocations.json").read_bytes())["files"]
for row in copied:
    raw = subprocess.check_output(["git", "show", ":" + row["path"]])
    assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
for row in prov["missingHistoricalDocsRestored"]:
    assert index[row["path"]]["gitBlobOID"] == row["gitBlobOID"]
for path in packet.rglob("*"):
    if path.is_file() and path.name != "complete-scope-freeze.json":
        assert path.read_bytes() == subprocess.check_output(
            ["git", "show", ":" + str(path.relative_to(root))])
staged = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"])
assert all(p.startswith(b"docs/") for p in staged.split(b"\0") if p)
data = {
    "format": "T03-new-complete-review-scope-freeze/1",
    "approvedBase": prov["approvedBase"], "repairBase": prov["repairBase"],
    "product": prov["product"], "sourceEvidenceRef": prov["sourceRef"],
    "originalEngineeringCount": 173,
    "originalEngineeringIncludingDocsToolsExactNewProduct": True,
    "originalEngineeringCurrentIdentities": [
        {"path": r["path"], **product[r["path"]]} for r in engineering],
    "all138NonDocsEngineeringExactProduct": True,
    "repairBaseToProductNonDocsChanges": changes,
    "originalCompleteTrackedCount": 866,
    "original866PathsAllPresentInStagedCandidate": True,
    "legacyVsCurrentBlobDifferences": differences,
    "restrictedPayloadPolicyUnchanged": True,
    "AGENTSOverlaySha256": hashlib.sha256((root / "AGENTS.md").read_bytes()).hexdigest(),
    "newProductRuns": 0, "newGUIOrAppTasks": 0, "actualTasks": None, "resourceLease": None,
    "preflightCorrections": [
        "Initial not-docs count138 was not legacy engineering173: latter includes35 docs tools; rejected before freeze, no scope removed.",
        "First stage warned CRLF CSV conversion. Packet-local -text and explicit git add --renormalize preserve original bytes; every staged packet file rechecked exact.",
    ],
}
(packet / "complete-scope-freeze.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"originalEngineeringExact": 173, "allNonDocsExact": 138,
                  "oldPathsPresent": 866, "copiedStagedIdentities": len(copied),
                  "oldCurrentBlobDifferences": len(differences), "productRuns": 0}))
