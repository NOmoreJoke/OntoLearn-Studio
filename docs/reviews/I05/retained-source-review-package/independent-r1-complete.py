"""Continue packet checks after the preserved exact-path failure; no tar reread."""
import base64
import collections
import gzip
import hashlib
import json
import pathlib
import subprocess

TREE = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package')
PREFIX = 'docs/reviews/I05/retained-source-review-package/'
ROOT = TREE / PREFIX
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
PROCESS = '2dd91056000c3ff7a6d102eff4a168ec5419bd1b'
FIRST = ROOT / 'independent-r1-first-structure.json'
if not FIRST.exists():
    FIRST.write_bytes((ROOT / 'independent-proof-r1.json').read_bytes())
proof = json.loads(FIRST.read_bytes())
assert proof['failure']['type'] == 'AssertionError'
assert 'line 223' in proof['failure']['traceback']
proof['firstFailurePreserved'] = {'path': FIRST.name, 'bytes': FIRST.stat().st_size, 'sha256': hashlib.sha256(FIRST.read_bytes()).hexdigest(), 'actualExitCode': 1, 'reason': 'Both prompts name an absent M0 architecture path; fixed originals exist at two other paths. Earlier archive/Git/diff/coverage checks completed before this assertion.'}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def run(argv, expected=0):
    cp = subprocess.run(argv, cwd=TREE, capture_output=True)
    proof['commands'].append({'argv': argv, 'cwd': str(TREE), 'exitCode': cp.returncode, 'stdoutBase64': base64.b64encode(cp.stdout).decode(), 'stderrBase64': base64.b64encode(cp.stderr).decode(), 'stdoutBytes': len(cp.stdout), 'stderrBytes': len(cp.stderr)})
    assert cp.returncode == expected
    return cp.stdout

def read(name):
    return json.loads((ROOT / name).read_bytes())

m = read('input-manifest.json')
rows = m['members']
by_label = collections.defaultdict(dict)
for r in rows:
    label = r['member'].split('/', 2)[1]
    by_label[label][r['sourcePath']] = r
main = by_label['main-source-only']
wrong = 'docs/architecture/m0-review-and-update-plan-2026-10-19.md'
assert wrong not in main
alternates = ['docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md', 'docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md']
assert all(p in main for p in alternates)
assert main[alternates[0]]['gitBlob'] == main[alternates[1]]['gitBlob']
required = ['docs/prd/PRD-本体学习与落地Agent工作台.md', *alternates, 'docs/architecture/0001-desktop-framework.md', 'docs/iterations/I01/ADR-0002-storage.md', 'docs/m0-checklist.md']
assert all(p in main for p in required)
req_metadata = []
for p in required:
    r = main[p]
    value = run(['git', 'cat-file', 'blob', r['gitBlob']])
    assert len(value) == r['bytes'] and sha(value) == r['sha256']
    req_metadata.append({k: r[k] for k in ('sourceRef', 'sourcePath', 'gitBlob', 'bytes', 'sha256')})
proof['checks']['requirementsMapping'] = {'wrongPromptPath': wrong, 'absent': True, 'alternatesSameBytes': True, 'fixedOriginals': req_metadata}
prompt_checks = {}
for name in ['zcode-glm53-input.md', 'minimax-m31flash-input.md']:
    text = (ROOT / name).read_text()
    assert wrong in text
    tokens = ['57P0', 'S1/S2/S3/C1/B1/U1', '附录C–G', '第10–12节', '70', '22', '完整417', 'NotPass', 'HOLD', 'whole-H', '两OS', 'CI']
    prompt_checks[name] = {'bytes': len(text.encode()), 'sha256': sha(text.encode()), 'wrongPathLine': next(i for i, line in enumerate(text.splitlines(), 1) if wrong in line), 'majorAcceptanceTokens': {t: t in text for t in tokens}, 'onlyOwnReportRequired': '不读另一方报告/任务' in text}
