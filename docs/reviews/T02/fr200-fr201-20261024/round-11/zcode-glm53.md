# T02 fresh R11 全新整候选独立工程审查报告（ZCode GLM-5.3）

本方：ZCode GLM-5.3／最高推理／完全访问。模型路由实况：本会话实际由 `account:bigmodel-individual-coding-plan/GLM-5.3` 承载；Start Plan 实查当前仅 Flash，未采购新套餐，按既有 BigModel 个人路由执行准确 GLM-5.3（与附件首部声明一致）。

唯一本方报告：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261027_t02_d1aca_fresh_r11_075/zcode/report.md`（本文件）。本轮不复跑验证、不修改 worktree 任何内容、不读另一作者本轮 R11 材料。

---

## 0. 输入与身份回执（先核后审，全部通过）

**附件两层边界**（实测，非引用）：

| 层 | 声明 | 实测 |
| --- | --- | --- |
| 外层完整输入 | 33355 B、246 个 LF、SHA256 `d8824ab8aa084c5be127a64a369d7bb038e77e4f0c8641232ec966e005c6a481`、UI 含末空行 247 行 | `wc -c`=33355；`tr -cd '\n' | wc -c`=246；`shasum -a 256` 全同；行 246 为 `<!-- R11 COMPLETE INPUT EOF: d1aca3e3 / 160 original checklist items -->`、行 247 末空行 |
| 内嵌原 160 项 | 11255 B、SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`、末字节非 LF（其后两个分隔 LF 不属原件） | 取附件行 75–244 去除 sed 尾随 LF 后 `wc -c`=11255、SHA256 全同；引文行 `grep -c '^>'`=160（行 84–230 共 147 项 + 行 232–244 共 13 项），为 SHA256 未写作 SHA1 |

**完整输入同原件**：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261027_t02_d1aca_fresh_r11_075/zcode-complete-input.md` 实测 33355 B、SHA256 与粘贴附件逐字节相同（同 `d8824ab8…`）。

**Git 身份**（cwd 实测）：`pwd`=`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes`；branch=`feature/weekly-t02-fr200-fr201`；HEAD=`d1aca3e34ec4d00095c10a14a413efb552d3776a`；tree=`389848f84fe60325bcdcd1b7827a7ee6e039a0e1`；唯一 parent=`2d6bc23fdc4f13afcceb7b79c8059ee3c74abbe8`；base→HEAD `rev-list --count`=43、`diff --name-only`=125、`ls-tree -r` tracked=1403。全部与声明一致，按约继续审查。

**工作树脏项**（git status 实测）：仅 `M AGENTS.md`（原保护 overlay）与 untracked `docs/reviews/T02/fr200-fr201-20261024/round-01/`、`round-02/`、`round-03/`，与输入声明一致，均不属候选内容。远端核对：本轮尝试一次只读 `git ls-remote` 因本机网络 SSL 失败未取得新读数；远端事实（remote feature=cfcc876e、develop=583、PR16 open 未合并、CI43 为唯一 cfcc CI）以 O072 官方回执为据，本轮无 push/PR 写动作。

**旧路径失效说明**：AGENTS.md 指向的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 已不在该路径；真实同主题原件在 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`（另有一份拷贝在 `docs/reviews/I03/inputs/`），本轮按 I01 inputs 原件全文核对（207 行）。

## 1. 审查范围与阅读披露

范围：base `583c05c7` → head `d1aca3e3` 全累计候选（43 提交/125 路径/1403 tracked 源叶），含必要依赖闭包、新增测试与契约正文；冻结 SHA 读源码。分层披露如下，不以摘要冒全文。

**本人亲读全文**：当前工作树 AGENTS.md（含保护 overlay）；m0 更新计划（I01 inputs 原件）；PRD FR-200/FR-201 条款全文与附录 C、D（D.1/D.2 全文）；ADR-0001、ADR-0002（含 Round2/3 澄清）、ADR-0003；docs/m0-checklist.md；docs/reviews/T02/status.md；round-10/disposition.md 全文 392 行；`tests/e2e/csp-lifecycle.spec.ts` 全文 377 行；`tests/e2e/t02-fr200-fr201.spec.ts` 全文 2175 行；`tests/e2e/ui-observation.ts` 全文 196 行；`packages/engine/src/ontolearn_engine/project/mainline.py` 全文 1207 行；`apps/desktop/src/renderer/src/ontology/OwnershipConflictDetailView.ts`、`mainline-ownership.ts` 全文；O072 `DIAGNOSIS-AND-BOUNDARIES.md` 全文；O074 `COMPLETION.json`、`BUILD-REBUILD-MAPPING.json`、`C1-INDEPENDENT-BOUNDARY-REVIEW.json`、`FR-INDEPENDENT-BOUNDARY-REVIEW.json` 全文。

**本人差异级全文（base→head 完整 diff 亲读）**：主进程 `desktop-ipc.ts`/`engine.ts`/`project-mainline-service.ts`、`preload/index.ts`；renderer `OntologyPage.tsx`/`OntologyMainlinePage.tsx`/`mainline-api.ts`/`mainline-facts.ts`/`mainline-session.ts`；contracts `src/index.ts`、`src/v2.ts`、`python/contract_v2.py`；engine `storage.py`、`rdf_snapshot.py`、`job_store.py`、`project_host.py`、`coordinator.py`、`domain_changesets.py`、`query_presentation.py`；`.github/workflows/ci.yml`；`tests/e2e/mainline-consumer-first-ack-loss.spec.ts`；`tests/e2e/native-driver.ts`（关键段逐行＋全文定位）。2d6→d1aca3e3（仅 2 文件 419+/132-）与 cfcc→2d6（仅 m0-checklist 删 1 行）逐字核对。

**本人定点亲读**：`packages/engine/tests/test_storage.py` L185–230（九行参数化正反断言在位）；`test_mainline_postwrite_admission.py` L200–240（replay 与后续合法 Read 区分）；`pyproject.toml` 排除段；`packages/engine/pyproject.toml`；`licenses/NOTICE` 头部；`tests/fixtures/t02-manual-fact-id.json` 头部（scope=generated、来源哈希）；`packages/contracts/v2/schema.json` ownership 段（manifest minItems/totalBytes≥2）；`scripts/run-engine-tests.py` 结算段。

**工具摘要＋抽查（未逐条全读，如实披露）**：O074 `NATIVE24-QUALIFICATION-02.json`（145KB，434 checks——读结构、COMPLETION 摘要计数与关键类别，未逐条重算）、`INDEPENDENT-COMMIT-BINDING.json`（52KB，487 checks 同上）；O072 `COMPLETION.json`（31KB，字段级提取）；round-10 `version-map.json`/`artifact-manifest.json`（经 disposition 交叉索引定位，未通读 3397/1070 行）；6 个新增 engine 测试中其余 5 个（`test_mainline_dispatch/language_input_rejection/manual_input_rejection/postwrite_rows_budget/postwrite_text_budget/read_work_budget`）与 12 个 unit 测试为文件级＋断言抽样（R04–R10 已历轮全文双审，本轮聚焦增量与在位性）；PRD 其余章节、附录 E/G、`contracts/v2/fixtures.json` 逐条目、4 个二进制 wheel 内容未读。

**未读/不读**：另一作者本轮 R11 目录、报告、意见、verdict（依职责不读）；产品 GUI/CI/测试一律未运行（O064/O069/O074/O072 等运行事实全部标注为既有原件证据，不冒本人运行）。

## 2. Top 真实最重要风险（本人列出 9 项；无第 10 项达到同级）

| # | stableID（承接） | 严重性 | 触发/现状 | 代码或原件定位 | 影响 | 最小建议 | push 前源码阻断 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | R10-01（承 Z08-01/Z08-06/F02/R06 D1/R05 Z P1/R05 MM01/R06 MM01/Z F1/Z09-01/F-R09-01） | 高（合并门禁） | 任何 push 后 CI/merge | CI43 run40406339836 overall failure（O072 原件）；d1aca3e3 未 push、无新 CI | 完整三平台 CI 从未在本候选通过；2d6 已修 Quality format 一字节但 CI 未重跑 | ROOT 精确票后 push 重跑；按原 15/20 分钟、逐 node/原有据 skip/自然 0 标准接收 | 否（门禁非源码缺陷） |
| 2 | R10-02（承 Z08-02/Z09-02/F-R09-02/03） | 高（未证根因 HOLD） | Windows C1 native 阶段 | CI43 C1 13086ms：readiness1、bootstrapComplete true 后 child close 1/null；ZIP 无 native.json（O072 `INDEPENDENT-WINDOWS-C1-DIAGNOSIS.json`） | Windows C1 异步失败根因 UNKNOWN；d1aca3e3 新增失败留证 catch 未在真实 Windows 触发（O074 limits 明示），不构成修复 | 未来授权 Windows CI 复验时依赖新增 capture 附件定因；不为凑绿改预算/断言 | 否（HOLD） |
| 3 | Z09-03/Z08-02 尾部（Windows FR201 预算） | 高（平台性能边界） | Windows FR201 整例 | CI43 180002ms：第 21 笔完成，Diff 可见等待起 179525.790ms、名义余量 474.210ms，未进第 22 笔（O072 timing 表） | 累计预算在 Windows 上近满；新计时（d1aca3e3）只补测量能力，未修也未证可修 | 下一授权 Windows 运行读取新 5×19 timing 附件定位大类耗时；不删断言/不加预算 | 否（CI 条件可阻断 merge） |
| 4 | Z08-06 分层（本地闭合资格维持） | 中（平台证据边界） | 本轮两文件增量 | O074：fullcheck/native24 实际在 2d6+exact2WIP 运行（内容逐字同 d1aca3e3）；C1 catch 仅 14 纯 mock 场景、FR 计时仅 12 VM 边界场景，均非 Windows 真实运行 | d1aca3e3 的观测修补在真实平台失败路径上的行为未验 | 维持 O074 limits 声明；随 #1 的 CI 一并取样 | 否 |
| 5 | R10-08（承 Z09-09 部分） | 中（维护耦合） | Playwright/Electron 升级或 DOM 形态变化 | `ui-observation.ts:57-81`（native BUTTON/fieldset/aria 判据，fail-closed）、`native-driver.ts`（450×100ms 就绪轮询、Electron44.9 resolver 映射） | 升级后可能误报超时或需重证；判据仅支持当前 light-DOM 形态 | 升级/形态演进窗口重证判据；CI 归因优先定因不扩轮询 | 否 |
| 6 | R10-07 | 中（测试质量） | 字段错绑/漂移时 | `t02-fr200-fr201.spec.ts` L316（`parametersHash: job.parametersHash`）、L329（`planHash: marker.planHash`）自指；ack-loss 同源快照自比较 | 回环恒真断言可能掩盖字段错绑 | 为 planHash/parametersHash 补独立 digest 期望或交叉来源值（原 T02 测试维护归口） | 否 |
| 7 | R10-03（承 Z09-05/MM R07-13） | 低（维护） | 契约类型整理时 | `packages/contracts/src/index.ts:893-894` `OwnershipDetailArgs` 第二变体 `startOrdinal:number; pageSize:number` 宽于 schema（0–511/1–64） | TS 类型不拦越界，仅运行时 zod 拦截，双源漂移风险 | 契约 owner 下次整理收敛为字面量区间类型 | 否 |
| 8 | R10-04（承 Z P6/R06 D5/R04 Z01/R05 MM08/F15＋F03 附带） | 低（未确认观察） | witness 并列/CI skip 对账 | `storage.py:1151`（GROUP BY…LIMIT 1）与 `:1168-1172`（…LIMIT 2）无 ORDER BY（本轮亲核在位）；`run-engine-tests.py:340-354` skip/xfailed/xpassed 不计失败 | 极端并列时"首个阻断行/前两条记录"不可复现；CI 汇总不因新增 skip 变红 | T01 触及 witness 选取时加确定性排序；CI 维护票评估 skip 逐项对账强化 | 否 |
| 9 | R10-05（承 Z09-04/F09/MM R07-12） | 低（供应链卫生） | T11 merge 后 | `vendor/rdflib/` 保留 fr201.1/fr201.2/fr201.3＋upstream 共 4 wheel（本轮 ls 核对）；`engine/pyproject.toml` 仅引用 fr201.3 | 仓库体积与制品审计面增大；PROVENANCE 三方哈希一致但冗余件在树 | T11 merge 后受控清理历史 wheel，保留 PROVENANCE 记录 | 否 |

