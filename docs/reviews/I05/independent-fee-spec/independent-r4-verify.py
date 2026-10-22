"""Independent R4 checks; no old review module is imported or executed."""
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
HERE=Path(__file__).parent
SPEC=ROOT/'docs/iterations/I05/independent-fee-spec'
REF=SPEC/'charge-reference-v4'
BASE='6bb1c1e5a4250468f894033e42864d480ccdb815'
CAND='f6b886208839037aeae93947549d32fc3ddc6b89'
HEAD='29705204c9f8274d7ab17433bd6ac3094461244b'
PREFIX=('docs/iterations/I05/independent-fee-spec/','docs/reviews/I05/independent-fee-spec/')
DOMAINS=('work','input_bytes','output_bytes','trace_items','firings','head_occurrences','bindings','scan_copy','hash_bytes','objects','scalar')
REASONS=('NONE','INVALID_RULE','INVALID_LITERAL_LEXICAL','UNSUPPORTED_LITERAL_DATATYPE','UNSUPPORTED_NONFINITE_LITERAL','RULE_COMPARISON_TYPE_MISMATCH','RESOURCE_LIMIT','INTERNAL_MATHEMATICAL_CHECK')
calls=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def load(p):return json.loads(p.read_bytes())
def blob(b):return {'bytes':len(b),'sha256':sha(b),'utf8':b.decode(),'base64':base64.b64encode(b).decode()}
def call(argv,opaque=False):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True,check=False)
    calls.append({'argv':argv,'cwd':str(ROOT),'exit':p.returncode,'stdout':{'bytes':len(p.stdout),'sha256':sha(p.stdout),'opaqueOnly':True} if opaque else blob(p.stdout),'stderr':blob(p.stderr)})
    assert p.returncode==0,(argv,p.stderr)
    return p.stdout
def save(name,data):
    data['subprocessCommands']=calls
    (HERE/('independent-r4-'+name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k not in ('members','modules','items','subprocessCommands','oldPaths','delta')},ensure_ascii=False,indent=2))

def replay(p,key):
    events=p[key];execution=key=='executionEvents'
    used={w:{d:0 for d in DOMAINS[:9]} for w in p['caps']}
    live={w:dict(objects=0,scalar=0) for w in p['caps']};peak=json.loads(json.dumps(live))
    held={};ever=set();h=slots=0;hpeak=dict(objects=0,scalar=0);stopped=False;rejected=None
    for ix,e in enumerate(events,1):
        assert e['ordinal']==ix
        w=e['wallet'];hold=e.get('hold');release=e.get('release');charges=e['charges']
        assert all(type(n) is int and n>=0 for n in charges.values())
        if e.get('debited') is False:
            assert execution and not stopped and not charges and not hold and not release
            attempt={d:used[w][d]+n for d,n in e['attemptedCharges'].items()}
            if e.get('attemptedHold'):
                _,o,s=e['attemptedHold'];attempt.update(objects=live[w]['objects']+o,scalar=live[w]['scalar']+s)
            first=next(d for d in DOMAINS if d in attempt and attempt[d]>p['caps'][w][d])
            assert first==e['failure']['domain'] and e['failure']['before']==used[w] and e['failure']['liveBefore']==live[w]
            assert e['failure']==p['firstError'];stopped=True;rejected=ix
        else:
            if execution and stopped:assert not charges and not hold and e.get('cleanupPrepaidBy')=='H01'
            attempt={d:used[w][d]+n for d,n in charges.items()}
            if hold:
                name,o,s=hold;assert name not in ever and min(o,s)>=0
                attempt.update(objects=live[w]['objects']+o,scalar=live[w]['scalar']+s)
            if execution:assert all(n<=p['caps'][w][d] for d,n in attempt.items())
            for d,n in charges.items():used[w][d]+=n
            if hold:
                ever.add(name);held[name]=(w,o,s)
                if name!='receipt' and not name.startswith('control'):h+=1;slots+=o
                live[w]['objects']+=o;live[w]['scalar']+=s
            if release:
                owner,o,s=held.pop(release);assert owner==w
                if release.startswith('control'):assert e['action']=='terminal cleanup control'
                live[w]['objects']-=o;live[w]['scalar']-=s
            for d in ('objects','scalar'):peak[w][d]=max(peak[w][d],live[w][d])
            if execution and e.get('semanticError'):
                assert not stopped and e['failure']==p['firstError'];stopped=True
        assert used[w]==e['requiredPrefix'] and live[w]==e['live'] and peak[w]==e['peak']
        total={d:sum(v[d] for v in live.values()) for d in ('objects','scalar')}
        for d in total:hpeak[d]=max(hpeak[d],total[d])
        assert e['wholeOwnerHLive']==total and e['wholeOwnerHPeak']==hpeak
    if execution:
        assert used==p['paidPrefix'] and peak==p['paidPrefixPeak'] and live==p['terminalLive'] and hpeak==p['paidWholeOwnerHPeak']
        assert {k:list(v) for k,v in held.items()}==json.loads(json.dumps(p['terminalRetainedHandles']))
        assert (h,slots)==(p['executionLifetime']['handles'],p['executionLifetime']['slots'])
        if p['firstError']:assert stopped and not held and all(not any(v.values()) for v in live.values())
        assert sha(canonical(events))==p['executionSha256']
    else:
        assert used==p['amount'] and peak==p['peak'] and hpeak==p['wholeOwnerHRequiredPeak']
        assert (h,slots)==(p['finalization']['handles'],p['finalization']['cumulativeSlots'])
        assert sha(canonical(events))==p['programSha256']
    return {'events':len(events),'dataHandles':h,'cumulativeSlots':slots,'rejectedExecutionOrdinal':rejected}

