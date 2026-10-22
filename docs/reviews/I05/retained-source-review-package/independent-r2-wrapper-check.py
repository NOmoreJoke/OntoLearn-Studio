"""R2 independent packet delta. Read fixed Git and two exact wrappers only."""
import base64
import collections
import datetime
import hashlib
import json
import os
import pathlib
import stat
import subprocess
import sys
import traceback

TREE = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package')
PREFIX = 'docs/reviews/I05/retained-source-review-package/'
ROOT = TREE / PREFIX
PRIOR = '1106f15629c41833be9c9604eb7bf02134fa0541'
CANDIDATE = '92652c2db7ad600e9c4ab304812fede7943a8f01'
PROCESS = 'dbf5b6a741d15e5c62b2992ec0a077c28adb2856'
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load(name):
    return json.loads((ROOT / name).read_bytes())

def run(argv, expected=0, reference=None, stdin=None):
    cp = subprocess.run(argv, cwd=TREE, input=stdin, capture_output=True)
    row = {'argv': argv, 'cwd': str(TREE), 'exitCode': cp.returncode, 'stdoutBytes': len(cp.stdout), 'stdoutSHA256': sha(cp.stdout), 'stderrBase64': base64.b64encode(cp.stderr).decode(), 'stderrBytes': len(cp.stderr)}
    if reference is None:
        row['stdoutBase64'] = base64.b64encode(cp.stdout).decode()
    else:
        row['stdoutLosslessFixedGitReference'] = reference
    if stdin is not None:
        row['stdinBase64'] = base64.b64encode(stdin).decode()
    proof['commands'].append(row)
    assert cp.returncode == expected, row
    return cp.stdout

def listing(ref):
    raw = run(['git', 'ls-tree', '-r', '-z', '-l', '--full-tree', ref])
    out = {}
    for item in raw.split(b'\0'):
        if not item:
            continue
        meta, p = item.split(b'\t', 1)
        mode, kind, oid, size = meta.decode().split()
        assert kind == 'blob'
        out[p.decode()] = {'mode': mode, 'gitBlob': oid, 'bytes': int(size)}
    return out

def safe(p):
    return bool(p) and not p.startswith('/') and '\\' not in p and all(x not in ('', '.', '..') for x in p.split('/'))

hash_cache = {}
def identity(path):
    st = path.lstat()
    assert stat.S_ISREG(st.st_mode)
    key = (st.st_dev, st.st_ino)
    if key not in hash_cache:
        h = hashlib.sha256()
        g = hashlib.sha1(b'blob ' + str(st.st_size).encode() + b'\0')
        n = 0
        with path.open('rb') as f:
            while block := f.read(1024 * 1024):
                h.update(block); g.update(block); n += len(block)
        assert n == st.st_size
        hash_cache[key] = {'bytes': n, 'sha256': h.hexdigest(), 'gitBlob': g.hexdigest()}
    return hash_cache[key], st

def exact(path, row, git=False):
    actual, st = identity(path)
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256'], str(path)
    if git:
        assert actual['gitBlob'] == row['gitBlob'], str(path)
    return actual, st

FIRST = ROOT / 'independent-r2-first-check-failure.json'
if not FIRST.exists():
    FIRST.write_bytes((ROOT / 'independent-proof-r2.json').read_bytes())