说明：R10-T05（兜底分支字节数）、R10-T06（命名/门禁语义）、R10-T09（"无机器校验"）、R10-T10（renderer 更早拒绝缺陷）四项原强论断经 R10 处置撤回/收窄，本轮本人复核其替代口径后同意不列为风险：T05 兜底固定字段实测 212B＋stage 34B 预算（本轮读 `ui-observation.ts:179-190` 确认兜底分支不含 `observed`）；T06 诊断步失败即红与"非验收凭证"不矛盾；T09 `t02-manual-fact-id.test.ts` 存在真实 Python Store 交叉核验（fixture scope=generated、golden 绑定 digest）；T10 renderer 判定刻意严于引擎 `_check_slot` 属设计（`storage.py:1211-1228` 本人读 diff 确认 reason 分流）。T11/T12 维持 R10 处置（见 §4.6）。

## 3. 本轮增量审查（cfcc876e → 2d6bc23f → d1aca3e3）

**2d6bc23f（仅 1 文件 1 行）**：`docs/m0-checklist.md` 删 offset 12140 一 LF（13999→13998 B）。O073 回执绑定：Prettier 全文 M0、全局 `format:check`、`verify:sources` 均 0；其余 1402 源/modes、5 build、旧 manifest（O071/round-10 绑定 cfcc 历史身份）逐字不变。本人核对 `git diff cfcc..2d6` 仅此一行，无第二个源码 pin 错误。此提交修复 CI43 Quality 的 format 失败首因；CI 未重跑，不倒填为绿。

**d1aca3e3（仅 2 文件 419+/132-，无产品路径）**：

- `tests/e2e/csp-lifecycle.spec.ts` L278–341：仅包原 `runNativeRecovery` 失败 catch。本人全文亲读控制流：单次 `readFile(nativeOutput)` 得 Buffer；读失败区分 ENOENT（`not-found`）与其他（`failed`）；读到后区分 JSON 有效（进 `evidence.nativeRecovery`）/坏 JSON（`parse:'failed'` 但仍保原始字节）；原始字节以 `application/octet-stream` 附件一次附加、capture 状态独立 JSON 附件；诊断各环节 best-effort（含 `String(error)`、附件拒绝、`test.info()` 抛错的容错），最终 `throw error` 重抛原异常对象、走原 finally（原 90s、原 cleanup、I02_EVIDENCE 写出全部未动）。与 O074 C1 独立审（真实 AST 抽取＋transpile＋VM 14 场景全过、catch 区外逐字相等）结论一致，本人独立复核无异议。观察两点非缺陷事实：capture 中含本机临时目录路径（`path: nativeOutput`），属测试诊断附件而非产品跨边界错误参数，不违反受限参数约束；本机 Mac 成功路径从未触发该 catch，真实 Windows 失败附件仍无平台实证（O074 limits 声明，本人照实保留）。
- `tests/e2e/t02-fr200-fr201.spec.ts`：只包原 5 处 `expect.poll`（`observedPoll`，5 固定 phase × 19 数值字段；WeakMap 以 `test.info().annotations` 对象为槽，每 test 一个 `t02-poll-timing`；4096 B UTF-8 上限，超限降级为固定 `unavailable` 字段；三个原 finally 头部同步 `sealPollTiming()`，sealed 后迟到 callback 不改已封槽；`performance.now`/`Date`/publish 失效时降级为原 `expect.poll` 直通，不碰原 callback 返回值与异常）。gaps 仅测同一 poll 相邻 callback 间（注释与实现一致）。原业务断言链（完整 Diff、提交回执、marker/Job/freshRead、受控拒绝 43、原 ID 编辑、同 host、100ms/5s/180s 预算）未变；普通原断言计数 C1 39→39、FR 133→133。与 O074 FR 独立审（12 VM 边界场景全过、5 个 callback 归一化 AST SHA 与原相同、最坏 3305B≤4096）结论一致，本人独立复核无异议。
- 验证身份（既有原件，非本人运行）：O074 唯一一次 `uv run --offline --frozen npm run check` exit0/209.26s（TS1912、Python 3769=3719P+50 原 S+1 原 duplicate-ZIP warning、Ruff393、lint/format/type/build PASS），实际运行时为 2d6 HEAD＋exact2 WIP，提交后两 Git blob 与测试输入逐字相同；native24 一次自然 driver 0（21P+3 原 I04 S、57 事务 7/7/7/7/22/7、43 拒绝 42INVALID+1ownership、FR201 终 rev22 九 facts、2 原 ID 编辑、case7 单 commit/0 replay、retry0/flaky0；12 timing 副本双层 5×19、实际最大 2223B）；5 build 仅 main 606471B 中 [602382,602406) 24B 开发 CSP nonce 差，其余 4 build 逐字旧。

**结论**：本轮增量（cfcc→d1aca3e3）为归档文档、一字节格式修复与两测试文件的失败留证/测量能力，产品源码零改动；本人未在增量中发现 push 前源码阻断。

## 4. 历史意见逐项承接（保原 stableID／主题／owner／事件窗口）

口径：`已闭`＝既有有界事实已核且无需动作；`保留`＝事项仍开（门禁/HOLD/维护/观察）；`未知`＝无法确认；`不采`＝原强论断有反证不采纳。本轮增量（R10 后 delta）未触及任何产品源码路径，故绝大多数源码在位性事实未变；每项给本人本轮核对依据。归口/窗口未注明变化者维持 R10 处置原归口窗口，不扩大、不新增执行授权。

### 4.1 当前31

| stableID | 本人处置 | 本轮依据 | 原 owner/窗口（简） |
| --- | --- | --- | --- |
| Z08-01 | 保留（门禁，数值更新 d1aca3e3 未 push 无新 CI；本轮 ls-remote 网络失败未获新读数，远端以 O072 为据） | O072 push/PR 回执 | ROOT 精确 push/CI 票；merge 前 |
| Z08-02 | 保留 | O074 `engineNaturalCode:"UNKNOWN"`、CI43 后代无 JobHandle | Windows CI 证据接收；新工具另票 |
| Z08-03 | 保留 | ci.yml 相对 240 无变化（本轮 `git diff 67b7..d1aca -- .github` 为空）；制品回单未发生 | 未来制品回单/预算变化须新授权 |
| Z08-04 | 保留 | 旧 79F/CI40 首败无逐例栈；CI43 新增结构化首败配置但 Windows 仍 2F | 下次真实 CI 复发时定因 |
| Z08-05 | 保留（维护） | `rdf_snapshot.py:57` `lang=result.language.lower()` 本轮亲核在位；与 CI41 helper12 主题分离 | T01 测试维护者下次触及 |
| Z08-06 | 已闭（本地闭合资格维持）＋远端仍开 | O074 fullcheck/native24 同内容证据；远端 Windows/Quality 未验 | Windows/Quality 实际 CI |
| Z08-07 | 保留 | 方法错误码覆盖/裸 detail 窗口未至；本轮 delta 未触及 | 原 T01/T02 方法接线窗口 |
| Z08-08 | 保留（P2 供应链） | 4 wheel 在树本轮 ls 核对 | 发布/供应链 owner 另票 |
| Z08-09 | 保留（卫生观察） | ci.yml artifact `if: always()`＋engine-tests 纳入本轮 diff 亲核在位；去重未做 | 未来 CI 维护票 |
| Z08-10 | 保留（部分采纳维持） | `dependabot.yml` 在树本轮 ls 核对；执行未核；不与 Ruff exclude 混题 | 发布/vendor owner 窗口 |
| Z08-11 | 保留（HOLD 群） | R10 后 delta 仅 docs＋2 测试文件，无 HOLD 面被触及 | 各原 owner 对应验收前 |
| Z08-TOP10-OLD79F | 保留（未知保原） | 无新证据 | ROOT 登记及复发证据 |
| F01 | 已闭（流程，本轮履行） | 本报告 §1 覆盖披露 | T02 作者完成本票；ROOT push 前接收 |
| F02 | 保留（门禁，数值 d1aca3e3） | 同 Z08-01 | ROOT 精确票后、merge 前 |
| F03 | 保留＋限定 | `run-engine-tests.py:331-354` 结算 fail-closed 语义本轮亲核在位；"完整 sys.path 等价"不声称 | ROOT CI 控制层维护票 |
| F04 | 维持撤回（不复活） | O067 缺陷已修复式承接；本轮不造失败样本 | 本票内闭合 |
| F05 | 保留（重新变开：R11 候选 d1aca3e3/2d6/cfcc 尚未登记状态段——status.md/m0-checklist 末段停在 67b7/R10，本人本轮亲核） | status.md 末段实测 | ROOT 指定文档 owner；状态追加＋归档票 |
| F06 | 保留 | SHARDS/env 传递在 CI diff 亲核；13 身份字段≠sys.path | 原 T02 归口首个 CI 维护票 |
| F07 | 保留 | 规则不变：无 head/tree 绑定产出不接收 | ROOT 证据控制层维护票 |
| F08 | 保留并正面复核 | `mainline-session.ts` requireCurrent 链与 ownershipDetail 异步 fence 本轮 diff 全读在位 | 原 T02 前端归口；UX/异步预览维护窗口 |
| F09 | 保留 | 4 wheel 不私自删（同 Z08-08） | T11 merge 后受控维护 |
| F10 | 保留 | 根 pyproject `per-file-ignores`（行27）与 format `exclude`（行34-39，round-NN 两作者件）本轮亲核两覆盖面不等 | 下次含 Python 围栏归档前核 |
| F11 | 已闭（收窄维持） | fixture scope=generated＋真实 Python 复核代码在位（本轮读 fixture 头与 R10-T09 处置） | 原 MM 作者票内闭合 |
| F12 | 保留 | ci.yml 无延时/重试/隐藏取消（diff 亲核） | ROOT CI 结算/控制层维护票 |
| F13 | 保留 | 无未实测提速量化声明面 | PR16 说明/CI 结算窗口 |
| F14 | 保留（→维护边界） | ownership-detail 契约双端 matcher 本轮 diff 亲读；新观察：TS/Python `matchesOwnershipDetail` 对"空段页"谓词不对称（TS 允许 start==end==count、Python 要求 start<end），但 schema `segments minItems:1`＋引擎 `start>=segmentCount→INVALID_REQUEST` 双前置使其不可达——记为契约维护注释点，非缺陷 | 原 T02 契约归口首个维护票 |
| F15 | 保留（未确认观察） | `storage.py:1151/:1168-1172` 无 ORDER BY 本轮亲核在位 | 原归口 witness 选取维护窗口 |
| F16 | 保留（容量维持） | `mainline.py:41-46` READ_LIMITS/HELD_BYTES/HELD_OBJECTS/READ_WORK/MAX_REPLIES 与 base 逐值相同（本轮 `git show base` 对比亲核） | 原 T02 契约归口 |
| F17 | 保留（语义等价无新动作） | 无变化 | 原 T02 前端归口 |
| F18 | 保留 | NOTICE/PROVENANCE 透明披露在位（本轮 head 核对） | T11+T02 依赖归口 |
| F19 | 保留 | 旧 raw/标题保留；round-NN format 排除不触旧件 | ROOT 唯一归档归口 |

