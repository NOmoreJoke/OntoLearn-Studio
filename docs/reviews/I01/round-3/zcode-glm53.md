# I01 Round 3 独立对抗性审查（ZCode / GLM-5.3）

## 结论

**通过。**

本人以独立对抗性审查者身份，基于冻结候选 `e628f5e → 1e3b179` 的完整 diff（91 文件、3 个提交，不沿用 Round 1/2 通过，不以增量视角审查）、冻结 inputs 原文、PRD V0.6 附录 C/D/E/G 与 S1 退出门槛 1–6 完成全量复审。Round 1 与 Round 2 双方历史意见共 **29 项编号**（Round 1：MiniMax F-01～F-11、ZCode R1～R6 共 17 项；Round 2：ZCode N1/N2、MiniMax 按正文编号 M-01/M-02、N-01～N-08 共 12 项，其中 N-08 为确认项）逐项基于本人对代码的阅读与独立运行重新判断：**24 项已关闭，5 项为原报告明确授权且已在 ADR 文档化登记的允许延期（F-07、F-11、R6、N-06、N-07；R4 的 TOCTOU 部分已关闭，其锁错误映射残余与 N-06/N-07 同属 F-11 延期范畴，不单独计数）**，无未关闭的阻断项，无任何延期项触碰 S1 退出门槛。两项 Round 1 阻断与 Round 2 全部中等问题在本候选均保持关闭且经本人反例探针独立复现。本轮新发现 2 项 P3 错误面观察（N-R3-1 非字符串 `kind` 无类型守卫、N-R3-2 `current()` 对非 dict implementation 静默返回 None），均为 F-11 已声明延期范畴的新实例，无数据副作用，不构成阻断。S1 六条退出门槛逐项有可执行证据且本人独立复跑通过；两档真实 RDFLib 测量、实际 app-resource 打包与包内同样例由本人独立复现，与 `evidence/round-3` 归档证据的确定性字段完全一致。

## 1. 评审任务、模型和思考设置的来源记录

- 任务标识：`I01-R3-ZCode-GLM53-20261020-0643`（由开发会话通过 ZCode UI 创建并在派发提示词中声明；本人未独立观测该 UI 操作过程，仅按派发信息登记）。
- 设置来源的区分声明：开发会话声明其已通过 ZCode 原生目录选择器重新核验本仓库精确绝对路径，且新空白任务 UI 实际显示 GLM-5.3 / 最高思考——这是**派发方 UI 声明**，本人无法从会话内独立复核该界面。本人**能独立观测**的信息：本会话系统上下文标识运行模型为 `account:bigmodel-individual-coding-plan/GLM-5.3`；当前工作目录即派发提示词给定的仓库绝对路径，且可对该路径执行 git 只读操作并全部成功；`git branch --show-current` 实测为受审分支。思考档位（最高）无法从会话内验证，仅作来源声明记录。
- 独立性声明：按派发要求未读取另一模型本轮 round-3 报告或结论（`docs/reviews/I01/round-3/minimax-m31flash.md` 已存在于磁盘，本人仅 `ls` 确认文件名，未打开内容）；Round 1/2 双方原始报告与 processing.md 按授权作为历史意见来源读取，但每条关闭判断均基于本人对当前候选代码、测试的阅读与独立运行，不以开发者处理声明或任一轮旧通过为依据，不预设应当通过。

## 2. 项目路径、分支、base/head 与工作区

