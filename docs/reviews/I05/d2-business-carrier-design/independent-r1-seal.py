"""Final read-only Git/current-byte freeze; writes only own trace and receipt.

Receipt excludes itself and the later capture-wrapper execution record.
Does not stage, commit, switch, mutate guidance or touch fixed inputs.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
OUT=ROOT/'docs/reviews/I05/d2-business-carrier-design'
PREFIX='docs/reviews/I05/d2-business-carrier-design/'
def sha(b):
    return hashlib.sha256(b).hexdigest()
def data_record(b):
    return {'bytes':len(b),'sha256':sha(b),'base64':base64.b64encode(b).decode()}
log=[]
def run(argv):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    log.append({'argv':argv,'cwd':str(ROOT),'envDelta':{'PYTHONDONTWRITEBYTECODE':'1'},'exit':p.returncode,'stdout':data_record(p.stdout),'stderr':data_record(p.stderr)})
    assert p.returncode==0, argv
    return p.stdout.decode()
tracked=run(['/usr/bin/git','diff','--name-only']).splitlines()
index=run(['/usr/bin/git','diff','--cached','--name-only'])
branch=run(['/usr/bin/git','branch','--show-current']).strip()
head=run(['/usr/bin/git','rev-parse','HEAD']).strip()
status=run(['/usr/bin/git','status','--short','--untracked-files=all'])
assert tracked==['AGENTS.md'] and not index
assert branch=='docs/I05-d2-consumer-design' and head=='3f171f7d1fb481d669acb92b835b4bb96a3bc584'
for line in status.splitlines():
    if line==' M AGENTS.md':
        continue
    assert line.startswith('?? '+PREFIX),line
    filename=line[len('?? '+PREFIX):]
    assert '/' not in filename and (filename.startswith('independent-r1-') or filename in ('independent-review-r1.md','independent-proof-r1.json')),line
identity=json.loads((OUT/'independent-r1-identity.json').read_bytes())
frozen=[]
for entry in identity['new']+identity['old']:
    b=(ROOT/entry['path']).read_bytes()
    expected=entry['sha256']
    assert sha(b)==expected and len(b)==entry['bytes'],entry['path']
    frozen.append({'path':entry['path'],'bytes':len(b),'sha256':sha(b)})
assert len(frozen)==90
assert sha((ROOT/'AGENTS.md').read_bytes())=='de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'
(OUT/'independent-r1-final-commands.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
excluded=['independent-r1-receipt.json','independent-r1-seal-execution.json']
members=[]
for path in sorted(OUT.iterdir()):
    if path.name in excluded or not (path.name.startswith('independent-r1-') or path.name in ('independent-review-r1.md','independent-proof-r1.json')):
        continue
    b=path.read_bytes()
    members.append({'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)})
receipt={'format':'i05-business-carrier-independent-r1-receipt/1','verdict':'Fail limited pure-design','findingIds':['R1-F01/P2','R1-F02/P2'],'base':'dc3fc7768167f206e09b410da4f737199d2c5e18','candidate':'cedefb069ddf77e48c2764793490517ab967aae3','process':head,'branch':branch,'fixedInputsVerifiedAtEnd':frozen,'unchangedNewCount':33,'unchangedOldCount':57,'indexEmpty':not index,'trackedDirtyOnly':['AGENTS.md'],'actualStatusBeforeFinalEvidence':status,'members':members,'memberCount':len(members),'excludedSelf':PREFIX+excluded[0],'excludedLaterExecutionTrace':PREFIX+excluded[1],'laterTraceReason':'Capture wrapper creates it after this receipt is complete; root fixes both hashes externally. No self/future hash reference.','formatBoundary':'Report, proof, identity summary and provenance summary explicitly prettier checked exit0. Lossless command records and later receipt are raw evidence JSON, not claimed in that format check.','writesStoppedAfterWrapperReturns':True,'rootOwnsFinalSeal':True}
receipt_path=OUT/'independent-r1-receipt.json'
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'receipt':{'path':str(receipt_path.relative_to(ROOT)),'bytes':len(receipt_path.read_bytes()),'sha256':sha(receipt_path.read_bytes())},'memberCount':len(members),'members':members,'new33AndOld57StillUnchanged':True,'indexEmpty':True,'exitBoundary':'all five read-only final Git commands exit0; outer capture records this script exit'},ensure_ascii=False,indent=2))
