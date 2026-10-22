# T04-S1 Round-1 ZCode GLM-5.3 指定完整独立审查报告

结论先行：**通过**（仅适用于登记的同版完整 T04-S1：base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → product `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6` 的全部 33 项固定输入及其登记边界）。未发现 P1/P2 阻断问题；新发现 3 项 P3（均不阻断本 S1 范围，见第六节）。全部 8 项历史意见经本人独立源码/测试复核确认关闭。**完整父 T04 与产品功能仍未完成**，第八节所列真实执行/接线/平台/发布门全部未验证，本结论不构成对它们的通过。

## 1. 任务来源、设置与时间线（真实读回）

- 任务来源：操作者（T04 setup owner 线）经本方 ZCode 界面以 computer use 新建的本轮新完整独立任务；会话即本对话。
- 设置收据：`test-results/t04-review-runtime/zcode/metadata/owner-task-settings.json`（observedAt `2026-10-22T15:43:19.606240+00:00`，即北京时间 23:43:19，phase 为提交前草稿观察）。读回：model `GLM-5.3`、thinking `最高`、permission `完全访问`（interpretation `yolo`）、cwd `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-zcode-review-554ec89`、branchLabel `游离 HEAD`、reviewHead `9a4dfc8f…`，`settingsActuallyObservedForThisDraft: true`、`globalConfigOrOtherTaskEvidenceUsed: false`。与指定要求 GLM-5.3/最高 max/yolo 一致。
- 实际 task ID：收据为提交前快照，`taskId: null`；本会话内无可用原生任务 ID 句柄，按"未知"如实报告，不伪造。创建/正文接收时间：2026-10-22 23:43:29（+08，附件投递时刻，与收据观察时刻相符）。
- 未读取全局身份配置、全局日志、凭据或另一方本轮任何材料；`minimax-m31flash-input.md` 仅知其共享清单内哈希，未读内容。

## 2. 身份、来源与完整性核验（全部实际执行）

| 项 | 声明 | 实测 | 结果 |
| --- | --- | --- | --- |
| 附件 | 83018B / SHA256 `d2c0b328…6bb28` / 496 行 | `shasum`/`wc` 实测一致 | ✓ |
| 附件嵌入关系 | full-zcode-input + diff 附录 | `full-zcode-input.md`（78475B/`c7abb78d…`）原字节嵌入附件；`operation-note.md` 原字节嵌入 diff 附录块 | ✓ |
| 审查树 | detached HEAD `9a4dfc8f1e9106a4c05423f80a26e9e88eb0aaa1` | `git rev-parse` 一致；`git status` 仅 ` M AGENTS.md` + 两个流程目录未跟踪 | ✓ |
| 554→HEAD 差异 | 仅流程证据 | `git diff --name-status 554 HEAD` 全部为 docs/ 路径，无源码/测试/配置/锁变化 | ✓ |
| 33 项产品 blob | mapping-zcode.json 逐项 bytes/sha256 | 33/33 与固定 554 Git blob 全等；除 `status.md`（物理文件属后续流程，产品原版 `237f2343…` 由 Git 读回）外，32 项在 9a4 与工作树亦全等 | ✓ |
| 完整产品 diff | 170428B / `777ef6d5…` | `git diff --abbrev=7 5f 554` 与 `--binary --abbrev=7` 均复现同值 | ✓ |
| 保护 AGENTS | 15147B / `de15f6ce…` 未暂存 M | 实测一致，未覆盖/未格式化/未提交 | ✓ |
| 锁文件 | package-lock `a462ba70…` / uv.lock `d5d027da…` | 实测一致（与 setup 收据同值） | ✓ |
| launch 输入 | delivery-manifest-zcode.json 11 项 | 逐项 shasum 全等（含 supplement `a6cf1335…`、common `567b6e70…`、desktop-policy `2032bd9e…`、permissions `feea1595…` 等） | ✓ |
| 旧冻结 prompt/manifest | `2761fa38…` / `804ce95a…` | 实测一致 | ✓ |
| raw 归档 | 6081B tar.gz / 37 成员 / 61602B | 本人独立解包：SHA、37/37 成员字节/大小/哈希逐项全等，总字节一致 | ✓ |
| PRD 源 | base 5f `7586b2c4…` | `git show 5f:…` 实测一致；T09 manifest 的 17 项输入哈希链（manifest `aaaef2c0…`→PRD）在测试内每次运行复核 | ✓ |

