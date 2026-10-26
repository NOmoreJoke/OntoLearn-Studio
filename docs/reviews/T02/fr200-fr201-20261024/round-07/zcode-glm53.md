# T02 FR-200/FR-201 R07 独立工程审查报告（ZCode / GLM-5.3）

> 版本说明：本文件为同 SID 内按操作者事实核对包（5985B / SHA256 `63a03aea7fc5bb9d3568ab7fd2dbdb89cd839a03fcb8596078ad5e977b0ae5a6`）对 Z-A01–A10 做的一次最小事实修订版；本方首自然稿已逐字封存于仓外 `zcode-natural-01.md`（30400B / SHA256 `f25d8827a115cb606c970e56dff5e3335eeba68f498fe3f7aed48255daac7723`），判词等级、完整 160 项、Top10 与全部 HOLD 未变。

## 0. 身份、配置与独立性声明

- 本方配置：ZCode 桌面 / Start Plan 优先 / GLM-5.3 / 最高思考 / 完全访问。会话：用户指明原 SID `session_1f663b7f4a09f84efc0dcd066f28ce63`；本报告在本 SID 内续作完成：本方作者直接经历三次 generic 系统繁忙（作者已知部分）；操作者官方归档原件记录该任务累计 5 次 generic busy、4 次同 SID 正常续接，本次恢复由谁触发不推断（来源＝操作者官方归档，非本方 UI 自证）。generic busy ≠ 额度耗尽，官方"5 小时剩余 100%"原件不被改写；未重置、未升级、未付费、未换模型、未新建任务。UI 任务 ID/provider/model/thinking 等由操作者从官方 UI 核验，本方不虚造 UI 观测，仅记录上述用户陈述与本会话实际行为。
- 实际 cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes`；分支 `feature/weekly-t02-fr200-fr201`；base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `b215f5432d0c9f74df9e9e3fbb6120bff57703a9`，tree `7cab46f041140114d5011d86077c54aeb93d537d`；33 累计提交、88 差异叶（+17736/−256）。以上全部由本人 `pwd`/`git rev-parse`/`git log`/`git diff --stat` 实测核对，与封存提示一致。
- Git 身份：`NOmoreJoke <kai1847756198@gmail.com>`。
- ROOT 封存提示核验：附件 28704 bytes、UTF-8、SHA256 `466fd48de09b5109ae7e0563557f01d811fb546caada6fb40441fe79f4af603e`，已完整读至 EOF；清单 `> ` 行恰 160。
- 工作区状态：`M AGENTS.md`（15147B / SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保护的未提交 policy overlay，不属候选新增）；`?? round-01/02/03` 未跟踪旧报告保持原样，未混入、未更改。
- 独立性：R01–R06 为双方同等历史输入，本方读取了双方历史报告与处置；R07 另一方正文未读取、未索取。写入前 `ls docs/reviews/T02/fr200-fr201-20261024/round-07/` 无输出（目录不存在或为空）——这是本轮唯一涉及的对方元信息事实，不据此反推任何正文内容。
- 冻结遵守：本轮未运行 npm/check/vitest/pytest/ruff/build/package/install/sync/HMR/GUI/产品/SQL/probe；未动 index/commit/push/branch/remote 写操作；未读密钥、无关 profile、`.mimosa/`、对方 R07 报告。纯计算（tomllib/ast/zipfile/hashlib/difflib、git 只读、`git ls-remote` 只读）在隔离临时目录 `/tmp/r07-zcode-glm53/` 完成，方法均在正文披露。唯一仓库写入即本文件。

## 1. 已读范围与"本人实做 vs 读回验证"的区分

本人实际执行（可复算）：
- 附件字节/SHA（`wc -c`/`shasum -a 256`）；AGENTS.md、PRD、pyproject（330 与 b215 两版）尺寸/SHA。
- `git log/diff/show/ls-tree/grep` 只读：33 提交链、88 叶清单、b215 单行 diff、330 十叶、8318 两测试文件 diff、storage/coordinator/domain_changesets/query_presentation/rdf_snapshot/mainline/job_store/project_host 现行实现、renderer/preload/main diff、CI/NOTICE/engine pyproject diff、vendor 四 wheel（zipfile 元数据：fr201.1=2378177B、fr201.2=2378736B、fr201.3=2379774B，各 142 条目全 STORED；upstream=615416B、deflate）。
- 纯计算：pyproject 去 literal 后 parsed TOML 与 bytes 双等价；glob 对 tracked 文件匹配恰 7 份；8318 两文件剥除六个 `encoding="utf-8"` keyword 后 `ast.dump` 与旧版严格相等（ensure_ascii/Try/Assert 计数不变）；全测试树 write_text 普查（AST）：39 处 write_text、19 处显式 utf-8、直接载荷 `json.dumps(..., ensure_ascii=False)` 的 10 处全部带显式 utf-8、0 处缺。
- `git ls-remote origin`（只读）：`develop=583c05c7`、`feature/weekly-t02-fr200-fr201=33059f8219623e59bf0816c36b083e5fa96d954f`——b215 确未推送，与封存提示一致。

读回验证（未重跑，只读原件）：
- 需求面：PRD（93584B/SHA `7586b2c4…0fbb`）FR-200 第307–309行、FR-201 第311–318行原文、附录 C（959–979）、D.1/D.2；ADR-0002 canonical 段（term(value).n3()、SHA-256 初始三元组、非规范别名拒绝、ownership/墓碑/单值执行格式、事务语义）；M0 计划 S1 全文（含 49/53 行交付与验收）；D8 选择 A 原件 JSON（decision A、45f64 不合并、四禁止、仅 T02 本功能 R4+、不扩预算/付费）。
- 闭包补充阅读（Z-A02 修订）：附录 E（1016–1078：E.1 事件/条件快照与写入、E.2 固定轮次状态机、E.3 工单语义、E.4 指标公式、E.5 沙盘验收）与附录 G（1115 起：G.0 固定基线与重置、G.1 映射与身份、G.2 查询/SHACL/推理/规则、G.3 行为/条件快照/冲突、G.4 沙盘）及 FR-003（244 内置示例）、FR-006（256 数据层次与结果失效）、FR-204（330 建模草稿与修改预览）、FR-804（521 版本化 Diff/原子提交/撤销）条款原文已读。映射与未验分层：FR-006 公共失效机制（invalidation-v2、同事务过期、test_storage 九行正负例）既有证据在，FR200 GUI 编辑→四具名下游（推导/保存查询/SHACL/报告）未逐类联验（与 D.10 同分层，不判缺失）；FR-204/804 中本候选承担的 ChangeSet 链（preview/confirm、基准复验 REVISION_CONFLICT、整批原子、Job/marker 幂等）已证，Agent 草稿生成路径未接线（S3 前），"撤销本次 ChangeSet"入口存在但本组未实测（见 #128 修订），FR-004 快照恢复单独确认路径不在本候选；FR-003 引擎侧示例提供器存在（mainline.py `BuiltinExampleProvider`，example_id+input_digest 绑定），附录 G 固定输入/预期输出/失败样例未由本候选验证；附录 E 行为/沙盘执行、E.4 指标、E.5 验收模型本轮范围外（断言事实仅按附录 C"作为查询、规则和行为输入"行成为未来输入），E.2 轮次状态机属 S1 storage（start_run/commit_round），本候选未改、其运行证据含于 3769 全集。以上为阅读/证据映射，不据此断言产品缺实现，也不补新功能或运行。
- 历史输入：round-04/05/06 双方报告与处置（R06 Z P1–P8、MM D1–D12、35 条历史位置、version-map.json）、round-05 原条款证据映射（28 笔、57 事务 7/7/7/7/22/7、43 拒绝=42 INVALID+1 OWNERSHIP）、status.md/m0-checklist 的 330 追加节。
- 原始证据目录（只读）：O040（934 Windows cp1252 首败）、O045（付款/spending limit 门禁三 job NOTRUN）、O046（330 attempt2：`121169236618-first-failure-excerpt.txt` 实证 Ruff lint 全过后 FORMAT 在 `round-06/minimax-m31flash-r2.md:118:52` 的 Python fence 报 1 would/385 already、exit 1；FINAL-CI-FACTS 含 checkout `5be52fc4`）、O047（COMPLETION.json 3595B/`c2759c4d…`、qualification.json 20910B/`e7e05e6a…`、FINAL-MANIFEST.json 23308B/`e1c2e852…`，均与封存提示逐字节一致；本次未重跑任何验证）。
- 未读/无法确认：O047 的 124 针逐针重算（采信其 ROOT 直核记录与本人上述抽样）、Windows 任何本轮新运行、打包产物新制、密钥类材料。

## 2. 候选链核验（本人实测）

1. cb8→aff386f6：证据文档+CI Windows 首败诊断 10 行（`engine:check` 拆分：非 Windows 原样；Windows 加 `-vv --maxfail=1 --tb=short` 与 locale/utf8 JSON 打印，步骤名明示 "not acceptance"）。产品/测试/依赖不变。
2. aff→934bd14f：10 纯证据文档。
3. 934→831813c6：恰两测试文件、5+1=6 处 `encoding="utf-8"`（本人 AST 剥除后严格等价已证）；不用 PYTHONUTF8。
4. 8318→33059f82：8 新 R06 证据叶+status/m0 追加；追加节诚实绑定 8318 历史身份、明示无 push/CI/merge 授权，未改写旧 manifest。
5. 330→b215：仅 pyproject.toml 一行——`[tool.ruff.format].exclude` 追加 literal `docs/reviews/T02/fr200-fr201-20261024/round-[0-9][0-9]/{zcode-glm53,minimax-m31flash,minimax-m31flash-r2}.md`；配置 1593B/`e4b989aa…`→1707B/`ed02773b…`。去新项 parsed TOML 等价、去该行 bytes 等价、lint/per-file-ignores（4 个冻结 T01 .py）、line-length/target-version、pytest testpaths、命令、CI、锁、依赖、预算均不变；其余 1370 物理源与全部旧 raw 报告无变化。该 pattern 对当前 tracked 恰匹配 7 份（round-04/05 各 zcode+mm、round-06 zcode+mm+mm-r2），含字符类与花括号 alternation、无跨层 `*`，不匹配 archive/disposition/manifest/其它 MD/任何 .py；只作用于 format，不改顶层或 lint exclude。`engine:check` 中 `ruff format --check .` 即 O046 实证的失败点，本修复直接覆盖该文件，未重排不可变审查引文。

## 3. 实现审查（按发现编号）

结论先行：**未发现 b215 相对受审基线的新增 P0/P1 源码缺陷**；以下按等级列出本轮发现与保留项。判定依据均出自本人直读代码/证据，非转述。

- **F1（阻断合并，非源码缺陷）Windows 完整验收仍缺**：b215 未 push、无本 head CI（`ls-remote` 实证远端仍 330）。O047 为 macOS 本地同 head 证据（自然 0 全检+原六 GUI 6 PASS），不能替代 Windows 3769 全集与后继步骤。属合并门禁，按第五节判词处理。
- **F2（P3，维护）formatter 排除面按名枚举**：literal 只含三个已知模型文件名。未来评审若引入新模型名 raw 报告，仅当该新 Markdown 含需要改写的可解析 Python 围栏时才会再次触发 `ruff format --check` 失败——单纯文件名不匹配不必然失败；本报告自身 `zcode-glm53.md` 恰在保护面内（正确）。不建议现在放宽为跨层通配（会放大排除面）；维持"新候选追加 literal"的最小维护约定即可。
- **F3（P3，维护）write_text 窄修复后的编码规约**：全测试树 39 处 write_text 中 20 处无显式 encoding（当前载荷为 ASCII/非 JSON）。六 keyword 修复只覆盖 Unicode trace 路径；未来向这些调用点添加 Unicode 载荷时必须同步带 `encoding="utf-8"`（Windows cp1252 默认编码风险）。历史意见"窄模式零残留不证明全部编码风险"维持。
- **F4（双口径已解清，Z-A07 修订）write_text 载荷 UTF-8 计数**：两口径均核清且无缺漏——第一实参恰为 `json.dumps(..., ensure_ascii=False)` 调用的 10 处、10/10 显式 UTF-8；计入第一实参内部 BinOp 拼接（`json.dumps(...) + "\n"`）后为 12 处、12/12 显式 UTF-8。额外两处不是间接变量，位置：`packages/engine/tests/test_mainline_postwrite_rows_budget.py:261`（同行显式 UTF-8）；`test_mainline_postwrite_text_budget.py:200` 调用、201–213 载荷+换行、214 显式 `encoding="utf-8"`——两处行号本方已读回核实。封存提示的"12"仅指这些 write_text 载荷，不指整个测试树所有 `ensure_ascii=False`；与 ROOT 独立静态窄核一致，无功能影响。
- **F5（P3，历史维护）两 TS 仍 PATH python**：`tests/unit/t01-ontology-metadata-contract.test.ts:168`、`tests/unit/t01-mainline-contract.test.ts:656` 用 `execFileSync('python', …)`；另两处已用 `uv run --frozen python`。维持原处分：下次授权触及或新环境适配前处理，非本轮阻断。
- **F6（历史 OPEN 保留）**：D3 definitions 早期坏 wire（preview 内 Store 校验先抛，UNKNOWN/HOLD，T01 接线前）；D6 standalone 裸 EOF 索引残余（当前 term 封装未构造可达反例，保 OPEN，不泛捕 IndexError）；D7/P5 契约 26/UI 17/交集 10/缺 16（集合事实成立，不证 16 条当前可达）；P6/D5 witness 选取 SQL 无 ORDER BY（SQL 事实+未确认观察，未证跨运行缺陷）；D11 4299/4300 应用边界断言（vendor 边界不等应用边界）。全部按 round-06 处置延续，不因 b215 自动关闭。
- **F7（发布前 HOLD 群保留）**：签名/公证/wholeApp 法律/_distutils、跨 OS/参考设备/macOS15/Win11、Q5/D2 容量与旧超限库恢复、损坏 SQLite 物理资源保护、unknown parser/N3/Store/坏快照、Undo GUI、未验 ownership 家族、native engine 及 named App 未知退出码、四具名下游（D.2）逐类联验。详见第六节。
- **F8（正面核验，Z-A04 修订）ownership 闭环与 D8 四禁止**：`rdf_snapshot.py` 的受控分类只接 `BadSyntax/Notation3InputError` 两族（vendored 补丁在 parser 源头定义 `Notation3InputError` 家族，NOTICE/PROVENANCE 透明披露，fr201.3 STORED 确定性重打包）；`preview_changeset` 对 manual/edits 做 `term(value)` + `parsed.n3()==value` 精确 canonical 拒绝，不静默规范化、不按异常文案分类、不泛捕 ValueError、不升容量上限——与 D8 选择 A 四禁止一致。同时 `rdf_snapshot.py:42–45` 仍保留 `except Exception → 普通 ValueError` 的未知失败分支，原 UNKNOWN/HOLD 语义不变——"不泛捕 ValueError 作业务分类、不按异常文案分类"的实质正由此保持（本次不改代码、不扩 catch）。`ManualOwnershipConflict`/`SingleDeclarationConflict` 携带真实首行 witness（id/owner/sourceRow/slot）；`_application` 两出口均 `OWNERSHIP_CONFLICT`：typed+proof → `_persist_ownership_detail`（预算预付、指纹去重、分段 blob、admission 单调校验、revision 复验、诊断不在调用方 savepoint 内提交）；裸冲突仅存固定三键。渲染端 `mainline-ownership.ts` 只读分页消费（512 页上限、逐页契约校验、重组绑定 revision，任何不一致 → unavailable），旧裸 detail 按设计不可用。`newManualFactPlan` 客户端按 `SHA-256(JSON[S,P,O])` 派生新 ID 并拒绝 lone surrogate（golden vectors 由真实 Python Store.canonical/digest 生成并双向校验，fixture+单测+O047 六 GUI 含 fresh en-001/de-ch 新增/原 ID 编辑链）；edit/remove 保原 ID。
- **F9（正面核验）安全不变量**：本轮读过的 SQL 全参数化；`material_profile` 表/列名来自 `sqlite_master`/`PRAGMA`（内部源）且 `"` 转义，无外部输入拼接；跨边界错误只传固定码+受限参数（Conflict message 仅内部诊断，注释明示不外发）；preload 仅新增业务命名方法 `getOwnershipConflictDetailPage`，主进程调用后复核 selectionEpoch/owner/projectId/engineSessionId，projectId 强制取 current 而非信任 args；渲染端无 Node/无 innerHTML（本轮 diff 内）。
- **F10（观察，非缺陷）**：e2e 为 3 个声明式测试（四类 CRUD 循环+FR201 原族+canonical 新组）= 6 次运行，与 O047 六 GUI 6 PASS 一致；断言为语义级（原 ID/完整 SPO 精确文本、阻止删除、Diff/Read/Job/marker 绑定），非数量断言，质量认可。`coordinator` 的 `prepare_mainline_store` 引导条件（business3+JobStore+非测试模式+无普通授权/派发）在注释中说明与 Store/lease 原限制同源，逻辑自洽。

