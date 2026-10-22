"""Final reviewer-only seal, with explicit read-only formatter ignore path."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
REPORT=HERE/'independent-review-r3.md'
PROOF=HERE/'independent-proof-r3.json'
FINAL=HERE/'independent-r3-final-check.json'
NODE='/usr/local/bin/node'
FMT='/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs'
records=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return {'bytes':len(b),'sha256':sha(b),'utf8':b.decode(),'base64':base64.b64encode(b).decode()}
def run(argv,data=None):
    p=subprocess.run(argv,cwd=ROOT,input=data,capture_output=True,check=False,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    records.append({'argv':argv,'cwd':str(ROOT),'stdin':None if data is None else {'bytes':len(data),'sha256':sha(data)},
                    'exit':p.returncode,'stdout':blob(p.stdout),'stderr':blob(p.stderr)})
    assert p.returncode==0,(argv,p.stderr)
    return p.stdout
def ident(p):
    raw=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(raw),'sha256':sha(raw)}
def load(name):return json.loads((HERE/name).read_bytes())
def fmt(path):path.write_bytes(run([NODE,FMT,'--ignore-path','/dev/null','--stdin-filepath',str(path)],path.read_bytes()))

assert not PROOF.exists() and not FINAL.exists()
PROOF.write_bytes(b'');FINAL.write_bytes(b'')
fmt(REPORT)
integrity=load('independent-r3-integrity.json')
one,two=load('independent-r3-recompute-1.json'),load('independent-r3-recompute-2.json')
assert one['items']==two['items'] and one['allCompleteResultsMatch'] and two['allCompleteResultsMatch']
assert (one['analysisFixedEvents'],one['executionFixedEvents'])==(231960,231899)
for row in integrity['members']:
    raw=(ROOT/row['path']).read_bytes();assert (len(raw),sha(raw))==(row['bytes'],row['sha256'])
head=run(['git','rev-parse','HEAD']).decode().strip();assert head==integrity['fixedHEAD']
branch=run(['git','branch','--show-current']).decode().strip();assert branch=='docs/I05-independent-fee-spec'
index=run(['git','diff','--cached','--name-only']).decode();assert not index
status=run(['git','status','--short']).decode()
untracked=run(['git','ls-files','--others','--exclude-standard','-z']).decode().rstrip('\0').split('\0')
assert all(p.startswith('docs/reviews/I05/independent-fee-spec/independent-r3-') or p in ('docs/reviews/I05/independent-fee-spec/independent-review-r3.md','docs/reviews/I05/independent-fee-spec/independent-proof-r3.json') for p in untracked)
tracked=run(['git','diff','--name-only']).decode().splitlines();assert tracked==['AGENTS.md']
run(['git','diff','--check']);run(['git','diff','--cached','--check'])
ag=ident(ROOT/'AGENTS.md');assert ag['bytes']==15147 and ag['sha256']=='de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'
refs=[ident(p) for p in sorted(HERE.glob('independent-r3-*')) if p.is_file() and p!=FINAL]
log=load('independent-r3-command-log.json')
nonzero=[{'sequence':x['sequence'],'argv':x['argv'],'exit':x['exit']} for x in log if x['exit']]
assert len(nonzero)==1 and nonzero[0]['argv'][:3]==['git','diff','--no-index'] and nonzero[0]['exit']==1
proof={
 'format':'i05-independent-fee-delta-review-r3/1','verdict':'Fail','scope':'pure proposal normative/math only; no product runtime conclusion',
 'reviewerTask':'/root/independent_fee_spec_review_r2','revisionBase':integrity['revisionBase'],'candidate':integrity['candidate'],'fixedHEAD':head,'branch':branch,
 'report':ident(REPORT),'artifactCount':189,'artifactInventory':integrity['members'],'all189CurrentGitDeclaredSha':True,
 'oldEvidenceCount':130,'all130CurrentEqualsRevisionBaseGit':True,'addedCandidateDocs':59,'candidateDelta':integrity['deltaStatusPaths'],
 'AGENTS':ag,'finalIndex':index,'finalStatus':status,'newReviewFileCount':len(untracked),'newReviewFiles':untracked,
 'findings':[{'id':'R3-F1','priority':1,'case':'nonstring-rule-id','reason':'plain JSON rule_id=7 lacks required type gate before allocation; caught error rethrows in receipt .encode; no invoice'},
             {'id':'R3-F2','priority':2,'case':'variable-rdf-type-object','reason':'fixed integration.md:59 requires declared Class TermInput; variable object unexpectedly completes'}],
 'r2Disposition':{'F1':'original six cases fixed; remains open due to new metadata failure path',
                  'F2':'original static cases fixed; related new type-object language widening is R3-F2'},
 'checks':{'independentFixedProgramsPerSeed':114,'independentOriginalErrorInputsPerSeed':6,'seeds':['1','2'],
           'all120FullFieldsEqual':True,'bothTapesIndependentlyReplayed':True,'all120IFR3Decoded':True,
           'analysisFixedEventsPerSeed':231960,'executionFixedEventsPerSeed':231899,
           'originalSixInputJSONFieldsUnchanged':True,'R3Source':'5da6cf11b8876d7823407b05474ec0ce3fe3a33c2f3c3464bfae96c2a87a1118',
           'newCompleteEntryAuthorMethodsActualExit0':10,'authorIndependentAuditActualExit':0,'old13TypedTestBytesUnchanged':True,
           'oldSmallLedgerNotRerun':True,'newAdversarialInvoicesAudited':8,'newMetadataExceptionCases':1,
           'freshAliasSourceObjects':[1,6],'freshAliasFullInvoicesEqual':True,'freshAliasScanHashOccurrences':[6,6],
           'lateHeadPaidHeads2Trace1Firing0Output0':True,'M0WorkBoundary':[10367,10368,10369],
           'H01InsufficientBoundary':{'need':19166,'loweredCap':19165,'firstEvent':2,'H01Paid':False,'allPaid0':True,'failedLive0':True},
           'baselineEvents':2410,'baselineReceiptBytes':792,'baselineInputBytes':85953},
 'evidenceFiles':refs,'commandLog':ident(HERE/'independent-r3-command-log.json'),'capturedCommandCount':len(log),
 'actualNonzeroCommands':nonzero,'nonzeroExplanation':'git diff --no-index exit1 means known v2/v3 differences; lossless stream retained, not a failed verification',
 'commandStreams':'exact argv/cwd/exit/separate stdout/stderr UTF8/base64/bytes/SHA from first command; integrity Git blob outputs explicitly opaque hashes',
 'sealCommandsSnapshot':records.copy(),'sealProcess':{'argv':[sys.executable,*sys.argv],'cwd':str(ROOT),'actualExitEvidence':'parent tool completion; no future exit prefilled'},
 'finalSealEvidence':'independent-r3-final-check.json includes formatter output/check argv and separate streams, actual completed subprocess exits, final bytes/SHA; proof does not self-hash',
 'retainedFailures':['original R1/R2 Fail','v1 not-independent quarantine','old2240/2239 determinism comparator exit1','old13vs15 typed failure','R3 expected49 actual53 exit1','R3 audit01 map order exit1','R3 audit04 unopenedM exit1','R3 titlequery exit2','R3 patch tool exitunknown','R3 firstmanifest numeric typo attempt01'],
 'rootReportedReadOnlyProcessBoundaries':[{'event':'initial R3 manifest artifacts key lookup','exit':1,'corrected':'members189 exit0','notCandidateFailure':True},
  {'event':'R2 seal new-file count17 assertion','exit':1,'corrected':'16 new review files plus AGENTS status line','notCandidateFailure':True}],
 'pending':['current native/wire/typed/planDigest/fingerprint codec','real same-issue17L/issuer/usage/capture/permissions','real ownerH/Job/Store','57/six-iteration/SQLiteHOLD/wholeH/owner gates','designated same-version dual-model/CI/twoOS/human/develop gates'],
 'notReadOrRun':['quarantine v1 raw contents','whole2d5/neighbor actual','product algorithms/actual/probes/generators','other product worktrees/backup/D2/WIP','old reviewer/collector or old failure code','mutating R3 drivers','product/pytest/npm/build/RDFLib/pySHACL/native/GUI/DB/network/install/version/model','417 product oracle/T05 candidate','stage/commit/push/branch change/environment/Goal/external chat']}
PROOF.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
fmt(PROOF)
run([NODE,FMT,'--ignore-path','/dev/null','--check',str(REPORT),str(PROOF)])
final={'report':ident(REPORT),'proof':ident(PROOF),'HEAD':head,'branch':branch,'index':index,'status':status,
       'newReviewFileCount':len(untracked),'newReviewFiles':untracked,'all189FrozenArtifactsUnchanged':True,
       'commands':records,'actualCompletedSubprocessExits':[x['exit'] for x in records],
       'outerSealCompletion':'actual tool result is authoritative; no self future exit claim'}
FINAL.write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in final.items() if k!='commands'},ensure_ascii=False,indent=2))
