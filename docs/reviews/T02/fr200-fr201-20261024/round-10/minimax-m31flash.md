# T02 FR-200／FR-201 fresh R10 整候选独立工程审查报告（MiniMax／M3.1-Flash／xhigh／始终授权）

## 0. 输入回执与身份核验（先行）

本报告为**全新 R10 独立审查**，不继承 R09 任何结论、Pass 状态或意见处置结论。R09 的 ConditionalPass 仅作为**历史核对材料**被读取，不作为本轮起点。

**输入回执**

- 我已将本条完整输入（含原用户 160 项原文）全文读至最终 EOF 标记 `<!-- R10 COMPLETE INPUT EOF: 67b7bcbd / 160 original checklist items -->`。
- 我方输入文件：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261027_t02_67b7_fresh_r10_070/minimax-complete-input.md`，实测 26558B、222 行，SHA256 `e4e8e2212f759affdb78e9ede639e99289a996fff6c8249dfbc02d807b29fa50`。
- 原用户清单 `ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt` 实测 **11255B**、SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`、**末字节非 LF**（末字节实测为 `0x29` 即 `)`）。我在我方完整输入中定位该 11255B 为**精确一次**的逐字子串（offset 15228），其后紧接 `b'\n\n'` 两个分隔换行再接 EOF 标记——这两个换行**不属于原件**，与输入声明一致。我未对补 LF 文本计算字节，未把 SHA256 误作 SHA1。
- 清单条目数实测：以 `> ` 开头的引用行共 **160** 条。

**Git 身份核验（在指定唯一 cwd 内实测）**

| 项 | 输入声明 | 本人实测 | 一致 |
|---|---|---|---|
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | 同 | 是 |
| branch | `feature/weekly-t02-fr200-fr201` | 同 | 是 |
| HEAD | `67b7bcbd2d911b4a6898d837dbf20688d793e844` | 同 | 是 |
| tree | `78a6b5d5ba4ff4e8e408e8f7da95c5c719be3996` | 同 | 是 |
| sole parent | `b0c0e8d37954a3b8c2563b6068d6ca3d151a8dd1` | 同（`git rev-list --parents` 仅一个父） | 是 |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 同 | 是 |
| base→head 提交数 | 40 | 40 | 是 |
| Git 实际差异路径 | 117 | 117 | 是 |
| tracked 源叶 | 1396 | 1396 | 是 |

**身份完全吻合，未审错目录。**

**工作树脏项核对（与保护声明一致）**：`git status --porcelain` 仅三项——` M AGENTS.md`、三个未跟踪目录 `docs/reviews/T02/fr200-fr201-20261024/round-01|02|03/`（各含 minimax/zcode 两稿，共 6 文件）。index 实测为空（`git diff --cached --stat` 无输出）。这与「唯一工作树脏项是上述既有保护项」一致；我未 stage、未提交、未切分支、未 push、未触发 CI、未 merge。

**远端实测（只读 API 查询）**：PR16 `state=OPEN`、`mergedAt=null`、`headRefOid=b0c0e8d3…`、`baseRefName=develop`。`gh run list` 最近三次：40382314925（b0c0e8d3，failure）、40294180350（2b6c8a26，failure）、40252093380（9cbddf34，cancelled）。**67b7bcbd 未 push，无新 CI。** develop 本地 ref 为 `5f910b52…`，`refs/remotes/origin/develop` 亦为 `5f910b52…`；注意这与输入所述「develop=583c05c…」**不一致**——这是本地/远端 develop 指针已前移的独立事实（属其他开发线），本候选的 base 仍是 `583c05c…`，我不据此改动任何结论。

**旧引用路径失效的说明（按真实同主题原件核对）**：
- `docs/architecture/m0-review-and-update-plan-2026-10-19.md` **不存在**。真实同主题原件位于 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` 与 `docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md`，两处实测 SHA256 **均为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`**、均 35812B，内容逐字相同。我按此原件读取 S1/S2/S3/C1/B1/U1 全文。
- `docs/architecture/0003-resident-coordinator-and-jobs.md` 存在（ADR-0003）；`ADR-0002` 实际位于 `docs/iterations/I01/ADR-0002-storage.md`（AGENTS.md 中的路径正确）。`docs/architecture/` 下只有 0001 与 0003，无 ADR-0004（S3 仍是计划阶段，本候选未新增该文件）。

---

## 1. 结论先行

**整体判定：ConditionalPass（限定技术阶段，本人独立判断，未预设）。**

本轮候选 `67b7bcbd`（相对 base `583c05c` 的 40 提交／117 差异路径累计候选）在**本人亲读范围内未发现 push 前源码技术阻断**。67 的实际变更只有 4 个测试/测试辅助路径（631+／43−），不触碰生产代码、契约、CI、依赖或配置；其新增的 UI 观测辅助层我逐行读完并做了独立的行为核验，未发现会削弱断言强度或伪造成功的缺陷。

但本判定**不构成**：

- 无条件整候选 Pass；
- 完整平台验收（67 未 push，无任何新 CI）；
- merge 授权；
- 任何既有 HOLD／UNKNOWN／OPEN 的关闭；
- 完整 C1／M0／发布完成（整体合并可用仍为 **2/17**，不推进 T04）。

R09 的 ConditionalPass **不转移**到本轮。本轮是基于 67 实际内容与 40 提交累计候选的独立重判。

---

## 2. Top 10 最重要实际风险

按严重程度排序。**本候选的 67 本身未引入源码级阻断**；以下风险全部是**累计候选 base→67** 或**未来 CI／合并条件**层面，故其「是否 push 前源码阻断」列绝大多数为「否」。这一分布本身是重要事实，不凑项。

### R10-T01｜完整平台 CI 缺位，合并门禁未开
- **stableID**：R10-T01（承接 `Z08-01`／`Z F1`／`R06 Z P1`／`R06 D1`）
- **严重性**：P1（合并门禁，非源码缺陷）
- **触发**：任何 merge 动作。
- **代码/原件定位**：远端实测 PR16 head 仍为 `b0c0e8d3`；`67b7bcbd` 未 push，无 run。O067 `COMPLETION.json` 记录 CI42 run40382314925/attempt1 整体 `cancelled`，Quality `cancelled`、Windows `failure`、macOS `success`；O068 `monitor-COMPLETION.json` 记录 attempt2 Quality job 121800851119 仍 `cancelled`。
- **影响**：无法判定 67 在 Windows/Quality 的真实终态。
- **最小建议**：push 前由 ROOT 发精确票，跑完整三 job，按原 15/20 分钟预算，逐 node 核 3769 全集（PASS 或原有据条件 skip）、无失败/早停/取消/timeout/NOTRUN、全部后继步骤自身 success、Quality packaged recovery 自身 success。
- **push 前源码阻断**：否（流程门禁）。
- **类别**：未来 CI／merge 条件。

### R10-T02｜CI41 Quality C1 根因仍 UNPROVEN；67 的观测层修复不等于根因证成
- **stableID**：R10-T02（承接 `Z09-02`／`F-R09-02`／`F-R09-03`／`R06 Z P2`）
- **严重性**：P1
- **触发**：需要判断 Quality C1 `native-recovery.cjs` 失败是否已消除。
- **原件定位**：O067 `DIAGNOSIS-AND-NEXT-OPTIONS.md:16` 逐字记「已证：19PASS／3原有SKIP／2FAIL之一；该例9311ms失败于line379外层原操作回执poll」；O059 记录真实 CI41 已执行到 `native-recovery.cjs:12`（`app.isPackaged` 为 undefined 的 TypeError），而 O060/O062 容器分别止于 sandbox owner/namespace EPERM，**在原 helper require 之前**——两者不可互为证成。
- **影响**：把「平台终态已知」与「具体根因未知」混称，会让后续 merge 判断失据。
- **最小建议**：新 CI 若复现，按新增结构化栈定因并处置；不得以 67 的本地观测能力倒填旧因果。
- **push 前源码阻断**：否。
- **类别**：未证根因（独立 HOLD）。

### R10-T03｜Windows FR201 整例 180s 超时，末权威业务终态仍未知
- **stableID**：R10-T03（承接 O067 `case16`、R09 `F-R09-04`）
- **严重性**：P1
- **触发**：Windows 平台跑 `t02-fr200-fr201.spec.ts` 整例。
- **原件定位**：O067 `WINDOWS-CI42-FAILURE-FACTS.json` `case16`：`durationMs=180010`、`status=timedOut`、`error="Test timeout of180000ms exceeded"`；`DIAGNOSIS-AND-NEXT-OPTIONS.md:23` 逐字：「该例180010ms；原commit poll已成功返回（约2953.068ms）并进入reconcile分支。随后"提交版本20"断言完成；最后开始的是commit line199"当前已读版本20"断言（callsite1168），trace没有after，距AfterHooks约397.549ms。最后完整拒绝快照19／19相等，38份拒绝附件。没有22次完整事务最终链」。
- **影响**：无最终权威业务结果，也无 failure annotation；不能断言「原 poll 补丁失效」或「已修复」。
- **最小建议**：在同 host／worker／retry／预算下用有界即时记录分辨预算消耗去向，保留同 22 事务／43 拒绝／5s／180s；不拆测试、不缓存替代、不重放。
- **push 前源码阻断**：否。
- **类别**：未证根因／未知终态。

### R10-T04｜67 的 UI 观测层只覆盖 `native` 形态，其他形态 fail-closed——这是设计选择，也是覆盖面限制
- **stableID**：R10-T04（本轮本人新发现，独立编号；与 `R06 Z P6`／`R04 Z01` 的「无 ORDER BY 未确认观察」无关）
- **严重性**：P2（测试覆盖面限制，非产品缺陷）
- **触发**：被观测节点出现 shadow DOM、`aria-labelledby`、或 BUTTON 带 `role`／`aria-label` 覆盖。
- **代码定位（本人亲读全文）**：`tests/e2e/ui-observation.ts:32-41` 抛出 `'Unsupported UI observation markup'` 的六个条件（`isConnected` 为假、`aria-labelledby`、`closest('head')`、匹配 `special` 选择器、含 `special` 后代、自身 `shadowRoot`、任一后代 `shadowRoot`）；`:55-56` 抛出 `'Native UI observation role/name override'`；`:52` 抛出 `'Ambiguous or unsupported UI observation target'`（`matches.length !== 1`）；`:82` 抛出 `'Duplicate strict UI observation target'`。
- **影响**：任何依赖该 helper 的断言在这些形态下会**报错而不是误判成功**——方向是安全的（fail-closed），但真实 UI 一旦演进到该形态，用例会失败且需人工判断是产品变化还是观测限制。
- **最小建议**：在 helper 顶部注释中把「仅支持当前 native light-DOM 形态」写成显式契约并在契约变动时同步；不需要为当前候选改代码。
- **push 前源码阻断**：否。

### R10-T05｜`updateObservationSlot` 的 16KiB 上限在 base64 兜底分支下**不保证**最终字节 ≤ 16384
- **stableID**：R10-T05（本轮本人新发现，独立编号）
- **严重性**：P2（诊断元数据边界，非产品数据）
- **触发**：观测载荷大到 JSON 化后超过 16384 字节，进入 `ui-observation.ts:182-190` 的兜底分支。
- **代码定位（本人亲读全文）**：`tests/e2e/ui-observation.ts:179-190`：
  ```
  const description =
    Buffer.byteLength(text) <= 16384
      ? text
      : JSON.stringify({ ..., utf8PrefixBase64: Buffer.from(text).subarray(0, 11000).toString('base64'), ... })
  ```
  兜底分支把 11000 字节原文做 base64，base64 膨胀为 11000/3*4 ≈ 14668 字节，再加 JSON 字段与 `boundary` 字符串，整体**必然大于 16384 字节**。该分支产出后**不再做长度复核**，直接赋给 `slot.description`。
- **影响**：**不截断、不伪造成功**，仅使「16KiB 上限」这一自述在兜底路径上不成立；`description` 变成约 14.7KB+ 的诊断文本（仍受 Playwright annotation 自身限制约束，未见崩溃）。对「断言数据完整、只有诊断副本截断」这一设计意图**无损害**。
- **最小建议**：兜底分支的 base64 前缀长度改为按 `16384 - 固定字段开销` 反算（例如取 10000 或先构造后复核并再截一次），使「≤16384」在两条路径上都成立；或明确把该常量改述为「主路径上限」。
- **push 前源码阻断**：否（不改变任何断言结果，不影响产品行为）。
- **我的处置**：**保留**。证据来自本人亲读源码；未运行任何测试来验证实际输出字节。

### R10-T06｜CI Windows 分支把 `engine:check` 降级为「diagnostic」，但该 step 仍会以其退出码决定 job 成败——命名与实际门禁语义不一致
- **stableID**：R10-T06（本轮本人新发现，独立编号；与 `Z08-03`／`F12` 的预算/取消边界相关但不是同一项）
- **严重性**：P2（流程语义）
- **触发**：Windows runner 上 `npm run engine:check` 失败。
- **代码定位**：`.github/workflows/ci.yml`（base→67 差异中 Windows job）：
  ```
  - run: npm run engine:check
    if: runner.os != 'Windows'
  # Diagnostic only: first-failure evidence; not acceptance or merge approval.
  - name: Windows engine first-failure diagnostic (not acceptance)
    if: runner.os == 'Windows'
    ...
    run: | ... npm run engine:check
  ```
  Windows step 名写「not acceptance」，但**没有** `continue-on-error: true`，因此该 step 非零退出仍会使 Windows job `failure`。
- **影响**：命名易被误读为「Windows 引擎检查失败不阻断」，实际仍是阻断。这是**保守方向**（不会放过红灯），但对「哪一步算验收」的记录口径造成歧义。
- **最小建议**：把 step 名改为中性描述（如「Windows engine run with first-failure diagnostics」）并显式说明其退出码仍决定 job 成败；或在需要真正「仅诊断」时补 `continue-on-error: true` 并另设接收步骤。**不建议**在本候选改——属 CI 语义澄清票。
- **push 前源码阻断**：否。

### R10-T07｜vendored rdflib 是**本地改版 wheel**，供应链与许可为独立 HOLD，且仓库内并存三个版本
- **stableID**：R10-T07（承接 `Z09-04`／`R05 MM09`／`R08 F09`／`F09`）
- **严重性**：P2（发布/供应链 HOLD）
- **触发**：打包与发布审计。
- **代码/原件定位**：`packages/engine/pyproject.toml` 依赖改为 `rdflib==7.6.0+ontolearn.fr201.3` 并加 `[tool.uv.sources]` 指向仓库内 wheel；`uv.lock` 中该包 `source = { path = ...rdflib-7.6.0+ontolearn.fr201.3-py3-none-any.whl }`、hash `sha256:99fab7bd…51edf`；仓库内同时保留 `rdflib-7.6.0+ontolearn.fr201.1/2/3` 三个 wheel 加上游 wheel；`packages/engine/vendor/rdflib/PROVENANCE.json` 明确 `officialUpstreamUnchanged: false`、`transparentLocalVersion: true`、`currentConsumerStatus: "Not asserted by this supplier."`；`licenses/NOTICE` 已追加说明并**逐字**写明「These repository references do not assert their inclusion in the App.」
- **影响**：上游 7.6.0 官方 sdist/wheel 已从 lock 中移除（不再有 pypi hash 锚），供应链核验必须走本仓库自述的 PROVENANCE，而该文件自称不主张采纳状态。冗余 wheel 增加 4.76MB 级别制品负担。
- **最小建议**：发布/供应链 owner 在 merge 后受控窗口做一次包内实物核验与冗余件清理；**不私自删 wheel**（原 owner 窗口与 F09 处置一致）。
- **push 前源码阻断**：否。

### R10-T08｜CI 制品上传范围扩大 + `failure-traces-linux` 改为 `always()`，但未设 `if-no-files-found` 且路径更宽
- **stableID**：R10-T08（承接 `Z09-08`／`F12`／`Z08-09`）
- **严重性**：P3（CI 卫生观察）
- **触发**：任何 CI 运行。
- **代码定位**：`.github/workflows/ci.yml` 中 Linux 与矩阵 job 的 upload-artifact `path` 由 `test-results/i04-*/` 改为 `build/engine-tests/` + `test-results/`；`failure-traces-linux` 的 `if: failure()` 改为 `if: always()`；Windows job 的 `if: always()` 同样扩到三路径。
- **影响**：制品上传体积与保留期（7 天）成本上升；`always()` 后失败轨迹会在成功运行也上传。**未发现**因宽路径导致凭据、业务数据或 `.sqlite` 被纳入上传的证据（上传源为 `build/engine-tests/` 与 `test-results/`，非业务数据目录）。
- **最小建议**：CI 维护票评估路径是否需要 `test-results/` 全量；确认 `build/engine-tests/` 内不含 `.sqlite`/`.env` 后再固化。
- **push 前源码阻断**：否。

### R10-T09｜`newManualFactPlan` 改为内容派生 ID 后，renderer 必须与 Python `Store.digest` **逐字节**一致——我已实测当前形态一致，但耦合无机器校验
- **stableID**：R10-T09（承接 `R04 M06`／`R05 MM11` 的「分层闭合、非绕过漏洞」口径）
- **严重性**：P2（跨语言契约耦合）
- **触发**：renderer 侧 `JSON.stringify([S,P,O])` 与 Python `canonical([S,P,O])` 出现任何字节差异（例如 Python 侧 `ensure_ascii=False` 与 JS 侧非 ASCII 转义策略、或 JSON 转义集合差异）。
- **代码定位**：`apps/desktop/src/renderer/src/ontology/mainline-facts.ts:73-80` 用 `new TextEncoder().encode(JSON.stringify([subject,predicate,object]))` + `crypto.subtle.digest('SHA-256', …)`；引擎侧 `packages/engine/src/ontolearn_engine/storage.py:24-31` `canonical()` = `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",",":"), allow_nan=False)`，`digest()` = `sha256(canonical(value).encode()).hexdigest()`；`storage.py:494` 在 `_fact()` 中强制 `fact["id"] != digest([subject,predicate,object])` 即拒绝。
- **影响**：若两侧漂移，**所有新建人工事实会被引擎拒绝**（`_fact` 抛 `ValueError`），表现为「界面可提交但引擎报错」，属可见失败而非静默损坏。
- **我已实测（只读、纯计算，不触碰仓库、不跑产品）**：用 JS `JSON.stringify` 与 Python `json.dumps(ensure_ascii=False, sort_keys=True, separators=(",",":"))` 对 7 组实际形态（中文 `@zh`、`@en-001`、`@de-ch-1901`、datatype IRI、制表符、转义引号、emoji）逐一比对，**全部逐字节相同**；仓库内 `tests/unit/t02-manual-fact-id.test.ts:53-76` 更以 `spawnSync` 调用**真实 Python `Store._fact`** 交叉校验 golden 向量（我读了该测试全文，确认其不插值进 Python 代码、不开数据库）。`mainline-facts.ts:56-64` 另外显式拒绝孤立代理项（lone surrogate），避免 `JSON.stringify` 的代理转义与 Python UTF-8 编码语义分歧。
- **最小建议**：把该跨语言等价写成一条可执行的机器检查（当前只有单测里的 golden 向量，未覆盖全部 Unicode 形态）；**不建议**在本候选新增——现有单测已覆盖关键形态且失败方向可见。
- **push 前源码阻断**：否。

### R10-T10｜`manualFactPlan` 的「多值事实」判定放宽后，同 slot 多条手动事实的歧义判定与引擎 `_check_slot` 语义不完全对齐
- **stableID**：R10-T10（本轮本人新发现，独立编号）
- **严重性**：P2
- **触发**：同一 (subject,predicate) slot 存在多条手动事实、且其中一条被编辑或删除。
- **代码定位**：**修改文件完整差异**（`apps/desktop/src/renderer/src/ontology/mainline-facts.ts`，base→67 累计）：
  - base 版本：`const live = source.domain.state.facts.filter(row => row.object !== null && row.subject === fact.subject && row.predicate === fact.predicate); if (live.length !== 1) throw new Error('AMBIGUOUS_FACT_SUPPORT')`。
  - head 版本改为：排除自身 `row.id !== fact.id` 后，若存在**任一**同 slot 行满足「有 owner/source_row/managed_value（受管）」**或**「`row.object === original.object`（重复）」**或**「edit 且 `row.object === replacement.object`（与替换值冲突）」，则抛 `AMBIGUOUS_FACT_SUPPORT`；否则允许。
  - 引擎侧 `packages/engine/src/ontolearn_engine/storage.py:788-812`（edit 路径）调用 `_check_slot(project, old.subject, old.predicate, value, {identity}, …)`，其冲突条件为 `row["id"] not in excluded and (row["id"] == reserved_id or (row["object"] is not None and (single or row["object"] == value)))`——其中 `single` 由 `single_predicates` 决定，`reserved_id = digest([subject,predicate,value])`。
- **影响**：renderer 侧按「重复对象/受管/替换值撞车」三者判定，引擎侧按「保留身份命中或单值谓词或对象相等」判定。**在编辑场景下两者大体一致**（`reserved_id` 命中恰对应 `row.object === replacement.object`），但存在两处口径差：① renderer 对「受管行」无条件拒绝，而引擎在 `single` 为假时允许同 slot 多值共存；② renderer 不感知 `single_predicates` 集合。差异的实际后果是 renderer 可能比引擎**更早、更严**地拒绝一次合法编辑（用户看到 `AMBIGUOUS_FACT_SUPPORT` 而非进入引擎冲突路径）。这是**保守方向**（不产生错误写入），但会让「受管同 slot 多值」场景的可用性受限，且与 `R05 MM07`（typed witness 部分闭合／裸族延期）所处的家族语义相关。
- **最小建议**：在 `mainline-facts.ts` 的 `AMBIGUOUS_FACT_SUPPORT` 判定处补一行注释，明确它**刻意**比引擎 `_check_slot` 更严格，以及「受管行」与「单值谓词」两个差异点；由原 T02 前端归口在下次维护窗口评估是否改为直接透传引擎冲突路径。**不建议**本轮改——那会改变已验证的产品行为面。
- **push 前源码阻断**：否。

**Top 统计**：10 项中，**0 项为 push 前源码技术阻断**；1 项为合并门禁（R10-T01）、2 项为未证根因/未知终态（R10-T02、R10-T03）、1 项为发布/供应链 HOLD（R10-T07）、6 项为 P2/P3 维护或覆盖面观察。

---

## 3. 本人实际审读范围与来源区分（不夸大覆盖）

### 3.1 本人亲读全文（逐行）

