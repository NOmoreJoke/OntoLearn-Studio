"""Pure temporary-file / injected-probe fixtures. NO mount, browser or native.

Only the synthetic print stub is ever spawned; fixture success is not physical
readonly or official app evidence. Production CLI has no fixture-probe option.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load('c4_fixture_checker', ROOT / 'check-inputs.template.py')
HELPER = load('c4_fixture_helper', ROOT / 'run-tool.template.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


class FakeProbe:
    """Deliberately simulated separate device; never exposed as a CLI flag."""
    def __init__(self, device, readonly=True):
        self.device, self.readonly = device, readonly

    def inspect(self, root):
        return {'readonly': self.readonly, 'dev': self.device, 'ino': root.stat().st_ino,
                'kind': 'PURE_FIXTURE_NOT_REAL_RO'}


class Fixture:
    def __init__(self, root):
        self.root = root
        self.volume = root / 'volume'
        self.ro = self.volume / 'input'
        self.rw = root / 'runtime'
        self.image = root / 'fixture-image-not-mounted.bin'
        self.image.write_bytes(b'pure fixture image; never mounted')
        self.ro.mkdir(parents=True)
        for directory in ['runs', 'reports', 'environment/tmp', 'environment/cache', 'environment/config']:
            (self.rw / directory).mkdir(parents=True, exist_ok=True)
        for name, source in [('check-inputs.py', ROOT / 'check-inputs.template.py'),
                             ('run-tool.py', ROOT / 'run-tool.template.py')]:
            (self.ro / name).write_bytes(source.read_bytes())
        (self.ro / 'tooling').mkdir()
        (self.ro / 'tooling/owned-browser-runner.mjs').write_text('// fixture data only\n')
        for name in ['AGENTS.md', 'prompt.md', 'review-scope.md']:
            (self.ro / name).write_text('fixed fixture ' + name)
            (self.rw / name).write_bytes((self.ro / name).read_bytes())
        config = self.ro / 'config'
        config.mkdir()
        self.cache = root / 'declared-cache'
        self.cache.mkdir()
        (self.cache / 'one.txt').write_text('one dependency')
        chrome = root / 'declared-chrome'
        chrome.mkdir()
        (chrome / 'one.txt').write_text('fixture browser resource NOT EXECUTED')
        self.native = root / 'declared-native'
        self.native.mkdir()
        for i in range(164):
            (self.native / (str(i) + '.txt')).write_text('native resource fixture NOT EXECUTED')
        resource = {'resourceRoot': str(self.cache), 'files': [{'path': 'one.txt', 'copiedIdentity': self.identity(self.cache / 'one.txt')}],
                    'externalChromeRoot': str(chrome), 'externalReadOnlyResources':
                    [{'path': str(chrome / 'one.txt'), **self.identity(chrome / 'one.txt')}]}
        write_json(config / 'resources.json', resource)
        write_json(config / 'native-resources.json', {'resourceRoot': str(self.native),
                   'entries': [{'path': p.name, 'type': 'file', **self.identity(p)} for p in sorted(self.native.iterdir())]})
        self.stub = self.ro / 'tooling/print-fixture.py'
        self.stub.write_text('import json\nprint(json.dumps({"pureFixture": True}))\n')
        commands = {}
        for command in HELPER.COMMANDS:
            commands[command] = [sys.executable, '-I', '-S', '-B', str(self.stub),
                                 '--authority', 'REPLACED', '--authority-sha256', 'REPLACED',
                                 '--work-root', 'REPLACED', '--output-root', 'REPLACED']
            if command == 'browserVerify':
                commands[command] += ['--session', 'REPLACED']
        env = {'PATH': '/usr/bin:/bin', 'NO_COLOR': '1'}
        env.update({k: str(self.rw / 'environment/tmp') for k in ['TMPDIR', 'TMP', 'TEMP']})
        env['XDG_CACHE_HOME'] = str(self.rw / 'environment/cache')
        env['XDG_CONFIG_HOME'] = str(self.rw / 'environment/config')
        runtime = {'inputRoot': str(self.ro), 'taskRoot': str(self.rw), 'cwd': str(self.rw / 'environment'),
                   'environment': env, 'commands': commands,
                   'executables': {c: sys.executable for c in HELPER.COMMANDS},
                   'entryPoints': {c: str(self.stub) for c in HELPER.COMMANDS}}
        write_json(config / 'runtime-config.json', runtime)
        write_json(config / 'authority.json', {'allowedRunBase': str(self.rw / 'runs'),
                   'protectedRoots': [str(self.ro), str(self.cache)], 'allowNativeBuild': False,
                   'limits': {'combinedScratchBytes': 67108864, 'capturedLogBytes': 4194304,
                              'browserTimeoutSeconds': 180, 'nativeTimeoutSeconds': 150}})
        self.fake_device = self.rw.stat().st_dev + 77
        self.probe = FakeProbe(self.fake_device)
        self.proof = root / 'mount-source-fixture.json'
        write_json(self.proof, {'kind': 'owner-observed-hdiutil-readonly-image', 'imagePath': str(self.image),
                   'mountPoint': str(self.volume), 'device': 'FIXTURE-NOT-REAL', 'readonly': True,
                   'shadow': False, 'overlay': False})
        self.receipt_path = root / 'external-root-receipt.json'
        self.seal()

    @staticmethod
    def identity(path):
        s = path.stat()
        return {'bytes': s.st_size, 'sha256': sha(path.read_bytes()), 'mode': oct(s.st_mode & 0o7777)}

    def seal(self):
        paths = sorted(p for p in self.ro.rglob('*') if p.is_file() and p.name != 'input-manifest.json')
        manifest = {'inputRoot': str(self.ro), 'taskRoot': str(self.rw), 'selfFile': 'input-manifest.json',
                    'exclusions': [], 'files': [{'path': p.relative_to(self.ro).as_posix(), **self.identity(p)} for p in paths],
                    'directories': sorted(p.relative_to(self.ro).as_posix() for p in self.ro.rglob('*') if p.is_dir()),
                    'mirrors': [{'source': n, 'target': n} for n in ['AGENTS.md', 'prompt.md', 'review-scope.md']],
                    'resourceManifestSHA256': sha((self.ro / 'config/resources.json').read_bytes()),
                    'nativeManifestSHA256': sha((self.ro / 'config/native-resources.json').read_bytes())}
        write_json(self.ro / 'input-manifest.json', manifest)
        receipt = {'schemaVersion': 1, 'infrastructureStatus': 'actual-readonly-mount',
                   'inputRoot': str(self.ro), 'taskRoot': str(self.rw),
                   'mount': {'mountPoint': str(self.volume), 'dev': self.fake_device,
                             'ino': self.volume.stat().st_ino, 'device': 'FIXTURE-NOT-REAL',
                             'readonly': True, 'shadow': False, 'overlay': False},
                   'image': {'path': str(self.image), **self.identity(self.image)},
                   'mountObservationPath': str(self.proof), 'mountObservationSHA256': sha(self.proof.read_bytes()),
                   'inputManifestSHA256': sha((self.ro / 'input-manifest.json').read_bytes()),
                   'helperSHA256': sha((self.ro / 'run-tool.py').read_bytes()),
                   'checkerSHA256': sha((self.ro / 'check-inputs.py').read_bytes()),
                   'runnerSHA256': sha((self.ro / 'tooling/owned-browser-runner.mjs').read_bytes())}
        receipt['commandGrants'] = {c: {'status': 'CONTROLLER_GRANTED', 'command': c,
                                    'inputManifestSHA256': receipt['inputManifestSHA256'],
                                    'ownerGrantId': 'PURE_FIXTURE_NOT_ACTUAL_WINDOW'} for c in HELPER.COMMANDS}
        write_json(self.receipt_path, receipt)
        self.receipt_sha = sha(self.receipt_path.read_bytes())

    def gate(self):
        return CHECK.gate(str(self.receipt_path), self.receipt_sha, True, self.probe)

    def run(self, command='browserBuild'):
        return HELPER.run(str(self.receipt_path), self.receipt_sha, command,
                          self.probe, self_path=self.ro / 'run-tool.py')


class AdapterFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='c4-pure-fixture-')
        self.f = Fixture(Path(self.tmp.name).resolve())

    def tearDown(self):
        self.tmp.cleanup()

    def refused(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.f.gate()

    def assert_saved(self, result):
        self.assertIsNotNone(result['receipt'])
        saved = json.loads(Path(result['receipt']).read_text())
        for key in ['passed', 'firstFailure', 'childStarted', 'lockCleanup']:
            self.assertEqual(saved[key], result[key])

    def test_simulated_positive_and_real_os_refuses(self):
        self.assertTrue(self.f.gate()['passed'])
        with self.assertRaisesRegex(ValueError, 'OS_INPUT_NOT_READONLY'):
            CHECK.gate(str(self.f.receipt_path), self.f.receipt_sha)

    def test_wrong_external_pin(self):
        with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
            CHECK.gate(str(self.f.receipt_path), '0' * 64, probe=self.f.probe)

    def test_fake_non_ro(self):
        self.f.probe.readonly = False
        self.refused('OS_INPUT_NOT_READONLY')

    def test_wrong_image_source(self):
        self.f.image.write_text('different source')
        self.refused('IMAGE_IDENTITY_CHANGED')

    def test_wrong_mount_observation(self):
        proof = json.loads(self.f.proof.read_text())
        proof['imagePath'] += '.wrong'
        write_json(self.f.proof, proof)
        self.f.seal()
        self.refused('SOURCE_OBSERVATION_MISMATCH')

    def test_shadow_refused(self):
        r = json.loads(self.f.receipt_path.read_text())
        r['mount']['shadow'] = True
        write_json(self.f.receipt_path, r)
        self.f.receipt_sha = sha(self.f.receipt_path.read_bytes())
        self.refused('MOUNT_BINDING_OR_OVERLAY')

    def test_extra_file_empty_directory_and_missing_input(self):
        extra = self.f.ro / 'extra.json'
        extra.write_text('do not open unknown')
        self.refused('EXACT_FILE_SET_DRIFT')
        extra.unlink()
        directory = self.f.ro / 'unknown-directory'
        directory.mkdir()
        self.refused('EXACT_DIRECTORY_SET_DRIFT')
        directory.rmdir()
        (self.f.ro / 'prompt.md').unlink()
        self.refused('EXACT_FILE_SET_DRIFT')

    def test_input_bytes_mode_and_manifest_pin(self):
        p = self.f.ro / 'prompt.md'
        old = p.read_bytes()
        p.write_text('changed')
        self.refused('DECLARED_FILE_DRIFT')
        p.write_bytes(old)
        p.chmod(0o400)
        self.refused('DECLARED_FILE_DRIFT')
        p.chmod(0o644)
        (self.f.ro / 'input-manifest.json').write_text('{}')
        self.refused('PINNED_JSON_HASH_MISMATCH')

    def test_symlink_and_hardlink(self):
        p = self.f.ro / 'extra-link'
        p.symlink_to(self.f.rw)
        self.refused('INPUT_SYMLINK')
        p.unlink()
        os.link(self.f.ro / 'prompt.md', p)
        self.refused('INPUT_NOT_ORDINARY')

    def test_simulated_nested_device_is_rejected(self):
        original = os.stat
        def changed(path, *args, **kwargs):
            s = original(path, *args, **kwargs)
            if path == 'prompt.md' and kwargs.get('dir_fd') is not None:
                fields = list(s)
                fields[2] += 1
                return os.stat_result(fields)
            return s
        with patch.object(CHECK.os, 'stat', side_effect=changed):
            self.refused('NESTED_MOUNT_OR_DEVICE_ALIAS')

    def test_cross_root_and_mirror_drift(self):
        r = json.loads(self.f.receipt_path.read_text())
        r['taskRoot'] = str(self.f.ro)
        write_json(self.f.receipt_path, r)
        self.f.receipt_sha = sha(self.f.receipt_path.read_bytes())
        self.refused('ROOTS_OVERLAP')
        self.f.seal()
        (self.f.rw / 'AGENTS.md').write_text('writable mirror changed')
        self.refused('NONAUTHORITY_MIRROR_DRIFT')

    def test_runner_pin_and_fourth_command(self):
        (self.f.ro / 'tooling/owned-browser-runner.mjs').write_text('changed')
        self.refused('DECLARED_FILE_DRIFT')
        self.f.seal()
        cfg = json.loads((self.f.ro / 'config/runtime-config.json').read_text())
        cfg['commands']['arbitrary'] = ['anything']
        write_json(self.f.ro / 'config/runtime-config.json', cfg)
        self.f.seal()
        self.refused('THREE_COMMANDS_REQUIRED')

    def test_cli_cannot_choose_fourth_command(self):
        result = self.f.run('arbitrary')
        self.assertFalse(result['childStarted'])
        self.assertEqual(result['firstFailure'], 'THREE_COMMANDS_ONLY')

    def test_readonly_evidence_without_command_grant_cannot_start(self):
        r = json.loads(self.f.receipt_path.read_text())
        r['commandGrants'] = {}
        write_json(self.f.receipt_path, r)
        self.f.receipt_sha = sha(self.f.receipt_path.read_bytes())
        result = self.f.run()
        self.assertFalse(result['childStarted'])
        self.assertEqual(result['firstFailure'], 'EXPLICIT_COMMAND_WINDOW_GRANT_REQUIRED')
        self.assert_saved(result)

    def test_synthetic_print_only_real_process(self):
        result = self.f.run()
        self.assertTrue(result['passed'], result)
        self.assertTrue(result['childStarted'])
        self.assertEqual(result['exitCode'], 0)
        self.assert_saved(result)

    def test_not_started_input_failure_is_saved(self):
        (self.f.ro / 'prompt.md').write_text('drift')
        result = self.f.run()
        self.assertFalse(result['childStarted'])
        self.assertFalse(result['passed'])
        self.assert_saved(result)

    def test_busy_lock_is_preserved(self):
        lock = self.f.rw / 'environment/launch.lock'
        lock.write_text('foreign')
        result = self.f.run()
        self.assertFalse(result['childStarted'])
        self.assertEqual(lock.read_text(), 'foreign')
        self.assert_saved(result)

    def test_failure_then_success_keeps_both_receipts(self):
        first = self.f.run('arbitrary')
        (self.f.ro / 'prompt.md').write_text('drift')
        second = self.f.run()
        old = Path(second['receipt']).read_bytes()
        self.f.seal()
        (self.f.rw / 'prompt.md').write_bytes((self.f.ro / 'prompt.md').read_bytes())
        third = self.f.run()
        self.assertFalse(first['passed'])
        self.assertFalse(second['passed'])
        self.assertTrue(third['passed'], third)
        self.assertEqual(Path(second['receipt']).read_bytes(), old)
        self.assertNotEqual(second['receipt'], third['receipt'])

    def test_capture_exception_still_runs_post_gate(self):
        def fail(*args, **kwargs):
            args[-1](12345)
            raise OSError('synthetic setup failure')
        with patch.object(HELPER, 'capture', side_effect=fail):
            result = self.f.run()
        self.assertTrue(result['childStarted'])
        self.assertIn('postGate', result)
        self.assertEqual(result['firstFailure'], 'synthetic setup failure')
        self.assert_saved(result)

    def test_timeout_cause_wins_over_derived_nonzero(self):
        fake = {'exitCode': -15, 'captureFailure': 'ACTIVE_TIMEOUT'}
        with patch.object(HELPER, 'capture', return_value=fake):
            result = self.f.run()
        self.assertEqual(result['firstFailure'], 'ACTIVE_TIMEOUT')
        self.assertIn('postGate', result)
        self.assert_saved(result)

    def test_resource_change_after_fake_execution(self):
        def mutate(*args, **kwargs):
            (self.f.cache / 'one.txt').write_text('changed')
            return {'exitCode': 0, 'captureFailure': None}
        with patch.object(HELPER, 'capture', side_effect=mutate):
            result = self.f.run()
        self.assertFalse(result['passed'])
        self.assertIn('postGateError', result)
        self.assert_saved(result)

    def test_changed_or_missing_lock_controls_final_receipt(self):
        for mode in ['token', 'missing']:
            with self.subTest(mode=mode):
                lock = self.f.rw / 'environment/launch.lock'
                def mutate(*args, **kwargs):
                    if mode == 'token':
                        lock.write_text('foreign token')
                    else:
                        lock.unlink()
                    return {'exitCode': 0, 'captureFailure': None}
                with patch.object(HELPER, 'capture', side_effect=mutate):
                    result = self.f.run()
                self.assertFalse(result['passed'])
                self.assert_saved(result)
                if mode == 'token':
                    self.assertEqual(lock.read_text(), 'foreign token')
                    lock.unlink()

    def test_existing_cumulative_log_refuses_before_child(self):
        (self.f.rw / 'runs/old.stdout.log').write_bytes(b'x' * 4194304)
        result = self.f.run()
        self.assertFalse(result['childStarted'])
        self.assertIn('BUDGET_EXHAUSTED', result['firstFailure'])

    def test_no_cwd_code_loaded(self):
        marker = self.f.root / 'UNEXPECTED_CWD_IMPORT'
        (self.f.rw / 'environment/json.py').write_text('raise RuntimeError("cwd code executed")')
        (self.f.rw / 'environment/sitecustomize.py').write_text('raise RuntimeError("cwd code executed")')
        result = self.f.run()
        self.assertTrue(result['passed'], result)
        self.assertFalse(marker.exists())

    def test_coverage_omission_and_variant_duplicates_cannot_pass(self):
        node = '/usr/local/bin/node'
        coverage = json.loads((ROOT / 'coverage-required.json').read_text())
        script = self.f.root / 'coverage-fixture.mjs'
        script.write_text('import {coverageVerdict} from ' + json.dumps((ROOT / 'tooling/owned-browser-runner.mjs').as_uri()) + ';\n' +
            'const required=' + json.dumps(coverage, ensure_ascii=False) + ';\n' +
            'const records=required.actions.flatMap(a=>a.requiredVariants?a.requiredVariants.values.map(v=>Object.fromEntries([["name",a.id],...a.requiredVariants.keys.map((k,i)=>[k,v[i]])])):[{name:a.id}]);\n' +
            'if(!coverageVerdict(records,required).passed)throw Error("positive failed");\n' +
            'for(const action of required.actions){if(coverageVerdict(records.filter(r=>r.name!==action.id),required).passed)throw Error("missing action passed "+action.id);}\n' +
            'const duplicate=records.filter(r=>r.name!=="c4-query-value-operator");for(let i=0;i<6;i++)duplicate.push({name:"c4-query-value-operator",operator:"eq"});\n' +
            'if(coverageVerdict(duplicate,required).passed)throw Error("duplicate variant passed");\n' +
            'console.log(JSON.stringify({pureFixture:true,actions:required.actions.length,browserLaunched:false}));\n')
        result = subprocess.run([node, str(script)], capture_output=True, text=True, timeout=10,
                                env={'PATH': '/usr/bin:/bin'}, cwd=self.f.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"browserLaunched":false', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
