"""Assemble immutable review inputs and static new-copy identities; no product execution."""
from pathlib import Path
import hashlib
import json
import subprocess
import tarfile
import datetime

prep = Path(__file__).resolve().parent
owner = prep.parents[3]
rows = json.loads((prep/'roots.json').read_text())['roots']
R = 'fdfd908e36a85140078aa1509f091de369157973'
P = 'f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3'
B = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
sha = lambda b: hashlib.sha256(b).hexdigest()
frozen = json.loads((owner/'docs/reviews/T07/round-1/frozen-manifest.json').read_text())
inline = [
 ('前一轮Z原始作者完整报告（原文不改）','docs/reviews/T07/launch-20261023/fresh-pair-snapshot/zcode/report.md'),
 ('前一轮M原始作者完整报告（原文不改）','docs/reviews/T07/launch-20261023/fresh-pair-snapshot/minimax/report.md'),
 ('前一轮本地封存独审（时点记录）','docs/reviews/T07/launch-20261023/fresh-pair-evidence-audit.md'),
 ('前一轮原生接收独立补审（解除旧UNKNOWN，保新缺项）','docs/reviews/T07/launch-20261023/native-receiving-20261023/independent-native-receiving-audit.md'),
 ('前一轮PROCESS_FAIL裁决及后继边界','docs/reviews/T07/launch-20261023/native-receiving-20261023/owner-process-disposition.md'),
 ('7项非阻断意见的现有依据、责任与延期处置','docs/reviews/T07/launch-20261023/native-receiving-20261023/seven-opinion-dispositions.json'),
]
common = [
 'docs/reviews/T07/current-dual-review-backlog-20261022.md',
 'docs/reviews/T07/current-dual-review-backlog-20261022.json',
 'docs/reviews/T07/current-dual-review-backlog-audit-20261022.md',
 'docs/reviews/T07/dispatch-20261022/guidance/developer-common-instructions.md',
 'docs/reviews/T07/dispatch-20261022/guidance/desktop-operation-policy-20261022.md',
 'docs/reviews/T07/round-1/README.md',
 'docs/reviews/T07/round-1/archive-manifest.json',
 'docs/reviews/T07/round-1/frozen-manifest.json',
 'docs/reviews/T07/round-1/historical-issues.md',
 'docs/reviews/T07/round-1/internal-review-original-finals.jsonl',
 'docs/reviews/T07/round-1/internal-review-sources.json',
 'docs/reviews/T07/round-1/preparation-audit.md',
] + [path for title,path in inline]
native = 'docs/reviews/T07/launch-20261023/native-receiving-20261023/'
for role in ['zcode','minimax']:
 for name in ['tool-calls.jsonl','tool-results.jsonl','report-write-edit-binding.json','attachment-read-reconstruction.json','final-response-candidates.jsonl']:
  common.append(native+role+'/'+name)
