# T01 package085 @ 7d30 累计（develop→head）指定独立完整工程审查报告（ZCode / GLM-5.3）

- 报告角色：本方（ZCode）指定独立审查，未读取另一模型本轮任务/报告（`../minimax/` 全程未打开）。
- 审查对象：OntoLearn Studio，本地优先桌面软件（Electron + Python stdio 引擎 + SQLite）。
- 产品实现严格只读：本审查仅使用只读 git / shasum / grep / 文件读取；未修改任何源码、测试、配置、标准、Git 索引；未运行新 build / GUI / APP / 打包 / 外部请求（除任务书明示要求的只读 `git ls-remote origin develop`）。唯一写入物为本报告文件。

## 0. 受理身份回读（任务书第 15 行要求）

| 项 | 要求 | 实测 | 一致 |
| --- | --- | --- | --- |
| prompt.txt | 16488 B，SHA256 `b2d80634…e89488`，读到 EOF | `16488 bytes`；SHA256 全匹配；187 换行/末行无换行符，Read 至末行（"remembering why it's built this way, a year from now (someone who was there)"）确认 EOF | ✅ |
| 项目绝对路径 | `…/本体/.worktrees/T01-project-transactions` | 一致 | ✅ |
| Git authority | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | `git rev-parse --git-dir` 一致 | ✅ |
| HEAD | `7d30ab34b59d696b40df9d6d959d3626612f4423` | 一致（分支 `feature/weekly-t01-project-transactions`） | ✅ |
| 远端 develop（只读 ls-remote） | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `refs/heads/develop` = 5f910b52…，且为 HEAD 的直接 merge-base | ✅ |
| 审查范围 | base→head 完整累计 525 files | `git diff --name-only` = 525；36 commits；+560720/−4638 | ✅ |
| AGENTS.md | 15147 B / SHA256 `de15f6ce…56a5c8c4`，受保护未暂存，不得修改 | 哈希与字节数全匹配；工作区状态仅 ` M AGENTS.md`（owner 规则，未触碰） | ✅ |
| Provider / Model / 思考 / 权限 | Start Plan / GLM-5.3 / 最高思考 / 完全访问 | 会话环境：`account:bigmodel-start-plan/GLM-5.3`；本审查全程无权限拒绝，实际完全访问（与用户 2026-10-21 授权的 yolo/bypass 口径一致）。本行仅为环境回读，不构成对审查深度的额外声明 | ✅（观察） |
| 清单 | 11255 B 原文逐项 | 已全量读毕并逐类判定（见 §5） | ✅ |

源码权威性：以 whole085 的 `S-source-after-commit.json`（1270 闭集）为准，本人抽查 8/8（含 AGENTS.md、engine.ts、transactions.py、storage.py、coordinator.py、workspace-controller.ts、v2.ts、registry.json）SHA256 全部匹配——worktree 源与 7d30 提交后闭集一致，未被篡改。N 侧临时 checkout（native Git UNBORN）不作为源码 authority，本审查未依赖它。

## 1. 总体结论（先行）

1. **本次审查在受核产品代码范围内未发现新的阻断级缺陷**（数据丢失、静默损坏、越权、注入、凭据泄露类：均未发现，且多处设计显著强于常规水准，见 §3）。
2. **合并与发布流程层面仍存在既定阻断，且历史失败/HOLD 一律不清零**：本候选未推送、未 PR、未 CI、未合并、未远端复核；用户 0/17 口径不变；签名/公证、全 APP legal/_distutils 来源、跨平台/参考设备、损坏 SQLite 物理 HOLD、D8 人工裁决（888ac 决策书待用户选 A/B）、C4–C6 三次配对失败已达熔断门、47 阶段指定双审 0 通过——全部留账（§6）。
3. **原生验收中引擎 ChildProcess exit/close `UNKNOWN_NOT_OBSERVED` 的独立判定：不构成产品代码阻断，但证据义务未履行**。代码存在双退出路径（SIGTERM 优雅停机 + 父进程退出导致 stdin EOF 兜底）+ query worker terminate→宽限→kill + flock 写租约在进程死亡时由 OS 自动释放；剩余风险仅在"引擎活体挂起但未死"场景（会以 `leaseBusy` 拒绝下一次引擎启动，无 UI 自愈提示）。不得以有限 PID 采样洗绿，仍需补观测证据（详见 Top1）。
4. 下列证据链本人独立回读并采信为"实际发生"：whole085 单次完整 `npm run check` 自然退出 0（141.96s；TS 35 文件 1691 通过；Python 3445 通过 44 skip；ruff/format 在同一退出 0 的命令链内——文件级 332 计数本人未单独复核）；e2e085-002 实际 18 collected / 16 pass + 2 个 macOS 平台条件 skip、全部入口进程自然 0；SOURCE005 三在途模式（reload / renderer-recovery / coordinator-exit）`faultApplied=true` 且 PASS；native 真实 CUA 对话框 0/0/1 + 真实 Cmd-Q，`before-quit(seq4)→第三窗口 closed(seq5)→will-quit(seq6)` 顺序成立；package085 为 whole085 JS + 复用真实 888 引擎产物（`newJSBuildExecuted=false`、`newEngineGenerationExecuted=false`、`engineReuseNotNewEngineBuild=true`），非本次重建 engine。

