# T11 发布与整体验收状态

2026-10-21（Asia/Shanghai）。阶段：private_implementation_validated，独立 Goal 当前 blocked；完整T11尚未验收。

- 会话：01a15bc2-4551-7b51-8453-add1943f3b6e；仅负责 T11。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-release`。
- 分支：`feature/weekly-t11-release`；启动base/head：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 启动实际 git 状态：仅 ` M AGENTS.md`；这是总控同步规则，保持未暂存，不进入产品提交。
- 启动指南 SHA256：`db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`；后续纯政策更新另记下文，保持未暂存。
- 远端 develop 实查为同一 base。分支保护 API 返回 HTTP403（private repo 计划限制）；未证明服务端保护启用，不绕过原流程门禁。
- 独占新增：`scripts/release/`、`tests/unit/t11-*.test.ts`、`tests/fixtures/release/`、`docs/reviews/T11/`、`docs/iterations/T11/`、`docs/release/`。
- 不改共享 package/lock/builder/build/CI/main/security；不写总控 state/tasks。

已实现：严格manifest v1与离线核验器，候选/版本/锁/安装文件格式/哈希/签名公证/许可证/渠道一致性检查；T09唯一manifest及G完整预期引用；外部freeze固定时间、模型评估、全部检查预期、恢复快照和上一版资产。提供双平台只读取证脚本、设备验收流程、恢复/双向迁移规范、周六至少5真人主持脚本与空观察表。

实际验证：显式 `T11_FIXED_BASELINE_PROBE=1` 的65个专项测试及全仓check通过695个TS测试、构建、ruff和1052个Python测试；其中3项固定输入探针实际执行、无skip，默认不启用时明确skip这3项，不能当联验通过。sources此前实际核对12份归档且本轮未改；release脚本另做显式lint/格式检查。Mac collector此前语法通过且未改，Windows仅静态审阅，均无目标机运行。早期17文件/50用例/3指针观察留在t09-readonly-alignment.json；当前另已获准固定873输入只读联验，逐文件身份与边界见approved-fixed-baseline-probe.json，不消费未批准服务。

独立agent内审首轮及残留复核发现的预期自证、空壳快照、冻结时间回填、当前包冒充旧版及真人完成矛盾均已修复，最终复核通过，见 `internal-review.md`。该结果不替代正式指定双模型审查。失败原件与重跑日志保留本树ignored的 `*.log`；提交摘要和哈希见 `verification.json`，未把失败覆盖为通过。

下一交付：按 `docs/iterations/T11/shared-file-handoff.md` 由总控完成唯一owner交接；待完整批准候选、真实资源后接线与联验，重新冻结base/head、双方指定新审、门禁push/PR/实际CI/正常合并/远端核验和最终下载实装。当前只作可恢复本地阶段提交，无推送。

本地实现提交：`ffa0972800d6cb14910c43c185bfdd4dcf96d629`，19个授权新增文件。提交后仅AGENTS为总控同步的未暂存修改；源实现与最终内审核验器哈希一致。后续仅追加本回执，无实现/测试/配置/依赖/验收基线变化。远端develop本轮末次实查仍为启动base，未push/创建PR/申请GUI资源或发布。Goal保持active，不能将本阶段提交标为T11完整完成。

续跑新增：专项正例现实际经过合成E.5 exact/replay引用，新增缺失对象/数组指针、引用文件漂移及同数量错误完成对象4个拒绝用例。核验器/CLI/collector字节不变；新增测试已独立只读复核通过，全仓check再验通过，原始结果在pointer-unit.log/pointer-full-check.log。完整目标逐项证据与缺口见 `completion-audit.md`；没有新的共享接管或真实资源证据。上述“后续仅追加回执”描述的是764d690当时，当前测试增量将另作本地提交，正式双审仍需最终新同候选。

仍缺完整 P0 同候选、目标干净设备、有效签名/公证、最终下载渠道、真实模型/API资源及真人预约；总控已集中询问，T11 不重复询问。不运行本机 Electron/native/e2e/HMR，不触发凭据提示，不签名/公证提交/发API/外发/购买；正式接线、双指定模型新同候选审查、push/PR/实际CI/合并及发布另按原门禁继续。

操作政策接收：已在安全边界全文读回新共同指令及本消息附带的第九节/无桌面段；共同指令SHA `9717f699…19880`、第九节 `1f57a08e…d4b54`、无桌面段 `5215df2e…551d` 均与总控给定值匹配，完整值及实际执行约束见 `operating-policy-receipt.json`。保留原Goal、分支和50a3212实现/测试候选，未改冻结原件；未因政策追加重跑测试或重开产品审查。当前无实际额度告警，未查额度、消费重置或新增支付；独立审查子agent已完成，无自有本机GUI任务待撤回。此补充不授予共享文件、GUI、凭据、外发或付费权限，也不证明发布资源到位。

当前候选变更已复核：比较证据v2分别核对当前恢复、映射重跑、沙盘重放，不强制携带未选历史/推导/会话/先前撤销，也不把零提交运行误判不可重放。独立内审发现的undo选择泄漏与零轮次误拒均已修；其后固定873输入探针和仅完整SPO事实集合比较也经新复核通过，事件/动作/轮次保序、重复事实数不丢。核验器SHA `8f6aac79f43167cd243cc978e1ecf50d1a5262f43fbc421b1e6472bf77ba6c06`，报告见selection-v2-review.md。此为真实实现/验收变化，已重新check及内审；旧报告不追改，不当实际领域通过。

最新权限政策接收：已完整阅读external-review-permissions.md与新增AGENTS段，共同指令SHA `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`、当前AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`匹配总控。已实际向独立agent透传全文；记录见external-review-permissions-receipt.json。ZCode yolo/MiniMax bypassPermissions默认获准，实际任务进入时仍读回模式；当前未启动两应用或改其配置，未扩大桌面/付费/密钥权限，不因政策本身重测。

