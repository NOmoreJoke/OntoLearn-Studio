# T05 R3 收件与完整工程发审准备：独立修复复审 R2

结论：**Pass，限定于冻结 docs candidate 的本轮修复与发审资料准备。R1-01、R1-02 两项 P2 均已关闭；未发现新增需退回的问题。** 原 R1 Fail 及原候选保持不变。本结论不是指定 ZCode/MiniMax 双审 Pass、运行依赖闭包、产品验收、137 pending 或父 T05/P0 的通过。

## 固定身份和先保存 Fail 的顺序

| 项目 | 实际身份 |
| --- | --- |
| reviewer | `/root/projection_receiving_review_package_independent_review`，原独立 R1 审者的定点修复复审 |
| cwd/worktree | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle` |
| branch | `feature/T05-source-package-oracle` |
| R2 candidate / 审查 HEAD | `e15ce44d3a39a4634d309a05bb2422d00a576b7c` |
| R1 Fail 保存 / R2 parent | `bbaf58aeff5f0617548c6bee645e27548b2e0497` |
| R1 failed candidate | `de301e1dcd8c862ed43db383a02d12543e62898f` |
| 原 T05 continuationBase | `77852d27a3c4e84867a42f243e0f4e0f32b8df67` |
| repositoryBase | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |
| 唯一新增写面 | 本报告 |

本轮全文重读实际 R1 报告及两项处置文件。Git 实取 parent 证实 `de301 → bbaf58 → e15ce44`；bbaf58 只有 R1 报告和初始 failure disposition 两件新增，处置仍为 Open/尚未修复。修复在后继 e15 中发生，没有倒改失败候选求绿。R1 实际仍 **16082 bytes / SHA256 `4536d4be70da690c10999f80e59db7f745be684160669cc71446ec238e3f20b1`**，current 与 bbaf58 Git 原件精确相等。

承接 R1 已全文读取的当前 AGENTS 和外控规则，本轮继续执行更窄的 Git/文件/标准库静态窗口。没有 import 或调用源模型、产品、原 authoring 工具/验证器，没有 selftest/pytest/npm/build/package、新 oracle/collector/actual、第三方、GUI/应用/网络/安装/native/DB/票据操作；不打开 M 原 actual ZIP、不把 actual 当 expected、不接触费用 WIP/Goal。没有 stage/commit、切分支或其他源文件写入。

## R1-01 [P2] 已关闭：补齐 authoring/fixture 数据与准确历史范围

**修复证据定位：**

- 新 `docs/iterations/T05/projection-R3-receiving/source-authoring-dependencies.json:2`：三个明确的 source tool 依赖记录；`:646`、`:657`：原31历史绑定及只读政策；`:912–913`：原25来源清单和本地固定 Q 树字节核对。
- `review-packages/Q/full-engineering-inventory.json:541`：R1 反例 `number-goldens.json` 现已实际进入 engineering/current/Git/SHA 范围；同一文件的其余固定输入、金标、source windows/gaps 和 manifest 也已进入。
- `candidate-coverage-matrix.json` 的 T05-09（stageId 在 `:27217`）和 T05-12（`:30695`）改为完整纯资料 delta；不再因为存在 Python 工具而只选代码。

**独立核对结果：**

1. 原 `9333` 的 `real-executor-oracle/inputs.json` 25 个 sources 逐项与新 manifest 的 declared 对象精确相等；对应 Q 固定 current/Git bytes、SHA 和清单条目全部核同，没有仅按来源名认定覆盖。
2. 原 `profile-M1-math-explanation-input-contract/fixed-inputs.json` 的31个 inputs 与 `original31Bindings` 完整有序对象相等。它们保留原 tree/ref/path/bytes/SHA 及 protected 标记；readPolicy 明示仅解析原绑定元数据、未打开外部 source/current 文件，`externalRuntimeOrPolicyDependencyClosureVerified=false`。没有把历史 AGENTS/外控 SHA 当当前值，也没有把其他树的 semantic 版本拼入 Q。此处通过的是原绑定精确保留，不是外部 runtime/policy 现状验证。
3. 三个直接 tool 的固定身份与所有 requiredLocalFiles 全部在对应工程 SHA inventory：`verify-document-fixtures.py` 19件、`assemble-explicit-oracle.py` 26件、`structure-check.py` 29件。独立 AST 读取 verifier 的字面 `read(...)` 路径，它们全部包含在19件中；原25来源也纳入后两项依赖。只解析 AST/原件，未执行工具。
4. 六包 `authoringAndManifestFiles` 的每个对象都与实际 engineering inventory 同条目完全相等：Q98、I14、B2、M75、G14、O26。原输入、goldens、必要清单和镜像不再只存 fullTrackedTree metadata。
5. 21个有固定 ref 的主历史范围均重新与 NUL Git diff/树集合比较。pure-design-and-tooling、external-fixture-and-tooling 的 present paths **等于完整 continuation delta**，删除集合另列；T05-09=26件、T05-12=28件、T05-14=76件。其余实现阶段与明示 engineering+authoring selector 精确相等，不由最后一个 commit 或祖先推导。各阶段对六包的同/改/缺及 complete 标志逐件核同。
6. 17个命名历史 ref 的 actualParent、全部 present delta、删除集合及六包同/改/缺逐件核同，现为完整 commit delta。显式工程/authoring 条目核 SHA，其余 raw/runtime/process-only 材料保 Git mode/blob/size 元数据；不把 metadata 当已经读取 actual 内容或完整运行验证。

依赖 manifest 的限制与提示一致：有些历史 evidence consumer 需要受限 runtime 原件，静态完整源码资料不代表可运行闭包或成功。未实施 E1–E4、早期不同源码版本、原失败及后继处置继续在 backlog，没有被共享字节消账。该修复满足 R1 的数据遗漏反例及范围要求，没有新增执行授权。

## R1-02 [P2] 已关闭：六包全部使用真实 UTF-8 Git 路径

本轮直接执行 `git ls-tree -r -l -z <六固定source refs>`，按 NUL 分隔、UTF-8 解码取得真实 `path`，逐项与 fullTrackedTree 的 path/mode/blob/type/size 比较。**无需任何 C-quote 反解，6390项全对象直接相等**；没有字面外层双引号路径。对原 de301 清单计数，原73条展示路径均已修正。

| 包 | 固定 source/process | 完整树 | engineering+authoring | 修正原展示路径 |
| --- | --- | ---: | ---: | ---: |
| Q | `9333e69234a6f54a0dfc1485f49d8fdeb4b69cfd` | 1031 | 276 | 12 |
| I | `1a9672a5bddcd8563f17a45acbc04a072aea0c45` | 935 | 187 | 12 |
| B | `ca0990a893a6d3af106985fe5dae5ff287b79553` | 890 | 141 | 12 |
| M | `057d2d96aaaac92d59f593678fc265fd13eace78` | 1145 | 313 | 13 |
| G | `525c91717c07dc4b386fcec00f897e1e6a75caf1` | 1475 | 250 | 12 |
| O | `77852d27a3c4e84867a42f243e0f4e0f32b8df67` | 914 | 149 | 12 |
| 合计 | 六套独立源码树 | 6390 | 1316 | 73 |

例如 Q 的真实 PRD 路径现出现在 inventory `:397` 和 `:3373`，分别属于工程条目与完整树条目；已是 `docs/prd/PRD-本体学习与落地Agent工作台.md`，直接可解析，不再存 Git 展示语法。

## 字节证明、计数及资料同步

独立逐件读取全部 **1316个 current occurrence**，与各包固定 Git blob 原字节、长度和记录 SHA256 精确比较，全部相等；其中472个唯一 current blob。Q 的8个原输入/提案 bundle ZIP 只作为不透明原字节做 hash，没有解包或执行；它们不是 M 的 runtime actual ZIP，M 三份原 actual 完全未打开。

**524 unique proof 的独立核算：** 当前工程+主历史带SHA源条目+命名历史带SHA源条目去重并集为521；还包含矩阵已有的三个 changed target byte hash，合计524。三件均在 T05-06→Q 的 `changedAtSamePath`，本轮另按真实目标 ref/path/blob/bytes/SHA 逐件核同：

| 目标原件 | bytes | Git blob | SHA256 |
| --- | ---: | --- | --- |
| `docs/reviews/T05/checkpoint.json` | 27974 | `650b5d6f1ce248e9b30a4543d466109063f4e3ce` | `5a4820be3a3b5a1f4fe28b38a2a98fe5a59b663162fc9c2bb2ff3395059ae4b2` |
| `docs/reviews/T05/internal-review.md` | 23347 | `c44e72719c9fec8562c0ba86c5fcee2cc316ee3b` | `197f59cd859279c63b3c8d09ad27453a0cb73b75aa81d0775c826b2b93c250f7` |
| `docs/reviews/T05/status.md` | 36882 | `ae2fbe7d7356d73aecf8a12e3806839fc8c9bb7b` | `b21111c777198f4aa77f7dc7bccbfa0c132eca919d4e26304f467cdb1aab255e` |

这些是字节对照的目标证据，不来自31外部绑定或 runtime actual。初次只合并源条目漏掉 targetSha256 导致521的差异已定位并核清，不构成候选统计问题。

12个提示的完整共同正文及全部包差异再次核对：包 worktree/branch/base/source/tree、真实 inventory 绝对路径、工程新计数、source-authoring-dependencies 要求、R1先保全 ref、唯一报告路径及两模型设置全部与 index 相等；除包身份/模型设置等明示变量外共同各行相同。26行历史摘要的件数及各包同/改/缺逐项等机器矩阵，六包件数也等清单。package-byte-verification、repair disposition、candidate receipt 的 proof 完整相等；matrix 的相应字段一致。

所有 model task ID/actual settings/report/terminal 仍为 null，taskCount=0。未把 required settings 当实际读回，未启动指定任务。调度 lease 的现状会变化，准备时 T02 文字只属历史；父 agent 告知的新 lease 与后续两模型物理审查隔离安排属于另行 launch 过程事实，本 Pass 不证明它们已建立或任务已开始。

## 原件保全与无变化范围

`77852d2..e15ce44` 的两个新前缀恰41个文档：manifest40成员+self。40件逐项 current=候选 Git=manifest bytes/SHA，manifest 自身 current=候选 Git；无额外产品/旧oracle路径。所有候选 JSON 已完整解析，并拒绝重复键及非有限值；全部文本末尾换行且无行末空白。两个新前缀 `git diff --check` 实际 exit 0。

旧 declared-allocation manifest 的129成员及自身共130件，current=778 Git=原清单 bytes/SHA，总 **20,762,965 bytes**。R3 receiving/gap-table、37 matrix、137 ledger、85 slot index、backlog JSON/MD、原验收 annex 全部 current=de301 原字节，故 R1 已独立核过的37/137/85、13数学侧车、原 source receipt 和所有未关闭边界保持，没有无变化重跑模型。280 specified/137 pending、wholeOracleComplete=false 未改。

保护 AGENTS 仍15147 bytes，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`；写报告前 `git status --short` 只有 ` M AGENTS.md`。没有将它 stage/reset 或修改。

