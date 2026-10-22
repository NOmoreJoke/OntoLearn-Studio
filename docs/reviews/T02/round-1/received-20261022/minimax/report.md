# T02-S1 round-1 MiniMax M3.1-Flash 完整独立审查报告

审查日期：2026-10-22（Asia/Shanghai）。本报告为指定模型本方唯一正式报告，独立结论，不引用、不读取、不交换另一审查方本轮输出。

---

## 1. 结论（先给）

**对完整 T02-S1 候选：通过。**

理由摘要：冻结输入全部逐项核验为字节一致（58 项 delta + 10 项引用 + 19 项产品路径，0 不符）；完整 `npm run check` 在同候选上独立复现出与 C3 记录完全相同的数字（633 TS / 1091 Python，exit 0）；本线 39 条 Python 与 3 条 TS 视图测试独立通过；headless UI 探针由我独立重跑，并**字节级复现**出已归档的两张截图（SHA 与原归档完全相同）；历史 H01–H08 全部以代码与运行证据逐项复核为关闭。发现 1 项 P2、4 项 P3，**均不构成当前 S1 验收条款或现行架构不变量的违反**（逐项理由见第 8 节，P2 附带明确的接线前置条件）。

**但本 "通过" 不关闭任何父门。** S1 只是私有领域服务 + 独立页面层；正式 Store 提交、人类确认、Turtle/SHACL 导入、真实草稿、正式 App/桥接、FR-200–204 跨模块完整验收、两目标平台/真人、指定双审同版双方一致、CI/正常合并/远端/上线仍全部待办（第 10 节）。

---

## 2. 任务与设置读回（实际终态）

| 项 | 实际值 | 读回来源 |
| --- | --- | --- |
| 平台 | macOS 27.0.1（Build 26A434），Darwin Kernel 27.0.0，arm64 / Apple Silicon | `sw_vers`、`uname -a` 实际输出 |
| 运行时 | MiniMax Code（本地桌面运行时） | 运行时环境上下文 |
| 真实 taskID / 会话 ID | `mvs_06002009bb614b3bb56905f07eb5b240` | 运行时注入的会话标识 |
| Agent 路由 | `mavis`（本会话 root） | 运行时注入 |
| 指定 provider/model | `MiniMax-M3.1-Flash` | 运行时模型标识（模型列表字段），非由文件名或报告标题推断 |
| 思考等级 | `xhigh`（本任务指定设置） | 指定提示正文；**运行时未提供独立的思考等级读回接口**，故此值按指定值声明，未由独立 API 二次确认 |
| 权限模式 | `bypassPermissions`（始终授权 / Full access） | 指定提示正文 + **行为读回**：全程工具调用（依赖安装、pytest、npm check、headless 浏览器、自建探针）未触发任何逐命令批准 |
| 正文接收时间 | 2026-10-22 17:17 (+0800)（会话启动同一 turn 收到完整正文） | 会话时间戳 |
| 实际开始执行 | 2026-10-22 17:19 (+0800) 首个只读核验命令；17:20:01 首个依赖安装 | 命令/日志 mtime |
| 最终状态 | 终态完成：本报告为该任务的完整交付全文 | 本报告 |
| 模型/会话更换 | 全程未更换模型、未复用其他会话、未借用另一审查方会话或意见 | 本会话工具调用记录 |

说明：本方严格遵守只读职责——未修改产品/测试/fixture/锁/配置/验收，未 stage/commit/push/checkout 分支，未创建 Goal，未调用模型 API、付费、重置，未触碰系统凭据，未触碰 T06 既有任务/session/stdio。

---

## 3. 候选身份与冻结输入核验（实际执行）

### 3.1 固定身份

| 项 | 值 |
| --- | --- |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |
| product head | `49321221733ea927484647352e05e7d833cebc86` |
| input process head | `d597b3c00980652042163d250c875d660d4d371e` |
| **实际 review 工作树 HEAD** | `ce1c3df41a233a07de4ef8fad54d5f201b222a23`（detached） |
| 原受审工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology`，分支 `feature/weekly-t02-ontology` |
| **本方审查工作树** | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-minimax-review-4932122`（detached HEAD） |

review 工作树 HEAD 高于 input process head 的部分**全部是本轮过程文件**（`docs/reviews/T02/round-1/` 下 15 件准备件 + `launch-20261022/`），未改变任何产品/测试/依赖/配置/验收。本报告不把新增过程 commit 称作产品变化。

### 3.2 哈希核验（实际运行，逐项）

| 核验对象 | 数量 | 结果 |
| --- | --- | --- |
| `input-manifest.json` → `fullBranchDeltaFiles`（按各自 `ref` 取 git blob 重算 bytes+SHA256） | 58 | **0 不符** |
| `input-manifest.json` → `unchangedReferences` | 10 | **0 不符** |
| 19 项产品/测试/fixture 在 product ref / process ref / review HEAD / 磁盘四处的同一性 | 19 | **完全一致** |
| 5 项 UI harness 文件在 process ref 与磁盘 | 5 | 一致 |
| `verification-c3.json` 记录的实现哈希 + owning source 哈希 vs 当前磁盘与 product ref | 5 | 全部一致 |
| `verification-c2.json` → `implementation_hashes` vs 当前磁盘 | 22 | **0 不符** |
| `original-log-index.json` 32 条日志：原工作树字节 **与** 归档成员字节 | 32×2 | **0 不符** |
| 证据归档 tar.gz bytes + SHA256 + 成员数 | 1 | `548417B` / `43d9e205…f2a6b86` / **48 成员**，与记录一致 |
| 终态复核（跑完全部探针后重跑 58+10+19） | 87 | **0 不符**，HEAD 与 git status 未变 |

