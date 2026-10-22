"""Prepared one-shot author check. An externally pinned root RUN_ONCE ticket is mandatory."""
import argparse
import datetime
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

ROOT = Path('/Users/kyle/Documents/工作/知爻/本体')
PLAN = ROOT / 'outputs/20261023_stage_review_c6/author-preflight/actual-build-once-plan'
WORK = ROOT / 'outputs/20261023_stage_review_c6/author-preflight/actual-build-once'
TICKET = ROOT / 'iteration-control/2026-10-21-weekly-release/.private/Stage-C6-actual-build-author-RUN_ONCE-ticket-20261023.json'
ISSUER = '01a154de-843b-7a00-8a80-51ba1c0aebce'
OWNER = '01a1628e-1220-7fb1-9135-97cbea4a3ed5'
FILES = ['author-browser-harness.py', 'authority.proposed.json',
         'runner-input.template.json', 'preparation-manifest.json']
SESSION = 'c6-author-actual-build-once-20261023'
LIMITS = dict(timeoutSeconds=180, combinedScratchBytes=67043328,
              capturedLogBytes=4161536, localBytes=64 * 1024 * 1024,
              samplingMs=100, terminationGraceSeconds=1, killReapUpperSeconds=5)
RUNNER = ROOT / 'outputs/20261023_stage_review_c6/runner-source/owned-browser-runner.mjs'
ACTUAL = ROOT / 'outputs/20261023_stage_review_c5/runtime/zcode/runs/browserbuild-a7077dfc6c474c958354d5be061aa6dc/out/index.html'
BUILD_REPORT = ACTUAL.parent / 'build-manifest.json'
BUILD_RECEIPT = ROOT / 'outputs/20261023_stage_review_c5/runtime/zcode/runs/launch-record-a7077dfc6c474c958354d5be061aa6dc/launch-receipt.json'
RO = Path('/Volumes/OntoLearn-Stage-C5-zcode-20261023/input')
SOURCE = RO / 'c3-input/subject/payload/artifacts/browser'
NODE = Path('/usr/local/bin/node')
MODULE = ROOT / 'outputs/20261022_stage_review_c3/resources/node_modules/playwright/index.mjs'
BROWSER = Path('/Users/kyle/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell')
COVERAGE = RO / 'coverage-required.json'
KNOWN = {
    str(RUNNER): (25942, '3df1fb5f79368d35707391c5ac9597901f30824010feaed5c8fd8e2af7a912c6'),
    str(ACTUAL): (523252, 'adff7f408e1844392d550a7e0a3bdacb5e1c1cd167b24d3b236a517456033a81'),
}
STOP_SIGNAL = None
REPORT_RESERVE_BYTES = 1024 * 1024  # Conservative logical space for checkpoint/final/refusal, inside original cap.


def require(value, reason):
    if not value:
        raise ValueError(reason)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(p, missing=False):
    p = Path(p)
    require(p.is_absolute() and os.path.normpath(str(p)) == str(p), 'NONCANONICAL_PATH')
    for ancestor in [*reversed(p.parents), p]:
        try:
            s = ancestor.lstat()
        except FileNotFoundError:
            require(missing, 'MISSING_PATH:' + str(ancestor))
            continue
        require(not stat.S_ISLNK(s.st_mode), 'SYMLINK_PATH:' + str(ancestor))
    return p


def read_identity(p, body=False):
    p = canonical(p)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                'ORDINARY_NLINK1_REQUIRED:' + str(p))
        h, chunks = hashlib.sha256(), []
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            h.update(chunk)
            if body:
                chunks.append(chunk)
        after = os.fstat(fd)
        names = ['st_dev', 'st_ino', 'st_size', 'st_mode', 'st_mtime_ns', 'st_nlink']
        require(all(getattr(before, k) == getattr(after, k) for k in names),
                'READ_CHANGED:' + str(p))
        current = p.lstat()
        require((current.st_dev, current.st_ino) == (before.st_dev, before.st_ino),
                'PATH_REPLACED:' + str(p))
        record = dict(path=str(p), bytes=after.st_size, sha256=h.hexdigest(),
                      dev=after.st_dev, ino=after.st_ino, mode=stat.S_IMODE(after.st_mode),
                      mtimeNs=after.st_mtime_ns)
        return record, b''.join(chunks) if body else None
    finally:
        os.close(fd)


