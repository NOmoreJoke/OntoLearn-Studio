"""Independent R3 delta verifier; only new reviewer evidence is writable."""
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
REF=SPEC/'charge-reference-v3'
BASE='8d703858a9e7777e0086057032aea280316e49c1'
CAND='ebd3e009a9588e4019880a34a3e8096f6f61d025'
HEAD='4699bd2b08178302beaf1660e7c0724d35ef8177'
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
    calls.append({'argv':argv,'cwd':str(ROOT),'exit':p.returncode,
                  'stdout':{'bytes':len(p.stdout),'sha256':sha(p.stdout),'opaqueOnly':True} if opaque else blob(p.stdout),'stderr':blob(p.stderr)})
    assert p.returncode==0,(argv,p.stderr)
    return p.stdout
def save(label,value):
    value['subprocessCommands']=calls
    (HERE/('independent-r3-'+label+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in value.items() if k not in ('members','subprocessCommands','items','sources','modules')},ensure_ascii=False,indent=2))
def integrity():
    manifest=load(HERE/'artifact-manifest-r3.json')
    expected=manifest['members']+[{'path':str((HERE/'artifact-manifest-r3.json').relative_to(ROOT)),'bytes':38854,'sha256':'20814a8d82f8eeeb94699d92941ea7daa00b72c8220c5979227daeb90cf44519'},
      {'path':str((HERE/'r3-author-process-receipt.json').relative_to(ROOT)),'bytes':77971,'sha256':'be199aeb1a07ac72a4eb90911d5df8f0ae1126ebc23a5b07c1ab9b2ba34c9029'}]
    rows=[]
    for x in expected:
        raw=(ROOT/x['path']).read_bytes();git=call(['git','show',HEAD+':'+x['path']],True)
        assert raw==git and (len(raw),sha(raw))==(x['bytes'],x['sha256']),x['path']
        rows.append({**x,'currentEqualsGit':True,'opaqueOnly':True})
    old=[]
    for part in call(['git','ls-tree','-rz',BASE,'--',*PREFIX]).split(b'\0'):
        if not part:continue
        meta,path=part.split(b'\t',1);name=path.decode();raw=(ROOT/name).read_bytes()
        git=call(['git','cat-file','blob',meta.split()[2].decode()],True)
        assert raw==git,name
        old.append(name)
    delta=call(['git','diff','--name-status','-z',BASE,HEAD]).decode().rstrip('\0').split('\0')
    assert all(delta[i]=='A' and delta[i+1].startswith(PREFIX) for i in range(0,len(delta),2))
    process=call(['git','diff','--name-only',CAND,HEAD]).decode().splitlines()
    assert process==[str((HERE/'r3-author-process-receipt.json').relative_to(ROOT))]
    ag=(ROOT/'AGENTS.md').read_bytes();assert (len(ag),sha(ag))==(15147,'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4')
    assert call(['git','rev-parse','HEAD']).decode().strip()==HEAD
    assert not call(['git','diff','--cached','--name-only'])
    static=[]
    for path in sorted(REF.glob('*.py')):
        tree=ast.parse(path.read_text());imports=[];writes=[];dynamic=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
            elif isinstance(n,ast.ImportFrom):imports.append(n.module)
            elif isinstance(n,ast.Call):
                f=ast.unparse(n.func)
                if f.split('.')[-1] in ('write_text','write_bytes','open','unlink','mkdir'):writes.append({'line':n.lineno,'call':ast.unparse(n)})
                if f in ('exec','eval','__import__'):dynamic.append({'line':n.lineno,'call':f})
        assert not dynamic
        static.append({'path':str(path.relative_to(ROOT)),'imports':imports,'writes':writes,'dynamic':dynamic})
    assert not next(x for x in static if x['path'].endswith('/reference.py'))['writes']
    assert not next(x for x in static if x['path'].endswith('/audit_execution_r3.py'))['writes']
    assert (REF/'test_reference.py').read_bytes()==(SPEC/'charge-reference-v2/test_reference.py').read_bytes()
    save('integrity',{'fixedHEAD':HEAD,'candidate':CAND,'revisionBase':BASE,'memberCount':len(rows),'members':rows,'all189CurrentGitSHA':True,
      'oldCount':len(old),'all130OldUnchanged':len(old)==130,'newCount':len(delta)//2,'deltaStatusPaths':delta,'processDelta':process,
      'AGENTS':{'bytes':len(ag),'sha256':sha(ag)},'indexEmpty':True,'typedGoldenBytesUnchanged':True,'modules':static})

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

