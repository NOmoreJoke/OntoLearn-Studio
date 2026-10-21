# N0 ABI1：T03 source/static 构建交接

2026-10-21。本文冻结可供 T03 准备 onlydocs 构建方案的 header 布局和当前 Node API 枚举，不等待九件产品/测试全部成熟。这里只记录源码预期：没有编译、链接、加载、测试、安装或 native/FS/child 运行证据，不称 N0 通过。真正采用与运行仍需根的后续精确授权。

## 1. 固定输入与责任

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`；branch：`feature/I06-native-location-N0`；本次已知 base/HEAD：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。root 将另给仅成熟 header/docs 的实际过程 ref；本文不把工作区 hash 冒称已提交 ref。
- `packages/native-location/include/location_abi.h`：13296B，SHA256 `fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172`，下称 H。全文读回，以下 ABI、宏及布局绑定此原字节。
- `packages/native-location/src/node_binding.cc`：12098B，SHA256 `7071905543e9dfbd6cf4467d19b5d7bd055a5e596d6370f9aad5be0167b06c57`，下称 N。仅为当前 API 枚举输入，不是本轮单独冻结的完整 addon 产品候选，也不授权 T03 复制未固定源码运行。
- N0 授权 `I06-native-N0-source-implementation-authorization.md`：6089B，SHA256 `fc4a74b81530197a3aa38d0bcc5027d952d83c64d7f0a6cd5be2abdd3c9ce4ee`。root 为六产品与三测试唯一 writer；T03 的三拟构建路径仍须其实际接收/精确授权。本文只新增此一文档，不改 H/N、原预审或其他产品。
- N0 仅受控 native fixture 对象、metadata、有限 owner/cap/child 生命周期。没有正文/create/publish/bootstrap opener、SQLite/Python/VFS、生产 LocationLease 或 renderer 入口。

## 2. C 符号、宏和调用约定

全部 public C 函数返回 `nl_status`（`uint32_t`），C++ 编译时 `extern "C"` 且 `NL_NOEXCEPT=noexcept`；C 头消费时 `NL_NOEXCEPT` 为空。Windows `NL_CALL=__cdecl`，其他目标为空。所有声明/定义/消费者均须采用同一调用约定；不得跨边界抛 C++ 异常。

核心11符号的完整声明为：

```c
nl_status NL_CALL nl_fixture_owner_create(const nl_fixture_anchor*, nl_owner_ref*) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_root(nl_owner_ref, nl_cap_ref*, nl_metadata*) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_acquire(nl_owner_ref, uint32_t expected_epoch,
    nl_cap_ref parent, const char* component, uint32_t component_bytes,
    uint32_t kind, const nl_identity* expected, nl_cap_ref*, nl_metadata*) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_observe(nl_owner_ref, nl_cap_ref, nl_metadata*) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_release(nl_owner_ref, nl_cap_ref) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_snapshot(nl_owner_ref, nl_snapshot*) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_revoke(nl_owner_ref) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_close(nl_owner_ref) NL_NOEXCEPT;
nl_status NL_CALL nl_fixture_child_adopt(nl_owner_ref, const nl_fixture_child*,
    nl_child_receipt*) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_poll_children(nl_owner_ref) NL_NOEXCEPT;
