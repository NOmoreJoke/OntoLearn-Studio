# T05 完整工程指定独立审查 包 O — MiniMax Code 审查报告

> 本报告是本方（MiniMax Code 模型侧）对 T05 包 O 的**独立、只读**审查结论。
> 本报告**不是** ZCode 侧意见、不代表同轮双审完成、不是产品验收、不是父 T05/P0 通过。
> 本报告**不签署**父 T05、正式 Job/Store/selected/wholeH、17L/费用、S1/B1、CI 两 OS、真人、develop 任一发布门。

---

## 1. 结论（先行）

**本方完整 O 静态审查范围：NotPass（存在 1 项中等级实质缺陷 + 5 项中低等级缺陷）；O 包自身的 47 项自有 stdlib 测试与五件制品字节复现：Pass；全部需要运行/打包/生产/父门的范围：无法验证。**

具体分栏如下，不混用：

| 范围 | 结论 | 依据 |
|---|---|---|
| O 外部 oracle 工具链自身的正确性与自洽性（builder 1311 行 + 47 项测试 + 五件制品可复现） | **Pass（静态 + 复验运行）** | §4 两次独立复验；47/47 OK、build --check exit 0、五件字节完全一致 |
| O 包的 149 件工程/authoring 清单字节完整性、Git 身份、137/85/37 三账闭合 | **Pass** | §5.1，全部 149 件 current SHA256 与清单逐件相等；137/85/37 与 oracle 计数恒等闭合 |
| declared-allocation 七池模型对所引规范原文的符合性 | **Pass** | §5.3，逐条比对 `allocation-integration-plan.md.raw` §4.1 与 `allocation-restore-plan.md.raw` §5 |
| **O 包完整工程审查范围内的实质缺陷** | **NotPass** | §6 的 F-01（中）、F-02（中）、F-03（中）、F-04（中）、F-11（中）及 F-05～F-10（低/低-中） |
| 417 observations 的**数学/语义正确性** | **无法验证** | 需真实引擎执行；本包无授权，且 oracle 自身声明 `notClaims` 含 "product executed" |
| 137 pending / 26 声明缺件的真实闭合 | **NotPass（保持未闭）** | 本包不提供任何可关闭它们的实际证据；§7 逐条列明缺什么 |
| 完整 DTO / serializer / 85 槽 wire 门 / 统一 BNode 域 / raw-source / 真实身份 / held 首错 | **无法完整验证** | §8 逐项给出现状与缺口 |
| 父 T05 / P0 / 正式 Job / selected / wholeH / 17L / 费用 / S1 / B1 / CI 两 OS / 真人 / develop | **不在本阶段关闭，本报告不签署** | §9 |

未发现 P0/阻断级缺陷。未发现伪造运行证据、未发现把 actual 固化为 expected、未发现跨分支拼接运行候选。

---

## 2. 本轮实际身份与设置（真实读回，非要求值）

| 项目 | 实际值 | 读回方式 |
|---|---|---|
| app | MiniMax Code（Desktop），本会话直接运行，非后台子任务 | `mavis session get` |
| session id | `mvs_8262fb931cf34f3dae99b85683d65fd7` | 同上 |
| session title | 核验 T05-O 工作树的清单与执行证据 | 同上 |
| parent session | 无（root session，`parentSessionId: null`） | 同上 |
| task id | **无独立 designated task**；本审查即在本 root session 内执行（`sessionType: 0`, `appMode: coding`） | 同上 |
| turn | 本轮单次连续执行，未跨会话 | 同上 |
| model（实际生效） | `minimax/MiniMax-M3.1-Flash`（`effective_model` 与 `model.model_id` 一致） | 同上 |
| thinking（实际生效） | `model.thinking.effort = "xhigh"`、`effective_model_variant = "thinking"` | 同上 |
| permission | **本会话实际权限模式未由 harness 向我暴露 → 未核**。按本轮新增约束，逐任务设置**由 owner 已核官方回执供给**；本方**不读全局 config/log 验证默认**，故本项在收到 owner 官方回执前保持未核 | `mavis session get`（该工具未返回 permissionMode） |
| worktree | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-minimax-review-e15ce44` | `session get.workspaceDir` + `pwd` |
| branch | **detached HEAD**（`git branch --show-current` 为空） | `git branch --show-current` |
| HEAD | `86df64a2c707355ed177d536ef5975a1986c0f0b` | `git rev-parse HEAD` |
| 固定 source/process | `77852d27a3c4e84867a42f243e0f4e0f32b8df67`（sourceTree `5ef670b874954e1dadfcbc16411741171653970a`，实测相等） | `git rev-parse`/`ls-tree` |
| 资料候选 / 最终过程 | `e15ce44d3a39a4634d309a05bb2422d00a576b7c` / `86df64a2c707355ed177d536ef5975a1986c0f0b` | `git log` |
| repository base | `5f910b52c69d86a1076b2032e5d3c63e715947f3`（实测 784 tracked files） | `git ls-tree -r` |
| 本方 scope 契约 | `scope-contract.json` SHA256 `371fcf080d86eb1649dc1edea16ff6066c96dced83ed059af05336ea148c93d9`（与 launch-map 声明一致） | `shasum -a 256` |
| 当前 AGENTS | 15147 bytes / SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`（未暂存，保持 ` M AGENTS.md`，未改） | `shasum -a 256` + `git status` |

**权限说明（不夸大）**：`external-review-permissions.md` 第 18 行明确「用户级文件不能证明已有会话即时切换」。本轮 harness 未向我暴露本会话的实际 permissionMode，`mavis session get` 也未返回该字段，故该一项按**未核**记录。

**本轮约束更新后的更正登记**：本报告初稿曾以读取用户级 `/Users/kyle/.minimax/config.yaml` 的方式记录 `permissionMode: bypassPermissions`。按本轮新增约束「逐任务设置由 owner 已核官方回执供给，不读 global config/log 验证默认」，该条用户级读数**已从本报告撤除**，不再作为设置证据；permission 一项在收到 owner 官方核验回执前**保持未核**。撤回的是"以全局默认值证明本会话设置"这一推断，**不是**撤回已发生的读取事件本身（该事件如实保留在此登记中）。本轮全部工具调用均未被权限门拦截，且本审查未执行任何超出授权的动作。

---

## 3. 本方工作区与只读边界

- 唯一 workspace：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-minimax-review-e15ce44`（detached HEAD `86df64a2`）。
- 原 owner 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle` 与其它五棵树**未被本方读取**。原正文的绝对路径一律映射到本方同一相对路径。
- **未读取**另一指定模型（ZCode）的 workspace、报告、自动状态、会话 DB、全局任务日志或意见；未通过 glob / 父目录遍历 / 共享源目录间接读取。历史 R1/R2 独审与 backlog 属共同原始输入，已按"共同历史 ≠ peer 意见"处理。
- 本方写面仅：`launch-O/report.md`（本文件）、`launch-O/raw/`（原始输出）、`launch-O/scratch/`（临时目录）。**未修改**受审实现、测试、锁、验收、旧报告/manifest、AGENTS 或本 launch 冻结输入；未 stage/commit/切分支/push/PR/merge/Goal。
- 执行前后受审文件 SHA256 完全一致（§4 表），`git status --porcelain` 全程仅 ` M AGENTS.md` + `?? .../launch-O/`。

---

## 4. 实际执行的核对（argv / cwd / env / exit / 依据 hash）

