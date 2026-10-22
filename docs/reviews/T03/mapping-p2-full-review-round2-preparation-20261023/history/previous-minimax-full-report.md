# Mapping P2 全新完整独立静态审查报告（minimax / M3.1-Flash）

- 报告路径：`build/review-session/reports/mapping-P2-minimax-full-report.md`
- 元数据：`build/review-session/metadata/task-actual.json`
- 逐路径覆盖台账：`build/review-session/raw/path-coverage-register.json`（1028 项）
- 本轮性质：全新指定外审（不继承旧 303 任务结论，不继承任何旧 Pass）

---

## 1. 结论（先行，分范围）

| 范围 | 判定 | 依据摘要 |
| --- | --- | --- |
| **本轮新审：静态审读 + 既存原件复核** | **通过（限本次可完成范围）** | 固定 HEAD 全部关键工程路径已读；P2 增量两文件逐行读完；17 项固定包证据、74 份原字节副本、14 条命令收据、首次失败原件全部逐字节复核；范围内**未发现 P1/P2/P3 级新缺陷** |
| **P2 增量本身**（`mapping/probe.py` + `tests/test_mapping_entrypoint.py`） | **通过** | 两文件全文审读；旧 11 项保留、新增 6 项的语义与 oracle 双向匹配；caps/入口/依赖/锁未变；socket guard 的累计语义与恢复路径成立 |
| **固定 17 项证据链** | **通过** | 本树 `actual-source-stdout.log` 与 `actual-package-stdout.log` **字节相同**，且与执行前写定的 `fixed-probe-v2-expected.json` **深度相等**；`-O` 单独一次执行 stdout 字节相同；3 类拒参 exit 2 / stdout 0 / 固定 32B stderr |
| **整体候选 / 发布门** | **不通过（未通过）** | 父业务正式接线、双 OS、GUI/e2e、签名安装、父 57 P0、CI/远端、生产均**未验证**；另有 1028 项中 964 项仅 metadata 级覆盖（见 §5），**未达成"完整全文覆盖"**；历史 Z2 的"P3 维持"与"无 P3 遗留"内部矛盾、Z1 残余说法、F09 统计错误仍需原报告侧纠正 |
| **本报告的效力** | **不构成指定双审通过** | 另一指定模型本轮尚未终态；本地 Codex 独审、setup 通过、旧候选双审均不是本候选的指定 Pass |

结论口径：本轮**不因"无 P1/P2/P3"或"17 项成功"给出整体通过**；整体明确记为不通过，并把不通过项分为「范围外未验门」与「本轮未达成覆盖」两类，不以局部通过掩盖。

---

## 2. 任务身份与实际设置来源

来源仅为本方同目录 `build/review-session/metadata/operator-own-ui-pre-submit.json`（1140 B，SHA-256 `649300a9d3f987146c094f2cf14cd993a5496c840ce1527634c5979ff930ef9b`，已逐字节核对一致）。**未**读取 agent list / session get / 全局配置 / 数据库 / 同侪方任何材料。

| 项 | 实际值 | 来源与限制 |
| --- | --- | --- |
| 角色 | minimax | operator 文件 `role` |
| 项目 UI | `T03-mapping-P2-minimax-review-da1795` | operator 文件 `projectUI` |
| 模型 UI 显示 | `M3.1-Flash（订阅限免）` | operator 文件 `modelUI`（UI 显示值） |
| 思考 UI 显示 | `xhigh` | operator 文件 `thinkingUI` |
| 权限 UI 显示 | `始终授权`（请求码 `bypassPermissions`） | operator 文件 `permissionUI` / `requestedPermissionCode` |
| 后端实际模型/思考/权限标量 | **UNKNOWN** | operator 文件三项均记 UNKNOWN；本方不据配置推断实际后端值 |
| owner 侧 task/session/turn ID | **UNKNOWN** | operator 文件三项均记 UNKNOWN；实际 ID 须由 owner 从其菜单复制补录 |
| 本方运行时会话标识 | `mvs_b159af436fec43caa2b7272568bfc248`（agent 上下文所载） | 非 owner UI 读回，仅作本方会话索引 |
| turn ID | **UNKNOWN** | 本方不可观测 |
| 提交时 composer 状态 | `accepted: false`、`composer: "empty before attachment"` | operator 文件；即本轮输入为附件投递，owner 侧尚未记录接受回执 |
| 派发输入身份 | 44876 B，SHA-256 `48839f37ed03a220ea1f82cf97e67528a4a82fd7f0ee769be47b213e55288662` | operator 文件 + 本树 `metadata/dispatch-prompt.md` 逐字节一致 |

本轮实际动作边界：**仅静态审读与既存原件复核**。未运行产品命令、未安装、未打包、未启动 Electron/e2e、未新建 Goal、未付费、未读密钥、未获取 CUA、未创建其他任务。

---

## 3. 现场与版本核验（先核验后审读）