产品原 `status.md`（554 blob，5541B）已按 Git 原字节完整读取；当前物理 status 属后续流程，未误判为源码漂移。

## 3. 实际执行的验证（S1 普通运行面；cwd 均为本审查树）

先静态核对脚本入口：`package.json`（`check` = lint→format:check→typecheck→test→build→engine:check）、`vitest.config.mts`（仅 `tests/unit/**`）、`apps/desktop` 构建为 `electron-vite build`、引擎 `pyproject.toml`（仅 rdflib==7.6.0，`query_service` 未接入 `__main__`/protocol）。环境隔离：`npm_config_cache`/`UV_CACHE_DIR`/`TMPDIR` 指向本方独占 `test-results/t04-review-runtime/zcode/`。

| # | argv | 起止/时长 | 真实退出 | 结果摘要 |
| --- | --- | --- | --- | --- |
| V1 | `npm test -- tests/unit/t04-query-authoring.test.ts tests/unit/t04-query-results.test.ts tests/unit/t04-query-reader.test.ts` | 23:52:45，约 3s | 0（输出判定：Test Files 3 passed） | 36/36（6+6+24）通过 |
| V2 | `node docs/iterations/T04/ssr-probe.mjs` | 23:52 前后，1s | 0（`passed:true`） | 14 项静态 SSR 检查全过，边界自declared |
| V3 | `uv run --frozen pytest packages/engine/tests/test_query_service_authoring.py packages/engine/tests/test_query_service_approved_baseline.py -q` | 23:52 前后，1s | 0 | 31 passed（28 编写 + 3 基线含同数量错义反例） |
| V4 | `npm run check`（完整链） | 23:53:17–23:54:36，79s | **0** | lint 0 警告；prettier 全过；typecheck 三套 tsc 全过；vitest **18 文件/666 项**；`electron-vite build` main/preload/renderer 成功；ruff check/format 全过（198 文件）；pytest **1083 passed in 55.36s**（含 `test_worker_parent.py` 1 项实际运行，即普通 worker 回归已在全量内覆盖） |

V1–V3 的 shell 记录行因 zsh `PIPESTATUS` 大小写差异未写入 EXIT 数字，成功以日志原文（vitest 汇总行、probe JSON、pytest 汇总行）为准；V4 用 `pipestatus` 正确记录 `EXIT=0`。原始日志（含完整 stdout、`EXIT=`/时长行）与 SHA-256 在 `test-results/t04-review-runtime/zcode/raw/review-*.log`（ignored 独占目录）：`review-vitest-t04-targeted.log` `f6776e9f…`、`review-ssr-probe.log` `d57d0bba…`、`review-pytest-query-service.log` `31e814c5…`、`review-npm-run-check-full.log` `09972afb…`（7576B）。本轮**无首失败**；历史首失败（正则 lint、类型、import 排序、SSR esbuild 误用、Vitest 错误形状等）经 37 成员归档与三份汇总的版本归属核对确认真实保留且不冒充终态。本轮数据与登记终态（TS 18 文件/666、Python 1083、新增 TS36/Python31、reader24、SSR14）逐项相等；旧 640/642/1080/1082/SSR8/11 汇总按其旧候选版本正确归属，未当最终数据。`npm run build` 已在 V4 链内实际执行，未做无变化重复。未运行：dev/HMR/test:e2e/package:dir/任何 Electron/GUI（不在本 S1 普通验证面）。

## 4. 完整范围逐项审查结论（33 项全读，含每份测试/fixture/文档）

**Python `query_service`（`drafts.py` 5786B、`__init__.py`）与 TS `draft.ts`**：模板意图（告警 High/Open）、对象/字段/条件编译、`SELECT DISTINCT ?item ?fieldN … ORDER BY` 两实现逐 token 一致并与 `authoring-case.json` 金样例互验（TS 与 Python 测试各自完整字符串断言）；IRI 校验（scheme 前缀 + 空白/控制/`<>"{}|^\`\\` 黑名单 + 代理对拒绝）与字面量序列化（JSON 短转义即 SPARQL ECHAR/UCHAR，`\x7f→\u007F`，语言/数据类型互斥、语言小写）两实现等价；注入尝试（含 `SERVICE`/`}`/`#`）经 RDFLib Turtle 往返证明为单 term，IRI 碎片全部拒绝。条件上限 32、字段 16、draft 六字段严格形状、scope/source 枚举、revision `type is int`（拒 bool/浮点/越界）、definitionId 正则拒路径穿越。`save_intent` 仅产出不可变值意图（family/id/expectedProjectRevision/draftDigest/value），无 Store/执行/授权；`__init__` 仅导出 4 个纯函数。编写不激活执行：model 来源文本仅作草稿通过。

