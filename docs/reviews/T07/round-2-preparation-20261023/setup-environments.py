"""Preparation only: locked dependency install; never run product/test/probe code."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

owner = Path(__file__).resolve().parents[4]
prep = Path(__file__).resolve().parent
role = sys.argv[1]
row = next(r for r in json.loads((prep / 'roots.json').read_text())['roots'] if r['role'] == role)
root, rt = Path(row['root']), Path(row['runtime'])
env = os.environ.copy()
for key in ['ROOT_SOURCE_PATH', 'PYTHONPATH', 'ONTOLEARN_TEST_ENGINE', 'ONTOLEARN_DB_PATH']:
    env.pop(key, None)
env.update({'TMPDIR': str(rt/'tmp'), 'UV_CACHE_DIR': str(rt/'uv-cache'),
            'UV_PROJECT_ENVIRONMENT': str(root/'.venv'), 'npm_config_cache': str(rt/'npm-cache'),
            'RUFF_CACHE_DIR': str(rt/'ruff-cache')})
commands = [('uv-sync', ['uv','sync','--frozen','--no-python-downloads']),
            ('npm-ci', ['npm','ci','--ignore-scripts','--no-audit','--fund=false'])]
records = []
for name, argv in commands:
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    stdout, stderr = rt/'raw/setup'/f'{name}.stdout.txt', rt/'raw/setup'/f'{name}.stderr.txt'
    assert not stdout.exists() and not stderr.exists()
    with stdout.open('xb') as out, stderr.open('xb') as err:
        result = subprocess.run(argv, cwd=root, env=env, stdout=out, stderr=err)
    records.append({'argv': argv, 'cwd': str(root), 'startedAtUTC': started,
                    'completedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'exitCode': result.returncode, 'productExecuted': False,
                    'outputs': [{'path': str(p), 'bytes': p.stat().st_size,
                                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in [stdout, stderr]]})
    (rt/'metadata/setup-results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n')
    if result.returncode:
        print(json.dumps({'role': role, 'setupFailure': records[-1]}, ensure_ascii=False))
        sys.exit(result.returncode)
# Own-role probe copy gets physical module files; workspace/bin symlinks retain local relative targets.
scratch_modules = rt/'scratch/probe-copy/node_modules'
assert not scratch_modules.exists()
shutil.copytree(root/'node_modules', scratch_modules, symlinks=True)
summary = {'role': role, 'commands': records, 'nodeModulesPhysicalCopy': True,
           'nodeModulesRootInode': (root/'node_modules').stat().st_ino,
           'nodeModulesScratchInode': scratch_modules.stat().st_ino,
           'venvInode': (root/'.venv').stat().st_ino, 'newExternalTasks': 0,
           'GUIReleased': True, 'productExecuted': False}
(prep/f'{role}-setup.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'role':role,'setupExitCodes':[r['exitCode'] for r in records],
                  'ownPhysicalModulesAndProbeCopy':True,'productExecuted':False}, ensure_ascii=False))
