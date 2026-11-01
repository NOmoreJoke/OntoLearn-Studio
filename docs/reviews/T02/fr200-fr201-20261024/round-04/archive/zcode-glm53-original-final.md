# T02 cb8c9b7a / package094 全新 R04 独立完整工程审查（zcode-glm53）

## 0. 结论（结论先行）

**最终结论：本审查范围内有条件通过（Pass）。** 条件与范围见 §10；不构成总代发布通过，mergedUsableFRs 仍为 2/17，未 push/PR/CI/merge。

依据摘要：

1. R03 唯一阻断项（数字型语言标签与超长裸整数逃逸为未受控异常 → 会话 HOLD）已在本候选 `cb8c9b7a` 实质关闭：本人独立核验了 vendored rdflib fr201.3 补丁的抛点类型化（`InvalidLanguageTagError`/`IntegerDigitLimitError` 等 → `Notation3InputError`）、`rdf_snapshot.term()` 的 `TermInputError` 收敛、`preview_changeset` 守卫的 `INVALID_REQUEST` 受控拒绝、pyproject/uv.lock/NOTICE 的供应链接线，以及真实独立 stdio 子进程 + package094 GUI 的端到端测试与运行证据。
2. FR-200/FR-201 本轮范围内的语义实现（真实表单 CRUD、事实原 ID 编辑、保留身份不可占用、多值并存、单值声明冲突、ownership 可见定位、词法受控拒绝）与 PRD FR-200/201 条款、附录 C/D/E/G、ADR-0002 身份政策逐条对得上（§5.2）。
3. 对用户中途补齐的原始需求（D8 决定单第 13/40 行），本人完成独立评估：现行"语法合法但非 canonical 大小写（`de-CH-1901`）→ 受控 INVALID_REQUEST；小写 `de-ch-1901`/`en-001` 正控接受"的边界满足既有需求的自洽解读（不按数字结尾一概拒绝、不静默 normalize），但 `de-CH-1901` 这一字面拼写被拒绝与 D8 第 13 行例证字面存在张力，单列为**需用户确认的语义边界**（§5.5、问题 6），不由本人代为批准或否决。
4. 本轮未发现新的阻断级缺陷。问题清单 7 项全部为低/信息级或既有 OPEN 的如实延续（§6）；已知无法确认项与独立 HOLD 见 §7。

本轮为全新独立审查：未读取另一方 round-04 报告（round-04 目录在我写入前不存在）；R01–R03 历史报告仅作历史原件对照，未沿用任何一方结论。

---

## 1. 任务、模型、思考、权限与输入完整性

| 项 | 值 | 来源与限定 |
| --- | --- | --- |
| 审查类型 | T02 cb8c9b7a / package094 全新 R04 独立完整工程审查（累计 58 叶，非只看末叶） | 任务下达 |
| 运行 App | ZCode | 本会话运行时 |
| 模型 | `account:bigmodel-start-plan/GLM-5.3` | 本会话 harness 环境声明（本人实际可知者） |
| 思考等级 | 任务声明"最高"；本人无法在会话内独立 UI 回读核对，如实标注为任务下达值 | 任务下达第 1 行 |
| 权限 | 任务声明"完全访问"；AGENTS 用户级记录 ZCode 默认 `permission.mode=yolo`。本轮实际仅执行只读命令与写入本报告一个文件 | 任务下达 + AGENTS.md（用户级） |
| 唯一写入 | 本文件 | 任务下达指定绝对路径 |
| 未做 | 未改任何源/测试/配置/依赖/AGENTS/旧报告/状态文件；未安装、未 build、未制造包、未 commit/push/切分支；未复跑全量 check（无变化不重跑）；未启动 GUI/包；未打开/复制旧 DB；未执行 SQL/PRAGMA 于产品库 | 本轮实际行为 |

### 1.1 输入完整性核验（本人实际执行，恰一次）

