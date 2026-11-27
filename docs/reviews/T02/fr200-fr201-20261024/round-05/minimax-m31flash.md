# T02 `aff386f6` 全新 R05 — 整个 FR-200／FR-201 候选独立工程审查（MiniMax M3.1-Flash）

## 0. 结论（结论先行）

**整个 FR-200／FR-201 候选：ConditionalPass（附条件通过），且现有合并门禁在当前候选上不可通过。**

- **功能范围结论**：FR-200／FR-201 所声称的交付能力（真实表单 CRUD、事实原 ID 编辑与多值、词法／IRI 受控拒绝、ownership 真 witness 分页重组与可见定位）在我实际读到的实现、契约、引擎、UI 与测试中成立；同版本地完整 check 绿、同版真实桌面 GUI 六例 6／6 PASS、包内原验收证据在源码等价物上成立。**不构成无条件发布通过。**
- **整候选门禁结论（分两层，见第 10 节的程序性效力分析）**：
  - **merge：明确不可。** 依据：候选**尚无自身**的完整远端 CI（G3 未完成）、Windows 侧失败未关闭、ROOT 授权暂停（`mayPushOrMerge: false`）。这三条都不依赖任何对 Windows 失败的预测。
  - **push：** 我**不**把 R05-01／R05-02 主张为 push 取证路径的技术阻断（平台门禁结果在 push 之后才产生；aff 自带的 Windows 首败诊断只在 push 后执行，而 O032 规定的下一步正是先取该首败）。但 push 仍须先满足两项不在我裁量内的前置：**ROOT 明确 push 授权**（当前为授权暂停；无人答复的可选诊断例外**不构成授权**）与**同候选双审及全部意见处置完成**。
  - 上一轮我在此写「不可按现有门禁直接 push／PR／CI／merge」，把 push 与 merge 并列，**在 push 层过宽**，据此精确化（见 §10.5）。
- **明确区分**：aff 唯一新增的 CI 改动只是「Windows 首败诊断」配置，其可过只证明诊断范围可过，**不等于整个候选可过**。本报告不把「诊断配置只改日志」当作产品缺陷已修复，也不把「R04 对 cb8 的附条件通过」继承给 aff。
- **本报告不是 ROOT 接收**：不授权 push／PR／CI／merge，不代替 ROOT 裁决。
- **版本说明**：本文件为 R05 终稿的**事实限定复核修订版**（原稿 65672 B／SHA-256 `26d4dbe2b39348e89b3cbd7c7307b98c33e0dd199e96e101f94adfe7fd4c9951` 的记载保留在案）；修订仅限事实表述，**不改变**「ConditionalPass + CI 门禁阻断」的结论。逐项修订与依据见第 9 节。

---

## 1. 实际身份、只读方式与证据范围

### 1.1 实际执行身份

| 项目 | 实际值（我本方读回／核验） |
| --- | --- |
| 审查主体 | MiniMax Code 内置 Agent（mavis），会话 `mvs_399a64eedb6b4c5a84b52d748dbb99ac` |
| 模型／思考／权限 | 按本次任务票实际配置：MiniMax Code / M3.1-Flash / xhigh / 始终授权（`bypassPermissions`）；任务票声明的 `taskID` 与 cwd 由操作者 UI 读回 |
| cwd（实测 `pwd`） | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` |
| 分支（实测） | `feature/weekly-t02-fr200-fr201` |
| 工作树状态（实测） | `M AGENTS.md`（未提交的指南同步，**非本候选内容**）；`?? docs/reviews/T02/fr200-fr201-20261024/round-01/02/03/`（他人历史产物）；**本方未写入除本报告外的任何路径** |
| 本方唯一写入 | 本文件 `docs/reviews/T02/fr200-fr201-20261024/round-05/minimax-m31flash.md` |

未切分支、未 reset、未 commit／push／PR／CI、未修改 AGENTS／验收／依赖／业务测试／cap、未改冻结输出、未打开旧 `/tmp` probe／旧 DB、未对旧失败库或用户 profile 做 SQL／读写／恢复、未新建功能会话或 worktree。

### 1.2 输入完整性（我本人实测，恰一次）

| 项 | 实测值 |
| --- | --- |
| 附件总字节 | `28994` B |
| 附件 SHA-256 | `c6802ec835f4ba4aad68ec8616377052adcae0e9a72282b5f9101a338c5c7a60`（与任务票一致） |
| 原始清单起止 | 偏移 `17739` → EOF，为附件最后一段，**恰一次**读取 |
| 原始清单字节 | `11255` B（与任务票声明的 11255B 一致；文件末尾无换行，故为 11255 而非 11256） |
| 原始清单 SHA-256 | `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c` |
| 清单条目数 | `160` 条（`>` 前缀条目 148–160 为附件尾部「还需要真人」段） |

该清单是**用户原始需求**，不是本轮摘要的替代；我按 1–160 逐条判定适用性（见第 5 节）。

### 1.3 候选身份（我本人独立复核）

| 项 | 任务票声明 | 我实测 | 一致 |
| --- | --- | --- | --- |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 存在（`commit`）；base tree `133357a527a3967417189195b5c24e3f8a5752e8` | ✔ |
| head | `aff386f6b43cf60a847c9c9597265b0b1b477095` | `git rev-parse HEAD` 同值 | ✔ |
| tree | `2d9b113b4b6ca25049c157c2b94fc79db42ef38d` | `git rev-parse HEAD^{tree}` 同值 | ✔ |
| 累计提交 | 29 | `git rev-list --count base..head` = 29 | ✔ |
| 差异叶 | 71 | `git diff --name-status` 行数 = 71 | ✔ |
| tracked 源 | 1355 | `git ls-tree -r --name-only head` = 1355 | ✔ |

**我另外独立核出的一条关键事实（本轮最重要的结构性结论）**：

```
git diff --stat cb8c9b7a5d780544b2910901ec9141236905d65c aff386f6b43cf60a847c9c9597265b0b1b477095
→ 13 files changed, 2517 insertions(+)
   .github/workflows/ci.yml            |  10 +
   docs/m0-checklist.md                |   2 +
   docs/reviews/T02/... (11 个审查归档与状态文件)
