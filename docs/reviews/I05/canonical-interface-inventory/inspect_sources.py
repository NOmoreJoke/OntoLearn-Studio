"""Static inventory of exactly eight controller-bound fixed Git source files.

Never imports the product or follows its imports. Source command stdout remains
losslessly available as its immutable Git blob; only identities/interfaces are
written into this documentation tree.
"""

import ast
import base64
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/reviews/I05/canonical-interface-inventory"
ITER = ROOT / "docs/iterations/I05/canonical-interface-inventory"
BINDING = Path(
    "/Users/kyle/Documents/工作/知爻/本体/iteration-control/"
    "2026-10-21-weekly-release/"
    "I05-M02-M05-eight-source-static-read-binding-20261022.json"
)
REF = "2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64"
NAMES = {
    "semantic.py", "semantic_scopes.py", "semantic_query.py",
    "semantic_error_adapter.py", "semantic_execution.py",
    "semantic_profile_input.py", "semantic_source_package_probe.py",
    "rdf_snapshot.py",
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def definitions(nodes, prefix=""):
    result = []
    for node in nodes:
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name = prefix + node.name
        item = {
            "name": name, "kind": type(node).__name__,
            "line": node.lineno, "endLine": node.end_lineno,
        }
        if isinstance(node, ast.ClassDef):
            item["bases"] = [ast.unparse(v) for v in node.bases]
            item["annotatedFields"] = [
                {"name": ast.unparse(v.target), "annotation": ast.unparse(v.annotation),
                 "line": v.lineno, "hasDefault": v.value is not None}
                for v in node.body if isinstance(v, ast.AnnAssign)
            ]
        else:
            item["signature"] = ast.unparse(node.args)
            item["returns"] = ast.unparse(node.returns) if node.returns else None
        result.append(item)
        result.extend(definitions(node.body, name + "."))
    return result


def main():
    binding_bytes = BINDING.read_bytes()
    binding = json.loads(binding_bytes)
    entries = binding["files"]
    assert len(entries) == 8
    assert {Path(e["path"]).name for e in entries} == NAMES
    assert {e["path"] for e in entries} == {
        "packages/engine/src/ontolearn_engine/" + name for name in NAMES
    }
    assert all(e["ref"] == REF for e in entries)
    repo = Path(binding["sourceWorkspace"])
    assert repo == Path("/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-source-package-probe")
    commands, modules = [], []
    for entry in entries:
        argv = ["git", "show", REF + ":" + entry["path"]]
        proc = subprocess.run(argv, cwd=repo, capture_output=True)
        commands.append({
            "argv": argv, "cwd": str(repo), "exitCode": proc.returncode,
            "stdout": {"preservedAt": "immutable-fixed-Git-blob",
                       "ref": REF, "path": entry["path"],
                       "bytes": len(proc.stdout),
                       "sha256": hashlib.sha256(proc.stdout).hexdigest()},
            "stderr": {"base64": base64.b64encode(proc.stderr).decode(),
                       "bytes": len(proc.stderr),
                       "sha256": hashlib.sha256(proc.stderr).hexdigest()},
        })
        assert proc.returncode == 0, entry["path"]
        assert len(proc.stdout) == entry["bytes"]
        assert hashlib.sha256(proc.stdout).hexdigest() == entry["sha256"]
        tree = ast.parse(proc.stdout.decode("utf-8"), filename=entry["path"])
        imports = [
            {"line": node.lineno, "statement": ast.unparse(node)}
            for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        modules.append({**entry, "importsNotFollowed": imports,
                        "definitions": definitions(tree.body)})
    ITER.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dump(ITER / "source-inputs.json", {
        "format": "i05-canonical-interface-static-inputs/1",
        "bindingPath": str(BINDING), "bindingBytes": len(binding_bytes),
        "bindingSha256": hashlib.sha256(binding_bytes).hexdigest(),
        "sourceWorkspace": str(repo), "sourceRef": REF, "files": entries,
        "sourceFactsOnly": True, "executionAuthorization": False,
    })
    dump(OUT / "source-index.json", {
        "format": "i05-static-source-index/1", "modules": modules,
        "noProductImportExecutionOrImportFollowing": True,
        "indexDoesNotProveCompleteCodecOrSameIssueAuthority": True,
    })
    dump(OUT / "source-read-commands.json", {
        "commands": commands,
        "stdoutPreservation": "Each complete stdout is the exact fixed Git blob identified above; no reconstructed or truncated source stream.",
        "productExecuted": False,
    })
    print("Indexed exactly eight fixed sources via AST only; no product execution.")
    for module in modules:
        print(Path(module["path"]).name, len(module["definitions"]), "definitions")


if __name__ == "__main__":
    main()
