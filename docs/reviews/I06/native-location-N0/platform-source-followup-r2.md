# N0 平台源码定点复核 R2

2026-10-22（Asia/Shanghai）。固定修订候选为 `fa1a7e4155f3afee4a1b3409f9ab8804cc620186`，比较基准为原完整候选 `4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8`。本报告只复核平台首审两项 P2、C-1 及 macOS FIFO 收窄，以及这些 diff 是否引入新的范围内阻断。

结论：上述两项 P2、C-1 和 FIFO 收窄建议在**静态源码层关闭**；本轮定点范围未发现新增确定 P1/P2。所有目标编译、链接、运行、真实 syscall 故障及故障注入仍未验证，不能称 N0 技术验收或两目标平台通过。未知 native open 仍保留、不提供解除或成功排空；修复只恢复其他已知资源的有限 cleanup 接纳机会。

原候选与 `platform-source-review-r1.md` 原字节不改。本轮没有产品编辑、编译、测试、native load、产品 import、FS/child 实验、安装、GUI、Keychain、提交或推送。

## 固定来源核对

产品读取使用 `git show fa1a7e4155f3afee4a1b3409f9ab8804cc620186:<path>`；没有采用工作区漂移内容。实际逐项计算九件源码的 bytes 与 SHA-256，全部匹配 `source-text-check-r2.json`。后者是文本记录，不是编译或运行证明。

| 输入 | bytes | SHA-256 |
| --- | ---: | --- |
| source-text-check-r2.json | 2981 | c00bbb725bd3f2323c383f5c60f4594d25685bc62fe73b35f130c43fc52dcbac |
| source-review-disposition-r2.md | 3755 | 6e5c28a5c93d8b709deb77df955d343edebacecd32acc6caee08455d595f01b7 |

下表列出四件变更产品及未变 ABI；路径以前缀 `packages/native-location/` 表示。

| 固定候选源码 | bytes | SHA-256 |
| --- | ---: | --- |
| src/capability_core.cc | 17304 | eae2d2dcf4ccf1f648dbec5fdd0424c0a2dac31a94a45d493e819948f2309319 |
| src/platform_macos.cc | 7675 | 28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be |
| src/platform_windows.cc | 12506 | bcf474ca9d9e5ce4efdf06284dd71b9504c5e69027d3a53c96fa7df56bc2b4c4 |
| tests/location_core_test.cc | 24169 | ee2460d5f4d2e6076d97622c4504734dd9f9f88e1f341358141b1f3ffbc61aaa |
| include/location_abi.h | 13296 | fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172 |

其余四件 Node binding、TS owner、child probe、TS unit test 与原候选字节不变，九件实际比对未以旧日志代替新 hash。未变 ABI 的资源上限仍为 process-wide inflight 2，不通过扩大容量绕过故障。

## P2-1：unresolved open 与 cleanup 接纳

新位置：`src/capability_core.cc:39-42,75-82,189-198,238-283`；`src/platform_windows.cc:26-33,134-146`。

在 gate 内，首个 `platform_open_member` 返回 RETAINED 即设置 `unresolved_native_open=true`、撤销所有已发布 owner 的 epoch，同时保留该原 work reservation。新 owner create 在发 metadata/duplicate 前直接 RETAINED；既有 owner 的 root/acquire/observe/child-adopt 经 active 检查后不再发新工作。gate 串行保护这个 bool，实际 open 同时只有一个，因此第一项 unresolved 后不能再进入第二次 open 耗尽剩余槽。

有限 cleanup 的 release、poll、close、snapshot 没有以 active 为前置门槛，仍经过原 admission。保留一项 inflight 后，总上限 2 留有一项可供这些同步 cleanup 使用；其正常退出会递减自身 reservation。并发调用可能先占这一个槽再因 try_lock 返回 BUSY，或另一调用短时 BUDGET；它们的 reservation 按原析构路径退回，没有形成第二项永久 unresolved。这里证明的是串行接纳与故障分支不变量，不能承诺调度公平或每次调用必定立即成功。

Windows `open_record` 增加 `returned_status`，在 NtCreateFile 返回后保存真实 NTSTATUS；静态输出仍留存 result/IO_STATUS_BLOCK。pending 和失败但输出非空两类都保守 RETAINED，但保留原 status 可以区分它们。新注释没有将失败异常输出称为仍在执行的请求；也没有将 retained slot 清掉或伪造 completion。out 只在认证成功路径赋值，异常句柄不被 core 当作确切拥有号码 close。

