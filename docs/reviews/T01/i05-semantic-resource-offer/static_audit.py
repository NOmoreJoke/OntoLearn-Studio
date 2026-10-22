"""Read fixed Git text with stdlib AST/JSON/hash; never import supplier code."""
import ast
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

BASE = "5f910b52c69d86a1076b2032e5d3c63e715947f3"
SUPPLIER = "6891a5842302859a531cf82767c5a482417bc274"
DOCS = "ee2b30a2dad35b2d395f9c735aff80371ab41110"
HERE = Path(__file__).resolve().parent


def git(ref, path):
    return subprocess.check_output(["git", "show", ref + ":" + path], cwd=HERE)


def identity(ref, path):
    raw = git(ref, path)
    return {
        "ref": ref,
        "path": path,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "gitBlob": subprocess.check_output(
            ["git", "rev-parse", ref + ":" + path], cwd=HERE, text=True
        ).strip(),
    }


def document(ref, path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    return json.loads(git(ref, path), object_pairs_hook=unique)


def functions(raw):
    return {
        node.name: ast.dump(node, include_attributes=False)
        for node in ast.parse(raw).body
        if isinstance(node, ast.FunctionDef)
    }


def main():
    paths = [
        "packages/contracts/python/contract_v2.py",
        "packages/contracts/v2/schema.json",
        "packages/contracts/v2/registry.json",
        "packages/contracts/v2/errors.json",
    ]
    shared = []
    for path in paths:
        shared.append({"supplier": identity(SUPPLIER, path), "baseline": identity(BASE, path)})
    schema_path, registry_path, errors_path = paths[1:]
    schema = document(SUPPLIER, schema_path)
    registry = document(SUPPLIER, registry_path)
    errors = document(SUPPLIER, errors_path)
    old_schema = document(BASE, schema_path)
    old_registry = document(BASE, registry_path)
    old_errors = document(BASE, errors_path)
    definitions = schema["$defs"]
    keywords = next(
        ast.literal_eval(node.value)
        for node in ast.parse(git(SUPPLIER, paths[0])).body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "KEYWORDS" for t in node.targets)
    )
    refs, unsupported = [], []

    def walk(node, location):
        if not isinstance(node, dict):
            raise ValueError("Non-schema at " + location)
        extra = sorted(set(node) - keywords)
        if extra:
            unsupported.append({"location": location, "keywords": extra})
        if "$ref" in node:
            target = node["$ref"]
            assert target.startswith("#/$defs/") and target[8:] in definitions
            refs.append({"from": location, "target": target})
        for key in ("items", "propertyNames"):
            if key in node:
                walk(node[key], location + "/" + key)
        if isinstance(node.get("additionalProperties"), dict):
            walk(node["additionalProperties"], location + "/additionalProperties")
        for key, child in node.get("properties", {}).items():
            walk(child, location + "/properties/" + key)
        for i, child in enumerate(node.get("oneOf", [])):
            walk(child, location + "/oneOf/" + str(i))

    for name, definition in definitions.items():
        walk(definition, "#/$defs/" + name)
    branches = {
        branch["properties"]["code"]["const"]: branch
        for branch in definitions["error"]["oneOf"]
    }
    assert len(branches) == len(definitions["error"]["oneOf"]) == len(errors["codes"])
    assert set(branches) == set(errors["codes"])
    for code, spec in errors["codes"].items():
        branch = branches[code]
        assert branch["properties"]["messageKey"] == {"const": spec["messageKey"]}
        assert branch["properties"]["retryable"] == {"const": spec["retryable"]}
        assert branch["properties"]["params"] == spec["paramsSchema"]
        assert set(branch["required"]) == {"code", "messageKey", "retryable", "params"}
        assert branch["additionalProperties"] is False
    old_funcs = functions(git(BASE, paths[0]))
    new_funcs = functions(git(SUPPLIER, paths[0]))
    closure = document(
        DOCS, "docs/reviews/I05/source-package-parity-contract/static-import-closure.json"
    )
    modules = {item["module"]: item for item in closure["modules"]}
    source_records, edges, unresolved, resource_calls, import_sites = [], set(), [], [], []
    forbidden = {
        "resource_manifest", "build_request", "execute_request", "derive_dependencies", "permits_transition"
    }
    forbidden_call_sites = []
    for name, item in modules.items():
        raw = git(SUPPLIER, item["path"])
        assert len(raw) == item["bytes"] and hashlib.sha256(raw).hexdigest() == item["sha256"]
        source_records.append(identity(SUPPLIER, item["path"]))
        tree = ast.parse(raw)
        package = name if item["path"].endswith("/__init__.py") else name.rsplit(".", 1)[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in modules:
                        edges.add((name, alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                target = (
                    importlib.util.resolve_name("." * node.level + (node.module or ""), package)
                    if node.level else node.module
                )
                if node.module and target in modules:
                    edges.add((name, target, node.lineno))
                for alias in node.names:
                    child = target + "." + alias.name
                    if child in modules:
                        edges.add((name, child, node.lineno))
                if target.startswith("ontolearn_engine") and target not in modules:
                    unresolved.append({"source": name, "target": target, "line": node.lineno})
                if "resources" in (node.module or ""):
                    import_sites.append({"module": name, "line": node.lineno, "text": ast.unparse(node)})
            elif isinstance(node, ast.Call):
                expression = ast.unparse(node.func)
                if expression == "semantic_identity" or expression.startswith(("CONTRACT.", "resources.")):
                    resource_calls.append({"module": name, "line": node.lineno, "call": ast.unparse(node)})
                if expression.rsplit(".", 1)[-1] in forbidden:
                    forbidden_call_sites.append({"module": name, "line": node.lineno, "call": ast.unparse(node)})
    expected_edges = {tuple(edge) for edge in closure["edges"]}
    edge_missing, edge_extra = sorted(expected_edges - edges), sorted(edges - expected_edges)
    lock = identity(SUPPLIER, "uv.lock")
    result = {
        "scope": "Static limited owner offer only, not product/checker execution or runtime validation",
        "base": BASE,
        "supplierRef": SUPPLIER,
        "contractDocsRef": DOCS,
        "sharedResourceIdentities": shared,
        "schema": {
            "baselineDefinitionCount": len(old_schema["$defs"]),
            "supplierDefinitionCount": len(definitions),
            "added": sorted(set(definitions) - set(old_schema["$defs"])),
            "removed": sorted(set(old_schema["$defs"]) - set(definitions)),
            "changedExisting": sorted(k for k in old_schema["$defs"] if definitions.get(k) != old_schema["$defs"][k]),
            "referenceCount": len(refs), "references": refs, "unsupportedKeywords": unsupported,
        },
        "registry": {
            "changedTopLevelKeys": sorted(k for k in set(old_registry) | set(registry) if old_registry.get(k) != registry.get(k)),
            "baselineCapabilities": len(old_registry["capabilities"]),
            "supplierCapabilities": len(registry["capabilities"]),
            "addedCapabilities": sorted(set(registry["capabilities"]) - set(old_registry["capabilities"])),
            "changedExistingCapabilities": sorted(k for k in old_registry["capabilities"] if registry["capabilities"].get(k) != old_registry["capabilities"][k]),
            "v2RuntimeUnchanged": registry["v2Runtime"] == old_registry["v2Runtime"],
            "unadoptedFoundationProfiles": registry.get("foundationProfiles"),
        },
        "errors": {
            "ordinaryCodeCount": len(errors["codes"]),
            "ordinaryCodes": sorted(errors["codes"]),
            "allOldTopLevelFieldsUnchanged": all(errors.get(k) == value for k, value in old_errors.items()),
            "ordinaryCatalogMatchesSchemaBranches": True,
            "encodedLimit": errors["maxEncodedBytes"],
            "unadoptedAddedTopLevelFields": sorted(set(errors) - set(old_errors)),
        },
        "checker": {
            "addedFunctions": sorted(set(new_funcs) - set(old_funcs)),
            "removedFunctions": sorted(set(old_funcs) - set(new_funcs)),
            "changedExistingFunctions": sorted(k for k in old_funcs if new_funcs.get(k) != old_funcs[k]),
            "topLevelReads": ["schema.json", "registry.json", "errors.json"],
            "allowedErrorValidationTransitiveFunctions": ["validate", "check", "equal", "semantic", "encoded_size", "_changeset_semantics"],
            "errorNameChangesetSemanticsFallsThroughTrue": "Manually inspected fixed checker lines266-309; not executed",
        },
        "closure": {
            "moduleCount": len(modules), "identities": source_records,
            "literalEdgeCount": len(edges), "literalEdgesMissingFromOurExtraction": edge_missing,
            "literalEdgesExtraInOurExtraction": edge_extra,
            "unresolvedLiteralTargets": unresolved,
            "resourceImportSites": import_sites, "resourceCallSites": resource_calls,
            "forbiddenNamedCallSitesIncludingUncalledDefinitions": forbidden_call_sites,
            "callGraphLimit": "AST literal names and manual owner-scope review, not dynamic import or future probe/runtime absence proof",
        },
        "resourceSidecar": {
            "resources": identity(SUPPLIER, "packages/engine/src/ontolearn_engine/resources.py"),
            "uvLockNotAdoptedByT01": lock,
            "registryReadTwice": "checker json text plus resources.REGISTRY_BYTES hash, both same exact bytes",
            "sourceLayout": {"checker": "packages/contracts/python/contract_v2.py", "jsonRoot": "packages/contracts/v2", "lock": "uv.lock"},
            "frozenLayout": {"checker": "contracts/python/contract_v2.py", "jsonRoot": "contracts/v2", "lock": "provenance/uv.lock"},
            "moduleIdentity": "canonical ontolearn_engine.resources loads one CONTRACT module object named ontolearn_contract_v2 via spec/exec_module; sys.modules caching not implemented here, no runtime uniqueness claim",
        },
        "executed": ["Git text reads", "stdlib AST", "stdlib JSON duplicate-key/ref/catalog comparison", "SHA256"],
        "notExecuted": ["supplier imports", "checker functions", "tests", "builds", "DB", "native", "GUI", "business child", "formatter"],
    }
    assert not unsupported and not edge_missing and not edge_extra
    output = HERE / "static-audit.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output), "bytes": output.stat().st_size,
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                      "modules": len(modules), "edges": len(edges), "refs": len(refs),
                      "forbiddenLexicalSites": forbidden_call_sites,
                      "resourceCalls": resource_calls}, ensure_ascii=False))


if __name__ == "__main__":
    main()