| 文件 | 方式 | 理由/重要性 |
|---|---|---|
| `tests/e2e/ui-observation.ts`（195 行，67 新增） | **全文** | 67 核心新增逻辑 |
| `tests/unit/ui-observation.test.ts`（194 行，67 新增） | **全文** | 唯一新增单测 |
| `tests/e2e/t02-fr200-fr201.spec.ts`（1942 行，67 修改 +208） | **全文（含 base→67 完整差异）** | FR-200/201 主验收 |
| `tests/e2e/mainline-consumer-first-ack-loss.spec.ts`（67 修改 +77） | **完整差异** | case7 修复所在 |
| `AGENTS.md`（工作树 overlay 版 +101/−10） | **全文 + 完整差异** | 执行约束 |
| `docs/prd/PRD-本体学习与落地Agent工作台.md` | FR-200/201 全文（第 307–319 行）+ 全文章节结构图（§7.3/附录 C/D/E/F/G 定位） | 需求依据 |
| `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` | **S1/S2/S3/C1/B1/U1 全文 + §4 执行批次 + §5 证据口径** | 验收依据 |
| `docs/reviews/T02/status.md`（28185B） | 尾部 R08/R09 追加段全文 + 开头结构 | 当前状态 |
| `docs/m0-checklist.md` | base→67 完整差异 + 新增四段 | 唯一状态源 |
| `docs/reviews/T02/fr200-fr201-20261024/round-09/disposition.md`（61912B） | **全文**（363 行，含 §1–§7 与 §5/§6/§6.3 三张表） | 历史处置权威入口 |
| `round-09/version-map.json`、`round-09/artifact-manifest.json`、`round-09/independent-*-disposition-audit.md` | 全文 | 版本/计数/独核 |
| `packages/engine/src/ontolearn_engine/storage.py` | `canonical`/`digest`/`_fact`/`commit` 的 manual+edits+remove 路径、`_check_slot`、`_snapshot_projection` 段 | 存储不变量 |
| `packages/engine/src/ontolearn_engine/job_store.py` | `_application`（含 ownership 落盘与 `fault` 边界）、`_ownership_header`、`_ownership_segment`、`ownership_detail_page`、`detail_get`、`_project`、`ordinary_project_choices`、`project_get` | 错误边界与 ownership detail |
| `packages/engine/src/ontolearn_engine/project/mainline.py` | base→67 **完整差异**（+417，含 `_WriteAdmission`、`_OwnershipProof`、`ownership_proof`、`prepare_mainline_store`、method 分派） | 引擎主路径 |
| `packages/engine/src/ontolearn_engine/project/domain_changesets.py` | base→67 完整差异（+36） | 预览/拒绝语义 |
| `apps/desktop/src/renderer/src/ontology/mainline-session.ts` | base→67 完整差异（+88）+ `read`/`#readNow`/`#current`/`#prepare` 段全文 | 时序与 fence |
| `apps/desktop/src/renderer/src/ontology/mainline-facts.ts` | base→67 完整差异（+50）+ 全文 | 事实 ID 与歧义判定 |
| `apps/desktop/src/renderer/src/ontology/mainline-ownership.ts`（78 行，新增） | **全文** | ownership 消费端 |
| `apps/desktop/src/renderer/src/ontology/OwnershipConflictDetailView.ts`（105 行，新增） | **全文** | 展示层 |
| `apps/desktop/src/renderer/src/ontology/OntologyMainlinePage.tsx` | base→67 完整差异（+89） | 预览 fence 与错误文案 |
| `apps/desktop/src/main/{desktop-ipc,engine,project-mainline-service}.ts`、`apps/desktop/src/preload/index.ts` | base→67 完整差异 | 边界接线 |
| `packages/contracts/src/v2.ts` | base→67 完整差异（+131，含手写 SHA-256 全实现） | 契约校验 |
| `packages/contracts/src/index.ts` | `reassembleOwnershipDetail` 全文段 | 重组与限额 |
| `scripts/run-engine-tests.py`（470 行）、`scripts/engine-test-reporting.py`（124 行） | **全文** | CI 分片与计账 |
| `.github/workflows/ci.yml`、`packages/engine/pyproject.toml`、`pyproject.toml`、`package.json`、`uv.lock`、`licenses/NOTICE` | base→67 完整差异 | 依赖/CI/许可 |
| `packages/engine/vendor/rdflib/PROVENANCE.json` | 全文 | 供应链 |

### 3.2 差异级（未逐行读全文，仅读该路径差异）

`tests/e2e/native-driver.ts`（+304）、`tests/unit/native-driver.test.ts`（+396）、`tests/unit/t01-*.test.ts`（5 个）、`tests/unit/t02-mainline-*.test.ts`（2 个）、`tests/unit/t02-manual-*.test.ts`（2 个）、`tests/unit/t02-ownership-*.test.ts`（2 个）、`tests/fixtures/t02-manual-fact-id.json`（+139）、`packages/engine/tests/test_mainline_*.py`（6 个，+3493）、`packages/engine/src/ontolearn_engine/{coordinator.py, project_host.py, project/query_presentation.py, rdf_snapshot.py}`、`packages/contracts/python/contract_v2.py`、`packages/contracts/v2/{schema,fixtures,registry,binding-regressions}.json`、`scripts/repack-rdflib-input-types.py`、`docs/reviews/T02/fr200-fr201-20261024/round-04..08/**`（归档文档）、`packages/engine/vendor/rdflib/*.whl`（二进制）。

### 3.3 子代理定位与本人复核

本轮我使用 4 个只读子代理（`explore`），**全部在收尾阶段因网络 `ERR_CONNECTION_CLOSED` 中断，未交付结构化终稿**。因此**本报告不依赖任何子代理结论**：

- 子代理 A（O069 原件取证）：其过程输出中提出「COMPLETION.json 声称 HANDOFF.json 1803B，目录内实测 1530B」的疑点——**我本人已独立复核并解决**：O069 目录内 `HANDOFF.json` 实测 1530B／SHA256 `6f8b3a00…d0c22`，而 COMPLETION.json `qualityRetryO068.handoff` 声称的 1803B／`2f8fbe97…57ed7` **精确对应 O068 目录的 `HANDOFF.json`**（我实测 O068 目录该文件确为 1803B／同 hash）。即该 pin 指向 O068 的交接文件，**不是 O069 自身文件的错配**；O069 自身 `HANDOFF.json` 的 `oldQualityRetryHandoff` 字段也指向该绝对路径。此为**引用对象的隐含路径歧义**，非字节造假。
- 子代理 B（R09/R08 稳定 ID 提取）：其过程输出给出 31/78/额外 13 的分组与 ID 规则，我**已用本人对 `round-09/disposition.md` 的全文亲读独立复核**，结论一致（见 §5）。
- 子代理 C（O065–O068 历史原件核验）：过程输出未成稿；O065–O068 的关键事实我**本人重做**（见 §3.4）。
- 子代理 D（Python 引擎差异缺陷定位）：网络中断前未交付结论；引擎侧我**本人改用直读**完成（见 §3.1）。

### 3.4 原件核对（本人实测）

| 原件 | 本人实测 |
|---|---|
| O069 `COMPLETION.json` | 6941B／SHA256 `6b9f8a52…58f60` **匹配** |
| O069 `staged.diff` | 36240B／`4716d937…6d18` **匹配**；与 `APPLIED-01.diff` **逐字节相同**（`cmp` 无差异） |
| O069 `FINAL-MANIFEST.json` | 14072B／`711993fd…7da4` **匹配**；其 **70 条 pin 我逐条重算 SHA256 与字节数，0 缺失、0 不匹配** |
| O069 `staged.diff` vs 实际 Git 差异 | 我执行 `git diff b0c0e8d3 67b7bcbd`，实测 36240B，与 `staged.diff` **逐字节相同** → 该 patch 精确等于真实提交差异 |
| O065 `ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt` | 11255B／`1ca23def…f709c`／末字节非 LF／**160** 条 |
| O065 `REVIEW-CLOSEOUT-MANIFEST-01.json` | `files` 列表实测 **159** 条 |
| O066 `COMPLETION.json` | `exactFiles` 列表实测 **9** 条 |
| O066 `FINAL-MANIFEST.json` | `files` 列表实测 **36** 条 |
| O067 `COMPLETION.json` | run40382314925/attempt1 整体 `cancelled`；Quality `cancelled`／Windows `failure`／macOS `success`；合成 checkout `166aa065…`、parents `583c05c`+`b0c0e8d3`、tree `94a6749d…`（=b0 的 tree，非真实 merge）；Linux 3716P+53S=3769／Windows 3721P+48S=3769／macOS 3719P+50S=3769 |
| O067 `WINDOWS-CI42-FAILURE-FACTS.json` | case7 `durationMs=9311`、`retry=0`、`exactError="Error: Timeout 5000ms exceeded while waiting on the predicate"`、`sourceFailureLine=379`；case16 `durationMs=180010`、`status=timedOut`；`actualCheckout.sha=166aa065…`、`isActualPRMerge=false` |
| O067 `DIAGNOSIS-AND-NEXT-OPTIONS.md:16` | 逐字含 `ded30765-ee2f-402b-98dd-7bc32d50ddeb`（trace sito@640 42803.074→42807.898）——该 ID **已知**，非「所有 ID 未知」 |
| O068 `monitor-COMPLETION.json` | `EVIDENCE_COMPLETE_QUALITY_CANCELLED_UNCHANGED_15MIN`；`sourceOrCIChanges=false`；两个 ZIP 官方 digest 与本地 hash 一致、`allZIPCRCValid=true`（memberCount 6543 / 11） |
| O068 `HANDOFF.json` | 1803B／`2f8fbe97…57ed7`（与 O069 COMPLETION 的 pin 精确对应）；逐字含 `additionalInvocationsAvailable: 0` |
| O067 `HANDOFF.json` | 1803B 声明外，实际实测 1245B（该文件为 O067 自身交接，pin 列表为 COMPLETION/FINAL-MANIFEST/FINAL-FROZEN-GUARD/DIAGNOSIS 四项） |

### 3.5 真正未覆盖（本报告不声称的部分）

1. **1396 tracked 源叶未逐叶全文审读**；我读的是 67 新增 4 文件全文 + 累计候选产品/契约/引擎/脚本/CI/依赖差异级 + 上述必要闭包。未变更的无关上下文（如 I01/I03/I04 历史实现、`.pen`、其他归档原稿正文）未读。
2. **未运行任何 check/vitest/pytest/build/package/install/formatter/HMR/产品/GUI/SQL/bridge/故意业务失败探针**。本报告**不含**任何「本人跑过」的测试事实；所有测试数字均来自标明身份的既有原件（O064/O067/O068/O069），并标明其执行时点。
3. **未验证** O069 的 89 项 qualificationChecks、native24 的 21P+3SKIP、六 T02 case、driver 74854/169.386s、5 build 的 24B nonce 差异——这些我只核对了**声明与归档存在性/哈希**，未复跑。
4. **未实测** `ui-observation.ts` 在真实 Electron 中的实际产出字节、16KiB 兜底分支的实际长度（见 R10-T05，标为「需运行验证」）。
5. **未审** `packages/engine/vendor/rdflib/*.whl` 内部字节内容（二进制），仅核 PROVENANCE/NOTICE/lock 的**声明层**。
6. **未读** round-01/02/03 的未跟踪 WIP 正文、round-04..08 的作者原稿全文（仅经 disposition 转述与必要的 §表核验）。
7. **未取得**另一作者本轮 R10 的任何输出/意见/verdict；`.../20261027_t02_67b7_fresh_r10_070/zcode/` 目录我仅执行 `ls`（实测为空），**未读取任何文件**。

---

## 4. 160 项清单逐项判定

**编号基准**：§4.1 的行号 **1–160 严格逐行对应**权威原件 `outputs/20261026_t02_240b_fresh_r09_065/ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt`（11255B／SHA256 `1ca23def…f709c`／末字节非 LF）中的 160 条 `> ` 行，顺序与文案一一对齐，无缺行、无重复行、无填充行；本人已逐行核对并做过机器化行号校验（min 1／max 160／missing ∅／dup ∅）。

**判定用词**：适用／部分适用／不适用／无法确认。复合判定自成一档、只计一次——每行只出一个档位、只计一次。统计见 §4.2。

### 4.1 逐项

