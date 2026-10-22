"""Static role-only additive package materialization; no ordinary/setup/GUI."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
CONTROL = Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/.private')
EXPECTED = {
    'zcode': (8603, 'd8a9bc4bd3eaa38e90a6d8dc5f442794b33af4109e67b5e5f8795323a7c93716'),
    'minimax': (8663, 'd6a36770dcc620130f83856f3c9d77f50023e43cf611e63d2b3f1170f9e46192'),
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': sha(b)}


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')


def frozen(t):
    root, runtime = Path(t['cwd']), Path(t['cwd'] + '.runtime')
    inputs = root / 'docs/reviews/T07/round-3-input'
    source = json.loads((inputs / 'full-git-files.json').read_text())
    required = json.loads((inputs / 'required-reading.json').read_text())
    rows = []
    for base, group in [(root, 'root'), (runtime / 'scratch/probe-copy', 'scratch')]:
        for x in source['files']:
            r = pin(base / x['path'])
            assert r['bytes'] == x['reviewBytes'] and r['sha256'] == x['reviewSha256']
            rows.append({'group': group, **r})
    assert len(source['files']) == 1020 and len(required['items']) == 236
    for x in required['items']:
        r = pin(Path(x['path']))
        assert r['bytes'] == x['bytes'] and r['sha256'] == x['sha256']
        rows.append({'group': 'required-236', **r})
    for p in sorted(inputs.iterdir()):
        assert p.is_file() and not p.is_symlink()
        rows.append({'group': 'original-r3-sidecars', **pin(p)})
    for x in accepted_setup['rawArchiveRegularMembers']:
        if x['member'].startswith(t['role'] + '/setup/'):
            r = pin(Path(x['path']))
            assert r['bytes'] == x['bytes'] and r['sha256'] == x['sha256']
            rows.append({'group': 'accepted-setup-immutable', **r})
    head = subprocess.check_output(['/usr/bin/git', '-C', str(root), 'rev-parse', 'HEAD']).decode().strip()
    assert head == t['reviewHEAD']
    detached = subprocess.run(['/usr/bin/git', '-C', str(root), 'symbolic-ref', '-q', 'HEAD'], capture_output=True)
    assert detached.returncode == 1
    return {'role': t['role'], 'head': head, 'detached': True, 'files': rows,
            'vectorSHA256': sha(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode())}


assert not (HERE / 'operator-handoff.json').exists(), 'one-shot new additive package only'
accepted_setup = json.loads((HERE.parent / 'round-3-setup-20261023/setup-manifest.json').read_text())
template = (HERE / 'current-addendum-template.md').read_text()
handoff = {'state': 'ADDITIVE_MATERIALS_FIXED_ONE_INDEPENDENT_DELTA_AUDIT_PENDING_NO_GUI_START',
           'preparedUTC': datetime.now(timezone.utc).isoformat(), 'roles': [], 'ordinaryCommandsSelected': [],
           'ordinarySelectionReason': 'No independent concrete static concern arose in additive packaging; no unchanged ritual validation.',
           'setupCommandsExecuted': 0, 'productRuns': 0, 'GUIUsed': False, 'GUIReleased': True,
           'newExternalTasks': 0, 'formalSends': 0, 'externalGUIStartAuthorized': False,
           'oldRejectedVerificationNotLifted': True, 'processGate': 'PROCESS_FAIL / Pair 0 retained'}
for role, (expected_n, expected_h) in EXPECTED.items():
    ticket_path = CONTROL / f'T07-R3-{role}-own-launch-additive-and-unheld-ordinary-ticket-20261023.json'
    ticket_bytes = ticket_path.read_bytes()
    assert len(ticket_bytes) == expected_n and sha(ticket_bytes) == expected_h
    t = json.loads(ticket_bytes)
    root, runtime = Path(t['cwd']), Path(t['cwd'] + '.runtime')
    launch = runtime / 'launch'
    assert not launch.exists(), 'do not replace an existing launch'
    before = frozen(t)
    save(HERE / f'{role}-before-frozen-vector.json', before)
    launch.mkdir(mode=0o700)
    (launch / 'ordinary-review-ticket.json').write_bytes(ticket_bytes)
    old_manifest = json.loads((root / 'docs/reviews/T07/round-3-input/input-manifest.json').read_text())
    old_path = Path(old_manifest['fullInputPath'])
    old = old_path.read_bytes()
    assert len(old) == old_manifest['fullInputBytes'] and sha(old) == old_manifest['fullInputSHA256']
    facts, receipt = runtime / 'setup/role-installed-facts.json', runtime / 'setup/role-setup-audit-receipt.json'
    assert json.loads(receipt.read_text())['result'] == 'PASS_STATIC_ACTUAL_SETUP_ONLY'
    prefix = template.replace('__ROLE__', role).replace('__ROOT__', str(root)).replace('__RUNTIME__', str(runtime)).encode()
    for title, p in [('本角色当前有限 ordinary 后继票全文', launch / 'ordinary-review-ticket.json'),
                     ('本角色实际安装事实原文（生成时尚待独审）', facts),
                     ('本角色后继 setup 静态独审回执全文', receipt)]:
        b = p.read_bytes()
        prefix += f'\n## BEGIN {title}\n原件：`{p}`；{len(b)} B；SHA256 `{sha(b)}`。\n\n'.encode() + b
        prefix += f'\n## END {title}\n'.encode()
    prefix += b'\n# BEGIN EXACT ORIGINAL R3 COMPLETE INPUT (unchanged suffix)\n\n'
    other = 'minimax' if role == 'zcode' else 'zcode'
    assert f'T07-{other}-review-r3'.encode() not in prefix
    (launch / 'launch-addendum.md').write_bytes(prefix)
    complete = prefix + old
    (launch / 'complete-launch-input.md').write_bytes(complete)
    assert complete[len(prefix):] == old and complete.endswith(old)
    full_pin = pin(launch / 'complete-launch-input.md')
    cover = f'''# T07 R3 {role} 完整追加启动壳（待独立 GUI START 后投递）

操作员须另获 controller GUI START 后才可创建/发送；本壳不授予 START。正式投递后的审查任务只使用本角色完整附件和精确路径，不从旧 SID 推定身份。

工程根：`{root}`；runtime：`{runtime}`。P=`{t['product']}`；detached R=`{t['reviewHEAD']}`。

完整附件：`{launch / 'complete-launch-input.md'}`，{len(complete)} B / {complete.count(bytes([10]))} LF；SHA256 `{sha(complete)}`。必须全文读取当前有效增补及其后的旧完整正文，不能只读摘要或历史前缀。

本角色追加清单：`{launch / 'own-launch-manifest.json'}`。当前票：`{launch / 'ordinary-review-ticket.json'}`，{len(ticket_bytes)} B，SHA256 `{sha(ticket_bytes)}`。安装事实与后继 setup 审查回执均为 own 路径，已在增补中全文嵌入；所有旧236项/历史范围照旧。

本侧 main root 依赖已装，scratch 未装；当前允许为独立具体静态疑点选择票内一次 unheld ordinary，须先审现成证据，不建立全部必跑矩阵。原 pytest/vitest/npm check 目的 hold 继续；不得拆命令/换角色或工具绕行。原七P3/NR01–05/M P2P3未决、PROCESS_FAIL/Pair0保留。无新安装、产品/DB/native/render/browser授权；模型不读本轮peer或aggregate。

实际 UI 模型/等级/权限、SID/turn、附件接收及正式终态另由操作员真实读回；当前均未产生，创建和发送数0。唯一报告仍为 `{old_manifest['report']}`。
'''
    (launch / 'launch-cover.md').write_text(cover)
    setup_files = [pin(p) for p in sorted((runtime / 'setup').iterdir()) if p.is_file()]
    mandatory = [pin(launch / 'ordinary-review-ticket.json'), pin(facts), pin(receipt)]
    mandatory += [pin(runtime / f'setup/{n:02d}.{stream}.txt') for n in range(1, 6) for stream in ['stdout', 'stderr']]
    manifest = {'role': role, 'root': str(root), 'runtime': str(runtime), 'product': t['product'], 'reviewHead': t['reviewHEAD'],
                'state': 'ROLE_ADDITIVE_FIXED_NO_GUI_START', 'fullInput': full_pin, 'fullInputLF': complete.count(b'\n'),
                'addendum': pin(launch / 'launch-addendum.md'), 'addendumLF': prefix.count(b'\n'),
                'originalFullInput': pin(old_path), 'prefixPlusOldExactBytes': True, 'originalSuffixBytes': len(old),
                'cover': pin(launch / 'launch-cover.md'), 'ordinaryTicket': pin(launch / 'ordinary-review-ticket.json'),
                'roleInstalledFacts': pin(facts), 'roleSetupAuditReceipt': pin(receipt),
                'modelVisibleSetupFiles': setup_files,
                'mandatorySupplementalFullEOF': [{**x, 'actualReadCompleted': False, 'requiredVisibleEOF': True} for x in mandatory],
                'originalRequiredReading': pin(root / 'docs/reviews/T07/round-3-input/required-reading.json'),
                'originalRequiredItems': 236, 'sourceFilesEachRootAndScratch': 1020,
                'supplementalReadPolicy': 'Own listed setup files only; mandatory13 do not replace original236; optional metadata pin inspection is not a pre-signed visible EOF.',
                'historicalFactsPendingSupersededByLaterOwnAuditReceipt': True,
                'currentLimitedOrdinaryPermissionOverridesHistoricalBlanketNoRun': True,
                'heldVerificationPurposesStillHeld': t['heldPurposesRemain'], 'environmentExactReplacement': t['environmentExactReplacement'],
                'ordinaryCommandsSelectedByPreparer': [], 'noNewMandatoryMatrix': True,
                'peerOrAggregateModelVisibleFiles': [], 'report': old_manifest['report'], 'operatorIdentityReceipt': old_manifest['operatorReceipt'],
                'actualSettingsUI': None, 'actualSID': None, 'originalTurnId': None,
                'externalGUIStartAuthorized': False, 'newExternalTasks': 0, 'formalSends': 0, 'GUIReleased': True,
                'processGate': 'PROCESS_FAIL / Pair 0 retained', 'originalMP2P3UnchangedPending': True}
    save(launch / 'own-launch-manifest.json', manifest)
    for p in sorted(launch.iterdir()):
        shutil.copyfile(p, HERE / f'{role}-{p.name}')
    after = frozen(t)
    assert before['files'] == after['files'] and before['vectorSHA256'] == after['vectorSHA256']
    save(HERE / f'{role}-after-frozen-vector.json', after)
    handoff['roles'].append({'role': role, 'root': str(root), 'runtime': str(runtime),
                             'launchFiles': [pin(p) for p in sorted(launch.iterdir())],
                             'frozenVectorBefore': pin(HERE / f'{role}-before-frozen-vector.json'),
                             'frozenVectorAfter': pin(HERE / f'{role}-after-frozen-vector.json'),
                             'frozenVectorSHA256': before['vectorSHA256'], 'frozenOldMaterialsUnchanged': True,
                             'fullInput': full_pin, 'prefixPlusExactOldInput': True,
                             'modelVisibleCurrentPeerPrefixFound': False})
save(HERE / 'operator-handoff.json', handoff)
print(json.dumps({'state': handoff['state'], 'roles': [{'role': r['role'], 'fullInput': r['fullInput']} for r in handoff['roles']], 'newTasks': 0, 'ordinaryCommands': 0}, ensure_ascii=False))