## 实际静态命令与非零探索

本轮 argv/cwd/输出在本审工具记录；以下是工具记录摘要，不伪称另建了原始 stdout/stderr 文件。cwd 均为固定 worktree。

| 实际调用 | 结果及用途 |
| --- | --- |
| `git status --short`、`git rev-parse HEAD/ref^`、`git show --stat bbaf58...`；完整读取 R1/两处置 | exit 0，证实冻结身份、先 Fail 后修复及原报告 |
| `git diff --name-only -z`、`git ls-tree -r -l -z`、`git show ref:path`、`git cat-file blob` | exit 0；41文档、6390真实路径、1316 current/Git/SHA、主历史及命名完整 delta、额外目标 hash |
| 标准库 `python3 - <<'PY'` JSON/hash/AST/集合断言 | 最终对应核对 exit 0；未 import 仓库模块或执行被审工具 |
| `git diff --check 77852d27a3c4e84867a42f243e0f4e0f32b8df67 e15ce44d3a39a4634d309a05bb2422d00a576b7c -- <两个新前缀>` | exit 0，仅本交付范围，不覆盖 I05 历史 full diffcheck exit 2 |

本轮三次非零探索准确保留：

- 首个工程检查脚本错误地断言任何 `.zip` 都应被排除，遇到 Q 原输入/提案 bundle 后 AssertionError，exit 1。随后逐项确认这8件是工程原输入资料，仅做不透明字节 hash；M 原 actual 未读。真实6390路径检查已在该断言前通过，后续全1316核对完成 exit 0。
- 合并主/命名矩阵脚本完成21个主范围后，对命名目标误用主矩阵字段 `fullyCoversHistoricalRangeBytes`，KeyError exit 1。按实际 schema 的 `fullyCoversNamedCommitBytes` 更正，17完整命名 delta×六目标独立核对完成 exit 0。
- 初次核算 unique hashes 只收集 source rows，得到521并断言524，exit 1。父 owner 指出已有 targetSha256 范围后，本审独立核所有 changed-target SHA，识别上述三个额外 Git blob，524核算与原记录一致，exit 0。没有因此修改受审文件。

