import ast, collections, hashlib, json, pathlib, subprocess, sys, tomllib
ROOT=pathlib.Path.cwd()
OUT=ROOT/'docs/reviews/I05/retained-source-review-triage'
FIX='2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64'
SUP='6891a5842302859a531cf82767c5a482417bc274'
BASE='5f910b52c69d86a1076b2032e5d3c63e715947f3'
receipts=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def command(args):
 r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
 receipts.append({'argv':args,'exitCode':r.returncode,'stdout':{'bytes':len(r.stdout),'sha256':sha(r.stdout)},'stderr':{'bytes':len(r.stderr),'sha256':sha(r.stderr),'text':r.stderr.decode('utf-8','replace')}})
 assert r.returncode==0, (args,r.returncode,r.stderr)
 return r.stdout
def show(ref,path): return command(['git','show',ref+':'+path])
def load(name): return json.loads((OUT/name).read_bytes())
assert command(['git','rev-parse','HEAD']).decode().strip()==FIX
assert command(['git','branch','--show-current']).decode().strip()=='fix/I05-retained-source-review-triage'
expected={
'docs/iterations/I05/retained-source-review-triage/minimal-owned-repair-plan.md':(9616,'44f8a3b1d55e20990de787e41b3c74b7b2b6695c71dafaff712fcfbbdb115e68'),
'docs/reviews/I05/retained-source-review-triage/opinion-association-matrix.json':(19804,'e18a8692b5a2501f833fc5d4f608366eb0b95e817e5b0bd50aa8dc4b70d11ee0'),
'docs/reviews/I05/retained-source-review-triage/m08-static-facts.json':(7929,'3f8703821ab4b0583969b45e2eed14d39a8edf993013616410e1cdffb0352dfd'),
'docs/reviews/I05/retained-source-review-triage/m08-static-closure-correction-r2.json':(3172,'8bf094f71ea351abfc76275fac26a5f9c9548eda8e64fdbe767ee8682b6dc43f'),
'docs/reviews/I05/retained-source-review-triage/m09-shared-owner-routing-facts.json':(7752,'b7447b9ab437863e2416c74bc56ac78b4abb1edcbad1c283bc6c6498621f60a1'),
'docs/reviews/I05/retained-source-review-triage/next-full-review-coverage-inventory.json':(898602,'75b4363cbcdc65211f71f03f2ef23b7c1d1efd6b458bdd82f6d8441864f943ec')}
for path,(size,digest) in expected.items():
 b=(ROOT/path).read_bytes(); assert (len(b),sha(b))==(size,digest),path
facts=load('m08-static-facts.json'); correction=load('m08-static-closure-correction-r2.json')
raw={}
for rec in facts['records']:
 b=show(rec['ref'],rec['path']);raw[rec['ref'],rec['path']]=b
 assert (len(b),sha(b))==(rec['bytes'],rec['sha256'])
 if 'topLevelImportsOnly' in rec:
  imports=[]
  for n in ast.parse(b).body:
   if isinstance(n,ast.ImportFrom): imports.append({'line':n.lineno,'module':n.module,'level':n.level,'names':[a.name for a in n.names]})
   elif isinstance(n,ast.Import): imports.append({'line':n.lineno,'module':None,'level':0,'names':[a.name for a in n.names]})
  assert imports==rec['topLevelImportsOnly'],rec['path']
