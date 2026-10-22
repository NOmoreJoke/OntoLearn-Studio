# T08 全量累计实现独立对抗审查报告（zcode / GLM-5.3）

- 角色：zcode（本轮唯一指定审查方之一；另一模型本轮意见未读、不引用）
- 报告路径：`docs/reviews/T08/review-runtime/reports/zcode-glm53.md`（唯一写面）
- 结论文本见第 11 节，结论类型：**不通过（NotPass）**。

## 0. 结论摘要（先行）

对固定 product `93516fa8455cf4b195cbfb699aa7a6652d428b6f`（base `5f910b52`）的全部 25 项实现/测试/fixture、44 项完整差异、828 项产品树做了全文阅读与受控验证：

1. **纯模块实现层未发现新的 P0/P1/P2 缺陷**。codec 严格拒绝未知/截断/空/非法结构并保留必需 thinking 字段；工具整批预验、可信上下文前后复验、收据完整性与防重放/预算不重置等设计在固定代码中成立并有测试支撑；侧栏为纯 props 驱动、React 文本转义、无网络/凭据/确认入口。本方独立运行全量 check（717 TS / 1052 Python，exit 0）、t08 定向 87 项（exit 0）、固定输入探针五例直连复现（A01 / 空 / 同数量语义错 A02 / QUERY_SYNTAX / CSV 字符串身份）全部符合。
2. **完整原验收不通过**：真实 I06 最终字节授权与安全传输、T01 真实 Diff/真人确认/原子事务/撤销、T02–T07 真实领域端口、真实 DeepSeek 主体与消费上限、App/bridge 挂载、e2e/native/两 OS/真人验收、CI/合并/远端全部缺失。按"关键验收缺失不得 Pass"的门禁，整体结论为不通过；下列"静态无问题"仅限已实现局部，不得拼为整体通过。

## 1. 真实任务身份与应用来源（读回）

- 应用来源：ZCode 桌面官方任务（owner 经 CUA 官方 UI 创建并提交，见本方受理记录引用的两份收据）。
- 会话：`session_cd996c3a9b47f03713b41eaae59a83b0`（来源 `metadata/owner-ui-submit-receipt-20261023.json`，官方 More > Copy session ID 读回）；**turnId：UNKNOWN（官方菜单补记前保持未知）**。
- 模型/思考/权限：GLM-5.3 / 最高（max）/ 完全访问（yolo）。依据为 owner 收据读回与本任务实际运行事实；按指示未扫描 globalconfig，用户级配置不充当本会话即时读回证明。
- 受理记录：`metadata/zcode-glm53-acceptance-20261023.json`（含全部核验项）。

## 2. 固定身份与输入完整性（本方逐项核验）

| 项 | 值 | 核验方式 |
| --- | --- | --- |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-zcode-review-93516fa` | `pwd` |
| Git | detached HEAD `5b64bfea538b638310cd3ce79e595c3b482e003d`；`M AGENTS.md`（受保护 de15f6ce…，未 stage）+ 未跟踪过程目录 | `git rev-parse` / `git status` |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3`（commit 对象存在） | `git cat-file -t` |
| product | `93516fa8455cf4b195cbfb699aa7a6652d428b6f`（commit 对象存在；`git ls-tree -r` 恰为 828 项） | `git cat-file` / `ls-tree` |
| 完整派发正文 | 59804 bytes / 373 行 / SHA256 `8951b0e305e9326dbb41ff8a2f16c4de5f1c35dc0163d19601b2daa08683029d`，与用户声明官方附件一致，全文读取 | `wc` / `shasum` |
| 旧公共输入正文 SHA | `8f361f4d984511214111f85fa26c649e844ccda7896c4e5f1041f736f47d805d`（派发正文内声明，前缀逐字保留） | 声明核对 |
| 旧 input-manifest | `33deedd2aaeb18852d513bef4d46ab047a27ded380d7fff9ef03e3eb9e9ba317`，284867 bytes，本树实测一致 | `shasum` |
| dispatch-manifest | `7bf46a2f89762a1fd0880265ccb16d7eb0037b859417ef94092479695358e472`（61942 bytes） | `shasum` |
| source-git-bytes | `60712efc110e2adb605819dcfff0585f6adfaf64330d56fcb3a4f88490de9cc2`；941 tracked 文件、策略外不匹配 0；本方抽查 257 项 git blob 哈希全对 | 读取+脚本核对 |
| 25 项包文件 | 快照（`inputs/product/…`，源码带 `.snapshot` 后缀）＝ product git 对象字节，25/25 全等；工作树同字节 | 逐字节比较 |
| 44 项差异 | `git diff --name-status base product`：25 项包文件 + 19 项设计/证据/内审文档，全部为 A，与 manifest 一致 | git |
| 环境 | 本树 node_modules/.venv 均为真实目录（非符号链接），editable .pth 与 direct_url 指向本树 packages/engine；setup 锁前后哈希不变 | `environment-source-binding.json` + `setup.json` 读回 |

