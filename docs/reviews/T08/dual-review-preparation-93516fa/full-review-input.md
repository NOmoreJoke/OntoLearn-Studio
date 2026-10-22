# T08 完整累计实现独立对抗审查输入

你必须实质审查完整当前累计代码及全部原验收，不是只读摘要或v2探针，也不是批准缩小S1。人类要求补齐所有未通过ZCode/MiniMax的审查；尚未具备完整运行验收不构成拒绝审查理由，但缺失关键验收时不得给Pass。允许结论NotPass（不通过）或无法完成验证，须列明真实可修项/缺前置。不要因为开发者预计有缺口而停止代码审查，也不要强写通过。

## 固定身份

worktree `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`；branch `feature/weekly-t08-agent-model`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；product `93516fa8455cf4b195cbfb699aa7a6652d428b6f`；本准备包证据来源process `77c45949d39d797b39ef2cf30a10f3e1772730a1`。准备包提交会使process HEAD仅新增docs/reviews/T08过程材料，product不变。实际派发时由root记录该准备提交和真实任务身份；本包没有任何已创建任务或已读回设置。用git对象/快照核验，不把移动HEAD或别线未批准实现当受审代码。

`input-manifest.json`列出25项全部实现/测试/fixture、完整base→product的44项差异、828项完整产品Git树哈希，以及每份快照/提示的来源、大小、SHA。先核对清单与快照；差异/缺件明确报出，不静默跳过。AGENTS主文错误链接的m0更新计划在固定树实际归档于`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`，本包提供该原件，未改源指南。

## 读取顺序及全部范围

1. 当前规则快照`inputs/current-policy/AGENTS.md`及`inputs/controller/developer-common-instructions.md`、`desktop-operation-policy-20261022.md`、`external-review-permissions.md`全文。历史launch、旧报告里的无GUI/CLI/旧哈希按历史解释；当前桌面偏好已撤回，但内部lease和本任务写/运行边界保留。
2. `inputs/product-context/docs/prd/PRD-本体学习与落地Agent工作台.md`全文，至少逐项核对FR-800–806/900–902/904、FR-204/302/400协作、附录F和G.5 A-01..10中的相关边界、C/D/E/G实际领域依据、10–12全文，尤其11.3全部九类及12.2全部七项。FR-903保持原P1，不新增范围或拿P1遮掩P0。`inputs/controller/requirements.csv`、`acceptance-baselines.csv`、`plan.md`、`decisions.md`保留原门，不拿数量替代验收。
3. 下列25项每项全文读取，源均为product93516fa，实际快照在`inputs/product/<原路径>`；其中所有TS/TSX/Python源码文件统一追加`.snapshot`数据后缀（例如`agent-service.ts.snapshot`），字节不变，准确路径及原路径映射见manifest的packageFiles.origin。该规则也适用于product-context中的源码，禁止把归档数据当作新增可执行实现。完整44差异中的其他19项原设计/证据也必须读；其余基础设施按完整Git树和`inputs/product-context/`核对实际调用/未接线状况。

- `apps/desktop/src/main/agent/agent-service.ts`
- `apps/desktop/src/main/agent/capabilities.ts`
- `apps/desktop/src/main/agent/conversation.ts`
- `apps/desktop/src/main/agent/deepseek-codec.ts`
- `apps/desktop/src/main/agent/errors.ts`
- `apps/desktop/src/main/agent/tools.ts`
- `apps/desktop/src/renderer/src/agent/AgentSidebar.tsx`
- `apps/desktop/src/renderer/src/agent/agent-sidebar.css`
- `apps/desktop/src/renderer/src/agent/context-actions.ts`
- `apps/desktop/src/renderer/src/agent/sidebar-presentation.ts`
- `tests/fixtures/agent/fixed-input-cases.v2.json`
- `tests/fixtures/agent/fixed-input-probe.py`
- `tests/fixtures/agent/manifest.v1.json`
- `tests/fixtures/agent/manifest.v2.json`
- `tests/fixtures/agent/synthetic-cases.v1.json`
- `tests/fixtures/agent/t09-873c8c0/G-base.json`
- `tests/fixtures/agent/t09-873c8c0/equipment.csv`
- `tests/fixtures/agent/t09-873c8c0/origin-manifest.json`
- `tests/fixtures/agent/t09-873c8c0/unclosed-high.rq`
- `tests/unit/t08-agent.test.ts`
- `tests/unit/t08-codec.test.ts`
- `tests/unit/t08-conversation.test.ts`
- `tests/unit/t08-evaluation.test.ts`
- `tests/unit/t08-fixed-input.test.ts`
- `tests/unit/t08-sidebar.test.ts`

4. `inputs/process/docs/reviews/T08/internal-review-1.md`至`internal-review-8.md`全文，原失败/暂不通过不能改写；`dual-review-backlog-2026-10-22.md`给四批与中间候选后继。`evidence/verification*.json`、首次失败gzip/元数据、T09授权输入验证、`fixed-input-actual-observations.json`和原`check-93516fa-original.txt`逐项核验。它们均为历史Codex独审/旧运行，不能当成你的测试或指定模型Pass。
5. `inputs/product-context/docs/iterations/T08/design-and-integration.md`及本包`acceptance-evidence-map.json`交叉核验；矩阵是导航，不替代原PRD全文，也不能只照抄开发者自述。

