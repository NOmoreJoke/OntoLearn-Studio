# T02 `cb8c9b7a` / package094 — R04 独立完整工程审查（MiniMax M3.1-Flash）

> 本报告为**本方（MiniMax M3.1-Flash）**独立审查原件。同目录 `zcode-glm53.md` 为另一方报告，**本方未读取其任何内容**（仅在列举目录项时看到文件名与字节数 54252B，未打开、未引用）。
> 本轮为**全新独立**审查，不预设 Pass/Fail；旧轮次结论不作为本轮依据，仅作为「历史必须披露」的材料来源。

---

## 0. 审查主体、可复算身份与边界声明

| 项 | 实际值 | 取得方式 |
| --- | --- | --- |
| 模型 | MiniMax M3.1-Flash | 运行上下文自报 |
| 思考等级 | xhigh | 运行上下文自报 |
| 权限 | always-authorize（始终授权） | 运行上下文自报 |
| 审查模式 | 只读实现审查；唯一可写文件为本报告 | 任务约束 |
| 实际 cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | `pwd` |
| branch | `feature/weekly-t02-fr200-fr201` | `git rev-parse --abbrev-ref HEAD` |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 任务给定 + `git merge-base --is-ancestor` 通过 |
| head | `cb8c9b7a5d780544b2910901ec9141236905d65c` | `git rev-parse HEAD` |
| tree | `b8010eea4e04f962598a80d767b7a9ea24d2d7e7` | `git rev-parse HEAD^{tree}` |
| 累计提交数 | 27（`git rev-list --count base..head`） | 实测 |
| 累计 diff 叶 | **58**（`git diff --name-only base..head \| wc -l`） | 实测，与任务给定一致 |
| tracked 文件 | **1344**（`git ls-files \| wc -l`） | 实测，与任务给定一致 |
| 远端 develop | `git ls-remote origin develop` = `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 实测（本地 develop ref 陈旧为 `5f910b5…`，已按远端为准） |

**附件核验**：附件 `/Users/kyle/.minimax/v2/assets/2026/10/25/12-14-21-586-asset_20261025-121421-586_f0a7c9ea83e8_a891b2a7-pasted-text.txt` 分两段读至 EOF（211 行），`wc -c` = **24561**，`shasum -a 256` = **f0a7c9ea83e81055d77df49e41a4ebb35dc8d0579ee49395929f3101a7ff4daf**（与给定完全一致）。用户原清单位于第 42–211 行，标记首行/末行各出现 1 次，EOF 后无附加字符。

**dirty 归属（`git status --porcelain=v1`，审查全程未变）**

| 状态 | 路径 | 归属与处置 |
| --- | --- | --- |
| ` M` | `AGENTS.md` | 用户政策覆盖件（15147B，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`；HEAD 版本仅 1056B）。已读取最新内容，**未修改** |
| `??` | `docs/reviews/T02/fr200-fr201-20261024/round-01/` | 既存历史报告（minimax-m31flash.md + zcode-glm53.md），受保护，未读未改 |
| `??` | `…/round-02/` | 同上 |
| `??` | `…/round-03/` | 同上（本轮**读取** round-03 两份源报告作为历史对照，见 §5；未改） |
| `??` | `…/round-04/` | 本轮开始时**不存在**；其后由另一方创建 `zcode-glm53.md`（54252B）。本方**未读取**，本报告写入 `…/round-04/minimax-m31flash.md`（本轮唯一新增文件） |
| tracked | `docs/reviews/T02/fr200-fr201-20261024/independent-review-source-94e20d4a.md` | 本候选 diff 之一，属受审内容 |

**本轮未执行**：未改任何源/测试/配置/依赖/AGENTS/旧报告/状态文件；未安装、未 build、未制造包；未 commit / push / 切分支；未运行产品、未开旧 DB、未启动 Electron/GUI 进程；未并发争用 GUI 或可变运行数据；未读取另一方 round-04 报告。

**本轮实际执行**均为只读或进程内纯计算探针（§13 列出）。因产品冻结，未无变化复跑全量 `npm run check` / `npm run test:e2e` / `npm run package:dir`。

---

## 1. 范围与需求依据

- **需求依据**：`docs/prd/PRD-本体学习与落地Agent工作台.md` 第 307–319 行（FR-200 业务概念管理【P0】、FR-201 结构关系与实例事实创建【P0】）。
- **身份政策依据**：`docs/iterations/I01/ADR-0002-storage.md` 第 27 行（新建事实 ID 是初始三元组规范数组的 SHA-256；**对象必须等于 `term(value).n3()`**；统一 xsd:string/语言标签及字面量词法后派生身份，**非规范别名拒绝提交**；显式 `edits={factId:object}` 保持记录身份与映射基线，编辑后 ID 仍是初始内容摘要；墓碑同样保留初始 ID；新来源既不能占用该保留身份，也不能接管相同有效语句）。
- **工程门禁依据**：仓库 `AGENTS.md`（第 1/2/3/4/5/6/7 节）与 `docs/m0-checklist.md`。
- **本候选实现**：`packages/engine/src/ontolearn_engine/`（`project/mainline.py`、`project/project_host.py`、`project/domain_changesets.py`、`project/query_presentation.py`、`storage.py`、`job_store.py`、`rdf_snapshot.py`、`coordinator.py`）、`packages/contracts/src/{v2.ts,index.ts}`、`packages/contracts/v2/schema.json`、`apps/desktop/src/{main,preload,renderer}`、`packages/engine/vendor/rdflib/*`。

---

## 2. 原需求上下文补齐（既有需求，不是新政策，不改变验收）

按本轮补充要求，本方全文读取并核对了以下**原决定原件**（绝对路径与行号如下，便于复核）：

**原决定文件**：`/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/six-patches-20261023/T02-package092-R03-disposition-and-D8-decision-20261025.md`（全文 52 行）

- **第 13 行**（语言标签判定口径）：「语言标签应按实际首子段约束判断：`1`、`zh1`等非法；`en-001`、`de-CH-1901`等后续数字子段合法，**不能一概拒绝数字结尾标签**。超4300位裸整数是本次语料观察到的另一个普通ValueError抛点，未保存其独立host级完整复现；"仅两个抛点/有限族穷尽"只能限于本次采样，不能证明全解析器穷尽。」
- **第 40 行**（必要验证范围与实现约束）：「必要验证范围：已确认非法语言标签new + 真实已提交原ID的edit；**合法数字子段对照**；**超长裸整数分类评估**；拒前后完整Read/身份不变、同host后续合法preview/全Diff确认/Job/marker成功；原未知parser/N3/Store/坏快照HOLD反例保持；同版完整check、实际GUI及包内原验收，再取得同新候选双Pass才能push→PR→CI→merge→remote。具体实现**选抛点专用类型或受控语法预检，不泛捕ValueError、不按异常文案分类、不静默normalize、不放宽cap**。」
- **第 24 行**（R03-04 / Z-R03-01 处置）：「采纳OPEN非阻断延期，当前UI生成canonical且不可达；Z有wire实测，MM为源码核对。T01在接线原始triples/Agent前处理，**不能说已修**。」
- **第 36 / 38 / 44 行**（D8 原文与选择 A）：「同一候选双审第3轮仍不过 → 升级用户人工裁决，裁决为终态，禁止R4+。」；推荐选择 A 明确「解除 T02 本功能的 R4+ 限制」，文末「用户尚未决定。」为**当时历史状态**，用户其后已采纳选择 A。

**R03 原报告（本方实际读取的路径与行）**

- `docs/reviews/T02/fr200-fr201-20261024/round-03/minimax-m31flash.md`
  - 第 5–13 行：R03 Fail 结论与 T02-R03-01 等条目。
  - **第 102 行**：`_is_valid_langtag` 正则 `^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$`；`1`/`2024`/`zh1`/`a1`/`zh2` 失败；`zh`/`ZH`/`zh-CN`/`zh-Hans-CN`/**`en-001`**/**`de-CH-1901`**/`sl-rozaj` 合法。
  - 第 145/162/167–179/271/281/472/483–486 行：探针矩阵与残余族。
- `docs/reviews/T02/fr200-fr201-20261024/round-03/zcode-glm53.md`
  - 第 65 行：fr201.2 补丁五类异常类清单。
  - 第 80 行：`classify()` / `observe_error()` 语义——裸 `ValueError`/`AssertionError`/`IndexError`/`KeyError`/`RuntimeError` → `INTERNAL_ERROR` 空 params（无文案泄露）；`observe_error` 非 JobFault/ServiceFault → `unknown=True; hold=True`。
  - 第 102 行：R02 最小修复成立性判定（`term()` 一行捕获 `(BadSyntax, Notation3InputError)` 即把两类新错误并入 `TermInputError`）。
  - 第 113 行：R03-01【低/非阻断】`definitions.triples` wire 面已知调用方输入仍升级为 INTERNAL_ERROR/HOLD。
  - 第 163 / 170 行：canonical 窄口径——事实面全闭，definitions wire 面开放为 R03-01；Z-R02-01 维持开放。
  - 第 337 / 354 行：清单「修一 bug 造两个」适用·通过；R02 唯一阻断已关闭。

**本轮定位声明**：以上均为**既有需求上下文补齐**。本轮不因补齐而改变验收范围，不接受也不拒绝任何预定结论。任务初始 prompt 中「当前实现拒绝 `de-CH-1901`」的描述**不构成用户对新语义的另行批准**；本轮对该行为的评价一律回溯到第 13 行、第 40 行与 ADR-0002 第 27 行。

---

## 3. `de-CH-1901` 边界的独立评估（本轮核心判定）

### 3.1 问题陈述

当前候选对 `"设备"@de-CH-1901` 的**产品级结果**是拒绝（受控 `INVALID_REQUEST`），而 `de-CH-1901` 按第 13 行的语法口径**是合法的**。二者并不矛盾，但必须把两个**独立维度**分开，否则会误读为「实现把合法标签一律按非法拒绝」。

| 维度 | 含义 | 本候选实际行为 | 依据 |
| --- | --- | --- | --- |
| **(a) 语法合法性** | 语言标签是否满足首子段约束 | `de-CH-1901` → **合法**；`1`/`zh1`/`a1`/`2024` → **非法** | vendored patch `packages/engine/vendor/rdflib/notation3-input-types.patch` 第 127–134 行：`RDFSink.newLiteral` 中 `if lang is not None and lang != "" and not _is_valid_langtag(lang): raise InvalidLanguageTagError`；`_is_valid_langtag` 复用 rdflib 既有校验器 |
| **(b) canonical 拼写策略** | 字面量的规范 N3 串是否与输入逐字相等 | `de-CH-1901` → n3 为 `de-ch-1901`（语言标签被小写化），≠ 输入 → **非规范别名，拒绝提交** | ADR-0002 第 27 行「对象必须等于 `term(value).n3()`…非规范别名拒绝提交」；实现位于 `packages/engine/src/ontolearn_engine/rdf_snapshot.py:57`（`Literal(str(result), lang=result.language.lower())`）与 `packages/engine/src/ontolearn_engine/storage.py:491-492` |

