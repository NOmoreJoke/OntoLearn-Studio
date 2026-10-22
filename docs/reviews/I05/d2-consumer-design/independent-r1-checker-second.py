"""Independent read-only finite design audit. No candidate code is executed.

Only stdlib JSON/hash/path/Git operations. Reads the 27 explicitly authorized
inputs and the new D2 candidate. Prints JSON; does not write any file. This is
not a JSON Schema engine, runtime validator, RDF parser, or product comparator.
"""
import base64
import collections
import hashlib
import itertools
import json
import pathlib
import subprocess

ROOT = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
REVIEW = ROOT / 'docs/reviews/I05/d2-consumer-design'
DESIGN = ROOT / 'docs/iterations/I05/d2-consumer-design'
CONTROL = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release')
BASE = '5f910b52c69d86a1076b2032e5d3c63e715947f3'
CANDIDATE = 'd2c28a2bf549f4202b6188dde7fe4efee1c8769e'
PROCESS = 'e4f11058ab92fee6731737a89fc87dfc9f552569'
COMMANDS = []
ISSUES = []
STREAM_FILES = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stream(raw):
    digest = sha(raw)
    if digest in STREAM_FILES:
        return {'bytes': len(raw), 'sha256': digest, 'exactExistingRawFile': STREAM_FILES[digest]}
    return {'bytes': len(raw), 'sha256': digest, 'base64': base64.b64encode(raw).decode('ascii')}


def git(*args, repo=ROOT):
    argv = ['git', '-C', str(repo), *args]
    p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    COMMANDS.append({'argv': argv, 'cwd': str(ROOT), 'exit': p.returncode,
                     'stdout': stream(p.stdout), 'stderr': stream(p.stderr)})
    if p.returncode:
        raise RuntimeError('read-only Git failed: ' + repr(argv))
    return p.stdout


def pairs(items):
    d = {}
    for k, v in items:
        if k in d:
            raise ValueError('duplicate JSON key')
        d[k] = v
    return d


def bad_constant(s):
    raise ValueError('nonfinite JSON')


def load(path):
    raw = pathlib.Path(path).read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        raise ValueError('BOM')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=bad_constant)


