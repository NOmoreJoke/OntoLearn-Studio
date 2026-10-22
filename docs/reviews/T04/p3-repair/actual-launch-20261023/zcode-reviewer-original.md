# T04-S1 修复候选 5070004：ZCode GLM-5.3 全新完整独立审查报告（Round-2）

结论先行：**通过**（仅适用于本报告登记的同版完整 T04-S1：批准共享基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3` → 固定产品 `5070004ec8e3219bea33960bd88f57f1976e9cf8` 的全部 42 项产品文件及其登记边界）。未发现 P1/P2 阻断问题，也未发现新的 P3 产品问题。旧 554 轮双方四项 P3（D1–D4）逐项独立确认正确修复并有真实运行证据；历史 11 项结论（10 项 closed＋1 项 partial）按原样复核并在 507 中保持。旧 554 双 Pass 未被继承，本结论是全新独立判断。**完整父 T04 与产品功能仍未完成**，第九节所列真实执行/接线/平台/发布门全部未验证，本结论不构成对它们的通过，也不代判另一方，不授权 push/PR/CI/merge。

## 1. 任务来源、设置与时间线（真实读回）

- 任务来源：原 T04 owner 经 computer use 在 ZCode 中创建的本方全新任务并向其投递完整正文附件；本会话即该任务实例。
- 会话/轮次：`session_17ab107de1b57d5bb5eaa88a997731d0` / 原轮 `turn_aadae121-702d-4abc-9abb-e8adc94aaf43`（来源：操作者收据 `test-results/t04-review-runtime/zcode/owner-task-settings.json`，`recordedAt 2026-10-22T18:07:35Z`；原生事件 `metadata/first-own-turn-and-model-scalars.json` 于 `18:17:45Z` 从本机官方 jsonl 以精确 SID+原轮过滤读回：`turn.started 18:05:20.711Z`）。
- 模型/思考/权限：UI 读回 `GLM-5.3` / `最高` / `完全访问`（yolo）；原生模型标量 `modelId GLM-5.3`、`providerId account:bigmodel-individual-coding-plan`（`18:05:40.282Z`）与本会话实际运行环境一致。`fullNativeInputReadProof` 在收据观察时点为 pending，随后 `metadata/input-read-proof.json`（`18:20:54Z`）从本会话官方 rollout 以 SID+原轮+requestId `47ff7638-5425-42b3-9634-204ba30f4207` 重建：附件 137 行（136 内容行＋终 LF）、26203 字节、SHA-256 `c9a2892d…c7eb3`，与冻结提交附件**逐字节相等**，`fullReadAccepted: true`。截至本报告撰写，原轮终态事件尚未落盘（任务进行中），操作者须按规则在完成后从官方状态读回同 SID＋原 turn 终态与全文报告，不以本文件存在替代。
- 附件：`docs/reviews/T04/p3-repair/launch/full-zcode-input.md`，26203B / SHA-256 `c9a2892dec9cccebaba784a10a6a9050a9e02a0fe2eebb74fd1d7316d32c7eb3`，136 行完整读取（Read 全文＋编号行重建证明）。
- 未读取另一方（MiniMax）本轮任何材料；`full-minimax-input.md`、`mapping-minimax.json` 仅在目录列举中见到文件名，未打开。未读全局凭据，未调用付费模型 API。

## 2. 身份、来源与完整性核验（全部实际执行）

| 项 | 声明 | 本方实测 | 结果 |
| --- | --- | --- | --- |
| 唯一路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-zcode-review-5070004` | `pwd` 一致；detached，无开发分支 | ✓ |
| 实际 review HEAD | `f2102f07…` | `git rev-parse HEAD` = `f2102f0738706d7ed29907ac84f10ad0a506555a`；`git status --short` 仅 ` M AGENTS.md` | ✓ |
| 固定产品/基线 | `5070004e…` / `5f910b52…` | 两提交均存在；HEAD 为产品后单条流程提交 | ✓ |
| 完整产品 diff | 256242B / SHA-256 `27c090fc…5b030` | `git diff --binary 5f910b52 5070004e` 实测 256242B、`27c090fc00cd6d1a851695551c2d5e4e9714d9845b9d5f3ee91ae51f9995b030` | ✓ |
| HEAD 相对 507 | 仅流程证据 | `git diff --name-status 507..f2102` 全部为 `docs/reviews/T04/p3-repair/{launch,post-freeze-review,preparation-audit}` 新增，无源码/测试/配置/锁变化；且 42 项产品文件按 Git blob 与工作树三方逐字核验（见下行），不视为新产品 | ✓ |
| 42 项产品文件 | product-manifest.json 逐项 bytes/sha256 | 脚本逐项：产品 507 Git blob = 当前工作树 = manifest，42/42 全等、0 缺失 | ✓ |
| candidate-files 22 项 | runtime/test/fixture/probe 子集 | 与 42 项清单对应条目哈希一致；仅子集，未替代 42 项核验 | ✓ |
| 保护 AGENTS | 15147B / `de15f6ce…` 仅 M 不提交 | 审前审后两次实测同值；未 stage/覆盖/格式化 | ✓ |
| 锁文件 | 无依赖变化 | `package-lock.json` `a462ba70…`、`uv.lock` `d5d027da…`，与 554 轮登记值相同 | ✓ |
| 本方 setup | uv0 + npm 首败 ECONNRESET + 重试成功 | `launch/setup-zcode.json` 三条记录（16:47–16:49Z）；仅为环境安装，非测试通过 | ✓ |
| 554 历史档案 | 71 成员，源自 `9da9da48…` 原字节 | 解包 71/71 到本方 `history/` 只读；`internal-candidate` 与内审 1–7 共 8 份与 507 产品 blob 逐字相同 | ✓ |
| R1 raw 归档 | 37 成员/61602B/`c17c2595…` | 档案内 `raw-logs-554ec89.tar.gz` 与 `9da9da48` 提交 blob 逐字节一致；37/37 成员 bytes/SHA 与 index 全等 | ✓ |
| T09 固定输入 | 提交 `873c8c05…`、manifest `aaaef2c0…` | 提交存在；provenance 归档 19 项（17 输入＋PRD＋manifest）全部哈希一致；manifest 17 项逐一对照原件哈希 17/17 通过；PRD 三方一致（provenance=manifest.source=当前树，`7586b2c4…`）；产品消费的 G-base/conventions/unclosed-high 三副本与 T09 原件逐字节相同 | ✓ |
| owner 验证归档 | `owner-verification-raw.tar.gz` 51 成员 | 解包 51 成员；verification.json 25 条命令 raw 的 bytes/SHA 25/25 匹配 | ✓ |

