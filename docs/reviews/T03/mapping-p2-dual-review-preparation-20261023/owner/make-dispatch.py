"""Make concrete role prompts for one already frozen review HEAD; no UI/run."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path.cwd()
packet = root / "docs/reviews/T03/mapping-p2-dual-review-preparation-20261023"
head = sys.argv[1]
assert re.fullmatch(r"[0-9a-f]{40}", head)
assert subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip() == head
out = packet / "dispatch"
out.mkdir(exist_ok=False)
tree_rows = []
legacy = json.loads((packet / "legacy-fixed-package/mapping-S1-fixed-inputs.json").read_bytes())
legacy_engineering = {r["path"] for r in legacy["completeTrackedTree"] if r["kind"] == "engineering"}
for entry in subprocess.check_output(["git", "ls-tree", "-rlz", head]).split(b"\0"):
    if not entry:
        continue
    info, path = entry.split(b"\t", 1)
    mode, kind, oid, size = info.decode().split()
    path = path.decode()
    tree_rows.append({"path": path, "mode": mode, "type": kind, "gitBlobOID": oid,
                      "bytes": int(size), "kind": "engineering"
                      if (not path.startswith("docs/") or path in legacy_engineering
                          or path.endswith((".py", ".mjs", ".py.raw", ".input.py.txt", ".gitattributes")))
                      else "documentation_or_evidence"})
(out / "full-candidate-tree.json").write_text(json.dumps({
    "reviewHead": head, "identityMethod": "Git ls-tree metadata; blob OID is not SHA256 or full-read claim",
    "completeTrackedTree": tree_rows, "completeTrackedCount": len(tree_rows),
    "allTrackedInputsInScope": True, "protectedAGENTSOverlaySeparate": True,
}, ensure_ascii=False, indent=2) + "\n")
template = (packet / "owner/full-review-template.md").read_bytes()
roles = {
    "zcode": "GLM-5.3 / highest thinking (max) / permission.mode=yolo",
    "minimax": "M3.1-Flash / xhigh / permissionMode=bypassPermissions (Full access)",
}
index = []
for role, model in roles.items():
    tree = root.parent / f"T03-mapping-P2-{role}-review-da1795"
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tree).decode().strip() == head
    report = tree / f"build/review-session/reports/mapping-P2-{role}-full-report.md"
    metadata = tree / "build/review-session/metadata/task-actual.json"
    raw = template
    for key, value in {"ROLE": role, "MODEL": model, "TREE": str(tree),
                       "REVIEW_HEAD": head, "REPORT": str(report), "META": str(metadata)}.items():
        raw = raw.replace(("@@" + key + "@@").encode(), value.encode())
    assert b"@@" not in raw
    appended = []
    for name in ["developer-common-instructions.md", "desktop-operation-policy-20261022.md",
                 "external-review-permissions.md"]:
        body = (packet / "control-snapshots" / name).read_bytes()
        raw += ("\n\n---\n\n# Current frozen policy original: " + name + "\n\n").encode()
        offset = len(raw)
        raw += body
        appended.append({"name": name, "offset": offset, "bytes": len(body),
                         "sha256": hashlib.sha256(body).hexdigest()})
    old_path = f"docs/reviews/T03/designated-review-backlog-20261022/dispatch-v2/mapping-S1-{role}-prompt.md"
    old = subprocess.check_output(["git", "show", "3df399e7b4131dca4b6bf2b3c5ebebc9e26008ab:" + old_path])
    raw += b"\n\n---\n\n# Exact frozen historical dispatch-v2 prompt; current header supersedes old execution paths/status\n\n"
    old_offset = len(raw)
    raw += old
    path = out / f"mapping-P2-{role}-full-prompt.md"
    path.write_bytes(raw)
    (tree / "build/review-session/metadata/dispatch-prompt.md").write_bytes(raw)
    task = {"status": "PREPARED_NO_ACTUAL_TASK", "role": role, "requestedModelSettings": model,
            "tree": str(tree), "reviewHead": head, "actualTask": None, "actualSettings": None,
            "sessionId": None, "turnId": None, "lease": None, "terminalOutcome": None,
            "report": str(report), "promptSha256": hashlib.sha256(raw).hexdigest()}
    metadata.write_text(json.dumps(task, indent=2) + "\n")
    index.append({**task, "prompt": str(path.relative_to(root)), "promptBytes": len(raw),
                  "appendedPolicyOriginals": appended, "legacyOffset": old_offset,
                  "legacyBytes": len(old), "legacySha256": hashlib.sha256(old).hexdigest(),
                  "legacySourceGit": "3df399e7b4131dca4b6bf2b3c5ebebc9e26008ab:" + old_path})
(out / "dispatch-index.json").write_text(json.dumps({
    "format": "T03-mapping-P2-concrete-new-review-dispatch/1", "actualReviewHead": head,
    "approvedBase": "5f910b52c69d86a1076b2032e5d3c63e715947f3",
    "repairBase": "30319412daf8ae4745987babf7bbed93c53b6b42",
    "product": "da1795b20c3c0d47ae975fe3371e802092a4b429",
    "status": "QUEUED_PREPARED_NO_GUI_TASK", "actualTasksCreated": 0, "roots": index,
}, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"reviewHead": head, "trackedFiles": len(tree_rows),
                  "newTasksCreated": 0, "concretePrompts": len(index)}))
