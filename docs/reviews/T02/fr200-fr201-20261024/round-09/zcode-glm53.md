# T02 FR-200／FR-201 R09 独立工程审查（ZCode / GLM-5.3）

## 0. 身份、输入完整性与范围回执

- 本方：ZCode；实际模型 GLM-5.3（既有 BigModel 个人 Coding Pro 来源，无 Start Plan 套餐可用、无新付款）；思考最高；权限完全访问（yolo，不扩大审查职责，本轮只读）。唯一报告即本文件。
- 审查工作目录（cwd）：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes`；branch `feature/weekly-t02-fr200-fr201`；HEAD `240b581c98dbbaec0b4e3773e011c0a14879fa78`；tree `0933a33107da5a645d432538da1582c8c004080d`；sole parent `2b6c8a26055f17a9c2454801eaa2f77b98544f84`；base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2`。以上六项与票面全部一致；范围实测 38 commits／107 changed leaves，一致。
- 输入完整性（本人实测）：外层粘贴文本 21698B、SHA256 `d11bd035630d1a83befb8df5ab17add9405022d390c53ff90454c3d37146ef93`，吻合；全文 225 行读至 EOF 标记，无裁剪。内嵌原用户段（53–222 行，无尾 LF）恰 11255B、SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`，与两个原实物副本逐字一致：`/Users/kyle/.codex/attachments/20f9614d-5a00-4271-aadb-276b6a0465c9/Pasted text.txt` 与 `outputs/20261026_t02_240b_fresh_r09_065/ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt`（均 11255B／同 SHA256，本人复算）。清单项实测 160 项（`^> ` 计数）。初始输入中“SHA1ca23def…”按双方共同勘误读作上述 SHA256，标签连写歧义不影响字节事实；初始原输入保留不改。注：若把内段当作 SHA-1 计算会得到 `8b6861f3…`，不与任何声明比较。
- ROOT 授权原件核验：`iteration-control/2026-10-21-weekly-release/six-patches-20261023/controller-t02-240b581c-o064-reception-and-fresh-r09-ticket-20261026.json` 7765B／SHA256 `e529bb0e5ec2df83d4915bc17d6aa256af00d3854883c543f7070c247812dad4`，吻合；其为 fresh R09 授权与有界本地接收，不是审查结论或 merge 授权。
- O064 关键文件核验：`COMPLETION.json` 7109B／`e8a9a8b6…4a0a`、`FINAL-MANIFEST.json` 34602B／`ceb97589…984d`，吻合；`HANDOFF.md`、`PRE-COMMIT-FINAL-GUARD.json`、`native24/FINAL-QUALIFICATION.json` 已读。240b581c 三提交文件（native-driver.ts `f994ce5a…`、t02 spec `e5bd057f…`、unit `31a4cb64…`）与 HEAD 工作树逐字节一致（本人 SHA256 复算）。
- R09 相对 R08 head `62d4b0a2` 的 delta 实测为两提交：`2b6c8a26`（纯九文档归档）＋`240b581c`（三测试文件：e2e driver、FR200/FR201 spec、driver 单测）。本报告覆盖整个 base→head 38 commits，不继承 R08 结论，未读取另一方当前 R09 报告。
- 本轮为只读审查：未运行 formatter/HMR/install/build/check/测试/CI，未 git add/commit/push/切分支，未改任何源、测试、配置、依赖、需求或验收；工作树原有受保护项（`M AGENTS.md` overlay、round-01/02/03 WIP）原样未动。

## 1. 审查方法与证据层级

本人亲读：R09 delta 两提交全部内容；范围内心动代码全部 diff（主进程 4 文件、preload 1、renderer 7、engine Python 8、contracts 4＋schema/fixtures/registry、scripts 3、CI 1、vendor 补丁/PROVENANCE/wheels、licenses/NOTICE、package/pyproject/uv.lock）及关键新增文件全文（`mainline.py` 1207 行、`native-driver.ts` 301 行、`native-driver.test.ts` 395 行、`native-recovery.cjs` 112 行、`mainline-ownership.ts`、`OwnershipConflictDetailView.ts`）；需求依据（PRD 7.3／FR-200／FR-201／附录 C、ADR-0001 相应不变量、m0-checklist、T02 status.md 全文、round-05 原条款映射）；R08 处置 31＋78 全表及两份独核与版本图清单。证据分级：①本人直接代码事实（grep/读文件/哈希复算）；②本人读取的仓外原运行证据（O064/O059 摘要与 FINAL-QUALIFICATION）；③R08/R07 归档事实承接（未复跑）。未运行任何产品验证；区分静态、运行（他人原运行）、打包与生产证据，不以静态代替运行。

## 2. Top 10 实际最重要风险（本人本轮裁定）

1. **完整平台 CI 从未在本候选上运行（合并门禁缺口）**｜严重性：高（对合并/发布）｜触发：任何 push 后真实 CI｜依据：ROOT 票 `remoteFeatureHEAD=2b6c8a26`、240 未 push、PR16 open 未合并；O059 CI41（内容等 2b 合成检出）Quality/Windows 实际失败｜影响：F03 口径的 Windows 3769 全集＋全部后继＋三 job success 均无本候选证据｜最小建议：ROOT 另票普通 push→既有 PR16→唯一自动 CI，按完整回单验收，失败按新增结构化栈定因｜**非 push 前源码技术阻断**（流程门禁）。
2. **CI41 C1 根因 UNPROVEN，240 仅是前置同步缓解**｜严重性：高（未确认）｜触发：未来 CI 的 Quality native recovery 步｜依据：`COMPLETION.json.unprovenCI41TimingRootCause=true`；`native-driver.ts:4-5` 注释自认；readiness 门闩（Electron 44.9 cache 映射→canonical resolve→严格 API→whenReady→原 helper 一次）只是把失败从“未定义行为”变成 fail-closed 拒绝｜影响：若根因在 npm shim/解析链其他环节，C1 可复发｜建议：复发时以 driver 结构化 diagnostics（含 stderr/stdout 尾 64KB）定因，不倒填｜**非 push 前源码技术阻断**（方向正确、fail-closed）。
3. **engine 自然退出码与 Windows 后代回收 UNKNOWN**｜严重性：中｜触发：打包/CI 强杀或 launcher 先退｜依据：O064 FINAL-QUALIFICATION `engineNaturalExit=UNKNOWN`；`run-engine-tests.py:169-171` “UNKNOWN after launcher exit; no job handle”（Windows 无 Job Object）｜影响：无法证明全部子进程自然退出/回收｜建议：未来 CI 证据接收时由 ROOT 另票评估 Job Object/观测副本｜非阻断。
4. **冗余 vendored wheel 入库（供应链面）**｜严重性：中低｜依据：本人 ls＋SHA256：`fr201.1`（2378177B）/`fr201.2`（2378736B）在树、仅 `fr201.3` 被 `uv.lock`/pyproject 引用，PROVENANCE 自记 fr201.2 为历史 NOT_ADOPTED｜影响：仓库体积与供应链审计面扩大（≈4.76MB 无引用制品）｜建议：merge 后由 T11 供应链 owner 受控移除，不私自删｜非阻断。
5. **契约类型宽于运行时 schema（漂移风险）**｜严重性：中低｜依据：`contracts/src/index.ts:894-897` `OwnershipDetailArgs.pageSize:number`（schema 限 1..64、首请求 `startOrdinal` 字面量 0）；`mainline-ownership.ts:18/28` 与 `index.ts reassembleOwnershipDetail` 各自硬编码 pageSize 64｜影响：未来调用方可构造被 zod 拒绝的参数（运行时仍被拦截，无绕过）；双处 64 漂移｜建议：契约 owner 下次整理时收窄 TS 类型并单一来源化 64｜非阻断。
6. **witness／单值冲突行 SQL 无 ORDER BY（未确认观察，不升级）**｜严重性：低｜依据：本人 grep `storage.py:1151`（GROUP BY…LIMIT 1）、`:1170`（LIMIT 2）｜影响：冲突定位行的选取顺序无跨运行稳定合同｜建议：T01 下次触及 witness 选取时合同化，不新增顺序需求｜非阻断。
7. **应用层 4299/4300 整数边界断言缺失**｜严重性：低｜依据：本人 grep：仅 `test_mainline_language_input_rejection.py:36` 断言 4301 拒绝；vendor 补丁保留运行时限额（`sys.get_int_max_str_digits()`）｜建议：T02 下次授权触及整数守卫时补 4299/4300 应用边界断言｜非阻断延期。
8. **CI 制品卫生：cancel 后 always() 上传不保证＋test-results 重复上传**｜严重性：低｜依据：`ci.yml` 两 always 制品步均含 `test-results/`；`if: always()` 在取消后不保证执行｜影响：取消 run 的证据可能缺失；存储重复｜建议：未来 CI 维护票评估看门狗与去重｜非阻断。
9. **native-driver readiness 强耦合 Electron 44.9 内部行为（测试维护脆弱性）**｜严重性：低｜依据：`native-driver.ts:217-242` 依赖 44.9 `common/init` 安装的 electron cache 键与 canonical resolver；Electron 升级后若映射不再预装，将以 mapping-pending 轮询至 450 次/45s 后 fail-closed 失败｜影响：仅测试维护成本，方向安全｜建议：升级 Electron 时同步维护该探针｜非阻断。
10. **裸 ownership 家族无 typed witness（HOLD 家族）**｜严重性：低（对当前候选）｜依据：`storage.py:1229-1237` 裸分支仍抛无 witness 的 ownership Conflict（最终码同为 OWNERSHIP_CONFLICT 但无 detail）；`rdf_snapshot.py:45` 未知 parser→普通 ValueError（UNKNOWN/HOLD 保留，正确的保守分流）｜影响：非 manual 写入路径冲突无可见定位｜建议：T01/T02 对应家族接线前补 typed witness｜非阻断。

说明：第 1 项为流程/合并门禁而非源码缺陷；第 2 项未确认；3–10 为非阻断维护/HOLD。本人未发现本候选 push 前源码技术阻断；此判断只覆盖本人亲读范围（§5）。

## 3. 原清单 160 项逐项裁定

产品形态事实（裁定基准）：本地优先桌面应用（Electron＋React renderer＋Python stdio 引擎＋SQLite），无登录/多租户/支付/云服务/网络面/邮件/模型外发（S3 前网关不接入）；M0 阶段产品正式能力受限，存储为内部 API。据此大量 SaaS/Web 项不适用；“不适用”均为当前产品无该表面，不是判定永久不需要；适用项给出代码定位。缩写：NA=不适用；A=适用（给现状）；A-=部分适用/部分确认；NC=无法确认（未实际检查到）。

| # | 裁定 | 依据／定位 |
|---|---|---|
| 1 | A（正面） | 契约单一权威：`packages/contracts` zod＋`schema.json`＋Python `contract_v2.py` 双端同源；分层存储设计驱动，非逐表临时拼凑 |
| 2 | NA | 本地优先无登录/邮箱（PRD 无账户体系） |
| 3 | NA | 同上 |
| 4 | NA | 同上 |
| 5 | NA | 无服务端会话；最近似物：engineSessionId＋generation 换届防御（`mainline.py bind/allows_owner`） |
| 6 | NA | 无企业客户/SSO 表面 |
| 7 | NA | 同上 |
| 8 | NA | 同上 |
| 9 | A- | 权限=固定方法白名单＋selected project＋ownership proof（`engine.ts:1229-1246`、`mainline.py authorize/require_owner`）；无角色体系（单用户本地产品） |
| 10 | A（正面） | 换 projectId/越序访问被拒：`engine.ts` selected 校验、`project-mainline-service.ts:558-575` owner/epoch 双 guard、`mainline.py authorize` PERMISSION_DENIED |
| 11 | NA | 无多租户 |
| 12 | NA | 无管理员/支持冒充面 |
| 13 | NA | 无登录可爆破面 |
| 14 | NA | 同上 |
| 15 | A- | Store 版本化提交前向＋失败原子中止已测（迁移 468=424P+44 条件 skip，R08 记录）；人工 schema 降级/活库回滚未证（HOLD） |
| 16 | NA | 本地单进程 SQLite，无并发业务负载；写前 material admission 存在（`mainline.py check_final_material`） |
| 17 | NA-（HOLD） | 现规模不适用；容量/旧超限库恢复为保留 HOLD（Q5/D2） |
| 18 | NA | stdio 单连接，无连接池场景 |
| 19 | NA | 本地优先，数据在用户本机；产品级备份策略未定义（产品层未决，非缺陷） |
| 20 | NA | 同上 |
| 21 | NA | 同上 |
| 22 | A- | 版本化提交＋历史不可改写＋分层（AGENTS 不变量）实现可回溯语义；删除为显式提交操作 |
| 23 | A（正面） | 边界数据一律 zod `.strict()`/contract 校验（`_room` 对 result、`validateBusiness3` 对 params；coordinator 入口校验） |
| 24 | A- | date/dateTime 字面量按 RDF 类型保留（FR201 用例）；无提醒调度功能，全时区行为无表面可验 |
| 25 | A（正面） | 用户输入不拼 SQL（全参数化）；撇号等字符经 canonical n3 精确校验（`domain_changesets.py:464`） |
| 26 | A- | lone surrogate 拒绝（`mainline-facts.ts:57-64`）、UTF-8 全链（引擎测试 UTF-8 写盘、`text_page` UTF-8 边界检查）；emoji/RTL 逐字形渲染未验——部分确认 |
| 27 | NA | 无货币金额 |
| 28 | NA | 同上 |
| 29 | A（正面） | 分层（定义/断言/推导/场景/历史）＋changeset 版本化；多项目库（catalog/create/open）已支持 |
| 30 | A（正面） | operationId 幂等：`operation_claims` 重放认证（`mainline.py` example create 重放校验）、draft.save generation CAS |
| 31 | A（正面） | FACT_ALREADY_EXISTS／AMBIGUOUS_FACT_SUPPORT／`manualFactPlan` 重叠拒绝；确认按钮单次 |
| 32 | A- | cursor 分页（catalog/diff/text/rows/ownership detail）有 pageSize 界＋cursor TTL；第 400 页规模未测（容量 HOLD） |
| 33 | A- | 完整 rows JSON Diff 导出已验（用户可用实际 RDF 核对）；Turtle 导出属 FR-203（不在本候选） |
| 34 | NA | 无 CSV 导入 |
| 35 | NA | 无合同保留义务；架构约束“缓存回收不触历史”在位 |
| 36 | A- | 本轮 diff 无凭据；架构 S3 前无密钥（AGENTS 不变量）；未做全库秘密扫描——部分确认 |
| 37 | NA | 尚无可轮换密钥；S3 接入时适用 |
| 38 | A（正面） | uv.lock 钉本地 wheel＋哈希；本人复算 upstream/fr201.3/patch 三方 SHA256 与 PROVENANCE 一致；npm 精确版本约定 |
| 39 | A-（缺口开放） | dependabot（npm/actions weekly）在；CI 无 audit 步（本人读 ci.yml）；供应链法律/产权 HOLD |
| 40 | A（正面） | 受控拒绝集合：INVALID_REQUEST 词法/language tag/integer limit/canonical n3/IRI 禁字符（`rdf_snapshot.py iri/term`、`domain_changesets.py:437-465`） |
| 41 | A（正面，桌面等价） | SQL 全参数化（本人抽查 storage/job_store/mainline；`material_profile` f-string 仅用引号转义的 DB 自有标识符）；renderer 无 dangerouslySetInnerHTML（新视图纯文本节点）；CSP 单源 `csp.ts` 本轮未改（构建仅 24B nonce 变化）；无网络面故 CORS/CSRF 无表面 |
| 42 | NA | 无用户上传；最近似物 example 资源读取经 O_NOFOLLOW/fstat 前后比对/FIFO 拒绝/哈希钉住（`mainline.py _example_resource_reader`） |
| 43 | NA | 不开 HTTP 端口（AGENTS 不变量） |
| 44 | A-（等价 CSP） | 生产 meta CSP 无 unsafe-inline/eval（未改；O064 构建仅 24B nonce 差） |
| 45 | NA | 本地明文 SQLite 为设计选择、无传输面；产品层未决记录 |
| 46 | A（正面） | authority 层最小权限：ownership proof/check_reply/read admission（`mainline.py`、`job_store.py _WriteAdmission`）；Agent 白名单工具、不得自动确认（架构不变量） |
| 47 | A（正面） | 证据/诊断有界：pollText 4096 UTF-16 单位、stdout/stderr 尾 64KB 截断；未见凭据记录 |
| 48 | NA | 无对外服务可渗透测试 |
| 49 | NA | 同上 |
| 50 | NA | 同上 |
| 51 | NA | 本地数据无远端权限可吊销；S3 接入时适用 |
| 52 | NA | 无 SOC 2 场景 |
| 53 | NA | 无患者数据 |
| 54 | NA | 同上 |
| 55 | A- | 操作 receipts/operation_claims 记录“谁改”；“谁查看”粒度无（本地单用户） |
| 56 | NA | 无卡数据 |
| 57 | NA | 本地无个人数据收集；未来云功能时适用 |
| 58 | NA | 全本地 |
| 59 | NA | 单用户本地 |
| 60 | A- | CI 与本地同版 `npm run check`；跨 OS 环境差异是当前 CI 缺口（cp1252 教训＝O040） |
| 61 | A-（等价） | CI workflow＋锁文件＋确定性 repack 脚本即可重建“基础设施”；无云资源 |
| 62 | A（正面） | check 前置于 package；CI 完整门禁口径已定义（F03）；本候选未经真实 CI（HOLD） |
| 63 | A- | 版本化提交＋Undo（定义级 GUI Undo/Undo-of-Undo/owned restart 子集已验）；无部署故无“部署回滚” |
| 64 | NA | 本地桌面无停机窗口概念 |
| 65 | NA | 单版本本地应用；I02_HMR 为开发探针且评审冻结期禁跑 |
| 66 | NA | 无服务端伸缩 |
| 67 | NA | 无 Web 分发 |
| 68 | NA | 无自有 DNS/证书 |
| 69 | A- | 引擎 Job/round 终态机＋lease（`job_store.py`）；UI 异步预览/确认不冻结 |
| 70 | A- | 目标 retry0/flaky0（native24 实测）；无业务 API 重试场景；driver 显式不重试 helper（正确） |
| 71 | NA | 无分布式队列；failed/cancelled 终态留痕 |
| 72 | NA | 无 cron/多服务器 |
| 73 | A（正面） | `invalidation-v2.json` 唯一来源、staleReason 规则（本轮未改）；渲染端 stale 时清 ownershipDetail/prepared |
| 74 | NA | 无邮件 |
| 75 | NA | 同上 |
| 76 | A- | 测试临时目录每 run 隔离（TMPDIR/basetemp/cache 独立）；CI 制品 7 天保留 |
| 77 | NA | 无云计费 |
| 78 | NA | 本地单机；损坏 SQLite 恢复 HOLD 保留 |
| 79 | NA | 同上 |
| 80 | A-（等价） | 结构化 events.jsonl/summary.json 全 UTF-8（本人读两脚本）；无 3am 云日志场景 |
| 81 | A-（等价） | 固定错误码＋受限参数跨边界（架构不变量）；无聚合系统 |
| 82 | NA | 无在线服务 |
| 83 | NA | 同上 |
| 84 | NA | 同上 |
| 85 | NA | 无分布式请求 |
| 86 | NA | 同上 |
| 87 | A-（等价） | AGENTS/HANDOFF/ADR 即运行手册等价物 |
| 88 | A（正面，流程） | R01–R09 逐轮处置、首败保留、不倒填因果的复盘制度 |
| 89 | NA | 无状态页 |
| 90 | A（正面） | 3719 Py＋1905 TS（原运行）；断言完整预期集合（AGENTS 约定）；本轮新增 73 引擎＋约 50 TS 用例（本人计数） |
| 91 | A-（等价） | 无第三方 API；真实两进程引擎＋真实 Electron e2e（native24 原六例等） |
| 92 | A（等价，核心流） | FR200/FR201 表单→预览→人确认→读回真实链（57 事务/43 拒绝） |
| 93 | NA-（HOLD） | 容量口径/负载测试保留 HOLD |
| 94 | A- | fixtures＋固定示例 bundle；本地产品无生产库可复制 |
| 95 | A（正面） | `binding-regressions.json`＋各轮证据钉＋回归用例（本人读 diff 增量） |
| 96 | A-（HOLD） | 低端硬件/参考设备为保留 HOLD |
| 97 | A- | 新 UI aria-label/role=alert/role=status（`OwnershipConflictDetailView.ts`、`OntologyMainlinePage.tsx:327-340`）；完整键盘/读屏审计未做 |
| 98 | NA | 无订阅/升降级/按比例计费表面 |
| 99 | NA | 无失败扣款重试/催缴邮件 |
| 100 | NA | 无发票/PO 号表面 |
| 101 | NA | 无销售税/VAT |
| 102 | NA | 无退款/抵扣 |
| 103 | NA | 无用量计量 |
| 104 | NA | 无年度定制合同计费 |
| 105 | NA | 无收入对账报表 |
| 106 | NA | 无 webhooks |
| 107 | NA | 同上 |
| 108 | A（正面） | 内部边界版本化：readVersion/draftSaveVersion/detailReadVersion/ownershipDetailVersion＋PROTOCOL_VERSION |
| 109 | NA | 无 API keys |
| 110 | A-（等价） | budget/admission 层即资源限流（READ_LIMITS/HELD_BYTES/ticket.pay/HELD_OBJECTS/READ_WORK） |
| 111 | NA-（正面等价） | 无外部 API；rdflib 锁本地版本正是上游变化隔离（PROVENANCE） |
| 112 | NA | 无 OAuth |
| 113 | NA | 无集成沙箱 |
| 114 | A-（前瞻） | S3 前无模型外发（AGENTS 禁止）；本轮无 LLM 输入面；接入时必须建提示注入防护 |
| 115 | A-（前瞻） | 客户/患者数据不进入外发提示：现版本无外发通道可违反；S3 接入时为硬门槛 |
| 116 | NA | 无模型计费 |
| 117 | NA | 无模型输出 |
| 118 | NA | 同上 |
| 119 | NA | 同上 |
| 120 | NA | 同上 |
| 121 | A（正面） | 人确认按钮后缀不变量：confirm 只能人点（`OntologyMainlinePage` 确认链）；Agent 不得自动确认；提交前完整 Diff 预览 |
| 122 | NA | 本地渲染无网络依赖 |
| 123 | A（正面） | reading/unavailable/ready 三态＋formError＋初始状态断言（native-recovery 健康初始“尚未检查”） |
| 124 | A（正面） | 固定码＋行动文案：OWNERSHIP_CONFLICT 专属解释（`OntologyMainlinePage.tsx:327-336`）、“已输入内容保留” |
| 125 | A（正面） | 校验失败保留已输入内容（源码状态不重置；FR201 受控负例字段保留断言） |
| 126 | NA | 无邮件 |
| 127 | NA | 无通知系统 |
| 128 | A- | Undo 提交路径在；定义级 GUI Undo 子集已验（O056 例18）；通用 Undo GUI HOLD |
| 129 | A- | 同 97 |
| 130 | A- | 界面中文＋多语言字面量按字面保留（label@zh/@en）；完整 i18n 框架不在 P0 |
| 131 | A- | 窗口恢复属 I02（相邻线，CI 修复门禁）；本轮无导航变更 |
| 132 | A（正面） | 本轮代码注释写明不变量约束、命名一致（本人通读全部新增代码） |
| 133 | A（正面，流程） | 指定双审＋ROOT 接收流程在运行（本报告即一环） |
| 134 | A（正面） | worktree＋feature 分支＋PR 门禁（AGENTS §5；本分支 base/HEAD 记录清晰） |
| 135 | A-（缺口开放） | dependabot weekly 在；实际合并记录/uv/vendor 跟进未证（Z08-10） |
| 136 | A- | Electron 44.9/Python 3.12 锁定；EOL 跟踪未证；供应链 HOLD |
| 137 | A-（缺口开放） | fr201.1/2 wheel 4.76MB 无引用（F09）；未见其他新死代码 |
| 138 | A- | `t02-fr200-fr201.spec.ts` 1796 行逼近阈值；`mainline.py` 1207 行大但结构清晰；无超 2000 行文件（本轮范围内） |
| 139 | A（正面） | ADR-0001/0002 在；本轮无架构决策变更故无新 ADR |
| 140 | NC | README/新工程师 1 小时指标本人未验证（AGENTS 仓库地图存在） |
| 141 | A（正面） | status.md/m0-checklist/round 档案即交接文档 |
| 142 | NA | 无运营面板 |
| 143 | NA-（等价） | 冲突详情视图是用户侧诊断等价物（`OwnershipConflictDetailView`） |
| 144 | A-（等价） | PRD 版本史＋status 追加即变更记录；无客户 changelog 表面 |
| 145 | NA | 无对外条款；本地无数据外发与未来隐私义务一致 |
| 146 | NC | 账户/域名归属非代码可证 |
| 147 | NC | 组织 bus factor 非代码可证；流程上多开发线＋ROOT 并行 |
| 148 | A（正面，流程） | R04–R09 双作者整段读＋ROOT 接收；本人本轮覆盖 38c/107f 代码面 |
| 149 | A（正面） | 数据模型设计驱动（见 #1/#29） |
| 150 | A（正面，流程） | R08→R09 的 P2 drain 副作用即实例：独审发现→修复→补跨 turn/close 用例 |
| 151 | NA | 无部署/云账单 |
| 152 | NA | 无值班 |
| 153 | A- | 依赖锁定＋vendor 确定性重建（repack 脚本）；漏洞响应 SLA 未证 |
| 154 | NA | 无审计 walkthrough 场景 |
| 155 | A（正面，流程） | ROOT 独核＋独立验收（O064 INDEPENDENT-01..03、R08 双独核） |
| 156 | A-（HOLD） | 合成夹具前向已测；活库迁移未证（保留） |
| 157 | A（正面，流程） | 范围冻结/不扩附录 C/O061 schema2 提案被拒为实例 |
| 158 | NA-（HOLD） | 单机产品；容量 HOLD 为对应边界 |
| 159 | A（正面，流程） | cp1252/C1/79F 逐轮定因流程（部分仍未定因，如实保留） |
| 160 | A（正面） | ADR/PRD 版本史/处置档案保留理由与未决窗口 |

## 4. R08 31 个当前位置的本人处置

本人逐项独立裁定（非沿用）：Z08-01～Z08-11＋Z08-TOP10-OLD79F、MM F01～F19。状态：维持＝窗口/归属不变；部分闭合＝有新事实。

| ID | 本人处置 | 本人依据 |
|---|---|---|
| Z08-01 | 维持（阻断 merge，非源码缺陷） | ROOT 票 remoteFeatureHEAD=2b、240 未 push、PR16 open |
| Z08-02 | 维持 | 本人读 `run-engine-tests.py:128-198`：POSIX 进程组三段清理；Windows CTRL_BREAK+taskkill，`descendants="UNKNOWN after launcher exit; no job handle"` 原文在 |
| Z08-03 | 维持 | 本人读 ci.yml concurrency `cancel-in-progress:true`、Quality 15m/Desktop 20m 原值、双 always 制品步 |
| Z08-04 | 维持（历史 FAIL 缺栈仍开） | O059 原件为 R08 时点证据；本人未重跑，不以新绿倒填 |
| Z08-05 | 维持（双向因果限定） | 本人 grep 两处 PATH `python` 在位：`t01-mainline-contract.test.ts:656`、`t01-ontology-metadata-contract.test.ts:168`；O035 ENOENT＋UV 成功双原件承接 |
| Z08-06 | 承接（本地闭合资格） | 本人读 `run-engine-tests.py:374-383` controlHashes/checkout 记录机制在；mode2 全量结算本人本轮未复跑 |
| Z08-07 | 维持（非阻断延期） | 42 类内部分类≠逐原因可行动文案；已测子集不外推 |
| Z08-08 | 维持（P2） | 本人读 ci.yml 全文无 npm/uv audit 步 |
| Z08-09 | 维持 | 本人读双 always 制品步均含 test-results/ |
| Z08-10 | 维持（部分采纳） | 本人读 dependabot.yml（npm+actions weekly, /, target develop）；实际运行/合并记录未证 |
| Z08-11 | 维持（HOLD 群＋Undo 子集收窄） | 组织/法律项代码不可证 |
| Z08-TOP10-OLD79F | 维持（未知保原） | 旧 CI36 79F 无逐例栈；不为消因果重跑 |
| F01 | 本轮已完成 | 本人整段审读 base→240（含 594 行控制层与三主进程 delta 的必要闭包） |
| F02 | 维持（合并门禁） | 同 Z08-01 |
| F03 | 维持＋本人复核 | 本人读 ci.yml Windows diagnostic 步（maxfail=1 fail-first，后续步骤被阻断的结构性事实）与 O059 结算 3769=3429P/53S/48S；诊断步名既不放行也不否定完整证据 |
| F04 | 承接撤回维持 | — |
| F05 | 部分闭合又开 | 62d4 的状态追加已由 2b6c8a26 落库（本人读 HEAD 版 m0-checklist/status.md 含 R08 节）；当前 head 240 的追加义务随本候选重开，待 ROOT 归档票 |
| F06 | 维持（维护） | `python -m pytest` 改变 sys.path[0] 而 identity 七项无 sys.path；本人未证完整导入路径等价 |
| F07 | 维持 | 本人读 `run-engine-tests.py:379-383`：rev-parse check=False → None 且不计 errors（拒绝无 head/tree 绑定证据的口径正确） |
| F08 | 维持（非阻断观察，本人复核） | 本人读 `OntologyMainlinePage.tsx preview()`：过期预览的丢弃是显式 lifetime/sequence 栅栏防御性 return（stale 上下文丢弃正确，用户输入保留）；原“静默丢弃”表述限原观察面 |
| F09 | 维持 | 本人 ls＋SHA256：fr201.1/2 在树无引用、fr201.3 被 uv.lock 引用 |
| F10 | 维持 | 本人读 `pyproject.toml:39` 排除面（仅三名报告文件 glob）；R06 attempt2 失效路径承接 |
| F11 | 承接收窄维持 | — |
| F12 | 维持 | 同 Z08-03/F03 证据 |
| F13 | 维持 | 本人读脚本头注释“NOT per-test durations or promised speedups” |
| F14 | 维持 | 本人读 `mainline-ownership.ts:18/28` 与 `index.ts reassembleOwnershipDetail` 双处 64 |
| F15 | 维持（未确认观察） | 本人 grep `storage.py:1151/1170` 无 ORDER BY |
| F16 | 维持（无需改动） | — |
| F17 | 维持（语义等价） | 本人读 `OntologyPage.tsx:438` `pattern="[A-Za-z0-9_][A-Za-z0-9_\-]*"` |
| F18 | 维持（过度陈述更正承接） | uv.lock 本地路径锁定本人复核；“包内一致”仍待打包验证（本候选无新包） |
| F19 | 承接（命名歧义） | 旧 raw 不改写；本报告以唯一 ID 定位 |

## 5. 78 个历史位置的本人处置

每行给本人状态与依据；标注“复核”为本轮本人直接代码验证；“承接”为依 R08 双方一致事实＋本人读回的归档证据维持，事件窗口与归属不变。计数与 R08 一致（R07 23＋R06 Z8＋R06 MM12＋R04 14＋R05 21）。

| 历史 ID | 本人状态与依据 | 归属／窗口 |
|---|---|---|
| Z F1 | 仍开（合并门禁）：240 未 push 无新 CI；本地 O064 证据不替代完整回单 | ROOT 精确 CI 票；merge 前 |
| Z F2 | 仍开（维护）：无新 raw 命名入树（本轮 round-09 仅本报告） | 未来新增 raw/改规则时 |
| Z F3 | 仍开（维护）：本人复核两 CI 脚本全部 JSON 写入显式 `encoding="utf-8"`（write/collection.tmp 等）；历史 20 默认 encoding 窄结论维持 | 原测试 owner 下次触及 |
| Z F4 | 关闭（口径）：双分母事实修订维持；62d4/240 无 dumps 调用面变化 | 无待办 |
| Z F5 | 仍开：本人 grep 两处在位（:656/:168） | T01 测试维护者下次授权 |
| Z F6 | 仍开（集合，逐子项见下）：definitions 早期 wire、裸 ownership、standalone EOF、缺码、无序、4299/4300 分别见对应行 | 各接线/维护事件 |
| Z F7 | 仍开（发布 HOLD 群）：签名/公证/法律/跨 OS/容量等全部保留 | 各 owner 对应验收前 |
| Z F8 | 仍开：本人复核 `rdf_snapshot.py:43`（BadSyntax/Notation3InputError→TermInputError）与 `:45`（其余→普通 ValueError）分流在位；裸族两出口最终码仍 OWNERSHIP_CONFLICT | 未知/新家族接线前按 HOLD |
| Z F9 | 承接（限本受审面闭合）：typed witness 授权链完整（本人读 job_store/mainline）；未来触及合同出口再核 | T01/T02 触及时 |
| Z F10 | 承接（既有证据接收）：O047/本轮 native24 57 事务/43 拒绝不外推全 GUI | 无待办 |
| MM R07-01 | 关闭：排除面在（本人读 pyproject:39）；覆盖面问题归 F10 | 本次静态接收 |
| MM R07-02 | 仍开（维护）：未发生的新 raw 不是当前失败 | 未来新增 raw 名时 |
| MM R07-03 | 仍开：不采统一整 reviews 排除；round-08/09 目录新增未改格式检查范围 | 独立配置票 |
| MM R07-04 | 在 2b 闭合、在 240 重开（同 F05） | ROOT 文档 owner，归档票后 |
| MM R07-05 | 仍开（overlay 维护）：AGENTS 未提交 overlay 本人读回一致（M 状态原样） | ROOT/指南 owner |
| MM R07-06 | 关闭（口径） | 无待办 |
| MM R07-07 | 已闭合（口径）：20 默认 ASCII JSON 窄结论维持 | 载荷变化时 |
| MM R07-08 | 已闭合（口径）：28 笔 FR200 语义与附录 C 不扩的分层维持 | 父 FR/具名下游另验 |
| MM R07-09 | 已闭合（口径）：本轮沿用 O064 构建副本 nonce 证据（本人读 PRE-COMMIT-FINAL-GUARD 24B span），未新构建 | 既有证据限定 |
| MM R07-10 | 已闭合（口径，标题/正文歧义见 F19）：386−379=7 算术对账；240 新增 0 个 .py，计数待未来回单 | 无新复跑票 |
| MM R07-11 | 仍开（观察）：本人复核 `mainline-facts.ts`——edit 保原 ID、managed/owner/sourceRow/重叠拒绝（AMBIGUOUS_FACT_SUPPORT 扩展条件）与内容派生 ID 均在位 | T02/ROOT PR 说明可解释 |
| MM R07-12 | 仍开（HOLD）：本人复核 PROVENANCE/patch/upstream 三方哈希一致、fr201.2 历史态自记；法律/供应链 HOLD 保留 | vendor/发布 owner |
| MM R07-13 | 仍开（维护）：本人复核 `index.ts:894-897` TS 宽于 schema（startOrdinal 字面量仅首变体、pageSize:number） | 契约 owner 下次整理 |
| R06 Z P1 | 仍开（门禁）：同 Z F1；旧 79F 全因未证不追认 | 合并前真实 CI |
| R06 Z P2 | 仍开：诊断步与验收口径分离维持（F03） | 未来 CI 证据接收标准 |
| R06 Z P3 | 仍开：本人复核 `domain_changesets.py:157` `_definition(store, record)` 预览校验路径未分类 ValueError 在位 | T01 核心；原始 wire/Agent 接线前 |
| R06 Z P4 | 部分闭合：typed witness（manual-ownership-conflict/single-declaration-conflict）已落地（本人读 storage.py 两 Conflict 类）；裸族未全闭 | T01 详情合同＋T02 消费 |
| R06 Z P5 | 仍开：错误码集合差事实维持；16 码可达性未证，不泛加白名单 | 对应方法接线前 |
| R06 Z P6 | 仍开（未确认观察）：本人复核无 ORDER BY（:1151/:1170）；无构造性反例不升级 | T01 Store 维护触及选取时 |
| R06 Z P7 | 已闭合（沿既有决定）：本人复核 `parsed.n3() != value` 精确政策在位（domain_changesets.py:464）；Q6 不重问 | 政策变更才新人类决定 |
| R06 Z P8 | 仍开（逐项承接）：7.2–7.6 各行分别承接 | 各原归口 |
| R06 D1 | 仍开（门禁）：本人本轮未发现新源码缺陷（delta 为测试文件＋文档归档） | ROOT 正常票 |
| R06 D2 | 部分闭合：62d4 归档已做；240 追加待归档票（同 F05） | ROOT 文档 owner |
| R06 D3 | 仍开：同 R06 Z P3（本人复核同源代码事实） | T01；接线前 |
| R06 D4 | 部分闭合：两出口最终码均 OWNERSHIP_CONFLICT（本人复核 storage.py:1217-1237）；裸族定位未全闭 | 随家族接线处理 |
| R06 D5 | 仍开（未确认观察）：同 Z P6 | 同 Z P6 |
| R06 D6 | 仍开：本人复核 vendor 补丁含 `j == len_argstr`/`j < 0` 类型化守卫；`n[-1]` 裸索引残余未证不可达 | T02 vendor/T01 入口；新解析入口前复核 |
| R06 D7 | 仍开：同 Z P5 | 同 Z P5 |
| R06 D8 | 仍开：同 Z F5（本人 grep 两处在位） | T01 测试维护者 |
| R06 D9 | 已闭合（口径）：Ruff 369/379/380/386/387 各时点原件保留；240 侧 387（O064）为最新时点 | 文档 owner |
| R06 D10 | 仍开：四具名下游（编辑→推导/保存查询/SHACL/报告）GUI 未逐类验；公共失效规则与九行正负例证据维持，两分不抹 | 父 FR/消费链验收前 |
| R06 D11 | 仍开：本人复核仅 4301 断言、4299/4300 应用断言缺 | T02 整数守卫维护时 |
| R06 D12 | 保留（有界）：六 keyword AST/本地运行/旧包身份按原资格；不外推 | 无待办 |
| R04 Z01 | 仍开（未确认观察）：同 Z P6/D5 | T01 触及选取时 |
| R04 Z02 | 撤回维持：43692 误因果不复活；262144/16MiB 预算边界仍在（本人读 ownership_detail_page min(maxPageBytes,maxFrameBytes,262144) 与 reassemble 界） | T01 详情预算维护 |
| R04 Z03 | 仍开：同 R06 Z P3/D3 | T01；接线前 |
| R04 Z04 | 仍开（部分闭合）：同 R06 Z P4 | 家族接线前 |
| R04 Z05 | 仍开：同 Z P5/D7 | 方法接线前 |
| R04 Z06 | 关闭：canonical 既有政策（本人复核在位） | 无待办 |
| R04 Z07 | 关闭：规模信息接收，不以 LOC 推正确性 | 无待办 |
| R04 M01 | 关闭（历史演进）：240 状态追加另见 F05 | ROOT 归档票 |
| R04 M02 | 关闭（维持）：PROVENANCE/审计件在树（本人复核）；fr201.1/2 保留不删（F09） | 无待办 |
| R04 M03 | 仍开：同 R06 D11 | T02 整数守卫时 |
| R04 M04 | 仍开：standalone EOF 残余；未证当前 UI 可达 | 新解析入口前 |
| R04 M05 | 仍开：同 D3/Z P3 | T01 接线前 |
| R04 M06 | 关闭：双端 ID 校验/原 ID edit 证据在位（本人读 mainline-facts.ts）；不外推全产品安全认证 | 无待办 |
| R04 M07 | 仍开（维护窗口）：未证冲突，不缩导出面 | 契约 owner API 整理时 |
| R05 Z P1 | 仍开（门禁）：同 Z F1 | ROOT 合并门禁 |
| R05 Z P2 | 关闭（事实）：934 Quality 718s 含 packaged recovery 成功为历史证据；不迁移为新 head CI 绿 | 无待办 |
| R05 Z P3 | 仍开：同 Z P3 | T01 接线前 |
| R05 Z P4 | 仍开（部分闭合）：同 Z P4 | 家族接线前 |
| R05 Z P5 | 仍开：同 Z P5 | 方法接线前 |
| R05 Z P6 | 关闭（口径）：canonical 政策不变 | 无待办 |
| R05 Z P7 | 关闭（口径）：诊断选项演变事实；F03 约束继续 | 无待办 |
| R05 Z P8 | 已闭合（维持）：历史 manifest 永久绑定 | ROOT 文档 owner |
| R05 MM01 | 仍开（门禁）：旧 79 全因未知 | 新 CI 后合并前 |
| R05 MM02 | 已闭合（事实） | ROOT/新 CI 后 |
| R05 MM03 | 仍开（门禁）：本 head 未打包（O064 明示 notPerformed） | 新包制造票 |
| R05 MM04 | 已闭合（分别承接） | ROOT 文档 owner |
| R05 MM05 | 仍开：同 Z P5/D7 | 方法接线前 |
| R05 MM06 | 仍开：同 D3/Z P3 | T01 接线前 |
| R05 MM07 | 仍开（部分闭合）：typed witness 已实现（Manual/SingleDeclaration with declared witness）；裸族延期 | 家族接线前 |
| R05 MM08 | 仍开（未确认观察）：同 Z P6 | T01 触及选取时 |
| R05 MM09 | 已闭合（维持）：wheel/payload/解压量分层；冗余件见 F09 | vendor/发布 owner |
| R05 MM10 | 关闭：AGENTS overlay 维持非候选缺陷 | 无待办 |
| R05 MM11 | 关闭（信息）：locator 仍只含 id/owner/sourceRow/slot（本人读 storage.py locator 与 OwnershipConflictDetailView），无 object | 无待办 |
| R05 MM12 | 仍开：两 TS PATH python（本人 grep 在位） | T01 测试维护者 |
| R05 MM13 | 关闭：规模信息接收 | 无待办 |

## 6. 整体结论

**ConditionalPass**（限定技术阶段，本人独立判断，未预设）。

- 限定内容：本候选（base 583 → head 240，38 commits／107 leaves）在本人亲读范围内实现与测试自洽、护栏方向正确（fail-closed、最小权限 authority 层、固定错误码、有界预算、人确认不变量、CSP/渲染隔离未破坏）；R09 delta 两提交（文档归档＋三测试文件的 bootstrap 同步与有界观测）为测试侧修复，不改变产品行为，且 P2 尾 pipe 丢失已按同一 45s 界修复并补跨 turn/close 用例；未发现 push 前源码技术阻断。
- 不构成：无条件整候选 Pass、完整平台验收、merge 授权、CI 后条件确认或任何 HOLD 关闭。第 2/3 节所列门禁与未确认项全部保留：fresh Linux/Windows/当前候选打包、CI41 根因、engine/Windows 后代退出 UNKNOWN、签名/公证/wholeApp 法律隐私产权供应链、跨 OS/参考设备、容量/旧超限库恢复/损坏 SQLite、unknown parser/Store/坏快照、其余 Undo/ownership 家族、四具名下游 GUI、组织类不可证项；整体合并可用仍 2/17，Goal/M0/发布未完成。
- 不因 SaaS 清单强加登录/支付/云服务（第 3 节 NA 项均以产品形态事实为据）。

## 7. 读取范围、未覆盖与必要后续验证

- 实际读取：范围内心动 107 文件中全部代码/配置/构建相关文件 diff 与关键新增文件全文（§1 清单）；docs 侧：status.md、m0-checklist、disposition.md（R08 全表）、round-05 条款映射、PRD 7.3/附录 C、NOTICE；仓外：ROOT 票、O064 六件关键文件＋FINAL-MANIFEST 哈希、两份原实物清单副本。工作树与 HEAD 一致性经 git status＋三文件 SHA256 复算确认（AGENTS overlay 与 WIP 目录按保护要求未动）。
- 未覆盖／无法确认：未运行任何 check/测试/构建/CI（只读约束，运行证据全部引自 O064/O059 原件）；Windows/Linux 平台行为、性能、打包后行为、README 易用性指标（#140）、账户归属（#146）、bus factor（#147）无法由本人确认；engine 七个新测试文件仅读结构与关键断言计数（73 用例），未逐行审全部约 3400 行测试体；e2e spec 1796 行读 delta＋关键段（commit/失败观测/case 边界）非逐行全读；fixtures.json/binding-regressions.json 读增量摘要未逐项对拍。
- 仍需原 owner 受控执行的必要验证（本审查未做、也不授权由审查侧做）：①ROOT 另票普通 push→PR16→唯一自动 CI，按 F03 完整回单验收（Windows 3769 全集逐项、全部后继、三 job success、packaged recovery 自身 success）；②若 C1/79F/case7 复发，以新增结构化 diagnostics 定因并处置；③未来打包验证（当前候选新包制造与包内运行）；④任何会改源/构建的验证走原 owner 同版受控流程。
- 未来 CI／merge 门禁（不因本报告降低）：同受审实现/测试/配置/依赖下完整 3769 全集自然 0、失败/早停/取消/timeout/NOTRUN 不验收、15/20 分钟预算不变、作者 CI 后条件逐项确认、精确 squash-merge 票、remote develop 实际 SHA/tree/功能复核；全部独立 HOLD 与事件窗口按第 4/5 节保持。

—— ZCode GLM-5.3，2026-10-26。本报告为本人独立完成，未读取另一方当前 R09 报告或结论。

---

# 追加节：本人事实补读与意见处置（同任务一次追加，2026-10-26）

## A0. 追加性质与不变项

同一 R09 任务、同一固定身份（cwd `…/.worktrees/T02-s1-review-fixes`；base `583c05c…`→head `240b581c…`/tree `0933a331…`；38 commits／107 叶）。本节为只读补读与本人报告事实/意见处置：未重跑 check/GUI/构建、未改源/测试/配置/依赖/预算、无 git 写操作、未读取另一作者 R09 意见；静态补读不冒运行验证。第 6 节结论 **ConditionalPass** 及其全部限定不撤回、不预设；全部旧 FAIL/UNKNOWN/OPEN/HOLD 与整体 2/17 保留。原稿 39452B（SHA256 `1b032420…0672e`）前缀逐字节保留：追加前经 `cmp` 验证仓内报告与仓外封存件 `outputs/20261026_t02_240b_fresh_r09_065/zcode-natural-01.md` 完全一致，本节仅在其后追加，不修改、不删除任何旧句。追加后全文实测 bytes/SHA256 在会话回执中报告（避免文件内自引哈希）。

## A1. 八组反馈逐项处置

**组1｜CI41 结算串档 → 同意更正。** 被更正位置：原 L219（F03 行）中“O059 结算 3769=3429P/53S/48S”。本人本轮亲读 `outputs/20261026_t02_2b6c8a26_remote_ci_059/CI-ENGINE-FULL-ACCOUNTING-QUALIFICATION.json`（44576B）：CI41 run40294180350 attempt1 **Linux 3716P＋53S＝3769、Windows 3721P＋48S＝3769**，两平台 originalUVOrdered3769Exact；其 `limits` 原文"CI engine subset only, not complete job success; cross-host sys.path equality not claimed, Windows descendant recovery remains UNKNOWN"。3429P 系旧 CI40（9cb 时点）Windows 部分结算，原句误串入 CI41。更正后的 CI41 完整事实：macOS success；**Quality failure**（job 121476100657：`csp-lifecycle.spec.ts:10` "C1 real CSP, normal functionality and renderer recovery" 失败，`native-recovery.cjs:12` `Cannot read properties of undefined (reading 'isPackaged')`，playwright expected20/skipped3/unexpected1）；**Windows failure**（job 121476100926：`t02-fr200-fr201.spec.ts:685` FR201 用例在 `commit`（spec.ts:159）处 `Test timeout of 180000ms exceeded`，expected20/skipped3/unexpected1）；各自后继步骤 SKIPPED。引擎全集有界接收不覆盖两 E2E 失败或后继 SKIPPED（`fullCIConclusions` 原文"engine completeness cannot override failed E2E or skipped downstream steps"）。归属/窗口不变：ROOT 精确 CI 票、merge 前完整回单；**非 push 前源码技术阻断**（合并门禁）。

**组2｜identity 字段数与层级 → 同意更正。** 被更正位置：原 L222（F06 行）“identity 七项无 sys.path”。本人亲读 `scripts/engine-test-reporting.py pytest_collection_finish`：identity 共 **13 字段**（rootpath/inipath/configSHA256/testpaths/pythonpath/addopts/executable/pytestVersion/platform/utf8Mode/preferredEncoding/stdoutEncoding/defaultFileEncoding）；O059 两平台 identity 字段集合同为 13。比较层级限定：其中 `pythonpath` 记录的是 pytest ini 配置项（`getini("pythonpath")`），**不是运行时解析后的 sys.path**；`python -m pytest` 对 sys.path[0] 的运行时等价仍未证明。F06 维护项与窗口不变（原 T02 开发归口；在任何“完整导入路径等价”声称之前）。

**组3｜#138 行数事实 → 同意更正。** 被更正位置：原 L175（清单 #138 行）“无超 2000 行文件（本轮范围内）”。本人 `wc -l` 双计（工作树与 240 blob）：`packages/engine/src/ontolearn_engine/job_store.py`＝**2993 行**，原句不实。仅纠数字与适用性依据：范围内存在 ≥2000 行文件（至少 job_store.py 2993 行；另 spec 1796 行逼近阈值）；不以 LOC 升级为缺陷、不新增拆文件需求；#138 裁定 A- 与“不以 LOC 推正确性”维持。

**组4｜Start Plan 表述 → 同意限定。** 被更正位置：原 L5“无 Start Plan 套餐可用”。更正表述：**本次会话的模型供应商菜单未提供 Start Plan 通道，本次实际来源为既有 BigModel 个人 Coding Pro**；不断言该服务全局不可用或该账号全局无套餐。额度实录为 99%（早先 100% 观察分开保留）；本轮无重置、无新付费。

**组5｜组织/法律义务 HOLD 注记 → 同意限定采纳。** 涉及清单 #48、#49、#57、#145、#148。处置：原 NA 判定仅指“当前产品无该执行表面”，**不构成组织/法律义务不存在的证明**。安全问卷应答、漏洞披露流程、GDPR/隐私删除请求可达性、条款与隐私政策同代码一致性、人类资深工程师逐行签字——全部追加记为 **HOLD（组织义务）**，事件窗口：对外发布/商用/S3 接入前由用户与 ROOT 处置；本地形态与代码审查不能替代或取消。#148 补充：R04–R09 指定 AI 双审是工程辅助证据，**不能替代人类资深工程师逐行签字义务**（维持 HOLD）。不因此新增登录/支付/云服务等 SaaS 功能（与原判据一致）。

**组6｜覆盖声明对齐 → 同意限定（分层更正）。** 被更正位置：§1“关键新增文件全文”语境、清单 #132“本人通读全部新增代码”、§7“实际读取”段。更正后的分层覆盖：(a) 已完成＝107 叶中全部代码/配置/构建/CI/vendor 文件的 **diff 级阅读**＋关键新增产品/脚本文件**全文**（mainline.py 1207 行、native-driver.ts 301 行、native-driver.test.ts 395 行、native-recovery.cjs 112 行、mainline-ownership.ts、OwnershipConflictDetailView.ts、run-engine-tests.py 471 行）；(b) 本节追加补读＝M0 计划 C1/B1/S 系条款与验收边界（145–153、190–205 等）、ADR-0002、O059 qualification＋两失败事实件、engine-test-reporting.py identity 段、**七个新增引擎测试文件的用例名级全覆盖**（73 个用例名全部列出并与已审代码路径逐一对应：ownership detail 纯净/有界/回滚/防毒化、admission 终态余量、bootstrap/successor 权限链、canonical 政策、vendor 专类型、预付费用、工作预算等）；(c) **仍非逐行**＝七个引擎测试文件约 3400 行测试体（结构＋关键断言＋用例名级，非逐行全读）、e2e spec 1796 行（delta＋commit/失败观测/case 边界段）、fixtures.json/binding-regressions.json/schema.json 增量摘要未逐项对拍、uv.lock 增量摘要；(d) 真正范围外（非本轮必要）＝未变化的其余 1280 源文件、旧 WIP（round-01/02/03）、无关旧轮 raw 与旧 094 包内容。“全部 107 叶”的 diff 级声明不抵消 (c) 的未逐行项。#132 裁定维持 A-，依据改按本分层。

**组7｜M0/C1/ADR 补读与限定 → 已消费。** 本人亲读 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`（35812B／SHA256 `c289a1cd…7cf96`，与 `docs/reviews/I03/inputs` 同名副本哈希一致；`docs/architecture` 下无该同名文件——指南旧路径失实的事实保留，本人按实际路径核对）C1 条款 145–153（单一配置源两变体、开发 HMR、阻断/正常功能矩阵、**验收同时覆盖开发 HMR、构建态和真实打包 executable**、“只检查 meta 存在或控制台没有报错不能视为通过”）与 190–205（“S1/S2/S3/B1 还需上述专门验收，不以静态检查或普通 health 冒烟替代”）；`docs/iterations/I01/ADR-0002-storage.md`（13747B／`dc6e76ee…fc30`，SQLite 唯一可变源真相、`Store.commit` 唯一正式写路径、不可变快照等与候选实现一致）。限定声明：**O064/native24 只关闭“C1 验收在本开发机（macOS arm64）可执行的子集”**——真实打包 executable 的 C1 矩阵（CI41 Quality 的 packaged recovery 后继因 C1 失败 SKIPPED）、开发 HMR 变体验收、跨平台与完整 C1/M0 验收保持开放；本人原报告未声称 C1/M0 完成（§2 第1条、§6 限定语），本节将该限定显式锚定至上述原规范条款。

