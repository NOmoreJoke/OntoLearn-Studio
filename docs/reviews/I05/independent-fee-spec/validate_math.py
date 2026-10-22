"""Bounded own-artifact validation; only stdlib + authorized existing formatter."""
from pathlib import Path
import ast
import hashlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
R=ROOT/'docs/reviews/I05/independent-fee-spec'
I=ROOT/'docs/iterations/I05/independent-fee-spec'
PYTHON='/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12'
FORMAT=['/usr/local/bin/node','/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs']
AUTHORED=[I/n for n in ('specification.md','operation-schedule.md','hand-examples.md','handoff.md',
                       'per-id.md','per-id.json','fee-contract.json','bound-formulas.json','hand_vectors.json')]
AUTHORED += [R/n for n in ('input-manifest.json','input-collection-result.json','normative-claims.json',
                          'process.md','retained-first-failures.json')]

def run(label,argv):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,
                     env=os.environ | {'PYTHONDONTWRITEBYTECODE':'1'},check=False)
    row={'label':label,'argv':argv,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    (R/(label+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'label':label,'exit':p.returncode},ensure_ascii=False))
    return p.returncode

if sys.argv[1:] == ['format']:
    raise SystemExit(run('format-write',FORMAT+['--write']+[str(p.relative_to(ROOT)) for p in AUTHORED]))
assert not sys.argv[1:]
# Read source bytes only from named frozen copies and exact local inputs.
manifest=json.loads((R/'input-manifest.json').read_text())
for row in manifest:
    p=ROOT/row.get('copy',row['path'])
    b=p.read_bytes()
    assert (len(b),hashlib.sha256(b).hexdigest()) == (row['bytes'],row['sha256']), row['name']
for p in list(I.glob('*.py'))+list(R.glob('*.py')):
    ast.parse(p.read_text(),filename=str(p))
for p in AUTHORED:
    if p.suffix=='.json':json.loads(p.read_text())
rows=json.loads((I/'per-id.json').read_text())['items']
assert len(rows)==114 and len({r['id'] for r in rows})==114
assert sum(r['category']=='profile82' for r in rows)==82
assert sum(r['category']=='chain32' for r in rows)==32
assert sum(r['predictedAllocation']['children'] is not None for r in rows)==113
assert sum(r['conditionalCanonicalApiDefaultAllocation'] is not None for r in rows)==1
assert sum(bool(r['mathFacts']) for r in rows)==18
for r in rows:
    assert r['authority']['actualSameIssue17L'] is None
    assert r['authority']['producerIssuer'] is None
    assert r['authority']['actualBudgetUsage'] is None
    assert r['currentInvoice']['exact'] is None
    assert r['decision']['resourceRejection']=='not-automatically-allowed'
# Source ranges must be exact frozen bytes. No current implementation body reads.
for claim in json.loads((R/'normative-claims.json').read_text()):
    raw=(ROOT/claim['source']['copy']).read_bytes().splitlines(keepends=True)
    excerpt=b''.join(raw[claim['startLine']-1:claim['endLine']])
    assert len(excerpt)==claim['excerptBytes']
    assert hashlib.sha256(excerpt).hexdigest()==claim['excerptSha256']
    for line in claim['lines']:
        b=raw[line['line']-1]
        assert len(b)==line['bytes'] and hashlib.sha256(b).hexdigest()==line['sha256']
result={'sourceIdentityChecks':len(manifest),'perIdRows':114,'full17LPredictions':113,
        'conditionalDefault17LPredictions':1,'independentIntegerTruthFacts':18,
        'exactCurrentCompleteInvoices':0,'sourceClaims':len(json.loads((R/'normative-claims.json').read_text())),
        'astOnlyOwnFiles':True,'productExecuted':False}
(R/'static-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
code=run('math-selftest',[PYTHON,str((I/'test_invoice_model.py').relative_to(ROOT))])
code2=run('format-check',FORMAT+['--check']+[str(p.relative_to(ROOT)) for p in AUTHORED])
code3=run('git-diff-check',['git','diff','--check'])
raise SystemExit(max(code,code2,code3))