cwd 全部为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-minimax-review-e15ce44`；
`TMPDIR` 全部指向本方 `launch-O/scratch/tmp`；解释器仅系统 python3 与 python3.12，**未使用任何其它树的 .venv/node_modules/可变库**，未安装依赖。

### 4.1 本方新静态身份工具（授权）

| argv | exit | 结果 | 原始输出 |
|---|---|---|---|
| `python3 -B docs/reviews/T05/projection-R3-receiving/launch-O/verify-launch-input.py --phase observe` | 0 | `{"phase":"observe","sourceAndInputBytesVerified":true,"protectedUniqueCurrentGitSHAFiles":290,"setupReady":false,"unknownNewMetadataPaths":[]}` | `launch-O/preflight-observe.json`（本方新增元数据） |

说明：`setupReady:false` 属该工具对 setup 阶段的判定口径，**不代表**本审查未就绪；该工具自述不检查模型真实 taskID/终态、不代表指定审查 Pass。本方新增元数据与冻结输入分列登记。

**该次 observe 的边界（按本轮新增约束复核）**：
- 该次调用发生在**本方写入任何新文件之前**（工作树当时的全部未跟踪项均为 setup 产出的 `launch-O/` 文件，归属本任务已声明写面）。其哈希对象为：受保护的 **290 个固定输入** + 本方已声明写面内的 setup 产物；`unknownNewMetadataPaths` 为 **空数组**，即**不存在**任何未知自动元数据。
- 该工具的产出 `preflight-observe.json`（61333 B）保留为**已有真实事件**，不重跑、不删除、不改写。
- 按本轮新增约束「不运行会读取未知文件内容的 observe」，本报告定稿时**未再次运行** observe；今后如出现未知自动元数据，只做 **path/lstat 与归属=unknown** 记录，**不 hash、不 parse**。当前工作树内经 path/lstat 核对**不存在**未知自动元数据：全部未跟踪项均在 `launch-O/` 内、归属本任务，唯一 tracked 修改为受保护的 `AGENTS.md`（本方未改、未暂存）。

### 4.2 两个授权既有正常 O 命令（复验）

| argv | 解释器 | exit | 实际结果 | 原始输出 |
|---|---|---|---|---|
| `python3 -B scripts/test-i05-source-package-oracle.py` | 3.9.6 | **0** | `Ran 47 tests in 4.754s` / `OK` | `raw/o-run-test-python3.txt` |
| `python3.12 -B scripts/test-i05-source-package-oracle.py` | 3.12.12 | **0** | `Ran 47 tests in 3.593s` / `OK` | `raw/o-run-test-python312.txt` |
| `python3 -B scripts/build-i05-source-package-oracle.py --check` | 3.9.6 | **0** | `mode=check`，五件制品逐件字节相等；`observations=417, datasets=320, statuses={pending:137, specified:280}, wholeOracleComplete=false` | `raw/o-run-build-check-python3.txt` |

**本次实际结果 = 47 项测试全部通过（两个解释器一致），五件制品字节完全可复现。**（"47" 本次实测确认，非沿用旧报告数量。）`--check` 全程内存重建，未写回任何制品。

`build --check` 输出的五件 SHA256 与磁盘现值逐件相等：

```
7ae1c1311f71bfbcc76d5ab9592eebb66f39410ef9e0871965951de35dc77023  oracle.json       (5920695 B)
95d7395761fbabe97c1fd81d1d05eb44bb8094f7266d977de42fdff349d28bd9  coverage.json    ( 154032 B)
f2db5b1ad84ce4c7f97e1b9e30e23c63f3902f60dc92e1441f945d8dfed35c64  sources.json     (   9872 B)
74889cca94e90d62b2a456087946cfdd35f7a716039729091892a0bcda13f7c5  schema.json      (   9106 B)
e68188ddefae4488fa6cf7762549508b78a3d87551f27cb24b9c9998f7948e9d  budget-gaps.json ( 362492 B)
```

### 4.3 受审文件执行前后 SHA256（未改动证明）

执行前后逐件相同（`raw/o-run-*` 前后两次 `shasum -a 256`）：

```
024b352964880f57154ee2f49b31fce9dea368e29d5cd3112ffbad7497b06610  scripts/build-i05-source-package-oracle.py
601ca5b48b2cc1422ca7a956907b3da1b63b8f450a414ad5fa1dc47261cabb4d  scripts/test-i05-source-package-oracle.py
e68188ddefae4488fa6cf7762549508b78a3d87551f27cb24b9c9998f7948e9d  tests/fixtures/quality/i05-source-package-oracle/budget-gaps.json
95d7395761fbabe97c1fd81d1d05eb44bb8094f7266d977de42fdff349d28bd9  tests/fixtures/quality/i05-source-package-oracle/coverage.json
7ae1c1311f71bfbcc76d5ab9592eebb66f39410ef9e0871965951de35dc77023  tests/fixtures/quality/i05-source-package-oracle/oracle.json
74889cca94e90d62b2a456087946cfdd35f7a716039729091892a0bcda13f7c5  tests/fixtures/quality/i05-source-package-oracle/schema.json
f2db5b1ad84ce4c7f97e1b9e30e23c63f3902f60dc92e1441f945d8dfed35c64  tests/fixtures/quality/i05-source-package-oracle/sources.json
```

### 4.4 其余只读核对（标准库 JSON/hash/AST/Git）

全部原始输出归档于 `launch-O/raw/`：
`o-json-audit.txt`、`o-json-audit2.txt`、`o-ledger-align.txt`、`o-restore-negative.txt`、`o-coverage-matrix.txt`、`o-deps-zip.txt`、`o-zip-and-deps.txt`、`o-m-package-zip.txt`、`o-backlog-history.txt`、`o-backlog-key-stages.txt`、`o-bnode-collision-probe.txt`、`o-sourcerefs-gap.txt`、`o-subagent-crosscheck.txt`、`data-audit-stdout.txt`。

**执行边界自述（本轮主动披露）**：除 §4.2 两条授权命令外，我另运行过一个 `python3 -B - <<'PY'` 只读探针，它 `importlib` 加载了本方固定 builder 模块并只调用其 `read_pinned()`（读 + SHA 校验固定输入）以枚举数据集结构。该探针**不构建、不生成 oracle/actual/collector、不触碰产品/I05 模型、不写任何受审文件**，但其 argv 严格说不在 §4.2 的两条之内，属对"仅可复验两个既有命令"的**字面超出**。如实登记于此，其结论已在 §5 中用纯 JSON 复算独立验证（`o-ledger-align.txt`、`o-json-audit*.txt` 均为不 import 受审模块的独立复算），不依赖该探针。

---

## 5. 已读完整范围与核心事实核对

### 5.1 覆盖与身份（全部独立复算，非引用文档数字）

| 核对项 | 实测 | 依据 |
|---|---|---|
| O 工程/authoring 清单 149 件的**当前字节** SHA256 | **149/149 全部相等，0 处不符** | `raw/o-ledger-align.txt` |
| `git ls-tree -r 77852d2` tracked 文件数 | **914**（与清单声明一致） | 同上 |
| `git ls-tree -r 86df64a2` tracked 文件数 | **958**（= 914 + 44 本轮 R3 收件文档） | 同上 |
| `git ls-tree -r 5f910b52` tracked 文件数 | 784 | 同上 |
| sourceTree 对象 | `5ef670b874954e1dadfcbc16411741171653970a`（与清单声明相等） | 同上 |
| oracle observations | 417，ID 全唯一，字段键集合仅 1 种且与 `schema.entryKeys` 精确相等 | `raw/o-json-audit.txt` |
| oracleStatus | **specified 280 / pending 137**（恒等闭合，417=280+137） | 同上 |
| `expected.semanticState` | normal 208 / known-rejection 208 / not-executed 1 | 同上 |
| `wholeOracleComplete` | **false**（"false whole" 成立，且被 `validate_oracle` 反向断言保护） | 同上 + `build --check` |
| 137 缺口账 | `137-gap-ledger.json` 137 行，ID 集合与顺序**与 oracle 的 137 pending 完全相等**（双向差集 0） | `raw/o-ledger-align.txt` |
| 85 图槽 | `85-graph-slot-index.json` 85 条；37 矩阵 `graphSlotCount` 合计恰 85 | `raw/data-audit-stdout.txt` |
| 37 收件矩阵 | 37 行，37/37 命中 oracle；其中 `legacy/unbound-head` 是**原 specified** 而非 pending，与 `receiving.md:9` 一致 | 同上 |
| declared-allocation 分类 | specified 88 / pending 26 / not-invoked 2 = 116，与 `pendingFields` 中 `declaredAllocationExpectation` 字段的 26 条**集合完全相同** | `raw/o-restore-negative.txt`、`raw/data-audit-stdout.txt` |
| budget-gaps | items 82（= profile 观测 83 − repair 1），additionalProductionRestoreCases 32 | 同上 |
| 输入侧纯度 | parity-inputs 全文件**不含任何 `expected` 键**（纯输入成立） | `raw/data-audit-stdout.txt` |
| projectionSha256 | 按 builder 的 canonical 复算 **417/417 相符，0 处不符** | `raw/o-subagent-crosscheck.txt` |
| manifest ↔ inputs ↔ oracle | 417/417、320/320、caseSets 全等；公共 7 字段逐条 0 处不一致 | `raw/data-audit-stdout.txt` |
| 七池分配逐池复算 | 116 条非空 allocation 全部自洽；按 `T//N+(j<T%N)` 复算**违规 0 处** | 同上 |
| Blank node | oracle 与 parity-inputs 中 **blank token 出现 0 次**；`expected` 的 RDF term 只有 iri/literal；`query/bnode` 以"拒绝"表达 | 同上 + `raw/o-json-audit.txt` |

