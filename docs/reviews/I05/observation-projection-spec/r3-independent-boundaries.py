"""Independent R3 wire/model boundaries. Detached JSON mathematics only."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
DESIGN = ROOT / "docs/iterations/I05/observation-projection-spec"
spec = importlib.util.spec_from_file_location("r3_review_model", DESIGN / "model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
schema = json.loads((DESIGN / "schema.json").read_text())
cases = json.loads((DESIGN / "cases.json").read_text())["cases"]
by_id = {c["id"]: c for c in cases}
results = {}

def value_at(obj, path):
    for key in path: obj = obj[key]
    return obj

def independent_graph_paths(p):
    out = []
    def legacy(data, prefix):
        out.extend([(prefix + ("rdfs",), "n3-graph"), (prefix + ("rules",), "n3-graph")])
        out.extend((prefix + ("rdfsEvidence", i, "basis"), "n3-graph") for i in range(len(data["rdfsEvidence"])))
        out.extend((prefix + ("evidence", i, "basis"), "n3-graph") for i in range(len(data["evidence"])))
    if p["kind"] == "legacy": legacy(p["value"], ("value",))
    if p["kind"] == "scope":
        out.extend([(("value", "facts"), "typed-graph"), (("value", "ontology"), "typed-graph")])
        v = p["value"]
        if v["reasoning_result"] is not None: legacy(v["reasoning_result"], ("value", "reasoning_result"))
        for i, row in enumerate(v["provenance"]["selectedFacts"]):
            out.extend((("value", "provenance", "selectedFacts", i, "sources", j, "basis"), "n3-graph") for j in range(len(row["sources"])))
        out.extend((("value", "provenance", "derivedAxioms", i, "source", "basis"), "n3-graph") for i in range(len(v["provenance"]["derivedAxioms"])))
    return out

count = 0
reverse_sides = 0
duplicate_sides = 0
for case in cases:
    original = case["expectedProjection"]
    snapshot = copy.deepcopy(original)
    expected_paths = independent_graph_paths(original)
    assert set(expected_paths) == {(p, mode) for p, mode in m.projection_layout(original) if mode.endswith("-graph")}
    assert m.matches(case, copy.deepcopy(original), schema)
    for path, mode in expected_paths:
        rows = value_at(original, path)
        assert m.canonical_graph_wire(rows, mode)
        count += 1
        if len(rows) > 1:
            bad = copy.deepcopy(original)
            value_at(bad, path).reverse()
            held = copy.deepcopy(bad)
            assert m.validate(bad, schema) and m.projection_identity_equal(original, bad)
            assert not m.matches(case, bad, schema)
            assert not m.matches({"expectedProjection": bad}, original, schema)
            assert bad == held
            reverse_sides += 2
        if rows:
            bad = copy.deepcopy(original)
            value_at(bad, path).append(copy.deepcopy(rows[0]))
            assert not m.validate(bad, schema)
            assert not m.matches(case, bad, schema)
            assert not m.matches({"expectedProjection": bad}, original, schema)
            duplicate_sides += 2
    assert original == snapshot
assert count == 85
results["all37And85IndependentGraphSlots"] = {"cases": 37, "graphSlots": count,
    "bothSideReversalRejects": reverse_sides, "bothSideExactDuplicateRejects": duplicate_sides,
    "noInputRepairOrMutation": True}

# Trace the actual complete acceptance entry, restoring pure model functions after
# the check. No product/harness functions or candidate files are patched.
left = by_id["rdfs/cycle"]["expectedProjection"]
right = copy.deepcopy(left)
bad_right = copy.deepcopy(right)
bad_right["value"]["rdfs"].reverse()
trace = []
old_validate, old_wire, old_identity = m.validate, m.canonical_graph_slots, m.projection_identity_equal
def traced_validate(value, shape, root=None):
    if root is None: trace.append("schema-expected" if value is left else "schema-observed")
    return old_validate(value, shape, root)
def traced_wire(value, slots):
    trace.append("wire-expected" if value is left else "wire-observed")
    return old_wire(value, slots)
def traced_identity(a, b):
    trace.append("identity")
    return old_identity(a, b)
try:
    m.validate, m.canonical_graph_slots, m.projection_identity_equal = traced_validate, traced_wire, traced_identity
    assert m.matches({"expectedProjection": left}, right, schema)
    good_trace = trace[:]
    assert good_trace == ["schema-expected", "schema-observed", "wire-expected", "wire-observed", "identity"]
    trace.clear()
    assert not m.matches({"expectedProjection": left}, bad_right, schema)
    bad_trace = trace[:]
    assert "identity" not in bad_trace
finally:
    m.validate, m.canonical_graph_slots, m.projection_identity_equal = old_validate, old_wire, old_identity
results["acceptanceOrder"] = {"valid": good_trace, "invalidObservedWire": bad_trace, "identityNotCalledOnBadWire": True}

def legacy(graph):
    return {"kind": "legacy", "complete": True, "value": {"rdfs": [], "rules": graph,
        "warnings": [], "rdfsEvidence": [], "evidence": []}}

XSD = "http://www.w3.org/2001/XMLSchema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
iri = lambda s: {"kind": "iri", "value": s}
blank = lambda s: {"kind": "blank", "label": s}
literal = lambda s, datatype=XSD + "string", language=None: {"kind": "literal", "lexical": s, "datatype": datatype, "language": language}
base = legacy([["<urn:x>", "<urn:p>", '"hello"@en']])
aliases = legacy([["<urn:x>", "<urn:p>", '"hello"@EN'], ["<urn:x>", "<urn:p>", '"hello"@en']])
assert m.validate(aliases, schema)
assert not m.matches({"expectedProjection": base}, aliases, schema)
assert not m.matches({"expectedProjection": aliases}, base, schema)
assert not m.matches({"expectedProjection": aliases}, aliases, schema)
single = legacy([["<urn:x>", "<urn:p>", '"hello"@EN']])
assert m.matches({"expectedProjection": base}, single, schema)
typed = copy.deepcopy(by_id["scope/asserted"]["expectedProjection"])
typed["value"]["facts"] = [[iri("urn:x"), iri("urn:p"), literal("hello", RDF + "langString", "en")]]
typed_aliases = copy.deepcopy(typed)
typed_aliases["value"]["facts"].insert(0, [iri("urn:x"), iri("urn:p"), literal("hello", RDF + "langString", "EN")])
assert m.validate(typed_aliases, schema)
assert not m.matches({"expectedProjection": typed}, typed_aliases, schema)
assert not m.matches({"expectedProjection": typed_aliases}, typed, schema)
assert not m.matches({"expectedProjection": typed_aliases}, typed_aliases, schema)
results["sortedAliasDuplicates"] = {"typedAndN3SchemaValid": True, "bothSidesAndBothBadRejected": True,
    "singleLanguageCaseIdentityStillAccepted": True, "abstractSerializerFixturesNotBusinessScopes": True}

clean = legacy([["<urn:x>", "<urn:p>", '"hello"']])
tokens = [
    '"hello"^^<' + XSD + 'string>', '"\\u0068ello"', '"a\\/b"',
    '"bad\nline"', '"bad\tline"', '"bad\rline"', '<urn:bad|value>',
    '<urn:bad^value>', '<urn:bad{value>', '<urn:bad\\value>', '<relative>',
    '"hello"@', '"hello"@en-', '"hello"^^<' + RDF + 'langString>', '_:1bad',
]
for token in tokens:
    malformed = legacy([["<urn:x>", "<urn:p>", token]])
    assert m.validate(malformed, schema)
    assert not m.canonical_graph_wire(malformed["value"]["rules"], "n3-graph")
    assert not m.matches({"expectedProjection": clean}, malformed, schema)
    assert not m.matches({"expectedProjection": malformed}, clean, schema)
    assert not m.matches({"expectedProjection": malformed}, malformed, schema)
typed_rows = [
    [iri("urn:bad|value"), iri("urn:p"), iri("urn:y")],
    [literal("subject"), iri("urn:p"), iri("urn:y")],
    [iri("urn:x"), blank("p"), iri("urn:y")],
    [iri("urn:x"), iri("urn:p"), literal("hello", XSD + "string", "en")],
    [iri("urn:x"), iri("urn:p"), literal("hello", RDF + "langString", None)],
    [iri("urn:x"), iri("urn:p"), literal("hello", "urn:bad|datatype", None)],
    [iri("urn:x"), iri("urn:p"), literal("\ud800")],
]
for row in typed_rows:
    malformed = copy.deepcopy(typed)
    malformed["value"]["facts"] = [row]
    assert m.validate(malformed, schema)
    assert not m.canonical_graph_wire([row], "typed-graph")
    assert not m.matches({"expectedProjection": malformed}, malformed, schema)
results["finiteExpressionGate"] = {"schemaAllowedN3BadTokens": len(tokens), "schemaAllowedTypedBadRows": len(typed_rows),
    "badExpectedBadObservedAndBothBadRejected": True, "fullRDFOrDatatypeValueValidationClaimed": False}

# Positive crossing alpha map: each side's original graph wire is sorted, while
# identity uses a->q and b->p. Evidence is ordered with distinct fixed rule IDs.
alpha_left = legacy([["_:a", "<urn:p>", "<urn:x>"], ["_:b", "<urn:p>", "<urn:y>"]])
alpha_right = legacy([["_:p", "<urn:p>", "<urn:y>"], ["_:q", "<urn:p>", "<urn:x>"]])
for p, a, b in [(alpha_left, "a", "b"), (alpha_right, "q", "p")]:
    p["value"]["evidence"] = [
        {"rule": "r-a", "result": ["_:" + a, "<urn:p>", "<urn:x>"],
         "inputs": [["_:" + b, "<urn:p>", "<urn:y>"]] * 2,
         "basis": [["_:" + a, "<urn:p>", "<urn:x>"]]},
        {"rule": "r-b", "result": ["_:" + b, "<urn:p>", "<urn:y>"],
         "inputs": [["_:" + a, "<urn:p>", "<urn:x>"]],
         "basis": [["_:" + b, "<urn:p>", "<urn:y>"]]},
    ]
assert m.matches({"expectedProjection": alpha_left}, alpha_right, schema)
assert m.matches({"expectedProjection": alpha_right}, alpha_left, schema)
bad = copy.deepcopy(alpha_right)
bad["value"]["evidence"][0]["result"][0] = "_:p"
assert not m.matches({"expectedProjection": alpha_left}, bad, schema)
bad = copy.deepcopy(alpha_right)
bad["value"]["evidence"][0]["inputs"].pop()
assert not m.matches({"expectedProjection": alpha_left}, bad, schema)
bad = copy.deepcopy(alpha_right)
bad["value"]["evidence"].append(copy.deepcopy(bad["value"]["evidence"][0]))
assert not m.matches({"expectedProjection": alpha_left}, bad, schema)
typed_left = copy.deepcopy(by_id["scope/asserted"]["expectedProjection"])
typed_right = copy.deepcopy(typed_left)
typed_left["value"]["facts"] = [[blank("a"), iri("urn:p"), iri("urn:x")], [blank("b"), iri("urn:p"), iri("urn:y")]]
typed_right["value"]["facts"] = [[blank("p"), iri("urn:p"), iri("urn:y")], [blank("q"), iri("urn:p"), iri("urn:x")]]
assert m.matches({"expectedProjection": typed_left}, typed_right, schema)
results["canonicalCrossingAlpha"] = {"n3AndTypedPositive": True, "sharedGraphEvidenceMapping": True,
    "conflictTailOrOccurrenceCountChangeRejected": True, "notProductInputPermissionOrScopeProof": True}

for token in ['"word@EN"', '"01"^^<' + XSD + 'integer>', '"1"^^<' + XSD + 'int>', '"a\\nb"', '"é"']:
    record = legacy([["<urn:x>", "<urn:p>", token]])
    assert m.matches({"expectedProjection": record}, copy.deepcopy(record), schema)
word = legacy([["<urn:x>", "<urn:p>", '"word@EN"']])
lowered_word = legacy([["<urn:x>", "<urn:p>", '"word@en"']])
assert not m.matches({"expectedProjection": word}, lowered_word, schema)
numeric = legacy([["<urn:x>", "<urn:p>", '"01"^^<' + XSD + 'integer>']])
for token in ['"1"^^<' + XSD + 'integer>', '"01"^^<' + XSD + 'int>']:
    assert not m.matches({"expectedProjection": numeric}, legacy([["<urn:x>", "<urn:p>", token]]), schema)
results["lexicalAndDatatypePreserved"] = True

known = [c["expectedProjection"] for c in cases if c["expectedProjection"]["kind"] == "rejection"]
refusal_checks = 0
for case in cases:
    assert not m.matches(case, m.unknown(case["harnessStage"]), schema)
    if case["expectedProjection"]["kind"] != "rejection":
        for refusal in known:
            assert not m.matches(case, refusal, schema)
            refusal_checks += 1
results["normalRejectSafety"] = {"unknownCannotMatch": 37, "normalAgainstKnownRejects": refusal_checks}
p = OUT / "r3-proof.json"
proof = json.loads(p.read_text())
proof["results"]["independentBoundaries"] = results
p.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(results, ensure_ascii=False, indent=2))