nl_status NL_CALL nl_owner_publish(nl_owner_ref) NL_NOEXCEPT;
```

这些声明均带 `NL_API`。条件 `NL_WITH_NODE` 另包含 `node_api.h`，公开第12个 native-host C 入口：

```c
nl_status NL_CALL nl_node_bind_fixture(napi_env, napi_value, nl_owner_ref) NL_NOEXCEPT;
```

宏构建责任：

- Windows shared producer 定义 `NL_BUILD_SHARED`，`NL_API=__declspec(dllexport)`；消费者定义 `NL_USE_SHARED`，`NL_API=__declspec(dllimport)`。二者不要同时定义，静态消费者不凭空设置 import/export。
- GNU-compatible 目标的 `NL_API` 显式 default visibility。T03 应隐藏未标 public 的 `i06_location_detail` 符号；不能全导出内部平台入口，也不能把上述 ABI 及必要 Node 注册符号隐藏掉。
- core-only 源码/测试不需要 `NL_WITH_NODE` 或 Node headers；addon 与调用 Node 专属 C 入口的 native host 才需要对应定义和固定 headers。
- H 的 private C++ namespace 不是 public C ABI。`handle/child_handle/close_result` 及 `platform_*`、`valid_component` 不应成为供外部消费的 ABI；不得因它们放在同一授权头内就扩大导出集。
- H 不定义跨进程 wire 格式，struct 不能按裸 bytes 作为外部消息/持久凭据使用。当前目标要求64位 intptr_t；目标架构、编译器、SDK、CRT、C++标准和实际导出列表由 T03 固定到其来源/锁，不能依赖宿主默认布局。

## 3. 八个 public struct 的完整预期布局

下列数字单位为 byte；每个字段均列 `sizeof / alignof / offsetof`。这些是 H:180–234 的源码 static_assert 所表达的预期与字段类型直接推导，**尚未由编译器验证**。不得启用改变布局的 pack；T03 后续须保留这些断言并记录目标编译实证。

### nl_owner_ref：sizeof=8，alignof=8

```text
field       type            sizeof  alignof  offsetof
value       uint64_t        8       8        0
```

### nl_cap_ref：sizeof=16，alignof=8

```text
field       type            sizeof  alignof  offsetof
owner       uint64_t        8       8        0
slot        uint32_t        4       4        8
generation  uint32_t        4       4        12
```

### nl_identity：sizeof=24，alignof=1

```text
field       type            sizeof  alignof  offsetof
volume      uint8_t[8]      8       1        0
file        uint8_t[16]     16      1        8
```

### nl_metadata：sizeof=48，alignof=8

```text
field             type          sizeof  alignof  offsetof
abi_version       uint32_t      4       4        0
kind              uint32_t      4       4        4
identity          nl_identity   24      1        8
link_count        uint64_t      8       8        32
acl_checked       uint32_t      4       4        40
held_object_only  uint32_t      4       4        44
```

### nl_fixture_anchor：sizeof=32，alignof=8

```text
field               type          sizeof  alignof  offsetof
abi_version         uint32_t      4       4        0
platform            uint32_t      4       4        4
borrowed_directory  intptr_t      8       8        8
reserved            uint32_t[4]   16      4        16
```

### nl_fixture_child：sizeof=56，alignof=8

```text
field             type          sizeof  alignof  offsetof
abi_version       uint32_t      4       4        0
platform          uint32_t      4       4        4
borrowed_process  intptr_t      8       8        8
child_pid         int64_t       8       8        16
borrowed_pipes    intptr_t[2]   16      8        24
reserved          uint32_t[4]   16      4        40
```

### nl_child_receipt：sizeof=24，alignof=4

```text
field        type          sizeof  alignof  offsetof
abi_version  uint32_t      4       4        0
child_slot   uint32_t      4       4        4
wait_owned   uint32_t      4       4        8
terminal     uint32_t      4       4        12
owned_pipes  uint32_t      4       4        16
reserved     uint32_t      4       4        20
```

### nl_snapshot：sizeof=48，alignof=4

```text
field                 type          sizeof  alignof  offsetof
abi_version           uint32_t      4       4        0
epoch                 uint32_t      4       4        4
accepting             uint32_t      4       4        8
closed                uint32_t      4       4        12
held_objects          uint32_t      4       4        16
unknown_objects       uint32_t      4       4        20
pending_children      uint32_t      4       4        24
held_pipes            uint32_t      4       4        28
inflight              uint32_t      4       4        32
ever_caps             uint32_t      4       4        36
name_bytes            uint32_t      4       4        40
production_admission  uint32_t      4       4        44
```

无损身份编码：volume 为 unsigned64 little-endian 八 bytes；macOS file 前八 bytes 为 unsigned inode little-endian，后八 bytes 为零；Windows file 保留 FILE_ID_128 原始16 bytes。不得先转 double/JS Number。`link_count` 是 uint64；当前 Node 输出为十进制字符串，volume/file为原始身份 bytes 的小写 hex，分别16/32字符。

输入 reserved 必须零；receipt reserved也应零。所有输入/output storage归调用者分配，ABI不返回需 caller free 的 heap buffer；OS对象、registry、cap及token记录归 native owner，调用者只能经原有限API release/close。borrowed输入在adoption返回前保持稳定，borrowed FD/HANDLE自身仍归 caller；native复制得到的对象由native关闭。C ref数值不是可给renderer或JS重建的授权凭据。`held_object_only=1`、`production_admission=0` 固定，不将 ACL/identity 快照当持续 namespace 或生产许可。

## 4. 有限 status、容量与资源接纳

status 精确集合：`NL_OK=0`、`NL_INVALID=1`、`NL_STALE=2`、`NL_DENIED=3`、`NL_UNSUPPORTED=4`、`NL_BUDGET=5`、`NL_BUSY=6`、`NL_RETAINED=7`、`NL_INTERNAL=8`。未知值不得解释成成功；异常不穿C ABI，Node不泄露路径/句柄/原OS异常。`NL_DIRECTORY=1`、`NL_REGULAR_FILE=2`、`NL_METADATA_ONLY=1`、`NL_PLATFORM_MACOS=1`、`NL_PLATFORM_WINDOWS=2`；没有正文/create/publish用途。

预算绑定 H 原值：

- process-wide：永久 owner records32，nonclosed owners最多2；inflight最多2；gate try-lock、不排队，最多一个OS call chain执行。
- 每owner：lifetime cap slots128，含root、failed、unknown attempts，slots不重用；名字16KiB，单组件255B，depth128；child attempts2，每child最多2 pipes。逻辑取消或超时不减实际资源计账。
- prepare TTL30000ms、logical wait5000ms；它们不能证明OS调用已中止、真实close完成或资源已排空。
- async worker queue0、maps0、message bytes0、ancillary transfers0；N0不以暗中队列或异步cleanup提高上限。

接纳矩阵来自 H:18–23：

- active epoch1且prepare未过期：允许root/acquire/observe/child-adopt，仍须对应owner/cap、用途、预算及gate有效。
- revoke后epoch2，不恢复、不wrap：不得新授root/acquire/observe/child-adopt；snapshot/revoke/release/poll/close继续仅为原owner有限cleanup。BUSY不认证完成撤销或释放。
- `nl_owner_publish` 始终unsupported，不dispatch OS操作。expected identity可空或作旧身份拒绝过滤，不授权、不允许跨owner cap混用。
- 返回非零 owner（包括失败adoption）仍有close责任；不能因status非OK丢掉owner。失败后的cap/metadata输出不能当成功使用，真实部分资源仍由native记录收口。
- child partial receipt：`wait_owned=1` 后即使随后pipe复制失败，caller也不得wait/reap或接管已转移的native process责任；`wait_owned=0`则caller仍是唯一reaper。borrowed原HANDLE/FD始终仍由caller自己关闭，native复制资源由owner清理。没有另一个thread/reaper可并发作用该child；receipt的terminal、owned_pipes与真实资源分别核。
- pipe EOF、child exit、Windows process HANDLE关闭为不同事实；不从timeout、kill返回或PID缺席推断。poll是实际非阻塞OS wait，N0不导出任意spawn/terminate/kill。
- 失败close数值永不再touch。后续BUSY/RETAINED cleanup只处理其他资源或继续真实child wait，不retry未知FD/HANDLE；不因晚返回、环境退出或GC删unknown记录。存在retained owner不得unload library。

## 5. 当前 Node API 枚举与最低 N-API

N:182–186、228注册精确为 `NAPI_MODULE(i06_native_location, init)`。普通JS import仅输出 `abiVersion:1`、`fixtureBound:0`、`productionAdmission:0`，没有JS owner构造器、path/fd/PID opener或native-host绑定函数。

`nl_node_bind_fixture(env,target,owner)` 是native host C入口，**不是JS方法**；native host必须先在真实native registry中adopt anchor取得owner，再绑定到指定env/target。当前N每env仅一个binding，callback data绑定私有native registry entry。JS不能用同shape对象、数字owner或自造external构造这份认证。

成功native绑定的target才具有八个同步方法：

```text
root()
directory(parentCap, component, expectedCap?)
file(parentCap, component, expectedCap?)
observe(cap)
release(cap)
snapshot()
revoke()
close()
```

root/directory/file成功返回opaque native external cap与metadata；expectedCap来自同一native binding，只提取早先identity作拒绝过滤。observe返回metadata，release/revoke/close返回status，snapshot返回status及ABI/epoch/资源计数。JS只持opaque external，无owner/cap整数或FD/PID输出。bound target另含 `abiVersion:1`、`fixtureBound:1`、`productionAdmission:0`；这些可见字段本身不是native认证，fake JS表也不是。

N直接使用的Node-API函数精确集合为：

```text
napi_set_named_property
napi_create_uint32
napi_create_object
napi_create_string_utf8
napi_create_external
napi_get_value_external
napi_get_cb_info
napi_typeof
napi_get_value_string_utf8
napi_add_env_cleanup_hook
napi_define_properties
```

没有 `napi_create_async_work` / queue/cancel/delete async_work，也没有 `napi_add_async_cleanup_hook` / remove_async_cleanup_hook 或TSFN。当前cleanup为同步env hook，只尝试revoke/close；retained owner留native记录，env teardown不签release。

官方Node文档标明 `napi_add_env_cleanup_hook` 属于N-API3；因此依据当前调用集合，构建请求应显式固定 `NAPI_VERSION=3`。这是源码API最低需求判断，不是目标headers/Node/Electron已经兼容的编译或加载证明。异步cleanup属于N-API8，当前没有使用，也不因此提高本阶段版本或新增异步资源。[Node.js v24.16.0官方Node-API文档](https://nodejs.org/download/release/v24.16.0/docs/api/n-api.html#napi_add_env_cleanup_hook)

当前注册宏的用法也与官方模块注册说明一致；实际注册导出、headers与宿主runtime仍须T03固定并后续验证，不凭宏存在认作addon可加载。[官方模块注册说明](https://nodejs.org/download/release/v24.16.0/docs/api/n-api.html#module-registration)

**同一registry实例是构建前置。** native host的owner_create与addon的bind_fixture必须落到同一份native registry/library instance。不得host和.node各静态链接一份capability_core，再跨实例传相同uint64 owner：那既不能证明对象相同，还可能碰到另一份registry相同编号。

root已指定最小测试装配合同，复用授权的 `location_core_test.cc`，不新增第十个host/helper源码：

- 普通core可执行模式保留 `main(argc,argv)`。
- 定义 `NL_NODE_FIXTURE_HOST` 与 `NL_WITH_NODE` 的测试addon模式不编译该main；同一测试源码提供私有C++ `fixture_node_bootstrap(napi_env,napi_value)`。声明只在 `node_binding.cc` 的内部conditional中出现，不新增公共C符号或header声明。
- 测试专用 `.node` 在同一目标链接 `capability_core.cc`、一个目标OS的platform TU、`node_binding.cc`、`location_core_test.cc` 四个TU。native bootstrap只在OS临时位置建立独占fixture，从held anchor创建owner，再实际调用 `nl_node_bind_fixture`；所有步骤处于该目标内同一registry instance。
- `node_binding.init` 仅在测试宏下调用该私有bootstrap；不新增JS方法，不接收JS path/fd/PID来构造owner。常规addon不定义测试宏，仍只返回未bound的三个标志。
- 这是后续源码与T03构建合同，尚无编译/运行权。它不属于上列N快照已实现API的额外实证；相关源码完成后应另固定其实际bytes/hash，H的13296B/fc3f原ABI与12个public C符号不因此改变。

## 6. core/child 测试argv交接与证据边界

以下为root指定的后续测试源码/构建接口，不是本次已读回并冻结的测试文件实现：

- core_test的 `main` 将取 `argv[1]` 为childprobe绝对target path；只由CMake的 `$<TARGET_FILE:childprobe>` 提供，不从renderer、普通JS或生产env取得可执行路径。
- child_probe的 `main` 只接受精确 `--hold-until-eof` 参数，等待EOF后exit0；错参数exit64。它是受控测试child，不是任意spawn业务API。
- CTest core test argv语义为 `core_test "$<TARGET_FILE:childprobe>"`；实际CMake target名须与T03登记的目标一致，不用相对路径猜产物。建议CTest外层timeout15s，仅用于测试进程失控时有界结束；它不证明native child/pipe/owner真实drain或可释放。
- TS单测fake表只证明薄owner机制/错误边界，与真实addon用例单列。真实addon测试只从显式绝对 `I06_NATIVE_LOCATION_TEST_ADDON` 指定的已编译测试专用 `.node` 路径经 `createRequire` 读取；缺输入明确skip，不回退fake或普通未bound addon。实际fixture绑定仍需上述native bootstrap调用 `nl_node_bind_fixture` 的证据；fixtureBound字段、import成功、skipped分支或fake表成功均不能单独补成native通过。当前不为此安装、编译、运行host/probe/addon或任何测试。

T03当前最小onlydocs交付应给：三既定构建路径的实际writer接受、输入header过程ref/hash、目标两OS架构/工具链/headers/Node与NAPI版本来源、宏/可见符号/同registry链接方案、core/child目标及argv、隔离输出与未来需授权的构建/运行命令。不得在该过程引入SQLite/Python/VFS、自动下载浮动headers或自动启动测试。

本文不会关闭原abi-preflight问题或替正式独审签通过；后续实际源码、布局、链接和生命周期保证仍须同版审查与获批运行证据逐项确认。
