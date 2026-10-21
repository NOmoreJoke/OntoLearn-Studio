from pathlib import Path
import hashlib,json,tarfile,io,zipfile
REPO=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation')
OUT=Path(__file__).resolve().parent
BASE=REPO/'docs/reviews/I05/evidence/integrated-c4'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
m=json.loads((BASE/'manifest.json').read_bytes());a=BASE/m['archive'];assert sha(a.read_bytes())==m['archiveSha256']=='eae749d05ac61b9cc726626f008507b3484d1ba8b1980f9f7a33eb0f51871acc' and a.stat().st_size==m['archiveBytes']
rows=[];nested=[]
with tarfile.open(a)as tf:
 members=tf.getmembers();assert len(members)==1254==m['memberCount'];assert len({x.name for x in members})==len(members)
 index={x['member']:x for x in m['members']};assert set(index)=={x.name for x in members}
 for x in members:
  assert x.isfile()and not Path(x.name).is_absolute()and '..'not in Path(x.name).parts
  raw=tf.extractfile(x).read();r=index[x.name];assert len(raw)==r['bytes']and sha(raw)==r['sha256'],x.name
  original=REPO/r['originalPath'];assert original.read_bytes()==raw,original
  lower=x.name.lower();assert not any(lower.endswith(suffix)for suffix in ['.sqlite','.db','.sqlite-wal','.sqlite-shm','.db-wal','.db-shm','.writer-lock','.pyc']),x.name
  assert not raw.startswith(b'SQLite format 3\0'),x.name
  assert not any(part in ['.venv','node_modules','__pycache__']for part in Path(x.name).parts),x.name
  assert not(raw[:4]in[b'\x7fELF',b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf']or raw.startswith(b'MZ')),x.name
  if lower.endswith(('.tar','.tar.gz','.tgz','.zip')):
   if lower.endswith('.zip'):
    with zipfile.ZipFile(io.BytesIO(raw))as z:
     children=[(n,z.read(n))for n in z.namelist()if not n.endswith('/')]
   else:
    with tarfile.open(fileobj=io.BytesIO(raw))as z:
     children=[(s.name,z.extractfile(s).read())for s in z.getmembers()if s.isfile()]
   assert all(not b.startswith(b'SQLite format 3\0')and not n.lower().endswith(('.sqlite','.db','.writer-lock'))for n,b in children),x.name
   nested.append({'member':x.name,'children':len(children)})
  target=OUT/'readback'/x.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  rows.append({'member':x.name,'bytes':len(raw),'sha256':sha(raw),'originalEqual':True})
assert sum(r['bytes']for r in rows)==62425493==m['uncompressedBytes']
original=REPO/'build/i05-integrated/c4';paths={str(p.relative_to(REPO))for p in original.rglob('*')if p.is_file()};inc={r['originalPath']for r in m['members']if r['originalPath'].startswith('build/i05-integrated/c4/')};exc={r['originalPath']for r in m['excluded']};assert not inc&exc
assert paths==inc|exc,(len(paths),len(inc),len(exc),paths-(inc|exc),(inc|exc)-paths)
for r in m['excluded']:
 p=REPO/r['originalPath'];assert p.stat().st_size==r['bytes']and sha(p.read_bytes())==r['sha256']
result={'archiveBytes':a.stat().st_size,'archiveSha256':m['archiveSha256'],'members':len(rows),'originalBytes':sum(r['bytes']for r in rows),'originalDirectoryFiles':len(paths),'includedOriginals':len(inc),'excluded':len(exc),'processFilesOutsideOriginalDirectory':len(rows)-len(inc),'nestedArchiveInspections':nested,'allSourcePathsAccounted':True,'memberResults':rows}
(OUT/'01-readback.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='memberResults'},indent=2))
print('CATEGORY COUNTS')
from collections import Counter
print(Counter(r['member'].split('/')[0]for r in rows))
