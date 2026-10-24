已全文读取并核对报告原针：95365B／683行／SHA256 `82d112e961392a161fcb57bfe857d8c531502cd135d286db15243e10052bc71f`。重点源码与固定 fde source-map 匹配。未发现需据本报告立即新增的内部演示阻断；多项确是未修复限制，但部分后果、建议及“新增发现”表述须收窄。MiniMax 自己的 **PASS／正式 HOLD** 原判定保持，不由本核查改写。

**§4／Top1 的重点结论**

责任保留链成立：未消费的原 delivery 留有原 token，重复回复的新 ACK 只删除新 token，不能释放原载荷；selection/dispose 也不代替原 ACK。对应 [service](/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions/apps/desktop/src/main/project-mainline-service.ts:637)、[receiver](/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions/apps/desktop/src/main/engine.ts:945)。

但须更正：

1. **并非本轮首次发现**。旧 pair002 处置第50行已明确登记“重复回复 ACK 不能替原 ACK、旧 token 及 full 槽继续保留”。
2. **ACK 丢失不等于 renderer pending 必留**。[preload](/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions/apps/desktop/src/preload/index.ts:26) 捕获 ACK 失败后仍返回业务 payload；controller `accept()` 成功会清除 pending。只有业务回复未被接受等额外条件，才保留取回按钮。
3. 旧 token 永不消费是条件，不是每次重复调用的必然事实；迟到原 ACK 若仍满足身份与会话条件仍可处理。
4. “receipt 不可达／窗口已销毁／delivery 不在集合”**不能推出原 aliases 和责任已结束**，不足授权释放。§4.4 第2建议不能直接采用。
5. 两个 delivery 上限和 owner uncertain 可能更早拒绝操作，不能宣称 UI 可无额外前提连续完成16次取回。容量限制真实，但固定累计路径未被本轮运行证明。

Top10 逐项意见：

| 项 | 核对结论与最小动作 | 内部演示阻断 |
|---|---|---|
| 1 重复回复/fullIntents | **采纳条件机制，保留 M3；不采纳无证退休建议。**可补充容量文案和精确产品路径覆盖；不得 FIFO、代 ACK、退款或改错误目录求绿。 | 不新增；保留容量边界 |
| 2 uncertain 单向闩锁 | **采纳既有 M1。**影响该主链 owner，不等于 health／全部应用永久不可用。只读也可能涉及新授权和材料责任，不能简单放行或按操作 UUID清闩锁。未来 resolution 需真实原操作证明。 | 已接受限制，未修复 |
| 3 跨会话创建回执 | **采纳 M2 的创建/示例限定范围。**新 origin 不等导致拒绝属现行创建合同；不能把 session 降成纯审计字段或只用稳定请求摘要替代原 dispatch 证明。Job/marker 对账不是全局失效。 | 已接受限制，未修复 |
| 4 未ACK两个16槽 | **采纳。**两容器独立、不相加；未知责任不凭时间、导航或新会话消失。所谓“有界回收”必须先证明具体责任结束，当前没有该证明。 | 已接受 M3，未修复 |
| 5 未签名目录包 | **采纳正式发布欠项。**当前内部未签名目录包范围明确；签名、公证、安装器仍 HOLD。 | 否；对正式分发阻断 |
| 6 用户备份/恢复 | **采纳入口及验收缺口。**迁移备份存在，不等于用户恢复演练；FR002/203 缺口保持，不能因此说现有库必定不可恢复。物理损坏 HOLD 不解除。 | 本轮范围限制；正式欠项 |
| 7 records＋prepare锁 | **两项均采纳，须分域。**records 是产品运行期容量；初始1＋15继任达到16，第17个新 record 被拒，当前有效 client 仍可复用。残留 prepare 锁是开发/构建可用性问题。最小先补安全恢复说明；不得按年龄自动删锁。`finally lstat` 遮蔽异常观察也成立。 | 不新增；保留限制 |
| 8 平台/D2 | **采纳。**mac27实测、mac15未验；两条Linux条件skip、Windows/参考设备/D2均不冒通过。 | 正式/平台 HOLD |
| 9 redo/本体整表/导出 | **采纳现状，收窄功能判断。**FR804不要求独立redo历史选择器；Undo-of-Undo不是假撤销。当前 UI只针对最后 receipt，并非一般历史撤销栈。本体整表和当前页CSV是真实范围限制。 | 非本轮新增规格违背 |
| 10 工程卫生 | nonce、随包fixture、文件规模、生产 `read_text()` 可登记维护项；workspace `"*"` 指向锁定仓库内包，不等于外部浮动依赖。**“messageKey从不渲染、合法输入可NaN”证据不足**：`explainError()`按messageKey选固定模板，先经过 `safeDisplayError()`；相关数字参数是严格必填数值。`invalidation-v2.json` 当前1745B全ASCII，缺UTF8是潜在维护风险，非当前cp1252故障。 | 无已证新增阻断 |

