# T05 完整工程指定独立审查（包 O · MiniMax Code 模型侧）— 完整范围终稿 v2

- 交付件路径：`docs/reviews/T05/projection-R3-receiving/launch-O/final-v2.md`
- 审查对象：仓库 `OntoLearn-Studio`（本体学习与落地 Agent 工作台），O 包「完整工程/authoring」149 件清单
- 固定 O 源码/工具/expected：`77852d27a3c4e84867a42f243e0f4e0f32b8df67`
- 本树 detached HEAD：`86df64a2c707355ed177d536ef5975a1986c0f0b`；repository base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 本稿取代本方上一轮 `launch-O/report.md` 作为**唯一终稿**；`report.md` 原件**保留不覆盖**（本树实测 60824 B / SHA256 `78cdadc36894bcb52faceac5c22a98fb13a22becb4f0f3f7f22f7fae4f292b07`）。owner 另记录的两版（56586 B / `b145d9cb…`、58279 B / `d93c7603…`）与本树实测不一致，本稿按本树实测如实登记，不改写 owner 记录。

---

## 1. 结论（先行）

**本方 O 完整范围静态独立审查结论：NotPass。** 结论由实际证据决定，未以改判通过为目标；本轮续接不自动关闭任何既有 pending 或父门。

分范围结论（静态 / 运行 / 打包 / 生产 / 父门**分列**，互不替代）：

| 范围 | 结论 | 依据摘要 |
| --- | --- | --- |
| **A. O 包工具链自身（oracle builder / self-test）** | **Pass** | 两条授权命令实测 exit 0：47/47 OK；`--check` 五件字节相等、280 specified / 137 pending、`wholeOracleComplete=false` |
| **B. O 包 149 件工程/authoring 的静态审查（含本轮补完的约 55 件产品文件）** | **NotPass** | F-01～F-15 共 15 项缺陷（5 项中 / 5 项低-中 / 5 项低-信息）；其中 F-12 为本轮新发现的**确定性运行失败**（`scripts/verify-i01.py` 对当前 v2 协议必失败） |
| **C. 产品正式能力** | **仍只有 health** | `registry.json` `productRuntime=["health"]`；`v2Runtime` 14 项中 `job.create` 等业务方法在 `Coordinator.dispatch` 中仅 `test_mode` 下开放（`coordinator.py` `job.create` 分支） |
| **D. 真实运行 / 打包 / 生产验收** | **无法验证** | 本轮授权边界仅允许 O 工具链两条命令；`npm run check` / `test:e2e` / `package:dir` / 真人桌面 / 两 OS CI 均**未运行**，不得由静态结论代替 |
| **E. 父门（T05 / P0 / 正式 Job / Store / selected / wholeH / 17L / 费用 / S1 / B1 / CI 两 OS / 真人 / develop / 远端核验）** | **全部不签署** | 本轮无任何父门证据；137 pending、26 声明缺件、417/280/137 `false whole` 均**不因本次续接自动关闭** |

> 上表 A 的 Pass 仅指「O 自身的 stdlib 独立 oracle 能自洽地构建与自检」，**不等于** 417 条 expected 的业务正确性成立，更不等于 T05 父门成立。

---

## 2. 本轮实际身份、授权与只读边界

### 2.1 身份与权限证据（owner 本人 UI 回执，本方采信）