## 3. 全文阅读覆盖清单

以下全部**全文**读取（非摘要）：

1. 派发正文 373 行（含旧 prompt 前缀、执行补充、四份政策逐字快照）。
2. PRD V0.6 全文 1255 行：FR-001..FR-1001，重点 FR-800–806、FR-900–904（FR-903 保持 P1）、FR-204/302/400 协作；附录 A–G 全部（C 能力矩阵、D 失效表、E 行为/沙盘语义含 E.5 固定模型、F Agent 授权表、G.0–G.6 含 G.5 A-01..A-10）；第 10–12 节全文，含 **11.3 全部九类**与 **12.2 全部七项**。
3. 控制器输入：`requirements.csv`（60 行全 FR 门）、`acceptance-baselines.csv`（51 行全部"未核验完整产品通过"）、`plan.md`、`decisions.md`、launch prompt、任务行（后三者为范围确认）。
4. 25 项包文件全文：`agent-service.ts`(340)、`capabilities.ts`(80)、`conversation.ts`(222)、`deepseek-codec.ts`(180)、`errors.ts`(21)、`tools.ts`(85)、`AgentSidebar.tsx`(290)、`agent-sidebar.css`(181)、`context-actions.ts`(42)、`sidebar-presentation.ts`(81)；测试 `t08-agent`(361)、`t08-codec`(201)、`t08-conversation`(394)、`t08-evaluation`(115)、`t08-fixed-input`(268)、`t08-sidebar`(196)；fixture `fixed-input-probe.py`(105)、`fixed-input-cases.v2.json`、`manifest.v1/v2.json`、`synthetic-cases.v1.json`(779 行 13 案逐案)、`t09-873c8c0/{G-base.json(273),equipment.csv,origin-manifest.json,unclosed-high.rq}`。
5. 其余 19 项差异全文：`design-and-integration.md`、`internal-review-1..7.md`（product 内）＋ `internal-review-8.md`、`policy-receipt-2026-10-21.md`、`status.md`、`verification.json`、`verification-af9e59f.json`（结构+要点）、`verification-3a4c2ea.json`（结构+要点）、`verification-93516fa.json`（全文）、`t09-input-verification.json`、`fixed-input-actual-observations.json`（结构+关键值）、三份首次失败 gzip 的元数据 JSON、`check-93516fa-original.txt`（归档原件，其 SHA `ecdc2ede…` 与 backlog 声明一致）。注：三份 `.gz` 原始字节与两份中间候选 verification 的逐字段全文未展开，其关键声明（数量、SHA、文件清单）已通过 backlog、verification-93516fa 与本方独立运行交叉核验；该限制不影响任何结论方向。
6. `acceptance-evidence-map.json`（107 行导航矩阵，全部如实标 not-passed）、`dual-review-backlog-2026-10-22.md`、`dispatch-manifest.json`（顶层字段）。

未读：peer 本轮任何材料（按盲审边界拒绝读取）；原开发树（历史地址仅作来源记录）；`.venv`/`node_modules` 内容除绑定核验外不作实现依据。

## 4. 本方实际验证（全部在本树、本 run 目录、raw 落盘）

