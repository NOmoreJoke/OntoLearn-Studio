import ast, hashlib, json, pathlib, re, subprocess
root=pathlib.Path.cwd()
process=root/'docs/reviews/T03/standalone-profile-implementation-20261023'
products=['scripts/build-engine.mjs','packages/engine/src/ontolearn_engine/semantic_build_provenance.py','packages/engine/tests/test_semantic_build_provenance.py','docs/iterations/T03/i05-semantic-parity-profile/private-profile-contract-v1.json']
def identity(path):
    raw=(root/path).read_bytes()
    return dict(path=path,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
reader=ast.parse((root/products[1]).read_bytes())
ast.parse((root/products[2]).read_bytes())
constants={n.targets[0].id:ast.literal_eval(n.value) for n in reader.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('STANDALONE_CONTRACT_SHA256','STANDALONE_CONTRACT_BYTES')}
contract_raw=(root/products[3]).read_bytes(); contract=json.loads(contract_raw)
assert constants['STANDALONE_CONTRACT_SHA256']==hashlib.sha256(contract_raw).hexdigest()
assert constants['STANDALONE_CONTRACT_BYTES']==len(contract_raw)
assert len(contract['sourceGuards'])==len(set(contract['sourceGuards']))==35
assert len(contract['analysisImports'])==len(set(contract['analysisImports']))==25
assert len(contract['buildInputs'])==5
assert len(contract['excludedModules'])==10
builder=(root/products[0]).read_text()
for name,argument in [('prepareProgram','2'),('finalizeProgram','3')]:
    block=re.search(r'const '+name+r" = (\[.*?\])\.join\('\\n'\)",builder,re.S).group(1)
    program='\n'.join(ast.literal_eval(block))
    ast.parse(program)
    standalone=program.replace('Path(sys.argv['+argument+']))','Path(sys.argv['+argument+']),profile="i05-source-package-parity")')
    parsed=ast.parse(standalone)
    assert 'profile="i05-source-package-parity"' in standalone
    (process/(name+'-standalone.py.raw')).write_text(standalone+'\n')
base='c706f8f581785053278f26e48d21d7bebadf09f6'
protected=json.loads((process/'protected-before.json').read_bytes())
for row in protected['files']: assert identity(row['path'])==row,row['path']
guards=[]
for path in contract['sourceGuards']:
    if path in products: continue
    raw=subprocess.check_output(['git','show',base+':'+path],cwd=root)
    expected=dict(path=path,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    assert identity(path)==expected,path
    guards.append(expected)
result=dict(scope='AST/JSON/literal-only; no product import or execution',base=base,products=[identity(p) for p in products],guardCount=35,unchangedGuardCount=len(guards),unchangedGuards=guards,protectedFiles=protected['files'],contractConstants=constants,inlinePrograms='parent and literal standalone variants AST parsed',runtimeChecks='NOT RUN; waiting independent review and exact START')
(process/'static-source-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
