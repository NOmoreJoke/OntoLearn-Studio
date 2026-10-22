"""External, finite document assertions only. No product imports, execution or fixtures.
This is not a JSONSchema2020-12 engine. It checks only the explicitly listed
shape keywords and finite relationships used by the accompanying synthetic data.
It cannot validate real archives, loaders, installs, licenses or approval.
"""
import base64
import copy
import hashlib
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parents[3] / "iterations/T03/i05-semantic-build-protocol"
HERE = pathlib.Path(__file__).resolve().parent


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            assert key not in result, ("duplicate-key", key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def resolve(schema, pointer):
    assert pointer.startswith("#/")
    node = schema
    for part in pointer[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def structural(value, node, schema):
    """Limited structural assertions; not standards compliance or engine validation."""
    if "$ref" in node:
        structural(value, resolve(schema, node["$ref"]), schema)
    if "const" in node:
        assert type(value) is type(node["const"]) and value == node["const"]
    if "enum" in node:
        assert any(type(value) is type(x) and value == x for x in node["enum"])
    for union in ["anyOf", "oneOf"]:
        if union in node:
            successes = 0
            for branch in node[union]:
                try:
                    structural(value, branch, schema)
                    successes += 1
                except (AssertionError, KeyError, TypeError):
                    pass
            assert successes >= 1 if union == "anyOf" else successes == 1
    if "type" in node:
        kinds = node["type"] if isinstance(node["type"], list) else [node["type"]]
        matches = {"object": type(value) is dict, "array": type(value) is list,
                   "string": type(value) is str, "integer": type(value) is int,
                   "boolean": type(value) is bool, "null": value is None}
        assert any(matches[k] for k in kinds)
    if type(value) is dict and "properties" in node:
        assert set(node.get("required", [])) <= set(value)
        if node.get("additionalProperties") is False:
            assert set(value) <= set(node["properties"])
        for key in value.keys() & node["properties"].keys():
            structural(value[key], node["properties"][key], schema)
    if type(value) is list:
        assert node.get("minItems", 0) <= len(value) <= node.get("maxItems", float("inf"))
        if "items" in node:
            for item in value:
                structural(item, node["items"], schema)
    if type(value) is str:
        assert node.get("minLength", 0) <= len(value) <= node.get("maxLength", float("inf"))
        if "pattern" in node:
            assert re.search(node["pattern"], value)
    if type(value) is int:
        assert value >= node.get("minimum", float("-inf"))


def same_file(a, b):
    assert (a["path"], a["bytes"], a["sha256"]) == (b["path"], b["bytes"], b["sha256"])


def relations(x, profile):
    b, f, v = x["provenance"], x["buildReceipt"], x["validationReceipt"]
    expected = [m["module"] for m in profile["canonicalModules"]]
    modules = b["moduleBindings"]
    assert [m["canonicalName"] for m in modules] == expected
    bindings = {m["bindingId"]: m for m in modules + [b["distributionCodeBinding"]]}
    assert len(bindings) == 24
    for module, source in zip(modules, b["inputs"]["modules"]):
        assert module["bindingId"] == "canonical:" + module["canonicalName"]
        assert module["sourceCompilation"]["source"] == source
        assert module["sourceCompilation"]["fingerprint"] == module["actualArchiveCode"]["fingerprint"]
        assert module["sourceCompilation"]["source"]["sha256"] != module["actualArchiveCode"]["fingerprint"]["sha256"]
    assert modules[-1]["role"] == "canonical-probe"
    archives = {}
    depths = {}
    for archive in b["archives"]:
        aid = archive["archiveId"]
        assert aid not in archives
        loc = archive["location"]
        assert set(loc) in [{"file"}, {"parentMember"}]
        if "file" in loc:
            assert aid in ["carchive-main", "external-pyc-main"]
            assert archive["kind"] == {"carchive-main": "CArchive", "external-pyc-main": "external-pyc"}[aid]
            assert loc["file"]["root"] == "bundle-root"
            assert (archive["bytes"], archive["sha256"]) == (loc["file"]["bytes"], loc["file"]["sha256"])
            if aid == "carchive-main":
                same_file(loc["file"], f["executable"])
            depths[aid] = 1
        else:
            pm = loc["parentMember"]
            assert aid == "pyz-main" and archive["kind"] == "PYZ"
            assert pm["parentArchiveId"] in archives
            parent = archives[pm["parentArchiveId"]]
            member = next(i for i in parent["inventory"] if i["name"] == pm["memberName"])
            assert (member["bytes"], member["sha256"]) == (pm["rawMemberBytes"], pm["rawMemberSha256"])
            assert (archive["bytes"], archive["sha256"]) == (member["bytes"], member["sha256"])
            depths[aid] = depths[pm["parentArchiveId"]] + 1
        assert depths[aid] <= 2
        assert len({i["name"] for i in archive["inventory"]}) == len(archive["inventory"])
        assert archive["rawWitness"]["root"] == "approved-witness"
        assert (archive["rawWitness"]["bytes"], archive["rawWitness"]["sha256"]) == (archive["bytes"], archive["sha256"])
        archives[aid] = archive
    for m in modules + [b["distributionCodeBinding"]]:
        a = m["actualArchiveCode"]
        assert a["archiveId"] == "pyz-main" and a["memberKind"] == "PYZ-module"
        item = next(i for i in archives[a["archiveId"]]["inventory"] if i["name"] == a["memberName"])
        assert (a["rawMemberBytes"], a["rawMemberSha256"]) == (item["bytes"], item["sha256"])
    assert [i["name"] for i in b["functionBindings"]] == [i["name"] for i in profile["functionBindings"]]
    for fun, target in zip(b["functionBindings"], profile["functionBindings"]):
        assert fun["moduleBindingId"] == target["moduleBindingId"]
        assert fun["moduleName"] == target["moduleName"]
        module = bindings[fun["moduleBindingId"]]
        assert fun["sourceCompilation"] == module["sourceCompilation"]
        assert fun["expectedFunctionCode"] == fun["actualArchiveFunctionCode"]
        assert fun["codeConstIndexPath"]
    assert b["distributionCodeBinding"]["canonicalName"] == "pyshacl.validator"
    checker = b["dynamicChecker"]
    assert checker["stage"] == "build-source-to-bundle-data-only"
    assert "runtimeLoaderCode" not in checker and "loaderCode" not in checker
    assert checker["sourceCompilation"]["fingerprint"] == checker["expectedBundleSourceCode"]
    assert checker["bundleFile"]["path"] == "_internal/contracts/python/contract_v2.py"
    files = {i["path"]: i for i in f["directoryFiles"]}
    assert len(files) == len(f["directoryFiles"])
    assert f["executable"]["path"] in ["ontolearn-semantic-parity", "ontolearn-semantic-parity.exe"]
    same_file(files[f["executable"]["path"]], f["executable"])
    assert f["embeddedProvenance"]["path"] == "_internal/provenance/i05/source-package-parity-build.json"
    same_file(files[f["embeddedProvenance"]["path"]], f["embeddedProvenance"])
    for payload in b["payloadFiles"]:
        assert payload["root"] == "meipass-root"
        assert payload["path"] != "provenance/i05/source-package-parity-build.json"
        final = files["_internal/" + payload["path"]]
        assert (payload["bytes"], payload["sha256"]) == (final["bytes"], final["sha256"])
    for runtime in b["runtimeComponents"]:
        for file in runtime["bundleFiles"] + runtime["licenses"]:
            assert file["root"] == "bundle-root"
            same_file(file, files[file["path"]])
        if runtime["kind"] == "pyinstaller-bootloader":
            assert any(i == f["executable"] for i in runtime["bundleFiles"])
    assert {i["kind"] for i in b["runtimeComponents"]} >= {"python", "stdlib", "pyinstaller-bootloader", "dynamic-library", "platform-runtime"}
    assert {i["name"]: i["version"] for i in b["distributions"]} == profile["requiredRuntimeDistributions"]
    for dist in b["distributions"] + b["build"]["buildToolDistributions"]:
        assert dist["selectedArtifact"] in dist["allPlatformArtifacts"]
        rows = dist["recordRows"]
        assert [i["rowIndex"] for i in rows] == list(range(len(rows)))
        raw = b"".join(base64.b64decode(i["rawRowBase64"], validate=True) for i in rows)
        assert raw == base64.b64decode(dist["recordOriginalBytesBase64"], validate=True)
        assert len(raw) == dist["record"]["bytes"] and hashlib.sha256(raw).hexdigest() == dist["record"]["sha256"]
        for row in rows:
            assert row["installationRootId"] == "approved-installation"
            assert not row["normalizedInstalledPath"].startswith("../")
            installed = dist["installedFiles"][row["installedFileIndex"]]
            assert row["rowIndex"] in installed["recordRowIndexes"]
            assert installed["installedRelativePath"] == row["normalizedInstalledPath"]
            assert row["disposition"] == installed["disposition"]
        for i, installed in enumerate(dist["installedFiles"]):
            assert all(rows[n]["installedFileIndex"] == i for n in installed["recordRowIndexes"])
            if installed["disposition"] == "bundled":
                assert installed["bundleMappings"] and installed["omissionReason"] is None
            else:
                assert not installed["runtimeRequired"] and not installed["bundleMappings"]
                assert installed["omissionReason"] and installed["ownerReview"] is not None
        assert dist["licenses"]
    assert f["runtimeValidation"] == "not-executed" and f["runtimeEvidenceManifest"] is None
    assert f["approvalStatus"] == "unapproved-produced-evidence"
    serialized = (json.dumps(f, ensure_ascii=False, indent=2) + "\n").encode()
    assert v["buildReceipt"]["bytes"] == len(serialized)
    assert v["buildReceipt"]["sha256"] == hashlib.sha256(serialized).hexdigest()
    assert f["compositionRef"] == v["compositionRef"] == b["composition"]["compositionRef"]
    assert v["runtimeEvidenceManifest"]["complete"] is True
    assert v["runtimeEvidenceManifest"]["files"]
    runtime_files = {i["path"]: i for i in v["runtimeEvidenceManifest"]["files"]}
    assert len(runtime_files) == len(v["runtimeEvidenceManifest"]["files"])
    assert v["runtimeEvidenceManifest"]["manifestFile"]["path"] not in runtime_files
    comparison = v["comparison"]
    if v["runtimeValidation"] == "collected-pending-comparison":
        assert comparison["state"] == "pending"
        assert all(comparison[k] is None for k in ["comparatorSource", "oracleSource", "comparisonReport", "sourcePackageEquivalent", "externalOracleMatched", "originalOperationPassed"])
    else:
        assert comparison["state"] == "compared"
        assert all(comparison[k] is not None for k in ["comparatorSource", "oracleSource", "comparisonReport"])
        same_file(comparison["comparisonReport"], runtime_files[comparison["comparisonReport"]["path"]])
        assert all(type(comparison[k]) is bool for k in ["sourcePackageEquivalent", "externalOracleMatched", "originalOperationPassed"])
    for run in v["runs"]:
        for field in ["stdout", "stderr", "header", "terminal"]:
            same_file(run[field], runtime_files[run[field]["path"]])
        assert run["argv"][-2:] in profile["exactProbeArgv"]
        if run["mode"] == "source":
            assert run["argv"] == ["python", "-m", "ontolearn_engine.semantic_source_package_probe"] + run["argv"][-2:]
            assert run["observedSource23"] is not None
        else:
            assert len(run["argv"]) == 3
            assert run["observedSource23"] is None
        assert run["selector"] == run["argv"][-1]
        assert run["declaredCompositionRef"] == v["compositionRef"]
        assert run["provenanceSha256"] == f["embeddedProvenance"]["sha256"]
        assert run["python"] == b["python"]
        assert [m["canonicalName"] for m in run["moduleLoaders"]] == expected
        assert run["distributionModuleLoader"]["canonicalName"] == "pyshacl.validator"
        assert run["dynamicChecker"]["runtimeLoaderCode"] == checker["expectedBundleSourceCode"]
        if run["fullSuiteCollectionComplete"]:
            assert run["collectionComplete"] and run["selector"] == "full-v1"
    # Finite evidence dependency graph is data, not filesystem traversal.
    graph = x["dependencyGraph"]
    done = set()
    for item in graph:
        assert item["id"] not in done and set(item["dependsOn"]) <= done
        done.add(item["id"])
    assert "validation-receipt" not in next(i for i in graph if i["id"] == "build-receipt")["dependsOn"]


def mutate(data, pointer, value):
    node = data
    parts = pointer.strip("/").split("/")
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    last = int(parts[-1]) if isinstance(node, list) else parts[-1]
    node[last] = value


def main():
    schemas = {k: read(BASE / n) for k, n in {"provenance": "build-provenance.schema.json", "buildReceipt": "build-receipt.schema.json", "validationReceipt": "runtime-validation-receipt.schema.json"}.items()}
    profile = read(BASE / "profile-descriptor.json")
    ref_count = 0
    def walk(node, schema):
        nonlocal ref_count
        if isinstance(node, dict):
            if "$ref" in node:
                resolve(schema, node["$ref"])
                ref_count += 1
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False
                assert set(node["required"]) == set(node["properties"])
            if "pattern" in node:
                re.compile(node["pattern"])
            for value in node.values():
                walk(value, schema)
        elif isinstance(node, list):
            for value in node:
                walk(value, schema)
    for schema in schemas.values():
        walk(schema, schema)
    cases = read(HERE / "synthetic-design-cases.json")
    assert cases["sampleKind"] == "synthetic design data; no actual build or run"
    valid = cases["valid"]
    for key, schema in schemas.items():
        structural(valid[key], schema, schema)
    relations(valid, profile)
    for variant in cases.get("validVariants", []):
        altered = copy.deepcopy(valid)
        for change in variant["changes"]:
            mutate(altered, change["pointer"], change["value"])
        for key, schema in schemas.items():
            structural(altered[key], schema, schema)
        relations(altered, profile)
    results = []
    for case in cases["invalid"]:
        altered = copy.deepcopy(valid)
        for change in case["changes"]:
            mutate(altered, change["pointer"], change["value"])
        rejected = False
        try:
            for key, schema in schemas.items():
                structural(altered[key], schema, schema)
            relations(altered, profile)
        except (AssertionError, KeyError, StopIteration, TypeError, ValueError):
            rejected = True
        assert rejected, case["id"]
        results.append({"id": case["id"], "rejectedByFiniteAssertions": True})
    print(json.dumps({"kind": "stdlib finite document selfcheck; not JSONSchema engine validation", "schemaCount": 3, "localRefsResolved": ref_count, "syntheticValid": 1, "syntheticValidVariants": len(cases.get("validVariants", [])), "syntheticInvalidRejected": len(results), "results": results, "actualBuildRunInstallApprovalEvidence": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
