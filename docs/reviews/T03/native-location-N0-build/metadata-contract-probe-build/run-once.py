"""Prepared single-build recorder. Do not invoke without root's separate authority.

This is neither an experiment runner nor a process/IO sandbox. It never invokes
its output executable. Leader exit and pipe EOF do not prove descendant drain.
"""
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

WORKSPACE = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build')
STAGE = WORKSPACE / 'docs/reviews/T03/native-location-N0-build/metadata-contract-probe-build'
SELF = STAGE / 'run-once.py'
PLAN = STAGE / 'call-plan.json'
AUTH = Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/T03-metadata-contract-probe-one-build-authorization.json')
PINS = STAGE / 'approved-identity-pins.json'
SOURCE = STAGE / 'inputs/location_metadata_contract_probe.cc.raw'
SOURCE_SHA = '6b6ff0969396c243c425dca507d0ea05732a0edb0123a264ab834cd2531690dd'
SOURCE_REF = '2b724f0188c233de5c8ef107d39fe0c4cb50311f'
COMPILER = '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++'
SDK = '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk'
INTERPRETER_REAL = '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
OUT_BASE = WORKSPACE / 'build/native-location/metadata-contract-probe/darwin-arm64'
CAP = 16 * 1024 * 1024
IDENTITY_CAP = 144 * 1024 * 1024
EVIDENCE_CAP = 48 * 1024 * 1024
PRIOR_USED = WORKSPACE / 'docs/reviews/T03/native-location-N0-build/host-core-build/sixth-acl-remedy-input-build/used-dependencies.json'
PRIOR_USED_SHA = 'c7a1c91c0d6cbb0e9f1daf087c79413c65973d5cc2c128b03a22c2196b2d3357'
CANCELLED = False
EMERGENCY_EMITTED = False
EMERGENCY_CAP = 65536
RAW_CAPTURE_CAP = CAP - EMERGENCY_CAP


class Stop(Exception):
    pass


class RecordFailure(Stop):
    def __init__(self, details):
        super().__init__('record-persistence-failure')
        self.details = details


class CaptureFailure(Stop):
    def __init__(self, details):
        super().__init__('command-stopped-no-retry')
        self.details = details


def error_info(exc):
    result = {'kind': str(exc)[:256] if isinstance(exc, Stop) else type(exc).__name__,
              'errno': getattr(exc, 'errno', None)}
    if isinstance(exc, (RecordFailure, CaptureFailure)):
        result['details'] = exc.details
    return result


