"""Fresh declaration-index reconciliation; AST only, no product execution."""
import ast
import base64
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-canonical-interface-inventory')
REV=ROOT/'docs/reviews/I05/canonical-interface-inventory'
ITS=ROOT/'docs/iterations/I05/canonical-interface-inventory'
CONTROL=Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release')
SOURCE=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-source-package-probe')
REF='2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64'
checks=[]; commands=[]; trees={}; texts={}

def check(label,truth,detail):
    checks.append({'check':label,'passed':bool(truth),'detail':detail})

def source(path):
    if path not in trees:
        assert not path.endswith('/resources.py')
        p=subprocess.run(['git','show',REF+':'+path],cwd=SOURCE,capture_output=True)
        commands.append({'argv':['git','show',REF+':'+path],'cwd':str(SOURCE),'exitCode':p.returncode,'stdout':{'fixedRef':REF,'path':path,'bytes':len(p.stdout),'sha256':hashlib.sha256(p.stdout).hexdigest()},'stderr':{'base64':base64.b64encode(p.stderr).decode(),'bytes':len(p.stderr)}})
        assert p.returncode==0
        texts[path]=p.stdout.decode(); trees[path]=ast.parse(texts[path])
    return trees[path]

def decl(n):
    if isinstance(n,ast.FunctionDef):return {'name':n.name,'line':n.lineno,'endLine':n.end_lineno,'signature':ast.unparse(n.args),'returnAnnotation':ast.unparse(n.returns) if n.returns else None}
    out={'name':n.name,'line':n.lineno,'endLine':n.end_lineno,'bases':[ast.unparse(x) for x in n.bases],'decorators':[ast.unparse(x) for x in n.decorator_list]}
    out['fields']=[{'name':ast.unparse(x.target),'annotation':ast.unparse(x.annotation),'line':x.lineno,'defaultSyntax':ast.unparse(x.value) if x.value else None} for x in n.body if isinstance(x,ast.AnnAssign)]
    out['methodInterfacesOnly']=[decl(x) for x in n.body if isinstance(x,ast.FunctionDef)]
    init=next((x for x in n.body if isinstance(x,ast.FunctionDef) and x.name=='__init__'),None)
    out['constructorAssignedFieldNamesOnly']=[{'field':x.attr,'line':x.lineno} for x in ast.walk(init) if isinstance(x,ast.Attribute) and isinstance(x.ctx,ast.Store) and isinstance(x.value,ast.Name) and x.value.id=='self'] if init else []
    return out

initial=json.loads((REV/'source-index.json').read_text())
count=0
for module in initial['modules']:
    t=source(module['path']); located={}
    def walk(nodes,prefix=''):
        for n in nodes:
            if isinstance(n,(ast.FunctionDef,ast.ClassDef)):
                located[prefix+n.name]=n;walk(n.body,prefix+n.name+'.')
    walk(t.body)
    for row in module['definitions']:
        n=located[row['name']];expected={'name':row['name'],'kind':type(n).__name__,'line':n.lineno,'endLine':n.end_lineno}
        if isinstance(n,ast.FunctionDef):expected.update(signature=ast.unparse(n.args),returns=ast.unparse(n.returns) if n.returns else None)
        else:expected.update(bases=[ast.unparse(x) for x in n.bases],annotatedFields=[{'name':ast.unparse(x.target),'annotation':ast.unparse(x.annotation),'line':x.lineno,'hasDefault':x.value is not None} for x in n.body if isinstance(x,ast.AnnAssign)])
        check('initialDeclaration:'+module['path']+':'+row['name'],row==expected,expected);count+=1

additional=json.loads((REV/'additional-source-index.json').read_text())
named_count=0
for entry in additional['records']:
    if 'functionOnly' in entry:
        b=(CONTROL/entry['approvedFragment']).read_bytes();top={x.name:x for x in ast.parse(b).body if isinstance(x,(ast.ClassDef,ast.FunctionDef))}
        wanted=[entry['functionOnly']]
    else:
        top={x.name:x for x in source(entry['path']).body if isinstance(x,(ast.ClassDef,ast.FunctionDef))};wanted=entry['namedTargets']
    expected=[decl(top[x]) for x in wanted if x in top]
    check('additionalNamedDeclarations:'+entry['path'],entry['definitions']==expected,expected);named_count+=len(expected)
    check('additionalMissingNames:'+entry['path'],entry.get('missingNamedTargets',[])==[x for x in wanted if x not in top],entry.get('missingNamedTargets',[]))

execution=next(k for k in trees if k.endswith('/semantic_execution.py'));tree=trees[execution]
value=next(m for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_ProfileProjection' for m in n.body if isinstance(m,ast.FunctionDef) and m.name=='value')
seventeen=[x for x in ast.walk(value) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='allowed' for t in x.targets)]
# Expose only canonical type names for human reconciliation, not execute the tuple.
allowed=[{'line':x.lineno,'syntax':ast.unparse(x.value)} for x in seventeen]
extra={}
for path,tree in trees.items():
    if path.endswith('/semantic_profile_production.py'):
        extra['catalogCodecAssignments']=[{'line':n.lineno,'syntax':ast.unparse(n)} for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='catalog_json' for t in n.targets)]
    if path.endswith('/semantic_execution.py'):
        extra['MAX_CELLDeclarations']=[{'line':n.lineno,'syntax':ast.unparse(n)} for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MAX_CELL' for t in n.targets)]
out={'format':'i05-interface-independent-declaration-reconciliation/1','sourceRef':REF,'checks':checks,'initialDefinitionCount':count,'additionalNamedDefinitionCount':named_count,'canonicalAllowedClassExpressions':allowed,'selectedCodecExpressions':extra,'commands':commands,'productExecuted':False,'resourcesWholeSourceRead':False,'ledgerArithmeticOrRatesRead':False}
with (REV/'independent-r1-index-proof.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'checks':len(checks),'failed':[x['check'] for x in checks if not x['passed']],'initialDeclarations':count,'additionalNamedDeclarations':named_count,'canonicalAllowedClassExpressions':allowed,'codecExpressions':extra},ensure_ascii=False,indent=2))