§9 编号 **11–42，共32项**逐项意见：

| ID | 处置与必要边界 |
|---|---|
| 11 两份16槽 | 采纳，重复Top4；保各自责任，不相加、不退款。 |
| 12 records16 | 采纳，重复Top7；更正为第17个新record被拒，非16次死亡必然使所有调用失效。 |
| 13 本体整表 | 采纳，重复Top9；服务端分页/规模验收待后续，不冒性能通过。 |
| 14 Turtle字节上限 | **部分误判。**`semantic_execution._term()` 在 SinkParser 前调用 `semantic._text(text)`，已有1MiB门。`semantic_scopes` 另一路缺局部显式字节门可留账，但需保留其内部来源、上游输入及当前能力边界，未证两处均绕过1MiB。 |
| 15 删除影响投影 | 采纳UX权威性风险；前端投影不是权威 undo-impact。尚未证明真实完整Diff/确认被替换或提交失真。 |
| 16 busy finally | **不采纳当前重叠写反例。**action 开始先拒 busy；disconnect 不清 busy，旧 finally 前没有另一 action把 busy设真的可达链。保未来维护风险。 |
| 17 焦点/aria-disabled | 采纳a11y欠项；`selectWorkspace()`仍检查真实busy/uncertain等门，链接可聚焦不等于已证绕过切换权限。 |
| 18 CSV | 当前N3编码使公式开头受限，护栏难触发不等于不安全；导出受已验证当前页、page/shape限制，缺单独字符串cap不等于无界。保当前页范围。 |
| 19 历史下一页 | 采纳UX限制；固定快照分页/顺序校验仍在，没有证明错页或混历史。 |
| 20 无AbortController | 采纳底层取消限制；不可把围栏称物理取消，也不能为了取消已进入写入而撤销责任。非单凭未出现API即可认产品缺陷。 |
| 21 controller Map | 采纳长会话保留风险；其中包含未决意图与认证Job，不能无条件LRU/切项目删除。后续回收需区分可结束责任。 |
| 22 read微任务丢弃 | 采纳条件UX观察；退役/序列变更导致不发旧读是防陈旧机制，也有单飞＋一次合并刷新。未证当前应发读取永久丢失。 |
| 23 软/硬删除 | 采纳语义分层说明；当前managed墓碑保来源，manual物理删除仍有不可变历史，不等于不可撤销。 |
| 24 seen65536 | 采纳有界session上限，保留防重放设计；无容量实测推论。 |
| 25 内部事实值异常 | 内部message含值属实；public分类只发固定码/受限params，未证跨边界泄露。按报告“潜在”留账，不升级当前事故。 |
| 26 再撤销冲突 | 采纳为保护；保ABA/后继编辑冲突，禁止统一no-op。 |
| 27 createIntent内存 | 采纳限制；重启后新operation创建同名项目是新请求，不自动等于重复副作用。原operation跨session UNKNOWN仍按M2。 |
| 28 内部create_project | 采纳潜在误用点；当前公开协议不可达，不能认已绕过正式创建合同。 |
| 29 workspace.py | 采纳测试专属易失模型的误用风险；当前正式draft走另一路，未证已丢持久草稿。 |
| 30 客户端Diff | **须精准措辞。**`OntologyPage`本身有生产调用；但生产传 `previewManagedEdit`，提前走权威事务路径，旧 `previewEdit`/本地preview展示分支不被采用。不能说整个组件无生产调用者。 |
| 31 测试profile不删除 | 采纳测试卫生观察；失败profile还是验收原件，不应统一删除。需要明确保留/清理政策，非运行产品缺陷。 |
| 32 文档/归属 | 采纳正式化欠项；appId/个人仓库名不能单独证明法律归属。 |
| 33 Python Dependabot | 采纳覆盖缺口；当前手工锁升级政策不等自动扫描，禁止据此自行升级。 |
| 34 弱断言grep | **不采纳模式命中即弱测试。**空集合、truthy等可是真实负例/辅助断言；需逐case证明缺失业务预期，当前没有新增具体反例。 |
| 35 ACK丢失测试边界 | 采纳：注入在原IPC业务回复返回后，未覆盖engine→main腿。且“main尚未持久化”须说清：领域提交由engine持久化，main intent为内存，不能暗示缺一个已承诺main持久账本。 |
| 36 缺失profile模块 | 悬挂私有分支可留维护风险；当前正式query使用现有 `execute_request`。**并非所有import都被except吞掉**，有的在try外。接线前须修闭包，当前未证该分支生产可达。 |
| 37 单飞拒并发 | 采纳设计事实，保有限拒绝；不改为无界排队。 |
| 38 Undo复杂度 | 采纳源码风险：每个后继commit重建retirement历史，可能重复扫描；实际规模/耗时仍待D2，不能量化退化。 |
| 39 全局book跨项目 | 采纳共享book更新事实；按job.projectId找原pending、局部state另核project，未证跨项目覆盖或授权扩大。 |
| 40 Git历史前置 | 采纳本地浅克隆文档欠项；CI fetch-depth0已补，固定旧reader验收不得删除。 |
| 41 非POSIX NOFOLLOW | 采纳平台防护降级及非合作写者竞态边界；当前是源码审查风险，没有实际Windows逃逸证据。 |
| 42 新uv前置 | 采纳新增工具依赖；但“未先uv sync必失败”过强：命令是 `uv run --frozen python ...`，不是直接调用缺失python，允许uv按锁准备环境。README也已列uv sync；可补钩子说明，不认已证清洁环境无法启动。 |

