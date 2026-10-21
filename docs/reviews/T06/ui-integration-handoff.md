# T06 UI 与行为服务接线交接

当前两个独立候选：S1产品61396a598b2dffc1d3d2fd4660f9af1d5c93d266；UI产品571b4d64120c8420d527f9fda2a3cb81bbd47d3f。均以批准5f910b5为base。UI树为 /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui，feature/T06-behavior-ui。它没有装配App或调用公共bridge。UI独立复核进行中，不以此交接签收组件或真实集成。

父开发线实际读回UI源码/verification：7源/测试/验证脚本SHA及11份本地证据SHA全部匹配；git只有保护AGENTS dirty。开发线完整check为651TS（本线21）/1052Python；真实headless交互/1440与390截图已生成，父线另查看390viewport。夹具不是实际引擎结果。

给T00/T01/T05/T07的具体接线条件（私有类型不是已批准公共合同）：

| 项目          | 当前两端实际表达                                                                                            | 接线须落实                                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 导航/草稿     | UI BehaviorWorkspace接收context/catalog/initialDraft/onDraftChange；同项目刷新保留草稿，换编辑行为需key重建 | 由App唯一维护者装配；保存/版本冲突/重开恢复使用唯一Store；草稿回调不能当已保存                                             |
| 定义范围      | UI编辑一个draft；S1计划接收完整行为集合                                                                     | 宿主读取同版本全部启用定义，以编辑草稿作明确覆盖；不得只传单行为而漏掉B05跨行为竞争                                        |
| 条件          | UI equals/exists/type；S1原生has精确值或always                                                              | T05/T06批准无损映射或扩展后才启用；exists无值、type推导不可静默丢弃或把手工事实当真实推理                                  |
| 事件          | UI有序数组id/type/标量payload和add/remove/set事实变更；S1还需sequence/version/edits及对象注册               | 数组位置确定sequence，version来源固定且重投不变；未知节点/创建/删除有批准RDF适配；不能用requestId作为事件内容版本          |
| 动作          | UI create/class、update、relate、notify；S1 create.initial/set/add/notify                                   | create与其类型初始化仍算一个源动作；single update/multi add分别映射；禁止拆分动作改变上限/轨迹；动态表达式不隐式推断       |
| 范围与消费    | UI context有project/input/behavior/scope，S1还需run/round/base/consumption                                  | T01提供真实隔离快照、operation/job/inputSnapshotRef及同事务消费/状态/轨迹保存；scope标签不能作权限证明                     |
| 推理与轮次    | S1始终committed=false，需事件后冻结推理；UI区分candidate/completed/failed/cancelled                         | T05提供真实current/版本与完整依据，T07接资源/轮末推理提交；只有真实隔离事务收据才completed+committed；计划不升级为轮次成功 |
| 结果/刷新     | UI严格zod，request/project/input/behavior/scope与原runId校验，保留草稿                                      | 正式受限结果适配及分页须批准；action index零基，页面加1；完整facts/Diff/通知/原因来自实际输出，不用expected预填            |
| 失败/取消     | S1内部evidence含domain诊断；UI只固定错误枚举，本地说明                                                      | 白名单映射内部诊断为受限结果，禁止直接转发evidence/原异常；cancel callback必须真实已取消终态，接受请求不等于收尾           |
| 版本失效/历史 | UI由宿主提供freshness及版本原因，拒绝迟到回包                                                               | 依据正式失效表，不由UI猜测current；历史只读与当前结果分离；Agent读取同一真实服务                                           |

UI具体私有类型/回调/草稿生命周期和待接线责任见该树 behavior/README.md、model.ts。现有共享App/env/style/main/preload/contracts与Store职责不变，本线未擅自写入。正式合同、适配路径与所有权批准后，在新独立集成候选实现并按原需求做真实事务/推理/Agent/UI验收和同版指定双审；本交接不授权复制第二套公共契约或Store。