### 4.2 权威78

| stableID | 本人处置 | 本轮依据（简） |
| --- | --- | --- |
| Z F1 | 保留（门禁，数值 d1aca3e3） | 同 Z08-01 |
| Z F2 | 保留 | R10 归档外无新 raw 入树（delta 亲核） |
| Z F3 | 保留 | 脚本 JSON 写出显式 UTF-8；历史 20 默认窄结论维持 |
| Z F4 | 已闭（口径）维持 | 双分母修订；无 dumps 变化 |
| Z F5 | 保留 | `t01-mainline-contract.test.ts:656` 裸 `python` execFileSync 本轮 grep 亲核在位（另一处 real-runtime 同） |
| Z F6 | 保留（逐项集合） | definitions wire、裸 ownership、standalone EOF、缺码、无序、4299/4300 各行独立未闭 |
| Z F7 | 保留（发布 HOLD 群） | delta 未触及 |
| Z F8 | 保留（部分） | `rdf_snapshot.py` TermInputError 分流本轮 diff 亲读在位；裸族两出口仍 OWNERSHIP_CONFLICT |
| Z F9 | 已闭（限受审面） | `_OwnershipProof` 授权链（mainline.py:477-517/677-705 本轮全文亲读） |
| Z F10 | 已闭（既有证据接收） | O074 native24 57 事务/43 拒绝；不外推全 GUI |
| MM R07-01 | 已闭 | 排除面在；覆盖面归 F10 |
| MM R07-02 | 保留 | 未发生新 raw |
| MM R07-03 | 保留 | 两覆盖面不等（同 F10） |
| MM R07-04 | 保留（重新变开） | 同 F05：R11 候选未登记 |
| MM R07-05 | 保留 | AGENTS.md 未提交 overlay 本轮 git status 亲核在位 |
| MM R07-06 | 已闭（口径）维持 | — |
| MM R07-07 | 已闭（口径）维持 | 载荷变化时重核 |
| MM R07-08 | 已闭（口径）维持 | 28 笔分层不扩 |
| MM R07-09 | 已闭（口径）维持 | 本轮无新构建（O074 为内容映射非新包制造） |
| MM R07-10 | 已闭（口径）维持 | d1aca3e3 无 .py 变化 |
| MM R07-11 | 保留（观察） | `mainline-facts.ts` edit 保原 ID/重叠拒绝扩展本轮 diff 亲读在位 |
| MM R07-12 | 保留（HOLD） | PROVENANCE/patch/upstream 三方哈希在位 |
| MM R07-13 | 保留 | `index.ts:893-894` 本轮亲核在位（→R10-03） |
| R06 Z P1 | 保留（门禁） | 同 Z F1 |
| R06 Z P2 | 保留 | 诊断步与验收口径分离维持；CI41 根因另归（R10-02） |
| R06 Z P3 | 保留 | `domain_changesets.py:157` 一带预览路径未分类 ValueError 本轮 diff 上下文亲核仍在（本候选新增的 TermInputError 分流仅覆盖调用方直接词法） |
| R06 Z P4 | 部分已闭维持 | typed witness（含 SingleDeclarationConflict）本轮 storage.py diff 亲读落地；裸族未全闭 |
| R06 Z P5 | 保留 | 错误码集合差；16 码可达性未证 |
| R06 Z P6 | 保留（未确认观察） | 同 F15 |
| R06 Z P7 | 已闭（沿既有决定） | canonical 政策不变；Q6 已决 |
| R06 Z P8 | 保留（逐项承接） | 各行独立 |
| R06 D1 | 保留（门禁） | R10 后无新源码缺陷；CI 待 |
| R06 D2 | 保留（重新变开） | 同 F05 |
| R06 D3 | 保留 | 同 R06 Z P3 |
| R06 D4 | 部分已闭维持 | 两出口终码 OWNERSHIP_CONFLICT＋typed ManualOwnershipConflict 落地；裸族定位未全闭 |
| R06 D5 | 保留 | 同 F15 |
| R06 D6 | 保留 | patch 类型化守卫在位；`n[-1]` 残余未证不可达（patch 未逐行重读，沿 R10 亲读记录） |
| R06 D7 | 保留 | 同 R06 Z P5 |
| R06 D8 | 保留 | 同 Z F5 |
| R06 D9 | 已闭（口径）维持 | d1aca3e3 无 Python 变化 |
| R06 D10 | 保留 | 四具名下游（编辑→推导/保存查询/SHACL/报告）GUI 未逐类验；公共九行正反例本轮 test_storage L190-223 亲核在位 |
| R06 D11 | 保留 | 4301 断言在（spec:1010 一带）；4299/4300 消费断言缺维持 |
| R06 D12 | 保留（有界）维持 | 六 keyword AST/本地运行/旧包身份不外推 |
| R04 Z01 | 保留（未确认观察） | 同 F15 |
| R04 Z02 | 撤回维持＋边界保留 | 误因果不复活；262,144/16MiB 预算边界在 |
| R04 Z03 | 保留 | 同 R06 Z P3 |
| R04 Z04 | 保留（部分） | 同 R06 Z P4 |
| R04 Z05 | 保留 | 同 R06 Z P5 |
| R04 Z06 | 已闭 | canonical :464 政策在位 |
| R04 Z07 | 已闭 | 规模信息接收 |
| R04 M01 | 已闭（历史演进） | 状态源另见 F05 |
| R04 M02 | 已闭（维持） | PROVENANCE 在树；fr201.1/2 保留见 F09 |
| R04 M03 | 保留 | 同 R06 D11 |
| R04 M04 | 保留 | standalone EOF 残余未证 UI 可达 |
| R04 M05 | 保留 | 同 R06 Z P3 |
| R04 M06 | 已闭（维持分层） | 双端 ID 校验/原 ID edit 在位；不外推全产品安全认证 |
| R04 M07 | 保留（维护窗口） | 未证冲突不缩导出面 |
| R05 Z P1 | 保留（门禁） | 同 Z F1 |
| R05 Z P2 | 已闭（事实）维持 | 934 packaged recovery 历史证据不迁移 |
| R05 Z P3 | 保留 | 同 R06 Z P3 |
| R05 Z P4 | 保留（部分） | 同 R06 Z P4 |
| R05 Z P5 | 保留 | 同 R06 Z P5 |
| R05 Z P6 | 已闭（口径）维持 | canonical 不变 |
| R05 Z P7 | 保留（信息级半面） | 诊断选项面已闭；"文件增长"信息级面维持（与 #138 互证） |
| R05 Z P8 | 保留（重新变开） | 同 F05 |
| R05 MM01 | 保留（门禁） | 旧 79 全因未知；新 CI 后合并前 |
| R05 MM02 | 已闭（事实）维持 | — |
| R05 MM03 | 保留（门禁） | 本 head 未打包（O074 构建副本非新包制造） |
| R05 MM04 | 保留（重新变开） | 同 F05 |
| R05 MM05 | 保留 | 同 R06 Z P5 |
| R05 MM06 | 保留 | 同 R06 Z P3 |
| R05 MM07 | 保留（部分） | typed witness 落地；裸族延期 |
| R05 MM08 | 保留（未确认观察） | 同 F15 |
| R05 MM09 | 已闭（维持） | wheel/payload/解压量分层；冗余件见 F09 |
| R05 MM10 | 已闭 | overlay 非候选缺陷在位 |
| R05 MM11 | 已闭（信息） | locator 仅 id/owner/sourceRow/slot（本轮 storage.py locator 亲读一致；不含 object） |
| R05 MM12 | 保留 | 同 Z F5 |
| R05 MM13 | 已闭（信息）维持 | — |

### 4.3 R09新增19＋OBS（20 项）

