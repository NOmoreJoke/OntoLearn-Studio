# T04-S1 修复候选 5070004 · minimax M3.1-Flash / xhigh 完整独立审查报告

2026-10-23。本方为指定审者之一（MiniMax Code，M3.1-Flash / xhigh / 始终授权），对固定候选
`5070004ec8e3219bea33960bd88f57f1976e9cf8` 做**全新完整独立审查**。旧 554 的双方双 Pass
**不继承**：旧结论仅作为历史意见来源被逐条重新复判，本报告不引用其通过结论。

---

## 0. 结论先行

**对固定候选 5070004 的完整 T04-S1 有界范围：通过。**

依据（本方独立实测，非采信任何自述）：

1. 本轮完整输入 136 行 / 26243 B / SHA-256 `e35e6fd38c5ae8808bad1f8bb9d8a67b5fd4333b039d0088d3bba9b527647cb2`
   逐行实读到底；与仓库内 `docs/reviews/T04/p3-repair/launch/full-minimax-input.md` **逐字节相同**。
2. 唯一工作树、detached HEAD、固定 product/base、批准基线与 42 项产品文件 **42/42 四路逐字一致**
   （manifest sha / manifest bytes / HEAD blob / worktree 文件），HEAD 与 product 的产品字节**完全相同**。
3. base→product 全量 binary diff 独立复现为 **256242 B / SHA-256 `27c090fc00cd6d1a851695551c2d5e4e9714d9845b9d5f3ee91ae51f9995b030`**。
4. 本方实际执行：`npm run check` **exit 0**（TS 18 文件 / 719 项、Python 1167 项、lint/格式/类型/构建/Ruff 全通过）；
   静态 SSR **exit 0 / 14 项**；真实组件 DOM **exit 0 / 5 情景**（Chrome 155.0.8059.85 headless/offline，requests 与 pageErrors 均为 0）。
5. D1 的跨语言边界以本方自建探针逐例比对：**20/20 fixture 用例 + 60/60 边缘空白 + 孤立代理项，两语言接受集完全一致**（allAgree=true）。
6. 四个 P3（D1/D2/D3/D4）经源码差分与实际运行**独立确认已修复**；10 项历史结论**逐项独立确认关闭**；
   第 11 项（T09 provenance）由旧轮的"部分可核"在本轮**升级为可逐字节独立复验**。
7. 本轮新发现 **6 项**：1 项 P3（环境配方可复现性）、2 项 P3（文档定位）、2 项承继未修 P3 观察、1 项未决语义观察。
   **无 P1/P2**；无假执行、假结果、第二可变源、共享越权、未批准依赖或渲染端隔离违规。

**真实边界（本结论不覆盖）**：完整父 T04 仍待真实 `query.execute`、项目内只读与外联拒绝、完整 Q-01/02、
分页/游标/时限/取消/历史、T01 preview/confirm/commit 与恢复/撤销/过期、T08 真实模型与工具闭环、
ASK/RDF term 与实际执行元数据及适用局部关系图、O-01「未记录」语义、App/T10、两 OS、真人、CI/合并/远端、
以及全部父 P0 与跨模块门。**本报告不构成父验收通过，也不把 S1 通过写成父功能完成。**

本报告不代判另一指定审者，不授权 push/PR/merge，不创建 Goal，不发外部消息，未读取另一方本轮任何材料。

---

## 1. 任务来源、实际设置与证据

| 项 | 实际值 | 来源 |
| --- | --- | --- |
| 审者 | minimax（MiniMax Code） | 本任务运行时 |
| session | `mvs_be9afd3ec94f4d05935086be63c127b7` | 运行时 `session get (me)`；操作者 UI 快照 `ui/copied-session-id.ax.txt` 同值 |
| 任务标题 | T04-S1 候选 full-minimax-input.md 全 42 项独立审查 | 运行时 + UI 快照 `ui/after-submit.ax.txt` |
| effective_model | `minimax/MiniMax-M3.1-Flash`（variant `thinking`） | 运行时 `session get (me)` 读回 |
| thinking effort | `xhigh` | 运行时 `session get (me)`；UI 按钮「选择模型 · M3.1-Flash（订阅限免） · xhigh」 |
| 权限模式 | **始终授权**（Full access / bypassPermissions） | 本任务 UI 快照 `ui/after-submit.ax.txt` 元素 1054 |
| turn id | **未取得** | 运行时未向审者暴露 turn 标识；不编造 |
| 正文附件 | `full-minimax-input.md`，MD · 25.6 KB，136 行 | UI 附件 chip + 实读 |
| 附件 sha256 | `e35e6fd38c5ae8808bad1f8bb9d8a67b5fd4333b039d0088d3bba9b527647cb2` | 本方 Read 前置校验 |
| 附件实读 | 136 行全部读完（两次有界 Read：1–112、113–136），无截断、无摘要替代 | 本方 Read |

- 用户级默认 `permissionMode: bypassPermissions`（`/Users/kyle/.minimax/config.yaml:107`）**仅作参考**，
  未被当成本任务会话级证明；会话级证明取自本任务 UI 快照。
- 本方设置收据：`test-results/t04-review-runtime/minimax/owner-task-settings.json`
  （含 reviewer 自有读回与一份**覆盖事件**记录，见 §10 N-7）。
