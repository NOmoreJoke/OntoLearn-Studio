# T02-S1 round-1 ZCode GLM-5.3 独立完整审查报告

- 审查者：本轮全新独立指定审查者（ZCode 桌面会话，由 T02 owner 于 2026-10-22 桌面创建窗口内新建；无独立可读数字 taskID，不伪造）。
- 平台：macOS darwin 27.0.0 arm64（本机）。会话创建/正文接收：launch-20261022 包落盘 2026-10-22 17:13（+08:00），本会话当日接收冻结提示与执行补充全文并开始执行；报告完成见本文件。
- 模型/设置读回：运行环境标识 `account:bigmodel-individual-coding-plan/GLM-5.3`，思考等级最高（会话配置），权限为完全访问（permission.mode=yolo，与 launch 文件及当前 AGENTS「ZCode / MiniMax Code 默认执行权限（2026-10-21 用户确认）」一致）。完全访问不改变只读审查职责：本轮未修改任何实现/测试/fixture/锁/配置/验收，未 stage/commit/push/切分支。
- 最终任务状态：真实完成（见下"终态"）；无认证/额度/服务错误发生，无需恢复操作。

## 固定身份与输入完整性

| 项 | 值 | 核验 |
| --- | --- | --- |
| 原工作树（冻结映射来源） | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology`，分支 `feature/weekly-t02-ontology` | 只读映射，未进入 |
| 本审查工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-zcode-review-4932122`，detached HEAD `ce1c3df41a233a07de4ef8fad54d5f201b222a23` | `git rev-parse` 实测 |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | commit 存在；10 项基线引用哈希一致 |
| product head | `49321221733ea927484647352e05e7d833cebc86` | commit 存在；19 产品路径逐字节=该 ref=manifest=工作树 |
| C2/C1 历史 | `5ef86a1da88d86f2de7b55a7e3be38b1e0f986b4` / `438c6ade34795cb3b0111f0bca463d4fd091b393` | commit 存在，仅作历史证据归属 |
| 冻结输入 process head | `d597b3c00980652042163d250c875d660d4d371e` | commit 存在 |
| 原冻结提示 | `round-1/zcode-glm53-input.md` 全文 28991B，SHA256 `58a62654038514f80528b147e73631acb70ddeaaa7a607f920dfccc76f761f35` | 实测一致；`launch-20261022/submitted-input.md` 内嵌 BEGIN/END 段哈希同样一致 |
| input-manifest | 58 个 delta（19 产品/测试/fixture + 5 harness + 34 流程/方案证据）+ 10 基线引用 + 3 保护未暂存项 + 5 政策快照 + 2 可复现 diff | 逐项三方核对（manifest / 工作树 / git ref）68/68 全部 OK，见 streams/010 |
| 终态复核 | 审查全部执行后 68 项 tracked 输入哈希全部不变；HEAD 仍 `ce1c3df`；无任何受审路径修改 | streams/070 |
| 保护项 | 两张未跟踪 PNG（`ui-desktop.png`/`ui-mobile.png`，哈希 4dd1d541…/87944618…）在本隔离树按构造不存在（新 worktree 不携带未跟踪文件）；其封存副本在 Git 内 tar 包（实测 48 成员、548417B、SHA `43d9e205…` 一致）。未复制、未重造、未暂存 | streams/015/020 |
| 本树 AGENTS.md | 为当前政策版本 de15f6ce…（未暂存、不提交），与 `AGENTS-current-20261022.txt` 逐字节一致；这是当前政策明确授权的携带方式，非受审产品漂移。原 78df… 仅是原树历史输入哈希 | streams/015 |

未读取、未写入另一方（MiniMax）本轮任何输入意见或报告；未触碰 T06 任务/会话/stdio；未另启共享 dataDir runtime；未做已被拒绝的 SQLite 物理实验（所有 SQLite 用例均为测试内临时库，与原证据相同）。

## 范围与覆盖（完整，未截断）

按 input-manifest 完整覆盖，非 UI 或提示子集：

