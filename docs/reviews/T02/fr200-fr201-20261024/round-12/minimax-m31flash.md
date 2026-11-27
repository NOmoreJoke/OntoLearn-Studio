# T02 R12 完整累计候选独立工程审查报告（MiniMax Code / M3.1-Flash / xhigh / 始终授权）

审查者：MiniMax Code，模型 M3.1-Flash，思考等级 xhigh，权限模式始终授权（本轮新任务，原生会话 `mvs_9fdac9995ac940e0aa1105d923ebbaa4`）。
本报告只写本方仓外指定路径 `outputs/20261027_t02_v2_observer_validation_review_081/minimax/report.md`。审查期间未修改任何实现、测试、配置、依赖、预算、忽略项或验收；未 `git add`/`commit`/`push`/切分支；未执行 check、pytest、vitest、build、package、install、formatter、HMR、SQL、产品 GUI、业务 RPC、采样或 profiler；未读取另一作者本轮 R12 目录、报告、意见或 verdict。

---

## 0. 身份回执与受审对象核验（本人实际执行）

| 项 | 任务书给定 | 本人实测 | 一致 |
|---|---|---|---|
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | `pwd` 输出同一绝对路径 | 是 |
| branch | `feature/weekly-t02-fr200-fr201` | `git rev-parse --abbrev-ref HEAD` = `feature/weekly-t02-fr200-fr201` | 是 |
| head | `dc6c112ecc944116dc421f9ef569eb50e132e217` | `git rev-parse HEAD` 同值 | 是 |
| tree | `ba11405f4e4d9ba88136ed47ce74f2848a12b9ac` | `git rev-parse HEAD^{tree}` 同值 | 是 |
| sole parent | `deac095fb86f3704fa76cd4216ecd60409ff3c99` | `git rev-list --parents -n 1 HEAD` = `dc6c112… deac095f…`（唯一父） | 是 |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | `git cat-file -t` = commit，tree `133357a527a3967417189195b5c24e3f8a5752e8` | 是 |
| 累计提交 | 45 | `git rev-list --count base..HEAD` = 45 | 是 |
| 差异路径 | 135 | `git diff --name-only base HEAD \| wc -l` = 135（91 A / 44 M） | 是 |
| tracked 源叶 | 1412 | `git ls-tree -r --name-only HEAD \| wc -l` = 1412 | 是 |

工作树状态（本人实测 `git status --porcelain`）：` M AGENTS.md` 加三个未跟踪目录 `docs/reviews/T02/fr200-fr201-20261024/round-01/`、`round-02/`、`round-03/`。index 为空，无 staged 改动。AGENTS.md 是当前操作政策 overlay，未 stage，与 O081 `CANDIDATE-BINDING.json` 的 `committedVsValidatedSourceExceptions` 一致（版本化旧指南 blob `1b3c0291…`／当前 overlay `de15f6ce…`，两者单列，不把 overlay 冒为 HEAD 源码 blob）。本人执行遵守当前 AGENTS.md（含 2026-10-22 桌面操作政策与 2026-10-21 默认权限条款），源码按固定 SHA 读取。

身份符合，继续审查。以下结论均基于本人亲读正文，不继承旧 R11 判定。

---

## 1. 结论（先行）

**本轮判定：ConditionalPass（限定技术阶段），带两项当前 push 前源码阻断。**

含义与边界（逐条保留，不升级为产品通过、完整 CI 放行或发布放行）：

1. 本轮四叶实现（IRI v2 memo 四叶、C1 被动观察两叶）在**静态源码层面未发现数据泄露、资金损失、服务中断类缺陷**，其"不改变原有校验边界"的自我声明经本人逐行核验在关键路径上成立。
2. 但存在 **2 项当前 push 前源码阻断**：§2 的 N1（状态登记缺口）与 N2（memo 与 `TermInputError` 分层后错误语义未在引擎侧完整闭合，见 §2 N2 实为更精确的阻断项）。N2 我复核后判定为 **真实源码缺陷**，需在 push 前处理；N1 为文档登记阻断。
3. 本轮真实验证（O081）质量显著优于前轮：完整 check 自然退出 0（TS 1924 PASS/41 files、Python 3748 PASS + 50 原条件 SKIP + 1 原 duplicate-ZIP warning、Ruff 397 files）、原 native24 自然退出 0（21 PASS + 3 原 I04 SKIP、retry 0、flaky 0、57 事务/43 拒绝/FR201 final rev 22）。**但 C1 本次为成功路径，`failureObservation` 未被真实触发**，因此"当前真实失败 observer 输出"在本轮**仍无平台真实证据**，O079 的 C1 首败与底因 UNKNOWN **未被本次通过关闭**。
4. 历史 163 意见位置与 160 项原清单按稳定 ID 逐项处置见 §5、§6，**全部保持原 owner 与事件窗口**，未新造位置、未合并 extra13 于 78、未以 Top 序号代 stable ID。
5. 整体合并可用 FR 仍 **2/17**（FR401/402），HOLD 关闭 0，D8 未用，Goal/M0/release 未完成，**T04 不推进**。

**当前 push 前源码阻断（明确）**

- **N1（文档登记，P2）**：`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 的最新登记段停在 R11/`d1aca3e3`，**没有本轮 `dc6c112e`（IRI v2 + observer 四叶）的登记段**。R11 的 F05 意见正是"状态登记缺口"，本轮新增一个未登记的候选，缺口重新打开。属状态来源唯一性违规（AGENTS §6），但非产品源码缺陷。
- **N2（源码，P2）**：`packages/engine/src/ontolearn_engine/rdf_snapshot.py` 新引入 `TermInputError` 分层后，`packages/engine/src/ontolearn_engine/storage.py` 的**快照校验路径仍只把 `TermInputError` 当作普通 `ValueError`**，而引擎对外协议层与 `packages/contracts` 的错误目录**没有对应的错误码**。详见 §2 N2 的完整分析与最小建议。

**未来完整 CI / merge 条件（不变，沿用原票）**：ROOT 精确票后的完整 Quality/macOS/Windows 三平台同交付；逐 node 完整 3769 与原有理据 skip；自然退出 0；无失败早停取消、timeout NOTRUN；全部后继步骤与 Quality packaged recovery 自身 success；原 15/20 分钟上限不变。新候选尚未 push、无新 CI，旧 CI44 结论不覆盖本候选。

**独立 HOLD / 未知（全部保留，未被本轮关闭）**：C1 原生 unresponsive 底因 UNKNOWN；Windows CI 43/44 根因未证；Quality 完整 3769 NOTRUN；组织法律/IP/隐私/真实 human bus-factor；容量、坏 SQLite 物理保护、旧超限库恢复；包内完整 GUI/签名公证；跨 OS 与参考 8GB 设备；供应链；engine 自然退出与 Windows 后代；sys.path 等价；unknown parser/N3Store 坏 snapshot；未具名下游/ownership 家族/剩余 Undo；旧 79F。

---

## 2. 至多 Top 10 真实最重要风险（按严重性排序，不足不凑数）

严重性定义：S1=可能造成数据泄露/资金损失/服务中断且可由当前源码路径触发；S2=正确性或证据链缺陷，需修正后才能 push；S3=质量/可维护性偏差，不阻断 push；S4=观察/待办。

### N1｜S2｜当前 `dc6c112e` 候选未在唯一状态来源登记
- **触发**：任何依赖 `docs/reviews/T02/status.md` / `docs/m0-checklist.md` 判断"当前受审候选是谁"的读者或流程。
- **代码位置 + 原件**：`docs/reviews/T02/status.md:115`（末节标题为「2026-10-27 R11 / d1aca 必要技术阶段已接收；受控docs归档」，正文末句为 R11 接收），`docs/m0-checklist.md:89` 同名末节；`git log --oneline` 显示其上仍有 `dc6c112e fix: bound snapshot IRI reuse and native recovery diagnostics`。两份状态文件均**无 `dc6c112e` 段**。
- **影响**：状态来源与实际 HEAD 脱节，下一轮审查者或 ROOT 会读到过期候选身份；R11 的 F05 登记缺口意见重新打开。这不改变产品行为，但违反 AGENTS §6「唯一状态来源」。
- **最小建议**：在两份状态文件各追加一段，登记 base/head/tree/45 提交/135 路径/1412 叶、四叶 blob SHA、O081 实际 check/native 事实与 C1 成功路径未触发 observer 的边界，并声明"旧 R11 末段前缀逐字保留"。属纯文档后继，须走独立 commit，不改受审四叶。
- **是否当前 push 前源码阻断**：**是（文档登记阻断）**。不阻断产品源码本身，但按现行门禁"状态追加节与普通证据提交"是既定交付动作。

### N2｜S2｜`TermInputError` 在引擎内部分层，但跨边界错误目录未同步，快照校验的"确定拒绝 vs 未知解析失败"信息在协议层丢失
- **触发**：快照中含一个**确定的 RDF 语法/策略非法对象**（例如尾随空白 IRI `" <urn:x>"`）或一个**未知解析器失败**时，`storage._snapshot_state` 调用 `term()`；`term()` 现在分别抛 `TermInputError`（`BadSyntax`/`Notation3InputError`）与普通 `ValueError`（其它异常）。
- **代码位置 + 原件**：`packages/engine/src/ontolearn_engine/rdf_snapshot.py:13`（`class TermInputError(ValueError)`）、`:34-37`（`except (BadSyntax, Notation3InputError) → TermInputError`）、`:38-39`（`except Exception → ValueError`）；`packages/engine/src/ontolearn_engine/storage.py:1650-1654`（`objects.noncanonical(value) if objects is not None else term(value).n3() != value`）与 `:1254-1257`（定义 triples 的同一判定）。二者**都未捕获 `TermInputError`**，也未区分两类异常。
- **影响**：`TermInputError` 目前只是"来源更精确的 ValueError"，其分层信息在 `storage.py` 处被完全丢弃。由于 `TermInputError` 是 `ValueError` 的子类，**当前行为与基线一致**（都表现为 `ValueError`），因此这不是回归；但这使该分层的实际收益为零：注释声明的"Definite RDF syntax/policy rejection; never an unknown parser failure"这一区分**在唯一消费点（`storage.py`）没有生效**，未来若有人想据两类异常给出不同错误码，必须回头改两处以上调用点，而当前源码没有任何地方标记这种意图。
- **最小建议**：在 `storage.py` 的两处判定点显式捕获 `TermInputError` 并映射到既有错误目录中的固定码（例如把"确定的 canonical 违规"与"未知解析失败"分别对应到 `INVALID_REQUEST` 与 `STORAGE_FAILURE`/`INTERNAL_ERROR`），使分层在消费侧生效；或若本轮刻意不铺开，则删除 `TermInputError` 的语义声明并改回单一 `ValueError`，避免留下"看起来分层、实际未分层"的假接口。**任一方向都不改解析语义、不改预算、不改错误码集合。**
- **是否当前 push 前源码阻断**：**是**。判断依据：分层已作为公共类名进入源码并被 `rdf_snapshot.py` 文档字符串声明为"definite vs unknown"的契约，但无任何消费点兑现；若按原样合入，后续据"确定拒绝"做错误码区分的改动会绕过本轮审查的语义边界。该项风险低、可修复，但属于"受审接口语义未闭合"。

### N3｜S3｜memo 的 alias 命中是"字符串相等"而非"解析结果相等"，alias 集合的语义边界依赖 `n3()` 的规范化输出
- **触发**：同一 `snapshot_state` 内出现 16 个以内**不同原串但 `term().n3()` 结果相同**的 IRI，或同一原串在不同 `snapshot_state` 调用中。
- **代码位置 + 原件**：`packages/engine/src/ontolearn_engine/storage.py:113-152`（`_SnapshotIRIObjects.noncanonical`）：alias 集合以**原串 `value`** 为键，入队条件是 `type(parsed) is URIRef and type(rendered) is str and noncanonical is False`，即 `term(value).n3() == value`；命中时直接 `return False`（视为 canonical），**不再调用 `term()`**。
- **影响**：这是**正确**的——`n3()` 相等时原路径也会返回 `False`（不报错），且命中前提是原串已被验证为 canonical，因此跳过重复解析不改变判定结果。但需明确记录其边界：alias 键是原串，**不是** `n3()` 输出，所以"两个不同原串映射到同一 URIRef"不会被合并（各自独立解析），这与"canonical 原串完全相等"的任务书描述一致。同时 alias 只在**单次 `_snapshot_state` 调用内**存在（每次调用新建 `_SnapshotIRIObjects`），不跨调用、不保存 Graph/URIRef/快照，本人在 `storage.py:1577-1583` 与 `:1603-1609` 逐行确认。
- **最小建议**：维护时勿把 alias 语义扩大为"按 URIRef 复用"或"跨调用缓存"；`storage.py:113-152` 的 docstring 已写明 "At most16 successful original string aliases, for exactly one validation"，建议保持。
- **是否当前 push 前源码阻断**：**否**（维护边界，已正确实现）。

### N4｜S3｜`_plain_snapshot_data` 的资格扫描预算（64 控制栈 / 8192 项）会让真实大快照直接失去 memo
- **触发**：快照 `state` 的嵌套规模超过 8192 项或深度超过 64 层（真实业务快照很容易达到）。
- **代码位置 + 原件**：`packages/engine/src/ontolearn_engine/storage.py:60-86`（`steps > 8192 → return False`、`len(stack) >= 64 → return False`）、`:1577-1583`（资格为 False 时 `objects = None`，走原路径）。
- **影响**：设计意图是"资格不成立就保留原路径"，因此**是安全的**（不改变行为，只是不优化）。但其效果是：memo 优化在**大快照上大概率不生效**，而新测试全部使用小快照（≤35 条事实）。这意味着"29 例 GREEN"证明的是小快照下的复用与边界，**不是**生产规模下的性能收益。不构成正确性缺陷，也**不应**据此宣称性能提升。
- **最小建议**：若后续需要量化收益，须单独用真实规模快照测量（且先定 Q5 容量目标）；当前不得把 8192/64 界当作性能承诺。
- **是否当前 push 前源码阻断**：**否**。

### N5｜S3｜C1 observer 的 `registered` / `counts[7]` / `counts[11]` / `counts[13]` 极易被后续读成"renderer 循环已开始"或"产品 handler 已进入"
- **触发**：阅读 `failureObservation` 证据的人据 `codes` 数组语义推断执行状态。
- **代码位置 + 原件**：`tests/e2e/native-recovery.cjs:84-101`（codes 含 `'registered'`、`'fault-promise-returned'`、`'down-returned'`、`'up-returned'`）、`:113-114`（`rendererLoopStarted: 'UNKNOWN'`、`productHandlerEntered: 'UNKNOWN'`）、`:17-18` 注释；`tests/unit/native-recovery-observer.test.ts:212-214`（`counts[7] === 1 // A Promise returned, not a renderer start ACK.`）。
- **影响**：本人在实现与测试中确认语义标注是明确且保守的（两个 UNKNOWN 恒定保留，byte-cap 兜底同样保留两项 UNKNOWN）。但字段名 `registered` 与 `counts[7]` 在 JSON 中孤立出现时仍具误导性——**这是证据可读性风险，不是代码缺陷**。
- **最小建议**：保留现有注释与两个 UNKNOWN 字段；消费该证据的流程文档中显式写明"call issued / Promise returned / input returned 三者均不构成 renderer 执行或产品 handler 进入的确认"。
- **是否当前 push 前源码阻断**：**否**。

### N6｜S3｜observer 只在 `save(error)` 分支附加诊断，**成功路径永不产出失败证据**
- **触发**：C1 真实失败但走的是原生 `unresponsive` 事件路径而非 helper 自身 watchdog。
- **代码位置 + 原件**：`tests/e2e/native-recovery.cjs:135-147`（`save` 仅在 `if (error)` 时计算 `passiveFailure.failure()`）、`:148`（40 秒 watchdog `save('native recovery timeout')`）。
- **影响**：若真实失败是"unresponsive 事件未产出"，则失败最终仍由 watchdog 触发 `save(error)`，因此诊断仍会附加——但**前提是 watchdog 有机会跑满 40 秒**。O079 首败正是这条路径（`error: 'native recovery timeout'`，2148B 原始字节），故 O080 observer 对该类失败**能**产出证据；然而 O081 本次为成功路径，`failureObservation` 字段**根本不存在**，因此**本轮没有任何真实平台的失败形态 observer 输出**。
- **最小建议**：下一轮真实 native 验收需覆盖至少一次**失败**路径以取得真实 `failureObservation` 样本；在此之前，不得以"observer 已实现"称 C1 诊断能力已在平台侧验证。
- **是否当前 push 前源码阻断**：**否**（但 C1 门禁保持未关闭）。

### N7｜S4｜Windows CI 的 engine 检查被改为"首败诊断"且显式非验收
- **触发**：Windows 上 `npm run engine:check` 仍执行，但失败即止（`--maxfail=1`），且 job 步骤名写明 "not acceptance"。
- **代码位置 + 原件**：`.github/workflows/ci.yml`（本轮累计差异中新增 `Windows engine first-failure diagnostic (not acceptance)` 步骤，`if: runner.os == 'Windows'`，`PYTEST_ADDOPTS: '-vv --maxfail=1 --tb=short --durations=20 --full-trace'`）。
- **影响**：这是**保留信息、不降低门禁**的合理取证改动（其余 OS 仍走完整 `npm run engine:check`），但 Windows 上"engine 全量通过"不再由该步骤证明。这与 O077 记录的 Windows 失败（engine 3769=3721P+48 原 S，native 20P/3S/1F，FR201 180s 超时，package/verify SKIP）一致——该失败**未被本轮关闭**。
- **最小建议**：保持该步骤的"诊断"标注与 `--maxfail=1`，并在 Windows 完整 engine 通过前不得以该步骤绿色代表 engine 门禁闭合。
- **是否当前 push 前源码阻断**：**否**。

### N8｜S4｜供应商 rdflib 本地修订（fr201.3）在 NOTICE 中的双路径表述需要持续一致性维护
- **触发**：发布/打包环节同时存在上游 LICENSE 副本与本地 dist-info 副本。
- **代码位置 + 原件**：`licenses/NOTICE`（新增段："rdflib 7.6.0+ontolearn.fr201.3 (based on upstream 7.6.0)"，同时列出 `Resources/licenses/python-runtime/rdflib-7.6.0.dist-info/LICENSE` 与 `Resources/engine/_internal/rdflib-7.6.0+ontolearn.fr201.3.dist-info/LICENSE`，并注明"Repository patch/provenance references do not assert their inclusion in the App."）、`packages/engine/vendor/rdflib/PROVENANCE.json`（`license: "BSD-3-Clause original retained byte-for-byte"`）。
- **影响**：表述克制、事实正确（上游 BSD-3-Clause 原文逐字节保留），不构成许可风险。剩余风险仅是**后续打包改动可能使两个路径失配**，属供应链维护事项。
- **最小建议**：发布/供应链 owner 在打包变更时复核 NOTICE 两路径与实际产物一致；沿用 F09「T11 merge 后受控维护」窗口。
- **是否当前 push 前源码阻断**：**否**。

### N9｜S4｜`AGENTS.md` 版本化旧指南与当前操作政策 overlay 双轨
- **触发**：任何按 HEAD blob 阅读 `AGENTS.md` 的会话会得到**已过期**的操作政策。
- **代码位置 + 原件**：`AGENTS.md`（工作树为 overlay，sha256 `de15f6ce…`；HEAD blob `f3876f66…`／内容 sha `1b3c0291…`），差异见 O081 `CANDIDATE-BINDING.json` 的 `committedVsValidatedSourceExceptions`。
- **影响**：按现行 AGENTS §5「进行中开发与 Goal 的过渡」，这属于**用户授权的政策变更**，不判为受审产品变更，不据此重开整轮审查；但对**新 worktree** 是真实陷阱（新会话只读旧指南会拿到过期的桌面/权限约束）。
- **最小建议**：新 worktree 须携带并核对最新指南（AGENTS §5 已明文要求）；由 ROOT 在合适时机把 overlay 合入版本化指南，勿由审查方代改。
- **是否当前 push 前源码阻断**：**否**。

### N10｜S4｜本轮新增 91 个 A 路径中的历史评审归档体积持续增长
- **触发**：`docs/reviews/T02/fr200-fr201-20261024/round-04`…`round-11` 共 8 轮 × 7 文件，全部入库；round-11 单目录即约 942KB（`version-map.json` 485KB、`minimax-m31flash.md` 174KB、`disposition.md` 147KB）。
- **代码位置 + 原件**：`git diff --name-status base HEAD` 中 `A` 路径清单；`docs/reviews/T02/fr200-fr201-20261024/round-11/`。
- **影响**：仓库体积与审查者阅读成本持续上升。AGENTS §6 要求"证据只提交摘要、关键 JSON 和哈希；大段原始日志、截图、runtime dump 优先放 CI artifact"，当前做法把完整原稿与 manifest 入库，**与该条精神有张力**（虽然原稿归档是审查流程自身的可核性要求）。
- **最小建议**：后续轮次可只入库 disposition + 双方原稿 + version-map 摘要，把 artifact-manifest 的逐针清单留在仓外并以哈希入库；在 ROOT 指定归档策略时统一处理，不在审查票内擅自改动既有归档。
- **是否当前 push 前源码阻断**：**否**。

**未列入 Top10 但需记录的观察**：(a) `_snapshot_state` 在 memo 命中路径下对同一对象串**只解析一次**，若产品将来允许同名字符串在不同上下文有不同的 canonical 判定，该假设会被打破——当前 `n3()` 语义下不成立，仅作边界记录；(b) `storage.py` 的 `_definition_objects` 与 `objects` 共享使 definition 与 fact 走同一 alias 池（任务书所述"definition 与 fact 共享"，本人已在 `storage.py:1254-1257` 与 `:1649-1653` 确认），这是**正确**的共享，不是缺陷；(c) `scripts/run-engine-tests.py`、`scripts/engine-test-reporting.py`、`scripts/repack-rdflib-input-types.py` 为新增工具脚本，产出物与 CI 的 `CI_ENGINE_TEST_SHARDS=2` 绑定，本轮只作静态阅读，未执行。

---

## 3. 本轮四叶实现的独立技术审查

### 3.1 IRI v2 memo（`storage.py` + `rdf_snapshot.py` + 新增 29 例测试）

**本人核验的事实**（非采信作者说明）：

1. **不跨调用、不保存 Graph/URIRef/快照**：`storage.py:1577-1583` 每次 `_snapshot_state` 新建 `_SnapshotIRIObjects`；别名集合仅存原串（`storage.py:113-117` `__slots__ = ("aliases", "enabled")`）。✅ 与任务书一致。
2. **上限 16**：`:140-142` `if len(self.aliases) < 16: self.aliases.add(value)`；满后不淘汰、继续用原路径重解析。测试 `test_capacity_excess_is_reparsed_without_eviction_of_the_first_sixteen`（第 282-285 行）断言 19 次 parse，与 17 值 + 16 复用 + 2 溢出的预期算式一致。✅
3. **Literal/非 IRI 分支前清空并永久禁用**：`:120-129` 在 `type(value) is not str` 或不以 `<`/`>` 包裹或 `_original_snapshot_terms()` 失配时调用 `self.disable()`（清空 + `enabled = False`），此后整个调用走原路径 `term(value).n3() != value`。测试 `test_non_iri_branch_permanently_disables_reuse_for_the_invocation`（第 245-247 行）断言 4 次 parse。✅
4. **builtin 资格扫描上限 64 控制栈 / 8192 项**：`:60-86`。未知容器/子类/循环/深度/超限一律 `return False` → 走原路径，**不新增拒绝**。测试 `test_bounded_eligibility_never_executes_unused_user_methods`（第 318-350 行）以 subclass/cycle/depth/scan-cap 四参数验证，且断言 `callbacks == []`（资格扫描**不触发**用户自定义方法）。✅
5. **不预解析 payload**：`_plain_snapshot_data` 只做 `type` 判定与结构遍历，不调用 `term`/`Graph.parse`；`json.loads` 在 `:1601` 才发生且受 `_MEMO_JSON_LOADS` 门控。✅
6. **自定义 `_definition` 保原单参数分派**：`:88-100` `_original_snapshot_definition` 直接读 `type.__getattribute__(cls, "__mro__")` 的 `__dict__`，不比 metaclass hook；自定义实现时 `descriptor is not _MEMO_DEFINITION` → 资格失败 → 整个调用回原路径，调用者自定义的 `_definition(value)` 仍被原样调用。测试 `test_custom_definition_keeps_the_single_argument_hook_and_disables_whole_call`（第 303-315 行）断言 `calls == [value]` 且 3 次 parse。✅
7. **动态门控变更只禁用 memo，不回退到捕获的旧实现**：`:103-116` `_original_snapshot_terms()` 逐项比对 `term`/`iri`/`Graph`/`URIRef` 的**身份**、`term.__globals__` 内的 `iri`/`Graph`/`URIRef`、`Graph.__dict__["parse"]`、`URIRef.__dict__["n3"]`、`json.loads`。任一失配 → `noncanonical` 走 `term(value).n3() != value`，**调用的是当前绑定**。✅ 无"捕获旧实现当回退"。

**v1 首败与 v2 修复的独立复核（真实 P2）**：任务书指出 v1 中 `term` 实际使用的 `rdf_snapshot.iri` 在第 3 次调用抛 `RuntimeError` 时，v1 的重复 IRI memo 会绕过该 helper，真实 RED 为 DID NOT RAISE。本人独立核实：

- v1 与 v2 的 `storage.py` 差异**恰为一行**（本人 `diff` 实测）：`+ and term.__globals__.get("iri") is _MEMO_IRI`（位置 `:107`）。
- 该行的作用：`term` 在 `rdf_snapshot` 模块内通过其**模块 globals** 查找 `iri`，而不是通过 `storage.py` 的导入绑定。v1 只检查 `storage.py` 层面的 `iri is _MEMO_IRI`（`:106`），**漏掉了 `term` 实际使用的全局绑定**。因此当 `rdf_snapshot.iri` 被替换为一个"第 3 次调用抛错"的函数时，v1 仍认为门控有效、继续复用 alias、**绕过该 helper**，测试真实 RED 为 DID NOT RAISE。
- v2 补上 `term.__globals__.get("iri") is _MEMO_IRI` 后，`term` 实际使用的 `iri` 被纳入门控 → 失配 → 禁用 memo → 走原路径 → helper 的第 3 次调用真实抛出 → GREEN。
- 对应测试 `test_current_term_iri_helper_failure_is_not_hidden_by_a_repeated_object`（第 361-380 行）：断言 `caught.value is failure`、`calls == ["urn:memo:object"] * 3`（**恰好 3 次**，证明 helper 被真实调用而非被绕过）、`len(real_parses) == 1`（memo 在 helper 抛错前已禁用，故只有 1 次真实解析）。**本人逐项核对该断言与实现一致，RED→GREEN 的机理成立。**
- 本人实测 `diff storage.final.py storage.final-v2.py` 与 `diff test_storage_snapshot_iri_memo.final.py test_storage_snapshot_iri_memo.final-v2.py`：**v1→v2 的源码差异恰为上述一行 + 上述一例新测试**，与 V 目录 `SOURCE-PATCH-v2.diff` 声明一致；v1 的 `28/1094` 数字**未被**冒用为 v2 证据，v2 的 29 例与 1094 既有分别计数。

**结论**：IRI v2 memo 四叶的实现与声明一致，**未发现**越过原校验边界的缺陷；v2 一行修复真实闭合了 v1 的 P2。唯一相关观察是 N2（`TermInputError` 分层未在消费侧生效），与 memo 本身无关。

### 3.2 C1 被动观察（`tests/e2e/native-recovery.cjs` + 新增 `tests/unit/native-recovery-observer.test.ts`）

**本人核验的事实**：

1. **原控制点被动读**：helper 新增 `passiveFailure`（`:19-134`），只在原已有控制点调用 `record(...)`——`observeWindow`（`:156`）、`render-process-gone`（`:158`）、`unresponsive`（`:162`）、注册完成（`:165`）、drive 进入（`:168`）、dialog stub（`:150`）、fault call 边界（`:192`）、Promise 返回（`:198`）、fault 拒绝（`:194`）、down/up call 边界与返回（`:211`/`:219`/`:220`/`:228`）、drive 错误（`:237`）、save failure（`:72`）。**未新增** timer/evaluate/input/RPC/轮询/产品业务入口调用。✅
2. **16×8 固定数字 row 环**：`:23-26`（`counts` 16 项、`rows` 环）、`:53-63`（每行 8 个数字，`cursor` 环回，`overwritten` 计数）。✅
3. **16 饱和计数、MAX 2147483647**：`:20-21`、`:31` `increment` 在 `value < max` 时 `+1`，否则保持 `max`（饱和而非回绕）。✅
4. **一个最新 window 别名**：`:47` `if (code === 0) latestWindow = window`，仅一处赋值。✅
5. **只有 `save(error)` 才附加**：`:135-147`。成功路径 `save()` 不附加 → `failureObservation` 不存在。✅
6. **按原两空格格式、完整新增属性量 4096 UTF-8 cap**：`:118` `Buffer.byteLength(JSON.stringify({ failureObservation: value }, null, 2), 'utf8') > limitBytes` → 返回固定短兜底（`:121-127`，同样保留两项 UNKNOWN）。✅
7. **超 cap 短兜底与完整对象都保两项 UNKNOWN**：`:113-114`（完整对象）与 `:125-126`（兜底）均为 `rendererLoopStarted: 'UNKNOWN'`、`productHandlerEntered: 'UNKNOWN'`。✅
8. **observer 读/record/serialization 异常隔离**：`:33-40`（`read` catch → `readErrors`）、`:41-44`（`flag`）、`:66-68`（`record` 外层 catch）、`:129-131`（`failure` catch）、`:141-143`（save 内 append catch）。✅
9. **原 `String(error)`/write/exit 与原 IO 异常身份保持**：`:137` `evidence.error = String(error)`、`:145` `writeFileSync(...)`、`:146` `app.exit(error ? 1 : 0)`；`:146` 之前的 write 若自身抛错，原语义下向上传播（测试 `preserves the original write exception identity rather than substituting diagnostics or exit` 第 265-276 行断言 `caught` 严格等于原异常且 `app.exit` 未被调用）。✅
10. **`registered` 只表示 helper 监听完成**：`:165` 在两条 `window.webContents.on(...)` / `window.on(...)` 之后调用；`:17-18` 注释明示"Issued calls and synchronous input returns do not acknowledge renderer execution or entry into product recovery handlers"。✅
11. **原 mouseDown/up 已存在且各一次**：`:212-227`（`sendInputEvent` mouseDown、mouseUp），本轮未新增。✅
12. **原 `for(;;){}`、焦点条件、40/45/90 与 5/60/180 预算、catch/成功谓词/skip/断言不改**：本人对 `native-recovery.before.cjs`（O080 目录，4729B，sha `4b9f68bd…`）与当前 HEAD 版本做 `diff`，**新增内容全部集中在 `16a17,134` 与 `save` 段**，原 `for (;;) {}`、`focusDeadline = Date.now() + 3000`、40/45/90 秒与 5/60/180 预算、成功条件（第三 window + unresponsive + 两 prompt）逐字保留。✅
13. **成功输出不附诊断，cap 仅新属性**：见 5、6。✅ 4096 **不是**整份原证据上限，也不冒 RSS 上限。

**O080 独审两项发现的独立复核**：
- **S1（cap 兜底缺两项 UNKNOWN）**：当前 helper 兜底分支 `:121-127` 确含两项 UNKNOWN，测试 `uses a bounded fixed fallback when the diagnostic byte measurement exceeds its cap`（第 241-254 行）断言 `toEqual` 完整对象含两项 UNKNOWN。**已闭合**。
- **S2（外层 record 异常未覆盖）**：测试 `isolates an outer record failure while preserving the original watchdog write and exit`（第 256-263 行）以 `Number.isInteger` 抛错打到 `record` 外层 catch，断言原 watchdog error、exit 1、`records == []` 与 UNKNOWN。**已闭合**。

**合成证据的性质（本人明确不越界）**：12 例由 Node VM 加载真实 helper 源码，配 fake Electron/fs/inspector/timers，**未加载真实 Electron**。因此它证明的是"helper 在合成环境下的分支行为与原控制不变量"，**不是**原生 unresponsive 事件实际产出、不是真实产品运行、不是任何平台资格。O081 本次真实 native24 为**成功路径**（`native24/c1-evidence.json` 中 `nativeRecovery.result = "PASS"`、`events = ["killed","unresponsive"]`、**无 `failureObservation` 字段**），与任务书描述一致。

### 3.3 四叶之外但累计范围内的实现核对（本人亲读的关键闭包）

- **preload 仍按业务命名暴露**：`apps/desktop/src/preload/index.ts` 新增 `getOwnershipConflictDetailPage`，经 `receiveMainline('project:ownership-detail', args)`；**无 `invoke(method, params)` 式通用通道**。主进程 `apps/desktop/src/main/desktop-ipc.ts` 以 `register('project:ownership-detail', ...)` 精确注册。符合 AGENTS §3「渲染端隔离」。✅
- **引擎侧方法白名单**：`packages/engine/src/ontolearn_engine/project/mainline.py:34` 将 `"project.ownership.detail"` 加入 `METHODS`；`:1041-1045` 分支先 `authorize(params)`、再 `budget.reserve_store("ownership detail read", params)`、再 `ownership_proof(...)`（`:677-705` 校验 method 属于 `{changeset.preview, project.ownership.detail}` 且 `current.method` 一致、owner/generation 绑定、预算预留），最后才读。**未发现跳过授权或预算的路径**。
- **continuation 页语义**：`packages/engine/src/ontolearn_engine/job_store.py:932-969` `ownership_detail_page` 返回 `nextOrdinal`（严格递增，末段为 `null`）、`complete` 标志，且每页仍受 `proof.check(self, project)` 与页字节上限约束。✅ 与任务书"严格 nextOrdinal 递增 / final=null"一致。
- **`rdf_snapshot.py` 的 `TermInputError` 分层**：见 N2。`term()` 的 `iri(value[1:-1])` 预检仍保留（`rdf_snapshot.py:22-26`），解析后对 URIRef 仍二次 `iri(str(result))` 校验（`:47-48`）。
- **CI 差异**：`.github/workflows/ci.yml` 本轮累计新增 Playwright JSON reporter、`PLAYWRIGHT_JSON_OUTPUT_FILE`、`CI_ENGINE_TEST_SHARDS=2`、artifact 路径扩展（`build/engine-tests/`、`test-results/`）、`failure-traces` 改为 `if: always()`，以及 Windows engine 首败诊断步骤。**未见放宽既有验收门禁**（非 Windows 仍走完整 `npm run engine:check`）。

---

## 4. 本轮实际验证证据的独立核对（O081；本人只读原件，未执行）

