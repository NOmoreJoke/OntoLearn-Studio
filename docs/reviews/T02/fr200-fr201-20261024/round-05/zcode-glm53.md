# T02 aff386f6 全新 R05 独立完整工程审查（zcode-glm53）

> 版本注记：本文件为原稿（36956B/259 行/SHA256 `24c87595bb08f8fa95090177f4e41099e2146f1541007cf9aba74e0e0f000f22`，已由操作者逐字封存于 `outputs/20261025_t02_aff386f6_fresh_r05_038/zcode/report-original.md`，本人哈希复核一致）经同任务事实复核后的修订稿；六项修订的事实依据与采否见 §12。结论维持原判定未变。

## 0. 结论（结论先行）

**最终结论：整个 FR-200/FR-201 候选（base 583c05c → head aff386f6，29 提交 / 71 差异叶 / 1355 tracked 源）为「附条件通过（ConditionalPass）」，其中包含对合并的阻断性条件；不是无条件 Pass，更不是 Fail。**

区分两层结论（任务明确要求不得偷换）：

1. **本地实现与同版证据层：通过。** aff 相对 cb8（R04 已双审的受审实现）仅 12 份证据文档 + 1 条 CI 路径（本人 `git diff HEAD~1..HEAD` 实测仅 `.github/workflows/ci.yml`；O036 桥接记录提交后全部 1355 物理源 bytes/mode 相等），业务源/测试/依赖/锁零变化。本地同版完整 check 一次自然 exit 0（O036：TS 39 文件 1892 全过；Python 3769 收集 / 3719 过 / 50 跳 / 1 原警告；Ruff 379 文件），aff 新 main 构建（606471B / SHA256 4309328d…）上原完整六 spec 真实 GUI 一次 6 PASS / 0 skip / 0 retry / 0 flaky（O037 + ROOT 票 64de5377… 逐笔重哈希核验）。FR-200/FR-201 本迭代范围（真实表单事实 CRUD、事实原 ID 编辑、多值并存、词法受控拒绝、ownership 真实 witness 分页重组与可见定位）与 PRD 307–318 行、附录 C/D/E/G、ADR-0002、D8 第 13/40 行的对照逐条成立（§4）。
2. **整候选现有门禁层：不可通过（阻断未关闭）。** 远端事实精确口径：**PR16 已存在**（https://github.com/NOmoreJoke/OntoLearn-Studio/pull/16，open、未合并，其 head 为旧 58c9）；**aff386f6 未 push、没有任何新 CI 运行**。CI36（run 40164456782 attempt1，跑在 58c9 原 head、实际 PR checkout 为合成 SHA 681ffbd0…，不得把 run.head_sha 当实际检出）三 job 中 macOS success，**Quality 取消**（进程打印 passed/runtime exit 0 但 GitHub step 结论 cancelled、packaged recovery skipped，不可抹平），**Windows 取消且取消前已出现 79 个 F**（language 6 + manual 72 + read-work 1，无任何 assertion traceback / 最终 pytest 总表；KeyboardInterrupt/stash KeyError 是取消次生，不是根因证据；默认编码假设仍是"高可信未确认"）。aff 的 CI 补丁只是 Windows 首败诊断配置（打印 Python/locale/utf8mode/file encoding + `PYTEST_ADDOPTS=-vv --maxfail=1 --tb=short` 仅作用于 Windows engine:check 步），**本人独立判定：该诊断补丁静态达到其声明目的（可过其自身诊断范围），但它尚未实跑——aff 未 push、无任何该配置下的真实结果；Mac 6 PASS 不能关闭 79F，未来诊断绿也不得当完整验收**；在 Windows 真实首败取证 → 根因关闭 → 三 job 在原 15/20 分钟预算内全绿之前，整候选不满足既有合并门禁。此为阻断条件，非新发现产品缺陷（根因未知，本人无 Windows 反例证据，不得预设为产品缺陷或环境噪音）。

阻断项与条件清单见 §10；本轮未发现新的阻断级代码缺陷（问题清单 §7，最高为中危/门禁级）；全部既有 OPEN/HOLD 按原分工保留（§7、§8）。

---

## 1. 实际身份、独立性与输入完整性

| 项 | 实际值 | 说明 |
| --- | --- | --- |
| 运行 App | ZCode | 本会话运行时 |
| 会话 | `session_020c0f92aa87dfa62b7b08aeba6f4839` | 操作者 UI 记录（O038/zcode/service-event-01.json 等），本人工具侧读回核验 |
| 模型 | `account:bigmodel-start-plan/GLM-5.3` | 会话环境声明（本人实际可知者） |
| 思考等级 | 任务声明「最高」；本人无法在会话内 UI 回读，如实标注为任务下达值 | 任务下达第 2 行 |
| 权限 | 任务声明「完全访问」（用户级 AGENTS 记录 ZCode 默认 permission.mode=yolo）；本轮实际仅执行只读命令、纯计算与写入本报告一个文件 | 任务下达 + AGENTS 用户级 |
| 实际 taskID | 由操作者 UI 读回，本人不在报告内自造 | 任务要求 |
| 唯一写入 | 本文件（本方唯一允许写入路径） | 任务下达第 3 行 |

**输入完整性（本人实际执行，恰一次）**：附件 `/Users/kyle/.zcode/tmp/paste-attachments/2026-10-25/pasted-text-20261025-142416-64cd8067.txt` 全文读至 EOF；`wc -c` = **28993**、SHA256 = **b6241981cdf2bcf0cfd93be5202b99749e9f7b41f8276d2b17c38f936013a7c0`，与下达一致（O038/zcode/actual-delivered-payload.txt 同 28993B，操作者投递回读件在）。末尾用户原始清单自 marker「你现在是我的软件工程审查员。」（字节偏移 17738）至 EOF 恰 **11255 字节**（SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`），恰核一次，未改写、未重复引用。

**服务繁忙事件（两类证据如实区分，修订见 §12-1）**：
- 工具可见证据（本人会话内）：两次收到用户同任务续接指示（O038/zcode/same-task-service-continuation-01.txt、-02.txt 与会话内两条用户消息逐字对应，本人读回核验）。
- 操作者 UI 证据（本人工具侧读回并哈希核验）：两次 generic「当前系统繁忙，请切换模型、升级账户，或稍后再试。」原件 `O038/zcode/service-busy-original.ax.txt`（17358B，SHA256 `cf646c5692360df2f87a538239a9279dada900df9d83148cdd464f7fb9699696`，14:31，附 PNG）与 `service-busy-02.ax.txt`（25283B，SHA256 `376c1ca152cc7c77ce22958a638da732c8cb78fcfe7a55f2445f7bf3918573da`，14:36，附 PNG）；`service-event-01.json` 记录 `actual5HourQuotaExhaustionConfirmed:false`、`modelSwitched:false`、`quotaResetOrPurchase:false`；`service-recovery-observed.json`（14:34）记录同模型/思考/权限正常同任务续接且实际出现新工具命令；`quota-readonly-classification.json`（14:38）记录官方 Start Plan（ZCode 1024 Dev Day）GLM-5.3 余额显示 34%（68037289/200000000，10-26 09:00 过期）、`exhaustionConfirmed:false`、`genericBusyEvents:2`、无重置/购买/换模型/换供应商。
- 结论：**两次 generic 繁忙 → 同 SID 正常续接 01/02；无真实额度耗尽，无重置、付费、换模型**。原稿「中途一次」「未遇服务失败」表述不准确，已按上述事实修正。

