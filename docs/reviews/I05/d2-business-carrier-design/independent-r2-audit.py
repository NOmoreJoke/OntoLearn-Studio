"""Independent R2 static finite grammar/schema/provenance audit.
Only stdlib; never loads author checker as code. Writes one exclusive proof.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
ROOT=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design')
R=ROOT/'docs/reviews/I05/d2-business-carrier-design';D=ROOT/'docs/iterations/I05/d2-business-carrier-design'
def read(p):return json.loads(p.read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def C(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
g=read(D/'wire-grammar-r2.json');old=read(D/'wire-grammar.json');defs=g['definitions']
projection=read(D/'receipt-projection-r2.json');fm=read(D/'field-map-r2.json');fwd=read(D/'forward-delta-r2.json');missing=read(D/'missing-materials-r2.json');a=read(D/'acceptance-r2.json')
schema=read(R/'fixed-v3-r2/runtime-validation-receipt.schema.json');responsibility=read(R/'fixed-v3-r2/field-responsibility.json')
checks=[]
def check(name,ok,details=None):checks.append({'name':name,'pass':bool(ok),'details':details})
# Exact primitive type semantics; JSON booleans cannot satisfy integer fields.
def typeok(t,v):return {'object':type(v) is dict,'array':type(v) is list,'string':type(v) is str,'integer':type(v) is int,'number':type(v) in (int,float),'boolean':type(v) is bool,'null':v is None}[t]
seen_keywords=set()
def jschema(s,v,path=''):
 seen_keywords.update(s)
 if 'anyOf' in s:
  if not any(not jschema(arm,v,path) for arm in s['anyOf']):return [path+': anyOf']
 if 'type' in s:
  ts=s['type'] if type(s['type']) is list else [s['type']]
  if not any(typeok(t,v) for t in ts):return [path+': type']
 if 'const' in s and (type(v) is not type(s['const']) or v!=s['const']):return [path+': const']
 if 'enum' in s and not any(type(v) is type(x) and v==x for x in s['enum']):return [path+': enum']
 e=[]
 if type(v) is dict:
  e += [path+'/'+k+': missing' for k in s.get('required',[]) if k not in v]
  props=s.get('properties',{})
  if s.get('additionalProperties') is False:e += [path+'/'+k+': extra' for k in v if k not in props]
  for k,body in props.items():
   if k in v:e += jschema(body,v[k],path+'/'+k)
 if type(v) is list:
  if len(v)<s.get('minItems',0) or len(v)>s.get('maxItems',len(v)):e.append(path+': items bound')
  for i,item in enumerate(v):
   if 'items' in s:e+=jschema(s['items'],item,path+'/'+str(i))
 if type(v) is str:
  if len(v)<s.get('minLength',0) or len(v)>s.get('maxLength',len(v)):e.append(path+': string bound')
  if 'pattern' in s and re.search(s['pattern'],v) is None:e.append(path+': pattern')
 if type(v) in (int,float) and v<s.get('minimum',v):e.append(path+': minimum')
 return e

def finite(expr,v,path=''):
 if 'ref' in expr:
  body=defs[expr['ref']];kind=body['kind']
  if kind=='record':
   if type(v) is not dict:return [path+': record']
   e=[] if set(v)==set(body['fields']) else [path+': exact keys']
   for k,f in body['fields'].items():
    if k in v:e+=finite(f['type'],v[k],path+'/'+k)
   return e
  if kind=='union':return [] if sum(not finite(arm,v,path) for arm in body['variants'])==1 else [path+': union']
  if kind=='external-strict':return jschema(read(R/'fixed-v3-r2/runtime-header.schema.json'),v,path)
  return jschema(body,v,path)
 if 'nullable' in expr:return [] if v is None else finite(expr['nullable'],v,path)
 if 'array' in expr:
  return [path+': array'] if type(v) is not list else [e for i,x in enumerate(v) for e in finite(expr['array'],x,path+'/'+str(i))]
 return jschema(expr,v,path)

changed=[k for k,v in old['definitions'].items() if defs.get(k)!=v];newdefs=[k for k in defs if k not in old['definitions']]
check('delta definition surface matches six changed and seven new',changed==['PinnedHeader','Negotiation','Carrier','RunCoreBinding','BusinessValidationBinding','ProcessLifecycle'] and len(newdefs)==7,{'changed':changed,'added':newdefs,'unchanged':len(defs)-len(changed)-len(newdefs)})
check('child Artifact/frames/old hash preimages unchanged',all(defs[k]==old['definitions'][k] for k in ('Artifact','ContextFrame','StageFrame','ObservationFrame','TerminalFrame','EvidenceValue')) and g['hashPreimages']==old['hashPreimages'])
fields={(name,k):v for name,body in defs.items() if body['kind']=='record' for k,v in body['fields'].items()}
rows={(r['definition'],r['field']):r for r in fm['fields']}
check('full R2 field-map exact keys/types/meaning/owner/rules',len(rows)==len(fm['fields'])==len(fields) and set(rows)==set(fields) and all(rows[key]['type']==f['type'] and rows[key]['meaning']==f['meaning'] and rows[key]['owner']==f['owner'] and rows[key]['relationshipRule']==f['rule'] for key,f in fields.items()),{'definitions':len(defs),'fields':len(fields)})
check('all new exact required sets and references',all(set(b['required'])==set(b['fields']) and b['additionalProperties'] is False for b in defs.values() if b['kind']=='record'))
rs=schema['properties']['runs']['items'];pointers=rs['properties']
check('all31 required projections exact received shape and pointer',len(projection['rows'])==31 and {r['field'] for r in projection['rows']}==set(rs['required']) and all(r['receivedShape']==pointers[r['field']] and r['schemaPointer']=='#/properties/runs/items/properties/'+r['field'] and r['required'] is True for r in projection['rows']))
check('receipt entry producer is caller at exact propertyIndex755',responsibility['propertyIndex'][755]['producer']=='caller',responsibility['propertyIndex'][755])
checksamples=[]
for x in a['completeSyntheticFailureExamples']:
 registry={entry['file']['path']:base64.b64decode(entry['base64'],validate=True) for entry in x['originalFileRegistry']}
 errors=finite({'ref':'Carrier'},x['carrier'],'/carrier')+finite({'ref':'BusinessValidationBinding'},x['binding'],'/binding')+jschema(schema,x['runtimeReceipt'],'/runtimeReceipt')
 files_ok=all(len(registry[e['file']['path']])==e['file']['bytes'] and sha(registry[e['file']['path']])==e['file']['sha256'] for e in x['originalFileRegistry'])
 checksamples.append({'id':x['id'],'errors':errors,'allFileBytesAndSha':files_ok,'registryPaths':list(registry),'state':x['carrier']['observationState'],'contextAvailable':x['carrier']['identityAvailability']=='observed-context'})
check('five full author records satisfy independent finite grammar plus exact received schema keywords',all(not x['errors'] and x['allFileBytesAndSha'] for x in checksamples),checksamples)
# Independent construction: no author predicate is called or imported.
empty={'root':'approved-witness','path':'independent-r2/stdout.bin','bytes':0,'sha256':sha(b'')}
err={'actor':'caller','phase':'header','reason':'raw-incomplete','stageId':None,'firstRange':None,'diagnosticArtifactId':None}
pre={'kind':'pre-context-failure','attemptId':'scheduled-before-child','childRunId':None,'mode':'source','selector':'full-v1','stdout':empty,'stderr':{**empty,'path':'independent-r2/stderr.bin'},'headerRange':None,'rejectedTerminalRange':None,'actualExitCode':7,'signal':None,'firstCollectionFailure':err,'lifecycleWitnessIds':[]}
nochild={'kind':'not-dispatched','attemptId':pre['attemptId'],'childRunId':None,'dispatchState':'not-started'}
bound={'kind':'child-context','attemptId':pre['attemptId'],'core':{'runId':'observed-child-context','mode':'source','selector':'full-v1','stdout':empty,'stderr':pre['stderr'],'headerRange':None,'terminalRange':None}}
check('independent all three AttemptCore shapes retain distinct identities',all(not finite({'ref':'AttemptCore'},v) for v in (nochild,pre,bound)),[nochild,pre,bound])
# Independent 31-key actual failure projection, intentionally unrelated attempt id.
row={k:None for k in rs['required']}
row.update({'runId':pre['attemptId'],'mode':'source','selector':'full-v1','argv':['--semantic-source-package-probe','full-v1'],'stdout':empty,'stderr':pre['stderr'],'actualExitCode':7,'signal':None,'collectionComplete':False,'fullSuiteCollectionComplete':False,'externalReceiptStatus':'external-unverified','moduleLoaders':[],'functionCodes':[],'observationState':'incomplete','headerState':'absent','terminalState':'absent','observationIds':[],'observedPaths':[],'failure':{'actor':'caller','phase':'stream','code':'RUNTIME_EVIDENCE_INCOMPLETE','reason':'stream-incomplete','firstEvidence':empty},'observationOutcomes':[]})
check('independent 31-key pre-context failure receipt row fits exact received schema',not jschema(rs,row,'/run'),{'row':row,'errors':jschema(rs,row,'/run')})
negatives=[]
for field in rs['required']:
 mutated=copy.deepcopy(row);del mutated[field];negatives.append({'name':'missing-receipt-'+field,'reject':bool(jschema(rs,mutated))})
nullreceipt=copy.deepcopy(row);nullreceipt['runId']=None
negatives.append({'name':'null receipt identity still rejected','reject':bool(jschema(rs,nullreceipt))})
extra=copy.deepcopy(row);extra['childRunId']=None
negatives.append({'name':'child identity cannot widen strict receipt keys','reject':bool(jschema(rs,extra))})

def identity_errors(dispatch,contexts,child_id,availability,core,receipt_id,attempt_id,registry_ids):
 e=[]
 if registry_ids.count(attempt_id)!=1 or receipt_id!=attempt_id:e.append('actual caller registry identity')
 if not dispatch:
  if contexts or child_id is not None or availability!='not-dispatched' or core['kind']!='not-dispatched':e.append('no dispatch branch')
 elif not contexts:
  if child_id is not None or availability!='unavailable-before-context' or core['kind']!='pre-context-failure':e.append('pre-context branch')
  if core.get('stdout') is None or core.get('stderr') is None:e.append('zero-byte files mandatory')
 elif len(contexts)!=1 or child_id!=contexts[0] or availability!='observed-context' or core['kind']!='child-context' or core['core']['runId']!=child_id:e.append('accepted child context branch')
 return e
cases=[]
for name,dispatch,contexts,child,avail,core in [('not-dispatched',False,[],None,'not-dispatched',nochild),('pre-context-exit7',True,[],None,'unavailable-before-context',pre),('post-context-incomplete',True,['observed-child-context'],'observed-child-context','observed-context',bound),('post-context-collected-identity-only',True,['observed-child-context'],'observed-child-context','observed-context',bound)]:
 cases.append({'name':name,'errors':identity_errors(dispatch,contexts,child,avail,core,pre['attemptId'],pre['attemptId'],[pre['attemptId']]),'scope':'identity branch only; collected business/source completeness is inherited and not asserted'})
for name,args in [('invented-child-before-context',(True,[],'invented','unavailable-before-context',pre)),('context-erased',(True,['observed-child-context'],None,'unavailable-before-context',pre)),('context-different',(True,['observed-child-context'],'other','observed-context',bound)),('duplicate-context',(True,['observed-child-context']*2,'observed-child-context','observed-context',bound))]:
 negatives.append({'name':name,'reject':bool(identity_errors(*args,pre['attemptId'],pre['attemptId'],[pre['attemptId']]))})
negatives.append({'name':'receipt label invented only for schema','reject':bool(identity_errors(True,[],None,'unavailable-before-context',pre,'invented-entry',pre['attemptId'],[pre['attemptId']]))})
check('independent identity positives preserve pre/post-context and caller separation',all(not c['errors'] for c in cases),cases)
# Independent caller witness: true/false/null remain full Tree values; no child range.
pin={'ref':'0'*40,'path':'independent-r2/prior-approved-collector.md','bytes':0,'sha256':sha(b''),'gitBlob':'0'*40,'repositoryId':'synthetic-approval-assumption'}
payload={'format':'i05-caller-witness-payload/1','attemptId':pre['attemptId'],'purpose':'reader-joined','value':{'tag':'bool','value':False}}
payloadbytes=C(payload)
witness={'witnessId':'caller-reader','origin':'caller-owned-file','attemptId':pre['attemptId'],'collectorOwnerPin':pin,'verificationState':'verified','purpose':'reader-joined','file':{**empty,'path':'independent-r2/reader-witness.json','bytes':len(payloadbytes),'sha256':sha(payloadbytes)},'codecId':'i05-caller-witness-payload/1','layoutPin':pin,'fieldPointer':'/value','parentWitnessIds':[]}
evidence={'state':'observed','value':payload['value'],'witnessIds':['caller-reader'],'reason':None}
check('independent caller-only witness and false value require no fake child fields',not finite({'ref':'CallerWitness'},witness) and not finite({'ref':'CallerWitnessPayload'},payload) and not finite({'ref':'CallerEvidenceValue'},evidence),{'witness':witness,'payloadBase64':base64.b64encode(payloadbytes).decode(),'evidence':evidence})
def witness_errors(w,ev,purpose,declared,files,approved,parents=()):
 e=finite({'ref':'CallerWitness'},w)+finite({'ref':'CallerEvidenceValue'},ev)
 if w['witnessId'] not in declared or ev['witnessIds']!=[w['witnessId']]:e.append('dangling or wrong namespace')
 if w['attemptId']!=pre['attemptId']:e.append('cross attempt')
 if w['purpose']!=purpose:e.append('wrong event purpose')
 if any(x not in parents for x in w['parentWitnessIds']):e.append('future witness')
 if w['file']['path'] not in files:e.append('manifest missing original')
 else:
  b=files[w['file']['path']]
  if len(b)!=w['file']['bytes'] or sha(b)!=w['file']['sha256']:e.append('raw digest mismatch')
  value=json.loads(b)
  if value['attemptId']!=w['attemptId'] or value['purpose']!=w['purpose'] or value['value']!=ev['value']:e.append('pointer/value/source mismatch')
 if ev['state']=='observed' and (not approved or w['verificationState']!='verified' or w['collectorOwnerPin'] is None or w['layoutPin'] is None or ev['reason'] is not None):e.append('unverified observed')
 return e
filemap={witness['file']['path']:payloadbytes};ids={'caller-reader'}
check('independent witness full raw/namespace/purpose checks accept only explicit origin',not witness_errors(witness,evidence,'reader-joined',ids,filemap,True))
for name,mutw,mute,purpose,declared,files,approved in [
 ('dangling caller ID',witness,{**evidence,'witnessIds':['child-artifact']},'reader-joined',ids,filemap,True),
 ('caller masquerades as child',{**witness,'stageId':'fake-stage'},evidence,'reader-joined',ids,filemap,True),
 ('request not terminated',{**witness,'purpose':'cancel-request'},evidence,'target-terminated',ids,filemap,True),
 ('wrong actual attempt',{**witness,'attemptId':'other'},evidence,'reader-joined',ids,filemap,True),
 ('missing manifest member',witness,evidence,'reader-joined',ids,{},True),
 ('wrong raw SHA',{**witness,'file':{**witness['file'],'sha256':'f'*64}},evidence,'reader-joined',ids,filemap,True),
 ('unverified pin cannot observed',{**witness,'collectorOwnerPin':None,'verificationState':'captured-unverified'},evidence,'reader-joined',ids,filemap,False),
 ('later parent reference',{**witness,'parentWitnessIds':['future']},evidence,'reader-joined',ids,filemap,True),
 ('false erased as true',witness,{**evidence,'value':{'tag':'bool','value':True}},'reader-joined',ids,filemap,True)]:
 negatives.append({'name':name,'reject':bool(witness_errors(mutw,mute,purpose,declared,files,approved))})
check('all independently constructed field/identity/caller mutations reject',all(c['reject'] for c in negatives),negatives)
# Audit incident records without running their embedded source strings.
incident=read(R/'write-collision-incident-r2.json');commands=read(R/'commands-r2.json');history=[]
for i in range(1,5):
 rec=read(R/f'author-check-r2-{i:02}.json');streams=[]
 for channel in ('stdout','stderr'):
  s=rec[channel];b=base64.b64decode(s['base64'],validate=True)
  streams.append({'channel':channel,'match':b==s['text'].encode() and len(b)==s['bytes'] and sha(b)==s['sha256']})
 history.append({'check':i,'exit':rec['exit'],'argv':rec['argv'],'streams':streams})
check('actual four author exits and original split streams retained', [h['exit'] for h in history]==[1,1,0,0] and all(s['match'] for h in history for s in h['streams']),history)
restored=(R/'checker-source-r2.json').read_bytes();newsource=(R/'business-checker-source-r2.json').read_bytes()
check('incident restored old source and exact new executed container separately',len(restored)==12013 and sha(restored)==incident['restoredSha256'] and len(newsource)==19751 and sha(newsource)==incident['newR2SourceSha256'])
check('known process evidence gaps explicit instead of fabricated', 'not separately preserved' in incident['chronology'][0]['event'] and 'No wall-clock' in incident['timestamps'],{'chronology':incident['chronology'],'timestamps':incident['timestamps'],'initialReads':read(R/'first-failure-r2.json')['initialToolReadFailures']})
check('M02-M05 remain exact pending source/codec/layout/verifier guards',all(x['actualPin'] is None and 'pending' in x['status'] for x in missing['requests'] if x['id'] in ('M02','M03','M04','M05')))
result={'scope':'R2 minimal independent static delta; no author/model/product execution, no third-party schema engine','checks':checks,'allChecksPassed':all(c['pass'] for c in checks),'schemaKeywordEvaluatorBoundary':{'supported':['type','anyOf','const','enum','required','properties','additionalProperties:false','items','minItems','maxItems','minLength','maxLength','pattern','minimum'],'observedSchemaKeys':sorted(seen_keywords),'notACompleteJsonSchemaEngine':True},'sampleCoverage':{'completeAuthorSamples':5,'postContextCompleteAuthorSamples':sum(x['contextAvailable'] for x in checksamples),'acceptedContextChecks':'four independent identity positives plus key/ID counterexamples; no complete collected business/source claim'},'incident':{'finalCurrentIntegrity':True,'interimFrozenWriteViolation':True,'initialDraftBytesAvailable':False,'eventWallClockAvailable':False,'initialReadSplitStreamsAvailable':False,'sequence':incident['chronology']},'r1Disposition':{'R1-F01':'design gap closed by explicit three-arm attempt union and caller-entry/child-context namespace separation; new policy adoption remains pending','R1-F02':'design gap closed by explicit caller-only witnesses and origin-specific lifecycle references; real source verification remains pending'},'provisionalVerdict':'Pass limited pure-design if every independent check passes; process violation remains recorded, not excused'}
with (R/'independent-proof-r2.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'checks':len(checks),'allChecksPassed':result['allChecksPassed'],'failed':[c for c in checks if not c['pass']],'independentNegativeCount':len(negatives),'sampleCoverage':result['sampleCoverage'],'r1Disposition':result['r1Disposition']},ensure_ascii=False,indent=2))