```

即 **`cb8c9b7a → aff386f6` 只差 12 个证据文档路径 + 1 个 CI 路径**；`packages/`、`apps/`、`tests/`、`scripts/`、`licenses/`、`uv.lock` 在 cb8 与 aff 之间**逐字相同**（`git diff --name-only` 对这些前缀输出为空）。因此：

1. aff 承载的**产品实现与测试**就是 cb8 的实现与测试（我已逐文件读过其 diff）；
2. 旧 package094 制品所承载的**包内验收**在「产品源码」层面可继承到 aff，但在「本候选制品」层面**没有任何 aff 自产的包与包内运行**（见 R05-03）；
3. aff 相对 cb8 的**全部新增内容**是「R04 审查归档 + 状态文档 + 一处 Windows CI 诊断」。

### 1.4 只读方式与证据范围（本人实际做／实际读／未执行，三者严格分开）

**本人实际执行（只读或纯计算，写入仅在我自己的临时目录）**：

1. 附件 SHA／清单字节与 SHA／清单条目计数（第 1.2 节）；
2. 全部 git 只读命令：`rev-parse`、`rev-list --count`、`diff --stat/--name-status`、`ls-tree`、`log --oneline`、`status`、`worktree list`；
3. **纯计算验证**：`packages/contracts/src/v2.ts` 中手写 SHA-256（`ownershipSha256`，v2.ts:465）——我在 `/tmp` 抽出该函数并与 Node `crypto.createHash('sha256')` 对拍 10 组（含空串、`abc`、55/56/63/64 字节、32767/32768/32769 字节边界、100000 随机字节）：**10/10 完全一致**；
4. **纯计算验证**：从 vendored wheel 内 `rdflib/term.py`、`rdflib/plugins/parsers/notation3.py` 逐行读出语言标签处理链（`_lang_tag_regex = ^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$`；解析器 `lang = argstr[j+1:i]` **保留大小写**；`Literal._language` 保留原样；`n3()` 输出 `@{self.language}` 原样），据此判定小写归一化发生在**项目自己的** `rdf_snapshot.py:57`（`Literal(str(result), lang=result.language.lower())`，**base 即存在、本候选未改**），而非 rdflib；
5. **纯计算验证**：`scripts/repack-rdflib-input-types.py` 在 `/tmp` 重建 fr201.3 wheel，结果与仓库内提交件**逐字节相同**（`99fab7bdd9148267ac0fcbd49363fc10d9a1edd47a4744726c14a7d14fc51edf`，2379774 B，142 成员，ZIP_STORED，时间戳固定 1980-01-01，LICENSE 未变）；
6. 4 个 vendored wheel 的成员清单／逐成员 RECORD 校验与压缩方式核对；
7. `uv.lock` path 源哈希与仓库内 wheel 实测哈希的比对；
8. 契约 schema 的新增定义（`ownershipDetailDocument`、`ownershipDetailManifest`、`ownershipDetailHeader`、`params_/result_project.ownership.detail`）与 `changeSetSegment` 边界的读取；
9. 渲染端错误码白名单（17）与契约错误码（26）的**重算**；
10. 三个 Python 测试文件中 79 个 Windows 失败候选点的**写出编码静态核对**。

**本人实际读取（只读）**：需求依据（PRD V0.6 FR-200／201、FR-003/006/204/804 与附录 C/D/E/G；ADR-0001；ADR-0002；归档 M0 更新计划）、候选 71 叶 diff（业务源／契约／引擎／UI／测试／CI／打包／文档）、历史 R04 双方终稿 + 处置表 + 两份独立处置核验、原始 R03 处置与 D8 决定单、choice-A 授权记录、O032／O035／O036／O037 原始 JSON 与日志摘录、ROOT 接收票、package094 边界记录。

**本人未执行（因此不声称）**：未运行 `npm run check`／vitest／pytest／ruff／build／package／install／sync／HMR／GUI；未启动产品或引擎进程；未运行任何 e2e；未访问 GitHub 远端（无授权）；未重建或运行旧 package094；未复跑 O022 被拒 probe；未打开旧失败 DB 或用户 profile；未读取本轮另一方（zcode）R05 报告或其结论。

---

## 2. 需求—实现—测试—打包／边界核查（整个候选）

### 2.1 需求依据的实读与两处「票面引用」偏差（事实披露）

| 任务票引用的依据 | 我实际读到的 | 说明 |
| --- | --- | --- |
| `docs/architecture/m0-review-and-update-plan-2026-10-19.md` | **该路径在 `aff386f6` 树中不存在** | `git ls-tree` 确认 `docs/architecture/` 只有 `0001-…`、`0003-…`；同文件归档于 `docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`（两处 SHA256 均为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`，与主检出 `OntoLearn-Studio/docs/architecture/…` 副本同哈希）。我据归档副本读取 S1/S2/S3/C1/B1/U1 全文，未以任务票替代需求。 |
| 「相关 FR-003/007/008 闭包」 | PRD 中**不存在 FR-007／FR-008** | PRD FR 编号为 FR-001…FR-006、FR-100…、FR-200…、FR-800…；`grep -rn "FR-007\|FR-008"` 全仓 0 命中。我按实际闭包 FR-003／FR-006／FR-204／FR-804 阅读。**这是任务票的范围引用偏差，不是产品缺陷**，不影响判定。 |
| 未提交的 `AGENTS.md` | 工作树 `M AGENTS.md`（+101/-10）为操作者同步的最新指南，**非 aff 提交树内容**（`git show aff386f6:AGENTS.md` 为旧 10 行版，不含下述链接） | 该**未提交**指南的「必读」链接指向候选树中不存在的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md`；**归指南维护，不计入本候选缺陷**（见 R05-10）。我未改动该文件。 |

### 2.2 FR-200／FR-201 逐条实现核查

**FR-200 业务概念管理（类／对象属性／数据属性／个体的创建、编辑、复制、删除 + 中文名／英文标识／定义／同义词／示例 + 删除前影响范围）**

- 入口：`apps/desktop/src/renderer/src/ontology/OntologyPage.tsx`（表单）与 `OntologyMainlinePage.tsx`（本体构建页装配）。表单英文标识 pattern 由 `[A-Za-z0-9_][A-Za-z0-9_-]*` 改为 `[A-Za-z0-9_][A-Za-z0-9_\-]*`（把连字符移出字符类末尾的转义歧义，语义等价、消除 HTML pattern 的实现差异）。
- 写入口唯一：`Store.commit`（`storage.py`），经 `JobStore._application`／`_transaction` 与写准入（`_WriteAdmission`）与版本化预览 → 人工确认 → 原子提交；断言事实不会被推导覆盖，历史不可改写（ADR-0002 与本次 diff 均守此边界）。
- 删除影响范围：`entityDeletionImpact`（renderer 侧既有实现）在删除前展示影响，未发现绕过。

**FR-201 结构关系定义 vs 实例事实（两种语义不得被同一句自然语言混淆，用户必须能用真实 RDF 核对）**

- 两条路径在契约与引擎层分离：结构定义走 `definitions`（ontology 层，含 `triples`、`singleValuedPredicates`），实例事实走 `facts`（`manual`/`edits`），渲染端 `manualFactPlan`（改）与 `newManualFactPlan`（新）生成完全不同的计划形状。
- **真实 RDF 可核对性**：`storage._fact`（storage.py:484–495）强制「对象必须等于 `term(value).n3()`」与「ID 必须等于 `digest([S,P,O])`」，即写库对象是规范 N3 形式；引擎侧有真实 rdflib 解析，不是字符串拼接。
- 事实原 ID 编辑与多值：`edits={factId:object}` 保留初始内容摘要身份（ADR-0002 规定），墓碑同样保留；同槽多值可并存，单值声明按 `singleValuedPredicates` 绝对 IRI 执行；`storage._check_slot`（1197–1232）区分三种可读原因：`reservedIdentity`／`sameStatement`／`singleSlot`。
- 词法／IRI 受控拒绝：`domain_changesets.preview_changeset`（417–470）在预览层先做 `iri(subject/predicate)` 与 `term(object)` 解析，`TermInputError` → `INVALID_REQUEST`；`parsed.n3() != value` → `INVALID_REQUEST`（非规范别名拒绝，符合 ADR-0002 第 27 行）。

**ownership 真 witness、分页重组与可见定位（本候选的核心新增）**

- 引擎侧：`ManualOwnershipConflict`／`SingleDeclarationConflict`（storage.py:67／89）携带**真实首个阻断行**的 locator（id／owner／sourceRow／S/P），不是从诊断文案反推；
- 落库：`_persist_ownership_detail`（job_store.py:772）把文档按 `SEGMENT_BYTES` 分段写入 `job_blobs`，头部写 `job_details`，带 `origin`／`requestHash`／`fingerprint`／`manifest`，同指纹复用既有 detailRef（幂等、不无界增长）；
- 读取：`ownership_detail_page`（job_store.py:932）按 `startOrdinal/pageSize` 出页，段级 sha256 与 base64 全量校验，页/帧预算 262144 与 manifest 16MiB 边界保留；
- 契约侧：`matchesOwnershipDetail`（v2.ts:535）与 `reassembleOwnershipDetail`（index.ts:942）做**信封硬化**（每段字符串 ≤43692，恰等于 32768 B 的 base64 长度）+ 段 hash + 整文档 SHA-256 + `validateBusiness3('ownershipDetailDocument')`；
- 渲染侧：`readOwnershipConflictDetail`（mainline-ownership.ts:13）逐页拉取、重组、校验 `sourceBaseRevision` 与预览基准一致，再映射为只读视图 `OwnershipConflictDetailView.ts`；会话层 `mainline-session.ts` 在 `OWNERSHIP_CONFLICT` 时转入 `ownershipDetail` 状态机（reading／unavailable／ready），并在 `OntologyMainlinePage.tsx` 渲染可操作文案（不丢用户已输入内容）。

**我独立确认的三处关键正确性**（不引用他人结论）：

1. **手写 SHA-256 正确**：见 1.4(3)，10/10 与 Node crypto 一致（含 32768 段边界）；
2. **43692 与 32768 精确自洽**：`ceil(32768/3)*4 = 43692`，schema `changeSetSegment.dataBase64.maxLength = 43692`，`capture` 的 `value.length > 43692` 判定不误伤引擎自身产物；
3. **43692 只作用于分页信封，不作用于解码后的 witness 字段**：`capture({expected, pages})` 仅在 index.ts:989 一处调用，解码后走 `validateBusiness3` → `validateV2`（v2.ts:314）的**整文档 262144 保守预算**与 schema 字段上限 16777216。此即 R04 Z-02 撤回后仍需保留的既有边界，本候选未改变。

### 2.3 测试面（实际读了测试定义，不只看测试名）

- 新增 Python 套件 7 个文件（dispatch 23 例、language 8 组、manual 22 组、postwrite admission 17 组、rows budget、text budget、read-work budget），覆盖：写入准入的持有／结算／失败保持、前台/后台作用域不可互借、终态增长余量、段失败整体回滚、诊断不得污染已准入读取器、旧 blob 损坏即 HOLD 而非零回退、原始 ID 保留、未知解析失败保持 HOLD 等。
- 新增 TS 套件 4 个文件 + 2 个既有文件扩充，其中 `tests/unit/t02-manual-fact-id.test.ts` 是**真跨语言**测试：把 TS 产生的记录喂进真实 Python `Store._fact` 验证「接受且不替换 ID」，并用 Python 生成的 golden 向量核对 TS 输出（覆盖 plain／language／integer／NFC／NFD，且 NFC≠NFD）。
- 新增 e2e `tests/e2e/t02-fr200-fr201.spec.ts`（1748 行，3 个 describe 级用例：FR200 表单矩阵、FR201 关系与多值原 ID 保留、canonical 数字子段 fresh cohort）。
- 契约侧新增 `ownershipDetailDocument` 等 schema 定义与 `fixtures.json`／`binding-regressions.json` 的 `registryHash` 同步（`058ed1be…` → `5e097b7e…`）。

### 2.4 同版证据（我读回原始记录，未复跑）

| 类别 | 实际结果 | 原件 |
| --- | --- | --- |
| 本地完整 check（第 1 次） | `npm run check` 直接调用 → exit 1，17.463s，TS 1890 PASS/2 FAIL（日志原文 `Error: spawnSync python ENOENT`；实际调用点为 `tests/unit/t01-mainline-contract.test.ts:656` 与 `tests/unit/t01-ontology-metadata-contract.test.ts:168` 的 `execFileSync('python', …)`，见 R05-12），`build` 与 `engine:check` 未运行 | O035 `fullcheck-result.json`（首败保留） |
| 本地完整 check（第 2 次，环境纠正） | `uv run --offline --frozen npm run check` → exit 0，173.333s，PID 35167；TS 39 文件/1892 PASS；Py 3769 收集/3719 PASS/50 SKIP/1 warning；Ruff 379 文件；stdout 12986B SHA `2132d7a7…` | O036 `CANDIDATE-QUALIFICATION.json`＋原始 stdout/stderr |
| 构建等价性 | 5 构建中 4 项 byteexact；main 606471B，SHA `4309328d…`，与旧包 main `20c94ed9…` 仅差一个 24 字符 dev CSP nonce（源码 `electron.vite.config.ts:7` `randomBytes(18)`，`src/main/index.ts:201` 仅在 `devURL` 分支） | O036 `build-difference-qualification.json`＋`main-build-before-after.diff` |
| 真实桌面 GUI | 6 spec 全 PASS（0 skip/retry/flaky），102625.483ms，runner 39319 自然 exit 0；57 成功事务（7/7/7/7/22/7，57 唯一 job/operation）、43 拒绝（42 INVALID_REQUEST + 1 OWNERSHIP_CONFLICT）、58 附件；FR201 保留 11 add／2 真实原 ID edit／2 remove；第 6 个 fresh cohort：`en-001`、`de-ch-1901` 各 new + 原 ID edit 共 4 笔全链成立 | O037 `runtime-full6-001/report.json`（3996488B，SHA `3b78d51e…`）＋`independent-actual-result-review.md` |
| 远端 CI（PR16 / run 40164456782 attempt1） | macOS success；Quality cancelled（15min annotation，check 469s／E2E 305s 已 success，packaged recovery skipped）；Windows cancelled（20min annotation，3769 收集、约 81%、已观测 79 个 F = language 6 + manual 72 + read-work 1），typecheck/build/e2e/package 全 skipped | O032 `FIRST-CI-FACTS.json`＋`DIAGNOSIS-AND-MINIMAL-PLAN.md`＋job 日志 |
| ROOT 接收 | O037 接收票逐项重算通过，`CI36Windows79FRootCauseNotClosed: true`、`R04NotInherited: true`、`freshR05Required: true`、`mayPushOrMerge: false`、合并可用仍 2/17 | `controller-t02-aff386f6-original6-actual-root-acceptance-20261025.json` |

---

## 3. 发现（按严重程度排序；不凑满 10 项，不把可选建议冒充验收）

### R05-01｜**High｜阻断整候选（门禁未满足）**｜Windows job 无任何成功证据；79F 根因仍属高可信假设，本候选只加诊断、未修因

- **现象**：CI36 的 Windows job 在 `engine:check` 步骤约 81% 处被 20min 上限取消，取消前已出现 79 个失败（6 language + 72 manual + 1 read-work），此后 typecheck／build／e2e／package 全部 skipped；此后继步骤均未执行，故**不存在任何 Windows 通过证据**，也没有这 79 个 F 的真实 assertion traceback 与最终 pytest 总表（O032 `FIRST-CI-FACTS.json` 明确记载 `noFailureAssertionTracebackOrFinalPytestSummary: true`）。
- **本候选实际改动**：aff 相对 cb8 只在 `.github/workflows/ci.yml` 增加 10 行——把原 `npm run engine:check` 在 Windows 上改为 `PYTEST_ADDOPTS='-vv --maxfail=1 --tb=short'` 的一步，并先打印 `sys.version / locale.getencoding() / locale.getpreferredencoding(False) / sys.flags.utf8_mode / defaultFileEncoding`。**这是 O032 建议的「先诊断」动作，未修任何测试或产品代码。**
- **我独立做的因果核对（静态，可复算）**：
  - `packages/engine/tests/test_mainline_manual_input_rejection.py:370,402,415,486,520` 与 `packages/engine/tests/test_mainline_read_work_budget.py:275` 使用 `write_text(json.dumps(..., ensure_ascii=False))`，**没有 `encoding=`**；
  - 同一批文件的载荷含非 ASCII：`:358` 项目名 `"同宿主规范输入"`、`:229/231/426/427` 事实对象 `"泵站A"`；
  - 对照组 `packages/engine/tests/test_mainline_language_input_rejection.py:303-307` 显式 `encoding="utf-8"`，而 O032 记录「language 同文件明确 UTF8 写 trace 的 12 个 stdio 例通过」；
  - 失败分组（6／72／1）与「owned 路径复用 manual 写 trace helper + manual stdio 族 + read-work finally 一处」高度吻合。
  - 因此「默认编码写 Unicode 证据导致 Windows 失败」是**高可信且有直接源码支撑**的假设；但它**仍不是已确证的根因**（无 traceback、无实测 locale、无 utf8_mode 值）。
- **严重度／阻断性**：High，**阻断（门禁未满足）**。阻断的依据是**事实**：本候选在 Windows 上**没有任何成功结果**（CI36 该 job 为 cancelled，其 typecheck／build／e2e／package 从未执行），因此「三平台真实 CI 全绿」这一门禁**未被满足**；而本候选对该 job 的唯一改动是诊断步骤（打印 locale/utf8_mode + `--maxfail=1`），**没有关闭任何失败**。
- **明确区分「门禁未满足」与「预测必失败」（本条经事实限定复核修订）**：我**不**把「Windows 这一 job 在本候选上不可能为绿／必失败」写成已证事实。理由有三：(1) 79 个 F 是 CI36 **进度输出中观测到的失败标记**（`observedFailureGlyphsBeforeTimeout: 79`），**没有真实断言 traceback、没有最终 pytest 总表**，因此它们究竟是哪一类失败（主体断言失败 vs `finally` 证据写出失败 vs 其他）**未被证实**；(2) 根因假设**未被实测**——无 Windows 运行环境、无实测 locale／utf8_mode、无首败栈；(3) CI36 的 head 是 **58c9**，**不是 aff**，且实际 checkout 为合成提交 `681ffbd0…`，故该观察对 aff 是**强指示而非 aff 的直接证据**。在假设成立的前提下，`--maxfail=1` 会让该 job 更快停在首个失败并从 cancelled 变为 failed，**预计仍红**；但这是**基于假设的预期，不是已测事实**。我据此**不**使用「不可能为绿」「必失败」这类断言。
- **不夸大**：我**不**宣布 UnicodeEncodeError 已被确认，**不**宣称已排除「主体断言失败被 finally 写出覆盖」的可能，**不**把 O022 被拒 probe 重新采集，**不**宣称已在 aff 上实测过 Windows 结果。

### R05-02｜**High｜阻断整候选**｜三 job 中两 job cancelled，无任何远端全绿证据；aff 未 push

- **现象**：PR16 `https://github.com/NOmoreJoke/OntoLearn-Studio/pull/16` 仍 open／unmerged；remote develop 仍 `583c05c`，feature 仍 `58c9bbb`，**aff 未 push**；CI36 attempt1 中 Quality 与 Windows 的 conclusion 均为 `cancelled`（非 failed），即 **Quality 的 packaged recovery 从未执行、Windows 的 build/e2e/package 从未执行**。
- **因果**：Quality 的 verify 进程虽打印 passed 且 runtimeExit0，但 GitHub step 仍 cancelled、后续 recovery skipped（O032 明载）；这与「进程打印 ≠ step 成功」一致，**不可抹平**。
- **严重度／阻断性**：High，**阻断**。现有门禁要求三平台真实 CI 全绿；本候选既无远端全绿证据，也无远端执行授权（R05 期间我未做任何远端动作）。
- **边界澄清（避免不公实的追责）**：CI36 的 head 是 58c9，**不是 aff**；实际 checkout 的合成提交为 `681ffbd0…`，**不得把 `run.head_sha` 当作实际被检出的 SHA**。因此 CI36 的红／cancelled 对 aff 而言是**强指示但非 aff 的直接证据**。

