# T03 N0 三构建源码独立静态审查

审查日期：2026-10-22。审查者：独立 agent `n0_build_review`，与三份产品源码的实施者分离。

**结论：候选 4 在本次三 writer 的静态交付范围内可接受；此前发现的具体问题均已静态关闭，未发现仍需阻止此静态交付的 P1/P2。此结论不批准 configure/build，也不表示 N0 构建、目标运行或资源终态通过。**完整批准输入分支仅作代码推演，未伪造已批准锁或九源来执行它。

## 范围与固定输入

审查树为 `.worktrees/T03-native-location-N0-build`，branch `feature/T03-native-location-N0-build`，授权 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。全文读精确授权 `iteration-control/2026-10-21-weekly-release/T03-native-N0-build-source-and-tool-input-authorization.md`（6607 bytes，SHA-256 `3f4c0aba50d613a717b4402a7d982c38aa3f017996667c0cc6ae1aa94ff21977`）；不把旧计划的条件当作新执行许可。本 agent 唯一写入本审查文件，不修改主稿、三 writer、材料、原 I06 源或其他证据，不提交。

候选 4 由 `source-candidate-4.json` 固定；本 agent 从实际文件重算下列 bytes/SHA，与该记录一致：

| 产品文件 | bytes | SHA-256 |
| --- | ---: | --- |
| `packages/native-location/CMakeLists.txt` | 13332 | `81df2fbf6169cfb8d990080cf9f804adc6e275accdfc912f9c334028578d7a5d` |
| `packages/native-location/toolchain-lock.json` | 4624 | `865c7c8ea12a2038437b81fb5718eaa3ce1ff9c3e30709f2ce03029e4456a30f` |
| `scripts/build-native-location.mjs` | 21117 | `cf0ad744bffaa29a7c2b932fa50d55bf4936584c477bf0bb7947ee64a5d04f0b` |

逐字读三源码的候选及后续修订，重点追踪未来 complete/build 分支，而非只看当前 false 门。只读全文读原契约 ref `6a7789bf0c1e5e7b0f25f37c86e0c9d64c6dc20d` 的 `location_abi.h`（13296 bytes，`fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172`）及 `abi-build-handoff.md`（17562 bytes，`8b3ba7c43935fac973a550944f6c2f5f69c94623162b31a75e0da26053ac7134`）。没有复制该头或采用可变 WIP。主交付稿 `docs/iterations/T03/native-location-N0-build.md` 也已读，其 pending/NOT_RUN 口径与本审查范围相符。

## 具体发现与处置

以下是同一交付中的发现和修订，不把候选编号当作固定审查轮数，也不抹去初始问题。

| 编号 / 等级 | 具体反例及影响 | 最终处置 |
| --- | --- | --- |
| R1 / P2 | 初稿异常出口恒报 `processExecution:false`。未来构建已 dispatch 工具后若日志写入等抛错，会掩盖已执行事实。 | driver 使用函数外单调执行标志，dispatch 前置 true，异常出口输出该真实标志；候选 4 保留。关闭。 |
| R2 / P2 | 初稿部分 addon/Windows/header/license 检查在 `project()` 后，直接 CMake 入口可能先 compiler probing，再拒绝缺输入，与先拒承诺冲突。候选 2 又仍漏 resource inventory、SDK 设置/许可/版本等入口闭包。 | 候选 3 将相关审批、五 executable pin、正在运行的 CMake 身份、资源/SDK inventory、SDK settings/terms/version、Win 环境及系统库 pin 放在 `project()` 前。候选 4 保留。关闭；未执行 CMake 语法/配置验证。 |
| R3 / P2 | 仅将 contract 的固定头 SHA 放进锁，并不能阻止未来 source.files[0] 采用另一份头；会出现 verify complete 而 ABI 合同已变。候选 2 的 driver 尚无一致检查。 | driver 在 source 已批准时显式比较 source header SHA 与固定 contract；CMake 同时比较 source pin、contract SHA 和固定常量。候选 3/4 代码均已核见。关闭。 |
| R4 / P2 | 一般 pin 的 `bytes > 0` 被 inventory 逐文件复用，拒绝真实官方同版 CMAKE_ROOT 的合法空文件。现有归档成员记录实际含 `Modules/IntelVSImplicitPath/hello.f`，regular、0644、0 bytes；完整库存据此会被错误拒绝。 | 候选 4 schema 允许安全整数 bytes >= 0；`checkPin` 默认仍要求非空，只有 inventory 逐文件显式 allowEmpty=true。CMake 的 inventory 函数局部允许空文件，manifest/executable/license 仍先要求非空。空文件仍须匹配 actual realpath、bytes 和 SHA。关闭；未做变锁运行实验。 |

实施者另作自审修订，本 agent 静态核见：inputDigest 包含三 writer 字节身份，锁摘要从而包含源和工具 pins；未来 build 使用批准绝对 Git，先检查三 writer+九源 clean、记录真实 HEAD、逐个比对固定 ref Git blob；首失败停止，日志保 status/signal/error 和双流路径。上述均为已写源码的行为设计，不是已执行成功的证据。

## 契约和平台核对

固定 I06 头的 ABI=1、自有 public C 函数与 Windows 调用/导出宏由原头决定，构建供方没有新增私有业务接口。当前 Node-API=3 是交接所列同步候选调用的最低集候选，其中同步 `napi_add_env_cleanup_hook` 属 API3；未用完整九源实际调用集验定，`bindingMinimumApproval` 仍 false。宿主 Node24 的 napi10 和 Electron 普通模块 ABI149 不能证明 Electron 实际 Node-API 版本。Node-API 的 C ABI 稳定也不能扩展为 C++、V8/libuv 或任意外部库稳定。