证据：`test-results/t02-s1-r1/streams/verify-final-hashes.log`、`verify-evidence-records.log`、`verify-log-index.log`。

### 3.3 提示与清单哈希

| 文件 | bytes | SHA256 |
| --- | --- | --- |
| `round-1/minimax-m31flash-input.md`（冻结原提示） | 29048 | `20e90310c471bb46ddb24dc1df31969be657382d13af2dac6498be7eedc94e5f` |
| `round-1/launch-20261022/submitted-input.md`（**本方实际收到的完整正文**：冻结原文 + 2026-10-22 桌面执行补充） | 32029 | `5c4317d0700a87b18aa8d9f018e91dac98a68de9a4a6b828711756de143f6a3d` |
| `round-1/input-manifest.json` | 23770 | `6c294b47ffeb4e42270ce824009960b2a9523b9f37adfa546da1d391ec39a527` |
| `round-1/preparation-manifest.json` | 8122 | `0f73be7688ae18b48fb30da37a883e85aaf7114e0755fd0331a4a4ecf2451f54` |

冻结原提示的 SHA256 与总控下发的 `20e90310c471bb46ddb24dc1df31969be657382d13af2dac6498be7eedc94e5f` **完全一致**，确认本方审的是同一份冻结输入。

### 3.4 保护项状态

- 原工作树两张 C2 截图仍为未跟踪保护项，字节与清单一致：`ui-desktop.png` `4dd1d541…07f6`（293943B）、`ui-mobile.png` `87944618…417`（269334B）。已核，未触碰。
- 原 C1 两张截图按清单 `historicalUnrecoverable` 如实缺失，只有原 hash，**未重造、未用 C2 替代**——已逐条核对清单措辞与实际文件状态一致。
- review 工作树 `AGENTS.md` 为当前政策版 15147B / `de15f6ce…c8c4`（未暂存），属操作政策传播，非受审产品漂移。
- review 工作树初始与终态 `git status` 一致：仅 `M AGENTS.md` 与 `?? docs/reviews/T02/round-1/launch-20261022/`；**产品/测试/依赖/配置/验收零改动**。

---

## 4. 实际执行的验证（本方新执行）

### 4.1 环境（独立于原 owner 环境）

在本树按既有锁独立建立，未借用其他功能线的 node_modules/.venv/临时库：

| 命令 | 结果 |
| --- | --- |
| `npm ci` | exit 0，440 packages，0 vulnerabilities（`streams/npm-ci.log`） |
| `uv sync --frozen`（根 workspace，含 dev 组 pytest/ruff/pyinstaller） | exit 0（`streams/uv-sync-root.log`） |

> 注（首失败已按纪律单独保留）：`packages/engine` 单独 `uv sync --frozen` 只装运行时依赖（无 pytest），而 `npm run engine:check` 是从**仓库根**执行 workspace 根 `pyproject.toml` 的 `[dependency-groups].dev`。我第一次在 `packages/engine/` 下同步即在 `packages/engine` 目录执行 pytest，导致 `error: Failed to spawn: pytest`、**exit 2**。该首失败原样另存于 `streams/pytest-ontology-s1-first-failure.log`（含完整原始 stdout/stderr、工作目录、exit 与实际补救动作），成功运行另存 `streams/pytest-ontology-s1.log`。**未修改锁或任何测试来掩盖该失败**；该失败是我方调用环境缺陷，不是产品缺陷，也未据此得出任何产品结论。

版本绑定：Node v24.15.0、Python 3.12.12、rdflib 7.6.0、pytest 9.1.1、ruff 0.17.1、vite 8.3.4、Chromium `151.0.7922.34`（与 C2 记录同版本）。

### 4.2 实际命令、结果与真实 exit

