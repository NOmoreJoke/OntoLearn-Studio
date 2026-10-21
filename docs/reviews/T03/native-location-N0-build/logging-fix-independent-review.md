# T03 N0 R5 日志异常路径独立复审

2026-10-22；独立 reviewer：`n0_build_review`。

**结论：R5-logging-1 在本次最小日志修复的静态范围内可接受；未发现剩余需阻断本修复交付的 P1/P2。原 R1 只修复布尔值，不足以覆盖同步异常和首因持久化；本报告是该问题的补充复审，旧报告原文保留。没有运行未来 complete/build 分支或故障注入，不能据此声称异常路径已实测。**

## 授权、身份与范围

根针对已固定基线 `c7ca9f517d3a4cffc39ce823b8f0bb16091e68a5` 的日志缺口明确授权最小修复和同候选独审；仍限定静态及原只读 incomplete 检查，禁止未来完整分支、故障注入或进程故障实验。本 reviewer 仅写本新报告，没有改旧报告、产品源码、锁、供应材料或其他证据，没有提交。

实际源码树：`.worktrees/T03-native-location-N0-build`，branch `feature/T03-native-location-N0-build`。本次全文读新 driver 的相关实现和相对基线 diff，逐分支检查 open/spawn/close/验证/persist 控制流，并从真实文件重算下列身份，与 `logging-fix-candidate-1.json` 一致：

| 文件 | bytes | SHA-256 |
| --- | ---: | --- |
| `scripts/build-native-location.mjs` | 27002 | `d1ddcbd699be1feccd85a39ec583bcab6563d08597f70df5ad430f9879f06714` |
| `packages/native-location/CMakeLists.txt` | 13332 | `81df2fbf6169cfb8d990080cf9f804adc6e275accdfc912f9c334028578d7a5d` |
| `packages/native-location/toolchain-lock.json` | 4624 | `865c7c8ea12a2038437b81fb5718eaa3ce1ff9c3e30709f2ce03029e4456a30f` |

CMake 和锁与原固定交付字节一致；本次产品差异局限于 driver 的执行证据及日志生命周期，没有改变审批门、供方 pins、固定 commands、shell:false 或验证语义。材料 agent 的后续供方清单不作为本修复能否关闭的前提。

## 原反例与当前处置

基线在 `spawnSync` 返回且两次 `closeSync` 成功之后才追加本条命令记录。因而第二次 open 失败、spawn 同步抛错、任一次 close 抛错，均可能跳过 argv/cwd/outputpaths/run/首因的日志记录；第二个 fd 也可能因首个 close 抛错而未尝试关闭。原 R1 的单调布尔值仅避免部分 false 报告，不能补齐此信息缺失。

新代码的静态控制流如下（行号为上述固定 driver）：

| 路径 | 核查依据与结果 |
| --- | --- |
| 任一输出 open 前已有完整命令计划 | 540–563 行预建全部命令的 executable、argv、cwd、stdout/stderr 绝对路径及初始 dispatch 状态；615–619 行初次 persist 失败即 return，后续 open 不可达。 |
| 初次或中途日志写入失败 | 579–614 行每次使用新编号、`wx` 的独占快照，不覆写已完成或失败 partial 文件；记录 persistenceFailures、目的路径和 lastPersistedSnapshot，回退 stderr 带完整内存 log。返回 false 后本次不继续 dispatch，也不会运行下一条命令；已开 fd 仍经 finally 清理。 |
| stdout open 失败 | 627–640 行逐个 open 的独立 catch 登记失败，不进入 dispatch；已有计划不丢失，随后 command-final 尝试记录失败状态。 |
| stdout 已开、stderr open 失败 | stdout handle 留在局部表中，stderr 失败后跳出；693–707 行 finally 仍逐 fd 清理已获得 handle。没有因第二次 open 失败跳过第一个 handle。 |
| dispatch 前中断或写入失败 | 643–651 行先持久化 intent，attempted=null/start unknown，不假称已调用；persist 失败则不触及 spawn。若在 intent 与实际调用之间中断，快照保持“是否调用未知”。 |
| spawn 同步抛错 | 657–688 行 catch 将其记为 spawn-throw，attempted=true，但 startEvidence 仍 unknown、pid=null；之后仍先尝试持久化结果，再独立清理 fd。 |
| spawn 返回 error/非零退出/signal | 666–684 行立即保存 run/status/signal/error，并在 cleanup 前登记失败。故 timeout/ENOENT 等已返回失败不会被之后 close 错误抢成首因。 |
| 两次 close 各自可能抛错 | 695–705 行先移除局部 handle，再各自 try/catch；第二次 close 不受第一次失败阻断。抛错标为 outcome-unknown，不重试该 fd；cleanupErrors 与一般 failures 分列。 |
| Git 输出读取/身份验证抛错 | 708–731 行仅对成功无 signal 的 run 验证，读取和三种身份检查位于单独 try/catch，失败登记 output-validation；不会跳过最终状态持久化而直接丢失命令。 |
| 首因与后续错误 | 571–575 行只有 firstFailure 为 null 时赋值；清理和日志错误另追加，不覆盖早先 open/spawn/process/validation 失败。733–738 行最终快照后，只要 persist 失败或已有首因即 exit1/return。 |
| 外层未预料异常 | 752–763 行回报 processExecution、activeBuildContext、lastPersistedSnapshot 和当前内存 log，并明确 fallback 不保证到达 durable sink。 |

本 reviewer 未发现上述路径还会重现原“整条命令身份未预先登记”或“首个 close 阻断第二个 close”的问题。persist 失败后允许继续做已打开 fd 的必要清理及一次最终快照尝试，但没有后续工具 dispatch；这不构成静默继续构建。

## 执行事实与保留边界

全局 `processExecution` 现在区分 dispatchAttempted、anyPidObserved、lastAttempt；单条记录也分 intent、call attempted、call returned/throw。仅返回正整数 pid 时标记 child-pid-reported，不把调用尝试、返回 error 或同步 throw 推成 started。正 pid 是 API 返回证据，仍不是进程当前存活、全部后代退出、资源已回收或目标构建成功的证明。preflight 的 processExecution=false 描述只读检查自身，不能替代 build 生命周期记录。

快照 `wx` 保全此前字节并提供按序状态；它没有 fsync/原子提交/掉电恢复保证，新候选也没有声称这些保证。失败的快照可能部分写入，lastPersistedSnapshot 只在写入返回成功后推进；stderr 自身也可能失败，代码明确无保证的最终持久化 sink。这是诚实记录的限制，不能将“已发起写入”称为 durable。若执行被强制终止，最近 intent 之后的实际结果仍可未知；本修复没有把该未知伪装为成功或排空。

本次未运行 driver、任何 complete/build 路径、伪锁/假源、open/close/spawn/日志故障注入、CMake/编译/CTest、native/child/FS 实验或 addon/Electron。仅做源码、Git diff、JSON 和现有文件 SHA/bytes 读取；没有借静态审查扩大原执行许可。Node --check、原只读 incomplete 检查如由实施者另执行，应以其真实单独记录为准，本报告不将其冒充异常分支覆盖。

R5 因此仅在新固定候选的静态代码层关闭。九源采用、实际 binding 最低 API、工具/SDK/许可供应、所选 component 执行窗口与后置真实依赖审计仍保原 pending；资源终态、目标 OS/Electron/Windows、生产接线、D2重测和原 Goal 不因日志修复而通过。