| stableID | 本人处置 | 本轮依据（简） |
| --- | --- | --- |
| Z09-01 | 保留（门禁，数值 d1aca3e3） | 无新 CI |
| Z09-02 | 保留（→R10-02） | CI43 C1 新事实已并入；根因仍 UNPROVEN |
| Z09-03 | 保留 | engine/Windows 后代退出 UNKNOWN（O072/O074 均明示） |
| Z09-04 | 保留 | 4 wheel 在树 |
| Z09-05 | 保留 | index.ts:893-894 在位（→R10-03） |
| Z09-06 | 保留（不升级缺陷） | 同 F15 |
| Z09-07 | 保留 | 4299/4300 消费断言缺维持 |
| Z09-08 | 保留 | artifact always＋engine-tests 入 artifact 在位；去重留票 |
| Z09-09 | 保留 | native-driver CDP 就绪探测耦合（本轮关键 diff 亲核） |
| Z09-10 | 保留 | 裸 ownership HOLD 家族未被 delta 触及 |
| F-R09-01 | 保留（maintain） | current d1aca real CI pending；累计本地执行证据已有（O074） |
| F-R09-02 | 保留（maintain） | UNPROVEN=HOLD 与主张纪律，非新证因门禁 |
| F-R09-03 | 维持撤回 | readiness-helper 断言已撤回；根因 HOLD 保留 |
| F-R09-04 | 保留（maintain） | 145.101s 非轮询耗时为有界观察（CI43 timing 表并入） |
| F-R09-05 | 保留（maintain） | failure-only annotation；成功 CI 无需失败样本 |
| F-R09-06 | 保留（maintain） | 证据绑定接收限制；脚本未再改 |
| F-R09-07 | 保留（maintain） | sys.path 等价限制不解除 |
| F-R09-08 | 保留（重新变开） | 同 F05：R11 候选待登记 |
| F-R09-09 | 保留（maintain） | 完整 CI/制品接收纪律；ci.yml 其后未改（67b7..d1aca 为空亲核） |
| OBS-R09-10 | 保留（maintain，P3） | 整数上限环境前提记录；4299/4300 不因此关闭 |

### 4.4 额外13（R06 MM01–MM13，单列不并入 78）

| stableID | 本人处置 | 本轮依据（简） |
| --- | --- | --- |
| R06 MM01 | 保留（门禁） | 同 Z F1 |
| R06 MM02 | 已闭（事实）维持 | — |
| R06 MM03 | 保留（门禁） | 未打包 |
| R06 MM04 | 保留（重新变开） | 同 F05 |
| R06 MM05 | 保留（撤回加注维持） | ID/状态仍开；"裸家族"加注无原件依据已撤回，本轮不采加注 |
| R06 MM06 | 保留 | definitions wire（同 R06 Z P3） |
| R06 MM07 | 保留（部分） | typed/裸家族分开 |
| R06 MM08 | 保留（未确认观察） | 同 F15 |
| R06 MM09 | 已闭（维持） | 分层维持；冗余件 →R10-T07 归口 |
| R06 MM10 | 已闭 | overlay 在位 |
| R06 MM11 | 已闭（信息） | locator 字段面亲核 |
| R06 MM12 | 保留 | PATH python 在位 |
| R06 MM13 | 已闭（信息）维持 | — |

### 4.5 R10 ZTop9（R10-10 为序号笔误不存在；§31 postwrite L211–213=replay 与 L216–218=后续合法 Read 已区分）

| ID | 本人处置 | 本轮依据（简） |
| --- | --- | --- |
| R10-01 | 部分采纳维持（门禁） | §2 #1 |
| R10-02 | 部分采纳维持（HOLD） | §2 #2 |
| R10-03 | 延期维持 | index.ts:893-894 亲核在位 |
| R10-04 | 延期维持（两建议分别归口） | :1151/:1168 无 ORDER BY＋run-engine-tests 结算亲核在位 |
| R10-05 | 延期维持 | 4 wheel 亲核在位 |
| R10-06 | 部分采纳维持（公式边界） | 源窄盲区＋独立证据并存 |
| R10-07 | 延期维持 | t02:316/329 自指断言本轮亲读在位 |
| R10-08 | 延期维持 | ui-observation 判据＋native-driver 轮询亲核在位 |
| R10-09 | 不采纳原强论断维持 | 两份 versioned M0 输入副本在树（iterations/I01/inputs＋reviews/I03/inputs 本轮 ls 亲核）；仅旧 AGENTS 引用路径失效（§0 已说明） |

### 4.6 MM Top10＋T11/T12

| ID | 本人处置 | 本轮依据（简） |
| --- | --- | --- |
| R10-T01 | 保留（合并门禁） | 同 Z F1 |
| R10-T02 | 保留 | CI 证据接收标准 |
| R10-T03 | 保留（覆盖面限制） | — |
| R10-T04 | 保留（覆盖面限制） | — |
| R10-T05 | 采纳本人撤回/收窄维持 | 兜底 212B＋stage 34B 静态预算；未证当前可达（本轮读 ui-observation.ts:179-190 确认兜底字段集） |
| R10-T06 | 不采纳命名矛盾推论维持 | 诊断失败即红正确；不加 continue-on-error |
| R10-T07 | 保留 | 发布/供应链 owner |
| R10-T08 | 保留 | CI 维护票 |
| R10-T09 | 部分采纳（收窄） | t02-manual-fact-id 真实 Python 交叉核验在位；残余为未穷尽 Unicode 空间 |
| R10-T10 | 不采纳缺陷强推论维持 | renderer 严于 `_check_slot` 属设计（storage.py:1211-1228 亲读） |
| R10-T11 | 部分采纳（只采来源 hash≠head 事实） | fixture 头部 scope=generated＋sourceStorageSha256 本轮亲核；不强制刷新来源针 |
| R10-T12 | 不采"仅3/9"与补五类门禁维持 | test_storage.py L190-223 九规则参数化正反断言本轮亲读在位 |

## 5. 原 160 项逐项判定（1–160，复合判定一档一次，总计 160）

判定口径：适用＝该关注点在本产品形态下真实存在且当前实现已覆盖其 P0 面；部分适用＝存在且有部分实现/或仅以设计边界替代；不适用＝产品形态（本地单用户 Electron 桌面、无账户/网络服务/计费/模型调用，ADR-0001 与 AGENTS 架构不变量）使其不成立；无法确认＝组织/法律/人员事实代码不可认证。**适用性计数不是产品通过数**。通用依据缩写：〔本地〕＝本地优先单用户桌面（无登录/多租户/云）；〔无资金〕＝无支付/订阅/金额；〔S3前〕＝无模型调用与外发；〔Store〕＝SQLite 事务源真相（ADR-0002）；〔契约〕＝packages/contracts 双端 zod strict；〔e2e〕＝t02 spec 真实表单流（既有 O074 证据）。

