# I05 / B1 C1 第一轮独立只读审查报告（MiniMax M3.1-Flash）

## 0. 结论先行

**最终判定：不通过（NotPass）— 1 个阻断问题（B-1′，见 §4.2）。**

> **判定变更历史（必须连同结论一起阅读）**
>
> | 版本 | 报告 SHA256 | 判定 | 触发
> |---|---|---|---|
> | 初稿 | `cdd27463cbe87925b70723e37557fe307793ed137add55d40c9a305b64094e44` | **通过（Pass）**，0 阻断 | 本人首轮独立审查
> | +来源事实更正 | `03fd0f8983fe3131137cbeea48eac72ee158389b0e00a3cc24594fbf8a67e0f1` | **通过（Pass）**，0 阻断 | 开发方 `round-1/source-lineage-note.json`（§4.1，我核实属实，不改判定） |
> | **本轮** | 见 §11 | **不通过（NotPass）**，1 阻断 | 开发方 `round-1/shacl-lexical-counterexample.py` + `.json`（§4.2）；我独立复现并**升级我自己在初稿中的 L-1 结论** |
> | **本轮追加（三轮）** | 见 §11 | **不通过（NotPass）**，1 阻断（**范围收窄**） | 开发方新增 `store-lexical-counterexample.*`、`query-numeric-counterexample.*`（§4.4）；同时提出针对我 §4.2(4)③ 的事实争议——**我接受更正，③ 不成立并从阻断依据中移除**；B-1′ 仅由 ①② 支撑，判定不变 |
>
> **本轮另有一项不改变判定的流程事实更正（§4.3）**：初稿与本轮正文把"三平台 CI 从未实际执行"（B-1）写成了"**push/PR 前**必须补齐"，与原 Goal 第六节「推送与合并门禁」的时序不符——CI 结果只能在 push/PR **之后**产生，属合并前核验阶段。该表述已更正为准确阶段归属。**此更正不改变判定**：B-1′ 的阻断评级由**本审查者**依据自行复现的可达性证据独立作出，未因开发方的补充说明而改变；本轮也**未**把未执行的 CI 记为已通过。
>
> 初稿判定 **Pass** 本身的事实基础仍然成立：受审候选在**它自己声明的有限范围内**满足 B1 原文的全部义务，并完成了 B1 所必需的**真实 I04 接线**；我独立复现了其中最关键的四项（源码/包内同样例逐字节相等、外联拒绝经正校准的可达接收端实测零命中、S1/B1 两档原始测量口径逐值复现、真实 stdio 三能力落库）。**判定改变的唯一原因是 §4.2 的 B-1′**：SHACL 允许值模板在合法可达输入上产生**错误验证结论**，且该缺陷**未在候选的 Q6 登记中体现**——这使负责人据以作 Q6 逐项决定的能力图景失真，按 Goal 门禁「阻断问题尚未关闭…不得出具通过」必须改判。