## 3. 已读完整范围

- **42 项产品文件全部逐字读取**：源码 7（`drafts.py`、`query_service/__init__.py`、`draft.ts`、`results.ts`、`reader.ts`、`QueryPage.tsx`、`query.css`）、测试 5（Python 2＋TS 3）、fixture 9（approved-baseline 5 原件＋authoring-case＋draft-boundaries＋p3-interaction.tsx）、探针 3（ssr-probe.mjs、p3-interaction-probe.mjs、fixtures.json 不在本清单）、文档 18（status/acceptance/计划/两独审/冻结后回执/candidate-files/verification.json/owner-verification-raw/integration-handoff/reader-integration/internal-candidate＋内审 1–7/final-verification/verification-summary）。
- **过程补充**：`post-freeze-review.md`、`preparation-audit.md`、launch 全部策略文件（current-agents/desktop-policy/permissions/section9，与正文附件一致）、`mapping-zcode.json`、`preparation-state.json`、`operator-deployment.json`、`owner-task-settings.json` 及其 UI 证据清单、`input-read-proof.json`、模型标量读回。
- **历史**：旧双方原报告（`zcode-glm53.md`、`minimax-m31flash.md`）、`owner-disposition-20261023.md`、`verification-and-history-index.md`、内审 1–8 全文、`internal-candidate.md`、旧 evidence 三件（reader-service 索引、raw index、两份旧候选 verification 原件）、launch/process 材料（按清单只读）。
- **父需求依据**：PRD（base 与当前树同哈希）FR-400–404、FR-006、附录 C（SELECT/ASK 仅项目内只读，CONSTRUCT/DESCRIBE/更新/远程联邦非 P0）、附录 D（失效表；仅模型配置变化不使领域结果过期）、附录 G（Q-01 完整结果只有 A01、Q-02 A01 改 Closed 后空、O-01 显示"未记录"不得展示为"已证明不存在"）、第 11–12 节（指标与端到端验收）。
- 未把 `final-verification.json`（c4 候选）与 `verification-summary.json`（4c17 候选）的旧汇总当作本轮终态；507 终态以 p3-repair/verification.json 为准，且经本方独立重跑对齐（见第 4 节）。