proof['checks']['prompts'] = prompt_checks
launch = [p for p in by_label['reference-C4'] if p.startswith('docs/reviews/I05/inputs-c1/')]
assert launch
wrong_round = 'docs/reviews/I05/round-4/full-review-input.md'
assert all(wrong_round not in cohort for cohort in by_label.values())
actual_rounds = [p for p in by_label['reference-C4'] if p.endswith('/full-review-input.md') and p.startswith('docs/reviews/I05/')]
assert len(actual_rounds) == 3
proof['checks']['historicalPromptMapping'] = {'wrongRound4PathAbsentInAll16': wrong_round, 'actualC4ReviewInputPaths': actual_rounds, 'launchResumeGoalInputs': launch}
license_paths = [p for p in by_label['reference-C4'] if p.startswith('packages/engine/licenses/') and p not in main]
assert len(license_paths) == 53
cv = read('coverage-matrix.json')
miss = [r for r in cv['rows'] if r['kind'] == 'test' and r['variants']['T'] and r['variants']['T']['status'] == 'missing']
i05 = [r['path'] for r in miss if 'semantic' in r['path'] or 'quality' in r['path']]
t01 = [r['path'] for r in miss if r['path'] not in i05]
assert len(i05) == 24 and len(t01) == 23
missing_source = [r['path'] for r in cv['rows'] if r['kind'] == 'product' and r['variants']['T'] and r['variants']['T']['status'] == 'missing']
changed_source = [r['path'] for r in cv['rows'] if r['kind'] == 'product' and r['variants']['T'] and r['variants']['T']['status'] == 'changed']
fixtures = [r['path'] for r in cv['rows'] if r['kind'] == 'fixture' and r['variants']['T'] and r['variants']['T']['status'] == 'missing']
assert len(missing_source) == 13 and len(changed_source) == 11 and len(fixtures) == 27
same_delta22 = {r['path'] for r in cv['rows'] if r['kind'] == 'product' and r['variants']['T'] and r['variants']['T']['status'] == 'same'}
supplier22 = {r['path'] for r in cv['supplier22']}
assert len(same_delta22) == 22 and len(supplier22) == 22 and same_delta22 != supplier22
proof['checks']['exactRetainedScopes'] = {'C1Inputs': launch, 'C4License53': license_paths, 'missingTTests24I05Quality': i05, 'missingTTests23T01': t01, 'missingTSource13': missing_source, 'changedTSource11': changed_source, 'missingFixtures27': fixtures, 'sameDeltaOnly': sorted(same_delta22 - supplier22), 'supplierOnly': sorted(supplier22 - same_delta22)}
# Independently ensure every non-document phase delta belongs to the declared row set.
listed = {r['path'] for r in cv['rows']}
phase_deltas = {}
for phase, ref in cv['phaseRefs'].items():
    if phase in ('M', 'B'):
        continue
    delta = run(['git', 'diff', '--name-only', '-z', BASE, ref]).decode().split('\0')
    remaining = {p for p in delta if p and p != 'AGENTS.md' and not p.startswith(('docs/', 'design/', 'packages/engine/licenses/'))}
    phase_rows = {r['path'] for r in cv['rows'] if r['variants'][phase] is not None}
    assert remaining == phase_rows, (phase, sorted(remaining - phase_rows), sorted(phase_rows - remaining))
    phase_deltas[phase] = len(remaining)
proof['checks']['coverageNoUnlistedPhaseDelta'] = phase_deltas
queue = read('retained-branch-queue.json')
assert len(queue['additionalRetainedBranches']) == 8
queue_rows = []
for row in queue['additionalRetainedBranches']:
    fp = ROOT / row['sourceDiff']['path']
    value = fp.read_bytes(); carrier = json.loads(value)
    decoded = base64.b64decode(carrier['data'], validate=True)
    assert len(decoded) == row['sourceDiff']['bytes'] and sha(decoded) == row['sourceDiff']['sha256']
    assert carrier['head'] == row['head'] and carrier['base'] == BASE
    assert any(r['sha256'] == carrier['sha256'] and r['exactGit'] for r in proof['checks']['losslessDiffCarriers'])
    queue_rows.append({'tree': row['tree'], 'head': row['head'], 'exactDecodedDiff': row['sourceDiff'], 'carrierBytes': len(value), 'carrierSHA256': sha(value), 'next': row['next']})
