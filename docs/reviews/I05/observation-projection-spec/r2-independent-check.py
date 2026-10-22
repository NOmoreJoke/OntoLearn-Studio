"""Independent R2 delta proof; stdlib and detached model only.

Only new r2-proof and r2-independent-* evidence is written. No old R1 scripts
are executed and no candidate file is changed.
"""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
DESIGN = ROOT / "docs/iterations/I05/observation-projection-spec"
R1 = "57c67631fab6a36f47963aca95b4036064e10777"
CANDIDATE = "1e753a82b837fb53f0389dabf1c401d89809238c"
PROCESS = "ce268c62cc33a5b85d9c663c87d8260d68ab9612"
PYTHON = "/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12"
PREFIXES = ["docs/iterations/I05/observation-projection-spec/", "docs/reviews/I05/observation-projection-spec/"]
proof = {"format": "i05-observation-independent-r2/1", "revisionBase": R1,
         "candidate": CANDIDATE, "process": PROCESS, "commands": [], "results": {}}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def save():
    (OUT / "r2-proof.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")

def run(argv, tag=None):
    r = subprocess.run(argv, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, check=False)
    row = {"argv": argv, "cwd": str(ROOT), "exitCode": r.returncode}
    for stream, b in [("stdout", r.stdout), ("stderr", r.stderr)]:
        row[stream] = {"bytes": len(b), "sha256": sha(b)}
        if tag:
            p = OUT / ("r2-independent-" + tag + "." + stream + ".txt")
            p.write_bytes(b)
            row[stream]["path"] = str(p.relative_to(ROOT))
    proof["commands"].append(row)
    save()
    assert r.returncode == 0, ("bounded command failed", argv[0])
    return r.stdout

def blob(ref, path):
    return run(["git", "show", ref + ":" + path])

def strict_load(b):
    def pairs(rows):
        x = {}
        for k, v in rows:
            if k in x: raise ValueError("duplicate member")
            x[k] = v
        return x
    def bad(_): raise ValueError("nonfinite")
    return json.loads(b, object_pairs_hook=pairs, parse_constant=bad)

assert run(["git", "rev-parse", "HEAD"], "head").decode().strip() == PROCESS
status = run(["git", "status", "--short", "--untracked-files=all"], "start-status").decode()
assert not run(["git", "diff", "--cached", "--name-only"], "staged")
delta = run(["git", "diff", "--name-status", R1, CANDIDATE], "delta-name-status").decode().splitlines()
assert len(delta) == 18
full_diff = run(["git", "diff", R1, CANDIDATE], "full-diff")
process_delta = run(["git", "diff", "--name-only", CANDIDATE, PROCESS], "process-delta").decode().splitlines()
assert process_delta == [PREFIXES[1] + "candidate-receipt-r2.json"]
files = run(["git", "ls-tree", "-r", "--name-only", PROCESS, "--", *PREFIXES]).decode().splitlines()
assert len(files) == 62
identities = []
for path in files:
    b = (ROOT / path).read_bytes()
    assert b == blob(PROCESS, path)
    identities.append({"path": path, "bytes": len(b), "sha256": sha(b), "currentEqualsProcess": True})
proof["results"]["fullInventory"] = identities
for name, length, digest in [
    ("manifest-r2.json", 12948, "3e8d9580a8174404a64dbba9a8a785f427fd7b8248a2c06a29d182e4e59f7ee2"),
    ("candidate-receipt-r2.json", 21764, "759522fdb603fe2d2132bd28a6d6d704d7829d581a9619a84f96824162211344")]:
    b = (OUT / name).read_bytes()
    assert len(b) == length and sha(b) == digest
manifest = strict_load((OUT / "manifest-r2.json").read_bytes())
receipt = strict_load((OUT / "candidate-receipt-r2.json").read_bytes())
for item in manifest["files"] + receipt["candidateFullInventory"]:
    b = (ROOT / item["path"]).read_bytes()
    assert len(b) == item["bytes"] and sha(b) == item["sha256"]
    assert b == blob(CANDIDATE, item["path"])
