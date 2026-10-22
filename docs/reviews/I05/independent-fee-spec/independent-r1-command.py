"""Independent R1 evidence: stdlib, fixed JSON and candidate pure math only.

This command deliberately does not run the author's inventory/seal/validator.
The opaque v1 draft is only passed through byte hashing, never decoded.
"""
from pathlib import Path
import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
R = ROOT / 'docs/reviews/I05/independent-fee-spec'
I = ROOT / 'docs/iterations/I05/independent-fee-spec'
S = R / 'author-v2-inputs'
CANDIDATE = '6bbea55f5134f95f715858f55c142fb8b760ccf1'
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
PY = '/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12'
proof = {'format': 'i05-independent-r1-proof/1', 'candidate': CANDIDATE,
         'base': BASE, 'commands': [], 'checks': {}, 'counterexamples': [],
         'productRuntimeExecuted': False, 'opaqueDraftContentDecoded': False}


def command(argv, text=True):
    p = subprocess.run(argv, cwd=ROOT, capture_output=True,
                       env=os.environ | {'PYTHONDONTWRITEBYTECODE': '1'}, check=False)
    row = {'argv': argv, 'cwd': str(ROOT), 'exit': p.returncode}
    if text:
        row.update(stdout=p.stdout.decode(), stderr=p.stderr.decode())
    else:
        row.update(stdoutBytes=len(p.stdout), stdoutSHA256=hashlib.sha256(p.stdout).hexdigest(),
                   stderr=p.stderr.decode())
    proof['commands'].append(row)
    if p.returncode:
        proof['firstCommandFailure'] = row
        (R / 'r1-proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    assert p.returncode == 0, row
    return p.stdout.decode() if text else p.stdout


def digest(b):
    return hashlib.sha256(b).hexdigest()


def encoded(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def census(v):
    totals = [0, 0, 0]
    def visit(a):
        totals[0] += 1
        if isinstance(a, dict):
            for k, b in a.items():
                totals[1] += 1
                totals[2] += len(k.encode())
                visit(b)
        elif isinstance(a, list):
            for b in a:
                visit(b)
        elif isinstance(a, str):
            totals[2] += len(a.encode())
    visit(v)
    return dict(zip(('valueNodes', 'keyNodes', 'stringUtf8BytesIncludingRepeatedFields'), totals))


assert command(['git', 'rev-parse', 'HEAD']).strip() == CANDIDATE
assert command(['git', 'branch', '--show-current']).strip() == 'docs/I05-independent-fee-spec'
assert not command(['git', 'diff', '--cached', '--name-only']).strip()
proof['checks']['initialStatus'] = command(['git', 'status', '--short'])
changes = command(['git', 'diff', '--name-status', BASE, CANDIDATE]).splitlines()
assert len(changes) == 53 and all(l.startswith('A\tdocs/') for l in changes)
paths = {l.split('\t')[1] for l in changes}
mf = R / 'artifact-manifest.json'
manifest = json.loads(mf.read_text())
assert len(manifest['entries']) == 52
assert {r['path'] for r in manifest['entries']} | {str(mf.relative_to(ROOT))} == paths
assert digest(mf.read_bytes()) == '4aba269a56b297b55d27ec01bb55606e508cb129531cadadddbcdd122f6535b4'
for row in manifest['entries']:
    b = (ROOT / row['path']).read_bytes()
    assert (len(b), digest(b)) == (row['bytes'], row['sha256']), row['path']
    original = command(['git', 'show', CANDIDATE + ':' + row['path']], text=False)
    assert b == original, row['path']
assert command(['git', 'show', CANDIDATE + ':' + str(mf.relative_to(ROOT))], text=False) == mf.read_bytes()
proof['checks']['candidateIdentity'] = {'manifestEntries': 52, 'addedFiles': 53,
                                       'currentEqualsGit': True, 'opaqueDraftPreserved': True}
inputs = json.loads((R / 'input-manifest.json').read_text())
for row in inputs:
    b = (ROOT / row.get('copy', row['path'])).read_bytes()
    assert (len(b), digest(b)) == (row['bytes'], row['sha256']), row['name']
    if 'ref' in row:
        assert b == command(['git', 'show', row['ref'] + ':' + row['path']], text=False)
    elif 'copy' in row:
        assert b == Path(row['path']).read_bytes()
claims = json.loads((R / 'normative-claims.json').read_text())
for claim in claims:
    raw = (ROOT / claim['source']['copy']).read_bytes().splitlines(keepends=True)
    b = b''.join(raw[claim['startLine'] - 1:claim['endLine']])
    assert (len(b), digest(b)) == (claim['excerptBytes'], claim['excerptSha256'])
    for line in claim['lines']:
        b = raw[line['line'] - 1]
        assert (len(b), digest(b), b.decode().rstrip('\n')) == (
            line['bytes'], line['sha256'], line['utf8'])
proof['checks']['sourceIdentity'] = {'manifestInputs': len(inputs), 'gitInputs': sum('ref' in r for r in inputs),
                                    'claims': len(claims), 'allHashesAndTextMatch': True}

# AST before executing the candidate's mathematical module or tests.
allowed_imports = {'__future__', 'dataclasses', 'hashlib', 'pathlib', 'ast', 'copy', 'json',
                   'unittest', 'invoice_model'}
for p in (I / 'invoice_model.py', I / 'test_invoice_model.py'):
    tree = ast.parse(p.read_text(), filename=str(p))
    imports = {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imports |= {n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert imports <= allowed_imports
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in
                   ('eval', 'exec', '__import__') for n in ast.walk(tree))
sys.path.insert(0, str(I))
import invoice_model as model

# Independent allocator formula and literal constants are not imported from the model.
pools = {'work': 16777216, 'input_bytes': 262144, 'output_bytes': 262144,
         'trace_items': 8192, 'firings': 1024, 'head_occurrences': 16384, 'bindings': 1024}
structure = dict(term_bytes=16384, source_bytes=65536, digits=4096, integer_bits=16384,
                 temporary_bits=32768, rules=100, when=16, comparisons=32, heads=16, variables=64)
def independently_allocate(defs, disabled):
    ordered = sorted(range(len(defs)), key=lambda j: defs[j]['rule_id']) if defs else [None]
    n = len(ordered)
    result = []
    for j, original in enumerate(ordered):
        limits = {k: t // n + (1 if t - n * (t // n) > j else 0) for k, t in pools.items()}
        limits.update(structure)
        rid = defs[original]['rule_id'] if original is not None else None
        result.append(dict(rule_id=rid, definition_ordinal=original,
                           disabled=rid in disabled, limits=limits))
    return result

dataset = json.loads((S / 'inputs.json').read_text())
observations = {o['id']: o for o in dataset['observations']}
gaps = json.loads((S / 'gaps.json').read_text())
gap_rows = {o['id']: o for o in gaps['items'] + gaps['additionalProductionRestoreCases']}
oracle = json.loads((S / 'oracle.json').read_text())
oracle_rows = {o['id']: (j, o) for j, o in enumerate(oracle['observations'])}
perid = json.loads((I / 'per-id.json').read_text())['items']
assert len(perid) == len(gap_rows) == 114 and {r['id'] for r in perid} == set(gap_rows)
checked_ids, conditional, math_checked, missing_groups = [], [], [], []
for row in perid:
    rid = row['id']; o = observations[rid]; gap = gap_rows[rid]
    ds = dataset['datasets'][o['datasetId']]; body = ds.get('input', ds)
    defs = body.get('definitions', body.get('rules'))
    assert row['operation'] == o['operation'] and row['datasetId'] == o['datasetId']
    assert row['declaredInputProjectionSha256'] == o['projectionSha256']
    expected_pointer = '/datasets/' + o['datasetId'].replace('~', '~0').replace('/', '~1')
    assert row['datasetPointer'] == gap.get('datasetPointer', expected_pointer)
    measure = row['independentAssetJsonMeasure']
    assert measure['bytes'] == len(encoded(ds)) and measure['sha256'] == digest(encoded(ds))
    assert all(measure[k] == v for k, v in census(ds).items())
    s = row['inputStructure']
    assert s['definitionCount'] == (len(defs) if defs is not None else None)
    for field, key in [('assertedRecords', 'asserted'), ('ontologyRecords', 'ontology'),
                       ('structuredRecords', 'records')]:
        assert s[field] == (len(body[key]) if key in body else None)
    assert s['requestedTargetOccurrences'] == len(o['parameters'].get('rootsTargets', []))
    assert s['disabledRuleIds'] == body.get('disabled_rule_ids', [])
    if defs is None:
        conditional.append(rid)
        assert row['predictedAllocation']['children'] is None
        assert row['conditionalCanonicalApiDefaultAllocation']['values'] == independently_allocate([], [])
    else:
        children = independently_allocate(defs, body.get('disabled_rule_ids', []))
        assert row['predictedAllocation']['children'] == children, rid
        assert row['conditionalCanonicalApiDefaultAllocation'] is None
        n = len(children)
        assert row['predictedAllocation']['revalidationCaps'] == dict(
            work=3 * 16777216 + 203 * n + 33 * 1024 + 4 * 262144,
            input_bytes=524288, output_bytes=524288)
    index, eo = oracle_rows[rid]
    expected = row['existingIndependentBusinessExpected']
    assert expected['pointer'] == '/observations/' + str(index) + '/expected'
    assert expected['expectedValueSha256'] == digest(encoded(eo['expected']))
    assert expected['feeAuthority'] is False
    for f in row['mathFacts']:
        assert f['left'] in (1, 2, 3) and f['right'] == 2
        a, b = f['left'], f['right']
        truth = {'eq': a == b, 'ne': a != b, 'lt': a < b, 'le': a <= b,
                 'gt': a > b, 'ge': a >= b}[f['operator']]
        assert truth is f['result']
        comp = defs[0]['comparisons'][0]
        left_value = [t['triple']['object'] for t in body['asserted']
                      if t['triple']['predicate'] == defs[0]['when'][-1]['predicate']]
        assert len(left_value) == 1
        assert left_value[0] == '"' + str(a) + '"^^<http://www.w3.org/2001/XMLSchema#integer>'
        assert comp['operator'] == f['operator']
        assert comp['right'] == '"2"^^<http://www.w3.org/2001/XMLSchema#integer>'
        math_checked.append(rid)
    assert row['currentInvoice']['exact'] is None and row['proposalInvoice']['amount'] is None
    assert all(v is None for k, v in row['authority'].items()
               if k not in ('status', 'missingReasons'))
    assert row['decision']['admission'] == 'pending'
    assert row['decision']['resourceRejection'] == 'not-automatically-allowed'
    if 'H01' not in row['proposalInvoice']['requiredScheduleGroups']:
        missing_groups.append(rid)
    checked_ids.append(rid)
proof['checks']['perId'] = dict(checkedIds=checked_ids, structureAllocationsExpectedPointersMatch=True,
    predictedFull17L=113, conditionalDefault=conditional, integerTruthIds=math_checked,
    completeCurrentInvoices=0, completeProposalInvoices=0, missingH01Count=len(missing_groups))

# Every hand vector is loaded and evaluated; literal expected values come from JSON.
hv = json.loads((I / 'hand_vectors.json').read_text()); vectors = {v['id']: v for v in hv['vectors']}
proof['checks']['handVectors'] = []
for v in hv['vectors']:
    events = copy.deepcopy(vectors[v.get('sameEvents', v['id'])]['events'])
    events = [copy.deepcopy(hv['finalizer']) if e == 'FINAL' else e for e in events]
    result = model.Ledger(hv['commonCaps'] | v.get('overrides', {})).run(events)
    for k, value in v['expected'].items():
        assert (all(result[k][a] == b for a, b in value.items()) if isinstance(value, dict)
                else result[k] == value), (v['id'], k)
    proof['checks']['handVectors'].append(dict(id=v['id'], result=result))

# Independent hand-picked boundary examples, not derived from author vectors.
caps = hv['commonCaps'] | {'work': 18, 'objects': 20, 'scalar': 20}
f = {'id': 'F', 'kind': 'finalize', 'handles': 1, 'slots': 1,
     'fields': 2, 'bytes': 3, 'domain_bytes': 1}  # 2+1+1+6=10 work
e = [f, {'id': 'large-limb', 'kind': 'mul', 'a': 1 << 64, 'b': 1 << 32},
     {'id': 'same-two-bytes', 'kind': 'scan', 'n': 2}, {'id': 'ok', 'kind': 'finish'}]
ok = model.Ledger(caps).run(e)
assert ok['used']['work'] == 18 and ok['used']['scan_copy'] == 8
fail = model.Ledger(caps | {'work': 17}).run(e)
assert fail['first'] == 'same-two-bytes' and fail['used']['work'] == 16
proof['checks']['independentLargeLimbBoundary'] = dict(exact=ok, oneShort=fail,
    handDerivation='F10 + L(2^64)*L(2^32)=3*2=6 + SCAN2 =18')

# Counterexample: finalization proof is checked after the data retention mutation.
bad_f = f | {'handles': 0, 'slots': 0}  # 8 work, not enough cleanup proof for x
ledger = model.Ledger(caps)
try:
    ledger.run([bad_f, {'id': 'unfunded-data', 'kind': 'hold', 'handle': 'x',
                       'objects': 1, 'scalar': 2}, {'id': 'ok', 'kind': 'finish'}])
except ValueError as error:
    proof['counterexamples'].append(dict(id='finalization-after-mutation', error=str(error),
        state=ledger.state, used=ledger.used, live=ledger.live, peak=ledger.peak,
        held=ledger.held, holdsSeen=ledger.holds_seen, slotsSeen=ledger.slots_seen))
else:
    raise AssertionError('expected insufficient-finalization counterexample')
assert ledger.state == 'running' and 'x' in ledger.held

# Counterexample: current prepayment gate permits releasing the control owner early.
program = [{'id': 'C', 'kind': 'hold', 'handle': 'control', 'objects': 64, 'scalar': 0},
           f, {'id': 'drop-control', 'kind': 'release', 'handle': 'control'},
           {'id': 'data', 'kind': 'hold', 'handle': 'x', 'objects': 1, 'scalar': 2},
           {'id': 'done', 'kind': 'finish'}]
result = model.Ledger(hv['commonCaps'] | {'objects': 67}).run(program)
assert result['state'] == 'completed' and result['peak']['objects'] == 67
proof['counterexamples'].append(dict(id='control-ticket-released-before-data', program=program,
    caps=hv['commonCaps'] | {'objects': 67}, result=result,
    expected='control64 stays live through ordinary events, so data needs objects68 and must reject'))

# No terminal retry; two independent authorized restore invoices sum, do not max.
once = model.Ledger(hv['commonCaps']); vr = vectors['whole-stream-restore-one']
events = [hv['finalizer'] if e == 'FINAL' else e for e in vr['events']]
rr = once.run(events)
try:
    once.run(events)
except ValueError as error:
    proof['checks']['sameLedgerRetryRejected'] = str(error)
else:
    raise AssertionError('retry unexpectedly accepted')
assert rr['used']['work'] == 28

command([PY, '-B', str(I.relative_to(ROOT) / 'test_invoice_model.py')])
# Check only authored, new md/json. Frozen raw copies and historic raw evidence are excluded.
authored = [p for p in paths if p.endswith(('.md', '.json')) and '/author-v2-inputs/' not in p
            and '/author-v1-input-exposure/' not in p and not p.endswith(('local-proof-excerpts.json',
                'retained-first-failures.json'))]
command(['/usr/local/bin/node', '/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration/node_modules/prettier/bin/prettier.cjs',
         '--check'] + sorted(authored))
command(['git', 'diff', '--check'])
assert command(['git', 'rev-parse', 'HEAD']).strip() == CANDIDATE
proof['checks']['endStatus'] = command(['git', 'status', '--short'])
proof['firstCommandFailure'] = next((c for c in proof['commands'] if c['exit']), None)
proof['runner'] = {'argv': [PY, '-B', str(Path(__file__).relative_to(ROOT))], 'cwd': str(ROOT),
                   'sourceSHA256': digest(Path(__file__).read_bytes()),
                   'ownExitEvidence': 'outer exec returncode; not prefilled inside running command'}
(R / 'r1-proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'candidateIdentity': proof['checks']['candidateIdentity'],
                  'sourceIdentity': proof['checks']['sourceIdentity'],
                  'perIdRows': len(checked_ids), 'vectors': len(hv['vectors']),
                  'counterexamples': proof['counterexamples'], 'commands': len(proof['commands'])},
                 ensure_ascii=False, indent=2))
