"""Verify declarative draft files and exact Git supply; never execute target code."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[3]
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'

def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def read(name): return json.loads((P/name).read_text())
def digest(raw): return hashlib.sha256(raw).hexdigest()
checks = {}
sources = read('source-manifest.json')['entries']
for row in sources:
    if 'ref' in row:
        raw=git('show',row['ref']+':'+row['path'])
        assert len(raw)==row['bytes'] and digest(raw)==row['sha256']
        assert git('rev-parse',row['ref']+':'+row['path']).decode().strip()==row['gitBlob']
checks['exactNamedGitSources'] = sum('ref' in row for row in sources)
x=read('input-identities.json')
assert len(x['modules23'])==23 and len({r['module'] for r in x['modules23']})==23
assert len(x['resources4'])==4 and len(x['assets2'])==2 and len(x['writers4'])==4
paths=[r['path'] for r in x['modules23']+x['resources4']+x['assets2']]+[r['path'] for r in x['writers4']]
assert len(set(paths))==33
for r in x['writers4']:
    assert (ROOT/r['path']).read_bytes()==git('show',BASE+':'+r['path'])
checks['exact33InputPathsAndFourWritersUntouched']=True
for r in x['modules23']:
    ast.parse(git('show',r['ref']+':'+r['path']))
checks['staticAstOnlyModules']=23
p=read('profile-descriptor.draft.json')
assert p['executionAuthorization'] is False and p['acceptedCompositionRef'] is None
assert p['canonicalModules']==x['modules23']
assert p['resources']==x['resources4'] and p['assets']==x['assets2']
assert p['selectors']==['full-v1','b1-semantic-1x-v1','b1-semantic-10x-v1']
assert 'ontolearn_engine.quality.rule_revalidation' in p['hiddenImports']
assert 'ontolearn_engine.quality.rule_revalidation' not in p['excludeEngineModules']
checks['draftProfileFiniteClosure']=True
y=read('suite-inventory.json')
assert y['counts']['observations']==417 and y['counts']['datasets']==320
assert len(y['observations'])==417 and sum(y['families'].values())==417
assert len(y['caseSets']['full-v1'])==417
assert all(len(y['caseSets'][key])==1 for key in p['selectors'][1:])
assert [o['id'] for o in y['observations']]==y['caseSets']['full-v1']
checks['fullSuiteInventory417AndB1Singletons']=True
g=read('guard-migration.json')
assert len(g['old43'])==43 and sum(r['matches'] for r in g['old43'])==30
checks['old43History30Same13Different']=True
lock=read('lock-distributions.json')
assert len(lock['allPackages'])==23 and len(lock['runtimeEight'])==8
assert lock['probeCheckoutLockMatchesRequiredSupplier'] is False
checks['twoLockIdentityDomainsAndFull23Packages']=True
for name in ['build-provenance.schema.json','final-build-receipt.schema.json']:
    schema=read(name)
    def walk(v):
        if isinstance(v,dict):
            if v.get('type')=='object':
                assert v.get('additionalProperties') is False
                assert set(v.get('required',[]))==set(v.get('properties',{}))
            if '$ref' in v:
                assert v['$ref'].startswith('#/$defs/')
                assert v['$ref'].split('/')[-1] in schema.get('$defs',{})
            for z in v.values(): walk(z)
        elif isinstance(v,list):
            for z in v: walk(z)
    walk(schema)
checks['schemasStrictObjectKeysAndLocalRefsOnly']=True
schema=read('build-provenance.schema.json')
assert len(schema['properties'])==17
assert schema['properties']['moduleBindings']['minItems']==23
assert schema['properties']['inputs']['properties']['resources']['maxItems']==4
assert schema['properties']['completion']['properties']['selfHashIncluded']['const'] is False
assert schema['properties']['completion']['properties']['runtimeParity']['const']=='not-run-by-builder'
checks['schemaHas23ActualCodeBindingsAndNoSelfHash']=True
main=(ROOT/'docs/iterations/I05/semantic-build-offer-draft.md').read_text()
for r in x['modules23']+x['resources4']+x['assets2']:
    assert r['sha256'] in main
assert 'external-unverified' in main and 'archive-loader-consistent-with-declared-source' in main
assert 'whole-H' in main and '指定同版' in main and '12 B1' in main and '原12 S1' in main
checks['mainPinsAndExternalAuthorityAndOriginalGates']=True
raw=(ROOT/'AGENTS.md').read_bytes()
assert len(raw)==15852 and digest(raw)=='78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759'
assert not git('diff','--cached','--name-only').strip()
checks['protectedAgentsAndEmptyIndexBeforeFreeze']=True
report={'format':'i05-offer-static-validation/1','checks':checks,
        'method':'stdlib Git bytes/AST/JSON/hash only; schema structure not runtime schema validation',
        'notExecuted':['product imports','pytest','builder/spec/reader/helper','fixture simulation',
            'source/frozen probe','business compile/archive decode','install/network','DB/native/GUI',
            'physical measurements','T03 meter ticket'],
        'failuresPreserved':['static-collect-first-failure.raw','static-collect-second-failure.raw',
                            'document-write-first-failure.raw']}
(P/'validation-static.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
