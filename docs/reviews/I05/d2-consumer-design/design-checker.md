"""Finite D2 design-document checker. This file is Python text under .md.

Imports only hashlib/json/pathlib/collections. Reads this worktree's new design
JSON and pinned pure-document snapshots. Writes nothing, imports no candidate
module or product, executes no schema/model source. stdout is a finite design
summary, never runtime receipt/certificate. No full JSON Schema engine claim.
"""

import collections
import hashlib
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[3]
DESIGN = ROOT / "iterations/I05/d2-consumer-design"
REVIEW = ROOT / "reviews/I05/d2-consumer-design"


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("nonfinite constant")


def read(path):
    raw = path.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), path
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=invalid_constant)


def pointer(value, location):
    if location in ("", "#"):
        return value
    location = location.removeprefix("#")
    assert location.startswith("/"), location
    for part in location[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if type(value) is list else value[part]
    return value


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def exact(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def leaves(value, path=""):
    if type(value) is dict:
        if not value:
            yield path, value
        for key, item in value.items():
            escaped = key.replace("~", "~0").replace("/", "~1")
            yield from leaves(item, path + "/" + escaped)
    elif type(value) is list:
        if not value:
            yield path, value
        for index, item in enumerate(value):
            yield from leaves(item, path + "/" + str(index))
    else:
        yield path, value


def schema_location_exists(schema, location):
    """Structural pointer reachability only; does not validate any instance."""
    parts = [] if location == "" else location.removeprefix("/").split("/")

    def walk(node, remaining):
        if not remaining:
            return True
        if type(node) is not dict:
            return False
        if "$ref" in node and walk(pointer(schema, node["$ref"]), remaining):
            return True
        for keyword in ["anyOf", "oneOf", "allOf"]:
            if any(walk(option, remaining) for option in node.get(keyword, [])):
                return True
        key = remaining[0].replace("~1", "/").replace("~0", "~")
        if key in node.get("properties", {}):
            return walk(node["properties"][key], remaining[1:])
        if key.startswith("{") and key.endswith("}") and "items" in node:
            return walk(node["items"], remaining[1:])
        return False

    return walk(schema, parts)


def finite_decision(value):
    """Only the detached design sample, NOT any complete receipt schema.

    This tests selected state/count/domain predicates; it has no IO/issuer/raw
    authenticity, graph matching, full observation payload or schema validation.
    """
    boolean_keys = ["dispatched", "stdoutPresent", "stderrPresent", "complete",
                    "full", "idsUniqueOrdered", "failure", "hasActualFalse",
                    "observedFalseIncluded", "codeDomainMatches", "moduleSetComplete",
                    "functionsComplete", "checkerSame", "argvExact", "sourceMode",
                    "frozenSourceNull", "selfPinEmbedded", "headerDigestMatches"]
    if any(type(value.get(k)) is not bool for k in boolean_keys):
        return False
    if type(value.get("count")) is not int or value["count"] < 0:
        return False
    if value["signal"] is not None and value["exit"] is not None:
        return False
    if value["hasActualFalse"] and not value["observedFalseIncluded"]:
        return False
    state = value["state"]
    if state == "not-started":
        return (not value["dispatched"] and not value["stdoutPresent"]
                and not value["stderrPresent"] and value["header"] == "absent"
                and value["terminal"] == "absent" and value["exit"] is None
                and value["signal"] is None and not value["complete"]
                and not value["full"] and value["failure"] and value["count"] == 0)
    if not value["dispatched"] or not value["stdoutPresent"] or not value["stderrPresent"]:
        return False
    if state == "pre-header-rejected":
        return (value["header"] == value["terminal"] == "absent"
                and type(value["exit"]) is int and value["exit"] == 2
                and value["signal"] is None and not value["complete"]
                and not value["full"] and value["failure"])
    if state == "incomplete":
        return (not value["complete"] and not value["full"] and value["failure"]
                and value["header"] in ["absent", "malformed", "parsed"]
                and value["terminal"] in ["absent", "malformed", "parsed"])
    if state != "collected":
        return False
    if not (type(value["exit"]) is int and value["exit"] == 0
            and value["signal"] is None and not value["failure"]
            and value["header"] == value["terminal"] == "parsed"
            and value["complete"] and value["idsUniqueOrdered"]
            and value["codeDomainMatches"] and value["moduleSetComplete"]
            and value["functionsComplete"] and value["checkerSame"]
            and value["argvExact"] and value["headerDigestMatches"]
            and not value["selfPinEmbedded"]):
        return False
    if value["sourceMode"]:
        if value["declaredSources"] != 22 or value["actualSources"] != 23:
            return False
    elif value["declaredSources"] != 23 or not value["frozenSourceNull"]:
        return False
    if value["selector"] == "full-v1":
        return value["count"] == 417 and value["full"]
    return (value["selector"] in ["b1-semantic-1x-v1", "b1-semantic-10x-v1"]
            and value["count"] == 1 and not value["full"])


def main():
    identity = read(REVIEW / "input-identity.json")
    sources = {}
    for entry in identity["inputs"]:
        raw = (REVIEW / entry["local"]).read_bytes()
        assert len(raw) == entry["bytes"]
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        sources[entry["inputId"]] = read(REVIEW / entry["local"]) if entry["path"].endswith(".json") else raw
    assert len(sources) == 27
    fields = read(DESIGN / "field-origin-map.json")
    acceptance = read(DESIGN / "acceptance-map.json")
    rejects = read(DESIGN / "reject-cases.json")
    rules = {rule["id"] for rule in acceptance["rules"]}
    assert len(rules) == 32
    original = sources["input-02"]["propertyIndex"]
    layers = {"build-receipt/2": sources["input-05"],
              "runtime-validation-receipt/2": sources["input-07"],
              "strict-header/1": sources["input-06"]}
    rows = fields["fieldRows"]
    assert len(rows) == len(original) == 1241
    assert len({row["id"] for row in rows}) == 1241
    assert len({(row["schema"], row["schemaPointer"]) for row in rows}) == 1241
    reachable = []
    definition_only = []
    schema_counts = collections.Counter()
    for row, prior in zip(rows, original):
        assert exact(row["originalResponsibility"], prior)
        source = sources[row["fixedSource"]["inputId"]]
        node = pointer(source, row["schemaPointer"])
        expected = {k: v for k, v in node.items() if k not in
                    ["properties", "items", "anyOf", "oneOf", "allOf", "prefixItems"]}
        assert exact(row["localConstraints"], expected)
        assert exact(pointer(source, row["fixedSource"]["pointer"]), node)
        assert row["consumerActor"] and row["crossLayerDisposition"]
        for destination in row["crossLayerDisposition"]["destinations"]:
            if "receiptPointerTemplate" in destination:
                assert schema_location_exists(sources["input-07"], destination["receiptPointerTemplate"])
            elif destination.get("pointer") is not None:
                assert schema_location_exists(layers[destination["layer"]], destination["pointer"]), (row["id"], destination)
        assert row["producer"] == prior["producer"]
        assert set(row["rules"]).issubset(rules)
        schema_counts[row["schema"]] += 1
        if row["instanceLocations"]:
            reachable.append(row["id"])
            assert "R01" in row["rules"]
            for location in row["instanceLocations"]:
                assert location["pointerTemplate"].startswith("/")
                variables = [x["variable"] for x in location["arrayVariables"]]
                assert len(variables) == len(set(variables))
                for branch in location["branchConditions"]:
                    if "schemaPointer" in branch:
                        pointer(source, branch["schemaPointer"])
        else:
            definition_only.append(row["id"])
            assert row["reachability"] == "definition-only-unreferenced"
            assert row["crossLayerDisposition"]["destinations"] == []
    assert len(reachable) == 1229 and len(definition_only) == 12
    assert dict(schema_counts) == fields["schemaPropertyCounts"]
    profile = sources["input-03"]
    actual = {x["pointer"]: x["value"] for x in fields["profileConcreteLeaves"]}
    assert exact(actual, dict(leaves(profile)))
    cases = sources["input-16"]["cases"]
    assert len(cases) == len(acceptance["projectionCases"]) == 37
    case_ids = [x["id"] for x in cases]
    assert len(set(case_ids)) == 37
    expected_leaves = {}
    for index, (case, item) in enumerate(zip(cases, acceptance["projectionCases"])):
        assert item["id"] == case["id"]
        assert item["expectedProjectionSha256"] == digest(case["expectedProjection"])
        assert exact(item["parameters"], case["parameters"])
        assert exact(item["preconditions"], case["preconditions"])
        assert exact(item["finiteRelations"], case["finiteRelations"])
        assert exact(item["pending"], case["pending"])
        assert item["requiredComparisonEntry"] == "matches"
        for key, val in leaves(case["expectedProjection"]):
            expected_leaves[(case["id"], key)] = val
    projected = {(x["caseId"], x["fieldPointer"]): x["value"]
                 for x in fields["projectionExpectedLeaves"]}
    assert exact(projected, expected_leaves)
    for item in fields["projectionExpectedLeaves"]:
        assert exact(item["value"], pointer(sources["input-16"], item["fixedSource"]["pointer"]))
    assert set(rejects["exhaustiveFieldMutationFamilies"][0]["appliesTo"]) == set(reachable)
    assert set(rejects["exhaustiveFieldMutationFamilies"][2]["appliesTo"]) == set(reachable)
    assert set(rejects["exhaustiveFieldMutationFamilies"][3]["appliesTo"]) == set(definition_only)
    assert all(item["rule"] in rules for item in rejects["cases"])
    assert len({x["id"] for x in rejects["cases"]}) == len(rejects["cases"])
    assert {x["id"] for x in acceptance["gaps"]} == {"G01", "G02", "G03", "G04", "G05"}
    for key, value in acceptance["frozenProfileApprovalFields"].items():
        assert exact(value, profile[key])
    assert acceptance["exactProbeArgv"] == profile["exactProbeArgv"]
    decisions = []
    for item in rejects["finiteSyntheticCases"]:
        result = finite_decision(item["value"])
        assert result is item["expected"], item["name"]
        decisions.append({"name": item["name"], "decision": result})
    for text in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1} trailing']:
        try:
            json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)
        except ValueError:
            continue
        raise AssertionError("strict JSON finite negative accepted")
    assert acceptance["wholeOracleComplete"] is False
    assert acceptance["productExecuted"] is False
    assert acceptance["schemaEngineValidation"] is False
    print(json.dumps({"evidenceClass": "finite-design-document-check-only",
                      "fixedInputIdentities": len(sources), "schemaProperties": len(rows),
                      "reachable": len(reachable), "unreferencedDefinitions": len(definition_only),
                      "profileLeaves": len(actual), "projectionCases": len(cases),
                      "projectionLeaves": len(projected), "normativeRules": len(rules),
                      "rejectDesigns": len(rejects["cases"]), "finiteDecisions": decisions,
                      "strictJsonNegatives": 4, "schemaEngineValidation": False,
                      "productExecuted": False, "independentReview": "pending"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
