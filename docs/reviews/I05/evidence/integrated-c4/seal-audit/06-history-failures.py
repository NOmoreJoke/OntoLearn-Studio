from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;B=O/'readback';read=lambda f:json.loads((B/f).read_bytes());digest=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
p=read('internal-review/pure-query-probe.json');assert p['phases']==2 and p['additionalConcurrentQueries']==12 and p['privateTrueFilterChecks']==4 and p['processGlobalStateUnchanged']and p['rawGraphUnchanged']and p['selectedNoRecompute'];assert p['strictNegativeCases']==4 and p['numericLanguageControlGraphSize']==5
h=read('internal-review/history-success.json');old=read('internal-review/old5-complete.json')['records'][0];assert h['oldOriginalPayloadRowsBytesAndHashes']['payloadHash']==digest(old['payload'])and h['oldOriginalPayloadRowsBytesAndHashes']['rowsHash']==digest(old['rows']);assert h['newHistoricalCompletedJobs']==2
for r in h['records']:assert r['payload']['inputSelection']=='historical'and r['payload']['selectedResultIds']and r['metadata']['historicalSelectionRequired']
assert read('query-prototype/v1-singleton-audit.json')['prototype_v1_mutated_truefilter_callback']
cache=read('linux-stale-pyc-observation.txt');assert cache['sourceHasFinite6']and cache['imported']['executionSemanticsVersion']=='i05-finite-5'
assert 'Unsupported'in(B/'source-suite-first.stderr').read_text()or'UNSUPPORTED_SHACL'in(B/'source-suite-first.stderr').read_text()
assert (B/'internal-review/pure-query-probe.stderr.txt.first-attempt.raw').stat().st_size>0 and (B/'internal-review/pure-query-probe.stderr.txt.second-attempt.raw').stat().st_size>0 and (B/'internal-review/pure-query-probe.stderr.txt.third-attempt.raw').stat().st_size>0
for f in ['internal-review/probe-oracle-correction.txt','internal-review/probe-state-correction.txt','internal-review/old5-bind-error-baseline.stdout.txt']:assert(B/f).stat().st_size>0
reporthash=hashlib.sha256((B/'internal-review/report.md').read_bytes()).hexdigest();assert reporthash=='d053c56b49f635ce6fbe3e1a6c44f0bc55c4816b5a2da3b68684336d0fd61a97'
result={'independentReportSha256':reporthash,'pureCaseListLength':len(p['cases']),'lexicalCases':len(p['lexicalCases']),'concurrentQueries':12,'privateTrueFilterChecks':4,'oldResultContentHashComparedToActualReceipt':True,'historicalActualSuccesses':2,'originalFailuresAndCorrectionsPresent':True,'sourceCacheActuallyImportedFiveWhileSourceSix':True,'firstPackageRuntimeNotInferredFromSourceCache':True};(O/'06-history-failures.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
