"""Run explicitly named pure R3 checks and preserve every actual exit/output."""
from pathlib import Path
import json
import subprocess
import sys
HERE=Path(__file__).resolve().parent
REVIEW=HERE.parents[3]/'reviews'/'I05'/'independent-fee-spec'
attempt=sys.argv[1];names=sys.argv[2:]
target=REVIEW/('r3-'+attempt+'.json')
if target.exists():raise ValueError('immutable attempt already exists')
commands=[]
for name in names:
    p=subprocess.run([sys.executable,'-B',str(HERE/name)],text=True,capture_output=True)
    commands.append({'argv':[sys.executable,'-B',str(HERE/name)],'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
record={'commands':commands,'firstFailure':next((i for i,c in enumerate(commands) if c['exit']),None),'exit':0 if all(c['exit']==0 for c in commands) else 1}
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
for c in commands:print(Path(c['argv'][-1]).name,c['exit'])
sys.exit(record['exit'])
