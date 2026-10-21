# T03 N0 九源采用后的锁增量独立静态审查

2026-10-22；独立 reviewer：`n0_build_review`。

**结论：source-lock-1 静态可接受，未发现本次锁增量仍需修正的 P1/P2。九源身份、审批引用与12产品/测试范围相符，六份只读输出准确保持 incomplete。此结论只接收源采用及静态合同审批，不批准工具/Node/Windows供方、configure/build、测试或加载。**

## 精确授权和审查范围

全文读根5965B授权 `T03-native-N0-fixed-nine-source-adoption-authorization.md`，SHA-256 `a783158a57df85f892da17021c1861ebdad5aab91a1bc458f6cc3ba83db0e405`，及3048B清单 `T03-native-N0-nine-approved-source-inputs.json`，SHA-256 `d48ea0bcb4ae6acb2f6e7f2b8691c5c620ec125c30e5f44826cc60ac08de1ee7`。它们明确只准九原Git字节采用和既有lock的source/contract批准；I06九源在T03仍只读。未扩为R5复审、完整I06实现审查、工具实物再hash或任何构建运行。

本 reviewer只读文件/Git/JSON并计算这些固定源码及元数据身份，没有运行driver或重复检查；唯一写本报告。没有修改九源、CMake、driver、lock、供应候选/原件或旧报告，也未提交。

实际采用树 `.worktrees/T03-native-location-N0-build`，branch `feature/T03-native-location-N0-build`；相关ref角色如下：

| 角色 | 固定ref |
| --- | --- |
| 原base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |
| I06九产品来源 | `b1c54c3de840e657aba07906587681f6415085d6` |
| I06完整过程后继 | `0534ec27a946b903decd72bd10067583f0615afc` |
| T03单独九源采用 | `a026322ad287bfc42cd24ac7a64e78d48046e96f` |
| T03保存授权/清单/逐件回执的过程 | `ac37ebf4d0fceaa2aabd9c06e33cc4c6ede26c47` |
| 未变构建源码/R5基线 | `fe98dab02375362fcc07ca9bb309de17b558fcf2` |

## 审批引用、锁delta与九身份

实际候选lock为5336B，SHA-256 `25bc2db37dc061b6ec736397d7d128576d1747a8954d178a4686d6d71278dc93`，与lock-candidate-1记录相符。对比fe98中的旧4624B/`865c7c8e…`锁，全部变化仅为source.ref、九源bytes/SHA，以及source.approval、bindingMinimumApproval、testAssemblyApproval的false/null改true/ac37；其它字段没有更改。

ac37过程提交实际含与根原文逐字相同的5965B授权、3048B清单和5122B逐件采用回执（SHA `955d43200b4032c86c7ffaf3ba640c0d2e57cf5b5c334e1532092f33b5c1712a`）。因此三个approval.reference可从固定Git身份解析到精确授权，而非借任意40位ref当批准。

本 reviewer逐九件读取current字节并核bytes/SHA，再分别与b1c、0534、a026、ac37的Git blob逐字比较，全部相同；锁中九项顺序及pins也与根清单逐项相符。单独a026的diff-tree恰九路径，没有whole-commit采用。

| 九源路径 | bytes | SHA-256 |
| --- | ---: | --- |
| `packages/native-location/include/location_abi.h` | 13296 | `fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172` |
| `packages/native-location/src/capability_core.cc` | 17304 | `eae2d2dcf4ccf1f648dbec5fdd0424c0a2dac31a94a45d493e819948f2309319` |
| `packages/native-location/src/platform_macos.cc` | 7675 | `28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be` |
| `packages/native-location/src/platform_windows.cc` | 12506 | `bcf474ca9d9e5ce4efdf06284dd71b9504c5e69027d3a53c96fa7df56bc2b4c4` |
| `packages/native-location/src/node_binding.cc` | 13163 | `e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383` |
| `apps/desktop/src/main/security/native-location-owner.ts` | 12496 | `e354b0830469647d70690f3e1d6e567c816f70cbbbe5c211dabba817fa7cc8d0` |
| `packages/native-location/tests/location_core_test.cc` | 29666 | `7d0965cafe74fcbaa0d6c0fcf57078d2969fd3f243d7a14d1e7244329017bcdc` |
| `packages/native-location/tests/location_child_probe.cc` | 380 | `041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c` |
| `tests/unit/i06-native-location-owner.test.ts` | 8460 | `e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04` |