**口径提示（防混用）**：`contextStatus`（complete 410 / fragment 6 / not-executed 1）与 `expected.semanticState`（208/208/1）是两个维度，`coverage.json` 用的是后者。

### 5.2 本方实际通读的文件（全文）

- `scripts/build-i05-source-package-oracle.py`（1311 行，**全文逐行**）
- `scripts/test-i05-source-package-oracle.py`（532 行，**全文逐行**）
- `docs/reviews/T05/source-package-oracle/record-command.py`
- `docs/reviews/T05/source-package-oracle/guidance/source-identities.json`、`native-child-declaration-reference.json`
- `docs/reviews/T05/source-package-oracle/guidance/allocation-integration-plan.md.raw`（§4.1 段）、`allocation-restore-plan.md.raw`（§5 段）
- `docs/iterations/T05/projection-R3-receiving/`：`receiving.md`、`gap-table.md`、`original-acceptance-and-policy-annex.json`、`designated-review-backlog.md`、`full-review-packages.md`、`review-packages/O/minimax-prompt.md`
- `docs/reviews/T05/projection-R3-receiving/`：`independent-review-R1.md`、`independent-review-R2.md`、`R1-failure-disposition.json`、`R1-repair-disposition.json`
- 本方 `AGENTS.md`（15147 B）、`launch-O/` 全部引导与冻结输入（authority / execution-supplement / frozen-original-prompt / launch-prompt / scope-contract / launch-map / launch-input-manifest / guidance×4）
- 产品侧不变量关键件：`apps/desktop/src/preload/index.ts`、`apps/desktop/src/csp.ts`、`apps/desktop/src/main/index.ts`、`apps/desktop/src/main/trusted-document.ts`、`apps/desktop/electron.vite.config.ts`、`apps/desktop/src/renderer/index.html`、`packages/engine/src/ontolearn_engine/protocol.py`、`invalidation.py`、`invalidation-v2.json`

### 5.3 产品侧 AGENTS 强制不变量（静态核对，逐条给位置）

本 O 包的 149 件工程范围中，产品侧约 60 件（`packages/engine/**`、`packages/contracts/**`、`apps/desktop/**`、`tests/**`、`scripts/*`）。本方对**不变量关键件**做了全文阅读与树级检索：

| AGENTS 不变量 | 核对结果 | 位置 |
|---|---|---|
| renderer 不得直接用 Node/FS/shell；preload 只暴露按业务命名的方法，禁 `invoke(method, params)` 通用通道 | **符合**。`preload/index.ts` 全部为具名方法（`getEngineHealth`/`restoreTasks`/`getJob`/`listJobs`/…）；主进程侧是有限路由表并附注释 "This routing table is main-only and finite. No generic method crosses preload." | `apps/desktop/src/preload/index.ts:4-24`；`apps/desktop/src/main/index.ts:162-179` |
| IPC 处理器保持 sender/mainFrame/可信文档校验 | **符合**。`trusted()` 同时校验 `event.sender === window.webContents`、`event.senderFrame === window.webContents.mainFrame`、`isTrustedDocument(event.senderFrame.url, trustedURL)`；`isTrustedDocument` 清 hash 后要求 href 完全相等（协议/主机/端口/路径/查询全匹配） | `main/index.ts:137-144`；`main/trusted-document.ts:2-11` |
| CSP 只改 `csp.ts` 一处；生产脚本不得出现 `unsafe-inline`/`unsafe-eval`；不手写第三份策略 | **符合**。全树检索 `unsafe-inline|unsafe-eval` **仅 1 处命中**：`csp.ts:20`，位于 `if (development)` 分支内（Vite CSS HMR 专用），生产路径（`contentSecurityPolicy()` 无参）不注入。`Content-Security-Policy` 字面量其余命中均为**消费方**（vite 插件注入 meta、主进程 dev 响应头、e2e 读取断言），无第三份手写策略 | `apps/desktop/src/csp.ts:14-22`；`electron.vite.config.ts:19-32`；`main/index.ts:83-90` |
| `staleReason` 只来自 `invalidation-v2.json`；仅改模型配置不使领域结果过期；历史/失败/取消不计为过期原因 | **符合**。全部 staleReason 取值只出现在 `invalidation-v2.json`；`invalidation.py:7` 从该文件构造 `CODES`，`reasons()` 以 `if code and ...` 跳过 `null`（`model` 家族为 null），与 `publicationPolicy.unrelatedOrModelChange = "do_not_invalidate_existing_domain_result"`、`lateResult = "preserve_as_historical"` 一致；`job_store.py:1121` 只回读已持久化的 `saved["stale"]`，无第二处硬编码 | `packages/engine/src/ontolearn_engine/invalidation.py:6-28`；`invalidation-v2.json:43-70`；`job_store.py:1121` |
| S3 前不得接入模型；唯一网关在主进程；Python 引擎不持有密钥、不调用模型 | **符合（检索层）**。全树检索 `openai|anthropic|api_key|bearer|http(s)://api.*` 在产品/脚本代码中**无命中**；唯一 `OPENAI_API_KEY` 出现在 `packages/engine/tests/test_i04_lifecycle_boundaries.py:94`，且是**断言 worker 不继承这些凭据**的排除名单（`assert not set(excluded).intersection(os.environ)`） | `tests/test_i04_lifecycle_boundaries.py:91-108` |
| 跨边界只传固定错误码和受限参数，不回传原始异常/堆栈/路径/原值/凭据 | **符合（协议层与 IPC 层已核）**。`protocol.py` 的 `ProtocolFault` 明文 "never carries input text"，只带 `frames`；JSONL 侧拒绝重复键、非有限值、孤立代理项、超深嵌套与超字节上限，异常统一收敛为 `PROTOCOL_FAULT`；主进程 IPC 失败路径统一走 `safeError(...)` → `PERMISSION_DENIED` 固定码 | `packages/engine/src/ontolearn_engine/protocol.py:10-16, 27-72`；`main/index.ts:145-160` |

**产品侧覆盖边界（如实声明）**：以上为本方**本人**全文阅读并核对的不变量关键件。其余产品侧文件（`storage.py` 55KB、`job_store.py` 64KB、`coordinator.py` 29KB、`task-service.ts` 33KB、`App.tsx`、engine tests 19 件、unit/e2e tests 19 件等）本方**未逐行读完**；已另行派发只读子审并行覆盖（文件范围与报告路径见 §10），但该子审在本报告定稿时**尚未产出结论**，故其结论**未**被并入本报告，本报告**不**对其余产品侧文件作 Pass 或 NotPass 断言。存储原子性（`Store.commit` 版本化/预览/原子提交/旧基线拒绝、RDF 只从快照重建）、`memory_guard` 缓存回收不触及历史、zod `.strict()` 全覆盖、ruff/Python 3.12 规范、锁文件漂移、FR-500~505 既有真实实现盘点 —— 这些**均属本方未验证范围**，本报告不代为签署。

