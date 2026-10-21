from pathlib import Path,PurePosixPath
import tarfile,hashlib,json,posixpath,struct,datetime
RUN=Path(__file__).parent
ARCHIVE=RUN/'cmake-4.4.4-macos-universal.tar.gz'
sha=lambda b:hashlib.sha256(b).hexdigest()
def file_sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def macho(b):
 result={'magic_hex':b[:4].hex()}
 if b[:4]!=bytes.fromhex('cafebabe'):return result
 n=struct.unpack_from('>I',b,4)[0]; result['fat_arch_count']=n; slices=[]
 for i in range(n):
  cpu,sub,off,size,align=struct.unpack_from('>IIIII',b,8+i*20)
  s={'cpu_type_hex':hex(cpu),'architecture':{0x100000c:'arm64',0x1000007:'x86_64'}.get(cpu,'other'),'offset':off,'bytes':size,'alignment_power':align}
  if off+32<=len(b) and b[off:off+4]==bytes.fromhex('cffaedfe'):
   ncmds,cmdsize=struct.unpack_from('<II',b,off+16); cursor=off+32
   for j in range(ncmds):
    if cursor+8>len(b):break
    cmd,cs=struct.unpack_from('<II',b,cursor)
    if cs<8 or cursor+cs>len(b):break
    if cmd==0x32 and cs>=24:
     platform,minos,sdk,ntools=struct.unpack_from('<IIII',b,cursor+8)
     ver=lambda v:f'{v>>16}.{(v>>8)&255}.{v&255}'
     s['LC_BUILD_VERSION']={'platform':platform,'minimum_os':ver(minos),'sdk':ver(sdk)}
    cursor+=cs
  slices.append(s)
 result['slices']=slices;result['has_arm64']=any(s['architecture']=='arm64' for s in slices)
 return result
