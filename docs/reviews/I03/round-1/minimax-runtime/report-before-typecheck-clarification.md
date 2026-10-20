# I03 候选4 独立外审报告 — M3.1-Flash / xhigh

> 本报告为指定双模型外审之一，独立作出。未读取另一模型本轮报告或输出；未修改实现代码、未提交、未推送、未切换分支。仅写入本文件与 `/tmp/i03-r1-minimax/` 独立日志。

## 0. 结论

**通过。** 未发现阻断问题；3 项中等级（P2）问题与 4 项轻等级（P3）建议全部允许延期，其中 1 项 P2 属门禁缺口、建议在 I03 合并前或最迟 I04 接线前单独处理。I03 本轮可验收范围（契约设计与公共校验器 + 最小 S1 边界守卫）经独立核验成立；I04/I05 的运行验收按设计归属不在本线，未被本报告代为宣称。

- 结构一致性：请求/响应 14 个方法 ↔ registry ↔ `schema.json` 的方法—schema 映射 **零错配**；`errors.json` ↔ `schema.json.error` 26/26 逐字段相同；`staleReason` 8 码与 S1 `invalidation-v2.json` 8 个非空码**逐项一致且码↔族配对完全吻合**。
- 候选4 焦点区（I05 v3）：v3 **25 项细码**与 I05 源快照**集合与顺序完全相同（25/25）**；五个退休合码**未出现在 v3 表或 v3 来源分支**；`SHAPE_PATH_UNCLASSIFIED` **仅**指向 `INTERNAL_ERROR/{}`；公共目录**不含任何 I05 内部码**。
- 双端一致性：自建 TS/Python 差分探针 **830 例**（705 + 111 + 14），**0 处语义分歧**（唯一差异为异常类型书写形式，两端同为 `INVALID_REQUEST`）。
- 独立验证：`npm run check` **exit 0**（lint / format / desktop 类型 / vitest 420 / **build** / ruff / pytest 622）、`npm run typecheck --workspace @ontolearn/contracts` **exit 0**、`npm run verify:sources` **exit 0**（12 项）、`git diff --check` **exit 0**。

---

## 1. 评审任务、模型与思考设置的来源记录

| 项 | 值 | 来源 |
| --- | --- | --- |
| 任务标识 | `I03-R1-MiniMax-M31Flash-C4-f574a72` | 派发提示词首段；并与 `docs/reviews/I03/round-1/tasks.json` 的 `tasks.minimax.taskId` 一致 |
| 模型 | M3.1-Flash | 派发提示词首段；`tasks.json` `tasks.minimax.model` = `M3.1-Flash`；`source.modelObserved` = `M3.1-Flash`（真实 UI 读回） |
| 思考设置 | xhigh | 派发提示词首段；`tasks.json` `tasks.minimax.thinking` = `xhigh`；`source.thinkingObserved` = `xhigh`（真实 UI 读回） |
| 任务创建方式 | 应用 `com.minimax.agent.cn`，`cua_repl` 原生应用控制 | `tasks.json` `tasks.minimax.source` |
| 创建时间 | 2026-10-20T11:45:17.780141+08:00 | `tasks.json` `tasks.minimax.createdAt` |
| 原生 task UUID | **不存在/未提供** | `tasks.json` `nativeTaskId: null`，`idKind: "dispatcher correlation ID present in actually sent prompt; native UUID unavailable in UI"`。**本报告不臆造原生 UUID**；上述标识为派发方关联 ID。 |
| 报告路径 | `docs/reviews/I03/round-1/minimax-m31flash.md` | `tasks.json` `tasks.minimax.report`（与本文件一致） |

**本轮独立性声明**：候选 1–3 从未产生过外审报告（`docs/reviews/I03/candidates/candidate-1..3/` 内只有 `prepared-prompts/`、`tasks-not-created.json`、`blocked-audit.json` 等流程件，无任何 `*-glm53.md` / `*-m31flash.md`）。因此本次不存在"沿用旧轮结论"的可能，本报告为 I03 的**首次**外审意见。另一模型本轮报告我未读取、未推测其结论。

---

## 2. 项目、分支与基线

| 项 | 值 |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I03-protocol-contracts` |
| 分支 | `feature/I03-protocol-contracts`（`git rev-parse --abbrev-ref HEAD` 实测） |
| base SHA | `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3` |
| head SHA | `f574a7234923f28e9356a45a17253803e7602e06`（= 实测 `git rev-parse HEAD`） |
| 合并方式 | `0ec24b7e12c9ffaee5895e461800649a04bfff2f`（可追踪 merge `origin/develop`，无冲突） |
| 变更规模 | 37 个文件（`git diff --name-only base head`），新增 21 704 行 / 删除 9 行 |
| 受保护规则 | `AGENTS.md` SHA-256 = `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与 `candidate.json.protectedGuidance.sha256` **实测一致**；`featureCommitIncludesFile: false`（未混入候选） |
| push / PR / CI / merge | 均未发生（`candidate.json`: `pushed:false`、`pullRequest:null`、`ci:null`、`merge:null`） |

### 2.1 候选完整性独立核验

对 `docs/reviews/I03/candidate.json` 冻结的 37 份文件逐份重算 SHA-256：

- **36/37 与冻结值一致**，包括全部受审实现（`packages/contracts/**`、`packages/engine/**`、`tests/unit/contract-v2.test.ts`）。
- **1 处不一致**：`docs/reviews/I03/status.md`（工作区 `925d0d4e3849…` ≠ 冻结 `2cda53c21320…`）。实测 `git diff` 显示该差异**仅为流程追加**：新增"候选4外审实际创建与控制中断（仅流程追加）"一节，外加"I05 修订验证收口"一节把"两指定外审仍未创建"改为"**当时**两指定外审仍未创建"。**未触及任何契约、schema、测试、依赖、CI、验收或受审实现**。`status.md` 自身亦声明"此节只更新过程状态，不改变契约、测试、依赖、验收或受审实现"。→ **不构成受审内容变化，不触发重新审查**（与 `scope.md` 第 5 条"单纯证据追加需核对不夹带实现改变"一致）。
- `git status --porcelain` 在我全部验证前后一致（仅 `AGENTS.md`、`docs/reviews/I03/status.md` 两处已披露修改 + 未跟踪的 `docs/reviews/I03/` 流程件）；我未新增、修改或删除任何仓库文件。

### 2.2 冻结输入（`inputs/sources.json`）核验

6 份冻结副本 SHA-256 **全部与 `sources.json` 记录一致**（`test_frozen_input_hashes_are_self_contained` 亦覆盖，我另行独立复算）。与实时原件比对：