### 3.2 本方独立实测（只读、进程内）

```
.venv/bin/python（仓库内实装 rdflib 7.6.0+ontolearn.fr201.3）
```

1. **校验器源码**：`rdflib.term._is_valid_langtag(tag) -> bool(_lang_tag_regex.match(tag))`，`_lang_tag_regex.pattern = ^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$`（flags=32）。
2. **13 个标签实测**：`de-CH-1901`=True、`de-ch-1901`=True、`en-001`=True、`en-US`=True、`en-0`=True、`en-0a`=True、`en-001-x`=True、`i-navajo`=True、`x-private`=True、`x`=True ⟶ 合法；`zh1`=False、`1`=False、`a1`=False ⟶ 非法。
   → **该正则在语法层面只约束「首子段必须纯字母」，并不拒绝「后续子段含数字」**，与第 13 行「不能一概拒绝数字结尾标签」**完全一致**。
3. **产品语义实测**（`rdf_snapshot.term()` + `parsed.n3()`）：
   - `"设备"@de-CH-1901` → n3 = `"设备"@de-ch-1901`，canonical=**False** → 预览守卫 `domain_changesets.py:464-465` 判 `INVALID_REQUEST`。
   - `"设备"@de-ch-1901` → canonical=**True** → 可提交（正控）。
   - `"设备"@en-001` → canonical=**True** → 可提交（正控）。
   - `"设备"@1` → `TermInputError`（cause=`InvalidLanguageTagError`）→ 受控 `INVALID_REQUEST`。
   - `"设备"@zh1` → 同上。
4. **策略先于本候选存在（关键）**：`git show 583c05c…:packages/engine/src/ontolearn_engine/storage.py` 第 450–454 行已有 `if term(fact["object"]).n3() != fact["object"]: raise ValueError("Canonical RDF object required; derive ID from term(value).n3()")`；`git show 583c05c…:packages/engine/src/ontolearn_engine/rdf_snapshot.py` 第 47 行已有 `Literal(str(result), lang=result.language.lower())`；base 中 `TermInputError` 出现次数 = **0**。
   → **canonical 拼写策略是既有 ADR-0002 策略，不是本轮新语义**。本候选做的是把该拒绝从「普通 `ValueError`」（基线路径下会逃逸为 `INTERNAL_ERROR` + 会话 HOLD）**收敛**为「受控 `INVALID_REQUEST`」。
5. **对照实现与测试**（本候选内）：
   - `packages/engine/tests/test_mainline_language_input_rejection.py:31-40`：`R03_REFUSALS` 含 `"设备"@1`、`"设备"@zh1`、`"9"*4301`；`CANONICAL_TAGS = ('"设备"@en-001', '"设备"@de-ch-1901')`。
   - 同文件 `:52-55`：`test_digit_subtags_are_grammatical_separate_from_canonical_case_policy` 断言 `de-CH-1901` **语法合法但 n3 小写**（正是本节两个维度的显式分离）。
   - 同文件 `:320-321`：`test_canonical_digit_subtags_still_commit_over_stdio`——canonical 数字子段标签经独立 stdio 仍能 commit。
   - 同文件 `:325-326`：`test_grammatical_uppercase_subtag_keeps_existing_canonical_rejection`——`de-CH-1901` 维持既有 canonical 拒绝。

### 3.3 判定

1. **第 13 行「不能一概拒绝数字结尾标签」→ 已满足**。实现的语法闸门是「首子段纯字母」，`en-001`/`de-CH-1901`/`de-ch-1901`/`en-0` 等后续含数字子段**均不被语法拒绝**（实测 13 例）。不存在「一概拒绝数字结尾标签」。
2. **第 40 行要求的三组验证 → 已实现并有独立 stdio 证据**：① 非法标签 new + 真实已提交原 ID 的 edit（测试 `:313-326`，且 GUI 第六例 fresh cohort 有 rev13/rev20 后继合法链）；② **合法数字子段对照**（`CANONICAL_TAGS` 正控 + `de-CH-1901` 对照）；③ 超长裸整数分类评估（见 §4.2 与 §6.4）。第 40 行末尾的实现约束（不泛捕 ValueError / 不按文案分类 / 不静默 normalize / 不放宽 cap）亦全部满足（§6.2 给出代码级证据）。
3. **拒绝 `de-CH-1901` 的直接原因是 canonical 拼写而非语法非法**——这属于既有 ADR-0002 第 27 行策略（先于本候选存在），本候选只改变了它的**错误分类**（普通 `ValueError`/会话 HOLD → 受控 `INVALID_REQUEST`），**未改变可接受集合**。
4. **对「当前实现是否满足既有需求」的回答：满足。** 「语法合法但被拒」不是矛盾，而是「语法合法 + 非规范拼写 = 按 ADR-0002 拒绝提交」这一既有组合规则的结果。
5. **本轮明确记录的边界**（避免被误读）：
   - 实现**未**把合法标签一律按非法拒绝；
   - 实现**未**静默 normalize（`de-CH-1901` 不会被改写为 `de-ch-1901` 后接受，而是明确拒绝）；
   - 实现**未**放宽 cap（4300 位上限保持，见 §6.4）；
   - 用户看到的错误是统一的 `INVALID_REQUEST`，**不区分**「语法非法」与「非规范拼写」——这是**错误码粒度**问题（见 §9 缺陷 T02-R04-05 的相邻观察），第 13 行**并未要求**产品面区分二者，故不列为需求违反；若产品希望区分，属新增产品语义，需用户/总控决定，本轮不代为决定。
6. **本节结论的适用范围**：仅覆盖语言标签与 canonical 拼写这一条语义线；不覆盖 §5 的其他 R03 历史项。

---

## 4. R03 历史问题的独立处置验证

| R03 条目 | 原判定 | 本候选现状（本方独立核对） | 本轮处置 |
| --- | --- | --- | --- |
| **T02-R03-01 / MM**：数字首子段语言标签、超长整数异常未分类 → 逃逸为 `INTERNAL_ERROR` + `host.hold=True`，后续 `project.read`→`STORAGE_FAILURE`（round-03/minimax 第 102 行；zcode 第 80 行） | **R03 阻断** | vendored patch 新增 5 个 `Notation3InputError` 子类；`rdf_snapshot.py:42-43` 新增 `except (BadSyntax, Notation3InputError) → TermInputError`；`domain_changesets.py:462-463` 捕获 `TermInputError → INVALID_REQUEST`。**实测**：`"设备"@1`、`"设备"@zh1` → `TermInputError`（受控）；`"9"*4301` → `TermInputError`（cause=`IntegerDigitLimitError`） | **已实质关闭**（阻断项解除） |
| **R03-02 / R03-03**：canonical 窄口径（`de-CH-1901` 事实面 vs definitions wire 面） | 事实面关闭、wire 面开放 | 事实面 canonical 判定由基线既有策略 + 本候选守卫共同保证（§3.2 第 4/5 点）；wire 面见下 | 事实面**维持关闭**；wire 面**维持开放**（下条） |
| **R03-04 / Z-R03-01**：`definitions.triples` wire 面已知调用方输入仍升级为 `INTERNAL_ERROR`/HOLD（round-03/zcode 第 113、170 行） | **OPEN 非阻断**（R03 处置第 24 行明示「不能说已修」） | 引擎侧 `storage.py:1118-1129` 的 `_definition` 走 `term(obj)` 单值路径；已类型化异常族 → `INVALID_REQUEST`（`domain_changesets.py:474-477` 捕获 `ValueError/KeyError/TypeError`）；**文档级解析路径的未分类 `IndexError` 仍在**（§9 T02-R04-04） | **维持 OPEN 非阻断**。本轮未发现其状态变化；**不声称已修** |
| **Z-R02-01**：首次 137 PASS / 2 身份 FAIL → 最终 139 PASS；standalone 恰 EOF 8 IndexError 未分类仍 OPEN | 非阻断 | standalone EOF IndexError **仍可复现**（§9 T02-R04-04） | **维持 OPEN**，按原披露口径保留 |
| **O026**：canonical 四正例隔离到第六例（fixture 适配） | 容量隔离，非修复 | 本方未复跑，仅记录 | 维持历史口径：隔离≠容量修复 |
| **O027**：`a0` 完整 check 真实 3 FAIL（ownership core-only 误 `RESOURCE_LIMIT`；两个 clean successor `PERMISSION_DENIED`） | 历史首败 | 本方未复跑 | 维持历史原件，不因当前绿而改写 |
| **旧 0e7**：TS 1891 PASS + 1 TIMEOUT；GUI 四 CRUD PASS、FR201 FAIL（commit rev24 但 projection 23） | 历史首败 | 本方未复跑 | 维持历史原件 |
| **旧 41a**：package093 原 18 真实 13 PASS / 1 FAIL / 2 SKIP / 2 NOTRUN | 历史 | 本方未复跑 | 维持历史原件 |
| **text001**：第一次 ASCII 失败、Unicode NOTRUN（错误 fixture 精确 vector 预期 + secondary cleanup TypeError） | 历史 | 本方未复跑 | 维持历史原件；source002/003 仅改外部 spec |
| **R03 处置第 40 行「同版完整 check、实际 GUI 及包内原验收，再取得同新候选双 Pass」** | 门禁 | 本方本轮**未复跑**完整 check / GUI / 包内原验收（只读约束 + 产品冻结）；仅对已归档 raw 做独立重算（§7） | 本轮**不代替**该门禁，仅就本范围给结论 |

---

## 5. 本候选实现与依赖闭包的独立审查

### 5.1 语言标签/词法受控拒绝的实现链路（自下而上）

1. **vendored patch**（`packages/engine/vendor/rdflib/notation3-input-types.patch`）：新增 `Notation3InputError` 基类 + `RelativeIRIBaseError`、`UnicodeCodePointError`、`UnterminatedStringError`、`MissingDatatypeError`、`InvalidLanguageTagError`、`IntegerDigitLimitError`；`RDFSink.newLiteral` 用 `_is_valid_langtag` 校验语言标签；`nodeOrLiteral` 的整数分支用 `sys.get_int_max_str_digits()` 显式判超限；`uri_ref2` 负返回显式抛 `MissingDatatypeError`；`strconst` 的 `assert m` 改为 `UnterminatedStringError` 并补尾部反斜杠检查。**patch 已确认存在于 wheel 内**（`unzip -p <wheel> rdflib/plugins/parsers/notation3.py` 可读出新增类）。
2. **异常继承关系（实测）**：
   `InvalidLanguageTagError(Notation3InputError, ValueError)`、`UnterminatedStringError(Notation3InputError, AssertionError)`、`MissingDatatypeError(Notation3InputError, IndexError, LookupError)`、`IntegerDigitLimitError(Notation3InputError, ValueError)`、`BadSyntax(SyntaxError)`、`Notation3InputError(Exception)`。
   → `rdf_snapshot.py:42` 的 `except (BadSyntax, Notation3InputError)` **覆盖全部已类型化抛点**，包括 `MissingDatatypeError`（虽继承 `IndexError`，但同时继承 `Notation3InputError`，先被类型化分支捕获）。
