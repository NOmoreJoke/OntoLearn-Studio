"""Read-only final process/Git manifest check, without writing inside its own inputs."""

import hashlib
import json
import subprocess
from pathlib import Path

base = Path(__file__).resolve().parent.relative_to(Path.cwd())
contract = Path('docs/iterations/T05/profile-M1-directsteps-consumer-contract.md')
manifest_path = base / 'delivery-manifest.json'
manifest = json.loads(manifest_path.read_text())
listed = {row['path'] for row in manifest['files']}
actual = {str(p) for p in base.rglob('*') if p.is_file() and p != manifest_path}
actual.add(str(contract))
assert listed == actual, sorted(actual - listed)
assert len(listed) == manifest['fileCount']
head = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
for row in manifest['files']:
    raw = Path(row['path']).read_bytes()
    assert len(raw) == row['bytes']
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    assert raw == subprocess.check_output(['git', 'show', head + ':' + row['path']])
assert manifest_path.read_bytes() == subprocess.check_output([
    'git', 'show', head + ':' + str(manifest_path)
])
names = {p for p in subprocess.check_output([
    'git', 'diff', '--name-only', '-z',
    'e0ee604ae5e63b4dfdda5db984c0eec8b59a65f5', head
]).decode().split('\0') if p}
assert names == listed | {str(manifest_path)}
assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'])
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'])
fixed = json.loads((base / 'fixed-inputs.json').read_text())
assert all(row['snapshotPath'] in listed for row in fixed['files'])
untracked = set(subprocess.check_output([
    'git', 'ls-files', '--others', '--exclude-standard'
]).decode().splitlines())
old = Path('docs/reviews/T05/profile-M1-math-observation')
assert untracked == {str(old / (tag + '-actuals.zip')) for tag in (
    'first-full', 'p2-full', 'final-full'
)}
print(json.dumps({
    'head': head, 'docsOnlyFiles': len(names),
    'allManifestBytesEqualGit': True, 'all26FixedInputsIncluded': True,
    'trackedClean': True, 'untrackedOnlyOriginalThreeZips': True,
    'productLibraryTestsGuiNetworkExecution': False
}, ensure_ascii=False, indent=2))