### R05-03｜**中｜非阻断（事实记录，不新增前置）**｜本候选自身没有自产新包与包内运行；ROOT 已以有界桥接保留原 094 未变制品

- **事实**：aff 的包内验收证据全部来自旧制品 package094（cb8 时期构建）。O036 记录 `packageManufacturedOrExecutedThisTurn: false`、`newHeadGUIActuallyExecuted: false`、`allChangesOnly12EvidenceDocsPlus1CIPath: true`、`oldRuntimeEvidenceNotRelabeledAsNewHeadRun: true`；ROOT 接收票记录 `packageBoundary: "Original unchanged 094 artifact prior runtime retained; no new packaging or packaged runtime at aff"`。
- **ROOT 已作的有界桥接**：即「原 094 未变制品的原运行继续作为包内证据保留，并明确不把它说成 aff 新包运行」。该处置**已由 ROOT 在接收票中作出**，本审**不**推翻、不重复审批。
- **我独立补充的支撑事实**：aff 与 cb8 的产品源码／测试／依赖**逐字相同**（仅 12 docs + 1 CI 路径），且旧包 main 与新构建 main 仅差一个 dev nonce、其余 4 构建 byteexact → 「产品实现已被包内验收覆盖」这一推理成立。
- **边界表述**：可以写「**本候选没有自产新包，也没有 aff 自产的包内运行**」；**不**可以把「旧 094 的运行」写成 aff 的新包运行；**不**可以把「未自产新包」当作产品缺陷——它是该候选「只改文档与 CI」的必然结果。
- **严重度／阻断性**：中，**非阻断**。**本审不把「另做一次 aff 制品与包内验收」写成新的合并前置**：该决定属 ROOT 既有处置范围，是否另做由 ROOT 裁定；本审只负责登记事实与边界，避免把「未自产新包」误升级为缺陷或新增授权要求。

### R05-04｜**中｜非阻断（当前入口需更新；历史数值不得篡改）**｜`status.md` 与 `m0-checklist.md` 的「当前状态」入口停在 58c9 时刻

- **事实**：`docs/reviews/T02/status.md` 记「受审 head `cb8c9b7a`、tree `b8010eea…`、27 累计提交、58 差异叶、1344 源文件」「尚未推送、创建 PR、运行本候选 CI 或合并」；`docs/m0-checklist.md` 末段同步引用它。该快照生成于 **58c9 入库时刻**，其引用的证据原件是 `outputs/20261025_t02_rows_text_integration_029/`（O029，head `cb8c9b7a`）。
- **需要「当前入口更新」的部分（事实）**：当前 head 是 `aff386f6`／tree `2d9b113b`／29 提交／71 叶／1355 源；PR16 已存在且 open；CI36 已运行（macOS success，另两 job cancelled）。
- **不属于缺陷、不得改写的部分（事实）**：`status.md` 中的「**Ruff 369 格式合格**」**在 O029 当时是真实值**——我已实测 `outputs/20261025_t02_rows_text_integration_029/full-check-01.stdout.log:107` 为 `369 files already formatted`（同 log `:106` 为 `All checks passed!`）。O036 的 `379 files already formatted` 是**另一个 head（58c9+CI 工作树）的另一次实测**（`check-attempt-02.stdout.log:107`），差异来自两次快照的 Python 文件数不同（候选新增 Python 测试文件）。**两者不是矛盾、不是记录错误、更不是篡改历史**；历史快照里的 369 应当原样保留。
- **因果**：M-01 的文档在入库时准确；此后 head、远端状态与 Ruff 计数口径变化，**当前入口**未回写。
- **严重度／阻断性**：中，非阻断技术缺陷，但 AGENTS.md §6 规定「完成度只在 `docs/m0-checklist.md` 和对应 `status.md` 中维护」，且状态文档不得被当作当前事实重复引用。**本审按冻结与只读纪律未修改该文件**；处置方式是「在当前入口补写 aff／PR16／CI36 的实况并注明快照时点」，**不是**回头改写 58c9 时刻的历史数值。

### R05-05｜**中｜非阻断（延续 OPEN）**｜渲染端错误码白名单仍缺 16 个契约码

- **我独立重算**（`errors.json` 26 码 vs `mainline-session.ts:86-104` 的 17 码，交集 10）：契约码中未进入 UI 白名单的仍为 16 个：`CURSOR_EXPIRED, CURSOR_MISMATCH, ENGINE_EXITED, HANDSHAKE_REQUIRED, MAPPING_VALUE_INVALID, METHOD_NOT_ALLOWED, NETWORK_FORBIDDEN, NOT_FOUND, PAYLOAD_EVICTED, QUEUE_FULL, SEMANTIC_INPUT_INVALID, SESSION_MISMATCH, TIMEOUT, UNSUPPORTED_CAPABILITY, UNSUPPORTED_CONSTRUCT, VERSION_INCOMPATIBLE`。
- **与 R04 Z-05 的关系**：R04 记录的同一缺集在 aff **未变化**（aff 相对 cb8 的产品源码逐字相同）；本候选新增的 `OWNERSHIP_CONFLICT` 已在 cb8 即在白名单内，故缺集仍为 16。
- **严重度／阻断性**：中，非阻断。**我不把 16 码全部断言为「当前可达」**（未逐方法穷尽错误出口）；按原分工，在各能力真实接线时逐方法对齐。

### R05-06｜**中｜非阻断（延续 OPEN）**｜`definitions[].value.triples[]` 的早期坏词法仍走 UNKNOWN→HOLD

- **我独立核实的代码边界**：`domain_changesets.preview_changeset:451-465` 的新词法守卫**只覆盖** `request["plan"]["manual"]` 与 `plan["edits"]`；定义体的 triples 仍在 `storage._definition`（storage.py:715-726 一带）内做 `iri`／`term` 校验，抛出的 `TermInputError`（`ValueError` 子类）或非 canonical `ValueError` 发生在**受控 catch 之前**，不会变成 `INVALID_REQUEST`。
- **后果**：此类输入仍会把会话置为 UNKNOWN／HOLD（基线约束，不放宽）。
- **严重度／阻断性**：中，非阻断，**与 R04 Z-03／D8 第 24 行一致**，在原始 triples／Agent 接线前由 T01 处理；本候选不得被解读为「已修」。

### R05-07｜**低｜非阻断（延续 OPEN）**｜通用／受管 ownership 冲突仍无真实可读定位

- **事实**：`storage._check_slot` 仅在 `manual_incoming is not None` 时抛带 witness 的 `ManualOwnershipConflict`（storage.py:1217-1229）；其它 ownership 冲突抛裸 `Conflict(category="ownership")`；`job_store._application:607-634` 对后者写**旧三字段** detail（`category/resource/projectId`），并在 `_ownership_header:651-…` 中显式识别该形状并 `fault("INVALID_STATE")`。
- **可见后果**：渲染端读到该 detailRef 会失败 → 会话把 `ownershipDetail` 置为 `unavailable` → 页面显示「冲突详情暂不可用」。
- **严重度／阻断性**：低，非阻断（延续 R04 Z-04 的合同边界：不得以伪 detailRef 或泄露诊断文本补齐）。

### R05-08｜**低｜未确认观察（非缺陷）**｜「首个阻断行」的排序仍未规定

- **事实**：`storage._check_slot:1212-1215` 的同槽 SELECT 无 `ORDER BY`；`_validate_single_slots:1147-1173` 的 `GROUP BY subject … LIMIT 2` 也无明确排序。
- **本候选的含义**：typed witness 承诺的是「**实际**首个阻断行」而非「按字典序第一个」，这比按文案反推是进步；但**跨运行的行序**未规定。
- **严重度**：低，**未确认观察**。我**没有**构造同槽双冲突的反例，**不**把它升级为已证缺陷（与 R04 Z-01／R03 双方一致）。

### R05-09｜**低｜信息级（正面结论 + 一项成本事实）**｜vendored 依赖可复现、许可已披露；成本是仓库体积与上游安全补丁需走 repack 流程

