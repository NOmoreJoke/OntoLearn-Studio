from pathlib import Path
from datetime import datetime,timezone
import subprocess,os,json,hashlib,posixpath,collections
D=Path(__file__).parent;REPO=D.parents[5];FB='fb40bde92cc35269c25c11a8628a71d5f750be4e';DRIVER='fe98dab02375362fcc07ca9bb309de17b558fcf2';PREFIX='docs/reviews/T03/native-location-N0-build/tool-supply/'
ENV=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0');sourcebytes={}
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(args):
 p=subprocess.run(['/usr/bin/git','--no-optional-locks',*args],cwd=REPO,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True);return p.stdout
def read(name):
 path=PREFIX+name
 if path not in sourcebytes:sourcebytes[path]=git(['show',FB+':'+path])
 return sourcebytes[path]
def j(name):return json.loads(read(name))
def out(name,v,compact=False):
 data=(json.dumps(v,ensure_ascii=False,separators=(',',':')) if compact else json.dumps(v,ensure_ascii=False,indent=2))+'\n';b=data.encode()
 with (D/name).open('xb') as f:f.write(b)
 return {'path':str(D/name),'realpath':str(D.resolve()/name),'bytes':len(b),'sha256':sha(b)}
tree=git(['ls-tree','-r','--name-only',FB,'--',PREFIX]).decode().splitlines();assert len(tree)==109
parts=j('inventory-parts.json');supply=[];cmake=[];sourcepartpointers=[]
for item in parts['parts']:
 b=read(item['name']);assert len(b)==item['bytes'] and sha(b)==item['sha256'];rr=[json.loads(x) for x in b.splitlines()];assert len(rr)==item['records']
 (supply if item['name'].startswith('supply-') else cmake).extend(rr)
 sourcepartpointers.append({'ref':FB,'path':PREFIX+item['name'],'bytes':len(b),'sha256':sha(b),'records':len(rr),'selector_scope':'All original records retained at fixed Git ref; derived files select regular records only.'})
assert len(supply)==53092 and len(cmake)==9041 and sum(x['type']=='regular' for x in cmake)==8839
probe=j('probe-index.json');bylabel={x['label']:x for x in probe};assert len(bylabel)==13
extraction=j('cmake-extraction-report.json');oldcandidate=j('candidate-pins.json');observed=j('observed-tool-metadata.json');settingsdoc=j('sdk-settings-observed.json');terms=j('terms-index.json');delta=j('dyld-delta-read-result.json');deltamanifest=j('dyld-delta-manifest.json');delta_raw=read('dyld-delta-complete-inventory.jsonl')
dm=next(x for x in deltamanifest['records'] if x['path']=='dyld-delta-complete-inventory.jsonl');assert len(delta_raw)==dm['bytes'] and sha(delta_raw)==dm['sha256'];delta_rows=[json.loads(x) for x in delta_raw.splitlines()];assert len(delta_rows)==81 and delta['all_81_pre_post_identity_and_hash_complete']
# Read fixed explanatory text only; no source/runtime reparse and no actual supplier object access.
read('independent-supply-review.md');read('delivery-notes.md');read('terms/Xcode-License.rtf');read('terms/Xcode-LicenseInfo.plist')
driver_path='scripts/build-native-location.mjs';driver_body=git(['show',DRIVER+':'+driver_path]);driver_text=driver_body.decode();sourcebytes[driver_path]=driver_body
assert "? { PATH: '/usr/bin:/bin', HOME: buildDir, TMPDIR: buildDir, LANG: 'C', LC_ALL: 'C' }" in driver_text
SDK='/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk';DEV='/Applications/Xcode.app/Contents/Developer';TC=DEV+'/Toolchains/XcodeDefault.xctoolchain';CMAKE_ROOT=next(x['realpath'].split('/CMake.app/')[0]+'/CMake.app' for x in cmake if x['type']=='regular')
def pin_from_host(x):
 assert x['type']=='regular' and isinstance(x['bytes'],int) and x['bytes']>=0 and isinstance(x.get('sha256'),str) and len(x['sha256'])==64
 return {'path':x['realpath'],'realpath':x['realpath'],'bytes':x['bytes'],'sha256':x['sha256']}
