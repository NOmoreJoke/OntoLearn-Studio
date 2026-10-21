# N0 接口源码独立审查 R1

2026-10-22。结论：固定候选存在一处 P2 测试 native owner 初始化/环境清理闭合性问题，尚不能在本审查范围签通过。Node/TS 方法形状、测试宏及 argv 链静态可对应，未发现另一个明确类型或导出阻断；这不等于 C++ 编译、TS 完整类型检查或运行通过。

## 1. 固定输入与实际检查

固定完整 ref：`4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8`，树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。产品只读；唯一新增为本报告，不提交、不改原报告或实现。

审查全文读取下列五文件的固定 Git blobs，并独立核 bytes/SHA 与同 ref 的 `docs/reviews/I06/native-location-N0/source-text-check.json` 完全相同：

```text
packages/native-location/src/node_binding.cc
13163B e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383

apps/desktop/src/main/security/native-location-owner.ts
12496B e354b0830469647d70690f3e1d6e567c816f70cbbbe5c211dabba817fa7cc8d0

tests/unit/i06-native-location-owner.test.ts
8460B e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04

packages/native-location/tests/location_core_test.cc
23353B 07e86432553ed0f0fe52b3d06ea656de9d55fd460dbe883a995d58a41ee906e8

packages/native-location/tests/location_child_probe.cc
380B 041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c
```

另只读必要的 core close/gate/owner 入口和 macOS pipe/reaper helper，确认接口责任与调用顺序；不重复完整平台实现审查。12个 Node-API 函数名由固定 Node 源码静态提取，与 source-text-check.json 的集合精确一致。只读取既有静态检查记录，不重跑原 parser；其中 `typescript-syntax-check.json` 明示 createSourceFile/parseDiagnostics，不是完整类型检查。

本轮未编译、运行测试、执行产品 import、加载 addon、安装或借其他树依赖，也未进行 FS/child/native 实验。下列轨迹由源码分支推导，不声称已经运行。T03 三构建路径尚未实际采用，不能据现有 CMake 建议或源码宏认作真实链接/目标平台验收。

## 2. P2-IF-01：bootstrap 的原 owner 未覆盖所有失败/teardown 分支

### 位置

- `location_core_test.cc:433–447`：创建 fixture/owner，注册 fixture cleanup hook，随后直接返回 `nl_node_bind_fixture(...)`。
- `node_binding.cc:218–229`：bind 先读 snapshot，或因 env 已绑定、binding 表耗尽而早退；这些早退不注册该 owner 的 env cleanup hook，也不统一关闭该新 owner。
- `node_binding.cc:193–198`、`location_core_test.cc:425–428`：已绑定 env 的 owner hook忽略 revoke/close返回；随后 fixture hook只清 fixture，不核其原 owner实际收口。

### 可达反例与影响

1. bootstrap 已成功获得真实 native owner，且已注册 fixture hook。bind 前的 `nl_owner_snapshot` 因另一 owner 的 OS 调用链占住 process-wide try-lock而非 OK，bind 在220行返回 INVALID；或者223/226行发生 env/容量早退。bootstrap 直接返回后，局部 owner引用丢失，只有清 fixture 的 hook，未有负责该 owner close的 hook。native registry仍正确记录该 nonclosed owner/dup anchor，但测试装配无法保证后续清理，可能耗住两active owner名额。
2. 已绑定的 owner 在 env teardown 时 close返回 BUSY/RETAINED。Node hook丢弃该结果；fixture hook仍删除fixture并可能成功返回。尤其 POSIX删除名字并不证明held FD已经结束，不能把“fixture清理成功/环境退出”当native owner已释放。此路径可能让测试宿主自然结束而未明确失败，丢失必要的收口证据。
3. fixture cleanup hook注册本身失败时，440–441行的一次close结果亦被忽略；如果close未确认结束，也不能将后续普通返回当已安全清理。

这不是“native registry已丢掉对象”的指控：原 registry保留记录是正确的。问题是测试bootstrap没有让fixture自身持续持有原owner责任，且没有把未确认收口变成明确测试失败。普通addon未创建owner，受影响的是测试专用装配和以后同模式的可信native host消费。

### 建议与验收断言

由唯一产品writer修复：fixture保留其原 `node_owner`，在注册hook前固定责任；无论bind是否接管成功，fixture自己的hook都对同owner执行幂等revoke和实际close，非OK明确失败/abort该测试进程，而不是仅删除目录。注册hook失败时同步close/cleanup未确认也不得绿色静默。重复cleanup不允许重试已退役的未知FD/HANDLE数值；core已保留的unknown须继续保留。

后续获运行权后至少覆盖：bind前snapshot BUSY、bind早退、owner hook close非OK、fixture hook注册失败；每条均不得成为测试绿或普通fixture-only清理成功。正常路径仍须真close OK且原owner无held/unknown/child/pipe；没有运行过的错误注入也须与真实OS故障证据分列。本轮不创建/运行这些反例。

root已通过协作消息接受上述P2候选，说明将按fixture原owner责任修订。此处只保留4cff原分支结论，不替尚未读取的新候选关闭问题。