## 必须实质检查的问题

- codec是否真正严格拒绝未知/截断/空/非法结构，保留所有必需thinking reasoning_content，多轮tool call/result ID一致、重放与边界长度，不能悄然退模式；仅数据编码不得成为第二网关。
- 工具整批参数预验、可信project/revision/snapshot/scope/module/mode/选择对象、读/草稿/隔离运行边界、取消/超时/迟到结果与真实任务状态区分、调用与交换/输出预算是否有绕过。
- 同一问题收据完整、失败不被自由文本/只选成功引用隐藏；跨问题旧证据不混入、全会话ID和预算不清零；provider失败/预算尽/部分批取消仍保留草稿及真实已完成记录，快照不可反写。
- 字段投影只是最小化，不是最终外发授权。实际messages/tools/reasoning/摘要/历史/错误、端点/主体/配置版本、完全本地切换都需I06唯一最终检查；不得默认工具结果获权。
- AgentSidebar真实props/SSR代码、DOM文本安全/资源注入、本地/未就绪/缺handler/旧context的发送与retry禁用、异步重入及输入/草稿保留；SSR不等于挂载事件、持久数据或真实Diff确认。
- v1合成case和v2真实RDFLib/CSV是否忠实，不从oracle预填；Q01/Q02阶段及同数量语义错误A02、001/002身份/名称/行号、SPARQL原字节/哈希一致性。手工provider消息/有限probe不得当实际NL生成/正式查询/推理/行为/沙盘产品能力。
- 从完整原验收反查遗漏/假设，发现缺件、异常路径或架构问题给具体文件、固定候选行号、触发输入、影响及可复现证据。只审已实现代码的局部安全性不能获得完整功能Pass。

## 真实证据和未验条件

现存原check717 TS/1052 Python、T08六文件87项；最新内审8通过纯模块范围。历史check679/691/706保留的是对应候选摘要及成功日志SHA，本包未提供这三次完整成功日志；717项check才有完整成功原日志。首次失败原日志另以gzip保留，全部内审失败/修复原件也保留。你须区分读过的旧日志、自行实际运行、静态推断、未验，不得宣称重跑。原check输出逐字节归档SHA见manifest。

目前T08没有正式获批I06传输/最终授权/安全存储接线、T01真实Diff/真人确认/事务/撤销/恢复、各领域真实服务/公共App/bridge挂载，没有真实API主体与批准消费上限/正式模型质量/版本固定/平台验收。本包展示的是当前本线证据缺口，不推断其他owner的最新产品状态。不能为凑通过用替身或复制未批代码补齐，不要求你花费API或搬运secret验证。

整体Pass须覆盖完整约定范围并有全部关键验收的实际证明。关键验收缺失、无法执行或仅有替身/SSR时，整体结论必须明确NotPass或无法完成验证；可以另列“哪些静态代码未发现问题”，不得用局部Pass作为整体结论。缺依赖也必须完成可做的实质代码审查并列可修项，不能只回复“等接口”而不读源。

## 只读职责与当前授权

只读实现/测试/依赖/配置；不修改、格式化或生成product文件，不提交/推送/切分支/合并，不改冻结prompt/manifest，不读取.env/secret环境/密钥/钥匙串/付款数据，不调用DeepSeek或其他付费API、不新购资源、不启动第二指定任务或互传本轮对方意见。Full access/yolo不扩大任务职责。

当前材料准备授权不是新的产品测试/native运行票；派发时如需新验证，先由root明确该任务可执行命令和互斥资源。现有日志已读不记重跑；有新疑点可提出精确最小复现与所需命令。不得无变化重跑、私自npm ci/uv sync/更新依赖/生成桩或恢复被自动审批拒绝的工作。若运行受限，静态审查继续并如实NotPass/无法完成验证，不隐藏限制。当前桌面可用性只影响内部短创建/核验lease，不占整个后台推理时长。SQLite损坏HOLD和其他阶段边界仍保留。

## 独立报告格式与完成门

使用中文，报告只写自己指定路径。必须记录真实任务/session/turn标识、应用来源、实际模型/思考/权限读回、worktree/branch/base/product/实际process与input-manifest SHA、全文阅读覆盖清单、实际命令/结果、静态/历史运行/自行运行/未验边界。然后逐项列历史内审1–8问题是否仍在固定代码中成立与证据；新增问题按P0/P1/P2/P3给固定文件行号/触发/影响/证据/建议，并把缺前置与可修代码问题区分，但都保留在完整验收结论中。

结尾必须明确“通过 / 不通过 / 无法完成验证”之一，说明完整原验收是否满足及阻断。不要自己修改实现或把已知未验改为通过。任务需实际终态和完整报告读回，不以已创建/流式途中/只有终态词当完成。双方本轮意见互不提供；历史Codex内审作为同一公共输入，两任务各自完整范围。