| # | 判定 | 依据 |
|---|---|---|
| 1 | 不适用 | 「schema someone designed instead of improvised table by table」——本产品是**本体/RDF 建模工作台**，不是多表关系型 SaaS；本体结构由 `packages/contracts/v2/schema.json` + 附录 C 能力矩阵定义，非逐表 AI 即兴。 |
| 2 | 不适用 | 无邮箱登录体系；项目为本地单机，无账号密码登录面。 |
| 3 | 不适用 | 无密码重置流程。 |
| 4 | 不适用 | 无 MFA、无手机号/设备恢复路径。 |
| 5 | 不适用 | 无会话超时/全端下线；进程内 `OntologySession` 生命周期由 `dispose()`/`#retired` 管理，非账号会话。 |
| 6 | 不适用 | 无企业 SSO 客户诉求证据；产品定位本地优先、不自动启用云服务。 |
| 7 | 不适用 | 无 SAML。 |
| 8 | 不适用 | 无 SCIM/员工目录。 |
| 9 | 部分适用 | 「比 admin/everyone else 更深的角色权限」——本产品有**能力注册表 + 方法级 allowlist**（`packages/contracts/v2/registry.json`、`packages/engine/src/ontolearn_engine/project/mainline.py` `METHODS` 集合、`apps/desktop/src/main/engine.ts` 按方法分派授权），比二元 admin 更细；但**不是**用户角色体系。判定为部分适用。 |
| 10 | 不适用 | 无「改 URL 中的一个数字读他人数据」的多用户 URL 资源；`projectId` 有 UUID 格式校验（`job_store.py:1053-1061`）与 public/internal 映射。 |
| 11 | 不适用 | 单租户本地应用，无租户隔离概念。 |
| 12 | 不适用 | 无「登录即此用户」的管理员按钮；无 impersonation 语义。 |
| 13 | 不适用 | 无登录面，故无登录限速/撞库。 |
| 14 | 不适用 | 无账号锁定概念。 |
| 15 | 部分适用 | 「能前滚也能回滚的数据库迁移」——`packages/engine/src/ontolearn_engine/storage.py` 有 `FORMAT_VERSION`／格式版本检查与 `UnsupportedProjectFormat`，但**未见可回滚的降级迁移路径**；M0 计划亦把「人工 schema 降级」列为未验。判定为部分适用（版本门禁在，回滚未证）。 |
| 16 | 不适用 | 本产品 SQLite 单文件本地库，无「周二下午锁主表」的并发在线迁移场景。 |
| 17 | 部分适用 | 「索引，因为 5M 行会超时」——存储层有 `facts`/`snapshots`/`job_details` 等表并使用 `ORDER BY id`（见 `storage.py` facts 查询 `ORDER BY id`）；但 Q5 容量目标与参考设备**未确认**，容量本身仍是独立 HOLD。判定为部分适用。 |
| 18 | 不适用 | 无连接池（本地 SQLite 单连接，见 `store._db` 单连接使用）。 |
| 19 | 不适用 | 无「每晚备份」服务端作业；本地库由使用者自行管理，M0 未实现备份。 |
| 20 | 不适用 | 无「从备份恢复」的已实现路径；相关能力在 M0 计划中属未实现。 |
| 21 | 不适用 | 无 PITR。 |
| 22 | 不适用 | 无软删除 UI 概念；不过引擎**确实**有「受管事实 tombstone」语义（`storage.py` 中 `object IS NULL` 表示受管墓碑，且注释明确「UI 手工删除不会制造受管墓碑」）。这是数据所有权标记，不是软删除功能。判定不适用。 |
| 23 | 部分适用 | 「服务端校验，不只在前端」——校验确实在引擎侧执行：`storage.py:484-495` `_fact()`、`:788-812` edits 的 `_check_slot`、`domain_changesets.py` 预览期 `term(value)`/`parsed.n3() != value` 拒绝非法 RDF；前端只做预检。判定为适用倾向，但前端仍存在**客户端预判歧义**（见 R10-T10），故记为部分适用。 |
| 24 | 不适用 | 无用户时区/提醒排程功能。 |
| 25 | 适用（正面） | 「姓里有撇号的用户」——N3 字面量与 IRI 均按 canonical 形式处理；`rdf_snapshot.py` 的 `term()` 决定 N3 输出，测试 golden 含 `'"泵站A"@zh'`、`'"quote\\"inside"'`（我实测 JS/Python canonical 对含转义引号、制表符、emoji 的字面量**逐字节一致**）。判定为适用且正面。 |
| 26 | 适用（正面） | 「每个字段里的 emoji、重音与从右到左文本」——仓库有专门的 `test_mainline_language_input_rejection.py`（+326）与 `test_mainline_language_input_rejection` 覆盖 `@en-001`／`@de-ch-1901`；`mainline-facts.ts` 显式拒绝孤立代理项以免 Unicode 分歧；`storage.py` canonical 用 `ensure_ascii=False` 且我实测与 JS `JSON.stringify` 一致。判定为适用且正面。 |
| 27 | 不适用 | 无金额存储。 |
| 28 | 不适用 | 无货币/税。 |
| 29 | 部分适用 | 「数据模型能扛住第二个客户的『小改动』」——分层数据模型（本体定义/断言事实/映射状态/快照/历史）已在 `storage.py` 的 `state()` 与 `domain_changesets.py` 中成形，FR-203 导入导出要求「超范围拒绝提交而非静默丢弃」；但尚无第二个真实客户证据，也未覆盖全部附录 C。判定为部分适用。 |
| 30 | 不适用 | 无支付。 |
| 31 | 不适用 | 无重复提交去重（表单提交非资金操作）；事实层有内容派生 ID 的天然幂等（见 R10-T09），但那不是支付幂等键。 |
| 32 | 不适用 | 无分页列表产品面。 |
| 33 | 不适用 | 无用户数据导出功能（M0 未实现导出）。 |
| 34 | 不适用 | 无 CSV 导入。 |
| 35 | 不适用 | 无保留期/自动删除策略。 |
| 36 | 适用（正面） | 「密钥不在代码、不在仓库、不在 AI 对话历史」——仓库无凭据；`.gitignore` 与 AGENTS 明确禁止提交凭据/`.env`/`.mimosa/`；`safeStorage` 凭据方案属 S3 未来范围，当前**未接入**任何模型凭据。判定为适用且正面（当前无泄露面）。 |
| 37 | 不适用 | 无密钥轮换面（当前无生产密钥）。 |
| 38 | 部分适用 | 「确认 AI 装的每个包存在且正是你要的」——依赖版本精确锁定（`packages/engine/pyproject.toml` 全 `==`，`package.json` 精确版本），`uv.lock`/`package-lock` 随改提交；但 rdflib 已改为**本地改版 wheel**，其「正是你要的」依赖自述 PROVENANCE（见 R10-T07）。判定为部分适用。 |
| 39 | 部分适用 | 「依赖扫描，因为 AI 拉了没人审过的库」——`licenses/NOTICE` 有 rdflib/pyshacl/pyparsing 许可清单，vendored wheel 有 LICENSE+PROVENANCE；但**未见依赖漏洞扫描配置**（dependabot 仅 root npm/actions 周更，缺 SLA/EOL 核验，见 R08 已记）。判定为部分适用。 |
| 40 | 适用（正面） | 「所有用户能输入的地方做输入净化」——输入面是 IRI 与 RDF 字面量；引擎 `rdf_snapshot.py` 的 `iri()`/`term()` 拒绝非法语法，`domain_changesets.py` 对 `manual` 与 `edits` 的值做 `term(value)` 且要求 `parsed.n3() == value`（即必须已是 canonical N3），非法即 `INVALID_REQUEST`。判定为适用且正面。 |
| 41 | 适用（正面） | 「防 SQL 注入、XSS、CSRF」——SQL 全部参数化（如 `storage.py` `WHERE project=? AND id=?`；动态表名来自 `sqlite_master` 并做引号转义 `'"' + table.replace('"','""') + '"'`）；无浏览器网络面故无 XSS/CSRF；CSP 由 `apps/desktop/src/csp.ts` 单一来源，**本候选未改该文件**（我实测 base→67 diff 中 `csp.ts` 无差异），生产脚本无 `unsafe-inline`/`unsafe-eval`（唯一 `unsafe-inline` 在 `csp.ts:20` 的 **style-src 开发 HMR 分支**，带注释「production uses local CSS」）。判定为适用且正面。 |
| 42 | 不适用 | 无用户文件上传面。 |
| 43 | 适用（正面） | 「CORS 不是允许一切」——本地应用无跨源网络面；`apps/desktop/src/main/index.ts` 用 `loadURL(devURL)`/`loadFile(rendererPath)` 加载本地资源，preload 只暴露按业务命名的方法（`apps/desktop/src/preload/index.ts`），无 `invoke(method, params)` 通用通道。判定为适用且正面。 |
| 44 | 适用（正面） | 「每个响应都有安全响应头」——桌面本地加载不经过 HTTP 服务器，故无 HTTP 响应头面；等价的安全响应头职责由 CSP + 窗口隔离 + IPC sender/mainFrame 校验承担。判定为适用（等价物已具备）。 |
| 45 | 不适用 | 无传输加密面（本地 stdio + 本地文件，不走网络）。静态加密亦未接入（属 S3）。 |
| 46 | 部分适用 | 「最小权限，包括持生产凭据的 AI Agent」——模型外发网关属 S3，本候选**未接入**任何模型凭据（AGENTS 不变量：Python 引擎不持密钥）。已实现的最小权限体现在：主进程持有 authority（`MainlineHost`、`_OwnershipProof`、`_WriteAdmission` 均要求 `owner` 身份与 store 同一性），renderer 无 Node/文件系统能力。判定为部分适用（AI 代理持凭据这一子项尚不存在）。 |
| 47 | 适用（正面） | 「日志记录谁做了什么，但不记密码/令牌/卡号」——AGENTS 不变量明确「跨边界只传固定错误码和受限参数，不回传原始异常、堆栈、路径、单元格原值或凭据」；我亲读 `job_store.py:628-636` 落盘 `{"category","resource","projectId"}` 固定集（逐字注释「Persist only fixed categories and authorized opaque identities, outside the rolled-back write. No exception text/values/paths.」）；`ManualOwnershipConflict` 的 locator 只含 `id/owner/sourceRow/slot`，**不含 object 原值**。判定为适用且正面。 |
| 48 | 无法确认 | 「上线前做一次渗透测试」——本候选无渗透测试证据；组织/流程事实（是否安排过外部渗透）不能由代码判定。判定为无法确认（组织事实）。 |
| 49 | 部分适用 | 「安全问卷逐条回答且有证据」——本地优先、无云服务、无账号体系，问卷面极小；但我方**不能**代答第三方审计问卷，亦无既有问卷答复原件。判定为部分适用。 |
| 50 | 不适用 | 无漏洞披露流程（无对外服务）。 |
| 51 | 不适用 | 无生产访问设备失窃场景。 |
| 52 | 不适用 | 无 SOC 2。 |
| 53 | 不适用 | 无 HIPAA/患者数据。 |
| 54 | 不适用 | 无供应商 BAA。 |
| 55 | 部分适用 | 「审计轨迹显示谁看过一条记录，不只是谁改了它」——写侧有操作标记（`operationId`/`jobId`/`marker`，`storage.py` 提交标记与数据同事务）；**读侧无访问审计**（`project_get`/`ordinary_project_choices` 只读不记 who-read）。判定为部分适用。 |
| 56 | 不适用 | 无 PCI/卡号。 |
| 57 | 部分适用 | 「GDPR 删除请求要触及每张表、备份与日志」——本产品有数据生命周期分层与「历史不可改写、缓存回收不得触及历史」的规则，但**没有**「用户删除请求」流程（无账号体系、无跨表/备份/日志的删除通道）；且历史层按设计不可改写。判定为部分适用（分层规则在，删除请求面不存在）。 |
| 58 | 不适用 | 无数据驻留/地域选项（本地单机）。 |
| 59 | 不适用 | 无季度访问复核（无用户角色体系）。 |
| 60 | 部分适用 | 「dev/staging/prod 环境一致」——本产品**无** staging/prod 环境之分，只有本机开发与打包产物；`package:dir` 与 `verify-i04-package.py` 构成「构建态 vs 打包态」的一致性面，但非三环境。判定为部分适用。 |
| 61 | 部分适用 | 「基础设施即代码」——CI 用 GitHub Actions（`.github/workflows/ci.yml`）为声明式 IaC，桌面应用本体为 Electron + Python 引擎的本地可复现构建（`scripts/build-engine.mjs`、`npm run package:dir`）；但「服务端基础设施」不存在。判定为部分适用。 |
| 62 | 适用（正面） | 「部署流水线先跑测试再触达用户」——`ci.yml` 顺序为 `npm ci` → `uv sync --frozen` → `npm run check` → `npm run verify:sources` → E2E → `package:dir` → `verify-i04-package.py`；本候选 `package.json` 的 `check` 已把 `engine:check` 换成 `scripts/run-engine-tests.py`（带逐 node 计账）。判定为适用且正面（但流水线当前**未绿**，见 R10-T01）。 |
| 63 | 不适用 | 无线上部署，故无一键回滚。 |
| 64 | 不适用 | 无线上服务，无维护窗口。 |
| 65 | 不适用 | 无功能开关机制。 |
| 66 | 不适用 | 无云端自动扩缩。 |
| 67 | 不适用 | 无 CDN。 |
| 68 | 部分适用 | 「DNS/SSL/续期」——本地应用不需 DNS/证书；但「续期不失效」的责任等价物是**签名/公证/发布链**，属明确保留的独立 HOLD（R10-T07 与原 HOLD 群）。判定为部分适用（无 DNS 面，替代责任仍开放）。 |
| 69 | 部分适用 | 「后台任务队列，别让慢活冻住页面」——引擎有常驻协调器与 job 机制（ADR-0003、`job_store.py`、`coordinator.py`），主进程有取消/心跳；但**耗时业务能力本身尚未接入**（M0 正式领域能力仍只有 health 级）。判定为部分适用。 |
| 70 | 部分适用 | 「带退避的重试，别让一次抖动 API 变成丢单」——无外部 API 调用面；但引擎的 `job`/重试与 `recoveredPending` 恢复逻辑存在，且 CI 侧明确 `retry0`。就「无外部 API 可丢单」而言不适用更准确，但就「重试语义不丢已提交」而言属适用。判定为**部分适用**（取保守中间档）。 |
| 71 | 不适用 | 无死信队列（无外部异步任务）。 |
| 72 | 不适用 | 无 cron/多服务器调度。 |
| 73 | 部分适用 | 「缓存与变更时失效」——有派生视图/快照缓存与 `invalidation-v2.json` 驱动的 `staleReason`（AGENTS 不变量明确「staleReason 只来自 invalidation-v2.json」）；但缓存键与失效的具体范围仍属 M0 计划项，且**九行正反例未逐类 GUI 实测**（原具名下游 OPEN）。判定为部分适用。 |
| 74 | 不适用 | 「SPF、DKIM、DMARC，让密码重置邮件不进垃圾箱」——本产品**无事务性邮件面**：无账号体系、无密码重置（见 #3）、无对外通知发送（见 #127），桌面端为本地单机，全程不经 SMTP。邮件认证域在当前产品形态下不存在需求面。判定为不适用。 |
| 75 | 不适用 | 无事务邮件（无密码重置/邮件发送）。 |
| 76 | 不适用 | 无对象存储生命周期/2021 临时文件清理面（本地库与构建目录）。 |
| 77 | 不适用 | 无云成本告警/AI 循环账单面（无模型接入、无云服务）。 |
| 78 | 不适用 | 无灾备（本地单机，无多地域/接管演练）。 |
| 79 | 不适用 | 无第二地域。 |
| 80 | 部分适用 | 「3am 能搜的结构化日志」——有结构化 JSON 事件流（`scripts/engine-test-reporting.py` 的 `events.jsonl`、`job_details`/`job_blobs` 表、`summary.json`），但**应用运行期无面向运维的结构化日志检索面**，且 O068 记录 engine 自然退出码为 UNKNOWN。判定为部分适用。 |
| 81 | 不适用 | 无错误聚合服务（无 Sentry 等）。 |
| 82 | 不适用 | 无外部 uptime 探测（无对外服务）。 |
| 83 | 不适用 | 无值班告警分页。 |
| 84 | 不适用 | 无运营看板（无在线服务指标）。 |
| 85 | 不适用 | 无跨服务链路追踪（单进程本地，无多服务调用）。 |
| 86 | 不适用 | 无值班轮转（无在线服务）。 |
| 87 | 部分适用 | 「runbook，让值班的人知道『队列深度临界』是什么意思」——仓库有 ADR（`0001-desktop-framework.md`、`0003-resident-coordinator-and-jobs.md`）、M0 计划中的 S1/S2/C1/B1/U1 验收全文与 `docs/reviews/T02/status.md` 状态源，具名 owner/事件窗口明确；**但面向运维值班人的运行手册不存在**。判定为部分适用。 |
| 88 | 不适用 | 无线上事故复盘（无生产事故）。 |
| 89 | 不适用 | 无状态页（无对外服务）。 |
| 90 | 部分适用 | 「由懂逻辑的人写的单测」——测试大量断言**完整预期集合/顺序**（如 `t02-fr200-fr201.spec.ts` 对 `sortFacts`/`sortDefinitions` 的精确数组相等断言、`commit()` 对 marker/job/commitProgress 的整体相等），并有真实 Python 交叉校验（`t02-manual-fact-id.test.ts`）；但无「人」参与的可证事实，且新增的 7 个单测是**纯 synthetic DOM 形状**（`ui-observation.test.ts` 自述「pure test only DOM-shaped synthetic, never Electron/product acceptance」）。判定为部分适用。 |
| 91 | 部分适用 | 「每个第三方 API 的集成测试」——无第三方 API（本地优先、不自动启用云服务）；但对**真实引擎**有集成测试（engine 3769 集合、真实 Electron E2E）。判定为部分适用（第三方 API 面不存在）。 |
| 92 | 适用（正面） | 「注册/结账等赚钱流程的端到端测试」——本产品对应流程是 FR-200/201 表单 CRUD 与事实创建，`t02-fr200-fr201.spec.ts` 走真实表单、完整 Diff、显式确认、原操作读取、marker/job 校验，21 PASS+3 原 I04 SKIP。判定为适用且正面（流程不同但性质对应）。 |
| 93 | 不适用 | 无发布前压测（Q5 容量目标未确认，M0 计划明确「此时不设业务容量通过线」）。 |
| 94 | 适用（正面） | 「看起来像生产但不是生产数据的测试数据」——测试用合成 `urn:t02:*` 命名空间与固定 golden 向量（`tests/fixtures/t02-manual-fact-id.json`），与真实业务库隔离（独立 `isolated-desktop` 启动、`app.isPackaged` 等）。判定为适用且正面。 |
| 95 | 适用（正面） | 「回归测试：修 bug 41 不让 bug 12 复现」——`packages/engine/tests/` 有大量既有回归集（本次累计 3769 收集项），新增 `test_mainline_*.py` 六个专门覆盖语言拒绝/手工输入拒绝/postwrite 准入/预算。判定为适用且正面。 |
| 96 | 不适用 | 「五年旧笔记本测试」——目标参考设备与跨 OS（macOS15/Win11）属明确保留的独立 HOLD，本轮未测。判定为不适用（该测试本身未实施；相关 HOLD 在 R10-T07 与原 HOLD 群保留）。 |
| 97 | 不适用 | 无障碍合规（无面向外部用户的产品交付面，M0 未做 a11y 验收）。 |
| 98 | 不适用 | 无订阅/升降级/按比例计费。 |
| 99 | 不适用 | 无失败付款重试与催款邮件。 |
| 100 | 不适用 | 无发票/PO 号。 |
| 101 | 不适用 | 无销售税/VAT。 |
| 102 | 不适用 | 无退款/贷项。 |
| 103 | 不适用 | 无用量计费。 |
| 104 | 不适用 | 无年度合约/自定义条款。 |
| 105 | 不适用 | 无收入报表。 |
| 106 | 不适用 | 无 webhook。 |
| 107 | 不适用 | 无 webhook 重试日志。 |
| 108 | 不适用 | 无对外版本化 API（stdio 本地协议 v2 是内部契约，非客户集成 API）。 |
| 109 | 不适用 | 无客户 API key。 |
| 110 | 不适用 | 无对外 API 限流。 |
| 111 | 不适用 | 无第三方 API 响应格式突变。 |
| 112 | 不适用 | 无 OAuth 令牌刷新（无 OAuth 对接）。 |
| 113 | 不适用 | 无客户沙箱集成环境。 |
| 114 | 部分适用 | 「防提示注入，进入模型的每个字段」——**当前无模型接入**（AGENTS：S3 前不得接入模型外发，Python 引擎不调模型），因此不存在提示注入面；但同一批字段正是 FR-200/201 的用户输入面，其净化/拒绝机制已在 `rdf_snapshot.py`/`domain_changesets.py` 落地（见 #40）。判定为部分适用。 |
| 115 | 不适用 | 无「客户/患者数据离开网络」的提示面（无模型外发）。 |
| 116 | 不适用 | 无按客户计的模型花费上限（无模型接入）。 |
| 117 | 不适用 | 无模型评测集（模型能力未接入）。 |
| 118 | 不适用 | 无模型服务商降级预案。 |
| 119 | 不适用 | 无模型弃用迁移计划。 |
| 120 | 不适用 | 无提示/输出日志（无模型调用）。 |
| 121 | 适用（正面） | 「AI 做的不可撤销的事要人工确认」——这是本候选的**核心不变量**：正式写入必须经「完整事务差异」显示 + 「我已核对完整差异，确认提交」按钮（`OntologyMainlinePage.tsx` 的 `我已核对完整差异，确认提交`），并由 `commit()` 断言 `commitProgress.mode === 'atomic'`、`confirmationRef` 非空；Agent 只产草稿的 FR-204 边界在 PRD 中确立。判定为适用且正面。 |
| 122 | 不适用 | 无「酒店 WiFi 下加载页面」场景（本地应用，无网络依赖）。 |
| 123 | 部分适用 | 「每个页面都有空态/加载态/错误态」——渲染层有 `phase`（reading/preparing/submitting/ready/idle/unknown）与 `role="status"`/`role="alert"` 状态元素（`正在读取冲突定位…`、`冲突详情暂不可用。…`、`操作未能完成：…`）；但不是每个页面都有完整三态。判定为部分适用。 |
| 124 | 适用（正面） | 「错误消息要客户能行动，而不是『出错了』」——本候选把错误文案从笼统改为可行动：`OWNERSHIP_CONFLICT` 给出「事实来源、保留身份或属性约束存在冲突。请核对原记录，修改输入后重新预览；已输入内容保留。」，并新增 ownership 冲突定位视图（`OwnershipConflictDetailView.ts`）；引擎错误只传固定码。判定为适用且正面。 |
| 125 | 适用（正面） | 「一个字段校验失败时保留已输入内容」——`mainline-facts.ts` 的 `newManualFactPlan` 不改入参（`t02-manual-fact-id.test.ts:98` 断言 `fact` 与输入相等），UI 层 `invalidateFactPreview()` 只丢预览不丢表单值；`t02-fr200-fr201.spec.ts` 的拒绝用例断言 `subject/predicate/object` 三值原样保留。判定为适用且正面。 |
| 126 | 不适用 | 无邮件渲染。 |
| 127 | 不适用 | 无通知开关。 |
| 128 | 部分适用 | 「撤销」——Undo 入口存在且定义级 GUI 撤销/撤销之撤销/owned restart 已由既有证据收窄验证（R08 已验子集），**但其余 Undo 面与 GUI 全面验证仍为 HOLD**。判定为部分适用。 |
| 129 | 部分适用 | 「键盘导航与屏幕阅读器」——用 `getByRole`/`aria-label`/`role="status" |
| 130 | 不适用 | 无多语言本地化（界面文案为中文固定；但**数据内容**支持多语言标签，见 #26）。 |
| 131 | 不适用 | 无浏览器后退按钮（Electron 无多页导航）。 |
| 132 | 适用（正面） | 「人能读的代码」——模块边界清晰（main/preload/renderer/engine/contracts），命名与注释密度高，关键不变量以注释固化（如「Persist only fixed categories… No exception text/values/paths.」）。判定为适用且正面。 |
| 133 | 适用（正面） | 「每次改动都有代码评审」——本轮即双指定模型独立审查（R10），历轮 R04–R09 均有独立 disposition 与独核记录。判定为适用且正面。 |
| 134 | 部分适用 | 「分支策略，让两个人不互相覆盖」——worktree + feature 分支 + PR16 流程已在用（`git worktree list` 实测数十个隔离 worktree）；但并行开发线的合并顺序协调仍靠人工调度。判定为部分适用。 |
| 135 | 不适用 | 无月度依赖升级流程（dependabot 仅 root npm/actions 周更，缺 SLA/EOL 核验，属原维护窗口）。 |
| 136 | 不适用 | 无框架大版本升级计划（Electron 升级耦合 `Z09-09` 维护窗口）。 |
| 137 | 部分适用 | 「删掉 AI 前几次尝试留下的死代码」——`packages/engine/vendor/rdflib/` 三个版本 wheel 并存（fr201.1/2/3）属已知冗余件（F09 保留原 owner 窗口，「不私自删 wheel」）；除此之外未见明显死代码残留。判定为部分适用。 |
| 138 | 不适用 | 无 2000 行单文件（最大文件为 `t02-fr200-fr201.spec.ts` 1942 行测试与 `disposition.md` 61912B 文档；产品源文件均在数百行内）。 |
| 139 | 适用（正面） | 「架构决定写下来并带理由」——ADR-0001/0003 + M0 计划（含 S1/S2/S3/C1/B1/U1 全文与理由）+ PRD 附录 C/D/E/F/G 齐备。判定为适用且正面。 |
| 140 | 部分适用 | 「README 让新工程师一小时内本地跑起来」——存在 `package.json` 脚本、`uv`/`npm` 双锁文件与 `npm run check` 入口；但**未见**面向新人的 README 快速上手（本轮我亦未读 README，因为其不在差异路径亦不在我读到的入口文档集合内——列为无法确认其质量，仅就「有无入口脚本」判部分适用）。 |
| 141 | 部分适用 | 「给接手的人写文档」——`docs/reviews/T02/status.md`、`docs/m0-checklist.md`、ADR 与 M0 计划构成交接面；归属与状态有唯一维护者约定。判定为部分适用。 |
| 142 | 不适用 | 无运维管理后台（无多租户/在线服务）。 |
| 143 | 不适用 | 无客户支持工具（无客户账号）。 |
| 144 | 不适用 | 无客户可读变更日志（无对外发布）。 |
| 145 | 部分适用 | 「条款与隐私政策与代码实际一致」——本地优先、无遥测、无云、无账号、无数据外发，隐私面天然极小且与代码一致；**但**整体法律/隐私/产权/供应链审计仍是明确保留的独立 HOLD。判定为部分适用。 |
| 146 | 部分适用 | 「公司名下而非搭建者名下的账号/域名/仓库」——仓库为 `NOmoreJoke/OntoLearn-Studio`（个人 GitHub 账号名），非组织名；属发布/法律 HOLD 的具体一项。判定为部分适用。 |
| 147 | 部分适用 | 「巴士系数大于 1」——文档与 owner 归口清晰、ADR 完整，但**关键知识集中于单一维护者**（ROOT 为唯一总控），且 T02/T01/T11 各只有一名负责线；无第二人复现记录。判定为部分适用。 |
| 148 | 无法确认 | 「高级工程师逐行读完 AI 写的代码再上线」——这是人工流程，无法由代码判定；本轮审查与独立 agent 审查即其实例，但「上线前逐行人审」无既成证据。判定为无法确认（组织事实）。 |
| 149 | 无法确认 | 「第二位后端工程师在第二个客户前设计数据模型」——组织事实，代码不能证明。判定为无法确认。 |
| 150 | 无法确认 | 「解释 AI 的一个修复为何制造两个新 bug」——历史上有此类记录（如 `R04 M02` 43692 分页信封误因果已撤回、`R08 F10` 报告残句），但是否已形成制度化解释能力无法由代码判定。判定为无法确认。 |
| 151 | 无法确认 | 「部署、回滚、服务器与云账单」——本产品无服务器与云账单面；桌面端发布链（签名/公证）是等价职责但整体发布流程属组织事实。判定为无法确认。 |
| 152 | 不适用 | 无支付服务与值班人。 |
| 153 | 不适用 | 无框架漏洞公开当周打补丁的运维面（Electron 升级属维护窗口，非当周响应）。 |
| 154 | 不适用 | 无患者数据与审计员演示。 |
| 155 | 部分适用 | 「测试 AI 声称自己测过的东西（QA）」——**能力面可核**：本轮本人即对 O069 的 70 针逐条重算（`COMPLETION.json`／`staged.diff`／`FINAL-MANIFEST.json` 的 SHA-256 与字节数实测全匹配），`git diff b0c0e8d3 67b7bcbd` 与 `staged.diff` 逐字节相同，并以手写 SHA-256 对标准向量、JS `JSON.stringify` 与 Python `canonical` 做跨语言交叉校验；AGENTS 亦把「双指定模型独立审查 ＋ CI ＋ 远端核验」固化为常规门禁，实质等价于「不采信 AI 自述的测试结果」。但**组织面无法确认**：不存在独立 QA 角色／编制，验证证据与被验证实现出自同一开发线（本轮即由修复者封存、由复审者独立重算），且既有测试数字仍受「本机 Mac 绿 ≠ 新候选全平台绿」边界约束（见 R10-T01）。判定为部分适用。 |
| 156 | 不适用 | 无在活跃库上跑迁移的行级保全演练（本地库迁移演练尚未实施，属原 HOLD）。 |
| 157 | 不适用 | 无「拒绝破坏三个其他功能的需求」的产品裁决记录（属组织流程）。 |
| 158 | 部分适用 | 「把『在我机器上能跑』变成『对每个客户都能跑』」——有跨平台矩阵 CI（macOS/Windows/Linux）与打包验证，但**矩阵当前未全绿**（R10-T01），且目标设备/跨 OS 属保留 HOLD。判定为部分适用。 |
| 159 | 不适用 | 无「调试 AI 写不出原因」的场景（团队有人工调试者）。 |
| 160 | 部分适用 | 「一年后还有人记得为什么这样建（当年在场的人）」——**机制面成立**：ADR-0001／ADR-0003 与 M0 计划记录决定与理由，round-04..09 的 `disposition.md`／`version-map.json`／`artifact-manifest.json` 逐轮保留原始位置与事件窗口，AGENTS 规定 ADR 采用后移入 `docs/architecture/` 且控制在 1–2 屏；**组织留存面无法确认**：关键知识集中于单一总控（巴士系数见 #147），且**归档目录极密**（round-04..09 六轮、每轮多份文档、Z/MM 两方原稿），一年后的检索成本是实际负担。判定为部分适用（可追溯机制在、组织留存未确认）。 |

**复合判定说明**：清单末尾「your vibe-coded app 仍然需要……people who know what they're doing」一段，在原件中为 **#148–#160 共 13 行**独立 `> ` 行（并非一行内含多义）。本人对其中每一行**只给出一个档位判定**（不拆成多个子判定），且**每行只计一次**——因此这 13 行在 §4.2 统计中各计 1 次，全表合计恒为 160；不存在同一行被重复计数、也不存在把 13 行合并成 1 次的情形。该 13 行的实际分布为：**无法确认 4 项**（#148 逐行人审、#149 第二个客户前设计数据模型、#150 解释修复引入的新缺陷、#151 部署/回滚/云账单——均为组织事实或人工流程，代码不能证明）、**不适用 6 项**（#152 支付值班、#153 漏洞当周打补丁、#154 审计员演示、#156 活跃库迁移保全、#158 全客户等价、#159 调试 AI 写不出的代码——当前产品形态无对应需求面）、**部分适用 3 项**（#155 QA、#157 技术负责人否决、#160 一年后仍记得为什么这样建——机制面可由代码与文档佐证，组织编制面无法确认）。

### 4.2 统计（总数 160）

| 判定 | 数量 |
|---|---|
| 适用（含「适用（正面）」） | 18 |
| 部分适用 | 35 |
| 不适用 | 102 |
| 无法确认 | 5 |
| **合计** | **160** |

复合判定组（#148–#160 共 13 行并列陈述）每行各出一个档位、各计一次，已逐行计入上表；合计恒为 160。上表数量为本人对重建后表格的**程序化实测**结果，非推算填入。

**说明**：本轮 4 个子代理均未交付终稿，本判定**全部由本人亲读代码/原件独立得出**，未引用任何另一作者 R10 意见。

---

## 5. 历史问题逐项承接（原 31／权威 78／R09 新增／关键 Top 风险）

索引来源：`docs/reviews/T02/fr200-fr201-20261024/round-09/disposition.md`。§5 为「当前 31 稳定位置」（`:222-252`），§6 为「权威 78 历史位置」（`:260-337`），§6.3 为「MM额外13行（不充作原78）」（`:339-355`）。本人**逐行**复核该三表并给出本轮适用性；owner 与事件窗口**沿用原表**，不自创新职责。

### 5.1 当前 31 稳定位置

| ID | 本人 R10 适用性 | 原件/代码依据 | 已闭/保留/未知/不采纳 + 最小理由 | 原owner／事件窗口 |
|---|---|---|---|---|
| Z08-01 | 保留（仍开，合并门禁） | 远端实测 PR16 head=`b0c0e8d3`、67 未 push | **保留**。数值更新为 67b7bcbd：仍无新 CI。→ R10-T01 | ROOT 未来精确 push/CI 票；merge 前 |
| Z08-02 | 保留（仍开，未确认） | O067 Windows `job.descendants=UNKNOWN`（`WINDOWS-CI42-FAILURE-FACTS.json` `unverified` 明列「No universal App/native engine natural-exit or descendant cleanup claim」） | **保留**。本轮无新工具、无后代回收证据。 | Windows 完整 CI 证据接收；Job Object/新工具须 ROOT 另票 |
| Z08-03 | 保留（仍开，非阻断） | `ci.yml` base→67 差异实测：预算参数未被扩大（`intervals:[100],timeout:5000` 与原 5s/180s 保留于 `t02-fr200-fr201.spec.ts`） | **保留**。→ R10-T06（命名与门禁语义歧义） | 未来实际制品回单判断；预算变化须新明确授权 |
| Z08-04 | 保留（历史 FAIL 缺栈仍开） | O067 `case7`/`case16` 仅有结论与阶段附件，无完整栈 | **保留**。新结构化栈须真实 CI 复发时取得。 | 下一真实 CI 若复发按新增结构化栈定因；新绿不倒填 |
| Z08-05 | 保留（双向因果限定） | O059 已到 helper12；O060/O062 止于 EPERM | **保留**。结果与因果分开。→ R10-T02 | T01 原测试维护者下次授权触及环境/测试时 |
| Z08-06 | 保留（远端侧仍待验） | 无 67 的平台 CI | **保留**。本地 O069 证据不替代远端回单。 | Windows/Quality 实际 CI 仍待验 |
| Z08-07 | 保留（未验/文案维护） | `storage.py:1226-1230` 仍只区分 `reservedIdentity`/`sameStatement`/`singleSlot`；`singleDeclaration` 在 `storage.py:98` | **保留**。裸家族延期的代码事实未变。 | 原 T01/T02 方法接线窗口 |
| Z08-08 | 保留（P2，发布/供应链缺口） | 无依赖漏洞扫描配置；`licenses/NOTICE` 已补 rdflib 说明 | **保留**。→ R10-T07 | 发布/供应链 owner 另票 |
| Z08-09 | 保留（非阻断卫生观察） | `ci.yml` upload-artifact 路径扩大、`always()` | **保留**。→ R10-T08 | 未来 CI 维护票评估去重 |
| Z08-10 | 保留（部分采纳） | `pyproject.toml` 的 ruff exclude 新增 `docs/reviews/T02/.../round-[0-9][0-9]/{zcode-glm53,minimax-m31flash,minimax-m31flash-r2}.md` | **保留**。配置存在≠执行完成；且该排除面本身须在归档票复核（F10 口径）。 | 发布/vendor 原 owner 未来窗口 |
| Z08-11 | 保留（独立 HOLD 群） | 签名/公证/法律/跨 OS/容量/损坏库/未知解析/Undo 全部未验证 | **保留**。本轮未发现任一 HOLD 被 67 关闭。 | 原各 owner/父 FR 与发布验收时 |
| Z08-TOP10-OLD79F | 保留（未知保原） | 旧 CI36 79 个 F 仍无逐例栈 | **保留**。 | ROOT 历史残留登记及未来真实复发证据 |
| F01 | 保留（流程） | 本轮即 fresh R10 覆盖接收对象 | **保留为流程**。本轮完成本方覆盖与处置；接收由 ROOT 决定。 | T02 作者完成本票；ROOT 在 push 前接收 |
| F02 | 保留（合并门禁），数值更新为 67b7bcbd | 远端实测 | **保留**。→ R10-T01 | ROOT 发精确 push 票后按原 15/20 分钟逐 node 核验 |
| F03 | 保留 + 限定 | `scripts/run-engine-tests.py` 与 `engine-test-reporting.py` 全文亲读：逐 node/phase/session/identity 计账逻辑在位且本轮未改 | **保留**。脚本结算语义本轮**未变**（我在 ci.yml 差异中确认本轮 CI 改动只涉及 shard=2 环境变量与 reporter/artifact，不改计账逻辑）。 | ROOT；同交付 3769 逐项核验接收 |
| F04 | 维持撤回，不复活 | 67 不引入失败 annotation 门禁 | **维持撤回**。本轮仍不造失败样本。 | 本票内闭合 |
| F05 | **重新变开（新增事实）** | `docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 实测归档**仍停在 b0/R09 段**，无 67 段 | **重新变开**。67 尚待本轮接收与后续归档，不能自动关闭。→ 本报告仅出报告，不改状态文档（只读职责）。 | ROOT 指定文档 owner；状态新增段与普通证据提交 |
| F06 | 保留（维护） | `engine-test-reporting.py:69-80` 的 identity 字段含 `pythonpath`（`config.getini("pythonpath")`）等 13 项 | **保留**。13 字段身份仍不证完整 sys.path 等价。 | 原 T02 开发归口；声称完整导入路径等价之前 |
| F07 | 保留（维护） | `run-engine-tests.py:378-383` 记录 `head`/`tree` 到 summary.json | **保留**。接收任何无 head/tree 产出前。 | 原 T02 开发归口；证据控制层维护票 |
| F08 | 保留（正面复核），并追加本人新发现 | `OntologyMainlinePage.tsx` 的 `factLifetime` + `useLayoutEffect` 同步 detach、`preview()` 的 `current()` fence、渲染端 `mainline-ownership.ts` 的 `requireCurrent()` 逐页校验 | **保留并正面复核**：异步预览 fence 在位。**追加**：R10-T10（renderer 歧义判定与引擎 `_check_slot` 口径差）属同一前端归口的新观察。 | 原 T02 前端归口；UX/异步预览维护窗口 |
| F09 | 保留（P3） | `packages/engine/vendor/rdflib/` 实测四个 wheel 并存（fr201.1/2/3 + upstream） | **保留**。不私自删 wheel。→ R10-T07 | 原 T11 供应链/发布归口；merge 后受控维护 |
| F10 | 保留（两覆盖面仍不等） | `pyproject.toml` ruff exclude 只排 3 个文件名模式；prettier 排除面另计 | **保留**。不改 raw、不宽泛排除绕过检查。 | ROOT 报告归档归口 + 原 T02 维护归口 |
| F11 | 维持原审作者收窄 | `ManualOwnershipConflict` locator 实测只含 `id/owner/sourceRow/slot`，无 object | **维持收窄**。本轮未发现需扩大的新证据。 | 原 MM 作者本票内闭合 |
| F12 | 保留 | `ci.yml` 的 `always()` 与 artifact 路径变更（见 R10-T08） | **保留**。不延时/重试/隐藏取消。 | ROOT 未来 CI 结算逐步核产物 |
| F13 | 保留 | `run-engine-tests.py:19-31` 的 `HISTORICAL_SCORES` 注释逐字「They are NOT per-test durations or promised speedups」 | **保留**。不量化未实测提速。 | ROOT 后续 PR16 说明/CI 结算窗口 |
| F14 | 保留（维护） | `packages/contracts/src/v2.ts` 手写 SHA-256 + `matchesOwnershipDetail`；`packages/contracts/src/index.ts` 的 `reassembleOwnershipDetail` 限额（nodes≤16384、depth≤8、单串≤43692、总字符≤512*(43692+1024)） | **保留**。→ R10-T09（本轮实测两侧 canonical 逐字节一致，但耦合无全 Unicode 机器校验）。 | 原 T02 契约归口；后续首个 ownership-detail 契约维护票 |
| F15 | 保留（未确认观察） | `storage.py:474-481` facts 查询 `ORDER BY id`；`_check_slot` 的行选取未含 ORDER BY | **保留**。SQL 无序事实未确认观察，不升级缺陷。 | 原 T02 storage/契约归口；原见证顺序合同维护窗口 |
| F16 | 保留（容量维持） | Q5 未确认；本轮未测任何容量数字 | **保留**。不提高上限、不解除容量 HOLD。 | 原 T02 契约归口持续保留原 capacity |
| F17 | 保留（无需改动） | `mainline-session.ts` 的 `#guard`/sequence 机制本轮未改语义 | **保留**。无新增动作。 | 原 T02 前端归口 |
| F18 | 保留 + 我方过度陈述更正 | `uv.lock` rdflib 已改为 path source；`licenses/NOTICE` 已声明不主张纳入 App | **保留**。→ R10-T07 | 原 T11 供应链 + 原 T02 依赖归口 |
| F19 | 保留 | round-01..03 WIP 未跟踪、AGENTS overlay 未暂存（实测） | **保留**。保留旧 raw 与旧标题，不改写旧 79F 或 Ruff 差因。 | ROOT 唯一归档归口 |