proof['checks']['retainedQueue'] = {'count': 8, 'allExactDiffBound': True, 'rows': queue_rows, 'noReviewedOrWithdrawnClaim': True}
dispatch = read('dispatch-requirements.json')
assert dispatch['actualTaskCount'] == 0 and dispatch['actualTasks'] == [] and dispatch['actualReports'] == []
assert dispatch['packetCandidateSHA'] is None
proof['checks']['dispatch'] = {'actualDesignatedTasks': 0, 'packetSHAInjectionRequiredBeforeDispatch': True, 'noDesignatedPassImplied': True}
run(['git', 'diff', '--check', BASE, PROCESS, '--', PREFIX], expected=2)
run(['git', 'diff', '--check', BASE, PROCESS, '--', PREFIX, ':(exclude)' + PREFIX + 'author-build.py', ':(exclude)' + PREFIX + 'author-finish-first.py'])
proof['checks']['whitespace'] = {'fullBaseDiffExit': 2, 'exactTwoOriginalHelperExclusionsExit': 0}
# Read and verify lossless archived author streams without rerunning their commands.
stream_checks = []
for logname in ['author-command-log.json', 'author-finish-command-log.json', 'author-finish-v2-command-log.json', 'author-freeze-command-log.json', 'text-correction-command-log.json', 'final-git-audit-command-log.json']:
    log = read(logname)
    for index, rec in enumerate(log.get('records', [])):
        desc = rec.get('stdout')
        if isinstance(desc, dict) and 'losslessGzipPath' in desc:
            h = hashlib.sha256(); size = 0
            with gzip.open(ROOT / desc['losslessGzipPath'], 'rb') as f:
                while block := f.read(1024 * 1024):
                    h.update(block); size += len(block)
            assert size == desc['uncompressedBytes'] and h.hexdigest() == desc['sha256']
        elif 'stdoutBase64' in rec:
            output = base64.b64decode(rec['stdoutBase64'], validate=True)
            if 'stdoutBytes' in rec:
                assert len(output) == rec['stdoutBytes']
        stderr = rec.get('stderr')
        if isinstance(stderr, dict) and 'base64' in stderr:
            error = base64.b64decode(stderr['base64'], validate=True)
            assert len(error) == stderr['bytes'] and sha(error) == stderr['sha256']
        elif 'stderrBase64' in rec:
            base64.b64decode(rec['stderrBase64'], validate=True)
        stream_checks.append({'log': logname, 'recordIndex': index, 'exitCode': rec.get('exitCode'), 'streamCarrierVerified': True})
proof['checks']['historicalStreamChecks'] = stream_checks
proof['checks']['historyBoundaries'] = {'firstReadbackInterruption130': read('author-first-readback-interruption.json')['authorReadbackInterruption']['exitCode'], 'firstTextNamePathFailure1': read('author-finish-first-failure.json')['exitCode'], 'earlyFormatterExit0NotCoverage': True, 'laterExplicitIgnore9AuthorPathsExit0': read('text-correction-proof.json')['formatCheck']['exitCode'], 'noHistoricalScriptsExecuted': True, 'earlierCandidateCompleteNotAuthoritative': read('final-input-audit.json')['earlierPreparationManifestBoundary']}
proof['structureResult'] = 'PASS: archive/Git/diff/coverage; exact prompt path finding remains'
proof['packetReviewResult'] = 'FAIL pending P2 exact original-path mapping and concrete independent dispatch isolation; no product or designated-review conclusion'
proof['findings'] = [{'id': 'PKT-R1-P2-01', 'severity': 'P2', 'files': ['zcode-glm53-input.md:20', 'zcode-glm53-input.md:21', 'minimax-m31flash-input.md:20', 'minimax-m31flash-input.md:21'], 'trigger': wrong + ' absent in main2cf; ' + wrong_round + ' absent across all16 snapshots', 'impact': 'Mandatory M0 and historical original reading instructions resolve to absent files. Real originals are present at different exact paths but prompts do not map them.', 'remedy': 'Before dispatch, provide a fixed root addendum mapping exact archived originals with ref/path/bytes/SHA, or create a new packet prompt candidate. Do not alter historical source archives.'}]
proof['findings'].append({'id': 'PKT-R1-P2-02', 'severity': 'P2', 'files': ['dispatch-requirements.json', 'zcode-glm53-input.md', 'minimax-m31flash-input.md'], 'trigger': 'Both planned tasks select the same worktree and reports parent; no task-specific immutable-copy identity or automatic-status read allowlist/disposition is specified.', 'impact': 'Textual no-peer-reading rule exists but actual independent dispatch and task-generated status isolation cannot yet be checked. This packet has zero real tasks; no leakage in this packet is asserted.', 'remedy': 'Before dispatch, root should bind two separate exact-input copies and each task own output/status namespace, allowlist shared immutable inputs, forbid discovery of peer task/state/auto metadata, and require stop/report on unexpected cross-task access.'})
proof['queueDescriptorBoundary'] = 'retained-branch-queue.sourceDiff bytes/SHA bind the decoded raw diff inside the JSON carrier. Candidate Git manifest separately binds carrier bytes/SHA. Earlier continuation assertion treated them as carrier metadata; that was a checker interpretation error, not corrupt source diff.'
proof['continuationFailureReceipts'] = ['independent-r1-continuation-failure.json', 'independent-r1-queue-descriptor-interpretation.json']
proof['finalStatus'] = run(['git', 'status', '--porcelain=v1']).decode()
proof['checks']['indexEmpty'] = run(['git', 'diff', '--cached', '--name-only', '-z']) == b''
(ROOT / 'independent-proof-r1.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'result': proof['packetReviewResult'], 'shape143AllCarried': proof['checks']['shapeFinalProcess']['allCarried'], 'requirements': req_metadata, 'checks': list(proof['checks'])}, ensure_ascii=False))
