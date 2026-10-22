"""Independent finite document checks. Not a JSONSchema engine or product test."""
import copy
import hashlib
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DOC = ROOT / "docs/iterations/T03/i05-semantic-build-protocol"


def read(path):
    def pairs(items):
        obj = {}
        for key, value in items:
            assert key not in obj, ("duplicate key", key)
            obj[key] = value
        return obj
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def shape(value, node, schema, path=""):
    errors = []
    if "$ref" in node:
        target = schema
        for part in node["$ref"][2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        errors += shape(value, target, schema, path)
    if "const" in node and (type(value) is not type(node["const"]) or value != node["const"]):
        errors.append(path + ":const")
    if "enum" in node and not any(type(value) is type(x) and value == x for x in node["enum"]):
        errors.append(path + ":enum")
    types = {"object": dict, "array": list, "string": str, "integer": int,
             "boolean": bool, "null": type(None)}
    if "type" in node:
        kinds = node["type"] if type(node["type"]) is list else [node["type"]]
        if not any(type(value) is types[k] for k in kinds):
            return errors + [path + ":type"]
    for key in ["anyOf", "oneOf"]:
        if key in node:
            passed = sum(not shape(value, branch, schema, path) for branch in node[key])
            if passed < 1 or (key == "oneOf" and passed != 1):
                errors.append(path + ":" + key)
    if type(value) is dict:
        errors += [path + "/" + k + ":required" for k in node.get("required", []) if k not in value]
        props = node.get("properties", {})
        if node.get("additionalProperties") is False:
            errors += [path + "/" + k + ":additional" for k in value.keys() - props.keys()]
        for key in value.keys() & props.keys():
            errors += shape(value[key], props[key], schema, path + "/" + key)
    if type(value) is list:
        if not node.get("minItems", 0) <= len(value) <= node.get("maxItems", float("inf")):
            errors.append(path + ":array-length")
        if "items" in node:
            for n, item in enumerate(value):
                errors += shape(item, node["items"], schema, path + "/" + str(n))
    if type(value) is str:
        if not node.get("minLength", 0) <= len(value) <= node.get("maxLength", float("inf")):
            errors.append(path + ":string-length")
        if "pattern" in node and not re.search(node["pattern"], value):
            errors.append(path + ":pattern")
    if type(value) is int and value < node.get("minimum", float("-inf")):
        errors.append(path + ":minimum")
    return errors


def main():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head == "76c774ec7612998cdcb1079deff5c988c15053e6"
    manifest = read(HERE / "candidate-manifest.json")
    for row in manifest["files"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
        assert raw == subprocess.check_output(["git", "show", head + ":" + row["path"]], cwd=ROOT)
    changed = set(subprocess.check_output(["git", "diff", "--name-only", manifest["base"], head], cwd=ROOT, text=True).splitlines())
    assert changed == {r["path"] for r in manifest["files"]} | {str((HERE / "candidate-manifest.json").relative_to(ROOT))}
    schemas = {k: read(DOC / n) for k, n in {"provenance": "build-provenance.schema.json", "buildReceipt": "build-receipt.schema.json", "validationReceipt": "runtime-validation-receipt.schema.json"}.items()}
    cases = read(HERE / "synthetic-design-cases.json")
    valid = cases["valid"]
    for key, schema in schemas.items():
        assert not shape(valid[key], schema, schema, "/" + key)
    fieldmap = read(DOC / "field-responsibility.json")
    byname = {n: schemas[k] for k, n in {"provenance": "build-provenance.schema.json", "buildReceipt": "build-receipt.schema.json", "validationReceipt": "runtime-validation-receipt.schema.json"}.items()}
    expected = set()
    def properties(node, file, pointer="#"):
        if type(node) is dict:
            if "properties" in node:
                assert node.get("additionalProperties") is False
                assert set(node.get("required", [])) == set(node["properties"])
                for key in node["properties"]:
                    expected.add((file, pointer + "/properties/" + key))
            for key, value in node.items():
                properties(value, file, pointer + "/" + key)
        elif type(node) is list:
            for n, value in enumerate(node):
                properties(value, file, pointer + "/" + str(n))
    for file, schema in byname.items():
        properties(schema, file)
    observed = set()
    for row in fieldmap["propertyIndex"]:
        node = byname[row["schema"]]
        for part in row["pointer"][2:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            node = node[int(part)] if type(node) is list else node[part]
        assert all(node[k] == v for k, v in row["shape"].items())
        observed.add((row["schema"], row["pointer"]))
    assert observed == expected and len(observed) == len(fieldmap["propertyIndex"]) == 917
    identities = read(HERE / "input-identities.json")
    for row in identities["frozenAdoptionIdentities"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
        assert raw == subprocess.check_output(["git", "show", manifest["base"] + ":" + row["path"]], cwd=ROOT)
    for row in identities["fourWriters"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
        assert raw == subprocess.check_output(["git", "show", manifest["base"] + ":" + row["path"]], cwd=ROOT)
    run = valid["validationReceipt"]["runs"][0]
    schema = schemas["validationReceipt"]
    runshape = schema["properties"]["runs"]["items"]
    failures = []
    def check(name, replacements):
        altered = copy.deepcopy(run)
        altered.update(replacements)
        errors = shape(altered, runshape, schema, "/runs/0")
        assert errors, name
        failures.append({"id": name, "syntheticOnly": True, "changes": replacements, "candidateShapeRejects": errors})
    check("precondition-no-header-no-loader", {"header": None, "terminal": None, "actualExitCode": 2, "collectionComplete": False, "fullSuiteCollectionComplete": False, "moduleLoaders": [], "distributionModuleLoader": None, "functionCodes": [], "dynamicChecker": None, "python": None, "declaredCompositionRef": None, "provenanceSha256": None, "packageCodeBoundToSource": None})
    check("hardkill-partial-raw", {"header": None, "terminal": None, "actualExitCode": None, "signal": "SIGKILL", "collectionComplete": False, "fullSuiteCollectionComplete": False, "moduleLoaders": []})
    check("header-then-partial-loaders", {"terminal": None, "actualExitCode": 1, "collectionComplete": False, "fullSuiteCollectionComplete": False, "moduleLoaders": run["moduleLoaders"][:1]})
    loaders = copy.deepcopy(run["moduleLoaders"])
    loaders[0]["exactCodeType"] = False
    check("observed-non-CodeType", {"actualExitCode": 2, "collectionComplete": False, "fullSuiteCollectionComplete": False, "moduleLoaders": loaders})
    loaders = copy.deepcopy(run["moduleLoaders"])
    loaders[0]["singleCanonicalObject"] = False
    check("observed-alias-mismatch", {"actualExitCode": 2, "collectionComplete": False, "fullSuiteCollectionComplete": False, "moduleLoaders": loaders})
    print(json.dumps({"kind": "independent finite document assertions; not JSONSchema engine", "candidate": head, "manifestPayloads": len(manifest["files"]), "candidatePathSet": len(changed), "allCurrentGitSHA": True, "all917ResponsibilityPointersExactAndComplete": True, "frozenAdoption12AndFourWriters": True, "threeSyntheticShapes": True, "failureEvidenceRepresentationCounterexamples": failures, "actualProductBuildLoaderRun": False}, indent=2))


if __name__ == "__main__":
    main()