## 2. 实际已核范围 / 未核范围

**本人亲读代码**（关键行号在后文引用）：`apps/desktop/src/main/index.ts`（全文）、`engine.ts`（生命周期/监督/杀停段）、`preload/index.ts`、`packages/engine/.../coordinator.py`（serve/SIGTERM/stdin 段全文）、`job_store.py`（marker/commit/reconcile/confirm 段）、`storage.py`（迁移/备份/事务段）、`project/transactions.py`（全文）、`project/compensation.py`（全文）、`project/project_lifecycle.py`（创建幂等段）、`project/format3.py`（acquire_lease）、`invalidation-v2.json`、`csp.ts` 语义（经代理复核原文）、CI/SECURITY/README/m0-checklist/tasks.json/T11 root acceptance 关键字段。
**代理面状侦察（只读 Explore，行号引用均回贴于报告）**：renderer ontology/ 与 query/ 全模块地图、安全十项扫描（SQL 354 处调用点逐一分类）、docs/iteration-control 开放事项枚举。
**证据文件**：whole085（ENTRY/FINAL/check 回单/S-source）、package085（ENTRY/package-readback/控制器验收）、e2e002 ENTRY、runtime001 ENTRY/ACTUAL-RUNTIME-RESULTS 四模式全文。
**未核/无法确认**：307 个 `docs/reviews` 过程文件仅抽样台账未逐字读；332 个 Ruff 文件计数未单独复核（仅信退出 0 命令链）；Windows/Linux 真机与参考设备实测（未发生）；五龄老设备性能（未发生）；G-base/G-map-empty/G-behavior/E.5 容量基线（m0-checklist 明示未生成）；签名/公证（未执行，decision D5 明示本轮不做）；真实 LLM 相关项（S3 未接入，代码中无模型客户端——已核为"不存在"而非"未测"）；`docs/prd` PRD 附录逐条对照（未全文重读，仅引用 m0-checklist 既有追踪）。

## 3. 关键边界独立追踪结论（任务书指定的五条边界）

### 3.1 项目创建 / 示例复制 / 补偿 / owned draft / 重启
- 创建是显式应用事务：`project_lifecycle.py:426-540` `commit()` 要求 format3 + 全新 uuid4 项目 + 多表 uuid 碰撞检查 + genesis 复核（`require(genesis == candidate["before"])`）+ 用**已验证的实际 genesis 重建 candidate 再落 claim**（:508-517）。**幂等**：`operation_claims` 命中且 request/origin 全等 → 原样返回旧回执，不产生新 CAS/预算身份（:458-470）——重试不会复制项目。
- 示例复制：`model(project, request, origin, library_evidence(store))` 从内置 library 证据构造；example root 由主进程唯一指定（`index.ts:241-250`，打包内 `resources/examples/...`），无存在性搜索回退。
- 补偿：`compensation.py` 纯函数、零 SQL 写入；undo/restore selector 要求真实不可变 commit 证据（`trusted_snapshot` 校验 commit_evidence 关联 + 映射快照 stale 一致性 :45-70）；`retirement_at` 从不可变历史重建撤销面，"Legacy missing evidence is not guessed"（:77-91）；ABA 防护显式（:170-188 先查 later edits 再判冲突）。
- owned draft：草稿属 owned 会话（`mainline.py:1` "owned business3 stdio session"），渲染层书签 `pendingBookmark` 保留 `preservedDraft` 且 65536B 上限（`mainline-recovery.ts:52-82`）；书签**无重试授权**（confirmationRef 永不重放，:31 注释）。
- 重启：引擎侧 `job_store.py:1924-1951` `reconcile_jobs()` 在取得 OS 写租约后，非终态 Job → cancelled/failed(ENGINE_EXITED, retryable)，"marker alone can never invent success"；渲染侧 `recoveredPending` 重新入账 → `reconcile()` 用 getOperation marker + getJob + 有界 listJobs（≤32×100）收敛，未定论停在 `unknown` 相位（"null 不是未发生的证明"，`mainline-session.ts:749`）。
- **判定：该边界实现与验收证据一致，未发现缺陷。**（观察）

