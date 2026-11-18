"""Deterministic plans only. Execution/persistence remain I05/T01/T00 responsibilities."""

import hashlib
import json

from ontolearn_engine.invalidation import family

from .definitions import absolute, fail, items, positive, shape, text, validate_definition

PLAN_VERSION = "t05-one-stage-plan/1"


def _signature(pattern: dict) -> tuple[str, str]:
    # Direct property access to rdf:type is equivalent to the type editor's pattern.
    if pattern["kind"] == "type":
        return ("type", pattern["class"])
    if pattern["path"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
        return ("type", pattern["object"].removeprefix("<").removesuffix(">"))
    return ("property", pattern["path"])


def build_plan(
    definitions: object, *, context: object, catalog: object, validation_scope: str
) -> dict:
    """Freeze private editor input; this function does not schedule or run a job.

    Registry-derived dependencies must still be supplied by the approved application
    service. Returning a plan never establishes current-result or execution evidence.
    """
    if validation_scope not in ("asserted", "asserted+rdfs+rules"):
        fail("UNSUPPORTED_SCOPE", ("validationScope",))
    ctx = shape(
        context,
        {"projectId", "inputSnapshotId", "projectRevision", "dependencyVector"},
        ("context",),
    )
    text(ctx["projectId"], ("context", "projectId"))
    text(ctx["inputSnapshotId"], ("context", "inputSnapshotId"))
    positive(ctx["projectRevision"], ("context", "projectRevision"), zero=True)
    vector = ctx["dependencyVector"]
    if not isinstance(vector, dict) or not vector:
        fail("INVALID_DEPENDENCIES", ("context", "dependencyVector"))
    for key, version in vector.items():
        text(key, ("context", "dependencyVector"))
        try:
            family(key)
        except ValueError:
            fail("INVALID_DEPENDENCIES", ("context", "dependencyVector"))
        positive(version, ("context", "dependencyVector", key), zero=True)
    source_catalog = shape(catalog, {"classes", "properties"}, ("catalog",))
    known = {}
    for key in ("classes", "properties"):
        known[key] = {
            absolute(item, ("catalog", key, index))
            for index, item in enumerate(items(source_catalog[key], ("catalog", key), empty=True))
        }
    parsed = [validate_definition(item).payload() for item in items(definitions, (), empty=True)]
    for definition in parsed:
        if definition["kind"] == "constraint":
            refs = [("classes", definition["targetClass"]), ("properties", definition["path"])]
        else:
            refs = []
            for pattern in definition["conditions"] + definition["conclusions"]:
                if pattern["kind"] == "type":
                    refs.append(("classes", pattern["class"]))
                elif pattern["kind"] == "property":
                    refs.append(("properties", pattern["path"]))
            for pattern in definition["conclusions"]:
                if pattern["kind"] == "property" and pattern["path"].startswith(
                    (
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        "http://www.w3.org/2000/01/rdf-schema#",
                        "http://www.w3.org/2002/07/owl#",
                        "http://www.w3.org/ns/shacl#",
                    )
                ):
                    fail("UNSUPPORTED_SCHEMA_CONCLUSION", (definition["id"], "conclusions"))
        for category, reference in refs:
            if reference not in known[category]:
                fail("UNRESOLVED_REFERENCE", (definition["id"], category))
    identities = [(d["kind"], d["id"]) for d in parsed]
    if len(set(identities)) != len(identities):
        fail("DUPLICATE_DEFINITION", ())
    parsed.sort(key=lambda d: (d["kind"], d["id"]))
    rules = [d for d in parsed if d["kind"] == "rule" and d["enabled"]]
    # Precompute signature sets: bounded O(rules² × signatures), not four nested
    # rule/condition/output loops. Type reads conservatively include domain/range
    # consequences because no approved RDFS closure is consumed by this planner.
    signatures = {
        rule["id"]: {
            "reads": {_signature(c) for c in rule["conditions"] if c["kind"] != "compare"},
            "writes": {_signature(c) for c in rule["conclusions"]},
        }
        for rule in rules
    }
    warnings = []
    for consumer in rules:
        reads = signatures[consumer["id"]]["reads"]
        type_read = any(kind == "type" for kind, _ in reads)
        for producer in rules:
            writes = signatures[producer["id"]]["writes"]
            if writes & reads or (type_read and writes):
                warnings.append(
                    {
                        "code": "RULE_CHAIN_UNSUPPORTED",
                        "producerRuleId": producer["id"],
                        "consumerRuleId": consumer["id"],
                        "certainty": "potential",
                        "message": "当前版本不支持规则链",
                    }
                )
    body = {
        "planVersion": PLAN_VERSION,
        "context": ctx,
        "validationScope": validation_scope,
        "definitions": parsed,
        "catalog": {key: sorted(values) for key, values in known.items()},
        "stages": [
            "parse-and-check-definitions",
            "rdfs-closure-from-asserted",
            "evaluate-all-enabled-rules-against-frozen-asserted-plus-rdfs",
            "collect-rule-outputs-without-rule-or-rdfs-refeeding",
            "shacl-on-explicit-validation-scope",
        ],
        "warnings": warnings,
        "executionState": "not-executed",
    }
    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {"planDigest": hashlib.sha256(canonical.encode()).hexdigest(), **json.loads(canonical)}


def validate_statement(value: object, path: tuple = ()) -> tuple[str, str, str]:
    """Validate stable RDF statement identity, not its truth or derivability."""
    from .definitions import rdf_value

    if not isinstance(value, list | tuple) or len(value) != 3:
        fail("INVALID_STATEMENT", path)
    return (
        absolute(value[0], (*path, 0)),
        absolute(value[1], (*path, 1)),
        rdf_value(value[2], (*path, 2)),
    )
