"""Independent review, restricted to fixed pure materials and reviewer outputs."""
from pathlib import Path
import ast
import base64
import hashlib
import importlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
REVIEW=Path(__file__).parent
SPEC=ROOT/'docs/iterations/I05/independent-fee-spec'
REF=SPEC/'charge-reference-v2'
HEAD='b04f359a53fbce2c137d09f20a020facd8916231'
CAND='7554c5582619a2beddaa42bf08ffd1a8e1961214'
REV='ac6e0a91763ea18d5e17e162a275822e7caee8f4'
BASE='5f910b52c69d86a1076b2032e5d3c63e715947f3'
PREFIX=('docs/iterations/I05/independent-fee-spec/','docs/reviews/I05/independent-fee-spec/')
FORBIDDEN='docs/reviews/I05/independent-fee-spec/author-v1-input-exposure/invoice_model.py.unreviewed.raw'
calls=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def jread(p):
    assert str(p)!=str(ROOT/FORBIDDEN)
    return json.loads(p.read_bytes())
def blob(b):return {'bytes':len(b),'sha256':sha(b),'utf8':b.decode(),'base64':base64.b64encode(b).decode()}
def call(args,opaque=False):
    p=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    output={'bytes':len(p.stdout),'sha256':sha(p.stdout),'opaqueOnly':True} if opaque else blob(p.stdout)
    calls.append({'argv':args,'cwd':str(ROOT),'exit':p.returncode,'stdout':output,'stderr':blob(p.stderr)})
    assert p.returncode==0,(args,p.stderr)
    return p.stdout
def save(name,v):
    v['subprocessCommands']=calls
    (REVIEW/('independent-r2-'+name+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in v.items() if k not in ('subprocessCommands','artifacts','items','sources','originErrors')},ensure_ascii=False,indent=2))

def integrity():
    manifest=jread(REVIEW/'artifact-manifest-r2.json')
    rows=[]
    targets=manifest['artifacts']+[{'path':str((REVIEW/'artifact-manifest-r2.json').relative_to(ROOT)),'bytes':29745,'sha256':'3ee69b02684a2934e01d67666eb10a11b2c0c328479cf9e95be2a44902ef3ced'},
      {'path':str((REVIEW/'r2-author-process-receipt.json').relative_to(ROOT)),'bytes':20589,'sha256':'3453a574b4a0ca80d02e69b0f1e80892159a5b5bb14993d6fcef6c2b5043d132'}]
    for entry in targets:
        path=entry['path'];raw=(ROOT/path).read_bytes();git=call(['git','show',HEAD+':'+path],opaque=True)
        row={'path':path,'bytes':len(raw),'sha256':sha(raw),'currentEqualsGit':raw==git,
             'expectedBytesAndSha':(len(raw),sha(raw))==(entry['bytes'],entry['sha256']),
             'opaqueOnly':path==FORBIDDEN}
        rows.append(row)
        assert row['currentEqualsGit'] and row['expectedBytesAndSha'],row
        # Never decode this incident draft; git command stdout is opaque below.
        if path==FORBIDDEN:
            calls[-1]['stdout']={'bytes':len(git),'sha256':sha(git),'opaqueOnly':True}
    diffs={}
    for label,base,head in [('base',BASE,HEAD),('revision',REV,CAND),('process',CAND,HEAD)]:
        raw=call(['git','diff','--name-only','-z',base,head]);paths=raw.decode().rstrip('\0').split('\0')
        assert all(p.startswith(PREFIX) for p in paths),paths
        diffs[label]={'paths':paths,'bytes':len(raw),'sha256':sha(raw)}
    status=call(['git','status','--short']).decode()
    index=call(['git','diff','--cached','--name-only']).decode();assert not index
    actual_head=call(['git','rev-parse','HEAD']).decode().strip();assert actual_head==HEAD
    branch=call(['git','branch','--show-current']).decode().strip();assert branch=='docs/I05-independent-fee-spec'
    sources=[]
    for entry in jread(REVIEW/'input-manifest.json'):
        if entry.get('copy'):
            raw=(ROOT/entry['copy']).read_bytes()
            okay=(len(raw),sha(raw))==(entry['bytes'],entry['sha256'])
            source={'name':entry['name'],'bytes':len(raw),'sha256':sha(raw),'copyMatches':okay}
            if entry.get('ref') and len(entry['ref'])==40:
                git=call(['git','show',entry['ref']+':'+entry['path']]);source['copyEqualsFixedGit']=raw==git
                assert source['copyEqualsFixedGit']
            assert okay,source
            sources.append(source)
    ag=(ROOT/'AGENTS.md').read_bytes()
    save('integrity',{'artifactCount':len(rows),'all113CurrentGitSha':True,'artifacts':rows,
      'baseRevisionProcessDeltas':diffs,'sources':sources,'HEAD':actual_head,'branch':branch,'status':status,'index':index,
      'guidanceCurrent':{'bytes':len(ag),'sha256':sha(ag)},
      'guidanceFrozenHistorical':manifest['AGENTSProtectedUnstaged'],'guidancePolicyUpdateAuthorizedByRoot':True})

