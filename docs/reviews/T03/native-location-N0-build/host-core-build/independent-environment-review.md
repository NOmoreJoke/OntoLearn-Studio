# T03 N0 实际宿主环境与gnumake增量独立静态审查

2026-10-22；独立 reviewer：`n0_build_review`。

**结论：固定 environment-candidate-2 的环境逻辑、既有pins承接及精确gnumake增量在本次静态范围内可接受，无剩余需阻止此候选交付的 P1/P2。M1可在“直接buildTool选择和供方身份”层关闭，不代表GNU make已执行、完整运行闭包或构建通过。**当前审查锁仍未将toolchain/core execution置true；后续精确采用和执行以7961授权为准，本 reviewer不运行这些步骤。

## 精确权限与候选

全文读host-core-build归档的7961B授权，SHA-256 `697ed52b2aab00ba737cb85b61228f65770a16692d44105627db0e47b21dea00`，并核其原字节实际存在于过程ref `c66f6e8ce7fee7f77ed7ed259d0771ef8c8ff278`。该窗只准固定DEVELOPER_DIR/真实工具选路的三writer最小delta，九源严格只读，先独审再仅Darwin/core配置和构建；版本/产物测试运行、try_run/CTest/native/child/addon等不在授权内。

随后全文读1879B gnumake精确补项，SHA-256 `2279b03c9acd0d969c6e1ea14cbe22f6c3cd84463e099fb43c102d0af20a041b`。它和3210B静态pin原件实际存在于后继ref `d6ed4e4bb9401ff310337937acd3196b9392e2fa`（parent c66）；补项只准固定路径的一次身份/静态元信息，不准版本执行、/var/select读取或新目录扫描。

最终定点候选为environment-candidate-2（711B，SHA `6cee288318713cecb5684177329994e22efb87b18ef1bc11fcef250809cbfc7f`）。本 reviewer从实际三产品文件重算，与该记录完全一致：

| 文件 | bytes | SHA-256 |
| --- | ---: | --- |
| `packages/native-location/CMakeLists.txt` | 13648 | `9455d850157fc8dc2480bd50206f83d2b648e8ae690aecc5fd5410c0af3a0444` |
| `scripts/build-native-location.mjs` | 27325 | `14e15fdf74f5ec57688fb15ff4218f856737bd4d15ff9ac7b10dd3c629c369ae` |
| `packages/native-location/toolchain-lock.json` | 9115 | `9d17ad269029c2b91060e67ced6ccc34b5f69841a62ca9a58ec865d32d5547c2` |

candidate1的9140B/7b6d0f50…锁及make selector gap保留为历史；审查过程中发现实际已切candidate2后，仅按新1879授权作有限pin增量，不给变更后的工作区签旧身份。候选1/2的CMake和driver相同，环境代码不重复全审。

## 实际环境差异和前门

对照固定fe98，driver仅三处差异：Darwin environment的exact-key集合由空改为仅DEVELOPER_DIR；显式要求值精确为 `/Applications/Xcode.app/Contents/Developer`；未来build的固定env对象加入这个已校验值。删去这三处精确差异后，driver逐字回到fe98，故本次没有同时修改CLI、JSON重复键/未知字段校验、审批/pin前门、固定argv、shell:false、parallel2、timeout或R5生命周期。

环境没有任意ambient spread；Mac PATH仍/usr/bin:/bin，HOME/TMPDIR仍精确buildDir，LANG/LC_ALL仍C。不接受用户任意DEVELOPER_DIR、CFLAGS/CXXFLAGS、toolchain-file、source或额外CLI覆盖，Windows环境集合未扩。供方pins和正式审批仍由原检查决定，添加固定环境不代替输入核验。

CMake仅在Darwin分支加入5行：读取锁DEVELOPER_DIR、固定字面值比较、实际环境与锁值比较，不同即FATAL_ERROR。这段实际位于project()前；删去它后CMake逐字回fe98，原source/toolchain/execution审批、所有文件pin/inventory/SDK/许可门均保留。没有通过环境delta提前compiler probing，Node/Windows或其它component没有放宽。

锁相对c66保存的source-lock-1，仅darwin-arm64 toolchain候选字段变化；把该对象替回即可完整回原锁。Darwin对象精确等于此前已独审候选加固定DEVELOPER_DIR，再换成下述gnumake buildTool和资源manifest。source/contract/ac37批准及九pins未改，Windows/Node字段未改。当前两toolchain、Node、WindowsAddon和全部六execution仍false/null，没有用“供应候选已齐”暗设complete或执行许可。

