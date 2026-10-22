"""Independent fixed-source AST/interface checks. Never imports product code."""
import ast
import base64
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-canonical-interface-inventory')
REV = ROOT / 'docs/reviews/I05/canonical-interface-inventory'
ITS = ROOT / 'docs/iterations/I05/canonical-interface-inventory'
CONTROL = Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release')
SOURCE = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-source-package-probe')
REF = '2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64'
CANDIDATE = '4beccef733396d525b9db56be544dbdb551581ad'
commands, checks = [], []

def sha(b):
    return hashlib.sha256(b).hexdigest()

def run(argv, cwd, stdout_source=None):
    p = subprocess.run(argv, cwd=cwd, capture_output=True)
    commands.append({'argv': argv, 'cwd': str(cwd), 'exitCode': p.returncode,
                     'stdout': {'bytes': len(p.stdout), 'sha256': sha(p.stdout),
                                'fixedSource': stdout_source,
                                'base64': None if stdout_source else base64.b64encode(p.stdout).decode()},
                     'stderr': {'bytes': len(p.stderr), 'sha256': sha(p.stderr),
                                'base64': base64.b64encode(p.stderr).decode()}})
    assert p.returncode == 0, (argv, p.returncode)
    return p.stdout

def check(name, truth, detail):
    checks.append({'check': name, 'passed': bool(truth), 'detail': detail})
    if not truth:
        print('MISMATCH', name, detail)

def fields(n):
    return [{'name': ast.unparse(v.target), 'typeAnnotation': ast.unparse(v.annotation),
             'line': v.lineno, 'defaultSyntax': ast.unparse(v.value) if v.value else None}
            for v in n.body if isinstance(v, ast.AnnAssign)]

