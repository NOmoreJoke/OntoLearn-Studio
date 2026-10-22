# T05 完整工程指定独立审查 包 O — ZCode 报告（designated round 1）

2026-10-22。审查者为 ZCode（GLM-5.3）指定独立审查 agent，未参与任何候选实现。本报告是本轮唯一新增报告写面；未修改任何受审实现、测试、锁、验收、旧报告/manifest、AGENTS 或 launch 冻结输入；未 stage/commit/切分支/push/PR/merge/Goal。

## 结论

**Pass，严格限定为本方完整 O 静态审查范围 + 两条授权既有正常 O 命令的本次实际复验。** 未发现需要阻断本范围收件的 P0/P1/P2 缺陷。

同 stage 内以下范围 **无法验证（不是 Pass）**：产品/模型运行、I05 model/probe/matches/selftest、collector/JSONL 适配、真实 JSONL/预算/费用/capture 生产验证、受限 runtime actual ZIP、打包/生产。全部历史失败与 137 pending 原样保持，本报告不关闭任何 pending、父 T05/P0、正式 Job/Store/selected/wholeH、SQLite HOLD/S1/B1、CI 两 OS/真人/develop 门。

## 1. 实际身份与设置读回

| 项目 | 实际读回 |
| --- | --- |
| app | ZCode（桌面端 CLI harness） |
| 模型 | `account:bigmodel-individual-coding-plan/GLM-5.3`（来自本会话 harness 系统上下文） |
| 思考等级 | 要求为 max/最高；模型内部思考等级无法从沙箱内独立读回，保持**未核**，不以要求设置充当读回 |
| 权限 | yolo/完全访问（本次全部工具调用实际未出现权限阻断，与要求一致；用户级配置不当作逐会话读回证据，实际行为见第 3 节命令记录） |
| 真实 task/session/turn ID | **未核**。无法从审查沙箱内读回 ZCode 应用任务数据库；未用 null 信息假称任务已建立。launch-map.json 中 actualTaskId/actualSettings/actualTerminal 仍为 null |
| workspace | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-zcode-review-e15ce44`（实测） |
| branch | detached HEAD（`git branch --show-current` 空，实测） |
| HEAD（过程 ref） | `86df64a2c707355ed177d536ef5975a1986c0f0b`（实测 `git rev-parse HEAD`） |
| 固定源 source/process | `77852d27a3c4e84867a42f243e0f4e0f32b8df67`（914 件）；`git ls-tree -r` 计数 914/958/784 全部实测吻合 |
| repository base | `5f910b52c69d86a1076b2032e5d3c63e715947f3`（784 件，实测） |
| 当前 AGENTS | 15147 B / SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持未暂存修改，本审未改（实测 shasum + git status） |
| launch 输入 | 11 件全部读毕并逐件 hash：scope-contract SHA256 `371fcf080d86eb1649dc1edea16ff6066c96dced83ed059af05336ea148c93d9`（与 launch-map commonScopeSHA256 相等）；launch-prompt `887066cd…`；frozen-original-prompt 与固定路径 `docs/iterations/T05/projection-R3-receiving/review-packages/O/zcode-prompt.md`（`57905299…`）同字节；guidance 四快照（AGENTS-current=`de15f6ce…`、desktop-operation-policy=`2032bd9e…`、developer-common-instructions=`567b6e70…`、external-review-permissions=`feea1595…`）已全文读 |
| 历史 Git AGENTS | 1056 B / `1b3c0291…`（launch-map 声明，未当当前指南） |

工作树状态（审查结束时）：仅 ` M AGENTS.md`（受保护未暂存）与未跟踪 `docs/reviews/T05/projection-R3-receiving/launch-O/`；本审新增写面仅 report.md、raw/、scratch/ 与 observe 工具产物。

### 本方新 runtime 自动元数据登记（单列，不并入冻结输入）

`python3 -B …/verify-launch-input.py --phase observe`（exit 0，写 preflight-observe.json）报告 `setupReady:false`，原因为本会话期间新出现的 `.mimosa/hook-state/` 自动元数据（95 件、约 1.3 MB，含 `session_c76c854a8d2736fb809ce34b124f861b.json` 13783 B / SHA256 `f8bb34e371695c72f96c9a0a821d7d87ecd7d3a86f1dce6dc6559ee82094ae60` 及同名 continue/baseline 目录，时间戳 18:36–18:46 落在本审查时段）。归属：本方桌面 harness 的 Mimosa hook 在本会话自动创建；只登记路径/大小/不透明 hash，不删、不改、不让 ignore 规则制造全树冻结通过；其不透明 session 文件名不作为 ZCode 任务/会话 ID 证据。

## 2. 已读完整范围

1. **launch 四快照 + 本树 AGENTS + authority.md/launch-map/launch-input-manifest/scope-contract/preflight-setup**（全文）。
2. **149 件工程/authoring 清单逐件字节核验**：`review-packages/O/full-engineering-inventory.json` 全部 `engineeringFiles` current bytes=SHA=固定 `77852d27` Git blob（missing 0 / mismatch 0 / blobDiff 0，stdlib 实测）。
3. **完整树独立核验（R1-02 本方复验）**：O 包 fullTrackedTree 914 条 path 集与 `git ls-tree -r -l -z 77852d27` 直接相等，mode/type/blob/size 逐项相等 0 差异，含引号/反斜杠的 C-quote 残留路径 0 条；`docs/prd/PRD-本体学习与落地Agent工作台.md` 以真实 UTF-8 路径存在。
4. **过程差异**：`77852d27..86df64a2` 恰为 44 份纯 docs 新增（两 receiving 前缀），无受审路径改动（git diff --name-status 实测）。
5. **oracle 工程**：`scripts/build-i05-source-package-oracle.py`（1312 行，全文结构 AST + 头部/allocation/business_expected/RELATIONS/evaluate_relation/construct/validate_oracle/assert_exact_model/main 全文精读）、`scripts/test-i05-source-package-oracle.py`（47 测试逐项纲目 + 关键断言精读）、五件 expected fixture（schema.json/sources.json 全文；oracle/coverage/budget-gaps 以 stdlib 完整解析并统计核验）。
6. **T05 receiving 全部输入**：receiving.md、gap-table.md（37 行）、137-gap-ledger.json（137 行逐项）、37-receiving-matrix.json、85-graph-slot-index.json（85 槽）、designated-review-backlog.md（26 行）+ JSON 索引抽取、original-acceptance-and-policy-annex.json（全文）、source-authoring-dependencies.json（结构+关键字段）、full-review-packages.md、review-package-index.json、package-byte-verification.json、static-readback.json、R1/R1-failure/R1-repair/R1-repair-static-readback/baseline-preservation/candidate-manifest/candidate-receipt/delivery-manifest/final-delivery-receipt/source-receipt、static-attempts/csv-header-disposition.json。
7. **历史审查链**：`docs/reviews/T05/source-package-oracle/` 的 README、field-policies.md、declared-allocation-delta.md（docs/iterations/T05/source-package-oracle/ 两件）、independent-review-R1（3d8f4ee 候选）、declared-allocation/independent-review-R1 + review-disposition、author-dispositions.json、receipt.json、attempts/01 首失败原件（KeyError id 转录）、commands/ 各 invocation/result（含 self-test-01 argv/双流 SHA）、projection-R3-receiving 的 independent-review-R1（Fail）与 R2（Pass）全文。
8. **PRD 固定 base**：FR-500..505 全文、附录 C/D 全文、G.2 全文、第 10–12 节全文（FR504/505、C 能力矩阵、D 失效表、G.2 V-01/R-01..06/O-01 与 annex 逐字一致）。
9. **产品树不变量抽核**：csp.ts（唯一配置源，生产 script-src 仅 `'self'`，唯一 `unsafe-inline` 在 dev 变体 style-src 且带 origin/nonce 严格校验）、preload/index.ts（仅按业务命名方法包裹字面 channel，无通用 invoke）、renderer（无 node/fs/shell 引用）、main/index.ts（有限路由表 + sender/senderFrame/可信文档校验 + safeError 固定码）、storage.py（Store/BEGIN IMMEDIATE/commit_evidence 不可变触发器/commit/snapshot/commit_round 结构）、rdf_snapshot.py（仅从快照 dict 重建）、invalidation-v2.json（附录行映射 staleReason）、protocol.py（strict decode）。
10. **六件 I05 R3 固定源**（`50317c79`）：不在本方树内；因该 commit 在共享仓库对象库可达，按允许的只读 Git 静态核对逐字节验证 source-receipt 六项 bytes/SHA 全部相符（未执行 model.py/matches/selftests）。

## 3. 实际命令与完整流（cwd 均为本 workspace）

| # | argv | 环境要点 | exit | 结果 |
| --- | --- | --- | --- | --- |
| 1 | `python3 -B scripts/test-i05-source-package-oracle.py` | TMPDIR=本方 scratch/tmp；stdout/stderr 全流落 raw/oracle-test.stdout(0 行)/.stderr(52 行) | 0 | **本次实际：Ran 47 tests in 4.754s — OK**（47 项全过；非引用旧报告数字） |
| 2 | `python3 -B scripts/build-i05-source-package-oracle.py --check` | 同上；stdout 全流落 raw/oracle-check.stdout | 0 | 内存重建五件 expected 与冻结字节逐件相同（oracle.json 5920695B/`7ae1c131…`、coverage.json 154032B/`95d7395…`、sources.json 9872B/`f2db5b1a…`、schema.json 9106B/`74889cca…`、budget-gaps.json 362492B/`e68188dd…`）；datasets 320、observations 417、specified 280、pending 137、wholeOracleComplete=false；未写回任何文件 |
| 3 | `python3 -B …/launch-O/verify-launch-input.py --phase observe` | — | 0 | sourceAndInputBytesVerified=true、290 保护件、写 preflight-observe.json；setupReady=false 由 .mimosa 新元数据所致（见第 1 节） |
| 4 | 源前后 hash | 命令 1/2 前后 `shasum -a 256` 七件（两脚本+五 fixture） | — | raw/oracle-source-pre/post-hashes.txt diff 为空，**源与 fixture 未变** |

静态核对均为 `git`（status/rev-parse/ls-tree/cat-file/show/diff）与 `python3` 标准库（json/hashlib/ast/subprocess）heredoc，未 import 任何仓库模块执行业务逻辑。授权边界遵守：未启动产品、未跑 I05 model/probe/matches/selftest/collector、未生成新 actual、未读受限 runtime actual ZIP、未用另一树 .venv/node_modules、未装依赖、未改源码/fixture 求绿。

**非零与冗余披露**：本审探索期有三次静态脚本自身错误（137 账首次比对用错行键名 `pendingFields`、ls-tree `-l` 元数据按 3/4 字段解析两次 ValueError），均已定位更正后通过；这些是本审工具错误，不是产品/候选失败，输入未变。另有一次在读取元数据的组合命令中**冗余地重复调用了命令 1 同一测试套件且 stderr 弃流、exit 未记录**——该重跑无调度必要（违反“无变化不重跑”的执行纪律），因是同源同范围授权命令且源未变，不影响结论，但如实披露不予隐瞒。

## 4. 静态审查发现

**未发现 P0/P1/P2 缺陷。** 要点核验：

1. **计数与状态真实性**：`oracleStatus` 由 `pendingFields` 实算（`'pending' if pending else 'specified'`），`wholeOracleComplete = not counts['pending']`，无硬编码；`validate_oracle` 强制 pending 不隐藏、unknown 不升为 matched、拒绝无部分 report、SHACL 六字段完整、conforms 一致、declared allocation 逐 ID 重推导并 exact-model 比较（builder L1122/1127/1159/1240-1262）。coverage/oracle/schema 三处 280/137/88/26/2 计数交叉一致。
2. **137 pending 字段分布**与 receiving 账逐类吻合：82 `budgetAdmissibility+typedSerializedUsage`、32×2 生产/DAG/restore 组、26 `declaredAllocationExpectation`、14 `A1ExactErrorProjection`、11 `legacyDTO+evidenceProjection`、8 前门（7 `reason+phase`+1 `exception+reason+phase`）+1 `exactStructuredOnlyError`、3 `scopeProvenanceDigestEncoding`。
3. **137-gap-ledger 与 oracle pending 集合逐 ID 相等**、`originalPendingFields` 逐项相等、closed 全 false、status 全 pending（本方 stdlib 实测，0 差异）。
4. **37 接收矩阵**：36 旧 pending + 1 旧 specified（`legacy/unbound-head`），101 pending 无 R3 完整 target——与 receiving.md/gap-table 声明一致，无外推关闭。
5. **独立性硬约束**：builder 仅标准库导入（测试 L65-73 AST 白名单强制，另禁 eval/exec/__import__）；six 输入 + 12 规范文档全部 pin bytes/SHA，任何变动在解释前即被拒（test_hash_change_rejected_before_interpretation）；`same-issued-object` 谓词拒绝 None/JSON 值等价，要求对象同一（L1023-1028）；`--check` 模式绝不写回（L1297-1299）。
6. **七池声明分配**：N=max(1,n)≤100、码点序 sorted-divmod、disabled 占槽不回流、空集匿名 dummy 不捏造身份；26 项 pending（25 records 缺显式 disabled + 1 fullview Turtle 缺 universe）无一被偷偷补默认；`actualAllocationCaptureProvided=false`、`actualUsageProvided=false` 保持声明/实际分离。
7. **R3 纯 docs 交付链**：R1 Fail（R1-01 authoring 依赖缺件、R1-02 C-quote 路径 73 条）→ bbaf58 先保全 → e15ce44 修复 → R2 有限 Pass → 86df64a2 绑定 final receipt；本方独立复验 R1-02（第 2.3 节）与 R1-01 的 O 侧物证（source-authoring-dependencies.json 存在、149 工程件含全部 inputs/goldens/manifest），链路自洽。

非缺陷观察（不计严重度）：`declared_allocation_expectation` 中 `rule_ids.index(rule_id)` 为 O(n²)（n≤100，无实际影响）；`canonical()` ensure_ascii=True 为有意保留（孤立代理拒绝输入的无损表示，builder L64 注释明确）。

## 5. 历史意见与失败逐项处置

| 历史项 | 本方处置 |
| --- | --- |
| R1-01 authoring/fixture 数据缺件（P2） | 已在 e15ce44 修复；O 侧证据本方核验：149 件工程清单含 5 inputs+goldens+manifest+guidance 16 件，dependencies manifest 存在且声明 25 来源/31 绑定已核（R2 记录）；本方未重跑其 1316 全包 occurrence 核对（无变化不重跑），仅对 O 的 149 件独立全量核同。**Closed（采纳 R2 结论并本方抽样独立复核）** |
| R1-02 73 条 C-quote 展示路径（P2） | **本方独立全量复验**：O 包 914 条真实 UTF-8 路径集与 `ls-tree -z` 直接相等、0 残留、0 元数据差异。Closed |
| R1 Fail 原件保全 | bbaf58 保全链、R1 报告 16082B/`4536d4be…` 原字节仍在（本方 hash 实测）；final-delivery-receipt 记录完整。保持 |
| IRI 旧 74 失败/57 通过（T05-08，fixed131） | backlog 行保留 `old74failed/57passed; fixed131`；属 I 包历史工程，本包不复制其 terms；未沿旧内审为指定 Pass。保持未指定双审 |
| FR505 旧 16 例不足（→T05-03 fff 22 例） | backlog 保留“22 authored cases, 18 comparison cells…not actual FR505 engine execution”；FR-505 原文与 G.2 已读；真实引擎执行仍未发生。保持 |
| graph 四红（T05-15 langString/nni/dateTime-equal/before）→ T05-16 修复 | backlog 保留“4fail…four original product differences closed with real Validator/report, date/illtyped stillValidator0”；修复属 G 包工程，本包不拼接；date/ill_typed 相关 pending 仍在 137 账。保持 |
| date 两次首检失败（T05-19） | backlog 保留“two first check failures retained; not global state/concurrency proof”。保持 |
| oracle 137 pending / wholeOracleComplete=false | 本方命令 2 实测 280/137/false；137 逐项账相等。**保持，无一关闭** |
| 26 allocation 声明缺件 | coverage.declaredAllocation.pending=26（25 records+1 fullview Turtle）本方实测；88 specified/2 not-invoked 同。保持 |
| 旧模型不指定 Pass / designated 实际任务缺证 | backlog 26 行 taskId/actualSettings/actualTerminal/report 全 null 保持；本审自身 task/session 亦如实未核（第 1 节），不用 null 假称启动。保持 |
| R3 37 targets 设计收件 | 36 pending 交集+1 specified 本方核验；10 legacy math 与旧 oracle 数学侧车的相等性沿用 R1 独审记录（本方未重跑数学比较，无变化不重跑）；fullMatches 入口/85 槽/全 BNode/raw-source/真实身份/held 首错均仍为设计输入未实施，gap-table“明确未闭”列与 137 账一致。保持设计态 |
| 12 项非标 date 首错 pre-registered 断言 | oracle 内 `declaredRegressionAuthority=pre-registered legacy regression assertion`、`independentLibraryClassificationProven=false` 声明仍在（schema/field-policies/README 一致）。不升格为独立库分类证明 |
| M 三份 localuntracked actual ZIP | 按边界仅登记为历史归属与可访问性缺口，本审未打开、未消费、未固化 expected。保持 |
| E1–E4 未实施原验收 | backlog 四行 planned-not-implemented 保留，不因 not-ready 排除。保持 |

## 6. 边界与未验证清单（全部为“无法验证”，不以静态/旧证据补绿）

- 产品运行：任何 pytest/npm check/build/package/e2e/GUI/原生窗口——本轮无授权，未执行。
- I05 model.py/probe/matches/selftests/collector、JSONL 适配、最终比较器——未实施/未授权，R3 仅为纯设计收件。
- 真实 source/package 观察、JSONL 实流、完整 17L/planDigest/budgetUsage/费用/capture/真实同次 allocation——82 profile + 32 生产/restore 链全部 pending。
- A1 精确安全错误投影（14）、legacy 五字段 DTO/evidence 编码（11）、scope 精确 provenance 编码（3）、7+1 前门精确码、implicit loader 守卫真实投影——逐项 pending。
- 85 槽/BNode 统一域/wire 顺序/raw-source exact——静态登记，无执行验证。
- 受限 runtime actual ZIP（M 三份）不可访问；六件 R3 源仅经共享仓库对象库只读核字节，未进入 I05 树。
- CI 两 OS、远端核验、真人验收、develop/PR/merge、SQLite 损坏 HOLD、未签 native/caller/producer 票——无授权、无证据，全部未关闭。
- 本报告不签署：父 T05/P0、FR500–505 六项 P0 的完整产品验收（annex 中 V-01/R-01..06/O-01 全部仍“未核验完整产品通过”）、正式 Job/Store/selected/wholeH、S1/B1。

## 7. 最终判定

- **本方完整 O 静态审查范围（149 件工程/authoring 字节与固定源一致性、oracle builder/test/五件 expected 的静态正确性与自洽、receiving/gap/backlog/annex 账实一致、历史失败与修复链保全、产品树不变量抽核）：Pass。**
- **两条授权 O 命令本次实际复验：Pass（47 tests OK；--check 五件逐字节一致，417/320，280/137，false whole）。**
- **运行/打包/生产依赖：无法验证（清单见第 6 节），按原门保持。**

报告最终 bytes/SHA 由落地后独立回读提供，不自含自身 hash。