## 4. 本方实际执行的验证（每条含完整收据；cwd 均为本审查树）

日志工具 `launch/run-review-command.py`（未修改），每条命令保存 argv/cwd/UTC 起止/真实 exit/raw 与 SHA-256 于 `test-results/t04-review-runtime/zcode/{metadata,raw}/`。

**首失败（保留）**：首次尝试用 PATH 上的 `python3`（解析到 Xcode Python 3.9）运行日志工具，`ImportError: cannot import name 'UTC' from 'datetime'`（工具要求 ≥3.11），两条命令在写 raw 前即失败；原始失败与处置记录于 `raw/first-failure-python3-version.md`。属环境问题（项目要求 3.12），改用本树 `.venv/bin/python`（3.12.12）新 label 重跑，未改产品/测试/工具。

| label | argv | UTC 起止 | exit | 结果 |
| --- | --- | --- | --- | --- |
| targeted-ts | `npx vitest run t04-query-authoring t04-query-results t04-query-reader` | 18:16:22–18:16:25 | **0** | 3 文件 **89** 项（57+8+24）全过 |
| targeted-python | `uv run --frozen pytest test_query_service_authoring.py test_query_service_approved_baseline.py -q` | 18:16:25–18:16:26 | **0** | **115 passed**（112+3） |
| ssr | `node docs/iterations/T04/ssr-probe.mjs` | 18:16:37–18:16:38 | **0** | 14 项静态检查全过；raw 423B/SHA `f730e859…f80874`，与 owner 归档 `ssr-after-fix` **逐字节相同**（独立复现） |
| full-check | `npm run check` | 18:16:48–18:18:11 | **0** | lint 0 警告；prettier 全过；三套 typecheck 全过；vitest **18 文件/719 项**；electron-vite build main/preload/renderer 成功；ruff check＋format 196 文件过；pytest **1167 passed in 60.77s**。与 owner 收据（TS719/Python1167）逐项一致 |
| component | `node p3-interaction-probe.mjs '/Applications/Google Chrome.app/…/Google Chrome' review-zcode` | 18:18:24–18:18:33 | **0** | Chrome 155.0.8059.85 headless/offline；`requests: []`、`pageErrors: []`；5 情景全过。产物 `test-results/t04-p3-repair/browser/review-zcode/`，其中 `interaction-results.json`（807B）SHA `bd16e983…1c76` 与 owner final 轮**逐字节相同**（独立复现） |

**独立反例（本方 runtime，未触产品）**：`counterexamples/cross-lang-boundary.{mjs,py}` 自生成 **141** 个跨语言用例（30 个边缘空白字符逐字符×前后缀/三连/sparql 包裹；非 trim 控制字符 U+00AD/U+200B/U+2060 保留；astral 边界 63+q=127、64=128、253 拒、空白后 64/65 单元；65535/65536/65537 邻界；lone surrogate；混合边缘空白核），比对 TS `draftSchema` 与 Python `validate_draft` 的接受判定与规范化值：**141/141 一致、0 分歧**（105 接受/36 拒绝同判，规范化值逐字相同）。反例探针自身首失败两次（TS ESM 转译未导出；Python lone-surrogate 默认编码拒绝），记录于 `counterexamples/first-failure-probe-harness.md` 后修正探针重跑；产品未改。

**owner 大 trace 原件**：5 个 `interaction-trace.zip`（987KB–1.78MB）在 owner 树本地 ignored，本树不存在，**不可逐字核验该大原件**；本方以重跑组件探针得到逐字节相同的结果 JSON 作等效独立证据，不以其哈希自述冒充已读。

## 5. 完整 S1 逐项审查结论（42 项全读后归纳）

**Python `query_service` 与 TS `draft.ts`（FR-400 编写面）**：离线告警模板（High/Open 二条件、告警等级/状态二字段）、`compile_visual`/`compileVisual` 两实现输出逐 token 相同并与 `authoring-case.json` 金样例互验（两侧完整字符串断言）；IRI 校验（scheme 前缀＋空白/控制/`<>"{}|^\`\\`＋DEL＋代理项拒绝）、literal 序列化（JSON 短转义即 SPARQL ECHAR/UCHAR、`\x7f→\u007F`、语言/数据类型互斥、语言小写、8192/64/2048 上限码点两侧一致）等价；注入尝试（SERVICE/`}`/`#`）经 RDFLib Turtle 往返证明为单一 term。条件 32、字段 16、六字段严格形状、scope/source 枚举、`type is int` revision、definitionId 正则拒路径穿越。`save_intent` 仅产出不可变值意图；`__init__` 仅导出 4 个纯函数；编写不激活执行（model 文本仅草稿）。