### 5.2 权威 78 历史位置（逐行）

按 `round-09/disposition.md` §6 的 ID 顺序与分组（R07 组 23、R06 组 20、R04 组 14、R05 组 21 = 78）。本人逐行给出 R10 适用性；**代码事实未变者维持原处置**，**代码事实变化者**由本人标注。

**R07 组（23 项）**

| ID | 本人 R10 适用性 | 原件/代码依据 | 处置 + 最小理由 | 原owner／事件窗口 |
|---|---|---|---|---|
| Z F1 | 保留（门禁） | 远端实测 PR16 head=b0c0e8d3 | **保留**。→ R10-T01 | ROOT 精确 CI 票；merge 前 |
| Z F2 | 保留（维护） | 本轮新增归档稿 `round-10` 不在本轮产出（我只写仓外报告）；仓内 `docs/reviews/T02/**` 无新 raw 命名入树 | **保留**。 | 未来新增 raw/改规则时 |
| Z F3 | 保留（维护） | `scripts/engine-test-reporting.py` 与 `run-engine-tests.py` 的 `write_text`/`open("x", encoding="utf-8")` 均显式 utf-8（本轮我亲读确认） | **保留**。 | 原测试 owner 下次触及 |
| Z F4 | 保留（口径闭合） | 本轮未改这两脚本的 dump 调用面 | **保留**。 | 无待办 |
| Z F5 | 保留（维护） | `tests/unit/t02-manual-fact-id.test.ts:67` `resolve('.venv/bin/python')` 仍为显式 PATH python（另一处） | **保留**。两 TS PATH python 仍在。 | T01 测试维护者下次授权 |
| Z F6 | 保留（集合未集合化关闭） | definitions 早期 wire、裸 ownership、standalone EOF、缺码、无序、4299/4300 逐项仍在 78 表内 | **保留**。 | 各接线/维护事件 |
| Z F7 | 保留（HOLD 群） | 全部保留 | **保留**。 | 各 owner 对应验收前 |
| Z F8 | 保留（部分） | `rdf_snapshot.py` 分流在位；裸族两出口仍 `OWNERSHIP_CONFLICT` | **保留**。 | 未知/新家族接线前 |
| Z F9 | 保留（限本受审面闭合） | typed witness 授权链（`ownership_proof` → `_OwnershipProof` → `_application`）本轮我亲读在位 | **保留**。 | T01/T02 触及时 |
| Z F10 | 保留（观察） | 本轮未实测 GUI | **保留**。 | 既有 O047 证据接收维持 |
| MM R07-01 | 保留（已闭合） | 正向窄 literal 格式事实 | **保留**。 | 本次静态接收 |
| MM R07-02 | 保留（维护） | 无新 raw 名字入树 | **保留**。 | ROOT/T02 未来确增 raw 时 |
| MM R07-03 | 保留 | ruff 排除面仍不等 | **保留**。 | 将来独立配置票 |
| MM R07-04 | 保留（重新变开） | 状态文档实测仍停在 b0/R09 段 | **保留为重新变开**。→ F05 | ROOT 文档 owner，归档票后 |
| MM R07-05 | 保留（overlay 维护） | `AGENTS.md` 仍为未提交 overlay（实测 ` M AGENTS.md`） | **保留**。 | ROOT/指南 owner 维护时 |
| MM R07-06 | 保留（口径） | 双分母事实维持 | **保留**。 | 本次事实修订 |
| MM R07-07 | 保留（口径） | 本轮未改 payload 面 | **保留**。 | 原测试 owner，载荷变化时 |
| MM R07-08 | 保留（口径） | 父 FR/具名下游未逐类实测 | **保留**。 | 整父 FR/具名下游由原 owner 另验 |
| MM R07-09 | 保留（口径） | 无新复跑票 | **保留**。 | 本次事实修订 |
| MM R07-10 | 保留（口径，标题与正文差异） | 原「已定位并闭合」标题 vs 正文「差因未证」 | **保留原口径**。 | 无新复跑票 |
| MM R07-11 | 保留（观察） | 无 PR 说明更新 | **保留**。 | T02/ROOT 未来 PR 说明可解释 |
| MM R07-12 | 保留（HOLD） | rdflib 本地改版 | **保留**。→ R10-T07 | 原 vendor/发布 owner |
| MM R07-13 | 保留（维护） | `packages/contracts/src/v2.ts` 手写 SHA-256 与 TS 类型宽于 schema 的面仍在 | **保留**。→ R10-T09 | 契约 owner 下次授权整理类型时 |

**R06 组（20 项）**

| ID | 本人 R10 适用性 | 依据 | 处置 | 原owner／事件窗口 |
|---|---|---|---|---|
| R06 Z P1 | 保留（门禁） | 无 67 平台 CI | **保留**。→ R10-T01 | 合并前真实 CI |
| R06 Z P2 | 保留 | CI41 根因 UNPROVEN | **保留**。→ R10-T02 | 未来 CI 证据接收标准 |
| R06 Z P3 | 保留 | definitions 早期 wire 未被后置 catch 覆盖 | **保留**。 | T01 核心；原始 wire/Agent 接线前 |
| R06 Z P4 | 保留（部分） | typed witness 已实现；裸族仍延期 | **保留**。 | T01 详情合同 + T02 消费 |
| R06 Z P5 | 保留 | 错误码集合差仍在 | **保留**。 | 对应方法接线前 |
| R06 Z P6 | 保留（未确认观察） | SQL 无 ORDER BY 事实仍在 | **保留**。 | T01 下次触及 witness 选取时 |
| R06 Z P7 | 保留（沿既有决定） | canonical 政策未变；用户已采用既有 canonical 政策 | **保留**。 | 政策变更才新人类决定 |
| R06 Z P8 | 保留（逐项） | 集合已拆解至单行 | **保留**。 | 各原归口 |
| R06 D1 | 保留（门禁） | 无 67 CI | **保留**。→ R10-T01 | ROOT 正常票 |
| R06 D2 | 保留 | 状态文档仍停在 b0 | **保留**。 | ROOT 文档 owner |
| R06 D3 | 保留 | definitions 时序定性维持 | **保留**。 | T01 原归口；接线前 |
| R06 D4 | 保留（部分） | `singleDeclaration` 在 `storage.py:98`；其余理由三分类在 `:1226-1230` | **保留**。 | T01+T02；随家族接线处理 |
| R06 D5 | 保留（未确认观察） | 同 R06 Z P6 | **保留**。 | T01 下次触及选取时维护 |
| R06 D6 | 保留 | standalone EOF 残余（vendored `notation3.py`） | **保留**。 | T02 vendor/T01 入口；新解析入口前 |
| R06 D7 | 保留 | 缺 16 码集合事实成立 | **保留**。 | T01/T02 对应方法接线前 |
| R06 D8 | 保留（维护） | `t02-manual-fact-id.test.ts:67` PATH python 在位 | **保留**。 | T01 原测试维护者 |
| R06 D9 | 保留（口径） | Ruff 计数各时点原件保留 | **保留**。 | 文档 owner 归档后追加 |
| R06 D10 | 保留 | FR200 编辑后推导/保存查询/SHACL/报告四类具名下游 GUI 未逐类实测 | **保留**。 | 父 FR/消费链验收前 |
| R06 D11 | 保留（维护） | 应用层 4299/4300 边界断言未加 | **保留**。 | T02 输入边界 |
| R06 D12 | 保留（有界） | 已完成证据与独立 HOLD 分别保留 | **保留**。 | 无待办 |

**R04 组（14 项）**

| ID | 本人 R10 适用性 | 依据 | 处置 | 原owner／事件窗口 |
|---|---|---|---|---|
| R04 Z01 | 保留（未确认观察） | 同 R06 Z P6 | **保留**。 | T01 下次触及 witness 选取 |
| R04 Z02 | 保留（撤回维持，不复活） | 无新证据复活 | **保留**。 | T01 详情预算维护 |
| R04 Z03 | 保留（OPEN） | definitions 早期 wire | **保留**。 | T01；接线前 |
| R04 Z04 | 保留（部分） | typed/裸分开 | **保留**。 | 家族接线前 |
| R04 Z05 | 保留 | 集合差与可达性分开 | **保留**。 | 方法接线前 |
| R04 Z06 | 保留（沿既有决定） | canonical 政策 | **保留**。 | 无待办 |
| R04 Z07 | 保留（信息） | 规模信息接收 | **保留**。 | 无待办 |
| R04 M01 | 保留（历史演进） | 归档演进事实 | **保留**。 | ROOT 归档票 |
| R04 M02 | 保留（维持） | 无 hash 前提不采 | **保留**。 | 无待办 |
| R04 M03 | 保留（未来维护） | 4299/4300 | **保留**。 | T02；下次授权触及整数守卫时 |
| R04 M04 | 保留（OPEN） | standalone EOF | **保留**。 | 新解析入口前 |
| R04 M05 | 保留（OPEN） | 早期 definitions 不受后置 catch 覆盖 | **保留**。 | T01 |
| R04 M06 | 保留（维持分层，非绕过漏洞） | 双端 ID 校验链在位：`mainline-facts.ts` 派生 + `storage.py:494` 强制 + `t02-manual-fact-id.test.ts` 真实 Python 交叉 | **保留**。→ R10-T09 | 无待办；不外推为全产品安全认证 |
| R04 M07 | 保留（维护窗口） | 契约 owner API 整理窗口 | **保留**。 | 契约 owner 下次 API 整理时评估 |

**R05 组（21 项）**

| ID | 本人 R10 适用性 | 依据 | 处置 | 原owner／事件窗口 |
|---|---|---|---|---|
| R05 Z P1 | 保留（门禁） | 旧 79 全因未知 | **保留**。 | ROOT 合并门禁 |
| R05 Z P2 | 保留（事实闭合） | 934 Quality 718s 含 packaged recovery 成功为历史证据 | **保留**；不迁移为新 head CI 绿。 | 无待办 |
| R05 Z P3 | 保留 | 早期 definitions OPEN | **保留**。 | T01 接线前 |
| R05 Z P4 | 保留（部分） | 通用定位合同 OPEN | **保留**。 | 家族接线前 |
| R05 Z P5 | 保留 | 缺码非阻断延期 | **保留**。 | 方法接线前 |
| R05 Z P6 | 保留（口径） | canonical 语义观察接收 | **保留**。 | 无待办 |
| R05 Z P7 | 保留（口径） | 诊断选项演变事实接收 | **保留**。 | 无待办 |
| R05 Z P8 | 保留（重新变开） | 状态文档仍停在 b0 | **保留为重新变开**。→ F05 | ROOT 文档 owner |
| R05 MM01 | 保留（门禁） | 旧 79 原因仍未知 | **保留**。 | ROOT；新 CI 后、merge 前 |
| R05 MM02 | 保留（事实） | 934 两 success/Windows failure 为新阶段事实 | **保留**。 | ROOT/新 CI 后 |
| R05 MM03 | 保留（门禁） | 本 head 未打包 | **保留**。 | 新包制造票 |
| R05 MM04 | 保留（重新变开） | 状态文档归档义务未完成 | **保留为重新变开**。 | ROOT 文档 owner |
| R05 MM05 | 保留 | 缺码非阻断延期 | **保留**。 | 方法接线前 |
| R05 MM06 | 保留 | definitions 早期 OPEN | **保留**。 | T01 接线前 |
| R05 MM07 | 保留（部分） | Manual/SingleDeclaration 真 witness 与裸族分开 | **保留**。 | 家族接线前 |
| R05 MM08 | 保留（未确认观察） | 同 R06 Z P6 | **保留**。 | T01 下次触及选取时 |
| R05 MM09 | 保留（维持） | wheel/payload/解压量分层维持；冗余件见 F09 | **保留**。→ R10-T07 | vendor/发布 owner |
| R05 MM10 | 保留（维持，非候选缺陷） | AGENTS overlay 仍在（实测） | **保留**。 | 无待办 |
| R05 MM11 | 保留（信息） | locator 字段面实测仍为 `id/owner/sourceRow/slot`，无 object | **保留**。 | 无待办 |
| R05 MM12 | 保留（维护） | 两 TS PATH python 仍在 | **保留**。 | T01 原测试维护者 |
| R05 MM13 | 保留（信息） | 核心规模信息接收 | **保留**。 | 无待办 |

### 5.3 MM 额外 13 行（明确不充作原 78，不并入、不改写）

`round-09/disposition.md:339` 小节标题逐字为「### MM额外13行（不充作原78）」；`round-09/version-map.json` 中 `MMExtra13Separate: true`；`round-09/independent-minimax-disposition-audit.md:9` 逐字「160/31/78齐唯一，extra13不混原78，Top9/OBS10不漂移」。

**本轮处置：13 行逐条独立列出，维持 R09 各自状态标签，不并入 78、不改写其 ID、不改写其内容。** 我另记录一项**事实观察**（不影响其 ID 与状态）：这 13 行（R06 MM01–MM13）的处置文字与 §6 表内 `R05 MM01`–`R05 MM13` 逐条对应且用词一致，**疑似同一组 13 项在 R09 被换前缀后重复列出**；R08 时 MiniMax 原稿对同组使用的正是 `R05 MM01`–`R05 MM13` 标签（R08 时对 R06 轮次 MM 侧另用 `R06 MM D1`–`D12`）。因找不到 MiniMax 对前缀来源的原文解释，我**不判定**其为新发现，仅作为**ID 集合可能被高估 13 项**的审计观察记录，供后续轮次向原作者求证。本人**不**据此改写原 78 的任何一行。

