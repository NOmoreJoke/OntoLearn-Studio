"""Tests of the independent design only. No engine, library, product or fixture runner."""

import copy
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
from model import (digest, exact, graph_isomorphic, legacy, matches, n3, rejection,
                   safe_projection, scope, strict_json, unknown, validate)

HERE = Path(__file__).parent
CASES = json.loads((HERE / "cases.json").read_text())["cases"]
SCHEMA = json.loads((HERE / "schema.json").read_text())
SOURCES = json.loads((HERE / "pure-sources.json").read_text())
BY_ID = {case["id"]: case for case in CASES}
TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
SUB = "<http://www.w3.org/2000/01/rdf-schema#subClassOf>"


class DesignTests(unittest.TestCase):
    def test_37_exact_ids_and_targets(self):
        self.assertEqual(len(CASES), 37)
        self.assertEqual(len(BY_ID), 37)
        for case in CASES:
            with self.subTest(id=case["id"]):
                self.assertTrue(validate(case["expectedProjection"], SCHEMA))
                self.assertTrue(matches(case, copy.deepcopy(case["expectedProjection"]), SCHEMA))
                if case["expectedProjection"]["kind"] == "legacy":
                    warnings = ["RULE_CHAIN_UNSUPPORTED:R-next"] if case["id"] == "legacy/no-rule-feedback" else []
                    self.assertEqual(legacy(case["independentTypedMath"], warnings),
                                     case["expectedProjection"]["value"])
                if case["expectedProjection"]["kind"] == "scope":
                    expected = SOURCES["externalIndependentOracle"][case["id"]]["expected"]
                    asserted = SOURCES["externalIndependentOracle"]["scope/asserted"]["expected"]
                    self.assertEqual(scope(expected, asserted, SOURCES["datasets"][case["datasetId"]]),
                                     case["expectedProjection"]["value"])

    def test_hand_authored_type_example(self):
        a = ["<urn:ontolearn:A>", SUB, "<urn:ontolearn:B>"]
        seed = ["<urn:ontolearn:x>", TYPE, "<urn:ontolearn:A>"]
        result = ["<urn:ontolearn:x>", TYPE, "<urn:ontolearn:B>"]
        # Independent literal expected: no model builder is used here.
        expected = {"rdfs": [result], "rules": [], "warnings": [],
                    "rdfsEvidence": [{"result": result, "basis": [a, seed]}], "evidence": []}
        self.assertEqual(BY_ID["rdfs/type"]["expectedProjection"]["value"], expected)

    def test_hand_depth_two_has_all_three_leaves(self):
        case = BY_ID["rdfs/domain-depth2"]["expectedProjection"]["value"]
        self.assertEqual(len(case["rdfsEvidence"][-1]["basis"]), 3)
        self.assertEqual(case["rdfsEvidence"][-1]["result"][-1], "<urn:ontolearn:B>")

    def test_hand_multiple_matches_preserve_two_occurrences(self):
        case = BY_ID["legacy/multiple-matches"]["expectedProjection"]["value"]
        self.assertEqual(len(case["rules"]), 1)
        self.assertEqual(len(case["evidence"]), 2)
        self.assertEqual(len(case["evidence"][0]["inputs"]), 4)
        self.assertEqual(case["evidence"][0]["result"], case["evidence"][1]["result"])
        self.assertNotEqual(case["evidence"][0]["inputs"], case["evidence"][1]["inputs"])

    def test_evidence_duplicate_occurrence_is_not_deduplicated(self):
        original = BY_ID["legacy/repeated-variable"]["independentTypedMath"]
        doubled = copy.deepcopy(original)
        doubled["matches"] *= 2
        self.assertEqual(len(legacy(doubled, [])["evidence"]), 2)

    def test_ordered_when_duplicate_positions_survive(self):
        math = copy.deepcopy(BY_ID["legacy/repeated-variable"]["independentTypedMath"])
        math["matches"][0]["when"] *= 2
        self.assertEqual(len(legacy(math, [])["evidence"][0]["inputs"]), 2)

    def test_normal_cannot_match_any_rejection_or_unknown(self):
        for case in CASES:
            if case["expectedProjection"]["kind"] != "rejection":
                self.assertFalse(matches(case, unknown("reason"), SCHEMA))
                self.assertFalse(matches(case, rejection("SemanticError", "INVALID_TURTLE",
                                                         "parse-data"), SCHEMA))
                bad = rejection("RestoreFailure", "RESTORE_LIMIT", "restore", "resource", "entry")
                self.assertFalse(matches(case, bad, SCHEMA))

    def test_known_rejections_do_not_all_match_each_other(self):
        wanted = BY_ID["scope/missing-source"]
        wrong = BY_ID["scope/wrong-source"]["expectedProjection"]
        self.assertTrue(validate(wrong, SCHEMA))
        self.assertFalse(matches(wanted, wrong, SCHEMA))
        for case in CASES:
            if case["family"] == "restore-negative":
                self.assertFalse(matches(case, rejection("RestoreFailure", "RESTORE_INPUT_INVALID",
                                                         "restore", "input", "entry"), SCHEMA))

    def test_missing_and_extra_each_top_field_rejected(self):
        for case in CASES:
            value = case["expectedProjection"]
            for key in value:
                bad = copy.deepcopy(value)
                del bad[key]
                self.assertFalse(matches(case, bad, SCHEMA))
            bad = copy.deepcopy(value)
            bad["exceptionText"] = "/private/path raw exception secret"
            self.assertFalse(validate(bad, SCHEMA))

    def test_every_nonempty_sequence_tail_is_observable(self):
        count = 0
        def paths(value, path=()):
            if isinstance(value, list):
                if value:
                    yield path
                for i, child in enumerate(value):
                    yield from paths(child, path + (i,))
            elif isinstance(value, dict):
                for key, child in value.items():
                    yield from paths(child, path + (key,))
        for case in CASES:
            for path in paths(case["expectedProjection"]):
                bad = copy.deepcopy(case["expectedProjection"])
                cursor = bad
                for item in path:
                    cursor = cursor[item]
                cursor.pop()
                self.assertFalse(matches(case, bad, SCHEMA))
                count += 1
        self.assertGreater(count, 200)

    def test_complete_five_fields_and_basis_tail(self):
        case = BY_ID["rdfs/domain-depth2"]
        for name in ["rdfs", "rules", "warnings", "rdfsEvidence", "evidence"]:
            bad = copy.deepcopy(case["expectedProjection"])
            del bad["value"][name]
            self.assertFalse(validate(bad, SCHEMA))
        bad = copy.deepcopy(case["expectedProjection"])
        bad["value"]["rdfsEvidence"][-1]["basis"].pop()
        self.assertFalse(matches(case, bad, SCHEMA))

    def test_when_reorder_changes_value(self):
        case = BY_ID["legacy/multiple-matches"]
        bad = copy.deepcopy(case["expectedProjection"])
        bad["value"]["evidence"][0]["inputs"].reverse()
        self.assertTrue(validate(bad, SCHEMA))
        self.assertFalse(matches(case, bad, SCHEMA))

    def test_exact_warning_and_unbound_case(self):
        value = BY_ID["legacy/no-rule-feedback"]["expectedProjection"]["value"]
        self.assertEqual(value["warnings"], ["RULE_CHAIN_UNSUPPORTED:R-next"])
        rejected = BY_ID["legacy/unbound-head"]["expectedProjection"]
        self.assertEqual(rejected["diagnostic"]["reason"], "UNBOUND_RULE_VARIABLE")

    def test_scope_sources_and_four_fields(self):
        a = BY_ID["scope/asserted"]["expectedProjection"]["value"]
        f = BY_ID["scope/fresh"]["expectedProjection"]["value"]
        p = BY_ID["scope/project"]["expectedProjection"]["value"]
        self.assertEqual(set(f), {"facts", "ontology", "reasoning_result", "provenance"})
        self.assertEqual((len(a["facts"]), len(a["ontology"])), (6, 2))
        self.assertEqual((len(f["facts"]), len(f["ontology"])), (9, 3))
        self.assertIsNone(a["reasoning_result"])
        self.assertIsNone(a["provenance"]["reasoningSource"])
        self.assertEqual(f, p)  # Value relation only; never same-issue authority proof.
        self.assertEqual(len(f["provenance"]["selectedFacts"]), 9)
        self.assertEqual(len(f["provenance"]["derivedAxioms"]), 1)

    def test_scope_shacl_null_and_multiplicity(self):
        report = BY_ID["scope/fresh"]["expectedProjection"]["shacl"]
        self.assertFalse(report["conforms"])
        self.assertEqual(len(report["violations"]), 2)
        self.assertTrue(all(row["value"] is None for row in report["violations"]))
        bad = copy.deepcopy(BY_ID["scope/fresh"]["expectedProjection"])
        del bad["shacl"]["violations"][0]["value"]
        self.assertFalse(validate(bad, SCHEMA))

    def test_bool_not_integer_and_no_untrusted_diagnostic(self):
        original = BY_ID["restore/fullview/payload-unknown-key"]["expectedProjection"]
        for key, value in [("slot", True), ("reason", "/tmp/raw-error"),
                           ("stage", "raw/secret/path"), ("domain", "any"),
                           ("location", {"path": "/secret"}), ("ruleId", "untrusted")]:
            bad = copy.deepcopy(original)
            bad["diagnostic"][key] = value
            self.assertFalse(validate(bad, SCHEMA))
            projected = safe_projection(bad["diagnostic"], "restore", SCHEMA)
            self.assertEqual(projected, unknown("restore"))
            self.assertNotIn("private/path", json.dumps(projected))
        bad = copy.deepcopy(original)
        bad["diagnostic"]["message"] = "raw loader text"
        self.assertFalse(validate(bad, SCHEMA))

    def test_unknown_is_fixed_safe_incomplete(self):
        value = unknown("restore")
        self.assertFalse(value["complete"])
        self.assertEqual(value["diagnostic"], {"origin": "Unknown", "reason": "INTERNAL_ERROR",
                                             "classification": None, "stage": None,
                                             "slot": None, "domain": None,
                                             "ruleId": None, "location": None})
        self.assertTrue(validate(value, SCHEMA))
        self.assertFalse(any(matches(case, value, SCHEMA) for case in CASES))
        value["complete"] = True
        self.assertFalse(validate(value, SCHEMA))
        direct = rejection("DirectStepsFailure", "DIRECT_STEPS_INVALID",
                           "structured-material-required", "resource", "entry")
        self.assertFalse(validate(direct, SCHEMA))

    def test_strict_json_duplicate_and_nonfinite(self):
        for value in ['{"reason": "x", "reason": "y"}', '{"a":NaN}', '{"a":Infinity}']:
            with self.assertRaises(ValueError):
                strict_json(value)

    def test_lexical_type_language_and_escape_preserved(self):
        def literal(s, datatype="http://www.w3.org/2001/XMLSchema#integer", lang=None):
            return {"kind": "literal", "lexical": s, "datatype": datatype, "language": lang}
        self.assertNotEqual(n3(literal("01")), n3(literal("1")))
        self.assertNotEqual(n3(literal("1")), n3(literal("1", "http://www.w3.org/2001/XMLSchema#int")))
        self.assertEqual(n3(literal('尾\n"\\', "http://www.w3.org/2001/XMLSchema#string")),
                         '"尾\\n\\"\\\\"')
        self.assertEqual(n3(literal("hello", "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString", "EN")),
                         '"hello"@EN')
        self.assertFalse(exact([1], [True]))
        self.assertNotEqual(digest({"a": None}), digest({"a": ""}))

    def test_global_blank_node_bijection_and_tail(self):
        iri = lambda s: {"kind": "iri", "value": s}
        blank = lambda s: {"kind": "blank", "label": s}
        left = [[blank("a"), iri("urn:first"), iri("urn:x")],
                [blank("a"), iri("urn:rest"), blank("b")],
                [blank("b"), iri("urn:first"), iri("urn:y")],
                [blank("b"), iri("urn:rest"), iri("urn:nil")]]
        right = [[blank("p"), row[1], blank("q") if row[2] == blank("b") else row[2]]
                 if row[0] == blank("a") else [blank("q"), row[1], row[2]] for row in left]
        self.assertTrue(graph_isomorphic(left, right))
        self.assertFalse(graph_isomorphic(left, right[:-1]))
        collapsed = copy.deepcopy(right)
        collapsed[-1][0] = blank("p")
        self.assertFalse(graph_isomorphic(left, collapsed))


if __name__ == "__main__":
    unittest.main(verbosity=2)
