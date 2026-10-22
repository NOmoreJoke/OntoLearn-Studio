"""Finalize only new R2 independent documents; no copy or fixed input mutation."""
import base64
import datetime
import hashlib
import json
import os
import pathlib
import subprocess

TREE = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package')
ROOT = TREE / 'docs/reviews/I05/retained-source-review-package'
PREFIX = 'docs/reviews/I05/retained-source-review-package/'
PROCESS = 'dbf5b6a741d15e5c62b2992ec0a077c28adb2856'
NODE = '/usr/local/bin/node'
PRETTIER = '/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs'
receipt = {'scope': 'Only new independent R2 docs/JSON; fixed packet/wrappers untouched.', 'commands': []}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def run(argv):
    env = dict(os.environ); env['NODE_DISABLE_COMPILE_CACHE'] = '1'
    cp = subprocess.run(argv, cwd=TREE, capture_output=True, env=env)
    receipt['commands'].append({'argv': argv, 'cwd': str(TREE), 'exitCode': cp.returncode, 'stdoutBase64': base64.b64encode(cp.stdout).decode(), 'stderrBase64': base64.b64encode(cp.stderr).decode(), 'stdoutBytes': len(cp.stdout), 'stderrBytes': len(cp.stderr)})
    assert cp.returncode == 0
    return cp.stdout

path = ROOT / 'independent-proof-r2.json'
proof = json.loads(path.read_bytes())
assert proof['result'].startswith('PASS') and proof['findings'] == []
assert proof['checks']['historicalLogs']['sequentialContinuationZeroRecordsPresent']
spec = json.loads((ROOT / 'physical-copy-spec-r2.json').read_bytes())
forbidden = {'zcode-glm53-input.md', 'minimax-m31flash-input.md', 'readme-r2.md', 'dispatch-r2.json', 'isolation-plan-r2.md', 'physical-copy-spec-r2.json'}
assert not forbidden & {r['source'] for r in spec['common']}
proof['checks']['commonInputExclusions'] = {'forbiddenCurrentOrR1PeerEntrySources': sorted(forbidden), 'intersection': [], 'actualWholePathsetsAlreadyVerified': True}
proof['checks']['outerContainerBoundary'] = {'bothRootModes': '0755', 'internalDirectoryCountExcludesOuterRoot': True, 'readonlyInputDirectoriesOnly': ['instructions', 'immutable', 'data'], 'onlyAuthorizedMutable': ['reports', 'scratch', 'review-status'], 'noActualApplicationGrowthTest': True}
proof['readOnlyDiscoveryFailure'] = {'toolChunk': 'b90c17', 'actualExitCode': 1, 'error': "AttributeError: 'list' object has no attribute 'get'", 'operation': 'Pinned Python stdlib JSON read-only schema summary expected dict for freeze-command-log-r2.json but raw original is list.', 'originalOutputReference': 'Full actual combined tool result in conversation chunk b90c17. No retrospective stdout/stderr split or product failure is claimed.', 'writes': False, 'resolution': 'New wrapper checker handles both list and dict and preserves all original records.'}
proof['checkerRuns'] = {'first': {'script': 'independent-r2-check.py', 'actualExitCode': 1, 'toolChunk': 'ad1211', 'rawProof': 'independent-r2-first-check-failure.json'}, 'continuation': {'script': 'independent-r2-wrapper-check.py', 'actualExitCode': 0, 'toolChunk': '0cee3e'}, 'outerToolBoundary': 'Actual combined tool outputs are retained in conversation; embedded subprocess stdout/stderr captured separately in proof.commands.'}
proof['completedUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
newdocs = ['independent-review-r2.md', 'independent-proof-r2.json']
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--write', *[str(ROOT / n) for n in newdocs]])
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--check', *[str(ROOT / n) for n in newdocs]])
assert run(['git', 'rev-parse', 'HEAD']).decode().strip() == PROCESS
assert run(['git', 'diff', '--cached', '--name-only', '-z']) == b''
assert run(['git', 'diff', '--name-only', '-z']).decode().split('\0') == ['AGENTS.md', '']
status = run(['git', 'status', '--porcelain=v1']).decode()
expected_new = {'independent-review-r2.md', 'independent-proof-r2.json', 'independent-r2-check.py', 'independent-r2-wrapper-check.py', 'independent-r2-first-check-failure.json', 'independent-r2-finalize.py'}
actual_new = {line.removeprefix('?? ' + PREFIX) for line in status.splitlines() if line.startswith('?? ')}
assert actual_new == expected_new
assert all(line == ' M AGENTS.md' or line.startswith('?? ' + PREFIX) for line in status.splitlines())
receipt['head'] = PROCESS
receipt['branch'] = run(['git', 'branch', '--show-current']).decode().strip()
receipt['indexEmpty'] = True
receipt['statusBeforeReceipt'] = status
receipt['result'] = proof['result']
receipt['actualModelTasks'] = 0
receipt['formattedOnlyNewDocs'] = newdocs
receipt['oldRawFirstFailureNotReformatted'] = 'independent-r2-first-check-failure.json'
receipt['filesExcludingSelf'] = [{'path': PREFIX + name, 'bytes': (ROOT / name).stat().st_size, 'sha256': sha((ROOT / name).read_bytes())} for name in sorted(expected_new)]
receipt['finishedUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt['selfBinding'] = 'Excluded from own files list; final bytes/SHA and exact final commands emitted to parent once. Stop writing afterward.'
out = ROOT / 'independent-r2-final-receipt.json'
out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--write', str(out)])
run([NODE, PRETTIER, '--ignore-path', '/dev/null', '--check', str(out)])
final_status = run(['git', 'status', '--porcelain=v1']).decode()
print(json.dumps({'result': receipt['result'], 'filesExcludingSelf': receipt['filesExcludingSelf'], 'finalReceipt': {'path': str(out), 'bytes': out.stat().st_size, 'sha256': sha(out.read_bytes())}, 'head': PROCESS, 'indexEmpty': True, 'finalStatus': final_status, 'finalCommandsExternalOnly': receipt['commands'][-3:], 'noFurtherWrites': True}, ensure_ascii=False))
