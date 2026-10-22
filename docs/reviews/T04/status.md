# T04 查询状态

2026-10-23 固定后过程更新：**产品候选 5070004 已固定；完整验证、固定候选内审及新双审准备包独审通过，两个新审查树已部署，等待总控内部创建窗口。新指定任务、报告和实际设置读回均未产生。**

- 固定产品：`5070004ec8e3219bea33960bd88f57f1976e9cf8`；共享批准基线仍为 5f。
- 两个新 review 树实际 HEAD：`f2102f0738706d7ed29907ac84f10ad0a506555a`（detached）；名称为 `T04-s1-zcode-review-5070004`、`T04-s1-minimax-review-5070004`，位于同一 `.worktrees/`。42 项产品字节均等固定 507，23 项支持 payload 均等过程 Git；各自独立依赖，仅 de15 指南保护 M。
- 准备包 manifest：`ff8c08b632b93bd8e5fd7a77a722f89dd7eb99a05ca60590aa836efe63c1bff4`；实际部署收据见 [deployment-receipt.json](p3-repair/deployment-receipt.json)，准备独审见 [preparation-audit.md](p3-repair/preparation-audit.md)，固定后内审见 [post-freeze-review.md](p3-repair/post-freeze-review.md)。
- 为新增过程命令记录 helper 按指南另跑完整 check，实际 TS719/Python1167 exit0；不将安装成功或过程准备冒充指定模型审查。双方完整正文和原件在各自部署树 `docs/reviews/T04/p3-repair/launch/`。
- 本方已向总控发送固定候选、实际部署与完整包身份申请内部调度；尚未取得新创建窗口，不抢其他 owner GUI。未 push/PR/CI/合并/发布，父验收不变；实际 Goal 仍 blocked，未新建 Goal。

本段是纯追加过程状态。以下保留固定 507 时的原实现/验证状态；审查该产品原文须从固定 507 Git blob 读取。本开发树的 status 后续过程追加不改变固定产品和两个 review 树，不沿用旧 554 双 Pass。

## 固定 507 时的记录

2026-10-23；owner/chat `01a15bcd-fcba-7583-a307-56497cdde347`。**四项 P3 已在新树修复，完整检查与独立内审通过；正在固定新候选、准备双方全新完整同版审查。父功能及发布未完成。** 实际 Goal 工具状态仍为 `blocked`，依总控具体授权续接原目标，未新建 Goal。

## 当前修复身份

- worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query-p3-repair`
- branch：`feature/weekly-t04-query-p3-repair`
- 起点：`554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`；批准共享依赖/集成基线仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 最新保护指南 SHA-256：`de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，仅未暂存 M，不纳入提交。
- 旧开发树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query` 停在 `9da9da48b45b4f0cbbe084d95c3d23ebd85c579b`；两个旧审查树停在 `9a4dfc8f1e9106a4c05423f80a26e9e88eb0aaa1`，全部冻结。
- 总控已实际接收旧产品 554 的完整有界 S1 双 Pass；该结论不能沿用为本轮修复候选通过。旧报告、原始输入与全部逐意见处置仅在冻结旧树保存。

本轮产品仅改 `query_service/drafts.py`、renderer `query/{draft,results,QueryPage}`；配套本线单测、fixture、交互探针和文档。未改 reader、共享 App/main/preload/contracts、Store/worker、依赖/锁/CI、其他 owner 或总控状态。

## 实现、验证与内审

既有完整 S1 包括离线模板、可视化条件及 SPARQL 编辑、严格 RDF 项序列化、保存意图/真实 ID 回填和异步切换隔离、显式范围/输入/历史身份、受绑定分页读取与取消 ACK 处理、表格/空结果解释及当前页 CSV。真实执行与保存接线未就绪时页面对应动作禁用。

四 P3 的技术选择和最小文件面见 [修复计划](../../iterations/T04/p3-repair-plan.md)：统一 name/SPARQL 原串 UTF-16 上限后按固定 30 字符去边缘空白；CSV 区分真实数值/布尔与受公式防护的字符串；字段达到 16 时仅禁用未选项；成功新建/载入 saved/model 清空 visual，非法条件禁用生成。

- `npm run check` 实际 exit 0：TS 18 文件/719 项、Python 1167 项，lint/格式/类型/构建/Ruff 全通过。
- 定向 TS65、Python112 项通过；静态 SSR14 项通过。
- 真实 QueryPage DOM5 情景通过：16 字段取消后重选；saved/new/model 三种载入清空；literal→非法 IRI 禁用生成、完整原 SPARQL 保持及修正后恢复。使用独立 Chrome 155.0.8059.85 headless/offline，上下文请求与 pageErrors 均 0。该组件 fixture 无 App、IPC、执行器、Store 或模型调用，不计生产 CSP/原生/父验收。
- 独立 agent `/root/t04_private_review` 的技术计划审查与完整 S1＋本轮差异审查均实际通过；固定提交后的字节核对待收口。记录见 [实施独审](p3-repair/implementation-review.md)。独审不替代指定双外审。
- 首次网络安装失败、真实回归失败、探针定位失败、Zod 码点长度反例及首次 lint 失败均保留。完整 argv/cwd/起止/真实 exit/raw SHA 与终态详见 [验证收据](p3-repair/verification.json)，本地大日志/trace 位于 `test-results/t04-p3-repair/`（ignored）。

## 父功能与交付门

精确接口责任见 [integration-handoff.md](../../iterations/T04/integration-handoff.md) 与 [reader-integration.md](../../iterations/T04/reader-integration.md)；逐 FR 入口见 [acceptance.md](../../iterations/T04/acceptance.md)。

1. T00/I05：正式 draft→query.execute、实际执行文本/列/RDF term/ASK 元数据、真实项目/快照/推导身份、外联拒绝、时限/取消/游标仍待批准依赖与联验。reader 的 columns 空数组语义未在本轮修改。
2. T01：唯一 preview/confirm/commit、读取恢复/撤销/过期及真实保存身份仍待正式事务接线。
3. T08 真实自然语言、T09 完整案例、T10 查询跨设备复用、适用局部关系图，以及 FR-400–404、C/D/G、11–12、两 OS/真人与全部父 P0/跨模块矩阵继续保留。
4. 新修复候选须由 ZCode GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh 各全新完整同版审查，实际终态/全文报告/逐意见处理后才可进入后续授权门。未 push、未 PR、未 CI、未合并或发布。

桌面操作按最新指南，由总控内部协调互斥资源；本轮未占用 GUI。未调用模型 API、读取凭据、兑换额度或新增付款。旧指南中的静默桌面与一律禁止 GUI 段已由现行政策取代，旧冻结输入不改写。
