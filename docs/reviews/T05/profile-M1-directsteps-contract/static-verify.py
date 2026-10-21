"""Read-only document/Git/stdlib validation. No product imports or evaluation."""

import hashlib
import json
import subprocess
from pathlib import Path

base = Path(__file__).parent
contract = Path('docs/iterations/T05/profile-M1-directsteps-consumer-contract.md')
text = contract.read_text()
manifest = json.loads((base / 'fixed-inputs.json').read_text())
for row in manifest['files']:
    raw = Path(row['snapshotPath']).read_bytes()
    assert len(raw) == row['bytes']
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    if row['sourceRef'] in manifest['sourceRefs'].values():
        assert raw == subprocess.check_output([
            'git', 'show', row['sourceRef'] + ':' + row['sourcePath']
        ])

inputs = base / 'inputs/t05/docs/reviews/T05/profile-M1-math-explanation-input-contract'
graph = json.loads((inputs / 'supplemental-graph-inputs.json').read_text())
cells = json.loads((inputs / 'consumer-C-inputs.json').read_text())
golden_cells = json.loads((inputs / 'consumer-C-goldens.json').read_text())
assert len(graph['cases']) == 5
assert len(cells['cases']) == len(golden_cells['cases']) == 13
assert [r['id'] for r in cells['cases']] == [r['id'] for r in golden_cells['cases']]
for row in graph['cases'] + cells['cases']:
    assert row['id'] in text, row['id']
    assert 'expected' not in row

window = json.loads((base / 'source-window-request.json').read_text())
assert len(window['paths']) == 10
assert len({r['path'] for r in window['paths']}) == 10
for row in window['paths']:
    assert row['authorizationByThisDocument'] is False
    if row['oldSha256'] is None:
        assert not Path(row['path']).exists()
    else:
        raw = subprocess.check_output(['git', 'show', row['sourceRef'] + ':' + row['path']])
        assert len(raw) == row['oldBytes']
        assert hashlib.sha256(raw).hexdigest() == row['oldSha256']

budget = json.loads((base / 'budget-model.json').read_text())
caps = budget['captureCaps']
M, A, S = 8388608, 250000, 100000
assert caps['fixedTraversalAnalysisSubBoundNotSeparateWallet'] == 128 + 8*A + 32*S + 16*M
assert caps['objects'] == 128 + 4*A + 12*S + 4*(1 + 8*M)
assert caps['scalar'] == 128 + 6*M
assert caps['generalWorkAndScanCopyEach'] == 64*M + 128*(A + S + 1)
assert A == 1000000 // 4
assert len(budget['domains']['cumulative']) == len(budget['domains']['live']) == 2

frozen = Path('docs/reviews/T05/profile-M1-math-observation')
controlled = json.loads((frozen / 'controlled-151.json').read_text())
for row in controlled['files']:
    raw = Path(row['path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
previous = json.loads((frozen / 'process-manifest.json').read_text())
for row in previous['files']:
    raw = Path(row['path']).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
assert (frozen / 'process-manifest.json').read_bytes() == subprocess.check_output([
    'git', 'show', 'e0ee604ae5e63b4dfdda5db984c0eec8b59a65f5:' + str(frozen / 'process-manifest.json')
])
assert Path('AGENTS.md').read_bytes() == subprocess.check_output([
    'git', 'show', '5f910b52c69d86a1076b2032e5d3c63e715947f3:AGENTS.md'
])
changed = subprocess.check_output(['git', 'diff', '--name-only', 'e0ee604ae5e63b4dfdda5db984c0eec8b59a65f5']).decode().splitlines()
assert all(p == str(contract) or p.startswith(str(base) + '/') for p in changed)
assert text.count('```') % 2 == 0
assert not any(line.endswith(' ') or line.endswith('\t') for line in text.splitlines())
assert text.endswith('\n')
print(json.dumps({
    'status': 'pass', 'kind': 'static Git/stdlib only',
    'fixedInputFiles': len(manifest['files']), 'pureGraphCases': 5,
    'consumerCells': 13, 'proposedExistingPaths': 6, 'proposedNewPaths': 4,
    'controlled151Unchanged': True, 'previous166ProcessFilesUnchanged': True,
    'baseAGENTSUnchanged': True, 'budget': 'bounded integer identities only',
    'noProductLibraryTestsGuiNetworkExecution': True,
    'notPrettierOrRuntimeVerification': True,
    'contractBytes': contract.stat().st_size,
    'contractSha256': hashlib.sha256(contract.read_bytes()).hexdigest(),
}, ensure_ascii=False, indent=2))
