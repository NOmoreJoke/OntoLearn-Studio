# 唯一宿主执行失败：独立结果复核

2026-10-22。固定 capture ref：`95bda10ea944efb7f3d26c5e41baec127c73f9db`；精确调用 ref：`b942e12cd122873109f4bd16d51e06e05ad7005d`。这是失败结果的证据审查，不是原因定位、修复设计或再运行授权。

## 结论

封存原件、原五输出、根一次窗口与精确调用相符；本轮未发现记录矛盾、字节/hash 错配或把失败写成通过。真实结论必须保持 **工具退出 1，core 原始退出码 1，宿主 case 失败**。可关闭本次失败封存的独立复核，不能关闭 native 技术验收。

唯一 stderr 为 `N0 fixture failure: owner-create\n`（33B）。这是通用 fixture 标签；不能从标签或状态名确定具体 owner、原生返回分支、OS 错误或根因。本轮未据此作定位或提出重跑。源/probe、目标 macOS15/Windows11、addon、产品启用、全部 N0、native drain 均不获通过。

## 实际读取及核对

全部命令显式 cwd 为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。全文读取 capture 目录七件、固定 b942 的完整 exact-tool-call JSON，以及 execution-001 的五件原输出。通过 Git/stdlib JSON、AST 和字节/hash 静态检查交叉核对，检查命令均 exit0；没有运行候选或空 guard、native、信号/进程/FS probe，没有扫描 `/tmp`、读供应目录/实物二进制、SDK、GUI 或修改产品。

capture 七件是 authorization-window、capture-manifest、dispatch-intent、outcome、output-readback、preservation-check、tool-receipts。manifest 的 11 个列项（除 manifest 自身）逐件对固定 Git blob 的 bytes/SHA256 全匹配。manifest 自身为 2820B，SHA256 `19873a241dd6c7df2b9f8da1229fcbbe6facfd3a57908b244d83e4d60a8bbe7b`。

原五输出另与实际本树文件逐字比较一致，当前 mode 均 0600；未改写。以下为实际重新计算值：

| 输出 | B | SHA256 |
| --- | ---: | --- |
| intent.json | 1899 | c6ac1f4e1b795942b376e1772062ff99159cad73304df49cef09bda1681e4bdb |
| postflight.json | 1135 | df9bd5f04b236f30566a847fdb665f96ad7bb6c53d2fa93257c43ab8b4337775 |
| result.json | 516 | 190b76899a8c27a72fa84a8da8fae7f62e36a4fb60374da58e1f72fb90cdafa2 |
| core.stdout | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core.stderr | 33 | 515e1cd5e4acaeaf8ac081ce18268aa2e7a007720811dbf06063d6f845866708 |

这里的文件检查只针对已授权原输出，不是 fixture 或进程状态探针。preservation-check 关于旧20件、26件、九源码的陈述本轮仅作为封存 owner 记录阅读，未另做该整套旧审计，也不据此签新产品通过。

## 授权、调用身份与预算

封存 authorization-window 与实际根 `iteration-control/2026-10-21-weekly-release/I06-N0-single-host-CLI-execution-window.md` 当前原字节一致：4121B，SHA256 `5bf62fa8d65d92bb24d80708d35c7efbc1d4f581a8fcf63c385a02602128f3cb`。它明确授本次 b942 arguments 唯一一次 dispatch，而非复用历史 NOT_GRANTED 文案或长期授权。

b942 exact-tool-call JSON 为 18740B，SHA256 `c5c660d7df87e4d1b158e93b8d42e8816f978df74290a286c982d79456d0d22d`；cmd 为 17176B，SHA256 `2428cac0cbfa5cf9bf8906e0e1800e776b865408eece1950ff1f0029884921a6`，与窗口、dispatch-intent、tool-receipts 一致。AST 仅作数据解析：相对已独审 cc1fc11，顶层仅 AUTHORIZATION/CORE_PIN/PROBE_PIN 三赋值变化；其余 AST、shell 首行及四个非 cmd 参数一致。cwd 精确本树、login=false、yield_time_ms=1000、max_output_tokens=1000，未见另加 wrapper/外层 timeout。

授权标识 `I06-N0-execution-001-227052c230da782c`、两精确 argv/pin 与 runtime intent/postflight 一致。pre/post 数组完全相等：core 343904B/SHA `229faf9fcf15ccbbc9e0e8fefefb1c91c016fc2ea6fea2df92998392e14e812b`，probe 34120B/SHA `be916e5252b21e6671c6bd2f32301f8581c1b32ce87f78a4a7b0f8314fb2a6b2`，同 dev/ino。每 pass 总 378024B，低于 2MiB。此为已封存运行前后检查的对应性，不是本轮重读实物，也不倒推排除 hash→exec 期间所有名字竞态。

三 runtime 控制记录共 3550B，各低于 64KiB，总低于 256KiB；raw 两件共 33B，各低于 1MiB。七件行政记录含 manifest 当前合计 13444B，与该 manifest 自排除行政总 10624B 加自身 2820B 相等，低于 32768B。本报告另增，未重写旧 manifest 或把新报告伪装为旧 capture 内容；本文控制在 8KiB 内，总行政量仍低于 32KiB。

## 工具终态和 core 终态分别保留

封存 receipts 记录一次 exec 返回唯一 session57976，随后仅同 session 一次空 write_stdin 跟踪；终态 chunk718f6f/exit1，工具流为空。没有第二次 dispatch 的记录，不能把该跟踪算作重试。此结论来自封存的实际工具回执，不是本轮重新等待或查询进程。

runtime result 为 `dispatchAttempted=true`、corePid52560、waitOutcome=terminal、leaderState=reaped、coreReturncode=1、coreWaitStatus=256、cancelSignal=0、events=[]、processApiRefusedOrWaitUnknown=false、retry=false。256 是 wait 原始 status；结合正常终态解码为退出码 1，不能写作 signal256 或 raw 输出256B。outcome 对应字段均与原 result 一致，工具 exit1 与 core exit1 分属不同层。

postflight 对两 raw 给出 stable=true，且声明只是 snapshot；原始流/hash 实际匹配。这支持记录完整保存该次失败的输出快照，不把失败转绿。没有 timeout/组信号事件或 retry 记录；不从 events=[] 外推所有后代已退出。记录的 2.54215675 秒只限 receipt 后 wait/cleanup 段，不是全命令 wall time、硬时限或性能结果。

`nativeDrainCertified=false`、fixture/descendant residual unknown 继续保留。确切 leader reaped、双流稳定、零 stdout、未记录 kill 都不证明全部 native 资源/后代 drain，更不授扫描或清理 `/tmp`。后续 root 可基于失败原件作固定源码分支静态定位，但本报告不替其归因，也不授权修复、重构建或再次执行。

本轮唯一写入为本报告；旧 receipt/原输出/manifest 保持不变，无提交、无 Goal 或系统配置操作。独立结果审查不替指定模型外审、目标平台实测或根后续授权。