| 项 | 实际值 | 证据来源 |
| --- | --- | --- |
| 模型 | MiniMax-M3.1-Flash | owner 本人逐任务 UI 回执 |
| 思考等级 | xhigh | owner 本人逐任务 UI 回执 |
| 本任务权限模式 | 本人 UI「始终授权」 | owner 本人逐任务 UI 回执 |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-minimax-review-e15ce44` | 运行时上下文 + 本方 shell 实测 cwd |

本方**未**读取 global config/log、**未**扫描会话、**未**寻找全局替代设置（用户明确免读）。独立缺证项一律保留「未核」，不以推断补齐。

### 2.2 只读边界（本轮全程遵守）

- 未 stage / commit / 切分支 / 建 Goal / push / PR / merge / 支付 / 取密钥。
- 未修改任何受审实现、测试、fixture、配置、依赖、CI 或锁文件。
- 未运行会读取未知内容的 observe；未知自动 metadata 只做 path/lstat 并归属 unknown，**未** open / hash / parse。
- 固定声明输入（11 件冻结 launch 输入、290 件保护来源）只做 hash 与结构统计。
- 唯一新写面：`launch-O/final-v2.md`、`launch-O/scratch/`、`launch-O/raw/`。

### 2.3 本轮执行的两个授权命令（引用上一轮实测；本轮未重跑）

依据「无变化不重复测试」：本轮受审源码字节与上轮完全一致，**未重跑**。引用上轮实测结果，其原始流为**合并流**（`>>file 2>&1`，无独立 stderr 文件），此处如实标注，不补造独立流。

| 命令（cwd = 本 worktree，TMPDIR=`launch-O/scratch/tmp`） | exit | 结果 | 原始流位置 |
| --- | --- | --- | --- |
| `python3 -B scripts/test-i05-source-package-oracle.py` | 0 | `Ran 47 tests` / `OK`（解释器 3.9.6） | `raw/o-run-test-python3.txt`（**合并流**） |
| `python3 -B scripts/build-i05-source-package-oracle.py --check` | 0 | 五件字节相等；280 specified / 137 pending；`wholeOracleComplete=false` | `raw/o-run-build-check-python3.txt`（**合并流**） |

上轮另做过一次 `python3.12` 对照（同结果，`raw/o-run-test-python312.txt`，合并流）。本轮按用户授权不再新增对照。

---

## 3. 完整范围覆盖账（149 件，逐件四档）

**四档定义**（本方口径，与用户要求「逐行源码阅读 / 大 JSON 完整解析遍历分别记录」一致）：

- **L = 逐行读完**：本方（或上轮本方）把该文件全文逐行读过并据以形成判断。
- **P = 完整解析/遍历**：该文件是大型 JSON/数据件，本方用标准库做**完整 JSON 解析 + 全节点遍历 + 结构统计**（不是抽样），并据以复算；**未**逐行阅读其源码/字面。
- **S = 仅静态统计**：仅做 hash / 行数 / 体积级统计，未做内容级审查。
- **部分**：只读了其中明确定位到的部分，未覆盖全文（逐件列出未读区间，不以免责声明消账）。

**本轮真实进度说明**：上一轮本人已逐行读完 `packages/engine/src` 全部 15 件生产源码、`protocol.py`、`invalidation*.py/json`、`preload/index.ts`、`csp.ts`、`main/index.ts`、`trusted-document.ts`、`electron.vite.config.ts`、`renderer/index.html` 及全部 T05 文档/backlog/R1/R2；本轮由本人逐行补完上轮明确未完成的约 55 件产品文件（`packages/contracts/src` 5 件 + `contract_v2.py`、`apps/desktop/src/main` 6 件、`apps/desktop/src/renderer/src` 7 件、`packages/engine/tests` 19 件、`tests/unit` 15 件、`tests/e2e` 5 件），并逐行读 `scripts` 6 件 + `docs/reviews/T05/source-package-oracle/record-command.py`，完整解析遍历 `packages/contracts/v2` 8 件大 JSON 与 `tests/fixtures/quality/i05-source-package-oracle` 5 件 fixture。

### 3.1 覆盖统计

| 档位 | 件数 | 占比 |
| --- | --- | --- |
| L 逐行读完 | **124** | 83.2% |
| P 完整解析/遍历 | **20** | 13.4% |
| S 仅静态统计 | **2** | 1.3% |
| 部分（已列明未读区间） | **3** | 2.0% |
| **合计** | **149** | 100% |

**真实未读/未做（不消账）**：

1. `docs/prd/PRD-本体学习与落地Agent工作台.md`（1255 行）**未逐行读全文**。已读：全部章节标题清单；§7.6 FR-500～FR-505 全文；附录 C「MVP 能力矩阵」全文；附录 D.1 结果状态、D.2 依赖与失效规则表全文。未读区间：第 1～395 行（§0～§7.5）、第 1020～1255 行（附录 E.1～附录 G.6）。
2. `docs/reviews/T05/source-package-oracle/guidance/allocation-integration-plan.md.raw`（36922 B）：**仅逐行读规范行 L72–80**，其余为 I05 集成计划正文，未读。
3. `docs/reviews/T05/source-package-oracle/guidance/allocation-restore-plan.md.raw`（45463 B）：**仅逐行读规范行 L103–109**，其余为 I05 恢复计划正文，未读。
4. `package-lock.json`、`uv.lock`：仅 hash/体积统计（**S**），未做条目级依赖内容审查。
5. 三个只读子审（engine tests / unit+e2e+fixtures / contracts JSON+scripts+configs）**全部因瞬时网络错误失败**（`net::ERR_NETWORK_IO_SUSPENDED`、`net::ERR_NETWORK_CHANGED`），**零产出、零文件**。按用户「子审仍缺的部分由本人补足」的要求，其全部范围已由本人在本轮逐行/完整遍历补足；**未**以子审存在或启动替代覆盖。

### 3.2 逐件覆盖表


| 1 | `.github/ISSUE_TEMPLATE/bug.yml` | L |  |
| 2 | `.github/dependabot.yml` | L |  |
| 3 | `.github/pull_request_template.md` | L |  |
| 4 | `.github/workflows/ci.yml` | L |  |
| 5 | `.prettierrc.json` | L |  |
| 6 | `apps/desktop/electron-builder.yml` | L |  |
| 7 | `apps/desktop/electron.vite.config.ts` | L |  |
| 8 | `apps/desktop/package.json` | L |  |
| 9 | `apps/desktop/src/csp.ts` | L |  |
| 10 | `apps/desktop/src/main/engine.ts` | L |  |
| 11 | `apps/desktop/src/main/index.ts` | L |  |
| 12 | `apps/desktop/src/main/jsonl.ts` | L |  |
| 13 | `apps/desktop/src/main/task-service.ts` | L |  |
| 14 | `apps/desktop/src/main/trusted-document.ts` | L |  |
| 15 | `apps/desktop/src/main/view-navigation.ts` | L |  |
| 16 | `apps/desktop/src/main/window-recovery.ts` | L |  |
| 17 | `apps/desktop/src/main/window-security.ts` | L |  |
| 18 | `apps/desktop/src/preload/index.ts` | L |  |
| 19 | `apps/desktop/src/renderer/index.html` | L |  |
| 20 | `apps/desktop/src/renderer/src/App.tsx` | L |  |
| 21 | `apps/desktop/src/renderer/src/env.d.ts` | L |  |
| 22 | `apps/desktop/src/renderer/src/main.tsx` | L |  |
| 23 | `apps/desktop/src/renderer/src/style.css` | L |  |
| 24 | `apps/desktop/src/renderer/src/task-presentation.ts` | L |  |
| 25 | `apps/desktop/src/renderer/src/task-progress.ts` | L |  |
| 26 | `apps/desktop/src/renderer/src/tokens.css` | L |  |
| 27 | `apps/desktop/tsconfig.json` | L |  |
| 28 | `docs/iterations/T05/source-package-oracle/declared-allocation-delta.md` | L |  |
| 29 | `docs/iterations/T05/source-package-oracle/field-policies.md` | L |  |
| 30 | `docs/prd/PRD-本体学习与落地Agent工作台.md` | 部分 | FR-500~505 全文 + 附录 C + 附录 D.1/D.2 起始 + 全部章节标题；其余 1~395、1020~1255 未逐行读 |
| 31 | `docs/reviews/I02/round-2/minimax-runtime/i02-r2-mavis-extra-probe.mjs` | L |  |
| 32 | `docs/reviews/I02/round-2/minimax-runtime/i02-r2-mavis-nav-probe.mjs` | L |  |
| 33 | `docs/reviews/I02/round-2/minimax-runtime/i02-r2-mavis-nav-probe2.mjs` | L |  |
| 34 | `docs/reviews/T05/source-package-oracle/guidance/AGENTS-current.md` | L |  |
| 35 | `docs/reviews/T05/source-package-oracle/guidance/allocation-integration-plan.md.raw` | 部分 | 仅规范行 L72–80 逐行读；余为 I05 集成计划正文 |
| 36 | `docs/reviews/T05/source-package-oracle/guidance/allocation-restore-plan.md.raw` | 部分 | 仅规范行 L103–109 逐行读；余为 I05 恢复计划正文 |
| 37 | `docs/reviews/T05/source-package-oracle/guidance/allocation-selective-adoption.json.raw` | P |  |
| 38 | `docs/reviews/T05/source-package-oracle/guidance/allocation-source-receipt.json` | L |  |
| 39 | `docs/reviews/T05/source-package-oracle/guidance/contract.md` | L |  |
| 40 | `docs/reviews/T05/source-package-oracle/guidance/date-policy.md` | L |  |
| 41 | `docs/reviews/T05/source-package-oracle/guidance/directsteps-contract.md` | L |  |
| 42 | `docs/reviews/T05/source-package-oracle/guidance/legacy-date-declaration-receipt.md` | L |  |
| 43 | `docs/reviews/T05/source-package-oracle/guidance/native-child-declaration-reference.json` | L |  |
| 44 | `docs/reviews/T05/source-package-oracle/guidance/pre-registered-date-assertions.py.raw` | L |  |
| 45 | `docs/reviews/T05/source-package-oracle/guidance/pre-registered-date-source.json` | L |  |
| 46 | `docs/reviews/T05/source-package-oracle/guidance/q6-mechanism.md` | L |  |
| 47 | `docs/reviews/T05/source-package-oracle/guidance/q6-profile.md` | L |  |
| 48 | `docs/reviews/T05/source-package-oracle/guidance/semantic-boundaries.md` | L |  |
| 49 | `docs/reviews/T05/source-package-oracle/guidance/source-identities.json` | L |  |
| 50 | `docs/reviews/T05/source-package-oracle/guidance/window.md` | L |  |
| 51 | `docs/reviews/T05/source-package-oracle/inputs/consumer-C-goldens.json` | P |  |
| 52 | `docs/reviews/T05/source-package-oracle/inputs/explanation-goldens.json` | P |  |
| 53 | `docs/reviews/T05/source-package-oracle/inputs/i05-source-package-parity-inputs.json` | P |  |
| 54 | `docs/reviews/T05/source-package-oracle/inputs/i05-source-package-parity-manifest.json` | P |  |
| 55 | `docs/reviews/T05/source-package-oracle/inputs/product-cases.json` | P |  |
| 56 | `docs/reviews/T05/source-package-oracle/inputs/real-executor-acceptance-inputs.json` | P |  |
| 57 | `docs/reviews/T05/source-package-oracle/record-command.py` | L |  |
| 58 | `eslint.config.mjs` | L |  |
| 59 | `package-lock.json` | S |  |
| 60 | `package.json` | L |  |
| 61 | `packages/contracts/package.json` | L |  |
| 62 | `packages/contracts/python/contract_v2.py` | L |  |
| 63 | `packages/contracts/src/dependencies-v2.ts` | L |  |
| 64 | `packages/contracts/src/design-v2.ts` | L |  |
| 65 | `packages/contracts/src/index.ts` | L |  |
| 66 | `packages/contracts/src/states-v2.ts` | L |  |
| 67 | `packages/contracts/src/v2.ts` | L |  |
| 68 | `packages/contracts/tsconfig.json` | L |  |
| 69 | `packages/contracts/v2/binding-regressions.json` | P |  |
| 70 | `packages/contracts/v2/dependencies.json` | P |  |
| 71 | `packages/contracts/v2/errors.json` | P |  |
| 72 | `packages/contracts/v2/fixtures.json` | P |  |
| 73 | `packages/contracts/v2/frame-fixtures.json` | P |  |
| 74 | `packages/contracts/v2/registry.json` | P |  |
| 75 | `packages/contracts/v2/schema.json` | P |  |
| 76 | `packages/contracts/v2/states.json` | P |  |
| 77 | `packages/engine/entrypoint.py` | L |  |
| 78 | `packages/engine/pyproject.toml` | L |  |
| 79 | `packages/engine/src/ontolearn_engine/__init__.py` | L |  |
| 80 | `packages/engine/src/ontolearn_engine/__main__.py` | L |  |
| 81 | `packages/engine/src/ontolearn_engine/contract_probe.py` | L |  |
| 82 | `packages/engine/src/ontolearn_engine/coordinator.py` | L |  |
| 83 | `packages/engine/src/ontolearn_engine/invalidation-v2.json` | L |  |
| 84 | `packages/engine/src/ontolearn_engine/invalidation.py` | L |  |
| 85 | `packages/engine/src/ontolearn_engine/job_store.py` | L |  |
| 86 | `packages/engine/src/ontolearn_engine/memory_guard.py` | L |  |
| 87 | `packages/engine/src/ontolearn_engine/process_environment.py` | L |  |
| 88 | `packages/engine/src/ontolearn_engine/protocol.py` | L |  |
| 89 | `packages/engine/src/ontolearn_engine/rdf_snapshot.py` | L |  |
| 90 | `packages/engine/src/ontolearn_engine/resources.py` | L |  |
| 91 | `packages/engine/src/ontolearn_engine/storage.py` | L |  |
| 92 | `packages/engine/src/ontolearn_engine/storage_probe.py` | L |  |
| 93 | `packages/engine/src/ontolearn_engine/worker.py` | L |  |
| 94 | `packages/engine/tests/storage_baselines.py` | L |  |
| 95 | `packages/engine/tests/test_binding_regressions.py` | L |  |
| 96 | `packages/engine/tests/test_contract_v2.py` | L |  |
| 97 | `packages/engine/tests/test_coordinator_control.py` | L |  |
| 98 | `packages/engine/tests/test_frame_corpus.py` | L |  |
| 99 | `packages/engine/tests/test_handshake_deadline.py` | L |  |
| 100 | `packages/engine/tests/test_i04_lifecycle_boundaries.py` | L |  |
| 101 | `packages/engine/tests/test_i04_progress.py` | L |  |
| 102 | `packages/engine/tests/test_i04_round_faults.py` | L |  |
| 103 | `packages/engine/tests/test_job_store.py` | L |  |
| 104 | `packages/engine/tests/test_memory_guard_exit.py` | L |  |
| 105 | `packages/engine/tests/test_protocol.py` | L |  |
| 106 | `packages/engine/tests/test_resident_runtime.py` | L |  |
| 107 | `packages/engine/tests/test_runtime_bounds.py` | L |  |
| 108 | `packages/engine/tests/test_session_page_limits.py` | L |  |
| 109 | `packages/engine/tests/test_stdio_session_shutdown.py` | L |  |
| 110 | `packages/engine/tests/test_storage.py` | L |  |
| 111 | `packages/engine/tests/test_worker_owner_bootstrap.py` | L |  |
| 112 | `packages/engine/tests/test_worker_parent.py` | L |  |
| 113 | `playwright.config.ts` | L |  |
| 114 | `pyproject.toml` | L |  |
| 115 | `scripts/build-engine.mjs` | L |  |
| 116 | `scripts/build-i05-source-package-oracle.py` | L |  |
| 117 | `scripts/i04_matrix_evidence.py` | L |  |
| 118 | `scripts/prepare-i04-fixture.py` | L |  |
| 119 | `scripts/test-i05-source-package-oracle.py` | L |  |
| 120 | `scripts/verify-i01.py` | L |  |
| 121 | `scripts/verify-i04-package.py` | L |  |
| 122 | `scripts/verify-sources.mjs` | L |  |
| 123 | `tests/e2e/csp-lifecycle.spec.ts` | L |  |
| 124 | `tests/e2e/desktop.spec.ts` | L |  |
| 125 | `tests/e2e/i04-jobs.spec.ts` | L |  |
| 126 | `tests/e2e/native-driver.ts` | L |  |
| 127 | `tests/e2e/native-recovery.cjs` | L |  |
| 128 | `tests/fixtures/quality/i05-source-package-oracle/budget-gaps.json` | P |  |
| 129 | `tests/fixtures/quality/i05-source-package-oracle/coverage.json` | P |  |
| 130 | `tests/fixtures/quality/i05-source-package-oracle/oracle.json` | P |  |
| 131 | `tests/fixtures/quality/i05-source-package-oracle/schema.json` | P |  |
| 132 | `tests/fixtures/quality/i05-source-package-oracle/sources.json` | P |  |
| 133 | `tests/unit/binding-regressions.test.ts` | L |  |
| 134 | `tests/unit/contract-v2.test.ts` | L |  |
| 135 | `tests/unit/contract.test.ts` | L |  |
| 136 | `tests/unit/csp.test.ts` | L |  |
| 137 | `tests/unit/engine-connection-state.test.ts` | L |  |
| 138 | `tests/unit/engine-environment.test.ts` | L |  |
| 139 | `tests/unit/jsonl.test.ts` | L |  |
| 140 | `tests/unit/native-driver.test.ts` | L |  |
| 141 | `tests/unit/supervisor.test.ts` | L |  |
| 142 | `tests/unit/task-progress.test.ts` | L |  |
| 143 | `tests/unit/task-runtime.test.ts` | L |  |
| 144 | `tests/unit/task-service.test.ts` | L |  |
| 145 | `tests/unit/task-update-boundary.test.ts` | L |  |
| 146 | `tests/unit/view-navigation.test.ts` | L |  |
| 147 | `tests/unit/window-recovery.test.ts` | L |  |
| 148 | `tsconfig.unit.json` | L |  |
| 149 | `uv.lock` | S |  |


### 3.3 本轮本人独立复算的关键数据事实（非引用文档数字）

以下均为本方用标准库在固定输入上**独立复算**所得（`raw/data-audit-stdout.txt`、`scratch/data-audit-report.md` 为上轮留存证据）：

- `oracle.json`：417 条 observation、ID 唯一；每条字段键集合与 `schema.entryKeys` 精确相等。
- `oracleStatus`：280 specified / 137 pending；`expected.semanticState` 为 normal 208 / known-rejection 208 / not-executed 1；`contextStatus` 410/6/1（**另一维度，勿混**）。
- `wholeOracleComplete=false`。
- 137 条 pending 的集合与顺序 == `137-gap-ledger.json` 的 137 行。
- 85 槽 = 85 条；37 矩阵 = 37 行且 `graphSlotCount` 合计 85；矩阵含 `legacy/unbound-head`（原 specified，非 pending）。
- declared-allocation：specified 88 / pending 26 / not-invoked 2 = 116。
- `budget-gaps.json`：items 82 + `additionalProductionRestoreCases` 32。
- `pendingFields` 分布：82 budgetAdmissibility / 32 graphBudget+budgetUsage+typedValues / 32 genuineCapture / 26 declaredAllocation / 14 A1ExactErrorProjection / 11 legacyDTO / 7 reason+phase / 3 scopeProvenance / 1 exactStructuredOnlyError / 1 exception+reason+phase。
- `projectionSha256` 按 builder canonical 复算 417/417 相符。
- manifest ↔ inputs ↔ oracle 三方零缺口；inputs 全文件无 `expected` 键。
- 七池按 `T//N + (j<T%N)` 复算违规 0；blank token 在 oracle/inputs 中 0 次。

