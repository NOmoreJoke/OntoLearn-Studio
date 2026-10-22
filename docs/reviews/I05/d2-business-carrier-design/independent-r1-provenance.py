"""Record pure-input reads, fixed D1 origins and author historical failures.

No author checker text execution. Only /bin/cat and read-only git show.
Writes independent-r1-provenance* files in the approved review directory.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
OUT=ROOT/'docs/reviews/I05/d2-business-carrier-design'
DESIGN=ROOT/'docs/iterations/I05/d2-business-carrier-design'
CONTROL=Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release')
def sha(data):
    return hashlib.sha256(data).hexdigest()
def stream(data):
    return {'bytes':len(data),'sha256':sha(data),'base64':base64.b64encode(data).decode()}
log=[]
def run(argv):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    log.append({'argv':argv,'cwd':str(ROOT),'envDelta':{'PYTHONDONTWRITEBYTECODE':'1'},'exit':p.returncode,'stdout':stream(p.stdout),'stderr':stream(p.stderr)})
    return p
inputs=json.loads((OUT/'input-identity.json').read_bytes())
reads=[]
for path in [ROOT/'AGENTS.md',*(CONTROL/name for name in ('developer-common-instructions.md','desktop-operation-policy-20261022.md','external-review-permissions.md')),*sorted(DESIGN.iterdir())]:
    p=run(['/bin/cat',str(path)])
    reads.append({'path':str(path),'exit':p.returncode,'bytes':len(p.stdout),'sha256':sha(p.stdout)})
origins=[]
for entry in inputs['rootInputs']+inputs['newD1AuthorizedPureInputs']:
    if 'repository' in entry:
        p=run(['/usr/bin/git','-C',entry['repository'],'show',entry['ref']+':'+entry['path']])
    else:
        p=run(['/bin/cat',entry['path']])
    local=(OUT/entry['local']).read_bytes()
    origins.append({**entry,'exit':p.returncode,'actualBytes':len(p.stdout),'actualSha256':sha(p.stdout),'matchesLocalAndDeclared':p.returncode==0 and p.stdout==local and len(local)==entry['bytes'] and sha(local)==entry['sha256']})
historical=[]
for i in range(1,6):
    name='author-check-'+str(i).zfill(2)+'.json'
    record=json.loads((OUT/name).read_bytes())
    streams=[]
    for channel in ('stdout','stderr'):
        data=record[channel]['text'].encode()
        streams.append({'channel':channel,'matchesBytesAndSha':len(data)==record[channel]['bytes'] and sha(data)==record[channel]['sha256']})
    historical.append({'path':name,'exit':record['exit'],'streams':streams})
result={'scope':'pure readbacks only; no actual source/body or author code execution','reads':reads,'exactD1AndRootOrigins':origins,'allOriginsMatch':all(x['matchesLocalAndDeclared'] for x in origins),'authorHistoricalChecks':historical,'authorExitSequence':[x['exit'] for x in historical],'authorReadonlyDiagnostic':json.loads((OUT/'first-failure-disposition.json').read_bytes())['readOnlyToolFailure'],'initialInteractiveReadBoundary':'Initial exploratory reads are preserved by the tool transcript; this file records fresh complete pure-input readback argv/cwd/exit and split streams, not a reconstruction of earlier commands.'}
(OUT/'independent-r1-provenance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'independent-r1-provenance-commands.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'readCount':len(reads),'originCount':len(origins),'allOriginsMatch':result['allOriginsMatch'],'authorExitSequence':result['authorExitSequence'],'authorStreamsVerified':all(s['matchesBytesAndSha'] for row in historical for s in row['streams']),'authorReadonlyDiagnosticExit':result['authorReadonlyDiagnostic']['exit']},ensure_ascii=False,indent=2))