def canonical(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def esc(s):
    return s.replace('~', '~0').replace('/', '~1')


def ptr(o, p):
    p = p.removeprefix('#')
    for part in p[1:].split('/') if p else []:
        part = part.replace('~1', '/').replace('~0', '~')
        o = o[int(part)] if type(o) is list else o[part]
    return o


def leaves(o, p=''):
    if type(o) is dict and o:
        for k, v in o.items():
            yield from leaves(v, p + '/' + esc(k))
    elif type(o) is list and o:
        for i, v in enumerate(o):
            yield from leaves(v, p + '/' + str(i))
    else:
        yield p, o


def check(value, label):
    if not value:
        ISSUES.append(label)


def enumerate_properties(o, p='#'):
    if type(o) is dict:
        for name, node in o.get('properties', {}).items():
            yield p + '/properties/' + esc(name), node, name in o.get('required', [])
        for k, v in o.items():
            yield from enumerate_properties(v, p + '/' + esc(k))
    elif type(o) is list:
        for i, v in enumerate(o):
            yield from enumerate_properties(v, p + '/' + str(i))


def locations(schema):
    found = collections.defaultdict(list)
    arrays, objects = [], []

    def visit(node, sp, ip, conditions, dimensions, trail):
        if type(node) is not dict:
            return
        if '$ref' in node:
            target = node['$ref']
            if target in trail:
                raise ValueError('recursive reference outside finite index')
            visit(ptr(schema, target), target, ip, conditions + (('$ref', sp + '/$ref', target),), dimensions, trail + (target,))
        if 'properties' in node:
            objects.append((sp, ip, tuple(conditions), node.get('required', []), node.get('additionalProperties'), list(node['properties'])))
        if 'items' in node:
            var = 'i' + str(len(dimensions))
            arrays.append((sp, ip, tuple(conditions), var))
            visit(node['items'], sp + '/items', ip + '/{' + var + '}', conditions,
                  dimensions + ((var, ip),), trail)
        for name, child in node.get('properties', {}).items():
            childp = sp + '/properties/' + esc(name)
            inst = ip + '/' + esc(name)
            found[childp].append((inst, tuple(conditions), dimensions))
            visit(child, childp, inst, conditions, dimensions, trail)
        for key in ('oneOf', 'anyOf', 'allOf'):
            for i, child in enumerate(node.get(key, [])):
                cp = sp + '/' + key + '/' + str(i)
                visit(child, cp, ip, conditions + ((key, cp),), dimensions, trail)
        for i, child in enumerate(node.get('prefixItems', [])):
            visit(child, sp + '/prefixItems/' + str(i), ip + '/' + str(i), conditions, dimensions, trail)
    visit(schema, '#', '', (), (), ())
    return found, arrays, objects


def branch_identity(branch):
    return (branch['keyword'], branch['schemaPointer']) if 'keyword' in branch else ('$ref', branch['ref'], branch['target'])


def main():
    identity = load(REVIEW / 'input-identity.json')
    for entry in identity['inputs']:
        p = REVIEW / entry['local']
        STREAM_FILES[sha(p.read_bytes())] = str(p)
    for entry in load(REVIEW/'candidate-manifest.json')['files']:
        p = ROOT / entry['path']
        STREAM_FILES[sha(p.read_bytes())] = str(p)
    for name in ('candidate-manifest.json', 'candidate-receipt.json'):
        p = REVIEW/name
        STREAM_FILES[sha(p.read_bytes())] = str(p)
    fixed = load(CONTROL / 'I05-d2-consumer-design-fixed-inputs.json')['inputs']
    check(len(identity['inputs']) == len(fixed) == 27, 'fixed-input-count')
    source, ids = {}, []
    for n, (declared, ident) in enumerate(zip(fixed, identity['inputs'])):
        original = git('show', declared['ref'] + ':' + declared['path'], repo=declared['repository']) if 'ref' in declared else pathlib.Path(declared['path']).read_bytes()
        raw = (REVIEW / ident['local']).read_bytes()
        check(raw == original and len(raw) == declared['bytes'] == ident['bytes'] and sha(raw) == declared['sha256'] == ident['sha256'], 'input-identity-' + str(n))
        source[n] = load(REVIEW / ident['local']) if declared['path'].endswith('.json') else raw.decode('utf-8')
        ids.append({'input': n, 'bytes': len(raw), 'sha256': sha(raw), 'currentGitDeclaredEqual': raw == original})
    check(git('rev-parse', 'HEAD').decode().strip() == PROCESS, 'HEAD')
    check(git('branch', '--show-current').decode().strip() == 'docs/I05-d2-consumer-design', 'branch')
    git('merge-base', '--is-ancestor', BASE, CANDIDATE)
    git('merge-base', '--is-ancestor', CANDIDATE, PROCESS)
    manifest = load(REVIEW / 'candidate-manifest.json')
    inventory = []
    for entry in manifest['files']:
        p = entry['path']
        raw = (ROOT / p).read_bytes()
        blob = git('show', CANDIDATE + ':' + p)
        process_blob = git('show', PROCESS + ':' + p)
        check(raw == blob == process_blob and len(raw) == entry['bytes'] and sha(raw) == entry['sha256'], 'manifest-' + p)
        inventory.append({'path': p, 'bytes': len(raw), 'sha256': sha(raw), 'currentCandidateProcessDeclaredEqual': raw == blob == process_blob})
    for name, ref, expected_bytes, expected_sha in [
        ('candidate-manifest.json', CANDIDATE, 8352, 'a70f81a78b862b0ad00a49157766097aced6ba7e6e19a7d1635f4e2bea5ea7b1'),
        ('candidate-receipt.json', PROCESS, 93700, '30dda838bc46f6c8332a529e902366a73f2d46fd0672a4274e2606eb04d5a209')]:
        p = REVIEW / name
        raw = p.read_bytes()
        check(raw == git('show', ref + ':' + str(p.relative_to(ROOT))) and len(raw) == expected_bytes and sha(raw) == expected_sha, name)
        inventory.append({'path': str(p.relative_to(ROOT)), 'bytes': len(raw), 'sha256': sha(raw), 'currentFixedGitDeclaredEqual': True})
    changed = git('diff', '--name-only', BASE, PROCESS).decode().splitlines()
    check(set(changed) == {x['path'] for x in inventory} and len(changed) == 38, 'precise-38-docs-diff')
    check(git('diff', '--cached', '--name-only') == b'', 'empty-index')
    agents = []
    for p in [ROOT/'AGENTS.md', pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/AGENTS.md')]:
        raw = p.read_bytes()
        check(len(raw) == 15147 and sha(raw) == 'de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4', 'guidance-'+str(p))
        agents.append({'path': str(p), 'bytes': len(raw), 'sha256': sha(raw)})
    fmap = load(DESIGN/'field-origin-map.json')
    amap = load(DESIGN/'acceptance-map.json')
    rejects = load(DESIGN/'reject-cases.json')
    schema_by_name = {fixed[i]['path'].split('/')[-1]: source[i] for i in (4, 5, 7, 6)}
    rows = {(x['schema'], x['schemaPointer']): x for x in fmap['fieldRows']}
    check(len(rows) == len(fmap['fieldRows']), 'duplicate-field-identity')
    field_results, counts = [], {}
    for name, schema in schema_by_name.items():
        enumerated = list(enumerate_properties(schema))
        loc, arrays, objects = locations(schema)
        counts[name] = len(enumerated)
        check({p for p, _, _ in enumerated} == {p for s, p in rows if s == name}, 'property-set-'+name)
        for sp, node, required in enumerated:
            row = rows[name, sp]
            actual = [(x['pointerTemplate'], tuple(branch_identity(c) for c in x['branchConditions']), tuple((d['variable'], d['arrayPointerTemplate']) for d in x['arrayVariables'])) for x in row['instanceLocations']]
            expected = loc[sp]
            check(actual == expected, 'instance-location-'+row['id'])
            check(row['originalResponsibility']['required'] is required, 'required-'+row['id'])
            check(canonical(ptr(source[2], row['responsibilitySource']['pointer'])) == canonical(row['originalResponsibility']), 'responsibility-'+row['id'])
            check(canonical(ptr(schema, row['fixedSource']['pointer'])) == canonical(node), 'fixed-pointer-'+row['id'])
            constraints = {k: v for k, v in node.items() if k not in ('properties','items','oneOf','anyOf','allOf','prefixItems')}
            check(canonical(constraints) == canonical(row['localConstraints']), 'constraints-'+row['id'])
            check(bool(actual) == (row['reachability'] == 'instance-reachable'), 'reachability-'+row['id'])
            field_results.append({'id': row['id'], 'schema': name, 'pointer': sp, 'independentLocations': [{'path': a, 'conditions': b, 'arrayDimensions': c} for a,b,c in expected]})
        actual_arrays = [(x['schemaPointer'],x['instanceTemplate'],tuple(branch_identity(b) for b in x['branchConditions']),x['indexVariable']) for x in fmap['arrayInstanceRules'] if x['schema']==name]
        check(actual_arrays == arrays, 'all-array-instance-rules-'+name)
        actual_objects = [(x['schemaPointer'],x['instanceTemplate'],tuple(branch_identity(b) for b in x['branches']),x['required'],x['additionalProperties'],x['properties']) for x in fmap['objectInstanceRules'] if x['schema']==name]
        check(actual_objects == objects, 'all-object-instance-rules-'+name)
    check(sum(counts.values()) == 1241, '1241-independent-property-count')
    check(sum(bool(x['independentLocations']) for x in field_results) == 1229, '1229-independent-reachable')
    check(canonical(dict(leaves(source[3]))) == canonical({x['pointer']:x['value'] for x in fmap['profileConcreteLeaves']}), 'profile-all-values')
    case_results = []
    for i,(original, candidate) in enumerate(zip(source[16]['cases'],amap['projectionCases'])):
        for key in ('id','api','parameters','kind','preconditions','finiteRelations','pending'):
            check(canonical(original[key]) == canonical(candidate[key]), 'projection-'+str(i)+'-'+key)
        check(candidate['requiredComparisonEntry']=='matches', 'comparison-entry-'+str(i))
        check(candidate['expectedProjectionSha256']==sha(canonical(original['expectedProjection']).encode()), 'expected-preimage-'+str(i))
        check(canonical(ptr(source[16],candidate['casePointer']['pointer'])) == canonical(original), 'whole-case-reference-'+str(i))
        declared_leaves = {x['fieldPointer']:x['value'] for x in fmap['projectionExpectedLeaves'] if x['caseId']==original['id']}
        check(canonical(dict(leaves(original['expectedProjection']))) == canonical(declared_leaves), 'expected-leaves-'+str(i))
        case_results.append({'id': original['id'], 'completeCaseSha256':sha(canonical(original).encode()), 'expectedSha256':candidate['expectedProjectionSha256'], 'expectedLeafCount':len(declared_leaves), 'completeOriginalKeys':list(original)})
    check(len(case_results)==37 and len(fmap['projectionExpectedLeaves'])==1469, '37-and-1469')
    # New independent finite witnesses. No schema/model/author function called.
    finite = []
    def witness(name, observed, expected):
        check(observed == expected, 'finite-'+name)
        finite.append({'name':name,'observed':observed,'expected':expected})
    observed = {'truth':False,'unknown':None,'zero':0,'nested':[False,None,{'v':''}]}
    nonnull = [p for p,v in leaves(observed) if v is not None and type(v) not in (dict,list)]
    witness('false-zero-empty-string-observed',nonnull,['/truth','/zero','/nested/0','/nested/2/v'])
    signal, exit_code = 'SIGKILL', 1
    witness('signal-cannot-have-exit',not (signal is not None and exit_code is not None),False)
    witness('pending-false-is-not-null',all(v is None for v in [None,None,None,None,None,False]),False)
    witness('compared-three-independent-booleans',all(type(v) is bool for v in [False,True,False]),True)
    witness('two-b1-do-not-total-full',1+1==417,False)
    witness('source22-declarations-distinct-from23-actual',22!=23,True)
    triples=[('<urn:a>','<urn:p>','<urn:x>'),('<urn:b>','<urn:p>','<urn:y>')]
    witness('reverse-wire-is-not-canonical',list(reversed(triples))==sorted(triples),False)
    # Joint-domain counterexample: graph alone admits swap, ordered query binds it.
    left={'graph':[('a','x'),('b','y')],'query':['a','a'],'raw':'EN'}
    right={'graph':[('p','y'),('q','x')],'query':['q','q'],'raw':'EN'}
    def detached_two_node_equal(a,b):
        for perm in itertools.permutations(['p','q']):
            m=dict(zip(['a','b'],perm))
            if sorted((m[x],v) for x,v in a['graph'])==sorted(b['graph']) and [m[x] for x in a['query']]==b['query'] and a['raw']==b['raw']:
                return True
        return False
    witness('cross-renaming-joint-domain',detached_two_node_equal(left,right),True)
    wrong={**right,'query':['p','p']}
    witness('independently-isomorphic-query-is-wrong-domain',detached_two_node_equal(left,wrong),False)
    witness('occurrence-duplicate-tail-required',[1,1]==[1],False)
    witness('numeric-lexical-01-not-1','01'=='1',False)
    witness('datatype-int-not-integer','xsd:int'=='xsd:integer',False)
    witness('raw-language-kept-exact','EN'=='en',False)
    for text in ['{"x":1,"x":2}','{"x":NaN}','{"x":1} extra']:
        rejected=False
        try:json.loads(text,object_pairs_hook=pairs,parse_constant=bad_constant)
        except ValueError:rejected=True
        witness('strict-json-'+text,rejected,True)
    output={'evidenceClass':'independent-finite-static-design-audit-only','issues':ISSUES,'fixedInputs':ids,'inventory':inventory,'guidance':agents,'independentSchemaCounts':counts,'fieldAudit':field_results,'profileLeafCount':len(dict(leaves(source[3]))),'caseAudit':case_results,'finiteWitnesses':finite,'declaredRejects':len(rejects['cases']),'declaredSyntheticDesigns':len(rejects['finiteSyntheticCases']),'commands':COMMANDS,'wholeOracleComplete':False,'productExecuted':False,'schemaEngineValidation':False}
    print(json.dumps(output,ensure_ascii=False,indent=2))
    raise SystemExit(1 if ISSUES else 0)


if __name__ == '__main__':
    main()
