"""R3 canonical-wire counterexamples plus unchanged original 32-method regression.

Only detached serializer examples and fixed documentation identities. No product
objects, RDF libraries, parser execution, capture, allocation or actual observations.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("frozen_r2_tests", HERE / "selftest-r2.py")
r2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r2)
DesignTests = r2.DesignTests
R2DeltaTests = r2.R2DeltaTests
BY_ID, CASES, SCHEMA, m = r2.BY_ID, r2.CASES, r2.SCHEMA, r2.m


def legacy_projection(graph):
    return {"kind": "legacy", "complete": True, "value": {
        "rdfs": [], "rules": graph, "warnings": [], "rdfsEvidence": [], "evidence": []}}


def path_value(value, path):
    for part in path:
        value = value[part]
    return value


class R3WireGateTests(unittest.TestCase):
    def test_all_37_expected_have_all_85_canonical_graph_slots(self):
        count = 0
        for case in CASES:
            value = case["expectedProjection"]
            layout = m.projection_layout(value)
            self.assertTrue(m.validate(value, SCHEMA))
            self.assertTrue(m.canonical_graph_slots(value, layout))
            self.assertTrue(m.matches(case, copy.deepcopy(value), SCHEMA))
            for path, mode in layout:
                if mode in ("typed-graph", "n3-graph"):
                    self.assertTrue(m.canonical_graph_wire(path_value(value, path), mode))
                    count += 1
        self.assertEqual(count, 85)

    def test_three_fixed_id_reversals_rejected_on_each_side(self):
        vectors = [("rdfs/cycle", ("value", "rdfs"), 8),
                   ("rdfs/domain-depth2", ("value", "rdfsEvidence", 1, "basis"), 3),
                   ("scope/fresh", ("value", "facts"), 9)]
        for case_id, path, length in vectors:
            case = BY_ID[case_id]
            original = case["expectedProjection"]
            bad = copy.deepcopy(original)
            self.assertEqual(len(path_value(bad, path)), length)
            path_value(bad, path).reverse()
            frozen = copy.deepcopy(bad)
            self.assertTrue(m.validate(bad, SCHEMA))
            self.assertTrue(m.projection_identity_equal(original, bad))  # identity alone is insufficient
            self.assertFalse(m.matches(case, bad, SCHEMA))
            self.assertFalse(m.matches({"expectedProjection": bad}, original, SCHEMA))
            self.assertEqual(bad, frozen)  # rejection never repairs/reorders input

    def test_exact_json_duplicates_remain_blocked_by_schema(self):
        vectors = [("rdfs/cycle", ("value", "rdfs")),
                   ("legacy/repeated-variable", ("value", "rules")),
                   ("scope/fresh", ("value", "facts")),
                   ("rdfs/domain-depth2", ("value", "rdfsEvidence", 1, "basis"))]
        for case_id, path in vectors:
            case = BY_ID[case_id]
            bad = copy.deepcopy(case["expectedProjection"])
            rows = path_value(bad, path)
            rows.insert(0, copy.deepcopy(rows[0]))
            self.assertFalse(m.validate(bad, SCHEMA))
            self.assertFalse(m.matches(case, bad, SCHEMA))

    def test_locally_sorted_n3_language_alias_duplicates_rejected_both_sides(self):
        expected = legacy_projection([["<urn:x>", "<urn:p>", '"hello"@en']])
        bad = copy.deepcopy(expected)
        bad["value"]["rules"] = [["<urn:x>", "<urn:p>", '"hello"@EN'],
                                   ["<urn:x>", "<urn:p>", '"hello"@en']]
        self.assertEqual(bad["value"]["rules"], sorted(bad["value"]["rules"]))
        self.assertTrue(m.validate(bad, SCHEMA))
        self.assertTrue(m.matches({"expectedProjection": expected}, expected, SCHEMA))
        self.assertFalse(m.canonical_graph_wire(bad["value"]["rules"], "n3-graph"))
        self.assertFalse(m.matches({"expectedProjection": expected}, bad, SCHEMA))
        self.assertFalse(m.matches({"expectedProjection": bad}, expected, SCHEMA))
        # A single EN spelling is allowed; only language identity changes.
        single = copy.deepcopy(expected)
        single["value"]["rules"][0][2] = '"hello"@EN'
        self.assertTrue(m.matches({"expectedProjection": expected}, single, SCHEMA))

    def test_locally_sorted_typed_language_alias_duplicates_rejected_both_sides(self):
        expected = copy.deepcopy(BY_ID["scope/asserted"]["expectedProjection"])
        row = [r2.iri("urn:x"), r2.iri("urn:p"), r2.literal("hello", language="en")]
        expected["value"]["facts"] = [row]
        bad = copy.deepcopy(expected)
        alias = copy.deepcopy(row)
        alias[2]["language"] = "EN"
        bad["value"]["facts"] = [alias, row]
        keys = [tuple(m.n3(t) for t in t3) for t3 in bad["value"]["facts"]]
        self.assertEqual(keys, sorted(keys))
        self.assertTrue(m.validate(bad, SCHEMA))
        self.assertTrue(m.matches({"expectedProjection": expected}, expected, SCHEMA))
        self.assertFalse(m.canonical_graph_wire(bad["value"]["facts"], "typed-graph"))
        self.assertFalse(m.matches({"expectedProjection": expected}, bad, SCHEMA))
        self.assertFalse(m.matches({"expectedProjection": bad}, expected, SCHEMA))

    def test_each_end_canonical_crossing_bnode_rename_is_accepted(self):
        # Handwritten independent literal positive: mapping a->q, b->p crosses
        # row indexes, while each ORIGINAL wire is in its own N3 ascending order.
        left = legacy_projection([["_:a", "<urn:p>", "<urn:x>"],
                                  ["_:b", "<urn:p>", "<urn:y>"]])
        right = legacy_projection([["_:p", "<urn:p>", "<urn:y>"],
                                   ["_:q", "<urn:p>", "<urn:x>"]])
        self.assertFalse(m.exact(left, right))
        self.assertTrue(m.canonical_graph_slots(left, m.projection_layout(left)))
        self.assertTrue(m.canonical_graph_slots(right, m.projection_layout(right)))
        self.assertTrue(m.matches({"expectedProjection": left}, right, SCHEMA))
        self.assertTrue(m.matches({"expectedProjection": right}, left, SCHEMA))
        typed_left = copy.deepcopy(BY_ID["scope/asserted"]["expectedProjection"])
        typed_right = copy.deepcopy(typed_left)
        typed_left["value"]["facts"] = [[r2.blank("a"), r2.iri("urn:p"), r2.iri("urn:x")],
                                           [r2.blank("b"), r2.iri("urn:p"), r2.iri("urn:y")]]
        typed_right["value"]["facts"] = [[r2.blank("p"), r2.iri("urn:p"), r2.iri("urn:y")],
                                            [r2.blank("q"), r2.iri("urn:p"), r2.iri("urn:x")]]
        self.assertTrue(m.matches({"expectedProjection": typed_left}, typed_right, SCHEMA))
        unsorted = copy.deepcopy(right)
        unsorted["value"]["rules"].reverse()
        self.assertTrue(m.projection_identity_equal(left, unsorted))
        self.assertFalse(m.matches({"expectedProjection": left}, unsorted, SCHEMA))

    def test_ordered_occurrence_duplicates_and_tail_are_not_graph_normalized(self):
        t = ["<urn:x>", "<urn:p>", "<urn:y>"]
        expected = legacy_projection([t])
        record = {"rule": "r", "result": t, "inputs": [t, t], "basis": [t]}
        expected["value"]["evidence"] = [record, copy.deepcopy(record)]
        self.assertTrue(m.matches({"expectedProjection": expected}, copy.deepcopy(expected), SCHEMA))
        for path in [("value", "evidence"), ("value", "evidence", 0, "inputs")]:
            bad = copy.deepcopy(expected)
            path_value(bad, path).pop()
            self.assertTrue(m.validate(bad, SCHEMA))
            self.assertFalse(m.matches({"expectedProjection": expected}, bad, SCHEMA))

    def test_generated_term_spelling_numeric_and_quoted_lexical_remain_exact(self):
        for token in ['"word@EN"', '"01"^^<' + r2.XSD + 'integer>']:
            expected = legacy_projection([["<urn:x>", "<urn:p>", token]])
            self.assertTrue(m.matches({"expectedProjection": expected}, expected, SCHEMA))
            bad = copy.deepcopy(expected)
            bad["value"]["rules"][0][2] = token.replace("@EN", "@en").replace('"01"', '"1"')
            self.assertFalse(m.matches({"expectedProjection": expected}, bad, SCHEMA))
        for token in ['"\\u0068ello"', '"hello"^^<' + r2.XSD + 'string>',
                      '<relative>', '<urn:bad iri>', '"hello"@', '_:bad label']:
            self.assertFalse(m.canonical_graph_wire([["<urn:x>", "<urn:p>", token]], "n3-graph"))
        malformed = [r2.iri("urn:x"), r2.literal("p", r2.XSD + "string", None), r2.iri("urn:y")]
        self.assertFalse(m.canonical_graph_wire([malformed], "typed-graph"))

    def test_schema_allowed_noncanonical_or_illegal_spellings_fail_each_wire(self):
        expected = legacy_projection([["<urn:x>", "<urn:p>", '"hello"']])
        # These strings are JSON-schema-valid cells. They are not the generated
        # N3 spelling defined by this serializer. No Turtle/RDF library is used.
        tokens = ['"hello"^^<' + r2.XSD + 'string>', '"\\u0068ello"',
                  '"bad\nline"', '"bad\tline"', '<urn:bad|value>']
        for token in tokens:
            bad = legacy_projection([["<urn:x>", "<urn:p>", token]])
            self.assertTrue(m.validate(bad, SCHEMA))
            self.assertFalse(m.canonical_graph_wire(bad["value"]["rules"], "n3-graph"))
            self.assertFalse(m.matches({"expectedProjection": expected}, bad, SCHEMA))
            self.assertFalse(m.matches({"expectedProjection": bad}, expected, SCHEMA))
        typed = copy.deepcopy(BY_ID["scope/asserted"]["expectedProjection"])
        typed["value"]["facts"] = [[r2.iri("urn:bad|value"), r2.iri("urn:p"), r2.iri("urn:y")]]
        self.assertTrue(m.validate(typed, SCHEMA))
        self.assertFalse(m.matches({"expectedProjection": typed}, typed, SCHEMA))


if __name__ == "__main__":
    unittest.main(verbosity=2)
