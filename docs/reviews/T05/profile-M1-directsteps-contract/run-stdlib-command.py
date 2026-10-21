"""Record exact allowed static commands with original separate output streams."""

import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

tag, *argv = sys.argv[1:]
assert argv and argv[0] in ('git', 'python3')
out = Path(__file__).parent / 'commands' / tag
out.mkdir(parents=True, exist_ok=False)
record = {
    'argv': argv, 'cwd': str(Path.cwd()),
    'startedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Git/stdlib static only; no product/library/test/GUI/network',
}
(out / 'invocation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
with (out / 'stdout.raw').open('wb') as stdout, (out / 'stderr.raw').open('wb') as stderr:
    result = subprocess.run(argv, stdout=stdout, stderr=stderr, check=False)
record['exit'] = result.returncode
record['finishedUtc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
record['streams'] = {}
for name in ('stdout.raw', 'stderr.raw'):
    raw = (out / name).read_bytes()
    record['streams'][name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
(out / 'result.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tag': tag, 'exit': result.returncode}))
sys.exit(result.returncode)
