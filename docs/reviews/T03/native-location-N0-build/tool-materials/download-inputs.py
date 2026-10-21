from pathlib import Path
from datetime import datetime,timezone
import urllib.request,urllib.error,urllib.parse,hashlib,json,time
RUN=Path(__file__).parent
results=[]
def now(): return datetime.now(timezone.utc).isoformat()
class Redirects(urllib.request.HTTPRedirectHandler):
 def __init__(self,chain): self.chain=chain
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  host=urllib.parse.urlsplit(newurl).hostname
  if host not in {'github.com','release-assets.githubusercontent.com','objects.githubusercontent.com','raw.githubusercontent.com','cmake.org','nodejs.org'}:
   raise ValueError('Unapproved redirect host: '+str(host))
  self.chain.append({'url':req.full_url,'status':code,'location':newurl})
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def download(label,url,filename,limit):
 rec={'label':label,'source_url':url,'started_utc':now(),'limit_bytes':limit,'redirect_chain':[]}
 part=RUN/(filename+'.partial'); final=RUN/filename
 try:
  opener=urllib.request.build_opener(Redirects(rec['redirect_chain']))
  req=urllib.request.Request(url,headers={'User-Agent':'T03-N0-official-static-material-audit/1.0','Accept-Encoding':'identity'})
  with opener.open(req,timeout=45) as response:
   rec.update(final_url=response.url,http_terminal_status=response.status,headers=dict(response.headers.items()))
   cl=response.headers.get('Content-Length')
   if cl and int(cl)>limit: raise ValueError('Content-Length exceeds authorized limit')
   size=0; sha=hashlib.sha256(); start=time.monotonic()
   with part.open('xb') as out:
    while True:
     chunk=response.read(min(1024*1024,limit-size+1))
     if not chunk: break
     size+=len(chunk)
     if size>limit: raise ValueError('stream exceeded authorized limit')
     out.write(chunk); sha.update(chunk)
     if time.monotonic()-start>180: raise TimeoutError('bounded transfer elapsed over 180 seconds')
   if cl and size!=int(cl): raise ValueError('Content-Length mismatch')
   part.rename(final)
   rec.update(outcome='downloaded',path=str(final),bytes=size,sha256=sha.hexdigest())
 except Exception as exc:
  rec.update(outcome='failed',exception_type=type(exc).__name__,error=str(exc))
  if isinstance(exc,urllib.error.HTTPError):
   rec.update(http_terminal_status=exc.code,final_url=exc.url,headers=dict(exc.headers.items()))
   body=exc.read(65536)
   errorfile=RUN/(filename+'.http-error-body')
   errorfile.write_bytes(body)
   rec.update(error_body_path=str(errorfile),error_body_bytes=len(body),error_body_sha256=hashlib.sha256(body).hexdigest())
  if part.exists(): rec.update(partial_path=str(part),partial_bytes=part.stat().st_size,partial_sha256=hashlib.sha256(part.read_bytes()).hexdigest())
 rec['finished_utc']=now(); results.append(rec)
 (RUN/'download-metadata.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps({k:rec[k] for k in ['label','outcome','bytes','sha256','http_terminal_status','error'] if k in rec}),flush=True)
 return rec
cmake_archive='cmake-4.4.4-macos-universal.tar.gz'
for name in ['cmake-4.4.4-SHA-256.txt',cmake_archive]:
 download('cmake-'+('checksum' if name.endswith('.txt') else 'archive'),'https://github.com/Kitware/CMake/releases/download/v4.4.4/'+name,name,2*1024*1024 if name.endswith('.txt') else 250*1024*1024)
for name in ['LICENSE','node_api.h','node_api_types.h','js_native_api.h','js_native_api_types.h']:
 url='https://raw.githubusercontent.com/nodejs/node/v24.15.0/'+('LICENSE' if name=='LICENSE' else 'src/'+name)
 download('node-v24.15.0-'+name,url,'node-v24.15.0-'+name,2*1024*1024 if name=='LICENSE' else 1024*1024)