- `goal-objective.md` / `scope.md` / `policy.md` / `m0-review-and-update-plan-2026-10-19.md`：**逐字一致**。
- `parallel-coordination.md`：**实时原件已前进**（新增 I06 独立开发线调度一段），冻结副本保持原样未覆盖。`status.md` 已披露"协调文件在初次归档后新增I06调度，另保留第二版，不覆盖原快照；不改变本功能受审产品/验收"。→ 属**协调/流程文件**变更，非产品需求变更，**不要求重新审查**。

---

## 3. 已检查范围

### 3.1 需求与验收依据（全部实读）

`docs/reviews/I03/inputs/scope.md`（I03 全范围与八项统一门禁）、`inputs/m0-review-and-update-plan-2026-10-19.md`（S1 退出门槛 1–6、S2 v2 契约草案/ExecutionJob 草案/退出门槛 1–5、U1 全节、C1/B1/S3 边界）、`docs/prd/PRD-…工作台.md`（附录 C/D/E 实读，8.6/8.7 实读）、`docs/iterations/I03/acceptance.md`（I03 必须通过 10 行 + I04 必须承接 6 行 + I05 补充验收 4 行）、`docs/iterations/I03/ADR-0003-design.md`、`protocol.md`、`jobs-and-storage.md`、`shared-state.md`、`I05-semantic-boundaries.md`（全文）、`docs/iterations/I01/ADR-0002-storage.md` 相关条款、`docs/reviews/I01/round-3/processing.md` 及 round-1/round-2 的历史意见编号与处置、`docs/reviews/I03/handoffs/*`（I05 两份源快照 + I06 11 类处置）、`docs/reviews/I03/internal-review.md`、`docs/reviews/I03/status.md`、`docs/reviews/I03/candidate.json`、`docs/iterations/I03/evidence/*.json`。

### 3.2 实现（全部实读 + 程序化核对）

- `packages/contracts/v2/`：`schema.json`（66 个 `$defs`）、`errors.json`（26 码 + `parameterMeanings`）、`registry.json`（24 能力）、`states.json`、`dependencies.json`、`fixtures.json`（397 例）。
- `packages/contracts/src/v2.ts`（556 行）、`dependencies-v2.ts`（50）、`states-v2.ts`（18）、`design-v2.ts`（4）、`packages/contracts/package.json`、`packages/contracts/tsconfig.json`。
- `packages/contracts/python/contract_v2.py`（473 行）。
- `packages/engine/src/ontolearn_engine/storage.py`（本候选改动 33 行：`publish`/`current` 共用 kind+provenance 守卫、开库 legacy kind 拒绝、`commit_round` legacy config 守卫）。
- `packages/engine/tests/test_contract_v2.py`（268 行）、`tests/unit/contract-v2.test.ts`（188 行）。
- `packages/engine/src/ontolearn_engine/invalidation-v2.json`（S1 失效码表）。

### 3.3 程序化一致性核对（我自建脚本，独立于仓内测试）

1. `request`/`response` 14 方法 ↔ `registry.capabilities` ↔ `params_*`/`result_*` `$defs` 映射：**0 错配**；`params_job.create.capability` 枚举 == registry 减去 14 个服务方法（恰为 10 个能力）。
2. `schema.error` 的 26 个 `oneOf` 分支 ↔ `errors.json.codes`：**逐码 code/messageKey/retryable/paramsSchema 全等**。
3. `schema.staleReason` 8 码 ↔ S1 `invalidation-v2.json` 8 个非空 `staleReason`：**顺序与集合完全一致**；`code`↔`family` 配对（ONTOLOGY_CHANGED↔ontology、FACTS_CHANGED↔facts…）**完全吻合**；`model` 族 `staleReason:null` 且 `staleReason.dependency` 模式**不含 model**；`dependencyKey`/`vector` **允许** `model:`（可作依赖但不可作过期原因），`definitionSetDigests.propertyNames` **排除** model 且 `maxProperties:7` == 七个集合族。
4. I05 v3：**源快照 25 码 vs I03 v3 表 25 码，集合与顺序完全相同**；I03 历史表 30 码 == 原 30 码交接表集合（无增删）；五个退休合码（`INPUT_LIMIT`/`RESULT_LIMIT`/`UNSUPPORTED_LITERAL`/`UNSUPPORTED_RDF`/`ASSERTED_SCOPE_REQUIRED`）**仅存在于历史表**，v3 表与 v3 来源分支均为 0 命中；v3 表每行的公共目的地（含 `field`/`construct`/`resource` 取值）**全部可在公共目录表达**；v3 表 25 行**无一行缺公共目的地**；公共目录**零个 I05 内部码**。
5. `runConfig` 常量 vs PRD 附录 E.2：`roundOrder = events>pre-inference>freeze-conflicts>behavior>resources>post-inference-metrics-commit` 精确对应 E.2 六阶段；`triggerOrder = priority:desc,behaviorId:asc,eventInputOrdinal:asc,eventId:asc,actionOrdinal:asc` 精确对应 E.1「行为排序」；`maxRounds 1..1000` ↔ E.2「1～1000 轮」；`maxActionsPerRound = 1000` ↔ E.2「每轮最多 1000 次行为动作」；`semantics = E.1-E.2-one-stage-v1` 与「reason 只做 RDFS 后一阶段受控规则」一致。
6. `registry.v2Runtime == []`、`productRuntime == ['health']` → 未实现能力无法被声明（`matchesResponse` hello 分支强制 `capabilities ⊆ v2Runtime`）。
7. 附录 D.2 九行 ↔ `invalidation-v2.json` 的 `appendixRow 1..9`：第 9 行 model 无 staleReason。**一致**。

### 3.4 双端差分探针（自建，隔离于 `/tmp/i03-r1-minimax/probe`）

