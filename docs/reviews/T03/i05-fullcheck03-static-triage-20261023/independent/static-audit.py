"""Read-only bytes/Git/AST/XML triage audit; never import candidate or run tests."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
PACKET = Path('/Users/kyle/Documents/工作/知爻/本体/outputs/20261023_i05_fullcheck03_static_triage')
FROZEN = '830cdd1d198bf549b563925a3a47f7f9444710bd'

def identity(path):
    raw = Path(path).read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def check(row):
    actual = identity(row['path'])
    return actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']

proof = json.loads((PACKET/'proof.json').read_bytes())
manifest = json.loads((PACKET/'manifest.json').read_bytes())
result = {'method':'static bytes/hash/Git/AST/XML only; no candidate import or execution',
          'packet': [identity(PACKET/name) for name in ['report.md','proof.json','manifest.json']],
          'packetManifestExact':all(check({**r,'path':str(PACKET/r['path'])}) for r in manifest['members']),
          'supplierHEAD':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
          'supplierStatus':subprocess.check_output(['git','status','--short']).decode(),
          'AGENTS':identity(ROOT/'AGENTS.md'), 'fourProducts':[]}
for relative in ['scripts/build-engine.mjs','packages/engine/entrypoint.py','packages/engine/src/ontolearn_engine/semantic_build_provenance.py','packages/engine/tests/test_semantic_build_provenance.py']:
    raw=(ROOT/relative).read_bytes()
    frozen=subprocess.check_output(['git','show',FROZEN+':'+relative])
    result['fourProducts'].append({**identity(ROOT/relative),'equal830cdd':raw==frozen})
original_records=[proof['receipt'],proof['streams']['stdout'],proof['streams']['stderr'],{k:proof['junit'][k] for k in ['path','bytes','sha256']}]
result['originalRunArtifacts']=[{**row,'identityExact':check(row)} for row in original_records]
xml=ET.fromstring(Path(proof['junit']['path']).read_bytes())
cases=xml.findall('.//testcase')
failures=[(case.attrib,case.find('failure').text) for case in cases if case.find('failure') is not None]
result['junit']={'caseCount':len(cases),'failures':len(failures),'errors':sum(case.find('error') is not None for case in cases),'skips':sum(case.find('skipped') is not None for case in cases),'failureNames':[r[0]['name'] for r in failures],'exactFullFailureTextMatchesProof':all(a==b['testcase'] and text==b['fullFailureText'] for (a,text),b in zip(failures,proof['failureFacts']))}
result['sourceReads']=[{**row,'identityExact':check(row)} for row in proof['sourceReads']]
segments=list(proof['staticImportChain'])+[value for value in proof['fixture'].values() if type(value)is dict and 'text' in value]
result['sourceSegments']=[{'path':row['path'],'start':row['start'],'end':row['end'],'exact':''.join(Path(row['path']).read_text().splitlines(keepends=True)[row['start']-1:row['end']])==row['text']} for row in segments]
reader=(ROOT/'packages/engine/src/ontolearn_engine/semantic_build_provenance.py').read_text()
tests=(ROOT/'packages/engine/tests/test_semantic_build_provenance.py').read_text()
r_ast,t_ast=ast.parse(reader),ast.parse(tests)
fixed=next(ast.literal_eval(item.value) for item in r_ast.body if isinstance(item,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='FIXED_DISTRIBUTIONS' for target in item.targets))
make=next(item for item in t_ast.body if isinstance(item,ast.FunctionDef) and item.name=='make_case')
result['fixtureStatic']={'fixedPrefixes':list(fixed),'prefixCount':len(fixed),'makeCaseLineRange':[make.lineno,make.end_lineno],'makeCaseDeletionCalls':[node.func.attr for node in ast.walk(make) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ['delitem','clear','pop','popitem']],'unknownLoadedBranch':{'line':669,'source':reader.splitlines()[668]},'syntheticRootCount':len(fixed),'actualOffendingName':'UNKNOWN; original failure did not capture loop name/lookup/sys.modules','fileOriginBranchLines':[625,626],'normalizationLine':419}
result['notReverified']=['private controller ticket payload','all48 protected files current byte state/before-after records','source417 or any runtime artifact outside this fullcheck triage']
print(json.dumps(result,ensure_ascii=False,indent=2))