## 4. 160 项清单逐项判定

判定词：适用（含已证/部分证于注）/ 部分 / 本轮范围外 / 不适用 / 无法确认。产品定性依据：本地优先单用户 Electron 桌面工作台（无 HTTP 服务、无登录/租户/支付/邮件/云），T02 候选范围=FR-200/FR-201 及其引擎/存储/渲染闭环。

1. 设计过的 schema 而非逐表即兴 — 适用（已满足）：ADR-0002 分层 schema+contracts/v2/schema.json 机器校验；本轮无新表。
2. 邮箱加号登录 — 不适用：无登录/邮箱面。
3. 重置链接过期且一次性 — 不适用。
4. MFA 与丢失恢复 — 不适用。
5. 会话超时与全员下线 — 不适用：无服务端会话；engine 会话由 epoch/generation 生命周期管理（非安全会话）。
6. SSO — 不适用。
7. SAML — 不适用。
8. SCIM — 不适用。
9. 深于 admin/everyone 的角色权限 — 部分：无用户角色；进程能力分离真实（渲染隔离/业务命名桥/_OwnershipProof 仅两方法/require_owner）。
10. 改一个数字读他人数据 — 不适用（单用户）；同类核对存在：服务端强制 projectId、detailRef 绑 proof origin。
11. 租户隔离 — 不适用：单用户本地；项目隔离由 SQLite project 键承担。
12. 管理员代入登录+审计 — 不适用。
13. 登录限流 — 不适用。
14. 不误锁 CFO 的锁定 — 不适用。
15. 迁移前进/回滚 — 部分：actual_format 版本管理存在；回滚迁移框架本轮范围外（B1/后续）。
16. 迁移不锁主表 — 本轮范围外：无在线并发迁移场景。
17. 索引抗规模 — 部分：本轮未新增索引；容量结论属 Q5 HOLD，不设通过线。
18. 连接池 — 不适用：嵌入式 SQLite 单连接。
19. 每夜备份 — 本轮范围外：快照机制非备份策略。
20. 已测试的恢复 — 本轮范围外。
21. PITR — 本轮范围外。
22. 软删除 — 适用（已证）：墓碑保留初始 ID（ADR-0002 实现）。
23. 服务端校验而非仅表单 — 适用（已证）：引擎 term/iri/canonical/schema strict；UI 预检不替代引擎拒绝。
24. 时区存储正确 — 无法确认：无时区语义字段；date/dateTime 按 RDF 词法保留。
25. 姓氏撇号 — 部分：UTF-8 全链+多语料正负例；撇号特例未逐例（风险低）。
26. emoji/重音/RTL — 部分：canonical 按 n3() 词法理论覆盖；未逐例测试。
27. 金额存整数 — 不适用：无金额。
28. 币种/舍入/税 — 不适用。
29. 数据模型抗二次变更 — 适用（设计层已满足）：分层+版本化+ownership/墓碑面向演化。
30. 幂等键 — 适用（已证）：同 operation/job 重试返回原标记不重复写入（ADR-0002+e2e Job/marker 断言）。
31. 四连点去重 — 部分：preview 生命周期围栏+discardPreview 防旧异步覆盖；四连点实测缺（历史保留）。
32. 第 400 页分页 — 部分：游标/ordinal 分页实现；深页未实测。
33. 导出 — 本轮范围外：Turtle 导出属附录 C/FR-203 家族，CRUD 不证明导出。
34. 2009 年 CSV 导入 — 本轮范围外：映射/导入后续（ADR 明示映射计划非 CSV 能力）。
35. 保留期规则 — 本轮范围外：缓存回收不触历史为不变量；具体策略未实现。
36. 密钥不入代码/仓库 — 适用（本轮无新增）：88 叶 diff 无凭据；S3 前引擎无密钥。
37. 轮换 AI 粘贴的密钥 — 本轮范围外：无已入库密钥。
38. 确认每个包存在且如愿 — 适用（已证）：vendor 四轮+upstream+PROVENANCE+补丁+repack 脚本+uv.sources 指向。
39. 依赖扫描 — 部分：Dependabot weekly 在（历史）；本轮未新扫，不称安全审查完成。
40. 输入净化 — 适用（已证）：TermInputError/canonical/iri；错误不回传原文。
41. SQLi/XSS/CSRF/OWASP — 部分：SQL 全参数化（本轮触及面）；React 文本渲染无 innerHTML；CSRF/网络面不适用（无 HTTP）。
42. 文件上传扫描 — 不适用：本 FR 无上传。
43. CORS — 不适用：不开端口（不变量）。
44. 每响应安全头 — 不适用（无 HTTP）；CSP 单源 csp.ts 保持。
45. 静态/传输加密 — 本轮范围外/部分：本地 SQLite 未加密（本地优先设计决定）；stdio 本机 IPC。
46. 最小权限（含 AI agent）— 部分：架构不变量已定（Agent 白名单/不自动确认/引擎无密钥）；本轮无 Agent 接线。
47. 日志记录行为且不含敏感值 — 适用（已证于触及面）：job_details 固定键、错误无原文/路径/凭据。
48. 渗透测试 — 本轮范围外：未做；公开发布前建议保留。
49. 安全问卷 — 本轮范围外。
50. 漏洞披露流程 — 本轮范围外：无公开接收渠道。
51. 笔记本被盗预案 — 本轮范围外：本地数据无加密/远擦。
52. SOC 2 — 不适用（现阶段无云/企业交付）。
53. HIPAA — 不适用。
54. BAA — 不适用。
55. 查看审计 — 部分：操作/详情持久化变更轨迹；"查看"审计在单用户本地非需求。
56. PCI — 不适用。
57. GDPR 删除 — 不适用（在线多租户/处理者场景）；组织法律身份与控制者—处理者关系不能由代码或单机架构认证，本轮范围外/无法确认，法律 HOLD 不变（Z-A05 修订）。
58. 数据驻留 — 不适用。
59. 季度权限复核 — 不适用。
60. 环境一致性 — 部分：CI 三平台与本地 macOS 有差（Windows 证据缺=F1）；CSP 两变体单源。
61. 基础设施即代码 — 不适用：本地桌面；ci.yml/锁文件即配置事实源。
62. 部署前跑测试 — 适用：ci.yml 全链；当前本 head 未跑（F1 门禁）。
63. 一键回滚 — 本轮范围外：无部署回滚面；分支策略承担。
64. 零停机部署 — 不适用。
65. 功能开关 — 不适用。
66. 自动扩缩 — 不适用。
67. CDN — 不适用。
68. DNS/SSL 续期 — 不适用。
69. 后台任务队列 — 部分：job_store 队列/lease/终态（进程内）；无分布式需求。
70. 带退避重试 — 部分：job 幂等重试已证；退避细节无法确认。
71. 死信队列 — 不适用：本地失败即终态记录。
72. cron 不双跑 — 不适用。
73. 缓存与失效 — 适用（核心已证）：invalidation-v2/staleReason+同事务过期+九行正负例；GUI 编辑→四具名下游未逐类联验（F7/D10）。
74. SPF/DKIM/DMARC — 不适用。
75. 退信处理 — 不适用。
76. 临时文件存储规则 — 部分：快照/证据文件本地管理；无自动清理承诺。
77. 成本告警 — 不适用（无云成本；模型支出 S3 后）。
78. 年度 DR 演练 — 本轮范围外。
79. 第二区域 — 不适用。
80. 可检索结构化日志 — 部分：引擎 JSON 协议+证据目录结构化；无集中检索。
81. 错误聚合 — 不适用（无遥测）。
82. 外部拨测 — 不适用。
83. 告警调优 — 不适用。
84. 延迟/错误率仪表盘 — 不适用。
85. 跨服务 tracing — 不适用（单机）。
86. 值班 — 不适用。
87. runbook — 部分：docs 树承担知识库；运维 runbook 阶段不适用。
88. postmortem 改变什么 — 部分：round 处置/证据归档即复盘机制，已多次改变候选走向。
89. 状态页 — 不适用。
90. 懂逻辑者写的单测 — 适用（已证）：3719 PASS/50 有据 skip（O047 同 head）；抽读断言语义级。
91. 第三方 API 集成测试 — 部分：无外部 API；TS↔引擎真实子进程单测+golden vectors 承担对应面。
92. 关键流程 e2e — 适用（已证）：真实 Electron 6 运行 6 PASS（O047 同 head/新构建）。
93. 上线前压测 — 本轮范围外：Q5 HOLD 明确不设容量通过线。
94. 类生产测试数据 — 部分：代表样例/G-base；无生产数据（未发布）。
95. 回归测试 — 适用（已证）：golden vectors、AST 等价、binding-regressions、旧反例保护（45f64 不合并）。
96. 旧设备测试 — 部分：CI 矩阵；参考设备/macOS15/Win11 HOLD 保留。
97. 无障碍合规 — 部分：aria-label/role=alert/status 在；完整 WCAG 无法确认。
98. 订阅/升降级/按比例 — 不适用。
99. 催付 — 不适用。
100. 带 PO 发票 — 不适用。
101. 销售税/VAT — 不适用。
102. 退款/抵扣 — 不适用。
103. 用量计量对账 — 不适用。
104. 年度定制合同 — 不适用。
105. 财务对账报表 — 不适用。
106. webhook 验签 — 不适用。
107. webhook 重试留痕 — 不适用。
108. 版本化 API — 部分：contracts v2+target_format 2/3 版本化；无对外 API。
109. API key 创建/吊销 — 不适用。
110. API 限流 — 不适用（无公共 API）；引擎内 budget/limits 即资源限流对应物。
111. 第三方 API 变更预案 — 部分：vendored rdflib 锁定+透明补丁主动隔离上游变化；pyparsing/pyshacl 精确锁定。
112. OAuth 刷新 — 不适用。
113. 客户集成沙箱 — 不适用。
114. 提示注入防护 — 本轮范围外：S3 前无模型接入；白名单/不自动确认已入不变量。
115. 客户数据不入外发提示 — 本轮范围外：无外发。
116. 按客户模型花费上限 — 本轮范围外：无调用；"不新增付费"约束在案。
117. 模型更新 evals — 本轮范围外。
118. 供应商宕机降级 — 本轮范围外。
119. 模型弃用预案 — 本轮范围外。
120. 提示/输出日志（合规裁剪）— 本轮范围外。
121. AI 不可逆操作的人工批准 — 部分（设计已内建）：Agent 只草稿、人确认；本轮无 Agent 动作。
122. 弱网加载 — 不适用：无网络依赖。
123. 空/加载/错误态 — 适用（已证）：reading/unavailable/ready、忙碌禁用、role=status/alert。
124. 可行动的错误文案 — 适用（部分已证）：OWNERSHIP_CONFLICT 定位视图+行动建议+输入保留；部分仍固定码。
125. 校验失败保留已输入 — 适用（已证）：错误路径不重置表单（"已输入内容保留"）。
126. 邮件客户端渲染 — 不适用。
127. 可关闭通知 — 不适用。
128. 撤销 — 部分（Z-A03 修订）：撤销入口已存在——`OntologyMainlinePage.tsx:401–404`"预览撤销本次修改"→`session.prepareUndo()`；`mainline-session.ts:393–400` 为真实预览入口：新读基准、intent=undo+targetOperationId，不做本地反向 Diff，UI 明示"读取新基准、展示完整影响、再次确认"。本组六 GUI 未实际执行 Undo；Undo GUI/HOLD 不变，不据此判 FR-804 全条通过，也不写"无撤销 UI"。
129. 键盘导航/读屏 — 部分：语义标签在；全键盘路径无法确认。
130. 翻译与本地格式 — 部分：界面中文（目标用户）；locale 格式化未做。
131. 后退按钮符合预期 — 无法确认：应用内导航语义本轮未验。
132. 人能读的代码 — 适用：本轮阅读面注释克制、命名与模块边界清晰。
133. 每次变更代码审查 — 适用（已证）：指定双模型独立审查流程运行至 R07，处置留痕。
134. 分支策略 — 适用（已证）：独立 worktree+feature 分支+base 记录+PR 门禁。
135. 月度依赖升级 — 部分：Dependabot weekly 在；本轮精确锁定不变。
136. 框架停更前升级 — 部分：Python3.12.12/rdflib7.6.0/Electron 锁定；升级策略无法确认。
137. 删除死代码 — 部分：本轮 diff 未见新死代码；全仓扫描未做。
138. 拆分超长文件 — 部分：e2e spec 1748 行、mainline.py 1206 行；结构化组织，维持"不据 LOC 推正确性/不强制重构"。
139. 写下架构决策与理由 — 适用（已证）：ADR-0001/0002/0003+M0 计划。
140. README 一小时上手 — 无法确认：存在 README；未实测新人上手。
141. 交接文档 — 适用（已证）：docs 树完整（PRD/ADR/迭代/评审/status/清单）。
142. 运维管理面板 — 不适用。
143. 客服工具 — 不适用。
144. 客户可读 changelog — 部分：status/m0 追加式记录；客户面不适用阶段。
145. 条款/隐私与代码一致 — 本轮范围外：未发布；法律 HOLD 保留。
146. 账号/域名/仓库在公司名下 — 无法确认：组织产权不可由代码认证。
147. 巴士因子>1 — 部分：控制器+双模型审查+文档化降低单点；人员维度无法确认。
148. 上线前高级工程师逐行读 — 部分（Z-A06 修订）：指定双模型独立审查+ROOT 自动总控（Codex 自动流程，非人类）逐项处分留痕，承担大部分工程核对职能且有实际价值；但人类逐行审读与人类签字放行未证，不假定已完成、不冒充人类证据；"每一行"不可计量。
149. 后端先设计数据模型 — 适用（已满足）：ADR-0002 设计驱动（对应第 1 项）。
150. 解释 AI 修复引入两个新问题 — 部分：round 处置/AST 等价/精确 diff 机制即该职能实例。
151. DevOps（部署/回滚/云账单）— 部分：CI 三平台+打包验证承担；无云面。
152. 凌晨 3 点响应 — 不适用。
153. 漏洞公开周内补框架 — 部分：vendored 补丁+锁定使上游补丁可控；响应流程无法确认。
154. 向审计者讲解数据流 — 不适用（受监管场景未确认，Z-A05 修订）；角色不适用不消解对实际数据流/来源/权限边界的说明责任：已有链路（引擎/存储/渲染闭环，见 §1/§3）与未验事项（F1、F7）已分开披露。
155. 测 AI 声称测过的 — 适用（已证）：O041/O042/O047 独立执行与读回分离；本轮本人重算（AST/TOML/glob/哈希/ls-remote）亦此职能。
156. 在线库迁移不丢行 — 本轮范围外：无在线库；同事务原子提交已证。
157. 技术负责人否决破坏性功能 — 部分：AGENTS 门禁/不扩功能/D8 四禁止为制度化"说不"；有效性由控制器保证。
158. 从"我机器能跑"到"所有客户同时可用" — 不适用（在线多客户并发场景，Z-A05 修订）；单用户事实不能证明目标 OS/参考设备/多环境可靠性：Windows（F1）、参考设备/macOS15/Win11 与容量 Q5 各自 HOLD 保留，不全挪给 Q5。
159. AI 调不通时人调试 — 部分：多轮 fix-review 循环实证（45f64 弃用、cb8/8318 修复链）。
160. 一年后记得为何这样建 — 适用（已证）：ADR 理由+逐轮处置+本报告。