- `test-results/t04-review-runtime/minimax/operator-deployment.json`（SHA-256 `530ad00f…c89c8`）声明
  `taskId=null / actualSettingsReadback=false / bodySubmitted=false / guiLeaseGranted=false`——
  该文件写入于**提交前**时刻；提交后事实以本报告 §1 与 UI 快照为准。其
  `actualReviewHead / fixedProduct / approvedCommonBase / branch / gitStatusShort / protectedGuideSHA256 /
  fullInput{bytes,sha256}` 与本方独立实测**逐项一致**。

---

## 2. 审查环境、身份与基线（审查前 / 审查后）

| 项 | 审查前 | 审查后 | 结论 |
| --- | --- | --- | --- |
| `pwd` | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-5070004` | 同左 | ✅ 与指定唯一工作树一致 |
| branch | detached（`git branch --show-current` 为空） | detached | ✅ |
| `git rev-parse HEAD` | `f2102f0738706d7ed29907ac84f10ad0a506555a` | 同左 | ✅ 与指定 review HEAD `f2102f07` 一致 |
| `git status --short` | ` M AGENTS.md` | 同左 | ✅ 仅保护指南未暂存 M，无其他改动 |
| 固定 product | `5070004ec8e3219bea33960bd88f57f1976e9cf8` | 同左 | ✅ |
| 批准共享基线 | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 同左 | ✅ |
| AGENTS.md SHA-256 | `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | 同左 | ✅ 未暂存、未格式化、未纳入提交 |

**HEAD 与 product 的关系**：`git log 5070004..HEAD` 仅 **1 个流程提交** `f2102f07 docs: prepare complete T04 repaired-candidate reviews`；
`git diff --name-status 5070004 HEAD` 显示新增 **25 个文件全部位于 `docs/reviews/T04/p3-repair/launch/`** 与
`docs/reviews/T04/p3-repair/{post-freeze-review,preparation-audit}.md`，**无一为产品文件**。
本方另行对 42 项产品文件在 HEAD 上重算 blob SHA-256：**42/42 与 product 完全相同**——
因此 HEAD 后的流程提交**未改变任何产品字节**，可安全按固定 507 判定。

**本方写面**：`test-results/t04-review-runtime/minimax/**`（raw/metadata/tmp/cache/counterexamples/history）、
`test-results/t04-p3-repair/browser/review-minimax/**`（唯一命名探针产物）、
`docs/reviews/T04/round-2/minimax-m31flash.md`（本报告）。
**未**修改任何产品/测试/fixture/依赖/配置/验收，未 stage、提交、切分支、push、PR、merge。
`package.json` 与 `package-lock.json` **零改动**（`git diff --stat` 为空）。

---

## 3. 输入、附件与固定身份核验

| 核验对象 | 本方实测 | 声明值 | 结果 |
| --- | --- | --- | --- |
| 附件 bytes | 26243 | 26243 | ✅ |
| 附件 SHA-256 | `e35e6fd38c5ae8808bad1f8bb9d8a67b5fd4333b039d0088d3bba9b527647cb2` | 同 | ✅ |
| 附件行数 | 136 | 136 | ✅ |
| 附件 vs 仓库副本 | `diff` 无差异 | 同源 | ✅ 逐字节相同 |
| base→product binary diff | 256242 B / `27c090fc…f9995b030` | 同 | ✅ 独立复现 |
| `product-manifest.json` files | 42 | 42 | ✅ |
| 42 项 × 四路（sha / bytes / HEAD blob / worktree） | 42/42 | 42/42 | ✅ 无失配 |
| `candidate-files.json` files | 22（runtime/test/fixture/probe 子集） | 22 | ✅ 与 42 项 manifest 完全一致（子集） |
| 历史归档 `prior-554-review-history.tar.gz` | 373621 B / `f57050ca…8c537`；成员 71 | 同 | ✅ 逐成员 bytes+sha 全等 |
| `historical-files.json` 71 项 vs 解包副本 | 71/71 | 71 | ✅ |
| 总控 37 raw 归档 `raw-logs-554ec89.tar.gz` | 6081 B / `c17c2595…4865`；成员 37；原始字节 61602 | 同 | ✅ 37/37 bytes+sha 全等 |
| T09 固定提交 | `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` | 同 | ✅ |
| T09 manifest | `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` | 同 | ✅ |
| T09 provenance 归档 | 19 成员（17 原件＋PRD＋manifest） | 同 | ✅ 19/19 与固定 873c8c0 blob **逐字节相同** |

---

## 4. 42 项产品文件逐字核验

本方对 `product-manifest.json` 的 42 项逐项执行四路比对
（manifest sha256 / manifest bytes / `git cat-file blob 5070004:<path>` / `git cat-file blob HEAD:<path>` / worktree 实际文件），
**42/42 全部一致，零失配**。42 项清单**未**被 `candidate-files.json` 的 22 项子集替代，
本方亦**未**只审四 P3 或 UI/reader/某单一 stage。

已**逐字读完**（或经固定 Git blob 逐字节读取等价的原字节）的 42 项：
5 个 renderer 源码（`QueryPage.tsx` / `draft.ts` / `reader.ts` / `results.ts` / `query.css`）、
2 个引擎源码（`query_service/__init__.py` / `drafts.py`）、3 个测试文件（2 TS + 1 Python，含 2 个新 fixture 的 Python 侧）、
7 个 fixture（`draft-boundaries.json` / `authoring-case.json` / `p3-interaction.tsx` / approved-baseline 5 份）、
2 个探针（`ssr-probe.mjs` / `p3-interaction-probe.mjs`）、
13 份文档（`acceptance.md` / `status.md` / `integration-handoff.md` / `reader-integration.md` / `p3-repair-plan.md` /
`p3-repair/{plan-review,implementation-review}.md` / `internal-candidate.md` / `internal-review-1..7.md` /
`evidence/{final-verification,verification-summary}.json` / `p3-repair/{candidate-files.json,verification.json}`）、
1 个归档包（`owner-verification-raw.tar.gz`，51 成员）。