| 项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| 工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-P2-minimax-review-da1795` | 同一路径 | 一致 |
| HEAD（detached） | `c1e44f81723f9c616f669f56481d1b1ada7e57f2` | `c1e44f81…` | 一致 |
| 产品候选 | `da1795b20c3c0d47ae975fe3371e802092a4b429` | 存在；`30319412→da1795b2` 仅 2 个产品文件改动 + docs 证据 | 一致 |
| 工程/既存证据来源 | `4ec492f07d261164283a939c65b5e835c30e561e` | 存在（`4ec492f0`） | 一致 |
| 批准 base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 存在 | 一致 |
| 两文件修复 base | `30319412daf8ae4745987babf7bbed93c53b6b42` | 存在 | 一致 |
| `da1795b2 → c1e44f81` | 仅追加 docs | 153 个文件，**全部在 `docs/` 下，非 docs 差异 0** | 一致 |
| AGENTS 保护覆盖 | 15147 B / `de15f6ce…` / unstaged | 15147 B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，`git status` 仅 ` M AGENTS.md`（Git 树内 AGENTS blob 为 `f3876f66…`，非覆盖实际值） | 一致 |
| 完整候选树索引 | 1028 项，SHA `a8afd3637dcc7fb613c95bd3009d20294e815a96b2043ed108a67afdef673eb4` | 273638 B，SHA 一致，`completeTrackedCount=1028` | 一致 |
| 派发提示原文 | 44876 B / `48839f37…` | 一致（附件与树内文件逐字节相同） | 一致 |
| operator 设置源 | 1140 B / `649300a9…` | 一致 | 一致 |

未执行任何 checkout/reset/fetch/cherry-pick，未改任何工程文件，未提交/推送/PR/切分支。

---

## 4. 输入读取与哈希核验

**派发提示**：按要求用官方文件读取工具分段读完附件至 EOF（243 行，两次读取；第二段自 offset 111 接续至末行，输出标注 `original_bytes=47063` 且结尾无截断标记）。随后核对树内 `metadata/dispatch-prompt.md` 与附件同 SHA。

**本次新审实际读入并核验的原件**：

| 原件 | 核验方式 | 结果 |
| --- | --- | --- |
| `docs/reviews/T03/mapping-p2-boundaries-20261023/` 全 9 件 + 其余原件 | 全文读 `delivery.md`、`actual-receipt.json`(28825 B/50 字段级)、`candidate-binding.json`、`fixed-probe-v2-expected.json`、`oracle-before-run.json`、`verify-packaged-boundaries.py`(280 行)；结构化解析 `command-records.json`(14 条)、`raw-evidence-manifest.json`(74 项)、`actual-engine-inventory.json`(440 项) | 全部一致 |
| `p2-original-raw/` 74 份原字节副本 | 按 `raw-evidence-manifest.json` 逐项重算 size+SHA-256 | **74/74 一致，0 缺失 0 不符**；`raw-relocations.json` 74 条哈希同样全一致，`originalManifestUnchanged: true` |
| docs 副本 ↔ raw 原件 | `actual-receipt.json`、`source/package stdout`、3 份拒参 stderr、engine inventory 逐字节比对 | 全部**字节相同** |
| `candidate-binding.json` 11 项 sourceIdentities | 与当前 HEAD 工作区逐文件重算 SHA-256 | **11/11 一致**（含 probe.py `219d6581…`、test_mapping_entrypoint.py `30d2abe6…`、source.py `93bf09e1…`、plan.py `cea9ca32…`、entrypoint.py `7653ddf2…`、uv.lock `9f5b6d2b…`、package-lock.json `a462ba70…`、pyproject.toml `55674b4f…`、build-engine.mjs `c53d704b…`、electron-builder.yml `95b993d5…`、AGENTS 覆盖 `de15f6ce…`） |
| oracle 身份 | `fixed-probe-v2-expected.json` = `e7a8c0d3…`（3123 B）、`oracle-before-run.json` = `48f34914…`（987 B） | 与 `actual-receipt.json` 内记录一致 |
| 14 条命令收据 | 结构化读取 action/argv/cwd/时间/exit/双流指针 | 全部指向**原 P2 树** cwd（`…/.worktrees/T03-mapping-p2-boundaries`），未伪装为本新树重跑 |
| 首次失败原件 | 逐份读原始 stdout/result | ruff-check 首次 **exit 1 / "Found 3 errors"**（E501×3）；ruff-format 首次 **exit 1 / "2 files would be reformatted"**；targeted 首次 **exit 1 / "1 failed, 11 passed"**（`test_socket_guard_is_restored_after_successful_fixed_probe`，tuple facts 与 JSON array 比较）；targeted 二次 **exit 0 / "12 passed"** — 与 `delivery.md` 叙述**逐条吻合**，首失败未被覆盖 |
| 历史原报告 | `mapping-S1-zcode-followup-1-full-report.md`(79 行) **全文**；`technical-disposition-draft.md`(58 行) **全文**；`mapping-S1-minimax-followup-1-full-report.md`(392 行) 读 200–392 行（F01–F11 原文、门判定、未验边界、最终判定），1–199 行仅取覆盖登记结构 | 见 §6 覆盖台账 |
| `history-agent/` | `historical-findings-index.md` 全文；`manifest.json`、`preparation-receipt.json`、`static-validation*.json`、`complete-scope-freeze.json`、`input-copy-provenance.json` 结构化解析 | 计数自洽：18 findings / 57 P0 / 866 旧 / 875 新 / 881 过程 / 892 并集 / 缺 11 |
| 过程工具源码 | `build/review-session/metadata/preparation-tools-v2/{make-dispatch.py.raw, full-review-template.md.raw, manifest.json}` | 模板即本次派发提示模板（`@@ROLE@@`/`@@MODEL@@`/`@@TREE@@`/`@@REVIEW_HEAD@@`/`@@REPORT@@`/`@@META@@` 占位）；未执行生成器或安装器 |

**过程工具静审**：`make-dispatch.py.raw` 与 `full-review-template.md.raw` 为纯文本模板/生成器副本，模板中不含执行、下载或越权动作；本轮仅作静审，未运行。

---

## 5. 完整范围覆盖（逐文件台账）

登记文件：`build/review-session/raw/path-coverage-register.json`（1028 项逐条，含 bytes、gitBlobOID、覆盖级别、范围说明/未读原因）。

| 覆盖级别 | 数量 | 含义 |
| --- | --- | --- |
| FULL（逐行读完全部内容） | **44** | 本方实际读完文件全部内容 |
| PARTIAL（按行区间/结构化字段读完） | **19** | 逐条登记实际范围与未读部分 |
| METADATA（仅身份/结构核对，未逐行读） | **964** | 逐条登记理由 |
| UNREAD | **1** | `design/prototypes/OntoLearn-Studio-Prototype.pen`（1.4 MB 设计原型资产，非工程代码，与产品验收无关） |

### 5.1 FULL（44）

mapping 四模块（`probe.py` 372 行 / `plan.py` 389 行 / `source.py` 297 行 / `__init__.py`）、`packages/engine/entrypoint.py`(37)、`invalidation.py`、`rdf_snapshot.py`、`protocol.py`、`resources.py`、`process_environment.py`、`__main__.py`；四个 mapping 测试（`test_mapping_entrypoint.py` / `test_mapping_plan.py` / `test_mapping_recovery.py` / `test_mapping_source.py`）；渲染层 `model.ts` / `MappingPage.tsx`；`csp.ts`；`tests/unit/t03-mapping-state.test.ts`；根 `pyproject.toml` / `package.json` / `eslint.config.mjs` / `.prettierignore`、`packages/engine/pyproject.toml`、`scripts/build-engine.mjs`、`apps/desktop/electron-builder.yml`；PRD 全文（1255 行 / 93584 B）；M0 计划全文（207 行）；P2 包 9 件原件与 5 份 stdout/stderr 日志；历史 Z 报告与技术处置草案全文；派发包 README 与历史意见索引。

### 5.2 PARTIAL（19，逐条范围）

`storage.py`（读 1–1007 / 1230 行；commit、`_check_slot`、`_replace_mapping`、快照/发布段全文，尾部 SCHEMA 与清理段未读）、`job_store.py`（85–120、700–745）、`coordinator.py`（240–262）、`main/index.ts`（34–95、170–190）、`mapping.css`（1–40 / 70）、`check-registered-scope.txt`（85–135）、minimax 历史报告（200–392）、`command-records.json` / `raw-evidence-manifest.json` / `actual-engine-inventory.json` / `complete-scope-freeze.json` / `input-copy-provenance.json` / history-agent 四份 JSON（结构化全字段解析）、`registry.json`（`productRuntime` 与 `mapping.commit` 条目）、`ci.yml`（1–40）、`invalidation-v2.json`（经消费路径确认，未逐行）。

### 5.3 METADATA（964）与未读原因

- `package-lock.json`（224331 B）、`uv.lock`（23393 B）：锁产物；以 `candidate-binding.json` 记录 SHA-256 **逐字节核对一致**，未逐行读；依赖版本另由 `packages/engine/pyproject.toml` 与 probe 内 `DEPENDENCY_VERSION_MISMATCH` 断言双向确认（openpyxl 3.1.5 / et-xmlfile 2.0.0 / defusedxml 0.7.1）。
- `packages/contracts/**`、`apps/desktop/src/main/**`（除已列 PARTIAL）、`apps/desktop/src/preload/**`：**base→303 的 T03 delta 未触及这些路径**（`git diff --name-status 5f910b52 30319412` 无 contracts/main 改动），属 I01–I04 继承面；本轮就 F03/F11 依赖的具体事实（registry 条目、coordinator 白名单、preload 12 个具名方法无 mapping、App.tsx 未挂载 MappingPage）做了定点核对。
- `packages/engine/tests/`（非 mapping 19 文件）、`tests/e2e/**`：继承测试面；本轮仅就 F08（Darwin skipif 恰 3 处）与 mapping 专项计数做定点核对，未逐行通读其语义。
- `docs/**`（除 §4 已列）：既有证据与历史文档，按索引与 manifest 核对身份。
- `p2-original-raw/**` 74 份：按 manifest 逐项重算哈希全部一致；stdout/stderr 为二进制原始流，未逐份当散文读。

**覆盖不足的诚实结论**：本轮**未达成**"1028 项全部逐行全文"这一上限；达成的是"全部业务相关源码与全部本候选证据逐行/逐字节读完 + 其余路径身份级核对"。因此整体候选不能给整体通过（见 §1、§9）。

---

## 6. 需求与验收范围

- **PRD 全文**已读：1255 行 / 93584 B / SHA `7586b2c4…`（与派发提示登记一致）。覆盖 §0–§17 全部条款、附录 A–G，含 **FR-001…FR-1001 全部 59 条**（57 P0 + 2 P1：FR-506 P1、FR-903 P1）、附录 C 能力矩阵、附录 D（含 D.1/D.2 九行依赖与失效规则）、附录 E（E.1 事件/条件/写入、E.2 固定轮次状态机、E.3 工单语义、E.4 指标公式、E.5 固定验收模型）、附录 F 授权表、附录 G（G.0 基线与重置契约、**G.1 M-01–M-06**、G.2、G.3、G.4、G.5、G.6）、§10 非功能、§11 指标、§12 端到端验收、§13 里程碑、§14 风险、§15 依赖、§16 待确认 Q1–Q10。**FR-300–304 仅按局部定位对待，未当作全范围**。
- **M0 全文**已读：`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` 207 行全六节（S1/ADR-0002、S2/ADR-0003、S3/ADR-0004、C1、B1、U1）及 §4 批次、§5 证据口径、§6 采纳记录。
- **父 57 P0 / 50 条 acceptance-baselines / requirements.csv / plan / review / 交接**：`control-snapshots/` 原字节副本在准备包内，本轮以结构化方式核对其存在与原字节保留，未逐行重做 57 条 P0 的跨模块验收（该范围本身未被本候选实现）。

---

## 7. Z1–Z7 / F01–F11（18 项）逐项独立复核

复核方法：**独立回到源码与固定原件**，不把 `technical-disposition-draft.md` 当最终事实。行号以本轮固定 HEAD `c1e44f81` 为准（与历史报告所引行号存在小偏移者已注明）。

| 编号 | 原性质 | 本轮独立复核结论 | 严重度处置 |
| --- | --- | --- | --- |
| **Z1** | 首报 P3；续报改判 P4；残余称"preview 不预显、commit 才发现" | **残余说法不成立**。`plan.py:310–317` 的 `candidate["id"] == fact["id"]` 判定位于 `fact["object"] is not None` 分支**之外**，故跨 owner 墓碑（object=None）同值复活在 **preview 层即报 OWNERSHIP_CONFLICT**；`storage.py:620–627` 的 `reserved_id = digest([subject,predicate,value])` 比较构成第二层独立拒绝 | 原严重度与改判历史**原样保留**；残余说法属**报告纠正项**，不改产品 |
| **Z2** | P3（renderer 无重复 predicate/引用列唯一性预检；后端 fail-closed） | 成立，并**精化触发面**：`model.ts:119–144` 只校验列存在、IRI 形式、引用列存在与主键唯一；**跨列重复 predicate 在页面上可达**（两个字段可填同一 IRI），后端 `plan.py:118–120` 拒绝；而**重复 referenceColumns 在本页 UI 不可达**（`MappingPage.tsx:210–218` 的 checkbox 切换去重），后端 `plan.py:132–135` 亦拒绝 | **维持 P3**；后端 fail-closed 已证，无越权/错误提交；正式 wire 字段级错误映射仍为待办 |
| **Z3** | P4（openpyxl 私有 `fs._worksheet_path`） | 成立：`source.py:268` 确用 `fs._worksheet_path`；当前钉死 openpyxl 3.1.5，无实际不兼容证据 | 维持 P4（升级断点观察） |
| **Z4** | P4（XLSX"三遍"读取） | 成立为 I/O 概括：`parse_xlsx` 两次 `_open_xlsx`（258、261）+ 一次选中表缓存扫描（268）；非实测性能数字 | 维持 P4，**不量化**时延/RSS |
| **Z5** | P4（ruff 计数口径；原报告称闭环） | 成立为工具输出口径；本轮**未复跑 ruff**，不追认 182/207 的全体解释 | 维持 P4（报告引用方保留命令与版本） |
| **Z6** | P4（CSV 严格行宽 vs XLSX 补稀疏尾空） | 成立：`source.py:96–97` 要求实际行宽等于标题宽（`ROW_WIDTH`），`source.py:283–286` 对稀疏行补空 | 维持 P4（已声明的解析差异） |
| **Z7** | P4（`storage.py:41–48` code 映射无 ownership → `INTERNAL_ERROR`） | 成立：`storage.py:41–48` 映射表仅 identity/revision/state/rounds/dependency/input，ownership 落入 `INTERNAL_ERROR`；`job_store.py:95–110` 的 `_application` 把 ownership 冲突转成有界 `OWNERSHIP_CONFLICT` + `detailRef` | 维持 P4（与 F11 同一接线约束，不制造第二缺陷） |
| **F01** | 低（`docs/iterations/T03/verify-packaged-probe.py` 回写三份受跟踪证据） | 成立（历史报告列 `:15–16`、`:66`；本轮未执行该脚本） | 维持"低"；流程/工具改进项，非已证包语义错误 |
| **F02** | 低（`draft.fields` 顺序漂移 + `JSON.stringify` 草稿等价比较） | 成立：`MappingPage.tsx:41–43` 将被编辑字段移到数组尾；`model.ts:65–67` `draftKey = JSON.stringify(draft)` 对顺序敏感；`model.ts:69–83` `currentPreview` 因此拒绝旧预览 | 方向 fail-closed，维持"低" |
| **F03** | 信息（registry `mapping.commit` 同时 `agentEligible:true` / `formal-write` / `design-only`） | 成立：`registry.json:341–356` 实见 `effect:"formal-write"`、`requiresChangeSet/Confirmation:true`、`agentEligible:true`；`coordinator.py:248–254` 的 `job.create` 仅允许 `test.read/test.atomic/test.rounds`；`packages/contracts` 在 base→303 **0 差异** | 维持"信息"；不能以单字段当可派发能力 |
| **F04** | 信息（ESLint ignores 不含 docs/reviews，`.prettierignore` 含 docs/reviews） | 成立：`eslint.config.mjs` ignores 仅 out/dist/release/build/.venv/playwright-report/test-results；`.prettierignore` 含 `docs/reviews` | 维持"信息"（策略不对称，非已证失败） |
| **F05** | 验证观察（preview 与 Store 所有权判定一致） | 成立为正面观察：`plan.py:289–329` 与 `storage.py:608–633`/`635–652`/`692–699` 双层设防；`test_mapping_plan.py::test_shared_fact_and_reserved_identity_block_ownership` 实测 preview 报 `OWNERSHIP_CONFLICT` | 非待修缺陷；结论仅在已核输入与分支内使用 |
| **F06** | 验证观察（"合法 XML 文本中的 `<` 必然转义，故 part 中不可能出现字面 DOCTYPE"，据此称闸门无假阳性） | **普遍结论不成立（须纠正）**。XML **元素文本节点与属性值**必须转义 `<`，但 **CDATA 段可承载字面文本**（如 `<t><![CDATA[<!DOCTYPE html>]]></t>`）；`source.py:181–186` 对**原始 part 字节**作无上下文子串拦截（`value.replace(b"\x00",b"").upper()` 后查 `<!DOCTYPE`/`<!ENTITY`），故含 CDATA 字面 DOCTYPE 的 part 会被判 `UNSAFE_XML`。历史实测仅覆盖三个普通单元格文本变体（正常解析），**未覆盖 CDATA** | 保留"验证观察"性质；**明确要求纠正普遍结论**；**本轮未制作/运行 CDATA fixture，不宣称产品已误拒**，亦**不擅改 DOCTYPE 闸**；是否属必须接收的合法输入属 root/T03 产品决定 |
| **F07** | 信息（开发态 CSP 校验失败→未捕获 rejection 且不建窗口） | 成立（行号校准：`csp.ts:16–17` 抛 `INVALID_DEVELOPMENT_CSP`；`main/index.ts:78` `void app.whenReady().then(async () => {`，`:84` 调用 CSP，`:180` 才 `createWindow()`，`:186` 无 catch） | 维持"信息"；继承缺陷，未见 CSP 绕过；交 desktop/main owner |
| **F08** | 信息（"0 skip"是 macOS 主机观测，CI Linux 仍有 3 处跳过） | 成立：`test_i04_lifecycle_boundaries.py:235,295,343` **恰 3 处** `skipif(sys.platform != "darwin")`；`ci.yml` quality job 为 `ubuntu-latest`；mapping 侧 5 处 `importorskip("openpyxl")` 位于 `test_mapping_source.py:103,121,153,173,204`（**在测试文件而非 source 模块**，原措辞"mapping source"易被误读） | 维持"信息"；不得发 Linux/目标 OS 零 skip 证书 |
| **F09** | 信息（"继承套件 1110 不含 mapping 专项"） | **原报告统计错误已证实**：`check-registered-scope.txt:90` 为 `collected 1110 items`；`:112–115` 明列 mapping 四文件点数 entrypoint 6 / plan 22 / recovery 9 / source 21 = **58**；`:130` 为 `1110 passed`。即 **1110 已含 58 mapping**，其余继承为 1052。**本候选静态计数**：entrypoint 12（6 旧 + 6 新）/ plan 22 / recovery 9 / source 21 = **64**，与 "1116 = 1110 + 6" 自洽 | 维持"信息/报告更正"；总数与专项必须分列引用 |
| **F10** | 信息（`dependencyKey` 字符集缺口对 T03 不可达） | 成立：`plan.py:102–108` 强制 `[A-Za-z0-9_.-]{1,128}` 并抛 `ValueError`；`storage.py:344–350` 对 definition id 仅校验非空字符串（较宽） | 维持"信息"；T03 假设消解，非 T03 调用方的约束归存储/契约 owner |
| **F11** | 信息（正式写入错误适配约束） | 成立：`job_store.py` `commit_job`（约 714–735）确在 `_application` 包裹内调用 `super().commit(...)`，与 `:95–110` 的有界 ownership 转换形成真实代码链；裸 `Store.commit` 的 ownership 冲突会降级 `INTERNAL_ERROR` 且 message 含 slot/predicate/owner/source_row（内部诊断） | 维持"信息"；未证明 `mapping.commit` 已正式接线；归 T01/受信应用服务 owner |

**18 项汇总**：本轮**未确认任何新的 P1/P2/P3**；确认 1 处报告统计错误（F09）、1 处普遍论断需纠正（F06）、1 处历史报告内部矛盾仍未闭合（Z2 续报"维持 P3"与终段"无任何 P1/P2/P3 遗留"并存）、1 处历史报告残余说法不成立（Z1）。Z1 的残余说法与主控处置一致，本轮以源码分支独立确认。

---

## 8. P2 增量与固定 17 项证据（本轮独立复核）

### 8.1 增量本体

`git diff --name-status 30319412 da1795b2` 的非 docs 改动**恰 2 个路径**：`packages/engine/src/ontolearn_engine/mapping/probe.py`、`packages/engine/tests/test_mapping_entrypoint.py`。`entrypoint.py`、`source.py`、`plan.py`、依赖、锁、builder、CSP、preload、App 均未改。

### 8.2 逐字节证据复核（本轮亲自比对，非采信文案）

| 断言 | 本轮复核方法 | 结果 |
| --- | --- | --- |
| source 与 package 结果一致 | 比对树内 `actual-source-stdout.log` 与 `actual-package-stdout.log` 字节 | **完全相同**（均 `da7c4574…`，2447 B） |
| 17 项完整匹配执行前 oracle | 解析两个 stdout 为 JSON，与 `fixed-probe-v2-expected.json` 深度比较 | **深度相等**（顶层键集、`cases` 17 项键值序、`boundaryEvidence` 六项、`limits`、`versions`、`exactFacts`、`registeredBusinessCapability:false` 全等） |
| oracle 为执行前写定 | `oracle-before-run.json` `createdAtUtc=2026-10-22T18:40:45Z`；实际 verifier 启动 18:47:19；所有受控命令记录同一 oracle SHA | 时间序一致，未见用新 stdout 重建 oracle |
| `-O` 优化模式另一次执行 | 读 raw 原件 `…184730Z-source-probe-optimized…/stdout.bin` | **字节相同**（`da7c4574…`），exit 0，argv 含 `-O` |
| 三类额外参数拒绝 | 读 raw 收据与 stderr | path/script/url 三例 **exit 2 / stdout 0 / stderr 32 B**，stderr 内容恒为 `MAPPING_PROBE_INVALID_ARGUMENTS\n`；stdout 与 stderr 互不混淆 |
| 440 项 engine inventory | 解析 `actual-engine-inventory.json` 并与 raw 原件比字节 | **字节相同**；条目 **440** = file 391 + directory 49 + **symlink 0** |
| 引擎可执行文件身份 | 收据记录 4622464 B / `c4c8d80c…` | 与候选绑定一致；**本树无 release/ 目录，故未在本树重算**（如实记为未验项） |
| 三模块 code object 绑定 | 读 `verify-packaged-boundaries.py:63–121`：`compile(..., optimize=0)` + 递归仅替换 `co_filename` + marshal4 | 与收据 normalization 描述一致；**不升级为全部依赖语义等价** |
| 首失败保留 | 逐份读 4 份失败/通过原件 | 全部保留，见 §4 |

### 8.3 六新增项语义复核（源码推导 + 证据对齐）

| 新 case | 预期 | 本轮独立推导（源码） | 实际证据 | 判定 |
| --- | --- | --- | --- | --- |
| `external-cached-formula` | 001 / 只读已保存值；设备/2/2 | `_external_workbook` 写死最小 OOXML：`<c r="B2" t="str"><f>WEBSERVICE("https://example.invalid/ref")</f><v>只读已保存值</v></c>`；`load_workbook(data_only=True)` 读缓存值，`data_only=False` 侧公式不触发 `FORMULA_CACHE_MISSING`（`cell.value` 非 None）；`fs._worksheet_path` 缓存扫描中该格 `v` 非空故不入 `empty_caches` | cells `["001","只读已保存值"]`，sheet 设备 / row 2 / column 2，socketCalls 全 0 | 匹配 |
| `external-hyperlink` | 001 / 显示文本；设备/2/2 | 同上，B2 为 `inlineStr`，另加 `TargetMode="External"` 关系；`load_workbook(keep_links=False)` 且解析层从不发起外联 | cells `["001","显示文本"]`，设备/2/2，socketCalls 全 0 | 匹配 |
| `csv-file-limit-located` | SOURCE_LIMIT，空/0/0 | `source.py:71–75` `_bytes` 先于任何表上下文拒绝 → `Issue(code, sheet="", row=0, column=0)` | SOURCE_LIMIT / "" / 0 / 0 | 匹配 |
| `csv-column-limit-located` | SOURCE_LIMIT，CSV/1/0 | `_table` 的 `len(cells) > MAX_COLUMNS` 先于表头校验 → `fail("SOURCE_LIMIT", sheet, number)`，column 默认 0 | SOURCE_LIMIT / CSV / 1 / 0 | 匹配 |
| `csv-cell-limit-located` | INVALID_CELL，CSV/2/1 | 第 2 行单格 32769 > `MAX_CELL` → `INVALID_CELL(sheet, number, i)` | INVALID_CELL / CSV / 2 / 1 | 匹配 |
| `csv-row-limit-located` | SOURCE_LIMIT，CSV/50002/0 | 50002 记录 > `MAX_ROWS+1` → `SOURCE_LIMIT(CSV, 50002)`，column 0 | SOURCE_LIMIT / CSV / 50002 / 0 | 匹配 |

旧 11 项保留：`probe.py` 中原 `run` 拆为 `_legacy_cases`，11 个 case 名与结果值与旧 oracle 一致；新增 6 项后 `cases` 共 17 项且与 oracle 键集完全相同。

### 8.4 边界口径逐条核对（与派发提示声明一致与否）

| 派发提示声明 | 本轮核对 | 结论 |
| --- | --- | --- |
| 17 项共用一次 source、一次 package 退出码；`independentPerCaseProcessExit:null` | 收据 17 条 `allCaseRecords` 与 6 条 `newBoundaryCases` **全部**为 null，且 `executionDomain` 明写"one mandatory17case invocation" | **一致，无夸大** |
| socket 为三 API 在固定输入构造/解析期间的累计计数，非 17 个隔离 counter | `probe.py:191–211` 为单次 `contextmanager`，`calls` 跨全部 case 累积，各 evidence 存当时快照；收据标 `guardEvidenceScope: cumulative across all17` | **一致** |
| dependency import 在 guard 前 | `run()` 先 `import_module("openpyxl")` 再进 guard；但 **`defusedxml` 的首次 import 发生在 guard 窗口内**（`probe.py:39` 的 `fromstring` 与 `probe.py:236` 的 `iterparse` 均在被 guard 包裹的解析路径中） | **表述不精确**（见 §9 N01）；方向为 guard 更严而非更松，不削弱零计数结论 |
| 非全 OS 网络证明、非 17 隔离 counter、非所有公式格式证明 | 三 API 计数不含预先保存的 API 别名、其他 OS 网络入口；仅证明两个固定合成输入 | **一致** |
| 两成功引用 case 的 column 2 是已知 B2 坐标；四 CSV 才是真实 issue 完整定位 | `probe.py:293` 的 `"column": 2` 为**硬编码字面量**（sheet/row 由解析结果派生） | **一致**（见 §9 N02） |
| 三模块绑定仅归一化 `co_filename`；440 项 inventory 是其余字节身份 | verifier 源码与收据一致；inventory 实际 440 项且 **symlink 0** | **一致**（见 §9 N04） |
| 1116 与 mapping 专项分列；总 1110 已含 mapping 58 | 本轮静态计数：当前 mapping 专项 64（entrypoint 12/plan 22/recovery 9/source 21），总数 1116 = 1110 + 6 | **一致**，F09 更正成立 |

---

## 9. 本轮新发现（本方意见）

严重度沿用历史报告口径（P1/P2/P3/P4/信息/验证观察）。**本轮未发现 P1/P2/P3 级产品缺陷**；以下为 P4/信息级与一处纠正性意见。

### N01 — 信息 — 证据域表述不精确：`defusedxml` 首次 import 发生在 socket guard 窗口内

- 位置：`packages/engine/src/ontolearn_engine/mapping/probe.py:39`、`:236`、`:346–353`
- 触发：`run()` 先 `import_module("openpyxl")`（guard 前），再进入 `_socket_guard()`；`_legacy_cases` → `_variant` 的 `from defusedxml.ElementTree import fromstring` 与 `_empty_formula_caches` 的 `iterparse` 均在 guard 内首次触发 `defusedxml` 导入。
- 影响：派发提示与 `delivery.md` 的"依赖 import 在 guard 前""证据域不包括依赖 import"对 `defusedxml` **不成立**。方向上 guard 覆盖了更多（若该导入触发 socket 会被计数并使 probe 失败），因此**不削弱**"零调用"结论；但作为对外证据口径应按实际执行描述，避免被引为"依赖导入期不在测量域"。
- 证据：probe.py 上述行号；`actual-receipt.json.socketMeasurementDomain` 亦写"dependency import happens before guard"。
- 建议：证据文案改为"openpyxl 于 guard 前导入；defusedxml 首次导入发生在 guard 窗口内"。**不改产品**；若要严格表达"依赖导入不计入"，可在 guard 前预导入 defusedxml（属产品改动，需新候选与双新审，本轮不建议）。

### N02 — 信息 — 两个外部引用 case 的 `column` 是硬编码字面量而非解析派生值

- 位置：`probe.py:288–295`（`"column": 2`）
- 事实：`sheet` 取自 `table.sheet`、`row` 取自 `table.rows[0].number`（均派生），唯 `column` 写死为 2。
- 影响：不影响本轮判定（cells 断言 `["001", value]` 已钉住内容与位置），但该列值**不构成解析器列定位的独立观测**，只是已知 B2 fixture 坐标；若 fixture 形状变化，记录会静默保持 2。
- 建议：与 §8.4 一致地按"已知 B2 坐标"引用；若需升级为定位证据，改为由解析结果派生列号（产品改动，需新候选）。

### N03 — 信息/正向观察 — 四类 CSV 上限在 303 基线已有单元级覆盖，P2 的增量价值在"包内可执行 + 完整定位"

- 位置：`packages/engine/tests/test_mapping_source.py` 的 `test_csv_file_column_cell_and_row_limits_are_enforced_with_locations`（与新增 probe 四例同输入同期望）；新增在 `probe.py:296–342`
- 影响：把"仅单元级语义"提升为"**打包后 CLI 实际执行**的固定 17 项之一，且补齐 sheet 维度并与执行前 oracle 整体比对"，是实质证据升级；同时提示引用时不应把它表述为"首次覆盖该语义"。
- 建议：交付文案按此口径表述；不改产品。

### N04 — 信息 — 440 项 inventory 实际无 symlink 条目

- 位置：`docs/reviews/T03/mapping-p2-boundaries-20261023/actual-engine-inventory.json`；verifier `verify-packaged-boundaries.py:136–149`
- 事实：440 项 = file 391 + directory 49 + symlink **0**；verifier 具备 symlink 分支与 `PACKAGE_SYMLINK_ESCAPE` 检查，但本包未命中。
- 影响：本地 Codex 独审中"symlink target 均核对"一句在本包无对应对象，属**表述超出实际对象**（非产品问题）。
- 建议：引用时改为"逐项核对 391 文件 + 49 目录的字节身份与种类，无 symlink 条目"。

### N05 — 信息/纠正性 — F06 的普遍结论须按精确表述纠正（CDATA 边界）

- 位置：`packages/engine/src/ontolearn_engine/mapping/source.py:181–186`
- 事实：精确表述应为"XML **元素文本与属性值**中的 `<` 必须转义，故正常单元格文本不会在 part 字节中形成字面 `<!DOCTYPE`；但 **CDATA 段**可承载字面文本，而闸门是无上下文原始字节子串匹配"。因此"合法 XML 中不可能出现字面 DOCTYPE"这一**普遍**命题为假。
- 影响：闸门对含 CDATA 字面 DOCTYPE 的 part 会判 `UNSAFE_XML`（潜在过拒）；**本轮未制作/运行 CDATA fixture，不宣称产品已误拒**，也不判定该输入是否属必须接收。
- 建议：原报告侧纠正普遍结论并区分已测普通转义样例与未测 CDATA；是否属必须接收输入与是否需要一次最小验证由 root/T03 决定。**不得据此自行放宽或加严安全闸。**

### N06 — 信息 — 运行发生在 repair base HEAD + 等候选产品字节，引用时不得写成"在候选提交上实测"

- 位置：`docs/reviews/T03/mapping-p2-boundaries-20261023/actual-receipt.json` 的 `runtimeHead: 30319412…`；`candidate-binding.json` 的 `runtimeState`
- 事实：实测时 HEAD 为 `30319412`，两产品文件内容已等于候选（`candidate-binding.sourceIdentities` 11/11 与当前 HEAD 工作区逐字节一致）；候选提交在其后产生。
- 影响：证据**适用于**候选字节（字节同一已证），但表述必须区分"提交后 HEAD 上的实测"与"提交前工作区（内容等同候选）的实测"。
- 建议：报告/交付统一采用后一口径，并附字节同一性证明。

### N07 — 信息 — Z2 的"维持 P3"与原续报终段"无任何 P1/P2/P3 遗留"仍并存

- 位置：历史 Z 报告 §3 各条处置与 §6 终态
- 事实：Z2 条目写"P3（维持）"，终态写"无任何 P1/P2/P3 遗留"，二者对 Z2 不自洽；主控草案亦要求"原 Z 对齐"。
- 影响：报告内部一致性缺陷，非产品缺陷。
- 建议：由原 Z 侧明确对齐后归档；本轮不代签、不改其历史原件。

---

## 10. 各门判定（分列，不以静态代替运行）

| 门 | 判定 | 依据与未验边界 |
| --- | --- | --- |
| **静态（源码/契约/锁/构建配置）** | **通过（限本次覆盖范围）** | 全部业务相关源码与本候选证据逐行/逐字节读完（FULL 44 + PARTIAL 19）；其余 964 路径身份级核对；范围内无 P1/P2/P3 新缺陷；**未达成 1028 全文覆盖**（见 §5.3） |
| **运行（单元/集成/恢复）** | **引用既有证据，本轮未重跑** | 固定 log：`check-registered-scope.txt` 显示 1110 passed（macOS 主机观测）。本轮**未执行** `npm run check`（本树无新结果，禁止借旧包/旧树伪称 fresh）。当前候选的 1116/638 属既有 P2 树实测，非本新树重跑 |
| **打包（unsigned macOS 27 arm64 目录包 CLI）** | **通过（限固定 17 项与三拒参）** | 本轮**未在包内重跑**（本树无 release/）；逐字节复核既有实际包 5 次执行原件：source/package exit 0 且 stdout 字节相同并与执行前 oracle 深度相等；`-O` exit 0 同字节；path/script/url 三拒参 exit 2/stdout 0/固定 32B stderr |
| **父业务（FR-300–304 正式接线：文件/工作表选择、公共契约、preload、IPC、正式 UI、Job/ChangeSet、Store 正式提交路径）** | **不通过 / 未完成** | `App.tsx` 未挂载 MappingPage；preload 无 mapping 方法；IPC 路由无 mapping 通道；registry `productRuntime=["health"]`；`mapping.commit` 为 design-only 且 coordinator 仅开放 test.* 能力；`MappingPage.tsx` 自述"受信文件选择尚未接入""正式项目事务尚未接入" |
| **GUI / 浏览器交互 / e2e / 原生恢复** | **无法验证** | 本轮未启动 Electron/e2e（GUI 由 T08 占用、且本轮不获运行票）。历史已记录的 e2e 精确重跑合同（Linux `openbox`/`xdotool`/`xvfb-run` + `I04_TEST_FIXTURE` 需新建目录、第 3 例需 `I04_NATIVE_ISOLATED=1`、必须 unset `I02_HMR`）未执行 |
| **两 OS（Windows / macOS 干净设备）** | **未验证** | 仅本机 macOS-27.0.1-arm64 未签名目录包 CLI |
| **签名安装** | **未验证** | `electron-builder.yml` 为 `mac.identity: null` + `target: dir`（无签名）；发布门不在本轮 |
| **native / ABI / loader / drain / SDK / witness / descriptor / index 受限载荷** | **未读 / 未验（按原权限保留）** | 未触碰 `.worktrees/T03-native-location-N0-build` 停止现场及其 caller WIP；未解码受限身份载荷；该项门独立记录，不因本次全范围审读而关闭 |
| **父 57 P0 / 跨模块验收 / 其他 FR 族** | **未关闭** | 本轮结论不关闭其中任何一项 |
| **CI 与远端** | **未验证** | `.github/workflows/ci.yml` 已静态读（quality=ubuntu-latest）；本轮未触发 CI、未核远端 develop/保护源 |
| **生产 / 发布** | **未到** | push/PR/合并/发布门保持关闭 |
| **同版双审（另一指定模型）** | **不在本轮范围 / 尚未终态** | 本轮未读取、未推断另一方本轮任何意见、进度、raw 或 metadata |

---

## 11. 若后续需要运行（本方给出的精确请求，交 owner 按根阶段票安排）

本轮**不需要**任何新运行即可支撑上述判定。若 root 决定补证，最小集合为：

1. **本候选同树 fresh check**（仅在需要"本树运行证据"时）：`npm run check`（cwd=本 reviewtree，env 沿用 `build/review-session/metadata/setup-receipt.json` 的 8 项路径与 8 项清空键），期望 638 TS / 1116 Python / 0 skip（macOS 主机观测）。**须新 raw 轮次目录**，不得覆盖 `docs/reviews/T03/check-*.txt` 或任何已归档 oracle。
2. **本候选同树 fresh package + 固定 17 项**：`npm run package:dir` 后 `uv run --frozen python docs/reviews/T03/mapping-p2-boundaries-20261023/verify-packaged-boundaries.py`（该脚本只写 `build/mapping-p2-boundaries-20261023/verification-<UTC>-<rand>/`，**不回写受跟踪 docs**，与 F01 的旧脚本不同）。期望：source/package exit 0 且 stdout 与 oracle 深度相等、三拒参 exit 2。
3. **e2e（历史遗留门）**：按历史 §9.1 合同，须 root 窗口 + `I04_TEST_FIXTURE` 新建目录 + `I04_NATIVE_ISOLATED=1`（第 3 例）+ unset `I02_HMR`；macOS 仅第 1 例可跑。
4. **CDATA 最小验证（可选，仅当 root 决定该输入属必须接收）**：构造一个含 `<t><![CDATA[<!DOCTYPE html>]]></t>` 的最小 worksheet part，交给 `parse_xlsx` 观察是否被判 `UNSAFE_XML`；本轮**未**制作该 fixture，**不建议**在未决前改闸。

以上均**未执行**，也不构成本轮结论的前提。

---

## 12. 独立性、STOP 与写入边界声明

- **未读取**另一指定模型本轮的意见、进度、raw、metadata；未通过 Git 新日志、应用数据库、状态库或其他报告获取对方本轮材料；**未传递**本轮意见。历史 Z1–Z7/F01–F11 仅从同一公开固定包（`docs/reviews/T03/mapping-followup-1-completed-20261023/` 与 `history-agent/`）读取，未冒充对方当前答复。
- **未触碰** `.worktrees/T03-native-location-N0-build` 停止现场及其 caller WIP；未研究或调用未签的 native/producer/caller、局部函数、runner/reader、ABI/loader/drain；未以 fixture/dry-run 替代；未借票、未抬 guard。
- **未修改**任何实现、测试、依赖、锁、配置、原验收或历史原件；**未** stage/commit/push/PR/切分支；**未**新建 Goal 或其他聊天；**未**付费、未重置、未读取密钥；**未**获取 CUA 或启动 GUI。
- 本方写面仅：`build/review-session/reports/mapping-P2-minimax-full-report.md`（本报告）、`build/review-session/metadata/task-actual.json`、`build/review-session/raw/path-coverage-register.json`。
- `git status` 末态应仍为仅 ` M AGENTS.md`（授权保护覆盖，未暂存）。

---

## 13. 移交建议（按责任方）

| 项 | 责任方 | 建议 |
| --- | --- | --- |
| N01 / N04 / N06 / F09 / Z1 / F06 | 报告与证据引用方（root/T03） | 统一按精确口径修正表述；F09、F06 需在原报告侧显式纠正；Z1 残余说法以本报告 §7 的源码分支结论为准 |
| N02 / N03 | T03 owner | 如需把列号升级为派生证据、或调整"首次覆盖"表述，须新候选 + 双新审；本轮不改产品 |
| Z2（P3） | T03 owner + T00/T01 接线 owner | UI 重复 predicate 预检与正式 wire 字段级错误映射；**改 UI 即须新候选与原双新审** |
| Z7 / F11 / F10 | T01 / 受信应用服务 owner | 正式 mapping 写入经 `JobStore.commit_job` 路由（取得有界 `OWNERSHIP_CONFLICT` + `detailRef`）；definition id 字符集与契约层对齐 |
| F01 | T03 owner | `verify-packaged-probe.py` 输出目录参数化（新增 P2 verifier 已不回写受跟踪文件，可作参照） |
| F02 | T03 owner | 草稿字段稳定排序或按字段名规范化 `draftKey` |
| F03 | contracts owner | `mapping.commit` 的 `agentEligible` 与 `design-only` 表述一致性 |
| F04 | 工具链 owner | ESLint ignores 与 `.prettierignore` 对 `docs/reviews` 的处置统一 |
| F07 | desktop/main owner | 开发态 CSP 校验失败的显式诊断 |
| F08 | 报告引用方 | 引用检查结果时标注主机平台 |

---

## 14. 本报告自限

本报告基于固定 HEAD `c1e44f81723f9c616f669f56481d1b1ada7e57f2` 的**静态审读 + 既有原件复核**成立；任何实现、测试、依赖、验收或基线变化后须重新验证并重新双审。本报告**不构成** push/PR/CI/合并/远端放行，**不关闭**父 57 P0、跨模块验收、双 OS、GUI、签名安装与生产门，**不替代**另一指定模型的独立同版审查，也**不继承**任何历史 Pass。范围内未发现 P1/P2/P3 级新缺陷；整体候选因父门未验与本轮覆盖未达全文上限而**明确记为不通过**。
