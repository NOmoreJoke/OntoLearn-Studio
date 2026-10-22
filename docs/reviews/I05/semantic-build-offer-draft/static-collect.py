"""Static Git/stdlib material collection only; never imports target modules."""
import ast
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
SUPPLIER = '6891a5842302859a531cf82767c5a482417bc274'
PROBE = '2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64'
CONTRACT = 'ee2b30a2dad35b2d395f9c735aff80371ab41110'
OFFER = '4fa5d62eb13269351384527b1f84761c08811e79'
SOURCES = []

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def blob(ref, path):
    raw = git('show', f'{ref}:{path}')
    row = {'ref': ref, 'path': path, 'bytes': len(raw),
           'sha256': hashlib.sha256(raw).hexdigest(),
           'gitBlob': git('rev-parse', f'{ref}:{path}').decode().strip()}
    if row not in SOURCES:
        SOURCES.append(row)
    return raw, row

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

prefix = 'docs/reviews/I05/source-package-parity-contract/'
attachments = ['case-catalog.json', 'inputs-and-coverage-investigation.md',
               'static-import-closure.json', 'guard-delta-audit.json',
               'packaging-resource-investigation.md', 'source-provenance.json',
               'requirements-mapping.md', 'independent-review.md',
               'independent-delta-review.md', 'dispositions.md']
for path in ['docs/iterations/I05/source-package-parity/contract.md',
             *[prefix + item for item in attachments]]:
    raw, _ = blob(CONTRACT, path)
    (OUT / 'inputs' / (Path(path).name + '.raw')).write_bytes(raw)
raw, _ = blob(OFFER, 'docs/iterations/T03/I05-profile-build-dependency-offer.md')
(OUT / 'inputs/T03-fixed-offer.md.raw').write_bytes(raw)
for path in ['packages/engine/src/ontolearn_engine/semantic_source_package_probe.py',
             'packages/engine/tests/test_semantic_source_package_probe.py',
             'docs/reviews/I05/source-package-probe-source/r1-resolution.md']:
    raw, _ = blob(PROBE, path)
    (OUT / 'inputs' / (Path(path).name + '.raw')).write_bytes(raw)
closure = json.loads(blob(CONTRACT, prefix + 'static-import-closure.json')[0])
modules = []
for module in closure['modules']:
    raw, row = blob(SUPPLIER, module['path'])
    assert row['bytes'] == module['bytes'] and row['sha256'] == module['sha256']
    current, current_row = blob(PROBE, module['path'])
    assert current == raw
    ast.parse(raw)
    modules.append({'module': module['module'], **row, 'owner': 'original I05/T05 owner; immutable supply only',
                    'inProbeRefSameBytes': current_row})
raw, row = blob(PROBE, 'packages/engine/src/ontolearn_engine/semantic_source_package_probe.py')
probe_ast = ast.parse(raw)
modules.append({'module': 'ontolearn_engine.semantic_source_package_probe', **row,
                'owner': 'I05; source-only R2 not root accepted'})
resource_paths = ['packages/contracts/python/contract_v2.py',
                  'packages/contracts/v2/schema.json', 'packages/contracts/v2/registry.json',
                  'packages/contracts/v2/errors.json']
resources = []
for path in resource_paths:
    raw, row = blob(SUPPLIER, path)
    assert blob(PROBE, path)[0] == raw
    resources.append({**row, 'owner': 'T01',
        'adoptionCandidate': 'dd972b79adf4d378636a7d41a6b0e3e08c0d5ca1',
        'adoptionProcess': '79d63cc1f403ee857a3af2a98f8870db9a6a910d',
        'bundlePath': path.removeprefix('packages/')})
writers = []
for path in ['packages/engine/pyproject.toml', 'uv.lock', 'scripts/build-engine.mjs',
             'packages/engine/entrypoint.py']:
    rows = [blob(ref, path)[1] for ref in [BASE, SUPPLIER, OFFER, PROBE]]
    writers.append({'path': path, 'owner': 'T03 exclusive; no adoption by this offer', 'snapshots': rows})
assets = []
asset_prefix = 'packages/engine/src/ontolearn_engine/probe_inputs/'
for name in ['i05-source-package-parity-inputs.json', 'i05-source-package-parity-manifest.json']:
    raw, row = blob(PROBE, asset_prefix + name)
    assets.append({**row, 'owner': 'I05', 'bundlePath': 'provenance/i05/source-package-parity/' + name})
inputs = json.loads(blob(PROBE, asset_prefix + 'i05-source-package-parity-inputs.json')[0])
descriptor = json.loads(blob(PROBE, asset_prefix + 'i05-source-package-parity-manifest.json')[0])
observations = inputs['observations']
save('suite-inventory.json', {'format': 'i05-offer-static-suite-inventory/1',
    'sourceRef': PROBE, 'notRuntimeAsset': True,
    'counts': descriptor['counts'], 'caseSets': descriptor['caseSets'],
    'operations': dict(collections.Counter(x['operation'] for x in observations)),
    'families': dict(collections.Counter(x['family'] for x in observations)),
    'contexts': {k: len(v) if isinstance(v, list) else v for k,v in inputs['contexts'].items()},
    'observations': observations})
