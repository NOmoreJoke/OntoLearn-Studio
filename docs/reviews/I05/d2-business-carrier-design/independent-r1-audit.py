"""Independent stdlib-only static grammar/relationship counterexamples.

No imports/exec of author checker or product. Reads seven design documents,
approved copied pure inputs, and independent identity; writes only own proof.
No runtime, source authorization, codec, RDF library or product validation.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT = Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
D = ROOT/'docs/iterations/I05/d2-business-carrier-design'
R = ROOT/'docs/reviews/I05/d2-business-carrier-design'
OLD = ROOT/'docs/reviews/I05/d2-consumer-design/fixed-inputs'
def read(p):
    return json.loads(p.read_bytes())
def digest(b):
    return hashlib.sha256(b).hexdigest()
g = read(D/'wire-grammar.json')
defs = g['definitions']
fieldmap = read(D/'field-map.json')
fwd = read(D/'forward-delta.json')
examples = read(D/'acceptance-rejects.json')
missing = read(D/'missing-materials.json')
dep = read(R/'fixed-d1/dependency-plan.json')
matrix = read(R/'fixed-d1/guard-scope-matrix.json')
index = read(R/'fixed-d1/forward-schema-change-index.json')
oldheader = read(OLD/'06-runtime-header.schema.json')
oldfieldmap = read(ROOT/'docs/iterations/I05/d2-consumer-design/field-origin-map.json')
oldacceptance = read(ROOT/'docs/iterations/I05/d2-consumer-design/acceptance-map.json')
checks = []
def check(label, condition, detail=None):
    checks.append({'name': label, 'pass': bool(condition), 'detail': detail})

def type_errors(expr, value, path):
    if 'ref' in expr:
        return definition_errors(expr['ref'], value, path)
    if 'nullable' in expr:
        return [] if value is None else type_errors(expr['nullable'], value, path)
    if 'array' in expr:
        if type(value) is not list:
            return [path+': expected array']
        return [e for i, item in enumerate(value) for e in type_errors(expr['array'], item, path+'/'+str(i))]
    if 'const' in expr:
        return [] if type(value) is type(expr['const']) and value == expr['const'] else [path+': const mismatch']
    if 'enum' in expr:
        return [] if any(type(value) is type(x) and value == x for x in expr['enum']) else [path+': enum mismatch']
    primitive = expr['type']
    expected = {'string': str, 'integer': int, 'boolean': bool, 'null': type(None)}[primitive]
    errors = []
    if type(value) is not expected:
        return [path+': expected exact '+primitive]
    if primitive == 'string':
        try:
            value.encode('utf-8')
        except UnicodeEncodeError:
            errors.append(path+': non-scalar Unicode')
        if 'pattern' in expr and re.fullmatch(expr['pattern'], value) is None:
            errors.append(path+': pattern mismatch')
        if 'maxLength' in expr and len(value) > expr['maxLength']:
            errors.append(path+': maxLength')
    if primitive == 'integer' and 'minimum' in expr and value < expr['minimum']:
        errors.append(path+': below minimum')
    return errors

def definition_errors(name, value, path=''):
    body = defs[name]
    if body['kind'] == 'primitive':
        errors = type_errors(body, value, path)
        if name == 'Base64' and not errors:
            try:
                raw = base64.b64decode(value, validate=True)
                if base64.b64encode(raw).decode('ascii') != value:
                    errors.append(path+': noncanonical base64')
            except ValueError:
                errors.append(path+': invalid base64')
        return errors
    if body['kind'] == 'record':
        if type(value) is not dict:
            return [path+': expected exact record']
        errors = [path+': exact keys mismatch'] if set(value) != set(body['fields']) else []
        for key, field in body['fields'].items():
            if key in value:
                errors.extend(type_errors(field['type'], value[key], path+'/'+key))
        return errors
    if body['kind'] == 'union':
        arms = [type_errors(arm, value, path) for arm in body['variants']]
        return [] if sum(not errors for errors in arms) == 1 else [path+': not exactly one union arm']
    return [path+': external-strict schema deliberately deferred']

def refs(expr):
    if 'ref' in expr:
        yield expr['ref']
    for key in ('nullable', 'array'):
        if key in expr:
            yield from refs(expr[key])

records = {name: body for name, body in defs.items() if body['kind'] == 'record'}
all_fields = {(name, field): body for name, record in records.items() for field, body in record['fields'].items()}
check('52 finite definitions / 39 exact records / 251 fields', (len(defs),len(records),len(all_fields)) == (52,39,251))
check('every record exact required field set without repeated required names', all(set(body['required']) == set(body['fields']) and len(body['required']) == len(body['fields']) and body['additionalProperties'] is False for body in records.values()))
references = [ref for body in records.values() for field in body['fields'].values() for ref in refs(field['type'])]
references += [ref for body in defs.values() if body['kind'] == 'union' for arm in body['variants'] for ref in refs(arm)]
check('all finite type references resolve', all(ref in defs for ref in references), sorted(set(references)))
mapped = {(row['definition'],row['field']): row for row in fieldmap['fields']}
check('251 field map exact membership with no duplicate', len(mapped) == len(fieldmap['fields']) == len(all_fields) and set(mapped) == set(all_fields))
mapping_errors=[]
for (name, field), body in all_fields.items():
    row=mapped[(name,field)]
    expected = {'type':body['type'],'owner':body['owner'],'meaning':body['meaning'],'relationshipRule':body['rule'],'required':True,'grammarPointer':'/definitions/'+name+'/fields/'+field}
    if any(row[key] != value for key,value in expected.items()):
        mapping_errors.append([name,field])
    check_rules = body['rule'].split('/')
    if any(key not in g['relationshipRules'] for key in check_rules):
        mapping_errors.append([name,field,'unknown relationship'])
check('all 251 mapping values and rule refs agree', not mapping_errors, mapping_errors)
fieldmap_other_columns = {key:[] for key in set().union(*(row.keys() for row in fieldmap['fields'])) if key not in ('definition','field','grammarPointer','type','owner','meaning','relationshipRule','required')}
for row in fieldmap['fields']:
    for key, values in fieldmap_other_columns.items():
        if row.get(key) not in values:
            values.append(row.get(key))
check('header 18 exact old keys and only explicit D1 changes', defs['PinnedHeader']['rootKeys'] == list(oldheader['properties']) and len(defs['PinnedHeader']['rootKeys'])==18 and fwd['D1LiteralChangesExact']==index)
check('26 package versions, six direct requirements, eight runtime values preserve fixed D1', fwd['exactProposedUnionPackageVersions']==dep['proposedUnionPackageVersions'] and fwd['sixDirectRequirements']==dep['preferredParentUnionDirectRequirements'] and fwd['semanticRuntimeEight']==dep['runtimeEight'])
check('all scope sets preserve fixed D1 matrix exact counts',fwd['distinctSets']==matrix['counts'])
rows_checked=[]
for group in ('nineConflicts','twentyOneOldOnly'):
    for row in fwd[group]:
        i=int(row['sourcePointer'].rsplit('/',1)[1])
        rows_checked.append({'group':group,'sourcePointer':row['sourcePointer'],'path':row['row']['path'],'matchesOriginal':row['row']==matrix['rows'][i], 'extraColumns':{k:v for k,v in row.items() if k not in ('row','sourcePointer')}})
check('9 conflict and 21 old-only full rows copied exactly', len(fwd['nineConflicts'])==9 and len(fwd['twentyOneOldOnly'])==21 and all(row['matchesOriginal'] for row in rows_checked), rows_checked)
check('futureApprovedPins all remain null',all(x is None for x in fwd['futureApprovedPins'].values()))
legacytext=(OLD/'24-contract.md').read_text()
familyrows=fieldmap['fullLegacyFamilies']
check('13 original full family cells exact fixed source lines', len(familyrows)==13 and all(legacytext.splitlines()[r['fixedSource']['line']-1]==r['fixedSource']['text'] for r in familyrows))
check('15 mandatory material map rows',len(fieldmap['legacyMandatoryMaterialDestinations'])==15)
check('all 15 mandatory original rows preserved and concrete destinations added', all({k:v for k,v in new.items() if k not in ('newConcreteDestination','guard')}==old for new,old in zip(fieldmap['legacyMandatoryMaterialDestinations'],oldacceptance['legacyMandatoryMaterialDestinations'],strict=True)))
check('all 13 original family rows complete and unchanged',fieldmap['fullLegacyFamilies']==oldacceptance['completeLegacyFamilyRequirements'])
def find_key(value,key):
    result=[]
    if type(value) is dict:
        if key in value:
            result.append(value[key])
        for child in value.values():
            result.extend(find_key(child,key))
    elif type(value) is list:
        for child in value:
            result.extend(find_key(child,key))
    return result
old_materials=find_key(oldfieldmap,'mandatoryMaterialDestinations')
old_families=find_key(oldfieldmap,'fullFamilyRequirements')

vectors=[]
for vector in examples['hashVectors']:
    canonical=json.dumps(vector['value'],ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
    preimage=('ontolearn/i05/'+vector['tag']+'\0').encode()+canonical
    vectors.append({'tag':vector['tag'],'canonicalMatch':base64.b64decode(vector['canonicalUtf8']['base64'])==canonical,'preimageMatch':base64.b64decode(vector['domainSeparatedPreimage']['base64'])==preimage,'hashMatch':digest(preimage)==vector['digest'],'preimageBytes':len(preimage),'digest':digest(preimage)})
check('all seven declared H vector original preimages independently reconstructed',len(vectors)==7 and all(v['canonicalMatch'] and v['preimageMatch'] and v['hashMatch'] for v in vectors),vectors)
custom_value={'z':[False,None,False], 'é':'\b\f\n\r\t/\\"', '😀':'原词法'}
custom_canonical=json.dumps(custom_value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
custom_hashes={tag:digest(('ontolearn/i05/'+tag+'\0').encode()+custom_canonical) for tag in ('return-tree/1','metadata-export/1')}
check('independent false/null/repetition Unicode vector is domain separated', len(set(custom_hashes.values()))==2,{'value':custom_value,'canonicalBase64':base64.b64encode(custom_canonical).decode(),'hashes':custom_hashes})
prefix=examples['terminalPrefixVector']
check('terminal prefix excludes terminal and differs full raw',base64.b64decode(prefix['rawPrefix']['base64'])+base64.b64decode(prefix['terminal']['base64'])==base64.b64decode(prefix['wholeRaw']['base64']) and prefix['priorPrefixSha256']==digest(base64.b64decode(prefix['rawPrefix']['base64'])) and prefix['priorPrefixSha256']!=prefix['wholeRaw']['sha256'])

# New counterexamples are independently constructed; no author sample execution.
empty_file={'root':'approved-witness','path':'synthetic-r1/stdout.bin','bytes':0,'sha256':digest(b'')}
pre_context_core={'runId':None,'mode':'source','selector':'full-v1','stdout':empty_file,'stderr':{**empty_file,'path':'synthetic-r1/stderr.bin'},'headerRange':None,'terminalRange':None}
core_errors=definition_errors('RunCoreBinding',pre_context_core,'/runCore')
check('counterexample confirms no null runId arm before context',core_errors==['/runCore/runId: expected exact string'],core_errors)
def unavailable():
    return {'state':'unavailable','value':None,'sourceRanges':[],'artifactIds':[],'reason':'not-observed'}
synthetic_pin={'repositoryId':'synthetic-external-approval-assumption','ref':'0'*40,'gitBlob':'0'*40,'path':'synthetic-r1/adopted-spec.md','bytes':0,'sha256':digest(b'')}
negotiation={'expectedStreamVersion':'i05-business-stream/2','protocolVersion':'3.0.0','profileFormat':'i05-semantic-build-protocol-profile/4','headerFormat':'i05-semantic-runtime-header/2','protocolPin':synthetic_pin,'profilePin':synthetic_pin,'businessAdoptionPin':synthetic_pin,'consumerPin':synthetic_pin,'buildReceipt':{**empty_file,'path':'synthetic-r1/build-receipt.json'},'approvedBuildRecord':synthetic_pin,'state':'matched'}
life={key:unavailable() for key in ('commandContext','targetBinding','cancelRequested','stopping','targetTerminated','readerJoined','referencesReleased','timing','physicalTicket')}
life.update({'dispatchState':'dispatched','argv':['--semantic-source-package-probe','full-v1'],'stdin':'dev-null','rawComplete':True})
failure_carrier={'format':'i05-business-carrier/1','attemptId':'independent-r1-dispatched-before-context','runId':None,'negotiation':negotiation,'observationState':'pre-header-rejected','stdout':pre_context_core['stdout'],'stderr':pre_context_core['stderr'],'header':{'state':'absent','range':None,'payload':None},'frames':[],'artifacts':[],'stages':[],'metadataBindings':[],'identityDomains':[],'actualExitCode':7,'signal':None,'collectionComplete':False,'fullSuiteCollectionComplete':False,'firstCollectionFailure':{'actor':'caller','phase':'header','reason':'raw-incomplete','stageId':None,'firstRange':None,'diagnosticArtifactId':None},'pendingMaterialIds':[],'lifecycle':life}
check('independent dispatched pre-context failure carrier has legal finite record shape',not definition_errors('Carrier',failure_carrier,'/carrier'))
failure_carrier_bytes=json.dumps(failure_carrier,ensure_ascii=False,separators=(',',':')).encode()
failure_binding={'format':'i05-business-validation-binding/1','carrier':{**empty_file,'path':'synthetic-r1/carrier.json','bytes':len(failure_carrier_bytes),'sha256':digest(failure_carrier_bytes)},'attemptId':failure_carrier['attemptId'],'buildReceipt':negotiation['buildReceipt'],'runCore':pre_context_core,'grammarPin':synthetic_pin,'state':'incomplete'}
binding_errors=definition_errors('BusinessValidationBinding',failure_binding,'/binding')
check('full mandatory companion binding rejects only unobserved runId',binding_errors==['/binding/runCore/runId: expected exact string'],binding_errors)
caller_witness_bytes=b'{"attemptId":"independent-r1-dispatched-before-context","exit":7,"readerJoined":true,"referencesReleased":true}'
caller_witness={'artifactId':'caller-exit','stageId':None,'pieceId':None,'representation':'captured-original-bytes','codecId':None,'file':{**empty_file,'path':'synthetic-r1/caller-exit.json','bytes':len(caller_witness_bytes),'sha256':digest(caller_witness_bytes)},'originRange':None,'fieldPointer':'/exit','parentArtifactIds':[]}
caller_errors=definition_errors('Artifact',caller_witness,'/callerWitness')
check('counterexample confirms no caller-origin artifact arm',len(caller_errors)==3,caller_errors)

# Detached independent guard relations, derived from explicit normative text.
guard_cases=[]
def guard(name,actual,expected):
    guard_cases.append({'name':name,'actual':actual,'expected':expected,'pass':actual==expected})
def metadata_gate(codec,layout,recipe,live,requested):
    return 'eligible-design-only' if all((codec,layout,recipe,live)) else ('reject' if requested else 'pending')
guard('opaque bytes only remain pending', metadata_gate(False,False,False,False,False),'pending')
guard('opaque cannot claim compatible', metadata_gate(False,False,False,False,True),'reject')
guard('equal issue strings without live verifier do not authorize',metadata_gate(True,True,True,False,True),'reject')
def flow(stages,planned,pieces):
    return all(stage in stages and all(piece in pieces for piece in required) for stage,required in planned.items())
guard('earlier success pieces retained after rejection',flow({'prepare':'returned-complete','restore':'rejected'},{'prepare':['payload','rows'],'restore':['safe-error']},['payload','rows','safe-error']),True)
guard('later rejection cannot erase prior rows tail',flow({'prepare':'returned-complete','restore':'rejected'},{'prepare':['payload','rows'],'restore':['safe-error']},['payload','safe-error']),False)
def domain_match(graphs,slots,witness,bijection):
    return witness and all(graphs[s['artifact']]==s['graph'] for s in slots) and len(set(bijection.values()))==len(bijection)
guard('independent parse same label cannot merge ownership',domain_match({'query-result':'g2'},[{'artifact':'query-result','graph':'g1'}],True,{'a':'x'}),False)
guard('all slots same graph accept one bijection only',domain_match({'query-result':'g1'},[{'artifact':'query-result','graph':'g1'}],True,{'a':'x','b':'y'}),True)
guard('noninjective BNode map rejects',domain_match({'query-result':'g1'},[{'artifact':'query-result','graph':'g1'}],True,{'a':'x','b':'x'}),False)
guard('B1 never full417',('b1-semantic-1x-v1'=='full-v1' and 1==417),False)
check('independent detached cross-structure guard cases',all(case['pass'] for case in guard_cases),guard_cases)
counterexamples=[
 {'id':'R1-F01','severity':'P2','scenario':'Dispatch occurred; child exited before emitting context; stdout/stderr both zero bytes; caller observed real process exit. Child runId never existed/was observed.', 'input':pre_context_core,'fullFiniteShapeCarrier':failure_carrier,'fullBindingAttempt':failure_binding,'shapeErrors':core_errors,'fullBindingErrors':binding_errors,'assumptions':'Synthetic external approval pins are shape placeholders for this detached design counterexample only. No actual approval/runtime claimed. Lifecycle unobserved fields remain null; caller witness path is separately F02.', 'alternatives':[{'encoding':'runCore.runId=null','result':'RunCoreBinding rejects Id shape'},{'encoding':'runCore=null','result':'Contradicts BINDING dispatched core requirement; loses raw binding'},{'encoding':'runCore.runId=invented string','result':'Shape only; no carrier/context/receipt observed child identity; violates no expected fill and same run requirement'}],'requiredFix':'Make dispatched failure run identity availability explicit; nullable runId with exact same availability guard, or a separate pre-context failure core union; include complete binding example.'},
 {'id':'R1-F02','severity':'P2','scenario':'Caller-only owned-process exit/reader-join/reference-release witness exists externally after child stdout/stderr end; child emitted no stage frame. Caller facts must not be manufactured as child observations.', 'externalWitnessAttempt':caller_witness,'externalWitnessBytesBase64':base64.b64encode(caller_witness_bytes).decode(),'shapeErrors':caller_errors,'alternatives':[{'encoding':'observed EvidenceValue without sourceRanges/artifactIds','result':'Violates EVIDENCE actual raw/artifact provenance rule'},{'encoding':'invent stageId/pieceId/originRange','result':'Violates Artifact actual owner stage/piece/whole source stage frame requirement'},{'encoding':'mark actual observed caller event unavailable','result':'Drops actual evidence / falsely states availability'}],'requiredFix':'Add an explicit caller-owned witness origin/file branch tied to attempt/lifecycle and external source pin; preserve child-piece branch unchanged. Require resolvable artifact IDs and no invented child ranges.'}
]
result={'scope':'limited pure-design independent static arithmetic/grammar/relationship audit; no runtime/product/model execution','identityEvidence':'independent-r1-identity.json','checks':checks,'allIndependentChecksPassed':all(c['pass'] for c in checks),'fieldMapAdditionalColumnValues':fieldmap_other_columns,'fullSevenInputParse': [{'path':str(p.relative_to(ROOT)),'bytes':len(p.read_bytes()),'sha256':digest(p.read_bytes())} for p in sorted(D.iterdir()) if p.is_file()], 'oldFieldMapTopKeys':list(oldfieldmap),'oldMaterialMatches':old_materials,'oldFamilyMatches':old_families,'counterexamples':counterexamples,'findingCount':2,'verdict':'Fail limited pure-design; two unrepresentable mandatory failure/evidence paths','deferred':['complete v3 adopted schema/header engine validation','old metadata codec/layout/recipe/live handle verification','RDF semantic comparison and complete 417 independent oracle','all source/runtime/authority/native/caller permissions and release gates']}
(R/'independent-proof-r1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verdict':result['verdict'],'checks':len(checks),'allIndependentChecksPassed':result['allIndependentChecksPassed'],'failedChecks':[c for c in checks if not c['pass']],'fieldMapAdditionalColumnValues':fieldmap_other_columns,'oldFieldMapTopKeys':list(oldfieldmap),'counterexamples':counterexamples},ensure_ascii=False,indent=2))
