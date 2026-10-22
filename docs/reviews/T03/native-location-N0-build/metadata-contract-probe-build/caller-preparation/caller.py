"""PREPARED ONLY. Four separately admitted, one-shot roles; no dryrun mode.

The trusted root invokes this exact pinned source with ROLE ADMISSION_SHA256.
No call or local function execution is authorized by the preparation window.
Python 3.9 stdlib only. This is not a cryptographic signer or a process-tree drainer.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import stat
import subprocess
import sys
import time

WORK = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build')
D = WORK / 'docs/reviews/T03/native-location-N0-build/metadata-contract-probe-build'
HERE = D / 'caller-preparation'
ROOT = Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release')
AUTH = ROOT / 'T03-metadata-contract-probe-one-build-authorization.json'
PARENT = WORK / 'build/native-location/metadata-contract-probe/parent'
OUT = WORK / 'build/native-location/metadata-contract-probe/darwin-arm64'
REVIEW = WORK / 'build/native-location/metadata-contract-probe/reviews'
GIT = Path('/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/.git')
HEAD = GIT / 'worktrees/T03-native-location-N0-build/HEAD'
BRANCH = GIT / 'refs/heads/feature/T03-native-location-N0-build'
INTERPRETER = '/Applications/Xcode.app/Contents/Developer/usr/bin/python3'
REAL_INTERPRETER = '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
ROLES = ('producer', 'peer-a', 'peer-b', 'owner')
PIN_MANIFEST = '415d45da0f9fe5de03cead96e3bc529d33d13613126c0d75ed7c7ed6ec35adf3'
PIN_DESCRIPTOR = 'b0c2fd15678081c101f659cd01d111218a06b6acea3901c9dca4dfe5c502465d'
CONTROLS = {
    'run-once.py': ('run-once.py', 44931, 'ddc5d9d7705dada5435f57a7f40c1f2be94e5787f10bb4cf203731959d9025c7'),
    'call-plan.json': ('call-plan.json', 10326, '6656a3d9e2205d970f2d63abc8c08ed47775852e38a94d91aabd58c3ccdaebaa'),
    'meter-plan.json': ('meter-plan.json', 1092, '2fb962a1597628d531041f9df492c7b78547731d1ffba9e8acf4a17ce822a595'),
    'meter-history.json': ('meter-history.json', 3711, '5799327df61dfea17ac842364a2336e47ed8f1168d66102d7313909ef976ea23'),
    'meter-proof.md': ('meter-forward-binding/meter-proof.md', 18228, '1b8a71847c72c9d922dfd1f593c12b043732438d8c83cea7525464b68910fead'),
    'method-plan.json': ('meter-forward-binding/review-methods/method-plan.json', 1417, '89de05af39fd51788dcda3e65588d289e266dc936630f7b34fb9aabb2a2074be'),
    'review-saved.py': ('meter-forward-binding/review-methods/review-saved.py', 57421, '044b84f37dc5d10dd24d4c42cfb6088e118c87de051be934ac384897ab2527db'),
}
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C', 'PYTHONDONTWRITEBYTECODE': '1'}
AUTH_KEYS = set(('authorized countingProofSHA256 dependencyMode freshFutureAllPartiesMetadataAccepted '
                 'freshFutureByteProposalAccepted freshFutureEntityAccepted historyLedgerSHA256 '
                 'identityDescriptorSHA256 identityManifestSHA256 inputProcessRef meterPlanSHA256 '
                 'ownerClosureMetadataAccepted peerMetadataEachAccepted planSHA256 '
                 'preparedIdentityHistoricalCapBytes reusePreparedIdentityHashesMetadataOnly '
                 'reviewMethodPlanSHA256 runnerSHA256 runtimeMetadataReserved runtimeOwnerBytes '
                 'schema scope sourceRef sourceSHA256').split())
ADMISSION_KEYS = set(('schema authorized role nonce notBefore expires inputProcessRef callerSHA256 '
                      'producerAuthorizationSHA256 configSHA256 outputToken roleIdentities '
                      'predecessorTerminalSHA256 predecessorCompletionSHA256 interpreterStat '
                      'argv cwd environment callerTicket originalTicketsFunded rootDecisionId '
                      'predecessorOuterExitCodes predecessorRootObservationSHA256 aggregateBudget '
                      'callerAllFourTicketsFunded').split())
CFG_KEYS = set(('schema authorized role metadataTicket byteTicket inputProcessRef reviewerIdentity '
                'outputToken outputRoot reviewOutputRoot producerAuthorizationSHA256 '
                'producerIdentityManifestSHA256 controlPins acceptedCompilerGeneratedImports').split())


class Hold(Exception):
    pass


class Fault(Exception):
    def __init__(self, first, cleanup):
        self.first = first
        self.cleanup = cleanup


def need(ok, reason):
    if not ok:
        raise Hold(reason)


class Meter:
    """Per-role independent proposal; all four role tickets are required in advance."""
    def __init__(self, role):
        self.byte_limit = 2097152 if role == 'producer' else 5242880 if role == 'owner' else 3145728
        self.metadata = 0
        self.entity = 0
        self.io = 0
        self.files = 0
        self.json_units = 0
        self.json_files = 0
        self.stream_events = 0
        self.select_calls = 0
        self.writes = 0
        self.work(4096, 4096)  # Fixed admission/bindings/control/cleanup/output envelope.

    def work(self, metadata, entity=0):
        need(self.metadata + metadata <= 28000 and self.entity + entity <= 27000,
             'caller-record-ticket-exhausted')
        self.metadata += metadata
        self.entity += entity

    def bytes(self, amount):
        need(type(amount) is int and amount >= 0 and self.io + amount <= self.byte_limit,
             'caller-byte-ticket-exhausted')
        self.io += amount

    def file(self):
        need(self.files < 37, 'caller-file-action-cap')
        self.files += 1
        self.work(216, 200)

    def json(self, cap):
        need(self.json_files < 7 and self.json_units + cap <= 1200,
             'caller-json-admission-cap')
        self.json_files += 1
        self.json_units += cap
        self.work(8 * cap + 80, 8 * cap + 80)

    def event(self):
        need(self.stream_events < 32, 'caller-stream-event-cap')
        self.stream_events += 1
        self.work(16, 8)

    def selecting(self):
        need(self.select_calls < 16, 'caller-select-call-cap')
        self.select_calls += 1
        self.work(256, 256)  # Backend/list/key/tuple maximum before select/native return.

    def writing(self):
        need(self.writes < 96, 'caller-output-write-cap')
        self.writes += 1
        self.work(8, 4)

    def snapshot(self):
        return {'metadataDebited': self.metadata, 'entityDebited': self.entity,
                'applicationBytesReserved': self.io, 'files': self.files,
                'jsonFiles': self.json_files, 'jsonUnitsReserved': self.json_units,
                'streamEvents': self.stream_events, 'writes': self.writes,
                'selectCalls': self.select_calls,
                'actualOSIO': None, 'physicalOrVMAllocationMeasured': False}


def hex_text(value, width):
    return type(value) is str and len(value) == width and re.fullmatch('[0-9a-f]+', value) is not None


def identity(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_nlink, st.st_size, st.st_mtime_ns)


def directory(path, private=False):
    """Every component is opened without following links; no recursive discovery."""
    need(path.is_absolute() and len(path.parts) <= 24, 'absolute-fixed-path-required')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new
        if private:
            st = os.fstat(fd)
            need(st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == 0o700,
                 'private-directory-permissions')
        return fd
    except BaseException as exc:
        first = error_value('directory-open-or-mode', exc)
        cleanup = []
        try:
            os.close(fd)
        except BaseException as close_exc:
            cleanup.append(error_value('directory-failed-open-close', close_exc))
        raise Fault(first, cleanup)


def read_file(path, cap, meter, private=False):
    meter.file()
    parent = directory(path.parent)
    fd = None
    first = None
    cleanup = []
    result = None
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= cap,
             'regular-input-cap')
        if private:
            need(before.st_uid == os.getuid() and stat.S_IMODE(before.st_mode) == 0o600,
                 'authority-config-permissions')
        meter.bytes(before.st_size)
        chunks = []
        remaining = before.st_size
        while remaining:
            need(len(chunks) < 32, 'input-chunk-cap-before-read')
            raw = os.read(fd, min(65536, remaining))
            need(bool(raw), 'input-short-read')
            chunks.append(raw)
            remaining -= len(raw)
        need(identity(before) == identity(os.fstat(fd)), 'input-changed-during-read')
        result = b''.join(chunks)
    except BaseException as exc:
        first = error_value('named-input-read', exc)
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except BaseException as exc:
                cleanup.append(error_value('named-input-close', exc))
        try:
            os.close(parent)
        except BaseException as exc:
            cleanup.append(error_value('named-input-parent-close', exc))
    if first is not None or cleanup:
        raise Fault(first, cleanup)
    return result


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def scan_json(raw, cap):
    """Guard semantic fields/array members/containers before native construction.

    Packed 4-bit states, depth<=12. Object key pays its field/value; array/root
    scalar pays one member; container also pays itself. No per-character list.
    Grammar and escape validity are finally checked by json.loads, once.
    """
    n = len(raw)
    p = 0
    packed = 0
    depth = 1
    units = 0
    while p < n:
        c = raw[p]
        if c in b' \t\r\n':
            p += 1
            continue
        state = packed & 15
        if state in (1, 5, 8):
            if c == 44 and state in (5, 8):
                packed = (packed & ~15) | (6 if state == 5 else 9)
                p += 1
                continue
            if c == (125 if state == 5 else 93) and depth > 1:
                packed >>= 4
                depth -= 1
                p += 1
                continue
            raise Hold('json-delimiter')
        if state in (2, 6):
            if c == 125 and state == 2:
                packed >>= 4
                depth -= 1
                p += 1
                continue
            need(c == 34, 'json-object-key')
            units += 1
            need(units <= cap, 'json-unit-cap-before-key')
            packed = (packed & ~15) | 3
        elif state == 3:
            need(c == 58, 'json-colon')
            packed = (packed & ~15) | 4
            p += 1
            continue
        else:
            if c == 93 and state == 7:
                packed >>= 4
                depth -= 1
                p += 1
                continue
            need(state in (0, 4, 7, 9), 'json-value-state')
            if state != 4:
                units += 1
                need(units <= cap, 'json-unit-cap-before-value')
            packed = (packed & ~15) | (1 if state == 0 else 5 if state == 4 else 8)
            if c in (123, 91):
                if state in (4, 7, 9):
                    units += 1
                    need(units <= cap, 'json-unit-cap-before-container')
                need(depth < 13, 'json-depth-before-push')
                packed = (packed << 4) | (2 if c == 123 else 7)
                depth += 1
                p += 1
                continue
        if c == 34:
            p += 1
            escaped = False
            while p < n:
                c = raw[p]
                p += 1
                if escaped:
                    escaped = False
                elif c == 92:
                    escaped = True
                elif c == 34:
                    break
            else:
                raise Hold('json-unclosed-string')
        else:
            start = p
            while p < n and raw[p] not in b' \t\r\n,]}':
                p += 1
            need(p > start, 'json-empty-scalar')
            token = raw[start:p]
            need(token in (b'true', b'false', b'null') or
                 (len(token) <= 32 and re.fullmatch(rb'-?(0|[1-9][0-9]*)', token)),
                 'json-only-short-integer-or-literal')
    need(depth == 1 and packed == 1, 'json-complete-single-root')


def decode(raw, cap, meter):
    meter.json(cap)
    scan_json(raw, cap)
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'json-duplicate-key')
            result[key] = value
        return result
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs)
    need(type(value) is dict, 'json-root-object')
    return value


def utc(value):
    need(type(value) is str and len(value) == 20, 'utc-exact-text')
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()


def check_time(admission):
    start = utc(admission['notBefore'])
    end = utc(admission['expires'])
    now = time.time()
    need(0 < end - start <= 3600 and start <= now < end, 'root-admission-time-window')


def write_bytes(dirfd, name, raw, meter):
    meter.file()
    meter.bytes(len(raw))
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dirfd)
    first = None
    cleanup = []
    try:
        offset = 0
        while offset < len(raw):
            meter.writing()
            written = os.write(fd, raw[offset:])
            need(written > 0, 'output-zero-write')
            offset += written
        os.fsync(fd)
    except BaseException as exc:
        first = error_value('exclusive-output-write-or-fsync', exc)
    finally:
        try:
            os.close(fd)
        except BaseException as exc:
            cleanup.append(error_value('exclusive-output-close', exc))
    if first is not None or cleanup:
        raise Fault(first, cleanup)


def record(dirfd, name, value, meter):
    raw = (json.dumps(value, ensure_ascii=True, separators=(',', ':'), allow_nan=False) + '\n').encode('ascii')
    need(len(raw) <= 16384, 'parent-record-cap')
    write_bytes(dirfd, name, raw, meter)
    return digest(raw)


def error_value(operation, exc):
    if isinstance(exc, Fault):
        return exc.first
    return {'operation': operation, 'kind': type(exc).__name__[:128],
            'errno': getattr(exc, 'errno', None),
            'safeCode': str(exc)[:128] if isinstance(exc, Hold) else None}


def private_child(parentfd, name):
    try:
        os.mkdir(name, 0o700, dir_fd=parentfd)
    except FileExistsError:
        pass
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parentfd)
    try:
        st = os.fstat(fd)
        need(st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == 0o700,
             'owned-private-output-directory')
    except BaseException as exc:
        first = error_value('private-output-open-or-mode', exc)
        cleanup = []
        try:
            os.close(fd)
        except BaseException as close_exc:
            cleanup.append(error_value('private-output-failed-close', close_exc))
        raise Fault(first, cleanup)
    return fd


def admit(role, trusted_hash, meter):
    raw = read_file(ROOT / ('T03-metadata-probe-parent-' + role + '-admission.json'), 32768, meter, True)
    need(digest(raw) == trusted_hash, 'trusted-root-admission-digest')
    a = decode(raw, 256, meter)
    need(set(a) == ADMISSION_KEYS and a['schema'] == 'T03_REAL_PARENT_ADMISSION_V1' and
         a['authorized'] is True and a['role'] == role, 'root-admission-shape')
    need(hex_text(a['nonce'], 64) and hex_text(a['inputProcessRef'], 40) and
         hex_text(a['outputToken'], 64) and type(a['rootDecisionId']) is str and
         1 <= len(a['rootDecisionId']) <= 128, 'root-admission-identities')
    check_time(a)
    ids = a['roleIdentities']
    need(type(ids) is dict and set(ids) == set(ROLES), 'four-role-identities')
    for name in ROLES:
        need(type(ids[name]) is str and 1 <= len(ids[name]) <= 128, 'actual-role-identity')
    need(len(set(ids.values())) == 4, 'four-distinct-root-accepted-identities')
    need(a['callerTicket'] == {'metadata': 28000, 'entity': 27000, 'bytes': meter.byte_limit} and
         a['originalTicketsFunded'] is True and a['callerAllFourTicketsFunded'] is True,
         'distinct-real-runtime-tickets-required')
    aggregate = a['aggregateBudget']
    fixed_aggregate = {'metadataBefore': 2291263, 'metadataAfter': 3209263,
                       'entityBefore': 521456, 'entityAfter': 1366736,
                       'buildBytesBefore': 109086362664, 'buildBytesAfter': 109271960616,
                       'buildByteGuard': 137438953472}
    need(type(aggregate) is dict and set(aggregate) == set(fixed_aggregate) | {'metadataGuard', 'entityGuard'},
         'root-global-aggregate-exact-shape')
    for key, value in fixed_aggregate.items():
        need(type(aggregate[key]) is int and aggregate[key] == value, 'root-global-fixed-aggregate')
    need(type(aggregate['entityGuard']) is int and aggregate['entityGuard'] >= aggregate['entityAfter'] and
         type(aggregate['metadataGuard']) is int and aggregate['metadataGuard'] >= aggregate['metadataAfter'],
         'new-caller-does-not-fit-root-explicit-forward-guards')
    need(read_file(HEAD, 100, meter) == b'ref: refs/heads/feature/T03-native-location-N0-build\n' and
         read_file(BRANCH, 41, meter) == (a['inputProcessRef'] + '\n').encode('ascii'), 'actual-git-input-ref')
    self_raw = read_file(HERE / 'caller.py', 49152, meter)
    need(digest(self_raw) == a['callerSHA256'], 'caller-source-identity')
    auth_raw = read_file(AUTH, 16384, meter, True)
    need(digest(auth_raw) == a['producerAuthorizationSHA256'], 'producer-root-auth-pin')
    auth = decode(auth_raw, 96, meter)
    need(set(auth) == AUTH_KEYS and auth['authorized'] is True and
         auth['schema'] == 'T03_METADATA_PROBE_BUILD_AUTH_V1' and
         auth['scope'] == 'ONE_COMPILE_AND_FIVE_STATIC_CHECKS_NO_EXPERIMENT_EXECUTION' and
         auth['sourceRef'] == '2b724f0188c233de5c8ef107d39fe0c4cb50311f' and
         auth['sourceSHA256'] == '6b6ff0969396c243c425dca507d0ea05732a0edb0123a264ab834cd2531690dd' and
         auth['inputProcessRef'] == a['inputProcessRef'] and
         auth['identityManifestSHA256'] == PIN_MANIFEST and auth['identityDescriptorSHA256'] == PIN_DESCRIPTOR,
         'producer-auth-exact-reference')
    expected_auth = {'runtimeMetadataReserved': 167000, 'freshFutureAllPartiesMetadataAccepted': 806000,
                     'freshFutureByteProposalAccepted': 171966464, 'freshFutureEntityAccepted': 737280,
                     'ownerClosureMetadataAccepted': 103000, 'peerMetadataEachAccepted': 268000,
                     'runtimeOwnerBytes': 41943040, 'preparedIdentityHistoricalCapBytes': 150994944,
                     'reusePreparedIdentityHashesMetadataOnly': True,
                     'dependencyMode': 'CAPTURE_REUSE_PINNED_WITNESS_AND_DEFER_UNKNOWN_NO_INDEX_READ'}
    for key, value in expected_auth.items():
        need(type(auth[key]) is type(value) and auth[key] == value, 'original-funding-profile')
    controls = {}
    for name, item in CONTROLS.items():
        raw_control = read_file(D / item[0], item[1], meter)
        need(len(raw_control) == item[1] and digest(raw_control) == item[2], 'frozen-source-control-pin')
        controls[name] = item[2]
        if name in ('run-once.py', 'call-plan.json'):
            controls[name + ':raw'] = raw_control
    auth_control = {'runnerSHA256': 'run-once.py', 'planSHA256': 'call-plan.json',
                    'meterPlanSHA256': 'meter-plan.json', 'historyLedgerSHA256': 'meter-history.json',
                    'countingProofSHA256': 'meter-proof.md', 'reviewMethodPlanSHA256': 'method-plan.json'}
    for key, value in auth_control.items():
        need(auth[key] == controls[value], 'producer-control-authority-pin')
    pins_raw = read_file(D / 'approved-identity-pins.json', 62664, meter)
    need(digest(pins_raw) == PIN_MANIFEST, 'approved-identity-manifest-metadata')
    token = digest(auth_raw + controls['call-plan.json:raw'] + controls['run-once.py:raw'] + pins_raw)
    need(token == a['outputToken'], 'actual-producer-token')
    if role == 'producer':
        cfg_path = AUTH
        cfg = auth
        cfg_raw = auth_raw
        argv = [INTERPRETER, '-I', '-S', '-B', str(D / 'run-once.py')]
    else:
        cfg_path = ROOT / ('T03-metadata-contract-probe-' + role + '-config.json')
        cfg_raw = read_file(cfg_path, 32768, meter, True)
        cfg = decode(cfg_raw, 256, meter)
        keys = CFG_KEYS | ({'expectedPeerIdentities', 'peerCompletionSHA256'} if role == 'owner' else set())
        need(set(cfg) == keys and cfg['schema'] == 'T03_SAVED_ORIGINAL_REVIEW_AUTH_V1' and
             cfg['authorized'] is True and cfg['role'] == role and cfg['inputProcessRef'] == a['inputProcessRef'] and
             cfg['reviewerIdentity'] == ids[role] and cfg['outputToken'] == token and
             cfg['outputRoot'] == str(OUT / token) and cfg['reviewOutputRoot'] == str(REVIEW / token / role) and
             cfg['producerAuthorizationSHA256'] == digest(auth_raw) and
             cfg['producerIdentityManifestSHA256'] == PIN_MANIFEST, 'actual-role-config-binding')
        need(type(cfg['metadataTicket']) is int and cfg['metadataTicket'] == (103000 if role == 'owner' else 268000) and
             type(cfg['byteTicket']) is int and cfg['byteTicket'] == (54525952 if role == 'owner' else 37748736),
             'original-role-ticket')
        attempt_raw = read_file(D / 'execution-attempt.json', 16384, meter)
        controls['execution-attempt.json'] = digest(attempt_raw)
        need(cfg['controlPins'] == {k: v for k, v in controls.items() if not k.endswith(':raw')},
             'all-eight-actual-control-pins')
        imports = cfg['acceptedCompilerGeneratedImports']
        need(type(imports) is list and len(imports) <= 128, 'generated-imports-cap')
        for name in imports:
            need(type(name) is str and len(name) <= 1024 and '_nl_' not in name and '_napi_' not in name,
                 'root-approved-generated-import-name')
        if role == 'owner':
            need(cfg['expectedPeerIdentities'] == {k: ids[k] for k in ('peer-a', 'peer-b')},
                 'actual-distinct-peer-identities')
        argv = [INTERPRETER, '-I', '-S', '-B', str(D / CONTROLS['review-saved.py'][0]), role, str(cfg_path)]
    need(digest(cfg_raw) == a['configSHA256'] and a['argv'] == argv and a['cwd'] == str(WORK) and
         a['environment'] == ENV, 'exact-config-argv-cwd-environment')
    expected_stat = a['interpreterStat']
    need(type(expected_stat) is dict and set(expected_stat) == {'device', 'inode', 'size', 'mtime_ns', 'mode'},
         'approved-interpreter-metadata-shape')
    need(all(type(v) is int and v >= 0 for v in expected_stat.values()), 'interpreter-exact-integer-metadata')
    real_stat = os.stat(REAL_INTERPRETER, follow_symlinks=False)
    alias_stat = os.stat(INTERPRETER)
    need(stat.S_ISREG(real_stat.st_mode) and not (stat.S_IMODE(real_stat.st_mode) & 0o022) and
         identity(alias_stat) == identity(real_stat) and
         expected_stat == {'device': real_stat.st_dev, 'inode': real_stat.st_ino, 'size': real_stat.st_size,
                           'mtime_ns': real_stat.st_mtime_ns, 'mode': stat.S_IMODE(real_stat.st_mode)},
         'actual-approved-interpreter-metadata')
    return a, cfg, argv, cfg_path


def predecessors(role, a, cfg, meter):
    prior = () if role == 'producer' else ('producer',) if role in ('peer-a', 'peer-b') else ('producer', 'peer-a', 'peer-b')
    need(type(a['predecessorTerminalSHA256']) is dict and set(a['predecessorTerminalSHA256']) == set(prior),
         'exact-predecessor-terminal-set')
    need(type(a['predecessorOuterExitCodes']) is dict and set(a['predecessorOuterExitCodes']) == set(prior) and
         type(a['predecessorRootObservationSHA256']) is dict and set(a['predecessorRootObservationSHA256']) == set(prior),
         'actual-root-observed-outer-terminal-set')
    peers = ('peer-a', 'peer-b') if role == 'owner' else ()
    need(type(a['predecessorCompletionSHA256']) is dict and set(a['predecessorCompletionSHA256']) == set(peers),
         'exact-predecessor-completion-set')
    for name in prior:
        need(type(a['predecessorOuterExitCodes'][name]) is int and a['predecessorOuterExitCodes'][name] == 0,
             'actual-prior-caller-root-observed-exit')
        observed = read_file(ROOT / ('T03-parent-' + a['outputToken'] + '-' + name + '-observation.json'),
                             16384, meter, True)
        need(hex_text(a['predecessorRootObservationSHA256'][name], 64) and
             digest(observed) == a['predecessorRootObservationSHA256'][name], 'root-actual-observation-file-pin')
        raw = read_file(PARENT / a['outputToken'] / name / 'terminal.json', 16384, meter, True)
        need(digest(raw) == a['predecessorTerminalSHA256'][name], 'actual-predecessor-terminal-pin')
        terminal = decode(raw, 96, meter)
        need(terminal['status'] == 'COMPLETE_PENDING_EXTERNAL_GATES' and terminal['role'] == name and
             terminal['inputProcessRef'] == a['inputProcessRef'] and terminal['outputToken'] == a['outputToken'] and
             terminal['actualExitCode'] == 0 and terminal['signal'] is None and terminal['firstError'] is None and
             terminal['cleanupErrors'] == [] and terminal['streamsComplete'] is True and
             terminal['stderrBytes'] == 0, 'predecessor-real-clean-terminal-required')
    for name in peers:
        raw = read_file(REVIEW / a['outputToken'] / name / 'completion.json', 16384, meter, True)
        actual = digest(raw)
        need(actual == a['predecessorCompletionSHA256'][name] == cfg['peerCompletionSHA256'][name],
             'owner-actual-peer-completion-pins')


def stop_owned(proc, errors):
    """Never reconstruct a PID or use process groups. Descendants remain UNKNOWN."""
    if proc is None:
        return
    try:
        if proc.poll() is not None:
            return
    except BaseException as exc:
        errors.append(error_value('owned-poll-unknown-no-signal', exc))
        return
    try:
        proc.terminate()
        proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
            proc.wait(timeout=1)
        except BaseException as exc:
            errors.append(error_value('owned-kill-wait', exc))
    except BaseException as exc:
        errors.append(error_value('owned-terminate-wait', exc))


def capture(proc, outfd, meter, timeout):
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    saved = {'stdout': {'bytes': 0, 'hash': hashlib.sha256()},
             'stderr': {'bytes': 0, 'hash': hashlib.sha256()}}
    meter.bytes(262144)  # Both complete 64KiB streams, read plus raw write, before access.
    selector = selectors.KqueueSelector()
    handles = {}
    errors = []
    first = None
    eof = {'stdout': False, 'stderr': False}
    deadline = time.monotonic() + timeout
    try:
        for name, pipe in (('stdout', proc.stdout), ('stderr', proc.stderr)):
            handles[name] = os.open(name + '.raw', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                    0o600, dir_fd=outfd)
            os.set_blocking(pipe.fileno(), False)
            selector.register(pipe, selectors.EVENT_READ, name)
        while not all(eof.values()):
            remaining_time = deadline - time.monotonic()
            need(remaining_time > 0, 'parent-hard-timeout')
            meter.selecting()
            ready = selector.select(remaining_time)
            need(len(ready) <= 2, 'two-owned-pipes-only')
            for key, unused in ready:
                meter.event()
                name = key.data
                remaining = 65536 - len(streams[name])
                need(remaining > 0, 'raw-exact-cap-incomplete')
                raw = os.read(key.fd, remaining)
                if not raw:
                    eof[name] = True
                    selector.unregister(key.fileobj)
                    continue
                streams[name].extend(raw)
                offset = 0
                while offset < len(raw):
                    meter.writing()
                    written = os.write(handles[name], raw[offset:])
                    need(written > 0, 'raw-zero-write')
                    saved[name]['hash'].update(raw[offset:offset + written])
                    saved[name]['bytes'] += written
                    offset += written
        remaining_time = deadline - time.monotonic()
        need(remaining_time > 0, 'parent-hard-timeout-after-eof')
        proc.wait(timeout=remaining_time)
    except BaseException as exc:
        first = error_value('capture-or-wait', exc)
        stop_owned(proc, errors)
    finally:
        for name in ('stdout', 'stderr'):
            if name in handles:
                try:
                    os.fsync(handles[name])
                except BaseException as exc:
                    errors.append(error_value('raw-fsync-' + name, exc))
                try:
                    os.close(handles[name])
                except BaseException as exc:
                    errors.append(error_value('raw-close-' + name, exc))
        try:
            selector.close()
        except BaseException as exc:
            errors.append(error_value('selector-close', exc))
        for pipe in (proc.stdout, proc.stderr):
            try:
                pipe.close()
            except BaseException as exc:
                errors.append(error_value('pipe-close', exc))
    persisted = {name: {'bytes': saved[name]['bytes'], 'sha256': saved[name]['hash'].hexdigest(),
                        'created': name in handles}
                 for name in ('stdout', 'stderr')}
    return streams, all(eof.values()), first, errors, persisted


def complete_reader(role, a, cfg, child_stderr, code, meter):
    out = REVIEW / a['outputToken'] / role
    fd = directory(out, True)
    first = None
    cleanup = []
    result = None
    try:
        write_bytes(fd, 'method.stderr', bytes(child_stderr), meter)
        facts_raw = read_file(out / 'facts.json', 65536, meter, True)
        facts = decode(facts_raw, 256, meter)
        need(facts['role'] == role and facts['reviewerIdentity'] == cfg['reviewerIdentity'] and
             facts['inputProcessRef'] == a['inputProcessRef'] and facts['outputToken'] == a['outputToken'] and
             facts['methodSHA256'] == CONTROLS['review-saved.py'][2], 'actual-reader-facts-binding')
        report = read_file(out / 'report.md', 2097152 if role == 'owner' else 524288, meter, True)
        index_name = 'archive-manifest.json' if role == 'owner' else 'original-index.json'
        index_raw = read_file(out / index_name, 1048576, meter, True)
        need(facts['archiveManifestSHA256' if role == 'owner' else 'originalIndexSHA256'] == digest(index_raw),
             'actual-reader-index-facts-pin')
        completion = {'role': role, 'inputProcessRef': a['inputProcessRef'],
                      'readerSHA256': CONTROLS['review-saved.py'][2], 'exitCode': code,
                      'stderrSHA256': digest(child_stderr), 'factsSHA256': digest(facts_raw),
                      'indexSHA256': digest(index_raw), 'reportSHA256': digest(report)}
        record(fd, 'completion.json', completion, meter)
        good = (facts['reportSHA256'] == completion['reportSHA256'] and
                facts['status'] == 'STATIC_PROFILE_COMPLETE_PENDING_EXTERNAL_GATES' and
                facts['findings'] == [] and facts['findingsOverflow'] is False and not child_stderr and code == 0)
        result = completion, good
    except BaseException as exc:
        first = error_value('actual-reader-completion', exc)
        if isinstance(exc, Fault):
            cleanup.extend(exc.cleanup)
    finally:
        try:
            os.close(fd)
        except BaseException as exc:
            cleanup.append(error_value('reader-output-directory-close', exc))
    if first is not None or cleanup:
        raise Fault(first, cleanup)
    return result


def main():
    need(len(sys.argv) == 3 and sys.argv[0] == str(HERE / 'caller.py') and
         sys.argv[1] in ROLES and hex_text(sys.argv[2], 64),
         'exact-role-and-trusted-root-admission-digest-required')
    need(sys.executable in (INTERPRETER, REAL_INTERPRETER) and sys.flags.isolated == 1 and
         sys.flags.no_site == 1 and sys.dont_write_bytecode is True and os.getcwd() == str(WORK),
         'actual-caller-interpreter-flags-cwd')
    role, trusted_hash = sys.argv[1:]
    os.umask(0o077)
    meter = Meter(role)
    a, cfg, argv, cfg_path = admit(role, trusted_hash, meter)
    predecessors(role, a, cfg, meter)
    # This parent base is root-created 0700 in the actual execution window.
    basefd = directory(PARENT, True)
    runfd = outfd = lockfd = None
    proc = None
    first = None
    cleanup = []
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    streams_complete = False
    persisted = {'stdout': {'bytes': 0, 'sha256': digest(b''), 'created': False},
                 'stderr': {'bytes': 0, 'sha256': digest(b''), 'created': False}}
    start = end = None
    popen_returned = None
    dispatched = False
    attempted = False
    completion = None
    common = {'role': role, 'inputProcessRef': a['inputProcessRef'], 'outputToken': a['outputToken']}
    terminal_saved = False
    try:
        lockfd = os.open('active.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=basefd)
        lock_raw = (a['nonce'] + '\n').encode('ascii')
        meter.bytes(len(lock_raw))
        meter.writing()
        need(os.write(lockfd, lock_raw) == len(lock_raw), 'active-lock-short-write')
        os.fsync(lockfd)
        runfd = private_child(basefd, a['outputToken'])
        os.mkdir(role, 0o700, dir_fd=runfd)  # Permanent one-shot role claim, no exist_ok.
        outfd = os.open(role, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=runfd)
        common = {'role': role, 'inputProcessRef': a['inputProcessRef'], 'outputToken': a['outputToken'],
                  'nonce': a['nonce'], 'admissionSHA256': trusted_hash, 'configSHA256': a['configSHA256'],
                  'callerSHA256': a['callerSHA256'], 'reviewerIdentity': a['roleIdentities'][role],
                  'argv': argv, 'cwd': str(WORK), 'environment': ENV}
        record(outfd, 'planned.json', dict(common, phase='planned', occurred=True, pid=None), meter)
        noncefd = private_child(basefd, 'nonces')
        try:
            write_bytes(noncefd, a['nonce'], (role + '\n').encode('ascii'), meter)
        finally:
            os.close(noncefd)
        # Re-read actual ref and immutable root/config bytes immediately before dispatch.
        need(read_file(BRANCH, 41, meter) == (a['inputProcessRef'] + '\n').encode('ascii'), 'input-ref-changed-before-launch')
        need(digest(read_file(cfg_path, 32768, meter, True)) == a['configSHA256'], 'config-changed-before-launch')
        need(digest(read_file(ROOT / ('T03-metadata-probe-parent-' + role + '-admission.json'), 32768, meter, True)) == trusted_hash,
             'root-admission-changed-before-launch')
        check_time(a)
        record(outfd, 'dispatch-attempted.json', dict(common, phase='dispatch-attempted', occurred=True, pid=None), meter)
        attempted = True
        check_time(a)
        start = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        proc = subprocess.Popen(argv, cwd=str(WORK), env=ENV, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                close_fds=True, start_new_session=False, shell=False)
        dispatched = True
        popen_returned = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        record(outfd, 'dispatched.json', dict(common, phase='dispatched', occurred=True, pid=proc.pid), meter)
        streams, streams_complete, first, errors, persisted = capture(proc, outfd, meter, 900 if role == 'producer' else 600)
        cleanup.extend(errors)
        if first is None:
            need(proc.returncode == 0 and not streams['stderr'], 'real-child-exit-or-stderr-HOLD')
            if role != 'producer':
                completion, reader_good = complete_reader(role, a, cfg, streams['stderr'], proc.returncode, meter)
                need(reader_good, 'reader-findings-or-parent-error-HOLD')
    except BaseException as exc:
        if first is None:
            first = error_value('admitted-parent', exc)
        if isinstance(exc, Fault):
            cleanup.extend(exc.cleanup)
    finally:
        stop_owned(proc, cleanup)
        if proc is not None:
            for pipe in (proc.stdout, proc.stderr):
                try:
                    pipe.close()
                except BaseException as exc:
                    cleanup.append(error_value('parent-final-pipe-close', exc))
        end = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        code = proc.returncode if proc is not None else None
        signal = -code if type(code) is int and code < 0 else None
        actual_exit = code if type(code) is int and code >= 0 else None
        if outfd is not None:
            # Unreached stages are explicit non-observations, never invented launches.
            if not attempted:
                try:
                    record(outfd, 'dispatch-attempted.json', dict(common, phase='dispatch-attempted', occurred=False, pid=None), meter)
                except BaseException as exc:
                    cleanup.append(error_value('attempt-nonobservation-persist', exc))
            if not dispatched:
                try:
                    record(outfd, 'dispatched.json', dict(common, phase='dispatched', occurred=False, pid=None), meter)
                except BaseException as exc:
                    cleanup.append(error_value('dispatch-nonobservation-persist', exc))
            terminal = {'phase': 'terminal', 'role': role, 'inputProcessRef': a['inputProcessRef'],
                        'outputToken': a['outputToken'], 'nonce': a['nonce'], 'admissionSHA256': trusted_hash,
                        'configSHA256': a['configSHA256'], 'actualStartUTC': start if dispatched else None,
                        'popenCallStartedUTC': start, 'popenReturnedUTC': popen_returned,
                        'actualEndUTC': end, 'dispatchAttempted': attempted, 'dispatched': dispatched,
                        'timeoutSeconds': 900 if role == 'producer' else 600,
                        'timedOut': first is not None and (first['kind'] == 'TimeoutExpired' or
                        first['safeCode'] in ('parent-hard-timeout', 'parent-hard-timeout-after-eof')),
                        'pid': proc.pid if proc is not None else None, 'actualExitCode': actual_exit, 'signal': signal,
                        'streamsComplete': streams_complete, 'stdoutReadBytes': len(streams['stdout']),
                        'stderrReadBytes': len(streams['stderr']), 'stdoutBytes': persisted['stdout']['bytes'],
                        'stdoutFileCreated': persisted['stdout']['created'], 'stderrFileCreated': persisted['stderr']['created'],
                        'stderrBytes': persisted['stderr']['bytes'], 'stdoutSHA256': persisted['stdout']['sha256'],
                        'stderrSHA256': persisted['stderr']['sha256'], 'firstError': first,
                        'cleanupErrors': cleanup[:8], 'cleanupErrorsOverflow': len(cleanup) > 8,
                        'ownedLeaderReaped': proc is not None and proc.returncode is not None,
                        'descendantDrain': 'UNKNOWN', 'readerCompletionCreated': completion is not None,
                        'meter': meter.snapshot(),
                        'status': 'COMPLETE_PENDING_EXTERNAL_GATES' if dispatched and streams_complete and
                        code == 0 and first is None and not cleanup else 'HOLD_FULL_ORIGINALS_RETAINED'}
            try:
                record(outfd, 'terminal.json', terminal, meter)
                os.fsync(outfd)
                terminal_saved = True
            except BaseException as exc:
                cleanup.append(error_value('terminal-persistence', exc))
                # Fixed emergency is separate; never overwrites terminal/first cause.
                try:
                    record(outfd, 'parent-persistence-failure.json',
                           {'firstError': first, 'cleanupErrors': cleanup[:8], 'terminalSaved': False}, meter)
                except BaseException:
                    pass
            try:
                os.close(outfd)
            except BaseException as exc:
                cleanup.append(error_value('parent-role-directory-close', exc))
                terminal_saved = False
        if runfd is not None:
            try:
                os.close(runfd)
            except BaseException as exc:
                cleanup.append(error_value('parent-run-directory-close', exc))
                terminal_saved = False
        if lockfd is not None:
            try:
                os.close(lockfd)
                if proc is None or proc.returncode is not None:
                    os.unlink('active.lock', dir_fd=basefd)
                    os.fsync(basefd)
            except BaseException as exc:
                cleanup.append(error_value('parent-active-lock-release', exc))
                terminal_saved = False
        try:
            os.close(basefd)
        except BaseException as exc:
            cleanup.append(error_value('parent-base-directory-close', exc))
            terminal_saved = False
    if not terminal_saved:
        emergency = {'status': 'HOLD_PARENT_PERSISTENCE_OR_PRE_OUTPUT', 'firstError': first,
                     'cleanupErrors': cleanup[:8], 'cleanupErrorsOverflow': len(cleanup) > 8}
        os.write(2, (json.dumps(emergency, separators=(',', ':'), ensure_ascii=True) + '\n').encode('ascii'))
    return 0 if terminal_saved and dispatched and streams_complete and proc.returncode == 0 and first is None and not cleanup else 1


if __name__ == '__main__':
    try:
        result = main()
    except BaseException as exc:
        # Invalid/untrusted admission may not choose an output location. The root
        # invocation must retain this true fixed stderr and exit from its tool.
        raw_error = {'status': 'HOLD_NOT_AUTHORIZED_OR_INCOMPLETE',
                     'firstError': error_value('caller-entry', exc),
                     'cleanupErrors': exc.cleanup[:8] if isinstance(exc, Fault) else []}
        os.write(2, (json.dumps(raw_error, ensure_ascii=True, separators=(',', ':')) + '\n').encode('ascii'))
        result = 2
    sys.exit(result)