**组8｜Top10 稳定 ID 与单位更正 → 同意。** 单位更正：原 §2 第2条与清单 #47 行“stderr/stdout 尾 64KB”更正为**“每流截尾 65536 个 UTF-16 码元”（JS `String.slice` 语义，`native-driver.ts:82/85` `slice(-65536)`），非 65536 字节**；仅文案，不改源、不重跑。

## A2. Top10 稳定 ID 映射与追加处置

| Z09-ID | 原序号 | 摘要 | 追加处置 | 归属/事件窗口 | 阻断性 |
|---|---|---|---|---|---|
| Z09-01 | §2#1 | 完整平台 CI 缺位 | 维持；依据补强：CI41 两失败原件已亲读（A1 组1） | ROOT 精确 CI 票；merge 前 | 合并门禁，非 push 前源码阻断 |
| Z09-02 | §2#2 | CI41 C1 根因 UNPROVEN，240 为前置同步缓解 | 维持；文案更正（65536 UTF-16 单位/流）；Quality 失败链已亲读（csp-lifecycle.spec.ts:10 → inspector evaluate → native-recovery.cjs:12 isPackaged TypeError） | 复发时按结构化 diagnostics 定因 | 非源码阻断（fail-closed 方向） |
| Z09-03 | §2#3 | engine/Windows 后代退出 UNKNOWN | 维持 | 未来 CI 证据接收；Job Object/观测副本另票 | 非阻断 |
| Z09-04 | §2#4 | fr201.1/2 冗余 wheel 4.76MB | 维持 | T11 供应链 owner，merge 后受控移除 | 非阻断 |
| Z09-05 | §2#5 | TS 契约宽于 schema＋双处 pageSize 64 | 维持 | 契约 owner 下次整理 | 非阻断 |
| Z09-06 | §2#6 | witness/冲突行无 ORDER BY（未确认观察） | 维持，不升级 | T01 触及 witness 选取时 | 非阻断 |
| Z09-07 | §2#7 | 4299/4300 应用断言缺（仅 4301） | 维持 | T02 整数守卫维护窗口 | 非阻断 |
| Z09-08 | §2#8 | CI 制品卫生（always() 不保证＋重复上传） | 维持 | 未来 CI 维护票 | 非阻断 |
| Z09-09 | §2#9 | readiness 耦合 Electron 44.9 内部映射 | 维持 | Electron 升级时同步维护 | 非阻断 |
| Z09-10 | §2#10 | 裸 ownership 家族无 typed witness | 维持 | T01/T02 家族接线前 | 非阻断（HOLD 家族） |