def insert(dest,p,origin):
 if p['path'] in dest:assert dest[p['path']]['pin']==p,(p,origin);dest[p['path']]['origins'].append(origin)
 else:dest[p['path']]={'pin':p,'origins':[origin]}
# Overlay completed fixed 81 metadata; original pending records are never rewritten.
overlay={x['path']:x for x in delta_rows};host=[]
for source_row in supply:
 x=dict(source_row)
 if x['path'] in overlay:
  dr=overlay[x['path']];assert x['bytes']==dr['bytes_read'] and x['realpath']==dr['expected_realpath'];assert x.get('sha256') is None
  x['sha256']=dr['sha256'];x['derived_overlay']='fixed dyld delta complete metadata only'
 host.append(x)
assert sum(x['type']=='regular' and x.get('sha256') is None for x in host)==0
sdkrows=[x for x in host if 'sdk-complete' in x['groups']];sdkfiles=[pin_from_host(x) for x in sdkrows if x['type']=='regular'];assert len(sdkfiles)==33464 and len({x['path'] for x in sdkfiles})==33464
assert all(x['path'].startswith(SDK+'/') and x['realpath'].startswith(SDK+'/') for x in sdkfiles)
sdk_inv={'roots':[SDK],'files':sorted(sdkfiles,key=lambda x:x['path'])};sdkPin=out('sdk-files-inventory.json',sdk_inv,True);assert sdkPin['bytes']<16*1024**2
# Retain metadata-only installation selectors separately from actual resource allowlist.
identity_paths={ '/Applications/Xcode.app/Contents/Info.plist', TC+'/ToolchainInfo.plist', DEV+'/Platforms/MacOSX.platform/Info.plist' }
resource={};identity=[];allhostpins={}
for x in host:
 if x['type']!='regular':continue
 p=pin_from_host(x);insert(allhostpins,p,{'source_group':x['groups'],'original_path':x['path']})
 if 'sdk-complete' in x['groups']:continue
 if p['path'] in identity_paths:identity.append(p);continue
 insert(resource,p,{'source':'fb40 supply parts','original_path':x['path'],'groups':x['groups'],'delta_overlay':x.get('derived_overlay')})
for x in cmake:
 if x['type']!='regular':continue
 p={'path':x['realpath'],'realpath':x['realpath'],'bytes':x['bytes'],'sha256':x['actual_sha256']};assert p['sha256']==x['archive_sha256'];insert(resource,p,{'source':'fb40 extracted archive member inventory','archive_path':x['archive_path'],'original_actual_path':x['actual_path']})
roots=[CMAKE_ROOT,TC+'/usr/include',TC+'/usr/lib',TC+'/usr/bin',DEV+'/usr/bin','/Applications/Xcode.app/Contents/SharedFrameworks/DVTSystemPrerequisites.framework','/Applications/Xcode.app/Contents/Resources','/usr/bin','/usr/lib','/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld']
resourcefiles=[resource[k]['pin'] for k in sorted(resource)]
assert len(resourcefiles)<=50000
for p in resourcefiles:assert any(p['path'].startswith(r+'/') and p['realpath'].startswith(r+'/') for r in roots),p
resPin=out('resource-files-inventory.json',{'roots':roots,'files':resourcefiles},True);assert resPin['bytes']<16*1024**2
assert sum(p['path'].startswith(CMAKE_ROOT+'/') for p in resourcefiles)==8839
assert sum(p['path'].startswith('/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/') for p in resourcefiles)==82
assert any(x['bytes']==0 and x['path'].endswith('/hello.f') for x in resourcefiles)
def hostpin(canonical):return allhostpins[canonical]['pin']
def probepin(label):
 p=bylabel[label]['executable_pin_before_spawn'];return {k:p[k] for k in ['path','realpath','bytes','sha256']}