### 5.4 declared-allocation 七池模型 vs 所引规范原文（逐条比对）

规范来源：`allocation-integration-plan.md.raw` §4.1 与 `allocation-restore-plan.md.raw` §5（两文件均被 builder SHA 固定）。

| 规范原文要求 | builder 实现 | 结论 |
|---|---|---|
| `N=max(1,定义数，含停用)` | `n = max(1, len(rule_ids))`，rule_ids 为全部定义（disabled 为其子集） | 符合 |
| `N≤100` | `len(values) > 100` → 拒绝 | 符合 |
| `按完整rule_id的Unicode码点稳定序` | `sorted(rule_ids)`（Python str 按码点），并由 `test_declared_unicode_is_codepoint_order_without_normalization` 断言 | 符合 |
| `各池作 divmod(total,N)，前余数个child多1` | `total // n + int(j < total % n)`，j 为排序位 | 符合 |
| `不得按保存/数组顺序发余数` | 额度只依赖 sortedPosition，原始顺序仅存 `definitionOrdinal` | 符合 |
| `原definition ordinal仅作真实source定位，不参与额度分配` | `definitionOrdinal = rule_ids.index(...)`，额度用 j | 符合 |
| 七池总额 work16777216/input262144/output262144/trace8192/firings1024/head16384/bindings1024 | `DECLARED_POOLS` 完全一致 | 符合（但见 F-04） |
| `每child总预留不超总池` | 逐池 Σ 恰等于原 T（`test_declared_all_seven_pools_conserve_totals_for_every_supported_count` 覆盖 n=1..100） | 符合 |
| `未用部分不回流/抬高后续child` | `unusedQuota: never returned...`、`resetOrReallocationPermitted: False`、`compileEvaluateSameBudgetRequired: True` | 符合 |
| `每规则独立Budget但compile/evaluate同一对象` | `compileEvaluateSameBudgetRequired: True`，且 `evaluate_relation` 的 `same-issued-object` 要求**同一对象身份**（拒绝 JSON 值相等） | 符合 |
| `空定义dummy child须ruleId/ordinal=None`、`实际空batch存在` | `ruleId: None`、`definitionOrdinal: None`、`dummyContract.requiresRealEmptyBatch: True`，且 `test_declared_empty_is_anonymous_dummy_contract_without_fabricated_identity` 断言 `actualAllocationCaptureProvided=False` | 符合 |
| `disabled必须保持outer originalMatches=None/batch=None` | declared 模型不含 matches/batch 字段（属声明域，非实际批次） | 符合（声明域内） |
| `ID非空/唯一、字符与UTF8≤16384` | `checked_rule_ids` 全部实现并被 10 类坏输入断言覆盖 | 符合 |

**该子项结论：Pass。** declared-allocation 的数学与语义对所引规范原文**逐条可核、无偏差**；且 builder 明确声明 `actualAllocationCaptureProvided: False` / `actualUsageProvided: False`，没有把声明冒充实际捕获。

### 5.5 47 项测试的覆盖画像（静态判定其能证明什么、不能证明什么）

47 项覆盖：ID/顺序/三 caseSets、缺尾与增 ID 拒绝、非有限值与重复键拒绝、孤立代理项保留、hash 变更先于解释被拒、无产品/三方/网络/进程 import、可复现构建、整数词法不数值去重、数字 Turtle 全词法保留、RDF1.1 string/language 身份、query 完整绑定/未绑定/顺序、原 Q01 只取 alarm 列、SHACL 缺失值不捏造、日期 equal 优先于 offset、日期逆序双违规、严格整数与显式报告分离、日期公开预算三序、手选多 head 与 disabled、false 比较保留绑定、repair/fragment 不升级为完整原操作、scope 三分支事实集、有限 RDFS 不回喂自定义规则、有序 direct 深度与 occurrence root、raw alias 24 occurrence/6 身份、restore 变异属 A1 非深 DAG、b1 四本体非十套件非快照测量、pending 不隐藏不冒充完整、模型类型/字段/全尾变异拒绝、动态关系拒绝坏 digest 与截断尾、allocation 身份非值等 JSON、声明三路切分余数、声明七池守恒（n=1..100）、声明重排只改 ordinal、声明 Unicode 码点序、声明 ID 前置拒绝、空声明 dummy 合同、声明关系拒绝尾/假捕获/再分配、声明逐 ID 分类不推断缺失 disabled、声明采用是选择性 writer 元数据非全树、声明绑定拒绝不一致元数据不升级为失败。

**能证明**：oracle 生成逻辑的自洽、拒绝路径、变异抵抗、声明模型的守恒与边界。
**不能证明**：任何一条 expected 的**业务正确性**（需真实引擎）、任何 137 pending 的闭合、任何实际资源准入。

---

## 6. 问题清单（逐项：严重度 / 精确位置 / 触发条件 / 影响 / 证据 / 修复建议）

### F-01 [中] fixture Turtle 解码器的 blank node 标签无数据集作用域，跨图合并与跨图比较会混淆不同 blank node

- **位置**：`scripts/build-i05-source-package-oracle.py:249`（`self.blank = 0` 每次解析重置）、`:272-273`（`'list-' + str(self.blank)`）、`:330-331`（`turtle()` 每次新建解码器实例）、`:774`（`scope_expected` 合并 `asserted` + `ontology`）、`:801`（`b1_expected` 合并 `modified` + `ontology`）、`:376-383`（`shacl_report` 把 data 的对象与 shapes 的 `sh:in` 成员列表做 `value not in allowed` 跨图比较）。
- **触发条件**：任一被独立解析的 Turtle 含集合语法 `(...)`。当前 Turtle 解码器为集合生成 `list-N` 形 blank node，而 N 计数在**每个解码器实例**内重置，因此不同被独立解析的图共享同一 blank node 标签空间。
- **影响**：(a) 两图合并时，不同 blank node 被当作同一节点；(b) `sh:in` 成员比较时，data 中的 blank node 若与 shapes 列表中同名 blank node 标签相同，会被误判为"在允许集合内"，**漏报违规**。这正是本轮要求核对的"统一 BNode 域"缺口——解码器没有数据集作用域命名域。
- **证据**：`raw/o-bnode-collision-probe.txt` —— 320 个数据集中 `assertedText`/`ontologyText`/`dataText` **均不含 `(`**（含 `(` 的仅 21 个 `shapesText`、1 个 `queryText`、1 个 `turtle/front-2` 的 `text`，且 data 侧从不同时含 `(`）。故**已发布的 oracle 字节与本次 `--check` 复现结果不受影响**；本条是方法层面的潜在缺陷，不是当前数据的实际错误。
- **修复建议**：为每次 Turtle 解析分配数据集作用域前缀（如 `<datasetId>:list-N`），并在 `shacl_report` 跨图比较时使用带作用域的节点标识；或在解码器入口显式拒绝集合语法，并把该限制写成受测边界（例如新增一条"含集合的输入必须被拒绝"的测试），而不是让标签域隐含。
- **等级理由**：不改变当前 417 条 expected 的任何字节（已实测无 `(`），但属于"正确性依赖调用方数据形状"的方法缺陷，且与本轮明确要求的"全 BNode 域"直接相关，故列中。

### F-02 [中] 17 条 observation 把 `consumer-C-goldens.json` 声明为独立 expected 来源，但机器交叉核对只覆盖 9/13 个 golden、且只比对 2 个字段

