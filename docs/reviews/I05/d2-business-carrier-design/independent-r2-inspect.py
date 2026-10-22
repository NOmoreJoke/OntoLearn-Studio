"""Read-only delta/identity inspection; own output files exclusively created.
No author checker/model/product execution. Only specified pure inputs and git trees.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
R=ROOT/'docs/reviews/I05/d2-business-carrier-design'
D=ROOT/'docs/iterations/I05/d2-business-carrier-design'
BASE='aefa82e51643e0a75ecb960645d63917b046edd6'
CAND='707c3915bc28a92955638cba4e6b8e3c18e8cfac'
HEAD='a23a2550c163e9571adebaf983f7c50909c2f09c'
def load(p): return json.loads(p.read_bytes())
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def write(name,value):
 with (R/name).open('x') as f:
  json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')
log=[]
def run(argv):
 p=subprocess.run(argv,cwd=ROOT,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 def st(b): return {'bytes':len(b),'sha256':sha(b),'base64':base64.b64encode(b).decode()}
 log.append({'argv':argv,'cwd':str(ROOT),'envDelta':{'PYTHONDONTWRITEBYTECODE':'1'},'exit':p.returncode,'stdout':st(p.stdout),'stderr':st(p.stderr)})
 assert p.returncode==0
 return p.stdout

def tree(ref,repository=None,paths=None):
 paths=paths or ['docs/iterations/I05/d2-consumer-design','docs/reviews/I05/d2-consumer-design','docs/iterations/I05/d2-business-carrier-design','docs/reviews/I05/d2-business-carrier-design']
 argv=['/usr/bin/git']+(['-C',repository] if repository else [])+['ls-tree','-r','-z',ref,'--',*paths]
 data=run(argv)
 return {entry.split(b'\t',1)[1].decode():entry.split(b'\t',1)[0].split()[2].decode() for entry in data.split(b'\0') if entry}
if sys.argv[1]=='identity':
 manifest=load(R/'business-author-manifest-r2.json'); inputs=load(R/'input-identity-r2.json')
 trees={ref:tree(ref) for ref in (BASE,CAND,HEAD)}
 rows=[]
 for e in inputs['oldFrozenInventory']:
  b=(ROOT/e['path']).read_bytes(); rows.append({**e,'scope':'old113','gitBlobActual':blob(b),'matches':len(b)==e['bytes'] and sha(b)==e['sha256'] and blob(b)==trees[BASE][e['path']]})
 for e in manifest['files']+[{'path':'docs/reviews/I05/d2-business-carrier-design/business-author-manifest-r2.json','bytes':10185,'sha256':'cfc6a607290c4e0d14e5d3b71a5153be8fa81e65dd24616465b12f0ddfafc352'},{'path':'docs/reviews/I05/d2-business-carrier-design/business-author-receipt-r2.json','bytes':73240,'sha256':'a20ec2ce67b89b425dabc24371ced0706afd48684b4a3bd00689defb2a447ef1'}]:
  b=(ROOT/e['path']).read_bytes(); ref=HEAD if e['path'].endswith('business-author-receipt-r2.json') else CAND
  rows.append({**e,'scope':'new46','ref':ref,'gitBlobActual':blob(b),'matches':len(b)==e['bytes'] and sha(b)==e['sha256'] and blob(b)==trees[ref][e['path']]})
 origins=[]
 for key in ('newV3Inputs','newM06PureInputs'):
  group=inputs[key]['inputs']
  sourceTree=tree(group[0]['ref'],group[0]['repository'],[e['path'] for e in group])
  for e in group:
   b=(ROOT/e['snapshot']).read_bytes(); origins.append({**e,'matches':len(b)==e['bytes'] and sha(b)==e['sha256'] and blob(b)==sourceTree[e['path']]})
 result={'scope':'current bytes/SHA and computed Git blob vs read-only fixed ls-tree','rows':rows,'origins':origins,'allMatches':all(x['matches'] for x in rows+origins),'guidance':{'bytes':len((ROOT/'AGENTS.md').read_bytes()),'sha256':sha((ROOT/'AGENTS.md').read_bytes())},'branch':run(['/usr/bin/git','branch','--show-current']).decode().strip(),'head':run(['/usr/bin/git','rev-parse','HEAD']).decode().strip(),'index':run(['/usr/bin/git','diff','--cached','--name-only']).decode()}
 write('independent-r2-identity.json',result);write('independent-r2-identity-commands.json',log)
 print(json.dumps({k:v for k,v in result.items() if k not in ('rows','origins')},ensure_ascii=False,indent=2))
elif sys.argv[1]=='delta':
 old=load(D/'wire-grammar.json');new=load(D/'wire-grammar-r2.json')
 changed=[k for k,v in old['definitions'].items() if v!=new['definitions'].get(k)]
 print('changed definitions',changed)
 for k in changed+[k for k in new['definitions'] if k not in old['definitions']]:
  print('DEFINITION',k,json.dumps(new['definitions'][k],ensure_ascii=False,separators=(',',':')))
 print('other top-level delta',json.dumps({k:v for k,v in new.items() if k!='definitions' and old.get(k)!=v},ensure_ascii=False,separators=(',',':')))
else:
 data=load(D/sys.argv[2]); key=sys.argv[3] if len(sys.argv)>3 else None
 value=data[key] if key else data
 if type(value) is list:
  for i,item in enumerate(value): print(i,json.dumps(item,ensure_ascii=False,separators=(',',':')))
 else: print(json.dumps(value,ensure_ascii=False,separators=(',',':')))
