"""C4 fixed-input gate. Production CLI never accepts simulated mount proofs.

Owner-pinned external receipts break the image/manifest self-reference cycle.
The receipt is evidence, not a sandbox; current OS readonly/device checks are
also required. Fixtures inject a probe only through imported Python functions.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat


def require(value, reason):
    if not value:
        raise ValueError(reason)


def canonical(value, missing=False):
    require(isinstance(value, str) and value.startswith('/'), 'ABSOLUTE_PATH_REQUIRED')
    p = Path(value)
    require(str(p) == value and os.path.normpath(value) == value and '..' not in p.parts,
            'CANONICAL_PATH_REQUIRED')
    absent = False
    for q in [*reversed(p.parents), p]:
        try:
            s = q.lstat()
        except FileNotFoundError:
            require(missing, 'MISSING_PATH ' + str(q))
            absent = True
            continue
        require(not absent and not stat.S_ISLNK(s.st_mode), 'LINK_OR_CHANGED_ANCESTOR ' + str(q))
    return p


def read_file(path):
    p = canonical(str(path))
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        a = os.fstat(fd)
        require(stat.S_ISREG(a.st_mode) and a.st_nlink == 1, 'ORDINARY_SINGLE_LINK_REQUIRED')
        parts = []
        while True:
            b = os.read(fd, 1024 * 1024)
            if not b:
                break
            parts.append(b)
        z = os.fstat(fd)
        require((a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) ==
                (z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns), 'FILE_CHANGED_DURING_READ')
        b = b''.join(parts)
        return b, {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
                   'mode': oct(stat.S_IMODE(a.st_mode)), 'dev': a.st_dev, 'ino': a.st_ino}
    finally:
        os.close(fd)


def checked_json(path, expected):
    b, identity = read_file(path)
    require(isinstance(expected, str) and len(expected) == 64 and
            identity['sha256'] == expected, 'PINNED_JSON_HASH_MISMATCH ' + str(path))
    return json.loads(b), identity


def relpath(text):
    p = Path(text)
    require(isinstance(text, str) and text and not p.is_absolute() and
            '..' not in p.parts and '.' not in p.parts and p.as_posix() == text,
            'UNSAFE_RELATIVE_PATH')
    return p


def tree(root):
    """Directory-fd traversal: do not follow unknown files/links to inspect bodies."""
    files, dirs, visited_directories = set(), set(), set()
    root_device = None

    def visit(fd, prefix):
        current = os.fstat(fd)
        directory_id = (current.st_dev, current.st_ino)
        require(directory_id not in visited_directories, 'INPUT_DIRECTORY_ALIAS')
        visited_directories.add(directory_id)
        for name in sorted(os.listdir(fd)):
            s = os.stat(name, dir_fd=fd, follow_symlinks=False)
            rel = prefix + name
            require(s.st_dev == root_device, 'NESTED_MOUNT_OR_DEVICE_ALIAS ' + rel)
            require(not stat.S_ISLNK(s.st_mode), 'INPUT_SYMLINK ' + rel)
            if stat.S_ISDIR(s.st_mode):
                dirs.add(rel)
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    a = os.fstat(child)
                    require((a.st_dev, a.st_ino) == (s.st_dev, s.st_ino), 'INPUT_DIRECTORY_CHANGED')
                    visit(child, rel + '/')
                finally:
                    os.close(child)
            else:
                require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'INPUT_NOT_ORDINARY ' + rel)
                files.add(rel)

    root = canonical(str(root))
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        root_device = os.fstat(fd).st_dev
        visit(fd, '')
    finally:
        os.close(fd)
    return files, dirs


class OSProbe:
    def inspect(self, root):
        s = root.stat()
        return {'readonly': bool(os.statvfs(root).f_flag & os.ST_RDONLY),
                'dev': s.st_dev, 'ino': s.st_ino, 'kind': 'current-os-statvfs-and-stat'}


def root_binding(receipt_path, receipt_sha, probe=None):
    receipt, receipt_identity = checked_json(receipt_path, receipt_sha)
    require(receipt.get('schemaVersion') == 1 and
            receipt.get('infrastructureStatus') == 'actual-readonly-mount', 'ACTUAL_RO_MOUNT_REQUIRED')
    ro = canonical(receipt['inputRoot'])
    rw = canonical(receipt['taskRoot'])
    require(ro != rw and ro not in rw.parents and rw not in ro.parents, 'ROOTS_OVERLAP')
    for a in [ro, *ro.parents]:
        for b in [rw]:
            require((a.stat().st_dev, a.stat().st_ino) != (b.stat().st_dev, b.stat().st_ino),
                    'ROOT_ANCESTOR_ALIAS')
    volume_root = canonical(receipt['mount']['mountPoint'])
    require(ro == volume_root / 'input', 'FIXED_INPUT_SUBTREE_REQUIRED')
    observer = probe or OSProbe()
    observation = observer.inspect(volume_root)
    input_observation = observer.inspect(ro)
    require(observation['readonly'] is True, 'OS_INPUT_NOT_READONLY')
    mount = receipt['mount']
    require(input_observation['readonly'] is True and input_observation['dev'] == observation['dev'] and
            mount['readonly'] is True and
            mount.get('shadow') is False and mount.get('overlay') is False,
            'MOUNT_BINDING_OR_OVERLAY')
    require((observation['dev'], observation['ino']) == (mount['dev'], mount['ino']),
            'MOUNT_IDENTITY_CHANGED')
    require(observation['dev'] != rw.stat().st_dev, 'INPUT_NOT_SEPARATE_VOLUME')
    image = receipt['image']
    image_path = canonical(image['path'])
    require(ro not in image_path.parents and rw not in image_path.parents, 'IMAGE_IN_MUTABLE_TASK_OR_IMAGE')
    _, image_identity = read_file(image_path)
    require(image_identity['sha256'] == image['sha256'] and
            image_identity['bytes'] == image['bytes'], 'IMAGE_IDENTITY_CHANGED')
    proof, proof_identity = checked_json(receipt['mountObservationPath'], receipt['mountObservationSHA256'])
    require(proof.get('kind') == 'owner-observed-hdiutil-readonly-image' and
            proof.get('imagePath') == str(image_path) and proof.get('mountPoint') == str(volume_root) and
            proof.get('device') == mount['device'] and proof.get('readonly') is True and
            proof.get('shadow') is False and proof.get('overlay') is False,
            'OWNER_MOUNT_SOURCE_OBSERVATION_MISMATCH')
    return receipt, ro, rw, {'rootReceipt': receipt_identity, 'image': image_identity,
                            'mountObservation': proof_identity, 'osObservation': observation,
                            'notAtomicOrWholeApplicationSandbox': True}


def match_row(path, row):
    _, ident = read_file(path)
    require(all(ident[k] == row[k] for k in ['bytes', 'sha256', 'mode']), 'DECLARED_FILE_DRIFT ' + str(path))
    return ident


def resource_gate(root, manifest):
    """Only old explicitly declared dependency/browser/native closures, no machine scan."""
    dependency_manifest, _ = checked_json(root / 'config/resources.json', manifest['resourceManifestSHA256'])
    cache = canonical(dependency_manifest['resourceRoot'])
    actual, _ = tree(cache)
    rows = dependency_manifest['files']
    require(actual == {r['path'] for r in rows}, 'CACHE_EXACT_SET_DRIFT')
    for r in rows:
        match_row(cache / relpath(r['path']), r['copiedIdentity'])
    chrome = canonical(dependency_manifest['externalChromeRoot'])
    chrome_files, _ = tree(chrome)
    externals = dependency_manifest['externalReadOnlyResources']
    require({str(chrome / p) for p in chrome_files} ==
            {r['path'] for r in externals if chrome in Path(r['path']).parents}, 'CHROME_EXACT_SET_DRIFT')
    for r in externals:
        match_row(canonical(r['path']), r)
    native, _ = checked_json(root / 'config/native-resources.json', manifest['nativeManifestSHA256'])
    native_root = canonical(native['resourceRoot'])
    regular_rows = [r for r in native['entries'] if r.get('type', 'file') == 'file']
    require(len(regular_rows) == 164 and len(native['entries']) == 164, 'EXPECTED_NATIVE_CLOSURE')
    # The actual entry schema is frozen by preparation; refuse unknown aliases.
    for r in regular_rows:
        match_row(native_root / relpath(r['path']), r)
    return len(rows) + len(externals) + len(regular_rows)


def gate(receipt_path, receipt_sha, resources=True, probe=None):
    receipt, ro, rw, proof = root_binding(receipt_path, receipt_sha, probe)
    manifest, manifest_identity = checked_json(ro / 'input-manifest.json', receipt['inputManifestSHA256'])
    require(manifest['inputRoot'] == str(ro) and manifest['taskRoot'] == str(rw), 'MANIFEST_ROOT_BINDING')
    require(manifest.get('selfFile') == 'input-manifest.json' and manifest.get('exclusions') == [],
            'EXACT_SET_NO_EXCLUSIONS_REQUIRED')
    rows = manifest['files']
    names = [str(relpath(r['path'])) for r in rows]
    require(len(names) == len(set(names)) and 'input-manifest.json' not in names, 'DUPLICATE_OR_SELF_MANIFEST')
    files, dirs = tree(ro)
    require(files == set(names) | {'input-manifest.json'}, 'INPUT_EXACT_FILE_SET_DRIFT')
    require(dirs == set(manifest['directories']), 'INPUT_EXACT_DIRECTORY_SET_DRIFT')
    before = {r['path']: match_row(ro / r['path'], r) for r in rows}
    for pin, rel in [('checkerSHA256', 'check-inputs.py'), ('helperSHA256', 'run-tool.py'),
                     ('runnerSHA256', 'tooling/owned-browser-runner.mjs')]:
        require(before[rel]['sha256'] == receipt[pin], 'ROOT_CODE_PIN_MISMATCH ' + rel)
    config = json.loads(read_file(ro / 'config/runtime-config.json')[0])
    require(config['inputRoot'] == str(ro) and config['taskRoot'] == str(rw) and
            config['cwd'] == str(rw / 'environment'), 'CONFIG_ROOT_BINDING')
    require(set(config['commands']) == {'browserBuild', 'browserVerify', 'nativeCLI'}, 'THREE_COMMANDS_REQUIRED')
    for mirror in manifest['mirrors']:
        source = before[mirror['source']]
        current = read_file(rw / relpath(mirror['target']))[1]
        require(all(source[k] == current[k] for k in ['bytes', 'sha256']), 'NONAUTHORITY_MIRROR_DRIFT')
    count = resource_gate(ro, manifest) if resources else 0
    require(tree(ro) == (files, dirs), 'INPUT_SET_CHANGED_DURING_CHECK')
    return {'passed': True, 'fixedFiles': len(rows) + 1, 'checkedResources': count,
            'inputRoot': str(ro), 'taskRoot': str(rw), 'proof': proof,
            'manifestIdentity': manifest_identity, 'fileIdentity': before,
            'evidenceScope': 'Observed exact input/OS/source/mirror/resource checks; not an atomic lifetime or application sandbox proof.'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root-receipt', required=True)
    p.add_argument('--root-receipt-sha256', required=True)
    p.add_argument('--no-resources', action='store_true')
    a = p.parse_args()
    result = gate(a.root_receipt, a.root_receipt_sha256, not a.no_resources)
    result.pop('fileIdentity')
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'passed': False, 'error': str(exc)}))
        raise SystemExit(1)