| # | 判定 | 当前依据 |
| --- | --- | --- |
| 1 | 适用 | SQLite 格式 v2 表结构设计先行（projects/definitions/facts/commits/snapshots/results…分层，storage.py DDL＋ADR-0002 表责任），非逐表即兴 |
| 2 | 不适用 | 〔本地〕无登录/邮箱；preload 无 auth 方法 |
| 3 | 不适用 | 同上，无密码重置链 |
| 4 | 不适用 | 无 MFA 面 |
| 5 | 不适用 | 无会话账户体系；引擎 stdio 会话有握手/预算/65,536 请求上限属传输层（见 #69/#110） |
| 6 | 不适用 | 无企业客户/SSO |
| 7 | 不适用 | 同上 |
| 8 | 不适用 | 同上（单用户本地无 IT offboarding 面） |
| 9 | 部分适用 | 无用户角色体系；存在进程/方法级授权边界（engine.ts 方法白名单＋projectId 校验、MainlineHost.authorize、_OwnershipProof、preload 业务命名方法），非 RBAC |
| 10 | 部分适用 | 无跨用户 IDOR；跨项目防护在位（deniedOrdinary、proof.check(selected)、coordinator 项目归属/通知路由校验） |
| 11 | 不适用 | 〔本地〕无租户 |
| 12 | 不适用 | 无客服代登 |
| 13 | 不适用 | 无登录端点 |
| 14 | 不适用 | 同上 |
| 15 | 适用 | v0→v1→v2 事务迁移、失败回滚 DDL/版本/数据、重开重试、未来格式拒绝打开（ADR-0002 迁移段＋迁移测试 424P+44 条件 skip 原件） |
| 16 | 部分适用 | 迁移取事务写锁后重读格式版本防双 opener；SQLite 本地单写者无"2pm 锁主表"负载场景 |
| 17 | 部分适用 | 容量以预算准入硬界（READ_LIMITS 4096 rows/1.5MiB、material_profile 全表聚合预付）拒收而非索引优化路径；索引集合未逐项核对 |
| 18 | 不适用 | 本地单连接 SQLite（BEGIN IMMEDIATE），无连接池需求 |
| 19 | 部分适用 | `Store.backup(newPath)` 在线备份 API 已实现（ADR-0002）；无夜间自动备份调度 |
| 20 | 部分适用 | 迁移故障注入＋重开恢复有测试；"从未恢复过的备份"风险由 backup API＋打开路径覆盖，未做备份演练流程 |
| 21 | 不适用 | 版本化快照/不可变历史提供逐提交恢复语义；无全库时间点恢复需求面 |
| 22 | 适用 | 受管事实删除留墓碑（tombstone）保留初始 ID；历史/已提交轮次不可改写（SQL 不可变触发器） |
| 23 | 适用 | 引擎侧权威校验（contract_v2/validateBusiness3、Store 形状校验、preview 词法/IRI 拒绝），UI 校验仅为第一道 |
| 24 | 部分适用 | 无提醒调度；xsd:date/dateTime 字面量按原文保留不重排（e2e 断言），时间戳 ISO/单调双轨 |
| 25 | 适用 | 中文/英文标识符、撇号类引号词法受控（unterminated-quote 等用例保留原词素拒绝，无静默修复） |
| 26 | 部分适用 | 多语言字面量 zh/en/@lang、UTF-8 字节级golden、全角斜杠拒绝用例在位；RTL 文本专项未测 |
| 27 | 不适用 | 〔无资金〕无金额字段 |
| 28 | 不适用 | 同上 |
| 29 | 部分适用 | 多项目 projects 表＋独立命名空间（urn:t02:*）、user_version 格式版本化；"第二个客户改需求"场景属产品演进未验 |
| 30 | 适用 | 同 operation/job/计划重试返回原 marker 不重复写入（ADR-0002；e2e replay 断言＋postwrite 测试） |
| 31 | 适用 | FACT_ALREADY_EXISTS 拒绝；提交期 pending/phase 状态防重复提交；43 受控拒绝含重复身份 |
| 32 | 适用 | catalog/diff/ownership-detail/rows/text 固定顺序游标分页；游标绑定项目/结果版本拒绝失配（CURSOR_MISMATCH/EXPIRED） |
| 33 | 不适用 | FR-203 Turtle 导出与 FR-1000 项目包导出未实现，无导出面可审 |
| 34 | 不适用 | CSV 映射未实现（mapping 计划仅存储形状） |
| 35 | 部分适用 | collect_cache 仅回收未 pin 可重建载荷；result_pins/历史/快照不可回收（ADR-0002）；用户级合同保留策略未到 |
| 36 | 适用 | 无密钥入源码（S3 前无模型凭据；.env/.sqlite 不提交规范在 AGENTS） |
| 37 | 不适用 | 无已发放密钥可轮换 |
| 38 | 适用 | uv.lock/npm 锁文件精确版本＋vendor wheel PROVENANCE 三方哈希＋固定 rdflib==7.6.0+ontolearn.fr201.3 |
| 39 | 部分适用 | dependabot.yml 在树（weekly root npm/actions）；执行与 CI 扫描结果未核 |
| 40 | 适用 | 边界 zod strict＋词法拒绝（IRI/语言标签/引号/超长整数）＋SQL 全参数化；错误参数白名单（detailRef 等）不含原值 |
| 41 | 部分适用 | SQLi＝参数化；XSS＝React 转义＋CSP（无 innerHTML 注入面，originalText 用 code 节点）；CSRF/外部 OWASP Web 面不适用（无 HTTP 服务） |
| 42 | 不适用 | 无用户文件上传入口；内置示例资源读取有 O_NOFOLLOW/fstat/FIFO/大小上限防护（mainline.py:316-342） |
| 43 | 不适用 | 无服务端 CORS 面；CSP connect-src 拦截外联（e2e fetchBlocked 断言） |
| 44 | 适用 | 生产 meta CSP＋开发 nonce 两变体同源 csp.ts；e2e 断言 violations enforce |
| 45 | 部分适用 | 本地 SQLite 明文＋用户目录隔离；传输层无网络；凭据加密（safeStorage）属 S3 未接，当前无凭据可加密 |
| 46 | 适用 | renderer 无 Node、preload 业务命名、Agent 未接入且架构禁自确认；引擎无凭据 |
| 47 | 部分适用 | operation_claims/commit_evidence 同事务记录 operation/job/origin（hostClientId/engineSessionId）；单用户无"who"身份维度；不记录敏感值 |
| 48 | 不适用 | 当前无外部攻击面（不开端口、无服务）；渗透测试属组织阶段决定 |
| 49 | 不适用 | 无企业买家问卷面 |
| 50 | 不适用 | 无对外服务/漏洞接收渠道（本地应用） |
| 51 | 不适用 | 无生产访问凭据可窃；本地数据暴露归 #45 设备加密范畴 |
| 52 | 不适用 | 组织合规阶段未到（无客户/审计方） |
| 53 | 不适用 | 无患者数据 |
| 54 | 不适用 | 同上 |
| 55 | 部分适用 | 提交/运行历史与 job 证据不可变可查（job.get/operation.get/历史运行）；"who viewed"审计在单用户形态不成立 |
| 56 | 不适用 | 无卡数据 |
| 57 | 不适用 | 本地单用户个人数据无服务端传播/删除请求面 |
| 58 | 不适用 | 无云存储区域 |
| 59 | 不适用 | 无多人访问权 |
| 60 | 部分适用 | 开发/生产 CSP 两变体同源生成；CI 三平台矩阵；无独立 staging 环境（本地产品无部署分层） |
| 61 | 部分适用 | CI workflow＋锁文件＋打包/验证脚本全部版本化；无云基础设施可 IaC |
| 62 | 部分适用 | CI 先 check 后 e2e/package/verify；当前完整 CI 未通过＝门禁未满足（§2 #1），管道存在且先测后达客户语义对本地包成立 |
| 63 | 部分适用 | ChangeSet 级撤销依据（前后快照）＋定义级 Undo/Undo-of-Undo 已验子集；应用部署级回滚不适用本地 |
| 64 | 不适用 | 本地桌面无维护窗口概念 |
| 65 | 不适用 | 无远程功能开关；能力按"已实现且验证才声明"原则（ADR-0003） |
| 66 | 不适用 | 本地无伸缩 |
| 67 | 不适用 | 无 web 资源分发 |
| 68 | 不适用 | 无自有域名/公网 TLS（本地应用） |
| 69 | 适用 | 常驻协调器＋ExecutionJob 按项目串行、队列上限、忙碌可取消/心跳（ADR-0003 真实探针） |
| 70 | 部分适用 | 协调器崩溃有限退避重启、不自动重放写；请求级取消有确认；无通用指数退避库（无外部 API） |
| 71 | 部分适用 | 失败 job 持久终态＋错误证据可查（dead-letter 语义内化于 JobStore）；无独立队列系统 |
| 72 | 不适用 | 无 cron/多服务器 |
| 73 | 适用 | invalidation-v2.json 九行机器规则＋依赖向量＋staleReason；仅改模型配置不失效领域结果（九行正反例测试在位） |
| 74 | 不适用 | 无邮件发送 |
| 75 | 不适用 | 同上 |
| 76 | 部分适用 | collect_cache 有界回收＋pin 豁免；快照 GC 未实现（保守全保留，ADR-0002 声明） |
| 77 | 不适用 | 无云成本/模型计费（S3 前）；FR-903 用量记录未接 |
| 78 | 部分适用 | 迁移/提交/崩溃故障注入＋backup API＋重启对账构成局部 DR 能力；正式书面 DR 计划与年度演练未立 |
| 79 | 不适用 | 本地单机无区域承诺 |
| 80 | 部分适用 | 引擎 JSONL 结构化协议＋固定错误码/受限参数；应用级可搜索日志体系未建（本地无 3am 运维场景） |
| 81 | 部分适用 | 错误按固定目录分类（ERROR_CATALOG）；无聚合上报系统（无遥测） |
| 82 | 不适用 | 无在线服务可监控 |
| 83 | 不适用 | 同上 |
| 84 | 不适用 | 同上 |
| 85 | 部分适用 | 跨进程 trace 事件＋operation/job/证据链＋测试级 timing 分解（CI43/O074）；无生产分布式 tracing |
| 86 | 不适用 | 无 on-call 值班场景（本地产品） |
| 87 | 部分适用 | ADR/AGENTS/状态文档/runbook 式交接在位；无值守 runbook（无值守） |
| 88 | 部分适用 | 审查轮次＋首败保留＋处置链构成复盘机制；正式 postmortem 流程未立 |
| 89 | 不适用 | 无对外服务状态页 |
| 90 | 适用 | vitest 1912＋pytest 3719（既有 O074 原件），断言完整预期集合/顺序风格（非仅计数） |
| 91 | 部分适用 | 无第三方外部 API；跨端公共正反例样例（TS/Python 同集）＋真实 RDFLib 引擎集成探针在位 |
| 92 | 部分适用 | 无收入流；核心业务流（FR200/201/case7/ack-loss/C1）真实 e2e 覆盖 |
| 93 | 部分适用 | 合成规模 1×/10× 测量记录（ADR-0002）；Q5 未定不设通过线，未做发布前负载测试 |
| 94 | 适用 | golden 由真实 Store 生成；e2e 用真实 GUI/表单；无生产数据复用 |
| 95 | 适用 | binding-regressions.json＋首败保留原则＋Undo/ownership 回归；修 41 不复活 12 的机制在轮次处置链 |
| 96 | 部分适用 | 跨 OS（Linux/macOS/Windows）CI 在跑；参考 8GB 设备与低端硬件 HOLD 保留未验；Windows FR201 预算近限暴露性能边界 |
| 97 | 部分适用 | aria-label/role 系统性使用（表单/区域/告警）、label 关联；正式 WCAG/屏幕阅读器全流程合规未验 |
| 98 | 不适用 | 〔无资金〕无订阅 |
| 99 | 不适用 | 同上 |
| 100 | 不适用 | 同上 |
| 101 | 不适用 | 同上 |
| 102 | 不适用 | 同上 |
| 103 | 不适用 | 同上 |
| 104 | 不适用 | 同上 |
| 105 | 不适用 | 同上 |
| 106 | 不适用 | 无 webhook |
| 107 | 不适用 | 同上 |
| 108 | 适用 | protocolVersion 2＋版本化 schema/registry 哈希＋ownershipDetailVersion/detailReadVersion 字段版本化 |
| 109 | 不适用 | 无外部 API 消费者密钥 |
| 110 | 适用 | 协议与预算限界真实（maxFrameBytes/页上限/HELD_BYTES/128MiB 簿/MAX_REPLIES/65,536 请求/会话） |
| 111 | 部分适用 | 依赖为本地固定 vendor wheel＋upstream 哈希＋patch 记录（变更影响可评估）；无外部服务格式变更风险 |
| 112 | 不适用 | 无 OAuth |
| 113 | 不适用 | 无客户集成沙箱；测试专用任务不登记产品能力（ADR-0003） |
| 114 | 不适用 | 〔S3前〕无模型调用即无提示注入输入面；FR-902/白名单工具/人工确认边界已在架构定型 |
| 115 | 不适用 | 同上（无外发 prompt） |
| 116 | 不适用 | 同上（无按客户模型开销） |
| 117 | 不适用 | 无模型答案质量面 |
| 118 | 不适用 | 无模型 provider 依赖 |
| 119 | 不适用 | 无已接模型可废弃 |
| 120 | 不适用 | 无 prompt/output 日志面（S3 前无调用） |
| 121 | 适用 | 显式确认按钮＋完整 Diff 展示＋Agent 不得自动确认修改（架构不变量）；case7/FR201 全链人确认 |
| 122 | 部分适用 | 本地加载零网络依赖（离线可用）；Windows 参考设备性能余量近限（§2 #3），"快"未全面证明 |
| 123 | 适用 | 空项目空状态（PRD 8.5 落地：初始 Read 空 definitions/facts）、reading/unavailable 状态、错误四段式（8.6 中文可操作文案） |
| 124 | 适用 | 错误码＋定位参数＋可操作中文文案（"请核对原记录，修改输入后重新预览；已输入内容保留"） |
| 125 | 适用 | 受控拒绝后输入值逐字段保留断言（retainUI/entered/objectInput toHaveValue） |
| 126 | 不适用 | 无邮件 |
| 127 | 不适用 | 无通知系统 |
| 128 | 适用 | 版本化撤销依据（同事务前后快照）＋定义级 GUI Undo/Undo-of-Undo/owned restart 已验子集；其余 Undo 家族 HOLD（不外推） |
| 129 | 部分适用 | 表单 label/键盘路径/焦点可达；屏幕阅读器端到端支持未验 |
| 130 | 部分适用 | 数据层多语言字面量按语言保留（zh/en/数字子标签）；UI 本身单语中文，无 i18n 框架 |
| 131 | 部分适用 | 单页应用无历史栈；崩溃/刷新恢复保留已提交状态并重连任务（C1/I04 已验） |
| 132 | 部分适用 | 模块分层＋strict 类型＋命名清晰；存在大文件（mainline.py 1207 行、t02 spec 2175 行、job_store.py）见 #138 |
| 133 | 适用 | R04–R11 每轮双指定模型独立审查＋ROOT 处置门禁在案 |
| 134 | 适用 | worktree＋feature 分支＋base SHA 记录＋禁共享分支强推（AGENTS §5） |
| 135 | 部分适用 | 锁文件冻结＋dependabot weekly 配置；月度升级执行节奏未核 |
| 136 | 部分适用 | Electron 44.9.0/RDFLib 7.6.0 锁定；安全补丁响应窗口为维护票未承诺 |
| 137 | 部分适用 | vendor 冗余 wheel 留树（受控清理票）；代码内死代码未见系统性清理流程 |
| 138 | 部分适用 | t02 spec 2175 行/mainline.py 1207 行为最大件（前者为矩阵生成式测试，可维护性观察）；无 2000 行级产品模块 |
| 139 | 适用 | ADR-0001/0002/0003 记录决定、理由、被拒替代与边界 |
| 140 | 部分适用 | AGENTS 指南＋仓库地图＋一键 check 脚本；README 快速上手未单独核验 |
| 141 | 适用 | status.md 逐轮快照＋迭代目录＋审查链完整可交接 |
| 142 | 不适用 | 无运维面板需求（本地产品） |
| 143 | 不适用 | 无客服/工单面 |
| 144 | 部分适用 | 提交历史＋状态文档构成变更记录；客户可读 changelog 无客户面 |
| 145 | 无法确认 | 代码侧隐私边界（无遥测/无外发/无收集）可核；正式条款/隐私政策文本与代码一致性未验证（组织法律未知保留） |
| 146 | 无法确认 | 账户/域名/仓库组织归属未核（组织事实） |
| 147 | 无法确认 | 人员配置未知；流程上多 agent/双作者并行机制存在但不等于 bus factor≥2 的人力事实 |
| 148 | 无法确认 | "senior engineer 逐行读 AI 代码"人力事实不可由代码认证；机制替代为双指定模型独立审查＋ROOT 接收，是否等效人工专家逐行无法确认 |
| 149 | 部分适用 | 数据模型由 ADR-0002 设计先行＋S1 spike 验证＋双审，非边做边改 |
| 150 | 无法确认 | 人员解释角色未配置（流程上首败保留＋处置链部分承担该职能） |
| 151 | 不适用 | 无云部署/运维/云账单（本地构建与 CI 成本属工具订阅，非产品运维） |
| 152 | 不适用 | 无 on-call 值守 |
| 153 | 部分适用 | 框架锁定版本＋升级须打包验证（AGENTS 改动表）；漏洞应急响应 SLA 未承诺 |
| 154 | 不适用 | 无患者数据/外部审计员 |
| 155 | 部分适用 | "testing what the AI tested"由独立审查轮＋既有原件身份标注＋不复跑原则部分承担；独立 QA 人力未配置 |
| 156 | 部分适用 | 迁移在真实 SQLite 上故障注入测试（新建/回填/触发器/崩溃窗口）；大规模活库迁移未验（HOLD） |
| 157 | 无法确认 | 产品范围否决机制（Q 决策点）设计在 PRD/计划中；实际 tech lead 人力决策未配置 |
| 158 | 部分适用 | "每客户同时可用"以预算准入硬界＋容量 HOLD（Q5 未定不设通过线）替代性处理；规模化验证未做 |
| 159 | 无法确认 | AI 无法调试时的资深兜底人力未配置 |
| 160 | 适用 | AGENTS/ADR/状态文档/m0 清单持续记录"为什么这样建"（本轮 §0 旧路径失效即按文档追踪关闭） |