**D1（Z-P3-1/M-F1）统一 name/SPARQL**：`drafts.py:40-48` 先现有 `_text`（码点＋lone-surrogate），再 `len(value.encode('utf-16-le'))//2 > maximum` 原串 UTF-16 上限，再 `_DRAFT_EDGE_SPACE` 固定集合 strip、拒空；`draft.ts:56-70` `scalarText.refine(s.length<=max)`（JS length 即 UTF-16）→ 同一 30 字符集手动 trim → 拒空。30 字符集合两侧逐字符相同（Python 29 空白＋U+FEFF；fixture `trimEdgeCodePoints` 30 码点参数化两侧共用）。顺序语义正确：`128+' '` 原串 129 拒绝、`127+' '` 接受（trim 后 127），fixture 20 case 断言规范化值等于核心而非只查长度；astral 64/65（name）、32768/32769（sparql）与 65536/65537 邻界覆盖；内部空白不动。description/question/RDF 上限未改（码点，两侧一致）。**判定：正确修复。** 另有本方 141 组独立反例 0 分歧（第 4 节）。

**QueryPage/CSS（FR-400/401/403）**：模板按钮无词汇禁用并提示；可视条件显式 RDF 类型选择（literal/iri 切换保留 value 文本）；SPARQL 编辑器可见可编辑；model 草稿经 `draftSchema` 后 `source:'model'` 载入；数据范围 select 持续显示、执行输入显式当前/历史快照并传 `{selection,snapshotId}`；结果身份 5 元组＋`executedSparql`（string、trim 非空、≤65536）校验，失败整块拒绝显示；实际执行 SPARQL 取自结果对象（`<pre>` 纯文本，React 转义经 SSR 探针核验）；null→"未记录"（O-01 UI 语义）；空页区分有无后续页并列 5 条可操作方向（含"不能据此证明业务事实不存在"）；"最多 200 行、导出仅当前页"如实声明；无示例结果（`!result` → "模板和草稿不会生成示例结果"）。CSS 无 `dangerouslySetInnerHTML`/Node/IPC/网络。stale 列表逐条 code/dependency/before→after 渲染，`staleReason` 只读自批准 result schema。

**D3（Z-P3-3）16 字段 UX**：`QueryPage.tsx:232` "已选 n/16"；`:238-240` 仅当 `length>=16 && 未选` 时禁用该复选；`:243-252` onChange 在 functional updater 内按最新 state 拒绝重复与超 16，已选可取消；condition 32 上限（`:424` 按钮＋schema＋Python）保持。真实 DOM 探针 16→字段17 禁用→取消 01→可选 17→生成完整 16 字段 SPARQL 核对。**判定：正确修复。**

**D4（M-F3）visual 重置**：新建（`QueryPage.tsx:548-557`）、成功载入 saved（`:559-574`）、成功载入 model（`:536-547`）均 `setVisual(emptyVisual())` 并推进 `documentGeneration`；生成按钮 `:442` 取真实 `visualSchema.safeParse(visual).success`，失败禁用并给检查提示（`:445`）；`build()` 内 `compileVisual` 抛错时不 `update`，原草稿不覆盖；RDF 类型切到非法 IRI 后生成禁用、编辑器原文保持、修正（填 `urn:High`）后生成将 `"High"` 替换为 `<urn:High>`——DOM 探针第 1 情景完整核验。模板按钮仍显式填充自己的 builder（`build(alarmTemplate(vocab),'template')` 即 `setVisual` 模板值）。不从任意 SPARQL 反解；definitionId/generation/保存身份逻辑未改。**判定：正确修复。**

**保存/复用（FR-404）**：私有 `SavedQuery{definitionId,draft}`；同名不同 definitionId 区分（测试）；新建保存回调返回 ID 经 `definitionIdSchema` 严格解析回填，更新时返回 ID 必须一致否则 `query.invalidIdentity`；ID 绑定需同 request token 且同 documentGeneration（新建/载入/卸载推进，迟到回执不绑）；保存期间新编辑由 `editRevision` 提示。无 `onSaveDraft`/`onExecuteDraft` 时按钮禁用并显示"尚未接入/尚未持久化"；renderer 不自报 ID、不写 Store；正式 CAS/preview/confirm/commit 仍属 T01 父接线（如实保留为缺口）。

