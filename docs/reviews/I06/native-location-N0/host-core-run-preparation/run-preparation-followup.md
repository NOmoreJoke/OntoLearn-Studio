# N0 host core执行准备：信号合同定点复核

2026-10-22。结论：**P2-RUN-01在文案层关闭，无新增准备合同阻断；仍为PREPARATION_ONLY_BLOCKED，不是run-ready或执行批准。** 现有executor实际信号能力、新产物/used、隔离条件及根一次窗口都没有由本次复核补成事实。

## 固定输入及实际范围

本次固定process ref：`fbebc7c716a55e7f3f017b69a1d0b8074f1aab87`；对照首审process/product ref `b59239f9c1ec2774c7922f95dfc67db4dc8754e8`。只读取固定Git内容、两版实际diff及必要本地首审原件，不读可变实现。

| 新process输入 | bytes | SHA256 |
| --- | ---: | --- |
| `plan.md` | 6511 | `8f1721037c690ad5b7e712e41f4099aeb64ae24dc4a75c76acd9fc5b1850517c` |
| `execution-plan.json` | 6938 | `f53f83258eb81b30f61832fe9bbe22efbf94eb71dc6c627be823c2f628891ac8` |
| `signal-state-disposition.md` | 1064 | `e5a2afa55a5c2327941fe5bc5332bdaddc49ddf3ce773c9a6f18e038e0411168` |

均由本人实际读取字节并实算；plan及处置全文读回，JSON完整解析并对照实际diff。九件产品/测试Git blobs与b592逐字相同，没有重新编译、运行或重开产品源码审查。

首审 `run-preparation-independent-review.md` 当前工作区原件仍为11167B/SHA256 `f0b04ff57dba81f0e5a6141e6be0903b3f8c137eca7f928ee4ba9202f2d9cafb`，未修改。该文件不在fbebc7c的Git树中：初次尝试按该ref读取它，git show返回128、静态Python读取命令exit1；随后按其获准工作区路径读回，哈希与原交付吻合。此区别仅为原件存放位置，不是假称该process ref已经收录首审，也不是产品运行失败。

本人唯一新增为本文，不改首审、计划、九源、AGENTS、依赖或T03 WIP，不提交。所有shell显式cwd为本N0工作树；纠正来源位置后的Git/JSON/hash静态读取正常exit0。未编译、执行产品/测试/断言/runner、动态加载native、进行FS/child实验、安装工具、GUI/凭据/模型或Goal操作。

## P2-RUN-01关闭依据

新plan明确由现有executor在**本次core子进程**exec前设置：SIGCHLD=SIG_DFL且无SA_NOCLDWAIT、SIGTERM=SIG_DFL，并清空继承signal mask；probe继承同一条件，全程无外部reaper。仅调整本次子进程，不改host或全UID。

JSON processControl.preExecSignals逐项对应，明确TERM unblocked、empty mask、restoreSignalsAloneIsInsufficient、noExternalReaper，以及能力未被executor证明时继续BLOCKED/不开发新runner。pendingFrontDoors也保留该实证供方要求。因此原来仅靠envreplace和sole-waiter名称而遗漏signal内核状态的文案缺口已关闭。

这不表示signal已经被设定、SA flags已经被本机查询，或任一Popen/preexec实现已安全可用。具体既有executor、调用线程条件、实际pre-exec控制与记录尚需根给来源；若不满足，不得用默认环境、restore_signals=True或临时wrapper替代。现文案没有预先批准产品/runner修改。

## 实际diff及BLOCKED边界

两版plan只新增信号前置段；JSON版本改2，sourceRepair绑定已固定b592并说明新build仍缺，新增preExecSignals，并把相应实件列入pendingFrontDoors。独立处置准确保留首审P2，没有改写首审为无问题。未见对资源预算、目标OS、路径、输出、kill权限、产品所有权或一次运行次数的扩大。

本人重新解析确认：admission仍PREPARATION_ONLY_BLOCKED，artifactExecutionAttempted=false，resolvedCoreArgv=null；旧b657产物仍superseded/no execution，不猜新路径。未从源码修复已静态审查跳到旧产物可运行。

此前确认的5owner/153cap/457B、2spawn/1已知未结child、显式FD峰值5排除stdio/loader/runner等源级预算不变；它们不认证实际资源峰值。固定/tmp不受TMPDIR隔离、无确权不glob删、不替native sole-reaper、仅原未reap本组有限控制、20s仅logical预算、CORE0不保证无OS自动提示等边界继续保留。

精确新artifact绝对路径/bytes/SHA/inputDigest及实际used/许可闭包、T03正式采用重构建、现有executor对stdio/signals/limits/未reap时序的实件、需要时的隔离CLI环境、根精确一次窗口仍缺。本文不代签其中任一项。

## 最终限定结论

对固定fbebc7c：**信号准备P2文案关闭，当前无新增需修产品或准备文案事项；可以连同首审交根继续审议。** 当前不具备run-ready，不构成根完整批准；未运行任何产物，不证明N0宿主case、macOS15/Win11目标或完整N0技术通过。后续实际执行只能基于新精确供方和根显式窗口，不能由本次关闭自动派生。
