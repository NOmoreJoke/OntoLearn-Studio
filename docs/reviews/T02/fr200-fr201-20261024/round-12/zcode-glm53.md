# T02 R12 独立工程审查报告（ZCode / GLM-5.3 / 最高思考 / 完全访问）

审查对象：base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `dc6c112ecc944116dc421f9ef569eb50e132e217`（tree `ba11405f4e4d9ba88136ed47ce74f2848a12b9ac`，sole parent `deac095fb86f3704fa76cd4216ecd60409ff3c99`），branch `feature/weekly-t02-fr200-fr201`，cwd `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes`。本人为本轮两方独立新任务中的 ZCode 方；未读取另一作者本轮任何目录、报告、意见或 verdict；R04–R11 历史只作为已提交原件与处置事实引用，不继承其判定。

## 0. 核验回执与身份绑定

- 本人实测：cwd/branch/HEAD/tree/parent 与输入完全一致；base→head 45 提交、135 差异路径、1412 tracked 源叶，均与输入及 O081/CANDIDATE-BINDING.json 一致。
- 四新叶在冻结 head 逐 bytes/SHA256 相等：storage.py 89563B/`23c9040e…55e60`、test_storage_snapshot_iri_memo.py 12775B/`aeeaf181…b2be`、native-recovery.cjs 9113B/`aa1d4fb6…2ba6f`、native-recovery-observer.test.ts 11472B/`d432cbd6…f73a6`。
- 本人独立生成 `git diff deac095f..dc6c112e`（IRI 两叶）SHA256 `76b3d663…f07f` 与 V/SOURCE-PATCH-v2.diff 相等；（observer 两叶）SHA256 `625737c0…8323` 与 O080/SOURCE-PATCH.diff 相等；deac095f 的 storage.py 为 84495B/`858e168f…d367`，与 V/HANDOFF-v2 的 before 针一致。即：**提交内容＝两份被独审的补丁原文**。
- 当前工作树唯一差异为受保护 AGENTS 操作政策 overlay（15147B/`de15f6ce…5c8c4`，未 stage）＋ round-01/02/03 untracked 保护叶；head 内 AGENTS blob 为 1056B 版本化旧指南（等于 parent），与 O081 绑定一致。未运行 check/pytest/vitest/build/package/install/formatter/HMR/SQL/GUI/RPC/profiler；未 git add/commit/push；未写除本报告外的任何文件。
- 完整 28139B/257 行输入（含原 160 项全文）已读至 EOF；owner 中途 Escape 停止与证据目录更正（本轮绑定原件在 O081，O079 保留旧首败）已知悉并按更正执行。

## 1. 阅读与验证披露（全文 / 差异级 / 结构级 / 未读）

**全文亲读**：当前 AGENTS.md overlay（经系统上下文全文提供）；PRD FR-200/201 正文、FR-804/805/806、附录 C/D/E/F/G 全文；ADR-0001/0002/0003 全文；M0 更新计划全文（207 行，S1/S2/S3/C1/B1/U1 验收与退出门槛）；docs/m0-checklist.md、docs/reviews/T02/status.md 全文；round-11 disposition.md 全文（549 行，含 160 项表、163 稳定位置、R11 新增 3+9、限证字典）；四新叶全文（storage.py 2037 行、29 例 memo 测试、native-recovery.cjs 256 行、observer 单测 326 行）；mainline.py 全文（1206 行）；rdf_snapshot.py 的 term/iri 实现全文；V 的 HANDOFF-v2.md、INDEPENDENT-SOURCE-TEST-REVIEW-v2.md、SOURCE-PATCH-v2.diff；O080 的 HANDOFF-PREPARED.md、INDEPENDENT-OBSERVER-SOURCE-REVIEW.md；O081 的 CANDIDATE-BINDING.json、INDEPENDENT-VALIDATION-BINDING-AUDIT.md、native24/result.json（21P/3S/0F/154.99s/双 exit0）、c1-evidence.json 主体、report.json 统计；O077/COMPLETION.json 主体（交付、CI44 run 40442149223、三平台结果与 Windows 细目）。

**差异级亲读（base→head）**：全量 diffstat（135 路径）；rdf_snapshot.py、coordinator.py、query_presentation.py、domain_changesets.py、project_host.py、job_store.py、contracts（contract_v2.py、src/v2.ts）、ci.yml、desktop-ipc.ts、engine.ts、project-mainline-service.ts、preload/index.ts、OntologyPage.tsx、mainline-api.ts、mainline-facts.ts、mainline-session.ts、OntologyMainlinePage.tsx、OwnershipConflictDetailView.ts（新）、mainline-ownership.ts（新）逐 hunk 读；t02-fr200-fr201.spec.ts 亲读约 1/3（头部、poll 计时 harness 全文、六例矩阵定义、FR201 拒绝族/原 ID 编辑/保留身份冲突 UI 断言段），其余为定位级。

**结构级/定位**：engine 7 个 mainline 测试（25+5+13+17+4+3+6 例计数）、ui-observation.ts 头部、vendor/rdflib PROVENANCE 头部、fixture t02-manual-fact-id.json（diffstat）、contracts schema/fixtures/binding-regressions/registry（diffstat＋关键不变量经代码闭读）、scripts 三件（diffstat）、native-driver(.test).ts、csp-lifecycle、mainline-consumer-first-ack-loss、t01/t02 全部单元测试族（diffstat/标题级）、native24/test-results（存在性）。

**未读（如实披露）**：vendor 四个 wheel 二进制内容（仅来源针）；round-04～10 各作者原稿正文（仅经 R11 处置表与 status 摘要了解，作为历史身份引用）；V/O080 的编号运行收据原始 log（读其独审与 TEST-SUMMARY 结论，未逐份复跑日志）；O079 全部文件（按 owner 更正不作本轮绑定目录，其事实经 O081/R11 处置间接引用）；O078 内部文件（历史 profile，非本轮验证；仅按输入边界引用）；O081 的 check/stdout 全量日志（读独审摘要与关键计数）；本轮另一作者全部材料（隔离，未读）。

## 2. Top 10 当前最重要真实风险（不足不凑数；排序按对数据/交付/门禁的实际影响）

