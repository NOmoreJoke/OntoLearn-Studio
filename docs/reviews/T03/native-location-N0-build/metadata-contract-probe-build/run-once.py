"""Prepared single-build recorder. Do not invoke without root's separate authority.

This is neither an experiment runner nor a process/IO sandbox. It never invokes
its output executable. Leader exit and pipe EOF do not prove descendant drain.
"""
import hashlib
import json
import os
from pathlib import Path
import selectors
import re
import signal
import stat
import subprocess
import sys
import time

WORKSPACE = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build')
STAGE = WORKSPACE / 'docs/reviews/T03/native-location-N0-build/metadata-contract-probe-build'
SELF = STAGE / 'run-once.py'
PLAN = STAGE / 'call-plan.json'
METER_PLAN = STAGE / 'meter-plan.json'
HISTORY = STAGE / 'meter-history.json'
REVIEW_METHOD = STAGE / 'meter-forward-binding/review-methods/method-plan.json'
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
PREPARED_IDENTITY_CAP = 144 * 1024 * 1024
PRIOR_USED = WORKSPACE / 'docs/reviews/T03/native-location-N0-build/host-core-build/sixth-acl-remedy-input-build/used-dependencies.json'
PRIOR_USED_SHA = 'c7a1c91c0d6cbb0e9f1daf087c79413c65973d5cc2c128b03a22c2196b2d3357'
CANCELLED = False
EMERGENCY_EMITTED = False
EMERGENCY_CAP = 65536
RAW_CAPTURE_CAP = CAP - EMERGENCY_CAP


class Stop(Exception):
    pass


# Fresh future invocation budgets; no historical preparation ticket is reused.
# Whole phases are prepaid before constrained access; unused fee is never refunded.
METER = None
BYTE_METER = None


class MeterLimit(Stop):
    pass


class PhaseMeter:
    LIMIT = 167000

    def __init__(self):
        self.reserved = 3000  # Emergency is reserved before any input access.
        self.used_upper = 0
        self.prepaid_pre = False
        self.prepaid_dep = False
        self.prepaid_ctl = False
        self.pre_used = 0
        self.dep_used = 0
        self.ctl_used = 0
        self.err_used = 0
        self.active = 'emergency'

    def enter(self, phase):
        if phase == 'preflight':
            if not self.prepaid_pre:
                self.reserved += 42000
                self.prepaid_pre = True
        elif phase == 'dependency':
            if not self.prepaid_dep:
                self.reserved += 62000
                self.prepaid_dep = True
        elif phase == 'control':
            if not self.prepaid_ctl:
                self.reserved += 60000
                self.prepaid_ctl = True
        elif phase != 'emergency':
            raise MeterLimit('unknown-meter-phase')
        if self.reserved > self.LIMIT:
            raise MeterLimit('master-reservation-cap')
        self.active = phase

    def work(self, units):
        if not isinstance(units, int) or units < 0:
            raise MeterLimit('invalid-meter-debit')
        # Only fixed scalar fields: no iteration of records or meter history.
        if self.active == 'preflight':
            if units > 42000 - self.pre_used:
                raise MeterLimit('preflight-work-bound')
            self.pre_used += units
        elif self.active == 'dependency':
            if units > 62000 - self.dep_used:
                raise MeterLimit('dependency-work-bound')
            self.dep_used += units
        elif self.active == 'control':
            if units > 60000 - self.ctl_used:
                raise MeterLimit('control-work-bound')
            self.ctl_used += units
        elif self.active == 'emergency':
            if units > 3000 - self.err_used:
                raise MeterLimit('emergency-work-bound')
            self.err_used += units
        else:
            raise MeterLimit('meter-not-active')
        self.used_upper += units

    def snapshot(self):
        # Construction is included in each record's prepaid JSON fee.
        return {'limit': self.LIMIT, 'phaseReserved': self.reserved,
                'upperWorkDebits': self.used_upper, 'phase': self.active,
                'preReserved': self.prepaid_pre, 'depReserved': self.prepaid_dep,
                'controlReserved': self.prepaid_ctl, 'emergencyReserved': True,
                'preUpper': self.pre_used, 'depUpper': self.dep_used,
                'controlUpper': self.ctl_used, 'emergencyUpper': self.err_used,
                'actualLogicalVisits': None, 'noRefund': True,
                'inputBytesReserved': BYTE_METER.inputs,
                'recordBytesReserved': BYTE_METER.outputs,
                'artifactBytesReserved': BYTE_METER.artifacts,
                'captureBytesReserved': BYTE_METER.capture}