3. **引擎侧映射**：`rdf_snapshot.py:13-14` 新增 `TermInputError(ValueError)`；`term()` 抛 `TermInputError` → `domain_changesets.py:455-456/462-463` → `fail("INVALID_REQUEST", field="params")` → `ServiceFault` → `coordinator.classify()`（`coordinator.py:92-93`）→ 固定错误码 `INVALID_REQUEST`，**不回传原文案/原值**。
4. **身份政策**：`storage.py:484-494` `_fact()` 强制 `term(fact["object"]).n3() == fact["object"]` 且 `fact["id"] == digest([S,P,O])`（内容派生）；`edits` 保留初始 ID（ADR-0002 第 27 行）。

### 5.2 「不泛捕 ValueError / 不按文案分类 / 不静默 normalize / 不放宽 cap」的逐条核对

| 约束 | 证据 | 判定 |
| --- | --- | --- |
| 不泛捕 ValueError | `rdf_snapshot.py:42-43` 是**新增的类型化分支**；其后 `:44-45` 的 `except Exception → ValueError` 是**基线既有上下文行**（`git diff base..head` 中未出现在新增侧），未被本候选扩写为 `except ValueError` | 满足（新增的是专用类型分支，非泛捕） |
| 不按异常文案分类 | 分类依据是**异常类型**（`BadSyntax`/`Notation3InputError` 子类），非 `str(error)` | 满足 |
| 不静默 normalize | `de-CH-1901` → 明确拒绝，不改写后接受（§3.2 第 3 点） | 满足 |
| 不放宽 cap | `sys.get_int_max_str_digits()` 动态取当前上限，patch 未设常量新上限；实测 4300 位通过解析、4301 位被 `IntegerDigitLimitError` 拒绝 | 满足 |

### 5.3 事实原 ID、多值、ownership 可见定位（静态核对）

- **原 ID**：ADR-0002 第 27 行 + `storage.py:494`（`fact["id"] != digest([S,P,O])` → 拒绝）双保险；`edits` 不重算 ID，保留初始摘要。
- **多值**：`storage.py` 的 `ManualOwnershipConflict` / `SingleDeclarationConflict`（含 `witness`）、`_validate_single_slots(project, declarations)`、`_check_slot(..., manual_incoming=)` 三分类 reason。
- **ownership 可见定位**：`mainline.py` 的 `_OwnershipProof.check()` 绑定 `store` 身份、`store._db` 连接身份、`store._format3_lease`、`project`、`owner.selected`、`owner.generation`、`reply.method`、`reply.project`，并调用 `owner.authorize({"projectId": project})`；`origin` 输出 `ownerId/hostClientId/engineSessionId`。`close()` 置 `self.host = self.session = None`、`closed=True`、`_clean_close=False`（`mainline.py:617-623`），`allows_owner()` 额外要求 `not self.closed and not self.actor.closed and not self.hold`。
- **确定性/Agent 解耦**：本次候选内 Agent 未接入写入路径；写入唯一入口为 `Store.commit`。

### 5.4 渲染端隔离 / CSP / IPC（静态核对）

- `apps/desktop/src/csp.ts` 为唯一 CSP 源，`contentSecurityPolicy(development?)` 提供生产 meta 与开发 header 两个变体；`unsafe-inline` 仅出现在**开发变体**的 `style-src`（`csp.ts:20`，注释明确「Vite CSS HMR; production uses local CSS」），**生产脚本无 `unsafe-inline`/`unsafe-eval`**（全仓 `apps/desktop/src` grep 仅此一处）。
- `preload/index.ts` 仅暴露按业务命名的方法（`getEngineHealth`/`getActiveProject`/`getJob`/`listJobs`/`cancelJob`/`subscribeJob`/`getResult`/`getResultPage`/`getOperation` 等），无通用 `invoke(method, params)` 通道。
- 新增 `project:ownership-detail` 走既有通用 `trusted(event)` → `isTrustedDocument` 全 URL 精确比对，未新增绕过路径。

### 5.5 共享依赖闭包

- `packages/engine/pyproject.toml:7,20` 与 `uv.lock:73` 一致 pin `rdflib==7.6.0+ontolearn.fr201.3`（path wheel）；`uv.lock` 使用 `path` 依赖形式，**不记录 sha256**。
- 磁盘 wheel 哈希（实测 `shasum -a 256`）：
  - `rdflib-7.6.0+ontolearn.fr201.1-py3-none-any.whl` = `13be2a17b60fbbadfefbb5b00d41fe12c9dd97d2844c41c22d1d00fc86d99137`（2378177B）
  - `rdflib-7.6.0+ontolearn.fr201.2-py3-none-any.whl` = `f30e6279edcc31dbcb0c84eb1ee79e43776e7a30cd8813bcde7cfa85848bc0ef`（2378736B）
  - `rdflib-7.6.0+ontolearn.fr201.3-py3-none-any.whl` = `99fab7bdd9148267ac0fcbd49363fc10d9a1edd47a4744726c14a7d14fc51edf`（2379774B）
  - `upstream/rdflib-7.6.0-py3-none-any.whl` = `30c0a3ebf4c0e09215f066be7246794b6492e054e782d7ac2a34c9f70a15e0dd`（615KB）
- `PROVENANCE.json` `/artifact/sha256 = 99fab7bd…`（与磁盘 fr201.3 一致），`/upstream/wheel/sha256 = 30c0a3eb…`（与 upstream 一致）；`/limitations` 明示 `actualIntegerLimit: 4300`、`noParserWideExhaustiveness: true`、`applicationSuiteNotRun: true`。
- 三个 fr20x wheel 与 upstream wheel 均为 **ZIP_STORED 未压缩**（`unzip -l` 的压缩方法列恒为 `01-01-1980`），故 fr201.x ≈ 2.38MB 而上游 ≈ 615KB。
- `fr201.1` / `fr201.2` **在仓库内无任何清单/锁文件引用**（仅 `PROVENANCE.json` 历史提及与历史评审报告提及），但两文件均被 git 跟踪。

---

## 6. 本方独立实测（只读、进程内；不启动产品、不改源）

### 6.1 渲染层与引擎层的 ID 派生一致性

- 渲染层 `JSON.stringify([S,P,O])` + TextEncoder + SHA-256 与 Python `canonical()/digest()` 逐例交叉比对：**14 例**（含 CJK、emoji、RTL、tab/nl、DEL、控制字符、U+2028/U+2029、裸反斜杠）→ **0 mismatch**。
- `packages/contracts/src/v2.ts` 的手写 `ownershipSha256` 用仓库自带 tsc 编译后与 Node `crypto` 对 **10 组**向量比对 → **0 mismatch**。

### 6.2 `term()` 分类矩阵（实测输出摘录）

| 输入 | 结果 |
| --- | --- |
| `"abc` / `"""abc` | `TermInputError`（cause=`UnterminatedStringError`） |
| `"a"^^` / `""^^` | `TermInputError`（cause=`MissingDatatypeError`） |
| `"a"b` / `urn:x` / `"a"@` / `"a"@@en` / `"a"@en--001` | `TermInputError`（cause=`BadSyntax`） |
| `"a"^^<not an iri>` | `TermInputError`（cause=`RelativeIRIBaseError`） |
| `"设备"@1` / `"设备"@zh1` / `"a"@a1` | `TermInputError`（cause=`InvalidLanguageTagError`） |
| `"9"*4301` | `TermInputError`（cause=`IntegerDigitLimitError`） |
| `"设备"@de-CH-1901` | 解析成功，n3=`de-ch-1901`，canonical=False → 拒绝 |
| `"设备"@de-ch-1901` / `"设备"@en-001` | canonical=True → 可提交 |
| `_:b` / `[]` | `TermInputError`（非 URIRef/Literal 或非恰好一个词项） |

### 6.3 对抗词法扫掠（两轮共 **92 例**，含未闭合串/缺 datatype/非法首子段/超长整数/嵌套集合/bnode/前缀声明/非法转义/CJK/emoji/RTL/控制字符）

**结果：落入 `term()` 基线 broad 分支（`except Exception`）的例数 = 0**；其余全部为受控 `TermInputError` 或正常接受。即：当前词法面**未发现**可把未分类异常泄漏到 `INTERNAL_ERROR`/HOLD 的实际反例。

### 6.4 整数边界实测

| 输入 | `term()` | canonical | 应用级结果 |
| --- | --- | --- | --- |
| `"9"*4299` | 成功（datatype `xsd:integer`） | **False**（n3 追加 `^^<…#integer>`） | `INVALID_REQUEST`（canonical 路径） |
| `"9"*4300` | 成功 | **False** | `INVALID_REQUEST`（canonical 路径） |
| `"9"*4301` | `TermInputError` | — | `INVALID_REQUEST`（类型化路径） |

→ **裸整数字面量在任何长度下都不是合法对象值**（canonical 规则使然）；4300/4301 的差别只体现在**内部机制**（canonical 路径 vs 类型化路径），**用户可见错误码完全相同**。仓库内**没有任何应用层断言**固定这一点（`grep -rn "4299\|4300" packages apps tests` 无命中；唯一断言是 `test_mainline_language_input_rejection.py:36` 的 `"9"*4301`）。见 §9 缺陷 T02-R04-03。

### 6.5 独立解析器 EOF 残余（实测复现）

```
Graph().parse(data='<urn:s> <urn:p> "abc"', format="turtle", publicID="urn:ontolearn:s1:")
→ builtins.IndexError: string index out of range
   at .venv/lib/python3.12/site-packages/rdflib/plugins/parsers/notation3.py:1609 in nodeOrLiteral  (if argstr[j] == "@")
   at …notation3.py:931  in path        (while argstr[j] in {"!", "^"})
```

`"abc"@en`、`"abc"^^<http://www.w3.org/2001/XMLSchema#string>` 同因。**未类型化 `IndexError`**，不属于 `Notation3InputError` 家族，故不会命中 `rdf_snapshot.py:42` 的类型化分支。

**可达性边界（重要）**：该残余是**文档级**解析路径；`rdf_snapshot.term()` 总是自行补 `" ."`（`rdf_snapshot.py:38`），因此 manual fact 值与 definitions triple 值（`storage.py:1128` 同样走 `term(obj)` 单值路径）**均不可达 EOF 位置**。当前产品面**不可达**；但 `PROVENANCE.json` 自述 `noParserWideExhaustiveness: true`、`applicationSuiteNotRun: true`，且未来任何直接调用 rdflib 文档级解析的新路径都会得到未分类 `IndexError` → `coordinator.classify()`（`:108`）→ `INTERNAL_ERROR` → `observe_error` 置会话 HOLD。见 §9 缺陷 T02-R04-04。

---

## 7. 收据的独立重算（不把摘要断言当事实）

