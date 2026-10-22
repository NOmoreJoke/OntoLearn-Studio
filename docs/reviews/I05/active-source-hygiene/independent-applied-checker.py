import ast, copy, hashlib, io, json, subprocess, tokenize
from pathlib import Path
ROOT=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-active-source-hygiene')
BASE='401a6844d25b8990606ae82fc85f932cac352d40'
FILES={'probe':('packages/engine/src/ontolearn_engine/semantic_source_package_probe.py',102669,'05f4ac85f883f40142782e9ee3943b8df9593ddf5a35e318ca35bbd6781a6dd4'),'test':('packages/engine/tests/test_semantic_source_package_probe.py',75277,'920883c27b6390a2f38aa71bbb399d3b588fe819b1298282da60e6217f11694b')}
result={'kind':'independent static bytes/AST review; no product import or execution','base':BASE,'git_reads':[],'files':{},'checks':{},'binding_sites':[],'snippets':[],'owner_evidence_streams':[]}
def dump(n):return ast.dump(n,include_attributes=False)
def git(args):
 argv=['git','-C',str(ROOT),*args];p=subprocess.run(argv,capture_output=True)
 result['git_reads'].append({'argv':argv,'exit_code':p.returncode,'stderr':p.stderr.decode(),'stdout_bytes':len(p.stdout),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stdout_text':p.stdout.decode() if args[0]!='show' else None})
 assert p.returncode==0
 return p.stdout
def named(t,name):
 ns=[n for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name];assert len(ns)==1,(name,len(ns));return ns[0]
def snippet(label,n,raw):
 lines=raw.decode().splitlines();result['snippets'].append({'label':label,'line_start':n.lineno,'line_end':n.end_lineno,'text':'\n'.join(f'{i}: {lines[i-1]}' for i in range(n.lineno,n.end_lineno+1))})
asts={};raws={}
for key,(rel,sz,h) in FILES.items():
 b=(ROOT/rel).read_bytes();assert len(b)==sz and hashlib.sha256(b).hexdigest()==h,(key,'identity mismatch')
 old=git(['show',f'{BASE}:{rel}']);now=ast.parse(b.decode(),filename=rel);before=ast.parse(old.decode(),filename=f'{BASE}:{rel}')
 asts[key]=(before,now);raws[key]=(old,b)
 result['files'][key]={'path':rel,'current_bytes':len(b),'current_sha256':hashlib.sha256(b).hexdigest(),'base_bytes':len(old),'base_sha256':hashlib.sha256(old).hexdigest()}
 before_comments=[tok.string for tok in tokenize.tokenize(io.BytesIO(old).readline) if tok.type==tokenize.COMMENT]
 now_comments=[tok.string for tok in tokenize.tokenize(io.BytesIO(b).readline) if tok.type==tokenize.COMMENT]
 assert before_comments==now_comments
 result['checks'][key+'_comments_sequence_unchanged']=True
before,now=asts['probe'];norm=copy.deepcopy(now);b1=named(norm,'_b1_observation');original_b1=named(before,'_b1_observation')
expected={'timed':['name','phases'],'build':['asserted','ontology'],'semantic.query':['combined'],'semantic.reason':['combined'],'semantic.check_shapes':['asserted','shapes'],'canonical_bytes':['outputs']}
def label(n):
 if isinstance(n,ast.FunctionDef) and n.name in {'timed','build'}:return n.name
 if isinstance(n,ast.Lambda) and isinstance(n.body,ast.Call):
  f=n.body.func
  if isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name):return f.value.id+'.'+f.attr
  if isinstance(f,ast.Name):return f.id
 return None
seen=[]
for n in ast.walk(b1):
 key=label(n)
 if key not in expected:continue
 names=expected[key];assert key not in seen;seen.append(key)
 assert [a.arg for a in n.args.kwonlyargs]==names,(key,'unexpected kwonlyargs')
 assert all(a.annotation is None and a.type_comment is None for a in n.args.kwonlyargs)
 assert len(n.args.kw_defaults)==len(names)
 assert all(isinstance(d,ast.Name) and d.id==name and isinstance(d.ctx,ast.Load) for d,name in zip(n.args.kw_defaults,names))
 original=[a for a in ast.walk(original_b1) if label(a)==key];assert len(original)==1
 assert not original[0].args.kwonlyargs and not original[0].args.kw_defaults
 result['binding_sites'].append({'site':key,'current_line':n.lineno,'defaults':names,'base_signature':ast.unparse(original[0].args),'current_signature':ast.unparse(n.args),'optional_keyword_only':True,'default_values':'same-name Load nodes evaluated at callable creation'})
 n.args.kwonlyargs=[];n.args.kw_defaults=[]
assert set(seen)==set(expected) and sum(len(x) for x in expected.values())==9
imports=[n for n in b1.body if isinstance(n,ast.ImportFrom)];origimports=[n for n in original_b1.body if isinstance(n,ast.ImportFrom)]
assert len(imports)==len(origimports)==1
imp,oldimp=imports[0],origimports[0]
assert imp.module==oldimp.module=='rdflib' and imp.level==oldimp.level==0
assert [a.name for a in imp.names]==['RDF','Graph','URIRef'] and [a.name for a in oldimp.names]==['Graph','RDF','URIRef']
assert all(a.asname is None for a in imp.names+oldimp.names)
imp.names=copy.deepcopy(oldimp.names)
assert dump(norm)==dump(before),'unexpected probe AST delta beyond exact allowed changes'
assert dump(asts['test'][0])==dump(asts['test'][1]),'test AST differs'
result['checks'].update({'exact_six_sites_nine_optional_keyword_defaults':True,'only_one_exact_unaliased_rdflib_import_permutation':True,'whole_probe_AST_equal_after_only_explicit_normalizations':True,'whole_test_AST_equal_without_normalization':True})
for name in ['ProbeFault','CollectionBoundary','_checked_call']:
 a=named(before,name);b=named(now,name);assert dump(a)==dump(b);snippet(name,b,raws['probe'][1]);result['checks'][name+'_AST_unchanged']=True
scope_before=named(before,'_scope_observation');scope=named(now,'_scope_observation')
assert dump(scope_before)==dump(scope)
result['checks']['whole_scope_observation_AST_unchanged']=True
for stmt in scope.body:
 if any(isinstance(n,ast.Raise) and isinstance(n.exc,ast.Call) and isinstance(n.exc.func,ast.Name) and n.exc.func.id=='ProbeFault' for n in ast.walk(stmt)):
  snippet('scope ProbeFault guard statement',stmt,raws['probe'][1])
testname='test_scope_without_counter_fails_before_loading_canonical_inputs'
a=named(asts['test'][0],testname);b=named(asts['test'][1],testname);assert dump(a)==dump(b);snippet(testname,b,raws['test'][1]);result['checks']['M06_exact_regression_AST_unchanged']=True
snippet('_b1_observation',named(now,'_b1_observation'),raws['probe'][1])
for n in ast.walk(now):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_b1_observation':
  result['snippets'].append({'label':'direct _b1_observation caller expression','line_start':n.lineno,'line_end':n.end_lineno,'text':ast.unparse(n)})
for name in ['environment-01','import-order-fix-01','format-write-01','binding-format-write-01','two-source-lint-01','two-source-format-check-01']:
 receipt_path=ROOT/'docs/reviews/I05/active-source-hygiene'/f'{name}.json';receipt=json.loads(receipt_path.read_bytes());assert receipt['exit']==0
 item={'receipt':str(receipt_path.relative_to(ROOT)),'exit':receipt['exit'],'receipt_sha256':hashlib.sha256(receipt_path.read_bytes()).hexdigest(),'streams':[]}
 for st in receipt['streams']:
  data=(ROOT/st['path']).read_bytes();assert len(data)==st['bytes'] and hashlib.sha256(data).hexdigest()==st['sha256']
  item['streams'].append({'path':st['path'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'exact_text':data.decode()})
 if name=='two-source-lint-01':assert item['streams'][0]['exact_text']=='[]' and item['streams'][1]['exact_text']==''
 result['owner_evidence_streams'].append(item)
result['branch']=git(['branch','--show-current']).decode().strip();result['HEAD']=git(['rev-parse','HEAD']).decode().strip();assert result['HEAD']==BASE
for key,(rel,sz,h) in FILES.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h
result['checks']['current_source_hashes_rechecked_at_end']=True
result['findings']={'P1':[],'P2':[],'scope':'no actionable P1/P2 found in permitted narrow static change; not full behavioral equivalence or release approval'}
print(json.dumps(result,ensure_ascii=False,indent=2))