## 5. Top 10 最值得修复/跟进项（按优先级）

1. **F1 Windows 完整验收缺口**：b215 push 后须真实 CI 三 job 全 success（Windows 3769 全集逐项 pass/原有据 skip、无失败/早停/取消/timeout/NOTRUN，后继 typecheck/build/E2E/package/verify，Quality packaged recovery 步骤自身 success）——合并门禁，非源码缺陷。
2. **F2 formatter 排除面按名枚举**：未来新评审模型 raw 文件名若不匹配 literal 且该 Markdown 含需改写的可解析 Python 围栏，才会再触 format --check（单纯名字不匹配不必然失败，Z-A09 修订）；约定新候选追加 literal（不建议现在放宽 glob）。
3. **F3 write_text 编码规约**：20 处无显式 encoding 的调用点在未来引入 Unicode 载荷时必须同步修复；建议写入贡献约定。
4. **D3 definitions 早期坏 wire（OPEN）**：T01 原始 triples/Agent 接线前处理，UNKNOWN/HOLD 语义保持。
5. **D6 standalone 裸 EOF 索引（OPEN）**：不泛捕 IndexError；新增不经封装的 parser 入口前复核。
6. **D7/P5 缺 16 错误码（延期）**：对应方法接线前补针对性证据，不一次性泛加白名单。
7. **P6/D5 witness 选取无 ORDER BY（未确认观察）**：T01 下次触及 witness 选取时核确定顺序。
8. **D8 两 TS PATH python**：`t01-ontology-metadata-contract.test.ts:168`、`t01-mainline-contract.test.ts:656`；下次授权触及或新环境适配前处理。
9. **D10 FR200 GUI→四具名下游失效未逐类联验**：父 FR/消费链整体验收前逐项（推导/保存查询/SHACL/报告）。
10. **发布前 HOLD 群**：签名/公证/wholeApp 法律/_distutils、参考设备/macOS15/Win11、Q5/D2 容量、损坏 SQLite 物理保护、Undo GUI 实际执行、未知退出码——公开发布前必须逐项处置。

