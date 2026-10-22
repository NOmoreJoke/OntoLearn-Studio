# -*- coding: utf-8 -*-
"""Static R3 preparation: Git/file materialization only; no dependency/product execution."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import tarfile

PREP = Path(__file__).resolve().parent
OWNER = PREP.parents[3]
P = 'f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3'
B = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
R = '7fd17f93ebb4b68bac69faec15cb657e60c90729'
POLICY = (OWNER / 'AGENTS.md').read_bytes()
sha = lambda b: hashlib.sha256(b).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=OWNER)


def unpack_regular(archive, target):
    target.mkdir(parents=True, exist_ok=True)
    records = []
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            name = Path(member.name)
            assert not name.is_absolute() and '..' not in name.parts, member.name
            if member.isdir():
                continue
            assert member.isfile(), member.name
            raw = tar.extractfile(member).read()
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            assert not dest.exists(), str(dest)
            dest.write_bytes(raw)
            dest.chmod(member.mode & 0o777)
            records.append({'path': member.name, 'bytes': len(raw), 'sha256': sha(raw)})
    return records


assert git('diff', '--name-only', P + '..' + R, '--', 'apps', 'packages', 'tests',
           'package.json', 'package-lock.json', 'pyproject.toml', 'uv.lock') == b''
assert sha(POLICY) == 'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'
snapshot = git('archive', '--format=tar', R)
frozen = json.loads((OWNER / 'docs/reviews/T07/round-1/frozen-manifest.json').read_text())
seven_path = 'docs/reviews/T07/launch-20261023/native-receiving-20261023/seven-opinion-dispositions.json'
r1_audit_path = 'docs/reviews/T07/launch-20261023/native-receiving-20261023/independent-native-receiving-audit.md'
r2 = 'docs/reviews/T07/round-2-native-receiving-20261023/'
static = 'docs/reviews/T07/round-2-static-disposition-20261023/'
inline_paths = [
    ('R2 ZCode completed 作者完整报告（NotPass 原文）', r2 + 'reviewer-reports/zcode-glm53.md'),
    ('R2 MiniMax completed 作者完整报告（原 PASS/P2/P3 不改）', r2 + 'reviewer-reports/minimax-m31flash.md'),
    ('R2 非作者最终原生接收独审（缺口/越写/映射逐项）', r2 + 'independent-final-audit.md'),
    ('R2 owner 完整接收回执及不放行边界', r2 + 'receiving-receipt.md'),
    ('R2 原 M 新工程 P2/P3 未决处置', r2 + 'new-opinion-dispositions.json'),
    ('R2 新工程意见的既有静态复核边界', r2 + 'engineering-opinion-audit.md'),
    ('根已接收的静态处置旁注（保完整 Definition 守卫）', static + 'static-disposition.md'),
    ('006/007/008 原输出与比较范围逐项对照', static + 'probe-output-comparison.json'),
    ('静态旁注的固定来源索引', static + 'evidence-manifest.json'),
    ('R2 M 越界写/清理/全局列举的脱敏证据', r2 + 'minimax-scope-violation.json'),
    ('R2 Z 写面和日志读取声明缺口索引', r2 + 'zcode-scope-and-reading-findings.json'),
    ('R2 首收当时的 pending/取证缺口记录', r2 + 'first-receive.md'),
    ('R2 仅一条全局列表导出脱敏声明', r2 + 'export-redactions.json'),
]
rows = []
all_manifests = []
for role in ('zcode', 'minimax'):
    root = OWNER.parent / f'T07-{role}-review-r3-f9a1157'
    runtime = Path(str(root) + '.runtime')
    assert root.exists() and not runtime.exists()
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip() == R
    for folder in ('metadata', 'history', 'raw/setup', 'raw/validation', 'reports', 'tmp',
                   'uv-cache', 'npm-cache', 'ruff-cache', 'pytest', 'scratch'):
        (runtime / folder).mkdir(parents=True, exist_ok=True)
    (runtime / 'metadata/source-snapshot.tar').write_bytes(snapshot)
    scratch = runtime / 'scratch/probe-copy'
    source_members = unpack_regular(runtime / 'metadata/source-snapshot.tar', scratch)
    (root / 'AGENTS.md').write_bytes(POLICY)
    (scratch / 'AGENTS.md').write_bytes(POLICY)
    for env_root in (root, scratch):
        for name in ('node_modules', '.venv'):
            assert not (env_root / name).exists() and not (env_root / name).is_symlink()
    r1_members = unpack_regular(root / 'docs/reviews/T07/round-1/frozen-inputs.tar.gz',
                                runtime / 'history/frozen-inputs')
    assert len(r1_members) == 75
    r2_archive = root / 'docs/reviews/T07/round-2-native-receiving-20261023.tar.gz'
    assert sha(r2_archive.read_bytes()) == '6d95d96c8bea923b5f31477b6774d686932389a1c37960602cea2e7eb88cf070'
    r2_history = runtime / 'history/prior-r2-public-evidence'
    r2_members = unpack_regular(r2_archive, r2_history)
    assert len(r2_members) == 72
    export_index = json.loads((r2_history / 'export-index.json').read_text())
    for entry in export_index['files']:
        actual = (r2_history / entry['path']).read_bytes()
        assert len(actual) == entry['bytes'] and sha(actual) == entry['sha256']
    assert len(export_index['files']) == 71
    for candidate in frozen['candidateFiles']:
        raw = git('show', P + ':' + candidate['path'])
        assert sha(raw) == candidate['sha256']
        dest = runtime / 'history/product-candidate' / candidate['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    prd = runtime / 'history/approved-prd-v0.6.md'
    prd.write_bytes(git('show', B + ':docs/prd/PRD-本体学习与落地Agent工作台.md'))

    dest = root / 'docs/reviews/T07/round-3-input'
    dest.mkdir(exist_ok=False)
    inventory_entries = []
    for entry in source_members:
        relative = entry['path']
        a = (root / relative).read_bytes()
        b = (scratch / relative).read_bytes()
        exception = relative == 'AGENTS.md'
        assert a == b and (sha(a) == entry['sha256'] or exception)
        if exception:
            assert a == POLICY
        inventory_entries.append({**entry, 'sourceRef': R, 'reviewBytes': len(a),
                                  'reviewSha256': sha(a), 'scratchSha256': sha(b),
                                  'matchesGit': sha(a) == entry['sha256'],
                                  'protectedPolicyException': exception})
    inventory = {'role': role, 'sourceReviewHead': R, 'trackedFiles': len(inventory_entries),
                 'exactGitFiles': sum(x['matchesGit'] for x in inventory_entries),
                 'policyOnlyException': [x['path'] for x in inventory_entries if not x['matchesGit']],
                 'reviewRoot': str(root), 'scratchSourceCopy': str(scratch),
                 'dependenciesInstalled': False, 'files': inventory_entries}
    dump(dest / 'full-git-files.json', inventory)
    dump(PREP / f'{role}-full-git-files.json', inventory)

    receipt = {'state': 'PREPARATION_ONLY_NOT_SUBMITTED', 'role': role,
               'expectedWorkspace': str(root), 'reviewHead': R, 'productHead': P,
               'requiredSettings': {'model': 'GLM-5.3' if role == 'zcode' else 'M3.1-Flash',
                                    'effort': '最高' if role == 'zcode' else 'xhigh',
                                    'permission': '完全访问' if role == 'zcode' else '始终授权'},
               'actualSettingsUI': None, 'actualSessionId': None, 'originalTurnId': None,
               'officialAttachment': None, 'officialTerminal': None, 'externalVerdict': None,
               'tasksCreated': 0, 'formalSends': 0, 'GUIReleased': True,
               'operatorOnly': True, 'modelMustNotDiscoverMissingIdentity': True}
    operator_receipt = runtime / 'metadata/operator-identity-receipt.json'
    dump(operator_receipt, receipt)
    dump(dest / 'operator-identity-receipt.template.json', receipt)
    caches = {key: str(value) for key, value in {
        'TMPDIR': runtime / 'tmp', 'UV_CACHE_DIR': runtime / 'uv-cache',
        'UV_PROJECT_ENVIRONMENT': root / '.venv', 'npm_config_cache': runtime / 'npm-cache',
        'RUFF_CACHE_DIR': runtime / 'ruff-cache', 'pytestBaseParent': runtime / 'pytest'}.items()}
    plan = {'state': 'PLAN_ONLY_NOT_EXECUTED', 'role': role, 'root': str(root),
            'runtime': str(runtime), 'scratchSourceCopy': str(scratch),
            'sourceFilesPrepared': True, 'nodeModulesPresent': False, 'venvPresent': False,
            'dependencyCommandsExecuted': 0, 'productCommandsExecuted': 0,
            'cachePaths': caches, 'allMutableCachesNewAndRoleExclusive': True,
            'clearOverridesBeforeAnyFutureAuthorizedSetup': [
                'ROOT_SOURCE_PATH', 'PYTHONPATH', 'ONTOLEARN_TEST_ENGINE', 'ONTOLEARN_DB_PATH'],
            'conditionalLockedInstallPlan': [
                {'argv': ['uv', 'sync', '--frozen', '--no-python-downloads'], 'executed': False},
                {'argv': ['npm', 'ci', '--ignore-scripts', '--no-audit', '--fund=false'], 'executed': False}],
            'planIsNotExecutionAuthorization': True,
            'initialReviewNeedsNoInstalledDependencies': 'Read-only source, contract and existing raw evidence first.',
            'oldEnvironmentsOrCachesReused': False, 'crossRoleMutableLinks': False,
            'oldRejectedValidationPurposesStillHeld': ['pytest T07', 'vitest T07', 'npm run check'],
            'noWrapperOrAlternateArgvPlanForRejectedPurposes': True}
    dump(dest / 'environment-setup-plan.json', plan)
    dump(PREP / f'{role}-environment-setup-plan.json', plan)
    (dest / 'current-AGENTS.md').write_bytes(POLICY)

    # Keep the original seven and each audit namespace intact; no guessed aggregate count.
    seven = json.loads((root / seven_path).read_text())
    r1_text = (root / r1_audit_path).read_text()
    nr = re.findall(r'(?m)^### (NR-0[1-5]) / (P2)：([^\n]+)', r1_text)
    assert len(seven['items']) == 7 and len(nr) == 5
    r2_text = (root / (r2 + 'independent-final-audit.md')).read_text()
    section = r2_text.split('## 实质发现\n', 1)[1].split('## 验证与边界', 1)[0]
    r2_findings = re.findall(r'(?ms)^([1-5])\. \*\*P2：(.+?)(?=^[1-5]\. \*\*P2|\Z)', section)
    assert len(r2_findings) == 5
    author_items = json.loads((root / (r2 + 'new-opinion-dispositions.json')).read_text())
    assert [x['authorPriority'] for x in author_items['items']] == ['P2', 'P3']
    z_calls = [json.loads(line) for line in (r2_history / 'final-zcode/tool-calls.jsonl').read_text().splitlines()]
    z_results = [json.loads(line) for line in (r2_history / 'final-zcode/tool-results.jsonl').read_text().splitlines()]
    rejected_id = 'call_67be7300c0dc4552845dc9c0'
    rejection = {'originalCall': next(x for x in z_calls if x['id'] == rejected_id),
                 'originalResults': [x for x in z_results if x['toolCallId'] == rejected_id],
                 'rootRelease': None, 'objectives': 'UNVERIFIED; no rerun or alternate route authorized',
                 'source': 'Already sealed R2 public evidence only; no native fallback.'}
    assert rejection['originalResults'][0]['isError'] is True
    rejected_path = runtime / 'history/prior-r2-rejection-call-and-result.json'
    dump(rejected_path, rejection)
    register = {'scope': 'Separate immutable histories and unresolved engineering observations; not a merged defect count',
                'originalSeven': seven, 'R1NativeFindings': [
                    {'originalId': i, 'priority': p, 'heading': h, 'state': 'R1 PROCESS_FAIL retained'}
                    for i, p, h in nr],
                'R2NativeFindings': [{'sourceNumber': n, 'priority': 'P2', 'exactOriginalParagraph': t.strip(),
                                      'state': 'R2 PROCESS_FAIL retained'} for n, t in r2_findings],
                'newAuthorEngineering': author_items,
                'operationalHold': {'originalCallId': rejected_id, 'priority': None,
                                    'rejectionNotLifted': True, 'state': 'UNVERIFIED'},
                'categoryCountsNotDistinctDefectTotal': {'originalSeven': len(seven['items']),
                    'R1NativeFindings': len(nr), 'R2NativeFindings': len(r2_findings),
                    'newAuthorEngineering': len(author_items['items']), 'operationalHold': 1},
                'noPriorityDowngradeOrDeferralAcceptance': True, 'rootDecision': None,
                'sourcePatchProposal': [], 'pairGateBeforeNewReview': 'PROCESS_FAIL / Pair 0'}
    dump(dest / 'issue-register.json', register)
    dump(PREP / f'{role}-issue-register.json', register)

    reading = []
    seen = set()

    def need(path, kind, ref=None, original_expected=None):
        path = Path(path)
        if str(path) in seen:
            return
        assert path.is_relative_to(root) or path.is_relative_to(runtime), str(path)
        raw = path.read_bytes()
        if original_expected:
            assert len(raw) == original_expected['bytes'] and sha(raw) == original_expected['sha256'], str(path)
        seen.add(str(path))
        reading.append({'path': str(path), 'kind': kind, 'sourceRef': ref,
                        'materializedAtReviewHead': R, 'bytes': len(raw), 'sha256': sha(raw),
                        'textNewlines': raw.count(b'\n') if path.suffix.lower() != '.png' else None,
                        'actualReadCompleted': False, 'requiredVisibleEOF': True})

    previous = json.loads((OWNER / f'docs/reviews/T07/round-2-preparation-20261023/{role}-required-reading.json').read_text())
    old_root = str(OWNER.parent / f'T07-{role}-review-r2-f9a1157')
    old_runtime = old_root + '.runtime'
    for entry in previous['items']:
        old = entry['path']
        if old.startswith(old_runtime + '/'):
            mapped = str(runtime) + old[len(old_runtime):]
        else:
            assert old.startswith(old_root + '/'), old
            mapped = str(root) + old[len(old_root):]
        need(mapped, entry['kind'], entry.get('sourceRef'), entry)
    assert len(reading) == previous['itemCount'] == 148
    for title, relative in inline_paths:
        need(root / relative, 'completed-R2-or-static-disposition-fulltext', R)
    for entry in r2_members:
        need(r2_history / entry['path'], 'complete-prior-R2-public-evidence', '92ebe268 sealed archive')
    need(rejected_path, 'prior-unlifted-rejection-original-call-result')
    for name in ('environment-setup-plan.json', 'issue-register.json'):
        need(dest / name, 'current-R3-plan-or-case-index')
    ledger = {'scope': 'Full engineering/source/contract/raw/fixture/history EOF, not delta; no pre-signed reading',
              'role': role, 'itemCount': len(reading), 'items': reading,
              'requiredImplementationEntries': len(frozen['implementationTestFixtureEntries']),
              'requiredCandidateEntries': len(frozen['candidateFiles']), 'requiredDiff': 'complete candidate.patch',
              'originalFrozenMembers': len(r1_members), 'originalLogPNGMembers': 35,
              'completedR2PublicMembers': len(r2_members), 'parentGapsRemainOpen': True}
    assert ledger['requiredImplementationEntries'] == 14 and ledger['requiredCandidateEntries'] == 25
    dump(dest / 'required-reading.json', ledger)
    dump(PREP / f'{role}-required-reading.json', ledger)

    report = root / f'docs/reviews/T07/round-3/{"zcode-glm53" if role == "zcode" else "minimax-m31flash"}.md'
    replacements = {'APP': 'ZCode' if role == 'zcode' else 'MiniMax Code', 'ROOT': str(root),
                    'RUNTIME': str(runtime), 'MODEL': receipt['requiredSettings']['model'],
                    'EFFORT': receipt['requiredSettings']['effort'],
                    'PERMISSION': receipt['requiredSettings']['permission'], 'REPORT': str(report)}
    prefix = (PREP / 'current-prefix-template.md').read_text()
    for key, value in replacements.items():
        prefix = prefix.replace('{{' + key + '}}', value)
    assert '{{' not in prefix
    parts = [prefix.encode()]
    inline_records = []
    extra_inline = [
        ('原 Z R2 自动拒绝原调用及结果（未解除）', rejected_path),
        ('原 Z R2 拒绝首错保全记录（作者原文）', r2_history / 'final-zcode/runtime-originals/r2-zcode-001/00-rejection-record.md'),
        ('采集端原首错及纠正/缺口（不补原模型证据）', r2_history / 'operator-first-errors.json'),
        ('本轮实际分类意见/事故索引（不猜数量）', dest / 'issue-register.json')]
    for title, path in [(t, root / r) for t, r in inline_paths] + extra_inline:
        raw = path.read_bytes()
        parts += [('\n\n## BEGIN COMPLETE HISTORICAL MATERIAL: ' + title + '\n'
                   'Current own readable copy: ' + str(path) + '\n'
                   'Bytes: ' + str(len(raw)) + '; SHA256: ' + sha(raw) + '\n\n').encode(),
                  raw, b'\n## END COMPLETE HISTORICAL MATERIAL\n']
        inline_records.append({'title': title, 'currentOwnPath': str(path), 'bytes': len(raw), 'sha256': sha(raw)})
    old_input_path = root / f'docs/reviews/T07/round-2-preparation-20261023/{role}-full-input.txt'
    old_input = old_input_path.read_bytes()
    expected_old = '513da17b6f17e8004244cbc72c8f98dbc55a837862bd9c4d6d5c5ae80814c87d' if role == 'zcode' else '525ac36e5e505c103760501ada799c4399b3780559891a3a1b6b28f8e2ed8ede'
    assert sha(old_input) == expected_old
    parts += [b'\n\n## BEGIN EXACT COMPLETE PREVIOUS R2 INPUT BYTES (HISTORY ONLY; CURRENT PREFIX GOVERNS)\n', old_input]
    full = b''.join(parts)
    (dest / 'full-input.txt').write_bytes(full)
    (PREP / f'{role}-full-input.txt').write_bytes(full)
    row = {'role': role, 'root': str(root), 'runtime': str(runtime), 'scratchSourceCopy': str(scratch),
           'base': B, 'productHead': P, 'reviewHead': R, 'report': str(report),
           'operatorReceipt': str(operator_receipt), 'requiredSettings': receipt['requiredSettings'],
           'fullInputPath': str(dest / 'full-input.txt'), 'fullInputBytes': len(full),
           'fullInputNewlines': full.count(b'\n'), 'fullInputSHA256': sha(full),
           'oldR2SuffixBytes': len(old_input), 'oldR2SuffixSHA256': sha(old_input),
           'oldR2SuffixExact': full.endswith(old_input), 'embeddedFullHistories': inline_records,
           'readingItems': len(reading), 'trackedFiles': len(source_members),
           'R1FrozenMembers': len(r1_members), 'R2PublicMembers': len(r2_members),
           'policySHA256': sha(POLICY), 'dependenciesInstalled': False,
           'environmentSetupExecuted': False, 'newExternalTasks': 0, 'GUIReleased': True,
           'actualSettingsUI': None, 'actualSessionId': None, 'originalTurnId': None,
           'officialTerminal': None, 'externalVerdict': None, 'productExecutedByPreparation': False}
    dump(dest / 'input-manifest.json', row)
    dump(PREP / f'{role}-input-manifest.json', row)
    launch = (f'T07-S1 R3 full independent engineering review; first inspect existing full original check/raw, no mechanical rerun. '
              f'Read the complete official full-input.txt attachment ({len(full)} bytes, {full.count(bytes([10]))} LF, SHA256 {sha(full)}) '
              f'and compare with {dest / "full-input.txt"}; continue actual truncated returns to EOF. '
              f'Unique workspace {root}; product {P}; reviewHead {R}. '
              f'Own identity receipt {operator_receipt}; missing identity remains UNKNOWN, no global/session discovery.\n'
              f'Complete 25-path diff/14 source-test-fixtures, full PRD/contracts, all original raw/history/finals and every issue namespace; not delta or digest-only. '
              f'Prior rejected pytest/vitest/check purposes remain unlifted: no rerun, wrappers, alternate argv, identities or paths. '
              f'All setup is plan-only and dependencies absent; do not execute setup/product/probe commands. '
              f'If critical existing evidence cannot be verified, state the precise gap; do not invent EOF or require fresh runs by default.\n'
              f'Write only {report} and explicit own runtime reviewer/evidence surfaces. '
              f'No /tmp/global assets/peer/controller discovery or placeholders; no source/config/test/digest changes. '
              f'Original seven observations, NR01-05, R2 scope/read incidents, compaction/30-character gaps, rejected first failure and original M P2/P3 remain distinct and unchanged; root decisions are pending.\n')
    (dest / 'short-launch.txt').write_text(launch)
    (PREP / f'{role}-short-launch.txt').write_text(launch)
    dump(dest / 'readiness-notice.json', {'state': 'PREPARATION_AUDIT_PENDING_NO_START',
         'role': role, 'preparedInputSHA256': sha(full), 'preparationAudit': None,
         'externalStartAuthorized': False, 'tasksCreated': 0, 'GUIReleased': True})
    rows.append({k: row[k] for k in ('role', 'root', 'runtime', 'scratchSourceCopy', 'reviewHead',
                                    'productHead', 'report', 'operatorReceipt')})
    all_manifests.append(row)

dump(PREP / 'roots.json', {'roots': rows, 'newExternalTasks': 0, 'oldRootsPreserved': True,
                         'GUIReleased': True, 'environmentSetupExecuted': False})
dump(PREP / 'dispatch-manifest.json', {'state': 'MATERIALS_FROZEN_AWAITING_ONE_NONAUTHOR_PREPARATION_AUDIT',
     'preparedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'base': B, 'productHead': P, 'reviewHead': R, 'roles': all_manifests,
     'newExternalTasks': 0, 'formalSends': 0, 'GUIUsed': False, 'GUIReleased': True,
     'productRuns': 0, 'environmentSetupExecuted': False, 'externalStartAuthorized': False,
     'oldRejectedValidationNotLifted': True, 'originalGoalUnchanged': True,
     'existingProcessFailsPreserved': True, 'validPassPairs': 0})
print(json.dumps([{'role': x['role'], 'bytes': x['fullInputBytes'], 'LF': x['fullInputNewlines'],
                   'sha256': x['fullInputSHA256'], 'requiredReading': x['readingItems'],
                   'trackedFiles': x['trackedFiles']} for x in all_manifests], ensure_ascii=False))
