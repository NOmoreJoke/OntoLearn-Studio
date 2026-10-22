"""Finalize independent R3 evidence without touching any frozen artifact."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
PROOF = OUT / "r3-proof.json"
d = json.loads(PROOF.read_text())

def sha(b):
    return hashlib.sha256(b).hexdigest()

def store(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

def run(argv, tag):
    r = subprocess.run(argv, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True)
    rec = {"argv": argv, "cwd": str(ROOT), "exitCode": r.returncode}
    for name, b in [("stdout", r.stdout), ("stderr", r.stderr)]:
        path = OUT / ("r3-independent-" + tag + "." + name + ".json")
        value = {"encoding": "utf-8-json-string", "bytes": len(b), "sha256": sha(b), "text": b.decode()}
        store(path, value)
        assert json.loads(path.read_text())["text"].encode() == b
        rec[name] = {"path": str(path.relative_to(ROOT)), "bytes": len(b), "sha256": sha(b),
                     "carrierBytes": len(path.read_bytes()), "carrierSHA256": sha(path.read_bytes())}
    d["commands"].append(rec)
    store(PROOF, d)
    assert r.returncode == 0, (tag, r.returncode)
    return r.stdout

# Preserve the exact output of repeated Git identity reads by reference to the
# independently proven matching frozen bytes, rather than duplicating artifacts.
referenced = 0
for c in d["commands"]:
    for stream in ("stdout", "stderr"):
        s = c[stream]
        if "path" in s:
            carrier = json.loads((ROOT / s["path"]).read_text())
            b = carrier["text"].encode()
            assert len(b) == s["bytes"] and sha(b) == s["sha256"]
            continue
        if s["bytes"] == 0:
            assert s["sha256"] == sha(b"")
            s["text"] = ""
            continue
        argv = c["argv"]
        if argv[:2] == ["git", "show"]:
            ref, path = argv[2].split(":", 1)
            b = (ROOT / path).read_bytes()
            assert len(b) == s["bytes"] and sha(b) == s["sha256"]
            s["contentReference"] = {"kind": "frozen-git-blob", "ref": ref, "path": path,
                                     "currentBytesEqualCapturedStream": True}
        elif argv[:3] == ["git", "ls-tree", "-r"]:
            b = ("\n".join(row["path"] for row in d["results"]["fullInventory"]) + "\n").encode()
            assert len(b) == s["bytes"] and sha(b) == s["sha256"]
            s["text"] = b.decode()
        elif argv == ["git", "diff", "57c67631fab6a36f47963aca95b4036064e10777", "1e753a82b837fb53f0389dabf1c401d89809238c"]:
            path = "docs/reviews/I05/observation-projection-spec/r2-independent-full-diff.stdout.txt"
            b = (ROOT / path).read_bytes()
            assert len(b) == s["bytes"] and sha(b) == s["sha256"]
            s["contentReference"] = {"kind": "immutable-original-raw-diff", "path": path,
                                     "currentBytesEqualCapturedStream": True}
        else:
            raise AssertionError("unpreserved stream")
        referenced += 1

run(["/usr/local/bin/node", "/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs",
     "--check", "docs/reviews/I05/observation-projection-spec/r3-review.md"], "final-prettier")
assert run(["git", "rev-parse", "HEAD"], "final-head").decode().strip() == d["process"]
assert not run(["git", "diff", "--cached", "--name-only"], "final-staged")
status = run(["git", "status", "--short", "--untracked-files=all"], "final-status").decode().splitlines()
assert [line for line in status if not line.startswith("?? ")] == [" M AGENTS.md"]
for line in status:
    if not line.startswith("?? "):
        continue
    path = line[3:]
    assert path.startswith("docs/reviews/I05/observation-projection-spec/")
    name = Path(path).name
    assert name in {"r3-review.md", "r3-proof.json"} or name.startswith("r3-independent-")
for row in d["results"]["fullInventory"]:
    b = (ROOT / row["path"]).read_bytes()
    assert len(b) == row["bytes"] and sha(b) == row["sha256"]
assert sha((ROOT / "AGENTS.md").read_bytes()) == "78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759"
report = OUT / "r3-review.md"
report_bytes = report.read_bytes()
d["results"]["finalProtection"] = {"headUnchanged": True, "indexEmpty": True, "frozenArtifactsUnchanged": 121,
    "protectedAGENTSUnchanged": True, "onlyAuthorizedReviewerAdditions": True, "formatterExit": 0,
    "capturedGitIdentityStreamsPreservedByContentReference": referenced,
    "report": {"path": str(report.relative_to(ROOT)), "bytes": len(report_bytes), "sha256": sha(report_bytes)},
    "verdict": "Pass-limited-detached-design-delta", "R2-01": "closed", "historicalFullDiffCheckExit": 2,
    "runtimeAndAuthorityPendingRemain": True, "proofSelfHashExcluded": True}
d["reviewerArtifacts"] = [{"path": str(p.relative_to(ROOT)), "bytes": len(p.read_bytes()), "sha256": sha(p.read_bytes())}
    for p in sorted(OUT.iterdir()) if p.is_file() and (p.name.startswith("r3-independent-") or p.name == "r3-review.md")]
store(PROOF, d)
print(json.dumps(d["results"]["finalProtection"], ensure_ascii=False, indent=2))