- 工具链：TS 侧用仓库锁定的 `vite 8.3.4`（rolldown/oxc）把 `packages/contracts/src/design-v2.ts` 打包到 `/tmp`；Python 侧直接加载 `packages/contracts/python/contract_v2.py`。两侧喂入**同一份** JSON 用例集，输出逐条比对。**未在仓库内新增任何文件。**
- 用例集 A（705 例）：仓内全部 397 条 fixture（cases/routing/cursors/responses/jobListCursors/transitions/validationBindings/unicodeMutations/dependencyChains）逐条重放 + 26 码各 7 类错误变体（合法/错 messageKey/错 retryable/多余参数/缺必需参数/free-text message/堆栈参数/超长）+ 全部 `parameterMeanings` 枚举值 + 跨类误用（如 `semanticInput` 塞进 `INVALID_REQUEST.field`、`semanticResult` 塞进 `INTERNAL_ERROR.params`）+ 16 个数值边界 + 依赖推导 13 组（族前缀碰撞、悬空引用、重复身份、显式 `facts:asserted` 引用、scope 越权、未知能力、4096/4097 上界、跨族引用、环、model 族不入选集）+ 游标绑定子集/过期边界 + 验证投影绑定变体。
- 用例集 B（111 例）：逐条复验历史问题 A1–A6 / B2–B5 / C1 的反例，含**我重新构造**的合法/非法对照（修正了首轮自造用例中"running→cancelled"属非法转移的构造缺陷）。
- 用例集 C（14 例，针对"多成员稳定顺序"）：我自查发现用例集 B 中的 `A4:joblist-order-violation` 作用在**只有 1 个成员**的 `job.list` 夹具上（反转后无变化），**并未真正检验多成员稳定顺序**；`tests/unit/contract-v2.test.ts` 的 `duplicate list members` 用例也只覆盖重复成员、未覆盖顺序。据此重新构造双成员用例（保持 `updatedAtMs==finishedAtMs` 以免触发无关的时间戳规则）并实测：
  - `job.list`：`asc-ok`=true、`desc`=false、`same-ts-asc`=true、`same-ts-desc`=false、`dup-jobid`=false、`other-project`=false、`filter=active` 含终态成员=false、`filter=terminal` 含终态成员=true（正确）。
  - `page.rows`：`rows-asc-ok`=true、`rows-desc`=false、`same-ordinal-asc`=true、`same-ordinal-desc`=false、`dup-rowid`=false。
  - **结论：`(createdAtMs,jobId)` 与 `(ordinal,rowId)` 双键升序、同值按次键升序、成员唯一、跨项目与过滤绑定，在两端均被正确强制。** 上一轮（A4）中"多成员顺序"一条**此前未被独立证实**，现已补齐并通过。
- **结果：830 例全部比对，0 处语义分歧。** 唯一形式差异为 `deriveDependencies` 越界时 Python 抛 `ValueError('INVALID_REQUEST')`、TS 抛 `Error('INVALID_REQUEST')` —— 语义等价。

---

## 4. 验证命令与实际结果（原始完整日志见 `/tmp/i03-r1-minimax/logs/`）

全部命令直接重定向保存完整 stdout/stderr，并**立即保存真实退出码**（`/tmp/i03-r1-minimax/logs/exitcodes.txt`），未以 `tail`/管道成功冒充通过。

| 命令 | 真实退出码 | 实际结果 | 日志 |
| --- | --- | --- | --- |
| `npm run check` | **0** | lint（`eslint . --max-warnings 0`）→ format:check → desktop typecheck（`tsc --noEmit`）→ **vitest 5 files / 420 tests passed** → **build（`electron-vite build` 成功，main/preload/renderer 产物生成）** → engine:check（ruff check + ruff format 105 files + **pytest 622 passed in 5.92s**） | `npm-run-check.log`（93 行，SHA-256 `7b2e19f3003b6a13b47058ed0e3f2ac409230b4dc82f775e64b4dd97acb30e43`） |
| `npm run typecheck --workspace @ontolearn/contracts` | **0** | `tsc --noEmit -p packages/contracts/tsconfig.json` 通过（strict） | `typecheck-contracts.log` |
| `npm run verify:sources` | **0** | 12 项归档源一致 | `verify-sources.log` |
| `npm run lint` | 0 | 无告警 | `lint.log` |
| `npm run format:check` | 0 | 通过 | `format-check.log` |
| `npm test` | 0 | 420/420 | `vitest.log` |
| `npm run engine:check` | 0 | ruff + 622 pytest | `engine-check.log` |
| `git diff --check` | 0 | 无空白错误 | — |
| 自建差分探针（TS 打包 + 双端 830 例比对） | 0 | 0 处语义分歧 | `probe-build*.log`、`probe-run*.log`、探针目录 JSON |

**说明**：我在续接前曾因"共享 build/out 由 ZCode 优先持有"而只跑 `npm run check` 的其余 6 个分项并如实记录 build 未执行；本次续接后资源已释放，我**实际完整执行了 `npm run check`（含 build）**，退出码 0，原始完整日志已保存并核对。

### 4.1 未验证 / 不在本次范围的事项（如实列出）

| 事项 | 状态 | 理由 |
| --- | --- | --- |
| Electron e2e / Playwright / 原生窗口 / HMR / 打包产物启动 | **未执行（按禁止项）** | 本机不得启动任何测试窗口；AGENTS 第 4 节"本地验证默认不打扰用户"与本次派发明确禁止。本候选不涉及 main/preload/renderer/CSP 改动 |
| 真实常驻 JSONL reader、worker/队列、任务持久化与取消接线 | **未执行** | 属 I04；`registry.v2Runtime == []`，无运行实现可测 |
| 真实 RDFS / pySHACL / 分层图投影 / 派生 rdf:type 保留 | **未执行** | 属 I05；本迭代仅做描述符与元数据校验，`I05-semantic-boundaries.md` 已如实声明"本迭代没有执行 RDFS、pySHACL 或实际图投影" |
| I05 v3 交接来源的真实性（I05 源码未冻结、仅交接声明 123 项定向回归） | **未验证，且本报告不代为宣称** | I05 未冻结；`I05-contract-source.json` 自身标注 `status: "Unfrozen I05 handoff table; implementation checkpoint and full/package validation pending; not adopted as public API"`。我只核对了**交接文本与 I03 契约的对应关系** |
| Q2/Q3/Q5/Q6/Q7/Q8/Q9 产品决定 | **未决，未被本线预设** | 契约中所有上限均标注为"本版契约安全上界，不是容量或性能承诺" |
| 另一模型本轮报告 | **未读取** | 互不披露本轮意见的门禁要求 |

---

## 5. 问题清单

严重度口径：**P0 阻断 / P1 严重 / P2 中 / P3 轻**（与仓内 `internal-review.md` 的 P2/P3 口径一致）。本次 **0 个 P0、0 个 P1**。

### F1（P2 中 · 非阻断）`parameterMeanings` 只覆盖 7 个含枚举参数错误码中的 2 个