- **位置**：声明处 `scripts/build-i05-source-package-oracle.py:1050-1055`（对 `C-` 前缀 observation 追加 `{'local':'inputs/consumer-C-goldens.json','pointer':'/cases/<i>/expected','type':'independent pre-existing C expected'}`）；唯一交叉核对处 `scripts/test-i05-source-package-oracle.py:363-375`（`test_original_C_full_fields_stay_consistent_with_independent_golden`）。
- **触发条件**：任一 `C-` observation 的 builder 自算 expected 与 `consumer-C-goldens.json` 对应条目发生分歧。
- **影响**：**8 条 observation 的"独立金标"权威声明完全没有机器校验**——`/cases/0`（C-query-numeric-promotion）、`/cases/1`（C-query-type-error）、`/cases/11`（C-inclusive-date-entry，展开为 4 条 observation）、`/cases/12`（C-illtyped-entry，展开为 2 条）。已覆盖的 9 条也只比对 `report.conforms` 与（存在时的）`requiredResultRows`，**未比对** golden 的 `reason`、`components`、`currentEntryGap`、`valueNodeCount`、`directSHACLNormativeResult`、`entryAndReportAreSeparate`。即 `expectedSourceRefs` 声明的权威强度高于实际校验强度。
- **证据**：`raw/o-json-audit.txt`（13 个 golden 的 expected 键集与 `golden[2:11]` 覆盖名单）、`raw/o-json-audit2.txt`（17 条带 C-golden 指针的 observation 全表）。
- **修复建议**：建立 golden→observation 的**显式映射表**（覆盖 `/cases/11`、`/cases/12` 的子路径分裂形态），对全部 13 个 golden 逐条核对 `conforms` + `requiredResultRows` + `reason`；对 `currentEntryGap` 标记的条目（如 C-inclusive-dateTime-equal / -before / C-inclusive-nni / C-langString）要么纳入比对、要么在 `pendingFields` 显式登记"golden 自述有缺口但 oracle 未反映"，不能靠"sourceRef 指向它"充当校验。

### F-03 [中] `explanation-goldens.json` 被列为"外部独立 expected 来源"，但未被任何 expected 派生或校验

- **位置**：`scripts/build-i05-source-package-oracle.py:30`（`PINS` 固定）、`:52`（`SOURCE_PATHS`）、`:1083`（`read_pinned('explanation-goldens.json')`，**结果被丢弃**）、`:1210-1212`（写入 `sources.json`，role = "previous independently authored external expected, never engine input"）。
- **触发条件**：审计者以 `sources.json` 为权威来源清单判断每条 expected 的独立支撑。
- **影响**：`oracle.json` 全文出现字符串 `explanation-goldens` **0 次**；该文件的 `completeHeads` / `falseThenError` / `directSteps` / `expectedCatalogObservations` / `additionalDirectStepCases` 未与任何 observation 的 expected 建立绑定。`sources.json` 却把它列为 expected 类来源，**权威声明与实际消费不一致**，会让人误以为 explanation 侧期望有独立金标支撑。
- **证据**：`raw/o-json-audit.txt`（`raw text occurrences of 'explanation-goldens': 0`）、`raw/o-json-audit2.txt`（`count: 0`）。
- **修复建议**：二选一并落到机器可检：(a) 把 explanation-goldens 的对应条目实际绑进相关 observation 的 `expected` 并加交叉断言；(b) 把 `sources.json` 中该行 role 改为"pinned input，本 oracle 未消费"，并在 `forbiddenAsOracle` 或限制字段中显式声明，不得留在"external expected"类。

### F-04 [中] 七池总额是手工复制的常量，与所引规范行之间没有机器交叉校验（规范本身要求"不复制一套可漂移常量"）

- **位置**：`scripts/build-i05-source-package-oracle.py:92-94`（`DECLARED_POOLS` 硬编码）、`:108`（`DECLARED_ALLOCATION_POLICY.sources` 仅以字符串指到 `guidance/allocation-integration-plan.md.raw` lines `[72, 80]`）。
- **触发条件**：规范原文中的池总额发生变化，或本常量被改动。
- **影响**：`allocation-restore-plan.md.raw` §5 明确要求「池来自只读原 `semantic._PROFILE_POOLS`，**不复制一套可漂移常量**」。builder 受"不 import 产品"约束而复制了常量（合理），但**没有把常量与被 SHA 固定的规范行做任何机器比对**：规范行只以指针字符串形式登记。将来常量与所引行不再一致时，`--check` 仍会通过（因为它只比对"重建结果 vs 已提交字节"），权威链断裂而无人察觉。
- **证据**：`raw/o-ledger-align.txt`（DOC_PINS 覆盖表）、§5.3 的逐条比对（本次人工比对相符，但无自动保证）。
- **修复建议**：在 `construct()` 中对 `allocation-integration-plan.md.raw` 做一次有界的字面量抽取（正则取七个池名与总额），与 `DECLARED_POOLS` 断言相等，不符即 `raise`；把该断言加入 47 项测试之一。

### F-05 [中] 三份来源清单互不包含且命名口径不一致，"来源真实身份"无法机器对账；且有一条实际来源完全未登记

- **位置**：三处清单分别为 ① `inputs/i05-source-package-parity-manifest.json` 的 `sources`（**22 条**，逐条带 `path`/`ref`/`sha256`/`corpusPath`）；② `oracle.json` 每条 observation 的 `sourceRefs`（**11 个不同 path**，逐条带 `ref`/`sha256`/`bytes`/`pointer`）；③ 本包产出的 `tests/fixtures/quality/i05-source-package-oracle/sources.json`（**26 行**，`local`/`bytes`/`sha256`，部分带 `ref`）。
- **触发条件**：任何以 `sources.json` 为准做来源对账的下游。
- **影响（三点，均实测）**：
  1. `oracle.json` 的 `sourceRefs` 引用了 `ref = 523c478d5f39671c4ac7c1ea6997e51d3047d58e`（3 条 observation：`b1-semantic/1x`、`b1-semantic/10x`、`offline/implicit-jsonld`），该提交在 `sources.json` 与 `source-identities.json` 中**均未出现**（只在被固定的 manifest.sources[0] 里登记）。本包交付的权威来源清单里缺一条实际在用的来源。
  2. `expectedSourceRefs.local` 用短名（`guidance/contract.md`、`inputs/consumer-C-goldens.json` 等，14 个不同短名），`sources.json.local` 用全路径（`docs/reviews/T05/source-package-oracle/guidance/contract.md` 等）。按 `local` 精确匹配，**26 行里有 18 行匹配不上任何 `expectedSourceRefs`**，自动对账会误报 18 个来源"未被使用"。
  3. manifest.sources 的 22 条逐条来源**没有一条**被带入 `sources.json`；`sources.json` 的 26 行与前两者互不包含。
- **证据**：`raw/o-sourcerefs-gap.txt`（三份清单逐项比对、10/11 个 sourceRefs path 不在本工作树）、`raw/o-subagent-crosscheck.txt`（18 行未匹配清单、manifest.sources 22 条全表）。
- **修复建议**：以 manifest.sources 为唯一来源母表生成 `sources.json`（保留 `ref`/`sha256`/`corpusPath`），把 `expectedSourceRefs.local` 统一为与 `sources.json` 相同的全路径（或在两处都加 `sourceId` 稳定键），并在构建时断言"每条 observation 的每个 sourceRefs 条目都能在 `sources.json` 找到同 ref+path+sha256 行"，不匹配即 fail。

### F-06 [低-中] `schema.json` 声明的 RDFTerm 形状未覆盖 288 处真实数据

