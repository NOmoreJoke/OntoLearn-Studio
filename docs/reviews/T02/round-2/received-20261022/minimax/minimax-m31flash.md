# T02-S1 round-2 完整同版独立审查报告（C5 新候选）

- **审查方**：MiniMax M3.1-Flash（指定模型方唯一正式报告）
- **报告路径**：`docs/reviews/T02/round-2/minimax-m31flash.md`（本轮本方唯一持久写入）
- **日期**：2026-10-22（Asia/Shanghai）
- **结论（先给）**：**通过（限 T02-S1 有界范围）。** 详见第 10 节。

本报告独立复核，不采信"已关闭"字样，不引用另一审查方本轮（round-2）任何报告/推理/状态意见。上一轮（round-1）双方原报告均按要求作为**历史输入**读取。

---

## 1. 实际身份、设置读回与环境

| 项 | 实际值 | 读回来源（原始） |
| --- | --- | --- |
| 平台 | macOS 27.0.0（Darwin Kernel 27.0.0, arm64） | `uname -a` / 环境上下文 |
| 运行时 | MiniMax Code 本地桌面运行时，agent 路由 `mavis` | 运行时上下文 + `mavis session get` |
| 真实 session/task ID | `mvs_1cdba3c3802647838bc5f5091a866e22` | `mavis session get` 实测返回 `sessionId` |
| 会话创建时间 | 2026-10-22T18:50:43+08:00 | `mavis session get` → `createdAt=1792666243288` |
| 指定 provider/model | `minimax/MiniMax-M3.1-Flash` | `mavis session get` → `effective_model` / `model.model_id`（会话生效值，非文件名或报告标题推断） |
| 思考等级 | `xhigh` | `mavis session get` → `model.thinking.effort = "xhigh"`、`effective_model_variant = "thinking"`（**会话生效读回**，非指定值自述） |
| 权限模式 | **无法给出配置级读回** | `mavis session get` 与 `mavis agent get` 返回体中**均无 permission 字段**；用户级配置不能证明既有会话即时切换。**行为读回**：本会话全部工具调用（bash / read / write / edit，含依赖核验、pytest、完整 `npm run check`、headless 浏览器、自建探针）**未触发任何逐命令批准**，与"始终授权/Full access"一致，但不能据此断言配置值已被读回 |
| 工作目录 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-c5-minimax-review-e5ad54e` | `mavis session get` → `workspaceDir` 实测一致 |
| 正文接收 | 2026-10-22 18:50（会话同一 turn 收到完整 R2 正文＋启动补充） | 会话时间戳 |

- **模型/会话更换**：全程未更换模型、未复用其他会话、未借用另一审查方会话或意见。
- **本轮无 Pass 可继承**：manifest `taskStatus` 实测为 `prepared only; no round2 tasks/IDs/results yet`；旧 493 双 Pass、旧 35aa 内审 Pass 均不传递。

---

## 2. 固定身份与冻结输入核验（本方实际执行）

| 项 | 值 |
| --- | --- |
| 批准 base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |
| 当前 product head | `e5ad54e5762157cafe532c2a0c07c22e8dd737cb`（C5） |
| 证据过程 ref | `516ba27cb824fd89f5a21609776af3844c5430aa` |
| **本方 review HEAD** | `7c52e33e92d76bb0a83938a0e50abc40b8fb234e`（detached） |
| 原 owner 树/分支 | `.worktrees/T02-s1-review-fixes` / `feature/t02-s1-review-fixes`（**本方未进入、只读路径映射**） |
| 本方 review 树 | `.worktrees/T02-c5-minimax-review-e5ad54e`（detached HEAD 7c52） |

### 2.1 输入哈希逐项核验（脚本实跑）

| 核验对象 | 数量 | 结果 |
| --- | --- | --- |
| `input-manifest.json` → `fullBranchDeltaFiles`（按各自 `ref` 取 git blob 重算 bytes+SHA256） | 120 | **0 不符** |
| `input-manifest.json` → `unchangedReferences` | 10 | **0 不符** |
| `currentPolicyPayloads`（工作区实文件） | 4 | **0 不符** |
| 25 项产品/测试/harness 路径：工作区字节 **vs** product commit `e5ad54e` | 25 | **0 不符**（且 25/25 相对 base `5f910b5` 均已变更） |
| 终态复核（全部探针与运行结束后重跑上表全部项） | 134 + 25 | **0 不符**，HEAD 未变 | 

证据：`test-results/t02-c5-r2-review/metadata/input-verification.json`、`product-path-verification.json`；脚本 `test-results/t02-c5-r2-review/verify_inputs.py`、`verify_product_paths.py`。

### 2.2 台账历史差异（如实核对，非源码漂移）

`docs/reviews/T02/review-backlog-20261022.md` 在 manifest 中固定到 ref `516ba27c`（SHA `3fa52384…6778`、9757B）；review HEAD `7c52` 的版本为 11467B（SHA `19c0e829…1aca`）。二者差异经 `git diff --numstat 516ba27c 7c52` 实测为 **11 行新增、0 行删除**，即纯追加的 C4/C5 条目，**无源码漂移**，与启动补充所述一致。

### 2.3 25 项产品路径相对 35aa 的实际变更面

逐 blob 比对 `35aa93fc` vs `e5ad54e`：**仅 `packages/engine/src/ontolearn_engine/ontology/model.py` 与新增 `packages/engine/tests/test_ontology_input_boundaries.py` 发生变化**；`OntologyPage.tsx`、`ontology.css`、`view-model.ts`、5 个 ui-probe 文件、`service.py`、`source_projection.py`、`__init__.py`、其余 3 个 Python 测试、全部 fixture 与 TS 单测**逐字节相同**（脚本实测 10/10 SAME）。故"UI/服务/来源绑定未变、仅 model 与边界测试变更"的声明成立。

---

## 3. 覆盖清单（25/25 逐项全文阅读 + 逐项哈希核对）

| 路径 | 已读 | 已核 hash | 审查要点与结论 |
| --- | --- | --- | --- |
| `apps/desktop/src/renderer/src/ontology/OntologyPage.tsx` | ✅ | ✅ | 654 行全文。`EditIntent` 已无 `copy` 死变体；`useMemo` 仅 `tab==='tree'` 计算树；删除影响与预览均标注"基准快照（项目版本 N）中的引用；包括本次修改计划将解除的引用"；`update` 为 `keyof ObjectRow` 泛型且 `classType` 仅放行 `rdfs/owl`；事实区给出规范 n3 单术语示例；请求序号防迟到；`key={props.view.project}` 跨项目重挂载；纯 props 回调，无 Node/IPC/shell |
| `apps/desktop/src/renderer/src/ontology/ontology.css` | ✅ | ✅ | 纯静态样式；850px 断点；无 `unsafe-inline/unsafe-eval`、无外联无脚本 |
| `apps/desktop/src/renderer/src/ontology/view-model.ts` | ✅ | ✅ | `classTree` 一次建 parent→children 索引，保留排序/闭环/多父/重复父/缺失父语义；`localGraph` 一跳 + limit 1..100 + 截断；`isCurrentPreview` 项目+版本判定 |
| `docs/iterations/T02/ui-probe/build.mjs` | ✅ | ✅ | vite 构建本目录，`configFile:false`，`outDir: out`（本树 `.gitignore` 覆盖） |
| `docs/iterations/T02/ui-probe/check.mjs` | ✅ | ✅ | 21 项 headless 探针；`page.route` 仅向 `t02-ui.invalid` 以 `route.fulfill` 回放本地静态产物，`path.startsWith(root)` 防穿越；**无 HTTP server/端口/外联**；失败分支写 `ui-probe-failure.json` |
| `docs/iterations/T02/ui-probe/fixture.json` | ✅ | ✅ | 25 对象 / 46 三元组 / 四种 kind 齐备 / IRI 唯一 / 四类元数据字段齐全；纯领域样本 |
| `docs/iterations/T02/ui-probe/harness.tsx` | ✅ | ✅ | **纯合成 callback**，三处显式声明"不代表引擎、Store 或正式产品接线"；`previewEdit` 回执取**请求时** base，晚回复必然失配 |
| `docs/iterations/T02/ui-probe/index.html` | ✅ | ✅ | 静态壳 |
| `packages/engine/src/ontolearn_engine/ontology/__init__.py` | ✅ | ✅ | 导出面封闭：7 个符号；**无 `snapshot_digest`/`references`**；无持久化/协议注册/模型调用 |
| `…/ontology/model.py` | ✅ | ✅ | 不可变 `Entity/Fact/Snapshot/Triple/ExternalReference`；`_is_utf8` 前门；kind/class_type/identifier 约束；labels/definitions 全语言元组；parents/domain/range/types 适用性与目标种类；dataProperty range 仅 7 个 XSD 类型；facts 通道禁 `rdf:type/rdfs:label/rdfs:comment`；外部引用不得悬空 |
| `…/ontology/service.py` | ✅ | ✅ | 纯编辑计划；命令类型前门先于查表/哈希/排序；`references` 含精确 statement；删除影响基于**基准快照**；`rdf_triples` 编译类声明/label/comment/subClassOf/domain/range/type；`snapshot_digest` 结构序不敏感、文本序敏感；`change_preview` 幂等集合语义；`require_current` 仅 (project,revision,digest) 守卫且自我声明非确认令牌 |
| `…/ontology/source_projection.py` | ✅ | ✅ | `_validated_source` 复用批准 `digest` + 键集 + `family()` + `Store._snapshot_state`（classmethod，无实例无 SQL）；`bind_rdf_projection` 要求完整 RDF 集合相等；保留原 fact ID/owner/source_row/managed_value、墓碑、多重支持与原下标；`removed_sources` 先 `require_current` 再校验 ⊆ known |
| `packages/engine/tests/test_ontology_editor.py` | ✅ | ✅ | 26 例，断言完整预期集合/顺序而非计数 |
| `packages/engine/tests/test_ontology_fixed_inputs.py` | ✅ | ✅ | 先逐字节验 manifest/G-base/PRD 哈希再投影；G-base 完整集合相等；显式自我声明"非产品 parser" |
| `packages/engine/tests/test_ontology_source_projection.py` | ✅ | ✅ | 13 例，真实临时 SQLite；读取零写入（`total_changes` 不变 + state/vector/revision 不变） |
| `packages/engine/tests/test_ontology_input_boundaries.py` | ✅ | ✅ | **C5 新增**：共 31 项 = 30 参数化 surrogate 拒绝反例（基准 7 字段 × 2、Put 5 字段 × 2、Triple 3 术语 × 2）+ 1 合法 Unicode 原样保留正例；结构与声明数一致 |
| `tests/fixtures/ontology/invalid-turtle.ttl` | ✅ | ✅ | 语法错误样本 |
| `tests/fixtures/ontology/manifest.json` | ✅ | ✅ | 自述 `purpose = "Future approved I05 import/roundtrip integration inputs, not executed product acceptance"`；**5/5 声明 SHA256 与实际逐字节相符（本方独立重算）** |
| `tests/fixtures/ontology/manual-supported.ttl` | ✅ | ✅ | 16 三元组基础 RDF |
| `tests/fixtures/ontology/supported-shacl-template.ttl` | ✅ | ✅ | SHACL 模板样本（4 空白节点） |
| `tests/fixtures/ontology/t09-fixed-inputs/G-base.json` | ✅ | ✅ | **8219B，SHA 与 t09 manifest 声明相符（本方独立重算）** |
| `tests/fixtures/ontology/t09-fixed-inputs/manifest.json` | ✅ | ✅ | 被测试以硬编码 `MANIFEST_SHA` 锚定，非自证 |
| `tests/fixtures/ontology/unsupported-owl.ttl` | ✅ | ✅ | `owl:equivalentClass` + `Restriction` |
| `tests/fixtures/ontology/unsupported-shacl-path.ttl` | ✅ | ✅ | `sh:inversePath` |
| `tests/unit/t02-ontology-views.test.ts` | ✅ | ✅ | **4 例**（较 R1 记录的 3 例新增"排序根/缺失父/共享后代/自环/重复父/空集"完整序列用例）；断言精确序列 |

### 3.1 语料未被执行（独立确认）

`grep` 全仓测试树：`tests/fixtures/ontology/*.ttl` 与 `manifest.json` **无任何测试引用**（唯一命中为 `t09-fixed-inputs` 目录常量与本方自建核验脚本）。该语料**不得计入 S1 导入能力证据**，FR-203 仍是父门。

### 3.2 需求依据（实际读取）

- PRD V0.6 原文 SHA256 `7586b2c4…f0fbb`，与 t09 manifest 声明**一致**（本方独立重算）。
- FR-200–204 原文、附录 C/D/E/F/G、12.1/12.4、FR-804、10.2 已读。附录 C 明确：`rdfs:domain/range` **不得当作必填约束**（S1 遵守）、多语言按字面量保留（S1 遵守）、OWL 类表达式与逆向 SHACL 路径 P0 不承诺（S1 不提供）。
- `docs/iterations/T02/acceptance.md`、`source-projection.md`、`stage-registration-request.md`、`interface-handoff.md`、`delivery.md`、`docs/reviews/T02/status.md`（**唯一状态源，实测已更新至 C5**）已读。

---

## 4. 本方实际执行的验证（新跑）

### 4.1 环境（独立于其它树）

本树 `node_modules` 与 `.venv` 已按原锁准备（**setup 不是产品验证**）：`uv sync --frozen --dry-run` 实测 `Would make no changes`；`.venv` 为 Python 3.12.12 / pytest 9.1.1 / rdflib 7.6.0；Node v24.15.0。**未借用任何其它树的 node_modules/.venv，未改锁。**

### 4.2 命令、结果与真实 exit

| # | 命令（cwd = 本 review 树根） | exit | 结果 |
| --- | --- | --- | --- |
| 1 | `uv run --frozen pytest packages/engine/tests/test_ontology_{editor,fixed_inputs,source_projection,input_boundaries}.py -v` | **0** | **112 passed in 1.10s** —— 与所有者记录的 ontology 112 完全一致；31 项 C5 新用例逐条 PASSED |
| 2 | `npm run check`（lint + format:check + typecheck + vitest + build + ruff + pytest） | **0** | **634 vitest passed (16 files) / 1164 pytest passed (57.71s)**，`All checks passed!` —— 与所有者记录 **634TS/1164Py** 完全一致；较 C4 的 1133Py 恰 +31（新增边界用例） |
| 3 | `T02_UI_OUTPUT_DIR=<本方目录> T02_HEADLESS_EXECUTABLE=<chrome-headless-shell 1234> node docs/iterations/T02/ui-probe/check.mjs` | **0** | **21/21 项 headless 全过**，`completedCheckCount:21`，evidence 列表与实现逐条对应；输出写入本方 `test-results/t02-c5-r2-review/ui/`（**历史 `ui-probe.json`/PNG 未覆盖，tracked `docs/reviews/T02/ui-probe.json` 终态 `git diff` 为空**） |
| 4 | `uv run --frozen python test-results/.../probe_unicode_independent.py` | 0 | 见 4.3（**探针脚本自身两处缺陷已保留首失败并修正重跑**） |
| 5 | `uv run --frozen python test-results/.../probe_unicode_independent_part2.py`（修正后重跑） | 0 | 见 4.3 |
| 6 | `uv run --frozen python test-results/.../probe_unicode_independent_part3.py` | 0 | 见 4.3 |
| 7 | `node test-results/.../probe_classtree_perf.mjs`（本树 `tsc` 编译 view-model 后测量） | 0 | 见 4.4 |
| 8 | 输入哈希核验 ×2 轮（起/终） | 0 | 见 2.1/2.2 |
| 9 | fixture/Turtle 语料哈希与引用扫描 | 0 | 5/5 + G-base 哈希相符；语料未被任何测试引用 |

### 4.3 我方独立 Unicode 探针（**不依赖所有者 30,720 组探针**）

1) **C4 残留复现（A/B 对照）**。我方把 `35aa` 的 `ontology/{__init__,model,service}.py` 用 `git cat-file` 抽出到**临时目录**（不触碰任何受审树），同一复现分别跑 C4 与 C5：

| 输入 | C4（35aa 实测） | C5（e5ad54e 实测） |
| --- | --- | --- |
| `project="p\ud800"` | **原生 `UnicodeEncodeError`** | `OntologyError(reason='invalid_text', location='project')` |
| `synonyms=("syn\ud800",)` | **原生 `UnicodeEncodeError`** | `OntologyError('invalid_text','synonyms')` |
| `examples=("ex\ud800",)` | **原生 `UnicodeEncodeError`** | `OntologyError('invalid_text','examples')` |

→ C4 的阻断性残留在 C5 **确实被关闭**，不是空改；且 `str(error)` 只含 reason，不含输入值、解析文本或堆栈。

2) **穷举扫描（我方独立注入点集合，覆盖全部 2048 个代理码位）**：20 个注入点 × 2048 码位 = **16,406 组**，结果 **原生异常 0 / 值泄漏 0 / 静默接受 0**。各点固定 reason：

```
base.project invalid_text | base.entity.iri invalid_iri | base.entity.identifier invalid_identifier
base.entity.labels.text invalid_text | base.entity.labels.language invalid_language
base.entity.definitions.text invalid_text | base.entity.synonyms invalid_text | base.entity.examples invalid_text
base.entity.parents/domain/types class_reference_required | base.entity.range unsupported_datatype
base.entity.class_type invalid_class_type | base.entity.kind unsupported_kind
base.external_reference.source invalid_external_reference | base.external_reference.target dangling_external_reference
base.fact.subject/predicate/object invalid_rdf_term
```

3) **Put/命令路径**：`Put(create=True)` 携带 surrogate IRI → `invalid_iri`；`Put(create=False)` → `not_found`（目标不存在，先于实体字段校验）；`Copy.source` 坏 → `not_found`；`Copy.identifier` 坏 → `invalid_identifier`；`Copy.target` 坏 → `invalid_iri`；`add_facts`/`remove_facts` 携带 surrogate → `invalid_rdf_term`；`deletion_impact` 非字符串目标 → `invalid_iri/target`。**全部为固定 reason，无原生异常。**

4) **合法 Unicode 原样保留**：CJK + emoji + **显式分解重音（`e`+U+0301）** 逐码位保留，**未做 NFC 归一化**（探针实测探针串尾码位 `[0x65, 0x301]`，保留后不含 U+00E9）。

5) **digest 编码语义未被改动（可证）**：`snapshot_digest` 结果 == 手算 `sha256(json.dumps(ensure_ascii=False, sort_keys=True, separators=(",",":")))`；且**同一合法输入下 C5 与 C4 的 digest 完全相同**（`2f8a0964ae0c04317b1e878930b74ba1f7e50213b94c8200cdd9206dfa8c444f`）。→ C5 是**在哈希前加守卫**，不是"改 digest 编码来避错"，符合处置声明。

6) **来源绑定边界**：手工构造含 surrogate 载荷的 source dict → `bind_rdf_projection` 返回固定 `invalid_source_snapshot`，且 **Store `total_changes` 不变**。

7) **本方探针脚本自身的两处缺陷（如实保留，非产品缺陷）**：part1 的 digest 复算用了不完整载荷（恒不匹配）；part2 的重音比较写成双重转义字面量且探针源文件实为预组合 U+00E9；part2 另有一次括号语法错误。三次首失败原始日志分别保存在 `raw/probe-unicode-independent.log`、`raw/probe-unicode-independent-part2.log`（SyntaxError, exit 1）与 `raw/probe-unicode-independent-part2-retry.log`，修正后重跑通过。**未以任何方式修改产品/测试来让探针通过。**

### 4.4 类树计算独立测量（本方实测，非沿用）

`view-model.ts` 用本树 `tsc` 编译后测量（我方 ad-hoc 编译参数与仓库 `tsc` 配置不同，产生了一个**与 `@types/keyv` 相关的无关报错**，属我方编译方式限制；仓库自身 `npm run check` 的 typecheck 全过，无产品问题）：

| 结构 | n=1000 | n=2000 | n=4000 |
| --- | --- | --- | --- |
| 宽树（1 根 + n 子） | 0.6 ms | 0.6 ms | 5.0 ms |
| 深链（每点 1 父） | 13.7 ms | 50.3 ms | 210.0 ms |
| 环 | 13.0 ms | 42.0 ms | 172.8 ms |

R1 曾实测 n=1000→16.5 ms、n=2000→81.8 ms。→ **索引化后宽树已近线性；但深链仍超线性**（每步复制祖先集合，`O(n·depth)`）。顺序稳定性实测：输入逆序后输出**完全一致**（`order stable under input reversal: true`）；环结构 20 点全部渲染并给出 repeated 标记。

---

## 5. 沿用的既有证据（**我方未重跑，不计为我方新验证**）

- C5 四份原始流封存包 `c5-raw-evidence.tar.gz`：实测 **1799B、SHA `0bb43ca61c22fc89a583d13e44c988d369c8f2b4f2150c57ce35fff66b841e6f`**，与 `disposition-c5.md` 声明**逐位一致**；4 成员为 `check-first.log`（1164 passed, EXIT=0）、`pytest-first.log`（112 passed, EXIT=0）、`ruff-first.log`（All checks passed, EXIT=0）、**`unicode-c4-first-failure.log`（project/synonyms/examples 三路 raw UnicodeEncodeError, EXIT=1 —— C4 首失败原件确实保留）**。
- C4 封存包 `c4-raw-evidence.tar.gz`：实测 SHA `b637c73924b856b89852547cf0dc82ce0621ee76d730543bb66c413cfb0faddf`、**84 成员**，与 `disposition-c4.md` 声明一致。
- C1/C2/C3 内审原件、41 日志 + 2 截图 + 4 索引归档（548417B / `43d9e205…f2a6b86` / 48 成员）、`original-log-index.json` 32 条索引、`typed-changeset-integration-plan` 十件纯方案（仅方案层）——按 manifest 哈希核对存在且一致，**未逐条重跑**。

---

## 6. 明确未执行（**不得记为通过**）

Electron / e2e / native / HMR / 打包产物内运行 / Windows·macOS 安装与首发 / 真实模型外发 / 正式 IPC·bridge·App 路由 / 正式 Store 写入 / 人类确认 / `Store.commit` / undo / T01 可信当前域与来源投影 / I05 批准 Turtle·SHACL 支持检查与无损往返（corpus 未执行）/ T08 真实草稿 / FR-200–204 跨模块完整验收 / 附录 C/F/G 与 12.1·12.4 全量 / 两目标平台 / 真人验收 / CI / push / PR / merge / 远端核验 / 上线 —— **本轮全部未执行**。

---

## 7. 上一轮 11 项意见的独立处置结论

> 11 项来源：MiniMax R1 报告实际为 **P2-1 + P3-1..5 共 6 项**（其摘要误称 4 P3，原报告保留不改），ZCode R1 为 **5 项 P3**，合计 11 项。

### 7.1 M-P2-1　畸形元素类型抛原始异常，偏离固定错误码契约（**唯一曾判不通过项**）

**结论：关闭（含 C4 残留 Unicode 缺口一并关闭）。**

- 独立依据（代码）：`model.py:126-132` 先判 tuple 与元素 `isinstance` 再哈希/解引用；`model.py:119-124` revision 用 `type(...) is not int` 精确守卫；`service.py:153-161` 先判三参数为 tuple、再判 `Fact` 实例并 `fact.triple()`（在集合构造前）；`service.py:167-176` 判命令类型、`Put.entity` 类型、`create` 精确 `bool`、`Copy.source` 类型、目标为 `str`，**全部先于查表/哈希/排序**；`model.py:44-56` `Triple.__post_init__` 在 `iri()/term()` 前做类型与可编码性前门；`service.py:68-71` `deletion_impact` 非法目标 → `invalid_iri/target`；`source_projection.py:62-80` `removed_sources` 先判 `Preview` 与 removed 元组元素类型。
- 独立依据（运行）：本方 112 项专项独立通过；16,406 组扫描 **0 原生异常**；真实 Store 测试断言 `total_changes`、state/vector/revision 三重不变。
- 错误协议：仅 `OntologyError(reason, location)`，`str(error) == reason`，**无第二公共错误协议**；`source_projection` 的 `except` 为具名元组且 `from None`，**不吞异常**、不回落原始文本。
- 边界如实保留：只保证已发现缺口已关闭，**不保证任意 Python 对象或无限输入空间**——与处置声明一致。

### 7.2 C4 内部残留 P2　未配对 surrogate 逃逸 `UnicodeEncodeError`

**结论：关闭。** 见 4.3 的 A/B 对照（C4 实测原生异常 / C5 实测固定 reason），以及 C5 原始流中保留的 `unicode-c4-first-failure.log`（EXIT=1）。覆盖面经我方 20 注入点 × 2048 码位独立确认，**含所有者未列的** identifier / class_type / kind / parents / domain / range / types / labels.language / external_reference.target 等点。合法 Unicode（含分解重音）逐码位保留，**未替换、未归一化、未改 digest 编码**（C4/C5 digest 同一输入完全相同）。

### 7.3 M-P3-1　批量删除影响按基准快照计算，可能含同批已解除引用

**结论：关闭（语义以显式标注固定，R1 建议的方案 (b) 已实现）。**

- 独立依据（代码）：`service.py:200` 明确以 `snapshot`（基准）计算 `deletion_impact`；`OntologyPage.tsx:332` 与 `:545` **两处**均显示"基准快照（项目版本 {N}）中的引用；包括本次修改计划将解除的引用。"；`OntologyPage.tsx:163` 删除影响按 `(base, iri)` 双条件启用。
- 独立依据（运行）：`test_ontology_input_boundaries.py::test_batch_delete_retains_all_original_reference_impacts_after_same_batch_release` 断言**基准三引用全留、六个 RDF 删除项、完整 candidate**；本方 21 项 headless 中 `delete_impact_and_preview_explicit_baseline_reference_semantics` 断言基线文案与引用项可见。
- 我的独立判断：R1 原文即提出"改用同批次候选 **或** 显式命名为基准快照引用并在 UI 标注基准版本"两条路径，处置选择后者且两处落实并有精确断言；保守过报**不构成错误写入**（终态 `validate(candidate)` 会拒任何悬空引用——我复核无下漏）。FR-200"删除已被引用的内容前必须展示影响范围"因此得到满足。**不以"已关闭"字样为据，而以代码语义、UI 文案与断言为据。**

### 7.4 M-P3-2　`EditIntent.copy` 死变体，复制路径不保留来源关联

**结论：关闭。**

- 独立依据：`OntologyPage.tsx:22-25` `EditIntent` 现仅 `create|edit|delete|assert|retract`，**`copy` 变体已删除**（`grep` 无 `action:'copy'` 发出点）。
- 复制语义：`OntologyPage.tsx:310-321` "复制定义到新表单"把**完整定义+元数据**载入**可编辑**新表单（`iri`/`identifier` 清空），提交时发 **`action:'create'`** 并携带用户编辑后的完整对象——**未机械发仅 source/IRI 的 copy 而丢弃用户编辑**。本方 21 项 headless 中 `copy_all_metadata_families_edit_then_create_complete_definition` 对 class/objectProperty/dataProperty/individual **四类**逐类断言 create 意图对象等于「源完整元数据 + 修改后 examples」。
- 谱系主张：`OntologyPage.tsx:18-21` 显式注明"本表单不持久化复制谱系"；FR-200 未要求持久复制谱系，引擎 `Copy` 亦仅选源。**未把"缺少持久溯源"编成已实现能力或修复目标。**
- 残留如实记录：`service.Copy` 仍是**产品路径不可达**的私有原语（仅测试触达），但类型面已无虚假声明，故不构成 R1 所指的"声明与能力不一致"。

### 7.5 M-P3-3　表格分页/复制/事实表单等 UI 路径无候选内自动化验证

**结论：关闭（仍仅为合成 callback 呈现证据）。**

- 独立依据（运行）：本方**独立重跑** 21 项 headless 全过（exit 0）。原 11 项全部保留（第 1–11 项 evidence 名称与 R1 时代一致），新增 10 项覆盖：25 对象前后分页**完整有序集合**与页边界、搜索重置与空集显式文案、**四类** metadata 复制后编辑再 create、新建表单清空、assert/retract 精确事实与请求基准、版本/项目基准重绑与阻断、坏 n3 值固定失败文案、基准删除影响语义、局部图截断与完整可见边集合。
- 边界诚实性：harness 三处显式声明"不代表引擎、Store 或正式产品接线"；`check.mjs` 写入 `mode: "headless Chromium presentation probe with synthetic callback; no IPC/Store/product integration"`；**未把合成拒绝冒充引擎/IPC 证明**。我确认合成 callback 无任何 Store 触达路径。
- 原 R1 缺口（"headless 组件探针从未点击表格分页"）**已实际闭合**：探针现断言 caption「共 25 项 · 每页 20 项」、首页恰 20 行、第二页剩余 5 行、两页拼接等于完整有序集合。

### 7.6 M-P3-4　`classTree` O(n²) 且在组件渲染中无条件计算

**结论：部分关闭，残余降为 P3 观察（见 8.3）。**

- 已关闭部分（代码+运行）：`OntologyPage.tsx:104` `useMemo(() => (tab === 'tree' ? classTree(view.objects) : []), [tab, view.objects])` —— **仅在类树页签且输入身份变化时计算**，消除"每次渲染（含每次按键）无条件重算整棵树"；`view-model.ts:36-44` 一次建 parent→children 索引，消除旧 `classes.filter(...)` 的 O(n² log n) 过滤。
- 语义保持：排序根/缺失父/共享后代/自环/重复父/闭环标记由 TS 单测**精确序列**断言；本方实测输入逆序输出完全一致、环结构全部呈现并带 repeated 标记。
- **未承诺线性、未给容量线、未量化提升幅度**——处置声明与实现一致。我方测量（4.4）显示宽树已近线性，但深链仍超线性。

### 7.7 M-P3-5　错误 reason 断言不足

**结论：关闭（覆盖面已超 R1 记录）。**

- 独立依据（我方独立统计）：三个产品模块中 `OntologyError` 字面 reason 共 **42 个**；四个 ontology 测试文件中**未被断言者 = 0**（全引擎测试树亦为 0）。R1 记录为 38 个 reason / 16 个未断言。
- **不以 AST 数量自证**：每条都由**真实业务负例**驱动（R1 列出的 16 条：重复/矛盾事实命令、IRI 身份冲突、非法字段/语言/字面量、来源移除集越界等，在 `test_ontology_input_boundaries.py` 与 `test_ontology_source_projection.py` 中均有具体输入与固定 reason/location 断言）。
- 不声称穷尽无限输入空间（处置已如此声明，我方同意）。

### 7.8 Z-P3-1　语言标签仅小写子集

**结论：接受并延期，限制保留；**不**构成 S1 不通过。**

- 独立依据：`model.py:167-170` 语言正则 `[a-z]+(?:-[a-z0-9]+)*`；`en-GB` → `invalid_language`（本方探针亦确认 surrogate 语言 → `invalid_language`）；UI `pattern="[a-z]+(-[a-z0-9]+)*|"` 一致；`rdf_snapshot.term()` 将语言小写化，故 `en-GB` 的规范 n3 形式在本私有模型中不可表示——三者**内部自洽**。
- 我的独立判断：FR-200 要求的是"中文名称、英文标识、定义、同义词、示例"，**不含** BCP-47 子标签全集；完整语言规范化与无损往返属于 FR-203 导入与批准 I05/T01 adapter 的父门（`stage-registration-request.md` 第 3 项、`interface-handoff.md` 均已登记）。故该限制**不违反 S1 现行验收**。
- 我**不替 owner 降低级别**，亦**不**把它读成"已实现导入支持"：三处限制声明（模型/UI/处置）必须随候选保留。

### 7.9 Z-P3-2　`class_type=None` 默认编译为 `rdfs:Class` 且 Copy 无断言克隆

**结论：关闭。** `service.py:85-87` 显式分支：仅 `class` 且 `class_type=='owl'` 用 `owl:Class`，否则 `RDFS.Class`；`test_ontology_input_boundaries.py::test_unspecified_class_declaration_and_copy_remain_rdfs_without_assertion_cloning` 直接断言 `rdf_triples` 为 `rdf:type rdfs:Class`、Copy 后新增 `rdf:type rdfs:Class`、**`candidate.facts == ()`（不克隆实例断言）**、原 `class_type is None` 不变。本方运行通过。

### 7.10 Z-P3-3　重加已有事实为幂等空 Diff

**结论：关闭。** `service.py:204-213` 集合语义：候选事实 = `(基事实 − 移除) ∪ 新增`；重加已存在事实 → `added == removed == ()`、`changed_entities == ()`、`entity_changes == ()`、候选事实与全 RDF 不变、基准不变——由专用测试**完整断言**（精确空 Diff）。RDF 集合语义下"不报错"可辩护；未来"已存在/无变化"提示属**呈现选择**，不在 S1 范围，我同意延期。

### 7.11 Z-P3-4　`update('classType', …)` 接受任意 string

**结论：关闭。** `OntologyPage.tsx:106` `update` 已改为 `<K extends keyof ObjectRow>(key: K, value: ObjectRow[K])` 泛型；`:393` classType select **只放行 `'rdfs'|'owl'`**；服务侧 `invalid_class_type` 仍是权威兜底（`model.py:145-148`，有真实负例）。本方 634 TS typecheck 全过。

### 7.12 Z-P3-5　事实 object 输入无前置格式校验

**结论：部分接受，限制保留。** `OntologyPage.tsx:482-487` 给出规范 n3 单术语示例（`<urn:t02:A01>`、`"名称"@zh`、`"3"^^xsd:integer`）；坏值经合成服务拒绝后，固定文案 `未能生成预览。正式项目未获保存确认，请检查输入或重新读取项目。` 在 assert/retract 两条路径**均被 21 项探针精确断言**；**未在 renderer 造第二 parser**。但**完整前置 parser 与边界提示仍未实现**，正式引擎/adapter 边界不能由合成探针替代——该限制必须保留，**不得记为导入或完整校验能力**。

---

## 8. 本方新发现问题（按 P0–P3）

> 无 P0、无 P1、无 P2。

### 8.1 P3-1　未导出的模块级 `snapshot_digest` 对未校验快照仍抛原生异常

- **严重度**：P3（私有模块内部函数，未导出，今日不可达）
- **位置**：`packages/engine/src/ontolearn_engine/ontology/service.py:105-112`（`snapshot_digest`）
- **触发**：`snapshot_digest(Snapshot("p\ud800", 0, ()))` → 实测**原生 `UnicodeEncodeError`**（`json.dumps(ensure_ascii=False).encode()`）。
- **影响**：**当前无用户可见影响**。`__init__.py` 的 7 个导出符号**全部**先 `validate`（`change_preview`、`rdf_triples`、`deletion_impact`、`Preview.require_current`、`bind_rdf_projection` 均已验证）；`snapshot_digest` 与 `references` **不在 `__all__`**。风险仅在于未来 adapter 若 `from ...service import snapshot_digest` 直接使用，会绕过校验并把原始异常带过边界（违反"跨边界只传固定错误码"）。
- **证据**：`raw/probe-unicode-independent.log` 第 7 节（`snapshot_digest(unvalidated): native -> UnicodeEncodeError`；`snapshot_digest exported in ontology.__all__: False`）。
- **建议**：将其更名为 `_snapshot_digest` 或在函数内先 `validate(snapshot)`；在正式接线前明确该模块为私有、不得绕过 `validate` 直接取用。

### 8.2 P3-2　交付/登记文档的证据指针再次落后两个候选

- **严重度**：P3（纯流程文档层，不影响产品能力与证据本体）
- **位置**：`docs/iterations/T02/delivery.md:3`（仍写"当前实现为 C3 `4932122`…全仓633 TS/1091 Python，本线39条"）；`docs/iterations/T02/stage-registration-request.md:20-23`（仍写 26 条 C2 Python、3 条 TS、11 项 headless、633TS/1091Py）
- **触发**：当前候选为 C5（634TS/1164Py、本线 112、21 项 headless）。
- **影响**：无产品影响；**唯一状态源 `docs/reviews/T02/status.md` 实测已更新至 C5**（含"C4 失败保留与 C5 当前候选"段），当前候选的权威证据（`round-2/disposition-c5.md`、`c5-evidence-manifest.json`、`status.md`）齐备，信息未丢失。风险是读者据 `delivery.md` 标题误判当前实现与证据数字。**这是 R1 的 H06 在 C2→C3 修过一次后的同类复发。**
- **证据**：上述文件首行直读；`status.md` 末段已含 C5 事实。
- **建议**：在下一候选刷新时一并更新指针与数字。**注意**：这两个文件是 manifest 固定输入（ref `516ba27c`），**本轮直接修改会改变受审输入 → 须走新候选与新验证**，我方因此未改。

### 8.3 P3-3　类树在深链结构下仍超线性（祖先集合逐步复制）

- **严重度**：P3（性能观察，**无已批准容量阈值**，不给出任何通过线）
- **位置**：`apps/desktop/src/renderer/src/ontology/view-model.ts:45-56`（`walk` 中 `const next = new Set([...ancestors, row.iri])` 每步复制祖先集合）
- **触发**：类层级呈深链（每点单父）时，祖先集合规模随深度线性增长，总代价 `O(n·depth)`。
- **影响**：我方实测深链 n=1000→13.7 ms、n=2000→50.3 ms、n=4000→210.0 ms（2 倍输入约 4 倍耗时）；宽树同规模 0.6/0.6/5.0 ms（近线性）。**索引化确已消除旧的过滤型 O(n² log n)**，但深链残余仍在。PRD 10.2 数据量/响应时间指标【待确认】，**本报告不给出容量通过线**，仅陈述实测点。
- **证据**：`raw/probe-classtree-perf.log`。
- **建议**：未来接线前按真实数据规模评估是否需要共享祖先链（而非逐步复制）；**在此之前不得宣称整体线性或任何提升幅度**。

### 8.4 范围外观察（**不计为本候选缺陷，也不计入 S1 判定**）

- `packages/engine/src/ontolearn_engine/storage.py:315`（`Store.commit` → `digest(plan)` → `canonical(value).encode()`）在定义载荷含未配对 surrogate 时抛**原生 `UnicodeEncodeError`**（本方实测）。
- **该文件为 T01 所有，不在本轮 25 项受审范围**；`packages/engine/src/ontolearn_engine/ontology/` 全包**无任何 Store 写调用**（`grep` 实测，仅注释提及）；且该载荷因 commit 本身先失败而**无法进入 Store**；即便手工注入 source dict，`bind_rdf_projection` 亦已收敛为固定 `invalid_source_snapshot` 且**零写入**（本方实测）。
- **建议总控按责任路由转给 T01/owning line**，本方不越界修改，也**不**据此对本候选作任何降级。

---

## 9. 架构不变量与不变量外的诚实边界核对

| 不变量 | 本方核对结论 |
| --- | --- |
| 本地优先 | ✅ ontology 包与页面全文核对：无模型/遥测/云/HTTP 端口/自动产物启动 |
| 渲染端隔离 | ✅ 纯 props 回调，无 Node/IPC/shell/通用通道 |
| CSP | ✅ 未触碰 `csp.ts`；CSS 无 `unsafe-inline/unsafe-eval` |
| 确定性与 Agent 解耦 | ✅ 无确认入口；`require_current`/`require_source` 自我声明为守卫 |
| 存储 | ✅ ontology 包不实例化 Store、不执行 SQL；正式写入只可能经未来 owning `Store.commit` |
| 数据层次/失效规则 | ✅ 未触碰；`invalidation-v2.json` 未改 |
| 错误边界 | ✅ 仅固定 reason/location；本方 16,406 组扫描 0 原生异常、0 值泄漏 |
| 未把替身/方案冒充产品能力 | ✅ harness/check.mjs/ui-probe.json/acceptance/status 五处一致披露合成边界；Turtle 语料未被执行且未被计入 |

---

## 10. 结论

### 10.1 对完整 T02-S1（当前 C5 候选 `e5ad54e`）：**通过**

依据：

1. **输入完整**：120 delta + 10 参考 + 4 政策载荷 = **134 项逐项 bytes/SHA256 零不符**；25 项产品/测试/harness 路径与产品提交**逐字节一致**；起止两轮复核 HEAD 与工作树**零漂移**；台账差异经实测为 **11 行纯新增、0 删除**，无源码漂移。
2. **运行独立复现**：`npm run check` **exit 0，634 TS / 1164 Python**（与所有者记录完全一致，较 C4 恰 +31 新用例）；本线 **112 项 Python** 独立通过；**21/21 headless 呈现项**在**本方独立输出目录**独立复跑通过（历史截图/日志与 tracked `ui-probe.json` 未被覆盖）。
3. **唯一曾判不通过项已实质关闭**：以抽出到临时目录的 C4 代码做 A/B 对照，**C4 仍抛原生 `UnicodeEncodeError`，C5 返回固定 reason**；我方独立 20 注入点 × 2048 代理码位 = **16,406 组扫描，原生异常 0 / 泄漏 0 / 静默接受 0**；合法 Unicode（中文／emoji／**分解重音**）逐码位保留且**未归一化**；**digest 编码语义可证未变**（C4 与 C5 对同一合法输入 digest 完全相同）。
4. **11 项历史意见逐项独立处置完成**：M-P2-1 关闭（含 Unicode 残留）、C4 残留 P2 关闭、M-P3-1 以显式基线语义关闭、M-P3-2 关闭、M-P3-3 关闭、M-P3-4 部分关闭并降为 P3 观察、M-P3-5 关闭（42 reason / 0 未断言）、Z-P3-1 接受延期且限制保留、Z-P3-2/3/4 关闭、Z-P3-5 部分接受且限制保留。**无一项沿用旧 Pass 字样。**
5. **本方新发现**：无 P0/P1/P2；3 项 P3（1 项私有未导出函数硬化、1 项流程指针滞后、1 项深链性能观察）+ 1 项**明确划归 T01 的范围外观察**。均不构成 S1 验收条款失败。

### 10.2 本通过**不关闭**以下任何门（逐项仍待）

T01 可信当前 domain/metadata/来源/引用投影与当前 scope；正式 canonical/named 桥与真实项目会话；人类确认；唯一原子 commit / receipt / undo；I05 批准 Turtle/SHACL 支持检查与无损往返（语料**未执行**，FR-203 导入能力**未实现**）；I06 正式 App/桥与壳生命周期；T08 真实草稿与模型；FR-200–204 完整跨模块验收与附录 C/F/G、12.1/12.4；两目标平台（Windows/macOS）与真人验收；**指定双审同版双方各自明确通过**（本报告仅为 MiniMax M3.1-Flash 一方，ZCode GLM-5.3 一方结论我方**未读取亦未推断**）；CI 通过、正常 merge、远端核验、上线；P3-1 建议在正式 adapter/IPC/Agent 接线前关闭。

### 10.3 明确声明

- 本报告仅为**本方一份**正式报告；不推断另一方结论，不构成 push/PR/CI/merge/发布授权。
- 父功能、跨平台、真人、CI、合并、远端与发布门**全部保留待验**；S1 子阶段通过**不得**被读作本体功能可用或 FR-200–204 已完成。
- 本方**未修改**任何产品/测试/fixture/依赖锁/配置/验收文件；未 stage/commit/push/PR/merge/checkout 分支；未创建 Goal；未调用模型 API、付费或额度重置；未读取系统凭据；未触碰 T06 或其它 task/session/stdio；未重启被拒的 SQLite 物理实验；未运行 Electron/e2e/native/HMR。
- 本方唯一持久写入：本报告 + `test-results/t02-c5-r2-review/`（原始流、探针脚本、元数据、我方 UI 输出、临时编译产物）。终态 `git status` 仅 `M AGENTS.md`（当前政策传播，未暂存）与总控下发的两个未跟踪准备件。

---

## 11. 本方证据清单

`test-results/t02-c5-r2-review/raw/`：`npm-check-full.log`、`pytest-ontology-4suites.log`、`ui-probe-run.log`、`probe-unicode-independent.log`、`probe-unicode-independent-part2.log`（**首失败：SyntaxError, exit 1**）、`probe-unicode-independent-part2-retry.log`、`probe-unicode-independent-part3.log`、`probe-classtree-perf.log`。
`test-results/t02-c5-r2-review/metadata/`：`input-verification.json`、`product-path-verification.json`、`probe_unicode_independent*.txt`。
`test-results/t02-c5-r2-review/`：`verify_inputs.py`、`verify_product_paths.py`、`probe_unicode_independent*.py`、`probe_classtree_perf.mjs`、`ui/`（本方独立 headless 输出：`ui-probe.json`、`ui-desktop.png`、`ui-mobile.png`）、`tmp/`（本方 `tsc` 临时编译产物）。