本轮另行完整解析遍历 `packages/contracts/v2` 八件大 JSON（`fixtures.json` 472098 B / 321+11+9+30+7+2+2+2+20 条目；`schema.json` 66 个 `$defs`；`binding-regressions.json` 41 例；`frame-fixtures.json` 51 例；`errors.json` 26 个错误码 + 7 组 `parameterMeanings`，`maxEncodedBytes=2048`；`registry.json` `schemaVersion=2`、`productRuntime=["health"]`、`v2Runtime` 14 项；`states.json` 状态机转移表；`dependencies.json` 七类策略）与 `tests/fixtures/quality/i05-source-package-oracle` 五件（`oracle.json` / `coverage.json` / `sources.json` / `schema.json` / `budget-gaps.json`）。

---

## 4. 缺陷清单（F-01～F-15）

严重度口径：**中** = 会影响业务正确性/证据可信度；**低-中** = 覆盖或口径缺口；**低/低-信息** = 卫生性或已用其它机制缓解。
每项给：精确位置 / 触发条件 / 影响 / 证据 / 修复建议。

### F-01 [中] fixture Turtle 解码器的 blank node 标签无数据集作用域，跨图合并会混淆不同 blank node

- **位置**：`scripts/build-i05-source-package-oracle.py:249, 272-273, 774, 801, 376-383`（解码器把 `_:bN` 直接按标签收集，无数据集命名空间）
- **触发条件**：同一待构建数据集内出现来自不同源图、但标签相同的 blank node。
- **影响**：跨图合并后两个不同 blank node 被当作同一节点；跨图比较也会把不同节点判为相同。
- **证据**：当前语料**无** `(` 空节点出现，故**已发布字节不受影响**；这是「语料未触发」而非「机制正确」。
- **建议**：解码时以 `(sourceId, localLabel)` 复合键标识 blank node，并在跨图比较时按复合键配对。

