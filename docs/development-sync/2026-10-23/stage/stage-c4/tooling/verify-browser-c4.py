"""Owned-process, offline browser acceptance. All writes are under a fresh owner-authorized run."""
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


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value, missing=False):
    p = Path(value)
    require(p.is_absolute() and os.path.normpath(value) == value, 'CANONICAL_ABSOLUTE_PATH_REQUIRED')
    for q in [*reversed(p.parents), p]:
        try:
            s = q.lstat()
        except FileNotFoundError:
            require(missing, 'MISSING_PATH: ' + str(q))
            continue
        require(not stat.S_ISLNK(s.st_mode), 'SYMLINK_PATH: ' + str(q))
    if p.exists():
        require(str(p.resolve()) == value, 'PATH_ALIAS')
    return p


def within(a, b):
    return a == b or b in a.parents


def regular(p):
    canonical(str(p))
    s = p.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'REGULAR_UNLINKED_INPUT_REQUIRED')
    return s


def identity(p):
    s = regular(p)
    return dict(path=str(p), bytes=s.st_size, mode=stat.S_IMODE(s.st_mode), dev=s.st_dev,
                ino=s.st_ino, sha256=digest(p.read_bytes()))


def load_checked(p, expected):
    regular(p)
    data = p.read_bytes()
    require(len(expected) == 64 and digest(data) == expected, 'INPUT_SHA_MISMATCH')
    return json.loads(data)