contract.ref仍为 `6a7789bf0c1e5e7b0f25f37c86e0c9d64c6dc20d`，只标识未变ABI原合同，header SHA及handoff SHA未变；没有把6a当作完整九源来源。实际source.ref正确指向b1c。

bindingMinimumApproval=true对应根本次对实际12个API调用、最高门3的静态接收，不是旧十一候选枚举。独立从已固定binding仅提取调用拼写，12种与候选记录相符，包含先前遗漏的napi_get_value_string_utf16；本审查不重新替代根33160B/`c3cfa6ce…`控制审及官方头逐符号证明，也不把静态门3推成运行时采用/编译/导出/加载通过。testAssemblyApproval=true同样只标静态core绝对child TARGET_FILE及fixture四TU单module合同，未证明实际链接单registry或host image pin。

## 12产品/测试范围与未越门

相对base、限定apps/packages/scripts/tests的当前diff恰九源加原三构建=12路径，与adoption-receipt的完整路径表相同；两个backend及TS wrapper/test均包含，不只报当前平台的编译TU。CMake实际13332B/`81df2fbf6169cfb8d990080cf9f804adc6e275accdfc912f9c334028578d7a5d`、driver实际27002B/`d1ddcbd699be1feccd85a39ec583bcab6563d08597f70df5ad430f9879f06714`均与fe98逐字一致。

toolchains两目标、node、windowsAddon和六个execution的approved均仍false，对应未获采用的引用为null。未因为源/API/拼装静态批准而暗设完整锁。Mac环境schema也仍为原空字段集合，本轮没有承接或绕过DEVELOPER_DIR；供应候选及任何后续环境delta需要另批，不能通过锁本轮批准悄悄放行。

## 已有检查原件的准确性

读取 `source-adoption/static-validation.json`（7989B，SHA `469ba9008b257822b0c0c90b37715c5a5e07b532c096124b61e3bcb0fc40f69b`）及8条检查完整双流；没有重跑这些命令。记录显示Node --check和锁Prettier --check各exit0，六个实际--verify-only均exit2。16份stdout/stderr原件存在，stderr全为空；六份JSON为status=incomplete、mode=verify-only、processExecution=false、inputWrites=false，lock SHA及三writer身份均匹配本候选。12个当前产品/test pins独立重算与validation一致；“before/after全同”本身仍按实施者保存的历史检查记录陈述，不冒充reviewer重跑。

| target/component | 输出缺口数 | 实际缺口类别 |
| --- | ---: | --- |
| darwin-arm64/core | 2 | toolchain/SDK采用；该component执行窗口 |
| darwin-arm64/addon | 3 | 同上；另Node头/许可采用 |
| darwin-arm64/fixture-addon | 3 | 同上；另Node头/许可采用 |
| win32-x64/core | 3 | Windows工具/SDK采用；执行窗口；宿主不匹配 |
| win32-x64/addon | 5 | Windows工具/SDK、Node采用、Windows import/hook/delayimp、执行窗口、宿主不匹配 |
| win32-x64/fixture-addon | 5 | 同上 |

六输出不再保留source、bindingMinimum或testAssembly旧缺口，符合本次批准；core没有混入Node/Windows addon要求。尚未采用的供方明确not read，不为了检查锁去重复hash SDK/cache；Darwin core仍只缺准确两门。incomplete/2是拒绝缺项的真实结果，不是构建Pass。

## 结论边界

本次锁采用审批与精确九源身份可接收；I06维护归属不变，后续源问题必须返回唯一owner，不由T03改原件消错。未运行正常产品测试、CMake/configure/try_compile/compile/link、CTest/child/native/FS实验、addon/Electron或任何未来完整分支，也未重读大供应物或新探针。R5和未变三源码不在本次重审范围。

九源和静态合同门已登记，不应继续误报缺源码；真实工具链采用、许可/静态传递解释、component执行窗口、后置used闭包/产物/运行/目标OS及生产位置仍按各自证据和授权推进。本审查不关闭D2、父57P0、指定双审/CI/develop或原Goal。
