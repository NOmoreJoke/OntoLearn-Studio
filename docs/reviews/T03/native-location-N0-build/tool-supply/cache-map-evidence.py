from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).parent;B=json.loads((R/'read-budget.json').read_text());B['read_bytes']+=1500
p=Path('/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e.map');data=p.read_bytes();B['read_bytes']+=len(data);h=hashlib.sha256(data).hexdigest();lines=data.decode().splitlines()
edges=json.loads((R/'runtime-load-edges-final.json').read_text());names=sorted({x['install_name'] for x in edges if not x['status'].startswith('on-disk')})
records=[]
for name in names:
 matches=[i for i,line in enumerate(lines) if line.strip()==name]
 records.append({'install_name':name,'exact_map_name_matches':len(matches),'line_numbers_1_based':[i+1 for i in matches],'following_map_lines':[[lines[j] for j in range(i,min(i+5,len(lines)))] for i in matches],'status':'CACHE_MAP_NAMES_IMAGE' if matches else 'MAP_MEMBERSHIP_NOT_PROVEN'})
rep={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'map_path':str(p),'bytes':len(data),'sha256':h,'basis':'Read-only text map of current concrete installed dyld cache. Exact image install-name matches; does not substitute for hashing cache bodies or recursively reading all embedded image dependencies.','records':records,'all_requested_image_names_present':all(x['exact_map_name_matches'] for x in records)}
(R/'runtime-cache-map-evidence.json').write_text(json.dumps(rep,indent=2)+'\n')
rows=[json.loads(x) for x in (R/'supply-inventory.jsonl').read_text().splitlines()]
for row in rows:
 if row['path']==str(p):row.update(sha256=h,hash_status='HASHED_CACHE_METADATA_MAP_ONLY_NOT_RUNTIME_BODY');row.pop('missing_reason',None)
with (R/'supply-inventory.jsonl').open('w') as out:
 for row in rows:out.write(json.dumps(row)+'\n')
unhashed=[{k:row[k] for k in ['path','bytes','realpath','hash_status']} for row in rows if row['type']=='regular' and row.get('sha256') is None]
(R/'unhashed-system-cache-objects.json').write_text(json.dumps(unhashed,indent=2)+'\n')
a=json.loads((R/'supply-hash-report.json').read_text());a.update(unhashed_cache_entries=len(unhashed),unhashed_cache_declared_bytes=sum(x['bytes'] for x in unhashed),regular_entries_with_sha256=sum(x['type']=='regular' and x.get('sha256') is not None for x in rows),remaining_read_budget=B['limit_read_bytes']-B['read_bytes'],read_budget=B)
a['minimum_additional_bytes_to_hash_all_unhashed_cache_candidates']=max(0,a['unhashed_cache_declared_bytes']-a['remaining_read_budget']);a['cache_map_evidence']='runtime-cache-map-evidence.json';a['physical_files_fully_hashed']+=1
(R/'supply-hash-report.json').write_text(json.dumps(a,indent=2)+'\n');(R/'read-budget.json').write_text(json.dumps(B,indent=2)+'\n')
print(json.dumps({'all_requested_image_names_present':rep['all_requested_image_names_present'],'requested_install_names':len(names),'missing_map_names':[x['install_name'] for x in records if not x['exact_map_name_matches']],'unhashed_cache_entries':len(unhashed),'unhashed_cache_bytes':a['unhashed_cache_declared_bytes'],'read_bytes':B['read_bytes'],'minimum_delta':a['minimum_additional_bytes_to_hash_all_unhashed_cache_candidates']},indent=2))