| 项 | 下达值 | 实测 | 结论 |
| --- | --- | --- | --- |
| 粘贴件路径 | `/Users/kyle/.zcode/tmp/paste-attachments/2026-10-25/pasted-text-20261025-121232-abbb18cf.txt` | 同 | 一致 |
| 全文 bytes | 24557 | `wc -c` → 24557 | 一致 |
| 全文 SHA256 | `1f2ca83dc538d79c6e6edd5c42422eeec1b80cf8b910b17c078a73e469521b0d` | `shasum -a 256` → 同 | 一致 |
| 末尾用户原清单 11255B 恰一次至 EOF | 要求 | 自 marker `你现在是我的软件工程审查员。`（字节偏移 13302）至 EOF 恰 **11255 字节**，SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`，首尾行字节核验无误；该 marker 在全文仅出现一次 | 一致（本报告引用该清单内容仅此一次依据） |
| 全文读至 EOF | 要求 | Read 工具全 211 行读毕 + 上述字节级复核 | 完成 |
| 未读取 | 另一方 round-04 报告 | `docs/reviews/T02/fr200-fr201-20261024/round-04/` 写入前不存在（`ls` 确认） | 合规 |

### 1.2 中途补齐的原需求依据（本轮新增输入，本人实际读取）

任务中途收到用户补齐指令后，本人全文读取（49 行）：

`/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/six-patches-20261023/T02-package092-R03-disposition-and-D8-decision-20261025.md`

关键原文（本人实读并引用）：

- **第 13 行**："语言标签应按实际首子段约束判断：`1`、`zh1`等非法；`en-001`、`de-CH-1901`等后续数字子段合法，不能一概拒绝数字结尾标签。超4300位裸整数是本次语料观察到的另一个普通ValueError抛点……"
- **第 38 行**：选择 A——本候选维持不合并、允许原负责会话最小修复、明确解除 T02 本功能 R4+ 限制、修复后的新候选继续同版验证/包内验收/两指定模型独立审查。
- **第 40 行**：必要验证范围——"已确认非法语言标签new + 真实已提交原ID的edit；合法数字子段对照；超长裸整数分类评估；拒前后完整Read/身份不变、同host后续合法preview/全Diff确认/Job/marker成功；原未知parser/N3/Store/坏快照HOLD反例保持；同版完整check、实际GUI及包内原验收……不泛捕ValueError、不按异常文案分类、不静默normalize、不放宽cap。"
- 第 44 行"用户尚未决定"为当时历史状态；用户其后已采纳选择 A（本轮 R04 得以发生本身与该采纳一致）。

对照原 R03 源报告（历史原件，均为 2026-10-25 所写）：

- `round-03/minimax-m31flash.md`（79648B）：**第 102 行**探针 5 给出语法域依据——`_is_valid_langtag` 正则 `^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$`：首段含数字失败（`1`/`zh1`/`a1`），`zh`/`en-001`/`de-CH-1901`/`sl-rozaj` 合法；**第 246 行**重申"不泛捕 ValueError、不按文本分类、不解除 UNKNOWN/HOLD、不静默 normalize"。
- `round-03/zcode-glm53.md`（54415B）：全文无 `de-CH`/`en-001` 字样（grep 核实），大小写 canonical 政策非其 R03 议题。

补齐指令到达时本人**尚未落盘任何报告稿**，故无"首稿保留"义务；本文件为唯一稿。

---

## 2. 冻结候选身份（本人独立复核）

| 项 | 下达值 | 实测 | 结论 |
| --- | --- | --- | --- |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | `pwd` → 同 | 一致 |
| branch | `feature/weekly-t02-fr200-fr201` | `git branch --show-current` → 同 | 一致 |
| head | `cb8c9b7a5d780544b2910901ec9141236905d65c` | `git rev-parse HEAD` → 同 | 一致 |
| tree | `b8010eea4e04f962598a80d767b7a9ea24d2d7e7` | `git rev-parse HEAD^{tree}` → 同 | 一致 |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | `git cat-file -t` → commit | 一致 |
| 累计 base 差异 | 58 叶 | `git diff --name-only base..HEAD \| wc -l` → 58 | 一致 |
| tracked source | 1344 | `git ls-files \| wc -l` → 1344 | 一致 |
| 远端 | develop 仍 base | `git ls-remote origin refs/heads/develop` → `583c05c7…`（exit 0） | 一致 |
| AGENTS.md 未暂存覆盖 | 15147B / SHA `de15f6ce…56a5c8c4` | `wc -c` 15147；`shasum -a 256` 同；内容经系统投递全文读取（现行最新政策，含 2026-10-21/22 更新节） | 一致 |
| dirty 归属 | AGENTS 覆盖 + round01–03 历史 + 本报告 | `git status --porcelain` → `M AGENTS.md`（用户政策覆盖，保护、非本方改动）、`?? round-01/ round-02/ round-03/`（6 份历史指定报告，untracked、保护）、本报告所在 `round-04/`（本方唯一新建）；另有 tracked `independent-review-source-94e20d4a.md`（在 58 叶 diff 内） | 一致 |

base→head 共 26 个提交；R03 候选 `45f64b38` 之后新增 5 个修复提交（`4472cd9f` 语言/整数分类、`0e7ba05b`/`a0b125e1` 测试、`362394aa` 读admission保持、`41a58557` 干净后继、`ef54674f`+`cb8c9b7a` rows/text 末编码预付），45f64..HEAD 差 19 叶 +2776/−311。

**未发现身份不符；产品源无新变化。**

---

## 3. 已检查范围（实际阅读/核验，非引用）

### 3.1 正式票与七份收据原件（全部字节+SHA256 本人实测一致）

| 文件（`iteration-control/2026-10-21-weekly-release/six-patches-20261023/` 下） | bytes | SHA256（本人实测） |
| --- | --- | --- |
| controller-t02-cb8c9b7a-package094-fresh-r04-review-authorization-20261025.json | 6083 | `26091fa3bc24f6782b484295e7f4a25b7abd1bc1d0fe5effa1151c3224d2fa21` ✔ |
| controller-t02-cb8c9b7a-fullcheck-actual-root-acceptance-20261025.json | 3553 | `aed03c75fdeac44710bab63b49ed214c98df4faa3a1a678dc8a03d8de49dc840` ✔ |
| controller-t02-cb8c9b7a-full6-gui-actual-root-acceptance-20261025.json | 3047 | `88e8e5d2d64c8e33b8a412ea568ab43126d0eb876dc548e5dce1f8b26ac01b08` ✔ |
| controller-t11-package094-cb8c9b7a-mechanical-root-acceptance-20261025.json | 6628 | `3e214eb2edc07206966efbcce93af4f9fabd25e27870cfb525c710d3b0cd8f3c` ✔ |
| controller-t01-package094-cb8c9b7a-original18-actual-root-acceptance-20261025.json | 3825 | `6467704672bcd3dd2bd3c75a369b47b20fefee796621ad2d3abd634c2ba7edc4` ✔ |
| controller-t01-package094-cb8c9b7a-threefault-native-actual-root-acceptance-20261025.json | 4393 | `d5d3a3b9fa597caee665afa404e1ba239f448eb4b028c8d39f54897cdcd15bca` ✔ |
| controller-t01-package094-cb8c9b7a-named-actual-root-acceptance-20261025.json | 43773 | `473ae2301a0be98ee992d70a79fe79d633e71f7aac0f96229a87f73dfc5322d9` ✔ |
| controller-t01-package094-cb8c9b7a-text002-actual-root-acceptance-20261025.json | 4164 | `4dd93a0b3800b7b73faf5b013639ee01fb33b98737859936afa41444dfb1a351` ✔ |

八份 JSON 正文全部本人通读（含 named 43KB 全文）。这些是**他方已验证事实的收据**，本人不将其当作本人执行；下述为本人独立抽验锚定的原始证据（哈希与收据 pin 一致）：

- `outputs/20261025_t02_rows_text_integration_029/full-check-01.json`（2884B `1b820db5…` ✔）、`full-check-01.stdout.log`（12986B `5857e586…` ✔，尾部本人实读：`3719 passed, 50 skipped, 1 warning in 161.84s`，1 warning 为原 duplicate-ZIP；JSON 内 exitCode 0 / naturalExit true / elapsed 181.28s / head+tree 与候选一致）。
- `outputs/20261025_t02_rows_text_integration_029/runtime-full6-001/report.json`（3996489B `ce072a8d…` ✔；stats：expected 6 / skipped 0 / unexpected 0 / flaky 0）。
- `outputs/20261025_t01_package094_named_inputs_001/named-api-isolated-001/report.json`（2177998B `220ded23…` ✔；stats：expected 24 / skipped 0 / unexpected 0 / flaky 0）。
- `outputs/20261025_t01_package094_text_inputs_002/records/packaged-text-pages.actual-001.json`（17692B `98814795…` ✔）与 `ACTUAL-TEXT002-SEMANTIC-SUMMARY-001.json`（本人实读：PASS 2/FAIL 0/SKIP 0，ASCII 变体 pages 5、utf8PageLengths `[30720,23990,1499,94,6]`、utf8Bytes=unicodeScalars=56309、App/Engine PID 10579/10589 实际 exit/close 0、textSHA256、guardsBeforeAfterEqual=true、trace 2078506B 另有 pin）。

本人**未**复跑任何产品/GUI/包/测试；以上为只读核验。

### 3.2 需求与决定文件（实读）

PRD `docs/prd/PRD-本体学习与落地Agent工作台.md`：FR-200（307–309）、FR-201（311–318，含"两种操作语义区分/不得同一句自然语句模糊代替/可经 RDF 核对"）、附录 C 全表（959–981）、附录 D（983–1014）、附录 E（1016–1092）、附录 G（1115–1178+）。`docs/iterations/I01/ADR-0002-storage.md`（第 19/27/29 行：事实记录与 owner/source_row/managed_value、内容派生 ID 与 `term(value).n3()` canonical 身份、非规范别名拒绝提交、`edits={factId:object}` 保持原 ID、墓碑保留初始 ID、冲突返回原 owner/source_row/slot/id、多值并存、`manual` 只新增、受管记录人工漂移停止映射重跑）。D8 决定单（§1.2）。

### 3.3 实现与调用链（实读源码，非只看测试名）

- 引擎：`project/mainline.py`（1206 行全文）、`storage.py`（1887 行中 manual/edits/remove 循环、`_check_slot`、`_validate_single_slots`、`ManualOwnershipConflict`/`SingleDeclarationConflict`、`canonical`/`digest`）、`job_store.py`（`_transaction` admission 边界、`_application`、`_ownership_header/_segment`、`_persist_ownership_detail`、`ownership_detail_page`）、`coordinator.py`（diff 部分：`project.ownership.detail` 注册、changeset.preview 注入 ownership_proof、bootstrap `prepare_mainline_store`）、`project/domain_changesets.py`（preview 守卫、`pack`、`_document`、undo-impact 持久化）、`project/project_host.py`（`material_profile`/`admit_terminal_growth` 重构）、`project/query_presentation.py`（497 行全文：rows/text 分页与 `_RowsPrepaid` 预付）、`rdf_snapshot.py`（76 行全文）。
- 桌面：`desktop-ipc.ts`、`engine.ts`（MainlineMethod 白名单 + projectId==selected 校验）、`project-mainline-service.ts`（`getOwnershipConflictDetailPage` 以主进程 current.projectId 覆盖 args + 事后 owner/epoch/session 复核）、`preload/index.ts`（业务命名方法，仅 +1 行）。
- 渲染：`mainline-session.ts`（OWNERSHIP_CONFLICT → detail 三态机、`#sequence` 递增防陈旧）、`mainline-ownership.ts`（78 行全文：分页拉取 + `matchesOwnershipDetail` 逐页验证 + `reassembleOwnershipDetail` + `sourceBaseRevision` 绑定）、`OwnershipConflictDetailView.ts`（105 行全文：原 ID/owner/sourceRow/slot 展示，React `createElement` 文本渲染无 innerHTML）、`mainline-facts.ts`（原 ID 编辑、digest 派生新 ID、lone surrogate 拒绝）、`OntologyMainlinePage.tsx`（事实生命周期栅栏/表单保留）、`OntologyPage.tsx`（pattern 连字符转义）。
- 契约：`packages/contracts/src/v2.ts`（`matchesOwnershipDetail` + 手写 SHA-256）、`src/index.ts`（`reassembleOwnershipDetail` 预算：nodes 16384/depth 8/每字符串 43692/总字符 512×44690）、`v2/schema.json`（`ownershipDetailDocument/Header/Manifest`、`params_/result_project.ownership.detail` 两段式、`changeSetFact/Plan/Triple` 262144 上限、`id`/`hash` defs）、`registry.json`（方法注册）、`python/contract_v2.py`（`ownership_detail_matches`）、`errors.json`（26 码）。
- 供应链：`packages/engine/vendor/rdflib/notation3-input-types.patch`（全文）、`PROVENANCE.json`（schema/3 全文）、`repack-rdflib-input-types.py`（哈希核验）、`pyproject.toml`、`uv.lock`（rdflib path+hash pin）、`licenses/NOTICE`。
- 测试：6 个新引擎测试文件（3490 行，48 个测试函数）抽样精读（language_input_rejection 全文关键段、manual_input_rejection 拒绝族、postwrite/budget 断言面）；e2e `t02-fr200-fr201.spec.ts` 关键向量段（815–845）。

