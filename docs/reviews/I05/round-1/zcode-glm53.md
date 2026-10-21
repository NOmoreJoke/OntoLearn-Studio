# I05 / B1 C1 第一轮独立只读审查报告（ZCode · GLM-5.3 · 最高思考）

- 审查者任务标识：I05-C1-ZCode-GLM53-043c20cc7934191339a8814c79666dbd2e94a62a（派发关联标签，非原生 UUID）。
- 派发方式：开发会话原生 UI 现场选择精确 worktree/分支/模型设置（派发方声明）；本审查者仅能区分"派发方 UI 实查声明"与自身可见设置，未观察到与本声明矛盾的证据，不编造不可见的原生任务 UUID 或设置。
- 报告路径：`docs/reviews/I05/round-1/zcode-glm53.md`（本文件，本人唯一主树写入）。
- 结论速览：**Pass（附 2 项 P1 材料性发现，须新候选修复并纳入 Q6 处置；详见 §7）**。

## 1. 实际身份与核对结果

| 项 | 实查结果 |
| --- | --- |
| 工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation`（pwd 实查） |
| Git 根 / 分支 | 同一路径即 Git 根；`feature/I05-semantic-validation` |
| HEAD | `043c20cc7934191339a8814c79666dbd2e94a62a`（与受审 head 一致） |
| 受审范围 | base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → head `043c20c…`，26 个提交、`git diff --name-only` 实数 **365** 个变更文件，与 candidate-1.json 一致；非只审 6b/851 增量 |
| 共同输入 | `full-review-input.md` SHA256 `a3ccbc7b4e01ad704dab1c1263c0974c120db929f3bec02b6aa0111d5b3ceaf3`（40684 bytes / 277 行，逐行读完）；`input-manifest.json` 与之一致 |
| candidate-1.json | SHA256 `91e48255347f0abd123be79370e6a6d8e16debe4e6c4a5376101a5f91e992874`，实查一致 |
| 零漂移 | candidate 内 365 变更文件、1126 非保护跟踪文件、198 执行输入逐一 SHA256 比对工作树：**全部一致（开始时与报告落笔前各复核一次，均 0 漂移）** |
| AGENTS.md | 实体 SHA256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，dirty 未 stage，与保护声明一致；未作为产品改动混入 |
| 工作区 | 仅 `AGENTS.md`（保护指南）、未跟踪的 `docs/reviews/I05/candidate-1.json`、`docs/reviews/I05/round-1/`（共同输入与本报告）及被 gitignore 的本人 `build/I05-review-C1-zcode/`；无其他会话未提交改动混入 |
| 写入纪律 | 本人唯一主树写入即本报告；未修改任何受审实现/测试/配置/依赖/验收/基线，未提交/推送/切分支，未创建 Goal，未操作任何审查/其他应用 UI。所有独立 export/venv/npm/缓存/TMPDIR/输出均在 `build/I05-review-C1-zcode/` 下新建（uv venv、npm ci 于 `git archive` 导出的独立树、独立 uv/npm 缓存）；主树运行一律 `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider`，复核确认未在主树新增缓存（现存 `__pycache__` 均为开发线历史产物且 gitignored）。未读取另一位审查者的 prompt/过程/报告/结论（round-1 下 `minimax-*` 文件未打开）。 |

## 2. 完整范围与已读需求

完整读取（非摘要）：`inputs-c1/scope.md`、`policy.md`、`parallel-coordination.md`；PRD V0.6 附录 C/D/E/G 全文与 FR-200/203/300-304/400-406/500-506/600-604/700-705/800-806/900-904/1000-1001、§8.6/8.7、§10、§16（Q1-Q10）；`m0-review-and-update-plan-2026-10-19.md` 的 B1 全文、S1/S2 交付与退出门槛、Q6 决策检查点；ADR-0001、ADR-0002（I01 目录）、ADR-0003；I05 的 `integrated-runtime.md`、`acceptance.md`、`q6-candidate-differences.md`（十二行逐行）、`selected-result-projection.md` 引用关系；`integrated-c1-verification.md`、`status.md`；共同输入末附原 launch、resume 交接、完整 goal-objective（含第九节）。

逐文件审查的受审代码（base→head 全量 diff + 关键文件全文）：引擎 7 个新语义模块（semantic / semantic_offline / semantic_execution / semantic_scopes / semantic_error_adapter / semantic_samples / semantic_probe）与 5 个修改（coordinator / job_store / worker / protocol / resources）、entrypoint.py、pyproject/uv.lock（pyshacl==0.30.1 固定）；contracts（v2.ts / index.ts / contract_v2.py / registry / schema / fixtures）；desktop（task-service.ts / index.ts / preload / App.tsx）；测试（引擎 10 个测试文件、semantic-bridge.test.ts、contract-v2.test.ts、i05-semantics.spec.ts 全文 544 行）；scripts 5 个；CI workflow；licenses 目录抽样与 provenance。

## 3. 独立执行命令、真实结果与证据来源区分

**本人实测（均在隔离环境，退出码真实）**：

| # | 命令（隔离方式） | 结果 |
| --- | --- | --- |
| 1 | `uv sync --frozen`（UV_PROJECT_ENVIRONMENT/UV_CACHE_DIR 指向自有 build 目录） | 建立独立 venv；rdflib 7.6.0、pyshacl 0.30.1 与锁一致 |
| 2 | 引擎全量 pytest（自有 venv，无缓存写入主树） | **1511 passed in 56.43s**，exit 0；与开发证据 `check-final.txt.raw`（1511 passed）一致 |
| 3 | `ruff check` + `ruff format --check`（engine+scripts） | 全部通过 / 58 files already formatted |
| 4 | `scripts/verify-i05.py --packaged release/mac-arm64/.../ontolearn-engine`（真实包内 CLI，只读包） | exit 0：`parity:true`、12 条原口径 + 12 条 fresh 测量、网络正校准 1 / 拒绝命中 **0** / 每运行时 28 拒绝用例、`engineBytes 37,632,518`、`appBytes 561,702,426` —— 与文档记录逐字节一致 |
| 5 | 包内引擎 SHA256 | `71d4b4bc…b32d9`，与 integrated-c1-verification.md 记录一致 |
| 6 | `scripts/verify-i05-runtime.py release/mac-arm64`（自有输出目录） | exit 0：suite 完整输出源/包相等、真实 stdio 三能力落库 exit 0、native 许可 provenance `matched exact macOS arm64 runtime` |
| 7 | TS 隔离树（`git archive 043c20c` 导出 + 自有 npm cache + `ELECTRON_SKIP_BINARY_DOWNLOAD=1` + 自建 .venv）`npx vitest run` | **672 passed (16 files)**，exit 0（初次 8 个失败系隔离树缺 `.venv` 的环境问题，自建后全过；与开发证据 672 一致） |
| 8 | 同树 `npm run typecheck` / `npm run lint` / `npx prettier --check .` | 全部通过，exit 0 |
| 9 | 同树 `npm run verify:sources` | 12 份归档源一致，exit 0 |
| 10 | 对抗探针 22 组（SERVICE/FROM 藏于 FILTER EXISTS、子查询嵌套；LIMIT/OFFSET 子查询；ORDER BY 表达式/非投影变量；SUM/AVG/MIN；CONSTRUCT/DESCRIBE/INSERT/DELETE；BNODE/扩展函数；owl/rdfs 前缀走私；未知 datatype、NaN/INF、空白节点、相对 IRI） | **全部按预期拒绝**（EXTERNAL_ACCESS_DENIED / QUERY_SLICE_UNSUPPORTED / UNSUPPORTED_QUERY_ORDER / UNSUPPORTED_QUERY_FUNCTION / READ_ONLY_QUERY_REQUIRED / INVALID_QUERY / UNSUPPORTED_OWL / UNSUPPORTED_RDFS / UNSUPPORTED_LITERAL_DATATYPE / UNSUPPORTED_NONFINITE_LITERAL / UNSUPPORTED_BLANK_NODE / INVALID_TURTLE）；图内只读属性路径放行（符合设计） |
| 11 | 变量谓词规则输出 / 变量类目标规则 | 前者 UNBOUND_RULE_VARIABLE 拒绝；后者仅允许纯领域 URI 类（公理谓词被 `_rule`+`_terms` 阻断） |
| 12 | 三项新增反例脚本独立复现（见 §6） | 全部复现，与开发方 raw 语义一致 |

**开发证据（只读核验，未重跑即引用的部分）**：`evidence/integrated-c1/manifest.json` 117 份原字节文件 SHA 逐一比对**全部一致**；`integrated-c1-sealed/manifest.json` 14 份**全部一致**；`source-binding.json` 198 份执行输入 `linuxMismatches=0`、`productionInputChanges=0`、`laterChangedHarnessFiles=1`（仅 e2e harness）；sealed native 证据（源/包各 1 份）实读：`result=PASS`、`events=[crashed,unresponsive]`、3 窗口全 visible、第 2 窗口 `focused=true` 且 xdotool/XGetInputFocus 外部焦点记录、两个真实 GTK 恢复对话框（`OntoLearn Studio 窗口恢复`，外部键盘操作）、`hangMonitorEnabled=true`、`noSandboxSwitch=false`、`inspectorClosed=true`、三时点不可变结果 SHA 相同、后台 COUNT worker 显式取消；源/包 native 各 2 tests passed（23.4s/24.4s）。check-final.txt.raw 尾部 1511 passed。以上均为开发线产物，本人以 SHA/内容核验采信，运行结果以本人 §3 表中实测为准。

## 4. 逐项发现（按严重度）

### Z-1（P1，材料性，须新候选修复；本轮不阻断）SHACL `sh:in` 词法规范化不对称造成双向误判

- 位置：`packages/engine/src/ontolearn_engine/semantic.py:98-111`（`parse_turtle` 使用标准 rdflib Turtle 解析，默认 sink 将类型字面量词法规范化，如 `"01"^^xsd:integer → "1"`）；对照 `semantic_scopes.py:85-88` `_LexicalSink`（normalize=False）与 `semantic_execution.py:204-229` `_term`（事实路径显式保词法，要求 n3 往返相等）。
- 触发与复现（本人实测，冻结 head）：
  - **误判为通过（假阴性，全链路）**：事实对象 `"1"^^xsd:integer`（Store 提交，storage.py:253 强制 canonical）+ 约束 `sh:in ("01"^^xsd:integer)`（形状按原文含 01）→ 真实 `validation.execute` succeeded、`report.conforms=true`、0 违规（`store-lexical-counterexample.py` 本人隔离复现，输出与开发方 raw `b2cb4a06…` 语义一致）。按 SHACL `sh:in` 的 RDF **term equality**（词法+数据类型，非值相等），`"1"` 不是成员 `"01"`，应为违规。规范依据：SHACL Rec §InConstraintComponent（term equality），本人另经检索确认（见报告末来源）。
  - **误判为违规（假阳性，模块级，且产品可达）**：事实/派生 `"01"^^xsd:integer` + 形状原文 `sh:in ("01"^^xsd:integer)` → `check_shapes` conforms=false；同一形状文本仅用既有 `_LexicalSink` 解析则 conforms=true（`shacl-lexical-counterexample.py` 本人复现，与 raw `42704db6…` 一致）。可达路径：规则 `then` 对象经 `_term` 接受非 canonical 词法（definitions 路径不受 storage 手工事实 canonical 约束），R-risk 类规则输出 `"01"` 进入 selected-derived 验证范围后即触发。
- 根因：形状解析路径（默认规范化）与事实/规则词法路径（保词法）不对称——同一作者文本 "01" 在两侧成为不同 RDF term。pySHACL 本身的 `sh:in` 比较表现为 term 语义（假阳性复现中成员为规范化后的 "1" 时对事实 "01" 报违规），缺陷在候选的输入适配层。
- 影响：仅非 canonical 数值（及同类可规范化）词法 + `sh:in` 白名单模板的合法输入；固定 G.2/V-01/template_suite/25×3 golden 样例均不含此形态，全部原验收样例结论不受影响；确定性不受影响（同输入稳定复现）；不涉及安全/外联/存储不变量。
- 建议：新候选统一形状解析词法（如 `parse_turtle(shapes=True)` 走 `_LexicalSink` 或对形状图禁用规范化），补 "01 in (01)"、"1 in (01)" 双向真实回归；修复须经新候选 + 双方重审，并登记到 Q6-01/Q6-10 行（Q6-01 现有"原始词法无损往返未取得证据"应升级为"已证实 sh:in 双向误判"）。
- 阻断性依据：原 B1 验收为代表性样例 + 同样例打包 + 外联拒绝 + 测量口径，全部成立且本人复验通过；该缺陷位于所声明能力包络内但不在任何固定验收用例中，且由开发方主动披露并进入处置循环 → 记 P1 不阻断本候选门，但**在 Q6 采用该模板子集与任何产品化推进前必须关闭**。

### Z-2（P1，材料性，须新候选修复；本轮不阻断）SPARQL 裸数字 token 被规范化，偏离 §4.1.2 词法保留语义

- 位置：`packages/engine/src/ontolearn_engine/semantic.py:127-202`（`query` 经 rdflib `prepareQuery`，裸数字 token 被 rdflib 解析器 canonical 化；候选未做补偿，而其对显式类型字面量刻意保词法）。
- 触发与复现（本人实测，`query-numeric-counterexample.py` 复现与 raw `b97fc1f5…` 一致）：
  - 存储 `"01"^^xsd:integer`，查询 `ASK { … 01 }`（裸 token）→ **false**；按 SPARQL 1.1 §4.1.2（#QSynLiterals，本人取规范原文确认："typed literal with the lexical value of the token"，示例 1.300 → "1.300"^^xsd:decimal），裸 01 即 `"01"^^xsd:integer`，应与同词法事实 term 相等 → 应为 true。
  - 反向（全链路）：事实 canonical `"1"`，`ASK { … 01 }` → 真实 `query.execute` succeeded、value=**true**（`store-lexical-counterexample.py` 复现）；按词法保留语义裸 01 ≠ "1"，应为 false。
  - `01e+00` 同样失配；裸 `-01.00`（SPARQL 文法合法的负 decimal）→ `INVALID_QUERY`（rdflib 解析失败，以保守拒绝暴露——拒绝方向安全，但属对合法查询的错误拒绝）。
  - 显式 `"01"^^xsd:integer` 查询文本本身保词法且正确匹配（现有 `_LexicalSink` 机制）。
- 影响：裸数字 token 与非 canonical 词法事实的组合查询返回错误布尔/失配；显式类型字面量路径正确；固定样例（Q-01/Q-02/O-01 等）不含裸非 canonical 数字，不受影响。
- 建议：新候选在 `prepareQuery` 前对裸数字 token 做词法保留改写或一律拒绝非 canonical 裸数字（保守方向），补齐 §4.1.2 语义回归；与 Z-1 同批进入 Q6-01/Q6-06/Q6-07 处置。
- 阻断性依据：同 Z-1——样例级原验收不受影响、开发方已披露、可修复、确定性问题以外无扩散；记 P1 不阻断本候选门，产品化前必须关闭。

### Z-3（P2，流程事实更正，已核实无产品影响）冻结文档历史失败措辞不准

- `source-lineage-note.json`（SHA `cc0a94a0…` 实查一致）声明：`integrated-c1-verification.md` 中"第一轮集成测试 fixture 误用非UUID事实身份"不准确。
- 本人独立核实：原 raw `logs/semantic-runtime-first.txt.raw`（SHA `56474ccf…` 一致）第 21/35 行实为 `fact = {'id': 'unit-type', …}` → `ValueError: Fact identity must be content derived`；owning code `storage.py:255-257` 为 `fact["id"] != digest([subject,predicate,object])` 的**内容派生**校验，非 UUID 要求。冻结文档与原 raw 均保留，1126 文件零漂移。
- 结论：更正属实，属措辞级流程事实修正，不改变受审实现/测试/验收，不影响判定。

### Z-4（P3，观察）依赖 rdflib 私有 API

`semantic.py:182` 从 `rdflib.plugins.sparql.evalutils` 导入私有 `_val` 用于 ORDER BY 比较。当前由 uv.lock 锁定 7.6.0 并经包内验证，风险受控；升级依赖时需回归。非阻断。

### Z-5（P3，观察）`finish_semantic_job` 发布时校验为子集

`job_store.py finish_semantic_job` 发布时校验 payload kind/inputSnapshotId/体积/绑定相等；definitionId/scope/selectedResultIds 等完整身份交叉校验在读路径 `semantic_result()` 完成（篡改会在任何读取/选择时以 INTERNAL_ERROR 拒绝，本人经 runtime 测试与代码路径确认）。worker 为第一方代码；建议后续在发布事务内一并校验以尽早失败。非阻断。

### Z-6（P3，已披露边界）`semantic_resources` 无回收

内容寻址资源只增不减（缓存回收仅清空 `semantic_payloads.payload`/`results.payload`，触发器防复活本人已核）。开发文档已如实登记"历史/resource 增长未宣称关闭"。非阻断。

### Z-7（P3，观察）主进程任务记忆上限

`task-service.ts` `acceptedSemanticJobs`（16 项目 LRU）与 `remembered`（16）意味着重启/切回后窗口视图可能不再列出较早任务；任务与结果仍持久并经 `listJobs`/`job:get` 可查。属 UI 行为边界，非数据正确性问题。非阻断。

### Z-8（P3，已披露边界）新 CI 步骤尚未执行

`.github/workflows/ci.yml` 新增 I05 源码/打包 e2e 与 `verify-i05-runtime`（三平台），但候选未 push，**从未运行**；`pendingGates` 已如实列"真实三平台 CI"。引用时不得称 CI 已覆盖。非阻断（属未到期门禁，非隐藏缺口）。

### 核验无问题的重点面（对抗性检查后确认）

- **外联拒绝**：代数树递归拒绝 ServiceGraphPattern/DatasetClause（含 FILTER EXISTS、多层子查询内嵌，本人探针证实）；owl:imports 三角色拒绝；context-local audit hook 阻断 socket/urllib.Request/子进程事件；JSON-LD 库级入口被 urllib.Request 事件拦下（verify-i05 实测 28 用例零命中、正校准 1 次）；hook 为库执行防线而非 OS 沙箱，文档已如实声明。
- **查询能力边界**：LIMIT/OFFSET/非 COUNT 聚合/随机时间 UUID/BNODE/扩展函数/表达式排序/CONSTRUCT/DESCRIBE/更新全部拒绝（本人 22 探针）；服务端不可变游标分页真实存在（runtime 测试逐页拼回全量比对 + e2e 200/页）。
- **RDFS+一阶段规则**：闭包仅子类传递/类型/domain-range，label/comment 不参与；规则读冻结闭包、输出不反馈、保存顺序无关（R-05/06 断言相等）；链式提示 RULE_CHAIN_UNSUPPORTED；公理谓词输出被 `_rule`/`_terms` 双重阻断；WORK/RULE_MATCH/EVIDENCE 三重预算。
- **两范围与选中投影**：断言/断言+选定推导分图、公理独立视图、混图拒绝；`_selected_output` 对既有载荷做完整结构+依据+绑定一致性校验，投影不重算（reason 调用在 project 路径被 monkeypatch 测试证明不存在）；输入指纹/规则计划变化即 REASONING_SOURCE_MISMATCH。
- **Store/Job 不变量**：`semantic_result` 十余项生产者/输入/版本/三键/字节/行哈希交叉鉴权；`semantic_payloads` 不可变触发器 + 逐出置空且不可复活（本人读触发器逻辑并经 1511 项中的 runtime 用例复验）；`_publish_job` 中 `inputSelection=historical` 永不发布 current；operationId 幂等重试绑定原接受输入、语义变更 IDENTITY_CONFLICT；取消/超时/worker 崩溃不产生成功 current；事务回滚钩子测试证明 results/job_results/semantic_payloads/job_current 同生共死；迟到结果保原输入为 stale。
- **私有分块协议**：输入/输出 8 MiB、单块 ≤32000 字符、1024 块、逐块 SHA256、公开协商帧预算与私有通道分离（maxFrameBytes=1024 反例测试）。
- **窄桥与主帧授权**：preload 仅 3 个业务命名方法，e2e 断言无 invoke/createJob/semanticStart；主进程 zod `.strict()` + 契约双端校验（TS/Python 对称 added）；语义参数三重 refine（current↔snapshot、scope↔derived、reasoning 限 asserted）在 bridge/contracts/coordinator/worker 四层一致。
- **窗口重建/会话代**：startSemantic 恰好发送一次创建，失败/刷新不自动重放；generation/session 双重检查防串线；订阅失败不撤销已接受任务。Linux 原生证据（只读核验）覆盖真实 crash/unresponsive/外部焦点/GTK 对话框/三窗口同结果。
- **证据链**：117+14 raw 清单、198 输入绑定、982/198 两级源绑定、引擎 SHA、测量字节数（37,632,518 / 561,702,426）全部与工作树/文档互洽；`productionSourceHead 6b57078` 与 `finalHarnessHead 851be57` 的唯一晚变更（e2e 入口）与 043c 相对 6b 的实际 diff（仅 `tests/e2e/i05-semantics.spec.ts` + 文档/证据）一致，生产源码未变主张成立。

## 5. 已知差异与未验边界的独立判断

- **Q6 十二行**：逐行读取；差异登记与"待负责人采用/修订/淘汰"状态如实，Q6-08（FR-505 比较运算/单规则多结论）明确"未覆盖、待处置"，未被冒称完成；2026-10-21 集成事实更新未把任何行默认采纳。判定：**登记诚实、无静默豁免**。
- **未实现业务（映射/行为/E.5 沙盘/规则编辑器 UI/交换包各列/模型外发）**：均在文档与验收边界内明示"非本轮范围"，未虚报为已做。判定：符合"B1 不当全 M1"的边界要求。
- **本 Mac 未执行项**：Electron/e2e/native/HMR 全部未运行（遵守无桌面打扰）；相应结论一律引用隔离 Linux 原始证据（只读核验其完整性与一致性），未冒称本人复跑。
- **未到期门禁**：push/PR、真实三平台 CI、正常合并、远端/保护源核验、签名/干净设备/首发平台、容量结论（Q5 未定）、Windows/其他平台 native 许可（未匹配运行时 pending）——均如实保留，本轮通过不覆盖它们。
- **测量口径**：S1 18/180 两档原口径 + fresh 12 条为开发证据（本人核验文件与摘要互洽，未重跑测量）；verify-i05.py 的 12+12 是本人实测通过的结构性复验（同脚本同样例，非新容量结论）。无任何业务容量通过线被宣称，符合 Q5 未决约束。

## 6. 派发中途新增三项材料的独立核实（同一 C1，合并一次核实）

1. **source-lineage-note.json**：SHA 一致；原 raw、错误文本、`storage.py:255-257` 内容派生校验逐项核实（§4 Z-3）。更正采纳，无产品影响。
2. **shacl-lexical-counterexample（.py SHA 37ff6ab2… / raw 42704db6…）**：脚本与 raw SHA 一致；本人隔离复现输出与 raw 语义逐字段一致（§4 Z-1 假阳性方向）；规范依据（SHACL term equality）经检索确认。
3. **store-lexical-counterexample（.py 5891b829… / raw b2cb4a06…）与 query-numeric-counterexample（.py 6aee4db0… / raw b97fc1f5…）**：SHA 一致；store 脚本按指示在本人自建输出目录全链路复现（真实 Store→coordinator→worker→不可变结果，conforms=true 与 ASK=true 均复现）；query 脚本复现三 token 行为一致；SPARQL §4.1.2 词法保留语义经规范原文取回确认（"1.300"→"1.300"^^xsd:decimal）。
   以上均为未跟踪流程材料，不计入 1126 固定源码输入；本人全仓静态核验均针对固定提交（本人 pytest/vitest/typecheck/lint 在 043c20c 的 `git archive` 导出或锁定源码上执行），已按指示不把流程脚本视为 C1 实现变更。**三项反例合并构成本报告 Z-1/Z-2 两个 P1 发现，判定与处置建议见 §4/§7。**

## 7. 最终判定：**Pass（附条件与材料性发现）**

**判定对象**：冻结候选 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → head `043c20cc7934191339a8814c79666dbd2e94a62a` 的完整 I05/B1（含真实 I04 接线）。

**理由**：

1. 原验收（M0 计划 B1 全文 + PRD C/G + S1 口径）逐项成立且经本人独立复验：真实 RDFLib/pySHACL 固定依赖；最小真实 Turtle/只读查询/RDFS+受控规则/SHACL 代表样例源码与包内**同样例完整相等**（本人跑 verify-i05.py：parity true，字节数与开发证据逐字节一致）；SERVICE/远程 FROM/解析器验证器隐式外联**实际拒绝**（本人 22 探针 + 28 用例零命中）；PyInstaller 导入/插件/资源/动态库/完整许可与 CPython 两平台来源核验（verify-i05-runtime 实测 matched）；原始测量与 S1 两档口径保留；未以合成样例或 arm64 开发包宣称容量或首发平台合格。
2. 必要真实 I04 接线成立：semantic.start 经真实协调器/隔离 worker/私有分块；Store 接受事务内冻结不可变输入并核验 producer/三键/内容哈希；选中既存推导只投影不重算；同 operation 幂等、历史选择不发布 current、取消/迟到/回滚/逐出/篡改边界全部有真实测试且本人 1511 项全量通过；窄 bridge/主帧授权/会话代与完整结果分页展示经代码审查 + 672 TS 独立通过 + Linux 原生证据只读核验。
3. 两个 P1（Z-1/Z-2 数值词法簇）为合法输入下所声明能力包络内的真实误判（双向），本人已独立复现并对照规范确认；但它们**不在任何固定验收样例中**、确定可修、由开发方主动披露进入处置循环、不影响确定性/安全/存储不变量/打包证据，且 Q6-01 已预留词法往返未证明的处置通道——按本轮原验收文本不构成阻断。**该 Pass 不签收词法边界行为**：Z-1/Z-2 必须在新候选修复、补真实双向回归，并更新 Q6-01/Q6-06/Q6-07/Q6-10 登记后经双方对新版本重新审查；在此之前不得将 `sh:in` 模板或裸数字 token 语义作为已定产品能力注册或宣传。
4. 无未披露缺口：所有未完成项（Q6 十二行、Q2/Q3/Q5/Q7/Q8/Q9、CI/合并/签名/干净设备/容量）均在冻结文档与 pendingGates 中如实开放；本轮通过明确不覆盖这些后续门禁。

**遗留要求（非阻断但须处置）**：Z-1/Z-2 新候选修复与 Q6 登记；Z-4/Z-5/Z-7 建议性加固；Z-6 增长策略；Z-8 待 push 后的真实 CI。历史失败与修正（含 117+14 raw）保留完好，未发现任何为通过而删改断言/限制/证据的迹象。

**未验事项（如实声明）**：本机 Electron/native/HMR 未运行（禁令遵守，相应结论仅引用隔离 Linux 原始证据）；三平台 CI 未发生；性能测量原始值未由本人重跑（仅结构性复验与文件互洽核验）；Windows native 许可匹配 pending。

## 8. 附：规范依据来源

- SHACL 1.1 `sh:in` term equality：W3C SHACL Recommendation §InConstraintComponent（term equality 而非值相等；"01"^^xsd:integer 与 "1"^^xsd:integer 为不同 term）。
- SPARQL 1.1 §4.1.2 Syntax for Literals（#QSynLiterals）：裸数字 token 按其原词法映射 typed literal（例 1.300 → "1.300"^^xsd:decimal）。
- 详见：[SHACL InConstraintComponent](https://www.w3.org/TR/shacl/#InConstraintComponent)、[SPARQL 1.1 §4.1.2](https://www.w3.org/TR/sparql11-query/#QSynLiterals)、[SHACL 1.2 Node Expressions（term equality 引用）](https://www.w3.org/TR/shacl12-node-expr)。

---

*报告完成时间：2026-10-21（Asia/Shanghai）。审查期间 365/1126/198 零漂移两度复核；本报告为本审查者对冻结候选的独立结论，未参考另一方本轮任何材料。*