| # | 命令（工作目录：review 树根，除注明） | exit | 结果 |
| --- | --- | --- | --- |
| 1 | `uv run --frozen pytest packages/engine/tests/test_ontology_editor.py packages/engine/tests/test_ontology_source_projection.py packages/engine/tests/test_ontology_fixed_inputs.py -v` | **0** | **39 passed**（本线 Python，与 C3 记录 39 一致） |
| 2 | `npm run check`（= lint + format:check + typecheck + vitest + build + ruff + pytest） | **0** | **633 TS passed / 16 files passed；1091 Python passed（57.06s）**——与 C3 `verification-c3.json` 记录数字**完全一致** |
| 3 | `T02_HEADLESS_EXECUTABLE=<chrome-headless-shell 1234> node docs/iterations/T02/ui-probe/check.mjs` | **0** | 11 项 headless 探针全过；**重新生成的 `ui-desktop.png`/`ui-mobile.png` 与已归档 C2 截图字节完全相同**（`4dd1d541…`、`87944618…`）；重新生成的 `docs/reviews/T02/ui-probe.json` 与 tracked 归档索引**字节完全相同** |
| 4 | `uv run --frozen python` 探针：RDF 规范化 14 种边界文本 | 0 | 全部 `Literal.n3()` 正确转义且经 RDFLib 往返一致（含 `"""`、尾随 `"`、反斜杠、CRLF、NUL、FF/VT、Unicode） |
| 5 | 同上：批量删除影响 / digest 语义 8 组反例 | 0 | 详见第 8 节 P3-1；**无下漏**，只有保守过报 |
| 6 | 同上：RDFLib 对 5 项 Turtle 语料解析与 manifest 哈希 | 0 | 5/5 声明哈希与实际相符；`invalid-turtle.ttl` 如期 `BadSyntax`；其余 4 项可解析 |
| 7 | 同上：Turtle 序列化往返 | 0 | 4 项**全部 `rdflib.compare.isomorphic == True`** |
| 8 | `node`（esbuild 打包 view-model）：`classTree`/`localGraph` 性能 | 0 | `classTree` n=1000→16.5ms、n=2000→81.8ms（超线性，见 P3-4） |
| 9 | `node`（esbuild + `react-dom/server`）：25 对象分页 SSR 断言 | 0 | caption「共 25 项」、首页恰 **20 行**、下一页可用、上一页禁用——**FR-202 每页 20 项经我独立验证成立**（候选自有探针未覆盖，见 P3-3） |
| 10 | `python` 探针：错误契约 18 组畸形输入 + 24 组语义异常输入 | 0 | 语义异常输入**全部**落在固定 `OntologyError` 码；畸形**类型**输入 6 处抛原始异常（P2-1） |
| 11 | `python` 探针：`OntologyError` reason 覆盖率 | 0 | 代码可抛 38 个 reason，候选测试仅断言 22 个；**16 个未被断言**，我逐个实测其行为**全部正确**（P3-5） |
| 12 | 证据归档 tar.gz / 32 条日志 / readback / git-readback 核验 | 0 | 全部一致（见 3.2） |

原始完整 stdout/stderr、exit code、探针脚本输出全部在 `test-results/t02-s1-r1/streams/`（16 份），首失败未覆盖。

### 4.3 沿用原候选证据（我未重跑，不计为我方新验证）

- C3 `verification-c3.json`：完整 check 633/1091、本线 39、来源专项 13 —— **我方以命令 1、2 独立复现**，故此条已从"沿用"升为"独立复现"。
- C2 `verification-c2.json`：11 项 headless 合成 callback 呈现核验 —— **我方以命令 3 独立重跑并字节复现截图与索引**，不再是单纯沿用。
- C1 `verification.json`：历史 check 633/1075、sources-first 12 归档源 exit 0、原失败 —— 保留历史身份，未混计为当前结果。
- C1 原首失败（格式、reference 顺序断言、浏览器执行器缺失、多行旧期望）与 C2 首失败（fact 顺序断言、键盘 caret）—— 原始字节在归档 41 日志中，已逐条核对存在且哈希相符。

### 4.4 明确未执行（不得记为通过）

Electron / e2e / native / HMR / 打包产物内运行 / Windows·macOS 安装 / 真实模型外发 / 正式 IPC / 正式 Store 写入 / 正式人类确认 / T01 提交与撤销 / Turtle·SHACL 导入与无损往返 / T08 真实草稿 / 两目标平台 / 真人验收 / CI / push / PR / merge / 远端核验 / 上线 —— **本轮全部未执行**。

> HMR 探针 `tests/e2e/csp-lifecycle.spec.ts` 仅在 `I02_HMR=1` 且运行 e2e 时改写源文件；本轮未运行 e2e，未触发改写。

---

## 5. 覆盖清单

### 5.1 19 项产品/测试/fixture（逐项读毕 + 逐项 hash 核对）

