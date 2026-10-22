"""Fresh reviewer-selected bounded fee mathematics, not product invocation."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import traceback

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
REF=ROOT/'docs/iterations/I05/independent-fee-spec/charge-reference-v3'
sys.path.insert(0,str(REF))
import reference as r
SOURCE=hashlib.sha256((REF/'reference.py').read_bytes()).hexdigest()
def term(text,dt=None):
    return {'kind':'literal' if dt else 'iri','lexical_form':text,'datatype_iri':r.XSD+dt if dt else None,'language_raw':None,'source':None}
def var(x):return {'variable':'?'+x}
def rule(rid,heads=None):
    return {'rule_id':rid,'when':[[var('s'),term('urn:score'),var('v')]],'comparisons':[],
       'heads':heads or [[var('s'),term('urn:score'),var('v')]],'source':None,'revision':None,'definition_digest':None,'policy':r.PROFILE}
DECL=[term('urn:score'),term(r.RDF+'type'),term(r.OWL+'DatatypeProperty')]
def data(rid,heads=None):return {'records':[[term('urn:s'),term('urn:score'),term('1','integer')],DECL],
      'rules':[rule(rid,heads)],'disabled_rule_ids':[]}
def run(label,dataset,business=None,limits=None):
    ob={'id':label,'datasetId':'review/'+label,'operation':'profile','parameters':{},
        'projectionSha256':r.sha(json.dumps(dataset,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode())}
    original=r.finish_program
    if limits:
        def constrained(t,*args,**kwargs):
            for w,domain,value in limits:t.caps[w][domain]=value
            return original(t,*args,**kwargs)
        r.finish_program=constrained
    try:
        result,_=r.make_program(ob,dataset,business or {'rdfsAdded':[],'customOutput':[]},SOURCE)
        return {'id':label,'input':dataset,'loweredMathematicalCaps':limits,'returnedInvoice':True,'invoice':result}
    except Exception as e:
        return {'id':label,'input':dataset,'loweredMathematicalCaps':limits,'returnedInvoice':False,
                'error':{'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}}
    finally:r.finish_program=original

rows=[]
rows.append(run('nonstring-rule-id',data(7)))
expected={'rdfsAdded':[],'customOutput':[[{'kind':'iri','value':'urn:s'},{'kind':'iri','value':'urn:score'},{'kind':'literal','lexical':'1','datatype':r.XSD+'integer'}]]}
rows.append(run('empty-rule-id',data(''),expected))
heads=[[var('s'),term('urn:score'),var('v')],[var('v'),term('urn:score'),var('v')]]
rows.append(run('last-head-bound-literal-subject',data('late-head',heads)))
valid=data('valid-fee-program')
business=expected
ok=run('lowercap-boundary',valid,business);rows.append(ok)
assert ok['returnedInvoice'] and ok['invoice']['state']=='completed'
f=ok['invoice']['finalization']['vector']['work'];m=ok['invoice']['paidPrefix']['M0']['work']
rows.append(run('lowercap-boundary',valid,business,[('C0','work',f-1)]))
rows.append(run('lowercap-boundary',valid,business,[('M0','work',m-1)]))
rows.append(run('lowercap-boundary',valid,business,[('M0','work',m)]))
rows.append(run('lowercap-boundary',valid,business,[('M0','work',m+1)]))
# Test a fixed rdf:type predicate whose object is a variable. The adopted I05
# profile contract requires this position to be a declared Class TermInput.
class_decl=[term('urn:C'),term(r.RDF+'type'),term(r.OWL+'Class')]
class_ref=[term('urn:s'),term('urn:classRef'),term('urn:C')]
typed=rule('variable-class',[[var('s'),term(r.RDF+'type'),var('v')]])
typed['when']=[[var('s'),term('urn:classRef'),var('v')]]
rows.append(run('variable-rdf-type-object',{'records':[class_ref,class_decl],'rules':[typed],'disabled_rule_ids':[]},
   {'rdfsAdded':[],'customOutput':[[{'kind':'iri','value':'urn:s'},{'kind':'iri','value':r.RDF+'type'},{'kind':'iri','value':'urn:C'}]]}))
# A different source alias graph from the original two-object selection: all six
# occurrences share one source; JSON readback has six independent source dicts.
source={'reference':'review-source','digest':None,'revision':r.INPUT_REF,'text':'independent source text'}
aliased={'records':[[term('urn:s'),term('urn:p'),term('urn:o')],[term('urn:t'),term('urn:p'),term('urn:o')]],'rules':[],'disabled_rule_ids':[]}
for triple in aliased['records']:
    for value in triple:value['source']=source
separate=json.loads(json.dumps(aliased))
a,b=run('fresh-source-alias',aliased),run('fresh-source-alias',separate)
assert a['returnedInvoice'] and b['returnedInvoice']
assert a['invoice']==b['invoice']
source_events=[e for e in a['invoice']['executionEvents'] if e['action']=='each original or synthetic SourceRecord full validation/copy']
hash_events=[e for e in a['invoice']['executionEvents'] if e['action']=='each synthesized SourceRecord digest, never locator bytes']
assert len(source_events)==len(hash_events)==6
alias={'valuesEqual':aliased==separate,'sharedSourceObjects':len({id(x['source']) for row in aliased['records'] for x in row}),
       'readbackSourceObjects':len({id(x['source']) for row in separate['records'] for x in row}),
       'completeInvoicesEqual':True,'scanOccurrences':6,'hashOccurrences':6,
       'sourceScanBytes':sum(e['charges']['scan_copy'] for e in source_events),'synthesizedHashBytes':sum(e['charges']['hash_bytes'] for e in hash_events),
       'programSha256':a['invoice']['programSha256'],'executionSha256':a['invoice']['executionSha256']}
out={'format':'i05-independent-r3-reviewer-counterexamples/1','cases':rows,'newSourceAliasBoundary':alias}
(HERE/'independent-r3-adversarial.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
summary=[]
for x in rows:
    p=x.get('invoice');summary.append({'id':x['id'],'loweredCaps':x['loweredMathematicalCaps'],'returnedInvoice':x['returnedInvoice'],
      'error':x.get('error'),'state':p['state'] if p else None,'firstError':p['firstError'] if p else None,'H01Paid':p['finalization']['H01Paid'] if p else None,
      'paidC0':p['paidPrefix']['C0']['work'] if p else None,'paidM0':p['paidPrefix'].get('M0',{}).get('work') if p else None,
      'retained':p['terminalRetainedHandles'] if p else None})
print(json.dumps({'cases':summary,'newSourceAliasBoundary':alias},ensure_ascii=False,indent=2))
