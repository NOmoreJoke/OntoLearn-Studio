import base64
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
REVIEW = ROOT / 'docs/reviews/I05/d2-canonical-interface-design'
DESIGN = ROOT / 'docs/iterations/I05/d2-canonical-interface-design'
BASE = '0841ffbe7a4599fbea96f4ff998808f3f4e00972'
CAND = 'eb5d4017e7dba86b568e879e34531e49d1b79920'
PROCESS = '6b94c152a8fca0f0e26d377b0e4d79ff4d64b8b5'
CONTROL = pathlib.Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/I05-canonical-interface-inventory-D2-limited-reception-20261022.json')
checks = []
commands = []

def sha(b):
    return hashlib.sha256(b).hexdigest()

def check(label, passed, detail=None):
    checks.append({'id': label, 'pass': bool(passed), 'detail': detail})

def read(p):
    return json.loads(p.read_text())

def git(args, cwd=ROOT):
    argv = ['git'] + args
    c = subprocess.run(argv, cwd=cwd, capture_output=True)
    def stream(b):
        return {'encoding': 'lossless-utf8-json', 'text': b.decode('utf-8'), 'bytes': len(b), 'sha256': sha(b)}
    if args[0] == 'show':
        stdout = {'encoding': 'immutable-git-blob-reference', 'gitObjectSpec': args[1], 'bytes': len(c.stdout), 'sha256': sha(c.stdout), 'notExecutedOrInterpreted': True}
    else:
        stdout = stream(c.stdout)
    commands.append({'argv': argv, 'cwd': str(cwd), 'exit': c.returncode, 'stdout': stdout, 'stderr': stream(c.stderr)})
    if c.returncode != 0:
        raise RuntimeError('git command failed with exit ' + str(c.returncode))
    return c.stdout

control = read(CONTROL)
manifest = read(REVIEW / 'canonical-candidate-manifest.json')
receipt = read(REVIEW / 'canonical-candidate-receipt.json')
identity = read(REVIEW / 'input-identity.json')
new_prefixes = ['docs/iterations/I05/d2-canonical-interface-design/', 'docs/reviews/I05/d2-canonical-interface-design/']
protected_prefixes = ['docs/iterations/I05/d2-consumer-design/', 'docs/reviews/I05/d2-consumer-design/', 'docs/iterations/I05/d2-business-carrier-design/', 'docs/reviews/I05/d2-business-carrier-design/']
protected = identity['protectedInventory']
base_names = git(['ls-tree', '-r', '--name-only', BASE, '--'] + [x.rstrip('/') for x in protected_prefixes]).decode().splitlines()
check('protected.exact176.membership', len(protected) == 176 and set(base_names) == {x['path'] for x in protected})
check('protected.no.duplicate.paths', len({x['path'] for x in protected}) == len(protected))
for x in protected:
    b = (ROOT / x['path']).read_bytes()
    check('protected:' + x['path'], len(b) == x['bytes'] and sha(b) == x['sha256'] and b == git(['show', BASE + ':' + x['path']]))

manifest_path = str((REVIEW / 'canonical-candidate-manifest.json').relative_to(ROOT))
receipt_path = str((REVIEW / 'canonical-candidate-receipt.json').relative_to(ROOT))
new_entries = manifest['files'] + [
    {'path': manifest_path, 'bytes': 6564, 'sha256': '172984bec405dcba94e1a5d3d0ea17e88b0c0df2902fce161bc5d0185ffffc4b'},
    {'path': receipt_path, 'bytes': 51056, 'sha256': 'de490facefe9db1dd613813d76c8ecdfce4ea5bf7903b4c13fa0d7462411ab04'}]
process_names = git(['ls-tree', '-r', '--name-only', PROCESS, '--'] + [x.rstrip('/') for x in new_prefixes]).decode().splitlines()
candidate_names = git(['ls-tree', '-r', '--name-only', CAND, '--'] + [x.rstrip('/') for x in new_prefixes]).decode().splitlines()
check('candidate.payload27.manifest28.process29.exact.membership', len(manifest['files']) == 27 and len(new_entries) == 29 and set(process_names) == {x['path'] for x in new_entries} and set(candidate_names) == set(process_names) - {receipt_path})
check('candidate.only.two.new.prefixes', all(any(x['path'].startswith(p) for p in new_prefixes) for x in new_entries))
check('candidate.no.protected.overlap', not ({x['path'] for x in new_entries} & {x['path'] for x in protected}))
for x in new_entries:
    b = (ROOT / x['path']).read_bytes()
    ok = len(b) == x['bytes'] and sha(b) == x['sha256'] and b == git(['show', PROCESS + ':' + x['path']])
    if x['path'] != receipt_path:
        ok = ok and b == git(['show', CAND + ':' + x['path']])
    check('candidate:' + x['path'], ok)
