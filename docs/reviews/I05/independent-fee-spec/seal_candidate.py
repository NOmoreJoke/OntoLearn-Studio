"""Seal only authorized docs. First-author preservation is bytes/hash opaque."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[4]
R=ROOT/'docs/reviews/I05/independent-fee-spec'
I=ROOT/'docs/iterations/I05/independent-fee-spec'
formatter=['/usr/local/bin/node','/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs']
own=list(I.glob('*.md'))+list(I.glob('*.json'))
own += [R/n for n in ('input-manifest.json','input-collection-result.json','normative-claims.json',
 'process.md','retained-first-failures.json','revision-record.md','format-write.json',
 'math-selftest.json','format-check.json','git-diff-check.json','static-validation.json')]
for action in ('--write','--check'):
 argv=formatter+[action]+[str(p.relative_to(ROOT)) for p in own]
 p=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True,check=False)
 label='final-format-write' if action=='--write' else 'final-format-check'
 (R/(label+'.json')).write_text(json.dumps({'argv':argv,'exit':p.returncode,
      'stdout':p.stdout,'stderr':p.stderr},ensure_ascii=False,indent=2)+'\n')
 assert p.returncode==0, label
# Verify raw source copies/protected guidance/excerpt have not changed.
for row in json.loads((R/'input-manifest.json').read_text()):
 b=(ROOT/row.get('copy',row['path'])).read_bytes()
 assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['name']
entries=[]
for prefix in (I,R):
 for p in sorted(prefix.rglob('*')):
  if not p.is_file() or p.name=='artifact-manifest.json':continue
  assert not p.is_symlink(), 'unexpected symlink'
  assert '__pycache__' not in p.parts, 'cache should not be delivered'
  b=p.read_bytes()  # Opaque bytes only for root-owned prior author preservation.
  rel=str(p.relative_to(ROOT))
  entries.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
      'classification':'root-preserved-not-independent-no-content-read' if 'author-v1-input-exposure' in p.parts
                       else 'root-provided-permitted-math-excerpts' if p.name=='local-proof-excerpts.json'
                       else 'author-v2-artifact-or-fixed-raw-input'})
manifest={'format':'i05-independent-fee-candidate-manifest/1',
 'base':'5f910b52c69d86a1076b2032e5d3c63e715947f3','branch':'docs/I05-independent-fee-spec',
 'candidateBinding':'the actual commit returned after staging; not prefilled future commit',
 'selfExclusion':'only this artifact-manifest.json is excluded to avoid self hash; postcommit hash is reported externally',
 'scope':'all regular files under the two authorized docs prefixes, including root-owned incident preservation; AGENTS excluded',
 'rootOwnedPreservationContentRead':False,'entries':entries}
(R/'artifact-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'entries':len(entries),'bytes':sum(e['bytes'] for e in entries),
                 'sourceIdentity':True,'formatterExit':0,'productExecuted':False}))