- **我独立做的正向验证**：在 `/tmp` 用仓库内 `scripts/repack-rdflib-input-types.py` 重建 fr201.3 wheel，与仓库提交件**逐字节相同**（`99fab7bdd9148267ac0fcbd49363fc10d9a1edd47a4744726c14a7d14fc51edf`）；脚本自身固定并校验上游 wheel SHA、patch SHA、逐成员上游 RECORD 与补丁后源码 SHA，且强制「除 notation3.py／METADATA／RECORD 与 dist-info 改名外逐成员字节不变」「LICENSE 未变」；`uv.lock` 的 path 源哈希与仓库 wheel 实测哈希一致；`licenses/NOTICE` 已披露本地修订、异常类型清单、仓库 patch／PROVENANCE 路径与「App 内 LICENSE 路径仍为上游版本名」这一事实。
- **成本事实（信息级，非缺陷）**：3 个本地 wheel 以 `ZIP_STORED`（未压缩）入库，fr201.3 为 2379774 B，而上游同内容压缩后为 596328 B；仓库因此多出约 7.6 MB 二进制。维护含义：上游 rdflib 安全补丁需经 repack + 哈希更新流程才能进入产品（`PROVENANCE.json` 已把供应链角色与消费者角色分离声明）。
- **严重度**：低／信息级，**不阻断**。

### R05-10｜**非本候选范围｜归指南维护**｜失效的「必读」链接位于**未提交**的 AGENTS.md，不属于 aff 提交树内容

- **实测事实**：`git show aff386f6:AGENTS.md` 为**旧 10 行版**，其中 `m0-review-and-update-plan` 出现 **0 次**——即 **aff 提交树内的 AGENTS.md 不含该链接，本候选不存在此缺陷**。
- **失效链接的实际位置**：仅存在于**工作树中未提交**的 `AGENTS.md`（操作者同步版，`git diff --stat` 显示 +101/-10），其「必读」表指向 `docs/architecture/m0-review-and-update-plan-2026-10-19.md`，而该路径在 `aff386f6` 树中不存在（实际归档位置：`docs/iterations/I01/inputs/`、`docs/reviews/I03/inputs/`）。
- **归类**：这是 **AGENTS.md 指南自身的维护事项**（文件在「冻结快照归档」提交中被移动，指南未同步），**不属于 aff 候选的提交树内容**，因此本条**不计入本候选的缺陷清单**，仅作对指南维护方的登记。
- **严重度**：非候选范围；我**未修改**该文件（只读纪律 + 本方唯一写入限制）。

### R05-11｜**低｜非阻断（观察）**｜ownership 冲突定位不含事实对象值，用户看不到「冲突的是哪个值」

- **事实**：`ManualOwnershipConflict` 的 witness（storage.py:67-86）只携带 `id / owner / sourceRow / S / P`；`OwnershipConflictDetailDocument` 的 schema 同样不含 `object`。
- **后果**：页面能回答「谁占着这个槽位」，但不能回答「我提交的那个值是什么、与谁重复」——用户需要回看自己的输入。
- **判断**：这是**刻意的跨边界最小化**（跨边界只传受限参数，不回传单元格原值），符合 AGENTS §3 的错误面规则；渲染端本地已有 domain state，理论上可按 id 自行补显对象值。**我不把它列为缺陷**，仅登记为「可见定位的信息量边界」，供产品决定；且**不得**以补充原值的方式违反跨边界原值禁令。

### R05-12｜**低｜非阻断（测试脆弱）**｜两个 TS 单测硬依赖 PATH 上存在 `python`（**本条经事实限定复核更正文件引用**）

- **实测事实（逐行读过源码）**：
  - `tests/unit/t01-mainline-contract.test.ts:656`：`execFileSync('python', ['-I','-B','-c', script], { cwd: root, encoding: 'utf8', … })` → **依赖 PATH 上的 `python`**；
  - `tests/unit/t01-ontology-metadata-contract.test.ts:168`：`execFileSync('python', ['-I','-B','-c', script], { cwd: resolve('.'), … })` → **依赖 PATH 上的 `python`**；
  - `tests/unit/t02-manual-fact-id.test.ts:66-68`：`spawnSync(resolve('.venv/bin/python'), ['-I','-c', pythonCheck, resolve('packages/engine/src')], …)` → **不依赖 PATH 的 `python`**，而是依赖**仓库内 uv venv 的 `.venv/bin/python`**（另一类脆弱性：venv 必须已就位）。
  - **更正声明**：原稿此处误引了不存在的 `tests/unit/t02-mainline-contract.test.ts`，并把 `t02-manual-fact-id.test.ts` 误列为 PATH-python 用例；两处均按上述实测更正。
- **与 O035 的对应**：O035 中本地裸 `npm run check` 的 2 个失败正来自上述**前两个**文件，日志原文措辞为 `Error: spawnSync python ENOENT`（vitest 的错误呈现方式；实际调用点是 `execFileSync('python', …)`）。该失败已被正确归因为调用环境未把 uv venv 放进 PATH，**未被误判为产品回归**。
- **影响**：这两个测试的结果取决于调用环境是否恰好把某个 `python` 放进 PATH；CI 中因宿主／uv 环境可用而绿（CI36 Quality：TS 1892 PASS）。
- **严重度**：低，非阻断（测试健壮性）。建议由唯一维护者把解释器解析固定（例如统一走 uv venv 路径），避免「环境偶然性」决定测试结果。

### R05-13｜**信息级｜代码可读性观察**｜核心文件持续变大

`packages/engine/src/ontolearn_engine/job_store.py` 2993 行、`storage.py` 1887 行、`tests/e2e/t02-fr200-fr201.spec.ts` 1748 行（我在 aff 实测，与 R04 记录的 cb8 数值完全一致，因为产品源码未变）。行数不等于正确性缺陷；仅登记为「按模块职责评估拆分」的信息级建议，本轮不改。

---

## 4. 历史 R04 十四项意见逐项追踪（历史技术条件，不继承给 aff）

我以 aff 的源码为准逐项复核；「维持」表示该事实在 aff 仍然成立；「已闭合」必须有 aff 源码或 aff 证据支撑。

| 原意见 | R04 处置 | 我在 aff 上的独立复核 | R05 状态 |
| --- | --- | --- | --- |
| Z-01 同槽 SELECT 无 ORDER BY | 未确认观察 | `storage.py:1212-1215`、`:1147-1173` 仍无 ORDER BY；未构造反例 | **维持未确认**（R05-08） |
| Z-02 43692 与 witness 字段限 | 作者撤回 | 我复算：`capture` 仅作用于分页信封（index.ts:989），43692 = 32768B 的 base64 长度；解码文档仍受 `validateV2` 整文档 262144 预算与 manifest 16MiB 约束（v2.ts:314）。**撤回维持**，不得恢复为缺陷 | **维持撤回**；整文档预算边界保留 |
| Z-03 definitions.triples 早期坏词法 | OPEN 非阻断延期 | 我核实守卫只覆盖 manual/edits（domain_changesets:451-465），定义体仍在 `storage._definition` 抛错 → 仍 UNKNOWN/HOLD | **维持 OPEN**（R05-06） |
| Z-04 ownership 无错误码映射／通用定位 | 部分采纳 OPEN | typed witness 仅覆盖 `ManualOwnershipConflict`／`SingleDeclarationConflict`；其余走旧三字段 detail，读取时 `INVALID_STATE` → UI「暂不可用」 | **维持部分 OPEN**（R05-07） |
| Z-05 白名单 17 vs 26 缺 16 | 采纳非阻断延期 | 我重算：契约 26、UI 17、交集 10、缺集仍为同样 16 码 | **维持**（R05-05） |
| Z-06 `de-CH-1901` 语义边界 | 交 ROOT 审结 | 见第 4.1 节独立判定 | **维持为语义边界，未变政策** |
| Z-07 文件增长 | 信息级 | aff 实测 2993／1887／1748，与 cb8 同 | **维持信息级**（R05-13） |
| M-01 状态文档与引用 | 本次完成 | `status.md` 与 `m0-checklist.md` 已在 aff 树内；但内容停留在 58c9 时刻 | **形式完成、内容已过时**（R05-04） |
| M-02 wheel 冗余／锁文件无哈希 | 核心前提不采 | 我重算：`uv.lock` 的 path 源确有 `sha256:99fab7bd…`／size 2379774，与仓库 wheel 实测一致；本地 wheel 为 ZIP_STORED(0)、上游为 DEFLATED(8)（我的实测）；**不采「删除历史 wheel」建议** | **维持不采**；我另给出更强的可复现性正向结论（R05-09） |
| M-03 4301 与 4299/4300 边界 | 部分采纳未来建议 | 仓库只有 `"9"*4301`（超限）覆盖；**4299／4300 边界仍无覆盖** | **维持延期**（可作未来最小补充） |
| M-04 standalone EOF 残余 IndexError | 保留 OPEN | `rdf_snapshot.term()` 仅捕获 `BadSyntax`／`Notation3InputError`；EOF 位置仍可能抛未类型化 `IndexError` → 落入 broad `except Exception` → `ValueError`（非 `TermInputError`）→ 仍 UNKNOWN/HOLD | **维持 OPEN**；本候选未泛捕、未改写语义 |
| M-05 definitions 未全面受控 | 部分观察 | 同 Z-03：不能由后置 catch 推出「所有定义出口已受控」 | **维持** |
| M-06 schema 只约束 id 形状 | 不认定当前缺陷 | `storage._fact` 仍是权威校验；`tests/unit/t02-manual-fact-id.test.ts` 以真实 Python 交叉验证 TS 产出 | **维持**（本候选未新增第二写入口） |
| M-07 `@ontolearn/contracts/v2` 桶导出 | 不直接改导出 | 未改导出面；无同名冲突反例 | **维持** |

### 4.1 我对 `de-CH-1901` 张力的独立判定（不把 ROOT 判断当人类选择，也不替用户新定规范）

- **事实链（我逐行核过）**：rdflib 7.6.0 的 `_lang_tag_regex = ^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$` 接受 `de-CH-1901`、`en-001`；解析器与 `Literal` 均**保留大小写**；**归一化发生在项目自己的** `packages/engine/src/ontolearn_engine/rdf_snapshot.py:57`：`Literal(str(result), lang=result.language.lower())`——该行在 **base 即存在，本候选未改**。
- **因此产品当前行为**：合法但混合大小写的 `"设备"@de-CH-1901` 被判为**非规范别名**而受控拒绝（`parsed.n3() != value` → `INVALID_REQUEST`）；精确小写 `"设备"@de-ch-1901`、`"设备"@en-001` 被接受。候选新增测试 `test_mainline_language_input_rejection.py:54` 正是把这条语义**固化**为回归（`term('"设备"@de-CH-1901').n3() == '"设备"@de-ch-1901'`），标题亦自陈「digit_subtags_are_grammatical_separate_from_canonical_case_policy」。
- **与需求的张力**：附录 C 要求「多语言按字面量保留」，而 ADR-0002 第 27 行要求「对象必须等于 `term(value).n3()`，非规范别名拒绝提交」。二者在此处确实存在张力：**语法合法 ≠ 可按原字面提交**。
- **我的独立结论**：本候选**没有引入任何新的大小写政策**，它只是把 base 既有 canonical 规则**写成了测试**；choice-A 授权的 requirements 明确「保持既有 canonical 输入政策、不静默规范化」，而实现禁止项含 `no silent normalization`——本候选符合这两条。因此**我不把该处判为缺陷，也不把它升格为需要用户新决定的合并前置**。若将来要放宽（接受混合大小写并按原字面存储），那是**改变既有存储／输入政策**，需要新的候选门禁与人类决定，且我不代为决定。
- **实测对照**：O037 中该输入确实被拒（42 INVALID_REQUEST 之一），而 `en-001`／`de-ch-1901` 的 new + 原 ID edit 在第 6 个 fresh cohort 全部成立 → 行为与静态分析一致。