executables={'cmake':probepin('cmake-version'),'c':probepin('clang-version'),'cxx':probepin('clangxx-version'),'buildTool':hostpin(DEV+'/usr/bin/make'),'git':hostpin(DEV+'/usr/bin/git')}
assert executables['c']['realpath']==executables['cxx']['realpath']==TC+'/usr/bin/clang'
sdksettings=hostpin(SDK+'/SDKSettings.json');sdkterms=hostpin('/Applications/Xcode.app/Contents/Resources/en.lproj/License.rtf')
# Exact current schema candidate only, kept unapproved. Environment sidecar identifies the necessary owner decision.
darwin={'approval':{'approved':False,'reference':None},'version':'Xcode 27.1 (27A9275), Apple clang 21.0.0, SDK 27.0, CMake 4.4.4','generator':'Unix Makefiles','executables':executables,'resourceInventory':resPin,'sdk':{'root':SDK,'version':'27.0','settings':sdksettings,'terms':sdkterms,'inventory':sdkPin},'environment':{},'systemLibraries':[]}
darwinPin=out('darwin-toolchain-candidate.json',darwin)
env={'approval':{'approved':False,'reference':None},'current_driver_ref':DRIVER,'driver_path':driver_path,'current_darwin_lock_schema_environment':{},'current_build_env_literal_values':{'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},'current_build_env_derived_values':{'HOME':'buildDir','TMPDIR':'buildDir'},'requested_unadopted_environment_literal_values':{'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','DEVELOPER_DIR':DEV},'requested_derived_values':{'HOME':'future exact driver buildDir','TMPDIR':'same future exact driver buildDir'},'current_driver_accepts_or_passes_DEVELOPER_DIR':False,'minimum_future_owner_delta':[{'site':'validateSchema darwin environment allowed keys','change':'If approved, explicitly allow and pin DEVELOPER_DIR instead of the currently exact empty object; retain exact key validation and no ambient inherit.'},{'site':'build darwin env construction','change':'If approved, pass the exact approved DEVELOPER_DIR literal along with existing PATH/HOME/TMPDIR/LANG/LC_ALL; current driver hardcodes the object and does not consume tc.environment.'}],'no_driver_or_lock_changed':True,'reason':'Direct actual make/git backend candidates avoid treating Apple dispatchers as compiler/tool identities; developer selection still must be an explicit adopted environment decision for any xcrun/compiler module selection.'}
out('environment-candidate.json',env)
routing={'source_ref':FB,'executables_candidate':executables,'auxiliary_linker':hostpin(TC+'/usr/bin/ld'),'make':{'dispatcher_pin':probepin('make-version'),'observed_version':observed['make-version'],'actual_backend_candidate':executables['buildTool'],'backend_metadata_groups':['selected-tools','selected-tools-real'],'backend_specific_version_probe_performed':False,'dispatch_chain_proven_by_exec_trace':False,'basis':'Fixed installed Developer/usr/bin/make file identity from selected-tools metadata, supplied by named Xcode root; prior version command was /usr/bin/make. Candidate chooses direct backend, not dispatcher pin.'},'git':{'dispatcher_pin':probepin('git-version'),'observed_version':observed['git-version'],'actual_backend_candidate':executables['git'],'backend_specific_version_probe_performed':False,'dispatch_chain_proven_by_exec_trace':False,'basis':'Fixed installed Developer/usr/bin/git identity from selected-tools metadata; prior version command was /usr/bin/git. Direct backend candidate is not a claim of a separate backend probe.'},'compiler':{'c_find_result':observed['clang-path'],'cxx_find_result':observed['clangxx-path'],'c_and_cxx_realpath':executables['c']['realpath'],'cxx_alias_record_retained_in_original_metadata':True,'version_observed':observed['clang-version'],'resource_dir_observed':observed['clang-resource-dir']},'sdk':{'canonical_root':SDK,'observed_alias':observed['sdk-path'],'version':observed['sdk-version'],'settings_pin':sdksettings,'terms_pin':sdkterms},'installed_development_terms':{'original_source_pin':sdkterms,'preserved_raw_at_fixed_ref':FB+':'+PREFIX+'terms/Xcode-License.rtf','LicenseInfo':{'licenseID':'EA2002','licenseType':'GM'},'scope':'Installed Xcode and Apple SDK development agreement; does not substitute for independent OSS notices or redistribution clearance.'},'future_distributable_third_party_notices':{'status':'NOT_COMPLETE','specific_gaps':terms.get('component_terms_gap',[])},'direct_system_link_inputs_candidate':{'pins':[],'meaning':'No extra explicit system library or Linux library is proposed. Empty list is not proof that the toolchain/runtime has no system dependencies; implicit SDK linker selections and actual used inputs remain future observations, and owner must approve the selected core link contract.'},'installation_identity_metadata_pins_not_claimed_as_compile_resources':identity,'node':{'approval':{'approved':False,'reference':None},'status':'Not adopted by this metadata derivation; Node runtime/headers/license adoption and addon load remain separate. Core does not require Node.'},'windows':{'approval':{'approved':False,'reference':None},'toolchain':None,'environment':None,'addon':None,'status':'No Windows/MSVC/Electron import/hook/delayimp supply adopted here.'}}
out('tool-routing-sdk-terms.json',routing)
nonregular={'fixed_source_ref':FB,'sdk_original_type_counts':dict(collections.Counter(x['type'] for x in sdkrows)),'sdk_directory_and_link_record_predicate':'supply original rows: groups contains sdk-complete AND type in directory/symlink','compiler_include_original_rows':[x for x in host if 'compiler-include-complete' in x['groups']],'compiler_resource_original_type_counts':dict(collections.Counter(x['type'] for x in host if 'compiler-resource-and-runtime-complete' in x['groups'])),'CMake_original_type_counts':dict(collections.Counter(x['type'] for x in cmake)),'CMake_implicit_container':extraction['implicit_container'],'source_parts':sourcepartpointers,'records_not_modified_or_discarded':True,'interpretation':'Regular driver pins are a compact derived allowlist. Full path/type/mode/link/realpath/directory identities remain in exact original Git parts; directory and symlink records are not silently treated as regular file pins.'}
out('directory-link-source-pointers.json',nonregular)
rootboundaries=[]
for r in roots:
 selected=[p for p in resourcefiles if p['path'].startswith(r+'/')]
 rootboundaries.append({'root':r,'selected_file_records':len(selected),'authority_scope':'Only exact listed file pins; root is a containment boundary, not permission to discover/read/accept unlisted files','coverage':'Complete extracted regular distribution' if r==CMAKE_ROOT else 'Complete compiler clang/21 resource tree and selected runtime dylibs; not every unrelated usr/lib object' if r==TC+'/usr/lib' else 'Complete selected 81 exact cache object identities plus previously hashed map; not embedded image dependency or atomic cross-file proof' if r.endswith('/dyld') else 'Original bounded metadata-selected files/headers only; see original type records'})
coverage={'generated_utc':datetime.now(timezone.utc).isoformat(),'source_ref':FB,'fixed_tool_supply_docs':len(tree),'sdk_regular_file_count':len(sdkfiles),'sdk_declared_regular_bytes':sum(x['bytes'] for x in sdkfiles),'sdk_inventory_pin':sdkPin,'sdk_limit_bytes':16*1024**2,'sdk_limit_files':50000,'resource_regular_file_count':len(resourcefiles),'resource_declared_regular_bytes_with_full_distribution_and_runtime':sum(x['bytes'] for x in resourcefiles),'resource_inventory_pin':resPin,'resource_zero_byte_regular_count':sum(x['bytes']==0 for x in resourcefiles),'full_extracted_CMake_regular_count':8839,'exact_completed_cache_objects':81,'cache_map_identity_records':1,'dedup_rule':'Canonical path equals previously recorded realpath; equal bytes/SHA required for every merged alias; no physical reread or fresh path resolve of supplier objects. Executable cxx alias pin separately preserved.','root_boundaries':rootboundaries,'remaining_specific_gaps':['Toolchain/execution adoption not granted; current exact current driver does not represent or pass proposed DEVELOPER_DIR; owner must decide a bounded future delta before using that candidate environment.','Actual make/git backend pins are fixed installed metadata; prior versions were through Apple dispatchers and no independent direct-backend probe or exec trace was performed.','Embedded cache-image transitive dependencies and cross-file atomic snapshot not proven by 81 object hashes.','Future postbuild compile_commands/depfiles/used headers/stubs/libs/link graph/import/export remain absent; do not pre-create or infer them.','Installed development agreement is recorded; independent component notices and future redistribution per-image terms remain incomplete as detailed in original terms index.','No current physical drift recheck: this task reads fixed metadata only; any actual adoption/preflight read needs a new exact scope and must continue the existing 9745727085 supply-body read account.','Node/Windows/Electron supplies not adopted and not a blocker for the separately chosen core component.'],'all_new_approvals_false':True,'actual_supplier_body_bytes_read_this_derivation':0,'prior_actual_cumulative_supplier_body_bytes_preserved':9745727085,'no_new_runtime_source_parse_or_probe':True,'no_product_lock_old_evidence_changed':True,'systemLibraries_empty_candidate_is_not_runtime_closure_waiver':True}
out('coverage-and-gaps.json',coverage)
bodyrecords=[]
for path,b in sorted(sourcebytes.items()):
 ref=DRIVER if path==driver_path else FB
 bodyrecords.append({'ref':ref,'path':path,'bytes':len(b),'sha256':sha(b),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'read_kind':'Fixed Git JSON/JSONL/text only'})
out('source-bodies-manifest.json',{'source_tool_supply_ref':FB,'fixed_tool_supply_total_paths':len(tree),'driver_ref':DRIVER,'metadata_bodies_read':bodyrecords,'metadata_bytes_read':sum(len(b) for b in sourcebytes.values()),'physical_supplier_objects_read':0,'derivation_rules':{'SDK':'All sdk-complete regular rows exactly; four pin fields only; canonical SDK root; none omitted.','resources':'All extracted CMake regular rows plus non-SDK regular supplied metadata except three installation-identity selectors preserved separately; exact 81 dyld SHA overlay from fixed delta; canonical equal-identity alias dedup.','pins':'Tool version and executable hashes reused only from fixed probe/selected-tool metadata; no fresh versions or object hash.','directories_links':'Exact full original metadata pointers and counts retained; not encoded as regular files in the driver JSON.'}})
auth=Path('/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/T03-native-N0-fixed-nine-source-adoption-authorization.md').read_bytes();assert len(auth)==5965 and sha(auth)=='a783158a57df85f892da17021c1861ebdad5aab91a1bc458f6cc3ba83db0e405'
with (D/'authorization.md.raw').open('xb') as f:f.write(auth)
index=f'''# 固定fb40供应元数据派生候选

SDK与resource两份完整 `roots + files` 四pin JSON已生成，供根后续审批；**toolchain、execution、Node、Windows均未采用**。本任务只读固定Git JSON/JSONL/文本，未重读/hash SDK、cache、大实物、归档或任何工具，未新probe、运行driver、解析新源码/runtime或改lock/旧证据。

源固定 `{FB}` 的109个tool-supply文档；实际消费body的ref/path/bytes/SHA/Git blob与派生规则见[source-bodies-manifest.json](source-bodies-manifest.json)。既定driver为`{DRIVER}`，只读其现有schema/env字面值。

- [SDK清单](sdk-files-inventory.json)：**33464 regular**、931393813B供方对象，JSON **{sdkPin['bytes']}B**，小于16MiB/50000；canonical root `{SDK}`。无删项、无截断。
- [Resource清单](resource-files-inventory.json)：**{len(resourcefiles)} regular**，JSON **{resPin['bytes']}B**；含全部8839 CMake regular、compiler resource/include/已定位工具runtime、81个完成cache身份及原map，合法0B hello.f保留。按记录的canonical realpath去重且同身份需bytes/SHA一致，不是重新测实物。
- [Darwin锁形候选](darwin-toolchain-candidate.json)保持当前schema，approval=false/reference=null；不写实际lock。[目录/链接指针](directory-link-source-pointers.json)保原全type记录与隐式容器；root只是文件allowlist的containment，不授新扫描范围。
- [实际工具/SDK/条款映射](tool-routing-sdk-terms.json)：cmake/c/cxx用原真实探针pin；make/git优先固定Developer/usr/bin实际backend，另列/usr/bin Apple dispatcher及其版本来源。未把相同dispatcher SHA当backend证明，也未新增backend版本探针。linker ld与runtime仅复用已有元数据。
- [环境候选](environment-candidate.json)明确提出未采用的`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`，以及现driver的PATH=/usr/bin:/bin、LANG=C、LC_ALL=C，HOME/TMPDIR由未来精确buildDir派生。**现Darwin schema要求env={{}}，build env又硬编码不承接DEVELOPER_DIR**；侧文列出两处最小未来owner delta，当前没有修改或冒用该环境。

[边界与缺口](coverage-and-gaps.json)分别保留cache嵌入传递、postbuild used、条款、当前实物漂移与未批环境等具体事项。systemLibraries空候选表示没有猜测或新增显式链接库，不能解释为没有隐式系统runtime或豁免根对core链接合同的审批；未加入Linux库或任意系统lib。Xcode/SDK原开发协议和未来分发第三方notices分别列明。Node/Windows/Electron未批，不能据此阻止不依赖它们的core候选准备。

本轮供方body新增读取0B；原累计9745727085B保留，未重置。未commit。所有文件bytes/SHA见[delivery-manifest.json](delivery-manifest.json)。
'''
with (D/'index.md').open('x') as f:f.write(index)
# Static metadata-only checks: schema fields/caps/roots/uniqueness/coverage; no driver execution or source-object reads.
for inv in [sdk_inv,{'roots':roots,'files':resourcefiles}]:
 assert set(inv)=={'roots','files'} and 0<len(inv['files'])<=50000 and len({x['path'] for x in inv['files']})==len(inv['files'])
 for p in inv['files']:
  assert set(p)=={'path','realpath','bytes','sha256'} and p['bytes']>=0 and len(p['sha256'])==64 and any(p['path'].startswith(r+'/') and p['realpath'].startswith(r+'/') for r in inv['roots'])
assert set(darwin)=={'approval','version','generator','executables','resourceInventory','sdk','environment','systemLibraries'} and not darwin['approval']['approved'] and darwin['environment']=={}
verification={'metadata_only':True,'SDK_records':33464,'sdk_regular_declared_bytes':931393813,'sdk_json_bytes':sdkPin['bytes'],'resource_records':len(resourcefiles),'resource_json_bytes':resPin['bytes'],'SDK_no_omission_or_truncation':True,'all_CMake_8839_regular_preserved':True,'legitimate_zero_byte_preserved':True,'completed_81_cache_metadata_overlay_only':True,'canonical_paths_unique_and_in_allowlist_roots':True,'all_inventory_entries_exact_four_pin_fields':True,'within_both_driver_caps':True,'all_new_approvals_false':True,'supplier_body_bytes_read':0,'new_probe_or_driver_execution':False,'old_evidence_and_product_writes':False}
out('verification.json',verification)
names=['authorization.md.raw','derive-candidates.py','sdk-files-inventory.json','resource-files-inventory.json','darwin-toolchain-candidate.json','environment-candidate.json','tool-routing-sdk-terms.json','directory-link-source-pointers.json','coverage-and-gaps.json','source-bodies-manifest.json','index.md','verification.json']
manifest={'generated_utc':datetime.now(timezone.utc).isoformat(),'fixed_source_ref':FB,'candidate_only':True,'records':[]}
for name in names:
 b=(D/name).read_bytes();manifest['records'].append({'path':name,'bytes':len(b),'sha256':sha(b)})
out('delivery-manifest.json',manifest)
print(json.dumps({'SDK_pin':sdkPin,'resource_pin':resPin,'darwin_candidate_pin':darwinPin,'resource_records':len(resourcefiles),'source_bodies':len(sourcebytes),'new_files':names+['delivery-manifest.json'],'manifest_sha256':sha((D/'delivery-manifest.json').read_bytes())},indent=2))
