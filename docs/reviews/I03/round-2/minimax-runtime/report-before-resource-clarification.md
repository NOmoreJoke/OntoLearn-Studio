# I03 候选5 独立对抗性审查报告 — MiniMax Code / M3.1-Flash

> 本报告为指定双模型外审之一，独立作出。**未读取**另一模型本轮报告、运行输出或本轮意见；未按其结论调整判断。未修改任何受审实现、依赖、配置或测试；未提交、未推送、未切换分支。仓库内仅写入本报告与 `docs/reviews/I03/round-2/minimax-runtime/`（探针与日志工件），另在 `/tmp/i03-r2-minimax/` 保留完整用例语料与原始 stdout/stderr。

## 0. 结论

**通过。** 未发现阻断（P0/P1）问题；本轮新增 **1 项非阻断 P3**（双端在"畸形可信 binding"上返回行为不一致），其余为已登记的观察/延期项，按原状态保留。全范围 I03 必须验收项均已由我独立实跑验证并留有真实退出码。

本结论**不**把任何未执行的运行项登记为已完成：常驻协调器、真实 JSONL reader、worker/队列、持久 job/marker 对账、窗口重连联验属 I04；真实 RDFS/SHACL 执行、分层图投影、C→Mid→Equipment 反例、外联拒绝与打包属 I05；Electron e2e/原生/HMR/产物启动按本机禁止项未执行；远端 CI、push/PR/合并未发生。v1 `health` 保持、v2 `v2Runtime=[]` 已独立核验。

## 1. 任务、模型与思考设置的来源记录

| 项 | 值 | 来源（两类来源分开记录） |
| --- | --- | --- |
| 任务标识 | `I03-R2-MiniMax-M31Flash-C5-30c10d8` | 派发提示词首段。**这是派发关联 ID，不是原生 UUID**；`docs/reviews/I03/round-2/tasks.json` 亦记 `idKind: "Dispatcher correlation ID in actual prompt; native UUID unavailable in UI"`、`nativeTaskId: null`。我不臆造原生 UUID |
| 模型 | `M3.1-Flash` | **环境自报**：本次会话环境标识为 `MiniMax-M3.1-Flash`。**UI 读回由派发方核验**（`tasks.json` 记 `model: "M3.1-Flash"`、`modelThinkingObservedInFreshTask: true`），我无法独立核验 UI 读回值 |
| 思考设置 | xhigh | **派发方/UI 读回**（`tasks.json` 记 `thinking: "xhigh"`、`modelThinkingObservedInFreshTask: true`）。本环境未提供独立的思考档位读回接口，故此项不属我独立核验范围 |
| 审查角色 | 独立对抗性审查者 | 派发提示词；本次任务为新建独立任务 |
| 报告路径 | `docs/reviews/I03/round-2/minimax-m31flash.md` | 派发提示词指定，与 `tasks.json` `tasks.minimax.report` 一致 |
| 资源预约记录 | "Read fixed source/history + types/unit/engine/tmp-only; full check/build prohibited until explicit resource release" | `tasks.json` `tasks.minimax.resourceReservation`（派发方记录）；我在未获显式释放前未写入共享 `build/out`，全链 check 改在隔离副本执行（见 §4.2） |

**独立性声明**：本轮我未打开另一模型本轮报告/输出/意见文件；对 `docs/reviews/I03/round-2/` 只做过目录名列举（确认 `prompts/`、`tasks.json` 存在），未读取任何 `*-glm53.md`/`*zcode*` 内容，也未据其结论调整判断。round-1 的两份历史报告与 `processing.md` 按派发授权对等读取，用于逐项关闭判定。

## 2. 实际路径、分支、base 与 head（以 git 实测为准）