def checked_json(p, sha):
    identity, raw = read_identity(p, True)
    require(identity['sha256'] == sha, 'PIN_MISMATCH:' + str(p))
    return json.loads(raw), identity


def exclusive_json(p, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    with Path(p).open('xb') as f:
        f.write(data)
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def budgeted_json(p, value, work_identity, final_commit=False):
    # Reserve is a conservative operating margin, never an increase to the root cap.
    occupied = scan_owned(work_identity)
    if final_commit:
        value['reportCommitPointUTC'] = utc()
        value['stopSignalAtCommit'] = STOP_SIGNAL
        if STOP_SIGNAL is not None:
            value['passed'] = False
            value['firstFailure'] = value.get('firstFailure') or ('HARNESS_SIGNAL_AT_COMMIT:' + str(STOP_SIGNAL))
    budget = dict(beforeWriteBytes=occupied, encodedReportBytes=0, projectedOwnedBytes=occupied,
                  capBytes=min(LIMITS['combinedScratchBytes'], LIMITS['localBytes']))
    value['reportWriteBudget'] = budget
    for _ in range(16):
        raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
        actual = len(raw)
        if budget['encodedReportBytes'] == actual:
            break
        budget['encodedReportBytes'] = actual
        budget['projectedOwnedBytes'] = occupied + actual
    else:
        raise ValueError('REPORT_SIZE_NOT_STABLE')
    require(budget['projectedOwnedBytes'] <= budget['capBytes'],
            'REPORT_BUDGET_REFUSED:' + str(budget['projectedOwnedBytes']))
    # The object is now fixed; this is its exact encoded byte count, including the budget record.
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    require(len(raw) == budget['encodedReportBytes'], 'REPORT_ENCODING_CHANGED')
    with Path(p).open('xb') as output:
        output.write(raw)
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                projectedOwnedBytes=budget['projectedOwnedBytes'])


def signal_requested(number, frame):
    global STOP_SIGNAL
    STOP_SIGNAL = number


