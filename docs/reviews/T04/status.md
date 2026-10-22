# T04 查询状态

2026-10-22；owner/chat `01a15bcd-fcba-7583-a307-56497cdde347`。**T04-S1 独立实现、完整检查与独立内审通过；指定双审实际任务仍为 0。总控曾授短 GUI 窗口，创建前遇 CUA 并发保护，已停止并明确释放；未发送正文、无真实任务 ID。完整 T04/父功能未完成，Goal 保持 active。**

## 当前身份与候选

- worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query`
- branch：`feature/weekly-t04-query`
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；无凭据提示的只读 ls-remote 实查远端 develop 同值。
- 当前产品/验收候选：`554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`。生产实现与 `070b1fa` 相同，新增显式同数量错义反例。其后仅追加 manifest/流程证据。
- 精确候选 33 文件及 SHA/大小：[service-candidate-554ec89.json](evidence/service-candidate-554ec89.json)；完整终态/原始日志哈希：[reader-service-verification.json](evidence/reader-service-verification.json)。旧 `c4aa5f9/99b8ab9` 及其 verification-summary/final-verification 原记录保留，不混称新候选证据。
- 仅保护 AGENTS.md 由总控更新后保持未暂存，当前 SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`；旧接收 SHA 与启动 SHA 保留在历史提交，不混入产品提交。2026-10-22 用户已撤回静默桌面限制，内部互斥调度仍适用。

全部产品变更只在授权 query_service/、test_query_service_*.py、renderer/src/query/、t04-*.test.ts、fixtures/query/、docs/{reviews,iterations}/T04/。未改共享契约/App/main/preload/Store/worker/锁/CI或总控 tasks/state；未消费未批准实现。

## 已实现与验证

离线模板、对象/字段/条件构建、SPARQL 草稿和严格 RDF 项序列化；私有保存意图、新旧定义 ID 与异步文档隔离；独立页面安全表格、当前页 CSV、空结果方向、范围/历史/实际查询显示。未接线执行/保存保持禁用，不生成假结果。

新增客户端 reader 直接使用批准 getResult/getResultPage/getJob/cancelJob、TaskView/TaskUpdate：切项目/输入/generation 后废弃迟到读取，始终一页载荷、空页保留两字段排序锚，query-only 取消且 ACK/真实终态分开，已知 ACK 版本下限跨读取/通知/取消前查保留，错误按批准分类。无新 IPC、持久缓存、执行器或 writer。

- `npm run check` 对最终候选真实 exit 0：TS 18 文件/666 项、Python 1083 项；lint/format/typecheck/build/ruff 通过。新增 TS 36 项、Python 31 项。原日志 `evidence/check-reader-service-final.log` 本地 ignored，完整哈希已入证据。
- reader 合成 transport 故障测试 24 项；静态 SSR 14 项通过（组件/探针原字节与本次修复前一致已核对），不算真实 IPC/浏览器互动/CSP/下载/原生通过。
- 总控批准 T09 固定 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 输入；manifest `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`，17 项/PRD 来源哈希核验。原始/生成查询各独立还原完整 G-base 仅 A01，Closed 后空；显式错义查询返回 A02，与 A01 同数量但完整答案不同。仅标准 RDFLib 编写互操作，未以 expected 预填 Store，不计 I05 联验。
- 独立 agent `/root/t04_private_review` 实际全范围复核最终固定 SHA 通过，报告 internal-review-8.md；旧不通过、全部意见处置与再复核在 internal-review-1..7.md 真实保留。新 reader 三项竞态/分页 P2、原文 P3和 canonical 错误参数 P2均关闭。不替代指定两模型外审。
- 首次 lint/type/SSR依赖/新增错误断言失败原件均保留；无变化不重复全套。`git diff --check` 通过。

## 实际调度与下一门

总控已在仓库外 service-stage-register.md 正式登记 T04-S1，并全文接收固定准备包；派发预检确认准备条件满足。产品仍固定 554、base 5f，两方 review root 均 detached 9a；prep a13 和 diff 参数补充 facac 仅流程件。新增 T01/T03 共享交接不扩张本线责任或允许消费未批代码。

总控随后实际授予 T04 短创建窗口。本方 ZCode 项目/空草稿曾核对为指定 review 目录、游离 HEAD、GLM-5.3「最高」及「完全访问」，但这些是草稿设置，不是任务受理。恢复原会话后，本方项目仍显示「暂无任务」；点击本方新建任务被 CUA 的 “The user changed '/Applications/ZCode.app'” 保护拦截，未执行点击。按约定只做一次 fresh 只读观察后停止该 app；MiniMax fresh 观察也已在无关会话，未对其点击、创建或粘贴。GUI 已明确释放并回报总控；两方 task ID、发送和全文实读均未产生。remote compact 的连接失败单列为本代理 transport 故障，不计为产品检查或指定模型失败。

当前可直接粘贴的完整附件已在各方独占 runtime 组装：原完整正文与同义 diff 附录分别保持原字节，新增投递封面只说明完整读取与最小设置收据。ZCode 83018 字节/496 行/SHA `d2c0b328070962ac56c9dbae9d99ee026df538d786dc6ac39c3fe47619b6bb28`；MiniMax 83104 字节/496 行/SHA `94be45ae7e598a57ad63a0e53521c6ca13d9c76be3028cd7941dea81e0c9921a`。文件生成不算发送或完整受理；下次实际创建后仍须逐任务设置、原生 ID 和实际 Read 全行证据。详见[派发状态](round-1/dispatch-state-20261022.json)。

