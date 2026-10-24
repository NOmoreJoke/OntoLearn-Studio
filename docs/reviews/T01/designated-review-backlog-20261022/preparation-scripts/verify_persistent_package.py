from pathlib import Path
import json,hashlib,subprocess,datetime
P=Path('/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/T01-complete-engineering')
def sha(b):return hashlib.sha256(b).hexdigest()
fail=[];counts={'sourceFiles':0,'sourceBytes':0,'stageEvidenceFiles':0,'controlFiles':0,'wipArchives':0}
for m in (P/'candidates').glob('*/source-manifest.json'):
 d=json.loads(m.read_text());recorded={x['path'] for x in d['files']};actual={str(x.relative_to(m.parent/'project')) for x in (m.parent/'project').rglob('*') if x.is_file()}
 if recorded!=actual:fail.append(str(m)+':file-set')
 assert not (m.parent/'project/.git').exists()
 for r in d['files']:
  b=(m.parent/'project'/r['path']).read_bytes();counts['sourceFiles']+=1;counts['sourceBytes']+=len(b)
  if len(b)!=r['bytes'] or sha(b)!=r['sha256']:fail.append(str(m)+':'+r['path'])
 if sha(json.dumps(d['files'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())!=d['canonicalManifestSha256']:fail.append(str(m)+':canonical')
x=json.loads((P/'evidence-manifest.json').read_text())
for r in x['files']:
 f=P/'evidence'/r['treeKey']/r['path'];b=f.read_bytes();counts['stageEvidenceFiles']+=1
 if len(b)!=r['bytes'] or sha(b)!=r['sha256']:fail.append(str(f))
for r in x['control']:
 f=P/'control'/r['path'];b=f.read_bytes();counts['controlFiles']+=1
 if len(b)!=r['bytes'] or sha(b)!=r['sha256']:fail.append(str(f))
for r in json.loads((P/'frozen-wip/archive-manifest.json').read_text())['files']:
 f=Path(r['path']);b=f.read_bytes();counts['wipArchives']+=1
 if len(b)!=r['bytes'] or sha(b)!=r['sha256']:fail.append(str(f))
inv=json.loads((P/'backlog.json').read_text());assert len(inv['stages'])==47 and len({r['id'] for r in inv['stages']})==47
for row in inv['stages']:
 for model in ['zcode','minimax']:
  r=row['specifiedReviews'][model]
  assert all(r[k] is None for k in ['actualTaskId','actualSessionId','actualTurnId','actualSettings','actualReport'])
summary=json.loads((P/'coverage/coverage-summary.json').read_text());assert summary['comparisons']==126 and len(summary['byteCoveredPairs'])==8
assert not fail,fail
result={'timeUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Static persistent copy/manifest/hash readback only; not product/test/runtime acceptance','counts':counts,'failures':fail,'stages':47,'coverageComparisons':126,'byteCoveredPairs':8,'actualSpecifiedTasks':0,'protectedSourcesChanged':False}
(P/'persistent-static-readback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
