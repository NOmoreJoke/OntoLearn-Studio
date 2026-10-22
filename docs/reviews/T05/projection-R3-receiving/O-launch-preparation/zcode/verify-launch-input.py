#!/usr/bin/env python3
"""Static launch identity check; never import repository code or run product tests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('setup', 'observe'), default='setup')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    mapping = json.loads((here / 'launch-map.json').read_text())
    root = Path(mapping['actualWorkspace'])
    if Path.cwd().resolve() != root or here != root / mapping['launchRelativeRoot']:
        raise ValueError('run only inside the assigned review workspace')

    def git(*argv):
        return subprocess.check_output(['git', *argv], cwd=root)

    def local(path):
        p = root / path
        if p.resolve().is_relative_to(root) is False or p.is_symlink():
            raise ValueError('non-local or symlink input: ' + path)
        return p

    ref = mapping['frozenProcessRef']
    if git('rev-parse', 'HEAD').decode().strip() != ref:
        raise ValueError('review HEAD changed')
    if git('rev-parse', '--abbrev-ref', 'HEAD').decode().strip() != 'HEAD':
        raise ValueError('expected detached review HEAD')
    if git('diff', '--cached', '--name-only', '-z'):
        raise ValueError('review index must remain empty')
    changed = [p.decode() for p in git('diff', '--name-only', '-z', ref).split(b'\0') if p]
    if changed != ['AGENTS.md']:
        raise ValueError('tracked changes must be exactly protected current AGENTS: ' + repr(changed))
    policy = local('AGENTS.md').read_bytes()
    if len(policy) != mapping['currentAGENTS']['bytes'] or digest(policy) != mapping['currentAGENTS']['sha256']:
        raise ValueError('current AGENTS propagation not complete')

    inventory = json.loads(local(mapping['sourceInventory']).read_text())
    original_tree = []
    for item in git('ls-tree', '-r', '-l', '-z', mapping['frozenSourceRef']).split(b'\0'):
        if not item:
            continue
        metadata, path = item.split(b'\t', 1)
        mode, kind, blob, size = metadata.decode().split()
        original_tree.append({'path': path.decode(), 'mode': mode, 'gitType': kind,
                              'gitBlob': blob, 'bytes': int(size)})
    if original_tree != inventory['fullTrackedTree']:
        raise ValueError('fixed original source tree differs from inventory')

    required = {f['path']: f for f in inventory['engineeringFiles']}
    for manifest_path, manifest_ref in mapping['protectedManifests'].items():
        raw = local(manifest_path).read_bytes()
        if raw != git('show', manifest_ref + ':' + manifest_path):
            raise ValueError('protected manifest changed: ' + manifest_path)
        manifest = json.loads(raw)
        for f in manifest['files']:
            if f['path'] in required:
                if (required[f['path']]['bytes'], required[f['path']]['sha256']) != (f['bytes'], f['sha256']):
                    raise ValueError('conflicting required identity')
            required[f['path']] = f
        required[manifest_path] = {'path': manifest_path, 'bytes': len(raw), 'sha256': digest(raw)}
    checked = []
    for path, expected in sorted(required.items()):
        raw = local(path).read_bytes()
        if len(raw) != expected['bytes'] or digest(raw) != expected['sha256']:
            raise ValueError('protected current bytes/SHA differ: ' + path)
        if raw != git('show', ref + ':' + path):
            raise ValueError('protected current bytes/Git differ: ' + path)
        checked.append({'path': path, 'bytes': len(raw), 'sha256': digest(raw)})

    input_manifest_path = here / 'launch-input-manifest.json'
    inputs = json.loads(input_manifest_path.read_text())
    for f in inputs['files']:
        raw = local(mapping['launchRelativeRoot'] + '/' + f['path']).read_bytes()
        if len(raw) != f['bytes'] or digest(raw) != f['sha256']:
            raise ValueError('launch input differs: ' + f['path'])
    tracked = {p.decode() for p in git('ls-files', '-z').split(b'\0') if p}
    fixed = {p.decode() for p in git('ls-tree', '-r', '--name-only', '-z', ref).split(b'\0') if p}
    if tracked != fixed:
        raise ValueError('review index path set differs from frozen process')
    output_path = here / ('preflight-' + args.phase + '.json')
    allowed_inputs = {mapping['launchRelativeRoot'] + '/' + f['path'] for f in inputs['files']}
    allowed_inputs.add(str(input_manifest_path.relative_to(root)))
    own_outputs = mapping['ownOutputPrefixes']
    own_output_files = set(mapping['ownOutputFiles'])
    extra = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in dirs:
            if (Path(directory) / name).is_symlink():
                raise ValueError('unregistered directory symlink inside review workspace')
        for name in names:
            path = Path(directory) / name
            relative = str(path.relative_to(root))
            if relative == '.git' or relative in tracked or path == output_path:
                continue
            raw = local(relative).read_bytes()
            declared = (relative in allowed_inputs or relative in own_output_files
                        or any(relative.startswith(p) for p in own_outputs))
            extra.append({'path': relative, 'bytes': len(raw), 'sha256': digest(raw),
                          'declaredOwnSurface': declared})
    unknown = [f['path'] for f in extra if not f['declaredOwnSurface']]
    result = {
        'format': 'T05-O-isolated-static-launch-preflight/1', 'phase': args.phase,
        'workspace': str(root), 'modelRole': mapping['modelRole'], 'frozenProcessRef': ref,
        'frozenSourceRef': mapping['frozenSourceRef'], 'detachedHEAD': True,
        'originalTrackedTreeMetadataCount': len(original_tree), 'trackedProcessPaths': len(tracked),
        'currentAGENTS': mapping['currentAGENTS'], 'protectedAGENTSUnstagedOnly': True,
        'engineeringFiles': len(inventory['engineeringFiles']),
        'protectedUniqueCurrentGitSHAFiles': len(checked), 'protectedFiles': checked,
        'launchManifestSHA256': digest(input_manifest_path.read_bytes()),
        'launchInputsChecked': len(inputs['files']), 'allActualUntrackedFilesExceptExactOutput': extra,
        'unknownNewMetadataPaths': unknown, 'metadataOmission': 'only .git administrative link and exact output self',
        'sourceAndInputBytesVerified': True, 'setupReady': args.phase == 'setup' and not unknown,
        'thisToolExecutedModelOrProductOrOriginalOracle': False,
        'actualTaskIdentityOrCountInspected': False,
        'note': 'Static preparation/observation only. New metadata is recorded, never deleted or ignored to claim freeze Pass. Actual task identity/settings/terminal and review verdict require separate real evidence.'
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('workspace', 'phase', 'protectedUniqueCurrentGitSHAFiles',
                                           'sourceAndInputBytesVerified', 'setupReady', 'unknownNewMetadataPaths')}))
    return 0 if not unknown else 2


if __name__ == '__main__':
    raise SystemExit(main())