---

## 5. 已读完整范围（需求侧）

- **PRD V0.6**（`docs/prd/PRD-本体学习与落地Agent工作台.md`，1255 行）相关条款逐字读：
  **FR-006**（数据层次与结果失效）、**FR-400**（多种查询入口）、**FR-401**（透明性与数据范围）、
  **FR-402**（本地只读与网络限制）、**FR-403**（结果与空结果解释）、**FR-404**（查询保存与复用）、
  **附录 C**（MVP 能力矩阵）、**附录 D**（D.1 结果状态、D.2 依赖与失效表）、
  **附录 G**（G.1 映射与身份、G.2 查询/推理组合：**Q-01、Q-02、O-01**）、
  **第 11 节**（指标与评估）、**第 12 节**（12.1–12.5 端到端验收）。
- 现行政策全文三份（`current-desktop-policy.md` 3160 B / `current-permissions.md` 4462 B /
  `current-section9.md` 4937 B）**逐字嵌入本轮输入正文**（本方以字符串包含判定复核，均为 True）。
- `current-agents.md`（15147 B）**与本树 AGENTS.md 逐字节相同**，SHA-256 `de15f6ce…a5c8c4`。
- 历史：`round-1` 双方原报告、`verification-and-history-index.md`、`owner-disposition-20261023.md`、
  两方 input-read-proof、`internal-review-1..8.md`、实际启动/创建/收件/终态 JSON（71 项归档内）。
- 过程补充：`post-freeze-review.md`、`preparation-audit.md`、`p3-repair/verification.json`（25 命令 + 10 浏览器产物 + 9 项首失败处置）。

---

## 6. 本轮实际执行的验证（完整 argv / cwd / UTC 起止 / 真实 exit / raw 与 SHA）

全部经本树 `docs/reviews/T04/p3-repair/launch/run-review-command.py` 执行（唯一标签、拒绝覆盖既有证据、
自动隔离 `npm_config_cache`/`UV_CACHE_DIR`/`TMPDIR`）。**首失败全部保留，未删除、未改写、未筛绿。**

| 标签 | argv | exit | raw SHA-256 | 结论 |
| --- | --- | --- | --- | --- |
| `d1-parity-ts-attempt1`（工具首调用失败） | `python3 …/run-review-command.py d1-parity-ts-attempt1 node …/d1-parity.mjs` | **1** | 见 `raw/d1-parity-ts-attempt1.toolcall-failure.log`（SHA `0831821e…5ea75`） | **首失败**：系统 `python3` 为 3.9.6，`from datetime import UTC` 失败。改用本树 `.venv/bin/python3`（3.12.12）后解决，**未修改该工具** |
| `d1-parity-ts`（首失败后修正探针） | `node …/counterexamples/d1-parity.mjs` | 0 | `f1e863e9…8cdde` | TS 侧实测（探针自身路径层级写错致 ERR_MODULE_NOT_FOUND，修正后通过） |
| `d1-parity-py` | `.venv/bin/python3 …/counterexamples/d1-parity.py` | 0 | `ea650c0a…c725a` | Python 侧实测 |
| `d1-parity-compare`（首失败） | `.venv/bin/python3 …/d1-parity-compare.py` | **1** | `metadata/d1-parity-compare.json` | **首失败**：TS/PY 边缘键大小写不一致致 KeyError |
| `d1-parity-compare2` | 同上 | 0 | `metadata/d1-parity-compare2.json` | 规范化键后逐例比对：`allAgree=true` |
| **`full-check`** | `npm run check` | **1** | `10699e2c…360ad` | **首失败（真实）**：lint/format/typecheck **通过**，`npm test` 启动即失败：`Cannot find native binding` / `Cannot find module '@rolldown/binding-wasm32-wasi'` |
| `rolldown-binding-pack` | `npm pack @rolldown/binding-darwin-arm64@1.2.14 --pack-destination …` | 0 | `8214f7bd…9b4d` | 环境修复步骤 1（不改产品/锁文件） |
| `rolldown-binding-install` | `bash -c "mkdir -p node_modules/@rolldown/binding-darwin-arm64 && tar -xzf … --strip-components=1"` | 0 | `58b7fd0a…5e62d1` | 环境修复步骤 2 |
| **`full-check-after-binding-repair`** | `npm run check` | **0** | `b1e43731…433622` | **TS 18 文件 / 719 项、Python 1167 项、lint/格式/类型/构建/Ruff 全通过** |
| `ssr` | `node docs/iterations/T04/ssr-probe.mjs` | 0 | `f730e85970c4fff87784f8d377da18f50da85de9487a4a0080fedc38a0f80874` | 14 项静态检查全过；**与历史登记的 SSR 最终 raw 逐字节相同** |
| `component` | `node docs/iterations/T04/p3-interaction-probe.mjs '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' review-minimax` | 0 | `61da5291…fede0` | 5/5 情景；Chrome 155.0.8059.85 headless/offline；`requests: []`、`pageErrors: []` |

**本方反例探针（写在 `test-results/t04-review-runtime/minimax/counterexamples/`，未污染产品树）**：