def static():
    rows=[]
    for path in [SPEC/'invoice_model.py',SPEC/'test_invoice_model.py',SPEC/'test_retention_r2.py',*sorted(REF.glob('*.py'))]:
        tree=ast.parse(path.read_text());imports=[];writes=[];danger=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
            if isinstance(n,ast.ImportFrom):imports.append(n.module)
            if isinstance(n,ast.Call):
                func=ast.unparse(n.func)
                if func.split('.')[-1] in ('write_text','write_bytes','open','unlink','mkdir'):writes.append({'line':n.lineno,'call':ast.unparse(n)})
                if func in ('eval','exec','__import__'):danger.append({'line':n.lineno,'call':ast.unparse(n)})
        assert not danger
        rows.append({'path':str(path.relative_to(ROOT)),'imports':imports,'writes':writes,'dynamicExec':danger})
    assert not next(x for x in rows if x['path'].endswith('/reference.py'))['writes']
    assert not next(x for x in rows if x['path'].endswith('/audit_prefixes.py'))['writes']
    save('static',{'parsedModules':len(rows),'items':rows,'authorMutatingDriversNotRun':True})

def import_ref():
    sys.path.insert(0,str(REF));return importlib.import_module('reference')

def pointer(root,p):
    value=root
    for part in p.split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        value=value[int(part)] if type(value) is list else value[part]
    return value

def inventory():
    old=jread(SPEC/'per-id.json');new=jread(SPEC/'per-id-r2.json');programs=jread(REF/'all114-fee-programs-r2.json')
    inputs=jread(REVIEW/'author-v2-inputs/inputs.json');oracle=jread(REVIEW/'author-v2-inputs/oracle.json');gaps=jread(REVIEW/'author-v2-inputs/gaps.json')
    ids=[x['id'] for x in gaps['items']+gaps['additionalProductionRestoreCases']]
    assert len(ids)==len(set(ids))==114
    assert [x['id'] for x in old['items']]==[x['id'] for x in new['items']]==[x['id'] for x in programs['items']]==ids
    obs={x['id']:x for x in inputs['observations']};exp={x['id']:x for x in oracle['observations']}
    errors=[];counts={};rows=[]
    for original,item,p in zip(old['items'],new['items'],programs['items']):
        # Examine every complete field of inherited per-ID material.
        transformed={'proposalInvoice','pureMathematicalProgram','proposalBinder'}
        assert {k:v for k,v in item.items() if k not in transformed}=={k:v for k,v in original.items() if k not in transformed}
        invoice=item['proposalInvoice'];o=obs[item['id']]
        assert invoice['amount']==p['amount'] and invoice['paidPrefix']==p['paidPrefix'] and invoice['firstLimit']==p['firstLimit']
        assert invoice['programSha256']==p['programSha256'] and invoice['eventCount']==p['programEventCount']
        assert invoice['H01Required'] and 'H01' in p['requiredScheduleGroups']
        assert p['actualSameIssueAuthority']==dict.fromkeys(('limits','usage','issuer','jobOrSourcePermission'))
        assert all(p['independentMathematicalChecks'].values())
        assert item['datasetId']==o['datasetId'] and item['operation']==o['operation'] and item['declaredInputProjectionSha256']==o['projectionSha256']
        assert p['programRecipe']['parameters']==o['parameters']
        assert pointer(inputs,p['programRecipe']['observationPointer'])==o
        assert pointer(oracle,p['programRecipe']['independentExpectedPointer'])==exp[item['id']]['expected']
        raw=inputs['datasets'][o['datasetId']]
        raw_body=raw.get('input',raw)
        sample_shape=type(raw_body.get('records',[None])[0]).__name__ if raw_body.get('records') else None
        for origin in p['fieldOrigins']:
            counts[origin['inputState']]=counts.get(origin['inputState'],0)+1
            ptr=origin.get('inputPointer','')
            if origin['inputState'] in ('supplied','explicit-None','explicit-empty') and ptr.startswith('/datasets/'):
                try:pointer(inputs,ptr)
                except (KeyError,IndexError,ValueError,TypeError) as e:
                    errors.append({'id':p['id'],'fieldOrigin':origin,'failure':type(e).__name__,'rawRecordsRowType':sample_shape})
        rows.append({'id':item['id'],'operation':o['operation'],'allInheritedFieldsUnchanged':True,'fullFeeFieldsBound':True,'events':p['programEventCount'],'firstLimit':p['firstLimit'],'originCount':len(p['fieldOrigins'])})
    save('inventory',{'IDs':114,'allCompletePerIdFieldsReadAndCompared':True,'eventCount':sum(x['events'] for x in rows),
       'inputStates':counts,'originErrorCount':len(errors),'originErrors':errors,'items':rows})