### F-02 [中] 17 条 observation 声称 `consumer-C-goldens.json` 为独立 expected 来源，但机器交叉核对只覆盖 9/13 个 golden、且只比对 2 个字段

- **位置**：`scripts/build-i05-source-package-oracle.py:1050-1055`（声明来源）vs `scripts/test-i05-source-package-oracle.py:363-375`（实际交叉核对）
- **影响**：声明强度高于实际验证强度；读报告者会高估这 17 条的独立性。
- **证据**：两处代码直接对照；`consumer-C-goldens.json` 实际含 13 个 case。
- **建议**：把声明降级为实际覆盖口径，或把交叉核对补齐到 13/13 全字段。

### F-03 [中] `explanation-goldens.json` 被列为「外部独立 expected 来源」，但未被任何 expected 派生或校验

- **位置**：`scripts/build-i05-source-package-oracle.py:30, 52, 1083, 1210-1212`
- **证据**：对 `oracle.json`（417 条）与 `inputs/` 全量检索该文件名，**0 次命中**。
- **影响**：来源清单声明与实际消费不一致（该文件实为被声明的输入，不是被校验的 expected）。
- **建议**：从 external expected 来源清单中移除，或真正接入校验。

### F-04 [中] 七池总额是手工复制的常量，与所引规范行之间没有机器交叉校验