**独立性（修订见 §12-3）**：本方独立性依据是**未读取 round-05 内任何另一方内容**——`round-05/minimax-m31flash.md`（84054B，14:47）存在且本方从未打开；两份繁忙原件中可见的文件名/大小亦未打开。本方首次列目录时 round-05 已存在（14:39，含一个子目录项），本方 `mkdir -p` 为幂等操作，**不能也不据此声称目录为本方创建或为空**；原稿「目录为本方写入前刚创建、内容为空」表述不成立，已撤回。R01–R04 历史双方报告仅作「同等披露的历史输入」全文/关键段读取，未沿用其结论；未把任何 ROOT 接收票当 R05 预判。

**本轮未做**：未改任何源/测试/配置/依赖/AGENTS/旧报告/状态文件；未 commit/push/PR/CI/merge/切分支；未跑 npm fullcheck/build/package/install/sync/HMR/GUI；未重跑任何 probe/测试制造新验证；未对旧失败 DB/profile 执行 SQL 或恢复；未重试 O022 被拒采集步骤；未动 /tmp 旧 probe；无真实额度/服务故障恢复动作（两次繁忙按上述证据为 generic 事件+正常续接）。

## 2. 冻结候选身份（本人独立复核）

| 项 | 下达值 | 实测 | 结论 |
| --- | --- | --- | --- |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | `pwd` 同 | 一致 |
| branch | `feature/weekly-t02-fr200-fr201` | 同 | 一致 |
| HEAD | `aff386f6b43cf60a847c9c9597265b0b1b477095` | `git rev-parse HEAD` 同 | 一致 |
| tree | `2d9b113b4b6ca25049c157c2b94fc79db42ef38d` | `git rev-parse HEAD^{tree}` 同 | 一致 |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 存在且为 merge-base（线性） | 一致 |
| 累计提交 / 差异叶 / tracked | 29 / 71 / 1355 | `git rev-list --count` 29；`git diff --name-only` 71；`git ls-files` 1355 | 一致 |
| base tree | — | `133357a5…`（记录用） | — |
| dirty | AGENTS.md 修改 + round-01/02/03 untracked | `git status --porcelain` 一致（用户政策覆盖与历史保护件，非本方改动） | 一致 |
| parent→head | 仅 CI 一文件 | `git diff --name-only HEAD~1..HEAD` = `.github/workflows/ci.yml` | 一致 |
| aff vs cb8 | 仅 12 证据 docs + 1 CI | O036 `changedSourcePathsFromCb8` 13 路径 + `allChangesOnly12EvidenceDocsPlus1CIPath:true`；业务源/测试/依赖同 | 一致 |
| 5 构建 / main | 5 构建；main 606471B / 4309328d… | O036/O037 `buildCurrent`/`currentMainSHA256` 同值；4/5 与旧包 byte-exact，main 仅差 24 字符开发 CSP nonce（O036 build-difference-qualification） | 一致 |

71 叶逐一归属：CI 1；主进程 3；preload 1；渲染 8；契约 6；引擎源 8；引擎新测试 7；vendor 7（4 wheel + patch + PROVENANCE + LICENSE）；scripts 1；licenses 1；pyproject/uv.lock 2；e2e+fixture+unit 15；docs 11（m0-checklist、status、94e20d4a 独审源、round-04 全套 8 件）。全部读差异或读关键全文（§3）。

## 3. 实际检查范围与方式（本人亲自 vs 读回既有真实运行 vs 未执行）

**本人亲自（只读/纯计算）**：71 叶 diff 逐类阅读（引擎 8 文件 diff 全读、mainline.py 1206 行全文、渲染 8 文件 diff 全读、契约三文件 diff 全读、CI patch 全读、vendor patch 头 40 行 + 哈希全验）；`digest`/`canonical` 与渲染端 `JSON.stringify`+TextEncoder 的字节等价推导（含 lone surrogate 前置拒绝与引擎侧 storage.py:494 重派生双防）；registry.json 文件字节 SHA256 重算 = binding-regressions 新 pin `5e097b7e…`；vendor 四 wheel + patch(5012B/de5755d6…)+repack(7112B/166b0919…)+LICENSE(1524B/53a705e5…) 哈希实测全对 PROVENANCE；uv.lock rdflib package 段 pin（path wheel + hash 99fab7bd…/size 2379774）核对；引擎 73 个新测试函数名与单测/e2e 标题及断言抽样；schema.json 5 个 ownership defs 与 registry 方法注册核对；29 提交清单逐一列出；三个核心文件行数 `wc -l` 实测（job_store.py 2993、storage.py 1887、e2e spec 1748）。

**读回既有真实运行（收据+原件，不当本人执行）**：O035 首败原件（ENTRY/COMPLETION：直接 npm 启动缺冻结 venv PATH → 1890 过/2 FAIL 均 `execFileSync python ENOENT`，17.463s，后继未跑，无重试）；O036（ROOT 明确授权一次环境纠正、原 argv `uv run --offline --frozen npm run check`、PID 35167、173.333s 自然 0、stdoutPin 2132d7a7…/stderr 空、执行时 HEAD=58c9+精确 CI dirty、提交后 1355 物理源桥接、无 shim/flags/PYTHONUTF8/第三次 check）；O037 + ROOT 票 64de5377…（六例逐例 7/7/7/7/22/7=57 真实事务、57 唯一 Job/operation、43 拒绝=42 INVALID_REQUEST+1 OWNERSHIP_CONFLICT、58 附件 base64 解码逐字节比对、57 笔 fullDiff=全量 Read+Job 原子 marker 绑定、fresh en-001/de-ch 四链 rev4–7、合法 add rev13/原 ID edit rev20、六独立 profile/App PID、实际 App PID/profile/appPath/argv+package.main+前后 main hash 入口绑定、builtHTML 模式、98 采样/33 known PID start、0/2/5 无已知残留、未 kill/删 profile、limits 明示不推广）；O032（CI36 三 job 步级事实、79F 分组、无 traceback、编码假设未确认、三份 job log pin）；O034（9 份已存在副本回执、新增找回 0、O022 整体仍不 sealed）；O038/zcode（本会话操作者 UI 证据包：start/权限/模型选择/工作目录/投递回读/14 份 progress/两次繁忙原件+PNG/两次续接/额度只读分类/原稿封签 integrity）；D8 决定单全文 + choice-A 原件（用户 verbatim、仅解除 T02 本功能 R4+ 限制、不放大预算/验证、四禁止）；R03 双方原稿结论与关键段、R04 双方原稿全文（zcode 492 行/66144B 链、minimax 646 行/78500B）、disposition 14 意见表、两份独立处置审计、evidence-only-bridge、artifact-manifest；package094 原运行边界（原 18=16+2 原条件 skip、三故障、named 24/24、text002 双过、engine/native/App exit UNKNOWN 边界）——按披露，不写成 aff 新包运行。

**未执行/未知**：Windows 任何诊断或测试；远端 push/新 CI（aff 无任何 CI 运行）；签名/公证/打包；npm 全量 check（本 head）；GUI（本人未启动）；SQL 于旧 DB；诊断步任何实跑结果。

