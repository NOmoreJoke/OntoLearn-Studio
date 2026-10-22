# T07-S1 round-1 ZCode 指定独立完整审查报告

- 审查者：ZCode 指定任务（GLM-5.3 / 思考最高 / 完全访问，operator UI 实读）。
- 报告日期：2026-10-23。本报告是该 ZCode 任务对本候选的唯一最终报告；由本任务全文写回，无 peer 意见输入。
- **总结论：通过（限本 S1 私有范围）。未发现新的 P1/P2 问题；IR-01～05 逐项确认关闭。全部父功能缺口与发布门保持未通过/未验证，不得将本结论扩大为 T07 父任务或产品能力通过。**

## 1. 任务身份、设置读回与输入受理

| 项 | 实际值 | 来源 |
| --- | --- | --- |
| 应用 | ZCode | 本会话 |
| nativeSessionId | `session_488117259b5e999c5321f8a1141cefd6` | operator 官方任务菜单 Copy session ID，收据 `../T07-zcode-review-f9a1157.runtime/metadata/owner-ui-accepted-retry-20261023.json`（nativeIdSource 记录完整取证链） |
| turnId | UNKNOWN（operator 收据 `officialTurnId: null`，终态时仍待官方补记） | 同上 |
| 任务级模型/思考/权限 | GLM-5.3 / 最高 / 完全访问 | operator 对本任务草稿 UI 实读（pre-submit 与 accepted 两份收据一致）；本会话自观测模型 `account:bigmodel-individual-coding-plan/GLM-5.3`。未扫描 globalconfig/peer/全 session 身份 |
| 正文受理 | 2026-10-23（本会话）完整读取 full-input.txt 全文 | 本报告 §1.1 |
| 终态 | 本报告即该任务最终输出（撰写时） | — |

### 1.1 官方附件受理与逐字核对

- 附件/本地副本同一文件：`docs/reviews/T07/dispatch-20261022/full-input.txt`。
- 实测：143012 bytes、896 行（wc -l）、SHA256 `bfd74c930cddbc9274ef05e30f7c3eaf482a56ff3caa5a10718fdc30128c7287`，与官方声明逐项相等；官方附件与本方副本为同一字节文件（单一文件哈希即证明逐字一致）。
- 全文读取覆盖 1–897 视行（末行无尾随换行，wc -l=896）；"BEGIN EXACT ORIGINAL FROZEN INPUT BYTES" 后旧冻结正文已完整读入。附件声明的旧正文 SHA `377509e0…` 与本树 `round-1/zcode-frozen-prompt.md` 实测一致。
- 受理元数据已存 `../T07-zcode-review-f9a1157.runtime/metadata/zcode-glm53-input-acceptance-20261023.json`。

## 2. 受审身份核验（base/diff/25路径/14项）

- 实际 cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-f9a1157`；HEAD `24f3703ecf4fce75e0d0375f7291ed928f083c41`（detached）。git status 仅 `M AGENTS.md`（受保护策略文件，未 stage、不混入）与 `?? docs/reviews/T07/dispatch-20261022/`（本派发输入）。
- 祖先链实测：base `5f910b52…` 是产品头 `f9a1157c…` 的祖先；产品头是 reviewHead `24f3703e…` 的祖先。`git diff --name-only base..product` 恰为 25 路径。
- `round-1/candidate.patch`：340601 bytes、SHA256 `3e697c94bae835307e1012bb30ea65bbbce680555e488135bfcb267b4210b8a3`，与冻结正文/manifest 声明一致。
- 25 路径身份：`git show f9a1157c:<path>` 内容 SHA256 与 frozen-manifest 逐项相等（25/25）。工作区 24/25 相等；唯一差异 `docs/reviews/T07/status.md` 为冻结后流程更新，manifest 已标 `physicalMatches:false`，产品内容按固定 ref 读取，未混作产品变化——处置正确。
- 14 项实现/测试/fixture：工作区文件 SHA256 与 manifest 逐项相等（14/14）。
- 旧正文中 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario` 仅作历史来源标识；本次全部读取/运行/输出均在本审查树完成，未跨树读取原开发目录或任何会话状态。

## 3. 完整读取范围与封存件核验

