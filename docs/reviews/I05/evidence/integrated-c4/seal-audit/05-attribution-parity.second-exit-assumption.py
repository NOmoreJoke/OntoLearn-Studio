from pathlib import Path
import json,hashlib,subprocess
O=Path(__file__).resolve().parent;B=O/'readback';R=Path('/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation');read=lambda p:json.loads((B/p).read_bytes());sha=lambda x:hashlib.sha256(x).hexdigest();result={}
old=json.loads((O.parent/'c3-seal-independent-audit/readback/source-export-manifest.json').read_bytes())['executionInputs'];new=read('source-export-manifest.json')['executionInputs'];assert len(old)==204 and len(new)==205;changed=[p for p in old if old[p]!=new[p]];assert len(changed)==9;assert sum(old[p]==new[p]for p in old)==195;result['executionDiff']={'old':204,'new':205,'changed':changed,'unchangedOriginal':195,'soleAdded':list(set(new)-set(old))}
for platform in ['macos','linux']:
 d=f'{platform}-parity';m=read(d+'/package-manifest.json');src=read(d+'/source-semantic.json');pkg=read(d+'/packaged-semantic.json');assert src['suite']['result']==pkg['suite']['result']and src['network']['result']==pkg['network']['result'];assert m['measurements']==m['freshProcessMeasurements']==12;assert len(m['files'])==m['fileCount']and sum(x['bytes']for x in m['files'])==m['engineDirectoryBytes'];assert m['inventory']['nativeLicenseProvenanceMatched'];assert m['network']['positiveCalibrationHits']==1 and m['network']['deniedRequestHits']==0
 network=src['network']['result'];assert len(network)==28 and all(x['actual']==x['expected']and not x['networkAuditEvents']for x in network[:-1]);assert network[-1]['actual']=='EXTERNAL_ACCESS_DENIED'and network[-1]['networkAuditEvents']==['urllib.Request']
 for runtime in ['source','packaged']:
  assert (B/f'{platform}-runtime/{runtime}-suite.stdout').read_bytes()==(B/f'{platform}-runtime/source-suite.stdout').read_bytes()
  for scale in [1,10]:
   reference=read(d+f'/source-{scale}x-0.json')['result']['result']
   for trial in range(3):
    oldrec=read(d+f'/{runtime}-{scale}x-{trial}.json');fresh=read(d+f'/{runtime}-fresh-{scale}x-{trial}.json');assert oldrec['stderr']==fresh['stderr']==''and oldrec['result']['result']==reference;assert oldrec['result']['assertedTriples']==18*scale and oldrec['result']['ontologyTriples']==4;events=fresh['events'];assert[e['event']for e in events]==['firstComplete','warmComplete'];assert events[0]['receivedElapsedNs']==fresh['spawnToFirstCompleteResultNs']<events[1]['receivedElapsedNs']<=fresh['processElapsedNs'];assert all(e['observation']['result']==reference for e in events)
 assert'7 passed'in(B/f'{platform}-runtime/real-stdio.stdout').read_text()and'17 passed'in(B/f'{platform}-i04-package/runtime.stdout').read_text();result[platform]={'originalMeasurements':12,'freshMeasurements':12,'fullResultParity':True,'networkCases':28,'engineBytes':m['engineDirectoryBytes'],'engineFiles':m['fileCount'],'rawAppBytes':m['appDirectoryBytes'],'exactNativeLicenseScope':m['inventory']['nativeLicenseScope']}
# Full original stdout/exit receipts rather than a success-only final log.
for file,patterns in {'check-full-first.txt':['would be reformatted'], 'check-full-second.txt':['1837 passed'],'check-full-third.txt':['1847 passed in 80.09s','672 passed'],'linux-source-affected.txt':['1 failed, 359 passed'],'linux-source-affected-second.txt':['1 failed, 359 passed'],'linux-source-affected-third.txt':['360 passed in 9.32s'],'internal-review/selected-tests.log':['522 passed in 33.31s'],'independent-regressions/c3-3289-final-red.stdout.txt':['40 failed, 23 passed'],'independent-regressions/c3-3289-isolation-errors.stdout.txt':['2 failed, 8 passed'],'independent-regressions/c4-83868b4-first-full.stdout.txt':['73 passed in 3.66s']}.items():
 s=(B/file).read_text();assert all(x.lower()in s.lower()for x in patterns),(file,patterns)
for file in ['check-full-first-exit.txt','first-affected-exit.txt','second-affected-exit.txt']:assert(B/file).read_text().strip()=='1'
for file in ['check-full-second-exit.txt','check-full-third-exit.txt','linux-source-and-package-exit.txt','linux-source-and-package-second-exit.txt','package-macos-exit.txt','verify-sources-exit.txt']:assert(B/file).read_text().strip()=='0'
assert not(B/'independent-stdio-driver/source-01/launch.json').exists()
v1=sha((B/'independent-stdio-driver/run_string_stdio-v1.py').read_bytes());guard=sha((B/'independent-stdio-driver/run_string_stdio.py').read_bytes());v2=sha((B/'independent-stdio-driver/run_string_stdio_v2.py').read_bytes());assert v1!=guard and guard==read('independent-stdio-driver/source-02/launch.json')['driverSha256'];assert v2==read('independent-stdio-driver/source-v2-01/launch.json')['driverSha256']
for name in ['macos-packaged','linux-source','linux-packaged']:assert read('stdio-string/'+name+'/launch.json')['driverSha256']==guard
for name in ['macos-old-c3-v2','macos-packaged-v2','linux-old-c3-v2','linux-source-v2','linux-packaged-v2']:assert read('stdio-string/'+name+'/launch.json')['driverSha256']==v2
for file in ['stdio-string/macos-v2-commands.json','stdio-string/linux-v2-commands.json']:
 for r in read(file):assert r['exitCode']==r['expectedExitCode']==(1 if'old-c3'in r['name']else 0)
f1=read('independent-stdio-driver/fixture/seed.json');f2=read('independent-stdio-driver/fixture-v2/seed.json');assert f1['databaseSha256']!=f2['databaseSha256']and f1['inputSnapshotId']!=f2['inputSnapshotId'];spec1=f1['spec'];spec2=f2['spec'];diff=[]
def differences(a,b,p=''):
 if type(a)is not type(b):diff.append(p)
 elif isinstance(a,dict):
  assert set(a)==set(b)
  for k in a:differences(a[k],b[k],p+'/'+k)
 elif isinstance(a,list):
  assert len(a)==len(b)
  for i,(x,y)in enumerate(zip(a,b)):differences(x,y,p+'/'+str(i))
 elif a!=b:diff.append(p)
differences(spec1,spec2);assert diff==['/definitions/4/value/when/0/2','/format']or set(diff)=={'/definitions/4/value/when/0/2','/format'}
result['driverAttribution']={'source01NoLaunchHash':True,'preservedPreGuardSHA':v1,'source02AndMainV1SHA':guard,'v2LaunchSHA':v2,'fixtureSpecDifferencePaths':diff,'oldRunExit1ForSemanticOracle':True}
(O/'05-attribution-parity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
