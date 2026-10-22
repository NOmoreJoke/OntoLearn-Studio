# T05 R3 收件与完整工程发审准备：独立内审 R1

结论：**Fail，限于冻结 docs candidate 的完整发审准备。发现两项 P2，未发现 P0/P1。** R3 设计收件、37/137 差距保留及指定审查缺证的登记未发现需退回的实质错误；完整工程覆盖证明仍漏掉必要 authoring/fixture 数据，完整树清单还把 Git 展示转义误存成真实路径。两项修复前不能将这份资料签为完整、可直接据其消账的工程字节覆盖包。

这是当前 agent 的独立静态内审，不是 ZCode/MiniMax 指定双审、产品验收或父门 Pass；没有创建任何指定任务。

## 固定身份与只读边界

| 项目 | 实际身份 |
| --- | --- |
| reviewer | `/root/projection_receiving_review_package_independent_review`，本轮全新独立内审 |
| cwd/worktree | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle` |
| branch | `feature/T05-source-package-oracle` |
| frozen candidate / 审查 HEAD | `de301e1dcd8c862ed43db383a02d12543e62898f` |
| parent / continuationBase | `77852d27a3c4e84867a42f243e0f4e0f32b8df67` |
| repositoryBase | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |
| fixed I05 R3 source process | `50317c791eca95e82dfbfaa2ef71c0dfc95a9302` |
| current protected AGENTS | 15147 bytes，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` |
| sole new write | 本报告；不修改受审 candidate 或其他文件 |

先全文读取当前树 AGENTS，以及根外控 `I05-projection-R3-limited-root-closure.md`、`desktop-operation-policy-20261022.md`、`developer-common-instructions.md`。按当前短 lease 政策理解调度：T02 是准备时点信息，不把旧排队文字当永久占用；T06 原任务保全。阶段只读/运行限制没有因桌面政策更新而解除。

本轮只使用 Git、文件读取、Python 标准库 JSON/AST/hash/集合核对。没有 import/调用 I05 model 或任何产品/模型函数，没有 selftest、pytest/npm/build/package、新 oracle/collector/actual、第三方、native/DB/GUI/网络/安装或 T03 票操作。未打开 M 的 actual ZIP，也未把历史 actual 当 expected；涉及 ZIP 的证据身份不读取内容。没有 stage/commit、切分支、push/PR/merge/Goal 或指定应用操作。

## R1-01 [P2] 完整工程 selector 漏掉工具实际消费的 docs fixture/authoring 数据

**定位：**

- `docs/iterations/T05/projection-R3-receiving/candidate-coverage-matrix.json:13006–13029`，JSON pointer `/stages/11/fullRangeEngineeringPaths`：T05-12 只有两个 `.py`，`fullRangePathCount=2`。
- 同文件 `:13045`，`/stages/11/targets/0/fullyCoversHistoricalRangeBytes=true`，Q 的 `sameCount=2`。
- `review-packages/Q/full-engineering-inventory.json:1431` 的 verification scope，及 `:8663` 的完整工程 scope；该清单 `/engineeringFiles` 没有下列数据。它们虽然在 `/fullTrackedTree` 有 Git blob/mode/size，未被纳入 current=Git/SHA 核对或历史逐包 fixture 覆盖。
- 人读摘要 `full-review-packages.md` 的 T05-12 行也写“2 / Q 完整同字节覆盖”。

**具体反例：** 固定 `9333e69234a6f54a0dfc1485f49d8fdeb4b69cfd` 的 `docs/reviews/T05/profile-M1-math-explanation-input-contract/verify-document-fixtures.py` 实际静态依赖：

| 代码行 | 必读同目录原件 |
| --- | --- |
| 28 | `fixed-inputs.json` |
| 38 | `domain-operator-goldens.json` |
| 43 | `math-operand-inputs.json` |
| 66 | `number-goldens.json` |
| 72 | `calendar-goldens.json` |
| 81 | `supplemental-graph-inputs.json` |
| 84–85 | `consumer-C-inputs.json`、`consumer-C-goldens.json` |
| 95、98 | `source-supply-and-windows.json`、`original-source-gaps.json` |

这些 JSON 在完整 `330fcedb297792e0addd55557688509550c3b26a..9333e69234a6f54a0dfc1485f49d8fdeb4b69cfd` range 内，却全部不在这两件的历史覆盖范围。例如 `number-goldens.json` 在 Q 的 `/fullTrackedTree/751`，在 `/engineeringFiles` 不存在。这里没有执行该 verifier；依赖来自固定函数文本的只读查看。