| 路径 | 已读 | 已核 hash | 审查要点 |
| --- | --- | --- | --- |
| `apps/desktop/src/renderer/src/ontology/OntologyPage.tsx` | ✅ | ✅ | 草稿基准、迟到回复、异项目卸载隔离、删除影响门控、Diff 呈现 |
| `apps/desktop/src/renderer/src/ontology/ontology.css` | ✅ | ✅ | 无 `unsafe-inline`/`unsafe-eval`；850px 断点；SVG 样式 |
| `apps/desktop/src/renderer/src/ontology/view-model.ts` | ✅ | ✅ | 类树循环/多父、局部图一跳与截断、`isCurrentPreview` |
| `packages/engine/src/ontolearn_engine/ontology/__init__.py` | ✅ | ✅ | 导出面封闭，无持久化/协议/model 调用 |
| `…/ontology/model.py` | ✅ | ✅ | 不可变输入、kind/类型/字面量白名单、唯一可编辑表示、引用完整性 |
| `…/ontology/service.py` | ✅ | ✅ | 纯编辑计划、完整 RDF 增删、删除影响、digest 守卫、Copy 语义 |
| `…/ontology/source_projection.py` | ✅ | ✅ | 完整 RDF 集合相等、原 record ID/归属/人工覆盖/墓碑/多重支持、定义 payload hash 与原 triples 下标 |
| `packages/engine/tests/test_ontology_editor.py` | ✅ | ✅ | 23 条，含 7 组参数化负例 |
| `packages/engine/tests/test_ontology_fixed_inputs.py` | ✅ | ✅ | T09 固定 G-base 原字节、10 定义/18 断言**具体集合**比对（非计数） |
| `packages/engine/tests/test_ontology_source_projection.py` | ✅ | ✅ | 13 条，真实临时 SQLite、读取零写入 |
| `tests/fixtures/ontology/invalid-turtle.ttl` | ✅ | ✅ | 如期语法拒绝 |
| `tests/fixtures/ontology/manifest.json` | ✅ | ✅ | 5/5 声明哈希与实际相符；`purpose` 已声明为未来 I05 输入 |
| `tests/fixtures/ontology/manual-supported.ttl` | ✅ | ✅ | 16 三元组，RDFLib 可读、往返同构 |
| `tests/fixtures/ontology/supported-shacl-template.ttl` | ✅ | ✅ | 16 三元组/4 空白节点，往返**同构** |
| `tests/fixtures/ontology/t09-fixed-inputs/G-base.json` | ✅ | ✅ | 与 manifest 声明哈希一致 |
| `tests/fixtures/ontology/t09-fixed-inputs/manifest.json` | ✅ | ✅ | 被测试以硬编码 `MANIFEST_SHA` 锚定，非自证 |
| `tests/fixtures/ontology/unsupported-owl.ttl` | ✅ | ✅ | 含 `owl:equivalentClass`+`Restriction` |
| `tests/fixtures/ontology/unsupported-shacl-path.ttl` | ✅ | ✅ | 含 `sh:inversePath` |
| `tests/unit/t02-ontology-views.test.ts` | ✅ | ✅ | 3 条，锁定类树完整顺序与一跳图/截断 |

### 5.2 5 项 UI harness（逐项读毕 + 独立重跑）

`build.mjs`（vite 构建，无 configFile 复用）、`check.mjs`（Playwright headless，`route.fulfill` 本地静态产物，无 HTTP 端口/外联）、`fixture.json`（纯领域样本 6 对象/13 三元组）、`harness.tsx`（**纯合成 callback**：无 Store/IPC/产品）、`index.html`。

**合成 callback 边界核验（逐项）**：`previewEdit` 返回的 `project/revision` 取自**请求时**的 `base`，因此版本推进后旧回复必然 `isCurrentPreview` 失配 → 报错而非展示；`requestDeleteImpact` 恒返回固定合成串；失败分支抛 `synthetic failure`；延迟分支由探针按钮手动释放。**探针不产生也不伪装任何 Store/IPC/产品/e2e/模型证据**——它只证明 React 状态呈现与并发隔离。

### 5.3 全部过程证据（58 项 delta 中 39 项非产品）

`acceptance.md`、`delivery.md`、`interface-handoff.md`、`source-projection.md`、`stage-registration-request.md`、`controller-message-draft.md`、`status.md`（22KB）、`independent-review-c1/c2/c3.md`、`stage-registration-review.md`、`verification.json`/`verification-c2.json`/`verification-c3.json`、`ui-probe.json`、`t09-input-verification.json`、`controller-message-receipt.json`、`evidence-archive/`（README/archive-index/manifest/readback/git-readback/independent-review/tar.gz）、`round-1/` 全部准备件与 `launch-20261022/` 全部 8 件、`typed-changeset-integration-plan` 十件（含 `independent-review-initial/final`、`disposition`、`source-manifest`、`static-verification*`）—— **全部读毕并核对**。

### 5.4 PRD 对照

已读 FR-200/201/202/203/204 原文（`docs/prd/PRD-本体学习与落地Agent工作台.md:307–333`）、附录 C 能力矩阵（:959–979）、附录 D（:983）、附录 E（:1016）、附录 F（:1096）、附录 G（:1115 起）、10.2 性能与容量（:713–718）、Q5（:903）、FR-804（:521）。附录 C 明确：`rdfs:domain/range` **不得当作必填约束**（S1 遵守）、`rdf:type`/label/comment **多语言按字面量保留**（S1 遵守）、OWL 类表达式与逆向 SHACL 路径 **P0 不承诺**（S1 不提供，语料仅作未来输入）。

---

## 6. 历史意见逐项依据（不采信"已关闭"字样）