| run | 命令（要点） | exit | 结果 | raw |
| --- | --- | --- | --- | --- |
| run-001 | `env -u ROOT_SOURCE_PATH -u ONTOLEARN_TEST_ENGINE -u PYTHONPATH UV_PROJECT_ENVIRONMENT=<本树.venv> VIRTUAL_ENV=<本树.venv> TMPDIR=<run>/tmp PYTEST_ADDOPTS=--basetemp=<run>/pytest npm run check` | 0 | lint/format/typecheck 通过；vitest 21 文件 **717** 项全过（含 6 个 t08 文件与真实探针）；build（electron-vite 编译，未启动 Electron）通过；ruff 通过；pytest **1052** 项 56.94s 全过 | `raw/run-001-check.txt`（SHA c201ad04…） |
| run-002 | `.venv/bin/python -I tests/fixtures/agent/fixed-input-probe.py {Q-01,Q-02,Q-01-semantic-wrong,Q-01-syntax-wrong,CSV-original}` | 0 | Q-01→仅 A01；Q-02→空且 inputSha256 与 Q-01 不同；semantic-wrong→A02（与 Q-01 同行数、不同成员、querySha256 不同）；syntax-wrong→`QUERY_SYNTAX`；CSV→001/泵站A(行2)、002/泵站B(行3) 字符串身份 | `raw/run-002-probe-direct.txt` |
| run-003 | `./node_modules/.bin/vitest run tests/unit/t08-{agent,codec,conversation,evaluation,fixed-input,sidebar}.test.ts` | 0 | 6 文件 **87** 项全过，与内审 8 及归档日志计数一致 | `raw/run-003-t08-targeted.txt` |

完整性脚本核对（无产品命令）：25/25 快照＝product 字节；verification-93516fa 的 25 项文件哈希全对；source-git-bytes 抽查 257 项 blob 全对；828/44/25 计数全对。

产品接线状态检查（grep）：`main/index.ts`、`main/task-service.ts`、renderer `App.tsx` 均无 agent 引用；agent 目录无 fetch/http/net 面（仅 codec 内 DEEPSEEK_ENDPOINT 常量与文档注释）。**侧栏未挂载、工具未接线**，与声明一致。

## 5. 按必查问题清单的实质结论

### 5.1 codec（deepseek-codec.ts）
- **严格拒绝**：请求/响应均 zod `.strict()`；未知字段（含 `endpoint`、`api_key`、`temperature` 等调用方键）拒绝；`finish_reason ∈ {length, content_filter, insufficient_system_resource, aborted}` → `INCOMPLETE_RESPONSE`（截断/过滤不得产出答案）；空内容、非法 JSON、usage 总量不一致、重复 call ID、`tool_calls` 与 finish_reason 矛盾均拒绝；请求/响应各 512KiB 上界；文本 262144 上界；消息 2..100；`decodeStructuredContent` 对 schema 失败拒绝。**真实通过（本方 run-001/003 + 静态）**。
- **thinking 保留**：`mode=enabled` 且携带工具时，历史中所有 assistant（含无工具调用轮次）缺 `reasoning_content` 即 `INVALID_PROTOCOL`；`conversation.acceptResponse` 在执行任何工具前再检一次；重放往返保字段（t08-codec:72–87、t08-conversation:71–126 实证）。不静默退模式：`thinking.type` 恒由受信 mode 决定，`reasoning_effort` 仅 enabled 时出现。**真实通过**。
- **多轮 ID 一致/重放**：`seen`/`pending` 集合保证工具结果紧跟、不孤儿、不重复、不复用；标点 ID（`call.provider/1`）按协议 schema 一致流转，空/超长 ID 拒绝。**真实通过**。
- **仅数据编码非第二网关**：`encodeChatRequest` 只产出最终 body 常量；不做授权判断；`projectToolMessage` 明示"最小化助手、非 I06 授权决定"，草稿/失败正文默认不回传 provider。分层正确。**静态通过；最终授权属 I06（未实现，见第 8 节）**。

### 5.2 工具边界（tools.ts / agent-service.ts）
- **整批预验**：`executeCalls` 先对全批 `prepare()`（名称白名单→参数 strict 解析→端口存在→`ontology_read` 的 objectIds ⊆ context.selectedObjectIds）再执行，批内重复 ID 拒绝；恶意后项导致零领域执行（t08-agent:59–74 实证）。**真实通过**。
- **可信上下文**：`contextSchema.strict()`（project/revision/snapshot/scope/module/mode/选中对象≤100）；执行前、每个结果回收时、答案解析时三重复验；适配器收到的是 `structuredClone` 的上下文与参数；上下文漂移→`STALE_CONTEXT`，迟到结果不落账（t08-agent:197–213）。**真实通过**。
- **读/草稿/隔离运行分级**：`toolAccess` 三类与结果 kind 强校验（read→evidence、propose→draft 且 draftType 必须匹配对应工具；behavior_test/scenario_run 为 isolated-run）；默认无任何端口即无任何工具；构造器拒绝白名单外端口键（`commit` 注入→`TOOL_NOT_ALLOWED`）；不提供 commit/confirm/undo/restore 工具。**真实通过**。
- **取消/超时/迟到**：每调用独立 AbortController+timer；预取消、执行中取消、超时均转固定 failure 收据；晚到适配器结果被忽略且不可再引用为成功（t08-agent:214–244、t08-conversation:207–230）。真实任务状态与本地等待区分（文案明确"实际任务状态请查运行记录"）。**真实通过**。
- **预算/防绕过**：批前 `calls+consumed>maxCalls` 拒绝；`usedCalls` 全会话防重放；`beginUserTurn` 只清收据不清 ID/预算（t08-agent:347–361）；会话层 maxExchanges/maxTokens/maxTotalRequestedTokens 在 `prepareExchange` 占用且失败不退还。**真实通过**。