CMake 精确列九文件，不 GLOB、不自动取源；只编 core 加一个目标 backend。三个组件相互分开：core 不要求 Node/Electron addon 供方；普通 addon 是 core+平台+binding；fixture-addon 再加入原 core test，四 TU 同模块且定义 `NL_NODE_FIXTURE_HOST`，符合单 registry 交接，未产生另一个携带 core registry 的宿主。addon 宏 `BUILDING_NODE_EXTENSION`、`NL_WITH_NODE`、`NAPI_VERSION=3` 明确，core/test 不传播 Node 宏。C++17 必需、禁扩展、PIC、私有 hidden visibility 均明确。

macOS 在 `project()` 前固定 arm64、批准绝对 SDK 和最低15.0；同模块 core TU 也受 PIC。MODULE 的动态宿主符号解析显式 `dynamic_lookup`，最终实际 undefined/export 审计仍待产物。macOS27 宿主/SDK 不等于 macOS15 实机或兼容性证据。Windows 保 MSVC x64/动态 CRT，直接编批准 delay hook，批准绝对 node.lib/delayimp，HOST_BINARY=node.exe 和 /DELAYLOAD:node.exe；没有凭空补 ntdll import 库。真实 Windows SDK、CRT/import 库及适用许可尚未提供批准，不能称 Windows 可构建。

core 的 CTest 注册给原测试绝对 child target 路径和15秒外部 timeout，符合 argv[1] 交接。驱动不执行 CTest 或 addon/Electron 加载。`--hold-until-eof`、fixture bootstrap、TS 真 addon 注入等行为仍属原 I06 源合同及以后受控运行验证；timeout 不能证明 child/owner/native 清理完成。

## 入口、材料与证据边界

CLI 只接受固定 target/component 与恰一个模式，拒绝未知/重复参数。driver 对锁作 exact-key/type/enum/order 校验并拒绝重复 JSON key；未批准源码/供应输入不读取。批准后对固定文件检查 realpath/bytes/SHA，inventory 对 roots、重复路径、越界及逐项 pin 作检查，SDK 清单要求覆盖所选供方 root。当前锁将九源 ref/pins、工具链、SDK、Node 采用、Windows addon 输入及全部执行窗口保为 null/false，未用已有材料静态可得替代 root 的采用批准。

未来 build 先完整只读检查，再创建独占目录，禁止重用已有 cache。argv 固定、shell:false、绝对批准工具和最小/批准环境；不自动联网安装、不承接用户额外 flags。Git 和 configure/build 才位于执行窗口后。成功仅输出 built-unverified；测试 NOT_RUN、实际依赖闭包 PENDING_POST_BUILD_AUDIT。供方 inventory 是构建前对象清单，不是构建后 depfiles、used headers、真实链接输入等观测输出；首次构建不要求伪造后者。inventory 的语法和逐 pin 验证也不能单独证明供应对象已穷尽，未来仍需 owner 审核清单覆盖及后置真实依赖审计。

材料 index 实际为28386 bytes，SHA `e6eea559a28087bebcd965f3632e2be7c8f0a58f3e593f25c5415b067c86e2e6`。本 agent 静态读取 index、下载元数据、库存、许可/版本依据、首次失败及修订记录，并独立核对7项已下载原件 bytes/SHA、官方 checksum 的唯一对应 basename、4头与本机原件字节相同、已保存许可/版本文本的身份。没有再次下载、运行材料审查脚本、提取执行安装树或运行归档内容；归档安全扫描是材料 agent 的静态证据，不冒称本 agent 独立重跑了整份 tar 审查器。

官方 CMake4.4.4 归档89454352 bytes、SHA `4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305`，完整同版 CMAKE_ROOT/CTest 和主许可有静态成员证据；尚未提取为批准工具链，不能称 executable 已供应/运行。Node v24.15.0 的4 API 头及完整 LICENSE 来源、bytes/SHA 有实物证据；不能用 @types/node 或 npm/node-gyp 的许可替代。首次网络/审查失败保留，后续成功不抹去原记录；无 PGP 验签结论。Windows材料仍缺，本范围没有用 N1/SQLite/Python/VFS/B-R 缺口阻止 N0 三源码交付。

## 实际验证与后续门

本 agent 仅作文件/Git/JSON/hash和源码阅读，不运行 driver、CMake、compiler、try_compile、CTest、native/child、FS 实验、addon/Electron、GUI 或 Keychain。主 agent 的 `static-validation.json` 与双流记录显示：候选4 Node --check/Prettier --check exit0，六 target/component 的真实 verify-only 均 exit2/incomplete；三 writer 前后身份一致、九源路径仍缺、没有 native build 目录。这里是对已有记录的审阅，不是本 agent 重测或构建成功。

全部审批 false 的当前路径可以准确拒绝/报告缺口，不证明未来 complete 分支已在真实供方上运行。没有执行 CMake parser/configuration，不能消除此边界；源码推演也不能证实实际编译/链接/导出/API 最低集、目标 OS、Electron runtime、native release/cleanup 或 timeout 后的进程树排空。未来工具超时/失败仍应保首失败与未知资源状态，不能由构建供方日志自证 drain。

因此，本次仅关闭三 writer 的独立静态审查。下一窗口仍需根分别核验固定九源及采用、真实工具/SDK/许可清单、所选 component 和宿主的执行批准；测试/加载另需精确运行许可。生产接线、D2重测、N1、CI、合并及原 Goal 完成均不在本结论内。
