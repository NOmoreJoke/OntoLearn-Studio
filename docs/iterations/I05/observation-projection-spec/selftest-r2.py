"""R2 detached-design regression and new R1 counterexamples; no product calls.

The original twenty test methods remain separately identifiable and unchanged.
New BNode fixtures are mathematical RDF artifacts, not permitted product inputs,
engine success objects, producer/capture records or actual observations.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
from selftest import DesignTests, CASES, BY_ID, SCHEMA
import model as m

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
R1 = "57c67631fab6a36f47963aca95b4036064e10777"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD = "http://www.w3.org/2001/XMLSchema#"


def iri(s):
    return {"kind": "iri", "value": s}


def blank(s):
    return {"kind": "blank", "label": s}


def literal(text, datatype=RDF + "langString", language="EN"):
    return {"kind": "literal", "lexical": text, "datatype": datatype, "language": language}


def list_graph(label="a", language="EN"):
    return [[blank(label), iri(RDF + "first"), literal("hello", language=language)],
            [blank(label), iri(RDF + "rest"), iri(RDF + "nil")]]


class R2DeltaTests(unittest.TestCase):
    def test_r1_01_stage_is_closed_before_any_untrusted_operation(self):
        touched = []
        class Poison:
            def __getattribute__(self, _):
                touched.append("getattribute")
                raise AssertionError("foreign attribute read")
            def __str__(self):
                touched.append("str")
                raise AssertionError("foreign string conversion")
            def __repr__(self):
                touched.append("repr")
                raise AssertionError("foreign repr conversion")
            def __eq__(self, _):
                touched.append("eq")
                raise AssertionError("foreign equality")
            def __hash__(self):
                touched.append("hash")
                raise AssertionError("foreign hash")
        class ForeignString(str):
            def __eq__(self, _):
                touched.append("str-subclass-eq")
                raise AssertionError("foreign string equality")
        bad = [None, True, 1, [], {}, "/private/r1-sensitive-path",
               "https://secret.invalid/path", "not-a-registered-stage", Poison(),
               ForeignString("restore")]
        diagnostic = BY_ID["scope/wrong-source"]["expectedProjection"]["diagnostic"]
        for value in bad:
            for output in (m.unknown(value), m.safe_projection(diagnostic, value, SCHEMA),
                           m.safe_projection(Poison(), value, SCHEMA)):
                self.assertTrue(m.validate(output, SCHEMA))
                self.assertEqual(output, m.unknown("collection-failure"))
                encoded = json.dumps(output)
                for secret in ("/private/r1-sensitive-path", "https://secret.invalid/path",
                               "not-a-registered-stage"):
                    self.assertNotIn(secret, encoded)
        self.assertEqual(touched, [])

    def test_r1_01_valid_stage_and_reserved_incomplete(self):
        for case in CASES:
            stage = case["harnessStage"]
            self.assertEqual(m.unknown(stage)["harnessStage"], stage)
            self.assertTrue(m.validate(m.unknown(stage), SCHEMA))
            self.assertFalse(m.matches(case, m.unknown(stage), SCHEMA))
            if case["expectedProjection"]["kind"] == "rejection":
                self.assertEqual(m.safe_projection(case["expectedProjection"]["diagnostic"],
                                                   stage, SCHEMA), case["expectedProjection"])
        bad = copy.deepcopy(BY_ID["scope/missing-source"]["expectedProjection"])
        bad["harnessStage"] = "collection-failure"
        self.assertFalse(m.validate(bad, SCHEMA))
        self.assertTrue(SCHEMA["$id"].endswith(":2"))
        branches = SCHEMA["$defs"]["rejection"]["oneOf"]
        self.assertEqual(set(branches[0]["properties"]["harnessStage"]["enum"]), set(m.HARNESS_STAGES))
        self.assertEqual(set(branches[1]["properties"]["harnessStage"]["enum"]),
                         set(m.HARNESS_STAGES) | {m.COLLECTION_FAILURE_STAGE})

    def test_r1_02_language_and_tail_graph_identity(self):
        left, right = list_graph(), list_graph("p", "en")
        before = copy.deepcopy((left, right))
        self.assertTrue(m.graph_isomorphic(left, right))
        self.assertFalse(m.graph_isomorphic(left, right[:-1]))
        self.assertEqual((left, right), before)
        self.assertNotEqual(m.n3(left[0][2]), m.n3(right[0][2]))
        folded = copy.deepcopy(right)
        folded[0][2]["lexical"] = "HELLO"
        self.assertFalse(m.graph_isomorphic(left, folded))

    def test_r1_02_numeric_lexical_datatype_and_node_collapse(self):
        for lexical, datatype in [("1", XSD + "integer"), ("01", XSD + "int")]:
            left = [[blank("a"), iri(RDF + "first"), literal("01", XSD + "integer", None)]]
            right = [[blank("p"), iri(RDF + "first"), literal(lexical, datatype, None)]]
            self.assertFalse(m.graph_isomorphic(left, right))
        left = [[blank("a"), iri(RDF + "rest"), blank("b")],
                [blank("b"), iri(RDF + "rest"), iri(RDF + "nil")]]
        right = [[blank("p"), iri(RDF + "rest"), blank("p")],
                 [blank("p"), iri(RDF + "rest"), iri(RDF + "nil")]]
        self.assertFalse(m.graph_isomorphic(left, right))

    def artifact(self, a="a", b="b", language="EN"):
        return {
            "typedGraph": [[blank(a), iri("urn:p"), literal("hello", language=language)],
                           [blank(b), iri("urn:p"), iri("urn:y")]],
            "evidence": [{"result": ["_:" + a, "<urn:p>", '"hello"@' + language],
                          "inputs": [["_:" + a, "<urn:p>", '"hello"@' + language]] * 2}],
            "query": {"variables": ["s"], "rows": [[blank(a)], [blank(b)], [blank(a)]]},
            "shacl": {"conforms": False, "violations": [{
                "focus": blank(a), "path": iri("urn:p"), "value": literal("hello", language=language),
                "sourceShape": blank(a), "constraint": iri("urn:constraint"),
                "severity": iri("urn:severity")}]},
            "raw": {"language_raw": "EN", "inputText": '"hello"@EN',
                    "source": None, "looksLikeNodeButIsRaw": "_:a"},
        }

    def slots(self):
        return [(("typedGraph",), "typed-graph"),
                (("evidence", 0, "result"), "n3-sequence"),
                (("evidence", 0, "inputs"), "n3-sequence"),
                (("query", "rows"), "typed-sequence"),
                *(((("shacl", "violations", 0, key), "typed-sequence"))
                  for key in ("focus", "path", "value", "sourceShape", "constraint", "severity"))]

    def test_shared_domain_normal_language_and_exact_raw_source(self):
        left, right = self.artifact(), self.artifact("p", "q", "en")
        before = copy.deepcopy((left, right))
        self.assertTrue(m.identity_domain_equal(left, right, self.slots()))
        self.assertEqual((left, right), before)
        for key, value in [("language_raw", "en"), ("source", ""),
                           ("looksLikeNodeButIsRaw", "_:p")]:
            changed = copy.deepcopy(right)
            changed["raw"][key] = value
            self.assertFalse(m.identity_domain_equal(left, changed, self.slots()))

    def test_shared_domain_contradictory_query_evidence_or_source_shape(self):
        left, right = self.artifact(), self.artifact("p", "q", "en")
        # Equal global label counts: this cannot be rejected by a count shortcut.
        changes = [("query", "rows", 0, 0, "label"),
                   ("shacl", "violations", 0, "sourceShape", "label")]
        for path in changes:
            changed = copy.deepcopy(right)
            cursor = changed
            for part in path[:-1]:
                cursor = cursor[part]
            cursor[path[-1]] = "q"
            self.assertFalse(m.identity_domain_equal(left, changed, self.slots()))
        changed = copy.deepcopy(right)
        changed["evidence"][0]["result"][0] = "_:q"
        self.assertFalse(m.identity_domain_equal(left, changed, self.slots()))
        # Each slice can independently choose a conflicting bijection.
        a1 = {"graph": [[blank("a"), iri("urn:p"), iri("urn:x")]]}
        a2 = {"graph": [[blank("a"), iri("urn:q"), iri("urn:y")]]}
        b1 = {"graph": [[blank("p"), iri("urn:p"), iri("urn:x")]]}
        b2 = {"graph": [[blank("q"), iri("urn:q"), iri("urn:y")]]}
        self.assertTrue(m.identity_domain_equal(a1, b1, [(("graph",), "typed-graph")]))
        self.assertTrue(m.identity_domain_equal(a2, b2, [(("graph",), "typed-graph")]))
        self.assertFalse(m.identity_domain_equal({"x": a1["graph"], "y": a2["graph"]},
                                                {"x": b1["graph"], "y": b2["graph"]},
                                                [(("x",), "typed-graph"), (("y",), "typed-graph")]))

    def test_shared_domain_order_duplicates_tail_and_no_substring_rewrite(self):
        left, right = self.artifact(), self.artifact("p", "q", "en")
        for field in ("inputs", "result"):
            changed = copy.deepcopy(right)
            changed["evidence"][0][field].pop()
            self.assertFalse(m.identity_domain_equal(left, changed, self.slots()))
        changed = copy.deepcopy(right)
        changed["query"]["rows"].reverse()
        # The original [a,b,a] palindrome intentionally survives reversal.
        self.assertTrue(m.identity_domain_equal(left, changed, self.slots()))
        changed["query"]["rows"] = [changed["query"]["rows"][1],
                                    changed["query"]["rows"][0], changed["query"]["rows"][2]]
        self.assertFalse(m.identity_domain_equal(left, changed, self.slots()))
        changed = copy.deepcopy(right)
        changed["evidence"][0]["result"][2] = '"HELLO"@en'
        self.assertFalse(m.identity_domain_equal(left, changed, self.slots()))

    def test_terminal_layout_covers_all_rdf_roles_and_shared_map(self):
        # Only detached projection comparison: this fixture does not establish
        # product input legality, provenance/digests, admission or success.
        left = copy.deepcopy(BY_ID["scope/fresh"]["expectedProjection"])
        left["value"]["ontology"] = [[blank("a"), iri(RDF + "rest"), iri(RDF + "nil")]]
        left["value"]["reasoning_result"]["evidence"][0]["result"][0] = "_:a"
        left["query"]["rows"][0][0] = blank("a")
        left["shacl"]["violations"][0]["sourceShape"] = blank("a")
        right = copy.deepcopy(left)
        right["value"]["ontology"][0][0] = blank("p")
        right["value"]["reasoning_result"]["evidence"][0]["result"][0] = "_:p"
        right["query"]["rows"][0][0] = blank("p")
        right["shacl"]["violations"][0]["sourceShape"] = blank("p")
        self.assertTrue(m.projection_identity_equal(left, right))
        right["shacl"]["violations"][0]["sourceShape"] = blank("q")
        self.assertFalse(m.projection_identity_equal(left, right))
        layout = m.projection_layout(left)
        self.assertIn((("value", "facts"), "typed-graph"), layout)
        self.assertIn((("query", "rows"), "typed-sequence"), layout)
        for field in ("focus", "path", "value", "sourceShape", "constraint", "severity"):
            self.assertIn((("shacl", "violations", 0, field), "typed-sequence"), layout)

    def test_shared_domain_provenance_basis_and_n3_numeric_identity(self):
        left = copy.deepcopy(BY_ID["scope/fresh"]["expectedProjection"])
        right = copy.deepcopy(left)
        paths = [
            ("value", "provenance", "selectedFacts", 0, "triple", 0),
            ("value", "provenance", "selectedFacts", 0, "sources", 0, "basis", 0, 0),
            ("value", "provenance", "derivedAxioms", 0, "source", "basis", 0, 0),
            ("value", "reasoning_result", "rdfsEvidence", 0, "basis", 0, 0),
            ("value", "reasoning_result", "evidence", 0, "inputs", 0, 0),
        ]
        for path in paths:
            for value, token in [(left, "_:a"), (right, "_:p")]:
                cursor = value
                for part in path[:-1]:
                    cursor = cursor[part]
                cursor[path[-1]] = token
        self.assertTrue(m.projection_identity_equal(left, right))
        right["value"]["provenance"]["derivedAxioms"][0]["source"]["basis"][0][0] = "_:q"
        self.assertFalse(m.projection_identity_equal(left, right))
        n3 = {"evidence": [["_:a", "<urn:p>", '"01"^^<' + XSD + 'integer>']]}
        for token in ['"1"^^<' + XSD + 'integer>', '"01"^^<' + XSD + 'int>']:
            changed = {"evidence": [["_:p", "<urn:p>", token]]}
            self.assertFalse(m.identity_domain_equal(n3, changed,
                                                     [(("evidence",), "n3-sequence")]))
        self.assertFalse(m.identity_domain_equal({"x": ['"word@EN"']},
                                                {"x": ['"word@en"']},
                                                [(("x",), "n3-sequence")]))

    def test_r1_03_shape_exact_chain(self):
        case = BY_ID["shape/front-2"]
        plan = case["invocation"]
        self.assertEqual(case["api"], "semantic.parse_turtle -> semantic.check_shapes")
        self.assertEqual([s["api"] for s in plan["steps"]],
                         ["semantic.parse_turtle", "semantic.parse_turtle", "semantic.check_shapes"])
        self.assertEqual(plan["steps"][0]["keywordArguments"], {"format": "turtle", "shapes": False})
        self.assertEqual(plan["steps"][1]["keywordArguments"], {"format": "turtle", "shapes": True})
        self.assertEqual(plan["steps"][2]["positional"],
                         [{"stageReturn": "dataGraph"}, {"stageReturn": "shapesGraph"}])
        self.assertEqual(plan["expectedReachedPrefix"], [0, 1])
        self.assertEqual(plan["expectedUnreachedSuffix"], [2])
        self.assertEqual(case["parameters"], {})
        self.assertIsNone(plan["newWrapper"])

    def test_r1_03_integer_explicit_parameter_mapping(self):
        case = BY_ID["integer/other-datatype-1"]
        self.assertEqual(case["api"], "semantic.validate_shacl_text")
        expected = {"data_policy": "integer-illtyped-report-v1", "range_policy": "legacy"}
        self.assertEqual(case["invocation"]["steps"][0]["keywordArguments"], expected)
        self.assertEqual({v["pythonKeyword"]: case["parameters"][k]
                          for k, v in case["invocation"]["inputParameterMapping"].items()}, expected)
        self.assertIsNone(case["invocation"]["newWrapper"])

    def test_37_fixed_inputs_and_expected_math_unchanged_from_r1(self):
        path = "docs/iterations/I05/observation-projection-spec/cases.json"
        old = json.loads(subprocess.check_output(["git", "show", R1 + ":" + path], cwd=ROOT))
        self.assertEqual(len(CASES), 37)
        for before, after in zip(old["cases"], CASES):
            for field in ("id", "parameters", "datasetId", "inputProjectionSha256",
                          "inputSourceRefs", "independentTypedMath", "expectedProjection"):
                self.assertTrue(m.exact(before[field], after[field]), (after["id"], field))
        source_path = "docs/iterations/I05/observation-projection-spec/pure-sources.json"
        self.assertEqual(subprocess.check_output(["git", "show", R1 + ":" + source_path], cwd=ROOT),
                         (ROOT / source_path).read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