## 6. 历史意见逐位置现状（Z-A01 修订：55 位置逐行可追踪）

前提（Z-A10 精度）：凡"pytest NOTRUN"均指完整 3769 项引擎 suite 在 O046 该 run 三 job 均 NOTRUN；同 run Quality 此前的专项 I04 pytest 144 PASS/21.89s、TS 39 文件 1892 PASS 及 typecheck/build 是实际运行过的前置步骤，原件保留——不得概括为"所有 Python 未跑"或"这些前置未跑"；该区别不是新执行/新 CI 通过，更不是 b215 已 CI。R06 双方结论（Z ConditionalPass / MM verification-incomplete）不继承为本版通过，本判词独立形成。原证据位置统一指向 `round-06/disposition.md` 对应小节（R06 Z 表 / R06 MM 表 / 历史 35 意见表）及双方 R06 terminal 报告（`round-06/version-map.json` 针定）；下列 55 行为位置现状，不是 55 个缺陷或开发任务。

R06 Zcode P1–P8：

1. Z P1 新 head Windows 缺证／旧 79F 全因未证 — b215 仍未 push（ls-remote 实证远端 330）＝F1 — 采纳·合并门禁 — ROOT 正常票/push 后真实 CI — disposition R06 Z 表。
2. Z P2 诊断参数与完整验收 — ROOT 全集口径维持；`--maxfail=1` 仅失败早停无筛选；不以 diagnostic 标签验收（O046 精度见前提）— 维持 — ROOT 证据接收标准 — 同上。
3. Z P3 definitions 早期坏 wire — b215 未触及；早期 preview 内 Store 校验未分类异常 — 保留 OPEN（UNKNOWN/HOLD）— T01 核心维护，原始 triples／Agent 接线前 — 同上。
4. Z P4 ownership 通用定位 — typed 两族 witness＋裸 detail unavailable、`_application` 两出口均 OWNERSHIP_CONFLICT 已核 — 限定延期 — T01 详情合同＋T02 消费，对应家族接线前 — 同上。
5. Z P5 错误码集合差 — 契约 26／UI 17／交集 10／额外 7／缺 16 集合事实维持，未证 16 条当前可达 — 延期 — T01 契约＋T02 方法出口接线前 — 同上。
6. Z P6 SQL 无 ORDER BY — SQL 事实＋未确认观察维持，未构造跨运行反例 — 下次触及 witness 选取 — T01 Store — 同上。
7. Z P7 canonical — 精确 term(value).n3() 代码核实保持；正控／混合大小写受控拒绝分开；未来改政策才新人类决定 — 维持 — T02/ROOT — 同上。
8. Z P8 规模／EOF／边界／状态／PATH — 逐项见 D6/D8 及对应行，不集合化 — 维持 — 各归口 — 同上。