- **位置**：`packages/contracts/v2/errors.json`（顶层 `parameterMeanings`，仅 `UNSUPPORTED_CONSTRUCT`、`RESOURCE_LIMIT` 两键）；`packages/contracts/src/v2.ts`、`packages/contracts/python/contract_v2.py`（两端**均不消费** `parameterMeanings`）；`tests/unit/contract-v2.test.ts:181-188`；`packages/engine/tests/test_contract_v2.py:251-258`；`docs/iterations/I03/I05-semantic-boundaries.md:7`。
- **事实**：含枚举参数的错误码共 7 个 —— `INVALID_REQUEST.field`(7 值)、`MAPPING_VALUE_INVALID.field`(4 值)、`NOT_FOUND.resource`(7 值)、`RESOURCE_LIMIT.resource`(8 值)、`SEMANTIC_INPUT_INVALID.field`(4 值)、`TIMEOUT.phase`(6 值)、`UNSUPPORTED_CONSTRUCT.construct`(17 值)。其中**仅 2 个**有 `parameterMeanings` 条目；`SEMANTIC_INPUT_INVALID`（I05 v3 的 25 细码中 9 项的主要公共去向之一）**没有**任何语义说明来源。`I05-semantic-boundaries.md:7` 自述"**`errors.json` 的 parameterMeanings 是有限类别的语义目录；键与 paramsSchema 枚举必须完全一致**"，但仓内两处测试都只断言了 `UNSUPPORTED_CONSTRUCT` 与 `RESOURCE_LIMIT` 两个码。
- **触发条件**：UI/Agent 需要为 `SEMANTIC_INPUT_INVALID` 的 `syntax`/`query`/`rule`/`constraint` 四种真实入口，或 `INVALID_REQUEST.field` 的七种类别，生成 PRD 8.6 的"发生了什么/为什么/如何修复/相关知识"四段式说明时，公共错误目录内没有任何可引用的语义来源；说明只能回到 `I05-semantic-boundaries.md` 的内部码表格中人工查表。
- **影响**：**不破坏契约封闭性**——枚举在 `schema.json` 与 `errors.json` 中逐码锁定，越界取值一律被拒（我实测：`cat:cross:semanticInput-via-INVALID_REQUEST` → 拒绝；`cat:cross:resource-via-INTERNAL_ERROR` → 拒绝；`err:extraparams:*` 26/26 拒绝）。**不泄漏数据**。实际影响是：(a) 公共错误目录**不自足**，语义说明散落在 I05 交接文档；(b) 目录自述的"键与枚举必须完全一致"这一不变式**仅被部分锁定**，后续若给 `NOT_FOUND`/`TIMEOUT`/`MAPPING_VALUE_INVALID` 增删枚举值，不会有任何测试失败；(c) 与候选4 焦点区（v3 目的地目录）直接相关。
- **建议**：为全部 7 个含枚举参数的码补齐 `parameterMeanings` 条目；把两处测试改为"**遍历所有含 enum 参数的码**，断言 `parameterMeanings[code]` 的键序与 `paramsSchema.properties[param].enum` **完全相等**，缺条目即失败"。
- **处理结论**：**允许延期**。不影响本候选可验收范围；但建议在 I03 内解决（改动仅限 `errors.json` + 两处测试，不触碰契约语义），否则将随 I04 接线一起带出。

### F2（P2 中 · 非阻断）两个 messageKey 的命名空间与实际条件域错位

- **位置**：`packages/contracts/v2/errors.json`（`RESOURCE_LIMIT.messageKey = "job.resourceLimit"`；`INVALID_STATE.messageKey = "job.invalidState"`）；`docs/iterations/I03/protocol.md:7`（"hello 后再 hello 为 INVALID_STATE"）、`protocol.md:50`（"UI 依 messageKey 在本地组装 PRD8.6 的四段式"）；`docs/iterations/I03/I05-semantic-boundaries.md:9-11`；PRD 8.6。
- **事实**：
  1. `RESOURCE_LIMIT` 的 `resource` 枚举已含 `semanticInput`/`semanticResult`/`semanticWork` 三个**语义预算**类别（I05 v3 的 5 项细码导向此处），但其 messageKey 仍是 **`job.resourceLimit`**。同一码同时承载 `memory`/`actions`/`rounds`/`frame`/`page`（任务/传输域）与三个语义域类别。
  2. `INVALID_STATE` 的 messageKey 为 **`job.invalidState`**，而 `protocol.md:7` 把它指定为"**重复 hello**"这一**会话/握手级**条件的错误码。
- **触发条件**：UI 按 messageKey 解析说明文案时，`job.resourceLimit` 无法区分"语义输入超限"与"任务帧/页超限"；`job.invalidState` 会把一个握手状态错误指向"任务"。PRD 8.6 明确要求错误按"发生什么/为什么/如何修复/相关知识"四段式呈现，命名空间错位会直接落到用户可见文案上。
- **影响**：**功能与安全均无缺陷**——四个安全字段（code/messageKey/params/retryable）仍原样穿过 bridge，`params.resource` 足以让 UI 二次判别；未泄漏原值/路径/堆栈。**实际风险是命名固化**：I04 接线时 UI 会按当前 messageKey 建映射，届时再改属破坏性语义变更（`protocol.md:60` 规定已采用协议的破坏性变化必须提高协商版本）。
- **建议**（二选一）：(a) 拆码 —— 保留 `job.resourceLimit` 承载传输/任务预算，新增 `semantics.resourceLimit` 承载三个语义预算；把 `INVALID_STATE` 拆为 `protocol.sessionStateInvalid`（重复 hello）与 `job.invalidState`（任务状态非法）；或 (b) 若确定共用，则在 `I05-semantic-boundaries.md` 与 `protocol.md` 明确记录"UI 必须同时读取 `messageKey` 与 `params.resource`/`params.field` 才能定位条件"，并把该判据固化为测试。
- **处理结论**：**允许延期**。建议在 **I04 接线（bridge→UI 四段式）之前**定稿，否则 UI 会固化错误命名空间；届时属破坏性变更，需走新候选与双审。

### F3（P2 中 · 非阻断）contracts 包与新测试文件未纳入任何自动类型检查门禁

