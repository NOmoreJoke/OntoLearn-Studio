# T02 FR-200／FR-201 R06 事实核对与修订（MiniMax Code / M3.1-Flash）— 第 2 版

本文件是本方在**同一原 R06 任务、原代码与候选未变**前提下，对已封存原稿所作的**事实修订**，另封为独立版本。**不改写历史原件，不改判，不为取得 Pass。** 原稿全部意见与独立结论继续完整有效。

---

## 0. 修订身份与依据

| 项 | 值 |
|---|---|
| 原稿 | `round-06/minimax-m31flash.md`，68803 B，SHA256 `150bb3cbbf9103a7227ecdfbbd1326335806d69e3fe66ff54c2d768a56892e13`，485 行（本轮核对前后**两次复算一致，未被改动**） |
| 本修订 | `round-06/minimax-m31flash-r2.md`（另封版本） |
| 审查方 | MiniMax Code / MiniMax-M3.1-Flash（订阅既有权益）/ xhigh / 始终授权 |
| 会话 ID | `mvs_e7a25882036e477fa423cd4dd3a5eced`（同原任务） |
| 任务 ID | 仍由操作者从正式 UI 读回；本方不代填 |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` |
| 候选 | base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `831813c60a32155a579a69fc9e2cbc879b8139bb`（tree `944724a8d0e2d03502de3cf6551e0cde97e5e2f4`），31 提交／79 差异叶／1363 tracked 源 |

**边界（与原稿一致）**：只读代码、配置、需求与既有证据；**未运行** npm/check/vitest/pytest/ruff/build/package/install/sync/HMR/GUI，未执行任何产品进程、SQL、probe；未 push/PR/CI/merge；未读本轮另一方报告；**本轮唯一仓库写入是本修订文件**。未新增测试、未新增功能、未要求新增开发。

**修订原则**：只改「源码事实陈述」；**不改**严重度判定本身（除非事实推翻）、不改独立结论、不删除任何原有意见、不把「未证」改写成「已证」。

---

## 1. 逐项事实核对结论

### 核对 1 — D-3：坏 definitions 词法是否真的「预览干净、确认才失败」？

**核对问题**：`domain_changesets.py:470-477` 中 471 先 `transactions.preview`、475 才 `supported`；`project/transactions.py:156-178` 中 162 直接 `store.commit`；`storage.py:726 → _definition:1128-1129` 在预演即抛 `ValueError` —— 那么「预览干净 Diff，确认才失败」是否有实际路径？

**实际源码事实（本轮逐行读回）**

1. `packages/engine/src/ontolearn_engine/project/domain_changesets.py:470-473`
   ```python
   try:
       preview = transactions.preview(internal, base, effective_plan)
   except MetadataError:
       fail("INVALID_REQUEST", field="params")
   ```
   **只捕 `MetadataError`**，不捕 `ValueError`。
2. `packages/engine/src/ontolearn_engine/project/transactions.py:158-178`
   ```python
   with self.store._transaction():
       ...
       self.store.commit(project, base, str(uuid4()), str(uuid4()), **plan)   # 162
       ...
       raise _PreviewRollback                                               # 165
   except _PreviewRollback:
       return ChangePreview(...)                                            # 166-178
   ```
   `store.commit` 在**预览事务内部**真实执行，随后以 `_PreviewRollback` 回滚。
3. `packages/engine/src/ontolearn_engine/storage.py:715-726`（commit 内 definitions 循环）第 **726** 行 `self._definition(definition["value"])`；`storage.py:1128-1129` 对 `term(obj).n3() != obj` 抛 `ValueError("Canonical RDF object required in definition")`。
4. 该 `ValueError` 不是 `Conflict` → `job_store.py:617 except Conflict` 不捕 → 逃出 `preview_changeset` → `coordinator.py:88-108 classify()`：既非 `ServiceFault`/`JobFault`/`Conflict`/`sqlite3.Error` → **`coordinator.py:108` `formatter("INTERNAL_ERROR")`** → `mainline.py:1187-1200 observe_error`（非 `JobFault`/`ServiceFault`）→ `reply.unknown = True`、`self.hold = True` → 之后 `mainline.py:659-663 require_owner` 一律 `fault("STORAGE_FAILURE")`。

**判定：原稿表述不成立，收窄。** 「预览显示干净 Diff、确认提交才失败」**没有实际路径**——坏词法在**预览请求本身内**即以未分类 `ValueError` 失败，并触发会话 HOLD。**不虚构"晚提交分歧"。**

**更正后 D-3 文本（替换原稿 D-3 的机制描述）**

> **D-3【中·产品】`definitions[].value.triples[]` 的坏词法在预览请求内即以未分类 `ValueError` 失败，并 HOLD 引擎会话。**
> 新守卫只覆盖 `manual`/`edits`（`domain_changesets.py:448-465`）；`definitions` 的 triples 由 `storage.py:726 → _definition:1128-1129` 校验，而该校验**发生在预览事务内的 `store.commit`**（`transactions.py:162`）。`domain_changesets.py:472` 只捕 `MetadataError`、`job_store.py:617` 只捕 `Conflict`，故 `ValueError` 逃逸 → `coordinator.py:108` 归为 `INTERNAL_ERROR` → `mainline.py:1187-1200` 置 `hold=True` → 后续调用 `mainline.py:659-663` 一律 `STORAGE_FAILURE`。
> 后果：用户提交含非 canonical 词法的定义三元组时，**预览请求本身失败**（非"预览通过、确认失败"），并使整个引擎会话进入 HOLD，需重启进程/会话恢复。
> 状态：Z-03／M-05／P-3／R05-06 的「早期坏 wire → UNKNOWN/HOLD」既有 OPEN **原样保留**；本条只更正失败发生的时机与调用链，不扩大也不缩小该 OPEN 的范围。

**严重度不变（中）；Top10 序号不变（第 3 位）。**

---

### 核对 2 — D-4：裸 ownership 冲突最终是否是 `INTERNAL_ERROR`？

**核对问题**：`job_store.py:617-636` 对 `Conflict.category == "ownership"` 统一转 `fault(OWNERSHIP_CONFLICT, detailRef)`，裸旧三字段在 636 亦如此；`storage.py` 的 `Conflict.code` 缺 `ownership` 键属类层事实 —— 能否直接推出该业务路径最终 `INTERNAL_ERROR`？

**实际源码事实（本轮逐行读回）**

1. `packages/engine/src/ontolearn_engine/job_store.py:617-636`
   ```python
   except Conflict as error:
       if error.category != "ownership":
           raise
       ...
       if (isinstance(error, (ManualOwnershipConflict, SingleDeclarationConflict))
               and ownership_proof is not None):
           identity = self._persist_ownership_detail(project, error, ownership_proof, hook)
           fault("OWNERSHIP_CONFLICT", detailRef=identity)          # 626-627
       identity = str(uuid4())
       detail = {"category": "ownership", "resource": resource, "projectId": project}
       with self._transaction():
           self._db.execute("INSERT INTO job_details VALUES(?,?,?)", ...)
       fault("OWNERSHIP_CONFLICT", detailRef=identity)              # 630-636（裸旧三字段分支）
   ```
   **两个分支的错误码都是 `OWNERSHIP_CONFLICT`，都不是 `INTERNAL_ERROR`。**
2. `packages/engine/src/ontolearn_engine/storage.py:57-64`：`Conflict.code` 映射表无 `"ownership"` 键 → `.get(category, "INTERNAL_ERROR")`；其**消费点**是 `coordinator.py:94-95` 的 `classify()`：`if isinstance(error, (JobFault, Conflict)): return formatter(error.code, error.params)`。
3. 因此 `INTERNAL_ERROR` 只在**裸 ownership Conflict 逃出 `_application` 包装**直达 `classify()` 时才成立。本轮已核的候选路径**均被 `_application` 包住**：预览路径 `domain_changesets.py:442` `with store._application(project, "plan", hook, ownership_proof=...)`；作业提交路径 `job_store.py:1814` `commit_job` 亦用 `_application`。

**判定：原稿「该业务路径最终 INTERNAL_ERROR」的推论不成立，收窄。**

**更正后 D-4 文本（替换原稿 D-4）**

> **D-4【低-中·产品/UX】裸 ownership 冲突可返回 `OWNERSHIP_CONFLICT`，但其详情定位不可用。**
> `job_store.py:617-636` 把 `category == "ownership"` 的冲突统一转为 `fault("OWNERSHIP_CONFLICT", detailRef=...)`——含 witness 分支（626-627）与裸旧三字段分支（630-636）——**该业务路径最终不是 `INTERNAL_ERROR`**。
> 保留的问题：裸分支落库的是旧三字段 `{"category","resource","projectId"}`，`job_store.py:674-682` 对该形状 `fault("INVALID_STATE")` → 渲染层 `mainline-session.ts` 走 `ownershipDetail.status === 'unavailable'` → 界面显示「冲突详情暂不可用」。即**有 witness 的两类冲突（`ManualOwnershipConflict`、`SingleDeclarationConflict`）可定位，其余 ownership 家族不可定位**。
> 类层事实保留：`storage.py:57-64` 的 `Conflict.code` 映射确无 `"ownership"` 键，若裸 ownership Conflict 逃出 `_application` 直达 `coordinator.py:94-95` 的 `classify()`，才会归为 `INTERNAL_ERROR`；本轮已核路径均被 `_application` 包装，故**只能作为条件性风险保留，不作为当前可达缺陷**。
> 状态：Z-04／P-4／R05-07「部分采纳」维持。

**严重度由「中·产品」下调为「低-中·产品/UX」（错误码误判撤回，详情不可用部分不变）；Top10 内保留但降位。**

---

### 核对 3 — D-6：wheel 无守卫索引点能否推出当前用户可触发？

**核对问题**：`wheel 931/1609` 无边界索引点存在属实，但 `rdf_snapshot.py:37-40` 给 `term` 增加 `<S> <P> {value} .` 封装，不是 standalone EOF 输入。

**实际源码事实（本轮逐行读回）**

1. 已发布 wheel 内 `rdflib/plugins/parsers/notation3.py:931` `while argstr[j] in {"!", "^"}` 与 `:1609` `if argstr[j] == "@"` —— **确无边界守卫**（本轮从 wheel 解包读出上下文，再次确认）。
2. `packages/engine/src/ontolearn_engine/rdf_snapshot.py:36-41`
   ```python
   parsed = Graph().parse(
       data=f"<{subject}> <{predicate}> {value} .",
       format="turtle", publicID="urn:ontolearn:s1:")
   ```
   文档恒以 `" ."` 结尾，解析器在该位置**不构成 standalone EOF**。
3. 引擎内全部 `.parse(` 调用点只有两处：`rdf_snapshot.py:37`（用户输入，经上述封装）与 `storage_probe.py:65`（自生成合成 Turtle fixture `fixture(scale)`，且本轮在 `packages/engine/src/ontolearn_engine/` 内**未找到任何模块 import `storage_probe`**）。`semantic*.py`、`query_presentation.py` 等处只有 `Graph()` 构造，无 `.parse(`。

**判定：原稿把条件性逃逸链当作可达链，收窄。** 本轮**未构造出实际可达反例**，不能宣布当前用户可触发。

**更正后 D-6 文本（替换原稿 D-6）**

> **D-6【保留项·条件性】已发布 vendored wheel 存在两处无边界索引点，但当前用户输入路径不构成 standalone EOF。**
> 事实：`rdflib-7.6.0+ontolearn.fr201.3` 内 `notation3.py:931`／`:1609` 确无边界守卫（本轮解包定位）。
> 收窄：`rdf_snapshot.py:37-41` 把用户值封装为 `<S> <P> {value} .`（恒以 `" ."` 结尾），解析器不会触及 standalone EOF；引擎内另一处 `.parse(` 是 `storage_probe.py:65` 的自生成合成 fixture，且无引擎模块 import 它。**因此本轮未构造出当前用户可触发的反例**，原稿"经 `rdf_snapshot.py:44-45` 变成普通 `ValueError` 后逃逸为 HOLD 后果"**撤回为条件性逃逸链**，不作为当前可达缺陷。
> 保留：与 M-04「standalone EOF 原 OPEN 维持，不外推当前 UI 已有构造反例」的既有处置一致；补丁覆盖缺口（`notation3-input-types.patch` 未覆盖 931／1609）作为**将来新增不经封装解析入口时的条件性风险**保留。

**Top10 第 6 位撤出，降为「保留项」，不删除、不改判为已修。**

---

### 核对 4 — D-2：是「入口需追加当前事实」还是「历史 manifest 伪装当前」？

**核对问题**：`status.md` 含明确「以上 cb8/O029 陈述保留当时快照、不作为当前远端事实」，末节是 aff/R05 当时状态；round-05 manifest 本来身份 aff，不应改写历史原件。

**实际源码事实（本轮逐行读回）**

1. `docs/reviews/T02/status.md:39` 原文：**「本节追加当前状态；以上 cb8／O029 数值与未推送陈述保留为当时快照，不作为当前远端事实。」** —— status.md **自身已声明**历史段落为时点快照。
2. `docs/reviews/T02/fr200-fr201-20261024/round-05/artifact-manifest.json` 的 `reviewedCandidate` 明确绑定 `head aff386f6…`／`tree 2d9b113b…`／`trackedSourceCount 1355`／`baseDiffLeaves 71`／`cumulativeCommits 29` —— 它**就是 aff386f6 的身份索引**，按设计应当保持 aff 身份。
3. 远端事实（本轮 `git ls-remote` 实测）：`refs/heads/feature/weekly-t02-fr200-fr201 = 934bd14f…`，`refs/heads/develop = 583c05c7…`。

**判定：原稿「仓内状态文件称未推送，与远端真实状态相反」「历史 manifest 伪装当前」的措辞过重，收窄。**

**更正后 D-2 文本（替换原稿 D-2）**

> **D-2【低·文档完整性】仓内缺少针对当前 head 831813c6 与 O040 的"当前事实追加节"。**
> 澄清：`docs/reviews/T02/status.md:39` 已明示「以上 cb8／O029 数值与未推送陈述保留为当时快照，不作为当前远端事实」，其末节按设计就是 aff386f6／R05 的当时状态；`round-05/artifact-manifest.json` 的 `reviewedCandidate` 是 aff386f6 的**身份索引**，本应保持 aff 身份，**不改写历史原件**。原稿「与远端真实状态相反」「历史 manifest 伪装当前」的表述**撤回**。
> 保留的真实缺口：本轮 `git ls-remote` 实测远端分支已在 `934bd14f`（`develop` 仍在 `583c05c7`），并已有 run `40171564866` 的真实结论（macOS success、Quality success、Windows failure）；而仓内**尚无任何针对当前 head `831813c6` 与该次远端 CI 的当前事实追加节**。
> 定性：这是**入口需要追加当前事实**，不是历史件失真；按 AGENTS「唯一状态来源」与「完成度只在 `docs/m0-checklist.md` 和对应 `status.md` 中维护」，应由唯一维护者追加，**本轮不代改、不改写历史原件**。

**严重度由「阻断·文档事实错误」下调为「低·文档完整性」（定性更正）；Top10 内保留但降位，且不再是"错误"而是"缺追加"。**

---

### 核对 5 — D-10：是否「完全无失效证据」？附录 C 映射是否每行均「本次未执行」？

**核对问题**：`invalidation-v2.json` 首两规则 ontology/ONTOLOGY_CHANGED、facts/FACTS_CHANGED；`storage.py:875-928` 同事务版本递增及 `_invalidate`，`:1613-1623` 更新 stale/移 current；`test_storage.py:190-223` 九行正负参数例含 ontology —— 这些不能证明全部具体 inference/query/SHACL/report 下游 GUI，但也不能称完全无失效证据。原 C 映射含多行实际 GUI，并非每行均「本次未执行」。

**实际源码事实（本轮逐行读回）**

1. `packages/engine/src/ontolearn_engine/invalidation-v2.json`：9 条规则，第 1 条 `appendixRow 1 / family "ontology" / staleReason "ONTOLOGY_CHANGED"`，第 2 条 `facts / FACTS_CHANGED`，第 9 条 `model / null`。
2. `packages/engine/src/ontolearn_engine/storage.py:905-910`：同一事务内 `family(key)` + `INSERT INTO versions VALUES(?,?,1) ON CONFLICT(project,key) DO UPDATE SET version=version+1`；`:927` `self._invalidate(project)`。
3. `packages/engine/src/ontolearn_engine/storage.py:1611-1622`：`_invalidate` 按 `reasons(json.loads(row["dependencies"]), now)` 重算 `result_state.stale`，`stale` 非空即 `DELETE FROM current_results`。
4. `packages/engine/tests/test_storage.py:190-223` `test_nine_appendix_d_rows_positive_and_negative`：对 9 条规则参数化（含 ontology family）；声明两个 ontology 定义 → 发布依赖 `ontology:one` 的结果与一个无关结果 → 改 `ontology:one` → 断言 `stale == [{"code": "ONTOLOGY_CHANGED", "dependency": "ontology:one", "before": 1, "after": 2}]`，并断言无关结果 `stale == []`，末尾负例 `reasons({key:1},{key:1}) == []`。
5. `docs/reviews/T02/fr200-fr201-20261024/round-05/fr200-fr201-original-clause-evidence-map.md:61-72`：附录 C 映射表中**只有 973（SHACL 模板）、974（受控规则）、975（只读 SELECT/ASK）三行写「本次未执行」**；961、965、966、967/968、969/970、971、972、976/977、979 各行均带实际 GUI 证据或范围语义（如 969/970 行「真实公理 create/edit/copy/delete，结构不制造实例 facts」、972 行「同版四类 zh/en 原文随 CRUD 保存并映射 RDF」）。

**判定：原稿两处表述均过强，收窄。**

**更正后 D-10 文本（替换原稿 D-10）**

> **D-10【中·覆盖】失效联动不是"无证据"，而是"未验到附录 D.2 首行点名的四类下游"。**
> 已有证据（本轮读回）：`invalidation-v2.json` 第 1/2 条规则 `ontology/ONTOLOGY_CHANGED`、`facts/FACTS_CHANGED`；`storage.py:905-910` 同事务版本递增、`:927` `_invalidate`、`:1611-1622` 重算 `stale` 并在 stale 时移出 `current_results`；`packages/engine/tests/test_storage.py:190-223` 对附录 D 九行做正负参数化（ontology family 命中 `ONTOLOGY_CHANGED`，无关键不失效负例成立）。
> 未验部分（保留）：上述为**存储级**依赖键机制；**经 FR-200 界面编辑**是否把附录 D.2 第 994–1000 行首行点名的四类下游（当前推导、保存查询结果、相关 SHACL 结果、相关报告）逐类标记过期，本轮**无证据**。
> 结构性缺口（保留）：round-05 条款映射覆盖 FR-200/201 与附录 C，**附录 D（983-1015）、附录 E（1016-1095）、附录 G（1115+）无映射行**。
> 更正原稿误述：原稿称 round-05 附录 C 映射「每行『实际证据』栏均为『本次未执行』」**不属实**（实读 `:61-72`，仅 973/974/975 三行为「本次未执行」，其余各行均载有实际 GUI 证据或范围语义）。原稿"没有任何证据说明改了它们之后下游结果被正确标记过期"**收窄为**"没有针对 D.2 首行四类下游的经 GUI 证据"。
> **不要求新增测试或功能**；本条只界定已证/未证的边界。

**Top10 内保留（仍属覆盖类缺口），但措辞由"无证据"改为"未验到具体下游"。**

---

### 核对 6 — #39 Dependabot 与 §6 笔误

**核对问题**：请读实际 `.github/dependabot.yml`；Dependabot 版本更新不等同漏洞扫描已通过，分别说明。另核正 §6「931813c6」。

**实际源码事实（本轮读回）**

- `.github/dependabot.yml` **存在**（279 B）：
  ```yaml
  version: 2
  updates:
    - package-ecosystem: npm
      directory: /
      target-branch: develop
      schedule: { interval: weekly }
      open-pull-requests-limit: 5
    - package-ecosystem: github-actions
      directory: /
      target-branch: develop
      schedule: { interval: weekly }
  ```
- `.github/` 下另有 `ISSERTEMPLATE/`、`pull_request_template.md`、`workflows/`；**无** pip/uv 生态条目，**无** 漏洞扫描（security/vulnerability）配置条目。
- 原稿 §6 表格首行写作「**931813c6** 的物理内容」——应为 **831813c6**。

**判定：原稿 #39 与 §6 两处更正成立，采纳。**

**更正后 #39（替换原稿 §8 第 39 行）**

> 39. 部分适用 —— 依赖固定到精确版本且有双锁与 CI `npm ci`/`uv sync --frozen`；**`.github/dependabot.yml` 确实存在**，配置 npm 与 github-actions 两个生态的**每周版本更新**（目标分支 `develop`，单次 PR 上限 5）。**但版本更新 ≠ 漏洞扫描**：该配置**不含** pip/uv 生态（Python 侧依赖与 vendored rdflib 本地 wheel 不在自动更新内），**也不含**任何漏洞扫描条目（Dependabot 的漏洞告警属仓库安全告警设置，不在本文件内）。故"依赖漏洞扫描已配置并通过"**不成立**，"无 Dependabot"**属原稿误述，撤回**；缺口为"无依赖漏洞扫描、Python 生态未纳入自动更新"。

**更正后 §6 首行**：`| O041 … | **831813c6** 的物理内容，但 `headAtExecution = 934bd14f` | …`

---

## 2. 连带更正与未受影响项确认

**连带更正**

1. 原稿 §9 Top10 第 2 位（D-2）依核对 4 降位并改写定性。
2. 原稿 §9 Top10 第 3 位（D-3）依核对 1 更正机制描述（预览内失败，而非预览干净后确认失败）。
3. 原稿 §9 Top10 第 4 位（D-4）依核对 2 下调等级并撤回 `INTERNAL_ERROR` 推论。
4. 原稿 §9 Top10 第 6 位（D-6）依核对 3 撤出 Top10，转入"保留项（条件性）"。
5. 原稿 §9 Top10 第 8 位（D-10）依核对 5 改写措辞。
6. 原稿 §8 第 39 行、§6 首行依核对 6 更正（见上）。

**未受影响、原样保留**

- **D-1**（head `831813c6` 无远端 CI、旧 head `934bd14f` Windows job 失败、旧 CI36 取消与 79F 未闭）：本轮未发现反证，**维持**。
- **D-5**（`storage.py:1212-1215`／`:1147-1157` 无 `ORDER BY`）：维持，仍为"可核对的源码事实，未证跨运行缺陷"。
- **D-7**（UI 白名单 17 / 契约 26 / 缺 16）：维持（本人实算一致）。
- **D-8**（`t01-mainline-contract.test.ts:656`、`t01-ontology-metadata-contract.test.ts:168` 依赖 PATH `python`）：维持。
- **D-9**（Ruff 369/379/380/386 为四次不同真实运行，380/386 仓内无记录）、**D-11**（4299/4300 无应用层断言）、**D-12**（正面结论表）：维持。
- §7 全部独立 HOLD（签名／公证／wholeApp 法律与 `_distutils`／全平台与参考设备／容量 Q5-D2 与旧超限库恢复／损坏 SQLite 物理保护／unknown parser-N3-Store-坏快照／Undo GUI 与未实测 ownership 家族／未知退出码）：维持；**本轮未抵消任何一项**。
- §5 的 R04 十四项 + R05 二十一项**全部 35 项处置追踪**：维持；核对 1/2/5 只是把其中的 Z-03/M-05/P-3/R05-06、Z-04/P-4/R05-07、P-8/R05-04 的**事实表述**收窄，**处置定性（OPEN／部分采纳／未确认／信息级）不变**。
- §8 的 **1–160 行全部保留**：仅第 39 行按核对 6 更正、第 73 行按核对 5 收窄，其余 158 行逐字有效。
- §0–§3、§6（除首行）、§8（除 39/73）、§10（除 Top10 相关条目）、§11：维持。
- **§10 独立最终结论维持不变**（见 §4）。
- 合并可用仍 **2/17**；本轮不新增 FR、不宣称 Goal／发布／M0 完成。

**更正后的第 73 行**

> 73. 部分适用 —— 无缓存层；有"当前推导"与失效语义（`invalidation-v2.json` 为唯一机器规则源，`ontology/ONTOLOGY_CHANGED`、`facts/FACTS_CHANGED` 等九条规则；`storage.py:905-910` 同事务版本递增、`:1611-1622` 重算 stale 并移出 current；`packages/engine/tests/test_storage.py:190-223` 对附录 D 九行做正负参数化，含 ontology family 与无关键不失效负例）。**缺口**：上述为存储级依赖键机制；**经 FR-200 界面编辑**后附录 D.2 首行点名的四类下游（当前推导、保存查询结果、SHACL 结果、报告）是否逐类被标记过期，本轮无证据；附录 D/E/G 在条款映射中亦无行（D-10）。

---

## 3. 未采项（本方不接受的意见及理由）

| 意见 | 不采理由 |
|---|---|
| 4-3「勿虚构晚提交分歧」——**已采纳并据以更正**，此处仅记录：原稿的"预览干净、确认才失败"确实属虚构表述，已撤回，不作为任何论据保留。 | 已落实 |
| 4-2「承认尚缺当前 8318/O040 追加状态」——**已采纳**；但本方**不接受**"应改写 round-05 manifest 使其表示当前候选"：该文件是 aff386f6 的身份索引，改写反而破坏审计链。 | 采事实、不采改写动作 |
| 5-6「不要求新增测试或功能」——**已遵守**：本轮未新增任何测试、脚本或功能；所有更正均为报告内的事实陈述收窄。 | 已遵守 |
| 6-6「Dependabot 版本更新不等同漏洞扫描已通过，分别说明」——**已采纳**：#39 已分别说明"存在每周版本更新（npm＋github-actions）"与"无漏洞扫描条目、未覆盖 pip/uv 生态"。 | 已落实 |
| 1-1「勿虚构晚提交分歧」在本轮其余条目上的延伸推论：不得因本轮收窄 D-3 而**连带**把「早期坏 wire → UNKNOWN/HOLD」既有 OPEN 说成已修或不存在 | **不采**：OPEN 原样保留 |
| 2-2「能否直接推该业务路径最终 INTERNAL_ERROR」——**不采**该推论；但**采**"类层映射缺 ownership 键"这一事实本身，作为条件性风险保留 | 已按条件性保留 |
| 3-3「不能从裸索引点直接宣布当前用户可触发」——**已采纳并据此撤回**原稿的可达性主张；同时**不采**"因此该问题不存在"：补丁覆盖缺口作为条件性风险保留 | 部分采、部分不采 |
| 任何要求改判、要求取得 Pass、或要求为凑清单新增功能的意见 | **一律不采** |

---

## 4. 更正后的 Top 10（替换原稿 §9）

排序依据修正后的严重度与事实强度；**未列入者不降级、未删除**（D-6 撤出后即列入保留项，D-9/D-11 合并为信息项）。

1. **【门禁级·阻断合并】当前 head `831813c6` 无任何远端 CI 证据**（远端只到 `934bd14f`；该次 run 40171564866 的 Windows job 失败，首败为 cp1252 `UnicodeEncodeError`，1 FAIL/980 PASS/3 SKIP/258.55s，`allWindowsAcceptanceProved false`）。旧 CI36 的取消与 79F 未闭。
2. **【中·产品】`definitions[].value.triples[]` 坏词法在预览请求内即以未分类 `ValueError` 失败并 HOLD 会话**（`domain_changesets.py:470-473` 只捕 `MetadataError`；`transactions.py:162` 预览事务内 `store.commit`；`storage.py:726,1128-1129`；逃逸至 `coordinator.py:108` → `mainline.py:1187-1200` → `mainline.py:659-663`）。**机制已按核对 1 更正**（非"预览干净后确认失败"）。
3. **【中·覆盖】附录 D.2 首行点名的四类下游失效联动无经 GUI 证据**；已有的是存储级机制与九行正负参数例（`invalidation-v2.json`、`storage.py:905-910/1611-1622`、`test_storage.py:190-223`）。附录 D/E/G 在条款映射中无行。**措辞已按核对 5 收窄**（非"完全无失效证据"）。
4. **【中·产品】"首个阻断行"无确定序**：`storage.py:1212-1215`／`:1147-1157` 无 `ORDER BY`，而 witness 文档字符串与 UI 标题均声称"首个/前两条"。
5. **【低-中·产品/UX】裸 ownership 冲突详情不可用**：错误码为 `OWNERSHIP_CONFLICT`（**非 `INTERNAL_ERROR`**，已按核对 2 撤回该推论），但旧三字段 detail 在 `job_store.py:674-682` 被判 `INVALID_STATE` → 界面显示"冲突详情暂不可用"。
6. **【低-中·产品/UX】渲染端错误码白名单缺 16 个契约码**（契约 26／UI 17／交集 10）。
7. **【低·文档完整性】仓内缺当前 head `831813c6` 与 O040 的当前事实追加节**（status.md 与 round-05 manifest 均按设计保持历史时点身份，**不改写历史原件**；定性已按核对 4 更正）。
8. **【低·测试】两个 TS 单测仍依赖 PATH `python`**（`t01-mainline-contract.test.ts:656`、`t01-ontology-metadata-contract.test.ts:168`）。
9. **【信息·记录】Ruff 369/379/380/386 为四次不同真实运行，380/386 仓内无记录**；4299/4300 应用层无断言；`PROVENANCE.json` 的 `applicationSuiteNotRun: true` 未被任何文档承接。
10. **【保留项·条件性】已发布 vendored wheel `notation3.py:931`／`:1609` 无边界守卫**：当前用户输入经 `rdf_snapshot.py:37-41` 封装，不构成 standalone EOF，**本轮未构造出当前可触发反例**；作为将来新增不经封装解析入口时的条件性风险保留（与 M-04 一致）。

**其余未列入者（D-9、D-11 之外的 D-3～D-12 各条、§7 全部独立 HOLD、R05-09/M-07/M-01 的处置缺口）不降级、不删除。**

---

## 5. 独立最终结论（维持，不改判）

**结论不变：无法完成验证（Conditional, verification-incomplete）——不通过整候选合并放行。** 本地实现与 macOS 本地验收通过；当前 head 的 Windows 平台验收缺证；存在明确的合并前条件。

**本轮事实核对不改变该结论的方向**，因为结论的两根主支柱均未受影响：

1. **D-1 不变**：`831813c6` 无远端 CI，旧 head `934bd14f` 的 Windows job 失败，旧 CI36 的取消与 79F 未闭——**本地绿与内部演示不得冲抵**。
2. **D-3 机制更正后仍在**：坏 definitions 词法在预览内即未分类失败并 HOLD 会话；只是失败发生的时机是"预览内"而非"确认时"，**严重度与处置要求不变**。

**更正带来的实质变化（如实登记）**：

- **降级/收窄**：D-6 由"中·产品"降为**条件性保留项**（撤回当前可触发主张）；D-4 撤回 `INTERNAL_ERROR` 推论，降为"低-中·UX（详情不可用）"；D-2 撤回"状态与远端相反/历史 manifest 伪装当前"，改为"低·文档完整性（缺当前事实追加）"；D-10 撤回"完全无失效证据"与"附录 C 每行均未执行"两处表述。
- **未改变**：D-1、D-5、D-7、D-8、D-9、D-11、D-12、§7 全部 HOLD、全部 35 项历史意见的处置定性、1–160 行（除 39/73）、合并可用 2/17。

**合并前条件（维持，仅第 2 条定性改写）**：

1. 在**同一候选 `831813c6`** 上取得远端 CI 的完整 Windows 绿灯，并对旧 CI36 的 79F 与取消给出"全部定因或明确残留清单"；不得以 `934bd14f` 的 macOS/Quality 绿或本机 macOS 绿替代。
2. 由唯一维护者**追加**当前事实节：远端已推送至 `934bd14f`、run `40171564866` 的真实结论、当前 head `831813c6` 无 CI；**不改写** `round-05/artifact-manifest.json` 等历史原件。
3. 对 D-3、D-5、D-7、D-8 给出明确处置（修复或正式延期到具名负责人与时点）；其中 D-3 属"用户可触发会话 HOLD"的可用性事件，建议在合并前给出可执行结论。
4. 附录 D（尤其 D.2 首行四类下游）补映射或明确列入未验证范围；**不要求新增测试或功能**。

**推后 CI／合并前条件（不变）**：签名、公证、wholeApp 法律与 `_distutils`、全平台／参考设备／macOS 15／Win11、容量 Q5/D2 与旧超限库恢复、损坏 SQLite 物理保护、unknown parser/N3/Store/坏快照、Undo GUI 与未实测 ownership 家族、未知退出码——全部 HOLD 保留。

---

## 6. 本轮新增的未验与自限

1. 本轮**未运行**任何产品、测试、GUI、构建、打包、probe 或 SQL；所有结论来自源码阅读与既有原件读回。
2. 本轮未构造 `definitions[].value.triples[]` 坏词法的**实际运行反例**（未运行产品）；D-3 的调用链结论为**静态调用链核对**，标注行号可复核。
3. 本轮**未找到** D-6 的当前用户可达反例（经 `rdf_snapshot.py:37-41` 封装）；该条按条件性风险保留，未再主张可达。
4. `packages/engine/src/ontolearn_engine/storage_probe.py` 无引擎模块 import（`grep` 未命中）；该点为**静态检索结论**，未执行。
5. 本轮**未重新评估** §5 的 35 项历史意见之逐条出处与处置独立性——仅在核对 1/2/5 涉及的 8 项上收紧事实表述，处置定性未变。
6. 另一方本轮报告**未读**；round-01～round-03 未跟踪历史目录**未读未改**；原封存稿 `minimax-m31flash.md` 字节与 SHA **未变**（本轮两次复算 `150bb3cbbf9103a7227ecdfbbd1326335806d69e3fe66ff54c2d768a56892e13`）。

---

*本修订为同原任务、原代码未变下的事实修订版本，按约定另封每版本；不改写历史原件，不改判，不通过诱导获取一致。原稿 `minimax-m31flash.md`（68803 B / SHA256 `150bb3cb…`）与本修订并存。*

---

## 7. 阶段判定澄清（追加于第 2 版末尾；不改判、不新增验收项）

本节只做两件事：登记本轮官方身份，并把原稿 §10 首句的**措辞歧义**改成精确表述。**等级、全部意见、verification-incomplete 结论与 HOLD 清单全部保留。**

### 7.1 官方身份与本轮 AX

- 官方 SID 已由 ROOT 读回并记入本轮官方 AX `outputs/20261025_t02_831813c6_fresh_r06_043/ACTUAL-STARTUP.json`：minimax `sid = mvs_e7a25882036e477fa423cd4dd3a5eced`、model `M3.1-Flash（订阅限免）`、thinking `xhigh`、permission `始终授权`；同文件记 `actualMessagesSent 2`、`newPaidOrGUIGrantRequested false`。同目录 `ROOT-START.json` 记 base/head/tree/1363 源/31 提交/79 差异叶与 O042 的 ROOT 侧复核锚点。
- 本方任务身份以该官方 SID 为准，**不另造 task ID**。本节所载即本方在 R06 的完整身份与设置。
- 本方**未读**另一方本轮报告（`zcode/` 目录未打开）；未运行产品/测试/构建/GUI/SQL/probe；代码与候选未变。
- 附带登记（ROOT 侧记录，非本方判定）：`ROOT-START.json` 的 `RootStaticReaderCorrection` 记 ROOT 首读期待 FR201 对象、后更正为直接 22 数组，并注明**未重跑产品、未构成验收失败**。

### 7.2 原稿 §10 首句的歧义与本作者的明确表述

原稿 §10 首句「存在明确的推送前/合并前技术阻断」与同节「推送前技术阻断：无（就源码本身）」**不是两个结论，是同一处表述不精确**：它把"push 前"与"merge 前"两个阶段并入一句。本作者按下列口径明确，**结论方向与全部等级不变**。

**问一：当前整个 base→831813c6 候选，是否存在必须在 push 前解决的技术阻断？**

**答：不存在。**

- 就源码本身，本轮**未发现任何必须先改代码才能 push 的缺陷**。D-3（坏 `definitions[].value.triples[]` 词法在预览内以未分类 `ValueError` 失败并 HOLD 会话）、D-5（`_check_slot`／`_validate_single_slots` 无 `ORDER BY`）、D-7（渲染端错误码白名单缺 16 码）、D-8（两个 TS 单测依赖 PATH `python`）均属**已定性的开放项**，其要求是"给出处置（修复**或**正式延期到具名负责人与时点）"，**不是 push 前置**——本文件第 2 版 §5 合并前条件第 3 条即按此口径写，"给出处置"≠"必须修复"，本节予以确认。
- 与 push 直接相关的源码改动只有 831813c6 的六处 `encoding="utf-8"`（本方已独立复算：剥离该六处关键字后，两文件完整 AST 与 `934bd14f` 严格相等；产品/依赖/CI/cap 零改动）。该改动本身**不是**阻断项。
- 因此原稿首句应读作：**本候选在 push 阶段无源码级阻断；"合并前条件"另行成立**。本节以此替换该歧义表述，不改判。

**问二：哪些是本地审查可通过、但必须等 push 后新 CI 才能合并的条件？**

**答：只有证据类条件，且只有下列两项——两者本地都无法产出。**

1. **同候选 `831813c6` 的完整远端 CI 绿**（含 Windows job 的**全量** pytest 总表）。本地 O041 全检与 O042 六例 GUI 均在 macOS 上，**不构成 Windows 平台验收**，也不构成 CI job 结论；现行 workflow 的 Windows 诊断步带 `--maxfail=1`，首败即止，只有不早停的完整运行才能给出总表。
2. **旧 CI36（run 40164456782 / head 58c9）的 79 个 Windows 失败标记与两次取消的归因结论**。O040 已把"旧 79F 是否全部同因"显式记为 `allOld79FCausesProved false`；该判定只能等新 run 的完整 Windows 表。

**问三：哪些是本地即可满足、无需等 CI 的合并前条件？**

- **记录类**（由唯一维护者**追加**，不改写历史原件）：为当前 head `831813c6` 与 O040／run `40171564866` 追加"当前事实节"（原 D-2，收窄后定性）；并使 R05 的 P-1／P-2／R05-01／R05-02 处置回执与 O040 新证据对齐（§5.3 三处缺口）。两项**不依赖任何 CI 结果**，本地即可完成。
- **处置类**（由具名负责人给出）：D-3／D-5／D-7／D-8 的修复或正式延期。同样**不依赖 CI**。

**问四：是否引入任何"新 CI 之前必须先由人批准"的诊断例外？**

**答：没有。** 本节**不引入**任何新的用户诊断例外批准前置；"未答复的旧诊断 fast-track 例外不是批准"的口径维持不变；本轮仍走正常门禁（本地验证 → 同候选 fresh 双审 → ROOT 接收 → push → PR/CI → merge/remote），push 仍须 ROOT 另发精确票，本方无远端执行授权。

### 7.3 阶段判定一览

| 阶段 | 本候选状态 | 依据 |
|---|---|---|
| 本地审查（本轮 R06 + 第 2 版修订） | **完成；结论为 verification-incomplete**（非通过、非不通过） | §4、§5 |
| push 前源码阻断 | **无** | §7.2 问一 |
| push 后新 CI（同候选 `831813c6`） | **未取得**（远端仅到 `934bd14f`，其 Windows job 失败） | D-1 |
| merge | **不可放行**：等 §7.2 问二两项证据 + 问三的记录类／处置类完成 | §5 合并前条件 |
| 发布／Goal／整体 | **不变**：合并可用仍 2/17；§7 全部独立 HOLD 保留 | §5、§7 |

### 7.4 本节不改动的内容

严重度与等级、原稿与第 2 版的**全部意见**（D-1…D-12、R04 十四项 + R05 二十一项共 35 项历史意见的处置定性）、**verification-incomplete** 结论、§7 独立 HOLD 清单、§8 的 1–160 行（第 39／73 行已按第 2 版更正）全部保留。本节只消除 §10 首句的措辞歧义，并把合并前条件按"是否需要 CI"分类；**不新增发现、不新增验收项、不要求新增测试或功能、不改判、不求 Pass**。