---

## 5. 用户原始清单 1–160 逐项适用性与证据

**判定口径**：适用＝本产品当前形态下应有对应能力且我实际核查了；部分适用＝能力存在但覆盖/边界有缺口；不适用＝该清单项描述的能力在本产品形态（本地优先、无账号体系的离线桌面端、模型网关未接入）下不成立，按用户要求「直接跳过，不要为了满足清单而增加无用的功能」。

### 5.1 身份、账号、权限、多租户（1–14）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 1 | 部分适用 | 契约有**被设计**的 v2 JSON Schema（`packages/contracts/v2/schema.json`）+ zod `.strict()` 边界 + 引擎权威校验；领域语义来自 PRD 附录 C 能力矩阵，非逐表即兴。不足：部分 schema 只能约束形状（如 id），内容派生身份靠引擎（见 M-06） |
| 2 | 不适用 | 产品无登录/账号体系（本地桌面、无网络入口），不存在邮箱登录 |
| 3 | 不适用 | 无密码重置 |
| 4 | 不适用 | 无 MFA、无账号体系 |
| 5 | 不适用 | 无用户会话；引擎会话（`engineSessionId`）是进程级 stdio 握手，不承载用户登录语义 |
| 6 | 不适用 | 无 SSO；企业身份在首发范围外 |
| 7 | 不适用 | 无 SAML |
| 8 | 不适用 | 无 SCIM／离职流程 |
| 9 | 部分适用 | 权限不是角色表，而是**能力白名单**：preload 仅暴露按业务命名的方法、IPC 处理器保留 sender／mainFrame／可信文档校验、引擎侧 `authorize` + `profile=business3` + 选中项目绑定。不足：不是「admin/everyone」两级角色模型（该模型在本产品不存在） |
| 10 | 适用 | 跨项目读取被拒：渲染端参数 `projectId` 被主进程强制覆写为当前选中项目（`project-mainline-service.ts` 的 `getOwnershipConflictDetailPage` 显式注入 `projectId: current.project.projectId`），引擎侧 `_OwnershipProof.check` 校验 `owner.selected == project`；改 URL/参数无效 |
| 11 | 不适用 | 无多租户；单用户本地项目 |
| 12 | 不适用 | 无「登录为他人」概念 |
| 13 | 不适用 | 无登录面 |
| 14 | 不适用 | 无锁定策略需求面 |

### 5.2 数据库、迁移、备份、容量（15–22）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 15 | 适用 | SQLite `user_version` 前向迁移 + 迁移 hook 贯穿提交前／中／后，失败回滚并可重开重试；未来格式拒绝打开（ADR-0002「迁移与恢复」）。实际格式 3（`store.actual_format != 3` 拒绝） |
| 16 | 部分适用 | 迁移取得事务写锁后重读格式版本，避免双 opener 重复 DDL；不足：未做「业务高峰不锁表」的现场测量（本地单机，无并发高峰） |
| 17 | 部分适用 | 依赖 SQLite 默认索引与 `GROUP BY subject` 聚合；不足：未测量真实数据量下的计划与耗时（Q5 容量未定，HOLD） |
| 18 | 不适用 | 无连接池（进程内单连接 SQLite） |
| 19 | 部分适用 | ADR-0002 记录 `backup(newPath)` 使用 SQLite 在线备份、禁止覆盖目标；不足：**未暴露为产品功能**，无定时备份 |
| 20 | 部分适用 | 可从备份恢复/快照恢复路径在 ADR-0002 有描述；不足：**恢复未被产品化、未做周期性恢复演练** |
| 21 | 不适用 | 本地单文件库不做时点恢复；历史以不可变快照与 commit 证据保留 |
| 22 | 适用 | 受管事实的人工删除留下**墓碑**（`object IS NULL` + `managed_value` 保留），非物理删除；人工与映射事实分层不互删 |

### 5.3 服务端校验、时区、Unicode、金额（23–28）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 23 | 适用 | 校验在引擎侧为权威：预览层 `iri()`／`term()` + canonical 判定（`domain_changesets.py:451-465`），存储层 `_fact`（484-495）+ `_definition` + `_check_slot` + `_validate_single_slots`；渲染端校验仅作前置 |
| 24 | 不适用 | 当前无提醒/排程功能；时间戳以毫秒整数存储，未涉时区语义 |
| 25 | 适用 | 撇号等字符不被特殊处理：对象走 Turtle 解析 + canonical 判定，中文对象（`"泵站A"`）在真实 GUI 中通过 |
| 26 | 部分适用 | CJK、NFC/NFD 区分有真实跨语言 golden 覆盖（`tests/unit/t02-manual-fact-id.test.ts` 的 `unicode-nfc`／`unicode-nfd` 且断言 ID 互不相同）；**emoji 与 RTL 未见针对性覆盖** → 不足 |
| 27 | 不适用 | 无金额/货币数据 |
| 28 | 不适用 | 无计费/币种 |

### 5.4 数据模型、幂等、去重、分页、导入导出、留存（29–35）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 29 | 适用 | 能力矩阵（附录 C）为边界主定义；分层为「本体定义／断言事实／当前推导／场景副本／历史运行」；RDF 图只从不可变快照重建 |
| 30 | 部分适用 | 幂等键＝`operationId`／`jobId`（同 operation/job/计划重试返回原标记，不重复写入）；不足：不涉及支付 |
| 31 | 适用 | 去重＝内容派生身份：同 S/P/O 第二次提交被 `reservedIdentity` 拒绝；重复点击产生同 ID → 引擎按内容身份拒绝而非重复建行 |
| 32 | 适用 | 分页为信封式（`startOrdinal/pageSize` + `nextOrdinal` + `complete` + manifest 计数一致性）；变更集 diff 分页与 ownership 详情分页均实现；不足：**未做「第 400 页」规模实测**（本轮只覆盖多页真实读取） |
| 33 | 部分适用 | 导出在 FR-203／FR-1000 范围（非本候选）；本候选不新增导出 |
| 34 | 部分适用 | CSV 导入在 FR-300 范围（非本候选）；存储层只接受「由未来业务层预先校验与预览的映射计划」，不冒充 CSV 能力 |
| 35 | 部分适用 | 留存规则＝历史不可改写 + `collect_cache` 只回收可重建载荷且跳过被固定项；不足：**容量口径与旧超限库恢复仍 HOLD**，无按合同自动删除的实现 |