1. **19 个产品/测试/fixture 路径**：逐文件全文审查（见下节）。
2. **5 个 headless harness 文件**（`docs/iterations/T02/ui-probe/{build.mjs,check.mjs,fixture.json,harness.tsx,index.html}`）：全文审查，含其真实探针覆盖与合成 callback 边界（见"UI harness 审查"）。
3. **流程证据**：`acceptance.md`、`source-projection.md`、`stage-registration-request.md`、`interface-handoff.md`、`delivery.md`、`controller-message-draft.md`、`status.md`（22KB 全文）、`verification.json`/`verification-c2.json`/`verification-c3.json`、三份内审报告、`stage-registration-review.md`、`t09-input-verification.json`、`ui-probe.json`、evidence-archive 全套（README/archive-index/manifest/readback/git-readback/independent-review/tar 包）。
4. **后续纯方案 10 文档**（typed-changeset-integration-plan*）：按 context-only 角色 reading，确认其自我声明"方案层关闭、未实施"与 `disposition.md` 一致，未发现把方案冒充实现的表述。
5. **索引**：`original-log-index.json`（32 条索引日志）、`history-disposition-index.md`、`scope-and-evidence.md` 全文。
6. **需求依据**：PRD V0.6 的 FR-200–204、FR-804 原文与附录 C（能力矩阵）、D.1/D.2、12.1/12.4、10.3 关键条款原文。

## 实现审查结论（逐 19 路径）

### Python 引擎（4 文件）

- `ontology/__init__.py`：仅导出私有 API，无持久化/协议注册/模型调用。
- `ontology/model.py`：不可变 `Entity/Fact/Snapshot/Triple/ExternalReference`。`Triple` 强制对象为 rdflib 单术语规范 n3 形式（`term(o).n3()==o`），我独立验证了带类型/语言/多行/内嵌引号/反斜杠字面量的往返全部成立，注入串与裸数字被拒。`validate()` 完整覆盖：project/revision 类型、元组不可变性、IRI 重复（IRI 是身份；identifier 允许跨实体重复）、kind/class_type/identifier 约束、labels/definitions 全语言集合（唯一性按 (text,lang)、语言小写子集、16000 上限）、parents/domain/range/types 的字段适用性与目标种类（dataProperty range 仅限 7 个 XSD 类型；其余必须引用已存在类）、facts 的 subject=个体/predicate=已存在属性/对象种类（objectProperty→个体 IRI，dataProperty→白名单字面量）、`rdf:type/rdfs:label/rdfs:comment` 在 facts 通道被拒（`entity_field_required`，唯一可编辑表示约束）、外部引用不得悬空。快照校验在服务边界显式调用（构造不自动校验，属设计而非遗漏）。
- `ontology/service.py`：`references()` 生成精确引用（含完整 statement 元组，不按主体/字段合并）；`deletion_impact()` 先 validate 再定位；`rdf_triples()` 编译类声明（owl/rdfs 保留原声明）、label/comment（语言字面量）、subClassOf/domain/range/type；`snapshot_digest()` 结构序不敏感、文本/列表序保留（保守守卫，实测标签重排触发 `stale_preview`，与代码注释声明一致）；`change_preview()` 命令重复/创建语义/种类变更拒绝、事实重复/矛盾/不存在拒绝、**先构造完整 candidate 再整体 validate**（删除被引用实体、悬空外部引用在终态校验被拒且影响清单完整）、before/after 全 RDF 集合 diff、changed_entities 含纯元数据变化、`require_current` 只做 (project,revision,digest) 守卫且自我声明非确认令牌。
- `ontology/source_projection.py`：`_validated_source` 用批准 `digest`+键集+`family()`+复用 `Store._snapshot_state`（classmethod，无实例、无 SQL）；`bind_rdf_projection` 要求编辑器编译 RDF 与源语句**集合相等**（漏项/同数量替换/虚构均拒），保留原 fact ID/owner/source_row/managed_value、墓碑（object=None 保留来源不成为语句）、同三元组多重支持（含 ontology-definition 原下标）、定义 payload digest 与定义间显式引用边；`removed_sources` 先 `require_current` 再检查 removed ⊆ known；`require_source` 拒绝换源。异常边界收敛为固定 reason，不透出解析器原文。

### 渲染端（3 文件）

