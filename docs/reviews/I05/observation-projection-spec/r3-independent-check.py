"""R3 independent fixed-tree identity and bounded execution evidence.

Only r3-proof.json and new r3-independent-* artifacts are written. Every retained
subprocess stream is a lossless UTF-8 JSON string carrier, never a raw diff file.
No product/third-party/network code is imported or executed.
"""
import ast
import hashlib
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
REVISION = "755326a26306f5bce0f36c172bd4994c7340f235"
CANDIDATE = "49e55cfdc68adca7f04faaf4f2335d1072553045"
PROCESS = "fb7dfbb676cd1f09030ab508a3625284bfd6d9e4"
PREFIXES = ["docs/iterations/I05/observation-projection-spec/", "docs/reviews/I05/observation-projection-spec/"]
RAW = PREFIXES[1] + "r2-independent-full-diff.stdout.txt"
PYTHON = "/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12"
proof = {"format": "i05-observation-independent-r3/1", "base": BASE,
         "revisionBase": REVISION, "candidate": CANDIDATE, "process": PROCESS,
         "commands": [], "results": {}, "productExecuted": False}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def dump(value, path):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

def save():
    dump(proof, OUT / "r3-proof.json")

def carrier(data, tag, stream):
    value = {"encoding": "utf-8-json-string", "bytes": len(data), "sha256": sha(data), "text": data.decode("utf-8")}
    path = OUT / ("r3-independent-" + tag + "." + stream + ".json")
    dump(value, path)
    roundtrip = json.loads(path.read_text())["text"].encode("utf-8")
    assert roundtrip == data
    return {"path": str(path.relative_to(ROOT)), "encoding": value["encoding"], "bytes": len(data),
            "sha256": sha(data), "carrierBytes": len(path.read_bytes()), "carrierSHA256": sha(path.read_bytes())}

def run(argv, tag=None, expected=(0,)):
    r = subprocess.run(argv, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, check=False)
    row = {"argv": argv, "cwd": str(ROOT), "exitCode": r.returncode}
    for stream, data in [("stdout", r.stdout), ("stderr", r.stderr)]:
        row[stream] = carrier(data, tag, stream) if tag else {"bytes": len(data), "sha256": sha(data)}
    proof["commands"].append(row)
    if r.returncode and "firstNonzeroCommand" not in proof:
        proof["firstNonzeroCommand"] = {"index": len(proof["commands"]) - 1, **row}
    save()
    assert r.returncode in expected, ("unexpected bounded command exit", r.returncode)
    return r.stdout, r.stderr, r.returncode

def blob(ref, path):
    return run(["git", "show", ref + ":" + path])[0]

def loads(data):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result: raise ValueError("duplicate member")
            result[key] = value
        return result
    def bad(_): raise ValueError("nonfinite constant")
    return json.loads(data, object_pairs_hook=pairs, parse_constant=bad)

assert run(["git", "rev-parse", "HEAD"], "head")[0].decode().strip() == PROCESS
run(["git", "status", "--short", "--untracked-files=all"], "start-status")
assert not run(["git", "diff", "--cached", "--name-only"], "staged")[0]
delta = run(["git", "diff", "--name-status", REVISION, CANDIDATE], "delta-name-status")[0].decode().splitlines()
assert len(delta) == 21
assert {row[2:] for row in delta if row.startswith("M\t")} == {PREFIXES[0] + "model.py", PREFIXES[0] + "spec.md"}
run(["git", "diff", REVISION, CANDIDATE], "full-diff")
assert run(["git", "diff", "--name-only", CANDIDATE, PROCESS], "process-delta")[0].decode().splitlines() == [PREFIXES[1] + "candidate-receipt-r3.json"]
paths = run(["git", "ls-tree", "-r", "--name-only", PROCESS, "--", *PREFIXES])[0].decode().splitlines()
assert len(paths) == 121
identities = []
for path in paths:
    b = (ROOT / path).read_bytes()
    assert b == blob(PROCESS, path)
    identities.append({"path": path, "bytes": len(b), "sha256": sha(b), "currentEqualsProcess": True})
proof["results"]["fullInventory"] = identities
for name, size, digest in [
    ("manifest-r3.json", 25501, "f8aac6b92326cfa094db7f2deadc498cd0bcfb96ba6948013bd2fe6f458c70f6"),
    ("candidate-receipt-r3.json", 47004, "91055f397914c55a735aed645084c542d342d644595998be22f744f648776e66")]:
    b = (OUT / name).read_bytes()
    assert len(b) == size and sha(b) == digest
