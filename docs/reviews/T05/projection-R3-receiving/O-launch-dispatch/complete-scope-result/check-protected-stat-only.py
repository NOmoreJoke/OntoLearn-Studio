"""Owner evidence: hash declared frozen inputs only; lstat other paths only."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PARENT = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees')
results = []
for model in ('zcode', 'minimax'):
    root = PARENT / ('T05-O-' + model + '-review-e15ce44')
    launch = root / 'docs/reviews/T05/projection-R3-receiving/launch-O'
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    def read_declared(relative):
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('nonlocal declared input')
        return path.read_bytes()
    mapping = json.loads((launch / 'launch-map.json').read_text())
    inventory = json.loads(read_declared(mapping['sourceInventory']))
    required = {f['path']: f for f in inventory['engineeringFiles']}
    for path, ref in mapping['protectedManifests'].items():
        raw = read_declared(path)
        assert raw == git('show', ref + ':' + path)
        for f in json.loads(raw)['files']:
            if f['path'] in required:
                assert (required[f['path']]['bytes'], required[f['path']]['sha256']) == (f['bytes'], f['sha256'])
            required[f['path']] = f
        required[path] = dict(path=path, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    checked = []
    for path, expected in sorted(required.items()):
        raw = read_declared(path)
        assert len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256'], path
        assert raw == git('show', mapping['frozenProcessRef'] + ':' + path), path
        checked.append(expected)
    inputs = json.loads((launch / 'launch-input-manifest.json').read_text())
    for f in inputs['files']:
        raw = read_declared(mapping['launchRelativeRoot'] + '/' + f['path'])
        assert len(raw) == f['bytes'] and hashlib.sha256(raw).hexdigest() == f['sha256'], f['path']
    policy = read_declared('AGENTS.md')
    assert len(policy) == mapping['currentAGENTS']['bytes'] and hashlib.sha256(policy).hexdigest() == mapping['currentAGENTS']['sha256']
    changed = [s.decode() for s in git('diff', '--name-only', '-z').split(b'\0') if s]
    assert changed == ['AGENTS.md']
    assert not git('diff', '--cached', '--name-only', '-z')
    assert git('rev-parse', 'HEAD').decode().strip() == mapping['frozenProcessRef']
    assert git('rev-parse', '--abbrev-ref', 'HEAD').decode().strip() == 'HEAD'
    tracked = {s.decode() for s in git('ls-files', '-z').split(b'\0') if s}
    extras = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in names + [n for n in dirs if (Path(directory) / n).is_symlink()]:
            path = Path(directory) / name
            relative = str(path.relative_to(root))
            if relative == '.git' or relative in tracked:
                continue
            stat = path.lstat()
            extras.append(dict(path=relative, bytes=stat.st_size, mtimeNs=stat.st_mtime_ns,
                               symlink=path.is_symlink(), attribution='unknown',
                               contentReadForThisInventory=False))
    results.append(dict(model=model, workspace=str(root), protectedCount=len(checked),
                        protectedFiles=checked, frozenLaunchMemberCount=len(inputs['files']),
                        protectedBytesPass=True, currentAGENTSPass=True, indexEmpty=True,
                        detachedHEAD=mapping['frozenProcessRef'], trackedChanges=changed,
                        otherPathsStatOnly=extras, wholeFilesystemFreezePass=False))
result = dict(format='T05-O-owner-protected-input-and-stat-only/1',
              observedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), models=results,
              noProductOrOracleExecution=True, unknownMetadataNeverOpenedOrHashed=True,
              note='Known launch input checks and stat inventory are distinct; extras are never attributed by filename.')
(HERE / 'protected-stat-readback.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps([dict(model=r['model'], protected=r['protectedCount'],
                       launch=r['frozenLaunchMemberCount'], extras=len(r['otherPathsStatOnly']),
                       protectedBytesPass=r['protectedBytesPass']) for r in results]))
