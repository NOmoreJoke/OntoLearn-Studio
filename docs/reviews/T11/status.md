# T11 发布与整体验收状态

2026-10-21（Asia/Shanghai）。阶段：private_implementation_validated，独立 Goal 保持 active；完整T11尚未验收。

- 会话：01a15bc2-4551-7b51-8453-add1943f3b6e；仅负责 T11。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-release`。
- 分支：`feature/weekly-t11-release`；启动base/head：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 启动实际 git 状态：仅 ` M AGENTS.md`；这是总控同步规则，保持未暂存，不进入产品提交。
- 指南 SHA256：`db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与共同指令一致。
- 远端 develop 实查为同一 base。分支保护 API 返回 HTTP403（private repo 计划限制）；未证明服务端保护启用，不绕过原流程门禁。
- 独占新增：`scripts/release/`、`tests/unit/t11-*.test.ts`、`tests/fixtures/release/`、`docs/reviews/T11/`、`docs/iterations/T11/`、`docs/release/`。
- 不改共享 package/lock/builder/build/CI/main/security；不写总控 state/tasks。

已实现：严格manifest v1与离线核验器，候选/版本/锁/安装文件格式/哈希/签名公证/许可证/渠道一致性检查；T09唯一manifest及G完整预期引用；外部freeze固定时间、模型评估、全部检查预期、恢复快照和上一版资产。提供双平台只读取证脚本、设备验收流程、恢复/双向迁移规范、周六至少5真人主持脚本与空观察表。

实际验证：45个T11合成正反例通过；最新 `npm run check` 通过675个TS测试、构建、ruff及1052个Python测试；sources核对12份归档；被既有release忽略规则排除的脚本另做显式lint/格式检查，Mac shell语法通过。Windows脚本仅静态审阅，未运行。T09只读对齐17文件/50用例/3指针，观察时head及manifest哈希见 `t09-readonly-alignment.json`，未采用为批准依赖。

独立agent内审首轮及残留复核发现的预期自证、空壳快照、冻结时间回填、当前包冒充旧版及真人完成矛盾均已修复，最终复核通过，见 `internal-review.md`。该结果不替代正式指定双模型审查。失败原件与重跑日志保留本树ignored的 `*.log`；提交摘要和哈希见 `verification.json`，未把失败覆盖为通过。

下一交付：按 `docs/iterations/T11/shared-file-handoff.md` 由总控完成唯一owner交接；待完整批准候选、真实资源后接线与联验，重新冻结base/head、双方指定新审、门禁push/PR/实际CI/正常合并/远端核验和最终下载实装。当前只作可恢复本地阶段提交，无推送。

本地实现提交：`ffa0972800d6cb14910c43c185bfdd4dcf96d629`，19个授权新增文件。提交后仅AGENTS为总控同步的未暂存修改；源实现与最终内审核验器哈希一致。后续仅追加本回执，无实现/测试/配置/依赖/验收基线变化。远端develop本轮末次实查仍为启动base，未push/创建PR/申请GUI资源或发布。Goal保持active，不能将本阶段提交标为T11完整完成。

续跑新增：专项正例现实际经过合成E.5 exact/replay引用，新增缺失对象/数组指针、引用文件漂移及同数量错误完成对象4个拒绝用例。核验器/CLI/collector字节不变；新增测试已独立只读复核通过，全仓check再验通过，原始结果在pointer-unit.log/pointer-full-check.log。完整目标逐项证据与缺口见 `completion-audit.md`；没有新的共享接管或真实资源证据。上述“后续仅追加回执”描述的是764d690当时，当前测试增量将另作本地提交，正式双审仍需最终新同候选。

仍缺完整 P0 同候选、目标干净设备、有效签名/公证、最终下载渠道、真实模型/API资源及真人预约；总控已集中询问，T11 不重复询问。不运行本机 Electron/native/e2e/HMR，不触发凭据提示，不签名/公证提交/发API/外发/购买；正式接线、双指定模型新同候选审查、push/PR/实际CI/合并及发布另按原门禁继续。

操作政策接收：已在安全边界全文读回新共同指令及本消息附带的第九节/无桌面段；共同指令SHA `9717f699…19880`、第九节 `1f57a08e…d4b54`、无桌面段 `5215df2e…551d` 均与总控给定值匹配，完整值及实际执行约束见 `operating-policy-receipt.json`。保留原Goal、分支和50a3212实现/测试候选，未改冻结原件；未因政策追加重跑测试或重开产品审查。当前无实际额度告警，未查额度、消费重置或新增支付；独立审查子agent已完成，无自有本机GUI任务待撤回。此补充不授予共享文件、GUI、凭据、外发或付费权限，也不证明发布资源到位。