check('receipt.manifest.identity', receipt['manifest']['bytes'] == 6564 and receipt['manifest']['sha256'] == sha((REVIEW / 'canonical-candidate-manifest.json').read_bytes()))
check('receipt.candidate.identity', receipt['candidateRef'] == CAND and len(receipt['candidateInventory']) == 28)
check('control.exact11', len(control['allowlist']) == 11)
check('snapshot.control.equals.author.reception', control == read(REVIEW / 'reception-control.json') or all(x in read(REVIEW / 'reception-control.json')['allowlist'] for x in control['allowlist']))
for x in control['allowlist']:
    snap = REVIEW / 'fixed-inputs' / pathlib.Path(x['path']).name
    b = snap.read_bytes()
    fixed = git(['show', x['ref'] + ':' + x['path']], pathlib.Path(control['sourceTree']))
    current = (pathlib.Path(control['sourceTree']) / x['path']).read_bytes()
    check('input:' + x['path'], len(b) == x['bytes'] and sha(b) == x['sha256'] and b == fixed and b == current)

facts = {p.name: read(p) for p in (REVIEW / 'fixed-inputs').iterdir() if p.suffix == '.json'}
bridge = read(DESIGN / 'field-codec-bridge.json')
dirs = bridge['directories']
rows = bridge['fieldRows']
dm = {d['id']: d for d in dirs}
check('bridge.counts', len(dirs) == 52 and len(rows) == 263 and bridge['fieldRowCount'] == 263)
check('bridge.unique.ids', len(dm) == len(dirs) and len({r['id'] for r in rows}) == len(rows))
for d in dirs:
    subset = [r for r in rows if r['layout'] == d['id']]
    check('field-order:' + d['id'], [r['field'] for r in subset] == d['orderedFields'] and len(set(d['orderedFields'])) == len(d['orderedFields']))
    check('not-adopted:' + d['id'], d['newGrammarAdopted'] is False)
for r in rows:
    check('field-retention:' + r['id'], r['id'] == r['layout'] + '/' + r['field'] and r['directoryKnown'] is True and r['actualFieldObserved'] is False and r['transitiveOwnerContractStillRequired'] is True and r['consumerDestination']['directoryId'] == r['layout'] and r['consumerDestination']['fieldEntryName'] == r['field'] and r['basis']['sourceFollowingAuthorized'] is False and r['basis']['ref'] == control['refs']['final'] and r['pendingRequests'])

def pointer(data, ptr):
    for part in ptr.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        data = data[int(part)] if isinstance(data, list) else data[part]
    return data

for j, x in enumerate(facts['api-layouts.json']['layouts']):
    d = dm['api:' + x['id']]
    check('api.directory:' + x['id'], d['orderedFields'] == x['orderedKeys'] and d['existingSourceMetadata'] == x['source'] and d['basis']['factPointer'] == '/layouts/' + str(j))
for j, x in enumerate(facts['api-layouts.json']['classAnnotationIndex']):
    d = dm['decl:' + x['source']['function']]
    check('annotation.directory:' + d['id'], d['orderedFields'] == [v['name'] for v in x['annotatedFields']] and d['existingSourceMetadata'] == x['source'])
for j, x in enumerate(facts['additional-return-layouts.json']['records']):
    d = dm['return:' + x['class']]
    fields = x['staticallyExpandedInheritedFields']
    check('return.directory:' + x['class'], d['orderedFields'] == [v['name'] for v in fields] and d['localFields'] == [v['name'] for v in x['fields']] and d['bases'] == x['bases'])
for r in rows:
    basis = r['basis']
    if basis['factFile'] == 'api-layouts.json' and '/annotatedFields/' in basis['factPointer']:
        x = pointer(facts[basis['factFile']], basis['factPointer'])
        default = 'declared default exists; value not supplied in this inventory' if x['hasDefault'] else None
        check('annotation.field:' + r['id'], x['name'] == r['field'] and x['annotation'] == r['existingAnnotation'] and r['defaultExpressionOnly'] == default)
    elif basis['factFile'] == 'additional-return-layouts.json':
        x = pointer(facts[basis['factFile']], basis['factPointer'])
        check('return.field:' + r['id'], x['name'] == r['field'] and x['typeAnnotation'] == r['existingAnnotation'] and x['defaultSyntax'] == r['defaultExpressionOnly'])
    elif basis['factPointer'].startswith('/'):
        x = pointer(facts[basis['factFile']], basis['factPointer'])
        check('source.pointer:' + r['id'], isinstance(x, str) or r['field'] in x)
    else:
        ln = int(basis['factPointer'].removeprefix('line:'))
        text = (REVIEW / 'fixed-inputs' / basis['factFile']).read_text().splitlines()[ln - 1]
        check('prose.pointer:' + r['id'], r['field'] in text)
