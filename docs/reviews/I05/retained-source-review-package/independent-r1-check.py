"""Independent packet-only checks. stdlib and read-only Git; never import product."""
import base64
import collections
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
import tarfile
import traceback

TREE = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package')
PREFIX = 'docs/reviews/I05/retained-source-review-package/'
ROOT = TREE / PREFIX
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
PACKET = '4de58348f25dc28e2dd18ef928101f2b7293355f'
PROCESS = '2dd91056000c3ff7a6d102eff4a168ec5419bd1b'
proof = {'format': 'independent-packet-review-r1/1', 'startedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checkerArgv': sys.argv, 'cwd': str(TREE), 'commands': [], 'checks': {}, 'failure': None, 'scope': 'Packet structure and read-only fixed Git. No product import/execution, tests, models, GUI/native, DB, network or installation.'}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def read(name):
    return json.loads((ROOT / name).read_bytes())

def command(args, stdin=None, reference=None, expected=0):
    cp = subprocess.run(args, cwd=TREE, input=stdin, capture_output=True)
    r = {'argv': args, 'cwd': str(TREE), 'exitCode': cp.returncode, 'stdoutBytes': len(cp.stdout), 'stdoutSHA256': sha(cp.stdout), 'stderrBase64': base64.b64encode(cp.stderr).decode(), 'stderrBytes': len(cp.stderr)}
    if stdin is not None:
        r['stdinBase64'] = base64.b64encode(stdin).decode()
    if reference is None:
        r['stdoutBase64'] = base64.b64encode(cp.stdout).decode()
    else:
        r['stdoutLosslessReference'] = reference
    proof['commands'].append(r)
    assert cp.returncode == expected, r
    return cp.stdout

trees = {}
def tree(ref):
    if ref not in trees:
        raw = command(['git', 'ls-tree', '-r', '-z', '-l', '--full-tree', ref])
        out = {}
        for item in raw.split(b'\0'):
            if not item:
                continue
            meta, path = item.split(b'\t', 1)
            mode, kind, oid, size = meta.decode('ascii').split()
            assert kind == 'blob' and mode in ('100644', '100755')
            path = path.decode('utf-8')
            assert path not in out
            out[path] = {'mode': mode, 'oid': oid, 'bytes': int(size)}
        trees[ref] = out
    return trees[ref]

def safe(path):
    pp = pathlib.PurePosixPath(path)
    return not pp.is_absolute() and '\\' not in path and path == pp.as_posix() and all(x not in ('', '.', '..') for x in path.split('/'))