- `view-model.ts`：`classTree` 循环/多父/闭环全覆盖且顺序确定（TS 测试精确断言期望序列）；`localGraph` 一跳边+limit 1..100+截断标志；`identity/isCurrentPreview` 项目+版本判定；`labelOf` 优先 zh。
- `OntologyPage.tsx`：纯 props 回调（`previewEdit`/`requestDeleteImpact`），无 Node/IPC/存储/自动确认；请求序号防迟到回复；草稿/事实双基准（draftBase/factBase），版本变化保留草稿并禁用预览、切项目按 key 重挂载隔离；删除影响绑定 (base,iri) 才启用删除预览；预览区恒标"尚未提交"、失败为固定文案不透异常；多行 textarea（含语言标签逐项、必填、16000 上限）；表格 20/页+搜索+页码钳制；一跳 SVG+完整列表+截断提示（12 条上限）。
- `ontology.css`：纯静态样式、响应式 850px 断点、无外联无脚本。

### 测试与 fixture（8 路径 + 3 Python 测试 + 1 TS 测试）

- `test_ontology_editor.py`（26 例）：结构与事实分离、真实 RDFLib 解析生成 RDF 全术语、多语言/多行/引号元数据保留、复制不复制断言、删除影响精确列表（外部/结构/断言三类）、批量删除、预览守卫、7 参数化非法事实、domain/range 非闭世界、循环保留、9 类命令错误原子性、注入术语拒绝、唯一编辑表示、精确语句影响。断言为完整预期集合/顺序，非计数。
- `test_ontology_fixed_inputs.py`（3 例）：先逐字节验 manifest/G-base/PRD 哈希再投影；G-base 10 定义+18 断言完整集合相等、空预览、推导三元组未预填；固定类编辑仅产生 label/comment 添加且 owl:Class 保留；行为引用阻止删除未实例化类。测试内投影明确自我声明非产品 parser。
- `test_ontology_source_projection.py`（13 例）：真实临时 SQLite Store.commit 造源；完整绑定零写入（`total_changes` 不变+state/vector/revision 不变+调用方改字典不影响绑定）；人工覆盖/墓碑保原 ID 与映射基线；漏项/同数量错误替换/虚构标签均拒；元数据（synonyms）不属 RDF 覆盖证明；重叠支持保双下标；身份 vs 完整性 vs 新源 vs 旧预览四类拒绝；5 参数化坏源固定诊断零写入；实体字段编辑定位原 asserted fact ID。
- `tests/unit/t02-ontology-views.test.ts`（3 例）：类树循环/多父精确序列+顺序不变性、一跳聚焦+截断+非法 limit、异项目/旧版本拒绝当前态。
- fixtures：5 个 Turtle 正反样本（合法基础/SHACL 模板/OWL 限制/SHACL 逆路径/语法错误）+ manifest 自我声明"未来 I05 集成输入，非当前产品验收"——**确认未被任何测试执行**（grep 全测试树无引用），与 acceptance.md"corpus 存在不等于导入通过"的表述一致，无冒充。t09-fixed-inputs manifest/G-base 原字节与固定 T09 提交 `873c8c05` 登记一致；G-base 实际内容（10 owl:Class/属性声明+18 断言，equipment/001 仅直接 type Equipment）与测试期望核对成立。

### UI harness 审查（5 文件）

`build.mjs`（vite 构建本目录）、`check.mjs`（headless Chromium；`page.route` 仅向 `t02-ui.invalid` 主机回放本地静态产物，含 `path.startsWith(root)` 防穿越；11 项状态探针覆盖多行载入/真实 Enter 与逐字输入/旧版本禁用/切项目隔离/迟到回复三种时序/失败不称成功/旧删除影响阻断/双尺寸无横向溢出；caret 仅用 evaluate 定位、按键真实）、`harness.tsx`（合成 callback+延迟/失败/换版本/换项目控制，明确"仅测试呈现"）、`fixture.json`（本线私有样本，n3 对象与引擎编译形式一致）、`index.html`（静态壳）。无 HTTP server、无端口、无外联、无 Electron/native。合成 callback 边界在文档、代码注释与 ui-probe.json 三处一致声明，未冒充 IPC/Store/e2e。

## 独立复现验证（本轮实际执行）

