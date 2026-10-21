from pathlib import Path
from datetime import datetime,timezone
import os,stat,json,struct,collections
R=Path(__file__).parent;B=json.loads((R/'read-budget.json').read_text());M=json.loads((R/'observed-tool-metadata.json').read_text());A=json.loads((R/'cmake-extraction-report.json').read_text())
TC=Path('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain');SDK=Path(M['sdk-path']).resolve();CACHE=Path('/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld')
roots=[('sdk-complete',SDK),('compiler-include-complete',TC/'usr/include'),('compiler-resource-and-runtime-complete',Path(M['clang-resource-dir']))]
items={};groups={};errors=[]
def add(p,group):
 key=str(p)
 if key in items:
  if group not in items[key]['groups']:items[key]['groups'].append(group)
  return
 if len(items)+B['inventory_items']>=B['limit_inventory_items']:raise RuntimeError('inventory item guard reached; not complete')
 s=p.lstat();kind='regular' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'special'
 row={'path':key,'type':kind,'mode':oct(stat.S_IMODE(s.st_mode)),'bytes':s.st_size if kind=='regular' else 0,'lstat_bytes':s.st_size,'realpath':str(p.resolve()),'groups':[group],'device':s.st_dev,'inode':s.st_ino,'mtime_ns':s.st_mtime_ns}
 if kind=='symlink':row['linkname']=os.readlink(p);row['target_exists']=p.exists()
 items[key]=row
for label,root in roots:
 assert root.is_dir() and not root.is_symlink();add(root,label)
 for dp,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):add(Path(dp)/name,label)
 groups[label]={'root':str(root),'entry_count':sum(label in x['groups'] for x in items.values()),'declared_regular_bytes':sum(x['bytes'] for x in items.values() if label in x['groups'])}
# Exact executable supply and aliases corresponding to permitted probes, linker and known Apple wrappers.
probes=json.loads((R/'probe-index.json').read_text())
seeds={p['executable_pin_before_spawn']['path'] for p in probes}
seeds.update([str(TC/'usr/bin/ld'),'/usr/lib/dyld'])
for name in ['git','make','xcrun','xcodebuild']:
 p=Path('/Applications/Xcode.app/Contents/Developer/usr/bin')/name
 if p.exists():seeds.add(str(p))
for s in sorted(seeds):
 p=Path(s)
 if p.exists():add(p,'selected-tools');add(p.resolve(),'selected-tools-real')
 else:errors.append({'path':s,'reason':'selected executable missing'})
# Parse only Mach-O load-command bytes, without executing new programs.
def loads(path):
 with path.open('rb') as f:
  b=f.read(4096);B['read_bytes']+=len(b)
  offsets=[0]
  if b[:4]==bytes.fromhex('cafebabe'):
   n=struct.unpack_from('>I',b,4)[0];offsets=[struct.unpack_from('>IIIII',b,8+i*20)[2] for i in range(n)]
  result=[]
  for off in offsets:
   f.seek(off);hdr=f.read(32);B['read_bytes']+=len(hdr)
   if hdr[:4]!=bytes.fromhex('cffaedfe'):continue
   ncmds,sz=struct.unpack_from('<II',hdr,16)
   if sz>2*1024**2:raise ValueError('abnormal Mach-O load commands size')
   commands=f.read(sz);B['read_bytes']+=len(commands);cur=0;deps=[];rpaths=[]
   for i in range(ncmds):
    cmd,size=struct.unpack_from('<II',commands,cur)
    if size<8 or cur+size>len(commands):raise ValueError('invalid load command')
    if cmd in [0xc,0x80000018,0x8000001f,0x80000023,0x20,0x8000001c,0xe]:
     st=struct.unpack_from('<I',commands,cur+8)[0];v=commands[cur+st:cur+size].split(b'\0')[0].decode()
     if cmd==0x8000001c:rpaths.append(v)
     else:deps.append({'command':hex(cmd),'name':v})
    cur+=size
   result.append({'cpu_type':hex(struct.unpack_from('<I',hdr,4)[0]),'dependencies':deps,'rpaths':rpaths})
  return result