def main():
    manifest = json.loads((REV/'candidate-manifest.json').read_text())
    member_names = [x['path'] for x in manifest['files']] + ['docs/reviews/I05/canonical-interface-inventory/candidate-manifest.json']
    changed = run(['git','diff','--name-only', '1b6df7a220fc9a67d7046133a340085f03f0a96c', CANDIDATE], ROOT).decode().splitlines()
    check('candidate23ExactMembership', sorted(changed) == sorted(member_names) and len(member_names)==23, changed)
    for name in member_names:
        b=(ROOT/name).read_bytes(); git=run(['git','show',CANDIDATE+':'+name],ROOT, {'ref':CANDIDATE,'path':name})
        e=next((e for e in manifest['files'] if e['path']==name),None)
        check('candidateCurrentGit:'+name,b==git and (e is None or (len(b)==e['bytes'] and sha(b)==e['sha256'])), {'bytes':len(b),'sha256':sha(b)})
        if name.endswith('.json'): json.loads(b)
    bindings=[]
    for name, inventory, key in [
        ('I05-M02-M05-eight-source-static-read-binding-20261022.json','source-inputs.json','files'),
        ('I05-M02-M05-additional-interface-static-read-binding-20261022.json','additional-source-inputs.json','inputs')]:
        b=(CONTROL/name).read_bytes(); binding=json.loads(b); inv=json.loads((ITS/inventory).read_text())
        check('binding:'+name, len(b)==inv['bindingBytes'] and sha(b)==inv['bindingSha256'], {'bytes':len(b),'sha256':sha(b)})
        check('bindingEntries:'+name, binding[key]==inv[key],len(inv[key]))
        bindings.append(binding)
    final_b=(CONTROL/'I05-M02-M05-final-two-declarations-static-read-binding-20261022.json').read_bytes()
    final=json.loads(final_b); final_inv=json.loads((ITS/'final-fragment-inputs.json').read_text())
    check('finalBinding', len(final_b)==final_inv['binding']['bytes'] and sha(final_b)==final_inv['binding']['sha256'],len(final_b))
    trees, texts={},{}
    for entry in bindings[0]['files'] + [e for e in bindings[1]['inputs'] if 'bytes' in e]:
        path=entry['path'];b=run(['git','show',REF+':'+path], SOURCE,{'ref':REF,'path':path})
        check('sourceIdentity:'+path,len(b)==entry['bytes'] and sha(b)==entry['sha256'],{'bytes':len(b),'sha256':sha(b)})
        trees[path]=ast.parse(b.decode());texts[path]=b.decode()
    check('19SourceFiles531192',len(trees)==19 and sum(len(t.encode()) for t in texts.values())==531192,len(trees))
    fragments=[]
    e=bindings[1]['inputs'][-1]
    fragments.append((e['approvedFragment'],e['fragmentBytes'],e['fragmentSHA256']))
    for e in final['entries']:
        fragments.append((e['fragment'],e.get('bytes'),e.get('sha256',e.get('fragmentSHA256'))))
    for name,count,digest in fragments:
        b=(CONTROL/name).read_bytes(); check('fragment:'+name,sha(b)==digest and (count is None or len(b)==count), {'bytes':len(b),'sha256':sha(b)})
    records=json.loads((ITS/'additional-return-layouts.json').read_text())['records']
    record_by_class={r['class']:r for r in records}
    for r in records:
        if r['class']=='RootRef':
            f=json.loads((CONTROL/'I05-M02-M05-rootref-fixed-field-declarations.json').read_text());node=ast.parse(f['header']+''.join(x['source'] for x in f['fields'])).body[0]
            expected=fields(node)
            for x,row in zip(expected,f['fields']):x['line']=row['firstLine']
        else:
            n=next(x for x in trees[r['path']].body if isinstance(x,ast.ClassDef) and x.name==r['class']);expected=fields(n)
            check('returnClassLocation:'+r['class'],r['line']==n.lineno and r['endLine']==n.end_lineno,{'line':n.lineno,'endLine':n.end_lineno})
        check('returnLocalFields:'+r['class'],r['fields']==expected,{'fields':expected})
        merged={}
        for base in r.get('bases',[]):
            if base in record_by_class:
                merged.update({x['name']:x for x in record_by_class[base]['staticallyExpandedInheritedFields']})
        merged.update({x['name']:x for x in expected})
        check('returnInheritedFields:'+r['class'],r['staticallyExpandedInheritedFields']==list(merged.values()),list(merged))
    check('ProfileExplanation15',len(record_by_class['ProfileExplanationComputation']['staticallyExpandedInheritedFields'])==15,15)
    api=json.loads((ITS/'api-layouts.json').read_text())
    def find(path,name):
        seq=trees[path].body
        node=None
        for part in name.split('.'):
            node=next(x for x in seq if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name==part);seq=node.body
        return node
    dictionary_shapes=[]
    for r in api['layouts']:
        n=find(r['source']['path'],r['source']['function']);shapes=[]
        for x in ast.walk(n):
            if isinstance(x,ast.Dict):
                keys=[k.value if isinstance(k,ast.Constant) else ('**'+ast.unparse(v) if k is None else ast.unparse(k)) for k,v in zip(x.keys,x.values)]
                shapes.append({'line':x.lineno,'keys':keys})
        dictionary_shapes.append({'id':r['id'],'actualFunctionLine':n.lineno,'actualFunctionEnd':n.end_lineno,'dicts':shapes})
        # Ranges may deliberately span an enclosing body, record all exact source facts for human review.
        if 'orderedKeys' in r:
            keylist=r['orderedKeys']; directly=any(x['keys']==keylist for x in shapes)
            if r['id']=='legacy-provenance':directly=any(x['keys']==['scope','**source']+keylist[5:] for x in shapes)
            check('apiDictKeys:'+r['id'],directly,{'expected':keylist,'sourceShapes':shapes})
    for r in api['classAnnotationIndex']:
        n=find(r['source']['path'],r['source']['function']);expected=[{'name':x['name'],'annotation':x['typeAnnotation'],'line':x['line'],'hasDefault':x['defaultSyntax'] is not None} for x in fields(n)]
        check('apiAnnotatedFields:'+r['source']['function'],r['annotatedFields']==expected,expected)
    # Text snippets restricted to initial eight approved files and a few permitted helper API expressions.
    snippets=[]
    selections={'semantic_scopes.py':['_digest','_source','project_validation_scope','prepare_validation_scope'],
                'semantic.py':['_legacy_reason','_check_shapes','query','_key','_canonical_rule'],
                'semantic_execution.py':['_json','_digest','_ProfileProjection','_profile_json_bytes','_profile_diagnostic','_execute_profile'],
                'semantic_source_package_probe.py':['_bytes_value','_graph_value','_typed_value','_capture_expectation','_production_observation'],
                'semantic_profile_input.py':['_project','_encode','_definitions']}
    for path, tree in trees.items():
        if Path(path).name in selections:
            for n in tree.body:
                if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in selections[Path(path).name]:
                    # Structured statements only, not copied whole source bodies.
                    snippets.append({'path':path,'name':n.name,'line':n.lineno,'endLine':n.end_lineno,
                                     'returnExpressions':[{'line':x.lineno,'value':ast.unparse(x.value)} for x in ast.walk(n) if isinstance(x,ast.Return)],
                                     'jsonCalls':[{'line':x.lineno,'value':ast.unparse(x)} for x in ast.walk(n) if isinstance(x,ast.Call) and ('json.' in ast.unparse(x.func) or ast.unparse(x.func) in ['hashlib.sha256'])]})
    result={'format':'i05-interface-independent-static-checks/1','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':CANDIDATE,'sourceRef':REF,'checks':checks,'commands':commands,'dictionaryShapes':dictionary_shapes,'selectedInterfaceExpressions':snippets,'productExecuted':False,'resourcesWholeSourceRead':False,'feeOrLedgerAlgorithmsReviewed':False,'noActualExpectedProbeInputsRead':True}
    with (REV/'independent-r1-proof.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'checks':len(checks),'failed':[x['check'] for x in checks if not x['passed']],'sources':len(trees),'returnClasses':len(records),'commands':len(commands)},ensure_ascii=False))
    print(json.dumps({'dictionaryShapes':dictionary_shapes,'selectedInterfaceExpressions':snippets},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