### 5.5 密钥、依赖、输入处理与 OWASP（36–47）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 36 | 适用 | 本候选范围无凭据；模型网关在 S3 前不接入，引擎不持密钥、不调模型（AGENTS §3「模型外发」）；仓库无 `.env`／运行库入库 |
| 37 | 不适用 | 本轮无密钥轮换面（无凭据产生路径） |
| 38 | 适用 | **我本人实测通过**：vendored fr201.3 wheel 由仓库内脚本在临时目录重建后与提交件逐字节相同（`99fab7bd…`），脚本固定上游/patch/补丁后源码 SHA 并逐成员校验上游 RECORD；`uv.lock` path 源哈希与实测一致 |
| 39 | 部分适用 | 精确版本 + 双锁文件 + vendored 源与许可/NOTICE/PROVENANCE；不足：**无自动依赖扫描 job**（未实测是否有扫描） |
| 40 | 适用 | 输入清洗＝词法/IRI 受控拒绝（`iri()` 拒空白与 `<>"{}|^\`\`、`term()` 解析失败即拒）； lone surrogate 在渲染端被显式拒绝（`mainline-facts.ts` 的 0xD800–0xDFFF 检查）；ownership 详情用 React 文本子节点渲染，不产生 HTML 执行 |
| 41 | 部分适用 | 无 HTTP 端口（无 CORS 面）；CSRF 面不适用（stdio IPC + 渲染端无凭据）；SQL 注入面：动态 SQL 仅以 `sqlite_master`/`PRAGMA table_info` 得到的**库内标识符**拼接并做双引号转义，用户输入不进 SQL 结构（storage/project_host/material_profile）；不足：**未做独立渗透测试** |
| 42 | 不适用 | 无文件上传功能 |
| 43 | 不适用 | 不开 HTTP 端口（AGENTS §3 明令） |
| 44 | 适用 | CSP 唯一配置源 `apps/desktop/src/csp.ts`；本候选**未改** CSP（`git diff` 显示 csp.ts 不在 71 叶内） |
| 45 | 部分适用 | 传输：无网络。静态：SQLite 未加密（本地明文库）→ 已知边界，非本候选引入；不足：无静态加密实现 |
| 46 | 适用 | 最小权限：preload 只暴露按业务命名的方法（新增 `getOwnershipConflictDetailPage` 仍是具名方法，未引入 `invoke(method,params)` 通道）；引擎侧需 `profile=business3` + 选中项目 + 栈内 `_OwnershipProof`（含 origin/session/lease/generation 绑定）；测试中 `ONTOLEARN_TEST_MODE` 仅用于测试夹具且在 `bind` 时被显式排除 |
| 47 | 适用 | 跨边界只传固定错误码与受限参数：conflict 错误只回 `detailRef`，不回异常文本/堆栈/路径/单元格原值；detail 文档只含 id/owner/sourceRow/S/P |

### 5.8 合规、租户运维、环境与交付（48–68）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 48 | 不适用 | 未做渗透测试；面向企业安全问卷的独立测评不在 M0 范围 |
| 49 | 不适用 | 无面向企业采购的安全问卷包 |
| 50 | 不适用 | 无对外漏洞披露流程（无对外发布渠道） |
| 51 | 不适用 | 无生产访问凭据可被窃（无生产环境） |
| 52 | 不适用 | 无 SOC 2 诉求（无客户合规要求在册） |
| 53 | 不适用 | 无患者数据 |
| 54 | 不适用 | 无外部数据处理方（模型网关未接入） |
| 55 | 部分适用 | 审计＝变更审计（commits/commit_evidence、operation/job 标记、快照）；**「谁查看了记录」的读审计**未实现 → 不足 |
| 56 | 不适用 | 无卡数据 |
| 57 | 不适用 | 无个人数据删除请求流程（无用户数据主体） |
| 58 | 不适用 | 无数据驻留合同面 |
| 59 | 不适用 | 无账号体系，无季度访问复核对象 |
| 60 | 部分适用 | 无 dev/staging/prod 三环境（本地应用）；CI 有 Linux/macOS/Windows 三平台差异 → 部分对应 |
| 61 | 部分适用 | CI workflow + electron-builder 配置 + `scripts/build-engine.mjs` 在库内；不足：无完整 IaC（无 Terraform 等） |
| 62 | 适用 | 交付前跑测试：CI 三 job（Quality 15min、macOS/Windows 20min）内含 lint/format/typecheck/vitest/pytest/build/e2e/package/verify。**但 Windows job 当前红（79F）→ 该条未达成**，与 R05-01 同源 |
| 63 | 部分适用 | 撤销一次 ChangeSet 与快照恢复在 ADR-0002 与引擎实现（`intent:'undo'`、preview/confirm）；不足：**本轮 GUI 未覆盖 Undo 路径**（O037 明示不含 Undo GUI） |
| 64 | 不适用 | 桌面应用无停机窗口概念 |
| 65 | 不适用 | 无功能开关体系（本地单版本） |
| 66 | 不适用 | 无自动扩缩 |
| 67 | 不适用 | 无 CDN |
| 68 | 不适用 | 无 DNS/SSL 证书（无在线服务） |

### 5.9 队列、重试、缓存、邮件、成本、灾备（69–89）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 69 | 适用 | 背景作业＝`ExecutionJob`／`JobStore`（stdio 引擎 + 常驻协调器），页面不因长任务冻结（作业状态经 `onTaskUpdate` 推送） |
| 70 | 部分适用 | 重试＝同 operation/job 返回原标记、不重复写入；**无退避（backoff）实现**（本地单用户，失败即显式终态） |
| 71 | 不适用 | 无 DLQ 语义（作业有明确终态 failed/cancelled，不入死信队列） |
| 72 | 不适用 | 无 cron |
| 73 | 适用 | 缓存回收＝`collect_cache` 只清未被 pin 的可重建载荷；失效原因只来自 `invalidation-v2.json`；数据变更即置过期并给重跑入口（附录 D） |
| 74 | 不适用 | 无事务邮件 |
| 75 | 不适用 | 无事务邮件 |
| 76 | 部分适用 | 快照/历史无 GC（ADR-0002 明示「没有快照 GC」）；不足：存储成本随历史增长（Q5 未定） |
| 77 | 不适用 | 当前无模型调用，无用量计费面（FR-903 为 P1） |
| 78 | 部分适用 | 有快照/备份/恢复原语；不足：**无成文且年度演练的灾备计划** |
| 79 | 不适用 | 无多区域部署 |
| 80 | 部分适用 | 结构化证据＝job DTO、commit 证据、快照、receipt（可机读）；不足：无可检索的日志产品 |
| 81 | 不适用 | 无错误追踪服务 |
| 82 | 不适用 | 无外部 uptime 探针（本地应用） |
| 83 | 不适用 | 无值班告警体系 |
| 84 | 部分适用 | 有逐笔事务/版本/快照数据可供核对；不足：无仪表盘 |
| 85 | 部分适用 | 有依据链（完整 Diff / Read / Job / marker 绑定，见 O037）；不足：无跨服务 tracing |
| 86 | 不适用 | 无 on-call（本地开发阶段） |
| 87 | 部分适用 | 有 ADR-0001/0002/0003 与审查/处置文档；不足：无以「队列深度」为口径的 runbook |
| 88 | 部分适用 | 有 R03/R04/R05 意见与处置链；不足：无独立 postmortem 制度化文档 |
| 89 | 不适用 | 无对外状态页 |

### 5.10 测试与质量（90–97）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 90 | 部分适用 | 单测/契约/引擎/GUI 测试由「懂业务语义」的规格驱动（附录 G 用例、真实 Store 交叉验证）；不足：谁写的无法从仓库证明 |
| 91 | 不适用 | 本范围无第三方 API 依赖（仅本地 stdio 引擎与 vendored 库） |
| 92 | 适用 | e2e＝真实 Playwright + 真实 Electron：6 spec 全 PASS，102.6s，57 事务 / 43 拒绝逐笔绑定 |
| 93 | 部分适用 | 有硬预算（行/字节/工作量/帧/对象数准入与 `RESOURCE_LIMIT` 受控拒绝）；不足：**无真实规模压测**，容量口径 HOLD |
| 94 | 适用 | 测试数据＝G-base／G-behavior 固定基线与合成命名空间（ADR-0002 明示不与产品数据混用） |
| 95 | 适用 | 回归集保留旧反例：R03 的 `"设备"@1`／`"设备"@zh1`／4301 位整数与 unknown/HOLD 族均成为常驻回归；旧首败不被新绿覆盖 |
| 96 | 部分适用 | 参考设备/低端硬件实测 **HOLD**（无） |
| 97 | 部分适用 | 新增视图使用 `aria-label`、`role="alert"`、`role="status"`、`dl/dt/dd` 结构；不足：**未做可访问性审计与辅助技术实测** |

### 5.11 商业、计费与 API（98–113）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 98 | 不适用 | 无订阅/升级 |
| 99 | 不适用 | 无失败扣款重试 |
| 100 | 不适用 | 无发票 |
| 101 | 不适用 | 无销售税 |
| 102 | 不适用 | 无退款 |
| 103 | 不适用 | 无用量计费 |
| 104 | 不适用 | 无年度合同 |
| 105 | 不适用 | 无收入报表 |
| 106 | 不适用 | 无 webhook |
| 107 | 不适用 | 无 webhook |
| 108 | 适用 | 版本化 API：`protocolVersion` 2/3、schema/registry 版本与 `registryHash`、能力清单（`registry.json`）与 fixtures 固定；`version` 变化时隔离 current 指针 |
| 109 | 不适用 | 无 API Key 体系（无对外 API） |
| 110 | 不适用 | 同上 |
| 111 | 部分适用 | 对第三方/上游变更的风险以「锁定精确版本 + 锁文件 + vendored 源可复现 + 上游许可与 PROVENANCE」处理；不足：**上游 rdflib 安全补丁需人工走 repack 流程**（我已核实该流程可复现） |
| 112 | 不适用 | 无 OAuth |
| 113 | 不适用 | 无对外沙箱 |

### 5.12 AI 相关（114–121）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 114 | 不适用 | 本候选无模型路径；FR-803 工具白名单与最终外发检查属后续里程碑 |
| 115 | 适用 | 本候选**不产生任何外发**：无 HTTP 端口、无模型调用；引擎不持密钥 |
| 116 | 不适用 | 无模型用量（FR-903 为 P1） |
| 117 | 部分适用 | 有黄金向量与回归集（含跨语言 golden）；不足：**无模型评估集**（A-10 不在本候选） |
| 118 | 不适用 | 无模型降级路径 |
| 119 | 不适用 | 无模型弃用迁移 |
| 120 | 不适用 | 无 prompt/output 日志（无模型调用） |
| 121 | 适用 | 确定性写入必须人工确认：`session.confirm()` 只由显式确认按钮触发（注释明写「Called only by the explicit human confirmation button」），预览与 Diff 先行，Agent 草稿不自动确认（FR-204/FR-804） |

### 5.13 体验、可访问性与工程卫生（122–147）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 122 | 适用 | 纯本地应用，不依赖外网 |
| 123 | 适用 | 每屏具备空/载入/错误态：新增「正在读取冲突定位…」「冲突详情暂不可用…」「操作未能完成：OWNERSHIP_CONFLICT。事实来源、保留身份或属性约束存在冲突。请核对原记录，修改输入后重新预览；已输入内容保留。」 |
| 124 | 适用 | 错误可操作：冲突给出「核对原记录 → 修改输入 → 重新预览」的下一步，而非泛化文案 |
| 125 | 适用 | 校验失败保留输入：会话 `prepared` 清空但表单内容保留，错误文案明写「已输入内容保留」；且 `invalidateFactPreview()` 只作废预览，不清空表单 |
| 126 | 不适用 | 无邮件 |
| 127 | 部分适用 | 领域内「通知记录」是行为动作产物（附录 E.3）；不足：**无用户可关闭的通知偏好**（无账号体系） |
| 128 | 部分适用 | 撤销＝ChangeSet 撤销 + 快照恢复（引擎与契约层完整）；**本轮真实 GUI 未覆盖 Undo**（O037 明示） |
| 129 | 部分适用 | 有 `aria-label`／`role`／语义化列表；不足：**未做键盘导航与读屏实测** |
| 130 | 部分适用 | 界面文案为中文固定；不足：**无 i18n/locale 框架**，日期与数字未按 locale 格式化 |
| 131 | 不适用 | 桌面工作流无「返回上一页」语义 |
| 132 | 部分适用 | 命名与分层清晰（contracts/engine/main/preload/renderer 分层、注释写明不变量）；不足：核心文件偏大（R05-13） |
| 133 | 适用 | 每轮变更走独立审查（本 R05 为全新第五轮，同版双审＋逐意见处置＋ROOT 接收票） |
| 134 | 适用 | worktree + feature 分支（AGENTS §5）；本轮我在独立 worktree 只读审查，未与他人同 checkout 写文件 |
| 135 | 部分适用 | 精确版本锁定；本地 rdflib 分支意味着「上游两版本之内」的判断需连同 repack 流程评估（R05-09） |
| 136 | 部分适用 | 上游补丁需人工 repack + 哈希更新（有脚本与 PROVENANCE，但无自动化） |
| 137 | 部分适用 | 历史 wheel（fr201.1/.2）按 R04 决定保留作审计来源 → 属「刻意保留的审计件」，非死代码，但增加仓库体积 |
| 138 | 部分适用 | 同 R05-13（行数事实，非缺陷） |
| 139 | 适用 | ADR-0001（桌面框架与进程边界）、ADR-0002（事务源真相与固定输入派生视图）、ADR-0003（常驻协调器与作业）均写明决定与理由 |
| 140 | 部分适用 | 有 `AGENTS.md`＋`docs/`；不足：**未提交**的最新指南其「必读」链接失效（属指南维护事项，非 aff 提交树内容，见 R05-10） |
| 141 | 部分适用 | 有迭代目录与评审归档；不足：交接文档分散、状态文档已过时（R05-04） |
| 142 | 不适用 | 无账号体系，无管理后台 |
| 143 | 部分适用 | 有作业视图、receipt、快照与审查证据可供支持排障；不足：无面向客服的支持台 |
| 144 | 不足 | 未见面向客户的 changelog（本地桌面 MVP，无对外发布节奏）；**非阻断，记录为文档缺口** |
| 145 | 部分适用 | PRD 与 `licenses/NOTICE` 与代码现状一致（含本地 rdflib 修订与 App 内 LICENSE 路径保留的事实）；不足：无对外发布的 terms/privacy 文本（离线 MVP 无对外服务） |
| 146 | 部分适用 | 仓库与包名以产品名 `OntoLearn Studio` 统一（非构建者个人名）；不足：发布主体与域名归属不在本仓可见 |
| 147 | 不足 | bus factor 无法从仓库证明；并行 worktree + 双审 + ADR + D8 人类裁决路径只能部分缓解 |

### 5.14 附件尾部「还需要真人」段（148–160）

| # | 适用性 | 依据／不足 |
| --- | --- | --- |
| 148 | 部分适用 | 本候选由独立审查者逐行阅读 diff 与测试定义（R05），但「读完全部代码再上线」对 1355 源规模只能部分做到 |
| 149 | 适用 | 数据模型先于实现：能力矩阵（附录 C）+ ADR-0002 的数据层次与身份规则先于 FR-200/201 实现 |
| 150 | 适用 | 每次修复的因果被独立复核：本轮我对「43692 是字段限」的旧错误因果重新复算，确认撤回成立 |
| 151 | 不适用 | 无服务器与云账单 |
| 152 | 不适用 | 无支付，无 on-call |
| 153 | 部分适用 | 上游漏洞处置路径＝vendored 源 + repack + NOTICE/PROVENANCE（R05-09）；不足：无自动化 |
| 154 | 不适用 | 无患者数据 |
| 155 | 适用 | 「测试什么它说什么」被反复执行：O037 独立重算 57 事务与 43 拒绝、逐笔 Diff/Read/marker 绑定；旧首败（text001、0e7、O027、093）一律保留 |
| 156 | 部分适用 | 迁移有前向/回滚与失败重开语义（ADR-0002）；不足：无真实活库迁移演练 |
| 157 | 部分适用 | 「说不」由能力矩阵与 P0 边界承担，附录 C 明列不支持构造；本候选**未**扩张能力面 |
| 158 | 部分适用 | 单机本地应用不涉多租户规模；但跨运行一致性依赖未规定的排序（R05-08） |
| 159 | 适用 | 审查者不运行产品也能定位根因（我用静态复算独立得出 Windows 失败的高可信编码假设，与 O032 方向一致） |
| 160 | 部分适用 | ADR + 处置链 + 状态文档保存「为什么」；不足：状态文档未随 head/远端状态更新（R05-04） |

**清单层面的总体判断**：160 项逐条判定、无遗漏无重复（本方脚本复核：适用 **34**、部分适用 **52**、不适用 **72**、不足 **2**，合计 160）；其中**真正需要在本候选上处理的只有清单第 62 项（交付前跑测试）**，其未达成即 R05-01／R05-02；两项「不足」（144 客户可读 changelog、147 bus factor）与其余「部分适用」的缺口均为已知边界或后续里程碑范围，本审**不**建议为满足清单而新增功能。

---

## 6. 无法确认项与下一最小动作

### 6.1 我无法确认（明确不假装检查过）

1. **Windows 79F 的真实根因与真实断言栈**：本轮无远端授权、无 Windows 执行环境；仅有静态编码假设与被取消的日志片段。**另需区分**：79 个 F 是进度输出中观测到的**失败标记**（`observedFailureGlyphsBeforeTimeout`），无最终 pytest 总表，故「哪一类失败」也未确证。
2. **Windows job 在 aff 上的真实结果**：aff 未 push，CI36 的 head 是 58c9；Windows 的 typecheck/build/e2e/package 从未执行。
3. **Quality job 的 packaged recovery**：CI36 中该步 skipped；本地打包与包内原验收证据来自 cb8 制品与更早输出。
4. **aff 候选自产的包与包内运行**：不存在（O036 `packageManufacturedOrExecutedThisTurn: false`）。
5. **非 Windows 平台的 Python 字节/编码路径**：Windows 特有；macOS/Linux 均为 UTF-8 环境。
6. **物理 DB 零写**：O037 明确「完整 Read 相等不等于物理 DB 零写」；本轮未做物理文件比对。
7. **全部 App/engine 自然退出**：只观测到 33 个已知 PID/start 在 0/2/5 秒后缺席；不能推广为全部自然 0 或未知后代已回收。
8. **签名／公证／法律／全平台／参考设备／低端硬件／Undo GUI／全部 ownership 家族 GUI**：一律 HOLD。
9. **O022 被拒 probe 的早期 stdout/stderr/exit/完整 seal**：仍 UNKNOWN；未复刻、未换路径采集。
10. **`docs/architecture/m0-review-and-update-plan-2026-10-19.md` 的候选树内版本**：该文件在候选树中不存在，我读的是归档副本（同哈希）。
11. **R04 两方原结论在 aff 上的适用性**：R04 审的是 cb8；由于 aff 的产品源码与 cb8 逐字相同，其技术条件在「产品实现」层可继承，但**审查结论本身不继承**（ROOT 票 `R04NotInherited: true`）。

### 6.2 下一最小动作（按依赖顺序，均不放大授权）

1. **先取 Windows 真实首败**（解除 R05-01 的信息缺口）：aff 新增的 CI 步骤已具备该能力（打印 `locale.getencoding()`/`utf8_mode`/默认文件编码，并以 `--maxfail=1 --tb=short` 取首个真实栈）。该步骤**只在被 push 的候选的 Windows runner 上执行**；因此其执行属 **ROOT 的远端授权与 push 决定**，不由本审查授权，本轮亦未执行任何远端动作。取得真实栈后再决定是否为「6 处显式 `encoding="utf-8"`」的最小修订。
   - 若真实栈确认编码写出错误：按 O032 的最小范围修订 → **产生新候选** → 必要定点 RED→GREEN → 本地完整 check → 真实 GUI → 新候选双审 → 才谈 push/PR/CI/merge。
   - 若栈指向产品故障：**另列真实修复**，不得用测试修订掩盖。
2. **不改 15/20min 上限、不拆 Quality、不加 retry、不删恢复链**（除非 ROOT 先裁定聚合预算）。
3. **在当前入口更新状态文档**（不改动历史快照数值）：`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 的**当前状态**应反映 aff／PR16／CI36 实况；**58c9 时刻的历史数值（如 Ruff 369）原样保留**（R05-04）。另：`AGENTS.md` 的失效「必读」链接属**指南维护**，不属本候选（见 R05-10）。
4. **制品级证据**：aff 无自产新包与包内运行；ROOT 接收票已以「原 094 未变制品 + 12 docs/1 CI 路径差异」的有界桥接保留该边界，并明确不把旧运行说成 aff 新包运行。**本审不把「另做 aff 制品」写成新的合并前置**，仅登记事实；是否另做由 ROOT 在既有处置范围内裁定（R05-03）。
5. **可选最小补充**（非本轮前置）：M-03 的 4299/4300 整数边界；Z-05 的 16 码逐方法对齐；TS 单测的解释器解析固定（R05-12）。
6. **不得**：以诊断配置可过冒充整候选可过；把「诊断只改日志」写成 79F 已修；把 R04 结论继承给 aff；把 package094 的旧运行写成 aff 新包运行；把 FullRead 相等说成物理 DB 零写；把 PID 缺席说成全部自然 0；伪造缺失的 Windows 栈。