报告自身另应登记而不改原件：

- §6.2 的 `545 files + 352 dirs + 14 links = 911`，与910总数不符；应按 ROOT inventory 的root计数口径更正。
- §10.1“§9全部42项”应为“编号11–42的32项”。
- “原始 `messageKey` 不直接显示”是安全呈现方式，不等于没有可操作中文解释。
- 不采纳§10.4要求“任何改码都重跑全部旧验收”的泛化：应生成新身份，并按实际受影响面验证，未变历史证据保留其原适用范围。

**建议本轮最小动作是登记上述采纳与纠正，保留 M1/M2/M3、正式HOLD和全部原失败，不为消除审查意见而松动未ACK责任、origin或硬预算。**本轮没有实施、运行或新增验证；未读取 Z 本轮目录。

---

## 追加：ROOT 实核补充与 Z 已结束报告处置

本段是在 Z 本轮报告真实终态、两方独立性已冻结后追加。前述 MiniMax 审核原文的前 10917 字节保持不动，历史前缀 SHA256 为 `38871f6253280199782eeddf4465f16d37acd62290ec906ee771604ae888bf42`。此前“未读取 Z 本轮目录”描述的是该前缀形成时的事实；本次追加已按授权全文读取 Z。

### A. MiniMax 补充校正（不覆盖原段）

1. ROOT 原 inventory 的 APP910 应为 **545 regular files + 351 directories + 14 symlinks = 910**，APP root 另列；报告括号的352目录把root计数口径混入。前述“按ROOT口径更正”据此明确，不改变原报告。
2. §4 业务回复丢失后的恢复按钮链还需同时满足：main已经offer；同一个renderer controller仍存活；原invoke已经reject或返回，而非永久悬挂使busy不结束；同owner/session仍健康；原pending未被真实业务payload接受清除。reload/crash会丢失该内存pending，不能直接用来证明同controller按钮仍在。这里只登记真实可达链的必要前提，不新增实验。
3. 每个未ACK的A同时占原engine/IPC delivery责任。A累计达到16时，恢复调用B已无额外delivery槽可用；所以不能表述成“16次恢复按钮点击后必在service:735抛INVALID_STATE”。实际通常可更早由IPC `deliveries.size>=16`、receiver容量或uncertain门返回有限拒绝；具体出口取决于当时状态，不能固定为service错误码。两独立16槽不能相加，也不能因后续回复ACK而解除原A。

### B. Z 报告身份与结论边界

已全文读取 `/Users/kyle/Documents/工作/知爻/本体/outputs/20261024_t01_fde989ac_package088_designated_dual_review_001/zcode/report.md`：**50991B / 259行 / SHA256 `8d333399fc032b0b82fd486ae0ff80ee24dc77db976b0783ad52510e46d21518`**。Z 原结论是当前内部演示 **PASS**、正式分发/平台 **HOLD**；本追加不改其结论或等级，不把范围限制说成已修复。

两报告结束后交叉处置不等于把本方发现发送给任一外部模型。此次仍未执行测试、构建、APP、engine、网络、SQL或GUI；只写本审计文件。

### C. Z Top10 逐项处置