**执行来源声明（必须区分，不得混同）**：本节的**归档件枚举与字节级重算**（ASAR readback 5 文件逐字节比对、App/engine 成员数与 regular 文件计数与总字节、PYZ 模块数、各 report.json 的 SHA256 与体积、raw wire 事务条数重算、56309 Unicode scalars 重算）由**本方委派的只读核验子代理**执行，其结果经本方抽样复核后采纳——**这是委派核验，不是本方亲手执行**。本方**本人直接执行**的是：§6 的全部 Python/Node 交叉验证与词法/身份探针、§1–§5 的全部源码阅读与 git 取证、以及本节表格中「本方直接复算」列标注为直接执行的项。下表「结论」列只写**重算一致 / 路径存在 / 仅由摘要断言**三种口径，不写「验证通过」。

**重要**：以下是对**已归档 raw** 的重算，**不是对产品行为的复跑**。已归档 raw 位于 `outputs/` 下。

| 收据 | 重算内容 | 执行来源 | 结论 |
| --- | --- | --- | --- |
| **A. package094**（`outputs/20261025_t11_package094_actual_001/`） | `source=1344`（与本方直接执行的 `git ls-files` 一致）、`build=5`（ASAR readback 5 文件逐字节/哈希一致）；`App.asar` 19094247B / SHA256 `3f800170…`；engine 6254048B / SHA256 `6bd514ba…`；App 912 成员 / 547 regular / 383168283B；engine 268 成员 / 227 regular / 37782451B；fresh PYZ 745 modules | 委派只读核验（`source=1344` 一项本方直接复核） | **重算一致** |
| | 实际 App 存在于 `outputs/20261025_t11_package094_actual_001/frozen-artifacts/release/mac-arm64/OntoLearn Studio.app` | 委派只读核验 | 路径存在 |
| **B. 原六 GUI**（`outputs/20261025_t02_rows_text_integration_029/runtime-full6-001/report.json`） | 3996489B / SHA256 `ce072a8d…`；6 passed / 0 skip / 0 retry；每例事务 7/7/7/7/22/7 = **57**；`negative-verification.json` **43** 条，分布 {INVALID_REQUEST: 42, OWNERSHIP_CONFLICT: 1}；43/43 `beforeAfterFullReadEqual=true` | 委派只读核验 | **重算一致** |
| **C. spec** | `tests/e2e/t02-fr200-fr201.spec.ts` = 73400B / SHA256 `1d8b8e2c…` | 委派只读核验 | **精确匹配** |
| **E. named** | 24/24 PASS、retry 0；98 事务由 raw wire 重算 = 15×4 + 4×4 + 4×2 + 14；43 拒绝 = 38 INVALID_REQUEST + 5 OWNERSHIP_CONFLICT；ownership 5 族齐备（reservedIdentity / sameStatement / singleSlot / singleDeclaration / large），large = 80545B / 3 段 / hash `c2c8d126…` | 委派只读核验 | **重算一致** |
| **F. text** | 2 PASS（ASCII + Unicode）、0 skip/retry；56309 Unicode scalars 重算一致；页字节 ASCII 30720/23990/1499/94/6、Unicode 30720/23995/1499/93/7 | 委派只读核验 | **重算一致**（56309 未从 SQLite blob 独立重导，仅重算已归档样本） |

**唯一消歧警示**：另存在 `outputs/20261025_t02_postwrite_successor_integration_028/runtime-full6-001/`，其 `report.json` 哈希不同（`69f842c2…`）。按目录名 glob 会取到错误样本——本方全部按**显式路径**取证。

**本方未独立复跑**：`npm run check`（TS 1892 PASS / Py 3769 collected / 3719 PASS / 50 skip / Ruff 369）、实际 GUI、包内原验收、named/text 的独立 profile 重生。这些仍是第 40 行要求的门禁项，**本报告不代替**。

---

## 8. 用户原清单逐项适用性与检查依据（160 项）

> 附件第 42–211 行，第 51–197 行（147 项）+ 第 199–211 行（13 项）= **160 项**。逐项判定如下。**不适用项直接跳过，不为清单新增 SaaS / 付费 / 账户 / 云服务。**

### 8.1 身份、账号与多租户（附件行 51–64）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 51 | schema 由人设计而非 AI 逐表即兴 | 部分适用 | 本体/契约 schema 由 `packages/contracts/v2/schema.json` + ADR-0002 显式定义，非即兴；`changeSetFact` 无内容派生约束（§9 T02-R04-06） |
| 52 | 邮箱带加号仍可登录 | 不适用 | 产品无账号/登录/邮箱体系 |
| 53 | 一次性且会过期的密码重置链接 | 不适用 | 同上 |
| 54 | MFA 与丢失设备恢复路径 | 不适用 | 同上 |
| 55 | 会话超时 + 一键吊销某用户全部会话 | 部分适用 | 有 host/engine 会话生命周期（`mainline.py` `close()`/`_clean_close`/`allows_owner`）与 `Job` 队列；**无用户维度**，故「按用户吊销全部会话」不适用 |
| 56 | 企业客户要求的 SSO | 不适用 | 无外部身份源；AGENTS.md「不开 HTTP 端口、不引入云服务」 |
| 57 | SAML | 不适用 | 同上 |
| 58 | SCIM 离职即刻回收访问 | 不适用 | 同上 |
| 59 | 比「管理员/所有人」更细的角色权限 | 部分适用 | 无角色体系；但有 **ownership 语义**（单一 owner + `origin` 归属 + 冲突证据）→ 已实现（§5.3） |
| 60 | 改 URL 里的一个数字就读到他人数据 | 适用 | 边界数据不可被越权读取：ownership proof 绑定 store/连接/lease/project/generation（`mainline.py:492-507`）；IPC `trusted(event)` 全 URL 精确比对；`projectId` 不匹配 → `IDENTITY_CONFLICT` |
| 61 | 租户隔离 | 不适用 | 本地单机单用户，无租户概念 |
| 62 | 管理员「以此用户登录」+ 审计 | 不适用 | 无多用户/支持通道 |
| 63 | 登录限流 | 不适用 | 无登录 |
| 64 | 锁定不误伤 CFO | 不适用 | 同上 |

### 8.2 数据库、迁移、备份、容量（附件行 65–72、79–85）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 65 | 数据库迁移可前进可回滚 | 部分适用 | SQLite 为唯一可变源真相；本候选**未新增 schema 迁移**（58 叶 diff 无 DDL 迁移面）；`store.actual_format != 3 → INVALID_STATE`（`domain_changesets.py:429-430`）；迁移策略本身属 M0 未完成项（`m0-checklist.md:20`） |
| 66 | 迁移不在周二下午锁主表 | 部分适用 | 桌面单机无并发高峰；但容量隔离历史（O026/O027）与 `RESOURCE_LIMIT.page` 仍为公开边界，见 §11 |
| 67 | 索引（5M 行超时） | 适用 | 已实测暴露：`547 rows / 1180333 scan / 911122 decoded / core 69783694 > 67108864`（旧 0e7 T01 只读测量），本候选未改变该上限口径；`ReadLimits`/`_budget()` 为受限读取机制 |
| 68 | 连接池 | 不适用 | 嵌入式 SQLite，无网络连接池 |
| 69 | 每晚备份 | 部分适用 | 本地产品无自动备份；存在归档导出（CSV/rows 页）证据 |
| 70 | 经测试的备份恢复 | 无法确认 | 仓库内无备份/恢复实现与测试；本轮未新增运行，无法确认 |
| 71 | 时间点恢复 | 不适用 | 同上 |
| 72 | 软删除 | 部分适用 | 有墓碑/retirement 机制（`storage.py:64` 注释「managed deletion tombstones are provenance, not facts」；`retirement_control`）；「删错变工单」的产品化入口本轮未核验 |
| 79 | 数据模型经得起第二个客户的小改动 | 部分适用 | 本体定义 / 断言事实 / 当前推导 / 场景副本 / 历史运行分层 + ADR-0002 身份政策；**无第二客户场景可验证**，故「经得起」无法确认 |
| 80 | 幂等键（重试不重复扣款） | 适用（改写为本地语义） | 无支付；等价机制为 `operationId` + `operation_claims`（`domain_changesets.py:288-291`）+ `previewHash` + `confirmationRef` |
| 81 | 重复点击四次的去重 | 适用 | 内容派生 ID（`storage.py:494`）+ `has_operation_claim`/`operation_claims` 唯一占用；实测 57/98 事务与 43 次拒绝均无重复写入 |
| 82 | 第 400 页仍正常 | 适用 | `changeset.diff.page` + `project.ownership.detail` 游标分页；实测 ownership large = 80545B / 3 段；客户端上限 512 次请求 / 16384 节点（`contracts/src/index.ts:437,442,451,517`；`mainline-ownership.ts:21,29`） |
| 83 | 导出为表格 | 部分适用 | 有 rows/CSV 导出证据（243 行 SELECT 原值 / 4 CSV）；**是否产品化导出入口本轮未核验** |
| 84 | 导入兼容 2009 年的 CSV | 部分适用 | 同上；`m0-checklist.md` 明确「映射计划…不能称为 CSV 映射能力已完成」 |
| 85 | 保留期与按合同删除 | 部分适用 | 历史/已提交轮次不可改写（AGENTS.md §3）；本地无合同保留期概念 |
| 77 | 金额用整数存储 | 不适用 | 无金额/货币字段 |
| 78 | 多国货币/舍入/税 | 不适用 | 同上 |

### 8.3 输入、国际化、时区（附件行 73–76）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 73 | 服务端校验而非只在前端 | 适用 | 预览守卫 `domain_changesets.py:451-477` + `storage._fact` 内容派生与 canonical 双端强制；`edits` 走 `term()`（`:459-465`） |
| 74 | 时区正确（9am 提醒不在 4am 触发） | 不适用 | 产品无定时/提醒/日程 |
| 75 | 名字里有撇号 | 部分适用 | 无姓名字段；等价的「用户输入含引号/撇号的字面量」已覆盖：未闭合串 → `UnterminatedStringError`；引号内任意字符（含撇号）在 canonical 字面量中可提交 |
| 76 | 每个字段都能处理 emoji、重音、RTL | 适用 | 引擎字面量层已实测（§6.1 14 例含 CJK/emoji/RTL/tab/nl/DEL/控制字符/U+2028/U+2029/裸反斜杠 → **0 mismatch**）；文本页实测 56309 Unicode scalars 一致、页字节 ASCII 30720/23990/1499/94/6 与 Unicode 30720/23995/1499/93/7 |