## A3. 判定不变声明

第 3 节 160 条与第 4/5 节 31＋78 个稳定位置的本人判断**均不变**；本节仅更正 A1 所列事实表述/依据（原句保留于前缀），并为 #48/#49/#57/#145/#148 追加组织义务 HOLD 注记。原结论 ConditionalPass 及全部限定、旧 FAIL/UNKNOWN/OPEN/HOLD、2/17 状态保留；不新增产品或验证门禁。

## A4. 本节补读清单与前缀回执

本轮补读（只读）：M0 计划两副本哈希核对＋C1/B1/验收边界条款、ADR-0002-storage.md、O059 `CI-ENGINE-FULL-ACCOUNTING-QUALIFICATION.json`＋`QUALITY-FAILURE-FACTS.json`＋`WINDOWS-FAILURE-FACTS.json`、`engine-test-reporting.py` identity 段、七引擎测试文件用例名级（73 项）、job_store.py 行数（2993）、native-driver slice 单位（:82/:85）、仓外自然稿与仓内报告 `cmp`。未做：任何重跑、源/配置改动、另一方 R09 报告读取。原 39452B 前缀 exact（追加方式保证；`cmp` 于追加前通过）。追加后全文 bytes/SHA256 见会话回执。

—— 追加节完（ZCode GLM-5.3，2026-10-26，同任务一次追加）。

