#!/usr/bin/env python3
"""Read Git blobs/retained WIP bytes only; write derived coverage to this directory.
No imported repository code, tests, databases, native apps, or mutation of source trees.
"""
import collections
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'backlog.json'
source_bytes = SOURCE.read_bytes()
D = json.loads(source_bytes)
BASE = D['base']
TREES = {x['key']: x['tree'] for x in D['currentTrees']}
REPO = TREES['early']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def run(*args):
    return subprocess.check_output(['git', '-C', REPO, *args])

def product_path(path):
    # Match backlog product/test convention: exclude documentation and AGENTS.
    return not path.startswith(('docs/', 'iteration-control/')) and path != 'AGENTS.md'

def diff_paths(ref):
    return sorted(p for p in run('diff', '--name-only', '--no-renames', '-z', BASE, ref).decode().split('\0') if p and product_path(p))

cache = {}
def git_state(ref, path):
    key = (ref, path)
    if key not in cache:
        entry = run('ls-tree', '-z', ref, '--', path)
        if not entry:
            cache[key] = {'exists': False, 'bytes': None, 'sha256': None, 'gitMode': None, 'gitBlob': None}
        else:
            header, entrypath = entry.rstrip(b'\0').split(b'\t', 1)
            mode, kind, oid = header.decode().split()
            if kind != 'blob':
                raise ValueError(f'Non-blob historical/target path {ref}:{path}: {kind}')
            data = run('cat-file', 'blob', oid)
            cache[key] = {'exists': True, 'bytes': len(data), 'sha256': sha(data), 'gitMode': mode, 'gitBlob': oid}
    return cache[key]

def same_bytes(a, b):
    return a['exists'] == b['exists'] and a['sha256'] == b['sha256'] and a['bytes'] == b['bytes']

selected = [s for s in D['stages'] if s.get('productRef') and (s['id'].startswith('E') or s['id'].startswith('C2-') or s['id'].startswith('D-'))]
assert len(selected) == 18
historical = []
for s in selected:
    paths = diff_paths(s['productRef'])
    historical.append({
        'id': s['id'], 'stage': s['stage'], 'productRef': s['productRef'],
        'processOrDocumentationRef': s.get('processOrDocumentationRef'),
        'tree': s['tree'], 'branch': s['branch'],
        'scopeDefinition': 'Full base-to-productRef changed product/test paths; not the single-commit delta',
        'changedPathCount': len(paths),
        'paths': [{'path': p, 'base': git_state(BASE,p), 'historical': git_state(s['productRef'],p)} for p in paths],
        'authorizationEvidenceFromBacklog': {
            'originalOwner': s.get('originalOwner'), 'writeBoundary': s.get('writeBoundary'),
            'authorizedProductTestWriters': s.get('authorizedProductTestWriters'),
            'evidence': s.get('evidence'),
            'warning': 'Copied inventory evidence, not a new grant. Actual historical delta is not itself authorization.'},
        'specifiedReviewMetadataFromBacklog': s.get('specifiedReviews'),
        'successorRelationshipFromBacklog': s.get('successorRelationship'),
    })

refs = [
    ('early-5de', 'early', '5de3fff8aa02c5d6e577938660e9362936d90550'),
    ('host-a816', 'host', 'a816c2d018772ce8b172101d9debec787ffa434a'),
    ('C1-423b', 'create', '423b7e4c799f188cf2ce6e8e7121893ce85624cd'),
    ('C2-ab792', 'c2', 'ab792c494db09ada1f20d0a598c3e0c96c338992'),
    ('dispatch-7dfa', 'drain', '7dfa9c8008727d469935181fc20beebb5ba4419a'),
]
targets = []
for ident, key, ref in refs:
    actual = run('rev-parse', ref).decode().strip()
    assert actual == ref
    paths = diff_paths(ref)
    targets.append({'id': ident, 'kind': 'committed-product-candidate', 'tree': TREES[key], 'productRef': ref,
                    'fullProductDeltaPathCount': len(paths), 'packetPathCount': len(paths), 'packetPaths': paths,
                    'scope': 'Entire committed Git candidate; all changed product/test paths relative to base',
                    'state': {p: git_state(ref,p) for p in paths}})

# Full retained S1 candidate = adopted 52-path product/test delta plus its two WIP paths.
s1tree = Path(TREES['s1'])
s1head = subprocess.check_output(['git','-C',str(s1tree),'rev-parse','HEAD']).decode().strip()
s1changed = subprocess.check_output(['git','-C',str(s1tree),'diff','--name-only','--no-renames','-z',BASE]).decode().split('\0')
s1untracked = subprocess.check_output(['git','-C',str(s1tree),'ls-files','--others','--exclude-standard','-z']).decode().split('\0')
s1paths = sorted({p for p in s1changed+s1untracked if p and product_path(p)})
assert len(s1paths) == 54, len(s1paths)