- **位置**：根 `package.json`（`"typecheck": "npm run typecheck --workspace @ontolearn/desktop"`、`"check": "… && npm run typecheck && npm test && …"`）；`apps/desktop/tsconfig.json`（`include: ["src","electron.vite.config.ts"]`）；`packages/contracts/tsconfig.json`（`include: ["src"]`）；`eslint.config.mjs`（`tseslint.configs.recommended`，**非**类型感知版）；`.github/workflows/ci.yml:30,68-70`。
- **事实（实测 `tsc --listFiles`）**：desktop 类型程序中 contracts 只有 `packages/contracts/src/index.ts`（v1 health 契约）。本候选新增的 `src/v2.ts`(556 行)、`src/dependencies-v2.ts`(50)、`src/states-v2.ts`(18)、`src/design-v2.ts`(4) **不在任何自动类型检查程序内**——`npm run check` 的 typecheck 只查 desktop；eslint 非类型感知；vitest 只转译不查类型；desktop 构建图不含 contracts；**CI 两个 job 都只跑 `npm run typecheck`（=desktop）**。此外 `tests/unit/contract-v2.test.ts`(188 行) **连手工的 contracts typecheck 都不覆盖**（两个 tsconfig 的 `include` 都不含 `tests/`）。
- **触发条件**：任何后续对 `packages/contracts/src/v2.ts` 等文件的改动引入类型错误（例如 `registry.capabilities[...]` 被写成可能为 `undefined` 却被直接取属性）时，`npm run check` 与 CI **全部保持绿灯**。
- **影响**：本次候选的**内容**类型正确（我已独立执行 `npm run typecheck --workspace @ontolearn/contracts`，exit 0；且 830 例差分全部一致，证明运行时行为正确）。**影响的是回归风险**：契约层是 I04 之后所有跨端行为的根基，却处在自动门禁之外；这与 AGENTS 第 7 节"边界数据一律经 zod `.strict()` 解析"、第 4 节"`npm run check`（lint/格式/类型/vitest/构建/ruff/pytest）"所设想的门禁覆盖面不一致。本候选的 `acceptance.md` 已把 contracts 独立 typecheck 列为**单独一行**要求，说明作者知情，但**该要求仍不在 CI 中**。
- **建议**：在根 `package.json` 增加 `typecheck:contracts` 脚本，并把 `check` 的 typecheck 步骤改为 `npm run typecheck && npm run typecheck --workspace @ontolearn/contracts`；`ci.yml` 的 check job 同步加入同一条命令；并把 `tests/unit/**` 纳入一个根级 `tsconfig`（或 contracts tsconfig 的 `include`）以覆盖新测试文件。
- **处理结论**：**允许延期，但须在 I03 合并前或最迟 I04 接线前处理**。**不建议在候选4 上直接追加**——该改动会修改 `package.json` 与 CI，按现行门禁属"实现/测试/配置/依赖/验收变更"，必须生成新候选并重新双审。请总控决定：作为 I03 合并前的一个独立小提交处理，或列为 I04 前置项。

### F4（P3 轻）`errors.json` 的 `maxEncodedBytes` / `schemaVersion` 无任何消费者

- **位置**：`packages/contracts/v2/errors.json`（顶层 `maxEncodedBytes: 2048`、`schemaVersion: 2`）；`packages/contracts/src/v2.ts:159`（`utf8(v) > 2048` 硬编码）；`packages/contracts/python/contract_v2.py:130`（`encoded_size(v) > 2048` 硬编码）。
- **事实**：`grep` 确认 `errors.json` **只被两处测试读取**（用于与 `schema.json` 对齐），运行期校验器一律走 `schema.json` 的 `error` 分支。2048 上界在两端各自硬编码，与目录声明值**无联动**。
- **触发条件**：目录作者把 `maxEncodedBytes` 调为 4096（或删掉），两端校验器**不会跟随**，且无任何测试失败。
- **影响**：当前目录值与执行值一致（我实测：超长 error 被拒，`err:oversized:*` 26/26），**无当前功能缺陷**；属漂移可能。
- **建议**：让两端适配器从 `errors.json` 读取该常量，或加一条测试锁定 `errors.maxEncodedBytes === 2048` 且两端一致；`schemaVersion` 同理加一条"与 `schema.json`/`registry.json` 同版本"的断言。
- **处理结论**：**允许延期**（建议随 F1 一并处理）。

### F5（P3 轻）I05 v3 的 25 码映射与"退休合码/仅 INTERNAL_ERROR"约束只有 Markdown 载体

- **位置**：`docs/iterations/I03/I05-semantic-boundaries.md`（v3 25 行表 + 历史 30 行表）、`docs/reviews/I03/handoffs/I05-typed-reasons-v3-source.md`；**无**对应的 `packages/contracts/v2/*.json` 机器可读映射。
- **事实（我已独立核验通过）**：v3 表 25 码与 I05 源快照 **25/25 集合与顺序完全相同**；五个退休合码在 v3 表与 v3 来源分支**均为 0 命中**；`SHAPE_PATH_UNCLASSIFIED` 在 I03 v3 表中**只**指向 `INTERNAL_ERROR/{}`（源表同样只允许 INTERNAL_ERROR 安全兜底）；公共目录**零个 I05 内部码**（实测 `X:error-retired-internal-code` → 拒绝；`X:error-unknown-code`（`SHAPE_PATH_UNCLASSIFIED` 作为公共码）→ 拒绝）。
- **影响**：**验收文本"逐项保留历史30码并优先覆盖v3的25项细码/来源分支；被替换的…合码不用于新分支；SHAPE_PATH_UNCLASSIFIED及来源未知只INTERNAL_ERROR安全兜底"在契约层已满足**，本项**不是缺陷**。风险在于：I05 后续冻结新检查点若新增或改名内部码，I03 侧无自动检测，只能靠再次人工文档复核。
- **建议**：把映射落成 `packages/contracts/v2/semantic-reasons.json`（`sourceCode → {publicCode, param}`），并加 TS/Python 共用反例：每个 v3 源码至少一个可接受公共码、五个退休码**不得**出现在新映射、五个退休码**不得**出现在公共目录、`SHAPE_PATH_UNCLASSIFIED` 只能映射 `INTERNAL_ERROR`。
- **处理结论**：**允许延期**（验收已满足，属增强）。

### F6（P3 轻 · 前向风险）附录 E.2"存在未处理事件"标记在 v2 契约中无明确承载路径

- **位置**：PRD 附录 E.2（"达到最大轮数但仍有未处理事件时，运行可结束，但必须标记'存在未处理事件'，不得显示为全部完成"）；`docs/iterations/I03/protocol.md` 方法表（14 方法，**无 `run.get`**）；`packages/contracts/v2/schema.json` 的 `job` / `committedProgress`（仅 `runId`/`lastCommittedRound`/`snapshotRef`）。
- **事实**：`grep` 确认 "未处理事件" 在 I03 全部文档与 schema 中**零命中**。逐轮任务的公开契约可读到"已提交到第几轮 + 快照引用"，但**没有方法也没有字段**承载 run 的终态证据与"仍有未处理事件"标记。
- **影响**：E.2 的该项是**强制显示标记**（不得显示为全部完成）。当前存在一条可行但**未被设计写明**的路径——随场景运行的 `result` 载荷（`kind=scenario`）承载该结论；但设计文档未声明这一点，I04/I05 实现者可能任选其一。若将来必须新增方法或字段，按 `protocol.md:60` 属破坏性变更，须提高协商版本。
- **建议**：在 `shared-state.md` 或 `jobs-and-storage.md` 明确写明"run 的终态证据与未处理事件标记由场景运行结果载荷承载"（或明确列为 I04 待定的协议扩展点并预留版本策略）。**不要求本候选新增方法**——那会扩大契约面并触发新一轮双审。
- **处理结论**：**允许延期**（前向风险，须在 I04/I05 联验前澄清）。

