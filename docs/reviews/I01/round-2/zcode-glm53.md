# I01 Round 2 独立对抗性审查（ZCode / GLM-5.3）

## 结论

**通过。**

本人以独立对抗性审查者身份，基于冻结候选 `e628f5e → 3e787fb` 的完整 diff（不沿用 Round 1 增量视角）、冻结 inputs 原文、PRD V0.6 附录 C/D/E/G 及 S1 退出门槛 1–6 完成全量复审，未采信开发者处理声明或另一模型结论。Round 1 双方共 17 条意见（MiniMax F-01～F-11、ZCode R1～R6）逐项独立核验：**14 条已关闭，3 条按原报告授权允许延期（F-07、F-11、R4 之错误映射部分与 R6）**，两项 Round 1 阻断（F-01 迟到快照覆盖、F-02 Windows `resource` 导入）均有代码修复、专项回归测试与本人独立反例复现。S1 六条退出门槛逐项有可执行证据且本人独立复跑通过；两档真实 RDFLib 测量、PyInstaller 基础打包与包内同样例回归均独立重建且与归档证据逐字节一致。本轮新发现 2 项低严重度观察（N1、N2），均属 F-11 已声明延期范畴的错误面实例，不构成阻断。

## 1. 评审任务、模型和思考设置的来源记录

- 任务标识：`I01-R2-ZCode-GLM53-20261020-0548`（由开发会话通过 ZCode UI 创建并在派发提示词中声明；本人未独立观测该 UI 操作过程，仅按派发信息登记）。
- 设置来源的区分声明：开发会话声明其已通过 ZCode 原生目录选择器重新绑定本仓库精确路径，且新空白任务界面实际显示 GLM-5.3 / 最高思考——这是 **UI 核验声明**，本人无法从会话内独立复核该界面。本人**能独立观测**的信息：本会话系统上下文标识运行模型为 `account:bigmodel-individual-coding-plan/GLM-5.3`；当前工作目录即派发提示词给定的仓库绝对路径，且可对该路径执行 git 只读操作并全部成功；`git branch --show-current` 实测为受审分支。思考档位（最高）无法从会话内验证，仅作来源声明记录。
- 独立性声明：按派发要求未读取另一模型本轮 round-2 报告或结论（本报告完成时该文件对本人不可见/未查阅）；Round 1 双方报告与 processing.md 按授权作为历史意见来源读取，但每条关闭判断均基于本人对代码、测试的阅读与独立运行，不以开发者处理声明为依据。

## 2. 项目路径、分支、base/head 与工作区

