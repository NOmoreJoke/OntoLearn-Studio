"""Own pure-math checks; all invoice expectations are literal hand values."""
from pathlib import Path
import ast
import copy
import json
import unittest

from invoice_model import (Ledger, Record, allocation, key_bytes, limb, revalidation_caps, tlv,
                           restore_bounds, direct_bounds)

BASE = Path(__file__).parent


class IndependentMathTests(unittest.TestCase):
    def test_literal_hand_invoices(self):
        data = json.loads((BASE / 'hand_vectors.json').read_text())
        by_id = {v['id']: v for v in data['vectors']}
        for vector in data['vectors']:
            with self.subTest(vector=vector['id']):
                source = by_id[vector['sameEvents']] if 'sameEvents' in vector else vector
                events = [copy.deepcopy(data['finalizer'] if e == 'FINAL' else e)
                          for e in source['events']]
                caps = data['commonCaps'] | vector.get('overrides', {})
                actual = Ledger(caps).run(events)
                for field, expected in vector['expected'].items():
                    if type(expected) is dict:
                        for domain, value in expected.items():
                            self.assertEqual(actual[field][domain], value, (vector['id'], field, domain))
                    else:
                        self.assertEqual(actual[field], expected, (vector['id'], field))

    def test_sorted_allocator_literal_full_three(self):
        children = allocation((('z', False), ('a', True), ('m', False)))
        self.assertEqual([c['rule_id'] for c in children], ['a', 'm', 'z'])
        self.assertEqual([c['definition_ordinal'] for c in children], [1, 2, 0])
        self.assertEqual([c['disabled'] for c in children], [True, False, False])
        expected = {
            'work': [5592406,5592405,5592405],
            'input_bytes': [87382,87381,87381], 'output_bytes': [87382,87381,87381],
            'trace_items': [2731,2731,2730], 'firings': [342,341,341],
            'head_occurrences': [5462,5461,5461], 'bindings': [342,341,341],
            'term_bytes': [16384]*3, 'source_bytes': [65536]*3, 'digits': [4096]*3,
            'integer_bits': [16384]*3, 'temporary_bits': [32768]*3,
            'rules': [100]*3, 'when': [16]*3, 'comparisons': [32]*3,
            'heads': [16]*3, 'variables': [64]*3,
        }
        self.assertEqual(len(expected), 17)
        for field, literal in expected.items():
            self.assertEqual([c['limits'][field] for c in children], literal)
        self.assertEqual(revalidation_caps(children),
                         {'work':51414625, 'input_bytes':524288, 'output_bytes':524288})

    def test_dummy_disabled_and_zero_remainder(self):
        dummy = allocation(())
        self.assertEqual((dummy[0]['rule_id'], dummy[0]['definition_ordinal']), (None,None))
        self.assertEqual(dummy[0]['limits']['work'], 16777216)
        self.assertEqual(revalidation_caps(dummy),
                         {'work':51414219, 'input_bytes':524288, 'output_bytes':524288})
        two = allocation((('z', False), ('a', True)))
        self.assertEqual([c['limits']['work'] for c in two], [8388608,8388608])
        self.assertEqual([c['limits']['firings'] for c in two], [512,512])
        self.assertEqual([c['limits']['trace_items'] for c in two], [4096,4096])
        self.assertRaises(ValueError, allocation, (('a', False), ('a', True)))
        self.assertRaises(ValueError, allocation, (('a', 1),))

    def test_limb_and_explicit_encoding(self):
        self.assertEqual([limb(v) for v in (0,1,-1,4294967295,4294967296)], [1,1,1,1,2])
        self.assertRaises(ValueError, limb, True)
        self.assertEqual(tlv(None).hex(), '4e')
        self.assertEqual(tlv(True).hex(), '54')
        self.assertEqual(tlv(0).hex(), '4900000003307830')
        self.assertEqual(tlv('中').hex(), '5300000003e4b8ad')
        self.assertEqual(tlv((None,False)).hex(), '41000000024e46')
        self.assertEqual(tlv(Record((('a',None),))).hex(), '52000000015300000001614e')
        self.assertRaises(ValueError, tlv, 0.0)
        fields = ('iri','urn:x',None,None,None,None,None,None)
        self.assertEqual(len(key_bytes(fields, False)), 57)
        self.assertEqual(key_bytes(fields, False)[:9], b'I05RTK1\x00\x00')
        self.assertNotEqual(key_bytes(fields, False), key_bytes(fields, True))
        self.assertNotEqual(key_bytes(('iri','urn:x',None,None,'',None,None,None), True),
                            key_bytes(fields, True))
        self.assertNotEqual(key_bytes(('literal','x',None,'EN',None,None,None,None),False),
                            key_bytes(('literal','x',None,'en',None,None,None,None),False))

    def test_same_ledger_no_retry_and_new_operation_aggregate(self):
        data = json.loads((BASE / 'hand_vectors.json').read_text())
        vector = next(v for v in data['vectors'] if v['id']=='whole-stream-restore-one')
        events = [data['finalizer'] if e=='FINAL' else e for e in vector['events']]
        a, b = Ledger(data['commonCaps']), Ledger(data['commonCaps'])
        r1, r2 = a.run(events), b.run(events)
        self.assertEqual(r1['used']['work'] + r2['used']['work'], 56)
        self.assertEqual(r1['used']['hash_bytes'] + r2['used']['hash_bytes'], 22)
        self.assertRaises(ValueError, a.run, events)
        failed = Ledger(data['commonCaps'] | {'work':13})
        self.assertEqual(failed.run(events)['first'], 'finalization-prepay')
        self.assertRaises(ValueError, failed.run, events)

    def test_unknown_not_zero_atomic_vector_and_finalize_gate(self):
        final = {'id':'f','kind':'finalize','handles':0,'slots':0,'fields':0,'bytes':0,'domain_bytes':0}
        self.assertRaises(ValueError, Ledger({'work':0,'objects':1,'scalar':0}).run, [final])
        self.assertRaises(ValueError, Ledger({'work':5}).run,
                          [{'id':'x','kind':'item','n':1}])
        data = json.loads((BASE / 'hand_vectors.json').read_text())
        cap = data['commonCaps'] | {'work':20,'output_bytes':1}
        events = [data['finalizer'], {'id':'x','kind':'output','n':7}, {'id':'done','kind':'finish'}]
        result = Ledger(cap).run(events)
        self.assertEqual(result['first'], 'x')
        self.assertEqual(result['domain'], 'work')
        self.assertEqual(result['used']['output_bytes'], 0)
        self.assertEqual(result['used']['work'], 14)
        self.assertRaises(ValueError, Ledger(data['commonCaps']).run,
                          [data['finalizer'], {'id':'x','kind':'block','proof':'','charges':{}}])

    def test_literal_local_bounds_are_not_invoices(self):
        self.assertEqual(direct_bounds(), {'fixed_traversal_subbound':139417856,
                         'objects':270635588,'scalar':50331776,
                         'general_work_cap':581671040,'general_scan_copy_cap':581671040})
        self.assertEqual(restore_bounds(b=1,q=2,j=3,n=1,f=0,m=0,u=0,s=0,
                         input_caps=0,output_caps=0),
                         {'wire_passes':18,'schema':24576,'traversal':67072,
                          'integer_hex':6144,'scan_copy':65728,'cache_query':0,
                          'cache_split':0,'cache_allocation':320,'rule_lookup':65842,
                          'pv_compare':0,'hash':65584,'scalar':1052720,'objects':6425,
                          'opaque_scalar':536870912,'opaque_objects':4096})
        self.assertRaises(ValueError, restore_bounds, b=1,q=2,j=4,n=1,f=0,m=0,u=0,s=0,
                          input_caps=0,output_caps=0)

    def test_pure_import_surface_ast(self):
        allowed = {'__future__','dataclasses','hashlib'}
        tree = ast.parse((BASE/'invoice_model.py').read_text())
        imports = {n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        imports |= {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
        self.assertLessEqual(imports, allowed)
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func,ast.Name)
                             and n.func.id in ('eval','exec','__import__') for n in ast.walk(tree)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
