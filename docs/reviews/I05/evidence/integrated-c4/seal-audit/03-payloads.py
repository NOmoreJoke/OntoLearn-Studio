from pathlib import Path
import json,hashlib
OUT=Path(__file__).resolve().parent;B=OUT/'readback';read=lambda p:json.loads(p.read_bytes());canonical=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False);digest=lambda x:hashlib.sha256(canonical(x).encode()).hexdigest()
def check_rows(rows,payload):
 assert rows[0]['cells']==['columns','path','value','part','parts'];assert[row['ordinal']for row in rows]==list(range(len(rows)))
 pieces={}
 for row in rows[1:]:
  pointer,fragment,ordinal,count=row['cells'];pieces.setdefault(pointer,[]).append((ordinal,count,fragment))
 decoded={}
 for pointer,parts in pieces.items():
  assert [v[0]for v in parts]==list(range(1,parts[0][1]+1))and all(v[1]==len(parts)for v in parts)
  decoded[pointer]=json.loads(''.join(v[2]for v in parts))
 expected={}
 def leaves(v,p=''):
  if isinstance(v,dict)and v:
   for key,item in v.items():leaves(item,p+'/'+key.replace('~','~0').replace('/','~1'))
  elif isinstance(v,list)and v:
   for i,item in enumerate(v):leaves(item,p+'/'+str(i))
  else:expected[p]=v
 leaves(payload);assert decoded==expected
names=['independent-source-01','macos-packaged','linux-source','linux-packaged','independent-source-v2-01','macos-old-c3-v2','macos-packaged-v2','linux-old-c3-v2','linux-source-v2','linux-packaged-v2'];runs={}
for name in names:
 directory=B/'stdio-string'/name;summary=read(directory/'summary.json');runtime=read(directory/'runtime.json');fixture=read(directory/'fixture.json');expectedImplementation=runtime.get('expectedProducerImplementation',runtime['implementation']);assert len(expectedImplementation)==3
 publics=sorted(directory.glob('*.public.json'));auths=sorted(directory.glob('*.authenticated.json'));assert len(publics)==len(auths)==summary['jobs']==19
 assert digest(fixture['spec'])==fixture['specSha256']==summary['fixtureSpecSha256'];assert fixture['databaseSha256']==summary['seedDatabaseSha256'];reason=read(directory/'reasoning.authenticated.json')['payload'];producer=read(directory/'reasoning.public.json')['metadata']['resultId'];rowcount=0;rawcount=0;rolechecks=0
 comparisons={}
 for a in auths:
  label=a.name.removesuffix('.authenticated.json');auth=read(a);public=read(directory/(label+'.public.json'));p=auth['payload'];meta=auth['metadata'];job=public['job'];rows=public['rows'];assert meta==public['metadata'];assert meta['implementation']==job['implementation']==expectedImplementation;assert job['state']=='succeeded'and job['resultRef']['resultId']==meta['resultId'];assert p['executionSemanticsVersion']==expectedImplementation['executionSemanticsVersion'];assert auth['payloadHash']==digest(p)and auth['rowsHash']==digest(rows);assert auth['rowCount']==len(rows);check_rows(rows,p);rowcount+=len(rows)
  rawpath=directory/(label+'.raw.json')
  if rawpath.exists():
   raw=read(rawpath);assert raw['public']==public and raw['storedRows']==rows;stored=raw['storedSemanticRow'];assert stored['result']==meta['resultId']and stored['payload']==canonical(p)and stored['payload_hash']==auth['payloadHash']and stored['rows_hash']==auth['rowsHash'];rawcount+=1
  if 'validationBinding'in p:
   source={'assertedFacts':reason['assertedFacts'],'ontologyAxioms':reason['ontology'],'constraints':next(d['value']for d in fixture['spec']['definitions']if d['layer']=='constraint'and d['id']==p['definitionId'])}
   if p['selectedResultIds']:source.update(derivedFacts=reason['reasoning']['rules'],derivedAxioms=reason['reasoning']['rdfs'])
   assert {r['role']for r in p['validationBinding']['resources']}==set(source)
   for r in p['validationBinding']['resources']:assert r['ref']==digest(source[r['role']]),(name,label,r['role']);rolechecks+=1
  content={k:v for k,v in p.items()if k!='validationBinding'}
  def replace(v):
   if isinstance(v,dict):return{k:replace(x)for k,x in v.items()}
   if isinstance(v,list):return[replace(x)for x in v]
   return '@existing-reasoning-result'if v==producer else v
  comparisons[label]=replace(content)
 comparison=read(directory/'comparison.json');assert comparison['payloads']==comparisons;assert hashlib.sha256((directory/'comparison.json').read_bytes()).hexdigest()==summary['comparisonSha256']
 old='old-c3'in name;observed={'conclusions':len(reason['reasoning']['rules']),'traces':len(reason['reasoning']['evidence'])}
 if old:
  assert observed==summary['observedReasoning']=={'conclusions':5,'traces':5};assert len(summary['oracleFailures'])==17;assert read(directory/'max1.authenticated.json')['payload']['report']['conforms']is False and read(directory/'min2.authenticated.json')['payload']['report']['conforms']is True;assert summary['status']=='failed-semantic-oracle';assert rawcount==19
 else:
  assert observed=={'conclusions':7,'traces':8};assert summary['status']=='passed'
  if name.endswith('-v2')or name=='independent-source-v2-01':assert rawcount==19
 runs[name]={'records':19,'rows':rowcount,'actualConclusionsAndTraces':observed,'rawStoredRowsChecked':rawcount,'resourceContentHashChecks':rolechecks,'implementation':expectedImplementation,'comparisonSha256':summary['comparisonSha256'],'oldSemanticFailures':len(summary.get('oracleFailures',[]))}
for group in [names[:4],['independent-source-v2-01','macos-packaged-v2','linux-source-v2','linux-packaged-v2']]:assert len({runs[n]['comparisonSha256']for n in group})==1
assert len({read(B/'stdio-string'/n/'fixture.json')['databaseSha256']for n in names if n.endswith('-v2')or n=='independent-source-v2-01'})==1
independent=[]
for file in ['old5-complete.json','worker6-complete.json','stdio6-complete.json','history-success.json']:
 x=read(B/'internal-review'/file);total=0
 for r in x['records']:
  assert r['job']['state']=='succeeded'and r['job']['implementation']==r['metadata']['implementation'];check_rows(r['rows'],r['payload']);total+=len(r['rows'])
 independent.append({'file':file,'records':len(x['records']),'rows':total})
assert sum(x['records']for x in independent)==50 and sum(x['rows']for x in independent)==5329
history=read(B/'internal-review/history-identity.json');assert history['oldMetadataPayloadRowsUnchanged']and history['oldFinite5AuthenticReadable'];assert len(history['checks'])==5
for r in history['checks']:assert r.get('code',r.get('error',{}).get('code'))=='IDENTITY_CONFLICT'
assert{r['alteredConsumerField']for r in history['checks']if'alteredConsumerField'in r}=={'engineVersion','executionSemanticsVersion','dependencyLockHash'}
result={'runs':runs,'independent50Records':independent,'historyThreeFieldAndCurrentHistoricalRejections':True};(OUT/'03-payloads.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
