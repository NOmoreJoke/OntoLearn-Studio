# I06 N0 完整源码交接

2026-10-22。本件交付六个产品和三个测试的待构建源码，不构成 N0 技术通过、构建采用批准或运行授权。所有产物仍为 held-object-only，productionAdmission 固定 unsupported。

## 精确采用对象

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。
- branch：`feature/I06-native-location-N0`；批准 base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 首 ABI 过程 ref：`6a7789bf0c1e5e7b0f25f37c86e0c9d64c6dc20d`，header 13296B，SHA256 `fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172`。
- 首完整受审源码：`4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8`；三份首审原文及首格式失败完整保留，不把此版本称通过。
- 修复后完整源码 ref：**`fa1a7e4155f3afee4a1b3409f9ab8804cc620186`**。九件 bytes/SHA 全量见 `source-text-check-r2.json`。其后的交付提交仅过程文档，不改九件源码；最终 `manifest.json` 会核当前文件等于该固定源码 ref。
- 本树 AGENTS 15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 是保护 dirty，不 stage。BM64、624收口、9ff1的18件方案逐文件同原字节，四个旧树 HEAD 不变，证据 `protected-work-preservation.json`。

## T03 的完整接口输入

public C ABI1 沿用首过程 header；8 struct 的每字段 expected offset/size/align、fixed-width/cdecl/noexcept、caller 分配输出、borrowed 原件及 native duplicate 分责、有限错误/预算/TTL/close/sole-reaper 均已固定在 header 与 `abi-build-handoff.md`。`public-symbol-source-check.json` 仅源码枚举匹配 11 core C 定义和条件 native-host 第12入口，不是实际导出/链接证明。私有 detail 和 fixture bootstrap C++ 符号应隐藏。

首 ABI 过程时 Node WIP 的11API枚举已经过时：最终 Node 源码实际是以下12项，新增 UTF16 严格读取；header 未改变。最低 **N-API3** 来自同步 env cleanup hook，无 async cleanup hook/async work/TSFN，不要求8。T03须用它实际固定的 headers 展开 `NAPI_MODULE(i06_native_location, init)` 并验证所有注册/版本符号，不以运行 Node 的 N-API10 或宏名代替 Electron 链接/加载证据。

```text
napi_add_env_cleanup_hook, napi_create_external, napi_create_object,
napi_create_string_utf8, napi_create_uint32, napi_define_properties,
napi_get_cb_info, napi_get_value_external, napi_get_value_string_utf16,
napi_get_value_string_utf8, napi_set_named_property, napi_typeof
```

准确的私有 Node 表是 abiVersion1、fixtureBound1、productionAdmission0 和八个同步方法 root/directory/file/observe/release/snapshot/revoke/close。普通 addon 只有三个 flags，fixtureBound0，无 JS owner/path/fd/PID bootstrap。trusted native host 用同一 image/registry 内的 `nl_node_bind_fixture` 装配原 owner。TS shape/WeakMap 不认证 arbitrary JS 为 native，也不制造 LocationLease。

构建闭包仍仅由 T03 写 `packages/native-location/CMakeLists.txt`、`packages/native-location/toolchain-lock.json`、`scripts/build-native-location.mjs`，本树三路径未写入。T03 当前 onlydocs，不因本件自动获得实际构建采用权。精确未结输入为：

