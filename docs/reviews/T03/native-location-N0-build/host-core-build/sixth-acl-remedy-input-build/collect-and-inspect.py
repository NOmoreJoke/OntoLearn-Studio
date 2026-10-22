from pathlib import Path
import os,json,hashlib,subprocess,time,stat
r=Path.cwd(); d=r/'docs/reviews/T03/native-location-N0-build/host-core-build/sixth-acl-remedy-input-build'; b=Path(json.loads((d/'build-input-plan.json').read_text())['exclusiveBuildDir'])
def save(n,x):
 p=d/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def pin(p,data=None):
 data=p.read_bytes() if data is None else data
 return {'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
final=json.loads((b/'supplier-log.0065.json').read_bytes());assert final['supplierCommit']=='bfe137f371361f9fda446d5cbe6b3079c5433ee5' and final['firstFailure'] is None and len(final['commands'])==13
assert all(c['run']['status']==0 and c['dispatch']['pid']>0 and c['phase']=='completed' for c in final['commands'])
external=[];rawrows=[];genrows=[]
generated={'compile_commands.json','CMakeCache.txt','CTestTestfile.cmake','CMakeFiles/CMakeConfigureLog.yaml',*[f'CMakeFiles/4.4.4/{n}' for n in ['CMakeCCompiler.cmake','CMakeCXXCompiler.cmake','CMakeSystem.cmake']],*[f'CMakeFiles/{t}.dir/{n}' for t in ['location_core_test','location_child_probe'] for n in ['flags.make','build.make','link.txt']]}
for p in sorted(b.rglob('*')):
 assert not p.is_symlink(),str(p)
 if not p.is_file():continue
 data=p.read_bytes();row=pin(p,data);external.append(row);rel=p.relative_to(b);s=rel.as_posix()
 dest=None;catalog=None
 if len(rel.parts)==1 and (p.name.startswith('supplier-log') and p.suffix=='.json' or p.suffix in ['.stdout','.stderr']):dest=d/'driver-raw'/rel;catalog=rawrows
 elif s in generated or (s.startswith('CMakeFiles/location_') and s.endswith('.o.d')):dest=d/'generated'/(s+'.raw');catalog=genrows
 if dest:
  dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as f:f.write(data)
  catalog.append({'originalPath':str(p),'archivedPath':str(dest.relative_to(r)),'bytes':row['bytes'],'sha256':row['sha256']})
assert len(rawrows)==92 and len(genrows)==17,(len(rawrows),len(genrows))
save('external-build-output-manifest.json',{'buildDir':str(b),'files':external,'totalBytes':sum(x['bytes'] for x in external),'artifactsNotStaged':True})
save('driver-raw-manifest.json',{'files':rawrows,'bytePreservingCopies':True});save('generated-evidence-manifest.json',{'files':genrows,'bytePreservingCopies':True})
artifacts=[]
for n in ['location_child_probe','location_core_test']:
 p=b/'artifacts'/n;row=next(x for x in external if x['path']==str(p));artifacts.append({**row,'realpath':str(p.resolve())})
save('artifact-pins.before.json',{'artifacts':artifacts,'notExecuted':True})
toolmeta=json.loads((r/'docs/reviews/T03/native-location-N0-build/host-core-build/gnumake-static-pin.json').read_bytes());tools={x['tool']['path']:x['tool'] for x in toolmeta['staticCommands']}
for path,expected in tools.items():assert {**pin(Path(path)),'realpath':os.path.realpath(path)}==expected,path
env={'PATH':'/usr/bin:/bin','DEVELOPER_DIR':'/Applications/Xcode.app/Contents/Developer','LANG':'C','LC_ALL':'C'}
commands=[]
for a in artifacts:
 for label,args in [('file-format',['/usr/bin/file']),('linked-libraries',['/usr/bin/otool','-L']),('load-commands',['/usr/bin/otool','-l']),('symbol-table',['/usr/bin/nm','-m']),('undefined-symbols',['/usr/bin/nm','-u'])]:
  i=len(commands);name=Path(a['path']).name;stem=f'inspection/{i:02d}-{name}-{label}';commands.append({'index':i,'target':name,'label':label,'argv':args+[a['path']],'stdout':stem+'.stdout','stderr':stem+'.stderr'})
assert len({x[k].casefold() for x in commands for k in ['stdout','stderr']})==20
save('inspection-plan.json',{'tools':list(tools.values()),'environment':env,'artifactPins':artifacts,'commands':commands,'artifactExecution':False,'perCommandTimeoutSeconds':30})
(d/'inspection').mkdir();results=[]
for c in commands:
 start=time.time()
 with (d/c['stdout']).open('xb') as out,(d/c['stderr']).open('xb') as err:
  p=subprocess.Popen(c['argv'],cwd=r,env=env,stdout=out,stderr=err)
  try:rc=p.wait(timeout=30);timeout=False
  except subprocess.TimeoutExpired:p.kill();rc=p.wait();timeout=True
 results.append({**c,'pid':p.pid,'startUnix':start,'endUnix':time.time(),'exitCode':rc,'signal':-rc if rc<0 else None,'timeout':timeout})
 save(f'inspection-results.{len(results):02d}.json',{'results':results,'artifactExecution':False})
 assert rc==0 and not timeout,c
assert [{**pin(Path(a['path'])),'realpath':str(Path(a['path']).resolve())} for a in artifacts]==artifacts
save('artifact-pins.json',{'artifacts':artifacts,'unchangedAfterInspection':True,'actualStaticCommands':10,'allActualToolCommandsExit0':True,'outputPathsUniqueCasefold':True,'notExecuted':True})
print(json.dumps({'externalFiles':len(external),'externalBytes':sum(x['bytes'] for x in external),'rawCopies':len(rawrows),'generatedCopies':len(genrows),'driverCommands':13,'staticCommands':10,'artifacts':artifacts},ensure_ascii=False))
