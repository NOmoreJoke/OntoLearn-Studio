# T10 round-2 实际创建与全文受理

总控在T01释放后给T10唯一短GUI创建lease，原owner经CUA各建一个全新完整任务，未复用旧会话。两项前台创建/设置/输入读回完成后即明确释放，后续仅后台只读核验；无其他任务/stdio/设置更改。

| 应用    | 实际session / turn                                                                       | 实际模型与权限                                     |
| ------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------- |
| ZCode   | `session_51c6a1c550181572a24f331b9a5c5e23` / `turn_024c2267-49dd-4c90-9e0a-8dd9b61c5b43` | GLM-5.3 / max；runtime yolo，任务UI完全访问        |
| MiniMax | `mvs_d314cc7a43c84a559e31d5ddf3663af7` / `5ad5f9d9-3db0-4872-86ab-04fbb3375fd3`          | minimax/MiniMax-M3.1-Flash / xhigh；任务UI始终授权 |

实际workspace均为各自T10-*-review-r2-66cc152。Z有独立项目；MiniMax界面归于父“本体”项目，但任务文件夹选择及真实模型Environment Primary working directory均为精确minimax隔离树，未以父项目标题代实际cwd。

两应用原生长文本附件收到副本与冻结全文byte-exact：Z106452B/a612c2e88c0f5da41d0dd2860215ec95d83d3756e9cf94a7e21e301eb789f830；M106507B/a503367fc7b686c28bf35f4a314dbd0ae116cfa7a1409f523fb9e78a29795941。不是只凭UI缩略：Z首请求自动追加Read先含1–551行，模型首工具Read(offset552,limit2000)补552–667；MiniMax五个真实read结果为1–123、124–238、239–450、451–587、588–667。逐行全部等于冻结完整667行；Z原读取结果中的668行仅空白格式尾行，不计入正文。

可提交的两个`*-prompt-read-evidence.json`仅投影本人提示的编号全文、实际request/message/toolCall标识、已知调用参数、覆盖和hash；未知自动Read调用标识保持null。完整上下文原件含系统/skills/reminder/thinking等非必要内容，仅在Git忽略的`out/t10-review-round2-private-source/`以目录0700、文件0600保留，不提交或共享；见`private-source-retention.json`。MiniMax该初始读取链实际保留12条消息，已纠正先前口头11条的计数；共享副本仅含5个Read结果中的本人提示行。runtime事件也仅保留自身session的必要启动字段，没有导出请求headers或后续推理流。官方应用原始日志与附件未修改或删除。

启动后两树各225项固定Git/工作文件逐项hash/长度匹配66cc152，各11输入副本仍一致；唯一tracked差异是受保护AGENTS/de15。额外.mimosa仅列path/lstat及路径中是否明确含自身session，不读取metadata内容或hash，不窥探peer，不删除或改verifier求绿，未知归属保持未知。

创建入口第一次click未激活MiniMax菜单，第二次打开；文件夹对话框初次快捷键未进入路径框，重新按键后setValue并精确读回，未选错目录提交。没有额外错误任务或首测试失败被丢弃。本次没有重跑不变产品测试、GUI产品验收或重写冻结输入。initial-launch-receipt是当时Z turn尚未知的原始记录，后由真实模型request补齐于正式receipt，未回填猜值。

收据状态仅实际启动与完整输入受理，正式模型终态/报告/全部意见仍待；不能据此给新候选Pass，也不沿用round1的通过。原完整父门和Goal blocked不变，未push/PR/CI/merge。最小派生证据入库用于固定逐任务模型/权限/cwd、完整供给链及源输入保护证据。

新README及派发JSON元数据曾有Prettier排版警告，已仅格式化新文档与JSON结构；编号行文本、原附件、私有原件、冻结输入和原报告均未改写。