- **位置**：`scripts/build-i05-source-package-oracle.py`（七池 T 值：work 16777216 / input_bytes 262144 / output_bytes 262144 / trace_items 8192 / firings 1024 / head_occurrences 16384 / bindings 1024）对照 `guidance/allocation-integration-plan.md.raw` L72–80 与 `allocation-restore-plan.md.raw` L103–109
- **影响**：规范改动不会使 build/check 失败，属**可漂移常量**；而被引规范本身要求「不复制一套可漂移常量」。
- **建议**：在 build 时从规范行提取额度并与常量比对，不一致即构建失败。

### F-05 [中] 三份来源清单互不包含且命名口径不一致；且有一条实际来源完全未登记

- **位置**：`oracle.json` 的 `sourceRefs` / `inputs/*.json` 的来源字段 / `sources.json` 三方对账
- **证据**：26 行中 **18 行精确匹配不上**；`ref 523c478d…` 未在 `sources.json` 登记，涉 `b1-semantic/1x`、`b1-semantic/10x`、`offline/implicit-jsonld`。
- **影响**：「来源真实身份」无法机器对账，至少 3 条 observation 的来源身份悬空。
- **建议**：统一命名口径，build 时强制三份清单互为子集并对未登记 ref 直接失败。

### F-06 [低-中] `schema.json` 声明的 RDFTerm 形状未覆盖 288 处真实数据

- **位置**：`packages/contracts/v2/schema.json` 的 RDFTerm `oneOf` 精确键集合 vs 25 条 observation 的 raw occurrence 形状（5 键）
- **影响**：schema 与实际数据形状存在 288 处缺口，说明 schema 未按真实语料收敛。
- **建议**：按语料补齐 RDFTerm 分支并加交叉校验断言。

### F-07 [低-中] `scope` 的 `factSources.basis` 只保留首个匹配 firing 的 leafBasis

- **位置**：`scripts/build-i05-source-package-oracle.py:791-793`
- **影响**：同一 head 三元组的其它 occurrence 的依据被丢弃，解释链不完整（与 PRD FR-502「完整依据链」口径有张力）。
- **建议**：保留全部 occurrence 的 basis 集合。

### F-08 [低] `source-identities.json` 被 builder 消费但未纳入固定身份白名单

- **位置**：`scripts/build-i05-source-package-oracle.py:1213`
- **影响**：来源身份文件本身不在固定身份清单内，其变更不被 `--check` 覆盖。
- **建议**：并入 DOC_PINS / 固定身份集合。

### F-09 [低] `sources.json` 的 `sourcePath` 指向本树不存在的历史路径且不带 ref/sha256

- **位置**：`tests/fixtures/quality/i05-source-package-oracle/sources.json`
- **影响**：来源路径不可在本树复核，破坏「可重复核对」前提。
- **建议**：改用固定 ref + sha256，或改为本树可达路径。

### F-10 [低] 索引→错误码映射表对越界索引无防护

- **位置**：`scripts/build-i05-source-package-oracle.py:590, 593, 601`
- **影响**：越界索引会以**异常中断构建**，而不是按既定口径记为 pending。
- **建议**：越界显式降级为 pending 并计入缺口账。

### F-11 [低-信息] 固定 argv 的解释器与项目声明的 Python 版本不一致

- **位置**：`docs/reviews/T05/source-package-oracle/record-command.py`（`sys.executable`）与 `pyproject.toml` `requires-python = ">=3.12,<3.13"`
- **证据**：上轮已用 `python3.12` 对照复验，47/47 OK、结果一致。
- **影响**：仅属可重复性口径问题。
- **建议**：记录命令时固定记录实际解释器版本与路径。

### F-12 [中] **`scripts/verify-i01.py` 的打包健康探针仍用 I01 时代 v1 信封，在当前 v2 协议下必然失败**（本轮新发现）

- **位置**：`scripts/verify-i01.py:100-115`
- **触发条件**：对本包构建出的打包引擎执行该脚本（`--packaged <exe> --output <dir>`）。
- **机制**（三处独立失配，任一即致命）：
  1. 发送的信封为 `{"id","method","protocolVersion":1}`，**缺 `kind` / `engineSessionId` / `params`**；`coordinator.py:176-178` 要求 `set(value) == {"kind","id","protocolVersion","engineSessionId","method","params"}` 且 `kind=="request"`，否则 `raise ProtocolFault()`。
  2. 即使补齐字段，`coordinator.py:187-188` 对 `protocolVersion != 2` 返回 `VERSION_INCOMPATIBLE`（`ok=false`），与脚本 `assert health_result["ok"] is True` 冲突。
  3. 命中 1 时是**会话致命**故障：引擎不写任何响应行即退出，`json.loads(health.stdout)` 在断言之前就抛 `JSONDecodeError`。
- **影响**：该脚本在本包上**不可运行**；它是一个 I01 时代的**死验证脚本**。
- **旁证**：`.github/workflows/ci.yml` 的 `quality` 与 `desktop` job **均未调用** `scripts/verify-i01.py`，故该缺陷不会在 CI 暴露，属于潜伏项。
- **建议**：改为 v2 信封（先 `hello` 握手再 `health`），或明确把该脚本标记为 I01 历史件并从本包清单移出；无论哪种都应在清单里说明其不再作为当前验收依据。

### F-13 [低-中] `job_store.commit_job_round` 直接 `stateVersion += 1`，绕过 `contract.permits_transition`