构建责任回执：已全文读回I05→T03四文件生效协议并核对execution-state。pyproject/uv.lock/build-engine/entrypoint后续仅T03维护；T11共享需求文档已注明按此路由，未修改/接管四文件，未采用未批源码/锁/包验。CI/resources等不随四文件转交，完整平台签名/配置和T01/T10接口仍待具体交接。

当前恢复入口：`recovery.json` 固定最新私有实现/测试/验收提交 `7d28fdb27c0aac39ed7df1f9fd5fa0f127b5d9f4` 及65/695/1052验证和最新内审报告哈希；前述ffa0972/50a3212为历史阶段，不用于恢复当前候选。后续仅追加本恢复回执，无实现或验收变化。AGENTS保持未暂存，尚未推送；完整目标和原门禁继续。

格式基础责任回执：已全文读回I05→T01 Python四文件生效协议并核对execution-state，协议与登记SHA一致。JobStore/coordinator/Python入口/合同及既有storage基础由T01负责，T11恢复/迁移证据的接口需求按此协调；公共canonical/main八文件未自动转交。详见format-python-ownership-receipt.json及共享接线请求。此次仅责任路由文档更新，核验器/测试/验收基线未变，不重跑无变化测试、不重开产品内审；完整候选、真实设备/签名/模型/真人及正式门禁仍待具备。

当前阻断审计：前两轮为官方活跃总控句柄的50秒有界等待，本轮再次核实相同T11依赖/资源缺口，连续第三轮无可推进的授权工作；Goal工具已实际返回blocked。总控仍为active/inProgress，不把观察超时当终止。私有候选/检查/内审保留，未重跑无变化测试；最新阻断依据与恢复条件见blocked-audit.json。等待批准的正式接口/配置或真实验收资源变化后续接原完整目标，不将局部工具完成当发布完成。前文active均为历史阶段记录。

新交接通知接收：I06→T01 canonical七文件/main engine八文件已实际生效，协议全文与登记hash核对一致；恢复接口责任路由已更新，见format-public-ownership-receipt.json。此前“尚待八文件交接”为历史记录。此次只转未来维护权，不证明精确SQL/JSON已批准、格式3 ready或T11依赖具备；Goal工具当前仍blocked，私有实现与既有验证不变。

共同指南责任同步：已在安全边界全文读回b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39，实际计算原第九节及无桌面段hash仍分别为1f57a08e…d4b54、5215df2e…551d，AGENTS仍78df2825…a759。旧9717/df090快照保留。已将责任追加通过send_message发给完成状态的独立agent，未触发新任务、不声称其读回；详见operating-policy-receipt.json追加记录。仅责任政策变化，无实现/测试/依赖/验收/资源变化，Goal保持blocked，未重测/重启/重开外审。

## 2026-10-23：指定 Z 报告收件与 M 续接准备

原工具产品候选仍为 `7d28fdb27c0aac39ed7df1f9fd5fa0f127b5d9f4`。Z 原 session 新 turn 已核真实 completed，183行报告已全文收件并保全原字节、Write关联、设置/范围及日志hash；审者自述工程范围通过，6项建议仍待处置，不能当双审或发布通过。M当前精确sid为网络错误50113/failed、processing已结束，尚无正常完成；只准备397B短继续，等总控后续短lease及fresh核再发，本次未发送。详见 `zcode-received-20261023/owner-reception.md` 及索引；旧failed/aborted、此前未发送回执均保留，不推断重试操作者或触发来源。Q5方案已交总控集中询问、用户仍待答；本次未benchmark、未改产品或既有验收，原Goal与全部发布门保持。

## 2026-10-23：M 单次正常续接后真实完成

在总控显式短GUI交接下，仅向原M session正常发送一次短继续，立即释放；应用canonical正文396B仅去源397B唯一尾LF。新turn `2bd54f89-0d87-4cce-b126-fb91175019ae` 后台已核assistant stop、runtime idle/agent completed。最新375行50693B报告已全文收件，审者工程终态仍NotPass，12项意见全部待处置；Z已收的工程Pass自述及6项建议不覆盖M不通过，不成立双Pass。旧failed/aborted、旧非正常终态报告的可核重建原字节和本次受理/终态证据均保留，见 `minimax-continue-20261023/README.md`、`minimax-received-20261023/owner-reception.md`。Z自述读另一提示的规定与最小Read证据另核，仅证读本方准备索引，正文Read未独立证实，不绝对宣称无违规。冻结产品/验收未改、未重测产品、Q5仍待用户答复，原Goal及全部发布门不变。
