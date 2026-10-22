"""R1 evidence only. Standard library; read fixed Git bytes and detached design JSON.

Writes only r1-proof.json and r1-command-* within this review directory. Never
imports product code, creates product objects, calls third party or network.
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
BASE = "5f910b52c69d86a1076b2032e5d3c63e715947f3"
CANDIDATE = "dd3e659e9214481700275afb3f3188891e42359d"
PROCESS = "6b665455a4cb88a9744c1b8d67573c5adf0c95f6"
PYTHON = "/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12"
COMMANDS = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def run(argv, retain=False):
    result = subprocess.run(argv, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, check=False)
    item = {"argv": argv, "cwd": str(ROOT), "exitCode": result.returncode,
            "stdoutBytes": len(result.stdout), "stdoutSHA256": sha(result.stdout),
            "stderrBytes": len(result.stderr), "stderrSHA256": sha(result.stderr)}
    if retain:
        prefix = OUT / ("r1-command-" + str(len(COMMANDS)))
        for name, data in [("stdout", result.stdout), ("stderr", result.stderr)]:
            p = Path(str(prefix) + "." + name + ".txt")
            p.write_bytes(data)
            item[name + "Path"] = str(p.relative_to(ROOT))
    COMMANDS.append(item)
    if result.returncode:
        raise RuntimeError("bounded reviewer command failed: " + argv[0])
    return result.stdout

def git_blob(ref, path):
    return run(["git", "show", ref + ":" + path])

def load(path):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("duplicate key")
            out[k] = v
        return out
    def bad(_):
        raise ValueError("nonfinite")
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=bad)

head = run(["git", "rev-parse", "HEAD"], True).decode().strip()
assert head == PROCESS
status = run(["git", "status", "--short"], True).decode()
delta = run(["git", "diff", "--name-only", BASE, PROCESS], True).decode().splitlines()
assert len(delta) == 19
assert all(p.startswith(("docs/iterations/I05/observation-projection-spec/", "docs/reviews/I05/observation-projection-spec/")) for p in delta)
files = []
for p in delta:
    b = (ROOT / p).read_bytes()
    assert b == git_blob(PROCESS, p)
    files.append({"path": p, "bytes": len(b), "sha256": sha(b), "currentEqualsProcess": True})
manifest = load(OUT / "manifest.json")
receipt = load(OUT / "candidate-receipt.json")
for row in manifest["files"] + receipt["candidateFilesCurrentEqualsGitEqualsSHA"]:
    b = (ROOT / row["path"]).read_bytes()
    assert len(b) == row["bytes"] and sha(b) == row["sha256"]
    assert b == git_blob(CANDIDATE, row["path"])
assert len((OUT / "manifest.json").read_bytes()) == 3977
assert sha((OUT / "manifest.json").read_bytes()) == "6900517c540f1d15b0d105cfe0cd48c32e71bc42e64f174ee12530cc5f578be2"
assert len((OUT / "candidate-receipt.json").read_bytes()) == 5063
assert sha((OUT / "candidate-receipt.json").read_bytes()) == "a7d221a2faa0dd2b1a924b4e9591c6c6e5165a2c978d0e68eb805765d691238d"
assert sha((ROOT / "AGENTS.md").read_bytes()) == "78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759"
source_checks = []
ledger = load(OUT / "source-ledger.json")
blobs = {}
for row in ledger["sources"]:
    b = git_blob(row["ref"], row["path"]) if "ref" in row else Path(row["path"]).read_bytes()
    assert len(b) == row["bytes"] and sha(b) == row["sha256"]
    if "ref" in row:
        blobs[(row["ref"], row["path"])] = b
    source_checks.append({"path": row["path"], "ref": row.get("ref"), "identityVerified": True})
for row in load(OUT / "literal-excerpts.json"):
    b = blobs[(row["ref"], row["path"])]
    lines = b.decode().splitlines()
    for frag in row["ranges"]:
        assert lines[frag["start"] - 1:frag["end"]] == frag["lines"]
raw = load(OUT / "I05-observation-literal-enum-reference.json.raw")
for row in raw["declarations"]:
    b = blobs[(raw["ref"], row["path"])]
    fragment = b.splitlines(keepends=True)[row["lineStart"] - 1:row["lineEnd"]]
    fragment = b"".join(fragment)
    assert len(b) == row["sourceBytes"] and sha(b) == row["sourceSHA256"]
    assert fragment.decode() == row["fragment"] and sha(fragment) == row["fragmentSHA256"]
defaults = load(OUT / "I05-canonical-profile-api-defaults-reference.json.raw")
b = git_blob(defaults["ref"], defaults["path"])
assert len(b) == defaults["bytes"] and sha(b) == defaults["sha256"]
# Parse the approved declaration fragment only. Function bodies are neither decoded
# for display nor imported/evaluated. The fixed file's full bytes were hash input.
for row in defaults["functions"]:
    lines = b.splitlines()
    i = row["line"] - 1
    declaration = []
    while True:
        line = lines[i].decode()
        declaration.append(line)
        if line.rstrip().endswith(":"):
            break
        i += 1
    node = ast.parse("\n".join(declaration) + "\n    pass\n").body[0]
    args = ast.unparse(node.args)
    assert args == row["parameterDeclaration"]

sources = load(DESIGN / "pure-sources.json")
cases = load(DESIGN / "cases.json")["cases"]
sealed = json.loads(blobs[("0e42a0fe349054a92817cb4d463bccdc15f6c042", "packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-inputs.json")])
oracle = json.loads(blobs[("3d8f4ee912f41bd03388322d29a9bfc0e7defe85", "tests/fixtures/quality/i05-source-package-oracle/oracle.json")])
print("sealed top keys", list(sealed), "oracle top keys", list(oracle))
print("sealed field types", {k: type(v).__name__ for k, v in sealed.items()})
print("oracle field types", {k: type(v).__name__ for k, v in oracle.items()})

for filename in ["model.py", "selftest.py"]:
    tree = ast.parse((DESIGN / filename).read_text())
    imports = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): imports.extend(a.name for a in n.names)
        if isinstance(n, ast.ImportFrom): imports.append(n.module)
    assert set(imports) <= {"hashlib", "itertools", "json", "re", "copy", "pathlib", "sys", "unittest", "model"}

run([PYTHON, str((DESIGN / "selftest.py").relative_to(ROOT))], True)
proof = {"format": "i05-observation-independent-review-r1-proof/1", "base": BASE,
         "candidate": CANDIDATE, "process": PROCESS, "head": head,
         "statusAtIdentityRunnerStart": status, "files": files,
         "sourceIdentityChecks": source_checks, "commands": COMMANDS,
         "scope": "stdlib detached design only; no product/third party/network/GUI/runtime identity proof"}
(OUT / "r1-proof.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")
print("identity and selftest checks passed")