def size(root, strict=False):
    total = 0
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                try:
                    info = entry.stat(follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
                    total += size(Path(entry.path), strict)
                else:
                    total += info.st_size
    except FileNotFoundError:
        return 0
    return total


def logs_size(root):
    total = 0
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                try:
                    info = entry.stat(follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
                    total += logs_size(Path(entry.path))
                elif entry.name.endswith(('.stdout.log', '.stderr.log')):
                    total += info.st_size
    except FileNotFoundError:
        return 0
    return total




def main():
    parser = argparse.ArgumentParser()
    for name in ['authority', 'authority-sha256', 'input-root', 'input-manifest',
                 'input-manifest-sha256', 'work-root', 'output-root', 'node',
                 'playwright-module', 'browser', 'session', 'runner', 'runner-sha256',
                 'coverage', 'coverage-sha256']:
        parser.add_argument('--' + name, required=True)
    args = vars(parser.parse_args())
    authority_path = canonical(args['authority'])
    authority = load_checked(authority_path, args['authority_sha256'])
    require(authority.get('schemaVersion') == 1 and authority.get('protectedRoots'), 'AUTHORITY_SCHEMA')
    limits = authority['limits']
    for key in ['combinedScratchBytes', 'capturedLogBytes', 'browserTimeoutSeconds']:
        require(isinstance(limits.get(key), int) and limits[key] > 0, 'AUTHORITY_LIMITS')
    base = canonical(authority['allowedRunBase'])
    source = canonical(args['input_root'])
    manifest_path = canonical(args['input_manifest'])
    require(within(manifest_path, source), 'MANIFEST_OUTSIDE_INPUT')
    manifest = load_checked(manifest_path, args['input_manifest_sha256'])
    work = canonical(args['work_root'], True)
    output = canonical(args['output_root'], True)
    require(work.parent == base and output.parent == work and not work.exists()
            and not output.exists(), 'NEW_DIRECT_RUN_AND_OUTPUT_REQUIRED')
    require(args['session'] == work.name and all(c.isalnum() or c in '-_' for c in args['session']),
            'SESSION_MUST_BE_FRESH_RUN_IDENTIFIER')
    dependencies = [canonical(args[x]) for x in ['node', 'playwright_module', 'browser']]
    for p in dependencies:
        regular(p)
    require(os.access(dependencies[0], os.X_OK) and os.access(dependencies[2], os.X_OK),
            'EXECUTABLE_UNAVAILABLE')
    protected = [canonical(x) for x in authority['protectedRoots']]
    protected += [source, manifest_path, authority_path, *dependencies]
    for p in protected:
        require(not (within(work, p) or within(p, work) or within(output, p) or within(p, output)),
                'PROTECTED_PATH_OVERLAP')
        ps = p.stat()
        for q in work.parent.parents:
            qs = q.stat()
            require((ps.st_dev, ps.st_ino) != (qs.st_dev, qs.st_ino), 'PROTECTED_ANCESTOR_ALIAS')
    require(len(manifest.get('sources', [])) == 34, 'EXPECTED_34_SOURCES')
    records = [identity(manifest_path)]
    entries = [('index.html', manifest['build']['indexSha256'], None),
               ('entry.tsx', manifest['build']['entrySha256'], None),
               ('shell.css', manifest['build']['cssSha256'], None)]
    entries += [('snapshot/' + x['path'], x['sha256'], x['bytes']) for x in manifest['sources']]
    seen = set()
    for rel, expected, expected_bytes in entries:
        require(not Path(rel).is_absolute() and '..' not in Path(rel).parts and rel not in seen,
                'SOURCE_PATH_INVALID')
        seen.add(rel)
        record = identity(source / rel)
        require(record['sha256'] == expected and (expected_bytes is None or record['bytes'] == expected_bytes),
                'SOURCE_IDENTITY_MISMATCH: ' + rel)
        records.append(record)
    deps_before = [identity(x) for x in dependencies]
    require(size(base) < limits['combinedScratchBytes'], 'COMBINED_SCRATCH_LIMIT')
    runner = canonical(args['runner'])
    coverage_path = canonical(args['coverage'])
    authority_root = Path(__file__).absolute().parent.parent
    require(runner == authority_root / 'tooling/owned-browser-runner.mjs' and
            coverage_path == authority_root / 'coverage-required.json', 'FIXED_READONLY_RUNNER_REQUIRED')
    require(bool(os.statvfs(runner.parent).f_flag & os.ST_RDONLY), 'RUNNER_VOLUME_NOT_READONLY')
    require(identity(runner)['sha256'] == args['runner_sha256'], 'RUNNER_SHA_MISMATCH')
    coverage = load_checked(coverage_path, args['coverage_sha256'])
    records += [identity(runner), identity(coverage_path)]
    work.mkdir()
    work_id = work.stat()
    output.mkdir()
    for name in ['tmp', 'cache', 'config', 'traces']:
        (work / name).mkdir()
    config = work / 'runner-input.json'
    config.write_text(json.dumps(dict(work=str(work), out=str(output), module=str(dependencies[1]),
                                     browser=str(dependencies[2]), index=str(source / 'index.html'),
                                     session=args['session'], requiredCoverage=coverage)))
    command = [str(dependencies[0]), str(runner), str(config)]
    env = {'PATH': str(dependencies[0].parent), 'TMPDIR': str(work / 'tmp'),
           'TMP': str(work / 'tmp'), 'TEMP': str(work / 'tmp'),
           'XDG_CACHE_HOME': str(work / 'cache'), 'XDG_CONFIG_HOME': str(work / 'config'),
           'NO_COLOR': '1'}
    start = time.monotonic()
    samples, reason, captured = [], None, 0
    child = subprocess.Popen(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    selector = selectors.DefaultSelector()
    stdout = (work / 'child.stdout.log').open('xb')
    stderr = (work / 'child.stderr.log').open('xb')
    selector.register(child.stdout, selectors.EVENT_READ, stdout)
    selector.register(child.stderr, selectors.EVENT_READ, stderr)
    terminated_at = None
    try:
        while selector.get_map() or child.poll() is None:
            for key, _ in selector.select(0.1):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                room = max(0, limits['capturedLogBytes'] - captured)
                key.data.write(chunk[:room])
                key.data.flush()
                captured += len(chunk)
            try:
                canonical(str(work))
                s = work.stat()
                require((s.st_dev, s.st_ino) == (work_id.st_dev, work_id.st_ino), 'WORK_REPLACED')
                total, local = size(base), size(work)
                elapsed = time.monotonic() - start
                samples.append(dict(elapsedSeconds=elapsed, combinedBytes=total, localBytes=local))
                if total > limits['combinedScratchBytes'] or local > 64 * 1024 * 1024:
                    reason = reason or 'SCRATCH_LIMIT'
                if elapsed > limits['browserTimeoutSeconds']:
                    reason = reason or 'TIME_LIMIT'
                if captured > limits['capturedLogBytes'] or logs_size(base) > limits['capturedLogBytes']:
                    reason = reason or 'LOG_LIMIT'
            except Exception as exc:
                reason = reason or str(exc)
            if reason and terminated_at is None:
                terminated_at = time.monotonic()
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            if terminated_at is not None and time.monotonic() - terminated_at > 1:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if terminated_at is not None and time.monotonic() - terminated_at > 4:
                reason += '; pipe/process cleanup not confirmed'
                break
    finally:
        selector.close()
        stdout.close()
        stderr.close()
    try:
        exit_code = child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        exit_code = child.wait(timeout=2)
    after = [identity(Path(x['path'])) for x in records]
    require(records == after, 'SOURCE_CHANGED')
    deps_after = [identity(x) for x in dependencies]
    require(deps_before == deps_after, 'DEPENDENCY_CHANGED')
    result_path = output / 'browser-result.json'
    result = json.loads(result_path.read_text()) if result_path.is_file() else None
    report = dict(tool='verify-browser', argv=sys.argv, cwd=os.getcwd(), childArgv=command,
                  childCwd=str(work), exit=exit_code, reason=reason,
                  passed=exit_code == 0 and reason is None and bool(result and result['passed']),
                  firstFailure=reason or (result or {}).get('firstFailure'), before=records, after=after,
                  dependencyIdentity=deps_before, dependencyAfter=deps_after, authoritySHA256=args['authority_sha256'],
                  samples=samples, peakCombinedBytes=max((s['combinedBytes'] for s in samples), default=0),
                  peakLocalBytes=max((s['localBytes'] for s in samples), default=0),
                  combinedBytesAfter=size(base), capturedLogBytes=captured,
                  limitsAreSamplingNotOSHardLimits=True,
                  cleanup='own process group only; normal browser close recorded in browser-result; '
                          'forced termination does not prove all descendants cleaned')
    with (output / 'launcher-report.json').open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    coverage_result = (result or {}).get('coverage', {})
    require(coverage_result.get('passed') is True and coverage_result.get('mandatoryUnverified') == [], 'MANDATORY_COVERAGE_UNVERIFIED')
    print(json.dumps(dict(passed=report['passed'], exit=exit_code, reason=report['firstFailure'],
                          report=str(output / 'launcher-report.json'))))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('VERIFY_REFUSED_OR_FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