for key, n in [('api:legacy-source',4),('api:legacy-provenance',13),('api:legacy-reason',5),('return:ProfileComputation',14),('return:ProfileExplanationComputation',15),('return:RootRef',5),('return:DirectStepsReceipt',11)]:
    check('critical.count:' + key, len(dm[key]['orderedFields']) == n)
check('native_kind.preserved', dm['return:ReadonlySequence']['orderedFields'] == ['native_kind','items'])
root_rows = [r for r in rows if r['layout'] == 'return:RootRef']
check('rootRef.kind.no.enum', root_rows[0]['existingAnnotation'] == 'str' and all('| None' in r['existingAnnotation'] for r in root_rows[1:]))
check('source.branch.keys', bridge['selectedFactSources']['cases'] == [{'kind':'asserted','keys':['kind']},{'kind':'rdfs','keys':['kind','basis']},{'kind':'rule','keys':['kind','rule','inputs','basis']}])
check('unclosed.pending', next(r for r in rows if r['id'] == 'helper:ProfileValue/value')['existingAnnotation'] == 'object' and next(r for r in rows if r['id'] == 'return:ProfileComputation/native_result')['existingAnnotation'] == 'dict' and not bridge['full417Closed'] and not bridge['wholeM02M05Closed'])

digest = read(DESIGN / 'digest-bridge.json')
check('digest.exact16.recipe.objects', len(facts['digest-recipes.json']['recipes']) == 16 and [x['existingRecipe'] for x in digest['bridges'][:16]] == facts['digest-recipes.json']['recipes'])
check('digest.supplemental3', len(digest['bridges']) == 19 and [x['id'] for x in digest['bridges'][16:]] == ['production-catalog','canonical-string-narrow','implementation-expression'])
check('scope.allow_nan.not-explicit', digest['scopeJsonOptionsFact']['allow_nanExplicitlySpecified'] is False)
check('profile.allow_nan.false', digest['profileJsonOptionsFact']['allow_nan'] is False)
check('rows.characters', digest['rowsRecipeFact']['unit'] == 'Python characters' and digest['rowsRecipeFact']['chunkLength'] == 8192 and digest['rowsRecipeFact']['allFinalSlicesRetained'])
check('lock.not.evaluated', digest['bridges'][-1]['actualDependencyLockHash'] is None and not digest['actualOriginalPreimagesVerified'])

grammar = read(DESIGN / 'proposed-export-grammar.json')
defs = grammar['definitions']
check('grammar.29.new.only', len(defs) == 29 and all(x['status'] == 'NEW-PROPOSED-NOT-ADOPTED' for x in defs.values()))
refs = []
def walk(v):
    if isinstance(v, dict):
        if set(v) == {'ref'}:
            refs.append(v['ref'])
        for x in v.values():
            walk(x)
    elif isinstance(v, list):
        for x in v:
            walk(x)
walk(defs)
check('grammar.refs.resolve', set(refs) <= set(defs))
for name,d in defs.items():
    if d['kind'] == 'exact-record':
        check('grammar.exact-record:' + name, d['additionalProperties'] is False and set(d['required']) == set(d['fields']) and len(d['required']) == len(set(d['required'])))