已完整读取：round-1 README、frozen-manifest.json、archive-manifest.json、historical-issues.md、internal-review-sources.json、9 条原始内审 final（JSONL 全文）、preparation-audit.md、candidate.patch（哈希层）、25 路径全部内容（含 t09-e5.json 结构与关键字段抽验、169895B 全量哈希核验）、PRD V0.6 于 base 的 FR-700–705、附录 D、E.1–E.5、G.4、G.6、第 10–12 节、docs/iterations/T07 三份文档、evidence 全部 JSON、render-probe.mjs、status.md@f9、internal-review.md。

封存包核验（提取仅至本角色 scratch `../T07-zcode-review-f9a1157.runtime/scratch/frozen-inputs/`，未覆盖固定 review 路径、未执行其中脚本）：

- `frozen-inputs.tar.gz` 946863 bytes / SHA256 `880d4cc9…` 与 archive-manifest 顶层声明一致；75 成员逐项大小/SHA 全部匹配（25 候选、35 原始 log/png、4 历史流程、6 操作快照、4 批准规范、1 原始终态合集），无缺失无重复。
- 9 条原始 final：合集文件 SHA `51f5746a…` 与 sources.json 声明一致；9 条 message ID/时间戳/作者与来源索引逐条对应；导出 payload 正文与 full-input 内嵌可读全文**逐字等价（9/9，含消息头四行）**。逐行 `rawLineSha256` 指向原始 source session 行，按独立性边界未跟随读取（不进正在增长的原会话），该项不在本角色可核范围——如实记为"未复算"，不作为缺陷；封存合集整件哈希与内容等价已足以支撑历史索引真实性。
- 3 条加密中间消息仅登记元信息，未尝试解密。
- 旧 42 项 READONLY 证明按已失效处理，43/44 项修复与交接为不同历史运行，未拼合计数；`ui-identity.log` 哈希 `e3b0c44…`（空文件 SHA）与"空日志不独立证明退出码"声明一致。

## 4. 独立工程审查（按完整正文，不限于 delta）

### 4.1 model.py（身份/FIFO/账本）

- `Capacity` 严格单模式（direct XOR people×per_person，含 direct+部分乘积的拒绝）；`integer()` 用 `type(value) is not int` 正确拒绝 bool。
- `State.created_orders` 不可变账本：同事件重复创建拒绝、身份变更拒绝、跨事件 ID 复用拒绝；`order_sequence` 取账本最大序号单调递增；删除工单后新事件必然得到全新 W 序号（IR-03 修复的机制本体）。`create_order` 对已登记事件幂等（E.1 触发幂等）。
- FIFO 排序键 `(created_round, sequence, id)` 与 E.3 一致；`metrics` 三指标按实际状态集合统计（backlog=非完成数、completed=len(set(累计完成身份))、High 且非 Closed 告警数），未使用简化递推公式冒充（E.4 明确该公式仅限简化测试模型）。
- `Definition`：max_rounds 1–1000、semantics 固定 `scenario-e2-v1`、八个版本/身份字段非空、rules/behaviors/parameters 必须 JSON 对象、initial_consumed 唯一且 ⊆ 事件目录；`digest` 覆盖全部字段（含 initial、initial_consumed），是续跑身份拒绝的根据。`copy_scenario` 要求新 scenario_id+input_version，显式复制不改源。
- 事件目录 `event_catalog`：同 ID 异内容拒绝、同内容去重——E.1 事件身份语义正确。

### 4.2 runner.py（E.2 编排）

