"""Independent preparation audit: metadata, ordinary packet text/raw and hashes only."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path.cwd()
PACKET = Path('docs/reviews/T03/mapping-p2-dual-review-preparation-20261023')
PROCESS = '70f4323fd574d7955fcbf7e581b2d06dd1f10e1c'
HEAD = 'c1e44f81723f9c616f669f56481d1b1ada7e57f2'
PRODUCT = 'da1795b20c3c0d47ae975fe3371e802092a4b429'
OLD = '3c396070c74fbf09cf319b0230c6f96ed2858482'

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd)

def frozen(path, ref=PROCESS):
    return git('show', ref + ':' + str(path))

def obj(name):
    return json.loads(frozen(PACKET / name))

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def identity(path):
    raw = Path(path).read_bytes()
    return {'bytes': len(raw), 'sha256': digest(raw)}

def metadata(ref):
    rows = {}
    for entry in git('ls-tree', '-rlz', ref).split(b'\0'):
        if not entry:
            continue
        fields, path = entry.split(b'\t', 1)
        mode, kind, oid, size = fields.decode().split()
        rows[path.decode()] = {'path': path.decode(), 'mode': mode, 'type': kind,
                               'gitBlobOID': oid, 'bytes': int(size)}
    return rows

def match(row, raw):
    return row['bytes'] == len(raw) and row['sha256'] == digest(raw)

result = {'process': PROCESS, 'reviewHead': HEAD, 'scope': 'preparation only; no product execution'}
old, product, current = metadata(OLD), metadata(PRODUCT), metadata(HEAD)
legacy = obj('legacy-fixed-package/mapping-S1-fixed-inputs.json')
original = legacy['completeTrackedTree']
engineering = [row for row in original if row['kind'] == 'engineering']
result['metadata'] = {
    'oldCount': len(original),
    'oldMatchesOriginalProcess': all({k: row[k] for k in old[row['path']]} == old[row['path']] for row in original),
    'engineeringCount': len(engineering),
    'engineeringDocsTools': sum(row['path'].startswith('docs/') for row in engineering),
    'allOldPresent': set(row['path'] for row in original) <= set(current),
    'engineeringProductEqualsReview': all(product[row['path']] == current[row['path']] for row in engineering),
    'allNonDocsProductEqualsReview': {k:v for k,v in product.items() if not k.startswith('docs/')} == {k:v for k,v in current.items() if not k.startswith('docs/')},
}
indexed = obj('dispatch/full-candidate-tree.json')['completeTrackedTree']
result['metadata']['headIndexCount'] = len(indexed)
result['metadata']['headIndexExact'] = {row['path']: {k:row[k] for k in current[row['path']]} for row in indexed} == current
provenance = obj('input-copy-provenance.json')
missing = provenance['missingHistoricalDocsRestored']
result['restoration'] = {'count': len(missing), 'allExactOriginalBlob': all(current[row['path']] == old[row['path']] for row in missing)}
result['copiedInputs'] = {'count': len(provenance['copiedInputs']), 'identityMismatches': [], 'gitSourceMismatches': []}
for row in provenance['copiedInputs']:
    raw = frozen(row['path'])
    if not match(row, raw):
        result['copiedInputs']['identityMismatches'].append(row['path'])
    if 'sourceGit' in row:
        ref, path = row['sourceGit'].split(':', 1)
        if raw != frozen(path, ref):
            result['copiedInputs']['gitSourceMismatches'].append(row['path'])
relocations = obj('raw-relocations.json')['files']
result['rawRelocations'] = {'count': len(relocations), 'mismatches': []}
for row in relocations:
    if not match(row, frozen(row['path'])) or not match(row, Path(row['originalPath']).read_bytes()):
        result['rawRelocations']['mismatches'].append(row['path'])
for label, name in [('historyManifest', 'history-agent/manifest.json')]:
    manifest = obj(name)
    rows = manifest.get('files', [])
    result[label] = {'count': len(rows), 'mismatches': []}
    for row in rows:
        path = Path(row['path'])
        if not str(path).startswith('docs/'):
            path = PACKET / 'history-agent' / path
        if not match(row, frozen(path)):
            result[label]['mismatches'].append(str(path))
history = obj('history-agent/historical-findings-index.json')
ids = [row['id'] for row in history['rows']]
result['history'] = {'ids': ids, 'exact18': set(ids) == {f'Z{i}' for i in range(1,8)} | {f'F{i:02d}' for i in range(1,12)}, 'originalReportsExact': all(match(row, frozen(row['path'])) for row in history['sourceIdentities'])}
req = list(csv.DictReader(io.StringIO(frozen(PACKET / 'control-snapshots/requirements.csv').decode('utf-8-sig'))))
accept = list(csv.DictReader(io.StringIO(frozen(PACKET / 'control-snapshots/acceptance-baselines.csv').decode('utf-8-sig'))))
prd = frozen('docs/prd/PRD-本体学习与落地Agent工作台.md', HEAD)
m0 = frozen('docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md', HEAD)
result['requirements'] = {'count': len(req), 'P0Prefix': sum(row['原始优先级'].startswith('P0') for row in req), 'P0Exact': sum(row['原始优先级']=='P0' for row in req), 'acceptanceRows':len(accept), 'PRD':{'bytes':len(prd),'lines':len(prd.splitlines()),'sha256':digest(prd)}, 'M0':{'bytes':len(m0),'lines':len(m0.splitlines()),'sha256':digest(m0)}}
index = obj('dispatch/dispatch-index.json')
result['dispatch'] = []
inodes = {}
for role in index['roots']:
    tree = Path(role['tree'])
    prompt = frozen(role['prompt'])
    suffix_ref, suffix_path = role['legacySourceGit'].split(':', 1)
    suffix = prompt[role['legacyOffset']:role['legacyOffset']+role['legacyBytes']]
    policies = []
    for item in role['appendedPolicyOriginals']:
        block = prompt[item['offset']:item['offset']+item['bytes']]
        policies.append(match(item, block) and block == frozen(PACKET / 'control-snapshots' / item['name']))
    setup = obj('owner/setup/' + role['role'] + '/metadata/setup-receipt.json')
    streams_ok = all(match(command[stream], Path(command[stream]['path']).read_bytes()) for command in setup['commands'] for stream in ['stdout','stderr'])
    actual = json.loads((tree/'build/review-session/metadata/task-actual.json').read_bytes())
    inode_set = set()
    for name in ['node_modules', '.venv']:
        for directory, dirs, files in os.walk(tree/name, followlinks=False):
            dirs[:] = [d for d in dirs if not (Path(directory)/d).is_symlink()]
            for name2 in files:
                entry = (Path(directory)/name2).lstat()
                if stat.S_ISREG(entry.st_mode):
                    inode_set.add((entry.st_dev, entry.st_ino))
    inodes[role['role']] = inode_set
    result['dispatch'].append({'role':role['role'], 'head':git('rev-parse','HEAD',cwd=tree).decode().strip(), 'detached': subprocess.run(['git','symbolic-ref','-q','HEAD'],cwd=tree,capture_output=True).returncode == 1, 'status':git('status','--short',cwd=tree).decode(), 'AGENTS':identity(tree/'AGENTS.md'), 'promptExact':match({'bytes':role['promptBytes'],'sha256':role['promptSha256']},prompt), 'ownPromptCopyExact':(tree/'build/review-session/metadata/dispatch-prompt.md').read_bytes()==prompt, 'policiesExact':all(policies), 'legacySuffixExact':suffix==frozen(suffix_path,suffix_ref), 'actualNull':all(actual[k] is None for k in ['actualTask','actualSettings','sessionId','turnId','lease','terminalOutcome']), 'metadataIndexExists':(tree/PACKET/'dispatch/full-candidate-tree.json').exists(), 'setupExits':[r['exitCode'] for r in setup['commands']], 'setupStreamsExact':streams_ok, 'setupStartHead':setup['setupStartingHead'], 'mutableRegularInodes':len(inode_set), 'nodeModulesSymlink':(tree/'node_modules').is_symlink(), 'venvSymlink':(tree/'.venv').is_symlink(), 'baseInterpreter':str((tree/'.venv/bin/python').resolve())})
result['sharedMutableRegularFileInodes'] = len(inodes['zcode'] & inodes['minimax'])
receipt = json.loads(frozen('docs/reviews/T03/mapping-p2-boundaries-20261023/actual-receipt.json', HEAD))
expected = json.loads(frozen('docs/reviews/T03/mapping-p2-boundaries-20261023/fixed-probe-v2-expected.json', HEAD))
result['P2Evidence'] = {'caseCount':receipt['caseCount'],'records':len(receipt['allCaseRecords']),'newCases':len(receipt['newBoundaryCases']), 'expectedCaseCount':len(expected['cases']), 'inventoryCount':len(json.loads(frozen('docs/reviews/T03/mapping-p2-boundaries-20261023/actual-engine-inventory.json',HEAD))), 'codeBindings':len(receipt['codeBindings']), 'newBoundaryIds':list(expected['boundaryEvidence']), 'noActualRuntimeRunByAudit':True}
print(json.dumps(result,ensure_ascii=False,indent=2))