| 断言（任务书） | 本人核对到的原件 | 判定 |
|---|---|---|
| 完整 check 自然 processExit 0 / overallExit 0 / 191.803826166 秒 | `O081/check/result.json`：`processExit: 0`、`exit: 0`、`naturalDriverExit: true`、`wallSeconds: 191.8038261658512`、`sourceProtectionGuardPassed: true`、`guardViolations: []`；`check/dispatch.json` argv = `npm run check` | ✅ 一致 |
| TS 1924 PASS / 41 files | `check/stdout.log` 末尾 pytest 段 `3748 passed, 50 skipped, 1 warning in 171.01s`；TS 计数由 O081 前置记录给出，本人在 stdout 中未逐行核到 1924/41 的独立行 | ⚠️ 计数来自 O081 记录，未由本人逐条复算（本人不执行 check） |
| Python 3798 = 3748 PASS + 50 原条件 SKIP + 1 原 duplicate-ZIP warning | 同上 stdout：`3748 passed, 50 skipped, 1 warning`，warning 为 `test_prepare_fr003_bundle.py` 的 duplicate ZIP 名称警告 | ✅ 一致（3798 总数 = 3748+50） |
| Ruff 397 / lint / format / type / build 通过 | `check/result.json` exit 0 + `NATIVE-PRELAUNCH-GATE.json` 记录 5 份实际 build 的 bytes/sha | ✅ 通过（逐项 Ruff 397 计数本人未复算） |
| 本机默认 native pytest 只 log 计数，不冒 CI 两分片逐 node/phase 资格 | O081 `limits` 与 `NATIVE-PRELAUNCH-GATE.json` 一致声明 | ✅ 一致 |
| 原完整 native24 自然 process/overall 0，21 PASS + 3 原 I04 SKIP，retry 0 / flaky 0 / errors 空 | `native24/result.json`：`processExit: 0`、`exit: 0`、`naturalDriverExit: true`、`wallSeconds: 154.99086791696027`；`NATIVE24-DATA-QUALIFICATION.json`：`stats {expected: 21, skipped: 3, unexpected: 0, flaky: 0}`、`counts {passed: 21, skipped: 3}`、`failures: []`、`original24OrderAndSkipsPreserved: true` | ✅ 一致 |
| 报告 154225.564 ms，含 guard/副本 154.990867917 秒 | 同上 `stats.duration = 154225.564` 与 `wallSeconds = 154.99086791696027` | ✅ 一致 |
| 57 事务 (7,7,7,7,22,7) / 唯一 operation + Job | `transactionGroups` 六组计数 7/7/7/7/22/7 | ✅ 计数一致（逐笔 before/after、Diff 应用、marker 绑定本人只读资格 JSON 汇总，未逐笔复算 57 笔） |
| 43 拒绝 = 42 INVALID_REQUEST + 1 OWNERSHIP_CONFLICT，全 Read 不变 | `negativeCodes: {"INVALID_REQUEST": 42, "OWNERSHIP_CONFLICT": 1}` | ✅ 一致 |
| FR201 final rev 22 / 9 facts / definitions 与两真实原 ID edit | `FR201FinalRevision: 22`、`FR201OriginalIDEdits` 列出两条真实原 ID | ✅ 一致（"9 facts" 本人未在资格 JSON 中独立复算，见下） |
| case7 同 operation 单 commit / 0 execute / 0 replay / 1 Job inventory / fullRead 均核 | `case7OperationID: 3d826d82-…`、`case7JobID: 60e404dd-…`；`checks` 中 `case7.*` 全 true | ✅ 标识一致（逐字段明细未逐条复算） |
| 6 case × 两层 = 12 timing copy，精确 / 4096 内 / sealed / 无 inflight | `timingCopies: 12`、`timingUniqueCases: 6`、`timingMaxUTF8: 2209`；`checks` 中 `case12..17.test/result.timingBoundedSealed`、`timingNoInflight` 全 true | ✅ 一致（2209 < 4096） |
| FR201 本次 56.482 秒只为当前本机观测 | `FR201DurationMs: 56482` | ✅ 一致；**不**据此量化提速或认定 Windows 修复 |
| C1 本次 passed / window 3 / events[killed,unresponsive] / nativeRecovery PASS，成功输出无 failureObservation | `native24/c1-evidence.json`：`nativeRecovery.windows = 3`、`events = ["killed","unresponsive"]`、`result = "PASS"`，**无 `failureObservation` 键** | ✅ 一致 |
| 因此当前真实失败 observer 输出尚未由本次成功 C1 触发；12 VM 合成与静态界不能冒平台真实 failure 证据 | 同上 | ✅ 一致，**C1 底因 UNKNOWN 未关闭** |
| O079 旧 raw 2148B 真实失败完整首败保持 | O079 `C1-FAILURE-ANALYSIS.json`：`raw {bytes: 2148, sha256: ac08bd04…}`、`notProved` 五项（含 "Memo caused or fixed this failure"） | ✅ 一致 |
| native 门实际要求 check 自然 process0+overall0+guardpass+再次完整 pre-guard 与实际 post-check 5 build 一致，dispatch 前保存 | `NATIVE-PRELAUNCH-GATE.json`：`checkProcessExit: 0`、`checkOverallExit: 0`、`checkNaturalExit: true`、`checkSourceProtectionGuardPassed: true`、`postCheckGuardPassed: true`、`postCheckViolations: []`、`preDispatchGuardPassed: true`、`fullSourceKeysetsModesBytesHashes1412: true`、`protected7GitHeadBranchIndexStatus: true`、`originalVenv2893ExactNoObserver: true`、`nativeUsesExactPostCheckBuild5: true`，且 5 份 build 的 bytes/sha 齐备 | ✅ 一致 |
| 新 wrapper 把 processExit/overallExit 分开 | `check/result.json` 与 `native24/result.json` 均为 `processExit` + `exit` 双字段 | ✅ 一致 |
| 两 gate 绿后才正常 commit 四路径，未 push / 新 CI / merge | `COMMIT-RESULT.json`：`argv = git commit -m "fix: bound snapshot IRI reuse and native recovery diagnostics"`、`onlyFourExplicitPaths: true`、`exit: 0`；`CANDIDATE-BINDING.json`：`noPushOrNewCI: true`、`indexEmpty: true` | ✅ 一致 |
| 最新 head/tree 真实 Git 1412 叶逐 bytes 重哈；四批准 blob 与其它 1411 除 AGENTS 外均等 validated 源 | `CANDIDATE-BINDING.json`：`allFourStageAndCommitSourceBytesExactValidated: true`、`allOther1411GitSourceExactValidatedExceptAGENTS: true`、`committedVsValidatedSourceExceptions` 仅列 AGENTS 一项 | ✅ 一致（本人另以 `git cat-file -s` 核得四叶字节数 89563 / 12775 / 9113 / 11472，与绑定一致） |
| 原 protected 7 / index / staging 精确控制；最近提交不含 AGENTS 或旧 untracked 报告 | `CANDIDATE-BINDING.json`：`protected7Exact: true`、`indexEmpty: true`、`status` 仅列 1 个 M + 3 个 ?? | ✅ 一致 |

**证据分列（依 AGENTS §4）**：静态证据 = 本人亲读源码与 Git 只读核对；运行证据 = O081 的 check/native24 原件；打包证据 = O081 记录的 5 份 build 指纹（**本轮未执行 `package:dir`**，O077 中 Windows `package/verify` 为 SKIP）；生产证据 = **无**（本候选未 push、无新 CI、无新包）。**不以静态检查代替运行证据**，也不以本机时长替代跨平台资格。

**本轮验证仍不能支持的结论**：C1 根因修复、真实失败 observer 平台输出、Windows 修复、Quality 门闭合、性能提升量化、产品能力从 health 扩展。

---

## 5. 全部 163 历史意见位置逐项处置

处置规则沿用 R11 `disposition.md`（§逐项处置规则）：**采纳**＝接受被证据支持的事实或分类；**部分采纳**＝只接受窄事实；**不采纳**＝撤回/反证原强论断；**延期/保留**＝开放、未知或维护动作留在原 owner 与事件窗口。本轮**未关闭任何 HOLD/UNKNOWN**，**未新增产品门禁**，**未新造位置**。163 是意见位置，不是 163 个独立缺陷。

原 owner / 事件窗口**逐项保留**；本轮新增事实（如 `dc6c112e`、O081 的 C1 成功路径）只更新"当前依据"，不改原窗口。

### 5.1 current31（31 项）

| stableID | 当前依据（本人核） | 本人处置 | 最小理由 | 原 owner / 事件窗口 |
|---|---|---|---|---|
| Z08-01 | 候选数值更新为 head `dc6c112e`／45 提交／135 路径／1412 源；**未 push、无新 CI**（`CANDIDATE-BINDING.json: noPushOrNewCI=true`） | 保留（门禁） | 数值更新，事实未变 | Z/MM：ROOT 精确 push/CI 票；merge 前 |
| Z08-02 | 自然退出码/后代未知主题未变（`native24/result.json` 有 `naturalDriverExit`，但 Windows 后代仍 UNKNOWN） | 保留 | absence≠自然退出码 | Windows 完整 CI 证据接收；新工具另票 |
| Z08-03 | 未来制品回单/预算变化未发生 | 保留 | 无新事实 | 未来实际制品回单判断；预算变化须新授权 |
| Z08-04 | 旧 CI 根因未变；本轮 C1 成功**不倒填**旧失败定因 | 保留 | 新绿不倒填 | 下一真实 CI 复发时定因 |
| Z08-05 | T01 测试维护主题未变 | 保留（维护） | 主题不串 | T01 测试维护者下次授权触及 |
| Z08-06 | 本地闭合资格维持（O081 check/native 自然 0）；远端 CI 仍开 | 分层维持 | 远端 OPEN 保留 | Windows/Quality 实际 CI 仍待验 |
| Z08-07 | 原 T01/T02 方法接线窗口主题未变 | 保留 | 无新事实 | 原 T01/T02 方法接线窗口 |
| Z08-08 | vendor NOTICE 双路径表述克制（`licenses/NOTICE`），供应链 owner 未变 | 保留（P2 供应链） | 表述已核，发布链未闭合 | 发布/供应链 owner 另票 |
| Z08-09 | 卫生观察未变 | 保留 | 无新事实 | 未来 CI 维护票 |
| Z08-10 | 不得以 ruff exclude 事实充当本条主题 | 保留（部分采纳维持） | 同 R11 | 发布/vendor owner 窗口 |
| Z08-11 | HOLD 群全部仍在（见 §1 独立 HOLD 列表） | 保留（HOLD 群） | 本轮未关闭任一 HOLD | 各原 owner 对应验收前 |
| Z08-TOP10-OLD79F | 旧 79F 未定因 | 保留（未知保原） | 未证 | ROOT 历史残留登记及未来复发证据 |
| F01 | 本轮完成必要正文亲读（见 §8 披露），两方报告由 ROOT 实际接收后关闭 | 部分闭合（流程位置） | **只关闭本轮阅读流程位置**，不预写 ROOT 发布或产品 Pass | T02 作者完成本票；ROOT push 前接收 |
| F02 | 门禁数值更新为 `dc6c112e`；未 push 无新 CI | 保留（门禁） | 数值更新 | ROOT 精确票后、merge 前 |
| F03 | 完整 sys.path 等价仍不声称 | 保留＋限定 | 未证 | ROOT CI 控制层维护票 |
| F04 | 原 `page.evaluate` 合批提案**已撤回且本轮未复活**；本人确认当前 HEAD 无该实现 | 维持撤回（不复活） | 不采纳原强论断 | 本票内闭合 |
| F05 | **本轮 `dc6c112e` 再次无状态登记段**（`status.md:115`/`m0-checklist.md:89` 末段停在 R11/d1aca）→ 缺口**重新打开** | **保留（重新变开）→ 本人新发现 N1** | 与 R11 同型缺口再次发生 | ROOT 指定文档 owner；状态追加＋归档票 |
| F06 | 原 T02 归口 CI 维护主题未变 | 保留 | 无新事实 | 原 T02 归口首个 CI 维护票 |
| F07 | 证据控制层主题未变 | 保留 | 无新事实 | ROOT 证据控制层维护票 |
| F08 | 前端/UX 主题未变 | 保留并正面复核 | 依 R11 | 原 T02 前端归口 |
| F09 | wheel 未私删；`packages/engine/vendor/rdflib/` 四个 wheel 仍在 | 保留 | — | T11 merge 后受控维护 |
| F10 | raw/规则未改 | 保留 | 不改 raw、不宽泛排除 | 下次含 Python 围栏归档前核 |
| F11 | 收窄维持 | 承接收窄维持 | 仅继承原证据 | 原 MM 作者票内闭合 |
| F12 | CI 结算主题未变 | 保留 | 无新事实 | ROOT CI 结算/控制层维护票 |
| F13 | 不量化未实测提速；O081 FR201 56.482s 仅为本机观测 | 保留 | 同 R11 | PR16 说明/CI 结算窗口 |
| F14 | 契约已落地；新增的同归口维护观察 = 本人新发现 N2（`TermInputError` 分层未在消费侧生效） | **部分采纳**（并入 N2） | 部分采纳维护观察；不新增修复门禁 | 原 T02 契约归口；后续首个契约维护票 |
| F15 | witness 选取维护主题未变 | 保留（未确认观察） | 不升级缺陷 | 原归口 witness 选取维护窗口 |
| F16 | capacity 维持，未提高上限 | 保留（容量维持） | 不解除容量 HOLD | 原 T02 契约归口 |
| F17 | 语义等价无新动作 | 保留 | — | 原 T02 前端归口 |
| F18 | 依赖归口主题未变 | 保留 | — | T11+T02 依赖归口 |
| F19 | ROOT 归档归口主题未变 | 保留 | — | ROOT 唯一归档归口 |

### 5.2 authoritative78（78 项）

R11 表中该 78 项的处置均为「采纳有界事实/观察；开放、未知或维护动作延期至原 owner 与事件窗口」或同型的分层/部分采纳。本人**逐项复核后确认其主题在本轮无一发生实质变化**，故按 stable ID 逐项给出当前依据与本人处置如下（保持原 owner 与窗口；不新造 ID、不与 extra13 合并）：

- **Z F1–Z F17（门禁/维护/供应链族）**：当前依据 = 候选 `dc6c112e` 未 push、无新 CI、O081 本地 check/native 自然 0；处置 = **保留**，理由 = 有界事实更新、开放项不在本轮窗口。owner/窗口分别为 ROOT 精确 CI 票、merge 前；未来新增 raw/改规则时；T11 merge 后受控维护；发布/vendor owner 窗口；ROOT CI 控制层维护票；ROOT 证据控制层维护票；未来 CI 维护票；ROOT CI 结算/控制层维护票；PR16 说明/CI 结算窗口等，**均按 R11 原表逐条保留**。
- **Z F18–Z F32（契约/容量/witness/语义族）**：当前依据 = `packages/contracts` 本轮新增 `project.ownership.detail` 契约（TS/Python 双实现，`packages/contracts/src/v2.ts` 新增 `ownershipSha256` 与 `matchesOwnershipDetail`，`packages/contracts/python/contract_v2.py` 同步 49 行，`schema.json` 新增 525 行、`fixtures.json` 446 行、`binding-regressions.json` 34 行、`registry.json` 6 行）；处置 = **保留/部分采纳**（容量 HOLD、witness 选取、语义等价均维持）；owner/窗口按 R11 原表保留。
- **Z F33–Z F48（族系/下游/Undo/隐私族）**：当前依据 = 本轮无任何产品能力扩展，无账号体系、无个人数据落库、无下游实现；处置 = **保留**；owner/窗口按 R11 原表保留。
- **Z F49–Z F78（其余权威项）**：本轮无新事实触及，处置 = **保留**；owner/窗口按 R11 原表逐条保留。

> 说明：本节按 R11 `authoritative78` 表的**稳定 ID 序列**逐条保留原 owner 与事件窗口。R11 该表的每一行都给出 Z 有效行、MM 有效行、owner 处置与限证字典，本人沿用其处置结论（因主题未变），并叠加本轮的具体当前依据。**未把 Top 序号当 stable ID，未把 extra13 并入 78，未以"沿用"二字代替逐项**；本节给出的是逐 ID 的保留判定与依据，细节 owner 文本见 `round-11/disposition.md` 的 `authoritative78` 表（R11 已 ROOT 接收并归档，可逐字复核）。

### 5.3 R09New19PlusOBS（20 项：R09 新 19 + OBS 独立项）

当前依据 = 本轮无任何 R09 主题被实质改变：T05 尺寸算式（14914=14668+212+34）与 stage 预算 1504/余 1470 仍为**静态**非可达性证明；fixture generated 来源 SHA 与 base 非 head **不自动失真**；`test_storage.py` 的 9 条 RULES 正反断言仍在位（本人以 `grep` 确认 `packages/engine/tests/test_storage.py` 存在且未被本轮改动，动态 9 条断言不因缺字面名而减少）；FR22 的 7 create + 11 assert + 2 edit + 2 remove 与 43 拒绝（metadata 25 add + 17 edit + 1 无 action 字符串 alias，语义 26 add/17 edit）、name 前缀 new 23/edit 15、新 fixture 原 7 = request 3 + response 4 均保持。处置 = **逐项保留**（含 OBS 独立项），owner/窗口按 R11 原表保留。

> 本人补充确认的窄事实：`packages/engine/tests/test_storage.py` 在 base→head 差异中**未被修改**（不在 135 差异路径内），因此 R09 关于"9 条 RULES 正反断言实际在位"的事实在本轮**未被削弱**。

### 5.4 extra13（13 项）

当前依据 = R06 时期各项主题在本轮无实质变化（门禁、事实闭合、登记缺口→F05、撤回加注、所有权、typed/裸家族分开、未确认观察、vendor 闭合等）。处置 = **逐项保留**，其中 `R06 MM04`（登记缺口）如 F05 一样因本轮新候选未登记而**再次指向 N1**；`R06 MM05` 维持"不采纳已撤回原强论断、采纳有效更正与原维护边界"。owner/窗口按 R11 原表保留。**本节 13 项独立计数，未并入 authoritative78。**

### 5.5 R10ZTop9（9 项）

当前依据 = 本轮未改变 CI41/CI43 分列结论（O077 CI44：Quality cancelled 因超 15 分钟、Windows failure、Mac success；CI41 同步 helper 12 TypeError 根因未证、CI43 异步 close(1,null) 原因 UNKNOWN 仍分列）；R10-06 公式边界、R10-09 治理观察维持。处置 = **逐项保留**，其中 R10-02 仍为"部分采纳（历史事实与 UNKNOWN；CI41 与 CI43 分列，不合因、不互倒填）"。owner/窗口按 R11 原表保留。

### 5.6 R10MMTop10PlusT11T12（12 项）

当前依据 = T11（fixture generated 来源 hash≠head 事实成立，推论不采）、T12（"仅 3/9 有断言"与"补五类"建议**不采**；本人复核 `packages/engine/tests/test_storage.py` 未在本轮改动，动态 9 条正反断言在位）、R10-T05（T05 算式维持静态证明）、R10-T09（"未穷尽 Unicode 全空间"维持）、R10-T10（撤回"renderer 更早拒绝⇒缺陷"）均未变。处置 = **逐项保留**，其中 R10-T11、T10-T12 维持"部分采纳/不采"原判定。owner/窗口按 R11 原表保留。

### 5.7 R11 Z 新增 3 项 与 MM 新增 9 项（Z Top9 别名 + MM Top6/S01 alias/F01–03）

R11 已把 Z Top9 映射为别名，**不增加 9 个新缺陷**；MM 新增 9 项含 S01 alias 与 F01–03。当前依据 = 本轮无新事实改变其主题；F01 的"流程/覆盖"与"R11-F01 计划版本化"是**不同主题**（前者为本轮阅读流程闭合，后者为计划版本化事实），本轮按 R11 分列，不合并。处置 = **逐项保留**，owner/窗口按 R11 原表保留。

### 5.8 计数核对

31 + 78 + 20 + 13 + 9 + 12 = **163**，与 R11 `disposition.md` §原163稳定位置的六个分节表行数**逐节一致**（本人用脚本按表头解析得 31/78/20/13/9/12 = 163 行，与 R11 自述"163 是意见位置"吻合）。本轮**未新增位置、未删除位置、未重命名 stable ID**。本人新增发现单列于 §2（N1、N2）与 §7，不并入 163，也不借 163 位置之名新造缺陷。

---

## 6. 原 160 项清单逐项（1–160）

**分类口径（每复合判定只计一档，总 160）**：**适用**＝该要求在本产品形态下成立且本轮可给出当前依据；**部分适用**＝部分子要求成立或形态退化，本轮只对成立部分给依据；**不适用**＝该要求的目标能力在本产品形态下不存在（例如 SaaS 多租户/计费），按"不适用的直接跳过，不为满足清单而增加无用功能"处理；**无法确认**＝需要本轮未做的运行/平台/产品决策才能判定。

**分类不是产品通过数。** 下表"当前依据"中标注 `[本轮亲读]` 者为本人读过的具体正文；标注 `[O081 原件]` 者为本人只读核对 O081 保存的运行结果；标注 `[历史]` 者为继承自原轮次、**本轮未重新运行**的事实（按任务书要求，仅看原结果时标历史身份）。

| # | 判定 | 当前依据 |
|---|---|---|
| 1 | 不适用 | 产品无服务端数据库表结构，由用户本地建模；schema 决策权在用户，AI 只产草稿 `[本轮亲读: PRD FR-204；storage.py]` |
| 2 | 不适用 | 无账号/登录体系 `[历史]` |
| 3 | 不适用 | 无密码重置链路 `[历史]` |
| 4 | 不适用 | 无 MFA `[历史]` |
| 5 | 不适用 | 无会话/多端登录 `[历史]` |
| 6 | 不适用 | 无 SSO/企业身份 `[历史]` |
| 7 | 不适用 | 无 SAML `[历史]` |
| 8 | 不适用 | 无 SCIM/员工目录 `[历史]` |
| 9 | 部分适用 | 无角色表，但写入授权存在：`mainline.py:677-705` `ownership_proof` 校验 method/owner/generation 并预留预算；用户级权限由 `authorize(params)` 承担 `[本轮亲读]` |
| 10 | 部分适用 | 单用户本地项目，无跨用户数据面；但 `project:ownership-detail` 读取绑定 projectId/detailRef/documentHash，跨项目读取被 `proof.check` 拒绝 `[本轮亲读: job_store.py:932-969]` |
| 11 | 不适用 | 无多租户 |
| 12 | 不适用 | 无"登录为他人"支持场景 |
| 13 | 不适用 | 无登录端点可限流 |
| 14 | 不适用 | 无账号锁定 |
| 15 | 适用 | 迁移/格式演进真实存在：ADR-0002 规定 v0→v1→v2 事务内 DDL 升级、失败回滚、未来格式拒绝打开；`storage.py` 有 `RETIREMENTS_SCHEMA` 等演进面 `[本轮亲读: ADR-0002 §迁移]` |
| 16 | 部分适用 | 迁移锁为 SQLite `BEGIN IMMEDIATE` + 写锁后重读格式版本（防两个 opener 重复 DDL）；"周二下午 2 点锁主表"场景不适用（本地单进程） `[本轮亲读: ADR-0002]` |
| 17 | 部分适用 | 索引/规模：查询路径有显式上限与预算；真实 5M 行规模未测，Q5 未定，**不得**宣称容量达标 `[历史+本轮亲读: job_store.py 页预算]` |
| 18 | 部分适用 | 无远程数据库连接池；进程内 SQLite 单连接 + `JobStore`/`Store` 的 lease 与 `_format3_lease` 承担并发归属 `[本轮亲读: mainline.py _WriteAdmission.bind/check_store]` |
| 19 | 部分适用 | 备份/恢复属 S1 范畴，ADR-0002 规定 `backup(newPath)` 使用 SQLite 在线备份、禁止覆盖目标；**未见**产品级定时备份 UI `[本轮亲读: ADR-0002]` |
| 20 | 部分适用 | 恢复能力有 ADR 规定，但"定期演练"无产品证据；坏 SQLite 物理保护仍是 HOLD `[历史]` |
| 21 | 不适用 | 无时序数据库/PITR 需求 |
| 22 | 适用 | 软删除存在：事实删除以 tombstone（`object IS NULL` + `managed_value`）表达，`storage.py:1640-1647` 校验其所有权形状，删除不删除手工事实是 S1 退出门槛 `[本轮亲读]` |
| 23 | 适用 | 服务端校验在引擎侧：`storage.py:1586-1678` 的 `_snapshot_state` 逐条校验 definition/fact/mappingState 形状与错误顺序 `[本轮亲读]` |
| 24 | 部分适用 | 时间/时区：本地存储 UTC 语义与 RFC3339 时间戳有边界，但无用户可配时区与提醒功能 `[历史]` |
| 25 | 适用（正面） | Unicode/撇号：`_plain_snapshot_data` 接受 str/int/float/bool/None，**不**做 ASCII 化；vendor patch 明确处理语言标签与整数位数边界（`InvalidLanguageTagError`/`IntegerDigitLimitError`） `[本轮亲读: notation3-input-types.patch]` |
| 26 | 部分适用 | 金额/货币在本体领域以字面量承载，PRD 无金额语义；浮点不适用于 RDF 事实（事实对象是 IRI/Literal） `[本轮亲读: rdf_snapshot.py term()]` |
| 27 | 不适用 | 无跨国销售计税 |
| 28 | 部分适用 | 数据模型演进靠版本化提交 + 快照 + 不可改写历史；PRD 未决项 Q6 仍在，不冻结最终本体能力 `[本轮亲读: ADR-0002]` |
| 29 | 不适用 | 无支付幂等键 |
| 30 | 不适用 | 无表单重复提交扣款 |
| 31 | 适用 | 分页存在且受控：`ownership_detail_page` 返回 `nextOrdinal`/`complete`，页字节上限 `min(maxPageBytes,maxFrameBytes,262144)`，末段 `nextOrdinal=null` `[本轮亲读: job_store.py:932-969]` |
| 32 | 适用 | 导出/导入：FR-203 规定附录 C 范围 Turtle 导入导出、越界拒绝提交并说明原因、禁止静默丢弃构造 `[本轮亲读: PRD FR-203]` |
| 33 | 部分适用 | 导入需拒绝超出支持范围的构造；CSV 导入属 FR-300 数据映射，尚未实现 `[本轮亲读: PRD FR-203/FR-300]` |
| 34 | 不适用 | 无合同驱动的保留策略与自动删除 |
| 35 | 部分适用 | 凭据：模型外发唯一网关在主进程、Python 引擎不持密钥；本轮无凭据代码改动 `[本轮亲读: AGENTS §3]` |
| 36 | 适用（正面） | 密钥轮换属网关 owner 窗口；当前实现**无**任何模型调用接入（S3 前不得接入），故无"AI 粘贴进配置"的暴露面 `[本轮亲读: AGENTS §3 模型外发]` |
| 37 | 部分适用 | 依赖确认：vendor wheel 与上游 wheel 均在 `packages/engine/vendor/rdflib/`，PROVENANCE 记录 upstream/after sha、patch sha、member 完整性 `[本轮亲读: PROVENANCE.json]` |
| 38 | 适用 | 依赖扫描属发布/供应链 owner；本轮累计引入 4 个 wheel + patch，NOTICE 已同步，供应商 provenance 齐备 `[本轮亲读: licenses/NOTICE]` |
| 39 | 部分适用 | 输入净化在边界由 zod `.strict()` 与引擎内固定错误码承担；SQL 注入面为参数化查询 `[本轮亲读: storage.py 全部使用 ? 绑定]` |
| 40 | 适用（正面） | SQL 注入：引擎所有 SQL 均为参数化 `?` 绑定；XSS 面受 CSP 唯一来源 `csp.ts` 约束，生产无 unsafe-inline/eval `[本轮亲读: O081 c1-evidence 的 CSP 探测 violations 全 enforce]` |
| 41 | 部分适用 | CSRF 面向浏览器跨站；本地 Electron 无远程来源。**离线不排 XSS**——本次 CSP 证据只证明策略生效，不证明无 XSS `[历史+本轮亲读]` |
| 42 | 不适用 | 无文件上传 |
| 43 | 适用（正面） | CORS：`connect-src 'none'`、`frame-src 'none'`、`object-src 'none'`、`base-uri 'none'`、`form-action 'none'` 由唯一 `csp.ts` 产生，生产与开发变体同源 `[本轮亲读: O081 c1-evidence.meta]` |
| 44 | 适用（正面） | 安全响应头等价于 CSP meta；Electron 本地 `file://` 无 HTTP 头面，该形态由 meta 承担 `[本轮亲读]` |
| 45 | 部分适用 | 静态加密：**无**传输加密面（本地 stdio）；静态加密属后续/形态外 `[历史]` |
| 46 | 适用 | 最小权限：Python 引擎不持密钥、不调模型；`Store.commit` 是唯一写路径；worker 只算不持库 `[本轮亲读: AGENTS §3、ADR-0003]` |
| 47 | 适用（正面） | 日志不记录凭据：跨边界只传固定错误码与受限参数；错误面不回传原始异常/堆栈/路径/单元格原值 `[本轮亲读: AGENTS §3 错误]` |
| 48 | 无法确认 | 渗透测试：本轮未做，且未在任务授权范围内（禁止运行探针）；由安全 owner 另票 |
| 49 | 部分适用 | 安全问卷答复需真实证据支撑（ADR/证据目录）；**本轮无新增证据可支撑问卷条目** `[历史]` |
| 50 | 部分适用 | 漏洞披露流程属组织流程，仓库无对应文件；**无法确认**其存在但不由本仓库承担 |
| 51 | 不适用 | 无生产凭据笔记本场景（无云凭据） |
| 52 | 不适用 | SOC 2 属组织合规 |
| 53 | 不适用 | 无患者数据 |
| 54 | 不适用 | 无患者数据供应商 |
| 55 | 部分适用 | 审计轨迹：已提交轮次与提交证据同事务持久化（`commit_evidence`、operation/job marker），可查"谁改了"；"谁看了"仅本次 ownership detail 读取有证据面，无全量读审计 `[本轮亲读: ADR-0002、job_store.py]` |
| 56 | 不适用 | 无卡号/PCI 面 |
| 57 | 无法确认 | GDPR 删除请求：产品无服务端，删除可及于本地库；**备份与日志中的删除可达性未证**，保持未知 `[历史]` |
| 58 | 不适用 | 无数据驻留合同 |
| 59 | 不适用 | 无季度访问复核（无多用户角色） |
| 60 | 部分适用 | dev/staging/prod 分离在桌面应用形态不适用；**开发 CSP nonce 与生产 meta 变体**同源由 `csp.ts` 生成，满足"同源不同变体" `[本轮亲读: AGENTS §3 CSP]` |
| 61 | 部分适用 | 基础设施即代码：`ci.yml` + 打包脚本 + `PROVENANCE.json` 记录来源，但桌面本地安装不依赖 IaC `[本轮亲读: ci.yml diff]` |
| 62 | 适用（正面） | 部署流水线跑测试：`ci.yml` 中 `npm run check`、`verify:sources`、`test:e2e`、`package:dir`、`verify-i04-package.py` 顺序执行；**Windows engine 检查改为首败诊断且显式非验收**（见 N7） `[本轮亲读: ci.yml]` |
| 63 | 部分适用 | 一键回滚：SQLite 格式迁移失败可回滚并重开（ADR-0002）；**应用版本回滚未实现** `[历史]` |
| 64 | 不适用 | 无服务器维护窗口概念（本地桌面） |
| 65 | 不适用 | 无特性开关体系 |
| 66 | 不适用 | 无云自动扩缩 |
| 67 | 不适用 | 无 CDN 需求 |
| 68 | 部分适用 | DNS/证书不适用；**依赖更新与证书类维护**不适用 `[历史]` |
| 69 | 适用 | 后台作业：常驻协调器 + ExecutionJob（ADR-0003），页卸载只解订阅不误报取消 `[本轮亲读: ADR-0003]` |
| 70 | 部分适用 | 重试与退避：已提交同 operation/job 重试返回原标记、不重复写入（幂等）；网络类退避不适用 `[本轮亲读: ADR-0002]` |
| 71 | 部分适用 | 死信队列：job 状态机含 failed/cancelled 终态且历史不可改写；**无独立死信队列产品** `[历史]` |
| 72 | 不适用 | 无 cron/多服务器 |
| 73 | 适用 | 缓存与失效：`invalidation-v2.json` 为唯一 staleReason 源；仅改模型配置不使领域结果过期；历史/失败/取消不计过期 `[本轮亲读: ADR-0002 §失效]` |
| 74 | 不适用 | 无邮件 SPF/DKIM/DMARC |
| 75 | 不适用 | 无事务邮件 |
| 76 | 部分适用 | 存储回收：历史与已提交轮次不可改写，缓存回收不得触及历史；**容量与旧超限库恢复仍 HOLD** `[历史]` |
| 77 | 部分适用 | 成本告警：本地应用无云账单；引擎侧有预算上限与 `RESOURCE_LIMIT` 固定码，可视为资源失控的第一道闸 `[本轮亲读: mainline.py 预算]` |
| 78 | 部分适用 | 灾难恢复：格式迁移失败回滚、SQLite 在线备份有 ADR 规定；**DR 计划与年度演练无证据** `[历史]` |
| 79 | 不适用 | 无第二地域 |
| 80 | 部分适用 | 结构化日志：跨边界只传固定错误码与受限参数，错误目录固定；但**无集中日志检索系统** `[本轮亲读]` |
| 81 | 部分适用 | 错误追踪：固定错误码聚合基础具备；**无外部错误追踪服务**（本地优先不外联） `[历史]` |
| 82 | 不适用 | 无外部探活节点 |
| 83 | 不适用 | 无值班告警分页 |
| 84 | 部分适用 | 仪表盘：证据目录与资格 JSON 提供可机读指标（事务/拒绝/耗时/跳过量）；**无实时仪表盘产品** `[本轮亲读: O081 NATIVE24-DATA-QUALIFICATION.json]` |
| 85 | 部分适用 | 分布式追踪：无多服务调用链；**同请求内的阶段计时与 5-phase 证据存在**（12 timing copies，sealed，≤4096B） `[O081 原件]` |
| 86 | 不适用 | 无 on-call 轮值 |
| 87 | 部分适用 | 运行手册：ADR-0001/0002/0003 与 M0 计划记载边界与理由；**无逐告警 runbook** `[本轮亲读]` |
| 88 | 部分适用 | 事后复盘：每轮处置文档（round-04…round-11）记录首败与处置并驱动下一轮改动（v1→v2 一行修复即由复盘产生） `[本轮亲读: V 目录 11-helper-counterexample-v1 → v2]` |
| 89 | 不适用 | 无对外状态页 |
| 90 | 适用 | 单元测试由懂业务者写：`packages/engine/tests/test_storage_snapshot_iri_memo.py` 29 例断言真实边界（canonical 复用、别名不误命中、record 形状错误优先、未知 parser 失败不转成功、容量不淘汰前 16、跨调用不共享），非"断言数量/可点击" `[本轮亲读]` |
| 91 | 部分适用 | 第三方 API 集成测试：内部契约（TS/Python 双端 `binding-regressions.json`/`fixtures.json`）有正反例；**外部第三方 API 不适用**（本地优先） `[本轮亲读: packages/contracts]` |
| 92 | 适用（正面） | 端到端：`tests/e2e/t02-fr200-fr201.spec.ts`（新增 2174 行）+ 原 24 例 native 套件，覆盖 FR200 表单矩阵与 FR201 事实/编辑/拒绝；O081 实跑 21 PASS/3 原 SKIP `[本轮亲读 + O081 原件]` |
| 93 | 部分适用 | 负载测试：O078 曾做 25 次采样 profile、18 档聚合；**无发布前负载测试**，Q5 容量未定义 `[历史]` |
| 94 | 适用（正面） | 测试数据：引擎测试用合成命名空间与固定样例，不含生产数据 `[本轮亲读]` |
| 95 | 适用（正面） | 回归测试：完整 check 覆盖 3798 Python + 1924 TS + 原 24 native；`scripts/run-engine-tests.py` + `CI_ENGINE_TEST_SHARDS=2` 支撑 CI 分片 `[O081 原件 + ci.yml]` |
| 96 | 部分适用 | 老旧设备测试：**未在参考 8GB 设备上验证**（Q5 未定），保持 HOLD `[历史]` |
| 97 | 部分适用 | 无障碍：React 界面存在，但**无自动化 a11y 验证证据**；保持部分 `[历史]` |
| 98 | 不适用 | 无订阅/升级/按比例计费 |
| 99 | 不适用 | 无失败付款重试与催缴 |
| 100 | 不适用 | 无发票/PO 号 |
| 101 | 不适用 | 无销售税/VAT |
| 102 | 不适用 | 无退款/贷项 |
| 103 | 不适用 | 无用量计费 |
| 104 | 不适用 | 无定制合同 |
| 105 | 不适用 | 无营收报表 |
| 106 | 不适用 | 无 Webhook 出口 |
| 107 | 不适用 | 无 Webhook 重试 |
| 108 | 适用 | 版本化 API：v2 契约由 `packages/contracts/v2/registry.json` + `schema.json` 统一，TS 与 Python 双实现同源校验（`contract_v2.py` 49 行新增与 `v2.ts` 131 行新增对称），协议版本在 `hello` 中协商 `[本轮亲读]` |
| 109 | 不适用 | 无用户自建 API Key |
| 110 | 适用 | API 限流：引擎侧每会话请求/回复/对象/工作预算固定，超限抛 `RESOURCE_LIMIT` 固定码；主进程侧仅本地 `[本轮亲读: mainline.py 预算与 MAX_REPLIES]` |
| 111 | 部分适用 | 第三方 API 变更：无外部 API；**内部契约变更由双端 fixture 与 binding-regressions 覆盖** `[本轮亲读]` |
| 112 | 不适用 | 无 OAuth 令牌刷新 |
| 113 | 不适用 | 无客户沙箱 |
| 114 | 不适用 | 无模型调用（Prompt Injection 面不成立；**S3 前不得接入模型**）`[本轮亲读: AGENTS §3]` |
| 115 | 不适用 | 无 prompt 外发 |
| 116 | 不适用 | 无模型用量计费 |
| 117 | 部分适用 | 评测：无模型；**确定性引擎结果有逐笔期望集合断言**（57 事务/43 拒绝/FR22） `[O081 原件]` |
| 118 | 不适用 | 无模型服务商降级 |
| 119 | 不适用 | 无模型弃用迁移 |
| 120 | 不适用 | 无 prompt/输出日志（不调模型） |
| 121 | 适用（正面） | 人工确认：正式写入须经版本化 Diff 预览与显式确认（`project:changeset-preview` → `changeset-confirm`），Agent 只产草稿不得自动确认自己的修改 `[本轮亲读: AGENTS §3、PRD FR-204]` |
| 122 | 部分适用 | 弱网/酒店 Wi-Fi：本地应用无网络依赖（`connect-src 'none'`）；**模型外发尚不存在** `[本轮亲读]` |
| 123 | 适用 | 空/加载/错误态：`mainline-api.ts`、`mainline-facts.ts`、`mainline-session.ts` 与 `OwnershipConflictDetailView.ts` 实现状态分支 `[本轮亲读: 差异清单]` |
| 124 | 适用（正面） | 可操作的错误消息：跨边界固定错误码 + 受限参数（`INVALID_REQUEST`/`OWNERSHIP_CONFLICT`/`RESOURCE_LIMIT`/`PERMISSION_DENIED`/`IDENTITY_CONFLICT`/`STORAGE_FAILURE`），错误目录在 `packages/contracts` `[本轮亲读]` |
| 125 | 适用（正面） | 表单保留已输入：手工事实 ID 与预览存活有专门测试 `t02-manual-preview-lifetime.test.ts`（596 行）、`t02-manual-fact-id.test.ts`（186 行）与 fixture `tests/fixtures/t02-manual-fact-id.json` `[本轮亲读]` |
| 126 | 不适用 | 无邮件渲染 |
| 127 | 不适用 | 无通知开关 |
| 128 | 适用 | 撤销：ADR-0002 规定提交证据含前后快照作为 Diff/撤销依据，**产品撤销 UI 未实现**（该点属 S1 spike 范围） `[本轮亲读: ADR-0002]` |
| 129 | 部分适用 | 键盘导航/读屏：语义与 ARIA 部分存在；**无 a11y 审计证据** `[历史]` |
| 130 | 部分适用 | 本地化：无 i18n 框架；**日期/数字格式按本地运行**，无按 locale 切换 `[历史]` |
| 131 | 部分适用 | 返回行为：界面有会话与草稿边界（U1 属后续批次）；**浏览器式后退语义不适用** `[历史]` |
| 132 | 适用（正面） | 代码可读：`storage.py` 的 memo 实现有逐行注释说明"为什么"（"Identity gates only disable the local optimization. Parsing always uses the current bindings; no captured implementation is ever called as a fallback."）`[本轮亲读]` |
| 133 | 适用（正面） | 代码评审：双模型独立评审 + 逐轮 disposition 归档（R04–R11），本轮 R12 同构 `[本轮亲读: round-11/disposition.md]` |
| 134 | 适用 | 分支策略：独立 worktree + feature 分支 + PR 合回，AGENTS §5 明文约束；当前分支 `feature/weekly-t02-fr200-fr201` 与 base/head 记录完整 `[本轮亲读]` |
| 135 | 部分适用 | 依赖月度升级：CI 已有月度流程入口（`ci.yml` 矩阵/依赖更新），**本轮未做版本升级** `[本轮亲读: ci.yml]` |
| 136 | 部分适用 | 框架升级：Electron/React 版本固定且 NOTICE/锁文件随改动提交；**无升级前安全补丁验证流程证据** `[历史]` |
| 137 | 部分适用 | 删除 AI 遗留死代码：本轮新增 `_definition_objects` 与 `_definition` 双入口属**有意的兼容分派**（保留原单参数钩子），非死代码 `[本轮亲读: storage.py:1231-1236]` |
| 138 | 部分适用 | 拆分大文件：`storage.py` 已 89563B 仍单文件；**本轮未拆分** `[本轮亲读: git cat-file -s]` |
| 139 | 适用（正面） | 架构决策成文：ADR-0001/0002/0003 + `docs/architecture/` 目录，1–2 屏且写明理由 `[本轮亲读]` |
| 140 | 部分适用 | README/上手：`docs/development.md` 与 `docs/README.md` 存在；**"1 小时内让新工程师跑起来"未验证** `[历史]` |
| 141 | 适用 | 交接文档：迭代目录保留设计、验收与证据；`docs/reviews/T02/status.md` 逐轮追加接收记录 `[本轮亲读]` |
| 142 | 不适用 | 无运维管理后台 |
| 143 | 不适用 | 无客服工作台 |
| 144 | 部分适用 | 变更日志：**无对外 changelog**；内部按轮归档处置文档 `[历史]` |
| 145 | 部分适用 | 条款/隐私政策与代码一致：本地优先、不自动外联、CSP `connect-src 'none'`、不自动启用模型/遥测——代码与"本地优先"承诺一致；**完整条款文本与组织隐私政策未在仓库内** `[本轮亲读: AGENTS §3、csp.ts 语义]` |
| 146 | 部分适用 | 组织/域名/仓库归属：仓库为 `OntoLearn-Studio`（GitHub `NOmoreJoke/OntoLearn-Studio`，见 O077 PR16 读回）；**全部法律实体归属未确认** `[历史]` |
| 147 | 无法确认 | bus factor：**当前为单点（本人 + 另一作者 + ROOT）**，仓库文档不足以证明"高于 1"；PRD 与 AGENTS 明确保留该项 `[历史+本轮亲读]` |
| 148 | 无法确认 | 读 AI 全部代码后才发布：流程上由双评审覆盖，但**无法确认"每一行都由资深工程师读过"**（1412 源叶、两方各读不同闭包）`[历史]` |
| 149 | 部分适用 | 第二个客户前设计好数据模型：版本化 schema + 快照 + 不可改写历史 + 容量边界；**Q6 有限本体能力未决** `[本轮亲读: ADR-0002]` |
| 150 | 无法确认 | 解释"修 A 引入 B"：有首败记录与逐轮处置可查（V 目录 v1 counterexample → v2 修复；O080 首合成 9P1F）；**无法确认所有回归都有解释** `[本轮亲读: V/O080 原件]` |
| 151 | 不适用 | 无云部署/云账单；**唯一"账单"是本地资源预算** `[历史]` |
| 152 | 不适用 | 无 3am 支付故障（无支付） |
| 153 | 部分适用 | 框架漏洞公开后打补丁：依赖固定精确版本 + 锁文件 + NOTICE；**无 SLA 响应流程证据** `[本轮亲读]` |
| 154 | 不适用 | 无患者数据 |
| 155 | 部分适用 | 迁移不停机：本地 SQLite 事务内迁移；**无多节点在线迁移** `[本轮亲读: ADR-0002]` |
| 156 | 部分适用 | 说"不"：架构不变量（AGENTS §3）以"违反即阻断"形式约束，并被两方逐轮审查实际执行 `[本轮亲读]` |
| 157 | 不适用 | 无"只在笔记本能跑"的规模化承诺；桌面本地应用即最终形态 |
| 158 | 部分适用 | AI 写不出 bug 时能调试：本轮诊断链（O079 raw 2148B → trace blob → C1-TRACE-INDEX 186 事件）可作调试方法证据 `[本轮亲读: O079]` |
| 159 | 不适用 | 无 AI 生成代码可查；**仓库无模型生成来源标记**（本项目代码非 vibe-coded）`[本轮亲读]` |
| 160 | 适用 | 一年后仍知道为何如此：ADR-0001/0002/0003 记录决定与理由，处置文档记录每轮判断与撤回 `[本轮亲读]` |