def recompute(seed):
    r=import_ref();inputs=jread(REVIEW/'author-v2-inputs/inputs.json');oracle=jread(REVIEW/'author-v2-inputs/oracle.json')
    programs=jread(REF/'all114-fee-programs-r2.json')['items'];obs={x['id']:x for x in inputs['observations']};exp={x['id']:x for x in oracle['observations']}
    code=sha((REF/'reference.py').read_bytes());rows=[];diffs=[]
    for p in programs:
        o=obs[p['id']];e=exp[p['id']]['expected'];actual,_=r.make_program(o,inputs['datasets'][o['datasetId']],e.get('conditionalBusinessExpected',e.get('businessMath')),code)
        # Complete regenerated mathematical fields, not merely SHA/count/amount.
        changes=[k for k,v in actual.items() if k!='events' and p.get(k)!=v]
        # JSON normalizes tuples in held handles/first requests.
        changes=[k for k in changes if json.loads(json.dumps(actual[k]))!=p.get(k)]
        if changes:diffs.append({'id':p['id'],'fields':changes})
        events=actual['events'];demand={w:{k:0 for k in c if k not in ('objects','scalar')} for w,c in actual['caps'].items()}
        live={w:{'objects':0,'scalar':0} for w in demand};peak=json.loads(json.dumps(live));held={};ever=set();first=None
        h=slots=0;hpeak={'objects':0,'scalar':0}
        for ix,event in enumerate(events,1):
            w=event['wallet'];assert ix==event['ordinal']
            attempted={k:demand[w][k]+v for k,v in event['charges'].items()}
            hold=event['hold']
            if hold:
                name,ob,sc=hold;assert name not in ever;ever.add(name)
                attempted.update(objects=live[w]['objects']+ob,scalar=live[w]['scalar']+sc)
            domain=next((d for d in r.DOMAINS if d in attempted and attempted[d]>actual['caps'][w][d]),None)
            if first is None and domain:first=(ix,w,domain)
            for d,v in event['charges'].items():demand[w][d]+=v
            if hold:
                held[name]=(w,ob,sc)
                if not name.startswith('control') and name!='receipt':h+=1;slots+=ob
                live[w]['objects']+=ob;live[w]['scalar']+=sc
            if event['release']:
                owner,ob,sc=held.pop(event['release']);assert owner==w
                if event['release'].startswith('control'):assert event['action']=='terminal cleanup control'
                live[w]['objects']-=ob;live[w]['scalar']-=sc
            for d in ('objects','scalar'):
                assert live[w][d]>=0;peak[w][d]=max(peak[w][d],live[w][d]);hpeak[d]=max(hpeak[d],sum(x[d] for x in live.values()))
            assert event['requiredPrefix']==demand[w] and event['live']==live[w] and event['peak']==peak[w]
            assert event['wholeOwnerHLive']=={d:sum(x[d] for x in live.values()) for d in ('objects','scalar')}
        assert demand==actual['amount'] and peak==actual['peak'] and hpeak==actual['wholeOwnerHRequiredPeak']
        assert (h,slots)==(actual['finalization']['handles'],actual['finalization']['cumulativeSlots'])
        assert first==((actual['firstLimit']['event'],actual['firstLimit']['wallet'],actual['firstLimit']['domain']) if actual['firstLimit'] else None)
        rows.append({'id':p['id'],'programSha256':actual['programSha256'],'events':len(events),'amountSha256':r.sha(r.canonical(actual['amount'])),'fullFieldsEqual':not changes,'first':first})
    save('recompute-'+seed,{'seed':os.environ.get('PYTHONHASHSEED'),'IDCount':len(rows),'eventCount':sum(x['events'] for x in rows),'differences':diffs,'allFullFieldsMatch':not diffs,'items':rows})

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='integrity':integrity()
    elif mode=='static':static()
    elif mode=='inventory':inventory()
    elif mode=='recompute':recompute(sys.argv[2])
    else:raise ValueError('unknown review mode')
