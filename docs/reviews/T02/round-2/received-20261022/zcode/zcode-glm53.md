# T02-S1 round-2 C5 ZCode GLM-5.3 独立完整审查报告

- 审查者：本轮全新独立指定审查者（ZCode 桌面会话，由 owner 于 2026-10-22 创建并交付完整冻结正文；无独立可读数字 taskID，不伪造）。
- 平台：macOS darwin 27.0.0 arm64（本机），审查全程在独立 worktree 内执行。
- 模型/设置读回：运行环境标识 `account:bigmodel-individual-coding-plan/GLM-5.3`（会话系统环境，非由文件名或报告标题推断）；思考等级最高为 owner 会话配置，无独立接口可在会话内部二次读回，按指定值声明；权限完全访问为行为读回——本轮全部工具调用（Bash、后台任务、test-results 写入）未触发任何逐命令批准。完全访问不改变只读审查职责：本轮未修改任何实现/测试/fixture/依赖锁/配置/验收，未 stage/commit/push/checkout/切分支。
- 最终任务状态：真实完成（见"终态"节）；无认证/额度/服务错误，无需恢复操作。

## 1. 固定身份与输入完整性（实际核验）

| 项 | 值 | 核验 |
| --- | --- | --- |
| 本审查工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-c5-zcode-review-e5ad54e`，detached HEAD `7c52e33e92d76bb0a83938a0e50abc40b8fb234e` | `git rev-parse` 实测 |
| product | `e5ad54e5762157cafe532c2a0c07c22e8dd737cb`（C5 当前候选） | commit 存在；20 产品/测试/fixture 路径逐字节=该 ref=清单=工作树 |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | commit 存在；10 项不变基线引用 hash 一致 |
| 证据过程 ref | `516ba27cb824fd89f5a21609776af3844c5430aa` | commit 存在；100 项过程证据按该 ref 核验 |
| 历史 | 旧受审 49321221（R1）、35aa93fc（C4 内部 Fail） | 仅作历史证据归属，未冒充当前 |
| input-manifest | **120 delta**（20 产品/测试/fixture @e5ad54e5 + 5 harness + 85 过程证据 + 10 纯方案）+ **10 基线引用** | 脚本逐项 `git show <ref>:<path>` 重算 bytes+sha256：**120/120 + 10/10 全部一致**（raw/input-verify-1.log） |
| preparation-manifest | 18 项 R2 包 payload 固定 @7c52 | **18/18 字节/hash 一致**（含两 tar 包、disposition-c4/c5、independent-c4/c5、AGENTS-current、三份 current 政策） |
| 分支 delta 完整性 | `git diff --name-only base..516` 恰为 120 项清单路径，无多无少 | 实测 |
| 台账已知差异 | `review-backlog-20261022.md` 在 7c52 追加 C4/C5 两段（9757B/3fa52384… → 11467B/19c0e829…），与启动补充声明一致；**其余 129 项工作树与固定 ref 全等，实测仅此一项差异** | 属已声明过程台账追加，非源码漂移 |
| 本树 AGENTS.md | sha256 `de15f6ce…a5c8c4`（未暂存），与 `AGENTS-current.txt` 逐字节一致 | 当前政策授权的携带方式 |
| 环境独立 | 本树自有 node_modules/.venv（owner 按原锁 `npm ci --ignore-scripts` + `uv sync --frozen` 准备，回执在 metadata/setup-receipt.json，exit 均 0；setup 非产品验证）；未借其他树环境；两锁文件字节未动 | 实测 |

未读取、未写入另一方（MiniMax）本轮任何输入/报告/意见（`minimax-m31flash-input.md` 及 launch 包内 minimax 文件仅见文件名，从未打开）；未触碰 T06 或其他任务/会话/stdio；未做被拒 SQLite 物理研究；未占用 native 票/HMR/交互桌面验收。

## 2. 范围与覆盖（完整，未截断为修复 delta）

1. **25 个产品/测试/harness 路径逐文件全文审查**：引擎 4 源文件（`ontology/{__init__,model,service,source_projection}.py`）、渲染 3 文件（`OntologyPage.tsx`/`view-model.ts`/`ontology.css`）、4 Python 测试（含 C5 新增 `test_ontology_input_boundaries.py` 339 行）、1 TS 单测、5 个 ui-probe harness 文件、9 个 fixture。并通读 base→产品完整差异（纯新增 4555 行、0 删除）与 C4→C5 精确 diff（仅 `model.py` 36 行 + 边界测试 +86 行，其余为过程证据）。
2. **产品提交链梳理**：C1=438c6ade→C2=5ef86a1d→C3=49321221（R1 受审）→UI 修复 a07c5634→C4=35aa93fc（内审 Fail）→C5=e5ad54e5（当前）；各固定 ref 均解析核验。
3. **需求依据**：PRD V0.6 FR-200–204、FR-804、附录 C 能力矩阵、附录 D（本体变化失效行）、附录 F、12.1/12.4 原文对照；T02 迭代五文档（acceptance/source-projection/stage-registration-request/interface-handoff/delivery）全文。
4. **历史证据链**：R1 双方正式报告全文（ZCode 19506B/af43f9ab…、MiniMax 36714B/51e3b498…，均按固定 ref 读取）+ triage-initial；C4/C5 disposition 与独立内审（含 C4 Fail 原件、C5 通过件）、c4/c5-evidence-manifest 与 tar 成员清单（C4 84 成员/C5 4 流，hash 已核未解包重跑）；C1/C2/C3 内审与三份 verification JSON；history-disposition-index、original-log-index、scope-and-evidence、evidence-archive 清单结构、status.md 全文、台账 516 版+7c52 追加段、ui-fix-handoff、prompt-manifest（原 R1 提示在各 R2 正文中恰一次出现，hash 一致）。
5. **10 项纯方案文档**按 context-only 角色确认其"仅方案层、未实施"自我声明与实际代码一致，无冒充。

## 3. 独立复现验证（本轮实际新跑；与沿用/未执行分列）

全部在本树独立环境执行，完整 stdout/stderr/真实 exit 见 `test-results/t02-c5-r2-review/raw/`，元数据（每条命令、cwd、exit、日志 hash）见 `metadata/runs.json`：

| 命令 | 结果 | exit |
| --- | --- | --- |
| 130 输入 + 18 payload 清单核验脚本（git 对象逐项 bytes+sha256） | 120/120、10/10、4/4、18/18 全过 | 0 |
| `uv run --frozen pytest` 本线 4 个 ontology 测试文件 -v | **112 passed**（1.07s） | 0 |
| `npm run check`（eslint/prettier/tsc/vitest/build/ruff/pytest 全 suite，含已批准 I04 回归与受控 worker 子进程） | **634 vitest（16 files）+ 1164 pytest，"All checks passed!"**；其中 t02-ontology-views 4 例在内 | 0 |
| 独立 Unicode 反例探针（第 4 次尝试，前 3 次为我方 harness 缺陷，首失败全部原样保留） | **33 项 ALL-EXPECTED**（详见下节） | 0 |
| 21 项 headless UI 探针（`T02_UI_OUTPUT_DIR` 指向本方 `test-results/t02-c5-r2-review/ui`；核可执行存在后用 chrome-headless-shell 1234） | **21/21 evidence 全过**；输出仅写本方目录，未覆盖历史 JSON/截图 | 0 |

关键数字与 owner 声明一致：本线 112、634TS/1164Py、21 headless 均为本方亲跑，非沿用。

**独立 Unicode 反例探针**（自建，区别于 31 项既有套件用例；使用 `\uDB80/\uDBFF/\uDC00` 等套件未用码位，全部经 `json.loads(json.dumps(...))` 产生普通 JSON 解码字符串）：
- C4 曾逃逸的七类路径——project、synonyms、examples、实体 IRI、labels、definitions、external source——全部得到固定 reason/location（`invalid_text`+字段 / `invalid_iri` / `invalid_external_reference`），无任何原生异常；
- Put/Copy 命令路径（edit synonyms、create 新 IRI、copy 目标 IRI、copy identifier）同样固定诊断（后者 `invalid_identifier`，经候选终态校验兜底，仍为固定码）；
- Triple 三术语与 add_facts 对象字面量含 surrogate → `invalid_rdf_term`；deletion 目标含 surrogate → `not_found`；
- 拒绝后输入对象逐字段不变、服务随后对合法输入仍正常出空 Diff；
- 合法 Unicode（U+1D306、🚀、组合重音 e+U+0301、ZWJ 家庭+公文包序列、ZWSP、CJK 扩 B U+20000、中文项目名/IRI）在 label/comment RDF 编译中**逐字保留，无归一化/替换**；
- 诊断文本不含任何输入值片段。
- 一条**内部边界观察**：`service.snapshot_digest` 直接喂未校验快照仍会抛原生 `UnicodeEncodeError`——该函数不在 `__init__.__all__` 导出面内，所有导出入口（change_preview/deletion_impact/rdf_triples/require_current/bind_rdf_projection）都先 validate，当前无任何外部边界可达；属未来 adapter 接线注意事项，不计 P 级缺陷。

**首失败保全**：探针 1–3 次失败均为我方 harness 缺陷（字符串字面量内真实换行；fixture 辅助函数 project/entities 关键字与位置参数冲突；dataProperty domain fixture 误用个体），完整原始流+exit 保留于 raw/probe-unicode-{1,2,3}.log，第 4 次修复后全过；产品代码在三轮失败中行为全部符合预期，未据我方脚本错误得出任何产品结论，亦未修改任何文件掩盖失败。

**沿用未重跑（按政策引用，不计为本方新验证）**：C4 84 成员原始证据 tar 与 C5 4 流 tar（含 `unicode-c4-first-failure.log` 首失败）——hash 在 18 项 payload 核验中字节验证，未解包重跑；R1 双方报告/三份 verification JSON/48 成员历史归档 tar——按固定 ref 读取并 hash 核验。

**明确未执行（不得记为通过）**：Electron/e2e/native/HMR/打包产物运行/双平台安装/生产；正式 IPC/bridge/App 路由、T01 人类确认/Store.commit/undo；I05 Turtle 导入/SHACL 支持检查/无损往返（corpus 按 fixture manifest 自我声明为未来 I05 输入，确认无任何测试执行它，无冒充）；T08 真实草稿；CI/push/PR/merge/远端；被拒 SQLite 物理研究、native 票、交互桌面验收。

## 4. C4 残留 P2 与 11 项 R1 意见逐项独立复审（不采信"已关闭"字样）

| 编号 | 我的独立依据（代码+本轮亲跑） | 我的结论 |
| --- | --- | --- |
| C4 残留 P2（surrogate 逃 UnicodeEncodeError） | `model.py` C5 diff 精确审读：`_is_utf8` 前门落于 project(:117)、实体 IRI(:138)、Triple 三术语(:46-49)、labels/definitions(:164)、synonyms/examples(:175)、external source(:228)，全部先于 `iri()/term()/digest/排序`；我的探针以**不同码位**独立复现七类路径+Put/Copy+Triple+fact 对象全部固定诊断，合法 Unicode 原样保留，无替换/归一化/digest 编码变化 | **关闭**（限本轮已发现类别；"任意 Python 对象/无限输入空间"不在保证范围，与文档声明一致） |
| M-P2-1（六类畸形元素类型逃逸） | `model.py:127-132` 元素类型检查先于集合哈希/解引用（含注释明示）；`service.py:152-176` validate→元组检查→Fact 元素+`fact.triple()` 先于建集合→Put.entity/精确 bool/Copy.source/目标 str 先于查表；未配对 surrogate 由 `_unique_tuple` 的 TypeError 兜底成 `invalid_value`（无不可哈希逃逸路径，我逐路推演+套件 14 参数化+探针复核）；六类原始反例在套件 `test_six_reported_malformed_inputs...` 逐项断言 reason/location/输入不变 | **关闭** |
| M-P3-1（批量删除影响=基准快照引用） | `service.py:200` 以基准 `snapshot` 计算 impact；UI 两处（详情面板与预览区）均标注"基准快照（项目版本 N）中的引用；包括本次修改计划将解除的引用"；套件断言同批 Delete+三处解除后**全部三个基准引用+六个实际 RDF 删除项**完整保留，且 `validate(candidate)` 兜底使下漏不可能（悬空必拒）。我的判断：该语义准确表达"此删除将解除什么"，保守方向、明确标注，非缺陷；R1 报告"成功提交"实为成功生成 Preview，本服务无 commit | **接受处置**（语义正确、已标注；不改为候选空集合是对的） |
| M-P3-2（copy 死变体） | `EditIntent` 现仅 create/edit/delete/assert/retract（OntologyPage:22-25），copy 变体已删；"复制定义到新表单"以完整 chosen 对象填充草稿（iri/identifier 置空），用户编辑后发完整 create；我亲跑 21 项探针中 `copy_all_metadata_families_edit_then_create_complete_definition` 对四类对象全字段复制+修改后精确完整意图断言通过；FR-200 原文只要求"复制"操作，未要求持久谱系；服务 `Copy` 保留完整可编辑模板复制、不克隆实例断言（套件 Z-P3-2 用例） | **接受处置**（模板复制+create 语义充分；不虚称谱系） |
| M-P3-3（分页/复制/事实表单 UI 无自动化验证） | check.mjs 现 21 项，含 25 对象前后翻页完整有序集合/页边界/返回、搜索重置与空集、四类复制、新建清空、assert/retract 精确事实与基准、版本推进阻断直至显式重读、切项目清空并重绑、坏 n3 固定文案（assert/retract 双路）、删除影响基准语义；**我本轮独立重跑 21/21 通过**；仍为合成 callback，ui-probe.json mode 字段如实声明"no IPC/Store/product integration"，未冒充 | **关闭**（合成呈现层；正式集成边界保持） |
| M-P3-4（classTree O(n²) 无条件计算） | `view-model.ts:36-44` 一次性建 parent→children 索引；`OntologyPage.tsx:104` `useMemo` 且仅在 tree tab 计算；排序根/缺失父/共享后代/自环/重复父语义由 4 条 TS 单测锁定（含输入逆序不变性）；全程无容量/O(n) 承诺。残留同族小项见新发现 P3-1 | **接受处置**（最小修复；无批准容量阈值，不作量化承诺是对的） |
| M-P3-5（16 个 reason 未断言） | 逐个核对：16/16（contradictory/duplicate_fact_command、duplicate_iri/value、invalid_class_type/external_reference/identifier/iri/language/literal/text/value、project_required、projection_origin_missing、unsupported_command/kind）均有具体业务负例断言 reason（多数含 location）+输入不变/零写入；为真实输入反例而非 AST 镜像，也不声称穷尽输入空间 | **关闭** |
| Z-P3-1（小写语言子集） | 三处一致（model 正则、rdf_snapshot `term()` 小写归一化导致非规范形式拒绝、UI pattern）；`en-GB` 拒绝已有固定负例；interface-handoff 已登记为正式 I05/T01 adapter 归一化前置。我的独立判断：**不影响 S1 验收**——S1 是私有编辑模型，子集自洽且一致执行；FR-203 完整导入本就是父门，不能借"处置"把它变成已支持 | **维持延期**（接线前置，登记在案） |
| Z-P3-2（None 默认 rdfs/Copy 断言） | `test_unspecified_class_declaration_and_copy_remain_rdfs_without_assertion_cloning`（boundaries:230-238）直接断言 None→`<rdfs:Class>` 单三元组、Copy added 仅类型三元组、无断言克隆；本轮 112 例亲跑含此例 | **关闭** |
| Z-P3-3（重加事实幂等） | 套件断言精确空 Diff（added/removed/entity_changes/changed_entities 全空、候选事实与完整 RDF 不变）；RDF 集合语义下幂等可辩护，PRD 无"已存在需报错"要求；未来"已存在"提示属呈现选择 | **接受现有语义**（关闭；呈现提示留待 owning 服务） |
| Z-P3-4（update 泛型/classType 守卫） | `update<K extends keyof ObjectRow>(key: K, value: ObjectRow[K])`（:106）；classType select onChange 仅接受 'rdfs'/'owl'（:392-394）；kind 切换清空 parents/domain/range/types/classType（:369-376）且编辑态禁改 kind（:366，对应服务 `kind_change_requires_new_entity`）；服务 `invalid_class_type` 权威兜底 | **关闭** |
| Z-P3-5（n3 提示/固定拒绝文案） | 事实表单规范 n3 示例+「预览服务检查格式和语义」（:483-486）；我亲跑探针 `bad_n3_input_synthetic_service_rejection_fixed_message...`：assert/retract 双路固定文案+无成功预览；renderer 未造第二 parser；完整前置 parser 按批准合同延期 | **部分接受（现状充分）**：S1 内服务校验权威正确；正式入口提示依未来 adapter 合同，不算导入能力 |

## 5. 新发现（按 P0–P3；本轮全部新跑+全文审读基础上）

**无 P0、无 P1、无 P2。**

1. **P3　`localGraph` 未记忆化且不随页签门控，每次渲染无条件计算**（M-P3-4 同族残留，非其回归）
   - 位置：`apps/desktop/src/renderer/src/ontology/OntologyPage.tsx:105`（`const graph = localGraph(view, selected, 12)`）；对照 `:104` 的 tree 已 `useMemo`+tab 门控。
   - 触发：任意表单按键/状态变化触发 Editor 重渲染时，即使当前不在"局部关系图"页签，也会对全部 triples 执行一次过滤+全排序（O(n log n)）。
   - 影响：S1 规模（fixture 46 条）不可测地轻微；与 M-P3-4 修复方向不一致，属呈现层一致性小项。无批准容量阈值，本报告不据此宣称任何性能/容量结论。
   - 建议：与 tree 同样 `useMemo` 且以 `tab === 'graph'` 门控；接线期随手处理即可，不阻断 S1。
   - 与原验收关联：FR-202 功能行为正确（本轮 21 项探针亲验含截断与完整边集合），此项纯为渲染成本一致性。

另记两条**非缺陷观察**（不计 P 级）：其一，`service.snapshot_digest` 对未校验快照抛原生 `UnicodeEncodeError`，但不在 `__all__` 导出面、所有导出入口先 validate、当前无外部边界可达——未来 T01/T00 adapter 若直接复用该内部函数须先 validate（探针 INTERNAL-NOTE 项）；其二，C4→C5 的 8 个 UI/harness 输入与 35aa 逐字节相同（我逐文件 hash 复核），21 项 headless 证据"沿用+本轮亲跑双重成立"的声明准确。

## 6. 架构不变量核对（全文审读+本轮运行）

本地优先：无模型/遥测/云/HTTP 端口（ontology 模块、UI、harness 全文；探针 route.fulfill 不启服务）✓；渲染端隔离：纯 props 回调、无 Node/fs/通用 IPC/自动确认 ✓；CSP 未触碰（csp.ts 不在 delta）✓；确定性与 Agent 解耦：仅 Preview/守卫，`require_current/require_source` 自我声明非确认令牌，无确认入口 ✓；存储：生产模块不实例化 Store、不执行 SQL，测试内临时库经真实 commit 造源、读取零写入（套件 `total_changes` 断言）✓；数据层次/失效规则未触碰 ✓；模型外发零 ✓；错误边界：跨边界固定 reason/location、`str(e)==reason`、无解析器原文/堆栈/输入值（探针亲验）✓。

## 7. 终态

- 实际执行命令全部 exit 0（含全 suite check）；首失败 3 次均为我方探针 harness 缺陷，原样保全于 raw/，未覆盖、未修改产品掩盖。
- 前后源码快照：26 文件（25 受审路径+AGENTS）hash 前后**零漂移**（metadata/source-hash-before.json vs source-hash-after.json）；工作树 git status 与启动时一致（仅 M AGENTS.md 政策传播 + 2 项 owner 下发未跟踪项 + 本方 test-results/报告）；无 stage/commit/push。
- 本报告为本方唯一持久写入（`docs/reviews/T02/round-2/zcode-glm53.md`）；原始流与元数据在 `test-results/t02-c5-r2-review/`（git 忽略目录）。历史截图/日志零覆盖。
- 未读取对方本轮任何输出；本报告仅为 ZCode GLM-5.3 一方结论，不推断 MiniMax M3.1-Flash 一方。

## 8. 最终结论

**通过**（严格限 T02-S1 有界范围：私有不可变本体编辑模型+精确 RDF/元数据 Diff/基准删除影响、批准 Store2 只读 RDF 来源绑定与来源保留证明、独立 React 页面与纯 view-model、112 条本线 Python+4 条 TS 专属测试、固定 T09 输入回归、五文件 headless harness；范围即 stage-registration-request.md 登记口径）。

理由：25 路径与全部 130 项输入/18 项 payload 逐字节核验一致；同版独立复现 112 本线 Python、全仓 check 634 TS/1164 Py、21 项 headless 探针、33 项自建 Unicode 反例全部通过且首失败如实保全；C4 残留 P2 经不同码位独立反例确认关闭；11 项 R1 意见逐项以代码与亲跑证据独立复核——1 项关闭、9 项接受处置/关闭、Z-P3-1 维持正式 adapter 前延期（不影响 S1 验收）；唯一新发现为 1 项 P3 呈现层一致性小项；边界声明与实现完全一致，无一处把阶段拼接、合成 callback、方案或 corpus 冒充产品能力。

**本通过不关闭任何父门**：T01 可信投影/人类确认/唯一原子 commit/receipt/undo、I05 Turtle/SHACL 支持检查与无损往返、I06 正式 App/桥与壳生命周期、T08 真实草稿、FR-200–204 完整跨模块验收、附录 C/F/G 与 12.1/12.4、双目标平台/真人、指定双审双方一致、CI/正常 merge/远端/上线全部仍待；本结论不授权 push/PR/CI/merge，需同候选另一方（MiniMax M3.1-Flash/xhigh）独立明确通过及全部原门禁满足。