| 额外ID | R09 状态 | 本人 R10 处置 |
|---|---|---|
| R06 MM01 | 仍开（门禁） | **保留**（旧 79 全因未知）→ R10-T01 |
| R06 MM02 | 已闭合（事实） | **保留** |
| R06 MM03 | 仍开（门禁） | **保留**（本 head 未打包/无新 CI）→ R10-T01 |
| R06 MM04 | 已闭合（分别承接）→ 240b581c 上重新变开 | **保留为重新变开**；本轮推进至 67b7bcbd 上仍变开（状态文档未归档 67 段，实测）→ F05 |
| R06 MM05 | 仍开 | **保留**（裸 ownership 家族） |
| R06 MM06 | 仍开 | **保留**（definitions 早期 wire） |
| R06 MM07 | 部分闭合 | **保留**（typed/裸家族分开） |
| R06 MM08 | 仍开（未确认观察） | **保留**（SQL 无序） |
| R06 MM09 | 已闭合（维持），冗余件见 F09 | **保留**；冗余件事实经本人实测仍成立 → R10-T07 |
| R06 MM10 | 已闭合（维持），overlay 仍在 | **保留**；overlay 经本人实测仍在 |
| R06 MM11 | 已闭合（信息），locator 字段面 | **保留**；本人实测 locator 仍无 object |
| R06 MM12 | 仍开（维护） | **保留**（PATH python） |
| R06 MM13 | 已闭合（信息） | **保留** |

### 5.4 R09 新增条目

**Z09 侧 10 条**（`round-09/disposition.md:22-31`）

| ID | 主题 | 本人 R10 处置 | 依据 |
|---|---|---|---|
| Z09-01 | 完整平台 CI 缺位 | **保留**（数值更新为 67b7bcbd）→ R10-T01 | 远端实测 |
| Z09-02 | CI41 根因 UNPROVEN | **保留** → R10-T02 | O059/O060/O062 分离 |
| Z09-03 | engine/Windows 后代退出 UNKNOWN | **保留** | O067 `unverified` 明列 |
| Z09-04 | 冗余 wheel 供应链 | **保留** → R10-T07 | 四个 wheel 实测并存 |
| Z09-05 | TS 契约宽于 schema + 双处 pageSize 64 | **保留** | `mainline-ownership.ts` 中 `pageSize: 64` 字面量两处（首请求与后续请求各一），`packages/contracts/src/v2.ts` 的 TS 类型由手写匹配器而非 schema 生成 |
| Z09-06 | 无 ORDER BY 观察，不升级缺陷 | **保留** | `storage.py` facts 查询 `ORDER BY id`；`_check_slot` 行选取无序 |
| Z09-07 | 4299/4300 消费断言缺 | **保留** | 应用层仅 4301 断言 |
| Z09-08 | 制品卫生 / always() 限制 | **保留** → R10-T08 | `ci.yml` artifact 路径与 `always()` |
| Z09-09 | readiness 耦合 Electron 内部映射 | **保留** | `native-driver.ts` base→67 差异级；Electron 内部映射随版本变动风险仍在（本轮未升级细读该 304 行差异，属 §3.2 差异级） |
| Z09-10 | 裸 ownership 家族无 typed witness | **保留** | `storage.py` 四类理由中裸族仍无 typed witness |

**MiniMax 侧 9 条**（`round-09/disposition.md:37-45`）

| ID | 级别 | 本人 R10 处置 | 依据 |
|---|---|---|---|
| F-R09-01 | P1 | **保留**：current67 realCI pending；累计 engine/spec 执行证据已存在；原 CI41 Quality/Windows 失败保留 | 远端实测 |
| F-R09-02 | P1 | **保留**：rootcause UNPROVEN 是 HOLD 与声明纪律，**不是**新增「合并前必须证因」门禁 | 与 R10-T02 一致 |
| F-R09-03 | P2 | **保留**：readiness-continues-helper 断言与 `app?.isPackaged` 建议已撤回；rootcause HOLD 仍在 | O067 记录 helper12 TypeError，但根因未定 |
| F-R09-04 | P2 | **保留**：Windows 观测（145.101449 nonpoll elapsed 等）不构成新合并门禁 | O067 case16 原文 |
| F-R09-05 | P2 | **保留**：failure-only annotation；成功 CI 无需失败样本 | 67 未造失败样本 |
| F-R09-06 | P2 | **保留**：证据绑定接收限制；A 属 base583→240 累计变更，2b→240 未改 | `run-engine-tests.py`/`engine-test-reporting.py` 在累计候选内 |
| F-R09-07 | P2 | **保留**：sys.path 等价限制；collector A 属 base583→240 累计变更 | `engine-test-reporting.py:69-80` identity 含 `pythonpath` 等 13 字段 |
| F-R09-08 | P2 | **保留**：指定文档 owner 的状态归档义务 | 状态文档实测停在 b0 → F05 |
| F-R09-09 | P2 | **保留**：完整 CI/制品接收纪律；ci.yml M 属 base583→240 累计变更 | 本轮 ci.yml 变更仍属累计范围 |

**观察项 OBS-R09-10**（P3，MiniMax）：**保留原处置**——「仅记录整数上限测试环境前提，沿原 T02 测试窗口，不新增门禁；4299/4300 原开放项不因此关闭」。本人未发现该前提在 67 中被错误固化。

### 5.5 两方 Top 清单

- **ZCode Top10（Z09-01…Z09-10）**：逐条已承接于 §5.4。
- **MiniMax Top9（F-R09-01…F-R09-09）**：逐条已承接于 §5.4。
- 本人 R10 的 Top10 见 §2（R10-T01…R10-T10），其中 R10-T04／T05／T06／T10 为**本轮本人新发现**，R10-T01/T02/T03/T07/T08/T09 为对历史 ID 的本轮收敛。

---

## 6. 门禁与完成度边界

**成立的事实**：PR16 open/unmerged，head=`b0c0e8d3`；`67b7bcbd` 未 push，无新 CI；develop 远端已前移至 `5f910b52`（与本候选 base `583c05c` 不同，属其他线）；整体合并可用仍 **2/17**；不推进 T04。

**继续保留原边界（本轮无一关闭）**：

- 完整 CI、完整 C1、完整 M0、当前新包与包内 GUI 验收；
- 签名、公证、整体法律/隐私/产权/供应链；
- 跨 OS 与参考设备（macOS15/Win11）、Q5/D2 容量、旧超限库恢复、损坏 SQLite 物理保护；
- 未具名下游家族、既有 79F、unknown parser/N3/Store/坏快照、Windows 后代 UNKNOWN、sys.path 等价限制；
- 既有 HOLD 与 UNKNOWN（含 Undo GUI 未验、standalone EOF、definitions 早期 wire、裸 ownership、缺码可达性、PATH-python、4299/4300、四类具名下游 GUI）。

**O068 部分 C1 PASS** 只补充该旧内容实际子集，不构成 CI41 根因证明，也不构成完整 C1 放行。

---

## 7. 建议（原 owner）

按证据归属建议，不新增职责：

1. **原 T02 owner**：在 `tests/e2e/ui-observation.ts` 的 `updateObservationSlot` 兜底分支按 16384 反算 base64 前缀长度（或明确改述常量语义），使 16KiB 声明在两条路径都成立（R10-T05）。**最小、不改断言**。
2. **原 T02 owner（前端归口）**：在 `mainline-facts.ts` 的 `AMBIGUOUS_FACT_SUPPORT` 判定处补注释说明其刻意严于引擎 `_check_slot` 的两点差异（受管行、单值谓词），并把是否透传引擎冲突路径留给既有维护窗口（R10-T10）。
3. **契约 owner**：把 TS `JSON.stringify([S,P,O])` 与 Python `canonical([S,P,O])` 的跨语言等价做成可执行检查（当前仅有 golden 向量覆盖）（R10-T09）。
4. **ROOT／CI 维护票**：把 Windows engine step 的名称改为中性描述并说明其退出码仍决定 job 成败（R10-T06）；同时确认 `build/engine-tests/` 与 `test-results/` 上传内容不含凭据/业务库后再固化 artifact 路径（R10-T08）。
5. **ROOT**：状态文档新增 67 段与归档 9 份证据（F05 重新变开）；本轮不代写（只读职责）。
6. **ROOT（精确 push 票）**：push 后按原 15/20 分钟跑完整三 job 并逐 node 核验（R10-T01）。若 CI41 case7/case16 复发，须定因并处置，而非仅解释。
7. **T11／发布**：merge 后受控窗口做包内实物核验与冗余 wheel 清理评估（R10-T07），不私自删件。

---

## 8. 本轮事实补正（对输入摘要的独立核对结果）

以下为本人**实测**发现、与输入摘要存在差异或需要限证之处，如实记录：

1. **O069 `COMPLETION.json` 的 `qualityRetryO068.handoff` pin（1803B／`2f8fbe97…57ed7`）指向 O068 目录的 `HANDOFF.json`，不是 O069 目录内的同名文件**（O069 自身 `HANDOFF.json` 实测 1530B／`6f8b3a00…d0c22`，未被 FINAL-MANIFEST 的 70 针收录，且被 COMPLETION 列为 `independentReview` 之外的交接件）。pin 内容本身真实（我实测 O068 该文件确为 1803B／同 hash），**不构成字节造假**；属**引用对象的隐含路径歧义**。
2. **O067 `HANDOFF.json` 实测 1245B**，其 pins 列的是 `COMPLETION.json`／`FINAL-MANIFEST.json`／`FINAL-FROZEN-GUARD.json`／`DIAGNOSIS-AND-NEXT-OPTIONS.md` 四项；这与「1803B」的 O068 文件不是同一物，二者不可混称。
3. **远端 develop 实际为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`**（本地与 `refs/remotes/origin/develop` 一致），与输入所述「develop=583c05c…」不同。本候选 base 仍为 `583c05c…`，不影响本轮判定；但「远端 develop」这一事实本身需按实况表述。
4. **O069 `FINAL-MANIFEST.json` 的 70 条 pin 我逐条重算，0 缺失、0 不匹配**；`fileCount` 字段为 70，条目实数亦为 70。O069 目录内另有 3 个文件（`FINAL-MANIFEST.json`、`HANDOFF.json`、`ROOT-SEND-RECEIPT.json`）按其自述**自我排除**，未计入 70 针——这与「70 针」的表述一致，不构成缺件。
5. **`staged.diff` 与实际 Git 差异逐字节相同**（我实测 `git diff b0c0e8d3 67b7bcbd` 输出 36240B，与 `staged.diff` 完全一致），故该 patch 精确等于真实提交差异，无「声明与实际不符」。
6. **R09「额外13」与原 78 中的 `R05 MM01`–`MM13` 疑似重复**（用词逐条一致），本人**不判定**为新发现，仅记录为 ID 集合可能被高估 13 项的审计观察。
7. 本轮 4 个只读子代理**全部在收尾阶段因网络中断未交付终稿**，本报告**不引用任何子代理结论**；所有判定与事实均来自本人亲读代码与原件。

---

## 9. 结论

**ConditionalPass（限定技术阶段）。**

- 在本人亲读范围内（67 新增 4 文件全文、累计候选产品/契约/引擎/脚本/CI/依赖差异级、O065–O069 原件实测、160 项清单逐项判定），**未发现 push 前源码技术阻断**。
- 本候选 67 的 4 路径变更（631+/43−）只触及测试与测试辅助层，**未改动生产代码、契约、依赖、CI 配置或验收标准**；其新增的 UI 观测层在「严格唯一、完整文本、原始输入值、按钮消失不等于成功、有界诊断槽」等关键点上均**加强**而非削弱断言强度。
- 本人新发现 3 项 P2 与 1 项 P2/P3 观察（R10-T04/05/06/10）均为**保守方向**（更严或更明确），不构成阻断，且均**不改变任何已断言的业务结果**。
- 合并仍受 R10-T01 门禁约束：67 未 push、无新 CI；完整三 job、完整 C1/M0、当前新包与包内 GUI、签名公证、法律隐私产权供应链、跨 OS 与参考设备、容量与损坏库保护等原 HOLD 全部保留。
- 整体合并可用仍 **2/17**，不推进 T04。R09 的 ConditionalPass 不转移，本轮为独立重判。

**本报告不含任何「本人运行过」的测试事实。** 所有测试与 CI 数字均来自标明身份的既有原件并标注其执行时点与局限。必要运行建议已按归属列入 §7。

---

*报告结束。本方：MiniMax；模型 M3.1-Flash；思考等级 xhigh；权限 始终授权。本报告写于仓外指定路径 `/Users/kyle/Documents/工作/知爻/本体/outputs/20261027_t02_67b7_fresh_r10_070/minimax/report.md`；未在 worktree 内写入任何文件，未改动源码/测试/依赖/配置，未 git add/commit/push/切分支/触发 CI/merge。*


---

# 10. 追加：本轮集中更正与有效替代关系（同一 R10 任务内，续首稿 §9 之后）

**本节性质**：以下为**本人**对首稿 `minimax-natural-01.md`（93024B／SHA256 `59bb1066…d4d8b5`，与 `minimax/report.md` 在本次追加前逐字节相同）的**集中更正**。首稿 93024B 全部原前缀**一字未改、未格式化、未替换尾行**（首稿末尾「报告结束…」行按原样保留，本节续于其后）。首稿 §1／§9 的 **ConditionalPass（限定技术阶段）作为首稿原判原样保留**；§2 的 R10-T01…T10 编号与原句**全部保留**，本节只给出其**新有效处置**与**替代关系**。

**边界**：本节不重开轮次、不改源码/测试/依赖/配置/需求/验收、不跑任何 check/vitest/pytest/build/package/formatter/HMR/产品/GUI/SQL/bridge 探针、不 git add/commit/push/切分支/CI/merge、不新设 scope/owner/门禁、不改任何既有 HOLD/UNKNOWN/OPEN 的原判归属。**本节同样不含任何「本人跑过」的测试事实**；所列新事实均为本人**只读实测**（Git 只读命令、源码直读、原件直读、纯文本/JSON/行数计算）。模型／思考等级／权限不变（M3.1-Flash／xhigh／始终授权）。

## 10.1 远端与 status 事实更正（撤回「远端已前移」推断）

| 项 | 首稿所写（§0 L30／L32、§8 第 3 条） | 有效替代 | 依据（本人本轮只读实测） | 原 owner／窗口 | 是否源码阻断 |
|---|---|---|---|---|---|
| 远端 `develop` | 「远端 develop 实测 `5f910b52c69d…`（本地与 origin/develop 一致），与输入所述 `583c05c…` 不同」 | **撤回该事实推断**：`5f910b52…` 是**本地缓存 refs**（`refs/heads/develop` 与 `refs/remotes/origin/develop` 实测同值），**不是当前服务器分支状态**。「远端已前移」的表述不成立 | 本人执行只读 `git ls-remote origin`：**`refs/heads/develop = 583c05c7870ba0f8f642e3eeea1d0590e5859ca2`**、**`refs/heads/feature/weekly-t02-fr200-fr201 = b0c0e8d37954a3b8c2563b6068d6ca3d151a8dd1`**；`git remote -v` 实测 origin URL = `https://github.com/NOmoreJoke/OntoLearn-Studio.git`（与 owner 提供的 `remote-after-natural-01.stdout` 原件一致）。**未执行 fetch／rebase／任何写操作** | ROOT 精确 push/CI 票；不改 base／fetch／rebase | 否 |
| 本候选 base | `583c05c…` | **维持不变**（首稿正确） | 同上：服务器 `develop` 实测仍为 `583c05c…`；本候选 base 未改 | ROOT | 否 |
| 工作树脏项 | 「`git status --porcelain` 仅**三项**」 | **有效表述**：`porcelain` 实测 **4 行** = ` M AGENTS.md`（1 行，已跟踪修改）＋ 3 个未跟踪目录 `round-01/`、`round-02/`、`round-03/`（各 1 行）。「**三目录**」与「**三项**」分清 | 本人实测 `git status --porcelain` 的行数 = **4**；index 实测为空 | 不据此改动 WIP 原计数 | 否 |

## 10.2 Top 风险的撤回与收窄（旧编号／旧句保留，给出新有效处置）

首稿 §2 的 10 个 stableID 与原句全部保留。下表给出本轮**本人自查后的新有效处置**。**不为凑满 10 项新增任何问题**；有效项由 10 收缩为 6。

| stableID | 首稿原句（保留） | 新有效处置 | 依据（本人本轮只读实测） | 原 owner／窗口 | 是否 push 前源码阻断 |
|---|---|---|---|---|---|
| R10-T01 | 完整平台 CI 缺位，合并门禁未开 | **保留（合并门禁）** | `git ls-remote` 实测服务器 `feature/weekly-t02-fr200-fr201` 仍为 `b0c0e8d3…`，67 未 push、无新 CI | ROOT 精确 push/CI 票 | 否（但阻断 merge） |
| R10-T02 | CI41 Quality C1 根因仍 UNPROVEN；67 的观测层修复不等于根因证成 | **保留** | 与 §10.7 的 `R06 Z P2` 主题更正**分离**：CI41 根因仍是独立未证项 | 未来 CI 证据接收标准 | 否 |
| R10-T03 | Windows FR201 整例 180s 超时，末权威业务终态仍未知 | **保留** | O067 `WINDOWS-CI42-FAILURE-FACTS.json`：case16 `durationMs=180010`、`status=timedOut` | 未来 CI 证据接收标准 | 否 |
| R10-T04 | 67 的 UI 观测层只覆盖 `native` 形态，其他形态 fail-closed——覆盖面限制 | **保留（覆盖面限制）** | `tests/e2e/ui-observation.ts:32-56`（unsupported／ambiguous／role-name override 均 fail-closed） | 原 T02 测试维护者 | 否 |
| R10-T05 | `updateObservationSlot` 的 16KiB 上限在 base64 兜底分支下**不保证**最终字节 ≤ 16384 | **撤回原证明与原建议**（保留编号与原句）。原证明「11000B base64 ≈ 14668B ＋ JSON 字段**必然大于** 16384」**不成立**：兜底分支丢弃 `observed`、只保留 `stage`／`at`／`monotonicMs`／`truncated`／`originalBytes`／`utf8PrefixBase64`／`boundary` 固定字段，固定开销经本人独立复算为 **212B**（不含 `stage` 与 base64 本身）。**新有效处置**：不再列为当前缺陷；仅保留一条**尚未证明当前可触发**的维护边界——兜底分支无二次长度复核，若 `stage` 长度增至约 **1538 字符**以上（实测余量 1504B），最终 `description` 可能超出 16384。**据此的前缀改法建议一并撤回** | 本人按 owner 给定的反例形态**独立复算**（纯 JSON/UTF-8/base64 计算，不 import helper、不跑产品/测试）：`stage='actual fresh readProject completed'`、`at='2026-10-27T00:00:00.000Z'`、`monotonicMs=123456.789`、`observed` 为 250 个 4000 ASCII 串，取 11000B 前缀后 base64 = **14668**、兜底最终 **14914B < 16384**（本人复算值与 owner 反例一致；`observed` 的具体形态不改变最终长度，只有 `originalBytes` 的位数会变）。源码复核：`ui-observation.ts:179-190`（兜底分支不含 `observed`）；`tests/unit/ui-observation.test.ts:178/191` 实测存在 `expect(Buffer.byteLength(saved)).toBeLessThanOrEqual(16384)` 与 `…(capped)…` 两条实际长度断言。**受审 stage 实参**：仅两个调用点（`t02-fr200-fr201.spec.ts:83`、`mainline-consumer-first-ack-loss.spec.ts:271`），stage 为调用方传入的有限常量 | 原 T02 测试维护者（命名/常量归口）；**本票不改码** | 否（撤回后为零） |
| R10-T06 | CI Windows 分支把 `engine:check` 降级为「diagnostic」，但该 step 仍会以其退出码决定 job 成败——命名与实际门禁语义不一致 | **撤回「命名与门禁语义不一致」这一缺陷判定**；**保留真实保守语义**（Windows first-failure diagnostic step 失败即 job 红），与「不是完整验收凭证」**不矛盾**。**不建议**用 `continue-on-error` 解决命名或证据问题；命名维护归 ROOT 窗口，**本票不改 CI** | `.github/workflows/ci.yml` Windows 分支：step 名含「first-failure diagnostic (not acceptance)」，且**无** `continue-on-error`；失败即红的保守语义**本就正确**，首稿把「命名易被误读」当成了语义缺陷 | ROOT／CI 维护窗口 | 否 |
| R10-T07 | vendored rdflib 是本地改版 wheel，供应链与许可为独立 HOLD，仓库内并存三个版本 | **保留** | `packages/engine/vendor/rdflib/PROVENANCE.json`（`officialUpstreamUnchanged:false`）、`pyproject.toml`／`uv.lock` path wheel、`licenses/NOTICE` | 发布/供应链 owner | 否 |
| R10-T08 | CI 制品上传范围扩大 ＋ `failure-traces-linux` 改 `always()` | **保留** | `.github/workflows/ci.yml` artifact 路径与 `always()` | CI 维护票 | 否 |
| R10-T09 | `newManualFactPlan` 改为内容派生 ID 后，renderer 必须与 Python `Store.digest` 逐字节一致——我已实测当前形态一致，但**耦合无机器校验** | **撤回标题与正文中的「无机器校验」表述**：仓库**存在真实的 Python 机器交叉核验**——`tests/unit/t02-manual-fact-id.test.ts`（本人本轮直读 50–90 段）以 `spawnSync(resolve('.venv/bin/python'), ['-I','-c', pythonCheck, resolve('packages/engine/src')], …)` 调用**真实 `Store._fact` 与 `digest`**，并与 golden 向量逐条比对 `record['id']==digest(values)` 与 `canonical` 输出。`resolve('.venv/bin/python')` 是**显式路径**，**不是**旧裸 PATH python 问题（那两处另见 §10.7 的 `Z F5`／`R06 D8`）。**新有效处置**：收窄为「**未穷尽 Unicode 全空间与未来组合**」的残余风险，非「无机器校验」；原最小建议（补一条覆盖全部 Unicode 形态的机器检查）随之收窄为「扩样」而非「从零建立」 | 本人直读 `tests/unit/t02-manual-fact-id.test.ts:50-90`；首稿已自行承认该文件存在 cross-test，与标题自相矛盾；本人本轮另实测 JS `JSON.stringify` 与 Python `canonical` 对 7 组实际形态逐字节一致 | 原 T02 测试维护者；**本票不改测试** | 否 |
| R10-T10 | `manualFactPlan` 的「多值事实」判定放宽后，同 slot 多条手动事实的歧义判定与引擎 `_check_slot` 语义不完全对齐 | **撤回「renderer 可能更早拒绝 ⇒ 构成缺陷」的推断**：首稿据「原 ID edit／tombstone 存在时 ID 与现值不恒等」推出语义差，**该等价推断不成立**。真实实现中 `reserved_id = digest([subject,predicate,value])`（`storage.py:1211`）与「live object 值／单值谓词」是**独立判断**：`storage.py:1216-1218` 条件为 `row["id"] not in excluded and (row["id"] == reserved_id or (row["object"] is not None and (single or row["object"] == value)))`，`reason` 为 `reservedIdentity`／`sameStatement`／`singleSlot`（`:1226-1228`）。ID 绑定原声明本就是设计（`storage.py:1510`「ID stays bound to the original statement across edits」），**不能据此推出缺陷，更不能据此改契约**。**新有效处置**：降为**可选注释澄清**（若原 T02 前端归口愿意，可补一行说明 renderer 判定刻意严于引擎 `_check_slot` 的两点差异），**非阻断维护项**，不改契约、不改行为 | 本人直读 `packages/engine/src/ontolearn_engine/storage.py:1197-1231` 全文；`OWNER-PRIMARY-MINIMAX-FACTS-01.json` 同一区段摘录与本人读数一致 | 原 T02 前端归口；**本票不改码** | 否 |