def emergency(value):
    """One bounded stderr attempt; never truncates then claims completeness."""
    global EMERGENCY_EMITTED
    if EMERGENCY_EMITTED:
        return
    EMERGENCY_EMITTED = True
    raw = (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    if len(raw) > EMERGENCY_CAP:
        raw = (json.dumps({'status': 'EMERGENCY_CONTEXT_EXCEEDS_CAP',
                           'firstFailure': value.get('firstFailure'),
                           'fullContextUnavailable': True}, separators=(',', ':')) + '\n').encode()
    if len(raw) > EMERGENCY_CAP:
        raw = b'{"status":"EMERGENCY_UNAVAILABLE_CONTEXT_TOO_LARGE","complete":false}\n'
    try:
        os.write(2, raw)  # A short/error write is not retried or called complete.
    except BaseException:
        pass


def demand(condition, reason):
    if not condition:
        raise Stop(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path, cap):
    """No-follow bounded regular input; read and close errors stay separate."""
    fd = None
    result = None
    first = None
    cleanup = []
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
        before = os.fstat(fd)
        demand(stat.S_ISREG(before.st_mode) and before.st_size <= cap, 'input-type-or-size')
        pieces = []
        remaining = before.st_size
        while remaining:
            data = os.read(fd, min(65536, remaining))
            demand(bool(data), 'input-short-read')
            pieces.append(data)
            remaining -= len(data)
        after = os.fstat(fd)
        demand((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
               (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'input-changed')
        result = b''.join(pieces)
    except BaseException as exc:
        first = error_info(exc)
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except BaseException as exc:
                cleanup.append(error_info(exc))
    if first or cleanup:
        raise RecordFailure({'path': str(path), 'firstFailure': first, 'cleanupErrors': cleanup})
    return result


def write_once_bytes(path, raw, mode):
    demand(len(raw) <= 2 * 1024 * 1024, 'record-or-source-size-cap')
    fd = None
    first = None
    cleanup = []
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
        demand(stat.S_IMODE(os.fstat(fd).st_mode) == mode, 'record-or-source-mode')
        demand(os.write(fd, raw) == len(raw), 'record-short-write')
        os.fsync(fd)
    except BaseException as exc:
        first = error_info(exc)
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except BaseException as exc:
                cleanup.append(error_info(exc))
    if first or cleanup:
        raise RecordFailure({'path': str(path), 'firstFailure': first,
                             'cleanupErrors': cleanup, 'recordMayBePartial': True})


def write_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    write_once_bytes(path, raw, 0o600)


def signal_cancel(signum, frame):
    global CANCELLED
    CANCELLED = True


def identity_preflight(authorization, pin_raw, pin_document):
    """Only the finite accepted metadata set; reuse preparation payload hashes.

    Approval authenticates this manifest externally; this is not a hostile-host
    bootstrap attestation. No whole SDK, directory, or index enumeration.
    """
    descriptor_raw = bounded_read(STAGE / 'identity-descriptor-sum.json', 262144)
    demand(digest(descriptor_raw) == authorization['identityDescriptorSHA256'], 'identity-descriptor-authority')
    described = json.loads(descriptor_raw)
    allowed = {}
    for row in described['fixedToolsAndInterpreterRows'] + described['moduleRows']:
        if 'metadataError' not in row:
            allowed[row['path']] = row
    files = pin_document['files']
    demand(0 < len(files) <= 256, 'identity-record-cap')
    demand({x['path'] for x in files} == set(allowed), 'identity-set-mismatch')
    demand(len(files) == len({x['path'] for x in files}), 'identity-duplicates')
    unique = {}
    before_rows = []
    for row in files:
        expectation = allowed[row['path']]
        demand(row['realpath'] == expectation['realpath'] and row['bytes'] == expectation['bytes'], 'identity-descriptor-mismatch')
        demand(len(row['sha256']) == 64, 'identity-hash-missing')
        demand(os.path.realpath(row['path']) == row['realpath'], 'identity-realpath')
        st = os.stat(row['realpath'])
        demand(stat.S_ISREG(st.st_mode) and st.st_size == row['bytes'], 'identity-current-size')
        demand((row['device'], row['inode'], row['mtime_ns']) ==
               (expectation['device'], expectation['inode'], expectation['mtime_ns']), 'authenticated-identity-metadata-mismatch')
        demand((st.st_dev, st.st_ino, st.st_mtime_ns) ==
               (row['device'], row['inode'], row['mtime_ns']), 'identity-metadata-drift')
        key = (st.st_dev, st.st_ino)
        before_rows.append({'path': row['path'], 'realpath': row['realpath'], 'bytes': st.st_size,
                            'device': st.st_dev, 'inode': st.st_ino, 'mtime_ns': st.st_mtime_ns})
        if key in unique:
            demand(unique[key]['sha256'] == row['sha256'], 'alias-pin-conflict')
        else:
            unique[key] = row
    payload_sum = sum(x['bytes'] for x in unique.values())
    # Two MiB plus explicit source/helper bounds are reserved for control reads.
    demand(payload_sum + 20278 + 65536 + 2097152 <= IDENTITY_CAP, 'identity-read-ticket-insufficient')
    demand(authorization['identityReadCapBytes'] == IDENTITY_CAP, 'identity-authority-cap')
    demand(authorization['reusePreparedIdentityHashesMetadataOnly'] is True, 'prepared-hash-reuse-not-accepted')
    demand(pin_document['payloadHashesPerformedInPreparation'] is True, 'prepared-hashes-missing')
    demand(pin_document['payloadHashRepeatPermitted'] is False, 'identity-ticket-must-not-reset')
    demand(pin_document['distinctPayloadBytesHashed'] == payload_sum, 'prepared-identity-byte-total')
    # Current isolated imports must be a subset of the prepared finite candidates.
    demand(len(sys.modules) <= 512, 'interpreter-module-visit-bound')
    for module in tuple(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and path.startswith('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/'):
            demand(path in allowed, 'unprepared-interpreter-module')
    return {'preparedPhysicalPayloadBytesHashed': payload_sum, 'physicalPayloadBytesHashedThisRun': 0,
            'metadataOnlyReuseAcceptedByRoot': True, 'logicalAliases': len(files),
            'distinctPhysicalPayloads': len(unique), 'before': before_rows,
            'interpreterTransitiveDylibAndActualOpenClosure': 'PENDING_NOT_PROVEN'}


def stop_owned_leader(process, record):
    """Only this unreaped Popen instance; no group, descendant or old-PID kill."""
    for action, grace in [('terminate', 1.0), ('kill', 1.0)]:
        if process.poll() is not None:
            break
        event = {'action': action, 'pid': process.pid, 'attempted': True}
        record['ownedLeaderControl'].append(event)
        try:
            # Popen.send_signal checks its own returncode/waitpid identity.
            getattr(process, action)()
            event['signalCallReturned'] = True
        except OSError as exc:
            event['errno'] = exc.errno
        try:
            process.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            event['waitTimedOut'] = True
    record['leaderReturnCode'] = process.poll()
    record['descendantDrain'] = 'UNKNOWN_NO_DESCENDANT_OR_GROUP_PROBE'


def capture(argv, env, output, number, label, seconds, ledger):
    """Capture at producer pipes, one global cap for all six invocations.

    Reaching the cap is incomplete even if it might coincide with exact EOF.
    No lookahead byte, post-hoc truncation, discarded drain, or output retry.
    """
    global CANCELLED
    stem = '%02d-%s' % (number, label)
    stdout = output / (stem + '.stdout')
    stderr = output / (stem + '.stderr')
    record = {'index': number, 'label': label, 'argv': argv, 'cwd': str(output), 'environment': env,
              'stdout': str(stdout), 'stderr': str(stderr), 'captureRemainingAtStart': RAW_CAPTURE_CAP - ledger['capturedBytes'],
              'timeoutSeconds': seconds, 'phase': 'planned', 'dispatchAttempted': False, 'pid': None,
              'leaderReturnCode': None, 'firstFailure': None, 'ownedLeaderControl': [],
              'captureEOF': {'stdout': False, 'stderr': False}, 'descendantDrain': 'UNKNOWN_NOT_MEASURED'}
    write_json(output / (stem + '.planned.json'), record)
    fds = {}
    pipes = {}
    process = None
    sel = selectors.DefaultSelector()
    started = time.monotonic()
    try:
        for name, path in [('stdout', stdout), ('stderr', stderr)]:
            fds[name] = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            demand(stat.S_IMODE(os.fstat(fds[name]).st_mode) == 0o600, 'capture-file-mode')
        demand(not CANCELLED and ledger['capturedBytes'] < RAW_CAPTURE_CAP, 'cancelled-or-no-capture-budget')
        record['phase'] = 'dispatch-attempted'
        record['dispatchAttempted'] = True
        write_json(output / (stem + '.dispatch-attempted.json'), record)
        process = subprocess.Popen(argv, cwd=str(output), env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True,
                                   start_new_session=True)
        pipes = {'stdout': process.stdout, 'stderr': process.stderr}
        record['pid'] = process.pid
        record['phase'] = 'dispatched'
        write_json(output / (stem + '.dispatched.json'), record)
        for name, pipe in [('stdout', process.stdout), ('stderr', process.stderr)]:
            pipes[name] = pipe
            os.set_blocking(pipe.fileno(), False)
            sel.register(pipe, selectors.EVENT_READ, name)
        deadline = started + seconds
        while sel.get_map() or process.poll() is None:
            if CANCELLED:
                raise Stop('cancelled')
            if time.monotonic() >= deadline:
                raise Stop('timeout')
            demand(ledger['capturedBytes'] < RAW_CAPTURE_CAP, 'output-cap-reached')
            for key, events in sel.select(min(0.1, max(0.0, deadline - time.monotonic()))):
                remaining = RAW_CAPTURE_CAP - ledger['capturedBytes']
                demand(remaining > 0, 'output-cap-reached')
                try:
                    chunk = os.read(key.fileobj.fileno(), min(65536, remaining))
                except BlockingIOError:
                    continue
                if not chunk:
                    record['captureEOF'][key.data] = True
                    sel.unregister(key.fileobj)
                    continue
                ledger['capturedBytes'] += len(chunk)
                written = os.write(fds[key.data], chunk)
                demand(written == len(chunk), 'capture-short-write')
                if ledger['capturedBytes'] == RAW_CAPTURE_CAP:
                    raise Stop('output-cap-reached')
        record['leaderReturnCode'] = process.returncode
        demand(process.returncode == 0, 'command-nonzero-exit')
        demand(all(record['captureEOF'].values()), 'capture-eof-not-observed')
        record['phase'] = 'completed'
    except BaseException as exc:
        record['firstFailure'] = dict(error_info(exc), phase=record['phase'])
        record['phase'] = 'failed-or-unknown'
        if process is not None:
            try:
                stop_owned_leader(process, record)
            except BaseException as control_error:
                record['controlError'] = {'kind': type(control_error).__name__, 'errno': getattr(control_error, 'errno', None)}
    finally:
        try:
            sel.close()
        except OSError as exc:
            record.setdefault('closeErrors', []).append(exc.errno)
        for pipe in pipes.values():
            try:
                pipe.close()
            except OSError as exc:
                record.setdefault('closeErrors', []).append(exc.errno)
        for fd in fds.values():
            try:
                os.close(fd)
            except OSError as exc:
                record.setdefault('closeErrors', []).append(exc.errno)
        if record.get('closeErrors'):
            record['phase'] = 'failed-or-unknown'
            if record['firstFailure'] is None:
                record['firstFailure'] = {'kind': 'capture-close-error'}
        record['elapsedSeconds'] = time.monotonic() - started
        record['captureCombinedBytesAfter'] = ledger['capturedBytes']
        record['outputComplete'] = record['phase'] == 'completed'
        # Failure to persist terminal leaves earlier exclusive intent as evidence;
        # it never authorizes redispatch or directory reuse.
        try:
            write_json(output / (stem + '.terminal.json'), record)
        except BaseException as persist_error:
            record['terminalPersistenceError'] = error_info(persist_error)
            emergency({'status': 'TERMINAL_PERSISTENCE_FAILED', 'firstFailure': record['firstFailure'], 'commandRecord': record})
            raise CaptureFailure(record)
    if record['phase'] != 'completed' or record.get('closeErrors'):
        raise CaptureFailure(record)
    return record


def parse_deps(raw):
    colon = None
    escaped = False
    for i, char in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if char == '\\':
            escaped = True
            continue
        if char == ':':
            colon = i
            break
    demand(colon is not None, 'depfile-target-missing')
    text = raw[colon + 1:]
    words, part = [], []
    i = 0
    while i < len(text):
        char = text[i]
        if char == '\\' and i + 1 < len(text):
            if text[i + 1] == '\n':
                i += 2
                continue
            if text[i + 1] == '\r' and i + 2 < len(text) and text[i + 2] == '\n':
                i += 3
                continue
            part.append(text[i + 1])
            i += 2
            continue
        if char.isspace():
            if part:
                words.append(''.join(part))
                part = []
                demand(len(words) <= 3072, 'raw-dependency-cap')
            i += 1
            continue
        if char == '$' and i + 1 < len(text) and text[i + 1] == '$':
            part.append('$')
            i += 2
            continue
        part.append(char)
        i += 1
    if part:
        words.append(''.join(part))
    demand(len(words) <= 3072, 'raw-dependency-cap')
    return words


def dependency_receipt(output):
    raw = bounded_read(output / 'probe.d', 2097152)
    words = parse_deps(raw.decode('utf-8'))
    normalized = sorted({os.path.normpath(x if os.path.isabs(x) else str(output / x)) for x in words})
    demand(len(normalized) <= 1024, 'unique-dependency-cap')
    # Future root explicitly accepts this one bounded 3MiB witness read; no old
    # 205-file package, SDK inventory, or records-index body is opened here.
    oldraw = bounded_read(PRIOR_USED, 3156859)
    demand(len(oldraw) == 3156859 and digest(oldraw) == PRIOR_USED_SHA, 'prior-witness-pin')
    old = json.loads(oldraw)
    oldmap = {x['normalizedPath']: x for x in old['covered']}
    demand(len(oldmap) == 880, 'prior-witness-count')
    supplied_raw = bounded_read(STAGE / 'inputs/source-evidence.json.raw', 3621)
    demand(len(supplied_raw) == 3621 and digest(supplied_raw) == '5afb7c58d5154e7bd6083a5c7e7c273e15f4e6176e5f65c24758fa54a5ccb176', 'fixed-source-evidence-pin')
    supplied = json.loads(supplied_raw)
    direct = {x['path']: x for x in supplied['sdkAndReleaseEvidence'] if 'path' in x}
    entries, pending = [], []
    resource_prefix = '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/'
    for path in normalized:
        if path == str(output / 'input/location_metadata_contract_probe.cc'):
            entry = {'path': path, 'basis': 'frozen-single-source', 'sha256': SOURCE_SHA}
        elif (path.startswith(SDK + '/') or path.startswith(resource_prefix)) and path in oldmap:
            entry = {'path': path, 'basis': 'prior-approved-used-witness', 'witness': oldmap[path]['approvedWitness']}
        elif path in direct:
            entry = {'path': path, 'basis': 'root-accepted-I06-SDK-pin', 'pin': direct[path]}
        else:
            pending.append(path)
            entry = {'path': path, 'basis': 'PENDING_NEW_APPROVED_RECORD_AND_LOCATOR'}
        entries.append(entry)
    demand(len(pending) <= 64, 'new-dependency-record-cap')
    result = {'rawTokens': len(words), 'uniquePaths': len(normalized), 'depfileBytes': len(raw),
              'depfileSHA256': digest(raw), 'entries': entries, 'pendingNewPaths': pending,
              'currentHeaderPayloadRehashes': 0, 'newWholeIndexPasses': 0,
              'bindingIsNotCompilerOpenTrace': True,
              'closure': 'PENDING_EXACT_NEW_WITNESSES_AND_IDENTITY' if pending else 'REUSED_PIN_BINDINGS_ONLY_CURRENT_OPEN_AND_LINK_CLOSURE_PENDING'}
    write_json(output / 'dependency-receipt.json', result)
    return result


def artifact_pin(path):
    raw = bounded_read(path, 4194304)
    return {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}


def verify_sdk_metadata(plan):
    expected = plan['SDKRootMetadata']
    demand(os.path.realpath(SDK) == expected['realpath'], 'SDK-root-realpath-drift')
    st = os.stat(SDK)
    demand(stat.S_ISDIR(st.st_mode) and (st.st_dev, st.st_ino, st.st_mtime_ns) ==
           (expected['device'], expected['inode'], expected['mtime_ns']), 'SDK-root-metadata-drift')
    # This binds only root metadata, not current header payload/open identity.


def create_owned_output(token):
    """Only fixed dirfd components; retire each descriptor before close."""
    parent = None
    created = False
    first = None
    cleanup = []
    try:
        parent = os.open(str(WORKSPACE), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        for name in ['build', 'native-location', 'metadata-contract-probe', 'darwin-arm64']:
            try:
                os.mkdir(name, mode=0o700, dir_fd=parent)
            except FileExistsError:
                pass
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            old, parent = parent, child
            # old is retired even if close fails; never retry its number.
            os.close(old)
        os.mkdir(token, mode=0o700, dir_fd=parent)
        created = True
    except BaseException as exc:
        first = error_info(exc)
    finally:
        if parent is not None:
            old, parent = parent, None
            try:
                os.close(old)
            except BaseException as exc:
                cleanup.append(error_info(exc))
    problem = {'firstFailure': first, 'cleanupErrors': cleanup} if first or cleanup else None
    return (OUT_BASE / token if created else None), problem


def main():
    output = None
    try:
        demand(len(sys.argv) == 1, 'no-runner-arguments')
        demand(Path(__file__).absolute() == SELF, 'fixed-runner-entry')
        demand(os.path.realpath(sys.executable) == INTERPRETER_REAL, 'fixed-interpreter')
        demand(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, 'isolated-interpreter-required')
        # AUTH does not exist in preparation. It must be created by root in a
        # separate execution window; no dry-run/verify-only execution entry.
        auth_raw = bounded_read(AUTH, 65536)
        auth = json.loads(auth_raw)
        demand(auth['schema'] == 'T03_METADATA_PROBE_BUILD_AUTH_V1' and auth['authorized'] is True, 'no-build-authority')
        demand(auth['scope'] == 'ONE_COMPILE_AND_FIVE_STATIC_CHECKS_NO_EXPERIMENT_EXECUTION', 'wrong-authority-scope')
        demand(auth['sourceRef'] == SOURCE_REF and auth['sourceSHA256'] == SOURCE_SHA, 'source-authority')
        demand(auth['identityReallocationAccepted'] is True and auth['evidenceReadCapBytes'] == EVIDENCE_CAP, 'budget-authority')
        demand(auth['metadataCountingMethodApproved'] is True and
               auth['acceptedCountingPlanSHA256'] == auth['planSHA256'], 'cumulative-visit-counting-not-approved')
        demand(auth['preparedPreflightDebitUpper'] == 1000 and
               auth['futurePreflightVisitBound'] >= 1467 and
               auth['metadataPreflightCap'] >= 1000 + auth['futurePreflightVisitBound'], 'cumulative-preflight-ticket-not-approved')
        demand(auth['metadataDependencyVisitBound'] >= 8055 and
               auth['metadataDepsBindingCap'] >= auth['metadataDependencyVisitBound'], 'dependency-visit-ticket-not-approved')
        demand(auth['dependencyMode'] == 'CAPTURE_REUSE_PINNED_WITNESS_AND_DEFER_UNKNOWN_NO_INDEX_READ', 'dependency-method-not-accepted')
        plan_raw = bounded_read(PLAN, 65536)
        self_raw = bounded_read(SELF, 65536)
        pin_raw = bounded_read(PINS, 262144)
        demand(digest(plan_raw) == auth['planSHA256'] and digest(self_raw) == auth['runnerSHA256'] and digest(pin_raw) == auth['identityManifestSHA256'], 'authority-input-hash')
        plan = json.loads(plan_raw)
        demand(plan['compiler']['path'] == COMPILER and plan['SDKRoot'] == SDK and plan['outputBase'] == str(OUT_BASE), 'fixed-command-roots')
        expected_flags = ['-std=c++17', '-arch', 'arm64', '-isysroot', SDK, '-mmacosx-version-min=15.0', '-MD', '-MF', '@OUT@/probe.d', '-v', '@OUT@/input/location_metadata_contract_probe.cc', '-o', '@OUT@/artifacts/location_metadata_contract_probe']
        demand(plan['flags'] == expected_flags, 'fixed-compiler-flags')
        demand(plan['captureCombinedCapBytes'] == CAP and plan['source']['sha256'] == SOURCE_SHA, 'fixed-plan-limits')
        source_raw = bounded_read(SOURCE, 20278)
        demand(len(source_raw) == 20278 and digest(source_raw) == SOURCE_SHA, 'source-copy-pin')
        token = digest(auth_raw + plan_raw + self_raw + pin_raw)
        # Valid authority is one-shot even if subsequent metadata checks fail.
        write_json(STAGE / 'execution-attempt.json', {'authorizationSHA256': digest(auth_raw),
                   'inputProcessRef': auth['inputProcessRef'], 'token': token, 'dispatchAttempted': False,
                   'singleUseAcrossAuthorizationWhitespaceChanges': True})
        identities = identity_preflight(auth, pin_raw, json.loads(pin_raw))
        verify_sdk_metadata(plan)
        output, output_problem = create_owned_output(token)
        if output_problem:
            raise RecordFailure(dict(output_problem, path=str(OUT_BASE / token), outputCreated=output is not None))
        demand(output is not None, 'exclusive-output-not-owned')
        for name in ['input', 'artifacts', 'tmp']:
            (output / name).mkdir(mode=0o700, exist_ok=False)
        write_once_bytes(output / 'input/location_metadata_contract_probe.cc', source_raw, 0o400)
        write_json(output / 'build-intent.json', {'authorizationSHA256': digest(auth_raw), 'planSHA256': digest(plan_raw), 'runnerSHA256': digest(self_raw), 'identityManifestSHA256': digest(pin_raw), 'authorizationInputRef': auth['inputProcessRef'], 'output': str(output), 'noRetry': True, 'runtime': 'NOT_AUTHORIZED', 'sourceArgcIfLaterI06Runs': 1, 'applicationIdentity': identities})
        env = {'PATH': '/usr/bin:/bin', 'DEVELOPER_DIR': '/Applications/Xcode.app/Contents/Developer', 'LANG': 'C', 'LC_ALL': 'C', 'TMPDIR': str(output / 'tmp')}
        flags = [x.replace('@OUT@', str(output)) for x in expected_flags]
        argv = [COMPILER] + flags
        ledger = {'capturedBytes': 0}
        signal.signal(signal.SIGINT, signal_cancel)
        signal.signal(signal.SIGTERM, signal_cancel)
        capture(argv, env, output, 0, 'compile-link', 600, ledger)
        dependencies = dependency_receipt(output)
        product = output / 'artifacts/location_metadata_contract_probe'
        before = artifact_pin(product)
        write_json(output / 'artifact-before-static.json', before)
        # Fixed whitelist. Never execute product, including with old child argv.
        for i, (label, args) in enumerate([
            ('file-format', ['/usr/bin/file']),
            ('linked-libraries', ['/usr/bin/otool', '-L']),
            ('load-commands', ['/usr/bin/otool', '-l']),
            ('symbol-table', ['/usr/bin/nm', '-m']),
            ('undefined-symbols', ['/usr/bin/nm', '-u'])
        ], 1):
            capture(args + [str(product)], env, output, i, label, 30, ledger)
        after = artifact_pin(product)
        demand(before == after, 'artifact-changed-during-static-checks')
        # Final metadata comparison costs no second compiler payload hash.
        for row in identities['before']:
            demand(os.path.realpath(row['path']) == row['realpath'], 'post-tool-realpath-drift')
            st = os.stat(row['realpath'])
            demand((st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns) ==
                   (row['device'], row['inode'], row['bytes'], row['mtime_ns']), 'post-tool-metadata-drift')
        verify_sdk_metadata(plan)
        write_json(output / 'build-terminal.json', {'status': 'BUILT_UNVERIFIED_STATIC_STREAMS_CAPTURED', 'artifact': after,
                   'capturedCombinedBytes': ledger['capturedBytes'], 'compilerCalls': 1, 'staticCalls': 5,
                   'dependencyClosure': dependencies['closure'], 'pendingNewPaths': dependencies['pendingNewPaths'],
                   'actualSelectedLinkInputsClosure': 'PENDING_VERBOSE_AND_SYMBOL_REVIEW',
                   'descendantDrain': 'UNKNOWN_NOT_PROVEN_BY_LEADER_OR_EOF', 'experimentInvoked': False, 'runtime': 'NOT_RUN'})
        return 0
    except BaseException as exc:
        failure = {'status': 'FAILED_OR_UNKNOWN_NO_RETRY', 'firstFailure': error_info(exc),
                   'runtime': 'NOT_RUN', 'descendantDrain': 'UNKNOWN',
                   'outputRetained': output is not None}
        if output is not None:
            try:
                write_json(output / 'build-failure.json', failure)
            except BaseException as persist_error:
                failure['failurePersistenceError'] = error_info(persist_error)
        emergency(failure)
        return 1



if __name__ == '__main__':
    sys.exit(main())
