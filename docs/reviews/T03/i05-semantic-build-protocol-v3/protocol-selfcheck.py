"""Finite stdlib document checks only; no products, schema engines or runtime probes.

Checks indexed schema deltas, full field/index preservation, exact historical
dependency sources and documented scope obligations. It cannot certify a real
resolver, lock, artifact, license, build, CodeType, loader or approval instance.
"""

import copy
import hashlib
import json
import pathlib
import subprocess
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "docs/iterations/T03/i05-semantic-build-protocol-v3"
OLD = "docs/iterations/T03/i05-semantic-build-protocol/"
D1 = "docs/iterations/T03/i05-semantic-D1-plan/"
FIXED = "86d6297a8cac5ad780f1be4416ec9052b82f3aaf"
D0 = "c3eb0694daad26527cc3a1eb0127ed5033f2be25"


def read(path):
    return json.loads(path.read_text())


def old_json(path, ref=FIXED):
    return json.loads(subprocess.check_output(["git", "show", ref + ":" + path], cwd=ROOT))


def pointer(value, path):
    for part in path.removeprefix("#/").split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def differences(a, b, path="#"):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            p = path + "/" + key.replace("~", "~0").replace("/", "~1")
            result += [p] if key not in a or key not in b else differences(a[key], b[key], p)
        return result
    if isinstance(a, list):
        if len(a) != len(b):
            return [path]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differences(x, y, path + "/" + str(i))]
    return [] if a == b else [path]


def design_relations(bundle, accepted, baseline_guard, old_profile):
    p, dep, guard = bundle["profile"], bundle["dependency"], bundle["guard"]
    assert p["id"] == "i05-source-package-parity-v3" and p["format"] == "i05-semantic-build-protocol-profile/4"
    assert p["protocolVersion"] == "3.0.0"
    assert p["lockPackageCount"] == dep["lockPackageCount"] == 26
    assert p["lockPackageVersions"] == dep["lockPackageVersions"] == accepted["proposedUnionPackageVersions"]
    assert p["dependencyDirectRequirements"] == dep["dependencyDirectRequirements"] == accepted["preferredParentUnionDirectRequirements"]
    assert dep["semanticRuntimeDistributions"] == accepted["runtimeEight"] == p["requiredRuntimeDistributions"]
    assert len(p["dependencyDirectRequirements"]) == 6
    assert [p[k] for k in ["canonicalModuleCount", "sourceDeclaredSupplierCount", "semanticRuntimeDistributionCount", "dedicatedSourceInputCount"]] == [23, 22, 8, 33]
    assert p["canonicalModules"] == old_profile["canonicalModules"]
    for key in ["resources", "assets", "hiddenImports", "collectAll", "copyMetadata", "excludeEngineModules", "functionBindings", "requiredRuntimeDistributions", "exactProbeArgv", "pathDomains", "archiveIds", "maximumArchiveDepth", "maximumProvenanceBytes", "runtimeObservationRules"]:
        assert p[key] == old_profile[key], key
    assert p["executionAuthorization"] is False and p["approvedWrapperPins"] == []
    assert all(p[k] is None for k in ["acceptedCompositionRef", "approvedConsumerPin", "approvedDependencyPin", "approvedToolchain", "approvedEvidenceRootRecord", "approvedProtocolRecord", "independentParentProfile"])
    assert dep["executionAuthorization"] is False
    assert all(dep[k] is None for k in ["actualDependencyRef", "actualCombinedLock", "actualEnginePyproject"])
    rows = dep["packageSources"]
    assert len(rows) == len({r["name"] for r in rows}) == 26
    assert {r["name"]: r["version"] for r in rows} == accepted["proposedUnionPackageVersions"]
    partitions = accepted["baselineLockFullTextPartition"]
    for row in rows:
        expected_label = "mappingProduct" if row["name"] in ["defusedxml", "et-xmlfile", "openpyxl"] else "profileProduct"
        assert row["referenceSelection"] == expected_label
        assert row["combinedMetadataRequiresNewActualLock"] == (row["name"] == "ontolearn-engine")
        assert all(row[k] is None for k in ["actualCombinedPackagePin", "selectedInstalledArtifact", "licenseApproved"])
        expected_sources = [label for label in ["profileProduct", "mappingProduct"] if any(r["name"] == row["name"] for r in partitions[label]["packages"])]
        assert [source["label"] for source in row["originCandidates"]] == expected_sources
        for source in row["originCandidates"]:
            original = next(r for r in partitions[source["label"]]["packages"] if r["name"] == row["name"])
            raw = source["exactOriginalBlock"].encode()
            assert raw == original["exactBlock"].encode()
            assert len(raw) == source["blockBytes"] == original["blockBytes"]
            assert hashlib.sha256(raw).hexdigest() == source["blockSha256"] == original["blockSha256"]
            parsed = tomllib.loads(source["exactOriginalBlock"])["package"][0]
            assert parsed["name"] == row["name"] and parsed["version"] == row["version"]
            artifacts = ([parsed["sdist"]] if "sdist" in parsed else []) + parsed.get("wheels", [])
            assert [{"url": a["url"], "sha256": a["hash"].removeprefix("sha256:"), "bytes": a["size"]} for a in artifacts] == source["artifacts"]
            if source["label"] == "profileProduct" and row["name"] == "rdflib":
                assert parsed["optional-dependencies"]["html"] == [{"name": "html5rdf"}]
            if row["name"] == "openpyxl":
                assert parsed["dependencies"] == [{"name": "et-xmlfile"}]
    assert guard["rows"] == baseline_guard["rows"]
    assert guard["executionAuthorization"] is False
    assert guard["futureApprovedPins"] == baseline_guard["futureApprovedPins"]
    for name, key, version, count in [("historical", "historicalScope", "historical-a4d-43/1", 45), ("dedicatedSemantic", "dedicatedSemanticScope", "semantic-v3-33/1", 33), ("parentDefault", "parentDefaultScope", "parent-default-v3-58/1", 58)]:
        scope = p["guardScopes"][name]
        paths = [r["path"] for r in guard["rows"] if r[key]["applicable"]]
        assert len(paths) == len(set(paths)) == count
        assert scope["sourceGuardPaths"] == paths and scope["guardVersion"] == version
        assert scope["guardManifest"]["actualApprovedManifestPin"] is None
        assert all(scope[k] is None for k in ["sourceRoot", "outputRoot", "environmentRoot", "actualGuardSourcePin"])
        assert scope["executionAuthorization"] is False