def receipt(p):
    raw=bytes.fromhex(p['finalization']['receiptHex']);position=0
    def take(n):
        nonlocal position
        out=raw[position:position+n];assert len(out)==n;position+=n;return out
    def uint(n):return int.from_bytes(take(n),'big')
    def text():return take(uint(4)).decode()
    assert take(5)==b'IFR3\3' and text()==p['id'];projection=take(32).hex()
    h,s=uint(4),uint(8);assert (h,s)==(p['finalization']['handles'],p['finalization']['cumulativeSlots']) and take(2)==b'\0\0'
    wallets=[]
    for _ in range(uint(4)):
        w=text();assert w in p['caps'] and w not in wallets;wallets.append(w)
        for d in DOMAINS:assert uint(8)==(p['paidPrefixPeak'][w][d] if d in ('objects','scalar') else p['paidPrefix'][w][d])
    assert set(wallets)==set(p['caps'])
    children=[];n=uint(4);totals=(16777216,262144,262144,8192,1024,16384,1024)
    for i in range(n):
        rid=text();present,ordinal,disabled=uint(1),uint(4),uint(1)
        limits=[uint(8) for _ in range(17)]
        assert limits[:7]==[v//n+int(i<v%n) for v in totals]
        assert limits[7:]==[16384,65536,4096,16384,32768,100,16,32,16,64]
        children.append({'rule_id':rid if present else None,'definition_ordinal':None if ordinal==0xffffffff else ordinal,'disabled':bool(disabled),'limits':dict(zip(DOMAINS[:7]+('term_bytes','source_bytes','digits','integer_bits','temporary_bits','rules','when','comparisons','heads','variables'),limits))})
    status,reason,ordinal=uint(1),REASONS[uint(2)],uint(8)
    assert take(32).hex()==p['executionSha256'];body=raw[:position];footer=take(32)
    assert position==len(raw) and hashlib.sha256(b'I05-FEE-RECEIPT/3\0'+body+b'\0'*32).digest()==footer
    err=p['firstError'];assert reason==(err['reason'] if err else 'NONE') and ordinal==(err['event'] if err else 0)
    assert status==(2 if err and reason=='RESOURCE_LIMIT' else 3 if err and err['kind']=='internal' else 1 if err else 0)
    f=14+12*len(wallets)+20*n
    assert f==p['finalization']['fields'] and p['finalization']['vector']=={'work':f+3*h+s+4*len(raw),'scan_copy':4*len(raw),'hash_bytes':18+len(raw)}
    assert len(raw)==p['finalization']['receiptBytes'] and sha(raw)==p['finalization']['receiptSha256']
    return children,projection



def integrity():
    manifest=load(HERE/'artifact-manifest-r4.json')
    expected=manifest['members']+[{'path':str((HERE/'artifact-manifest-r4.json').relative_to(ROOT)),'bytes':55402,'sha256':'a3b6d25cfc6541dfea96cfc29659db440b6394b1f143ebe6574410587ccd8516'},
      {'path':str((HERE/'r4-author-process-receipt.json').relative_to(ROOT)),'bytes':106221,'sha256':'6f7f53ced437ce874d00707287b66906622c2175950a02ea997d427319d44562'}]
    members=[]
    for row in expected:
        raw=(ROOT/row['path']).read_bytes();git=call(['git','show',HEAD+':'+row['path']],True)
        assert raw==git and (len(raw),sha(raw))==(row['bytes'],row['sha256']),row['path']
        members.append({**row,'currentEqualsGit':True,'opaqueOnly':True})
    old=[]
    for item in call(['git','ls-tree','-rz',BASE,'--',*PREFIX]).split(b'\0'):
        if not item:continue
        meta,path=item.split(b'\t',1);name=path.decode();raw=(ROOT/name).read_bytes()
        assert raw==call(['git','cat-file','blob',meta.split()[2].decode()],True),name
        old.append(name)
    delta=call(['git','diff','--name-status','-z',BASE,HEAD]).decode().rstrip('\0').split('\0')
    assert len(old)==203 and len(delta)//2==66
    assert all(delta[i]=='A' and delta[i+1].startswith(PREFIX) for i in range(0,len(delta),2))
    assert call(['git','diff','--name-only',CAND,HEAD]).decode().splitlines()==[str((HERE/'r4-author-process-receipt.json').relative_to(ROOT))]
    assert call(['git','rev-parse','HEAD']).decode().strip()==HEAD
    assert not call(['git','diff','--cached','--name-only'])
    guidance=(ROOT/'AGENTS.md').read_bytes();assert (len(guidance),sha(guidance))==(15147,'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4')
    modules=[]
    for p in sorted(REF.glob('*.py')):
        tree=ast.parse(p.read_text());imports=[];writes=[];dynamic=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
            elif isinstance(n,ast.ImportFrom):imports.append(n.module)
            elif isinstance(n,ast.Call):
                f=ast.unparse(n.func)
                if f.split('.')[-1] in ('write_text','write_bytes','open','unlink','mkdir'):writes.append({'line':n.lineno,'call':ast.unparse(n)})
                if f in ('exec','eval','__import__'):dynamic.append({'line':n.lineno,'call':f})
        assert not dynamic
        modules.append({'path':str(p.relative_to(ROOT)),'imports':imports,'writes':writes,'dynamic':dynamic})
    assert not next(x for x in modules if x['path'].endswith('/reference.py'))['writes']
    save('integrity',{'fixedHEAD':HEAD,'candidate':CAND,'revisionBase':BASE,'members':members,'memberCount':len(members),'all269CurrentGitSha':True,'oldCount':len(old),'all203OldUnchanged':True,'oldPaths':old,'newCount':len(delta)//2,'delta':delta,'modules':modules,'guidance':{'bytes':len(guidance),'sha256':sha(guidance)},'indexEmpty':True})

def independent_delta(data,p):
    body=data.get('input',data);definitions=body.get('definitions',body.get('rules',[]))
    work,scan,events=4,0,4;seen=[]
    def text(value):
        if value is None:return 1,0,1
        size=len(value.encode());return 2+len(value)+size,size,4
    values=[]
    for d in definitions:
        work+=5;events+=5
        values.append(d['rule_id'])
        for previous in seen:
            n=len(previous.encode())+len(d['rule_id'].encode());work+=n;scan+=n;events+=1
        seen.append(d['rule_id'])
        values.extend(d.get(k) for k in ('revision','definition_digest','definitionJsonValueSha256','policy'))
        if d.get('source') is not None:
            fields=('ref','path','pointer','sha256') if 'definitions' in body else ('reference','digest','revision','text')
            values.extend(d['source'][k] for k in fields)
    values.extend(body.get('disabled_rule_ids',[]))
    for value in values:
        a,b,c=text(value);work+=a;scan+=b;events+=c
    rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    def triple(row):return [row[k] for k in ('subject','predicate','object')] if type(row) is dict else row
    def iri(t):
        if type(t) is dict:return t['lexical_form'] if t.get('kind')=='iri' else None
        return t.strip('<>') if not t.startswith(('?','"')) else None
    raw=[x['triple'] for sec in ('asserted','ontology') for x in body[sec]] if 'input' in data else body.get('records',[])
    classes={iri(triple(x)[0]) for x in raw if iri(triple(x)[1])==rdf and iri(triple(x)[2]) in ('http://www.w3.org/2002/07/owl#Class','http://www.w3.org/2000/01/rdf-schema#Class')}
    extra={}
    for i,d in enumerate(sorted(definitions,key=lambda d:d['rule_id'])):
        vector={'work':0,'scan_copy':0,'eventShift':0}
        for row in d['when']:
            parts=triple(row)
            if iri(parts[1])!=rdf:continue
            target=iri(parts[2]);assert target in classes
            size=sum(len(c.encode())+len(target.encode()) for c in classes)
            vector['work']+=size+2;vector['scan_copy']+=size;vector['eventShift']+=len(classes)+2
        extra['M'+str(i)]=vector
        if 'R16-'+str(i) in p['amount']:extra['R16-'+str(i)]=vector.copy()
    return {'work':work,'scan_copy':scan,'hash_bytes':0,'eventShift':events},extra

def recompute(seed):
    sys.path.insert(0,str(REF));r=importlib.import_module('reference')
    inputs=load(HERE/'author-v2-inputs/inputs.json');oracle=load(HERE/'author-v2-inputs/oracle.json')
    obs={x['id']:x for x in inputs['observations']};exp={x['id']:x for x in oracle['observations']}
    programs=load(REF/'all114-fee-programs-r4.json')['items'];table=load(SPEC/'per-id-r4.json')['items'];oldtable=load(SPEC/'per-id-r3.json')['items']
    oldprograms={x['id']:x for x in load(SPEC/'charge-reference-v3/all114-fee-programs-r3.json')['items']}
    deltas=load(REF/'metadata-delta-r4.json')['items'];rows=[];code=sha((REF/'reference.py').read_bytes())
    assert code=='bc47b16bf528b973aeebcc0be4a103bf00acbf0f351485f5370510817bf1467c'
    totals={'metadataWork':0,'metadataScan':0,'metadataEvents':0,'whenWork':0,'whenScan':0,'whenEvents':0}
    for p,row,old,d in zip(programs,table,oldtable,deltas):
        assert p['id']==row['id']==old['id']==d['id']
        assert {k:v for k,v in row.items() if k not in ('proposalInvoice','pureMathematicalProgram','proposalBinder')}=={k:v for k,v in old.items() if k not in ('proposalInvoice','pureMathematicalProgram','proposalBinder')}
        ob=obs[p['id']];e=exp[p['id']]['expected'];data=inputs['datasets'][ob['datasetId']]
        actual,_=r.make_program(ob,data,e.get('conditionalBusinessExpected',e.get('businessMath')),code)
        changes=[k for k,v in actual.items() if k not in ('events','executionEvents') and json.loads(json.dumps(v))!=p.get(k)]
        assert not changes,(p['id'],changes)
        ana=replay(actual,'events');exe=replay(actual,'executionEvents');children,projection=receipt(actual)
        assert projection==ob['projectionSha256']
        if row['predictedAllocation'].get('children') is not None:assert children==row['predictedAllocation']['children']
        assert row['proposalInvoice']['amount']==p['amount'] and row['proposalInvoice']['paidPrefix']==p['paidPrefix']
        meta,when=independent_delta(data,p)
        assert meta==d['metadataAdditionalVector'] and when==d['whenClassAdditionalVectors']
        before=oldprograms[p['id']]
        for wallet,amount in p['amount'].items():
            for domain,value in amount.items():assert value-before['amount'][wallet][domain]==(meta.get(domain,0) if wallet=='C0' else when.get(wallet,{}).get(domain,0)),(p['id'],wallet,domain)
        assert p['caps']==before['caps'] and p['wholeOwnerHRequiredPeak']==before['wholeOwnerHRequiredPeak']
        shift=meta['eventShift']+sum(x['eventShift'] for x in when.values())
        assert p['programEventCount']-before['programEventCount']==p['executionEventCount']-before['executionEventCount']==shift
        if p['firstError']:assert p['firstError']['event']==before['firstError']['event']+shift
        totals['metadataWork']+=meta['work'];totals['metadataScan']+=meta['scan_copy'];totals['metadataEvents']+=meta['eventShift']
        totals['whenWork']+=sum(x['work'] for x in when.values());totals['whenScan']+=sum(x['scan_copy'] for x in when.values());totals['whenEvents']+=sum(x['eventShift'] for x in when.values())
        rows.append({'id':p['id'],'analysis':ana,'execution':exe,'programSha256':p['programSha256'],'executionSha256':p['executionSha256'],'receiptSha256':p['finalization']['receiptSha256'],'firstError':p['firstError'],'fullFieldsEqual':True,'independentDelta':{'metadata':meta,'when':when}})
    cases=load(REF/'complete-entry-programs-r4.json')['cases'];assert len(cases)==27
    for c in cases:
        label,data=c['id'],c['input'];ob={'id':label,'datasetId':label,'operation':'profile','parameters':{},'projectionSha256':sha(json.dumps(data,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode())}
        business={'rdfsAdded':[],'customOutput':[]}
        if label in ('variable-property-object-allowed','valid-id-boundary'):business['customOutput']=[[{'kind':'iri','value':'urn:s'},{'kind':'iri','value':'urn:score'},{'kind':'literal','lexical':'1','datatype':r.XSD+'integer'}]]
        if label in ('fixed-class-variable-subject-allowed','fixed-when-class-allowed'):business['customOutput']=[[{'kind':'iri','value':'urn:s'},{'kind':'iri','value':r.RDF+'type'},{'kind':'iri','value':'urn:C'}]]
        actual,_=r.make_program(ob,data,business,code);assert json.loads(json.dumps(actual))==c['invoice'],label
        ana=replay(actual,'events');exe=replay(actual,'executionEvents');receipt(actual)
        if actual['entryMetadata']['state']=='rejected':assert set(actual['caps'])=={'C0'} and actual['finalization']['fields']==26 and not actual['entryMetadata']['allocationStarted']
        rows.append({'id':label,'analysis':ana,'execution':exe,'programSha256':actual['programSha256'],'executionSha256':actual['executionSha256'],'receiptSha256':actual['finalization']['receiptSha256'],'firstError':actual['firstError'],'fullFieldsEqual':True})
    assert len(rows)==141
    save('recompute-'+seed,{'seed':os.environ.get('PYTHONHASHSEED'),'fixedCount':114,'completeEntryCases':27,'all141CompleteFieldsMatch':True,'allDoubleTapesReplayed':True,'all141IFR3Decoded':True,'fixedAnalysisEvents':sum(x['analysis']['events'] for x in rows[:114]),'fixedExecutionEvents':sum(x['execution']['events'] for x in rows[:114]),'independentDeltaTotals':totals,'items':rows})

if __name__=='__main__':
    if sys.argv[1]=='integrity':integrity()
    elif sys.argv[1]=='recompute':recompute(sys.argv[2])
    else:raise ValueError('unknown review mode')
