"""PREPARED ONLY. Read saved originals; never import/dispatch an artifact.

Future root must issue a distinct role configuration and prepaid ticket.
Current preparation permits AST/text only, including this file's own checks.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import struct
import sys

WORK = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build')
STAGE = WORK / 'docs/reviews/T03/native-location-N0-build/metadata-contract-probe-build'
METHOD = STAGE / 'meter-schema-init-repair/review-methods'
OUT_BASE = WORK / 'build/native-location/metadata-contract-probe/darwin-arm64'
REVIEW_BASE = WORK / 'build/native-location/metadata-contract-probe/reviews'
SOURCE_SHA = '6b6ff0969396c243c425dca507d0ea05732a0edb0123a264ab834cd2531690dd'
WITNESS_SHA = 'c7a1c91c0d6cbb0e9f1daf087c79413c65973d5cc2c128b03a22c2196b2d3357'
SOURCE_EVIDENCE_SHA = '5afb7c58d5154e7bd6083a5c7e7c273e15f4e6176e5f65c24758fa54a5ccb176'
SDK = '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk'
TOOL = '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/'
LABELS = ('compile-link', 'file-format', 'linked-libraries', 'load-commands', 'symbol-table', 'undefined-symbols')
SUFFIXES = ('stdout', 'stderr', 'planned.json', 'dispatch-attempted.json', 'dispatched.json', 'terminal.json')


class Hold(Exception):
    pass


def need(ok, reason):
    if not ok:
        raise Hold(reason)


class Account:
    def __init__(self, role):
        self.role = role
        self.limit = 48000 if role == 'owner' else 202000
        self.reserved = self.limit  # Before configuration or any input access.
        self.used = self.files = self.json_files = self.units = 0
        self.schema_initializations = 0
        self.raw = self.records = self.artifact = self.dep = self.tail = 0
        self.tail_limit = (22 if role == 'owner' else 6) * 1048576
        self.unit_limit = 10240 if role == 'owner' else 12288
        self.json_limit = 22 if role == 'owner' else 40
        # Output construction/encoding and fixed checks prepaid, never refunded.
        self.work(8000 + 3 * 768 + 3 * 1024 if role == 'owner'
                  else 6400 + 32 * 4096 + 4096 + 8 * 13 + 3 * 2048 + 1024)
        self.raw_init_prepaid = role != 'owner'  # Set only after the complete fixed fee above.
        if role == 'owner': self.bytes(12582912, 'tail')  # Reserved external report/index/commit closure.
        self.output_caps = {'report.md': 2097152 if role == 'owner' else 524288, 'facts.json': 524288}
        if role == 'owner': self.output_caps['archive-manifest.json'] = 1048576
        else: self.output_caps['original-index.json'] = 1048576
        if role != 'owner': self.bytes(1048576, 'tail')  # External full report/facts read, never a free re-read.
        self.unwritten = set(self.output_caps)
        self.work(32 * len(self.output_caps)); self.files = len(self.output_caps)
        self.bytes(3670016 if role == 'owner' else 2097152, 'tail')  # Whole output envelopes, no refund.

    def work(self, n):
        need(type(n) is int and 0 <= n <= self.limit - self.used, 'metadata-ticket-exhausted')
        self.used += n

    def bytes(self, n, group):
        need(type(n) is int and n >= 0, 'invalid-size')
        if group == 'raw':
            need(n <= 16777216 - self.raw, 'all-13-stream-byte-cap'); self.raw += n
        elif group == 'records':
            need(n <= 8388608 - self.records, 'record-source-joint-cap'); self.records += n
        elif group == 'artifact':
            need(n <= 4194304 - self.artifact, 'artifact-cap'); self.artifact += n
        elif group == 'dep':
            need(n <= 2097152 - self.dep, 'depfile-cap'); self.dep += n
        else:
            need(group == 'tail' and n <= self.tail_limit - self.tail, 'tail-joint-cap'); self.tail += n

    def snapshot(self):
        return {'reserved': self.reserved, 'upperDebits': self.used, 'actualLogicalVisits': None,
                'noRefund': True, 'files': self.files, 'jsonFiles': self.json_files,
                'jsonUnits': self.units, 'schemaInitializations': self.schema_initializations, 'rawBytes': self.raw, 'recordSourceBytes': self.records,
                'artifactBytes': self.artifact, 'depBytes': self.dep, 'tailBytes': self.tail}


def read_once(path, group, acc, required=True, cap=None):
    need(acc.files < 72, 'file-object-cap-before-open')
    acc.work(32); acc.files += 1
    fd = None; result = None; first = None; cleanup = None
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and (cap is None or before.st_size <= cap), 'nonregular-or-oversize-input')
        acc.bytes(before.st_size, group)
        chunks = []; left = before.st_size
        while left:
            chunk = os.read(fd, min(65536, left)); need(bool(chunk), 'short-input')
            chunks.append(chunk); left -= len(chunk)
        after = os.fstat(fd)
        need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
             (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'changed-input')
        raw = b''.join(chunks)
        result = (raw, {'path': str(path), 'group': group, 'present': True, 'bytes': len(raw),
                        'sha256': hashlib.sha256(raw).hexdigest()})
    except FileNotFoundError as exc:
        if required: first = exc
        else: result = (None, {'path': str(path), 'group': group, 'present': False, 'bytes': None, 'sha256': None})
    except BaseException as exc: first = exc
    finally:
        if fd is not None:
            try: os.close(fd)
            except BaseException as exc: cleanup = exc
    if first is not None or cleanup is not None:
        raise Hold('read-first=' + (str(first)[:400] if first is not None else 'none') +
                   ';close=' + (str(cleanup)[:400] if cleanup is not None else 'none'))
    return result


def shape(raw):
    # Character-only structural precheck; no JSON field/list objects materialized.
    text = raw.decode('utf-8'); stack = []; units = 0; quoted = escaped = False
    for c in text:
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
            continue
        if c.isspace(): continue
        if stack and stack[-1][0] == '[' and stack[-1][1] and c != ']':
            units += 1; stack[-1][1] = False
        if c == '"': quoted = True
        elif c in '{[':
            units += 1; stack.append([c, c == '[']); need(len(stack) <= 12, 'json-depth')
        elif c in '}]':
            need(bool(stack) and ((c == '}' and stack[-1][0] == '{') or
                                  (c == ']' and stack[-1][0] == '[')), 'json-shape')
            stack.pop()
        elif c == ':': units += 1
        elif c == ',' and stack and stack[-1][0] == '[': stack[-1][1] = True
    need(not quoted and not stack, 'json-incomplete')
    return units


def decode(raw, acc):
    units = shape(raw)
    need(acc.json_files < acc.json_limit and units <= acc.unit_limit - acc.units,
         'joint-json-cap-before-native-decode')
    acc.work(3 * units + 8); acc.units += units; acc.json_files += 1
    # Root accepts 3U as semantic-record model, not a VM/OS/heap bound.
    return json.loads(raw)


def encode(value, unit_cap, byte_cap):
    # Its complete construction/serialization fee was prepaid at Account entry.
    parts = []; units = count = 0
    def emit(s):
        nonlocal count
        count += len(s.encode('utf-8')); need(count <= byte_cap, 'report-byte-cap'); parts.append(s)
    def reserve(n):
        nonlocal units
        need(n <= unit_cap - units, 'report-U-before-container-access'); units += n
    def visit(v, depth):
        need(depth <= 12, 'report-depth')
        if type(v) is dict:
            reserve(1 + len(v)); emit('{'); first = True
            for k, child in v.items():
                need(type(k) is str, 'report-key-type')
                if not first: emit(',')
                first = False; emit(json.dumps(k)); emit(':'); visit(child, depth + 1)
            emit('}')
        elif type(v) is list:
            reserve(1 + len(v)); emit('['); first = True
            for child in v:
                if not first: emit(',')
                first = False; visit(child, depth + 1)
            emit(']')
        else:
            need(type(v) in (str, int, bool, type(None)), 'report-scalar-type')
            if type(v) is str: need(len(v) <= 4096, 'report-string-cap')
            emit(json.dumps(v, ensure_ascii=False))
    visit(value, 0); emit('\n'); return ''.join(parts).encode('utf-8')


def save(name, raw, outfd, acc):
    need(name in acc.unwritten and len(raw) <= acc.output_caps[name], 'output-name-size-or-repeat')
    acc.unwritten.remove(name)  # Fee/file slot/byte envelope prepaid at Account entry.
    fd = None; first = cleanup = None
    try:
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=outfd)
        need(stat.S_IMODE(os.fstat(fd).st_mode) == 0o600, 'output-mode')
        need(os.write(fd, raw) == len(raw), 'output-short-write'); os.fsync(fd)
    except BaseException as exc: first = exc
    finally:
        if fd is not None:
            try: os.close(fd)
            except BaseException as exc: cleanup = exc
    if first is not None or cleanup is not None:
        raise Hold('write-first=' + (str(first)[:400] if first is not None else 'none') +
                   ';close=' + (str(cleanup)[:400] if cleanup is not None else 'none'))


def original_table(root, intake):
    # Deterministic table, no directory enumeration, sort or linear next-search.
    table = [('input/location_metadata_contract_probe.cc', 'records', True),
             ('artifacts/location_metadata_contract_probe', 'artifact', False),
             ('probe.d', 'dep', False), ('build-intent.json', 'records', False),
             ('artifact-before-static.json', 'records', False),
             ('build-terminal.json', 'records', False), ('build-failure.json', 'records', False)]
    for i, label in enumerate(LABELS):
        for suffix in SUFFIXES:
            table.append(('%02d-%s.%s' % (i, label, suffix),
                          'raw' if suffix in ('stdout', 'stderr') else 'records', False))
    return table


def lines(raw):
    # Byte windows, no splitlines/findall list of uncharged records.
    cursor = 0
    while cursor < len(raw):
        end = raw.find(b'\n', cursor)
        if end < 0: end = len(raw)
        yield raw[cursor:end].rstrip(b'\r')
        cursor = end + 1


def projection(raw):
    # A record plus twice its whitespace word count over-approximates argument,
    # symbol, command-member and regex field projection without materializing it.
    total = 0
    for line in lines(raw):
        words = 0; inside = False
        for c in line:
            if c in (9, 11, 12, 13, 32): inside = False
            elif not inside: words += 1; inside = True
        total += 1 + 2 * words
        need(total <= 4096, 'raw-projection-T-cap-preserve-full-originals')
    return total


def macho(raw):
    need(len(raw) >= 32, 'short-mach-o')
    magic, cpu, subtype, kind, ncmd, cmdbytes, flags, reserved = struct.unpack_from('<8I', raw, 0)
    need(magic == 0xfeedfacf and cpu == 0x100000c and kind == 2, 'mach-o-arm64-executable')
    need(ncmd <= 256 and 32 + cmdbytes <= len(raw), 'mach-o-command-cap')
    pos = 32; commands = []
    for unused in range(ncmd):
        need(pos + 8 <= 32 + cmdbytes, 'mach-o-command-short')
        cmd, size = struct.unpack_from('<2I', raw, pos)
        need(size >= 8 and size % 8 == 0 and pos + size <= 32 + cmdbytes, 'mach-o-command-size')
        commands.append((cmd, size)); pos += size
    need(pos == 32 + cmdbytes, 'mach-o-command-table-end')
    return commands, 9 + 3 * ncmd



def driver_argv(argv, root):
    """Consume every token with explicit arity; unsupported syntax is HOLD."""
    source = str(root / 'input/location_metadata_contract_probe.cc')
    product = str(root / 'artifacts/location_metadata_contract_probe')
    need(argv and argv[0] in (TOOL + 'clang', TOOL + 'ld'), 'driver-tool')
    cc = argv[0] == TOOL + 'clang'
    bare = ({'-cc1', '-emit-obj', '-disable-free', '-clear-ast-before-backend',
             '-disable-llvm-verifier', '-discard-value-names', '-mrelax-all',
             '-fmath-errno', '-fno-rounding-math', '-fdeprecated-macro', '-fblocks',
             '-fencode-extended-block-signature', '-fregister-global-dtors-with-atexit',
             '-fdiagnostics-show-option', '-fstack-check', '-sys-header-deps', '-vectorize-loops',
             '-vectorize-slp', '-fno-implicit-modules', '-fno-modules', '-fno-module-lazy'} if cc else
            {'-demangle', '-dynamic', '-pie', '-adhoc_codesign', '-no_deduplicate', '-lc++', '-lSystem'})
    single = ({'-triple', '-main-file-name', '-mrelocation-model', '-pic-level', '-target-sdk-version',
               '-target-cpu', '-target-feature', '-resource-dir', '-dependency-file', '-MT', '-isysroot',
               '-internal-isystem', '-internal-externc-isystem', '-fdebug-compilation-dir',
               '-fcoverage-compilation-dir', '-ferror-limit', '-stack-protector', '-fgnuc-version',
               '-fobjc-runtime', '-fmax-type-align', '-o', '-x'} if cc else
              {'-arch', '-syslibroot', '-o', '-lto_library', '-L'})
    joined = {'-std=c++17', '-mframe-pointer=non-leaf', '-ffp-contract=on', '-funwind-tables=1',
              '-debugger-tuning=lldb', '-Wundef-prefix=TARGET_OS_', '-Werror=undef-prefix'} if cc else set()
    values = {}; inputs = []; seen = set(); i = 1
    while i < len(argv):
        token = argv[i]; i += 1
        need(not token.startswith(('@', '-D', '-U')), 'response-or-macro-not-supported')
        if token in bare or token in joined:
            need(token not in seen, 'duplicate-driver-switch'); seen.add(token); continue
        if not cc and token == '-platform_version':
            need(token not in values and i + 3 <= len(argv), 'platform-arity-or-duplicate')
            values[token] = argv[i:i+3]; i += 3; continue
        if token in single:
            need(i < len(argv) and not argv[i].startswith('-'), 'missing-or-option-as-driver-value')
            value = argv[i]; i += 1
            repeatable = token in ('-target-feature', '-internal-isystem', '-internal-externc-isystem', '-L')
            need(repeatable or token not in values, 'duplicate-driver-value')
            values.setdefault(token, []).append(value)
            if token in ('-internal-isystem', '-internal-externc-isystem', '-resource-dir', '-lto_library', '-L'):
                need(os.path.isabs(value) and os.path.normpath(value) == value and
                     (value.startswith(SDK + '/') or value.startswith(TOOL.replace('/usr/bin/', '/usr/lib/'))),
                     'driver-search-path-domain')
            elif token in ('-fdebug-compilation-dir', '-fcoverage-compilation-dir'):
                need(value == str(root), 'driver-working-directory')
            elif token == '-main-file-name': need(value == 'location_metadata_contract_probe.cc', 'main-source-name')
            elif token == '-dependency-file': need(value == str(root / 'probe.d'), 'driver-depfile')
            elif token == '-MT': need(value == product, 'driver-dependency-target')
            elif token in ('-pic-level', '-ferror-limit', '-stack-protector', '-fmax-type-align'):
                need(re.fullmatch('[0-9]+', value) is not None, 'driver-numeric-value')
            elif token == '-target-feature': need(re.fullmatch('[+][A-Za-z0-9_.-]+', value) is not None, 'target-feature')
            elif token == '-target-cpu': need(value in ('apple-m1', 'generic'), 'target-cpu')
            elif token == '-mrelocation-model': need(value == 'pic', 'relocation-model')
            elif token == '-target-sdk-version': need(re.fullmatch('[0-9]+(?:[.][0-9]+){1,2}', value) is not None, 'sdk-version')
            elif token == '-fgnuc-version': need(re.fullmatch('[0-9]+(?:[.][0-9]+){1,2}', value) is not None, 'gnuc-version')
            elif token == '-fobjc-runtime': need(re.fullmatch('macosx-[0-9.]+', value) is not None, 'objc-runtime')
            continue
        need(os.path.isabs(token) and os.path.normpath(token) == token, 'unsupported-driver-token')
        inputs.append(token)
    def one(key, expected): need(values.get(key) == [expected], 'driver-value:' + key)
    if cc:
        need({'-cc1', '-emit-obj', '-std=c++17'} <= seen and inputs == [source], 'cc1-complete-source-and-mode')
        triple = values.get('-triple', [])
        need(len(triple) == 1 and re.fullmatch('arm64-apple-macosx15[.]0(?:[.]0)?', triple[0]) is not None, 'cc1-target-triple')
        one('-isysroot', SDK); one('-x', 'c++')
        output = values.get('-o', [])
        need(len(output) == 1 and output[0].startswith(str(root / 'tmp') + '/') and output[0].endswith('.o'), 'cc1-owned-object-output')
        return 'cc1', output[0]
    one('-arch', 'arm64'); one('-syslibroot', SDK); one('-o', product)
    platform = values.get('-platform_version', [])
    need(len(platform) == 3 and platform[0] == 'macos' and platform[1] in ('15.0', '15.0.0') and
         re.fullmatch('[0-9]+(?:[.][0-9]+){1,2}', platform[2]) is not None, 'ld-platform-minimum-sdk')
    need({'-dynamic', '-lc++', '-lSystem'} <= seen and len(inputs) == 1 and
         inputs[0].startswith(str(root / 'tmp') + '/') and inputs[0].endswith('.o'), 'ld-one-object-and-libraries')
    return 'ld', inputs[0]


def init_load_schemas(acc):
    """Once per peer invocation; Account prepaid4096 before config/file access."""
    need(acc.role != 'owner' and acc.raw_init_prepaid and acc.schema_initializations == 0,
         'schema-init-not-prepaid-or-repeated')
    acc.schema_initializations = 1
    raw_schemas = {
        'LC_SEGMENT_64': (0x19, 'segname vmaddr vmsize fileoff filesize maxprot initprot nsects flags'),
        'LC_SYMTAB': (2, 'symoff nsyms stroff strsize'),
        'LC_DYSYMTAB': (11, 'ilocalsym nlocalsym iextdefsym nextdefsym iundefsym nundefsym tocoff ntoc modtaboff nmodtab extrefsymoff nextrefsyms indirectsymoff nindirectsyms extreloff nextrel locreloff nlocrel'),
        'LC_LOAD_DYLINKER': (14, 'name'), 'LC_UUID': (27, 'uuid'),
        'LC_LOAD_DYLIB': (12, 'name time current compatibility'),
        'LC_BUILD_VERSION': (50, 'platform minos sdk ntools'),
        'LC_VERSION_MIN_MACOSX': (36, 'version sdk'),
        'LC_MAIN': (0x80000028, 'entryoff stacksize'),
        'LC_SOURCE_VERSION': (42, 'version'),
        'LC_FUNCTION_STARTS': (38, 'dataoff datasize'), 'LC_DATA_IN_CODE': (41, 'dataoff datasize'),
        'LC_CODE_SIGNATURE': (29, 'dataoff datasize'),
        'LC_DYLD_EXPORTS_TRIE': (0x80000033, 'dataoff datasize'),
        'LC_DYLD_CHAINED_FIXUPS': (0x80000034, 'dataoff datasize'),
        'LC_DYLD_INFO_ONLY': (0x80000022, 'rebase_off rebase_size bind_off bind_size weak_bind_off weak_bind_size lazy_bind_off lazy_bind_size export_off export_size'),
        'LC_RPATH': (0x8000001c, 'path')}
    schemas = {}
    for name, (code, spelling) in raw_schemas.items():
        allowed = set(spelling.split())
        allowed.add('cmdsize')
        # cmd has its own parser branch; all ordinary keys are unique+allowed.
        schemas[name] = (code, allowed, len(allowed) + 1)
    section_fields = set('sectname segname addr size offset align reloff nreloc flags reserved1 reserved2 reserved3'.split())
    return schemas, section_fields


def load_review(raw, product, commands, schemas, section_fields):
    """Every opened numbered command must finish a complete typed body."""
    index = -1; completed = 0; kind = None; fields = {}; section = None; sections = 0
    tool_count = 0; tool_pending = False; kinds = set(); minimum = False
    def finish():
        nonlocal minimum, completed
        if index < 0: return  # Only the initial state, before any LC header.
        need(kind is not None, 'opened-load-command-has-no-body')
        need(len(fields) == schemas[kind][2], 'missing-or-extra-load-field:' + kind)
        need(section is None or len(section) == len(section_fields), 'incomplete-section')
        if kind == 'LC_SEGMENT_64': need(sections == int(fields['nsects'], 0), 'section-count')
        if kind == 'LC_BUILD_VERSION':
            need(fields['platform'] in ('1', 'macos') and int(fields['ntools']) == tool_count and
                 tool_count <= 16 and not tool_pending, 'build-platform-tool-record-count')
            need(fields['minos'] in ('15.0', '15.0.0'), 'minimum-os'); minimum = True
        if kind == 'LC_VERSION_MIN_MACOSX':
            need(fields['version'] in ('15.0', '15.0.0'), 'minimum-os'); minimum = True
        completed += 1
    header = False
    for line in lines(raw):
        text = line.decode('utf-8').strip()
        if not text: continue
        if text == product + ':': need(not header and index == -1, 'load-header-repeat'); header = True; continue
        match = re.fullmatch('Load command ([0-9]+)', text)
        if match:
            finish(); index += 1; need(header and int(match[1]) == index and index < len(commands), 'load-index')
            kind = None; fields = {}; section = None; sections = 0; tool_count = 0; tool_pending = False; continue
        need(index >= 0, 'load-field-before-command')
        if text.startswith('cmd '):
            need(kind is None and text[4:] in schemas, 'unsupported-or-duplicate-load-kind')
            kind = text[4:]; need(schemas[kind][0] == commands[index][0], 'load-kind-binary-mismatch')
            fields['cmd'] = kind; kinds.add(kind); continue
        need(kind is not None, 'load-kind-missing')
        if text == 'Section':
            need(kind == 'LC_SEGMENT_64' and (section is None or len(section) == len(section_fields)), 'section-boundary')
            section = {}; sections += 1; continue
        match = re.fullmatch(r'([a-z][a-z0-9_]*)(?: (version))?\s+(.+)', text)
        need(match is not None, 'load-field-grammar')
        key, qualifier, value = match.groups()
        if qualifier: need(key in ('current', 'compatibility'), 'load-field-qualifier')
        if kind == 'LC_BUILD_VERSION' and key in ('tool', 'version'):
            if key == 'tool':
                need('ntools' in fields and tool_count < 16 and not tool_pending and
                     value in ('1', '2', '3', 'clang', 'swift', 'ld'), 'build-tool-id')
                tool_pending = True
            else:
                need(tool_pending and re.fullmatch('[0-9]+(?:[.][0-9]+){0,4}', value) is not None,
                     'build-tool-version'); tool_pending = False; tool_count += 1
            continue
        target = section if section is not None else fields
        permitted = section_fields if section is not None else schemas[kind][1]
        need(key in permitted and key not in target, 'unknown-or-duplicate-load-field')
        if key in ('name', 'path'):
            need(re.fullmatch(r'/[^\s]+ \(offset [0-9]+\)', value) is not None, 'load-path-offset')
        elif key == 'uuid': need(re.fullmatch('[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}', value) is not None, 'load-uuid')
        elif key in ('minos', 'sdk', 'version', 'current', 'compatibility'):
            need(re.fullmatch('[0-9]+(?:[.][0-9]+){0,4}', value) is not None, 'load-version')
        elif key in ('segname', 'sectname'):
            need(re.fullmatch('__[A-Za-z0-9_]+|', value) is not None, 'load-segment-name')
        elif key == 'platform': need(value in ('1', 'macos'), 'load-platform')
        elif key == 'time': need(re.fullmatch('[0-9]+(?: .*)?', value) is not None, 'load-timestamp')
        else:
            need(re.fullmatch('(0x[0-9a-fA-F]+|[0-9]+)(?: \(.*\))?', value) is not None, 'load-numeric-field')
        if key == 'cmdsize': need(int(value, 0) == commands[index][1], 'load-size-binary-mismatch')
        target[key] = value
    finish()
    need(completed == len(commands) and index + 1 == len(commands) and 'LC_MAIN' in kinds and minimum, 'load-command-completeness')


def raw_review(buffers, root, plan, cfg, finding, acc):
    # All files have already been read/hash-retained. Prepaid 32T plus4096 fixed initialization before any raw
    # semantic collection is built; first establish joint complete projection.
    artifact = buffers.get('artifacts/location_metadata_contract_probe')
    need(artifact is not None, 'missing-artifact')
    commands, binary_t = macho(artifact)
    total = binary_t
    for i, label in enumerate(LABELS):
        for suffix in ('stdout', 'stderr'):
            raw = buffers.get('%02d-%s.%s' % (i, label, suffix))
            need(raw is not None, 'missing-command-original')
            total += projection(raw); need(total <= 4096, 'joint-raw-binary-T-cap')
    emergency_raw = buffers['runner-emergency.stderr']
    total += projection(emergency_raw); need(total <= 4096, 'joint-raw-binary-T-cap')
    if emergency_raw: finding('runner-emergency-stream-nonempty')
    product = str(root / 'artifacts/location_metadata_contract_probe')
    source = str(root / 'input/location_metadata_contract_probe.cc')
    api = plan['sourceAPICallSites']; need(type(api) is dict and len(api) <= 128, 'source-import-profile')
    allowed = {'_' + name for name in api}
    extra = cfg.get('acceptedCompilerGeneratedImports', [])
    need(type(extra) is list and len(extra) <= 128, 'extra-import-profile')
    allowed.update(extra)
    selected = {}; driver_originals = []; undefined = set(); undefined_m = set()
    file_records = library_headers = library_rows = 0
    for i, label in enumerate(LABELS):
        for suffix in ('stdout', 'stderr'):
            raw = buffers['%02d-%s.%s' % (i, label, suffix)]
            if i == 0 and suffix == 'stdout': need(not raw, 'compiler-stdout-unexpected')
            for original in lines(raw):
                text = original.decode('utf-8').strip()
                if not text: continue
                need('\x00' not in text, 'raw-NUL')
                if i and suffix == 'stderr': raise Hold('static-tool-stderr-not-empty')
                if i == 0:
                    if text.startswith('"' + TOOL):
                        need(len(selected) < 2, 'more-than-two-selected-driver-lines')
                        argv = shlex.split(text, posix=True)
                        kind, obj = driver_argv(argv, root)
                        need(kind not in selected, 'duplicate-selected-driver-kind')
                        selected[kind] = obj; driver_originals.append(text)
                    elif text.startswith(('Apple clang version ', 'clang version ', 'Target: arm64', 'Thread model: posix',
                                          'InstalledDir: ' + TOOL.rstrip('/'), 'ignoring nonexistent directory ',
                                          'ignoring duplicate directory ', '#include "..." search starts here:',
                                          '#include <...> search starts here:', 'End of search list.', '(in-process)')):
                        pass
                    elif original.startswith((b' ', b'\t')) and text.startswith('/'):
                        # Full include-search path retained as byte-backed evidence.
                        pass
                    else: raise Hold('unrecognized-complete-compiler-verbose-line')
                elif i == 1:
                    need(text == product + ': Mach-O 64-bit executable arm64', 'file-format-grammar'); file_records += 1
                elif i == 2:
                    if text == product + ':': library_headers += 1; continue
                    library_rows += 1
                    need(re.fullmatch(r'[^\s]+ \(compatibility version [0-9.]+, current version [0-9.]+\)', text) is not None,
                         'otool-L-full-line-grammar')
                elif i == 3:
                    pass  # Complete typed per-command interpretation below.
                else:
                    if i == 5:
                        need(re.fullmatch(r'[_A-Za-z.$][_A-Za-z0-9.$]*', text) is not None, 'nm-u-full-line')
                        symbol = text; undefined.add(symbol)
                    else:
                        match = re.fullmatch(r'(?:[0-9a-fA-F]{8,16}\s+)?\([^\r\n)]+\)\s+[^\r\n]*?(?:external|private external|non-external)\s+([_A-Za-z.$][_A-Za-z0-9.$]*)(?:\s+\(from [^\r\n)]+\))?', text)
                        need(match is not None, 'nm-m-full-line'); symbol = match.group(1)
                        if '(undefined)' in text: undefined_m.add(symbol)
                    need(not symbol.startswith(('_nl_', '_napi_')), 'forbidden-product-import-or-symbol')
    need(len(selected) == 2 and 'cc1' in selected and 'ld' in selected and selected['cc1'] == selected['ld'], 'one-cc1-one-ld-same-object')
    schemas, section_fields = init_load_schemas(acc)
    load_review(buffers['03-load-commands.stdout'], product, commands, schemas, section_fields)
    need(file_records == 1 and library_headers == 1 and library_rows > 0, 'missing-or-duplicate-static-tool-content')
    need(undefined == undefined_m, 'all-undefined-symbol-sets-must-match')
    need('_fgetattrlist' in undefined and undefined <= allowed, 'unreviewed-or-missing-import')
    return total, driver_originals


def bindings(dep, root, acc):
    entries = dep['entries']; pending = dep['pendingNewPaths']
    need(type(entries) is list and len(entries) <= 1024 and type(pending) is list and len(pending) <= 64, 'D-pending-cap')
    acc.work(12 * len(entries))  # Before membership/maps/row fields/validation.
    need(dep['priorWitnessSHA256'] == WITNESS_SHA and dep['sourceEvidenceSHA256'] == SOURCE_EVIDENCE_SHA, 'binding-root-pins')
    pend = set(pending); seen = set()
    for entry in entries:
        path = entry['path']; basis = entry['basis']
        need(type(path) is str and os.path.isabs(path) and os.path.normpath(path) == path and path not in seen,
             'noncanonical-or-duplicate-binding'); seen.add(path)
        if basis == 'frozen-single-source':
            need(path == str(root / 'input/location_metadata_contract_probe.cc') and entry['sourceSHA256'] == SOURCE_SHA, 'source-binding')
        elif basis == 'prior-approved-used-witness':
            ordinal = entry['priorRowOrdinal']
            need(type(ordinal) is int and 0 <= ordinal < 880 and (path.startswith(SDK + '/') or path.startswith(TOOL.replace('/usr/bin/', '/usr/lib/clang/'))), 'prior-binding-domain-ordinal')
        elif basis == 'root-accepted-I06-SDK-pin':
            ordinal = entry['sdkEvidenceOrdinal']; need(type(ordinal) is int and 0 <= ordinal < 7, 'SDK-ordinal')
        else:
            need(basis == 'PENDING_NEW_APPROVED_RECORD_AND_LOCATOR' and path in pend, 'unknown-binding-basis')
    need(dep['uniquePaths'] == len(entries) and pend <= seen, 'binding-completeness')
    return len(pending)


def meter_check(value, expected=None):
    caps = {'preUpper': 22000, 'depUpper': 61000, 'controlUpper': 60000, 'emergencyUpper': 3000}
    total = 0
    for key, cap in caps.items():
        n = value[key]; need(type(n) is int and 0 <= n <= cap, 'meter-phase-upper:' + key); total += n
    reserved = 3000
    for flag, upper, cap in (('preReserved', 'preUpper', 22000), ('depReserved', 'depUpper', 61000),
                             ('controlReserved', 'controlUpper', 60000)):
        need(type(value[flag]) is bool and (value[flag] or value[upper] == 0), 'meter-reservation-flag')
        if value[flag]: reserved += cap
    need(value['emergencyReserved'] is True and value['noRefund'] is True and value['actualLogicalVisits'] is None,
         'meter-emergency-no-refund-actual')
    phase_flag = {'preflight': 'preReserved', 'dependency': 'depReserved', 'control': 'controlReserved', 'emergency': 'emergencyReserved'}
    phase = value['phase']; need(phase in phase_flag and value[phase_flag[phase]] is True and
          (expected is None or phase == expected), 'meter-active-phase')
    need(value['limit'] == 146000 and value['upperWorkDebits'] == total and
         value['phaseReserved'] == reserved and total <= reserved <= 146000, 'meter-total-reserved')
    for key, cap in (('inputBytesReserved', 8388608), ('recordBytesReserved', 8388608),
                     ('artifactBytesReserved', 8388608), ('captureBytesReserved', 16777216)):
        need(type(value[key]) is int and 0 <= value[key] <= cap, 'meter-byte-cap:' + key)


def profile_review(control, cfg, acc):
    meter = decode(control['meter-plan.json'], acc); history = decode(control['meter-history.json'], acc)
    need(meter['schema'] == 'T03_METADATA_PHASE_METER_V2' and meter['runtimeMetadataReserved'] == 146000 and
         meter['phaseReservations'] == {'preflight': 22000, 'dependency': 61000, 'control': 60000, 'emergency': 3000} and
         meter['futureOwnerClosureMetadataProposal'] == 48000 and meter['futureAuthorMetadataProposal'] == 202000 and
         meter['futureRootMetadataProposal'] == 202000 and meter['futureAllPartiesMetadataProposal'] == 598000 and
         meter['futureByteProposal'] == 171966464 and meter['futureEntityProposal'] == 532480 and
         meter['runtimeOwnerBytes'] == 41943040 and meter['ownerClosureBytes'] == 54525952 and
         meter['peerBytesEach'] == 37748736 and meter['noRefund'] is True and
         meter['proofSHA256'] == cfg['controlPins']['meter-proof.md'] and
         meter['reviewMethodPlanSHA256'] == cfg['controlPins']['method-plan.json'], 'meter-plan-profile-and-pins')
    need(history['schema'] == 'T03_METER_HISTORY_SEPARATE_V1' and
         history['historicalOwnerActual'] is None and history['historicalOwnerActualStatus'] == 'UNKNOWN_NOT_RETROACTIVELY_BOUNDED' and
         history['oldOwner1000Retained'] is True and history['oldOwner1000Reusable'] is False and
         history['oldRoot4000Retained'] is True and history['oldRoot4000Reusable'] is False and
         history['oldFuturePool16628Retained'] is True and history['oldBytePool256MiBRetained'] is True and
         history['allPriorFailuresUnknownAnd255Retained'] is True and
         history['historicalUnknownIsolationRetained'] == 24000 and
         history['historicalIsolationNotActualUpperOrFutureReusable'] is True and
         history['currentAuthorActual'] is None and history['currentAuthorOtherWitnessVisits'] == 'UNKNOWN_NOT_ZERO' and
         history['currentAuthorKnownTwoTraversalMinimum'] == 5280 and history['currentAuthorKnownSubticketExcessAtLeast'] == 680 and
         history['currentOwnerWitnessFailure6400Retained'] is True and
         history['currentMetadataCumulative'] == 2225263 and history['currentMetadataRemaining'] == 774737 and
         history['forwardLogicalGuard'] == 3000000 and history['freshFutureProposalNotApplied'] == 598000 and
         history['guardChangeIsNotPhysicalOrRetroactive'] is True, 'history-unknown-retained-and-fresh-only')
    return meter


def control_review(decoded, control, root, token, cfg, pins, plan, acc):
    # Entire fixed matrix covered by prepaid fixed6400; all four command stages.
    flags = plan['flags']; need(type(flags) is list and len(flags) <= 32, 'fixed-flag-count-before-construction')
    expected_flags = [x.replace('@OUT@', str(root)) for x in flags]
    wanted_env = {'PATH': '/usr/bin:/bin', 'DEVELOPER_DIR': '/Applications/Xcode.app/Contents/Developer',
                  'LANG': 'C', 'LC_ALL': 'C', 'TMPDIR': str(root / 'tmp')}
    static = (('/usr/bin/file',), ('/usr/bin/otool', '-L'), ('/usr/bin/otool', '-l'),
              ('/usr/bin/nm', '-m'), ('/usr/bin/nm', '-u'))
    attempt = decode(control['execution-attempt.json'], acc)
    need(attempt['token'] == token and attempt['dispatchAttempted'] is False and
         attempt['inputProcessRef'] == cfg['inputProcessRef'] and
         attempt['authorizationSHA256'] == cfg['producerAuthorizationSHA256'] and
         attempt['singleUseAcrossAuthorizationWhitespaceChanges'] is True, 'single-attempt-ref-token-authorization')
    meter_check(attempt['meter'], 'preflight')
    intent = decoded['build-intent.json']
    need(intent['runnerSHA256'] == cfg['controlPins']['run-once.py'] and
         intent['planSHA256'] == cfg['controlPins']['call-plan.json'] and intent['output'] == str(root) and
         intent['authorizationInputRef'] == cfg['inputProcessRef'] and
         intent['authorizationSHA256'] == attempt['authorizationSHA256'] and
         intent['identityManifestSHA256'] == cfg['producerIdentityManifestSHA256'] and
         intent['noRetry'] is True and intent['runtime'] == 'NOT_AUTHORIZED' and intent['sourceArgcIfLaterI06Runs'] == 1,
         'intent-version-ref-authority-output')
    meter_check(intent['meter'], 'control')
    captured = prior_select = prior_loop = 0; prior_meter = intent['meter']['upperWorkDebits']
    for i, label in enumerate(LABELS):
        stem = '%02d-%s' % (i, label)
        planned = decoded[stem + '.planned.json']; tried = decoded[stem + '.dispatch-attempted.json']
        dispatched = decoded[stem + '.dispatched.json']; terminal = decoded[stem + '.terminal.json']
        argv = [plan['compiler']['path']] + expected_flags if i == 0 else list(static[i - 1]) + [str(root / 'artifacts/location_metadata_contract_probe')]
        need(planned['phase'] == 'planned' and planned['dispatchAttempted'] is False and planned['pid'] is None, 'planned-stage-fields')
        need(tried['phase'] == 'dispatch-attempted' and tried['dispatchAttempted'] is True and tried['pid'] is None, 'attempted-stage-fields')
        need(dispatched['phase'] == 'dispatched' and dispatched['dispatchAttempted'] is True and
             type(dispatched['pid']) is int and dispatched['pid'] > 0 and terminal['pid'] == dispatched['pid'], 'dispatched-pid-fields')
        for item in (planned, tried, dispatched, terminal):
            need(item['index'] == i, 'all-stage-index')
            meter_check(item['meter'], 'control')
            need(prior_meter <= item['meter']['upperWorkDebits'], 'nonmonotone-command-meter')
            prior_meter = item['meter']['upperWorkDebits']
        for item in (planned, terminal):
            need(item['label'] == label and item['argv'] == argv and item['environment'] == wanted_env and
                 item['cwd'] == str(root) and item['stdout'] == str(root / (stem + '.stdout')) and
                 item['stderr'] == str(root / (stem + '.stderr')) and item['selectorBackend'] == 'KqueueSelector' and
                 item['timeoutSeconds'] == (600 if i == 0 else 30), 'complete-command-matrix')
        need(planned['captureRemainingAtStart'] == 16711680 - captured and terminal['phase'] == 'completed' and
             terminal['dispatchAttempted'] is True and terminal['leaderReturnCode'] == 0 and
             terminal['captureEOF'] == {'stdout': True, 'stderr': True} and terminal['outputComplete'] is True and
             terminal['firstFailure'] is None and not terminal.get('closeErrors') and not terminal['ownedLeaderControl'], 'success-or-EOF-incomplete')
        captured += pins[stem + '.stdout']['bytes'] + pins[stem + '.stderr']['bytes']
        select = terminal['selectCallsCombinedAfter']; loop = terminal['selectorLoopChecksCombinedAfter']
        need(type(select) is int and type(loop) is int and prior_select <= select <= 128 and prior_loop <= loop <= 134 and
             select <= loop <= select + i + 1 and terminal['captureCombinedBytesAfter'] == captured and captured <= 16711680,
             'stream-and-event-cumulative-reconciliation')
        prior_select, prior_loop = select, loop
    final = decoded['build-terminal.json']; meter_check(final['meter'], 'control')
    need(final['meter']['upperWorkDebits'] >= prior_meter and final['compilerCalls'] == 1 and final['staticCalls'] == 5 and
         final['capturedCombinedBytes'] == captured and final['experimentInvoked'] is False and final['runtime'] == 'NOT_RUN' and
         final['pendingNewPaths'] == decoded['dependency-receipt.json']['pendingNewPaths'] and
         final['dependencyClosure'] == decoded['dependency-receipt.json']['closure'], 'final-build-reconciliation')


def main():
    role = sys.argv[1] if len(sys.argv) > 1 else ''
    need(role in ('owner', 'peer-a', 'peer-b') and len(sys.argv) == 3, 'fixed-role-and-config-only')
    acc = Account(role); outfd = None; rows = []; findings = []; peer_reports = []; driver_originals = []; overflow = False
    def finding(value):
        nonlocal overflow
        if len(findings) < (128 if role == 'owner' else 32) and len(value) <= 4096:
            findings.append(value)
        else: overflow = True
    try:
        config_raw, row = read_once(Path(sys.argv[2]), 'tail', acc, cap=131072); rows.append(row)
        need(shape(config_raw) <= 256, 'role-config-U-cap')
        cfg = decode(config_raw, acc)
        need(cfg['schema'] == 'T03_SAVED_ORIGINAL_REVIEW_AUTH_V1' and cfg['authorized'] is True and cfg['role'] == role,
             'root-role-authority-required')
        need(cfg['metadataTicket'] == acc.limit and cfg['byteTicket'] == (52 if role == 'owner' else 36) * 1048576,
             'fresh-role-tickets-required')
        token = cfg['outputToken']; need(type(token) is str and re.fullmatch('[0-9a-f]{64}', token) is not None, 'token')
        root = OUT_BASE / token; intake = REVIEW_BASE / token / 'intake'; own = REVIEW_BASE / token / role
        need(cfg['outputRoot'] == str(root) and cfg['reviewOutputRoot'] == str(own), 'fixed-original-output-roots')
        # Root precreates these private role dirs; no scanning/following new paths.
        outfd = os.open(str(own), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        controls = [('run-once.py', STAGE / 'run-once.py'), ('call-plan.json', STAGE / 'call-plan.json'),
                    ('meter-plan.json', STAGE / 'meter-plan.json'), ('meter-history.json', STAGE / 'meter-history.json'),
                    ('meter-proof.md', METHOD.parent / 'meter-proof.md'), ('method-plan.json', METHOD / 'method-plan.json'),
                    ('review-saved.py', Path(__file__).absolute()), ('execution-attempt.json', STAGE / 'execution-attempt.json')]
        control = {}
        for name, path in controls:
            raw, row = read_once(path, 'tail', acc, cap=65536); rows.append(row)
            need(row['sha256'] == cfg['controlPins'][name], 'fixed-current-control-sha:' + name)
            control[name] = raw
        need(shape(control['method-plan.json']) <= 256, 'method-plan-U-cap')
        method = decode(control['method-plan.json'], acc)
        expected_method = {'schema': 'T03_SAVED_ORIGINAL_METHOD_V1', 'status': 'PREPARATION_ONLY_NOT_AUTHORIZED',
            'reader': 'review-saved.py', 'ownerMetadata': 48000, 'peerMetadataEach': 202000, 'runtimeMetadata': 146000,
            'jointMetadataProposal': 598000, 'totalByteProposal': 171966464, 'runtimeBytes': 41943040, 'ownerBytes': 54525952,
            'peerBytesEach': 37748736, 'fileActionsCap': 72, 'peerJSONUnits': 12288, 'peerJSONFiles': 40,
            'ownerJSONUnits': 10240, 'ownerJSONFiles': 22, 'rawProjectionCap': 4096, 'depBindingsCap': 1024,
            'peerResultUnits': 2048, 'ownerManifestUnits': 768, 'ownerResultUnits': 1024, 'peerWorstUpper': 200616,
            'ownerWorstUpper': 46576, 'priorWitnessRereadPermitted': False, 'artifactExecutionPermitted': False,
            'freshWideEntityProposal': 532480, 'rawMetadataFactor': 32, 'rawEntityFactor': 16,
            'rawInitMetadata': 4096, 'rawInitEntity': 4096, 'schemaRows': 17, 'schemaNameFields': 67, 'sectionNameFields': 12}
        for key, expected in expected_method.items(): need(method[key] == expected, 'method-profile:' + key)
        need(method['readerSHA256'] == cfg['controlPins']['review-saved.py'] and
             method['readerBytes'] == len(control['review-saved.py']), 'method-reader-identity')
        profile_review(control, cfg, acc)
        buffers = {}; pins = {}
        for name, group, required in original_table(root, intake):
            raw, row = read_once(root / name, group, acc, required); rows.append(row); buffers[name] = raw; pins[name] = row
        raw, row = read_once(intake / 'runner-emergency.stderr', 'raw', acc, cap=65536); rows.append(row); buffers['runner-emergency.stderr'] = raw
        # Full original read/hash table completed before semantic interpretation.
        decoded = {}
        for name, raw in buffers.items():
            if raw is None:
                if name != 'build-failure.json': finding('missing:' + name)
                continue
            if name.endswith('.json'):
                if role == 'owner' and not (name.endswith('.terminal.json') or name in
                     ('build-intent.json', 'dependency-receipt.json', 'artifact-before-static.json', 'build-terminal.json', 'build-failure.json')):
                    continue
                decoded[name] = decode(raw, acc)
        # dependency receipt is an additional original, not part of capture streams.
        dep_raw, row = read_once(root / 'dependency-receipt.json', 'records', acc, False); rows.append(row)
        dep = decode(dep_raw, acc) if dep_raw is not None else None
        if dep is not None: decoded['dependency-receipt.json'] = dep
        source = buffers['input/location_metadata_contract_probe.cc']
        need(pins['input/location_metadata_contract_probe.cc']['sha256'] == SOURCE_SHA, 'source-original-pin')
        terminal = decoded.get('build-terminal.json')
        if terminal is None or terminal.get('status') != 'BUILT_UNVERIFIED_STATIC_STREAMS_CAPTURED': finding('build-not-completed')
        if decoded.get('build-failure.json') is not None: finding('build-failure-present')
        if dep is None: finding('missing-dependency-receipt')
        if role != 'owner' and dep is not None:
            if bindings(dep, root, acc): finding('new-binding-identities-pending')
            if buffers.get('probe.d') is None or pins['probe.d']['sha256'] != dep['depfileSHA256']:
                finding('depfile-byte-pin-mismatch')
        before = decoded.get('artifact-before-static.json'); artifact = buffers.get('artifacts/location_metadata_contract_probe')
        if artifact is None or before is None: finding('missing-artifact-or-before-pin')
        elif pins['artifacts/location_metadata_contract_probe']['sha256'] != before['sha256'] or (terminal and terminal['artifact'] != before):
            finding('artifact-before-final-pin-mismatch')
        for i, label in enumerate(LABELS):
            item = decoded.get('%02d-%s.terminal.json' % (i, label))
            if item is None or item.get('phase') != 'completed' or item.get('firstFailure') or item.get('outputComplete') is not True:
                finding('command-incomplete:' + label)
            elif item.get('selectorBackend') != 'KqueueSelector': finding('wrong-backend:' + label)
        if role == 'owner':
            attempt = decode(control['execution-attempt.json'], acc)
            intent = decoded['build-intent.json']
            need(attempt['inputProcessRef'] == cfg['inputProcessRef'] == intent['authorizationInputRef'] and
                 attempt['token'] == token and attempt['authorizationSHA256'] == cfg['producerAuthorizationSHA256'] == intent['authorizationSHA256'] and
                 intent['runnerSHA256'] == cfg['controlPins']['run-once.py'] and intent['planSHA256'] == cfg['controlPins']['call-plan.json'] and
                 intent['identityManifestSHA256'] == cfg['producerIdentityManifestSHA256'], 'owner-original-ref-authority-binding')
            meter_check(attempt['meter'], 'preflight'); meter_check(intent['meter'], 'control')
            # Full reports read once, separately from ≤256U facts. No summary-only
            # substitution: both originals are hashed and kept in the archive.
            own_pins = {item['path']: item for item in rows[1:]}
            expected_ids = cfg['expectedPeerIdentities']
            need(expected_ids['peer-a'] != expected_ids['peer-b'], 'distinct-peer-identities-required')
            for peer in ('peer-a', 'peer-b'):
                report, row = read_once(REVIEW_BASE / token / peer / 'report.md', 'tail', acc, cap=524288); rows.append(row)
                report_sha = row['sha256']
                facts_raw, row = read_once(REVIEW_BASE / token / peer / 'facts.json', 'tail', acc, cap=524288); rows.append(row)
                facts_sha = row['sha256']
                need(shape(facts_raw) <= 256, 'peer-facts-profile-before-decode')
                facts = decode(facts_raw, acc)
                need(facts['role'] == peer and facts['outputToken'] == token and
                     facts['reviewerIdentity'] == expected_ids[peer] and facts['inputProcessRef'] == cfg['inputProcessRef'] and
                     facts['methodSHA256'] == cfg['controlPins']['review-saved.py'] and
                     facts['producerRunnerSHA256'] == cfg['controlPins']['run-once.py'] and
                     facts['methodPlanSHA256'] == cfg['controlPins']['method-plan.json'], 'independent-peer-version')
                need(report_sha == facts['reportSHA256'], 'full-peer-report-pin')
                index_raw, row = read_once(REVIEW_BASE / token / peer / 'original-index.json', 'tail', acc, cap=1048576); rows.append(row)
                index_sha = row['sha256']
                need(index_sha == facts['originalIndexSHA256'] and shape(index_raw) <= 768, 'peer-full-index-pin-and-U')
                peer_index = decode(index_raw, acc)
                peer_rows = peer_index['objects']; need(type(peer_rows) is list and len(peer_rows) == len(own_pins), 'peer-object-table-completeness')
                indexed = set()
                for item in peer_rows:
                    path = item['path']; need(path in own_pins and path not in indexed, 'peer-object-duplicate-domain'); indexed.add(path)
                    expected = own_pins[path]
                    need(item == expected, 'peer-original-bytes-presence-sha-version')
                peer_stderr, row = read_once(REVIEW_BASE / token / peer / 'method.stderr', 'tail', acc, cap=65536); rows.append(row)
                stderr_sha = row['sha256']
                completion_raw, row = read_once(REVIEW_BASE / token / peer / 'completion.json', 'tail', acc, cap=16384); rows.append(row)
                need(row['sha256'] == cfg['peerCompletionSHA256'][peer] and shape(completion_raw) <= 64, 'root-peer-completion-pin')
                completion = decode(completion_raw, acc)
                need(completion['role'] == peer and completion['inputProcessRef'] == cfg['inputProcessRef'] and
                     completion['readerSHA256'] == cfg['controlPins']['review-saved.py'] and
                     completion['factsSHA256'] == facts_sha and completion['indexSHA256'] == index_sha and
                     completion['reportSHA256'] == report_sha and completion['stderrSHA256'] == stderr_sha, 'parent-completion-all-output-pins')
                if completion['exitCode'] != 0 or peer_stderr: finding(peer + ':parent-exit-or-stderr-HOLD')
                # Each finding gets an explicit retained HOLD disposition; no
                # automatic edits, reruns or assertion that a finding is closed.
                items = facts['findings']; need(type(items) is list and len(items) <= 32, 'peer-findings-cap')
                for item in items: finding(peer + ':OPEN:' + item)
                if facts['status'] != 'STATIC_PROFILE_COMPLETE_PENDING_EXTERNAL_GATES': finding(peer + ':not-complete')
                if not report: finding(peer + ':empty-full-report')
                peer_reports.append(report.decode('utf-8'))
        else:
            plan = decode(control['call-plan.json'], acc)
            try:
                control_review(decoded, control, root, token, cfg, pins, plan, acc)
            except (Hold, KeyError, TypeError) as exc: finding('control-review:' + str(exc))
            try: unused, driver_originals = raw_review(buffers, root, plan, cfg, finding, acc)
            except Hold as exc: finding(str(exc))
        if overflow: finding('finding-cap-HOLD-full-originals-retained')
        status = 'HOLD_FULL_ORIGINALS_RETAINED' if findings or overflow else 'STATIC_PROFILE_COMPLETE_PENDING_EXTERNAL_GATES'
        report = ('# Saved-original review\n\nRole: ' + role + '\nStatus: ' + status +
                  '\n\nAll available named originals retained in place; no product dispatch.\n' +
                  '\n'.join('* OPEN: ' + x for x in findings) +
                  ('\n\n# Complete selected driver originals\n' + '\n'.join(driver_originals) if driver_originals else '') +
                  ('\n\n# Full peer report originals\n' + '\n'.join(peer_reports) if role == 'owner' else '') +
                  '\n\nActual compiler-open/loader/stub/archive identity, runtime ABI, descendant drain, designated dual-model/two-OS/CI/human/parent/remote gates remain PENDING.\n').encode('utf-8')
        need(len(report) <= (2097152 if role == 'owner' else 524288), 'full-report-size')
        facts = {'role': role, 'outputToken': token, 'inputProcessRef': cfg['inputProcessRef'],
                 'reviewerIdentity': cfg['reviewerIdentity'], 'methodSHA256': cfg['controlPins']['review-saved.py'],
                 'producerRunnerSHA256': cfg['controlPins']['run-once.py'], 'methodPlanSHA256': cfg['controlPins']['method-plan.json'],
                 'status': status, 'findings': findings,
                 'findingsOverflow': overflow, 'reportSHA256': hashlib.sha256(report).hexdigest(),
                 'originalsRetainedInPlace': True, 'parentCompletionRequired': True, 'meter': acc.snapshot()}
        if role == 'owner':
            archive = {'outputToken': token, 'retainedInPlace': True, 'objects': rows,
                       'gitCommitRequiresExactManifestIndexVerification': True}
            archive_raw = encode(archive, 768, 1048576)
            facts['archiveManifestSHA256'] = hashlib.sha256(archive_raw).hexdigest()
            save('archive-manifest.json', archive_raw, outfd, acc)
        else:
            original_index = {'outputToken': token, 'objects': rows[1:], 'retainedInPlace': True}
            index_raw = encode(original_index, 768, 1048576)
            facts['originalIndexSHA256'] = hashlib.sha256(index_raw).hexdigest()
            save('original-index.json', index_raw, outfd, acc)
        save('report.md', report, outfd, acc)
        save('facts.json', encode(facts, 1024 if role == 'owner' else 256, 524288), outfd, acc)
        return 0 if status.startswith('STATIC_PROFILE_COMPLETE') else 2
    except BaseException as exc:
        # One bounded literal/scalar failure. No cleanup scan, retry or discarded
        # tail. The root wrapper must preserve this stderr as a separate original.
        raw = ('{"status":"HOLD_REVIEW_INCOMPLETE","reason":' + json.dumps(str(exc)[:400]) + '}\n').encode()
        try: os.write(2, raw)
        except BaseException: pass
        return 2
    finally:
        if outfd is not None:
            try: os.close(outfd)
            except BaseException:
                try: os.write(2, b'{"status":"HOLD_REVIEW_DIRECTORY_CLOSE_FAILED","complete":false}\n')
                except BaseException: pass


if __name__ == '__main__':
    sys.exit(main())
