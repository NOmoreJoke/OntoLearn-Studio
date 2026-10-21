# T05 质量与推理状态

## 真实身份

- owner：开发聊天 `01a15bce-021c-74e0-a7ac-a899380b424a`；独立 Goal active，未重建。
- worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-quality-reasoning`。
- branch：`feature/weekly-t05-quality-reasoning`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，本轮远端 develop 实查一致。
- 保护 `AGENTS.md` 保持未暂存；启动 SHA `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`；总控追加政策后实际读回 SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。
- 独占质量 Python/UI、`test_quality_*.py`、`t05-*.test.ts`、quality fixture、本线 docs；没有改共享 Store/contracts/bridge/semantic/resources/依赖锁或 root 状态。

## 当前实际交付

私有局部实现已完成，准备可恢复本地提交：

- 五类约束模板严格校验、规则类型/属性存在/值比较/合取/多结论编辑校验；拒绝多余字段、未绑定变量、不支持构造、未知引用和schema属性输出。
- 不可变定义/快照上下文的稳定执行计划，固定先 RDFS、规则统一读冻结输入、输出不反馈。保存顺序不改变计划，潜在链保守提示且不删/禁用已保存规则。
- 完整事实集合比较、显式依据 DAG 结构校验、推导新增/撤回/多依据变化比较。只处理传入观察，绝不构造推理结果。
- 独立约束/规则编辑、样本/预期草稿、版本/范围/结果状态、三分级/定位、actual差异和依据展示页面。尚未挂到 App；正式检查按钮禁用，草稿明确未校验/保存/执行。
- 私有 G.2 输入及领域预期，V-01/R-01–06/O-01 各自重置；`001` 保持字符串身份。尚缺批准真实执行器的全actual/trace集合、完整RDFS闭包oracle。总控随后实际批准T09固定873c8c0输入，下一步单独校验17输入并补本线适配测试，不消费T09未批准服务。

## 实际验证与审查

首 `npm run check`：633 TS / 1094 Python 全通过。内审发现并修复日志泄露、隐藏约束参数拦截规则、id/label及依赖键 surrogate 原始异常；独立 reviewer 对修复后完整范围明确通过，49 Python/5 Vitest，随后同版全check 635 TS / 1101 Python通过。

自主对照I05报告后补常见 datatype 模板 IRI，增加4回归；最新定向53 Python通过。末次独立完整复核明确通过（仅私有准备），最终全check退出0：635 TS / 1105 Python，详见 verification.md / internal-review.md。真实错误、首失败和各次输出本地保留，未覆盖。

只有一个开发者写实现/测试，独立 `/root/t05_internal_review` 只读，未争写或开启GUI；不替代指定 ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh 双新完整任务。指定外审资源仍由总控预约，未 push/PR/CI/合并。

## 正式集成缺口与下一步

批准基线的 reasoning.execute / validation.execute 仍 design-only。T01需正式确认/持久化constraint/rule定义与唯一ChangeSet流程；I05需批准同版真实执行器并补FR-505通用比较/多结论；T00需唯一协议/Job/result/分页/取消/导航接线。精确成功/失败样例、原要求正反例及I05报告差异见 `docs/iterations/T05/interface-proposal.md`，已实际发给总控。

真实失效/重算、完整V/R/O、空白项目创建保存修复、真实依据、T06/T08/T09/T10联验、指定双审/CI/正常合并/远端及父功能全部P0保持。下一步在已批准依赖与owner接口明确后接入并真实联验，刷新实际develop再冻结最终外审候选；不因无关M0未完成停止独立工作，不以本次局部测试关闭父任务。

## 操作政策接收与执行

总控消息附带第九节及无桌面约束已全文读取接收：第九节 SHA `1f57a08e909e9d49a6e2c2d6e7012beec3e22b8e3c9e8eacad22c84dfb2d4b54`；无桌面段 `5215df2ead4745e7d74f137c4fa6ac837a54114590b5dee2d83cd16bb728551d`。默认执行权限新段已实际读回并透传独立reviewer，ZCode yolo / MiniMax bypassPermissions 不改变只读和资源预约职责；旧Goal/计算不重启，AGENTS不stage。

本线只有无窗口 CLI/unit/build，未跑本机 Electron/e2e/native/HMR，未操作审查应用/配置、读取secret、发真实模型请求/对外消息或新增费用。没有额度告警或重置。未运行的包内/GUI/真实运行/生产验收均未记通过。
