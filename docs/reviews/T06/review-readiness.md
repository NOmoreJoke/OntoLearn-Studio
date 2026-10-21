# T06-S1 当前冻结候选与指定外审入口

当前产品候选 **61396a598b2dffc1d3d2fd4660f9af1d5c93d266** 已完成新全仓检查和完整本地独立复核，待总控实际核验后派发指定双模型任务。旧 e81cfc9/567ab48 的就绪或通过仅适用于其历史版本。

## 精确版本及完整范围

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior`
- 分支：`feature/weekly-t06-behavior`
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 产品候选：`61396a598b2dffc1d3d2fd4660f9af1d5c93d266`
- 后续仅有自有流程证据提交；流程 HEAD 以总控实际 git rev-parse 为准，产品路径须与上述候选 diff 为空。保护 AGENTS 保持未暂存。
- 完整 12 项产品来源及 SHA、base→产品完整二进制 diff 哈希/文件清单、命令、日志、审查与固定输入记录：`evidence/validation-61396a5.json`。
- 完整 diff 可重现：`git diff --binary 5f910b52c69d86a1076b2032e5d3c63e715947f3 61396a598b2dffc1d3d2fd4660f9af1d5c93d266`。同时审阅 base→实际流程 HEAD 的全部自有文档，不以本摘要代替完整范围。

受审范围是 behavior/ 三个源码、四份 test_behavior 测试、私有 fixture 作者脚本及完整 JSON、docs/iterations/T06/ 三个接口/适配/探针文件，以及全部 T06 审查与证据。包括 prepare_events/PreparedRound/plan_behaviors、事件身份与消费 scope、冻结推导绑定、四层排序、跨实例任意单值竞争、同值幂等、源动作粒度 create.initial、通知/模板、详细失败位置、完整候选与 Diff/轨迹、固定输入加载/编译/投影和严格 RDF 子集。不是只有旧两个源码的审查。

批准 T09 输入仅固定 Git `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380`，manifest SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`，版本 prd-v0.6-learning-1；17 文件/PRD/manifest 已按固定字节核验。out 下只读导出是缓存，无复制公共 fixture 或导入 T09 Python。九例完整比较通过仍使用人工推导，product_runtime=not-executed、formal_acceptance=false。

## 当前实证

- npm run check 实际 exit 0：15 TS 文件 / 630 TS 测试，1174 Python 测试（含 122 行为测试），lint/格式/类型/构建/ruff 通过。
- 完整本地独立复核通过：local-review-6.md；前五份报告和原始失败记录保留，全部历史问题逐项关闭。
- 当前固定九例 B-01/02/03/04/05/06/09/10/11 的完整 facts/orders/notifications/action 顺序/消费和精确冲突比较通过。输出原件及当前运行哈希见 manifest，未把 expected 当 Store/runtime 结果。
- 没有公共业务注册/Store 写入/真实推理/GUI。未 push/PR/CI/合并或生产验证。

## 指定外审门禁

总控已在 I05 两原任务实际终态并全文读回后，将两审查应用独占时段转交 T06-S1；这不是当前候选已获指定外审通过。必须先由总控核验上述新版本、完整 diff/source manifest、dirty 状态，再派发 **ZCode GLM-5.3/最高** 与 **MiniMax Code M3.1-Flash/xhigh**，双方各自新建独立完整只读任务，不互传同轮意见。当前未启动任务、无句柄，不伪造报告。

实际核实应用/任务/模型/版本与会话权限：ZCode permission.mode=yolo；MiniMax permissionMode=bypassPermissions。完全访问不改变只读评审职责、无桌面约束、支付/密钥等边界。权限来源为总控 external-review-permissions.md 与当前 AGENTS/共同指令。无主动 GUI/e2e/native/HMR。

要求两报告：来源/设置、worktree/branch/base/产品与流程 HEAD、完整范围、实际命令/结果、未验边界；每项发现严重度/位置/触发/影响/证据/建议，历史问题处置，明确通过/不通过/无法验证。需审完整集合/顺序及边界负例，不以数量替代。两任务实际终态后全文读回处置。预留 `round-1/zcode-glm53.md`、`round-1/minimax-m31flash.md`，尚无结果。实现/测试/验收变化后重新验证并双方新完整任务；本地 agent 不能替代。

## 完整 FR-600–604 后续仍在本聊天推进

| 拥有者  | 仍需批准的真实输入                                                       | T06 后续                                     |
| ------- | ------------------------------------------------------------------------ | -------------------------------------------- |
| T01/I04 | run/round/inputSnapshotRef/operation/job、取消，同事务保存消费/状态/轨迹 | 原子提交、失败/取消/迟到与重开读回联验       |
| T05/I05 | 事件后真实推理、版本/current 与完整 RDF 交接                             | B-03 新增、B-04 删除依据和失效联验           |
| T00     | 行为正式业务方法、受限错误/分页、权限/取消、具体接线路径                 | 公共唯一维护者接线，行为页和工具共用实际服务 |
| T07     | E.2 资源/轮末推理/指标/提交执行器                                        | B-07 与完整 G.3 验收                         |
| T08     | 实际 Agent 工具与失败表达                                                | B-08 真正页面/工具结果联验                   |

UI 已按新授权独立推进：agent /root/behavior_ui，独立树 T06-behavior-ui / feature/T06-behavior-ui / base5f910b5，仅 renderer/src/behavior/ 和 tests/unit/t06-*.test.ts。它不在本冻结树与外审范围，不把私有组件当公共接线已成；待其交付后另行独立复核与真实接口联验。

Goal 保持 active；纯服务与父模块分别记录，不缩小成功定义。指定双审与相应验收通过后才 push/PR，再实际 CI/正常合并。
