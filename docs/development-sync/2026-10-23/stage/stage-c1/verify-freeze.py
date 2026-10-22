"""Read-only verification of this immutable review subject and optional existing native outputs."""
from pathlib import Path
import argparse,hashlib,json,stat
ROOT=Path(__file__).resolve().parent
h=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--external',action='store_true');args=p.parse_args()
c=json.loads((ROOT/'candidate.json').read_text());raw=(ROOT/'payload-manifest.json').read_bytes();assert h(raw)==c['payloadManifestSHA256'],'payload manifest identity mismatch'
m=json.loads(raw);expected={row['path'] for row in m['files']};actual={str(p.relative_to(ROOT)) for p in (ROOT/'payload').rglob('*') if p.is_file()};assert actual==expected,{'unexpected':list(actual-expected),'missing':list(expected-actual)}
for row in m['files']:
 b=(ROOT/row['path']).read_bytes();assert len(b)==row['bytes'] and h(b)==row['sha256'],row['path']
package_manifest=ROOT/'package-manifest.json'
if package_manifest.exists():
 package_rows=json.loads(package_manifest.read_text())['files']
 package_expected={row['path'] for row in package_rows}
 package_actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and p.name!='package-manifest.json' and p.relative_to(ROOT).parts[0]!='reports'}
 assert package_actual==package_expected,'package static file set mismatch'
 for row in json.loads(package_manifest.read_text())['files']:
  b=(ROOT/row['path']).read_bytes();assert len(b)==row['bytes'] and h(b)==row['sha256'],'package metadata mismatch: '+row['path']
e=json.loads((ROOT/'payload/external-artifacts.json').read_text());external_result='not requested'
if args.external:
 native=e['native'];z=Path(native['zipPath']);assert z.stat().st_size==native['zipBytes'] and h(z.read_bytes())==native['zipSHA256'],'native ZIP mismatch'
 a=Path(native['appPath']);rows=json.loads((ROOT/'payload/artifacts/desktop/app-files.json').read_text())['entries'];count=links=0
 expected_entries={row['path'] for row in rows};actual_entries={str(p.relative_to(a)) for p in a.rglob('*') if p.is_file() or p.is_symlink()}
 assert actual_entries==expected_entries,'native app file set mismatch'
 for row in rows:
  q=a/row['path'];s=q.lstat();assert oct(stat.S_IMODE(s.st_mode))==row['mode'],row['path']
  if row['type']=='symlink':assert q.is_symlink() and q.readlink().as_posix()==row['target'],row['path'];links+=1
  else:
   b=q.read_bytes();assert len(b)==row['bytes'] and h(b)==row['sha256'],row['path'];count+=1
 assert count==native['appFileEntries'] and links==native['appSymlinkEntries'];external_result={'files':count,'symlinks':links,'zip':native['zipSHA256']}
print(json.dumps({'candidate':c['label'],'payloadManifestSHA256':c['payloadManifestSHA256'],'files':len(m['files']),'external':external_result,'writes':False},ensure_ascii=False,indent=2))