**需求依据实读**：PRD 307–318（FR-200/201）、623、附录 C（959–981）、D（983–1014）、E（1016–1092）、F（1096–1112）、G（1115+）；M0 计划 S1 节（`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`：28–53 行交付/验收/两档规模/Q5 边界）；ADR-0001 全文；ADR-0002 全文（含 Round2/3 澄清）；AGENTS.md（系统投递现行版）；m0-checklist、status.md（58 入库时快照，非当前最新事实——按披露以 O032/O036/O037/ROOT 票为准）。

## 4. 全候选需求—实现—测试—打包/边界核查（本轮独立重核，非沿用 R04）

### 4.1 FR-200（业务概念管理）

表单/表格 CRUD：OntologyMainlinePage → OntologyPage 编辑器（中文名/英文标识 pattern `[A-Za-z0-9_][A-Za-z0-9_\-]*` 连字符已转义修复/同义词/示例五字段联动）+ e2e 四 kind（class/objectProperty/dataProperty/individual）create/edit/copy/delete 保完整 M/RDF 与兄弟记录；删除影响（`entityDeletionImpact`：精确引用事实阻断删除、保映射溯源与墓碑）有单测与 GUI 链。满足本迭代事实面；FR-200 全条款（类层级等其余构造）按 94e20d4a 独审源与附录 C 属后续迭代，不虚称。

### 4.2 FR-201（结构关系与实例事实创建）

- 两语义区分：结构关系（definitions 层）与实例事实（facts 层）分开编辑/存储（附录 C 行 971「结构定义与实例事实分开编辑」对应）；UI 不以单句自然语言混代替（表单按 S/P/O 显式三元组 + 完整事务 Diff 展示 + 实际 RDF 核对入口）。
- 事实原 ID 编辑：`edits={factId:object}`（storage.py:798–833：`_check_slot(..., manual_incoming=dict(old))`，ID 不变、映射基线保持）；ADR-0002 第 27 行逐点对应；e2e「keep original IDs, other literals」+ O037 rev20 原 ID 编辑链。
- 多值：`_check_slot` 仅拒单值谓词或同有效语句；不同值并存；`AMBIGUOUS_FACT_SUPPORT` 渲染端收紧（同槽存在 owner/受管/同值记录时拒绝编辑，与引擎所有权政策一致）。
- 新事实 ID：渲染端 `newManualFactPlan` = SHA-256(JSON([S,P,O])) UTF-8，与 Store `digest`（`ensure_ascii=False, sort_keys=True, separators=(",",":")`）对有效 Unicode 字节等价；lone surrogate 先拒（JS 会转义致哈希漂移）；引擎 `storage.py:494` 无条件重派生拒绝不匹配 ID（双防）。NFC/NFD 不归一（单测钉住）。
- 词法受控拒绝：vendored rdflib fr201.3 补丁在真实抛点类型化（`InvalidLanguageTagError`/`IntegerDigitLimitError`/`RelativeIRIBaseError`/`UnicodeCodePointError`/`UnterminatedStringError`/`MissingDatatypeError` → `Notation3InputError`）；`rdf_snapshot.term()` 收敛 `(BadSyntax, Notation3InputError)→TermInputError`，未知解析失败保持 ValueError/UNKNOWN/HOLD（D8 禁泛捕遵守）；`preview_changeset` 对 manual S/P 与 manual/edits 全部对象 `iri()/term()+parsed.n3()==value` 预检 → `INVALID_REQUEST(field=params)` 受控回滚。R03 唯一阻断（`"设备"@1`/`@zh1`/4301 位整数逃逸 HOLD）关闭链本人逐层复核成立。
- canonical 语言政策（口径修订见 §12-4）：**政策本身为既有**——base ADR-0002 第 27 行「对象必须等于 `term(value).n3()`、非规范别名拒绝提交」，choice-A 明确「保持既有 canonical 输入政策、不静默规范化」，本候选未改该政策。现行事实：`de-ch-1901`/`en-001` 正控四链过；`de-CH-1901` 语法合法（`_is_valid_langtag` 通过）但 n3 小写 → 按 canonical 政策受控 INVALID_REQUEST（`test_grammatical_uppercase_subtag_keeps_existing_canonical_rejection` 钉住），与 D8 第 13 行（语法域：不能一概拒绝数字结尾标签）不冲突、第 40 行（不静默 normalize）自洽。**「`de-CH-1901` 字面拼写不可提交」与 D8 第 13 行例证字面之间的张力作为语义边界观察保留（Z-06）**：当前候选不因此新增任何用户表态或合并前置；仅当未来要改变 canonical 政策（例如允许字面拼写提交）时，才需要用户显式决定并按新候选走门禁——本报告不替用户发起或预设该改变。

### 4.3 ownership 真实 witness 与可见定位（本轮重点）

引擎：`ManualOwnershipConflict`（kind=manual-ownership-conflict；reason ∈ reservedIdentity/sameStatement/singleSlot；existing=真实阻断行 locator{id,owner,sourceRow,slot}；incoming 显式 owner/source_row=None 不虚构）/`SingleDeclarationConflict`（真实前两条阻断记录 + 声明定位；同计划移除不再作签发者）。持久化 `_persist_ownership_detail`：字符估算→MAX_DOCUMENT 预算→proof 预付→指纹去重（旧候选逐段 base64/sha256 复核）→写入前后双 admission（`admissions()` core/full 两向量、`material_profile` 精确行/列字节增量、`project_admissions` rows/scan/decoded/plans）→REVISION_CONFLICT 基线复核。读侧 `ownership_detail_page` 两段式游标、逐段哈希/序号校验、262144 页/帧下限。契约：TS/Python 双 `matchesOwnershipDetail`（段级 SHA-256、序号/长度/nextOrdinal/complete 全等式；TS 手写 SHA-256 常数与实现核对，≤32KiB 段位长 <2^32 安全；Python base64 validate+hashlib）+ `reassembleOwnershipDetail`（信封 capture 预算→逐页校验→16MiB totalBytes 预分配→subtle SHA-256 全文档哈希→UTF-8 fatal 解码→schema→sourceBaseRevision 绑定）。渲染：`mainline-ownership.ts` ≤512 页循环逐页校验 + `OwnershipConflictDetailView` createElement 文本渲染（敌意 HTML 仅转义文本，单测 8 处 split 断言）、reading/unavailable/ready 三态、STALE_CONTEXT 围栏。GUI O037 的 1 笔 OWNERSHIP_CONFLICT + 43 拒绝 FullRead 不变 + 57 事务为运行侧证据（limits 明示仅 reservedIdentity family，不推广全部 family）。

### 4.4 写许可/预算/会话生命周期