### 3.2 T02 ontology 完整 diff / commit / undo / redo
- 完整 diff：分页拉取（页 32 段、≤512 轮、≤16MB、≤32KB/段）+ 段 sha256 + ordinal/byteOffset 连续性 + 整文档 sha256 + 严格 UTF-8/代理对校验（`mainline-diff.ts:16-124`）；确认按钮只在全部行展示后可用（`OntologyMainlinePage.tsx:281-290`）。
- commit：三次 currency 检查（getActiveProject，`mainline-session.ts:459/476/502`）→ 确认游标 → **先 CAS 写书签后进域写**（:486-501）→ commit → Job 绑定校验 → reconcile。引擎侧 `transactions.commit` 幂等（marker 命中且身份匹配 → 返回既有 marker，:214-216），前置/后置状态与预览逐字节比对（PREVIEW_RESULT_MISMATCH :235-239）。
- undo：**服务端补偿性新事务**（`intent='undo'` + 全新 base 读取，`transactions.py:253-283`；渲染层 "never an inverted local diff"，`mainline-session.ts:386`）；冲突面逐资源比对（UNDO_CONFLICT 携带资源名）。
- **redo：不存在独立 redo**。引擎 `preview_undo` 可作用于任何有证据操作（含 undo 自身 → 语义等价 redo），但 UI 唯一入口 `prepareUndo()` 无参、固定取**当前回执**的 operationId（`mainline-session.ts:382-390`、`OntologyMainlinePage.tsx:330`），无操作历史选择器。→ Top3。
- **判定：diff/commit/undo 实现与 e2e（`t02-ontology-mainline.spec.ts`、`mainline-consumer-first-ack-loss.spec.ts` 首测试）一致；redo 为真实功能缺口。**（观察）

### 3.3 T04 查询 / 分页 / 历史快照 / 导出
- 查询执行走持久 Job；断言+derived 作用域被硬拒绝（`QueryWorkspacePage.tsx:155-157` `ASSERTED_DERIVED_UNAVAILABLE`）。
- 分页：服务端 UUID cursor + 绝对 startIndex，页大小固定 200；显示层 zod 校验 ordinal 连续、`end ≤ rowCount`、`nextCursor⟺还有行`（`typed-results.ts:175-243`）——深页无 offset 退化，"page 400" 场景不劣化。执行文本按 UTF-8 字节区间 32KB 分页并做再编码往返校验。
- 历史快照：`listJobs` 固定 `listSnapshotId` + 严格单调 `createdAtMs+jobId:asc` 验证（`workspace-controller.ts:1260-1281`）；`restoreQueryResult` 只读恢复、"未重新执行"（noReplay，:1294）。
- 导出：**仅 CSV、仅当前页（或单 ASK 值）**，含 BOM/CRLF/CSV 注入防护（前导 `=+-@`/制表符加 `'` 前缀，`typed-results.ts:252-266`）——无全量导出、无 JSON/XLSX。→ Top4。
- **判定：查询/分页/历史快照实现一致；导出为真实覆盖缺口。**（观察）

### 3.4 首次 commit ACK 丢失：原操作对账 + 项目切换隔离
- e2e `mainline-consumer-first-ack-loss.spec.ts:256-460`：在主进程插桩丢弃**首个**消费侧 reply，断言 `commitCalls===1、executeCalls===0、lostAckCalls===0`，UI 进入"原操作状态"，经"核对原操作与提交回执"收敛到已提交回执——**无二次提交、无重放**；query 消费者第二测试断言"以完全相同 intent 恢复且只有一个 Job"。
- 切换隔离：`query-draft-switch.spec.ts:182` "hash-pending A 草稿不得跨入 B；原操作仅在保留的 A 中重试"（`released=false`、B 状态逐字节不变、A 草稿原样保留）；`ontology-switch-preflight.spec.ts:107` "预检 reply 不得在 UI 已切到同版本 B 后启动 A 写"（`held.calls===[]`，实际读取返回 A）。
- 引擎侧权威：marker 与 receipt/terminal 同事务落库（`job_store.py:1937-1939`），`transactions.reconcile` marker 缺失 → `uncommitted` 且**永不授权自动重试**（:181-184）。
- **判定：实现一致，边界质量高。**（观察）

