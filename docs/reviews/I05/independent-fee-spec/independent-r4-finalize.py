"""Seal only fresh independent R4 artifacts. No candidate imports or mutations."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HEAD = '29705204c9f8274d7ab17433bd6ac3094461244b'
COMMANDS = []

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return {'bytes': len(b), 'sha256': sha(b), 'utf8': b.decode(), 'base64': base64.b64encode(b).decode()}
def call(argv):
    p = subprocess.run(argv, cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), capture_output=True, check=False)
    COMMANDS.append({'argv': argv, 'cwd': str(ROOT), 'exit': p.returncode, 'environmentOverride': {'PYTHONDONTWRITEBYTECODE':'1'}, 'stdout': blob(p.stdout), 'stderr': blob(p.stderr)})
    assert p.returncode == 0, argv
    return p.stdout
def read(name): return json.loads((HERE/name).read_text())
def describe(p):
    b=p.read_bytes()
    return {'path':str(p.relative_to(ROOT)), 'bytes':len(b), 'sha256':sha(b)}
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    one=read('independent-r4-recompute-1.json');two=read('independent-r4-recompute-2.json');integrity=read('independent-r4-integrity.json');bounds=read('independent-r4-boundaries.json')
    assert one['items']==two['items'] and one['seed']=='1' and two['seed']=='2'
    assert one['fixedCount']==114 and one['completeEntryCases']==27 and len(one['items'])==141
    assert len(bounds['cases'])==25 and bounds['failedCases']==21 and bounds['successCases']==4 and bounds['allReplayReceiptAssertionsPassed']
    for row in integrity['members']:
        p=ROOT/row['path'];b=p.read_bytes();assert (len(b),sha(b))==(row['bytes'],row['sha256']),row['path']
    assert (len((ROOT/'AGENTS.md').read_bytes()),sha((ROOT/'AGENTS.md').read_bytes()))==(15147,'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4')
    report=HERE/'independent-review-r4.md';proof=HERE/'independent-proof-r4.json';final=HERE/'independent-r4-final-check.json'
    proof.write_text('{}\n');final.write_text('{}\n')
    prettier=['/usr/local/bin/node','/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs','--ignore-path','/dev/null']
    report.write_bytes(call(prettier+[str(report)]))
    assert call(['git','rev-parse','HEAD']).decode().strip()==HEAD
    branch=call(['git','branch','--show-current']).decode().strip();assert branch=='docs/I05-independent-fee-spec'
    assert not call(['git','diff','--cached','--name-only'])
    assert call(['git','diff','--name-only']).decode().splitlines()==['AGENTS.md']
    new=call(['git','ls-files','--others','--exclude-standard']).decode().splitlines()
    expected=sorted(str(p.relative_to(ROOT)) for p in HERE.glob('independent-r4-*'))+ [str(report.relative_to(ROOT)),str(proof.relative_to(ROOT))]
    assert sorted(new)==sorted(expected),(new,expected)
    status=call(['git','status','--short','--untracked-files=all']).decode()
    call(['git','diff','--check']);call(['git','diff','--cached','--check'])
    logs=read('independent-r4-command-log.json')
    nonzero=[{'sequence':x['sequence'],'argv':x['argv'],'exit':x['exit']} for x in logs if x['exit']!=0]
    assert len(nonzero)==1 and nonzero[0]['exit']==1 and nonzero[0]['argv'][:3]==['git','diff','--no-index']
    members=[describe(ROOT/p) for p in new if p not in (str(proof.relative_to(ROOT)),str(final.relative_to(ROOT)))]
    payload={'format':'i05-independent-fee-spec-review-r4/1','verdict':'Pass','scope':'proposal-only specification and fee mathematics; not product runtime or actual authority','revisionBase':integrity['revisionBase'],'candidate':integrity['candidate'],'processHEAD':HEAD,'branch':branch,'R3Dispositions':{'R3-F1/P1':'closed within authorized proposal scope','R3-F2/P2':'closed within authorized proposal scope'},'newPriorityFindings':[],
      'integrity':{'all269CurrentGitSHA':True,'all203OldUnchanged':True,'delta66AdditionsOnly':True,'candidateMembers':integrity['members'],'guidance':integrity['guidance']},
      'verification':{'all141FieldsBothSeeds':True,'seedItemsIdentical':True,'allDoubleTapesReplayed':True,'all141IFR3IndependentlyDecoded':True,'fixedAnalysisEvents':one['fixedAnalysisEvents'],'fixedExecutionEvents':one['fixedExecutionEvents'],'independentDeltaTotals':one['independentDeltaTotals'],'freshBoundaryCalls':25,'expectedRefusals':21,'successes':4,'authorFocusedMethodsExit':0,'authorReadonlyAuditExit':0,'unchangedNumericAndSmallLedgerRerun':False},
      'commands':{'captureLog':describe(HERE/'independent-r4-command-log.json'),'nonzero':nonzero,'directToolBoundary':[{'argv':['pwd'],'cwd':str(ROOT),'exit':0,'combinedOutput':blob((str(ROOT)+'\n').encode()),'splitStreamsAvailable':False,'note':'observed exec_command output only; no invented stdout/stderr'}]},
      'artifactMembers':members,'newFileCount':len(new),'newFiles':sorted(new),'git':{'HEAD':HEAD,'indexEmpty':True,'trackedUnstaged':['AGENTS.md'],'status':status},
      'pending':['current actual codec','actual same-issue 17L / issuer / usage / capture','actual Catalog and source authority','owner H','JobStore and platform runtime','417 and parent gates'],
      'historicalFailures':'Author and earlier independent failures remain in immutable originals; unknown exits remain unknown; no old failure version rerun.',
      'sealNote':'Final-check records final formatting/check commands and report/proof identities; proof excludes its own hash and final-check hash to avoid cycles.'}
    write(proof,payload);proof.write_bytes(call(prettier+[str(proof)]))
    call(prettier+['--check',str(report),str(proof)])
    final_members=[describe(ROOT/p) for p in new if p!=str(final.relative_to(ROOT))]
    write(final,{'format':'i05-independent-r4-final-check/1','verdict':'Pass','HEAD':HEAD,'branch':branch,'indexEmpty':True,'candidate269UnchangedAtSeal':True,'original203PreviouslyVerifiedUnchanged':True,'newFileCount':len(new),'newFiles':sorted(new),'membersExcludingSelf':final_members,'report':describe(report),'proof':describe(proof),'commands':COMMANDS,'status':status,'outerFinalizerExit':'see actual tool result; not predicted here'})
    print(json.dumps({'report':describe(report),'proof':describe(proof),'finalCheck':describe(final),'HEAD':HEAD,'indexEmpty':True,'newFileCount':len(new),'newFiles':sorted(new),'nonzeroCommands':nonzero},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
