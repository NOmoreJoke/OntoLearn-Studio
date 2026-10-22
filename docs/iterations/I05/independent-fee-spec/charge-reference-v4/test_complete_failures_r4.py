"""Focused full-entry R4 metadata/language gates + unchanged R2 failure scope."""
from pathlib import Path
import hashlib
import json
import unittest
import reference as r
HERE=Path(__file__).resolve().parent
REVIEW=HERE.parents[3]/'reviews'/'I05'/'independent-fee-spec'
def fixed(name,size,digest):
    b=(REVIEW/name).read_bytes();assert (len(b),hashlib.sha256(b).hexdigest())==(size,digest);return json.loads(b)
OLD=fixed('independent-r2-adversarial.json',885171,'9ff669c97b24cd72a4aa22862dca344dac8cd75ac0ce34d8d8624ee94506f49d')
NEW=fixed('independent-r3-adversarial.json',3314201,'34ac5fac52c20e43aa544798874c36fa0f1307e0e87e32116eb04925f62e6142')
CASES={c['id']:c['input'] for c in OLD['cases']}
BASE=NEW['cases'][0]['input'];TYPE=NEW['cases'][-1]['input']
SOURCE=hashlib.sha256((HERE/'reference.py').read_bytes()).hexdigest()
def copy(v):return json.loads(json.dumps(v))
def run_case(label,data):
    ob={'id':label,'datasetId':label,'operation':'profile','parameters':{},'projectionSha256':hashlib.sha256(json.dumps(data,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
    business={'rdfsAdded':[],'customOutput':[]}
    if label in ('variable-property-object-allowed','valid-id-boundary'):
        business['customOutput']=[[{'kind':'iri','value':'urn:s'},{'kind':'iri','value':'urn:score'},{'kind':'literal','lexical':'1','datatype':r.XSD+'integer'}]]
    if label in ('fixed-class-variable-subject-allowed','fixed-when-class-allowed'):
        business['customOutput']=[[{'kind':'iri','value':'urn:s'},{'kind':'iri','value':r.RDF+'type'},{'kind':'iri','value':'urn:C'}]]
    return r.make_program(ob,data,business,SOURCE)[0]
def metadata_cases():
    result={'nonstring-rule-id':copy(BASE),'outer-input-not-mapping':{'input':7},'outer-dataset-not-mapping':[]}
    valid=copy(BASE);valid['rules'][0]['rule_id']='valid-first'
    data=copy(valid);data['rules'].append(copy(data['rules'][0]));data['rules'][1]['rule_id']=[];result['late-invalid-rule-id']=data
    data=copy(valid);data['rules'].append(copy(data['rules'][0]));result['duplicate-rule-id']=data
    data=copy(valid);data['rules']={'bad':'container'};result['rules-not-sequence']=data
    data=copy(valid);data['disabled_rule_ids']=7;result['disabled-not-sequence']=data
    data=copy(valid);data['rules'][0]['rule_id']='é'*8193;result['rule-id-byte-plus-one']=data
    data=copy(valid);data['rules'][0]['rule_id']='\ud800';result['rule-id-invalid-unicode']=data
    data=copy(valid);data['rules'][0]['revision']={'bad':'mapping'};result['rule-metadata-revision-not-string']=data
    return result
def language_cases():
    result={}
    for mode in ('enabled','disabled','zero-match'):
        data=copy(TYPE)
        if mode=='disabled':data['disabled_rule_ids']=['variable-class']
        if mode=='zero-match':data['rules'][0]['when'][0][1]=r.term('<urn:no-match>')
        result['variable-class-'+mode]=data
    data=copy(TYPE);data['rules'][0]['heads'][0][2]=r.term('<urn:C>');result['fixed-class-variable-subject-allowed']=data
    data=copy(BASE);data['rules'][0]['rule_id']='valid-variable-property-object';result['variable-property-object-allowed']=data
    return result
def when_cases():
    result={}
    for mode in ('enabled','disabled','zero-match'):
        data=copy(TYPE);rule=data['rules'][0]
        rule['when'][0][1]=r.term('<'+r.RDF+'type>');rule['heads'][0][2]=r.term('<urn:C>')
        data['records'].append([r.term('<urn:s>'),r.term('<'+r.RDF+'type>'),r.term('<urn:C>')])
        if mode=='disabled':data['disabled_rule_ids']=['variable-class']
        if mode=='zero-match':rule['when'].append([{'variable':'?s'},r.term('<urn:absent>'),{'variable':'?x'}])
        result['variable-when-class-'+mode]=data
    data=copy(result['variable-when-class-enabled']);data['rules'][0]['when'][0][2]=r.term('<urn:C>');result['fixed-when-class-allowed']=data
    data=copy(result['variable-when-class-enabled']);data['rules'][0]['when'][0][2]=r.term('<urn:undeclared>');result['undeclared-when-class']=data
    data=copy(result['variable-when-class-enabled']);data['rules'][0]['when'][0][2]=r.term('"class"');result['literal-when-class']=data
    return result
EXTRA={**metadata_cases(),**language_cases(),**when_cases()}
def closed(test,p,reason):
    test.assertEqual(p['state'],'failed');test.assertEqual(p['firstError']['reason'],reason)
    test.assertTrue(p['finalization']['H01Paid']);test.assertTrue(p['finalization']['staticProofBeforeExecution'])
    test.assertTrue(p['noSuccessPrefix']);test.assertEqual(p['terminalRetainedHandles'],{})
    test.assertTrue(all(v=={'objects':0,'scalar':0} for v in p['terminalLive'].values()))

class FullEntryR4(unittest.TestCase):
    def test_metadata_complete_front_gate_no_child_or_sort(self):
        pointers={'nonstring-rule-id':'/rules/0/rule_id','outer-input-not-mapping':'/input','outer-dataset-not-mapping':'','late-invalid-rule-id':'/rules/1/rule_id','duplicate-rule-id':'/rules/1/rule_id','rules-not-sequence':'/rules','disabled-not-sequence':'/disabled_rule_ids','rule-id-byte-plus-one':'/rules/0/rule_id','rule-id-invalid-unicode':'/rules/0/rule_id','rule-metadata-revision-not-string':'/rules/0/revision'}
        for label,data in metadata_cases().items():
            with self.subTest(label=label):
                p=run_case(label,data);closed(self,p,'RESOURCE_LIMIT' if label=='rule-id-byte-plus-one' else 'INVALID_RULE')
                self.assertEqual(p['firstError']['inputPointer'],'/datasets/'+label+pointers[label])
                self.assertEqual(p['entryMetadata']['state'],'rejected');self.assertFalse(p['entryMetadata']['allocationStarted'])
                self.assertEqual(p['binderMeasures']['state'],'binding-not-completed')
                self.assertIsNone(p['feeCodec']['nativeBytes']);self.assertIsNone(p['feeCodec']['payloadBytes'])
                self.assertEqual(p['finalization']['fields'],26) # C0 wallet only, N=0; no synthetic dummy/17L.
                self.assertEqual(set(p['caps']),{'C0'})
                self.assertFalse(any('allocator' in e['action'] or e['wallet'].startswith('M') for e in p['events']))
    def test_id_utf8_boundary_and_empty_identity_preserve_original_scope(self):
        for rid in ('','é'*8192):
            data=copy(BASE);data['rules'][0]['rule_id']=rid;p=run_case('valid-id-boundary',data)
            self.assertEqual(p['entryMetadata']['state'],'validated');self.assertIsNone(p['firstError']);self.assertEqual(p['state'],'completed')
    def test_fixed_declared_class_term_required_all_compile_modes(self):
        for label,data in language_cases().items():
            p=run_case(label,data)
            if label.startswith('variable-class-'):
                closed(self,p,'INVALID_RULE');self.assertEqual(p['firstError']['phase'],'compile:head')
                self.assertTrue(any(e['action']=='static controlled head predicate/class reference' for e in p['executionEvents']))
                self.assertFalse(any('join candidate' in e['action'] for e in p['executionEvents']))
            else:
                self.assertEqual(p['state'],'completed');self.assertEqual(p['paidPrefix']['M0']['head_occurrences'],1)
                self.assertTrue(all(p['independentMathematicalChecks'].values()))
    def test_original_six_complete_entry_boundaries(self):
        expected=('INVALID_LITERAL_LEXICAL','RULE_COMPARISON_TYPE_MISMATCH','INVALID_RULE','INVALID_RULE','INVALID_RULE','RESOURCE_LIMIT')
        for (label,data),reason in zip(CASES.items(),expected):
            with self.subTest(label=label):
                p=run_case(label,data);closed(self,p,reason)
                if label=='resource-before-late-lexical':
                    self.assertEqual(p['firstError']['domain'],'input_bytes')
                    self.assertEqual((p['firstError']['before']['input_bytes'],p['firstError']['requested']['input_bytes']),(250824,50202))
                    self.assertFalse(p['semanticAnalysis']['reachedByExecution'])
    def test_source_alias_full_invoice_equal(self):
        data=copy(CASES['resource-before-late-lexical']);shared=copy(data);source=shared['records'][0][0]['source']
        for record in shared['records']:
            for term in record:term['source']=source
        # Use equal values for one shared backing object vs independent JSON.
        independent=copy(shared)
        self.assertEqual(run_case('source-alias-boundary',shared),run_case('source-alias-boundary',independent))
    def test_when_class_gate_all_modes_and_permitted_constant(self):
        for label,data in when_cases().items():
            with self.subTest(label=label):
                p=run_case(label,data)
                if label=='fixed-when-class-allowed':
                    self.assertEqual(p['state'],'completed');self.assertTrue(all(p['independentMathematicalChecks'].values()))
                    self.assertEqual(p['paidPrefix']['M0']['head_occurrences'],1)
                else:
                    closed(self,p,'INVALID_RULE');self.assertEqual(p['firstError']['phase'],'compile:when')
                    self.assertTrue(any(e['action']=='static when rdf:type fixed class TermInput guard' for e in p['executionEvents']))
                    self.assertFalse(any('join candidate' in e['action'] for e in p['executionEvents']))

if __name__=='__main__':unittest.main(verbosity=2)
