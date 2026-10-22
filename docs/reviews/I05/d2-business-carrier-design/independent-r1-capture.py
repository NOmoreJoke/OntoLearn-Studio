"""Capture authorized argv with lossless streams; writes only review evidence."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
out = root / 'docs/reviews/I05/d2-business-carrier-design'
label, *argv = sys.argv[1:]
assert label.startswith('independent-r1-') and '/' not in label
p = subprocess.run(argv, cwd=root, capture_output=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
def stream(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'base64': base64.b64encode(data).decode('ascii')}
record = {'argv': argv, 'cwd': str(root), 'exit': p.returncode, 'stdout': stream(p.stdout), 'stderr': stream(p.stderr)}
(out/(label+'.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
sys.stdout.buffer.write(p.stdout)
sys.stderr.buffer.write(p.stderr)
sys.exit(p.returncode)
