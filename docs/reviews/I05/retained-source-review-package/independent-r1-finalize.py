"""Format only new independent docs/JSON; bind final metadata and stop writing."""
import base64
import datetime
import hashlib
import json
import os
import pathlib
import subprocess

TREE = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package')
ROOT = TREE / 'docs/reviews/I05/retained-source-review-package'
PROCESS = '2dd91056000c3ff7a6d102eff4a168ec5419bd1b'
PREFIX = 'docs/reviews/I05/retained-source-review-package/'
NODE = '/usr/local/bin/node'
PRETTIER = '/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs'
receipt = {'scope': 'Independent packet review and final new files only; no stage/commit/product execution.', 'commands': []}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def run(argv):
    env = dict(os.environ)
    env['NODE_DISABLE_COMPILE_CACHE'] = '1'
    cp = subprocess.run(argv, cwd=TREE, capture_output=True, env=env)
    receipt['commands'].append({'argv': argv, 'cwd': str(TREE), 'exitCode': cp.returncode, 'stdoutBase64': base64.b64encode(cp.stdout).decode(), 'stderrBase64': base64.b64encode(cp.stderr).decode(), 'stdoutBytes': len(cp.stdout), 'stderrBytes': len(cp.stderr)})
    assert cp.returncode == 0
    return cp.stdout

p = ROOT / 'independent-proof-r1.json'
proof = json.loads(p.read_bytes())
assert len(proof['findings']) == 2 and proof['packetReviewResult'].startswith('FAIL')
proof['findings'][0]['files'] = ['zcode-glm53-input.md:20', 'zcode-glm53-input.md:21', 'minimax-m31flash-input.md:20', 'minimax-m31flash-input.md:21']
proof['completionUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
proof['checkerProcessBoundary'] = {'pythonExecutable': '/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12', 'environmentOverride': {'PYTHONDONTWRITEBYTECODE': '1'}, 'cwd': str(TREE), 'firstCheckerToolChunk': '28a904', 'firstCheckerActualExit': 1, 'continuationFailedToolChunks': ['fb5b43', '493241'], 'completedContinuationToolChunk': '8f5b62', 'completedContinuationActualExit': 0, 'boundary': 'Outer tool outputs retained in conversation. Embedded subprocess streams are captured separately in commands; outer tool-only outputs are not retrospectively split.'}
p.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
formatted_names = ['independent-review-r1.md', 'independent-proof-r1.json', 'independent-r1-continuation-failure.json', 'independent-r1-queue-descriptor-interpretation.json']
paths = [str(ROOT / name) for name in formatted_names]
# Disable the formatter entrypoint's optional Node compile cache; only the exact
# new files below may be rewritten. No product module is imported or run.
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--write', *paths])
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--check', *paths])
assert run(['git', 'rev-parse', 'HEAD']).decode().strip() == PROCESS
assert run(['git', 'diff', '--cached', '--name-only', '-z']) == b''
assert run(['git', 'diff', '--name-only', '-z']).decode().split('\0') == ['AGENTS.md', '']
status = run(['git', 'status', '--porcelain=v1']).decode()
assert all(line == ' M AGENTS.md' or line.startswith('?? ' + PREFIX + 'independent-') for line in status.splitlines())
receipt['statusBeforeFinalReceipt'] = status
receipt['head'] = PROCESS
receipt['branch'] = run(['git', 'branch', '--show-current']).decode().strip()
receipt['indexEmpty'] = True
receipt['onlyTrackedModificationProtectedAGENTS'] = True
receipt['packetReviewResult'] = proof['packetReviewResult']
receipt['actualDesignatedTaskCount'] = 0
receipt['formattedScope'] = formatted_names
receipt['preservedRawFirstProofNotReformatted'] = 'independent-r1-first-structure.json'
files = []
for candidate in sorted(ROOT.glob('independent-*')):
    if candidate.name == 'independent-r1-final-receipt.json':
        continue
    value = candidate.read_bytes()
    files.append({'path': candidate.relative_to(TREE).as_posix(), 'bytes': len(value), 'sha256': sha(value)})
receipt['filesExcludingSelf'] = files
receipt['finishedUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt['selfBinding'] = 'This receipt excludes itself. Actual final bytes/SHA and final status printed once to the parent; stop writing afterward.'
out = ROOT / 'independent-r1-final-receipt.json'
out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--write', str(out)])
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--check', str(out)])
# Last two formatter receipts are emitted as exact tool output to avoid circular
# self-mutation after the final receipt bytes have been fixed.
final_status = run(['git', 'status', '--porcelain=v1']).decode()
value = out.read_bytes()
print(json.dumps({'result': receipt['packetReviewResult'], 'files': files, 'finalReceipt': {'path': str(out), 'bytes': len(value), 'sha256': sha(value)}, 'finalCommandsExternalOnly': receipt['commands'][-3:], 'head': PROCESS, 'indexEmpty': True, 'finalStatus': final_status, 'noFurtherWrites': True}, ensure_ascii=False))