required={'rdflib','pyparsing','pyshacl','owlrl','prettytable','wcwidth','html5rdf','packaging'}
depsproof={}
for label,ref in [('candidate',FIX),('supplier',SUP)]:
 project=tomllib.loads(raw[ref,'packages/engine/pyproject.toml'].decode())['project']
 lock=tomllib.loads(raw[ref,'uv.lock'].decode()); packages={p['name']:p for p in lock['package']}
 assert len(packages)==len(lock['package'])
 claimed=facts['versions'][label]
 assert project['dependencies']==claimed['projectDependencies']
 assert project['requires-python']==claimed['requiresPython']
 assert len(packages)==claimed['packageCount']
 assert packages['ontolearn-engine']['metadata']==claimed['engineLockMetadata']
 closure={'ontolearn-engine'}; extras=collections.defaultdict(set)
 while True:
  old=(set(closure),{k:tuple(sorted(v)) for k,v in extras.items()})
  for name in list(closure):
   p=packages[name];edges=list(p.get('dependencies',[]))
   for extra in list(extras.get(name,set())): edges+=p.get('optional-dependencies',{}).get(extra,[])
   for edge in edges:
    closure.add(edge['name']);extras[edge['name']].update(edge.get('extra',[]))
  if old==(set(closure),{k:tuple(sorted(v)) for k,v in extras.items()}): break
 active={k:sorted(v) for k,v in extras.items() if v}
 c=correction['versions'][label]
 assert sorted(closure)==c['runtimeClosureIncludingActivatedExtras']
 assert active==c['activatedExtras']
 assert (required<=closure)==c['allRequiredEightInClosure']
 assert sha(raw[ref,'uv.lock'])==c['lockSHA256']
 # Independently reproduce original no-extras closure; preserved as a documented superseded result.
 simple={'ontolearn-engine'}
 while True:
  nxt=simple|{e['name'] for n in simple for e in packages[n].get('dependencies',[])}
  if nxt==simple: break
  simple=nxt
 assert sorted(simple)==claimed['engineDependencyClosure']
 for name,entry in claimed['requiredEightPackages'].items():
  if entry is None: assert name not in packages
  else:
   assert entry['version']==packages[name]['version']
   assert entry['dependencies']==packages[name].get('dependencies',[])
   assert entry['inEngineClosure']==(name in simple)
 depsproof[label]={'projectDependencies':project['dependencies'],'requiresPython':project['requires-python'],'lockPackageCount':len(packages),'closureIncludingActivatedExtras':sorted(closure),'activatedExtras':active,'requiredMissingFromLock':sorted(required-packages.keys()),'requiredMissingFromEngineClosure':sorted(required-closure),'originalNoExtrasClosureReproduced':True}
assert depsproof['candidate']['requiredMissingFromLock']==['html5rdf','owlrl','prettytable','pyshacl','wcwidth']
assert depsproof['candidate']['requiredMissingFromEngineClosure']==['html5rdf','owlrl','packaging','prettytable','pyshacl','wcwidth']
shared=load('m09-shared-owner-routing-facts.json');sharedproof=[]
for rec in shared['records']:
 b=show(FIX,rec['path']);assert (len(b),sha(b))==(rec['bytes'],rec['sha256'])
 if rec['path'].endswith(('storage.py','job_store.py')):
  assert b==show(BASE,rec['path']);assert rec['identicalToApprovedBase5f'] is True
  lines=b.decode().splitlines()
  for sn in rec['snippets']:
   actual='\n'.join(f'{i+1}: {lines[i]}' for i in range(sn['firstLine']-1,sn['lastLine']))
   assert actual==sn['text']
  sharedproof.append({'path':rec['path'],'sameBytesAs5f':True,'verifiedSnippetRanges':[[s['firstLine'],s['lastLine']] for s in rec['snippets']]})
 else:
  entry=json.loads(b)['codes']['OWNERSHIP_CONFLICT']
  assert rec['exactOwnershipErrorEntries']==[['/codes/OWNERSHIP_CONFLICT',entry]]
  assert entry['paramsSchema']['required']==['detailRef']
  sharedproof.append({'path':rec['path'],'onlyEntryInterpreted':'/codes/OWNERSHIP_CONFLICT','detailRefRequired':True})
matrix=load('opinion-association-matrix.json');old={}
for rec in matrix['sourceReportsAndStatuses']:
 b=pathlib.Path(rec['path']).read_bytes();assert (len(b),sha(b))==(rec['bytes'],rec['sha256'])
 old[rec['reviewer'],rec['phase'],rec['kind']]=json.loads(b) if rec['kind']=='reviewer-status' else b.decode()
rows=matrix['currentOpinionRows'];assert len(rows)==matrix['currentOpinionCount']==13
mrows=[r for r in rows if r['reviewer']=='minimax'];assert len(mrows)==9
for phase,field in [('first','firstOpinion'),('continuation','continuationOpinion')]:
 status=old['minimax',phase,'reviewer-status']; lookup={f['id']:f for f in status['findings']}
 for row in mrows: assert row[field]==lookup.get(row['id'])
 assert status['finalVerdict']=='NotPass'