- 每轮严格顺序：事件（按 sequence,id 排序、round<=n 且未消费）→ apply_events → 行为前推理 → plan（冻结）→ execute → 生成事件仅准下一轮 → resource_stage → 轮末推理 → 构造完整 Round → commit → 推进 checkpoint。首步对空初始场景也强制真实 initial 推理（Context(round,"initial")）。
- `Context(round, phase)` 显式贯穿，`_inference` 校验 input_state 深相等 + rule_version + context 相等 + snapshot 非空——错阶段/换输入的推理结果被拒（INFERENCE_IDENTITY）。
- 动作边界：action_count 必须为 int 0–1000（`type is not int` 拒绝 bool）；trace 数量=action_count、三元组唯一、event_id 必须属于本轮事件、behavior_id 非空、action_index 正整数；execute 返回数必须等于计划数。缺一即失败且不执行不提交。
- 取消：每阶段间 check()，commit 前最后一次 check，commit 后无取消检查点（durable commit 保持可见）；取消/失败返回最后已提交 checkpoint，未提交轮次零效果。异常经受限错误码传出（ScenarioFailure 仅 code；其余归一 SCENARIO_STAGE_FAILED），无堆栈/路径/原值外泄。
- 续跑 `_validate_resume` 五重校验：digest 全等、round∈[0,max]、消费⊆目录且无重复、定义事件必须在目录中逐字相同、**非 initial 消费不得早于其所属轮次被消费（IR-02）**、已提交轮次事件消费不得丢失、completed 唯一且 ⊆ 创建账本、initial_consumed ⊆ consumed。跨项目/引擎/锁/输入版本续跑全部拒绝（digest 不等）。独立重放从 `_initial`（initial_consumed）开始，不复制源运行历史。
- 达到 max 后未来事件保留在 `pending`，`has_unprocessed_events` 如实暴露；生成事件 round≠n+1 即失败。

### 4.3 test_scenario_persistence.py（真实 Store 边界）

- 被测 `storage.py` 与批准 base 逐字一致（不在 25 路径 diff 中）；测试仅用公共 API（create_project/commit/snapshot/start_run/commit_round/history/load_snapshot/finish_run/collect_cache/state/revision）。`commit_round` 实测具备 operationId 幂等（同内容返回原 snapshot）、终态不可变、顺序轮次、maxRounds 1–1000 边界；`_transaction(hook)` 阶段为 before→BEGIN→(mid_data/mid_marker)→before_commit→COMMIT→after_commit，与测试 PHASES 一一对应，无第二写入通道。
- 故障矩阵（前轮 0/1 × 5 阶段 × 异常/取消/真实 READONLY）：提交后投递失败按公共 history+完整载荷对账确认效果（ack-loss 语义演示），未对账成功不得推断"零提交"；正式哨兵事实与 revision 全程不变；`collect_cache()` 不删轮次；重开后仅已提交轮次可见。
- 10 个真实子进程 `os._exit(92)` 用例：退出码 92、stderr 为空（无业务数据泄漏）、terminal 为 None（崩溃不冒充终态）。
- READONLY（IR-05 修复）：`disk_errors` 捕获 `(isinstance OperationalError, SQLITE_READONLY 码, 名称)` 并在 **runner 外**由 `assert_readonly_fault` 逐例强断言；禁用注入负对照使该断言必然失败——假通过路径已封死。旧 42 项证明未追认。

### 4.4 页面与 presentation（INV-02）

- 历史运行使用 `run.identity`/`run.evidence` 自身不可变依据；`resultLabel`：非成功一律历史标签，成功且 `sameInput`（全 10 字段含引擎/锁/config/语义）才"当前结果"，否则"历史结果 · 输入版本已变化"——V1 晚到不可能成为 V2 当前结果（IR-01）。
- 来源选择（IR-04）：`sourceMode` 显式 project/scenario；project 时 `copySource=undefined`，场景存在时仍可从基准项目创建；无场景时 scenario 选项禁用。
- 受限操作：无适配器方法（actions.X 缺失）或状态不允许时按钮禁用（运行中禁运行/恢复、仅 active 可取消、仅终态可重放/续跑/删除、重放另需 replayAvailable）；错误统一脱敏为固定文案。
- 文本安全：全部动态值经 React 文本节点渲染，无 dangerouslySetInnerHTML/外链资源；封存探针证据含 `<script>bad()</script>` 场景名转义通过（scriptTextEscaped=true，本报告未重跑该探针，见 §6）。
- 结构化输入校验 `validInputs`：对象/数组类型、事件仅 id/round/sequence/payload 四键、safe-integer 边界、同 ID 异内容拒绝——本地格式检查，未冒充 T00 语义校验（文档如实声明）。
- 对比表：仅成功运行参与，缺轮显示"无该轮记录"（null），不补造观测；未处理事件显式计数。

### 4.5 接线边界（防"占位即产品"）

