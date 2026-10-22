import ast, collections, copy, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path.cwd(); OUT=ROOT/'docs/reviews/I05/retained-source-review-triage'
FIX='2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(n):return json.loads((OUT/n).read_bytes())
commands=[]
def run(args):
 r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 commands.append({'argv':args,'exitCode':r.returncode,'stdoutBytes':len(r.stdout),'stdoutSHA256':sha(r.stdout),'stderrText':r.stderr.decode(),'stderrBytes':len(r.stderr),'stderrSHA256':sha(r.stderr)})
 assert r.returncode==0
 return r.stdout
assert run(['git','rev-parse','HEAD']).decode().strip()==FIX
summary=load('m06-author-applied-summary.json');files=[r['path'] for r in summary['actualTwoFiles']]
sourceproof=[]
for r in summary['actualTwoFiles']:
 current=(ROOT/r['path']).read_bytes();base=run(['git','show',FIX+':'+r['path']])
 assert (len(current),sha(current))==(r['afterBytes'],r['afterSHA256'])
 assert (len(base),sha(base))==(r['beforeBytes'],r['beforeSHA256'])
 before=ast.parse(base);after=ast.parse(current)
 if '/src/' in r['path']:
  func=next(n for n in after.body if getattr(n,'name',None)=='_scope_observation')
  guard=func.body.pop(0);assert ast.dump(guard)==ast.dump(ast.parse('if counter is None: raise ProbeFault("INTERNAL_ERROR")').body[0])
  error=next(n for n in after.body if getattr(n,'name',None)=='ProbeFault')
  assert [a.arg for a in next(n for n in error.body if getattr(n,'name',None)=='__init__').args.args]==['self','code']
  admissionBeforeAllOriginalStatements=True
 else:
  test=next(n for n in after.body if getattr(n,'name',None)=='test_scope_without_counter_fails_before_loading_canonical_inputs')
  after.body.remove(test)
 assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)
 sourceproof.append({'path':r['path'],'beforeBytes':len(base),'beforeSHA256':sha(base),'actualBytes':len(current),'actualSHA256':sha(current),'onlyAddedGuardOrTestAST':True})
diff=run(['git','diff',FIX,'--']+files)
assert diff==(OUT/'m06-final-source-diff.stdout.raw').read_bytes()
with (OUT/'independent-triage-r1-applied-diff.stdout.raw').open('xb') as f:f.write(diff)
receiptNames=['m06-regression-red-01.json','m06-regression-green-01.json','m06-env-prepare-01.json','m06-two-source-ruff-check-01.json','m06-two-source-format-check-01.json','m06-final-source-diff.json','m06-final-source-whitespace.json','m06-baseline-ruff-1.json','m06-baseline-ruff-2.json','m06-baseline-format-1.json','m06-baseline-format-2.json','m06-added-guard-format.json','m06-added-test-format.json']
verified=[]
for name in receiptNames:
 rec=load(name)
 if 'streams' in rec:
  for stream in rec['streams']:
   b=(ROOT/stream['path']).read_bytes();assert (len(b),sha(b))==(stream['bytes'],stream['sha256'])
 else:
  for stream in ['stdout','stderr']:
   b=(OUT/(name[:-5]+'.'+stream+'.raw')).read_bytes()
   assert (len(b),sha(b))==(rec[stream+'Bytes'],rec[stream+'SHA256'])
 verified.append({'path':name,'exit':rec['exit'],'rawStreamsMatched':True})
red=load('m06-regression-red-01.json');green=load('m06-regression-green-01.json')
assert red['argv']==green['argv'] and red['exit']==1 and green['exit']==0
assert red['argv'][5]==files[1]+'::test_scope_without_counter_fails_before_loading_canonical_inputs'
assert "KeyError: 'ontolearn_engine.semantic'" in (OUT/'m06-regression-red-01.stdout.raw').read_text()
assert '1 passed' in (OUT/'m06-regression-green-01.stdout.raw').read_text()
current=load('m06-two-source-ruff-check-01.stdout.raw');baseline=load('m06-baseline-ruff-1.stdout.raw')+load('m06-baseline-ruff-2.stdout.raw')
def signature(issue,old=False):
 out={k:copy.deepcopy(issue[k]) for k in ['code','message','location','end_location','filename']}
 if old:
  delta=2 if '/src/' in issue['filename'] else 8
  threshold=1162 if '/src/' in issue['filename'] else 762
  for pos in ['location','end_location']:
   if out[pos]['row']>=threshold:out[pos]['row']+=delta
 return json.dumps(out,sort_keys=True)
assert len(current)==len(baseline)==10
assert collections.Counter(signature(i) for i in current)==collections.Counter(signature(i,True) for i in baseline)
assert collections.Counter(i['code'] for i in current)=={'I001':1,'B023':9}
assert load('m06-two-source-ruff-check-01.json')['exit']==1
assert load('m06-two-source-format-check-01.json')['exit']==1
assert all(load('m06-baseline-format-'+str(i)+'.json')['exit']==1 for i in [1,2])
assert all(load('m06-added-'+s+'-format.json')['exit']==0 for s in ['guard','test'])
errata=(OUT/'triage-disposition-r1.md').read_text();assert all(s in errata for s in ['五个','六个','packaging','pyparsing'])
for name,size,digest in [('independent-triage-r1-report.md',7513,'b205c2cafc300e0f1e4da72e000046d6b22d3343d45fe55d771d27bb0a11d8b0'),('independent-triage-r1-m06-addendum.md',1543,'886b539fc1367fed50b171abc3c86a0f52baeb6e4c6180951c9185b9b742e81d')]:
 b=(OUT/name).read_bytes();assert (len(b),sha(b))==(size,digest)
proof={'kind':'independent-I05-applied-M06-narrow-proof','fixedBase':FIX,'files':sourceproof,'actualDiffMatchesAuthorSavedDiff':True,'onlyExactNewCaseReportedBySavedReceipts':True,'reviewerRanProductTests':False,'verifiedSavedReceipts':verified,'lint':{'currentExit':1,'baselineCount':10,'currentCount':10,'codes':{'I001':1,'B023':9},'exactSignaturesAfterInsertionLineMap':True,'newDiagnosticSignatures':0,'overallPass':False},'format':{'bothCurrentExit':1,'eachBaselineExit':1,'addedSnippetsExit':0,'overallPass':False},'oldSealedReportAndAddendumIdentityUnchanged':True,'P1P2InAppliedDiff':[],'scopeLimits':['no runtime/test/uv/install/fullcheck performed by reviewer','green single negative boundary case does not prove legal full-v1/B1/full417/canonical integration','environment raw and receipts checked; no environment/native/global inspection','formatted-source large raw only byte/hash checked, not used to expand algorithm reading'],'commandReceipts':commands}
with (OUT/'independent-triage-r1-applied-proof.json').open('x') as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print('PASS: applied exact two-source identities and fixed-base diff; AST remainder unchanged; 13 saved command receipts/raw streams; red KeyError and green one-case; ten inherited lint signatures. Overall lint/format remain failed. No product/test command executed by reviewer.')