### 5.3 收据与可信回答（agent-service.ts resolveAnswer / conversation）
- 同一问题内存在任何工具收据时，宿主以**全部**收据为答案体，模型选证据/建议/不确定任一分支都不能删减或只引成功项（t08-agent:300–327）；伪造 callId→`INVALID_EVIDENCE`；自由成功文本→`INVALID_JSON`；无收据时仅允许 6 选 1 固定教育模板（带"模型建议，未经确定性工具验证"标签）或固定不确定文案。stale/historical/failed/cancelled 状态原样保留。**真实通过**。
- 跨问题隔离：新用户问题清本轮收据；旧 callId 引用被拒（t08-conversation:250–285）；provider 失败/预算尽/三工具批中途取消后已完成收据与草稿仍可从 `state().localReceipts` 只读克隆读取，快照不可反写（t08-conversation:287–394）。**真实通过**。
- 注：以上"真实通过"指**本方受控运行+固定代码静态审查**层面；恶意/低质模型在真实评估集上的表现属 11.3（未验，见 8.2）。

### 5.4 字段投影与外发授权（FR-902/A-03 向）
- `projectToolMessage` 按 allowedFieldIds 过滤 evidence 字段、丢弃 traceRefs/resultId 等；草稿/失败仅回 `{"kind":…}`。**这是最小化，不是授权**：代码注释、设计文档与本报告一致认定最终 messages/tools/reasoning/摘要/历史/错误的逐字节授权归 I06，且 I06 未实现、未批准。工具结果不自动获权（PRD FR-803 边界在分层上成立）。**静态通过；最终授权未验**。

### 5.5 AgentSidebar（SSR 层）
- 真实 TSX 内存编译 + `renderToStaticMarkup`（非挂载）：所有业务/模型字符串走 React 文本节点，`<script>`/`onerror`/`<img>` 实证被转义或不存在；CSS 无 `url()`/外部资源。**真实通过（仅 SSR 范围）**。
- 发送禁用：busy/旧上下文/`privacy==='local'`/`modelReady=false`/缺 `onSubmit`/空文本任一成立即禁用；重试额外要求 `modelAvailable`（本地模式宿主给了 handler 也禁用，t08-sidebar:176–182 实证）；缺 handler 动作禁用且文案区分"本地服务尚未接线"；每页动作 ≤4；旧上下文持续提示"不能当作当前结果"并禁用预览；Diff 入口仅预览、`canPreviewDraft` 校验 project/base/snapshot/盖章，无确认/提交/撤销控件。异步 `inFlight` ref 防重入；回调异常只显固定文案；输入不清空。**SSR 层真实通过**。
- **SSR ≠ 挂载事件、持久数据、真实 Diff 确认**：组件未挂载 App，无真实交互/可访问性/视觉验收。**该边界如实保留，不折算为产品通过**。

### 5.6 评估与 fixture 忠实性
- v1 十三案：输入/adapterOutcome/answer/expected 完整闭合，oracle 未预填进被测路径（每案 fresh session + 注入适配器）；哈希钉死（manifest.v1.sha256 与文件实测一致，run-001 内含）。
- v2 固定输入：probe 先验 manifest+三文件哈希再建**新**内存图，仅从 facts 加载；有限 case 白名单（5 个），非任意查询端点；Q-02 显式改 A01 状态、semantic-wrong 显式改查询文本，`inputSha256` 区分阶段、`querySha256` 区分查询；本方 run-002 直连复现全部五例。**SPARQL 原字节**：`query_execute` schema 只验非空/长度不 trim（t08-codec:193–201 保留尾换行），首失败（instruction.trim 裁掉尾换行）有原件与修复记录。001/002 身份、名称、行号与 equipment.csv 实测一致。**真实通过（固定输入范围）**。
- 手工 provider 消息与有限 probe **不得**计为真实 NL 生成、正式查询/推理/行为/沙盘产品能力——本报告严格按此口径（见 8.2）。

