"""Exclusive final R2 receipt/command trace; read-only Git and fixed bytes only."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
ROOT=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design');R=ROOT/'docs/reviews/I05/d2-business-carrier-design'
PREFIX='docs/reviews/I05/d2-business-carrier-design/'
def sha(b):return hashlib.sha256(b).hexdigest()
def st(b):return {'bytes':len(b),'sha256':sha(b),'base64':base64.b64encode(b).decode()}
log=[]
def run(argv):
 p=subprocess.run(argv,cwd=ROOT,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 log.append({'argv':argv,'cwd':str(ROOT),'envDelta':{'PYTHONDONTWRITEBYTECODE':'1'},'exit':p.returncode,'stdout':st(p.stdout),'stderr':st(p.stderr)})
 assert p.returncode==0
 return p.stdout.decode()
def write(name,value):
 with (R/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
branch=run(['/usr/bin/git','branch','--show-current']).strip();head=run(['/usr/bin/git','rev-parse','HEAD']).strip();index=run(['/usr/bin/git','diff','--cached','--name-only']);tracked=run(['/usr/bin/git','diff','--name-only']).splitlines();status=run(['/usr/bin/git','status','--short','--untracked-files=all'])
assert branch=='docs/I05-d2-consumer-design' and head=='a23a2550c163e9571adebaf983f7c50909c2f09c' and not index and tracked==['AGENTS.md']
for line in status.splitlines():
 if line==' M AGENTS.md':continue
 assert line.startswith('?? '+PREFIX),line
 n=line[len('?? '+PREFIX):]
 assert '/' not in n and (n.startswith('independent-r2-') or n in ('independent-review-r2.md','independent-proof-r2.json')),line
identity=json.loads((R/'independent-r2-identity.json').read_bytes());assert identity['allMatches']
frozen=[]
for e in identity['rows']:
 b=(ROOT/e['path']).read_bytes();assert len(b)==e['bytes'] and sha(b)==e['sha256'],e['path']
 frozen.append({'path':e['path'],'bytes':len(b),'sha256':sha(b)})
assert len(frozen)==159
assert json.loads((R/'independent-proof-r2.json').read_bytes())['allChecksPassed']
assert sha((ROOT/'AGENTS.md').read_bytes())=='de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'
write('independent-r2-final-commands.json',log)
excluded=['independent-r2-receipt.json','independent-r2-seal-execution.json'];members=[]
for p in sorted(R.iterdir()):
 if p.name in excluded or not (p.name.startswith('independent-r2-') or p.name in ('independent-review-r2.md','independent-proof-r2.json')):continue
 b=p.read_bytes();members.append({'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)})
value={'format':'i05-business-independent-r2-receipt/1','verdict':'Pass limited pure-design delta','r1Disposition':{'R1-F01/P2':'closed only normative failure expressibility / caller-entry versus child-context separation','R1-F02/P2':'closed only normative caller-origin collection and reference expressibility'},'revisionBase':'aefa82e51643e0a75ecb960645d63917b046edd6','candidate':'707c3915bc28a92955638cba4e6b8e3c18e8cfac','process':head,'branch':branch,'fixed159':frozen,'old113CurrentRestored':True,'interimFrozenWriteViolation':True,'notClaimingWholeProcessFrozenCompliance':True,'knownEvidenceGaps':['initial unexecuted draft exact bytes/hash not separately preserved','no independent event wall-clock','initial read split streams not independently captured','no complete post-context collected fixture; identity-only checks not runtime/collection proof'],'indexEmpty':True,'trackedDirtyOnly':['AGENTS.md'],'actualStatusBeforeFinalEvidence':status,'members':members,'memberCount':len(members),'excludedSelf':PREFIX+excluded[0],'excludedLaterCapture':PREFIX+excluded[1],'noCycle':'root independently fixes receipt and later capture hashes; no future hash recorded here','formatBoundary':'report/proof/identity summary explicitly prettier check exit0; raw command captures and later receipt not claimed formatted','writesStoppedAfterCaptureReturns':True,'rootOwnsFinalReception':True}
write('independent-r2-receipt.json',value)
b=(R/'independent-r2-receipt.json').read_bytes()
print(json.dumps({'verdict':value['verdict'],'receipt':{'bytes':len(b),'sha256':sha(b)},'memberCount':len(members),'members':members,'fixedOld113New46Unchanged':True,'indexEmpty':True,'gitExitSequence':[x['exit'] for x in log]},ensure_ascii=False,indent=2))