R06 MiniMax D1–D12：

9. D1 新 head 未 CI — 合并条件非源码缺陷；b215 同（远端 330 实证）— 维持 — ROOT/CI 后合并前 — disposition R06 MM 表。
10. D2 状态／历史 manifest — 330 追加节本方核过为追加式、历史身份不改写 — 维持 — ROOT 指定唯一文档维护者，归档票后追加 — 同上。
11. D3 definitions 时序 — preview 内 Store 先抛实证；早期坏 wire — 保留 OPEN — ＝Z P3，T01 接线前 — 同上。
12. D4 ownership 最终码 — 两出口 OWNERSHIP_CONFLICT 核实；裸旧 detail unavailable 成立 — 限定延期 — T01＋T02 家族接线前 — 同上。
13. D5 无序查询 — 未确认观察 — 维持 — ＝Z P6，T01 下次触及 — 同上。
14. D6 standalone 裸 EOF 索引 — 两处残余在；当前 term 封装未构造可达反例 — 保留 OPEN、不泛捕 IndexError — T02 vendor 补丁／T01 入口，新增不经现封装 parser 入口前 — 同上。
15. D7 缺 16 码 — 集合事实非 16 条可达缺陷 — 延期 — ＝Z P5 — 同上。
16. D8 两 TS PATH python — 本方定位仍在：`t01-ontology-metadata-contract.test.ts:168`、`t01-mainline-contract.test.ts:656` — 维护 — T01 测试维护者，下次授权触及／新环境适配前 — 同上。
17. D9 Ruff 计数分层 — O046=386 目标（385 already＋1 would）→ O047=379 formatted（386−7 排除后），两计数自洽；无差因结论 — 维持 — 文档唯一维护者 — 同上。
18. D10 D/E/G 与失效联动 — 公共失效＋九行正负例既有；四具名下游 GUI 未逐类联验（§1 闭包映射补强）— 分层维持 — T01 公共失效＋T02 编辑＋各下游 owner，父 FR／消费链验收前 — 同上。
19. D11 4299/4300 — 应用边界断言未来维护；4301 拒绝＋合法后继已证；vendor 边界≠应用边界 — 维护 — T02 输入边界，下次授权触及整数守卫 — 同上。
20. D12 正面结论有界 — 六 keyword AST 本方独立复算成立；不外推全部安全／全平台／法律 — 资格保留 — 同上。

