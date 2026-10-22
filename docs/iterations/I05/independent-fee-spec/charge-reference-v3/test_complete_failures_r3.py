"""Full-entry R3 failures from independent review inputs + fresh literal cases."""
from pathlib import Path
import json
import hashlib
import unittest
import reference as r

HERE=Path(__file__).resolve().parent
REVIEW=HERE.parents[3]/'reviews'/'I05'/'independent-fee-spec'
RAW=(REVIEW/'independent-r2-adversarial.json').read_bytes()
assert len(RAW)==885171 and hashlib.sha256(RAW).hexdigest()=='9ff669c97b24cd72a4aa22862dca344dac8cd75ac0ce34d8d8624ee94506f49d'
CASES={v['id']:v['input'] for v in json.loads(RAW)['cases']}
SOURCE=hashlib.sha256((HERE/'reference.py').read_bytes()).hexdigest()

def run_case(label,dataset):
    observation={'id':label,'datasetId':label,'operation':'profile','parameters':{},'projectionSha256':hashlib.sha256(json.dumps(dataset,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
    return r.make_program(observation,dataset,{'rdfsAdded':[],'customOutput':[]},SOURCE)[0]


def assert_closed(test,result,reason):
    test.assertEqual(result['state'],'failed');test.assertEqual(result['firstError']['reason'],reason)
    test.assertTrue(result['H01Required']);test.assertTrue(result['finalization']['H01Paid'])
    test.assertTrue(result['finalization']['staticProofBeforeExecution']);test.assertTrue(result['noSuccessPrefix'])
    test.assertEqual(result['terminalRetainedHandles'],{})
    test.assertTrue(all(v=={'objects':0,'scalar':0} for v in result['terminalLive'].values()))
    test.assertTrue(any(e['action']=='receipt+all cumulative cleanup prepayment' for e in result['executionEvents']))
    test.assertTrue(any(e['action']=='terminal cleanup control' for e in result['executionEvents']))
    test.assertEqual(result['finalization']['receiptCounters'],'paid execution, never analytic demand')
    test.assertEqual(len(bytes.fromhex(result['finalization']['receiptHex'])),result['finalization']['receiptBytes'])

class CompleteEntryFailures(unittest.TestCase):
    def test_independent_late_bad_integer_full_entry_invoice(self):
        v=run_case('late-input-invalid-integer',CASES['late-input-invalid-integer']);assert_closed(self,v,'INVALID_LITERAL_LEXICAL')
        self.assertEqual(v['firstError']['wallet'],'ENTRY');self.assertIsNone(v['firstLimit'])
        self.assertEqual(v['paidPrefix']['ENTRY']['input_bytes'],337)
        self.assertEqual(sum(e['action']=='term+source occurrence encoding' for e in v['executionEvents']),3)
    def test_independent_false_then_actual_domain_error(self):
        v=run_case('false-then-type-error',CASES['false-then-type-error']);assert_closed(self,v,'RULE_COMPARISON_TYPE_MISMATCH')
        self.assertEqual(sum(e['action']=='comparison occurrence' for e in v['executionEvents']),2)
        self.assertEqual(v['paidPrefix']['M0']['trace_items'],1)
        self.assertEqual(v['paidPrefix']['M0']['head_occurrences'],0)
    def test_earlier_resource_preserved_not_later_lexical(self):
        v=run_case('resource-before-late-lexical',CASES['resource-before-late-lexical']);assert_closed(self,v,'RESOURCE_LIMIT')
        self.assertEqual(v['firstError']['kind'],'resource');self.assertEqual(v['firstError']['domain'],'input_bytes')
        self.assertEqual((v['paidPrefix']['ENTRY']['input_bytes'],v['firstError']['requested']['input_bytes']),(250824,50202))
        self.assertEqual(v['firstError']['event'],53) # H01 + four additional SourceRecord visits: JSON has six distinct records, prior collector reused two.
        self.assertEqual(sum(e['action']=='each original or synthetic SourceRecord full validation/copy' for e in v['executionEvents']),6)
        self.assertFalse(v['semanticAnalysis']['reachedByExecution'])
        self.assertEqual(v['semanticAnalysis']['observed']['reason'],'INVALID_LITERAL_LEXICAL')
        self.assertFalse(any(e.get('semanticError') for e in v['executionEvents']))
    def test_source_alias_cannot_waive_occurrence_validation(self):
        independent=CASES['resource-before-late-lexical']
        shared=json.loads(json.dumps(independent))
        for record in shared['records']:
            for term in record:term['source']=record[0]['source']
        a=run_case('resource-before-late-lexical',independent)
        b=run_case('resource-before-late-lexical',shared)
        self.assertEqual(a['programSha256'],b['programSha256'])
        self.assertEqual(a['executionSha256'],b['executionSha256'])
        self.assertEqual(a['amount'],b['amount']);self.assertEqual(a['paidPrefix'],b['paidPrefix'])
        self.assertEqual(a['firstError']['event'],53)
        self.assertEqual(sum(e['action']=='each original or synthetic SourceRecord full validation/copy' for e in b['executionEvents']),6)
    def test_zero_match_and_disabled_compile_static_head_permission(self):
        for label in ('uncontrolled-head-zero-match','uncontrolled-head-disabled'):
            with self.subTest(label=label):
                v=run_case(label,CASES[label]);assert_closed(self,v,'INVALID_RULE')
                self.assertEqual(v['firstError']['wallet'],'M0')
                self.assertTrue(any(e['action']=='static controlled head predicate/class reference' for e in v['executionEvents']))
                self.assertFalse(any(e['action']=='join candidate visit' for e in v['executionEvents']))
    def test_disabled_when_variable_predicate_structure(self):
        v=run_case('variable-predicate-disabled',CASES['variable-predicate-disabled']);assert_closed(self,v,'INVALID_RULE')
        self.assertTrue(any(e['action']=='static when subject/predicate/object positions' for e in v['executionEvents']))
        self.assertFalse(any(e['action']=='proposal-only plan fingerprint' for e in v['executionEvents']))
    def test_constant_class_and_property_object_with_subject_variable(self):
        base=CASES['uncontrolled-head-disabled']
        for predicate,obj in [(r.RDF+'type',r.term('<urn:undeclaredClass>')),('urn:score',r.term('<urn:wrongIRI>'))]:
            data=json.loads(json.dumps(base));data['rules'][0]['heads']=[[{'variable':'?s'},r.term('<'+predicate+'>'),obj]]
            v=run_case('constant-head-precheck',data);assert_closed(self,v,'INVALID_RULE')
            self.assertEqual(v['paidPrefix']['M0']['output_bytes'],0)
    def test_entry_binder_errors_are_closed_without_fake_dummy(self):
        data={'input':{'asserted':[{'triple':{'subject':'urn:s','predicate':'urn:p','object':'"bad'},'source':None}],'ontology':[],'definitions':[]}}
        v=run_case('bad-raw-outer-string',data);assert_closed(self,v,'INVALID_RULE')
        self.assertEqual(v['binderMeasures']['state'],'binding-not-completed')
        self.assertIsNone(v['feeMaterialSha256']);self.assertIsNone(v['feeCodec']['payloadBytes'])
    def test_invalid_unicode_and_late_receiver_exit_still_close(self):
        data=json.loads(json.dumps(CASES['late-input-invalid-integer']));data['records'][0][2]['lexical_form']='\ud800'
        v=run_case('invalid-unicode',data);assert_closed(self,v,'INVALID_RULE');self.assertIsNone(v['feeMaterialSha256'])
        data={'records':[[r.term('<urn:s>'),r.term('<urn:p>'),r.term('<urn:o>')]],'rules':[],'disabled_rule_ids':[]}
        observation={'id':'invalid-receiver-enum','datasetId':'invalid-receiver-enum','operation':'restore-negative','parameters':{'mutation':'not-an-enum'},'projectionSha256':hashlib.sha256(r.canonical(data)).hexdigest()}
        v,_=r.make_program(observation,data,{'rdfsAdded':[],'customOutput':[]},SOURCE)
        assert_closed(self,v,'INVALID_RULE');self.assertGreater(v['feeCodec']['payloadBytes'],0)
        self.assertEqual(v['firstError']['phase'],'restore:receiver')

    def test_supported_primitive_errors_close_through_real_make_program(self):
        base=CASES['late-input-invalid-integer']
        for lexical,dt,reason in [('NaN','double','UNSUPPORTED_NONFINITE_LITERAL'),('2147483648','int','INVALID_LITERAL_LEXICAL'),('0001-01-01T24:00:00.1Z','dateTime','INVALID_LITERAL_LEXICAL'),('x','unsupported','UNSUPPORTED_LITERAL_DATATYPE')]:
            data=json.loads(json.dumps(base));data['records'][0][2].update(lexical_form=lexical,datatype_iri=r.XSD+dt)
            v=run_case('primitive-error-'+dt,data);assert_closed(self,v,reason)

if __name__=='__main__':unittest.main(verbosity=2)
