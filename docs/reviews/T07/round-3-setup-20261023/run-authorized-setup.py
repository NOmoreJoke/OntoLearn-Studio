"""One-shot exact-ticket dependency setup; no product validation or imports."""

import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import time
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
TICKET = Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/.private/T07-R3-two-role-isolated-dependency-setup-ticket-20261023.json')
TICKET_SHA = '2b6dada1ddd4f4270b94c7924a85095a5df14b50349744e91bb8a5673ef5566d'


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')


def info(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': sha(b)}


def git(root, *args):
    return subprocess.check_output(['/usr/bin/git', '-C', str(root), *args]).decode().strip()


def snapshot(role, source, required, baseline_inputs, baseline_metadata):
    root, runtime = Path(role['cwd']), Path(role['namespace'])
    scratch = runtime / 'scratch/probe-copy'
    rows = []
    for base, label in [(root, 'root-source'), (scratch, 'scratch-source')]:
        for x in source['files']:
            p = base / x['path']
            assert not p.is_symlink(), p
            r = info(p)
            assert r['bytes'] == x['reviewBytes'] and r['sha256'] == x['reviewSha256'], r
            rows.append({'group': label, **r})
    assert len(source['files']) == 1020 and len(required['items']) == 236
    for x in required['items']:
        p = Path(x['path'])
        assert p.is_relative_to(root) or p.is_relative_to(runtime)
        r = info(p)
        assert r['bytes'] == x['bytes'] and r['sha256'] == x['sha256'], r
        rows.append({'group': 'required-input', **r})
    for group, baseline in [('input-sidecars', baseline_inputs), ('metadata-originals', baseline_metadata)]:
        for x in baseline:
            r = info(Path(x['path']))
            assert r == x, r
            rows.append({'group': group, **r})
    for x in ticket['fixedDependencyInputs']:
        r = info(root / x['path'])
        assert r['bytes'] == x['bytes'] and r['sha256'] == x['sha256']
    assert git(root, 'rev-parse', 'HEAD') == ticket['reviewHEAD']
    detached = subprocess.run(['/usr/bin/git', '-C', str(root), 'symbolic-ref', '-q', 'HEAD'], capture_output=True)
    assert detached.returncode == 1
    for name in ['node_modules', '.venv']:
        assert not os.path.lexists(scratch / name)
    return {'UTC': utc(), 'role': role['role'], 'head': ticket['reviewHEAD'], 'detached': True,
            'sourceFilesEach': 1020, 'requiredInputs': 236, 'files': rows,
            'vectorSHA256': sha(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode()),
            'trackedStatus': git(root, 'status', '--porcelain=v1', '--untracked-files=no'),
            'scratchDependenciesAbsent': True}


def command(role, number, argv, setup, before_snapshot):
    label = f'{number:02d}'
    stdout, stderr = setup / f'{label}.stdout.txt', setup / f'{label}.stderr.txt'
    limit = ticket['operationalLimits']
    seconds = limit['versionSeconds'] if number <= 3 else limit['npmInstallSeconds'] if number == 4 else limit['uvSyncSeconds']
    start = utc()
    rec = {'number': number, 'argv': argv, 'cwd': role['cwd'], 'environmentExactReplacement': role['environmentExactReplacement'],
           'parentPID': os.getpid(), 'startUTC': start, 'timeoutSeconds': seconds, 'shell': False,
           'beforeSnapshot': before_snapshot, 'noRetry': True}
    with stdout.open('xb') as out, stderr.open('xb') as err:
        process = subprocess.Popen(argv, cwd=role['cwd'], env=role['environmentExactReplacement'],
                                   stdout=out, stderr=err, stdin=subprocess.DEVNULL, start_new_session=True)
        rec['childPID'] = process.pid
        save(setup / f'{label}.started.json', rec)
        print(json.dumps({'event': 'started', 'role': role['role'], 'number': number, 'childPID': process.pid, 'UTC': start}), flush=True)
        deadline = time.monotonic() + seconds
        stop = None
        while process.poll() is None:
            if stdout.stat().st_size > limit['stdoutBytesEach'] or stderr.stat().st_size > limit['stderrBytesEach']:
                stop = 'stream-operational-bound-exceeded'
            elif time.monotonic() >= deadline:
                stop = 'timeout'
            if stop:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=limit['termGraceSeconds'])
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=limit['killCloseSeconds'])
                break
            time.sleep(0.2)
        code = process.wait()
    rec.update({'endUTC': utc(), 'realChildIntegerExit': code, 'operationalStop': stop,
                'stdout': info(stdout), 'stderr': info(stderr), 'completeSeparateStreamsCapturedToFiles': True,
                'noWholeProcessTreeOrHardQuotaClaim': True})
    if number <= 3 and code == 0:
        expected = [f"v{ticket['expectedVersions']['node']}", ticket['expectedVersions']['npm'], f"uv {ticket['expectedVersions']['uv']}"][number - 1]
        actual = stdout.read_text().strip()
        rec['versionExpected'] = expected
        rec['versionActual'] = actual
        rec['versionMatches'] = actual == expected or (number == 3 and actual.startswith(expected + ' '))
    save(setup / f'{label}.result.json', rec)
    print(json.dumps({'event': 'completed', 'role': role['role'], 'number': number, 'exit': code, 'stop': stop, 'UTC': rec['endUTC']}), flush=True)
    return rec