处置：原“两个永久 reservation 导致 cleanup 永久 BUDGET”的具体反例在新代码闭合；**源码层关闭**。尚无证据证明同步 NtCreateFile 自然出现 STATUS_PENDING，也未验证异常输出、在途结束、清理进展或保留后卸载行为；N0 仍不允许在 retained owner 下卸载。

## P2-2：ACL unknown 与已知 FD 首次关闭

新位置：`src/capability_core.cc:90-98,117-133,217-222,274-283`；mac getter/free 分支仍为 `src/platform_macos.cc:70-80`。

close_object 不再因 unknown 立即跳过。只要 object.value 仍是已知 FD/HANDLE，它调用 platform_close 恰一次，随后无条件退休数字为 -1。unknown 使用原 unknown 与关闭未确认的 OR：即便该 FD 关闭成功，原 ACL unknown 也不会清除。下次 close 看到 -1，只返回 `!unknown`，不会对可能复用的编号再次 close。

因此 metadata 附属释放未知不会再阻止已知文件资源的首次关闭；close_all 仍因保留的 unknown 返回未结束，不将 owner.closed 置 true。snapshot 也能区分数字已退休但 unknown obligation 仍在。对根失败采用同一 close_all 路径，未只修成员成功路径。

处置：原具体资源归属反例在新代码闭合；**源码层关闭**。固定 Apple Libc acl_free 总返回 0 的事实仍按首审保留，本项不冒称自然 OS free 失败已经发生。没有运行注入或证明 allocator 故障后的实际资源情况。

## C-1 与 macOS FIFO

`tests/location_core_test.cc:23` 在 mac 分支显式 include signal.h，消除 kill 声明依赖偶然传递头的问题。此前来自 Apple 固定 signal.h 的声明依据不变；本轮没有再把 public include 修正当实际 SDK 编译成功。**声明依赖问题源码层关闭**。

`src/platform_macos.cc:115-123` 将接受类型从 FIFO 或 socket 收窄为仅 S_ISFIFO。dup 成功仍先存入 out；若后续 fstat 失败或类型不是 FIFO，core child record 仍拥有已创建副本，receipt 反映已持 pipe 数，调用失败不抹掉 sole-reaper 责任。该副本由原 owner close_all 有限清理；borrowed 原 FD 始终由 fixture 持有。没有引入新的 socket API、正文读取、网络 channel 或句柄转移面。**FIFO 收窄建议源码层关闭**；pipe 正向与 socket 负向尚未运行。

## 其余变更与复核边界

同一 diff 还将 member open 前及 child 比较/dup 之间检查改为 active，使 TTL 和全局 fence 能在下一 dispatch 前阻接纳；owner create 返回前也核 active。它们没有增加异步回调，也没有将先前已取得的 partial child responsibility 回滚成未持有。实际 late-return/TTL 并发轨迹仍缺，不能用源码检查签在途覆盖。

fixture 新增 node_owner fallback 与 teardown 原 owner 收尾，属于另线接口审查主要范围。本轮核其跨平台 record 是同样的 opaque owner，未改变 pipe/process 原借用归属；非 OK 清理明确 abort，而非继续删除 fixture并报告成功。此处不将 abort/进程退出当 release receipt，也不代替其完整 Node 接口生命周期复审。

此修订未改平台 API 签名、C ABI/header、Windows SDK 类型或库依赖。首审要求的实际 C++17/SDK/CRT/Node-API 同 registry 链接、NtCreateFile/Ntdll、ACL/Advapi32、CompareObjectHandles/Kernelbase 仍未证明。macOS15 arm64 与 Windows11 x64 的编译、运行、真实 ACL/alias、pipe/child wait、close 失败、pending/异常输出及并发故障均待精确授权后验证。本结论只处理列明源码反例，不扩展 SQLite/VFS、生产 bootstrap、发布围栏或 DLP 边界。

文档检查仅 UTF-8、末行换行、行尾空白、表格列数与 diff 空白；本树无本地 Prettier，未安装或借用其他树依赖。不以文本检查充 C++ syntax/typecheck 或测试。
