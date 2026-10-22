import datetime,hashlib,json,os,pathlib,subprocess,time
root=pathlib.Path.cwd();process=root/'docs/reviews/T03/standalone-profile-implementation-20261023';out=process/'unit-run-e37-first'
freeze=json.loads((process/'delta-f1-n1/delta-freeze.json').read_bytes())
expected='e37cc2b161b53a6250a4085104ee955c423fb149'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()==expected

def vector():
    rows=[]
    for row in freeze['products']:
        raw=(root/row['path']).read_bytes();observed=dict(path=row['path'],bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        assert observed==row,row['path']
        assert raw==subprocess.check_output(['git','show',expected+':'+row['path']],cwd=root)
        rows.append(observed)
    return rows
before=vector();(out/'source-before.json').write_text(json.dumps(before,indent=2)+'\n')
argv=['/Users/kyle/.local/bin/uv','run','--frozen','pytest','packages/engine/tests/test_semantic_build_provenance.py','-q','--maxfail=1']
env={'PATH':str(root/'.venv/bin')+':/Users/kyle/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin','HOME':'/Users/kyle','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','LC_CTYPE':'C.UTF-8','VIRTUAL_ENV':str(root/'.venv'),'UV_PROJECT_ENVIRONMENT':str(root/'.venv'),'UV_CACHE_DIR':str(root/'build/t03-profile-unit-20261023/cache/uv'),'TMPDIR':str(root/'build/t03-profile-unit-20261023/tmp'),'UV_NO_SYNC':'1','UV_OFFLINE':'1','UV_PYTHON_DOWNLOADS':'never','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
stdout_path=out/'stdout.log';stderr_path=out/'stderr.log';receipt_path=out/'receipt.json'
start=datetime.datetime.now(datetime.timezone.utc).isoformat();monotonic=time.monotonic();child=None;status=None;timeout=False;error=None;ioerror=None
try:
    with stdout_path.open('xb') as stdout,stderr_path.open('xb') as stderr:
        try:
            child=subprocess.Popen(argv,cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,shell=False)
            try: status=child.wait(timeout=600)
            except subprocess.TimeoutExpired:
                timeout=True
                child.terminate()
                try: status=child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill();status=child.wait(timeout=5)
        except Exception as caught:
            error=dict(type=type(caught).__name__,errno=getattr(caught,'errno',None),message=str(caught))
except OSError as caught: ioerror=dict(type=type(caught).__name__,errno=caught.errno,message=str(caught))
end=datetime.datetime.now(datetime.timezone.utc).isoformat();elapsed=time.monotonic()-monotonic
streams={};ranges={}
for channel,path in [('stdout',stdout_path),('stderr',stderr_path)]:
    try:
        size=0;digest=hashlib.sha256()
        with path.open('rb') as raw:
            first=os.fstat(raw.fileno())
            while True:
                chunk=raw.read(65536)
                if not chunk:break
                size+=len(chunk);digest.update(chunk)
            last=os.fstat(raw.fileno())
        assert first.st_ino==last.st_ino and first.st_size==last.st_size==size and first.st_mtime_ns==last.st_mtime_ns
        streams[channel]=dict(path=str(path),bytes=size,sha256=digest.hexdigest());ranges[channel]=[0,size]
    except Exception as caught:
        ioerror=ioerror or dict(type=type(caught).__name__,errno=getattr(caught,'errno',None),message=str(caught));streams[channel]=None;ranges[channel]=None
try: after=vector();source_equal=after==before
except Exception as caught:
    after=None;source_equal=False;error=error or dict(type=type(caught).__name__,message=str(caught))
(out/'source-after.json').write_text(json.dumps(after,indent=2)+'\n')
receipt=dict(format='t03-approved-single-file-unit/1',sourceCommit=expected,gate='explicit controller SINGLE-FILE UNIT START after e37 independent actual delta 0 new blocking P1/P2',argv=argv,cwd=str(root),environment=env,pid=child.pid if child else None,startUtc=start,endUtc=end,wallSeconds=elapsed,wallLimitSeconds=600,status=status,signal=(-status if status is not None and status<0 else None),timeout=timeout,error=error,ioError=ioerror,overflow=False,stdoutPath=str(stdout_path),stderrPath=str(stderr_path),receiptPath=str(receipt_path),streams=streams,captureRange=ranges,complete=(status is not None and not timeout and error is None and ioerror is None),sourceBefore=before,sourceAfter=after,sourceUnchanged=source_equal,firstFailure=(status!=0 or timeout or error is not None or ioerror is not None or not source_equal),afterRun='STOP: no product edit, no rerun, no process final commit; wait controller intake')
with receipt_path.open('x') as stream:stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
