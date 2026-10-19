# I01 Round 1 独立对抗性审查（ZCode / GLM-5.3）

## 结论

**通过（无阻断问题；附 6 项非阻断建议 R1–R6，均可延期到后续迭代处理）。**

本人以独立对抗性审查者身份，基于冻结候选 `e628f5e → 6d8e4b3` 的固定 diff、冻结 inputs 与仓库 PRD 原文完成审查，未采信开发者文档或另一模型的结论。S1 退出门槛 1–6 逐项有可执行证据且本人独立复跑通过；未发现需求遗漏、数据一致性破坏、安全或回归阻断问题。6 项非阻断观察（类型校验缺口、轮次重试语义、两条净零改动的过度失效、迁移并发 TOCTOU/锁竞争错误形状、映射校验的 O(n·m) 重复解析、每次提交全量快照增长）均不违反冻结范围或 PRD 条款方向，详见问题清单；每项均已给出处理结论。

## 1. 任务与设置来源记录

- 任务标识：I01-R1-ZCode-GLM53-20261020-0015（由开发会话通过 ZCode UI 创建并声明，本人在任务提示词中收到同样标识）。
- 设置来源的区分声明：开发会话声明其已通过 ZCode UI 原生 Open 目录核验项目路径、选择 GLM-5.3 与最高思考档位——这是**UI 核验声明**，本人无法独立观测该 UI 操作过程。本人**能独立观测**的信息：任务提示词完整给定了项目绝对路径、迭代标识、审查范围 SHA 与报告路径；本会话系统上下文标识模型为 `account:bigmodel-individual-coding-plan/GLM-5.3`；当前工作目录即上述仓库。思考档位（最高）无法从会话内直接验证，仅作为来源声明记录。
- 审查依据：`docs/iterations/I01/inputs/scope.md`（I01 冻结范围）、`inputs/m0-review-and-update-plan-2026-10-19.md`（S1 全文及"新增真实 RDFLib 依赖即执行对应基础打包和包内样例回归，不等 I05"条款）、仓库 `AGENTS.md`、PRD V0.6 FR-006/304/604/700–705/804/1000 及附录 C/D/E/G、`docs/iterations/I01/ADR-0002-storage.md`、`docs/iterations/I01/acceptance.md`。开发者文档（ADR/acceptance/status/internal-review）仅作线索，不作为通过依据；所有通过判断基于本人对代码、测试的阅读与独立运行。
- 独立性声明：同目录 `minimax-m31flash.md` 存在但本人未读取，避免结论污染。

## 2. 受审对象

