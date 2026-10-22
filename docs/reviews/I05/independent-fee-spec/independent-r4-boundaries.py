"""New reviewer choices for metadata pointers, source domains and class gates."""
from pathlib import Path
import copy
import hashlib
import importlib
import json
import sys
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
REF=ROOT/'docs/iterations/I05/independent-fee-spec/charge-reference-v4'
sys.path.insert(0,str(REF));sys.path.insert(0,str(HERE))
import reference as r
audit=importlib.import_module('independent-r4-verify')
SOURCE=hashlib.sha256((REF/'reference.py').read_bytes()).hexdigest()
def iri(v):return {'kind':'iri','lexical_form':v,'datatype_iri':None,'language_raw':None,'source':None}
def literal(v):return {'kind':'literal','lexical_form':v,'datatype_iri':r.XSD+'string','language_raw':None,'source':None}
def var(v):return {'variable':'?'+v}
def definition(rid):return {'rule_id':rid,'when':[[var('s'),iri('urn:p'),var('v')]],'comparisons':[],
     'heads':[[var('s'),iri('urn:q'),var('v')]],'source':None,'revision':None,'definition_digest':None,'policy':r.PROFILE}
def base():return {'records':[[iri('urn:s'),iri('urn:p'),iri('urn:o')],[iri('urn:q'),iri(r.RDF+'type'),iri(r.OWL+'ObjectProperty')]],'rules':[definition('first')],'disabled_rule_ids':[]}
business={'rdfsAdded':[],'customOutput':[[{'kind':'iri','value':'urn:s'},{'kind':'iri','value':'urn:q'},{'kind':'iri','value':'urn:o'}]]}
rows=[]
def run(label,data,expected=None,lower=None):
    ob={'id':label,'datasetId':'review/a~b/'+label,'operation':'profile','parameters':{},
        'projectionSha256':r.sha(json.dumps(data,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode())}
    original=r.finish_program
    if lower:
        def constrained(t,*args,**kwargs):
            t.caps['C0']['work']=lower
            return original(t,*args,**kwargs)
        r.finish_program=constrained
    try:p,_=r.make_program(ob,data,expected or business,SOURCE)
    finally:r.finish_program=original
    audit.replay(p,'events');audit.replay(p,'executionEvents');children,projection=audit.receipt(p)
    assert projection==ob['projectionSha256']
    if p['state']=='failed':assert not p['terminalRetainedHandles'] and all(not any(x.values()) for x in p['terminalLive'].values())
    rows.append({'id':label,'input':data,'observation':ob,'loweredMathematicalC0Work':lower,'invoice':p,'decodedAllocation':children})
    return p,children
def metadata_fail(label,data,pointer_suffix,reason='INVALID_RULE'):
    p,children=run(label,data)
    assert p['firstError']['reason']==reason and p['entryMetadata']['state']=='rejected'
    assert p['firstError']['inputPointer']=='/datasets/review~1a~0b~1'+label+pointer_suffix
    assert not p['entryMetadata']['allocationStarted'] and children==[] and p['finalization']['fields']==26
    assert p['feeCodec']['nativeBytes'] is None and set(p['caps'])=={'C0'}
    assert not any('allocator' in e['action'] for e in p['events'])
    return p

late=base();late['rules'].extend([definition('second'),definition(True)])
p=metadata_fail('third-bool-id-before-bad-term',late,'/rules/2/rule_id')
assert p['entryMetadata']['validatedRuleCount']==2
third=base();third['rules'].extend([definition('second'),definition('third')]);third['rules'][2]['source']={'reference':7,'digest':None,'revision':None,'text':None}
metadata_fail('third-source-field-type',third,'/rules/2/source/reference')
both=base();both['definitions']=[];metadata_fail('ambiguous-rule-containers',both,'/rules')
missing=base();del missing['rules'][0]['heads'];metadata_fail('missing-heads-container',missing,'/rules/0/heads')
disabled=base();disabled['disabled_rule_ids']=['first',False];metadata_fail('disabled-bool-tail',disabled,'/disabled_rule_ids/1')
# Later metadata still wins before binder/record parsing; no partial allocation.
late_bad=copy.deepcopy(late);late_bad['records'][0][2]['lexical_form']='\ud800'
metadata_fail('metadata-before-invalid-record-scalar',late_bad,'/rules/2/rule_id')
# Typed SourceRecord and raw locator are deliberately different domains.
locator={'ref':'review-ref','path':'review/rules','pointer':'/rules/0','sha256':'0'*64}
wrong=base();wrong['rules'][0]['source']=locator
metadata_fail('locator-in-typed-rule',wrong,'/rules/0/source')
def raw_term(t):
    if 'variable' in t:return t['variable']
    return '<'+t['lexical_form']+'>'
b=base();d=b['rules'][0]
raw={'input':{'asserted':[{'triple':dict(zip(('subject','predicate','object'),map(raw_term,b['records'][0]))),'source':locator}],
     'ontology':[{'triple':dict(zip(('subject','predicate','object'),map(raw_term,b['records'][1]))),'source':locator}],
     'definitions':[{'rule_id':'raw-locator','when':[dict(zip(('subject','predicate','object'),map(raw_term,t))) for t in d['when']],
        'comparisons':[],'heads':[dict(zip(('subject','predicate','object'),map(raw_term,t))) for t in d['heads']],
        'source':locator,'revision':None,'policy':r.PROFILE}],'disabled_rule_ids':[]}}
good,_=run('raw-locator-is-not-SourceRecord',raw);assert good['state']=='completed' and all(good['independentMathematicalChecks'].values())
wrongraw=copy.deepcopy(raw);wrongraw['input']['definitions'][0]['source']={'reference':None,'digest':None,'revision':None,'text':None}
metadata_fail('SourceRecord-in-raw-locator',wrongraw,'/input/definitions/0/source')
# Four-byte scalar UTF8 boundary, distinct from the author's two-byte selection.
for count,okay in ((4096,True),(4097,False)):
    data=base();data['rules'][0]['rule_id']='\U00010000'*count
    if okay:
        result,_=run('four-byte-id-exact-bound',data);assert result['state']=='completed'
    else:metadata_fail('four-byte-id-over-bound',data,'/rules/0/rule_id','RESOURCE_LIMIT')
# IDs retain full Unicode identity rather than applying a new normalization.
distinct=base();distinct['rules']=[definition('é'),definition('e\u0301')]
result,children=run('distinct-unicode-rule-identities',distinct);assert result['state']=='completed'
assert [c['rule_id'] for c in children]==['e\u0301','é']
# Kind/Catalog checks on both sections, with an allowed object-property binding.
classes=base();classes['records'].append([iri('urn:C'),iri(r.RDF+'type'),iri(r.OWL+'Class')])
classes['records'][0][2]=iri('urn:C')
for section in ('when','heads'):
    for mode in ('enabled','disabled','zero-match'):
        data=copy.deepcopy(classes)
        if section=='heads':data['rules'][0]['heads']=[[var('s'),iri(r.RDF+'type'),var('v')]]
        else:
            data['records'].append([iri('urn:s'),iri(r.RDF+'type'),iri('urn:C')])
            data['rules'][0]['when']=[[var('s'),iri(r.RDF+'type'),var('v')]]
        if mode=='disabled':data['disabled_rule_ids']=['first']
        if mode=='zero-match':data['rules'][0]['when'].append([var('s'),iri('urn:no-match'),var('x')])
        result,_=run(section+'-variable-class-'+mode,data)
        assert result['state']=='failed' and result['firstError']['phase']=='compile:'+('head' if section=='heads' else 'when')
        assert not any(e['action']=='join candidate visit' for e in result['executionEvents'])
    for obj,label in ((literal('C'),'literal'),(iri('urn:undeclared'),'undeclared')):
        data=copy.deepcopy(classes)
        data['rules'][0][section]=[[var('s'),iri(r.RDF+'type'),obj]]
        if section=='when':data['rules'][0]['heads']=[[var('s'),iri('urn:q'),iri('urn:o')]]
        result,_=run(section+'-'+label+'-class',data)
        assert result['state']=='failed' and result['firstError']['phase']=='compile:'+('head' if section=='heads' else 'when')
positive=base();result,_=run('object-property-variable-object-allowed',positive)
assert result['state']=='completed' and all(result['independentMathematicalChecks'].values())
# An E00 budget prefix must win over the later real metadata error.
original,_=run('early-E00-resource',late)
cap=original['finalization']['vector']['work']+2
limited,_=run('early-E00-resource',late,lower=cap)
assert limited['state']=='failed' and limited['firstError']['kind']=='resource' and limited['firstError']['event']==5
assert limited['paidPrefix']['C0']['work']==cap and not limited['semanticAnalysis']['reachedByExecution']
out={'format':'i05-independent-r4-fresh-boundaries/1','cases':rows,'allReplayReceiptAssertionsPassed':True,
     'failedCases':sum(x['invoice']['state']=='failed' for x in rows),'successCases':sum(x['invoice']['state']=='completed' for x in rows)}
(HERE/'independent-r4-boundaries.json').write_text(json.dumps(out,ensure_ascii=True,indent=2)+'\n')
print(json.dumps({'caseCount':len(rows),'failedCases':out['failedCases'],'successCases':out['successCases'],'allReplayReceiptAssertionsPassed':True,
    'summaries':[{'id':x['id'],'state':x['invoice']['state'],'firstError':x['invoice']['firstError'],'metadata':x['invoice']['entryMetadata']} for x in rows]},ensure_ascii=True,indent=2))