### 8.4 密钥、依赖、OWASP（附件行 86–104）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 86 | 密钥不进代码/仓库/AI 聊天历史 | 适用 | 仓库内无凭据；`.gitignore:26` 含 `.mimosa/`（`packages/engine/vendor/rdflib/.mimosa` 已确认被忽略）；AGENTS.md「不提交凭据、业务数据、`.sqlite`/`.db`、`.env`、`.mimosa/`」。**本轮未做全仓密钥扫描器级扫描**，按 grep 抽查结论 |
| 87 | 轮换上月 AI 粘进配置文件的每个 key | 不适用 | 无生产密钥、无配置内密钥 |
| 88 | 确认每个安装的包都存在且正是预期的那个 | 适用 | **发现缺口**：见 §9 T02-R04-02（4 个 tracked wheel、锁文件无 hash、fr201.1/.2 无引用） |
| 89 | 依赖扫描（AI 拉进来的库无人审） | 部分适用 | 精确版本 pin + 双锁文件（`uv.lock`/`package-lock`）+ `licenses/NOTICE` + `PROVENANCE.json` 逐文件哈希；**无 SCA/漏洞扫描工具**，且 patch 属自维护 fork（`noParserWideExhaustiveness: true`） |
| 90 | 用户能输入处一律做输入清洗 | 适用 | 词法/IRI 受控拒绝（§6.2）；`iri()` 拒绝空白以及 `<>{}`、竖线、`^`、反引号、反斜杠六类字符；`TermInputError` 映射固定错误码且**不回传原值** |
| 91 | SQL 注入 / XSS / CSRF / OWASP | 适用（本地进程面） | 全部 SQL 参数化（未见字符串拼接 SQL；`material_profile()` 的表名/列名用 `"` + `""` 转义）；无网络端口故无 CSRF 面；renderer 无 Node、无 `dangerouslySetInnerHTML` 路径；CSP 单一源且生产无 `unsafe-inline`/`unsafe-eval` |
| 92 | 上传文件被扫描/限大小/不可执行 | 不适用 | 本轮无文件上传能力 |
| 93 | CORS 不是「全放开」 | 不适用 | 无 HTTP 服务 |
| 94 | 每个响应都有安全头 | 部分适用 | 桌面应用无 HTTP 响应；等价面为 CSP + `will-navigate`/来源校验 + IPC sender/mainFrame/可信文档校验 |
| 95 | 静态与传输加密 | 不适用 | 无传输；本地 SQLite 未加密（本地单机产品，AGENTS.md 未要求） |
| 96 | 最小权限，含持生产凭据的 AI Agent | 适用 | 凭据只在主进程；Python 引擎不持密钥、不调模型；Agent 只产草稿并调白名单工具、不得自动确认自己的修改；模型外发在 S3 前不得接入（AGENTS.md §3） |
| 97 | 日志记录谁做了什么且不记密码/token/卡号 | 适用 | `Job`/`marker`/receipt 记录变更归属与 revision；跨边界只传固定错误码与受限参数（`classify()` 对裸异常 → `INTERNAL_ERROR` 空 params，round-03/zcode 第 80 行实测口径，本方已核对 `coordinator.py:88-108`） |
| 98 | 企业安全团队自测前的渗透测试 | 不适用 | 本轮范围外；且属独立 HOLD（§11） |
| 99 | 安全问卷逐条有证据 | 不适用 | 无对外企业销售流程 |
| 100 | 漏洞披露流程 | 不适用 | 同上 |
| 101 | 生产访问笔记本被盗的预案 | 不适用 | 无生产访问凭据 |
| 102 | SOC 2 | 不适用 | 无运营实体 |
| 103 | HIPAA | 不适用 | 无患者数据 |
| 104 | 与每个接触数据的供应商签 BAA（含模型商） | 不适用 | 无外部供应商/模型调用 |

### 8.5 审计、合规、租户运维（附件行 105–118）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 105 | 审计轨迹显示**谁看过**记录（不只是谁改过） | 部分适用 | 变更侧有 `operation_claims`/marker/receipt/ownership origin；**读取侧无审计留痕**（`project.read` 无读审计事件）→ 记录为未实现而非缺陷（本轮范围不含读审计） |
| 106 | PCI 范围，卡号不入库 | 不适用 | 无支付/卡数据 |
| 107 | GDPR 删除请求覆盖每张表/备份/日志 | 部分适用 | 本地数据有墓碑/retirement；**无「删除请求」工作流**，也无远端备份/日志可删 |
| 108 | 数据驻留（合同要求 EU only） | 不适用 | 本地单机，无数据驻留问题 |
| 109 | 季度访问复核签字 | 不适用 | 无多用户 |
| 110 | dev/staging/prod 环境一致 | 部分适用 | 单一本地发行，无环境分层；因此「一致」无从比较 |
| 111 | 基础设施即代码 | 部分适用 | 打包脚本 + CI 配置在仓库内（可复算）；**本轮未核验 CI 是否等价于「装得上」** |
| 112 | 部署流水线先跑测试 | 适用 | CI 用 `npm ci` + `uv sync --frozen`（AGENTS.md §7）；**本轮未运行 CI，也未本地复跑完整 check** → 状态来源为收据 + 仓库配置 |
| 113 | 一键回滚 | 不适用 | 无生产部署 |
| 114 | 零停机部署 | 不适用 | 同上 |
| 115 | 功能开关 | 不适用 | 同上 |
| 116 | 自动扩缩容 | 不适用 | 同上 |
| 117 | CDN | 不适用 | 同上 |
| 118 | DNS/SSL 证书与续期 | 不适用 | 同上 |

### 8.6 运行时可靠性、可观测性（附件行 119–139）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 119 | 后台作业队列 | 适用 | `Job` 队列 + `maxQueuedJobs` → `QUEUE_FULL`（`coordinator.py:518-521`）；`execute_changeset` 在唯一写者中执行 |
| 120 | 带退避的重试 | 部分适用 | `ENGINE_EXITED` 标记 `retryable`（收据口径）；引擎内**无通用指数退避队列** |
| 121 | 死信队列 | 不适用 | 无异步失败作业队列（失败 Job 落库可查，非死信队列） |
| 122 | 加第二台服务器时不重复跑的 cron | 不适用 | 无 cron、无服务器 |
| 123 | 缓存与数据变更时清缓存 | 适用 | `result_state` / `staleReason` / `invalidation-v2.json`；`staleReason` 只来自 `invalidation-v2.json`，仅改模型配置不使领域结果过期（AGENTS.md §3） |
| 124 | SPF/DKIM/DMARC | 不适用 | 无邮件 |
| 125 | 事务邮件退信与投诉处理 | 不适用 | 同上 |
| 126 | 存储规则（清理旧临时文件） | 部分适用 | 工作区 `outputs/` 与运行 profile 目录；**无自动保留期清理策略**（本轮未核验） |
| 127 | 成本告警 | 不适用 | 无云账单 |
| 128 | 写下来并每年演练的灾难恢复计划 | 不适用 | 无生产环境 |
| 129 | 第二可用区 | 不适用 | 同上 |
| 130 | 凌晨 3 点能搜的结构化日志 | 部分适用 | Job/事件/`evidence` JSON 化；无集中日志系统 |
| 131 | 错误归并（同一 bug 不发 4000 封邮件） | 部分适用 | 固定错误码天然归并（`INVALID_REQUEST`/`INTERNAL_ERROR`/`STORAGE_FAILURE` 等）；无邮件通道 |
| 132 | 外部网络的存活探测 | 不适用 | 无对外服务 |
| 133 | 会叫醒人的告警 | 不适用 | 同上 |
| 134 | 延迟/错误率/吞吐看板 | 不适用 | 同上 |
| 135 | 跨服务追踪一次慢请求 | 不适用 | 单进程（主进程 + stdio 引擎） |
| 136 | 值班轮转 | 不适用 | 同上 |
| 137 | Runbook | 部分适用 | `AGENTS.md` + `docs/iterations/*` + `docs/reviews/*` 构成事实上的操作说明；**正式 runbook 文档未确认** |
| 138 | 会改变东西的复盘 | 部分适用 | `docs/reviews/Ixx/` 与 R01–R03 处置链有完整复盘链路；非产品代码 |
| 139 | 状态页 | 不适用 | 无对外服务 |

### 8.7 测试与质量（附件行 140–147）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 140 | 由懂逻辑的人写的单测 | 适用 | `packages/engine/tests/`（pytest）+ `tests/unit`（vitest）；本候选新增 `test_mainline_language_input_rejection.py`（含 R03_REFUSALS / CANONICAL_TAGS / 数字子段语法与 canonical 分离用例）；断言覆盖具体预期集合而非仅计数 |
| 141 | 每个第三方 API 的集成测试 | 适用（依赖面唯一） | 唯一第三方运行时依赖为 vendored rdflib；其回归由供应方仓库外证据 + `PROVENANCE.json` 记录，**供应方自述 `applicationSuiteNotRun: true`** |
| 142 | 注册/结账等赚钱流程的端到端测试 | 不适用（无注册/结账）；部分适用（等价流程） | `tests/e2e/t02-fr200-fr201.spec.ts`（73400B）覆盖 FR-200/201 表单 CRUD 与 ownership 定位 |
| 143 | 上线前的负载测试 | 部分适用 | 容量/分页实测：56309 Unicode scalars、80545B ownership 3 段、243 行 SELECT/4 CSV；但**「上线」容量口径属 Q5 未决**（`m0-checklist.md:16`） |
| 144 | 看起来像生产的测试数据 | 适用 | 真实已提交原 ID 编辑、真实字面量、真实 revision 链（rev13/rev20/rev22/rev24）；negative-verification 43/43 `beforeAfterFullReadEqual=true` |
| 145 | 回归测试（修 41 不带回 12） | 适用 | 本候选保留 R01/R02/R03 全部回归面；`storage.py:601` 明确保持旧 marker 的 canonical plan/hash 不变 |
| 146 | 在客户运维的五年前笔记本上测试 | 无法确认 | 无参考设备基线；属 Q2 未决（`m0-checklist.md:14`） |
| 147 | 无障碍合规 | 部分适用 | **本轮未核验**键盘导航/屏幕阅读器/对比度 → 记为无法确认（§10） |

### 8.8 商业与计费（附件行 148–163）

行 148（订阅/升降级/按比例）、149（失败付款重试与催缴）、150（发票带 PO 号）、151（销售税与 VAT）、152（退款/贷项/部分退款）、153（用量计费精确到分）、154（年度合同自定义条款）、155（营收报表可对账）、156（Webhook 验签）、157（Webhook 重试与失败投递日志）、159（客户自助创建/吊销 API key）、161（第三方 API 静默变更的应对）、162（OAuth 令牌刷新）、163（客户沙箱）—— **均不适用**：产品为本地优先桌面应用，无订阅、付款、发票、Webhook、外部 API 客户或 OAuth 集成（AGENTS.md §3「不自动启用模型、遥测或云服务；不开 HTTP 端口」）。

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 158 | 版本化 API（改接口不破客户集成） | 适用 | `packages/contracts` v1/v2 双 schema + `v2Registry`/`validateV2`/`validateBusiness3` + IPC 契约 + `business3` profile；`packages/contracts/src/v2.ts` 运行时校验（zod `.strict()` 风格，见 AGENTS.md §7） |
| 160 | 保护真实集成的 API 限流 | 部分适用 | 引擎侧 `limits`/`_wire_room`/`MAX_REPLIES=16`/`ReadLimits`/`SEGMENT_BYTES=32768`/`MAX_DOCUMENT=16MiB`；无外部 API |

