import datetime, hashlib, json, os, pathlib, subprocess, sys
root = pathlib.Path.cwd()
process = root / 'docs/reviews/T03/standalone-profile-implementation-20261023'
name, argv = sys.argv[1], sys.argv[2:]
env = {key: os.environ[key] for key in ('PATH','HOME','LANG','LC_ALL','LC_CTYPE') if key in os.environ}
env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', TMPDIR=str(root/'build/t03-profile-unit-20261023/tmp'), UV_NO_SYNC='1', UV_OFFLINE='1')
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (process/(name+'.stdout.log')).open('xb') as out, (process/(name+'.stderr.log')).open('xb') as err:
    child=subprocess.Popen(argv,cwd=root,env=env,stdout=out,stderr=err)
    status=child.wait()
end=datetime.datetime.now(datetime.timezone.utc).isoformat()
streams={}
for channel in ('stdout','stderr'):
    p=process/(name+'.'+channel+'.log'); raw=p.read_bytes()
    streams[channel]={'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
receipt=dict(argv=argv,cwd=str(root),environment=env,pid=child.pid,startUtc=start,endUtc=end,status=status,scope=('local product-only source freeze; no product runtime' if name.startswith('freeze-') else 'static source only'),streams=streams)
(process/(name+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
for channel in streams:
    raw=(process/(name+'.'+channel+'.log')).read_text()
    if raw: print(channel+':\n'+raw)
sys.exit(status)
