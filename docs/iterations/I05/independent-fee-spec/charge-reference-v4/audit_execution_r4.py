"""Independent artifact arithmetic/receipt decoder. No reference/model imports."""
from pathlib import Path
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
DOMAINS=('work','input_bytes','output_bytes','trace_items','firings','head_occurrences','bindings','scan_copy','hash_bytes','objects','scalar')
REASONS=('NONE','INVALID_RULE','INVALID_LITERAL_LEXICAL','UNSUPPORTED_LITERAL_DATATYPE','UNSUPPORTED_NONFINITE_LITERAL','RULE_COMPARISON_TYPE_MISMATCH','RESOURCE_LIMIT','INTERNAL_MATHEMATICAL_CHECK')
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()

def replay(p,execution):
    used={w:{d:0 for d in DOMAINS[:9]} for w in p['caps']}
    live={w:{'objects':0,'scalar':0} for w in p['caps']};peak=json.loads(json.dumps(live))
    active={};seen=set();handles=slots=0;hpeak={'objects':0,'scalar':0}
    events=p['executionEvents'] if execution else p['events']
    stopped=False
    for index,e in enumerate(events,1):
        assert e['ordinal']==index
        w=e['wallet'];charges=e['charges'];hold=e['hold'];release=e['release']
        assert all(type(n) is int and n>=0 for n in charges.values())
        if e.get('debited') is False:
            assert execution and not stopped and not charges and not hold and not release
            attempted=e['attemptedCharges'];candidate={d:used[w][d]+n for d,n in attempted.items()}
            if e['attemptedHold']:
                _,o,s=e['attemptedHold'];candidate.update(objects=live[w]['objects']+o,scalar=live[w]['scalar']+s)
            d=next(d for d in DOMAINS if d in candidate and candidate[d]>p['caps'][w][d])
            assert d==e['failure']['domain'] and e['failure']==p['firstError']
            assert e['failure']['before']==used[w] and e['failure']['liveBefore']==live[w]
            stopped=True
        else:
            if execution and stopped:assert not charges and not hold and e.get('cleanupPrepaidBy')=='H01'
            attempt={d:used[w][d]+n for d,n in charges.items()}
            if hold:
                name,o,s=hold
                assert name not in seen and type(o) is int and type(s) is int and min(o,s)>=0
                attempt.update(objects=live[w]['objects']+o,scalar=live[w]['scalar']+s)
                if name!='receipt' and not name.startswith('control'):handles+=1;slots+=o
            if execution:assert all(n<=p['caps'][w][d] for d,n in attempt.items())
            for d,n in charges.items():used[w][d]+=n
            if hold:
                seen.add(name);active[name]=(w,o,s)
                for d,n in zip(('objects','scalar'),(o,s)):live[w][d]+=n;peak[w][d]=max(peak[w][d],live[w][d])
            if release:
                assert release in active
                if release.startswith('control'):assert e['action']=='terminal cleanup control'
                owner,o,s=active.pop(release)
                live[owner]['objects']-=o;live[owner]['scalar']-=s
            if execution and e.get('semanticError'):
                assert not stopped and e['failure']==p['firstError'];stopped=True
        assert e['requiredPrefix']==used[w] and e['live']==live[w] and e['peak']==peak[w]
        total={d:sum(x[d] for x in live.values()) for d in ('objects','scalar')}
        for d,n in total.items():hpeak[d]=max(hpeak[d],n)
        assert e['wholeOwnerHLive']==total and e['wholeOwnerHPeak']==hpeak
    if execution:
        assert used==p['paidPrefix'] and peak==p['paidPrefixPeak'] and live==p['terminalLive']
        assert {n:list(v) for n,v in active.items()}==p['terminalRetainedHandles']
        assert hpeak==p['paidWholeOwnerHPeak']
        assert handles==p['executionLifetime']['handles'] and slots==p['executionLifetime']['slots']
        if p['firstError']:assert stopped and not active and not any(any(x.values()) for x in live.values()) and p['noSuccessPrefix']
        assert digest(canonical(events))==p['executionSha256']
    else:
        assert used==p['amount'] and peak==p['peak'] and hpeak==p['wholeOwnerHRequiredPeak']
        assert digest(canonical(events))==p['programSha256']
        assert handles==p['finalization']['handles'] and slots==p['finalization']['cumulativeSlots']