**更正后有效 Top 清单**：**保留 6 项**（R10-T01／T02／T03／T04／T07／T08）＋ **撤回 2 项**（R10-T05 证明撤回、T06 缺陷判定撤回）＋ **收窄 2 项**（R10-T09 改「未穷尽 Unicode/未来组合」，T10 改「可选注释澄清」）。**push 前源码技术阻断仍为 0 项**。首稿「Top 统计」段原句保留于 §2，本节为唯一有效处置。


## 10.3 §4.1 逐项标签的有效替代（首稿 §4.1 表 160 行原样保留，本节给出逐行替代）

下表按**权威原件行号**（`ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt` 的 160 条 `> ` 行）列出本轮因事实更正而**标签或依据发生变化**的 20 行；**其余 140 行首稿判定与依据原样有效**。**行号不变、判定词只用「适用（正面）／部分适用／不适用／无法确认」四档、复合判定仍自成一档且每行只计一次**。

| # | 权威原问题（片段） | 首稿判定 | **有效判定** | 有效依据与更正理由（本人本轮只读实测） |
|---|---|---|---|---|
| 19 | backups every night | 不适用 | **部分适用** | **代码能力在**：`storage.py:1839-1847` 的 `Store.backup(destination)`（SQLite 在线备份 API，目标必须为新文件）；`storage.py:209` 在格式迁移前调用 `project/format3.py:158 migration_backup(...)`（`PRAGMA integrity_check` ＋ 文件与父目录 `fsync` ＋ 备份证明哈希，缺目标即 `Format3Fault("backupRequired")`）。**未证门禁**：无夜备调度/自动化、无保留与轮转策略、无异地副本。首稿「M0 未实现备份」把「无夜备自动化」误述为「无备份能力」。 |
| 20 | a restore from those backups, tested | 不适用 | **部分适用** | **恢复面部分在**：快照级恢复/补偿在 `project/transactions.py:285 preview_restore(project, snapshot)` 与 `project/compensation.py:118`（`{"kind":"restore","snapshotRef":…}`）；`Store.backup()` 产物是合法 SQLite 库，可作为项目重新打开。**未证门禁**：**没有**针对 `backup()` 产物的恢复入口与**恢复演练证据**；损坏库/旧超限库恢复仍属保留 HOLD；`integrity_check` 只在迁移备份路径内执行。 |
| 26 | emoji, accents and right-to-left text in every field | 适用（正面） | **部分适用** | **已覆盖的是引擎层 Unicode 与语言语义**：`storage.py:24-31` canonical `ensure_ascii=False`（本人实测与 JS `JSON.stringify` 对 7 组实际形态逐字节一致）、`rdf_snapshot.py` 的 `term()`／`iri()`、`packages/engine/tests/test_mainline_language_input_rejection.py`（`@en-001`／`@de-ch-1901`）、`mainline-facts.ts:56-64` 显式拒绝孤立代理项。**未覆盖的是界面层**：本人全量 grep renderer 的 `dir=`／`unicode-bidi`／`direction:` —— **0 处命中 RTL 处理**（仅命中 `flex-direction`）；亦无 emoji/重音的界面级专项用例。首稿据引擎层证据推出「每字段全覆盖」的正面判定，属**过度外推**。 |
| 31 | deduplication for the user who clicks submit four times | 不适用 | **部分适用** | **去重/幂等链在**：事实 ID 内容派生（`mainline-facts.ts:73-80`，见 R10-T09）、`storage.py:1820/1836` 的 `replayable` 判定、`project/mainline.py:890`「Accepted creation replays from its authenticated immutable…」、作业链以 `operationId`／`JobID`／receipt marker 结算（O069 实测 singlecommit=1／execute=0／replay=0）。**未证门禁**：**无「连点四次」的重复/并发提交用例**；O069 的「43 拒绝」是**冲突拒绝**（42 INVALID ＋ 1 ownership），**不是多击试验**。首稿称「无重复提交去重」不准确。 |
| 32 | pagination that still works on page 400 | 不适用 | **部分适用** | **有界分页在**：`project/query_presentation.py:381` 约束 `pageSize > min(200, limits["maxPageItems"])` 即拒绝，`:128/130/232/443` 以 `RESOURCE_LIMIT`（page/frame/memory）保护；ownership 详情为分段有界分页（`job_store.py:932-977 ownership_detail_page` ＋ `packages/contracts/src/index.ts` 的 `reassembleOwnershipDetail` 限额 nodes≤16384／depth≤8／单串≤43692）。**未证门禁**：超大页号与百万行规模未测，原生 24 例只覆盖有限行数与**当前页 CSV 子集**。首稿「无分页列表产品面」与源码不符。 |
| 33 | exports … data in a spreadsheet | 不适用 | **部分适用** | **有限 CSV 导出在**：`apps/desktop/src/renderer/src/query/QueryResultPanel.tsx:16-17` 的 `downloadCsv` 生成带 BOM(`\uFEFF`) 的 `text/csv;charset=utf-8` Blob，`:252` 导出 `query-ask.csv`、`:319` 导出 `query-current-page.csv`（**当前页**子集）；`packages/contracts/src/v2.ts:863/980` 对 `format==='csv'` 与 cell kind 做契约校验。**未实现**：Turtle 等语义格式**未**作为用户导出面接通（`query_presentation.py:263-269` 的 `LexicalSink(..., turtle=True)` 是内部语义序列化，不是导出产品面）。 |
| 41 | protection against SQL injection, XSS, CSRF and the rest of the OWASP list | 适用（正面） | **部分适用** | **SQL 面已闭合**：全部参数化（`storage.py` 的 `WHERE project=? AND id=?` 等），动态表名取自 `sqlite_master` 并做 `"`→`""` 转义。**XSS 面有机制、未专项验证**：renderer `dangerouslySetInnerHTML` 实测 **0 处**，React 默认文本转义，`apps/desktop/src/csp.ts` 为 CSP 唯一来源且**本候选未改该文件**（实测 base→67 无差异），生产脚本无 `unsafe-inline`/`unsafe-eval`（唯一 `unsafe-inline` 在 `csp.ts:20` 的 style-src 开发 HMR 分支）；但**无 XSS 专项用例**，且用户输入的 RDF 字面量／IRI 确实以文本渲染进界面（渲染隔离成立、专项回归未做）。**CSRF**：本地无浏览器网络面。首稿「无浏览器网络面故无 XSS/CSRF」把「无网络面」当作「无 XSS 面」，属**过度外推**，与本地架构成立、与该清单项的适用性不成立。 |
| 57 | GDPR deletion requests that reach every table, backup and log | 部分适用 | **无法确认** | **可观测代码事实**：无账号体系、无用户删除请求通道；数据分层规则（历史不可改写、缓存回收不得触及历史）与备份/日志面均为本地单机。**但**：是否受 GDPR 约束、是否存在个人数据主体、删除请求的法律义务与范围，属**法律/组织事实**，**不能由本地架构作法律结论**。首稿据分层规则推出「部分适用」，实为代码事实，不构成法律判断。 |
| 69 | background job queues, so slow work doesn't freeze the page | 部分适用 | **部分适用（依据重写）** | **首稿依据错误已更正**：「耗时业务能力尚未接入（M0 正式领域能力仍只有 health 级）」与实际不符——`coordinator.py:502` `formal = self.version == 3 and p["capability"] == "changeset.commit"`，`:523 create_changeset_job`、`:644 execute_changeset` 把**领域 changeset 提交作为作业执行**；`job_store.py` claim kind 含 `job`／`application`／`query`，协调器有 `_progress`／`_stage`／`_notify` 与取消/心跳（ADR-0003 常驻协调器）。**未证门禁**：是否把耗时操作普遍后台化、队列持久化/重试/死信策略未成制度。 |
| 73 | caching, and clearing that cache when the data changes | 部分适用 | **部分适用（依据重写：机制与下游分开）** | **九例失效机制已在引擎层验证**：`packages/engine/src/ontolearn_engine/invalidation-v2.json` 实测 **9 条规则**（appendixRow 1–9；家族 ontology/facts/mapping/constraint/rule/behavior/scenario/query/model；第 9 条 model 的 `staleReason` 为 `null`，与 AGENTS「仅改模型配置不使领域结果过期」一致），`packages/engine/tests/test_job_store.py` 实测存在多条 `staleReason` 断言（含 `mid_invalidation`、迟到/历史态传播）。**仍缺的是四类具名下游的 GUI 逐类实测**（编辑后推导／保存查询／SHACL／报告，见 `R06 D10`、`MM R07-08` 的原 OPEN）——该缺口属**下游 GUI 验收**，**不抹除**九例机制已验的事实。首稿把两者并入「九行正反例未逐类 GUI 实测」，属**未分开**。 |
| 96 | testing on the five-year-old laptop … | 不适用 | **部分适用** | 该要求在产品计划中**明确挂起而非不存在**：M0 更新计划第 181／183 行逐字写明「Q5 容量与参考设备」为待产品确认项，并写明「在宣称容量达标前明确目标与参考设备」。**未实施不等于不适用**；本轮未测，参考设备与跨 OS 仍属保留 HOLD。首稿以「该测试本身未实施」判不适用，属**把未实施当作不适用**。 |
| 97 | accessibility compliance, because the enterprise contract requires it | 不适用 | **部分适用** | **界面确有语义可达基础**：renderer 实测 77 处 `aria-*`／`role` 用法，含 `role="status" aria-live="polite"`（`App.tsx:607/680/693`）、`role="alert"`（`OntologyMainlinePage.tsx:159/166/196`）、`aria-label` 区域标注；67 的 e2e 以 `getByRole` 精确角色+名称为**唯一定位源**。**缺口**：无 a11y 合规验收、无专项用例；M0 计划与 m0-checklist 中**无** a11y 条目（本人 grep 0 命中）；「企业合同要求」这一前提属**组织/法律事实**。 |
| 129 | keyboard navigation and screen reader support | 部分适用 | **部分适用（证据为完整 replacement，见 §10.6）** | 首稿该行证据**截断于** `` `role="status"` `` 处，属不完整输出。本轮给出完整 replacement（§10.6）。 |
| 135 | monthly dependency upgrades … | 不适用 | **部分适用** | **机制部分在**：`.github/dependabot.yml` 实测存在（npm 与 github-actions 两生态、`directory: /`、`interval: weekly`、`target-branch: develop`、npm `open-pull-requests-limit: 5`）；历史核对：`round-08/disposition.md:31` 已纠正「全无节奏」的暗示。**缺口**：**无 Python/uv 生态条目**、无月度节奏、无实际运行/合并记录、无 SLA/EOL 核验；`packages/engine` 的精确锁定依赖仍无自动更新通道。 |
| 136 | framework upgrades before the old version stops getting security patches | 不适用 | **部分适用** | **需求真实且有具体依赖**：桌面端框架为 Electron（`package.json` 精确版本），其安全补丁节奏是真实维护压力，并已与 `Z09-09`（readiness 耦合 Electron 内部映射）挂接。**缺口**：无「停止支持前必须升级」的制度、无 EOL 监控、无跨版本验证矩阵。 |
| 138 | splitting up the 2,000-line file … | 不适用 | **部分适用（事实更正）** | **首稿事实断言与固定 67 相反，已更正**：「无 2000 行单文件／产品源文件均在数百行内」**不成立**——本人实测 `packages/engine/src/ontolearn_engine/job_store.py` **2993 行**（128502B）、`storage.py` **1887 行**（84495B）、`tests/e2e/t02-fr200-fr201.spec.ts` **1942 行**。历史核对（仅作事实来源，不继承其判断）：`round-05/minimax-m31flash.md:264` 记「Z-07 文件增长｜信息级｜aff 实测 2993／1887／1748」；`round-04` 原稿把同一事实列为「适用·未达标（信息级）」。**行数本身不是质量结论**；本候选未做拆分，拆分属维护窗口。 |
| 146 | every account, domain and repo in the company's name … | 部分适用 | **无法确认** | **可观测事实**：远端 origin URL 实测 `https://github.com/NOmoreJoke/OntoLearn-Studio.git`。**不能推出**：该主体是公司还是个人、域名与账号是否合规、发布主体归属——属**组织/法律事实**，**不能由 GitHub 用户名形态推定「不合规」，也不由 AI 双审推定「已履行」**。发布/法律 HOLD 保留。 |
| 147 | a bus factor higher than one | 部分适用 | **无法确认** | **可观测事实**：文档与 owner 归口清晰、ADR 齐备，且本轮存在**独立于修复者本人**的复审流程（本人只读复算 70 针、`staged.diff` 逐字节比对等）。**不能推出**：是否存在第二名能复现与接手的人——属**组织事实**，**不能由「当前是 solo 架构」推定「无义务」，也不能由「有双审流程」推定「巴士系数>1 已履行」**。组织 HOLD 保留，不新增门禁。 |
| 153 | patching the framework the week a vulnerability goes public | 不适用 | **部分适用** | **依赖与压力真实存在**：桌面端框架为 Electron，其安全公告与补丁节奏是真实维护面，与 `Z09-09`／`R08 Z P10` 的升级事项同族；仓库已有 dependabot 机制可承接部分升级。**缺口**：「公开当周打补丁」是**组织 SLA/流程事实**，代码不能证明其是否被承诺或执行；亦无 EOL/公告监控机制。 |
| 156 | running a migration on a live database without losing a row | 不适用 | **部分适用** | **迁移机制在且带保全**：`project/format3.py:158-185 migration_backup` 在迁移发布事务前完成备份（`PRAGMA integrity_check` ＋ 文件与父目录 `fsync` ＋ 备份证明哈希；缺目标即 `Format3Fault("backupRequired")`），`storage.py:209` 在迁移分支调用它，迁移事务以 `logical_hash` 比对源库、源在迁移期间被改动即 `Format3Fault("sourceChanged")`。**未证门禁**：**未做**活跃库迁移的行级保全演练，「一行不丢」未证，该演练属原 HOLD。 |

## 10.4 更正后**唯一有效**统计分布

首稿 §4.2 的 **18／35／102／5（合计 160）作为首稿当时原判原样保留**（首稿表体未改）。本节给出本轮更正后的**唯一有效新分布**，由上表 17 处标签变化**程序化得出**（非手填）：

| 判定 | 首稿（当时原判，保留） | **有效新分布** | 变化来源 |
|---|---|---|---|
| 适用（含「适用（正面）」） | 18 | **16** | #26、#41 由「适用（正面）」下调为「部分适用」 |
| 部分适用 | 35 | **46** | ＋12（#19、#20、#31、#32、#33、#96、#97、#135、#136、#138、#153、#156 由「不适用」上调）＋2（#26、#41 下调落入）−3（#57、#146、#147 移出） |
| 不适用 | 102 | **90** | −12（#19、#20、#31、#32、#33、#96、#97、#135、#136、#138、#153、#156） |
| 无法确认 | 5 | **8** | ＋3（#57、#146、#147） |
| **合计** | **160** | **160** | 行号集合不变，仍为 1–160 严格逐行对应权威原件 |

**结构事实不变**：160 行、min 1／max 160／missing ∅／dup ∅、每行只出一档且只计一次；复合组仍为 **#148–#160 共 13 行**，分布为 **无法确认 4（#148–#151）／不适用 6（#152、#153、#154、#156、#157、#159）／部分适用 3（#155、#158、#160）**。

## 10.5 §4.2 末 13 项示例的 #157／#158 互换更正

首稿 §4.2「复合判定说明」的末 13 项枚举中，**把 #157 与 #158 互换了**（首稿把 #158「works for every customer」列入不适用、把 #157「saying no to the feature that breaks three others」列入部分适用）。**首稿原文保留，本节为有效替代**：正确分布为

- **无法确认 4 项**：#148 逐行人审、#149 第二个客户前设计数据模型、#150 解释修复引入的新缺陷、#151 部署/回滚/云账单；
- **不适用 6 项**：#152 支付值班、#153 漏洞当周打补丁、#154 审计员演示、#156 活跃库迁移保全、**#157 技术负责人否决**、#159 调试 AI 写不出的代码；
- **部分适用 3 项**：#155 QA、**#158 把「在我机器上能跑」变成「对每个客户都能跑」**、#160 一年后仍记得为什么这样建。

**统计总数本身仍正确（160），但统计正确不等于语义正确**——本节更正的是逐项归类语义，不改总数。

## 10.6 §4.1 #129 的完整有效 replacement（首稿该行证据截断，现补全）

首稿 #129 行证据在 `` `role="status"` `` 处截断，属**不完整输出**；行号与判定（部分适用）不变，**完整 replacement 如下**：

> **#129｜部分适用**：「键盘导航与屏幕阅读器」——**语义基础在**：renderer 实测 **77 处** `aria-*`／`role` 用法，含 `role="status" aria-live="polite"`（`App.tsx:607/680/693`）、`role="alert"`（`OntologyMainlinePage.tsx:159/166/196`）、`aria-label` 区域与分组标注、`aria-current`／`aria-disabled` 导航状态（`App.tsx:503-525`）；`OwnershipConflictDetailView.ts:61/70/80` 以 `aria-label` 标注首个阻断冲突定位、冲突声明与原始事实定位；67 的 e2e 以 `getByRole` 精确角色+名称作为**唯一定位源**（不靠 CSS 选择器、不用截断文本、不用 first 匹配遮重复），即**可访问名称已是产品契约的一部分**。**缺口**：renderer 全量 grep `tabIndex`／`onKeyDown`／`onKeyPress`／`keydown` 实测 **0 处**——**无显式键盘可达与焦点管理实现**；无屏幕阅读器实测、无 a11y 合规验收、无键盘导航专项用例；「企业合同要求」前提属组织/法律事实，无法确认。判定为部分适用（语义标注在，键盘与读屏未验）。

**#138 的事实更正**已在 §10.3 表内给出（2993／1887／1942 行实测），其完整 replacement 为：

> **#138｜部分适用**：「拆掉 AI 一直追加的那个 2000 行文件」——该现象**真实存在**：`packages/engine/src/ontolearn_engine/job_store.py` 实测 **2993 行**（128502B）、`storage.py` **1887 行**（84495B）、`tests/e2e/t02-fr200-fr201.spec.ts` **1942 行**（首稿称「产品源文件均在数百行内」与固定 67 相反，已更正）。历史核对：`round-05/minimax-m31flash.md:264` 已把同一事实记为「Z-07 文件增长｜信息级｜aff 实测 2993／1887／1748」。**行数本身不是质量结论**，本候选未做拆分，拆分属维护窗口。判定为部分适用。


## 10.7 历史 stableID 的真实主题更正（原 owner／窗口维持，主题不得被我错配）

首稿 §5.2／§5.3 的 31／78／13 行**ID 集合、行数与行序全部保留**；下表只更正**我错配或无依据的主题**，**不删行、不改 ID、不改状态标签归属、不新增门禁**。依据为本人本轮直读原件：`round-09/disposition.md`（363 行）、`round-08/disposition.md`（161 行），及本方更早原稿的对应行。

| stableID | 首稿所记主题 | **有效主题（据原件）** | 本人处置 | 原 owner／事件窗口 | 是否源码阻断 |
|---|---|---|---|---|---|
| Z08-05 | 「O059 已到 helper12；O060/O062 止于 EPERM」（= CI41 helper 主题） | **两处裸 PATH python 在位 ＋ O056 双原件 ＋ 双向因果限定**：`round-08/disposition.md:26` 逐字为「本人 grep 两处在位（:656/:168）；O056 保留首次 ENOENT 失败与正确 uv 通过双原件」，并把 v1.0「已知与 79F 归因无关」更正为「不作为 79F 根因认定，亦不能排除其为部分环境因素」；`round-09/disposition.md:226` 记「仍开（维护），本轮实测复核代码事实仍在」 | **保留（仍开·维护）**，并**与 CI41 helper12 主题分离**——后者归 §2 的 R10-T02 与 §10.7 的 `R06 Z P2` | T01 原测试维护者下次授权触及环境/测试时；**无需重跑旧失败填因果** | 否 |
| Z08-10 | 「`pyproject.toml` 的 ruff exclude 新增 `docs/reviews/T02/.../round-[0-9][0-9]/{zcode-glm53,minimax-m31flash,…}.md`」 | **dependabot 节奏与核验**：`round-08/disposition.md:31` 逐字为「本人实读 dependabot.yml（npm+github-actions，均 directory /，weekly，target develop；npm open-pull-requests-limit 5）；实际运行/合并记录、uv/vendor 跟进、SLA/EOL 未证——纠正 v1.0『全无节奏』暗示」；`round-09/disposition.md:231` 记「仍开（部分采纳维持）」 | **保留（仍开·部分采纳维持）**。首稿引用的 ruff exclude 事实**在仓库中真实存在**，但属**另一主题**（归档复核 `R08 F10` 口径），**不得**充当 Z08-10 的主题 | 发布/vendor 原 owner 未来窗口；**配置存在不称执行完成** | 否 |
| Z F5 | 「`tests/unit/t02-manual-fact-id.test.ts:67` `resolve('.venv/bin/python')` 仍为显式 PATH python（另一处）」 | **两处裸 PATH python**：`round-09/disposition.md:264` 逐字为「仍开：本人 grep 两处在位（:656/:168）」。本人本轮实测确认：`tests/unit/t01-mainline-contract.test.ts:656` 与 `tests/unit/t01-ontology-metadata-contract.test.ts:168` 两行均为 `execFileSync('python', ['-I','-B','-c', script], {`（**裸 PATH**） | **保留（仍开·维护）**；首稿引用的 `t02-manual-fact-id.test.ts:67` 是 `resolve('.venv/bin/python')` **显式路径**，**不能替换**上述两点（见 §10.2 的 R10-T09 更正） | T01 测试维护者下次授权触及两测试或环境适配前 | 否 |
| R06 D8 | 「`t02-manual-fact-id.test.ts:67` PATH python 在位」 | **同 Z F5**：`round-09/disposition.md:298` 逐字为「仍开：同 Z F5（本人 grep 两处在位）」 | **保留（仍开·维护）**，主题同上更正 | T01 原测试维护者；下次授权触及或环境适配前 | 否 |
| Z08-06 | 「保留（远端侧仍待验）／无 67 的平台 CI」 | **本地闭合资格与远端 CI OPEN 分层**：`round-09/disposition.md:227` 逐字为「承接（本地闭合资格）／仍开（远端侧）；**本地控制层资格不再由本轮重述**」，owner/窗口＝「Windows/Quality 实际 CI 仍待验」 | **分层维持**：**本地配置/控制层闭合资格维持，不静默重开**；远端 CI OPEN 保留（合并门禁由 R10-T01 承接） | Windows/Quality 实际 CI 仍待验 | 否（合并门禁另计） |
| R06 Z P2 | 「CI41 根因 UNPROVEN」 | **诊断步与验收口径分离维持（F03）**：`round-09/disposition.md:284` 逐字为「仍开：诊断步与验收口径分离维持（F03）」 | **保留（仍开）**，主题更正为「诊断步与完整验收政策/F03」；**与 CI41 根因主题分离**（CI41 根因见 R10-T02） | 未来 CI 证据接收标准 | 否 |
| R05 Z P7 | 「保留（口径）／诊断选项演变事实接收」 | **闭合只覆盖一半**：`round-09/disposition.md:323` 逐字为「关闭（口径）：诊断选项演变事实；F03 约束继续」——**只覆盖「诊断选项演变事实」**；本人**更早原稿** `round-07/minimax-m31flash.md:506` 逐字记载「**该条原含两部分**：①诊断参数（当时有效 pytest 选项已随时间变化）；②文件增长信息。本轮只作读回、未重跑；**两部分均按原处分保留**，不因本轮复核改写旧报告」；`round-08/minimax-m31flash.md:410` 记「已闭合（口径），但见 F03」；文件增长一半在 `round-05/minimax-m31flash.md:264` 记为「Z-07 文件增长｜信息级｜aff 实测 2993／1887／1748」 | **保留（口径闭合限于诊断选项一半）**；**不得因只列诊断就宣告「文件增长」那一面关闭**——该面维持**信息级**（并与本轮 §10.3 的 #138 事实更正互相印证）。本轮**已读**该更早本人原文（真实来源如上），**未造新原件** | R09 所记 owner/窗口＝无待办；增长面沿原信息级归口 | 否 |
| R06 MM05（额外 13 行内） | 「保留（裸 ownership 家族）」 | **原件该行只有状态**：本人实测 `round-09/disposition.md:347` 逐字仅「**仍开**」，**无主题文字** | **保留 ID 与状态「仍开」**；首稿所加「裸 ownership 家族」主题**无原件依据，予以撤回**；本轮**不删**该 extra 行、**不改**其状态，依据不足即限定并给出真实来源（R09:347） | 沿 R09 该行（R09 未另列窗口） | 否 |