**results/reader（FR-401/402/403）**：直接复用批准 5f 契约（`validateV2('result'/'page'/'pageBinding'/'job'/'result_job.cancel')`、`isTaskUpdate`、`TaskView/JobView/SafeError/internalError/safeError`、DesktopBridge 四命名方法）；五字段身份逐层复验；generation/project/snapshot/revision 变化全量重置并废弃在途读；连接失效废弃在途读；仅消费真实发行 cursor（`nextPage` 要求等于当前页 `nextCursor`；`fetchPage` 拒自循环 cursor）；页内行唯一/有序（`ordinal+rowId` 严格递增）＋跨页倒退/重复拒绝＋最后非空行两字段锚跨空页保留；evicted 保留身份不请求缺失载荷；快照 `structuredClone`；仅一页载荷。`executedSparql` 原文保留（trim 仅非空判定，测试含首尾空白原样）。未扩大 bridge、未新公共协议、未发行 cursor。

**任务/取消**：`queryJob` 复用批准 job validator 限定同项目＋`capability==='query.execute'`；activeJob 期间执行禁用；取消 single-flight（`cancelBusy`）经 `return await refreshJob` 覆盖 ACK 后权威重读全生命周期；ACK 经 schema＋jobId＋版本不回退校验后仅设 `cancelFloor`（该下限贯通 refreshJob/通知/取消前 getJob 三处），`cancelRequested` 与真实终态分离；`compatibleJob` 拒同版本矛盾与已观察终态重开、允许版本跳跃；旧结果（jobId 不同）持续标注"此前查询结果"；dispose 只清显示态不取消 worker；`alreadyTerminal` 不再请求取消。24 个合成 transport 测试全部对应上述语义。

**错误（受限）**：`invalid(field)` 固定 `INVALID_REQUEST`＋`params.field∈{identity,params,cursor}`（批准枚举）；`read()` 参数问题归 `params`、身份归 `identity`、分页归 `cursor`；原始 bridge 异常固定 `internalError`，测试以 `PRIVATE_PATH` 标记验证不泄漏；页面失败说明走受限 `explainError`。无假结果/执行、第二可变权威、共享抢写、未批准依赖。

**D2（Z-P3-2/M-F2）CSV（FR-403）**：`results.ts:80-106` 列头必 string（≤64 列）；仅 string（含列头）做公式（`^[\s]*[=+\-@]`）与前导控制字符（`^[\t\r\n]`）防护并加 `'` 前缀；有限 number/boolean 输出 `String(value)` 规范文本（真实 `-5`→`-5`、`-0`→`0`、`1e-7`→`1e-7`、bool→true/false），null→空单元格；NaN/Infinity/undefined/对象/数组 fail-closed throw；引号双写、CRLF、BOM、≤200 行。测试精确断言：字符串 `'-5'` 与数值 `-5` 语义不同（前者 `'` 前缀）、字符串负数/前导空白/控制字符/引号逗号换行/200 边界全过，字符串防护未削弱。**判定：正确修复。**

**T09 固定输入（S1-C）**：manifest 17 项＋PRD 来源哈希链完整；测试每次运行重核 manifest 与选用文件哈希，仅从 ontology+facts 独立还原（不读 expected、不用 T09 helper/Store）；原始 `unclosed-high.rq` 与生成查询独立还原 G-base 完整结果均仅 `alarm/A01`（Q-01），A01 改 Closed 后均空（Q-02）；同数量错义反例（`"Open"→"Closed"` 完整答案 A02 与 A01 行数相同）以完整集合比较。本方已读 G-base 原件独立印证语义（A01=High/Open、A02=High/Closed、A03=Low/Open）。产品仅消费三副本；**本轮 provenance 归档提供全部 17 项原件，本方逐项哈希 17/17 核验通过**——上轮 M"仅 3/17 可核"的限制在本轮不再成立；但该 14 项额外原件仍是只读 provenance，不构成"已运行"或正式规则/行为/Store 验收。

**测试/fixtures/探针全量**：TS 3 份（57+8+24）与 Python 2 份（112+3）断言完整预期集合/顺序而非数量；`draft-boundaries.json` 两语言共用同一原始边界（非 trim 后）；`p3-interaction.tsx`/probe 为隔离组件 fixture（无桥接/执行/持久化/模型调用，offline＋route abort＋唯一运行名防覆盖）；SSR 14 项纯静态。文档声明边界与实现一致，无把占位/替身说成产品能力之处。