### 3.4 历史报告（保护原件，只读）

`round-01/`、`round-02/`、`round-03/` 各两份（zcode/minimax）。本轮精读 round-03 双方结论与问题清单、round-03 minimax 第 1/2/102/246 行等关键段；round-01/02 仅经 round-03 双方处置表与 D8 决定单转引定位，未逐字重读全文（如实标注）。**未读取任何 round-04 内容**（写入前目录不存在）。

---

## 4. 实际执行的验证与真实结果

全部为只读命令；无产品运行、无 GUI、无包、无测试复跑、无 SQL 于产品库。

| # | 命令（概述） | 结果 |
| --- | --- | --- |
| 1 | `wc -c` + `shasum -a 256` + Python 字节级 tail 复核粘贴件 | 24557B / `1f2ca83d…`；tail 11255B @offset 13302，tail SHA `1ca23def…`，恰一次 |
| 2 | `pwd`/`git branch`/`git rev-parse HEAD`/`HEAD^{tree}`/`cat-file -t base`/`git status --porcelain`/`git ls-files \| wc -l`/`git diff --name-only base..HEAD \| wc -l` | §2 全部一致 |
| 3 | `git ls-remote origin refs/heads/develop` | `583c05c7…`，exit 0 |
| 4 | 8 份收据 `wc -c`+`shasum -a 256` 循环 | §3.1 八项全一致 |
| 5 | `git diff --name-status/--stat base..HEAD`、45f64..HEAD stat | 58 叶清单与分文件规模（§2） |
| 6 | O029/full6/named/text002 关键文件 `shasum -a 256` + JSON 解析抽读 | §3.1 四项 pin 一致；stdout 尾部与 stats 实读 |
| 7 | vendor 四文件 + repack 脚本 `shasum -a 256` + `wc -c` | 与 PROVENANCE schema/3 全部一致（fr201.3 wheel `99fab7bd…` 2379774B、upstream `30c0a3eb…` 615416B、patch `de5755d6…` 5012B、LICENSE `53a705e5…` 1524B、repack `166b0919…`） |
| 8 | `uv.lock` rdflib 条目解析 | `7.6.0+ontolearn.fr201.3` path wheel + hash `99fab7bd…` 一致 |
| 9 | 源码/契约/schema/测试精读（§3.3 清单） | §5 判断依据 |
| 10 | D8 决定单全文读取 + round-03 双方关键行 grep 对照 | §1.2、§5.5 |

无新增实测缺口需要申请协调运行：本人认为现有已保存 raw + 源码级核验足以支撑本范围结论。

---

## 5. 独立技术判断（本人核对，非引用开发方或 ROOT 结论）

### 5.1 R03 阻断项关闭链（T02-R03-01）独立验证

缺陷链（R03 时点）：`"设备"@1`/`"@zh1` → rdflib `term.py:661` 普通 `ValueError` → `rdf_snapshot.term()` 的 `except Exception` 降级 → `preview_changeset` 守卫只捕 `TermInputError` → 逃逸 → `classify()` INTERNAL_ERROR → `observe_error()` 置 `hold=True` → 会话级不可用。超长裸整数（`notation3.py:1577`）同类。

本候选关闭链（本人逐步核对）：

1. **vendored 补丁**（`notation3-input-types.patch`，随 fr201.3 wheel 安装）：`RDFSink.newLiteral` 在调用 `Literal(s, lang=lang)` 前以 `_is_valid_langtag` 预检非空 lang，失败抛 `InvalidLanguageTagError(Notation3InputError, ValueError)`；`nodeOrLiteral` 对已匹配 ASCII 带符号十进制整数按 `sys.get_int_max_str_digits()`（实测 4300）主动抛 `IntegerDigitLimitError`；另类型化 `RelativeIRIBaseError`/`UnicodeCodePointError`/`UnterminatedStringError`/`MissingDatatypeError`。无泛捕、无文案分类、无 cap 改写（补丁 `changeScope` 与本人阅读一致）。
2. **消费层**（`rdf_snapshot.py:35-46`）：`except (BadSyntax, Notation3InputError) → TermInputError`；其余未知解析器失败保持 `ValueError`（UNKNOWN，符合"不解除未知 HOLD"）。
3. **preview 守卫**（`domain_changesets.py:437-453`）：manual 的 S/P 经 `iri()`、manual object 与 edits 全部值经 `term()`，`TermInputError` 或 `parsed.n3() != value` → `fail("INVALID_REQUEST", field="params")`——受控拒绝、事务回滚、无 HOLD。
4. **测试**（`test_mainline_language_input_rejection.py`）：R03_REFUSALS 三族（`"设备"@1`、`"设备"@zh1`、`9*4301`）× manual/edit，同 owned host 拒绝后同宿主读/提交成功；独立 stdio 子进程版本（真实 `ontolearn_engine --t01-internal-profile=business3`、wire trace、物理 DB 文件级 `database_files` 哈希）断言拒绝 + 后继成功 + 进程自然 exit 0。
5. **package094 运行证据**：named24（`ROOTCanonicalNumericSubtagFourChainsVerified`、8 个 R03 新增拒绝 + 8 物理向量不变、43 拒绝 FullRead 不变、98 真实事务）；GUI full6 8 新增 typed 边界输入覆盖 new 与真实 committed ID 编辑。收据哈希本人锚定（§3.1）。

结论：R03-01 阻断已实质关闭，且方式符合 D8 第 40 行约束（专用类型/受控预检，未泛捕、未按文案、未静默 normalize、未动 cap）。

### 5.2 FR-200/FR-201 核心语义 vs 需求