class CaptureBytes:
    def __init__(self):
        self.captured_bytes = 0
        self.select_calls = 0
        self.loop_checks = 0


class ByteMeter:
    # Runtime40MiB, independent owner closure52MiB, each peer36MiB.
    # Total164MiB proposal; none is borrowed from historical preparation.
    def __init__(self):
        self.inputs = 0
        self.outputs = 0
        self.artifacts = 0
        self.capture = 0

    def reserve(self, size, role):
        if not isinstance(size, int) or size < 0:
            raise MeterLimit('invalid-byte-debit')
        if role == 'input':
            if size > 8388608 - self.inputs:
                raise MeterLimit('input-byte-cap')
            self.inputs += size
        elif role == 'output':
            if size > 8388608 - self.outputs:
                raise MeterLimit('record-output-byte-cap')
            self.outputs += size
        elif role == 'artifact':
            if size > 8388608 - self.artifacts:
                raise MeterLimit('artifact-byte-cap')
            self.artifacts += size
        elif role == 'capture':
            if self.capture:
                return
            if size != CAP:
                raise MeterLimit('capture-reservation-shape')
            self.capture = CAP
        else:
            raise MeterLimit('unknown-byte-role')


def json_shape(raw, unit_cap):
    """Bounded packed scalar state; caller prepaid before character decoding."""
    text = raw.decode('utf-8')
    units = steps = depth = array_bits = pending_bits = 0
    quoted = escaped = bare = False
    step_cap = 4 * unit_cap + 8
    for c in text:
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
            continue
        if bare:
            if c not in '\"{}[],: \t\r\n': continue
            bare = False
        if c.isspace(): continue
        demand(steps < step_cap, 'json-structural-action-cap-before-state')
        steps += 1
        # Only a value start can create an array-member unit. Punctuation
        # also consumes an action before looking at packed scalar state.
        if c not in '}],:' and depth and array_bits & 1 and pending_bits & 1:
            demand(units < unit_cap, 'json-unit-cap-before-array-member')
            units += 1
            pending_bits &= ~1
        if c == '"': quoted = True
        elif c in '{[':
            demand(units < unit_cap, 'json-unit-cap-before-container')
            units += 1
            demand(depth < 12, 'json-depth-before-state')
            array_bits = (array_bits << 1) | (c == '[')
            pending_bits = (pending_bits << 1) | (c == '[')
            depth += 1
        elif c in '}]':
            demand(depth > 0 and bool(array_bits & 1) == (c == ']'), 'json-container-shape')
            array_bits >>= 1; pending_bits >>= 1; depth -= 1
        elif c == ':':
            demand(units < unit_cap, 'json-unit-cap-before-field')
            units += 1
        elif c == ',':
            if depth and array_bits & 1: pending_bits |= 1
        else: bare = True
    demand(not quoted and depth == 0, 'json-incomplete-shape')
    return units, steps


def decode_metadata(raw, unit_cap):
    METER.work(16)  # Admission/type/fee checks, before any raw access.
    demand(type(unit_cap) is int and unit_cap >= 0, 'json-unit-cap-type')
    METER.work(8 * unit_cap + 80)  # Native3U+8 plus structure5U+72, before scan.
    units, steps = json_shape(raw, unit_cap)
    return json.loads(raw)


def read_metadata(path, byte_cap, unit_cap):
    return decode_metadata(bounded_read(path, byte_cap), unit_cap)