### F7（P3 轻 · 观察，非缺陷）S1 开库守卫为全库级；实测无性能问题

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:47-53`（开库时对 `results` 与 `current_results` 执行 `typeof(kind) != 'text' OR trim(kind) = ''` 检查，命中即拒绝开库）。
- **事实与实测**：我以同形表在 0 / 1 000 / 10 000 / 50 000 行下实测该查询为 **0.02 / 0.08 / 0.67 / 3.45 ms**（5 次平均）→ **不构成性能问题**，原计划中我曾拟列为性能风险，实测后**撤回该判断**。真实影响是"行为特征"而非性能：任一历史行非法即**整库不可打开**（任一项目都读不到），且错误只给固定 `ValueError("Invalid legacy result kind; explicit repair required")`，不含受限的项目/结果标识（符合"不回传路径"，但运维定位困难）。
- **对照要求**：I01 意见 N-R3-1/F3-01 明确要求"既存 NULL/空键须**显式拒绝**并保留数据修复证据，不能假报无结果"——**显式拒绝本身正是被要求的行为**，且我实测拒绝路径零副作用（DB dump 逐字未变，`test_existing_null_kind_is_rejected_without_silent_cleanup` 覆盖）。故**不作为缺陷**。
- **建议**：I04/运维侧需有明确的修复路径（如何在不改写正式事实/历史的前提下修正非法 kind），必要时错误可带受限公开 UUID 定位。
- **处理结论**：**不阻断，允许延期**（M0 无真实用户数据）。

### F8（P3 轻 · 观察，非缺陷）`dependencies.json` 的 `readOnlyViewPolicies` 为纯声明性文本

- **位置**：`packages/contracts/v2/dependencies.json`（`readOnlyViewPolicies.comparison` / `.report`）；`packages/contracts/src/dependencies-v2.ts`（只读 `policies`）。
- **事实**：`grep` 确认 `readOnlyViewPolicies` **无任何代码消费**；`comparison`/`report` 也**没有对应 registry 能力或 v2 方法**。
- **影响**：**与"业务能力设计项不进入开放名单"一致**（`registry.v2Runtime == []`），不构成缺陷；仅提示不得被后续读者误读为"对比/报告依赖合并已实现"。
- **处理结论**：**非问题，仅记录**。

---

## 6. 历史问题逐项判断（复审）

### 6.1 I03 内部只读审查历史项（`docs/reviews/I03/internal-review.md`）

**我未采信其中的"已关闭"结论，全部用自己的差分探针重放反例。**

| 编号 | 原判定 | 我的独立复核 | 结论 |
| --- | --- | --- | --- |
| I03-A1 `result.current` 跨 kind/definition/scope/参数/实现或 historical 仍被接受 | P2 | `A1:wrong-kind`/`wrong-definitionId`/`wrong-scope`/`wrong-parametersHash`/`wrong-implementation`/`historical-result`/`stale-result`/`other-project-result` **全部 false**；`A1:null-result-allowed` true（合法无当前结果） | **已关闭** |
| I03-A2 `operation.get`/`job.unsubscribe` 身份未绑定 | P2 | `A2:op:other-operation` false、`A2:unsub:other-subscription` false | **已关闭** |
| I03-A3 queued atomic 异 operationId / 带 marker；cancel disposition 与 state 脱钩 | P2 | `A3:*` 4 例 **全部 false** | **已关闭** |
| I03-A4 result.page 超页大小 / job.list 重复、跨项目、过滤、稳定顺序；同 rowId 异 ordinal | P2 | `A4:page-rows-exceed-pageSize`、`joblist-dup`、`joblist-other-project`、`joblist-filter-violation`、`page-same-rowid-other-ordinal` **全部 false**；**多成员稳定顺序经重新构造后实测**：`JL2:asc-ok`/`same-ts-asc`/`PG2:rows-asc-ok`/`same-ordinal-asc` 为 true，`desc`/`same-ts-desc`/`rows-desc`/`same-ordinal-desc`/`dup-jobid`/`dup-rowid` 为 false | **已关闭** |
| I03-A5 终态仍可收同版本反向通知 / seq 与版本缺口 | P2 | `A5:terminal-binding`、`terminal-binding-cancelled`、`version-not-next`、`cancelling-to-succeeded-not-allowed` **全部 false**；合法 `cancelling→cancelled` 为 true | **已关闭** |
| I03-A6 尾换行正则与 lone surrogate 双端分歧 | P2 | `A6:name:'Q1\n'/'Q1\r\n'/'Q1\r'` 全 false、`A6:surrogate` false、`A6:name:'Q1'` true；数值 2.0 双端同 true、bool/小数/NaN 双端同 false | **已关闭** |
| I03-B1 整数浮点 stateVersion 双端分歧 | P2 | `A6:float-stateVersion-2.0` 双端同 true；`2.5`/`bool`/`NaN` 双端同 false | **已关闭** |
| I03-B2 长引用链裸 RecursionError | P2 | `B2:chain-1200`/`4094`/`4095` 双端**同**成功（4095 键含 `facts:asserted` = 4096 上限）；`chain-4096` 双端同拒绝 | **已关闭** |
| I03-B3 同一 stale 原因重复 / before 被改 / 集合成员无定位 | P2 | `B3:dup-dependency`、`before-mismatch`、`before-equals-after`、`model-dependency-stale`、`stale-state-no-reason`、`current-with-reason` **全部 false**；`B3:model-in-vector-ok` true（model 可作依赖、不可作原因） | **已关闭** |
| I03-B4 job/result 空向量仍有效 | P2 | `B4:result-empty-vector`/`job-empty-vector` false；`B4:project-empty-vector-ok` true（项目投影允许空向量，与 `shared-state.md` 一致） | **已关闭** |
| I03-B5 `job.create` 只改 definitionId/derivedResultIds 仍接受；DTO 未保存完整输入 | P2 | `B5:definitionId-changed`/`derivedResultIds-changed`/`parametersHash-changed`/`confirmation-changed`/`outer-input-scope-mismatch` **全部 false** | **已关闭** |
| I03-C1 根 `constraintDefinitionId` 可改而原 `constraintsRef` 仍接受 | P2 | `C1:root-constraintDefinitionId-changed`、`wrong-hash`、`wrong-project`、`wrong-snapshot`、`missing-layer`、`extra-layer`、`asserted-claims-constraint`、`derived-*-non-reasoning`、`derived-*-evicted`、`derived-*-impl-mismatch`、`derived-*-state-mismatch`、`current-selection-historical`、`asserted-scope-with-derived-layer` **全部 false**；`current-selection-current` true | **已关闭** |
| I03-C2 `UNSUPPORTED_SHACL_PATH` 合码误分类（targetClass/datatype 非 IRI 一律称路径不支持） | P2 | 文档三分支（合法范围外路径→`shaclPath`；已确认非法模板项→`SEMANTIC_INPUT_INVALID/constraint`；可信违约/未知来源→`INTERNAL_ERROR`）在 `I05-semantic-boundaries.md` v3 表与 I05 源快照**逐项一致**（我已程序化比对） | **已关闭**（文档级；机器可读守卫缺失见 F5） |
| 内部审查"I05 v3 25/25 无遗漏/误分类、双快照 SHA 一致" | 声明 | 我独立重算两份快照 SHA-256 **全部匹配**；独立程序化比对 25/25 集合与顺序一致 | **确认** |
| 内部审查"I02 合并后新基线无新阻断" | 声明 | 我在含 I02 的新 base 上重跑完整 `npm run check`（420 TS / 622 Python / build）**全绿** | **确认**（仅就静态/单元/构建层面；I02 的原生/e2e 证据不在本线） |

### 6.2 I01 三轮历史意见的 I03 承接（逐项）

`jobs-and-storage.md` 的"I01 交接闭环与错误映射"表是承接声明。我逐条核对**是否真有代码或契约承载**：

| 历史编号 | 原处置 | I03 承接 | 我的核验 | 结论 |
| --- | --- | --- | --- | --- |
| N-R3-1 / F3-01 kind 未守卫（非字符串 kind 被接受） | 延期 I03 | publish/current 共用非空字符串守卫 + 既存 NULL/空键显式拒绝 | `storage.py` 新增 `_result_identity`（`publish`/`current` 共用）+ 开库 legacy kind 拒绝；7 种非法 kind（None/""/"  "/1/False/[]/{}）实测**零写入且 DB dump 不变**；合法身份复跑只保留唯一 current | **已关闭（代码级）**；全库级拒绝的行为特征见 F7（非缺陷） |
| N-R3-2 current 非 dict 实现来源静默 None | 延期 I03 | current 复用 publish 守卫，形状错误与"无结果"可区分 | `current()` 现调用 `_result_identity`；非法 provenance（None/[]/1/False/{}/缺键）抛 `ValueError`（形状错误）而非静默 None，合法未找到才返回 None | **已关闭** |
| F3-02 旧非对象 config 写轮次裸 AttributeError | 延期 I03/I04 | 写前对象检查 + 受限形状错误，零轮次/标记副作用 | `commit_round` 写前 `json.loads(record["config"])` 后 `isinstance(config, dict)` 否则 `ValueError`；5 种 legacy config（None/[]/42/"legacy"/False）实测 **DB dump 不变、progress 仍为 None、history.replayable=False** | **已关闭** |
| F3-03 `collect_cache` 全库范围 | 部分采纳、延期 I03 契约 | 明确全库维护与项目清理的接口区别、pin 顺序、并发预期 | `jobs-and-storage.md` 写明"当前不增加项目清理 API；主进程显式全库范围确认，不向 Agent 暴露；将来增加须单独 schema/授权与跨项目反例"；本候选**确未**新增 project 清理 API | **已关闭（契约级）** |
| F3-04 人工值删除后的恢复语义 | 采纳说明、延期 I03 契约 | 恢复人工值须读历史、重新生成显式 edits、预览、确认、当前 base 复验 | `schema.changeSet.intent` 枚举含 `restore-managed-value` / `restore-historical-manual-value` / `undo-one-changeset` / `edit`；`jobs-and-storage.md` 写明"不是覆盖/修改旧 marker" | **已关闭（契约级）**；实际恢复流程属 I04 |
| F3-05 同批 remove+edits 固定顺序 | 采纳说明、延期 I03 契约 | 显式采用 definitions→remove→edits→manual→mapping 顺序 | `jobs-and-storage.md` 明确该顺序且与 JSON 键顺序无关；同 fact remove+edits 净效果为 edits | **已关闭（文档级）**；顺序本身位于 plan blob 内、无公开机器载体，属 I04 解析责任 |
| F3-06 facts 依赖仅项目级 | 保留延期 I03 | 能力契约决定真实数据范围/实际依赖映射 | `dependencies.json` `factsScope: "facts:asserted"`；`deriveDependencies` 恒以 `facts:asserted` 为基键；`shared-state.md` 写明"不能虚构 facts:某主体"；`staleReason` 仅允许 `facts:asserted` 单一 facts 依赖模式 | **已关闭**；细粒度 facts 键未实现、未被宣称 |
| F-07 提交后异常/投递失败拿不到成功返回 | 部分采纳、I03/I04 统一 | 异常不等于未提交；凭 operation marker/planHash/job 恢复，不盲目重试 | `jobs-and-storage.md` 逐行写明；`schema.commitMarker` 具备 project/operation/job/planHash/前后快照；`operation.get` 为只读对账 | **已关闭（设计级）**，实际恢复属 I04 |
| F-11 / R4 / N-07 锁与 I/O 错误面不统一 | 延期 I03/I04 统一映射 | 只按 `sqlite_errorcode` 主码识别 BUSY/LOCKED→`STORAGE_BUSY`；IOERR/FULL/READONLY/CORRUPT→`STORAGE_FAILURE`；未知→`INTERNAL_ERROR`；禁止匹配/传递异常文本 | `errors.json` 具备 `STORAGE_BUSY`（retryable true，params `retryAfterMs` 1..60000）、`STORAGE_FAILURE`（params 仅可选 `operationId`）、`INTERNAL_ERROR`（严格 `{}`）；`jobs-and-storage.md` 写明映射规则与"禁止匹配/传递 exception 文本" | **已关闭（错误目录级）**；真实 SQLite 异常→码的映射实现属 I04 |
| N-06 重复 `finish_run` / 重复 pin 裸 IntegrityError | 延期 | 服务事务内先查既有证据，同身份同内容返回原记录，异内容 INVALID_STATE； evicted→PAYLOAD_EVICTED | `errors.json` 具备 `IDENTITY_CONFLICT`、`INVALID_STATE`、`PAYLOAD_EVICTED`（params `resultId`）；`jobs-and-storage.md` 逐项写明且注明"S1 内部一次性 SQL 不直接暴露" | **已关闭（契约级）**，实现属 I04 |
| N-03 严格 revision 资格可能没有 current | 部分采纳 | 保留保守策略；无关提交也可能使首个新结果仅为历史；不把历史身份混为 staleReason | `shared-state.md`"保留 S1 严格发布：新发布的 snapshot.projectRevision 必须等于最新 revision…该 kind 可以没有 current"；`schema.result.state` 枚举 current/stale/historical；`staleReason` 模式**不含**历史码 | **已关闭** |
| N-04 未固定 stale 派生载荷可被回收 | 部分采纳 | 载荷可清空而条目/原因/依赖/输入保留 | `schema.result.payloadStatus` 枚举 available/evicted；`historicalSelectionRequired` 必填；`staleReason` 与 `state` 联动（`current` 必 available 且 `historicalSelectionRequired=false`；`historical` 必 true）——我实测 `X:current-and-evicted`/`X:current-and-historical-flag`/`X:historical-and-no-flag` **全为 false** | **已关闭** |
| N-08 pin/current/历史缓存安全 | 无需改动 | 保持回归 | 未回归破坏；I03 未改 pin/cache 行为 | **确认** |
| R6 历史增长 | 延期（真实负载/Q5 后） | 保留已提交历史与快照；不以删除历史补性能 | `shared-state.md` 与 `jobs-and-storage.md` 均保留该权衡；本候选未引入任何历史回收 | **仍开放（按原定边界，非本迭代）** |
| I01 首轮 F-01…F-06、R1/R2/R3/R5 | 已在 S1 内关闭 | 不在 I03 范围 | 我实测 S1 回归（`test_storage.py` 等 622 项全通过） | **维持原关闭** |

### 6.3 I05 v3 交接与 I06 交接

| 项 | 判断 |
| --- | --- |
| I05 v3 25 项细码进入 I03 公共契约 | **已承接且正确**：25/25 集合与顺序与源快照一致；每项有可表达的公共目的地；退休合码零命中；`SHAPE_PATH_UNCLASSIFIED` 仅 INTERNAL_ERROR |
| I05 v3 快照 SHA-256 与逐字性 | **已验证**：两份快照 SHA-256 与 `I05-contract-source.json` 记录一致 |
| I05 源码未冻结、仅交接声明 123 项定向回归 | **本报告不代为宣称通过**；`I05-contract-source.json` 自标 `Unfrozen ... not adopted as public API`；I03 文档亦未把 I05 声明当已验证能力 |
| I06 11 类错误 | **已安全承接且不越界**：`I06-error-disposition.md` 逐类给出"当前可用边界/正式接线前承接"，全部 `GATEWAY_*` 均为**预留未注册**；当前无 S3 方法或网关能力注册项；未把私有码穿透进公共目录 |

---

## 7. 正面确认（核对过且未发现问题的关键点）

1. **候选4 焦点区全部核实通过**：v3 25/25 映射准确；五个退休合码未用于新分支；`SHAPE_PATH_UNCLASSIFIED` 仅 INTERNAL_ERROR；公共目录零内部码；`parameterMeanings` 与 `UNSUPPORTED_CONSTRUCT`/`RESOURCE_LIMIT` 的枚举**逐项完全相等**（我程序化比对键序与取值）。
2. **结构零错配**：14 方法的 request/response ↔ registry ↔ `$defs`；`errors.json` ↔ `schema.error` 26/26；`staleReason` 8 码 ↔ S1 8 码且码↔族配对完全吻合。
3. **双端行为一致**：830 例差分 0 分歧；TS 与 Python 的 `semantic()` 在**已知**差异点（`cursorMatches` 的子集比较 vs Python 全等比较、`job.create` input 的子集比较 vs 全等比较、`validationProjectionMatchesResources` 的实现三元组子集比较 vs 全等比较）**均因 schema 固定键集而不可达**——我逐一构造了"多带一个键/少一个键"的变体，双端结论一致（如 `mr:job.create:response-input-extra-key`、`mr:result.page:response-binding-extra-key`、`cur:record-binding-extra-key`）。
4. **无能力越权**：`registry.v2Runtime == []`、`productRuntime == ['health']`；hello 的 `capabilities` 必须 ⊆ `v2Runtime`（实测 `mr:hello:capability-not-in-v2Runtime` 双端 false）；业务能力（query/reasoning/validation/mapping/changeset/behavior/scenario）与测试能力（`test.*`）仅作为 `job.create` 的 capability 取值存在，均未注册为方法。
5. **安全错误封闭**：越界/多余/缺失参数、free-text message、堆栈、原值参数、2048 字节上界、行列上界全部被拒（我按 26 码逐码实测，26×7 类变体全数拒绝）；`MAPPING_VALUE_INVALID` 不接受 `cellValue`；`INTERNAL_ERROR` 严格 `{}`。
6. **未接线诚实**：`ADR-0003-design.md`"本迭代保留现 v1 health 调用路径，v2Runtime 为空"；`status.md`/`candidate.json` 如实记录未 push/PR/CI/merge、未跑 Electron/e2e/native/HMR/产物；`evidence/validation.json` 的 `notRun` 列表与我的独立验证边界一致。
7. **冻结完整性**：37 份受审文件 36 份 SHA-256 精确匹配，唯一差异为已披露的 `status.md` 纯流程追加；`AGENTS.md` 受保护 SHA-256 匹配且未混入 feature commit。

---

## 8. 证据边界

- 本结论**只覆盖**：v2 契约设计、公共校验器（TS/zod 与 Python 子集适配器）、错误目录、依赖/状态/注册表 JSON、S1 最小边界守卫（kind/provenance/config）、公共语料与文档一致性，以及静态/单元/构建层面的回归。
- 本结论**不覆盖**（且本报告未代为宣称）：常驻 JSONL reader、拆包/粘包/UTF-8 分片、worker 与有界队列、任务持久化与取消竞态、原子 job/marker 对账、窗口重建联验、真实 RDFS/pySHACL/分层图投影、真实语义候选与打包、模型网关、Electron/原生/HMR/产物运行行为。这些属 I04/I05/I06 与 CI 隔离环境。
- 本结论**不采用**任何其他模型或开发者的通过意见；候选 1–3 无外审报告可沿用；我的结论由上列命令与自建探针独立产生。
- 本报告未读取 ZCode 本轮报告或输出，也未修改其任何内容。

---

## 9. 最终结论

**通过。**

- 阻断问题：**0**（无 P0/P1）。
- 中等问题：**3 项（F1、F2、F3），全部允许延期**；其中 F3（contracts 未纳入自动类型检查门禁）建议在 I03 合并前或最迟 I04 接线前以独立小提交关闭——因它会改动 `package.json`/CI，按现行门禁须新候选并重新双审，**不建议在候选4 上追加**。
- 轻等建议：**4 项（F4、F5、F6、F7，其中 F7/F8 为观察记录）**，均可延期。
- 历史问题：I03 内部 A1–A6 / B1–B5 / C1–C2 **全部仍关闭**（我独立重放反例确认）；I01 三轮历史意见的 I03 承接项**逐条已关闭**，仅 R6 按原定边界保留开放。
- 未验证事项已逐条列出（第 4.1 节），其中桌面窗口类验证按 AGENTS 与本次派发明确禁止；`npm run check`（含 build）已由我**实际完整执行并通过**，不再存在此前因共享构建资源而未执行的项。

后续仍需总控处理的事项：读取本报告与另一模型报告、逐项记录采纳/部分采纳/不采纳/延期、双方同版明确通过后再预约 develop 集成与 push；本报告不构成 push/PR/CI/merge 的授权。
