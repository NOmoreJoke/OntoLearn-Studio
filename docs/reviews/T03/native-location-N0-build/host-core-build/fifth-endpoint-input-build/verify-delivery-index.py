from pathlib import Path
import hashlib, json, subprocess, sys
root = Path.cwd()
d = root / 'docs/reviews/T03/native-location-N0-build/host-core-build/fifth-endpoint-input-build'
manifest_path = d / 'delivery-manifest.json'
raw = manifest_path.read_bytes()
m = json.loads(raw)
files = list(m['files']) + [{'path': str(manifest_path.relative_to(root)), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}]
assert len({x['path'] for x in files}) == len(files)
requests = b''.join((':' + x['path'] + '\n').encode() for x in files)
r = subprocess.run(['git', 'cat-file', '--batch'], input=requests, capture_output=True, check=True)
pos = 0
mismatches = []
for f in files:
    end = r.stdout.index(b'\n', pos)
    header = r.stdout[pos:end].decode(); pos = end + 1
    parts = header.split()
    if len(parts) != 3 or parts[1] != 'blob':
        mismatches.append({'path': f['path'], 'reason': header}); continue
    size = int(parts[2]); data = r.stdout[pos:pos+size]; pos += size
    assert r.stdout[pos:pos+1] == b'\n'; pos += 1
    current = (root / f['path']).read_bytes()
    if len(data) != f['bytes'] or hashlib.sha256(data).hexdigest() != f['sha256'] or current != data:
        mismatches.append({'path': f['path'], 'expectedBytes': f['bytes'], 'indexBytes': len(data), 'indexSHA256': hashlib.sha256(data).hexdigest(), 'workingTreeEqualsIndex': current == data})
assert pos == len(r.stdout)
expected = {f['path']: f for f in files}
for name in ['driver-raw-manifest.json', 'generated-evidence-manifest.json']:
    catalog = json.loads((d / name).read_bytes())
    for f in catalog['files']:
        dest = f.get('archivedPath')
        assert dest in expected, (name, f)
        assert expected[dest]['bytes'] == f['bytes'] and expected[dest]['sha256'] == f['sha256'], (name, dest)
staged = subprocess.run(['git', 'diff', '--cached', '--name-only', '-z'], capture_output=True, check=True).stdout.split(b'\0')
assert all(not x or x.decode().startswith(str(d.relative_to(root)) + '/') for x in staged)
print(json.dumps({'manifestPath': str(manifest_path.relative_to(root)), 'manifestBytes': len(raw), 'manifestSHA256': hashlib.sha256(raw).hexdigest(), 'manifestRecordsPlusSelf': len(files), 'indexAndWorkingTreeMismatches': mismatches, 'copiedRawPinCatalogsMatched': True, 'stagedScope': 'fifth-endpoint-input-build process files only', 'artifactExecution': False}))
assert not mismatches, mismatches