R04 Z01–Z07：

21. Z01 无序查询观察未确认 — ＝D5 维持 — T01 下次触及 witness 选取 — disposition 历史 35 表。
22. Z02 分页信封误因果已撤回；262144 整文档／16MiB 预算边界另保 — 撤回维持、边界保留 — T01 详情预算下次授权维护 — 同上。
23. Z03 definitions 早期 wire — 保留 OPEN — ＝D3，T01 接线前 — 同上。
24. Z04 typed／裸 detail 分开 — 维持 — ＝D4，家族接线前 — 同上。
25. Z05 集合差与可达性分开 — 维持 — ＝D7 — 同上。
26. Z06 canonical 既有政策 — 维持 — ＝Z P7 — 同上。
27. Z07 规模信息（2993/1887/1748）— 不新增重构 — 维持 — 同上。

R04 M01–M07：

28. M01 归档演进（待 ROOT→最终追加）不矛盾 — 维持 — ROOT 文档维护 — 同上。
29. M02 无 hash 前提不采；uv/PROVENANCE 审计件保留 — 本方核四 wheel＋upstream＋补丁＋PROVENANCE 均在 — 维持 — T03/T02 vendor — 同上。
30. M03 4299/4300 未来维护 — 维持 — ＝D11 — 同上。
31. M04 standalone 残余 OPEN 未证 UI 可达 — 维持 — ＝D6 — 同上。
32. M05 早期 definitions 不受后置 catch 覆盖 — 维持 — ＝D3 — 同上。
33. M06 schema 形状与 Store 内容身份分层 — 双端 ID 校验／原 ID edit 证据在，非当前绕过漏洞 — 维持 — T01 契约 — 同上。
34. M07 桶导出兼容信息 — 未证冲突 — 维持 — 契约 owner 下次 API 整理评估 — 同上。