| 编号 | 我的独立依据 | 结论 |
| --- | --- | --- |
| **H01** 旧草稿被套用新版本 | `OntologyPage.tsx:75` 独立 `draftBase`；`:124-128` `plan()` 比对 `base !== identity(view)` 即拒绝；`:350-352` 告警；`:456` 提交按钮在基准不符时禁用；`:75-76` 事实表单另持 `factBase`；`:86-91` 卸载时 `request.current++`；`:108` 每次输入 `request.current++` 作废旧预览；`:68` `key={view.project}` 跨项目重挂载。命令 3 独立重跑探针，逐条复现"版本推进后禁用 + 保留草稿 + 迟到回复不替换新草稿 + 切项目隔离 + 卸载隔离" | **关闭** |
| **H02** 单值名称/定义丢多语言 | `LocalizedFields`（`:548-599`）按 (text,language) **逐项**渲染独立 textarea 与独立语言输入框，`onChange` 以 map 保留语言；`normalizedDraft`（`:54-65`）**不触碰** labels/definitions；命令 3 实测意图收到 `[['设备','zh'],['Equipment\nAssets','en']]` 与完整多行定义 | **关闭** |
| **H03** `Entity.types` 与 `rdf:type` 事实双重可编辑 | `model.py:172-173` 事实通道对 `rdf:type/rdfs:label/rdfs:comment` 一律 `entity_field_required`；`service.py:92-99` 实体字段单向编译为 RDF；仅一处可编辑表示 | **关闭** |
| **H04** label/comment 绕过字面量白名单 | `model.py:163-168` 字面量 datatype 白名单与 `ill_typed` 检查**先于** `:172-173` 的入口拒绝；命令 10 实测：未知 datatype → `unsupported_datatype`，`"abc"^^xsd:integer` → `invalid_literal`，`"2020-13-45"^^xsd:date` → `invalid_literal` | **关闭** |
| **H05** C1 P2 多行定义被单行 input 截断 | C1 `438c6ad` 不通过原件保留；C2 `5ef86a1` 改 textarea；当前 `OntologyPage.tsx:564-573` 为 `<textarea rows={定义?3:1} maxLength={16000}>`。**我以命令 3 独立重跑**，其 `check.mjs:44-58` 真实键盘 Enter + `pressSequentially` 断言通过，且截图字节复现——非采信报告标题 | **关闭** |
| **H06** C3 非阻断 P3：delivery 入口仍指 C2 | `delivery.md:3` 已改述当前实现为 C3 `4932122…`、证据以 `status.md`/`verification-c3.json` 为准；`:5` 明确 C2 记录仅作历史、不得当恢复指针。属**纯流程指针**修正，不含产品/测试/配置/依赖/验收/基线变化，按现行规则不触发无变化重审 | **关闭**（文档层） |
| **H07** 原始日志/截图仅本地不受控 | 归档 tar.gz `548417B`/`43d9e205…f2a6b86`/48 成员（41 日志 + 2 C2 截图 + 4 索引 + 1 manifest）经我复核一致；32 条索引日志在**原工作树**与**归档成员**两侧字节均一致；`git-readback.json` 记录 `c30927000bdf7fafd5f396c08b39ae3ce9829f6d` 恢复 48 成员。**我进一步独立重跑探针并字节级复现两张 C2 截图**——强于原声明。限制如实保留：仅本机 Git 对象恢复，无远端/异机备份；C1 两图仅存 hash | **关闭**（限制保留） |
| **H08** 后续集成方案来源 proof 未贯穿、预算无执行前接点 | `typed-changeset-integration-plan/independent-review-initial.md` 保留初版 `64bbfe2` 两项 P2 **不通过**原件；`disposition.md` 逐项列修订并注明「**仅方案层**」；`independent-review-final.md` 为修订版复审通过。方案文档本身明确「没有实施来源绑定或 meter，也没有运行产品」。**未冒充 metadata/commit/meter 已实现** | **方案层关闭**（S1 未实现，非本轮问题） |

---

## 7. 我方新发现的边界与反例（探针原始记录）

| 探针 | 结论 |
| --- | --- |
| RDF 规范化 14 种文本边界 | 全部正确转义并往返一致，**无缺陷** |
| Turtle 语料解析/往返 | 5/5 哈希相符；`invalid-turtle.ttl` 如期拒绝；4 项往返**同构**。首轮我用朴素 `set(g)==set(g2)` 曾误报 `supported-shacl-template.ttl` 往返 False，经 `rdflib.compare.isomorphic` 复核实为**空白节点身份差异**导致的假阳性，非数据丢失 |
| 语义异常输入 24 组 | 全部落在固定 `OntologyError` 码（`invalid_language`/`invalid_text`/`invalid_identifier`/`invalid_iri`/`field_not_applicable`/`invalid_class_type`/`class_reference_required`/`invalid_literal`/`invalid_rdf_term` 等） |
| 畸形**类型**输入 6 组 | **原始 AttributeError/TypeError 逃逸** → P2-1 |
| 批量删除影响 | 仅**保守过报**，无下漏（最终 `validate(candidate)` 兜底） → P3-1 |
| digest 语义 | metadata-only 变化、旧 project、revision 变更、实体/事实乱序 —— 全部按预期（内容敏感、对顺序不敏感） |
| 错误 reason 覆盖 | 38 个可抛 reason，候选断言 22 个，**16 个未断言**；我逐个实测**行为全部正确** → P3-5 |
| `classTree` 性能 | n=1000→16.5ms，n=2000→81.8ms，超线性 → P3-4 |
| 分页（SSR，25 对象） | 首页恰 20 行、caption「共 25 项」、下一页可用 → FR-202 成立 → P3-3（证据缺口由我补齐） |

---

## 8. 新发现问题（按 P0–P3）

### P2-1　引擎公开 API 对畸形元素类型抛原始 Python 异常，偏离固定错误码契约

