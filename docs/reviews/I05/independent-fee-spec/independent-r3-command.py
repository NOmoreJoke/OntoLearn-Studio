"""R3 reviewer-only subprocess capture; no candidate writes."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).with_name('independent-r3-command-log.json')
def blob(b):
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
            'utf8':b.decode('utf-8'),'base64':base64.b64encode(b).decode('ascii')}
def main():
    argv=sys.argv[1:]
    p=subprocess.run(argv,cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    rows=json.loads(OUT.read_text()) if OUT.exists() else []
    rows.append({'sequence':len(rows)+1,'argv':argv,'cwd':str(ROOT),'exit':p.returncode,
                 'environmentOverride':{'PYTHONDONTWRITEBYTECODE':'1'},
                 'stdout':blob(p.stdout),'stderr':blob(p.stderr)})
    OUT.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    sys.stdout.buffer.write(p.stdout);sys.stderr.buffer.write(p.stderr)
    print(f'\n[captured sequence={len(rows)} exit={p.returncode}]')
    return p.returncode
if __name__=='__main__':raise SystemExit(main())