### 8.9 AI 相关（附件行 164–171）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 164 | 每个流向模型的字段都防提示注入 | 不适用（当前无模型接入） | 模型外发在 S3 前不得接入，唯一网关在主进程（AGENTS.md §3）；本候选**未接入模型**，无「流向模型的字段」 |
| 165 | 客户/患者数据不进入出网提示 | 适用（架构不变量） | 本地优先、不开端口、不启遥测；Python 引擎不调模型；本候选无数据出网路径 |
| 166 | 每客户模型花费上限 | 不适用 | 无模型调用 |
| 167 | Evals（模型更新导致回答变差） | 不适用 | 同上 |
| 168 | 模型服务商宕机的降级 | 不适用 | 同上 |
| 169 | 模型被弃用的迁移预案 | 不适用 | 同上 |
| 170 | 提示与输出日志 | 不适用 | 同上 |
| 171 | AI 不可撤销动作前的人工确认 | 适用 | Agent 只产出草稿并调用白名单工具，**不得自动确认自己的修改**（AGENTS.md §3）；确定性写入唯一入口 `Store.commit`，需 preview → 确认 → commit 链（`changeset.preview` → `changeset.confirm` → `job.create(changeset.commit)`），commit 绑定已存证 preview envelope（`domain_changesets.py:919-949`，`envelope != context["plan"] → INVALID_STATE`） |

### 8.10 体验、可访问性、工程卫生（附件行 172–197）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 172 | 酒店 WiFi 下页面能加载 | 不适用 | 本地打包应用，无远程资源加载 |
| 173 | 每个界面都有空/加载/错误态 | 适用 | `OntologyMainlinePage.tsx` 具备状态分支；**本轮未逐屏核验** → 部分无法确认（§10） |
| 174 | 错误信息可行动，而非「出错了」 | 适用 | 固定错误码 + 受限参数；`INVALID_REQUEST`/`OWNERSHIP_CONFLICT`/`REVISION_CONFLICT`/`IDENTITY_CONFLICT`/`PERMISSION_DENIED`/`RESOURCE_LIMIT.*` 等可区分 |
| 175 | 一个字段校验失败时表单保留已输入内容 | 部分适用 | `mainline-session.ts` `prepare()` 与 `factLifetime` 围栏保留输入；**本轮未逐字段核验** → 部分无法确认 |
| 176 | 邮件在所有客户端正常渲染 | 不适用 | 无邮件 |
| 177 | 可关闭的通知 | 不适用 | 无外发通知 |
| 178 | 撤销 | 部分适用 | 引擎有 `impact`/反例与 `targetOperationId` 机制（`domain_changesets.py:275+`）；R03 已记录「Undo 未证」（见 §11） |
| 179 | 键盘导航与屏幕阅读器 | 部分适用 | 未核验（§10） |
| 180 | 翻译与按 locale 格式化日期数字 | 部分适用 | 引擎侧 Unicode 字面量已实测；**界面国际化未核验** |
| 181 | 后退按钮符合预期 | 部分适用 | renderer 路由未核验 |
| 182 | 人能读懂的代码 | 适用 | 模块分层清晰（`project/`、`storage.py`、`job_store.py`、`rdf_snapshot.py`、`coordinator.py`）；命名与注释一致；**注**：引擎无单文件 2000 行以上的巨块（最大实现文件为 `storage.py`，本轮未逐行统计行数 → 以 `wc -l` 复核为需补项） |
| 183 | 每次变更都有代码评审 | 适用 | 本候选经 R01–R03 多轮双审；本轮 R04 为该链的一环 |
| 184 | 分支策略（两人并行不互相覆盖） | 适用 | 独立 worktree + feature 分支 + PR 合回（AGENTS.md §5）；本方在 `feature/weekly-t02-fr200-fr201` 的独立 worktree 内只读作业，未切分支 |
| 185 | 每月升级依赖 | 部分适用 | vendored fork 固定为 `fr201.3`（patch 语义需要手工 rebase），**无月度升级流程**；这是有意的稳定性取舍，非缺陷 |
| 186 | 框架在停更前升级 | 无法确认 | 无框架升级台账；本轮未查 |
| 187 | 删掉 AI 前几次尝试留下的死代码 | 适用 | **发现缺口**：见 §9 T02-R04-02（fr201.1/.2 + upstream wheel 共约 5.4MB 仍在 tracked 源内且无引用） |
| 188 | 拆分被 AI 持续追加的 2000 行文件 | 适用 | 引擎已按 `project/` 子包拆分；`storage.py` 仍是最大文件（行数待 §10 复核） |
| 189 | 写下架构决策及理由 | 适用 | `docs/architecture/0001-desktop-framework.md`、`docs/iterations/I01/ADR-0002-storage.md`、`0003-resident-coordinator-and-jobs.md`、`docs/architecture/m0-review-and-update-plan-2026-10-19.md` |
| 190 | README 让新工程师 1 小时内跑起来 | 部分适用 | README 存在；**「1 小时内」未实测** → 无法确认 |
| 191 | 给继承者写的文档 | 适用 | `docs/iterations/*`、`docs/reviews/*`、本 `AGENTS.md` |
| 192 | 给运维的管理后台 | 不适用 | 无运维后台；产品为单机桌面工具 |
| 193 | 让客服自查的支持工具 | 不适用 | 无客户支持流程 |
| 194 | 客户能读的更新日志 | 不适用 | 内部工具，未发布 |
| 195 | 条款与隐私政策与代码一致 | 不适用 | 无对外服务、无用户数据收集（本地优先） |
| 196 | 账号/域名/仓库用公司名而非搭建者名 | 无法确认 | 仓库内无对外账号/域名；包内标识已在 package094 收据中固定，但「公司名」需人工判断 |
| 197 | 巴士因子大于 1 | 无法确认 | 团队构成不可从仓库判定；仓库文档（ADR、评审链）可降低单点依赖，但不能替代结论 |

### 8.11 「还需要真人」段（附件行 199–211）

| 行 | 清单项 | 适用性 | 检查依据 / 结论位置 |
| --- | --- | --- | --- |
| 199 | 上线前读完 AI 写的每一行（资深工程师） | 适用 | 本轮为该流程的一环：58 叶 diff 全部 name-status/stat 列出，引擎核心与前端/契约关键文件逐文件读；收据做独立重算 |
| 200 | 第二个客户弄坏前先设计好数据模型（后端） | 适用 | ADR-0002 身份政策 + FR-200/201 分层；`storage.py` 内容派生 ID + canonical 强制 |
| 201 | 解释「AI 的一个修复为什么制造了两个新问题」（资深工程师） | 适用 | R01→R02→R03→R04 处置链完整保留，含首败与未关闭项（§4） |
| 202 | 部署、回滚、服务器与云账单（DevOps） | 不适用 | 无生产运维；打包流程在仓库内 |
| 203 | 付款停摆时凌晨 3 点接告警 | 不适用 | 无支付 |
| 204 | 漏洞公开当周修补框架 | 不适用 | 无对外服务框架 |
| 205 | 带审计员讲清患者数据如何流动 | 不适用 | 无患者数据 |
| 206 | 验证「AI 说它测过了」这件事（QA） | 适用 | 本轮对六组收据做独立重算（§7），并明确区分「重算一致」与「仅由摘要断言」 |
| 207 | 在活跃数据库上跑迁移且不丢一行 | 适用 | SQLite 原子提交 / 旧基线拒绝 / 墓碑保留初始 ID；`store.actual_format` 版本闸门；**本轮仅静态 + 既有收据，未实跑迁移** → 部分无法确认 |
| 208 | 对会破坏另外三个特性的功能说不（技术负责人） | 适用 | 冻结门禁 + 只 stage 本任务文件 + 候选冻结后不修改受审路径（AGENTS.md §5）；本轮严格遵守 |
| 209 | 让「在我机器上能跑」变成「对所有客户同时成立」 | 部分适用 | 单机桌面产品，无多客户并发；等价面为容量/分页/Unicode 实测与 RESOURCE_LIMIT 边界 |
| 210 | AI 写不出问题时也能调试代码（资深工程师） | 适用 | 文档化决策 + 固定错误码 + 可复算证据路径 |
| 211 | 一年后还记得它为什么这样建（在场的人） | 适用 | ADR + 迭代文档 + 评审链 + 本报告（§2 记录原决定路径/行） |

**清单统计（本方按表逐行机械复核，非估计）**：不适用 **80** 项、适用（含改写为本地等价语义）**40** 项、部分适用 **35** 项、无法确认 **5** 项；合计 **160**。
复核口径：§8.1–§8.11 共 146 个逐项表行（每行首列为附件行号，机器可数），另 §8.8 将 14 项纯不适用条目（148–157、159、161–163）合并为一段散文并逐项点名，故 146 + 14 = 160。
**本轮未因清单新增任何 SaaS / 付费 / 账户 / 云服务能力。**

---

## 9. 缺陷（按严重度，最多 10 项；不足不凑数）

> 本轮**未发现阻断 FR-200/FR-201 语义的缺陷**。以下 7 项按「最值得修复」排序，均为非阻断项。严重度用「中 / 低」两档（无高、无阻断）。每项含：原源位置、可行动验收、是否阻断。

### T02-R04-01（中）本候选交付了 FR-200/201 能力，但仓库内没有任何状态来源记录它

- **原源位置**：`docs/m0-checklist.md`（全文 35 行，无 T02/FR-200/FR-201 条目；第 35 行只声明「按 FR → 附录 C…维护轻量需求追踪」但未落地）；`docs/reviews/T02/` 下**无 `status.md`**（对照：`docs/reviews/I01..I04`、`docs/reviews/T01` 均有 `status.md`）。
- **依据**：`AGENTS.md` §6「**唯一状态来源**：完成度只在 `docs/m0-checklist.md` 和对应 `status.md` 中维护；其他文档链接过去，不重复……」。
- **风险**：合并后无法从仓库读出「FR-200/201 是否已交付、边界到哪、哪些仍开放」，后续会话可能重复实现、或误判为未实现而重做。这是**流程性**而非功能性问题，但直接影响本仓「唯一状态来源」这一硬约束。
- **可行动验收**：新增 `docs/reviews/T02/status.md`，写明本候选能力范围（FR-200/201 表单 CRUD、事实原 ID、多值、词法受控拒绝、ownership 可见定位）、证据位置（§7 收据目录）、已知边界（§11 HOLD 列表）与「整体合并可用 FR 仍 2/17」这一事实；并在 `docs/m0-checklist.md` 增加一行指向该 status.md。
- **是否阻断**：否。

### T02-R04-02（中）vendored wheel 冗余三个版本，且锁文件不约束其内容哈希