逐档计数（逐行复核）：**适用 30／部分适用 50／不适用 73／无法确认 7，合计 160**。再次强调：这是适用性判定分布，不是产品功能通过数；"适用/部分适用"项中多数仅 P0 面已覆盖，其余面按 §2/§4 的门禁与 HOLD 处理。

## 6. 总体结论

**本人判定：ConditionalPass（有条件通过——限定为推送前技术阶段）。**

依据：

1. **无 push 前源码技术阻断**。本人对 base→d1aca3e3 全累计候选做了独立分层阅读（§1）：产品实现链（renderer 表单/会话/ownership 详情、主进程 IPC 白名单与 epoch 复验、preload 业务命名、contracts 双端 matcher 与字节流重组、engine 存储 typed 冲突 witness/写准入记账/分页详情、coordinator bootstrap 限制）与 PRD FR-200/FR-201、附录 C/D 及架构不变量逐项对照，未发现新的产品源码缺陷。本轮 delta（cfcc→d1aca3e3）为归档、一字节格式修复与两测试文件的失败留证/测量能力，产品代码零改动，且其保全性有 O074 双独立审（C1 14 纯 mock＋FR 12 VM 边界，callback AST 归一化相同）与本人独立复核双重确认。
2. **通过的条件（全部既有，非本轮新设）**：(a) 完整三平台真实 CI 在同交付（实现/测试/CI/依赖）下通过——Quality/Windows/macOS 三 job 真实 success、3769 逐 node 或原有据 skip、自然 0、无失败/早停/取消/timeout/NOTRUN、packaged recovery 步骤自身 success、原 15/20 分钟预算不变；(b) Windows C1 与 FR201 在下一授权运行中复验，C1 根因在取得新留证附件后定因，FR201 累计预算在 Windows 上不再近满；(c) §2 #5–#9 与 §4 全部保留/HOLD/窗口事项按原归口推进；(d) 既有测试事实（O074 fullcheck/native24 等）为既有原件身份，不因本报告变为本人运行。
3. **不构成 Pass 的原因**：完整平台 CI 从未在本候选通过（CI43 failure，2d6 修复未重跑）；Windows 两大 E2E 失败的根因/预算问题处于 UNKNOWN/未验状态；签名公证、法律隐私产权供应链、跨 OS/参考设备、容量、损坏 SQLite、未验 Undo/ownership 家族、未知退出码等独立 HOLD 全部保留。技术阶段有界通过不等于完整产品放行，整体合并可用仍为 2/17（FR401/402），M0/Goal/发布未完成。

本判定为本人独立形成，不继承 R04–R10 任何一方的结论，也与另一作者本轮意见无涉。

## 7. 未验证与边界（本报告不冒充的清单）

- 本轮未运行任何 check/vitest/pytest/build/package/formatter/HMR/GUI/SQL/bridge/探针；§3 引用的 fullcheck/native24/CI43/CI42 等全部为既有原件（O072/O073/O074 及更早 outputs）身份，本人只做只读核对与引用。
- Windows 平台行为（C1 异步失败根因、FR201 预算、后代进程回收、引擎退出码）全部保持 UNKNOWN/未验；d1aca3e3 新增的失败留证与计时在该平台无样本。
- 签名/公证/安装、法律/隐私/产权/供应链、跨 OS 与参考 8GB 设备、容量与旧超限库恢复、损坏 SQLite 物理保护、unknown parser/N3/Store/坏快照、Undo/未验 ownership 家族、四具名下游 GUI、T04 基线更新等独立 HOLD 未关闭。
- 本报告不嵌入自身最终 bytes/hash（由 owner 实测保存）；不授权 push/CI/merge/预算/新任务；发现实质源码问题时的处理权在 owner。
- 远端状态：本轮 ls-remote 网络失败未获新读数，远端事实以 O072 官方回执为据（remote feature=cfcc、develop=583、PR16 open 未合并）。

（报告完）

---

# R11-a1 追加稿：必要补读闭合与事实更正（同会话 session_473f2e39…，owner 依自然稿 51429B/SHA256 a35ea30d… 与固定源码读回反馈；仅追加，原报告全部原字节前缀保留）

以下各节是对自然稿 §1/§2/§4/§5/§6 的有效替代与事实更正；替代处以本稿为准，未列出的原判定维持。本轮仍未改源码/测试/预算/门槛、未复跑验证、未新任务/付费/重置，不为求通过改判。

## A. F01 必要覆盖补读闭合（替代原 §1"文件级＋抽样"缺口与 §4.1 F01 行）

owner 指出原稿 §1 声明 6 个 engine 测试/12 个 unit 仅文件级＋断言抽样、以旧轮全文作理由，却判 F01"已闭/本轮履行"且结论称全累计完成——成立。本轮已按 `git diff --name-status base..head` 实际清单补读至 EOF，具体亲读范围与断言如下（全部本轮新增正文，非继承旧轮）：

