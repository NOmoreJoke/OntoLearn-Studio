# N0 接口源码定点复核 R2

2026-10-22。结论：在固定修订 `fa1a7e4155f3afee4a1b3409f9ab8804cc620186`，原 **P2-IF-01 在源码层关闭**。失败bind、hook注册失败及env teardown均保留原owner清理责任，未确认close不再继续删fixture或绿色返回。本次定点范围未发现新引入接口问题；不是编译、测试、native运行或完整N0技术通过。

## 1. 固定输入与范围

- 首候选：`4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8`。
- 修订候选：`fa1a7e4155f3afee4a1b3409f9ab8804cc620186`。
- 原独审：同目录 `interface-source-review-r1.md`，10473B，SHA256 `cfce3c180c3388ea693192fb6234853f87ae9a3e0e576c44b61defd219dc2cc3`，保留原文，不改写首候选结论。
- 本次依据修订ref中的 `source-text-check-r2.json`、`source-review-disposition-r2.md`、`packages/native-location/tests/location_core_test.cc`、core实际close入口，以及主说明image生命周期段。产品只读；唯一新增为本报告，不提交。

实际以Git读取两固定ref作diff、逐blob核bytes/SHA。九产品/测试均与R2 source-text-check声明完全相同；其中header、Node、TS owner、child probe、TS test五文件逐字等首候选，未重跑其原检查。core/mac/Windows其他修订由相应完整源码审查负责，本次只核支持IF-01关闭所需的close语义，不将定点复核扩大成它们的完整通过。

关键修订源：

```text
packages/native-location/tests/location_core_test.cc
24169B ee2460d5f4d2e6076d97622c4504734dd9f9f88e1f341358141b1f3ffbc61aaa

packages/native-location/src/capability_core.cc
17304B eae2d2dcf4ccf1f648dbec5fdd0424c0a2dac31a94a45d493e819948f2309319
```

五件不变输入：

```text
packages/native-location/include/location_abi.h
13296B fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172

packages/native-location/src/node_binding.cc
13163B e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383

apps/desktop/src/main/security/native-location-owner.ts
12496B e354b0830469647d70690f3e1d6e567c816f70cbbbe5c211dabba817fa7cc8d0

packages/native-location/tests/location_child_probe.cc
380B 041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c

tests/unit/i06-native-location-owner.test.ts
8460B e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04
```

本次未编译、执行测试、import产品、加载addon、安装依赖、借旧树环境或进行native/FS/child实验。下述均为源码条件与责任闭合判断，没有生成运行反例或将abort当实际释放证据。

## 2. IF-01 逐分支关闭依据

行号均对应修订ref的 `location_core_test.cc`。

1. **先固定原owner。** macOS和Windows fixture在47/148行各保留 `node_owner`。bootstrap在448–449行取得owner后，立即保存到fixture，再于451行注册cleanup hook。这样该责任不依赖后续bind是否成功或是否注册自己的owner hook。
2. **bind早退仍有fallback。** 457行虽仍直接返回bind状态，但成功注册的fixture hook已持有原owner。Node原220/223/226行的snapshot/BUSY、env重复、binding表耗尽等早退不会使该owner只剩局部变量；env teardown将进入430–438行的fallback。
3. **fallback先核owner终态。** 434–436行对同一 `node_owner` 调用实际 `nl_owner_close`。非OK立即固定错误并abort，尚未进入437行的fixture cleanup/delete。因此不能再出现“原owner retained，但只删fixture并正常退出环境”的绿色收口。
4. **hook注册失败有同步责任。** 451–455行在注册失败时核原owner close及fixture cleanup；任一未确认即abort。短路求值保证owner close非OK时不继续删fixture。两者都确认成功才delete并返回INTERNAL，不能静默把未知清理当完成。
5. **failed adoption不丢非零owner。** 301–307行的make_owner在失败且返回非零owner时先实际close；非OK明确abort。只有已确认close或没有获得owner时，才允许抛出固定owner-create失败给bootstrap。不会把失败adoption的未知close藏在普通异常返回中。

重复cleanup的安全依据同时核到修订core：`capability_core.cc:90–98` 对已退役 `value==-1` 不再调用OS close，未知义务仍返回false；对确切仍持有的号码只close一次，立即退役，unknown用OR保留。`342–346` 的owner close先revoke，再经原有限gate执行close_all，非终态返回RETAINED。故Node owner hook先成功close后，fallback对同一owner再次确认不会重复触碰已退役号码；若首次close未知，fallback也不会重试号码或把unknown清成OK。

本修订没有在Node或TS接口中引入新的公共方法、资源工厂、异步cleanup或所有权替身；header与原接口字节未变。上述源码依据足以关闭IF-01，不替将来的真实close失败、hook失败或bind竞争运行证据签通过。

## 3. image lifecycle 文案复核

修订主说明 `docs/iterations/I06/native-location-N0.md:67` 已明确：

- 同步Node env hook只作一次实际revoke/close尝试，retained owner仍在native记录中，不认证所有资源终态。
- trusted native host独立提供依赖image存活/pin闭包，这是绑定装配前置；当前源码没有动态库self-pin。static registry和env hook不充自动保库证据。
- 测试fixture hook持同一node_owner，close非OK则abort，不能继续删除fixture或假装卸载安全。

这些边界与本次源分支一致。普通addon仍无owner；真正trusted host仍须独立保证retained期间image存活。**测试abort不是release receipt，也不是host pin实现或验证**；进程最终退出、OS最终回收同样不构成该证明。源码阶段无需为关闭本项新增self-pin API或第十个host文件；T03当前仅onlydocs，实际单registry链接、image保活和目标运行仍待准确装配及授权。

## 4. 限定结论与未运行项

IF-01在本固定ref的源码层关闭，image生命周期文案准确；本定点范围没有新增待修P1/P2。原R1的其他符合项继续只绑定未变字节与当时的静态审查范围，不扩大为完整类型检查或运行通过。

N0仍是待构建/待运行候选。T03三构建路径实际采用、C++布局/符号/链接、真实addon fixture、目标两OS、实际close/child/晚返/错误清理、host pin、native生产用途、N1/SQLite/VFS/T01消费及父功能门均不由本报告关闭。root仍唯一产品writer；本报告不授权后续实验、提交或合并。