R05 Z P1–P8：

35. R05 Z P1 O040 首败定因／不追认旧 79 全因 — 维持；b215 Windows 缺＝F1 — ROOT 合并门禁 — 同上。
36. R05 Z P2 934 Quality 718s（含 recovery 成功）新阶段证据／旧 CI36 取消留历史 — 维持，不迁移成新 CI 绿 — 同上。
37. R05 Z P3 早期 definitions — 保留 OPEN — ＝D3 — 同上。
38. R05 Z P4 通用定位合同 — 维持 — ＝D4 — 同上。
39. R05 Z P5 缺 16 按出口延期 — 维持 — ＝D7 — 同上。
40. R05 Z P6 canonical 语义观察 — 不新增当前批准 — 维持 — 同上。
41. R05 Z P7 当时有效 pytest 诊断选项已变／规模信息 — 维持（O046 步骤中实际 PYTEST_ADDOPTS 在案）— 同上。
42. R05 Z P8 历史 aff 状态永久保留／当前时点按归档票追加 — 维持 — ＝D2 — 同上。

R05 MM01–MM13：

43. MM01 首败假设被 O040 一个真实栈部分超越／旧 79 全因未知 — 维持；新 CI 门禁保留 — 同上。
44. MM02 934 两 success／一 failure 新阶段事实／旧两 cancelled 不抹除 — 维持 — 同上。
45. MM03 无新包／原 094 有界桥接 — b215 亦无新包制造 — 维持 — 同上。
46. MM04 当前入口追加与 Ruff 差因未知分开承接 — 维持 — ＝D2/D9 — 同上。
47. MM05 缺码非阻断延期 — 维持 — ＝D7 — 同上。
48. MM06 definitions 早期 OPEN、不采晚确认分歧 — 维持 — ＝D3 — 同上。
49. MM07 Manual/SingleDeclaration 真 witness 与裸族分开 — 维持 — ＝D4 — 同上。
50. MM08 SQL 事实维持未确认观察 — 维持 — ＝D5 — 同上。
51. MM09 整 wheel／payload／解压量及压缩方式分层 — 本方核 fr201.x 全 STORED／upstream deflate 615416B — 维持、保历史 vendor 原件 — 同上。
52. MM10 AGENTS 为保护的未提交 overlay、链接维护非候选产品缺陷 — 维持（15147B/`de15f6ce` 核过）— 同上。
53. MM11 locator 无 object 为最小定位信息边界 — 维持不新增显示需求 — T02 消费 — 同上。
54. MM12 两 TS 仍 PATH python、报告更正≠源码修复 — 维持（本方定位仍在）— ＝D8 — 同上。
55. MM13 核心规模信息不据 LOC 推正确性 — 维持 — 同上。