- 项目绝对路径：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`（实测 cwd 一致）。
- 分支：`feature/I01-storage-invalidation`（`git branch --show-current` 实测）。
- base：`e628f5e7b6c09e10e15644552a6171c4a9a3072e`；head：`1e3b179de1e1f9f7ad4b6556f292ef769c113d18`（`git rev-parse HEAD` 实测等于候选 head）。范围含 3 个提交：`6d8e4b3`（spike 主体）、`3e787fb`（Round 1 修复）、`1e3b179`（Round 2 修复：storage.py +167、test_storage.py +301、ADR/acceptance 更新、evidence/round-3 与 round-2 报告归档），共 91 文件 +9369/−2。
- 工作区状态：相对候选 HEAD 的未提交改动仅为 7 个文档/原型文件（.pen、docs/*.md、source-manifest.json）与 untracked 文档/审查目录；`git diff --name-only HEAD | grep -Ev '^(docs/|design/)'` 无匹配，**实现/测试/配置/依赖/验收与候选 HEAD 无未提交差异**，与"审查期间冻结"声明一致。`preexisting-files.json` 登记的 61 项预存文件本人逐项重算 SHA-256：**61/61 一致，0 缺失、0 不匹配**。本人未修改、未暂存、未覆盖任何仓库文件；本轮仅新增本报告，对抗探针（`/tmp/i01-r3-probe/`）与独立打包测量（`/tmp/i01-r3-verify/`）全部写入 `/tmp`，未触碰归档证据。
- 远端：无 push/PR/merge 痕迹（与本轮门禁顺序一致）。

## 3. 检查范围

- 实现：`packages/engine/src/ontolearn_engine/` 全部变更文件——storage.py（1068 行全文）、invalidation.py、invalidation-v2.json、rdf_snapshot.py、storage_probe.py、entrypoint.py、`__main__.py`（确认无探针依赖）；`git ls-tree HEAD` 确认 invalidation-v1.json 已删除、仅存 v2。
- 测试与基线：test_storage.py（1295 行全文）、storage_baselines.py（G-base/G-map-empty/G-behavior 全量定义与 E.5 原表数值）、test_protocol.py（11 项未改动）。
- 构建与验证：scripts/build-engine.mjs（`--collect-all rdflib`/`--collect-data ontolearn_engine`/双许可证 copy-metadata）、scripts/verify-i01.py、packages/engine/pyproject.toml（rdflib==7.6.0）、uv.lock（rdflib 7.6.0、pyparsing 3.3.3 锁定）、.prettierignore；`.github/` 与 `apps/` 在整个范围内 diff 为空（CI 矩阵与桌面代码未动）。
- 文档与证据：ADR-0002-storage.md（含 Round 3 证据补强节）、acceptance.md（含 Round 3 补强验收）、inputs/ 4 份冻结副本（SHA-256 与 sources.json 逐一相符：b8836fbb…/1b3120bd…/c289a1cd…/77a6c534…）、evidence/round-3 全部 19 个文件、preexisting-files.json、internal-review.md（仅作线索）、status.md（仅作线索）。
- 需求对照：仓库 AGENTS.md；inputs/scope.md I01 冻结行（含"新增真实 RDFLib 依赖即执行对应基础打包和包内样例回归，不等 I05"）；inputs/m0-review-and-update-plan-2026-10-19.md S1 全文（数据责任四分表、三类版本、同事务提交边界、D.2 九行要求、两档合成规模、退出门槛 1–6）；inputs/M0深度审查_采纳评估；PRD V0.6 FR-006/304/604/700–705/804/1000 及附录 C/D（D.1/D.2 逐行）/E（E.1/E.2/E.5 逐值）/G（G.0–G.6）原文逐条比对。
- 历史报告：round-1/zcode-glm53.md、round-1/minimax-m31flash.md、round-1/processing.md、round-2/zcode-glm53.md、round-2/minimax-m31flash.md、round-2/processing.md（全部读取；round-2 MiniMax 摘要"9 项、3 中 6 低"与其正文编号 M-01/M-02+N-01～N-08（含确认项 N-08）不一致，按任务指示以正文全部编号处理，不杜撰 M-03）。

## 4. 验证命令与实际结果（本人独立运行）

| # | 命令/探针 | 实际结果 |
| --- | --- | --- |
| V1 | `git rev-parse HEAD` / `git branch --show-current` / `git diff --stat e628f5e..1e3b179` | 与候选 head、分支、范围完全一致（91 文件，3 提交） |
| V2 | `npm run check` | **通过（EXIT=0）**：eslint 0 警告、prettier、tsc、**vitest 4 项**、electron-vite 构建、ruff/format、**pytest 198 项全部通过（5.79s）＝187 项 S1 存储 + 11 项协议**，与 evidence/round-3/check.txt（198 passed in 5.33s）一致 |
| V3 | `npm run verify:sources` | **通过**：13 个归档源文件核对一致（与归档 verify-sources.txt 一致） |
| V4 | `npm run test:e2e` | **通过**：1 passed（1.9s，与归档 e2e.txt 一致；范围无桌面/桥接改动，此项为既有回归复核而非新能力证据） |
| V5 | `uv run --frozen python scripts/verify-i01.py --packaged "release/.../Resources/engine/ontolearn-engine" --output /tmp/i01-r3-verify` | **通过**：12 条测量（开发+包内 × 1x/10x × 3 次），health ok 且仅声明 `["health"]`，rdflib 7.6.0 (BSD-3-Clause) / pyparsing 3.3.3 (MIT) 许可证字节一致，invalidation-v2.json 确认在包内，引擎目录 25,123,766 字节/154 文件——**与归档 manifest 逐字段一致** |
| V6 | 独立测量 vs 归档 evidence/round-3 交叉核对 | 12 条 JSON 的 `inputSha256`/`querySha256`/`result`/`snapshotId`/`triples`/`rdflib`/`seed`/`expected` **全部逐字段相同**；`shasum` 实测 app-resource 引擎与 build/engine PyInstaller 产物均为 `bbcfdc3c…36ac86`＝manifest 登记值——打包与测量证据完全可复现 |
| V7 | 对抗探针 A/B 组（`/tmp/i01-r3-probe/`，uv 环境） | 见第 5 节与第 6 节各项证据；保留 ID 冲突定位、轮次证据拒作项目输入、非法 provenance 拒绝、既存不合格输入 replayable=false、合法 edited/tombstone 快照可用、首个 kind 无 current 等全部按文档语义复现 |
| V8 | 61 项 preexisting 文件 + 4 份冻结输入 SHA-256 重算 | 61/61、4/4 全部一致 |
| V9 | 静态确认 | invalidation-v1.json 已从 HEAD 删除；`__main__.py` 仅依赖 protocol（探针为 entrypoint 惰性导入）；`.github/`、`apps/` 范围内零改动；round-3 候选清单 90 项与提交内容相符；Round 3 提交自身仅含 storage.py/test_storage.py 实现测试改动 + 文档/证据/报告归档 |

**未验证事项（如实声明证据边界）：**

1. **实际 Windows/Linux CI 实跑**：本机为 macOS arm64。Windows 兼容依据是受保护导入 + 惰性导入的代码修复、仓库自带子进程 `meta_path` 拦截测试（`test_missing_unix_probe_module_cannot_break_health_or_measurement` 2 项在本人 V2 中通过）与 Python 文档（`resource` 仅 Unix）；按 scope 门禁 6 的既定顺序（双审通过 → push → CI 核验），Windows 实跑属推送后动作，acceptance.md 第 69 行已如实标注"此为本机模拟，实际 Windows CI 须在双审通过后推送 PR 再核验，不能冒称已实跑"，与本判断一致。
2. **100× 规模**：计划中按资源余量选做，未执行（两档为 1×/10×）。
3. **干净设备、无系统 Python、断网安装、签名、跨平台产物**：不在本候选声明范围（manifest `scope` 字段明示 no clean-device/install/signing claim；package-dir.txt 明示 skipped macOS code signing）。
4. **完整业务执行器**（CSV 解析/预览 UI、SHACL/RDFS+规则组合、行为触发与资源阶段、E.2 执行器、Q-02 查询流程、Agent 流程 A-03–10、设备 B 项目包导出、FR-705 用户删除运行）：不在 I01 范围；acceptance.md"实际范围/完整业务验收状态"两列表格逐行与实际相符（Q-02/V-01/R-01–06/O-01/行为执行/资源消费/Agent/设备 B 均如实标"未执行/未通过"），未发现存储替身冒称业务通过。
5. **Q5 容量线**：未定；实现与文档均未自设通过线，两档小样本无外推（evidence 条件如实标注 "OS cache uncontrolled"、Warm 为同进程第二次调用、ru_maxrss 为进程生命周期值）。
6. **存储 G-base fixture 的 RDF/RDFS/SHACL 语义验证**：按 ADR Round 3 节与 acceptance G.2 Q-01 行的更正声明，存储 fixture（JSON 定义 + `urn:type` 等描述谓词）只做完整集合存储回归，固定 SELECT 仅作用于 `urn:ontolearn:`/`urn:case:{i}:` 标准 `rdf:type` 合成孪生，两者身份不混用——该边界与实现一致（storage_baselines 谓词集 vs storage_probe 查询谓词），完整语义属 I05。

## 5. 本轮新发现问题（全部非阻断）

严重程度定义沿用前轮：阻断=违反冻结范围/PRD 或破坏数据一致性；P2=应修复；P3=轻微/建议。本轮无阻断、无 P2，共 2 项 P3，均属 F-11 已声明延期范畴（错误面/身份类型一致性）的新实例，事务均无写入副作用。

### N-R3-1（P3｜错误面）`publish`/`current` 对非字符串 `kind` 无类型守卫

- 位置：`packages/engine/src/ontolearn_engine/storage.py:735-744`（publish 的 `kind` 形参无 isinstance 检查）、`storage.py:841-849`（current 同样直接参与查询与 digest）。
- 触发条件：调用方以非字符串（如整数 `42`）作为业务结果定义身份 `kind` 调用 publish。
- 影响：本人探针实测 `kind=42` 被接受并成为 current 指针键（`state=current`），经 canonical JSON 与内容寻址一致，**无数据损坏、无越权**；但与 commit/commit_round 对 operationId/jobId 的非空字符串守卫（R1 修复）不对称，I03 能力契约落地前调用方可能在 TS/Python 边界形成两种词法形态。与 Round 1 R1 同族的残余面。
- 证据：`/tmp/i01-r3-probe/probe_a.py` E 段 `E kind=42: ACCEPTED state=current (observation)`。
- 修复建议：I03 统一身份类型守卫时为 `kind`（及 current 的 implementation 形状）补 `isinstance(str)` 前置检查；或在未来候选一行修复（均需新候选重审）。
- 处理结论：允许随 F-11 延期至 I03，不阻断本次。

### N-R3-2（P3｜错误面）`current()` 对非 dict `implementation` 静默返回 None

- 位置：`storage.py:841-860`；`canonical(implementation)` 对任意可序列化值均成功（如 `None`→`"null"`），查询未命中即返回 None。
- 触发条件：调用方误传 `implementation=None` 等非 dict 值查询当前结果。
- 影响：本人探针实测返回 None 而非 `ValueError("Complete execution provenance required")`——与 publish 的前置形状守卫（N1 修复）不对称；纯读取路径，无写入副作用。误用方得到"无当前结果"而非明确的形状错误，可能掩盖调用 bug。
- 证据：`/tmp/i01-r3-probe/probe_a.py` E 段 `E current impl=None: returns None (no error)`。
- 修复建议：随 N-R3-1 在 I03 统一，或当前结果读取入口复用 publish 的 provenance 形状检查。
- 处理结论：允许随 F-11 延期至 I03，不阻断本次。

### 安全与数据一致性专项检查结果（未发现新问题）

- SQL 注入：生产代码全部 `?` 参数绑定；仅常量 DDL/触发器名与测试侧整数 PRAGMA 使用字面量。本人探针脚本亦全部参数化（一处 f-string 表名常量被安全 Hook 拦截后改写为固定语句，不影响受审代码判断）。
- 事务边界：正式数据、版本、所有权、失效、operation/job 标记、前后快照证据同一 `BEGIN IMMEDIATE`；提交前/中取消异常回滚完整（56 项矩阵 + 真实 SQLITE_FULL 3 模式在本人 V2 通过），`after_commit` 后取消/退出不撤销（marker 与数据双存活）。
- 不可变性：snapshots/commits/runs/rounds/run_terminal/commit_evidence 六表 SQL 触发器防 UPDATE/DELETE；本轮新增的保留 ID/快照形状路径均不触碰历史表。
- 输入校验：`iri()` 拒绝相对/含空白/非法字符 IRI；`term()` 经 Turtle 单三元组解析拒绝指令注入与非规范词法；`_snapshot_state` 逐记录校验定义/JSON/引用/事实/所有权/mappingState 形状（NaN 载荷经 `canonical(allow_nan=False)` 拒绝）。
- 无网络、无凭据、无遥测新增；探针纯本地合成数据；未提交任何数据库/业务数据/密钥。

## 6. Round 3 重点修复的独立核验（对应用户指定复核点）

- **保留事实 ID 冲突可定位且不误拒不同多值**：`_check_slot`（storage.py:476-500）以 `reserved_id = digest([subject, predicate, value])` 对槽内全部非排除行判定。本人探针独立复现：① 墓碑后另一来源提交原语句 → `Conflict` 含 subject/predicate/`other=M1`/`row=001`/原 `id`，事实/向量/revision/marker 全部回滚（A1）；② edits 后另一来源提交原语句同样可定位（A2）；③ 另一来源提交**编辑后的当前值**也被同值分支阻止（A2 后半）；④ manual 无法占用墓碑保留身份（A4）；⑤ 同槽**不同多值**不被误拒，M1/M2 并存（A1 后半）；⑥ 单值槽仅有墓碑时另一来源可提交不同值——墓碑不构成 SP 槽排他锁、`_validate_single_slots` 只统计非空对象，与 acceptance"不把墓碑当成整个 SP 槽的排他锁"一致（探针 B1，判为符合文档语义而非缺陷）。专项测试 `test_reserved_fact_identity_conflict_is_locatable_without_blocking_other_values` 覆盖 ①⑤，本人在 198 项中复跑通过。
- **start_run/publish/history 共用完整项目快照形状检查**：`_project_snapshot`（storage.py:619-644）+ `_snapshot_state`（646-733）校验 project 字符串/跨项目 Conflict/非 bool 非负 revision/合法 family 键与非 bool 非负版本向量/state 三容器/逐定义记录（layer∈LAYERS、唯一、payload JSON 往返 + `canonical` + `_definition` 校验、显式 references 可解析）/逐事实记录（7 键、唯一 id、IRI、owner 为 None 时 source_row/managed_value 必须为 None 且 object 规范、owner 为字符串时 managed_value 必填且 object（若非 None）规范）/**不复算已编辑记录的初始 ID**（代码注释明示"ID stays bound to the original statement"）/逐 mappingState 记录（generatedVersion≥−1、stale 原因四键且 code/dependency/before/after 绑定 owner）。本人探针 C 组以 4 类篡改快照构造既存 legacy run，全部 `replayable=False` 且仍可查看；合法 edited/tombstone 快照 `replayable=True` 且保留 ID 不变。
- **轮次证据不能当正式项目输入；publish 非 dict 实现来源 ValueError**：探针 B 组实测 start_run/publish 对轮次快照均抛 `ValueError("Project state snapshot required")`、runs/results/snapshots 计数不变；跨项目仍 `Conflict`；身份缺失仍 `KeyError`；`implementation∈{None,[],42,"engine"}` 统一 `ValueError`（provenance）且 results 计数为 0。与 ADR/acceptance Round 3 声明一致。
- **G-map-empty 固定两行回归**：`test_g_map_empty_fixed_two_row_prepared_collection_is_exact_and_repeatable` 以 PRD 附录 G 固定 CSV 的 001/泵站A、002/泵站B 构造 prepared mapping，断言恰好两个实体、完整四条类型/名称事实（含 owner=`fixed-csv`、source_row 分别为 001/002）、重复提交事实集合与依赖向量均不变。与 G.1 M-01/M-02 的存储侧预期一致；CSV 解析/预览业务仍未执行（acceptance 如实标注）。
- **文档边界更正**：ADR Round 3 节与 acceptance 已区分存储 JSON/`urn:type` fixture（仅存储回归）与固定 SELECT 的独立 RDF 合成孪生（`urn:case:{i}:` 命名空间、标准 `rdf:type`），两者身份不混用；并明确严格 revision 发布策略下"该 kind 可能暂时没有 current"与"未固定 stale 派生载荷可被回收、条目/原因/依赖/输入保留"两条边界。本人探针 D 组实测：首个 kind 在无关提交后发布 → `historical` 且 `current()=None`；已发布结果在无关 query 定义变更后 `stale=[]` 且保持 `current`（unrelatedOrModelChange 不误失效既有领域结果）——两条边界与文档吻合。

## 7. 历史 29 项意见逐项判断

以下判断均为本人基于当前候选 HEAD 代码阅读与独立运行的结论，不采信 processing.md 声明本身。

### Round 1 MiniMax（F-01～F-11）

| # | 原严重度 | 我的判断 | 独立依据 |
| --- | --- | --- | --- |
| F-01 迟到旧快照覆盖新当前 | 阻断 | **已关闭（保持）** | `publish` 事务内 `can_publish_current` 要求 stale 为空且快照 revision==当前 revision（storage.py:800；invalidation.py:31-35；invalidation-v2.json `currentRequiresLatestProjectRevision: true`）；`test_late_snapshot_without_domain_change_stays_history_and_cannot_displace_current` 在本人 198 项中通过；探针 D 组独立复现 late→historical、current 不回退 |
| F-02 `import resource` 破坏 Windows | 阻断 | **已关闭（代码+本机模拟层面；Windows 实跑按门禁顺序留待 PR CI）** | storage_probe.py:21-24 受保护导入（RSS null、`rssAvailable=false`、method 明示）；entrypoint.py 探针惰性导入、`__main__` 无探针依赖（本人 grep 确认）；子进程 `meta_path` 拦截双模块测试在本人 V2 通过；CI 配置未动、windows-latest 腿保留 |
| F-03 空/未解析依赖永不过期 | 中 | **已关闭（保持）** | publish 拒绝空列表（storage.py:754-755）、逐键 `family()` 与三通道登记校验（756-773）、`facts:asserted` 显式空项目范围；`test_unregistered_or_empty_dependencies_cannot_be_published` 5 参数通过 |
| F-04 定义级 IRI/词法未校验 | 中 | **已关闭（保持）** | `_definition`（415-440）校验 triples 键集/绝对 IRI/规范词法、references 与 singleValuedPredicates 形状；`_validate_references` 全表复验；4 参数测试断言同批 manual 事实回滚 |
| F-05 迁移故障注入单点 | 中 | **已关闭（保持）** | `_transaction(hook)` 贯穿迁移（storage.py:76）；11 注入点 ×（异常/真实子进程退出）+ v0 4 点 × 2 全参数化（test:704-761, 907-941），断言 sqlite_master 完整结构/数据/版本回滚与重开重试 |
| F-06 当前格式开库取写锁 | 中 | **已关闭（保持）** | `version == FORMAT_VERSION` 提前 return（73-74）；锁内重读消 TOCTOU（76-81）；`test_current_format_open_does_not_take_writer_lock` 与并发迁移交错回归通过 |
| F-07 提交后异常拿不到成功返回 | 低 | **允许延期（保持；文档化+轮次幂等已补）** | ADR 明确"异常本身不能证明事务未提交，必须另查 marker 对账"；轮次同标记幂等测试覆盖 after_commit OSError 后重试返回原快照。专用异常类型留 I03/I04——原报告明确允许 |
| F-08 墓碑阻断/恢复未记录 | 低 | **已关闭（保持）** | ADR 明确人工修改与墓碑均为漂移、恢复是显式 `edits` 的新预览确认 ChangeSet；`test_tombstone_restore_and_net_zero_change_do_not_spuriously_invalidate` 覆盖全链路；本人探针 C 组复现墓碑快照合法可用 |
| F-09 单值并集语义/基线字段惰性 | 低 | **已关闭（保持）** | ADR 明确唯一执行格式为 ontology 顶层 `singleValuedPredicates`、作用域全项目并集；G-behavior fixture 已含真实字段（storage_baselines.py:67）；`_validate_single_slots` 拒绝与既有事实冲突的新声明 |
| F-10 实现兼容规则未机器化 | 低 | **已关闭（保持）** | invalidation-v2.json（schemaVersion 2）单列 `implementationCompatibility` 与 `publicationPolicy`（staleReason 均 null）；publish 从 RULES 读取 identityKeys/发布策略；`test_machine_readable_implementation_and_publication_policy` 通过；v1 JSON 已从 HEAD 删除（本人 ls-tree 确认） |
| F-11 错误面不统一/未知删除 no-op | 低 | **允许延期（保持；范畴内实例 M-01/N1/N2 已在 Round 3 关闭）** | ADR Round 2 节完整登记 Conflict/ValueError/KeyError/裸 SQLite 错误现状；重复 pin/finish_run 抛唯一性错误、未知事实删除为可审计 no-op 均如实登记；本轮新发现的 N-R3-1/N-R3-2 是该范畴新实例，随 I03 统一处理 |

### Round 1 ZCode（R1～R6）

| # | 原严重度 | 我的判断 | 独立依据 |
| --- | --- | --- | --- |
| R1 operation/job 类型校验 | P3 | **已关闭（保持）** | commit 强制非空字符串并拒 bool revision（226-229）、round 同守卫（905-908）；`test_operation_and_job_identity_types_are_checked_before_write` 4 类非法值 × 双参数通过 |
| R2 轮次重试/跨运行复用 | P3 | **已关闭（保持）** | commit_round 以全局 `rounds.operation` 查询（919-930）：同内容返回原快照（终态后亦然）、异内容/跨 run 抛 Conflict；四情形回归通过 |
| R3 净零事实过度失效 | P3 | **已关闭（保持）** | 重复墓碑 no-op（285-286）；按提交前后终态/owner 记录/映射定义净变化判定（344-366）；净零与真实变更反例（test:842-877, 957-993）通过 |
| R4 迁移 TOCTOU/锁错误形状 | P3 | **部分修复+允许延期（保持）** | TOCTOU 与当前格式免写锁已修并有并发测试；`snapshot()` 仍持写事务（593-594，N-07 登记项），锁竞争裸 OperationalError 按 F-11 延期 I03——原报告明确允许 |
| R5 映射循环重复查询/解析 | P3 | **已关闭（保持）** | own_ids 与 single_predicates 循环外预取（519-525）；ADR 明确"未测量性能改善，不作承诺" |
| R6 全量快照增长 | P3 | **允许延期（保持）** | ADR Round 2 节登记"正确性优先的 spike 选择，存储随历史增长；压缩/差分留待真实负载与兼容性设计"；Q5 未定，无容量宣称 |

### Round 2 ZCode（N1、N2）

| # | 原严重度 | 我的判断 | 独立依据 |
| --- | --- | --- | --- |
| N1 publish 非 dict implementation 裸 TypeError | P3 | **已关闭（本轮验证）** | publish 前置 dict/键集/非空字符串检查（storage.py:745-751）→ 统一 `ValueError("Complete execution provenance required")`；`test_publish_provenance_shape_has_stable_validation_error` 4 参数通过；本人探针 B 组独立复现 4 类非法值且 results 计数为 0 |
| N2 轮次快照误传 publish 裸 KeyError | P3 | **已关闭（本轮验证）** | 与 start_run/history 共用 `_project_snapshot`：类型误用 ValueError、身份缺失 KeyError、跨项目 Conflict；`test_round_evidence_cannot_become_project_input_or_claim_legacy_replayability` 断言拒绝时 runs/results/snapshots 计数不变；本人探针 B 组独立复现 |

### Round 2 MiniMax（按正文编号 M-01、M-02、N-01～N-08）

| # | 正文原严重度 | 我的判断 | 独立依据 |
| --- | --- | --- | --- |
| M-01 墓碑/edits 后第二来源撞保留 ID 抛裸 IntegrityError | 中 | **已关闭（本轮验证）** | `_check_slot` 保留 ID 判定（488-500）：墓碑/编辑两路径的原语句第二来源均得到含 slot/owner/row/id 的 `Conflict`，事实/向量/revision/marker 全回滚，不同多值不误拒；`test_reserved_fact_identity_conflict_is_locatable_without_blocking_other_values`（tombstone/edited 参数化）通过；本人探针 A 组六情形独立复现，不再出现裸 `IntegrityError` |
| M-02 验收/ADR 表述超出实际实现 | 中 | **已关闭（本轮验证）** | 实现侧补齐项目输入形状检查（`_project_snapshot`/`_snapshot_state`）；文档侧更正：acceptance G.2 Q-01 行区分存储 fixture 与 RDF 合成孪生、ADR 补记 edits 后 ID 与内容摘要解耦及墓碑保留身份、`acceptance.md:77` 限定 replayable 只是必要条件、ADR:56 收紧为依赖键与全部存储形状。本人逐条对照现文档与实测行为，未再发现"已覆盖/已校验"类不成立表述 |
| N-01 轮次快照 publish 裸 KeyError | 低 | **已关闭（同 ZCode N2）** | 同上集中校验；本人探针复现 ValueError |
| N-02 轮次/不完整输入仍 replayable=True | 低 | **已关闭（本轮验证）** | start_run/publish/history 共用形状校验：新输入直接 ValueError；既存不合格运行仍可查看但 `replayable=False`（本人探针 C 组 4 类篡改快照复现）；轮次证据形状不齐同样 False（`test_incomplete_round_state_is_rejected_and_legacy_evidence_not_replayable`）；旧非对象 config/impl 同样 False（`test_legacy_nonobject_run_configuration_is_not_claimed_replayable`） |
| N-03 严格 revision 资格可能没有 current | 低 | **已按建议关闭（文档化语义选择）** | 保守策略为 F-01 修复所必需并已进 invalidation-v2.json `publicationPolicy`；ADR Round 3 节明示"即使某 kind 首次发布……也仅为历史，该 kind 可能暂时没有 current；I03 能力契约必须考虑此选择"；本人探针 D 组实测行为与文档一致（first-kind→historical、无 current；既有 current 不因无关变化失效） |
| N-04 未固定 stale 派生载荷可被回收 | 低 | **已按建议关闭（文档化）** | ADR:41 明确"过期而未固定的派生载荷也可被回收，条目、原因、依赖与输入保留……不能承诺过期载荷无限期直接查看"；acceptance Round 3 节重申；与 S1"可安全重建的载荷可回收"一致 |
| N-05 G-map-empty 两行集合未入测试 | 低 | **已关闭（本轮验证）** | 新增 `test_g_map_empty_fixed_two_row_prepared_collection_is_exact_and_repeatable`：恰好两实体、四条类型/名称事实、owner/source_row、重复提交集合与向量不变；CSV 业务仍如实未执行 |
| N-06 重复 finish_run 裸 IntegrityError | 低 | **允许延期（原报告明确允许至 I03/I04）** | 一次性终态不可改写语义保持（`test_schema_cannot_overwrite_history...` 断言 IntegrityError）；ADR Round 2 节已登记；不向 UI/模型转发原始异常由 I03 落地 |
| N-07 snapshot() 写锁竞争裸 OperationalError | 低 | **允许延期（原报告明确允许至 I03/I04）** | 代码确认 snapshot() 仍经 `_transaction`（写事务持久化内容寻址证据，processing 说明不能以读事务掩盖写入）；开库读路径已免写锁并有测试；锁错误统一映射随 R4/F-11 留 I03 |
| N-08 pin/current/历史缓存安全确认项 | 低（确认项） | **维持确认，无需改动** | 报告本身判定断言成立；本轮复验：pinned 载荷保留、六历史表触发器防改写、collect_cache 仅清未 pin 非当前载荷（本人 V2 相关测试 + 探针通过），无回归 |

**汇总：29 项中 24 项已关闭（R4 按 TOCTOU 部分计为关闭，其锁错误映射残余与 N-06/N-07 同属 F-11 延期范畴，不单独计数）；F-07、F-11、R6、N-06、N-07 共 5 项为原报告明确授权的延期且均在 ADR 中如实登记，不触碰任何 S1 退出门槛（门槛 6 的"重放输入缺失如实标识"已由 N-02 修复独立满足）。无未关闭阻断。**

## 8. 关键验收项独立核验记录

- **同事务提交标记**：commits/commit_evidence（operation/job/fingerprint/plan/前后快照）与正式数据、版本、所有权、失效同一 `BEGIN IMMEDIATE`；after_commit 点取消/退出后 marker 与数据双存活（56 项矩阵在本人 check 中通过）；同 operation 同 plan/job 重试返回原标记、异 plan/job 拒绝。
- **故障矩阵与真实磁盘失败**：2 模式 × 7 提交点 × cancel/exception/disk/exit（exit 为真实独立进程 `os._exit(73)`）；另 `max_page_count` 真实触发 SQLITE_FULL 的 mapping/ChangeSet/round 3 模式。恢复只见最后已提交状态。
- **九行正反例与唯一机器码表**：`invalidation-v2.json` 九行与 PRD D.2（第 983–1012 行）逐行对照一致；第 9 行 model `staleReason: null`，`reasons()` 对 falsy code 恒不产生原因（invalidation.py:23-27）——model 不得生成领域 staleReason；正反例参数化测试对每行覆盖"订阅实际依赖过期（含 before/after 版本断言）/不相关不过期/同版本不过期"；实现兼容与发布策略单列且不新增领域原因。
- **E.5 与 G 基线诚实性**：`storage_baselines.E5` 与 PRD E.5 原表（第 1084–1092 行）逐轮逐值一致（产能 3：积压 W004/W007–W008/W010–W012/W013–W016，累计 3/6/9/12；产能 4 全清，累计 4/8/12/16；两产能各两次重放一致）；G-base/G-map-empty/G-behavior 定义与 PRD G.0 逐项对齐（4 类、6 属性、3 设备、3 告警、SHACL 约束、R-risk、B-risk、空初始事件；G-behavior 全部测试对象/工单/行为/产能 0 一轮参数）；测试比较完整定义与事实集合而非计数；acceptance 两列表格逐行与实际相符。
- **两档合成负载**：`urn:case:{i}:` 按档独立命名空间与对象 ID（1x/10x `inputSha256` 不同、`triples` 18/180 恒等式、固定 SELECT 完整结果集断言）；六阶段（load/build/select + Warm）耗时 tracemalloc 当前/峰值 + 进程 ru_maxrss 原始值；种子为固定元数据、生成器无随机分支；条件与方法如实标注。12 条测量与归档证据确定性字段完全一致（V6）。
- **实际打包与包内同样例**："不等 I05"条款兑现：app-resource 引擎哈希、目录字节数、文件数、uvLockSha256 与 manifest 一致；包内 health 仅 `["health"]`；包内 invalidation-v2.json 与 rdflib/pyparsing 许可证字节一致（V5 独立复现）。
- **文档与实现一致性**：ADR-0002/acceptance 的 Round 3 补强声明（保留 ID 定位、共用形状校验、G-map-empty 回归、fixture/孪生区分、无 current 边界、可回收边界）与本人对代码、测试、探针的全部观察吻合；未发现冒称、缩减或以存储替身冒充业务基线。

## 9. 对比历史轮通过意见的适用性

Round 1/Round 2 任一方或双方的历史通过意见按门禁不沿用；本轮以同一 base→新 head 全量重审，全部判断基于当前候选代码与本人本轮独立运行重新作出。Round 2 之后开发者主动选择不沿用双通过而先行关闭 M-01/N-02 再重审，本轮独立确认该决定对应的实现与文档变化确实落地，且未引入新的阻断级回归（本人以探针在历史反例路径及新边界上未复现任何等价缺陷）。

## 10. 最终结论

**通过。**

- 历史全部 29 项编号意见全部有处置结论：24 项已关闭（含两项 Round 1 阻断 F-01/F-02 与 Round 2 全部中等问题 M-01/M-02/N 系列），5 项为原报告明确授权且 ADR 已登记的允许延期（F-07、F-11、R4 错误映射部分、R6、N-06、N-07），延期均不影响 S1 退出门槛 1–6 的满足。
- S1 六条退出门槛逐项验证通过；验收声明（ADR-0002、acceptance.md）与实现、测试、evidence/round-3 三者互相吻合，未发现冒称、缩减或以存储模拟替代完整 M0 基线的情况。
- 本轮新发现 2 项 P3（N-R3-1 非字符串 kind、N-R3-2 current 非 dict implementation）均为 F-11 延期范畴的错误面观察，无写入副作用，随 I03 统一身份/错误面时处理即可，不构成阻断、无需新候选即可按门禁推进（若开发者选择立即修复则需新候选重审）。
- 证据边界如实：Windows CI 实跑、干净设备/签名/断网、100× 规模、完整业务执行器、Q5 容量线、存储 fixture 的完整 RDF/RDFS/SHACL 语义均未验证也未宣称；本机模拟与实际平台验证、存储回归与业务执行的区分在文档中诚实标注。
- 按 scope.md 统一门禁第 4 条，本通过结论与另一模型的独立结论需由开发会话读回核对后汇总；任何后续实现/测试/配置/依赖/验收变更须新候选并重新双审，本通过不自动延续。

（附：本轮本人执行的独立探针与产物位于 `/tmp/i01-r3-probe/`（probe_a.py/probe_b.py 及日志）与 `/tmp/i01-r3-verify/`（12 条测量 + manifest），均不写入仓库；仓库侧仅新增本报告一个文件。）