def encode_metadata(value, unit_cap, byte_cap):
    """Own bounded container encoder; json.dumps sees scalar values only.

    Caller prepays 3*unit_cap before snapshot/construction or any traversal.
    No generic prewalk followed by an uncharged second container-library pass.
    """
    fragments = []
    units = 0
    byte_count = 0

    def emit(text):
        nonlocal byte_count
        count = len(text.encode('utf-8'))
        demand(count <= byte_cap - byte_count, 'json-output-byte-cap')
        byte_count += count
        fragments.append(text)

    def take(count):
        nonlocal units
        demand(count <= unit_cap - units, 'json-output-unit-cap-before-access')
        units += count

    def visit(item, depth):
        demand(depth <= 12, 'json-output-depth-cap')
        kind = type(item)
        if kind is dict:
            take(1 + len(item))  # Reserve all member iteration before items().
            emit('{')
            first = True
            for key, child in item.items():
                demand(type(key) is str and len(key) <= 4096, 'json-key-type-cap')
                if not first:
                    emit(',')
                first = False
                emit(json.dumps(key, ensure_ascii=False))
                emit(':')
                visit(child, depth + 1)
            emit('}')
        elif kind is list:
            take(1 + len(item))
            emit('[')
            first = True
            for child in item:
                if not first:
                    emit(',')
                first = False
                visit(child, depth + 1)
            emit(']')
        else:
            # Scalar dispatch is included in its parent member fee; root scalar
            # has one explicit unit. All scalar characters remain byte work.
            if depth == 0:
                take(1)
            demand(kind in (str, int, float, bool, type(None)), 'json-no-custom-object')
            if kind is str:
                demand(len(item) <= 4096, 'json-string-cap')
            elif kind is int:
                demand(-(1 << 63) <= item < (1 << 64), 'json-integer-width')
            elif kind is float:
                demand(item == item and abs(item) <= 1e15, 'json-float-bound')
            emit(json.dumps(item, ensure_ascii=False, allow_nan=False))
    visit(value, 0)
    emit('\n')
    return ''.join(fragments).encode('utf-8')


class RecordFailure(Stop):
    def __init__(self, details):
        super().__init__('record-persistence-failure')
        self.details = details


class CaptureFailure(Stop):
    def __init__(self, details):
        super().__init__('command-stopped-no-retry')
        self.details = details


def error_info(exc):
    METER.enter('emergency')
    METER.work(32)
    result = {'kind': str(exc)[:256] if isinstance(exc, Stop) else type(exc).__name__,
              'errno': getattr(exc, 'errno', None)}
    if isinstance(exc, (RecordFailure, CaptureFailure)):
        result['details'] = exc.details
    return result


def emergency(value):
    global EMERGENCY_EMITTED
    if EMERGENCY_EMITTED:
        return
    EMERGENCY_EMITTED = True
    try:
        METER.enter('emergency')
        METER.work(3 * 192)
        raw = encode_metadata(value, 192, EMERGENCY_CAP)
    except BaseException:
        # Literal last-resort status does not traverse a failed metadata graph.
        raw = b'{"status":"EMERGENCY_CONTEXT_INCOMPLETE","complete":false}\n'
    try:
        os.write(2, raw)
    except BaseException:
        pass


