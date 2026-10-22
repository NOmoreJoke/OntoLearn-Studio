"""Independent prefix arithmetic and binary receipt decoder; no interpreter import."""
from pathlib import Path
import json
import hashlib
HERE=Path(__file__).resolve().parent
v=json.loads((HERE/'baseline-prefix-r2.json').read_text())
order=('work','input_bytes','output_bytes','trace_items','firings','head_occurrences','bindings','scan_copy','hash_bytes','objects','scalar')
used={w:{k:0 for k in c if k not in ('objects','scalar')} for w,c in v['caps'].items()}
live={w:{'objects':0,'scalar':0} for w in used};peak=json.loads(json.dumps(live));held={};ever=set();h=slots=0
for event in v['events']:
    w=event['wallet'];assert event['ordinal']==v['events'].index(event)+1
    for d,n in event['charges'].items():assert n>=0;used[w][d]+=n
    hold=event['hold']
    if hold:
        name,o,s=hold;assert name not in ever;ever.add(name);held[name]=(w,o,s)
        if not name.startswith('control') and name!='receipt':h+=1;slots+=o
        live[w]['objects']+=o;live[w]['scalar']+=s
    if event['release']:
        name=event['release'];owner,o,s=held.pop(name)
        if name.startswith('control'):assert event['action']=='terminal cleanup control'
        live[owner]['objects']-=o;live[owner]['scalar']-=s
    for k in ('objects','scalar'):peak[w][k]=max(peak[w][k],live[w][k])
    assert event['requiredPrefix']==used[w] and event['live']==live[w] and event['peak']==peak[w]
    for k,n in used[w].items():assert n<=v['caps'][w][k]
    for k,n in live[w].items():assert 0<=n<=v['caps'][w][k]
    assert event['wholeOwnerHLive']=={k:sum(d[k] for d in live.values()) for k in ('objects','scalar')}
assert used==v['amount'] and peak==v['peak'] and live==v['terminalLive']
# These literals are the separately written complete baseline hand arithmetic.
assert used['C0']['work']==3215450
assert used['ENTRY']['work']==176580
assert used['G']['work']==185814
assert used['M0']['work']==140761
assert (h,slots)==(8,149538)
assert set(held)=={'receipt','native-fee-view'}
assert v['finalization']['vector']=={'work':152782,'scan_copy':3128,'hash_bytes':800}
raw=bytes.fromhex(v['finalization']['receiptHex']);assert len(raw)==782
position=0
def take(n):
    global position
    b=raw[position:position+n];assert len(b)==n;position+=n;return b
def uint(n):return int.from_bytes(take(n),'big')
def text():return take(uint(4)).decode()
assert take(5)==b'IFR2\2'
assert text()==v['id'];take(32)
assert (uint(4),uint(8),take(2))==(8,149538,b'\0\0')
assert uint(4)==5
seen=[]
for _ in range(5):
    w=text();assert w in v['caps'] and w not in seen;seen.append(w)
    for domain in order:assert uint(8)==(peak[w][domain] if domain in ('objects','scalar') else used[w][domain])
assert uint(4)==1;assert text()=='R-risk';assert (uint(1),uint(4),uint(1))==(1,0,0)
limits=(16777216,262144,262144,8192,1024,16384,1024,16384,65536,4096,16384,32768,100,16,32,16,64)
assert tuple(uint(8) for _ in range(17))==limits
assert uint(1)==0;assert take(32).hex()==v['programSha256']
body=raw[:position];digest=take(32);assert position==len(raw)
assert hashlib.sha256(b'I05-FEE-RECEIPT/2\0'+body+b'\0'*32).digest()==digest
assert hashlib.sha256(raw).hexdigest()==v['finalization']['receiptSha256']
# Second independent encoder checks actual synthetic input bytes, not product wire.
material=json.loads((HERE/'baseline-fee-material-r2.json').read_text())
def enc(value):
    def n(x):return x.to_bytes(4,'big')
    if value is None:return b'N'
    if value is True:return b'T'
    if value is False:return b'F'
    if isinstance(value,str):
        b=value.encode();return b'S'+n(len(b))+b
    if isinstance(value,list):return b'A'+n(len(value))+b''.join(map(enc,value))
    if isinstance(value,dict):return b'R'+n(len(value))+b''.join(enc(k)+enc(x) for k,x in value.items())
    raise ValueError('unexpected baseline fee-material kind')
encoded=enc(material)
assert encoded==bytes.fromhex((HERE/'baseline-fee-material-r2.bytes.hex').read_text())
assert hashlib.sha256(encoded).hexdigest()==v['feeCodec']['nativeSha256']
assert len(encoded)==85953
assert v['feeCodec']['nativeBytes']==85953
print('all2282 baseline prefixes, literal totals, lifetime counters and782-byte receipt: PASS')
