from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,collections,plistlib,shutil
R=Path(__file__).parent;C=json.loads((R/'run-config.json').read_text());D=Path(C['evidence']);B=json.loads((R/'read-budget.json').read_text());rows=[json.loads(x) for x in (R/'supply-inventory.jsonl').read_text().splitlines()];A=json.loads((R/'cmake-extraction-report.json').read_text());P=json.loads((R/'probe-index.json').read_text());H=json.loads((R/'supply-hash-report.json').read_text());S=json.loads((R/'supply-declaration-final.json').read_text())
# Account earlier supporting source reads explicitly, without rehashing old files or rereading their contents.
extra={'authorization_full_text':6465,'original_archive_member_json_for_first_failure_diagnosis':(Path(C['source_run'])/'cmake-archive-members.json').stat().st_size,'LicenseInfo_initial_read':280,'Xcode_License_initial_and_scope_text_reads':2*163452}
B['supporting_source_read_accounting']=extra;B['read_bytes']+=sum(extra.values());assert B['read_bytes']<B['limit_read_bytes']
groups=collections.defaultdict(lambda:{'entries':0,'regular_files':0,'declared_bytes':0,'hashed_regular_files':0})
for row in rows:
 for g in row['groups']:
  groups[g]['entries']+=1
  if row['type']=='regular':groups[g]['regular_files']+=1;groups[g]['declared_bytes']+=row['bytes'];groups[g]['hashed_regular_files']+=row.get('sha256') is not None
H.update(groups=dict(groups),read_budget=B,remaining_read_budget=B['limit_read_bytes']-B['read_bytes']);H['minimum_additional_bytes_to_hash_all_unhashed_cache_candidates']=max(0,H['unhashed_cache_declared_bytes']-H['remaining_read_budget'])
S['type_counts']=dict(collections.Counter(x['type'] for x in rows));S['final_group_counts']=dict(groups)
(R/'supply-hash-report.json').write_text(json.dumps(H,indent=2)+'\n');(R/'supply-declaration-final.json').write_text(json.dumps(S,indent=2)+'\n');(R/'read-budget.json').write_text(json.dumps(B,indent=2)+'\n')
rootdigests={}
for g in ['sdk-complete','compiler-include-complete','compiler-resource-and-runtime-complete']:
 selected=[x for x in rows if g in x['groups']];raw=''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in selected).encode();rootdigests[g]={'entries':len(selected),'declared_regular_bytes':sum(x['bytes'] for x in selected),'canonical_record_sha256':hashlib.sha256(raw).hexdigest(),'recipe':'Sorted path-order original inventory records; each JSON sort_keys=True,separators=(comma,colon),UTF-8 with newline. Symlinks metadata included, regular files complete sha256.'}