def demand(condition, reason):
    if not condition:
        raise Stop(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path, cap, role='input'):
    """No-follow bounded regular input; read and close errors stay separate."""
    METER.work(16)  # File metadata/ownership/close, prepaid before open.
    fd = None
    result = None
    first = None
    cleanup = []
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
        before = os.fstat(fd)
        demand(stat.S_ISREG(before.st_mode) and before.st_size <= cap, 'input-type-or-size')
        BYTE_METER.reserve(before.st_size, role)
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
    METER.work(16)
    BYTE_METER.reserve(len(raw), 'output')
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
    name = path.name
    if name == 'dependency-receipt.json':
        cap = 5248
    elif name == 'build-intent.json':
        cap = 1050
    elif name == 'build-failure.json' or (name.endswith('.terminal.json') and value.get('firstFailure')):
        METER.enter('emergency')
        cap = 192
    elif name.endswith('.dispatch-attempted.json') or name.endswith('.dispatched.json'):
        cap = 32
    elif name.startswith('artifact-'):
        cap = 32
    elif name == 'build-terminal.json':
        cap = 128
    else:
        cap = 96
    METER.work(3 * cap)  # Includes fixed snapshot construction, before traversal.
    value['meter'] = METER.snapshot()
    raw = encode_metadata(value, cap, 2 * 1024 * 1024)
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
    described = decode_metadata(descriptor_raw, 1200)
    fixed = described['fixedToolsAndInterpreterRows']
    modules = described['moduleRows']
    demand(type(fixed) is list and type(modules) is list and len(fixed) + len(modules) <= 117, 'descriptor-row-cap')
    allowed = {}
    METER.work(8 * 117)
    for group in (fixed, modules):
        for row in group:
            if 'metadataError' not in row:
                path = row['path']
                demand(path not in allowed, 'descriptor-duplicates')
                allowed[path] = (row['realpath'], row['bytes'], row['device'], row['inode'], row['mtime_ns'])
    files = pin_document['files']
    demand(type(files) is list and len(files) == len(allowed) == 117, 'identity-record-cap')
    unique, seen = {}, set()
    before_rows = []
    payload_sum = 0
    METER.work(32 * 117)
    for row in files:
        path, real, size, device, inode, mtime, sha = (row['path'], row['realpath'], row['bytes'], row['device'], row['inode'], row['mtime_ns'], row['sha256'])
        demand(path not in seen and path in allowed, 'identity-set-or-duplicate')
        seen.add(path)
        demand((real, size, device, inode, mtime) == allowed[path], 'identity-descriptor-mismatch')
        demand(len(sha) == 64, 'identity-hash-missing')
        demand(os.path.realpath(path) == real, 'identity-realpath')
        st = os.stat(real)
        demand(stat.S_ISREG(st.st_mode) and (st.st_size, st.st_dev, st.st_ino, st.st_mtime_ns) == (size, device, inode, mtime), 'identity-metadata-drift')
        before_rows.append({'path': path, 'realpath': real, 'bytes': size, 'device': device, 'inode': inode, 'mtime_ns': mtime})
        key = (device, inode)
        if key in unique:
            demand(unique[key] == sha, 'alias-pin-conflict')
        else:
            unique[key] = sha
            payload_sum += size
    demand(payload_sum + 20278 + 65536 + 2097152 <= PREPARED_IDENTITY_CAP, 'prepared-identity-ticket-insufficient')
    demand(authorization['preparedIdentityHistoricalCapBytes'] == PREPARED_IDENTITY_CAP, 'identity-authority-cap')
    demand(authorization['reusePreparedIdentityHashesMetadataOnly'] is True, 'prepared-hash-reuse-not-accepted')
    demand(pin_document['payloadHashesPerformedInPreparation'] is True, 'prepared-hashes-missing')
    demand(pin_document['payloadHashRepeatPermitted'] is False, 'identity-ticket-must-not-reset')
    demand(pin_document['distinctPayloadBytesHashed'] == payload_sum, 'prepared-identity-byte-total')
    demand(len(sys.modules) <= 512, 'interpreter-module-visit-bound')
    METER.work(3 * 512)
    for module in sys.modules.values():
        path = getattr(module, '__file__', None)
        if path and path.startswith('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/'):
            demand(path in allowed, 'unprepared-interpreter-module')
    return {'preparedPhysicalPayloadBytesHashed': payload_sum, 'physicalPayloadBytesHashedThisRun': 0,
            'metadataOnlyReuseAcceptedByRoot': True, 'logicalAliases': len(files),
            'distinctPhysicalPayloads': len(unique), 'before': before_rows,
            'interpreterTransitiveDylibAndActualOpenClosure': 'PENDING_NOT_PROVEN'}


