"""Static files only. Does not import or execute any installed product/package."""

import hashlib
import json
import os
from pathlib import Path
import stat
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
ticket = json.loads((HERE / 'setup-authorization.json').read_text())


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')


def info(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def tree(base):
    files, links, identities = [], [], set()
    if not base.exists():
        return files, links, identities
    assert not base.is_symlink()
    for current, dirs, names in os.walk(base, followlinks=False):
        for name in dirs + names:
            p = Path(current) / name
            s = p.lstat()
            if stat.S_ISLNK(s.st_mode):
                links.append({'path': str(p), 'target': os.readlink(p), 'resolved': str(p.resolve())})
            elif stat.S_ISREG(s.st_mode):
                identities.add((s.st_dev, s.st_ino))
                files.append({'path': str(p), 'bytes': s.st_size, 'device': s.st_dev, 'inode': s.st_ino})
    return files, links, identities


rows, identities = [], {}
for role in ticket['roles']:
    root, runtime = Path(role['cwd']), Path(role['namespace'])
    setup = runtime / 'setup'
    execution = json.loads((setup / 'role-execution-receipt.json').read_text())
    lock = json.loads((root / 'package-lock.json').read_text())
    npmfiles, npmlinks, npmids = tree(root / 'node_modules')
    pyfiles, pylinks, pyids = tree(root / '.venv')
    identities[role['role']] = npmids | pyids
    packages = []
    for x in npmfiles:
        p = Path(x['path'])
        if p.name != 'package.json':
            continue
        relative = p.parent.relative_to(root).as_posix()
        if relative not in lock['packages']:
            continue
        package = json.loads(p.read_text())
        expected = lock['packages'][relative]
        assert package.get('version') == expected.get('version'), (relative, package.get('version'), expected.get('version'))
        packages.append({**info(p), 'name': package.get('name'), 'version': package.get('version'), 'lockPath': relative, 'lockVersionMatches': True})
    pymetadata = []
    for x in pyfiles:
        p = Path(x['path'])
        if '.dist-info' in str(p.parent) and p.name in ['METADATA', 'WHEEL', 'INSTALLER', 'RECORD', 'direct_url.json']:
            row = info(p)
            if p.name == 'direct_url.json':
                row['content'] = json.loads(p.read_text())
            elif p.name == 'METADATA':
                lines = p.read_text().splitlines()
                row['name'] = next((s[6:] for s in lines if s.startswith('Name: ')), None)
                row['version'] = next((s[9:] for s in lines if s.startswith('Version: ')), None)
            pymetadata.append(row)
    pths = []
    for x in pyfiles:
        p = Path(x['path'])
        if p.suffix == '.pth':
            pths.append({**info(p), 'content': p.read_text()})
    dirs = []
    for name in ['home', 'tmp', 'xdg-cache', 'xdg-config', 'xdg-data', 'npm-cache', 'uv-cache', 'setup']:
        p = runtime / name
        s = p.stat()
        dirs.append({'path': str(p), 'device': s.st_dev, 'inode': s.st_ino, 'isSymlink': p.is_symlink()})
    for name in ['node_modules', '.venv']:
        p = root / name
        if p.exists():
            s = p.stat()
            dirs.append({'path': str(p), 'device': s.st_dev, 'inode': s.st_ino, 'isSymlink': p.is_symlink()})
    assert all(not x['isSymlink'] for x in dirs)
    allowed_base = Path(ticket['pinnedExistingPython']['path']).parent
    assert all(Path(x['resolved']).is_relative_to(root) for x in npmlinks), 'npm symlink escapes role'
    assert all(Path(x['resolved']).is_relative_to(root) or Path(x['resolved']).is_relative_to(allowed_base) for x in pylinks), 'venv symlink escapes role or pinned base'
    scratch = runtime / 'scratch/probe-copy'
    assert all(not os.path.lexists(scratch / x) for x in ['.venv', 'node_modules'])
    configs = []
    for name in ['npm-user-empty.npmrc', 'npm-global-empty.npmrc']:
        p = setup / name
        assert p.read_bytes() == b'' and stat.S_IMODE(p.stat().st_mode) == 0o600
        configs.append({**info(p), 'mode': '0600'})
    row = {'role': role['role'], 'UTC': datetime.now(timezone.utc).isoformat(),
           'method': 'Static file metadata/JSON/hash/stat only; no installed executables or product imports',
           'executionStatus': execution['status'], 'directoryIdentities': dirs, 'emptyNpmConfigs': configs,
           'nodeRegularFiles': npmfiles, 'nodeSymlinks': npmlinks, 'installedNpmPackageMetadata': packages,
           'pythonRegularFiles': pyfiles, 'pythonSymlinks': pylinks, 'pythonDistributionMetadata': pymetadata,
           'pythonPthFiles': pths, 'scratchDependenciesAbsent': True,
           'electronDownloadedBinaryPresent': (root / 'node_modules/electron/dist').exists(),
           'playwrightBrowserDirectoryPresentInOwnHome': (runtime / 'home/Library/Caches/ms-playwright').exists(),
           'pyvenvCfg': {'content': (root / '.venv/pyvenv.cfg').read_text(), **info(root / '.venv/pyvenv.cfg')} if (root / '.venv/pyvenv.cfg').exists() else None,
           'npmInstalledLock': info(root / 'node_modules/.package-lock.json') if (root / 'node_modules/.package-lock.json').exists() else None,
           'noProductValidationClaim': True, 'oldRejectedVerificationNotLifted': True}
    assert not row['electronDownloadedBinaryPresent'] and not row['playwrightBrowserDirectoryPresentInOwnHome']
    save(setup / 'installed-metadata.json', row)
    rows.append({'role': role['role'], 'metadata': info(setup / 'installed-metadata.json'),
                 'npmPackageMetadataCount': len(packages), 'pythonDistributionMetadataFiles': len(pymetadata),
                 'regularDependencyFiles': len(npmfiles) + len(pyfiles), 'directoryIdentities': dirs})
assert len({(x['device'], x['inode']) for r in rows for x in r['directoryIdentities']}) == sum(len(r['directoryIdentities']) for r in rows)
overlap = identities['zcode'] & identities['minimax']
assert not overlap, 'cross-role regular mutable dependency file inode sharing'
save(HERE / 'static-installed-isolation.json', {'roles': rows, 'crossRoleRegularDependencyInodeIntersection': len(overlap),
     'declaredMutableDirectoryIdentitiesAllUnique': True, 'pinnedBasePythonSymlinkSharedReadOnly': True,
     'noProductOrInstalledToolExecuted': True})
print(json.dumps({'roles': [(r['role'], r['npmPackageMetadataCount'], r['pythonDistributionMetadataFiles']) for r in rows], 'crossRoleRegularInodeOverlap': len(overlap)}))