def scan_owned(work_identity):
    canonical(WORK)
    s = WORK.lstat()
    require((s.st_dev, s.st_ino) == work_identity, 'WORK_REPLACED')
    def walk(folder):
        total = 0
        with os.scandir(folder) as entries:
            for entry in entries:
                try:
                    item = entry.stat(follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if stat.S_ISDIR(item.st_mode) and not stat.S_ISLNK(item.st_mode):
                    total += walk(Path(entry.path))
                else:
                    # Count owned temporary links/sockets as metadata only; never follow them.
                    total += item.st_size
        return total
    return walk(WORK)


def run_child(config_path, environment, work_identity):
    command = [str(NODE), str(RUNNER), str(config_path)]
    child, selector = None, selectors.DefaultSelector()
    streams, outputs = {}, {}
    received, stored = dict(stdout=0, stderr=0), dict(stdout=0, stderr=0)
    eof, signals, failures = set(), [], []
    sampler, sample_count, peak_owned = None, 0, 0
    sampler_complete = True
    start, began_utc = time.monotonic(), utc()
    first_failure, stop_at, exit_code, reaped = None, None, None, False
    term_sent, kill_sent, capture_write_failed = False, False, False
    pgid, ownership_unknown, capture_incomplete = None, False, False

    def fail(reason):
        nonlocal first_failure, stop_at
        if reason not in failures:
            failures.append(reason)
        if first_failure is None:
            first_failure, stop_at = reason, time.monotonic()

    def owned_signal(number):
        nonlocal ownership_unknown
        positive = False
        if child is not None and not reaped and child.returncode is None and pgid == child.pid:
            try:
                positive = os.getpgid(child.pid) == child.pid
            except OSError as exc:
                fail('OWNERSHIP_QUERY_FAILED:' + str(exc))
        if not positive:
            ownership_unknown = True
            signals.append(dict(atUTC=utc(), signal=number, sent=False,
                                ownership='UNKNOWN_NO_SIGNAL'))
            return
        try:
            os.killpg(pgid, number)
            signals.append(dict(atUTC=utc(), signal=number, sent=True,
                                pid=child.pid, pgid=pgid, ownership='OWN_UNREAPED_CHILD_GROUP'))
        except ProcessLookupError:
            signals.append(dict(atUTC=utc(), signal=number, sent=False,
                                ownership='OWN_GROUP_NO_LONGER_PRESENT'))
        except OSError as exc:
            ownership_unknown = True
            fail('OWN_SIGNAL_FAILED:' + str(exc))
            signals.append(dict(atUTC=utc(), signal=number, sent=False,
                                ownership='OWN_QUERY_POSITIVE_SIGNAL_ERROR', error=str(exc)))

    def try_wait(timeout):
        nonlocal reaped, exit_code, ownership_unknown
        try:
            exit_code = child.wait(timeout=timeout)
            reaped = True
            return True
        except subprocess.TimeoutExpired:
            return False
        except OSError as exc:
            ownership_unknown = True
            fail('OWN_WAIT_FAILED:' + str(exc))
            return False

    try:
        require(STOP_SIGNAL is None, 'CANCELLED_BEFORE_SPAWN')
        sampler = (WORK / 'sampler.jsonl').open('xb')
        for name in ['stdout', 'stderr']:
            outputs[name] = (WORK / ('child.' + name + '.log')).open('xb')
        child = subprocess.Popen(command, cwd=str(WORK), env=environment,
                                 shell=False, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 start_new_session=True)
        try:
            pgid = os.getpgid(child.pid)
            require(pgid == child.pid, 'NEW_OWN_PROCESS_GROUP_NOT_CONFIRMED')
        except Exception as exc:
            fail('OWNERSHIP_UNKNOWN:' + str(exc))
            ownership_unknown = True
        for name, stream in [('stdout', child.stdout), ('stderr', child.stderr)]:
            streams[name] = stream
            selector.register(stream, selectors.EVENT_READ, name)
        next_sample = start
        while True:
            now = time.monotonic()
            if STOP_SIGNAL is not None:
                fail('HARNESS_SIGNAL:' + str(STOP_SIGNAL))
            if now >= next_sample:
                try:
                    size = scan_owned(work_identity)
                    sample = dict(elapsedSeconds=now - start, localBytes=size, combinedOwnedBytes=size,
                                  logicalReportReserveBytes=REPORT_RESERVE_BYTES)
                    sampler.write((json.dumps(sample) + '\n').encode())
                    sampler.flush()
                    sample_count += 1
                    peak_owned = max(peak_owned, size)
                    if size + REPORT_RESERVE_BYTES > min(LIMITS['combinedScratchBytes'], LIMITS['localBytes']):
                        fail('SCRATCH_LIMIT_WITH_REPORT_RESERVE')
                except Exception as exc:
                    sampler_complete = False
                    fail('SCRATCH_OBSERVATION_FAILED:' + str(exc))
                next_sample = now + LIMITS['samplingMs'] / 1000
            if now - start > LIMITS['timeoutSeconds']:
                fail('TIME_LIMIT')
            if first_failure is not None:
                if not term_sent:
                    owned_signal(signal.SIGTERM)
                    term_sent = True
                if now - stop_at >= LIMITS['terminationGraceSeconds'] and not kill_sent:
                    owned_signal(signal.SIGKILL)
                    kill_sent = True
                if now - stop_at >= LIMITS['killReapUpperSeconds']:
                    capture_incomplete = len(eof) != 2
                    if not try_wait(0):
                        ownership_unknown = True
                        fail('DIRECT_CHILD_REAP_UNKNOWN')
                    break
            try:
                events = selector.select(0.1)
            except Exception as exc:
                fail('CAPTURE_SELECT_FAILED:' + str(exc))
                events = []
            for key, _ in events:
                name = key.data
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except Exception as exc:
                    fail('CAPTURE_READ_FAILED:' + str(exc))
                    capture_incomplete = True
                    selector.unregister(key.fileobj)
                    continue
                if not chunk:
                    eof.add(name)
                    selector.unregister(key.fileobj)
                    continue
                received[name] += len(chunk)
                room = max(0, LIMITS['capturedLogBytes'] - sum(stored.values()))
                prefix = chunk[:room]
                if prefix and not capture_write_failed:
                    try:
                        outputs[name].write(prefix)
                        outputs[name].flush()
                        stored[name] += len(prefix)
                    except Exception as exc:
                        capture_write_failed = True
                        capture_incomplete = True
                        fail('CAPTURE_WRITE_FAILED:' + str(exc))
                if sum(received.values()) > LIMITS['capturedLogBytes']:
                    capture_incomplete = True
                    fail('CAPTURE_LIMIT')
            # Do not poll/reap while inherited pipes still have unknown writers.
            if len(eof) == 2 and try_wait(0):
                break
    except BaseException as exc:
        fail('HARNESS_CHILD_PHASE_EXCEPTION:' + str(exc))
        capture_incomplete = True
    finally:
        # Unexpected parent errors still get the same finite, positively owned cleanup.
        if child is not None and not reaped:
            if stop_at is None:
                fail('UNSETTLED_DIRECT_CHILD')
            if not term_sent:
                owned_signal(signal.SIGTERM)
                term_sent = True
            deadline = stop_at + LIMITS['killReapUpperSeconds']
            while not reaped and time.monotonic() < deadline:
                if time.monotonic() - stop_at >= LIMITS['terminationGraceSeconds'] and not kill_sent:
                    owned_signal(signal.SIGKILL)
                    kill_sent = True
                if not try_wait(min(0.02, max(0, deadline - time.monotonic()))):
                    time.sleep(min(0.01, max(0, deadline - time.monotonic())))
            if not reaped:
                ownership_unknown = True
                fail('DIRECT_CHILD_REAP_UNKNOWN')
        try:
            selector.close()
        except Exception as exc:
            capture_incomplete = True
            fail('SELECTOR_CLOSE_FAILED:' + str(exc))
        for handle in [*streams.values(), *outputs.values()]:
            try:
                handle.close()
            except Exception as exc:
                capture_incomplete = True
                fail('OWN_HANDLE_CLOSE_FAILED:' + str(exc))
        if sampler is not None:
            try:
                sampler.close()
            except Exception as exc:
                sampler_complete = False
                fail('SAMPLER_CLOSE_FAILED:' + str(exc))
    if child is not None and exit_code not in (None, 0):
        fail('CHILD_NONZERO:' + str(exit_code))
    if len(eof) != 2:
        capture_incomplete = True
    raw = {}
    for name in ['stdout', 'stderr']:
        p = WORK / ('child.' + name + '.log')
        try:
            identity, _ = read_identity(p)
            raw[name] = dict(path=str(p), bytes=identity['bytes'], sha256=identity['sha256'],
                             bytesReceived=received[name], storedOriginalRange=[0, identity['bytes']],
                             eofObserved=name in eof,
                             complete=(name in eof and received[name] == identity['bytes']
                                       and not capture_write_failed))
        except Exception as exc:
            fail('RAW_CAPTURE_UNREADABLE:' + str(exc))
            capture_incomplete = True
            raw[name] = dict(path=str(p), bytes=None, sha256=None,
                             bytesReceived=received[name], complete=False, error=str(exc))
    if not all(raw[name].get('complete') is True for name in ['stdout', 'stderr']):
        capture_incomplete = True
        fail('RAW_STREAM_INCOMPLETE')
    try:
        sampler_identity, _ = read_identity(WORK / 'sampler.jsonl')
    except Exception as exc:
        sampler_identity = None
        sampler_complete = False
        fail('SAMPLER_UNREADABLE:' + str(exc))
    if not sampler_complete:
        fail('SAMPLER_INCOMPLETE')
    return dict(argv=command, cwd=str(WORK), environment=environment, startedAtUTC=began_utc,
                endedAtUTC=utc(), pid=child.pid if child else None, pgid=pgid,
                actualChildExit=exit_code, directChildReaped=reaped, signals=signals,
                ownershipUnknown=ownership_unknown, captureIncomplete=capture_incomplete,
                capture=raw, sampler=dict(identity=sampler_identity, count=sample_count,
                                         peakOwnedBytes=peak_owned, complete=sampler_complete),
                failures=failures, firstFailure=first_failure,
                forcedTerminationStarted=term_sent, limits=LIMITS,
                cleanupBoundary='Only this own process group. Escaped descendants UNKNOWN; '
                                'normal runner close and forced group cleanup are separate facts.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticket', required=True)
    parser.add_argument('--ticket-sha256', required=True)
    args = parser.parse_args()
    require(Path(__file__).absolute() == PLAN / FILES[0], 'EXACT_HARNESS_PATH_REQUIRED')
    require(Path(args.ticket) == TICKET, 'EXTERNAL_ROOT_TICKET_PATH_REQUIRED')
    require(len(args.ticket_sha256) == 64 and
            all(c in '0123456789abcdef' for c in args.ticket_sha256), 'TICKET_SHA_REQUIRED')
    ticket, ticket_identity = checked_json(TICKET, args.ticket_sha256)
    require(ticket.get('kind') == 'Stage-C6-actual-build-author-RUN_ONCE' and
            ticket.get('status') == 'RUN_ONCE' and ticket.get('maxRuns') == 1 and
            ticket.get('issuedByThreadId') == ISSUER and ticket.get('ownerThreadId') == OWNER and
            ticket.get('executionRoot') == str(WORK) and
            ticket.get('mode') == 'actual-build-once', 'ROOT_RUN_ONCE_NOT_GRANTED')
    require(ticket.get('limits') == LIMITS, 'ROOT_LIMITS_MISMATCH')
    pins = ticket.get('preparationFiles')
    require(isinstance(pins, list) and len(pins) == 4 and
            {x.get('path') for x in pins} == {str(PLAN / f) for f in FILES}, 'FOUR_EXACT_PREPARATION_PINS_REQUIRED')
    preparation_before = []
    for pin in pins:
        current, _ = read_identity(pin['path'])
        preparation_before.append(current)
        require(current['bytes'] == pin['bytes'] and current['sha256'] == pin['sha256'],
                'PREPARATION_DRIFT:' + pin['path'])
    authority, _ = checked_json(PLAN / FILES[1], next(x['sha256'] for x in pins if x['path'] == str(PLAN / FILES[1])))
    require(authority.get('status') == 'PROPOSED_NOT_RUNTIME_AUTHORIZATION' and
            authority.get('mode') == 'actual-build-once' and authority.get('executionRoot') == str(WORK)
            and authority.get('limits') == LIMITS, 'AUTHORITY_TEMPLATE_MISMATCH')
    config_identity, config_raw = read_identity(PLAN / FILES[2], True)
    config = json.loads(config_raw)
    require(config['work'] == str(WORK) and config['out'] == str(WORK / 'out') and
            config['module'] == str(MODULE) and config['browser'] == str(BROWSER) and
            config['index'] == str(ACTUAL) and config['session'] == SESSION, 'EXACT_ACTUAL_BUILD_CONFIG_REQUIRED')
    require(config_identity['sha256'] == authority['runnerInputTemplateSHA256'], 'INPUT_TEMPLATE_PIN_MISMATCH')
    coverage_identity, coverage_raw = read_identity(COVERAGE, True)
    require(coverage_identity['sha256'] == '60788383d78c26cdbd5e442349adb83aefe2c8bd8aaafdf9f616db1f5203e94a'
            and config['requiredCoverage'] == json.loads(coverage_raw), 'COMPLETE_COVERAGE_MISMATCH')
    source_manifest, source_identity = checked_json(SOURCE / 'manifest.json', authority['sourceManifestSHA256'])
    require(len(source_manifest.get('sources', [])) == 34, 'EXPECTED_34_SOURCES')
    source_paths = [SOURCE / 'entry.tsx', SOURCE / 'shell.css', SOURCE / 'index.html']
    for source in source_manifest['sources']:
        rel = Path(source['path'])
        require(not rel.is_absolute() and '..' not in rel.parts, 'SOURCE_RELATIVE_PATH_REQUIRED')
        source_paths.append(SOURCE / 'snapshot' / rel)
    permitted = {str(p) for p in [RUNNER, ACTUAL, BUILD_REPORT, BUILD_RECEIPT, COVERAGE,
                                  NODE, MODULE, BROWSER, SOURCE / 'manifest.json', *source_paths]}
    bindings = authority['bindings']
    require(len(bindings) == len(permitted) and {x['path'] for x in bindings} == permitted,
            'EXACT_SOURCE_RESOURCE_BINDINGS_REQUIRED')
    before = []
    for expected in bindings:
        current, _ = read_identity(expected['path'])
        require(current == expected, 'BOUND_INPUT_DRIFT:' + expected['path'])
        if current['path'] in KNOWN:
            require((current['bytes'], current['sha256']) == KNOWN[current['path']], 'FIXED_KNOWN_PIN_MISMATCH')
        before.append(current)
    require(os.access(NODE, os.X_OK) and os.access(BROWSER, os.X_OK), 'EXECUTABLE_UNAVAILABLE')
    build, _ = checked_json(BUILD_REPORT, authority['buildManifestSHA256'])
    receipt, _ = checked_json(BUILD_RECEIPT, authority['buildReceiptSHA256'])
    require(build.get('passed') is True and build.get('exit') == 0 and build.get('reason') is None
            and build.get('indexSha256') == KNOWN[str(ACTUAL)][1]
            and build.get('expectedIndexSha256') == KNOWN[str(ACTUAL)][1]
            and build.get('before') == build.get('after'), 'SUCCESSFUL_MATCHING_BUILD_REQUIRED')
    expected_build_paths = {str(SOURCE / 'manifest.json'), *map(str, source_paths)}
    require(isinstance(build.get('before'), list) and len(build['before']) == len(expected_build_paths)
            and {x['path'] for x in build['before']} == expected_build_paths,
            'BUILD_SOURCE_BINDING_SET_MISMATCH')
    current_by_path = {x['path']: x for x in before}
    for old in build['before']:
        current = current_by_path[old['path']]
        require(all(current[k] == old[k] for k in ['path', 'bytes', 'sha256', 'dev', 'ino', 'mode']),
                'BUILD_SOURCE_IDENTITY_DRIFT:' + old['path'])
    require(receipt.get('passed') is True and receipt.get('command') == 'browserBuild'
            and receipt.get('exitCode') == 0 and receipt.get('firstFailure') is None
            and receipt.get('workRoot') == str(ACTUAL.parent.parent), 'SUCCESSFUL_OWN_BUILD_RECEIPT_REQUIRED')
    canonical(WORK, True)
    require(not WORK.exists(), 'RUN_ALREADY_CONSUMED_OR_WORK_PRECREATED')
    require(STOP_SIGNAL is None, 'CANCELLED_BEFORE_WORK_CREATION')
    WORK.mkdir()  # Exclusive one-shot consumption; never remove or reuse this directory.
    work_stat = WORK.stat()
    work_identity = (work_stat.st_dev, work_stat.st_ino)
    exclusive_json(WORK / 'run-start.json', dict(startedAtUTC=utc(), authorPrevalidationId=SESSION,
                                              modelSID=None, ticket=ticket_identity,
                                              mode='actual-build-once', inputBefore=before))
    child = None
    try:
        for folder in ['out', 'tmp', 'cache', 'config', 'traces', 'downloads']:
            (WORK / folder).mkdir()
        config_path = WORK / 'runner-input.json'
        with config_path.open('xb') as f:
            f.write(config_raw)
        require(read_identity(config_path)[0]['sha256'] == config_identity['sha256'], 'ACTUAL_CONFIG_DRIFT')
        environment = dict(PATH='/usr/local/bin:/usr/bin:/bin', TMPDIR=str(WORK / 'tmp'),
                           TMP=str(WORK / 'tmp'), TEMP=str(WORK / 'tmp'),
                           XDG_CACHE_HOME=str(WORK / 'cache'), XDG_CONFIG_HOME=str(WORK / 'config'),
                           NO_COLOR='1')
        signal.signal(signal.SIGTERM, signal_requested)
        signal.signal(signal.SIGINT, signal_requested)
        child = run_child(config_path, environment, work_identity)
        budgeted_json(WORK / 'child-state.json', child, work_identity)
        post, post_failures, preparation_after = [], [], []
        if STOP_SIGNAL is not None:
            post_failures.append('HARNESS_SIGNAL_AFTER_CHILD:' + str(STOP_SIGNAL))
        try:
            final_size = scan_owned(work_identity)
            child['tailScratchObservation'] = dict(atUTC=utc(), phase='after-child-checkpoint',
                                                  localBytes=final_size, combinedOwnedBytes=final_size)
            if final_size > LIMITS['combinedScratchBytes'] or final_size > LIMITS['localBytes']:
                post_failures.append('FINAL_SCRATCH_LIMIT')
        except Exception as exc:
            post_failures.append('FINAL_SCRATCH_UNVERIFIED:' + str(exc))
        for expected in before:
            try:
                current, _ = read_identity(expected['path'])
                post.append(current)
                if current != expected:
                    post_failures.append('POST_INPUT_DRIFT:' + expected['path'])
            except Exception as exc:
                post_failures.append('POST_INPUT_UNREADABLE:' + str(exc))
        for expected in [*preparation_before, ticket_identity]:
            try:
                current, _ = read_identity(expected['path'])
                preparation_after.append(current)
                if current != expected:
                    post_failures.append('POST_PREPARATION_OR_TICKET_DRIFT:' + expected['path'])
            except Exception as exc:
                post_failures.append('POST_PREPARATION_OR_TICKET_UNREADABLE:' + str(exc))
        try:
            if read_identity(config_path)[0]['sha256'] != config_identity['sha256']:
                post_failures.append('POST_ACTUAL_CONFIG_DRIFT')
        except Exception as exc:
            post_failures.append('POST_ACTUAL_CONFIG_UNREADABLE:' + str(exc))
        try:
            raw_result_identity, raw_result_bytes = read_identity(WORK / 'out/browser-result.json', True)
            result = json.loads(raw_result_bytes)
        except Exception as exc:
            raw_result_identity, result = None, None
            post_failures.append('BROWSER_RESULT_MISSING_OR_INVALID:' + str(exc))
        url = ACTUAL.as_uri()
        launches = [x for x in (result or {}).get('results', []) if x.get('name') == 'owned-launch']
        actual_url = launches[0].get('url') if len(launches) == 1 else None
        if actual_url != url:
            post_failures.append('ACTUAL_BUILD_URL_NOT_CONFIRMED')
        normal_close = bool(result and result.get('ownedClosed') is True
                            and result.get('onlyOwnObjectsClosed') is True)
        raw_coverage = (result or {}).get('coverage')
        coverage_pass = bool(isinstance(raw_coverage, dict) and raw_coverage.get('passed') is True
                             and raw_coverage.get('mandatoryUnverified') == [])
        if STOP_SIGNAL is not None:
            post_failures.append('HARNESS_SIGNAL_BEFORE_DECISION:' + str(STOP_SIGNAL))
        passed = (child['actualChildExit'] == 0 and child['directChildReaped']
                  and not child['ownershipUnknown'] and not child['captureIncomplete']
                  and child['firstFailure'] is None and not post_failures
                  and child['sampler']['complete'] is True
                  and all(child['capture'][name].get('complete') is True for name in ['stdout', 'stderr'])
                  and not child['forcedTerminationStarted'] and normal_close and coverage_pass
                  and result.get('passed') is True and result.get('requests') == []
                  and result.get('errors') == [])
        failure = child['firstFailure'] or (result or {}).get('firstFailure')
        if not failure and post_failures:
            failure = post_failures[0]
        if not passed and not failure:
            failure = 'REQUIRED_SUCCESS_OR_NORMAL_CLEANUP_UNVERIFIED'
        final = dict(passed=passed, firstFailure=failure, postFailures=post_failures,
                     runnerFirstFailure=(result or {}).get('firstFailure'),
                     authorOnlyNotDesignatedReview=True, authorPrevalidationId=SESSION,
                     finishedAtUTC=utc(), ticket=ticket_identity, child=child,
                     inputBefore=before, inputAfter=post, preparationBefore=preparation_before,
                     preparationAndTicketAfter=preparation_after, configSHA256=config_identity['sha256'],
                     expectedActualBuildURL=url, observedActualBuildURL=actual_url,
                     rawBrowserResultIdentity=raw_result_identity, rawCoverage=raw_coverage,
                     recordedActions=[x.get('name') for x in (result or {}).get('results', [])],
                     normalRunnerOwnedCloseReported=normal_close,
                     forcedCleanupNotNormalClose=child['forcedTerminationStarted'],
                     escapedDescendants='UNKNOWN_NOT_CLAIMED',
                     noRetryOrNextAuthorRunUnlessRootResolvesFailure=True,
                     resourceLimits='Soft sampling of new own work only; not OS hard quota or whole descendant proof.')
        final_identity = budgeted_json(WORK / 'harness-result.json', final, work_identity, final_commit=True)
        passed, failure = final['passed'], final['firstFailure']
        print(json.dumps(dict(passed=passed, firstFailure=failure, childExit=child['actualChildExit'],
                              result=str(WORK / 'harness-result.json'), resultIdentity=final_identity)))
        return 0 if passed else 1
    except BaseException as exc:
        minimal = dict(passed=False, firstFailure=str(exc), atUTC=utc(), noRetry=True,
                       childFacts={k: child.get(k) for k in ['pid', 'pgid', 'actualChildExit',
                                   'directChildReaped', 'ownershipUnknown', 'firstFailure']} if child else None,
                       childCheckpoint=str(WORK / 'child-state.json'),
                       cleanup='Raw logs/sampler retained; missing evidence remains UNKNOWN')
        try:
            budgeted_json(WORK / 'harness-exception.json', minimal, work_identity)
        except Exception as record_error:
            minimal['refusalRecordNotWritten'] = str(record_error)
        print(json.dumps(minimal), file=sys.stderr)
        raise


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps(dict(passed=False, firstFailure=str(error), noRetry=True)), file=sys.stderr)
        sys.exit(1)
