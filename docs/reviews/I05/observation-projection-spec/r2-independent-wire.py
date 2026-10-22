"""Separate semantic graph identity from canonical serialized graph arrays."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
DESIGN = ROOT / "docs/iterations/I05/observation-projection-spec"
spec = importlib.util.spec_from_file_location("r2_wire_model", DESIGN / "model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
schema = json.loads((DESIGN / "schema.json").read_text())
cases = json.loads((DESIGN / "cases.json").read_text())["cases"]
by_id = {c["id"]: c for c in cases}

def get(obj, path):
    for key in path: obj = obj[key]
    return obj

def n3(t, identity=False):
    if t["kind"] == "iri": return "<" + t["value"] + ">"
    if t["kind"] == "blank": return "_:" + t["label"]
    text = json.dumps(t["lexical"], ensure_ascii=False)
    if t["language"] is not None:
        return text + "@" + (t["language"].casefold() if identity else t["language"])
    if t["datatype"] == "http://www.w3.org/2001/XMLSchema#string": return text
    return text + "^^<" + t["datatype"] + ">"

def sorted_wire(rows, mode):
    keys = [tuple(n3(term) for term in row) if mode == "typed-graph" else tuple(row) for row in rows]
    return keys == sorted(keys)

expected_graphs = 0
for c in cases:
    p = c["expectedProjection"]
    for path, mode in m.projection_layout(p):
        if mode in ["typed-graph", "n3-graph"]:
            assert sorted_wire(get(p, path), mode)
            expected_graphs += 1

exact_duplicates = []
for id, path in [
    ("rdfs/cycle", ("value", "rdfs")),
    ("legacy/repeated-variable", ("value", "rules")),
    ("scope/fresh", ("value", "facts")),
    ("rdfs/domain-depth2", ("value", "rdfsEvidence", 1, "basis"))]:
    c = by_id[id]
    changed = copy.deepcopy(c["expectedProjection"])
    rows = get(changed, path)
    rows.append(copy.deepcopy(rows[0]))
    exact_duplicates.append({"id": id, "path": list(path), "schemaValid": m.validate(changed, schema),
        "identityOnlyEqual": m.projection_identity_equal(c["expectedProjection"], changed),
        "matchesWithSchemaGate": m.matches(c, changed, schema)})
    assert not m.validate(changed, schema) and not m.matches(c, changed, schema)

# An abstract serializer example, not an engine outcome or new product fixture.
lang_triple = ["<urn:x>", "<urn:p>", '"hello"@en']
legacy = {"kind": "legacy", "complete": True, "value": {"rdfs": [], "rules": [lang_triple],
    "warnings": [], "rdfsEvidence": [], "evidence": []}}
changed = copy.deepcopy(legacy)
changed["value"]["rules"].append(["<urn:x>", "<urn:p>", '"hello"@EN'])
assert m.validate(legacy, schema) and m.validate(changed, schema)
n3_duplicate_match = m.matches({"expectedProjection": legacy}, changed, schema)
assert n3_duplicate_match

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
iri = lambda value: {"kind": "iri", "value": value}
lang = lambda language: {"kind": "literal", "lexical": "hello", "datatype": RDF + "langString", "language": language}
scope = copy.deepcopy(by_id["scope/asserted"]["expectedProjection"])
scope["value"]["facts"] = [[iri("urn:x"), iri("urn:p"), lang("en")]]
typed_changed = copy.deepcopy(scope)
typed_changed["value"]["facts"].append([iri("urn:x"), iri("urn:p"), lang("EN")])
assert m.validate(scope, schema) and m.validate(typed_changed, schema)
typed_duplicate_match = m.matches({"expectedProjection": scope}, typed_changed, schema)
assert typed_duplicate_match

ordered_left = {"graph": [["_:a", "<urn:p>", "<urn:x>"], ["_:b", "<urn:p>", "<urn:y>"]]}
ordered_right = {"graph": [["_:p", "<urn:p>", "<urn:y>"], ["_:q", "<urn:p>", "<urn:x>"]]}
assert sorted_wire(ordered_left["graph"], "n3-graph")
assert sorted_wire(ordered_right["graph"], "n3-graph")
assert m.identity_domain_equal(ordered_left, ordered_right, [(("graph",), "n3-graph")])
results = {"registeredExpectedGraphSlotsAlreadyN3Sorted": expected_graphs,
    "exactDuplicateSchemaGate": exact_duplicates,
    "rdfIdentityDuplicateAliases": {"n3SchemaValidAndMatchesTwoRowsForOneIdentity": n3_duplicate_match,
        "typedSchemaValidAndMatchesTwoRowsForOneIdentity": typed_duplicate_match,
        "abstractSerializerExamplesOnly": True},
    "crossingBNodeRenameBothSidesLocallyCanonicalAndIdentityEqual": True,
    "fixMustCheckEachWireBeforeSharedIdentityMapping": True}
p = OUT / "r2-proof.json"
proof = json.loads(p.read_text())
proof["results"]["wireVersusIdentityChecks"] = results
p.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(results, ensure_ascii=False, indent=2))