---

## 7. 最终结论

**整个 FR-200／FR-201 候选（`583c05c7` → `aff386f6`，29 提交 / 71 叶 / 1355 源）：ConditionalPass（附条件通过）。**
**合并明确不可；push 在技术上不被 R05-01／R05-02 阻断，但须先有 ROOT 明确授权与同候选双审完成（§10）。**

- **成立的**：FR-200／FR-201 所声称的产品能力在实现、契约、引擎、UI、测试层均可核对成立；同版本地完整 check 绿（O036，173.333s，TS 1892 PASS、Py 3719 PASS/50 SKIP、Ruff 379）；同版真实桌面 GUI 6/6 PASS（O037，57 事务 / 43 拒绝 / 58 附件逐笔绑定）；vendored 依赖可复现且许可已披露（我独立重建验证）；D8 choice-A 的各项必要验证在产品实现与测试层均已落地（非法语言标签 new+真实原 ID edit、数字子段对照、超长整数分类、拒前后完整 Read/身份不变、同 host 后续合法 preview/Diff/确认/Job/marker 成功、未知解析失败 HOLD 不回归）；既有 canonical 输入政策未被静默规范化。
- **未成立、因而不能通过整候选门禁的**：
  1. **R05-01（阻断 merge；不阻断 push 取证路径）**：Windows job 在本候选上**无任何成功证据**（58c9 时 cancelled，aff 时无任何结果）→ 三平台真实 CI 门禁未满足；本候选对该 job 只加诊断步骤，未关闭任何失败。**我不把「Windows 必失败／不可能为绿」写成已证事实**——79F 仍是观测到的失败标记，根因仍属高可信假设，CI36 的 head 也不是 aff。程序性效力见 §10.3。
  2. **R05-02（阻断 merge；属阶段事实而非候选缺陷）**：PR16 仍 open/unmerged，CI36 三 job 中两 job cancelled，Windows 后续步骤与 Quality 的 packaged recovery 从未执行，无任何远端全绿证据；aff 未 push。程序性效力见 §10.4。
  3. **R05-03（事实记录，非新增前置）**：aff 无自产制品与包内运行；ROOT 已以有界桥接保留原 094 未变制品，且产品源码与 cb8 逐字相同（我独立核验）；**不**把「未自产新包」当缺陷，**不**把「另做 aff 制品」当新的合并前置。
  4. **R05-04／R05-05／R05-06／R05-07 等非阻断项**：状态**当前入口**需更新（历史数值不得篡改）、16 码白名单缺集、definitions.triples 与通用 ownership 定位两条延续 OPEN——按原分工处理，不得被记为已关闭。（R05-10 的指南链接问题**不属本候选提交树内容**，归 AGENTS.md 维护。）
- **不改变本结论的既有边界**：签名／公证／法律／全平台／参考设备／低端硬件／容量与旧库恢复／Undo GUI／全部 ownership 家族 GUI／unknown-parser-N3-Store-坏快照-损坏 SQLite 物理保护／standalone EOF 残余／native 与 named App 退出 UNKNOWN／旧 0e7、O027、093、text001 等首败——全部保留，不因本轮绿而消解。
- **本报告的效力边界**：仅为本方 R05 独立审查结论与证据，不构成 ROOT 接收、不授权 push／PR／CI／merge、不改变整体 2/17。

---

## 8. 本方实际执行的命令（全部只读；临时产物只写在我自己的 `/tmp` 目录）

- 读附件与核清单：`read`（全文两段，至 EOF）＋ `shasum -a 256` ＋ `wc -c` ＋ Python 偏移/字节计数（清单 11255 B、SHA `1ca23def…`）。
- 身份与范围：`pwd`、`git rev-parse`（branch/HEAD/HEAD^{tree}/base^{tree}）、`git rev-list --count`、`git diff --name-status/--stat`、`git ls-tree -r`、`git log --oneline`、`git status --porcelain`、`git worktree list`、`git diff cb8c9b7a..aff386f6`（逐前缀）。
- 源码只读：`sed`／`grep`／`read`（storage.py、job_store.py、mainline.py、project_host.py、domain_changesets.py、query_presentation.py、coordinator.py、rdf_snapshot.py、contracts v2.ts/index.ts、schema.json、errors.json、fixtures/registry、renderer 5 个文件、main/preload、ci.yml、pyproject/uv.lock/NOTICE、repack 脚本、7 个新增 Python 测试、4 个新增 TS 测试、e2e spec）。
- 纯计算（写入仅 `/tmp`）：Node 对拍手写 SHA-256（10 例）；wheel 重建对拍（`python3 scripts/repack-rdflib-input-types.py --upstream … --patch … --output-dir /tmp/…`，产物与仓库件 `cmp` 逐字节相同）；4 个 wheel 的成员/RECORD/压缩方式核对；`uv.lock` 哈希比对；schema/错误码集合运算；清单条目计数。
- 外部证据只读：`cat`／`grep` O032、O035、O036、O037、ROOT 接收票、D8 决定单、choice-A 授权、归档 M0 计划副本、package094 边界记录、R04 双方终稿与处置链及两份独立处置核验。
- **未执行**：npm/vitest/pytest/ruff/build/package/install/sync/HMR/GUI/e2e；任何远端动作；任何对旧 DB／用户 profile 的读写或恢复；未打开被拒 probe。

---

## 9. 事实限定复核修订记录（仅事实修订，结论不变）

**被修订的原终稿**：65672 B／SHA-256 `26d4dbe2b39348e89b3cbd7c7307b98c33e0dd199e96e101f94adfe7fd4c9951`（该身份保留在案；本文件为修订版）。**复核范围**：同一 R05 原任务内的 5 项具体事实限定；**只修改本方报告**；未读另一方 R05；未跑产品／tests／build／GUI；**不改变**「ConditionalPass + CI 门禁阻断」的结论。

