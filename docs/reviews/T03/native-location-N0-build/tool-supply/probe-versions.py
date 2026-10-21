from pathlib import Path
from datetime import datetime,timezone
import os,hashlib,json,subprocess,shutil,time
R=Path(__file__).parent;A=json.loads((R/'cmake-extraction-report.json').read_text());B=json.loads((R/'read-budget.json').read_text())
assert A['status']=='PASS' and A['all_archive_vs_actual_path_type_mode_link_realpath_bytes_sha_match']
ENV={k:os.environ[k] for k in ['PATH','HOME','USER','LOGNAME','TMPDIR','LANG','LC_ALL','LC_CTYPE','DEVELOPER_DIR','SDKROOT','SYSTEM_VERSION_COMPAT'] if k in os.environ}
results=[];P=R/'probes';P.mkdir(mode=0o700)
def now():return datetime.now(timezone.utc).isoformat()
def pin(path):
 p=Path(path);real=p.resolve(strict=True);s=real.stat();h=hashlib.sha256()
 with real.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);B['read_bytes']+=len(b)
 return {'path':str(p),'realpath':str(real),'bytes':s.st_size,'sha256':h.hexdigest(),'mode':oct(s.st_mode & 0o7777)}
def run(label,args):
 rec={'label':label,'argv':args,'cwd':str(R),'environment':ENV,'timeout_seconds':30,'executable_pin_before_spawn':pin(args[0]),'started_utc':now()}
 (P/(label+'.preflight.json')).write_text(json.dumps(rec,indent=2)+'\n')
 started=time.monotonic()
 try:
  p=subprocess.Popen(args,cwd=R,env=ENV,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  try:out,err=p.communicate(timeout=30);rec['timed_out']=False
  except subprocess.TimeoutExpired:p.kill();out,err=p.communicate();rec['timed_out']=True
  rec.update(exit_code=p.returncode if p.returncode>=0 else None,signal=-p.returncode if p.returncode<0 else None,pid=p.pid)
 except Exception as exc:out=b'';err=str(exc).encode();rec.update(spawn_error=type(exc).__name__+': '+str(exc),exit_code=None,signal=None,timed_out=False)
 rec.update(finished_utc=now(),elapsed_seconds=time.monotonic()-started)
 for name,b in [('stdout',out),('stderr',err)]:
  path=P/(label+'.'+name);path.write_bytes(b);rec[name]={'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 rec['success']=rec.get('exit_code')==0 and not rec['timed_out']
 (P/(label+'.json')).write_text(json.dumps(rec,indent=2)+'\n');results.append(rec)
 (R/'probe-index.json').write_text(json.dumps(results,indent=2)+'\n');(R/'read-budget.json').write_text(json.dumps(B,indent=2)+'\n')
 print(label,rec['success'],out.decode(errors='replace').strip(),err.decode(errors='replace').strip(),flush=True)
 return rec,out
for label,args in [('cmake-version',[A['cmake_path'],'--version']),('ctest-version',[A['ctest_path'],'--version'])]:
 rec,out=run(label,args)
 if not rec['success'] or not out.decode().startswith(('cmake version 4.4.4' if label.startswith('cmake') else 'ctest version 4.4.4')):raise SystemExit('STOP: fixed CMake/CTest exact version probe failed; no retry')
commands=[('xcode-version',['/usr/bin/xcodebuild','-version']),('sdk-path',['/usr/bin/xcrun','--sdk','macosx','--show-sdk-path']),('sdk-version',['/usr/bin/xcrun','--sdk','macosx','--show-sdk-version']),('clang-path',['/usr/bin/xcrun','--find','clang']),('clangxx-path',['/usr/bin/xcrun','--find','clang++']),('make-version',['/usr/bin/make','--version']),('git-version',[shutil.which('git'),'--version'])]
outs={}
for label,args in commands:
 rec,out=run(label,args)
 if not rec['success']:raise SystemExit('STOP: authorized metadata probe failed: '+label)
 outs[label]=out.decode().strip()
for label in ['clang','clangxx']:
 path=outs[label+'-path'];assert path.startswith('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/')
 for flag,suffix in [('--version','version'),('-print-resource-dir','resource-dir')]:
  rec,out=run(label+'-'+suffix,[path,flag])
  if not rec['success']:raise SystemExit('STOP: compiler metadata probe failed')
  outs[label+'-'+suffix]=out.decode().strip()
(R/'observed-tool-metadata.json').write_text(json.dumps(outs,indent=2)+'\n')