- **真实表单 CRUD**：OntologyMainlinePage 事实表单（subject/predicate/object + 原记录 ID 装载）→ `manualFactPlan`（edit/remove 保原 ID）/`newManualFactPlan`（add）→ preview → 全 Diff 展示 → 人工确认按钮提交；e2e full6 六例 57 成功事务。对应 FR-200"通过表格和表单创建、编辑、复制和删除"（本迭代事实面）。
- **事实原 ID**：`edits={factId:object}` 引擎侧保持记录身份（storage.py:798-815）；ADR-0002 第 27 行"编辑后 ID 仍是初始内容摘要"一致；GUI 8 新增输入含真实 committed ID 编辑（收据 `ROOT8TypedBoundaryNewAndRealOriginalIdEditAndFollowingLegalJobsVerified`）。渲染端 add 的 digest 派生 ID 与引擎 `digest([S,P,O])`（`canonical` ensure_ascii=False、separators 与 JSON.stringify 一致；lone surrogates 前置拒绝）字节等价（§5.4 复核）。
- **多值与单值**：`_check_slot` 仅对单值谓词或同值语句拒绝，不同值多值并存（ADR-0002 第 29 行）；`_validate_single_slots` 提交时检查声明与既有事实矛盾，引入声明的同计划移除不再作为签发者。
- **ownership 可见定位**：四族 witness（reservedIdentity/sameStatement/singleSlot + singleDeclaration）来自真实阻断行（`ManualOwnershipConflict` 构造时 incoming 的 owner/source_row 显式置 None，不虚构）；持久化为分段哈希文档（`_persist_ownership_detail`：指纹去重、REVISION_CONFLICT 基线复核、逐段 base64/sha256 校验、写入前后双 admission）；分页读（`ownership_detail_page` 两段式 cursor、逐页 256KiB/帧预算）；渲染端逐页 `matchesOwnershipDetail`（TS 手写 SHA-256，≤32KiB 段正确）+ `reassembleOwnershipDetail` 全文档哈希 + `sourceBaseRevision` 绑定 + `OwnershipConflictDetailView` 展示原始 ID/owner/sourceRow/slot 与中文行动提示。对应 FR-201"用户必须能够通过实际 RDF 核对生成结果"与 ADR-0002"冲突返回原 owner/source_row/slot/id"。
- **跨层授权**：渲染不能传 projectId（主进程覆盖）、引擎侧 `authorize`/`check_reply`/`_OwnershipProof.check`（store/connection/lease/generation/session 六重绑定）、`ownership_proof` 仅 `changeset.preview`/`project.ownership.detail` 两用途、 supervisor 校验 params 契约与 selected 一致。旧三字段 legacy detail 与 confirm receipt 头有显式分类（INVALID_STATE/NOT_FOUND），不误读为他类型。

### 5.3 R03 后 5 个修复提交的独立复核

- `ef54674f` + `cb8c9b7a`（rows/text 末编码预付）：`text_page`/`rows_page` 在候选搜索/行装配**之前**以 `ticket.pay("text/rows final prepaid")` 预留末次 `_room` 编码费（4×maxPageBytes+4096 / 256 / 8×maxPageBytes+4096，rows 另加 `_rows_final_overhead`），`_RowsPrepaid` 本地账本只消费不退款、`complete()` 强制归零；候选失败的 RESOURCE_LIMIT 只收缩前缀，末编码不再被候选消耗挤掉（本人核对 `_room` 费用与预付值精确相等、`final.check`/`ticket.check` 在 cursor 分配与 deliver 前后均在场）。`begin_transaction` 对 rowsPage/textPage reply 预付 `_final_material_cost()`（8×schema+64KB 标量），`check_final_material` 拒绝重复 settle（`INVALID_STATE`）。text002（56309/56314 字节 5 页）与 named large 3 页为运行侧证据。
- `362394aa`（读 admission 跨受控写保持）：`JobStore._transaction` 边界在 `before_commit` 调 `check_final_material`；`settlement_failed`/`completed` 对未知异常保留 holding、绝不退款复用；`mark_controlled` 覆盖 `_save`/`commit_job`/`start_job_run`。
- `41a58557`（干净后继）：`_clean_predecessor` 16 项条件（clean_close、reader 归闭、actor 无活动任务/队列等）；bootstrap 的不确定 writer 不被首任或后继收养（`bind` 五状态检查）。O027 的两个 clean successor PERMISSION_DENIED 首败与修复后通过的历史均保留（收据 `precheckUnicodeKeyErrorPreserved` 等）。
- **一个我曾怀疑并亲自闭合的疑点**（记录判断过程）：`_persist_ownership_detail` 去重循环对项目内**所有** `job_details` 行要求 ≤ validation_bytes(1.5MiB) 否则 `STORAGE_FAILURE`（会触发 hold），而 undo-impact/确认回执等合法行可至 16MiB——本人追查后确认该路径不可达为缺陷：`_persist_ownership_detail` 在循环**之前**先 `proof.admissions()` → `material_profile`（core=True 时 job_details 计入 total_bytes，超 1.5MiB 即 `RESOURCE_LIMIT page` 受控拒绝），单行 >1.5MiB 蕴含总量 >1.5MiB，故 STORAGE_FAILURE 分支被前置 admission 封死；同量级费用（32×size/行）上界 32×1.5MiB=48MiB < 128MiB 书。该边界退化为已披露的容量 RESOURCE_LIMIT.page 政策（Q5/D2），非新缺陷。

### 5.4 身份/摘要一致性与注入面

- `canonical`（`ensure_ascii=False, sort_keys=True, separators=(",",":")`）与渲染端 `JSON.stringify`+TextEncoder 对无 lone-surrogate 字符串字节等价；lone surrogates 在 `newManualFactPlan` 前置拒绝——ID 派生跨语言一致。
- 动态 SQL 仅两处（`material_profile`/`_OwnershipProof.material_profile` 的表名/列名拼接）：标识符取自 `sqlite_master`/`PRAGMA table_info`，`"` 一律双写转义，值一律参数化——无注入面（本人逐行核）。
- 示例资源读取：`O_NOFOLLOW|O_NONBLOCK` 打开、仅常规文件、大小上限、前后 `fstat` 四元组比对——TOCTOU 加固到位；Windows 走独立模块。

### 5.5 D8 原需求 vs 现行 de-CH-1901 边界（用户中途补齐点的独立评估）

**现行行为**（代码 + 测试事实）：

- 语法层：`_is_valid_langtag`（`^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$`）判定——`1`、`zh1`（首子段约束失败）解析器层即拒（`InvalidLanguageTagError`）；`en-001`、`de-CH-1901` **语法均接受**（`test_digit_subtags_are_grammatical_separate_from_canonical_case_policy`：`term('"设备"@de-CH-1901').n3() == '"设备"@de-ch-1901'`，证明可解析且 n3 输出小写）。
- 消费层：`preview_changeset` 要求 `parsed.n3() == value`——小写 `en-001`、`de-ch-1901` 端到端接受并真实提交（引擎 stdio 双族 + package094 named 四链 canonical cohorts）；混合大小写 `de-CH-1901` 得 `INVALID_REQUEST`（受控、可恢复、无 HOLD；stdio 测试 `test_grammatical_uppercase_subtag_keeps_existing_canonical_rejection` manual/edit 双族 + e2e 向量 `noncanonical-language-case`，e2e 注释自述"Valid language syntax, but ADR-0002 requires the exact lowercase canonical spelling. Do not silently normalize the caller's input."）。

**对照原需求**（D8 第 13/40 行 + MM R03 102/246 行 + ADR-0002 第 27 行）：

| 原需求约束 | 现行实现 | 判定 |
| --- | --- | --- |
| "按实际首子段约束判断：`1`、`zh1` 等非法" | 首子段约束失败在解析器层类型化拒绝，端到端覆盖 | 满足 |
| "`en-001`、`de-CH-1901` 等**后续数字子段**合法，**不能一概拒绝数字结尾标签**" | 数字结尾作为**类别**未被拒绝：`en-001`、`de-ch-1901`（皆数字结尾）在单测/stdio/包内 GUI 四链全部受控接受并提交；拒绝维度是大小写规范形（与数字无关） | 满足（类别解读） |
| "不得静默 normalize"（D8 40、MM 246） | `term()` 内部小写化**从不落库**：`parsed.n3() != value` 把任何规范化差异转为显式 `INVALID_REQUEST`；无任何静默改写接受路径 | 满足 |
| ADR-0002（base 既有）："对象必须等于 `term(value).n3()`……非规范别名拒绝提交" | 大小写变体即非规范别名，按既有身份政策拒绝 | 一致 |