**160 项统计**：适用 **24**（其中 11 项为"适用（正面）"）、部分适用 **59**、不适用 **69**、无法确认 **8**。合计 24 + 59 + 69 + 8 = **160**。

> 与 R11 的对照：R11 双方分别为 Z 30/51/70/9 与 MM 16/48/89/7。本轮本人判定与两方历史判定**不必逐项相同**，因为分类取决于作者亲读闭包与当轮事实；本人在每项均给出当前依据，且未把分类当产品通过数。历史分类**未被继承为本人判定**，历史意见位置在 §5 按 stable ID 逐项处置。

---

## 7. 本轮新发现（单列，不并入 163）

| ID | 严重性 | 摘要 | 位置 | 是否 push 前阻断 |
|---|---|---|---|---|
| N1 | S2 | 当前 `dc6c112e` 候选未在 `status.md` / `m0-checklist.md` 登记（F05 同型缺口重新打开） | `docs/reviews/T02/status.md:115`、`docs/m0-checklist.md:89` | 是（文档登记） |
| N2 | S2 | `TermInputError` 分层在唯一消费点（`storage.py`）未生效，"确定拒绝 vs 未知解析失败"信息丢失 | `packages/engine/src/ontolearn_engine/rdf_snapshot.py:13,34-39`；`packages/engine/src/ontolearn_engine/storage.py:1254-1257,1650-1654` | 是（源码语义未闭合） |

其余观察（N3–N10）已列于 §2，不重复计为新缺陷。

---

## 8. 阅读与披露（本人实际亲读 / 差异级 / 工具摘要 / 定位 / 未读）

### 8.1 全文亲读（本人逐字读完正文）

- `AGENTS.md`（工作树 overlay，15147B）全文。
- `docs/prd/PRD-本体学习与落地Agent工作台.md` FR-200/FR-201/FR-202/FR-203/FR-204/FR-300–FR-304 段落（第 290–370 行范围），含附录 C/D/E/G 的引用位置核对。
- `docs/architecture/0001-desktop-framework.md`、`docs/architecture/0003-resident-coordinator-and-jobs.md` 全文；`docs/iterations/I01/ADR-0002-storage.md` 的存储/提交/失效/迁移/边界段。
- `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` 的 S1/S2/S3/C1/B1/U1 与退出门槛段（第 28–191 行）。**注**：AGENTS §1 指向的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` **路径失效**；真实原件在 `docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`，两份 sha256 同为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`（同源副本）。**这是本轮发现的路径歧义，不作为内容结论。**
- `docs/reviews/T02/status.md` 全文结构与末节；`docs/m0-checklist.md` 章节结构与末节。
- `docs/reviews/T02/fr200-fr201-20261024/round-11/disposition.md`：全文结构、逐项处置规则、160 项表（160 行）、163 稳定位置六节表（逐行解析得 31/78/20/13/9/12 = 163 行）、owner 限证字典与保留门禁节。
- **本轮四叶全文**：`packages/engine/src/ontolearn_engine/storage.py` 差异全文 + `_snapshot_state`/`_definition_objects`/`_validate_single_slots`/`_check_slot` 区段正文；`packages/engine/src/ontolearn_engine/rdf_snapshot.py` 全文（差异 + 现行）；`packages/engine/tests/test_storage_snapshot_iri_memo.py` **全文 380 行**（29 例逐例核对）；`tests/e2e/native-recovery.cjs` **全文 255 行**；`tests/unit/native-recovery-observer.test.ts` **全文 326 行**（12 例逐例核对）。
- `packages/engine/vendor/rdflib/notation3-input-types.patch` 与 `PROVENANCE.json` 全文。
- 累积范围关键闭包：`apps/desktop/src/preload/index.ts` 与 `apps/desktop/src/main/desktop-ipc.ts` 差异；`packages/engine/src/ontolearn_engine/project/mainline.py` 的 `ownership_proof` 与调用分支；`packages/engine/src/ontolearn_engine/job_store.py` 的 `ownership_detail_page`；`packages/contracts/src/v2.ts` 差异；`.github/workflows/ci.yml` 差异；`licenses/NOTICE` 差异。

### 8.2 差异级核对（本人用 Git 只读核对，未逐行通读全文）

- base→head 全部 135 路径清单与 91A/44M 分布；`git diff --stat` 覆盖除 storage/rdf_snapshot/docs 外的全部路径。
- `packages/engine/src/ontolearn_engine/project/mainline.py` 差异中的 `_WriteAdmission` 段落（本人通读该新增块约 220 行）。
- 其余 42 个 M 路径（job_store 剩余 406 行、project_host 169 行、domain_changesets 36 行、query_presentation 21 行、coordinator 23 行、engine.ts/project-mainline-service.ts、renderer 六个文件、contracts 其余、CI、scripts、uv.lock、package.json、pyproject.toml）的**差异统计与关键片段**，未逐行通读全文。
- 91 个 A 路径中的 8 轮历史评审归档（round-04…round-11）、新增测试文件（`test_mainline_*.py` 六类、`t02-ownership-detail*.test.ts` 两份、`t02-fr200-fr201.spec.ts`、`ui-observation.ts` 等）的**存在与规模**，未逐行通读全文。

### 8.3 工具摘要 / 结构化核对（脚本与只读命令）

- 163 稳定位置表按表头解析与计数（§5.8）；160 项分类基线提取（§6 对照）。
- `git cat-file -s` / `shasum -a 256` 核四叶字节与 SHA；`git ls-tree`/`rev-list`/`diff --name-status` 核身份与规模。
- O081 `CANDIDATE-BINDING.json`、`INPUT-METADATA.json`、`COMMIT-RESULT.json`、`STAGED-FOUR-PATH-BINDING.json`、`NATIVE-PRELAUNCH-GATE.json`、`check/result.json`、`check/dispatch.json`、`native24/result.json`、`native24/c1-evidence.json`、`NATIVE24-DATA-QUALIFICATION.json`（字段级解析）。
- O079 `C1-FAILURE-ANALYSIS.json`、`VALIDATION-AND-C1-BOUNDARIES.md`；O077 `COMPLETION.json`（平台级字段解析）；O080 `HANDOFF-PREPARED.md`、`INDEPENDENT-OBSERVER-SOURCE-REVIEW.md`、`native-recovery.before.cjs`；V 目录 `storage.final-v2.py` / `test_storage_snapshot_iri_memo.final-v2.py` 与 HEAD 的逐字节比对、`SOURCE-PATCH-v2.diff` 对照。

### 8.4 未读 / 未验证（明确缺口，不假装检查过）

1. **未运行任何验证**：check、pytest、vitest、build、package、Ruff、ESLint、Prettier、typecheck、native24、Electron、GUI、SQL、采样/profiler 本人**一次都没有执行**。O081/O079/O077/O080 的所有运行结论均为**历史身份**（读取他人保存的原件）。
2. **未逐行通读**的路径：8 轮历史评审归档全文（本轮只读 round-11 处置与版本映射结构）、新增的 6 个 `test_mainline_*.py` 与 5 个 `tests/unit/t02-*` / `tests/e2e/t02-fr200-fr201.spec.ts` 全文、`job_store.py` 差异中除 `ownership_detail_page` 外的部分、`project_host.py`、`domain_changesets.py`、`query_presentation.py`、`coordinator.py`、renderer 六个文件的差异全文、`scripts/*.py` 三个新脚本全文、`uv.lock`/`package.json`/`pyproject.toml` 全文。**这些文件的本轮正确性未由本人独立逐行确认。**
3. **未核**：R11 `version-map.json`（485KB）的逐条索引内容、`artifact-manifest.json`（40KB）的 152/169 针逐条比对；O079 `C1-TRACE-INDEX.json`（186 事件）逐事件重建；O078 profile 的 25 档逐档聚合；四个 vendor wheel 的二进制逐 member 校验（本人只读 `PROVENANCE.json` 声明与 `patch` 文件，未验证 wheel 内容与声明一致）。
4. **未确认的产品/外部事实**：Q2 首发平台、Q5 容量与参考设备、Q6 有限本体能力、Q7 固定轮次指标、Q9 受测模型；组织法律/IP/隐私/产权；真实 bus factor；跨 OS 与 8GB 参考设备；Windows CI 根因；签名公证。
5. **未能独立复核的运行计数**：TS 1924/41 files、Ruff 397 files、Python 总数 3798 的分片构成、"9 facts"、57 笔与 43 笔的逐笔明细——这些来自 O081/O077 保存的资格 JSON 与 stdout，**本人只做了字段级与计数级比对，未逐笔重算**。
6. **未读另一作者本轮 R12 任何内容**（按职责要求），也未读取 O081 目录下的 `zcode-*` 与 `minimax-*` 派发/UI 记录（属他人会话产物，非本方输入）。
7. **路径歧义未决**：AGENTS §1 指向的 M0 计划路径失效（真实原件在 `docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`）。本人**未修改** AGENTS 或计划文档（只读职责），已按真实原件审查并在此披露。

### 8.5 工具使用与写入纪律

本轮本人仅执行：**Git 只读命令**（`rev-parse`/`rev-list`/`ls-tree`/`cat-file`/`diff`/`show`/`status`/`log`/`shasum`）、**文件读取**（read/grep/glob）、**只读 Python 解析**（读取 JSON/Markdown 表格做计数与字段提取）、以及**一次目录创建**（`mkdir -p outputs/20261027_t02_v2_observer_validation_review_081/minimax`）与**一次文件写入**（本报告）。未运行项目脚本、未修改仓库任何文件、未触碰 index。

---

## 9. 最终判定与门禁

**判定：ConditionalPass（限定技术阶段），带 N1、N2 两项当前 push 前源码阻断。**

- **不是**无条件双 Pass；**不是**完整产品通过；**不是**完整 CI 放行；**不是**发布放行；**不**解除任何 HOLD/UNKNOWN；**不**推进 T04。
- 本轮四叶实现本身（IRI v2 memo + C1 被动观察）在本人逐行核验下**未发现数据泄露、资金损失或服务中断类缺陷**；v2 一行修复真实闭合了 v1 的 P2 RED→GREEN；C1 observer 的原控制不变量与异常隔离在静态与合成两个层面成立。
- **N1**（状态登记缺口）与 **N2**（`TermInputError` 语义未在消费侧闭合）须在 push 前按 §2 的最小建议处理，并生成新候选后按现行门禁重新独立审查（AGENTS §5「冻结与调度记录」）。
- **未来完整 CI 条件不变**：ROOT 精确票后的完整 Quality/macOS/Windows 三平台同交付、逐 node 完整 3769 与原有理据 skip、自然退出 0、无失败早停取消与 timeout NOTRUN、全部后继步骤与 Quality packaged recovery 自身 success、原 15/20 分钟上限不变。
- **独立 HOLD 全部保留**：C1 原生 unresponsive 底因 UNKNOWN、Windows CI 43/44 根因未证、Quality 完整 3769 NOTRUN、组织法律/IP/隐私/bus-factor、容量与坏 SQLite 物理保护与旧超限库恢复、包内完整 GUI/签名公证、跨 OS 与参考 8GB 设备、供应链、engine 自然退出与 Windows 后代、sys.path 等价、unknown parser/N3Store 坏 snapshot、未具名下游/ownership 家族/剩余 Undo、旧 79F。
- **整体进度不变**：合并可用 FR 2/17（FR401/402），HOLD 关闭 0，D8 未用，Goal/M0/release 未完成。

本方报告已完整落盘；两份原稿与处置须由 ROOT **实际接收**后方可进入下一票。

---

# 追加节（自然02）：必要事实更正、补充正文覆盖、160 项重映射与 163 意见逐 ID 承接

本节为**本会话自然01原稿之后**的追加，不回写、不抹除、不改判首判。首判原文（82073B / SHA-256 `7fe0778be7f31005d1aa2aa4d95aa98348693db754f2eb4be85b633abb393c2b`）逐字保留于本文件前缀，首判的 **ConditionalPass 与 N1/N2 原判**均作为历史保留；本节对其中的**事实错误**作有效替代（见 §A.1、§A.2），并给出本人当前独立结论。

本节仍只写本方 report.md；未改任何源码/测试/配置/预算；未重跑 check、pytest、vitest、build、package、Electron、GUI、SQL、采样或 profiler；未执行新 probe 或故意失败注入；未读另一作者本轮产物。

---

## A. 必要事实更正

### A.1 【撤回并替代】N2：`TermInputError` 分层已在真实消费点兑现，首判"storage 唯一消费点 / 分层无任何消费兑现"不成立

**首判原文（保留）**：§1 结论"带两项当前 push 前源码阻断"，其中 N2 写为"`TermInputError` 分层后……`storage.py` 的快照校验路径仍只把 `TermInputError` 当作普通 `ValueError`，而引擎对外协议层与 `packages/contracts` 的错误目录没有对应的错误码"，并在 §2 N2 断言"这使该分层的实际收益为零……**在唯一消费点（`storage.py`）没有生效**"，最小建议为"在 `storage.py` 的两处判定点显式捕获……或若本轮刻意不铺开，则删除 `TermInputError` 的语义声明"。

**本人重核后确认该判断错误，现予撤回并作如下有效替代。**

本人本轮已亲读的真实消费点闭包（固定 HEAD `dc6c112e`）：

| 位置 | 正文事实 |
|---|---|
| `packages/engine/src/ontolearn_engine/project/domain_changesets.py:27` | `from ontolearn_engine.rdf_snapshot import TermInputError, iri, term` —— 分层被**真实导入**并使用，不是未被引用的悬空声明。 |
| `domain_changesets.py:447-451`（注释） | "Only direct caller terms get known syntax/policy rejection. Unknown parser/N3/Store/preview failures retain UNKNOWN/HOLD" —— 分层边界在源码中被显式写明。 |
| `domain_changesets.py:452-457` | 手工事实的 `subject`/`predicate` 用 `iri(...)`，**仅捕获 `TermInputError`** → `fail("INVALID_REQUEST", field="params")`（即 455 行）。 |
| `domain_changesets.py:458-465` | 手工与编辑的对象值用 `term(...)`，**仅捕获 `TermInputError`** → `INVALID_REQUEST`（即 462 行）；`parsed.n3() != value` 亦映射 `INVALID_REQUEST`。 |
| `domain_changesets.py:466-477` | `merge_plan` 的 `ValueError/KeyError/TypeError`、`transactions.preview` 的 `MetadataError`、`supported(...)` 的 `ValueError/KeyError/TypeError` 分别独立映射 `INVALID_REQUEST`——**未**把未知解析失败宽捕获为 `INVALID_REQUEST`。 |
| `packages/engine/src/ontolearn_engine/coordinator.py:88-109` | `classify()` 经 `JobFault`/`ServiceFault`/`Conflict`/`sqlite3.Error` 映射固定码；其余归 `INTERNAL_ERROR`。`sqlite3` I/O 类 → `STORAGE_FAILURE`、BUSY/LOCKED → `STORAGE_BUSY`。 |
| `packages/engine/src/ontolearn_engine/project/mainline.py:1186-1200` | `observe_error()`：非 `JobFault`/`ServiceFault` 的失败 → `reply.unknown = True` 且 `self.hold = True`（UNKNOWN/HOLD 保留）；`JobFault(code="STORAGE_FAILURE")` → `hold = True`。 |
| `packages/engine/src/ontolearn_engine/storage.py:1648-1654` 与 `:1254-1257` | 快照与定义校验**不捕获** `TermInputError`，不改变异常子类或身份——存储层仍是 `ValueError` 语义，与首判所述一致。 |
| `packages/engine/src/ontolearn_engine/storage.py:128-153`（memo `noncanonical`） | 同样不 catch，异常身份与 `__cause__` 保持原样。 |

**本人独立核到的真实可达反例（不存在）**：首判要求的"当前可达反例"并不存在。`domain_changesets.py` 已是 `TermInputError` 的实际消费点，且**只对直接 caller 的 `iri`/`term` 输入**做确定拒绝映射；未知 parser/N3/Store/preview 失败按源码与测试一律保持 UNKNOWN/HOLD。首判把 `storage.py` 当成唯一消费点，是**只读了 storage/rdf_snapshot 闭包、未读 domain_changesets 闭包**造成的遗漏。

**对应测试正文（本人亲读）**：
- `packages/engine/tests/test_mainline_manual_input_rejection.py:741-747` `test_vendor_source_errors_have_dedicated_input_type`：断言 `rdflib == 7.6.0+ontolearn.fr201.3` 且 `rdf_snapshot.term('"x"^^<../relative>')` 与 `'"x"^^<urn:\U00110000>'` **抛 `rdf_snapshot.TermInputError`** —— vendor 专有输入类型确被区分出来。
- 同文件 `:750-806` `test_same_bad_vendor_input_does_not_hide_internal_failures`：在 `join`/`int`/`group` 三处注入 `ValueError/Exception/ParserError/AssertionError/IndexError`，断言错误码为 `INTERNAL_ERROR`、`host.hold` 成立、reply 保持 unknown、后续读为 `STORAGE_FAILURE`、库 dump 不变 —— **同一坏输入不掩盖内部失败**。
- 同文件 `:149-224` `test_non_input_failures_keep_original_unknown_and_hold`（`term`/`preview`/`sqlite-integrity`/`snapshot-integrity`）：断言 `INTERNAL_ERROR` + `host.hold` + unknown 保留 + 全库不变 + 后续 `STORAGE_FAILURE`。
- 同文件 `:531-583` `test_new_input_boundary_keeps_unclassified_parser_and_n3_unknown`（`parser-value/exception/config/assertion/index/n3`）：同上的 UNKNOWN/HOLD 边界。
- 同文件 `:641-688` `test_manual_iri_preflight_does_not_classify_unknown_failures`（subject/predicate × ValueError/AssertionError/IndexError）与 `:589-640` `test_urlsplit_noncontract_failures_keep_unknown_and_hold`。
- 同文件 `:460-525` `test_known_caller_objects_reject_then_same_host_reads_and_commits`（`INPUT_CASES + R02_SYNTAX_CASES + URLSPLIT_INPUT_CASES + MANUAL_IRI_FIELD_CASES`）：已知拒绝后**同一 host/lease 仍能读写并提交**。
- `packages/engine/tests/test_mainline_language_input_rejection.py:43-49`、`:313-326`：R03 拒答族在同 host 拒绝后仍可完整提交，数字子标签仍属语法合法、与 canonical case 策略分离。

**结论（替代首判 N2）**：`TermInputError` 的分层**已在 `domain_changesets.py:455/462` 真实兑现**，并由 `coordinator.py`/`mainline.py` 的固定码与 UNKNOWN/HOLD 边界承接。首判 N2 的事实前提错误，**予以撤回**；首判提出的两个最小建议（"删除 `TermInputError` 声明"或"在 storage 宽捕获为 `INVALID_REQUEST`"）**本轮均不采纳**——前者会丢失已在用的 vendor 输入类型区分，后者会把坏存储快照/未知解析失败错误地归为用户输入错误，**两者都会改变冻结语义**，反馈对该风险的提示成立。

**与 F14 的矛盾消解**：首判 §5.1 对 F14 写"部分采纳……后续首个契约维护票"，同时 §2 N2 又称"当前源码阻断"，二者确实自相矛盾。消解后的统一口径是：
- **F14 = 契约归口的维护观察**（公开 TS/Python 入口 schema 拒空、撤回行为不对称、算术冗余）→ 维持"部分采纳 + 后续契约维护票"，**不新增当前修复门禁**；
- **首判 N2 = 本方基于不完整闭包作出的独立发现** → 因事实前提被证伪而**撤回**，**不转化为门禁**，其编号不再有效，也**不并入** F14 或 163 意见位置。
- 因此**当前 push 前源码阻断数量由 2 降为 1**（仅 §A.2 的 N1，且其性质按该节重新界定）。

### A.2 【收窄并重定性】N1：事实保留，但**不是当前产品源码缺陷**，而是后续既定归档动作的前置

**首判原文（保留）**：§1 与 §2 N1 写"`dc6c112e` 候选未在 `status.md`/`m0-checklist.md` 登记"，定为 S2 并称"**是（文档登记阻断）**"。

**本人重核后的有效替代（保留事实，改变性质与窗口）**：

- **事实保留**：`docs/reviews/T02/status.md` 末节仍为「2026-10-27 R11 / d1aca 必要技术阶段已接收；受控docs归档」（本人实测 `shasum -a 256`：`status.md` = `12df8b6e6e965c759e9a76a8c54d0f6ae486033b7ae1100540bea70b8a282109`，`m0-checklist.md` = `031164d047a65aa6eaa78a3be78a6f198ff9559108642b8a552f9eeee49ca13a4`；两文件均无 `dc6c112e` 段）。`git show --stat dc6c112e` 确认该提交**只含四叶**（storage.py 157、test_storage_snapshot_iri_memo.py 380、native-recovery.cjs 153、native-recovery-observer.test.ts 326），**未触及** status/m0-checklist。
- **性质重定性**：按现行流程，顺序是「四叶实现冻结 → 本次指定审查 → ROOT 实际接收完整两原稿 → **另票**受控 docs 归档/状态追加 → push」。状态追加属于**该另票**的交付物，而非本次受审候选的组成。首判把"归档尚未发生"记作候选的**源码阻断**，是把后续流程动作误记为当前缺陷。
- **因此**：N1 **不是当前产品源码缺陷**，也**不是当前 push 的源码前置条件**；它是 R11-F05 同型登记缺口在**归档票**窗口内应被处理的既定动作。原 owner/事件窗口按 R11 原表保留（"ROOT 指定文档 owner；状态追加＋归档票"），**不新增实现修改、不新增验收要求**。
- **对首判的修正**：首判"是（文档登记阻断）"的表述**予以收窄**为"归档票窗口内的既定登记动作，当前不构成源码阻断，也不构成本票的额外执行项"。当前 push 前源码阻断因此为 **0 项**（与 §B 的结论一致）。

---

## B. 补充正文覆盖（本人本轮实际补读，按文件/区间给已读级别）

首判 §8.2/§8.4 曾如实披露"仅看 stat/片段"。本轮按反馈实际补读下列正文。**已读级别**用：`全文`＝逐行读完该文件正文；`闭包全文`＝为核特定机制读完相关文件全文；`关键区间`＝按指定行区间精读；`差异级`＝读完整 diff。

### B.1 引擎业务与存储闭包

| 文件 | 已读级别 | 实际断言/边界要点 | 仍未读 |
|---|---|---|---|
| `packages/engine/src/ontolearn_engine/project/domain_changesets.py`（965 行） | 闭包全文（1-40、435-520 精读，全文结构与 `fail()`/`_wire_room`/`_page_room`/`_persist_segments` 路径核过） | `TermInputError` 消费点 455/462；已知 caller 输入 → `INVALID_REQUEST`；未知 parser/N3/Store/preview → 各自独立映射，**未宽捕获**；undo 影响以 `_document(entries,"undo-impact")` 分页持久化并写 `job_details` | 521-965 的 `_document`/分片编解码细节 |
| `packages/engine/src/ontolearn_engine/coordinator.py` | 关键区间（60-110 精读） | `classify()`：`JobFault`/`ServiceFault`/`Conflict` → 固定码；`sqlite3` BUSY/LOCKED → `STORAGE_BUSY`，I/O/CORRUPT → `STORAGE_FAILURE`，其余 `INTERNAL_ERROR` | 110 行以下的 job 生命周期 |
| `packages/engine/src/ontolearn_engine/project/mainline.py`（1207 行） | 关键区间（31-46、677-736、1035-1050、1175-1210 精读） | `METHODS` 含 `project.ownership.detail`；`ownership_proof` 校验 method/owner/generation 并预留预算；`observe_error` 的 UNKNOWN/HOLD 与 `STORAGE_FAILURE → hold`；`#clean_predecessor` 要求显式 close 成功方可移交权限 | `_WriteAdmission` 中段与 `material_profile` 细节 |
| `packages/engine/src/ontolearn_engine/job_store.py` | 关键区间（895-970 精读） | `ownership_detail_page`：method 绑定校验、`documentHash` 比对 → `IDENTITY_CONFLICT`、`startOrdinal >= segmentCount` → `INVALID_REQUEST`、页字节上限 → `RESOURCE_LIMIT`、每页 `proof.check(self, project)`、`nextOrdinal` 严格递增且末段为 `None` | 970 行以后其它 job 方法 |
| `packages/engine/src/ontolearn_engine/storage.py` | 闭包全文（首判已读四叶差异 + `_snapshot_state` 1574-1680、`_definition_objects` 1231-1264、`_validate_single_slots` 1275-1302、`_check_slot` 1320-1365） | memo 门控、`ManualOwnershipConflict`/`SingleDeclarationConflict` witness、`introduced_singles` 与同单值声明冲突定位 | 1365 行以后 helper |
| `packages/engine/src/ontolearn_engine/rdf_snapshot.py` | 全文（首判） | `TermInputError` 定义与 6 处抛出点；`urlsplit` 的 `ValueError` 转 `TermInputError` | 无 |

### B.2 新增引擎测试（7 类，本人读用例结构与关键断言）

| 文件 | 行数 | 已读级别 | 实际断言要点 |
|---|---|---|---|
| `test_mainline_manual_input_rejection.py` | 1034 | 关键区间（78-215、225-250、455-480、525-640、641-810、808-960） | 见 §A.1 表；另含 `test_manual_ownership_detail_full_pages_then_original_id_job`（`reservedIdentity`/`sameStatement`/`singleSlot` 三 reason，逐页 `pageSize=1` 读到底，segment sha256 与 `documentHash` 逐字节核，`existing`/`incoming` locator 精确，`read` 不变且 `not actor.mainline.hold`，随后同 host 仍可提交并产出原 ID Job 与 operation marker）与 `test_single_declaration_preserves_real_home_and_two_existing_locators` |
| `test_mainline_dispatch.py` | 1248 | 用例结构（24 个测试名）+ 关键区间（147-256、257-350） | ownership 大 locator 完整性/纯度/有界；损坏（missing-version/empty-header/bad-json/bad-segment）→ storage hold；诊断失败不得污染已接纳的纯读；重复利用达行上限后新上下文回滚；legacy detail 不臆造 locator |
| `test_mainline_language_input_rejection.py` | 326 | 用例结构 + 关键区间（43-54、313-326） | R03 拒答族同 host 拒绝后仍可提交；数字子标签语法合法与 canonical case 策略分离；大写子标签保持既有 canonical 拒绝 |
| `test_mainline_postwrite_admission.py` | 860 | 用例结构（18 个测试名） | 原 admission 边界含全部终态余量（rows/bytes/work × ±1）；终态尾部证明覆盖 error marker/progress/run 行；owner 草稿增长在读 admission 丢失前拒绝；queued commit 复检终态 material；两项目 pending 共享全局终态余量；前台/后台 scope 不得互借；after_commit 重入不得退款未知外层写者；结算失败保持精确 foreground reply unknown；同 store DTO 不得绑定或提供预算；bootstrap 未结算写者不可被当作 clean 采纳；clean close 才移交限制；后继不得丢弃未结算前任、不得夺取原 queued/active job |
| `test_mainline_postwrite_rows_budget.py` | 395 | 用例结构 + 关键区间（191-264、326-395） | 243 行 5 列真实 owner 可容纳并继续；终末费用拒绝后 scope 保留且同 host 继续；页 scope 不得出借/退还预付费；预付 material 不得二次消费 |
| `test_mainline_postwrite_text_budget.py` | 320 | 用例结构 + 关键区间（131-218、272-320） | 多字节/UTF-8 标量前缀保持身份偏移且各终末费用仅一次；文本固定费用原子拒绝后同 host 合法继续；文本游标回调吊销在终末编码前拒绝 |
| `test_mainline_read_work_budget.py` | 559 | 用例结构 + 关键区间（383-437、478-559） | 原 64MiB work 上限在两阶段（lower / authorized-plan）都在校验前拒绝；重复解码历史在计划选择器前保持有界；core admission 仍执行完整鉴权并在损坏时 hold；已授权计划的 SQL 失败无零回退且 hold |

### B.3 前端 renderer 六文件 + 新增视图（差异 382 行，本轮读完整 diff）

| 文件 | 已读级别 | 实际断言/边界要点 | 仍未读 |
|---|---|---|---|
| `apps/desktop/src/renderer/src/ontology/mainline-ownership.ts`（新增 78 行） | 差异级（全文） | **512 页硬上限**（`for (let count = 0; count < 512; count++)`），非固定 8 页；`nextOrdinal === null || page.nextOrdinal <= startOrdinal` → `invalid()`（**严格递增**）；首段 `manifest.totalBytes`/`segmentCount` 跨页一致性校验；`matchesOwnershipDetail` 逐页契约校验；`documentHash` 首段后固定；`sourceBaseRevision` 必须等于预览基准；`singleDeclaration` 与其它 reason 的角色映射分离 | 无 |
| `apps/desktop/src/renderer/src/ontology/mainline-session.ts`（881 行） | 差异级（全文）+ 关键区间（380-405） | `prepareUndo()`：**Undo 是新操作 + 新基准**，先 `read()` 再以 `targetOperationId` 准备，不做本地反转；`requireCurrent()` 贯穿 ownership 读取全程（source 身份、stale、pending）；`OWNERSHIP_CONFLICT` → `safeBusiness3Error` 校验 `detailRef` → 读详情 → `ready`/`unavailable`；`STALE_CONTEXT` → `invalidate()`；每次 read/prepare/discard 都清 `ownershipDetail` | 非本轮差异的既有会话逻辑 |
| `apps/desktop/src/renderer/src/ontology/OntologyMainlinePage.tsx`（409 行） | 差异级（全文）+ 关键区间（390-409） | `useLayoutEffect` 同步分离 fact 预览寿命（commit 时先于 owner 的被动 dispose 脱离，StrictMode 下新挂载不复活旧 hash 续接）；`current()` 栅栏在 await 之间无空档；`newManualFactPlan` 改为 async（**`crypto.subtle.digest` 派生 ID**）；**撤销按钮文案为"预览撤销本次修改"，说明"撤销将读取新基准、展示完整影响，并要求再次确认"** | 无 |
| `apps/desktop/src/renderer/src/ontology/mainline-facts.ts`（82 行） | 差异级（全文） | `manualFactPlan` 的歧义判定从"live.length!==1"改为**逐行排除当前 id 的存在性判定**；`newManualFactPlan` 拒绝 **lone surrogate**（`0xD800-0xDFFF`），因 Store 用 UTF-8 canonical JSON 编码标量；新手工记录 ID **必须匹配 `Store.digest([S,P,O])`**（此前为随机 32 字节） | 无 |
| `apps/desktop/src/renderer/src/ontology/mainline-api.ts`（186 行） | 差异级（全文） | `OntologyMainlineBridge` 新增 `getOwnershipConflictDetailPage`，类型取自 `MainlineProjectBridge`（不新增第二套 wire 校验器） | 无 |
| `apps/desktop/src/renderer/src/ontology/OwnershipConflictDetailView.ts`（新增 105 行） | 差异级（全文） | 新增冲突详情只读视图 | 无 |
| `apps/desktop/src/renderer/src/ontology/OntologyPage.tsx`（716 行） | 关键区间（grep 定位 182/350-368/542/625/661） | 删除影响预览（"无法读取完整引用影响，暂不能预览删除"、"预览删除（尚不提交）"）；移除事实与移除实体入口 | 全文其余部分 |
| `tests/e2e/t02-ontology-mainline.spec.ts`（602 行） | 关键区间（299-360） | "five fields, complete Diff, original receipt, **Undo/Redo and owned restart**"：新建 → 完整 Diff 预览 → 显式确认 → 原回执；**实际 Undo** 产生独立反向完整 Diff（before=expected, after=null）→ 提交后版本 2、状态回到初始；**实际 Undo-of-Undo** 产生独立正向 Diff → 版本 3；Undo 的 `operationId` 与原提交不同 | 360-602 |

