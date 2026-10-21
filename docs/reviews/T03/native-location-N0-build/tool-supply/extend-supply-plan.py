from pathlib import Path
import json,os,stat,struct,datetime
R=Path(__file__).parent;B=json.loads((R/'read-budget.json').read_text());items={x['path']:x for x in map(json.loads,(R/'supply-plan.jsonl').read_text().splitlines())};edges=json.loads((R/'runtime-load-edges.json').read_text());summary=json.loads((R/'supply-declaration.json').read_text())
# Reuse the already-reviewed local static parser function, not its discovery driver.
src=(R/'discover-supply.py').read_text();func=src[src.index('def loads(path):'):src.index('\nqueue=[Path(s).resolve()')];exec(compile(func,'local-static-Mach-O-parser','exec'))
allowed=summary['legal_supply_roots']+['/Applications/Xcode.app/Contents/SharedFrameworks','/Applications/Xcode.app/Contents/Frameworks']
def add(p,group):
 k=str(p)
 if k in items:
  if group not in items[k]['groups']:items[k]['groups'].append(group)
  return
 assert len(items)+B['inventory_items']<B['limit_inventory_items']
 s=p.lstat();kind='regular' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special'
 row={'path':k,'type':kind,'mode':oct(stat.S_IMODE(s.st_mode)),'bytes':s.st_size if kind=='regular' else 0,'lstat_bytes':s.st_size,'realpath':str(p.resolve()),'groups':[group],'device':s.st_dev,'inode':s.st_ino,'mtime_ns':s.st_mtime_ns}
 if kind=='symlink':row.update(linkname=os.readlink(p),target_exists=p.exists(),realpath_within_declared_supply_roots=any(str(p.resolve())==x or str(p.resolve()).startswith(x+'/') for x in allowed))
 items[k]=row
q=[]
for e in edges:
 if e['status']=='outside-declared-runtime-roots':
  p=next((Path(x) for x in e['candidate_paths'] if Path(x).is_file()),None)
  if p and any(str(p.resolve()).startswith(x+'/') for x in allowed):
   e.update(status='on-disk-explicit-Xcode-framework-reference',resolved_path=str(p.resolve()),basis='Exact static load-command and rpath reference of authorized xcodebuild executable; no framework directory scan')
   add(p,'explicit-Xcode-framework-reference');add(p.resolve(),'explicit-Xcode-framework-reference');q.append(p.resolve())
seen=set()
while q:
 p=q.pop(0)
 if str(p) in seen:continue
 seen.add(str(p))
 for sl in loads(p):
  for dep in sl['dependencies']:
   name=dep['name'];candidates=[]
   if name.startswith('/'):candidates=[Path(name)]
   elif name.startswith('@loader_path/'):candidates=[p.parent/name[13:]]
   elif name.startswith('@executable_path/'):candidates=[p.parent/name[17:]]
   elif name.startswith('@rpath/'):
    for rp in sl['rpaths']:
     rp=rp.replace('@loader_path',str(p.parent)).replace('@executable_path',str(p.parent))
     if rp.startswith('/'):candidates.append(Path(rp)/name[7:])
   found=next((x for x in candidates if x.is_file()),None)
   e={'source':str(p),'cpu_type':sl['cpu_type'],'load_command':dep['command'],'install_name':name,'candidate_paths':[str(x) for x in candidates]}
   if found and any(str(found.resolve()).startswith(x+'/') for x in allowed):
    e.update(status='on-disk',resolved_path=str(found.resolve()));add(found,'explicit-runtime-reference');add(found.resolve(),'explicit-runtime-reference');q.append(found.resolve())
   else:e['status']='not-a-standalone-file; system dyld cache candidate' if name.startswith(('/usr/lib/','/System/Library/')) else 'unresolved-token'
   edges.append(e)
# Preserve observed SDK alias identity and relevant installation selectors without re-walking any completed roots.
M=json.loads((R/'observed-tool-metadata.json').read_text());add(Path(M['sdk-path']),'observed-sdk-alias')
for s in ['/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain','/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Info.plist']:
 p=Path(s)
 if p.exists():add(p,'installation-identity')
records=sorted(items.values(),key=lambda x:x['path'])
with (R/'supply-plan-final.jsonl').open('w') as out:
 for x in records:out.write(json.dumps(x)+'\n')
summary.update(inventory_entries=len(records),with_cmake_entries=len(records)+B['inventory_items'],declared_total_regular_bytes=sum(x['bytes'] for x in records),noncache_declared_bytes=sum(x['bytes'] for x in records if 'external-system-dyld-cache-candidate' not in x['groups']),read_bytes_before_hashing=B['read_bytes'],remaining_read_budget=B['limit_read_bytes']-B['read_bytes'],all_selected_runtime_load_edges=len(edges),unresolved_or_cache_runtime_edges=sum(not e['status'].startswith('on-disk') for e in edges),unresolved_unique_install_names=sorted({e['install_name'] for e in edges if not e['status'].startswith('on-disk')}),legal_supply_roots=allowed)
summary['minimum_additional_read_budget_for_full_candidate_hashing']=max(0,summary['declared_total_regular_bytes']+B['read_bytes']-B['limit_read_bytes'])
summary['full_hashing_would_fit']=summary['minimum_additional_read_budget_for_full_candidate_hashing']==0
(R/'supply-declaration-final.json').write_text(json.dumps(summary,indent=2)+'\n');(R/'runtime-load-edges-final.json').write_text(json.dumps(edges,indent=2)+'\n');(R/'read-budget.json').write_text(json.dumps(B,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['inventory_entries','declared_total_regular_bytes','noncache_declared_bytes','read_bytes_before_hashing','minimum_additional_read_budget_for_full_candidate_hashing','unresolved_or_cache_runtime_edges','unresolved_unique_install_names']},indent=2))