### 10.7.1 证据串档更正（F-R09-03／F-R09-04）

首稿 §5.4 两行的**处置结论保留**，但**来源标注串档，已更正**：

| stableID | 首稿依据（错） | **有效来源** | 处置 | 原 owner／窗口 | 是否源码阻断 |
|---|---|---|---|---|---|
| F-R09-03 | 「O067 记录 helper12 TypeError，但根因未定」 | helper12 的 `app?.isPackaged` TypeError 来自 **O059（CI41 run40294180350／attempt1）**，**不是 O067**；O067 的 Quality job 是在 apt 包下载阶段被原 15m 上限取消（`Quality cancelled`），**不能评价该次 C1** | **保留原处置**（readiness-continues-helper 断言与 `app?.isPackaged` 建议已撤回；rootcause HOLD 仍在），**来源标注更正为 O059 CI41**；两者**不得拼成共同因果** | 未来 CI 证据接收标准 | 否 |
| F-R09-04 | 「O067 case16 原文」（用于 145.101449 nonpoll elapsed） | **145.101449s 非轮询区间来自 O059 CI41**，**不是 O067**；**O067 的 Windows case16 是另一个 180s 失败样本**（`durationMs=180010`、`status=timedOut`、末次 Read 断言仅约 397ms 余量） | **保留原处置**（Windows 观测不构成新合并门禁），**来源标注更正**：145.101449s → O059 CI41；O067 case16 独立列为另一观测样本，**两者不得拼为共同因果** | 未来 CI 证据接收标准 | 否 |

## 10.8 本轮追加的实际阅读范围与**仍未覆盖**的边界

**本轮新增直读（本人，只读）**：`git ls-remote origin`／`git remote -v`／`git status --porcelain` 的只读输出；`packages/engine/src/ontolearn_engine/storage.py:190-225`（迁移分支）、`:1180-1239`（`_check_slot` 全文）、`:1839-1847`（`backup`）；`project/format3.py:150-200`（`logical_hash`／`migration_backup`）；`project/transactions.py:285-307`（`preview_restore`）、`project/compensation.py:118-146`（restore selector）；`project/query_presentation.py` 的 pageSize 限额与 `RESOURCE_LIMIT` 段；`apps/desktop/src/renderer/src/query/QueryResultPanel.tsx:16-17/252/319`（CSV 导出）；`packages/contracts/src/v2.ts:863/980`（csv 契约）；`coordinator.py:460-530/640-700`（`changeset.commit` 作业路径）；`packages/engine/src/ontolearn_engine/invalidation-v2.json`（全文，9 条规则）；`packages/engine/tests/test_job_store.py` 中 `staleReason` 断言位置（grep 定位）；`tests/unit/t02-manual-fact-id.test.ts:50-90`；`tests/e2e/ui-observation.ts:154-195`；`apps/desktop/src/renderer/src/ontology/mainline-facts.ts:1-90`；`tests/unit/t01-mainline-contract.test.ts:656`、`tests/unit/t01-ontology-metadata-contract.test.ts:168`；`.github/dependabot.yml`（全文）；`round-08/disposition.md:26/31/96/115/130`、`round-09/disposition.md:220-240/264/284/298/323/347`、`round-07/minimax-m31flash.md:506`、`round-08/minimax-m31flash.md:410`、`round-05/minimax-m31flash.md:264`、`round-04/zcode-glm53.md:418`；`outputs/20261027_t02_67b7_fresh_r10_070/OWNER-PRIMARY-MINIMAX-FACTS-01.json`（本方 owner 更正事实文件，含 `storage.py:1205-1230`／`1839-1847` 摘录）；`outputs/.../remote-after-natural-01.stdout`（owner 原件）。另做只读计算：`wc -l` 行数实测、renderer 全量 grep（`aria-`/`role=`/`tabIndex`/`onKeyDown`/`keydown`/`dangerouslySetInnerHTML`/`dir=`/`unicode-bidi`）、base64/UTF-8 字节数的纯计算（不 import helper、不跑产品/测试）。

**本轮仍然未覆盖（不声称的部分）**：

1. **未重跑任何验证**：未运行 check/vitest/pytest/build/package/install/formatter/HMR/产品/GUI/SQL/bridge/故意业务失败探针；本节同样**不含任何「本人跑过」的测试事实**。
2. **不声称 117 条差异路径的必要覆盖已完成**：首稿 §3.2 所列 40 余条差异级路径**仍未逐行读全文**，其中 `tests/fixtures/t02-manual-fact-id.json` 与 `packages/contracts/v2/*.json` 的**正文语义**、`packages/engine/tests/*.py` 的**全文**均未核（本轮只核了路径、存在性、grep 命中与被点名段落）；「metadata/hash 存在」≠「runtime 原件正文语义已核」。
3. **1396 tracked 源叶未逐叶全文审读**；未变更的无关上下文未读。
4. **未读** round-01/02/03 的未跟踪 WIP 正文；round-04..08 的作者原稿**未全文读**（本轮只按行号读了 9 处、本方历史稿 3 处）；`round-04/zcode-glm53.md:418` 仅作**历史事实来源**引用，**不继承其判断**。
5. **4 个子代理无有效终稿**：本人复核其状态为 3 个 `failed`（`net::ERR_CONNECTION_CLOSED`）、1 个 `succeeded` 但本人复读其输出**未见交付正文**；其过程输出**只作定位线索**，首稿 §5 的全部结论均由本人直读原件独立复核得出，**不依赖子代理结论**。
6. **未取得**另一作者本轮 R10 的任何输出/意见/verdict；`.../20261027_t02_67b7_fresh_r10_070/zcode/` 目录本轮**未读取任何文件**。
7. 本轮**未读** `OWNER-PRIMARY-MINIMAX-FACTS-01.json` 之外的任何新 owner 指令文件；**未新设** scope/owner/门禁/测试。

## 10.9 对首稿 §8「事实补正」7 条的撤回与维持

| §8 条目 | 本轮处置 |
|---|---|
| 第 1 条（O069 `qualityRetryO068.handoff` 的 1803B pin 指向 O068 的 HANDOFF.json；O069 自身 HANDOFF 实测 1530B） | **维持**。owner 确认该目录歧义**可保维护建议**，**不是错针、更不是造假**；首稿表述与实测一致 |
| 第 2 条（O067 `HANDOFF.json` 实测 1245B） | **维持** |
| 第 3 条（远端 develop 实测 `5f910b52…`） | **撤回**。`5f910b52…` 是**本地缓存 refs**，非服务器分支状态；本人只读 `git ls-remote origin` 实测服务器 `develop` 仍为 `583c05c…`、`feature/weekly-t02-fr200-fr201` 为 `b0c0e8d3…`。**「远端已前移」的推断撤回**，本候选 base 不变、不 fetch/rebase（详见 §10.1） |
| 第 4 条（O069 70 针全通过；3 个文件自我排除与「70 针」表述一致） | **维持** |
| 第 5 条（`staged.diff` 与实际 Git 差异逐字节相同） | **维持** |
| 第 6 条（R09「额外 13」与原 78 中 `R05 MM01–MM13` 疑似同组换前缀重复，仅作审计观察） | **维持**为审计观察，**不判定**、**不改写**原 78 |
| 第 7 条（4 个子代理中断） | **维持**，并按 §10.8 第 5 条补记精确状态码 |

## 10.10 结论更新

**维持 ConditionalPass（限定技术阶段）——依更正后的事实重裁，首稿 §1／§9 的该判定原样保留且继续有效。**

裁裁理由（据实）：

- 本轮更正**未发现**任何指向本候选的源码缺陷；相反，我撤回了自己两项**过强证明**（R10-T05 的「必然 >16384」算术、R10-T10 的「renderer 更早拒绝 ⇒ 缺陷」推断）并收窄两项表述（R10-T09 的「无机器校验」、R10-T06 的「命名与门禁语义不一致」）。**push 前源码技术阻断仍为 0 项**。
- §4.1 的标签更正**方向一致**：把若干「不适用」上调为「部分适用」= 把更多需求面认定为「适用但未实施/未证」。这些**全部落在既有 HOLD 与未证门禁之内**（备份夜备与恢复演练、参考设备 Q5、a11y 合规、依赖节奏与 EOL、框架升级制度、活跃库迁移保全演练、文件拆分维护窗口、组织与法律事实），**不新增门禁、不改产品、不造新测试**。
- 合并门禁不变：**67 未 push、服务器 `feature/weekly-t02-fr200-fr201` 仍为 `b0c0e8d3…`、无新 CI**（R10-T01，本轮 `git ls-remote` 实测复核）。整体合并可用仍 **2/17**，**不推进 T04**。
- 该判定**不构成**：无条件整候选 Pass、完整平台验收、完整 C1/M0、当前新包与包内 GUI、签名公证、法律/隐私/产权/供应链放行、跨 OS 与参考设备验收、容量与损坏库恢复放行、merge 授权，或**任何**既有 HOLD／UNKNOWN／OPEN 的关闭。
- R09 的 ConditionalPass **不转移**本轮；本轮为独立重判。

**必要运行建议的归属不变**：凡需运行才能确证的事项（兜底分支实际字节、T05 泛化维护边界是否可触发、CI 完整三 job、当前新包与包内 GUI、参考设备与跨 OS、备份恢复演练、活跃库迁移保全演练），一律按 §7 的归属交回原 owner，**本轮不改码、不改 CI、不改验收**。

---

*追加完（§10）。本节由本人追加于首稿 93024B 原前缀之后，首稿一字未改；首稿末尾「报告结束…」行按原样保留。本方：MiniMax；模型 M3.1-Flash；思考等级 xhigh；权限 始终授权；SID mvs_e86f1d95643c4044a136ae2f1cca13fe。候选 base `583c05c…` → head `67b7bcbd…`、tree `78a6b5d5…` 未变。本报告不含自身终态 bytes/SHA（由 owner 另存实测）。*


---

# 11. 追加二：原 R10 必要覆盖闭合（本轮实读与范围结论）

## 11.0 本节性质与边界

**仍为同一 R10 任务、同一 SID（`mvs_e86f1d95643c4044a136ae2f1cca13fe`）、同一候选（base `583c05c…` → head `67b7bcbd…`／tree `78a6b5d5…`）、同一模型与权限（M3.1-Flash／xhigh／始终授权）。** 不重开轮次、不改源码/测试/依赖/配置/需求/验收、不运行任何 check/vitest/pytest/build/package/formatter/HMR/产品/GUI/SQL/bridge 探针、不 push/merge、不新设 scope/owner/门禁、不使用积分续跑/重置/购买/升级/API/新任务。**§10 与首稿 135675B 原前缀一字未改**（本节亦为纯追加）。

**§10 的更正作为「限定阶段接收」已纳入本人当前判断；本节只做两件事**：①把 §10.8 明确列为「未读」的**原任务必要正文**真正读完并据实登记；②据本轮实读给出必要替代与范围结论。

## 11.1 本轮真实已读模式（EOF／必要闭包位置）

| # | 路径 | 本轮读法 | 位置／范围 | 本轮读到的实质内容（要点） |
|---|---|---|---|---|
| 1 | `packages/engine/tests/test_mainline_language_input_rejection.py` | **全文到 EOF（326/326）** | 全部 | R03 拒绝集（`"设备"@1`、`"设备"@zh1`、`9`×4301）× manual/edit；`term()` 对数字子 tag 的**文法**与**大小写策略**分开（`@en-001`／`@de-ch-1901` 合法且可提交，`@de-CH-1901` 在**调用层**因非 canonical 被拒）；独立 stdio 子进程真链路（同一 PID/会话、拒后同宿主续写成功、物理库字节比对、原始 ID 不变） |
| 2 | `packages/engine/tests/test_mainline_manual_input_rejection.py` | **全文到 EOF（1034/1034；本轮补 497–1034）** | 全部 | canonical 拒绝语义与 `INVALID_REQUEST`/`params` 固定码；`assert_rejected` 要求错误体内**不含**原值；原始 ID 在 edit/undo 后仍绑定原声明；非输入类失败（term/preview/sqlite-integrity/snapshot-integrity）必须保留 UNKNOWN/HOLD；`urlsplit`/IRI 预检的**未知失败不得被归类**；vendor 源错误有专门输入类型；三种 ownership reason（reservedIdentity/sameStatement/singleSlot）的分页详情与重复引用幂等；单值声明冲突 |
| 3 | `packages/engine/tests/test_mainline_postwrite_admission.py` | **全文到 EOF（860/860；本轮补 477–860）** | 全部 | 终局增长准入边界（rows/bytes/work 三轴 ±1）；终局尾包证明 2742<4096；写后草稿增长在**读准入丢失前**被拒且不污染原宿主；排队提交在终局重核全部素材；前台/后台作用域不得互借；结算失败保留精确回复为 unknown；同 Store DTO 不能绑定预算；**后继协调器不得丢弃前驱未结算状态**（8 种状态）、不得接管前驱排队/活跃作业；真实 stdio 增长拒绝后续写与启动对账 |
| 4 | `packages/engine/tests/test_mainline_postwrite_rows_budget.py` | **全文到 EOF（395/395）** | 全部 | 真实 243 行五列有序结果在**固定最终素材**内可完成（费用恒为 bytes 1114112／objects 8192／work 134217728，`HELD_BYTES/HELD_OBJECTS/READ_WORK=(134217728,1048576,536870912)`）；`rowsPage` 与 `textPage` 的**预付费用不得借用/退还**；预付素材不得消费两次 |
| 5 | `packages/engine/tests/test_mainline_postwrite_text_budget.py` | **全文到 EOF（320/320）** | 全部 | 冷历史 56309 字符文本（多字节变体）**按 UTF-8 字节序**分页，游标不重复、每页 ≤32768B、帧预算成立；`QueryRead.pay("text final prepaid")` 固定费 `{bytes_:528384, objects:256, work:1052672}` 且每页恰一次；固定费原子拒绝后同宿主可继续；游标回调撤销在最终编码前拒绝（**编码器未被调用**） |
| 6 | `packages/engine/tests/test_mainline_read_work_budget.py` | **全文到 EOF（559/559；本轮补 493–559）** | 全部 | 真实历史的读工作量核算（scan/decoded/plans/repeats）；**64MiB 工作上限在两个阶段（lower／authorized-plan）都在校验前拒绝**且不触发 `_validate`；重复解码历史在计划选择器前即受限；**损坏的 claim/plan/snapshot/checkpoint/跨项目引用仍走完整鉴权并 HOLD**，不静默降级；`json_extract` 被拒时**无零回退**且 HOLD |
| 7 | `tests/fixtures/t02-manual-fact-id.json` | **全文到 EOF（139/139）** | 全部 | 13 组 golden 向量：首个真实 UI 三元组、中文 IRI＋`@zh`、非 BMP emoji IRI、转义引号/反斜杠字面量、多行字面量、plain/language/integer/decimal/boolean/date 类型化、**unicode-nfc 与 unicode-nfd 分列且 ID 不同**；声明 `sourceStorageSha256`／`sourceRdfSnapshotSha256`／`pythonVersion`／`rdflibVersion` |
| 8 | `tests/unit/t02-manual-fact-id.test.ts` | **全文到 EOF（186/186；前轮仅 50–90，本轮补齐）** | 全部 | 单元仅验证消费端输入形态；经 `resolve('.venv/bin/python')` 调**真实** `Store._fact` 与 `digest` 复核全部 golden；TS 产出的记录再由真实 Store 复核且**不替换其 ID**；WebCrypto 摘要**先捕获三元组再 await**；未配对代理项在有损 UTF-8 哈希前被拒（且 `digest` 未被调用） |
| 9 | `tests/unit/t02-manual-preview-lifetime.test.ts` | **全文到 EOF（596/596；本轮补 556–596）** | 全部 | 用 `vm`＋`ts.transpileModule` 真实加载 `OntologyMainlinePage.tsx` 的 hook/事件测试台；冲突详情在 9 类变更（主体/谓词/对象/结构/载入/重置/读取/布局/会话）下清除或隔离；**迟到**的成功/失败详情不得复活；哈希完成后只准备一次；13 种「迟到哈希」场景一律拒绝；脱离附件的失败不显示为当前错误 |
| 10 | `tests/unit/t02-ownership-detail-view.test.ts` | **全文到 EOF（138/138）** | 全部 | 真实组件＋**React SSR** 渲染；三种 reason 与 singleDeclaration 的文案；>16KiB 历史 ID 不规范化、不截断、不生成链接（`white-space:pre-wrap;overflow-wrap:anywhere`，无 `href=`）；HTML 样式值**只作转义文本**（无 script/img/a/iframe，无 href/src/onerror）；**只读**（无 button/input/form/a，且不含「确认/提交/写入/自动执行/chunk/hash/detailRef」） |
| 11 | `tests/unit/t02-ownership-detail.test.ts` | **全文到 EOF（843/843；本轮补 421–843）** | 全部 | 真实契约重组与渲染端消费；>17KiB 原始 Unicode ID/owner/sourceRow 与 null 保真；14 类首段破坏（project/ref/startOrdinal/ordinal/offset/length/hash/base64/预算/段预算/无进展/提前 complete/缺段/重复段）与 6 类后续页破坏（hash/total/repeat/skip/denied/throw）**不读后续、不发布半成品 VM**；公开重组器自身拒绝；SHA await 后仍做 STALE_CONTEXT 栅栏；会话层绑定只发布已校验 VM、**永不创建事务**；无效 detailRef 不触发 getter；错误码/消息键/额外参数不被当作授权；7 类失效下同步清除；5 个阶段的迟到成功/错误一律不改变快照；发布前复核 active 的 5 个维度；调用方微任务间隙栅栏 |
| 12 | `packages/contracts/v2/schema.json` | **base→head 变更正文全文（+525）** | 新增全部 | 新增 `project.ownership.detail` 请求/响应信封两态；`ownershipDetailDocument`（`manual-ownership-conflict`／`single-declaration-conflict` 的 `oneOf`）；`ownershipDetailManifest`（`segmentCount` 1–512、`totalBytes` 2–16777216、`documentHash`）；`ownershipDetailHeader`（origin 三元身份、`requestHash`／`fingerprint`／`segmentBlobRefs`）；`params_project.ownership.detail`（**首页 `documentHash:null` ＋ `startOrdinal:0`**，续页 `documentHash` 为 hash ＋ `startOrdinal` 1–511，`pageSize` 1–64）；`result_project.ownership.detail`（`segments` 1–64、`nextOrdinal`、`complete`）；既有字符串字段上限 16777216 |
| 13 | `packages/contracts/v2/fixtures.json` | **base→head 变更正文（+350/−96；非 registryHash 新增 287 行）** | 新增全部 | 7 个新 case：`named ownership request`(valid)、`ownership no null continuation`(**null 哈希 + startOrdinal 1 → invalid**)、`ownership wire issuer forbidden`(**注入 `ownerId` → invalid**)、`named ownership page`(valid)、`ownership wrong ref`(invalid)、`ownership corrupted segment SHA`(invalid)、`ownership premature next`(invalid)；其余为 registryHash 与 wireBase64 同步更新 |
| 14 | `packages/contracts/v2/registry.json` | **变更正文全文（+4/−2）** | 全部 | `project.ownership.detail` 加入两处方法集合 |
| 15 | `packages/contracts/v2/binding-regressions.json` | **变更正文全文（17/17，全为 registryHash）** | 全部 | 16 处 `registryHash` 由 `058ed1be…` 更新为 `5e097b7e…`，与 registry 变更一致 |
| 16 | `packages/contracts/python/contract_v2.py` | **变更正文全文（+49）** | 全部 | 新增 `ownership_detail_matches()`：`segmentCount=(totalBytes+32767)//32768`、段 ordinal/offset/length 一致、base64 严格解码、逐段 SHA-256、`nextOrdinal`/`complete` 与 `end==count` 一致、续页必须回带 `documentHash`；并在 `matches_business3_response` 中为该方法单独分支（**不进入 `draft.save` 分支**） |
| 17 | `packages/engine/tests/test_mainline_dispatch.py` | **新增段 59–581 全文** | 59–581 | `ownership_fixture`（大 locator/受管两种）；分页读详情并逐段校验 SHA；**错哈希 → IDENTITY_CONFLICT**、最后一页合法但只到段尾、**他项目 → NOT_FOUND**、读详情**不新增游标行**；详情损坏 → STORAGE_FAILURE＋HOLD；段写失败整体回滚且**不产生 detailRef**；诊断不得污染已准入的核心读取器；私域准入与核心全量读取向量分离；**坏 blob 在 intern 复用前被有界拦截**；原始段预算在 JSON 解码前拒绝；重复引用复用同一 ref 且在行上限处新上下文回滚；旧三字段详情**不得臆造定位器**（→ INVALID_STATE）；引用**不得跨后继会话**（→ NOT_FOUND），只有新会话的新预览才能铸新 ref |
| 18 | `packages/engine/src/ontolearn_engine/rdf_snapshot.py` | **全文（76/76）** | 全部 | `TermInputError(ValueError)` 为**确定性**输入拒绝；`iri()` 捕获 `urlsplit` 的 `ValueError` 并转 `TermInputError`；`term()` 把 `BadSyntax`/`Notation3InputError` 转 `TermInputError`，**其余异常仍为普通 ValueError（保持 UNKNOWN）**；恰好一个 RDF term、仅 URIRef/Literal、XSD.string 归一、**语言 tag 小写化** |
| 19 | `packages/engine/src/ontolearn_engine/project/project_host.py` | **1–200 全文 ＋ base→head 差异正文（+110/−59）** | 1–200 及全部差异 | `ReadLimits`（validation_rows 16384／validation_bytes 33554432／validation_work 536870912 等）；新增 `MaterialProfile.admit_terminal_growth` 与 `material_profile()`；`_preflight` 改为调用它。**语义变化（更严）**：核心读取器的工作量公式由 `scan*(1+repeats)` 变为 `2*scan + total_bytes*repeats`，并新增 `work + plan_bytes*repeats > validation_work` 判据；**默认读取器保持原全表口径** |
| 20 | `packages/engine/src/ontolearn_engine/project/query_presentation.py` | **base→head 差异正文（+19/−2）** | 全部差异 | 文本页在编码前**一次性预付**固定终局费用并用局部 `_RowsPrepaid` 消费，编码前再做一次绑定复核（`ticket.pay("text final binding recheck")`），不重复收费、不借用他人额度 |
| 21 | `packages/engine/src/ontolearn_engine/coordinator.py` | **base→head 差异正文（+22/−1）** | 全部差异 | `project.ownership.detail` 加入只读方法集；`changeset.preview` 传入 `ownership_proof`；启动时在**非测试模式且无普通授权/查询派发**下调用 `prepare_mainline_store(store)`，使**启动对账前**就受同一 Store/租约限制约束 |
| 22 | `packages/engine/src/ontolearn_engine/project/domain_changesets.py` | **base→head 差异正文（+34/−2）** | 全部差异 | `preview_changeset` 增 `ownership_proof` 参数并校验 `request_hash`/`base`；**只有直接调用者的项**走已知语法/策略拒绝：`manual` 的 subject/predicate 过 `iri()`、所有对象值（含 edits）过 `term()` 且要求 `parsed.n3() == value`，否则 `INVALID_REQUEST(field=params)`；未知解析/N3/Store 失败仍为 UNKNOWN/HOLD；**edits 不派生也不替换其 ID** |
| 23 | `packages/engine/src/ontolearn_engine/project/mainline.py` | 复用首稿**完整差异**读法（+417） | 全部差异 | `_WriteAdmission`／`_OwnershipProof`／`ownership_proof`／`prepare_mainline_store`／`project.ownership.detail` 分派／`close()` 的 `_clean_close`（首稿已全文读，本轮不重复） |
| 24 | `packages/engine/tests/test_job_store.py` | **九类失效的断言体定位 ＋ 逐代码 grep 分布** | `:253/263-264/272/728/1056/1069/1120/1136/1239-1240` | 见 §11.4 的 R10-T12 |
| 25 | O069 `COMPLETION.json`（6941B） | **正文全文** | 全部 | 候选身份（head/tree/parent/base/4 路径/631+/43−/1396/40 提交/117 路径）、patch pin、五条变更说明、focusUnit 7PASS、fullCheck（exit 0／189.306389s／TS 1912PASS/40 files／Python 3769=3719PASS+50SKIP）、native24（21PASS+3 原 I04 SKIP／retry0／flaky0／57 事务向量 7,7,7,7,22,7／43 拒绝=42 INVALID+1 OWNERSHIP）、driver 169.386s／89 项 qualification、三次保留失败、构建绑定、保护项、远端状态（feature 仍 b0、develop 仍 583、PR16 open、未 push）、O068 交接引用、下一门禁与保留限制 |
| 26 | O069 `INDEPENDENT-CANDIDATE-BINDING.json`（8941B） | **正文全文** | 全部 | 判定 `PASS_LOCAL_CANDIDATE_BINDING_ONLY`、`blocking: []`；**四条源针**（字节＋SHA-256＋「与固定 Git／评审／full-check03／native 输入一致」）；1392 源叶保全与 1394→1396 计数；owner full-check03 回读（含「**在 b0 checkout＋四路径 WIP 上运行、未谎称在 committed HEAD 上运行**」）；owner native24 回读（report 5274213B／原始三例 I04 SKIP 全文／89 项声明与复算边界）；构建绑定（main 606471B／仅 [602382,602406] 24B 变化）；保护守卫回读与限制清单 |
| 27 | O069 `INDEPENDENT-PRE-REGRESSION-REVIEW.json`（12316B） | **正文全文** | 全部 | 判定 `PASS_STATIC_PRE_REGRESSION`（明示**不等于**回归成功/双审/CI/merge）；三条初始发现 IR069-01/02/03 的复现与关闭方式；逐项语义复核（role/name 范围、严格性、enabled 判据、文本、可见性、first-ACK-loss、FR201、有界证据、只读 DOM 单元）；**AST 静态保全**（9/2 与 9/12 业务调用点、参数与源码顺序完全一致，明示**未测量运行时调用次数**）；Playwright 1.64.1 本地判据定位；requiredNextValidation 5 条；notPerformed 10 项；限制 3 条；首败 TS7022 与**仅加类型标注**的字节级证明（移除该标注可复现原 7490B／`062f5cb6…`） |
| 28 | O069 `NATIVE24-QUALIFICATION.json`（61604B） | **结构 ＋ 全部 89 项 check 名与值 ＋ limits/annotations/transactionGroups/attachmentPins/case7Evidence/FR201Final/driver/request/runtimeIdentity/stats** | 全部 | `PASS_LOCAL_NATIVE24_BOUNDED`、`unresolvedChecks: []`、**89/89 均为 true**；23 项非 case 级 check（原始 24 案例序与标题完全一致、21PASS+3 原 SKIP、单结果 retry0、无 flaky/意外、SKIP 仅原三例 I04、六 T02 通过、57 事务向量、57 唯一 op/Job、完整 Diff/Read/Job/marker 绑定、43 拒绝=42+1、拒绝后完整 Read 不变、FR201 单项目 22 事务与终态 9 facts、2 次真实原 ID 编辑、终态定义保全、case7 单提交/原 operation/全链、唯属画像、驱动自然 0、已知进程缺席不等于清理、**b0+WIP 运行身份**、四路径输入针与 fullcheck 成功、跟踪 spec 针与实际启动源一致）；**annotations 14 条实测 542–1211B**（远低于 16KiB，stage 为 `actual fresh readProject completed`）；`attachmentPins` 101 项；`engineNaturalExit: UNKNOWN`；limits 5 条（含「不主张物理零写」「不继承模型结论」） |
| 29 | O069 `staged.diff`（36240B） | 复用首稿**已实测的逐字节相同结论**（本轮未重复） | — | 首稿已执行 `git diff b0c0e8d3 67b7bcbd` 并与 `staged.diff` 逐字节比对一致；本轮仅复核四路径 Git blob 针（见 §11.4） |