def main():
    assert command(['git', 'rev-parse', 'HEAD']).decode().strip() == PROCESS
    assert command(['git', 'branch', '--show-current']).decode().strip() == 'docs/I05-retained-source-review-package'
    proof['initialStatus'] = command(['git', 'status', '--porcelain=v1']).decode()
    assert command(['git', 'diff', '--cached', '--name-only', '-z']) == b''
    m = read('input-manifest.json')
    cv = read('coverage-matrix.json')
    candidates = read('candidate-git-manifest.json')
    expected = {r['member']: r for r in m['members']}
    assert len(expected) == len(m['members']) == 22492
    cohorts = {c['label']: c for c in m['cohorts']}
    assert len(cohorts) == 16
    by_label = collections.defaultdict(dict)
    identities = {}
    by_oid = {}
    all_names = set()
    regular = links = 0
    # Hash compressed carrier separately, then one sequential tar decompression only.
    h = hashlib.sha256()
    with (ROOT / m['bundle']['path']).open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    assert (ROOT / m['bundle']['path']).stat().st_size == m['bundle']['bytes']
    assert h.hexdigest() == m['bundle']['sha256']
    with tarfile.open(ROOT / m['bundle']['path'], mode='r|gz') as archive:
        for info in archive:
            name = info.name
            assert safe(name) and name not in all_names and name in expected
            all_names.add(name)
            row = expected[name]
            prefix, label, sourcepath = name.split('/', 2)
            assert prefix == 'snapshots' and label in cohorts
            assert row['sourcePath'] == sourcepath and safe(sourcepath)
            assert row['sourceRef'] == cohorts[label]['ref']
            original = tree(row['sourceRef'])[sourcepath]
            assert original == {'mode': row['mode'], 'oid': row['gitBlob'], 'bytes': row['bytes']}
            assert info.mode == (int(row['mode'], 8) & 0o777)
            if info.isreg():
                assert row['hardlinkTarget'] is None and info.size == row['bytes']
                value = archive.extractfile(info).read()
                identity = {'bytes': len(value), 'sha256': sha(value), 'gitBlob': hashlib.sha1(b'blob ' + str(len(value)).encode() + b'\0' + value).hexdigest()}
                regular += 1
            else:
                assert info.islnk() and safe(info.linkname) and info.linkname in identities
                assert info.linkname == row['hardlinkTarget'] and info.size == 0
                identity = identities[info.linkname]
                links += 1
            assert identity == {k: row[k] for k in ('bytes', 'sha256', 'gitBlob')}
            identities[name] = identity
            by_oid[row['gitBlob']] = identity
            by_label[label][sourcepath] = original
    assert all_names == set(expected)
    for label, cohort in cohorts.items():
        actual = by_label[label]
        full = tree(cohort['ref'])
        if label == 'main-completion-process':
            main_tree = tree(m['candidate'])
            full = {p: r for p, r in full.items() if main_tree.get(p) != r}
            assert len(full) == 6 and all(p.startswith('docs/') for p in full)
        assert actual == full and len(actual) == cohort['members']
    assert regular == len(by_oid) == m['uniqueGitBlobs'] == 3006 and links == 19486
    proof['checks']['archive'] = {'members': len(all_names), 'regular': regular, 'backwardHardlinks': links, 'safeUniqueMemberPaths': True, 'allRefsModesBytesSHA256GitBlobVerified': True, 'all16ExactPathsets': True, 'sha256': h.hexdigest()}
    # Read all independent Git blob bytes in one batch. Preserve exact fixed object
    # identities rather than duplicate all source in a second large proof carrier.
    packet_rows = {p: r for p, r in tree(PROCESS).items() if p.startswith(PREFIX)}
    packet_candidates = {p: r for p, r in tree(PACKET).items() if p.startswith(PREFIX)}
    assert len(packet_candidates) == 119 and len(packet_rows) == 124
    assert set(packet_candidates) == {r['path'] for r in candidates['files']}
    blob_oids = sorted(set(by_oid) | {r['oid'] for r in packet_rows.values()} | set(cv['blobSHA256']))
    common_dir = command(['git', 'rev-parse', '--git-common-dir']).decode().strip()
    batch = command(['git', 'cat-file', '--batch'], ''.join(oid + '\n' for oid in blob_oids).encode(), {'kind': 'immutable-git-objects', 'gitCommonDirectory': str((TREE / common_dir).resolve()), 'orderedOids': blob_oids, 'encoding': 'git cat-file --batch canonical header, exact object bytes, LF; complete bytes reconstructable from fixed local Git; no product source copied to stdout'})
    pos = 0
    got = {}
    for oid in blob_oids:
        end = batch.index(b'\n', pos)
        header = batch[pos:end].decode().split()
        assert header[:2] == [oid, 'blob']
        n = int(header[2]); pos = end + 1
        value = batch[pos:pos+n]; pos += n
        assert batch[pos:pos+1] == b'\n'; pos += 1
        got[oid] = {'bytes': n, 'sha256': sha(value), 'gitBlob': oid}
    assert pos == len(batch)
    del batch
    assert all(got[oid] == value for oid, value in by_oid.items())
    assert all(got[oid]['sha256'] == digest for oid, digest in cv['blobSHA256'].items())
    proof['checks']['allUniqueGitPayloads'] = {'objects': len(blob_oids), 'archiveUnique': len(by_oid), 'coverageUnique': len(cv['blobSHA256']), 'allExact': True}
    for row in candidates['files']:
        assert packet_candidates[row['path']] == {'mode': row['mode'], 'oid': row['gitBlob'], 'bytes': row['bytes']}
        assert got[row['gitBlob']]['sha256'] == row['sha256']
    for path, row in packet_rows.items():
        value = (TREE / path).read_bytes()
        assert len(value) == row['bytes'] and sha(value) == got[row['oid']]['sha256']
    additions = set(packet_rows) - set(packet_candidates)
    assert all(packet_rows[p] == packet_candidates[p] for p in packet_candidates)
    proof['checks']['packetBinding'] = {'candidate': PACKET, 'process': PROCESS, 'candidateFiles': 119, 'candidateBytes': sum(r['bytes'] for r in packet_candidates.values()), 'processFiles': 124, 'candidateCurrentEqualsGitAndManifest': True, 'onlyProcessAdded': sorted(additions)}
    # Exact lossless diff carriers: one main full binary diff and 16 scoped diffs.
    diffs = [ROOT / 'candidate.patch.json', *sorted((ROOT / 'reference-diffs').glob('*.json'))]
    diff_results = []
    for path in diffs:
        item = json.loads(path.read_bytes())
        value = base64.b64decode(item['data'], validate=True)
        assert len(value) == item['bytes'] and sha(value) == item['sha256']
        argv = item['argv']
        assert argv[:5] == ['git', 'diff', '--binary', '--full-index', BASE]
        assert len(argv[5]) == 40 and all(c in '0123456789abcdef' for c in argv[5])
        assert len(argv) == 6 or argv[6:] == ['--', 'apps', 'packages', 'scripts', 'tests', '.github', 'uv.lock', 'package.json', 'package-lock.json']
        actual = command(argv, reference={'file': path.relative_to(TREE).as_posix(), 'encoding': 'base64', 'key': 'data', 'bytes': len(value), 'sha256': sha(value)})
        assert actual == value
        diff_results.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': len(value), 'sha256': sha(value), 'exactGit': True})
    proof['checks']['losslessDiffCarriers'] = diff_results
    # Matrix: independently derive phase membership from full Git tree metadata.
    stats = {}
    main_tree = tree(m['candidate']); base_tree = tree(BASE)
    phases = {k: tree(v) for k, v in cv['phaseRefs'].items()}
    for row in cv['rows']:
        p = row['path']; target = main_tree.get(p)
        if row['M'] is None:
            assert target is None
        else:
            assert target['oid'] == row['M']['oid'] and target['bytes'] == row['M']['bytes']
        for label, variant in row['variants'].items():
            actual = phases[label].get(p)
            changed_from_base = actual != base_tree.get(p)
            if variant is None:
                assert not changed_from_base
                continue
            assert changed_from_base and actual is not None
            assert actual['oid'] == variant['oid'] and actual['bytes'] == variant['bytes']
            status = 'missing' if target is None else 'same' if actual['oid'] == target['oid'] else 'changed'
            assert variant['status'] == status
            stats.setdefault(label, {}).setdefault(row['kind'], collections.Counter())[status] += 1
    assert len(cv['rows']) == 148 and len(cv['blobSHA256']) == 211
    for row in cv['supplier22']:
        assert main_tree[row['path']]['oid'] == row['oid'] == phases['T'][row['path']]['oid']
        assert got[row['oid']]['sha256'] == row['sha256'] and got[row['oid']]['bytes'] == row['bytes']
    assert len(cv['supplier22']) == 22
    for row in cv['newMainOnlyScope']:
        assert main_tree[row['path']]['oid'] == row['oid']
        assert got[row['oid']]['sha256'] == row['sha256']
    missingT = [r['path'] for r in cv['rows'] if r['kind'] == 'test' and r['variants']['T'] and r['variants']['T']['status'] == 'missing']
    proof['checks']['coverage'] = {'rows': 148, 'uniqueCoverageBlobs': 211, 'stats': stats, 'supplier22': True, 'missingTTests': missingT, 'missingTI05Quality': [p for p in missingT if 'semantic' in p or 'quality' in p], 'opaqueWipCount': len(cv['untrackedOpaqueOnly']), 'opaqueNotReadFromWip': True}
    # Bind copied guidance and current external identities, without reading any WIP.
    guidance = read('guidance-manifest.json')
    for name, row in guidance.items():
        b = (ROOT / 'guidance' / name).read_bytes()
        assert len(b) == row['bytes'] and sha(b) == row['sha256']
        actual = pathlib.Path(row['sourcePath']).read_bytes()
        assert b == actual
    assert (TREE / 'AGENTS.md').read_bytes() == (ROOT / 'guidance/AGENTS-current.md').read_bytes()
    proof['checks']['guidance'] = {'all12CopiesCurrentAndExact': True, 'treeProtectedAGENTSMatches': True}
    # Determine whether named shape final-process objects are actually carried.
    closure_ref = 'a15f1478e398fb3b58fd60b1421a9cad04fdb430'
    old = tree(cv['phaseRefs']['S']); final = tree(closure_ref)
    delta = {p: r for p, r in final.items() if old.get(p) != r}
    reverse = collections.defaultdict(list)
    for label, rows in by_label.items():
        for p, r in rows.items():
            reverse[(p, r['oid'])].append(label)
    carried = {p: reverse[(p, r['oid'])] for p, r in delta.items()}
    proof['checks']['shapeFinalProcess'] = {'ref': closure_ref, 'deltaCount': len(delta), 'allCarried': all(carried.values()), 'carriers': carried, 'missing': [p for p, v in carried.items() if not v]}
    # Original requirements and failures are fixed originals, not title-only refs.
    required = ['docs/prd/PRD-本体学习与落地Agent工作台.md', 'docs/architecture/m0-review-and-update-plan-2026-10-19.md', 'docs/architecture/0001-desktop-framework.md', 'docs/iterations/I01/ADR-0002-storage.md', 'docs/m0-checklist.md']
    assert all(p in by_label['main-source-only'] for p in required)
    launch = [p for p in by_label['reference-C4'] if p.startswith('docs/reviews/I05/inputs-c1/')]
    assert launch and 'docs/reviews/I05/round-4/full-review-input.md' in by_label['reference-C4']
    licenses = [p for p in by_label['reference-C4'] if p.startswith('licenses/') and p not in main_tree]
    proof['checks']['requiredOriginals'] = {'mainRequirements': required, 'C1InputMembers': launch, 'C4AbsentMainLicensePaths': licenses, 'sourceOnlyRecords': [p for p in main_tree if p.startswith('docs/reviews/I05/source-package-probe-source/')]}
    dispatch = read('dispatch-requirements.json')
    assert dispatch['actualTaskCount'] == 0 and dispatch['actualTasks'] == [] and dispatch['actualReports'] == []
    assert dispatch['packetCandidateSHA'] is None
    proof['checks']['dispatch'] = {'actualDesignatedTasks': 0, 'packetSHAInjectionRequiredBeforeDispatch': True, 'noDesignatedPassImplied': True}
    # Whitespace original exceptions remain immutable and explicit.
    command(['git', 'diff', '--check', BASE, PROCESS, '--', PREFIX], expected=2)
    command(['git', 'diff', '--check', BASE, PROCESS, '--', PREFIX, ':(exclude)' + PREFIX + 'author-build.py', ':(exclude)' + PREFIX + 'author-finish-first.py'])
    proof['checks']['whitespace'] = {'fullBaseDiffExit': 2, 'exactTwoOriginalHelperExclusionsExit': 0}
    proof['finalStatus'] = command(['git', 'status', '--porcelain=v1']).decode()
    proof['checks']['indexEmpty'] = command(['git', 'diff', '--cached', '--name-only', '-z']) == b''
    proof['structureResult'] = 'PASS'

try:
    main()
except BaseException as exc:
    proof['failure'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    proof['structureResult'] = 'FAIL'
finally:
    proof['finishedUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT / 'independent-proof-r1.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'structureResult': proof.get('structureResult'), 'failure': proof['failure'], 'checks': list(proof['checks'])}, ensure_ascii=False))
sys.exit(0 if proof.get('structureResult') == 'PASS' else 1)