**结论与残余张力**：在"不静默 normalize + ADR-0002 canonical 身份"双约束下，"接受 `de-CH-1901` 原样"只有两条路——(a) 规范化为小写后落库（违反"不静默 normalize"，被 D8 40 明确禁止）；(b) 大小写保形存储（与 ADR-0002 "`n3()` 必须等于原值"的身份派生冲突，属政策改写）。因此现行边界（语法合法 → canonical 精确形接受、大小写别名受控拒绝 + 小写正控）是既有需求下**唯一自洽**的实现，本人判定其满足既有需求的自洽解读。但必须如实上报：D8 第 13 行以 `de-CH-1901` 这一**字面拼写**作"合法"例证（其语境是 MM 探针 5 界定 `_is_valid_langtag` 触发域，即语法合法性，而非可提交拼写），现行实现下该字面拼写不可提交、需用户改用 `de-ch-1901`；若用户原意是"该字面拼写必须可提交"，则与 D8 第 40 行及 ADR-0002 不相容，须由用户显式改写其一。**本人不将任务 prompt 对该拒绝行为的描述视为用户另行批准的新语义**；此项列为问题 6（需用户确认的语义边界，非缺陷、非阻断）。

---

## 6. 问题清单（按严重程度；本轮无阻断/高危，7 项，不凑满 10）

### 问题 1【低 · 非阻断】ownership/单值声明 witness 的"首个阻断行"选取无 ORDER BY，跨运行不确定

- 位置：`packages/engine/src/ontolearn_engine/storage.py:1226-1232`（`_check_slot` 的 `SELECT * FROM facts WHERE project=? AND subject=? AND predicate=?` 无 ORDER BY）；`storage.py:1147-1170`（`_validate_single_slots` 的 `GROUP BY subject … LIMIT 1` 与 `LIMIT 2` 行序同样未定）。
- 触发反例：同槽同时存在保留 ID 行与同值行（或多行同值）时，SQLite 依查询计划/物理布局返回的首行不同，`ManualOwnershipConflict.witness.existing` 与 `SingleDeclarationConflict.existing[]` 展示的"首个阻断记录"在不同运行/库布局下可能不同。
- 风险：定位展示与测试快照的可复现性受损；不改变拒绝结果、回滚与一致性。
- 证据：本人实读上述行；R03 双方（Z R03-04 / MM R02-03）与 D8 处置表第 23 行均"保留未确认/无构造性反例"；本轮仍未修。
- 验收建议：两处查询加 `ORDER BY id`，补同槽双冲突确定性回归（同一库两种物理插入序断言同一 existing）。
- 阻断：否。

### 问题 2【低 · 非阻断】witness 字符串上限跨层不一致：极端合法输入使 UI 冲突定位恒为"暂不可用"

- 位置：引擎/契约允许 `changeSetFact`/edits 值至 262144 字符、`ownershipDetailDocument` 字符串 maxLength 16777216（`packages/contracts/v2/schema.json`）；渲染端 `reassembleOwnershipDetail` 每字符串硬上限 43690/43692 字符（`packages/contracts/src/index.ts:961-966` `value.length > 43692`）。
- 触发反例：wire 提交 subject 为 50000 字符的合法绝对 IRI（`iri()` 无长度检查、schema 允许）→ 后续冲突 witness 含该串 → 引擎持久化成功 → 渲染端 `capture()` 判 invalid → 详情显示"冲突详情暂不可用"。
- 风险：FR-201 定位能力在极端但合法输入上优雅降级（受控、无泄露、无崩溃）；已发布 UI 不可达（正常 IRIs 远小于阈值）。MM R03-06 延续（16MiB 引擎 vs 渲染端上限不混同），本轮仍未统一。
- 验收建议：schema 将 witness 内字符串收紧至 ≤43690，或渲染端上限与页预算显示一致化；补跨层边界测试。
- 阻断：否。

### 问题 3【低 · 延续 OPEN】wire 层 `definitions[].value.triples[].object` 已知词法错误仍走 UNKNOWN → INTERNAL_ERROR → 会话 HOLD

- 位置：`packages/engine/src/ontolearn_engine/project/domain_changesets.py:437-453`（preview 守卫仅覆盖 manual S/P/O 与 edits 值）；`storage.py` `_definition` 对 triples object 抛普通 `ValueError`。
- 触发反例：wire 调用方（未来 Agent 草稿）在定义 triples 提交未闭合引号/非法词法 → UNKNOWN → HOLD → 项目会话不可用。当前已发布 UI 生成 canonical 词法，不可达。
- 风险：与事实面同类缺陷残留；Agent 草稿接线前必须收口（D8 处置表第 24 行：T01 接线原始 triples/Agent 前处理，不能说已修）。
- 验收建议：接线时把守卫同样扩展到显式 triples 对象（TermInputError/非规范 → INVALID_REQUEST），勿静默规范化。
- 阻断：否（FR-200/201 主验收不依赖该面；如实登记 OPEN）。

### 问题 4【低 · 延续】`Conflict` "ownership" 类别无错误码映射；通用非 witness 所有权冲突无定位

- 位置：`storage.py:56-64`（类别→码映射无 `"ownership"` 键，默认 `INTERNAL_ERROR`）；`_check_slot` 对非 manual_incoming 路径（如受管行编辑、映射人工漂移 `_replace_mapping`）抛普通 `Conflict`，`_application` 拦截后写旧三字段 detail → 新 getter `INVALID_STATE` → UI"详情暂不可用"（设计内降级、无泄露）。
- 风险：第三方若绕过 `_application` 直接消费 `Conflict.code` 得 INTERNAL_ERROR；通用冲突长期无定位语义（D8 处置表第 22 行：T01 真实 witness/显式无定位合同 + T02 消费展示，FR-201 收口前完成）。
- 验收建议：补 `"ownership": "OWNERSHIP_CONFLICT"` 仅码映射；为通用冲突补真实 witness 或显式"无定位"契约。
- 阻断：否。

### 问题 5【低 · 延续】渲染端错误码白名单 17 码 vs 契约 26 码，缺 16 码

- 位置：`apps/desktop/src/renderer/src/ontology/mainline-session.ts:93-112`（`message()` 白名单）；`packages/contracts/v2/errors.json` 26 码。缺集：CURSOR_EXPIRED/CURSOR_MISMATCH/ENGINE_EXITED/HANDSHAKE_REQUIRED/MAPPING_VALUE_INVALID/METHOD_NOT_ALLOWED/NETWORK_FORBIDDEN/NOT_FOUND/PAYLOAD_EVICTED/QUEUE_FULL/SEMANTIC_INPUT_INVALID/SESSION_MISMATCH/TIMEOUT/UNSUPPORTED_CAPABILITY/UNSUPPORTED_CONSTRUCT/VERSION_INCOMPATIBLE（本人按当前 26 码集合重算）。
- 风险：当前主线不可达；接线对应能力时若忘扩列将复现"降级 INTERNAL_ERROR 展示"。
- 验收建议：接线新能力时同步扩列，并加"白名单 ⊇ 已接线方法可产生码集"测试（D8 处置表第 27 行同款要求）。
- 阻断：否。

### 问题 6【需用户确认的语义边界 · 非缺陷】`de-CH-1901` 字面拼写受控拒绝 vs D8 第 13 行例证字面

- 位置/事实/判定：全见 §5.5。现行边界是"不静默 normalize + ADR-0002 canonical 身份"下唯一自洽实现，且数字结尾类别未被一概拒绝（`en-001`/`de-ch-1901` 正控全链通过）；但 D8 第 13 行例证的**字面拼写** `de-CH-1901` 不可提交（需改小写）。
- 需要用户表态：确认"类别合法 + canonical 拼写才可提交"即为原意；若原意是字面拼写必须可提交，则须显式改写 D8 第 40 行（不静默 normalize）或 ADR-0002 canonical 政策之一，属政策决定，不属本审查可代答。
- 阻断：否（不阻塞 FR-200/201 本轮验收；语义确认前如实保留）。

