"""Run only local static checks; never import or execute the product/test module."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = Path(__file__).resolve().parent
TARGET = ROOT / 'packages/engine/tests/test_semantic_profile_directsteps.py'
RUN = Path(tempfile.mkdtemp(prefix='static-final-', dir=EVIDENCE))
BASE = tempfile.mkdtemp(prefix='i05-directsteps-static-basetemp-')
ENV_KEYS = ('PATH', 'VIRTUAL_ENV', 'UV_CACHE_DIR', 'PYTHONPATH', 'I05_DIRECTSTEPS_FEE_EVIDENCE_DIR')


def stamp():
    return datetime.now(timezone.utc).isoformat()


def member(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def run(name, argv):
    packet = {'argv': argv, 'cwd': str(ROOT), 'environment': {k: os.environ.get(k) for k in ENV_KEYS}, 'basetempReserved': BASE, 'basetempUsedByPytest': False, 'start': stamp(), 'membersBefore': [member(TARGET)]}
    outcome = subprocess.run(argv, cwd=ROOT, capture_output=True)
    (RUN / (name + '.stdout.txt')).write_bytes(outcome.stdout)
    (RUN / (name + '.stderr.txt')).write_bytes(outcome.stderr)
    packet.update({'end': stamp(), 'exitCode': outcome.returncode, 'membersAfter': [member(TARGET)], 'feeEvents': 'not applicable: static check, no product imported'})
    (RUN / (name + '.json')).write_text(json.dumps(packet, indent=2, ensure_ascii=False) + '\n')
    if outcome.returncode:
        raise SystemExit(outcome.returncode)


run('ruff-check', [str(ROOT / '.venv/bin/ruff'), 'check', str(TARGET)])
run('ruff-format', [str(ROOT / '.venv/bin/ruff'), 'format', '--check', str(TARGET)])
start = stamp()
tree = ast.parse(TARGET.read_text(), filename=str(TARGET))
tests = [node.name for node in tree.body if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
assert not any(isinstance(node, ast.Attribute) and node.attr in ('skip', 'skipif', 'xfail') for node in ast.walk(tree))
fixed = json.loads((EVIDENCE / 'input-readback.json').read_text())
verified = []
for expected in fixed['sources']:
    current = member(ROOT / expected['path'])
    original = subprocess.run(['git', 'show', fixed['adoption'] + ':' + expected['path']], cwd=ROOT, check=True, capture_output=True).stdout
    assert current['bytes'] == expected['bytes'] and current['sha256'] == expected['sha256'], expected['path']
    assert hashlib.sha256(original).hexdigest() == current['sha256'], expected['path']
    verified.append(current)
assert len(verified) == 139
(RUN / 'ast-fixed-inputs.json').write_text(json.dumps({'argv': ['stdlib ast.parse (no imports)', '139 local read_bytes + git show adoption:path'], 'cwd': str(ROOT), 'environment': {k: os.environ.get(k) for k in ENV_KEYS}, 'start': start, 'end': stamp(), 'exitCode': 0, 'testFunctionCount': len(tests), 'testFunctions': tests, 'target': member(TARGET), 'all139Unchanged': True, 'members': verified, 'pytestRun': False, 'productImports': False, 'feeEvents': 'not applicable: static checks only'}, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'run': str(RUN), 'testFunctions': len(tests), 'all139Unchanged': True, 'test': member(TARGET)}, ensure_ascii=False))
