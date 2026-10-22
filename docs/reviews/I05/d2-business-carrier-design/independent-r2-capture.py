"""Only capture authorized child argv; exclusive new evidence, no product imports."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
root=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
out=root/'docs/reviews/I05/d2-business-carrier-design'
label,*argv=sys.argv[1:]
assert label.startswith('independent-r2-') and '/' not in label
path=out/(label+'.json')
assert not path.exists()
p=subprocess.run(argv,cwd=root,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
def stream(b):
 return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'base64':base64.b64encode(b).decode()}
with path.open('x') as f:
 json.dump({'argv':argv,'cwd':str(root),'envDelta':{'PYTHONDONTWRITEBYTECODE':'1'},'exit':p.returncode,'stdout':stream(p.stdout),'stderr':stream(p.stderr)},f,ensure_ascii=False,indent=2)
 f.write('\n')
sys.stdout.buffer.write(p.stdout)
sys.stderr.buffer.write(p.stderr)
sys.exit(p.returncode)
