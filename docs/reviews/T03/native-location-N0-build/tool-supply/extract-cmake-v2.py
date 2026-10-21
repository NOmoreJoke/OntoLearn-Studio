from pathlib import Path
from datetime import datetime,timezone
import os,stat,tarfile,posixpath,hashlib,json
R=Path(__file__).parent;C=json.loads((R/'run-config.json').read_text());S=Path(C['source_run'])
readbytes=178939105
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(p):
 global readbytes
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);readbytes+=len(b)
 return h.hexdigest()
sourceindex=S/'source-index.json';assert sourceindex.stat().st_size==28386 and digest(sourceindex)=='e6eea559a28087bebcd965f3632e2be7c8f0a58f3e593f25c5415b067c86e2e6'
archive=S/'cmake-4.4.4-macos-universal.tar.gz';assert archive.stat().st_size==89454352 and digest(archive)=='4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305'
raw=(S/'cmake-4.4.4-SHA-256.txt').read_bytes();readbytes+=len(raw)
match=[x for x in raw.decode().splitlines() if x.split()[-1].lstrip('*')==archive.name]
assert len(match)==1 and match[0].split()[0]=='4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305'
with tarfile.open(archive,'r:gz') as tf:
 ms=tf.getmembers();readbytes+=archive.stat().st_size
 assert len(ms)==9041
 seen={};counts={};total=0
 for m in ms:
  n=posixpath.normpath(m.name)
  assert not m.name.startswith('/') and not(n=='..' or n.startswith('../')) and n not in seen and '\\' not in n
  kind='regular' if m.isfile() else 'directory' if m.isdir() else 'symlink' if m.issym() else 'REJECT'
  assert kind!='REJECT';seen[n]=m;counts[kind]=counts.get(kind,0)+1;total+=m.size
 assert counts=={'directory':189,'regular':8839,'symlink':13} and total==252707197
 root=ms[0].name.split('/')[0];assert root=='cmake-4.4.4-macos-universal'
 def resolve(p):
  visited=set()
  for hop in range(64):
   assert p not in visited;visited.add(p);parts=p.split('/');changed=False
   for k in range(1,len(parts)+1):
    prefix='/'.join(parts[:k]);m=seen.get(prefix)
    if m and m.issym():
     assert not m.linkname.startswith('/') and '\\' not in m.linkname
     p=posixpath.normpath(posixpath.join(posixpath.dirname(prefix),m.linkname,*parts[k:]));assert p==root or p.startswith(root+'/');changed=True;break
   if not changed:assert p in seen;return p
  raise ValueError('link bound')
 for m in ms:
  if m.issym():resolve(m.name)
 dest=R/'cmake-distribution-v2';dest.mkdir(mode=0o700)
 (dest/root).mkdir(mode=0o700) # archive omits this implicit container, retain as separately declared supply container
 def target(m):
  p=dest/m.name
  assert str(p).startswith(str(dest)+'/')
  for parent in p.parents:
   if parent==dest:break
   assert parent.is_dir() and not parent.is_symlink(),str(parent)
  assert not os.path.lexists(p),str(p)
  return p
 for m in sorted((x for x in ms if x.isdir()),key=lambda x:x.name.count('/')):target(m).mkdir(mode=0o700)
 sourcehash={}
 for m in ms:
  if not m.isfile():continue
  p=target(m);h=hashlib.sha256();size=0
  with tf.extractfile(m) as src,p.open('xb') as out:
   for b in iter(lambda:src.read(1024*1024),b''):out.write(b);h.update(b);size+=len(b);readbytes+=len(b)
  assert size==m.size;os.chmod(p,m.mode);sourcehash[m.name]=h.hexdigest()
 for m in ms:
  if not m.issym():continue
  p=target(m);os.symlink(m.linkname,p)
  if hasattr(os,'lchmod'):os.lchmod(p,m.mode)
 for m in sorted((x for x in ms if x.isdir()),key=lambda x:-x.name.count('/')):os.chmod(dest/m.name,m.mode)
 inventory=[];zeros=[]
 for m in ms:
  p=dest/m.name;s=p.lstat();kind='regular' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'REJECT'
  expected='regular' if m.isfile() else 'directory' if m.isdir() else 'symlink'
  assert kind==expected and stat.S_IMODE(s.st_mode)==m.mode,(m.name,kind,oct(stat.S_IMODE(s.st_mode)),oct(m.mode))
  row={'archive_path':m.name,'actual_path':str(p),'type':kind,'archive_mode':oct(m.mode),'actual_mode':oct(stat.S_IMODE(s.st_mode)),'realpath':str(p.resolve()),'archive_bytes':m.size}
  assert p.resolve().is_relative_to(dest.resolve())
  if m.isfile():
   got=digest(p);assert s.st_size==m.size and got==sourcehash[m.name]
   row.update(bytes=s.st_size,archive_sha256=sourcehash[m.name],actual_sha256=got)
   if s.st_size==0:zeros.append(m.name)
  elif m.issym():assert os.readlink(p)==m.linkname;row.update(linkname=os.readlink(p),final_archive_target=resolve(m.name))
  inventory.append(row)
 # compare actual tree as well: no omission or extra unlisted object
 actual=[]
 for dp,dirs,files in os.walk(dest,followlinks=False):
  for n in dirs+files:actual.append(str((Path(dp)/n).relative_to(dest)))
 assert set(actual)==set(seen)|{root} and len(actual)==9042
 cmake=dest/root/'CMake.app/Contents/bin/cmake';ctest=dest/root/'CMake.app/Contents/bin/ctest'
 assert cmake.stat().st_size==26639440 and sourcehash[str(cmake.relative_to(dest))]=='80cbc0d5ee08c9e6166bcc44bf51faf5469e360346f5cefbf36e8f8e4351a4cb'
 assert ctest.stat().st_size==29114000 and sourcehash[str(ctest.relative_to(dest))]=='3c91499c53345b601504d30f84662dbaa043ecaee8915c66a769c95b7d6fcd88'
 (R/'cmake-extracted-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 report={'finished_utc':datetime.now(timezone.utc).isoformat(),'archive_sha256':'4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305','source_index_sha256':'e6eea559a28087bebcd965f3632e2be7c8f0a58f3e593f25c5415b067c86e2e6','official_checksum_unique_matches':1,'member_count':len(ms),'type_counts':counts,'declared_file_bytes':total,'zero_byte_regular_files':zeros,'actual_extra_or_missing_archive_members':[],'implicit_container':{'path':str(dest/root),'mode':oct(stat.S_IMODE((dest/root).lstat().st_mode)),'reason':'Required parent omitted by official tar member list'},'actual_objects_including_implicit_container':9042,'all_archive_vs_actual_path_type_mode_link_realpath_bytes_sha_match':True,'extractall_used':False,'destination':str(dest),'cmake_path':str(cmake),'ctest_path':str(ctest),'conservative_read_bytes':readbytes,'status':'PASS'}
 (R/'cmake-extraction-report.json').write_text(json.dumps(report,indent=2)+'\n')
 (R/'read-budget.json').write_text(json.dumps({'read_bytes':readbytes,'inventory_items':9042,'limit_read_bytes':8*1024**3,'limit_inventory_items':200000},indent=2)+'\n')
 print(json.dumps(report,indent=2))
