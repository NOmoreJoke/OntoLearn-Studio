# coding: utf-8
"""Dependency setup only. No application, tests, builds, or probes are run."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys

BASE = Path('/Users/kyle/Documents/工作/知爻/本体')
OUT = BASE / '.worktrees/T03-mapping/docs/reviews/T03/designated-review-physical-setup-20261022'
REGISTRY = BASE / 'iteration-control/2026-10-21-weekly-release/T03-T04-review-roots-20261022.json'
ITEMS = [x for x in json.loads(REGISTRY.read_text())['roots'] if x['module'].startswith('T03-')]
GENERATED = ['node_modules', '.venv', 'build/review-session']


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def counts(root):
    # lstat inventory counts are directory-entry observations, not OS I/O meters.
    n = {'regularFiles': 0, 'regularBytes': 0, 'directories': 0, 'symlinks': 0,
         'hardlinkedRegularFiles': 0, 'other': 0}
    inodes = set()
    for name in GENERATED:
        top = root / name
        if not top.exists():
            continue
        for folder, dirs, files in os.walk(top, followlinks=False):
            for p in [Path(folder), *(Path(folder) / x for x in dirs + files)]:
                s = p.lstat()
                key = (s.st_dev, s.st_ino)
                if key in inodes:
                    continue
                inodes.add(key)
                if stat.S_ISREG(s.st_mode):
                    n['regularFiles'] += 1
                    n['regularBytes'] += s.st_size
                    n['hardlinkedRegularFiles'] += int(s.st_nlink > 1)
                elif stat.S_ISDIR(s.st_mode):
                    n['directories'] += 1
                elif stat.S_ISLNK(s.st_mode):
                    n['symlinks'] += 1
                else:
                    n['other'] += 1
    n['uniqueObservedInodes'] = len(inodes)
    return n


def env_for(root):
    session = root / 'build/review-session'
    env = dict(os.environ)
    clear = ['ROOT_SOURCE_PATH', 'ONTOLEARN_TEST_ENGINE', 'ONTOLEARN_PACKAGED_EXECUTABLE',
             'I04_TEST_FIXTURE', 'I04_NATIVE_ISOLATED', 'I02_HMR', 'ELECTRON_RENDERER_URL',
             'UV_PROJECT_ENVIRONMENT', 'ELECTRON_OVERRIDE_DIST_PATH', 'ELECTRON_INSTALL_PLATFORM',
             'ELECTRON_INSTALL_ARCH', 'npm_config_platform', 'npm_config_arch',
             'electron_use_remote_checksums', 'npm_config_electron_use_remote_checksums']
    for key in clear:
        env.pop(key, None)
    values = {
        'PATH': str(root / 'node_modules/.bin') + ':/usr/local/bin:/Users/kyle/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
        'npm_config_cache': str(session / 'env-cache/npm'),
        'UV_CACHE_DIR': str(session / 'env-cache/uv'),
        'UV_LINK_MODE': 'copy',
        'UV_PROJECT_ENVIRONMENT': str(root / '.venv'),
        'ELECTRON_CACHE': str(session / 'env-cache/electron'),
        'electron_config_cache': str(session / 'env-cache/electron'),
        'ELECTRON_BUILDER_CACHE': str(session / 'env-cache/electron-builder'),
        'XDG_CACHE_HOME': str(session / 'env-cache/xdg'),
        'TMPDIR': str(session / 'tmp') + '/',
        'TMP': str(session / 'tmp'),
        'TEMP': str(session / 'tmp'),
        'I02_EVIDENCE': str(session / 'raw/c1-evidence.json'),
    }
    env.update(values)
    return env, values, clear


def main():
    action = sys.argv[1]
    if action == 'prepare':
        for item in ITEMS:
            root = Path(item['tree'])
            assert git(root, 'rev-parse', 'HEAD') == item['reviewHead']
            assert git(root, 'branch', '--show-current') == ''
            assert git(root, 'status', '--porcelain') == 'M AGENTS.md'
            assert hashlib.sha256((root / 'AGENTS.md').read_bytes()).hexdigest() == 'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4'
            before = counts(root)
            assert before['uniqueObservedInodes'] == 0
            session = root / 'build/review-session'
            for name in ['env-cache/npm', 'env-cache/uv', 'env-cache/electron', 'env-cache/electron-builder',
                         'env-cache/xdg', 'tmp', 'scratch', 'raw', 'reports', 'metadata']:
                (session / name).mkdir(parents=True, exist_ok=True)
            env, values, clear = env_for(root)
            shell = '#!/bin/sh\n# Source in this physical review tree; dependency setup is owner-only.\n'
            shell += 'unset ' + ' '.join(clear) + '\n'
            shell += '\n'.join('export ' + k + '=' + shlex.quote(v) for k, v in values.items()) + '\n'
            shell += 'cd ' + shlex.quote(str(root)) + '\n'
            (session / 'environment.sh').write_text(shell)
            receipt = dict(item, at=now(), beforeGenerated=before, metricMeaning='logical lstat inventory; actual OS metadata operations are UNKNOWN',
                           shell=str(session / 'environment.sh'), paths={x:str(session / x) for x in ['scratch','raw','reports','metadata','tmp','env-cache']},
                           dependencyRoots=[str(root/'node_modules'),str(root/'.venv')], productExecuted=False,
                           toolVersions={'node':'v24.15.0','npm':'11.12.1','uv':'0.11.12','python':'3.12.12'})
            dump(session / 'metadata/setup-before.json', receipt)
            dump(OUT / (root.name + '-before.json'), receipt)
        return
    item = next(x for x in ITEMS if Path(x['tree']).name == sys.argv[2])
    root = Path(item['tree'])
    session = root / 'build/review-session'
    env, _, _ = env_for(root)
    if action == 'electron':
        # The installed 44.9.0 install.js only downloads/extracts dependencies;
        # it does not launch Electron. The code was read before this action.
        env, values, clear = env_for(root)
        shell = '#!/bin/sh\n# Source only for this physical review tree.\n'
        shell += 'unset ' + ' '.join(clear) + '\n'
        shell += '\n'.join('export ' + k + '=' + shlex.quote(v) for k, v in values.items()) + '\n'
        shell += 'cd ' + shlex.quote(str(root)) + '\n'
        (session / 'environment.sh').write_text(shell)
        cmd = ['node', 'node_modules/electron/install.js']
        raw = session / 'raw/setup-3-electron.log'
        started = now()
        with raw.open('wb') as stream:
            p = subprocess.run(cmd, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
        dump(session / 'metadata/electron-command.json', {'argv':cmd,'cwd':str(root),'started':started,'ended':now(),'exitCode':p.returncode,'raw':str(raw),'productLaunched':False})
        print(json.dumps({'tree':root.name,'electronInstallExit':p.returncode}), flush=True)
        return
    if action == 'install':
        commands = [
            ['npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund'],
            ['uv', 'sync', '--frozen', '--python', '/Users/kyle/.local/bin/python3.12', '--no-managed-python', '--link-mode', 'copy'],
        ]
        receipts = []
        for index, cmd in enumerate(commands, 1):
            started = now()
            raw = session / 'raw' / ('setup-' + str(index) + '.log')
            with raw.open('wb') as stream:
                p = subprocess.run(cmd, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
            receipts.append({'argv':cmd,'cwd':str(root),'started':started,'ended':now(),'exitCode':p.returncode,'raw':str(raw)})
            dump(session / 'metadata/dependency-commands.json', receipts)
            print(json.dumps({'tree':root.name,'command':index,'exit':p.returncode}), flush=True)
        return
    if action == 'snapshot':
        dump(session / 'metadata/setup-after.json', {'at':now(),'generated':counts(root),
             'metricMeaning':'Logical unique-inode lstat inventory before writing this receipt; actual OS metadata operations UNKNOWN',
             'head':git(root,'rev-parse','HEAD'),'status':git(root,'status','--porcelain'),'productExecuted':False})
        print((session / 'metadata/setup-after.json').read_text())


if __name__ == '__main__':
    main()