- **严重度**：P2
- **位置**（固定行号，均为本候选真实行）：
  - `packages/engine/src/ontolearn_engine/ontology/model.py:105` — `entities = {item.iri: item for item in snapshot.entities}`
  - `packages/engine/src/ontolearn_engine/ontology/model.py:160` — `fact.triple()`
  - `packages/engine/src/ontolearn_engine/ontology/model.py:187` — `reference.target`
  - `packages/engine/src/ontolearn_engine/ontology/service.py:160` — `target = command.entity.iri if isinstance(command, Put) else command.iri`
  - `packages/engine/src/ontolearn_engine/ontology/service.py:188` — `set(add_facts)`
- **触发**（实测）：
  | 调用 | 逃逸 |
  | --- | --- |
  | `change_preview(snap, add_facts=("notafact",))` | `AttributeError: 'str' object has no attribute 'triple'`（model.py:160） |
  | `change_preview(snap, add_facts=({"subject":"x"},))` | `TypeError: unhashable type: 'dict'`（service.py:188） |
  | `change_preview(snap, (Put(None, True),))` | `AttributeError: 'NoneType' object has no attribute 'iri'`（service.py:160） |
  | `change_preview(Snapshot("p",1,("notanentity",)))` | `AttributeError`（model.py:105） |
  | `change_preview(Snapshot("p",1,(),("notafact",)))` | `AttributeError`（model.py:160） |
  | `change_preview(Snapshot("p",1,(),(),("notareference",)))` | `AttributeError`（model.py:187） |
- **影响**：`model.py:20-26` 明确声明 `OntologyError` 是「Internal fixed reason and field location, **never an underlying parser message**」；仓库级不变量亦要求「跨边界只传固定错误码……不回传原始异常、堆栈」。当前 `ontology` 包为**私有 Python 服务**（`__init__.py:1` 声明「No persistence, protocol registration or model calls」），**尚未**暴露到 IPC / UI / Agent，故今日无用户可见影响、无数据损坏、无错误写入；一旦 T01/T00 adapter 转发未经校验的表单行，即会把 Python 原始异常与堆栈带过边界。
- **为何仍列 P2 而非 P3**：这是错误契约的**系统性**缺口，且触发条件是**调用方类型错误**而非语义错误——正是适配层最容易犯、且最难在集成期定位的一类缺陷；C1 的 P2 判不通过是因为它造成可达的用户数据丢失，本项**不可由任何现有用户路径触发**，故不构成不通过，但必须在接线前关闭。
- **证据**：`test-results/t02-s1-r1/streams/probe-error-contract.log`
- **建议**：在 `model.validate` 起始处对 `entities/facts/external_references` 元素做 `isinstance` 守卫，抛 `OntologyError("invalid_entity")` / `"invalid_fact"` / `"invalid_external_reference"`；在 `service.change_preview` 对 `Put.entity` 与 `add_facts/remove_facts` 元素做类型守卫，抛 `OntologyError("invalid_command")` / `"invalid_fact"`。补 6 条回归用例。
- **强制前置条件**：本项须在 `ontology` 服务被接入任何 adapter / IPC / Agent 边界**之前**关闭。该接线本身已在 T01/I06 父门下阻塞，故不改变本轮 S1 判定。

### P3-1　批量删除影响按基准快照计算，可能包含同批次已消除的引用（保守过报）

- **严重度**：P3
- **位置**：`packages/engine/src/ontolearn_engine/ontology/service.py:184` — `impact.update(deletion_impact(snapshot, target))`，此处 `snapshot` 是**基准**快照而非同批次演进中的 `entities`。
- **触发**：同一批次内 `Delete(E)` + `Put(P, domain=())` + `Put(D, types=())`。
- **影响**：实测该批次**成功提交**，但 `preview.deletion_references` 仍列出 `(P,'domain')` 与 `(D,'types')`，而候选中两者已为空——UI「删除影响」清单会显示本批次已自行解除的引用。反向（**下漏**）不存在：任何候选中残留的悬空引用都会被 `service.py:199` 的 `validate(candidate)` 拒绝（实测 `individual_reference_required`）。即恒为保守方向，不致错误写入，但呈现与最终状态不一致。
- **证据**：`test-results/t02-s1-r1/streams/probe-batch-semantics.log`
- **建议**：影响计算改用同批次候选状态，或把该清单显式命名为「基准快照中的引用」并在 UI 标注基准版本。

### P3-2　`EditIntent` 的 `copy` 变体在页面中从未发出，复制路径不保留来源关联

- **严重度**：P3
- **位置**：`apps/desktop/src/renderer/src/ontology/OntologyPage.tsx:21` 声明 `{ action: 'copy'; source: string; iri: string; identifier: string }`，但全文件**无任何** `action: 'copy'` 的发出点；「复制定义到新表单」（`:311-322`）产出的是 `iri=''`、`identifier=''` 的**匿名 create** 意图。
- **影响**：用户可见的复制功能本身可用（定义/元数据进入新表单），但**复制来源关联永远到不了引擎**，`service.Copy`（`service.py:172-180`，保留来源、只复制定义不复制实例断言）**仅被测试触达，产品路径不可达**。声明的类型面与实际产品能力不一致，存在被后续审查者/集成方误读为「已实现带来源溯源的复制通道」的风险。
- **证据**：`grep 'copy' OntologyPage.tsx` 仅命中类型声明行；`probe` 与源码通读。
- **建议**：二选一 —— (a) 让「复制定义到新表单」发出真实 `copy` 意图（含 `source`），使 `service.Copy` 的来源语义在产品路径可达；(b) 删除该死变体并在类型注释中写明复制语义与来源丢弃事实。