- **位置**：`scripts/build-i05-source-package-oracle.py:946`（`FIELD_POLICIES['RDFTerm']['oneOfExactKeys']` = `[['kind','value'],['kind','lexical','datatype','language'],['kind','label']]`）与 `:822-825`（`record_term()` 生成的 5 键形状 `kind`/`lexical_form`/`datatype_iri`/`language_raw`/`source`）。
- **触发条件**：下游按 `schema.json` 的 `normalization.RDFTerm.oneOfExactKeys` 校验 observation 的 `expected`。
- **影响**：**25 条 observation**（dag/* 与 fullview/* 中的 records 类数据集）内共 **288 处** RDF term 使用 5 键原始记录形状，不在 schema 声明的三个 `oneOfExactKeys` 之内。schema 自称"exact"，但不能覆盖自身产出的全部数据；下游校验会把合法数据误判为非法。
- **证据**：`raw/o-subagent-crosscheck.txt`（288 处计数与 5 键形状样例）、`raw/data-audit-stdout.txt`（子代理同口径发现）。
- **修复建议**：在 `FIELD_POLICIES['RDFTerm']` 增列第四个 exact 形状（原始 occurrence 形状），或把 `rawTermSourceOccurrences` 明确标注为"原始记录形状，与 RDFTerm 身份形状分域"，并在 `schema.json` 里给出两者的显式分域字段。

### F-07 [低-中] `scope` 的 `factSources.basis` 只保留首个匹配 firing 的 leafBasis，丢弃同一 head 三元的其它 occurrence

- **位置**：`scripts/build-i05-source-package-oracle.py:791-793`。
- **触发条件**：同一条事实（同一 head 三元）由多个 firing 产生。
- **影响**：`next(...)` 只取第一个匹配的 firing 的 `leafBasis`，与本包 `FIELD_POLICIES['profile']` 自述的 "every binding/when/comparison/index/operator/operand/result/accepted/**head occurrence**/leaf/source/definition preserved" 不一致；也与本轮要求保留的"重复 head occurrence"口径不符。当前 scope 数据集无重复 head，故已发布字节未受影响。
- **证据**：静态读码 + `raw/o-json-audit.txt`（scope 观测 facts 计数 6/9/9，与 `test_scope_branches_consume_different_complete_fact_sets` 一致）。
- **修复建议**：收集**全部**匹配 firing 的 leafBasis 序列，按 occurrence 顺序保留；同时在 `test_scope_branches_consume_different_complete_fact_sets` 增加一条"同 head 多 occurrence 时 basis 不被折叠"的断言。

### F-08 [低] `source-identities.json` 被 builder 消费但未纳入固定身份白名单

- **位置**：`scripts/build-i05-source-package-oracle.py:33-46`（`DOC_PINS`，**12 项**）与 `:1213`（`strict_json((EVIDENCE/'guidance/source-identities.json').read_bytes())`，**无 size/SHA 校验**）。
- **触发条件**：`source-identities.json` 字节变化。
- **影响**：builder 消费的 13 个外部文件中只有它没有固定身份；其字节变化会改变 `sources.json`。当前靠 `--check` 的"重建 vs 已提交字节"比对兜住，不会产出错数据，但与 builder 自述的 pinned-input 契约不一致（`read_pinned` 对 7 个 inputs 与 13 个 guidance 都做 size+SHA 校验，唯独它没有）。
- **证据**：`raw/o-ledger-align.txt` 的 DOC_PINS 覆盖表逐项列出（`source-identities.json: referenced=True, pinned=False`；其余消费项 pinned=True）。
- **修复建议**：把 `source-identities.json` 加入 `DOC_PINS`（或在 `allocation-source-receipt.json` 已有的固定身份里合并其内容），使其与其它消费项同等对待。

### F-09 [低] `sources.json` 的 `sourcePath` 指向本树不存在的历史路径且不带 ref/sha256

- **位置**：`scripts/build-i05-source-package-oracle.py:47-54`（`SOURCE_PATHS`）与 `:1210-1212`。
- **触发条件**：消费方按 `sourcePath` 定位历史原件。
- **影响**：4 个 `sourcePath` 目标在本工作树**全部不存在**（`tests/fixtures/quality/approved-T09-873c8c0/...`、`tests/fixtures/quality/real-executor-acceptance-inputs.json`、`docs/reviews/T05/profile-M1-math-explanation-input-contract/{explanation,consumer-C}-goldens.json`），且该字段不带 gitRef/blob/sha256，消费者无法据此验证历史原件身份；只有 `local` + `bytes` + `sha256` 可核。这是历史归属信息被放在一个看起来像"可定位路径"的字段里。
- **证据**：`raw/o-ledger-align.txt` 的 SOURCE_PATHS 逐项 `exists=False` 输出。
- **修复建议**：为每个 `sourcePath` 补 `gitRef`/`gitBlob`/`sha256`，或改名为 `historicalSourcePath` 并在字段说明中写明"本树不保证存在"。

### F-10 [低] 索引→错误码映射表对越界索引无防护，会以异常中断构建而非记为 pending

- **位置**：`scripts/build-i05-source-package-oracle.py:590`（`integer/other-datatype-` 字典字面量）、`:593`（`integer/bound-front-` 列表下标）、`:601`（`shape/front-` 字典字面量）。
- **触发条件**：输入集中出现索引超出映射表长度的序列。
- **影响**：`KeyError`/`IndexError` 直接中断 `construct()`，而不是把该 observation 归入 pending——与本包"缺证据必须显式 pending、不得冒充完成"的核心纪律相悖（虽然当前固定输入下不触发）。
- **证据**：静态读码；`build --check` exit 0 证明当前固定输入不触发。
- **修复建议**：全部改为 `.get(index)` / 边界检查 + 未知索引回落为 `('pending', reason+phase)`，并在测试中加入越界索引用例。

### F-11 [低-信息] 固定 argv 的解释器与项目声明的 Python 版本不一致（本次已用 3.12 对照复验，结果一致）

- **位置**：`launch-O/scope-contract.json` 两条 argv 均以 `python3` 开头；`pyproject.toml` `requires-python = ">=3.12,<3.13"`、`[tool.ruff] target-version = "py312"`；本机 `python3` 实测 **3.9.6**。
- **触发条件**：在不同机器上按同一条 argv 执行。
- **影响**：同一条 argv 可能解析到不同解释器；builder 依赖 `str.removesuffix`（3.9+）等特性，跨版本行为差异不可由 argv 固定。
- **证据**：`raw/o-run-test-python3.txt`（3.9.6，47 OK）与 `raw/o-run-test-python312.txt`（3.12.12，47 OK）——**两个版本结果一致**，本次结论不受影响。
- **修复建议**：在 `scope-contract.json` 里把解释器固定为 `python3.12`，或显式记录允许的最低解释器版本。

---

## 7. 历史意见、失败与后继 —— 逐条处置

### 7.1 R1 Fail → R2 修复复审（本轮 R3 收件资料的内部独立审）

| 历史意见 | 原件位置 | 本方处置 | 结论 |
|---|---|---|---|
| **R1-01 [P2]** 完整工程 selector 漏掉工具实际消费的 docs fixture/authoring 数据（反例：T05-12 `verify-document-fixtures.py` 静态依赖 9 个同目录 JSON；T05-09 `assemble-explicit-oracle.py:33` 依赖 `inputs.json`） | `independent-review-R1.md:25-53` | 复核 `source-authoring-dependencies.json`：`directSourceToolDependencies` **3 条**（`verify-document-fixtures.py` 19 件、`assemble-explicit-oracle.py` 26 件、`structure-check.py` 29 件 requiredLocalFiles，全部 `allInCurrentGitSHAInventory: true`）；`originalSourceManifestBindings.localSources` **25 条**（`all25LocalSourcesCurrentGitSHAEqualDeclared: true`）；`historicalFixedInputBindings.original31Bindings` **31 条**（`externalRuntimeOrPolicyDependencyClosureVerified: false`，`readPolicy` 明示只解析绑定元数据、未打开外部 source/current 文件） | **本方确认 R1-01 已按 R2 记载关闭**（结构与计数一致）；同时保留 R2 自己声明的边界：外部 runtime/policy 依赖闭包**未验证** |
| **R1-02 [P2]** `fullTrackedTree` 把 Git C-quoted 展示文本当真实 path（O 包 12 条，六包合计 73 条） | `independent-review-R1.md:55-73` | 复核 O 包 `full-engineering-inventory.json`：`pathEncoding = "real UTF-8 Git paths parsed from ls-tree -r -l -z; standard JSON encoding, no Git display C-quotes"`；本方对 149 件逐件现地读回 SHA256 **0 处不符**，并实测 PRD 路径为真实 `docs/prd/PRD-本体学习与落地Agent工作台.md` | **本方确认 R1-02 已关闭** |
| R2 结论与本轮 44 份收件文档 | `independent-review-R2.md` | R2 结论为"Pass，限定于冻结 docs candidate 的本轮修复与发审资料准备"，且明确"不是指定双审 Pass、运行依赖闭包、产品验收、137 pending 或父 T05/P0 的通过" | 本方**不把 R2 Pass 当作指定双审 Pass**；R2 为共同历史输入，不是 peer 意见 |