def mutate(data, path, value):
    parts = path.removeprefix("#/").split("/")
    parent = pointer(data, "#/" + "/".join(parts[:-1])) if len(parts) > 1 else data
    key = parts[-1]
    parent[int(key) if isinstance(parent, list) else key] = value


def main():
    index = read(BASE / "schema-change-index.json")
    changed = []
    for name in ["build-provenance.schema.json", "build-receipt.schema.json", "runtime-validation-receipt.schema.json", "runtime-header.schema.json"]:
        old, new = old_json(OLD + name, D0), read(BASE / name)
        actual = differences(old, new)
        declared = [r["pointer"] for r in index["schemaChanges"] if r["schema"] == name]
        assert set(actual) == set(declared) and len(actual) == len(declared)
        for row in [r for r in index["schemaChanges"] if r["schema"] == name]:
            assert pointer(old, row["pointer"]) == row["old"] and pointer(new, row["pointer"]) == row["new"]
        changed.extend({"schema": name, "pointer": p} for p in actual)
    old_fields, new_fields = old_json(OLD + "field-responsibility.json", D0), read(BASE / "field-responsibility.json")
    assert len(old_fields["propertyIndex"]) == len(new_fields["propertyIndex"]) == 1241
    for key in ["actors", "exactCodes", "indexMeaning"]:
        assert old_fields[key] == new_fields[key]
    allowed = [r["fieldResponsibilityPointer"] for r in index["fieldResponsibilityLiteralChanges"]] + ["#/format", "#/normativeCrossFieldRules"]
    assert set(differences(old_fields, new_fields)) == set(allowed)
    accepted = old_json(D1 + "dependency-plan.json")
    baseline_guard = old_json(D1 + "guard-scope-matrix.json")
    old_profile = old_json(OLD + "profile-descriptor.json", D0)
    bundle = {"profile": read(BASE / "profile-descriptor.json"), "dependency": read(BASE / "dependency-specification.json"), "guard": read(BASE / "guard-adoption-matrix.json")}
    design_relations(bundle, accepted, baseline_guard, old_profile)
    cases = read(HERE / "protocol-negative-cases.json")
    results = []
    for case in cases["cases"]:
        altered = copy.deepcopy(bundle)
        mutate(altered, case["pointer"], case["value"])
        try:
            design_relations(altered, accepted, baseline_guard, old_profile)
        except (AssertionError, KeyError, StopIteration, TypeError, ValueError):
            results.append({"id": case["id"], "rejectedByFiniteDocumentAssertions": True})
        else:
            raise AssertionError(("negative-accepted", case["id"]))
    report = {"kind": "finite stdlib document structure and relationship assertions; not JSONSchema engine validation", "schemaChanges": changed, "versionLiteralCount": 14, "metadataOnlyCount": 8, "propertyIndex": 1241, "dependencyPackages": 26, "directRequirements": 6, "guardCounts": [45, 33, 58], "additionalFiniteNegativesRejected": len(results), "results": results, "actualBuildInstallResolverLoaderRunApproval": False}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