### 3.5 task/engine epoch / 主进程生命周期 / 权限 / 持久 Job / marker / noReplay / 引擎退出监督
- epoch：supervisor generation + 引擎 hello `engineSessionId`；同代才 `#current`（`engine.ts:2037-2039`）；重启窗口 60s 内 ≤5 次且指数退避（:2060、:2106-2107）；`reconcile_jobs` 的"Same lifetime lease; no old worker can commit"（`coordinator.py:1118`）完成跨代隔离。
- 主进程生命周期：`before-quit` 同步 dispose 四服务 + `supervisor.stop()`（`index.ts:24-32`）；`stop()` → `#finish` → **立即 `child.kill()`（SIGTERM）**，1s 后升级 SIGKILL（timer unref，`engine.ts:2062-2068`）。
- 引擎侧双兜底：SIGTERM 处理器 → `coordinator.closed=True` → 优雅清理（`coordinator.py:1133-1136`）；父进程退出 → stdin EOF → inbox None → 同一清理路径（:1068-1071、:1154-1155）。清理含 query reply 清账（>16 或未清 → `QUERY_CLEANUP_UNKNOWN` 记失败，不静默）、coordinator.stop、store.close、信号还原、临时目录清理（:1195-1234）。query worker 取消路径 terminate→cancelGraceMs→kill→wait（:927-942）。
- 写租约：`format3.py:128-151` flock(LOCK_EX|LOCK_NB) 于 `<db>.writer-lock`——进程**死亡**（含 SIGKILL）时 OS 自动释放；仅**活体挂起**的引擎会令下一次启动 `leaseBusy`。→ Top1 的风险面。
- 权限：fixture 仅经主进程启动参数（`index.ts:208-236`，renderer 永不可供）；IPC 全部 `trusted(event)` sender/frame/文档三重校验（:317-324）；preload 为闭合命名面（28 个方法，无通用 invoke）；引擎子进程 env 白名单（无继承凭据）。
- noReplay：T04 历史恢复只读；任务侧 `i04-jobs.spec.ts:22-81` 断言 reload 后同批 Job 不新建不取消、generation 递增、stateVersion 单调。
- **判定：除 Top1 的观测证据缺口外，实现一致。**（观察 + Top1 中标注的推断部分）

## 4. 最值得修复的 10 项（按严重度排序；每项区分【观察】/【推断】）

