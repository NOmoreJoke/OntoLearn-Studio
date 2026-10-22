# coding: utf-8
"""Finite document/identity checks; no product execution."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).parent
REPO=HERE.parents[3]
checks=[]
def identity(path):
    b=path.read_bytes()
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
old=REPO/'docs/reviews/T03/designated-review-backlog-20261022/final-preparation-manifest.json'
assert identity(old)['sha256']=='818f767ac872fabb585f911e029022ed24392abb94ed3561a6c8f20b3deb23d5'
for x in json.loads(old.read_text())['files']:
    assert identity(REPO/x['path'])=={k:x[k] for k in ['bytes','sha256']}
checks.append('Original 36 payload files and final self-manifest unchanged')
index=json.loads((HERE/'prompt-index.json').read_text())
assert len(index)==6 and len({x['tree'] for x in index})==6
for x in index:
    data=(HERE/x['prompt']).read_bytes()
    frozen=Path(x['frozenOriginalPath']).read_bytes()
    assert identity(HERE/x['prompt'])=={'bytes':x['promptBytes'],'sha256':x['promptSha256']}
    assert data[x['frozenSuffixOffset']:]==frozen
    assert identity(Path(x['frozenOriginalPath']))=={'bytes':x['frozenOriginalBytes'],'sha256':x['frozenOriginalSha256']}
    assert x['actualTask'] is None and x['actualSettings'] is None and x['lease'] is None
    for p in x['policies']:
        assert identity(Path(p['path']))=={k:p[k] for k in ['bytes','sha256']}
    root=Path(x['tree'])
    actual=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    assert actual==x['reviewHead']
    differences=subprocess.check_output(['git','-C',str(root),'diff','--name-only',x['product'],x['reviewHead'],'--','.',':(exclude)docs/**',':(exclude)AGENTS.md'],text=True).strip()
    assert not differences
    assert identity(root/'AGENTS.md')=={'bytes':15147,'sha256':'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'}
    assert subprocess.check_output(['git','-C',str(root),'status','--porcelain'],text=True).strip()=='M AGENTS.md'
    paths=x['pathMap']
    assert all(Path(paths[k]).is_relative_to(root) for k in paths)
    assert paths['c1Evidence']==str(root/'build/review-session/raw/c1-evidence.json')
    assert 'export I02_EVIDENCE=' in Path(paths['environmentShell']).read_text()
    site=root/'.venv/lib/python3.12/site-packages'
    pth=list(site.glob('_editable_impl_ontolearn_engine.pth'))
    assert len(pth)==1 and str(root/'packages/engine/src') in pth[0].read_text()
    receipt=json.loads((HERE/(root.name+'-after.json')).read_text())
    assert not receipt['productExecuted'] and not receipt['normalValidationExecuted']
    assert all(c['exitCode']==0 for c in receipt['commands'])
    for raw in receipt['raw']:
        assert identity(Path(raw['path']))=={k:raw[k] for k in ['bytes','sha256']}
        assert Path(raw['path']).read_text()==raw['fullText']
checks.append('Six exact frozen suffixes, policies, physical trees, clean product bytes, protected rules, own editable paths, 18 setup exits and full raw logs')
for path in HERE.glob('*.py'):
    ast.parse(path.read_text(),filename=str(path))
for path in HERE.glob('*.json'):
    json.loads(path.read_text())
checks.append('All new Python scripts ast.parse; all new JSON syntax valid; no product imports')
isolation=json.loads((HERE/'isolation-verification.json').read_text())
assert not isolation['crossTreeRegularInodeCollisions'] and len(isolation['externalSymlinks'])==18
checks.append('Isolation scan receipt: zero cross-tree regular inode collisions; 18 disclosed base interpreter links')
repair=json.loads((HERE/'F1-environment-repair.json').read_text())
assert len(repair['rows'])==6
assert all(x['exitCode']==0 and not x['stderr'] and x['stdout']==str(Path(x['tree'])/'build/review-session/raw/c1-evidence.json') for x in repair['rows'])
checks.append('F1 exact repair: six own C1 output maps and six pure-shell stale-env overwrite readbacks')
result={'scope':'Finite documents/setup-identity checks only, not product tests or designated review','checks':checks,'exitCode':0,'productExecuted':False}
(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
