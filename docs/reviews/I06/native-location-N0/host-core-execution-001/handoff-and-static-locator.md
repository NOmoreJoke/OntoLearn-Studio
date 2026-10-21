# 唯一宿主执行：失败交接与静态定位

2026-10-22。实际失败 capture：`95bda10ea944efb7f3d26c5e41baec127c73f9db`；调用：`b942e12cd122873109f4bd16d51e06e05ad7005d`。一次dispatch/session57976，仅同session一次空跟踪；工具退出1，corePid52560、原waitstatus256/正常退出码1，terminal/reaped、cancel0、events空。stderr原33B为 `N0 fixture failure: owner-create\n`，stdout0B。两产物前后pin相同；记录2.54215675s只属receipt后阶段，不是全命令耗时或性能结论。

独立结果审查原件6292B，SHA256 `f04b83c689aa7cee067e9ebdc9fb0f4ebf112d7ffdee8e8d5c388e027a82779f`：失败封存一致，无记录/hash矛盾；不签native通过。原五输出位于host-core-run-preparation/execution-001，原控制三件3550B，双流共33B、五件均0600；capture-manifest与output-readback保其身份。本轮未重试、未杀已reap PGID、未扫描/删除fixture、未读改设置或追加探针。native drain及后代/fixture残留保持unknown。

## 已能定位的失败边界

固定九源仍为b592，以下只读Git源码，无代码修改或新运行。入口见 [test:379](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0/packages/native-location/tests/location_core_test.cc:379)，创建链见 [core:189](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0/packages/native-location/src/capability_core.cc:189)，Darwin返回分支见 [macOS:29](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0/packages/native-location/src/platform_macos.cc:29)。

make_owner调用nl_fixture_owner_create后，仅以 `status==NL_OK && owner.value!=0` 放行；失败统一抛owner-create，main:555–556统一打印并return1。**core退出1不是底层NL_INVALID=1的证据**，原native status和失败owner序号均未记录。若非OK且owner非零，helper先作既有owner_close；失败将abort。本次正常exit1不能区分“无需close”与“该close返回OK”，更不能代签全部资源drain。

| 创建链位置                  | 源码实际返回条件；不是本次已命中分支                                                                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| core191–195                 | out为空→INVALID；input/ABI/platform不符→UNSUPPORTED；reserved非零→INVALID。固定fixture:149构造ABI/macOS常量、reserved全0并传非空&owner；这只是源码事实 |
| core196–198、admission47–64 | inflight预留/try_lock/异常可回BUDGET、BUSY、INTERNAL；全局unresolved_native_open→RETAINED                                                              |
| core202–206                 | 无剩余owner历史槽或活跃owner达上限→BUDGET；不能据此或退出1直接扩limit                                                                                  |
| core208–215、macOS29–41     | 单调时钟失败/越界→UNSUPPORTED；anchor非法→INVALID；fcntl失败映射BUDGET/UNSUPPORTED/DENIED                                                              |
| core216、macOS58–80         | fstat错误映射状态；类型/UID/可写位/link或ACL判据不符→DENIED；ACL查询空→UNSUPPORTED；acl_free失败→RETAINED                                              |
| core217–222、active75–82    | 已有非OK状态被返回；否则若全局围栏/closed/epoch/时钟/TTL使active失败→STALE。先作close_all，但返回值不单独记录                                          |
| core224                     | 只有正常成功才回OK；helper仍另核owner非零                                                                                                              |

macOS error_status:17–20把EMFILE/ENFILE/ENOMEM映为BUDGET，ENOSYS/ENOTSUP为UNSUPPORTED，其余DENIED。本次没有这些errno/status证据。ACL表格仅陈述源码检查条件，不把注释当本轮OS语义或ACL返回观测；不选定ACL、FD上限、时钟或权限为根因。

## 哪些后续case未到达

CLI main:551–552依序为metadata、child、partial-child、revoke/concurrency、budget；其五次make_owner位置分别为388、424、447、469、488，均使用同一label。不能仅凭33B stderr宣称第一次创建失败，也不能把前序case当已通过。

| 若实际失败在         | 该次创建之后未到达的步骤                                                                              |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| metadata owner388    | root/成员元数据、身份替换、hardlink/symlink、EXCL root rename、publish/revoke/close，以及全部后续case |
| child owner424       | 本case的probe构造/spawn/adopt/wait，partial、concurrency与budget                                      |
| partial owner447     | 本case的probe构造/spawn/部分adopt责任和关闭，concurrency与budget                                      |
| concurrency owner469 | observer线程与并发revoke/关闭，budget                                                                 |
| budget owner488      | budget-root、cap生命周期循环、预算拒绝和关闭                                                          |

以上为条件表，记录未提供实际命中行。共同确定：正常顺序未走到main553显式fixture-final-cleanup和554最终成功输出；栈展开的fixture析构另会尝试cleanup，其结果未被本次记录认证。EXCL实际执行与成功不能从当前通用失败标签签收，后序正常/部分child回收、并发、预算等也不能记为完成。

## 最小下一窗建议（尚未实施）

不建议原样复跑当前pair：它仍只产生通用label，现有证据不足以定位phase/status；本次窗口已消耗，不能复用。

建议总控下一步先裁定是否另授**单test失败回执精化**：只在既有失败返回处记录固定case枚举、现成nl_status、owner是否非零，复用当前stderr上限与原cleanup；不追加OS诊断查询、实时探针、路径/FD/业务数据或errno猜测，不扩大limit/换路径。它仍是测试输出改动，当前未制作patch或改源码；如获批，须新源独审、T03必要新采用/构建和pins，再另授一次精确运行窗。若不允许这项输出改动，就保留当前unknown，不以重复运行冒充归因。

本轮只有证据封存、独审和上述静态定位；九源、旧准备及构建原件未改，无GUI/设置/付费/push/PR/merge/Goal变更。宿主组件case失败，完整N0、macOS15/Windows11与父门均未通过。