1. **引擎退出监督证据缺口 + 活体挂起引擎可独占写租约（可用性）** —【观察】runtime001：native hook 中引擎子进程 exit/close 均 `UNKNOWN_NOT_OBSERVED`，终态 `ps -p …` 自然退出 1 且无输出，`globalReapClaim=false`；【观察】代码双退出路径成立（见 §3.5）；【推断】剩余场景：引擎在清理/长事务中挂起但未死 → flock 不释放 → 下次启动 `leaseBusy` → 应用不可用且无 UI 指引自愈。建议：(a) 原生验收补 exit/close 观测（引擎退出前落一条退出记录文件亦可）；(b) 主进程把 `leaseBusy` 映射为可操作错误（提示存在残留引擎及处置方法）。严重度：中高（对合并不阻断；对"原生验收完整闭环"义务阻断）。
2. **签名/公证缺失，深度校验失败** —【观察】`package-readback.json`：`allNativeSignaturesVerify=false`、`appDeepCodesign.exit=1`（"code has no resources but signature indicates they must be present"）、`signedReleaseGate=false`、identity null；【推断】任何外部机器分发将被 Gatekeeper 拦截/降信。属既定发布义务（decision D5：本轮明示不签），非代码缺陷，但为对外发布的头号前置。严重度：高（仅在外部分发场景）。
3. **T02 无独立 redo，撤销仅限最近一次回执** —【观察】`mainline-session.ts:382-390`（prepareUndo 固定取当前 receipt）、`OntologyMainlinePage.tsx:330`；引擎已支持对任意有证据操作（含 undo-of-undo）求 `preview_undo`（`transactions.py:253-283`），能力与 UI 脱节。风险：连续误操作只能逐次撤销、无法跳选历史操作点，任务书边界明列 redo。建议：增加已提交操作历史列表 + 对历史操作的撤销入口。严重度：中（功能完整性）。
4. **导出仅当前页 CSV，无全量导出** —【观察】`QueryResultPanel.tsx:16-23`、`typed-results.ts:252-266`（导出边界重校验当前页，"表格与导出仅包含当前页"明示）；rowCount 大时用户无法取得全量数据，无 JSON/XLSX/复制全部。建议：沿服务端 cursor 链做流式全量导出（分批拉取+大小上限+进度）。严重度：中（数据所有权与 FR 验收缺口）。
5. **损坏 SQLite 物理 HOLD：无用户侧修复/导出路径** —【观察】`storage.py:95-101` 对 legacy 损坏 kind 显式拒绝（"explicit repair required"）；iteration-control `execution-state.json` 记录用户 2026-10-22 选择保留 HOLD、B/C 未授权。风险：DB 损坏 → 应用拒启 → 用户数据无法自救（只能手工文件级操作）。属用户保留的产品决策项，需决策后实现一次性导出/修复通道或书面处置指引。严重度：中（数据可用性，非完整性——完整性方向设计是强的）。
6. **无用户级备份/恢复入口** —【观察】数据为单文件 `userData/engine.sqlite`（`index.ts:256`），自动备份仅发生在 v2→v3 迁移时（`storage.py:148-168`，随机名 `.t01-backup-*.sqlite`，保留作证据）；无应用内项目备份/导出、无数据位置文档。`synchronous=FULL`+原子提交+快照保证一致性，但不防磁盘故障/误删整库。建议：项目级导出/备份菜单（可复用 snapshot 机制）+ README/应用内说明数据目录。严重度：中（数据丢失风险，本地优先软件的核心承诺面）。
7. **可访问性缺口：无自定义键盘导航、树形结构无 aria 层级** —【观察】ontology/query 两模块 0 处 onKeyDown/tabIndex 自定义导航；类树为扁平按钮列表，无 `aria-level/expanded`（被动 aria 良好：57 处 role/aria，错误区 `role="alert"`、状态 `role="status"`）。对企业/教育合同构成潜在门槛。建议：补树形 aria 与 roving tabindex、焦点管理。严重度：中低（当前无企业客户义务，提前项）。
8. **i18n 完全缺失** —【观察】无任何 i18n 层，全部文案硬编码简体中文（`index.html lang="zh-CN"`）；`SafeError.messageKey` 携带但从不渲染（`typed-results.ts`/Panel 均直接拼 code）。非中文用户即阻断。建议：先抽文案常量层 + 渲染 messageKey，暂不做多语言。严重度：低-中（由目标市场决定）。
9. **大文件与死代码** —【观察】`job_store.py` 2589 行、`engine.ts` 2578 行（>2000 行清单线）、`storage.py` 1795 行临近；`query/draft.ts` 3 个零消费者导出（alarmTemplate/emptyDirections/savedQuerySchema）；`OntologyPage.tsx` legacy `previewEdit` 路径未接线（唯一宿主走 previewManagedEdit）；`workspace-controller.ts:2`/`typed-results.ts:2` 深路径 import 绕过 `@ontolearn/contracts` 别名。均为可维护性项，无行为风险。严重度：低。
10. **跨平台/参考设备未实测 + 容量基线未生成** —【观察】实测仅 macOS 15 arm64；CI 的 Linux e2e 存在（`ci.yml` xvfb+openbox+原生恢复矩阵）但无参考设备（Win11 x64 / macOS 最低配 8GB）实测记录；Q5/G-base 等容量口径已决策、基线"目前未生成或执行"（m0-checklist 原文）。属既定发布义务与 M0 退出项。严重度：中（发布前置，非代码缺陷）。

（以上 10 项均未发现可导致数据泄露/资金损失/服务中断级别的实现缺陷；第 1 项是最接近"服务中断"的残余风险，已如实定级。）

## 5. 检查清单逐类适用性判定

原则：本地优先、单用户、无服务器/无网络外发（`connect-src 'none'`、无 HTTP 客户端、无模型客户端）、无支付——整类不适用者按类说明，不为 SaaS 清单扩建功能。