另一同类反例是 T05-09：固定 `f9af899fad31ea19c7540e9624c437a189b8b5bf` 的 `docs/reviews/T05/real-executor-oracle/assemble-explicit-oracle.py:33` 必读同目录 `inputs.json`，但该阶段主矩阵只有两个 Python 工具及 `tests/fixtures/quality/real-executor-acceptance-inputs.json` 三件。完整树登记不等于完整依赖字节证明。

**触发与影响：** 只要同路径 JSON 被修改、遗漏，或在另一后继树中发生不同变化，当前工程 SHA 证明和 historical complete 标志都不会对此作出判定。它不证明已经发生数据篡改，也不表示 Git 树遗失；问题在于本交付明确要求的完整源码/工具/测试/fixture 精确覆盖尚未完成。只在“没有任何工程路径”时回退到全部设计数据的规则，无法覆盖有 Python 工具同时存在 JSON 数据的阶段。

**修复要求：** 用真实静态依赖和原阶段 manifest 确定 fixture/authoring 输入、goldens、必要数据清单；补入六包 current/Git/SHA 和完整 continuation range 的逐包覆盖，区分设计输入、expected、历史 actual 与过程证据，不因后缀直接打开 runtime actual。同步更新计数、摘要、proof/receipt/manifest 和所有 complete 声明。不能只改数字，也不能用完整树 metadata 替代缺少的 current 文件核对；不可执行 assemble/verify 来补本轮授权之外的运行结果。

## R1-02 [P2] fullTrackedTree 将 Git C-quoted 展示文本当成真实 path

**定位：** 六套 `review-packages/*/full-engineering-inventory.json` 的 `/fullTrackedTree`。以 Q 的 `:2587` 为例，`path` 保存了带字面双引号及 `\\346...` 八进制转义的 `docs/prd/PRD-...md`，而真实路径是 `docs/prd/PRD-本体学习与落地Agent工作台.md`。Q 首个受影响元素为 `/fullTrackedTree/109`。各包同一 PRD 条目行：I 2519、B 2135、M 2955、G 2925、O 2014。

**独立复核：** 使用 `git ls-tree -r -l -z <sourceProcessRef>`，逐项解析 NUL 分隔的原始路径，与 JSON 的 `path` 集合直接比较不相等；将记录的 Git C-quote 显式反解后，六包全部 mode/blob/size/path 元数据才与真实 Git 树相等。

| 包 | 完整树件数 | 被误存为 C-quoted path 的条数 |
| --- | ---: | ---: |
| Q | 1031 | 12 |
| I | 935 | 12 |
| B | 890 | 12 |
| M | 1145 | 13 |
| G | 1475 | 12 |
| O | 914 | 12 |
| 合计 | 6390 | 73 |

**触发与影响：** 消费方按字段名 `path` 直接定位文件、构造 `git show ref:path`、核对完整清单或同路径覆盖时，会把转义及外层引号也作为路径内容，无法找到这些原件；其中包括必须读的 PRD 和中文历史审查。当前格式没有声明这些是待反解的 Git display path。blob/size 可在反解后核同，故没有把它升级成原始内容损坏。

**修复要求：** 通过 `ls-tree -z` 获取原路径，以标准 JSON 编码存储真实 Unicode `path`；若保留展示文字，应另设显式 display 字段。新清单直接 path 集必须与 `-z` 原路径集相等，逐件路径可解析，不能靠下游猜测补解码。同步更新全部受影响清单及 manifest/receipt；保留本 R1 原字节及 Fail。

## 已完成的必要静态核对

### 候选和旧件保全

独立 `git diff --name-only 77852d27a3c4e84867a42f243e0f4e0f32b8df67 de301e1dcd8c862ed43db383a02d12543e62898f` 恰为 36 个新文件，全部在两个授权新前缀；manifest 35 成员+self 恰覆盖该集合。每成员 current bytes/SHA 与 candidate-manifest 逐件一致。独立 `git diff --check` 该新范围 exit 0。

原 declared-allocation delivery manifest 的 129 成员及该 manifest 自身共 130 件，current=778 Git=原 bytes/SHA，合计 **20,762,965 bytes**。当前受保护 AGENTS bytes/SHA 如上；写本报告前状态只有 ` M AGENTS.md`。没有旧 oracle/golden/工具/产品变更。