### 问题 7【信息】核心文件持续增长

- `job_store.py` 2993 行（本迭代 +406）、`storage.py` 1887 行、e2e spec 1748 行。功能正确性与可读性本轮未发现问题（本人全读 `mainline.py`/`rdf_snapshot.py`、精读其余关键段），但对应清单"拆分 AI 不断追加的 2000 行文件"项，建议后续迭代拆分 ownership detail 持久化/读页为独立模块。不阻断。

---

## 7. 无法确认项与独立 HOLD（不以静态/历史证据代替）

**无法确认（本轮只读未覆盖）**：

1. 全量 npm 依赖漏洞扫描未在本 head 复跑（无 OSV/mimosa 扫描记录；vendored rdflib 供应链已人工核验到字节/哈希/RECORD 收据级）。
2. macOS 签名/公证、whole-APP 法律与 `_distutils` 来源、目标 OS/跨平台、参考设备/低端硬件——独立 HOLD 未清（内部 unsigned 包不清这些 HOLD）。
3. 完整可访问性（全流程键盘 + 读屏）与 RTL 文本专项未验证（新增视图有 aria-label/role，属部分证据）。
4. 生产构建 CSP 实际渲染链未起 GUI 复验（沿用 I02 门禁与 O029 构建产物哈希；本人未运行应用）。
5. SQLite 迁移回滚路径（format2→3 前向有 lease 语义；回滚未见演练证据）。
6. 5×10⁶ 行级索引/分页行为（当前实测上限 243 行 4 页 + 80545B 3 页 + 56KB 文本 5 页；更大规模走受控 RESOURCE_LIMIT）。

**独立 HOLD（延续，本轮不解除）**：unknown parser/N3/Store/badSnapshot/损坏 SQLite 物理保护；native engine exit UNKNOWN；named App 退出码 UNKNOWN（known PID 缺席≠自然 0/reap/后代全闭）；standalone 恰 EOF 8 例 IndexError 未分类（不宣称解析器穷尽）；FR-201 仅 reservedIdentity family 有本轮 GUI，不推广全部 ownership family/Undo GUI/旧超限库恢复；容量累计行为（Q5/D2 无通过线）未修；mergedUsableFRs 2/17；未 push/PR/CI/merge。

---

## 8. 历史意见处置对照（R03 双方 → 本候选，本人独立复核）

| 原意见 | 本候选状态（本人依据） | 处置 |
| --- | --- | --- |
| MM T02-R03-01（High 阻断：数字语言标签/超长整数逃逸 HOLD） | §5.1 关闭链逐步核验 + fr201.3 补丁/测试/包内证据 | **已关闭**（方式符合 D8 40 约束） |
| MM T02-R03-02 / Z R03-03（托管/通用冲突无定位） | `_check_slot` 非 manual_incoming 路径仍普通 Conflict（问题 4） | 未关闭，按 D8 延期（T01/T02 分工） |
| MM T02-R03-03 / Z R03-04（行序非确定） | 无 ORDER BY 仍在（问题 1）；本人亦未构造双冲突反例 | 未关闭（低） |
| MM T02-R03-04 / Z R03-01（definitions.triples wire HOLD） | 守卫范围未扩（问题 3） | 未关闭，OPEN 延期 |
| MM T02-R03-05（PROVENANCE 陈旧） | PROVENANCE 升 schema/3、fr201.3 供应链哈希本人全验、状态语义/路径明示 | **已改善/关闭**（仓库内补丁/wheel/上游/LICENSE 可复核） |
| MM T02-R03-06（渲染端文档预算注释） | `reassembleOwnershipDetail` 现为显式 43692/512 数字预算；跨层上限不一致仍在（问题 2） | 部分改善，上限统一延期 |
| Z R03-02（白名单 16 码缺集） | OWNERSHIP_CONFLICT 已入列，缺集仍 16（问题 5） | 未关闭，延期 |
| Z R03-05（incoming 强制 null） | 四族 incoming 仍全人工来源、强制 null 与事实相符 | 范围内不成立，前瞻加固项保留 |
| Z R03-06（容量/框架映射） | §5.3 末段：本人证明 dedup-loop STORAGE_FAILURE 被 admission 前置封死，退化为已披露容量边界 | 按 ROOT 边界如实保留 |
| Z R03-07（092 运行证据语义边界） | 本轮包 094 新证据替代表述，首败链保留原则一致 | 边界确认 |

旧 0e7/41a/package092/093 历史失败、text001 首败与 Unicode NOTRUN、两次 namespace preparation 错误、full18 首次 fixture directory-metadata 控制失败、reload 首次旧 guard pin 失败、staleAX15 拒绝后 freshAX4、ROOT named 99→98 修正、O029 旧索引 C-quoting KeyError、O028 短命令断言失败——均按"不以新绿洗旧"保留，本人未发现任何被覆盖或伪造迹象。

---

## 9. 用户 11255 字节原始清单逐项适用性判定（160 项 + 尾部人员清单）

口径：本产品为本地优先单用户 Electron+Python 桌面本体工作台（M0：health + 内部存储 API + 本轮 FR-200/201 事实面；无账户/云/支付/网络服务）。判定三分：**适用**（本产品存在对应面，给达标/未达标与依据）、**不适用**（无该面；不为清单增加 SaaS/付费/账户/云功能）、**无法确认**。"达标"限于本人本轮实际核验面。