| # | 复核要求 | 我的实测依据 | 处置 |
| --- | --- | --- | --- |
| 1 | R05-01 及「Windows job 不可能为绿」是否超过高可信假设证据？区分「未满足 CI 门禁」与「预测必失败」 | 79 F 是 CI36 **进度输出中的失败标记**，无断言 traceback／无最终 pytest 总表（O032 `noFailureAssertionTracebackOrFinalPytestSummary: true`）；根因未实测；CI36 head 为 58c9（非 aff，实际 checkout 为合成 `681ffbd0…`） | **采纳**：删去「不可能为绿／必失败」断言，改为两分表述——**事实**：Windows 无任何成功证据 → 三平台 CI 门禁未满足；**假设下的预期**：若 79F 成因成立，预计仍红。阻断性保留，但依据改为门禁未满足 |
| 2 | R05-03 不得把「重打包／再审批」写成尚未授权的新前置 | ROOT 接收票已含 `packageBoundary: "Original unchanged 094 artifact prior runtime retained; no new packaging or packaged runtime at aff"`、`oldRuntimeEvidenceNotRelabeledAsNewHeadRun: true`、`allChangesOnly12EvidenceDocsPlus1CIPath: true` | **采纳**：R05-03 改标「事实记录，不新增前置」；删除「需在合并前闭环」与「产出一次 package:dir」的祈使表述；§6.2 第 4 项与 §7 第 3 项同步改写；**保留**「本候选无自产新包、不可写成 aff 已包内验收」的边界陈述 |
| 3 | status 为冻结历史快照；Ruff 369 是 O029 真实值，O036 379 是另一实测；区分「当前入口更新」与「篡改历史」 | 实测 O029 `full-check-01.stdout.log:106-107` = `All checks passed!` / `369 files already formatted`，`readback.json` 亦记 `RuffFormattedFiles: 369`；O036 `check-attempt-02.stdout.log:107` = `379 files already formatted`（不同 head、不同文件数） | **采纳**：R05-04 改为「当前入口需更新；历史数值不得篡改」，明确 369 与 379 是**两个快照的两次实测**、不是矛盾也不是记录错误；把 Ruff 数值从「与事实的差距」清单中移除，只保留 head/tree/提交/叶/源、PR16、CI36 的当前入口更新项 |
| 4 | R05-10 的未提交 AGENTS 不属 aff 提交树内容，只归指南维护 | `git show aff386f6:AGENTS.md` = 旧 10 行版，`m0-review-and-update-plan` 命中 **0** 次；失效链接仅存在于工作树中**未提交**的指南（`git diff --stat` = +101/-10） | **采纳**：R05-10 改标「**非本候选范围｜归指南维护**」，明确 aff 提交树内不存在该缺陷、不计入候选缺陷清单；§1.1／§2.1／§5 第 140 项／§6.2／§7 的引用同步更正 |
| 5 | R05-12 文件引用有误，须实际读源码纠正；并检查前文同类引用 | 实测：`tests/unit/t01-mainline-contract.test.ts:656` = `execFileSync('python', ['-I','-B','-c',script], {cwd: root,…})`；`tests/unit/t01-ontology-metadata-contract.test.ts:168` = `execFileSync('python', …)`；`tests/unit/t02-manual-fact-id.test.ts:66-68` = `spawnSync(resolve('.venv/bin/python'), …)`（**非** PATH python）；**不存在** `tests/unit/t02-mainline-contract.test.ts` | **采纳**：R05-12 逐行更正三处引用并删除不存在的文件名；§2.4 表格中 O035 行补注「日志原文措辞为 spawnSync python ENOENT，实际调用点见 R05-12」。前文同类引用（§2.3 的 `t02-manual-fact-id.test.ts` 跨语言测试表述、§4 的 M-06 行、§5 第 26 项）经复核**均属实**，未改 |

**本轮复核新增的只读命令**（不跑产品／tests／build／GUI）：`ls tests/unit | grep`、`sed -n` 三个测试文件对应行、`git show aff386f6:AGENTS.md`、`grep` 该提交版 AGENTS.md 的链接命中数、O029 与 O036 的 stdout 行核对（`369/379 files already formatted`）、O029 `readback.json` 的 `RuffFormattedFiles`、本报告内引用字符串自检。**未新增任何运行、安装、打包或远端动作。**

---

## 10. R05-01／R05-02 的程序性效力（仅依据原 Goal 与已给原件，不预设结论）

### 10.1 我据以判断的正常顺序（原件原文，非我自拟）

| 闸门 | 原件依据（原文/字段） |
| --- | --- |
| **G1 本地验收** | choice-A `requirements`：「定向回归+完整check→真实GUI及原包内验收→冻结源码构建证据→fresh指定双审与全部意见处理」；「同新候选双Pass且无阻断才push→PR→CI→merge→remote」 |
| **G2 同候选双审＋无阻断** | 同上（「fresh指定双审与全部意见处理」）；ROOT 接收票 `freshR05Required: true`、`R04NotInherited: true`；AGENTS.md（未提交最新指南）第 58 行「操作政策更新不改变冻结候选、指定双审与发布门禁」、第 67 行「每条开发线独立验证并履行现行评审门禁…保留双指定模型、CI 和远端核验要求」 |
| **G3 push→PR→CI（完整远端 CI，合并前必需）** | choice-A requirements 原文顺序；归档 M0 计划 §4「进入下一阶段的条件」以验证/评审为前提；ROOT 接收票 `mayPushOrMerge: false`、`mergedUsableFRs: "2/17"` |
| **G4 merge→remote** | choice-A requirements（「push→PR→CI→merge→remote」）；ROOT 授权暂停 |

### 10.2 三条决定性程序事实（我本人实测）

1. **G1 对 aff 的内容成立**：O036 执行时 HEAD 为 `58c9bbb`，但工作树的 `ci.yml` blob 已是 `94d0bb5a1a47c057e05fddbce5e4c73abd7582f3`——**正是 aff 的 ci.yml blob**（我实测 `git rev-parse aff:.github/workflows/ci.yml` 同值），而 `58c9→aff` **仅** ci.yml 一处变化（`git diff --name-status` 仅 `M .github/workflows/ci.yml`）。故 **O036 的完整 check（exit 0）所检查的工作树与 aff 的树逐字相同**；O037 的真实 GUI 亦在 aff 的构建（main `4309328d…`）上执行，6/6 PASS。
2. **取得 Windows 首败真栈的机制只存在于 push 之后**：aff 新增的 CI 步骤（打印 `locale.getencoding()`／`utf8_mode`／默认文件编码，并以 `--maxfail=1 --tb=short` 取首个真实栈）**只在被 push 的候选的 Windows runner 上执行**。这正是 O032 最小动作票第 1 条所要求的取证手段（「先诊断，单独授权实际Windows入口…各独立命令，-vv --maxfail=1 --tb=short，保留真实stdout/stderr/exit与trace」）。
3. **79F 的观测对象不是 aff**：CI36 的 head 是 58c9，实际 checkout 为合成提交 `681ffbd0…`；aff 从未 push，其远端平台门禁**在程序上尚未产生过任何结果**。

### 10.3 ① 79F 尚未定位／未修（候选问题）

- **性质**：**候选问题**。涉事的三个测试文件自 cb8 起即在候选内，aff 未修改；`write_text(...)` 无 `encoding=` 且载荷含中文这一源码事实与失败分组吻合。
- **是否阻断正常 push 取证路径：否。** 理由：
  1. 该观察来自**平台阶段**（58c9 的远端 Windows job）。候选在程序上尚无该平台门禁结果；把平台阶段的失败当作 push 的前置条件，等于要求一个尚未产生的门禁先通过。
  2. 取证手段（aff 自带的诊断步骤）**只在 push 后可用**。若以 ① 阻断 push，则取得真实首败的唯一路径被自我封闭——这与 O032「先诊断」的既定动作票直接冲突。
  3. O032 明令：在取得真实栈之前**不得**先改测试掩盖、不得盲改、不得以 trace 修订掩盖产品故障；因此「先 push 取证、再定修复」是原件规定的唯一合规次序。
  4. G1（本地验收）对 aff 内容已满足、G2（同候选双审）正在按程序进行；push 是 G2→G3 的**取证动作**，不是绕过 G1／G2 的后门。
- **但我明确保留**：① 是 **High 级、尚未关闭的候选问题**；它**不得**被表述为「已修」「可忽略」「只是日志」；其根因仍是**高可信假设**而非确证。
- **是否阻断 merge：是（确定）。** merge 前必需完整远端 CI；Windows job **从未在候选上成功过**（58c9 时 cancelled，aff 时无任何结果）。① 未关闭前不存在可合并的候选。若诊断确认为编码写出错误 → 最小修订产生**新候选** → 新候选须重新满足 G1 与 G2 → 再走完整 G3；merge 只能发生在**某个候选的完整三平台 CI 全绿**之后。

### 10.4 ② aff 未获准 push，故尚无 aff 远端 CI（阶段事实）

- **性质**：**阶段事实，不是候选缺陷**。候选内容中不存在「缺少远端 CI」这种可由代码修复的东西。
- **是否阻断正常 push 取证路径：否。** 它是 push 的**前提**而非其障碍；不存在「push 取证被自身阻断」的逻辑。此处不存在需要我判断的技术裁量。
- **是否阻断 merge：是（且为必然）。** G3 要求**候选自身**的完整远端 CI；候选尚无 → G3 未完成 → G4 不可进入。此结论不依赖 ① 的根因是否成立，也不依赖任何预测。
- **授权状态**：ROOT 接收票明载 `mayPushOrMerge: false`、`mergedUsableFRs: "2/17"`，属**授权暂停**。我上一轮提到的「可选诊断例外」**未获真人答复，按任务票与本轮指令均不构成授权**；我在本报告中也不将其当作授权使用。

### 10.5 我对「当前候选可否 push」的独立原判（保留并精确化）

- **维持的独立判断**：**当前候选不可 merge。** 依据为 G3 未完成（无候选远端 CI）＋ ① 未关闭 ＋ ROOT 授权暂停；这三条均不依赖任何对 Windows 失败的预测。
- **同时明确、且不回避**：**我不再把 ① 或 ② 主张为 push 取证路径的技术阻断**（理由见 10.3、10.4）。上一轮我在 §0／§7 写的「不可按现有门禁直接 push／PR／CI／merge」把 push 与 merge 并列，**在 push 这一层过宽**，据此精确化如下：
  - **merge**：明确不可（G3 未完成、① 未关闭、授权暂停）。
  - **push**：**不被 ①／② 技术性阻断**，但须先满足两项**不在我裁量内**的前置：(i) ROOT 的明确 push 授权（当前为授权暂停，无人答复的例外不是授权）；(ii) G2 完成——同一候选的两份双审终稿与 ROOT 对全部意见的逐项处置（含本 R05）。
- **我不因此宣称「可以 push」**：授权与 G2 完成度的判断不属本审查职权；我只提供技术侧判断与条件。
- 本轮**未执行任何远端动作**，也未把「取证需要 push」解读为已获 push 许可。

### 10.6 不得由本次程序性分析推出的结论

- 不得推出「本候选可以 push」（授权与 G2 完成度不在我处）；
- 不得推出「79F 可忽略／不是问题」（它是 High 级未关闭候选问题，只是**不**是 push 前置条件）；
- 不得把 58c9 的 CI 结果表述为 aff 的结果，也不得把 aff 自带诊断步骤的可过表述为候选可过；
- 不得把 G1／G2 已满足表述为 G3／G4 已满足；
- 不得把无人答复的「可选诊断例外」当作任何授权。