### 不适用（按类，依据：产品形态）
- **账号与身份（login+/email、密码重置、MFA、会话超时/踢出、SSO、SAML、SCIM、深于 admin 的角色、按 URL 改号越权、租户隔离、管理员模拟登录、登录限流、防 CFO 误锁）**：无服务器、无登录、无多用户/多租户；单用户本地数据，IPC 侧以 sender/frame/文档校验替代（`index.ts:317-324`）。全类不适用。
- **支付与计费（订阅/升降级/按比例、失败重试与催缴、PO 号发票、销售税/VAT、退款/部分退款、用量计量、年约条款、财务对账报表）**：无任何支付与货币处理（无 money 字段，"money as integers"随之不适用）。全类不适用。
- **对外 API 与集成（版本化 API、客户 API key、API 限流、第三方 API 变更预案、OAuth 刷新、集成沙箱、webhook 签名与重试）**：无对外 API/webhook；引擎协议为私有 stdio 契约（registry.json+schema.json 双端校验，本身即是"designed schema"而非逐表即兴）。全类不适用（内部契约质量已另核）。
- **邮件（SPF/DKIM/DMARC、退信与投诉处理、邮件客户端渲染）**：不发邮件。不适用。
- **云基础设施与交付（dev/staging/prod 对齐、IaC、零停机、一键回滚云语义、功能开关、自动扩缩、CDN、DNS/SSL 续期、二区域、灾难恢复年度演练、状态页）**：无云服务。本地等价物已核：CI 全量门禁（下条）、回滚=上一目录包+git 还原（流程层）。全类不适用。
- **观测与值班（3am 可搜结构化日志、错误聚合、外部拨测、告警 paging、仪表盘、跨服务 tracing、on-call、runbook、postmortem）**：无运行服务可观测；且产品以"零日志策略"为隐私设计（主进程零 console/零日志文件，错误只出固定码受限参，`errors.json` 上限 2048B）——这是有意取舍而非缺失，如实记录。不适用（若未来接入模型网关，需重评）。
- **合规套件（SOC2、HIPAA、BAA、PCI、GDPR 全表/备份/日志删除、数据驻留、季度权限评审、渗透测试、安全问卷、企业买方尽调）**：不处理 PHI/卡号/第三方 PPI，无企业买方。当前不适用；SECURITY.md 已含私有披露约定。转为"首个企业客户前的义务"而非现在动工。
- **流量与规模（连接池、周一尖峰、负载测试、5M 行索引超时）**：本地 SQLite 单连接；分页/导出边界（16MB diff、512 段、200 行/页、32KB 文本页）已设硬顶。容量与老设备口径属 Q5/D2 未执行项（见 §4.10 与"无法确认"）。按当前形态不适用，规模口径待基线。
- **cron 双跑 / 死信队列 / 存储生命周期规则 / 成本告警**：无定时任务、无队列服务、无按量云成本。不适用（本地等价：Job 限额+取消+重启对账已核）。
- **通知开关 / "notifications people can turn off"**：应用无通知系统。不适用。
- **后台慢任务不冻结页面**：适用且已验证——查询/提交均为持久 Job + 订阅更新（subscribeJob/onTaskUpdate），UI 保留响应。