`_WriteAdmission`（Store 实例+lease+format3 六重绑定、bootstrap 不确定 writer 不被收养、干净后继 16 条件）+ `JobStore._transaction` before_commit `check_final_material`（rowsPage/textPage 生产者预付 `_final_material_cost`、其余目的原时序、settlement_failed 永不退款）+ `material_profile`/`admit_terminal_growth`（pending jobs 4096/个终端余量）+ text/rows page 末编码器预付（`final prepaid` 先于有界搜索、`_RowsPrepaid` 本地消费、cursor 回调吊销先于末编码）。73 个新引擎测试逐一对应上述语义（admission/budget/rejection/succession 命名与实现吻合）。`project.ownership.detail` 注册全链（coordinator 白名单+ownership_proof 注入 → supervisor 方法白名单+projectId==selected → service 主进程覆盖 projectId+事后 owner/epoch/session 复核 → preload 业务命名方法）。渲染 preview 生命周期（useLayoutEffect 同步 detach、sequence 围栏、digest await 后 tuple 捕获）有 596 行单测。

### 4.5 CI 补丁（aff 唯一实现面改动）

`git diff 58c9..aff`：仅 ci.yml +10 行——Windows engine:check 步骤拆分为非 Windows 原命令 + Windows 诊断（env 打印 Python 版本/locale.getencoding/preferred/utf8_mode/devnull stream.encoding 一次 + `PYTEST_ADDOPTS='-vv --maxfail=1 --tb=short'`）。Quality/Mac 原命令、三 job、15/20 分钟 cap、依赖、runner 均不变；无新 job。本人判定：(a) 该补丁与其自我声明一致，属诊断配置，**静态可用**；(b) `--maxfail=1` 只在存在失败时早停——若 Windows 全绿则整套仍完整执行（语义等价全绿），但按操作者约束与本门禁口径，**即使未来该步绿也不得单独当完整 Windows 验收/合并许可**（-vv/tb=short 输出形态与首败即停的取证定位已改变该步性质；且 Windows 后续 typecheck/build/e2e/package 步仍依赖 engine:check 成功，取消链未动）；(c) **该配置当前零实跑**——aff 未 push，无任何新 CI 运行；本报告不把诊断静态可用说成已实跑。

### 4.6 供应链/许可

pyproject pin `rdflib==7.6.0+ontolearn.fr201.3` + `[tool.uv.sources]` path wheel；uv.lock `[[package]] rdflib` 段含该 wheel hash/size（回应 MM R04-02 误报，维持不删 .1/.2/upstream 审计件的处置）；NOTICE 索引本地修订、补丁路径、PROVENANCE、App/引擎双份许可位置与 setuptools vendored 全清单，并明示"非完整覆盖证书"；PROVENANCE lifecycle 明示 supplier 记录≠仓库采用状态。全部哈希本人重算一致（§3）。

### 4.7 打包/运行边界（如实，不越证据）

旧 package094 为 cb8 实现制品；aff 业务源与其 byte-equal（除 main 24 字符 dev CSP nonce，源码 `electron.vite.config.ts` randomBytes(18) + 非打包/devURL 条件可解释字节差异，不扩称已验分支）；O037 六例为 aff 构建入口绑定的真实 GUI（builtHTML、八环境缺席、不声称 nonce serve/HMR/CSP 分支实跑）。签名/公证/法律/跨 OS/参考设备/低端硬件/Q5/D2/累计容量/旧超限库恢复 HOLD 全部保留。远端口径：PR16 已存在（head 58c9、open 未合并）；aff 未 push、无新 CI；未 merge。

## 5. 旧意见逐项追踪（R03 → R04 → 本 R05 本人现状核）

| 旧意见 | 本候选现状（本人依据） | 判定 |
| --- | --- | --- |
| MM R03-01（High：数字语言标签/超长整数逃逸 HOLD） | §4.2 关闭链 + O037 八拒绝向量（new+真实原 ID edit，含 4301 位整数）+ 后继合法事务 | 已关闭（维持 R04 结论，依据为本轮独立重核） |
| Z-01 / MM R03-03（无 ORDER BY 行序） | storage.py:1226–1232 与 1147–1170 现状同；本人仍未构造同槽双冲突反例 | 未确认观察（非缺陷、不阻断；加固建议维持：ORDER BY id + 确定性回归） |
| Z-02（43692 witness 上限） | R04 已整项撤回；勘误链归档 | 已撤回（不恢复） |
| Z-03 / MM R03-04 / MM-05（definitions.triples wire 面） | 守卫仍仅 manual/edits；MM 审计证实后置 supported catch 不覆盖 transactions.preview/_definition 早期抛点 | OPEN 非阻断延期（T01，接线原始 triples/Agent 前处理；不能说已修） |
| Z-04 / MM R03-02（ownership 码映射 + 通用无定位冲突） | storage.py:57–64 无 "ownership" 键仍在；`_application` 拦 ownership 类 + 真实 witness 走新详情；非 witness 通用冲突仍旧三字段 detail（getter INVALID_STATE→UI「详情暂不可用」设计内降级） | OPEN 非阻断延期（T01 合同 + T02 消费） |
| Z-05（渲染白名单 17 vs 契约 26，缺 16 码） | mainline-session.ts message() 白名单 +OWNERSHIP_CONFLICT 后仍缺 16（CURSOR_EXPIRED…VERSION_INCOMPATIBLE，本人 R04 重算维持） | OPEN 非阻断延期（接线时同步 + 白名单⊇可产生码集测试） |
| Z-06（de-CH-1901 字面拼写语义） | §4.2：政策为既有 base ADR-0002 第 27 行且 choice-A 明确保留；张力作为语义边界观察保留；**当前候选不新增用户表态前置**；仅未来改变政策时才需用户显式决定（新候选门禁） | 语义边界观察（非缺陷、不阻断、不设新门禁、不代答） |
| Z-07（文件增长） | `wc -l` 实测：job_store.py 2993 行、storage.py 1887 行、e2e spec 1748 行（base→head diff 新增行 +406/+114/+1748 为差异口径，不与总行数混同） | 信息级建议维持 |
| M-01（状态文档缺口） | 58c9bbb3 已建 status.md + m0-checklist 引用（M-01 唯一落实项）；status.md 内容为 58 时点快照，未反映 aff/CI36/远端现状（披露 #8 已明示，属已知时点差，非造假） | 已落实；快照时效由 ROOT 收口时更新 |
| M-02（wheel 无 hash/删除建议） | uv.lock 258 行 hash 实测在；本地 STORED vs 上游 DEFLATED；不删审计件 | 不采（维持处置） |
| M-03（4299/4300 边界回归） | 引擎测试仍仅 4301 断言；4301 有 GUI/stdio 证据 | 未来覆盖建议延期（T01） |
| M-04（standalone EOF OPEN） | 8 例恰 EOF IndexError 未分类维持 | OPEN（不泛捕，接线前类型化） |
| M-06（schema hash 形状） | 引擎 494 权威校验 + 双端金向量测试在 | 不作为当前漏洞 |
| M-07（桶导出） | 维持不改导出面 | 低优先维护建议 |
| R03 其余（容量/Q5/D2、Undo、native/named exit UNKNOWN、text001 首败等） | 全部按原 HOLD/保留 | 不变 |

## 6. 本轮证据链核查结论

