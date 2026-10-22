# T08 全量指定双审积压盘点（2026-10-22）

本附录响应总控核验的人类“把之前没有通过zcode和minimax的审查都补上”授权，仅登记全部保留实现与技术准备，不新造候选、缩减原验收或假称ready。依据为本线Git对象、既有验证/内审原件和当前工作区。以下四批名称沿用status中的历史批次，不是新设S1或新增产品验收阶段。

## 固定身份和写面

- 原owner聊天/Goal：`01a15bc2-40dd-7393-a1cb-1e87086e6993`，原Goal保持blocked，没有重建或恢复。
- 唯一worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`。
- 分支：`feature/weekly-t08-agent-model`。
- 四批实际批准base均为`5f910b52c69d86a1076b2032e5d3c63e715947f3`，未刷新或消费未批准依赖。
- 当前累计product：`93516fa8455cf4b195cbfb699aa7a6652d428b6f`；盘点开始时process HEAD：`9f1b9af6bf3ba26a21ce1a928cdb53131d1c7f2f`。本附录及原日志归档只产生文档/证据process提交，不生成新product。
- 原owner写面：`apps/desktop/src/main/agent/`、`apps/desktop/src/renderer/src/agent/`、`tests/unit/t08-*.test.ts`、`tests/fixtures/agent/`、`docs/reviews/T08/`、`docs/iterations/T08/`。没有shared contracts、App、bridge、Store、gateway、依赖锁或CI写权。
- 盘点时只有受保护AGENTS未暂存，当前SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。这是已传播的桌面政策版本，不修改或暂存它；旧内审/manifest的旧政策哈希保留历史。

## 全部已开发实现及历史后继

| 历史批次与实际范围 | product SHA | 当时最终process SHA | 验证与独立内审 | 当前关系及完整验收状态 |
| --- | --- | --- | --- | --- |
| 第一批：严格DeepSeek文字非流式codec、私有白名单/可信证据/草稿、能力判定、context-actions、v1合成评估 | `9bfd3105a2f847771d8039b93e6615fa94c4fdfa` | `f2215d94e11d875ab6147aa989a08d1f70957752` | evidence/verification.json；check 679 TS/1052 Python；verify:sources通过；内审1不通过→内审2固定候选修复复核通过，49定向 | 被第二、三、四批增量继承；不是撤回/删除。真实API、最终字节授权、实际领域与父验收未完成 |
| 第二批：纯会话交换、防重放/预算/取消、新用户轮次隔离、失败/取消后草稿收据保留 | `af9e59f7ce856521e751fcf23f417fdd3377e2da` | `5f9f085de4e619e70a4e39df3d2e8add5860507c` | evidence/verification-af9e59f.json；check 691 TS/1052 Python；内审3/4不通过→内审5固定候选通过，61定向 | 被第三、四批继承；真实传输/持久任务取消及领域服务仍未接线 |
| 第三批：私有AgentSidebar、呈现/CSS、完整上下文快照、local/retry禁用及SSR | `3a4c2ea29da12afe2a4f2e8f8504331e9f8cf967` | `4a2abbaf3b996d3898782d73eee632f1d4866b65` | evidence/verification-3a4c2ea.json；check 706 TS/1052 Python；内审6不通过→内审7固定候选通过，76定向 | 被第四批继承；组件未挂载App，SSR不是事件交互/真实页面/native/两OS验收 |
| 第四批：获准T09固定输入、独立RDFLib/CSV真实库探针、v2评估及SPARQL原字节修复；累计包含上述全部实现 | `93516fa8455cf4b195cbfb699aa7a6652d428b6f` | `9f1b9af6bf3ba26a21ce1a928cdb53131d1c7f2f`（本附录前） | evidence/verification-93516fa.json；check 717 TS/1052 Python；内审8固定候选通过，87定向；fixed-input-actual-observations.json | 当前冻结累计product；真实库执行只在test-only probe，手工模型消息不是实际模型，不能替代T03/T04/I05正式工具或11.3/12.2 |

上述验证数量均为各时点实际结果，不累加为通过数量。本次只重算文件哈希，不重跑上述命令。

第一批内审1对应提交前初版（agent-service SHA见原报告），没有独立product提交。第二批失败固定候选依次是`960d374cbb203752cd61fb4c42c6eed0df1cf521`（内审3），修复至`9641446a6c53c02d95b069a29235c92d956254eb`后内审4仍暂不通过，再修复至af9e59f通过。第三批内审6对应冻结前初次侧栏工作区；没有将其事后绑定到3a4c2ea冒充初次通过。全部原失败和处置继续保留。

## 两指定模型的真实积压

四批以及上述失败中间候选：**ZCode任务ID=null、MiniMax任务ID=null，实际设置读回=null，指定报告不存在，指定结论=未执行**。本线没有任何指定Pass、指定Fail或已撤销指定任务，也无等待中的session/turn/stream。`internal-review-1.md`至`internal-review-8.md`均来自Codex独立agent `/root/t08_internal_review`，不得填写为ZCode/MiniMax任务。

尚需的指定设置为ZCode GLM-5.3/最高、默认yolo，以及MiniMax M3.1-Flash/xhigh、默认bypassPermissions；这只是门禁要求，不是实际设置证据。root未给T08创建租约，本次未创建任务、操作GUI或使用模型，不占T06资源。

旧内审Pass只能说明各历史固定候选的已列范围。第二批改agent-service，第三批改conversation/上下文并新增UI，第四批改tools的SPARQL校验及评估输入；因此不能把内审2/5/7当作当前累计候选的完整通过，更不能转成指定Pass。内审8是当前累计候选的本地独审，仍不代替指定双方。政策/证据process变化本身未改变执行输入，不因此重审。

所有历史行继续登记，状态为“被当前累计实现继承，指定双审尚缺”。可把当前93516fa累计scope与四行关联后由root精确授予补审范围；不能仅审v2新增探针而遗漏旧codec/会话/侧栏。若root要求历史SHA专项补审，应保留该任务自己的base/head，不能回填为当前候选Pass，也不把修复前失败代码恢复为产品。没有历史正式撤回实现或替代分支。

## 原验收与真实就绪缺口

原任务local_service_acceptance仍为FR-800..806、900..902、904，A-01..05/09/10，实际Q9服务与各相关领域工具，以及11.3、12.2；未改为纯单测/SSR门。

1. I06：获批唯一模型配置/安全存储/最终messages、tools、reasoning、历史、错误逐字节溯源与授权接口；实际连接/JSON/工具往返和最小调用记录、费用硬上限/主体权限仍未验。T08只编码数据，不发送或保存凭据。
2. T01/T02–T07：真实项目/版本、Diff/真人确认/原子事务/撤销，以及各实际查询、映射、推理、行为、沙盘结果与轨迹服务。T08默认端口不可用；测试注入和固定图不构成已批准领域接线。
3. 公共接线/页面：T00公共命名映射、共享bridge/App的明确owner接线；T09真实本地处理和辅助记录。当前侧栏未挂载，持久草稿/输入恢复、离线连续性、真实用户事件/视觉/可访问性尚待验证。
4. 质量与父功能：真实模型正式模式和11.3完整集合/语义反例/真实映射/开放世界和依据链/沙盘逐轮解释、A-10零伪造、12.2闭环未完成。模型设置功能未在T08实现，不以I06方案当成已交付。
5. 原发布门：完整同候选指定双审及全部意见、必要e2e/package/native、Win11/macOS15、真人验收、push/PR/实际CI/正常合并/develop远端均无本线通过证据，父P0未关闭。

桌面静默/等待用户时段/先CLI登录已按2026-10-22政策撤回，不再列为阻断；具体T08外审创建只待root内部短lease。该政策不解除上述接口、真实服务、费用/密钥、SQLite HOLD、阶段运行票或自动审批拒绝的独立边界。

## 可独立补齐的下一行动

- 当前已完成且本次可独立补齐的是：全量积压身份/历史关系、原件与提示边界登记；本附录已完成，无需造新实现或重测。
- root可先明确纯代码技术补审范围及短创建lease，以当前累计93516fa覆盖四批保留实现，附当前政策和本附录，将真实API/领域/UI未验逐项交给审查者判断；不能要求其用静态Pass替代原完整功能验收。最终任务base/product/process、实际模型/权限和报告必须创建后真实读回。
- 真实集成只能在具体owner提供批准版本/接口与相应阶段授权后逐项推进；原本线已写精确接口需求于design-and-integration.md，不复制他线gateway/契约/Store。若发现缺陷，沿本线独占范围修复并新候选、新必要验证、双方同版新完整审；共享文件先具体交接。
- 尚未获得真实接口时，不永久删除积压，也不重复无变化验证、猜测生产状态、解冻旧候选或改变原Goal终态。

## 固定清单与原件入口

- `evidence/verification.json`：SHA256 `21c3734c0c8a29b957fe4a9f7427a6dfb44a982956618cfbe410b48c2426792a`，11项历史Git文件核对一致。
- `evidence/verification-af9e59f.json`：`b3f58af40f9cd5cc0464c422c83310590a0a9f316a65ff941d0f5b1512a0e513`，13项历史Git文件核对一致。
- `evidence/verification-3a4c2ea.json`：`8ba6df7bc747a0dc999d836ab04797943a8ba594b0a58e9325ee438057e4a786`，17项历史Git文件核对一致。
- `evidence/verification-93516fa.json`：`da86847a0eb36e3bbdcb244409ffe9b8a930455d229b1bdd442b702dd53c9eba`，25项历史Git/当前文件核对均一致。原manifest不改。
- 既有`/tmp/t08-fixed-check.log`实际仍为SHA `ecdc2edea5df90cc96bf59cd29116fc8106d13135d78699da4e31af18e8845ce`，本次逐字节归档为`evidence/check-93516fa-original.txt`，同SHA；这是旧运行日志原件保全，不是新执行。
- `internal-review-1.md`至`internal-review-8.md`完整意见与关闭关系保留；内审8 SHA `f63758c7673fca9c1ac77639fd75a0e2e08ecf784f9d8feea3d7f06142e11b0c`。
- `tests/fixtures/agent/manifest.v2.json` SHA `02165ae0a93193d04e84bf21e051dc926f9555376fe37f6fcea2352d9b4a3459`，继承v1全部真实验收；`evidence/fixed-input-actual-observations.json`、三份首次失败gzip/元数据及T09输入验证原件保留。
- `docs/iterations/T08/design-and-integration.md`为边界与接口提案，SHA `67c46408e9b7277e1ea5c7121310cf9afabecb9b6fa3521018839905d0b7d900`。它不是第二gateway/公共schema，也没有指定Pass。相关纯模块内审覆盖了边界检查；并无另一个已指定审查通过的“设计阶段”报告。

没有其他本线已开发或保留的模型设置/实际API/领域适配/UI挂载/native实现。未实施项作为父功能缺口登记，不伪造product SHA或审查任务。
