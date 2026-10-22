#!/usr/bin/env python3
"""Bounded packaged-engine probe. CLI only; owner-authorized resource identity required.
Path checks/periodic budgets are engineering guards, not an OS sandbox or atomic snapshot.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import selectors
import signal
import stat
import subprocess
import sys
import time
import uuid


class BoundaryError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise BoundaryError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def absolute(value):
    p = Path(value)
    require(p.is_absolute() and '..' not in p.parts, 'ABSOLUTE_NORMAL_PATH_REQUIRED')
    return p


def no_links(path):
    """Check all currently existing ancestors, without following a link."""
    p = absolute(str(path))
    for part in reversed((p, *p.parents)):
        try:
            s = part.lstat()
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(s.st_mode), 'SYMLINK_WRITE_OR_ROOT_CHAIN')
    return p


def overlap(a, b):
    return a == b or a in b.parents or b in a.parents


def read_regular(path, cap=16 * 1024 * 1024):
    no_links(path)
    s = path.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_size <= cap, 'INVALID_INPUT_FILE_OR_SIZE')
    with os.fdopen(os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)), 'rb') as f:
        t = os.fstat(f.fileno())
        require((s.st_dev, s.st_ino) == (t.st_dev, t.st_ino), 'INPUT_IDENTITY_CHANGED')
        data = f.read(cap + 1)
    require(len(data) <= cap, 'INPUT_SIZE_LIMIT')
    after = path.lstat()
    identity = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_size, x.st_mtime_ns, x.st_ctime_ns, x.st_nlink)
    require(identity(after) == identity(s), 'INPUT_CHANGED_DURING_READ')
    return data


def tree_bytes(root):
    """Non-atomic lstat accounting through no-follow directory handles; no content reads."""
    def count(fd):
        total = 0
        with os.scandir(fd) as it:
            names = [e.name for e in it]
        for name in names:
            try:
                s = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if stat.S_ISDIR(s.st_mode):
                    child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                    try:
                        actual = os.fstat(child)
                        require((s.st_dev, s.st_ino) == (actual.st_dev, actual.st_ino), 'BUDGET_DIRECTORY_CHANGED')
                        total += count(child)
                    finally:
                        os.close(child)
                else:
                    total += s.st_size
            except FileNotFoundError:
                continue  # Another run removed its temporary entry during this sample.
        return total
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return count(fd)
    finally:
        os.close(fd)


class Guard:
    def __init__(self, args, sources):
        raw = read_regular(absolute(args.authority))
        require(sha(raw) == args.authority_sha256, 'AUTHORITY_SHA_MISMATCH')
        self.authority = json.loads(raw)
        a = self.authority
        require(a.get('schemaVersion') == 1 and isinstance(a.get('protectedRoots'), list) and a['protectedRoots'], 'AUTHORITY_SCHEMA')
        self.base = no_links(absolute(a['allowedRunBase'])).resolve(strict=True)
        require(self.base.is_dir(), 'RUN_BASE_NOT_DIRECTORY')
        self.protected = [no_links(absolute(x)).resolve(strict=True) for x in a['protectedRoots']]
        self.protected += [no_links(absolute(str(x))).resolve(strict=True) for x in sources]
        self.work = no_links(absolute(args.work_root))
        self.out = no_links(absolute(args.output_root))
        require(self.work.parent == self.base and not os.path.lexists(self.work), 'RUN_MUST_BE_NEW_DIRECT_CHILD')
        require(self.work in self.out.parents and not os.path.lexists(self.out), 'OUTPUT_MUST_BE_NEW_RUN_DESCENDANT')
        require(not any(overlap(self.work, x) or overlap(self.out, x) for x in self.protected), 'PROTECTED_ROOT_OVERLAP')
        self.cap = int(a['limits']['combinedScratchBytes'])
        self.log_cap = int(a['limits']['capturedLogBytes'])
        self.timeout = float(a['limits']['nativeTimeoutSeconds'])
        require(0 < self.cap <= 128 * 1024 * 1024 and 0 < self.log_cap <= 8 * 1024 * 1024 and 0 < self.timeout <= 150, 'AUTHORITY_LIMITS')
        self.peak = self.sample()
        self.log_bytes = 0
        self.started = False
        self.work_id = None

    def sample(self, reserve=0):
        value = tree_bytes(self.base)
        require(value + reserve <= self.cap, 'COMBINED_SCRATCH_BUDGET')
        if hasattr(self, 'peak'):
            self.peak = max(self.peak, value)
        return value

    def begin(self):
        self.sample()
        no_links(self.work.parent)
        self.work.mkdir(mode=0o700)
        s = self.work.lstat()
        self.work_id = (s.st_dev, s.st_ino)
        self.started = True
        self.directory(self.out)
        for n in ['tmp', 'cache', 'db']:
            self.directory(self.work / n)

    def check(self, p):
        require(self.started and (p == self.work or self.work in p.parents), 'OUTSIDE_OWN_RUN')
        s = self.work.lstat()
        require((s.st_dev, s.st_ino) == self.work_id and stat.S_ISDIR(s.st_mode), 'RUN_IDENTITY_CHANGED')
        no_links(p)
        require(not any(overlap(p, x) for x in self.protected), 'PROTECTED_OUTPUT')
        self.sample()

    def directory(self, p):
        self.check(p)
        if p == self.work:
            return
        missing = []
        q = p
        while not q.exists():
            missing.append(q)
            q = q.parent
        for q in reversed(missing):
            self.check(q)
            q.mkdir(mode=0o700)
        require(p.is_dir(), 'EXPECTED_OWN_DIRECTORY')

    def new(self, p):
        self.directory(p.parent)
        self.check(p)
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        return os.fdopen(fd, 'wb')

    def write_json(self, name, value):
        data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
        self.sample(len(data))
        with self.new(self.out / name) as f:
            f.write(data)
        self.sample()

    def env(self, db_name):
        keep = ['PATH', 'HOME', 'LANG', 'LC_ALL', 'TZ', 'SYSTEMROOT', 'WINDIR']
        env = {k: os.environ[k] for k in keep if k in os.environ}
        env.update({'TMPDIR': str(self.work/'tmp'), 'TMP': str(self.work/'tmp'), 'TEMP': str(self.work/'tmp'),
                    'XDG_CACHE_HOME': str(self.work/'cache'), 'ONTOLEARN_DB_PATH': str(self.work/'db'/db_name),
                    'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
                    'GIT_CONFIG_COUNT': '0', 'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0'})
        return env


def run_child(g, argv, tag, env, timeout, on_line=None):
    """Drain both pipes with bounded logs; terminate only our new process group."""
    g.check(g.work)
    require(0 < timeout <= g.timeout, 'TIMEOUT_RANGE')
    streams = {n: g.new(g.out / (tag + '.' + n + '.log')) for n in ['stdout', 'stderr']}
    started = time.monotonic()
    proc = None
    failure_info = None
    sel = selectors.DefaultSelector()
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    info = {'argv': [str(x) for x in argv], 'cwd': str(g.work), 'envKeys': sorted(env), 'tag': tag,
            'stdout': str(g.out/(tag+'.stdout.log')), 'stderr': str(g.out/(tag+'.stderr.log'))}
    try:
        proc = subprocess.Popen([str(x) for x in argv], cwd=g.work, env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        for name, pipe in [('stdout', proc.stdout), ('stderr', proc.stderr)]:
            os.set_blocking(pipe.fileno(), False)
            sel.register(pipe, selectors.EVENT_READ, name)
        if on_line:
            on_line(None, proc)
        else:
            proc.stdin.close()
        while sel.get_map():
            require(time.monotonic()-started < timeout, 'CHILD_TIMEOUT')
            g.sample()
            for key, _ in sel.select(0.05):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                name = key.data
                allowed = max(0, g.log_cap - g.log_bytes)
                kept = chunk[:allowed]
                streams[name].write(kept)
                streams[name].flush()
                g.log_bytes += len(kept)
                require(len(kept) == len(chunk), 'CAPTURED_LOG_LIMIT')
                buffers[name].extend(chunk)
                if on_line and name == 'stdout':
                    while b'\n' in buffers[name]:
                        line, _, rest = buffers[name].partition(b'\n')
                        buffers[name] = bytearray(rest)
                        on_line(line, proc)
        remaining = timeout - (time.monotonic()-started)
        require(remaining > 0, 'CHILD_TIMEOUT')
        rc = proc.wait(timeout=remaining)
        require(rc == 0, 'CHILD_NONZERO_EXIT_' + str(rc))
        require(not on_line or not buffers['stdout'], 'UNTERMINATED_PROTOCOL_FRAME')
        info.update({'exitCode': rc, 'passed': True, 'stderrBytes': len(buffers['stderr']), 'elapsedSeconds': time.monotonic()-started})
        return info, bytes(buffers['stdout']), bytes(buffers['stderr'])
    except Exception as e:
        info.update({'passed': False, 'error': str(e), 'exitCode': proc.poll() if proc else None,
                     'elapsedSeconds': time.monotonic()-started})
        failure_info = info
        raise
    finally:
        if proc:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=2)
            for pipe in [proc.stdin, proc.stdout, proc.stderr]:
                if pipe and not pipe.closed:
                    pipe.close()
        sel.close()
        for f in streams.values():
            f.close()
        if failure_info is not None:
            failure_info['exitCodeAfterCleanup'] = proc.poll() if proc else None
            failure_info['ownedChildReaped'] = proc is None or proc.poll() is not None
            g.write_json(tag + '.failure.json', failure_info)


def common_args(parser):
    for n in ['authority', 'authority-sha256', 'work-root', 'output-root']:
        parser.add_argument('--' + n, required=True)


def validate_resources(args):
    manifest_path = absolute(args.engine_resource_manifest)
    raw = read_regular(manifest_path)
    require(sha(raw) == args.engine_resource_manifest_sha256, 'RESOURCE_MANIFEST_SHA_MISMATCH')
    m = json.loads(raw)
    require(m.get('schemaVersion') == 1 and m.get('ownerApproved') is True, 'OWNER_RESOURCE_APPROVAL_REQUIRED')
    require(args.engine_mode != 'readonly-declared-engine' or m.get('readonlyExecutionApproved') is True, 'READONLY_EXECUTION_NOT_APPROVED')
    root = no_links(absolute(m['resourceRoot'])).resolve(strict=True)
    relengine = m['engineRelativePath']
    expected = {}
    for row in m['entries']:
        rel = PurePosixPath(row['path'])
        require(not rel.is_absolute() and '..' not in rel.parts and str(rel) == row['path'] and row['path'] not in expected, 'UNSAFE_OR_DUPLICATE_RESOURCE_PATH')
        require(row['type'] in ['file', 'symlink'], 'RESOURCE_TYPE')
        expected[str(rel)] = row
    require(expected and relengine in expected and expected[relengine]['type'] == 'file', 'EXACT_ENGINE_REQUIRED')
    require(absolute(args.engine_input) == root/relengine, 'ENGINE_INPUT_NOT_DECLARED')
    actual = set()
    for d, dirs, files in os.walk(root, followlinks=False):
        for name in list(dirs):
            p = Path(d)/name
            if p.is_symlink():
                actual.add(p.relative_to(root).as_posix())
                dirs.remove(name)
        for name in files:
            actual.add((Path(d)/name).relative_to(root).as_posix())
    require(actual == set(expected), 'RESOURCE_SET_MISMATCH')
    for rel, row in expected.items():
        p = root/rel
        s = p.lstat()
        require(oct(stat.S_IMODE(s.st_mode)) == row['mode'], 'RESOURCE_MODE_MISMATCH')
        if row['type'] == 'file':
            require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'RESOURCE_FILE_OR_LINKCOUNT')
            data = read_regular(p, max(row['bytes'], 1))
            require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'RESOURCE_HASH_MISMATCH')
        else:
            require(stat.S_ISLNK(s.st_mode) and os.readlink(p) == row['target'], 'RESOURCE_LINK_MISMATCH')
            target = p.resolve(strict=True)
            require(root in target.parents and target.relative_to(root).as_posix() in expected, 'RESOURCE_LINK_OUTSIDE_CLOSURE')
    return m, root, expected, raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    common_args(parser)
    parser.add_argument('--engine-mode', required=True, choices=['readonly-declared-engine', 'copy-declared-engine-resources'])
    parser.add_argument('--engine-input', required=True)
    parser.add_argument('--engine-resource-manifest', required=True)
    parser.add_argument('--engine-resource-manifest-sha256', required=True)
    parser.add_argument('--timeout-seconds', type=float)
    args = parser.parse_args()
    g = None
    try:
        m, root, rows, raw = validate_resources(args)
        g = Guard(args, [root, absolute(args.engine_resource_manifest)])
        timeout = args.timeout_seconds if args.timeout_seconds is not None else g.timeout
        require(0 < timeout <= g.timeout, 'TIMEOUT_RANGE')
        g.sample(sum(r.get('bytes', 0) for r in rows.values()) if args.engine_mode.startswith('copy') else 0)
        g.begin()
        engine = absolute(args.engine_input)
        if args.engine_mode == 'copy-declared-engine-resources':
            copy_root = g.work/'native-engine'
            g.directory(copy_root)
            for rel, row in rows.items():
                if row['type'] != 'file':
                    continue
                data = read_regular(root/rel, max(row['bytes'], 1))
                require(sha(data) == row['sha256'], 'SOURCE_CHANGED_BEFORE_COPY')
                with g.new(copy_root/rel) as f:
                    f.write(data)
                    os.fchmod(f.fileno(), int(row['mode'], 8))
                verified = read_regular(copy_root/rel, max(row['bytes'], 1))
                require(len(verified) == row['bytes'] and sha(verified) == row['sha256'], 'COPIED_RESOURCE_HASH_MISMATCH')
                copied = (copy_root/rel).stat()
                source = (root/rel).stat()
                require((copied.st_dev, copied.st_ino) != (source.st_dev, source.st_ino) and copied.st_nlink == 1, 'COPY_NOT_INDEPENDENT')
            for rel, row in rows.items():
                if row['type'] == 'symlink':
                    p = copy_root/rel
                    g.directory(p.parent)
                    g.check(p)
                    os.symlink(row['target'], p)
                    require(copy_root in p.resolve(strict=True).parents, 'COPY_LINK_ESCAPE')
            engine = copy_root/m['engineRelativePath']
        require(os.access(engine, os.X_OK), 'ENGINE_NOT_EXECUTABLE')
        observations = []
        pending = {}
        session = None
        health_count = 0
        def on_line(line, proc):
            nonlocal pending, session, health_count
            if line is None:
                method = 'hello'
            else:
                value = json.loads(line)
                require(value.get('id') == pending['id'] and value.get('ok') is True, 'PROTOCOL_RESPONSE_MISMATCH')
                if pending['method'] == 'hello':
                    session = value.get('engineSessionId')
                    require(isinstance(session, str) and session, 'HELLO_SESSION_MISSING')
                else:
                    require(value.get('engineSessionId') == session and value.get('result', {}).get('status') == 'ok', 'HEALTH_RESPONSE_MISMATCH')
                    health_count += 1
                observations.append({'method': pending['method'], 'ok': True})
                if health_count == 10:
                    proc.stdin.close()
                    return
                method = 'health'
            pending = {'kind': 'request', 'id': str(uuid.uuid4()), 'protocolVersion': 2, 'engineSessionId': session,
                       'method': method, 'params': {'supportedVersions': [2], 'clientId': str(uuid.uuid4())} if method == 'hello' else {}}
            proc.stdin.write((json.dumps(pending)+'\n').encode())
            proc.stdin.flush()
        start = time.monotonic()
        first, _, err = run_child(g, [engine], 'hello-health', g.env('hello-health.sqlite'), timeout, on_line)
        require(health_count == 10 and len(observations) == 11 and not err, 'INCOMPLETE_OR_NOISY_HEALTH')
        remaining = timeout-(time.monotonic()-start)
        require(remaining > 0, 'NATIVE_TOTAL_TIMEOUT')
        second, data, err = run_child(g, [engine, '--storage-probe', '--scale', '1', '--trial', '0'], 'storage-probe', g.env('storage-probe.sqlite'), remaining)
        storage = json.loads(data)
        require(storage.get('scale') == 1 and storage.get('triples') == 18 and storage.get('result') == ['urn:case:0:alarm/A01'] and storage.get('result') == storage.get('expected') and not err, 'STORAGE_PROBE_MISMATCH')
        # Check original declared bytes again, not only before execution.
        validate_resources(args)
        result = {'passed': True, 'scope': 'synthetic stub protocol only' if m.get('kind') == 'synthetic-stub' else 'packaged CLI only; no Electron/GUI/userData/parity/integration proof',
                  'mode': args.engine_mode, 'manifestSHA256': sha(raw), 'engineExecuted': str(engine), 'handshakeAndHealth': observations,
                  'subprocesses': [first, second], 'guiLaunched': False, 'combinedScratchBytesAtEnd': g.sample(), 'sampledCombinedPeakBytes': g.peak,
                  'capturedLogBytes': g.log_bytes, 'limitsAreEngineeringChecksNotOSHardQuotas': True, 'atomicSnapshotClaimed': False}
        g.write_json('native-probe-result.json', result)
        print(json.dumps({'passed': True, 'result': str(g.out/'native-probe-result.json'), 'scope': result['scope']}))
        return 0
    except Exception as e:
        failure = {'passed': False, 'error': str(e), 'scope': 'native boundary/protocol failure; not a product verdict'}
        if g and g.started:
            try:
                g.write_json('native-probe-failure.json', failure)
            except Exception as evidence_error:
                failure['failureEvidenceWriteError'] = str(evidence_error)
        print(json.dumps(failure), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