O035→O036 首败保留+一次授权纠正链完整、无第三次 check、无 shim/flags；O036→aff 桥接（1355 物理源 bytes/mode 相等）成立；O037 与 ROOT 票 64de5377… 数值互相咬合（57/57/43/58/rev13/rev20/四链/PID/102625.483ms/39319）；O032 三 job 步级事实与日志 pin 在（246025/65720/99951B）；O034 仅副本回执、O022 整体不 sealed；O038/zcode 本会话证据包（含原稿封签 36956B/24c87595… 与本人文件逐字节同）自洽；D8 choice-A 授权范围与四禁止未被任何后续动作突破（本轮 CI 补丁不改 cap、不静默 normalize、不泛捕、不按文案分类）；远端事实（PR16 open/develop 583/CI36 在 58c9/aff 未 push）与 O032+票一致（本人未执行远端命令，采信 O032+票）。未发现证据互相矛盾或伪造迹象。

## 7. 本轮问题清单（按严重度；不足 10 不凑数）

### P-1【中·阻断合并（门禁级，非已证产品缺陷）】Windows 79F 根因未关闭，三 OS 门禁不可判绿
- 事实：CI36（跑在 58c9；aff 无新 CI）Windows 取消前 79 F（6+72+1 分组）无 traceback/总表；编码假设未确认；aff 诊断补丁未实跑。
- 因果/风险：若为真实 Windows 特有缺陷（如 trace 默认编码写失败），则同一测试面在 Windows 上不可用；若为环境差异，也须证据关闭。在取证→修复（如需）→全绿前，PR16 无法合并，整候选卡在现有门禁。
- 位置：`.github/workflows/ci.yml`（诊断步）；失败源于 `test_mainline_language/manual_input_rejection/read_work_budget`（Windows 侧表现）。
- 阻断：**是（对整候选合并）**；对本地 mac 同版证据不构成反驳。

### P-2【中·阻断合并（门禁级）】Quality job 取消未复绿
- 事实：CI36 Quality 进程打印 passed/runtime exit 0 但 step cancelled、packaged recovery skipped（O032）。
- 风险：打包恢复验收缺位；合并前须有一轮真实全绿（不限于是次 infra 取消的归因）。
- 阻断：**是（合并前必须绿）**；非代码缺陷。

### P-3【低·延续 OPEN】definitions.triples wire 面（同 Z-03）：见 §5。阻断：否。
### P-4【低·延续 OPEN】ownership 码映射与通用无定位合同（同 Z-04）：见 §5。阻断：否。
### P-5【低·延续 OPEN】渲染错误码白名单缺 16 码（同 Z-05）：见 §5。阻断：否。
### P-6【语义边界观察·非缺陷·不设新门禁】de-CH-1901 字面拼写与 canonical 政策的张力（同 Z-06）：政策为既有（base ADR-0002 第 27 行）且 choice-A 明确保留；本候选行为与政策一致；仅当未来改变该政策时才需用户显式决定并走新候选门禁，本报告不替用户发起。阻断：否。
### P-7【信息】诊断步 PYTEST_ADDOPTS 未来若转常规须移除/收窄，避免诊断输出长期混入验收命令；核心文件行数（wc 实测 job_store.py 2993、storage.py 1887、e2e spec 1748；diff 新增 +406/+114/+1748 为差异口径）持续增长（同 Z-07）。阻断：否。
### P-8【信息】status.md 为 58 时点快照，与 aff/远端现状有时差（披露已知）；ROOT 收口时更新即可，不擅自改冻结状态文件。阻断：否。

本轮**未发现新的阻断级/高危代码缺陷**；无机械凑数项。

## 8. 无法确认项与独立 HOLD（不因附条件通过解除）

无法确认：本 head 全树依赖漏洞扫描（无 OSV/mimosa 新记录；rdflib 供应链人工核到字节级）；Windows 全套行为（P-1 根因；aff 诊断配置零实跑）；5×10⁶ 行级索引/分页（实测上限 243 行/80545B/56KB 文本 5 页 + 420002B 历史字面量三份滞留预算静态核）；迁移回滚演练（format2→3 前向+lease 在）；全流程键盘+读屏与 RTL；生产 CSP 渲染链 GUI 复验（builtHTML 证据边界）；README 新人 1 小时上手。HOLD（延续）：unknown parser/N3/Store/坏快照/损坏 SQLite 物理保护；standalone EOF 8 例；native engine exit UNKNOWN、named App exit UNKNOWN（PID 缺席≠自然 0/全后代回收）；签名/公证/wholeAPP 法律/_distutils；跨 OS/参考设备/低端硬件；Q5/D2 累计容量与旧超限库恢复；FR-201 仅 reservedIdentity family 有本轮 GUI；FullRead 相等≠物理 DB 零写；mergedUsableFRs 2/17；**PR16 已存在（58c9 head、open 未合并）、aff 未 push、无新 CI、未 merge**。

## 9. 用户 11255 字节原始清单逐项适用性（1–160 每项独立一行；口径同产品形态：本地优先单用户 Electron+Python 桌面，无账户/云/支付/网络服务；判定=适用（达标/未达标）·不适用·无法确认，依据限本人本轮实际核验面）