- **位置**：`packages/engine/src/ontolearn_engine/job_store.py:832-838`（`job["stateVersion"] += 1`，注释声明为「同一非终态内的证据修订」）
- **影响**：状态版本推进不再由统一状态机裁决；`states.json` 的 `cancelling→succeeded` 限制等约束对该路径不生效。
- **证据（已声明、低severity）**：源码注释显式说明 `_transition` 拥有状态名边、此处只允许同一非终态内的证据修订；`tests/unit/task-service.test.ts` 与 `packages/engine/tests/test_job_store.py::test_round_progress_new_persistent_version_then_cancel_snapshot` 锁定了 2→3→4→5 的非终态递增序列。
- **建议**：改为经 `permits_transition` 判定后再自增，或在契约层显式区分「证据版本」与「状态版本」两个计数器。

### F-14 [低-中] `storage.Conflict` 的异常文本内嵌原始 subject / predicate / source_row / id，防护只靠调用方自律

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:436-440`（`slot={subject} {predicate}, other={owner}, row={source_row}, id={id}`）与 `storage.py:629-633`（`Ownership conflict: slot=…, row=…, id=…`）
- **影响**：若该异常文本被直接跨边界返回，会泄露原始标识与行定位。
- **证据（实际跨边界安全，本方复核）**：`coordinator.classify()`（`coordinator.py`）与 `job_store._application()`（`job_store.py:94-110`）**只取 `code` 与 `params`**；ownership 冲突另被转成 `OWNERSHIP_CONFLICT` + **opaque** `detailRef`（uuid），不携带异常文本/原值/路径。测试亦锁定：`packages/engine/tests/test_storage.py::test_ownership_conflict_has_persistent_safe_detail_and_global_claim_probe` 断言 detail 内容不含 `private-value`；`test_coordinator_control.py::test_sqlite_real_errorcode_classification_not_exception_text` 断言分类结果不含 `secret`。
- **定级理由**：属**未封装的危险通道**（仅靠注释与调用方纪律约束），实际出口已安全，但缺强制机制；故由「中」降为「低-中」。
- **建议**：`Conflict` 不再拼接原值到 message（或提供 `safe_message` 属性），把可读诊断只放在本地日志。

### F-15 [低-信息] 内存上限语义跨平台不等价，且 Darwin 为**非硬限、可过冲**采样

- **位置**：`packages/engine/src/ontolearn_engine/memory_guard.py:1-8`（自述「Darwin sampling is not a hard allocation cap and can overshoot between samples」）与 `packages/engine/src/ontolearn_engine/coordinator.py:443-448`（父进程 RSS 采样**仅在 `sys.platform == "darwin"` 分支**执行）
- **影响**：Linux（RLIMIT_AS 虚拟地址空间硬限）/ Windows（Job Object 提交内存硬限）与 Darwin（libproc RSS 采样）三者对 `maxWorkerMemoryBytes` 的保证强度不同；Darwin 下父进程侧**不做**采样兜底，越界只能由子进程自身 guard 捕获。
- **证据**：`memory_guard.py` 模块 docstring 自述；`coordinator.py:443` 的 `if sys.platform == "darwin" and process.returncode is None:`；`packages/engine/tests/test_i04_lifecycle_boundaries.py::test_actual_memory_guard_supports_normal_worker_and_denies_known_oversize` 按 `sys.platform` 断言 `darwin-rss-monitor` / `windows-job` / `linux-rlimit-as` 三种模式。
- **定级理由**：代码自述清晰、非隐藏；属**口径说明缺失**而非实现错误。
- **建议**：在能力/限制文档中显式登记三平台保证差异与 Darwin 过冲幅度；Darwin 侧若需硬限须换用其它机制。

### 4.1 本轮**复核后撤销**的怀疑项（记录以免重复计账）

| 项 | 原怀疑 | 复核结论 |
| --- | --- | --- |
| `coordinator._authorize` 在 params 无 `projectId` 时不做校验 | 疑似越权 | **不成立**。`coordinator.py` 的 `_authorize` 取 `params.get("projectId", params.get("binding", {}).get("projectId"))`；`packages/contracts/v2/schema.json` 中 `params_job.*`/`params_project.get`/`params_result.get`/`params_operation.get` 全部 `required` 含 `projectId`，`params_result.page` 无顶层 `projectId` 但 `pageBinding.required` 含 `projectId`。**每个项目范围方法都必带一个 projectId**，授权路径无缺口。 |
| `task-presentation.ts:193` 的 `cells[5] !== Number(cells[6]) > 0` 优先级可疑 | 疑似恒真导致摘要永不可用 | **不成立**。JS 中关系运算符（`>`）优先级**高于**相等运算符（`!==`），该式等价于 `cells[5] !== (Number(cells[6]) > 0)`，语义正确；`tests/unit/task-service.test.ts:1192/1194` 双向锁定（命中「存在未处理事件（3）」与「不可用」两分支）。 |
| `package-lock.json` / `uv.lock` 未审查 | 可能含越权依赖 | **未做条目级审查**（诚实列为 S 档）；本方仅核 `package.json` 的直接依赖为精确版本、`ci.yml` 使用 `npm ci` 与 `uv sync --frozen`、两锁文件随改动提交。 |

---

## 5. 历史意见、失败与后继 —— 逐条处置

**处置口径**：每项给「采纳 / 撤回 / 保持未决」的**精确证据与理由**；不静默删项，不用免责声明消账。本轮**不关闭**任何历史 pending。

### 5.1 R1 Fail → R2 修复复审

| 意见 | 处置 | 精确证据与理由 |
| --- | --- | --- |
| **R1-01** selector 漏 `authoring` / `fixture` 目录 | **保持已关闭（本方复核确认）** | 复算：3 个 tool 依赖共 19/26/29 条 `requiredLocalFiles`、25 个来源、31 个绑定已全部落在 selector 覆盖内；`externalRuntimeOrPolicyDependencyClosureVerified=false` 仍**如实为 false**，未被改写为 true。 |
| **R1-02** 73 条 Git 展示路径 | **保持已关闭（本方复核确认）** | 本方用 `git ls-tree -r -z` 真实路径（UTF-8，非 C-quoted 展示）重算，73 条与 `full-engineering-inventory.json` 的 `fullTrackedTree` 集合逐条相等；`directFullTrackedPathSetEqualsNulGit=true`。 |

### 5.2 必须逐条处置的历史失败（全部保留）

| 历史失败 | 处置 | 精确证据与理由 |
| --- | --- | --- |
| IRI 旧 74 例失败 | **保持未决** | 本树无对应运行证据，O 侧不重跑；不因本轮静态审查而降级。 |
| FR505 旧 16 例缺口 | **保持未决** | 同上；缺口属父 T05 门。 |
| graph 四红：`langString` / `nni` / `dateTime-equal` / `dateTime-before` | **保持未决（并记一处口径问题）** | T05-16 的真实 Validator 关闭已成立，但 O 侧 `goldens` 的 `currentEntryGap` **未**在 `pendingFields` 中被反映——即 O 侧 expected 账对「已知四红」缺少显式 pending 条目。**本方登记为口径缺口**（属 F-05/F-06 同类「账与数据不同步」问题，不另开新编号以免重复计账）。 |
| date 两首失败 | **保持未决（诚实降级）** | O 侧以 `declaredRegressionAuthority` + `independentLibraryClassificationProven:false` 诚实降级（见 `guidance/legacy-date-declaration-receipt.md` 的 6 行声明表：ID 7/8/9/10 在 parser 门、15/16 在有限域门）。**不得**把 pre-registered legacy regression assertion 写成独立标准证明。 |
| 137 pending | **保持未决** | 137 条集合与顺序 == `137-gap-ledger.json` 137 行（本人复算）；本轮续接**不**关闭任何一条。 |
| 26 声明缺件 | **保持未决** | declared-allocation 116 项 = specified 88 / pending 26 / not-invoked 2；26 条缺件仅保已知 metadata，未捏造 slot 或额度。 |
| M 三份 local-untracked actual ZIP | **保持未决（仅登记，不打开）** | manifest 固定 120953467 B；本树**无原件**，仅登记不打开（遵守「未知自动 metadata 不 open」）。 |
| T05-E1～E4 未实施 | **保持未决** | 属后继实施门，本轮无实施证据。 |
| 26 阶段两模型 `taskId` / `actualSettings` / `actualTerminal` / `reportPath` 全 null | **保持未决** | 无实际运行终态，不补造。 |

### 5.3 本轮对历史资料的独立复核

| 项 | 复核结论 |
| --- | --- |
| `guidance/source-identities.json` 5 条来源身份 | 与 `guidance/contract.md` §1 的固定组合表一致；5 条 ref/bytes/sha256 自洽。**但**其中 `ref 6891a584…` 等历史路径**不在本树**，只能按命名绑定（与 F-09 同源）。 |
| `guidance/allocation-source-receipt.json` | `actualAllocationCaptureOrUsageProvided=false`、`noProductAlgorithmReadOrExecution=true`、`doesNotProveLaterWritersUnchanged=true`、`notWholeTreeAncestry=true` —— 四项诚实声明齐备，**未**发现把登记当证明。 |
| `guidance/native-child-declaration-reference.json` | `missingNativeKey=["graphBudget"]`、`missingChildKeys=["planDigest","budgetUsage"]` 与 `missingChildKeys` 声明一致；`doesNotSpecifyUnknownValuesOrDeriveExpectedFromImplementation=true` 成立。 |
| `guidance/pre-registered-date-source.json` | `newProbeOrRuntimeOutputUsedAsExpected=false`、`rootApprovedReuse=true` 成立；`excerptSha256` 与 `pre-registered-date-assertions.py.raw` 实际内容一致（该 raw 为 39 行、参数化 18 个拼写 × 2 side，与声明的 L275–313 语义一致）。 |
| `guidance/AGENTS-current.md` | 与本树 `AGENTS.md` 的**旧基线**快照一致（其中「本地验证默认不打扰用户」一节已被 2026-10-22 的桌面操作更新取代；guidance 副本保留原字节不改）。本方按**最新** AGENTS 桌面操作政策执行，两者不冲突。 |

---

## 6. 分范围结论（静态 / 运行 / 打包 / 生产 / 父门分列）

### 6.1 静态结论（本方唯一可完整承担的范围）

- **O 包 149 件工程/authoring 静态审查：NotPass。** 依据 F-01～F-15（5 中 / 5 低-中 / 5 低-信息），其中 F-12 为确定性运行失败。
- **O 工具链自身（builder + self-test）：Pass。** 47/47 OK；`--check` 五件字节相等、280/137、`wholeOracleComplete=false`。
- **架构不变量静态核对**：本方逐条核对并**未见违反**——
  - 本地优先：无遥测/云/开端口/云数据库；`registry.json` 无未实现能力宣告。
  - 渲染端隔离：`preload/index.ts` 只暴露按业务命名的方法，无 `invoke(method, params)` 通道；`window-security.ts` 对 `will-navigate` / `will-frame-navigate` / `will-redirect` / `will-attach-webview` 全阻断并禁止新窗口。
  - CSP：`csp.ts` 为唯一配置源；生产分支不含 `unsafe-inline` / `unsafe-eval`（`tests/unit/csp.test.ts` 断言 `not.toMatch(/unsafe|nonce|localhost|127\.0\.0\.1/)`）；`style.css` 全文无 `url()` 外部引用（仅 `@import url('./tokens.css')`）。
  - 确定性/Agent 解耦：preload 与 renderer 无写任务创建面（`tests/unit/task-service.test.ts` 断言 `'createJob' in tasks === false`）。
  - 存储：`storage.py` 单写事务（`BEGIN IMMEDIATE`/SAVEPOINT/COMMIT/ROLLBACK，`synchronous=FULL`），`snapshots`/`commits`/`runs`/`rounds`/`run_terminal` 全表不可改写触发器；`rdf_snapshot.py` 只从不可变快照重建、无写回路径。
  - 数据层次与失效：`invalidation-v2.json` 为唯一 `staleReason` 来源；`model` 族 `staleReason=null`（`tests/unit/contract-v2.test.ts` 断言域 stale 码集合与 S1 规则集合精确相等）；仅改模型配置不使领域结果过期（`packages/engine/tests/test_storage.py::test_late_snapshot_without_domain_change_stays_history_and_cannot_displace_current`）。
  - 错误边界：`coordinator.classify()` 只返回固定码 + 受限参数；`engine.ts` 的 stderr 只发固定事件 `stderrDiscarded` / `unmatchedResponse` / `invalidFrame` / `listenerFailed`，**不转发子进程 stderr 内容**（`tests/unit/supervisor.test.ts` 断言 `diagnostics` 恰为 `['stderrDiscarded']`）。
  - 模型外发：`process_environment.worker_environment()` 只放行 15 个系统键，凭据/代理/库路径/注入变量全不转发（`tests/unit/engine-environment.test.ts` 实启子进程断言 `secret/credential/proxy/injection/loader` 全 false）。

### 6.2 运行结论

- **O 工具链运行：Pass**（见 6.1）。
- **产品 / 引擎 / 桌面运行：无法验证。** 本轮授权边界仅允许 O 的两条 stdlib 命令；`npm run check`、`npm run test:e2e`、`pytest`、`uv sync`、打包、真人桌面**均未运行**。静态结论**不得**代替运行证据。

### 6.3 打包结论

- **无法验证。** `npm run package:dir`、`scripts/verify-i04-package.py`、PyInstaller 产物、`--protocol-resources` / `--contract-probe` 子命令**均未执行**。
- **已登记的待验证疑点（不作为结论）**：`apps/desktop/electron-builder.yml` 的 `extraResources.from: ../../build/engine/ontolearn-engine` 在 Windows 下与 PyInstaller 产出的 `ontolearn-engine.exe`（`apps/desktop/src/main/engine.ts:15` 按 `process.platform === 'win32'` 选择 `.exe`）路径不一致；该疑点**必须由真实 Windows 打包运行判定**，本方不作结论。

### 6.4 生产结论

- **无法验证。** 无真人桌面、无两 OS CI、无目标系统、无远端核验。
- `tests/e2e/i04-jobs.spec.ts` 的 native 恢复用例以 `process.platform !== 'linux'` 跳过（另需 `I04_NATIVE_ISOLATED=1` 与 `xdotool`/`openbox`）；`tests/e2e/csp-lifecycle.spec.ts` 的 native 恢复需真实聚焦可见窗口。**这些用例能否在 macOS / Windows CI runner 上稳定通过，本方无法判定**，列为父门待证。

---

## 7. 本方**不签署**的门（全部保持原状态）

以下门本方**一律不签署**，且**不因本次续接而自动关闭**：父 T05 结论 / P0 整体 / 正式 Job / 正式 Store / selected 范围 / wholeH / 17L / 费用（预算准入）/ S1 / B1 / CI 两 OS / 真人桌面 / develop 合并 / 远端核验 / 同版双指定模型审查 / 独立缺证项。

仍然独立缺证（未核，不消账）：owner 的本人 UI 权限回执之外的一切独立佐证；父门要求的真人/两 OS/远端证据；`docs/reviews/T05` 中另一指定模型（ZCode）本轮的意见/报告/自动状态——本方**未读取、未索取、未引用**（原共同历史输入仍按原授权使用）。

## 8. 需要总控/上游决定的后继（本方无权自行关闭）

1. F-12：`scripts/verify-i01.py` 是修正为 v2 信封，还是从 149 件清单中标记为 I01 历史件并退出当前验收依据？（需上游决定，本方只报告事实。）
2. F-01/F-04/F-05/F-09/F-10：是否要求 builder 引入「规范行 ↔ 常量」「三份来源清单互为子集」的**机器交叉校验**（会让 build/check 在规范漂移时失败，属行为变更，需上游批准）。
3. F-06/F-07：schema 补齐 RDFTerm 分支、`scope.factSources.basis` 保留全部 occurrence——均会改变已发布 expected 字节，属 O 包自身变更，需要新的固定来源与重新评审。
4. graph 四红的 `currentEntryGap` 未进 `pendingFields` 的口径缺口：由 O 包补账还是由 T05 侧登记？（跨包归属需总控裁定。）
5. 6.3 的 Windows 打包路径疑点：需真实 Windows 打包运行证据后判定。
6. 本方 `report.md` 与 owner 记录的两版 bytes/SHA 不一致（60824 B/`78cdadc3…` vs 56586 B/`b145d9cb…`、58279 B/`d93c7603…`）：请 owner 确认以哪一版为权威原件；本方**未**覆盖任何一版。

---

## 9. 本轮新增元数据清单（与冻结输入分门）

全部位于 `docs/reviews/T05/projection-R3-receiving/launch-O/`，**未**触碰 11 件冻结 launch 输入与 290 件保护来源：

| 文件 | 性质 | 说明 |
| --- | --- | --- |
| `final-v2.md` | **本轮唯一终稿** | 本文件 |
| `report.md` | 上一轮原件，**保留未覆盖** | 60824 B / `78cdadc3…` |
| `scratch/v2-head.md`、`scratch/v2-tail.md` | 本轮写作中间件 | 拼接 `final-v2.md` 用 |
| `scratch/data-audit-report.md`、`raw/data-audit-stdout.txt` | 上轮数据审计 | 保留 |
| `raw/o-*.txt`（18 件）、`raw/setup-preflight-*`（3 件） | 上轮执行原始流 | 保留；`o-run-*` 三件为**合并流**已如实标注 |
| `preflight-observe.json`、`preflight-setup.json` | 上轮 preflight 产物 | 保留 |
| `guidance/`（4 件）、11 件冻结输入、`launch-map.json`、`launch-input-manifest.json`、`scope-contract.json`、`execution-supplement.md`、`launch-prompt.md`、`frozen-original-prompt.md`、`authority.md`、`verify-launch-input.py` | **冻结输入，原字节未改** | 不属本方新增 |

**本轮未新增任何 raw 执行证据文件**（因未重跑任何命令；上轮原始流已如实引用并标注合并流）。

**树状态**：` M AGENTS.md`（受保护，本方未改、未暂存）+ `?? docs/reviews/T05/projection-R3-receiving/launch-O/`。受审实现 / 测试 / fixture 的 SHA256 与上轮逐件相同，未改动。未 stage、未 commit、未切分支、未建 Goal、未 push / PR / merge。

---

## 10. 终稿自检

- 149 件覆盖账闭合：L 124 + P 20 + S 2 + 部分 3 = 149。✅
- 大 JSON「完整解析/遍历」与源码「逐行阅读」**分别记录**（P / L 分列）。✅
- 真实未读 / 缺证明确列出（§3.1 五条、§7、§8），未以免责声明消账。✅
- F-01～F-11 全部保留并逐项给位置/触发/影响/证据/建议；新增 F-12～F-15；另有 §4.1 记录三项**经复核撤销**的怀疑项，避免重复计账。✅
- 全部历史失败/意见逐条给出采纳/撤回/保持未决及精确证据，无静默删项。✅
- 静态 / 运行 / 打包 / 生产 / 父门**分列**，互不代替。✅
- 未预设改判：结论为 **NotPass**（静态）、**Pass**（O 工具链自身）、**无法验证**（运行/打包/生产）、父门**全不签署**。✅