## make M1与精确gnumake补项

旧Developer/usr/bin/make身份69456B/dc25a33f…真实，但实际nm原件含xcselect调用，已固定字符串含make.wrapper.c、wrapper_invoke_xcrun及usr/bin/gnumake。单靠路径/不同SHA不能把它认作最终GNU backend，原M1成立。记录中出现/var/select/make字面值不等于授予读取/使用该selector。

新1879授权直接采用该已知字面值所指的唯一对象：

`/Applications/Xcode.app/Contents/Developer/usr/bin/gnumake`

记录pin的path=realpath、206624B、SHA-256 `67e9807088cb4fdc58e2a3b3406e5dea7cb1611c7ce9ef17fc3373cfcc4cf525`，位于原Developer根内。静态pin原件3210B，SHA `2620f287bc6de938f0745f1349e72f72c6f623db35f636ba1c59919ad9565adc`，与d6ed Git逐字核同。其lstatBefore六字段和lstatAfterEqual=true为实施者实测记录；没有单独序列化after全字段，reviewer不冒称已由两套原始stat独立逐字段复证，更未重读实物hash。

读取已保存file/otool-L/nm-u三个原argv、cwd/环境、固定工具身份、双流及结果，均exit0、无signal/timeout、stderr空；file为Mach-O arm64，otool仅列libSystem.B.dylib，nm-u无xcselect。另有GNU Make格式字符串记录。这些是该对象的静态依据，不是执行gnumake或版本探针，也不把“无xcselect undefined”扩为任意动态行为都已穷尽。

采用其批准绝对路径为CMAKE_MAKE_PROGRAM/buildTool，可以避免本次依赖make wrapper、PATH或/var/select选择最终GNU对象。M1的具体工程选择缺口因此在candidate2关闭；future recipes的实际编译/链接输入和行为仍由精确构建输出观测。

新 `gnumake-resource-inventory.json` 实际4717464B，SHA-256 `42c30336dbcc6444222f2d2b3760fef04df7a0ec7c236ef849a0f76e7a2caa19`。本 reviewer从docs重建对比：roots与原9307资源清单完全相同，全部原pins及0B hello.f保留，只增加上述gnumake一项，排序/去重后恰9308，声明bytes为7588760397，符合原值加206624。仍低于16MiB/50000，没有扫描或加入其它backend。lock仅将buildTool换为该pin、resourceInventory换为这个新manifest pin；没有改CMake/driver代码来绕输入门。

## 完整12范围与已有静态检查

逐九源核current bytes/SHA与5965授权清单、a026 Git字节完全相同；T03未修改I06原header/core/backend/binding/wrapper/tests。相对5f的apps/packages/scripts/tests集合仍精确九源+三writer=12，未仅统计当前平台TU。此前ABI原6a合同、实际b1c九源来源及ac37静态合同审批各层保持。

candidate1中两条真实Node --check、Prettier --check的双流与exit0记录已读，driver在candidate2未变。格式原件中的锁当时为candidate1，不能据此谎称candidate2新锁或后续批准锁已跑过同一检查；本 reviewer只静态解析候选2 JSON并核精确对象delta。实施者应按当前最终锁的必要变化真实记录对应格式/静态检查，不需无变化重跑六verify-only造成重复大物读取。

本 reviewer仅执行文件/Git/JSON/hash元数据核对，未运行driver、probe、nm/file/otool、构建、注入或任何供应实物重hash；没有复审未变I06/R5全实现。唯一写本环境报告，不改旧报告、源码、锁或原件。

## 接收边界

candidate2环境支持和精确gnumake供方增量可接收；正式采用仍须按7961将仅Darwin toolchain及Darwin/core execution指向实际归档授权的真实ref/path/SHA映射，其他审批保持false。d6ed包含补项且继承c66，不能用假ref或原6a ABI ref替代执行授权。授权允许在这些前置成立后继续原单次core构建，不需要每条常规回执重复停等根；本报告本身不声称该执行已发生。

当前没有configure/build/try_compile或产物运行证据。后续构建阶段最多32GiB/200000项的实际读量与原供应阶段9745727085B分账续记，不清零；实际used/新输入、产物架构与min15参数、系统/第三方依赖均按输出审，不先伪造也不因未穷尽全部系统image而无限阻止薄core。任何新未批对象或I06编译诊断按原责任返回根/唯一owner，T03不改九源消错。成功也只可built-unverified/NOT_RUN，测试、native/child、目标OS、生产位置及原Goal等门保持。