- `d1-parity.mjs` / `d1-parity.py` / `d1-parity-compare.py`：以**同一** `tests/fixtures/query/draft-boundaries.json`
  分别驱动 TS `draftSchema` 与 Python `validate_draft`，逐例比较接受/拒绝与规范化结果。
  **结果：20/20 用例一致、60/60 边缘空白一致、孤立代理项一致、description 4096/4097 边界一致，`allAgree=true`**。
- 附带实证：本树 `zod@4.6.7` 的 `z.string().max()` **按码点计数**（`max(4)` 接受 4 个 emoji＝8 个 UTF-16 单元）。
  故 TS 侧 `description/capabilityQuestion/label/language/literal-value` 用 `.max()`（码点）与 Python `_text()`（码点）一致；
  而 name/SPARQL 必须用显式 `s.length`（UTF-16）才能与 Python 的 UTF-16 检查对齐——**产品实现正是如此**，输入中
  「当前 Zod max 内部按码点，所以显式 s.length」的判断经本方独立实证成立。

---

## 7. S1 清单逐组独立审查结论

### 7.1 Python query_service 与 TS draft

| 要求 | 本方核对位置 | 结论 |
| --- | --- | --- |
| 离线告警模板 | `draft.ts:122-146` `alarmTemplate`；`authoring-case.json` 固定词汇/条件/SPARQL 三方一致 | ✅ |
| 对象/返回字段/条件编译 | `draft.ts:98-120` / `drafts.py:83-128`，生成文本逐字节相同 | ✅ |
| 名称/说明/SPARQL/范围/关联问题/source | `draft.ts:71-81` / `drafts.py:131-145`，键集 exact、scope/source 枚举固定 | ✅ |
| IRI/语言/datatype/literal 序列化安全与完整值 | `draft.ts:83-97` / `drafts.py:60-80`；JSON 短转义对齐 SPARQL ECHAR/UCHAR；控制符与 DEL 均转义；`serialize_term` 逐字节对齐 | ✅ |
| 边界/异常/类型 | 孤立代理项、非有限数、非法对象、非字符串列头一律拒绝 | ✅ |
| 严格 shape 及孤立代理项拒绝 | 全链路 `.strict()` / `_object()` exact 键集 | ✅ |
| 不借编写激活执行、授权、第二公共 schema/writer/Store | `drafts.py` 无执行/IO/网络；`save_intent` 仅返回私有意图（family/id/expectedProjectRevision/draftDigest/value），docstring 明示非提交标记 | ✅ |
| 两语言共用 fixture（含孤立代理项） | `draft-boundaries.json` 同时被 TS 与 Python 测试消费；本方探针另证接受集一致 | ✅ |

### 7.2 D1（长度/trim 口径）

实现即「原串先按 UTF-16 code units 限 128/65536 → 再按固定 30 字符去边缘空白 → 拒空 → 内部不变」
（`draft.ts:55-70` / `drafts.py:33-48`）。固定并集 = Python 29 空白 + U+FEFF = **30 字符**，两侧集合逐字符一致。
description/question/RDF 上限未变。**本方以 20 fixture 用例 + 60 边缘码点 + 孤立代理项逐例比对，两语言接受集完全一致（allAgree=true）**——
不是"数量相同"，而是**逐例接受/拒绝与规范化结果相同**。收紧面确认：仅缩小接受面，未提高任何上限。

### 7.3 QueryPage / CSS

模板、基础可视条件/字段、SPARQL 与 model 草稿可见载入、显式范围与当前/历史输入、结果身份俱在；
源字符串全部经 React 文本转义（无 `dangerouslySetInnerHTML`，探针实测 `<script>alert(1)</script>` 输出为 `&lt;script&gt;…`）；
`null` 显示「未记录」；空页与后续页分别文案；5 条可操作检查方向；「仅展示当前页，最多 200 行」；
无示例结果（离线态无结果时明确提示「模板和草稿不会生成示例结果」）。
**200 行上限经本方核实由批准契约强制**：`packages/contracts/v2/schema.json` 的 `page.rows` 为 `minItems:0, maxItems:200`，
`additionalProperties:false`，经 `validateV2('page')` 在 `acceptPage` 内生效——本方据此**推翻**了自己最初"显示层无行数兜底"的疑点，不计入发现。
CSS 无 `unsafe-inline`/`unsafe-eval`/外部资源/URL 引用，类名与组件用法一一对应。

### 7.4 D3（可视字段 16 上限）

最新 state 防重复与超 16（函数式 `setVisual` 内判定 `selected || length>=16`）；达 16 后**只禁未选项**、已选项可取消；
显示「已选 n/16」；`condition` 32 上限独立保持（`visualSchema` max(32) 与按钮 `disabled`）。

### 7.5 D4（visual 重置与生成门）

新建、成功载入 saved、成功载入 model 三条路径均 `setVisual(emptyVisual())` 清空 class/fields/conditions；
生成按钮取**真实** `visualSchema.safeParse(visual).success` 并禁用 + 给检查提示；
非法 RDF 类型切换只改 `visual`、**不改草稿**，修正后才可生成；不猜反解任意 SPARQL；
保存身份与 `documentGeneration` 规则未改；模板仍显式填自己的 builder。

### 7.6 保存 / 复用

同名不同定义以不同 `definitionId` 区分（`savedQuerySchema` strict + `definitionIdSchema`）；
成功保存回填**真实** ID（由回调返回并经 `definitionIdSchema.parse` 校验）；更新时 ID 必须一致否则抛错；
`request` token + `documentGeneration` 双闸拒绝迟到回执；`editRevision` 变化时提示「当前编辑已变化」；
新建/切项目/载入/卸载推进 generation；**无真实 adapter 时保存/执行按钮禁用**，并明示「项目事务服务尚未接入，草稿尚未持久化」；
renderer 不发行 ID、不直接触达 Store；正式 CAS/preview/confirm/commit 仍缺父接线。