### 5.7 从完整原验收反查的遗漏/假设
- 未发现被隐藏的已实现但未审产品面：grep 证实 agent 模块零接线；44 差异外无其他产品变更；828 树与 source-git-bytes 一致。
- 发现的**架构层未闭合点**（非 T08 代码缺陷，属缺前置）：`query_execute` 的只读/禁外联（FR-402 SERVICE/远程 FROM）依赖真实 T04/I05 执行器，当前产品任何路径都未强制；真实 Diff/原子/撤销全部在 T01；最终外发授权全部在 I06。均列入第 8 节未验清单。

## 6. 历史内审 1–8 逐项关闭核对（在固定 product 代码中）

| 内审 | 原结论 | 问题 | 固定代码中的状态（本方证据） |
| --- | --- | --- | --- |
| 1 | 不通过 | P1 自由建议文本可称成功/隐藏失败 | **已关闭**：`resolveAnswer` schema 仅 evidence(callIds)/suggestion(guidance 枚举)/uncertain；有收据即返回全部收据（agent-service.ts:277–312；t08-agent:300–344） |
| 1 | 不通过 | P2 答案引用 ID 正则与协议 ID 不一致 | **已关闭**：callIds 复用 `toolCallSchema.shape.id`（agent-service.ts:283；t08-agent:300–318 标点 ID、t08-codec:176–191 空/超长 ID） |
| 2 | 通过（9bfd3105 修复复核） | — | 历史结论，不改写；其范围被后续批次继承，最终以 93516fa 全量复审为准（本报告） |
| 3 | 不通过 | 跨用户轮次复用旧收据 | **已关闭**：`beginUserTurn()` 清收据不清 usedCalls/预算（agent-service.ts:127–131；t08-agent:347–361、t08-conversation:250–285） |
| 4 | 暂不通过 | answer=null 隐藏已完成草稿/收据；批中取消丢前项 | **已关闭**：`state()` 提供 `localReceipts`+`inputContext` 只读克隆，fail/cancel 不擦除（conversation.ts:93–103,86–91；t08-conversation:287–394） |
| 5 | 通过（af9e59f） | — | 历史结论保留 |
| 6 | 不通过 | P2 本地模式可触发模型重试；P2 侧栏上下文比较不完整 | **已关闭**：重试 `disabled={…||!modelAvailable}`（AgentSidebar.tsx:196；t08-sidebar:176–182）；`sidebarIsCurrent` 全字段+有序选中对象比较（sidebar-presentation.ts:42–56；t08-sidebar:183–196） |
| 7 | 通过（3a4c2ea） | — | 历史结论保留 |
| 8 | 通过（93516fa） | — | 本方独立复核：87 项定向全过（run-003）、探针五例复现（run-002）、25 文件哈希全对 |

全部历史不通过问题在固定 product 中均已关闭；原失败原件与 gzip 元数据逐份在包内保全，未发现改写痕迹（首失败 SHA 与 backlog/verification 声明交叉一致）。

## 7. 新发现问题（本方独立发现）

**无 P0 / P1 / P2。** 以下为 P3 观察项（不阻断，不构成整体结论变化；修改属产品文件，留原 owner 按唯一写面处置）：

1. **[P3] `agent-service.ts:145`** — `executeCalls` 在 `this.running` 时抛 `BUDGET_EXCEEDED`。触发：会话执行工具期间并发第二次 `executeCalls`。影响：错误码语义混淆（"已达请求上限"文案会显示给实际的并发冲突），排障误导；测试已固化该行为（t08-agent:256–258），属既定但欠精确的协议选择。建议：后续候选引入独立 busy/`INVALID_PROTOCOL` 语义并同步测试。
2. **[P3] `agent-service.ts:160–162`** — 批内重复 ID 检查发生在逐项 `prepare()` 全部完成之后。触发：同批两个相同 ID 且第二个参数非法时，先报 `INVALID_TOOL_ARGUMENTS` 而非重复 ID。影响：仅错误归因顺序，无执行面影响（任何路径均零执行）。无需立即修。
3. **[P3] `capabilities.ts:5–16`（signatureSchema）** — `returnedModel` 为自由文本 1..256 且参与漂移判定；真实 provider 返回串中的版本号自然漂移会触发 `drift-requires-evaluation`。影响：按设计这是保守正确行为（宁可重评估），但正式接入后可能产生高频重评估告警，届时需在 I06/评估侧给出版本可比规则。当前无产品影响。

