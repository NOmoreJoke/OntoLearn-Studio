# N0 ABI 初稿静态预审

2026-10-21。结论：仅 metadata、held-object-only、无 publish/正文/绝对路径 bootstrap、真实 close 失败保留未知等方向符合 N0 边界；头文件尚需固定以下容量、所有权转移和接纳语义。本文是实施中接口建议，不是最终源码审查通过，也没有编译、运行或平台证据。

## 固定输入与边界

- 全文读取授权 `I06-native-N0-source-implementation-authorization.md`：6089B，SHA256 `fc4a74b81530197a3aa38d0bcc5027d952d83c64d7f0a6cd5be2abdd3c9ce4ee`。
- 初稿 `packages/native-location/include/location_abi.h`：5747B，SHA256 `38c6591277fbec9d9ed9f10ba045ef0d13839259c036cbfdf235931edafe0331`。以下行号只绑定该初稿，不代表随后可变源码。
- 实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，branch `feature/I06-native-location-N0`；本次读取时 HEAD/base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。AGENTS 实核为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，不修改或 stage。
- 只读授权和 header，不读用其余实施中产品；仅新增本报告。没有产品 import、测试、编译、动态加载、native/FS/child 实验、依赖安装、网络、GUI 或 Goal 操作。以下反例均是待实现与验证的设计轨迹，不称已经实跑。

## 必须固定的接口问题与反例

### 1. child adopt 的失败也必须有唯一责任人

`113` 行的 `nl_fixture_child_adopt` 只返回 status，无 child ref 或逐资源 receipt；`109–112` 行同时承诺转移 sole wait/reap 责任并复制 borrowed handles。必须明确转移的线性化点及非 OK 语义。

反例：复制 process 成功，复制第一 pipe 成功，第二 pipe 失败或撤销到达；native 已持部分资源，但 caller 因非 OK 自行 wait/reap，native 随后也 poll/reap。或者 caller 假定全部转移、native 假定失败无转移，留下无人拥有的 child。Windows process HANDLE、POSIX waitable child 和 pipes 的状态必须分别收口；不能用一个 failure status 消除真实部分持有。

最小合同应规定：接纳前检查不会启动任何复制；一旦发生实际持有即全部归原 owner 的有限 cleanup，非 OK 不等于零资源。caller 对 wait/reap 何时停止负责须可精确判断。若无需新 child ref，必须说明 status/owner snapshot 如何无歧义表达转移，且同 PID 再 adopt、同一个 pipe 重复输入、已被他方 reap 的 child 均不能形成第二责任人。可信 harness 仍须先建立“这是自身可 wait 的 child”的真实前置，不把 PID 数字当认证。

### 2. 上限必须声明作用域和计费单位

`16–31` 行给出 owner history32、active2、caps128、名字16384B、depth128、inflight2、child2、每 child pipe2，以及 async/map/message/ancillary 为零。头文件未明确这些值哪些全 registry、哪些每 owner，哪些按 ever/history，哪些按实际 retained 计费。

需要固定的具体断言：

- 两个 owner 同时存在时，不能未经明确决定把 inflight2 变成4、caps128变成256或名字16384B变成32768B。全局与每 owner 的更小界应分别列明。
- root cap 是否消耗128之一；128是否是 ever-issued，而非 release 后回补；retired/unknown cap、失败 adoption、迟到成功和关闭未知对象都须计入相关预算。不能回收后重用旧 cap 的 slot/generation。
- owner history32不能因 revoke/closed tombstone 删除而重置，owner id/epoch/generation 溢出不得回绕；耗尽拒绝必须在任何 OS dispatch 前完成。
- `name_bytes` 是存活名字、全部历史名字还是组合 component 链的 UTF-8 字节；包含终止符/重复 components/失败但已保留对象与否必须固定。depth 包含 root 与否、单组件255B和总名16KiB先后检查也须明确。
- child/process handle、每个 pipe、cap FD/HANDLE、未知关闭记录都须有实际有限容器槽。inflight 是正在执行的本地同步调用/系统调用，不是 JS 等待者数量；不排队意味着 gate 被占时立即 BUSY，不能暗中累计异步 work。

### 3. revoke、epoch 与晚返回需要逐入口接纳矩阵

