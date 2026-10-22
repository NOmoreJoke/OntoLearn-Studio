"""Final R3 two-seed pure mathematical regression; immutable new evidence."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
HERE=Path(__file__).resolve().parent
REVIEW=HERE.parents[3]/'reviews'/'I05'/'independent-fee-spec'
code='''import run_reference,reference,json,test_complete_failures_r4 as failures
from pathlib import Path
d=run_reference.load();i=d['inputs.json'];o=d['oracle.json'];g=d['gaps.json'];ii={v['id']:v for v in i['observations']};oi={v['id']:v for v in o['observations']};s=reference.sha(Path(reference.__file__).read_bytes());out=[]
def append(p):
 out.append([p['id'],p['programSha256'],p['programEventCount'],p['executionSha256'],p['executionEventCount'],reference.sha(reference.canonical(p['amount'])),reference.sha(reference.canonical(p['paidPrefix'])),p['state'],p['firstError'],p['finalization']['receiptSha256']])
for x in g['items']+g['additionalProductionRestoreCases']:
 v=ii[x['id']];e=oi[x['id']]['expected'];p,_=reference.make_program(v,i['datasets'][v['datasetId']],e.get('conditionalBusinessExpected',e.get('businessMath')),s);append(p)
for label,data in {**failures.CASES,**failures.EXTRA}.items():append(failures.run_case(label,data))
print(json.dumps(out,separators=(',',':')))
'''
path=REVIEW/('r4-final-determinism'+('-'+sys.argv[1] if len(sys.argv)>1 else '')+'.json')
if path.exists():raise ValueError('immutable proof already exists; use new explicit path')
runs=[]
for seed in ('1','2'):
    p=subprocess.run([sys.executable,'-B','-c',code],env=dict(os.environ,PYTHONHASHSEED=seed,PYTHONPATH=str(HERE)),text=True,capture_output=True)
    runs.append({'seed':seed,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
equal=all(p['exit']==0 for p in runs) and runs[0]['stdout']==runs[1]['stdout']
evidence={'sourceSha256':hashlib.sha256((HERE/'reference.py').read_bytes()).hexdigest(),'argvProgram':code,'runs':runs,'scope':'114 fixed programs, six prior real rejections and twenty-one focused metadata/language full-entry cases','allProgramExecutionAmountPaidPrefixReceiptSequencesEqual':equal,'exit':0 if equal else 1}
path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print('141 full-entry programs, two seeds:',equal)
sys.exit(evidence['exit'])