## 3. env/image 生命周期的装配前置

普通addon init只有三flags，没有owner，不能推导存在资源持有。可信C bind一旦装配owner，host必须确保所有retained owner期间相应native依赖image持续存活。

当前 static registry、同步 `napi_add_env_cleanup_hook`、`state.env=nullptr` 均不self-pin动态库，也不证明image不会unload。环境退出只执行一次best-effort清理，不是库保活或真实drain回执。root拟将host实际pin列为T03装配/运行前置，这在N0源码阶段可以接受，无需本审擅自增加self-pin公共API或第十个helper源文件。

测试专用hook可对原owner close非OK明确abort以避免假绿；这不替普通native消费者完成pin，也不把进程最终退出/OS最终回收签成release receipt。T03后续须给同registry/linkage及host pin的准确来源与验证，再申请实际运行；本轮尚无此证据。

## 4. 接口连通与符合项

### Node → TS

固定 Node 注册为 `NAPI_MODULE(i06_native_location, init)`。普通import仅有 `abiVersion=1/fixtureBound=0/productionAdmission=0`；测试宏才调用私有C++ bootstrap，无新增JS path/fd/PID构造器或公共C符号。

native bind定义的八方法为root/directory/file/observe/release/snapshot/revoke/close，与TS的methodNames/bindingSchema精确对应。methods即使非enumerable，TS以Reflect.ownKeys和own data descriptors捕获，不依赖Object.keys(rawBinding)漏掉方法。TS strict schema拒额外入口；但shape/WeakMap只证明投影机制，不认证任意JS表为native，源码与测试注释已准确限定可信native-harness装配。

Node external cap先与当前binding固定token地址集合精确匹配再解引用；TS wrapper只存在于自己的WeakMap，跨wrapper/clone拒绝。身份hex与links十进制字符串无double中转；TS验证links≤uint64上限，regular file要求links=1，ACL/heldObjectOnly/prod字段有限。

TS只调用同步native方法，没有伪造underlying Promise。call异常/坏形状封本地新接纳并请求revoke；receiveCap在重入revoke后不发late wrapper。failed release标unknown，不再次调用同cap的release；close仅以原native close status OK设置本地closed，二次close缓存OK不代表第二次native调用。retained是保守历史标志，不能当生产能力。

### Node API floor

实际集合精确为12：

```text
napi_add_env_cleanup_hook
napi_create_external
napi_create_object
napi_create_string_utf8
napi_create_uint32
napi_define_properties
napi_get_cb_info
napi_get_value_external
napi_get_value_string_utf16
napi_get_value_string_utf8
napi_set_named_property
napi_typeof
```

新增utf16读取先guard≤255units并拒未配对surrogate，再核UTF8≤255B，避免用replacement编码接受孤立surrogate。此基础读取API不提高现有N-API3 floor；同步env cleanup hook是当前floor来源。没有async_work、async_cleanup_hook或TSFN。此前官方版本说明的出处仍为[Node-API文档](https://nodejs.org/download/release/v24.16.0/docs/api/n-api.html#napi_add_env_cleanup_hook)；这不是当前headers/链接/加载已经通过的证据。

### 测试双模式、argv与假绿边界

- `location_core_test.cc:14–19,422–470`：NL_NODE_FIXTURE_HOST要求NL_WITH_NODE；测试addon模式没有main，提供同namespace的private bootstrap；普通模式才有main。Node TU的conditional declaration与该定义名称/signature对应。四TU同目标链接仍是T03实际采用前置，源码存在不证明registry同实例。
- core main要求argc2，从argv[1]传入probe；macOS probe用绝对目标path构造精确 `--hold-until-eof` argv，Windows用独立applicationName与引用的command line。CMake TARGET_FILE绝对路径仍须实际供方给出，不以源码自行定位或搜索可执行文件。
- child_probe精确只接受一个 `--hold-until-eof` 参数；错参数64，EOF且无stdin错误0，stdin错误1。core test对生命周期认actual wait/reap；它没有证明所有子进程正向退出码或所有故障模式。
- TS真实组仅在显式I06_NATIVE_LOCATION_TEST_ADDON下运行，路径必须absolute且createRequire实际加载；缺输入skip，未回退fake。fake表组明确只测投影机制。真实组的root/file/observe/revoke/close调用与方法表对应，finally对close非OK会失败；但不替P2中的bootstrap/env teardown路径。
- core并发revoke case明确只是竞争表征：可能没有在途OS调用，不能算确定的late syscall测试通过。unsupported host返回77，不能计macOS15或Win11通过；缺失ACL/reparse正例也不能用skip补目标平台绿。

## 5. 未决与验证范围

本窄范围发现P2-IF-01，须新候选复核后再关闭。没有发现另一个确定的源码类型/导出/参数连通阻断；TS完整语义类型检查、C++编译、public layout实证、真实symbols/链接、T03单registry与pin、目标平台实际addon/child/close故障均未完成。

root继续唯一产品修复；本报告不改实现或测试，不消费T03未采用构建，不授native运行/生产IO或父I06通过。本报告自身允许使用既有全局纯formatter，仅作用本新文档；工具及结果另随交付消息回报。