terms={'Xcode_and_Apple_SDKs':{'source':'/Applications/Xcode.app/Contents/Resources/en.lproj/License.rtf','preserved':str(R/'terms/Xcode-License.rtf'),'license_info_source':'/Applications/Xcode.app/Contents/Resources/LicenseInfo.plist','license_info':{'licenseID':'EA2002','licenseType':'GM'},'scope_evidence':'Original installed agreement has Xcode and Apple SDKs Agreement heading, Apple SDK and macOS SDK definitions; full RTF retained.','acceptance_or_legal_adoption_claim':False},'CMake':{'source':A['destination']+'/cmake-4.4.4-macos-universal/CMake.app/Contents/doc/cmake/LICENSE.rst','kind':'BSD 3-Clause; original bytes present in fully verified extracted distribution'},'component_terms_gap':['Separate full GNU Make/Git/other component copying notices were not located in the bounded examined installed documentation directories; version stdout gives GNU Make copyright/copying reference. Xcode agreement preserves its separate open-source component exception; no claim that this substitutes for every component license.','System dyld cache runtime terms were not independently resolved to a complete per-image notice set.'],'no_new_terms_accepted':True}
(R/'terms-index.json').write_text(json.dumps(terms,indent=2)+'\n')
# Candidate only. Parent controls lock and adoption; no actual approval changed.
candidate={'kind':'Unadopted toolchain supply candidate','generated_utc':datetime.now(timezone.utc).isoformat(),'source_authorization_sha256':C['authorization_sha256'],'cmake':{'version_observed':'4.4.4','archive_bytes':89454352,'archive_sha256':A['archive_sha256'],'cmake_path':A['cmake_path'],'ctest_path':A['ctest_path'],'extraction_report':'cmake-extraction-report.json','version_probe_labels':['cmake-version','ctest-version']},'probed_executable_pins':[{'label':x['label'],'argv':x['argv'],'pin':x['executable_pin_before_spawn'],'exit_code':x['exit_code'],'signal':x['signal'],'timed_out':x['timed_out']} for x in P],'supply_root_digests':rootdigests,'observed_tool_metadata':json.loads((R/'observed-tool-metadata.json').read_text()),'overall_supply_status':H['overall_supply_status'],'missing_system_runtime_cache_objects':H['unhashed_cache_entries'],'missing_system_runtime_cache_bytes':H['unhashed_cache_declared_bytes'],'minimum_guard_delta_bytes':H['minimum_additional_bytes_to_hash_all_unhashed_cache_candidates'],'terms_gaps':terms['component_terms_gap'],'root_adoption_required':True,'approvals':{'toolchain':False,'execution':False,'source':False,'bindingMinimum':False,'testAssembly':False},'build_runtime_test_status':'NOT_RUN; exact allowed metadata/version probes only; no configure/compiler-input/link/CTest tests/native/addon/Electron/OS behavior pass'}
(R/'candidate-pins.json').write_text(json.dumps(candidate,indent=2)+'\n')
# Complete inventories are split by record count for review, never truncated. Originals remain in tmp.
parts=[]
for prefix,source,records in [('supply',R/'supply-inventory.jsonl',rows),('cmake-extracted',R/'cmake-extracted-inventory.json',json.loads((R/'cmake-extracted-inventory.json').read_text()))]:
 for start in range(0,len(records),5000):
  name=f'{prefix}-inventory-{start//5000+1:03d}.jsonl';b=''.join(json.dumps(x)+'\n' for x in records[start:start+5000]).encode();dest=D/name
  if dest.exists():raise FileExistsError(str(dest))
  dest.write_bytes(b);parts.append({'name':name,'records':len(records[start:start+5000]),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(R/'inventory-parts.json').write_text(json.dumps({'parts':parts,'supply_records':len(rows),'cmake_archive_member_records':9041,'cmake_implicit_container_records_in_extraction_report':1,'all_records_preserved':True},indent=2)+'\n')
copy_names=['run-config.json','first-failure.json','cmake-extraction-report.json','probe-index.json','observed-tool-metadata.json','supply-declaration-final.json','runtime-load-edges-final.json','runtime-cache-map-evidence.json','supply-hash-report.json','unhashed-system-cache-objects.json','read-budget.json','sdk-settings-observed.json','terms-index.json','candidate-pins.json','inventory-parts.json','extract-cmake.py','extract-cmake-v2.py','probe-versions.py','discover-supply.py','extend-supply-plan.py','hash-supply.py','cache-map-evidence.py','finalize-supply.py']
for name in copy_names:
 dest=D/name
 if dest.exists():raise FileExistsError(str(dest))
 shutil.copyfile(R/name,dest)
for folder in ['probes','terms']:
 dest=D/folder
 if dest.exists():raise FileExistsError(str(dest))
 shutil.copytree(R/folder,dest)
md=f'''# T03 N0 固定工具提取与宿主供应清单

**完整CMake提取核同与13条获准版本/元信息探针成功。SDK/编译器资源逐文件清单完整；整体供应仍未闭合。** 系统runtime cache对象受8GiB累计读取guard阻止，独立组件条款仍有明确缺口。全部审批维持false；未改toolchain-lock或任何产品源码。

受控run：`{R}`。原下载目录保持只读。完整候选值：[candidate-pins.json](candidate-pins.json)；完整原argv/cwd/精确传入环境/预执行真实path和SHA/双流/exit/signal/timeout：[probe-index.json](probe-index.json)及probes目录。每条timeout30s，13条各仅运行一次，均exit0、无timeout/signal。探针环境为明确列出的继承元信息环境子集，PATH沿用原值，没有更改PATH或系统配置。

## CMake原件与提取

原官方归档89,454,352B/SHA `4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305`、原source-index及官方完整checksum唯一basename已重核。按目录、普通文件、已核链接顺序提取；未用extractall。9,041原成员（8,839 regular、189 directory、13 symlink）与实物path/type/mode/link/realpath/bytes/SHA全部一致，声明文件总尺寸252,707,197B。另记录归档未显列的1个必要外层容器，实际共9,042对象；合法0B `Modules/IntelVSImplicitPath/hello.f`保留。原结构/完整CMAKE_ROOT/CTest/许可和dylib都保留。

首轮安全脚本在提取第一个目录前因归档缺省外层容器停止，未写普通文件或运行探针；[首失败](first-failure.json)、原脚本与空目的地保留。第二个全新目的地显式声明隐式容器后完成，未复用失败目录。完整记录：[cmake-extraction-report.json](cmake-extraction-report.json)。仅核同后，固定CMake与CTest各一次`--version`实际均4.4.4；两binary大小/SHA也核同授权固定值。

## 供应清单覆盖与边界

完整声明与范围：[supply-declaration-final.json](supply-declaration-final.json)；清单分片：[inventory-parts.json](inventory-parts.json)，共53,092宿主/精确工具记录，含目录/符号链接/realpath及所有已读取常规文件完整SHA。与CMake及隐式容器合计62,134项，未触200,000项guard。分片没有截断；每片有数量、bytes、SHA。

- SDK整个canonical树52,590项，常规文件931,393,813B；所有headers、modules、framework stubs、SDK库和settings都在树中，逐文件已hash。xcrun观察到的MacOSX27.0.sdk是指向MacOSX.sdk的链接，别名身份也记录。
- compiler resource/runtime整个`usr/lib/clang/21`树380项、80,801,250B；toolchain完整`usr/include`与其指向SDK的C++头链接、固定clang/clang++/ld、make/git、Apple wrapper实际对象及静态Mach-O解析到的落盘dylib都列入并hash。全部同根链接无外部/悬空例外。
- 当前实际版本为Xcode27.1/27A9275、SDK27.0、AppleClang21.0.0、GNU Make3.81、Apple Git2.54.0。只证明获准元信息，不代表macOS15或宿主构建行为。
- 外部系统依赖按静态Mach-O load commands逐边列出：[runtime-load-edges-final.json](runtime-load-edges-final.json)。21个系统install names在具体安装的dyld cache.map里逐名命中：[runtime-cache-map-evidence.json](runtime-cache-map-evidence.json)。map仅为身份/地址文本依据，不代替cache实物hash或其内部传递依赖清单。

## 尚未闭合的精确缺口

[unhashed-system-cache-objects.json](unhashed-system-cache-objects.json)完整列出 **81个** 未读cache对象，共 **7,046,515,706B**。其余当前供应常规文件SHA均完整（含map）。已计供应读取 **{B['read_bytes']:,}B**，8GiB guard剩 **{H['remaining_read_budget']:,}B**；仅再hash该全部候选cache集就至少还需 **{H['minimum_additional_bytes_to_hash_all_unhashed_cache_candidates']:,}B** guard增量，尚不含后续cache嵌入image依赖解释的额外读取。因此本窗未读取这些cache实物，未把部分cache清单冒称完整runtime闭包。未自动扩大guard、重新下载或重算旧对象求绿。

已保存本机适用Xcode and Apple SDKs Agreement原始RTF及LicenseInfo（EA2002/GM）、CMake原始BSD许可位置，见[terms-index.json](terms-index.json)。独立GNU Make/Git等组件完整copying notices和系统cache各image适用条款未在本次有界本机文档查找中独立收齐；保留为条款缺口。没有替用户接受许可，也不把安装/版本探针解释为法律采用批准。

未运行configure/try_compile/编译器输入/link/CTest测试/native/child/FS/addon/Electron/GUI/网络；未改全局安装、代理、证书或安全政策；未commit/push/PR/merge或改Goal。只有版本/元信息探针获得运行实证，完整供应采用及后续构建仍等待根审查与授权。

[evidence-manifest.json](evidence-manifest.json)给出本目录全部证据（自身除外）的路径/大小/SHA；工具二进制仍仅在tmp，SDK未复制。
'''
(D/'index.md').write_text(md)
manifest=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p.name!='evidence-manifest.json':
  b=p.read_bytes();manifest.append({'path':str(p.relative_to(D)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(D/'evidence-manifest.json').write_text(json.dumps({'generated_utc':datetime.now(timezone.utc).isoformat(),'records':manifest},indent=2)+'\n')
print(json.dumps({'evidence':str(D),'run':str(R),'evidence_files':len(manifest)+1,'candidate_sha256':hashlib.sha256((D/'candidate-pins.json').read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((D/'evidence-manifest.json').read_bytes()).hexdigest(),'read_bytes':B['read_bytes'],'remaining_budget':H['remaining_read_budget'],'minimum_delta':H['minimum_additional_bytes_to_hash_all_unhashed_cache_candidates']},indent=2))