def stop_owned_leader(process, record):
    """Only this unreaped Popen instance; no group, descendant or old-PID kill."""
    METER.enter('emergency')
    METER.work(64)
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
    METER.enter('control')
    BYTE_METER.reserve(CAP, 'capture')
    METER.work(48)  # Original fixed command fields.
    METER.work(1024)  # Kqueue construction/register/rollback/unregister/close.
    stem = '%02d-%s' % (number, label)
    stdout = output / (stem + '.stdout')
    stderr = output / (stem + '.stderr')
    record = {'index': number, 'label': label, 'argv': argv, 'cwd': str(output), 'environment': env,
              'stdout': str(stdout), 'stderr': str(stderr), 'captureRemainingAtStart': RAW_CAPTURE_CAP - ledger.captured_bytes,
              'timeoutSeconds': seconds, 'selectorBackend': 'KqueueSelector', 'phase': 'planned', 'dispatchAttempted': False, 'pid': None,
              'leaderReturnCode': None, 'firstFailure': None, 'ownedLeaderControl': [],
              'captureEOF': {'stdout': False, 'stderr': False}, 'descendantDrain': 'UNKNOWN_NOT_MEASURED'}
    write_json(output / (stem + '.planned.json'), record)
    fds = {}
    pipes = {}
    process = None
    sel = selectors.KqueueSelector()  # Fixed Darwin backend; no fallback/probe.
    started = time.monotonic()
    try:
        for name, path in [('stdout', stdout), ('stderr', stderr)]:
            fds[name] = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            demand(stat.S_IMODE(os.fstat(fds[name]).st_mode) == 0o600, 'capture-file-mode')
        demand(not CANCELLED and ledger.captured_bytes < RAW_CAPTURE_CAP, 'cancelled-or-no-capture-budget')
        record['phase'] = 'dispatch-attempted'
        record['dispatchAttempted'] = True
        write_json(output / (stem + '.dispatch-attempted.json'), {'index': number, 'phase': record['phase'], 'dispatchAttempted': True, 'pid': None})
        process = subprocess.Popen(argv, cwd=str(output), env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True,
                                   start_new_session=True)
        pipes = {'stdout': process.stdout, 'stderr': process.stderr}
        record['pid'] = process.pid
        record['phase'] = 'dispatched'
        write_json(output / (stem + '.dispatched.json'), {'index': number, 'phase': record['phase'], 'dispatchAttempted': True, 'pid': process.pid})
        for name, pipe in [('stdout', process.stdout), ('stderr', process.stderr)]:
            pipes[name] = pipe
            os.set_blocking(pipe.fileno(), False)
            sel.register(pipe, selectors.EVENT_READ, name)
        deadline = started + seconds
        while True:
            demand(ledger.loop_checks < 134, 'selector-loop-check-cap-incomplete')
            METER.work(16)  # Before get_map/bool/len and leader-state condition.
            ledger.loop_checks += 1
            if not (sel.get_map() or process.poll() is None):
                break
            if CANCELLED:
                raise Stop('cancelled')
            if time.monotonic() >= deadline:
                raise Stop('timeout')
            demand(ledger.captured_bytes < RAW_CAPTURE_CAP, 'output-cap-reached')
            # Only stdout/stderr are registered: at most two returned events.
            # Pay before native collection creation, including an empty wakeup.
            demand(ledger.select_calls < 128, 'select-call-cap-incomplete')
            METER.work(256)  # Backend + <=2 complete caller/event paths.
            ledger.select_calls += 1
            for key, events in sel.select(min(0.1, max(0.0, deadline - time.monotonic()))):
                remaining = RAW_CAPTURE_CAP - ledger.captured_bytes
                demand(remaining > 0, 'output-cap-reached')
                try:
                    chunk = os.read(key.fileobj.fileno(), min(65536, remaining))
                except BlockingIOError:
                    continue
                if not chunk:
                    record['captureEOF'][key.data] = True
                    sel.unregister(key.fileobj)
                    continue
                ledger.captured_bytes += len(chunk)
                written = os.write(fds[key.data], chunk)
                demand(written == len(chunk), 'capture-short-write')
                if ledger.captured_bytes == RAW_CAPTURE_CAP:
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
        record['captureCombinedBytesAfter'] = ledger.captured_bytes
        record['selectCallsCombinedAfter'] = ledger.select_calls
        record['selectorLoopChecksCombinedAfter'] = ledger.loop_checks
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
                demand(len(words) < 3072, 'raw-dependency-cap-before-append')
                METER.work(1)
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
        demand(len(words) < 3072, 'raw-dependency-cap-before-append')
        METER.work(1)
        words.append(''.join(part))
    demand(len(words) <= 3072, 'raw-dependency-cap')
    return words