manifest = loads((OUT / "manifest-r3.json").read_bytes())
receipt = loads((OUT / "candidate-receipt-r3.json").read_bytes())
assert len(manifest["files"]) == 119 and len(receipt["candidateCompleteInventory"]) == 120
for row in manifest["files"] + receipt["candidateCompleteInventory"]:
    b = (ROOT / row["path"]).read_bytes()
    assert len(b) == row["bytes"] and sha(b) == row["sha256"]
    assert b == blob(CANDIDATE, row["path"])
declaration = loads((OUT / "delta-r3.json").read_bytes())
assert len(declaration["preservedFiles"]) == 99
for row in declaration["preservedFiles"]:
    b = (ROOT / row["path"]).read_bytes()
    assert b == blob(REVISION, row["path"])
    assert len(b) == row["bytes"] and sha(b) == row["sha256"]
assert sha((ROOT / "AGENTS.md").read_bytes()) == "78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759"
proof["results"]["priorImmutableFiles"] = 99

raw = (ROOT / RAW).read_bytes()
assert len(raw) == 128276 and sha(raw) == "13c4471bc5518f354b8315220c14b8fbd5f722c722075ed93c1fc29183b01477"
original_diff = run(["git", "diff", "57c67631fab6a36f47963aca95b4036064e10777", "1e753a82b837fb53f0389dabf1c401d89809238c"])[0]
assert original_diff == raw
full_stdout, full_stderr, full_exit = run(["git", "diff", "--check", BASE, PROCESS, "--", "."], "full-diffcheck", expected=(2,))
assert full_exit == 2 and not full_stderr
diagnostic_lines = [line for line in full_stdout.decode().splitlines() if line.endswith("trailing whitespace.")]
assert diagnostic_lines and all(line.startswith(RAW + ":") for line in diagnostic_lines)
assert all(line.startswith(RAW + ":") or line == "+ " for line in full_stdout.decode().splitlines())
run(["git", "diff", "--check", BASE, PROCESS, "--", ".", ":(exclude)" + RAW], "single-transcript-excluded-diffcheck")
run(["git", "diff", "--check", REVISION, PROCESS, "--", "."], "revision-diffcheck")
proof["results"]["whitespaceScope"] = {"fullBaseToProcessExit": full_exit, "onlyDiagnosticPath": RAW,
    "diagnosticCount": len(diagnostic_lines), "exactSingleTranscriptExcludedExit": 0, "revisionToProcessExit": 0,
    "fullCheckPass": False, "originalRawRecomputedUnchanged": True}

for name in ["r3-full-diffcheck.stdout.json", "r3-full-diffcheck.stderr.json", "r3-single-transcript-excluded-diffcheck.stdout.json", "r3-single-transcript-excluded-diffcheck.stderr.json", "r3-revision-diffcheck.stdout.json", "r3-revision-diffcheck.stderr.json"]:
    item = loads((OUT / name).read_bytes())
    b = item["text"].encode()
    assert len(b) == item["bytes"] and sha(b) == item["sha256"]
assert loads((OUT / "r3-full-diffcheck.stdout.json").read_bytes())["text"].encode() == full_stdout

before = loads(blob(REVISION, PREFIXES[0] + "cases.json"))
after = loads((DESIGN / "cases.json").read_bytes())
assert before == after and len(after["cases"]) == 37
for name in ["schema.json", "pure-sources.json", "selftest.py", "selftest-r2.py"]:
    assert (DESIGN / name).read_bytes() == blob(REVISION, PREFIXES[0] + name)
proof["results"]["all37CompleteCasesAndSchemaInputsOldTestsUnchanged"] = True
for name in ["model.py", "selftest.py", "selftest-r2.py", "selftest-r3.py"]:
    tree = ast.parse((DESIGN / name).read_text())
    imports = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): imports.extend(a.name for a in n.names)
        if isinstance(n, ast.ImportFrom): imports.append(n.module)
    assert set(imports) <= {"hashlib", "itertools", "json", "re", "copy", "pathlib", "sys", "unittest", "subprocess", "importlib.util", "model", "selftest"}
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in {"write_text", "write_bytes", "unlink", "mkdir"} for n in ast.walk(tree))
run([PYTHON, PREFIXES[0] + "selftest-r3.py"], "selftest-41")
proof["results"]["selftestMethods"] = 41
save()
print(json.dumps({"files": 121, "priorImmutableFiles": 99, "unchangedCases": 37, "selftestMethods": 41,
                  "whitespaceScope": proof["results"]["whitespaceScope"]}, ensure_ascii=False, indent=2))