除 B-1′ 外，初稿的其余发现维持原判：1 项高（H-1）、3 项中（M-1/M-2/**M-3**，M-3 为本轮新增，见 §4）、3 项低（L-2、L-3、L-4）全部非阻断；H-1 候选已明确登记为"明确未覆盖、待负责人处置"且未宣称完成；M-1/M-2/M-3 属错误分类精度、登记清单完整性与查询侧保真缺口，不影响安全边界与验收结论。初稿列为 L-1 的词法规范化观察已被升级并以 **B-1′** 单独列示，不再计入低危。

同时如实登记 **6 项本轮未取得/未复现的边界**（B-1…B-6），其中三平台 CI 从未实际执行、I05 原生窗口矩阵在 CI 中只存在于 Linux。

**2026-10-21 追加的来源事实更正（§4.1）：** 我已独立核实原 raw 与 owning code，确认更正**属实**——历史失败的真实原因是"事实 ID 未按 subject/predicate/object 内容派生"，而非冻结文档所写的"非 UUID 事实身份"。更正经 `round-1/source-lineage-note.json` 承载，冻结文档与原 raw 原样保留，未触及代码/测试/配置/依赖/验收/基线，base/head 与 365 文件范围不变，1126 跟踪文件再次零漂移。**该更正本身不改变判定**：我在其到达时（报告 SHA `03fd0f89…`）核实的结论是"更正属实、判定仍为 Pass"，本轮改判的唯一触发是其后到达的 SHACL 词法反例（§4.2 → B-1′），与该来源更正无关。两项追加材料的先后与各自影响必须区分阅读。

---

## 1. 实际身份、任务来源与核对结果

### 1.1 身份与来源（区分可核验与不可核验）

| 项 | 值 | 核验方式 |
|---|---|---|
| 审查者 | MiniMax Code / MiniMax-M3.1-Flash | 本会话运行时公开身份可见 |
| 思考程度 | xhigh | **派发者声明**（开发会话原生 UI 现场选定）。本审查者**无法**在审查任务内核验原生任务的 UUID 或思考程度控件，故仅记录为派发方声明，未独立复核，不编造原生 UUID |
| 模型/路径/分支选定 | M3.1-Flash／xhigh，精确 I05 路径与分支 | 同上，**派发者核验声明**，本审查者未在 UI 侧复核 |
| 另一审查者（本轮 ZCode/GLM-5.3） | 未读取其 prompt／过程／报告／结论 | 遵守约束；仅读取共同输入 `full-review-input.md`、`input-manifest.json` 与 `candidate-1.json` |

### 1.2 仓库状态核对（我本人执行）

```
pwd            /Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation
git root       同上
branch         feature/I05-semantic-validation
HEAD           043c20cc7934191339a8814c79666dbd2e94a62a
merge-base     5f910b52c69d86a1076b2032e5d3c63e715947f3  == 受审 base ✅
remote         origin https://github.com/NOmoreJoke/OntoLearn-Studio.git
diff           365 files changed, 592153 insertions(+), 46 deletions(-)
git status     M AGENTS.md   ?? docs/reviews/I05/candidate-1.json   ?? docs/reviews/I05/round-1/
```

### 1.3 冻结输入完整性（我本人执行）

| 文件 | 声明 SHA256 | 实测 | 结论 |
|---|---|---|---|
| `docs/reviews/I05/round-1/full-review-input.md` | `a3ccbc7b4e01ad704dab1c1263c0974c120db929f3bec02b6aa0111d5b3ceaf3` | 同 | ✅ 40684 bytes / 277 行，与声明一致 |
| `docs/reviews/I05/round-1/input-manifest.json` | — | 816 bytes，base/head/路径/两个报告名/隔离目录一致 | ✅ |
| `docs/reviews/I05/candidate-1.json` | `91e48255347f0abd123be79370e6a6d8e16debe4e6c4a5376101a5f91e992874` | 同 | ✅ |
| `docs/reviews/I05/round-1/source-lineage-note.json`（2026-10-21 追加的纯流程来源说明） | `cc0a94a05fc5fd46eba985e1ae9817e55db04bb3e9bcfc49a419414d48ca12fe` | 同 | ✅ 内容已独立核实，见 §4.1 |
| `AGENTS.md`（受保护操作规则，故意 dirty 且未 stage） | `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786` | 同 | ✅ 仍为 dirty、未 stage，未被混入候选 |

**candidate-1.json 内容独立重算（我本人执行，对 HEAD blob 而非工作树）：**

| 区段 | 声明条数 | 逐条重算匹配 | 不匹配 | 缺失 |
|---|---|---|---|---|
| `files`（变更集） | 365 | **365 / 365** | 0 | 0 |
| `fullTrackedFilesExceptProtectedGuidance` | 1126 | **1126 / 1126** | 0 | 0 |
| `executionInputs` | 198 | **198 / 198** | 0 | 0 |

`git diff --name-only base...head` 的 365 条与 `files` 键集合**完全相等**（双向零差）。受保护文件 ∩ 变更集 = **0**（7 个受保护路径出现在全量清单中，但 base↔head blob 逐字节相同，属未改动的受保护上下文，非变更）。

**证据清单独立重算（我本人执行）：**

| 清单 | 声明条数 | 逐条重算 |
|---|---|---|
| `docs/reviews/I05/evidence/integrated-c1/manifest.json` | 117 raw | **117 / 117 匹配**（sha256 + 字节数） |
| `docs/reviews/I05/evidence/integrated-c1-sealed/manifest.json` | 14 raw | **14 / 14 匹配** |
| `integrated-c1-sealed/source-binding.json` | `sourceBindingSha256=635920ec…` | 与文件实测 SHA 一致 ✅；内含 198 条，与 candidate 的 198 条路径与 SHA **逐条相同**；`linuxMismatches=[]`、`productionInputChanges=[]`、`laterChangedHarnessFiles=["tests/e2e/i05-semantics.spec.ts"]` |

**证据中引用的 5 个 git 对象全部真实存在**：`5f910b5`(base) / `043c20c`(head) / `6b57078`(productionSourceHead) / `0218d6e` / `851be57`(finalHarnessHead)，均为 HEAD 祖先。另有 10 个 40-hex 串并非 git 对象，而是内容寻址的附件**文件名**成分（`…-0c0a592e….json.raw` 等），不构成缺失引用。

**候选分层与我实测一致：** `git diff 851be57...043c20c` 仅含 `docs/`（证据与两份文档），**零产品源码变更**；`git diff 6b57078...851be57` 仅含 `tests/e2e/i05-semantics.spec.ts` 一个文件。→ **候选头 043c20c 确实只追加验收与证据，未偷改受审实现。**

---

## 2. 完整审查范围与已读需求

### 2.1 已逐字读完的需求原文

- `docs/reviews/I05/round-1/full-review-input.md`（277 行全文，含原 launch、完整 resume 交接、完整原 Goal 含第九节）
- `docs/reviews/I05/inputs-c1/`：`scope.md`（冻结范围与六项门禁）、`policy.md`（无桌面打扰与进行中任务过渡）、`parallel-coordination.md`（I04 完成后交接与共享文件责任）、`I05-launch-prompt.md`、`I05-resume-integrated-I04-20261021.md`、`goal-objective.md`、`sources.json`
- `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`：**B1 全文（S1/S2/S3 之外的独立小节）**、S1 测量口径、退出门槛、Q2/Q3/Q5/Q6/Q7/Q8/Q9 开放状态
- `docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6：**附录 C（能力矩阵主定义）、附录 D（九行失效表）、附录 E（E.1/E.2/E.5）、附录 G（G-base/G-map-empty/G-behavior/G.2 十二例）**，以及 FR-203/401/402/500/501/502/504/505/006、§9.2、§10.2–10.5、§12.3–12.5、附录 F
- `docs/reviews/I05/handoff-shared-entry-build-20261020.md`（I05→I04 入口/构建承接义务）
- ADR-0001/0002/0003 与 `packages/contracts/v2/`、`packages/engine/src/ontolearn_engine/{storage,invalidation,memory_guard,process_environment,__main__}.py`（**全部零 diff**）

### 2.2 B1 原文（逐字，判定基准）

> **B1：真实候选引擎库打包**
>
> 在隔离分支/验证环境固定 RDFLib、pySHACL 及实际规则实现候选的完整依赖，先运行最小真实 Turtle 解析、只读查询、RDFS/受控规则和 SHACL 检查，再执行 `package:dir` 并从产物内运行相同样例。引入依赖即启动验证，不必等到 Q6 最终冻结，更不能等 M2。
>
> 检查 PyInstaller 隐式导入、资源/插件、动态库与许可证清单；实测 `SERVICE`、远程 `FROM`、解析器/验证器可能产生的隐式外联均被拒绝，不能用"配置关闭"替代证据。候选组合只承诺附录 C 的有限语义，不能以库默认推理模式扩大为完整标准能力。
>
> 记录包体、冷启动/热调用耗时、内存峰值、样例规模、设备、版本和原始测量值；业务容量是否达标须等待 Q5 的目标，不能先编造秒数或性能提升。首轮可在现有 macOS arm64 开发环境证明依赖可打包；Q2 确定的首发平台仍需干净设备、无系统 Python、断网、签名安装等后续证据。当前空引擎打包通过不覆盖这些事项。

我按 B1 四段义务逐项判定，见 §5 表格。

### 2.3 逐文件核查的 365 个变更文件

按目录分组的实际审查覆盖：

| 组 | 文件数 | 我的核查深度 |
|---|---|---|
| `packages/engine/src/ontolearn_engine/` | 12（`semantic.py` 562、`semantic_execution.py` 489、`semantic_scopes.py` 326、`semantic_samples.py` 561、`semantic_probe.py` 349、`semantic_error_adapter.py` 357、`semantic_offline.py` 51、`job_store.py` 306、`coordinator.py` +163、`worker.py` +105、`protocol.py`、`resources.py`） | **全文逐行读 + 独立对抗性探针** |
| `packages/engine/tests/` | 10（合计约 3200 行） | 逐个测试函数名与语义核查；本地实跑 |
| `packages/contracts/` | 6（`v2/schema.json`、`v2/registry.json`、`v2/fixtures.json`、`src/v2.ts`、`src/index.ts`、`python/contract_v2.py`） | 全文 diff + schema/registry 结构核查 |
| `apps/desktop/src/` | 4（`main/index.ts`、`main/task-service.ts`、`preload/index.ts`、`renderer/src/App.tsx`） | 全文 diff + 安全不变量核查 |
| `scripts/` | 5（`build-engine.mjs`、`i05-build-inventory.py`、`prepare-i05-fixture.py`、`verify-i05.py`、`verify-i05-runtime.py`） | 全文读 |
| `tests/` | 3（`e2e/i05-semantics.spec.ts` 544、`unit/semantic-bridge.test.ts` 333、`unit/contract-v2.test.ts`） | 全文读 + 断言强度评估 |
| `.github/workflows/ci.yml`、`uv.lock`、`packages/engine/pyproject.toml` | 3 | 全文 diff |
| `docs/iterations/I05/`、`docs/reviews/I05/`（含 evidence、licenses） | 其余 | 文档/证据逐项核对与独立重算 |

**未逐字节通读的只有**：53 个 `packages/engine/licenses/**` 许可原字节（大体积上游元数据，我以清单哈希与包内 SHA 逐条核对，未逐行读第三方许可正文）、以及 evidence 目录下的大体量 `.raw` 原始产物（我按 manifest 逐条重算 SHA 与字节数，并对其中所有 `logs/*.txt.raw`、runtime summary、native 证据做了内容通读）。

---

## 3. 我本人独立执行的验证（与开发证据严格分离）

### 3.1 执行环境与写入界限

- 复用本 worktree 既有 `.venv` 解释器本体（只读），**未**执行 `uv sync`、**未**改动 `.venv`/`node_modules`/`out`/`release`
- 所有临时输出、探针脚本、`TMPDIR` 位于自建目录 `build/I05-review-C1-minimax/{tmp,out,venv}`
- **全程无窗口**：未运行 Electron / Playwright e2e / native / HMR；未启动或操作任何 GUI 应用；未触发凭据提示；未操作 ZCode / MiniMax / Codex 界面
- 未提交、未推送、未切分支、未改任何冻结实现/测试/配置/依赖/验收/基线

### 3.2 实跑命令与真实结果

| # | 命令（workdir 均为本 worktree） | exit | 真实结果 |
|---|---|---|---|
| 1 | `.venv/bin/python -m pytest -q -p no:cacheprovider packages/engine/tests` | **0** | **1511 passed in 54.30s** |
| 2 | `npx vitest run` | **0** | **16 test files / 672 tests passed**（6.89s） |
| 3 | `npx eslint . --max-warnings 0` | **0** | 无输出（通过） |
| 4 | `npx prettier --check .` | **0** | `All matched files use Prettier code style!` |
| 5 | `npm run typecheck`（contracts + unit + desktop） | **0** | 三个 `tsc --noEmit` 全过 |
| 6 | `.venv/bin/ruff check .` | **0** | `All checks passed!` |
| 7 | `.venv/bin/ruff format --check .` | **0** | `207 files already formatted` |
| 8 | `PYTHONPATH=packages/engine/src .venv/bin/python -m ontolearn_engine.semantic_probe --mode suite` | **0** | 30984 bytes，stderr 空 |
| 9 | `release/mac-arm64/…/engine/ontolearn-engine --semantic-probe --mode suite` | **0** | 30984 bytes，stderr **0 字节** |
| 10 | 上述 #8/#9 输出逐字节比较 | — | **完全相同**：两边 SHA256 均为 `2ae81bd9efc27052256000b178743fea4c6a37ee6f1433359a90af1142dfeabb` |
| 11 | `--mode reject`（源码 + 包内） | **0** | 各 **28** 例；`EXTERNAL_ACCESS_DENIED` 15 / `UNSUPPORTED_SHACL` 9 / `UNSUPPORTED_FORMAT` 4；网络审计事件各 **1**（即刻意触发的 JSON-LD 真实库隐式路径，止于 `urllib.Request`） |
| 12 | **正校准环回接收端**（我的独立脚本 `out/loopback_check.py`） | **0** | 先由我自己发 1 次请求证明接收端**真实可达**（hits=1）；再跑源码与包内两轮拒绝矩阵，**接收端命中数仍为 1**（引擎零命中） |
| 13 | `ONTOLEARN_TEST_ENGINE=<包内引擎> pytest …::test_actual_stdio_source_or_packaged_jobs_persist_all_three_semantic_outputs` | **0** | **1 passed in 1.03s**（真实 stdio 三能力 Job/结果落库） |
| 14 | `--mode measure --scale 1 / 10`（我的独立复测） | **0** | scale1: 18 断言三元组 / 22 语义三元组；scale10: **180 / 184**；seed **20261019**；`inputSha256(10x)=25393c99db270c57…`、`querySha256=7879b25f2833b8e4…` — 与开发记录 `macos-parity-final/source-10x-0.json.raw` **逐值相同**；依赖版本 rdflib 7.6.0 / pyshacl 0.30.1 / owlrl 7.6.2 / html5rdf 1.2.1 亦相同 |
| 15 | 包内引擎 SHA256 | — | `71d4b4bcb33c2d529560aaa76935a95c9d2991941345d9fc850705fbc6bb32d9` — 与证据 `package-manifest.json.raw` 的 `executableSha256` **一致** |

> 说明：#1–#7 使 `npm run check` 的六个阶段在**候选头 043c20c** 上由我本人全部实跑通过；开发方证据 `check-final.txt.raw`（672 TS / 1511 Py）对应的是 `6b57078`（Python 测试文件在 6b→HEAD 间逐字节未变，故计数成立）。`npm run build` 我**未运行**（会改 `apps/desktop/out`，违反本轮写入界限），构建/打包证据以只读方式核验。

### 3.3 我本人编写的对抗性语义探针（`out/adversarial.py`、`out/adv2.py`、`out/adv3.py`）

**（a）外联拒绝矩阵（对真实可达的环回接收端）**

| 查询形态 | 实测分类 | 接收端命中 |
|---|---|---|
| `SERVICE <iri>` | `EXTERNAL_ACCESS_DENIED` | 0 |
| `SERVICE SILENT <iri>` | `EXTERNAL_ACCESS_DENIED` | 0 |
| `VALUES ?e {<iri>} SERVICE ?e {…}` | `EXTERNAL_ACCESS_DENIED` | 0 |
| `{{ SELECT * WHERE { SeRvIcE <iri> {…} } }}`（大小写与嵌套） | `EXTERNAL_ACCESS_DENIED` | 0 |
| `SELECT * FROM <iri> WHERE {…}` | `EXTERNAL_ACCESS_DENIED` | 0 |
| `SELECT * FROM NAMED <iri> WHERE { GRAPH ?g {…} }` | `EXTERNAL_ACCESS_DENIED` | 0 |
| `BASE <iri> SELECT * FROM <relative> WHERE {…}` | `EXTERNAL_ACCESS_DENIED` | 0 |
| `SELECT * FROM <file:///must-not-read.ttl> WHERE {…}` | `EXTERNAL_ACCESS_DENIED` | 0 |
| `GRAPH ?g {…}` / `GRAPH <http://…> {…}` | `QUERY_FAILED`（rdflib 拒绝；**无外联**） | 0 |

**（b）语义边界拒绝（真实库行为，非配置声明）**

`ILL_TYPED_LITERAL→INVALID_LITERAL_LEXICAL`；`NaN^^xsd:decimal→UNSUPPORTED_NONFINITE_LITERAL`；未知 datatype→`UNSUPPORTED_LITERAL_DATATYPE`；事实/本体空白节点→`UNSUPPORTED_BLANK_NODE`；`<relative>`→`INVALID_TURTLE`；`owl:imports`→`EXTERNAL_ACCESS_DENIED`；`rdfs:seeAlso`→`UNSUPPORTED_RDFS`；`owl:NamedIndividual`→`UNSUPPORTED_OWL`；1.1 MB 文本→`TEXT_INPUT_LIMIT`；SHACL 事实域混入公理→`FACT_SCOPE_CONTAINS_AXIOMS`；`CONSTRUCT`/`DESCRIBE`→`READ_ONLY_QUERY_REQUIRED`；`LIMIT`/`OFFSET`→`QUERY_SLICE_UNSUPPORTED`；`ORDER BY` 表达式或非投影变量→`UNSUPPORTED_QUERY_ORDER`；`SUM`/`MIN`/`GROUP_CONCAT`→`UNSUPPORTED_QUERY_FUNCTION`；`RAND`/`NOW`→`UNSUPPORTED_QUERY_FUNCTION`；自定义函数 IRI 与 `xsd:integer(...)` cast→`UNSUPPORTED_QUERY_FUNCTION`；规则输出 `rdfs:subClassOf`→`UNSUPPORTED_RULE_OUTPUT`。

**（c）一阶段语义与确定性（我实测）**

- 规则链不产生二阶事实：`R1: Equipment→Marked`、`R2: Marked→Second`，`reason()` 结果**只含 R1 产出**，`warnings=["RULE_CHAIN_UNSUPPORTED:R2"]`；**规则顺序颠倒后结果完全相同**（对应 FR-501 第 4 点与附录 G R-05/R-06）。
- 规则输出结构上不可能反馈 RDFS（`_rule()` 拒绝 rdfs/owl/sh 命名空间谓词输出）。
- 确定性：同图连续 5 次 `query()`、5 次 `reason()` 结果**逐字节相同**；无 ORDER BY 时按规范次序排序。

**（d）附录 G G.2 用例覆盖核对**：源码 `semantic_samples.suite()` 逐条断言 Q-01/Q-02/V-01/R-01/R-02/R-03/R-04/R-05-06/O-01 的**完整预期集合与顺序**（非仅计数），与 PRD G.2 表逐行对应。

### 3.4 开发方证据（我只读核验，未由我复现）

- `evidence/integrated-c1/manifest.json` 117 raw 与 `integrated-c1-sealed/manifest.json` 14 raw：**逐条重算全部匹配**（我方独立执行）。
- Linux 原生证据（我**只读**，因本 Mac 禁止 Electron/native/GUI）：source 与 packaged 两份 `i05-native-verified-evidence.json.raw` 均 `result="PASS"`、`events=["crashed","unresponsive"]`、`inspectorClosed=true`、`hangMonitorEnabled=true`、`noSandboxSwitch=false`、**3 个重建窗口全部 visible**、第 2 窗 `focused=true` 且外部 `xdotool/XGetInputFocus` 记录 `visible=true`、**2 个真实 GTK 对话框**（标题 `OntoLearn Studio 窗口恢复`，crash/hang 各一）、三时点 `resultsSha256` **只有 1 个不同值**（持久结果未重放）、显式取消 `state="cancelled"` 且 `resultRef=null`。
- 证据中保留的**历史失败**未被抹除，且均能看到对应后续通过日志：`check-first.txt.raw`（1 failed/1478 passed）、`runtime-baseline.txt.raw`（7 failed）、`semantic-runtime-first.txt.raw`（1 failed + 14 errors）、`linux-semantic-source{,-second,-third}.txt.raw`（namespace 权限失败）、`linux-packaged-native-final.txt.raw`（1 failed of 5，Electron 内建模块未就绪）、`package-macos-*.txt.raw`（electron-builder 3 步 skip：未重建依赖/无图标/未签名）。

### 3.5 本轮第三轮追加材料与我自己的探针（我本人执行，仍为无窗口 CLI/引擎验证）

| # | 命令（workdir 均为本 worktree） | exit | 真实结果 |
|---|---|---|---|
| 16 | `shasum -a 256` 四份新材料 | — | 4/4 与声明一致（`5891b829…` / `b2cb4a06…` / `6aee4db0…` / `b97fc1f5…`） |
| 17 | `PYTHONPATH=packages/engine/src .venv/bin/python docs/reviews/I05/round-1/store-lexical-counterexample.py build/I05-review-C1-minimax/out/store-lexical-01` | **0** | stderr 空；与开发 raw **结构等价**（差异仅 `resultId`/`jobId`/`operationId`/`projectId`/`createdAtMs`/`finishedAtMs`/`updatedAtMs`）；`validation.execute` → `report={"conforms":true,"violations":[]}`；`query.execute` → `{"type":"ASK","value":true}` |
| 18 | `PYTHONPATH=packages/engine/src .venv/bin/python docs/reviews/I05/round-1/query-numeric-counterexample.py` | **0** | stdout 与开发 raw **逐字节相同**（SHA `b97fc1f5…b712e`） |
| 19 | 我的探针 `build/I05-review-C1-minimax/out/probe-lexical-20261021.py` | **0** | 字面量项语义（`==`False / `.eq`True / 哈希不同 / Graph 查找区分）、规则层矩阵、查询层矩阵、其余 datatype 词法影响半径 |
| 20 | 我的探针 `build/I05-review-C1-minimax/out/probe-lexical2-20261021.py` | **0** | `sh:in` 列表解析后首值 = `"1"^^xsd:integer`（约束被改写）；**非空洞对照**：minCount 形状给出 `focus=<urn:unit>`，证明 target 命中；假阳（fact "01" → violates，value="01"）与假阴（fact "1" → conforms）矩阵 |

> 两次探针均只写自建 ignored 目录 `build/I05-review-C1-minimax/out/`，未触碰受审 365 文件集。

---

## 4. 发现（按严重度）

### H-1［高·非阻断］FR-505 的"属性值比较"与"单条规则多结论"未实现，但候选已明确登记为未覆盖

- **位置**：`packages/engine/src/ontolearn_engine/semantic.py:205-210`（`Rule` 只有单个 `then` 三元组）、`semantic.py:230-231`（`when` 项只接受 `URIRef|Literal|Variable`，无比较运算符）、`semantic.py:250-263`（输出谓词受限）；`docs/iterations/I05/q6-candidate-differences.md` 的 Q6-08 行
- **触发**：构造规则条件 `level > "High"`（大小比较）或单条规则产出两个事实 → 能力不存在（前者无法表达，后者需多条规则）
- **影响**：与 PRD FR-505「条件支持类型判断、属性存在、属性值比较及条件合取…结论支持添加类成员关系或受控属性断言」「推导一个或多个新事实」存在差距
- **候选处置（我核实为真实、不是口头）**：Q6-08 行明写「**明确未覆盖，待负责人处置**…B1 最小探针不能冒称此条产品完成；若路线无法承载原要求须淘汰」；`docs/iterations/I05/acceptance.md` 与 `integrated-runtime.md` 同步声明"不等于规则编辑器/表达层比较与单条多结论已完成"；UI 文案（`App.tsx`）亦写明"规则链、递归及范围外构造仍不支持；当前候选范围等待 Q6 确认"
- **阻断判定：非阻断。** 依据：B1 原文只要求"最小真实样例 + 附录 C 有限语义"，且 B1 明确"引入依赖即启动验证，不必等到 Q6 最终冻结"；本项被**如实登记为未覆盖**而非冒充完成
- **建议**：Q6 负责人须在采用/修订/淘汰三选一中给结论；若保持原 FR-505，须修订候选表达层并补"比较/多结论"代表样例。**产品采用层不可省略此缺口标注**，否则与 FR-500「不支持必须显示"不支持"或"未执行"，不得展示为"已通过"」及附录 C「不得静默删减」冲突

### M-1［中·非阻断］SPARQL `GRAPH` 形态被归类为"执行失败"而非"不支持"

- **位置**：`packages/engine/src/ontolearn_engine/semantic.py:138-166`（代数预扫描只拦 `ServiceGraphPattern` 与 `DatasetClause`，未拦 `GraphGraphPattern`）、`semantic.py:199-202`（`except Exception → SemanticError("QUERY_FAILED")`）
- **触发**：`SELECT * WHERE { GRAPH <http://…> { ?s ?p ?o } }` 或 `GRAPH ?g {…}`
- **实测**：`GRAPH <http://127.0.0.1:port/x> {…}` → `QUERY_FAILED`；`GRAPH ?g {…}` → `QUERY_FAILED`；**两种情况下环回接收端命中数均保持 1（即我的正校准），零外联发生**
- **影响**：FR-402「不得以"只读"替代外联控制」**未被违反**（无任何外联）；但 FR-500 要求把"不支持/未执行"与"执行失败"分开，一个合法的 SPARQL 1.1 形态会在 UI 四段式里被呈现为失败，分类精度不足
- **阻断判定：非阻断。** GRAPH 不在附录 C 承诺的"项目内只读 SELECT/ASK"范围内；无安全后果
- **建议**：在 `query()` 的代数预扫描中显式拒绝 `GraphGraphPattern`，归入受控不支持码；或在 Q6-04 行明确登记"项目内命名图未实现"并同步错误分类表

### M-2［中·非阻断］被接受的确定性内建函数集合未在候选文档中枚举

- **位置**：`packages/engine/src/ontolearn_engine/semantic.py:142-156`（聚合白名单与函数黑名单）
- **实测接受**（我在真实库上逐个验证）：`str` / `langMatches` / `CONCAT` / `SUBSTR` / `STRLEN` / `IRI`
- **实测拒绝**：`xsd:integer("5")` cast 与自定义函数 IRI（rdflib 解析为 `Function` 类）、`RAND`/`NOW`/`UUID`/`STRUUID`/`BNODE`、`SUM`/`AVG`/`MIN`/`MAX`/`SAMPLE`/`GROUP_CONCAT`、`CONSTRUCT`/`DESCRIBE`、`LIMIT`/`OFFSET`
- **文档对照**：`acceptance.md` 与 Q6-06 行的表述（拒绝"扩展 IRI 函数"与随机/时间/UUID/BNOKE，除 COUNT 外的聚合）与实现**一致**，不是虚假声明
- **影响**：Q6-06 标题为"C SELECT/ASK 的**函数 / 聚合**范围"，负责人逐项采用时需要一份明确的"接受集"清单；当前文档只描述拒绝侧
- **阻断判定：非阻断。** 拒绝侧与实现完全吻合，不构成能力夸大
- **建议**：在 Q6-06 行补记上述实际接受的内建函数清单，并注明这是可继续收紧的白名单

### M-3［中·非阻断·本轮新增］查询文本中的裸数值 token 被解析器规范化，与 SPARQL 的"缩短形式保留词法"不一致

- **位置**：`packages/engine/src/ontolearn_engine/semantic.py:133`（`prepareQuery(text)` 直接使用 rdflib 的 SPARQL 解析器）；规范化发生在候选自己钉死的 **rdflib 7.6.0** 内部
- **实测（我的探针，非开发方材料）**：查询层的 BGP 匹配本身是 **RDF 项匹配**（正确），但**裸整数 token 在解析阶段即被规范化**，使 `01` 等价于 `"1"^^xsd:integer`：

  | 事实对象 | 裸 `01` | 显式 `"01"^^xsd:integer` | 显式 `"1"^^xsd:integer` |
  |---|---|---|---|
  | `"1"^^xsd:integer` | true | false | true |
  | `"01"^^xsd:integer` | **false** | true | false |

  → 同一用户意图（按 SPARQL §2.3.2，`01` 与 `"01"^^xsd:integer` 是同一写法）在引擎里给出**相反**答案；且对 `"01"^^xsd:integer` 的事实给出**静默 false**（按 §2.3.3 的"词法形式与 datatype IRI 都匹配"应为 true）。`01e+00`（DOUBLE）同样失配；`-01.00` 在 **rdflib 解析器**被拒（`Not a number; Literal('1.00', datatype=xsd:decimal)`），引擎包装为受控 `INVALID_QUERY`——**可见错误**（符合 FR-500 的显式拒绝取向），但按规范语法 `-01.00` 是合法 DECIMAL token，属**保真缺口**。
- **可达性**：需要事实带非规范词法。Store 对断言事实强制 canonical（`Canonical RDF object required`），故只有**规则产出**的事实可达（与 B-1′ 同一前提）；查询范围含 `asserted+selected-derived`（Q6-11），故可达。这与候选自己"原词法 integer `01` 的真实规则输出经 JSON 往返投影仍为 `01`"（`acceptance.md:42`）所展示的场景直接相关：**结果里看得到 `"01"^^xsd:integer`，用 `01` 却查不到**。
- **登记状态**：**未**出现在 Q6-01/Q6-04/Q6-05/Q6-06/Q6-07 任一行；候选对查询语法的其他收窄（LIMIT/OFFSET、函数、聚合）**都有登记**，唯独此项未登记
- **阻断判定：非阻断。** 依据：① **无 FR-500 式的直接禁止**——FR-500 的文义限于"每次 SHACL 检查…对于当前引擎不支持的检查，必须明确显示'不支持'或'未执行'，不得展示为'已通过'"，**不覆盖查询结果**；FR-402 只管只读/外联/分页，FR-203 管导入导出。② 该行为**继承自候选自己钉死的 rdflib 7.6.0**（B1 的前提正是"固定 RDFLib 候选依赖并实测"），确定、可复现，候选**未对该项作能力夸大**。③ 触发前提窄（需规则产出非规范词法事实）。④ 性质更接近**登记与保真缺口**（与 M-2 同类：实现真实但边界未枚举），而非 B-1′ 那样"静默改写已保存构造并给出错误验证结论"
- **升级条件（须提请 Q6 负责人判断）**：若 Q6 采用"SPARQL 1.1 数值 token 词法保真属 P0 承诺"，或产品层要把查询结果当作可直接引用的确定性结论而未标注该收窄，本项即应升为阻断
- **建议**：① 在 Q6-01（类型字面量/词法）与 Q6-04（SELECT/ASK）补记该收窄；② 与 B-1′ 的修复**一并处理但独立成条**——开发方拟修的"约束入口保词法"**不覆盖查询侧**（查询侧须在解析入口保词法，或对非规范数值 token 显式拒绝并给固定安全错误）；③ 补回归：裸 `01`/`+1`/`01e+00`/`-01.00` 对 canonical 与非规范词法事实的完整矩阵

### L-1［初稿：低 → **本轮升级为阻断，见 §4.2 / B-1′**］`parse_turtle` 使用 rdflib 默认 Turtle 解析器，字面量会被规范化

> **初稿原文（保留历史）**：位置 `semantic.py:105`（`Graph().parse(...)` 默认行为）对 `semantic_scopes.py:85-87` 的 `_LexicalSink(normalize=False)`（仅用于规则输出与结果投影的行解析）。实测 `"01"^^xsd:integer` 经 `parse_turtle` 变为 `"1"^^xsd:integer`，而同一字面量经 `_LexicalSink` 路径保持 `"01"`。**初稿影响判断**：SHACL 为**值等价**比较，判定结果不受影响；"词法保真"这一候选结论的适用范围应写明。**初稿阻断判定：非阻断。**
>
> **本轮更正**：初稿"值等价比较 ⇒ 判定结果不受影响"这一推理**是错的**，据此升级为阻断问题 **B-1′**（§4.2）。事实部分（规范化确实发生、位置一致）不变；错误在于我把 `sh:in`（允许值）当成了值语义，而它按 **RDF 项**比较，且该模板在合法可达输入上产出**错误验证结论**。初稿的"非阻断"判断同时构成我自己的审查缺陷，在此明确记录。

### L-2［低］`semantic.start` 的登记语义与其余能力不统一，且 `productRuntime` 无运行时约束

- **位置**：`packages/contracts/v2/registry.json`（`productRuntime=["health","query.execute","reasoning.execute","validation.execute"]`，`v2Runtime` 另含 `semantic.start`；`capabilities` 里 `semantic.start` 的 `scope="project"`、`dataScopes=[]`、`dependencyPolicy=null`、`implementation="runtime"`、`agentEligible=false`、`exposure="business-named-bridge-only"`）
- **实测**：`productRuntime` 在仓库内**除 `tests/unit/contract-v2.test.ts:126` 的断言外没有任何消费方**——它是声明性清单，不构成运行时门禁
- **影响**：**不构成能力越权**（`semantic.start` 有真实实现且已在 `v2Runtime`；`agentEligible=false`；`exposure` 为业务命名 bridge）；但"声明清单"与"运行时强制"的关系应登记清楚
- **阻断判定：非阻断**
- **建议**：登记中注明 `productRuntime` 为声明性清单、`v2Runtime` 才是握手时实际暴露的方法集合

### L-3［低］worker 非语义分支的内存守卫关闭不在 `finally` 内

- **位置**：`packages/engine/src/ontolearn_engine/worker.py:212-262`（语义分支有 `try/finally: guard.close()`；非语义分支的 `guard.close()` 在函数末尾，`failRound` 提前 `return` 时不执行）
- **影响**：进程随即退出，无实际行为后果；但两条分支不对称
- **阻断判定：非阻断**

### L-4［低］桌面层永不触发引擎侧的操作幂等分支

- **位置**：`apps/desktop/src/main/task-service.ts`（每次 `startSemantic` 生成新的 `randomUUID()` 作为 `operationId`）对 `packages/engine/src/ontolearn_engine/coordinator.py` 的 `start_semantic`（`accepted_operation_job` 幂等路径）
- **影响**：引擎侧幂等实现正确且有测试覆盖（`test_semantic_operation_idempotent_after_current_moves_and_cannot_change_meaning`），但只可达于直接调用协调器；产品层目前没有"同一操作重试"的实际语义。属纵深防御，非缺陷
- **阻断判定：非阻断**

### 观察（不计为发现，供负责人判断）

- **O-1** 证据 `integrated-c1-sealed/sealed-harness-check.txt.raw` 只覆盖最终 harness `851be577` 的 `typecheck:unit` + prettier 两阶段（145 bytes），不含 lint / vitest / build / ruff / pytest。**我已在候选头 043c20c 上本人补跑全部静态阶段并全绿（§3.2 #1–#7）**，该缺口在本次审查中关闭。
- **O-2** sealed 桥接证据中，packaged 的 `first` 快照 `.jobs[4].error.code` 为 `null`（source 为 `NETWORK_FORBIDDEN`），因该快照捕获于 forbidden 作业终止之前；`final`/`restored`/`history` 三处均已收敛为 `NETWORK_FORBIDDEN`，两者 `failed` 块完全一致。属采样时序差异，非语义差异。
- **O-3** `logs/check-second.txt.raw` 记 1510 passed、`check-first.txt.raw` 记 1479 collected + 1 failed，与 1511 的最终值来自不同时点；`check-final.txt.raw` 的 vitest 起跑时间 `06:31:48` 晚于 `6b57078` 提交（`06:31:00`），归因自洽。
- **O-4** `bindings/linux-linkage-and-source.json.raw` 顶层 `python: "3.11.2"` 是诊断 python3，产品 CPython 3.12.15 来自包内清单与实际探针——`integrated-c1-verification.md:24` 已明确区分，未冒称。
- **O-5** `bindings/*.raw` 中 `AGENTS.md` 一处 1/982 不匹配，是"故意 dirty 的受保护指南不入提交"这一已记录约定的预期偏差，两个 binding 内均自带 `protectedGuidance` 说明。
- **O-6** 冻结文档 `docs/reviews/I05/integrated-c1-verification.md:33` 对一次历史失败的**措辞**不准确（"第一轮集成测试 fixture 误用**非UUID事实身份**"）。经核实，真实失败原因是"事实 ID 未按 subject/predicate/object 内容派生"，与 UUID 无关。开发方已用 `round-1/source-lineage-note.json` 更正该措辞而**保留冻结文档与原 raw**。属文档准确性缺陷，不涉及代码、测试、配置、依赖、验收或基线，详见 §4.1。

### 4.1 来源事实更正（2026-10-21 追加）—— 我独立核实原 raw 与 owning code

开发方追加 `docs/reviews/I05/round-1/source-lineage-note.json`（SHA256 `cc0a94a05fc5fd46eba985e1ae9817e55db04bb3e9bcfc49a419414d48ca12fe`），声明对冻结文档历史失败**措辞**的更正，不改代码/测试/配置/依赖/验收/基线，并要求审查者独立核实。按要求我逐条核实如下（全部为我本人执行）：

| 核实项 | 我的方法 | 结果 |
|---|---|---|
| 说明文件自身 SHA | `shasum -a 256` | `cc0a94a0…a12fe` **与声明一致** ✅ |
| 原 raw 的 SHA | `shasum -a 256 docs/reviews/I05/evidence/integrated-c1/logs/semantic-runtime-first.txt.raw` | `56474ccf2b4e15c30b87cea928ee075e5cf16a4318a7ed380b9f432ace407ef5` **与说明声明一致** ✅ |
| 原 raw 中的事实身份 | 直读 raw | `fact = {'id': 'unit-type', 'subject': 'urn:unit', 'predicate': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'object': '<urn:Child>'}` —— `id` 是语义标签 **`unit-type`，不是 UUID** ✅ |
| 实际报错 | 直读 raw | `ValueError: Fact identity must be content derived`（`storage.py:257`）；失败计数 `1 failed, 14 errors in 0.35s` ✅ |
| owning code 语义 | 读 `packages/engine/src/ontolearn_engine/storage.py:256-257` | `if fact["id"] != digest([fact["subject"], fact["predicate"], fact["object"]]): raise ValueError("Fact identity must be content derived")` —— **要求的是内容派生，不是 UUID** ✅ |
| owning code 是否被本候选改动 | `git diff --numstat base...head -- storage.py` | **0 行差异**，仍是已批准的 S1 内容身份校验 ✅ |
| 该 id 是否满足内容派生 | 我本人计算 `digest(["urn:unit", TYPE, "<urn:Child>"])` | `d4253da208a54a985063e0c8dd158e68e2a800d43f7d47d7f95564b008a0d981` ≠ `"unit-type"`；且 `"unit-type"` 长度 9、非 64 位十六进制 → **失败原因确为内容派生违规，不是"非 UUID"** ✅ |
| 现 fixture 的修正是否正确 | 读 `packages/engine/tests/test_semantic_runtime.py:69` | 已改为 `"id": digest(["urn:unit", TYPE, "<urn:Child>"])`，与 owning code 要求逐字一致 ✅ |
| 冻结文档原措辞是否存在 | `grep -n "非UUID事实身份" docs/reviews/I05/integrated-c1-verification.md` | 命中 `:33`：**确有不准确措辞** ✅ |
| 追加说明是否改动候选 | `git status` / `git diff base...head --name-only \| wc -l` | 新增文件位于 `docs/reviews/I05/round-1/`（未跟踪、非候选 365 文件集）；**base/head 未变、365 文件范围未变** ✅ |
| 追加后 1126 跟踪文件零漂移 | 我本人重算 HEAD blob SHA | `fullTrackedFilesExceptProtectedGuidance` **1126/1126 匹配**；同时复核 `files` **365/365**、`executionInputs` **198/198**，三项均零不匹配、零缺失 ✅ |

**我的判断：**

1. 更正**属实**。原措辞把一次"S1 内容身份校验拒绝了未按内容派生的 fixture ID"描述成"误用非 UUID 事实身份"，两者技术含义不同：前者是内容寻址身份不变量，后者会让人以为 S1 存在 UUID 格式要求。owning code 与原 raw 都支持更正后的表述。
2. 更正**恰当且保守**。冻结文档与原 raw 均按"保留历史失败"原则原样保留，更正以独立说明文件承载，未回改冻结证据，也未触及任何代码、测试、配置、依赖、验收或基线。
3. 对本轮判定**无影响**：该失败是历史 fixture 构造问题，已由最小修正关闭，且其后的 1511 全绿、我本人复跑的同文件 1511 全绿与包内真实 stdio 用例均已验证通过；更正不改变 B1 义务判定、Q6 逐项判断或任何安全不变量结论。
4. **残留建议（非阻断）**：冻结文档 `integrated-c1-verification.md:33` 的该行措辞仍不准确且被后续读者直接引用。更正说明文件与被更正文档分离虽符合"冻结证据不改写"的规则，但**只靠旁注不足以让只读冻结文档的读者看到正确原因**。建议在下一候选的文档更新（而非改写冻结历史）中，把该行改为内容派生表述，并保留本说明作为来源链。

---

### 4.2 SHACL 允许值模板的词法反例（2026-10-21 追加）—— 我独立复现、评估可达性并据此改判

开发方追加只读反例材料 `docs/reviews/I05/round-1/shacl-lexical-counterexample.py`（声明 SHA `37ff6ab298a5c6e33c9672948d905c335e35beda9b0250d17d7a35af70a4e1af`）与其实测 raw `shacl-lexical-counterexample.json`（声明 SHA `42704db646eed1ecd96150577852e72e5005c9d616148d5f0130801e7eace15e`），要求我独立核实"该对允许值模板是否造成实际误判"。我未采信其结论，全部自行重跑与重判。

#### (1) 材料完整性与我自己的复现

| 项 | 我的实测 |
|---|---|
| 脚本 SHA | `37ff6ab298a5c6e33c9672948d905c335e35beda9b0250d17d7a35af70a4e1af` ✅ 与声明一致 |
| raw SHA | `42704db646eed1ecd96150577852e72e5005c9d616148d5f0130801e7eace15e` ✅ 与声明一致 |
| 我本人运行脚本 | `.venv/bin/python docs/reviews/I05/round-1/shacl-lexical-counterexample.py` → exit 0；我的 stdout **与开发 raw 逐字节相同**（同为 `42704db6…`）✅ |

复现到的现象（开发 raw 原文）：`currentShapeListValues = ["1"^^xsd:integer]`（形状允许值被规范化），`lexicalShapeListValues = ["01"^^xsd:integer]`（同一文本经 `_LexicalSink` 保真），`actualCurrentResult.conforms = false`（InConstraintComponent 违规，`value = "01"^^xsd:integer`），`comparisonWithLexicalShapes.conforms = true`。

#### (2) 规范依据（我自行取原文核对）

SHACL W3C REC（<https://www.w3.org/TR/shacl/#InConstraintComponent>）§4.8.3 `sh:in`：

> `sh:in` specifies the condition that each **value node** is a **member** of a provided **SHACL list**.

同规范 §2.1.3 对 SHACL list 的定义：*"The members of any SHACL list except rdf:nil in an RDF graph G consist of its value for rdf:first in G followed by the members in G of its value for rdf:rest in G."* 即**成员就是列表项本身的 RDF 项**。同规范对 `sh:hasValue` 更直接写明 *"If the **RDF term** `$hasValue` is not among the value nodes…"*。候选所固定的 pySHACL 0.30.1 实测按 **RDF 项**比较（`"01"^^xsd:integer` 与 `"1"^^xsd:integer` 不相等），与上述规范一致。

#### (3) 反例所走路径是否可达 —— 我逐层核实（结论：**反例自身走的那条路不可达，但同一根因另有可达路径**）

| 层 | 我的实测 | 结论 |
|---|---|---|
| Store 断言事实层 | `storage.py:255` 要求 `term(fact["object"]).n3() == fact["object"]`；`storage.term('"01"^^<xsd:integer>').n3()` = `"1"^^<...>` ≠ 输入。真实 `JobStore.commit(manual=[…])` 传入词法 "01" 的事实 → **被拒**：`ValueError: Canonical RDF object required; derive ID from term(value).n3()` | **断言事实路径不可达**——反例直接喂 `_graph()` 绕过了 Store 闸门 |
| Store 规则定义层 | 规则词法文本**无同等闸门**。真实 `JobStore.commit` 提交 `then = ["?s","<urn:out>",'"01"^^<xsd:integer>']` → **COMMIT ACCEPTED**，且落库定义**逐字保留** `"01"^^<…integer>` | **规则层可达** |
| 推导事实 | 真实 `execute_request`（生产路径，worker `_semantic` 即调用它）跑 `reasoning.execute`，规则 `then` 产出 → 推导事实 `["<urn:s>","<urn:out>","\"01\"^^<xsd:integer>"]`，**词法保真** | 可达 |
| 约束层 | 约束 Turtle 由用户自由文本保存（Store 逐字保留 `sh:in ("01"^^<…integer>)`），`parse_turtle` 规范化为 `"1"` | 可达 |

#### (4) 我在**真实生产路径**（`execute_request`）上复现的三个可观察后果

| # | 输入（全部为合法用户输入） | 引擎实际结果 | 规范应有结果 | 性质 |
|---|---|---|---|---|
| **①** | 规则 `then` 产出 `"01"^^xsd:integer`；约束 `sh:path <urn:out>; sh:in ("01"^^xsd:integer)`；`asserted+derived` 范围 | `conforms=false`，**InConstraintComponent 违规，且违规报告的 `sh:value` 正是 `"01"^^xsd:integer`——即允许值列表里的那一个** | `conforms=true`（该值就是列表成员） | **假阳性**：报告一个"允许值里明明有、却违规"的自相矛盾结论 |
| **②** | 断言事实（canonical）`"1"^^xsd:integer`；约束 `sh:in ("01"^^xsd:integer)`；`asserted` 范围 | `conforms=true`（约束已被静默规范化为 `sh:in ("1"^^xsd:integer)`） | `conforms=false`（"1" 与 "01" 是不同 RDF 项） | **假阴性 + 用户保存的约束被静默改写** |
| **③** | 规则 `when` 为 `"01"^^xsd:integer`，事实为 canonical `"1"^^xsd:integer`（同一 RDF **值**、不同 RDF **项**） | 规则**不触发**，`rules=[]`、`warnings=[]` | **不触发即为正确行为**（当前获准语义 = 结构三元组 = RDF 项匹配；详见 §4.4(4)） | **本轮更正：③ 不构成缺陷**，已从 B-1′ 阻断依据中移除（我的初稿预期"应触发（同值同项）"错误） |

补充对照（我用同一路径逐个验证其余模板，界定影响半径）：`sh:datatype`、`sh:minInclusive`、`sh:maxInclusive`、`sh:minCount`、`sh:maxCount` 在词法 "01" 下**全部不受影响**（值/基数语义）。

#### (5) 影响评估

- **根因**：引擎在**约束（形状）侧**做值规范化（`parse_turtle` → rdflib 默认 Turtle 解析器），在**取值侧**不做（事实/规则经 `_LexicalSink`/`_term()` 的 `normalize=False`），而 `sh:in` 按 **RDF 项**比较。同一对项因而在约束侧"相等"、在比较处"不等"，引擎**内部不自洽**。这一不自洽与"采用哪种相等语义"之争无关——无论采值等价还是项等价，当前实现都至少在一个方向上给出错误结论。
- **影响面**：仅 `sh:in`（允许值，附录C 明列、FR-504 明列的 P0 模板）；仅当 typed literal 词法非规范时（`"01"^^xsd:integer`、`"1.0"^^xsd:decimal`、`"+1"^^xsd:integer` 等）；纯字符串与规范 typed literal 不受影响。
- **对固定验收样例与测试套件的影响**：**无**。附录 G G.2 与候选样例只使用纯字符串与规范形式；1511 pytest、672 vitest 全绿不覆盖该情形——**这正是它此前未被发现的原因**。
- **登记状态**：该缺陷**未**出现在候选的 Q6-01/Q6-10 登记中（Q6-01 只提到"词法…不能扩推所有类型无损往返"，指向往返保真，不指向验证结论错误）。因此负责人据以逐项作采用/修订/淘汰决定的**能力图景失真**。
- **本轮范围收窄（§4.4）**：B-1′ 现**仅**由 ①（假阳）与 ②（假阴 + 静默改写用户已保存约束）支撑；③ 经裁定不成立，已移除。①② 本身未被推翻，且已由开发方新增材料在**真实 Store→coordinator→worker→不可变结果路径**上确认（并由我用 `sh:minCount` 对照证明非空洞通过）。

#### (6) 我的判定：**阻断（Blocking）** —— B-1′

依据：

1. `validation.execute` 已在 `registry.json` 登记为 `productRuntime` 且 `implementation: runtime`；允许值模板是附录C SHACL 行与 FR-504 明列的 P0 能力。候选对模板的登记声明是"真实 Validator 的每种模板…均已执行"，而实际在该模板上产出**错误验证结论**。
2. 后果 ① 的报告**自相矛盾**（违规值即允许值），后果 ② 漏报并静默改写用户约束——**这两项**都是 FR-500「不得展示为已通过」、FR-203「禁止静默丢弃/改变构造」、附录C「不得静默删减」与 PRD 12.3「SHACL 预期违规对象与修复后结果必须与附录 G 一致」直接覆盖的禁止项。**后果 ③ 已按 §4.4(4) 的裁定移除**（规则层项匹配是既定语义，非缺陷）。
3. 该缺陷在**真实生产路径**上可达（Store 接受规则层非规范词法 → 推导事实保真 → 允许值模板误判），非单元级假象。
4. 依据 Goal 门禁「阻断问题尚未关闭，或关键验收仍无法验证时，不得出具通过」，本轮不得出具 Pass。

**不构成阻断、且我明确不主张的部分**：无安全或外联后果；不涉及数据损坏；其余 5 个 SHACL 模板、全部 SPARQL/RDFS/规则语义、全部架构不变量与 B1 其余义务均不受影响；附录 G 固定样例与全部测试套件结论不受影响。

**修复方向（供开发方参考，本审查不代为实现）**：使两侧词法处理一致——或在与事实/规则同源的约束/规则入口采用非规范化解析（仓库已有 `_LexicalSink`，无需改全局设置），或在约束与规则词法入口对非规范 typed literal **显式拒绝**并给出固定安全错误（与 Store 对断言事实已有的 `Canonical RDF object required` 策略一致）。任一方向都需补回归：**允许值模板的假阳一例、假阴一例**，以及规则 `when`/`then` 的**同词法触发**与**异词法不触发**各一例（后者是 §4.4(4) 裁定的**负例**，不是待修缺陷）。修复后需**新候选**并由双方重新全范围审查。**注意**：开发方拟修的"约束入口保词法"**不覆盖查询侧**（M-3），两者须分别处理。

---

### 4.3 推送与合并门禁的时序事实澄清（2026-10-21 本轮追加，无验收变更）——我自查并更正自己报告的表述

开发方指出：我自己的报告（初稿 §8 与本轮 §8.3）把"三平台 CI 从未实际执行"（B-1）表述为"**必须在 push/PR 前补齐**"，与原 Goal 门禁的实际时序不符，可能形成"CI 须在 push 前完成"的时序歧义，要求我依原完整输入独立说明。按要求我**只依据原输入独立核对**，不接受任何替我判定阻断等级的意见。

#### (1) 我核对的原输入原文（逐字）

| 来源 | 原文要点 |
|---|---|
| `docs/reviews/I05/inputs-c1/goal-objective.md` 第六节「推送与合并门禁」 | "只有以下条件全部成立，才能推送并合并：①本功能验收与必要验证通过；②两个指定模型对同一候选版本均明确通过；③**阻断问题全部关闭**；④其余建议均有处理结论，且不影响双方的通过判断；⑤待推送实现与受审实现一致。" 随后"满足门禁后"第 1–6 项为：推送 feature 分支 → 创建指向 dev 的 PR → "**遵守仓库实际分支保护和 CI 要求，不绕过检查**" → dev 变化则重新验证与双审 → "**CI 失败需要修改实现时，也必须回到验证与双审循环**" → 合并后核验远端 dev |
| `docs/reviews/I05/inputs-c1/scope.md:48` | "验收+双指定模型同版本明确通过+全部意见有结论后**才 push**；优先 PR→develop，遵守 CI 保护不绕过。develop 变化则更新验证并双审，CI 修代码同样回审。" |
| `docs/reviews/I05/inputs-c1/scope.md:44` | "冻结候选本地提交，记录固定 base/head、验证、完整文件范围和剩余未提交文件；**双审前不 push**，不改受审代码。" |
| `round-1/full-review-input.md`（原 launch 段，:57） | "完整功能全部验收、同版两方通过、全部意见有处置后，向总控预约串行集成；**PR→develop、实际 CI 全部成功、正常合并并核验远端**，才能完成 I05 Goal。" |
| `round-1/full-review-input.md`（resume 段，:84） | "完整验收、同版双方明确通过、意见有处理、待推送实现逐字一致**才 push/PR→develop**（创建后 attach_artifact）；**实际 CI 通过**、正常合并、远端与保护源核验后才完成原 I05 Goal。" |
| `round-1/full-review-input.md`（审查提示，:25） | "当前没有 push/PR/三平台CI/合并/签名/干净设备/生产/容量结论；它们各自仍有后续门禁，**不能伪称本轮通过已覆盖**。" |

#### (2) 由原输入直接推出的正确时序

```
① 本地完整验证（验收 + 必要验证）
② 同一候选版本、两项新建独立全范围审查均明确 Pass
③ 阻断问题全部关闭；其余建议均有处理结论
④ 待推送实现与受审实现一致
   ── 以上四项全部成立，才允许 push ──
⑤ push feature 分支 → 创建指向 dev 的 PR
⑥ 实际三平台 CI 在此执行并核验（遵守分支保护，不绕过）
⑦ CI 失败 → 回到验证与双审循环；CI 通过 → 正常合并
⑧ 合并后核验远端 dev 确实包含受审实现
   ── 至此才完成原 I05 Goal ──
```

**CI 结果不在 push 的前置条件列表内**（第 ⑥ 步在第 ⑤ 步之后）；它在原输入中被三处独立表述为"PR→develop **之后**、正常合并**之前**"的核验环节。

#### (3) 我的报告原文与我的自查结论

- **原文（初稿 §8 与本轮 §8.3，措辞相同）**："**B-1/B-2 必须在 push/PR 前补齐**：……PR→develop 前须取得真实 CI 结果……"
- **自查结论：该表述有误，属我自己的时序表述缺陷。** 其后半句"PR→develop 前须取得真实 CI 结果"与原门禁一致（CI 在 PR 之后、合并之前），但前半句"必须在 **push/PR 前**补齐"把 B-1 放进了 push 的前置条件，与原输入相反，并使"CI 结果先于 push 产生"成为逻辑上不可能的要求。**我接受这一更正。**

#### (4) 更正后的表述（§8.3 已按此改写）

- **B-1（三平台 CI 从未实际执行）**：属 **push/PR 之后的合并前核验阶段**，**不是** push 前可补齐的事项。本候选尚无 push/PR/CI，因此其状态是"**尚未到该阶段**"，既不是"已通过"，也不是"未通过"——本审查**未**把未执行的 CI 记为已通过，也**不**以 CI 结果缺失为由否定本轮候选的本地验收结论。
- **B-2（原生窗口矩阵在 CI 中只存在于 Linux）**：属候选 CI 配置的**已知覆盖边界**。原门禁对此要求的是"其余建议均有处理结论"，即**如实登记 + 给出归属**（归 Q2 首发平台与跨平台原生语义的产品/平台范围），**不**要求在 push 前实现跨平台原生矩阵；`ci.yml` 中 macOS/Windows 作业确实执行 `verify-i05-runtime.py`（我已复核 `ci.yml:117-149`），只有 `tests/e2e/i05-semantics.spec.ts` 的原生窗口 spec 因 `test.skip(process.platform !== 'linux')` 永久跳过。
- **B-1′（本轮唯一阻断）** 仍属"阻断问题全部关闭"这一 **push 前**前置条件，必须在 push 之前由开发方修复并形成新候选。

#### (5) 本轮更正的边界（明确声明）

1. **不改变判定**：C1 候选（head `043c20c…`）的结论仍是 **NotPass，1 阻断（B-1′）**。
2. **不由开发方指定阻断评级**：B-1′ 的评级依据是**我本人**在真实生产路径（`execute_request`）上复现的三个后果、其对 FR-500 / FR-203 / 附录C / PRD 12.3 的覆盖关系，以及"未在 Q6 登记中体现"这一事实；开发方本轮的补充说明**未被采纳为评级依据**，也未用于提升或降低任何发现的严重度。原 Goal 第七节亦要求"不得自行降低其阻断问题等级"，且对分歧应交下一轮独立任务重判——本轮**不**代行该机制。
3. **本 turn 只是同一 C1 候选的事实核实与报告更正**，**不构成**修复后 C2 所需的复审。C2 复审的前提是：开发方修复 B-1′ → 形成**新候选（新 head）** → 在该新版本上**新建两项独立全范围任务**（ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh）。本 turn 审的是固定的旧 head `043c20c…`，其结论**不得**被计入 C2 的复审通过，**也不**得被援引为"已复审通过"。
4. **未把未跑 CI 写成已通过**：§6 B-1 的事实陈述（"只有配置、没有远端结果"）保持不变，本节只是补上其**阶段归属**。

---

### 4.4 开发方新增反例材料与针对 ③ 的事实争议（2026-10-21 第三轮追加）——我独立核实、复现并裁定

开发方追加两份只读材料（真实 Store→coordinator→worker→不可变结果反例、纯查询数值词法反例），并同时提出一项针对我 §4.2(4)③ 的事实争议，要求我给出"应触发"的精确获准需求/语义依据。我**未采信其任何结论**，全部自行重跑、重测、重判。

#### (1) 材料完整性与我的独立复现

| 文件 | 声明 SHA256 | 实测 | 结论 |
|---|---|---|---|
| `round-1/store-lexical-counterexample.py` | `5891b8296c573e2b3ae4a0d0eb79caac15024954b9ef2dfc5946d4f9e8d76d32` | 同 | ✅ |
| `round-1/store-lexical-counterexample.json` | `b2cb4a0626b6ad380dd0ae98a1d47b82680dffd8303bd0615d5a7eb9a1b4e6a4` | 同 | ✅ |
| `round-1/query-numeric-counterexample.py` | `6aee4db0667c37d62b12360939d799197abf6975d420d02339107655deff108f` | 同 | ✅ |
| `round-1/query-numeric-counterexample.json` | `b97fc1f5860f61cc37684e00e383f459fd6627fba8e2a22791435cac8b16712e` | 同 | ✅ |

- **store 反例**：我以**自建 ignored 输出目录** `build/I05-review-C1-minimax/out/store-lexical-01` 运行（脚本只写调用方目录），exit 0、stderr 空；与开发 raw **结构等价**，差异**仅**为随机 UUID（`resultId`/`jobId`/`operationId`/`projectId`）与时间戳——我逐字段比对确认，无语义差异。
  - `validation.execute` → `report = {"conforms": true, "violations": []}` → **假阴确认**（事实 canonical `"1"`，约束允许值 `"01"`）
  - `query.execute` → `ASK { <urn:unit> <urn:p> 01 }` → `{"type":"ASK","value":true}`
- **query 数值反例**：我的 stdout 与开发 raw **逐字节相同**（SHA `b97fc1f5…b712e`）。

#### (2) 我加做的"非空洞"对照（结论依赖它，开发材料未含）

若 `sh:targetClass` 未命中，约束会**空洞通过**（`conforms=true`、`violations=[]`），假阳与假阴都会被掩盖。我另用 `sh:minCount 1` 的对照形状证明目标确实命中（违规记录 `focus = <urn:unit>`）。在此前提下复测：

| 事实（`<urn:unit> a <urn:Child>` 且 `<urn:unit> <urn:p> …`） | 引擎结果 | 应有结果 | 性质 |
|---|---|---|---|
| `"1"^^xsd:integer`（canonical） | `conforms=true`，violations=[] | **违规**（允许值集合为 {01}，"1" 不在其中） | **假阴** |
| `"01"^^xsd:integer` | `conforms=false`，InConstraintComponent 违规，`value = "01"^^xsd:integer` | **合规**（"01" 正是允许值） | **假阳（自相矛盾）** |

并直接观测到**用户保存的约束被静默改写**：引擎解析形状后，`sh:in` 列表首值是 `"1"^^xsd:integer`（用户保存的是 `"01"^^xsd:integer`）。这正是 FR-203「禁止静默丢弃/改变构造」与附录C「不得静默删减」所禁止的**已保存构造被改写**。

#### (3) 我自己的探针（`build/I05-review-C1-minimax/out/probe-lexical-20261021.py`、`probe-lexical2-20261021.py`，均为 ignored 目录内）

| 组 | 我的实测结论 |
|---|---|
| 字面量语义 | `Literal("01", XSD.integer, normalize=False) == Literal("1", …)` = **False**；`.eq` = **True**；哈希不同；Graph 查找区分二者 → **同值 ≠ 同项**（开发方该断言**属实**） |
| 规则层矩阵 | 事实 "1"：when "1" **触发**、when "01" **不触发**；事实 "01"：when "01" **触发**、when "1" **不触发** → 规则层**严格 RDF 项匹配** |
| 查询层矩阵 | 事实 "1"：裸 `01`→true、显式 `"01"`→false、显式 `"1"`→true；事实 "01"：裸 `01`→false、显式 `"01"`→true、显式 `"1"`→false → 查询层（BGP）**同样是项匹配** |
| 形状解析 | `sh:in ("01"^^xsd:integer)` 解析后首值 = `"1"^^xsd:integer`（**约束被改写**） |
| `-01.00` | 失败发生在 **rdflib 解析器**（`Not a number; Literal('1.00', datatype=xsd:decimal)`），引擎包装为受控 `INVALID_QUERY` → **可见错误**，非静默 |

#### (4) ③ 事实争议的裁定：**我接受更正，③ 不成立**

开发方指出我把 §4.2(4)③ 写成"应触发（同值同项）"，与候选已登记的合取三元组模式/RDF 项匹配可能冲突，要求我给出"应触发"的精确获准需求/语义依据。

**我没有这样的获准依据。我原来的预期是错的，特此更正。** 逐条依据：

1. **获准语义只有项匹配**：候选 Q6-08 明写「当前最小规则是**合取三元组模式**，支持存在与**等值常量匹配**，单条 Rule 一个结论」，并把 FR-505 的"属性值比较"登记为「**明确未覆盖，待负责人处置**」（我的 H-1 已独立记录）。故当前获准的规则匹配语义 = **结构三元组 = RDF 项匹配**，**未承诺**数值相等/值等价比较。
2. **"同值同项"本身自相矛盾**（我的措辞缺陷）：我实测 rdflib 中 `Literal("01", XSD.integer, normalize=False) == Literal("1", …)` 为 **False**，`.eq` 为 **True**，哈希不同、Graph 查找区分二者 → **同值但不同项**。我既写"同值"又写"同项"，二者不能同时成立。
3. **引擎内部三层一致**：查询层（BGP）、规则层、SHACL `sh:in`（SHACL REC §4.8.3 + §2.1.3，成员是列表项的 RDF 项）**全部按 RDF 项匹配**。规则层"异词法不触发"不是异常，而是与另两层一致的既定语义。
4. **正确的负例**：在当前有限语义下，规则 `when` 的字面量必须与事实字面量**逐字符相同**才触发；`when "01"^^xsd:integer` 对事实 `"1"^^xsd:integer` **不触发是正确行为**，应作为**负例**保留并写进回归测试。

**因此**：③ 从 B-1′ 的阻断依据中**移除**。这是本轮第二次由我自己的推理缺陷导致的更正（第一次为初稿 L-1），我一并记录，不掩盖。

**对开发方拟修方向的独立判断**：拟修"约束入口保词法 + 测试**同词法** when/then 触发、**异词法不触发**、假阳假阴均正确"——**不引入**任何数值相等/FR-505 表达扩展，恰好把③固化为受控负例，符合"不得为关闭③偷偷加入 Q6 未采纳的数值相等/FR505 表达扩展"的要求。**该方向正确且必要**，我确认。

#### (5) B-1′ 收窄后仍成立

B-1′ 现**仅**由 **①（假阳：违规值即允许值本身）** 与 **②（假阴 + 静默改写用户已保存约束）** 支撑。二者均已由开发方新材料在**真实 Store→coordinator→worker→不可变结果路径**上确认，并由我用 `sh:minCount` 对照证明非空洞。**判定不变：NotPass，1 阻断（B-1′，范围收窄）**。

#### (6) 规范取证（我取到的原文，以及一处**未取得**项）

- **语法（规范 §19 原文，我从 W3C 规范源码取得）**：`INTEGER ::= [0-9]+`、`DECIMAL ::= [0-9]* '.' [0-9]+`、`DOUBLE ::= ( ([0-9]+ ('.'[0-9]*)? ) | ( '.' ([0-9])+ ) ) EXPONENT`，另有 `INTEGER/DECIMAL/DOUBLE_POSITIVE/NEGATIVE`。→ `"01"` 是合法 INTEGER token；`"-01.00"` 是合法 DECIMAL token（`'-'` + `[0-9]* '.' [0-9]+`）。
- **§2.3.2（Informative，原文）**："Integers in a SPARQL query indicate an RDF literal with the datatype xsd:integer. For example: **42 is a shortened form of "42"^^<http://www.w3.org/2001/XMLSchema#integer>**."
- **§2.3.3（Informative，原文）**："…The query processor does not have to have any understanding of the values in the space of the datatype. **Because the lexical form and datatype IRI both match, the literal matches.**"
- **规范自身的效力约定（原文）**："Unless otherwise noted in the section heading, all sections and appendices in this document are normative."（§4.1.2 未标注 Informative，故为规范条款）
- **未取得项（如实登记）**：我**未**取到 §4.1.2 的**逐字正文**（抓取工具在规范中段截断，只拿到目录、§2.3 与语法部分）。因此我**不引用**该节的逐字句子；上面的结论由「规范语法 + §2.3.2 的缩短形式定义 + §2.3.3 的词法匹配 + 规范效力约定」推出。**我没有据此下任何阻断判定**（该结论只支撑 M-3 的非阻断判定与建议）。

#### (7) 本轮对判定的影响

- **B-1′ 阻断依据收窄**（移除 ③），**阻断本身不撤销**，判定仍为 **NotPass，1 阻断**。
- **新增 1 项非阻断发现 M-3**（查询侧裸数值 token 规范化，§4）。
- 本 turn 仍**只是同一 C1 候选**（head `043c20c…`）的事实核实，**不构成**修复后 C2 所需的新建双任务复审。

---

## 5. B1 原文逐项义务判定

> **本轮对 §5 的修正**：B1 原文"固定…最小真实 Turtle 解析、只读查询、RDFS/受控规则和 SHACL 检查"与"只承诺附录 C 的有限语义"两行，其判定由 ✅ 改为 **⚠ 受 B-1′ 影响**——受限语义在 `sh:in` 模板上的词法一致性未达成，且该差异未登记。其余各行维持初稿判定。

| B1 义务（原文要点） | 判定 | 依据 |
|---|---|---|
| 固定 RDFLib/pySHACL/规则实现候选的**完整依赖** | ✅ 满足 | `pyshacl==0.30.1`、`rdflib==7.6.0` 精确版本入 `pyproject.toml` 与 `uv.lock`；传递依赖 owlrl 7.6.2 / html5rdf 1.2.1 / prettytable / packaging / wcwidth 全部锁定；CI 用 `uv sync --frozen` |
| 先运行最小真实 **Turtle 解析、只读查询、RDFS/受控规则、SHACL 检查** | ⚠ **受 B-1′ 影响** | 真实库实现 + 完整 G.2 样例 + 拒绝矩阵；我本人实跑。但"SHACL 检查"在**允许值模板（`sh:in`）**上不成立：约束侧规范化、取值侧保真导致同值不同项，产出**错误验证结论**（§4.2 后果①②）；"只读查询"另有裸数值 token 规范化导致的静默失配（**M-3**）。**"受控规则"层本身不构成缺陷**：规则按 RDF 项匹配，异词法不触发是既定语义（§4.4(4) 裁定）。其余模板与样例不受影响 |
| 执行 `package:dir` 并**从产物内运行相同样例** | ✅ 满足 | 源码与包内 `--mode suite` 输出**逐字节相等**（我本人实测，SHA `2ae81bd9…`）；包内 `--semantic-probe` stderr 0 字节；`PATH=/usr/bin:/bin` 剥离开发 Python |
| 检查 **PyInstaller 隐式导入、资源/插件、动态库与许可证清单** | ✅ 满足 | `scripts/i05-build-inventory.py` 先跑且失败即停；`--collect-all rdflib/pyshacl/owlrl/html5rdf`、`--collect-data ontolearn_engine`、`--copy-metadata rdflib/pyparsing`、`--recursive-copy-metadata pyshacl`、`--add-data i05-inventory`；包内清单含 400 引擎文件、CPython LICENSE、native 来源原始字节与哈希；我复核 `uvLockSha256` 与许可文件 SHA |
| **实测** `SERVICE`、远程 `FROM`、解析器/验证器隐式外联均被拒绝，**不能用"配置关闭"替代证据** | ✅ 满足（**我独立复现**） | 正校准环回接收端先由我自己命中 1 次证明可达，再跑源码与包内两轮 28 例拒绝矩阵，**接收端命中数始终为 1（引擎零命中）**；真实 JSON-LD 隐式路径确实到达 `urllib.Request` 并被拒（证明守卫是运行时的，非开关声明）；SERVICE/FROM/FROM NAMED/BASE+file 全部拒绝 |
| 只承诺附录 C 有限语义，**不以库默认推理模式扩大** | ⚠ **受 B-1′ 影响** | 推理模式侧成立：`Validator(..., ont_graph=None, inference="none", advanced=False, use_js=False, iterate_rules=False, sparql_mode=False)`，直接调用真实 `Validator.run()`；OWL/RDFS/SHACL 白名单与命名空间前缀检查显式拒绝越界构造；未启用 OWL-RL 推理——**未扩大**。但承诺的"有限语义"在 `sh:in` 模板上的**比较语义未达成**（§4.2），且该差异**未在 Q6 登记中体现**，故"只承诺附录 C 有限语义"这一行不能判为完全满足 |
| **记录**包体、冷/热调用耗时、内存峰值、样例规模、设备、版本和原始测量值 | ✅ 满足 | 包体 37,632,518 B（引擎）/ 561,702,426 B（app）；两档 18/180 三元组、seed 20261019、输入/查询摘要 SHA、tracemalloc 峰值与 ru_maxrss、12+12 条 warm/fresh 测量、设备与全部库版本、方法自述；**我本人复测得到与记录逐值相同的 inputSha256/querySha256/三元组数** |
| **不编造**容量结论，等待 Q5 | ✅ 满足 | 测量对象自述"无容量阈值"；文档反复声明"不是业务容量基线""不把样例当容量阈值或量化性能提升" |
| **Q2 首发平台**（干净设备/无系统 Python/断网/签名）另行取证 | ✅ 正确登记为未取得 | 文档与证据 limits 明确列出；Mac 记录自述"unsigned development app-resource executable" |
| **不等待 Q6 冻结**即可进行候选验证 | ✅ 满足 | 12 行 Q6 全部保持开放，未代负责人决定；未把候选限制写成产品边界 |
| **必要真实 I04 接线**（Store/Job/worker/protocol/bridge/窗口联验） | ✅ 满足 | `semantic.start` 走协调器；接受事务内固定 immutable Job context；worker 私有分块通道（单帧 262144 B、重组 ≤8 MiB、逐字节 SHA 校验）；取消/超时/原子终态/迟到结果/幂等；窄 bridge + 主帧授权 + session-generation 复核；结果全量分页展示 |

**Q6 十二项逐项判断（判断"差异登记是否如实充分"，不代负责人决定）**

| 行 | 我的判断 |
|---|---|
| Q6-01 类型字面量/词法 | **登记不充分（需补记两处）**：① 原登记只覆盖"词法…不能扩推所有类型无损往返"，**未覆盖** B-1′ 的"允许值模板按 RDF 项比较导致的错误验证结论"与"用户已保存约束被静默改写"；② **未覆盖** M-3 的查询侧裸数值 token 规范化（`01`/`+1`/`01e+00` 失配、`-01.00` 被解析器拒绝）。建议补记 §4.2 与 §4 M-3 的完整适用范围与可达路径 |
| Q6-02 空白节点/列表 | 与实现一致：事实/本体空白节点拒绝；`sh:in` 列表经 `_shapes` 结构校验 |
| Q6-03 子类/domain/range 推理 | 与实现一致，我实测一阶段闭包与依据链 |
| Q6-04 禁 SERVICE/远程 FROM | **核心已实测通过**；需补登记 M-1 的 GRAPH 分类精度，**以及 M-3 的裸数值 token 规范化收窄**（SPARQL §2.3.2 的"缩短形式"在实现上不保词法） |
| Q6-05 结果分页/限量 | 如实登记：文本 LIMIT/OFFSET 拒绝属语法收窄，**未撤销** FR-402 的服务分页要求；产品侧分页已接线并实测 |
| Q6-06 函数/聚合范围 | 拒绝侧与实现完全吻合；**需补接受集清单（M-2）** |
| Q6-07 确定性/排序 | 与实现一致，我实测 5 次重复逐字节相同 |
| Q6-08 FR-505 比较/多结论 | **确认未覆盖**（H-1）。候选登记为"明确未覆盖、待负责人处置"，未宣称完成 |
| Q6-09 规则单阶段/顺序无关 | 与实现一致，我实测链不触发、顺序颠倒结果相同 |
| Q6-10 有限 SHACL 模板 | **登记与实现不一致（须更正）**：原登记"模板集全部产生真实 pySHACL 违规"在**其余 5 个模板**上成立，但在**允许值模板 `sh:in`** 上不成立——该模板在合法可达输入上**假阳性**（违规值即允许值本身）、**假阴性**（约束被静默改写为 `{1}` 后放行 `{1}`），已在真实 Store→coordinator→worker→不可变结果路径上确认（§4.4(1)(2)）。此行必须改写为"允许值模板存在词法一致性缺陷，未覆盖" |
| Q6-11 两范围/版本记录 | 与实现一致：asserted 与 asserted+selected-derived 两范围、既存结果身份核验、不重算；FR-500 产品流程仍未完成（已登记） |
| Q6-12 导入/编辑/解释/导出各列 | **确认未实现**；UI 明写"当前没有项目创建或定义编辑流程"；未把未做列标成通过 |

---

## 6. 未取得 / 未复现的边界（如实登记，均不构成本轮阻断）

> **编号说明**：本节的 B-1…B-6 是**「未取得/未复现的证据边界」**编号（初稿即有，指证据缺口），与 §4.2 的 **B-1′「阻断问题」**编号属**不同命名空间**，两者不构成冲突、不可互相抵消：B-1…B-6 表示"某些证据本轮未取得"，B-1′ 表示"某个已定位的缺陷必须关闭"。本节各项**均不构成本轮阻断**，本轮阻断**仅**来自 B-1′。

| 编号 | 边界 |
|---|---|
| **B-1** | **三平台 CI 从未实际执行。** 本候选无 push/PR，`ci.yml` 新增的 I05 步骤（Linux xvfb/openbox 下 `tests/e2e/i05-semantics.spec.ts` 源码与包各 2 项；三平台 `verify-i05-runtime.py`）只有配置、没有远端结果。候选自身 `integrated-c1-verification.md:41` 已如实登记此项未取得。**阶段归属见 §4.3**：此项属 **push/PR 之后的合并前核验**，不是 push 前可补齐事项；本候选状态为"尚未到该阶段"，**既未记为已通过，也未记为未通过** |
| **B-2** | **I05 原生窗口矩阵在 CI 中只存在于 Linux。** `tests/e2e/i05-semantics.spec.ts:109-112`、`:342-345` 的 `test.skip(process.platform !== 'linux' \|\| …)` 使 macOS/Windows 的 `npm run test:e2e` 永久跳过该 spec，故跨平台原生窗口语义矩阵在 CI 中不存在（`ci.yml:117-149` 的 macOS/Windows 作业仍执行 `verify-i05-runtime.py`）。属**已知覆盖边界**，按原门禁要求"有处理结论"即可（如实登记 + 归属 Q2/平台范围），**不要求 push 前实现**（§4.3(4)） |
| **B-3** | native 许可来源仅匹配 macOS PBS CPython 3.12.12 与 Linux aarch64 CPython 3.12.15；其他运行时 `nativeLicenseProvenanceMatched=false` 保持 pending（`verify-i05-runtime.py` summary 的 limits 已明写） |
| **B-4** | 首发平台签名/干净设备/无系统 Python/断网安装、生产环境、容量阈值，以及 Q2/Q3/Q5/Q6/Q7/Q8/Q9 的负责人结论**全部未取得**；本审查不代为决定 |
| **B-5** | **本 Mac 未执行 Electron/e2e/native/HMR**（无桌面打扰约束）。Linux 原生结论我只读原始证据并核验其内部一致性、117/14 条清单哈希与 198 条执行输入绑定，**未由我本人复现** |
| **B-6** | 409 条 Linux 构建产物哈希（`bindings/linux-linkage-and-source.json.raw`）与 982 条 Docker↔提交逐文件比对**无法在本 macOS worktree 重新推导**（相关产物不在此工作树） |

---

## 7. 架构不变量核查（我本人逐项核对）

| 不变量 | 结论 | 依据 |
|---|---|---|
| 本地优先：不自动启用模型/遥测/云；不开 HTTP 端口 | ✅ | 产品引擎无监听器；环回接收端仅存在于验证脚本（测试专用，非产品服务）；引擎无模型调用 |
| 渲染端隔离：renderer 不用 Node/FS/shell/通用 IPC | ✅ | `App.tsx` 只用 `window.ontolearn`；preload 暴露 `runSavedQuery`/`runReasoning`/`runValidation` 等业务命名方法，**无 `invoke(method, params)` 式通道**；e2e 断言无 `invoke`/`createJob`/`semanticStart` |
| CSP 只改一处、不得出现 unsafe-inline/eval | ✅ | `apps/desktop/src/csp.ts` **零 diff** |
| IPC sender/mainFrame/可信文档校验 | ✅ | 新增三个 semantic 路由统一走既有 `trusted(event)`（`main/index.ts:142-149`、`:183-187`），未绕过 |
| 确定性结果只来自真实引擎；Agent 不自动确认自己的修改 | ✅ | 结果只由真实 worker 产出；本轮无 Agent 参与写入 |
| SQLite 为唯一可变源真相；正式写入只经 `Store.commit` | ✅ | 语义路径**不改项目状态**，只发布结果 + payload + 来源哈希，与 Job succeeded **同事务**（`job_store.finish_semantic_job`）；RDFLib 图只从不可变快照重建，不写回 |
| 数据层次：本体/事实/推导/场景/历史分层；历史不可改写 | ✅ | `storage.py`、`invalidation-v2.json` 零 diff；迟到结果保留原输入、按依赖成为 stale/history |
| `staleReason` 只来自 `invalidation-v2.json`；仅改模型配置不使领域结果过期 | ✅ | 失效注册表与实现零 diff；`resources.py` 仅把 `executionSemanticsVersion` 由 `i04-infrastructure-v1` 改为 `i05-finite-3` |
| 错误只传固定错误码与受限参数，不回传原始异常/路径/单元格原值 | ✅ | `SemanticErrorAdapter` 绑定 canonical catalog/schema，未知原因一律 `INTERNAL_ERROR`；`semantic_offline` 过滤 rdflib 字面量诊断日志；e2e 断言 canary 不出现在错误 JSON |
| C4 保留：owner bootstrap / 严格环境 / 资源 / 终止界限 | ✅ | `engine.ts`、`window-security.ts`、`trusted-document.ts`、`window-recovery.ts`、`view-navigation.ts`、`memory_guard.py`、`process_environment.py` **全部零 diff**；worker 的 owner 监控与内存守卫未被绕过 |

---

## 8. 最终判定与理由

### 判定：**不通过（NotPass）— 1 个阻断问题（B-1′，§4.2）**

**理由：**

1. **存在 1 个已定位、可复现、尚未关闭的阻断缺陷（B-1′）**。允许值模板（`sh:in`）在**真实生产路径**（Store→coordinator→worker→不可变结果）上对合法用户输入产出**错误验证结论**：**假阳性**（违规报告的 `sh:value` 正是允许值列表里的那一个）与**假阴性**（同时**静默改写用户已保存的约束**——用户写 `sh:in ("01")`，引擎实际检查 `sh:in ("1")`）。该缺陷触及 FR-500「不得展示为已通过」、FR-203「禁止静默丢弃/改变构造」、附录C「不得静默删减」与 PRD 12.3 覆盖的禁止项，且**未被候选的 Q6 登记体现**（§4.2、§4.4）。
2. **Goal 门禁直接适用**：「阻断问题尚未关闭，或关键验收仍无法验证时，**不得出具通过**」。B-1′ 尚未由开发方修复并形成新候选，本审查**不得**在关闭前出具 Pass。
3. **判定改变仅因 B-1′，与本轮其他材料无关**：§4.1 的来源事实更正经我独立核实**属实**，且**不改变**任何义务判定；初稿 Pass 的其余事实基础（§8.2）**依然成立**，修复 B-1′ 后无需重做这些结论。
4. **本判定的范围是清晰的**：除 `sh:in` 允许值模板外，其余 5 个 SHACL 模板、全部 SPARQL/RDFS/规则语义、全部架构不变量、外联拒绝证据链、源码/包内同样例一致性、附录 G 固定样例与 1511/672 测试结论**均不受影响**；本轮**不**主张任何安全或外联后果、**不**主张数据损坏。
5. **本轮范围收窄（不改变判定）**：§4.2(4)③ 的"规则 `when` 异词法不触发"经我独立裁定**不构成缺陷**（规则层按 RDF 项匹配是既定且与查询层、SHACL 层一致的语义），已从阻断依据中**移除**；本轮新增 **M-3**（查询侧裸数值 token 规范化）为**非阻断**。B-1′ 现仅由 ①② 支撑，**仍然成立**。

### 8.1 复审通过的必要条件

1. **修复 B-1′** 并形成**新候选**（新 head），修复方向见 §4.2 末段（约束入口保词法，或对非规范 typed literal 显式拒绝并给固定安全错误）。
2. **补回归测试**：允许值模板的**假阳一例**、**假阴一例**；规则 `when`/`then` 的**同词法触发一例**与**异词法不触发一例**（后者是 §4.4(4) 裁定的**负例**，必须断言"不触发"，不得为凑"通过"而改成数值相等）。
3. **更正 Q6 登记**：Q6-10 行改写为"允许值模板存在词法一致性缺陷"；Q6-01 行补记 §4.2 的适用范围与可达路径；Q6-01/Q6-04 另需补记 **M-3** 的查询侧收窄。
4. **M-3 须独立处置**（登记或修复）：开发方拟修的"约束入口保词法"**不覆盖查询侧**；须在查询解析入口保词法或对非规范数值 token 显式拒绝给固定安全错误，并补裸 `01`/`+1`/`01e+00`/`-01.00` 的完整矩阵。
5. **由双方对同一新候选重新执行完整范围审查**（不得沿用本次对旧 head 的通过结论）。
   - **本 turn（§4.3 的门禁时序事实核实、§4.4 的材料核实与 ③ 裁定）都不是 C2 复审**，其结论不得计入第 5 项；C2 必须在修复后的**新 head** 上**新建两项独立全范围任务**后另行执行。

> **push 前置条件与本判定的关系**：按原 Goal 第六节（§4.3(2)），push 的前置条件为"验收与必要验证通过 + 同版双模型明确通过 + **阻断问题全部关闭** + 其余建议有处理结论 + 待推送实现与受审实现一致"。**CI 结果不在 push 前置条件内**，它在 push/PR 之后、正常合并之前核验。本轮**唯一**阻断 B-1′ 属"阻断问题全部关闭"，因此 C1 候选当前**不可 push**；B-1/B-2 的阶段归属更正（§4.3）**不改变**这一结论。

### 8.2 初稿 Pass 判定的事实基础（保留历史，仍然成立）

初稿（报告 SHA `cdd27463…`，随后 `03fd0f89…`）判定 **Pass**（0 阻断），其理由如下。**这些理由除受 B-1′ 影响者外均未被本轮推翻**，一并保留以备复审对照：

1. **B1 原文四段义务逐项满足**，且最关键的两项——"实测外联拒绝、不得用配置关闭替代证据"与"源码与产物内运行相同样例"——由我**独立复现**（正校准可达接收端零命中；源码/包内 suite 输出逐字节相同）。**本轮修正**：其中"最小真实 Turtle 解析、只读查询、RDFS/受控规则、SHACL 检查"与"只承诺附录 C 有限语义"两行因 B-1′ 改判为 ⚠（§5）。
2. **必要真实 I04 接线确实存在且被真实验证**：Store/Job/worker/protocol/bridge/窗口链路与取消、超时、原子终态、迟到结果、幂等、稳定分页均有实现与运行证据。**本轮维持成立**。
3. **无阻断问题**。**本轮修正**：此条被 B-1′ 推翻——初稿把 `sh:in` 当作值语义比较，从而低估了词法规范化的后果，该推理缺陷已在 §4 L-1 与 §4.2 中显式记录。其余 H-1（候选已如实登记为未覆盖的产品决定项）、M-1/M-2（分类精度与登记清单完整性，不触及安全边界或验收结论）、L-2/L-3/L-4（低影响观察）维持非阻断。
4. **证据链自洽且可核**：candidate-1.json 365/1126/198 逐条重算全匹配；证据清单 117/14 全匹配；sealed 绑定 198=198=198；受保护文件零混入；候选头相对 851be57 仅追加证据与文档，**生产源码未变**。**本轮维持成立**（§4.1 末行三段清单再次重算全匹配）。
5. **失败与限制未被抹除**：历史失败日志、namespace 权限失败、inspector 未就绪失败、未签名 skip 均原样保留并有对应后续通过日志。**本轮维持成立**。

### 8.3 与初稿并列仍然有效的放行附带约束（不因改判而失效）

> **本轮已更正本节首条的时序表述**（原措辞"B-1/B-2 必须在 push/PR 前补齐"有误，详见 §4.3）。按原 Goal 第六节，正确时序为：本地完整验证 + 同版双审明确 Pass + 阻断问题全部关闭 + 其余建议有处理结论 + 待推送实现与受审实现一致 → **才 push** → PR → **实际三平台 CI 核验** → 正常合并 → 远端核验 → Goal 完成。CI 结果**不在** push 的前置条件内。

- **B-1（三平台 CI 从未实际执行）属 push/PR 之后的合并前核验阶段，不是 push 前可补齐的事项。** 本候选尚无 push/PR/CI，状态是"**尚未到该阶段**"——我**未**把它记为已通过，也**不**以 CI 结果缺失为由否定本轮候选的本地验收结论。它进入原门禁的位置是"PR→develop、**实际 CI 全部成功**、正常合并并核验远端，才能完成 I05 Goal"。**本轮唯一的 push 前阻断是 B-1′**（§4.2），须在 push 之前关闭。
- **B-2（原生窗口矩阵在 CI 中只存在于 Linux）属已知覆盖边界**，按原门禁需"有处理结论"——即如实登记 macOS/Windows 无 I05 原生矩阵这一事实，并将其归属到 Q2 首发平台与跨平台原生语义的产品/平台范围；**不要求**在 push 前实现跨平台原生矩阵。
- **H-1 的 Q6-08 结论必须在产品采用层保持显式**：`query.execute/reasoning.execute/validation.execute` 已进入 `productRuntime` 且 `implementation=runtime`，若后续产品文案省略"FR-505 比较语义与单条多结论未覆盖"，将违反 FR-500 与附录 C「不得静默删减」。
- **M-1/M-2 建议在下一候选前修订**：前者是错误分类精度，后者是 Q6-06 负责人逐项采用所需的清单完整性。
- **B-3…B-6 保持 pending，不得在任何汇报中升级为已通过**。

---

## 9. 审查者自陈的局限

1. 本轮**未运行** Electron/e2e/native/HMR，无窗口/原生结论全部为只读原始证据的核验，不是我的复现；**原生（Linux）结论我只读原始产物并核验其内部一致性，未由我本人复现**，跨平台原生语义矩阵在 CI 中亦不存在（B-2）。
2. 未逐行通读 53 个上游许可原字节正文与全部大体量 `.raw` 产物；这些以清单 SHA 逐条重算与关键日志内容通读的方式核验。
3. **未运行 `npm run build`**（会改 `apps/desktop/out`，超出本轮写入界限），构建/打包产物以只读方式核验；同理未运行 `package:dir` / `engine:build`。
4. 思考程度 xhigh 与原生任务 UUID 为派发方声明，我未在 UI 侧独立复核，也未编造。
5. 本报告是**独立判断**，未参考本轮另一审查者的任何 prompt、过程、报告或结论。
6. **本轮反例核实的范围**：我对 SHACL 词法反例的核实限于 `sh:in` 允许值模板与规则 `when`/`then` 词法一致性的**可达性、后果与影响半径**；我用真实 `execute_request` 生产路径复现了三个后果，并逐个验证了 `sh:datatype`/`minInclusive`/`maxInclusive`/`minCount`/`maxCount` 不受影响。**未**覆盖：其余未列入的 SHACL 高级构造（复杂路径、JS、SPARQL 约束——候选已声明不支持）、其他 typed datatype 的完整词法矩阵、以及非 typed literal 的比较语义。若开发方修复后扩大词法处理范围，我本轮的"其余模板不受影响"结论需重新评估。
7. 我对 B-1′ 的判定基于**当前实现**（`parse_turtle` 规范化 + `_LexicalSink`/`_term()` 保真 + pySHACL 0.30.1 的项比较）。修复后这些前提会变化，**复审须重新执行**而非沿用本节结论。
8. §4.3 的门禁时序核实范围：我核对了 `goal-objective.md` 第六节、`scope.md:44/:48`、`full-review-input.md:25/:57/:84` 与 `ci.yml:66-149`，**只校正时序归属**；我**未**重新评估 CI 配置本身的正确性（`ci.yml` 是否覆盖了 B1 要求的全部验证点）、**未**评估三平台 CI 在真实远端的行为、也**未**核验任何 CI 实际结果（因为本候选尚无 CI 可核）。这些仍属 §6 B-1/B-2 的 pending 边界。
9. **我本轮第二次由自身推理缺陷导致的更正**（§4.4(4)）：初稿 L-1（"值等价比较 ⇒ 判定不受影响"）与本轮 §4.2(4)③（"规则异词法应触发"）都是我的推理错误。两处均已在报告中保留原文并标注更正，不抹除历史。**根因**是我把"值等价"与"项等价"混用；更正后我的结论建立在实测的 rdflib 项语义与候选已登记的有限语义之上。
10. **规范取证的未取得项**：我**未**取到 SPARQL 1.1 §4.1.2 的**逐字正文**（抓取工具在规范中段截断）。我的规范性结论仅依赖我**实际取到原文**的四项：规范 §19 的 `INTEGER/DECIMAL/DOUBLE` 语法 productions、§2.3.2 的"42 是 "42"^^xsd:integer 的缩短形式"、§2.3.3 的"词法形式与 datatype IRI 都匹配才匹配"、以及规范"除标题另注外全部条款为规范条款"的效力约定。**M-3 的非阻断判定不依赖 §4.1.2 逐字正文**；若该节正文另有"数值 token 可被实现规范化"的许可条款，M-3 的**严重度**需相应复核（我未据此下任何阻断判定）。
11. **M-3 的核实范围**：我覆盖了整数（`01`/`+1`）、double（`01e+00`）、decimal（`-01.00`）在查询文本中的行为，以及 canonical 与非规范词法事实的对照。**未**覆盖：非数值字面量（字符串、日期、布尔）的查询侧词法保真、SPARQL `FILTER`/函数中的数值运算、以及 `xsd:float`/`xsd:nonNegativeInteger` 等白名单内其他数值类型。

---

## 10. 冻结与零漂移声明

审查全程未修改任何受审实现、测试、配置、依赖、验收或基线；未提交、未推送、未切分支；未创建 Goal 或功能会话；未写入 `state.json` 或其他 worktree。**唯一主树写入为本文件**。所有临时产物位于自建目录 `build/I05-review-C1-minimax/`（`tmp/`、`out/`、`venv/`）。

审查结束时复核（我本人执行）：

```
git status --short
 M AGENTS.md
?? docs/reviews/I05/candidate-1.json
?? docs/reviews/I05/round-1/

AGENTS.md                                    db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786
docs/reviews/I05/round-1/full-review-input.md  a3ccbc7b4e01ad704dab1c1263c0974c120db929f3bec02b6aa0111d5b3ceaf3
docs/reviews/I05/candidate-1.json           91e48255347f0abd123be79370e6a6d8e16debe4e6c4a5376101a5f91e992874
docs/reviews/I05/protection-c1.json         f98d96c797415c8487104c7946932473ce62a9c82035bd75797f2be4cc4ada02
docs/reviews/I05/round-1/source-lineage-note.json  cc0a94a05fc5fd46eba985e1ae9817e55db04bb3e9bcfc49a419414d48ca12fe
docs/reviews/I05/round-1/shacl-lexical-counterexample.py  37ff6ab298a5c6e33c9672948d905c335e35beda9b0250d17d7a35af70a4e1af
docs/reviews/I05/round-1/shacl-lexical-counterexample.json 42704db646eed1ecd96150577852e72e5005c9d616148d5f0130801e7eace15e
docs/reviews/I05/round-1/store-lexical-counterexample.py 5891b8296c573e2b3ae4a0d0eb79caac15024954b9ef2dfc5946d4f9e8d76d32
docs/reviews/I05/round-1/store-lexical-counterexample.json b2cb4a0626b6ad380dd0ae98a1d47b82680dffd8303bd0615d5a7eb9a1b4e6a4
docs/reviews/I05/round-1/query-numeric-counterexample.py 6aee4db0667c37d62b12360939d799197abf6975d420d02339107655deff108f
docs/reviews/I05/round-1/query-numeric-counterexample.json b97fc1f5860f61cc37684e00e383f459fd6627fba8e2a22791435cac8b16712e
git diff --name-only base...head | wc -l      365
HEAD                                         043c20cc7934191339a8814c79666dbd2e94a62a
```

受保护指南仍为 dirty 且未 stage；共同输入、candidate 清单、保护清单、来源说明与反例材料的 SHA 均与声明一致；受审范围仍为 365 文件。**本轮两项追加材料到达后与收尾时，我都再次重算 candidate-1.json 的三段清单：`files` 365/365、`fullTrackedFilesExceptProtectedGuidance` 1126/1126、`executionInputs` 198/198 —— 全匹配，零不匹配、零缺失**（§4.1 末行）。本审查全程未向受审 365 文件集写入任何内容。

---

## 11. 本轮最终状态

| 项 | 值 |
|---|---|
| 审查范围（固定） | base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → head `043c20cc7934191339a8814c79666dbd2e94a62a` |
| 分支 / 工作区 | `feature/I05-semantic-validation` ／ `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation` |
| 变更集规模 | 365 files changed, 592153 insertions(+), 46 deletions(-) |
| 唯一主树写入 | `docs/reviews/I05/round-1/minimax-m31flash.md`（本文件） |
| **最终判定** | **不通过（NotPass）— 1 个阻断问题：B-1′（§4.2）** |
| 阻断项 | B-1′：SHACL 允许值模板（`sh:in`）词法不一致 → **假阳**（违规值即允许值）与**假阴**（用户已保存约束被静默改写）；真实 Store→coordinator→worker→不可变结果路径可达；**未在 Q6 登记中体现**。**本轮已移除原 ③（规则异词法不触发），阻断依据收窄为 ①②，阻断不撤销** |
| 非阻断发现 | H-1、M-1、M-2、**M-3（本轮新增）**、L-2、L-3、L-4（7 项）+ 观察 O-1…O-6 |
| 未取得边界 | B-1…B-6（6 项，与 B-1′ 不同命名空间，§6） |
| 复审必要条件 | 修复 B-1′ → 新候选 → 补三类回归 → 更正 Q6-01/Q6-10 → 双方对同一新候选重新全范围审查（§8.1） |
| 最终报告 SHA256 | 本文件定稿内容的 SHA256（**自指哈希无法内嵌于文件自身**），以 `shasum -a 256 docs/reviews/I05/round-1/minimax-m31flash.md` 实测值为准，并在本轮交付消息中给出 |
| 本轮附加事实核实 | 门禁时序澄清（§4.3）：更正我原报告"CI 须在 push/PR 前补齐"的时序表述。**不改变判定、不改变 B-1′ 评级、不构成 C2 复审** |
| 本轮第三轮追加 | 开发方新增 store/query 反例材料（§4.4）+ 针对 ③ 的事实争议。**我接受更正**：③ 不成立并从阻断依据移除；B-1′ 阻断**收窄但不撤销**；新增非阻断 **M-3**。**判定不变：NotPass，1 阻断**；**不构成 C2 复审** |

**本轮判定序列（完整保留）：**

1. `cdd27463cbe87925b70723e37557fe307793ed137add55d40c9a305b64094e44` — 初稿，**Pass**，0 阻断。
2. `03fd0f8983fe3131137cbeea48eac72ee158389b0e00a3cc24594fbf8a67e0f1` — +来源事实更正（§4.1），核实属实，**维持 Pass**，0 阻断。
3. 本轮 — +SHACL 词法反例（§4.2）：我独立复现并证明该根因在**真实生产路径**可达，**改判 NotPass**，1 阻断（B-1′）。初稿 L-1 的"值等价比较 ⇒ 判定不受影响"推理被判定为**本人审查缺陷**，已在 §4 L-1 与 §4.2 中显式记录并保留原文。
4. 本轮附加 — 门禁时序事实澄清（§4.3）：**判定不变（NotPass，1 阻断 B-1′）**；仅更正我在 §8.3/§8 的 CI 时序表述，并补上 B-1/B-2 的阶段归属。**未**把未执行的 CI 记为已通过；**未**采纳开发方的任何评级意见；**本 turn 不充当修复后 C2 所需的新建双任务复审**。
5. 本轮第三轮追加 — 新增 store/query 反例材料 + ③ 事实争议（§4.4）：**判定不变（NotPass，1 阻断 B-1′）**。**我接受对 ③ 的更正**：原表述"规则异词法应触发（同值同项）"错误（我的第二次推理缺陷），③ 已从阻断依据移除；B-1′ 收窄为 ①② 且经真实 Store→coordinator→worker 路径确认后**仍然成立**。新增非阻断 **M-3**（查询侧裸数值 token 规范化）。本 turn 仍**不是 C2 复审**。