assert len(manifest["files"]) == 60 and len(receipt["candidateFullInventory"]) == 61
declaration = strict_load((OUT / "delta-r2.json").read_bytes())
assert len(declaration["preservedOriginalFiles"]) == 43
for row in declaration["preservedOriginalFiles"]:
    b = (ROOT / row["path"]).read_bytes()
    assert b == blob(R1, row["path"])
    assert len(b) == row["bytes"] and sha(b) == row["sha256"]
assert sha((ROOT / "AGENTS.md").read_bytes()) == "78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759"
proof["results"]["immutableR1Files"] = 43

old = strict_load(blob(R1, PREFIXES[0] + "cases.json"))
current = strict_load((DESIGN / "cases.json").read_bytes())
assert len(current["cases"]) == 37
for before, after in zip(old["cases"], current["cases"]):
    for field in ["id", "parameters", "datasetId", "inputProjectionSha256", "inputSourceRefs", "independentTypedMath", "expectedProjection"]:
        assert before[field] == after[field]
assert (DESIGN / "pure-sources.json").read_bytes() == blob(R1, PREFIXES[0] + "pure-sources.json")
assert (DESIGN / "selftest.py").read_bytes() == blob(R1, PREFIXES[0] + "selftest.py")
proof["results"]["all37SealedFieldsUnchanged"] = True
contract = blob("ee2b30a2dad35b2d395f9c735aff80371ab41110", "docs/iterations/I05/source-package-parity/contract.md")
assert sha(contract) == "d2cdc2e6017ad0257f30611d2928a60a116f4dc389cacdfc977c17efe13e2a23"
proof["results"]["approvedInvocationSource"] = {"ref": "ee2b30a2dad35b2d395f9c735aff80371ab41110", "lines": {str(i): contract.decode().splitlines()[i-1] for i in [51, 52]}}

for name in ["model.py", "selftest.py", "selftest-r2.py"]:
    tree = ast.parse((DESIGN / name).read_text())
    imports = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): imports.extend(a.name for a in n.names)
        if isinstance(n, ast.ImportFrom): imports.append(n.module)
    assert set(imports) <= {"hashlib", "itertools", "json", "re", "copy", "pathlib", "sys", "unittest", "subprocess", "model", "selftest"}
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in {"write_text", "write_bytes", "unlink", "mkdir"} for n in ast.walk(tree))
run([PYTHON, PREFIXES[0] + "selftest-r2.py"], "selftest-32")

spec = importlib.util.spec_from_file_location("r2_reviewed_model", DESIGN / "model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
schema = strict_load((DESIGN / "schema.json").read_bytes())
by_id = {c["id"]: c for c in current["cases"]}
for c in current["cases"]:
    assert m.validate(c["expectedProjection"], schema)
    assert m.matches(c, copy.deepcopy(c["expectedProjection"]), schema)
    assert not m.matches(c, m.unknown(c["harnessStage"]), schema)

sort_examples = []
for id, path in [("rdfs/cycle", ("value", "rdfs")), ("rdfs/domain-depth2", ("value", "rdfsEvidence", 1, "basis")), ("scope/fresh", ("value", "facts"))]:
    c = by_id[id]
    changed = copy.deepcopy(c["expectedProjection"])
    cursor = changed
    for k in path: cursor = cursor[k]
    cursor.reverse()
    sort_examples.append({"id": id, "path": list(path), "schemaValid": m.validate(changed, schema), "matchesUnsorted": m.matches(c, changed, schema), "exactOriginal": m.exact(changed, c["expectedProjection"])})
proof["results"]["stableSerializationCounterexamples"] = sort_examples
proof["results"]["productExecuted"] = False
save()
print(json.dumps({"fullInventory": len(files), "preserved": 43, "sealedCases": 37, "selftestMethods": 32,
                  "sortCounterexamples": sort_examples}, ensure_ascii=False, indent=2))