**T09 固定输入（S1-C）**：manifest（17 项，PRD 源 `7586b2c4…`）+ provenance（sourceCommit `873c8c05…`、`copiedUnmodified` 三件）哈希链完整；测试每次运行先验 manifest 与文件哈希，再仅从 `ontology`+`facts` 独立还原 G-base（不读 expected、不消费 T09 helper/Store）；原始 `unclosed-high.rq` 与生成查询各自独立重置图下完整结果均仅 `alarm/A01`（Q-01 语义），A01 改 Closed 后均空（Q-02 语义）；同数量错义反例 `"Open"→"Closed"` 完整答案为 A02 且与 A01 行数相同——完整集合比较而非数量。本人已读 G-base 原件（A01=High/Open@001、A02=High/Closed@002、A03=Low/Open@003）独立印证查询语义正确。

**`QueryPage.tsx`/`query.css`/结果工具**：模板按钮（无词汇禁用）、可视条件（显式 RDF 类型选择，不以 URL 外观伪造）、生成后 SPARQL 进入可见编辑器、model 草稿经 `draftSchema` 后以 `source:'model'` 载入编辑器（仍需用户执行）；范围选择持续渲染且执行输入（当前/历史快照）显式传递；结果侧 `queryMetadata`+`acceptPage` 严格校验，身份不匹配整块拒绝显示（不显示载荷），`executedSparql` 只取自结果对象（不取编辑器文本），React 文本节点天然转义（SSR 探针验证 `<script>` 转义）；表格 null→`未记录`（O-01 语义在 UI 层正确）；空页区分 `nextCursor` 有无（"仍有后续页" vs 末页）并列出 5 条可操作检查方向（含"不能据此证明业务事实不存在"）；单页 ≤200 行声明与 `exportPageCsv` 防护（`'` 前缀对抗 `=+\-@`/制表符前缀、`""` 转义、CRLF、BOM、仅当前页 ≤200 行/≤64 列）；evicted → 保留身份提示"载荷已回收"；stale 列表逐条渲染 code/dependency/before→after。无 `dangerouslySetInnerHTML`、无 Node/IPC/网络。

**保存/复用 UI**：私有 `SavedQuery{definitionId,draft}`；同名不同 definitionId 可区分；新建保存回调返回 ID 经 `definitionIdSchema` 严格解析，更新时返回 ID 必须与原 ID 一致（否则 `query.invalidIdentity`）；ID 绑定需同 request token 且同 document generation（新建/载入/卸载推进 generation，迟到响应不绑定）；保存期间新编辑由 `editRevision` 检测并在完成提示中标注"当前编辑已变化"。无真实 adapter 时执行/保存禁用并如实显示"尚未接入/尚未持久化"；renderer 不自报项目 ID、不写 Store。

**`results.ts`/`reader.ts`（S1-D）**：直接复用批准 5f 契约——`validateV2('result'/'page'/'pageBinding'/'job'/'result_job.cancel'/'error')`、`isTaskUpdate`、`TaskView`/`JobView`/`SafeError`/`internalError`/`safeError`、`DesktopBridge` 的 `getResult/getResultPage/getJob/cancelJob` 四个命名方法（本人已读 contracts/schema/registry 原件确认全部存在且 554 未改）。五字段身份（project/result/snapshot/scope/parametersHash）逐层复验；generation/project/snapshot/revision 变化全量重置；迟到 metadata/page 在 token/epoch 失配时拒绝发布；连接失效废弃在途读；仅用实际发行 cursor 单页读取且拒绝自循环 cursor；页内有序/唯一 + 跨页倒退/重复拒绝，最后非空行 ordinal/rowId 两字段有界锚跨空页保留；快照仅一页载荷且 `structuredClone` 防外泄修改；evicted 保留身份不请求缺失载荷。未扩大 bridge、未新增公共协议。