| # | 项（缩写） | 判定 | 依据/不足 |
| --- | --- | --- | --- |
| 1 | 有人设计的 schema | 适用·达标 | contracts JSON Schema+zod 双端 141 defs、registry/fixtures/binding-regressions（registryHash 本人重算同步）、SQLite 版本化 |
| 2 | 邮箱带+号登录 | 不适用 | 本地单用户无账户/登录 |
| 3 | 密码重置链接过期且一次性 | 不适用 | 无登录/邮件 |
| 4 | MFA+丢失手机恢复 | 不适用 | — |
| 5 | 会话超时/一键终止 | 不适用（账户语义）；引擎/窗口生命周期属 I02 已验面 | 无账户会话 |
| 6 | SSO | 不适用 | 无企业客户面 |
| 7 | SAML | 不适用 | — |
| 8 | SCIM | 不适用 | — |
| 9 | 深于 admin 的角色权限 | 适用·达标（本范围） | permission(library.create/write/read)、ownership proof 六重绑定、admission/writer 分离、IPC 白名单 |
| 10 | 改一个数字读他人数据 | 适用·达标（已核路径） | 主进程强制覆盖 projectId、selected/generation、detailRef origin+fingerprint；无通用 invoke |
| 11 | 租户隔离 | 不适用（无多租户）；项目级隔离达标 | 同 #10 |
| 12 | 管理员代登录 | 不适用 | 无支持面 |
| 13 | 登录限速 | 不适用 | 无登录 |
| 14 | 锁定不误伤 CFO | 不适用 | — |
| 15 | 迁移前进/回滚 | 部分适用 | format2→3 前向+迁移写锁+失败回滚在（ADR-0002）；回滚演练未见→回滚侧无法确认 |
| 16 | 迁移不锁主表 | 适用·达标（本地语义） | 嵌入式单写者、启动期迁移，无高峰并发面 |
| 17 | 索引撑 500 万行 | 部分适用·无法确认（大规模） | 实测 243 行/80545B/56KB 文本 5 页；更大受控 RESOURCE_LIMIT；500 万行为未测 |
| 18 | 连接池 | 不适用 | 嵌入式单连接 |
| 19 | 每夜备份 | 不适用（本地数据主权） | backup(newPath) 在线备份 API 在；无自动夜间任务需求（M0 边界） |
| 20 | 恢复演练 | 无法确认 | 旧 DB 禁打开，无 restore 演练证据 |
| 21 | PITR | 不适用 | 无运维删库场景 |
| 22 | 软删除 | 适用·达标 | 受管事实墓碑、保留初始 ID、历史/已提交轮次不可改写 |
| 23 | 服务端（引擎）校验 | 适用·达标（含披露缺口） | canonical/词法/四族冲突/受控码全在；definitions.triples 面 OPEN（P-3） |
| 24 | 时区存储 | 部分适用·达标（存储口径） | 安全整数/UTC；无提醒调度面 |
| 25 | 撇号姓氏 | 适用·达标（词法面） | UTF-8 全链、中文字面量实测；Turtle 词法受控；无 SQL 拼接 |
| 26 | emoji/重音/RTL | 部分达标 | 56309 Unicode scalars/56314 UTF-8B 实测；RTL 专项未测→无法确认（RTL） |
| 27 | 金额存整数 | 不适用 | 无金额 |
| 28 | 币种/舍入/税 | 不适用 | — |
| 29 | 抗第二客户变更 | 部分适用·达标（P0 边界内） | 版本化契约+不可变快照+canonical 身份；附录 C 前言要求任何扩展重评 |
| 30 | 幂等键 | 适用·达标 | operationId/operation_claims 同操作同内容返回原结果；example 重放闭环实测 |
| 31 | 四次点击去重 | 适用·达标 | 43 拒绝 FullRead 不变；preview 生命周期围栏 |
| 32 | 第 400 页分页 | 适用·达标（已测范围） | 游标校验+页/帧预算；更大受控拒绝（#17） |
| 33 | 导出表格 | 不适用（现阶段） | FR-203 Turtle 导出属后续能力，不虚称 |
| 34 | 2009 年 CSV 导入 | 不适用 | FR-300 映射后续 |
| 35 | 留存规则删除 | 不适用 | 本地用户数据，无合同删除义务 |
| 36 | 密钥不入代码/仓库/chat | 适用·达标 | 本轮 71 叶 diff 无凭据；引擎无密钥；S3 网关未接线 |
| 37 | 轮换 AI 粘贴的密钥 | 不适用 | 未发现任何已入库密钥 |
| 38 | 确认安装包是所要的 | 适用·达标 | vendored 四 wheel/patch/repack/LICENSE 哈希本人全验=PROVENANCE；uv.lock path+hash pin；NOTICE 索引 |
| 39 | 依赖扫描 | 部分适用·无法确认（全树） | 本 head 无新自动扫描记录；rdflib 补丁人工审读达标 |
| 40 | 输入消毒 | 适用·达标（含披露缺口） | 受控拒绝族（词法/语言标签/整数/IRI）；P-3 面如实登记 |
| 41 | SQLi/XSS/CSRF/OWASP | 适用·达标（已读面） | SQL 全参数化+标识符双写转义；createElement 文本渲染；CSP 单源两变体；无 HTTP→CSRF 面不适用 |
| 42 | 上传扫描/限大小/不可执行 | 适用（等价面）·达标 | 示例资源 O_NOFOLLOW/O_NONBLOCK/仅常规文件/大小限/前后 fstat |
| 43 | CORS | 不适用 | 无 HTTP 服务 |
| 44 | 每响应安全头 | 部分适用·达标 | csp.ts 唯一源 meta/header 两变体；无服务器响应头概念 |
| 45 | 静态/传输加密 | 不适用（本地单机 M0） | 边界披露 |
| 46 | 最小权限（含 AI agent） | 适用·达标 | preload 业务命名桥、Agent 只草稿+人工确认、admission/proof 边界 |
| 47 | 日志谁做了什么无敏感 | 适用·达标 | origin(hostClientId/engineSessionId)、固定错误码、无堆栈/路径/原值跨边界 |
| 48 | 渗透测试 | 不适用（现阶段） | 未执行、未虚称 |
| 49 | 安全问卷 | 不适用 | 无企业买家 |
| 50 | 漏洞披露流程 | 不适用 | — |
| 51 | 盗笔预案 | 不适用 | 本地无凭据/生产访问；磁盘加密属用户系统策略 |
| 52 | SOC 2 | 不适用 | — |
| 53 | HIPAA | 不适用 | 无患者数据 |
| 54 | BAA | 不适用 | — |
| 55 | 查看审计 | 部分适用 | 变更审计完整（不可变操作/快照/receipt）；本地单用户无"查看"审计需求→主体不适用 |
| 56 | PCI | 不适用 | 无支付 |
| 57 | GDPR 删除触达每表 | 不适用 | 无云个人数据 |
| 58 | 数据驻留 | 不适用 | 本地优先 |
| 59 | 季度访问审查 | 不适用 | 单用户 |
| 60 | dev/staging/prod 一致 | 不适用（部署语义）；源-包一致性已验 | cb8→aff 1355 物理源桥接+912 包成员收据 |
| 61 | IaC | 不适用 | 无基础设施 |
| 62 | 部署管线先跑测试 | 部分适用·当前未达标（进行中） | CI 门禁在册、CI36 macOS 绿；但 Quality/Windows 取消、79F 未闭（P-1/P-2）；本地同版 check 自然 0（O036） |
| 63 | 一键回滚 | 不适用 | 无部署 |
| 64 | 零停机部署 | 不适用 | — |
| 65 | 特性开关 | 不适用 | registry 能力注册即面；无运行时 flag 需求 |
| 66 | 自动扩缩 | 不适用 | — |
| 67 | CDN | 不适用 | — |
| 68 | DNS/SSL 续期 | 不适用 | — |
| 69 | 后台任务不冻结页面 | 适用·达标（已测面） | Job 队列/恢复/57 事务；旧三故障注入（cb8 包） |
| 70 | 带退避重试 | 部分适用 | retryable 语义在；退避策略未断言 |
| 71 | 死信队列 | 适用（等价物）·达标 | 失败 Job 终态保留可查、不与成功混排 |
| 72 | cron 不双跑 | 不适用 | 无多服务器 |
| 73 | 缓存与失效 | 适用·达标（架构面） | invalidation-v2.json 唯一源；本轮未重跑失效用例 |
| 74 | SPF/DKIM/DMARC | 不适用 | 无邮件发送 |
| 75 | 退信/投诉处理 | 不适用 | — |
| 76 | 存储清理规则 | 不适用 | 本地文件用户主权；collect_cache/pin 回收语义在 |
| 77 | 成本告警 | 不适用 | 无云成本；模型网关未接线 |
| 78 | DR 计划 | 不适用 | 本地优先单机无多区域运维面 |
| 79 | 第二区域 | 不适用 | — |
| 80 | 3am 可搜结构化日志 | 部分适用·达标（存在面）；检索工具无法确认 | 逐例结构化 report.json/trace 归档+哈希；集中检索工具未建设 |
| 81 | 错误聚合 | 不适用（运营上报系统）；本地逐例 trace 在 | — |
| 82 | 外部 uptime 检查 | 不适用 | — |
| 83 | 告警呼叫人类 | 不适用 | — |
| 84 | 延迟/错误率/吞吐仪表盘 | 不适用 | — |
| 85 | 跨服务追踪 | 不适用（多服务）；request/Job/origin 绑定为单服务等价物 | — |
| 86 | on-call 轮值 | 不适用 | — |
| 87 | runbook | 不适用（值班语义）；AGENTS/docs 流程文档在但非 runbook | — |
| 88 | postmortem 改变什么 | 适用·达标 | 失败链留痕→D8 熔断→choice-A 实际改变流程；勘误/处置机制在运转 |
| 89 | 状态页 | 不适用 | — |
| 90 | 懂逻辑者写的单测 | 适用·达标（mac 侧）；Windows 侧未闭 | O036 1892 TS+3719 Py 自然 0；73 新引擎测试断言语义/哈希/wire；CI36 Windows 79F（P-1） |
| 91 | 三方 API 集成测试 | 不适用 | 无第三方 API；唯一依赖 vendored+172/158 回归 |
| 92 | 赚钱流 e2e | 不适用（无金钱流）；CRUD/冲突 e2e 等价达标 | aff main 六例 6/6（O037） |
| 93 | 上线前负载测试 | 部分适用·无法确认 | 预算/容量受控测试在；性能负载未测（Q5/D2 无通过线） |
| 94 | 类生产非生产测试数据 | 适用·达标 | 固定 fixture/合成孪生独立命名空间，无生产数据入库 |
| 95 | 修 bug 不复活旧 bug | 适用·达标 | binding-regressions、R03 拒绝向量回归、旧 PASS 不迁移；registryHash 同步 |
| 96 | 五年前笔记本 | 无法确认 | 参考设备/低端硬件 HOLD |
| 97 | 可访问性合规 | 部分达标·无法确认（全面性） | 新视图 aria-label/role=alert/status；全流程键盘+读屏未验 |
| 98 | 订阅/升降级/按比例 | 不适用 | 无计费 |
| 99 | 催付重试/催缴邮件 | 不适用 | — |
| 100 | 发票带 PO | 不适用 | — |
| 101 | 销售税/VAT | 不适用 | — |
| 102 | 退款/部分退款 | 不适用 | — |
| 103 | 计量与账单一致 | 不适用 | — |
| 104 | 年度定制合同 | 不适用 | — |
| 105 | 财务对账报表 | 不适用 | — |
| 106 | webhook 验签 | 不适用 | 无 webhook |
| 107 | webhook 重试/日志 | 不适用 | — |
| 108 | 版本化 API | 适用·达标 | protocolVersion 2/3、schema $id/registry 版本化、旧版本并行校验 |
| 109 | 用户建撤 API key | 不适用 | 无公开 API |
| 110 | API 限速 | 不适用；等价物帧/页/预算/队列限制在场 | — |
| 111 | 三方 API 变格式预案 | 不适用 | 唯一依赖 vendored 固定（优于预案） |
| 112 | OAuth 刷新 | 不适用 | — |
| 113 | 客户集成沙箱 | 不适用 | — |
| 114 | 提示注入防护 | 不适用（现阶段；S3 未接线） | 架构已定 Agent 白名单+人工确认+网关唯一主进程 |
| 115 | 客户/患者数据不出网 | 不适用（现阶段） | 同上 |
| 116 | 模型花费上限 | 不适用（未接线） | — |
| 117 | evals | 不适用（现阶段） | — |
| 118 | 模型降级 fallback | 不适用（未接线） | — |
| 119 | 模型弃用迁移预案 | 不适用（现阶段） | — |
| 120 | 提示/输出日志（合法保留） | 不适用（现阶段） | 附录 F 最小调用记录不含业务正文的设计已定 |
| 121 | AI 不可撤销动作人工批准 | 适用·达标（架构） | Agent 只草稿、不得自动确认（AGENTS 不变量+预览/确认流） |
| 122 | 酒店 wifi 加载 | 不适用 | 本地应用 |
| 123 | 空/加载/错误态 | 适用·达标 | reading/unavailable/ready 三态+role=status/alert（本轮实读） |
| 124 | 可行动错误信息 | 适用·达标 | OWNERSHIP_CONFLICT 中文行动提示+定位视图；固定码 |
| 125 | 表单失败保留输入 | 适用·达标 | 「已输入内容保留」；8 拒绝向量 toHaveValue 冻结 |
| 126 | 邮件客户端渲染 | 不适用 | 无邮件 |
| 127 | 可关通知 | 不适用 | 无通知系统 |
| 128 | undo | 适用·达标（引擎面）；GUI Undo 面 HOLD | undo-impact 预览/暂停语义+测试 |
| 129 | 键盘导航+读屏 | 部分达标·无法确认 | 同 #97 |
| 130 | 翻译/本地化格式 | 不适用 | 中文单语；无日期数字本地化面 |
| 131 | 后退按钮符合预期 | 不适用 | 桌面工作台；窗口恢复属 I02 |
| 132 | 人能读的代码 | 适用·达标 | 本轮实读核心；意图注释密度高 |
| 133 | 每次变更 code review | 适用·达标 | 同版双指定模型审查在执行（本轮 R05） |
| 134 | 分支策略 | 适用·达标 | worktree+feature+base SHA+PR 回并（本 worktree 实证） |
| 135 | 月度依赖升级 | 无法确认 | 未建立月度节奏文档 |
| 136 | 框架 EOL 前升级 | 无法确认 | Electron/React 升级策略未文档化 |
| 137 | 删除 AI 死代码 | 适用·达标 | 本轮 diff 无死代码/调试残留；.1/.2/upstream 为审计证据保留（维持处置） |
| 138 | 拆 2000 行文件 | 适用·未达标（信息级） | job_store.py 2993 行（wc 实测）等（P-7） |
| 139 | 架构决定写理由 | 适用·达标 | ADR-0001/0002、M0 计划、迭代/评审体系 |
| 140 | README 1 小时上手 | 无法确认 | 未做新人实验 |
| 141 | 交接文档 | 适用·达标 | docs 树+每轮留痕+唯一状态源 m0-checklist/status.md |
| 142 | 运维 admin 面板 | 不适用 | — |
| 143 | 客服支持工具 | 不适用 | — |
| 144 | 客户可读 changelog | 不适用 | 无外部客户 |
| 145 | 条款/隐私与代码一致 | 不适用（未发布）；本地优先行为与 PRD 一致 | — |
| 146 | 资产归公司名下 | 不适用 | 个人项目现阶段 |
| 147 | bus factor>1 | 部分适用 | 双模型评审+总控留痕降低单点；创始人单人边界如实 |
| 148 | senior 读每行 AI 代码（人） | 不适用（现阶段组织角色）；双模型逐文件审查+ROOT 重哈希部分替代 | 不虚称已满足 |
| 149 | 后端工程师先建模（人） | 部分适用·达标 | 附录 C 主定义+ADR-0002 数据层次先于实现；Q6 能力冻结仍开放 |
| 150 | 解释 AI 修复副作用（人） | 不适用（组织角色）；本轮无此类事件 | R02→R04 修复链每步带独立审查 |
| 151 | DevOps 管部署/云账单（人） | 不适用 | 无服务器/云账单；CI/打包由总控承担 |
| 152 | 3am 值班（人） | 不适用 | — |
| 153 | 漏洞公开周补框架（人） | 部分适用·无法确认 | 依赖维护仅个案（global-agent/rdflib）；升级节奏未文档化（同 #136） |
| 154 | 陪审计走患者数据（人） | 不适用 | 无 HIPAA/审计场景 |
| 155 | QA 验 AI 所称测试（人） | 适用·达标 | 同版双指定模型独立审查+ROOT 重哈希/逐笔核验即此机制（本轮亦执行） |
| 156 | 在线库迁移不掉行（人） | 部分适用·无法确认 | 迁移 lease/回滚语义+测试在；无真实用户库在线迁移演练 |
| 157 | tech lead 拒绝破坏性功能（人） | 适用·达标 | 能力矩阵"扩展须重评"、AGENTS 不代答 Q2/Q3/Q5-9、D8 熔断实践 |
| 158 | architect 规模化（人） | 不适用（现阶段单机）；Q5 容量 HOLD 为对应风险登记 | — |
| 159 | AI 调不动时人来 debug（人） | 不适用（组织角色）；R02→R04 缺陷定位链显示流程可完成 | — |
| 160 | 一年后记得为什么（人） | 适用·达标 | ADR/评审留痕/m0-checklist/状态文件体系即为此设计 |

