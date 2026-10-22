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


def strict_json_text(text):
    assert not text.startswith("\ufeff")
    def pairs(items):
        result = {}
        for key, value in items:
            assert key not in result, ("duplicate-key", key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def read(path):
    return strict_json_text(path.read_text())

def resolve(schema, pointer):
    assert pointer.startswith("#/")
    node = schema
    for part in pointer[2:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        node = node[int(key)] if isinstance(node, list) else node[key]
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


RAW_HEADER_EXAMPLES = {}
HEADER_DOCUMENT_SCHEMA = None

OBSERVATION_GROUPS = ["python", "moduleLoaders", "distributionModuleLoader", "functionCodes", "dynamicChecker", "observedSource23", "declaredCompositionRef", "provenanceSha256", "packageCodeBoundToSource", "sourceCodeBoundToSource"]


def observation_paths(run):
    paths = []
    def walk(value, pointer):
        if value is None:
            return
        if type(value) is dict:
            for key, item in value.items():
                walk(item, pointer + "/" + key.replace("~", "~0").replace("/", "~1"))
        elif type(value) is list:
            for index, item in enumerate(value):
                walk(item, pointer + "/" + str(index))
        else:
            paths.append(pointer)
    for name in OBSERVATION_GROUPS:
        walk(run[name], "/" + name)
    return paths


def runtime_relations(run, provenance, build_receipt, profile, runtime_files):
    state = run["observationState"]
    expected = [m["module"] for m in profile["canonicalModules"]]
    names = [m["canonicalName"] for m in run["moduleLoaders"]]
    assert len(names) == len(set(names)) and set(names) <= set(expected)
    assert names == [name for name in expected if name in names]
    fnames = [f["name"] for f in run["functionCodes"]]
    fexpected = [f["name"] for f in profile["functionBindings"]]
    assert len(fnames) == len(set(fnames)) and set(fnames) <= set(fexpected)
    assert fnames == [name for name in fexpected if name in fnames]
    assert len(run["observedPaths"]) == len(set(run["observedPaths"]))
    assert set(run["observedPaths"]) == set(observation_paths(run))
    assert len(run["observationIds"]) == len(set(run["observationIds"]))
    assert len(run["observationIds"]) == len(run["observationOutcomes"])
    if run["signal"] is not None:
        assert run["actualExitCode"] is None
    for key in ["stdout", "stderr", "header", "terminal"]:
        if run[key] is not None:
            same_file(run[key], runtime_files[run[key]["path"]])
    for key in ["header", "terminal"]:
        availability = run[key + "State"]
        assert (run[key] is None) == (availability == "absent")
    assert (run["headerPayload"] is None) == (run["headerState"] != "parsed")
    if run["failure"] is not None and run["failure"]["firstEvidence"] is not None:
        evidence = run["failure"]["firstEvidence"]
        same_file(evidence, runtime_files[evidence["path"]])
    for item in run["moduleLoaders"] + ([run["distributionModuleLoader"]] if run["distributionModuleLoader"] else []) + ([run["dynamicChecker"]] if run["dynamicChecker"] else []):
        evidence = item["freshColdWarmEvidence"]
        if evidence is not None:
            same_file(evidence, runtime_files[evidence["path"]])
    if state == "not-started":
        assert all(run[k] is None for k in ["stdout", "stderr", "header", "terminal", "headerPayload", "actualExitCode", "signal"])
        assert not run["observedPaths"] and not run["observationIds"]
        assert not run["collectionComplete"] and not run["fullSuiteCollectionComplete"]
        assert run["failure"]["actor"] == "caller" and run["failure"]["phase"] == "prelaunch"
        assert run["failure"]["code"] in ["APPROVED_BUILD_RECEIPT_UNAVAILABLE", "APPROVED_SOURCE_BINDING_INVALID", "BUNDLE_DIRECTORY_MISMATCH"]
        return
    assert run["stdout"] is not None and run["stderr"] is not None
    if state != "collected":
        assert run["failure"] is not None and run["failure"]["firstEvidence"] is not None
    if state == "pre-header-rejected":
        assert run["headerState"] == run["terminalState"] == "absent"
        assert run["actualExitCode"] == 2 and run["signal"] is None
        assert not run["collectionComplete"] and not run["fullSuiteCollectionComplete"]
        assert run["failure"]["actor"] == "probe"
        if run["failure"]["phase"] == "argv":
            assert run["failure"]["reason"] == "argv-rejected" and run["failure"]["code"] is None
        else:
            assert run["failure"]["code"] in ["FROZEN_BUILD_PROVENANCE_UNAVAILABLE", "BUILD_PROVENANCE_FORMAT_INVALID", "DECLARED_COMPOSITION_FORMAT_INVALID", "BUNDLE_PROVENANCE_RESOURCE_MISMATCH", "LOADER_ARCHIVE_CODE_MISMATCH", "CODE_DOMAIN_INVALID", "DYNAMIC_CHECKER_IDENTITY_INVALID", "LOADER_SOURCE_CODE_MISMATCH"]
    elif state == "incomplete":
        assert run["failure"] is not None
        assert not run["collectionComplete"] and not run["fullSuiteCollectionComplete"]
    else:
        assert state == "collected" and run["failure"] is None
        assert run["actualExitCode"] == 0 and run["signal"] is None
        assert run["headerState"] == run["terminalState"] == "parsed"
        assert run["collectionComplete"]
    if run["header"] is not None:
        example = RAW_HEADER_EXAMPLES[run["header"]["path"]]
        raw = example["utf8"].encode("utf-8")
        assert len(raw) == run["header"]["bytes"] and hashlib.sha256(raw).hexdigest() == run["header"]["sha256"]
        if run["headerState"] == "parsed":
            assert strict_json_text(raw.decode("utf-8")) == run["headerPayload"]
        else:
            try:
                parsed = strict_json_text(raw.decode("utf-8"))
                structural(parsed, HEADER_DOCUMENT_SCHEMA, HEADER_DOCUMENT_SCHEMA)
            except (ValueError, AssertionError, KeyError, TypeError):
                pass
            else:
                raise AssertionError("malformed header example was strict valid JSON")
    header = run["headerPayload"]
    if header is not None:
        assert header["declaredCompositionRef"] == run["declaredCompositionRef"]
        assert (header["provenanceRead"]["sha256"] if header["provenanceRead"] else None) == run["provenanceSha256"]
        python = run["python"]
        assert header["observedPython"] == ({k: v for k, v in python.items() if k not in ["compilerExecutable", "dontInherit"]} if python else None)
        for group in ["moduleLoaders", "distributionModuleLoader", "functionCodes", "dynamicChecker"]:
            def project(item):
                return {k: v for k, v in item.items() if k != "freshColdWarmEvidence"} if item else None
            actual = run[group]
            projected = [project(item) for item in actual] if type(actual) is list else project(actual)
            assert header[group] == projected
        for group in ["observedSource23", "packageCodeBoundToSource", "sourceCodeBoundToSource"]:
            assert header[group] == run[group]
    if state != "collected":
        return
    assert header["mode"] == run["mode"] and header["selector"] == run["selector"]
    count = 22 if run["mode"] == "source" else 23
    assert header["declaredSupplierSources"] == [{"canonicalName": name, "source": source} for name, source in zip(expected[:count], provenance["inputs"]["modules"][:count])]
    if run["mode"] == "source":
        assert header["provenanceRead"] is None and header["declaredPython"] is None and header["declaredCompositionRef"] is None
        assert run["declaredCompositionRef"] is None and run["provenanceSha256"] is None and run["packageCodeBoundToSource"] is None
    else:
        assert run["observedSource23"] is None and run["sourceCodeBoundToSource"] is None
        assert all(m["actualSource"] is None for m in run["moduleLoaders"])
    assert run["argv"][-2:] in profile["exactProbeArgv"]
    if run["mode"] == "source":
        assert run["argv"] == ["python", "-m", "ontolearn_engine.semantic_source_package_probe"] + run["argv"][-2:]
        assert run["sourceCodeBoundToSource"] == "loader-consistent-with-observed-source"
        assert run["observedSource23"] is not None
    else:
        assert len(run["argv"]) == 3
        assert run["declaredCompositionRef"] == provenance["composition"]["compositionRef"]
        assert run["provenanceSha256"] == build_receipt["embeddedProvenance"]["sha256"]
        assert header["provenanceRead"]["bytes"] == build_receipt["embeddedProvenance"]["bytes"]
        assert header["declaredPython"] == provenance["python"]
        assert run["packageCodeBoundToSource"] == "archive-loader-consistent-with-declared-source"
    assert run["selector"] == run["argv"][-1]
    assert run["python"] == provenance["python"]
    assert names == expected
    bindings = {m["bindingId"]: m for m in provenance["moduleBindings"] + [provenance["distributionCodeBinding"]]}
    for item in run["moduleLoaders"] + [run["distributionModuleLoader"]]:
        assert item is not None and item["exactCodeType"] is True and item["singleCanonicalObject"] is True
        expected_binding = bindings[item["bindingId"]]
        assert item["canonicalName"] == expected_binding["canonicalName"]
        assert item["specName"] == item["canonicalName"] and item["loaderClass"] and item["origin"]
        assert item["runtimeLoaderCode"] == expected_binding["actualArchiveCode"]["fingerprint"]
        assert item["freshColdWarmEvidence"] is not None
    assert run["distributionModuleLoader"]["canonicalName"] == "pyshacl.validator"
    if run["mode"] == "source":
        for item, source in zip(run["moduleLoaders"], provenance["inputs"]["modules"]):
            assert item["actualSource"] == {"bytes": source["bytes"], "sha256": source["sha256"]}
        source23 = run["observedSource23"]
        assert source23 == {"actualSourceBytes": run["moduleLoaders"][-1]["actualSource"]["bytes"], "actualSourceSha256": run["moduleLoaders"][-1]["actualSource"]["sha256"], "actualLoaderCode": run["moduleLoaders"][-1]["runtimeLoaderCode"]}
    assert fnames == fexpected
    for item, expected_function in zip(run["functionCodes"], provenance["functionBindings"]):
        assert item["exactCodeType"] is True
        assert item["moduleBindingId"] == expected_function["moduleBindingId"]
        assert item["codeConstIndexPath"] == expected_function["codeConstIndexPath"]
        assert item["runtimeFunctionCode"] == expected_function["expectedFunctionCode"]
    checker = run["dynamicChecker"]
    assert checker is not None and checker["exactCodeType"] is True and checker["sameConsumerObject"] is True
    assert checker["runtimeLoaderCode"] == provenance["dynamicChecker"]["expectedBundleSourceCode"]
    assert checker["freshColdWarmEvidence"] is not None
    if run["selector"] == "full-v1":
        assert run["fullSuiteCollectionComplete"] and len(run["observationIds"]) == 417
    else:
        assert not run["fullSuiteCollectionComplete"] and len(run["observationIds"]) == 1


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
        runtime_relations(run, b, f, profile, runtime_files)
    if v["comparison"]["state"] == "compared":
        if any(v["comparison"][k] is True for k in ["sourcePackageEquivalent", "externalOracleMatched", "originalOperationPassed"]):
            assert all(run["observationState"] == "collected" for run in v["runs"])
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
    global HEADER_DOCUMENT_SCHEMA
    header_schema = read(BASE / "runtime-header.schema.json")
    HEADER_DOCUMENT_SCHEMA = header_schema
    assert schemas["validationReceipt"]["properties"]["runs"]["items"]["properties"]["headerPayload"]["anyOf"][0] == {k: v for k, v in header_schema.items() if k not in ["$schema", "$id", "title", "$comment"]}
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
    for schema in list(schemas.values()) + [header_schema]:
        walk(schema, schema)
    responsibility = read(BASE / "field-responsibility.json")
    schema_files = {"build-provenance.schema.json": schemas["provenance"], "build-receipt.schema.json": schemas["buildReceipt"], "runtime-validation-receipt.schema.json": schemas["validationReceipt"], "runtime-header.schema.json": header_schema}
    declared_index = responsibility["propertyIndex"]
    actual_pointers = set()
    def enumerate_properties(node, pointer, filename):
        if type(node) is dict:
            for key in node.get("properties", {}):
                actual_pointers.add((filename, pointer + "/properties/" + key.replace("~", "~0").replace("/", "~1")))
            for key, value in node.items():
                enumerate_properties(value, pointer + "/" + key.replace("~", "~0").replace("/", "~1"), filename)
        elif type(node) is list:
            for index, value in enumerate(node):
                enumerate_properties(value, pointer + "/" + str(index), filename)
    for filename, schema in schema_files.items():
        enumerate_properties(schema, "#", filename)
    assert len(declared_index) == len(actual_pointers)
    assert {(row["schema"], row["pointer"]) for row in declared_index} == actual_pointers
    for row in declared_index:
        node = resolve(schema_files[row["schema"]], row["pointer"])
        assert row["shape"] == {k: v for k, v in node.items() if k in ["type", "const", "enum", "$ref"]}
        assert row["required"] is True
    cases = read(HERE / "synthetic-design-cases.json")
    assert cases["sampleKind"] == "synthetic design data; no actual build or run"
    global RAW_HEADER_EXAMPLES
    RAW_HEADER_EXAMPLES = cases["headerRawExamples"]
    valid = cases["valid"]
    for key, schema in schemas.items():
        structural(valid[key], schema, schema)
    relations(valid, profile)
    for example in cases["headerExamples"].values():
        structural(example, header_schema, header_schema)
    assert cases["headerExamples"]["frozen"] == valid["validationReceipt"]["runs"][0]["headerPayload"]
    source_example = next(v for v in cases["validVariants"] if v["id"] == "R-source-complete-header")["changes"][0]["value"][0]["headerPayload"]
    assert cases["headerExamples"]["source"] == source_example
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
    print(json.dumps({"kind": "stdlib finite document selfcheck; not JSONSchema engine validation", "schemaCount": 4, "propertyIndexRows": len(declared_index), "headerRawExamples": len(RAW_HEADER_EXAMPLES), "localRefsResolved": ref_count, "syntheticValid": 1, "syntheticValidVariants": len(cases.get("validVariants", [])), "syntheticInvalidRejected": len(results), "results": results, "actualBuildRunInstallApprovalEvidence": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
