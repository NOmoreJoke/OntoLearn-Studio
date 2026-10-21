"""Structural consistency only. Does not infer RDF, discover bindings or compare values."""
from pathlib import Path
import hashlib
import csv
import io
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def no_duplicates(pairs):
    d = {}
    for k, v in pairs:
        assert k not in d, ('duplicate JSON key', k)
        d[k] = v
    return d

def read(p):
    return json.loads(p.read_text(), object_pairs_hook=no_duplicates)

def digest(b):
    return hashlib.sha256(b).hexdigest()

inputs = read(HERE / 'inputs.json')
sources = {}
for entry in inputs['sources']:
    p = ROOT / entry['path']
    raw = p.read_bytes()
    assert len(raw) == entry['bytes'] and digest(raw) == entry['sha256'], entry['path']
    sources[entry['id']] = read(p) if p.suffix == '.json' else raw.decode()

oracle = read(ROOT / 'tests/fixtures/quality/real-executor-acceptance-inputs.json')
triples = oracle['triples']
graphs = oracle['graphs']
matches = oracle['matches']
rules = oracle['ruleDefinitions']
witnesses = oracle['rdfsWitnesses']

def pointer(value, path):
    for part in path.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value

def check_ref(r):
    assert r['sourceId'] in sources, r
    entry = next(x for x in inputs['sources'] if x['id'] == r['sourceId'])
    assert entry['sha256'] == r['sha256'], r
    return pointer(sources[r['sourceId']], r['pointer'])

canonical = [tuple(t['n3']) for t in triples.values()]
assert len(canonical) == len(set(canonical)), 'duplicate canonical triple dictionary entries'
for tid, t in triples.items():
    assert len(t['n3']) == 3 and all(type(v) is str for v in t['n3'])
    assert t['n3'] == ['<' + t['encodedFixtureTerms'][0] + '>', '<' + t['encodedFixtureTerms'][1] + '>', t['encodedFixtureTerms'][2]]
    assert t['rawImportSource'] == 'unavailable' and t['rawImportToken'] is None and t['rawImportByteSpan'] is None
    for r in t['inputOccurrences']:
        original = check_ref(r)
        original = [original['subject'], original['predicate'], original['object']] if isinstance(original, dict) else original
        assert original == t['encodedFixtureTerms'], (tid, r)
for r in rules.values():
    assert check_ref(r['inputRef']) == r['definition']
for wid, w in witnesses.items():
    assert w['resultTripleId'] in triples
    assert w['derivationLevel'] == 1
    assert set(w['axiomTripleIds']) <= set(w['orderedDirectPremiseTripleIds'])
    assert set(w['leafBasisTripleIds']) == set(w['orderedDirectPremiseTripleIds'])
    for r in w['inputRefs']:
        check_ref(r)
for gid, g in graphs.items():
    for field in ['assertedTripleIds', 'ontologyTripleIds', 'rdfsAddedTripleIds', 'customOutputTripleIds', 'derivedUnionTripleIds']:
        ids = g[field]
        assert ids == sorted(set(ids)), (gid, field, 'duplicate/unsorted ID set')
        assert set(ids) <= set(triples), (gid, field, 'unknown triple ID')
    assert not (set(g['rdfsAddedTripleIds']) & (set(g['assertedTripleIds']) | set(g['ontologyTripleIds']))), gid
    assert set(g['derivedUnionTripleIds']) == set(g['rdfsAddedTripleIds']) | set(g['customOutputTripleIds']), gid
    assert all(r in rules for r in g['ruleDefinitionRefs'])
    closure = set(g['assertedTripleIds']) | set(g['ontologyTripleIds']) | set(g['rdfsAddedTripleIds'])
    leaves = set(g['assertedTripleIds']) | set(g['ontologyTripleIds'])
    heads = set()
    for mid in g['matchRefs']:
        m = matches[mid]
        assert set(m['whenTripleIdsInDefinitionOrder']) <= closure, (gid, mid, 'when not present')
        assert set(m['leafBasisTripleIds']) <= leaves, (gid, mid, 'basis not input leaf')
        assert len(m['whenTripleIdsInDefinitionOrder']) > 0
        assert m['accepted'] is True or (m['accepted'] is False and m['heads'] == [])
        for h in m['heads']:
            assert h['tripleId'] in triples
            heads.add(h['tripleId'])
    assert heads == set(g['customOutputTripleIds']), (gid, 'head set/custom set mismatch')
    assert {witnesses[r]['resultTripleId'] for r in g['rdfsWitnessRefs']} == set(g['rdfsAddedTripleIds']), gid
    assert g['completenessArgument'] in oracle['completenessArguments'], gid
    payload = {'asserted': [triples[t]['n3'] for t in g['assertedTripleIds']], 'ontology': [triples[t]['n3'] for t in g['ontologyTripleIds']], 'rules': [rules[r]['definition'] for r in g['ruleDefinitionRefs']]}
    assert g['oracleInputSha256'] == digest(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()), gid