def dependency_receipt(output):
    METER.enter('dependency')
    METER.work(128)  # Fixed result construction, scalar checks and provenance.
    raw = bounded_read(output / 'probe.d', 2097152)
    words = parse_deps(raw.decode('utf-8'))
    normalized = {}
    METER.work(3 * len(words))  # normalization + membership + insert; no sorting.
    for word in words:
        path = os.path.normpath(word if os.path.isabs(word) else str(output / word))
        if path not in normalized:
            demand(len(normalized) < 1024, 'unique-dependency-cap-before-insert')
            normalized[path] = None
    # This future read is paid afresh. Deep prior references and witnesses remain
    # opaque bytes. Whole-file pin plus row ordinal binds provenance, not current
    # header/open identity. No whole JSON decoding of this historic document.
    oldraw = bounded_read(PRIOR_USED, 3156859)
    demand(len(oldraw) == 3156859 and digest(oldraw) == PRIOR_USED_SHA, 'prior-witness-pin')
    METER.work(880 * 24 + 64)
    start_marker = b'  "covered": [\n'
    start = oldraw.find(start_marker)
    demand(start >= 0, 'prior-covered-array-missing')
    start += len(start_marker)
    end = oldraw.find(b'\n  ],', start)
    demand(end > start, 'prior-covered-array-end')
    covered = oldraw[start:end]
    oldmap = {}
    cursor = ordinal = 0
    while cursor < len(covered):
        begin = covered.find(b'    {\n', cursor)
        if begin < 0:
            break
        demand(ordinal < 880, 'prior-row-cap-before-access')
        finish = covered.find(b'\n    }', begin)
        demand(finish > begin, 'prior-row-end')
        row = covered[begin:finish]
        # Only a scalar JSON string is decoded; nested graphs are never built.
        path_prefix = b'      "normalizedPath": '
        demand(row.startswith(b'    {\n' + path_prefix), 'prior-path-field-order')
        line_end = row.find(b'\n', len(b'    {\n'))
        path_raw = row[len(b'    {\n') + len(path_prefix):line_end]
        demand(path_raw.endswith(b','), 'prior-path-delimiter')
        path_raw = path_raw[:-1]
        demand(len(path_raw) <= 4096, 'prior-path-string-cap')
        top = re.findall(rb'^      "([^"\n]+)":', row, re.MULTILINE)
        demand(top == [b'normalizedPath', b'references', b'approvedWitness'], 'prior-opaque-field-schema')
        demand(b'\n      "approvedWitness": {' in row, 'prior-witness-object')
        path = json.loads(path_raw)
        demand(type(path) is str and path not in oldmap, 'prior-path-scalar-or-duplicate')
        oldmap[path] = ordinal
        ordinal += 1
        cursor = finish + len(b'\n    }')
    demand(ordinal == len(oldmap) == 880, 'prior-witness-count')
    supplied_raw = bounded_read(STAGE / 'inputs/source-evidence.json.raw', 3621)
    demand(len(supplied_raw) == 3621 and digest(supplied_raw) == '5afb7c58d5154e7bd6083a5c7e7c273e15f4e6176e5f65c24758fa54a5ccb176', 'fixed-source-evidence-pin')
    supplied = decode_metadata(supplied_raw, 128)
    candidates = supplied['sdkAndReleaseEvidence']
    demand(type(candidates) is list and len(candidates) <= 7, 'SDK-candidate-cap')
    direct = {}
    METER.work(5 * 7)
    for ordinal, row in enumerate(candidates):
        if 'path' in row:
            path = row['path']
            demand(path not in direct, 'SDK-evidence-duplicate')
            direct[path] = ordinal
    entries, pending = [], []
    resource_prefix = '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/'
    METER.work(10 * len(normalized))
    for path in normalized:
        if path == str(output / 'input/location_metadata_contract_probe.cc'):
            entry = {'path': path, 'basis': 'frozen-single-source', 'sourceSHA256': SOURCE_SHA}
        elif (path.startswith(SDK + '/') or path.startswith(resource_prefix)) and path in oldmap:
            entry = {'path': path, 'basis': 'prior-approved-used-witness', 'priorRowOrdinal': oldmap[path]}
        elif path in direct:
            entry = {'path': path, 'basis': 'root-accepted-I06-SDK-pin', 'sdkEvidenceOrdinal': direct[path]}
        else:
            demand(len(pending) < 64, 'new-dependency-record-cap-before-append')
            pending.append(path)
            entry = {'path': path, 'basis': 'PENDING_NEW_APPROVED_RECORD_AND_LOCATOR'}
        entries.append(entry)
    result = {'rawTokens': len(words), 'uniquePaths': len(normalized), 'depfileBytes': len(raw),
              'depfileSHA256': digest(raw), 'entries': entries, 'pendingNewPaths': pending,
              'priorWitnessSHA256': PRIOR_USED_SHA, 'sourceEvidenceSHA256': digest(supplied_raw),
              'currentHeaderPayloadRehashes': 0, 'newWholeIndexPasses': 0,
              'bindingIsNotCompilerOpenTrace': True,
              'closure': 'PENDING_EXACT_NEW_WITNESSES_AND_IDENTITY' if pending else 'REUSED_PIN_BINDINGS_ONLY_CURRENT_OPEN_AND_LINK_CLOSURE_PENDING'}
    write_json(output / 'dependency-receipt.json', result)
    METER.enter('control')
    return result