### 7.7 results / reader

直接复用批准 `validateV2('result'/'page'/'job')`、`TaskView`/`TaskUpdate` 与四个命名 bridge 方法，未扩大 bridge、未公开新协议；
完整 project/job/result/snapshot/scope/params 身份贯穿；generation/input 切换拒迟到；
**实际已执行 SPARQL 原文保留**（`executedSparql` 仅做非空判定，不 trim 改写）；仅消费真实发行的 cursor 并核绑定
（`nextPage` 只接受当前页 `nextCursor`，不自造 OFFSET 游标）；页内/跨空页稳定排序与有界锚（ordinal+rowId，空页保留锚）；
回收载荷保留身份（evicted → ready 但 page=null，不再取缺失载荷）。

### 7.8 任务 / 取消 / 错误

仅同项目 `query.execute`；single-flight 覆盖 ACK 后实际 job 重读全生命周期；ACK 与真实终态分离
（ACK 只置 `cancelRequested`，不改成 cancelled）；已知版本下限跨刷新/通知/取消前查询保留；
拒同版本矛盾与已观察终态重开，允许合法跳跃观测；旧结果与当前 job 区分（jobId 不同则标「此前查询结果」）。
错误面固定受限：仅 `INVALID_REQUEST` + `params.field ∈ {identity, params, cursor}`；原始 bridge 异常一律固定
`INTERNAL_ERROR`（测试断言 `PRIVATE_PATH` 不出现在快照）。无假结果/执行、无第二可变权威、无共享抢写、无未批准依赖。

### 7.9 D2（CSV）

列头必为 string；仅字符串单元格（含列头）沿用公式与前导控制字符防护；有限 number/boolean 输出规范文本；
`null` 为空；引号双写、CRLF 行结束；非有限数值与对象/数组等非法运行时类型**拒绝**。
**字符串负数与实际负数语义分离**已被本方确认：`-5`（数值）导出为 `"-5"`，`"-5"`（字符串）导出为 `"'-5"`；
`-0` 输出 `"0"`（规范数值文本，非字符串分支，不加前缀）；`1e-7` 输出 `"1e-7"`；`'=SUM(1)'`、`" +SUM(1)"`、`"\t=1"`、`"\rline"` 均按字符串防护加前缀；`a,"b"\n` 双写引号安全；201 行拒绝。

### 7.10 全部 42 项、测试/fixture/SSR/DOM probe

42/42 已逐字审（§4）；TS 18/719 与 Python 1167 全部通过；fixture 为跨语言共享且被两侧真实消费；
SSR 14 项与 DOM 5 情景本方实跑通过；**测试通过不替代源码审查**，manifest/hash 自述未被当逐字核验。

---

## 8. 历史项逐项独立复判（不沿用旧 closed）

| 项 | 原问题 | 本方独立复核结论 | 本方证据（实际文件:行） |
| --- | --- | --- | --- |
| **R1-01** | 复用保存丢失 definitionId；新建不返回真实 ID | **已关闭** | `draft.ts:158-164` strict `savedQuerySchema`；`QueryPage.tsx:559-574` 载入保身份；`QueryPage.tsx:505-527` 回调返回真实 ID→`definitionIdSchema.parse`→不一致即抛错→`request`/`documentGeneration` 双闸；`QueryPage.tsx:78-82,83-101` editRevision 提示 |
| **R1-02** | 同项目非 query 任务被显示并可取消 | **已关闭** | `results.ts:108-121` `queryJob` 复用 `validateV2('job')` + 同项目 + `capability==='query.execute'`，否则 `undefined`；`QueryPage.tsx:148-151,580-621` 任务区与取消入口据此渲染；`QueryPage.tsx:632-634` 不同 jobId 标「此前查询结果」 |
| **R5-01** | ACK 后重读未完成即释放 cancelBusy | **已关闭** | `reader.ts:396-424` `cancelBusy` 仅在 `finally` 且 `current()` 成立时释放，`return await this.refreshJob(jobId)` 覆盖 ACK 后全生命周期；`reader.ts:360-368` 双闸防重入 |
| **R5-02** | 空页丢失最后非空排序锚 | **已关闭** | `reader.ts:303-304` 仅在有行时更新锚；`reader.ts:294-302` 跨页回退/自循环 cursor 拒绝；`reader.ts:209,116,434` 新读/新绑定/释放清锚 |
| **R5-03** | ACK 版本下限在后续路径丢失 | **已关闭** | `reader.ts:79,412-415` `cancelFloor`；`reader.ts:188-190` `minimumJobVersion()` 供 `reader.ts:136,167,338,384` 共用；`reader.ts:346,118` 切 job/新绑定清理 |
| **R5-04** | trim 改写实际 SPARQL 原文 | **已关闭** | `reader.ts:34-38` `executedSparql` 仅 trim 判非空、保留原串；`reader.ts:271-278,305-315` 原样入快照 |
| **R6-01** | INVALID_REQUEST `params={}` 被降级 internal | **已关闭** | `reader.ts:57-63` 仅用批准枚举 `identity/params/cursor` 并写 `params.field`；`reader.ts:260,266,292,302` 分别归类；`reader.ts:317-319,350-353,419-421` 原始异常固定 internal；`t04-query-reader.test.ts:257-269` 断言不泄漏 |
| **同版本矛盾 / 已观察终态重开** | 须拒绝矛盾与终态重开，不得误拒合法跳跃 | **已关闭** | `reader.ts:177-186` `compatibleJob()`：同版本异状态拒、终态异状态拒、版本跳跃接受；**本方确认未使用相邻状态转换约束** |
| **同数量错义反例** | A01 与 A02 行数相同必须比完整答案 | **已关闭** | `test_query_service_approved_baseline.py:86-95` `assert wrong_rows != correct_rows` 且 `len` 相等；本方在隔离沙箱用 rdflib 独立复算：正确→`[["…alarm/A01"]]`，错误→`[["…alarm/A02"]]`，Closed 变体→`[]` |
| **总控 R1 原件可恢复性** | 37 raw 仅 ignored，需无损归档 | **已关闭** | 本方本轮独立解包 `raw-logs-554ec89.tar.gz`：**37/37 成员 bytes+sha 全等，原始字节合计 61602**，与索引声明一致 |
| **T09 固定输入 provenance** | 17 项与 PRD 来源 hash | **由旧轮「部分可核」升级为可逐字节独立复验** | 本轮 `approved-t09-provenance-inputs.tar.gz` 提供 19 成员：**19/19 与固定 `873c8c0` blob 逐字节相同**，manifest sha 匹配；产品实际**只消费 3 副本**（`test_query_service_approved_baseline.py:29,39,70,88`）+ manifest 作哈希校验器，其余 **14 项在产品树中无副本、无读取** |

