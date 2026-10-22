"""Independent fixed-text audit. Does not import or call reviewed product code."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
CANDIDATE = '4064b216635f9b7a472879b31b07033edf14d185'
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
SUPPLIER = '6891a5842302859a531cf82767c5a482417bc274'
DOCS = 'ee2b30a2dad35b2d395f9c735aff80371ab41110'
PREFIX = 'docs/reviews/T01/i05-semantic-resource-offer/'
EXPECTED = {
 'packages/contracts/python/contract_v2.py': (34608, '17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7'),
 'packages/contracts/v2/schema.json': (207256, 'e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf'),
 'packages/contracts/v2/registry.json': (15962, '1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b'),
 'packages/contracts/v2/errors.json': (16299, 'ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c'),
}


def command(*args):
 return subprocess.check_output(['git', *args], cwd=ROOT)


def fixed(ref, path):
 return command('show', ref + ':' + path)


def sha(raw):
 return hashlib.sha256(raw).hexdigest()


def parse(raw):
 def pairs(items):
  result = {}
  for key, value in items:
   assert key not in result, key
   result[key] = value
  return result
 return json.loads(raw, object_pairs_hook=pairs)


assert command('rev-parse', 'HEAD').decode().strip() == CANDIDATE
names = command('diff', '--name-only', BASE, CANDIDATE).decode().splitlines()
assert len(names) == 26
assert all(n.startswith(PREFIX) or n == 'docs/iterations/T01/i05-semantic-resource-offer.md' for n in names)
assert command('diff', '--cached', '--name-only') == b''
for name in names:
 assert fixed(CANDIDATE, name) == (ROOT / name).read_bytes(), name
manifest = parse(fixed(CANDIDATE, PREFIX + 'candidate-manifest.json'))
assert {x['path'] for x in manifest['files']} == set(names) - {PREFIX + 'candidate-manifest.json'}
for item in manifest['files']:
 raw = fixed(CANDIDATE, item['path'])
 assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], item['path']
raw_input = parse(fixed(CANDIDATE, PREFIX + 'inputs/manifest.json'))
for item in raw_input['files']:
 raw = fixed(CANDIDATE, item['saved'])
 assert len(raw) == item['bytes'] and sha(raw) == item['sha256']
 if 'sourceRef' in item:
  assert raw == fixed(item['sourceRef'], item['sourcePath'])
 else:
  assert raw == Path(item['source']).read_bytes()
for path, expected in EXPECTED.items():
 raw = fixed(SUPPLIER, path)
 assert (len(raw), sha(raw)) == expected
# Parse all JSON data without invoking the shared validator.
a = parse(fixed(BASE, 'packages/contracts/v2/schema.json'))
b = parse(fixed(SUPPLIER, 'packages/contracts/v2/schema.json'))
assert all(b['$defs'].get(k) == v for k, v in a['$defs'].items())
assert len(a['$defs']) == 66 and len(b['$defs']) == 94
old_registry = parse(fixed(BASE, 'packages/contracts/v2/registry.json'))
registry = parse(fixed(SUPPLIER, 'packages/contracts/v2/registry.json'))
assert len(old_registry['capabilities']) == 24 and len(registry['capabilities']) == 27
assert all(registry['capabilities'].get(k) == v for k, v in old_registry['capabilities'].items())
assert registry['v2Runtime'] == old_registry['v2Runtime']
old_errors = parse(fixed(BASE, 'packages/contracts/v2/errors.json'))
errors = parse(fixed(SUPPLIER, 'packages/contracts/v2/errors.json'))
assert all(errors.get(k) == v for k, v in old_errors.items())
branches = b['$defs']['error']['oneOf']
assert len(branches) == len(errors['codes']) == 26
for branch in branches:
 fields = branch['properties']; spec = errors['codes'][fields['code']['const']]
 assert fields['messageKey']['const'] == spec['messageKey']
 assert fields['retryable']['const'] is spec['retryable']
 assert fields['params'] == spec['paramsSchema']
 assert branch['additionalProperties'] is False
 assert set(branch['required']) == {'code', 'messageKey', 'retryable', 'params'}
# Independent local $ref walk, without using the author's schema traversal.
refs = []
stack = [b['$defs']]
while stack:
 value = stack.pop()
 if isinstance(value, dict):
  if '$ref' in value:
   ref = value['$ref']; assert ref.startswith('#/$defs/') and ref[8:] in b['$defs']; refs.append(ref)
  stack.extend(value.values())
 elif isinstance(value, list): stack.extend(value)
assert len(refs) == 607
# Independent literal edge reconstruction from fixed module texts.
closure_path = 'docs/reviews/I05/source-package-parity-contract/static-import-closure.json'
closure = parse(fixed(DOCS, closure_path))
mods = {m['module']: m for m in closure['modules']}
assert len(mods) == 22
edges = set(); calls = []; trees = {}
for name, info in mods.items():
 raw = fixed(SUPPLIER, info['path']); assert (len(raw), sha(raw)) == (info['bytes'], info['sha256'])
 tree = ast.parse(raw); trees[name] = tree
 package = name if info['path'].endswith('__init__.py') else name.rpartition('.')[0]
 for node in ast.walk(tree):
  if isinstance(node, ast.Import):
   edges.update((name, a.name, node.lineno) for a in node.names if a.name in mods)
  elif isinstance(node, ast.ImportFrom):
   if node.level:
    parts = package.split('.'); prefix = '.'.join(parts[:len(parts)-node.level+1])
    target = prefix + ('.' + node.module if node.module else '')
   else: target = node.module
   if node.module and target in mods: edges.add((name, target, node.lineno))
   for alias in node.names:
    if target + '.' + alias.name in mods: edges.add((name, target + '.' + alias.name, node.lineno))
  elif isinstance(node, ast.Call):
   expr = ast.unparse(node)
   if any(s in expr for s in ['CONTRACT.', 'semantic_identity(', 'resource_manifest(', 'derive_dependencies(', 'permits_transition(', 'build_request(', 'execute_request(']):
    calls.append([name, node.lineno, expr])
assert edges == {tuple(x) for x in closure['edges']} and len(edges) == 128
checker = ast.parse(fixed(SUPPLIER, 'packages/contracts/python/contract_v2.py'))
old_checker = ast.parse(fixed(BASE, 'packages/contracts/python/contract_v2.py'))
func = {n.name:n for n in checker.body if isinstance(n, ast.FunctionDef)}
old_func = {n.name:n for n in old_checker.body if isinstance(n, ast.FunctionDef)}
changed = [name for name in old_func if ast.dump(old_func[name], include_attributes=False) != ast.dump(func[name], include_attributes=False)]
assert changed == ['validate']
# Inventory the reviewed allow-closure. Calls below are lexical, not execution proof.
allow = ['validate','check','equal','semantic','encoded_size','_changeset_semantics']
checker_calls = {name:sorted(set(ast.unparse(n.func) for n in ast.walk(func[name]) if isinstance(n,ast.Call))) for name in allow}
assert not any(any(s in call for s in ['read_text','read_bytes','derive_dependencies','permits_transition','open','exec']) for v in checker_calls.values() for call in v)
assert isinstance(func['_changeset_semantics'].body[-1],ast.Return)
assert isinstance(func['_changeset_semantics'].body[-1].value,ast.Constant) and func['_changeset_semantics'].body[-1].value.value is True
agents = (ROOT / 'AGENTS.md').read_bytes()
assert len(agents) == 15852 and sha(agents) == '78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759'
for name in names:
 raw=fixed(CANDIDATE,name);raw.decode('utf-8')
 if not name.endswith('.raw'):
  assert raw.endswith(b'\n') and b'\r' not in raw
  assert not any(line.endswith((b' ',b'\t')) for line in raw.splitlines())
  if name.endswith('.json'): parse(raw)
subprocess.run(['git','diff','--check',BASE,CANDIDATE],cwd=ROOT,check=True)
result = {'candidate':CANDIDATE,'base':BASE,'supplier':SUPPLIER,'candidateFiles':len(names),'candidateBytesUnchanged':True,'manifest25Verified':True,'inputs17Verified':True,'schemaDefs':[66,94],'oldSchemaDefsChanged':[],'registryCapabilities':[24,27],'ordinaryErrors':26,'localReferences':len(refs),'staticModules':len(mods),'literalEdges':len(edges),'resourceNamedCallSites':calls,'checkerAllowedClosureCalls':checker_calls,'changedExistingCheckerFunctions':changed,'formatBoundary':'stdlib UTF8/JSON/LF/whitespace and git diff --check exit0; not Prettier','noProductExecution':True}
p=OUT/'independent-check.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'candidateFiles':len(names),'modules':len(mods),'edges':len(edges),'refs':len(refs)},ensure_ascii=False))