初次打印大依赖 JSON 被工具截断，后续改为完整 JSON 解析、定点结构/所有条目及依赖集合核对，不把截断打印当已看到全部原文。R1 自身非零、作者 CSV BOM 错误及改正、研究者路径错误、I05 历史 Fail/exit 2 均原样保留；本轮不称全部历史探索命令全绿。

## 最终处置

R1-01：**Closed in e15ce44**，必要 authoring/fixture 数据、原25来源/31历史绑定、六包字节证明与完整纯资料/命名历史 delta 已补齐，runtime边界明确。

R1-02：**Closed in e15ce44**，6390真实路径直接核同，原73条 Git 展示路径误存已消除。

本轮无新增需作者修改的发现。允许把该固定资料候选作为后续指定完整审查的输入准备；实际调度仍须 root 当前短 lease、两个模型独立物理环境与固定同候选映射、实际设置/ID/终态/完整报告读回和全部意见处置。上述下一阶段没有在本审发生。

原137/417、真实 caller/source/issuer/capture/allocation/费用/17L、正式 Job/Store/selected/wholeH、S1/B1、CI两OS/真人/develop及父P0门均保持原状态，不因本资料 Pass 关闭。报告最终 bytes/SHA由落地后回读及交接消息提供，不自含自身 hash。
