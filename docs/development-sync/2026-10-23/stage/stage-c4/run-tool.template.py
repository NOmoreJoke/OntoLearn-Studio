"""C4 serial three-command launcher, loaded directly from the readonly input.

No CLI fixture mode, arbitrary command, cwd-code loading or shell evaluation.
Pure-fixture tests may inject the OS probe into run() without using this CLI.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import sys
import time
import types
import uuid

CALLER_LOG_RESERVE = 32768
RECEIPT_RESERVE = 65536
COMMANDS = ('browserBuild', 'browserVerify', 'nativeCLI')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bootstrap(receipt_path, receipt_sha, self_path=None):
    # No cwd import. Pin the external receipt, ourselves and the checker before
    # executing any code from the mounted input. Subsequent gates reject links.
    def raw(path):
        path = Path(path)
        require(path.is_absolute() and os.path.normpath(str(path)) == str(path), 'BOOTSTRAP_ABSOLUTE_PATH')
        for q in [*reversed(path.parents), path]:
            s = q.lstat()
            require(not stat.S_ISLNK(s.st_mode), 'BOOTSTRAP_SYMLINK')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            s = os.fstat(fd)
            require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'BOOTSTRAP_ORDINARY_FILE')
            parts = []
            while True:
                b = os.read(fd, 1024 * 1024)
                if not b:
                    break
                parts.append(b)
            z = os.fstat(fd)
            require((s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns) ==
                    (z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns), 'BOOTSTRAP_FILE_CHANGED')
            return b''.join(parts)
        finally:
            os.close(fd)
    body = raw(receipt_path)
    require(len(receipt_sha) == 64 and digest(body) == receipt_sha, 'ROOT_RECEIPT_PIN_MISMATCH')
    receipt = json.loads(body)
    ro = Path(receipt['inputRoot'])
    actual = Path(self_path or __file__).absolute()
    require(actual == ro / 'run-tool.py', 'HELPER_MUST_RUN_FROM_AUTHORITY_INPUT')
    require(digest(raw(actual)) == receipt['helperSHA256'], 'HELPER_PIN_MISMATCH')
    checker_path = ro / 'check-inputs.py'
    checker_body = raw(checker_path)
    require(digest(checker_body) == receipt['checkerSHA256'], 'CHECKER_PIN_MISMATCH')
    module = types.ModuleType('c4_pinned_checker')
    module.__file__ = str(checker_path)
    exec(compile(checker_body, str(checker_path), 'exec'), module.__dict__)
    return module


def measure(root):
    """Only this run base. Reject symlinks, special files and changed directories."""
    def walk(fd):
        total = logs = 0
        for name in os.listdir(fd):
            try:
                s = os.stat(name, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            require(not stat.S_ISLNK(s.st_mode), 'RUN_SYMLINK')
            if stat.S_ISDIR(s.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    a = os.fstat(child)
                    require((a.st_dev, a.st_ino) == (s.st_dev, s.st_ino), 'RUN_DIRECTORY_CHANGED')
                    x, y = walk(child)
                    total += x
                    logs += y
                finally:
                    os.close(child)
            else:
                require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'RUN_NOT_ORDINARY')
                total += s.st_size
                if name.endswith(('.stdout.log', '.stderr.log')):
                    logs += s.st_size
        return total, logs
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return walk(fd)
    finally:
        os.close(fd)


def capture(argv, cwd, env, meta, timeout, budget_base, limits, on_start=None):
    selector = selectors.DefaultSelector()
    handles, child = {}, None
    try:
        child = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        if on_start is not None:
            on_start(child.pid)
        return monitor(child, selector, handles, meta, timeout, budget_base, limits)
    finally:
        selector.close()
        for handle in handles.values():
            if not handle.closed:
                handle.close()
        if child is not None:
            if child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait(timeout=2)
            for pipe in [child.stdout, child.stderr]:
                if not pipe.closed:
                    pipe.close()


def monitor(child, selector, handles, meta, timeout, budget_base, limits):
    counts = {'stdout': 0, 'stderr': 0}
    for name, pipe in [('stdout', child.stdout), ('stderr', child.stderr)]:
        handle = (meta / ('caller.' + name + '.log')).open('xb')
        handles[name] = handle
        selector.register(pipe, selectors.EVENT_READ, name)
    start, stop_at, reason = time.monotonic(), None, None
    peak_bytes = peak_logs = 0
    try:
        while selector.get_map() or child.poll() is None:
            for key, _ in selector.select(.05):
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                name = key.data
                room = max(0, CALLER_LOG_RESERVE // 2 - counts[name])
                handles[name].write(data[:room])
                handles[name].flush()
                counts[name] += len(data)
                if counts[name] > CALLER_LOG_RESERVE // 2:
                    reason = reason or 'CALLER_CAPTURE_LIMIT'
            try:
                size, logs = measure(budget_base)
                peak_bytes, peak_logs = max(peak_bytes, size), max(peak_logs, logs)
                if size + RECEIPT_RESERVE > limits['combinedScratchBytes']:
                    reason = reason or 'SIDE_SCRATCH_LIMIT'
                if logs > limits['capturedLogBytes']:
                    reason = reason or 'SIDE_LOG_LIMIT'
            except Exception as exc:
                reason = reason or str(exc)
            if time.monotonic() - start > timeout:
                reason = reason or 'ACTIVE_TIMEOUT'
            if reason and stop_at is None:
                stop_at = time.monotonic()
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            if stop_at is not None and time.monotonic() - stop_at > 1:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if stop_at is not None and time.monotonic() - stop_at > 3:
                break
    finally:
        selector.close()
        for handle in handles.values():
            handle.close()
        for pipe in [child.stdout, child.stderr]:
            if not pipe.closed:
                pipe.close()
    try:
        exit_code = child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        exit_code = child.wait(timeout=2)
        reason = reason or 'CHILD_REAP_TIMEOUT'
    return {'exitCode': exit_code, 'captureFailure': reason, 'callerObservedBytes': counts,
            'callerTruncated': any(x > CALLER_LOG_RESERVE // 2 for x in counts.values()),
            'peakSampledRunBytes': peak_bytes, 'peakSampledCapturedLogBytes': peak_logs,
            'descendantCleanup': 'UNKNOWN after forced termination' if stop_at else
                                 'Direct child reaped; no full-descendant claim'}


def gate_summary(value):
    return {k: value[k] for k in ['passed', 'fixedFiles', 'checkedResources',
                                 'manifestIdentity', 'proof', 'evidenceScope']}


def run(receipt_path, receipt_sha, command, probe=None, self_path=None):
    result = {'passed': False, 'command': command, 'childStarted': False,
              'firstFailure': None, 'lockCleanup': 'not acquired',
              'limitsAreEngineeringSampling': True, 'wholeApplicationSandboxClaimed': False}
    meta = None
    lock = lock_identity = lock_token = None
    try:
        require(command in COMMANDS, 'THREE_COMMANDS_ONLY')
        checker = bootstrap(receipt_path, receipt_sha, self_path)
        receipt, ro, rw, _ = checker.root_binding(receipt_path, receipt_sha, probe)
        # A bounded refusal receipt can be saved only after the pinned root/OS
        # binding is valid. No output is followed from an untrusted receipt.
        base = checker.canonical(str(rw / 'runs'))
        environment = checker.canonical(str(rw / 'environment'))
        used, logs = measure(base)
        require(used + RECEIPT_RESERVE < 67108864 and logs + CALLER_LOG_RESERVE < 4194304,
                'SIDE_PREEXISTING_BUDGET_EXHAUSTED')
        token = uuid.uuid4().hex
        meta = base / ('launch-record-' + token)
        meta.mkdir()
        before = checker.gate(receipt_path, receipt_sha, True, probe)
        result['preGate'] = gate_summary(before)
        grant = receipt.get('commandGrants', {}).get(command, {})
        require(grant.get('status') == 'CONTROLLER_GRANTED' and grant.get('command') == command and
                grant.get('inputManifestSHA256') == receipt['inputManifestSHA256'] and
                isinstance(grant.get('ownerGrantId'), str) and bool(grant['ownerGrantId']),
                'EXPLICIT_COMMAND_WINDOW_GRANT_REQUIRED')
        result['controllerCommandGrant'] = grant
        config = json.loads(checker.read_file(ro / 'config/runtime-config.json')[0])
        authority = json.loads(checker.read_file(ro / 'config/authority.json')[0])
        limits = authority['limits']
        require(limits == {'combinedScratchBytes': 67108864, 'capturedLogBytes': 4194304,
                           'browserTimeoutSeconds': 180, 'nativeTimeoutSeconds': 150}, 'FIXED_SIDE_LIMITS')
        require(authority['allowedRunBase'] == str(base) and authority['allowNativeBuild'] is False and
                str(ro) in authority['protectedRoots'], 'AUTHORITY_ROOT_OR_NATIVE_BUILD_DRIFT')
        require(config['cwd'] == str(environment), 'OWN_ENVIRONMENT_CWD')
        env = config['environment']
        require(set(env) == {'PATH', 'NO_COLOR', 'TMPDIR', 'TMP', 'TEMP', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME'},
                'ENVIRONMENT_KEYS_REQUIRED')
        for key in ['TMPDIR', 'TMP', 'TEMP', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME']:
            path = checker.canonical(env[key])
            require(environment in path.parents, 'ENVIRONMENT_PATH_ESCAPE')
        lock = environment / 'launch.lock'
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        try:
            s = os.fstat(fd)
            lock_identity = (s.st_dev, s.st_ino)
            lock_token = uuid.uuid4().hex.encode()
            os.write(fd, lock_token)
        finally:
            os.close(fd)
        work = base / (command.lower() + '-' + token)
        require(not work.exists(), 'NEW_RUN_REQUIRED')
        dynamic = json.loads(json.dumps(authority))
        dynamic['limits']['combinedScratchBytes'] -= RECEIPT_RESERVE
        dynamic['limits']['capturedLogBytes'] -= CALLER_LOG_RESERVE
        if command == 'nativeCLI':
            dynamic['limits']['capturedLogBytes'] -= logs
        dynamic_path = meta / 'authority.json'
        dynamic_path.write_text(json.dumps(dynamic, indent=2) + '\n')
        argv = list(config['commands'][command])
        require(all(isinstance(x, str) for x in argv) and len(argv) >= 2, 'ARGV_SCHEMA')
        require(argv[0] == config['executables'][command], 'EXECUTABLE_BINDING')
        entry = config['entryPoints'][command]
        require(entry in argv and str(ro) + '/' in entry and ro in Path(entry).parents,
                'ENTRY_MUST_BE_READONLY_BOUND')
        require(str(Path(entry).relative_to(ro)) in before['fileIdentity'], 'ENTRY_NOT_IN_FIXED_MANIFEST')
        values = {'--authority': str(dynamic_path), '--authority-sha256': digest(dynamic_path.read_bytes()),
                  '--work-root': str(work), '--output-root': str(work / 'out')}
        if command == 'browserVerify':
            values['--session'] = work.name
        for flag, value in values.items():
            require(argv.count(flag) == 1, 'UNIQUE_FLAG_REQUIRED ' + flag)
            argv[argv.index(flag) + 1] = value
        result.update(argv=argv, cwd=str(environment), environmentKeys=sorted(env),
                      workRoot=str(work), beforeBytes=used, beforeCapturedLogBytes=logs,
                      dynamicAuthoritySHA256=digest(dynamic_path.read_bytes()), dynamicLimits=dynamic['limits'])
        result['spawnAttempted'] = True
        try:
            capture_result = capture(argv, str(environment), env, meta,
                                     150 if command == 'nativeCLI' else 180, base, limits,
                                     lambda pid: result.update(childStarted=True, childPID=pid))
            result.update(capture_result)
            if capture_result['captureFailure'] is not None:
                result['firstFailure'] = capture_result['captureFailure']
            elif capture_result['exitCode'] != 0:
                result['firstFailure'] = 'ACTIVE_CHILD_NONZERO'
        except Exception as exc:
            result['captureException'] = str(exc)[:2048]
            result['firstFailure'] = result['captureException']
        try:
            after = checker.gate(receipt_path, receipt_sha, True, probe)
            result['postGate'] = gate_summary(after)
            require(before['fileIdentity'] == after['fileIdentity'], 'INPUT_BEFORE_AFTER_IDENTITY_CHANGED')
        except Exception as exc:
            result['postGateError'] = str(exc)[:2048]
            result['firstFailure'] = result['firstFailure'] or result['postGateError']
        size, log_size = measure(base)
        result.update(afterBytes=size, afterCapturedLogBytes=log_size)
        require(size + RECEIPT_RESERVE <= limits['combinedScratchBytes'] and
                log_size <= limits['capturedLogBytes'], 'FINAL_SIDE_BUDGET')
        require(result['firstFailure'] is None, result['firstFailure'])
        result['passed'] = True
    except Exception as exc:
        result['firstFailure'] = result['firstFailure'] or str(exc)[:2048]
    finally:
        if lock_identity is not None:
            try:
                body, identity = checker.read_file(lock)
                require((identity['dev'], identity['ino']) == lock_identity and body == lock_token,
                        'LOCK_IDENTITY_OR_TOKEN_CHANGED')
                lock.unlink()
                result['lockCleanup'] = 'owned lock removed'
            except Exception as exc:
                result['passed'] = False
                result['lockCleanup'] = 'UNKNOWN; changed/missing lock preserved'
                result['firstFailure'] = result['firstFailure'] or str(exc)[:2048]
        if meta is not None:
            try:
                encoded = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode()
                require(len(encoded) < RECEIPT_RESERVE, 'RECEIPT_RESERVE_EXCEEDED')
                with (meta / 'launch-receipt.json').open('xb') as f:
                    f.write(encoded)
            except Exception as exc:
                result['passed'] = False
                result['receiptWriteFailure'] = str(exc)[:2048]
    result['receipt'] = str(meta / 'launch-receipt.json') if meta is not None else None
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root-receipt', required=True)
    p.add_argument('--root-receipt-sha256', required=True)
    p.add_argument('--command', required=True, choices=COMMANDS)
    a = p.parse_args()
    result = run(a.root_receipt, a.root_receipt_sha256, a.command)
    print(json.dumps({'passed': result['passed'], 'firstFailure': result['firstFailure'],
                      'receipt': result['receipt'], 'childStarted': result['childStarted']}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