### P3-3　表格分页、复制、事实表单等 UI 路径无任何候选内自动化验证（本方已独立补验）

- **严重度**：P3（证据覆盖缺口，非产品缺陷）
- **位置**：`apps/desktop/src/renderer/src/ontology/OntologyPage.tsx:101`（`currentPage` 计算）、`:224`（`rows.slice(...)`）、`:239-248`（翻页按钮）—— 分页逻辑**内联在组件中**，不在受单测覆盖的 `view-model.ts` 内。
- **触发**：候选的 headless 探针 `docs/iterations/T02/ui-probe/check.mjs` 与单测 `tests/unit/t02-ontology-views.test.ts` 中，以下选择器命中数**均为 0**：`下一页`、`上一页`、`复制定义到新表单`、`预览新增事实`、`预览移除事实`、`新建概念`、`查找概念`、局部图截断文案、邻近关系列表。
- **影响**：`docs/iterations/T02/acceptance.md` 的 FR-202 行把「表格每页 20 项」的验证写为「纯视图模型完整集合/顺序，headless 组件表格/树/图」，但 headless 组件探针**从未点击表格分页**，视图模型单测也**不含分页**——该条验收的验证描述与实际断言不符。**产品行为本身正确**：我以 SSR 独立断言（25 对象）实测首页恰 20 行、caption「共 25 项 · 每页 20 项」、下一页可用、上一页禁用。
- **证据**：`test-results/t02-s1-r1/streams/probe-ssr-pagination.log`
- **建议**：把分页计算抽入 `view-model.ts` 供单测覆盖，并在 headless 探针补表格翻页、复制、事实新增/移除三组断言；或修正 `acceptance.md` 的验证描述以如实标注未覆盖项。

### P3-4　`classTree` 为 O(n²) 且在组件渲染中无条件计算

- **严重度**：P3
- **位置**：`apps/desktop/src/renderer/src/ontology/view-model.ts:43-46`（对每个已访问节点执行 `classes.filter(item => item.parents.includes(row.iri))` 并排序 → 总体约 O(n² log n)）；`apps/desktop/src/renderer/src/ontology/OntologyPage.tsx:102` — `const tree = classTree(view.objects)` 在组件体中**无条件**执行，即**每次渲染**（含编辑表单每次按键）都会重算整棵树，即使「类树」页签并未显示。
- **触发**：类数量增大或用户连续输入。
- **影响**：实测单次 `classTree`：n=1000 → **16.5ms**，n=2000 → **81.8ms**（呈超线性）。PRD 10.2 明确数据量/响应时间指标【待确认】且禁止未经验证的大规模承诺，故**本报告不给出任何容量通过线**，仅陈述实测点与结构性问题。
- **证据**：`test-results/t02-s1-r1/streams/probe-perf-viewmodel.log`
- **建议**：按 `view.objects` 身份做 memo；并仅在 `tab === 'tree'` 时计算；树构建可改为一次性建立 parent→children 索引（O(n)）。

### P3-5　38 个错误 reason 中仅 22 个被候选测试断言（16 个未覆盖，实测行为全部正确）

- **严重度**：P3（证据覆盖缺口，非代码缺陷）
- **位置**：`packages/engine/src/ontolearn_engine/ontology/{model.py,service.py,source_projection.py}` 全模块；测试侧 `packages/engine/tests/test_ontology_{editor,fixed_inputs,source_projection}.py`
- **触发**：静态统计代码中全部 `OntologyError("...")` 字面量，与候选测试中的字符串断言求差集。
- **影响**：未被断言的 16 个 reason：`contradictory_fact_command`、`duplicate_fact_command`、`duplicate_iri`、`duplicate_value`、`invalid_class_type`、`invalid_external_reference`、`invalid_identifier`、`invalid_iri`、`invalid_language`、`invalid_literal`、`invalid_text`、`invalid_value`、`project_required`、`projection_origin_missing`、`unsupported_command`、`unsupported_kind`。**我逐个实测，16/16 行为全部正确并抛出预期固定码**（其中 `projection_origin_missing` 是 `removed_sources` 的关键越界守卫）。问题在于 `acceptance.md` 的 FR-200 行称「完整预期与异常」，与此不符。
- **证据**：`test-results/t02-s1-r1/streams/probe-reason-coverage.log`
- **建议**：补齐这 16 条回归断言（成本极低），或把 `acceptance.md` 的「完整预期与异常」改为如实描述已覆盖集合。

### 未列为 P 级的两项（已核，属已披露边界，非缺陷）