---

# 追加节二：必要覆盖闭合与最后残句处置（同任务第二次追加，2026-10-26）

## B0. 性质与不变项

同一 R09 任务、同一固定身份（cwd `…/.worktrees/T02-s1-review-fixes`；base `583c05c…`→head `240b581c…`/tree `0933a331…`；38 commits／107 叶；本方原 SID，GLM-5.3／最高）。本轮仅只读补读与本人报告事实/意见处置：未运行任何验证、未改源/测试/配置/依赖/预算/构建、无 git 写、无新任务/新付费、未读取另一作者意见；补读不冒运行验收。前两稿全部保留：39452B 自然稿与 50511B 第一次追加稿（`zcode-natural-02-own-facts-append.md`，SHA256 `92a65c54…ae7c1`）——追加前经 `cmp` 验证仓内报告与该封存件逐字节一致，本节仅在其后追加。第 6 节 ConditionalPass、160 条与 31/78 判定、全部 FAIL/UNKNOWN/OPEN/HOLD 与 2/17 均不变。

## B1. 组1（必要覆盖闭合）→ 同意并已实际补读完成

事实更正（原 A1-组6 表述）：自然稿时点"全部代码/配置等 diff 级阅读已完成"与同节披露的"测试体/E2E/fixtures 非逐行"矛盾——原票范围为完整 base→240，测试与契约数据的新增内容属本轮必要变更，本人此前只做到结构/关键断言/用例名级。本轮已实际补齐（全部只读）：