| # | 清单项（缩写） | 判定 | 依据/说明 |
| --- | --- | --- | --- |
| 1 | 有人设计的 schema | 适用·达标 | contracts v2 JSON Schema+zod 双端、registry/fixtures/binding-regressions、SQLite 表结构版本化 |
| 2 | 邮箱带 + 号的登录 | 不适用 | 无登录/邮箱（本地单用户） |
| 3 | 密码重置链接过期且一次性 | 不适用 | 同上 |
| 4 | MFA+丢失手机恢复 | 不适用 | 同上 |
| 5 | 会话超时/一键终止 | 不适用（账户语义）；引擎会话生命周期/恢复属 I02 已验面 | 无账户会话 |
| 6 | SSO | 不适用 | 无企业客户面 |
| 7 | SAML | 不适用 | 同上 |
| 8 | SCIM | 不适用 | 同上 |
| 9 | 深于 admin/everyone 的角色权限 | 适用·达标（本范围） | 引擎 permission（library.create/write/read）、ownership proof 六重绑定、admission/writer 分离、IPC 业务命名白名单 |
| 10 | 改一个数字读别人数据（IDOR） | 适用·达标（已核路径） | projectId 由主进程强制覆盖、selected/generation 校验、detailRef 绑定 origin+fingerprint；渲染无通用 invoke |
| 11 | 租户隔离 | 不适用（多租户）；单机项目级隔离达标 | 同上 |
| 12 | 管理员代登录 | 不适用 | 无支持面 |
| 13 | 登录限速 | 不适用 | 无登录 |
| 14 | 锁定不误伤 CFO | 不适用 | 同上 |
| 15 | 迁移可前进可回滚 | 部分适用 | format2→3 前向迁移+lease 已实现；回滚未演练→回滚侧无法确认 |
| 16 | 迁移不锁主表 | 适用·达标（本地语义） | 嵌入式 SQLite 单写者、启动期迁移，无高峰并发面 |
| 17 | 索引支撑 500 万行 | 部分适用 | 实测 243 行/80545B/56KB 文本；更大规模受控 RESOURCE_LIMIT；500 万行行为无法确认 |
| 18 | 连接池 | 不适用 | 无连接场景 |
| 19 | 每夜备份 | 不适用（本地数据主权；WAL/快照/backup_path 存在，无自动备份需求） | M0 边界 |
| 20 | 恢复演练 | 无法确认 | 禁止打开旧 DB，无恢复演练证据 |
| 21 | PITR | 不适用 | 无删库运维场景 |
| 22 | 软删除 | 适用·达标 | 受管事实墓碑、保留初始 ID、历史/已提交轮次不可改写 |
| 23 | 服务端（引擎）校验 | 适用·达标 | 契约 .strict()/zod + canonical 词法 + 四族冲突 + 受控拒绝码；残余 definitions.triples 面 OPEN（问题 3） |
| 24 | 时区正确存储 | 部分适用 | 时间戳安全整数/UTC 口径（收据字段）；无提醒调度→主要面不适用，存储口径达标，全量无法确认 |
| 25 | 姓氏含撇号 | 适用·达标（词法面） | UTF-8 全链、中文字面量实测；撇号在 Turtle 词法内受控处理，无 SQL 拼接 |
| 26 | emoji/重音/RTL | 部分达标 | 56309 Unicode scalars 实测（含多字节）；RTL 专项未测→无法确认（RTL） |
| 27 | 金额存整数 | 不适用 | 无金额 |
| 28 | 币种/舍入/税务 | 不适用 | 同上 |
| 29 | 数据模型抗第二客户变更 | 部分适用·达标（P0 边界内） | 版本化契约+不可变快照+canonical 身份；能力矩阵明示扩展须重评 |
| 30 | 幂等键 | 适用·达标 | operationId/operation_claims、同操作同内容返回原结果、Job 幂等 |
| 31 | 四次点击去重 | 适用·达标 | 同上；43 拒绝 FullRead 不变 |
| 32 | 第 400 页分页 | 适用（已测范围达标） | 游标校验+页/帧预算；更大规模受控拒绝（见 #17） |
| 33 | 导出表格 | 不适用（现阶段） | FR-203 Turtle 导出属后续能力，不虚称 |
| 34 | 2009 年 CSV 导入 | 不适用 | 映射 FR-300 后续 |
| 35 | 留存规则删除 | 不适用 | 本地用户数据，无合同删除义务 |
| 36 | 密钥不入代码/仓库/chat | 适用·达标 | 本轮 diff 无凭据；引擎无密钥；S3 网关未接线 |
| 37 | 轮换 AI 粘贴的密钥 | 不适用 | 未发现任何已入库密钥 |
| 38 | 确认安装的包是所要的 | 适用·达标 | vendored rdflib 哈希/PROVENANCE/uv.lock path+hash/npm 精确版本；141 wheel 载荷+151 RECORD 行收据 |
| 39 | 依赖扫描 | 部分适用·无法确认（全树） | 本 head 无自动扫描记录；rdflib 补丁人工审读达标 |
| 40 | 用户可输入处一律消毒 | 适用·达标（含披露缺口） | canonical 词法/引号/datatype/authority/语言标签/整数受控拒绝；definitions.triples 延期面如实登记 |
| 41 | SQLi/XSS/CSRF/OWASP | 适用·达标（已读面） | SQL 全参数化+标识符双写转义；React createElement 文本渲染；CSP 单源两变体；无 HTTP→CSRF 不适用 |
| 42 | 文件上传扫描/限大小/不可执行 | 适用（等价面）·达标 | 示例资源 O_NOFOLLOW/仅常规文件/大小限/前后 fstat |
| 43 | CORS 非全放行 | 不适用 | 无 HTTP 服务 |
| 44 | 每响应安全头 | 部分适用·达标 | CSP meta/header 两变体（csp.ts 唯一源）；无响应头概念的其他面不适用 |
| 45 | 静态/传输加密 | 不适用（本地单机；M0 无此要求） | 边界披露 |
| 46 | 最小权限（含 AI agent） | 适用·达标 | preload 业务命名桥、无通用 invoke、Agent 只草稿+人工确认、引擎 admission/proof/fault 边界 |
| 47 | 日志记录谁做了什么且无敏感 | 适用·达标 | operation origin（hostClientId/engineSessionId）、固定错误码、无堆栈/路径/原值跨边界 |
| 48 | 渗透测试 | 不适用（现阶段） | 未执行、未虚称 |
| 49 | 安全问卷 | 不适用 | 无企业买家 |
| 50 | 漏洞披露流程 | 不适用 | 同上 |
| 51 | 笔记本被盗预案 | 不适用 | 本地无凭据/无生产访问；磁盘加密属用户系统策略 |
| 52 | SOC 2 | 不适用 | 同 49 |
| 53 | HIPAA | 不适用 | 无患者数据 |
| 54 | BAA | 不适用 | 同上 |
| 55 | 谁查看过的审计 | 部分适用 | 变更审计完整（不可变操作/快照/receipt）；本地单用户无"查看"审计需求→主体不适用 |
| 56 | PCI/卡号 | 不适用 | 无支付 |
| 57 | GDPR 删除触达每表 | 不适用 | 无云个人数据 |
| 58 | 数据驻留 | 不适用 | 本地优先 |
| 59 | 季度访问审查 | 不适用 | 单用户 |
| 60 | dev/staging/prod 一致 | 不适用（部署语义）；源-包一致性已验 | package094 source1344/build5/App912 收据+哈希 |
| 61 | IaC | 不适用 | 无基础设施 |
| 62 | 部署管线先跑测试 | 部分适用 | CI 门禁在册（AGENTS）；本候选未 push/CI，本地同版完整 check 一次自然 0（O029） |
| 63 | 一键回滚 | 不适用 | 无部署 |
| 64 | 零停机部署 | 不适用 | 同上 |
| 65 | 特性开关 | 不适用 | registry 能力注册即开关面；无运行时 flag 需求 |
| 66 | 自动扩缩 | 不适用 | 同 61 |
| 67 | CDN | 不适用 | 同上 |
| 68 | DNS/SSL 续期 | 不适用 | 同上 |
| 69 | 后台任务队列不冻结页面 | 适用·达标（已测面） | Job 队列/恢复/57 事务；三故障注入（reload/renderer-recovery/coordinator-exit）真实恢复证据 |
| 70 | 带退避重试 | 部分适用 | retryable 标志+ENGINE_EXITED 可重试语义；退避策略未断言 |
| 71 | 死信队列 | 适用（等价物）·达标 | 失败 Job 终态保留可查、不与成功混排 |
| 72 | cron 不双跑 | 不适用 | 无多服务器 |
| 73 | 缓存与失效 | 适用·达标（架构面） | invalidation-v2.json 唯一来源、仅模型配置不使领域结果过期（AGENTS 不变量；本轮未重跑失效用例） |
| 74–75 | SPF/DKIM/DMARC、退信处理 | 不适用 | 无邮件 |
| 76 | 存储清理规则 | 不适用 | 本地文件由用户主权 |
| 77 | 成本告警 | 不适用 | 无云成本；模型网关未接线 |
| 78–79 | DR 计划、第二区域 | 不适用 | 本地优先 |
| 80 | 3am 可搜结构化日志 | 部分适用 | trace.zip/report JSON 结构化逐例；本地检索工具未建设 |
| 81–85 | 错误聚合/uptime/告警/仪表盘/跨服务追踪 | 不适用（运营面）；Job 级 trace 存在 | — |
| 86–87 | on-call/runbook | 不适用 | — |
| 88 | postmortem 改变什么 | 适用·达标（项目实践） | 失败链 006→012、每轮 RED 与处置单留痕（含本 D8 单） |
| 89 | 状态页 | 不适用 | — |
| 90 | 懂逻辑者写的单测 | 适用·达标 | Py 3719 pass/50 skip、TS 39 文件 1892 pass；新 48 测试函数断言语义/物理哈希/wire trace，非仅数量 |
| 91 | 第三方 API 集成测试 | 不适用 | 无第三方 API；唯一依赖已 vendored 并带 172+158 回归 |
| 92 | 赚钱流程 e2e | 不适用（无金钱流）；CRUD e2e 等价达标 | full6 6/6 |
| 93 | 上线前负载测试 | 部分适用·无法确认（性能） | 预算/容量受控测试在；性能负载未测（Q5/D2 无通过线） |
| 94 | 类生产非生产测试数据 | 适用·达标 | 固定 fixture/definition-only/G-base 式基线，无生产数据入库 |
| 95 | 修 bug41 不复活 bug12 | 适用·达标 | binding-regressions、R03 拒绝向量回归、旧 PASS 不迁移 |
| 96 | 五年前笔记本 | 无法确认 | 参考设备 HOLD |
| 97 | 可访问性合规 | 部分达标·无法确认（全面性） | 新视图 aria-label/role=alert/status；全流程键盘+读屏未验证 |
| 98–105 | 订阅/催付/发票 PO/税/退款/计量/年约/营收报表 | 不适用 | 无计费 |
| 106–107 | webhook 验签/重试日志 | 不适用 | 无 webhook |
| 108 | 版本化 API | 适用·达标 | protocolVersion 2/3、契约 $id/registry 版本化、旧版本并行校验 |
| 109 | 用户可建可撤 API key | 不适用 | 无公开 API |
| 110 | API 限速 | 不适用（等价物：帧/页/预算/队列限制在场） | — |
| 111 | 三方 API 变格式预案 | 不适用 | 唯一依赖已 vendored 固定（优于预案） |
| 112 | OAuth 刷新 | 不适用 | — |
| 113 | 客户集成沙箱 | 不适用 | — |
| 114–115 | 提示注入/客户数据出网 | 不适用（现阶段；S3 未接线） | 架构已定：Agent 白名单+人工确认+网关唯一在主进程 |
| 116 | 模型花费上限 | 不适用（未接线） | — |
| 117–120 | evals/降级/弃用预案/提示日志 | 不适用（现阶段） | — |
| 121 | AI 不可撤销动作须人工批准 | 适用·达标（架构） | Agent 只产草稿、不得自动确认自己的修改（AGENTS 不变量+预览/确认流） |
| 122 | 酒店 wifi 也能加载 | 不适用 | 本地应用 |
| 123 | 空/加载/错误态 | 适用·达标 | reading/unavailable/ready 三态、role=status/alert（本轮新视图实读） |
| 124 | 可行动错误信息 | 适用·达标 | OWNERSHIP_CONFLICT 中文行动提示+定位视图；固定码不打印异常 |
| 125 | 表单校验失败保留输入 | 适用·达标 | "已输入内容保留"、错误不清空表单（OntologyMainlinePage 实读） |
| 126 | 邮件客户端渲染 | 不适用 | — |
| 127 | 可关通知 | 不适用 | 无通知系统 |
| 128 | undo | 适用·达标（引擎面）；GUI Undo 面 HOLD 保留 | undo-impact 预览/暂停语义+测试；仅 reservedIdentity family 有本轮 GUI |
| 129 | 键盘导航+读屏 | 部分达标·无法确认 | 同 97 |
| 130 | 翻译/本地化格式 | 不适用 | 中文单语产品；无日期数字本地化面 |
| 131 | 后退按钮符合预期 | 不适用 | 桌面工作台；窗口恢复属 I02 |
| 132 | 人能读的代码 | 适用·达标 | 本轮实读 9349 行核心：命名/注释/结构清晰，意图注释到位 |
| 133 | 每次变更 code review | 适用·达标 | 同版双指定模型审查制度在执行（本轮即 R04 之一） |
| 134 | 分支策略 | 适用·达标 | worktree+feature 分支+base SHA+PR 回并（AGENTS §5，本 worktree 实证） |
| 135 | 月度依赖升级 | 无法确认 | 未建立月度节奏；rdflib 刚 vendored 固定 |
| 136 | 框架 EOL 前升级 | 无法确认 | Electron/React 升级策略未见文档化 |
| 137 | 删除 AI 留下的死代码 | 适用·达标 | 本轮 diff 无死代码/调试残留（grep console/TODO/debugger 仅测试证据字符串）；fr201.1/2 历史 wheel 为审计证据保留，非死代码 |
| 138 | 拆分 2000 行文件 | 适用·未达标（信息级） | 问题 7：job_store.py 2993 行持续增长 |
| 139 | 写下架构决定及理由 | 适用·达标 | ADR-0001/0002、M0 计划、迭代/评审文档体系 |
| 140 | README 一小时上手 | 无法确认 | 未做新人上手实验 |
| 141 | 交接文档 | 适用·达标 | docs 树+每轮留痕+状态唯一来源 m0-checklist/status.md |
| 142 | 运维 admin 面板 | 不适用 | — |
| 143 | 客服支持工具 | 不适用 | — |
| 144 | 客户可读 changelog | 不适用 | 无外部客户 |
| 145 | 条款/隐私与代码一致 | 不适用（未发布）；本地优先行为与 PRD 一致 | — |
| 146 | 账户/域名/仓库归公司 | 不适用 | 个人项目现阶段 |
| 147 | bus factor > 1 | 部分适用 | 双模型评审+总控留痕降低单点；创始人单人边界如实记录 |
| 148–160（尾部"仍需要懂行的人"清单：senior 读每行/数据建模/解释 AI 修复副作用/DevOps/3am 值班/漏洞补丁/审计陪同/QA/在线库迁移/tech lead 拒绝功能/architect 规模化/debug/一年后记得为什么） | 不适用（现阶段组织形态）；作为长期风险记录 | 当前以流程（门禁/双审/失败留痕/文档）部分替代；不虚称已满足 |