- engine 新增 6A 全文亲读至 EOF：`test_mainline_language_input_rejection.py`（327 行：R03 语言/整数拒绝 6 参数化×owned 复用＋独立 stdio 子进程物理文件级 databaseBefore==After、requestUnchanged、RED HOLD 首拒即停、forcedKill=0、数字子标签合法提交/大写保规范拒绝）、`test_mainline_manual_input_rejection.py`（1035 行：R02 五词法＋urlsplit/IRI 字段隔离；未知 parser/N3/urlsplit/iri/vendor 内部故障含"相同文案不按消息分类"保留 INTERNAL_ERROR+HOLD+unknown 不驱逐；reservedIdentity 受控冲突 detail 行级 diff 仅增诊断行；三 reason 完整分页＋重复拒绝同 ref 去重；singleDeclaration 三形态，removed-first 保留原 Store 矛盾计划 UNKNOWN 不弱化守卫求通过 L955–972）、`test_mainline_postwrite_admission.py`（861 行：三轴±1 边界、终态尾部 2742<4096 独立钉、真实 draft 增长受控拒绝＋同 owner 小后继、排队 commit 三结局复检、双项目全局余量、前后台 scope 不可借用、after_commit 重入 INVALID_STATE、清理/结算失败保因保持有、bootstrap 未结算写者 8 状态不可收养、继承者不接管排队/活跃 job、真实 stdio 增长拒绝＋bootstrap 重启对账 ENGINE_EXITED＋marker null）、`test_mainline_postwrite_rows_budget.py`（396 行：243 行五列真实 rowsPage 固定 final fee 1114112/8192/134217728 每页恰一次、预付拒绝原子无退款、页 scope 不借不退、预付材料不可二次消费）、`test_mainline_postwrite_text_budget.py`（321 行：56309 字节冷历史前缀（含多字节界😀）恒等偏移、text final prepaid 528384/256/1052672、游标回调吊销在最终编码器前拒绝且无新游标行）、`test_mainline_read_work_budget.py`（560 行：默认全表公式与 core 公式分离（同 fixture 默认 reader limit 而 core 通过）、64MiB 两阶段（lower/authorized-plan 由 json_extract SQL trace 区分）、真实重复解码历史有界、六种损坏形态在完整鉴权后 STORAGE_FAILURE+HOLD、authorizer 拒绝 json_extract 无零回退）。
- `test_mainline_dispatch.py` 完整 diff（+523 行）亲读：40k 字符 locator 分页完整性、错 documentHash→IDENTITY_CONFLICT、跨项目→NOT_FOUND、四损坏→STORAGE_FAILURE+HOLD、segment 写入失败全回滚无 detailRef、诊断不污染已准入 reader（早/晚）、私有 admission 保 core-only 向量、坏 blob 复用前 reserve、raw 段预算拒绝先于 JSON 解码、行帽去重复用/新上下文回滚、legacy 三字段 detail→INVALID_STATE 不发明 locator、跨会话 ref→NOT_FOUND。
- unit 新增 5A 全文亲读至 EOF：`t02-manual-fact-id.test.ts`（187 行，spawnSync 显式 `resolve('.venv/bin/python')`＋真实 Store._fact/digest/canonical 交叉核验 golden 全向量、延迟 digest 捕获原 tuple、lone surrogate 在 digest 前拒绝）、`t02-ownership-detail-view.test.ts`（139 行 SSR：XSS 全字段转义、>16KiB ID 不截断不推断 IRI、只读无操作面）、`t02-manual-preview-lifetime.test.ts`（597 行：真实 Page transpile+VM harness，13 种晚到 hash 拒绝、同 tuple 重复 submit 只取最新、真实 Session retire/dispose 阻断、同步订阅者改稿不领养、detail 挂载/清除 9 种、晚到 detail 成功/失败不复活）、`t02-ownership-detail.test.ts`（844 行：公共 reassembly 14 首页篡改＋6 后页＋4 文档级负例、>17KiB Unicode 保留、SHA await 后 fence、私有页捕获、Session 绑定 invalid detailRef 8 形态/伪装码 4/getter 失败 8/7 种同步清除/5 阶段×2 晚到隔离/5 种 active 复验/microtask gap fence）、`ui-observation.test.ts`（195 行：fieldset legend 豁免、ARIA 大小写折叠不 trim、重复/不支持形态 fail-closed、receipt 首段身份与已读版本精确、16KiB 槽上限与保留他 annotation）。
- 8M unit 完整 diff 亲读：`t01-business3-contract.test.ts`（手写 SHA-256 对 Node crypto 8 长度交叉、ownership 页关联/合法错误/禁止 wire issuer 参数）、`t01-mainline-contract.test.ts`（reassemble 私有页捕获/末页乱序/重复段/坏字节拒绝）、`t01-mainline-ipc-delivery.test.ts`（ownership 页同 sender/frame 校验与缺 ACK 持有）、`t01-mainline-project-service.test.ts`（真实 source fence 后晚到页不可重发布、撤销选择保留不确定投递）、`t01-mainline-real-runtime.test.ts`（真实 preload→IPC→service→stdio 全链 4 family＋large ownership detail，退出码全 0 断言）、`t02-mainline-consumer.test.ts`（OWNERSHIP_CONFLICT 可操作＋下一有效 preview、未知码/异常不泄私值、manualFactPlan 多值不动兄弟支持/词法不塌缩/受管 fence/重叠拒绝）、`t02-mainline-metadata.test.ts`（五变体 C 子集矩阵 create/edit/copy/delete 独立预期三元组、外部引用精确报告）、`native-driver.test.ts`（绝对截止复查、whenReady 卡住限界内、晚 ready/取消后不再发 helper、drain 限原 deadline）。
- 契约正文亲读：`tests/fixtures/t02-manual-fact-id.json` 全 139 行（13 向量含中文 IRI/非 BMP/转义/多行/NFC-NFD）；`schema.json` ownership 新增块全文（request/response 信封、ownershipDetailDocument 两 kind、manifest totalBytes≥2/segmentCount 1–512、result segments minItems:1/maxItems:64、startOrdinal 0–511）；`registry.json` 两处方法表新增；`binding-regressions.json` 全 diff（仅 registryHash 16 处值更新）；`fixtures.json` 新增段（named ownership request/response 正反样例、registryHash 同步）。
- O074 必读件正文读回（不重算）：`NATIVE24-QUALIFICATION-02.json` 读回结构、头部与代表性 check 正文（original24Cases/orderedFileTitleExact/21Pass3OriginalSkip、case1–17 test/result 三槽检查族）、关键汇总段（FR201Final marker rev22、case7 singleCommit1/execute0/replay0、transactionGroups 7/7/7/7/22/7、negativeCodeCounts 42 INVALID_REQUEST＋1 OWNERSHIP_CONFLICT、pollTimingSummary 12 副本实际最大 2223B、runtimeIdentity 2d6＋两 inputPins、engineNaturalExit=UNKNOWN、limits）；`INDEPENDENT-COMMIT-BINDING.json` 读回 487 checks 全 true（exactAuthorizedTwoPaths/actualHeadTreeSoleParent/stagedTreeEqualsActualCommittedTree/commitExactlyTwoPaths/blob 与 WIP/fullcheck pin 逐字节绑定、executionToCommitMapping 明示 runtimeWasExecutedOnLaterCommit=false 且映射非重跑）。原失败的 `NATIVE24-QUALIFICATION.json`/`STATIC-VALIDATOR-FIRST-FAILURE.json` 维持失败原件身份，不充当有效 -02。

**补读结论**：新增测试与契约正文未发现弱化断言、删例、放宽边界或新的产品源码缺陷；相反确认多处正面事实（见上）。原稿"无 push 前源码技术阻断、ConditionalPass"的结论经本轮全文补读后维持。F01 现可如实记为已闭（本轮履行，含本追加稿补读）。仍属未读/摘要级：`fixtures.json` 其余既有条目、二进制 wheel 内容、PRD 附录 E/G 全文（原稿已披露，维持）。

## B. §6(2)(b)(c) 门禁措辞撤回（有效替代，不新增门禁）

原稿 §6(2)(b) 中"Windows C1 与 FR201 在下一授权运行中复验，C1 根因在取得新留证附件后定因，FR201 累计预算在 Windows 上不再近满"超出了原验收，**撤回后两句**，替代为：

- C1：根因 UNPROVEN 是 HOLD 与主张纪律（F-R09-02 口径），不是"取得附件后必须定因"的 merge 前证因门禁；d1aca3e3 新增失败留证 catch 在真实 Windows 失败路径上未被触发（O074 limits），未来授权 CI 若复发，读其附件定因即可，不定因不构成额外阻断条件，也不以未来 CI 绿倒填旧原因。
- FR201：按原验收实际结果判断（原 180s 预算、22 事务/43 拒绝、完整 Diff/断言链），**无"预算不再近满"之类余量阈值**；CI43 的 474ms 名义余量是事实记录，不是通过线。
- §6(2)(c) 的全部维护/HOLD/窗口事项**保留原 owner 与事件窗口**，是既有归口的延期事项，不是当前推送前的完成条件；推送前条件仅为 (a) 类既有 CI 门禁与授权票。

ConditionalPass 判定本身不变；其"条件"以本节修正后的口径为准。

## C. F14 行内观察更正与本方新 ID（Z11-OBS-01）

原稿 §4.1 F14 行称"TS/Python matchesOwnershipDetail 对'空段页'谓词不对称（TS 允许 start==end==count、Python 要求 start<end），但 schema minItems:1＋引擎 INVALID_REQUEST 双前置使其不可达"。owner 读回证实该表述不成立：**两侧公开 matcher 都先做 schema 校验**——`v2.ts:535-540` `matchesOwnershipDetail` 首步即 `validateBusiness3('params_…')`＋`validateBusiness3('result_…')`，`contract_v2.py:468-482` 同样先 `validate(…)`；`schema.json:11850-11857` `segments minItems:1` 使空段页在两端的 validate 阶段一致拒绝，根本进入不了算式分支。因此不存在"TS 允许空页、Python 不允许"或"当前 schema 合法域内行为不对称"；Python 的 `not start < end <= count` 只是 schema 合法域之外的冗余防御写法差异。引擎侧 `job_store.py:943-944`（`start>=segmentCount`→INVALID_REQUEST）与 renderer reassemble 的 fail-closed 亦非唯一防线，本稿不再以它们作为该不对称"不可达"的依据。

**正式新 ID：Z11-OBS-01**（非缺陷·维护观察）：双端 `matchesOwnershipDetail` 的算式写法存在冗余防御差异（Python 多一条 schema 合法域外 `start<end` 下界检查，TS 无对应项）；当前行为在 schema 合法域内完全一致。未来若 schema 收窄或 matcher 重构，注意保持双端谓词集合同步。不新增修复门禁。归口：原 T02 契约归口维护票（同 F14 窗口），仅注释级。原 F14 状态"保留（→维护边界）"维持，其行内技术描述以本节更正为准。

## D. Top 表稳定主题修正与本方新条（Z11-R01/Z11-R02）

- **原 §2 #3 撤销挂靠**：Z09-03/Z08-02 的稳定主题是 engine/Windows 后代**退出码 UNKNOWN**，不用其承载 FR201 预算主题。两项维持退出主题（数值不变：O074 `engineNaturalExit=UNKNOWN`、CI43 后代无 JobHandle）。CI43 FR201 预算近满改列本方新条 **Z11-R01**：Windows FR201 整例 180002ms、第 21 笔后 Diff 可见等待起 179525.790ms、名义余量 474.210ms（O072 原件与 timing 表），无单次>5s 已完成 poll；严重性高（CI 条件），非源码阻断；最小建议＝下一授权 Windows 运行读取 d1aca3e3 新增 5×19 timing 附件定位大类耗时（测量用途，非修复承诺）；按 §B 口径无余量阈值。
- **R10-02 主题分列**：R10-02/Z09-02 保持 CI41 `native-recovery.cjs:12` `app.isPackaged` TypeError 根因未证主题不变。CI43 C1 新形态（readiness1、bootstrapComplete true 跨过同步装载后收到 child close 1/null、driver L103 cause/L284 drain 包装）列本方新条 **Z11-R02**：与 R10-02 分列不替换，根因同属 UNKNOWN/HOLD（非证因门禁）；d1aca3e3 失败留证 catch 未在真实 Windows 触发。原 §2 #2 的内容主体正确，其"承 Z08-02/Z09-02/F-R09-02/03"链中 CI41 部分归 R10-02、CI43 部分归 Z11-R02。

## E. 行号与定位修正（对原稿 §3/§4.2/§5 的有效替代）

1. postwrite §31 限证：原 replay 引用 **L211–213 无误**；"后续合法 Read"实际为 **L231–233**（`assert final["ok"]…projectRevision == 1`），原稿所写 L216–218 是 `confirmed_job(actor, project, {…})` 的参数段。两段区分结论不变。
2. 两个裸 PATH python 实际位置：`tests/unit/t01-mainline-contract.test.ts:656`（`execFileSync('python', …)`，本轮亲读）与 `tests/unit/t01-ontology-metadata-contract.test.ts:168`（同形态，本轮亲读）。原稿 §4.2 Z F5 行"另一处 real-runtime 同"**错误**——`t01-mainline-real-runtime.test.ts` 无裸 python 调用（其子进程经 `getEngineCommand` 固定命令并观察 `spawnfile/spawnargs`，L330–345 亲读）。Z F5/R06 D8/R05 MM12/R06 MM12 的"两 TS PATH python 在位"事实不变，定位以本条为准。
3. `QueryResultPanel.tsx` 位于 `apps/desktop/src/renderer/src/query/`（原稿未写路径，此处补正）：`downloadCsv` L16（`'\uFEFF'` BOM＋`text/csv;charset=utf-8` Blob＋临时 a[download]）、真实调用 L250（ASK 结果 CSV）与 L317（当前页 CSV），本轮亲读。
4. `job_store.py` 实测 **2993 行**、`storage.py` 1887 行（产品模块）。