| 项 | 实测值 |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I03-protocol-contracts` |
| 分支 | `feature/I03-protocol-contracts`（`git rev-parse --abbrev-ref HEAD`） |
| base | `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3`（`git rev-parse` 可解析，与派发一致） |
| head | `30c10d8ad1b9156b1fa5317c6b41b179f927c761`（`git rev-parse HEAD`，与派发一致） |
| 提交序列 | `ad9756e` → `6f35ffd` → `8305d20` → `0ec24b7`（merge origin/develop）→ `f574a72` → `30c10d8`（本轮修订） |
| 变更规模 | 101 个文件，+26214 / −11 行（`git diff --stat base head`） |
| 受保护 `AGENTS.md` | 工作区 SHA-256 = `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，**与派发声明一致**；`git log base..head -- AGENTS.md` 为空 → **未混入任何提交**；我未修改该文件 |
| 工作区 dirty | `M AGENTS.md`（他方规则文件，未 stage）、`?? docs/reviews/I03/{blocked-audit,candidate,frozen-integrity}.json`（流程件）、`?? docs/reviews/I03/round-2/`（本审查工件）。**无受审实现/测试/依赖的未提交改动** |
| push / PR / CI / merge | 未发生（本线无 push/PR/CI/合并动作） |

`apps/desktop` 在 base..head 范围内**零改动**（`git diff --name-only base head -- apps/desktop` 为空），这是 §5 中把 `build` 步骤放到隔离副本执行的依据。

## 3. 全范围检查与每项实际验证 / 失败 / 未验

### 3.1 需求依据（实读）

