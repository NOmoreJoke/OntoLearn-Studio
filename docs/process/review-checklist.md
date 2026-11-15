# 工程审查清单（160 项分层拆分版）

> 来源与效力：本文是 2026-10-24 用户授权审查清单（160 条英文原文）的结构化拆分版，原文逐字保留、一字未改；加载规则见 [`review-policy.md`](review-policy.md) §4 第 5 条。本文与政策同受 L2 保护（`.github/review-policy.json` 第一条规则），改动即触发双审，防止降低门槛。
> 总量核对：核心必审项 37 条 + 领域模块 M1–M6 共 84 条 + 默认不适用项 39 条 = **160 条**；每条原文在本文中恰好出现一次。

## 使用规则（流程约束，不可跳过）

1. 先判断适用性；不适用直接跳过，报告简短交代类别和依据。
2. 不为了满足清单而增加无用的功能；严禁为满足第三节清单扩建 SaaS/登录/计费/云功能。
3. 适用但未检查、缺条件的，明确写"无法确认"，不假装检查过。
4. 按严重程度排序，先列最值得修复的 Top N（不足 10 项不凑数），同时完整列出其余阻断问题与原验收缺口；具体证据、文件位置、风险、严重度和未验证边界必须明确。
5. 禁止审查员修改被审业务代码；审查模型只读实现，仅约定验证和独立报告写入。
6. 加载方式：L1 只审第一节"核心必审项"；L2 审第一节 + 按 diff 路径命中的领域模块（第二节）；第三节默认整组跳过，仅在重激活条件成立时审。

## 一、核心必审项（Core Mandatory Items — 每次 L1/L2 必查，37 条）

每次代码变更（L1/L2）都必须过一遍。条目中的 SaaS 场景词（如 signup/checkout）按本地优先单机桌面端的对应流程理解（首次启动、核心计算流、导出等）。

#### 设计与数据模型（1 条）

> a schema someone designed, instead of one the AI improvised table by table

#### 输入校验与净化（3 条）

> validation on the server, not just in the form

> input sanitization everywhere a user can type

> forms that keep what people typed when one field fails validation

#### 密钥卫生与依赖真实性（4 条）

> secrets out of the code, out of the repo and out of the AI chat history

> rotating every key the AI pasted into a config file last month

> confirming every package the AI installed exists and is the one you meant

> dependency scanning, because the AI pulled in libraries nobody reviewed

#### 反馈、状态与可逆性（含幂等/去重）（6 条）

> empty states, loading states and error states on every screen

> error messages a customer can act on, instead of "something went wrong"

> undo

> a back button that does what people expect

> idempotency keys, so a retried payment doesn't charge the card twice

> deduplication for the user who clicks submit four times

#### 测试（单元/E2E/回归）（3 条）

> unit tests written by someone who knows what the logic should do

> end-to-end tests for signup, checkout and the other flows that make you money

> regression tests, so fixing bug 41 doesn't bring back bug 12

#### 可访问性基础（1 条）

> keyboard navigation and screen reader support

#### AI 行为边界（不可逆动作人工批准）（1 条）

> a human approval step for anything the AI does that can't be undone

#### 代码与工程流程（6 条）

> code a human can read

> code review on every change

> a branching strategy, so two people can work without overwriting each other

> deleting the dead code the AI left behind from its first three attempts

> splitting up the 2,000-line file the AI kept appending to

> architecture decisions written down, with the reasons

#### 文档与传承（5 条）

> documentation for whoever inherits this

> a changelog customers can read

> terms and a privacy policy that match what the code does

> every account, domain and repo in the company's name, not the name of whoever built the prototype

> a bus factor higher than one

#### 人的角色（每次变更仍适用的部分）（7 条）

> reading every line the AI wrote before it ships (a senior engineer)

> explaining why the AI's fix for one bug created two new ones (a senior engineer, again)

> testing what the AI says it tested (QA)

> saying no to the feature that breaks three others (a tech lead)

> turning "works on my laptop" into "works for every customer at once" (an architect)

> debugging the code when the AI that wrote it can't (a senior engineer)

> remembering why it's built this way, a year from now (someone who was there)

## 二、按变更路径加载的领域模块（Domain Modules M1–M6，共 84 条）