**关于旧 M 报告「11 项历史 closed」的表述**：其 §5 实际表为 **10 行「已关闭」＋1 行
「T09 provenance｜部分可核，其余仅记录 ⚠️」**，结论节第 5 条亦自述「共 10 项历史结论」。
本方按**实际表**记为 **10 closed ＋ 1 partial**，并按本轮新证据把该 partial 项升级为可独立复验，
**不把 partial 抹平为 closed**。

**关于旧 Z 报告的 columns 非空下限观察**：该观察存在**事实误读**——`reader.ts:33` 的
`columns: z.array(z.string().min(1).max(128)).max(64)` 中 `.min(1)` 只约束**每个列名字符串**，数组本身仍允许 `[]`。
本方**不**复述该错误观察为已有保证；本轮亦**未**改 `reader.ts`（554→507 差分中 `reader.ts` 不在改动集内），
零列与 ASK 的父元数据语义**仍未定**，见 §10 N-5。

---

## 9. 四个 P3 逐项独立复判

| 编号 | 来源 | 旧问题 | 本轮实现（实际差分 `554ec89 → 5070004`） | 本方独立结论 |
| --- | --- | --- | --- | --- |
| **D1** | Z-P3-1 / M-F1 | Python 按原串判长后 strip，TS 先 trim 后判长，边界口径分歧 | `draft.ts` 新增 `draftText()`：显式 `s.length`（UTF-16）判长 → 固定 30 字符并集 trim → 拒空；`drafts.py` 新增 `_draft_text()`：现有标量/原串检查 → UTF-16 长度 → 同并集 strip → 拒空 | **已修复并独立验证**：20/20 + 60/60 + 孤立代理项，两语言接受集逐例一致（allAgree=true） |
| **D2** | Z-P3-2 / M-F2 | CSV 公式防护误伤数值单元格（`-5` → `'-5`） | `results.ts` 改为：仅 `typeof value==='string'` 施加公式/前导控制字符防护；`null`→空；有限 number/boolean→规范文本；其余（NaN/±Infinity/undefined/对象/数组）**抛错拒绝**；并新增列头非 string 拒绝 | **已修复并独立验证**：数值/布尔/字符串三类语义分离（含 `-0`→`"0"`、`1e-7`→`"1e-7"`）；字符串防护未削弱；200 行与引号/CRLF 保持 |
| **D3** | Z-P3-3 | 字段 >16 仅在"生成"时以通用提示失败 | `QueryPage.tsx`：显示「已选 n/16」；达 16 后**只禁未选项**（已选可取消）；函数式 `setVisual` 内同时防重复与超 16；生成按钮取真实 `visualSchema` 有效性 | **已修复并独立验证**：DOM 情景 `sixteen-fields-and-reselection` 实跑通过（17 项禁用、1 项可用、计数显示、取消后可再选、生成 SPARQL 完整选择集合）；condition 32 上限独立保持 |
| **D4** | M-F3 | 新建/复用未重置 visual，可静默覆盖已载入 SPARQL | `QueryPage.tsx`：新建、成功载入 saved、成功载入 model 三处 `setVisual(emptyVisual())`；生成按钮 `disabled={!validVisual}` + 检查提示；非法 RDF 类型切换只改 visual 不改草稿；不改 definitionId/generation 规则 | **已修复并独立验证**：DOM 情景 `saved-load-clears-old-builder` / `new-query-clears-old-builder` / `model-load-clears-old-builder` / `invalid-rdf-type-blocks-generation` 实跑通过（非法切换期间原 SPARQL 文本逐字保持，修正为合法 IRI 后方可生成） |

四项 P3 均**不构成 S1 阻断**，且本轮实现未降低任何既有上限或防护。

---

## 10. 本轮新发现

### N-1（P3｜复现性）文档记载的环境配方在本机不足以跑通 `npm run check`

