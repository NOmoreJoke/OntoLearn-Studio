# T10 round-1 实际派发回执

2026-10-22，总控短时CUA创建lease内，由T10原owner直接创建两个全新独立任务。两项提交后已开始后台审查，实际设置、完整输入和工作目录已读回；前台核验完成后已明确释放lease。本记录不是指定审查通过。

| 应用 | 实际session / turn | 实际模型与设置 |
| --- | --- | --- |
| ZCode | `session_65271e095f85aad0c95b5e1f512243f1` / `turn_6b38be66-cb82-46f7-836a-43b742cfe944` | GLM-5.3，max；运行时mode=yolo，任务UI完全访问 |
| MiniMax Code | `mvs_41069a5454874e1aa0bd61c40d1daffa` / `854a6900-aadf-4f1e-b035-5806dc1cf2c8` | minimax/MiniMax-M3.1-Flash，xhigh；任务UI始终授权 |

ZCode实际cwd为T10-zcode-review-c3c7e90；MiniMax UI按父项目“本体”归类，但新任务明确选择T10-minimax-review-c3c7e90文件夹，官方llm-call环境的Primary working directory也为该隔离树。未更改T06/T02/stage会话、stdio或设置。

完整原提示通过两应用原生长文本附件提交，收到副本逐字节一致：Z52504B/c76e34d0b2639b1cab23eb0c3f3b7c848cb8ddc8f58e34c7a9e83f80e545b902；M52555B/d8b551c6f4d2bc678849b55e739872f767cac8cc6895c4440097202237fb1587。Z首个真实模型request内Read结果含完整290行；M真实三次read结果（1–134、135–245、246–290）完整含290行，逐行与原文核对。保留accepted附件和实际供给模型的编号文本/初始三read消息，不能只凭“粘贴成功”声称全文受理。

准备提交30ec443173d1f69925679d2f440516c49fa755f8与准备索引SHA83ba084841933e2c2638e6591bc63274efc383627f77b389032285771765f566不改；本目录单独追加实际回执。两个审查树仍detached77；实际执行身份77、产品C、证据A分开。派发后147项固定Git输入长度/hash全符原manifest，147个工作文件均等于执行77；AGENTS为批准de15。新增.mimosa/hook-state文件按实观路径/长度/hash另列，保留原件；未删除、改verifier或仅凭目录名静默豁免其来源/影响。

此处raw入库是为了固定实际派发、全文受理与设置证据；未复制凭据、业务运行库、全应用日志或其他模型本轮结论。UI无效索引曾导致一次取消按钮点击失败，刷新后已正常取消项目编辑；无错误提交或额外任务。两次macOS路径粘贴未改变目录，改用可访问性setValue后实读回精确路径。以上过程未修改产品。之后等待各任务终态与全文报告，再独立处理全部意见；完整父门、双审、CI与远端核验仍保留，Goal原blocked状态不因本次派发重建或标完成。