## 10. 最终结论、条件与下一最小动作

**结论：ConditionalPass（附条件通过）。** 本迭代授权范围的 FR-200/FR-201 候选实现与其共享闭包，在 aff386f6（tree 2d9b113b）本地同版静态+运行证据上达标；诊断配置自身静态可达目的（未实跑，aff 无新 CI）；但**整个候选在现有远端门禁下不可判通过**——Windows 79F 根因未关闭与 Quality 取消是合并阻断（P-1/P-2），且全部既有 OPEN/HOLD 未解除。不预设 ROOT 会接收任何条件。

**条件（合并前，依既有原标准，非本报告新设）**：
1. push aff → 新 CI 实跑：Windows engine:check 诊断步产出真实首败 traceback/环境事实；据此定根因——若需改代码/测试/配置则生成新候选并重走门禁；最终三 job（Quality/macOS/Windows）在原 15/20 分钟 cap 内全绿（诊断参数不得用于宣称完整 Windows 验收，须恢复或明示等价全量语义）。【阻断】
2. Quality 全绿含 packaged recovery 步真实执行。【阻断】
3. 既有 OPEN 按 D8/R04 分工处理（definitions.triples wire、ownership 通用定位合同、白名单、4299/4300 回归）。canonical 语言政策维持 base ADR-0002 第 27 行不变（choice-A 明确保留）；**本报告不为当前候选新增任何用户表态或政策前置**——仅当未来要改变该政策时，才需用户显式决定并走新候选门禁。【非阻断，接线/收口前】
4. 签名/公证/法律/跨 OS/参考设备/Q5/D2/容量/旧库恢复等 HOLD 按原归属保留，不得以本附条件通过冲抵。【非阻断，发布前】