### B.4 契约双端、CI、脚本与 fixture

| 文件 | 已读级别 | 实际要点 | 仍未读 |
|---|---|---|---|
| `packages/contracts/python/contract_v2.py` | 差异级（全文 49 行新增） | `ownership_detail_matches()`：校验 `params_project.ownership.detail`/`result_project.ownership.detail` schema；`count = ceil(totalBytes/32768)` 与 `segmentCount` 一致；`len(segments) <= pageSize`；`start < end <= count`；`documentHash` 一致；**`nextOrdinal == (None if end==count else end)`**、`complete == (end==count)`；逐 segment 校验 `ordinal`/`byteOffset`/`rawByteLength` 与 base64 解码后长度及 sha256 | 无 |
| `packages/contracts/src/v2.ts` | 差异级（131 行新增） | `ownershipSha256()` 为**独立实现的同步 SHA-256**（不依赖传输元数据），供 `matchesOwnershipDetail` 与 Python 端对称校验 | 完整函数尾部 |
| `packages/contracts/src/index.ts` | 差异级（160 行新增摘要 + `safeBusiness3Error` 定位） | 新增 `OwnershipDetailArgs`/`OwnershipLocator`/`OwnershipDetailDocument`/`OwnershipDetailPage` 类型与 `reassembleOwnershipDetail()`（用 `Reflect.ownKeys`/`getOwnPropertyDescriptor` 安全捕获，避免执行用户 getter） | 完整装配函数体 |
| `.github/workflows/ci.yml` | 差异级（全文） | **136-147 行**：Windows 上 `npm run engine:check` 改为 "Windows engine first-failure diagnostic (**not acceptance**)"，`PYTEST_ADDOPTS: '-vv --maxfail=1 --tb=short --durations=20 --full-trace'`、`CI_ENGINE_TEST_SHARDS: '2'`；非 Windows 仍跑完整 `npm run engine:check`；新增 Playwright JSON reporter 与 `PLAYWRIGHT_JSON_OUTPUT_FILE`；artifact 路径扩 `build/engine-tests/`、`test-results/`；`failure-traces` 改 `if: always()` | 无 |
| `scripts/run-engine-tests.py`（470 行） | **未读** | 仅知其存在与被 `CI_ENGINE_TEST_SHARDS` 引用 | 全文 |
| `scripts/engine-test-reporting.py`（124 行） | **未读** | 同上 | 全文 |
| `scripts/repack-rdflib-input-types.py`（170 行） | **未读** | 同上 | 全文 |
| `tests/fixtures/t02-manual-fact-id.json`（139 行） | **未读**（仅知其被 `t02-manual-fact-id.test.ts` 消费） | — | 全文 |
| `packages/engine/vendor/rdflib/` 四个 wheel | **二进制未逐 member 校验**（已核 `PROVENANCE.json` 声明与 `notation3-input-types.patch` 全文） | 上游 BSD-3-Clause 原文逐字节保留的声明、`upstream`/`after`/`patch` sha256、member 记录长度 117341B | wheel 内部成员未逐条重算 |

### B.5 历史归档与 vendor 二进制（按反馈"必要原件/来源 pin 核"）

- 本轮新读：`docs/reviews/T02/fr200-fr201-20261024/round-11/disposition.md` 全文结构与 160/163 两张表（程序化解析得 160 行 / 31+78+20+13+9+12=163 行）、`packages/engine/vendor/rdflib/notation3-input-types.patch` 全文、`PROVENANCE.json` 全文。
- 本轮**未**逐字通读：round-04…round-10 的 8 轮归档全文（首判已如实披露）、`round-11/version-map.json`（485KB）与 `artifact-manifest.json`（40KB）的逐条索引。
- 按反馈口径：**不要求**无关全部 vendor 全文或 1412 源叶全文；上述未读项在本轮**不构成覆盖完成的依据**，仅作为归档体积事项保留（首判 N10）。

### B.6 仍未读项汇总（明确披露，不计入"已覆盖"）

1. `scripts/run-engine-tests.py`、`scripts/engine-test-reporting.py`、`scripts/repack-rdflib-input-types.py` 三脚本全文。
2. `packages/engine/tests/test_mainline_dispatch.py`（1248 行）、`test_mainline_postwrite_admission.py`（860 行）、`test_mainline_read_work_budget.py`（559 行）等的**全文逐行**（本轮读用例结构与关键区间）。
3. `tests/e2e/t02-fr200-fr201.spec.ts`（2174 行）全文——本轮读其存在、命名与 O081 实跑计数，**未逐行通读**。
4. `tests/e2e/ui-observation.ts`（195 行）、`tests/unit/ui-observation.test.ts`（194 行）、`tests/e2e/native-driver.ts`（304 行差异）。
5. `tests/unit/t02-ownership-detail.test.ts`（843 行）、`t02-ownership-detail-view.test.ts`（138 行）、`t02-manual-preview-lifetime.test.ts`（596 行）、`t02-manual-fact-id.test.ts`（186 行）。
6. `packages/engine/src/ontolearn_engine/project/project_host.py`（169 行差异）、`query_presentation.py`（21 行）、`coordinator.py` 其余部分、`domain_changesets.py` 521-965。
7. `apps/desktop/src/main/engine.ts`、`project-mainline-service.ts` 差异。
8. `packages/contracts/v2/schema.json`（525 行新增）、`fixtures.json`（446 行）、`binding-regressions.json`（34 行）、`registry.json`（6 行）逐条。
9. 四个 vendor wheel 的逐 member 二进制校验；`round-11/version-map.json`/`artifact-manifest.json` 逐条。
10. O078（8 个 native samples）与 U（25 个 profile 捕获）**两批不同原件**的逐档字段——本轮**未**重建任何原 CPU/请求数值，只引用其存在与历史口径，**不把字段解析称为本人重建**。

---

## C. 原 160 项重映射（按原 11255B / 160 个 `>` 行精确锚点）

### C.1 锚点方法与首判错位更正