- **原源位置**：`packages/engine/vendor/rdflib/`（tracked：`rdflib-7.6.0+ontolearn.fr201.1-py3-none-any.whl` 2378177B、`…fr201.2…` 2378736B、`…fr201.3…` 2379774B、`upstream/rdflib-7.6.0-py3-none-any.whl` 615KB）；`packages/engine/pyproject.toml:7,20`；`uv.lock:73`（`{ name = "rdflib", path = "packages/engine/vendor/rdflib/rdflib-7.6.0+ontolearn.fr201.3-py3-none-any.whl", specifier = "==7.6.0+ontolearn.fr201.3" }`，**path 依赖不记 sha256**）；`packages/engine/vendor/rdflib/PROVENANCE.json`（`/artifact/sha256 = 99fab7bd…` 仅作记录，无自动校验点）。
- **实测事实**：`fr201.1` / `fr201.2` **在仓库内没有任何清单或锁文件引用**（仅 `PROVENANCE.json` 历史提及 + 历史评审报告提及）；三者均为 ZIP_STORED 未压缩，故 fr20x ≈ 2.38MB 而上游 615KB。
- **风险**：(a) **构建不可复现 / 供应链**——同名 wheel 被替换，锁文件与 CI 都不会拒绝（`uv sync --frozen` 只校验路径与版本标识）；(b) **死代码进入 tracked 源**（约 5.4MB 无引用内容），直接命中清单第 187 项；(c) **误 pin 风险**——`fr201.1`/`.2` 不含 typed 拒绝能力（`fr201.2` 才引入 `UnterminatedStringError`/`MissingDatatypeError`），一旦被 pin 就会退回 R03 阻断态而**无任何机制报警**。
- **可行动验收**：(1) 在 `uv.lock` 记录该 path wheel 的 sha256，或在安装/打包步骤断言磁盘 wheel 哈希等于 `PROVENANCE.json` 的 `/artifact/sha256`；(2) 删除 `fr201.1`/`.2` 与 `upstream/` wheel 文件，其来源与哈希信息保留在 `PROVENANCE.json`（已含 `/upstream/wheel/sha256`）与 `licenses/NOTICE`。
- **是否阻断**：否（当前 pin 指向正确文件；纯供应链与卫生问题）。

### T02-R04-03（中）整数边界在**应用层**不可证，且 4300/4301 两条路径语义不同但错误码相同

- **原源位置**：`packages/engine/src/ontolearn_engine/rdf_snapshot.py:30-58`（`term()`）；`packages/engine/src/ontolearn_engine/project/domain_changesets.py:459-465`（canonical 守卫）；`packages/engine/src/ontolearn_engine/storage.py:491-492`（canonical 强制）；`packages/engine/tests/test_mainline_language_input_rejection.py:36`（唯一整数断言 `"9"*4301`）；`packages/engine/vendor/rdflib/PROVENANCE.json` `/limitations/actualIntegerLimit: 4300`。
- **实测事实**：4299 / 4300 位裸整数**解析成功但 canonical=False**（n3 会补 `^^<http://www.w3.org/2001/XMLSchema#integer>`）→ 应用级 `INVALID_REQUEST`；4301 位 → `TermInputError`（cause=`IntegerDigitLimitError`）→ 应用级**同样** `INVALID_REQUEST`。全仓 `grep -rn "4299\|4300" packages apps tests` **无命中**：应用层没有任何断言固定「裸整数一律不是合法对象值」或 4299/4300/4301 两侧边界。
- **风险**：「不超过 cap 即接受」这一直觉在应用层不成立（裸整数任何长度都被拒）。若未来有人把 canonical 规则放宽或把 cap 从 4300 改成 4301，**仓库内没有任何测试会失败**——4301 仍受类型化抛点保护，4300 则会静默转为可提交。R03 决定第 40 行要求的「超长裸整数分类评估」目前只有供应方仓库外证据（`/limitations` 与外部 harness）。
- **可行动验收**：补应用层三条断言——(a) 4299 位与 4300 位裸整数均被拒（并注明拒绝来自 canonical 路径而非 cap）；(b) 4301 位被类型化拒绝；(c) 一条显式注释/测试固定「裸整数字面量在任何长度都不是 canonical 对象值；只有带 `^^<…#integer>` 的显式 datatype 形式才可提交」。同时可在 `PROVENANCE.json` 记录 4299/4300 的仓库内复算证据位置。
- **是否阻断**：否（当前行为正确且用户可见结果一致；缺的是回归保护）。

### T02-R04-04（中）vendored patch 未覆盖文档级解析的 EOF 位置，仍抛未类型化 `IndexError`

- **原源位置**：`packages/engine/vendor/rdflib/notation3-input-types.patch`（已覆盖 `strconst` 断言、尾部反斜杠、`uri_ref2` 负返回、`unicodeExpand` 码点、`newLiteral` 语言标签、整数位限——**但未覆盖** `rdflib/plugins/parsers/notation3.py:1609 in nodeOrLiteral`（`if argstr[j] == "@"`）与 `:931 in path`（`while argstr[j] in {"!", "^"}`）两处 `argstr[j]` 越界）；`packages/engine/src/ontolearn_engine/rdf_snapshot.py:42-45`（类型化分支在前，broad 分支在后）；`packages/engine/src/ontolearn_engine/coordinator.py:108`（非 ServiceFault/JobFault/sqlite3 → `INTERNAL_ERROR`）+ `observe_error`（→ `unknown=True; hold=True`）。
- **实测复现**：`Graph().parse(data='<urn:s> <urn:p> "abc"', format="turtle")` → `builtins.IndexError: string index out of range`（`"abc"@en`、`"abc"^^<…#string>` 同因）；`IndexError` 不属 `Notation3InputError` 家族，故不会命中类型化分支。
- **可达性**：**当前产品面不可达**——`rdf_snapshot.term()` 总是自行补 `" ."`（`rdf_snapshot.py:38`），manual fact 值与 definitions triple 值（`storage.py:1128` 同样走单值 `term()`）都无法把字面量停在 EOF。`PROVENANCE.json` 自述 `noParserWideExhaustiveness: true` / `applicationSuiteNotRun: true`，与 Z-R02-01「standalone 恰 EOF 8 IndexError 未分类仍 OPEN」一致。
- **风险**：**低可达、高爆炸半径**——任何未来直接调用 rdflib 文档级解析的新路径（批量导入、ontology 文件解析、原始 triples 接线）都会得到未分类 `IndexError`，后果是 `INTERNAL_ERROR` + **整个引擎会话 HOLD**（R03 实测过该后果：`project.read`/`project.get`/`project.create` 全部 `STORAGE_FAILURE`），而非一个受控错误码。
- **可行动验收**：二选一——(a) 在 vendored patch 中把两处 `argstr[j]` 越界改为抛 `Notation3InputError` 子类（新增 `UnexpectedEofError`），并同步 `PROVENANCE.json` 的 patch 哈希与来源记录；(b) 在引擎所有 rdflib 入口处显式把裸 `IndexError` 归一为受控错误码（不得按文案分类）。另建议补一条仓库内回归：断言文档级 EOF 输入产生受控错误码而非裸 `IndexError`。
- **是否阻断**：否（当前不可达；属已披露残余的收口建议）。

### T02-R04-05（低）`term()` 的基线 broad 分支在两条出口上产生**不同的错误语义**（会话 HOLD vs 受控拒绝）

- **原源位置**：`packages/engine/src/ontolearn_engine/rdf_snapshot.py:44-45`（`except Exception as error: raise ValueError("Unsupported S1 RDF object") from error`；**基线既有上下文行，本候选 diff 未改该侧**）；manual fact 出口 `packages/engine/src/ontolearn_engine/project/domain_changesets.py:459-465`（只捕获 `TermInputError` → 未分类 `ValueError` **逃逸** → `coordinator.py:108` → `INTERNAL_ERROR` → `observe_error` 置 HOLD）；definitions 出口 `packages/engine/src/ontolearn_engine/storage.py:1128`（`term(obj).n3() != obj` 抛普通 `ValueError`）→ 被 `domain_changesets.py:474-477` 的 `except (ValueError, KeyError, TypeError)` 捕获 → `INVALID_REQUEST`。
- **实测事实**：两轮共 **92 例**对抗词法输入（未闭合串 / 缺 datatype / 非法首子段 / 超长整数 / 嵌套集合 / bnode / 前缀声明 / 非法转义 / CJK / emoji / RTL / 控制字符）→ **0 例**落入 broad 分支。因此**当前无实际反例**，但两条出口对同一类失败给出不同结果这一**结构性不一致**是实在的。
- **风险**：一旦 broad 分支被触发（例如未来 rdflib 新增未类型化抛点），manual 路径会用**单个不可信输入**把整个引擎会话置 HOLD，而 definitions 路径返回普通受控拒绝——同一个产品面对同类输入给出量级完全不同的故障。
- **可行动验收**：给 broad 分支一个专用异常类型（例如 `UnknownTermParseError`，**不是** `TermInputError`，以保留「已知拒绝」与「未知解析失败」的区分），并在 manual 出口显式映射为受控错误码（仍不得静默 normalize、不得按文案分类）。若产品决定「未知解析失败必须 HOLD」是有意的，请在代码注释与 `PROVENANCE.json` 的 `noParserWideExhaustiveness` 旁写明该意图，使其成为**已声明的**设计而非隐式副作用。
- **是否阻断**：否（无实际反例）。

### T02-R04-06（低）`changeSetFact` 契约只约束 `id` 的形状，内容派生身份的唯一防线在引擎

- **原源位置**：`packages/contracts/v2/schema.json`（`changeSetFact.id` = `{"$ref": "#/$defs/hash"}`，**无「内容派生」约束**）；唯一强制点 `packages/engine/src/ontolearn_engine/storage.py:491-494`（`term(fact["object"]).n3() != fact["object"]` → ValueError；`fact["id"] != digest([S,P,O])` → ValueError）；`edits` 依 ADR-0002 第 27 行保留初始 ID，**不重算**。
- **风险**：跨层契约无法自证身份——任何绕过引擎直写 SQLite 的路径、或未来新增的第二写入路径，都不会被 schema 拦截，只能靠 `storage._fact` 单点守门。当前架构只有 `Store.commit` 一个写入点，故**尚未构成实际缺陷**，属结构性脆弱。
- **可行动验收**：二选一——(a) 在 v2 schema 增加 `id` 与 `subject/predicate/object` 派生关系的约束说明（JSON Schema 无法直接表达 SHA-256 派生，至少加 `x-derived-from` 注解与规则文本）；(b) 增加一条契约测试，断言「引擎对同一 (S,P,O) 计算的 digest 与契约中 `id` 的形态与来源一致」，把「身份由内容派生」这条政策从引擎实现提升为**双端可测**的不变量。
- **是否阻断**：否。

### T02-R04-07（低）`@ontolearn/contracts/v2` 子路径实际暴露三个模块的并集

- **原源位置**：`packages/contracts/package.json`（`"exports": { ".": "./src/index.ts", "./v2": "./src/design-v2.ts" }`）；`packages/contracts/src/design-v2.ts`（`export * from './v2'` + `'./dependencies-v2'` + `'./states-v2'`）。
- **实测事实**：`import { matchesOwnershipDetail } from '@ontolearn/contracts/v2'` **解析正常**（经 `design-v2.ts` 桶文件转出），当前无同名符号冲突。
- **风险**：名为「v2」的边界子路径实际是 v2 + dependencies-v2 + states-v2 的并集，弱化模块边界；一旦三者出现同名导出，`export *` 的解析顺序会决定实际生效者（TS 侧报错但运行时行为敏感）。这是共享契约文件，属 AGENTS.md §5「共享契约…指定唯一维护者」的范围。
- **可行动验收**：把 `exports["./v2"]` 指向 `./src/v2.ts`；确需并集时另设 `./v2/all`（或 `./design-v2`）并在调用方显式选择。
- **是否阻断**：否。