wip_read_log = {}
def fs_state(tree, path):
    full = Path(tree)/path
    if not full.exists():
        return {'exists':False,'bytes':None,'sha256':None,'gitMode':None,'gitBlob':None}
    if full.is_symlink():
        raise ValueError(f'Symlink not accepted for WIP packet: {full}')
    data = full.read_bytes()
    stat = {'exists':True,'bytes':len(data),'sha256':sha(data),'gitMode':None,'gitBlob':None}
    wip_read_log[str(full)] = stat
    return stat

targets.append({'id':'S1-current54','kind':'retained-uncommitted-complete-product-packet','tree':str(s1tree),
                'adoptionOnlyRef':s1head,'productRef':None,'packetPathCount':54,
                'scope':'52 adopted delta paths plus two retained untracked S1 product/test paths; current bytes captured only',
                'packetPaths':s1paths,'state':{p:fs_state(s1tree,p) for p in s1paths}})

producer = D['wipIdentities']['producer']
producerpaths = [x['path'] for x in producer['packet149']]
assert len(producerpaths) == 149 and len(set(producerpaths)) == 149
producer_states = {p:fs_state(TREES['producer'],p) for p in producerpaths}
producer_drift = []
for expected in producer['packet149']:
    actual = producer_states[expected['path']]
    if not actual['exists'] or actual['bytes'] != expected['bytes'] or actual['sha256'] != expected['sha256']:
        producer_drift.append({'path':expected['path'],'expected':expected,'actual':actual})
targets.append({'id':'producer-current149','kind':'retained-uncommitted-149-input-packet','tree':TREES['producer'],
                'adoptionOnlyRef':producer['adoptionOnlyRef'],'productRef':None,'packetPathCount':149,
                'scope':'Exact 149 paths already listed in backlog; includes read-only base inputs/document fixtures; no expansion of packet',
                'expectedPacketCanonicalSha256FromBacklog':producer.get('packet149CanonicalSha256'),
                'backlogManifestDrift':producer_drift,'packetPaths':producerpaths,'state':producer_states})

matrix = []
for h in historical:
    for t in targets:
        rows=[]
        for item in h['paths']:
            p=item['path']; hs=item['historical']; bs=item['base']
            inpacket = p in t['state']
            if t['kind']=='committed-product-candidate':
                ts=git_state(t['productRef'],p)
                # A base-equal path is readable in the complete tree but outside its diff packet.
                available=True
            else:
                ts=t['state'].get(p, {'exists':False,'bytes':None,'sha256':None,'gitMode':None,'gitBlob':None})
                available=inpacket
            if not available or (hs['exists'] and not ts['exists']):
                classification='missing'
            elif same_bytes(hs,ts):
                classification='same'
            elif same_bytes(bs,ts):
                classification='no-longer-delta'
            else:
                classification='different'
            rows.append({'path':p,'classification':classification,'base':bs,'historical':hs,'target':ts,
                         'targetInChangedOrExplicitPacket':inpacket,
                         'targetAvailableForComparison':available,
                         'targetDiffersFromBase':not same_bytes(bs,ts) if available else None,
                         'modeSame':hs['gitMode']==ts['gitMode'] if hs['gitMode'] and ts['gitMode'] else None})
        counts=dict(collections.Counter(r['classification'] for r in rows))
        counts={k:counts.get(k,0) for k in ['same','different','missing','no-longer-delta']}
        covered=all(r['classification']=='same' for r in rows)
        matrix.append({'historicalId':h['id'],'historicalProductRef':h['productRef'], 'targetId':t['id'],
                       'counts':counts,'historicalChangedPathCount':len(rows),'byteCovered':covered,
                       'disposition':'Full historical changed-product/test bytes present identically; byte equality only, review is still required' if covered else 'Independent historical version / successor evolution remains to review; not automatically discarded or semantically covered',
                       'paths':rows})

# Re-read only previously captured WIP paths, verifying no in-run identity drift.
wip_read_stable=True
for full, expected in wip_read_log.items():
    data=Path(full).read_bytes()
    if len(data)!=expected['bytes'] or sha(data)!=expected['sha256']:
        wip_read_stable=False
        raise RuntimeError(f'WIP changed during static capture: {full}')
if SOURCE.read_bytes()!=source_bytes:
    raise RuntimeError('backlog.json changed during static coverage capture; rerun with new input')

