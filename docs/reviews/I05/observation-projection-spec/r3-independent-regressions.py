"""R3 independent remaining receiver boundaries; stdlib and detached model only."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
DESIGN = ROOT / "docs/iterations/I05/observation-projection-spec"
spec = importlib.util.spec_from_file_location("r3_receiver_review", DESIGN / "model.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
schema = json.loads((DESIGN / "schema.json").read_text())
cases = json.loads((DESIGN / "cases.json").read_text())["cases"]
by_id = {c["id"]: c for c in cases}
results = {}

class Poison:
    def __getattribute__(self, name):
        raise AssertionError("foreign attribute touched")
    def __eq__(self, other):
        raise AssertionError("foreign equality touched")
    def __hash__(self):
        raise AssertionError("foreign hash touched")
    def __str__(self):
        raise AssertionError("foreign str touched")
    def __repr__(self):
        raise AssertionError("foreign repr touched")

class ForeignText(str):
    def __eq__(self, other):
        raise AssertionError("str subclass equality touched")
    def __hash__(self):
        raise AssertionError("str subclass hash touched")

safe = {"kind": "rejection", "complete": False, "harnessStage": "collection-failure",
        "diagnostic": {"origin": "Unknown", "reason": "INTERNAL_ERROR", "classification": None,
                       "stage": None, "slot": None, "domain": None, "ruleId": None, "location": None},
        "partialView": None, "report": None}
values = ["/Users/private/secret", "https://secret.invalid/token", "unregistered", "", None,
          True, 1, [], {}, ForeignText("reason"), Poison()]
for value in values:
    for observed in (m.unknown(value), m.safe_projection(Poison(), value, schema)):
        assert observed == safe and m.validate(observed, schema)
results["invalidStage"] = {"distinctInputs": len(values), "unknownAndSafeProjection": 2 * len(values),
                            "foreignOperationsAndDiagnosticAccess": 0, "exactSafeSchemaValid": True}

XSD = "http://www.w3.org/2001/XMLSchema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
iri = lambda s: {"kind": "iri", "value": s}
blank = lambda s: {"kind": "blank", "label": s}
lit = lambda s, d=XSD + "string", lang=None: {"kind": "literal", "lexical": s, "datatype": d, "language": lang}
clean = copy.deepcopy(by_id["scope/asserted"]["expectedProjection"])
clean["value"]["facts"] = [[iri("urn:x"), iri("urn:p"), iri("urn:y")]]
rows = [[iri("urn:bad|value"), iri("urn:p"), iri("urn:y")],
        [lit("subject"), iri("urn:p"), iri("urn:y")],
        [iri("urn:x"), blank("p"), iri("urn:y")],
        [iri("urn:x"), iri("urn:p"), lit("hello", XSD + "string", "en")],
        [iri("urn:x"), iri("urn:p"), lit("hello", RDF + "langString", None)],
        [iri("urn:x"), iri("urn:p"), lit("hello", "urn:bad|datatype")],
        [iri("urn:x"), iri("urn:p"), lit("\ud800")]]
for row in rows:
    bad = copy.deepcopy(clean)
    bad["value"]["facts"] = [row]
    assert m.validate(bad, schema)
    assert not m.matches({"expectedProjection": clean}, bad, schema)
    assert not m.matches({"expectedProjection": bad}, clean, schema)
    assert not m.matches({"expectedProjection": bad}, bad, schema)
results["typedBadExpressionAllSides"] = {"schemaValidRows": len(rows), "rejections": 3 * len(rows)}

# Empty-to-nonempty graphs are value changes even when both wires are canonical.
checks = 0
for c in cases:
    p = c["expectedProjection"]
    for path, mode in m.projection_layout(p):
        if mode not in ("typed-graph", "n3-graph"):
            continue
        target = p
        for part in path:
            target = target[part]
        if target:
            continue
        bad = copy.deepcopy(p)
        rows_at_path = bad
        for part in path:
            rows_at_path = rows_at_path[part]
        rows_at_path.append([iri("urn:x"), iri("urn:p"), iri("urn:y")] if mode == "typed-graph"
                            else ["<urn:x>", "<urn:p>", "<urn:y>"])
        assert m.validate(bad, schema)
        assert m.canonical_graph_slots(bad, m.projection_layout(bad))
        assert not m.matches(c, bad, schema)
        assert not m.matches({"expectedProjection": bad}, p, schema)
        checks += 2
results["emptyGraphInsertion"] = {"bothSideRejections": checks}

proof_path = OUT / "r3-proof.json"
proof = json.loads(proof_path.read_text())
proof["results"]["independentRegressions"] = results
proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(results, ensure_ascii=False, indent=2))