1. **[Z11-R01 / R11-T03 谱系] Windows FR201 整例 180s 累计超时仍在真实平台复现**。CI44（deac）Windows 20P/3S/1F：失败边界为 "edit relative datatype controlled-rejection UI observation"，整例 180000ms 到期；本人核 O077 明细：failedPoll 411.396ms，五相测得 poll 合计 78744.649ms（含 callback 12222.011ms、gap 66284.663ms），测得 poll 之外 98004.098ms；trace 最大组 Evaluate read 143 次/39967.994ms、toBeVisible 38 次/23126.63ms、rejectCallerObject 39 次/13503.715ms。影响：完整三平台 CI merge 门禁无法通过；当前 memo/observer 候选与该超时的因果未证。最小建议：由 owner 在授权 Windows 运行中用既有五相计时＋trace 分组做归因（是否 Playwright expect 轮询节奏/超时预算结构问题），必要时走预算/断言结构的独立评审票；不得以本机 56.482s 推断 Windows。**当前 push 前源码阻断：否**（ROOT 已定不设 push 前证因/余量门禁；计时仅测量）。
2. **[R10-02 / Z09-02 / R11-T02 / Z11-R02 谱系] C1 异步失败家族 UNKNOWN，且新 observer 的真实失败输出从未在真实平台产生**。CI43 C1 为 ready/bootstrap true 后 child close 1/null（异步原因 UNKNOWN）；CI41 helper12 TypeError 旧根因 UNPROVEN；O079 40 秒 watchdog 真实首败保留。本轮 O081 的 C1 为成功路径（window3/两 prompt/events=[killed,unresponsive]，成功输出无 failureObservation——属预期，不是失败捕获证据）；16×8 环、4096B cap、异常隔离只在 12 例 VM 合成中验证。影响：若平台再发 C1 失败，诊断能力仍未被真实样本证明。最小建议：下一次授权 Windows/CI 失败发生时优先收取 failureObservation 原件；不为制造失败样本而改成功门禁。**当前 push 前源码阻断：否**。
3. **[Z08-01 / F02 / R10-01 / R11-T01 谱系] 当前 head dc6c112e 无新 CI；deac 的 CI44 已是 overall cancelled＋Windows failure＋Quality 15min 取消（verify 内部 17 witness PASS 但父 step 取消、packaged-recovery 三族 NOTRUN）**。本人核 O077：CI44 run 40442149223 attempt1 pull_request head deac、合成 checkout `5afe9cc0`（parents 583+deac，非真实 merge）；PR16 open/未合并、remote head=deac。影响：完整 CI merge 门禁全开；dc6c112e 的四叶变更（含 CI 依赖的测试文件）从未在任何平台 CI 执行。最小建议：ROOT 精确票 push dc6c112e 并接收完整三 job 回单；沿用原 15/20min、3769 全集逐 node、原有据 skip、自然 0、全部后步骤与 Quality packaged recovery 门禁。**当前 push 前源码阻断：否（是 merge 前阻断）**。
4. **[Z08-02 / Z09-03 谱系] 引擎自然退出与全部后代回收 UNKNOWN**。CI44 Windows "mainE2Edriver1; all native descendants UNKNOWN_NO_JOB_HANDLE"；本地 naturalDriverExit 由 proc.wait 路径固定 true，不能把负 signal returncode 说成自然。影响：崩溃/退出对账的外推边界受限；不构成本轮源码缺陷。最小建议：未来 Windows 失败附件/授权样本中核对后代句柄；不新增当前门禁。**当前 push 前源码阻断：否**。
5. **[F05 / R06 D2 / MM R07-04 / R05 Z P8 / R05 MM04 / F-R09-08 谱系] 状态登记缺口对 dc6c112e 再次打开**。本人核：status.md 与 m0-checklist.md 末段均停在 R11/d1aca，无 dc6c112e/R12 节；本轮四叶为产品代码＋测试，属必须登记的受审候选变化。影响：文档状态与受审实现脱节（历轮同型缺口）。最小建议：owner 在本轮双审接收后以常规 docs 后继补登 dc6c112e/R12 节（含 O081 绑定指针），不预写检查结论。**当前 push 前源码阻断：否（文档登记项）**。
6. **[#146/#147/#160 谱系；LEGAL146/HUMAN147] 法律/IP/隐私与真实 bus factor UNKNOWN**。个人 GitHub namespace 可见，不证明公司产权；RDF 内容是否含个人数据未知（无账号关键词≠无）；agent 负责线＋文档密度不证明第二人类可接手。影响：发布/商业化前置。最小建议：发布前由用户完成产权/隐私/继承的明确决定。**当前 push 前源码阻断：否（独立 HOLD）**。
7. **[Z08-08 / F09 / MM R07-12 / R09-04 / R10-05 / R10-T07 谱系] 供应链分层 HOLD**：仓库内 vendor 四个 rdflib wheel（fr201.1/2/3 重打包＋upstream）来源锚完整（PROVENANCE 本人核头部），但无干净设备/断网/签名公证/NOTICE 物理包检查闭环；无自动 CVE 扫描。最小建议：T11 受控维护窗口继续；不私删旧来源。**当前 push 前源码阻断：否**。
8. **[F16 / Q5 / 坏 SQLite / unknown parser / N3Store 坏 snapshot 谱系] 容量与物理损坏防护 HOLD 未关闭**。Q5 未决；旧超限库恢复、损坏 SQLite 物理保护、unknown parser 失败（本轮 TermInputError 只把**已知词法/策略**拒绝定为 INVALID_REQUEST，未知解析器失败仍 ValueError→UNKNOWN/HOLD，本人核 rdf_snapshot.py 与 domain_changesets.py 确认该分层未被破坏）。最小建议：维持原窗口。**当前 push 前源码阻断：否**。
9. **[本人新观察 N1，映射 F13/静态界主题] IRI memo 的"有界"是静态控制界声明，不是 RSS/CPU/性能测量；且 memo 命中依赖"同一原串＋身份门全等⇒同结果"的窄假设**。本人核：身份门覆盖 storage/rdf_snapshot 两模块的 term/iri/Graph/URIRef/parse/n3/json.loads 绑定及 term.\_\_globals\_\_ 动态 iri（v2 一行门），未覆盖 rdflib 解析器插件注册/bnode 计数器等全局状态；对仅 `<…>` 且已证 URIRef/n3 相等的串，实际风险极窄（Literal/转换器路径在命中前永久禁用 memo）。影响：若未来升级 rdflib 或改解析器全局态，需重新评估；不得据此宣称提速百分比。最小建议：在 vendor/引擎升级票中把 memo 身份门清单列为复核项。**当前 push 前源码阻断：否**。
10. **[R11-T02 / F-R09-05 谱系＋本人新观察 N2] 观察诊断本身有界：16 行环会覆盖、计数饱和、超 4096B 只留固定兜底（含 requiredBytes 提示），成功输出零诊断；observer 隔离仅合成验证**。影响：真实失败发生时诊断可能不完整——这是设计取舍而非缺陷。最小建议：真实失败样本到手后评估是否需要在原票内扩界（不改成功路径）。**当前 push 前源码阻断：否**。

## 3. 原 160 项逐项分类（每项一档；分类是适用性，不是产品通过数）

依据基线：本产品为本地优先 Electron+Python 离线本体工作台；无账号/多租户/支付/邮件/云服务；产品正式能力仅 health＋存储内部 API；T02 候选交付 FR200/201 表单/事实/所有权链。以下"核"均指本人本轮对代码/文档/证据的亲自核对位置。

| 项 | 分类 | 当前依据（本人核） |
|---|---|---|
| 1 | 适用 | ADR-0002＋SCHEMA（storage.py:2003–2036）＋format3 迁移为设计化 schema，非逐表即兴 |
| 2 | 不适用 | 无登录/邮箱体系（preload 仅业务命名桥，无远程认证面） |
| 3 | 不适用 | 无账号，无密码重置 |
| 4 | 不适用 | 无 MFA 面 |
| 5 | 不适用 | 无用户会话；引擎会话为握手/任务预算，非用户会话 |
| 6 | 不适用 | 无企业 SSO 客户 |
| 7 | 不适用 | 无 SAML |
| 8 | 不适用 | 无 SCIM |
| 9 | 部分适用 | 进程级权限边界在位（renderer 无 Node、coordinator PERMISSION_DENIED、engine.ts selected 校验）；产品级 RBAC 属后续 FR-803 |
| 10 | 部分适用 | 单用户本地；跨项目绑定/ownership/单值槽检查在位（mainline.authorize、\_check\_slot、ownership proof）；无 URL 数字 ID 攻击面 |
| 11 | 不适用 | 无多租户服务端 |
| 12 | 不适用 | 无管理员冒充功能 |
| 13 | 不适用 | 无登录面可限流；无远程 API |
| 14 | 不适用 | 无锁定场景 |
| 15 | 适用 | v0→v3 前向迁移＋回滚/故障注入矩阵（\_migrate、format3 657 测试族；R08 迁移 468=424P+44S 为既有证据） |
| 16 | 部分适用 | BEGIN IMMEDIATE＋5s 超时＋writer lease/OS lease；本地单写者，无高峰锁表负载面 |
| 17 | 部分适用 | PK 与游标分页在位（ownership detail ≤512 段、catalog/operations 有界页）；真实规模索引策略随 Q5 未决 |
| 18 | 不适用 | 单进程 SQLite＋stdio，无连接池需求 |
| 19 | 部分适用 | backup() 在线备份＋format3 migration_backup 在位；无定时策略（本地产品策略未定） |
| 20 | 适用 | 恢复经真实测试：迁移 hook 故障矩阵、快照完整性校验（load_snapshot digest）、重开重试 |
| 21 | 部分适用 | commit_evidence 前后快照＋不可变 snapshots＝项目级时点恢复；无 WAL PITR 需求 |
| 22 | 适用 | 受管事实墓碑（object=NULL）、definition_retirements、显式恢复 ChangeSet 语义在位 |
| 23 | 适用 | 双端 strict 契约校验＋Store 形状校验；错误只传固定码＋白名单参数（\_host\_fault 映射） |
| 24 | 不适用 | 当前无定时提醒功能 |
| 25 | 适用 | 引号/撇号/类型字面量经 43 拒绝族实测（knownQuoteAndDatatype/knownLanguage/authority 输入，无静默规范化） |
| 26 | 适用 | UTF-8/Unicode 标量处理（ensure_ascii=False、UI 孤立代理拒绝、text002 56309 scalars）；RTL 未专项但字符串原样保留 |
| 27 | 不适用 | 无金额字段；xsd:integer 词法由 vendored parser 受控拒绝（overlong-integer 拒绝实测） |
| 28 | 不适用 | 无多国计税 |
| 29 | 部分适用 | 分层 definitions＋版本向量支持演进；真实"第二客户变更"未验 |
| 30 | 适用 | operationId/jobId 幂等 marker：同计划重试返回原 marker 不重复写（storage.commit:794–800） |
| 31 | 适用 | 同 operation 幂等＋UI pending/receipt；rapid-click 专项未测（OPERATION 限证） |
| 32 | 适用 | 游标分页：catalog/operations/ownership detail（512 段不变量）/text 页；PAGES 限证在位 |
| 33 | 部分适用 | Turtle 导出/项目包为 P0（FR-203/1000）但非本候选交付；无表格导出需求 |
| 34 | 不适用 | CSV 映射未实现（仅 prepared plan 契约；ADR-0002 明示） |
| 35 | 不适用 | 保留/删除属 FR-705 后续；collect_cache 仅回收未固定派生载荷 |
| 36 | 适用 | 仓库/引擎无凭据（diff 核无 .env/密钥；S3 前引擎不持密） |
| 37 | 不适用 | 尚无密钥轮换面（模型网关未接入） |
| 38 | 适用 | vendored wheel PROVENANCE＋上游 member 哈希＋uv.lock 冻结（本人核 PROVENANCE 头部） |
| 39 | 部分适用 | 锁文件＋来源锚在位；CI 无自动依赖漏洞扫描步骤 |
| 40 | 适用 | 全输入 strict schema＋词法拒绝＋canonical 校验（内外一致） |
| 41 | 适用 | 参数化 SQL＋动态标识符转义（material\_profile/table\_info 引号翻倍）；CSP 单源；renderer 文本节点渲染无 innerHTML；本地边界内 OWASP 面成立（OFFLINE\_XSS：离线不排除 XSS，未专项渗透） |
| 42 | 不适用 | 无用户文件上传（示例资源为受信 bundle＋O\_NOFOLLOW/fstat 检查） |
| 43 | 不适用 | 无 HTTP 服务，无 CORS 面 |
| 44 | 部分适用 | CSP meta/header 单源两变体；无其他 HTTP 响应 |
| 45 | 部分适用 | 本地 SQLite 明文属本地优先设计；stdio 本地传输；凭据加密留 S3（safeStorage 计划） |
| 46 | 适用 | renderer 沙箱/contextIsolation；引擎无密钥；Agent 白名单设计未接入（模型推理与权限执行分离在架构层落实） |
| 47 | 适用 | operation/receipt ledger 记录 origin（hostClientId/engineSessionId/permission）；错误参数白名单不含原值/密钥 |
| 48 | 不适用 | 无企业客户安全团队前置；发布前独立安全审查为 HOLD（未执行） |
| 49 | 不适用 | 无企业安全问卷需求 |
| 50 | 不适用 | 无外部漏洞披露流程（未发布） |
| 51 | 部分适用 | 本地数据无凭据外泄面；设备失窃＝本地项目数据暴露，盘加密策略未定 |
| 52 | 不适用 | 无 SOC2 需求 |
| 53 | 不适用 | 无健康数据 |
| 54 | 不适用 | 无 BAA |
| 55 | 部分适用 | 变更审计完整（commits/evidence/job ledger）；"谁查看过"未单列审计 |
| 56 | 不适用 | 无支付，无 PCI 面 |
| 57 | 部分适用 | RDF 是否含个人数据未知（DATA57：无账号关键词≠无）；删除请求义务未实现 |
| 58 | 不适用 | 本地存储，无驻留需求 |
| 59 | 不适用 | 无企业访问复核 |
| 60 | 部分适用 | 开发/CI/本机一致性由同版 check＋CI 保证；无 staging 概念 |
| 61 | 部分适用 | CI workflows＋双锁文件为基础设施代码化；无云资源 |
| 62 | 适用 | CI 先测试后交付为 merge 硬门禁（且当前为开放条件） |
| 63 | 部分适用 | git 回滚＋不可变历史＋撤销设计在位；无服务端部署回滚 |
| 64 | 不适用 | 无在线服务 |
| 65 | 部分适用 | 无 feature flag 系统；测试经环境变量/替身隔离 |
| 66 | 不适用 | 无自动伸缩 |
| 67 | 不适用 | 无 CDN |
| 68 | 不适用 | 无 DNS/SSL（本地应用） |
| 69 | 适用 | ExecutionJob/JobStore 队列、取消、崩溃对账在位（ADR-0003；native/reload/disconnect CI 各 1 真实） |
| 70 | 部分适用 | 有界退避重启/不自动重放写在位；无网络重试面 |
| 71 | 部分适用 | 失败终态持久（run_terminal/failed jobs）；无 DLQ 需求 |
| 72 | 不适用 | 无 cron；协调器有界重启不重复写（marker 幂等） |
| 73 | 适用 | 派生缓存＋invalidation-v2.json 失效规则＋collect_cache 边界（历史/pin 不回收） |
| 74 | 不适用 | 无外发邮件 |
| 75 | 不适用 | 无退信处理 |
| 76 | 部分适用 | 存储/缓存回收规则在位；历史不可清理导致增长（I01 R6 开放） |
| 77 | 不适用 | 无云成本（模型未接入） |
| 78 | 部分适用 | 本地灾难恢复路径已测（迁移/快照/退出对账）；成文 DR 计划未写 |
| 79 | 不适用 | 无双区域可用性承诺 |
| 80 | 部分适用 | 结构化错误码＋事件 evidence 可检索；无中心日志系统 |
| 81 | 部分适用 | 错误按固定码/messageKey 分组（ERROR\_CATALOG 2048B 界）；无外部错误跟踪 |
| 82 | 不适用 | 无在线服务可外部探测 |
| 83 | 不适用 | 无告警值班 |
| 84 | 不适用 | 无运维仪表盘 |
| 85 | 部分适用 | operationId/job/trace 链路跨进程可追（receipt/checkpoint 绑定）；无分布式 tracing 需求 |
| 86 | 不适用 | 无 on-call |
| 87 | 部分适用 | ADR/状态文档承担 runbook 职能；无值班场景 |
| 88 | 不适用 | 无正式复盘制度（历史首败保留机制在位） |
| 89 | 不适用 | 无状态页 |
| 90 | 适用 | 单测断言完整预期集合/顺序（本轮 29 例逐计数核；R10-T12 九 rules 正反断言在位为历史事实） |
| 91 | 部分适用 | 无第三方网络 API；rdflib 为 vendored 本地库（非服务依赖） |
| 92 | 部分适用 | E2E 覆盖核心闭环（六例矩阵＋FR201 拒绝/编辑/所有权链＋24 native）；无 signup/checkout 类收入流 |
| 93 | 不适用 | 无上线流量；容量属 Q5（不预设 load 门槛） |
| 94 | 部分适用 | 测试数据为构造本体样例（独立命名空间）；G-base 生产基线待 M0 冻结 |
| 95 | 适用 | 回归族在位：每候选同版全量 check＋native24；历史首败全部保留不覆盖 |
| 96 | 部分适用 | 参考 8GB/旧设备为 HOLD 未验；仅 mac-arm64 本机与 CI 三平台 |
| 97 | 部分适用 | 语义标注/role 在 renderer（aria-label/role=alert/status）；读屏与 a11y 合规未验（A11Y 限证） |
| 98 | 不适用 | 无订阅计费 |
| 99 | 不适用 | 无支付重试 |
| 100 | 不适用 | 无发票/PO |
| 101 | 不适用 | 无销售税/VAT |
| 102 | 不适用 | 无退款 |
| 103 | 不适用 | 无用量计费 |
| 104 | 不适用 | 无年度合同 |
| 105 | 不适用 | 无收入对账 |
| 106 | 不适用 | 无 webhooks |
| 107 | 不适用 | 无 webhooks |
| 108 | 部分适用 | v2 协议版本化＋错误码目录＋公共正反例（双端一致校验）；对外公共 API 未发布 |
| 109 | 不适用 | 无 API key |
| 110 | 部分适用 | 引擎侧请求/帧/队列/内存预算在位（65536 ID、帧限、HELD\_BYTES 等）；无公共 API 限流 |
| 111 | 部分适用 | 无第三方模型 API（S3 前）；vendored rdflib 隔离上游变化并留 upstream 针 |
| 112 | 不适用 | 无 OAuth |
| 113 | 不适用 | 无客户集成沙箱 |
| 114 | 部分适用 | prompt injection 防护属 S3/Agent 接入设计（FR-902/附录 F）；当前无模型面 |
| 115 | 部分适用 | 同上；最终外发检查未实施 |
| 116 | 不适用 | 无按客户模型费用（本地优先） |
| 117 | 部分适用 | evals（A-10 评估集）为设计未执行 |
| 118 | 部分适用 | 模型失败降级 FR-806 为 P0 设计；未实施 |
| 119 | 部分适用 | 模型弃用计划属 S3/Q9 未决 |
| 120 | 部分适用 | 最小外发记录 FR-904 设计在位未实施 |
| 121 | 适用 | 人确认边界：Agent 只草稿、ChangeSet 人工确认/不得自确认（FR-804/附录 F）；原子提交/撤销/墓碑在位 |
| 122 | 不适用 | 本地包内资源加载，无弱网页面 |
| 123 | 适用 | 空态（"当前未发现已登记的引用"等）、pending/role=status、错误 role=alert 在位并实测 |
| 124 | 适用 | 错误文案可操作：固定码映射中文说明＋"已输入内容保留"（OWNERSHIP\_CONFLICT 专属指引） |
| 125 | 适用 | 表单失败保留输入实测（retainedUI 断言、原 ID 展示不变） |
| 126 | 不适用 | 无邮件 |
| 127 | 不适用 | 无通知系统 |
| 128 | 部分适用 | 存储级撤销依据（commit\_evidence 前后快照）在位；Undo GUI 未验（定义级 Undo 子集已验为历史事实） |
| 129 | 部分适用 | 部分键盘/语义标注；读屏/键盘全流程与合规未验（A11Y） |
| 130 | 不适用 | 单语中文界面，无本地化框架需求 |
| 131 | 不适用 | 桌面应用无浏览器返回按钮语义 |
| 132 | 适用 | 本人亲读 storage/mainline/job_store 等：注释解释约束而非噪声，结构清晰 |
| 133 | 适用 | 每候选指定双模型独立审查＋独核＋ROOT 接收流程实际在位（R04–R12） |
| 134 | 适用 | worktree＋feature 分支＋PR 门禁＋禁止 add -A（AGENTS 第 5 节，实际执行） |
| 135 | 部分适用 | 锁文件冻结＋wheel 来源锚在位；定期升级制度未建立 |
| 136 | 部分适用 | Electron/rdflib 版本锁定；漏洞响应升级窗口未制度化（供应链 HOLD） |
| 137 | 部分适用 | 卫生观察在位（Z08-09）；本轮无新增死代码 |
| 138 | 部分适用 | storage.py 2037 行/mainline.py 1206 行/t02 spec 2174 行已超阈值；内聚但拆分维护项保留 |
| 139 | 适用 | ADR-0001/0002/0003＋M0 计划＋iteration/status 追溯在位 |
| 140 | 部分适用 | README/贡献/架构说明为 M0 交付项；"新工程师 1 小时跑通"未验证 |
| 141 | 部分适用 | 文档密度高；接手仍依赖原上下文（HUMAN147） |
| 142 | 不适用 | 无运维后台 |
| 143 | 不适用 | 无客服工具 |
| 144 | 部分适用 | 无正式 changelog；迭代状态文档替代 |
| 145 | 部分适用 | 条款/隐私政策未发布（产品未发布）；代码与本地优先声明一致 |
| 146 | 无法确认 | 账户/域名/仓库法律归属：个人 namespace 可见，公司产权 UNKNOWN（LEGAL146） |
| 147 | 无法确认 | bus factor：agent 负责线＋文档不证明第二人类可接手（HUMAN147） |
| 148 | 部分适用 | 双模型逐行独立读 AI 代码在本流程实际发生；人类 senior 逐行未发生 |
| 149 | 部分适用 | 数据模型先于第二客户设计（ADR-0002）；真实压力未验 |
| 150 | 部分适用 | 独立双审承担"解释 AI 修复引入新问题"机制（v1→v2 P2 即实例）；无人类复核层 |
| 151 | 不适用 | 无服务器/云账单运维（打包发布属 T11 职责线） |
| 152 | 不适用 | 无 3am 支付值班 |
| 153 | 部分适用 | 框架漏洞周级补丁策略未制度化（升级窗口 HOLD） |
| 154 | 不适用 | 无患者数据审计 |
| 155 | 适用 | "testing what the AI tested"由独核/绑定审计/ROOT 接收承担（O081 独核实测重算数据） |
| 156 | 适用 | 活库迁移前进/回退/故障注入在真实 SQLite 测试（历史 468=424P+44S） |
| 157 | 部分适用 | "说不"机制＝ROOT 门禁＋范围冻结＋Q2–Q9 停下来问（流程在位） |
| 158 | 不适用 | 无同时多客户在线（本地单用户；规模化议题属 Q5/架构后续） |
| 159 | 部分适用 | AI 不能调试时的人类升级路径存在（ROOT/用户；v1 P2 由独审发现、owner 修复为实例） |
| 160 | 无法确认 | 一年后记忆：version-map/disposition/ADR 链在位；真实传承未验 |

**本方统计：适用 33 / 部分适用 68 / 不适用 58 / 无法确认 3，合计 160**（复合项各只计一档；分类为适用性判断，不计作产品通过数）。

## 4. 全部历史意见稳定位置逐 ID 处置

计数口径说明：R11 处置表自身头部为"原 163 稳定位置（31+78+20+13+9+12）"＝current31＋权威78＋R09New19+OBS（20）＋extra13＋R10ZTop9＋R10MMTop12；R11 新增 Z3（Z11-OBS-01/Z11-R01/Z11-R02）与 MM9（R11-T01..T06、R11-F01..F03，其中 R11-S01 仅 alias R11-T06）在其后单列。本输入把"R11 Z新增3/MM新增9"计入"163"枚举；两口径相差 12。**本人处置全部 175 个位置（163＋R11 新增 12），无遗漏；别名按历史映射不重复造位（R11-S01→R11-T06，Z R11 Top9 为既有 ID 排名映射不新增）**。处置动词：已闭＝本人核当前证据关闭该位置本轮范围；保留＝开放/维护动作延期原窗口；重新变开＝本轮出现新事实使原登记再次落后；不采＝维持撤回/收窄；未知＝UNKNOWN 保持。原 owner/事件窗口逐项承接 R11 处置表原文，不在本报告重复全文，仅在同表注明变化；以下"gates 群数值更新"指：head=dc6c112e/45 提交/135 路径/1412 源、PR16 remote head=deac（CI44 已推）、dc6 未 push 无新 CI。

### 4.1 current31

| 稳定ID | 本轮处置 | 当前依据与最小理由 | 原owner/窗口 |
|---|---|---|---|
| Z08-01 | 保留（数值更新） | push/CI 门禁开放：dc6 未 push、无新 CI；deac CI44 overall cancelled | ROOT 精确 push/CI 票；merge 前 |
| Z08-02 | 保留 | 引擎自然退出/后代 UNKNOWN 未变；CI44 Windows 后代 UNKNOWN_NO_JOB_HANDLE | Windows CI 证据接收；新工具另票 |
| Z08-03 | 保留 | 制品回单/预算变化无新授权；本轮未打包 | 未来制品回单/预算变化须新授权 |
| Z08-04 | 保留 | CI 复发定因：CI44 Windows FR201 同族超时再发，归因仍 UNKNOWN（新增五相/trace 数据未定性） | 下次真实 CI 复发时定因 |
| Z08-05 | 保留（维护） | T01 测试维护观察不变 | T01 测试维护者下次触及 |
| Z08-06 | 保留＋分层 | 本地闭合资格随 O081 重验（check/native24 双自然 0，四 blob 同源绑定）；远端 CI 仍开 | Windows/Quality 实际 CI |
| Z08-07 | 保留 | 方法接线窗口不变（本轮无 T01 接线） | 原 T01/T02 方法接线窗口 |
| Z08-08 | 保留 | 供应链 P2：vendor 四 wheel 在仓，签名/干净设备未闭环 | 发布/供应链 owner 另票 |
| Z08-09 | 保留 | 卫生观察不变；本轮四叶无死代码新增 | 未来 CI 维护票 |
| Z08-10 | 保留（部分采纳维持） | 未穷尽面保持；本轮 vendor/发布未动 | 发布/vendor owner 窗口 |
| Z08-11 | 保留 | HOLD 群不关闭（见 §6） | 各原 owner 对应验收前 |
| Z08-TOP10-OLD79F | 保留 | 旧 79F 逐例原因仍未知；CI44 Windows 引擎 3721P/48S 无 79F 复现，新绿不倒填 | ROOT 登记及复发证据 |
| F01 | 已闭（本轮流程，限本人） | 本人必要正文阅读本轮完成（披露见 §1）；ROOT 接收待定，不预写 | T02 作者完成本票；ROOT push 前接收 |
| F02 | 保留（数值更新） | 完整 CI 结算门禁开放（CI44 Quality 15min 取消、verify 父 step 取消） | ROOT 精确票后、merge 前 |
| F03 | 保留＋限定 | 完整逐 node/phase CI 资格未变；O081 本机 pytest 只 log 计数不冒 CI 资格 | ROOT CI 控制层维护票 |
| F04 | 不采（维持撤回） | page.evaluate 合批提案仍撤回：本轮 spec 仍逐 read/expect＋计时观测，未复活 | 本票内闭合 |
| F05 | 重新变开（dc6c112e） | status.md/m0-checklist 末段停 R11/d1aca，未登记 dc6c112e/R12；本人亲核 | ROOT 指定文档 owner；状态追加＋归档票 |
| F06 | 保留 | CI 维护归口不变 | 原 T02 归口首个 CI 维护票 |
| F07 | 保留 | 证据控制层要求不变（O081 已按其履行，但门禁不因此关闭） | ROOT 证据控制层维护票 |
| F08 | 保留并正面复核 | 前端归口维护不变；本轮 renderer 仅 ownership detail/预览 lifetime 收口（承前轮） | 原 T02 前端归口；UX/异步预览维护窗口 |
| F09 | 保留 | wheel 维护不变（fr201.3 采用为历史；无新 wheel） | T11 merge 后受控维护 |
| F10 | 保留 | 归档 raw 不格式化要求不变；本轮未格式化任何作者 raw | 下次含 Python 围栏归档前核 |
| F11 | 已闭（收窄维持） | 信息状态维持，无新证据 | 原 MM 作者票内闭合 |
| F12 | 保留 | CI 结算：CI44 verify step 内部 17 witness PASS 但父 step 取消，不允许内部 witness 升级 step 绿 | ROOT CI 结算/控制层维护票 |
| F13 | 保留 | 不量化未实测提速：FR201 本机 56.482s 仅单机观测；memo 无性能声明 | PR16 说明/CI 结算窗口 |
| F14 | 保留（部分采纳维持） | 契约空页行为撤回维持；算术冗余维护沿原窗口 | 原 T02 契约归口首个维护票 |
| F15 | 保留 | witness 选取无序观察不变 | 原归口 witness 选取维护窗口 |
| F16 | 保留 | 容量 HOLD 不解除；Q5 未决 | 原 T02 契约归口 |
| F17 | 保留 | 语义等价观察无新动作 | 原 T02 前端归口 |
| F18 | 保留 | 依赖归口不变（uv/npm 锁随本轮无变化） | T11+T02 依赖归口 |
| F19 | 保留 | 归档格式/唯一归口要求不变 | ROOT 唯一归档归口 |

### 4.2 authoritative78（historical78）

| 稳定ID | 本轮处置 | 当前依据与最小理由 | 原owner/窗口 |
|---|---|---|---|
| Z F1 | 保留（数值更新） | CI 门禁开放同 gates 群 | ROOT 精确 CI 票；merge 前 |
| Z F2 | 保留 | 未来新增 raw/改规则时点未到 | 未来新增 raw/改规则时 |
| Z F3 | 保留 | 原测试 owner 触及窗口不变 | 原测试 owner 下次触及 |
| Z F4 | 已闭（口径）维持 | 信息状态维持 | 无待办 |
| Z F5 | 保留 | 两测试环境适配窗口不变 | T01 测试维护者下次授权触及 |
| Z F6 | 保留 | 逐项集合（接线事件）不变 | 各接线/维护事件 |
| Z F7 | 保留 | 发布 HOLD 群不关闭 | 各 owner 对应验收前 |
| Z F8 | 保留（部分） | 未知/新家族接线窗口不变 | 未知/新家族接线前 |
| Z F9 | 已闭（限受审面）维持 | 本轮未扩受审面 | T01/T02 触及时 |
| Z F10 | 已闭（既有证据接收）维持 | 无新运行 | 既有证据接收维持 |
| MM R07-01 | 已闭维持 | 口径闭合信息状态 | 本次静态接收 |
| MM R07-02 | 保留 | 未来确增 raw 未发生 | ROOT/T02 未来确增 raw 时 |
| MM R07-03 | 保留 | 独立配置票未到 | 将来独立配置票 |
| MM R07-04 | 重新变开（→F05 同因） | dc6c112e 未登记 | ROOT 文档 owner |
| MM R07-05 | 保留 | overlay 维护窗口（当前 overlay 15147B 保护中） | ROOT/指南 owner |
| MM R07-06 | 已闭（口径）维持 | 事实修订维持 | 本次事实修订 |
| MM R07-07 | 已闭维持 | 口径闭合 | 原测试 owner |
| MM R07-08 | 已闭维持 | 父 FR/具名下游另验边界不变 | 父 FR/具名下游另验 |
| MM R07-09 | 已闭维持 | 既有证据限定 | 既有证据限定 |
| MM R07-10 | 已闭维持（前提已变标注） | 历史口径保留 | 无新复跑票 |
| MM R07-11 | 保留（观察） | PR 说明可解释性待未来 PR | T02/ROOT 未来 PR 说明 |
| MM R07-12 | 保留（HOLD） | vendor/发布升级前 HOLD 不变 | vendor/发布 owner |
| MM R07-13 | 保留 | 契约类型整理窗口不变 | 契约 owner 下次授权整理 |
| R06 Z P1 | 保留（数值更新） | 合并前真实 CI 门禁开放 | 合并前真实 CI |
| R06 Z P2 | 保留 | 新旧 CI 证据接收标准不变（CI44 为旧 deac 候选） | 未来 CI 证据接收标准 |
| R06 Z P3 | 保留 | T01 核心 wire/Agent 接线前 | T01 核心；原始 wire/Agent 接线前 |
| R06 Z P4 | 保留（部分已闭维持） | 详情合同＋消费边界不变 | T01 详情合同＋T02 消费 |
| R06 Z P5 | 保留 | 错误码集可达性接线窗口不变 | 对应方法接线前 |
| R06 Z P6 | 保留（未确认观察） | 无序观察不变 | T01 下次触及 witness 选取时 |
| R06 Z P7 | 已闭（沿既有决定）维持 | 人类决定政策未变 | 政策变更才新人类决定 |
| R06 Z P8 | 保留 | 逐项承接不变 | 各原归口 |
| R06 D1 | 保留 | ROOT 正常票要求不变 | ROOT 正常票 |
| R06 D2 | 重新变开（→F05 同因） | dc6c112e 未登记 | ROOT 文档 owner |
| R06 D3 | 保留 | T01 接线前 | T01；接线前 |
| R06 D4 | 保留（部分已闭维持） | T01+T02 边界不变 | T01+T02 |
| R06 D5 | 保留 | witness 选取窗口不变 | T01 下次触及选取时 |
| R06 D6 | 保留 | 新解析入口窗口不变；本轮 TermInputError 分层未扩拒绝面（本人核） | T02 vendor/T01 入口；新解析入口前 |
| R06 D7 | 保留 | 方法接线窗口不变 | T01/T02 对应方法接线前 |
| R06 D8 | 保留 | T01 测试维护窗口不变 | T01 测试维护者 |
| R06 D9 | 已闭（口径）维持（前提已变标注） | 归档后追加口径保留 | 文档 owner 归档后追加 |
| R06 D10 | 保留 | 父 FR/消费链验收前 | 父 FR/消费链验收前 |
| R06 D11 | 保留 | 整数守卫维护窗口不变 | T02 整数守卫维护窗口 |
| R06 D12 | 保留（有界）维持 | 有界口径不变 | 无待办 |
| R04 Z01 | 保留 | witness 选取观察不变 | T01 触及选取时 |
| R04 Z02 | 不采维持（撤回＋边界保留） | T01 详情预算维护边界不变 | T01 详情预算维护 |
| R04 Z03 | 保留 | T01 接线前 | T01；接线前 |
| R04 Z04 | 保留（部分） | 家族接线窗口不变 | 家族接线前 |
| R04 Z05 | 保留 | 方法接线前 | 方法接线前 |
| R04 Z06 | 已闭维持 | 无待办 | 无待办 |
| R04 Z07 | 已闭维持 | 无待办 | 无待办 |
| R04 M01 | 已闭（历史演进）维持 | 归档票口径 | ROOT 归档票 |
| R04 M02 | 已闭维持 | 无待办 | 无待办 |
| R04 M03 | 保留 | 整数守卫窗口不变 | T02 整数守卫时 |
| R04 M04 | 保留 | 新解析入口前 | 新解析入口前 |
| R04 M05 | 保留 | T01 接线前 | T01 接线前 |
| R04 M06 | 已闭（分层）维持 | 不外推全产品安全认证 | 无待办 |
| R04 M07 | 保留 | 契约 API 整理窗口 | 契约 owner API 整理时 |
| R05 Z P1 | 保留 | 合并门禁开放 | ROOT 合并门禁 |
| R05 Z P2 | 已闭（事实）维持 | 无待办 | 无待办 |
| R05 Z P3 | 保留 | T01 接线前 | T01 接线前 |
| R05 Z P4 | 保留（部分） | 家族接线前 | 家族接线前 |
| R05 Z P5 | 保留 | 方法接线前 | 方法接线前 |
| R05 Z P6 | 已闭（口径）维持 | 无待办 | 无待办 |
| R05 Z P7 | 已闭（口径，诊断选项半面）维持 | R09/R10 演进主题保留；本轮无文件增长新增（memo 叶为新增非改名） | 无待办 |
| R05 Z P8 | 重新变开（→F05 同因） | dc6c112e 未登记 | ROOT 文档 owner |
| R05 MM01 | 保留（数值更新） | 新 CI 后、merge 前门禁开放 | ROOT；新 CI 后、merge 前 |
| R05 MM02 | 已闭（事实）维持 | ROOT/新 CI 后 | ROOT/新 CI 后 |
| R05 MM03 | 保留 | 新包制造票未发 | 新包制造票 |
| R05 MM04 | 重新变开（→F05 同因） | dc6c112e 未登记 | ROOT 文档 owner |
| R05 MM05 | 保留 | 方法接线前 | 方法接线前 |
| R05 MM06 | 保留 | T01 接线前 | T01 接线前 |
| R05 MM07 | 保留（部分） | 家族接线前 | 家族接线前 |
| R05 MM08 | 保留（未确认观察） | 无序观察不变 | T01 下次触及选取时 |
| R05 MM09 | 已闭维持 | vendor/发布 owner | vendor/发布 owner |
| R05 MM10 | 已闭维持 | 无待办 | 无待办 |
| R05 MM11 | 已闭（信息）维持 | 无待办 | 无待办 |
| R05 MM12 | 保留 | 原测试维护窗口 | T01 原测试维护者 |
| R05 MM13 | 已闭（信息）维持 | 无待办 | 无待办 |

### 4.3 R09New19＋OBS（20）

| 稳定ID | 本轮处置 | 当前依据与最小理由 | 原owner/窗口 |
|---|---|---|---|
| Z09-01 | 保留（数值更新） | gates 群同因 | ROOT；精确 CI 票/merge 前 |
| Z09-02 | 保留 | CI41 同步 helper 主题与 CI43/CI44 异步形态分列不合因 | ROOT；真实 CI 归因/回单接收 |
| Z09-03 | 保留 | 引擎退出 UNKNOWN 主题不变 | ROOT；CI 证据接收 |
| Z09-04 | 保留 | T11 merge 后受控维护 | T11；merge 后受控维护 |
| Z09-05 | 保留 | 契约整理窗口 | 契约 owner；下次整理 |
| Z09-06 | 保留（不升级） | 无序观察不变 | T01；触及 witness 选取时 |
| Z09-07 | 保留 | 整数守卫窗口不变 | T02；原整数守卫维护窗口 |
| Z09-08 | 保留 | 下次回单/CI 维护票 | ROOT；下次回单/CI 维护票 |
| Z09-09 | 保留 | native 线＋ROOT 归口不变 | 原 T02 native 线＋ROOT |
| Z09-10 | 保留 | 家族接线前 | T01/T02；对应家族接线前 |
| F-R09-01 | 保留（数值更新） | 下一精确 push 后真实 CI（dc6 尚未 push） | ROOT/原 T02；下一精确 push 后真实 CI |
| F-R09-02 | 保留 | 新旧 CI 归因分列不变 | 原 T02/ROOT；真实 CI 归因 |
| F-R09-03 | 不采维持（撤回） | 维持撤回 | 原 T02 测试/打包 |
| F-R09-04 | 保留 | 真实 Windows 运行观测窗口不变 | 原 T02 测试；真实 Windows 运行后观测 |
| F-R09-05 | 保留 | 真实失败样本尚未存在（本轮 C1 成功无 failureObservation） | 原 T02；真实失败样本存在时核 annotation |
| F-R09-06 | 保留 | 证据接收拦截要求不变 | ROOT；证据接收拦截 |
| F-R09-07 | 保留 | 原 T02 归口 | 原 T02 |
| F-R09-08 | 重新变开（→F05 同因） | dc6c112e 未登记 | ROOT 指定 owner |
| F-R09-09 | 保留 | 每次 CI 完整回单接收要求不变 | ROOT；每次 CI 完整回单接收 |
| OBS-R09-10 | 保留（P3 维护） | 观察项不变 | 沿原 T02 测试窗口 |

### 4.4 extra13（R06 MM01–13）

| 稳定ID | 本轮处置 | 当前依据与最小理由 | 原owner/窗口 |
|---|---|---|---|
| R06 MM01 | 保留（数值更新） | gates 群同因 | ROOT 精确 push/CI 票；merge 前 |
| R06 MM02 | 已闭（事实）维持 | 无待办 | 无待办 |
| R06 MM03 | 保留 | 新包制造票未发 | ROOT 新包制造票 |
| R06 MM04 | 重新变开（→F05 同因） | dc6c112e 未登记 | ROOT 文档 owner |
| R06 MM05 | 保留（撤回加注维持） | ID 仍开、原强论断不采 | T01 契约＋T02 方法出口；接线前 |
| R06 MM06 | 保留 | 原始 triples/Agent 接线前 | T01；原始 triples/Agent 接线前 |
| R06 MM07 | 保留（部分） | typed/裸家族分开窗口不变 | T01 详情合同＋T02 消费 |
| R06 MM08 | 保留（未确认观察） | 无序观察不变 | T01 触及 witness 选取时 |
| R06 MM09 | 已闭维持 | vendor/发布 owner | vendor/发布 owner |
| R06 MM10 | 已闭维持 | 无待办 | 无待办 |
| R06 MM11 | 已闭（信息）维持 | 无待办 | 无待办 |
| R06 MM12 | 保留 | 原测试维护窗口 | T01 原测试维护者 |
| R06 MM13 | 已闭（信息）维持 | 无待办 | 无待办 |

### 4.5 R10ZTop9

| 稳定ID | 本轮处置 | 当前依据与最小理由 | 原owner/窗口 |
|---|---|---|---|
| R10-01 | 保留（数值更新） | gates 群同因 | ROOT；精确 push/CI 票、merge 前 |
| R10-02 | 保留 | CI41 helper 根因 UNPROVEN 与 CI43 异步新形态分列；本轮无新平台证据 | ROOT/原 T02；真实 CI 归因窗口 |
| R10-03 | 保留 | 契约 owner 下次整理 | 契约 owner；下次整理 |
| R10-04 | 保留 | witness 选取/CI-skip 建议归口不变 | witness：T01；CI/skip：ROOT/原 T02 控制层 |
| R10-05 | 保留 | 供应链卫生窗口不变 | T11；merge 后受控维护 |
| R10-06 | 保留（部分采纳维持） | 公式边界（同源窄盲区）不变；本轮 reserve_store/material 预扣结构本人核未改公式 | 原 T02 测试维护/CI 控制层维护票 |
| R10-07 | 保留 | 测试质量维护窗口不变 | 同 R10-06 |
| R10-08 | 保留 | native/测试维护与 ROOT 归口不变 | 原 T02 native/测试维护与 ROOT |
| R10-09 | 不采维持 | 治理观察强论断不采 | ROOT/AGENTS 指南维护归口 |

### 4.6 R10MMTop10＋T11/T12

| 稳定ID | 本轮处置 | 当前依据与最小理由 | 原owner/窗口 |
|---|---|---|---|
| R10-T01 | 保留（数值更新） | 合并门禁开放（CI44 deac 未过，dc6 无 CI） | ROOT 精确 push/CI 票 |
| R10-T02 | 保留 | 新旧 CI 证据接收标准不变 | 未来 CI 证据接收标准 |
| R10-T03 | 保留 | 覆盖面限制观察不变 | 未来 CI 证据接收标准 |
| R10-T04 | 保留 | 测试覆盖面限制不变 | 原 T02 测试维护者 |
| R10-T05 | 不采维持（撤回/收窄） | T05 算式口径维持 | 原 T02 测试维护者；本票不改码 |
| R10-T06 | 不采维持 | 命名/门禁矛盾推论不采；未加 continue-on-error | ROOT／CI 维护窗口 |
| R10-T07 | 保留 | 发布/供应链 HOLD | 发布/供应链 owner |
| R10-T08 | 保留 | CI 维护票 | CI 维护票 |
| R10-T09 | 保留（部分采纳维持） | 机器校验在位＋未穷尽边界维持 | 原 T02 测试维护者；本票不改测试 |
| R10-T10 | 不采维持 | renderer 更早拒绝⇒缺陷推论不采；仅可选注释 | 原 T02 前端归口；本票不改码 |
| R10-T11 | 保留（部分采纳维持） | 生成来源锚≠head 事实维持；本轮无 fixture 变更 | 原 T02 fixture 维护归口 |
| R10-T12 | 不采维持 | "仅 3/9"与补五类不采；九 rules 正反断言在位（历史核，本轮未改 test_storage.py） | 不采建议 |

### 4.7 R11 新增（Z3＋MM9；共 12 位置）

| 稳定ID | 本轮处置 | 当前依据与最小理由 | 原owner/窗口 |
|---|---|---|---|
| Z11-OBS-01 | 保留（非缺陷维护观察） | schema 合法域空段一致拒绝、Python 冗余下界口径不变 | 原 T02 契约归口维护票（同 F14） |
| Z11-R01 | 保留（数值更新） | CI44 Windows：整例 180000ms、failedPoll 411.396ms、五相合计 78744.649ms、poll 外 98004.098ms、trace 四大组合计（read 39.97s/toBeVisible 23.13s/reject 13.50s/commit 7.81s）；余量归因仍 UNKNOWN，不设余量门禁 | 下一授权 Windows 运行读取新计时；原 T02 测试/ROOT |
| Z11-R02 | 保留 | CI43 异步形态 UNKNOWN 不变；本轮本机 C1 成功未触发失败 catch | 未来授权 Windows 失败附件/CI 归因；原 T02 native/ROOT |
| R11-T01 | 保留（数值更新） | 完整三 job CI 合并门禁开放；不要求首次 push 前先有新 CI | ROOT 精确 push/CI 票；merge 前三 job 回单 |
| R11-T02 | 保留 | 真实 Windows 失败附件仍无（O081 C1 成功、成功输出无 failureObservation 为预期） | 原 T02 测试/ROOT 未来 Windows 实际证据窗口 |
| R11-T03 | 保留（数值更新） | CI44 佐证累计超时事实与"计时只测量"边界（见 Top10-1）；修复/性能未证，不加预算 | 原 T02 测试/ROOT 未来完整 CI 后结算 |
| R11-T04 | 保留（未确认观察） | 无 ORDER BY 事实不变；无构造反例不升级 | T01 下次触及 witness 选择时 |
| R11-T05 | 保留 | TS 宽类型维护观察不变 | 契约 owner 下次授权整理类型时 |
| R11-T06（R11-S01 alias） | 保留（常量维护边界） | 本人本轮复核：mainline-ownership.ts 512 页循环、SEGMENT\_BYTES=32768、MAX\_DOCUMENT 16MiB⇒≤512 段、nextOrdinal 仅 complete 为 null（双端 matcher 一致） | 原 T02 契约归口未来改 SEGMENT\_BYTES/MAX\_DOCUMENT/页数/pageSize 时 |
| R11-F01 | 保留（事实维持） | M0 两份计划版本化事实不变；与 coverage F01 分开 | ROOT/AGENTS 指南维护归口 |
| R11-F02 | 保留（事实维持） | O074 exact2 Prettier/AST 保全限证不变；本轮无 Prettier/AST 行为变化 | 本报告事实处置/O074 原静态资格窗口 |
| R11-F03 | 保留（索引口径维持） | extra13 与末 13 分别计数口径不变（本报告 §4.4/§3 分列） | 本人意见索引与 ROOT 归档原窗口 |

**处置汇总（逐表重数）**：已闭/维持已闭（限本轮范围）29；不采（维持撤回/收窄）8；重新变开（同一 F05 型登记缺口）7（F05、R06 D2、MM R07-04、R05 Z P8、R05 MM04、R06 MM04、F-R09-08）；保留 131（含数值更新项 Z08-01/Z08-06 分层/F02/R06 Z P1/R05 MM01/R06 MM01/Z09-01/F-R09-01/R10-01/R10-T01/R11-R01/Z11-R01/R11-T01/R11-T03）；29+8+7+131=175。UNKNOWN 主题未关闭任何一项。所有原 owner/事件窗口不变、不扩大、不提前执行。

## 5. 本轮四叶实现的本人独立核验结果（不只接受作者说明）

**IRI memo（storage.py + 29 例测试）**——本人全文亲读后独立复核以下断言，全部成立：

- `_plain_snapshot_data` 资格扫描：手工栈、精确类型（`kind is dict/list`，子类即不合格）、键必须精确 str、8192 步与 64 栈深上限，全程仅 builtin 迭代（`dict.items(value)`/`iter(value)`），不触发用户方法；测试以 Untouched 子类/环/2048 深度/10000 项四类反例证"不合格只回原路径"。
- `_original_snapshot_definition`：经 `type.__getattribute__` 读原始 `__mro__`/`__dict__`，首个含 `_definition` 命名空间必须是 `_MEMO_DEFINITION` 且 code 相等；自定义子类覆盖 → 整次原分派（CustomStore 测试 3 次 parse 佐证）。
- `_original_snapshot_terms`（v2）：11 项身份门，含 v2 新增 `term.__globals__.get("iri") is _MEMO_IRI`。本人推演 counterexample 计数自洽：monkeypatch rdf_snapshot.iri 后门在资格判定即失败 → 两对象都走原 term → 第 3 次 helper 调用抛原 RuntimeError（entry iri + result iri + 第二对象 entry iri），恰 1 次真实 parse——与 29 例最后一测断言（calls==3、real\_parses==1、failure 对象同一）完全一致。删除该行即逐字恢复 v1（独审已证，本人读其方法）。
- `_SnapshotIRIObjects.noncanonical`：命中前逐次重验身份门；非精确 str/非 `<…>`/门失败 → `disable()` 后走原 `term(value).n3() != value`；仅"URIRef 精确类型＋str 渲染＋canonical False 比较"入 16 上限别名集；17 个不同值后不逐出、不缓存、继续逐次真实解析（19-parse 测试）；非 IRI/Literal/str 子类分支在任何命中前永久禁用；异常/真值语义原样传播。
- 校验顺序与错误文本不变：定义记录形状→重复→payload canonical→定义校验→引用核对→事实 7 键形状/重复→ownership 分支（manual 三非空约束 / managed 双非空串）→对象 canonical→mappingState 形状，逐条错误文案与既有文本一致（测试 `^…$` 精确匹配）。
- 预算归属不变：`_snapshot_state` 本身不扣账；material/work 预扣在调用方 `reserve_store`（32×validation\_bytes+2048×rows+32768 等）与 `_WriteAdmission.check_final_material`→`material_profile`→`admit_terminal_growth`（每非终态 job 4096B、run\_terminal 269B 口径），`_final_material_cost` 为 schema 聚合常量非付款证明——本人核 mainline.py/project\_host.py 确认公式未被本轮改动。
- 结论：**memo 不新增业务拒绝、不改变任何错误边界，身份门失效时只禁用自身并回落当前绑定实现**；无 P1/P2 发现。

**C1 被动观察（native-recovery.cjs + observer 单测）**——本人全文亲读后独立复核，全部成立：

- 原控制面保持：40000 watchdog/150 bootstrap/250 input/3000 focus deadline/50 聚焦轮询，1×crash、2×focus、mouseDown/up 各一次、`for(;;){}`、成功三窗条件（events 含 unresponsive＋prompts==2）、`String(error)`→write→`app.exit(1/0)` 顺序；成功输出零诊断（O081 c1-evidence 原件核）。
- 新增仅被动：16×8 数值环、16 计数、饱和 2147483647、非法整数 −1、一个 latestWindow 别名；15 个 record 控制点；save(error) 才附 failureObservation，4096 UTF8 cap（量整属性 JSON、两空格）超限转固定兜底（两 UNKNOWN＋unavailable:'byte-cap'）；observer 序列化/读取/记录异常全部隔离，原 write 异常身份与短路第二 input 语义保持（VM 测试逐项断言）。
- 边界正确表述：`registered` 只证 helper 监听完成；call issued/Promise/input returned 不构成 renderer 循环或产品 handler ACK（counts[7]==1 的注释级断言在位）；12 例为 fake Electron/fs/inspector/timer 的 VM 合成，非真实原生事件证明。
- 结论：**无 P1/P2 发现；真实失败捕获能力仍未被平台样本证明（Top10-2）**。

**累计面（FR200/201/契约/主进程/renderer/CI 观测）**：本人差异级亲读全部产品路径；renderer 事实 ID 生成改为与 `Store.digest([S,P,O])` 一致的 SHA-256（crypto.subtle）并拒孤立代理；manualFactPlan 歧义判定细化为逐行条件；ownership detail 全链（coordinator→job\_store 分段持久化→双端 matcher 含自含 SHA-256→主进程 epoch 复核→preload 业务命名通道→renderer 512 页拼装与 view model）闭环自洽；TermInputError 把已知词法/策略拒绝定为 INVALID\_REQUEST 而未知解析失败保持 UNKNOWN/HOLD 分层；text 页最终编码器预付（`_RowsPrepaid`）不重复扣费。未发现新增架构不变量违反（本地优先/渲染端隔离/CSP 单源/确定性解耦/存储唯一源真相/数据层次/失效规则/模型外发未接入/错误边界九项逐条对照通过）。

## 6. 本人本轮新发现（单列；原 owner/窗口保留）

- **N1（P3，观察；映射 F13/升级隔离主题，不新开门禁）**：memo 身份门清单不含 rdflib 解析器插件注册表/blank-node 计数器等模块级全局态。对当前仅缓存"已证 URIRef 且 n3()==原串"的 `<…>` 值，Literal/转换器路径已被"命中前禁用"覆盖，实际暴露面极窄；但未来 vendor 升级/解析器全局态变更时该假设需重验。建议列入 T11/vendor 升级票复核项。
- **N2（P3，观察；映射 R11-T02/F-R09-05）**：诊断有界性（16 行环覆盖、4096B 兜底）在真实失败发生时可能欠捕获；这是明示取舍，无需当前动作。
- **N3（P3，代码观察，无需动作）**：`noncanonical` 在别名集满 16 后仍保持启用并对后续新值逐次真实解析（正确保守行为，测试覆盖）；`_original_snapshot_terms` 每值重验 11 项身份带来有界常数开销——性能中性与否未测量，不构成声明。
- **N4（P3，维护观察）**：coordinator `serve()` 的 `prepare_mainline_store` 引导条件含 `ordinary_authority is None and query_dispatch is None`；若未来 profile 装配传入任一非 None 值，引导准备将被静默跳过（现生产装配不可达；本人仅读 diff hunk 级上下文）。建议未来接线票中显式断言或注释该前置。
- **登记缺口（映射 F05 家族，见 §4）**：dc6c112e/R12 未入 status.md/m0-checklist——本人亲核两文件末段；按既有 F05 处置模式登记为重新变开，owner 补登即可，非源码阻断。

除上述外，本人独立审查未发现 base→dc6c112e 的新增 P1/P2 源码缺陷。

## 7. 当前源码阻断、未来完整 CI/merge 条件、独立 HOLD、维护建议

**当前 push 前源码技术阻断：0**（本人对全部 135 差异路径的产品代码/测试/配置/依赖逐类核对；四叶与累计面无 P1/P2；与 R11 双方及 ROOT 的"push 前源码阻断 0"结论独立一致地再现）。

**未来完整 CI/merge 条件（本人不放宽、不变造新门槛）**：dc6c112e 精确 push 后完整 Quality/macOS/Windows 三 job 真实回单；同交付下引擎 3769（现 3798 口径随新增测试更新，以当次全集为准）逐 node/逐项通过或原有据条件 skip、自然 0、无失败/早停/取消/timeout/NOTRUN；全部后继 typecheck/build/E2E/package/verify 与 Quality packaged recovery 步骤自身 success；原 15/20 分钟预算不变；Windows FR201 超时与 C1 异步家族须真实归因或处置（case7 若复发须定因）；远端 develop SHA/tree/功能复核后另票 merge。本报告不授权 push/CI/merge。

**独立 HOLD（全部保留，不关闭）**：组织法律/IP/隐私、真实 human bus factor、supply-chain/license/签名公证/干净设备断网、跨 OS 与参考 8GB 设备、Q5 容量与旧超限库恢复、损坏 SQLite 物理保护、unknown parser/N3Store 坏 snapshot、未具名下游/其余 ownership 家族/剩余 Undo GUI、包内完整 GUI、engine 自然退出及 Windows 后代、sys.path 等价、旧 79F 残留、CI41/CI43 根因。整体可用已合并 FR 仍 2/17（FR401/402），HOLD 关闭 0，D8 未用，Goal/M0/release 未完成，T04 不推进。

**维护建议（最小集）**：(a) owner 常规 docs 后继补登 dc6c112e/R12 状态节（F05 型，双状态文件＋O081 指针）；(b) 授权 Windows 运行中用五相计时＋trace 分组对 FR201 180s 做归因，动预算/断言结构前走独立评审；(c) T11/vendor 升级票把 memo 身份门清单与解析器全局态列为复核项；(d) 下次真实平台失败优先收取 failureObservation 原件再评估诊断扩界。

## 8. 最终判定

**ConditionalPass（限定技术阶段）**。

- 依据：base→dc6c112e 全部 135 差异路径本人独立审阅，四新叶逐行核验无 P1/P2 且与两份被独审补丁逐 bytes 相等；O081 同源绑定（实际 deac+四 WIP 运行→check 双自然 0 191.80s/TS1924/Python3748P+50S、native24 双 0 154.99s/21P+3原S/57 事务/43 拒绝/rev22/case7 单提交/12 计时副本 sealed）经绑定审计与我本人的原件抽核成立；本轮 160 项与 175 个稳定位置逐项处置完成；无 push 前源码技术阻断。
- 条件（全部保留、逐条可核）：① 完整三平台 CI merge 门禁开放（dc6 无新 CI；CI44 deac overall cancelled/Windows failure/Quality 取消）；② Windows FR201 累计超时与 C1 异步家族根因 UNKNOWN，本机/合成/一次成功不得倒填；③ 引擎自然退出与后代 UNKNOWN；④ 全部 §7 独立 HOLD 不关闭；⑤ F05 型登记缺口待 owner 补登；⑥ 本判定不是产品 Pass、完整 CI 放行、merge 或发布授权，两份完整原稿与处置须经 ROOT 实际接收后方可进入下一票。
- 本判定为本人据实独立给出，未预设通过；与 R11 两作者"限定技术阶段 ConditionalPass"为同型但独立重新达成，不继承其票。

（完。本报告仅写入指定路径；本人未修改任何实现/测试/配置/依赖/验收，未运行产品与验证命令，未 git 写操作，未读取另一作者本轮任何材料。）


---

# 追加（同一 R12 会话补读与有效事实更正；原 56528B 前缀逐字节保留）

本节为同 SID 后续补票：完成原 §1 如实披露的必要正文缺口，并更正原稿统计/事实错误。不改变原稿文字；若本节与前文冲突，以本节为准。原首判 **ConditionalPass／push 前源码技术阻断 0** 经补读后维持，全部条件保留并按下文更正表述。

## A. 补读清单（文件×亲读区间×级别×真实断言/边界）

**全文亲读（本次补完）**：
- `tests/e2e/t02-fr200-fr201.spec.ts` 2174 行全文（原读约 1/3，本次补 395–2174）。补读段真实边界：`commit()` 逐字段核对 marker/job 等式（jobId UUID、succeeded、inputSnapshotId 前后不等、planHash、commitProgress atomic）；FR200 四类矩阵的 create/edit/copy/delete 全 Diff 与 siblings 保全；FR201 十元组多值、词法受控拒绝全族（R02 五语法、R03 数字语言、urlsplit 四 authority、manual subject/predicate 逐字段隔离、4301 位整数、显式 xsd:string 别名、全角斜杠）、无静默规范化断言；保留身份 OWNERSHIP_CONFLICT 的 UI 定位两记录；**失败 catch 有界只读诊断**（≤2s/179s 余量、pack 截断、DOM-before-reads 顺序、仅既有只读桥方法、诊断失败不吞原始错误）；第三例数字子标签独立 cohort（`fixtureIsolationIsNotCapacityRepair`，不关闭 rev24 committed-but-unreadable 保留失败）。
- engine mainline 7 测试族全文（25/5/13/17/4/3+外延=实际用例数远超函数数）：`test_mainline_dispatch.py` 523 行（大定位器 40000 字符×manual/managed、逐页 sha256/totalBytes 拼装、iterdump 全库不变含无新游标、损坏四型→STORAGE_FAILURE+hold、第二段 put_blob IntegrityError 全回滚、admission 不毒化 full reader、私有 admission 向量 (True,False) 且不退款、坏 blob 在 intern 复用前有界预付、行帽去重回滚）；`test_mainline_manual_input_rejection.py` 1034 行（同宿主拒绝→同宿主后续合法提交、term/preview/sqlite/snapshot 四型未知故障→INTERNAL_ERROR+hold+reply.unknown、独立 stdio 子进程端到端+物理库文件字节不变+自然退出 0、输入边界不把未知解析器/n3/urlsplit/manual-IRI 故障分类为已知拒绝、vendor 专属输入类型断言 fr201.3、三 reason 全分页+原 ID 后续 Job、single-declaration 三变体含"同计划又删又改"保原 UNKNOWN）；`test_mainline_language_input_rejection.py` 326 行（复用 owned 断言族、数字子标签语法与规范大小写政策分离、独立 stdio 物理文件 sha 前后相等）；`test_mainline_read_work_budget.py` 559 行（21+1 真实提交+16 段 opaque 到达 64MiB 工作界、core 读可行而默认 full reader 拒绝、SQL trace 证明 lower/authorized-plan 两段拒在不同聚合前、损坏六型→认证后 hold、json_extract 授权拒绝无零回退）；`test_mainline_postwrite_admission.py` 860 行（三轴×[−1,0,1] 终态余量代数、2742<4096 尾证、32 次真实草稿增长到受控拒后小后继仍可写、排队 commit/cancel/fail 全量重检且仅 Job DTO 变化、两项目 pending 全局余量、前台/后台 scope 不可借贷/退款、after_commit 重入拒、清理失败保原错误与持有、DTO 不能 bind、未清 boot writer 不可被继任者当干净账本、clean close 移交真继任、八态继任者不弃未清算前任、继任者不能接管原排队/活动 Job、独立 stdio 增长拒后同宿主完整提交、boot 重启对账 ENGINE_EXITED）；`test_mainline_postwrite_rows_budget.py` 395 行（243 行×5 列真实查询、固定 final fee {1114112,8192,134217728} 每页恰一次、边界事件 before==after 无错、预付拒原子且同宿主续行、预付费不可借贷/重复消费）；`test_mainline_postwrite_text_budget.py` 320 行（56309 字节 ASCII/多字节文本冷历史、逐页身份偏移/游标唯一、final 预付 {528384,256,1052672}、拒后同宿主合法续行、游标回调吊销在最终编码器前拒绝且不产新游标行）。
- `tests/e2e/ui-observation.ts` 195 行全文（严格 role 定位失败关闭、无 shadow/覆盖、Playwright1.64.1 原生 disabled 语义复刻、单槽诊断 16KB/4096 双界截断）。
- contracts：`src/index.ts` diff 全（DesktopIpcMap 通道、桥方法、Ownership 类型、`reassembleOwnershipDetail` 有界 capture：≤16384 节点/深 8/串 ≤43692/数组 ≤512/总字符 ≤512×(43692+1024)，逐页 matcher 链+SHA-256+fatal UTF-8）；`v2/registry.json` diff 全（两处 method 清单加 `project.ownership.detail`→registryHash 更新）；`v2/fixtures.json` diff 增量区（新增 named ownership request/response 等向量+registryHash 引用更新）；`v2/schema.json` 结构级+15 个 ownership defs 全读（两 kind oneOf、16MiB 串界、sourceBaseRevision ≤2^53−1）；`v2/binding-regressions.json` diff 仅 registryHash 值替换（抽读核实）。
- scripts：`run-engine-tests.py` 470 行全文（两分片 dispatcher：全量收集→按 CI40 历史跨度权重 partition→每子进程独立 temp/owner/session 身份→逐 node setup/call/teardown 记账→覆盖全集对账；POSIX 进程组/Windows CTRL_BREAK+taskkill 且后代 UNKNOWN 无句柄；信号不越 Popen）；`engine-test-reporting.py` 124 行全文（只读事件流+collection identity：rootpath/configSHA/编码身份）；`repack-rdflib-input-types.py` 前 120/170 行（upstream/patch/after 三 SHA 钉、逐 RECORD 行先验、exact patch 上下文断言、ZIP_STORED 确定性重建；尾部为写出与复验）。
- `tests/e2e/native-driver.ts` diff 304 行全文（45s 绝对 deadline、waitFor 统一取消注册、readiness ≤450×100ms 只等 electron 映射不加载 shim、真 whenReady 后才一次性 require 原 helper、发送边界复检、socket 生命周期清理）；`csp-lifecycle.spec.ts` diff 63 行全文（失败才读一次、区分 read/parse/attach 失败并附原始字节）；`mainline-consumer-first-ack-loss.spec.ts` diff 主体（observation slot 接线+关键拒绝/和解断言）。
- 单测：`t01-business3-contract.test.ts` 全（TS 自含 SHA-256 对 Node 权威实现 8 长度对照、相关性/合法错误才匹配）；`t01-mainline-contract.test.ts` 全（>16KiB 定位与 legacy 身份在私有 capture 下保全、篡改首页后 reassembler 仍正确）；`t01-mainline-ipc-delivery.test.ts` harness 全（sender/frame 可信校验+会话绑定）；`t01-mainline-project-service.test.ts` harness 头部全（MemoryChild 真实 Supervisor/TaskService）；`t02-ownership-detail.test.ts` 前 560/843 行全文（四 reason 映射不改原文、>17KiB 原样、14 类首页篡改只调一次即拒、6 类后页坏、reassembler 拒四类文档、SHA await 后的 requireCurrent 与私有页捕获、Session 仅发布验证后 VM 不建事务、非法 detailRef 不调 getter、同码 throw/未知码/错 message/多参数不当作授权、8 类安全拒不留痕、同步清除族）；其余尾部为同型生命周期/订阅例（结构级）。
- fixture `tests/fixtures/t02-manual-fact-id.json` 前 60/139 行（来源针 sourceStorageSha256/sourceRdfSnapshotSha256+golden 向量族：中文 IRI、非 BMP、转义/多行字面量、plain "7" 等；剩余同型向量）。
- 小 diff 全读：`licenses/NOTICE`（fr201.3 本地修订透明披露+补丁/来源指针）、根 `pyproject.toml`（T02 round 作者 .md 的 ruff format 排除 literal）、`packages/engine/pyproject.toml`（rdflib 精确版本+vendor wheel path source）、`package.json`（engine:check 接 run-engine-tests.py）、`uv.lock`（rdflib path-source+wheel sha 钉替换，结构级抽读）；`mainline-session.ts` diff 尾部（OWNERSHIP_CONFLICT→readOwnershipConflictDetail 流、requireCurrent 栅栏、STALE_CONTEXT invalidate、discard 清 ownershipDetail）。
- 历史件：`docs/reviews/T02/fr200-fr201-20261024/independent-review-source-94e20d4a.md` 头 30 行（早期四叶修复阶段独立审查，其自身范围声明，历史身份）。

**结构级+关键区（如实标注，未逐行）**：`tests/unit/native-driver.test.ts`（it 标题+关键 expect：监听清空、ENOENT→SIGKILL、迟到 ready 忽略、映射等待不载 shim、单次 helper、计时器零残留）；`t02-manual-preview-lifetime.test.ts`/`t02-mainline-consumer.test.ts`/`t02-mainline-metadata.test.ts`/`t02-manual-fact-id.test.ts`/`t02-ownership-detail-view.test.ts`/`t01-mainline-real-runtime.test.ts`/`ui-observation.test.ts`（it 标题全列+关键区抽读：如 manual-fact-id 的 Python golden 对照与孤立代理拒绝、metadata 的 M/RDF 分离与歧义拒绝、view 的 8 处转义断言与只读面、real-runtime 的四 ownership 家族+十七连提交不重放）。**未读残留（诚实列出）**：vendor `notation3-input-types.patch` 136 行未逐行（内容效果经 PROVENANCE/NOTICE/repack 三 SHA 与 `test_vendor_source_errors_have_dedicated_input_type` 断言锚定）；`fixtures.json`/`binding-regressions.json` 既有大部与 `schema.json` 其余 ~430 defs（属 base 既有契约面，经其测试消费）；`t02-ownership-detail.test.ts` 尾 283 行；`native-driver.ts` 本体（非 diff）既有部分；O081 check/stdout 全量日志（读独核摘要+关键计数）；O079/O078 内部；round-04~10 作者原稿正文。

## B. 有效事实更正（原稿错误，逐条）

1. **§3 统计行错误**：原自报"33/68/58/3"和为 162 却称 160。机械重数原表实际为 **31 适用/56 部分适用/70 不适用/3 无法确认=160**（owner 程序重数同）。错误在自报计数而非行内容。见 D 节最终统计（含本人主动改判）。
2. **§3 依据基线陈旧**："产品正式能力仅 health＋存储内部 API"抄自 2026-10-20 旧快照，与本候选及 R11 JOBS 限证矛盾。更正：当前正式能力=health＋T01/T02 business3 mainline 链（project create/open/read/draft.save/**ownership.detail**、changeset preview/confirm/commit Jobs、查询定义/执行/结果 rows/text 分页链、查询结果**当前页 CSV 导出**）＋存储内部 API；仍不含模型/推导/沙盘业务执行。
3. **#128（undo）依据更正**：原句"Undo GUI 未验"过时。本人核：`OntologyMainlinePage.tsx:401` 预览撤销按钮、`mainline-session.ts:393` `prepareUndo()`（新基准新 operation，非本地反演）、`tests/e2e/t02-ontology-mainline.spec.ts:301/349-358` 独立逆向/正向完整 Diff 与 Undo-of-Undo、**O081 native24 第 18 例本轮实际 passed（5120ms）**。更正口径：**定义级 Undo/Undo-of-Undo/owned restart 已实际验证**；其余 Undo/ownership 家族 HOLD 保留，不外推全 Undo 已验。分类维持部分适用。
4. **#33（exports）改判：不适用→部分适用**：本人核 `QueryResultPanel.tsx:313-320` "导出当前页 CSV"（downloadCsv(currentPageCsv(...), 'query-current-page.csv')）与 `t04-query-variants.spec.ts:813/914/964`、`t04-query-workspace.spec.ts:595-597` 真实下载验证。当前产品已有查询结果页级 CSV 导出（T04 交付并 native 验证）；本票 FR200/201 不交付全项目导出，亦不扩大为全量导出或 M0 已交付。
5. **末 13 题语义边界（#155/#156/#157/#159 改判、#158 依据更正）**：#155（QA）→**无法确认**：独核/绑定审计/ROOT 接收机制实际发生，但不证明原文真人 QA 职责已具备；#156 维持适用但依据限定：迁移前进/回退/故障注入在**真实但临时的** SQLite 库上验证（468=424P+44S 为既有证据），非生产活库，人类 backend 角色未证；#157（tech lead）→**无法确认**：ROOT 门禁/范围冻结/Q2-Q9 停下来问为 agent 流程，真人 tech-lead"说不"职责未证；#159→**无法确认**：ROOT 为 agent 流程；v1 P2 由 agent 独审发现、owner 人类修复为真实参与实例，但不证明"AI 不能调试时"的人类调试能力已备；#158 维持部分适用但依据更正：原文"works for every customer at once"不限云并发——本地单用户不能排除多 OS/参考设备交付题意，正确依据是**跨 OS（macOS15/Win11）/参考 8GB 设备 HOLD 未验、交付规模化未证**。#146/#147/#160 维持无法确认。
6. **Top10 第 10 条错误**：observer 超 cap 固定兜底（`native-recovery.cjs:118-127` 本人核）仅 `{schema, limitBytes, unavailable:'byte-cap', rendererLoopStarted:'UNKNOWN', productHandlerEntered:'UNKNOWN'}`，**无 requiredBytes**；requiredBytes 只存在于 t02 spec poll-timing 注释兜底（spec 约 159-167 行）。原句混淆两者。更正后该条风险表述：真实失败时 16 行环/4096B 兜底可能欠捕获且兜底不提示所需字节数——设计取舍，非缺陷。**"原票内扩界"仅为未来另一精确 ROOT 票下的讨论方向，当前无任何扩 16/4096 观察界、40/45/90 与 5/60/180 预算或 CI 15/20 分钟预算的授权**。
7. **未来 CI 发现集统一（Top10-3 与 §7 冲突消解）**：未来 CI 以**当次完整收集全集**为准；当前 O081 为 **collected 3798＝原 3769＋新增 29 memo 测试**，未来 CI 必须包含这 29 例；3769 仅作 CI43/44 历史数量引用。三 job、原 15/20min、原有据 skip、自然终态 0、全部后继步骤与 Quality packaged recovery 资格不变，不改预算/断言。
8. **实际运行身份表述**：完整 check/native24 实际在 **deac095f checkout＋精确四 WIP** 上执行；dc6c112e 仅经四 Git blob 内容逐字节相等事后绑定。不称任何原运行发生在已提交 dc6c112e 上（CANDIDATE-BINDING 与独审同口径）。
9. **§7 归因表述更正**：原句"Windows FR201 超时与 C1 异步家族须真实归因或处置"改为——（a）**复发时**：按既有门禁接收真实证据并定因处置（case7 若复发须定因且完整 CI 绿）；（b）旧 CI41/CI43/O079 根因 UNKNOWN **保留不关闭**；（c）**不新增**"无论复发与否均须先证明旧根因才可 merge"的先决条件；不以本机/合成/一次成功倒填任何旧因或旧失败。
10. **§4 处置汇总计数错误**：原自报 29/8/7/131 不符。机械重数原表为 **已闭 31／不采 8／重新变开 7／保留 129＝175**（owner 程序重数同）。错误在自报计数；逐 ID 行内容无误。
11. **F01 口径**：原稿在覆盖未完成时即写"已闭（本轮流程）"并在 §5/7/8 用"全部 135 逐类核"隐含升级，不当。本次补读完成后，F01 按本人有效口径闭合：**本限定技术阶段的必要正文阅读已完成（A 节清单为准，含如实标注的结构级与未读残留）**；"逐类核对"更正为"分类核对＋A 节亲读区间"；ROOT 对本票流程的接收仍待定。

## C. 补读后技术结论

- 补读未发现任何新的 P1/P2；四新叶与累计产品面的原结论（§5）全部维持。engine mainline 测试族、native-driver/csp/ack-loss、单元测试族的真实断言与我在原稿 §5 的独立核验相互印证（预算公式 {1114112,8192,134217728}/{528384,256,1052672}、512 页/32768 段、身份门、HOLD 语义、无借贷/退款、成功路径零诊断等均与实现一致）。
- **N1–N4 逐项复核（可达性/依据/建议窗口）**：N1（memo 身份门不含解析器全局态）——当前可达性：仅当 rdflib 解析器模块级全局态在进程内被改动且作用于已缓存 `<…>` 串；现无产品路径改动之（测试以 monkeypatch 显式模拟，且此类改动多会破坏身份门本身）。依据：storage.py:99-112 门清单＋rdflib 插件注册机制。建议窗口：T11/vendor 升级或任何解析器全局态变更票。N2（诊断有界性）——当前可达性：仅在真实 C1 失败发生时呈现；成功路径零诊断（本轮实证）。建议窗口：真实失败样本接收票。N3（门满后逐次真实解析/每值重验门开销）——核实为正确保守行为＋有界常数开销，无需动作。N4（coordinator `serve()` 引导条件）——**当前生产装配不可达**（business3 且 ordinary_authority/query_dispatch 双 None 才 prep；生产路径两者均 None 方成立，TEST_MODE 有守卫）；维持未来接线维护观察，不构成当前回归或新门禁。
- 状态登记缺口（F05 型，dc6c112e/R12 未入两状态文件）事实保留；按现行流程为：实现冻结→本次指定双审→ROOT 实际接收两份原稿→**另票** docs 归档/状态追加→push。该缺口是流程登记项，**不是当前源码缺陷**；本人不抢改受审 HEAD。

## D. 最终统计与判定

- **160 项最终统计（含本人改判 5 项：#33 不适用→部分适用；#155/#157/#159 部分适用→无法确认；#128 依据更正不改档）**：**适用 31／部分适用 54／不适用 69／无法确认 6＝160**。分类是适用性，不是产品通过数。
- **§4 处置有效重数**：已闭 31／不采 8／重新变开 7／保留 129＝175（机械口径；F01 现按 B-11 有效口径闭合；R11-S01 为 R11-T06 alias 不另计；数值更新项见原表）。原 owner/事件窗口/alias 全部保留不变；补读未引发任何 ID 的处置变更。
- **最终独立结论：ConditionalPass（限定技术阶段）维持；push 前源码技术阻断 0 维持。** 条件（更正后全集）：① 完整三平台 CI merge 门禁开放（dc6c112e 未 push 无新 CI；CI44 为 deac 候选 overall cancelled/Windows failure/Quality 取消）；未来 CI 以当次全集（现 3798）逐 node/原有据 skip/自然 0/全部后继与 Quality packaged recovery 自身 success、原 15/20min 不变（B-7）；② Windows FR201 超时与 C1 异步家族按 B-9 双轨口径处理：复发须定因处置、旧 UNKNOWN 保留、不加证因先决；③ 引擎自然退出与后代 UNKNOWN；④ §7 全部独立 HOLD 不关闭（2/17、D8 未用、法律/隐私/bus factor、供应链/签名公证/干净设备、Q5 容量/坏库物理保护/unknown parser/N3Store、剩余 Undo/ownership 家族、包内完整 GUI）；⑤ F05 型登记缺口待 ROOT 接收后另票补登；⑥ 两份完整原稿与处置经 ROOT 实际接收后方可进入下一票；本判定不是产品 Pass、CI 放行、merge 或发布授权。
- 原 §8 判定全文与条件保留；本节更正并入其条件集。本次追加未运行任何产品/验证命令、未改任何受审文件、未读取另一作者本轮材料。

（追加完）

---

# 追加二（第三轮必要正文补读完成；前 75020B 前缀逐字节保留）

本节为同 SID 第三轮补票。冻结校验：追加前文件 75020B/SHA256 `a31c2e4c…57`（＝zcode-natural-02.md）；本轮仅末尾追加。首判 ConditionalPass／源码阻断 0 与追加一全部更正保留；本节只新增完成项与四点口径更正，不预设判定。

## E. 本轮补读完成清单（文件×精确级别）

**A 类（新增文件全文亲读，本轮补完）**：
- `scripts/repack-rdflib-input-types.py` 121–170 行：dist-info 改名与 METADATA 单处版本替换、非目标成员字节不变断言、RECORD 重建、拒绝覆盖既有输出、ZIP_STORED＋固定 1980 时间戳/0644 确定性写出、输出自述 JSON（wheel sha/来源三 SHA/licenseUnchanged）。来源链完整。
- `tests/fixtures/t02-manual-fact-id.json` 61–139 行：余下 8 个 golden 向量逐一核（plain-seven／language-seven／integer-seven／decimal-lexical 1.50／boolean-typed／date-typed／unicode-nfc é／unicode-nfd é́ 分立），与前 5 个（first-real-ui-tuple、chinese-iri、non-bmp、escaped、multiline）合计 13 向量全读；NFC/NFD 同形异码两向量 id 不同，印证"不归并"。
- `vendor/rdflib/notation3-input-types.patch` 136 行全文：7 个异常类（Notation3InputError 基类＋RelativeIRIBaseError/UnicodeCodePointError/UnterminatedStringError/MissingDatatypeError/InvalidLanguageTagError/IntegerDigitLimitError，各自继承原 ValueError/AssertionError/IndexError 族）＋7 处窄替换（join 相对基、unicodeExpand 仅 >0x10FFFF 抛类型错其余照旧、整数位限保留 sys.get_int_max_str_digits、^^ 后缺 datatype URI、两处未终结串、\\U 转发仅捕 UnicodeCodePointError、语言标签复用 rdflib 自身 _is_valid_langtag）。与 NOTICE 披露、repack 三 SHA、rdf_snapshot 的 TermInputError 映射一致。
- `vendor/rdflib/PROVENANCE.json` 全结构＋全部来源针值：upstream wheel/source/LICENSE 三针（30c0a3eb/a3e36163/53a705e5）、artifact 针 2379774B/99fab7bd（＝uv.lock 钉）、patch 针 de5755d6（＝repack PATCH_SHA）、lifecycle 供方/消费方/T11 分工与外部 ENTRY/manifest 自绑定语义。LICENSE 头部经 PROVENANCE 针（1524B/unchanged）核。
- `tests/unit/t02-ownership-detail.test.ts` 561–843 行：七类同步清除（discard/read/invalidate/dispose/retire/connection/book）、五阶段迟到成功/失败在失效后拒收且快照恒等、发布前 active 五字段复检（project/revision/snapshot/dependencies/null→stale）、同步订阅者丢弃栅栏、七类隔离迟到首页、新 preview 调用即清旧面板（ACK 前）、读失败同 OWNERSHIP_CONFLICT 码不查详情、读取预约先于清面板订阅者合并刷新、两次 queueMicrotask 间隙栅栏（第 2/3 次 active 调用目标差）。
- `tests/unit/t02-manual-preview-lifetime.test.ts` 1–596 行全文：真实 Page 模块经 TS transpile＋VM 注入 hooks 的事件级测试（非 DOM）；detail 挂载/九类清除；真 Session 迟到成功/失败不复活面板；digest 队列——最新未变元组恰一次 prepare（id=SHA-256(canonical)）、十三类"refuses late hash"（ABA/reset/load/structural/read/source ABA/project switch/reading/layout 重挂/pending/retire/layout detach/session 替换）、同元组重复提交取新代旧、过期 hash 拒绝不冒充当前错误、retire 与 dispose 前置 layout detach 阻断、分离附件的错误被忽略而当前错误可见、同步丢弃订阅者不带来新 draft 代。
- `tests/unit/t02-manual-fact-id.test.ts` 1–186 行全文：13 golden 全过实际隔离 Python `Store._fact`（spawnSync -I，无库、无插值）；TS plan 与 golden 逐向量相等且不改输入；同元组重复调用同 id；plain/language/datatype/NFC/NFD 五向量 id 互异；延迟 digest 下先捕获原元组（断言 SHA-256 输入恰为 canonical 串字节）；subject/predicate/object × high/low 孤立代理六例在哈希前拒绝。
- `tests/unit/t02-ownership-detail-view.test.ts` 1–138 行全文：真 React SSR；三 reason 双定位＋基准修订展示、singleDeclaration 两现有记录无传入、>16KiB 历史 ID 不截断不推断 IRI（pre-wrap/anywhere、无 …/href）、敌意串 8 处全转义无 script/img/a/iframe/onerror、冻结模型只读渲染恒等且无按钮/表单/确认面。
- `tests/unit/ui-observation.test.ts` 1–194 行全文：移除按钮＝未完成直至同操作回执、原生 disabled＋fieldsets/legend 豁免、最近显式 aria 真/假大小写折叠不 trim（含 shadow host 链）、重复/歧义/覆盖/shadow 失败关闭、规范化文本与未规范化输入值分离（4301 位整数原样）、回执首段身份＋已读版本＋无 pending 三合一、单槽 1000 次更新 ≤16384B 且保留其它 annotation。

**M 类（全部修改 hunk，本轮补完/补准）**：
- `test_mainline_dispatch.py`：**更正前次级别标注**——该文件为 M（base 725 → 现 1248 行），diff 为单一 hunk `@@ -56,6 +56,529 @@` 纯插入 523 行（＝现文件 59–581 行）。本轮已读全部插入行（含尾部 legacy 三字段 detail 不伪造定位、跨继任会话 detailRef NOT_FOUND＋新 preview 新 ref 两测试）及两侧闭包；现文件 600 行后的 base 未改部分未读（M 规则不要求）。前次"全文 523 行"表述作废。
- `native-driver.test.ts` diff 全 396+ 行逐 hunk：setup/InspectorSocket/realm/connect 新 harness；静默 socket 45s 拒＋迟到 ready 忽略且无 helper；ENOENT 立拒＋计时器零残留；exit 后管道排水受原 deadline 界且 70KB 截断保留尾部诊断、迟到 helper 不发；映射等待不载 shim→真 whenReady→原 helper 恰一次（请求序 1/2/3、focus/exit/hasSwitch 未触）；wrongMapping/missingAPI 立败无重试；whenReady 停滞 45s 无后续 helper；exit/close/error 取消映射轮询且无后续 send；计时器未触发时发送边界复检绝对截止；invalid-json/send-throw/unknown-state/helper-error 清除在途请求不重试。
- `t01-mainline-ipc-delivery.test.ts` diff 全：harness 加 getOwnershipConflictDetailPage；新测试"ownership pages 用同一 sender/frame 精确校验与缺 ACK 持有"（不可信拒、错 frame ACK 拒、正 frame ACK 受理）。
- `t01-mainline-project-service.test.ts` diff 全：MemoryChild 增 holdOwnership/pendingOwnership 与合法单页合成；新测试"ownership pages 不能越过真实 source selection fence"（挂起期间 fence→迟到回执 consume 抛 EngineError、两次调用 projectId 绑定）。
- `t01-mainline-real-runtime.test.ts` diff 全部新增行（distinct-line 级全覆盖，两次筛读合并）：真 preload import＋registerDesktopIpc 接线＋观测子进程 stdout；新测试"实际 preload/named IPC/service/stdio 暴露四个完整 ownership 家族"——五家族（reservedIdentity/sameStatement/singleSlot/singleDeclaration/large×40000 字符）、每族真实 create→commit 链→拒绝仅 detailRef 参数→逐页读取且 selection 不变。
- `t02-mainline-consumer.test.ts` diff 全 267 行逐 hunk：harness 加 getter；OWNERSHIP_CONFLICT 可操作且下一次合法 preview 成功（detailRef/messageKey 不入快照、四种写通道未调）；unknown-code/thrown-error 不泄私值并 INTERNAL_ERROR 后可恢复；manualFactPlan 多值 edit/remove×双记录不碰 sibling（墓碑/他槽 managed/legacyOpaque/mappingState 原样）；三对 RDF 拼写不折叠；三 ownership 字段选中/同槽围栏；原/替换单元组双围栏；定义原/目标重叠围栏；newManualFactPlan 改 Store 内容 ID。
- `t02-mainline-metadata.test.ts` diff 全 190 行：五变体（rdfs/owl class、object/dataProperty、individual）C 子集 create/edit/copy/delete 独立预期三元组与五字段 M 精确性、删除影响矩阵（谓词使用/类型引用两类）、孤立代理 RDF 文本拒绝。
- `mainline-consumer-first-ack-loss.spec.ts` diff 全 136 行：observation slot 接线、reconciliation observeUI 轮询（100ms/5s）＋marker/job/after 逐段记录。
- contracts：`schema.json` **更正为 M**（11363→11888 行；3 hunks 纯插入 525 行）——hunk1/2（wire request/response ok|error oneOf 各 25/64 行）逐行；hunk3（436 行 $defs）document/manifest/header 全约束骨架＋document 定义全文，其余为同形字段界字面量（minLength 1/maxLength 16777216×14 对等）已逐类核。`fixtures.json` 53 hunks 全=17 处 registryHash 替换＋ownership 向量族（named request 有效、null-continuation 无效、wire issuer forbidden 无效、`{}` 文档页 sha256=44136fa3… 与 binding 请求/响应对）。`binding-regressions.json` 34 行=17 对 registryHash 旧→新，无其它内容。`registry.json` 2 处方法清单。`uv.lock` 全 24 行（rdflib registry 源→path 源、sdist 删、wheel 2379774B/99fab7bd、metadata 块）。

**残余未读（均为非本轮 A/M 必要正文，如实披露）**：vendor 三个 wheel 与 upstream wheel 的二进制成员内容（owner 明示不要求）；各 M 文件 base 未改部分；round-04～10 作者原稿正文；O081 check/native 原始 stdout 全量（读独核与关键计数）；O079/O078 内部文件；`t01-mainline-real-runtime.test.ts` 新增行中纯结构括行未逐字连续（distinct-line 全覆盖）。

## F. 对追加一的四点口径更正

1. **160 最终映射更正**：经程序核冻结原表，#33 原判＝**部分适用**（B-4"不适用→部分适用"为对原稿的误述，实为依据更正不改档）；#155 原判＝**适用**→现**无法确认**；#157、#159 原判＝部分适用→现**无法确认**；#158 原判＝**不适用**→现**部分适用**（B-5 已改而 D 漏列）。**最终有效统计＝30 适用／55 部分适用／69 不适用／6 无法确认＝160**（在原 31/56/70/3 上：155 −1适用＋1无法；157 −1部分＋1无法；159 −1部分＋1无法；158 −1不适用＋1部分）。分类变更共 4 项（#155/#157/#159/#158），依据更正 2 项（#33/#128）；B-4 与 D"改判 5 项（含 128）"的表述作废。#156 维持适用、依据限临时真实 SQLite；#146/#147/#160 维持无法确认。
2. **§4 汇总伪 ID 更正**：原"数值更新项"列表中的 `R11-R01` 不是正式稳定 ID（R11 无此位），应删；该主题的正式 ID 为 **Z11-R01**（Z11 新增）与 R11-T01/T03（MM 新增），列表以此为准。175 位置逐 ID 行与 31/8/7/129 机械计数不受影响；标签非闭合证据，逐 ID 真伪以各行为准。
3. **B-5"owner 人类修复"更正**：无证据表明修复由人类执行——T01 供应方 owner 亦为 agent 流程。作废"人类修复为真实参与实例"表述；保留实际链：v1 P2 由独立 agent 审查发现、owner（agent）以 v2 一行门修复并留真实 RED/GREEN；真人能力维持 UNKNOWN（同 #159 口径）。
4. **N4 准确化**：当前生产装配（business3 profile、`ordinary_authority`/`query_dispatch` 双 None）下 `serve()` **会正常执行** `prepare_mainline_store` 并安装 MainlineHost（Coordinator 同条件）；"静默跳过 prep"分支仅在非 None 注入的不同装配/隔离场景可达，属未来接线维护观察。前文"当前生产装配不可达"表述作废。未见当前绕过反例，不构成缺陷或新门禁。

## G. F01 最终口径

按本轮规则（A 新增正文完整亲读／M 全部变更 hunk＋必要闭包）对照 E 节清单：**本限定技术阶段的必要正文亲读已完成**，残余未读均为 wheel 二进制成员、M 文件 base 未改部、旧轮作者原稿与仓外原始日志全量等非必要项。F01（本人阅读流程位置）据此闭合；ROOT 对本票流程的接收仍待定；本口径不把"结构级/筛读"冒充逐字连续全文（real-runtime、schema hunk3 两处已如实标注 distinct-line 级）。

## H. 最终独立结论（第三轮后）

- 补读未发现任何新 P1/P2；E/F 两节更正后，原稿与追加一的全部技术结论（四新叶无 P1/P2、九条架构不变量通过、Top10、175 位置处置、N1–N4）**全部维持**。
- **最终判定：ConditionalPass（限定技术阶段）维持；push 前源码技术阻断 0 维持。** 全部条件＝追加一 D 节条件集＋B 节更正（CI 集合 3798/当次全集、归因双轨、运行身份 deac+四WIP、扩界仅未来另票）＋本节 F 节四点口径更正。原预算、成功/失败门、全部 HOLD/UNKNOWN、2/17、D8 未用不变；无 push/CI/merge 授权；两份完整原稿与处置待 ROOT 实际接收后进入下一票。

（追加二完；本节未运行产品/验证命令、未改受审文件、未读另一作者本轮材料。）

---

# 追加二·补记（过滤/截断读法更正与最后补齐；此前全部内容与前缀逐字节保留）

owner 指正成立：追加二 E 节对 `schema.json` 第 3 hunk 的读法是 grep 滤掉约 96 条 minLength/maxLength/结构行后 head 截断，"distinct-line 级全覆盖"不能当全部修改差异本人已读。本补记按连续、未过滤、未截断读至各 hunk EOF 补齐，并把 E 节相关表述替换如下。

**schema.json 第 3 hunk（436 插入行）连续全读补齐，位置/分支语义本人复核**：`ownershipDetailDocument.oneOf[0]`（manual-ownership-conflict）中 `existing.id` 为普通串（1..16777216，可容 legacy ID），而 `incoming.id` 为 `$ref hash`（64 位十六进制）——**两侧不对称**；`existing.owner/sourceRow` 各为 oneOf(string 1..16777216 | const null)，`incoming.owner/sourceRow` 为 const null——**传入侧不允许带来源**；两 slot 均为 subject/predicate 各 1..16777216、required、additionalProperties false。`oneOf[1]`（single-declaration-conflict）中 `declaration` 为 {layer const ontology, id/predicate 串}，`slot` 同上，`existing` 为 **array minItems/maxItems 恰 2**、元素无 slot（id/owner/sourceRow）。`ownershipDetailManifest`：documentKind const、documentHash $ref hash、**totalBytes 2..16777216、segmentCount 1..512**。`ownershipDetailHeader`：version/kind enum/projectId/detailRef/origin(三 id required)/requestHash/fingerprint/manifest/segmentBlobRefs（hash 数组 **1..512**）全 required。`params_project.ownership.detail` oneOf 两支：**首页支 documentHash const null＋startOrdinal const 0**；**续页支 documentHash $ref hash＋startOrdinal 1..511**；两支 pageSize 均 1..64、additionalProperties false。`result_project.ownership.detail`：detailReadVersion const 1、startOrdinal 0..511、segments 为 $ref changeSetSegment 数组 **1..64**、nextOrdinal oneOf(1..511 | null)、complete boolean，全 required、additionalProperties false。hunk 1/2（wire 层 request/response ok|error oneOf 各 25/64 行）前次已未过滤全读，维持。

**uv.lock 全 24 行变更行连续未截断读齐**（3 hunks）：根 requires-dist 中 rdflib `==7.6.0` registry 项→`path = vendor wheel`＋`==7.6.0+ontolearn.fr201.3`；rdflib package 块 version/source registry→path、**删 sdist 行**、wheels 由 pypi URL（30c0a3eb…）替换为本地 filename（**99fab7bd…，2379774B**）；新增 `[package.metadata]` requires-dist（8 条 extras 依赖带 marker）与 provides-extras 七项——path 源 wheel 需自带元数据的机械结果，无新增运行依赖。

**fixtures.json 全部变更行归类封闭**：新增向量恰 7 个（named ownership request 有效；ownership no null continuation／wire issuer forbidden／wrong ref（响应 detailRef≠请求）／corrupted segment SHA／premature next 五个无效；named ownership page 有效响应，`{}` 文档 sha256=44136fa3…）；**删除 97 行＝内嵌旧 registryHash（058ed1be…）的 startup-failure wireBase64 样本整体重编码**（含尾随空格、\r\n、`\u0007` 前缀等原有填充变体，hash 换为 5e097b7e…），加 17 处 JSON registryHash 行替换；无其它语义新增。**binding-regressions.json**：非 registryHash 变更行＝0（34 行恰为 17 对旧→新 hash），此前结论维持且已穷尽。**registry.json** 2 处方法清单插入维持前读。

**t01-mainline-real-runtime.test.ts diff（287 行）连续未过滤全读**（替换 E 节"distinct-line 级"表述）：真 preload mock＋registerDesktopIpc 接线＋子进程 stdout 观测；五家族（reservedIdentity/sameStatement/singleSlot/singleDeclaration/large×40000）各自 createBlankProject→openProject→真实 preview→逐页 diff→confirm→commit→Job succeeded→marker 等式；singleDeclaration 先双事实＋声明、singleSlot 先声明；拒绝响应**仅 detailRef 一个参数**；逐页读取期间 source selection 恒等；`reassembleOwnershipDetail` 复装后按家族断言（manual 型 existing.id/slot、declaration 型 declaration 与恰两条 existing）；large>1 页；读回 before 不变；后续合法提交（移除一条后同声明可确认/编辑 '"C"'）成功、revision 递增、会话不变、replies diagnostic 全 0；trace 落盘。

**E 节相应表述作废/替换汇总**：schema.json hunk3 由"约束骨架＋document 定义全文"改为**连续未过滤全读至 hunk EOF**；uv.lock 由"结构级抽读"改为**全部 24 变更行**；fixtures.json 由"增量区"改为**全部变更行归类封闭＋7 向量正文全见**；real-runtime 由"distinct-line 全覆盖（两轮筛读）"改为**连续全读**。t01-mainline-project-service/native-driver.test/ipc-delivery/consumer/metadata/ack-loss/dispatch 前次即为逐 hunk/全插入行级，维持。至此 A/M 规则下本人实际亲读范围与本补记及 E 节（经本补记替换后）所列一致；残余未读仍仅 wheel 二进制成员、M 文件 base 未改部、旧轮作者原稿、O081 原始日志全量、O079/O078 内部等非必要项。

**结论不变**：本轮补齐未产生任何新的技术发现；schema 位置语义（existing/incoming 不对称、恰 2 条 declaration existing、512/64/16MiB 界、首页/续页 oneOf 分支）与已读实现/测试一致并互证。最终判定维持 **ConditionalPass（限定技术阶段）／push 前源码技术阻断 0**，全部条件、HOLD/UNKNOWN、2/17、D8 未用、预算与无 push/CI/merge 授权均不变；原分类独立性、175 位置处置与纠正链全部保留。

（补记完；未运行产品/验证命令、未改受审文件、未读另一作者本轮材料。）
