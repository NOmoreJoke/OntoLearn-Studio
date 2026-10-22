"""Reviewer-selected pure fee examples; never product or original input edits."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import traceback

ROOT=Path(__file__).resolve().parents[4]
REVIEW=Path(__file__).parent
SPEC=ROOT/'docs/iterations/I05/independent-fee-spec'
REF=SPEC/'charge-reference-v2'
sys.path.insert(0,str(REF))
import reference as r
sys.path.insert(0,str(SPEC))
import invoice_model as m

def term(text,dt=None):
    return {'kind':'literal' if dt else 'iri','lexical_form':text,'datatype_iri':r.XSD+dt if dt else None,'language_raw':None,'source':None}
def var(name):return {'variable':'?'+name}
def triple(s,p,o):return [s,p,o]
def definition(when,comparisons,heads):
    return {'rule_id':'review-rule','when':when,'comparisons':comparisons,'heads':heads,'source':None,'revision':None,'definition_digest':None,'policy':r.PROFILE}
def observation(label):
    return {'id':'independent-review/'+label,'datasetId':'synthetic/'+label,'operation':'profile','parameters':{},'projectionSha256':'00'*32}

def case(label,dataset,business=None):
    tapes=[];original=r.Tape
    class Observed(original):
        def __init__(self,*a,**k):
            super().__init__(*a,**k);tapes.append(self)
    r.Tape=Observed
    result=None;failure=None
    try:
        result,_=r.make_program(observation(label),dataset,business or {'rdfsAdded':[],'customOutput':[]},hashlib.sha256((REF/'reference.py').read_bytes()).hexdigest())
    except Exception as e:
        failure={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
    finally:r.Tape=original
    t=tapes[-1]
    return {'id':label,'input':dataset,'error':failure,'returnedInvoice':result is not None,
       'resultSummary':None if result is None else {k:result[k] for k in ('feeAdmission','firstLimit','terminalLive','H01Required','mathematicalCounts')},
       'observedGenerationTape':{'eventCount':len(t.events),'firstLimit':t.first,'used':t.used,'live':t.live,
         'retainedHandles':t.handles,'H01EventPresent':any(e['action']=='receipt+all cumulative cleanup prepayment' for e in t.events),
         'events':t.events}}

rows=[]
# A real semantic error during the complete reference entry, after normal data.
rows.append(case('late-input-invalid-integer',{'records':[triple(term('urn:s'),term('urn:p'),term('bad','integer'))],'rules':[],'disabled_rule_ids':[]}))
# A false first comparison cannot hide a later mismatch; the complete reference
# must return a failed invoice rather than lose its already-enumerated prefix.
score=term('urn:score');decl=triple(score,term(r.RDF+'type'),term(r.OWL+'DatatypeProperty'))
record=triple(term('urn:s'),score,term('1','integer'))
when=[triple(var('s'),score,var('v'))]
comp=[{'left':var('v'),'operator':'gt','right':term('2','integer')},{'left':var('v'),'operator':'ne','right':term('x','string')}]
rule=definition(when,comp,[triple(var('s'),score,var('v'))])
rows.append(case('false-then-type-error',{'records':[record,decl],'rules':[rule],'disabled_rule_ids':[]}))
# Invalid constant head predicate is knowable at compile, independent of matches.
bad=definition([triple(var('s'),term('urn:never-present'),var('v'))],[],[triple(var('s'),term('urn:undeclared'),var('v'))])
for disabled in (False,True):
    rows.append(case('uncontrolled-head-'+('disabled' if disabled else 'zero-match'),{'records':[decl],'rules':[bad],'disabled_rule_ids':['review-rule'] if disabled else []}))
# Fixed new-profile Triple.predicate is a TermInput, never Variable. This is a
# compile guard independent of any successful instantiated head.
bad_when=definition([triple(var('s'),var('predicate'),var('o'))],[],[triple(var('s'),score,var('o'))])
rows.append(case('variable-predicate-disabled',{'records':[decl],'rules':[bad_when],'disabled_rule_ids':['review-rule']}))
# Crossing the input cap before a bad lexical value must preserve resource first.
source={'reference':None,'digest':None,'revision':None,'text':'s'*50000}
large=[term('urn:s')|{'source':source},term('urn:p')|{'source':source},term('1','integer')|{'source':source}]
second=copy.deepcopy(large);second[-1]['lexical_form']='bad'
rows.append(case('resource-before-late-lexical',{'records':[large,second],'rules':[],'disabled_rule_ids':[]}))

# Independent strengthened F2/F3 vectors; these are separate from author tests.
caps={'work':1000,'scan_copy':1000,'hash_bytes':1000,'objects':100,'scalar':100}
final={'id':'final','kind':'finalize','handles':3,'slots':5,'fields':2,'bytes':3,'domain_bytes':1}
control={'id':'control','kind':'hold','handle':'control','objects':64,'scalar':0}
block={'id':'delegate','kind':'block','proof':'reviewer bounded2/3 temporary and1/2 retained',
       'charges':{'work':11,'scan_copy':7,'hash_bytes':5},'live':{'objects':2,'scalar':3},
       'retained':{'handle':'out','objects':1,'scalar':2}}
tail={'id':'after-release','kind':'hold','handle':'tail','objects':2,'scalar':1}
events=[control,final,block,{'id':'release-out','kind':'release','handle':'out'},tail,{'id':'done','kind':'finish'}]
bound=[]
for oc in (69,70):
    ledger=m.Ledger(caps|{'objects':oc});result=ledger.run(events)
    bound.append({'objectsCap':oc,'result':result})
    if oc==69:
        assert result['state']=='failed' and result['first']=='delegate'
        assert result['used']['work']==16 and result['newHandles']==0
        assert result['peak']['objects']==67 and result['live']=={'objects':0,'scalar':0}
    else:
        assert result['newHandles']==3 and result['newSlots']==5
        assert result['used']['work']==27 and result['state']=='completed' and result['peak']['objects']==70

data={'format':'i05-reviewer-pure-adversarial/2','cases':rows,'independentLifecycleVectors':bound}
(REVIEW/'independent-r2-adversarial.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'cases':[{'id':x['id'],'error':None if x['error'] is None else x['error']['message'],'returnedInvoice':x['returnedInvoice'],'H01Present':x['observedGenerationTape']['H01EventPresent'],'eventCount':x['observedGenerationTape']['eventCount'],'firstLimit':x['observedGenerationTape']['firstLimit']} for x in rows],'lifecycle':bound},ensure_ascii=False,indent=2))