- 项目绝对路径：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`（实测 cwd 一致）。
- 分支：`feature/I01-storage-invalidation`（`git branch --show-current` 实测）。
- base：`e628f5e7b6c09e10e15644552a6171c4a9a3072e`；head：`3e787fb7f8923a0848c173215af2747861e4b35a`。两 SHA 均可解析；`git rev-parse HEAD` 实测等于候选 head。
- 固定 diff 共 67 个文件（+6961/−2）：实现 4 个源文件（storage.py 935 行、invalidation.py、invalidation-v2.json、rdf_snapshot.py）+ storage_probe.py + entrypoint.py；测试 993 行 test_storage.py + storage_baselines.py；scripts/build-engine.mjs、scripts/verify-i01.py、uv.lock（rdflib==7.6.0、pyparsing==3.3.3 锁定）；I01 文档与两轮 evidence。
- 工作区状态：相对候选 HEAD 的未提交改动仅为 7 个文档/原型文件（.pen、docs/*.md、source-manifest.json）与 untracked 文档目录，`git diff --name-only HEAD` 实测**不含任何实现、测试、配置、依赖或验收文件**，与"审查期间冻结"声明一致。`preexisting-files.json` 登记的 61 项预存文件本人逐项重算 SHA-256：**61/61 一致，0 缺失、0 不匹配**。本人未修改、未暂存、未覆盖任何仓库文件；本轮仅新增本报告，对抗探针与独立打包/测量产物全部写入 `/tmp/i01-r2-probe`、`/tmp/i01-r2-verify` 与既有 gitignored `build/`。

## 3. 检查范围、验证命令与实际结果

### 3.1 需求依据（逐条读取原文，不依赖开发者摘要）

仓库 `AGENTS.md`；`docs/iterations/I01/inputs/scope.md`（I01 冻结范围全文，含"新增真实 RDFLib 依赖即执行对应基础打包和包内样例回归，不等 I05"条款）；`inputs/m0-review-and-update-plan-2026-10-19.md` S1 全文（数据责任四分表、三类版本、提交边界、D.2 九行要求、两档合成规模、退出门槛 1–6）；`inputs/M0深度审查_采纳评估_2026-10-19.md`；PRD V0.6 FR-006/304/604/700–705/804/1000 及附录 C/D/E/G 关键段（D.1/D.2、E.1/E.2/E.5、G 基线声明）逐条比对；`ADR-0002-storage.md`、`acceptance.md`（作为被审对象，不作为通过依据）。冻结输入 4 份副本哈希与 `inputs/sources.json` 登记一致（Round 1 已核对的 b8836fbb/c289a1cd 等值本轮经 `npm run verify:sources` 间接复核，13 个归档源文件全部通过）。

### 3.2 实现检查范围

`packages/engine/src/ontolearn_engine/`：storage.py（935 行全文）、invalidation.py、invalidation-v2.json、rdf_snapshot.py、storage_probe.py、entrypoint.py、`__main__.py`（确认无探针依赖）；`packages/engine/tests/`：test_storage.py（993 行全文）、storage_baselines.py（G 三基线与 E.5 全量数值）；`scripts/build-engine.mjs`、`scripts/verify-i01.py`、`packages/engine/pyproject.toml`、`uv.lock`、`.prettierignore`、`.github/workflows/ci.yml`（diff 为空，确认未动 CI 配置、windows-latest 矩阵腿仍在）；evidence/round-2 全部 18 个文件；preexisting-files.json。

### 3.3 验证命令与实际结果（本人独立运行）

| # | 命令/探针 | 实际结果 |
|---|---|---|
| V1 | `git rev-parse HEAD` / `git branch --show-current` / `git rev-parse` 两 SHA | 与候选 head、分支完全一致 |
| V2 | `npm run check` | **通过**：eslint 0 警告、prettier、tsc、vitest 4 项、electron-vite 构建、ruff、**pytest 160 项全部通过（5.29s）**，其中 S1 存储 149 项（故障矩阵 56 = 2 模式 × 7 提交点 × 4 失败态、真实 SQLITE_FULL 3 模式、九行正反例 9 项、迁移 11 点 × 2 故障 + v0 新建 4 点 × 2、E.5 双产能两次重放等）+ 既有 protocol 11 项；与 evidence/round-2/check.txt 记录一致 |
| V3 | `npm run verify:sources` | **通过**：13 个归档源文件核对一致 |
| V4 | `npm run engine:build`（PyInstaller onedir，写入既有 ignored `build/engine`） | **成功** |
| V5 | `uv run --frozen python scripts/verify-i01.py --packaged build/engine/... --output /tmp/i01-r2-verify` | **通过**：开发+包内 × 1x/10x × 3 次 = 12 条测量，结果集/三元组断言通过，同 scale 跨 6 条 `snapshotId`/`inputSha256`/`querySha256`/`result` 完全一致；包内 health 仅声明 `["health"]`；`invalidation-v2.json` 确认在包内；rdflib(BSD-3-Clause)/pyparsing(MIT) 许可证文件字节一致；引擎目录 25,120,774 字节 |
| V6 | 独立产物 vs 归档 evidence 交叉核对 | `executableSha256` **逐字节一致**（ddd465de1a1d…），engineDirectoryBytes、fileCount(154)、uvLockSha256 全部一致；12 条 JSON 的确定性字段（inputSha256/querySha256/snapshotId/result/triples/rdflib）两两相同——**打包与测量证据完全可复现** |
| V7 | F-01 变体探针（`/tmp/i01-r2-probe/probe_late.py`） | 依赖未变+旧快照迟到 → `historical`、stale 空、current 保持 rev2 结果；依赖已变迟到 → `stale=['FACTS_CHANGED']`、current 保持 rev3；同 revision 发布 → `current`；空依赖拒绝——**迟到覆盖反例不复现** |
| V8 | F-02 探针（同进程 meta_path 拦截，无 subprocess） | 拦截 `resource`：measure 正常、`rssAvailable=False`、全部 RSS null、method 明示 "RSS unavailable"、查询结果完整；拦截整个 `storage_probe` 模块：`__main__`（health 路径）仍可导入——**Windows 导入链修复成立** |
| V9 | 类型/幂等/锁探针 | operation/job 四类非法值（int/bool/None/""）全拒；bool revision 拒绝；同 operation 异 job → `Conflict: operationId reused`、原 marker 保留；v2 库在写者持 `BEGIN IMMEDIATE` 期间新 reader **0.00s** 打开读取 |
| V10 | 真实并发迁移探针（4 线程同时打开 v1 库，无人工 hook） | 4/4 全部成功打开，最终 user_version=2、mapping_state/commit_evidence 齐全——**锁内重读消除 TOCTOU** |
| V11 | 61 项 preexisting 文件 SHA-256 重算 | 61/61 一致，0 缺失、0 不匹配 |
| V12 | evidence/round-2 12 条 JSON 抽查 | 18/180 三元组、六阶段（load/build/select + Warm）耗时/内存字段齐全、`condition` 如实标注 "OS cache uncontrolled"、rdflib 7.6.0、RSS 可用标记 true（本机） |

### 3.4 未验证事项（如实声明证据边界）

1. **实际 Windows/Linux CI 实跑**：本机为 macOS arm64。F-02 的关闭依据是代码修复 + 同进程导入链模拟（本人独立复现）+ 官方测试 `test_missing_unix_probe_module_cannot_break_health_or_measurement`（子进程 meta_path 拦截两种模块并执行 health）+ Python 文档（`resource` 仅 Unix）。CI 配置未改动、windows-latest 腿仍在；按 scope 门禁 6 的既定顺序（双审通过 → push → CI 核验），Windows 实跑属推送后动作，acceptance.md 第 69 行已如实标注"此为本机模拟，实际 Windows CI 须在双审通过后推送 PR 再核验，不能冒称已实跑"，与本判断一致。
2. **100× 规模**：计划中标为按资源余量选做，未执行（与 Round 1 相同边界）。
3. **干净设备、无系统 Python、断网安装、签名、跨平台产物**：明确不在本候选声明范围（manifest scope 字段与 ADR 声明一致，package-dir.txt 明示 skipped macOS code signing）。
4. **完整业务执行器**（CSV 导入/预览 UI、SHACL/RDFS+规则、行为触发、E.2 沙盘执行、Q-02 查询流程、Agent 流程 A-03–10、设备 B 项目包导出）：不在 I01 范围；acceptance.md 的"实际范围/完整业务验收状态"两列表格逐行核对与测试实际情况相符，**未发现存储替身冒称业务通过**。
5. **Q5 容量**：未定；实现与文档均未自设通过线，两档小样本无外推。
6. **`npm run test:e2e`**：候选 diff 不含桌面/桥接改动（apps/ 未触碰），AGENTS 触发条件不满足；归档 e2e.txt（1 passed）仅作既有回归记录，本人未重跑。

## 4. 本轮新发现问题（全部非阻断）

严重程度定义沿用 Round 1：阻断=违反冻结范围/PRD 或破坏数据一致性；P2=应修复；P3=轻微/建议。本轮无阻断、无 P2，共 2 项 P3。

### N1（P3｜错误面）`publish` 对非 dict `implementation` 抛裸 `TypeError`，与 `start_run` 的形状守卫不对称

- 位置：`packages/engine/src/ontolearn_engine/storage.py:624-628`（`set(implementation)` 在成员检查前未先验证 dict 类型）。
- 触发条件：`publish(..., implementation=None)` 或其他非可迭代/无 `.values()` 的值。
- 影响：实测抛 `TypeError: 'NoneType' object is not iterable`，而非声明的 `ValueError("Complete execution provenance required")`；对比 `start_run`（storage.py:763-764）先做 `isinstance(..., dict)` 检查返回 ValueError，两个入口形状守卫不对称。异常发生在事务开始之前，**无任何写入副作用**，纯错误面一致性问题，属 F-11 已声明延期范畴（"SQLite I/O/锁/唯一性错误可原样抛出…I03/I04 统一转换为受限结构化错误"）在本轮新增代码中的实例化。
- 证据：`/tmp/i01-r2-probe/probe_edges.py` 首段实测 traceback。
- 建议：I03 统一错误面时为 publish 补 `isinstance(implementation, dict)` 前置检查；或立即一行修复（均需新候选）。
- 处理结论：允许随 F-11 延期至 I03，不阻断本次。

### N2（P3｜错误面）轮次快照 id 误用于 `publish` 时抛裸 `KeyError('dependencyVector')`

- 位置：`storage.py:630`（`snap["projectRevision"]` 等键访问）；轮次快照 payload（storage.py:791-796）不含 `dependencyVector`/`projectRevision` 字段。
- 触发条件：调用方将 `commit_round` 返回的快照 id 传给 `publish` 的 `snapshot` 参数（API 误用）。
- 影响：实测抛 `KeyError: 'dependencyVector'`——ADR Round 2 澄清（第 57 行）将 KeyError 语义描述为"读取身份缺失"，此处实为输入形状不符，语义描述与行为不完全吻合。同样发生在结果写入之前，无数据副作用；属 F-11 延期范畴。
- 证据：`/tmp/i01-r2-probe/probe_edges.py` 实测 `round snapshot in publish -> KeyError 'dependencyVector'`。
- 建议：I03 统一错误面时区分"快照类型不适用"与"身份缺失"；或在 ADR 错误面一节补一句该误用路径的现状。
- 处理结论：允许随 F-11 延期，不阻断本次。

### 安全与数据一致性专项检查结果（未发现新问题）

- SQL 注入：生产代码全部 `?` 参数绑定；仅常量 DDL/触发器名与测试侧整数 PRAGMA 使用字面量（本人对抗探针全程参数化亦通过 Mimosa 前置约束）。
- 事务边界：正式数据、版本、所有权、失效、operation/job 标记、前后快照证据同一 `BEGIN IMMEDIATE` 事务；提交前/中取消异常回滚完整（56 项矩阵 + 真实 SQLITE_FULL 3 模式），提交后取消/退出不撤销（after_commit 分支断言 marker 与数据双存活）。
- 不可变性：snapshots/commits/runs/rounds/run_terminal/commit_evidence 均有 SQL 触发器防 UPDATE/DELETE；本人 Round 1 与本轮 check 中的触发器拒绝测试均通过。
- 依赖登记：空依赖、未知 family、非字符串键、未登记身份全部拒绝（V7/V9 独立复现）；`facts:asserted` 是空项目显式范围；ADR 明示登记校验不证明无漏报、完整依赖集合由 I03 能力契约强制——边界诚实。
- 无网络、无凭据、无遥测新增；探针纯本地合成数据；未提交任何数据库/业务数据/密钥。

## 5. 历史 17 条意见逐项判断

以下判断均为本人基于代码阅读与独立运行的结论，不采信 processing.md 的声明本身。

### MiniMax Round 1（F-01～F-11）

| # | 原严重度 | 我的判断 | 独立依据 |
|---|---|---|---|
| F-01 迟到旧快照覆盖新当前 | 阻断 | **已关闭** | `publish` 事务内复验依赖且 `can_publish_current` 要求 `snapshot_revision == project_revision`（storage.py:679；invalidation.py:31-35；invalidation-v2.json `currentRequiresLatestProjectRevision: true`）；专项测试 `test_late_snapshot_without_domain_change_stays_history_and_cannot_displace_current` 恰覆盖原反例的"依赖未变+旧快照迟到"组合。本人 V7 探针独立复现：late→historical、stale 空、current 不回退；依赖已变迟到→stale 且指针不动。acceptance.md 对"旧快照及旧实现迟到发布被隔离"的表述已由 Round 2 补强条款（第 64 行）与实现一致 |
| F-02 `import resource` 破坏 Windows | 阻断 | **已关闭（代码+本机模拟层面；Windows 实跑按门禁顺序留待 PR CI）** | storage_probe.py:21-24 受保护导入，`high_water_rss()` 返回 None、`method`/`rssAvailable` 明示；entrypoint.py 探针改惰性导入（`--storage-probe` 分支内），`__main__` 不引用探针（本人 grep 确认）；测试覆盖两种模块阻断 + health 可用。本人 V8 同进程独立复现两种阻断均正常。CI 配置未动，windows-latest 腿保留——修复使其可收集可运行，实跑属推送后核验（acceptance.md:69 如实声明，非冒称） |
| F-03 空/未解析依赖永不过期 | 中 | **已关闭** | publish 拒绝空列表（storage.py:633-634）；逐键 `family()` 校验（非字符串/未知类别抛 ValueError）+ 三通道登记校验（definitions/mappingState/dependencyVector，storage.py:635-652）；`facts:asserted` 显式豁免为空项目范围；5 参数化测试 `test_unregistered_or_empty_dependencies_cannot_be_published`；本人 V7 独立验证空依赖、`facts:missing-scope` 均拒绝。"漏报依赖"残余风险由 ADR 明示移交 I03 能力契约，属声明的范围边界而非缺口 |
| F-04 定义级 IRI/词法未在提交时校验 | 中 | **已关闭** | `_definition`（storage.py:409-435）校验 triples 完整键集/绝对 IRI/规范 RDF 词法、references 列表形状、singleValuedPredicates 形状；definitions 写入路径逐条调用（storage.py:268）+ `_validate_references` 全表复验含 references 可解析（storage.py:337,456-469），失败整批回滚；测试断言同批 manual 事实一并回滚、marker 不存在、revision 不变。有效定义建图回归在测 |
| F-05 迁移故障注入单点 | 中 | **已关闭** | `_transaction(hook)` 贯穿迁移（storage.py:76）；11 个注入点（v1_created 之外的 v1→v2 全部 DDL/回填/触发器/指针重建/版本更新 + before/before_commit/after_commit，test_storage.py:704-716）× 异常/真实子进程 `os._exit` 全参数化，断言 sqlite_master 完整结构、数据、user_version 回滚与重开重试；v0 新建另 4 点 × 2 故障（test:907-941） |
| F-06 当前格式开库取写锁 | 中 | **已关闭** | `version == FORMAT_VERSION` 提前 return（storage.py:73-74）；需要迁移时锁内重读版本消 TOCTOU（storage.py:75-81）；测试 `test_current_format_open_does_not_take_writer_lock`（写者持锁时 reader 打开读取）与 `test_concurrent_migration_rereads_version_after_lock`；本人 V9/V10 独立复现（0.00s reader；4 线程并发 opener 全成功且最终 v2 完整） |
| F-07 提交后异常拿不到成功返回 | 低 | **允许延期（原报告明确可延期）；已文档化+轮次幂等补强** | ADR Round 2 澄清（第 57 行）明确"异常本身不能证明事务未提交，必须另查 marker 对账，不盲目重试"；轮次路径新增同标记幂等：`test_round_retry_after_ack_loss_is_idempotent_and_cross_run_reuse_is_conflict` 覆盖 after_commit OSError 后同参数重试返回原快照。专用投递失败异常类型留待 I03/I04 按真实 job/传输边界制定——与原报告建议一致 |
| F-08 墓碑阻断/恢复未记录 | 低 | **已关闭（文档+回归）** | ADR 第 29 行明确人工修改与人工删除（墓碑）均为漂移、阻断重跑，恢复路径是新的预览确认 ChangeSet（`edits={factId:managed_value}`），无静默恢复；`test_tombstone_restore_and_net_zero_change_do_not_spuriously_invalidate` 覆盖墓碑→显式恢复→重映射成功全链路（本人代码走读确认 manual 无法接管受管墓碑，storage.py:322-326 owner 非空即 Conflict） |
| F-09 单值并集语义/基线字段惰性 | 低 | **已关闭** | ADR 第 29 行明确唯一执行格式为 ontology 顶层 `singleValuedPredicates` 绝对 IRI 列表、作用域全项目并集、`properties.*.single` 仅为描述字段；storage_baselines.py G-behavior 已增加真实执行字段 `singleValuedPredicates: ["urn:P","urn:workOrderStatus"]`（storage_baselines.py:67）；提交时 `_validate_single_slots` 拒绝与既有事实冲突的新声明（storage.py:447-454，测试 test:483-488） |
| F-10 实现兼容规则未机器化 | 低 | **已关闭** | invalidation-v2.json schemaVersion 2：`implementationCompatibility`（identityKeys 三键/default isolate/reuse disabled_in_S1/futureReusePrerequisites）与 `publicationPolicy`（registeredDependenciesRequired/emptyDependenciesAllowed=false/currentRequiresLatestProjectRevision/lateResult=preserve_as_historical 等）单列，两者 staleReason 均 null，未新增领域过期原因；publish 从 RULES 读取 identityKeys（storage.py:624）与发布策略（invalidation.py:31-35）；`test_machine_readable_implementation_and_publication_policy` 断言契约内容 |
| F-11 错误面不统一/未知删除 no-op | 低 | **允许延期（原报告明确可延期至 S2/I03）** | ADR Round 2 第 57 行完整登记现状（Conflict/ValueError/KeyError/裸 SQLite 错误各自语义、重复 pin/finish_run 抛唯一性错误、未知事实删除为可审计 no-op、终态不可改写）；跨运行 round operation 复用已随 R2 修复改为 Conflict。本人复现重复 pin IntegrityError 与 ADR 声明一致。本轮 N1/N2 是该延期范畴的实例，随 I03 统一时一并处理 |

### ZCode Round 1（R1～R6，本人上轮意见，本轮重新独立核验而非自我沿用）

| # | 原严重度 | 我的判断 | 独立依据 |
|---|---|---|---|
| R1 operation/job 类型校验 | P3 | **已关闭** | commit 强制 `isinstance(str)` 且非空（storage.py:228-229）、`type(base) is not int` 拒 bool（storage.py:226-227）、round 同守卫（storage.py:785-787）；`test_operation_and_job_identity_types_are_checked_before_write` 四类非法值 × 双参数；本人 V9 独立复现全部拒绝且 revision 不变 |
| R2 轮次重试/跨运行复用 | P3 | **已关闭** | commit_round 以全局 `rounds.operation` 查询（storage.py:797-808）：同 run/round/job/内容返回原快照（终态后亦然）、不同内容或跨 run 抛 `Conflict("Round operationId reused...")`，不再依赖裸 IntegrityError；`test_round_retry_after_ack_loss...` 覆盖响应丢失重试/内容不符/跨运行/取消后对账四情形 |
| R3 净零事实过度失效 | P3 | **已关闭** | 重复墓碑删除 no-op（storage.py:286 continue）；版本推进改为按提交前后终态判定——facts 集相等则丢弃 `facts:asserted`（storage.py:339-341）、定义 payload 与 owner 事实净变化判定（storage.py:342-361）；两组测试覆盖重复删除、同批 remove+manual 净零、managed remove+edits 恢复净零、sourceHash 真变仍推进（test:842-863, 957-977） |
| R4 迁移 TOCTOU/锁错误形状 | P3 | **部分修复 + 延期（原报告允许）**：TOCTOU 与写锁已修复，错误映射延期 | 锁内重读版本（storage.py:75-81）+ 当前格式免写锁（storage.py:73-74）+ 两项并发测试；本人 V10 以 4 线程真实并发（无人工 hook）复现全部成功。普通写锁竞争的裸 `OperationalError` 服务层映射按 F-11 同步延期 I03，ADR 已登记 |
| R5 映射循环重复查询/解析 | P3 | **已关闭** | own_ids 与 single_predicates 循环外预取（storage.py:514-520），`_check_slot` 传参复用（storage.py:477-482）；ADR 第 58 行明确"未测量性能改善，不作倍数或时延承诺"，无夸大声明 |
| R6 全量快照增长 | P3 | **允许延期（原报告即建议维持登记）** | ADR 第 59 行保留"正确性优先的 spike 选择，存储随历史增长；压缩/差分快照留待真实负载与兼容性设计后评估，不能清理不可变历史来冒充优化"；Q5 未定，无容量宣称 |

**汇总：17 条中 14 条已关闭；F-07、F-11、R6 三条延期均在原报告授权的延期路径上且不影响任何 S1 退出门槛；R4 的未竟部分（错误映射）与 F-11 同属 I03 范畴。无一条违反"延期须不影响通过"的约束。**

## 6. 关键验收项独立核验记录

- **同事务提交标记**：commits（operation/job/fingerprint/plan）与 commit_evidence（前后快照）同正式数据、版本、所有权、失效一个 `BEGIN IMMEDIATE`；after_commit 点取消/退出后 marker 与数据双存活（本人 check 内 56 项矩阵通过）。operation 幂等：同 plan/job 重试返回原标记、异 plan/job 拒绝（V9 复现）。
- **故障矩阵**：2 模式 × 7 提交点 × cancel/exception/disk/exit 全通过；exit 为真实独立进程 `os._exit(73)`；另 max_page_count 真实触发 SQLITE_FULL 的 mapping/changeset/round 3 模式。恢复只见最后已提交状态。
- **九行正反例**：参数化测试对 D.2 每行"订阅实际依赖过期（含 before/after 版本值断言）/不相关不过期/同版本不过期"；第 9 行 model staleReason 为 null 不生成原因码。invalidation-v2.json 九行与 PRD D.2 原文（983-1012 行）本人逐行对照一致；`reasons()` 对 model 家族 code 为 null 恒不产生原因（invalidation.py:23-27）；实现兼容/发布策略单列不混入 staleReason。
- **迟到结果**：依赖未变+旧快照迟到→historical（不覆盖、stale 空）；依赖已变迟到→stale；旧实现迟到→按 implementation 隔离指针（test:524-531）。已有结果不因模型配置变更被错误失效（test:614-615）。
- **场景/历史**：轮次连续 1–1000、单轮快照+标记原子、取消保留前轮、终态后拒绝新轮次但同标记重试返回原证据、新运行不自动续跑、SQL 触发器防改写、progress 零轮 null。
- **迁移**：11 点 × 异常/真实退出 + v0 4 点 × 2，结构/数据/版本完整回滚、重开可重试、after_commit 保持 v2、备份拒绝覆盖目标并可恢复全部所有权、未来格式拒绝打开、旧格式 mapping_state 写 -1 显示过期。
- **G/E.5 诚实性**：`storage_baselines.E5` 与 PRD E.5 原表（1084-1092 行）逐轮逐值一致（产能 3 积压 W004/W007-008/W010-012/W013-016 累计 3/6/9/12；产能 4 全清累计 4/8/12/16）；测试比较完整定义与事实集合而非计数；两产能各两次重放一致。acceptance.md 两列表格逐行与实际相符：Q-02/V-01/R-01–06/O-01/行为执行/资源消费/Agent 流程/设备 B 导出等全部如实标"未执行/未通过"。
- **测量与打包**：独立重建可执行文件与归档 manifest 哈希逐字节一致；12 条测量确定性字段跨记录一致；探针生成器独立命名空间 `urn:case:{i}:`（无同 ID 冒充扩容）、固定 SELECT 完整结果集断言、种子为常量元数据且生成器无随机分支、冷热与条件方法如实标注；包内样例/health/数据契约/许可证全部通过。"不等 I05"的基础打包条款兑现且可复现。

## 7. 对比 Round 1 通过意见的适用性

本人 Round 1 通过意见按门禁不沿用；本轮以同一 base→新 head 全量重审，上述所有判断均基于新候选代码与本人本轮独立运行重新作出。Round 1 时期本人未发现 F-01/F-02（MiniMax 发现）——本轮本人已将这两个维度的反例探针独立重放并确认修复，作为对本人上轮盲区的补强验证。

## 8. 最终结论

**通过。**

- 两项 Round 1 阻断（F-01、F-02）已关闭且有本人独立反例复现；17 条历史意见全部有处置结论，其中 3 条为原报告授权的合理延期，不影响 S1 退出门槛。
- S1 退出门槛 1–6 逐项验证通过；验收声明（acceptance.md、ADR Round 2 澄清）与实现、测试、证据三者互相吻合，未发现冒称、缩减或以存储替身冒充业务基线的情况。
- 本轮新发现 2 项 P3（N1、N2）均为错误面一致性观察，无数据副作用，属 F-11 延期范畴实例，随 I03 统一处理即可；不构成阻断，无需新候选即可按门禁推进（若开发者选择立即修复则需新候选重审）。
- 证据边界如实：Windows CI 实跑、干净设备/签名/断网、100× 规模、完整业务执行器、Q5 容量线均未验证也未宣称；本机模拟与实际平台验证的区分在文档中诚实标注。
- 按 scope.md 统一门禁第 4 条，本通过结论与另一模型的独立结论需由开发会话读回核对后汇总；任何后续实现/测试/配置/依赖/验收变更须新候选并重新双审，本通过不自动延续。

（附：本轮本人执行的独立探针与产物位于 `/tmp/i01-r2-probe/`（probe_late、probe_no_subprocess、probe_edges、blocked_child）与 `/tmp/i01-r2-verify/`（12 条测量 + manifest），均不写入仓库。）