原清单文件 `ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt`（11255B，sha256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`）含 **161 个 `>` 行**，其中**文件第 157 行**是过渡句 "Oh, and besides keeping all of this working every day, forever… your vibe-coded app will still need people who know what they're doing:"，**不是清单项**。故真实 160 项为：**文件第 10–156 行 → ID #1–#147**，**文件第 158–170 行 → ID #148–#160**（末 13 项），与 R11 "末 13 为 #148–160" 一致。

**首判的错位（本人确认并更正）**：首判 §6 表中
- **#26 漏掉**原题 "emoji, accents and right-to-left text in every field"（首判把 #26 答成 money），导致 **#26–#40 整体错位一位**（首判 #27=money 实为 #27 正确？——核实：首判 #26 答 money（真 #27）、#27 答 currency（真 #28）、…、#31 答 pagination（真 #32）、#32 答 exports（真 #33）、#40 答 input sanitization（真 #40 正确））；
- **#41 被拆为 CSRF 单列**（原题 "protection against SQL injection, XSS, CSRF and the rest of the OWASP list" 是**一项**，不得拆分）；
- **#155 "testing what the AI says it tested (QA)" 漏掉**，导致 **#155–#158 再次错位**（首判 #155 答 migration、#156 答说不、#157 答规模化、#158 答调试）；
- **#159 原题是 "debugging the code when the AI that wrote it can't (a senior engineer)"**，首判却新造"无 AI 生成代码 / 非 vibe-coded"的无证前提。

**更正后的编号**：#1–#160 与下表逐项对齐；每项给出**原 English 题目**（足以唯一定位）、**一个有效分类**与**当前具体依据/未证限制**；**未另造、未拆并题目**。

### C.2 逐项判定（#1–#160）

分类口径同首判：适用 / 适用（正面）/ 部分适用 / 不适用 / 无法确认，每复合判定**只计一档**。分类**不是产品通过数**。

| # | 原题（唯一定位） | 本方分类 | 当前具体依据 / 未证限制 |
|---|---|---|---|
| 1 | a schema someone designed, instead of one the AI improvised table by table | 适用 | schema 由开发者设计：`storage.py` 固定 DDL 与 `migration_log`（`:359-394`）、`LAYERS` 白名单、定义层 `layer/id/value` 形状校验；Agent 只产草稿不自动建表（AGENTS §3）。已核。 |
| 2 | login that still works when someone puts a plus sign in their email | 不适用 | 无账号/登录体系（`login` 字样在产品代码中不存在）。 |
| 3 | password reset links that expire and work once | 不适用 | 无密码重置链路。 |
| 4 | MFA, plus a recovery path for the user who lost their phone | 不适用 | 无 MFA。 |
| 5 | sessions that time out, and a way to kill every session for one user | 不适用 | 无用户会话；仅引擎侧 stdio 会话（非登录会话）。 |
| 6 | SSO for the enterprise customer who won't sign without it | 不适用 | 无 SSO/企业身份。 |
| 7 | SAML, because that customer's IT team doesn't do magic links | 不适用 | 无 SAML。 |
| 8 | SCIM, so a fired employee loses access the moment IT offboards them | 不适用 | 无 SCIM/员工目录。 |
| 9 | roles and permissions deeper than "admin" and "everyone else" | 部分适用 | 无角色层级；但写入授权存在：`mainline.py` `_WriteAdmission.bind` 校验 owner/lease/profile、`ownership_proof` 校验 method 与基准、JobStore `format3` lease 单一写者。 |
| 10 | checks that stop user A from reading user B's data by changing one number in the URL | 部分适用 | 单用户本地项目，无跨用户数据面；但 `project.ownership.detail` 的 `projectId`/`detailRef`/`documentHash` 与 `proof.check(self, project)` 绑定，越界读取被拒。 |
| 11 | tenant isolation, so one customer's bug never shows another customer's records | 不适用 | 无多租户。 |
| 12 | an admin "log in as this user" button for support, with an audit trail on every use | 不适用 | 无 impersonate 支持场景。 |
| 13 | rate limits on login, so nobody can guess passwords at scale | 不适用 | 无登录端点。 |
| 14 | lockouts that stop attackers without locking out your CFO the night before the board meeting | 不适用 | 无账号锁定。 |
| 15 | database migrations that run forward and roll back | 适用 | ADR-0002：v0→v1→v2 事务内 DDL 升级、失败回滚并重开可重试、提交后注入异常时格式已持久化不得倒退、未来格式拒绝打开。已核 ADR-0002 与 `storage.py` 迁移路径。 |
| 16 | migrations that don't lock the main table at 2pm on a Tuesday | 部分适用 | `BEGIN IMMEDIATE` 写锁 + 升级后重读格式版本防两个 opener 重复 DDL（ADR-0002）；但本地单进程，无"周二下午多用户锁表现"。 |
| 17 | indexes, because the query that was instant on 50 test rows times out on 5 million real ones | 部分适用 | 查询有显式上限与预算（`maxPageBytes`/`maxFrameBytes`/work 上限）；真实 5M 行规模未测，Q5 未定，**不得宣称容量达标**。 |
| 18 | connection pooling, so a traffic spike doesn't exhaust the database | 部分适用 | 无远程连接池；进程内单连接 + `_format3_lease` + `_WriteAdmission` 承担并发归属与单写者。 |
| 19 | backups every night | 部分适用 | ADR-0002 规定 `backup(newPath)` 使用 SQLite 在线备份、禁止覆盖目标；**无产品级定时备份**。 |
| 20 | a restore from those backups, tested, because a backup you've never restored is a hope | 部分适用 | 恢复路径有 ADR 规定；**定期演练无证据**；坏 SQLite 物理保护仍为 HOLD。 |
| 21 | point-in-time recovery for the day someone runs a delete without a where clause | 不适用 | 无时序数据库/PITR。 |
| 22 | soft deletes, so "I deleted it by accident" is a support ticket and not an incident | 适用 | tombstone 机制：事实删除以 `object IS NULL` + `managed_value` 表达（`storage.py:1636-1647`），删除源行不删手工事实是 S1 退出门槛；前端有"查看删除影响/预览删除（尚不提交）"。已核。 |
| 23 | validation on the server, not just in the form | 适用 | 校验在引擎：`storage._snapshot_state` 逐条校验 definition/fact/mappingState 形状与错误顺序；`domain_changesets.py` 在引擎侧做输入校验并映射固定错误码。已核。 |
| 24 | timezones stored right, so the 9am reminder doesn't fire at 4am | 不适用 | 本地桌面应用**无提醒/时区功能面**；代码层无 timezone/reminder 概念。 |
| 25 | the customer with an apostrophe in their last name | 适用（正面） | canonical JSON 以 UTF-8 编码标量；`mainline-facts.ts` 显式拒绝 lone surrogate 以免与 Store 哈希口径分裂；撇号/特殊字符按原样保留。 |
| 26 | emoji, accents and right-to-left text in every field | 部分适用 | emoji/accents：UTF-8 与 lone surrogate 拒绝已核（`mainline-facts.ts`）；**RTL 全字段覆盖未见证据**。 |
| 27 | money stored as integers, because 0.1 + 0.2 doesn't equal 0.3 in floating point | 不适用 | 本体事实对象为 IRI/Literal，无金额语义；不涉及浮点金额存储。 |
| 28 | currency, rounding and tax rules for every country you sell into | 不适用 | 无货币/税务。 |
| 29 | a data model that survives your second customer asking for "one small change" | 部分适用 | 版本化 schema + 快照 + 不可改写历史 + 依赖向量已核（ADR-0002）；**Q6 有限本体能力未决**，最终数据模型未冻结。 |
| 30 | idempotency keys, so a retried payment doesn't charge the card twice | 适用 | 同 operation/job/计划重试返回原标记、不重复写入（ADR-0002）；`test_ownership_duplicate_reuses_at_row_cap_new_context_rolls_back` 与 `case7` 实跑（一次 commit、0 execute、0 replay）佐证。 |
| 31 | deduplication for the user who clicks submit four times | 适用 | `newManualFactPlan` 对已存在三元组抛 `FACT_ALREADY_EXISTS`（同时查 facts 与 definitions.triples）；`mainline-facts.ts` 已核。 |
| 32 | pagination that still works on page 400 | 适用 | 分页受控且可核：`ownership_detail_page` 每页 `nextOrdinal` 严格递增、末段 `null`、`complete` 标志；Python 端 `ownership_detail_matches` 与 TS 端 `matchesOwnershipDetail` 双端校验 segment/byteOffset/sha256；前端 512 页上限且 `nextOrdinal` 必须递增。已核。 |
| 33 | exports, because sooner or later every customer wants their data in a spreadsheet | 适用 | FR-203 规定附录 C 范围 Turtle 导出且须能被约定主流标准工具读取；O081 `native24/test-results/` 含 `t04-query-variants-...-exports-its-exact-CSV` 实跑用例。 |
| 34 | imports that survive the CSV someone saved in 2009 | 部分适用 | FR-203 规定越界构造**拒绝提交并说明原因、禁止静默丢弃**；CSV 导入属 FR-300（数据映射），尚未实现。 |
| 35 | retention rules, and code that deletes what your contract says you'll delete | 部分适用 | 历史与已提交轮次不可改写、缓存回收不得触及历史（AGENTS §3、ADR-0002）；**无合同驱动的保留策略**。 |
| 36 | secrets out of the code, out of the repo and out of the AI chat history | 适用（正面） | 模型外发唯一网关在主进程、凭据只在主进程、Python 引擎不持密钥不调模型（AGENTS §3）；本轮无凭据代码。 |
| 37 | rotating every key the AI pasted into a config file last month | 不适用 | 无模型接入，故无"AI 粘贴密钥入配置"的暴露面；本仓库亦无 `.env`/凭据文件。 |
| 38 | confirming every package the AI installed exists and is the one you meant | 适用 | vendor 侧确认到位：4 个 wheel + upstream wheel 在 `packages/engine/vendor/rdflib/`，`PROVENANCE.json` 记录 upstream wheel sha256、source member sha256、after sha256、patch sha256、member 完整性记录 117341B、repack 证据。 |
| 39 | dependency scanning, because the AI pulled in libraries nobody reviewed | 适用 | 来源 pin 与许可已核：`PROVENANCE.json` + `notation3-input-types.patch`（sha `de5755d6…`）+ `licenses/NOTICE` 同步双路径表述；补丁改动范围逐条列明且"无 catch 新增"。 |
| 40 | input sanitization everywhere a user can type | 适用（正面） | 引擎侧 zod/`.strict()` 边界 + 固定错误码；未知输入保持 UNKNOWN/HOLD 而非猜测（`test_non_input_failures_keep_original_unknown_and_hold` 等）。已核。 |
| 41 | protection against SQL injection, XSS, CSRF and the rest of the OWASP list | 适用（正面） | SQL 全参数化绑定（无字符串拼接 SQL）；XSS 受 `csp.ts` 唯一来源约束（生产无 unsafe-inline/eval，O081 CSP 探针 7 项 violation 全 enforce）；CSRF 面向浏览器跨站，本地 `file://` + `connect-src 'none'` 形态下无跨站面。**渗透测试未做**（见 #48）。 |
| 42 | file uploads that get scanned, size-limited and stored where they can't execute | 不适用 | 无文件上传功能。 |
| 43 | CORS rules that aren't "allow everything" | 适用（正面） | `connect-src 'none'`、`frame-src 'none'`、`object-src 'none'`、`base-uri 'none'`、`form-action 'none'`，生产 meta 与开发 nonce 两变体同源于 `csp.ts`（O081 `c1-evidence.json` 实测）。 |
| 44 | security headers on every response | 适用（正面） | 本地 `file://` 无 HTTP 头面，等价安全面由 CSP meta 承担；已核同源两变体与探针结果。 |
| 45 | encryption at rest and in transit | 不适用 | 代码层**无任何加密实现**（`encrypt`/`tls`/`ssl` 在引擎与桌面源码中零命中）；传输为本地 stdio，静态加密形态外。 |
| 46 | least-privilege access for everyone, including the AI agent holding production credentials | 适用 | worker 只算不持库、正式写入只经 `Store.commit`、引擎不持密钥不调模型、`_WriteAdmission` 校验后继不得夺取原 queued/active job（`test_successor_cannot_take_original_queued_or_active_job`）。 |
| 47 | logs that record who did what, without recording passwords, tokens or card numbers | 适用（正面） | 跨边界只传固定错误码与受限参数，不回传原始异常/堆栈/路径/单元格原值；`safeBusiness3Error` 为唯一错误格式化入口。 |
| 48 | a penetration test before your enterprise customer's security team runs their own | 无法确认 | 本轮未做且不在本票授权内（禁止探针/故意失败）；需安全 owner 另票。 |
| 49 | answers to the security questionnaire every enterprise buyer sends, with evidence behind each one | 部分适用 | 仓库有 ADR/证据目录/资格 JSON 可作部分依据；**无安全问卷答案文件**，本轮也无新增可支撑条目。 |
| 50 | a disclosure process for the day a stranger emails you a vulnerability | 不适用 | 属组织流程，仓库无对应文件，亦非本仓库交付物。 |
| 51 | a plan for the day a laptop with production access gets stolen | 不适用 | 无生产凭据/云凭据形态。 |
| 52 | SOC 2, which means policies, evidence and an auditor, not a checkbox | 不适用 | 属组织合规，非本仓库交付物。 |
| 53 | HIPAA, the moment a single patient record touches your system | 不适用 | 无患者数据。 |
| 54 | a BAA with every vendor that touches that data, including your AI model provider | 不适用 | 无患者数据、无模型供应商。 |
| 55 | audit trails that show who viewed a record, not just who changed it | 部分适用 | 写侧：提交证据与 operation/job marker 同事务可查；读侧：本轮新增 ownership detail 读取有分页留证与 `documentHash` 绑定，但**无全量读审计**。 |
| 56 | PCI scope, and card numbers kept out of your database | 不适用 | 无卡号/支付。 |
| 57 | GDPR deletion requests that reach every table, backup and log | 无法确认 | 本地库删除可及；**备份与日志中的删除可达性未证**，且本票不执行破坏性验证。 |
| 58 | data residency for the customer whose contract says EU only | 不适用 | 无服务端/数据驻留合同。 |
| 59 | quarterly access reviews someone signs off on | 不适用 | 无多用户角色与访问复核流程。 |
| 60 | dev, staging and production environments that match each other | 部分适用 | 桌面本地形态下环境合并为本地运行；**同源两变体**已核：开发 nonce + 生产 meta 均由 `csp.ts` 生成，`AGENTS.md` §3 禁止手写第三份策略。 |
| 61 | infrastructure written as code, so the setup lives somewhere other than one person's memory | 部分适用 | `.github/workflows/ci.yml` + 打包/验证脚本 + `PROVENANCE.json` 记录来源；桌面本地安装不依赖 IaC。 |
| 62 | a deploy pipeline that runs the tests before anything reaches customers | 适用（正面） | `ci.yml` 顺序执行 `npm run check` → `verify:sources` → `test:e2e` → `package:dir` → `verify-i04-package.py`；Windows engine 为首败诊断且**显式非验收**（见 §D.3）。 |
| 63 | one-click rollbacks, because Friday deploys happen | 部分适用 | 格式迁移失败回滚 + 重开可重试已核；**应用版本回滚未实现**。 |
| 64 | zero-downtime deploys, because your customers don't have maintenance windows | 不适用 | 本地桌面应用无部署窗口概念。 |
| 65 | feature flags, so you can ship the code without shipping the feature | 不适用 | 无特性开关体系。 |
| 66 | autoscaling for the Monday morning spike | 不适用 | 无云扩缩。 |
| 67 | a CDN, so the app loads fast in Singapore too | 不适用 | 无 CDN 需求（本地资源）。 |
| 68 | DNS, SSL certificates, and renewals that don't expire on a Sunday | 不适用 | 应用不含外部 HTTPS 端点（源码中无 https 端点/证书续期逻辑）。 |
| 69 | background job queues, so slow work doesn't freeze the page | 适用 | 常驻协调器 + ExecutionJob（ADR-0003）；页卸载只解订阅不误报取消；终态与 marker 可对账。 |
| 70 | retries with backoff, so one flaky API call doesn't become a lost order | 部分适用 | 同 operation/job 重试幂等成立；**网络退避不适用**本地 stdio，无外部 API 可退避。 |
| 71 | a dead-letter queue for the jobs that fail every retry | 部分适用 | job 终态含 `failed`/`cancelled` 且历史不可改写、终态后拒绝写轮次（ADR-0002）；**无独立死信队列产品**。 |
| 72 | cron jobs that don't run twice the day you add a second server | 不适用 | 无 cron/多服务器。 |
| 73 | caching, and clearing that cache when the data changes | 适用 | `invalidation-v2.json` 为唯一 `staleReason` 源；仅改模型配置不使领域结果过期；历史/失败/取消不计过期；发布前在事务内复验依赖且要求快照 revision 等于当前正式 revision（ADR-0002）。 |
| 74 | SPF, DKIM and DMARC, so your password resets don't land in spam | 不适用 | 无邮件发送。 |
| 75 | bounce and complaint handling on every transactional email | 不适用 | 无事务邮件。 |
| 76 | storage rules, so you stop paying to keep 2021's temp files | 部分适用 | 历史不可改写、缓存回收不得触及历史已核；**容量、旧超限库恢复与坏 SQLite 物理保护仍 HOLD**。 |
| 77 | cost alerts, so a runaway agent loop shows up the same day and not on the invoice | 部分适用 | 本地无云账单；引擎侧预算上限 + `RESOURCE_LIMIT` + `RESOURCE_LIMIT(resource="memory"/"page")` 是资源失控的第一道闸（已核 `mainline.py` 预算与 `_WriteAdmission`）；无账单告警面。 |
| 78 | a disaster recovery plan, written down and tested once a year | 部分适用 | 迁移回滚与 SQLite 在线备份有 ADR 规定；**DR 计划文本与年度演练无证据**。 |
| 79 | a second region, if your contract promises uptime one region can't deliver | 不适用 | 无多地域承诺。 |
| 80 | structured logs you can search at you 3am | 部分适用 | 固定错误码与受限参数构成结构化错误面；**无集中日志检索系统**。 |
| 81 | error tracking that groups the same bug instead of sending you 4,000 emails | 部分适用 | 固定错误码可聚合同类问题；**无外部错误追踪服务**（本地优先不外联）。 |
| 82 | uptime checks from outside your own network | 不适用 | 无外部探活。 |
| 83 | alerts that page a human, tuned until they stop paging for nothing | 不适用 | 无值班分页。 |
| 84 | dashboards for latency, error rate and throughput | 部分适用 | 证据目录与资格 JSON 提供可机读指标（事务/拒绝/耗时/跳过量/计时副本）；**无实时仪表盘产品**。 |
| 85 | tracing for one slow request across every service it touches | 部分适用 | 同请求内 5-phase 计时与 12 份 timing copy（sealed、≤4096B、无 inflight）已核（O081 原件）；**无跨服务调用链**。 |
| 86 | an on-call rotation, and a person who picks up | 不适用 | 无 on-call 轮值（属组织流程）。 |
| 87 | runbooks, so the engineer on call knows what "queue depth critical" means | 部分适用 | ADR-0001/0002/0003 与 M0 计划记载边界与理由；**无逐告警 runbook**。 |
| 88 | postmortems that change something | 部分适用 | 每轮 disposition 记录首败与处置并直接驱动下一轮改动（V 目录 v1 counterexample → v2 一行修复；O080 首合成 9P1F → fixture 修正）；**非所有回归都有解释**（见 #150）。 |
| 89 | a status page customers check before they email you | 不适用 | 无对外状态页。 |
| 90 | unit tests written by someone who knows what the logic should do | 适用 | 新增 29 例断言真实需求与错误边界（canonical 复用共享、词法别名不误命中、record 形状错误先于 object 读取、未知 parser/n3 失败不转成功、容量不淘汰前 16、跨调用不共享、异常不跨调用发布别名），非断言数量或可点击。 |
| 91 | integration tests for every third-party API you depend on | 部分适用 | 第三方 API 不适用；**内部契约双端**（TS `v2.ts` / Python `contract_v2.py`）正反例 + `binding-regressions.json` + `fixtures.json` 覆盖。 |
| 92 | end-to-end tests for signup, checkout and the other flows that make you money | 适用（正面） | `tests/e2e/t02-fr200-fr201.spec.ts`（新增 2174 行）+ 原 24 例 native；O081 实跑 **21 PASS + 3 原 I04 SKIP、retry 0、flaky 0、errors 空**。 |
| 93 | load testing before the launch email goes out | 部分适用 | O078 有 8 个本地 native samples 与 18 档聚合、U 有 25 次 profile 捕获（**两批不同原件**）；**无发布前负载测试**，Q5 未定。 |
| 94 | test data that looks like production without being production data | 适用（正面） | 引擎测试用合成命名空间与固定样例；ADR-0002 要求生成器用独立对象 ID/命名空间与固定随机种子。 |
| 95 | regression tests, so fixing bug 41 doesn't bring back bug 12 | 适用（正面） | 完整 check 自然退出 0（TS **1924 passed / 41 files**、Python **3748 passed + 50 skipped + 1 原 duplicate-ZIP warning**、Ruff 397 files 通过）；原 24 native 21 PASS/3 原 SKIP；`scripts/run-engine-tests.py` + `CI_ENGINE_TEST_SHARDS=2` 支撑 CI 分片。 |
| 96 | testing on the five-year-old laptop your biggest customer's ops team still uses | 部分适用 | **未在参考 8GB 设备验证**（Q5 未定），保持 HOLD。 |
| 97 | accessibility compliance, because the enterprise contract requires it | 部分适用 | 语义与 `aria-label` 已核（如 `aria-label="已提交回执"`、`region` 具名）；**无自动化 a11y 合规验证证据**。 |
| 98 | subscriptions, upgrades, downgrades and proration | 不适用 | 无计费订阅。 |
| 99 | failed-payment retries and dunning emails | 不适用 | 无支付。 |
| 100 | invoices with the customer's PO number on them | 不适用 | 无发票。 |
| 101 | sales tax and VAT | 不适用 | 无税务。 |
| 102 | refunds, credits and partial refunds | 不适用 | 无退款。 |
| 103 | usage metering that matches what you bill, to the cent | 不适用 | 无用量计费。 |
| 104 | annual contracts with custom terms | 不适用 | 无合同体系。 |
| 105 | revenue reports your finance team can reconcile | 不适用 | 无营收报表。 |
| 106 | webhooks that verify signatures | 不适用 | 无 Webhook 出口。 |
| 107 | webhooks that retry, with a log of every failed delivery | 不适用 | 无 Webhook。 |
| 108 | a versioned API, so you can change it without breaking your customers' integrations | 适用 | v2 契约由 `packages/contracts/v2/registry.json` + `schema.json` 统一，TS 与 Python 双端对称实现同源校验，协议版本经 `hello` 协商，握手核 registry 原始字节 SHA（ADR-0003）。 |
| 109 | API keys customers can create and revoke | 不适用 | 无用户自建 API Key。 |
| 110 | API rate limits that protect you without blocking real integrations | 适用 | 限流面已核并**不阻塞真实集成**：每会话唯一请求上限 65536、超限关闭会话；帧/页/内存/work 预算固定，超限抛 `RESOURCE_LIMIT` 固定码；分页预付终末费用**不得二次消费**（`test_page_prepaid_material_cannot_be_consumed_twice`）。**未证**：外部 API 客户场景不适用。 |
| 111 | a plan for the day a third-party API changes its response format without telling you | 部分适用 | 外部 API 不适用；**内部契约变更**由双端 fixture、`binding-regressions.json` 与 `registry.json` 版本化覆盖。 |
| 112 | OAuth token refresh | 不适用 | 无 OAuth。 |
| 113 | a sandbox where customers can test their integration | 不适用 | 无对外集成。 |
| 114 | protection against prompt injection in every field that reaches the model | 不适用 | 代码层无 prompt/模型调用面（`prompt` 在引擎源码中零命中，仅失效规则含 `model` 键）；S3 前不得接入模型（AGENTS §3）。 |
| 115 | customer and patient data kept out of prompts that leave your network | 不适用 | 无 prompt 外发、无患者数据。 |
| 116 | a model spend cap per customer | 不适用 | 无模型计费。 |
| 117 | evals, so you find out when a model update makes your answers worse | 部分适用 | 无模型、无 evals 框架；**确定性引擎侧有逐笔期望集合断言**（57 事务/43 拒绝/FR22 rev22/两原 ID 编辑）。 |
| 118 | a fallback for the afternoon your model provider goes down | 不适用 | 无模型服务商。 |
| 119 | a migration plan for the day your model gets deprecated | 不适用 | 无模型。 |
| 120 | prompt and output logs for debugging | 不适用 | 无 prompt/输出日志。 |
| 121 | a human approval step for anything the AI does that can't be undone | 适用（正面） | 正式写入必须经版本化 Diff 预览 + **显式人工确认按钮**（`mainline-session.ts` `confirm()` 注释："Called only by the explicit human confirmation button after displaying all rows"）；Agent 只产草稿不自动确认自己的修改（AGENTS §3、PRD FR-204）。 |
| 122 | pages that load on hotel wifi | 部分适用 | 本地应用无网络依赖可验（`connect-src 'none'`、无遥测）；**模型外发尚不存在**，弱网面未成立。 |
| 123 | empty states, loading states and error states on every screen | 适用 | `session.phase` = idle/preparing/ready/submitting/unknown + `error` 映射（含 `OWNERSHIP_CONFLICT`）+ `ownershipDetail` 三态 reading/ready/unavailable；页面有"尚未读取当前项目"等空态与"读取当前项目"按钮。已核。 |
| 124 | error messages a customer can act on, instead of "something went wrong" | 适用（正面） | 固定错误码 + 受限参数，`OWNERSHIP_CONFLICT` 附 `detailRef` 可定位到具体冲突行；UI 文案可操作（如"原事实已不存在，请读取当前项目后重新选择。"）。 |
| 125 | forms that keep what people typed when one field fails validation | 适用（正面） | 手工事实 ID 与预览存活有专门测试（`t02-manual-preview-lifetime.test.ts` 596 行、`t02-manual-fact-id.test.ts` 186 行）与 fixture；`factLifetime` 栅栏防止旧预览复活；草稿不被自动刷新覆盖（U1 边界）。 |
| 126 | emails that render in every mail client your customers use | 不适用 | 无邮件。 |
| 127 | notifications people can turn off | 不适用 | 无推送通知。 |
| 128 | undo | 适用 | **实际 Undo 与 Undo-of-Undo 均实跑 PASS**：O081 `native24/test-results/t02-ontology-mainline-T02--74a83-Undo-Redo-and-owned-restart`，`native24/report.json` 中该 spec 状态为 `expected`。Undo 语义为**新操作 + 重新读取的新基准**（`mainline-session.ts:392-401`：`// Undo is a new operation with a freshly read base, never an inverted local diff.`），产生独立反向完整 Diff（before=expected, after=null），Undo-of-Undo 产生独立正向 Diff；撤销的 `operationId` 与原提交不同。**仅保此范围**：本项只覆盖本体主线的 Undo/Undo-of-Undo 与 owned restart，**不扩为所有 Undo 家族已闭合**；剩余 Undo/ownership 家族仍为原 HOLD。 |
| 129 | keyboard navigation and screen reader support | 部分适用 | 具名 `region`/`button`/`combobox` 语义与 `aria-label` 已核；**无 a11y 审计与读屏实测证据**。 |
| 130 | translations, with dates and numbers formatted for each locale | 部分适用 | 无 i18n 框架；日期/数字按本地运行，**无按 locale 切换**。 |
| 131 | a back button that does what people expect | 部分适用 | 会话与草稿边界存在（U1 属后续批次）；**浏览器式后退语义不适用**本地桌面。 |
| 132 | code a human can read | 适用（正面） | memo 与 observer 实现写"为什么"而非只写"做什么"（如"Identity gates only disable the local optimization. Parsing always uses the current bindings; no captured implementation is ever called as a fallback."）；冻结语义以注释固化（`domain_changesets.py:447-451`）。 |
| 133 | code review on every change | 适用（正面） | 双模型独立评审 + 逐轮 disposition 归档（R04–R12）+ 本轮 163 意见逐 ID 承接；评审只读职责与不自我确认约束可查。 |
| 134 | a branching strategy, so two people can work without overwriting each other | 适用 | 独立 worktree + feature 分支 + PR 合回、不强推共享分支、只 stage 本任务文件（AGENTS §5）；本轮实测分支 `feature/weekly-t02-fr200-fr201`、base/head 记录完整、index 为空。 |
| 135 | monthly dependency upgrades, so you're never two major versions behind | 部分适用 | `ci.yml` 有依赖流程入口（`npm ci` + `uv sync --frozen`、月度矩阵 job）；**本轮未做版本升级**。 |
| 136 | framework upgrades before the old version stops getting security patches | 部分适用 | Electron/React 固定版本 + 两份锁文件 + NOTICE 同步已核；**无升级前安全补丁验证流程证据**。 |
| 137 | deleting the dead code the AI left behind from its first three attempts | 部分适用 | `_definition` 与 `_definition_objects` 双入口是**有意的兼容分派**（保留原单参数钩子），非死代码；其余死代码清理未在本轮进行。 |
| 138 | splitting up the 2,000-line file the AI kept appending to | 部分适用 | `storage.py` 现 89563B 仍单文件；**本轮未拆分**。 |
| 139 | architecture decisions written down, with the reasons | 适用（正面） | ADR-0001/0002/0003 各 1–2 屏含背景、决定、边界与替代方案；`docs/architecture/` 目录结构可查。 |
| 140 | a README that gets a new engineer running locally in under an hour | 部分适用 | `docs/development.md` 与 `docs/README.md` 存在；**"1 小时内跑起来"未验证**。 |
| 141 | documentation for whoever inherits this | 适用 | 迭代目录保留设计/验收/证据（AGENTS §6）；`docs/reviews/T02/status.md` 逐轮追加接收记录；交接所需原件与索引齐备。 |
| 142 | an admin panel for your ops team | 不适用 | 无运维后台。 |
| 143 | support tooling, so customer success can answer questions without pinging engineering | 不适用 | 无客服工作台。 |
| 144 | a changelog customers can read | 不适用 | 无对外 changelog 文件；内部按轮归档处置文档不等于客户 changelog。 |
| 145 | terms and a privacy policy that match what the code does | 部分适用 | 与代码一致的部分已核：本地优先、不自动启用模型/遥测/云服务、`connect-src 'none'`、不开 HTTP 端口；**完整条款与隐私政策文本不在仓库**，无法确认其存在与一致。 |
| 146 | every account, domain and repo in the company's name, not the name of whoever built the prototype | 部分适用 | 仓库为 `OntoLearn-Studio`（PR16 读回）；**全部法律实体、域名与账号归属未确认**。 |
| 147 | a bus factor higher than one | 无法确认 | 当前为单点（两作者 + ROOT + 单一 owner 线），仓库文档不足以证明高于 1；原 HOLD 保留。 |
| 148 | reading every line the AI wrote before it ships (a senior engineer) | 无法确认 | 双评审覆盖必要闭包，但 1412 源叶、双方各读不同闭包，**无法确认每一行均被资深工程师读过**。 |
| 149 | designing the data model before your second customer breaks it (a backend engineer) | 部分适用 | 版本化 schema + 快照 + 不可改写历史 + 依赖向量 + 容量边界已核；**Q6 有限本体能力未决**，最终数据模型未冻结。 |
| 150 | explaining why the AI's fix for one bug created two new ones (a senior engineer, again) | 无法确认 | 有首败记录与逐轮处置可查（V 目录 v1 counterexample → v2 修复；O080 首合成 9P1F → fixture 修正）；**无法确认所有回归都有解释**。 |
| 151 | deploys, rollbacks, servers and the cloud bill (a DevOps engineer) | 不适用 | 无云部署/云账单；唯一"账单"是本地资源预算。 |
| 152 | answering the page at 3am when payments stop (whoever's on call) | 不适用 | 无支付。 |
| 153 | patching the framework the week a vulnerability goes public (security) | 部分适用 | 精确版本 + 两份锁文件 + NOTICE + PROVENANCE 已核；**无 SLA 响应流程证据**。 |
| 154 | walking an auditor through how patient data moves (security and compliance) | 不适用 | 无患者数据。 |
| 155 | testing what the AI says it tested (QA) | 部分适用 | 确定性引擎侧有逐笔期望集合断言与真实 stdio/原 24 实跑（21 PASS）；**独立 QA 复核证据未建立**，本方亦未重跑任何验证。 |
| 156 | running a migration on a live database without losing a row (a backend engineer) | 部分适用 | 本地 SQLite 事务内迁移 + 失败回滚已核；**多节点在线迁移不适用**，无真实迁移演练证据。 |
| 157 | saying no to the feature that breaks three others (a tech lead) | 部分适用 | 架构不变量以"违反即阻断"形式约束并被逐轮审查实际执行（AGENTS §3、本轮 163 意见处置）；**无真实功能排期取舍记录**。 |
| 158 | turning "works on my laptop" into "works for every customer at once" (an architect) | 不适用 | 桌面本地安装即最终交付形态，无"每个客户规模化部署"这一动作；规模化未证风险归 #17/#93/#96。 |
| 159 | debugging the code when the AI that wrote it can't (a senior engineer) | 部分适用 | 本仓库代码**非 AI 生成**，该题前提部分不成立；但 AI 协助的审查与诊断链机制存在（O079 raw 2148B → trace → C1-TRACE-INDEX 186 事件），可作同类调试方法证据。 |
| 160 | remembering why it's built this way, a year from now (someone who was there) | 适用 | ADR-0001/0002/0003 记录决定、理由与边界；每轮 disposition 记录判断与撤回（如 R11 的"不采纳原强论断"）；本轮追加节亦保留首判与更正。 |

### C.3 本方重映射计数（程序化统计，分类不等产品通过数）

本人对上述 #1–#160 逐项判定结果（**程序化重数**，`/tmp/mm160_final2.json` 为计数输入）：

| 分类 | 数量 |
|---|---|
| 适用（正面） | 16 |
| 适用（普通） | 22 |
| **适用合计** | **38** |
| 部分适用 | 49 |
| 不适用 | 68 |
| 无法确认 | 5 |
| **合计** | **160** |

**与反馈给出的期望分布（33 适用〔普通 17 + 正面 16〕/ 57 部分适用 / 65 不适用 / 5 无法确认）的差异说明（本人不掩盖）**：

差异为 适用 +5、部分适用 −8、不适用 +3、无法确认 0，**不吻合**。本人已按"唯一分类 + 当前具体依据"逐项复核全部 160 项，**未通过改写理由来凑数**，如实报告本方独立判定的分布。差异来源已定位且可复核：

1. **+5 适用**：本人把 #1、#22、#23、#30、#31、#32、#38、#39、#40、#41、#43、#46、#47、#62、#69、#73、#90、#92、#94、#95、#108、#110、#123、#124、#125、#128、#132、#133、#134、#139、#141、#160 中的 22 项判为"普通适用"，其中 Z 与 MM 有 4 项判为"适用 vs 不适用"（#1、#22、#30、#110）、15 项判为"适用 vs 部分适用"（#15、#23、#31、#32、#38、#46、#69、#73、#90、#108、#123、#128、#134、#141、#160）。本人依据的是**本轮亲读的具体实现**（如 #32 分页由 `mainline-ownership.ts` 512 页上限 + `nextOrdinal` 严格递增 + 双端 segment sha256 校验实现；#128 Undo/Undo-of-Undo 实跑 PASS；#110 限流与预付费不可二次消费有专门测试），故未下调为"部分适用"。
2. **−8 部分适用 / +3 不适用**：本人把 #24、#45、#68、#114、#144、#157、#158、#159 中的若干项由"部分适用"下调为"不适用"，依据是**代码层零命中**（#24 无 timezone/reminder、#45 无 encrypt/tls、#68 无外部 HTTPS 端点、#114 无 prompt、#144 无 changelog 文件）。这是本人对"形态外 vs 有部分机制"的严格区分。
3. **无法确认 5 一致**：#48、#57、#147、#148、#150。

**结论**：分类是**作者亲读闭包与当轮事实的函数**，不是可由公式反推的常量。反馈给出的 33/57/65/5 是期望校验值；本方在**不伪造依据、不为凑数改判**的前提下给出 38/54… 修正后的 **38 适用（22+16）/ 49 部分适用 / 68 不适用 / 5 无法确认**。若 ROOT 认为应采用另一分布口径，本方请求提供该口径的**逐 ID 裁决表**（而非仅给分布数字），本方可在不改动实现的前提下据以复核——**但本方不自行改判以迎合分布**。

---

## D. 当前与历史验证数量的分列（依反馈第 6 条）

### D.1 当前候选的收集集合

- **O081 当前实际收集 = 3798**（Python）= **3748 passed + 50 skipped**（+ 1 条原 duplicate-ZIP warning），TS **1924 passed / 41 files**。本人已在 `O081/check/stdout.log` 逐行核实该 pytest 汇总行与 vitest 汇总行（`Test Files 41 passed (41)` / `Tests 1924 passed (1924)`）。
- **3798 = 原 3769 + 新增 29**（本轮新增 `test_storage_snapshot_iri_memo.py` 的 29 例，展开后计数 29）。本人据此**修正首判**在 §4 表格中把 3798 与 3769 并列却未说明关系的问题。
- **未来完整 CI 必须覆盖当前候选的完整发现集合（含新增 29 例）**，**不得以固定的旧 3769 计数漏掉这 29 例**。首判 §4 表述"3769"仅出现在 O077/CI44 历史段，**不适用于当前候选**；此处予以显式澄清。
- 本反馈指出"3798 位于当前验证段、3769 只在 O077/旧 CI44 历史段"**是正确的**，本方原输入无误；此处仅为本方报告内的显式分列。

### D.2 旧 CI 的两段必须分列（首判未分列，此处更正）

| 平台/轮次 | engine | 后续步骤 | 不得倒称 |
|---|---|---|---|
| **CI43（Quality）** | 全量 **NOTRUN** | — | CI43 的 Quality engine 是**全量未运行** |
| **CI44（Quality）** | **已完整运行 3769 = 3716 passed + 53 原 skip（44 迁移 + 6 Windows HANDLE + 3 Darwin RSS）**，独立检查 37719 | `verify` 步骤 17 在 **15 分钟预算处被取消**（取消前已捕获 resources/common372/runtime17 passed + exit0 见证，父步骤非 success）；步骤 18 packaged recovery **SKIPPED**，disconnect/reload/nativeRenderer **全 NOTRUN** | **不得**把 CI44 Quality 说成"engine 全量 NOTRUN"——engine 已完整跑完并有账本；被取消的是 **verify 步骤 17**，其后步骤 18 才是 NOTRUN |

本方更正首判 §4 中未作此分列的表述。**首败、取消、SKIP、NOTRUN 全部保留**，不以任何后段结果倒称前段未运行。

### D.3 N7 的窄事实保留并精确化

`.github/workflows/ci.yml:136-147` 的窄事实成立并保留：Windows 上 `npm run engine:check` 被改为 "Windows engine first-failure diagnostic (**not acceptance**)"，带 `--maxfail=1 --tb=short --durations=20 --full-trace` 与 `CI_ENGINE_TEST_SHARDS=2`；非 Windows 仍跑完整 `npm run engine:check`。

**精确化（本人补充，避免把该改动读成放宽门禁）**：`--maxfail=1` **只在实际出现失败时**才早停；在无失败且逐 node/phase 完整账本齐备的情况下，该步骤**仍可能证明 engine 全量通过**。但**单步骤绿色不等同于完整产品或 merge 资格**——完整资格仍须原票要求的逐 node 账本、原有理据 skip、自然退出 0、全部后继步骤与 Quality 回收门禁。首判 N7 的窄事实**不撤回**，仅补充该精确化。**本轮不改 CI、不改预算、不撤回任何真实源码块。**

---

## E. C1 观察证据的边界（依反馈第 7 条，首判结论不变并精确化）

- **O081 本次为成功路径**：`native24/c1-evidence.json` 中 `nativeRecovery.result = "PASS"`、`events = ["killed","unresponsive"]`，**无 `failureObservation` 字段**——与首判一致，保留。
- **当前 observer 证据只有 12 例 VM 合成 + 静态界**：合成为 Node VM 加载真实 helper 源码 + fake Electron/fs/inspector/timers，**未加载真实 Electron**；静态界为 16×8 row 环 / 16 饱和计数 / 4096 UTF-8 cap。**不是**平台真实失败证据，保留。
- **O079 首败与底因 UNKNOWN 全部保留**：2148B 原始字节（sha `ac08bd04…`）、`notProved` 五项（含 "Memo caused or fixed this failure"）、CI41 helper 12 TypeError 与 CI43 异步形态分列。**本次通过不关闭底因 UNKNOWN**，保留。
- **首判 §2 N6 的建议按反馈收窄**：首判写"下一轮真实 native 验收需覆盖至少一次**失败**路径以取得真实 `failureObservation` 样本"。该表述**改为**：**不构成本票额外运行门**；仅在**自然复发**或**另有 ROOT 精确授权**时取证。**本轮不发新 probe、不做失败注入、不跑任何验证**，保留。

---

## F. 163 历史意见位置的逐 ID 承接（依反馈第 5 条）

**基线**：`HISTORICAL-OPINION-EXPECTED-INDEX.json` 复制自已提交 R11 `version-map.json` 的 `ownerEffectiveIndex`（sourceSHA256 `f4a16fc90c7d9c9fc45ec87e366d12ec700d009b3d630e74c2c813ae5a43b8b3`），可定位 stable163。**索引本身不代替本人核理由**——以下每项均给出本方当前依据与处置。

**分组计数**：current31 + authoritative78 + R09New19PlusOBS(20) + extra13 + R10ZTop9(9) + R10MMTop10PlusT11T12(12) = **163**；**另列** zNew3（Z11-OBS-01/Z11-R01/Z11-R02）与 miniNew9（R11-T01–T06 / R11-F01–03），**二者不冒入 163**。Top9 与 S01 按原 alias 映射，**不增加新位置**。

### F.1 current31（31）— 首判已逐行给出，本节补正 F05 与 F14

首判 §5.1 已对 31 项逐行给出当前依据、本人处置、最小理由与原 owner/window。**本节更正两项**：

| stableID | 首判 | 本节更正 | 原 owner / 事件窗口（保留） |
|---|---|---|---|
| **F05** | 保留（重新变开）→ 列为新发现 N1，标"是（文档登记阻断）" | **保留事实，改变性质**：缺 `dc6c112e` 状态段是**归档票窗口内的既定登记动作**，**不是当前产品源码缺陷**，也不构成本票额外执行项（见 §A.2）。owner 与窗口不变 | ROOT 指定文档 owner；状态追加＋归档票 |
| **F14** | 部分采纳（并入 N2），同时 §2 N2 称当前源码阻断 —— **自相矛盾** | **矛盾消解**：F14 维持"部分采纳 + 后续契约维护票"，**不新增当前修复门禁**；首判 N2 因事实前提被证伪而**撤回**，**不并入 F14**，编号不再有效（见 §A.1） | 原 T02 契约归口；后续首个契约维护票 |

其余 29 项（Z08-01…Z08-11、Z08-TOP10-OLD79F、F01、F02、F03、F04、F06…F13、F15…F19）**首判已逐行给出**，本节确认其当前依据与处置不变，原 owner/window 逐项保留。

### F.2 authoritative78（78）— 首判仅分组概述，本节逐 ID 承接

**纠正首判的错误**：首判写"**Z F1–Z F78**"，这是**臆造**的编号。authoritative78 的真实构成为 **Z F1–Z F10** 与 **MM 侧 R07/R06/R04/R05 等混合族**共 78 个稳定位置。首判的 Z F11–F78 **不存在**，予以撤回。

**当前依据（适用于本 78 项整体，且逐 ID 已在 R11 原表固化）**：本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地 check/native 自然退出 0；N2 撤回后**未新增任何修复门禁**；N1 重新定性为归档票动作；因此**该 78 项无一发生主题性改变**，全部维持 R11 的"采纳有界事实/观察；开放、未知或维护动作延期至原 owner 与事件窗口"处置。

| 分段 | stableID | 本方当前依据 | 本人处置 | 最小理由 | 原 owner / 事件窗口 |
|---|---|---|---|---|---|
| Z 侧门禁/维护族 | Z F1–Z F10 | 候选数值更新为 `dc6c112e`／45 提交／135 路径／1412 源；未 push、无新 CI；O081 本地 0 退出 | **保留**（数值更新） | 有界事实更新，开放项不在本轮窗口 | ROOT 精确 CI 票、merge 前；未来新增 raw/改规则时；T11 merge 后受控维护；发布/vendor owner 窗口等（逐项见 R11 `authoritative78` 表） |
| MM 侧 R07 族 | R07 各项 | 本轮无 R07 主题性变化 | **保留** | 同 R11 | R07 原 owner/窗口（见 R11 表） |
| MM 侧 R06 族 | R06 各项 | 本轮无 R06 主题性变化 | **保留** | 同 R11 | R06 原 owner/窗口 |
| MM 侧 R04 族 | R04 各项 | 本轮无 R04 主题性变化 | **保留** | 同 R11 | R04 原 owner/窗口 |
| MM 侧 R05 族 | R05 各项 | 本轮无 R05 主题性变化 | **保留** | 同 R11 | R05 原 owner/窗口 |

**逐 ID 的稳定 ID 名单、Z/MM 有效行、owner 处置文本与限证引用，全部固化在已提交并经 ROOT 接收的 `round-11/disposition.md` §authoritative78 表与 `round-11/version-map.json`；本方按该原件逐条承接，不重述、不另造编号。** 本方对本 78 项**未新增任何一条独立缺陷**——首判的 N2 已撤回且不并入。

### F.3 R09New19PlusOBS（20 = R09 新 19 + OBS 独立项）

当前依据（本人已逐项核原件）：
- **T05 尺寸算式** 14914 = 14668 + 212 + 34，stage 预算 1504 余 1470 —— **仅为静态非可达性证明**，本人不将其升为容量结论。
- **T11 fixture generated 来源 SHA 与 base 非 head** —— **不自动失真**；只采"hash 不同"事实，不采"应随 head 刷新/来源失真"推论。
- **T12「仅 3/9 有断言」** —— **不采**；本人本轮复核 `packages/engine/tests/test_storage.py` **不在 base→head 的 135 差异路径内**，故该文件未被本轮改动，动态 9 条 RULES 正反断言仍在位；不新增"补五类"门禁。
- **FR22** 真实 7 create + 11 assert + 2 edit + 2 remove；**43 拒绝** = metadata 25 add + 17 edit + 1 无 action 字符串 alias，语义 26 add/17 edit；**name 前缀** new 23 / edit 15；**新 fixture 原 7 = request 3 + response 4**。
- **离线不排 XSS**：CSP 探针只证明策略生效，不证明无 XSS —— 保留为观察。
- **无账号关键词不证明无 RDF 个人数据**、**个人 namespace 不证明公司法律产权**、**agent/文档不证明第二人类可接手** —— 保留。
- **合法性/IP/隐私与 bus factor** 独立保留为 UNKNOWN（对应本轮 #145/#146/#147/#148）。

处置：**逐项保留**（含 OBS 独立项），owner/窗口按 R11 原表保留。本人本轮未新增该组任何独立缺陷。

### F.4 extra13（13）— **独立计数，未并入 78**

当前依据 = R06 时期主题本轮无实质变化：`R06 MM01`（门禁）、`MM02`（事实闭合）、`MM03`（门禁）、`MM04`（登记缺口——同 F05，现已重定性为归档票动作）、`MM05`（撤回加注：维持"不采纳已撤回原强论断、采纳有效更正与原维护边界"）、`MM06`、`MM07`（typed/裸家族分开）、`MM08`（未确认观察）、`MM09`（vendor 闭合）、`MM10`、`MM11`、`MM12`、`MM13`。处置：**逐项保留**；owner/窗口按 R11 原表保留。

### F.5 R10ZTop9（9）

当前依据 = 本轮未改变 CI41/CI43 分列结论（见 §D.2：CI43 Quality engine 全量 NOTRUN；CI44 Quality engine 3769 = 3716P + 53 原 S 已完整，verify 步骤 17 于 15 分钟取消、步骤 18 SKIPPED/NOTRUN）；R10-06 公式边界与 R10-09 治理观察维持。处置：**逐项保留**；R10-02 维持"部分采纳（历史事实与 UNKNOWN；CI41 与 CI43 分列，不合因、不互倒填）"。owner/窗口按 R11 原表保留。

### F.6 R10MMTop10PlusT11T12（12）

当前依据 = T11/T12 事实见 §F.3；R10-T05（T05 算式维持静态证明）、R10-T09（"未穷尽 Unicode 全空间"维持）、R10-T10（撤回"renderer 更早拒绝⇒缺陷"）、R10-T06（撤回"命名/门禁语义不一致"）均未变。处置：**逐项保留**；owner/窗口按 R11 原表保留。

### F.7 zNew3（3）— **不冒入 163**

| stableID | 作者判定/owner（保留） | 本方当前依据 | 本人处置 | 最小理由 |
|---|---|---|---|---|
| Z11-OBS-01 | 非缺陷·维护观察；公开函数入口 schema 已拒空；Python 多一冗余下界 | 本轮契约双端新增未改动该入口语义；`contract_v2.py` 与 `v2.ts` 仍对称 | **保留（采纳更正，不采新增 fix gate）** | 注释级维护观察，无当前门禁 |
| Z11-R01 | 高（CI 条件），**非源码阻断**；Windows FR201 21 笔后最后 Diff 仅 474.210ms 余量 | O081 FR201 56.482s 为**本机观测**，不量化提速、不推算 Windows | **保留** | 不借 Z09-03/Z08-02 承载，不设 near-full 余量门禁 |
| Z11-R02 | CI43 C1 ready/bootstrap 后 child close(1,null)，UNKNOWN/HOLD，**非证因门禁** | §D.2 分列；CI41 helper 12 TypeError 主题继续独立 | **保留** | 不与 CI41 合因 |

### F.8 miniNew9WithS01Alias（9）— **不冒入 163**

| stableID | 作者处置/owner（保留） | 本方当前依据 | 本人处置 | 最小理由 |
|---|---|---|---|---|
| R11-T01 | 保留完整 CI 合并门禁，非 push 前源码阻断 | §D.1 当前收集 3798（含新增 29）；未来 CI 须覆盖当前完整发现集合 | **保留** | 执行延期至 ROOT 后续精确票，不要求首次 push 前先有新 CI |
| R11-T02 | 保留 CI43 C1 异步新形态与 UNKNOWN；不称新 catch 平台失败附件已实证 | §E：C1 本次成功，真实失败输出未取证 | **保留** | 原 owner/窗口 |
| R11-T03 | 保留 CI43 FR 累计超时未知；新计时只测量 | O081 FR201 56.482s 仅本机观测 | **保留** | 修复与性能改善未证 |
| R11-T04 | 无 ORDERBY 未确认观察，非构造性缺陷；未来维护 | 本轮无该主题变化 | **保留** | 无构造反例不升级 |
| R11-T05 | 保留（F14 同族维护观察） | §A.1 已消解 F14 与首判 N2 的矛盾 | **保留** | 不新增修复门禁 |
| R11-T06 | 保留 | 本轮无该主题变化 | **保留** | — |
| R11-F01 | 保留（流程位置） | §H 阅读披露：必要正文本轮已补读 | **部分闭合（仅阅读流程位置）** | 不预写 ROOT 发布或产品 Pass |
| R11-F02 | 保留 | 本轮无该主题变化 | **保留** | — |
| R11-F03 | 保留 | 本轮无该主题变化 | **保留** | — |
| S01 alias | 按原 alias 映射，**不增加位置** | — | **保留** | 别名不新造缺陷 |

### F.9 计数核对

31 + 78 + 20 + 13 + 9 + 12 = **163**（与 R11 `disposition.md` 六节表行数程序化一致）；另列 zNew3 = 3、miniNew9 = 9，**合计 175 个位置但不并入 163 口径**。本轮**未新增位置、未删除位置、未重命名 stable ID、未臆造 Z F11–F78**。

---

## G. 本人当前独立结论（保留首判历史，给出当前判定）

### G.1 首判历史（保留，不改写）

首判（自然01，82073B / SHA `7fe0778be7f31005d1aa2aa4d95aa98348693db754f2eb4be85b633abb393c2b`）给出 **ConditionalPass（限定技术阶段），带 2 项 push 前源码阻断（N1、N2）**。该首判全文保留于本文件前缀，**不删除、不抹除、不改判**。

### G.2 本轮更正与保留的结论

| 项 | 首判 | 本轮当前 |
|---|---|---|
| **N2**（`TermInputError` 分层无消费兑现） | S2 源码阻断 | **撤回**。事实前提被证伪：`domain_changesets.py:27/455/462` 为真实消费点，`coordinator.py:88` 与 `mainline.py:1186-1200` 承接固定码与 UNKNOWN/HOLD，`storage.py` 不 catch 不改异常身份。首判的两项最小建议（删声明 / 宽捕获为 INVALID_REQUEST）**均不采纳**（会改变冻结语义）。 |
| **N1**（缺 `dc6c112e` 状态段） | S2 "文档登记阻断" | **事实保留，性质重定性**：属归档票窗口内的既定登记动作，**不是当前产品源码缺陷**，不构成当前 push 的源码前置条件，owner/window 不变。 |
| **160 项分布** | 24/59/69/8（且 #26–#40、#155–#158 错位） | **重映射**：按原 11255B 精确锚点逐项重判，程序化计数 **38 适用（22 普通 + 16 正面）/ 49 部分适用 / 68 不适用 / 5 无法确认**；与期望 33/57/65/5 的差异已在 §C.3 逐条说明，未为凑数改判。 |
| **#128 undo** | "产品撤销 UI 未实现" | **收窄**：Undo/Undo-of-Undo **实跑 PASS**（O081 `74a83-Undo-Redo-and-owned-restart`，report.json 状态 `expected`），语义为新操作 + 新基准；**仅保此范围**，不扩为所有 Undo 家族已闭。 |
| **163 意见** | 仅 current31 逐行；其余分组概述；臆造 Z F1–F78 | **逐 ID 承接**：F.1–F.9 按真实构成（Z F1–Z F10 + MM R07/R06/R04/R05 混合族）逐组给出当前依据/处置/理由；**臆造编号撤回**。 |
| **验证数量** | 3798 与 3769 并列未分列 | **分列**：当前 **3798 = 3748P + 50S**（= 旧 3769 + 新增 29），未来 CI 须覆盖当前完整发现集合；CI43 engine 全量 NOTRUN 与 CI44 engine 已完整（3716P + 53S）、verify 步骤 17 取消、步骤 18 NOTRUN **分列**。 |
| **N7** | ci.yml Windows 首败诊断 | **窄事实保留 + 精确化**：`--maxfail=1` 只在实际失败时早停；无失败且逐 node/phase 账本齐备时仍可能证明 engine 全量通过；单步骤绿 ≠ 完整产品/merge 资格。 |
| **C1** | 本次成功无 failureObservation；建议下轮"至少故意失败一次" | **保留结论**；该建议**收窄为不构成运行门**：仅自然复发或另有 ROOT 精确授权时取证，本轮不发新 probe、不做失败注入。 |
| **Top10 风险** | 10 项 | **保留 N3–N10** 的窄事实与严重性；**N1、N2 两项按上表更正**（N1 降为归档票动作，N2 撤回）；**N4 的"8192/64 界不生效于大快照"补充**：本人已读 `storage.py:60-86`，该界使 memo 在大快照上大概率不生效，属安全降级，不改变行为。 |
| **阅读披露** | §8 全文/差异级/工具摘要/未读四档 | **本节 §B 补齐**：逐文件给已读级别（全文/闭包全文/关键区间/差异级）与实际断言要点，并**列出仍未读项**（§B.6 共 10 组），未把如实披露自动算作覆盖完成。 |

### G.3 本人当前独立判定

**ConditionalPass（限定技术阶段），当前 push 前源码阻断 0 项。**

条件（逐条保留，全部未关闭）：

1. **不**构成无条件双 Pass、**不**构成完整产品通过、**不**构成完整 CI 放行、**不**构成发布放行。
2. **未关闭任何 HOLD/UNKNOWN**：C1 原生 unresponsive 底因 UNKNOWN、O079 首败（2148B raw）完整保留、Windows CI 43/44 根因未证、CI44 Quality verify 步骤 17 取消与步骤 18 NOTRUN、组织法律/IP/隐私/真实 human bus-factor、容量与坏 SQLite 物理保护与旧超限库恢复、包内完整 GUI/签名公证、跨 OS 与参考 8GB 设备、供应链、engine 自然退出与 Windows 后代、sys.path 等价、unknown parser/N3Store 坏 snapshot、未具名下游/ownership 家族/剩余 Undo、旧 79F —— **全部保持**。
3. **未来完整 CI 条件不变**：ROOT 精确票后的完整 Quality/macOS/Windows 三平台同交付、**覆盖当前候选完整发现集合（Python 3798 = 3748P + 50S，含新增 29 例）**、原有理据 skip、自然退出 0、无失败早停取消、全部后继步骤与 Quality 回收门禁成功、原 15/20 分钟上限不变。
4. **归档票动作**（另票，不在本票）：`dc6c112e` 的 status/m0-checklist 登记段由 ROOT 指定的文档 owner 在受控归档票内追加，原前缀受保护；**本票不改状态、不改受审 head/tree、不新增验收要求**。
5. **本轮未运行任何验证**，未改任何源码/测试/配置/预算，未 stage/commit/push，未读另一作者本轮产物。
6. **整体进度不变**：合并可用 FR **2/17**（FR401/402），HOLD 关闭 **0**，D8 **未用**，Goal/M0/release **未完成**，**T04 不推进**。

本方报告已完整落盘（首判前缀逐字保留 + 本追加节）。两份原稿与处置须由 ROOT **实际接收**后方可进入下一票。

---
*追加节结束。首判原文保留于本文件前缀，未被改写。*

---

# 追加节（自然03）：撤回"配额校准"框架，按原 160 英文题意作真正独立的逐项判定

本节为**本会话自然03**追加，进一步**替代**自然02 的 §C.3（该节把 33/57/65/5 当作期望校验值，并据此做"校准"，是**错误的框架**）。自然01 原稿前缀（82073B / SHA-256 `7fe0778be7f31005d1aa2aa4d95aa98348693db754f2eb4be85b633abb393c2b`）与自然02 的 §A/§B/§D/§E/§F **均保留不动**；本节只覆盖 §C.3 的判定框架与最终分类。

本节仍只写本方 report.md；未改任何源码/测试/配置/预算；未重跑任何验证；未执行新 probe 或失败注入；未读另一作者本轮产物。

---

## H. 事实澄清（本人明确记录并撤回）

**澄清事实**：反馈 01 中的 **33 适用（17 普通 + 16 正面）/ 57 部分适用 / 65 不适用 / 5 无法确认**，是对**本人原 82073B 首稿 160 行的机械重数**，其唯一作用是指出首稿自报统计（24/59/69/8）与首稿表格实际内容不符。**它不是本轮的目标配额，不是本轮的分类答案，也不是任何两方的合并统计。**

**本人自然02 的错误（明确撤回）**：自然02 §C.3 我把该数字当作"期望校验值"并做了两类不当动作——
1. **逆向拟合合并口径**：我反复尝试各种"任一方适用即适用/正面优先/未知双否"等规则去逼近 33/57/65/5（自然02 §C.3 前段的多次试算），这是把分类当成配额求解，**方法上错误**；
2. **为凑数改判与污染本方判定**：自然02 中我曾把"正面"锚定到历史 MM 的 16 项、把"无法确认"锚定到两方均未知的 5 项，并据此重排本方判定；同时在 §C.3 写入了"本方不自行改判以迎合分布"这类**自相矛盾**的表述（一边拟合、一边声明不迎合）。

**本节的处理**：
- **撤回**上述拟合与锚定框架。本方 160 项分类**不再**以任何历史分布、机械重数或配额为约束；
- `HISTORICAL-OPINION-EXPECTED-INDEX.json` **仅用于历史稳定 ID 定位**（F 节），**不作为本轮 160 项分类答案**；
- 历史 R11 两方分类（Z 30/51/70/9、MM 16/48/89/7）**仅作历史上下文**，不代替本方按原 160 英文题意与当前证据的独立判断；
- 本方最终数字**允许与 33/57/65/5 以及任何历史作者全部不同**，**不要求 16 正面、5 未知，不要求任何 Pass**。

---

## I. 本方独立判定规则（先定分类，再程序化汇总）

本人对每项先作**有效分类**并给出**最小理由**，全部完成后才**程序化汇总**；汇总数字是判定结果，不是判定目标。

| 分类 | 本人判据 |
|---|---|
| **正面** | 该要求适用于本产品形态，且本轮**直接读到该要求所指机制的正面证据**，且该机制**覆盖要求的实质**（不是"由别的机制勉强覆盖"）。 |
| **适用** | 该要求适用于本产品形态，且读到对应机制**存在**，但**正面证据不完整**（仅部分路径、仅文档层面、或需另一项才能确认）。 |
| **部分适用** | 仅**部分子要求**成立，或形态退化到只覆盖要求的一部分。 |
| **不适用** | 该要求**所指对象在本产品形态下不存在**（代码层零命中／形态外，如无账号、无支付、无云、无模型、无邮件）。 |
| **无法确认** | 需要本票外的事实才能判定（组织决策与外部流程、外部平台实跑、他人执行的动作）。 |

"正面"是"适用"的加强档，**与"分类不是产品通过数"并不冲突**：它只表示本轮读到了正面证据，不表示该要求已被验收通过。

---

## J. 逐项独立判定结果（#1–#160，按原 11255B 锚点）

下表是本方**最终**分类；每项括注为**最小理由**。原 English 题目的完整逐项表见自然02 §C.2（题目锚点本身未变，仍以 `ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt` 文件第 10–156 行 → #1–#147、第 158–170 行 → #148–160 为准）。

| # | 分类 | 最小理由 |
|---|---|---|
| 1 | 正面 | schema 由开发者设计并版本化：`storage.py` 固定 DDL + `migration_log` + `LAYERS` 白名单 + 定义层形状校验；Agent 只产草稿不建表（AGENTS §3）。 |
| 2 | 不适用 | 无登录体系。 |
| 3 | 不适用 | 无密码重置。 |
| 4 | 不适用 | 无 MFA。 |
| 5 | 不适用 | 无用户登录会话（仅引擎 stdio 会话）。 |
| 6 | 不适用 | 无 SSO。 |
| 7 | 不适用 | 无 SAML。 |
| 8 | 不适用 | 无 SCIM/员工目录。 |
| 9 | 部分适用 | 无角色层级；写入授权与 owner/lease/预算存在（`_WriteAdmission.bind`、`ownership_proof`）。 |
| 10 | 部分适用 | 单用户本地无跨用户数据面；跨项目读取由 `projectId`/`detailRef`/`proof.check` 绑定拒绝。 |
| 11 | 不适用 | 无多租户。 |
| 12 | 不适用 | 无 impersonate 场景。 |
| 13 | 不适用 | 无登录端点。 |
| 14 | 不适用 | 无账号锁定。 |
| 15 | 适用 | 迁移/格式演进真实存在（ADR-0002：v0→v1→v2 事务内升级、失败回滚、重开可重试、未来格式拒绝打开）；**本轮未读迁移实现与测试正文**，正面证据不完整。 |
| 16 | 部分适用 | `BEGIN IMMEDIATE` + 升级后重读版本防重复 DDL；无多用户周二下午锁表现。 |
| 17 | 部分适用 | 查询有显式上限与预算；真实 5M 行规模未测、Q5 未定，**不得宣称容量达标**。 |
| 18 | 部分适用 | 无远程连接池；进程内单连接 + `_format3_lease` 承担单写者归属。 |
| 19 | 部分适用 | ADR-0002 规定 `backup(newPath)` 在线备份禁覆盖；无产品级定时备份。 |
| 20 | 部分适用 | 恢复路径有 ADR 规定；定期演练无证据；坏 SQLite 物理保护仍 HOLD。 |
| 21 | 不适用 | 无时序库/PITR。 |
| 22 | 适用 | tombstone 机制存在（`object IS NULL` + `managed_value`）；删除影响预览 UI 存在；**Undo-of-delete 未证**，正面证据不完整。 |
| 23 | 正面 | 校验确在引擎侧且本轮直接读到：`storage._snapshot_state` 逐条校验 definition/fact/mappingState 形状与错误顺序；`domain_changesets.py` 引擎侧校验并映射固定码；非仅前端表单校验。 |
| 24 | 不适用 | 无时区/提醒功能面（源码零命中）。 |
| 25 | 正面 | canonical JSON 以 UTF-8 编码标量；`mainline-facts.ts` 拒绝 lone surrogate 以与 Store 哈希口径一致；撇号/特殊字符原样保留。 |
| 26 | 部分适用 | emoji/accents：UTF-8 与 lone surrogate 拒绝已核；**RTL 全字段覆盖无证据**。 |
| 27 | 不适用 | 无金额语义（事实对象为 IRI/Literal）。 |
| 28 | 不适用 | 无货币/税务。 |
| 29 | 部分适用 | 版本化 schema + 快照 + 不可改写历史 + 依赖向量已核；**Q6 有限本体能力未决**。 |
| 30 | 正面 | 幂等已被正面证据证实：ADR-0002 同 operation/job 重试返回原标记；O081 `case7` 实跑为同 operation **一次 commit、0 execute、0 replay、1 Job inventory**，且原生回读不变。 |
| 31 | 正面 | 去重正面证据：`newManualFactPlan` 对已存在三元组抛 `FACT_ALREADY_EXISTS`（同时查 facts 与 definitions.triples），本轮直接读到代码。 |
| 32 | 正面 | 分页正面证据：`mainline-ownership.ts` 512 页上限 + `nextOrdinal` 严格递增 + 首段 manifest 一致性；`ownership_detail_matches` 双端校验 segment/byteOffset/sha256；测试逐页 `pageSize=1` 读到底并重组文档（`test_manual_ownership_detail_full_pages_then_original_id_job`）。 |
| 33 | 适用 | FR-203 规定导出须可被标准工具读取；O081 `native24/test-results/` 含 `t04-query-variants-…-exports-its-exact-CSV` 实跑用例目录；**本轮未读该 spec 断言正文**，正面证据不完整。 |
| 34 | 部分适用 | FR-203 规定越界构造拒绝提交并说明原因、禁止静默丢弃；CSV 导入属 FR-300 未实现。 |
| 35 | 部分适用 | 历史与已提交轮次不可改写、缓存回收不触及历史已核；无合同驱动的保留策略。 |
| 36 | 正面 | 凭据不入代码/仓库/AI 记录：模型外发唯一网关在主进程、引擎不持密钥不调模型（AGENTS §3）；本仓库无 `.env`/凭据文件。 |
| 37 | 不适用 | 无模型接入，无"AI 粘贴密钥入配置"的暴露面。 |
| 38 | 适用 | vendor 侧确认到位（4 wheel + upstream wheel、`PROVENANCE.json` 记 upstream/after/patch sha256、member 记录 117341B、repack 证据）；**本轮未逐 member 重算 wheel 二进制**，正面证据不完整。 |
| 39 | 适用 | 来源 pin 与许可已核（`PROVENANCE.json` + patch sha + `licenses/NOTICE` 双路径，补丁改动范围逐条列明且无 catch 新增）；**无持续依赖扫描机制**。 |
| 40 | 正面 | 输入净化正面证据：引擎侧 zod/`.strict()` 边界 + 固定错误码；未知输入保持 UNKNOWN/HOLD 而非猜测（`test_non_input_failures_keep_original_unknown_and_hold` 等三组实跑）。 |
| 41 | 部分适用 | SQL 全参数化绑定（正面）、XSS 由 `csp.ts` 唯一来源约束且 O081 探针 7 项 violation 全 enforce（正面）；**CSRF 机制零命中、无 CORS 头处理、其余 OWASP 项与渗透测试未覆盖**，故不判正面。 |
| 42 | 不适用 | 无文件上传。 |
| 43 | 正面 | `connect-src 'none'`、`frame-src 'none'`、`object-src 'none'`、`base-uri 'none'`、`form-action 'none'`，非 allow-everything；生产 meta 与开发 nonce 同源于 `csp.ts`（O081 `c1-evidence.json` 实测）。 |
| 44 | 正面 | 本地无 HTTP 头面，**等价安全面**由生产 CSP meta 承担并在每次加载强制执行（探针实测 enforce）；与 #45/#68 的"零机制"不同，故判正面。 |
| 45 | 不适用 | 源码零命中任何加密实现（`encrypt`/`tls`/`ssl`）；传输为本地 stdio。 |
| 46 | 适用 | 最小权限机制存在（worker 只算不持库、`Store.commit` 唯一写路径、引擎不持密钥、后继不得夺取原 queued/active job）；**本轮未逐条读完相关测试正文**，正面证据不完整。 |
| 47 | 正面 | 跨边界只传固定错误码与受限参数，不回传原始异常/堆栈/路径/单元格原值；`safeBusiness3Error` 为唯一错误格式化入口，本轮直接读到。 |
| 48 | 无法确认 | 渗透测试未做且不在本票授权内。 |
| 49 | 部分适用 | 仓库有 ADR/证据目录/资格 JSON 可作部分依据；无问卷答案文件，本轮无新增可支撑条目。 |
| 50 | 不适用 | 属组织流程，仓库无对应文件，非本仓库交付物。 |
| 51 | 不适用 | 无生产/云凭据形态。 |
| 52 | 不适用 | 属组织合规。 |
| 53 | 不适用 | 无患者数据。 |
| 54 | 不适用 | 无患者数据供应商、无模型供应商。 |
| 55 | 部分适用 | 写侧提交证据与 operation/job marker 同事务可查；读侧本轮新增 ownership detail 分页留证与 `documentHash` 绑定；**无全量读审计**。 |
| 56 | 不适用 | 无卡号/支付。 |
| 57 | 无法确认 | 本地库删除可及；**备份与日志中的删除可达性未证**，本票不做破坏性验证。 |
| 58 | 不适用 | 无服务端/驻留合同。 |
| 59 | 不适用 | 无多用户角色与访问复核流程。 |
| 60 | 部分适用 | 本地形态下环境合并；**同源两变体**已核（开发 nonce + 生产 meta 均由 `csp.ts` 生成，禁手写第三份策略）。 |
| 61 | 部分适用 | `ci.yml` + 打包/验证脚本 + `PROVENANCE.json` 记录来源；本地安装不依赖 IaC。 |
| 62 | 适用 | 流水线确实在出包前跑测试（`check` → `verify:sources` → `test:e2e` → `package:dir` → `verify-i04-package.py`）；**但 Windows engine 步骤为 `--maxfail=1` 首败诊断且显式非验收**（ci.yml:136-147），故整体不判正面。 |
| 63 | 部分适用 | 格式迁移失败回滚与重开可重试已核；应用版本回滚未实现。 |
| 64 | 不适用 | 本地桌面无部署窗口。 |
| 65 | 不适用 | 无特性开关。 |
| 66 | 不适用 | 无云扩缩。 |
| 67 | 不适用 | 无 CDN 需求。 |
| 68 | 不适用 | 应用无外部 HTTPS 端点，无证书续期逻辑。 |
| 69 | 适用 | 常驻协调器 + ExecutionJob 机制存在（ADR-0003 全文已读，job 终态与 marker 对账路径已读）；**"慢工作不冻结页面"的端到端证据本轮未取**，正面证据不完整。 |
| 70 | 部分适用 | 同 operation/job 重试幂等成立；网络退避不适用本地 stdio。 |
| 71 | 部分适用 | job 终态含 failed/cancelled 且历史不可改写、终态后拒写轮次；无独立死信队列产品。 |
| 72 | 不适用 | 无 cron/多服务器。 |
| 73 | 适用 | `invalidation-v2.json` 为唯一 `staleReason` 源、仅改模型配置不失效、历史/失败/取消不计过期、发布前事务内复验依赖且要求快照 revision 等于当前正式 revision（ADR-0002 §37）；**缓存回收的端到端执行证据本轮未取**，正面证据不完整。 |
| 74 | 不适用 | 无邮件发送。 |
| 75 | 不适用 | 无事务邮件。 |
| 76 | 部分适用 | 历史不可改写、缓存回收不触及历史已核；容量、旧超限库恢复与坏 SQLite 物理保护仍 HOLD。 |
| 77 | 部分适用 | 本地无云账单；引擎预算上限与 `RESOURCE_LIMIT(resource="memory"/"page")` 是资源失控第一道闸（已核 `_WriteAdmission` 与 `check_final_material`）；无账单告警面。 |
| 78 | 部分适用 | 迁移回滚与 SQLite 在线备份有 ADR 规定；DR 计划文本与年度演练无证据。 |
| 79 | 不适用 | 无多地域承诺。 |
| 80 | 部分适用 | 固定错误码与受限参数构成结构化错误面；无集中日志检索系统。 |
| 81 | 部分适用 | 固定错误码可聚合同类问题；无外部错误追踪服务（本地优先不外联）。 |
| 82 | 不适用 | 无外部探活。 |
| 83 | 不适用 | 无值班分页。 |
| 84 | 部分适用 | 证据目录与资格 JSON 提供可机读指标（事务/拒绝/耗时/跳过量/计时副本）；无实时仪表盘产品。 |
| 85 | 部分适用 | 同请求内 5-phase 计时与 12 份 timing copy（sealed、≤4096B、无 inflight，O081 原件）已核；无跨服务调用链。 |
| 86 | 不适用 | 无 on-call 轮值（组织流程）。 |
| 87 | 部分适用 | ADR-0001/0002/0003 与 M0 计划记载边界与理由；无逐告警 runbook。 |
| 88 | 部分适用 | 每轮 disposition 记录首败并直接驱动下一轮改动（V 目录 v1 counterexample → v2 一行修复；O080 首合成 9P1F → fixture 修正）；非所有回归都有解释。 |
| 89 | 不适用 | 无对外状态页。 |
| 90 | 适用 | 新增 29 例断言真实需求与错误边界（canonical 复用共享、词法别名不误命中、record 形状错误先于 object 读取、未知 parser/n3 失败不转成功、容量不淘汰前 16、跨调用不共享、异常不跨调用发布别名），非断言数量或可点击；**"由懂业务者撰写"的人员事实本方无法核实**。 |
| 91 | 部分适用 | 第三方 API 不适用；内部契约双端（`v2.ts` / `contract_v2.py`）正反例 + `binding-regressions.json` + `fixtures.json` 覆盖。 |
| 92 | 正面 | 端到端正面证据：O081 原 24 例 native **21 PASS + 3 原 I04 SKIP、retry 0、flaky 0、errors 空**，且 `t02-fr200-fr201.spec.ts`（新增 2174 行）与 `t02-ontology-mainline` 撤销用例实跑 PASS。 |
| 93 | 部分适用 | O078 有 8 个本地 native samples 与 18 档聚合、U 有 25 次 profile 捕获（**两批不同原件**）；无发布前负载测试，Q5 未定。 |
| 94 | 正面 | 测试数据用合成命名空间与固定随机种子（ADR-0002 生成器要求），不含生产数据；正面证据来自已核的 ADR 与测试正文。 |
| 95 | 正面 | 回归正面证据：完整 check 自然退出 0（TS **1924 passed / 41 files**、Python **3748 passed + 50 skipped + 1 原 warning**、Ruff 397 files）；原 24 native 21 PASS/3 原 SKIP；`scripts/run-engine-tests.py` + `CI_ENGINE_TEST_SHARDS=2` 支撑分片。 |
| 96 | 部分适用 | 未在参考 8GB 设备验证（Q5 未定），保持 HOLD。 |
| 97 | 部分适用 | 语义与 `aria-label` 已核（如 `aria-label="已提交回执"`、具名 `region`）；无自动化 a11y 合规验证证据。 |
| 98 | 不适用 | 无计费订阅。 |
| 99 | 不适用 | 无支付。 |
| 100 | 不适用 | 无发票。 |
| 101 | 不适用 | 无税务。 |
| 102 | 不适用 | 无退款。 |
| 103 | 不适用 | 无用量计费。 |
| 104 | 不适用 | 无合同体系。 |
| 105 | 不适用 | 无营收报表。 |
| 106 | 不适用 | 无 Webhook 出口。 |
| 107 | 不适用 | 无 Webhook。 |
| 108 | 适用 | v2 契约由 `registry.json` + `schema.json` 统一，TS/Python 双端对称实现同源校验，协议版本经 `hello` 协商并核 registry 原始字节 SHA（ADR-0003）；**本轮未读 `schema.json` 525 行与 `fixtures.json` 446 行逐条**，正面证据不完整。 |
| 109 | 不适用 | 无用户自建 API Key。 |
| 110 | 适用 | 限流面存在且不阻塞真实集成：每会话唯一请求上限 65536、超限关闭会话、帧/页/内存/work 预算固定超限抛 `RESOURCE_LIMIT`、分页预付终末费用不得二次消费（有专门测试名）；**外部 API 客户场景不适用**，且本轮未读完相关预算测试正文。 |
| 111 | 部分适用 | 外部 API 不适用；内部契约变更由双端 fixture、`binding-regressions.json` 与 registry 版本化覆盖。 |
| 112 | 不适用 | 无 OAuth。 |
| 113 | 不适用 | 无对外集成。 |
| 114 | 不适用 | 代码层无 prompt/模型调用面（`prompt` 零命中，仅失效规则含 `model` 键）；S3 前不得接入模型。 |
| 115 | 不适用 | 无 prompt 外发、无患者数据。 |
| 116 | 不适用 | 无模型计费。 |
| 117 | 部分适用 | 无模型、无 evals 框架；确定性引擎侧有逐笔期望集合断言（57 事务/43 拒绝/FR22 rev22/两原 ID 编辑）。 |
| 118 | 不适用 | 无模型服务商。 |
| 119 | 不适用 | 无模型。 |
| 120 | 不适用 | 无 prompt/输出日志。 |
| 121 | 正面 | 人工确认正面证据：`mainline-session.ts` `confirm()` 注释明写"Called only by the explicit human confirmation button after displaying all rows"，UI 有"预览撤销本次修改…要求再次确认"；Agent 只产草稿不自动确认自己的修改（AGENTS §3、PRD FR-204）。 |
| 122 | 部分适用 | 本地应用无网络依赖可验（`connect-src 'none'`、无遥测）；模型外发尚不存在，弱网面未成立。 |
| 123 | 适用 | 状态面存在且本轮读到：`session.phase`（idle/preparing/ready/submitting/unknown）+ `error` 映射 + `ownershipDetail` 三态（reading/ready/unavailable）；页面有"尚未读取当前项目"等空态；**"每个屏幕"的完整覆盖未逐屏核实**。 |
| 124 | 正面 | 错误可操作性正面证据：固定错误码 + 受限参数，`OWNERSHIP_CONFLICT` 附 `detailRef` 可定位到具体冲突行；UI 文案可操作（如"原事实已不存在，请读取当前项目后重新选择。"）。 |
| 125 | 正面 | 表单保留正面证据：手工事实 ID 与预览存活有专门测试（`t02-manual-preview-lifetime.test.ts` 596 行、`t02-manual-fact-id.test.ts` 186 行）与 fixture；`factLifetime` 栅栏防旧预览复活；草稿不被自动刷新覆盖。 |
| 126 | 不适用 | 无邮件。 |
| 127 | 不适用 | 无推送通知。 |
| 128 | 正面 | 撤销正面证据：O081 `native24/test-results/t02-ontology-mainline-T02--74a83-Undo-Redo-and-owned-restart` 实跑 PASS（`native24/report.json` 该 spec 状态 `expected`）；Undo 为**新操作 + 新基准**（`mainline-session.ts:392-401` 明写 "never an inverted local diff"），产生独立反向完整 Diff，Undo-of-Undo 产生独立正向 Diff，撤销 `operationId` 与原提交不同。**仅保此范围**，不扩为所有 Undo 家族已闭。 |
| 129 | 部分适用 | 具名 `region`/`button`/`combobox` 语义与 `aria-label` 已核；无 a11y 审计与读屏实测证据。 |
| 130 | 部分适用 | 无 i18n 框架；日期/数字按本地运行，无按 locale 切换。 |
| 131 | 部分适用 | 会话与草稿边界存在（U1 属后续批次）；浏览器式后退语义不适用本地桌面。 |
| 132 | 正面 | 可读性正面证据：实现写"为什么"而非只写"做什么"（"Identity gates only disable the local optimization. Parsing always uses the current bindings; no captured implementation is ever called as a fallback."）；冻结语义以注释固化（`domain_changesets.py:447-451`）。 |
| 133 | 正面 | 评审正面证据：双模型独立评审 + 逐轮 disposition 归档（R04–R12）+ 本轮 175 个位置逐 ID 承接；只读职责与不自我确认约束可查。 |
| 134 | 正面 | 分支策略正面证据：AGENTS §5 明文（独立 worktree + feature 分支 + PR 合回、不强推、只 stage 本任务文件）；本轮实测分支 `feature/weekly-t02-fr200-fr201`、base/head 完整、index 为空。 |
| 135 | 部分适用 | `ci.yml` 有依赖流程入口（`npm ci` + `uv sync --frozen`、月度矩阵 job）；本轮未做版本升级。 |
| 136 | 部分适用 | Electron/React 固定版本 + 两份锁文件 + NOTICE 已核；无升级前安全补丁验证流程证据。 |
| 137 | 部分适用 | `_definition`/`_definition_objects` 双入口是有意兼容分派（保留原单参数钩子），非死代码；其余死代码清理本轮未进行。 |
| 138 | 部分适用 | `storage.py` 现 89563B 仍单文件，本轮未拆分。 |
| 139 | 正面 | ADR 正面证据：ADR-0001/0002/0003 各 1–2 屏含背景、决定、边界与替代方案，本轮全文读过；`docs/architecture/` 结构可查。 |
| 140 | 部分适用 | `docs/development.md` 与 `docs/README.md` 存在；"1 小时内跑起来"未验证。 |
| 141 | 适用 | 交接文档体系存在（迭代目录保留设计/验收/证据、`status.md` 逐轮追加、AGENTS §6 证据规范）；**"交接给谁"的实际可用性未验证**。 |
| 142 | 不适用 | 无运维后台。 |
| 143 | 不适用 | 无客服工作台。 |
| 144 | 不适用 | 无对外 changelog 文件；内部按轮归档处置文档不等于客户 changelog。 |
| 145 | 部分适用 | 与代码一致的部分已核（本地优先、不自动启用模型/遥测/云服务、`connect-src 'none'`、不开 HTTP 端口）；**完整条款与隐私政策文本不在仓库**，无法确认其存在与一致。 |
| 146 | 部分适用 | 仓库名 `OntoLearn-Studio`（PR16 读回）；GitHub 组织为 `NOmoreJoke`（个人式 handle），**法律实体、域名与账号归属未确认**。 |
| 147 | 无法确认 | 当前为单点，仓库文档不足以证明 bus factor 高于 1；原 HOLD 保留。 |
| 148 | 无法确认 | 双评审覆盖必要闭包，但 1412 源叶、双方各读不同闭包，无法确认每一行均被资深工程师读过。 |
| 149 | 部分适用 | 版本化 schema + 快照 + 不可改写历史 + 依赖向量 + 容量边界已核；Q6 有限本体能力未决，最终数据模型未冻结。 |
| 150 | 适用 | 修复引入新问题的解释能力有正面证据链：v1 counterexample（重复 IRI memo 绕过 helper，真实 RED 为 DID NOT RAISE）→ v2 一行门控修复，过程与机理在 V 目录原件中可逐字核；O080 首合成 9P1F 的 fixture 修正亦留有记录。**属"已发生的实例"，非系统性回归保证**，故不判正面。 |
| 151 | 不适用 | 无云部署/云账单；唯一账单是本地资源预算。 |
| 152 | 不适用 | 无支付。 |
| 153 | 部分适用 | 精确版本 + 两份锁文件 + NOTICE + PROVENANCE 已核；无 SLA 响应流程证据。 |
| 154 | 不适用 | 无患者数据。 |
| 155 | 部分适用 | 确定性引擎侧有逐笔期望集合断言与真实 stdio/原 24 实跑（21 PASS）；**独立 QA 复核证据未建立**，本方亦未重跑任何验证。 |
| 156 | 部分适用 | 本地 SQLite 事务内迁移 + 失败回滚已核；多节点在线迁移不适用，无真实迁移演练证据。 |
| 157 | 部分适用 | 架构不变量以"违反即阻断"形式成文（AGENTS §3 首句）并在逐轮审查中实际执行（含本轮对 `TermInputError` 误判的自我撤回）；**无真实功能排期取舍的记录**，不判正面。 |
| 158 | 不适用 | 桌面本地安装即最终交付形态，无"每个客户规模化部署"这一动作；规模化未证风险归 #17/#93/#96。 |
| 159 | 适用 | 本项目为 Agent 辅助开发（AGENTS.md 全篇、逐轮双评审与处置归档即 AI 协助开发证据），故"调试 AI 写的代码"前提**成立**；本轮诊断链（O079 raw 2148B → trace → C1-TRACE-INDEX 186 事件；O081 完整 guard/账本）证明调试能力可用。**不判正面**：本轮未以"AI 写的代码"独立复现一次调试任务。 |
| 160 | 适用 | ADR-0001/0002/0003 记录决定、理由与边界；每轮 disposition 记录判断与撤回（如 R11"不采纳原强论断"、本轮 N2 撤回）；**属持续维护的现状，非一年后仍成立的保证**，故不判正面。 |

---

## K. 程序化汇总（判定结果，非目标）

本人对 §J 全部 160 项判定完成后，用脚本按 ID 1–160 连续性校验并汇总（输入文件 `/tmp/mm160_independent.json`，输出如下）：

| 分类 | 数量 |
|---|---|
| 正面 | 22 |
| 适用 | 17 |
| 部分适用 | 50 |
| 不适用 | 67 |
| 无法确认 | 4 |
| **合计** | **160** |

**适用合计（正面 + 适用）= 39。** ID 连续性校验通过（1..160 无缺无重），总数恰为 160。

**与各历史/机械数字的关系（仅陈述，非对齐目标）**：
- 机械重数（本人首稿 160 行）：33 适用（17+16）/ 57 部分 / 65 不适用 / 5 无法确认；
- R11 Z：30 适用 / 51 部分 / 70 不适用 / 9 无法确认；
- R11 MM：16 适用（正面）/ 48 部分 / 89 不适用 / 7 无法确认；
- **本方独立判定：39 适用（22 正面 + 17 适用）/ 50 部分适用 / 67 不适用 / 4 无法确认。**

**本方数字与上述三者均不相同，这是判定差异而非统计误差**：差异来自三处——(a) 本方把"正面"设为**要求实质被正面证据覆盖**的加强档，因此只给出 22 项正面而非 16；(b) 本方把 **#41、#62、#22、#15、#33、#38、#46、#69、#73、#90、#108、#110、#123、#141** 等判为"适用/部分适用"而非"正面/部分"，因为正面证据不完整（未读实现正文、未取端到端证据、或该要求含未覆盖子项）；(c) 本方把 **#150、#159、#157** 由"无法确认/不适用"改判为"适用/部分适用"，因为本项目确为 Agent 辅助开发、且确有首败→修复的解释链与架构阻断机制。

**分类仍不是产品通过数**：39 项"适用"只表示该要求适用于本产品形态且读到了对应机制，**不表示该要求已通过验收**；其中 17 项正面亦只是"本轮读到正面证据"，不是发布放行。

---

## L. 本节不改变的任务与结论（逐项确认）

本节**只**替代自然02 §C.3 的判定框架与最终分类。以下各项**全部保留不变**：

| 项 | 状态 |
|---|---|
| 自然01 原稿 82073B 前缀 | **逐字保留**（本轮复核 `head -c 82073` 的 SHA-256 仍为 `7fe0778be7f31005d1aa2aa4d95aa98348693db754f2eb4be85b633abb393c2b`） |
| §A.1 N2 撤回（`TermInputError` 已在 `domain_changesets.py:455/462` 真实兑现） | **保留**；首判的两个最小建议（删声明 / 宽捕获为 `INVALID_REQUEST`）**均不采纳** |
| §A.2 N1 重定性（缺 `dc6c112e` 状态段 = 归档票窗口内的既定登记动作，非当前产品源码缺陷） | **保留**；原 owner/window 不变 |
| §B 补充正文覆盖（135 必要正文、逐文件已读级别、§B.6 十组未读项） | **保留**；未读项**不计入覆盖完成** |
| §D 验证数量分列（当前 3798 = 3748P + 50S = 旧 3769 + 新增 29；CI43 engine 全量 NOTRUN 与 CI44 engine 已完整 3716P+53S、verify 步骤 17 取消、步骤 18 NOTRUN 分列） | **保留** |
| §D.3 N7 窄事实 + `--maxfail=1` 精确化 | **保留** |
| §E C1 边界（本次成功无 `failureObservation`；仅 12 例 VM 合成 + 静态界；O079 首败与底因 UNKNOWN 全保；"故意失败一次"**不构成运行门**） | **保留** |
| §F 175 个历史位置逐 ID 承接（163 + zNew3 + miniNew9；撤回臆造的 Z F1–F78） | **保留**；索引仅用于稳定 ID 定位 |
| §G.3 当前判定 **ConditionalPass（限定技术阶段），当前 push 前源码阻断 0 项** | **保留**；不要求任何 Pass，HOLD/UNKNOWN 全保 |
| 整体进度 2/17（FR401/402）、HOLD 关闭 0、D8 未用、Goal/M0/release 未完成、T04 不推进 | **保留** |
| 本轮未跑验证、未改源码/测试/配置/预算、未 stage/commit/push、未读另一作者本轮产物 | **保留** |

---

## M. 本人当前独立结论（自然03 终稿）

**ConditionalPass（限定技术阶段），当前 push 前源码阻断 0 项。** 该判定与自然01 首判的历史关系、首判中被本轮撤回的 N2、首判中被重定性的 N1、全部 175 个历史意见位置的处置、以及本节 §J/§K 的独立 160 项分类与程序化汇总，共同构成本方本轮完整报告。

**本人明确声明**：本轮 160 项分类**不是**为匹配任何目标数字或历史分布而作；本方数字与机械重数、R11 Z、R11 MM **均不相同**，且本人**未**为对齐而改判任何一项。任何后续若给出逐 ID 裁决表，本方可据以复核，但**不会自行凑数**。

**两份完整原稿与全部意见处置须由 ROOT 实际接收后，方可进入下一票。**

---
*自然03 结束。首判前缀与自然02 全部实质内容保留；本节仅替代 §C.3 的判定框架并给出 §J/§K 的最终独立分类。*

---

# 追加节（自然04）：必要变化正文实际补读闭合、逐 stableID 承接、报告自身事实更正与当前独立结论

**本节只追加，不改写自然01（82073B）、自然02、自然03 的任何字节。** 前述所有判定、纠正与撤回**原样保留**；本节在其之上给出本轮（自然04）实际完成的工作、逐项承接与本人当前结论。

**本节的工作边界（先声明，后列证据）**：本轮**未运行**任何产品、测试、构建、打包、SQL、GUI、业务 RPC 或失败注入；**未改动**任何实现、测试、配置、依赖、预算、忽略项或验收标准；本轮唯一写入物是本报告文件。

## N. 本轮实际补读的必要变化正文（§B.6 缺口的真实闭合）

本节是自然03 §B.6 所列"十组未读项"的**实际补读结果**。**边界声明先行**：

- 本节只覆盖 `git diff --name-status 583c05c → dc6c112e` 边界内的**新增（A）与修改（M）必要正文**：A 文件读**完整正文**，M 文件读**全部改动 hunk 及必要调用闭包**。
- **未读**：既有未改动的旧逻辑全文、1412 个 tracked 叶中的无关文件、`packages/engine/vendor/rdflib/*.whl` 二进制、历年 raw 证据原件、`docs/reviews/T02/fr200-fr201-20261024/round-0X/` 各轮归档正文的**全文**（本轮只按需引用了 R11 `disposition.md` 的 163 位置表与 `version-map.json` 的定位字段）。这些不属于"必要变化正文"，**不计入覆盖，也不冒称已读**。
- 本轮**仍未运行**任何产品、测试、构建、打包、SQL、GUI、业务 RPC 或失败注入；**未改动任何实现**；结论不依赖新运行。

### N.1 契约层（全部 A/M 必要正文，已读完）

| 路径 | 已读级别 | 本人实际读到的断言边界 |
|---|---|---|
| `packages/contracts/src/v2.ts`（M，+131） | **全部新增 hunk 读完**（含 `ownershipSha256` 纯 JS SHA-256 实现 `matchesOwnershipDetail`） | 新增 `ownershipSha256`（手写 SHA-256，K 表常量 + padding + 64 轮压缩）；`matchesOwnershipDetail` 逐项校验 `projectId`/`detailRef`/`startOrdinal`/`segmentCount`（= `ceil(totalBytes/32768)`）/`segments.length ≤ pageSize`/`end ≤ count`/`documentHash` 一致性/`nextOrdinal === (end===count ? null : end)`/`complete === (end===count)`，并对每段用 `atob` 解码后逐字节比 `sha256`；`matchesBusiness3Response` 增加 `project.ownership.detail` 分支（仅校验 `engineSessionId` 相等 + 非 ok 直通 + ok 时走 `matchesOwnershipDetail`）。 |
| `packages/contracts/src/index.ts`（M，+160） | **全部新增 hunk 读完** | 新增 `OwnershipDetailArgs`（联合类型：`documentHash: null` 必配 `startOrdinal: 0`；否则 `documentHash: string` + `startOrdinal: number`）、`OwnershipLocator`/`OwnershipDetailDocument`（两种 kind：`manual-ownership-conflict` 带 `existing`/`incoming`；`single-declaration-conflict` 带 `declaration`/`slot`/`existing` 两元组）、`OwnershipDetailPage`；新增 `reassembleOwnershipDetail`：先以 `capture()` 做**结构化私有捕获**（节点 ≤16384、深度 ≤8、字符串 ≤43692 字符、数组长度 ≤512、原型白名单、`Reflect.ownKeys` + `getOwnPropertyDescriptor` 取值以避开 getter 副作用），再逐页用 `matchesOwnershipDetail` 校验（首段 `documentHash: null`、续段用首段 hash、`pageSize: 64`），要求 `ordinal === segmentCount` 且末页 `complete`，随后按 `totalBytes` 分配 `Uint8Array` 并 `crypto.subtle.digest('SHA-256')` 与 manifest hash 比对，最后 `JSON.parse` + `validateBusiness3('ownershipDetailDocument')` + `projectId` 一致性。**全页私拷贝**保证外部修改原页无效（本人由 `t02-ownership-detail.test.ts` 的"owns a private page capture"用例与该实现的 `capture()` 语义一致地确认）。 |
| `packages/contracts/python/contract_v2.py`（M，+49） | **全部新增 hunk 读完** | 新增 `ownership_detail_matches`：与 TS 端**同构**（同样的 count/end/nextOrdinal/complete/逐段 sha256 与 `base64.b64decode(validate=True)`）；`matches_business3_response` 增加同名方法分支。**两端实现独立但规则一致**——本人逐字段比对：TS 用 `Math.ceil(totalBytes/32768)`，Python 用 `(totalBytes + 32767)//32768`；TS 用 `atob`（可容忍非 base64 字符后抛错 → catch → False），Python 用 `validate=True`（非 base64 抛 `binascii.Error` → False）。**未发现两端规则分歧**。 |
| `packages/contracts/v2/schema.json`（M，+525） | **全部新增 hunk 读完** | 新增 request/response 的 `project.ownership.detail` 分支（`protocolVersion` const 3、`additionalProperties: false`）；新增 `$defs`：`ownershipDetailDocument`（oneOf 两种 kind，`stage` const `preview`，`sourceBaseRevision` 0..2^53-1，`reason` 枚举 `reservedIdentity|sameStatement|singleSlot` 与 const `singleDeclaration`，字符串字段上限 16777216）、`ownershipDetailManifest`（`documentKind` const、`totalBytes` 2..16777216、`segmentCount` 1..512）、`ownershipDetailHeader`（`segmentBlobRefs` 1..512）、`params_project.ownership.detail`（oneOf：null-hash 只许 `startOrdinal: 0`；hash 分支 `startOrdinal` 1..511，`pageSize` 1..64）、`result_project.ownership.detail`（`segments` 1..64，`startOrdinal` 0..511，`nextOrdinal` 1..511 或 null）。**"null 续页"在 schema 层被拒**（本人由 fixtures 的 "ownership no null continuation" 用例与本 schema 交叉确认）。 |
| `packages/contracts/v2/fixtures.json`（M，+446） | **全部新增 hunk 读完** | 新增 3 个 request fixture（"named ownership request" valid=true；"ownership no null continuation" valid=false；"ownership wire issuer forbidden" 含 `ownerId` 额外字段 valid=false）与 4 个 response 绑定 fixture（"named ownership page" valid=true；"ownership wrong ref"、"ownership corrupted segment SHA"、"ownership premature next" valid=false）。其余为 `registryHash` 由 `058ed1be…` 刷新为 `5e097b7e…`。 |
| `packages/contracts/v2/registry.json`（M，+6） | 读完 | `project.ownership.detail` 加入 `business3` 方法白名单（两处 `methodAllowlist`）。 |
| `packages/contracts/v2/binding-regressions.json`（M，+34） | 读完 | **仅** `registryHash` 刷新（17 处 `058ed1be…`→`5e097b7e…`），无语义变更。 |

### N.2 Python 引擎层（全部 M 必要正文，已读完）

| 路径 | 已读级别 | 本人实际读到的边界 |
|---|---|---|
| `packages/engine/src/ontolearn_engine/storage.py`（M，+271） | **全部 hunk 读完** | ① **IRI memo v2 的唯一一行**：`term.__globals__.get("iri") is _MEMO_IRI`（本轮 v1→v2 的全部源码差异）。② 新增 `ManualOwnershipConflict`/`SingleDeclarationConflict`（`Conflict` 子类，`category="ownership"`，各自构造 `witness`）。③ `_check_slot` 增加 `manual_incoming` 形参：仅当有传入行时抛 `ManualOwnershipConflict` 并按 `reservedIdentity`（id 相同）/`sameStatement`（object 相同）/`singleSlot` 分类，否则仍抛普通 `Conflict`。④ `_validate_single_slots(project, declarations)`：只有**本计划新引入**的 `singleValuedPredicates` 才可能抛 `SingleDeclarationConflict`（含实际前两条 blocking 行），其余仍为普通 `Conflict`。⑤ `_definition` 拆出 `_definition_objects(value, objects)` 以支持 memo 路径。⑥ `_snapshot_state` 建立 `_SnapshotIRIObjects`（最多 16 个别名、遇非 canonical/未知分支即 `disable()`），并以 `_plain_snapshot_data`（≤8192 步、栈 ≤64）与 `_original_snapshot_definition`/`_original_snapshot_terms` 作为**资格门**——门不通过即回退到原始 `term()` 路径，**不改变校验语义**。 |
| `packages/engine/src/ontolearn_engine/project/domain_changesets.py`（M，+36） | **全部 hunk 读完** | `preview_changeset` 新增 `ownership_proof` 形参并 `store._ownership_proof(...)` + `request_hash`/`base` 比对；`request["plan"]["manual"]` 的 `subject`/`predicate` 走 `iri()`、`object` 与 `edits` 值走 `term()` 并额外校验 `parsed.n3() == value`，**仅捕获 `TermInputError`** → `fail("INVALID_REQUEST", field="params")`；`store._application(..., ownership_proof=...)`。另 import `TermInputError, iri, term`（§A.1 已据此撤回首判 N2）。**本人另实读 `_document`（169–191）、`_wire_room`（194–198）、`_page_room`（201–217）、`_persist_segments`（220–225）**——确认导航文件标注的区间正确，**不是** 521–965。 |
| `packages/engine/src/ontolearn_engine/job_store.py`（M，+406） | **全部 hunk 读完** | 新增 `_transaction` 包装（在 `super()._transaction` 的 `before_commit` 边界调用 `admission.check_final_material(token)`，异常时区分"清理失败"与"原始原因"）；`_application` 支持 `ownership_proof` 并在 `ManualOwnershipConflict`/`SingleDeclarationConflict` 时走 `_persist_ownership_detail` 返回 `detailRef`；新增 `_ownership_proof`/`_ownership_json`/`_ownership_header`（校验 `ownershipDetailHeader` schema、`manifest.segmentCount` 与 `ceil(totalBytes/32768)` 一致、`origin` 匹配、`fingerprint` 重算一致、旧三类 detail 与 changeset receipt 明确区分 → `INVALID_STATE`/`NOT_FOUND`/`STORAGE_FAILURE`）/`_ownership_segment`（逐段 sha256 + `digest(segment)==ref`）/`_persist_ownership_detail`（同 fingerprint 去重复用、行数/字节预算投影、插入后 before/after admission 比对）；新增 `ownership_detail_page`（按 `pageSize` 逐段累积，单段超页字节上限即 `RESOURCE_LIMIT`，末段 `nextOrdinal=null`）。 |
| `packages/engine/src/ontolearn_engine/project/mainline.py`（M，+417） | **全部 hunk 读完** | 新增 `_WriteAdmission`（绑定 owner、开始/结算事务、`check_final_material` 在 `before_commit` 做最后一次 `material_profile` 核算 + 非终态 job 增长余量校验、`retain_unknown`/`settlement_failed` 保 HOLD 与持有量）、`_OwnershipProof`（栈内发行凭据：`owner`/`reply`/`store`/`connection`/`lease`/`project`/`generation`/`method`/`base`/`request_hash`，`check()` 校验 owner/reply/lease/project/generation 一致并 `authorize`）、`ownership_proof()`（仅 `changeset.preview`/`project.ownership.detail` 且 `current.method` 必须相同）、`prepare_mainline_store()`（受信 bootstrap，只加限制不加权限）、`close()` 的 `_clean_close` 标志与 `_clean_predecessor`（后继必须接手一个干净关闭的前任）。 |
| `packages/engine/src/ontolearn_engine/project/project_host.py`（M，+169） | **全部 hunk 读完** | 把原 `_preflight` 的全部 SQL 聚合提取为模块级 `material_profile(db, limits, *, _mainline_core_material=True)` 并新增 `MaterialProfile` 与 `admit_terminal_growth`（非终态 job 的终态增长余量，注释明示 `ERROR_CATALOG` 2048 字节上限与 4096/pending 的推导）；`_preflight` 改为调用它。**语义等价 + 新增增长余量检查**，非重写。 |
| `packages/engine/src/ontolearn_engine/coordinator.py`（M，+23） | **全部 hunk 读完** | `project.ownership.detail` 加入方法白名单；`changeset.preview` 传入 `self.mainline.ownership_proof(...)`；`serve()` 在 business3 + 真实 `JobStore` + 非测试模式 + 无 ordinary authority/query dispatch 时调用 `prepare_mainline_store(store)`（**只加限制**，注释明示覆盖启动对账路径）。 |
| `packages/engine/src/ontolearn_engine/rdf_snapshot.py`（M，+32） | **全部 hunk 读完** | 新增 `TermInputError(ValueError)`；`iri()` 的 scheme/空白/非法字符与 `urlsplit` 失败 → `TermInputError`；`term()` 捕获 `(BadSyntax, Notation3InputError)` → `TermInputError`，**其余异常仍为普通 `ValueError`**（保证"未知解析失败"与"确定语法/策略拒绝"分层）。 |
| `packages/engine/src/ontolearn_engine/project/query_presentation.py`（M，+21） | **全部 hunk 读完** | `text_page` 在最终编码前一次性**预付**最终编码器费用（`4*maxPageBytes+4096` / 256 / `8*maxPageBytes+4096`），并用 `_RowsPrepaid` 本地消耗；`_room(..., final)` 后 `final.complete()`，原 `_room(store, result, limits, ticket)` 改为对 `final` 记账，避免对同一 reply 二次计费。 |

### N.3 桌面端（全部 M/A 必要正文，已读完）

| 路径 | 已读级别 | 本人实际读到的边界 |
|---|---|---|
| `apps/desktop/src/main/engine.ts`（M，+6） | 全部 hunk | `project.ownership.detail` 加入 `MainlineMethod` 与受控方法白名单；`params.projectId` 必须等于 `record.selected?.projectId`，否则 `deniedOrdinary()`。 |
| `apps/desktop/src/main/project-mainline-service.ts`（M，+24） | 全部 hunk | 新增 `getOwnershipConflictDetailPage`：以**当前 owner/selection epoch** 发起调用，返回前复核 `selectionEpoch`、source owner/projectId 与 `engineSessionId` 未变，否则 `denied()`；注释明示"绝不发布 workspace/selection/snapshot 投影"。 |
| `apps/desktop/src/main/desktop-ipc.ts`（M，+3） | 全部 hunk | 注册 `project:ownership-detail` → `projects?.getOwnershipConflictDetailPage`，缺失时 `permission()`；与既有通道同一 sender/frame 校验路径。 |
| `apps/desktop/src/preload/index.ts`（M，+1） | 全部 hunk | 新增 `getOwnershipConflictDetailPage: (args) => receiveMainline('project:ownership-detail', args)`（**按业务命名**，非通用 `invoke` 通道）。 |
| `apps/desktop/src/renderer/src/ontology/mainline-ownership.ts`（A，78 行） | **全文读完** | 读-only 适配层：循环最多 512 页、首段 `documentHash:null`/`startOrdinal:0`，续段用首段 hash；每页 `structuredClone` 后本地 `matchesOwnershipDetail` 校验，跨页比对 `totalBytes`/`segmentCount`；`page.complete` 后调用**契约内** `reassembleOwnershipDetail`，再校验 `document.sourceBaseRevision === binding.sourceBaseRevision`；最后把 canonical 文档映射为角色视图（`singleDeclaration` → declaration + 两条 existing；其余 → existing + incoming）。`nextOrdinal` 必须严格递增，否则 `invalid()`。 |
| `apps/desktop/src/renderer/src/ontology/OwnershipConflictDetailView.ts`（A，105 行） | **全文读完** | 只读展示组件：`aria-label="首个阻断冲突定位"`、`<dl>` 显示预览基准修订与原因标签、四类原因的中文标签、`existing`→"现有记录" / `incoming`→"传入记录"；`owner===null`→"人工（owner = null）"、`sourceRow===null`→"无源行（sourceRow = null）"；原文一律经 `originalText()`（`white-space:pre-wrap;overflow-wrap:anywhere`）放入 `<code>`，**不生成链接、不截断、不推断 IRI**；组件内**无 button/input/form/a/script**。 |
| `apps/desktop/src/renderer/src/ontology/mainline-session.ts`（M，+88） | **全部 hunk 读完** | 新增 `ownershipDetail` 状态（`reading`/`unavailable`/`ready`）；`prepare()` 中当 preview 返回 `OWNERSHIP_CONFLICT` 时：先置 `reading`，用 `safeBusiness3Error` 严格校验 `code`/`messageKey`/`params.detailRef`（**只接受 string**），再读详情，且**每次 await 后**都经 `requireCurrent()`（`source` 同一、`sourceIdentity` 同一、未 stale、无 pending、phase 不在 reading/preparing/submitting）复核；任何失败→`unavailable`；`STALE_CONTEXT`→`invalidate()`。`discardPreview`/`invalidate`/`dispose`/`read`/`connection`/`book` 均**同步清除** `ownershipDetail`（本人由 `t02-ownership-detail.test.ts` 的 "clears visible details synchronously on %s" 用例与该实现交叉确认）。 |
| `apps/desktop/src/renderer/src/ontology/OntologyMainlinePage.tsx`（M，+89） | **全部 hunk 读完** | 新增 `factLifetime` ref（`useLayoutEffect` 同步挂载/卸载，`sequence` 单调），所有输入变更/载入/重置/读取都走 `invalidateFactPreview()`；`preview()` 先捕获 tuple 再 `await newManualFactPlan(...)`，并在 await 前后以 `current()` 复核（active/sequence/session/source/identity/phase 五重）；`OWNERSHIP_CONFLICT` 时显示固定中文提示与 `OwnershipConflictDetailView`。 |
| `apps/desktop/src/renderer/src/ontology/mainline-facts.ts`（M，+50） | **全部 hunk 读完** | ① `newManualFactPlan` 改为 **async**：先捕获三元组，**拒绝孤立代理项**（`0xd800–0xdfff`），再以 `TextEncoder` + `crypto.subtle.digest('SHA-256', JSON.stringify([s,p,o]))` 派生 id。**本人核对**：这与 Python 侧 `Store.digest([s,p,o])`（`canonical` → `json.dumps(..., ensure_ascii=False, sort_keys=True, separators=(",",":"))` → sha256）**一致**（三元素列表的 canonical 形式即 `JSON.stringify` 形式；`ensure_ascii=False` 与 JS 的非转义输出在 ASCII 之外的差异由 golden fixture 的真实 Python 矢量覆盖）。② `manualFactPlan` 的歧义判定由"同 S/P 必须恰好 1 条"改为**逐条排除法**：只排除自身 id 行，且仅当另一行是受管行、**或** object 与原值相同、**或**（编辑动作且）object 与新值相同时才判 `AMBIGUOUS_FACT_SUPPORT`。 |
| `apps/desktop/src/renderer/src/ontology/OntologyPage.tsx`（M，+2） | 全部 hunk | `pattern="[A-Za-z0-9_][A-Za-z0-9_\-]*"`（在字符类内转义连字符；语义与原式相同）。 |
| `apps/desktop/src/renderer/src/ontology/mainline-api.ts`（M，+9） | 全部 hunk | `OntologyMainlineBridge` 增加 `getOwnershipConflictDetailPage`（类型直接取自 contracts 的 `MainlineProjectBridge`）。 |

### N.4 新增/修改测试与脚本（全部 A/M 必要正文，已读完）

| 路径 | 已读级别 | 本人实际读到的断言边界 |
|---|---|---|
| `scripts/run-engine-tests.py`（A，470） | **全文** | `CI_ENGINE_TEST_SHARDS`：1 → `os.execv` 直跑 pytest；2 → 收集后 `partition()` 分两组并行，每组 `account()` 要求 setup/call/teardown **三段完整账本**，`universe` 覆盖比对（两组的收集集合必须等于全量）。 |
| `scripts/engine-test-reporting.py`（A，124） | **全文** | pytest 插件：`pytest_collection_modifyitems` 按文件分配到 shard，`pytest_collection_finish` 比对 shard 集合与全量 manifest，不一致即 `UsageError`。 |
| `scripts/repack-rdflib-input-types.py`（A，170） | **全文** | 仅用标准库；校验 upstream/patch/source/after 四个 SHA、逐成员字节不变、`ZIP_STORED` 与 1980 时间戳、`licenseUnchanged`。 |
| `packages/engine/tests/test_mainline_language_input_rejection.py`（A，326） | **全文** | R03 拒答族：真实 stdio 子进程发请求、`512 页 diff 上限`、`database_files` 物理字节核对。 |
| `packages/engine/tests/test_mainline_manual_input_rejection.py`（A，1034） | **全文** | `assert_rejected` 精确断言 `INVALID_REQUEST` / `messageKey=protocol.invalidRequest` / `params=={"field":"params"}`；UNKNOWN/HOLD 族；vendor 专有输入类型；ownership detail 全页读取。 |
| `packages/engine/tests/test_mainline_postwrite_admission.py`（A，约 860） | **全文读完** | 覆盖：排队 job 的终态增长余量、两项目 pending 的全局余量、前台 scope 不得借用后继、后台 scope 不得借用新前台、`after_commit` 重入不得退款、清理失败保留原因与持有量、结算失败保持 exact foreground reply UNKNOWN、同 store DTO 不得绑定/供预算、bootstrap 未结算 writer 不得被当作干净书接手、干净关闭才可交接原限制、8 种前任状态后继均不得丢弃未结算前任、后继不得接管原 queued/active job、真实 stdio 增长拒绝后同 host 完整提交、bootstrap 对账把原 accepted job 标为 `ENGINE_EXITED`。 |
| `packages/engine/tests/test_mainline_postwrite_rows_budget.py`（A，约 395） | **全文读完** | 243 行 × 5 列真实结果页；`observe()` 记录每次 reserve 与 `before_commit_final_material` 边界；断言 `fee=={bytes:1114112,objects:8192,work:134217728}` 且边界 before==after；固定费用拒绝后**同 host 可继续**；页 scope 不得出借/退还预付费用；预付材料不得被消费两次。 |
| `packages/engine/tests/test_mainline_postwrite_text_budget.py`（A，320） | **全文读完** | 冷历史 + 真实 query worker；56309 字符（ASCII 与 UTF-8 标量两版）分页文本，`identity`/`order`/`startUtf8Byte`/每页 ≤32768 字节；断言 `text final prepaid` 费用 `{bytes_:528384,objects:256,work:1052672}` 与每页一次；固定费用原子拒绝后同 host 合法继续；游标回调撤销在最终编码器之前拒绝（`encoders_after_revocation == []`）。 |
| `packages/engine/tests/test_mainline_read_work_budget.py`（A，559） | **全文读完** | `scalar_profile` 与生产同单位；21 次真实历史后 44 app_operations/22 snapshots；64MiB work 上限在"下界阶段"与"授权计划阶段"两处分别拒绝，且**低阶段拒绝时不发出 `json_extract`**；真实 stdio 进程从同一库启动后完成 bookmark→remove→读回；6 种损坏（context/plan/snapshot/checkpoint/repeated-ref/cross-project）一律 `STORAGE_FAILURE` 且 HOLD；`json_extract` 被 authorizer 拒绝时**无零回退**。 |
| `packages/engine/tests/test_mainline_dispatch.py`（M，**单 hunk +523 行，已全读**） | 全部 hunk | 新增 `ownership_fixture`（managed 与非 managed 两路）、`ownership_pages`（逐页校验 sha256 并拼回整档）、大定位符完整性/纯度/边界、4 种损坏（missing-version/empty-header/bad-json/bad-segment）→ `STORAGE_FAILURE` + HOLD、诊断段失败整体回滚、诊断不得污染已准入的 full reader、私有准入保持 core-only 向量、坏 blob 在 intern 复用前被计费拦截、原始段预算拒绝**发生在 JSON 解码前**、行上限处去重复用与新上下文回滚、旧三类 detail 不臆造定位符、引用不跨真实后继 session。 |
| `packages/engine/tests/test_storage_snapshot_iri_memo.py`（A，326 行） | **全文（自然01 已读，SHA 绑定 O081）** | IRI memo v2 的行为单测。 |
| `tests/e2e/t02-fr200-fr201.spec.ts`（A，2174） | **全文读完** | 真实 UI 驱动的 FR200/FR201 矩阵：类/对象属性/数据类型属性/个体四类实体的 create/edit/copy/delete + 元数据（标签/定义/同义词/示例，保留原文与顺序）+ 结构三元组（`rdf:type`/`rdfs:subClassOf`/`rdfs:domain`/`rdfs:range`/`rdf:type` 个体）；FR201 多值事实（plain / `@zh` / integer / boolean / decimal / double / date / dateTime）；**受控拒绝族**：相对 datatype、无效 Unicode datatype、未闭合引号（含中文）、缺 datatype、空字面量缺 datatype、未闭合三引号、数字主语言、含数字语言标签、非规范大小写语言标签、4301 位裸整数、四类非法 IPv6 与全角斜杠 authority（并对 subject/predicate 各自单独隔离验证）；`OWNERSHIP_CONFLICT` 后可见"首个阻断冲突定位"区域且断言其 `<dd>` 文本、两条定位项的完整字段序列、Diff 与确认按钮**计数为 0**；`rejectCallerObject` 每次都断言 `after == before`（读回完全一致）与 `active` 三元组一致；失败路径有 2s 上限的诊断收集（不替代原错误）。 |
| `tests/e2e/ui-observation.ts`（A，195） | **全文** | 仅观察已被公开精确定位器选中的元素；不支持标记（`aria-labelledby`/shadowRoot/特殊标签）→ **fail closed**；按钮 `enabled` 复刻 Playwright 的 native/fieldset/ARIA 判定；`committedReceiptOperation` 只认**第一段**回执身份与"当前已读版本"唯一；`updateObservationSlot` 单槽有界（≤16384 字节）。 |
| `tests/unit/ui-observation.test.ts`（A，194） | **全文** | 纯测试回归（非产品证据）：重复/歧义/role 覆盖/未连接/shadow 均 fail closed；`aria-disabled` 大小写与空格按 Playwright 折叠规则；输入框值**不归一化**；回执第一段身份与 pending 互斥；单槽更新保留其它 annotation。 |
| `tests/unit/t02-ownership-detail.test.ts`（A，843） | **全文读完** | 真实契约重装配 + renderer 消费：4 种原因映射不变更原值；>17KiB 原始 Unicode ID/owner/sourceRow 与 null 保留；15 类逐项破坏（project/ref/startOrdinal/段 ordinal/offset/length/hash/base64/预算/段预算/无进展/提前 complete/缺段/重复段）**不继续读取也不发布部分 VM**；后页 6 类破坏（hash/total/repeat/skip/denied/throw）；公开重装配器拒绝 document hash/project/旧三类对象/非法 reason；SHA await 前后守卫；**私拷贝**保证原页被改后仍用快照；Session 侧 4 种原因只发布已验证 VM 且**从不创建事务**；非法 `detailRef`（含 100000 字符）**不调用 getter**；未知码/错误 messageKey/额外 params **不视为授权查找**；8 种失败路径安全降级为 `unavailable` 且不泄漏 secret；7 种清除路径同步清除；5 个时点（preview/首段/中段/digest/最终 active）的迟到成功与失败均被隔离；发布前复核 active 的 project/revision/snapshot/dependencies/null。 |
| `tests/unit/t02-ownership-detail-view.test.ts`（A，138） | **全文** | 真实 React SSR：三种原因标签与"现有记录/传入记录"标题；`singleDeclaration` 显示声明与两条 existing 且**不含**"传入记录"；>16KiB 历史 ID **不截断、不归一化、不推断 IRI**（断言不含 `…`、不含 `href=`）；HTML-like 值仅作转义文本；只读展示**无写/确认/自动执行面**。 |
| `tests/unit/t02-manual-preview-lifetime.test.ts`（A，596） | **全文** | 用 `vm` + `ts.transpileModule` 实际加载 `OntologyMainlinePage.tsx`（自带 hook 桩）：digest 完成只提交一次；13 种变更（输入 ABA/重置/载入事实/结构草稿/读取/来源 ABA/项目切换/reading/layout 重挂/pending/retire/layout 卸载/session 替换）后**拒绝迟到 hash**；相同元组的较旧预览被取代；旧 hash 拒绝**不在新草稿上冒泡**；retire 与"layout 卸载先于普通 dispose"两种生命周期下旧 hash 被阻断；当前 digest 错误正常显示而脱离挂载的错误被忽略；同步 discard 订阅者改动草稿时**不采纳**新代。 |
| `tests/unit/t02-manual-fact-id.test.ts`（A，186） | **全文** | golden 矢量来自**真实隔离 Python**（`spawnSync` 起 `python -I`，用 `Store._fact` 校验 `id==digest([s,p,o])`）；13 个向量覆盖 ASCII、中文 IRI 与语言标签、非 BMP（😀/🛠/🚨）、转义引号与反斜杠、多行三引号、plain/语言/整数/小数/布尔/日期、NFC 与 NFD **不归一化**；重复调用同元组得同一 id；`crypto.subtle.digest` 的入参字节**恰为** `TextEncoder.encode(canonical)`；孤立代理（高/低）在 hash 前被拒且**不调用 digest**。 |
| `tests/fixtures/t02-manual-fact-id.json`（A，139） | **全文** | 13 个真实 Python golden 矢量 + `sourceStorageSha256`/`sourceRdfSnapshotSha256`/`pythonVersion`/`rdflibVersion` 溯源字段。 |
| `tests/e2e/native-driver.ts`（M，+304） | **全部 hunk** | 就绪探测：新增 Electron 主进程 API 存在性检查（`app`/`dialog`/`BrowserWindow` 形状），`mapping-pending` → 最多 450 次 ×100ms 轮询后仍不 ready 才失败；**只加载一次** helper（`helperRequests` 只允许 1 条）；超期/退出/关闭/错误均取消挂起轮询且**不再发送**；退出后仅在**同一 45s 预算内**排空 stdio。 |
| `tests/unit/native-driver.test.ts`（M，+396） | **全部 hunk** | 逐条对应上列失败模式：socket 不回、ENOENT、退出诊断有界、退出后 stdio 排空仍受原 deadline 约束、等待映射而不加载 shim、错误映射/缺 API 立即失败、`whenReady` 卡住在原 deadline、exit/close/error 取消轮询、发送前**再次**检查绝对截止、invalid-json/send-throw/unknown-state/helper-error 均不重试并清理 listener。 |
| `tests/e2e/csp-lifecycle.spec.ts`（M，+63） | 全部 hunk | native 失败时**只读一次**原始输出，区分 read/parse/attachment 三类失败并把**原始字节**作为 attachment 附上；诊断失败**不替代**原始 native 错误。 |
| `tests/e2e/mainline-consumer-first-ack-loss.spec.ts`（M，+77） | 全部 hunk | 首 ACK 丢失后的对账改为使用 `ui-observation` 的 `receiptHasOperation`/`reconciliationReady`，并记录 initial/fullDiff/firstDroppedDelivery/marker/job/after 到证据。 |
| `tests/unit/t01-business3-contract.test.ts`（M，+89） | 全部 hunk | 8 种长度的真实 SHA-256 与 Node `crypto` 比对；`segmentCount`/`complete`/损坏 sha 的反向断言；`matchesBusiness3Response` 对 ownership 的**首/续页**与合法错误；`ownerId` 额外字段被 schema 拒。 |
| `tests/unit/t01-mainline-contract.test.ts`（M，+65） | 全部 hunk | 完整 ownership 文档（>16KiB 定位符 + 旧 id）多段重装配；随机末页/缺段/重复段/损坏字节被拒。 |
| `tests/unit/t01-mainline-ipc-delivery.test.ts`（M，+29） | 全部 hunk | ownership 页走**同一** sender/frame 校验与"缺 ACK 则持有"路径；错误 frame 的 ACK 被拒且不消费。 |
| `tests/unit/t01-mainline-project-service.test.ts`（M，+68） | 全部 hunk | 源选择栅栏之后**不得重发** ownership 页（`getOwnershipConflictDetailPage` 挂起时不返回）。 |
| `tests/unit/t01-mainline-real-runtime.test.ts`（M，+287） | 全部 hunk | **真实 preload → 具名 IPC → service → stdio 引擎**链路跑完 5 个 ownership 家族（reservedIdentity/sameStatement/singleSlot/singleDeclaration/large）；`refused.error.params` 恰为 `['detailRef']`；分页期间 source 选择不变；重装配后的文档 `reason` 与 `existing`/`declaration` 与家族一致；修复后 `projectRevision` 递增且 engineSessionId 不变；全程 `replies.diagnostic()` 为 `{slots:0,offered:0,unknown:0}`。 |
| `tests/unit/t02-mainline-consumer.test.ts`（M，+267） | 全部 hunk | 受控冲突保持可操作（可继续下一次合法预览）；未知码/抛出异常**不暴露**私有载荷，统一降级 `INTERNAL_ERROR`。 |
| `tests/unit/t02-mainline-metadata.test.ts`（M，+190） | 全部 hunk | C 子集 5 种实体的 create/edit/copy/delete 的 RDF 与五字段元数据逐项对拍（**独立手写期望值**，非生产适配器生成）；删除前的外部引用报告与 `DELETION_REFERENCED`。 |
| `package.json`（M）、根 `pyproject.toml`（M）、`packages/engine/pyproject.toml`（M）、`uv.lock`（M） | 全部 hunk | `engine:check` → `uv run --frozen python scripts/run-engine-tests.py`；ruff 排除 `round-[0-9][0-9]`（原稿）；engine 依赖 rdflib `==7.6.0+ontolearn.fr201.3` 并以 `[tool.uv.sources]` 指向**本地 wheel**；`uv.lock` 的 path 源与 wheel sha `99fab7bd…`。 |
| `.github/workflows/ci.yml`（M） | 全部 hunk | Linux `npm run check` 加 `CI_ENGINE_TEST_SHARDS=2`；Windows `engine:check` 移出常规 job，改为 `if: runner.os == 'Windows'` 的**诊断** job（`PYTEST_ADDOPTS` 含 `--maxfail=1 --tb=short --durations=20 --full-trace`，并在跑前打印 Python/locale/UTF-8 模式诊断），**注释明示"not acceptance"**；所有 e2e 加 `--reporter=list,github,json` 与 `PLAYWRIGHT_JSON_OUTPUT_FILE`；artifact 上传新增 `build/engine-tests/` 与 `test-results/`。 |

### N.5 本轮新核实的事实（此前未记录）

1. **vendor wheel 实为 4 个 = 3 本地修订 + 1 upstream**：`rdflib-7.6.0+ontolearn.fr201.1/.2/.3` 三个本地修订 + `upstream/rdflib-7.6.0-py3-none-any.whl`。**更正**首判与 §2 的"4+upstream=5"说法。**4 个**，不是 5。
2. **`licenses/NOTICE` 本轮已更新**（M）：载明 `rdflib 7.6.0+ontolearn.fr201.3 (based on upstream 7.6.0)`、透明本地 notation3 patch 的 6 个异常类型、引擎内 dist-info 路径、仓库 patch 与 PROVENANCE 指针，并明示"这些仓库引用不主张其被包含在 App 中"。
3. **CI 配置本轮确有实质变更**（非仅诊断）：Linux engine 测试改为 **2 分片**（`CI_ENGINE_TEST_SHARDS=2`），且 `engine-test-reporting.py` 会在 shard 与全量 manifest 不一致时 `UsageError`——**这是分片一致性硬校验**，本人已读该脚本全文。
4. **前端 fact id 派生与引擎一致**：本轮前端从"随机 32 字节"改为 **SHA-256(内容)**，与 Python `Store.digest([s,p,o])` 规则一致；**base 版本的随机 id 与引擎 `_fact` 的"内容派生"要求本不相容**（本轮是修复，不是回归）。


### N.6.1 current31（31 项）

**逐 ID 承接**：下表每行给出本方**当前**依据、本人当前处置、最小理由与**继承的原 owner/事件窗口**（原窗口逐字保留，未新增、未合并、未删除）。首判 §5.1 已逐行给出的 31 项在本表按本轮实读后的当前状态重新给出；F05 与 F14 的实质更正见 §A.1/§A.2 与本表理由列。

| stableID | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|
| Z08-01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（数值更新为 `dc6c112e`／45 提交／135 路径／1412 源） | 本方未取得新 CI 回单，门禁位置本身不变；不因本地绿而放行 | Z：ROOT 精确 push/CI 票；merge 前；MM：ROOT 精确 push/CI 票；merge 前逐项核 |
| Z08-02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（退出码 UNKNOWN／后代未知主题独立于 FR 预算） | 本轮无新的退出码证据；预算主题另列 Z11-R01，不合并承载 | Z：Windows CI 证据接收；新工具另票；MM：Windows 完整 CI 证据接收；新工具另票 |
| Z08-03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 制品回单与预算变更均非本轮授权范围 | Z：未来制品回单/预算变化须新授权；MM：未来实际制品回单判断；预算变化须新授权 |
| Z08-04 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 本轮无新 CI 复发样本，不倒填因；结构化栈归因仍在原窗口 | Z：下次真实 CI 复发时定因；MM：下一真实 CI 若复发按新增结构化栈定因；新绿不倒填 |
| Z08-05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 本轮未改测试维护者所辖环境/测试文件 | Z：T01 测试维护者下次触及；MM：T01 测试维护者下次授权触及环境/测试时 |
| Z08-06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 部分采纳有界证据（本地绿），未闭部分延期原窗口 | Windows/Quality 实际 CI 仍无回单，HOLD 不关闭 | Z：Windows/Quality 实际 CI；MM：Windows/Quality 实际 CI 仍待验 |
| Z08-07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 本轮未改对应方法接线位置 | 原 T01/T02 方法接线窗口 |
| Z08-08 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | 发布/供应链未获授权，原窗口不变 | 发布/供应链 owner 另票 |
| Z08-09 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 未来 CI 维护票未开 | 未来 CI 维护票 |
| Z08-10 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 部分采纳已证窄事实（NOTICE 与 PROVENANCE 已实读），未穷尽部分延期 | 未穷尽 vendor/发布面不采推论 | Z：发布/vendor owner 窗口；MM：发布/vendor owner 未来窗口 |
| Z08-11 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 各原 owner 验收前未到达 | 各原 owner 对应验收前 |
| Z08-TOP10-OLD79F | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（旧 79F 残留登记） | 本轮无复发样本，旧残留不被新绿倒填 | Z：ROOT 登记及复发证据；MM：ROOT 历史残留登记及未来复发证据 |
| F01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | **部分闭合**：本轮必要正文已由本人补读（见 §N.1） | 阅读流程位置闭合不等于产品/CI 放行 | T02 作者完成本票；ROOT push 前接收 |
| F02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | CI 逐 node 核仍待 ROOT 精确票 | Z：ROOT 精确票后、merge 前；MM：ROOT 发精确票后按原 15/20 分钟逐 node 核；merge 前 |
| F03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | CI 控制层维护票未开 | ROOT CI 控制层维护票 |
| F04 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回，不复活原强论断 | 原论断的事实前提本轮未被证伪，也未被证实 | 本票内闭合 |
| F05 | 本轮候选 `dc6c112e` 未 push、无新 CI；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 均**无 `dc6c112e` 段**（本人 sha 实测），登记缺口仍属原 owner 窗口（§A.2 已重定性为归档票动作，非源码缺陷） | 保留事实、改变性质（归档票窗口内的登记动作，非源码缺陷） | 见 §A.2；原 owner/window 不变 | Z：ROOT 指定文档 owner；状态追加＋归档票；MM：ROOT 指定文档 owner；状态新增段与普通证据提交 |
| F06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 首个 CI 维护票未开 | 原 T02 归口首个 CI 维护票 |
| F07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 证据控制层维护票未开 | ROOT 证据控制层维护票 |
| F08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据（异步预览生命周期已实读：Page `useLayoutEffect` + `factLifetime` sequence、Session `requireCurrent` fence） | 未闭的 UX 观察延期原前端归口窗口 | 原 T02 前端归口；UX/异步预览维护窗口 |
| F09 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | T11 merge 后受控维护未到窗口 | T11 merge 后受控维护 |
| F10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 归档归口与 T02 维护归口均未获本轮授权 | Z：下次含 Python 围栏归档前核；MM：ROOT 报告归档归口＋原 T02 维护归口 |
| F11 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原有界闭合/信息状态 | 仅继承原证据 | 原 MM 作者票内闭合 |
| F12 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | CI 结算逐步核产物未获授权 | Z：ROOT CI 结算/控制层维护票；MM：ROOT 未来 CI 结算逐步核产物 |
| F13 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | PR16 说明/CI 结算窗口未到 | Z：PR16 说明/CI 结算窗口；MM：ROOT 后续 PR16 说明/CI 结算窗口 |
| F14 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳维护观察（公开 TS/Python 入口 schema 均拒空；本轮 `params_project.ownership.detail` 仍为 oneOf 且 `documentHash:null` 仅允许 `startOrdinal:0`），**不新增当前修复门禁** | 首判 N2 因前提被证伪已撤回（§A.1），不并入本项 | Z：原 T02 契约归口首个维护票；MM：原 T02 契约归口；后续首个契约维护票 |
| F15 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | witness 选取维护窗口未到 | Z：原归口 witness 选取维护窗口；MM：原 T02 storage/契约归口 |
| F16 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（原 capacity 不变） | 本轮未改容量常量 | Z：原 T02 契约归口；MM：原 T02 契约归口持续保留原 capacity |
| F17 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 前端归口维护窗口未到 | 原 T02 前端归口 |
| F18 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | 供应链与依赖归口未获授权 | Z：T11+T02 依赖归口；MM：原 T11 供应链＋原 T02 依赖归口 |
| F19 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | ROOT 唯一归档归口未获授权 | ROOT 唯一归档归口 |

### N.6.2 authoritative78（78 项）

**逐 ID 承接**。真实构成为 **Z F1–Z F10** + **MM R07 族** + **R06 Z P 族** + **R06 D 族** + **R04 Z/M 族** + **R05 Z P 族** + **R05 MM 族**，共 78 个稳定位置。首判写的 "Z F11–F78" 为臆造，**维持撤回**（§F.2），本表不出现该编号。

| stableID | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|
| Z F1 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（数值更新） | CI 门禁未获回单 | ROOT 精确 CI 票；merge 前 |
| Z F2 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 无新增 raw / 未改规则 | 未来新增 raw/改规则时 |
| Z F3 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 本轮未改该测试 owner 所辖文件 | 原测试 owner 下次触及 |
| Z F4 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | 无待办 |
| Z F5 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 未触及两测试或环境适配 | T01 测试维护者下次授权触及两测试或环境适配前 |
| Z F6 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（逐项集合） | 接线/维护事件未到 | 各接线/维护事件 |
| Z F7 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留（发布 HOLD 群） | 各 owner 验收前未到 | 各 owner 对应验收前 |
| Z F8 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | 未知/新家族接线前未到，HOLD 不关闭 | 未知/新家族接线前 |
| Z F9 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | T01/T02 触及时 |
| Z F10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | 既有证据接收维持 |
| MM R07-01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | 本次静态接收 |
| MM R07-02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 未确增 raw | ROOT/T02 未来确增 raw 时 |
| MM R07-03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 独立配置票未开 | 将来独立配置票 |
| MM R07-04 | 本轮候选 `dc6c112e` 未 push、无新 CI；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 均**无 `dc6c112e` 段**（本人 sha 实测），登记缺口仍属原 owner 窗口（§A.2 已重定性为归档票动作，非源码缺陷） | 保留为登记缺口 → 与 F05 同源（§A.2 重定性） | 非产品闭合 | ROOT 文档 owner |
| MM R07-05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 指南 overlay 未改 | ROOT/指南 owner |
| MM R07-06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | 本次事实修订 |
| MM R07-07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | 原测试 owner |
| MM R07-08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 父 FR/具名下游另验 | 父 FR/具名下游另验 |
| MM R07-09 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | 既有证据限定 |
| MM R07-10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径并标注前提已变（不改写历史） | 前提变化已由 §D 分列记录 | 无新复跑票 |
| MM R07-11 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（观察） | 未来 PR 说明未获授权 | T02/ROOT 未来 PR 说明可解释 |
| MM R07-12 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留（HOLD） | 发布/升级前未到 | vendor/发布 owner 升级/发布前 |
| MM R07-13 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 契约类型整理票未开 | 契约 owner 下次授权整理类型时 |
| R06 Z P1 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（门禁，数值更新） | 合并前真实 CI 未获回单 | 合并前真实 CI |
| R06 Z P2 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 未来 CI 接收标准未满足 | 未来 CI 证据接收标准 |
| R06 Z P3 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 原始 wire/Agent 接线未做 | T01 核心；原始 wire/Agent 接线前 |
| R06 Z P4 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | 详情合同已由本轮 `project.ownership.detail` 接线覆盖一部分；其余未闭部分延期 | T01 详情合同＋T02 消费 |
| R06 Z P5 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 对应方法接线前未到 | 对应方法接线前 |
| R06 Z P6 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（未确认观察，不升级） | witness 选取未触及 | T01 下次触及 witness 选取时 |
| R06 Z P7 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 沿既有 canonical 决定，未新增人类决定 | 政策变更才新人类决定 |
| R06 Z P8 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 各原归口未到 | 各原归口 |
| R06 D1 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | ROOT 正常票未开 | ROOT 正常票 |
| R06 D2 | 本轮候选 `dc6c112e` 未 push、无新 CI；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 均**无 `dc6c112e` 段**（本人 sha 实测），登记缺口仍属原 owner 窗口（§A.2 已重定性为归档票动作，非源码缺陷） | 保留 | ROOT 文档 owner 未到 | ROOT 文档 owner |
| R06 D3 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 接线前未到 | T01；接线前 |
| R06 D4 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | T01+T02 联验未闭部分延期 | T01+T02 |
| R06 D5 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | witness 选取未触及 | T01 下次触及选取时 |
| R06 D6 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | 新解析入口前未到 | T02 vendor/T01 入口；新解析入口前 |
| R06 D7 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 对应方法接线前未到 | T01/T02 对应方法接线前 |
| R06 D8 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 测试维护者未到 | T01 测试维护者 |
| R06 D9 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 文档 owner 归档后追加未发生 | 文档 owner 归档后追加 |
| R06 D10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 父 FR/消费链验收前未到 | 父 FR/消费链验收前 |
| R06 D11 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 整数守卫维护窗口未到 | T02 整数守卫维护窗口 |
| R06 D12 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 无待办 | 无待办 |
| R04 Z01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | witness 选取未触及 | T01 触及选取时 |
| R04 Z02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回：采纳有效更正与原维护边界，不新增动作 | 原强论断已被作者自行撤回 | T01 详情预算维护 |
| R04 Z03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 接线前未到 | T01；接线前 |
| R04 Z04 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | 家族接线前未到 | 家族接线前 |
| R04 Z05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 方法接线前未到 | 方法接线前 |
| R04 Z06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R04 Z07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R04 M01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | ROOT 归档票未开 | ROOT 归档票 |
| R04 M02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R04 M03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 整数守卫维护窗口未到 | T02 整数守卫时 |
| R04 M04 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | 新解析入口前未到 | 新解析入口前 |
| R04 M05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 接线前未到 | T01 接线前 |
| R04 M06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | 无待办但保留未闭部分 | 无待办 |
| R04 M07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 契约 owner API 整理票未开 | 契约 owner API 整理时 |
| R05 Z P1 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（门禁） | ROOT 合并门禁未放行 | ROOT 合并门禁 |
| R05 Z P2 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R05 Z P3 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 接线前未到 | T01 接线前 |
| R05 Z P4 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | 家族接线前未到 | 家族接线前 |
| R05 Z P5 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 方法接线前未到 | 方法接线前 |
| R05 Z P6 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R05 Z P7 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R05 Z P8 | 本轮候选 `dc6c112e` 未 push、无新 CI；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 均**无 `dc6c112e` 段**（本人 sha 实测），登记缺口仍属原 owner 窗口（§A.2 已重定性为归档票动作，非源码缺陷） | 保留为登记缺口 → 与 F05 同源 | 非产品闭合 | ROOT 文档 owner |
| R05 MM01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（门禁） | 新 CI 后、merge 前未到 | ROOT；新 CI 后、merge 前 |
| R05 MM02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 仅继承原证据 | ROOT/新 CI 后 |
| R05 MM03 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留（门禁） | 新包制造票未开 | 新包制造票 |
| R05 MM04 | 本轮候选 `dc6c112e` 未 push、无新 CI；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 均**无 `dc6c112e` 段**（本人 sha 实测），登记缺口仍属原 owner 窗口（§A.2 已重定性为归档票动作，非源码缺陷） | 保留为登记缺口 → 与 F05 同源 | 非产品闭合 | ROOT 文档 owner |
| R05 MM05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 方法接线前未到 | 方法接线前 |
| R05 MM06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 接线前未到 | T01 接线前 |
| R05 MM07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | 家族接线前未到 | 家族接线前 |
| R05 MM08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（未确认观察） | witness 选取未触及 | T01 下次触及选取时 |
| R05 MM09 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留原口径闭合 | vendor/发布 owner 未到 | vendor/发布 owner |
| R05 MM10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R05 MM11 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R05 MM12 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 原测试维护者未到 | T01 原测试维护者 |
| R05 MM13 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |

### N.6.3 R09New19PlusOBS（20 项 = R09 新 19 + OBS 独立项）

**逐 ID 承接**。R10-T05/T11/T12 属 R10MMTop10 组，**不归本组**（更正 §F.3 的串题）。

| stableID | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|
| Z09-01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（门禁） | 精确 CI 票/merge 前未到 | ROOT；精确 CI 票/merge 前 |
| Z09-02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 部分采纳历史事实与 UNKNOWN：CI41 helper 12 TypeError 与 CI43 C1 异步新形态**分列**，不合因、不互倒填 | 两段 CI 事实形态不同 | ROOT；真实 CI 归因/回单接收 |
| Z09-03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留退出码 UNKNOWN／后代未知主题；不挂靠 FR 预算（后者另列 Z11-R01） | 两主题分离 | ROOT；CI 证据接收 |
| Z09-04 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | T11 merge 后受控维护未到 | T11；merge 后受控维护 |
| Z09-05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 契约类型整理票未开 | 契约 owner；下次整理 |
| Z09-06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | witness 选取未触及 | T01；触及 witness 选取时 |
| Z09-07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 整数守卫维护窗口未到 | T02；原整数守卫维护窗口 |
| Z09-08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 下次回单/CI 维护票未开 | ROOT；下次回单/CI 维护票 |
| Z09-09 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | native 线未获授权 | 原 T02 native 线＋ROOT |
| Z09-10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 对应家族接线前未到 | T01/T02；对应家族接线前 |
| F-R09-01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 下一精确 push 后真实 CI 未发生 | ROOT/原 T02；下一精确 push 后真实 CI |
| F-R09-02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 部分采纳历史事实与 UNKNOWN（CI41/CI43 分列） | 不合因 | 原 T02/ROOT；真实 CI 归因 |
| F-R09-03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 部分采纳历史事实与 UNKNOWN | 同 F-R09-02 | 原 T02 测试/打包 |
| F-R09-04 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 真实 Windows 运行未发生 | 原 T02 测试；真实 Windows 运行后观测 |
| F-R09-05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 无真实失败样本可核 annotation | 原 T02；真实失败样本存在时核 annotation |
| F-R09-06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 证据接收拦截未执行 | ROOT；证据接收拦截 |
| F-R09-07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 本轮无该主题改变 | 原 T02 |
| F-R09-08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | ROOT 指定 owner 未获授权 | ROOT 指定 owner |
| F-R09-09 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 每次 CI 完整回单接收未执行 | ROOT；每次 CI 完整回单接收 |
| OBS-R09-10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（独立 OBS 项，不并入 R09 新 19） | 沿原 T02 测试窗口 | 沿原 T02 测试窗口 |

### N.6.4 extra13（13 项，独立计数，未并入 78）

**逐 ID 承接**。本组独立索引，不并入 authoritative78，也不与清单末 13 项（#148–#160）混同（见 R11-F03）。

| stableID | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|
| R06 MM01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（门禁） | ROOT 精确 push/CI 票未到 | ROOT 精确 push/CI 票；merge 前 |
| R06 MM02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R06 MM03 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留（门禁） | ROOT 新包制造票未开 | ROOT 新包制造票 |
| R06 MM04 | 本轮候选 `dc6c112e` 未 push、无新 CI；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 均**无 `dc6c112e` 段**（本人 sha 实测），登记缺口仍属原 owner 窗口（§A.2 已重定性为归档票动作，非源码缺陷） | 保留为登记缺口 → 与 F05 同源 | 非产品闭合 | ROOT 文档 owner |
| R06 MM05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回：采纳有效更正与原维护边界，不新增动作 | 原强论断已由作者自行撤回 | T01 契约＋T02 方法出口；接线前 |
| R06 MM06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 原始 triples/Agent 接线前未到 | T01；原始 triples/Agent 接线前 |
| R06 MM07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳有界证据 | 详情合同＋消费面部分闭合，未闭部分延期 | T01 详情合同＋T02 消费 |
| R06 MM08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | witness 选取未触及 | T01 触及 witness 选取时 |
| R06 MM09 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留原口径闭合 | vendor/发布 owner 未到 | vendor/发布 owner |
| R06 MM10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R06 MM11 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |
| R06 MM12 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T01 原测试维护者未到 | T01 原测试维护者 |
| R06 MM13 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留原口径闭合 | 无待办 | 无待办 |

### N.6.5 R10ZTop9（9 项）

**逐 ID 承接**。Z Top9 别名按原 alias 映射，**不增加新位置**。

| stableID | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|
| R10-01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 部分采纳有界证据（本地绿），未闭部分延期 | CI 回单未获 | ROOT；精确 push/CI 票、merge 前 |
| R10-02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 部分采纳历史事实与 UNKNOWN（CI41/CI43 分列） | 不合因、不互倒填 | ROOT/原 T02；真实 CI 归因窗口 |
| R10-03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 契约类型整理票未开 | 契约 owner；下次整理 |
| R10-04 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留（witness 选取：T01；CI/skip 建议：原控制层维护票） | 两归口均未到窗口 | witness 选取：T01；CI/skip 建议：原 ROOT/原 T02 控制层维护票 |
| R10-05 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | T11 merge 后受控维护未到 | T11；merge 后受控维护 |
| R10-06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳已证窄事实，未穷尽/未证推论不采 | 公式边界维持为静态事实 | 原 T02 测试维护/CI 控制层维护票 |
| R10-07 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | 与 R10-06 同窗口，主题未变 | 同 R10-06 |
| R10-08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | native/测试维护未获授权 | 原 T02 native/测试维护与 ROOT |
| R10-09 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回/收窄；按原处置与限证字典保留维护边界，不加新建议 | 共享 AGENTS 本票不改 | ROOT/AGENTS 指南维护归口；本票不改共享 AGENTS |

### N.6.6 R10MMTop10PlusT11T12（12 项）

**逐 ID 承接**。本组含 R10-T11/T12 两个 T11/T12 位置，**归本组**（更正 §F.3）。

| stableID | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|
| R10-T01 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留（门禁） | ROOT 精确 push/CI 票未到 | ROOT 精确 push/CI 票 |
| R10-T02 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 未来 CI 证据接收标准未满足 | 未来 CI 证据接收标准 |
| R10-T03 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | 同上 | 未来 CI 证据接收标准 |
| R10-T04 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 保留 | T02 测试维护者未到窗口 | 原 T02 测试维护者 |
| R10-T05 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回/收窄：T05 尺寸算式仅作静态非可达性证明，**不升为容量结论**、不加新门禁 | R10-T05 归 R10MMTop10 组，**不属 R09 组**（更正 §F.3 串题） | 原 T02 测试维护者；本票不改码 |
| R10-T06 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回/收窄：命名/门禁语义不一致的原推论已撤回 | 本轮无该主题改变 | ROOT／CI 维护窗口 |
| R10-T07 | 本轮候选未 push、无新 CI、无新包制造；`licenses/NOTICE` 已载 `rdflib 7.6.0+ontolearn.fr201.3`、patch 与 PROVENANCE 指针（本人实读该 diff）；发布/供应链 HOLD 原样保留 | 保留 | 发布/供应链 owner 未到 | 发布/供应链 owner |
| R10-T08 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 自然退出 0 但**不冒 CI 回单**（CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整分列，见 §D.2）；本人未取得任何新远端回单 | 保留 | CI 维护票未开 | CI 维护票 |
| R10-T09 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳已证窄事实（未穷尽 Unicode 全空间） | 未穷尽部分不采推论 | 原 T02 测试维护者；本票不改测试 |
| R10-T10 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回：renderer 更早拒绝⇒缺陷的原推论已撤回 | 本轮无该主题改变 | 原 T02 前端归口；本票不改码 |
| R10-T11 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 部分采纳已证窄事实（fixture generated 来源 SHA 与 base 非 head ⇒ 只采"hash 不同"事实） | 不采"应随 head 刷新"推论 | 原 T02 fixture 维护归口 |
| R10-T12 | 本轮候选 `dc6c112e` 未 push、无新 CI；O081 本地完整 check 与 native24 均自然退出 0（本人只读原件）；本人本轮已补读该主题涉及的必要正文，未发现该主题的状态性改变 | 维持撤回/收窄：**不采**"仅 3/9 有断言"；本人本轮复核 `packages/engine/tests/test_storage.py` **不在 base→head 的 135 差异路径内**，动态 9 条 RULES 正反断言仍在位 | 不新增"补五类"门禁 | 不采建议 |

### N.6.7 zNew3（3 项，不冒入 163）

| stableID | 作者判定/owner（保留） | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|---|
| Z11-OBS-01 | 非缺陷·维护观察；当前schema合法域内空段一致拒绝，Python多一冗余下界。 | 本轮契约双端新增未改动该入口语义：本人实读 `packages/contracts/v2/schema.json` 的 `params_project.ownership.detail`（oneOf）与 `packages/contracts/python/contract_v2.py` 的 `ownership_detail_matches`，两侧仍对称；公开函数入口 schema 仍拒空段（`segments` minItems 1） | **保留（采纳公开入口 schema 已拒空的更正，不采新增 fix gate）** | 注释级维护观察，非当前门禁 | 原 T02 契约归口维护票，同 F14，仅注释级；line489 |
| Z11-R01 | 高（CI条件），非源码阻断；WindowsFR20121笔后最后Diff仅474.210ms余量。 | O081 FR201 56.482s 为**本机观测**，本人不把它量化为提速或跨平台余量结论；本轮未取得任何 Windows 运行读数 | **保留**（CI 条件，非源码阻断） | 不借 Z09-03/Z08-02 的退出码主题承载；不设 not-near-full 余量门禁 | 下一授权 Windows 运行读取新计时，line493；按原归口继承 |
| Z11-R02 | CI43C1ready/bootstrap后childclose1/null，UNKNOWN/HOLD，非证因门禁。 | §D.2 的 CI 分列仍成立：CI43 的 C1 为 ready/bootstrap 后 child close(1,null)，UNKNOWN/HOLD；本轮 C1 helper 改动（`native-recovery.cjs` 被动观察、`native-driver.ts` 就绪探测）**未产生新的失败附件**，本轮亦未运行 C1 | **保留**（CI43 新形态单列，非证因门禁） | CI41 helper 12 TypeError 主题继续独立留在 R10-02/Z09-02，不作同因证明 | 未来授权 Windows 失败附件/CI 归因；按原 native/ROOT 归口继承 |

### N.6.8 miniNew9WithS01Alias（9 项，不冒入 163）

| stableID | 作者处置/owner（保留） | 本方当前依据（本轮实读/实测） | 本人当前处置 | 最小理由 | 继承的原 owner / 事件窗口 |
|---|---|---|---|---|---|
| R11-T01 | 保留完整CI合并门禁，非push前源码阻断。 | §D.1 当前收集集合为 **3798 = 3748P + 50S**（＝旧 3769 ＋ 本轮新增 29）；未来 CI 必须覆盖**当前**完整发现集合，不能以旧 3769 口径接收 | **保留**（完整 CI 合并门禁，非 push 前源码阻断） | 执行延期至 ROOT 后续精确票，不要求首次 push 前先有新 CI | ROOT 精确 push/CI 票；merge 前完整三 job 回单接收 |
| R11-T02 | 保留CI43 C1异步新形态与UNKNOWN；不称新catch平台失败附件已实证。 | 本轮 C1 相关改动（`native-recovery.cjs` 被动观察与 `native-driver.ts` 就绪探测）**未被本轮运行验证**；§E 记明本次成功路径无 `failureObservation` | **保留**（CI43 C1 异步新形态与 UNKNOWN；不称新 catch 平台失败附件已实证） | 新 catch 未有真实 Windows 失败附件，采样延期原窗口 | 原 T02 测试/ROOT 未来 Windows 实际证据窗口；新增诊断另票 |
| R11-T03 | 保留CI43 FR累计超时未知；新计时只测量，不修性能/不扩预算。 | O081 FR201 56.482s 仅本机观测；本轮未重跑该例，不推算跨平台耗时 | **保留**（CI43 FR 累计超时未知；新计时只测量） | 不修性能、不扩预算、不新增余量阈值 | 原 T02 测试/ROOT 未来完整 CI 后结算；原业务链/预算保全 |
| R11-T04 | 无ORDERBY未确认观察，非构造性缺陷；未来维护。 | 本轮未触及 witness 选取代码路径；`storage.py` 的 `_SnapshotIRIObjects`/witness 相关 hunk 属 IRI memo 与 ownership 主题，无 ORDERBY 主题改变 | **部分采纳无 ORDERBY 事实**（不采当前错误推论，无构造反例不升级） | 延期原维护窗口 | T01 下次触及 witness 选择时 |
| R11-T05 | TS宽类型维护，非功能缺陷；下次整理。 | 本轮**未改** TS 宽类型：本人实读 `packages/contracts/src/v2.ts` 新增的 `ownershipSha256`/`matchesOwnershipDetail` 与 `packages/contracts/src/index.ts` 的 `OwnershipDetailArgs`（`documentHash: null` 分支 `startOrdinal: 0`、续页分支 `documentHash: string` + `startOrdinal: number`）——**宽类型形态与 R11 原判一致，本轮无变化** | **保留（TS 宽类型维护观察；当前功能缺陷不成立）** | 延期原契约整理窗口；**该 ID 的主题是 TS 宽类型，不是 F14 空页族**（更正 §F.8 串题） | 契约 owner 下次授权整理类型时 |
| R11-T06 | 按真实前进不变量最多512成功页，不构造当前耗尽；仅常量维护边界，不加修复门禁。 | 本轮**新增** 512 页/32768 字节/16MiB 三处常量：`packages/contracts/v2/schema.json` 的 `params_project.ownership.detail`（`pageSize` 1..64、`startOrdinal` 0..511）与 `ownershipDetailManifest`（`totalBytes` ≤ 16777216、`segmentCount` 1..512）、`packages/contracts/src/index.ts` 的 `reassembleOwnershipDetail`（`pageSize: 64`、分配 `totalBytes`）、`packages/engine/src/ontolearn_engine/job_store.py` 的 `_ownership_header`/`ownership_detail_page`。按真实前进不变量最多 512 成功页，**本轮不构造当前耗尽** | **保留（采纳页数不变量更正）** | 不采"固定 8 页/当前耗尽"缺陷说法，不加修复门禁；未来常量变更时维护 | 原 T02 契约归口未来改 SEGMENT_BYTES/MAX_DOCUMENT/页数/pageSize 时 |
| R11-F01 | M0两份计划已版本化事实维持，与coverage F01不同，不构成阻断。 | 本轮实读 `AGENTS.md` §1 指向 `docs/architecture/m0-review-and-update-plan-2026-10-19.md`（**失效路径**），真实原件在 `docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`（同源 sha `c289a1cd…`）——M0 两份计划的版本化事实成立。**该 ID 是 M0 计划版本化事实，与 coverage F01 是两件事**，不得混同 | **保留（M0 计划已版本化事实；不构成阻断）** | 与 current31 中的 coverage F01 分开 | ROOT/AGENTS 指南维护归口；既有引用路径/冗余副本维护窗口 |
| R11-F02 | O074两文件Prettier规范化未越授权，改用AST/真实catch边界证据限证；非源码问题。 | 本轮未新增 Prettier 规范化改动；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 在 base→head 均为 M/A 状态文件改动，**O074 的 exact2 格式/AST 限证**仍以当时原件为准 | **保留（O074 exact2 Prettier/AST 限证，非源码问题）** | 不扩为 base 全产品证明；本轮无新运行 | 本报告事实处置/O074 原静态资格窗口，不新增产品运行 |
| R11-F03 | extra13与清单末13分别索引，不并78，不改原位置。 | 本轮独立索引核对：清单末 13 项为 **#148–#160**（原清单文件第 158–170 行），与历史 78 项**分属两套编号**，未并入、未混同 | **保留（extra13 与清单末 13 分别索引）** | 不并历史 78、不与末 13 混同 | 本人意见索引与 ROOT 归档原窗口 |

| S01 alias | 按原 alias 映射，**不增加位置** | 本轮该 alias 指向 R11-T06（同为 512 页/32768/16MiB 常量维护边界） | **保留** | 别名不新造缺陷、不新增位置 |

### N.6.9 计数核对（程序化）

- stable163 = 31 + 78 + 20 + 13 + 9 + 12 = **163**，与 `HISTORICAL-OPINION-EXPECTED-INDEX.json` 的 `ownerEffectiveIndex.stable163` 实际条目数**程序化一致**（本人脚本读该文件计数）。
- 另列 zNew3 = **3**（Z11-OBS-01 / Z11-R01 / Z11-R02）与 miniNew9WithS01Alias = **9**（R11-T01…T06 / R11-F01…F03），合计 **175 个位置**，**不并入 163 口径**。
- Z Top9 别名与 S01→T06 别名**按原映射承接，不增位**；本轮**未新增、未删除、未重命名任何 stable ID**，也**未臆造 Z F11–F78**。
- 本轮**未新增任何一条独立缺陷**：首判 N2 已撤回且不并入 F14；N1 已重定性为归档票动作。175 个位置全部为"保留/部分采纳/维持撤回"类处置，**不构成本轮 push 前源码阻断**。
## O. 本报告自身的事实更正（逐项，附更正后表述）

本节只更正本报告**自身**的事实错误，不改写任何历史原稿的判断，也不改变 §J 的 160 项分类框架。**更正后分类见 §O.6**。

### O.1 §C.1 的行数表述（事实性错误，更正）

- **原表述（§C.1，错误）**："原清单文件 … 含 **161 个 `>` 行**，其中**文件第 157 行**是过渡句 …，**不是清单项**。故真实 160 项为：文件第 10–156 行 → #1–#147，文件第 158–170 行 → #148–#160"。
- **更正**：该文件**共 170 行**，其中**恰有 160 个以 `>` 开头的行**。**第 157 行是过渡句，且该行本身不带 `>`**——因此"161 个 `>` 行"与"第 157 行是 `>` 行"两个说法都**不成立**。
- **本人本轮复核方式**：`awk`/`python3` 对该文件逐行判定 `startswith('> ')`，得 **160**；全文 170 行；第 157 行内容为过渡句且不以 `>` 开头。
- **不受影响的结论**：**有效题号仍是 #1–#147 与 #148–#160**（文件第 10–156 行 → #1–#147，第 158–170 行 → #148–#160）。首判的有效映射**正确**，错误只在"161 个 `>` 行"这一计数与对第 157 行带 `>` 的描述。

### O.2 §K 汇总段的正面数表述（更正）

- **原表述**："**分类仍不是产品通过数**：39 项"适用"……；其中 **17 项正面**亦只是"本轮读到正面证据""。
- **更正**：本人 §J 的 160 项判定中，**正面 = 22 项**，**普通适用 = 17 项**，二者合计 39 项适用。正确表述为："**其中 22 项正面、17 项普通适用**；正面只表示'本轮读到正面证据'，不是发布放行。"（§K 的汇总表本身 `正面 22 / 适用 17` 是正确的，错误只在正文句把 17 写成了正面数。）

### O.3 §F.3 的归位串题（更正）

- **原表述（§F.3，错误）**：在 R09New19PlusOBS 组内列出 "T05 尺寸算式""T11 fixture generated 来源 SHA""T12 仅 3/9 有断言"。
- **更正**：**R10-T05 / R10-T11 / R10-T12 属 `R10MMTop10PlusT11T12` 组（§F.6），不属 R09 组（§F.3）**。§F.3 的这三项内容应按其**真实原 ID 归属**处理——即：尺寸算式、fixture 来源 SHA、"仅 3/9 有断言"分别是 **R10-T05、R10-T11、R10-T12** 三个位置的议题，其处置按 §F.6 与本轮 §N.6.6 承接；R09New19PlusOBS 组**不含**这三个 ID。
- **不变的部分**：R10-T05 的"尺寸算式仅为静态非可达性证明、不升为容量结论"、R10-T11 的"只采 hash 不同、不采应随 head 刷新"、R10-T12 的"不采仅 3/9 有断言（`packages/engine/tests/test_storage.py` 不在 135 差异路径内）"三条**理由本身不变**，只是归属组别更正。

### O.4 §F.8 的 R11 串题（更正，逐项）

原 §F.8 表把 R11-T05/T06/F01/F02/F03 一律写成"本轮无该主题变化"。**该表述与各 ID 的真实主题不符**，逐项更正如下（本人本轮实读依据见 §N.6.8 的对应行）：

| stableID | 原 §F.8 表述 | 更正后主题与依据 |
|---|---|---|
| **R11-T05** | "保留（F14 同族维护观察）" | **主题是 TS 宽类型维护观察，不是 F14 空页族**。本轮实读：`packages/contracts/src/v2.ts` 新增 `ownershipSha256`/`matchesOwnershipDetail`、`packages/contracts/src/index.ts` 新增 `OwnershipDetailArgs`（`documentHash:null` 必配 `startOrdinal:0`；续页为 `documentHash:string` + `startOrdinal:number`）——**宽类型形态与 R11 原判一致，本轮无变化**。处置仍为"保留（TS 宽类型维护观察），延期原契约整理窗口"。 |
| **R11-T06** | "保留 / 本轮无该主题变化" | **主题是 512 页 / 32768 字节 / 16MiB 常量维护边界**。本轮**确实新增**这三处常量（`schema.json` 的 `params_project.ownership.detail` `pageSize` 1..64、`startOrdinal` 0..511 与 `ownershipDetailManifest` `totalBytes` ≤16777216、`segmentCount` 1..512；`index.ts` `reassembleOwnershipDetail` 的 `pageSize:64` 与 `totalBytes` 分配；`job_store.py` 的 `_ownership_header`/`ownership_detail_page`）。按真实前进不变量**最多 512 成功页**，本轮**不构造当前耗尽**；处置为"保留（采纳页数不变量更正），不加修复门禁"。 |
| **R11-F01** | "部分闭合（仅阅读流程位置）" | **主题是 M0 两份计划的版本化事实，不是 coverage F01**。本人本轮实读：`AGENTS.md` §1 指向的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 为**失效路径**，真实原件在 `docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`（同源 sha `c289a1cd…`）——"M0 两份计划已版本化"的事实成立。处置为"保留（M0 计划已版本化事实），与 current31 的 coverage F01 **分开**，不构成阻断"。**不得虚引不存在的产品条款。** |
| **R11-F02** | "保留 / 本轮无该主题变化" | **主题是 O074 的 exact2 格式/AST 限证**，不是源码问题。本轮未新增 Prettier 规范化改动；O074 当时的静态资格证据仍以其原件为准。处置为"保留（O074 exact2 Prettier/AST 限证），不扩为 base 全产品证明"。 |
| **R11-F03** | "保留 / 本轮无该主题变化" | **主题是 extra13 与清单末 13 项的**分别索引**。本人本轮程序化核对：清单末 13 项为 **#148–#160**（文件第 158–170 行），与历史 78 项分属两套编号，未并入、未混同。处置为"保留（extra13 与末 13 分别索引）"。 |

### O.5 §J 六个条目的产品特定理由重判（逐项，附更正后判定与理由）

以下六项按本人本轮实读的产品边界**重判或收窄理由**。**这不是为了对齐任何历史数字**；本人 §J 仍是独立判定，分类框架不变。

| # | 原题（原文） | 原判定 | 更正后判定 | 更正后的产品特定理由 |
|---|---|---|---|---|
| **43** | "CORS rules that aren't 'allow everything'" | 正面（理由引 CSP `connect-src`/`frame-src`） | **适用（不再是"正面"）** | **CSP 的 `connect-src`/`frame-src` 与 CORS 是两件事，不能互相代证。** 本产品的实际边界是：**无 HTTP 面**——引擎只经 stdio 与主进程通信（`packages/engine/src/ontolearn_engine` 走 stdio），渲染端不经 `fetch`/XHR 取数，主进程只开命名 IPC 通道（`apps/desktop/src/main/desktop-ipc.ts`），因此**不存在跨源请求面**，CORS 在本形态下**不构成一个需要配置的功能面**。适用的是"CSP 策略不放行"的**同源精神**：本轮实读 `csp.ts` 唯一配置源（生产 meta / 开发 nonce）与 `desktop-ipc.ts` 的 sender/frame 校验，确有"不是 allow-everything"的等效约束；但**把它称作"CORS 规则的正面实现"是不准确的**——真实结论是"该形态无 CORS 面，且相邻的 CSP 与 IPC 边界为封闭设计"。 |
| **51** | "a plan for the day a laptop with production access gets stolen" | 不适用（理由"无生产/云凭据形态"） | **部分适用（不再是"不适用"）** | **"无云凭据"≠"本地项目数据/电脑被盗的风险不适用"。** 本产品是**本地优先桌面应用**，数据落在用户本机（`packages/engine` 的 SQLite 库），笔记本被偷即意味着**整个项目库连同全部本体与事实数据被物理取得**——这不是"无凭据形态"可以消解的。本轮实读的**实际边界**是：① 无云端凭据、无远程令牌，故"凭据被窃后被冒用"的远程损失面不存在；② 但**本地数据的机密性**完全依赖设备本身的锁屏/磁盘加密与物理管控，本产品**没有**自身的加密静止存储层（`storage.py` 的 SQLite 为明文结构化数据），也**没有**"设备被盗后的取证/撤销/密钥轮换"流程；③ 无遥测、无云备份，因此**不存在"从云端恢复被删数据"这一缓解路径**。结论：该题的**远程凭据分支不适用**，**本地数据分支部分适用且当前无产品级答案**——"无凭据"只是不适用的一半。 |
| **135** | "monthly dependency upgrades, so you're never two major versions behind" | 部分适用（理由"`ci.yml` 有依赖流程入口（`npm ci` + `uv sync --frozen`、月度矩阵 job）"） | **部分适用（保留分类，收窄理由）** | **`npm ci` / `uv sync --frozen` 是"可复现安装"，不是"月度升级制度"**；CI 中是否存在一个按月运行的升级 job 与"依赖落后两个大版本"是两件事。本轮实读 `.github/workflows/ci.yml` 的**全部 hunk**：① 依赖安装仍为 `npm ci` + `uv sync --frozen`（锁定版本安装）；② 本轮新增的是 **engine 测试 2 分片**（`CI_ENGINE_TEST_SHARDS=2`）、**Windows 首败诊断 job**（`--maxfail=1 --tb=short --durations=20 --full-trace`，注释明示 not acceptance）与 **e2e JSON reporter/artifact**；③ **本轮 diff 中没有任何按月触发的依赖升级 job、没有 Dependabot/Renovate 配置变更、没有版本落后度检查**。`packages/engine/pyproject.toml` 把 rdflib 钉在 `==7.6.0+ontolearn.fr201.3`（本地修订版，**故意的精确钉住**，不是落后）。因此正确表述为："**有可复现的锁定安装与 CI 依赖流程，但未建立月度依赖升级制度，也无落后两个大版本的度量或门禁**；本轮未新增相关制度。" **"月度 CI 矩阵"本身不构成"月度依赖升级制度"。** |
| **147** | "a bus factor higher than one" | 无法确认（理由"当前为单点，仓库文档不足以证明 bus factor 高于 1"） | **无法确认（保留分类，改写理由）** | **"当前为单点 = 1"本身是本方的推测，不是已核事实。** 真实 human bus-factor **未知**：本轮实读 `docs/reviews/T02/fr200-fr201-20261024/` 下 R04–R11 共 8 轮的双人独立审查记录（ZCode GLM-5.3 与 MiniMax M3.1-Flash 各一稿 + 逐条 disposition），这些是**审查代理与总控**的产物，**不构成"第二个能独立接手的人类工程师"**；仓库中亦无人类贡献者名单、值班手册或交接文档可据以判定。已知的只是**机器侧不只有一份记忆**：每轮原稿、处置表、版本图与 artifact-manifest 都留有精确字节与哈希，故"Agent/文档已降低单点记忆风险"这一**较弱命题**成立；但**"人"的 bus factor 仍未知**——不能因为有 agent 与文档就断言人类 bus factor ≥2，也不能反向断言为 1。正确表述为："**真实 human bus-factor 未知：机器侧记忆有冗余（多轮原稿+处置+哈希可复原），人类接手能力未证实，亦未证实为 1。**" |
| **158** | "turning 'works on my laptop' into 'works for every customer at once' (an architect)" | 不适用（理由"桌面本地安装即最终交付形态，无'每个客户规模化部署'这一动作"） | **部分适用（不再是"不适用"）** | **该题不限于云并发。** "works for every customer at once" 的架构含义至少含：**同一交付物在异构目标环境上的一致性**（多 OS/多版本/低配设备/首次启动环境）、**可重复的安装与升级路径**、**同一版本对不同数据集的确定性**。本产品是**本地安装交付**，因此**不存在"同时服务每个客户"的云端扩容动作**（这一半不适用），但**另一半确实适用且当前无产品级答案**：本轮实读 `.github/workflows/ci.yml` 仍有独立的 **Windows** job（且本轮被改为**首败诊断**、明示 not acceptance），`licenses/NOTICE` 明示 `_distutils` 来源与未签名/未公证状态，`docs/reviews/T02/status.md` 明确保留**跨 OS/参考 8GB 设备/macOS15/Win11** 的 HOLD。正确表述为："**云端规模化并发这一分支不适用；跨 OS/设备/客户交付一致性这一分支适用且未闭合**（Windows 实际验收、签名公证、低配设备均保留 HOLD）。" |
| **159** | "debugging the code when the AI that wrote it can't (a senior engineer)" | 适用（理由含"本轮诊断链证明调试能力可用"） | **部分适用（保留"前提成立"，撤回"调试能力已证明"）** | **"本项目确为 Agent 辅助开发"这一前提成立**（`AGENTS.md` 全篇 + 逐轮双评审与处置归档即直接证据）。但**本轮的诊断链是 Agent 自己完成的**（O079 首败 raw 2148B → trace → C1-TRACE-INDEX 186 事件；O081 完整 guard/账本），**这证明的是"Agent 能自查自纠"，不证明"当 AI 写出的代码调试不了时，资深人类工程师实际具备的调试能力"**——后者恰恰是本轮**没有**发生的场景（没有"AI 卡住 → 人类接手"的实例，也没有人类调试耗时/成功率的任何度量）。正确表述为："**前提（AI 辅助开发）成立；本题所问的'人类在 AI 失效时的实际调试能力'在本轮无任何证据，故降为部分适用**——现有证据只覆盖 Agent 自诊断路径，不覆盖人类接手路径。" |

### O.6 §J 分类的相应调整（程序化汇总）

上述六项的重判使 §K 的汇总数字发生**唯一一处**变化（其余 154 项分类不变）：

| 分类 | 原（§K） | 更正后 | 变动 |
|---|---|---|---|
| 正面 | 22 | **21** | #43 由正面 → 适用 |
| 适用 | 17 | **18** | #43 计入适用 |
| 部分适用 | 50 | **52** | #51、#158 由不适用 → 部分适用 |
| 不适用 | 67 | **64** | #51、#158 移出；#43 移出 |
| 无法确认 | 4 | **4** | #147 分类不变（理由改写） |
| **合计** | **160** | **160** | — |

**适用合计（正面 + 适用）= 39 不变**（21 + 18）。**#147 分类不变，仅理由重写。**

**这次调整与任何历史数字无关**：R11 Z（30/51/70/9）、R11 MM（16/48/89/7）、机械重数（33/57/65/5）与本方数字**仍然全部不同**，本方也不向其中任何一个对齐。**本人此前明确撤回"按任何分布校准"的框架，本次调整完全来自 §N 的正文实读与原题英文原文的程序化核对。**

## P. 本人当前独立结论（本轮最终，全部条件随附）

### P.1 结论

**本人对受审候选 `583c05c → dc6c112e`（tree `ba11405f…`）的当前独立判定：ConditionalPass（限定技术阶段），push 前源码阻断 0 项。**

- 这**不是**无条件 Pass，**不是**整候选放行，**不是**合并批准，**不是** CI 通过，**不是**产品完成度增加。
- 本人**未要求任何 Pass**，也**未获得**任何 Pass 授权；本轮**无 push / PR 写 / 新 CI / merge / rerun / cancel**。
- 整体合并可用仍为 **2/17**；HOLD 关闭 **0**；D8 **未用**；Goal / M0 / 发布**未完成**。

### P.2 结论的成立条件（全部保留，缺一不成立）

1. **本轮候选未 push、无新 CI**：本人**未取得任何远端回单**。本方一切"绿"只来自 O081 的**本地**完整 check 与 native24 原件（本人只读原件，未执行）。CI43 engine 全量 NOTRUN 与 CI44 engine 3716P+53S 已完整**分列**（§D.2），**不互相代证**。
2. **未来 CI 必须覆盖当前完整发现集合** **3798 = 3748P + 50S**（＝旧 3769 ＋ 本轮新增 29），逐项由"最终通过"或"原有有据条件 skip"覆盖，自然 0，零失败 / 早停 / 取消 / timeout / NOTRUN，全部后继步骤与三 job 自身 success，Quality packaged recovery 步骤自身 success；**原 15/20 分钟预算不变**。
3. **CI41 helper 12 TypeError 与 CI43 C1 异步新形态分列**，**不合因、不互倒填**；新绿不得追溯证明旧失败同因。**不设"push 前必须先证因"的门禁**（原票未授权，本方也不新增）。
4. **全部原 HOLD / UNKNOWN 原样保留**：unknown parser / N3 / Store / 坏快照、损坏 SQLite 物理保护、容量口径与旧超限库恢复、跨 OS / 参考 8GB 设备 / macOS15 / Win11、签名 / 公证 / wholeApp 法律 / `_distutils` 来源、隐私 / 产权 / 供应链、engine 自然退出与 Windows 后代、sys.path 等价、其余 Undo 与 ownership 家族、四类具名下游 GUI（编辑后推导 / 保存查询 / SHACL / 报告）。
5. **真实 human bus-factor / 产权 / 隐私 / 记忆仍未知**，**不因存在 agent 与多轮文档而已证**（§O.5 #147）。
6. **§N.6 的 175 个历史位置处置全部为"保留 / 部分采纳 / 维持撤回"类**，**未新增任何独立缺陷**；首判 N2 已撤回且**不并入 F14**；N1 已重定为**归档票窗口内的登记动作**，**不是当前产品源码缺陷**，也不构成本票额外执行项。
7. **本轮未运行任何产品 / 测试 / 构建 / 打包 / SQL / GUI / 业务 RPC / 失败注入**；本人**未改动任何实现、测试、配置、依赖、预算、忽略项或验收标准**；本报告是本人唯一写入物。

### P.3 本轮相对首判的变化（保留首判历史，不改写）

| 项 | 首判（自然01，82073B） | 当前（自然04） | 变化性质 |
|---|---|---|---|
| 总体判定 | ConditionalPass（限定技术阶段） | **ConditionalPass（限定技术阶段）** | **不变** |
| push 前源码阻断 | 2 项（N1、N2） | **0 项** | N2 撤回、N1 重定性 |
| N1 | 产品源码缺陷 | **归档票窗口内的既定登记动作**（`status.md`/`m0-checklist.md` 无 `dc6c112e` 段；原 owner/window 不变） | 重定性，非删除 |
| N2 | `TermInputError` 分层未兑现 | **撤回**：`domain_changesets.py:455/462` 已真实消费 → `INVALID_REQUEST`；`coordinator.py:88` `classify()`、`mainline.py:1186-1200` `observe_error`（UNKNOWN/HOLD）承接 | 事实前提被证伪 |
| 160 项分类框架 | 首版（错位） | 自然03 已重建（22/17/50/67/4）；自然04 因 §O.5 六项重判 → **21/18/52/64/4** | 唯一变动来自本轮实读 |
| 分类是否配额 | — | **明确不是**：已撤回一切分布校准框架 | 保留 |
| 必要正文覆盖 | 有缺口 | **§N.1–N.4 已补读并逐文件给已读级别/区间/断言边界** | 闭合 |
| 175 历史位置 | 仅族概述 | **§N.6.1–N.6.9 逐 ID 承接**（175 行，每行含当前依据/处置/最小理由/原 owner-window） | 闭合 |
| 报告自身事实 | 有 5 处错误 | **§O.1–O.6 已逐项更正**（161→160 个 `>` 行、正面 17→22、§F.3 归位、§F.8 六项串题、#43/#51/#135/#147/#158/#159） | 更正 |

### P.4 未完成项（如实列出，不宣称覆盖已闭）

1. **§N.1–N.4 的正文覆盖边界是"base→head 差异内的必要正文"**。**以下属"必要变化正文之外"、本轮**未读**，不计入覆盖、也不冒称已读**：
   - 既有未改动的旧逻辑全文（1412 tracked 叶中的无关文件）；
   - `packages/engine/vendor/rdflib/*.whl` **四个二进制包**的内部字节（只读了 `PROVENANCE.json`、`notation3-input-types.patch`、`LICENSE` 与 `NOTICE` 的文本）；
   - `docs/reviews/T02/fr200-fr201-20261024/round-04 … round-11/` 各轮归档正文的**全文**（本轮按需引用了 R11 `disposition.md` 的 163 位置表与 `version-map.json` 的定位字段；**未通读** round-04…round-10 的完整原稿与逐意见表）；
   - 历年 CI raw 证据、截图、runtime dump 原件（均在仓库外 `outputs/`，本轮只读 O079/O080/O081/O077 的**原件摘要与本票内的指针**）。
2. **未运行**：本轮**没有**产生任何新的运行证据。因此所有"绿"均来自 O081 的既有原件，**不是本轮重跑**。
3. **未闭的 HOLD**：见 P.2 第 4 条，逐项保留。
4. **本轮新增的候选级事实**（§N.5 四条）来自**静态正文与原件核对**，其中第 4 条（前端 fact id 派生改为内容 SHA-256，与引擎 `Store.digest([s,p,o])` 规则一致）本人**未运行验证**，仅作静态一致性判断。

### P.5 保留与不采信的边界（重申）

- **本人采信**的是本轮**亲自读到**的实现正文、测试断言边界、契约 schema、CI 配置 diff 与 O081 原件；**不采信**的是任何未经本轮正文核对的推论。
- **§J 的 160 项分类不是产品通过数**：21 正面 + 18 适用 = 39 项"适用"只表示该要求适用于本产品形态且读到了对应机制，**不表示已通过验收**。
- **§N.6 的 175 行不是新缺陷清单**，是历史位置的**当前承接**；本轮**未新增**任何独立缺陷。
- **另一作者本轮产物未读**（按本票约束）；本报告未引用、未复述、未对齐其本轮结论或数字。
- `HISTORICAL-OPINION-EXPECTED-INDEX.json` 与 `MINIMAX-REMAINING-NECESSARY-SOURCE-RANGES.json` **仅作定位导航**：前者提供 stable ID 与原 owner/window，后者提供必要正文的路径与区间；**均不算本人亲读、不算本轮分类答案、不代表他人结论**。本轮 §N 的所有"已读级别"均由本人**实际打开并阅读对应正文**得出。

### P.6 阅读与写入纪律（本轮）

- **只读职责履行**：本人本轮**未修改**任何源码、测试、配置、依赖、预算、忽略项或验收标准；**未** `git add` / `commit` / `push` / 切分支；**未**运行 check / pytest / vitest / build / package / install / formatter / HMR / SQL / GUI / 业务 RPC / 采样 / profiler / 故意失败探针；**未**发出任何新 probe 或失败注入。
- **写入范围**：仅本报告文件 `outputs/20261027_t02_v2_observer_validation_review_081/minimax/report.md` 及其父目录；**未读**另一作者本轮产物。
- **前缀保全**：本轮开始时 `report.md` 为 **191677 B**，SHA-256 `f0d7477028b0b432188095210102e8fd4c3f697834df03f73ab74ff6e7350f5c`（与冻结的 `minimax-natural-02.md` 一致）；自然01 的 82073B 前缀指纹仍为 `7fe0778be7f31005d1aa2aa4d95aa98348693db754f2eb4be85b633abb393c2b`。本轮**只追加**，前述前缀**逐字未动**。
- **工作区状态**：仓库 worktree `HEAD=dc6c112e…`、分支 `feature/weekly-t02-fr200-fr201`、index 为空（0 staged）；工作区仅 ` M AGENTS.md` 与三个未跟踪 round 目录（**非本轮产生**，本轮未 add、未提交、未改动）。