old = json.loads(blob(CONTRACT, prefix + 'guard-delta-audit.json')[0])
builder_raw = blob(SUPPLIER, 'scripts/build-engine.mjs')[0].decode()
literal = builder_raw.split('const fixedInputs = ',1)[1].split('\nconst distributions',1)[0].strip()
old_literal = ast.literal_eval(literal)
assert len(old_literal) == 43
assert {row['path'] for row in old['entries']} == {row[0] for row in old_literal}
for path, count, digest in old_literal:
    entry = next(item for item in old['entries'] if item['path'] == path)
    assert entry['oldGuard'] == {'bytes':count,'sha256':digest}
    _, actual = blob(SUPPLIER,path)
    assert actual['bytes'] == entry['supplier']['bytes']
    assert actual['sha256'] == entry['supplier']['sha256']
assert sum(entry['matches'] for entry in old['entries']) == 30
allowed = {x['path'] for x in modules + resources + assets}
old_delta = []
for row in old['entries']:
    path = row['path']
    disposition = ('retain exact approved supplied bytes' if path in allowed else
        'T03 must approve final dependency bytes; not accepted here' if path in {'uv.lock','packages/engine/pyproject.toml'} else
        'omit from dedicated profile only; historical/parent guard unchanged')
    old_delta.append({**row, 'newDedicatedDisposition': disposition})
save('guard-migration.json', {'format': 'i05-offer-guard-migration/1', 'historicalTotal': old['total'],
    'historicalMatches': old['matches'], 'historicalMismatches': old['mismatches'],
    'old43': old_delta, 'dedicatedModules23': modules, 'resources4': resources,
    'assets2': assets, 'writers4': writers,
    'requiredAdditionalGuards': ['approved final T03 four writer bytes',
        'approved composition descriptor bytes', 'future I05 consumer delta source bytes',
        'approved build tools metadata + installed dist/RECORD/metadata/license rows',
        'runtime/platform components and postbuild archive witness/receipt']})
lock_raw, lock_id = blob(SUPPLIER, 'uv.lock')
lock = tomllib.loads(lock_raw.decode())
project_raw, project_id = blob(SUPPLIER, 'packages/engine/pyproject.toml')
project = tomllib.loads(project_raw.decode())
probe_lock_raw, probe_lock_id = blob(PROBE, 'uv.lock')
probe_project_raw, probe_project_id = blob(PROBE, 'packages/engine/pyproject.toml')
runtime_names = ['rdflib','pyshacl','pyparsing','owlrl','prettytable','wcwidth','html5rdf','packaging']
packages = lock['package']
assert len(packages) == 23
selected = [p for p in packages if p['name'] in runtime_names]
assert len(selected) == 8
save('lock-distributions.json', {'format': 'i05-offer-static-lock/1', 'notInstalledEvidence': True,
    'lock': lock_id, 'pyprojectIdentity': project_id, 'pyproject': project,
    'probeCheckoutLock': probe_lock_id, 'probeCheckoutPyproject': probe_project_id,
    'probeCheckoutLockMatchesRequiredSupplier': probe_lock_raw == lock_raw,
    'lockTopLevel': {k:v for k,v in lock.items() if k != 'package'},
    'allPackages': packages, 'runtimeEight': selected,
    'licenseConclusions': 'unknown: installed files and final bundle have not been collected'})
save('input-identities.json', {'format':'i05-offer-fixed-input-identities/1',
    'base':BASE,'supplier':SUPPLIER,'probeCandidate':PROBE,'contract':CONTRACT,
    'oldOffer':OFFER,'modules23':modules,'resources4':resources,'assets2':assets,'writers4':writers})
for name in ['I05-semantic-build-offer-draft-window.md',
             'I05-source-package-contract-limited-root-closure.md',
             'T01-i05-resource-offer-root-closure-and-adoption.md',
             'I05-source-package-source-only-root-closure.md']:
    path = Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release') / name
    raw = path.read_bytes()
    (OUT / 'inputs' / (name+'.raw')).write_bytes(raw)
    SOURCES.append({'localNamedSource':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
raw=(ROOT/'AGENTS.md').read_bytes()
assert len(raw)==15852 and hashlib.sha256(raw).hexdigest()=='78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759'
SOURCES.append({'localNamedSource':'protected working AGENTS.md','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
save('source-manifest.json', {'format':'i05-offer-static-sources/1','method':'git show; stdlib AST/JSON/TOML/hash; no product import', 'entries':SOURCES})
print(json.dumps({'moduleCount':len(modules),'resources':len(resources),'assets':len(assets),
                  'observations':len(observations),'datasets':len(inputs['datasets']),
                  'lockPackages':len(packages),'sources':len(SOURCES)},ensure_ascii=False))