加载规则：以本次 diff 的文件路径与变更主题为准，命中某模块的触发路径或触发主题即整模块纳入审查；未命中则整模块跳过并在报告中注明"未触发 Mx"。判断宁可保守：拿不准时按触发处理。

### M1 安全与进程隔离（12 条）

- 触发路径：`apps/desktop/src/main/**`、`apps/desktop/src/preload/**`；CSP、IPC bridge、窗口安全边界；文件上传/导入；安全响应头、CORS、OWASP、静态与传输加密、最小权限；渗透测试、安全问卷、漏洞披露、失窃设备预案；公开漏洞后的框架修补。
- 不适用时如何跳过：变更不触及主进程/preload/任何安全边界（纯渲染层样式、纯文档、纯测试数据），整模块跳过并注明"未触发 M1"。

#### 注入与网络边界（4 条）

> protection against SQL injection, XSS, CSRF and the rest of the OWASP list

> file uploads that get scanned, size-limited and stored where they can't execute

> CORS rules that aren't "allow everything"

> security headers on every response

#### 加密与最小权限（3 条）

> encryption at rest and in transit

> least-privilege access for everyone, including the AI agent holding production credentials

> logs that record who did what, without recording passwords, tokens or card numbers

#### 安全运营与响应（5 条）

> a penetration test before your enterprise customer's security team runs their own

> answers to the security questionnaire every enterprise buyer sends, with evidence behind each one

> a disclosure process for the day a stranger emails you a vulnerability

> a plan for the day a laptop with production access gets stolen

> patching the framework the week a vulnerability goes public (security)

### M2 存储、迁移与备份恢复（11 条）

- 触发路径：`packages/engine/src/**/storage*`、`Store`、SQLite schema/migrations、`tests/unit/*storage*`；备份、恢复、PITR；软删除/回收站；分页；保留策略；在线库迁移；审计轨迹的查看与编辑；跨表/备份/日志的删除。
- 不适用时如何跳过：变更不涉及任何持久化结构、迁移脚本或数据删除/恢复路径，整模块跳过并注明"未触发 M2"。

#### 迁移与结构演进（4 条）

> database migrations that run forward and roll back

> migrations that don't lock the main table at 2pm on a Tuesday

> running a migration on a live database without losing a row (a backend engineer)

> designing the data model before your second customer breaks it (a backend engineer)

#### 备份与恢复（3 条）

> backups every night

> a restore from those backups, tested, because a backup you've never restored is a hope

> point-in-time recovery for the day someone runs a delete without a where clause

#### 删除、保留、分页与审计轨迹（4 条）

> soft deletes, so "I deleted it by accident" is a support ticket and not an incident

> retention rules, and code that deletes what your contract says you'll delete

> pagination that still works on page 400

> audit trails that show who viewed a record, not just who changed it

### M3 公共契约与版本兼容（18 条）

- 触发路径：`packages/contracts/**`；版本化 API、第三方 API 响应格式变化、webhooks、OAuth、API keys/限流、sandbox；CSV 导入/导出；数据模型演进；时区、撇号、i18n、emoji、RTL、本地化格式；浮点金额。
- 不适用时如何跳过：变更不涉及对外契约、导入导出格式或本地化/数值正确性，整模块跳过并注明"未触发 M3"。

#### 数据正确性与本地化（6 条）

> timezones stored right, so the 9am reminder doesn't fire at 4am

> the customer with an apostrophe in their last name

> emoji, accents and right-to-left text in every field

> money stored as integers, because 0.1 + 0.2 doesn't equal 0.3 in floating point

> currency, rounding and tax rules for every country you sell into

> translations, with dates and numbers formatted for each locale

#### 数据模型演进与导入导出（3 条）

> a data model that survives your second customer asking for "one small change"

> exports, because sooner or later every customer wants their data in a spreadsheet

> imports that survive the CSV someone saved in 2009

#### 契约与第三方集成（9 条）

> integration tests for every third-party API you depend on

> webhooks that verify signatures

> webhooks that retry, with a log of every failed delivery

> a versioned API, so you can change it without breaking your customers' integrations

> API keys customers can create and revoke

> API rate limits that protect you without blocking real integrations

> a plan for the day a third-party API changes its response format without telling you

> OAuth token refresh, because tokens expire at the worst possible moment

> a sandbox where customers can test their integration

