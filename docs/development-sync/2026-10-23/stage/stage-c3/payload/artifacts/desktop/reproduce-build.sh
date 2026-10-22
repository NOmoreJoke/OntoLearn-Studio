#!/bin/sh
# Self-contained Python stdlib implementation; no shared runtime helper.
exec python3 - "$@" <<'PY_NATIVE_REBUILD'
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


import io
import re
import tarfile


def build_main():
    p = argparse.ArgumentParser(description='Fixed-SHA native rebuild plan; execution requires owner authority.')
    common_args(p)
    for n in ['source-root', 'expected-git-sha', 'source-manifest', 'source-manifest-sha256', 'cache-root', 'git-path']:
        p.add_argument('--'+n, required=True)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--npm-path')
    p.add_argument('--uv-path')
    args = p.parse_args()
    g = None
    try:
        require(re.fullmatch('[0-9a-f]{40}', args.expected_git_sha) is not None, 'FULL_GIT_SHA_REQUIRED')
        source = no_links(absolute(args.source_root)).resolve(strict=True)
        manifest_path = absolute(args.source_manifest)
        raw = read_regular(manifest_path)
        require(sha(raw) == args.source_manifest_sha256, 'SOURCE_MANIFEST_SHA_MISMATCH')
        manifest = json.loads(raw)
        require(manifest.get('schemaVersion') == 1 and manifest.get('gitSHA') == args.expected_git_sha and manifest.get('entries'), 'SOURCE_MANIFEST_SCHEMA')
        entries = {}
        for row in manifest['entries']:
            v = PurePosixPath(row['path'])
            require(not v.is_absolute() and '..' not in v.parts and str(v) == row['path'] and row['path'] not in entries, 'UNSAFE_SOURCE_PATH')
            require(row.get('type', 'file') == 'file', 'SOURCE_LINK_EXPORT_NOT_SUPPORTED')
            entries[row['path']] = row
        git = no_links(absolute(args.git_path))
        require(git.is_file() and os.access(git, os.X_OK), 'GIT_EXECUTABLE_REQUIRED')
        g = Guard(args, [source, manifest_path])
        cache = no_links(absolute(args.cache_root))
        require(g.work in cache.parents and not os.path.lexists(cache) and cache != g.out, 'CACHE_MUST_BE_NEW_OWN_DESCENDANT')
        if args.execute:
            require(g.authority.get('allowNativeBuild') is True, 'NATIVE_BUILD_EXECUTION_NOT_AUTHORIZED')
            require(args.npm_path and args.uv_path, 'EXPLICIT_INSTALLER_PATHS_REQUIRED')
            for v in [args.npm_path, args.uv_path]:
                require(absolute(v).is_file() and os.access(v, os.X_OK), 'INSTALLER_EXECUTABLE_REQUIRED')
        g.begin()
        g.directory(cache)
        env = g.env('unused-build-db.sqlite')
        env.update({'npm_config_cache': str(cache/'npm'), 'UV_CACHE_DIR': str(cache/'uv'),
                    'ELECTRON_CACHE': str(cache/'electron'), 'ELECTRON_BUILDER_CACHE': str(cache/'electron-builder')})
        started = time.monotonic()
        runs = []
        def command(argv, tag):
            remaining = g.timeout - (time.monotonic()-started)
            require(remaining > 0, 'BUILD_TOTAL_TIMEOUT')
            result = run_child(g, argv, tag, env, remaining)
            runs.append(result[0])
            return result[1]
        actual = command([git, '-C', source, 'rev-parse', args.expected_git_sha+'^{commit}'], 'git-fixed-sha').decode().strip()
        require(actual == args.expected_git_sha, 'SOURCE_COMMIT_MISMATCH')
        tree = command([git, '-C', source, 'ls-tree', '-rz', '--full-tree', args.expected_git_sha], 'git-tree')
        paths = {}
        for item in tree.split(b'\0'):
            if not item:
                continue
            meta, name = item.split(b'\t', 1)
            mode, kind, blob = meta.decode().split(' ')
            require(kind == 'blob' and mode in ['100644', '100755'], 'UNSUPPORTED_SOURCE_OBJECT')
            paths[name.decode()] = '0o755' if mode == '100755' else '0o644'
        require(set(paths) == set(entries), 'SOURCE_TREE_SET_MISMATCH')
        require(all(entries[n]['mode'] == mode for n, mode in paths.items()), 'SOURCE_TREE_MODE_MISMATCH')
        for i, name in enumerate(sorted(entries)):
            data = command([git, '-C', source, 'show', args.expected_git_sha+':'+name], 'git-source-'+str(i))
            row = entries[name]
            require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'SOURCE_BLOB_HASH_MISMATCH')
        copy_root = g.work/'source-copy'
        plan = {'status': 'PLAN_ONLY', 'passed': False, 'notARebuildPass': True, 'expectedSHA': args.expected_git_sha,
                'source': str(source), 'sourceCopy': str(copy_root), 'output': str(g.out), 'cache': str(cache),
                'executeRequested': args.execute, 'installOrNetworkStarted': False, 'commands': runs,
                'futureBuildSteps': ['npm ci (copy only)', 'uv sync --frozen (copy only)', 'npm run typecheck', 'npm run package:dir', 'electron-builder --dir --publish never, own output'],
                'globalGitConfigDisabled': True, 'atomicSnapshotClaimed': False, 'OSHardBudgetClaimed': False}
        if args.execute:
            # This branch remains unexecuted in the owner-controlled validation window.
            archive = command([git, '-C', source, 'archive', '--format=tar', args.expected_git_sha], 'git-export')
            g.directory(copy_root)
            seen = set()
            with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as tf:
                for member in tf.getmembers():
                    rel = PurePosixPath(member.name)
                    require(not rel.is_absolute() and '..' not in rel.parts, 'ARCHIVE_PATH_ESCAPE')
                    if member.isdir():
                        g.directory(copy_root/str(rel))
                        continue
                    require(member.isfile() and member.name in entries and member.name not in seen, 'ARCHIVE_UNDECLARED_OR_LINK')
                    d = tf.extractfile(member).read()
                    row = entries[member.name]
                    require(len(d) == row['bytes'] and sha(d) == row['sha256'], 'SOURCE_EXPORT_HASH_MISMATCH')
                    with g.new(copy_root/member.name) as f:
                        f.write(d)
                        os.fchmod(f.fileno(), int(row['mode'], 8))
                    seen.add(member.name)
            require(seen == set(entries), 'ARCHIVE_SET_MISMATCH')
            # Install/build cwd must be the exported source copy, never source-root.
            def build_command(argv, tag, cwd=None):
                cwd = cwd or copy_root
                g.check(cwd)
                # run_child binds cwd to work; launch a trusted shim only to select own copy cwd.
                shim = [sys.executable, '-c', 'import os,sys; os.chdir(sys.argv[1]); os.execv(sys.argv[2],sys.argv[2:])', str(cwd), *[str(x) for x in argv]]
                return command(shim, tag)
            plan['installOrNetworkStarted'] = True
            build_command([args.npm_path, 'ci'], 'npm-ci')
            build_command([args.uv_path, 'sync', '--frozen'], 'uv-sync')
            build_command([args.npm_path, 'run', 'typecheck'], 'typecheck')
            build_command([args.npm_path, 'run', 'package:dir'], 'package-dir')
            builder = copy_root/'node_modules/.bin/electron-builder'
            build_command([builder, '--dir', '--publish', 'never', '--config.productName=OntoLearn Stage Acceptance 20261022',
                           '--config.appId=io.github.nomorejoke.ontolearnstudio.stageacceptance20261022',
                           '--config.extraMetadata.name=ontolearn-stage-acceptance-20261022',
                           '--config.extraMetadata.productName=OntoLearn Stage Acceptance 20261022',
                           '--config.directories.output='+str(g.out/'build-stage')], 'electron-builder', copy_root/'apps/desktop')
            plan['status'] = 'BUILD_COMMANDS_COMPLETED_NOT_GUI_RELEASE'
            plan['commands'] = runs
        plan['combinedScratchBytesAtEnd'] = g.sample()
        plan['sampledCombinedPeakBytes'] = g.peak
        g.write_json('native-rebuild-plan.json', plan)
        print(json.dumps({'status': plan['status'], 'result': str(g.out/'native-rebuild-plan.json'), 'notARebuildPass': True}))
        return 0
    except Exception as e:
        failure = {'passed': False, 'error': str(e), 'installOrNetworkStarted': False if not g or not g.started else 'see commands', 'notARebuildPass': True}
        if g and g.started:
            try:
                g.write_json('native-rebuild-failure.json', failure)
            except Exception as evidence_error:
                failure['failureEvidenceWriteError'] = str(evidence_error)
        print(json.dumps(failure), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(build_main())

PY_NATIVE_REBUILD
