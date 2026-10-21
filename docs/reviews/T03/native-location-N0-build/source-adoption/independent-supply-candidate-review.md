# T03 N0 派生供应候选有限独立元数据审查

2026-10-22；独立 reviewer：`n0_build_review`。

**结论：13件候选的元数据身份、两份清单的派生集合及大小约束可接受；不接收“实际GNU make backend已证明”的解读。make选择链仍是采用前具体缺口，供方和执行不可据本报告放行。**环境patch在本报告中仅按固定proposal审查，不等于审核后续实际应用源码。没有把元数据核同签成构建/OS/native/used依赖通过。

## 范围和固定身份

沿5965B/`a783158a…`九源采用与锁准备授权中的供应候选条款，仅消费固定fb40 Git JSON/JSONL/text；全文读候选index、实际工具/SDK/条款映射、环境及coverage说明，并静态审1401B patch文本。唯一写本报告，没有改原锁报告、候选、原件或产品，没有提交。

派生基线为fe98 driver及source-lock-1的25bc2db3…锁。审查期间owner另授7961窗口并更新了三产品文件；本报告明确不覆盖该新实际环境/供方overlay候选，也不误报当前产品仍为未应用状态。这里固定的是13件派生材料和1401B原proposal，其身份不随随后产品变化。

本 reviewer仅读docs文件和固定Git文本blob，计算元数据身份和集合；未运行derivation脚本、driver、候选注入、--build、probe或业务，未读取/hash实际SDK、cache、工具或归档。不重审R5、九源实现或先前锁审批。

| 候选原件 | bytes | SHA-256 |
| --- | ---: | --- |
| `supply-candidates/delivery-manifest.json` | 2084 | `2b741c1b148fac12199c7602848b5ecf14c72dd38579b9e3247879324a61eb20` |
| `supply-candidates/sdk-files-inventory.json` | 14649771 | `ba16d77b0668329b861290b3ef638818bc4c08b295944d39210323c9cda8d3ff` |
| `supply-candidates/resource-files-inventory.json` | 4717231 | `ea79f0988c55b4dd863ce4b0746013fe422524d27cdff4241aa64c034acd520b` |
| `supply-candidates/source-bodies-manifest.json` | 11895 | `e303eb7067460bf8f5da483d2b66308e64fd84bd51bf379e550391d34fe61859` |
| `supply-candidates/darwin-toolchain-candidate.json` | 3905 | `192f247d0ca519745b8f1c1d34ca6161f2958e2fa5d64297d70bcb38409f7d95` |
| `environment-minimal-unapplied.patch` | 1401 | `fefe12f04574af70d2a3f34927408473447c612d085a01fe171d77610eb90a9c` |

delivery manifest的12条记录全部bytes/SHA与实际docs匹配，另加manifest自身恰13件。source-bodies-manifest的28个消费body、共41928578B，逐一与其声明的fb40或fe98 Git blob核bytes/SHA及Git blob SHA-1相同。fb40固定tool-supply目录实际109路径，未把“消费28份正文”误报成“只保28份来源”。driver来源fe98单列，未以可变工作区充固定来源。

## 两份四pin清单的独立集合核对

从固定11个host供应JSONL、2个CMake提取JSONL及dyld完成元数据重建期望集合，没有执行原派生脚本。SDK只选sdk-complete regular；resource取全部CMake regular及非SDK host regular，三个安装身份plist另保映射，按记录realpath合并别名且重复项bytes/SHA必须相同。原pending81条只在新派生内用固定dyld完成记录覆盖SHA，旧pending原件未改。

| 清单 | regular数量 | 供方声明bytes | JSON bytes | 距16MiB余量 |
| --- | ---: | ---: | ---: | ---: |
| SDK | 33464 | 931393813 | 14649771 | 2127445 |
| resource | 9307 | 7588553773 | 4717231 | 12059985 |

两份files与重建期望集合逐项完全一致，path唯一、已排序，每项严格为path/realpath/bytes/sha256四字段；bytes非负、SHA形状正确，path及realpath都落在声明roots内。两份均低于50000 files及16MiB，SDK无删项或截断。当前JSON比先前纯紧凑内存估算多1B的末尾换行，不影响cap结论。

resource保全部8839个CMake regular、81个精确cache对象及原map，合法0B `Modules/IntelVSImplicitPath/hello.f`恰一项，完整保留。以canonical realpath去重没有丢SHA或把未读对象伪装为已hash；executables中的clang++原别名pin另保留。目录/链接没有混入regular file pins：directory-link-source-pointers保原SDK 10984目录/8142链接、resource目录/链接、CMake189目录/13链接及隐式容器的原始指针/计数，其source part身份可追到固定fb40。roots是确切file allowlist的containment边界，不是授予新扫描或任意文件采用。