**下一最小动作**：由 ROOT 授权 push aff386f6（或按现行流程由负责会话执行）触发 PR16 新 CI，先取 Windows 首败事实，再决定是否新候选修复；期间不动冻结候选、不预写结论。

## 11. 自然终态声明

本报告为唯一写入文件（原稿已由操作者封存于 O038，修订仅落本文件）；报告绝对路径/bytes/行数/SHA 由本人写后实测回显于会话终态（操作者 UI 另行读回实际 taskID/模型/思考/权限）。本轮服务事件如实记录：两次 generic「当前系统繁忙」→ 同 SID（session_020c0f92…）正常同任务续接 01/02，无真实额度耗尽、无重置/付费/换模型（O038/zcode 原件+JSON，本人哈希核验）。整个候选结论与阻断项见 §0/§10；未把诊断配置静态可用说成已实跑，未把旧包运行写成 aff 运行，未读对方 R05（round-05/minimax-m31flash.md 存在且未打开），未重试被拒步骤，未预设改判（结论维持 ConditionalPass）。

## 12. 事实复核与原交付补齐记录（修订稿新增；原稿 36956B/259 行/SHA 24c87595… 逐字封存于 O038/zcode/report-original.md，本人哈希复核一致）

1. **服务繁忙事件口径（修订 §1/§3/§11）**：原稿「中途一次系统繁忙」「未遇服务失败」不准确。实据（本人工具侧读回+哈希）：两份 generic 原件（service-busy-original.ax.txt 17358B/cf646c56…、service-busy-02.ax.txt 25283B/376c1ca1…，各附 PNG）+ service-event-01.json（exhaustionConfirmed:false/modelSwitched:false/quotaResetOrPurchase:false）+ service-recovery-observed.json（同模型同任务正常续接、实际新工具命令）+ quota-readonly-classification.json（官方余额 34%、genericBusyEvents:2、无重置/购买/换模型）+ 两条同任务续接原件与会话内用户消息逐字对应。工具可见（用户续接指示）与操作者 UI 证据（原件/JSON/SID）已分别标注；两者现在均为本人工具侧核验过的事实。**采纳**。
2. **行数口径（修订 §5/§7）**：原稿「job_store.py ~3399 行、storage.py ~1900 行（本候选再+406/+0/+114）」错误且混合口径。`wc -l` 实测：job_store.py **2993**、storage.py **1887**、e2e spec **1748**；base→head diff 新增行 +406（job_store）/+114（storage）/+1748（e2e，新文件）是差异统计口径，不得与总行数混同。**采纳**。
3. **round-05 目录表述（修订 §1）**：原稿「目录为本方写入前刚创建、内容为空」不成立——本方首次列目录（14:39）时 round-05 已存在且含一个子目录项；`mkdir -p` 为幂等操作不能证明创建，未读对方内容也不能推出目录为空。现口径：独立性唯一依据=未读取对方任何内容（round-05/minimax-m31flash.md 84054B 存在且未打开）。**采纳**。
4. **canonical/用户表态口径（修订 §4.2/§5/§7/§10）**：原稿在条件 3 列「Z-06 语义边界取得用户显式表态」并为 P-6 写「待用户表态」。政策事实：base ADR-0002 第 27 行已有 canonical 政策、choice-A 明确「保持既有 canonical 输入政策」，本候选行为与之一致；故当前候选**不需要新的用户决定，本报告不为其设新门禁**。修订为：张力作为语义边界观察保留（语法合法 vs canonical 拒绝的事实不变）；仅当未来要改变该政策时才需用户显式决定并走新候选门禁。**采纳**。
5. **160 项逐项展开（重写 §9）**：原稿将 2–8、78–89、98–107、126–127、148–160 等多项合并行。现 §9 为 1–160 每项独立一行、各自判定与依据/不足（78–89 与 148–160 中各项适用性确有差异，如 80/85/88 达标或部分、81–87/89 不适用；148–160 中 149/155/156/157/160 部分适用或达标、余不适用）。纯文档补齐，未因清单新做功能或运行。**采纳**。
6. **远端口径（修订 §0/§8/§10）**：原稿多处「未 push/PR/CI/merge」易误读为无 PR。精确事实：**PR16 已存在**（open、未合并、head 58c9）；CI36 跑在 58c9（实际 PR checkout 为合成 681ffbd0…，run.head_sha≠实际检出）；**aff 未 push、无任何新 CI**；未 merge。§4.5 已强调诊断配置静态可用但零实跑。**采纳**。

以上六项均为事实准确性修订；不改变 §0 两层结论、P-1/P-2 阻断属性、ConditionalPass 总判定及全部技术判断依据。