**取消/任务**：`queryJob` 复用批准 job validator 并限定同项目 + `capability==='query.execute'`；single-flight（`cancelBusy`）覆盖 ACK 后 `return await refreshJob(jobId)` 完整生命周期；取消受理（`cancelRequested`）与真实终态分离，ACK 经 `result_job.cancel` schema + jobId + 版本不回退校验后仅记 floor `{jobId, max(floor, ackVersion)}`，该下限覆盖后续 refreshJob/通知/取消前查询；同版本状态矛盾拒绝、已观察终态重开拒绝、合法跳跃观测接受（`compatibleJob`）；此前结果（jobId 不同）持续标注；dispose 只清显示状态不取消 worker。错误分类：身份/分页/参数分别落 INVALID_REQUEST 的 `identity`/`cursor`/`params`（均为批准 params.field 枚举成员），原始 bridge 异常固定 `internalError`，无原异常泄漏（测试以 `PRIVATE_PATH` 标记验证）。

**测试/fixtures/文档全量**：3 份 TS 测试（6+6+24）与 2 份 Python 测试（28+3）断言完整预期集合/顺序而非数量；fixtures 6 项与登记哈希一致；`ssr-probe.mjs` 为纯静态渲染（无浏览器/CSP/下载声明）；4 份迭代文档（acceptance/integration-handoff/reader-integration + 候选/状态/服务阶段/内审 1–8/证据）全部读取，其声明的边界与实现一致，无把占位/替身说成产品能力之处。

## 5. 历史意见逐项独立复核（本人结论，不沿用内审 closed）

| 项 | 独立复核证据（本人源码/运行） | 结论 |
| --- | --- | --- |
| R1-01 保存身份丢失 | QueryPage.tsx:61,495–514,540–555（SavedQuery/ID 回填/更新 ID 一致/generation+token 隔离）；authoring 测试 #6；SSR | 已关闭 |
| R1-02 同项目非查询任务可取消 | results.ts:101–114（validateV2('job')+capability+project）；QueryPage.tsx:145–147,585–601,613–615（此前结果标注）；results 测试 #6、reader 测试 #10、SSR 探针 | 已关闭 |
| R5-01 ACK 后重读提前释放 cancelBusy | reader.ts:369,418,422–424（try 内 await refresh，finally 释放）；reader 测试 "holds the cancel single-flight guard…" | 已关闭 |
| R5-02 空页丢锚 | reader.ts:78,237,294–304（仅非空行更新锚，空页保留）；测试 10→空→5 拒 / 11 收 | 已关闭 |
| R5-03 ACK 版本下限丢失 | reader.ts:79,412–415,188–190,136,166,329/338,384（floor 跨刷新/通知/取消前查）；测试 "keeps the ACK version floor…" | 已关闭 |
| R5-04 trim 改写原文 | reader.ts:34–38（仅非空检查）、结果原样入快照；测试 "preserves the exact actual execution text…" | 已关闭 |
| R6-01 INVALID_REQUEST params={} | reader.ts:57–63（params:{field} 批准枚举）+ 各失败路径分类 + catch 固定 internalError；测试 #3/#7/#9 | 已关闭 |
| 同版本矛盾/终态重开 | reader.ts:177–186（compatibleJob）；测试 #23（v4 同版本 cancelled 拒、v6 跳跃收、v7 重开拒） | 已关闭 |
| 同数量错义反例 | `test_equal_count_wrong_semantics_is_not_the_expected_answer`（完整答案 A01≠A02 且行数相等）；本人 V3 实跑通过并读 G-base 印证 | 已关闭 |
| 总控 R1 原件可恢复性 | 本人独立解包 37/37 成员逐字节全等（见第 2 节） | 已关闭 |

内审 1–8 全文已读；其"通过"仅按各自固定 SHA 适用，本人未将其当作本轮结论依据。

## 6. 本轮新发现（均 P3，不阻断 S1）