1. macOS15 arm64、Windows11 x64 的编译器/SDK/部署目标/C++17/CRT/线程库及固定来源；Win feature macros、NtCreateFile/Ntdll、ACL/Advapi32、CompareObjectHandles/Kernelbase、普通 Kernel32 闭包；mac O_EVTONLY/openat/F_DUPFD_CLOEXEC/ACL 声明及系统库。header asserts 尚未实编。
2. NAPI_VERSION3、实际 Electron 与 Node headers/runtime 的版本和来源、Win node.lib/导入与 delay-load 装配、目标 architecture、实际模块注册/导出、普通 addon 与测试 addon 的分离。PATH 缺 cmake/ninja 不用手工绕锁补编译。
3. 单 registry：测试 `.node` 将 core、目标 platform、node_binding、core_test 四 TU 放进同一目标，定义 NL_NODE_FIXTURE_HOST+NL_WITH_NODE。core_test 此模式只有 private fixture bootstrap、没有 main；不要 host 和 `.node` 各复制 core 后传相同数字 owner。普通 addon 不带测试宏。
4. ordinary core executable 只有 main，唯一 argv[1] 为 CMake TARGET_FILE 的 child_probe 绝对路径；child_probe 只接受 `--hold-until-eof`。usage64、失败1、unsupported host77、正常0；77可标 skip，不能计目标平台绿。CTest 外层15s只防失控，不是 drain 事实。
5. TS 真实组只从显式绝对 I06_NATIVE_LOCATION_TEST_ADDON 装载已构建测试 artifact；缺输入 skip，synthetic 组仅投影机制。测试 addon 通过真实 OS-temp fixture 和 held anchor 创建 owner，不添第十个 helper 文件。所有测试本轮均未执行。
6. trusted host 必须独立提供 retained 期间依赖 image 存活/pin 闭包及 Node env 线程约束；当前源码没有 self-pin。同步 env hook/static registry 不证明库保活。测试 fallback close 非OK abort不等 release receipt，不代替普通 host pin。

## 静态交付与实际未运行项

独立首审确认四项 P2（cleanup 槽、ACL unknown与FD首次close、下一dispatch TTL、test fallback owner），另有 FIFO P3 与 signal.h 声明依赖；原文、作者处置及三份新固定 ref 复核均保留。源码问题的关闭只以各自复核原文为准，不推导真实 OS 故障已发生或实际清理已通过。

| 修订 ref 的独立复核原文           | bytes | SHA256                                                           | 源码结论                                             |
| --------------------------------- | ----: | ---------------------------------------------------------------- | ---------------------------------------------------- |
| independent-source-followup-r2.md | 10110 | f6f889d85aba8e5ce02cfa8b46a8f682868b6c6357646fd75c21a91aec292f2b | 三P2/FIFO P3及IF-01相关修复关闭，无新增产品阻断      |
| platform-source-followup-r2.md    |  7909 | e8ac4025610782ae798dde50f3d8e4e10ddefc9001622f6cd4ff5d9fff7f1e9e | 两P2/C-1/FIFO源码关闭，无新增确定P1/P2               |
| interface-source-followup-r2.md   |  6501 | da8dfbff8dbca848cbba33400e461186b83bbc0a18045876dac034be9615f250 | IF-01源码关闭，image生命周期文案准确，无新增接口问题 |

总审提出的非阻断说明精度已在主文档更正：Mac先dup再fstat，Windows先核borrowed pipe再dup。九件源码无后续改动；这些过程文档修订不冒充新产品复审。

实际执行了 Git/hash/UTF8/空白/预处理条件平衡/公开符号文本枚举、既有 Prettier3.9.10，以及 TypeScript5.9.3 createSourceFile/parseDiagnostics（两份TS为0语法诊断，后续字节未变）。没有完整 TS 类型检查；没有 C++ syntax-only 或任何编译、测试执行、产品 import、addon load、native/FS/child 实验、工具或依赖安装。首 Prettier exit1 原日志和三份 preformat 原件在案，修复后 TS2+主文档 check0；独审原文保持原字节，不强行重格式化。

未来精确运行窗仍须实际记录正向 metadata、member/ancestor/root普通替换与rename分支、hardlink/symlink/reparse、partial child/sole-reaper、真实close和未知、取消/TTL/晚返、原inflight/有限cleanup与host image生命周期。现 revoke 并发测试只是非确定表征；未覆盖的确定 fault/TTL 边界不能用注入或 mock 充真实 OS 证据。首 unresolved open会封全局新接纳保原一槽责任，并留另一槽给有限cleanup；不实现该未知的恢复或卸载认证。publish一直unsupported。

N1 SQLite/VFS/SHM/所有附属IO、跨崩溃oldholder、fresh/历史/B-R耐久、T01消费/dispatch/scope/永久排空、公开首IO、父I06/57P0、指定双模型同版/CI/正常develop合并与远端门仍未通过。本次不改原 Goal，不push/PR/merge，不向其他聊天派任务。