### 适用且已验证（证据）
- **designed schema 而非即兴**：`packages/contracts/v2/schema.json` 单一契约源 + TS zod `.strict()` 与 Python 受限 JSON-Schema 校验器双端执行；canonical JSON（拒 NaN/代理对）贯穿。
- **服务端校验而非仅表单**：引擎对每个请求按契约校验（contract_v2.py）；IPC 入参 zod strict（query-definition-service/task-service/desktop-ipc 多处）；名称类被 schema 锁 `[A-Za-z0-9_.-]{1,128}`（防注入/路径，兼作标识符规范；自由文本走 RDF 字面量，UTF-8 全量支持）。
- **幂等键（重试不重复扣费的钱类等价物=重试不重复提交）**：operation_claims 幂等创建（`project_lifecycle.py:458-470`）、changeset marker 幂等 commit（`transactions.py:214-216`）、e2e 实测首次 ACK 丢失零重放（§3.4）。为全代码库最强项之一。
- **重复点击防抖/去重**：pending 精确重试语义（原 operationId/参数重放）、CAS 代际草稿、单飞读取+1 次合并重读。
- **分页在 page 400 仍正确**：cursor+startIndex+严格显示校验（§3.3）。
- **软删除语义**：定义"撤回"（retirement）为状态而非物理删；历史/已提交轮次不可改写（commit_evidence/snapshots 不可变）；无任何 DELETE 用户数据路径（除缓存回收且不触历史，`job_store.py:1970-1994` 失效只动 current 指针与 stale 标记）。
- **时区**：全部 epoch 毫秒+单调钟；无 naive 本地时间存储（grep 佐证：无 `datetime.now()` 无 tz 用法）。
- **emoji/重音/RTL**：strict UTF-8 全链、代理对拒绝、按码点切片、无有损截断；字面量层可容纳任意 Unicode（标识符层有意受限，见上）。
- **撇号客户名**：标识符不接受撇号（设计选择，防止注入/路径面），标签/定义/说明字段 UTF-8 自由文本可含撇号。
- **SQL 注入**：354 处 execute 全参数化；动态标识符仅来自字面量表名元组或 quote-转义的 sqlite_master 读取（`project_lifecycle.py:301` 等）；零 executescript、零拼接。
- **XSS/CSRF/CORS/安全头**：CSP 生产无 unsafe-inline/eval、connect/object/frame/form-action 'none'（`csp.ts:3-13`）；无 HTTP 服务故无 CORS 面；renderer 无 Node/进程 IPC（隔离三件套 contextIsolation+sandbox+nodeIntegration:false）；权限 handler 全拒绝（`index.ts:196-199`）。
- **文件上传扫描/大小限制/不可执行存放**：无用户上传面（导入=打包内置示例资源，路径由主进程硬指定）。
- **密钥出库/轮换**：无密钥存在（无模型客户端）；`.gitignore` 排 env/key/pem/p12；无 .env 无 dotenv；引擎 env 白名单不继承。轮换项随之不适用（无物可轮）。
- **依赖确认与扫描**：直接依赖精确 pin（.npmrc save-exact）、464 个 registry resolved、0 git/tarball 源；Actions 全 SHA 固定；Dependabot（npm+Actions）+ `uv lock --upgrade` 政策（SECURITY.md）；`verify:sources` 校归档资料。
- **传输/静态加密**：传输=无网络（最强形态）；静态=SQLite 明文——本地优先设计下的接受项，明示记录【观察】；未来含凭据/外发时需重评（含 keychain 计划）。
- **最小权限（含 AI agent）**：Agent 尚未接入（S3 前）；现有"代理"=渲染层，被沙箱+闭合 preload+trusted 校验约束；引擎无密钥无外联。
- **日志不记密码/令牌/卡号**：零日志策略+固定错误码+参数受 schema 限制（errors.json paramsSchema）；引擎 stderr DEVNULL、worker `os._exit(76)` 不带原始输入。
- **备份/恢复已测试**：形态转换——迁移备份强制度+哈希（format3 migration_backup 强制新目标、源变更即 abort）；应用级用户备份缺失（Top6）。夜间备份/PITR 按云语义不适用。
- **迁移前进与回滚**：v2→v3 单向前向迁移+不可变备份+user_version 拒绝降级（UnsupportedProjectFormat）；回滚=保留的迁移备份（文件级）。"2pm 锁主表"按云语义不适用（启动期持租约迁移）。
- **缓存与失效**：`invalidation-v2.json` 单一规则源；已核 `unrelatedOrModelChange: do_not_invalidate_existing_domain_result`（仅改模型配置不作废领域结果）；历史/失败/取消不计过期由 publicationPolicy/reconcile 语义保证。
- **单元/集成/e2e/回归测试**：1691 TS + 3445 Py(44 skip) 自然 0；18 e2e 用真实 Electron（16 pass + 2 macOS 条件 skip）；I04 故障矩阵进 CI；ACK 丢失/切换隔离/重载 noReplay 均有断言真实语义的 e2e（非点击冒烟）。
- **测试数据像生产而非生产数据**：fixtures+内置设备维护示例项目；无生产数据入仓（.sqlite/.db/.env 均禁入）。
- **空态/加载态/错误态**：两模块均有专门空态文案、busy 禁用、`role=alert/status`；PAYLOAD_EVICTED 等有专门解释；空 SELECT 引导明示"不是对数据原因的判断"。
- **可行动的错误信息**：四段式"发生了什么/为什么发生/如何修复/相关知识"由 e2e 断言（i04-jobs:39-41）；受限码+参数而非"something went wrong"。
- **表单失败保留输入**：服务端保留 `preservedDraft`；选择操作不覆盖未保存草稿；错误文案明示"已输入内容保留"（OntologyMainlinePage:268-272）。
- **undo**：见 §3.2（redo 缺=Top3）。
- **代码评审每一变更 / 分支策略 / 架构决策记录**：AGENTS 并行 worktree+feature 分支+指定双审流程在案运行（本轮即其一）；ADR 0001–0003 存在；迭代文档树完整。
- **README 一小时内跑起来**：README 快速开始（npm ci/uv sync/npm run dev）+ development.md——结构达标，"一小时"未实测（无法确认）。
- **为接手者留文档**：docs/prd|architecture|iterations|reviews + source-manifest；达标。
- **条款/隐私与代码一致**：README/SECURITY 声明本地优先、无遥测、无外联、未签名仅内部——与代码实测一致（无网络客户端、无遥测代码）。
- **AI 专项（提示注入防护/客户数据不进提示/花费上限/evals/降级/弃用预案/提示日志/人工批准）**：现阶段无模型调用，前七项不适用（转为 S3 接入前义务清单）；**人工批准步骤已实现且为不变量**：预览必须全量展示后人工点确认、Agent 不得自确认（AGENTS 不变量 4 + 确认按钮门禁）。
- **删除 AI 死代码 / 拆 2000 行文件**：部分缺口=Top9。
- **"reading every line the AI wrote"等人员项**：以指定双审+独立证据链部分满足；单人创始人的 bus factor=1 是真实组织风险（README 仓库在个人名下 NOmoreJoke/OntoLearn-Studio，账户归属公司项待办）——如实记录，不适用代码修复。