def receipt(p):
    raw=bytes.fromhex(p['finalization']['receiptHex']);pos=0
    def take(n):
        nonlocal pos
        b=raw[pos:pos+n];assert len(b)==n;pos+=n;return b
    def uint(n):return int.from_bytes(take(n),'big')
    def text():return take(uint(4)).decode()
    assert take(5)==b'IFR3\3' and text()==p['id'];take(32)
    h=uint(4);s=uint(8);assert (h,s)==(p['finalization']['handles'],p['finalization']['cumulativeSlots'])
    assert take(2)==b'\0\0';wallets=[]
    for _ in range(uint(4)):
        w=text();wallets.append(w)
        for d in DOMAINS:assert uint(8)==(p['paidPrefixPeak'][w][d] if d in ('objects','scalar') else p['paidPrefix'][w][d])
    # Canonical artifact JSON sorts map keys; receipt preserves opening order.
    assert len(wallets)==len(set(wallets)) and set(wallets)==set(p['caps'])
    n=uint(4)
    children=[]
    for i in range(n):
        rid=text();present=uint(1);ordinal=uint(4);disabled=uint(1)
        assert present in (0,1) and disabled in (0,1)
        limits=[uint(8) for _ in range(17)]
        # An ENTRY error may precede opening any M wallet. Allocation values
        # already exist, while unopened wallets are not invented in the receipt.
        pools=(16777216,262144,262144,8192,1024,16384,1024)
        expected=[p['caps']['M'+str(i)][d] for d in DOMAINS[:7]] if 'M'+str(i) in p['caps'] else [v//n+int(i<v%n) for v in pools]
        assert limits[:7]==expected
        assert limits[7:]==[16384,65536,4096,16384,32768,100,16,32,16,64]
        children.append({'rule_id':rid if present else None,'definition_ordinal':ordinal if ordinal!=0xffffffff else None,'disabled':bool(disabled),'limits':dict(zip(DOMAINS[:7]+('term_bytes','source_bytes','digits','integer_bits','temporary_bits','rules','when','comparisons','heads','variables'),limits))})
    status=uint(1);reason=REASONS[uint(2)];ordinal=uint(8)
    assert take(32).hex()==p['executionSha256']
    footer=take(32);assert pos==len(raw)
    assert footer==hashlib.sha256(b'I05-FEE-RECEIPT/3\0'+raw[:-32]+b'\0'*32).digest()
    err=p['firstError'];assert reason==(err['reason'] if err else 'NONE') and ordinal==(err['event'] if err else 0)
    assert status==(2 if err and reason=='RESOURCE_LIMIT' else 3 if err and err['kind']=='internal' else 1 if err else 0)
    f=14+12*len(wallets)+20*n;assert f==p['finalization']['fields']
    assert p['finalization']['vector']=={'work':f+3*h+s+4*len(raw),'scan_copy':4*len(raw),'hash_bytes':18+len(raw)}
    assert len(raw)==p['finalization']['receiptBytes'] and digest(raw)==p['finalization']['receiptSha256']
    assert p['finalization']['staticProofBeforeExecution'] and p['finalization']['H01Paid']
    return children

def fee_encode(v):
    def framed(tag,b):return tag+len(b).to_bytes(4,'big')+b
    if v is None:return b'N'
    if type(v) is bool:return b'T' if v else b'F'
    if type(v) is int:return framed(b'I',hex(v).encode())
    if type(v) is str:return framed(b'S',v.encode())
    if type(v) is list:return b'A'+len(v).to_bytes(4,'big')+b''.join(fee_encode(x) for x in v)
    if type(v) is dict:
        if set(v)=={'integerHex'}:return fee_encode(int(v['integerHex'],16))
        if set(v)=={'encoding','bytes'} and v['encoding']=='hex':return framed(b'B',bytes.fromhex(v['bytes']))
        return b'R'+len(v).to_bytes(4,'big')+b''.join(fee_encode(k)+fee_encode(x) for k,x in v.items())
    raise AssertionError(type(v))

def metadata_cost(data):
    """Independent arithmetic table E00 on valid fixed JSON, not a matcher."""
    body=data.get('input',data);rules=body.get('definitions',body.get('rules',[]))
    work=4;scan=0;actions=4;seen=[]
    def text(v):
        if v is None:return (1,0,1)
        b=len(v.encode());return (2+len(v)+b,b,4)
    def add(v):
        nonlocal work,scan,actions
        w,s,n=text(v);work+=w;scan+=s;actions+=n
    for row in rules:
        work+=5;actions+=5 # mapping1, three sequence guards, source mapping1
        add(row['rule_id'])
        for previous in seen:
            n=len(previous.encode())+len(row['rule_id'].encode());work+=n;scan+=n;actions+=1
        seen.append(row['rule_id'])
        for k in ('revision','definition_digest','definitionJsonValueSha256','policy'):add(row.get(k))
        if row.get('source') is not None:
            fields=('ref','path','pointer','sha256') if 'definitions' in body else ('reference','digest','revision','text')
            for k in fields:add(row['source'][k])
        # Byte lengths and type bounds are checked separately by the full entry.
    for disabled in body.get('disabled_rule_ids',[]):add(disabled)
    return {'work':work,'scan_copy':scan,'hash_bytes':0,'eventShift':actions}

def when_class_cost(data):
    """Independent raw-declaration/RuleSpec field arithmetic, no graph engine."""
    body=data.get('input',data)
    def row(g):return [g[k] for k in ('subject','predicate','object')] if type(g) is dict else g
    def lex(t):
        if type(t) is dict:return t.get('lexical_form') if t.get('kind')=='iri' else None
        # Fixed raw JSON spells predicates/subjects as bare full IRIs and
        # objects as <IRI>; both are the already-declared binder forms.
        return t.strip('<>') if not t.startswith(('?','"')) else None
    rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    cls=('http://www.w3.org/2002/07/owl#Class','http://www.w3.org/2000/01/rdf-schema#Class')
    raw=[r['triple'] for section in ('asserted','ontology') for r in body.get(section,[])] if 'input' in data else body.get('records',[])
    classes=sorted({lex(row(g)[0]) for g in raw if lex(row(g)[1])==rdf and lex(row(g)[2]) in cls})
    rules=body.get('definitions',body.get('rules',[]));out={}
    for slot,definition in enumerate(sorted(rules,key=lambda d:d['rule_id'])):
        work=scan=events=0
        for g in definition['when']:
            if lex(row(g)[1])==rdf:
                target=lex(row(g)[2]);assert target is not None and target in classes
                n=sum(len(c.encode())+len(target.encode()) for c in classes)
                work+=2+n;scan+=n;events+=2+len(classes)
        out['M'+str(slot)]={'work':work,'scan_copy':scan,'eventShift':events}
    return out

def main():
    baseline=json.loads((HERE/'baseline-prefix-r4.json').read_text());complete=json.loads((HERE/'complete-entry-programs-r4.json').read_text())
    allp=[baseline]+[c['invoice'] for c in complete['cases']]
    for p in allp:replay(p,False);replay(p,True);receipt(p)
    assert baseline['programEventCount']==2455 and baseline['executionEventCount']==2455
    assert {w:v['work'] for w,v in baseline['paidPrefix'].items()}=={'C0':3278484+567,'ENTRY':176580,'G':185814,'M0':141562+262,'WIRE8M':0}
    assert baseline['paidPrefix']['M0']['scan_copy']==3867+60+64+72+64
    assert baseline['paidPrefix']['C0']['scan_copy']==2275119+271 and baseline['paidPrefix']['C0']['hash_bytes']==823438
    assert baseline['finalization']['handles']==8 and baseline['finalization']['cumulativeSlots']==149538
    assert baseline['finalization']['receiptBytes']==792 and baseline['finalization']['vector']['work']==152824
    assert baseline['wholeOwnerHRequiredPeak']=={'objects':149697,'scalar':6819815}
    material=json.loads((HERE/'baseline-fee-material-r4.json').read_text());encoded=fee_encode(material)
    assert encoded.hex()==(HERE/'baseline-fee-material-r4.bytes.hex').read_text().strip()
    assert len(encoded)==85953 and digest(encoded)=='5bc7b79b64ae371f95078a21eb152fb90e7884a1380764d2b9823a879bda9f8d'
    by={c['id']:c['invoice'] for c in complete['cases']}
    # Independent literal prefix accounts, with no allocation on metadata fail.
    p=by['nonstring-rule-id'];assert p['firstError']['event']==8 and p['executionEventCount']==10
    assert p['paidPrefix']['C0']['work']==26+4*249+5==1027
    assert p['finalization']['handles']==p['finalization']['cumulativeSlots']==0 and p['finalization']['fields']==26
    p=by['outer-input-not-mapping'];assert p['firstError']['event']==5 and p['paidPrefix']['C0']['work']==26+4*255+2==1048
    p=by['late-invalid-rule-id'];assert p['firstError']['event']==25 and p['paidPrefix']['C0']['work']==1178 and p['entryMetadata']['validatedRuleCount']==1 and not p['entryMetadata']['allocationStarted']
    assert by['duplicate-rule-id']['paidPrefix']['C0']['work']==1211
    assert by['rule-id-byte-plus-one']['firstError']['reason']=='RESOURCE_LIMIT' and by['rule-id-byte-plus-one']['paidPrefix']['C0']['work']==9272
    for label in ('variable-class-enabled','variable-class-disabled','variable-class-zero-match'):
        p=by[label];assert p['firstError']['phase']=='compile:head' and p['paidPrefix']['M0']['work']==1273
        # Independent schema framing: R header5 + definitions560 + Catalog96
        # + limits439 = 1100 bytes, 101 nodes -> INPUT work1201; static72.
        assert p['paidPrefix']['M0']['input_bytes']==5+560+96+439==1100 and p['paidPrefix']['M0']['head_occurrences']==0
        assert p['paidPrefix']['M0']['work']==1100+101+72
    assert by['variable-class-enabled']['firstError']['event']==86 and by['variable-class-disabled']['firstError']['event']==90
    assert by['fixed-class-variable-subject-allowed']['paidPrefix']['M0']['work']==11145
    assert by['variable-property-object-allowed']['paidPrefix']['M0']['work']==10433
    for label in ('variable-when-class-enabled','variable-when-class-disabled','variable-when-class-zero-match','undeclared-when-class','literal-when-class'):
        p=by[label];assert p['firstError']['phase']=='compile:when' and p['paidPrefix']['M0']['head_occurrences']==0
    assert by['variable-when-class-enabled']['firstError']['event']==90 and by['variable-when-class-disabled']['firstError']['event']==94
    assert by['variable-when-class-enabled']['paidPrefix']['M0']['work']==1323
    assert by['fixed-when-class-allowed']['state']=='completed' and by['fixed-when-class-allowed']['paidPrefix']['M0']['work']==11691
    p=by['resource-before-late-lexical'];e=p['firstError'];assert e['event']==57 and e['before']['input_bytes']==250824 and e['requested']['input_bytes']==50202 and e['cap']==262144
    assert not p['semanticAnalysis']['reachedByExecution'] and p['terminalRetainedHandles']=={}
    all114=json.loads((HERE/'all114-fee-programs-r4.json').read_text());table=json.loads((HERE.parent/'per-id-r4.json').read_text())
    old=json.loads((HERE.parent/'per-id-r3.json').read_text());oldprograms=json.loads((HERE.parent/'charge-reference-v3'/'all114-fee-programs-r3.json').read_text())
    raw=HERE.parents[3]/'reviews'/'I05'/'independent-fee-spec'/'author-v2-inputs'/'inputs.json'
    b=raw.read_bytes();assert len(b)==8205267 and digest(b)=='47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa';inputs=json.loads(b)
    assert len(all114['items'])==114 and len({p['id'] for p in all114['items']})==114
    assert [p['id'] for p in table['items']]==[p['id'] for p in old['items']]
    byid={p['id']:p for p in all114['items']};oldid={p['id']:p for p in oldprograms['items']};deltas=[]
    for row,previous in zip(table['items'],old['items']):
        p=byid[row['id']];before=oldid[row['id']];children=receipt(p);predicted=row['predictedAllocation']
        if predicted.get('children') is not None:assert children==predicted['children']
        assert p['programSourceSha256']==all114['sourceSha256']==digest((HERE/'reference.py').read_bytes())
        assert row['proposalInvoice']['amount']==p['amount'] and row['proposalInvoice']['paidPrefix']==p['paidPrefix']
        for key in previous:
            if key not in ('proposalInvoice','pureMathematicalProgram','proposalBinder'):assert row[key]==previous[key]
        data=inputs['datasets'][p['datasetId']];delta=metadata_cost(data);class_delta=when_class_cost(data)
        # Fullview replay has an independently funded compile in R16-child.
        # It executes the same static clause again; held-byte negative paths
        # never open that wallet and cannot be billed for unexecuted replay.
        for wallet,vector in list(class_delta.items()):
            replay_wallet='R16-'+wallet[1:]
            if replay_wallet in p['amount']:class_delta[replay_wallet]=vector.copy()
        for wallet,amount in p['amount'].items():
            for domain,value in amount.items():
                expected=delta.get(domain,0) if wallet=='C0' else class_delta.get(wallet,{}).get(domain,0)
                assert value==before['amount'][wallet][domain]+expected,(p['id'],wallet,domain)
        assert p['caps']==before['caps'] and p['wholeOwnerHRequiredPeak']==before['wholeOwnerHRequiredPeak']
        shift=delta['eventShift']+sum(v['eventShift'] for v in class_delta.values())
        assert p['programEventCount']==before['programEventCount']+shift and p['executionEventCount']==before['executionEventCount']+shift
        if p['firstError']:assert p['firstError']['event']==before['firstError']['event']+shift and p['noSuccessPrefix'] and not p['terminalRetainedHandles']
        else:assert p['state']=='completed'
        assert p['entryMetadata']['state']=='validated' and p['entryMetadata']['allocationStarted']
        assert p['actualSameIssueAuthority']=={'limits':None,'usage':None,'issuer':None,'jobOrSourcePermission':None}
        deltas.append({'id':p['id'],'metadataAdditionalVector':delta,'whenClassAdditionalVectors':class_delta,'totalEventShift':shift,'reason':'E00 complete metadata gate plus integration59+64 when fixed-class guard and full Catalog class occurrence scan, including each actual R16-child recompile; head gate uses original billed check','capUnchanged':True,'unchangedWallets':sorted(w for w in p['amount'] if w!='C0' and not class_delta.get(w,{}).get('work',0)),'sourceOccurrencesUnchanged':'record-term.source and definition.source only; constant TermInput.source remains M0'})
    expected_delta={'format':'i05-independent-r4-per-id-fee-delta/2','items':deltas,'scope':114,'formula':'independent E00 and when-class tables from fixed source JSON; all wallets/caps/peaks/events cross-checked'}
    if sys.argv[1:]==['--write-delta']:(HERE/'metadata-delta-r4.json').write_text(json.dumps(expected_delta,ensure_ascii=False,indent=2)+'\n')
    else:assert json.loads((HERE/'metadata-delta-r4.json').read_text())==expected_delta
    print('independent replay/IFR3/literal arithmetic passed: baseline+27 complete-entry programs; 114 receipt/17L/current-column preservation and every-ID metadata+when-class fee delta/cap/peak/event audit passed')

if __name__=='__main__':main()
