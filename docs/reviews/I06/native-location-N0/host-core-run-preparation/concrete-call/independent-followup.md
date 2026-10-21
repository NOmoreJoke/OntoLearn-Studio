# 一次性控制调用：定点独立复核

2026-10-22。复核者：I06 独立审查子任务。本报告仅复核固定准备材料，不是运行许可、native drain 证明、N0 技术通过或指定模型外审替代。

## 结论

固定 `cc1fc11d1537c36cb9de948802c08a5af940fad2` 相对首审 `a93733837e0611c6d5681c7efc2572a829389371` 的 P2 与 P3 已在本次静态范围关闭；本轮未发现新增阻断。原始首审意见与原件保持不变。

这只表示所审具体调用材料已完成该两项修正。`AUTHORIZATION`、`CORE_PIN`、`PROBE_PIN` 仍为 `None`；精确供方产物路径、正式 manifest/采用事实及根一次运行窗口未由本报告提供或认可。禁止据此执行空 guard 或补值后执行；填值会改变调用身份，须重新由根核验精确差异与授权条件。

## 固定输入与读取方式

工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。全部读取命令显式设置该 cwd。实际全文读取新 ref 的 `call.md`、`api-basis.md`、`disposition.md`、完整 `tool-call.preparation.json`，并读取 a937→cc1fc11 的对应 diff。通过独立标准库 JSON/字节检查核对两版完整 cmd；没有执行、eval、导入或编译任一候选 shell/Python。

以下均为实际 `git show` blob 的 UTF-8 原字节：

| 文件（均位于 concrete-call） | 字节数 | SHA256 |
| --- | ---: | --- |
| call.md | 19048 | 1188378bf9dca71e76c2e32b5dd31130d8c84531533716c9c76db3b0356876f4 |
| api-basis.md | 10177 | 01f33b641aa60835272e64281370461c7523134ce536bf8e601e5c28b5469447 |
| disposition.md | 1416 | 70c532e0cef3ee2586208bd8b3e4829e181b4777bcaeb2dcf8e2d1017551f380 |
| tool-call.preparation.json | 17892 | f08aff2ffa8c9c7e4f30052fd584b250154e6cb0c5194871373f98ea8bf78dab |
| tool-call-a937.preparation.json | 17111 | f0e1bf51d6d4729c87690b45253dbc978e93588b777e16b16d4a9712f75bfa7b |

新 JSON `arguments.cmd` 与新 Markdown `sh` fenced block 内完整命令逐字一致（含末尾 LF）：16536B，SHA256 `0d47f1f282ec78a199654de1671d9206d38609c722e71043a054b76672900cb4`；JSON 自记 cmd 和 callSource 的字节/hash 都实际匹配。旧 JSON 的 cmd 亦与固定 a937 原 call fenced block 逐字一致。五个工具参数完整，cwd 为本树、login=false、yield_time_ms=1000、max_output_tokens=1000；三个 None guard 仍存在。

`git diff --name-only a937 cc1fc11` 只列八件 concrete-call 准备材料，没有九产品/测试源码变化。本轮不重新验证源码或此前平台/旧矩阵。

## P2：已观察取消及后核失败——关闭

新 `call.md` 后核成功判定先检查 `cancel_signal`；已观察取消改为 `FAILED_CANCELLED_POSTFLIGHT` 并返回非零。原始流超限/不稳定返回 stable=false 时，若 core 原终态为零，不再沿用 `HOST_CASE_EXIT0`，改为 `FAILED_POSTFLIGHT`，控制返回非零。读取/产物后核异常仍走非零异常分支。

finally 写记录前再次检查取消，已观察取消设置 `FAILED_CANCELLED_CONTROL`，将尚为零的控制退出码改为 1。原确切 wait 留下的 `coreReturncode`、`coreWaitStatus` 未被覆盖；因此真实 core 退出零与控制因取消/后核失败而非零可以同时保留，不把失败倒写成 core 失败。

最后 `os._exit(1 if cancel_signal and exit_code == 0 else exit_code)` 再对返回参数求值时的取消状态取快照。故在记录写出或持有 FD 关闭期间已执行 Python handler 的取消，会使原拟成功的控制返回非零；不会重写独占 result/postflight 原件。

必须保留其有限语义：最终参数取值和真正退出之间没有原子信号捕获保证；信号可能到达但 handler 尚未执行，或在最后快照之后到达。较早 result.json 也可能仍为成功/未取消快照，而稍后的工具终态非零。根归档/判定必须同时看实际工具终态和原记录，不能只凭早 JSON 的 HOST_CASE_EXIT0 宣称控制通过，也不能宣称任意时刻取消均被最后指令捕获。新 call 末段及 disposition 已明确这项限制。本报告没有把参数表达式当作原子 signal fence。

## P3：不重试的层级——关闭

`wait_until` 异常注释与 `api-basis.md` 已明确：脚本在 Python 层收到 EINTR/ECHILD/权限等异常后不再尝试该异常 API；不保证 CPython/OS 内部从未按 PEP475 重试系统调用。实际 diff 没有增加异常重试循环、第二次 Popen、替代 process API 或提权路径。

这与首审已读本机标准库/官方 Python 实现的证据层级相容；本轮不再读取网络页面或运行 API 验证。工具平台拒绝后停止、不重提调用的约束继续保留，不能用内部 EINTR 行为为权限拒绝重试辩解。

## 验证与未验边界

本轮只运行 Git 静态读取、stdlib JSON/字节/hash 检查，实际检查命令 exit0。JSON 检查仅处理候选为数据，未运行候选（包括 None guard），未做 signal/process/FS probe、产品 import、编译、测试、native load、GUI 或构建；未读 T03 可变 WIP，也未采用摘要供方产物。

本次修正未增加 runner 文件、线程、产品范围、预算或资源清理权限。单线程/无原生注入与外部 reaper、精确供方/冻结路径窗口、私有控制进程信号状态细化、quiet environment 条件仍待根独立认可。Popen 构造、文件与系统调用无硬墙钟时限；15+1+2 是取得精确 receipt 后的逻辑控制预算，未知 child/残留 fixture 仍不能凭信号或目录差分冒签 drain，禁止无确权删除。未授任何实际执行许可。

首审报告 `independent-review.md` 重新只读核对为 11788B，SHA256 `89b4eb2706092cfda74b9a6efdff70cba926b2888a8cb7f6c4d13cd68db0a9a7`；未修改其原文。本跟进是唯一新增报告，无产品或旧证据改写、无提交。
