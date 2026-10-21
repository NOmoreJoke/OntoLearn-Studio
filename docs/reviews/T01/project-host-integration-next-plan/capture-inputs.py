"""Read-only fixed-Git evidence for the next host integration design."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEST = Path(__file__).parent
ENGINE_REF = "5de3fff8aa02c5d6e577938660e9362936d90550"
BASE = "5f910b52c69d86a1076b2032e5d3c63e715947f3"
I06 = ROOT.parent / "I06-model-gateway"
I06_REF = "660da44aa7ad1b3ba7dbfb3a90fef37e25763ec8"
sources = [
    "apps/desktop/src/main/index.ts",
    "apps/desktop/src/main/task-service.ts",
    "apps/desktop/src/main/engine.ts",
    "apps/desktop/src/preload/index.ts",
    "apps/desktop/src/renderer/src/App.tsx",
    "apps/desktop/src/renderer/src/env.d.ts",
    "packages/contracts/src/index.ts",
    "packages/engine/src/ontolearn_engine/job_store.py",
    "packages/engine/src/ontolearn_engine/coordinator.py",
    "packages/engine/src/ontolearn_engine/storage.py",
    "packages/engine/src/ontolearn_engine/project/format3.py",
    "packages/engine/src/ontolearn_engine/project/applications.py",
    "docs/prd/PRD-本体学习与落地Agent工作台.md",
    "docs/iterations/T01/full-function-acceptance-map.md",
]
contracts = [
    "docs/iterations/I06/main-integration-handoff.md",
    "docs/iterations/I06/format3-consumer-integration-request.md",
    "docs/iterations/I06/source-selection-lifecycle-interface.md",
]


def git(repo, ref, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", f"{ref}:{path}"])


def identity(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


rows = []
for path in sources:
    data = git(ROOT, ENGINE_REF, path)
    assert data == (ROOT / path).read_bytes(), f"Frozen product/input changed: {path}"
    rows.append({"repository": str(ROOT), "ref": ENGINE_REF, "path": path, **identity(data)})
for path in contracts:
    data = git(I06, I06_REF, path)
    assert data == (I06 / path).read_bytes(), f"I06 contract has uncommitted drift: {path}"
    local = DEST / "inputs/I06" / Path(path).name
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists():
        assert local.read_bytes() == data
    else:
        local.write_bytes(data)
    rows.append(
        {
            "repository": str(I06),
            "ref": I06_REF,
            "path": path,
            "copy": str(local.relative_to(ROOT)),
            "permission": "Read-only contract reference, not adoption of unapproved gateway code",
            **identity(data),
        }
    )
for repo, ref, path in [
    (
        I06,
        "b1283bce1daf7198fc6b0b62f8b0a6bbffa5a874",
        "docs/iterations/I06/T01-owner-response-alignment-r1.md",
    ),
    (
        ROOT.parent / "I06-transfer-guard-core",
        "961ce77f26accd11bd1cd3ad4a9e560cd3565e37",
        "docs/iterations/I06/transfer-guard-core-v1.md",
    ),
]:
    data = git(repo, ref, path)
    local = DEST / "inputs/I06" / Path(path).name
    if local.exists():
        assert local.read_bytes() == data
    else:
        local.write_bytes(data)
    rows.append(
        {
            "repository": str(repo),
            "ref": ref,
            "path": path,
            "copy": str(local.relative_to(ROOT)),
            "permission": "Read-only fixed contract; metadata eligibility never grants content I/O",
            **identity(data),
        }
    )
for path in sources[:3] + [
    "packages/engine/src/ontolearn_engine/job_store.py",
    "packages/engine/src/ontolearn_engine/coordinator.py",
]:
    data = git(ROOT, BASE, path)
    rows.append(
        {
            "repository": str(ROOT),
            "ref": BASE,
            "path": path,
            "purpose": "Approved baseline comparison only",
            **identity(data),
        }
    )
output = DEST / "inputs.json"
document = {
    "scope": "Docs-only next plan; no product/test/GUI execution",
    "frozenProduct": ENGINE_REF,
    "approvedBase": BASE,
    "sources": rows,
}
output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
print(
    json.dumps(
        {"sources": len(rows), "manifest": str(output), **identity(output.read_bytes())},
        ensure_ascii=False,
    )
)