queue=[Path(s).resolve() for s in seeds if Path(s).exists()];done=set();edges=[];unresolved=[]
while queue:
 p=queue.pop(0)
 if str(p) in done:continue
 done.add(str(p));slices=loads(p)
 for sl in slices:
  for dep in sl['dependencies']:
   name=dep['name'];candidates=[]
   if name.startswith('/') :candidates=[Path(name)]
   elif name.startswith('@loader_path/'):candidates=[p.parent/name[len('@loader_path/'):]]
   elif name.startswith('@executable_path/'):candidates=[p.parent/name[len('@executable_path/'):]]
   elif name.startswith('@rpath/'):
    for rp in sl['rpaths']:
     rp=rp.replace('@loader_path',str(p.parent)).replace('@executable_path',str(p.parent))
     if rp.startswith('/'):candidates.append(Path(rp)/name[len('@rpath/'):])
   found=next((x for x in candidates if x.is_file()),None)
   edge={'source':str(p),'cpu_type':sl['cpu_type'],'load_command':dep['command'],'install_name':name,'candidate_paths':[str(x) for x in candidates]}
   if found:
    real=found.resolve();allowed=(str(real).startswith(str(TC)+'/') or str(real).startswith('/Applications/Xcode.app/Contents/Developer/') or str(real).startswith(A['destination']+'/') or str(real).startswith('/usr/lib/') or str(real).startswith('/System/Library/'))
    if not allowed:edge['status']='outside-declared-runtime-roots';unresolved.append(edge)
    else:
     edge.update(status='on-disk',resolved_path=str(real));add(found,'selected-runtime-closure');add(real,'selected-runtime-closure');queue.append(real)
   else:
    edge['status']='not-a-standalone-file; system dyld cache candidate' if name.startswith(('/usr/lib/','/System/Library/')) else 'unresolved-token'
    unresolved.append(edge)
   edges.append(edge)
# The concrete currently installed cache set is finite, separately declared; no unknown link traversal.
cache_rows=[]
for p in sorted(CACHE.iterdir()):
 if p.is_symlink() or not p.is_file():raise ValueError('unexpected cache object type')
 add(p,'external-system-dyld-cache-candidate');cache_rows.append(str(p))
licenses=[Path('/Applications/Xcode.app/Contents/Resources/LicenseInfo.plist'),Path('/Applications/Xcode.app/Contents/Resources/en.lproj/License.rtf'),Path('/Applications/Xcode.app/Contents/Resources/en.lproj/License.pdf'),Path('/Applications/Xcode.app/Contents/Info.plist'),TC/'ToolchainInfo.plist',SDK/'SDKSettings.json',SDK/'SDKSettings.plist']
for p in licenses:
 if p.exists():add(p,'terms-and-settings')
 else:errors.append({'path':str(p),'reason':'optional terms/settings candidate not present'})
legalroots=[str(x[1]) for x in roots]+[str(TC),'/Applications/Xcode.app/Contents/Developer','/Applications/Xcode.app/Contents/Resources',A['destination'],'/usr/bin','/usr/lib','/System/Library',str(CACHE)]
links=[]
for row in items.values():
 if row['type']=='symlink':
  row['realpath_within_declared_supply_roots']=any(row['realpath']==root or row['realpath'].startswith(root+'/') for root in legalroots)
  if not row['target_exists'] or not row['realpath_within_declared_supply_roots']:links.append(row)
records=sorted(items.values(),key=lambda x:x['path'])
with (R/'supply-plan.jsonl').open('w') as out:
 for x in records:out.write(json.dumps(x)+'\n')
cachebytes=sum(x['bytes'] for x in records if 'external-system-dyld-cache-candidate' in x['groups'])
normalbytes=sum(x['bytes'] for x in records if 'external-system-dyld-cache-candidate' not in x['groups'])
summary={'generated_utc':datetime.now(timezone.utc).isoformat(),'scan_complete':True,'inventory_entries':len(records),'with_cmake_entries':len(records)+B['inventory_items'],'type_counts':dict(collections.Counter(x['type'] for x in records)),'declared_total_regular_bytes':sum(x['bytes'] for x in records),'groups':groups,'noncache_declared_bytes':normalbytes,'cache_candidate_entries':len(cache_rows),'cache_candidate_bytes':cachebytes,'read_bytes_before_hashing':B['read_bytes'],'remaining_read_budget':B['limit_read_bytes']-B['read_bytes'],'full_hashing_would_fit':sum(x['bytes'] for x in records)+B['read_bytes']<=B['limit_read_bytes'],'all_selected_runtime_load_edges':len(edges),'unresolved_or_cache_runtime_edges':len(unresolved),'unresolved_unique_install_names':sorted({x['install_name'] for x in unresolved}),'symlink_exceptions':links,'optional_missing_candidates':errors,'legal_supply_roots':legalroots,'sdk_scope':'Entire canonical SDK tree, including all headers/modules/framework stubs/SDK libraries/settings; symlinks inventoried without external traversal','compiler_scope':'Entire selected compiler resource/runtime root and entire toolchain usr/include, plus exact selected executables, known Apple wrapper-resolved tools, and recursively resolved on-disk Mach-O dependencies across both slices','external_system_cache_scope':'Finite installed arm64e cache set declared separately as conservative backing candidate for absent standalone system dylibs; image membership not yet proven.'}
(R/'supply-declaration.json').write_text(json.dumps(summary,indent=2)+'\n');(R/'runtime-load-edges.json').write_text(json.dumps(edges,indent=2)+'\n');(R/'read-budget.json').write_text(json.dumps(B,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['symlink_exceptions','legal_supply_roots']},indent=2));print('SYMLINK_EXCEPTIONS',len(links))
