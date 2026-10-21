from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import json,tarfile,hashlib,plistlib
r=Path(__file__).parent
report=json.loads((r/'static-audit.json').read_text())
(r/'static-audit-v2-initial.json').write_text(json.dumps(report,indent=2)+'\n')
archive=r/'cmake-4.4.4-macos-universal.tar.gz'
texts=report['license_and_version_texts'];already={x['archive_member'] for x in texts}
with tarfile.open(archive,'r:gz') as tf:
 for m in tf:
  basename=PurePosixPath(m.name).name
  if not m.isfile() or basename not in {'LICENSE.rst','LICENSE','COPYING','Copyright.txt'} or m.name in already:continue
  if m.size>2*1024**2:raise ValueError('license text size exceeds text bound')
  b=tf.extractfile(m).read();b.decode('utf-8')
  dest=r/'cmake-static-texts'/(f'{len(texts):03d}-'+basename)
  dest.write_bytes(b)
  texts.append({'archive_member':m.name,'saved_path':str(dest),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
main=[x for x in texts if x['archive_member'].endswith('/Contents/doc/cmake/LICENSE.rst')]
assert len(main)==1
license_text=Path(main[0]['saved_path']).read_text()
assert 'Redistribution and use in source and binary forms' in license_text
info=plistlib.loads((r/'cmake-static-texts/000-Info.plist').read_bytes())
assert info['CFBundleShortVersionString']=='4.4.4'
report['cmake_root']['verified_CFBundleShortVersionString']=info['CFBundleShortVersionString']
report['cmake_root']['version_basis']='Official checksum verifies full 4.4.4 distribution; preserved Info.plist CFBundleShortVersionString=4.4.4; CMAKE_ROOT Modules/CMake.cmake resource present.'
report['main_cmake_license']={'member':main[0]['archive_member'],'bytes':main[0]['bytes'],'sha256':main[0]['sha256'],'kind':'CMake BSD 3-Clause license text; full exact bytes retained in tmp'}
report['license_supplement_utc']=datetime.now(timezone.utc).isoformat()
(r/'static-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'license_text_count':len(texts),'main_cmake_license':report['main_cmake_license'],'version':info['CFBundleShortVersionString']},indent=2))