1. **[P3] Python/TS 对 draft `name`/`sparql` 的最大长度检查基准不一致（原文 vs 去空格后）**。`packages/engine/src/ontolearn_engine/query_service/drafts.py:116-117` 对原始串检查 ≤128/≤65536 后再 strip；`apps/desktop/src/renderer/src/query/draft.ts:57-59` zod `.trim()` 先变换后校验（≤128/≤65536 作用于去空格后）。触发：名称 130 字符且尾部 10 个空格——TS 通过、Python `validate_draft` 拒绝。影响：未来 T01 集成时 UI 已通过的边界草稿会在引擎侧被拒（fail-closed，无安全影响），仅边界值；digest 归一化两側一致（均 trim）。建议：统一检查顺序（两侧都按 trim 后或都按原文）。
2. **[P3] CSV 公式防护对负数数值单元格加 `'` 前缀**。`apps/desktop/src/renderer/src/query/results.ts:91` 的 `/^[\s]*[=+\-@]/u` 使 `String(-5)="-5"` 命中 `-`，导出为 `'-5`。这是标准防公式取舍（安全正确、仅当前页 ≤200 行），但负数字段在部分表格软件中显示前缀/按文本处理。建议：未来真实列类型元数据接入后对数值列豁免 `-`。
3. **[P3] 可视字段 >16 仅在"生成"时以通用提示失败**。`QueryPage.tsx:229-245` 字段复选无 16 上限禁用（条件在 :412 有 32 上限禁用）；超限时 :110-118 经 `visualSchema` 拒绝并显示通用"无法生成查询"。fail-closed、无安全影响，仅 UX。建议：超限时禁用复选或给定向提示。

观察项（不计发现）：`acceptPage` 对 columns 仅查类型与 ≤128（results.ts:54），非空下限由 `presentationSchema`（min 1）在 reader 路径保证；QueryPage 直连 `props.result.columns` 路径未重复 min-1（未来 adapter 契约已含），集成时应保持该下限。`read()` 将缺 authority/项目不匹配归 `params`（reader.ts:211-221），属批准枚举内的合理归类，非缺陷。

## 7. 审前/审后冻结一致性

审后复测（2026-10-22 23:55 +08）：HEAD 仍 `9a4dfc8f…`；`git status` 仍仅 ` M AGENTS.md`（SHA `de15f6ce…` 未变）+ 两个流程目录未跟踪；33 项产品 blob 与工作树复核 0 偏差；完整 diff 复现 `777ef6d5…`；两锁文件哈希未变；本方运行产物仅写入 ignored 的 `test-results/t04-review-runtime/zcode/` 与常规构建产物。源码/测试/配置/依赖/验收/Git 状态全程只读，无 add/commit/push/checkout/reset。

## 8. 未验边界与父缺口（本报告不证明）

真实 `query.execute`/项目内只读与外联拒绝（SERVICE/FROM/更新/非 SELECT-ASK）、真实 Q-01/02/O-01 业务联验、真实分页 cursor 发行/过期/取消/历史输入、T01 原子保存/preview/confirm/commit/CAS/恢复/撤销/过期、T08 真实模型草稿与工具闭环、ASK 与真实 RDF term/列元数据及适用局部关系图、App/preload 实际挂载、浏览器交互/CSP/真实下载、T10 跨设备、Windows/macOS 平台、真人验收、父 57 P0/跨模块/发布门，以及指定双审通过、push/PR attach/实际 CI/正常合并/远端核验——全部未由本 S1 或本轮验证证明。SSR/合成 transport/RDFLib 互操作与普通受控 worker 回归均不冒充真实业务 IPC/Store/App/平台验收。

## 9. 结论与声明

对登记的同版完整 T04-S1（33 项固定输入、S1-A/B/C/D 全部组件、其登记的有界验收）：**通过**。理由：全部产品输入与登记身份逐字节核验一致；实现与批准 5f 契约/架构不变量（本地优先、渲染端隔离、确定性/Agent 解耦、错误受限、无第二可变源/执行器/公共 schema）无冲突；8 项历史意见独立确认关闭；本轮 4 组验证真实 exit 0 且与登记终态逐项吻合；新发现仅 3 项 P3 边界一致性/UX 问题，建议由唯一 owner 在后续候选中处置（处置后按规则走必要验证与双方同版新完整审，若届时实现有变）。

本结论：仅为本方（ZCode GLM-5.3/最高/yolo）对 S1 的独立判断，不代判另一方；不授权 push/PR/CI/merge；不改变父 T04/产品未完成状态；不构成对第八节任何未验边界的通过。