| Z项 | 核对、采纳及最小必要动作 | 对当前内部演示的影响 |
|---|---|---|
| 1 真实CI三失败未闭环 | **采纳流程欠项。**fde尚未push，本地fresh002不等于远端通过。后继push/CI/合入按ROOT真实授权和原流程执行；不能提前宣称CI已绿。环境首败不自动要求产品新候选；若实际改码，才刷新身份并按受影响面验证。 | 发布流程仍未闭，不新增源码缺陷 |
| 2 M1与records16 | **采纳限制，保原权限/未知责任。**uncertain影响该owner的主链，health/tasks等不是全部失效；新session可以发新record，但旧责任不会因此清零。初始1加15继任后第17个新record拒绝，现有有效client仍能复用。文案/自救说明可留后续，不凭对账UUID清闩锁。 | 既有范围限制，未修复 |
| 3 M3与fullIntents | **采纳安全责任，不当泄漏统一退款。**ACK丢失、未受理回复丢失、已入线UNKNOWN、未入线失败的重试条件不同；原token只有原精确消费能结算。16次可达累计须保前提，见本文件MM原段及追加A；不能将全部失败泛化为16个互不归结的新UI意图。 | 既有有限容量，不新增阻断 |
| 4 注入retire失败无产品恢复 | **采纳潜伏限制。**测试的直接consume重试不冒充产品自动ACK重试；自然可达抛错未证成。有界私有ACK重试仅为未来方案，须保真实frame/session、原receipt和已完成回调幂等，不能本轮擅实施。 | 当前没有新增自然故障反例 |
| 5 M2跨session创建 | **采纳现行创建合同边界。**origin全等保护原dispatch归因；旧创建回执缺物理重证明时保持UNKNOWN。后继resolution不能删origin、只凭同UUID/body重授或扩建持久intent账本。 | 已接受限制，未修复 |
| 6 签名/公证/目录包 | **采纳正式分发硬门。**当前仅用户明确的未签名内部目录包；签名、公证和安装目标均未补，不借内部PASS关闭。 | 内部范围允许，正式HOLD |
| 7 wholeAPP legal/_distutils | **采纳法律/来源未闭门。**机械闭包接受不等法律全闭合；292B package.json由builder规范化不能单独说明合法性已解决，也不是意外丢源码的证据。 | 正式HOLD保持 |
| 8 备份/物理HOLD/P0欠项 | **采纳。**迁移备份有机制不等恢复演练；应用内项目备份/恢复及FR002/203/300完整功能仍欠。现范围不是完整MVP交付；不据此启动损坏SQLite研究、绕HOLD或伪称已验恢复。 | 范围/正式欠项，不由本轮补功能 |
| 9 平台/设备/D2 | **采纳。**当前运行host27.0.1，目标15、Windows、参考设备与规模/执行计划未验。UNIQUE隐式索引存在，“只有PK索引”旧说不能恢复；没有新增负载或性能数字。 | 平台/规模HOLD |
| 10 a11y/i18n/卫生 | **部分采纳。**a11y实测、单语/RTL、法律文档、Python自动扫描与大型文件维护欠项留账。messageKey用于固定模板，不直接显示不是功能缺陷；NaN须给通过safeDisplayError及paramsSchema的合法反例，目前无。1627行semantic.py低于2000，不能列作超2000实例；profile悬挂分支需保持当前不可达与部分import在try外的边界。 | 没有已证新增内部阻断 |

### D. Z 清单未核/不满足项的保留口径

