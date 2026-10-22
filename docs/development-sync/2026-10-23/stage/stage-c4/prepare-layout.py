"""Prepare ordinary trees ONLY. No image creation, mounting, OS discovery or tool run.

Rebuild from the exact C3 716-row manifests, never walk/copy the old subject.
All old instructions are retained as history; C4's authority chain is separate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parent
C3_PINS = {'zcode': '8057b158af78caa5984052e75121c34922c275873239d3f122d45a23f17303ca',
           'minimax': 'dbe1a37dc1cf600d0f58cce201d014192230e63d433ea1be7bed1a87b92f6c9e'}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def read_ordinary(path):
    for q in [*reversed(path.parents), path]:
        require(not stat.S_ISLNK(q.lstat().st_mode), 'SOURCE_ANCESTOR_LINK')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'SOURCE_NOT_ORDINARY')
        parts = []
        while True:
            body = os.read(fd, 1024 * 1024)
            if not body:
                break
            parts.append(body)
        after = os.fstat(fd)
        require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'SOURCE_CHANGED')
        return b''.join(parts), stat.S_IMODE(before.st_mode)
    finally:
        os.close(fd)


def put(path, body, mode=0o644):
    safe_mkdir(path.parent)
    parent = path.parent.stat()
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        current = os.fstat(fd)
        require((parent.st_dev, parent.st_ino) == (current.st_dev, current.st_ino), 'OUTPUT_PARENT_CHANGED')
        out = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=fd)
        with os.fdopen(out, 'wb') as f:
            f.write(body)
            os.fchmod(f.fileno(), mode)
    finally:
        os.close(fd)


def safe_mkdir(path):
    require(path == ROOT or ROOT in path.parents, 'OUTPUT_OUTSIDE_EXCLUSIVE_PREFIX')
    for q in [*reversed(path.parents), path]:
        try:
            s = q.lstat()
        except FileNotFoundError:
            require(q == ROOT or ROOT in q.parents, 'MISSING_EXTERNAL_OUTPUT_ANCESTOR')
            q.mkdir()
            s = q.lstat()
        require(stat.S_ISDIR(s.st_mode) and not stat.S_ISLNK(s.st_mode), 'OUTPUT_ANCESTOR_LINK_OR_NOT_DIRECTORY')


def put_json(path, value):
    put(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def row(path, base):
    body, mode = read_ordinary(path)
    return {'path': path.relative_to(base).as_posix(), 'bytes': len(body),
            'sha256': sha(body), 'mode': oct(mode)}


def prepare_party(party, spec):
    source = Path(spec['c3Source'])
    require(source == ROOT.parent / '20261022_stage_review_c3' / party, 'EXACT_C3_SOURCE_ONLY')
    original_manifest_body, _ = read_ordinary(source / 'input-manifest.json')
    require(sha(original_manifest_body) == C3_PINS[party], 'C3_MANIFEST_PIN')
    original = json.loads(original_manifest_body)
    # C3's pinned manifest has an explanatory exclusions object for its runtime
    # directories/self-reference. Preserve it as history, never use it to walk
    # or filter the source; only these 716 exact declared rows are copied.
    require(len(original['files']) == 716 and isinstance(original.get('exclusions'), dict),
            'EXACT_PINNED_C3_716_SCHEMA_REQUIRED')
    volume_tree = Path(spec['preparedVolumeTree'])
    require(volume_tree == ROOT / 'prepared' / party / 'volume-root' and not volume_tree.exists(),
            'NEW_EXCLUSIVE_PREPARED_TREE_REQUIRED')
    stage = volume_tree / 'input'
    safe_mkdir(stage)
    mapping = []
    seen = set()
    for item in original['files']:
        relative = Path(item['path'])
        require(not relative.is_absolute() and '..' not in relative.parts and
                relative.as_posix() == item['path'] and item['path'] not in seen, 'UNSAFE_OR_DUPLICATE_C3_PATH')
        seen.add(item['path'])
        old = source / relative
        body, mode = read_ordinary(old)
        require(len(body) == item['bytes'] and sha(body) == item['sha256'] and oct(mode) == item['mode'],
                'C3_DECLARED_SOURCE_DRIFT ' + item['path'])
        new = stage / 'c3-input' / relative
        put(new, body, mode)
        require(new.stat().st_ino != old.stat().st_ino, 'COPY_NOT_INDEPENDENT')
        mapping.append({'source': str(old), 'sourceRelative': item['path'],
                        'destination': 'c3-input/' + item['path'], 'status': 'exact_c3_bytes_and_mode_preserved',
                        'bytes': len(body), 'sha256': sha(body), 'mode': oct(mode)})
    put(stage / 'history-c3-original-manifest.json', original_manifest_body)
    put_json(stage / 'c3-716-mapping.json', {'schemaVersion': 1, 'party': party,
             'originalManifestSHA256': C3_PINS[party], 'mappingCount': 716, 'mapping': mapping,
             'oldUnknownExtraPathsNeverEnumeratedReadHashedCopiedOrDeleted': True})
    history_index = ROOT.parent / '20261022_stage_review_c3/execution-evidence/c3-terminal-owner-handoff-index.json'
    index_body, _ = read_ordinary(history_index)
    require(sha(index_body) == 'dc288892048b498619081b303d131e635ede42a5d702597aa00ef5d5b417409d',
            'C3_TERMINAL_HANDOFF_PIN')
    history = json.loads(index_body)
    for item in history['files']:
        old = Path(item['path'])
        require(old == history_index.parent / item['relativePath'] and '..' not in Path(item['relativePath']).parts,
                'HISTORY_REFERENCE_ESCAPE')
        body, mode = read_ordinary(old)
        require(sha(body) == item['sha256'] and len(body) == item['bytes'], 'C3_TERMINAL_HISTORY_DRIFT')
        put(stage / 'history-c3' / item['relativePath'], body, mode)
    put(stage / 'history-c3/handoff-index.json', index_body)
    for name in ['check-inputs', 'run-tool']:
        put(stage / (name + '.py'), read_ordinary(ROOT / (name + '.template.py'))[0])
    for name in ['verify-browser-c4.py', 'owned-browser-runner.mjs']:
        put(stage / 'tooling' / name, read_ordinary(ROOT / 'tooling' / name)[0])
    put(stage / 'coverage-required.json', read_ordinary(ROOT / 'coverage-required.json')[0])
    for name in ['layout-design.json', 'prepare-layout.py', 'tests/test-c4-adapter.py',
                 'mount-and-tool-read-preflight-plan.json']:
        put(stage / 'owner-preparation/c4-tools' / name, read_ordinary(ROOT / name)[0])
    ro, rw = Path(spec['inputRoot']), Path(spec['taskRoot'])
    require(rw == ROOT / 'runtime' / party and not rw.exists(), 'NEW_RUNTIME_ROOT_REQUIRED')
    for directory in ['environment/tmp', 'environment/cache', 'environment/config', 'runs', 'reports', 'owner-evidence']:
        safe_mkdir(rw / directory)
    agents = ('# C4 fixed read-only review\n\nRead the complete current prompt and scope from the pinned readonly input. '
              'The official cwd is a writable runtime root only. Its rule/launch mirrors are non-authority and must match '
              'the pinned input. Do not read global configurations, logs, other sessions, current peer opinions or old opaque streams. '
              'Do not run c3-input historical scripts except the three exact active bindings in current config. '
              'Only current readonly check-inputs/run-tool are entry points. Preserve every failure. No install, native build or GUI '
              'without a separate controller window. All original product and release gaps remain.\n')
    scope = ('# C4 complete stage scope\n\nThe full original 185-payload scope, 34 component snapshots, 58 baseline source files and '
             'imports, fixed PRD/architecture, packaging manifests and all prior failures remain mandatory review material in '
             'c3-input/subject and c3-input/common-history. c3-input prompts/configs are preserved historical text, not C4 commands. '
             'Read complete actual source to EOF; grep/head/hash or delegated summaries are not full reading. '
             'Read both old C3 reports, owner crosschecks, all findings and access limitations in history-c3. '
             'Current code additionally includes this full fixed trust chain, two-root gate/helper, readonly JS runner and coverage-required.json. '
             'Original eight groups and three prior P2 checks remain. The pinned actual entry provides synthetic alarmVocabulary: '
             'verify actual template generation against the full independent expected query without injecting vocabulary or services. '
             'If a future candidate lacks vocabulary, verify its disabled/disclosed boundary instead of manufacturing success. '
             'Preserve condition-reorder absent-control unverified note. '
             'Keep static, actual runtime, packaging and production evidence distinct. No original GUI/userData, Windows, signing or full '
             'business/release success is implied. Only both fresh actual same-version terminal reviews with full reports and dispositions '
             'can close designated dual review.\n')
    prompt = ('# C4 fresh complete independent designated review: ' + party + '\n\n'
              'Authoritative inputRoot: ' + str(ro) + '\nWritable task cwd: ' + str(rw) + '\n\n'
              'Use the external root-receipt path and SHA supplied separately in the actual launch. The image/manifest hash is not '
              'embedded here to avoid a self-reference cycle. A pending template is not actual readonly evidence. '
              'First verify readonly input, external image/source pins, exact complete input set and cwd rule mirrors using the pinned checker. '
              'Read AGENTS.md, review-scope.md, coverage-required.json and the complete current code plus all original baseline/requirements/history '
              'to EOF. All 716 old declared files are preserved with explicit mapping; extra C3 metadata is not a source or an input exception. '
              'Only browserBuild/browserVerify/nativeCLI via readonly run-tool are authorized command definitions; do not run before the controller '
              'grants the specific execution windows. No arbitrary command, install, old verifier/harness, global history or peer reading. '
              'Record actual source reading, every mandatory action or exact unverified item, first failures, identity, runtime versus static references. '
              'Write a full independent Chinese report and receipt under your writable reports, with PASS/FAIL/NEEDS_EVIDENCE. '
              'Required unverified items cannot pass. Do not query or fabricate your own final native terminal; owner provides task identity and '
              'later verifies the original turn externally. A single readonly canary Read is not Bash/helper/MiniMax/full execution proof.\n')
    for name, text in [('AGENTS.md', agents), ('review-scope.md', scope), ('prompt.md', prompt)]:
        put(stage / name, text.encode())
        put(rw / name, text.encode())
    # Use only the already verified independent copies, not a second unpinned
    # read from a live source that could have changed during preparation.
    old_cfg = json.loads(read_ordinary(stage / 'c3-input/config/runtime-config.json')[0])
    resource_body = read_ordinary(stage / 'c3-input/config/resource-manifest.json')[0]
    native_body = read_ordinary(stage / 'c3-input/config/native-resources.json')[0]
    put(stage / 'config/resources.json', resource_body)
    put(stage / 'config/native-resources.json', native_body)
    authority = {'schemaVersion': 1, 'allowedRunBase': str(rw / 'runs'),
                 'protectedRoots': [str(ro), json.loads(resource_body)['resourceRoot']],
                 'allowNativeBuild': False, 'limits': {'combinedScratchBytes': 67108864, 'capturedLogBytes': 4194304,
                                                     'browserTimeoutSeconds': 180, 'nativeTimeoutSeconds': 150}}
    put_json(stage / 'config/authority.json', authority)
    authority_sha = sha((stage / 'config/authority.json').read_bytes())
    commands, entries = {}, {}
    for command, argv in old_cfg['commands'].items():
        transformed = [x.replace(str(source) + '/', str(ro / 'c3-input') + '/') for x in argv]
        def flag(name, value):
            transformed[transformed.index(name) + 1] = value
        flag('--authority', str(ro / 'config/authority.json'))
        flag('--authority-sha256', authority_sha)
        flag('--work-root', str(rw / 'runs/REPLACED_FRESH_RUN_REQUIRED'))
        flag('--output-root', str(rw / 'runs/REPLACED_FRESH_RUN_REQUIRED/out'))
        if command == 'browserVerify':
            old_entry = str(ro / 'c3-input/subject/payload/artifacts/browser/verify-browser.py')
            entry = str(ro / 'tooling/verify-browser-c4.py')
            transformed[transformed.index(old_entry)] = entry
            transformed += ['--runner', str(ro / 'tooling/owned-browser-runner.mjs'), '--runner-sha256',
                            sha((stage / 'tooling/owned-browser-runner.mjs').read_bytes()),
                            '--coverage', str(ro / 'coverage-required.json'), '--coverage-sha256',
                            sha((stage / 'coverage-required.json').read_bytes())]
        elif command == 'browserBuild':
            entry = str(ro / 'c3-input/subject/payload/artifacts/browser/build.mjs')
        else:
            entry = str(ro / 'c3-input/subject/payload/artifacts/desktop/probe-packaged-engine.py')
            flag('--engine-resource-manifest', str(ro / 'config/native-resources.json'))
        entries[command] = entry
        commands[command] = transformed
    environment = {k: v.replace(str(source / 'environment'), str(rw / 'environment'))
                   for k, v in old_cfg['environment'].items()}
    cfg = {'schemaVersion': 1, 'party': party, 'inputRoot': str(ro), 'taskRoot': str(rw),
           'cwd': str(rw / 'environment'), 'environment': environment, 'commands': commands,
           'executables': {k: v[0] for k, v in commands.items()}, 'entryPoints': entries,
           'commandExecutionWindow': 'NOT_GRANTED; definitions only until controller separately grants',
           'branch': 'N/A', 'gitCommit': 'N/A', 'allowNativeBuild': False}
    put_json(stage / 'config/runtime-config.json', cfg)
    put_json(stage / 'candidate.json', {'label': 'stage-acceptance-20261023-review-c4', 'party': party,
             'sourceCandidateSHA256': original['candidateManifestSHA256'], 'oldDeclaredFilesPreserved': 716,
             'oldUnknownMetadataReadOrCopied': False, 'currentAuthorityFiles': ['check-inputs.py', 'run-tool.py',
             'tooling/verify-browser-c4.py', 'tooling/owned-browser-runner.mjs', 'coverage-required.json'],
             'C3ExactSetAndFullReadingAndInteractionGatesClosed': False,
             'actualReadOnlyMountProven': False, 'designatedReviewTasksCreated': 0})
    files = sorted(p for p in stage.rglob('*') if p.is_file())
    manifest = {'schemaVersion': 1, 'inputRoot': str(ro), 'taskRoot': str(rw), 'party': party,
                'selfFile': 'input-manifest.json', 'exclusions': [], 'files': [row(p, stage) for p in files],
                'directories': sorted(p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_dir()),
                'mirrors': [{'source': n, 'target': n} for n in ['AGENTS.md', 'prompt.md', 'review-scope.md']],
                'resourceManifestSHA256': sha(resource_body), 'nativeManifestSHA256': sha(native_body)}
    put_json(stage / 'input-manifest.json', manifest)
    pending = {'schemaVersion': 1, 'infrastructureStatus': 'PENDING_NOT_ACTUAL_EVIDENCE',
               'party': party, 'inputRoot': str(ro), 'taskRoot': str(rw),
               'inputManifestSHA256': sha((stage / 'input-manifest.json').read_bytes()),
               'helperSHA256': sha((stage / 'run-tool.py').read_bytes()),
               'checkerSHA256': sha((stage / 'check-inputs.py').read_bytes()),
               'runnerSHA256': sha((stage / 'tooling/owned-browser-runner.mjs').read_bytes()),
               'image': {'path': spec['imagePath'], 'sha256': 'UNKNOWN', 'bytes': None},
               'mount': {'mountPoint': spec['volumeRoot'], 'device': 'UNKNOWN', 'dev': None, 'ino': None,
                         'readonly': None, 'shadow': False, 'overlay': False},
               'mountObservationPath': 'UNKNOWN', 'mountObservationSHA256': 'UNKNOWN',
               'commandGrants': {}}
    put_json(rw / 'owner-evidence/root-receipt.PENDING.json', pending)
    return {'party': party, 'preparedOnly': True, 'mounted': False, 'actualOSROProven': False,
            'old716Mapping': 716, 'preparedFixedFilesIncludingManifest': len(files) + 1,
            'preparedInputBytes': sum(p.stat().st_size for p in stage.rglob('*') if p.is_file()),
            'inputManifestSHA256': pending['inputManifestSHA256'], 'runtimeRoot': str(rw)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--design-sha256', required=True)
    a = p.parse_args()
    design_body, _ = read_ordinary(ROOT / 'layout-design.json')
    require(sha(design_body) == a.design_sha256, 'DESIGN_PIN_MISMATCH')
    design = json.loads(design_body)
    require(design['status'] == 'TOOLS_PREPARATION_ONLY_NO_MOUNT_OR_PRODUCT_EXECUTION', 'PREPARATION_ONLY')
    result = [prepare_party(party, spec) for party, spec in design['parties'].items()]
    require(sum(x['preparedInputBytes'] for x in result) <= design['spacePlan']['bothPreparedInputTreesMaxBytes'],
            'PREPARED_INPUT_STORAGE_PLAN_EXCEEDED')
    roots = [Path(design['parties'][party]['preparedVolumeTree']) / 'input' for party in ['zcode', 'minimax']]
    manifests = [json.loads((root / 'input-manifest.json').read_text()) for root in roots]
    maps = [{x['path']: x for x in manifest['files']} for manifest in manifests]
    require(set(maps[0]) == set(maps[1]), 'TWO_SIDE_FIXED_PATH_SET_DIFFERS')
    equal, different = [], []
    for name in sorted(maps[0]):
        stats = [(root / name).stat() for root in roots]
        require((stats[0].st_dev, stats[0].st_ino) != (stats[1].st_dev, stats[1].st_ino),
                'TWO_SIDE_SHARED_INODE ' + name)
        same = all(maps[0][name][k] == maps[1][name][k] for k in ['bytes', 'sha256', 'mode'])
        (equal if same else different).append(name)
        if name.startswith(('c3-input/subject/', 'c3-input/common-history/', 'history-c3/')):
            require(same, 'TWO_SIDE_COMMON_CANDIDATE_OR_HISTORY_DIFFERS ' + name)
    put_json(ROOT / 'author-evidence/two-side-preparation-comparison.json', {
        'onlyNewPreparedTreesRead': True, 'fixedPairCount': len(maps[0]), 'independentInodePairs': len(maps[0]),
        'identicalBytesModePairs': len(equal), 'differentBindingOrPreservedOldPartyPaths': different,
        'sourceCandidateAndHistoryIdentical': True, 'physicalReadonlyClaimed': False})
    put_json(ROOT / 'author-evidence/layout-preparation-receipt.json', {'schemaVersion': 1,
             'scope': 'Declared-file copies and generated fixed authority inputs only; no images/mounts/tool or product execution.',
             'designSHA256': a.design_sha256, 'parties': result})
    print(json.dumps(result))


if __name__ == '__main__':
    main()