---

## 10. 最终结论与范围

**结论：通过（Pass，附条件）**——针对本轮授权范围：FR-200/FR-201 真实表单事实 CRUD、事实原 ID、多值并存、词法受控拒绝、ownership 可见定位，及其引擎/契约/主进程/渲染/测试/供应链闭包，在候选 `cb8c9b7a`（tree `b8010eea`）、package094 同包运行证据基础上。

**条件（全部非阻断，须在后续迭代/接线前处理）**：问题 1–5（witness 行序、跨层字符串上限、definitions.triples wire 面、ownership 码映射与通用定位、错误码白名单）按 D8 处置表分工延期；问题 6（`de-CH-1901` 字面拼写语义）需用户确认；问题 7 为维护性建议。§7 无法确认项与独立 HOLD 不因本 Pass 解除。

**不外推**：本 Pass 不覆盖 Undo GUI、旧超限/损坏库恢复、容量通过线、签名/公证/跨平台/参考设备，不构成发布通过；mergedUsableFRs 仍 2/17；push→PR→CI→merge→remote 仍须双指定模型同版双 Pass 与 ROOT 核验后进行。

**对 D8 选择 A 必要验证范围的对照确认**（本人逐项）：非法语言标签 new（named24 拒绝族）✔；真实已提交原 ID 的 edit（`actualOriginalIDsUsedForEdits`）✔；合法数字子段对照（canonical 四链）✔；超长裸整数分类（`r03-refused-integer-over-default-digit-bound` + 补丁 IntegerDigitLimitError）✔；拒前后完整 Read/身份不变（43 拒绝 FullRead）✔；同 host 后续合法 preview/全 Diff 确认/Job/marker 成功（98 事务 + followup）✔；原未知 parser/N3/Store/坏快照 HOLD 反例保持（未知 ValueError 路径与 HOLD 语义未动）✔；同版完整 check 自然 0 一次（O029）✔；实际 GUI（full6 6/6）✔；包内原验收（原18=16+2 原条件 skip、三故障、named24、text002 双过）✔；不泛捕/不按文案/不静默 normalize/不放宽 cap（补丁 changeScope 与守卫实读）✔。