- `docs/reviews/I03/inputs/scope.md`（I03 行与八项统一门禁）——实读全文。
- `docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md`——S1 退出门槛 6 条、S2 退出门槛 5 条、U1 全节逐字提取（U1 **无编号验收条目**，为两段散文；相关行另见批次 4 表）。
- `docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6——8.6（四段式）、8.7、10.2–10.5、附录 C/D/E/G、FR-006/303/304/401–404/500–505/600–705/803–805 相关条款逐字提取。
- `docs/iterations/I03/acceptance.md`（I03 必须通过 10 行 + I04 必须承接 6 行 + I05 补充验收 4 行 + 候选5 修订验收 4 行）——实读全文。
- `docs/iterations/I03/ADR-0003-design.md`、`protocol.md`、`jobs-and-storage.md`、`shared-state.md`、`I05-semantic-boundaries.md`——实读。
- `docs/iterations/I01/ADR-0002-storage.md`、`docs/reviews/I01/round-3/processing.md`——实读，**I01 仍开放/延期项（7 条 + R6）按原状态保留，未被改写为关闭**。

### 3.2 实现（实读 + 程序化核对）

| 文件 | 核对结论 |
| --- | --- |
| `packages/contracts/src/v2.ts`（557 行） | 纯校验器；无 transport/scheduler/renderer 接线 |
| `packages/contracts/python/contract_v2.py`（474 行） | 与 TS 同源同 JSON；差异见 §6 R2-F1 |
| `packages/contracts/src/dependencies-v2.ts` / `states-v2.ts` / `design-v2.ts` | 依赖闭包/状态边/导出面 |
| `packages/contracts/v2/schema.json`（66 个 `$defs`） | 14 线方法 ↔ registry ↔ params/result `$ref` **零错配**；错误 oneOf 26 分支与 `errors.json` **逐字段全等**；数组全部显式有限 `maxItems`；受限词汇外 **0** 关键词 |
| `packages/contracts/v2/errors.json` | 26 码；7 个含枚举参数的码全部具备 `parameterMeanings`，键序与枚举**完全一致**且说明非空（合计 53 个枚举值） |
| `packages/contracts/v2/registry.json` | 24 项（14 服务方法 + 10 job 能力）；`v2Runtime=[]`、`productRuntime=["health"]`；全部 `implementation` 为 design-only/test-design-only |
| `packages/contracts/v2/states.json` / `dependencies.json` | 状态边与依赖策略与 `shared-state.md`、PRD 附录 E 一致 |
| `packages/contracts/v2/fixtures.json` | 316 cases + routing/cursors/responses/jobListCursors/unicodeMutations/transitions/dependencyChains/validationBindings |
| `packages/engine/src/ontolearn_engine/storage.py`（本候选改 33 行） | 开库 legacy kind 拒绝（:47）、`_result_identity`（:743）共用 kind+来源守卫、legacy 非对象 config 守卫（:952） |
| `tests/unit/contract-v2.test.ts` / `packages/engine/tests/test_contract_v2.py` | 双端测试；断言面向真实预期集合而非数量 |

### 3.3 I03「必须通过」逐行判定

| 验收行（`acceptance.md`） | 判定 | 我的实际验证依据 |
| --- | --- | --- |
| 信封与每方法 params/result 都严格 | 通过 | batch8b：14 方法 ↔ registry ↔ schema 零错配；28 个响应分支 = 14 方法 × ok/result + ok/error；批次 1/3 共 52219 例双端一致 |
| hello、身份与响应绑定 | 通过（设计层；实际常驻握手属 I04） | batch2 的 responses 变异全量双端比对；`matchesResponse` 绑定 id/method/session/project/job/resultId/operation/subscription/nonce；hello 能力必须 ⊆ `v2Runtime=[]`（batch5 独立核验） |
| 安全错误 | 通过 | 26 码全码正反例；batch5b 双端动态穷举 53/53 接受、未知 53/53 拒绝、跨码误用 0；`maxEncodedBytes=2048`、参数 ≤5 项、无原值/路径/堆栈/自由文本 |
| 取消与状态 | 通过 | batch8b：6 状态笛卡尔积 36 组合与 `states.json` 完全一致；`cancelling→succeeded` 需最终提交证明门；同版本倒退被拒 |
| 真实依赖 | 通过 | `deriveDependencies` 双端一致（批次 1 覆盖 `params_job.create` 语义分支）；4096 上界、环去重、悬空拒绝由双端测试与批次 1 变异覆盖 |
| U1 | 通过（契约层） | `shared-state.md` 与 `schema.json` 覆盖项目/任务/不可变结果/实现/范围/参数身份、current/stale/historical/evicted、跨项目/输入/范围/参数/页大小/游标未知与到期拒绝；`job.list` 双身份、快照、`(createdAtMs,jobId)` 稳定序由批次 2 变异实测 |
| S1 实际边界 | 通过 | batch7（31 项全 PASS）：kind=None/''/空格/1/False/[]/{} 被拒且 dump 零副作用；合法身份唯一 current；legacy NULL kind 开库拒绝且零清理；legacy 非对象 config → ValueError 且 progress/history 不变 |
| S1 交接无遗漏 | 通过（契约层） | `jobs-and-storage.md` 逐项承接 I01 round-3 的 7 条延期项（kind 守卫、current 来源 schema、legacy config、collect_cache 全库与 pin 顺序、人工值恢复、ChangeSet 顺序、facts 项目级依赖）+ F-07/R4/N-06/N-07；**R6 明确保持原等级开放/延期**（`jobs-and-storage.md:83`） |
| 独立审查与源输入 | 通过 | `inputs/sources.json` 6 份冻结输入 SHA 我独立重算**全部一致**（batch6c）；两份 I05 交接快照 SHA 一致；`verify:sources` exit 0（12 个归档源）；内部审查逐项处置已存档 |
| 仓库静态与引擎回归 | 通过 | 见 §4；`git diff --check` 内容级 exit 0 |

### 3.4 本轮修订重点项（F1/F2/F3/F4/F6/Z/I05）复核

| 重点项 | 结论 | 证据 |
| --- | --- | --- |
| F1 7 个含枚举错误码的 `parameterMeanings` + 动态穷举 | **通过** | batch5/batch5b：7 码含义键与枚举**顺序完全一致**、说明非空；TS 与 Python 各自 53/53 枚举值被接受、未知值全拒、跨码误用全拒 |
| F2 通用 `resource.limitExceeded` / `protocol.invalidState` + schema/全部夹具 + 旧键负例 | **通过** | `errors.json:252,358`；`schema.error` oneOf 26 分支与目录全等；旧键 `job.resourceLimit`/`job.invalidState` 被 schema 拒绝（batch5）；夹具含"reject retired messageKey job.resourceLimit"(fixtures.json:8253) 与 "job.invalidState"(:8266) 负例；`protocol.md:70` 记录了"不从模板命名空间推断产生者、不自动重放" |
| F3 标准根 typecheck 严格覆盖 contracts/全部 unit/desktop + 注入 exit2+TS2322 + 字节恢复 | **通过** | `package.json:16` 串行三入口；`tsconfig.unit.json` 纳入全部 `tests/unit/**/*.ts`；隔离副本实测：基线 0 → contracts 源注入 **exit 2 / TS2322** → 恢复后 SHA-256 与原值一致且 exit 0 → 单测注入 **exit 2 / TS2322** → 恢复 SHA 一致 → desktop 对照注入 **exit 2 / TS2322** → 恢复 exit 0。我独立算出的两个 SHA 与候选 `evidence/typecheck-gate.json` 记录值**逐字一致** |
| F4 两端动态消费同一预算/版本一致性 | **通过** | batch5：TS 直接读 `errorCatalog.maxEncodedBytes`，暂改为 1 → 合法错误被拒 → 恢复 → 接受；`errors.schemaVersion == registry.schemaVersion == 2`；`schema.$id == urn:ontolearn:contracts:2` |
| F6 E.2/FR-701/FR-704/G.4 场景终态摘要 | **通过（契约层冻结，运行时属 I04）** | `jobs-and-storage.md:73–81`：`succeeded` ≠ 事件耗尽；摘要首行 `run.summary.v1` 固定 cell 顺序；成功 `lastCommittedRound ≥ 1`；零提交失败/取消仅状态且 `committedProgress=null`、不生成成功摘要、不新增提前停止规则或业务方法（batch8b 核验线方法仍为 14，无 scenario/summary/event 新方法）。与 PRD 附录 E.2「达到最大轮数但仍有未处理事件时，运行可结束，但必须标记'存在未处理事件'」、FR-701、G.4 逐句对齐 |
| Z 双端词汇/数组显式有限上界元守卫 | **通过** | batch5：schema 遍历未知关键词 0、所有 `type=array` 节点均有显式整数 `maxItems` 且有 `items`；双端各自有元测试（`tests/unit/contract-v2.test.ts:235`、`packages/engine/tests/test_contract_v2.py:286`）锁定该两条不变式 |
| Z kind 显式白名单/拒绝未知，不静默 trim/归并存储身份 | **通过（契约层 + S1 守卫）** | 公开 `result.kind` 为固定枚举；batch7 实测 S1 内部 `" query "` **原样存储**、与 `"query"` 分列两个 current 键、查找互不串扰 → 无 trim、无大小写归并、无身份合并；`jobs-and-storage.md:83` 记录 I04 须显式白名单映射或拒绝未知值 |
| I05 交接（25 细码 / 退休码 / 来源归责 / SHAPE_PATH_UNCLASSIFIED） | **通过** | batch6c：v3 表 25 行与 `I05-typed-reasons-v3-source.md` 25 码**集合与顺序完全一致**；5 个退休合码（`INPUT_LIMIT`/`RESULT_LIMIT`/`UNSUPPORTED_LITERAL`/`UNSUPPORTED_RDF`/`ASSERTED_SCOPE_REQUIRED`）**不在 v3 表**且仍保留在历史表；`SHAPE_PATH_UNCLASSIFIED` 仅 → `INTERNAL_ERROR`；公共目录**零个 I05 内部码**；v3 每行均可由公共码+公共参数表达；语义预算与 `frame/page/actions/rounds` **零混用** |
| I01 R6 开放/延期不得改成关闭 | **通过** | `jobs-and-storage.md:83` 明写"I01 R6 历史增长及其原等级维持开放/延期"；本候选未改写 I01 记录 |
| 无测量依据的扫描优化不实施 | **通过** | 开库守卫仍为每次 `Store.__init__` 两次全表扫描（batch7 末项实测源码仍在），未做未经测量的优化 |

## 4. 验证命令与真实退出码

原始 stdout/stderr 与退出码逐条保存于 `docs/reviews/I03/round-2/minimax-runtime/logs/`（`*.exit.txt` 为退出码）。

### 4.1 在被审 worktree 内实跑（不写共享 build/out）

| 命令 | 退出码 | 实际结果 |
| --- | --- | --- |
| `npm run typecheck` | **0** | 串行 contracts strict → 全部 unit strict → desktop strict，全过 |
| `npm test` | **0** | 5 文件 / **424 测试通过** |
| `npm run engine:check` | **0** | ruff check 通过 + 119 文件格式检查 + **pytest 626 通过** |
| `npm run verify:sources` | **0** | 已核对 12 个归档源文件 |
| `npm run lint` | **0** | `eslint . --max-warnings 0` 无告警 |
| `npm run format:check` | **0** | 通过。**注意**：`.prettierignore` 含 `docs/reviews`，故该退出码**不覆盖** `docs/reviews/**`（含本报告与仓内评审文档），不能当作这些文件的内容格式校验 |
| `git diff --check base head`（未过滤） | **2** | 仅命中 4 个**原始统一 diff 工件**空上下文行的前缀空格（`docs/reviews/I03/**/*.diff`） |
| `git diff --check base head -- . ':(exclude)docs/reviews/I03/**/*.diff'` | **0** | 实际源码/配置/测试/文档**无空白错误** |

### 4.2 在隔离副本实跑（共享 build/out 由另一任务独占）

我未在派发方未释放前触碰共享 `build/out`。改为用 `git archive 30c10d8` 导出 HEAD 到 `/tmp/i03-r2-minimax/candidate-copy`（node_modules 采用符号链接农场，`@ontolearn/*` 指向副本自身），在其中执行构建类步骤；桌面源码在本候选范围内零改动，故构建证据等价。

| 命令 | 退出码 | 实际结果 |
| --- | --- | --- |
| `npm run check`（含 build 全链） | **0** | eslint → prettier → 三入口 typecheck → vitest 5 文件 **424/424** → electron-vite build（main/preload/renderer 产物生成）→ ruff + **pytest 626/626** |
| `npm run build` | 0 | 产物写入副本自身 `apps/desktop/out`，未触碰共享输出 |
| F3 注入四步（基线/contracts 源/单测/desktop 对照） | 0 / **2** / **2** / **2** | 见 §3.4 F3；三次注入后字节 SHA-256 均恢复为原值 |

**未执行（按本机禁止项与范围）**：`npm run test:e2e`、Playwright、Electron/原生窗口、HMR、产物启动。**未执行且属后续迭代**：I04 运行时与 I05 真实语义（见 §9）。

## 5. 自建探针（累计 56167 例双端差分）

工具链：TS 侧用 Node ESM loader（`hooks.mjs`）直接加载仓库真实 `packages/contracts/src/v2.ts`（Node 原生类型剥离 + JSON 模块适配 + 无扩展名 TS 解析）；Python 侧直接加载仓库真实 `packages/contracts/python/contract_v2.py`。两侧喂同一份 JSON 用例集，逐条比对接受/拒绝。**未在仓库内新增任何源文件。**

| 批次 | 输入 | 规模 | 分歧 | 抛异常 |
| --- | --- | --- | --- | --- |
| 1 | 全部夹具 + 逐字段系统变异（删字段/加未知键/换类型/换枚举值/插孤立代理/数值边界/数组重复反转/嵌套对象破坏） | 25819 | **0** | TS 0 / Py 0 |
| 2 | 游标 / 任务列表游标 / 响应绑定 / 通知路由的逐字段变异 | 3948 | **24**（单一类别，§6） | TS 0 / **Py 24** |
| 3 | 固定种子（20261020）随机模糊，66 个 `$defs` × 400 | 26400 | **0** | TS 0 / Py 0 |

另有 6 组定向断言批次（batch5 34 项、batch5b 双端各 5 项、batch6c 24 项、batch7 31 项、batch8b 17 项）全部 PASS，唯一一次 FAIL（batch5 的 49/53）经定位为**我的探针构造缺陷**（`MAPPING_VALUE_INVALID` 还需 `worksheetId/row/column` 三个必填兄弟字段），已在 batch5b 以正确构造更正，TS 与 Python 各自 53/53 通过；该失败批次与其更正批次**分别独立命名留存**，未覆盖早批。

工件清单、批次命名、退出码、哈希与复算方法见 `docs/reviews/I03/round-2/minimax-runtime/MANIFEST.md`。

## 6. 本轮发现的问题

### R2-F1（P3 · 轻 · 非阻断）Python `accepts_job_event` 对畸形可信 binding 抛异常，TS 同输入返回 false

- **位置**：`packages/contracts/python/contract_v2.py:263-282`（`accepts_job_event`）；对照 `packages/contracts/src/v2.ts:330-355`（`acceptsJobEvent`）。
- **事实**：`accepts_job_event` 在校验 notification 之后直接以 `binding["lastSeq"]`、`binding["stateVersion"]`、`binding["state"]` 取值，**没有像同文件 `validate()`（:248-260，捕获 KeyError/TypeError/ValueError 等）那样的兜底**；TS 侧用 `binding[key]` 与 `binding.lastSeq + 1` 读取同一结构，缺字段时得到 `undefined`/`NaN`，返回 `false`，**不抛异常**。
- **触发条件**：可信 binding 字典缺少 `state` / `lastSeq` / `stateVersion` 任一字段，或 `lastSeq` 为字符串等错误类型 —— 即批次 2 对 routing 夹具的 binding 做 `drop:` / `str:` 变异。
- **影响**：同一输入下**双端行为不一致**（Python 抛 `KeyError`/`TypeError`，TS 返回 false），触及 S2 退出门槛第 5 条"TS/Python 对同一公共样例接受/拒绝一致"的不变式。**当前不可由仓内交付语料触发**（仓内 binding 均形状正确），且 binding 是服务端可信投影、不来自客户端，故**无权限提升、无数据泄漏、无契约封闭性破坏**；实际影响是 I04 接线时，若 Python 侧的可信投影被上游 bug 污染为畸形结构，消费者进程会因未捕获异常中断，而不是像 TS 一样安静拒绝该事件。
- **证据**：`docs/reviews/I03/round-2/minimax-runtime/probe/divergences2.json`（24 条，模式一致：`ts=false` vs `py=THROW`）；批次 2 的 TS/Python 结果文件。
- **建议**：在 `accepts_job_event` 外层补与 `validate()` 一致的 `try/except (KeyError, TypeError) → False`，或先对 binding 做一次显式形状校验（`engineSessionId/projectId/jobId/subscriptionId/lastSeq/stateVersion/state` 齐备且类型正确）。此为纯防御性对齐，不改变任何接受/拒绝语义，**不要求新候选**（可与 I04 接线同批修复）。
- **处理结论**：**允许延期到 I04**，不阻断 I03 合并。理由：I03 交付的是设计与纯校验器契约，该缺陷不影响任何 I03 必须验收项；建议在 I04 引入 Python 消费端之前修复，避免把两端不一致带入运行时。

### 其余观察（非问题，记录）

- O1：`packages/contracts/src/v2.ts:46-48` 的 `fail()` 在 schema 出现受限词汇外关键词时抛 `Error('INVALID_REQUEST')` 且 `validateV2` 不捕获，而 Python `check()` 返回 false。当前 schema 未知词汇 0，该路径不可达；batch5 的元守卫 + 双端测试已把"词汇受限"锁为不变式。后续**若扩展词汇，必须先统一双端失败模式**（TS 捕获或改用失败校验器），否则分歧会变为可达。此即 Z P3-1 的剩余部分，按原记录延期。
- O2：TS 数组在缺 `maxItems` 时静默取 100000，Python 无上界；当前 schema 所有数组均有显式有限 `maxItems`（batch5 实测），分歧不可达。与 O1 同批处置。
- O3：开库 kind 守卫每次 `Store.__init__` 做两次无索引全表扫描（M0 规模下可忽略）。**按原记录延期 I04/Q5 真实负载测量**，本候选未做无依据优化。

## 7. 历史意见逐项判定（契约闭环与运行时完成分开记录）

来源：`docs/reviews/I03/round-1/processing.md`（15 项）、round-1 两份外审报告、以及 I01 round-3 移交项。

### 7.1 本会话 round-1 的 15 项

| 项 | 契约闭环 | 运行时完成 | 我的判定依据 |
| --- | --- | --- | --- |
| MM F1 `parameterMeanings` 仅覆盖 2/7 码 | **已关闭** | UI 文案组装属 I04 | batch5/5b：7 码含义键序与枚举完全一致、非空；双端 53/53 动态穷举通过 |
| MM F2 messageKey 命名空间错位 | **已关闭** | 端到端传播属 I04 | `resource.limitExceeded`/`protocol.invalidState` 已改；旧键被 schema 拒绝且有负例夹具；`protocol.md:70` 记录了不从 namespace 推断产生者、不自动重放 |
| MM F3 标准门禁遗漏新契约/单测 | **已关闭** | — | 根 typecheck 三入口串联；注入 exit 2 + TS2322（contracts 源 / 单测 / desktop 对照）并字节恢复；我算出的 SHA 与候选 evidence 记录逐字一致 |
| MM F4 未消费错误预算/版本目录 | **已关闭** | — | batch5：暂缩预算 → 拒绝 → 恢复 → 接受；版本与 registry/schema `$id` 一致 |
| MM F5 source→public 映射仅 Markdown | **仍开放（明确延期 I04/I05）** | 未完成 | 公共目录零 I05 内部码；25 细码映射表仍是唯一来源文档；未凭空新增第二份映射真相，符合原处置 |
| MM F6 未处理事件终态路径 | **已关闭（设计冻结）** | 摘要生成/消费属 I04 | `jobs-and-storage.md:73–81` 固定布局与语义；I04 验收清单已列明剩余事件/空队列/失败取消/畸形/清理反例 |
| MM F7 性能观察（已撤回） | **保留观察** | 测量属 I04/Q5 | 本候选未做无依据优化，也未宣称提速 |
| MM F8 readOnlyViewPolicies | **保留观察** | I04/I05 接入 | `v2Runtime=[]` 独立核验准确，未虚构已接入 UI |
| Z P3-1 双端不可达 fallback 差异 | **部分关闭** | — | 词汇/数组上界元守卫已在双端加锁并实测（0 未知词汇、全数组有界）；剩余为"未来扩词汇先统一失败模式"的约定（O1/O2） |
| Z P3-2 开库两次全库扫描 | **仍开放（延期 I04/Q5）** | 未完成 | 源码仍为两次扫描；I01 R6 保持原等级开放 |
| Z P3-3 kind 前后空白 | **部分关闭** | 公开映射属 I04 | batch7：S1 原样存储、不 trim、不归并、current 键分离；`jobs-and-storage.md:83` 记录 I04 须显式白名单或拒绝未知 |
| Z 观察1 接收层/应用层 | **已承接（文档）** | 真实传输属 I04 | `protocol.md:44`（接收层：seq>lastSeq、缺口触发 job.get）与 `protocol.md:56`（应用层：连续 seq、严格下一 stateVersion）分层仍完整保留 |
| Z 观察2 cancel 响应决策快照 | **已承接（文档）** | 竞态验证属 I04 | `jobs-and-storage.md:19–29` 取消线性化表保留"判定时刻快照"语义 |
| Z 观察3 `maxActionsPerRound=1000` | **已承接（常量）** | — | `schema.json` `maxActionsPerRound` 仍为 `const 1000`，`maxRounds` 1–1000，与 PRD 附录 E.2 一致；未新增可配置自由度 |
| Z 观察4 historical 选择仍可读 current | **已承接（语义）** | 真实读取属 I04 | `shared-state.md:44` 历史显式选择语义保留；batch8b 未发现与该语义冲突的校验分支 |

### 7.2 I01 round-3 移交 I03 的 7 条（+ R6）

| 历史项 | 契约闭环 | 运行时完成 | 依据 |
| --- | --- | --- | --- |
| N-R3-1 / F3-01 kind 守卫 | **已关闭** | — | batch7：`publish`/`current` 共用 `_result_identity`，非法 kind 零写入、合法身份唯一 current、既存 NULL/空键开库显式拒绝且零清理 |
| N-R3-2 current 非法 provenance 伪装无结果 | **已关闭** | — | `current()` 前置守卫，形状错误 ValueError 与"合法未找到 null"区分 |
| F3-02 legacy 非对象 config | **已关闭** | — | `commit_round` 写前对象检查统一 ValueError，真实旧记录反例零副作用 |
| F3-03 collect_cache 全库范围与 pin 顺序 | **已关闭（契约层）** | 实现属 I04 | `jobs-and-storage.md` 明确全库维护、显式确认、先 pin 后报告、PAYLOAD_EVICTED 语义 |
| F3-04 人工值恢复语义 | **已关闭（契约层）** | 产品撤销 UI 属后续 | `changeSet.intent` 含三种恢复意图；恢复须新显式 edits/预览/确认，不改写旧 marker |
| F3-05 ChangeSet 固定顺序 | **已关闭（契约层）** | — | definitions→remove→edits→manual→mapping 固定顺序写入设计文本 |
| F3-06 facts 项目级依赖 | **已关闭（契约层）** | — | job/result 向量强制 `facts:asserted`；细粒度 facts 键未伪造 |
| **R6 历史增长** | **仍开放（原等级维持，未被改写为关闭）** | 留真实负载/Q5 | `jobs-and-storage.md:83` 明文保留；本候选未实施任何存储优化 |

## 8. 全部问题处理结论

| 问题 | 等级 | 本轮结论 |
| --- | --- | --- |
| R2-F1 Python `accepts_job_event` 对畸形可信 binding 抛异常 vs TS 返回 false | P3 | **非阻断，允许延期 I04**（建议在 Python 消费端接线前修复；纯防御性对齐，不改语义） |
| O1 词汇外关键词时 TS 抛 / Python false | 观察（不可达） | 现状可接受；扩词汇前须统一失败模式（承接 Z P3-1 剩余部分） |
| O2 数组缺 `maxItems` 时 TS 100000 / Python 无上界 | 观察（不可达） | 同 O1；元守卫已锁定当前不变式 |
| O3 开库两次全表扫描 | 观察 | 保持延期 I04/Q5，不做无依据优化 |

历史 15 项与 I01 7 项的处置见 §7，**均已关闭、明确延期或按原状态保留，无一项被改写为关闭而实际未做**。

## 9. 未验证事项与证据边界

| 事项 | 状态 | 理由 |
| --- | --- | --- |
| Electron e2e / Playwright / 原生窗口 / HMR / 产物启动 | **未执行（按本机禁止项）** | 本机不得启动测试窗口；本候选不涉及 main/preload/renderer/CSP 改动 |
| 真实常驻 JSONL reader、worker/队列、任务持久化、取消接线、marker 对账 | **未执行** | 属 I04；`v2Runtime=[]`，无运行实现可测 |
| Python→主进程→窄 bridge→UI 的错误四段式全链路 | **未执行** | 属 I04；纯校验器接受的是已解码 JSON 值，不证明错误真的到达 UI |
| 真实 RDFS / pySHACL / 分层图投影 / C→Mid→Equipment 反例 / 外联拒绝 / 打包 | **未执行** | 属 I05；`I05-semantic-boundaries.md` 与 `fixtures.validationProjectionSemantics.runtimeStatus` 已如实标注 |
| 共享 build/out 内的完整 `npm run check` | **以隔离副本等价完成** | 派发方通知另一任务先独占共享 build/out；我未在其释放前写入共享输出，改为在 HEAD 导出副本执行全链（exit 0），且桌面源码在本候选范围内零改动 |
| I05 交接来源的真实性（I05 未冻结） | **未验证，亦不代为宣称** | 仅核验交接文本与 I03 契约的对应关系与快照 SHA；`I05-contract-source.json` 自标 `status: "Unfrozen I05 handoff table; ... not adopted as public API"` |
| Q2/Q3/Q5/Q6/Q7/Q8/Q9 产品决定 | **未决，未被本线预设** | 契约中所有上限均自述为"契约安全上界，不是容量或性能承诺"；未采纳 Q6 |
| 另一模型本轮报告 | **未读取** | 互不披露本轮意见的门禁要求 |
| push / PR / 远端 CI / 合并 / 远端 develop 核验 | **未发生** | 门禁未到 |

证据边界：纯校验器接受的是已解码 JSON 值，**不证明**原始帧字节、marker 真实存在、hash 对应真实 blob、权限成立、摘要已生成或引擎计算正确；`docs/reviews/I03/` 下的候选文档对此如实声明，与我的判断一致。

## 10. 最终结论

**通过。**

候选 5（base `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3` → head `30c10d8ad1b9156b1fa5317c6b41b179f927c761`）在 I03 冻结范围内满足全部可现实验收：严格信封与逐方法 schema、hello 与身份绑定、安全错误目录（26 码 / 7 码含义 / 53 枚举值双端穷举）、状态机与取消语义、真实依赖策略、U1 身份与分页、S1 最小边界守卫（真实 SQLite 反例）、I01 历史移交项与 R6 开放状态的忠实承接、I05 v3 交接 25 细码与退休码纪律、类型门禁（注入 exit 2 + TS2322 且字节可恢复）、双端 56167 例差分（除 1 类畸形可信 binding 的 P3 外无分歧）。

本通过**不**将任何未执行的运行项（I04 运行时、I05 真实语义、桌面联验、远端 CI）登记为完成，不改变 Q2/Q3/Q5–Q9 决策边界，不构成对 I05 未冻结交接或 `v2Runtime` 空集之外任何能力的承认，也**不**把 I01 R6 或 Z P3-2 由开放/延期改写为关闭。

—— 审查者：MiniMax Code（MiniMax-M3.1-Flash，xhigh），任务 `I03-R2-MiniMax-M31Flash-C5-30c10d8`，2026-10-20。