- 项目路径：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`
- 分支：`feature/I01-storage-invalidation`（`git branch --show-current` 实测）
- base：`e628f5e7b6c09e10e15644552a6171c4a9a3072e`；head：`6d8e4b3021b368661247c03c47f01e4d32ebf6e1`
- `git rev-parse HEAD` 实测等于候选 head；两 SHA 均可解析。固定 diff 共 43 个文件（实现、测试、脚本、I01 文档与 evidence）。
- 工作区另有本轮前已存在的文档/原型修改与 untracked 文件（含 `docs/reviews/I01/round-1/minimax-m31flash.md`），均不属于受审实现，本人未读取、未修改、未暂存；本轮仅新增本报告一个仓库文件，其余产物只写入 `/tmp` 与被 gitignore 的 `build/`。

## 3. 已检查范围

- 实现：`packages/engine/src/ontolearn_engine/storage.py`（770 行全文）、`invalidation.py`、`invalidation-v1.json`、`rdf_snapshot.py`、`storage_probe.py`、`entrypoint.py`、`pyproject.toml`。
- 测试与基线：`tests/test_storage.py`（592 行全文）、`tests/storage_baselines.py`、既有 `test_protocol.py` 未改动（仅确认在 check 中通过）。
- 构建与验证脚本：`scripts/build-engine.mjs`、`scripts/verify-i01.py`、`.prettierignore`、`uv.lock`（rdflib==7.6.0、pyparsing 3.3.3 锁定）。
- 文档与证据：ADR-0002、acceptance.md、inputs/（scope、计划、goal-objective、采纳评估、sources.json）、evidence/ 全部 20 个文件抽查或全文核对、`docs/reviews/I01/internal-review.md`（仅作线索）、已提交版 `status.md`。
- 需求对照：PRD 附录 D.1/D.2 九行原文、E.5 固定模型原表、FR-006/304/604/700–705/804/1000 条款原文逐条比对；`invalidation-v1.json` 九行与 D.2 一一对应（第 9 行 model → null 反例规则正确）。
- 冻结输入完整性：4 份 inputs 副本 SHA-256 与 `sources.json` 记录逐一相符（实测 b8836fbb…、1b3120bd…、c289a1cd…、77a6c534…）。

## 4. 验证命令与实际结果（本人独立运行）

| 命令 | 结果 |
| --- | --- |
| `git rev-parse HEAD` / `git branch --show-current` | 与候选 head、分支一致 |
| `npm run check` | **通过**：eslint 0 警告、prettier 通过、tsc 通过、vitest 4 项通过、构建成功、ruff 通过、pytest **105 项全部通过**（含 94 项 S1：56 项故障矩阵、真实 SQLITE_FULL 3 模式、九行正反例、迁移/备份/未来格式、E.5 两次重放等），3.0s 内完成 |
| `npm run verify:sources` | **通过**：13 个归档源文件核对一致 |
| `npm run engine:build`（PyInstaller onedir，产物在被忽略的 `build/engine`） | **成功**；可执行文件 SHA-256 = `b8e076d10af0d7420bdac7057ce64b2446bb482a09475b1f47dee9917edd0146`，**与提交内 evidence `package-manifest.json` 的 executableSha256 逐字节一致**（独立重建可复现） |
| `uv run python scripts/verify-i01.py --packaged build/engine/ontolearn-engine/ontolearn-engine --output /tmp/i01-verify-round1` | **通过**：开发+包内 × 1x/10x × 3 次 = 12 条测量，结果集与三元组数断言通过，同 scale 跨 6 条记录 `snapshotId`/`inputSha256`/`querySha256`/`result` 完全一致；包内 health 仅声明 `["health"]`；`invalidation-v1.json` 确认在包内；rdflib(BSD-3-Clause)/pyparsing(MIT) 许可证文件字节与开发环境原件一致；引擎目录 25,116,200 字节与 manifest 一致 |
| 对抗性探针（8 个场景，`/tmp/i01_adversarial_probe.py`，uv 环境运行） | 结果见问题清单 R1–R4 证据与第 6 节正向确认 |

**未验证事项（如实声明）：**

- 未运行完整 `npm run package:dir`（electron-builder 应用级打包）。本人验证到 PyInstaller 引擎 onedir 产物，其可执行文件哈希与提交内 app-resource 证据完全一致，应用资源嵌套步骤采信提交的 `package-dir.txt` 与 manifest。此差异不改变"基础打包与包内同样例回归已真实执行"的判断。
- 未运行 `npm run test:e2e`：候选 diff 不含桌面/桥接改动（`apps/` 未触碰），AGENTS 触发条件不满足。
- 100× 规模未运行（计划中标为按资源余量选做）。
- 干净设备、无系统 Python、断网安装、签名与其他平台：明确不在本次声明范围（ADR 与 manifest 的 scope 字段一致）。
- 完整业务用例（G.2 Q-02/V-01/R-01–06/O-01、G.3 行为执行、G.4/E.5 执行器、pySHACL、网络拒绝矩阵）：不在 I01 范围，acceptance.md 已如实标记未执行/未通过，本人确认该标记与实际相符，未发现存储测试冒称业务通过。
- Q5 容量线：未定，实现与文档均未自定通过线，测量仅为原始记录（本人抽查 evidence JSON：18/180 三元组、六阶段耗时/内存字段齐全、条件与方法如实标注"OS cache uncontrolled""process lifetime ru_maxrss"）。

## 5. 问题清单（全部非阻断）

严重程度定义：阻断=违反冻结范围/PRD 或破坏数据一致性且必须修复后方可通过；P2=应修复；P3=轻微/建议。本轮无阻断、无 P2，共 6 项 P3。

### R1（P3｜类型校验）operationId/jobId 仅校验真值，未校验字符串类型

- 位置：`packages/engine/src/ontolearn_engine/storage.py:219-220`（commit）、`storage.py:638-639`（commit_round）。
- 触发条件：调用方传入真值非字符串（如整数 `12345`）作为 operation/job。
- 影响：探针实测 `commit("p", 0, 12345, "job", manual=[...])` 静默成功，经 TEXT 亲和性存为 `'12345'`。无数据损坏（int 与等值字符串查询均可命中 marker），但守卫未兑现"字符串标识"的文档契约，未来 TS/Python 边界若传入数字 ID 会形成两种词法形态。
- 证据：探针 `nonstring_operation: NO-ERROR (unexpected)`。
- 修复建议：改为 `isinstance(operation, str) and operation` 与 job 同样处理。
- 处理结论：建议在 I03 契约冻结前修复；允许延期，不阻断本次。

### R2（P3｜重试语义）轮次提交重试不返回原标记；跨运行复用 operation 抛裸 IntegrityError

- 位置：`storage.py:644-646`（Nonsequential 判定）、`storage.py:660-662` 与 `storage.py:761`（`rounds.operation TEXT UNIQUE`）。
- 触发条件：a) 轮次提交成功但响应丢失后原样重试；b) 同一 operation 字符串用于另一运行的轮次。
- 影响：a) 返回 `Conflict("Nonsequential round")` 而非原标记，调用方需经 `progress(run)` 对账——S1 的"同 operation 重试返回原标记"契约只对 `Store.commit` 声明，轮次路径不违反冻结文本，但与提交路径行为不对称；b) 探针实测抛出未包装的 `sqlite3.IntegrityError: UNIQUE constraint failed: rounds.operation`（事务正常回滚，无残留写入），错误形状不是领域 Conflict。
- 证据：探针 `round_retry_same: OK Conflict: Nonsequential round`、`round_op_cross_run: RAW IntegrityError (unwrapped)`。
- 修复建议：在插入前查询 `rounds.operation`，命中则按"身份重复内容不同拒绝 / 相同返回原快照"处理；至少将 IntegrityError 包装为 Conflict。
- 处理结论：I04（持久 job 状态与提交标记对账）设计时必须覆盖此路径；允许延期，不阻断本次。

### R3（P3｜过度失效）两条净零内容变化仍推进 `facts:asserted` 版本

- 位置：`storage.py:255-269`（remove 对已墓碑事实再次 UPDATE）、`storage.py:272-305`（同一提交内 remove 手工事实后 manual 同事实重插）。
- 触发条件：a) 对已是墓碑（object=NULL）的受管事实再次 `remove`；b) 一个计划内先 remove 再 manual 添加完全相同的手工事实。
- 影响：探针实测 a) `facts_version 2→3` 且 stale 元数据的 after 值刷新；b) `state_equal=True` 但 `facts_version 1→2`。错误方向保守（只会多标记过期、绝不会漏标记），依赖该事实的结果被无谓置为过期需重跑。D.2 第 9 行"无意义失效"禁令仅针对模型配置，此处不构成条款违反；与"完全相同人工事实不推进版本"（事实已存在路径已正确实现）精神略有不一致。
- 证据：探针 `double_remove_bumps_version`、`net_noop_remove_readd`。
- 修复建议：remove 前判断墓碑状态跳过；或以"提交前后事实终态集合相同则不推进版本"统一判定。
- 处理结论：建议后续迭代统一 no-op 语义；允许延期，不阻断本次。

### R4（P3｜并发鲁棒性）迁移版本号读取在事务外的 TOCTOU；写锁竞争超时为裸 OperationalError

- 位置：`storage.py:69-74`（`PRAGMA user_version` 在 `BEGIN IMMEDIATE` 之前读取）、`storage.py:41`（`timeout=5`）。
- 触发条件：a) 两个进程同时打开同一 pre-v2 数据库；b) 一个连接持有写事务超过 5 秒时另一连接提交。
- 影响：a) 后者 `CREATE TABLE mapping_state` 报 `already exists` 失败（诚实失败、可重开恢复，无损坏）；b) 探针实测第二写入方 5.2s 后 `OperationalError`，而非结构化 Conflict——对 spike 单进程场景可接受，但 I03 错误码映射需覆盖。
- 证据：代码路径推理（a）+ 探针 `second_writer_under_lock: OperationalError after 5.2s`（b）。
- 修复建议：把版本读取移入 `BEGIN IMMEDIATE` 之后；忙碌/锁错误在服务层映射为结构化错误。
- 处理结论：允许延期至 I03/I04；不阻断本次。

### R5（P3｜性能预告）映射与槽位校验存在 O(事实数 × 本体定义数) 重复解析

- 位置：`storage.py:418-424`（`own_ids` 查询在每事实循环内重复执行）、`storage.py:372-381` 与 `storage.py:428-435`（每事实重新 `json.loads` 全部本体 payload）。
- 触发条件：大映射计划或大量本体定义。
- 影响：18/180 三元组 spike 规模下无感知（evidence 测量正常）；真实项目规模会放大。仅性能，无正确性影响。
- 修复建议：循环外预取 own_ids 与 singleValuedPredicates 集合。
- 处理结论：允许延期；引入真实数据规模前处理即可。

### R6（P3｜容量预告）每次正式提交写入全量前后状态快照

- 位置：`storage.py:229-236`、`storage.py:333-344`。
- 触发条件：项目状态较大时每次 commit 均序列化完整 state（内容寻址去重仅当完全相同）。
- 影响：存储随提交次数线性增长；ADR 已明确"存储压缩留待对应业务"，属已知权衡而非缺陷。
- 修复建议：后续以增量/差分快照或压缩策略替代，须保持不可变语义。
- 处理结论：维持 ADR 登记的延期状态即可；不阻断本次。

### 安全与数据一致性专项检查结果（未发现新问题）

- SQL 注入：生产代码全部参数绑定（`?`）；仅常量 DDL/触发器名与测试侧整数 PRAGMA 使用插值，满足数据库参数化约束。
- 输入校验：`iri()` 拒绝相对/含空白/非法字符 IRI；`term()` 经 Turtle 单三元组解析拒绝多语句注入、非规范词法（三引号、`\u` 转义、显式 xsd:string、大写语言标签），既有测试覆盖。
- 隔离与不可变：正式提交、快照、runs/rounds/run_terminal/commit_evidence 均有 SQL 触发器防改写（测试实测 DELETE 被 ABORT）；`publish`/`start_run` 校验快照项目归属；缓存回收仅清未 pin、非当前的 payload。
- 无网络、无凭据、无遥测新增；未提交任何数据库/业务数据/密钥。

## 6. 关键验收项的独立核验记录

- **故障矩阵**：7 个提交点 × cancel/exception/disk/exit × mapping/changeset 共 56 项在本人 `npm run check` 中通过；exit 为真实子进程 `os._exit`；另有 `max_page_count` 真实触发 SQLITE_FULL 的映射/ChangeSet/轮次 3 项。提交前任意点失败后重开仅见最后已提交状态、无 marker；`after_commit` 后取消/退出不撤销已提交数据。
- **九行正反例**：参数化测试对 D.2 每行给出"订阅实际依赖过期、不相关依赖不过期、同版本不过期"三类断言；第 9 行 model 为 null 原因，不生成第九种码。`invalidation-v1.json` 与 PRD D.2、acceptance.md 对照表逐行一致。
- **同事务提交标记**：commits/commit_evidence（operation/job、前后快照引用）与正式数据、版本、所有权、失效同处一个 `BEGIN IMMEDIATE` 事务；operation 重试返回原标记、身份重复内容不同拒绝、旧基线拒绝均有测试。
- **历史/所有权/乐观并发/迁移**：源行删除保留手工事实、内容不变重跑不推进版本、人工漂移/多来源/单值 slot 冲突、墓碑阻断重跑且可经显式 `edits` 复活后重跑（探针实测恢复路径成立）、第二连接旧基线拒绝；迁移中断回滚（DDL+版本号+数据）后重开可重试、未知映射版本写 -1 显示过期、未来格式拒绝打开、备份拒绝覆盖目标。
- **两档真实 RDFLib**：独立复跑 verify-i01，开发与包内 1x/10x 各三次，固定 SELECT 完整结果集、18/180 三元组、六阶段耗时与内存（tracemalloc 峰值 + 进程级 ru_maxrss，条件如实标注）均为原始记录，无容量达标宣称。
- **实际包内同样例**：独立重建的引擎可执行文件与提交 evidence 哈希逐字节一致，包内探针、health、数据契约（invalidation-v1.json）、许可证资源全部通过——"不等 I05"的基础打包条款已兑现且可复现。
- **E.5 与 G 基线诚实性**：`storage_baselines.E5` 与 PRD E.5 原表逐轮数值完全一致（产能 3：积压 W004；W007–W008；W010–W012；W013–W016，累计 3/6/9/12；产能 4 全清，累计 4/8/12/16；两次重放一致）；acceptance.md 明确区分"存储回归已执行"与"业务执行器未执行/未通过"，无冒称。

## 7. 历史问题复审

本轮为本模型首个独立 Round（Round 1），无本模型历史问题需要复审。开发会话提交前的内部 agent 复核 7 项意见（internal-review.md）对应的修复均有专项回归测试且在本人复跑中通过；此为本人独立验证结果，不构成对该文档结论的采信。

## 8. 对问题处理的总要求

R1–R6 均为非阻断建议：R1、R2 建议在 I03 契约冻结/I04 对账设计时一并关闭；R3 可与 no-op 语义统一处理；R4 的错误映射归属 I03/I04；R5、R6 在真实规模引入前处理。开发会话应在 `docs/reviews/I01/status.md` 中对每项记录采纳/部分采纳/不采纳/延期及理由。若后续候选修改实现、测试、配置、依赖或验收口径，须新候选并重新双审，本轮通过不自动延续。