产品头全库检索：`scenario` 在 main/preload/contracts/entrypoint 中仅命中批准 base 既有的查询数据范围枚举（`asserted|asserted+derived|scenario`），与 T07 模块无关；`ScenarioPage` 无任何挂载点，renderer 无 scenario 目录外引用，无 IPC/bridge 通道。`__init__.py` 明示"Product integration is intentionally unregistered"。S1 自称"私有未接线"与代码事实一致，无越权注册。

### 4.6 T09 批准输入消费边界

`t09-manifest.json` source 声明的 base PRD SHA `7586b2c4…` 与本树 `git show base:docs/prd/…` 实测一致；t09-e5.json 副本 SHA 与 manifest 内 `E.5.json` 条目一致；17 项文件哈希清单与 receipt 逐项一致。测试仅消费原字节做资源/指标投影（含告警 4/8/12/16、scheduledFutureEvents 区分），未消费 T09 服务、未把投影称为完整 E.5——与声明一致。

## 5. 问题清单

本轮**未发现 P1/P2**。以下为 P3/观察项（不阻断本 S1 结论，供正式接线阶段处理）：

1. **[P3·设计说明] `initial_consumed` 可声明未来轮次事件**。`model.py:197,221-224` 只校验唯一性与目录包含；`runner.py:171-176` 的未来消费检查显式排除 initial 集合。影响：若未来适配器误声明，该事件整个运行被静默跳过。评估：initial_consumed 属 Definition digest 签名内容，语义是"运行前已显式消费的基线"，属操作者声明而非续跑顺序违规；当前无真实调用方。建议：正式 T01 适配器接线时对 initial_consumed 增加"轮次≤起始轮"或显式确认约束。
2. **[P3·范围说明] 资源阶段"选中即完成"**。`model.py:146-159` 将队列前 capacity 个工单直接置 completed；PRD E.3 允许该最小语义（选择即完成条件），验收文档已明示合成端口边界。真实"达到完成条件"语义留待正式 T06/资源适配；无需本轮修改。
3. **[P3·证据限制] 9 条原始 final 的逐行 rawLineSha256 不可在本角色复算**（指向禁止跟随的原 session 行）。缓解已充分：合集整件 SHA 匹配声明 + 9/9 内容与 full-input 内嵌全文逐字等价 + ID/时间戳全对应 + 准备期独立文档核验已对源行核过。记录为边界，非缺陷。
4. **[P3·观察] `docs/reviews/T07/.gitignore` 忽略 `evidence/*.log`/`*.png`**：原始日志不入库、以哈希索引的方式已由 README/validation.json 如实声明，且 35 份原件已封存于 frozen-inputs.tar.gz（本报告逐项核哈希）。可接受。

## 6. 实际运行验证（本角色隔离环境）

环境：TMPDIR/UV_CACHE_DIR/UV_PROJECT_ENVIRONMENT/npm cache/RUFF_CACHE_DIR 全部指向 `../T07-zcode-review-f9a1157.runtime/` 本角色目录；清除 ROOT_SOURCE_PATH/PYTHONPATH/ONTOLEARN_TEST_ENGINE/ONTOLEARN_DB_PATH；pytest basetemp 用本角色唯一新子目录。本树独占 node_modules 与 .venv（Python 3.12.12 / Node v24.15.0）。原始输出存 `../T07-zcode-review-f9a1157.runtime/raw/validation/002–011`。

| 命令 | 退出码 | 结果 | 首错 |
| --- | --- | --- | --- |
| `uv run --frozen pytest test_scenario_rounds.py test_scenario_persistence.py` | 0 | **90 passed**（46+44，含 READONLY 强断言与负对照、10 真实子进程退出） | 无 |
| `npx --no-install vitest run tests/unit/t07-scenario.test.ts` | 0 | **27 passed** | 无 |
| `npm run check`（lint+format+typecheck+vitest+build+ruff+pytest 全量） | 0 | eslint 0 警告、prettier 全过、3×tsc 通过、**vitest 657 passed**、electron-vite 三环境构建成功、ruff check/format 全过、**pytest 1142 passed (49.10s)** | 无 |

实测计数与封存证据声明完全一致（657 TS / 1142 Py；T07 90 Py / 27 TS）。检查后工作区仅新增 gitignored 的 `apps/desktop/out` 构建产物，源码/测试/配置零改动。