`12` 行称 revoke terminal，`99` 行只有 acquire 显式 expected_epoch；root/observe/release/snapshot/child_adopt/poll/close 没有该参数。因此实现必须按真实 owner/cap 关系校验，而不是只在 acquire 入口读一次 accepting。

建议固定矩阵：新 root/acquire/child adoption 在撤销后不得产生新可用权；snapshot 与有限 cleanup 可继续；observe 是否只为原 held 对象 cleanup/审计而保留应明确，不能充新准入。release 必须校验 cap.owner、slot、generation 与原 owner 精确匹配，旧/克隆/别 owner refs 不得触发 OS close。

反例：acquire 进入时 epoch 有效，OS open 正在进行，revoke 已线性化，open 晚返成功。晚返对象必须计回旧 owner，并关闭或 retained/unknown，不能返回一份仍可用的新 cap。若 gate 忙导致 revoke 返回 BUSY，BUSY 本身不证明 native 已撤销；TypeScript 可以先停止本地新接纳，但须保留“native revoke 尚未确认”。源码还应避免持 gate 等待 OS 终态导致 revoke/close 排队或死锁。

### 4. 失败 close 的 unknown 记录不能再触碰同一数值

`126` 行正确注明 failed close never retry the number；`12–14` 行的“BUSY/RETAINED requires subsequent cleanup”须明确不是重试那个未知 FD/HANDLE。

反例：close 返回不确定时 OS 实际已关闭；另一对象复用相同数值；下次 owner_close 为清 unknown 又 close 该数值，误关新对象。允许后续 cleanup 仅处理尚未尝试关闭的其他资源、等待实际 child 终态等；未知记录保留，不恢复权限或减成“已证实释放”。`NL_OK` 的 close 只能在所有 owned 对象/pipe/process 与 inflight 确认终态后返回；不可关闭的 unknown 可以永久保留并阻止 library unload。并发/reentrant close/release 不得对同一资源启动第二次 close。

需同时定义失败 owner_create 的 out-owner：无责任则必须清零；非零即唯一 cleanup 责任，即使 status 非 OK。所有失败 out-cap/out-metadata/out-snapshot 的初始化规则应统一，不能留下 caller 上次成功值而误用。

### 5. pipe 和 child 终态不是同一件事

`111–112` 行不从逻辑超时推断 pipe EOF/child exit 是正确边界；`134–137` 行也将 Windows process HANDLE close 单独列出。应明确 poll 是否只证明 child 终态，何时对每个实际 duplicated pipe 发起 close，以及 close receipt 如何计入 held_pipes/unknown_objects。

反例：child 已 exit，但 owner 的 pipe HANDLE close 失败，或另一个实际 child 尚未终态；owner 仍不能 closed/active-slot 归零。反向 pipe EOF 不证明 process 已 wait/reap。当前 private platform ABI 没有 pipe-EOF 查询输出；若本阶段只靠关闭自己的 pipe 获取资源终态，应准确如此描述，不将它写成已经证明对端 EOF。native 不暴露 terminate/kill/spawn，harness 对未退出 child 的后续受控终止准备不等于当前 poll 已成功。

### 6. ABI 布局、身份与时钟规则不能由编译器默认补齐

`7–10` 行说固定宽度，但 fixture 结构 `66,73,75` 使用 intptr_t，其尺寸有目标前提。当前目标为64位，也须由 T03 锁定，并对 public structs 的 sizeof/alignof/offsetof 做静态断言；不要传 packed/不同 CRT/compiler 假设的结构。保留字段清零、padding/out 初始化、ABI version 不符拒绝、未知 enum/status 处理与 null out-pointer 拒绝需要一致定义。

`53` 行的 volume8/file16须冻结字节序和平台无损编码：macOS dev/inode如何补零，Windows volume serial/128-bit file ID如何映射；expected identity 只作拒绝过滤，不能通过同数值复制来授 owner 权。`acl_checked` 仅可表示本次 held 对象真实检查结果，未知/不支持必须拒绝；不得等同持续 ACL 许可。

`138` 行时钟返回 uint64_t，但未知失败值、回退、加30000/5000溢出行为尚未定义。应 fail closed，不因无符号下溢或回绕恢复 accepting。调用前后同步工作均核真实单调截止；5秒逻辑等待和30秒prepare TTL不能声称中止阻塞 syscall 或释放实际资源。当前 C 接口没有公开 prepare/等待对象，常量由哪层消费应明确，不能仅有宏就宣称落实时限。