### M4 引擎、后台任务与缓存失效（17 条）

- 触发路径：`packages/engine/src/**`、`invalidation-v2.json`；后台任务队列、退避重试、死信队列、cron；缓存与失效；索引；连接池；结构化日志、错误追踪；告警、仪表盘、追踪、状态页、runbook、postmortem；临时文件存储规则。
- 不适用时如何跳过：变更不触及引擎执行路径、任务调度或缓存键/失效逻辑，整模块跳过并注明"未触发 M4"。

#### 查询性能与并发（2 条）

> indexes, because the query that was instant on 50 test rows times out on 5 million real ones

> connection pooling, so a traffic spike doesn't exhaust the database

#### 任务、缓存与临时文件（6 条）

> background job queues, so slow work doesn't freeze the page

> retries with backoff, so one flaky API call doesn't become a lost order

> a dead-letter queue for the jobs that fail every retry

> cron jobs that don't run twice the day you add a second server

> caching, and clearing that cache when the data changes

> storage rules, so you stop paying to keep 2021's temp files

#### 可观测性与运维（9 条）

> structured logs you can search at 3am

> error tracking that groups the same bug instead of sending you 4,000 emails

> alerts that page a human, tuned until they stop paging for nothing

> dashboards for latency, error rate and throughput

> tracing for one slow request across every service it touches

> a disaster recovery plan, written down and tested once a year

> runbooks, so the engineer on call knows what "queue depth critical" means

> postmortems that change something

> a status page customers check before they email you

### M5 模型网关与 Agent 治理（8 条）

- 触发路径：涉及 `T08`/`I06`/模型调用/Agent 执行路径的任何变更；提示词组装、模型输出处理、模型供应商配置、用量计量与日志。注意："AI 不可逆动作须经人工批准"属第一节核心必审项，本模块变更时须同时核对。
- 不适用时如何跳过：变更不涉及任何模型调用或 Agent 路径，整模块跳过并注明"未触发 M5"。涉及把数据发往外部模型的路径时，"客户/患者数据不进提示词"按最严格口径审。

#### 注入与数据边界（2 条）

> protection against prompt injection in every field that reaches the model

> customer and patient data kept out of prompts that leave your network

#### 成本与质量护栏（3 条）

> cost alerts, so a runaway agent loop shows up the same day and not on the invoice (we learned this one for $1,382.59)

> a model spend cap per customer, so one heavy user can't run up your bill

> evals, so you find out when a model update makes your answers worse

#### 供应商依赖与留痕（3 条）

> a fallback for the afternoon your model provider goes down

> a migration plan for the day your model gets deprecated

> prompt and output logs for debugging, minus whatever you're not allowed to keep

### M6 打包、CI 与发布验收（18 条）

- 触发路径：`apps/desktop/electron-builder.yml`、`electron.vite.config.ts`、`scripts/build*`、`scripts/run-*`、`.github/workflows/**`、`tests/e2e/**`、`scripts/verify-*`、`docs/source-manifest.json`、`scripts/ci-quality-schedule.py`、`scripts/run-engine-tests.py`、`scripts/review-level*`、`.github/review-policy.json`、`docs/process/review-policy.md`、`docs/process/review-checklist.md`、`tests/unit/review-level*.test.ts`；部署管线、一键回滚、零停机、feature flags、环境一致、IaC、压测、预发测试数据、老旧硬件（五年前的笔记本）、on-call/SLA、弱网（酒店 Wi-Fi）、README 一小时本地跑通、支持与后台面板。
- 不适用时如何跳过：变更不触及打包配置、构建脚本、CI workflow 或 E2E，且不声称发布/验收，整模块跳过并注明"未触发 M6"。

#### 构建与环境（3 条）

> dev, staging and production environments that match each other

> infrastructure written as code, so the setup lives somewhere other than one person's memory

> feature flags, so you can ship the code without shipping the feature

#### 发布、回滚与验收环境（7 条）

> a deploy pipeline that runs the tests before anything reaches customers

> one-click rollbacks, because Friday deploys happen

> zero-downtime deploys, because your customers don't have maintenance windows

> load testing before the launch email goes out

> test data that looks like production without being production data

> testing on the five-year-old laptop your biggest customer's ops team still uses

> pages that load on hotel wifi

#### 依赖维护（2 条）