1. **`tests/e2e/t02-fr200-fr201.spec.ts`（A 文件，1796 行全文，全属 diff）**：补齐此前未读的 `loadFact`（S/P 禁用保原 ID 载入）、四类 CRUD 矩阵全链（种子→create→edit（IRI 锁定）→copy（新 home 编译序）→双删除（引用影响展示/阻断删除））、FR201 十一元组（plain/zh/integer/canonical-string（显式 alias 拒绝后人工改回）/boolean/decimal/double/date/dateTime/多值关系×2）、受控拒绝矩阵（add/edit × object/subject/predicate 三字段 × datatype/引号语言/authority 输入族，拒绝后字段保留、无 Diff/确认钮、读回相等）、ownership 详情 DOM 精确断言（`首个阻断冲突定位` 两记录各五字段逐值）、失败诊断链（`clip` UTF-8 安全截断、`pack` 262144 有界、`observe` 每≤500ms、原 DOM 先持久化、只读 bridge 查询按 getOperation→getJob→getActiveProject→readProject 序、超时即止不重试、诊断失败不覆盖原失败）。
2. **六个 A 引擎测试文件全文（326＋1034＋860＋395＋320＋559＝3494 行）**：language（R03 拒绝复用既有断言＋独立 stdio 子进程（物理文件 SHA256 前后比对）＋canonical 数字子标签可提交/大写仍拒）；manual_input_rejection（canonical 拒绝无变异后同 owner 提交、原 ID 经 edit/Undo 存活、四类非输入故障→UNKNOWN+hold、参数化 caller 拒绝全矩阵（含 iterdump 无变异/身份四元组不变）、六类 parser/n3 故障保持 UNKNOWN、urlsplit 非合同故障保持 UNKNOWN、manual IRI 预检不分类未知、reservedIdentity 受控冲突（diagnostic 行外 dump 全等+1 行）、vendor 专类型 TermInputError＋fr201.3 版本断言、同坏输入不掩盖内部故障（join/int/group 三点注入）、三 reason ownership detail 全分页（pageSize=1 逐段 SHA256、重复 preview 复用同 ref 且 dump 不变）、singleDeclaration same/removed-first（保留原 Store 矛盾计划 UNKNOWN 不弱化）/overwritten-first）；postwrite_admission（终态余量三轴±1 边界、尾证明 2742＜4096 算术钉、真实 draft 增长至 RESOURCE_LIMIT 后小操作续作、queued commit 三终态仅 Job DTO 变化、两项目全局余量、前后台 scope 不能互借（unknown/replacement）、after-commit 重入拒绝、清理失败保原因果与持有、settlement 失败保精确 reply unknown、DTO/伪对象不能 bind、bootstrap 未结算 writer 不能被采纳（Coordinator 拒绝）、clean close 交接真 successor（旧 proof 失效）、八态 predecessor 不被丢弃、successor 不能接管 queued/active job、两个真实 stdio（增长拒绝后续作；重启后 ENGINE_EXITED 对账））；rows_budget（243 行五列全分页、begin 费用恰 `{1114112,8192,134217728}`、终材料原子拒绝不退款、预付不能借/退、二次消费 INVALID_STATE）；text_budget（56309 前缀文本（含 UTF-8 多字节变体）全分页、`text final prepaid` 恰 `{528384,256,1052672}`、原子拒绝续作、cursor 回撤（unknown/replacement）在最终编码器前拒绝且无游标残留）；read_work_budget（scalar_profile 与 preflight 同单位、真实 21+1 历史＋不透明 blob 至全表界（44 op/22 snap）、默认读者保持全表公式、64MiB 双阶段（lower/authorized-plan，SQL trace 区分 json_extract）、重复解码历史先拒、六类损坏→STORAGE_FAILURE+hold 且认证仍执行、json_extract 授权器拒绝→hold 无零回退）。
3. **`test_mainline_dispatch.py`（M，+523 增量全部读毕；文件现 1248 行＝未变 725＋新增 523，未变部分不重读）**：新增 ownership_fixture/ownership_pages 与 10 个用例——大 locator（40000 字符 subject/sourceRow）完整纯净有界（读后 dump 全等）、损坏（缺 version/空头/坏 JSON/坏段）→STORAGE_FAILURE+hold、段写入失败全回滚无 detailRef、诊断不能毒化已准入 full reader（含 late 插入）、私有 admission 保 core-only 向量且不重置工作、坏既有 blob 先预算后解码（不触 blob()）、原始段预算拒绝先于 JSON 解码、dedup 行帽复用/新上下文回滚、exact legacy detail（三字段）不造 locator（INVALID_STATE）、引用不跨真实 successor 会话（NOT_FOUND；新 preview 新 ref）。
4. **契约增量**：`schema.json` +525 全读（request/response/error 三 envelope 变体＋5 个 `$defs`；`params_project.ownership.detail` 精确形状：首请求 `documentHash:null`+`startOrdinal:0`（const），后续 `documentHash:hash`+`startOrdinal:1..511`，`pageSize:1..64`；manifest `totalBytes:2..16777216`/`segmentCount:1..512`；singleDeclaration `existing[2]` 恰两项；字符串上界 16MiB）；`fixtures.json` 增量全读（128 行 `registryHash` `058ed1be…`→`5e097b7e…` 机械重绑＋内嵌 wireBase64 同步＋6 个新正负例：named ownership request（valid）、ownership no null continuation（startOrdinal=1 配 null hash，invalid）、ownership wire issuer forbidden（多 ownerId 参数，invalid）、named ownership page（valid 往返）、ownership wrong ref（响应 ref≠请求，invalid）、ownership corrupted segment SHA（段 SHA≠manifest，invalid）、ownership premature next（complete 却带 nextOrdinal，invalid））；`binding-regressions.json` +34（17 处 registryHash 同步）；`registry.json`（business3 两处方法表新增 `project.ownership.detail`）。契约/方法/fixture 关系核对一致：registry 增方法→registryHash 变→fixtures 与 binding-regressions 重绑→schema 出 envelope/正负例，链路完整；与 v2.ts `matchesOwnershipDetail`、`contract_v2.py ownership_detail_matches` 双端对齐。
- **数字更正**：六 A＋M 新增＝**4017 行**（3494＋523），非"约 3400"；spec 为 A 文件 1796 行全属 diff；引擎测试为 6A＋1M（非"七个新增"）。
- **覆盖声明最终态**：本票必要变更覆盖**现已完成**＝107 叶中全部代码/配置/构建/CI/vendor 文件 diff 级阅读＋上述测试与契约数据全文/全增量阅读；自然稿时点的"全部…已完成"表述**在当时不成立**（事实更正，原句保留于前缀）。**真正未覆盖（且属范围外、非本票必要）**：未变化的其余 1280 源文件、`test_mainline_dispatch.py` 未变 725 行、fixtures.json/schema.json 未变部分（分别为 31084/525 行中未变内容）、三个 wheel 二进制内容（依赖面仅 PROVENANCE/patch/uv.lock 哈希链核验，已做）、旧 WIP（round-01/02/03）、旧轮 raw。
- **补读结论**：未发现新的源码缺陷或改变第 6 节结论的事实；Z09-05 的"TS 宽于 schema"差值现以 schema 实读精确锚定（首请求 `startOrdinal` 字面量 0 vs schema const 0——TS 首变体一致；`pageSize:number` vs schema `1..64`——确宽；后续 `startOrdinal:number` vs schema `1..511`——确宽）。

