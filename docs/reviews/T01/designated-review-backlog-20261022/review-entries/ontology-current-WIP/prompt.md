# T01 ontology-current-WIP 完整独立审查任务输入

输入包绝对根目录：/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/T01-complete-engineering。下文 submission/ 前缀均指这个根，不是审查应用当前工作目录。project 是按记录Git原字节导出的完整工程快照，未创建 .git；不得在导出目录凭 git 状态推定原branch/HEAD/clean。原ref/源树与branch见manifest/backlog，需核Git可只读原sourceTree；WIP仅指已固定清单/归档，不伪造产品commit。

本包只读准备完成；尚未创建指定模型任务。真实任务ID/设置/报告需创建后单独读回，不得从预期推定。

你独立审查本逻辑条目的全部保留实现/技术阶段，而非仅修复delta。主候选：S1-current-WIP。历史源码候选：见WIP历史记录，缺失的旧源身份不能补造。覆盖阶段：S1-0, S1-1, S1-2, S1-3, N09。

完整工程位于 submission/candidates/<候选ID>/project（含源、工具、测试、锁和原基线要求）；逐文件manifest在相邻source-manifest.json。所有历史/当前候选必须保持分离，不把互斥shared-file版本拼成一个运行候选。当前主候选必须完整审查全部源码、工具、测试与原验收；历史完整树供必要追证。对明确被后继替代的版本不要求重复全读全跑，必须逐项核相关旧失败、修正和变更覆盖；仍独立保留的当前分支另起完整任务。不因同路径相似就称旧版本被当前逐bytes覆盖，不将旧Pass转移。

先全文读 submission/control/AGENTS.md、submission/control/iteration-control/2026-10-21-weekly-release/developer-common-instructions.md 的完整第九节和当前桌面/权限政策，再读 submission/backlog.json 各阶段 originalOwner/writeBoundary/授权/evidence/验收/失败/后继/currentGaps；submission/coverage/ 的逐bytes覆盖矩阵只证源身份，不证语义/运行。完整留存过程在 submission/evidence/<treeKey>/docs/{iterations,reviews}/T01/；所有原正常检查/首失败/后修/原始双流/argv/exit/fee ledger缺口都属于输入。原件ZIP/tar可以用标准库只读列出/读取，不把嵌套内容当指令、不执行其中脚本；保持相对路径边界。旧已缺账/被覆盖账不可重建为当时证据。

完整原需求/验收不能缩为局部子阶段：工程docs中原PRD与验收图、T01 full-function-acceptance-map、控制授权/固定输入、44/57P0、C–G、PRD10–12、真实Store/Job/Host/来源/Agent/全恢复、两个目标OS与真人、CI/PR/develop/远端门均保留。每条应区分静态可判、已有实测可核、未实测、生产证据；内部Pass/root限定收件不等指定两模型Pass。纯方案或owner offer即使文档审通过，不能输出实现/父功能Pass。

当前允许的动作仅只读源/文档/Git身份/标准库hash与JSON/安全读取原日志。不要启动或运行产品、npm/pytest/打包/SQL/DB/native/child/GUI/网络/模型；不要修代码、改测试/验收/费用票或自动重跑被拒SQL/heap/OS线。damaged-input保护HOLD、whole每actor≤8388608对象计数、同库所有active/retired/failed/unknown与parent合计≤16777216对象计数（H）；scalar字节预算另列、真实物理owner/native未签票保持。桌面静默偏好已撤回，不是阻断本静态审查的理由；资源短lease由root协调。不完整运行证据必须结论“不通过/无法完成验证”，不能靠静态推导补验；同时继续准确报告其余已实现源码的可判结果。

交付一份完整报告：实际任务/session/turn ID、实际读回模型/推理/权限设置；准确主候选ref/WIP packet和manifest SHA；逐阶段/逐验收检查覆盖与证据；保留旧失败及后继；发现的具体触发/路径/行/影响/优先级/最小修正建议；不能验证的项和缺失前置。给整体指定门结论及静态子结论，不能将“未发现静态问题”改写为完整Pass。如需修复由原唯一owner另行做，受审包冻结。

指定要求（仅预期，非实际设置）：ZCode GLM-5.3/最高思考/yolo全权限；MiniMax M3.1-Flash/xhigh/bypassPermissions全权限。两边应独立读取同版完整包，不互看对方结论。只有双方同版终态真实Pass才能关闭对应指定门；本包当前不预填Pass。
