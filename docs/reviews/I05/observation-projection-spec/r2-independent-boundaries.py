"""New independent mathematical boundary checks; no product objects or calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
DESIGN = ROOT / "docs/iterations/I05/observation-projection-spec"
spec = importlib.util.spec_from_file_location("r2_independent_model", DESIGN / "model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
schema = json.loads((DESIGN / "schema.json").read_text())
cases = json.loads((DESIGN / "cases.json").read_text())["cases"]
by_id = {c["id"]: c for c in cases}
results = {}
touched = []

class Poison:
    def __getattribute__(self, _):
        touched.append("attribute")
        raise AssertionError("foreign attribute touched")
    def __str__(self):
        touched.append("str")
        raise AssertionError("foreign str touched")
    def __repr__(self):
        touched.append("repr")
        raise AssertionError("foreign repr touched")
    def __eq__(self, _):
        touched.append("eq")
        raise AssertionError("foreign eq touched")
    def __hash__(self):
        touched.append("hash")
        raise AssertionError("foreign hash touched")
    def __iter__(self):
        touched.append("iter")
        raise AssertionError("foreign iter touched")

class ForeignString(str):
    def __eq__(self, _):
        touched.append("str-eq")
        raise AssertionError("foreign str eq touched")
    def __hash__(self):
        touched.append("str-hash")
        raise AssertionError("foreign str hash touched")

bad_stages = ["/private/independent-stage", "https://private.invalid/secret", "new-unknown-stage",
              None, True, 23, [], {}, Poison(), ForeignString("restore")]
outputs = 0
for stage in bad_stages:
    for output in [m.unknown(stage), m.safe_projection(Poison(), stage, schema),
                   m.safe_projection(by_id["scope/missing-source"]["expectedProjection"]["diagnostic"], stage, schema)]:
        assert m.validate(output, schema)
        assert output == m.unknown("collection-failure")
        assert output["complete"] is False
        assert not any(secret in json.dumps(output) for secret in ["/private/independent-stage", "https://private.invalid/secret", "new-unknown-stage"])
        outputs += 1
for stage in m.HARNESS_STAGES:
    output = m.safe_projection(Poison(), stage, schema)
    assert m.validate(output, schema) and output == m.unknown(stage)
assert not touched
assert not any(m.matches(c, m.unknown("collection-failure"), schema) for c in cases)
results["stageSafety"] = {"invalidInputs": len(bad_stages), "schemaValidSafeOutputs": outputs,
    "validStagesWithPoisonDiagnostic": len(m.HARNESS_STAGES), "dangerousMethodCalls": touched}

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD = "http://www.w3.org/2001/XMLSchema#"
iri = lambda s: {"kind": "iri", "value": s}
blank = lambda s: {"kind": "blank", "label": s}
literal = lambda s, lang: {"kind": "literal", "lexical": s, "datatype": RDF + "langString", "language": lang}
left_graph = [[blank("a"), iri(RDF + "first"), literal("word@EN", "EN")], [blank("a"), iri(RDF + "rest"), iri(RDF + "nil")]]
right_graph = [[blank("p"), iri(RDF + "first"), literal("word@EN", "en")], [blank("p"), iri(RDF + "rest"), iri(RDF + "nil")]]
assert m.graph_isomorphic(left_graph, right_graph)
assert not m.graph_isomorphic(left_graph, right_graph[:-1])
wrong = copy.deepcopy(right_graph)
wrong[0][2]["lexical"] = "word@en"
assert not m.graph_isomorphic(left_graph, wrong)

# This is an abstract terminal-shaped identity object. It deliberately does not
# claim a business-valid scope, source digest/capture, legal data BNodes or runtime.
left = copy.deepcopy(by_id["scope/fresh"]["expectedProjection"])
assignments = [
    (("value", "facts", 0, 0), "typed", "a"),
    (("value", "facts", 1, 0), "typed", "b"),
    (("value", "ontology", 0, 0), "typed", "a"),
    (("value", "reasoning_result", "rdfs", 0, 0), "n3", "a"),
    (("value", "reasoning_result", "rules", 0, 0), "n3", "b"),
    (("value", "reasoning_result", "rdfsEvidence", 0, "result", 0), "n3", "a"),
    (("value", "reasoning_result", "rdfsEvidence", 0, "basis", 0, 0), "n3", "a"),
    (("value", "reasoning_result", "evidence", 0, "result", 0), "n3", "b"),
    (("value", "reasoning_result", "evidence", 0, "inputs", 0, 0), "n3", "a"),
    (("value", "reasoning_result", "evidence", 0, "inputs", 3, 0), "n3", "b"),
    (("value", "reasoning_result", "evidence", 0, "basis", 0, 0), "n3", "a"),
    (("value", "provenance", "selectedFacts", 0, "triple", 0), "n3", "a"),
    (("value", "provenance", "selectedFacts", 0, "sources", 0, "basis", 0, 0), "n3", "a"),
    (("value", "provenance", "selectedFacts", 6, "sources", 0, "inputs", 0, 0), "n3", "b"),
    (("value", "provenance", "derivedAxioms", 0, "triple", 0), "n3", "a"),
    (("value", "provenance", "derivedAxioms", 0, "source", "basis", 0, 0), "n3", "b"),
    (("query", "rows", 0, 0), "typed", "a"),
    (("query", "rows", 1, 0), "typed", "b"),
    (("shacl", "violations", 0, "focus"), "typed", "a"),
    (("shacl", "violations", 0, "sourceShape"), "typed", "a"),
    (("shacl", "violations", 1, "sourceShape"), "typed", "b"),
]

def put(obj, path, v):
    for k in path[:-1]: obj = obj[k]
    obj[path[-1]] = v

for path, mode, label in assignments:
    put(left, path, blank(label) if mode == "typed" else "_:" + label)
right = copy.deepcopy(left)
for path, mode, label in assignments:
    mapped = {"a": "q", "b": "p"}[label]
    put(right, path, blank(mapped) if mode == "typed" else "_:" + mapped)
assert m.validate(left, schema) and m.validate(right, schema)
assert m.projection_identity_equal(left, right)
assert m.matches({"expectedProjection": left}, right, schema)
rejected_conflicts = []
for path, mode, label in assignments:
    changed = copy.deepcopy(right)
    other = {"a": "p", "b": "q"}[label]
    put(changed, path, blank(other) if mode == "typed" else "_:" + other)
    assert not m.projection_identity_equal(left, changed)
    rejected_conflicts.append(list(path))
changed = copy.deepcopy(right)
changed["value"]["reasoning_result"]["evidence"][0]["inputs"].pop()
assert not m.matches({"expectedProjection": left}, changed, schema)
changed = copy.deepcopy(right)
changed["value"]["reasoning_result"]["evidence"].append(copy.deepcopy(changed["value"]["reasoning_result"]["evidence"][0]))
assert not m.matches({"expectedProjection": left}, changed, schema)
changed = copy.deepcopy(right)
changed["value"]["provenance"]["reasoningSource"]["assertedDigest"] = "0" * 64
assert not m.projection_identity_equal(left, changed)
results["jointDomain"] = {"globalMap": {"a": "q", "b": "p"}, "schemaValidAbstractFixture": True,
    "globalPermutationAccepted": True, "contradictoryPositionsRejected": rejected_conflicts,
    "evidenceTailAndOccurrenceMultiplicityExact": True, "digestMutationRejected": True,
    "businessScopeOrProvenanceProved": False}

slots = [(("graph",), "typed-graph"), (("tokens",), "n3-sequence")]
small_left = {"graph": left_graph, "tokens": ['"word@EN"@EN', '"word@EN"', "_:a"], "raw": {"language_raw": "EN", "source": None, "text": "_:a"}}
small_right = {"graph": right_graph, "tokens": ['"word@EN"@en', '"word@EN"', "_:p"], "raw": copy.deepcopy(small_left["raw"])}
assert m.identity_domain_equal(small_left, small_right, slots)
for field, value in [("language_raw", "en"), ("source", ""), ("text", "_:p")]:
    changed = copy.deepcopy(small_right)
    changed["raw"][field] = value
    assert not m.identity_domain_equal(small_left, changed, slots)
changed = copy.deepcopy(small_right)
changed["tokens"][1] = '"word@en"'
assert not m.identity_domain_equal(small_left, changed, slots)
results["quotedLexicalAndNonRDFRawExact"] = True

a = {"graph": [[blank("a"), iri("urn:p"), iri("urn:x")]]}
p = {"graph": [[blank("p"), iri("urn:p"), iri("urn:x")]]}
q = {"graph": [[blank("q"), iri("urn:p"), iri("urn:x")]]}
assert m.identity_domain_equal(a, p, [(("graph",), "typed-graph")])
assert m.identity_domain_equal(a, q, [(("graph",), "typed-graph")])
assert not m.identity_domain_equal({"one": a["graph"], "two": a["graph"]}, {"one": p["graph"], "two": q["graph"]}, [(("one",), "typed-graph"), (("two",), "typed-graph")])
results["independentArtifacts"] = {"eachIndependentlyComparedDomainAccepted": True,
    "combiningIndependentArtifactsCreatesFalseConstraint": True,
    "callerMustSupplyActualArtifactBindingAndSeparateDomains": True,
    "runtimeBindingImplementedByThisWindow": False}

def digest(v): return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
with_hash_left = {"graph": left_graph, "digest": digest(left_graph)}
with_hash_right = {"graph": right_graph, "digest": digest(right_graph)}
assert with_hash_left["digest"] != with_hash_right["digest"]
assert not m.identity_domain_equal(with_hash_left, with_hash_right, [(("graph",), "typed-graph")])
results["bnodeDigestCompatibility"] = {"eachPreimageDigestCorrect": True, "alphaEquivalentGraphs": True,
    "contentDigestsDiffer": True, "currentExactDigestComparisonRejects": True,
    "explicitlyPendingInSpec": True, "notClaimedAValidCapturedScope": True}

refusals = [c["expectedProjection"] for c in cases if c["expectedProjection"]["kind"] == "rejection"]
count = 0
for c in cases:
    if c["expectedProjection"]["kind"] != "rejection":
        for r in refusals:
            assert not m.matches(c, r, schema)
            count += 1
results["normalAgainstEveryKnownRefusalRejected"] = count
proof_path = OUT / "r2-proof.json"
proof = json.loads(proof_path.read_text())
proof["results"]["independentBoundaryChecks"] = results
proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(results, ensure_ascii=False, indent=2))