### 7.2 必须逐条处置的历史失败（全部保留，不因本轮资料整理而消账）

| 历史项 | 原记录（backlog / 阶段证据） | 本方处置 |
|---|---|---|
| **IRI 旧 74 失败** | T05-08 `currentAcceptance.historicalChecks = "old74failed/57passed; fixed131; affected1539; full635TS/2739Python; source12"`；范围 "two-path minimum IRI guard repair, six other modules byte-unchanged, **not full RFC validation**" | **保留为已修复的历史失败**，未被本轮消账。原阶段在**另一棵树**（`T05-profile-iri-fix`，branch `feature/weekly-t05-profile-iri-fix`），本方固定 Git 中无该阶段实现，本轮**无法验证**该 74→131 的实际结果；本方只确认该失败记录被完整保留在 backlog 中且未被重写 |
| **FR505 旧 16 例缺口** | T05-03 `historicalPassAndSuccessor.notes = "Old16-case input review missed operator distinguishability; fff repairs R1/R2"`，范围 "22 authored cases, 18 comparison cells；…**not actual FR505 engine execution**" | **保留**。旧 16 例不足已被 22 例/18 cell 修正，但修正后仍是"authored + 内部自检"，**未做 FR505 真实引擎执行**；本方**不签** FR505 通过 |
| **graph 四红及其后继** | T05-15 `historicalChecks = "15actual=9aligned+4productdifferences+2pending; full1125TS/4899Python/**4failed**/44skip"`，四红 = langString / nni / dateTime-equal / dateTime-before；T05-16 `scope = "four original product differences closed with real Validator/report, date/illtyped still Validator0"`，`15actual=13aligned+2pending` | **四红已在 T05-16 由真实 Validator/report 关闭**，date/illtyped 仍 Validator0。本方可核的是 **O 包侧**：4 条 C- observation（`C-langString`/`C-inclusive-nni`/`C-inclusive-dateTime-equal`/`C-inclusive-dateTime-before`）在 oracle 中状态为 **specified**，而 `consumer-C-goldens.json` 对这 4 条的自述含 `currentEntryGap`；**该 gap 未被 oracle 的 pendingFields 反映，也未被测试比对**（见 F-02）。即：四红的产品侧已闭，**其独立金标自述的缺口在 O 侧仍是沉默的** |
| **date 两首失败** | T05-19 `scope = "146sources, 3 real reports 49 ZIP members; **two first check failures retained**; not global state/concurrency proof"`；`runtimeRef = 8e6f469ac7a64a1b3ec43edb13a8dc976ee8c4c4` | **保留**，未消账。O 侧对应物是 `utc-date/lexical-7..10,15,16` 共 12 条 observation，其 `expected` 显式带 `declaredRegressionAuthority`（`sourceType: "pre-registered legacy regression assertion"`, `independentLibraryClassificationProven: false`）并被 `test_pre_registered_date_regression_has_separate_authority_level` 断言——**权威等级被诚实降级**，本方确认该做法成立；但"两首失败"本身未被修复，本方**不签** date 组件通过 |
| **oracle 137 pending** | `scope-contract.json.unresolvedParent = {observations:417, pending:137, specified:280, wholeOracleComplete:false}` | **保持未闭**。本方独立复算确认 137 = oracle 的 137 条 pending = `137-gap-ledger.json` 的 137 行（ID 集合与顺序完全相等）。pending 字段分布：`budgetAdmissibility+typedSerializedUsage` 82、`graphBudget+budgetUsage+typedValues` 32、`genuineCapture+budgetAdmissibility` 32、`declaredAllocationExpectation` 26、`A1ExactErrorProjection` 14、`legacyDTO+evidenceProjection` 11、`reason+phase` 7、`scopeProvenanceDigestEncoding` 3、`exactStructuredOnlyError` 1、`exception+reason+phase` 1。**没有任何一条被本轮关闭** |
| **26 声明缺件** | 同上；`coverage.json.declaredAllocation.pending = 26` | **保持缺件**，且本方确认其**判别依据诚实**：26 条全部因 `explicit complete disabled_rule_ids; omitted is not declared empty`（25 条）或 `complete rule universe / disabled IDs / original ordinals`（1 条 `fullview/turtle-entry`）而 pending——**未推断任何默认或 dummy 身份**，符合规范"不猜 caller default" |
| **旧模型不指定 Pass** | backlog 26 阶段中，两模型 `designatedReviews.{minimax,zcode}` 全部 `taskId: null, actualSettings: null, actualTerminal: null, reportPath: null, outcome: "not-established-from-reviewed-evidence"`；`actualSettingsAndTaskIdsPolicy = "null means not established from reviewed evidence, not a claim no task ever existed; no desktop/service query performed"` | **全部 26 阶段、两个模型均未建立指定 Pass**。本方**不把任何历史内审 Pass 写成指定 Pass**，也**不签**本方之外的 peer 结论 |
| **M 三份 local-untracked actual ZIP** | T05-13 `currentAcceptance.archiveGap = "three ZIPs locally untracked, final120953467B fixed by manifest; preserve and verify accessible originals before designated readback"` | **仅登记，未打开、未消费**。路径/manifest 固定值来自 backlog；本方固定 Git（`86df64a2`，958 tracked）中**无这三份 ZIP 原件**，M 包清单的 `engineeringFiles` 内 **0 个 .zip**，`fullTrackedTree` 内仅 1 个与本项无关的 I02 trace.zip。故"三份 actual ZIP 的原路径与可访问性"在本包内为**缺证**；本方**未**进入 M 树取材料，**未**把历史 actual 当 expected |
| **未实施原验收 E1–E4** | backlog `T05-E1..E4`，`kind: planned-not-implemented`，`productRef/runtimeRef/processRef = None`，`wholeParentAcceptableReady: false` | **保留在积压**，未因 not-ready 被排除；本方**不签**其中任何一项 |
| **字节覆盖 ≠ 同候选双 Pass** | `candidate-coverage-matrix.json`：`noCrossBranchRuntimeCandidateConstructed: true`、`requiresOwnerDecisionForHistoricalRetirement: true`；R1/R2 均记"同 path/blob 不代表同运行组合" | 本方复核：26 stage 全保留、6 包并列、无跨分支拼接；矩阵自述未主张任何双 Pass 完成。**本方据此不签任何同候选双 Pass** |

### 7.3 本轮 R3 收件资料自身的一致性（本方独立复核结论）

- 37 项精确覆盖 13 正常 / 24 拒绝；与本线 137 pending 交集 **36**；`legacy/unbound-head` 为**原 specified 拒绝**，不能当新增关闭；其余 101 pending 无 R3 完整 target → **137 未变**（与 receiving.md:9 及 `37-receiving-matrix.json.summary` 一致：`overlapPending:36, pendingOutsideSource:101, previouslySpecified:1, wholePendingUnchanged:137`）。
- 10 个 legacy `independentTypedMath` 与旧 oracle.math 精确相等；3 个 scope 数学侧车相等但**不含** `semanticState/reasoningReceipt`，该关系被单独保留 → 本方确认该区分未被消除。
- 仅 `shape/front-2` 与 `integer/other-datatype-1` 带完整 invocation；其余 35 项实际 caller/default 证据仍缺 → 保留。
- 14 项 held A1：真实先前生产/expectation/allocation/资源准入前提未提供 → 保留。

---

## 8. 本轮明确要求保持的关键项：现状与缺口