common += [native+'zcode/official-turn-events.json',native+'minimax/official-terminal-scalars.json',native+'minimax/inplace-probe-original-turn-provenance.json']
results=[]
for row in rows:
 role = row['role']; root = Path(row['root']); rt = Path(row['runtime']); scratch=Path(row['scratchCopy'])
 dest = root/'docs/reviews/T07/round-2-input'; dest.mkdir(exist_ok=False)
 source_entries=[]
 with tarfile.open(rt/'metadata/source-snapshot.tar') as t:
  for member in t.getmembers():
   if not member.isfile(): continue
   path=member.name; raw=t.extractfile(member).read(); a=(root/path).read_bytes(); c=(scratch/path).read_bytes()
   exception=path=='AGENTS.md'; expected=sha(raw)
   assert (sha(a)==expected and sha(c)==expected) or (exception and a==c==(owner/'AGENTS.md').read_bytes()),path
   source_entries.append({'path':path,'gitRef':R,'gitBytes':len(raw),'gitSha256':expected,'reviewBytes':len(a),'reviewSha256':sha(a),'scratchBytes':len(c),'scratchSha256':sha(c),'physicalMatchesGit':a==raw and c==raw,'protectedPolicyException':exception})
 inventory={'role':role,'sourceReviewHead':R,'sourceGitArchive':str(rt/'metadata/source-snapshot.tar'),'sourceGitArchiveSha256':sha((rt/'metadata/source-snapshot.tar').read_bytes()),'reviewRoot':str(root),'scratchCopy':str(scratch),'trackedFiles':len(source_entries),'exactGitFiles':sum(x['physicalMatchesGit'] for x in source_entries),'policyExceptions':[x['path'] for x in source_entries if not x['physicalMatchesGit']],'files':source_entries}
 for path in [dest/'full-git-files.json',prep/f'{role}-full-git-files.json']:path.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
 reading=[]
 def need(path,kind,ref=None):
  p=Path(path);raw=p.read_bytes();reading.append({'path':str(p),'kind':kind,'sourceRef':ref,'bytes':len(raw),'sha256':sha(raw),'textNewlines':raw.count(b'\n') if p.suffix.lower()!='.png' else None,'actualReadCompleted':False,'requiredVisibleEOF':True})
 # Physical root implementation + all f9 candidate references; source check is new-copy identity, not old-tree retest.
 for e in frozen['implementationTestFixtureEntries']:need(root/e['path'],'implementation-test-fixture-fulltext',P)
 for e in frozen['candidateFiles']:
  raw=subprocess.check_output(['git','show',P+':'+e['path']],cwd=root);assert sha(raw)==e['sha256']
  p=rt/'history/product-candidate'/e['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);need(p,'product-candidate-fulltext',P)
 need(root/'docs/reviews/T07/round-1/candidate.patch','complete-25-path-diff',P)
 prd='docs/prd/PRD-本体学习与落地Agent工作台.md';raw=subprocess.check_output(['git','show',B+':'+prd],cwd=root);p=rt/'history/approved-prd-v0.6.md';p.write_bytes(raw);need(p,'approved-PRD-complete',B)
 for path in common:need(root/path,'history-or-current-guidance-fulltext',R)
 need(root/'AGENTS.md','current-protected-policy')
 archives=[]
 with tarfile.open(root/'docs/reviews/T07/round-1/frozen-inputs.tar.gz') as t:
  for m in t.getmembers():
   if not m.isfile():continue
   p=rt/'history/frozen-inputs'/m.name;assert p.read_bytes()==t.extractfile(m).read();need(p,'sealed-original-image' if p.suffix=='.png' else 'sealed-original-fulltext')
   archives.append({'member':m.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
 assert len(archives)==75
 before=rt/'raw/probe-before';before.mkdir(exist_ok=False);p=scratch/'docs/reviews/T07/evidence/ui-probe.json';(before/'ui-probe.json').write_bytes(p.read_bytes())
 (before/'before-state.json').write_text(json.dumps({'sourceReviewHead':R,'scratchCwd':str(scratch),'uiProbeSha256':sha(p.read_bytes()),'widePNGExists':(scratch/'docs/reviews/T07/evidence/page-wide.png').exists(),'narrowPNGExists':(scratch/'docs/reviews/T07/evidence/page-narrow.png').exists(),'probeHasNotRun':True},ensure_ascii=False,indent=2)+'\n')
 ledger={'scope':'All required full sources + complete sealed history, not delta; every actualReadCompleted is initially false','role':role,'items':reading,'itemCount':len(reading),'archiveMembers':len(archives),'requiredImplementationEntries':14,'requiredCandidateEntries':25,'requiredDiff':'full candidate.patch','parentGapsRemainOpen':True}
 (dest/'required-reading.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n');(prep/f'{role}-required-reading.json').write_bytes((dest/'required-reading.json').read_bytes())
 prefix=(prep/'current-prefix-template.md').read_text()
 substitutions={'APP':'ZCode' if role=='zcode' else 'MiniMax Code','ROOT':str(root),'RUNTIME':str(rt),'MODEL':'GLM-5.3' if role=='zcode' else 'M3.1-Flash','EFFORT':'最高' if role=='zcode' else 'xhigh','PERMISSION':'完全访问' if role=='zcode' else '始终授权','REPORT':row['report'],'SCRATCH':str(scratch)}
 for k,v in substitutions.items():prefix=prefix.replace('{{'+k+'}}',v)
 assert '{{' not in prefix
 parts=[prefix.encode()]
 inline_records=[]
 for title,path in inline:
  raw=(root/path).read_bytes();parts += [('\n\n## BEGIN HISTORICAL FULL TEXT: '+title+'\nSource within this own root: '+path+'\nBytes: '+str(len(raw))+'; SHA256: '+sha(raw)+'\n\n').encode(),raw,b'\n## END HISTORICAL FULL TEXT\n'];inline_records.append({'title':title,'path':path,'bytes':len(raw),'sha256':sha(raw)})
 old=(owner/f'docs/reviews/T07/dispatch-20261022/{role}-full-input.txt').read_bytes();parts += [b'\n\n## BEGIN EXACT PREVIOUS COMPLETE INPUT BYTES (HISTORY ONLY; CURRENT RULES ABOVE)\n',old]
 full=b''.join(parts);ownerFull=prep/f'{role}-full-input.txt';ownerFull.write_bytes(full);(dest/'full-input.txt').write_bytes(full)
 (dest/'current-AGENTS.md').write_bytes((owner/'AGENTS.md').read_bytes());(dest/'operator-identity-receipt.template.json').write_bytes(Path(row['operatorReceipt']).read_bytes())
 data={**row,'base':B,'fullInputOwnerPath':str(ownerFull),'fullInputRolePath':str(dest/'full-input.txt'),'fullInputBytes':len(full),'fullInputNewlines':full.count(b'\n'),'fullInputSha256':sha(full),'oldCompleteInputSuffixBytes':len(old),'oldCompleteInputSuffixSha256':sha(old),'oldCompleteInputSuffixExact':full.endswith(old),'embeddedHistoricalTexts':inline_records,'readingItems':len(reading),'trackedSourceFiles':len(source_entries),'trackedExactGitFiles':inventory['exactGitFiles'],'protectedPolicyOnlyException':inventory['policyExceptions']==['AGENTS.md'],'archiveOriginalMembers':75,'archiveLogPNGOriginals':35,'actualTaskSettings':None,'actualSessionId':None,'originalTurnId':None,'officialTerminal':None,'externalVerdict':None,'newTasks':0,'GUIReleased':True,'productExecutedByPreparation':False,'newRootSetup':json.loads((prep/f'{role}-setup.json').read_text())}
 for p in [dest/'input-manifest.json',prep/f'{role}-input-manifest.json']:p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 results.append(data)
(prep/'dispatch-manifest.json').write_text(json.dumps({'preparedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewHead':R,'product':P,'base':B,'roles':results,'newExternalTasks':0,'GUIReleased':True,'rootPreflight':'PENDING','independentPreflight':'PENDING','ownerProductRetests':0,'scopeReduced':False,'priorRound':'PROCESS_FAIL retained; no original verdict rewrite'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{'role':x['role'],'bytes':x['fullInputBytes'],'newlines':x['fullInputNewlines'],'sha256':x['fullInputSha256'],'readingItems':x['readingItems'],'trackedFiles':x['trackedSourceFiles'],'exactGitFiles':x['trackedExactGitFiles'],'policyExceptionOnly':x['protectedPolicyOnlyException']} for x in results],ensure_ascii=False))