report={'kind':'static archive and byte audit only','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executed_archive_programs':False,'extracted_archive_tree':False,'findings':[]}
checksums=(RUN/'cmake-4.4.4-SHA-256.txt').read_text('utf-8')
lines=[x for x in checksums.splitlines() if x.split() and x.split()[-1].lstrip('*')==ARCHIVE.name]
if len(lines)!=1:raise ValueError('checksum basename match is not unique')
expected=lines[0].split()[0];actual=file_sha(ARCHIVE)
report['checksum']={'manifest_lines':len(checksums.splitlines()),'basename_unique_matches':len(lines),'official_line':lines[0],'archive_bytes':ARCHIVE.stat().st_size,'actual_sha256':actual,'matches':actual==expected}
if actual!=expected:raise ValueError('archive checksum mismatch')
listing=[];seen=set();members={};total=0;types={};syms=[]
with tarfile.open(ARCHIVE,'r:gz') as tf:
 for m in tf:
  n=m.name; normalized=posixpath.normpath(n)
  if n.startswith('/') or normalized in ('..','.') or normalized.startswith('../') or '\\' in n:raise ValueError('unsafe archive path '+repr(n))
  if normalized in seen:raise ValueError('duplicate normalized archive path '+repr(n))
  seen.add(normalized)
  kind='regular' if m.isfile() else 'directory' if m.isdir() else 'symlink' if m.issym() else 'hardlink' if m.islnk() else 'abnormal'
  if kind=='abnormal':raise ValueError('abnormal member type '+repr(n))
  if m.size<0:raise ValueError('negative member size')
  total+=m.size
  if len(listing)>50000 or total>2*1024**3:raise ValueError('audit resource ceiling exceeded')
  row={'path':n,'normalized_path':normalized,'type':kind,'bytes':m.size,'mode_octal':oct(m.mode),'linkname':m.linkname or None}
  if kind in ('symlink','hardlink'):
   target=posixpath.normpath(posixpath.join(posixpath.dirname(normalized),m.linkname) if kind=='symlink' else m.linkname)
   if m.linkname.startswith('/') or target=='..' or target.startswith('../') or '\\' in m.linkname:raise ValueError('escaping link '+repr(n))
   row['resolved_archive_target']=target;syms.append(row)
  listing.append(row);types[kind]=types.get(kind,0)+1;members[normalized]=m
 (RUN/'cmake-archive-members.json').write_text(json.dumps(listing,indent=2)+'\n')
 roots=sorted({n.split('/')[0] for n in seen})
 if len(roots)!=1:raise ValueError('archive has multiple roots')
 root=roots[0];report['archive']={'member_count':len(listing),'declared_total_member_bytes':total,'type_counts':types,'root':root,'path_link_type_safety':'PASS','links':syms}
 def resolve_link_path(path):
  visited=set()
  for hop in range(64):
   if path in visited:raise ValueError('cyclic archive link '+path)
   visited.add(path)
   parts=path.split('/');changed=False
   for k in range(1,len(parts)+1):
    prefix='/'.join(parts[:k]);pm=members.get(prefix)
    if pm is not None and (pm.issym() or pm.islnk()):
     target=posixpath.join(posixpath.dirname(prefix),pm.linkname) if pm.issym() else pm.linkname
     path=posixpath.normpath(posixpath.join(target,*parts[k:]))
     if not(path==root or path.startswith(root+'/')):raise ValueError('resolved archive link escapes root')
     changed=True;break
   if not changed:
    if path not in seen:raise ValueError('resolved archive link target missing '+path)
    return path
  raise ValueError('archive link resolution exceeds bounded hop count')
 for link in syms:link['final_resolved_archive_target']=resolve_link_path(link['resolved_archive_target'])
 cmake_bins=[n for n in seen if n.endswith('/Contents/bin/cmake') or n.endswith('/Contents/bin/ctest')]
 if len(cmake_bins)!=2:raise ValueError('expected unique cmake and ctest members')
 report['binaries']=[]
 for n in sorted(cmake_bins):
  b=tf.extractfile(members[n]).read()
  report['binaries'].append({'member':n,'bytes':len(b),'sha256':sha(b),'macho_static_headers':macho(b)})
  if not report['binaries'][-1]['macho_static_headers'].get('has_arm64'):raise ValueError('arm64 slice missing')
 module_paths=sorted(n for n in seen if '/Contents/share/cmake-4.4/Modules/' in n and members[n].isfile())
 if not module_paths:raise ValueError('CMAKE_ROOT Modules tree missing')
 cmake_root=module_paths[0].split('/Modules/')[0]
 required=['CMake.cmake','CMakeDetermineSystem.cmake','CMakeDetermineCXXCompiler.cmake','CMakeCXXCompiler.cmake.in','CMakeTestCXXCompiler.cmake','Platform/Darwin.cmake','Platform/Darwin-Initialize.cmake']
 missing=[f for f in required if cmake_root+'/Modules/'+f not in seen]
 if missing:raise ValueError('necessary Module resources missing '+repr(missing))
 report['cmake_root']={'archive_member_root':cmake_root,'modules_regular_file_count':len(module_paths),'necessary_module_members_present':required,'same_distribution_version':'4.4.4','version_basis':'Archive basename; Info.plist and Modules/CMake.cmake content are preserved separately'}
 text_names=sorted(n for n in seen if members[n].isfile() and (n.endswith('/Contents/Info.plist') or n==cmake_root+'/Modules/CMake.cmake' or 'Copyright' in PurePosixPath(n).name or '/Licenses/' in n))
 texts=[];text_dir=RUN/'cmake-static-texts';text_dir.mkdir(exist_ok=False)
 for i,n in enumerate(text_names):
  if members[n].size>2*1024**2:raise ValueError('unexpectedly large license/version text '+n)
  b=tf.extractfile(members[n]).read();b.decode('utf-8')
  dest=text_dir/(f'{i:03d}-'+PurePosixPath(n).name)
  dest.write_bytes(b);texts.append({'archive_member':n,'saved_path':str(dest),'bytes':len(b),'sha256':sha(b)})
 report['license_and_version_texts']=texts
 if not any('Copyright.txt' in x['archive_member'] for x in texts):report['findings'].append('No Copyright.txt member found; inspect license member inventory before approval')
report['node']={'version':'v24.15.0','license':{},'headers':[]}
license=RUN/'node-v24.15.0-LICENSE';lb=license.read_bytes();lb.decode('utf-8')
report['node']['license']={'path':str(license),'bytes':len(lb),'sha256':sha(lb),'complete_download':True,'npm_or_node_gyp_substitution':False}
for name in ['node_api.h','node_api_types.h','js_native_api.h','js_native_api_types.h']:
 p=RUN/('node-v24.15.0-'+name);b=p.read_bytes();b.decode('utf-8');lp=Path('/usr/local/include/node')/name
 rec={'header':name,'downloaded_path':str(p),'downloaded_bytes':len(b),'downloaded_sha256':sha(b),'local_path':str(lp),'local_exists':lp.exists()}
 if lp.exists():
  local=lp.read_bytes();rec.update(local_bytes=len(local),local_sha256=sha(local),byte_identical=local==b)
 report['node']['headers'].append(rec)
report['node']['headers_aggregate_bytes']=sum(x['downloaded_bytes'] for x in report['node']['headers'])
if report['node']['headers_aggregate_bytes']>4*1024**2:raise ValueError('headers total exceeds bound')
report['static_result']='PASS'
(RUN/'static-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