本线交付：[服务阶段](../../iterations/T04/service-stage.md)、[接线缺口](../../iterations/T04/integration-handoff.md)、[已批准读取适配](../../iterations/T04/reader-integration.md)、[验收对应](../../iterations/T04/acceptance.md)。正常回执固定 candidate、过程 HEAD、manifest/raw；下一步按总控实际交接的短窗口完成两方创建，不自行重占已释放窗口或改前方候选基线。

正式审查前刷新实际批准 develop/依赖并必要验证；ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh各全新完整独立任务，实际路径/模式/模型读回、真实终态全文报告/全部处置/同候选双方明确通过后才 push/PR（attach），实际 CI 通过后正常合并/远端核验。**当前未指定双外审、未 push/PR/CI/合并、未上线。**

## 原父功能完整缺口保留

真实 query.execute、只读与禁止外联、业务 Q-01/02完整结果及分页/取消/游标/历史身份；T01 唯一保存/预览/确认/原子提交/恢复/撤销/过期；T08 真实模型草稿与工具闭环；实际 ASK/RDF项/执行文本元数据和适用局部图；App、T10 跨设备、目标平台和原 FR-400–404/C/D/G/11–12/全部父 P0跨模块门。S1 合并后仍不关闭这些缺口或整个 Goal。

## 操作政策接收（以下为 2026-10-21 历史记录）

本节旧无桌面约束仅描述当时接收与执行事实，已被 2026-10-22 用户更新撤回。现行规则以最新 AGENTS、共同指令和桌面政策为准；不能将旧限制继续当作当前桌面阻断理由。当前阻断是实际 CUA 并发保护后释放了内部窗口，非等待用户预约或登录。

第九节与无桌面段全文已读/透传独立 agent：第九节 SHA `1f57a08e909e9d49a6e2c2d6e7012beec3e22b8e3c9e8eacad22c84dfb2d4b54`，无桌面 `5215df2ead4745e7d74f137c4fa6ac837a54114590b5dee2d83cd16bb728551d`，早期补发共同指令 `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`；后续共同指令 `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4` 和 external-review-permissions.md 亦已全文读/透传并实际回执。

ZCode 默认 yolo、MiniMax 默认 bypassPermissions，实际任务仍须读回；只读审查、指定模型和无桌面限制不变。本线未重建 Goal，未 GUI/Electron/e2e/native/HMR/凭据提示，未 secret/模型外发/新增付费/额度兑换。Codex 兑换仍须本人该次确认/阈值/幂等/读回，账号唯一负责人处理真实告警；无政策变化重测或放宽验收。

## 总控审计 R1：原始日志可恢复保全

总控审计 `T04-controller-service-candidate-audit.md`（SHA `ac844c9c75255127df142d3a6a23111213bb3e3fb6220dd33155eb915a6150a8`）确认固定候选/汇总/37 份原日志一致；本次只补 ignored 日志的 Git 可恢复副本。候选仍为 `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`，审计流程 HEAD 为 `19ef25259e6304949cef4a1993b006de11fb885b`。33 文件 manifest 针对固定候选；当前 status 流程内容已更新，不能声称当前物理 33 文件全等。

[无损归档](evidence/raw-logs-554ec89.tar.gz) 6081 字节，SHA `c17c2595d79900c539e4a0aa61bc1ad012e058af9e666282aa9c1f6079064865`；[逐成员索引](evidence/raw-logs-554ec89.index.json) 记录全部 37 成员、原始 61602 字节及每项 SHA/大小，并链接旧、新三份汇总的固定提交与哈希。已重新打开归档、完整读取全部成员，与原件逐字节/大小/哈希相等；首次失败原件及空日志保留，旧汇总未改。恢复方法见[恢复说明](evidence/raw-logs-recovery.md)。未重跑不变产品测试，未改产品代码/公共契约。

最新共同指令 SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39` 已全文读并透传独立审查 agent：T01 接收 storage/Python4/main8，T03 接收 engine packaging/entrypoint，其余按正文；仅更新归属，不代表批准未合并实现，也不放宽既有无桌面/指定外审资源/推送门。

2026-10-21 总控聊天 `01a154de-843b-7a00-8a80-51ba1c0aebce` 直接回执：从 `ae86f294a19befc94247733ee7ea186b5fab3d6d` Git blob 读回 archive/index，实算归档 SHA 如上、索引 SHA `6d369a87a25fa5db8e88307e7032827f95778b8ba4415ee4b5371432af5dc811`，37 成员逐字节等于原件/61602 字节，3 份原 summary 固定 blob 全吻合；**R1 已由总控实际核验关闭**，无需无变化重测。该回执晚于旧审计正文的“待闭合”，不改写旧审计记录。S1 产品仍冻结 554；独立树的 `82630f50def6aac2a5ba60470757791dd39053db` 讨论材料已收到，父接口按 T01 统一基础合同回应；4 个 canonical 错误形状校验仍不是业务运行证据。
