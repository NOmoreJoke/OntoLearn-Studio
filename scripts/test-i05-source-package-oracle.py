#!/usr/bin/env python3
"""Stdlib tests of this independent oracle, never the product or future collector."""
from __future__ import annotations

import ast
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BUILDER = Path(__file__).with_name('build-i05-source-package-oracle.py')
SPEC = importlib.util.spec_from_file_location('t05_own_oracle', BUILDER)
oracle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(oracle)


class OracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = oracle.construct()
        cls.data = cls.artifacts['oracle.json']
        cls.entries = {e['id']: e for e in cls.data['observations']}
        cls.input = oracle.read_pinned(oracle.ASSET)
        cls.manifest = oracle.read_pinned(oracle.DESCRIPTOR)

    def expected(self, key):
        return self.entries[key]['expected']

    def test_417_exact_order_and_three_case_sets(self):
        self.assertTrue(oracle.validate_oracle(self.data, self.input, self.manifest))
        self.assertEqual([e['id'] for e in self.data['observations']], [e['id'] for e in self.input['observations']])
        self.assertEqual(self.data['caseSets'], self.manifest['caseSets'])
        for name, selected in self.manifest['caseSets'].items():
            self.assertEqual([self.entries[i]['caseSets'][name] for i in selected], list(range(len(selected))))

    def test_missing_tail_or_added_id_rejected(self):
        for mutate in (lambda d: d['observations'].pop(), lambda d: d['observations'].append(copy.deepcopy(d['observations'][0]))):
            d = copy.deepcopy(self.data)
            mutate(d)
            with self.assertRaises(ValueError):
                oracle.validate_oracle(d, self.input, self.manifest)

    def test_nonfinite_and_duplicate_json_rejected(self):
        for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}']:
            with self.assertRaises(ValueError):
                oracle.strict_json(raw)

    def test_surrogate_is_preserved_not_crashed_or_replaced(self):
        raw = oracle.canonical({'bad': '\ud800'})
        self.assertEqual(json.loads(raw)['bad'], '\ud800')
        self.assertEqual(self.expected('utc-date/surrogate-data')['reason'], 'INVALID_UNICODE')
        self.assertEqual(self.expected('utc-date/surrogate-data')['validatorCalls'], 0)

    def test_hash_change_rejected_before_interpretation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / oracle.ASSET
            path.write_bytes(b'{}')
            with patch.object(oracle, 'INPUTS', Path(directory)):
                with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                    oracle.read_pinned(oracle.ASSET)

    def test_no_product_third_party_network_or_process_imports(self):
        allowed = {'__future__', 'argparse', 'copy', 'hashlib', 'json', 're', 'collections', 'datetime', 'decimal', 'pathlib'}
        for node in ast.walk(ast.parse(BUILDER.read_text())):
            if isinstance(node, ast.Import):
                self.assertTrue(all(alias.name.split('.')[0] in allowed for alias in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertIn(node.module.split('.')[0], allowed)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, ('eval', 'exec', '__import__'))

    def test_reproducible_build_exact_full_artifacts(self):
        again = oracle.construct()
        for name in self.artifacts:
            self.assertEqual(oracle.canonical(self.artifacts[name]), oracle.canonical(again[name]))

    def test_integer_spelling_never_numeric_deduplicated(self):
        graph = self.expected('turtle/integer-distinct')['graph']
        self.assertEqual({t[2]['lexical'] for t in graph}, {'01', '1'})
        self.assertEqual(len(graph), 2)
        model = copy.deepcopy(graph)
        model[0][2]['lexical'] = model[1][2]['lexical']
        with self.assertRaises(ValueError):
            oracle.assert_exact_model(graph, model)

    def test_numeric_turtle_preserves_every_original_lexical(self):
        pairs = [('01', '1'), ('+01', '+1'), ('-01', '-1'), ('-00', '0'),
                 ('01.00', '1.0'), ('+01.00', '+1.0'), ('-01.00', '-1.0'),
                 ('01e+00', '1e+00'), ('+01e+00', '+1e+00'), ('-01e+00', '-1e+00')]
        for i, expected in enumerate(pairs):
            graph = self.expected('turtle/numeric-lexical-' + str(i))['graph']
            self.assertEqual({t[2]['lexical'] for t in graph}, set(expected))

    def test_rdf11_strings_and_language_identity_without_losing_source(self):
        for i in range(5):
            graph = self.expected('turtle/string-identity-' + str(i))['graph']
            self.assertEqual(len(graph), 1)
            self.assertEqual(graph[0][2]['datatype'], oracle.XSD + 'string')
        self.assertEqual(len(self.expected('turtle/lang-case')['graph']), 1)
        self.assertEqual(self.expected('turtle/lang-case')['graph'][0][2]['language'], 'en-us')
        raw = self.input['datasets']['turtle/lang-case']['text']
        self.assertIn('@EN-us', raw)
        self.assertIn('@en-US', raw)

    def test_query_complete_bindings_unbound_and_order(self):
        q = self.expected('query/optional-unbound')['query']
        self.assertEqual(q['variables'], ['s', 'missing'])
        self.assertEqual([r[0]['value'] for r in q['rows']], ['urn:case:0:equipment/' + x for x in ('001', '002', '003')])
        self.assertEqual([r[1] for r in q['rows']], [None] * 3)
        changed = copy.deepcopy(q)
        changed['rows'][-1][1] = oracle.literal('')
        with self.assertRaises(ValueError):
            oracle.assert_exact_model(q, changed)
        self.assertEqual(self.expected('C-query-type-error')['query']['rows'], [])
        self.assertEqual(self.expected('C-query-numeric-promotion')['query']['rows'], [[oracle.iri('urn:m1:s')]])

    def test_original_query_is_alarm_only_not_equipment_column(self):
        q = self.expected('original-Q01')['query']
        self.assertEqual(q, {'type': 'SELECT', 'variables': ['alarm'], 'rows': [[oracle.iri('urn:ontolearn:learning:alarm/A01')]]})
        self.assertEqual(self.expected('original-Q02')['query']['rows'], [])

    def test_shacl_aggregate_absent_value_is_not_fabricated(self):
        report = self.expected('shape/template-maximum')['report']
        self.assertFalse(report['conforms'])
        row, = report['violations']
        self.assertIsNone(row['value'])
        self.assertEqual(row['constraint'], oracle.iri(oracle.SH + 'MaxCountConstraintComponent'))
        self.assertEqual(set(row), {'focus', 'path', 'value', 'sourceShape', 'constraint', 'severity'})
        changed = copy.deepcopy(report)
        changed['violations'][0]['value'] = oracle.literal('a')
        with self.assertRaises(ValueError):
            oracle.assert_exact_model(report, changed)

    def test_date_equal_before_offset_policies(self):
        equal = self.expected('C-inclusive-date-entry/strict/utc-date-range-v1')
        self.assertEqual(equal['report'], {'conforms': True, 'violations': []})
        self.assertEqual(equal['entryVersion'], 'i05-shacl-text-2')
        before = self.expected('utc-date/C-before')['report']
        row, = before['violations']
        self.assertEqual(row['value'], oracle.literal('1999-12-31Z', oracle.XSD + 'date'))
        self.assertEqual(row['constraint'], oracle.iri(oracle.SH + 'MinInclusiveConstraintComponent'))
        offset = self.expected('utc-date/C-offset')
        self.assertEqual((offset['reason'], offset['validatorCalls'], offset['report']), ('RDF_TERM_INVALID', 0, None))
        self.assertEqual(self.expected('utc-date/minExclusive')['reason'], 'UNSUPPORTED_SHACL')

    def test_date_reversed_has_both_complete_violations(self):
        report = self.expected('utc-date/reversed')['report']
        self.assertFalse(report['conforms'])
        self.assertEqual({r['constraint']['value'] for r in report['violations']}, {oracle.SH + n + 'ConstraintComponent' for n in ('MinInclusive', 'MaxInclusive')})
        self.assertEqual(len(report['violations']), 2)

    def test_bad_integer_strict_and_explicit_report_are_distinct(self):
        self.assertEqual(self.expected('C-illtyped-entry/strict')['reason'], 'INVALID_LITERAL_LEXICAL')
        wide = self.expected('C-illtyped-entry/integer-illtyped-report-v1')
        self.assertFalse(wide['report']['conforms'])
        self.assertEqual(wide['report']['violations'][0]['value']['lexical'], 'not-an-int')
        self.assertTrue(self.expected('integer/lexical-5/strict')['report']['conforms'])

    def test_date_exact_public_budget_and_three_orders(self):
        exact = self.expected('utc-date/public-budget-43460')
        self.assertEqual((exact['work']['consumed'], exact['work']['remaining']), (1000000, 0))
        self.assertEqual(exact['validatorCalls'], 1)
        over = self.expected('utc-date/public-budget-43461')
        self.assertEqual((over['reason'], over['validatorCalls']), ('GRAPH_INPUT_LIMIT', 0))
        self.assertEqual(over['work']['uncappedRequired'], 1000023)
        for p, consumed, code in [('p0', 366042, 'RDF_TERM_INVALID'), ('p99', 1000000, 'GRAPH_INPUT_LIMIT')]:
            all_results = [self.expected('utc-date/D1-' + p + '/' + order) for order in ('forward', 'reverse', 'rotate')]
            self.assertEqual([r['work']['consumed'] for r in all_results], [consumed] * 3)
            self.assertEqual([r['reason'] for r in all_results], [code] * 3)

    def test_hand_selected_multihead_and_disabled_not_same_rule_id_as_case(self):
        multi = self.expected('profile-83/extension:MULTI-OUTPUT-ONE-FIRING')['conditionalBusinessExpected']
        self.assertEqual([r['ruleId'] for r in multi['matches']], ['R-risk-multi'])
        self.assertEqual([h['headIndex'] for h in multi['matches'][0]['heads']], [0, 1])
        disabled = self.expected('profile-83/extension:DISABLED-RULE-NO-OUTPUT')['conditionalBusinessExpected']
        self.assertEqual(disabled['matches'], [])
        self.assertEqual(disabled['customOutput'], [])

    def test_false_comparisons_keep_binding_not_persistent_false_evidence(self):
        math = self.expected('profile-83/extension:CMP-EQ-FALSE')['conditionalBusinessExpected']
        self.assertEqual(math['customOutput'], [])
        match, = math['matches']
        self.assertFalse(match['accepted'])
        self.assertFalse(match['typedComparisons'][0]['result'])
        self.assertEqual(match['typedComparisons'][0]['left']['value']['denominator'], 1)

    def test_repair_and_fragments_never_promote_full_original_operation(self):
        self.assertEqual(self.expected('profile-83/transfer:repair')['semanticState'], 'not-executed')
        for number in range(1, 5):
            e = self.expected('profile-83/E.5:event-fragment:round:' + str(number))['conditionalBusinessExpected']
            self.assertTrue(e['fragmentOnly'])
            self.assertEqual(len(e['matches']), 4 * number)
        for category, count in [('originalOperations', 106), ('learningChecks', 54), ('productCases', 50)]:
            rows = self.data['contextLedger'][category]
            self.assertEqual(len(rows), count)
            self.assertEqual({r['state'] for r in rows}, {'not-executed'})
        self.assertTrue(all('originalOperationText' in r for r in self.data['contextLedger']['originalOperations']))

    def test_scope_branches_consume_different_complete_fact_sets(self):
        asserted, fresh, project = [self.expected('scope/' + k) for k in ('asserted', 'fresh', 'project')]
        self.assertEqual([len(v['facts']) for v in (asserted, fresh, project)], [6, 9, 9])
        self.assertEqual(len(fresh['derivedAxioms']), 1)
        self.assertNotIn(fresh['derivedAxioms'][0], fresh['facts'])
        self.assertTrue(asserted['shacl']['conforms'])
        self.assertEqual(len(fresh['shacl']['violations']), 2)
        self.assertEqual(project['reasonCallsByStage']['project'], 0)

    def test_finite_rdfs_does_not_refeed_custom_rules(self):
        math = self.expected('legacy/no-rule-feedback')['math']
        self.assertEqual(len(math['customOutput']), 1)
        self.assertEqual(math['customOutput'][0][2], oracle.iri('urn:ontolearn:HighRiskEquipment'))
        self.assertFalse(any(t[2] == oracle.iri('urn:ontolearn:NeedsInspection') for t in math['customOutput']))
        repeated = self.expected('legacy/repeated-variable')['math']['matches']
        self.assertEqual(len(repeated), 1)
        self.assertEqual(repeated[0]['bindings'], {'?s': oracle.iri('urn:c')})

    def test_ordered_direct_depth_and_occurrence_roots(self):
        math = self.expected('dag/domain-depth2')['businessMath']
        self.assertEqual([s['depth'] for s in math['selectedDirectSteps']], [1, 2])
        self.assertEqual(math['selectedDirectSteps'][1]['premises'][0], {'kind': 'step', 'ordinal': 0})
        two = self.expected('dag/two-head-occurrences')['businessMath']
        self.assertEqual(len(two['rootOccurrences']), 4)
        self.assertEqual([r['ref']['headIndex'] for r in two['rootOccurrences']], [0, 1, 0, 1])

    def test_raw_aliases_keep_all24_occurrences_and_six_identities(self):
        math = self.expected('fullview/raw-aliases')['businessMath']
        self.assertEqual(len(math['inputGraph']), 6)
        self.assertEqual(sum(map(len, math['rawTermSourceOccurrences'])), 24)
        self.assertEqual(len(math['selectedDirectSteps']), 0)

    def test_restore_mutations_are_A1_not_rebound_deep_dag_coverage(self):
        entries = [e for e in self.data['observations'] if e['operation'] == 'restore-negative']
        self.assertEqual(len({e['parameters']['mutation'] for e in entries}), 9)
        for e in entries:
            r = e['expected']
            self.assertEqual(r['failureStage'], 'A1')
            self.assertIsNone(r['partialView'])
            self.assertTrue(r['noDeepRevalidationClaim'])
            self.assertEqual(r['restoreReasonCalls'], 0)

    def test_b1_four_ontology_is_not_ten_suite_or_snapshot_measurement(self):
        for scale in (1, 10):
            e = self.expected('b1-semantic/' + str(scale) + 'x')
            self.assertEqual(len(e['assertedOriginal']), 18 * scale)
            self.assertEqual(len(e['ontology']), 4)
            self.assertEqual(len(e['mergedInput']), 18 * scale + 4)
            self.assertEqual(len(e['rdfsAdded']), 8 * scale + 1)
            self.assertEqual(len(e['matches']), scale)
            self.assertTrue(all(len(m['leafBasis']) == 6 for m in e['matches']))
            self.assertEqual(e['snapshotLoad']['state'], 'not-executed')
            self.assertFalse(e['instrumentation'])

    def test_pending_not_hidden_or_counted_complete(self):
        self.assertFalse(self.data['wholeOracleComplete'])
        self.assertEqual(self.entries['shape/front-2']['oracleStatus'], 'pending')
        self.assertEqual(self.entries['profile-83/baseline:G-base']['oracleStatus'], 'pending')
        d = copy.deepcopy(self.data)
        d['wholeOracleComplete'] = True
        with self.assertRaises(ValueError):
            oracle.validate_oracle(d, self.input, self.manifest)
        d = copy.deepcopy(self.data)
        next(e for e in d['observations'] if e['pendingFields'])['oracleStatus'] = 'specified'
        with self.assertRaises(ValueError):
            oracle.validate_oracle(d, self.input, self.manifest)

    def test_model_type_field_and_full_tail_mutations_are_rejected(self):
        model = {'integer': 1, 'allRows': [1, 2, 3], 'source': {'raw': None, 'empty': ''}}
        for change in ({'integer': True, 'allRows': [1, 2, 3], 'source': model['source']},
                       {'integer': 1, 'allRows': [1, 2], 'source': model['source']},
                       {'integer': 1, 'allRows': [1, 2, 3], 'source': {'raw': '', 'empty': ''}},
                       {**model, 'ignoredUnknown': None}):
            with self.assertRaises(ValueError):
                oracle.assert_exact_model(model, change)

    def test_dynamic_relations_reject_bad_received_digest_and_tail(self):
        payload = b'{"all":true}'
        held = {'payload_sha256': oracle.digest(payload)}
        model = {'wire': {'payload_json': payload, 'rows': ['{"all":', 'true}']}, 'held': held}
        sha = next(r for r in oracle.RELATIONS if r['id'] == 'received-payload-sha')
        tail = next(r for r in oracle.RELATIONS if r['id'] == 'rows-no-truncated-tail')
        self.assertTrue(oracle.evaluate_relation(sha, model))
        self.assertTrue(oracle.evaluate_relation(tail, model))
        model['wire']['payload_json'] = b'{"all":false}'
        with self.assertRaises(ValueError):
            oracle.evaluate_relation(sha, model)
        model['wire']['payload_json'] = payload
        model['wire']['rows'].pop()
        with self.assertRaises(ValueError):
            oracle.evaluate_relation(tail, model)

    def test_allocation_identity_is_not_value_equal_json(self):
        class Issued:
            def __eq__(self, other):
                return type(other) is Issued
        actual = Issued()
        rule = next(r for r in oracle.RELATIONS if r['id'] == 'allocation-same-issuance')
        model = {'issued': {'allocation': actual}, 'used': {'allocation': actual}}
        self.assertTrue(oracle.evaluate_relation(rule, model))
        model['used']['allocation'] = copy.deepcopy(actual)
        with self.assertRaises(ValueError):
            oracle.evaluate_relation(rule, model)
        for value in (None, {'claimedAllocation': True}, 'allocation-id'):
            model = {'issued': {'allocation': value}, 'used': {'allocation': value}}
            with self.assertRaises(ValueError):
                oracle.evaluate_relation(rule, model)

    def test_stable_first_witness_is_ordered_by_approved_pair_key(self):
        first = self.expected('dag/first-witness')['businessMath']['selectedDirectSteps']
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]['orderedDirectInputTriples'][0][2], oracle.iri('urn:A'))
        cross = self.expected('dag/cross-rule-witness')['businessMath']['selectedDirectSteps']
        self.assertEqual(cross[0]['rule'], 'rdfs2')
        self.assertEqual(cross[0]['orderedDirectInputTriples'][0][0], oracle.iri('urn:a'))

    def test_pre_registered_date_regression_has_separate_authority_level(self):
        for number in (7, 8, 9, 10, 15, 16):
            for side in ('bound', 'value'):
                entry = self.entries['utc-date/lexical-' + str(number) + '/' + side]
                expected = entry['expected']
                self.assertEqual(entry['oracleStatus'], 'specified')
                self.assertEqual(expected['reason'], 'INVALID_LITERAL_LEXICAL' if number <= 10 else
                                 'INVALID_SHAPE' if side == 'bound' else 'RDF_TERM_INVALID')
                self.assertFalse(expected['declaredRegressionAuthority']['independentLibraryClassificationProven'])
                self.assertEqual(expected['declaredRegressionAuthority']['sourceType'], 'pre-registered legacy regression assertion')

    def test_literal_only_native_schema_reference_closes_exact_key_names(self):
        fields = self.artifacts['schema.json']['exactIssuedRecordKeys']
        self.assertEqual(len(fields['_PAYLOAD']), 7)
        self.assertEqual(len(fields['_REASONING']), 15)
        self.assertEqual(len(fields['_CHILD']), 11)
        self.assertIn('graphBudget', fields['_REASONING'])
        self.assertTrue({'planDigest', 'budgetUsage'}.issubset(fields['_CHILD']))

    def test_versions_are_exact_approved_format_tags_not_invented_profile_names(self):
        versions = self.data['dynamicRules']['versions']
        self.assertEqual(versions['fullview']['payloadFormat'], 'i05-reasoning-result/2')
        self.assertEqual(versions['explanation']['payloadFormat'], 'i05-reasoning-result/3')
        self.assertEqual(versions['fullview']['executionSemanticsVersion'], 'i05-finite-7')
        self.assertEqual(versions['explanation']['executionSemanticsVersion'], 'i05-finite-8')

    def test_each_expected_has_distinct_precise_authority_from_input_refs(self):
        for e in self.data['observations']:
            self.assertTrue(e['sourceRefs'])
            self.assertTrue(e['expectedSourceRefs'])
            self.assertTrue(all('type' in r and 'local' in r and ('pointer' in r or 'pointers' in r) for r in e['expectedSourceRefs']))
        e = self.entries['profile-83/extension:MULTI-OUTPUT-ONE-FIRING']
        self.assertTrue(any('/matches' in r.get('pointers', []) for r in e['expectedSourceRefs']))

    def test_budget_gaps_pin_each_operation_and_leave_allocation_unknown(self):
        gaps = self.artifacts['budget-gaps.json']['items']
        self.assertEqual(len(gaps), 82)
        self.assertEqual({g['id'] for g in gaps}, {e['id'] for e in self.data['observations'] if e['operation'] == 'profile' and e['expected']['semanticState'] != 'not-executed'})
        for gap in gaps:
            self.assertEqual(gap['entry'], 'execute_profile_records')
            self.assertIsNone(gap['allocationRequired']['value'])
            self.assertEqual(len(gap['missingInvoiceOperations']), 5)
            self.assertTrue(all('missingFormula' in item and 'knownRule' in item for item in gap['missingInvoiceOperations']))
            self.assertTrue(gap['firstErrorEntry']['missingDecision'])

    def test_original_C_full_fields_stay_consistent_with_independent_golden(self):
        golden = oracle.read_pinned('consumer-C-goldens.json')['cases']
        mapping = {'focusNode': 'focus', 'resultPath': 'path', 'value': 'value',
                   'sourceShape': 'sourceShape', 'sourceConstraintComponent': 'constraint',
                   'resultSeverity': 'severity'}
        for row in golden[2:11]:
            report = self.expected(row['id'])['report']
            expected = row['expected']
            self.assertEqual(report['conforms'], expected['conforms'])
            if 'requiredResultRows' in expected:
                rows = [{key: None if value.get(name) is None else oracle.n3_term(value[name])
                         for name, key in mapping.items()} for value in expected['requiredResultRows']]
                self.assertEqual(sorted(report['violations'], key=oracle.canonical), sorted(rows, key=oracle.canonical))


if __name__ == '__main__':
    unittest.main(verbosity=2)