**本轮新增的只读独立复算（不是测试事实）**：①O069 四条源针对 head 真实 Git blob 的字节与 SHA-256 **四条全部 MATCH**（本人 `git cat-file` 实测）；②构建产物 `apps/desktop/out/main/index.js` 与 O064 旧产物**逐字节比对：全长均 606471B，差异恰为连续 24 字节（0-based 602382–602405），前缀与后缀完全相同**，内容为开发期 CSP nonce 串——即原件所称「仅 24B 变化」的边界**由本人独立复算确认**；③fixture 声明的两个源码哈希锚点**实测等于 base 源而非候选源**（见 §11.4 R10-T11）；④九类失效代码在引擎测试中的断言分布（见 §11.4 R10-T12）。


## 11.2 既有意见处置（稳定 ID 维持，不新增也不改写既有集合）

- **本人 Top10 稳定 ID 维持**：R10-T01…R10-T10 编号与首稿原句全部保留；本轮**不新增条目以凑数**，§10.2 已给出的处置（保留 6／撤回 2／收窄 2）**本轮无进一步变化**，仅补充三处可核证据：①R10-T05 的兜底边界——O069 qualification 的 **14 条实测槽位为 542–1211B**，其 `stage` 正是 `actual fresh readProject completed`（34B），与本人复算的 14914B 反例同一形态，进一步支持「当前不构成缺陷」；②R10-T09 的机器交叉核验——本轮读完 `tests/unit/t02-manual-fact-id.test.ts` 全文，确认其 7 个用例中有**两处**以真实 Python 复核 golden（一次校验既有 golden、一次校验 TS 产出），且 golden 含 **unicode-nfc / unicode-nfd 分列**；③R10-T10 的引擎侧真实语义——`test_mainline_manual_input_rejection.py:808-909` 以 `reservedIdentity`／`sameStatement`／`singleSlot` 三种 reason **逐一**跑到分页详情，确认 ID 保留身份与 live object/single 是两条独立判据。
- **§5.1／§5.2／§5.3 的 31／78／13 集合、行序、ID 一律不变**；§10.7 的八处历史主题更正继续有效，本轮**只补一条依据**：`R06 MM05` 在 `round-09/disposition.md:347` 确为**仅有状态「仍开」**（本轮复读该行确认），其「裸 ownership 家族」主题无原件依据的撤回维持。
- **§4.1 的 160 行、§4.2 的 16/46/90/8** 不变；§4.1 表体与 §4.2 表体原样保留，替代关系只在本节与 §10 给出。
- 既有 HOLD／UNKNOWN／OPEN 全部保留，**逐一关闭数为 0**；整体合并可用仍 **2/17**，不推进 T04。

## 11.3 本轮校正的三处残句（保留旧原句，以本节为唯一有效替代）

**(a) 复合组末 13 项的分布**：旧句（§10.4／§10.5）写为「无法确认 4／不适用 6／部分适用 3」，**与 §10.3 自身对 #153、#156 的标签上调不一致**。**唯一有效分布为 4／4／5（无法确认 4／不适用 4／部分适用 5）**：

| 档位 | 数量 | 明细 |
|---|---|---|
| 无法确认 | **4** | #148 逐行人审、#149 第二个客户前设计数据模型、#150 解释修复引入的新缺陷、#151 部署/回滚/云账单 |
| 不适用 | **4** | #152 支付值班、#154 审计员演示、#157 技术负责人否决、#159 调试 AI 写不出的代码 |
| 部分适用 | **5** | **#153** 漏洞当周打补丁（更正）、#155 QA、**#156** 活跃库迁移保全（更正）、#158 全客户等价、#160 一年后仍记得为什么这样建 |

即：**#153、#156 由「不适用」上调为「部分适用」后，末 13 项为 4／4／5**。**全 160 的 16／46／90／8 不变**（本轮再次程序化复算：17 处标签变化集合不变，合计 160）。

**(b) R10-T05 的固定开销与 stage 预算**：旧句（§10.2）写为「固定开销 212B……stage 长度增至约 1538 字符以上（实测余量 1504B）」，**「1538 字符」的表述不精确**。**唯一有效口径**：base64 **14668B** ＋ 固定字段开销 **212B** ＝ 14914B（≤16384），因此 **stage 的 UTF-8 总预算为 1504B**；当前受审 `stage` 为 34B（`actual fresh readProject completed`），**余量 1470B**。越界需 stage 自身超过 1504B。**该边界属「尚未证明当前可触发」的维护观察，不作当前缺陷**，原前缀改法建议维持撤回。

**(c) 历史 stableID `R06 Z P2` 的主题**：唯一有效主题仍是 **「诊断步与完整验收口径分离（F03）」**，**不是** CI41 的具体根因；§10.7 的更正**继续有效**，本节重申以免与 §2 的 R10-T02 混读（R10-T02 才是 CI41 根因未证项）。本轮**未发现**任何新证据需要改写该主题。

## 11.4 本轮新发现（2 项；均为 P3 可追溯性/覆盖口径观察，**非源码阻断**，不进入 Top10）

### R10-T11｜`tests/fixtures/t02-manual-fact-id.json` 的**来源锚点指向 base 源**，不指向候选源
- **stableID**：R10-T11（本轮新增，独立编号；**不进入 Top10**，不替代任何既有 ID）
- **严重性**：P3（可追溯性标签）
- **触发**：按 fixture 声明的哈希去取「产生向量的那份源码」时，取到的是 **base** 而非候选。
- **代码/原件定位与本人实测**：`tests/fixtures/t02-manual-fact-id.json:3-4` 声明 `sourceStorageSha256 = 92be4def1dba41e7ff93ec596934b717eee42011240b9f92c4e6d5cb2ce2914e`、`sourceRdfSnapshotSha256 = 7cca115fa77e0926a632ba58d404ed39071f7dcfb8d52af2d212e89d36b2309a`；本人 `shasum -a 256` 实测：**这两个值恰是 base `583c05c…` 的 `storage.py` 与 `rdf_snapshot.py` 的 SHA-256**，而候选 head 的对应文件为 `858e168f7c3a…`（storage.py）与 `b2acac581c3b…`（rdf_snapshot.py）。`git log --diff-filter=A` 实测该 fixture 由 `c5122e1b`（`fix: derive new manual fact IDs and fence async previews`）引入，此后 `storage.py`／`rdf_snapshot.py` 又经 `30febe0e`、`75ecaf22`、`6b2a5f28` 三次变更；**`canonical`／`digest` 定义本身未变**（差异中无其定义行）。
- **影响**：**向量本身仍然有效**——`tests/unit/t02-manual-fact-id.test.ts`（本轮读完全文）在运行时用**候选的真实 Python** 复核全部 golden（`resolve('.venv/bin/python')` ＋ 真实 `Store._fact` ＋ `digest` 断言），故源码漂移会被测试捕获而非静默通过；但**两个哈希标签已不再指向产生向量的那两份源码**，追溯时会取到 base 文件。同类漂移：`rdflibVersion: "7.6.0"` 与候选实际 vendored `7.6.0+ontolearn.fr201.3` 不同。
- **最小建议**：由 fixture 维护者把两个哈希刷新为候选源并说明向量是否需重生成，或把字段改述为「向量生成时的上游版本」；**本轮不改码、不改 fixture**。
- **是否 push 前源码阻断**：**否**（不影响任何断言结果与产品行为）。

### R10-T12｜九类失效规则中**有断言体的只有 3 个家族**（`invalidation-v2.json` 定义 9 条）
- **stableID**：R10-T12（本轮新增，独立编号；**不进入 Top10**）
- **严重性**：P3（覆盖口径）
- **触发**：按「九例失效机制已验」的口径追责或补测时，会高估引擎断言覆盖。
- **代码/原件定位与本人实测**：`packages/engine/src/ontolearn_engine/invalidation-v2.json` 确定义 **9 条规则**（appendixRow 1–9；家族 ontology/facts/mapping/constraint/rule/behavior/scenario/query/model；第 9 条 model 的 `staleReason` 为 `null`）。本人逐代码 grep 引擎源码与测试目录，实测**有 `staleReason` 断言体的仅 3 个家族**：`FACTS_CHANGED`、`MAPPING_INPUT_CHANGED`、`RULE_CHANGED`（断言体见 `packages/engine/tests/test_job_store.py:253`、`:263-264`、`:272`、`:728`、`:1056`、`:1069`、`:1120`、`:1136`、`:1239-1240`；另见 `test_storage.py`、`test_project_transactions.py`）；而 `ONTOLOGY_CHANGED`、`VALIDATION_DEFINITION_CHANGED`、`BEHAVIOR_CHANGED`、`SCENARIO_CHANGED`、`QUERY_CHANGED` **五个代码只出现在 `invalidation-v2.json` 的定义中，测试目录 0 命中**。
- **影响**：属**断言覆盖口径**问题，非功能缺陷：九类定义与失效通道在位，但「每类都有正向/反向断言」这一更强说法**不成立**。
- **最小建议**：把这五类的断言补进既有测试文件，或在 `invalidation-v2.json` 内标注「暂无引擎断言」；**本轮不改码、不造新测试**。
- **是否 push 前源码阻断**：**否**。
- **同时更正 §10.3 的 #73 表述**：准确说法是「九例**定义**在、失效通道在、**逐类断言仅 3/9**」；**四类具名下游 GUI 缺口（编辑后推导／保存查询／SHACL／报告，见 `R06 D10`、`MM R07-08` 的原 OPEN）仍独立保留**，二者不得混为一谈，也不得用前者抹去后者。

## 11.5 范围结论

**维持 ConditionalPass（限定技术阶段）。** 本轮补齐原任务必要正文后：

- **未发现任何指向本候选的源码缺陷**。本轮新增两项发现（R10-T11／R10-T12）**均为 P3 可追溯性与覆盖口径观察**，不改业务结果、不改契约、不构成阻断。
- 67 的实际变更仍只有 4 个测试/测试辅助路径（631+/43−），**未改生产代码、契约、依赖、CI 或验收**；本轮读完的契约新增（`project.ownership.detail` 信封、`params` 首页/续页约束、`result` 分段约束）、Python 契约闭包（`ownership_detail_matches`）、引擎闭包（`TermInputError` 的确定性/未知分离、编辑不派生 ID、`ownership_proof` 绑定、终局增长准入、文本页固定费预付、启动期 Store 租约限制）与前端消费端（`reassembleOwnershipDetail` 限额、冲突详情只读渲染、页面生命周期栅栏）**逐项相互闭合**。
- **合并门禁不变**：67 未 push；服务器 `feature/weekly-t02-fr200-fr201` 仍为 `b0c0e8d3…`（本轮只读 `git ls-remote` 复核）；无新 CI。整体合并可用仍 **2/17**，**不推进 T04**。
- 该判定**仍不构成**：无条件整候选 Pass、完整平台验收、完整 C1/M0、当前新包与包内 GUI、签名公证、法律/隐私/产权/供应链放行、跨 OS 与参考设备验收、容量与损坏库恢复放行、merge 授权，或**任何**既有 HOLD／UNKNOWN／OPEN 的关闭。
- R09 的 ConditionalPass **不转移**；本轮为同一 R10 任务内的独立续判，**未重开轮次**。

## 11.6 本轮**真正仍未覆盖**的部分（不声称完成）

1. **未重跑任何验证**：未运行 check/vitest/pytest/build/package/install/formatter/HMR/产品/GUI/SQL/bridge/故意失败探针；本节**不含任何「本人跑过」的测试事实**。所有测试与 CI 数字仍来自标明身份的既有原件（O064/O067/O068/O069），本轮只是**读了其正文语义**并**独立复算了其中可只读复算的子集**。
2. **六个 engine 测试与 89 项 qualification 的运行时结果未由本人复现**：本人读的是**测试正文与断言语义**，不是执行结果；`NATIVE24-QUALIFICATION.json` 的 89 项 check 本人读其**名称与值及边界声明**（并确认 `unresolvedChecks` 为空），**未重算其 57 事务／43 负例算法本体**（原件亦自述该边界）。
3. `packages/engine/tests/` 中**未列入本轮清单的其余文件全文未读**（本轮读 6 个指定文件全文 ＋ `test_mainline_dispatch.py` 新增段 ＋ `test_job_store.py` 的九类失效断言体定位）。
4. `packages/contracts/v2/fixtures.json` 与 `schema.json` 的**未改部分**（数万行既有 fixture/定义）未读；`contract_v2.py` 只读变更闭包，未做全文复读。
5. `packages/engine/src/ontolearn_engine/storage.py`（1887 行）与 `job_store.py`（2993 行）**未读全文**；本轮只按被点名函数与差异读（`storage.py` 的 `_check_slot`／`backup`／canonical；`job_store.py` 首稿已读 `_application`／`_ownership_header`／`_ownership_segment`／`ownership_detail_page`／`_project`）。
6. `packages/engine/src/ontolearn_engine/project/mainline.py`（1206 行）本轮**复用首稿的完整差异读法**，未做全文复读（首稿 §3.1 已登记为 base→67 完整差异）。
7. O069 的 `native24/report.json`（5274213B）与 **101 个 `attachmentPins` 附件未逐个打开**；本人只读 pin 清单、其绑定声明与 `annotationLimit`／`limits` 语义。
8. `packages/engine/vendor/rdflib/*.whl` 二进制内部未读（首稿已声明，仅核 PROVENANCE／NOTICE／lock 声明层）。
9. **另一作者本轮 R10 的任何输出/意见/verdict 未读**；`.../20261027_t02_67b7_fresh_r10_070/zcode/` 目录本轮**未读取任何文件**；未互传结论。
10. **未跑任何新 CI、未 push、未 merge**；远端状态只以只读 `git ls-remote` 复核。

**只读合规实测（本轮结束时）**：worktree `git status --porcelain` 仍为 **4 行**既有保护项（` M AGENTS.md` ＋ 3 个未跟踪目录），index 为空，`HEAD=67b7bcbd…`／`tree=78a6b5d5…` 未变；本轮在仓库内**未写入任何文件**（仅运行时的 `.mimosa/hook-state` 会话文件，属运行时自有、且 AGENTS 明令禁止提交）。全部写入仅发生在本仓外指定报告路径，且为**纯追加**。

---

*追加二完（§11）。本节由本人追加于 §10 之后；首稿 135675B 与 §10 前缀一字未改。本方：MiniMax；模型 M3.1-Flash；思考等级 xhigh；权限 始终授权；SID mvs_e86f1d95643c4044a136ae2f1cca13fe。候选 base `583c05c…` → head `67b7bcbd…`／tree `78a6b5d5…` 未变。报告不含自身终态 bytes/SHA（由 owner 另存实测）。*
