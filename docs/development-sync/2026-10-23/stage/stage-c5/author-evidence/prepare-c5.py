# coding: utf-8
"""C5 preparation only: declared source copies, pins and ordinary new trees. No tool/product execution."""
from pathlib import Path
import hashlib,json,os,stat,datetime
if not __debug__:raise RuntimeError('OPTIMIZED_STARTUP_FORBIDDEN')
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'20261023_stage_review_c4'
PINS={'zcode':'b54b88f746ff65214d6a6c48f2d08402399c5ef8f3ff25a1b320af3f5c124899','minimax':'3aa98771d5d0eb31bfee4c8d5dea4125f666ff0003ac79cd66e383264c246dec'}
PROPOSAL=OLD/'author-evidence/behavior-selector-proposal-20261023'
AFTER='7ff9d140035aa026a92231f9c9d5e9c860ab82abf7b1a8b5c9617573cb856be1'
def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):
 for q in [*reversed(p.parents),p]:assert not q.is_symlink()
 a=p.stat();assert stat.S_ISREG(a.st_mode) and a.st_nlink==1
 b=p.read_bytes();z=p.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return b,stat.S_IMODE(a.st_mode)
def put(p,b,mode=0o644):
 assert ROOT in p.parents
 p.parent.mkdir(parents=True,exist_ok=True)
 for q in [*reversed(p.parents),p]:assert not q.is_symlink()
 with p.open('xb') as f:f.write(b)
 p.chmod(mode)