全部在本树独立依赖环境（`npm ci --ignore-scripts` 90 包 0 漏洞、`uv sync --frozen` rdflib 7.6.0，锁原字节未动）内执行，完整原始流与哈希见 `test-results/t02-s1-r1/streams/`（清单 streams-inventory.txt）：

| 命令 | 结果 | exit |
| --- | --- | --- |
| 68 项输入三方哈希核对（脚本） | 68/68 OK | 0 |
| `uv run --frozen pytest packages/engine/tests/test_ontology_{editor,fixed_inputs,source_projection}.py -q` | **39 passed**（1.19s） | 0 |
| `npx vitest run tests/unit/t02-ontology-views.test.ts` | **3 passed** | 0 |
| 边界/反例探针（内存内，见下） | 全部按预期 | 0 |
| `npm run check`（eslint/prettier/tsc/vitest/build/ruff/pytest） | **633 vitest + 1091 pytest 全过**，"All checks passed!" | 0 |
| 终态 68 项哈希复核 | 0 漂移 | 0 |

专项 39+3 与完整 check 633/1091 均与 `verification-c3.json` 固定记录同数——同版独立复现成立。

**边界/反例探针**（streams/050，独立新增、超出既有测试）：n3 规范形式往返（typed/lang/多行/引号/反斜杠）；手写非规范形式（含我最初误写的 `"""quo"te"""`）被 `invalid_rdf_term` 正确拒绝——规范形式应为 `"quo\"te"`，这是规范化检查按设计工作；服务路径对含引号/反斜杠/三引号标签编译正常；大写语言标签被拒（小写规范化）；class_type=None 编译为 rdfs:Class、Copy 保留 owl；无 types 个体不产生 RDF 但计入元数据变化；重加已有事实幂等空 diff；同语言多标签合法（RDF 合法）；最小真实 Store+完整公理集绑定成立；`removed_sources` ⊆ 预览移除集；源含悬空定义引用→`invalid_source_snapshot`；字段适用性负例（individual 带 parents、属性带 types、dataProperty range 非法类型、objectProperty range 未知 IRI→`class_reference_required`）；重复 parents→`duplicate_value`；标签重排→`stale_preview`。

**沿用的原运行证据（未复跑，按政策引用）**：C2 的 11 项 headless 呈现探针（UI 源未变；且复跑会写保护路径 `ui-probe.json`/PNG，故仅静态审查+证据读回）；`npm run verify:sources` 12 归档源（本轮未触碰任何 source 资料，无变化不重跑）；全部 32+9 份原始日志（tar 封存实测一致）。

## 历史意见逐项独立依据

| 编号 | 我的独立核对（非仅凭"已关闭"字样） |
| --- | --- |
| H01 旧草稿套新版本 | 读 OntologyPage draftBase/factBase/key 重挂载实现与 check.mjs 5 项时序探针；require_current (project,revision,digest) 三重守卫 |
| H02 多语言丢失 | labels/definitions 全语言 tuple 在 model/service/UI 三层保留；editor 测试断言未编辑语言原样进入意图 |
| H03 types 与 facts 双表示 | model.py:172-173 拒绝 facts 通道三谓词；source_projection 测试证明实体字段编辑定位原 asserted 记录 |
| H04 label/comment 绕白名单 | Triple 构造前置规范形式检查；`unsupported_datatype`/`invalid_literal` 负例；我的探针复证 |
| H05 C1 多行丢失（P2） | textarea + rows + maxLength；check.mjs 真实 Enter/逐字输入；editor 测试 `"""第一行\n第二行"""@zh` 三引号形式断言 |
| H06 delivery 指针 | delivery.md 当前已指 C3 `4932122` 并保留 C2 历史段——P3 已实际关闭 |
| H07 证据本地不受控 | tar 48 成员/548417B/SHA 实测一致；git-readback.json 在档；旧 C1 两图仅有哈希、未重造（本树亦不存在，如实记录） |
| H08 方案两 P2 | disposition.md 自我声明仅方案层；S1 产品代码无 commit/metadata/meter 实现——确认无冒充 |

## 新发现（按 P0–P3）

**无 P0、无 P1、无 P2。** 以下 P3 均为观察/未来接线注意，不阻断 S1：