- **Turtle/SHACL 语料未被任何测试执行**：`tests/fixtures/ontology/*.ttl` 与 `manifest.json` 无任何测试引用；`manifest.json:3` 已自述 `purpose = "Future approved I05 import/roundtrip integration inputs, not executed product acceptance"`；`packages/engine/src/ontolearn_engine/ontology/` 内无任何 turtle/shacl/import 路径（grep 为空）。**这与冻结提示的警告完全一致**（"Turtle corpus 存在、RDFLib 基础项可读不等于安全导入/完整模板/往返"），且 `acceptance.md` FR-203 行已如实列为 I05/T01/T00 待办。我已独立核验：5/5 声明哈希相符、`invalid-turtle.ttl` 如期拒绝、4 项往返同构。**该语料不得被计入 S1 导入能力证据**；FR-203 导入仍是父门。
- **未随 review 树携带两张原 PNG**：`docs/reviews/T02/ui-*.png` 在 review 树中原本缺席（保护项原件在原工作树与归档中，均已核验一致）。我用探针重生成后**字节与归档完全相同**，随即把生成物移入本方证据目录并以可恢复方式从 review 树移除，使 review 树回到运行前状态（git status 与 19 项产品路径 hash 均复验一致）。

---

## 9. 本轮候选未被本方改变（写入面声明）

- 产品/测试/fixture/依赖锁/配置/验收：**零改动**（终态 git status 仅 `M AGENTS.md` 与 `?? launch-20261022/`，均为总控下发的政策/准备件，非我方写入）。
- 允许写入范围仅限：本树独立 `node_modules`/`.venv`、测试缓存、`test-results/t02-s1-r1/` 下的原始流与探针产物、以及本报告。
- 未 stage / commit / push / PR / merge / checkout 分支；未改 root 控制记录；未创建 Goal；未读写系统凭据；未新增付费/模型调用/额度重置；未触碰 T06 的任务、session 或 stdio；未运行已被拒绝的 SQLite 物理实验。
- 探针过程中曾由 `docs/iterations/T02/ui-probe/check.mjs` 在本树生成 `docs/reviews/T02/ui-desktop.png`、`ui-mobile.png` 并重写 tracked 的 `docs/reviews/T02/ui-probe.json`；三者均已核验为**与归档字节完全相同**（即生成结果 == 既有内容），生成的 PNG 已移入 `test-results/t02-s1-r1/generated-screenshots/` 保留为证据，并以 `mavis-trash` 可恢复方式从本树移除。终态该 tracked 文件 `git diff` 为空、hash 未变。

---

## 10. 父门与未关闭项（本报告不关闭）

**仍待（不可因 S1 通过而视为完成）**：T01 可信 domain/metadata/来源/引用投影与当前 scope；正式 canonical / named 桥 / 真实项目会话；人类确认；唯一原子 commit / receipt / undo；I05 批准 Turtle/SHACL 列表与全部支持检查及无损往返；I06 正式 App/桥与壳生命周期；T08 真实草稿与模型；FR-200–204 完整跨模块验收、附录 C/F/G 与 12.1/12.4；两目标平台（Windows/macOS）与真人验收；**指定双审同版双方各自明确通过**（本报告仅为 MiniMax M3.1-Flash 一方，ZCode GLM-5.3 一方结论我方未读取亦未推断）；CI 通过、正常 merge、远端核验、上线；P2-1 必须在任何 adapter/IPC/Agent 接线前关闭。

**Q6 已由用户采纳推荐规则与规范 pin，不再询问**；该采纳不等于当前已实现全部类型/语义。本轮无共享写权限，未改 `state.json` 等总控文件。

---

## 11. 证据清单（本方原始流，均在本方登记目录）

`test-results/t02-s1-r1/streams/`：`npm-ci.log`、`uv-sync.log`、`uv-sync-root.log`、`pytest-ontology-s1.log`、`npm-check-full.log`、`ui-probe-run.log`、`probe-turtle-corpus.log`、`probe-turtle-roundtrip.log`、`probe-boundary-edge.log`、`probe-batch-semantics.log`、`probe-perf-viewmodel.log`、`probe-ssr-pagination.log`、`probe-error-contract.log`、`probe-reason-coverage.log`、`verify-evidence-records.log`、`verify-log-index.log`、`verify-final-hashes.log`；另有 `pre-run/`（运行前快照与 19 项产品路径 hash）与 `generated-screenshots/`（独立重生成的 C2 截图）。

---

## 12. 最终判定

**通过。**

完整 T02-S1 候选在本方独立审查下：冻结输入字节一致、完整 check 独立复现（633 TS / 1091 Python，exit 0）、本线 39 Python + 3 TS 通过、headless 呈现探针独立重跑并字节复现归档截图与索引、历史 H01–H08 逐项以代码与运行证据复核为关闭。发现 1 项 P2 与 4 项 P3，均已给出固定行号、触发、影响、证据与建议；**无一项构成当前 S1 验收条款的失败或现行架构不变量的违反**，P2-1 已附加"任何 adapter/IPC/Agent 接线前必须关闭"的强制前置条件。

本通过**仅限**本方 S1 私有服务与独立页面层，**不构成**对父功能、正式存储/桥接、导入往返、跨平台、真人验收、双审一致、CI/合并/远端/上线的任何通过结论。