def jb(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
def ident(p):
 b,m=read(p);s=p.stat();return {'bytes':len(b),'sha256':digest(b),'mode':oct(m),'dev':s.st_dev,'ino':s.st_ino}
def row(p,base):return {'path':str(p.relative_to(base)),**{k:v for k,v in ident(p).items() if k in ['bytes','sha256','mode']}}
proof=read(PROPOSAL/'handoff.json')[0];assert len(proof)==3965 and digest(proof)=='df204adac64a9c34f8b1553d842e37011b2c52e8300768536d70b5da75564e20'
pr=json.loads(proof);assert len(pr['files'])==10
failure=OLD/'full-review-execution-evidence/approved-browserverify-failure-artifacts'
fb=read(failure/'handoff.json')[0];assert len(fb)==3311 and digest(fb)=='2996a90c240a8f195e61204df624f3d56eaef4e3bb3da3c9d4cb1fd4efa802c1'
frows={Path(r['path']).name:r for r in json.loads(fb)['files']}
extras={}
for r in pr['files']:
 p=Path(r['path']);assert p.parent==PROPOSAL
 b,m=read(p);assert len(b)==r['bytes'] and digest(b)==r['sha256']
 extras['history-c4/accepted-unapplied-proposal/'+p.name]=(b,m,str(p))
for n in ['browser-result.json','launcher-report.json']:
 b,m=read(failure/n);r=frows[n];assert len(b)==r['bytes'] and digest(b)==r['sha256']
 extras['history-c4/approved-browser-failure/'+n]=(b,m,str(failure/n))
facts="""# C4 historical failure and C5 disposition

Both C4 complete tasks were created; neither closes designated review. Z original turn failed, no helpers; cause UNKNOWN in this owner's permitted native fields. M original browserBuild child exit0, browserVerify child exit1/ACTIVE_CHILD_NONZERO, four behavior mandatory missing. M then continued nativeCLI and extra shells, violating firstFailure/command bounds; official Stop once, formal original aborted. No final four report files were produced.

Only approved browserVerify raw browser-result and launcher-report are copied here, with the accepted unapplied runner/flow proposals and independent static reports. No non-helper shell return bodies or current task/peer opinions are inputs. C4 originals remain unchanged. Proposal static PASS is not designated model PASS. Current C5 runner applies exactly the accepted local helper plus five strict-selector replacements, retaining all assertions and coverage.

New C5 full reviews must independently read original full scope and all history to EOF, then perform all eight groups/21 actions and required gates under new own grants. Four C4 behavior mandatory records remain unverified until actual new successful evidence. Single official Bash chain must quote three newly signed helper argv with &&; first nonzero stops later calls. No retry, extra shell, standalone fourth checker, or directory discovery; precise own failure artifacts only through official Read. Current peer isolation remains.

The original 185 payload, 34 component snapshots, 58 baseline/imports and 716 mapping remain. Condition reordering has no control and stays unverified. Fixed browser HTML verification is independent of browserBuild output, so no equivalence claim. Windows/nativeGUI/signing/parent/release and unanswered policies remain open. No active grant exists in this image; controller supplies external receipt identity and later actual execution window.
""".encode()
extras['history-c4/failure-and-disposition.md']=(facts,0o644,'author-bounded-facts')
result={'status':'C5_ORDINARY_PREPARATION_ONLY','createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parties':{},'externalResourcesRescanned':False,'checkerHelperProductExecuted':False,'commandGrants':{},'actualGrants':'UNKNOWN_WAIT_CONTROLLER','sourceProposal':json.loads(proof)}
for party in ['zcode','minimax']:
 src=Path('/Volumes/OntoLearn-Stage-C4-'+party+'-20261023/input');mb,mm=read(src/'input-manifest.json');assert digest(mb)==PINS[party]
 old=json.loads(mb);assert len(old['files'])==766 and old['exclusions']==[]
 stage=ROOT/'prepared'/party/'volume-root/input';assert not stage.exists()
 rw=ROOT/'runtime'/party;assert not rw.exists()
 ro=Path('/Volumes/OntoLearn-Stage-C5-'+party+'-20261023/input')
 newfiles={};sources={};changes=[]
 for r in old['files']:
  rel=Path(r['path']);assert not rel.is_absolute() and '..' not in rel.parts and str(rel)==r['path'] and r['path'] not in newfiles
  b,m=read(src/rel);assert (len(b),digest(b),oct(m))==(r['bytes'],r['sha256'],r['mode'])
  newfiles[r['path']]=(b,m);sources[r['path']]=ident(src/rel)
 def change(n,b):
  before=newfiles[n][0];newfiles[n]=(b,newfiles[n][1]);changes.append({'path':n,'before':{'bytes':len(before),'sha256':digest(before)},'after':{'bytes':len(b),'sha256':digest(b)}})
 runner=read(PROPOSAL/'owned-browser-runner.proposed.mjs')[0];assert len(runner)==25734 and digest(runner)==AFTER
 change('tooling/owned-browser-runner.mjs',runner)
 oldro=str(src);oldrw=old['taskRoot']
 def reb(s):return s.replace(oldro,str(ro)).replace(oldrw,str(rw))
 authority=json.loads(newfiles['config/authority.json'][0]);authority['allowedRunBase']=str(rw/'runs');authority['protectedRoots']=[reb(x) for x in authority['protectedRoots']]
 change('config/authority.json',jb(authority));ash=digest(newfiles['config/authority.json'][0])
 cfg=json.loads(reb(newfiles['config/runtime-config.json'][0].decode()))
 for a in cfg['commands'].values():a[a.index('--authority-sha256')+1]=ash
 v=cfg['commands']['browserVerify'];v[v.index('--runner-sha256')+1]=AFTER
 change('config/runtime-config.json',jb(cfg))
 for n in ['AGENTS.md','prompt.md','review-scope.md']:
  text=reb(newfiles[n][0].decode()).replace('# C4 ','# C5 ').replace('not C4 commands','not C5 commands')
  if n=='prompt.md':
   text=text.replace('First verify readonly input, external image/source pins, exact complete input set and cwd rule mirrors using the pinned checker.','Each authorized helper retains its full readonly/input/resource preGate and postGate; no standalone fourth checker command is authorized. Complete required Read/EOF first; execute only when controller supplies new own active grants and exact sole Bash chain.')
  text+='\nC5 continuation: read history-c4/failure-and-disposition.md and all history-c4 accepted proposals/raw failure artifacts as common historical inputs. No C4 old task or static PASS closes C5. After complete EOF reads, only one official Bash call containing the newly signed browserBuild && browserVerify && nativeCLI helper argv is eligible when separately granted. First nonzero stops successors. No extra shell/ls/python discovery or retry; use official Read on explicit own result paths. Grant identity and START remain external and UNKNOWN until controller issuance.\n'
  change(n,text.encode())
 candidate=json.loads(newfiles['candidate.json'][0]);candidate['label']='stage-acceptance-20261023-review-c5';candidate['predecessorC4ManifestSHA256']=PINS[party];candidate['runnerOnlyBehaviorDeltaSHA256']=AFTER;candidate['C4HistoricalFullPairPassed']=False;candidate['actualGrants']='UNKNOWN_EXTERNAL_CONTROLLER_ONLY'
 change('candidate.json',jb(candidate))
 for n,(b,m,source) in extras.items():assert n not in newfiles;newfiles[n]=(b,m)
 for n,(b,m) in sorted(newfiles.items()):put(stage/n,b,m)
 for n in ['environment/tmp','environment/cache','environment/config','runs','reports','owner-evidence']:(rw/n).mkdir(parents=True,exist_ok=False)
 for n in ['AGENTS.md','prompt.md','review-scope.md']:put(rw/n,newfiles[n][0])
 manifest={**old,'inputRoot':str(ro),'taskRoot':str(rw),'files':[row(stage/n,stage) for n in sorted(newfiles)],'directories':sorted(str(p.relative_to(stage)) for p in stage.rglob('*') if p.is_dir())}
 put(stage/'input-manifest.json',jb(manifest))
 comparisons=[]
 for n in sorted(sources):
  before=sources[n];after=ident(stage/n);assert (before['dev'],before['ino'])!=(after['dev'],after['ino'])
  if n not in {c['path'] for c in changes}:assert all(before[k]==after[k] for k in ['bytes','sha256','mode'])
  comparisons.append({'path':n,'source':before,'new':after,'changed':n in {c['path'] for c in changes}})
 result['parties'][party]={'sourceManifestSHA256':PINS[party],'inputRoot':str(ro),'taskRoot':str(rw),'preparedInputRoot':str(stage),'volumeRoot':str(ro.parent),'imagePath':str(ROOT/'images'/('stage-c5-'+party+'.dmg')),'manifestIdentity':ident(stage/'input-manifest.json'),'fixedFilesIncludingManifest':len(newfiles)+1,'directories':len(manifest['directories']),'changedPaths':changes,'newHistoricalPaths':sorted(extras),'copiedOriginalRows':comparisons,'resourceManifestUnchanged':True,'nativeManifestUnchanged':True,'commandGrants':{},'actualGrants':'UNKNOWN_WAIT_CONTROLLER'}
# Cross-party fixed payload/history and physical independence.
z=ROOT/'prepared/zcode/volume-root/input';m=ROOT/'prepared/minimax/volume-root/input'
zn={str(p.relative_to(z)) for p in z.rglob('*') if p.is_file()};mn={str(p.relative_to(m)) for p in m.rglob('*') if p.is_file()};assert zn==mn
for n in zn:
 a=ident(z/n);b=ident(m/n);assert (a['dev'],a['ino'])!=(b['dev'],b['ino'])
 if n.startswith(('c3-input/subject/','c3-input/common-history/','history-c3/','history-c4/')):assert all(a[k]==b[k] for k in ['bytes','sha256','mode'])
put(ROOT/'author-evidence/preparation-result.json',jb(result))
print(json.dumps({'status':result['status'],'parties':{k:{x:v[x] for x in ['manifestIdentity','fixedFilesIncludingManifest','directories']} for k,v in result['parties'].items()}},ensure_ascii=False))
