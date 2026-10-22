"""Seal reviewer documents only; formatter is read-only and emits stdout."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
PY='/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12'
NODE='/usr/local/bin/node'
PRETTIER='/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs'
REPORT=HERE/'independent-review-r2.md'
PROOF=HERE/'independent-proof-r2.json'
records=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return {'bytes':len(b),'sha256':sha(b),'utf8':b.decode(),'base64':base64.b64encode(b).decode()}
def run(argv,data=None):
    p=subprocess.run(argv,cwd=ROOT,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,
                     env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    records.append({'argv':argv,'cwd':str(ROOT),'exit':p.returncode,'stdin':None if data is None else {'bytes':len(data),'sha256':sha(data)},'stdout':blob(p.stdout),'stderr':blob(p.stderr)})
    assert p.returncode==0
    return p.stdout
def load(name):return json.loads((HERE/name).read_bytes())
def ident(path):
    raw=path.read_bytes();return {'path':str(path.relative_to(ROOT)),'bytes':len(raw),'sha256':sha(raw)}
def format_file(path):
    path.write_bytes(run([NODE,PRETTIER,'--stdin-filepath',str(path)],path.read_bytes()))

assert not PROOF.exists() and not (HERE/'independent-r2-final-check.json').exists()
PROOF.write_bytes(b'')
(HERE/'independent-r2-final-check.json').write_bytes(b'')
format_file(REPORT)
one,two=load('independent-r2-recompute-1.json'),load('independent-r2-recompute-2.json')
assert one['items']==two['items'] and one['allFullFieldsMatch'] and two['allFullFieldsMatch']
integrity=load('independent-r2-integrity.json')
head=run(['git','rev-parse','HEAD']).decode().strip()
index=run(['git','diff','--cached','--name-only']).decode()
status=run(['git','status','--short']).decode()
assert head==integrity['HEAD'] and not index
run(['git','diff','--check'])
run(['git','diff','--cached','--check'])
artifacts=integrity['artifacts']
for x in artifacts:
    raw=(ROOT/x['path']).read_bytes();assert (len(raw),sha(raw))==(x['bytes'],x['sha256'])
guidance=ident(ROOT/'AGENTS.md')
assert guidance['bytes']==15147 and guidance['sha256']=='de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'
logs=load('independent-r2-command-log.json')
adversarial=load('independent-r2-adversarial.json')
refs=[ident(p) for p in sorted(HERE.glob('independent-r2-*')) if p.is_file()]
evidence={
 'format':'i05-independent-fee-review-r2/1','verdict':'Fail','scope':'proposal-only normative fee mathematics; no product conclusion',
 'reviewerTask':'/root/independent_fee_spec_review_r2','base':integrity['baseRevisionProcessDeltas'],
 'fixedHEAD':head,'candidateRef':'7554c5582619a2beddaa42bf08ffd1a8e1961214',
 'revisionBase':'ac6e0a91763ea18d5e17e162a275822e7caee8f4','branch':integrity['branch'],
 'report':ident(REPORT),'all113FrozenArtifactsUnchanged':True,'artifactInventory':artifacts,
 'guidanceCurrent':guidance,'guidanceFrozenHistorical':integrity['guidanceFrozenHistorical'],
 'policyChange':'authorized rule-owner update; current AGENTS reread; no candidate edits or automatic rerun',
 'finalHEAD':head,'finalIndex':index,'finalStatus':status,
 'findings':[{'id':'R2-F1','priority':1,'title':'complete semantic-error entry has no failed fee invoice/H01 and cannot deliver earlier resource first',
              'evidenceCases':['late-input-invalid-integer','false-then-type-error','resource-before-late-lexical']},
             {'id':'R2-F2','priority':2,'title':'compile skips known head permissions and predicate structure for variable/disabled/zero-match rules',
              'evidenceCases':['uncontrolled-head-zero-match','uncontrolled-head-disabled','variable-predicate-disabled']}],
 'r1Disposition':{'F1':'partially addressed; remains open due to complete error program and compile gates',
                  'F2':'closed within reviewed pure state machine; independent69/70 strengthened boundary passes',
                  'F3':'closed within reviewed pure state machine; whole vector and cumulative lifetime proof passes'},
 'checks':{'originalMethods':8,'oldHandVectors':19,'lifetimeMethods':8,'typedMethods':13,
           'q6DomainClassifications':486,'numericTruths':648,'independentIEEEBoundaries':11,
           'recomputedProgramsPerSeed':114,'recomputedEventsPerSeed':219815,'seeds':['1','2'],
           'allFullFieldsAndPrefixArithmeticMatch':True,'twoIndependentRecomputeOutputsEqual':True,
           'baselinePrefixes':2282,'baselineInputBytes':85953,'baselineReceiptBytes':782,
           'fullPerIdInheritedFieldsUnchanged':True,'badSuppliedFieldOriginPointers':0},
 'bootstrapToolOnlyCommands':[
   {'argv':['pwd'],'cwd':str(ROOT),'exit':0,'combinedStdout':str(ROOT)+'\n','separateStderrNotAvailable':True},
   {'argv':['cat','AGENTS.md'],'cwd':str(ROOT),'exit':0,'streamCapture':'exact combined output retained in initiating tool transcript; not copied/recreated here','separateStreamsAvailable':False},
   {'argv':['cat','/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/I05-independent-fee-spec-design-window.md','/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/I05-independent-fee-spec-setup-proof.md','/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/I05-fee-F1-proposal-binder-and-charge-interpreter-amendment.md'],
    'cwd':str(ROOT),'exit':1,'reason':'setup-proof.md absent; actual .json discovered next; no product failure',
    'streamCapture':'exact combined output retained in initiating tool transcript; not reconstructed as split streams','separateStreamsAvailable':False},
   {'argv':['rg','--files','/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release','-g','*I05*setup*','-g','*I05*proof*'],'cwd':str(ROOT),'exit':0,'streamCapture':'exact combined output retained in initiating tool transcript','separateStreamsAvailable':False},
   {'argv':['rg','--files','docs/iterations/I05/independent-fee-spec','docs/reviews/I05/independent-fee-spec'],'cwd':str(ROOT),'exit':0,'streamCapture':'exact combined output retained in initiating tool transcript','separateStreamsAvailable':False}],
 'capturedCommands':logs,'independentIntegritySubprocesses':integrity['subprocessCommands'],
 'sealCommands':records,'evidenceFiles':refs,
 'sealCommandCaptureBoundary':'proof formatting/check commands and seal process completion follow this snapshot; exact completion is in tool transcript and independent-r2-final-check.json; no future exit/self hash fabricated',
 'firstFailuresPreserved':{'R1':'original formal Fail unchanged','authorIncident':'not-independent unchanged; draft opaque hash only',
                          'oldDeterminism':'2240/2239; comparator exit1; each subprocess exit0 retained',
                          'q6Literal':'13 vs15 actual test exit1 retained','oldUnknownExit':'remains unknown',
                          'thisReviewFirstCommandFailure':'missing setup-proof.md actual cat exit1'},
 'notRun':['product imports/execution','pytest','npm check/build','RDFLib/pySHACL','native/DB/GUI','network/install/version probes','417 product oracle','mutating author drivers','old failure version','stage/commit/push','Goal or external-chat changes'],
 'pending':['current native/wire/planDigest/fingerprint codec','real same-issue17L/usage/issuer/capture/source permissions','real ownerH/Job/Store','57/six-iteration/SQLiteHOLD/wholeH/owner gates','same-version designated dual-model/CI/twoOS/human/develop gates']}
PROOF.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
format_file(PROOF)
run([NODE,PRETTIER,'--check',str(REPORT),str(PROOF)])
final={'report':ident(REPORT),'proof':ident(PROOF),'commands':records,
       'actualCompletedSubprocessExits':[x['exit'] for x in records],
       'sealProcess':{'argv':[sys.executable,*sys.argv],'cwd':str(ROOT),'completionEvidence':'actual parent tool result, not prefilled exit'},
       'HEAD':head,'index':index,'statusAtSeal':status,'all113FrozenArtifactsUnchanged':True}
(HERE/'independent-r2-final-check.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in final.items() if k!='commands'},ensure_ascii=False,indent=2))