### 适用但本次无法确认（如实声明）
- 五龄老设备 / Win / Linux 参考设备实测（未发生）。
- G-base/G-map-empty/G-behavior/E.5 容量与行为基线（明示未生成）。
- Ruff "332 文件"逐文件计数（仅采信退出 0 命令链）。
- README "一小时上手"实测时长。
- 307 个过程评审文档的逐字复核（抽样台账一致）。
- 框架安全补丁响应节奏（Electron 44.9.0 当前版；无既定 SLA）。
- changelog：不存在 CHANGELOG 文件——按"客户可读变更日志"计为低优先适用缺口（当前无外部客户）。
- 返回按钮语义：桌面视图导航经菜单/链接（installViewNavigation），无浏览器历史栈语义——未深核，低风险。

## 6. 其余阻断与验收缺口（不得清零，与历史台账一致）

以下经本人对 tasks.json / m0-checklist / T11 root acceptance / D8 决策书原文核对，全部仍开放：

1. **合并链未走**：未推送、无 PR、无 CI 运行、未合并、未远端复核；`mergedUsableFRs: "0/17"` 不变；本审查者无推送/合并授权，未做任何推送。
2. **指定双审体系**：47 阶段指定双审积压、0 个真实指定模型 Pass（backlog.md/status.md）；C4→C5→C6 同一 subject 三次正式配对尝试未通过，已达 D8 人工裁决门；`D8-mainchain-888ac-human-decision-20261024.md` 待用户选 A/B，未预填。
3. **发布义务五项**（tasks.json `releaseObligationsSeparate` 原文）：签名、公证、全 APP 法律与 `_distutils` 来源、跨平台/参考设备、损坏 SQLite 物理保护 HOLD。T11 root acceptance：`formalReleaseAccepted=false`、`legalFullClosureAccepted=false`、nine nonengine 签名与 deep verify exit1 保留。
4. **M0 退出项全部未勾**（m0-checklist 原文）：Q2/Q3/Q5/Q6/Q7/Q8/Q9、四类基线、项目文件格式等六项技术设计、S2/I04 合并门、签名公证离线启动；原型遗留 A-01/B-03/B-04 三项保留。
5. **真实 LLM 验收**：阻塞并如实标注（代码无模型客户端，S3 前不得接入——已核实现状一致）。
6. **whole085 剩余门原文**："Full new packaged18-case E2E and other original platform/physical HOLD gates remain; no release-complete claim. New ROOT ticket required for further execution."——后续 e2e002/runtime001 已履行的部分以其实际证据为准，其余平台/物理 HOLD 仍在。
7. first full001 环境等值首败及其 22 字段修正史、002 原件均保留未改写（本审查未触碰任何历史证据文件）。

## 7. 结语判定

- **是否存在阻断**：受核产品代码（base 5f910b52 → head 7d30ab34，525 文件）内——**未发现新的实现级阻断缺陷**；事务/幂等/隔离/校验/安全面在本审查的独立追踪中全部与证据一致。流程与发布层面——**阻断仍在**（§6 全清单），其中 `UNKNOWN_NOT_OBSERVED` 属"验收证据义务未闭环"而非已证实缺陷（我的独立判定见 §3.5/Top1，不可洗绿亦不可升格为已证实故障）。
- **0/17 口径**：不变。仅在实际审查通过且 push→PR→CI→merge→远端复核后方可改变；本轮未获推送授权。
- 本报告为本方唯一写入物；未读取对方模型任务/报告；产品源只读。

— ZCode / GLM-5.3（bigmodel-start-plan），2026-10-24，指定独立完整审查。