assert matrix['historicalOpinionsAsReportedByMContinuation']==old['minimax','continuation','reviewer-status']['priorOpinions']
assert all(r['findingClosedByTriage'] is False for r in rows)
assert [r['id'] for r in rows if r['reviewer']=='zcode']==['Z-R2-F-1','Z-R2-F-2','Z-R2-O-1','Z-R2-O-2']
zfirst=old['zcode','first','report'];zcont=old['zcode','continuation','report']
assert all(x in zfirst for x in ['F-1','F-2']) and all(x in zcont for x in ['F-1','F-2','O-1','O-2','550–1203'])
assert len(matrix['firstFingerprintDifferencesKeptOpen'])==3
inv=load('next-full-review-coverage-inventory.json');src=inv['sourceManifest'];manifestbytes=pathlib.Path(src['path']).read_bytes()
assert (len(manifestbytes),sha(manifestbytes))==(src['bytes'],src['sha256'])
# Only fixed member identity metadata is used. Never read or execute materialized source bodies.
manifest=json.loads(manifestbytes); members=[{k:r[k] for k in ('path','sourceRef','sourcePath','gitBlob','bytes','sha256')} for r in manifest['materialized']]
counts=collections.Counter(r['path'].split('/')[2] for r in members)
assert dict(counts)==inv['namespaceCounts'] and len(counts)==16 and sum(counts.values())==22492
main=[{k:r[k] for k in ('sourcePath','gitBlob','bytes','sha256')} for r in members if r['path'].split('/')[2]=='main-source-only']
assert main==inv['fullMainFiles'] and len(main)==inv['mainFullMemberCount']==856
exts=set(inv['codeClassifierExtensions']);groups=collections.defaultdict(list)
for r in members:
 if pathlib.PurePosixPath(r['sourcePath']).suffix in exts:
  key=tuple(r[k] for k in ('sourcePath','gitBlob','bytes','sha256'))
  groups[key].append({'namespace':r['path'].split('/')[2],'sourceRef':r['sourceRef'],'materializedPath':r['path']})
actual={tuple(g[k] for k in ('sourcePath','gitBlob','bytes','sha256')):g['aliases'] for g in inv['codeByteGroups']}
assert len(actual)==len(groups)==251
assert actual==groups
assert inv['productBodiesReadToGenerateThisInventory'] is False and inv['previewOnlyNotNewCandidateManifest'] is True
assert len(inv['queuedBranches'])==8
proof={'kind':'independent-I05-static-triage-r1-proof','sourceRef':FIX,'scope':'static triage and repair plan only; no product acceptance','inputs':[{'path':p,'bytes':v[0],'sha256':v[1]} for p,v in expected.items()],'M08':depsproof,'M09':sharedproof,'matrix':{'currentM':9,'currentZ':4,'firstAndContinuationMRecordsExactMatch':True,'historicalMStatusExactMatch':True,'oldReportsAndStatusesIdentityMatched':8,'allCurrentOpinionsRemainOpen':True,'ZUnreadMiddleRetained':True},'inventory':{'fullyParsedMetadataBytes':len((OUT/'next-full-review-coverage-inventory.json').read_bytes()),'sourceManifestMetadataRowsCompared':len(members),'mainRowsCompared':len(main),'namespaceCountsCompared':len(counts),'exactCodeByteGroupsCompared':len(groups),'queuedBranchesPreserved':8,'sourceBodiesReadForInventory':False,'metadataDoesNotProveActualReview':True},'commandReceipts':receipts,'productOrImportOrRuntimeOrTestsOrInstallOrNetworkOrDbOrNativeExecuted':False}
with (OUT/'independent-triage-r1-proof.json').open('x') as f: json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print('PASS: all six fixed input identities; TOML/AST M08 including extras; M09 fixed snippets/byte identity; 13 matrix opinions; all inventory metadata groups. Product acceptance not assessed.')
