import ast,hashlib,json,pathlib,re,subprocess
root=pathlib.Path.cwd(); out=root/'docs/reviews/T03/standalone-profile-implementation-20261023/delta-f1-n1'; review=out.parent/'independent-code-review'
def sha(raw): return hashlib.sha256(raw).hexdigest()
manifest_raw=(review/'manifest-d4686b.json').read_bytes()
assert len(manifest_raw)==2644 and sha(manifest_raw)=='78bad0d5bdad109f6c7ed495c11d82fe72a754f47b68ed275eb75b5b7e2af8a9'
manifest=json.loads(manifest_raw)
for row in manifest['files']:
    raw=(review/row['path']).read_bytes(); assert len(raw)==row['bytes'] and sha(raw)==row['sha256'],row['path']
paths=[r['path'] for r in manifest['products']]
products=[]
for path in paths:
    raw=(root/path).read_bytes(); products.append(dict(path=path,bytes=len(raw),sha256=sha(raw)))
reader=ast.parse((root/paths[1]).read_bytes());ast.parse((root/paths[2]).read_bytes())
names=('STANDALONE_CONTRACT_SHA256','STANDALONE_CONTRACT_BYTES','STANDALONE_CONTRACT_SOURCE','STANDALONE_CONTRACT_BUNDLED','STANDALONE_PROVENANCE','STANDALONE_TARGET','STANDALONE_ANCHOR')
constants={n.targets[0].id:ast.literal_eval(n.value) for n in reader.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in names}
raw=(root/paths[3]).read_bytes();x=json.loads(raw);layout=x['fixedLayout'];d=x['pathDomains'];scratch=x['buildScratch']
assert constants['STANDALONE_CONTRACT_SHA256']==sha(raw) and constants['STANDALONE_CONTRACT_BYTES']==len(raw)
assert d['contract']['rowPath']==constants['STANDALONE_CONTRACT_SOURCE']==paths[3]
assert d['contract']['frozenPath']==layout['embeddedContract']==constants['STANDALONE_CONTRACT_BUNDLED']
assert d['inputs']['rowPaths']==[r['path'] for r in x['fixedInputs']]==[r['path'] for r in x['inputMappings']]
assert d['inputs']['sourcePaths']==[r['sourcePath'] for r in x['inputMappings']]
assert d['entrypoint']['rowPath']==layout['target']==constants['STANDALONE_TARGET']
binding=x['schemas']['artifactBinding']['properties'];target=binding['targetCode']
assert target['required']==d['entrypoint']['targetCodeKeys']
assert target['properties']['sourcePath']['const']==layout['target']
assert target['properties']['archiveEntry']['const']==d['entrypoint']['archiveEntry']==x['archivePolicy']['businessScript']
assert binding['launcher']['const']==layout['launcher'] and x['bindingKindRules']['file']['launcherRule'].startswith(layout['launcher']+' ')
assert d['provenance']['frozenPath']==layout['embeddedProvenance']==constants['STANDALONE_PROVENANCE']
assert d['anchor']['module']==layout['anchorModule']==constants['STANDALONE_ANCHOR']
assert scratch['repositoryRelativeRunRoot']==scratch['sampling']['rootTemplate']==layout['uniqueBuildRoot']
assert scratch['sampling']['thresholdBytes']==8589934592 and scratch['sampling']['root']=='runRoot'
assert scratch['sampling']['recursive'] is True
assert all(scratch['sampling'][k] is False for k in ('builderEnforced','osHardLimitImplemented','runtimeGuarantee'))
assert scratch['executionGuard']['guardRequired'] is True and scratch['executionGuard']['permitDigestMayBypass'] is False
assert scratch['executionGuard']['missingOutcome']=='BUILD_SCRATCH_GUARD_REQUIRED'
assert len(x['requiredNegativeTests'])==16 and len(x['sourceGuards'])==len(set(x['sourceGuards']))==35
builder=(root/paths[0]).read_text(); compact=re.sub(r'\s+','',builder)
for field,path in scratch['paths'].items():
    assert path and not path.startswith('/') and '..' not in pathlib.PurePosixPath(path).parts
for option,key in scratch['argv'].items():
    literal="resolve(runRoot,'"+scratch['paths'][key]+"')"
    assert literal in compact or key=='generated',option
for env,key in scratch['environment'].items():
    assert env+":resolve(runRoot,'"+scratch['paths'][key]+"')" in compact,env
assert "constparent=resolve(root,'build/i05-semantic-parity')" in compact
assert 'stdoutPath,stderrPath,receiptPath,stdout,stderr,' in compact
for forbidden in ('docs/reviews/T03/i05-m08-provenance-20261023/private-contract-v1.json','provenance/i05-private-contract-v1.json','packages/engine/entrypoint.py','only static/unit/build helpers permitted','current2cf/6891/401a'):
    assert forbidden not in raw.decode(),forbidden
base='c706f8f581785053278f26e48d21d7bebadf09f6'
protected=json.loads((out.parent/'protected-before.json').read_bytes())
for row in protected['files']:
    current=(root/row['path']).read_bytes();assert len(current)==row['bytes'] and sha(current)==row['sha256']
for path in x['sourceGuards']:
    if path not in paths: assert (root/path).read_bytes()==subprocess.check_output(['git','show',base+':'+path],cwd=root),path
result=dict(scope='static AST/JSON/literal/hash relationships only; no product import, test, stub or helper execution',reviewManifestUnchanged=True,reviewFilesVerified=8,products=products,mechanicalMap=scratch,contractConstants=constants,protectedVectorUnchanged=True,sourceGuardCount=35,unchangedGuards=32,unitGate='NOT_RELEASED')
(out/'static-delta-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