## 6. 历史意见逐项独立复核（在 507 上重新独立判断，不沿用旧 closed）

| 项 | 独立复核证据（本方源码/运行） | 结论 |
| --- | --- | --- |
| R1-01 保存身份 | `draft.ts:158-165`（SavedQuery/definitionIdSchema）、`QueryPage.tsx:505-530`（真实 ID 回填/更新一致/token+generation）、`t04-query-authoring.test.ts:116-131` | 在 507 保持关闭 |
| R1-02 非查询任务可取消 | `results.ts:108-121`、`QueryPage.tsx:148-151,580-621`、results 测试 #7、reader 测试 #10、SSR | 保持关闭 |
| R5-01 ACK 后提前释放 | `reader.ts:357-425`（try 内 `return await refreshJob`，finally 释放）、reader 测试 "holds the cancel single-flight guard…" | 保持关闭 |
| R5-02 空页丢锚 | `reader.ts:78,237,294-304`（仅非空页更新锚）、测试 10→空→5 拒/11 收 | 保持关闭 |
| R5-03 ACK 版本下限丢失 | `reader.ts:79,188-190,412-415`，三处共用 `minimumJobVersion`，测试 "keeps the ACK version floor…" | 保持关闭 |
| R5-04 trim 改写原文 | `reader.ts:34-38`（trim 仅非空检查）、测试 "preserves the exact actual execution text…" | 保持关闭 |
| R6-01 params={} | `reader.ts:57-63`＋各失败路径分类＋catch 固定 internal；测试 #3/#7/#9 | 保持关闭 |
| 同版本矛盾/终态重开 | `reader.ts:177-186 compatibleJob`；测试 v4 同版本拒、v6 跳跃收、v7 重开拒 | 保持关闭 |
| 同数量错义反例 | `test_query_service_approved_baseline.py:86-95` 完整答案比较；本方 targeted-python 实跑 115 通过＋读 G-base 原件印证 | 保持关闭 |
| 总控 R1 raw 归档可恢复 | 归档在旧树流程提交 `ae86f294→9da9da48`（不在 554/507 产品树内），本轮经历史档案内嵌副本核验：与 9da blob 逐字节一致、37/37 成员哈希与 index 全等、61602B | 保持关闭（恢复途径：9da 提交或本轮历史档案） |
| T09 provenance（上轮 partial） | 上轮 M：3/17 可逐字核、14 项不可核（partial，如实保留）。**本轮 17/17 全部逐字核验通过**，该 partial 在本轮条件下已可完全核验；仍未扩大为正式 Q-01/02 运行验收 | 上轮 partial 记录不被抹平；本轮条件升级为全部可核 |

**旧 M 报告开头"11 项历史结论确认关闭"表述与其实际表格不符**：表格为 **10 项 closed ＋ T09 provenance 1 项 partial**（"部分可核，其余仅记录"）。本报告按 10＋1 如实记录，不抹平 partial。

**旧 Z columns 观察为事实误读（不复述为保证）**：`reader.ts:33` `columns: z.array(z.string().min(1).max(128)).max(64)` 的 `.min(1)` 约束每个列名字串非空，数组本身允许 `[]`。父适配器/查询元数据对零列与 ASK 的语义仍未定，本报告不将该误读当作已有"至少一列"保证。

## 7. 四项 P3 修复逐项判断（旧双方意见 → 507 实现）

| 编号 | 旧意见核实边界 | 507 实现与验证 | 本方判定 |
| --- | --- | --- | --- |
| D1（Z-P3-1/M-F1） | Python 原文判长后 strip vs TS 先 trim 后判长，5 个边界例分歧；UI 当前传规范化值无跨界故障 | 原串 UTF-16 上限→固定 30 字符 trim→拒空，两侧逐字符同集合；共用 boundary fixture 断言规范化值；本方另以 141 组独立反例 0 分歧 | 已正确修复，验证充分 |
| D2（Z-P3-2/M-F2） | 数值 `-5` 被加 `'` 前缀，保真下降；防护本身正确 | 仅 string（含列头）防护；有限 number/boolean 规范文本；非法类型 fail-closed；测试含真实负数/字符串负数/`-0`/`1e-7`/公式/控制字符/200 边界 | 已正确修复，验证充分 |
| D3（Z-P3-3） | 编译器 fail-closed 但超 16 后无 UI 上限反馈 | 仅禁未选、可取消、显示 n/16、最新 state 防超限；真实 DOM 验证 16/17/取消重选；32 条件上限独立保持 | 已正确修复，验证充分 |
| D4（M-F3） | 新建/复用不重置 visual，遗留构建器可静默覆盖新载入草稿；RDF 类型切换仅通用提示 | 三种载入均清空 visual＋推进 generation；生成按钮取真实 schema 有效性并给提示；非法切换不覆盖原草稿、修正后生成；真实 DOM 5 情景（含非法 RDF 类型负例）全过 | 已正确修复，验证充分 |

