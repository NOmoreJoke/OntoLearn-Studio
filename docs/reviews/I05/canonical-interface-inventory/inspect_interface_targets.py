"""Extract only bound interface declarations, never execute product sources."""

import ast
import base64
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/reviews/I05/canonical-interface-inventory"
ITER = ROOT / "docs/iterations/I05/canonical-interface-inventory"
CONTROL = Path("/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release")
BINDING = CONTROL / "I05-M02-M05-additional-interface-static-read-binding-20261022.json"
REF = "2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64"


def fresh(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def function_header(node):
    return {"name": node.name, "line": node.lineno, "endLine": node.end_lineno,
            "signature": ast.unparse(node.args),
            "returnAnnotation": ast.unparse(node.returns) if node.returns else None}


def declaration(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return function_header(node)
    result = {"name": node.name, "line": node.lineno, "endLine": node.end_lineno,
              "bases": [ast.unparse(v) for v in node.bases],
              "decorators": [ast.unparse(v) for v in node.decorator_list]}
    result["fields"] = [
        {"name": ast.unparse(n.target), "annotation": ast.unparse(n.annotation),
         "line": n.lineno,
         "defaultSyntax": ast.unparse(n.value) if n.value is not None else None}
        for n in node.body if isinstance(n, ast.AnnAssign)
    ]
    result["methodInterfacesOnly"] = [
        function_header(n) for n in node.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    # Only assignment targets, never right-hand arithmetic/rates or ledger logic.
    init = next((n for n in node.body if isinstance(n, ast.FunctionDef)
                 and n.name == "__init__"), None)
    targets = []
    if init is not None:
        for n in ast.walk(init):
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                if isinstance(n.value, ast.Name) and n.value.id == "self":
                    targets.append({"field": n.attr, "line": n.lineno})
    result["constructorAssignedFieldNamesOnly"] = targets
    return result


def main():
    raw = BINDING.read_bytes()
    binding = json.loads(raw)
    assert binding["ref"] == REF
    entries = binding["inputs"]
    assert len(entries) == 12
    repo = Path(binding["sourceRepo"])
    assert repo == Path("/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-source-package-probe")
    records, commands = [], []
    for entry in entries:
        if "functionOnly" in entry:
            # Never read the resources.py whole Git blob, body, or globals.
            path = CONTROL / entry["approvedFragment"]
            data = path.read_bytes()
            assert len(data) == entry["fragmentBytes"]
            assert hashlib.sha256(data).hexdigest() == entry["fragmentSHA256"]
            tree = ast.parse(data.decode("utf-8"))
            records.append({**entry, "textSource": str(path),
                            "definitions": [declaration(n) for n in tree.body
                                            if isinstance(n, ast.FunctionDef)]})
            continue
        argv = ["git", "show", REF + ":" + entry["path"]]
        proc = subprocess.run(argv, cwd=repo, capture_output=True)
        commands.append({
            "argv": argv, "cwd": str(repo), "exitCode": proc.returncode,
            "stdout": {"preservedAt": "immutable-fixed-Git-blob", "ref": REF,
                       "path": entry["path"], "bytes": len(proc.stdout),
                       "sha256": hashlib.sha256(proc.stdout).hexdigest()},
            "stderr": {"base64": base64.b64encode(proc.stderr).decode(),
                       "bytes": len(proc.stderr),
                       "sha256": hashlib.sha256(proc.stderr).hexdigest()},
        })
        assert proc.returncode == 0
        assert len(proc.stdout) == entry["bytes"]
        assert hashlib.sha256(proc.stdout).hexdigest() == entry["sha256"]
        tree = ast.parse(proc.stdout.decode("utf-8"))
        top = {n.name: n for n in tree.body
               if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))}
        records.append({**entry,
                        "topLevelNamesForLocationOnly": [
                            {"name": n.name, "kind": type(n).__name__, "line": n.lineno}
                            for n in top.values()],
                        "definitions": [declaration(top[name]) for name in entry["namedTargets"]
                                        if name in top],
                        "missingNamedTargets": [name for name in entry["namedTargets"]
                                                if name not in top]})
    fresh(ITER / "additional-source-inputs.json", {
        "format": "i05-additional-interface-inputs/1", "bindingPath": str(BINDING),
        "bindingBytes": len(raw), "bindingSha256": hashlib.sha256(raw).hexdigest(),
        "inputs": entries, "sourceFactsOnly": True, "noExecution": True,
    })
    fresh(OUT / "additional-source-index.json", {
        "format": "i05-bound-interface-declarations/1", "records": records,
        "resourceWholeSourceRead": False,
        "ledgerArithmeticOrRatesInspected": False,
        "declarationIndexIsNotNormativeAdoption": True,
    })
    fresh(OUT / "additional-read-commands.json", {
        "commands": commands,
        "stdoutPreservedAtFixedGitObject": True,
        "resourceFragmentVerifiedSeparately": True, "productExecuted": False,
    })
    print("Indexed eleven bound interface declarations and one approved fragment only.")
    for record in records:
        print(Path(record["path"]).name, "targets", len(record["definitions"]),
              "missing", record.get("missingNamedTargets", []))


if __name__ == "__main__":
    main()