- **严重度**：P3（低）。**不构成 S1 阻断**——产品字节本身全部通过。
- **实际路径**：`docs/iterations/T04/acceptance.md:18`（`npm ci --ignore-scripts`）、
  `docs/reviews/T04/p3-repair/launch/setup-minimax.json`（`records[0].argv` 同配方）、
  `docs/reviews/T04/p3-repair/verification.json` → `commands[label=setup-npm-retry].argv`（同配方）。
- **具体触发**：本方按该配方安装后运行 `npm run check`：lint / format:check / typecheck **全部通过**，
  到 `npm test` 启动即失败：
  `Error: Cannot find native binding… Cannot find module '@rolldown/binding-wasm32-wasi'`，**exit 1**。
- **根因**：`package-lock.json` **含** `node_modules/@rolldown/binding-darwin-arm64` 条目，
  但 `npm ci --ignore-scripts` 触发 npm 可选依赖已知 bug（错误信息本身即引用 npm/cli#4828）跳过该平台绑定。
- **证据**：本方首失败原件 `raw/full-check.log`（exit 1，raw SHA `10699e2cbdd5a590e04f5a06d1e629472f38e7e9b51ab9e6e77aceac000360ad`），
  与修复后 `raw/full-check-after-binding-repair.log`（exit 0，raw SHA `b1e43731afba12c2b34a57cdac06c5c297fccdcfe983ac2fb69abe8434f33622`）。
  修复动作：`npm pack @rolldown/binding-darwin-arm64@1.2.14` → 解包至本方 `node_modules/@rolldown/binding-darwin-arm64`
  （锁内版本，未改 `package.json`/`package-lock.json`）。
- **影响**：独立复现者按文档无法直接跑通完整 check；owner 自述的「完整 check exit 0」在本方树上**仅在补装绑定后**复现。
  产品代码、测试断言与验收口径不受影响。
- **建议**：在 `acceptance.md` 的命令清单补一条平台绑定补装（或改用不触发该 bug 的安装方式），
  并在 `setup-minimax.json` 记录补装步骤，使后续审者首跑即可得到可比终态。

### N-2（P3｜文档定位）42 项清单内的两份证据文件描述的是更早候选

- **严重度**：P3（低，可读性/防误读）。无产品影响。
- **实际路径**：`docs/reviews/T04/evidence/final-verification.json`（`implementationCandidate=c4aa5f9c…`、
  TS 642 / Python 1082 / SSR 11）与 `docs/reviews/T04/evidence/verification-summary.json`
  （`candidate=4c17a381…`、TS 640 / Python 1080 / SSR 8）。二者**均在 42 项产品清单内**。
- **具体触发**：只读 42 项清单的读者会误以为这两份是本候选终态；本候选真实终态证据在
  `docs/reviews/T04/p3-repair/verification.json`（TS 719 / Python 1167 / SSR 14 / DOM 5）与 `docs/reviews/T04/status.md:22-26`。
- **影响**：仅文档阅读路径。两份文件按"原件保留不改写"保留原字节（符合既定做法），本方**不要求**改写其内容。
- **建议**：在 42 项清单或 `status.md` 就地加一行指向 `p3-repair/verification.json`，标明两份证据属历史候选。

### N-3（P3｜样式作用域，承继未修）`query.css` 两条选择器未限定作用域

- **实际路径**：`apps/desktop/src/renderer/src/query/query.css:76-78`（`.query-check input`）与 `:79-84`（`.query-condition`）。
- **具体触发**：二者在 `.query-workspace` 作用域之外，属全局选择器；父 App 接入同名元素时可能互相影响。
- **影响**：当前全仓无同名元素，**当前无实际冲突**。属旧轮 M 方 CSS 观察的承继项，本轮未改。
- **建议**：父 App 样式接线时一并收敛（与旧轮处置一致）。

### N-4（P3｜类型放宽，承继未修）`staleReason.code` 静态类型宽于批准枚举

- **实际路径**：`apps/desktop/src/renderer/src/query/results.ts:20`（`staleReason: { code: string; … }[]`）。
- **具体触发**：静态类型标注为 `string`，批准 schema 为固定枚举。
- **影响**：**运行时未放宽**——仍由 `validateV2('result')` 强制。仅属类型收敛建议，承继旧轮观察，本轮未改。

### N-5（观察｜未决语义，非缺陷）零列 columns 与 ASK 的父元数据语义仍未定

- **实际路径**：`apps/desktop/src/renderer/src/query/reader.ts:33`（`.min(1)` 只约束列名，数组允许 `[]`）、
  `results.ts:54`（`acceptPage` 只查列类型与 ≤128，**不**查非空下限）。
- **具体触发**：父适配器提供空列数组时，本线不会拒绝。
- **影响**：**不得**据旧 Z 报告的相关观察宣称已存在"至少一列"保证；本轮亦未决定该语义。
  按旧轮处置，零列/ASK 语义属父元数据契约待定项，须在批准约定下另行补边界验证。
- **建议**：由父适配器/查询元数据契约明确零列与 ASK 语义后，再在 `acceptPage` 或 `presentationSchema` 侧收紧并补测。

### N-6（观察｜承继，未决）载入 model 草稿不重置 `definitionId`/`documentGeneration`

- **实际路径**：`apps/desktop/src/renderer/src/query/QueryPage.tsx:536-547`（model 载入仅 `setVisual(emptyVisual())` + `update({...parsed.data, source:'model'})`），
  对比 `:548-557`（新建）与 `:559-574`（saved 载入）会推进 `documentGeneration` 并重置 `definitionId`。