## 8. 本轮新发现

**无 P1/P2/P3 产品新发现。** 观察项（不计发现、不需本候选处置）：

1. `query.css` 中 `.query-check input`、`.query-condition` 未限定在 `.query-workspace` 作用域内（沿用上轮 M 观察；当前仓库无同名冲突，父 App 样式接线时收敛）。
2. `exportPageCsv` 自身不重复列名 ≤128 检查（`results.ts:84`），该界由上游 `acceptPage`/`presentationSchema` 在两条真实路径保证；直连路径无第三入口。
3. `QueryPage.tsx:133` 对 `executedSparql` 用 `length`（UTF-16）而 reader `presentationSchema` 用 Zod max（码点）：UTF-16 检查更严，方向一致，非不一致缺陷。

## 9. 未验边界与父缺口（本报告不证明）

真实 `query.execute`/项目内只读与外联拒绝（SERVICE/FROM/更新/非 SELECT-ASK）、真实 Q-01/02/O-01 业务联验、真实分页 cursor 发行/过期/时限/取消/历史输入恢复、T01 preview/confirm/commit/CAS/保存恢复/撤销/过期、T08 真实模型草稿与工具闭环、ASK/真实 RDF term/列元数据及适用局部关系图、App/preload 实际挂载与生产 CSP、浏览器交互/下载/原生提示、T10 跨设备、Windows 11 x64/macOS 15 arm64、真人验收、全部父 P0/跨模块矩阵与发布门；push/PR/实际 CI/合并/远端核验。本轮无共享 main/preload/CSP/打包/依赖改动，按本轮输入未运行 e2e/native/HMR/打包验证（如有对应风险应由总控协调）。SSR/合成 transport/RDFLib 互操作/隔离组件 DOM 均不冒充真实 IPC/Store/App/平台验收。

## 10. 审前/审后冻结一致性与写面

审前审后两次核验：HEAD `f2102f07…`、`git status` 仅 ` M AGENTS.md`（SHA `de15f6ce…` 未变）、两锁文件哈希未变、输入文件哈希未变、42 项产品 blob 无漂移。本方写入仅限：本报告、`test-results/t04-review-runtime/zcode/`（raw/metadata/counterexamples/history/t09-provenance/owner-raw 解包与首失败记录）、本树 `test-results/t04-p3-repair/browser/review-zcode/`（唯一命名探针产物）。未 stage/commit/push、未改产品/测试/fixture/依赖/配置/验收/另一方材料、未启动 GUI/Electron/HMR、未连接用户 profile（组件探针为独立 headless Chrome、offline、全请求 abort，实测 0 外联请求）。

## 11. 结论

对登记的同版完整 T04-S1（base `5f910b52…` → product `5070004e…` 全部 42 项固定输入及其有界验收）：**通过**。依据：输入与产品身份逐字节核验一致（42/42、diff、T09 17/17、历史 71 成员、owner 25 raw）；四项 P3 修复经源码审查＋定向测试＋真实组件 DOM＋本方 141 组独立反例确认正确；历史 10 项 closed 在 507 保持、1 项 partial 按原样记录且本轮条件下已全部可核；本方五组验证真实 exit 0（89/115/14/719+1167/5），其中 SSR 与组件结果与 owner 归档逐字节相同构成独立复现；架构不变量（本地优先、渲染端隔离、确定性/Agent 解耦、无第二可变源、错误受限、staleReason 只读）无冲突。本结论仅为本方对 S1 的独立判断：不代判另一方，不授权 push/PR/merge，不改变父 T04/产品未完成状态，任务终态以操作者随后从官方状态读回的同 SID＋原 turn 终态为准。