### R3 接收、差距与数学关系

完整解析新前缀 20 个 JSON；对大清单按结构、全部条目和独立 Git/hash 核对，没有把工具截断的全文打印当完整阅读。人读 receiving、gap-table、full-review-packages、backlog 已分段读全；12 提示全文文本以 Q 的完整共同正文加所有差异核对，机器确认除标题、包身份、设置、说明及报告路径外其余各行完全一致。

固定来源六件的实际 Git bytes/SHA 全部核同 source-receipt；AST 仅解析 model.py 的 28 个函数定义，未执行。另全文读固定 R3 原独立报告，并静态核 `matches`/`projection_layout`：入口为 expected schema→observed schema→expected 本端 wire→observed 本端 wire→全 terminal identity。41 方法、92逆序、154重复等只属于原审者历史运行，本轮未重跑。

- 37 ID 全部绑定旧 oracle 的 datasetId、input projectionSha、parameters、sourceRefs；source case/expectedProjection 子树 SHA、authority、finiteRelations、preconditions、pending、API、harnessStage 和两件 explicit invocation 逐项核同；24 个 proposed diagnostic 对象与固定源精确相同。
- 37/19 datasets，10 legacy 正常+3 scope 正常+24 拒绝。与旧 pending 交集 36，另一个 `legacy/unbound-head` 是原 specified，剩余 101 pending 不被外推关闭。没有把 legacy 域 11 ID 当 11 正常。
- 全 137 pending ID 集与原 oracle 相等，逐项完整有序 pendingFields 对象相等，closed 全 false，status 全 pending。原 oracle 仍 417、280 specified/137 pending、wholeOracleComplete=false。
- 独立按 JSON 字段枚举 **graph 子集**，与 85 登记槽的 ID/path/mode 多重集相等；各槽 rowCount 和完整子树 hash 核同。ordered RDF occurrence 不是 graph 槽，保留完整顺序/重复/共享身份门，不能把 85 当所有 RDF 位置数。
- 10 个 legacy math 与旧 expected.math 全对象相等；3 个 scope math 仅在另列 semanticState/reasoningReceipt 门后相等。旧 asserted receipt=null，fresh/project 保“同次 freshly returned reasoning_result/provenance.reasoningSource，不能值等副本”的关系。
- 只有 shape/front-2 和 integer/other-datatype-1 带完整 invocation；其余 35 的实际 caller/default 证据仍缺。14 held A1 有真实先前生产/expectation/allocation/资源准入前提，未达保原首错及 pending，未冒深 DAG 覆盖。
- 私有 display/content-source 不是旧 metadata authority/入参或公共四字段 ErrorFrame。raw/source/null/词法/摘要 exact、全域 BNode、一端 wire 与数学身份分门、真实来源/发行/费用/完整阶段缺口均在接收账保留，没有设计当实施的问题。

### Backlog、六包和提示

26 项保持 21 技术阶段+E1–E4+当前 pure docs；queueIncluded 全 true。逐项两模型的 taskId、actualSettings、actualTerminal、reportPath 全 null，requiredSettings 分列；没有用缺同名报告断言应用全历史从未审。源内审、FR505旧16例、IRI74失败、graph四红、date两首失败和明确修复/撤回后继均保留；原通过不自动移用，未实现原验收不因 not-ready 消失。

独立解析/核验 backlog 中 **50 个实际 commit refs、60 个唯一固定 Git 文档证据身份**；各 product parent/delta paths 与 Git 相等。另一个 ZIP 身份仅保 metadata，不打开内容。该数量是本审者实际核的定点范围，不复述作者研究的56 refs/101元数据为自己的全量结果。

六包完整树按固定 ref 全 6390 元数据项核对，需显式 C-quote 反解才相等，见 R1-02。声明的 engineering 1087 个 current 文件 occurrence 逐件等固定 Git bytes/SHA；当前唯一 blob 311，连同主历史工程范围带 SHA 的条目合并为 326 个唯一 blob，均已核。**此通过仅针对声明 selector，不能抵消 R1-01。**