| 未核/不满足范围 | 处置与边界 |
|---|---|
| Windows/Linux参考设备、五龄设备、目标macOS15 | 全部保未验；本机27.0.1的PASS不能替代。两原Linux条件skip不作PASS，亦非本轮隐藏失败。 |
| D2规模、负载、索引执行计划 | 保未验；本地SQLite也有规模义务，不能因“非云”整体判不适用。存在UNIQUE隐式索引，不等计划/延迟已测。 |
| 签名、公证、安装、wholeAPP legal/_distutils | 保独立正式门，机械身份不代法律和目标设备接收。 |
| 损坏SQLite B/C、用户备份/恢复演练 | 保HOLD/未验；不将内部演示限定范围变成物理安全全通过。 |
| a11y、焦点/读屏/对比度、locale/i18n/RTL | 保未核/欠项；源码可见aria等不能代合规实测，也不因当前单语就扩功能授权。 |
| 全屏状态、逐表单输入保留、后退语义 | 保逐屏未核；已有Query/Ontology有限正反例不代全应用覆盖。 |
| 渗透测试、安全问卷、谁查看过审计、静态加密与失窃预案 | 保未建/未验；单用户离线可排除部分SaaS机制，但不能全局免除本地数据安全义务。 |
| 依赖advisory、Python自动扫描、死分支/大文件清理 | 保未知/维护欠项；不以有锁和许可证文件认定无漏洞，不自行升级或接通profile分支。 |
| README一小时、文档、组织归属/bus factor、人员13项 | 无实际人员与时间证据保持UNKNOWN；appId/账户名本身不能证明法律归属或人员只有一名。 |
| 保留期/彻底删除、DLQ视图、运行维护机制 | 按当前本地形态判断；领域历史、未决责任与临时验收证据不能为“清理”直接删。不是所有云实现适用，但本地恢复与运维说明仍可适用。 |
| FR002项目导出、FR203 Turtle导入导出、FR300 CSV/XLSX | 明确保未完成P0；当前页CSV/内置示例采用不能代替这些独立功能。FR804不要求独立redo历史选择器；Undo-of-Undo保持有效，FR402/403不强制普通查询一次全量导出。 |
| 真实LLM/网关、密钥与外发、模型质量/花费/eval | S3前没有运行接入，不称实现；未来接入须重新评估整类义务。当前“无模型key”也不能作为全仓任意历史秘密不存在的完整证明。 |
| CI远端闭环、保护分支、dev/staging/prod、0/17、C4–C6/D8/双审积压 | 全部保持真实状态；仓库模板、当前双审PASS和本地绿不代远端配置、push/CI/merge/远端复核。 |

Z对只读覆盖有明确自述：若只是既有回单复核、抽查或继承历史事实，不把它改成新运行、全部源码穷举或已经实测。“参数化全量（抽查）”只能按实际抽查解释；“page400”没有400页/性能新证据，已有分页身份/顺序验证仍成立。新制备锁崩溃残留、lstat遮蔽和非POSIX降级按前述MM Top7/§9#41留账；Z未新增该段不抹MM观察。

### E. Z 报告事实更正（原件全部保留）

1. **§1.3所称声明哈希差异不存在。**本方重新读取actual timeline、shared-prefix.txt及两份冻结prompt的原字节，全部实际引用/哈希为 `49a2c19acd047f0ed7223e30dde80208b8b4c097037296c9f4b8a62f4264aada`；原timeline **17590B**。三份提示文本均有 `c097037296`，均无Z所称的 `c097037298`。因此Z§0第5项、§1.3、§9的“任务书转录笔误”须按报告读取/转录错误登记，不归因父提示词或证据文件被改。直接证据 `/Users/kyle/Documents/工作/知爻/本体/outputs/20261024_t01_fde989ac_package088_designated_dual_review_001/ZCODE-HASH-CLAIM-CORRECTION.json` **2464B / SHA256 `de1fd900550f30c2c24b568f6a2c80a90950ab7d066987499fa643d2c7f40ebd`**，本方已复算匹配。
2. **§4.3 checkout范围错误。**源码 `.github/workflows/ci.yml` 是quality一个checkout、desktop一个checkout；desktop `matrix.os=[macos-latest,windows-latest]`，同一 `fetch-depth:0` 实际作用Windows和macOS。不是“quality/mac两个作业，windows未动”。Windows cp1252修复另在测试中，但不能据失败类型把workflow影响范围切开。
3. **UTF8读取位置需精确。**6文件8处读取修复成立；并非8处全是module-level eager装载：ordinary_library的读取在测试方法内。新增为7个module/variable组合而非7个不同文件（business3和query_definition各重复变量）；不影响真实eager回归及原60PASS回单。
4. **2000行算术及messageKey/NaN收窄。**engine2623/job_store2589超过2000；semantic1627不超过。`explainError()`按messageKey选固定中文模板且前置safeDisplayError，错误目录对相关数字必填并限域；仅看`Number()`不能证明产品会显示NaN。保持可行动文案改善建议，不造当前合法反例。
5. **正式范围和重启口径。**新session可能使M1换record恢复部分主链；旧UNKNOWN、未ACK槽、跨session创建物理绑定不由此消失。不能把“重启可恢复”解释成旧回执已被确认/责任已结算。所有历史失败与native首0 UNKNOWN仍保留。

### F. 本次追加结论

Z Top10全部登记，清单未核及正式门继续保留；上述事实更正不改两方报告的原始PASS/HOLD。当前没有从新增意见中确认需要立即修改当前候选的内部演示阻断，也未批准任何退款、容量变更、origin弱化、代码改动或运行。本文件前缀及两外部报告均保原字节；后继动作由ROOT按真实流程裁定。