proof = json.loads(FIRST.read_bytes())
assert proof['result'] == 'FAIL' and len(proof['failures']) == 1
proof['firstFailureBoundary'] = {'file': FIRST.name, 'bytes': FIRST.stat().st_size, 'sha256': sha(FIRST.read_bytes()), 'meaning': 'Checker required0555 on the outer wrapper container. Actual input subdirectories are the readonly scope; container root is0755 and excluded from internal2428 directory preflight. Preserve observation, check intended input/output scope without claiming outer root readonly.'}
proof['continuationArgv'] = sys.argv
def main():
    im = load('input-manifest.json')
    member_rows = {r['member']: r for r in im['members']}
    maps = load('original-material-map-r2.json')
    candidate = {r['path']: r for r in load('candidate-git-manifest-r2.json')['entries']}
    spec = load('physical-copy-spec-r2.json')
    setup = load('setup-receipt-r2.json')
    dispatch = load('dispatch-r2.json')
    assert setup['packetCandidate'] == CANDIDATE
    assert setup['actualTaskCount'] == dispatch['actualTaskCount'] == 0
    assert setup['actualApplicationGrowthVerified'] is False and dispatch['applicationGrowthVerified'] is False
    exact(ROOT / 'physical-copy-spec-r2.json', setup['copySpec'])
    register = pathlib.Path(setup['registerPath'])
    exact(register, setup['registerHash'])
    assert len(spec['common']) == 60 and len(spec['reviewers']) == 2
    wrapper_results = []; wrapper_inode_sets = []
    for reviewer in spec['reviewers']:
        root = pathlib.Path(reviewer['root'])
        assert root.name in ('I05-retained-review-zcode', 'I05-retained-review-minimax')
        root_mode = f'{stat.S_IMODE(root.lstat().st_mode):04o}'
        assert root_mode == '0755'
        manifest_path = root / 'instructions/own-input-manifest.json'
        own_manifest = json.loads(manifest_path.read_bytes())
        assert own_manifest['root'] == str(root) and own_manifest['packetCandidate'] == CANDIDATE
        assert own_manifest['actualTaskCount'] == 0 and own_manifest['nativeTaskId'] is None
        assert own_manifest['applicationMetadataGrowthVerified'] is False
        assert own_manifest['settingsReadback'] == 'pending' and own_manifest['branch'] is None
        preflight = load('wrapper-' + reviewer['key'] + '-preflight-r2.json')
        exact(manifest_path, preflight['ownManifest'])
        setup_copy = next(r for r in setup['actualCopies'] if r['key'] == reviewer['key'])
        exact(ROOT / setup_copy['preflight'], setup_copy)
        common = spec['common']; copied = common + reviewer['files']
        assert len(copied) == 64 and len(own_manifest['copiedFiles']) == 64
        actual_files = {}; actual_dirs = {}; inode_paths = collections.defaultdict(list)
        def walk(directory):
            for entry in sorted(os.scandir(directory), key=lambda x: x.name):
                p = pathlib.Path(entry.path); rel = p.relative_to(root).as_posix()
                assert safe(rel) and '.git' not in rel.split('/')
                st = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(st.st_mode):
                    actual_dirs[rel] = st
                    walk(p)
                else:
                    assert stat.S_ISREG(st.st_mode), rel
                    actual_files[rel] = st
                    inode_paths[(st.st_dev, st.st_ino)].append(rel)
        walk(root)
        assert len(actual_files) == 22557 and len(actual_dirs) == 2428
        expected_files = {'data/' + r['member'] for r in im['members']} | {r['destination'] for r in copied} | {'instructions/own-input-manifest.json'}
        assert set(actual_files) == expected_files
        expected_dirs = set(spec['mutableDirectories'])
        for p in expected_files:
            expected_dirs.update(parent.as_posix() for parent in pathlib.PurePosixPath(p).parents if parent.as_posix() != '.')
        assert set(actual_dirs) == expected_dirs
        mutable = set(spec['mutableDirectories'])
        for p, st in actual_dirs.items():
            assert stat.S_IMODE(st.st_mode) == (0o700 if p in mutable else 0o555), p
        for p, st in actual_files.items():
            assert stat.S_IMODE(st.st_mode) == 0o444
        # Every observed path/inode/type/mode still equals exact setup preflight.
        assert {r['path'] for r in preflight['fullPathset']} == set(actual_files) | set(actual_dirs)
        for row in preflight['fullPathset']:
            st = actual_files.get(row['path'], actual_dirs.get(row['path']))
            assert st.st_dev == row['device'] and st.st_ino == row['inode']
            assert f'{stat.S_IMODE(st.st_mode):04o}' == row['mode']
            assert ('file' if stat.S_ISREG(st.st_mode) else 'directory') == row['kind']
            assert (st.st_size if row['kind'] == 'file' else None) == row['bytes']
            assert st.st_nlink == row['links']
        own_copied = {r['path']: r for r in own_manifest['copiedFiles']}
        for row in copied:
            path = root / row['destination']; value, st = exact(path, row)
            source_value, source_st = exact(ROOT / row['source'], row)
            assert value == source_value
            assert (st.st_dev, st.st_ino) != (source_st.st_dev, source_st.st_ino)
            own = own_copied[row['destination']]
            assert own['device'] == st.st_dev and own['inode'] == st.st_ino
            assert all(own[k] == row[k] for k in ('bytes', 'sha256'))
            assert own['sourcePacketPath'] == row['source']
            assert candidate[PREFIX + row['source']]['gitBlob'] == value['gitBlob']
        assert len(own_manifest['materialized']) == 22492
        own_materialized = {r['path']: r for r in own_manifest['materialized']}
        seen = {}; payloads = set(); regular = hardlinks = 0
        for row in im['members']:
            rel = 'data/' + row['member']; path = root / rel
            value, st = exact(path, row, True)
            inode = (st.st_dev, st.st_ino)
            own = own_materialized[rel]
            assert all(own[k] == row[k] for k in ('sourceRef', 'sourcePath', 'bytes', 'sha256', 'gitBlob'))
            assert own['device'] == st.st_dev and own['inode'] == st.st_ino and own['mode'] == '0444'
            target = row['hardlinkTarget']
            if target is None:
                assert inode not in payloads
                regular += 1; payloads.add(inode)
                assert own['internalHardlinkTarget'] is None
            else:
                assert safe(target) and target in seen
                assert inode == seen[target]
                assert own['internalHardlinkTarget'] == 'data/' + target
                hardlinks += 1
            seen[row['member']] = inode
        assert (regular, hardlinks, len(payloads)) == (3006, 19486, 3006)
        # Hardlinks stay wholly inside this root, with no hidden outside aliases.
        for inode, paths in inode_paths.items():
            assert actual_files[paths[0]].st_nlink == len(paths)
        file_inodes = set(inode_paths)
        directory_inodes = {(st.st_dev, st.st_ino) for st in actual_dirs.values()}
        assert file_inodes.isdisjoint(directory_inodes)
        wrapper_inode_sets.append(file_inodes | directory_inodes | {(root.lstat().st_dev, root.lstat().st_ino)})
        baselines = {}
        for mutable_dir in spec['mutableDirectories']:
            content = sorted(p.relative_to(root).as_posix() for p in (root / mutable_dir).iterdir())
            assert content == own_manifest['outputBaseline'][mutable_dir]
            baselines[mutable_dir] = content
        assert baselines == {'reports': [], 'scratch': [], 'review-status': ['review-status/application-metadata'], 'review-status/application-metadata': []}
        assert sorted(p.name for p in (root / 'instructions').glob('*input-r2.md')) == [reviewer['key'] + '-input-r2.md']
        for original in maps['originals']:
            exact(root / 'data' / original['archiveMember'], original, True)
        prompt_path = root / 'instructions' / (reviewer['key'] + '-input-r2.md')
        peer = 'I05-retained-review-minimax' if reviewer['key'] == 'zcode-glm53' else 'I05-retained-review-zcode'
        assert peer not in prompt_path.read_text()
        total_copied = sum(r['bytes'] for r in copied)
        assert total_copied == preflight['copiedBytes']
        logical = sum(r['bytes'] for r in im['members'])
        assert logical == 1938077906 == preflight['materializedLogicalBytes']
        wrapper_results.append({'root': str(root), 'outerContainerMode': root_mode, 'outerContainerExcludedFromInputDirectoryClaim': True, 'files': len(actual_files), 'directories': len(actual_dirs), 'fullPathsetPreflightIdentity': True, 'allInputs0444Dirs0555Outputs0700': True, 'materializedMembers': 22492, 'payloadInodes': regular, 'backwardInternalHardlinks': hardlinks, 'allPathBytesSHA256GitBlob': True, 'manifestBytes': manifest_path.stat().st_size, 'manifestSHA256': sha(manifest_path.read_bytes()), 'promptBytes': prompt_path.stat().st_size, 'promptSHA256': sha(prompt_path.read_bytes()), 'copiedBytes': total_copied, 'logicalDataBytes': logical, 'noGitSymlinksSpecialFiles': True, 'noOutsideHardlinkAlias': True, 'mutableBaseline': baselines, 'actualTaskCount': 0, 'applicationGrowthVerified': False})
    assert wrapper_inode_sets[0].isdisjoint(wrapper_inode_sets[1])
    proof['checks']['wrappers'] = {'roots': wrapper_results, 'crossRootSharedFileOrDirectoryInodes': 0, 'inputOutputSharedInodes': 0, 'actualCopiedSourceIdentityIndependent': True, 'scope': 'Only two explicitly authorized roots; no global or other task metadata read'}
    # Preserve truthful historical failures; never execute author scripts.
    history = []
    for name in ['freeze-command-log-r2.json', 'freeze-continuation-command-log-r2.json', 'finalize-command-log-r2.json', 'author-command-log-r2.json']:
        obj = load(name)
        rows = obj if isinstance(obj, list) else obj.get('commands', obj.get('records', []))
        for i, row in enumerate(rows):
            for stream in ('stdoutBase64', 'stderrBase64'):
                if stream in row:
                    base64.b64decode(row[stream], validate=True)
            history.append({'path': name, 'index': i, 'exit': row.get('exit', row.get('exitCode')), 'argv': row.get('argv'), 'rawStreamsRetainedInFixedOriginal': True})
    failed = load('freeze-first-failure-r2.json')
    assert failed['exit'] == 1 and failed['exactFailedCommandRecord']['exit'] == 1
    assert any(r['exit'] == 1 for r in history)
    proof['checks']['historicalLogs'] = {'records': history, 'firstFormatterExit1Preserved': True, 'sequentialContinuationZeroRecordsPresent': any(r['exit'] == 0 and '--check' in r['argv'] for r in history), 'originalHistoricalR1FailAndWhitespaceExceptionsRetained': True, 'authorScriptsExecuted': False}
    run(['git', 'diff', '--check', BASE, PROCESS, '--', PREFIX], expected=2)
    run(['git', 'diff', '--check', BASE, PROCESS, '--', PREFIX, ':(exclude)' + PREFIX + 'author-build.py', ':(exclude)' + PREFIX + 'author-finish-first.py'])
    proof['checks']['whitespace'] = {'completeBaseExit': 2, 'exactTwoHistoricalHelperExclusionsExit': 0}
    proof['checks']['closingBoundaries'] = {'actualTasks': 0, 'nativeTaskIDs': None, 'taskSettings': 'pending real readback', 'applicationMetadataGrowth': 'not tested; root exact-task path confirmation required', 'productRuntime': 'not executed/not passed', 'modelDispatch': 'not authorized for reviewer', 'rootFullPreflightAndShortLease': 'still required'}
    proof['findings'] = []
    proof['disposition'] = {'PKT-R1-P2-01': 'CLOSED for exact original reading map', 'PKT-R1-P2-02': 'CLOSED for actual input-copy/initial-output isolation; real application creation/settings/metadata growth remain root preflight'}
    proof['result'] = 'PASS limited to R2 static input-copy readiness and packet delta; no actual review-task/model/product/release Pass'
    proof['finalStatus'] = run(['git', 'status', '--porcelain=v1']).decode()
    assert run(['git', 'diff', '--cached', '--name-only', '-z']) == b''

try:
    main()
except BaseException as exc:
    proof['result'] = 'FAIL'
    proof['failures'].append({'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()})
finally:
    proof['finishedUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT / 'independent-proof-r2.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'result': proof.get('result'), 'failures': proof['failures'], 'checks': list(proof['checks'])}, ensure_ascii=False))
sys.exit(0 if proof.get('result', '').startswith('PASS') else 1)