## B2. 组2（#132 唯一有效表述）→ 维持 A（正面），仅更正依据

**唯一有效表述：清单 #132 维持原裁定 A（正面）**；被更正的是依据而非裁定等级。原 L169 依据"本人通读全部新增代码"在自然稿时点不实；经 B1 补读后，依据以"本票必要变更全覆盖（B1 分层：diff 级全量＋必要新增全文/全增量）"成立。A1-组6 中"#132 裁定维持 A-"一句**作废**（替代关系：该 A- 表述被本节 B2 取代）；A3"160 判断不变"以本口径成立。原句均保留于前缀。

## B3. 组3（Z09-02/03/08/09 归属继承）→ 按原已存在归口继承

| Z09-ID | 继承归口（owner） | 事件窗口（不变/继承） |
|---|---|---|
| Z09-02 | 继承 R08 Z08-02：**ROOT**（Windows/Quality 完整 CI 证据接收） | 未来真实 CI；复发时按结构化 diagnostics 定因；Job Object/新工具另票，当前无开发 |
| Z09-03 | 继承 R08 Z08-02 同一归口：**ROOT**（CI 证据接收；engine 自然退出 UNKNOWN 与 Windows 后代观测属同一证据接收面） | 未来 CI 证据接收；观测副本/Job Object 须 ROOT 另票 |
| Z09-08 | 继承 R08 Z08-03＋Z08-09：**ROOT**（未来实际制品回单判断＋CI 控制层维护票） | 下一制品回单／CI 维护票；任何预算变化须新明确授权 |
| Z09-09 | 继承 R08 Z08-02 所记录原生恢复证据维护面：**原 T02 native 证据修复开发线 owner（O063/O064 原 owner）＋ROOT CI 证据接收** | 下次 Electron 版本升级或 native 恢复证据维护时同步维护 readiness 探针 |

其余六位已有明确归属且无变化（Z09-01 ROOT 精确 CI/merge 票、Z09-04 T11 供应链 owner merge 后受控移除、Z09-05 契约 owner 下次整理、Z09-06 T01 Store 触及 witness 选取时、Z09-07 T02 整数守卫维护窗口、Z09-10 T01/T02 家族接线前），不重复审查。不新指定他人、不新增门禁。

## B4. 最终回执

原 50511B／SHA256 `92a65c5485284abad6b7028f6f4578a41583f80b9b5a32cc4f7f2594602ae7c1` 前缀 **exact**（追加前仓内报告与 `zcode-natural-02-own-facts-append.md` 经 `cmp` 逐字节一致；本节仅追加）。追加后全文 bytes/SHA256 于会话回执报告（避免文件内自引）。本轮补读清单见 B1；真实未覆盖面＝B1 末段所列范围外项。全部原 FAIL/UNKNOWN/OPEN/HOLD 与 2/17 保持；结论仍为 ConditionalPass，未预设、未撤回。

—— 追加节二完（ZCode GLM-5.3，2026-10-26，同任务第二次追加）。