主矩阵 21 个有固定实现/设计 ref 的 full continuation ranges×六目标包的同/改/缺分类，在声明路径集合内逐件正确；无固定实现范围的五行继续保留。补充 17 个命名历史 ref 的 actualParent、delta 成员及 path/blob/size 与 Git 相等。无跨分支拼接运行候选，没有由同字节/祖先自动弃用 T05-01、早期 graph 或旧 oracle。

12 提示的绝对 receiving 根、各包源码树/branch/base/source/tree、完整清单路径、独立报告唯一写面、两模型要求设置均与 index 相等。共同正文要求完整源码/工具/测试/fixture/原验收/失败，不只修复 delta；实际任务设置和终态需另读回。保持独立意见、历史失败、静态范围和运行缺证、不代跑 HOLD/未签 caller、M ZIP 内容限制及 root 短 lease；未发现提示扩大运行授权。因为 R1-01/R1-02，**包完整性声明需修复后再冻结**，本轮不建议直接以现有完整覆盖标志结项。

## 实际命令与非零披露

所有下列核对 cwd 均为固定 worktree。`python3 - <<'PY'` 是本轮实际工具调用的标准库静态核对代码，不 import 任何仓库模块；原命令/输出在本审工具记录，本文是准确摘要，不伪称另有原始 stdout/stderr 文件。

| 实际 argv/调用族 | 实际结果与含义 |
| --- | --- |
| `cat AGENTS.md <三件root外控绝对路径>` | exit 0，全文读取规则 |
| `git status --short`、`git rev-parse HEAD` | exit 0，candidate 身份与保护 M |
| `cat`/`sed -n` 人读文档；Python JSON 全量解析/逐项读取 | exit 0；大组合打印曾截断，后续以分段及共同文本/差异核对补齐，不称所有大型 JSON 全文打印可见 |
| `git show <fixedRef>:<path>` / `git cat-file blob/-s/-t` / `git rev-parse ref:path` / `git diff --name-only` / `git diff-tree` | 成功核 fixed source、manifest、旧件、refs、parent、声明矩阵字段；未跑算法 |
| `git ls-tree -r -l -z <六固定refs>` | exit 0；发现 73 条 path 编码问题；独立显式解码后全树 metadata 核同 |
| Python manifest/hash/旧件、37/137/85/13math、1087工程 occurrence、21 ranges×6、17补充refs、12提示核对 | 最终各对应核对 exit 0；声明 selector 外缺口另报 P2 |
| `git diff --check 77852d27a3c4e84867a42f243e0f4e0f32b8df67 de301e1dcd8c862ed43db383a02d12543e62898f` | exit 0，仅新 docs delta |

本审自己的非零探索也保留，不称所有命令 exit 0：一次 `rg` 误用不存在的 `docs/reviews/T05/source-package-oracle/tools` 目录 exit 2，后改读实际固定脚本；一次静态 Python 错用 oracle 字段 `status`，KeyError exit 1，改为真实 `oracleStatus` 后相同 pending 核对通过；一次完整树 path 集 AssertionError exit 1 揭示 R1-02；后续合并静态脚本在完成1087 current核对后，误以为纯设计每条均有 sha256，KeyError exit 1，改按实际字段分 metadata/hash 两层后完成；一次把 ordered RDF sequence 也放入85 graph-only登记的比较，AssertionError exit 1，改为明确 graph 子集后多重集核同。这些均未改输入、未执行产品，不伪装为模型失败或新原始流。

作者 CSV BOM KeyError exit 1/utf-8-sig 更正 exit 0 的载体、研究者原 inventory 路径定位错误、I05 历史 full diffcheck exit 2 的限定都仍存在且没有被新局部 exit 0 覆盖。

## 处置与最终限制

R1-01、R1-02 均 **Open**。应先保全本 Fail，再由唯一 owner 在原授权两个新前缀修订成新 candidate，更新清单/矩阵/提示相关完整性描述，独立复核实际改动；不改本候选或本报告求绿。本轮没有需要重跑未变化产品检查的理由，也没有新的运行授权。

R3 设计收件及旧137差距保全可作为规划输入；完整发审准备在两项 P2 关闭前仍为 Fail。所有 designated actual IDs/settings/reports、运行/打包/平台/生产、完整 caller/source/费用/issuer/capture/17L、正式 Job/Store/selected/wholeH、S1/B1/CI两OS/真人/develop、417及父P0门继续依原证据保持未关闭。报告最终 bytes/SHA由落地后的独立文件 hash 回读及交接消息给出，不自含自身 hash。