for t in targets:
    manifest=[{'path':p,**t['state'][p]} for p in sorted(t['state'])]
    canonical=json.dumps(manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    t['capturedPacketCanonicalSha256']=sha(canonical)
    t['manifest']=manifest
    del t['state']

result={
    'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'base':BASE,'sourceBacklog':{'path':str(SOURCE),'bytes':len(source_bytes),'sha256':sha(source_bytes)},
    'policy':{
        'operation':'Static Git blobs and retained WIP files only; derived output written only under coverage directory',
        'historicalScope':'Every selected historical productRef full 5f-to-product changed set; excludes docs/, iteration-control/, AGENTS.md; includes tests/fixtures/build/config if changed',
        'byteCovered':'True only if EVERY historical changed path has identical bytes/absence at target; SHA256, byte count and existence match. Not a semantic coverage or review Pass claim.',
        'classification':{'same':'historical and target byte identity/absence equal','different':'target available, differs from historical and from base','missing':'historical file absent in target, or path outside explicit WIP packet','no-longer-delta':'target is present and byte-identical to base, while historical differs'},
        'scopeCaveat':'Committed targets compare entire tree for historical paths; WIP targets are strictly their explicit54/149 packet. targetInChangedOrExplicitPacket and targetDiffersFromBase preserve this distinction.',
        'reviewPass':'No test/internal/design Pass is transferred; no specified task is created by this output',
        'authorization':'Historical author fields copied from backlog are evidence only; no new write grant',
        'runtime':'No repository Python/JS imports or execution, product/test/DB/native/child/GUI launched',
    },
    'wipReadStableDuringCapture':wip_read_stable,'producerManifestMatchesBacklog':not producer_drift,
    'historicalCandidates':historical,'targets':targets,'matrix':matrix,
}
(OUT/'coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

md=['# T01历史候选 → 当前保留候选逐bytes覆盖矩阵','',f'基线 `{BASE}`。来源backlog SHA256 `{sha(source_bytes)}`。',
    '', '只读Git blob与已保留WIP。每个历史阶段使用完整基线→productRef产品及测试差异集合，非单commit delta。`byteCovered=true`仅表示完整同bytes；没有语义覆盖或指定审查Pass含义。不同/缺失/已回基线的版本保留独立审查义务，不自动废弃。',
    '', '计数格式：same / different / missing / no-longer-delta。详细每路径SHA256、大小、Git blob、基线/历史/目标及packet归属见coverage.json与下方逐路径表。',
    '', '|历史阶段/完整差异路径数|'+ '|'.join(t['id'] for t in targets)+'|',
    '|---|'+ '|'.join('---' for t in targets)+'|']
for h in historical:
    ms=[m for m in matrix if m['historicalId']==h['id']]
    md.append('|'+h['id']+' '+str(h['changedPathCount'])+'|'+ '|'.join('/'.join(str(m['counts'][k]) for k in ['same','different','missing','no-longer-delta'])+(' **byteCovered**' if m['byteCovered'] else '') for m in ms)+'|')
md+=['','## 候选身份','', '|目标|产品ref/adoption|路径数|捕获packet SHA256|','|---|---|---:|---|']
for t in targets:
    md.append(f"|{t['id']}|`{t.get('productRef') or t.get('adoptionOnlyRef')}` {'(仅adoption，当前未提交)' if not t.get('productRef') else ''}|{t['packetPathCount']}|`{t['capturedPacketCanonicalSha256']}`|")
md+=['',f"S1/producer逐路径重读稳定：{wip_read_stable}；producer149与backlog逐路径大小/SHA一致：{not producer_drift}。",'',
'## 分类及限制','',
'- same：该历史路径原bytes与目标完全相同。只有该阶段全部路径均same才byteCovered。',
'- different：目标存在且已演进，bytes既不同于历史也不同于基线。',
'- missing：历史文件目标缺失；或不在WIP显式54/149包内。后者不冒充已核整个文件树。',
'- no-longer-delta：目标文件已回到基线原bytes。',
'- 已提交目标读取整个候选Git树；S1与producer只比较明确54/149输入。目标的改动包归属在JSON另列。',
'- 所有历史指定task/session/turn/settings/report字段按backlog原样保留；未以矩阵结果填造审查。',
'- 原owner写面与证据从backlog原样复制，null不补猜，不作为当前授权。','']
for h in historical:
    md += [f"## {h['id']} {h['stage']}", '',f"历史产品 `{h['productRef']}`；完整差异 {h['changedPathCount']} 路径。",'']
    for m in [x for x in matrix if x['historicalId']==h['id']]:
        md += [f"### → {m['targetId']} / byteCovered={str(m['byteCovered']).lower()}", '',
               '|路径|类别|历史SHA256 / bytes|目标SHA256 / bytes|基线SHA256 / bytes|','|---|---|---|---|---|']
        for row in m['paths']:
            def f(state):
                return '`'+str(state['sha256'])+'` / '+str(state['bytes']) if state['exists'] else 'absent'
            md.append('|`'+row['path']+'`|'+row['classification']+'|'+f(row['historical'])+'|'+f(row['target'])+'|'+f(row['base'])+'|')
        md.append('')
(OUT/'coverage.md').write_text('\n'.join(md)+'\n')
summary={
    'historicalCandidates':len(historical),'targetCandidates':len(targets),'comparisons':len(matrix),
    'byteCoveredPairs':[{'historical':m['historicalId'],'target':m['targetId']} for m in matrix if m['byteCovered']],
    'producerManifestMatchesBacklog':not producer_drift,'producerDrift':producer_drift,
    'wipStable':wip_read_stable,
    'files':[{'path':str(OUT/name),'bytes':(OUT/name).stat().st_size,'sha256':sha((OUT/name).read_bytes())} for name in ['build_coverage.py','coverage.json','coverage.md']],
}
(OUT/'coverage-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
