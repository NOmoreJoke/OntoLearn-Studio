from pathlib import Path
import json,hashlib,subprocess,marshal
from PyInstaller.archive.readers import CArchiveReader
REPO=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation');OUT=Path(__file__).resolve().parent;B=OUT/'readback';read=lambda p:json.loads((B/p).read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
s=read('source-export-manifest.json');proc=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for path,expected in s['files'].items():
 lookup='docs/reviews/I05/inputs-c2/AGENTS-current.txt'if path=='AGENTS.md'else path
 proc.stdin.write(f'{s["head"]}:{lookup}\n'.encode());proc.stdin.flush();header=proc.stdout.readline().decode().split();assert len(header)==3,header
 raw=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'and sha(raw)==expected,path
proc.stdin.close();assert proc.wait()==0;assert len(s['files'])==1238 and len(s['executionInputs'])==205
for p,h in s['executionInputs'].items():assert sha((REPO/p).read_bytes())==h,p
receiptResults={}
for folder,rowkey,exkey in [('internal-review','included','excludedDeterministicTransports'),('independent-stdio-driver','included','excluded'),('independent-regressions','files','excluded')]:
 r=read(folder+'/copy-receipt.json');inc=r[rowkey];exc=r[exkey]
 for row in inc:
  raw=(B/folder/row['path']).read_bytes();assert len(raw)==row['bytes']and sha(raw)==row['sha256']
 for row in exc:
  original=Path(r['originalDirectory'])/row['path'];assert original.stat().st_size==row['bytes']and sha(original.read_bytes())==row['sha256']
  if'recoveryCommand'in row:
   raw=subprocess.check_output(row['recoveryCommand'],cwd=REPO);assert raw==original.read_bytes()
 receiptResults[folder]={'included':len(inc),'excluded':len(exc),'allBytesVerified':True,'exactTarRebuilt':sum('recoveryCommand'in x for x in exc)}
 if'originalMemberCount'in r:assert len(inc)+len(exc)==r['originalMemberCount']
 if folder=='internal-review':assert{row['path']for row in inc+exc}=={row['path']for row in read(folder+'/artifact-manifest.json')['members']}
 if folder=='independent-stdio-driver':
  idx=read(folder+'/original-evidence-manifest.json')['files'];assert set(idx)=={row['path']for row in inc+exc}
  for row in inc+exc:assert idx[row['path']]=={'bytes':row['bytes'],'sha256':row['sha256']}
# Read actual CArchive code; neither import nor execute an extracted product module.
expect=read('bundled-code-verification.json');actual={}
for label,path in [('macos',REPO/'release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine'),('linux',REPO/'build/i05-integrated/c4/binary-inputs/linux-engine'),('linuxFirstPreserved',REPO/'build/i05-integrated/c4/binary-inputs/linux-first-stale-engine')]:
 assert sha(path.read_bytes())==expect[label]['executableSha256'];pyz=CArchiveReader(str(path)).open_embedded_archive('PYZ.pyz');modules={}
 for name,row in expect[label]['modules'].items():
  source=subprocess.check_output(['git','show','1a79731091e671c497824c94e12dae34a4e8609b:packages/engine/src/ontolearn_engine/'+name+'.py'],cwd=REPO);code=pyz.extract('ontolearn_engine.'+name);compiled=compile(source,code.co_filename,'exec',dont_inherit=True,optimize=0)
  assert code==compiled and sha(source)==row['sourceSha256']and sha(marshal.dumps(code))==row['archiveCodeMarshalSha256'],(label,name)
  modules[name]=True
 assert len(modules)==7;actual[label]={'sha256':sha(path.read_bytes()),'allSevenActualCodeObjectsEqual':True,'runtimeAcceptanceRecorded':expect[label]['runtimeAcceptance']}
assert actual['linux']['sha256']==actual['linuxFirstPreserved']['sha256']and not actual['linuxFirstPreserved']['runtimeAcceptanceRecorded']
# Original checkout protection list was preserved in the prior C3 archive.
protected=json.loads((Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-lexical-regressions/build/c3-seal-independent-audit/readback/execution-and-protection-post.json')).read_bytes())['originalProtected']
for row in protected:assert sha((Path('/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio')/row['path']).read_bytes())==row['actual']==row['expected']
result={'fixedSourceHead':s['head'],'restoredSourceMembers':len(s['files']),'currentExecutionInputsVerified':205,'originalProtectedVerified':len(protected),'receipts':receiptResults,'actualBundledCodeReadback':actual}
(OUT/'02-source-code.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