- **具体触发**：已打开保存定义 X 时载入 model 草稿，随后点「保存到项目（更新 X）」会把 model 草稿写向 X。
- **影响**：**不构成假执行或假持久化**——需用户显式点击保存，按钮文案明示「更新 X」，草稿在编辑器可见；
  且旧轮处置对 D4 明确要求"不改已有 definitionId/generation/保存身份逻辑"，故本轮**不**按缺陷计。
  仅作为父接线需明确语义的观察项。
- **建议**：父接线时明确"载入 model 草稿是否应脱离当前保存身份"，再由唯一 owner 决定是否改规则。

### N-7（过程事项｜非产品缺陷）本方写入 owner-task-settings.json 时覆盖了操作者同名文件

- **实际路径**：`test-results/t04-review-runtime/minimax/owner-task-settings.json`。
- **具体触发**：本方 02:22 以 Write 写入该路径时，工具报 `overwrote existing file`；
  本方 02:11 首次列目录时该文件尚不存在，其后（约 02:13）出现，**推断为操作者写入**。
- **影响**：**仅影响本方 ignored runtime 目录内的收据文件**；产品/测试/fixture/依赖/配置/验收与 Git 状态均未因此改变
  （审查后 `git status --short` 仍仅 ` M AGENTS.md`，42 项产品 blob 复验 42/42 一致）。
- **恢复**：操作者原内容**无法**从本机运行时恢复（`/Users/kyle/.minimax/v2/sessions` 中除本 session 外无任何会话记录该路径写入）。
  本方已在该文件内写入 `incident` 段如实记录事件、时间、影响与恢复条件，并另存
  `test-results/t04-review-runtime/minimax/reviewer-task-settings-readback.json`（同内容同 SHA `d10f7762…e26a7f`）。
- **建议**：请操作者据本方文件内同口径事实复核后重新签发权威回执（内容已齐备，无需重跑任何验证）。

---

## 11. 未验证项与真实边界（本方明确不声称通过）

- **真实执行**：I05 `query.execute`、`SERVICE`/远程 `FROM`/更新/隐式外联拒绝、非 SELECT/ASK 拒绝、真实任务时限与排队、真实游标发行与过期绑定。
- **结果元数据**：实际执行文本与列名的权威来源、ASK 布尔结果约定、RDF term 类型与**适用局部关系图**（当前 cells 仅有 string/number/bool/null，无法区分 IRI 与字面量）。
- **保存事务**：T01 唯一 preview/confirm/commit、同项目与旧基线拒绝、原子失败/撤销、读取恢复与过期、真实保存身份回填。
- **历史与选择**：完整历史运行不可变、历史显式选择、结果过期原因与重跑入口的引擎侧实现。
- **模型与工具**：T08 真实自然语言草稿、工具闭环、失败离线与不伪造成功。
- **跨设备与平台**：T10 项目包跨设备复现、App 挂载、生产 CSP、下载/原生提示、Windows 11 x64 与 macOS 15 arm64、真人与发布门。
- **父需求全量**：FR-400–404、FR-006、附录 C/D/G 的 Q-01/02/O-01、第 11–12 节，以及全部父 P0 与跨模块矩阵。
  本方本轮只核到 **Q-01/Q-02 的编写互操作层**（RDFLib 标准库，非 I05 运行）；**O-01「未记录」语义未验**。
- **流程与发布**：实际 CI、两 OS 远端核验、push/PR/正常合并 develop 与远端保护原件核验、正式发布。
- **独立内审 244 组纯探针**：按 `post-freeze-review.md` 的如实记录，其为原会话内联命令、无绝对起止时间、无独立 script/raw/SHA 文件，
  **本方不将其计为持久运行原件**，本方结论不依赖它。

---

## 12. 结论与声明

对固定候选 `5070004ec8e3219bea33960bd88f57f1976e9cf8`（base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，
42 项产品文件，HEAD `f2102f07` 与 product 产品字节相同）的**完整 T04-S1 有界范围：通过**。

依据为 §3–§9 的本方独立核验与实际运行（首失败全部保留、未筛绿），非采信任何 manifest/自述。
本轮新发现 6 项，**无 P1/P2**；N-1 为环境配方可复现性，不改变产品判定，且补装后完整 check 与 owner 终态数值完全吻合
（TS 18/719、Python 1167、SSR 14、DOM 5）。

本结论仅为本方（MiniMax M3.1-Flash / xhigh / 始终授权）对固定 S1 范围的独立判断：
**不代判另一指定审者**；**不授权 push / PR / merge**；**不构成完整父 T04 或产品验收通过**；
**不关闭**任何父 P0、跨模块、两 OS、真人、CI、远端或发布门。

---

### 附：本方证据落点

- 命令收据：`test-results/t04-review-runtime/minimax/metadata/*.json`（argv / cwd / UTC 起止 / 真实 exit / raw 与 SHA）
- 原始输出：`test-results/t04-review-runtime/minimax/raw/*.log`（**含首失败**：`full-check.log`、`d1-parity-ts-attempt1.toolcall-failure.log`）
- 反例探针：`test-results/t04-review-runtime/minimax/counterexamples/{d1-parity.mjs,d1-parity.py,d1-parity-compare.py,d1-parity.ts.json,d1-parity.py.json,d1-parity.compare.json}`
- 历史档案解包：`test-results/t04-review-runtime/minimax/history/`（71 项，逐字节核验一致）
- 组件 DOM 产物：`test-results/t04-p3-repair/browser/review-minimax/`（`interaction-results.json`、`interaction-trace.zip`）
- 本方设置收据：`test-results/t04-review-runtime/minimax/owner-task-settings.json` 与 `reviewer-task-settings-readback.json`