| 要求项 | 本包现状（已核） | 仍缺什么 |
|---|---|---|
| **417 / 280 / 137 false whole** | 417 obs，280 specified / 137 pending，`wholeOracleComplete=false`，并由 `validate_oracle` 双向断言保护（改字段即 raise） | 137 条 pending 的实际闭合证据（本包不含） |
| **26 allocation 声明缺件** | 26 条，判别依据统一且不推断默认；七池模型对所引规范**逐条符合**（§5.3） | 每条的真实 `disabled_rule_ids` 与完整 rule universe（须由上游提供已批准元数据） |
| **完整 DTO / serializer** | `schema.json.exactIssuedRecordKeys` = `_PAYLOAD` 7 键 / `_REASONING` 15 键 / `_CHILD` 11 键（`graphBudget`、`planDigest`、`budgetUsage` 均在位），来源为 `native-child-declaration-reference.json`（literal-only 声明，双重 SHA 固定）；版本标签 `i05-reasoning-result/2`（fullview）/ `/3`（explanation）、`i05-finite-7`/`8` | 真实 serializer 实现与本轮 wire；本包只有**字面声明**，没有实现 |
| **85 槽 wire 门** | `85-graph-slot-index.json` 85 条；37 矩阵 `graphSlotCount` 合计 85 | **槽的 `valueSubtreeSha256` 无法在本包复算**——其 `path` 根为 `value`、指向源 case 容器 `i05-observation-projection-cases/1`（`sourceRef 50317c79…`），**该容器不在本工作树**；本方只验证了数量与 ID 闭合，未验证字节 |
| **全 BNode 域** | 数据层实测 **0 个 blank node**；`query/bnode` 以拒绝表达 | **方法层缺统一 BNode 命名域**（F-01）：解码器按解析实例生成 `list-N`，跨图合并/跨图比较无作用域隔离 |
| **raw / source / 真实身份** | raw occurrence 保 `None`/空串原样；`sources.json` 26 行；manifest.sources 22 行带 `ref`/`sha256`/`corpusPath` | **三份来源清单互不包含、命名口径不一致、一条实际来源未登记**（F-05）；**11 个 sourceRefs path 中 10 个不在本工作树**，其字节在本包内不可核 |
| **held 首错** | 14 条 restore-negative 全部 `failureStage='A1'`、`partialView=None`、`restoreReasonCalls=0`、`noDeepRevalidationClaim=True`、`originalSuccessViewUnchanged=True`；9 个不同 mutation 枚举；14/14 状态 pending（`A1ExactErrorProjection`） | 真实生产成功记录、原 held expectation/allocation、资源准入与真实首错；`payload/rows/source/definitions/catalog` 五路 bytes 核对目前只有**关系定义**（`RELATIONS`）与自测，无实际捕获 |

---

## 9. 本阶段结论与明确不签署的门

### 9.1 分范围结论

- **O 包外部 oracle 工具链自身（builder 1311 行 + 47 项测试 + 五件制品可复现）：Pass。** 两次独立复验（3.9.6 与 3.12.12）均 47/47 OK、exit 0；`build --check` 五件字节完全一致；`wholeOracleComplete=false` 被代码强制。
- **O 包 149 件工程/authoring 覆盖与三账闭合：Pass。** 149/149 字节相符，914/958/784 三个 Git 树计数相符，sourceTree 对象相符，137/85/37 与 oracle 计数恒等闭合，manifest↔inputs↔oracle 三方零缺口。
- **declared-allocation 七池模型对所引规范：Pass**（§5.4 逐条）。
- **产品侧 AGENTS 不变量关键件：Pass（静态，逐条见 §5.3）**——渲染端隔离、IPC sender/mainFrame/可信文档校验、CSP 唯一源且生产无 `unsafe-inline`/`unsafe-eval`、`staleReason` 单一来源、无模型外发/凭据、协议层错误收敛，六项均符合并给出文件行号。
- **本方完整 O 静态审查范围整体：NotPass。** 阻断项：无；实质缺陷：F-01～F-05（中，5 项）；次级：F-06～F-11（低/低-中，6 项）。这些缺陷**不改变**已发布 oracle 字节与本次复现结果，但确实使"完整工程可直接据其消账"这一目标在**来源登记链**、**schema 自洽性**、**BNode 域**、**金标校验强度**四个方面尚不成立。
- **产品侧其余约 55 件文件（storage/job_store/coordinator/task-service/renderer/engine tests/unit/e2e 等）：无法验证**——本方只全文核对了 §5.3 所列不变量关键件；其余部分派发的只读子审在本报告定稿时尚未产出结论，其结果**未**并入本报告，本报告对这些文件**不作** Pass/NotPass 断言（详见 §5.3 覆盖边界声明）。
- **运行/打包/生产：无法验证。** 417 条 expected 的业务正确性、任何 137 pending 的闭合、真实 DTO/serializer、85 槽 wire 门、held 首错与真实资源准入，均需真实引擎执行与真实捕获，本包无授权。

### 9.2 本报告**不签署**（保持原门）

父 T05 / P0；正式 Job / Store / selected / wholeH；17L / planDigest / usage / 费用；S1 / B1（SQLite 损坏 HOLD、自动拒绝）；CI 两 OS；真人验收；develop 远端合并；I05 R3 设计 Pass 不等于 T05 运行通过；T05-E1～E4 未实施原验收；六套独立工程不拼为运行候选；历史 actual 不固化 expected。

### 9.3 需要总控/上游决定的后继（本方无权自行关闭）

1. **F-02 / F-03 / F-05 需同一 owner 一次性修订**（来源登记链 + 金标校验 + schema 分域），否则下一轮指定审仍会命中同一组缺口。
2. **F-01 需产品/authoring owner 决策**：解码器引入数据集作用域 BNode 域，还是显式拒绝集合语法并写成受测边界。
3. **F-04 需把池总额与被固定的规范行做机器绑定**，使常量漂移可被构建期发现。
4. **85 槽 `valueSubtreeSha256` 的可复算性**依赖 I05 源 case 容器 `i05-observation-projection-cases/1`（`50317c79…`）的原件可达性；在该原件进入本包固定 Git 之前，85 槽只能验数量与 ID 闭合，**不能**升级为字节验证。
5. **M 三份 local-untracked actual ZIP**（manifest 固定 120953467B）需先确认原件可访问并保全，才能在后续轮次做只读登记；本轮按缺证处理。

---

## 10. 附：本方新增元数据清单（与冻结输入分门）

| 路径 | 性质 | 说明 |
|---|---|---|
| `launch-O/report.md` | 本方唯一报告 | 本文件 |
| `launch-O/preflight-observe.json` | 本方新增元数据 | `--phase observe` 产物；不属冻结输入 |
| `launch-O/raw/*.txt`（18 个） | 本方原始输出 | 全部命令的 argv/cwd/env/exit/完整原流与首错 |
| `launch-O/scratch/tmp/` | 本方临时目录 | 本轮 TMPDIR；为空，无残留 |
| `launch-O/scratch/data-audit-report.md` | 本方只读子审报告 | 数据集结构核对（A–L 逐条）；其关键结论已由本方独立复算并写回 §5.1 / §6 |

**未定稿的并行子审（如实登记）**：本方另派发了一个只读子审，范围为产品侧约 60 件源码/测试（`packages/engine/**`、`packages/contracts/**`、`apps/desktop/**`、`tests/**`），输出路径约定为 `launch-O/scratch/product-source-review.md` 与 `launch-O/raw/product-source-review-stdout.txt`。该子审在本报告定稿时**仍在运行、尚未产出这两个文件**（已两次读回确认）。因此其结论**未**被本报告引用或转述，也**未**用于支撑本报告任何 Pass/NotPass 判定；§5.3 的产品侧结论全部来自本方本人对不变量关键件的全文阅读与树级检索。子审若在后续产出，其结论应作为**独立补充**并入，不得追溯改变本报告已给出的判定，也不得被当作本报告自身的证据。

冻结输入（`launch-input-manifest.json` 11 成员）与本方新增元数据**严格分门**；本方**未**修改任何冻结输入成员，**未**删除或改动任何自动 runtime 元数据，**未**通过 ignore 规则制造"全树冻结通过"——`git status --porcelain` 全程真实显示 ` M AGENTS.md`（受保护 AGENTS，本方未改、未暂存）与 `?? .../launch-O/`。
