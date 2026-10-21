from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,stat,collections,plistlib
R=Path(__file__).parent;B=json.loads((R/'read-budget.json').read_text());plan=[json.loads(x) for x in (R/'supply-plan-final.jsonl').read_text().splitlines()]
known={};done=[];unhashed=[];errors=[];zeros=[];groups=collections.defaultdict(lambda:{'entries':0,'regular_files':0,'declared_bytes':0,'hashed_regular_files':0})
with (R/'supply-inventory.jsonl').open('w') as out:
 for row in plan:
  p=Path(row['path']);s=p.lstat();assert (s.st_dev,s.st_ino,s.st_mtime_ns)==(row['device'],row['inode'],row['mtime_ns']),row['path']
  assert stat.S_IMODE(s.st_mode)==int(row['mode'],8)
  if row['type']=='regular':
   assert s.st_size==row['bytes'];key=(s.st_dev,s.st_ino,s.st_mtime_ns,s.st_size)
   if 'external-system-dyld-cache-candidate' in row['groups']:
    row.update(sha256=None,hash_status='NOT_READ_GUARD_FULL_CACHE_SET_WOULD_EXCEED',missing_reason='Full cache candidate set cannot fit remaining cumulative 8GiB read authorization; no partial set represented as complete')
    unhashed.append({k:row[k] for k in ['path','bytes','realpath','hash_status']})
   elif key in known:
    row.update(sha256=known[key]['sha256'],hash_status='REUSED_SAME_PHYSICAL_FILE_IDENTITY',hash_reference_path=known[key]['path'])
   else:
    if B['read_bytes']+s.st_size>B['limit_read_bytes']:raise RuntimeError('Guard before file '+str(p))
    h=hashlib.sha256();count=0
    with p.open('rb') as f:
     for b in iter(lambda:f.read(1024*1024),b''):h.update(b);count+=len(b);B['read_bytes']+=len(b)
    after=p.lstat();assert count==row['bytes'] and (after.st_dev,after.st_ino,after.st_mtime_ns,after.st_size)==key
    row.update(sha256=h.hexdigest(),hash_status='HASHED_FULL_BYTES');known[key]={'sha256':row['sha256'],'path':row['path']}
   if s.st_size==0:zeros.append(row['path'])
  elif row['type']=='symlink':
   assert os.readlink(p)==row['linkname'] and str(p.resolve())==row['realpath']
   row['link_text_sha256']=hashlib.sha256(row['linkname'].encode()).hexdigest();row['hash_status']='SYMLINK_IDENTITY_NOT_TARGET_DUPLICATION'
  elif row['type']=='directory':row['hash_status']='DIRECTORY_METADATA'
  else:errors.append(row);row['hash_status']='REJECT_SPECIAL_TYPE'
  for label in row['groups']:
   groups[label]['entries']+=1
   if row['type']=='regular':
    groups[label]['regular_files']+=1;groups[label]['declared_bytes']+=row['bytes'];groups[label]['hashed_regular_files']+=row.get('sha256') is not None
  out.write(json.dumps(row)+'\n');done.append(row)
B['inventory_items']+=len(plan)
report={'finished_utc':datetime.now(timezone.utc).isoformat(),'metadata_inventory_complete':True,'entries':len(done),'physical_files_fully_hashed':len(known),'regular_entries_with_sha256':sum(x['type']=='regular' and x.get('sha256') is not None for x in done),'unhashed_cache_entries':len(unhashed),'unhashed_cache_declared_bytes':sum(x['bytes'] for x in unhashed),'remaining_read_budget':B['limit_read_bytes']-B['read_bytes'],'minimum_additional_bytes_to_hash_all_unhashed_cache_candidates':max(0,sum(x['bytes'] for x in unhashed)-(B['limit_read_bytes']-B['read_bytes'])),'groups':dict(groups),'zero_byte_regular_files':zeros,'errors':errors,'sdk_headers_modules_framework_stubs_and_compiler_resource_inventory_complete':all(v['regular_files']==v['hashed_regular_files'] for k,v in groups.items() if k in ['sdk-complete','compiler-include-complete','compiler-resource-and-runtime-complete']),'full_external_system_runtime_cache_closure_complete':False,'overall_supply_status':'INCOMPLETE_EXTERNAL_SYSTEM_RUNTIME_CACHE_GUARD','approvals_changed':False,'read_budget':B}
(R/'supply-hash-report.json').write_text(json.dumps(report,indent=2)+'\n');(R/'unhashed-system-cache-objects.json').write_text(json.dumps(unhashed,indent=2)+'\n');(R/'read-budget.json').write_text(json.dumps(B,indent=2)+'\n')
# Preserve exact local applicable agreement bytes, already hashed above; no SDK objects are copied.
terms=R/'terms';terms.mkdir(mode=0o700)
for name,path in [('Xcode-License.rtf','/Applications/Xcode.app/Contents/Resources/en.lproj/License.rtf'),('Xcode-LicenseInfo.plist','/Applications/Xcode.app/Contents/Resources/LicenseInfo.plist')]:
 data=Path(path).read_bytes();B['read_bytes']+=len(data);(terms/name).write_bytes(data)
settings={}
for path in ['/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/SDKSettings.json','/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/SDKSettings.plist']:
 b=Path(path).read_bytes();B['read_bytes']+=len(b);settings[path]=json.loads(b) if path.endswith('.json') else plistlib.loads(b)
(R/'sdk-settings-observed.json').write_text(json.dumps(settings,indent=2)+'\n')
report['read_budget']=B;report['remaining_read_budget']=B['limit_read_bytes']-B['read_bytes'];report['minimum_additional_bytes_to_hash_all_unhashed_cache_candidates']=max(0,sum(x['bytes'] for x in unhashed)-(B['limit_read_bytes']-B['read_bytes']))
(R/'supply-hash-report.json').write_text(json.dumps(report,indent=2)+'\n');(R/'read-budget.json').write_text(json.dumps(B,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['groups','zero_byte_regular_files']},indent=2));print('ZERO_BYTE_REGULAR_FILES',len(zeros))
