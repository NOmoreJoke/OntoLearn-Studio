# T02 round-1 隔离review工作区映射需求（提案）

2026-10-22。仅提案，所有下列路径/分支尚未创建、未批准、未借用；T02尚无模型lease。本次不建树、不安装依赖、不运行测试、不连接后台daemon或创建实际任务。

## 固定基线与需原样携带的输入

建议未来由root批准后，使用本次addendum最终固定docs commit建立隔离review树；其祖先准备提交为 `ce1c3df41a233a07de4ef8fad54d5f201b222a23`，而受审产品仍为 `49321221733ea927484647352e05e7d833cebc86`，base仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，原S1证据process为 `d597b3c00980652042163d250c875d660d4d371e`。实际建树基线须用root核验的**包含本addendum的精确完整commit SHA**登记，不将ce1误称已含新补充。

原冻结双提示取93c1125完整原字节，58项原差异/19产品+5harness及10未变引用、32索引日志和现存Git封存、原14份准备文件及manifest、此次addendum和政策来源快照均逐path/ref/bytes/SHA核同。产品与base间没有新增依赖/锁改动；不借T03 native/D0环境或打断其运行，不采用T01/I05未来供方。

## 建议每个模型各自独立工作区

| 任务 | 未来候选路径（仅提议） | 未来候选分支（仅提议） |
| --- | --- | --- |
| ZCode | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-r1-zcode-review` | `review/weekly-t02-s1-r1-zcode` |
| MiniMax | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-r1-minimax-review` | `review/weekly-t02-s1-r1-minimax` |

每个任务各使用唯一树；允许各自只读核相同产品，不共享可变node_modules/venv/pytest缓存/Vite产物/临时SQLite/证据目录。若root只批准一棵树，须先明确串行运行租约、两套互不复用的deps/cache/output映射和完整清理/保护规则，再执行，不能自动把此提案理解成两树批准。

依赖建议仍放该任务自有node_modules和`.venv`，按原批准锁固定恢复；验证临时路径建议由root批准在各树的 `test-results/t02-s1-r1/` 下分 `tmp/`、`streams/`。已只读核验当前`.gitignore`的`test-results/`、node_modules/、.venv/及既有cache/out规则；实际新树仍须复核规则一致，不新增ignore配置。实际命令环境的TMPDIR、PYTEST缓存和构建产物须记录。若既有命令不能通过现有参数定向临时输出，先辨明其真实生成路径是否只是该隔离树ignored构建输出；会改受保护输入则不执行，不能改测试/配置来绕过。不得在原T02源树执行或把repo公共目录当临时空间。

## AGENTS与报告/原始流映射

新树从Git继承的AGENTS可能是旧版本。需由被授权的启动owner把原受保护AGENTS原字节复制到各自新review树并实际核SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，保持该树未暂存，不混入产品提交；本提案不自行复制，也不从旧Git版本虚称政策已生效。五份原操作快照与本addendum/实际lease同时交付，实际设置独立读回。

建议本方最终报告写入各自review树的 `docs/reviews/T02/round-1/zcode-glm53.md` 或 `minimax-m31flash.md`，完整原始流留各自登记的streams目录；该方不能访问另一方目录/任务/输出。最终由原T02负责人从明确报告输出映射全文读回并封存，不能把UI草稿、任意同名文件或摘要当真实任务终态。

root若要求报告最终仍存原源树，应另登记精确的**仅本方报告/原始流封存**输出权限和安全读回路径；不得扩大为源树测试/构建权限。原提示内的源树报告绝对路径保留为历史默认，实际路径必须由新映射明文覆盖；没有覆盖时不能擅猜或写入源树其它文件。

## 启动前尚需的实际交接

1. root核验此addendum hash及两个review树/环境/输出提案，给明确实际基线、路径和独占lease；尚未发生不能记为创建完成。
2. 原T06完成支持的MiniMax多session/daemon无干扰交接，并说明ZCode官方入口/真实registry状态；原T02随后才按root实际交接作为本线两个新任务唯一创建者。当前T06仍是入口恢复owner，不能同时抢建。
3. 实际逐任务获取GLM-5.3/max/yolo与M3.1-Flash/xhigh/bypassPermissions设置回执、真实taskID、正文接收、prompt/addendum/完整输入hash；保存前后source哈希和每项独立验证的完整原始流/首失败/exit。
4. 任何scope/base/product或测试/配置/依赖/验收变化走原新候选/必要验证/双方全新完整审查门；纯追加本提案和映射不改变受审产品。