check('grammar.gates.false', all(x is False for x in grammar['currentGateState'].values()))
requests = read(DESIGN / 'authority-and-requests.json')
check('requests.nine.pending', [r['id'] for r in requests['requests']] == ['Q0' + str(j) for j in range(1,10)] and all(r['actualReceivedPin'] is None and r['sourceFollowingAuthorized'] is False for r in requests['requests']))
check('requests.roles.only', requests['roleLinkPolicyReception']['bodyRead'] is False and requests['roleLinkPolicyReception']['actualImplementationAdoption'] is False)
check('requests.gates.false', all(x is False for x in requests['gateState'].values()))
acceptance = read(DESIGN / 'acceptance-map.json')
check('acceptance.21.declarative.only', len(acceptance['negativeDesignCases']) == 21 and all(x['evidenceClass'] == 'declarative future acceptance design; not actual product test' for x in acceptance['negativeDesignCases']))
examples = read(DESIGN / 'hand-examples.json')
x = examples['rowsCharacterUnit']
check('example.rows.literal', len(x['inputText']) == 8194 and x['rows'] == [[x['inputText'][0:8192]], [x['inputText'][8192:]]] and len(x['rows'][0][0].encode()) == 16385 and [len(r[0]) for r in x['rows']] == [8192,2])
x = examples['originalDigestAndProposedRelation']
old = base64.b64decode(x['oldLiteralPreimageBase64'],validate=True)
core = json.dumps(x['relationCore'],ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
prefix = b'ontolearn/i05/canonical-interface-bridge/1-proposal'
relation = prefix + bytes([0]) + core
check('example.old.raw.sha', len(old) == 2 and sha(old) == x['oldLiteralRawSha256'])
check('example.relation.single.NUL.hash', relation == base64.b64decode(x['newRelationPreimageBase64'],validate=True) and relation.count(bytes([0])) == 1 and sha(relation) == x['newRelationSha256'] and x['oldDigestNeverReplaced'])
check('example.relation.core.exact.keys', list(x['relationCore']) == digest['newRelationHash']['exactCoreKeys'] and set(x['relationCore']) == set(defs['RelationCore']['required']))
check('example.envelope.keys', set(examples['completePendingDtoExample']) == set(defs['DtoEnvelope']['required']))
check('example.envelope.pending.false', all(examples['completePendingDtoExample'][k] is False for k in ['wholeValueExportComplete','semanticCompatible','authorityVerified']))

stream_errors = []
for filename,key in [('commands-bootstrap.json','commands'),('canonical-candidate-receipt.json','commands')]:
    doc = read(REVIEW / filename)
    for j,c in enumerate(doc[key]):
        for k in ['argv','cwd','exit','stdout','stderr']:
            if k not in c:
                stream_errors.append([filename,j,'missing.'+k])
        for name in ['stdout','stderr']:
            stream = c[name]
            if 'text' in stream:
                b = stream['text'].encode()
                if len(b) != stream['bytes'] or sha(b) != stream['sha256']:
                    stream_errors.append([filename,j,name])
check('author.command.stream.integrity', not stream_errors, stream_errors)
check('author.commands.count190.and43', len(read(REVIEW/'commands-bootstrap.json')['commands']) == 190 and len(receipt['commands']) == 43)
check('author.first.failure.not.swallowed', receipt['actualExits']['firstAuthoringParseFailure'] == 1 and read(REVIEW/'first-authoring-failure.json')['actualOuterExit'] == 1 and receipt['actualExits']['staticCheck01MinimalOnly'] == 0)
check('author.receipt.no.self.or.future.hash', 'after frozen receipt' in receipt['processRef'] and 'without mutating its bytes' in receipt['postReceiptCommands'])
check('author.actual.gates.false', receipt['actualM02M05OrAuthorityRuntimeClosed'] is False)

observations = [
    {'id':'IR1-P2-01a','source':'api-layouts.json#/layouts/1/selectedFacts','knownWrapperFields':['triple','sources'],'explicitDirectoryFound':any(d['id'].startswith('api:legacy-provenance/selectedFacts') for d in dirs),'explicitWrapperRowsFound':[r['id'] for r in rows if r['layout'].startswith('api:legacy-provenance/selectedFacts')],'originalRawPreservationRulePresent':True,'scope':'known per-item wrapper fields not explicitly bridged; source branch directories alone do not include wrapper'},
    {'id':'IR1-P2-01b','source':'api-layouts.json#/layouts/11/optionalBranch','knownOptionalBranch':'mutation','explicitOuterFieldFound':'mutation' in dm['api:probe-production-observation']['orderedFields'],'explicitFieldOrBranchMappingFound':any(r['field']=='mutation' for r in rows),'originalRawPreservationRulePresent':True,'scope':'branch inner directory remains unprovided; known branch name can be retained without guessing internals'}]
print(json.dumps({'format':'i05-d2-canonical-independent-r1-proof/1','scope':'identity plus authorized fixed JSON/markdown field/recipe/grammar/literal static checks; no product/codec/runtime/schema engine','candidateRef':CAND,'processRef':PROCESS,'revisionBase':BASE,'checkCount':len(checks),'failed':[x for x in checks if not x['pass']],'checks':checks,'designFindings':observations,'commands':commands,'limits':['original source pins in received docs remain provenance only and were not followed','new R2 prefixes and newly received type-directory not read','old176 only byte-identity checked; no old checker/model executed','original 383 inherited static checks and old1241 not rerun','declarative21 not run as product tests','later15 post-receipt commands available only root transcript f7b997, not reconstructed here']},ensure_ascii=False,indent=2))
sys.exit(0 if all(x['pass'] for x in checks) else 1)