for alias in oracle['inputValueAliases'].values():
    left=check_ref(alias['left']);right=check_ref(alias['right'])
    assert left==right
    raw=json.dumps(left,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    assert digest(raw)==alias['canonicalValueSha256']
for key,row in oracle['mappingDerivations'].items():
    csv_text=check_ref(row['csvRef']);mapping=check_ref(row['mappingRef'])
    records=list(csv.DictReader(io.StringIO(csv_text)))
    record=records[row['physicalLine']-2]
    assert record[row['column']]==row['rawCell'] and record['equipment_id']==row['key']
    encoded=triples[row['tripleId']]['encodedFixtureTerms']
    assert encoded[0]==mapping['subjectTemplate'].replace('{equipment_id}',row['key'])
    if row['column']=='equipment_id':
        assert encoded[2]=='<'+mapping['type']+'>'
    else:
        assert encoded[1]==mapping['columns'][row['column']]
        assert encoded[2]==json.dumps(row['rawCell'],ensure_ascii=False)
for gid,g in graphs.items():
    if gid.startswith(('map-','imported')):
        baseline=check_ref(g['effectiveBaselineRef'])
        assert baseline['id']=='G-map-empty'
        assert g['ruleDefinitionRefs']==['R-risk/map']
        assert check_ref(rules['R-risk/map']['inputRef'])==baseline['rules'][0]
        ont=check_ref(g['effectiveOntologyRef'])
        assert {tuple(triples[t]['encodedFixtureTerms']) for t in g['ontologyTripleIds']}=={(r['subject'],r['predicate'],r['object']) for r in ont}
        assert set(g['mappingDerivationRefs'])=={k for k,v in oracle['mappingDerivations'].items() if v['tripleId'] in g['assertedTripleIds']}
assert not any('deviceB-edit' in gid for gid in graphs)
assert not any(t['encodedFixtureTerms'][2]=='"设备B编辑"' for t in triples.values())

src_cases = sources['T09/tests/fixtures/product-baselines/cases.json']['cases']
assert [c['id'] for c in oracle['productCases']] == [c['id'] for c in src_cases]
assert len(set(c['id'] for c in oracle['productCases'])) == 50
op_count = 0
for c, original in zip(oracle['productCases'], src_cases):
    assert check_ref(c['inputRef']) == original
    assert check_ref(c['effectiveBaselineRef'])['id']==original['baseline']
    for key in c.get('inputValueAliasRefs',[]):
        assert key in oracle['inputValueAliases']
    for r in c.get('effectiveAdditionalInputRefs',[]):
        check_ref(r)
    if c['id']=='G-list-13':
        unknown=c['unspecifiedIntermediate']
        assert unknown['selectedSubject'] is None and unknown['intermediateGraph'] is None
        check_ref(unknown['operationRef'])
        assert c['operationGraphBindings'][-1]['afterGraphRef']=='imported'
    assert c['sourceSetup'] == original['setup'] and c['sourceSteps'] == original['steps']
    assert len(c['operationGraphBindings']) == len(original['setup']) + len(original['steps'])
    op_count += len(c['operationGraphBindings'])
    for op in c['operationGraphBindings']:
        check_ref(op['inputRef'])
        if op['afterGraphRef'] is None:
            assert op['branchOrUnknownReason'] and op['oracleInputSha256'] is None
        else:
            assert op['oracleInputSha256'] == graphs[op['afterGraphRef']]['oracleInputSha256']
for c in [*oracle['productCases'], *oracle['extensions'], *oracle['supplementalLearningCases']]:
    check_ref(c['inputRef'])
    for p in c['phases']:
        assert p['graphRef'] in graphs
        assert p['oracleInputSha256'] == graphs[p['graphRef']]['oracleInputSha256']
        check_ref(p['inputRef'])
assert [c['id'] for c in oracle['extensions']] == [c['id'] for c in sources['tests/fixtures/quality/fr505-extension-cases.json']['cases']]
assert len(oracle['extensions']) == 22
for c in oracle['extensions']:
    assert c['reset']['inheritBaseRules'] is False and c['reset']['inheritPreviousResults'] is False
for cap, rows in oracle['e5Rounds'].items():
    assert cap in ['3', '4'] and [r['round'] for r in rows] == [1, 2, 3, 4]
    for j, row in enumerate(rows):
        for key, value in row.items():
            if key.endswith('GraphRef'):
                assert value in graphs
        assert row['beforeEventGraphRef'] == ('e5-initial' if j == 0 else rows[j-1]['committedGraphRef'])
        assert set(row['completedOrderIds']) | set(row['backlogOrderIds']) == set(row['orderIds'])
        assert not set(row['completedOrderIds']) & set(row['backlogOrderIds'])
assert set(oracle['importedSubcases']) == {'A-01', 'M-04', 'M-06', 'A-02'}
for phases in oracle['importedSubcases'].values():
    assert phases[0][1] == 'imported'
    assert all(gid in graphs for _, gid in phases)

# Exact repeated source relationships: consistency/read optimization only, not new expected values.
checks = sources['T09/content/learning/checks.json']['checks']
e5 = sources['T09/tests/fixtures/product-baselines/E.5.json']
relations = read(HERE / 'source-relations.json')
for row in relations['sameExpected48']:
    a = pointer(sources['T09/content/learning/checks.json'], row['checkPointer'])
    b = pointer(sources['T09/tests/fixtures/product-baselines/cases.json'], row['casePointer'])
    canonical_bytes = json.dumps(a, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    assert a == b and digest(canonical_bytes) == row['canonicalJsonSha256']
for row in relations['E5ExpandedRelationships']:
    left=pointer(sources['T09/content/learning/checks.json'],row['checkPointer'])
    src=sources['T09/tests/fixtures/product-baselines/'+row['rightSource']]
    right=[pointer(src,p) for p in row['rightPointers']] if 'rightPointers' in row else pointer(src,row['rightPointer'])
    assert left==right
    assert digest(json.dumps(left,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==row['canonicalValueSha256']
assert checks['G-list-01']['expected']['capacities'] == e5['expected']
for cap, replays in checks['G-list-01']['expected']['independentReplays'].items():
    assert len(replays) == 2 and all(r == e5['expected'][cap] for r in replays)
assert all(r == e5['expected']['3'] for r in checks['G-list-06']['expected']['independentReplays'])
assert checks['G-list-06']['expected']['resumeFromRound2']['newCommittedRounds'] == e5['expected']['3'][2:]
assert set(checks) == {c['id'] for c in oracle['productCases']} | {'ontology-model','transfer-repair','transfer-classify','learning-report'}

# Frozen product identities are read as bytes/hashes only; never imported or executed.
frozen = read(ROOT / 'docs/reviews/T05/profile-mechanism/candidate-4-inputs.json')['files']
assert len(frozen) == 20
for path, e in frozen.items():
    raw = (ROOT / path).read_bytes()
    assert len(raw) == e['bytes'] and digest(raw) == e['sha256'], path
print(json.dumps({'status':'passed-structural-only','productCases':50,'extensions':22,'learningChecksBound':54,'sourceSetupAndStepsBound':op_count,'tripleDictionaryEntries':len(triples),'graphSnapshots':len(graphs),'explicitPatternMatchRecords':len(matches),'rdfsWitnesses':len(witnesses),'approved17AndProfileSourcesHashed':True,'closed20PathsByteUnchanged':True,'engineImportsOrExecution':False,'matchingClosureOrComparisonComputed':False,'semanticCompletenessEstablishedBy':'manual argument plus independent agent review, not this checker'},ensure_ascii=False,indent=2))