1. **P3 语言标签仅小写子集**（`model.py:132-134`、`rdf_snapshot.py:47`、`OntologyPage.tsx:580` 三处一致）：`en-GB` 等大写/混合大小写合法 RDF 语言标签在私有模型被拒（term() 归一化为小写导致非规范形式）。这是有意的私有收窄且 UI/服务一致，但未来 I05/T01 导入 adapter 必须先归一化语言标签，否则合法基础 RDF 会被拒。已在 interface-handoff"最终导入投影需同 I05/T01 验证"边界内，登记供接线时处理。
2. **P3 class_type=None 默认编译为 rdfs:Class 无直接测试断言**（`service.py:76-86` 行为存在，我已探针确认；UI 表单恒显式选 rdfs/owl，fixed-inputs 显式 owl）：建议后续补一行直接断言，避免依赖隐式覆盖。
3. **P3 重加已有事实为幂等空 Diff**（`service.py:194-197`）：不报错、added/removed 为空。RDF 集合语义下可辩护；若未来希望向用户区分"已存在"与"无变化"，属 owning 服务呈现职责。
4. **P3 `update('classType', …)` 接受任意 string 落入 draft**（`OntologyPage.tsx:389`，仅 select 两个选项可触发；服务侧 `invalid_class_type` 兜底）：类型收紧属未来接线清理项。
5. **P3 事实 object 输入无前置格式校验**（`OntologyPage.tsx:480-511`）：依赖 previewEdit 拒绝+固定文案。S1 内服务校验权威、可接受；正式接线时可加轻量提示。

另记两条**非缺陷观察**：`snapshot_digest` 对标签顺序敏感（守卫更保守，代码注释已声明设计意图）；`references()` 中 fact.subject 的 Reference source 即目标自身（statement 元组已消除歧义，纯呈现细节）。

## 架构不变量核对

本地优先（无模型/遥测/云/HTTP 端口——ontology 模块与 UI 全文核对）✓；渲染端隔离（纯 props、无 Node/IPC）✓；CSP 未触碰 ✓；确定性与 Agent 解耦（无确认入口、require_* 自我声明为守卫）✓；存储（生产模块不实例化 Store、不执行 SQL；正式写入只可能经未来 owning Store.commit）✓；数据层次/失效规则未触碰 ✓；模型外发零 ✓；错误边界固定 reason ✓。

## 未验边界（如实，不得记为通过）

Electron/e2e/native/HMR/打包内运行/双平台安装/生产（原候选亦未执行）；正式 IPC/bridge/App 路由、T01 可信投影/人类确认/Store.commit/undo、I05 Turtle 支持检查与无损往返（corpus 未执行）、T08 真实草稿、FR-200–204 跨模块/附录 C 完整交换/12.1/12.4/双平台/真人/CI/远端/上线——全部仍为父缺口，S1 通过不关闭上述任何门。本轮 UI headless 探针未复跑（理由见上）。

## 终态

- 实际执行的全部命令 exit 0；首失败保全：本轮无失败运行（探针脚本两次修正为我方脚本错误——非规范 n3 输入与误传 7 键记录/错实体索引——均在 streams/050 完整保留，产品代码行为全部符合预期）。
- 冻结输入前后哈希一致（streams/010 vs 070），无受审路径改动，无 stage/commit/push。
- 本报告为唯一持久写入（docs/reviews/T02/round-1/zcode-glm53.md）；原始流在 test-results/t02-s1-r1/（git 忽略目录）。

## 最终结论

**通过**（限 T02-S1 有界范围：私有不可变本体编辑模型+精确 RDF/元数据 Diff/删除影响、批准 Store2 只读 RDF 来源绑定与来源保留证明、独立 React 页面与纯 view-model、39+3 专属测试、固定 T09 输入回归、五文件 headless harness；范围即 stage-registration-request.md 登记口径）。理由：19+5 路径与全部证据完整审查无阻断缺陷；同版独立复现 39 Python+3 TS+全仓 check 633/1091 全过；历史 H01–H08 逐项有真实依据；边界声明与实现一致、无一处把阶段拼接/替身/方案冒充产品能力；5 项 P3 均为未来接线注意项。父功能门与发布门全部保留待验；本结论不授权 push/PR/CI/merge，需同候选另一方（MiniMax M3.1-Flash/xhigh）独立明确通过及全部原门禁满足。