def recompute(seed):
    sys.path.insert(0,str(REF));r=importlib.import_module('reference')
    inputs=load(HERE/'author-v2-inputs/inputs.json');oracle=load(HERE/'author-v2-inputs/oracle.json')
    obs={x['id']:x for x in inputs['observations']};exp={x['id']:x for x in oracle['observations']}
    programs=load(REF/'all114-fee-programs-r3.json')['items'];table=load(SPEC/'per-id-r3.json')['items'];old=load(SPEC/'per-id-r2.json')['items']
    rows=[];code=sha((REF/'reference.py').read_bytes());assert len(programs)==114
    for p,row,previous in zip(programs,table,old):
        assert p['id']==row['id']==previous['id']
        assert {k:v for k,v in row.items() if k not in ('proposalInvoice','pureMathematicalProgram','proposalBinder')}=={k:v for k,v in previous.items() if k not in ('proposalInvoice','pureMathematicalProgram','proposalBinder')}
        ob=obs[p['id']];e=exp[p['id']]['expected']
        actual,_=r.make_program(ob,inputs['datasets'][ob['datasetId']],e.get('conditionalBusinessExpected',e.get('businessMath')),code)
        changes=[k for k,v in actual.items() if k not in ('events','executionEvents') and json.loads(json.dumps(v))!=p.get(k)]
        assert not changes,(p['id'],changes)
        ana=replay(actual,'events');exe=replay(actual,'executionEvents');children,projection=receipt(actual)
        assert projection==ob['projectionSha256']
        if row['predictedAllocation'].get('children') is not None:assert children==row['predictedAllocation']['children']
        assert row['proposalInvoice']['amount']==actual['amount'] and row['proposalInvoice']['paidPrefix']==actual['paidPrefix']
        assert all(actual['independentMathematicalChecks'].values())
        rows.append({'id':p['id'],'analysis':ana,'execution':exe,'programSha256':actual['programSha256'],'executionSha256':actual['executionSha256'],'receiptSha256':actual['finalization']['receiptSha256'],'firstError':actual['firstError'],'fullFieldsEqual':True})
    failures=load(REF/'complete-failure-programs-r3.json')['cases'];original=load(HERE/'independent-r2-adversarial.json')['cases']
    assert [x['input'] for x in failures]==[x['input'] for x in original]
    for c in failures:
        data=c['input'];label=c['id'];ob={'id':label,'datasetId':label,'operation':'profile','parameters':{},'projectionSha256':sha(json.dumps(data,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode())}
        actual,_=r.make_program(ob,data,{'rdfsAdded':[],'customOutput':[]},code)
        assert json.loads(json.dumps(actual))==c['invoice'],label
        ana=replay(actual,'events');exe=replay(actual,'executionEvents');receipt(actual)
        assert actual['state']=='failed' and actual['finalization']['H01Paid']
        rows.append({'id':label,'analysis':ana,'execution':exe,'programSha256':actual['programSha256'],'executionSha256':actual['executionSha256'],'receiptSha256':actual['finalization']['receiptSha256'],'firstError':actual['firstError'],'fullFieldsEqual':True})
    save('recompute-'+seed,{'seed':os.environ.get('PYTHONHASHSEED'),'fixedCount':114,'originalErrorCases':6,'analysisFixedEvents':sum(x['analysis']['events'] for x in rows[:114]),'executionFixedEvents':sum(x['execution']['events'] for x in rows[:114]),'allCompleteResultsMatch':True,'bothTapesIndependentlyReplayed':True,'all120ReceiptsDecoded':True,'items':rows})

def adversarial_audit():
    data=load(HERE/'independent-r3-adversarial.json');rows=[]
    for c in data['cases']:
        if not c['returnedInvoice']:
            rows.append({'id':c['id'],'noInvoice':True,'exception':c['error']});continue
        p=c['invoice'];a=replay(p,'events');e=replay(p,'executionEvents');receipt(p)
        rows.append({'id':c['id'],'loweredCaps':c['loweredMathematicalCaps'],'analysis':a,'execution':e,'state':p['state'],'firstError':p['firstError'],'receiptDecoded':True})
        if c['id']=='last-head-bound-literal-subject':
            assert p['state']=='failed' and p['firstError']['phase']=='evaluate:head' and p['paidPrefix']['M0']['output_bytes']==0
            assert p['paidPrefix']['M0']['head_occurrences']==2 and p['paidPrefix']['M0']['firings']==0 and p['paidPrefix']['M0']['trace_items']==1
        if c['loweredMathematicalCaps'] and c['loweredMathematicalCaps'][0][0]=='C0':
            assert p['firstError']['event']==2 and not p['finalization']['H01Paid']
            assert not any(any(v.values()) for v in p['paidPrefix'].values()) and not p['terminalRetainedHandles']
    save('adversarial-audit',{'independentArtifactReplayOnly':True,'completeInvoicesAudited':sum(c['returnedInvoice'] for c in data['cases']),
       'exceptionCases':sum(not c['returnedInvoice'] for c in data['cases']),'newAliasBoundary':data['newSourceAliasBoundary'],'items':rows})

if __name__=='__main__':
    if sys.argv[1]=='integrity':integrity()
    elif sys.argv[1]=='recompute':recompute(sys.argv[2])
    elif sys.argv[1]=='adversarial-audit':adversarial_audit()
    else:raise ValueError('unknown review mode')