## F. 原 160 项必要事实限证（逐项有效替代；其余 154 项维持原判）

- **#31（dedup 四次点击）**：判定维持"适用"，依据改写——43 输入/ownership 拒绝是词法与所有权拒绝，**不能单独证明重复点击去重**；真实去重证据为：同 operation/job/计划重试返回原 marker 不重复写入（ADR-0002＋postwrite/stdio replay 断言）、每笔提交单一显式确认链（e2e 22 事务每笔一次 confirm）、提交期 pending/phase 阻断新提交、ack-loss 首投递丢失后按回执 reconcile 不自动重放（e2e 真实断言）。
- **#33（exports）**：**不适用→部分适用**。有限 CSV 导出真实存在（`query/QueryResultPanel.tsx:16/250/317`，BOM＋当前页/ASK 两处真实调用）；FR-203 Turtle 导出与 FR-1000 项目包导出未实现，另保未完成。
- **#48（渗透测试）**：**不适用→无法确认**。其组织适用与实施未知；"本地/无端口"只说明当前外部暴露面小，不能由此判定已无风险或不需要渗透测试。
- **#57（GDPR 删除）**：**不适用→无法确认**。组织法律适用性未知；本地单用户形态降低暴露面，但不等于合规义务豁免的判定。
- **#138（2000 行文件）**：判定维持"部分适用"，事实更正——`job_store.py` 约 2993 行、`mainline.py` 1207 行、`storage.py` 1887 行，**存在 2000 行级产品模块**；LOC 非质量结论，低优先维护观察，归 owner 限证。
- **#23/#40 及全稿"双端 zod"措辞更正**：准确表述为 TS 侧 zod（`z` schema/strict）＋Python 侧自有 schema 适配（`contract_v2.py` `validate`），不称"双端 zod"。
- 逐行重算后分布（与原稿 §5 末计数不同处以此为准）：**适用 30／部分适用 51／不适用 70／无法确认 9，合计 160**（#33 NA→部分；#48、#57 NA→未知）。末 13 项（#148–160）本人逐行重算维持：4 无法确认（148/150/157/159）、3 不适用（151/152/154）、5 部分适用（149/153/155/156/158）、1 适用（160）；未预设标签或对齐他方分布。

## G. 补读新登记正面事实（非缺陷，供归档）

manual_input_rejection 对未知 parser/N3/urlsplit/iri/vendor 内部故障（含相同文案异常不按消息分类）保留 INTERNAL_ERROR＋HOLD 且 unknown 回复不驱逐；removed-first 矛盾计划保留原 Store 守卫（不弱化 fixture 求通过）；rows/text 固定 final fee 与 text final prepaid 数值断言在位；read_work 默认/core 双公式分离有同 fixture 反例断言；real-runtime 真实全链 4 family＋large ownership detail 子进程退出码全 0；native-driver.test 绝对截止复查与晚就绪不补发 helper；metadata 五变体独立预期三元组；business3 手写 SHA-256 与 Node crypto 8 长度交叉一致。以上与原稿结论一致，无新阻断。

## H. 边界重申（本轮追加后不变）

CI43 overall failure 保留；Windows C1/FR201 根因 UNKNOWN（Z11-R02/Z11-R01 分列，非证因门禁）；d1aca3e3 失败留证 catch 与 poll 计时在真实 Windows 无样本、非修复；整体合并可用 2/17；HOLD 关闭 0；新候选无 push/CI/merge；测试事实均为既有原件身份。最终意见集合维持：原31、权威78、R09 新19＋OBS、额外 R06 MM01–13、R10 ZTop9＋MM Top10＋T11/T12、本方 Top9（§2 修正后）＋新观察 Z11-OBS-01＋新条 Z11-R01/Z11-R02，各保原 owner 与事件窗口。本稿为本次必要补读与事实追加的完整闭合，此后自然结束；后续低优先措辞由 owner 限证。

（R11-a1 追加稿完）

---

# R11-a2 追加：末次极小阅读回执（同一 SID／d1aca3e3／base583；仅追加，自然稿 01 前缀 51429B 与自然稿 02 全部 68488B 前缀逐字节保留）

本节为 owner 指定的四处剩余正文补读回执；不改模型/源/测试/预算、不复跑、不新增门禁，不扩大 scope（未变无关上下文、vendor 二进制、新平台运行不在本次范围）。

## 本轮实际读取范围（官方回执口径）

1. `tests/unit/native-driver.test.ts` 累计 M diff 第 421–437 行（此前已 sed 1–200、200–420，至此 437 行 diff 全量闭合）。尾部为实质断言而非闭合括号：`helper-error` 形态下原 helper 异常以 `exceptionDetails:{text:'original helper failure'}` 传播、`helperRequests` 恰 1 次、总 `requests` 恰 2 次（readiness 评估＋helper）；invalid-json/send-throw/unknown-state 形态 helper 0 次、requests 1 次；四形态均 `expectClean()`（监听清空、无残留 timer）。
2. `packages/contracts/v2/schema.json` 累计新增行 341–525（新增行口径＝diff 后仅 `+` 排除 `+++`；至此 525 新增行全量闭合）。内容：`ownershipDetailManifest`（documentKind 常量、documentHash hash、totalBytes 2–16,777,216、segmentCount 1–512，required＋additionalProperties:false）；`ownershipDetailHeader`（origin 三 id 必填 ownerId/hostClientId/engineSessionId、requestHash/fingerprint hash、segmentBlobRefs 1–512 hash 数组）；`params_project.ownership.detail` 两变体——首页 `documentHash:null`＋`startOrdinal` const 0、续页 hash＋startOrdinal 1–511，pageSize 两变体均 1–64；`result_project.ownership.detail`（detailReadVersion 1、startOrdinal 0–511、segments minItems:1/maxItems:64、nextOrdinal 1–511|null、complete 布尔、全 strict）。与引擎发送端（job_store ownership_detail_page）及消费端（matchesOwnershipDetail/reassemble）约束一致。
3. `packages/contracts/v2/fixtures.json` 完整 M diff 变更对象正文读全（剔除 registryHash 行后 1–417 段逐段读）：**全部 96 个删除行均为 registryHash 旧值替换**（`058ed1be…`→`5e097b7e…`，随 registry.json 方法表新增两处同步），无任何其他旧 wire 字段被删除或改写。新增样例 6 个正文全读：request 侧 `named ownership request`（正）、`ownership no null continuation`（首页带 startOrdinal:1，负）、`ownership wire issuer forbidden`（params 附加 ownerId，负）；response 侧 `named ownership page`（正，2 字节 `{}` 段，documentHash/段 sha 均 `44136fa3…`＝sha256("{}")，dataBase64 `e30=`）、`ownership wrong ref`（响应 detailRef ≠ 请求 detailRef，负）、`ownership corrupted segment SHA`（段 sha 全 f，负）、`ownership premature next`（单段页 nextOrdinal:1＋complete:true，负）。
4. PRD 附录 G 本功能必要闭包（非整 E/G 全文，本轮实际读取）：G.5 表 A-01（生成 Diff 后手工修改同一属性→旧 ChangeSet 不得直接覆盖）、A-02（模拟 ChangeSet 提交中途失败→项目保持修改前状态，不得只提交前半部分）两行原文（PRD:1236–1237）；G.6 项目恢复与迁移全 7 条原文（PRD:1249–1255：提交边界异常退出只恢复最后已提交状态、存储写入失败已提交项目可读且未完成批次不混入、设备 A/B 完整项目包恢复相同断言/查询结果/来源/所有权并重识别同一冲突、模板包不承诺恢复、无原始文件＝可恢复不可重跑、可重放需输入/配置/行为规则版本/执行语义版本齐全、导入后编辑/查询/重跑/撤销同原规则）。

## 语义断言要点（本人对照实现，非旧轮引用）

- **A-01 ↔ 本候选实现**：preview 绑定 baseRevision＋confirm/commit 时基准复验（REVISION_CONFLICT，storage/domain_changesets 亲读）＋mainline-session requireCurrent/epoch fence＋renderer 异步预览 fence（F08 链）共同落实"旧 ChangeSet 不得直接覆盖"；手工修改他人槽位由 reservedIdentity/sameStatement/singleSlot typed 冲突拒绝（storage.py:1211–1228 亲读）。
- **A-02 ↔ 本候选实现**：Store.commit 单事务原子（基准复验/数据/所有权/版本/失效/前后快照/marker 同事务，ADR-0002），提交前/中异常回滚；postwrite/manual/stdio 测试以 `non_job_rows` 不变与物理 DB 字节相等断言"不提交前半"；提交成功后取消不撤销为对称面。
- **G.6 ↔ 本候选实现**：重启对账（bootstrap reconcile→未完成 job ENGINE_EXITED＋marker null，postwrite stdio 测试亲读）、所有权/对账边界（同 operation/job 重试返回原标记幂等；ownership detail 跨会话 NOT_FOUND、去重复用、损坏 STORAGE_FAILURE+HOLD，dispatch diff 测试亲读）。G.6 第三条设备 A/B 项目包迁移属 FR-1000 未实现，本候选不覆盖、不冒已验；G.5 A-03–A-10（Agent/隐私/导出/HTML）在 S3 前不在本候选链内，不作为已验引用。
- schema 341–525 与 fixtures 新增 6 样例同前述实现/测试三方一致；registryHash 替换为 registry 方法表新增的必然连带，非独立契约变更。

## scope 与结论确认

以上四处为前稿覆盖清单的最后缺口，本方对 base583→d1aca3e3 全累计候选（43 提交/125 路径/1403 源叶）的必要正文阅读至此闭合：无新的源码问题。维持原判定 **ConditionalPass** 及全部边界：CI43 overall failure 保留、Windows C1/FR201 根因 UNKNOWN（R10-02/Z11-R01/Z11-R02 分列口径）、d1aca3e3 失败留证与计时在真实 Windows 无样本、整体 2/17、HOLD 关闭 0、无 push/CI/merge。统计 30/51/70/9、末 13、原 163 稳定位置＋Z11-OBS-01/R01/R02、门禁撤回与主要事实替代均已由 owner 核收，不重做。append B 末"推送前条件为(a)CI"一句按 owner 限证理解：真实 CI 门槛约束 merge 与后续票，不构成 CI 必须先于首次 push 的逻辑循环，本方无需另释。本轮后自然结束，不为美容再循环。

（R11-a2 完；本报告至此为最终态）