## 工具身份核同与make路由具体缺口

cmake/c/cxx候选pins与固定探针元数据逐字段一致；make/git所选Developer/usr/bin文件的bytes/SHA也与原selected-tools元数据相同。`/usr/bin/make`和`/usr/bin/git`共享200560B/34129c71…身份的Apple入口另列，不能当actual backend证明。此前GNU Make3.81/Apple Git2.54.0版本观察来自这些/usr/bin命令；候选保backend_specific_version_probe_performed=false、dispatch_chain_proven_by_exec_trace=false，未发明直接backend探针或exec trace。

**M1：Developer/usr/bin/make的69456B/dc25a33f…固定身份，不足以证明它就是GNU make实际backend。**owner在后续准备时指出该点，本 reviewer随后直接读取固定fb40 `runtime-load-edges-final.json`核见：该文件的arm64静态load edge含/usr/lib/libxcselect.dylib与libSystem；所以“换成Developer路径、hash不同”不能排除继续选择/转发工具的行为。libxcselect依赖本身也不反向证明具体转发目标；不能未经证据就猜另一个make路径。原候选的actual_backend_candidate标签应只按“已固定安装入口候选”理解，真实GNU backend/选择链未证须明确保留，实际采用前由owner另按精确权限补具体证据。该缺口不影响已核文件身份与派生集合，但本报告不以原actual标签签完整工具闭包。

Developer/usr/bin/git为3837392B/acf0f202…，固定load edge包含CoreServices/libz等，与上述make入口情况不同；本审查仍不将静态库表冒充动态exec链路跟踪。后续owner的nm等工具元信息查询不属于本报告，reviewer未执行这些探针。

SDKSettings和SDK terms pin与原host记录完全相符；canonical SDK与xcrun别名分开，ld及runtime仅复用既有元数据。空systemLibraries候选表示没有猜测新的显式系统库，不能推出没有隐式SDK/runtime依赖；后置真实link inputs/used headers/depfiles/import/export仍待相应产物观测，不要求首core前伪造它们。

## 开发条款和供方采用边界

根已认可合法安装的宿主开发使用；候选将原Xcode/Apple SDK开发协议与未来分发第三方notices分开。未齐独立组件/per-image notices记录为具体分发缺口，不能以未穷尽所有系统image条款无限阻止后续由根选择的薄core窗口；也不能用开发安装事实替代实际分发许可/声明审查。本报告不新增法律采用或许可接受动作。

cache身份完整仍不证明内部image传递依赖、跨文件原子快照或实际被某次构建使用。派生body新增读取0B，原9745727085B累计没有重置；后续如真实采用/preflight读取供应物，仍须新精确读取/执行授权和续记费用，不能以元数据清单绕过。没有在此重hash7GB对象“求绿”。

13件固定候选自身的toolchain、environment、Node、Windows approval均false；source/API/testAssembly既有批准属于另一层。coverage列明实物漂移未复核、backend直接版本未另测、内部传递/后置used、分发notices和环境未批准等事项。M1的具体事实应与这些gap一起保留，不以笼统“全系统未穷尽”代替其具体对象和选择链证据。

## DEVELOPER_DIR原proposal的静态判断

环境候选准确描述派生基线fe98：Darwin schema的environment必须空对象，build env硬编码PATH/HOME/TMPDIR/LANG/LC_ALL，不读取DEVELOPER_DIR。固定Darwin锁形候选仍environment={}且approval=false/reference=null，符合当时schema，没有假称环境请求已采用。

1401B patch文本仅提出三writer内窄变化：Darwin环境exact-key集合改为仅DEVELOPER_DIR，强制固定 `/Applications/Xcode.app/Contents/Developer`；build env显式传该固定值，不继承任意ambient环境；CMake在Darwin分支、project()之前比较锁定值和实际环境，缺值/漂移即拒绝compiler probing。Windows环境分支未扩，PATH仍固定，不增任意flags/toolchain file入口。

该原proposal从代码意图看符合最小环境delta；reviewer没有apply、没有验证补丁上下文可应用性、configure或故障注入。正式应用后的实际三源码和锁需按新固定候选单独审，不能以本proposal判断自动通过。owner已说明后续7961窗口已应用相关delta，本报告不覆盖那份新产品实现。

## 结论边界

两份清单及身份/环境映射可作为候选元数据归档；未发现集合派生遗漏或cap/schema形状问题。M1所涉make实际选择链不在本报告中关闭；工具采用和执行仍待根据具体证据决定。Node/Windows/N1未齐不阻止单独core候选准备。构建、测试、加载、目标OS/native终态、生产接线及原Goal均不在本次通过范围。