### 7. 单组件解析必须与两个平台实际 namespace 一致

`96–103` 行允许 held parent 下单 component acquire，没有绝对路径 opener，方向正确。需要实现逐个拒绝 NUL、分隔符、`.`/`..`、无效 UTF-8、Windows ADS/设备别名/尾点尾空格等会改变名字解释的输入；拒绝不能在 OS 已接纳后补做。Windows UTF-8→UTF-16转换不能截断、替换或隐式归一化；255B是有限工程拒绝政策，不借平台更长名提高上限。

parent 必须是同 owner 的活 directory cap；file cap 不可当 parent，旧 cap 或跨 owner cap 不能经 expected identity 相同而通过。held 对象并不证明其仍位于原 namespace：祖先/root rename或member替换之后，不能把返回对象身份快照提升为持续路径许可。无可证明 no-replace/源围栏的 publish 始终 UNSUPPORTED，且不 dispatch OS 操作。

## TypeScript 薄 owner 需要的绑定

本节是新 `apps/desktop/src/main/security/native-location-owner.ts` 的接口要求，不授权修改 main/Supervisor/T01，也不实现第二 registry。

- 构造只接受已由可信 native harness 装配的私有 binding 闭包。真实 native wrapper/type tag/私有实例关系负责认证，不能仅凭 shape、JS Symbol/WeakSet、复制的状态或“返回 native Promise”授能力。Node 不接受 renderer/JSON/raw external 注入，不导出 FD/PID/整数 owner/cap 或通用 callback。
- JS 只能持 opaque owner 与 cap wrappers，native 仍是 epoch/用途/资源计数权威；所有入口由实际 native owner闭包处理。跨 owner混用、clone、revoke后旧wrapper、owner已closed的调用均有限拒绝，不能用字段相同重建能力。
- native 返回可能同时带失败与 retained responsibility。薄层不能在 reject/throw、5秒逻辑timeout、GC/finalizer或本地 detach 后删除其 owner；也不能 Promise.race 后发下一组资源而丢原 in-flight责任。晚返回cap继续归原owner直到真实cleanup。
- C ABI当前全同步且async work0。薄层不得包装成异步而宣称 syscall已可取消；调用线程、Node事件循环阻塞风险与两inflight槽的实际作用域需写清。若将来要 worker queue/TSFN/跨线程消息，属于新授权，而不是在 addon 内暗加。
- 所有C边界捕获异常、返回固定status；Node抛出固定有限错误，不带路径、OS原异常、指针或句柄。构造/参数捕获需防getter/Proxy重入，安装状态前复核epoch/revision；unknown throw的检查自身不得再次抛出。

## 最小 T03 source/static 请求

仅由 root 路由，不向其他聊天发任务。本次只提三既定T03路径的必要输入，不创建或修改它们，也不申请立即编译/运行。

1. 固定 I06 六产品/三测试的最终 refs/bytes/SHA；锁 ABI1、目标 macOS15 与 Win11x64 的架构、指针宽度、语言标准、编译器/SDK/Node与N-API来源、CRT与异常/RTTI约定。未知字段保持缺口，不读本机版本代替目标证明。
2. CMake只引用授权九路径，不另建未授权helper；分别选择真实平台实现，未知OS显式拒绝，不把另一平台空stub链接成支持。锁 public struct 布局静态断言与C调用约定；冻结C ABI和Node registration需要的精确可见符号，隐藏 `i06_location_detail`，不能以全隐藏导致ABI不可消费或全导出泄漏私有入口。
3. `toolchain-lock.json` 记录精确可重现来源/hash/许可证/目标；`scripts/build-native-location.mjs` 在未来获运行权后只消费该锁、隔离输出，不下载浮动依赖或自动运行 probe。N0不含SQLite/Python binding/VFS，不能在构建闭包中悄然添加第二SQLite或新权限。
4. 明确 core test、child probe、Node addon各产物与编译/链接职责；源码静态准备与实际两OS构建、后续受控运行分别回执。现有开发宿主、语法文本或编译脚本存在不能代替macOS15/Win11运行证据。

上述问题由 root 固定ABI/实现后交独立同版源码复核；关闭状态不由本前置报告代填。本报告不授生产LocationLease、正文/create/publish/bootstrap、N1/VFS/SQLite、T01接线、native运行或父模块通过。