## 8. 完整原验收逐项状态

### 8.1 FR 覆盖（T08 相关条款，产品级口径）

| 条款 | 固定代码静态 | 受控运行 | 产品级完整验收 |
| --- | --- | --- | --- |
| FR-800 上下文感知 | 通过（TrustedContext/三重复验/克隆） | 通过（单测） | **未通过**：真实项目/选中对象/导入数据路径未接线（T00/T01 缺） |
| FR-801 页面动作/离线降级 | 通过（≤4 动作、离线路由、禁用态） | SSR 通过 | **未通过**：未挂载 App、T09 真实离线 handler 未接 |
| FR-802 导师/项目模式 | 通过（mode 约束/提示/草稿边界） | 单测通过 | **未通过**：真实模型两模式质量未评估 |
| FR-803 工具白名单 | 通过（私有词汇/整批预验/默认无端口/分级） | 单测通过 | **未通过**：唯一公共注册映射与 T02–T07 真实端口未接 |
| FR-804 Diff/原子/撤销 | 部分（版本化草稿盖章+预览门） | 单测通过 | **未通过**：T01 真实 Diff/真人确认/事务/撤销/恢复全部缺失 |
| FR-805 可信回答边界 | 通过（宿主收据/固定模板/状态保真） | 单测+固定输入通过 | **未通过**：真实查询/推理/质量/沙盘轨迹表达未接线 |
| FR-806 模型失败降级 | 通过（失败/取消/超时保留输入与已完成记录） | 单测+SSR 通过 | **未通过**：真实页面恢复/重试事件、真实网关失败、离线连续性未验 |
| FR-900 配置与能力验证 | 通过（codec/能力判定分层，连接≠JSON≠工具≠质量） | 单测通过 | **未通过**：I06 配置 CRUD/启停/删除、真实连接/JSON/工具往返未验 |
| FR-901 密钥保护 | 通过（T08 零密钥面；分层归 I06） | n/a | **未通过**：安全存储未实现/未验 |
| FR-902 最终外发检查 | 部分（投影最小化+UI 禁发） | 单测通过 | **未通过**：I06 逐字节授权/端点-主体失效/完全本地切换在途语义未实现 |
| FR-903 用量 | 保持 P1，未新增承诺 | — | 按原延期 |
| FR-904 最小外发记录 | 通过（不另建日志权威，提案在案） | n/a | **未通过**：真实最小记录未实现/未验 |
| FR-204/302/400 协作面 | 通过（草稿/建议/查询草稿数据层） | 部分（固定输入） | **未通过**：对应 T02/T03/T04 产品能力未接线 |

### 8.2 11.3 九类逐项

| # | 类别 | 现状 |
| --- | --- | --- |
| 1 | 本体修改正确性/基准过期/可撤销 | 合成层验证盖章与过期拒绝；真实正确性与撤销 **无法验证**（T01 缺） |
| 2 | NL→SPARQL 语法/完整预期/语义错反例 | 库侧**真实通过**（run-002：Q-01/Q-02/同数量 A02/语法错）；真实模型生成侧 **未验**（无 API 主体） |
| 3 | 映射建议与样本一致性 | 库侧真实（CSV 字符串身份/名称/行号）；模型建议侧 **未验** |
| 4 | 推理解释忠实/开放世界/定义域值域 | 仅合成字段；**未验**（无真实推理） |
| 5 | 沙盘解释忠实 | 仅合成字段；**未验** |
| 6 | 失败称成功/过期当当前 | 合成层通过（状态保真+收据不可隐藏）；真实路径 **未验** |
| 7 | 无依据拒答/不确定 | 合成层通过（宿主强制）；真实模型行为 **未验** |
| 8 | 工具结果/摘要/历史/错误越权外发 | **未验**（I06 最终检查不存在） |
| 9 | 导入/工具输出提权 | 合成层通过（注入不改权限、系统消息注入拒绝、confirm_changeset 拒绝）；真实导入路径 **未验** |