## 7. 最终整候选判词（base 583c05c7 → b215f543）

- **结论：附条件通过（ConditionalPass）。**
- **本地实现及验收：通过（限定）**——FR-200/FR-201 候选范围内（四类 CRUD+层级/domain/range/type/五组 metadata、结构定义与实例事实语义分离、canonical 输入政策、ownership 冲突定位、事务幂等/Diff/确认/Job/marker）实现成立；本地证据：O047 同 b215 head/tree 一次 `npm run check` 自然 0（TS 39 文件 1892 PASS、Python 3769 收集/3719 PASS/50 有据 skip/1 原 warning、Ruff 379 formatted）+ 原六 GUI 6 PASS（新构建、57 事务/43 拒绝/58 body 已由独立结果审查与 ROOT 直核）。该"通过"不外推全部附录 C、父 FR 全条、Undo GUI 实际执行（入口已存在、本组六 GUI 未实测）、四具名下游、其他 OS 或打包面。
- **push 前技术阻断：未发现**——b215 相对 330 仅 format exclude 一行；本人独立核验其对 330 attempt2 实证唯一 CI 阻断点（raw 报告 Python fence）的覆盖恰为 7 份 tracked 文件，且不改任何受审实现/测试/依赖/CI 命令。R06 双作者"无 push 前技术阻断"的判断与本人独立结论一致（非继承）。
- **必须等 push 后真实 CI 才可 merge**：Windows 3769 全集每项最终 pass 或原有据 skip、自然 0、无失败/早停/取消/timeout/NOTRUN；Windows 后继 typecheck/build/E2E/package/verify 与三 job 实际 success；Quality packaged recovery 须步骤自身 success。在此之前不得合并（远端 feature 仍 330、develop 583、PR16 open，本人 ls-remote 实证）。
- **边界重申**：本报告不新增 FR、不解除任何具名 OPEN/HOLD、不把缺少尚未 push 产生的 CI 写成源码缺陷、不提前预判未来 CI 会绿；合并可用状态仍 2/17（FR401/402），Goal/M0/发布未完成。未发现缺陷的面（如本报告第三节 F8–F10 正面项）也已写明证据界限。