**未列为缺陷但需记录的相邻观察**（不单独占位，因第 13 行**未要求**产品面区分）：当前对「语法非法的语言标签」与「语法合法但非规范拼写」返回**同一个** `INVALID_REQUEST`，用户无法区分二者。若产品希望给出可行动提示（清单第 174 项「错误信息可行动」），需要先有产品决定（属新增语义），本轮不代为决定。

---

## 10. 无法确认（本方未实际检查到，明确不假装检查过）

| # | 事项 | 为何无法确认 | 需要什么才能确认 |
| --- | --- | --- | --- |
| U-1 | 本候选的**完整 check**（TS 1892 PASS / Py 3769 collected / 3719 PASS / 50 skip / Ruff 369 formatted / 1 duplicate-ZIP warning） | 产品冻结 + 只读约束；本方未复跑全量 | 开发会话在同 head 上跑 `npm run check` 并回填 raw |
| U-2 | **实际 GUI**（原六例 6 PASS / 0 skip / 0 retry）与**包内原验收**（原 18 实际 16 PASS + 2 Linux 条件 SKIP） | 本轮未启动 Electron、未开包 | 同 head + 同包的独立 profile 实跑（须与另一方串行，避免争用 GUI/可变运行数据） |
| U-3 | 原 native engine exit、named App 退出码（均为 UNKNOWN）、PID/start 采样缺席 ≠ 自然 0 / OS reap / 全后代关闭 | 需要专门的进程回收观测 | 专门的进程观测实验（本方不做宽泛 kill/删 profile） |
| U-4 | 真实三 query fault 的「读取与施加 fault 非原子」导致的 observer 时序扰动 | 需要受控注入 | 受控注入实验 |
| U-5 | 无障碍（清单 147/179）：键盘导航、屏幕阅读器、对比度 | 本轮未做 UI 审查 | UI 专项审查 |
| U-6 | 界面国际化与 locale 格式化（清单 180）、逐屏空/加载/错误态（173）、表单逐字段保留（175）、renderer 路由与后退（181） | 本轮只做引擎/契约/安全面静态与语义实测 | UI 专项审查 |
| U-7 | 备份与恢复（清单 70）、低配设备基线（146）、README「1 小时内跑起来」（190）、公司名/域名/仓库归属（196）、巴士因子（197）、框架升级台账（186）、正式 runbook（137） | 仓库内无对应实现/台账，团队事实不可由仓库判定 | 产品/团队侧材料 |
| U-8 | `storage.py` 等大文件的实际行数与「2000 行文件」现状（清单 188）、README 的实际可跑性（190） | 本轮未完成 `wc -l` 统计与实跑 | 一次 `wc -l` 与一次干净环境安装 |
| U-9 | 「56309 Unicode scalars 未从 SQLite blob 独立重导」 | 已归档样本内重算一致，但未从原始 blob 重新导出核对 | 对原始 blob 的独立重导（本方仅做样本重算） |
| U-10 | `npm run test:e2e` 在本 worktree 的实际通过情况 | 未运行 | 同 head 实跑（Linux 需 `xvfb-run -a`） |

---

## 11. 独立 HOLD（本方单列，不因当前绿而消解）

| # | HOLD 项 | 状态 | 说明 |
| --- | --- | --- | --- |
| H-1 | 未知 parser / N3 / Store / 坏快照 / 损坏 SQLite 的物理保护 | 保持 | R03 决定第 40 行要求「原未知 parser/N3/Store/坏快照 HOLD 反例保持」；本候选未见相关保护被削弱 |
| H-2 | standalone 恰 EOF 8 IndexError 未分类 | 保持 OPEN | 与 `PROVENANCE.json` 的 `noParserWideExhaustiveness: true` 一致；见 §9 T02-R04-04 |
| H-3 | R03-04 / Z-R03-01（wire 面 `definitions.triples` 坏词法 → `INTERNAL_ERROR` + HOLD） | 保持 OPEN（非阻断） | R03 处置第 24 行明示「不能说已修」；当前 UI 不可达 |
| H-4 | 旧 0e7 / O026 / O027 / 旧 41a / text001 的首败与未证实根因 | 保持 | 初始 TIMEOUT 根因未证实、旧库恢复未做、旧 DB 未打开 |
| H-5 | 内部未签名演示包的签名/公证、whole-APP 法律与 `_distutils` 来源、targetOS/跨平台、参考设备/低端硬件 | 保持 | 与本候选无关但同属发布前置 |
| H-6 | 整体合并可用 FR 仍 **2/17**；未 push / PR / CI / merge | 保持 | 本报告不代替总控的发布判定 |
| H-7 | 仅 `reservedIdentity` 有本轮 GUI 证据 | 保持 | 不得推广到全部 ownership family、Undo 或旧超限库恢复 |

---

## 12. 结论：明确通过 / 不通过与范围

### 12.1 结论

**在本审查范围内不通过（Fail）→ 不成立；本方给出「有条件通过（Conditional Pass）」，且明确：本轮不预设、未被任何一方结论影响。**

更精确地表述为：

1. **FR-200 / FR-201 的实现语义：通过。** 本方在冻结候选上逐文件审查了 58 叶累计 diff，独立复核了 R03 的阻断项（语言标签首子段与超长整数的未分类异常）在当前候选**已实质关闭**（§4、§6.2、§6.3、§6.4），并独立确认 `de-CH-1901` 边界**满足既有需求**（§3）。
2. **本轮未发现任何阻断 FR-200/FR-201 语义的缺陷。** 发现的 7 项（§9）全部为非阻断的中/低项，其中 2 项为流程与供应链卫生问题，3 项为回归保护与错误语义收敛，2 项为契约边界卫生。
3. **本轮未执行运行/打包验收**，因此结论**不覆盖**：完整 check、实际 GUI、包内原验收、native 退出码、进程回收（§10 U-1~U-4、U-10）。这些仍是 R03 决定第 40 行要求的门禁项；本报告以「对已归档 raw 的独立重算」（§7）替代执行，**并已在每处标明「重算一致」与「仅由摘要断言」的区别**。

### 12.2 通过的范围

- 范围：`cb8c9b7a` / tree `b8010eea…` 的 FR-200/FR-201 实现语义、事实原 ID 与内容派生身份、多值与 ownership 冲突语义、词法受控拒绝的分类与错误码、ownership 可见定位、渲染端隔离/CSP/IPC 不变量、vendored rdflib 依赖闭包的**静态与语义层面**。
- 不在范围：发布判定、合并/CI/push、签名与公证、旧 DB 恢复、容量口径（Q5）、参考设备（Q2）、模型外发（S3 前）。

### 12.3 通过的条件（全部满足才成立）

1. §9 的 7 项缺陷在合并前**逐项处置或被总控显式接受**（T02-R04-01 与 T02-R04-02 建议在合并前完成，因二者分别是「唯一状态来源」与「供应链完整性」的基础设施项）。
2. §11 的 7 项 HOLD **保持开放**，不得在合并说明中被描述为已解决或已消解。
3. §10 的 U-1 / U-2（完整 check、实际 GUI、包内原验收）**由开发会话在同 head 取得**，并与本轮 R04 报告一同构成「同版双审 + 同版验收」的完整证据；**本报告不可替代这两项**。
4. 合并/push/PR/CI/发布由总控决定；本报告不代替总控的发布通过。

---

## 13. 实际执行命令与终态

**只读/分析类（本方本人执行，全部无副作用）**

```
pwd
git rev-parse HEAD / HEAD^{tree} / --abbrev-ref HEAD
git ls-remote origin develop
git rev-list --count 583c05c..cb8c9b7a
git diff --name-only 583c05c..cb8c9b7a | wc -l          # 58
git ls-files | wc -l                                     # 1344
git status --porcelain=v1
git merge-base --is-ancestor 583c05c cb8c9b7a
git show 583c05c:packages/engine/src/ontolearn_engine/storage.py | grep -n "def _fact" -A 14
git show 583c05c:packages/engine/src/ontolearn_engine/rdf_snapshot.py | grep -n "def term" -A 32
git diff 583c05c..cb8c9b7a -- <每个变更文件>             # 逐文件读 diff
wc -c / shasum -a 256 <附件>
unzip -l / unzip -p <vendored wheel> rdflib/plugins/parsers/notation3.py
shasum -a 256 packages/engine/vendor/rdflib/*.whl packages/engine/vendor/rdflib/upstream/*.whl
.venv/bin/python -c "…"    # rdflib 版本、异常继承矩阵、_is_valid_langtag、term() 分类矩阵、
                            # 92 例对抗词法扫掠、EOF IndexError 复现、4299/4300/4301 边界
node /tmp/_xcheck2.mjs + python3   # 渲染层 digest vs Python digest（14 例）
node /tmp/_shatest3/run.mjs        # tsc 编译后手写 SHA-256 vs node:crypto（10 组）
```

**执行终态**：全部命令退出码 0（预期非 0 的 `grep -c`/`grep` 无命中场景已单独判定）；**未修改任何源、测试、配置、依赖、AGENTS、旧报告或状态文件**；**未安装、未 build、未制造包**；**未 commit / push / 切分支**；**未启动 Electron / 引擎进程 / GUI**；**未打开旧 DB**；**未读取另一方 round-04 报告**。

**本轮新增文件（唯一）**：`docs/reviews/T02/fr200-fr201-20261024/round-04/minimax-m31flash.md`（本文件）。其 bytes 与 SHA256 见最终回显。

---

## 14. 本轮实际读取的原决定与 R03 原报告（路径 / 行 索引）

| 类型 | 绝对路径 | 读取行 |
| --- | --- | --- |
| 原决定（全文 52 行） | `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/six-patches-20261023/T02-package092-R03-disposition-and-D8-decision-20261025.md` | 全文；重点 **13、24、36、38、40、44** |
| R03 原报告（本方） | `docs/reviews/T02/fr200-fr201-20261024/round-03/minimax-m31flash.md` | 5–13、102、145、162、167–179、271、281、472、483–486 |
| R03 原报告（他方） | `docs/reviews/T02/fr200-fr201-20261024/round-03/zcode-glm53.md` | 65、80、102、113、157、163、170、337、354 |
| 身份政策 | `docs/iterations/I01/ADR-0002-storage.md` | 27 |
| 需求 | `docs/prd/PRD-本体学习与落地Agent工作台.md` | 307–319 |
| 工程门禁 | `AGENTS.md`（用户覆盖件，SHA256 `de15f6ce…`） | 全文 |
| 状态来源 | `docs/m0-checklist.md` | 全文 35 行 |

---

*本报告为 MiniMax M3.1-Flash / xhigh / always-authorize 独立审查原件。所有结论均标注本方实际读/测范围；凡由子代理委派核验或仅由收据断言支持的部分，均已在正文中显式区分，未伪装为本方执行。*