ticket_bytes = TICKET.read_bytes()
assert len(ticket_bytes) == 10996 and sha(ticket_bytes) == TICKET_SHA
ticket = json.loads(ticket_bytes)
assert ticket['status'] == 'START_EXACT_TWO_ROLE_LOCKED_DEPENDENCY_SETUP_ONLY'
assert not (HERE / 'execution-summary.json').exists(), 'one-shot summary already exists'
python_pin = info(Path(ticket['pinnedExistingPython']['path']))
assert python_pin['sha256'] == ticket['pinnedExistingPython']['sha256'] and python_pin['bytes'] == ticket['pinnedExistingPython']['bytes']
save(HERE / 'setup-authorization.json', ticket)
summary = {'status': 'SETUP_IN_PROGRESS', 'startUTC': utc(), 'runnerPID': os.getpid(),
           'authorization': info(TICKET), 'pythonBaseReadOnlyPin': python_pin, 'roles': [],
           'productRuns': 0, 'externalTasks': 0, 'formalSends': 0, 'GUIReleased': True,
           'oldRejectedVerificationNotLifted': True, 'processGate': 'PROCESS_FAIL / Pair 0 retained'}
for role in ticket['roles']:
    root, runtime = Path(role['cwd']), Path(role['namespace'])
    setup = runtime / 'setup'
    assert not setup.exists(), 'no replacement/retry of existing setup namespace'
    inputs = root / 'docs/reviews/T07/round-3-input'
    source = json.loads((inputs / 'full-git-files.json').read_text())
    required = json.loads((inputs / 'required-reading.json').read_text())
    base_inputs = [info(p) for p in sorted(inputs.iterdir()) if p.is_file()]
    base_metadata = [info(p) for p in sorted((runtime / 'metadata').iterdir()) if p.is_file()]
    baseline = snapshot(role, source, required, base_inputs, base_metadata)
    assert all(not os.path.lexists(root / n) for n in ['node_modules', '.venv'])
    for n in ['npm-cache', 'uv-cache', 'tmp']:
        assert not any((runtime / n).iterdir()), n
    setup.mkdir(mode=0o700)
    save(setup / '00-chain-before.json', baseline)
    for n in ['home', 'xdg-cache', 'xdg-config', 'xdg-data']:
        p = runtime / n
        p.mkdir(mode=0o700)
    for n in ['npm-user-empty.npmrc', 'npm-global-empty.npmrc']:
        fd = os.open(setup / n, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
        assert stat.S_IMODE((setup / n).stat().st_mode) == 0o600
    recs = []
    for number, argv in enumerate(role['commandsOnceInOrder'], 1):
        before = snapshot(role, source, required, base_inputs, base_metadata)
        before_path = setup / f'{number:02d}.before.json'
        save(before_path, before)
        result = command(role, number, argv, setup, info(before_path))
        after = snapshot(role, source, required, base_inputs, base_metadata)
        assert before['vectorSHA256'] == after['vectorSHA256'] == baseline['vectorSHA256']
        after_path = setup / f'{number:02d}.after.json'
        save(after_path, after)
        result['afterSnapshot'] = info(after_path)
        result['frozenVectorsUnchanged'] = True
        save(setup / f'{number:02d}.result.json', result)
        recs.append(result)
        if result['realChildIntegerExit'] != 0 or result['operationalStop'] or result.get('versionMatches') is False:
            break
    after = snapshot(role, source, required, base_inputs, base_metadata)
    save(setup / '99-chain-after.json', after)
    row = {'role': role['role'], 'root': str(root), 'runtime': str(runtime),
           'status': 'SETUP_COMMANDS_EXIT0' if len(recs) == 5 and all(x['realChildIntegerExit'] == 0 and not x['operationalStop'] and x.get('versionMatches', True) for x in recs) else 'SETUP_STOPPED_FIRST_FAILURE',
           'commands': recs, 'before': info(setup / '00-chain-before.json'), 'after': info(setup / '99-chain-after.json'),
           'frozenVectorsUnchanged': baseline['vectorSHA256'] == after['vectorSHA256'],
           'sourceVectorSHA256': baseline['vectorSHA256'], 'scratchDependenciesInstalled': False,
           'setupIsNotProductValidation': True, 'independentAuditPending': True}
    save(setup / 'role-execution-receipt.json', row)
    summary['roles'].append(row)
    save(HERE / 'execution-summary.json', summary)
summary.update({'status': 'COMMAND_EXECUTION_FINISHED_STATIC_METADATA_AND_AUDIT_PENDING', 'endUTC': utc()})
save(HERE / 'execution-summary.json', summary)
print(json.dumps({'event': 'all-chains-finished', 'status': [(x['role'], x['status']) for x in summary['roles']]}), flush=True)
