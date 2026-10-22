"""Independent pure-design inspection; no author checker or product imports.

Reads only approved design prefixes and AGENTS. Git commands are read-only.
Writes only independent-r1-* evidence under the authorized review prefix.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
OUT = ROOT / 'docs/reviews/I05/d2-business-carrier-design'
DESIGN = ROOT / 'docs/iterations/I05/d2-business-carrier-design'
BASE = 'dc3fc7768167f206e09b410da4f737199d2c5e18'
CANDIDATE = 'cedefb069ddf77e48c2764793490517ab967aae3'
PROCESS = '3f171f7d1fb481d669acb92b835b4bb96a3bc584'
LOG = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encoded(data):
    return {'bytes': len(data), 'sha256': sha(data), 'base64': base64.b64encode(data).decode('ascii')}

def command(argv):
    p = subprocess.run(argv, cwd=ROOT, capture_output=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    LOG.append({'argv': argv, 'cwd': str(ROOT), 'exit': p.returncode, 'stdout': encoded(p.stdout), 'stderr': encoded(p.stderr)})
    return p

def load(path):
    return json.loads(path.read_bytes())

def identity():
    manifest = load(OUT / 'manifest.json')
    inputs = load(OUT / 'input-identity.json')
    checks = []
    for entry in manifest['files']:
        path = entry['path']
        current = (ROOT/path).read_bytes()
        fixed = command(['/usr/bin/git', 'show', CANDIDATE+':'+path])
        checks.append({**entry, 'current': encoded(current), 'fixedBytes': len(fixed.stdout), 'fixedSha256': sha(fixed.stdout), 'gitExit': fixed.returncode, 'match': fixed.returncode == 0 and current == fixed.stdout and len(current) == entry['bytes'] and sha(current) == entry['sha256']})
    for path, ref in [('docs/reviews/I05/d2-business-carrier-design/manifest.json', CANDIDATE), ('docs/reviews/I05/d2-business-carrier-design/candidate-receipt.json', PROCESS)]:
        current = (ROOT/path).read_bytes()
        fixed = command(['/usr/bin/git', 'show', ref+':'+path])
        checks.append({'path': path, 'ref': ref, 'bytes': len(current), 'sha256': sha(current), 'match': fixed.returncode == 0 and current == fixed.stdout})
    old = []
    for entry in inputs['oldD2ImmutableInventory']:
        path = entry['path']
        data = (ROOT/path).read_bytes()
        fixed = command(['/usr/bin/git', 'show', BASE+':'+path])
        old.append({**entry, 'actualBytes': len(data), 'actualSha256': sha(data), 'gitExit': fixed.returncode, 'match': fixed.returncode == 0 and data == fixed.stdout and len(data) == entry['bytes'] and sha(data) == entry['sha256']})
    statuses = {}
    for label, argv in {
        'branch': ['/usr/bin/git', 'branch', '--show-current'],
        'head': ['/usr/bin/git', 'rev-parse', 'HEAD'],
        'status': ['/usr/bin/git', 'status', '--short'],
        'index': ['/usr/bin/git', 'diff', '--cached', '--name-only'],
        'candidatePaths': ['/usr/bin/git', 'diff', '--name-only', BASE, CANDIDATE],
        'processPaths': ['/usr/bin/git', 'diff', '--name-only', CANDIDATE, PROCESS],
    }.items():
        p = command(argv)
        statuses[label] = {'exit': p.returncode, 'stdout': p.stdout.decode('utf-8'), 'stderr': p.stderr.decode('utf-8')}
    result = {'scope': 'independent fixed Git/current/raw SHA checks only', 'newCount': len(checks), 'new': checks, 'oldCount': len(old), 'old': old, 'allMatch': all(e['match'] for e in checks+old), 'guidance': {'bytes': len((ROOT/'AGENTS.md').read_bytes()), 'sha256': sha((ROOT/'AGENTS.md').read_bytes())}, 'git': statuses}
    (OUT/'independent-r1-identity.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'newCount': len(checks), 'oldCount': len(old), 'allMatch': result['allMatch'], 'guidance': result['guidance'], 'git': statuses}, ensure_ascii=False, indent=2))

def view():
    name = sys.argv[2]
    data = load(DESIGN/name)
    if name == 'wire-grammar.json':
        for key, value in data.items():
            if key == 'definitions':
                start, stop = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, len(value))
                for definition, body in list(value.items())[start:stop]:
                    print('DEFINITION', definition, json.dumps(body, ensure_ascii=False, separators=(',', ':')))
            else:
                print(key, json.dumps(value, ensure_ascii=False, separators=(',', ':')))
    else:
        print(json.dumps(data, ensure_ascii=False, separators=(',', ':')))

try:
    if sys.argv[1] == 'identity':
        identity()
    elif sys.argv[1] == 'view':
        view()
    else:
        raise ValueError('unknown action')
finally:
    if LOG:
        (OUT/'independent-r1-commands-identity.json').write_text(json.dumps(LOG, ensure_ascii=False, indent=2)+'\n')
