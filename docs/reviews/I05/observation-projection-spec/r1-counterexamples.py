"""Independent finite design checks. No product/library/runtime objects or calls."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
DESIGN = ROOT / "docs/iterations/I05/observation-projection-spec"
spec = importlib.util.spec_from_file_location("r1_detached_design", DESIGN / "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
cases = json.loads((DESIGN / "cases.json").read_text())["cases"]
schema = json.loads((DESIGN / "schema.json").read_text())
sources = json.loads((DESIGN / "pure-sources.json").read_text())
proof = json.loads((OUT / "r1-proof.json").read_text())
results = {}

def command(argv):
    r = subprocess.run(argv, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, check=False)
    proof["commands"].append({"argv": argv, "cwd": str(ROOT), "exitCode": r.returncode,
        "stdoutBytes": len(r.stdout), "stdoutSHA256": hashlib.sha256(r.stdout).hexdigest(),
        "stderrBytes": len(r.stderr), "stderrSHA256": hashlib.sha256(r.stderr).hexdigest()})
    assert r.returncode == 0
    return r.stdout

sealed = json.loads(command(["git", "show", "0e42a0fe349054a92817cb4d463bccdc15f6c042:packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-inputs.json"]))
oracle = json.loads(command(["git", "show", "3d8f4ee912f41bd03388322d29a9bfc0e7defe85:tests/fixtures/quality/i05-source-package-oracle/oracle.json"]))
so = {o["id"]: o for o in sealed["observations"]}
eo = {o["id"]: o for o in oracle["observations"]}
for o in sources["observations"]:
    assert model.exact(o, so[o["id"]])
for id, data in sources["datasets"].items():
    assert model.exact(data, sealed["datasets"][id])
for id, e in sources["externalIndependentOracle"].items():
    assert model.exact(e, eo[id])
assert len(sealed["observations"]) == 417 and len(sealed["datasets"]) == 320
assert len(sources["observations"]) == 37 and len(sources["datasets"]) == 19
for c in cases:
    original = so[c["id"]]
    assert c["parameters"] == original["parameters"]
    assert c["datasetId"] == original["datasetId"]
    assert c["inputSourceRefs"] == original["sourceRefs"]
    assert c["inputProjectionSha256"] == original["projectionSha256"]
    m = c["independentTypedMath"]
    if c["expectedProjection"]["kind"] == "legacy":
        assert model.exact(m, eo[c["id"]]["expected"]["math"])
    if c["expectedProjection"]["kind"] == "scope":
        assert all(model.exact(v, eo[c["id"]]["expected"][k]) for k, v in m.items())
results["sealedInputsAndIndependentOracleExact"] = {"observations": 37, "datasets": 19, "oracleEntries": 37, "sealedInventory": [417, 320]}

def canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def hash_json(v):
    return hashlib.sha256(canon(v).encode()).hexdigest()

def independent_n3(term):
    if term["kind"] == "iri":
        return "<" + term["value"] + ">"
    if term["kind"] == "blank":
        return "_:" + term["label"]
    text = json.dumps(term["lexical"], ensure_ascii=False)
    if term["language"] is not None:
        return text + "@" + term["language"]
    return text if term["datatype"] == "http://www.w3.org/2001/XMLSchema#string" else text + "^^<" + term["datatype"] + ">"

def triples(rows):
    return sorted({tuple(independent_n3(t) for t in row) for row in rows})

legacy_rows = []
for c in cases:
    if c["expectedProjection"]["kind"] != "legacy":
        continue
    m = c["independentTypedMath"]
    v = c["expectedProjection"]["value"]
    assert [list(t) for t in triples(m["rdfsAdded"])] == v["rdfs"]
    assert [list(t) for t in triples(m["customOutput"])] == v["rules"]
    by_result = {tuple(independent_n3(t) for t in w["result"]): w for w in m["selectedWitnesses"]}
    assert v["rdfsEvidence"] == [{"result": t, "basis": [list(r) for r in triples(by_result[tuple(t)]["leafUnion"])]} for t in v["rdfs"]]
    for i, w in enumerate(m["selectedWitnesses"]):
        assert w["ordinal"] == i
        depths = []
        leaves = []
        direct = []
        for p in w["premises"]:
            if p["kind"] == "input-triple":
                assert p["triple"] in m["inputGraph"]
                depths.append(0)
                leaves.append(p["triple"])
                direct.append(p["triple"])
            else:
                assert p["ordinal"] < i
                earlier = m["selectedWitnesses"][p["ordinal"]]
                depths.append(earlier["depth"])
                leaves.extend(earlier["leafUnion"])
                direct.append(earlier["result"])
        assert len(depths) == 2 and w["depth"] == 1 + max(depths)
        assert direct == w["orderedDirectInputTriples"]
        assert triples(leaves) == triples(w["leafUnion"])
    records = []
    for match in m["matches"]:
        if match["accepted"]:
            assert triples([t for b in match["whenBasis"] for t in b]) == triples(match["leafBasis"])
            for head in match["heads"]:
                records.append({"rule": match["ruleId"], "result": [independent_n3(t) for t in head["triple"]],
                    "inputs": [[independent_n3(t) for t in t3] for t3 in match["when"]],
                    "basis": [list(t) for t in triples(match["leafBasis"])]})
    records.sort(key=lambda r: (r["rule"], r["result"], r["inputs"], r["basis"]))
    assert records == v["evidence"]
    legacy_rows.append({"id": c["id"], "rdfs": len(v["rdfs"]), "rules": len(v["rules"]), "rdfsEvidence": len(v["rdfsEvidence"]), "evidence": len(records)})
results["legacyFullProjectionAndWitnessConsistency"] = legacy_rows

scope_rows = []
asserted = next(c for c in cases if c["id"] == "scope/asserted")["expectedProjection"]["value"]
for c in cases:
    if c["expectedProjection"]["kind"] != "scope":
        continue
    p = c["expectedProjection"]
    v = p["value"]
    pr = v["provenance"]
    for name, facts, ontology in [("asserted", asserted["facts"], asserted["ontology"]), ("selected", v["facts"], v["ontology"])]:
        assert pr["views"][name] == {"factsCount": len(facts), "ontologyCount": len(ontology),
            "factsDigest": hash_json({"domain": "i05-scope-facts/1", "graph": facts}),
            "ontologyDigest": hash_json({"domain": "i05-scope-ontology/1", "graph": ontology})}
    if c["id"] == "scope/asserted":
        assert pr["reasoningSource"] is None and v["reasoning_result"] is None
    else:
        assert pr["reasoningSource"] == {"format": "i05-scope-content-source/1",
            "assertedDigest": pr["views"]["asserted"]["factsDigest"],
            "ontologyDigest": pr["views"]["asserted"]["ontologyDigest"],
            "rulesDigest": hash_json({"domain": "i05-scope-rules/1", "rules": sources["datasets"][c["datasetId"]]["rules"]})}
    assert [r["triple"] for r in pr["selectedFacts"]] == [list(t) for t in triples(v["facts"])]
    assert p["query"] == eo[c["id"]]["expected"]["query"]
    assert p["shacl"] == eo[c["id"]]["expected"]["shacl"]
    scope_rows.append({"id": c["id"], "facts": len(v["facts"]), "ontology": len(v["ontology"]), "allDigestsRecomputed": True})
results["scopeFullGraphsSourcesAndDigests"] = scope_rows

def locations(v, path=()):
    yield path, v
    if isinstance(v, dict):
        for k, val in v.items(): yield from locations(val, path + (k,))
    if isinstance(v, list):
        for k, val in enumerate(v): yield from locations(val, path + (k,))

def access(v, path):
    for k in path: v = v[k]
    return v

counts = {"missingNestedField": 0, "nonemptyTail": 0, "emptyToNonempty": 0, "typeConfusion": 0, "normalVsKnownRejection": 0}
known = [c["expectedProjection"] for c in cases if c["expectedProjection"]["kind"] == "rejection"]
for c in cases:
    v = c["expectedProjection"]
    assert model.validate(v, schema) and model.matches(c, v, schema)
    for path, item in locations(v):
        if isinstance(item, dict):
            for key in item:
                changed = copy.deepcopy(v)
                del access(changed, path)[key]
                assert not model.matches(c, changed, schema)
                counts["missingNestedField"] += 1
        if isinstance(item, list):
            changed = copy.deepcopy(v)
            sequence = access(changed, path)
            if sequence:
                sequence.pop()
                counts["nonemptyTail"] += 1
            else:
                sequence.append(None)
                counts["emptyToNonempty"] += 1
            assert not model.matches(c, changed, schema)
        if item is None or type(item) in (bool, int):
            changed = copy.deepcopy(v)
            parent = access(changed, path[:-1])
            parent[path[-1]] = 1 if item is None or type(item) is bool else True
            assert not model.matches(c, changed, schema)
            counts["typeConfusion"] += 1
    if v["kind"] != "rejection":
        for refusal in known:
            assert not model.matches(c, refusal, schema)
            counts["normalVsKnownRejection"] += 1
    assert not model.matches(c, model.unknown(c["harnessStage"]), schema)
results["independentMutationCounts"] = counts

repeat = next(c for c in cases if c["id"] == "legacy/repeated-variable")
m = copy.deepcopy(repeat["independentTypedMath"])
m["matches"][0]["heads"] *= 2
assert len(model.legacy(m, [])["evidence"]) == 2
m["matches"][0]["when"] *= 2
assert all(len(r["inputs"]) == 2 for r in model.legacy(m, [])["evidence"])
results["duplicateHeadAndPremiseOccurrencesRetained"] = True

good_diag = known[0]["diagnostic"]
bad_stage = "/private/r1-sensitive-path"
unsafe = model.safe_projection(copy.deepcopy(good_diag), bad_stage, schema)
results["counterexampleUnsafeHarnessFallback"] = {"inputStage": bad_stage, "actualOutput": unsafe,
    "schemaValid": model.validate(unsafe, schema), "sensitiveStageRetained": unsafe["harnessStage"] == bad_stage}

iri = lambda s: {"kind": "iri", "value": s}
blank = lambda s: {"kind": "blank", "label": s}
literal = lambda lang: {"kind": "literal", "lexical": "hello", "datatype": "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "language": lang}
left = [[blank("a"), iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#first"), literal("EN")],
        [blank("a"), iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest"), iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#nil")]]
right = [[blank("p"), row[1], literal("en") if i == 0 else row[2]] for i, row in enumerate(left)]
results["counterexampleBNodeLanguageIdentity"] = {"left": left, "right": right,
    "actualGraphIsomorphic": model.graph_isomorphic(left, right), "requiredByRDFIdentityPolicy": True}
assert not model.graph_isomorphic(left, right)
renamed = [[blank("p"), row[1], row[2]] for row in left]
assert model.graph_isomorphic(left, renamed)
assert not model.graph_isomorphic(left, renamed[:-1])

lang_a = [iri("urn:x"), iri("urn:p"), literal("EN")]
lang_b = [iri("urn:x"), iri("urn:p"), literal("en")]
assert model.graph([lang_a]) == model.graph([lang_b])
assert model.n3(literal("EN")) != model.n3(literal("en"))
assert model.n3({"kind": "literal", "lexical": "01", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "language": None}) != model.n3({"kind": "literal", "lexical": "1", "datatype": "http://www.w3.org/2001/XMLSchema#integer", "language": None})
results["numericLexicalAndRawLanguageRemainDistinct"] = True

restore = [c for c in cases if c["family"] == "restore-negative"]
assert len(restore) == 14
for c in restore:
    assert c["preconditions"] and c["independentTypedMath"] is None
    assert c["expectedProjection"] == restore[0]["expectedProjection"]
    assert c["parameters"] == eo[c["id"]]["parameters"]
    assert eo[c["id"]]["expected"]["failureStage"] == "A1"
results["restoreTargetAudit"] = {"ids": [c["id"] for c in restore], "conditionalNewProposalOnly": True,
    "mutationBytesExecuted": False, "earlierFailuresMustRemainNotReached": True}
proof["independentChecks"] = results
(OUT / "r1-proof.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(results, ensure_ascii=False, indent=2))