**未运行项及理由**：`evidence/render-probe.mjs` 未重跑——当前派发明文禁止在固定 review checkout 原位执行（避免覆盖旧证据），且其断言目标（presentation 逻辑）已由 27 项单测+代码审读覆盖，封存 `ui-probe.json`（Chromium 151.0.7922.34、双视口、转义/来源可达/未处理事件/错误脱敏）作为历史证据引用、不追认为本轮运行。`verify:sources` 未重跑（归档源未变化，base PRD 哈希已另行实测核对）。dev/HMR、`test:e2e`、`engine:build`、`package:dir`、Electron/GUI、外联模型、付费操作：按派发边界不属于本轮授权，全部未执行。

## 7. 历史问题逐项处置

| 编号 | 本轮判定 | 依据（本 head 实测代码/测试） |
| --- | --- | --- |
| IR-01/P2 V1 历史显示 V2 依据 | **关闭** | RunView 独立 identity/evidence；`presentation.ts:137-148` 非成功必历史、成功需 `sameInput` 全字段；TS 用例 + 封存探针 lateV1MarkedHistorical |
| IR-02/P2 快照提前消费未来事件 | **关闭** | `runner.py:171-176` 拒绝非 initial 未来消费、`:177-181` 拒绝丢失已提交消费；正反例测试在 90 项内实跑通过 |
| IR-03/P2 删除后复用工单 ID | **关闭** | `model.py:104-127` 账本+单调序号、`create_order` 幂等与碰撞拒绝；`test_deleted_order_id_and_event_identity_are_never_reused` 实跑通过 |
| IR-04/P2 已有场景后无法从项目创建 | **关闭** | `ScenarioPage.tsx:34,41,102-111` 显式来源选择，项目来源不传 scenarioId；封存探针 projectSourceReachableWithExistingScenario=true（第三调用 source 为 undefined） |
| IR-05/P2 READONLY 假通过 | **关闭** | `test_scenario_persistence.py:239-267` runner 外逐例断言 `(True, SQLITE_READONLY, "SQLITE_READONLY")` + 禁注入负对照必然失败；本轮 90 项含这些用例实跑通过；旧 42 项证明维持失效不追认 |

## 8. 未验边界（全部保留，不因本报告关闭）

真实 T05 初始/事件后/轮末推理；真实 T06 冻结条件/稳定排序/冲突/动作语义与动作间取消；T01/I04 正式 scenario 任务生命周期、取消竞态、原子进度、终态持久化、operation-id 响应丢失的**正式**对账 API；公共契约/bridge/App 挂载与真实数据接线；用户真实删除运行/恢复基准/从快照创建与续跑；完整 E.5 facts/inferred/actionTrace/triggeredInstances 与真实 RDF 执行；T10 跨设备重放；FR-700–705 及 E.2–E.5/G.4/G.6 的父级跨模块验收；macOS/Windows 完整产品/平台/发布门；push/PR、CI、远端 develop 核验；真人验收。合成 `ProbePorts`/`PersistentProbe` 是编排与事务探针，不证明上述任何一项。

## 9. 结论

在"完整私有轮次编排/资源 FIFO 指标/独立场景页及现有验证"这一 S1 范围内：受审身份链（base→产品头→reviewHead、25 路径、14 项、candidate.patch、封存包、9 条历史终态）完整且逐项哈希吻合；实现与测试经完整源码级独立审查未发现新的 P1/P2；四类运行验证（专项 90 Py、27 TS、全量 check 657 TS/1142 Py）在本角色隔离环境全部通过且与封存证据一致；IR-01～05 确认关闭；文档对自身边界的表述与代码事实一致（无私有能力冒充、无越权注册、无父验收冒领）。

**判定：通过（限上述 S1 私有范围）。** 本判定不构成 MiniMax 同版审查、push/PR、CI、合并、父模块/平台/发布或任何未验边界的通过；产品/测试/配置/依赖/验收/base 变化后须新候选与双方各全新完整审查。任务级实际设置已由 operator 收据读回（GLM-5.3/最高/完全访问，session `session_488117259b5e999c5321f8a1141cefd6`）；turnId 待 operator 官方补记，缺项按 UNKNOWN 如实保留，未据此预填任何通过。