def artifact_pin(path):
    raw = bounded_read(path, 4194304, 'artifact')
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
    global METER, BYTE_METER
    METER, BYTE_METER = PhaseMeter(), ByteMeter()
    METER.enter('preflight')
    METER.work(2000)  # Fixed authority/plan/scalar checks, paths, SDK and directories.
    output = None
    try:
        demand(len(sys.argv) == 1, 'no-runner-arguments')
        demand(Path(__file__).absolute() == SELF, 'fixed-runner-entry')
        demand(os.path.realpath(sys.executable) == INTERPRETER_REAL, 'fixed-interpreter')
        demand(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, 'isolated-interpreter-required')
        # AUTH does not exist in preparation. It must be created by root in a
        # separate execution window; no dry-run/verify-only execution entry.
        auth_raw = bounded_read(AUTH, 65536)
        auth = decode_metadata(auth_raw, 96)
        demand(auth['schema'] == 'T03_METADATA_PROBE_BUILD_AUTH_V1' and auth['authorized'] is True, 'no-build-authority')
        demand(auth['scope'] == 'ONE_COMPILE_AND_FIVE_STATIC_CHECKS_NO_EXPERIMENT_EXECUTION', 'wrong-authority-scope')
        demand(auth['sourceRef'] == SOURCE_REF and auth['sourceSHA256'] == SOURCE_SHA, 'source-authority')
        meter_raw = bounded_read(METER_PLAN, 32768)
        history_raw = bounded_read(HISTORY, 16384)
        demand(digest(meter_raw) == auth['meterPlanSHA256'] and digest(history_raw) == auth['historyLedgerSHA256'], 'meter-history-authority')
        meter_plan = decode_metadata(meter_raw, 256)
        history = decode_metadata(history_raw, 128)
        proof_raw = bounded_read(STAGE / 'meter-forward-binding/meter-proof.md', 32768)
        demand(digest(proof_raw) == meter_plan['proofSHA256'] == auth['countingProofSHA256'], 'counting-proof-authority')
        method_raw = bounded_read(REVIEW_METHOD, 32768)
        demand(digest(method_raw) == meter_plan['reviewMethodPlanSHA256'] == auth['reviewMethodPlanSHA256'], 'review-method-authority')
        method = decode_metadata(method_raw, 256)
        METER.work(128)  # Method/joint/byte/entity profile scalar validation.
        demand(method['ownerMetadata'] == 103000 and method['peerMetadataEach'] == 268000, 'external-method-tickets')
        demand(meter_plan['runtimeMetadataReserved'] == 167000 and meter_plan['futureAllPartiesMetadataProposal'] == 806000, 'fixed-runtime-ticket')
        demand(auth['runtimeMetadataReserved'] == 167000 and auth['freshFutureAllPartiesMetadataAccepted'] == 806000, 'fresh-runtime-ticket-not-accepted')
        demand(meter_plan['futureAllPartiesMetadataProposal'] <= history['currentMetadataRemaining'] == 926737 and
               history['currentMetadataCumulative'] == 2273263 and history['forwardLogicalGuard'] == 3200000 and
               history['currentEntityDeclarationUnchanged'] == 521456 and history['currentEntityGuardUnchanged'] == 1300000,
               'joint-forward-declaration-and-guard-binding')
        demand(meter_plan['futureEntityProposal'] == 737280 and auth['freshFutureEntityAccepted'] == 737280, 'fresh-entity-ticket-not-accepted')
        demand(auth['ownerClosureMetadataAccepted'] == 103000 and auth['peerMetadataEachAccepted'] == 268000, 'joint-component-authority')
        demand(auth['freshFutureByteProposalAccepted'] == 171966464 and auth['runtimeOwnerBytes'] == 41943040, 'fresh-byte-ticket-not-accepted')
        demand(history['historicalOwnerActual'] is None and history['oldOwner1000Reusable'] is False and history['oldRoot4000Reusable'] is False, 'historical-unknown-must-remain')
        demand(auth['dependencyMode'] == 'CAPTURE_REUSE_PINNED_WITNESS_AND_DEFER_UNKNOWN_NO_INDEX_READ', 'dependency-method-not-accepted')
        plan_raw = bounded_read(PLAN, 65536)
        self_raw = bounded_read(SELF, 65536)
        pin_raw = bounded_read(PINS, 262144)
        demand(digest(plan_raw) == auth['planSHA256'] and digest(self_raw) == auth['runnerSHA256'] and digest(pin_raw) == auth['identityManifestSHA256'], 'authority-input-hash')
        plan = decode_metadata(plan_raw, 768)
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
        identities = identity_preflight(auth, pin_raw, decode_metadata(pin_raw, 1100))
        verify_sdk_metadata(plan)
        output, output_problem = create_owned_output(token)
        if output_problem:
            raise RecordFailure(dict(output_problem, path=str(OUT_BASE / token), outputCreated=output is not None))
        demand(output is not None, 'exclusive-output-not-owned')
        for name in ['input', 'artifacts', 'tmp']:
            (output / name).mkdir(mode=0o700, exist_ok=False)
        write_once_bytes(output / 'input/location_metadata_contract_probe.cc', source_raw, 0o400)
        METER.enter('control')
        write_json(output / 'build-intent.json', {'authorizationSHA256': digest(auth_raw), 'planSHA256': digest(plan_raw), 'runnerSHA256': digest(self_raw), 'identityManifestSHA256': digest(pin_raw), 'authorizationInputRef': auth['inputProcessRef'], 'output': str(output), 'noRetry': True, 'runtime': 'NOT_AUTHORIZED', 'sourceArgcIfLaterI06Runs': 1, 'applicationIdentity': identities})
        env = {'PATH': '/usr/bin:/bin', 'DEVELOPER_DIR': '/Applications/Xcode.app/Contents/Developer', 'LANG': 'C', 'LC_ALL': 'C', 'TMPDIR': str(output / 'tmp')}
        flags = [x.replace('@OUT@', str(output)) for x in expected_flags]
        argv = [COMPILER] + flags
        ledger = CaptureBytes()
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
        METER.work(12 * 117)
        for row in identities['before']:
            path, real, device, inode, size, mtime = row['path'], row['realpath'], row['device'], row['inode'], row['bytes'], row['mtime_ns']
            demand(os.path.realpath(path) == real, 'post-tool-realpath-drift')
            st = os.stat(real)
            demand((st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns) ==
                   (device, inode, size, mtime), 'post-tool-metadata-drift')
        verify_sdk_metadata(plan)
        write_json(output / 'build-terminal.json', {'status': 'BUILT_UNVERIFIED_STATIC_STREAMS_CAPTURED', 'artifact': after,
                   'capturedCombinedBytes': ledger.captured_bytes, 'compilerCalls': 1, 'staticCalls': 5,
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