### 8.3 12.2 七项、G.5 A-01..A-10、其余基线

- 12.2 第 1–3 项（Diff 接受/旧 Diff 冲突/整批中途失败原子性）：**无法验证**——T01 ChangeSet/确认/事务/撤销不存在。
- 12.2 第 4 项（查询草稿实际 SPARQL/范围/完整结果）：固定输入+手工协议层通过；真实模型与真实范围 UI **未验**。
- 12.2 第 5 项（仅依真实轨迹解释/失败不称成功）：数据层约束就位；真实轨迹与真实模型 **未验**。
- 12.2 第 6 项（越权内容不进入请求）：**未验**（I06 缺）。
- 12.2 第 7 项（模型不可用时离线可用）：策略函数+SSR 就位；App 未挂载、T09 离线课程 **未验**。
- A-01/A-02（T01）；A-03/A-05（I06）；A-06/A-07/A-08（T10）；A-04/A-09（合成层通过、真实路径未验）；A-10（指定评估集零伪造：**未验**，无真实 provider）。
- requirements.csv/acceptance-baselines.csv 全部条目维持"未核验完整产品通过"，与实际一致，无被篡改为通过的痕迹。
- e2e/package/native/两 OS/真人/CI/远端/57 P0 发布门：本线无任何证据，全部保留。

## 9. 缺前置与可修代码问题区分

- **缺前置（阻断整体，非本候选代码缺陷，不能靠改 T08 代码解决）**：① I06 获批网关+安全存储+最终字节授权+最小调用记录+真实主体/消费上限；② T01 真实项目/ChangeSet/Diff/确认/撤销；③ T02–T07 真实领域端口与 T00 公共命名接线、T09 离线 handler 与 App 挂载；④ 隔离 e2e/native 与两 OS 验收；⑤ 同候选双方外审+CI+合并门。以上顺序与 design-and-integration.md 接线顺序一致，本方认可该顺序为最小恢复路径。
- **可修代码问题（本候选范围内）**：仅第 7 节三条 P3；均可在未来候选中随手处理，不构成重审理由本身。

## 10. 证据分类声明

- **静态**：第 2/3/5/6 节中标注"静态/通过"的结论来自固定 Git 对象与工作区字节级核对的全文阅读。
- **历史运行（读档，不称重跑）**：归档 check-93516fa 原件、三份首失败 gzip 元数据、verification*.json、内审 1–8 的历史结论。
- **自行运行**：run-001/002/003 及全部完整性脚本（第 4 节），原始 stdout/stderr 均在本方 raw/ 下落盘。
- **未验**：第 8 节全部"未验/无法验证"项；未宣称重跑任何历史命令之外的产品验证；未启动 Electron/e2e/打包；未调用任何付费 API；未读取 .env/密钥/钥匙串；未读取 peer 任何材料。

## 11. 最终结论

**不通过（NotPass）。**

理由：固定候选 `93516fa` 的已实现纯模块范围（严格 codec、会话编排、工具白名单与证据保真、私有侧栏 SSR、版本化合成评估与真实固定输入观测）经本方独立全文审查与三类受控运行**未发现新的阻断缺陷**，历史内审 1–8 问题在该固定代码中全部核实关闭；但完整原验收所要求的真实 I06 授权与传输、T01 Diff/事务/撤销、真实领域工具与页面接线、真实模型主体与消费上限、11.3 真实评估、12.2 端到端闭环、A-01..A-10 真实路径、e2e/native/两 OS/真人验收及 CI/合并发布门**全部缺失**。按"关键验收缺失不得 Pass、局部静态无问题不得拼为整体通过"的门禁，整体结论必须为不通过；局部通过清单仅限第 5/8 节所列边界内。

阻断项（恢复所需最小外部变化，同第 9 节）：I06 网关/授权/记录 → T01 及各真实领域服务 → T00/T09 接线与挂载 → 真实 API 主体/预算 → 11.3/12.2/A 系列真实路径评估 → 隔离 e2e/native/两 OS → 同候选双方外审与发布门。届时须刷新批准 base、生成新候选并按门禁重新完整审查，不继承本报告任何局部结论为整体通过。

（完）