> monthly dependency upgrades, so you're never two major versions behind

> framework upgrades before the old version stops getting security patches

#### 支持与文档入口（3 条）

> a README that gets a new engineer running locally in under an hour

> an admin panel for your ops team

> support tooling, so customer success can answer questions without pinging engineering

#### 运维值守（3 条）

> an on-call rotation, and a person who picks up

> deploys, rollbacks, servers and the cloud bill (a DevOps engineer)

> answering the page at 3am when payments stop (whoever's on call)

## 三、本地优先单机桌面端默认不适用项及重激活条件（Default Non-Applicable SaaS/Cloud Items，39 条）

**本产品当前形态是本地优先单机桌面端。** 下列各项默认不适用：审查时可凭本节一行引用整组跳过（报告注明"引用第三节第 N 组，不适用"），**严禁为满足清单扩建 SaaS/登录/计费功能**。仅当文末重激活条件成立时，对应组才重新纳入审查（重激活由总控在任务书中标注，重激活后整组审查，不逐条挑拣）。

#### 第 1 组：多租户/SaaS 登录与账号权限（13 条）

> login that still works when someone puts a plus sign in their email

> password reset links that expire and work once

> MFA, plus a recovery path for the user who lost their phone

> sessions that time out, and a way to kill every session for one user

> SSO for the enterprise customer who won't sign without it

> SAML, because that customer's IT team doesn't do magic links

> SCIM, so a fired employee loses access the moment IT offboards them

> roles and permissions deeper than "admin" and "everyone else"

> checks that stop user A from reading user B's data by changing one number in the URL

> tenant isolation, so one customer's bug never shows another customer's records

> an admin "log in as this user" button for support, with an audit trail on every use

> rate limits on login, so nobody can guess passwords at scale

> lockouts that stop attackers without locking out your CFO the night before the board meeting

#### 第 2 组：计费、订阅与税务（9 条）

> subscriptions, upgrades, downgrades and proration

> failed-payment retries and dunning emails

> invoices with the customer's PO number on them, because procurement won't pay without it

> sales tax and VAT

> refunds, credits and partial refunds

> usage metering that matches what you bill, to the cent

> annual contracts with custom terms your billing logic never planned for

> revenue reports your finance team can reconcile

> PCI scope, and card numbers kept out of your database

#### 第 3 组：公网云基础设施与邮件（9 条）

> autoscaling for the Monday morning spike

> a CDN, so the app loads fast in Singapore too

> DNS, SSL certificates, and renewals that don't expire on a Sunday

> SPF, DKIM and DMARC, so your password resets don't land in spam

> bounce and complaint handling on every transactional email

> a second region, if your contract promises uptime one region can't deliver

> uptime checks from outside your own network

> emails that render in every mail client your customers use

> notifications people can turn off

#### 第 4 组：受监管与合同合规（8 条）

> SOC 2, which means policies, evidence and an auditor, not a checkbox

> HIPAA, the moment a single patient record touches your system

> a BAA with every vendor that touches that data, including your AI model provider

> GDPR deletion requests that reach every table, backup and log

> data residency for the customer whose contract says EU only

> quarterly access reviews someone signs off on

> walking an auditor through how patient data moves (security and compliance)

> accessibility compliance, because the enterprise contract requires it

### 重激活条件

- 第 1 组（登录与账号权限）：引入任何需要远端身份验证/授权的能力时重激活——云同步、团队协作、在线授权、远端账号体系。本地单机无账号体系，默认整组不适用。
- 第 2 组（计费与税务）：引入订阅、付费授权、发票开具或计费计量时重激活。当前无任何计费逻辑，默认整组不适用。
- 第 3 组（公网云基础设施与邮件）：部署任何公网服务端组件（自更新分发、遥测接收端、云后端）或开始发送事务性邮件时重激活。当前无公网部署面，默认整组不适用。
- 第 4 组（受监管与合同合规）：处理受监管个人数据（患者记录等）、签署含 SOC 2/HIPAA/BAA/GDPR 数据驻留条款的合同、或企业客户合同明确要求无障碍合规认证时重激活。当前均不成立，默认整组不适用。
- 以实际 diff 为准：只要变更实际触发第 1–4 组任一重激活条件，审查员应直接重激活对应组并整组审查，不因任务书未标注而跳过。
