#!/usr/bin/env python3
"""Meaningful synthetic CLI/path/process tests only. Never executes the real packaged engine."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT/'desktop/probe-packaged-engine.py'
BUILD = ROOT/'desktop/reproduce-build.sh'
AUTH = ROOT/'authority.json'
AUTH_SHA = '5c68a8d00257149d9846ec4fb0dcba7fa13ea7922a8ab04c361b812f0efdc210'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sizes(base):
    total = 0
    pending = [base]
    while pending:
        p = pending.pop()
        try:
            st = p.lstat()
            if stat.S_ISDIR(st.st_mode):
                pending.extend(p.iterdir())
            else:
                total += st.st_size
        except FileNotFoundError:
            continue
    return total


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


STUB = r'''#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path
SCENARIO = '__SCENARIO__'
phase='storage' if '--storage-probe' in sys.argv else 'handshake'
if SCENARIO=='hang': time.sleep(5)
if SCENARIO=='flood': sys.stderr.write('x'*16384);sys.stderr.flush();time.sleep(1)
if SCENARIO=='nonzero': sys.exit(7)
capture={'cwd':os.getcwd(),'db':os.environ.get('ONTOLEARN_DB_PATH'),'tmp':os.environ.get('TMPDIR'),'envKeys':sorted(os.environ),'argv':sys.argv[1:]}
(Path.cwd()/('stub-'+phase+'.json')).write_text(json.dumps(capture))
if phase=='storage':
 print(json.dumps({'scale':1,'triples':18,'result':['urn:case:0:alarm/A01'],'expected':['urn:case:0:alarm/A01']}));sys.exit(0)
for line in sys.stdin:
 r=json.loads(line);s='synthetic-stub-session'
 v={'id':r['id'],'ok':True,'engineSessionId':s,'result':{'status':'ok'}}
 if SCENARIO=='bad-id': v['id']='wrong'
 if SCENARIO=='truncated': sys.stdout.write(json.dumps(v));sys.stdout.flush();sys.exit(0)
 print(json.dumps(v),flush=True)
'''


def main():
    check(sha(AUTH) == AUTH_SHA, 'AUTHORITY_CHANGED')
    authority = json.loads(AUTH.read_text())
    base = Path(authority['allowedRunBase'])
    fixture = base/('native-fixtures-'+uuid.uuid4().hex)
    fixture.mkdir(mode=0o700)
    evidence = ROOT/'evidence'/('native-boundary-tests-'+uuid.uuid4().hex+'.json')
    records = []
    tool_hashes = {str(p): sha(p) for p in [PROBE, BUILD, Path(__file__).resolve()]}
    peak = sizes(base)
    start = time.monotonic()
    sources = {}
    def resource(scenario='ok', approved=True, readonly=True):
        root = fixture/(scenario+'-'+uuid.uuid4().hex)
        root.mkdir()
        engine = root/'engine-stub'
        engine.write_text(STUB.replace('__SCENARIO__', scenario))
        engine.chmod(0o755)
        manifest = fixture/('resources-'+uuid.uuid4().hex+'.json')
        body={'schemaVersion':1,'kind':'synthetic-stub','ownerApproved':approved,'readonlyExecutionApproved':readonly,
              'resourceRoot':str(root),'engineRelativePath':engine.name,'entries':[{'path':engine.name,'type':'file','bytes':engine.stat().st_size,'sha256':sha(engine),'mode':'0o755'}]}
        manifest.write_text(json.dumps(body))
        sources[str(engine)] = sha(engine)
        sources[str(manifest)] = sha(manifest)
        return engine, manifest
    def args_for(engine, manifest, mode='copy-declared-engine-resources', authority_path=AUTH):
        work=base/('native-case-'+uuid.uuid4().hex)
        return [sys.executable,str(PROBE),'--authority',str(authority_path),'--authority-sha256',sha(authority_path),
                '--work-root',str(work),'--output-root',str(work/'out'),'--engine-mode',mode,
                '--engine-input',str(engine),'--engine-resource-manifest',str(manifest),'--engine-resource-manifest-sha256',sha(manifest)],work
    def invoke(name, argv, work, expected, marker=None):
        nonlocal peak
        before=sizes(base)
        check(before < authority['limits']['combinedScratchBytes']-1024*1024, 'GLOBAL_BUDGET_HEADROOM_REQUIRED')
        env=os.environ.copy()
        env['ONTOLEARN_DB_PATH']=str(fixture/'outside-do-not-touch.sqlite')
        env['ONTOLEARN_UNTRUSTED_SENTINEL']='synthetic'
        env['PYTHONPATH']=str(fixture/'untrusted-python-path')
        proc=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=12)
        after=sizes(base);peak=max(peak, before, after)
        stdout_path=fixture/(name+'.stdout.log');stderr_path=fixture/(name+'.stderr.log')
        stdout_path.write_bytes(proc.stdout);stderr_path.write_bytes(proc.stderr)
        record={'case':name,'argv':argv,'harnessCwd':str(Path.cwd()),'exitCode':proc.returncode,
                'stdout':str(stdout_path),'stderr':str(stderr_path),'stdoutSHA256':sha(stdout_path),'stderrSHA256':sha(stderr_path),
                'combinedBytesBefore':before,'combinedBytesAfter':after,'workCreated':work.exists(),'expected':expected,
                'toolSourceHashesAtInvocation':{str(p):sha(p) for p in [PROBE, BUILD]}}
        records.append(record)
        if expected=='success':check(proc.returncode==0,name+' expected exit0')
        else:check(proc.returncode!=0,name+' expected rejection')
        if marker:check(marker.encode() in proc.stderr,name+' missing reason '+marker)
        return proc
    try:
        engine,manifest=resource()
        for mode in ['copy-declared-engine-resources','readonly-declared-engine']:
            argv,work=args_for(engine,manifest,mode)
            invoke('healthy-'+mode,argv,work,'success')
            result=json.loads((work/'out/native-probe-result.json').read_text())
            check(result['passed'] is True and len(result['handshakeAndHealth'])==11,'protocol proof missing')
            captures=[json.loads((work/('stub-'+phase+'.json')).read_text()) for phase in ['handshake','storage']]
            for c in captures:
                check(c['cwd']==str(work),'cwd not isolated')
                check(Path(c['db']).parent==work/'db' and Path(c['tmp'])==work/'tmp','DB/tmp not isolated')
                check(not any(k.startswith('PYTHON') for k in c['envKeys']),'inherited PYTHON env')
                check([k for k in c['envKeys'] if k.startswith('ONTOLEARN_')]==['ONTOLEARN_DB_PATH'],'inherited engine env')
            check(captures[0]['db']!=captures[1]['db'],'two calls reused DB')
            if mode.startswith('copy'):
                check((work/'native-engine/engine-stub').stat().st_ino!=engine.stat().st_ino,'hardlink copy')
            invoke('existing-run-'+mode,argv,work,'reject','RUN_MUST_BE_NEW_DIRECT_CHILD')
        e,m=resource()
        info=e.stat();os.utime(e,ns=(1,info.st_mtime_ns))
        argv,work=args_for(e,m);invoke('source-atime-not-identity',argv,work,'success')
        tiny=fixture/'tiny-budget-authority.json'
        tiny.write_text(json.dumps(dict(authority,limits=dict(authority['limits'],combinedScratchBytes=1))))
        argv,work=args_for(engine,manifest,authority_path=tiny)
        invoke('combined-budget-preflight',argv,work,'reject','COMBINED_SCRATCH_BUDGET');check(not work.exists(),'budget denial created run')
        # Rejections before any run is created.
        tests=[('bad-authority-hash','--authority-sha256','0'*64,'AUTHORITY_SHA_MISMATCH'),
               ('bad-manifest-hash','--engine-resource-manifest-sha256','0'*64,'RESOURCE_MANIFEST_SHA_MISMATCH'),
               ('wrong-engine','--engine-input',str(fixture/'no-engine'),'ENGINE_INPUT_NOT_DECLARED')]
        for name,option,value,marker in tests:
            argv,work=args_for(engine,manifest);argv[argv.index(option)+1]=value
            invoke(name,argv,work,'reject',marker);check(not work.exists(),'rejection created run')
        e,m=resource(approved=False);argv,work=args_for(e,m);invoke('owner-unapproved',argv,work,'reject','OWNER_RESOURCE_APPROVAL_REQUIRED');check(not work.exists(),'unapproved run')
        e,m=resource(readonly=False);argv,work=args_for(e,m,'readonly-declared-engine');invoke('readonly-unapproved',argv,work,'reject','READONLY_EXECUTION_NOT_APPROVED')
        # Output source/ancestor aliases and link chains.
        for name,target in [('output-to-source',str(engine.parent)),('output-escape',str(fixture/'escaped'))]:
            argv,work=args_for(engine,manifest);argv[argv.index('--output-root')+1]=target
            invoke(name,argv,work,'reject','OUTPUT_MUST_BE_NEW_RUN_DESCENDANT');check(not work.exists(),'unsafe output created run')
        alias=base/('native-alias-'+uuid.uuid4().hex);alias.symlink_to(fixture,target_is_directory=True)
        argv,work=args_for(engine,manifest);argv[argv.index('--work-root')+1]=str(alias/'new');argv[argv.index('--output-root')+1]=str(alias/'new/out')
        invoke('symlink-parent',argv,alias/'new','reject','SYMLINK_WRITE_OR_ROOT_CHAIN')
        argv,work=args_for(engine,manifest);argv[argv.index('--work-root')+1]=str(base/'..'/'escape');invoke('dotdot-work',argv,work,'reject','ABSOLUTE_NORMAL_PATH_REQUIRED')
        # Source identity and link/hardlink guard, never touching a real engine.
        for scenario in ['source-hash','source-hardlink','source-link','source-extra']:
            e,m=resource()
            if scenario=='source-hash':e.write_text(e.read_text()+'\n# mutation\n')
            if scenario=='source-hardlink':os.link(e,fixture/('hardlink-'+uuid.uuid4().hex))
            if scenario=='source-link':
                target=fixture/('external-'+uuid.uuid4().hex);target.write_bytes(e.read_bytes());e.unlink();e.symlink_to(target)
            if scenario=='source-extra':(e.parent/'unexpected').write_text('synthetic')
            sources[str(e)]=sha(e)
            argv,work=args_for(e,m);invoke(scenario,argv,work,'reject');check(not work.exists(),'source rejection created run')
        # Process failures with final cleanup and separated bounded output.
        for scenario,marker in [('hang','CHILD_TIMEOUT'),('nonzero','CHILD_NONZERO_EXIT_7'),('bad-id','PROTOCOL_RESPONSE_MISMATCH'),('truncated','UNTERMINATED_PROTOCOL_FRAME')]:
            e,m=resource(scenario);argv,work=args_for(e,m);argv+=['--timeout-seconds','1' if scenario=='hang' else '5']
            invoke('process-'+scenario,argv,work,'reject',marker)
            failure=json.loads((work/'out/hello-health.failure.json').read_text())
            check(failure['ownedChildReaped'] is True and failure['exitCodeAfterCleanup'] is not None,'own child not reaped')
        capauth=fixture/'small-log-authority.json';small=dict(authority,limits=dict(authority['limits'],capturedLogBytes=1024));capauth.write_text(json.dumps(small))
        e,m=resource('flood');argv,work=args_for(e,m,authority_path=capauth);invoke('process-log-cap',argv,work,'reject','CAPTURED_LOG_LIMIT')
        check((work/'out/hello-health.stderr.log').stat().st_size<=1024,'log cap exceeded')
        # Git fixture: only local standard Git, all global/system config disabled.
        repo=fixture/'synthetic-source';repo.mkdir();(repo/'package.json').write_text('{"name":"synthetic-only","private":true}\n')
        git=Path(shutil.which('git')).resolve();genv={k:os.environ[k] for k in ['PATH','HOME'] if k in os.environ}
        genv.update({'GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_SYSTEM':os.devnull,'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_COUNT':'0','GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0'})
        def local_git(*args):return subprocess.run([str(git),'-C',str(repo),*args],env=genv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=4).stdout
        local_git('init','-q');local_git('add','package.json');local_git('-c','user.name=StageValidation','-c','user.email=stage@example.invalid','commit','-qm','synthetic only')
        commit=local_git('rev-parse','HEAD').decode().strip()
        source_manifest=fixture/'source.json';source_manifest.write_text(json.dumps({'schemaVersion':1,'gitSHA':commit,'entries':[{'path':'package.json','type':'file','bytes':(repo/'package.json').stat().st_size,'sha256':sha(repo/'package.json'),'mode':'0o644'}]}))
        sources[str(repo/'package.json')]=sha(repo/'package.json');sources[str(source_manifest)]=sha(source_manifest)
        def build_args():
            w=base/('native-build-plan-'+uuid.uuid4().hex)
            return ['/bin/sh',str(BUILD),'--authority',str(AUTH),'--authority-sha256',AUTH_SHA,'--work-root',str(w),'--output-root',str(w/'out'),
                    '--source-root',str(repo),'--expected-git-sha',commit,'--source-manifest',str(source_manifest),'--source-manifest-sha256',sha(source_manifest),'--cache-root',str(w/'cache-build'),'--git-path',str(git)],w
        argv,work=build_args();invoke('rebuild-plan-only',argv,work,'success')
        plan=json.loads((work/'out/native-rebuild-plan.json').read_text());check(plan['status']=='PLAN_ONLY' and plan['installOrNetworkStarted'] is False,'plan installed')
        argv,work=build_args();argv+=['--execute'];invoke('rebuild-execute-forbidden',argv,work,'reject','NATIVE_BUILD_EXECUTION_NOT_AUTHORIZED');check(not work.exists(),'execute denial created run')
        argv,work=build_args();argv[argv.index('--cache-root')+1]=str(fixture/'wrong-cache');invoke('rebuild-cache-escape',argv,work,'reject','CACHE_MUST_BE_NEW_OWN_DESCENDANT')
        badsource=fixture/'wrong-source.json';x=json.loads(source_manifest.read_text());x['entries'][0]['sha256']='0'*64;badsource.write_text(json.dumps(x))
        argv,work=build_args();argv[argv.index('--source-manifest')+1]=str(badsource);argv[argv.index('--source-manifest-sha256')+1]=sha(badsource);invoke('rebuild-blob-mismatch',argv,work,'reject','SOURCE_BLOB_HASH_MISMATCH')
        for path,value in sources.items():check(sha(Path(path))==value,'source mutated '+path)
        for path,value in tool_hashes.items():check(sha(Path(path))==value,'tool source changed during validation '+path)
        result={'toolSourceHashes':tool_hashes,'passed':True,'scope':'native synthetic stub/plan/path tests only; no real engine/build/GUI/network','cases':records,
                'sourceAfterHashesMatch':True,'sourceHashes':sources,'sampledCombinedPeakBytes':peak,'combinedBytesAtEnd':sizes(base),
                'elapsedSeconds':time.monotonic()-start,'perCaseAndChildBudgetSamples':True,'OSHardQuotaOrAtomicityClaimed':False}
    except Exception as e:
        result={'passed':False,'firstFailure':str(e),'cases':records,'combinedBytesAtFailure':sizes(base),'scope':'synthetic native validation only'}
    evidence.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'evidence':str(evidence),'cases':len(records),'combinedBytes':sizes(base)}))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
