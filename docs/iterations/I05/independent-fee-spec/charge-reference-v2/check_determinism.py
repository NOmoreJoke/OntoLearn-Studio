"""Repeat only this independent mathematical interpreter under two hash seeds."""
from pathlib import Path
import subprocess
import os
import json
import sys
import hashlib
HERE=Path(__file__).resolve().parent
REVIEW=HERE.parents[3]/'reviews'/'I05'/'independent-fee-spec'
code='''import run_reference,reference,json
from pathlib import Path
d=run_reference.load();i=d['inputs.json'];o=d['oracle.json'];g=d['gaps.json'];ii={v['id']:v for v in i['observations']};oi={v['id']:v for v in o['observations']};s=reference.sha(Path(reference.__file__).read_bytes());out=[]
for x in g['items']+g['additionalProductionRestoreCases']:
 v=ii[x['id']];e=oi[x['id']]['expected'];r,_=reference.make_program(v,i['datasets'][v['datasetId']],e.get('conditionalBusinessExpected',e.get('businessMath')),s);out.append([r['id'],r['programSha256'],r['programEventCount'],reference.sha(reference.canonical(r['amount']))])
print(json.dumps(out,separators=(',',':')))
'''
rows=[]
for seed in ('1','2'):
    env=dict(os.environ,PYTHONHASHSEED=seed,PYTHONPATH=str(HERE))
    argv=[sys.executable,'-B','-c',code];p=subprocess.run(argv,env=env,text=True,capture_output=True)
    rows.append({'seed':seed,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
equal=all(x['exit']==0 for x in rows) and rows[0]['stdout']==rows[1]['stdout']
proof={'sourceSha256':hashlib.sha256((HERE/'reference.py').read_bytes()).hexdigest(),'argvProgram':code,
       'runs':rows,'all114ProgramSequencesAmountsAndEventCountsEqual':equal,'exit':0 if equal else 1}
path=REVIEW/'r2-final-all114-determinism-v2.json'
if path.exists():raise ValueError('proof is immutable; use a new explicit attempt name')
path.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print('two seeds, all114 program/amount/count equality:',equal)
sys.exit(proof['exit'])
