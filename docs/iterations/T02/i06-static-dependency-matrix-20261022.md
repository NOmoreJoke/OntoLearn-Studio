# T02 对 I06 App／bridge 固定交接的依赖核对

本次所列批准基线与保留 I06 源码表面未提供本体编辑 gateway；模型授权、既有任务读取和恢复不能充当本体完整 Diff 确认或 typed ChangeSet 写入口。该结论仅覆盖交接中的固定 I06 输入，不判断 T01 新 C1 或其他后续实现。正式采用仍需 T01／总控的新固定供方收件及精确路径授权。

T02 已实际核对 16 项固定 Git blob 的大小/SHA，完整 preload 方法表、相关 App 生命周期源码及保留产品到 fullsource 的 apps/packages 空差异。批准 base 为 `5f910b52`，I06 保留产品 `e2c269ad`、fullsource `1f3b053d`；本次仅只读材料，不采用、import 或运行产品。

来源及全部 SHA 见 [I06 读回](../../reviews/T02/interface-intake-20261022/i06-source-readback.json)。供应方交接目录在本次读取时未被其 Git 跟踪，不能将其 workspace HEAD `b22a36fd` 冒称该文档包 ref。T02 已精确保全七份文档快照（README、供方 JSON、四输入 manifest、原独审、closure、两份格式日志），并核对 manifest 四项；固定源码 ref 和文档快照 hash 分开记录。原 I06 独审与 root 接收仅证明其有界静态交接，不是 T02 产品或运行通过。

## 已有表面与待供给合同

| 环节                   | 固定材料可确认的事实                                                                                                                          | T02 仍需的正式供给与联验                                                                                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 当前读取／页面入口     | 固定 preload 有 getActiveProject、Job、result/page、operation 读取；新增十二方法均为模型解释。App 的“本体构建”是模块展示，未接入 OntologyPage | T01 的可信当前全量 domain＋metadata／来源／全部支持／显式引用投影，公共/内部项目身份及版本绑定；随后由获准 I06 bridge/App 接入真实本体页面。按 ID 读到对象不等于当前性或权限       |
| typed proof            | DesktopBridge 和 task update 校验存在                                                                                                         | 指定真实持久 planRef／previewHash／sourceBinding 与固定 schema 的采用范围；T02 私有 Preview 或同形 TS 对象不能授予写权限。预览、确认、Job 接纳及 commit 原事务中分别独立复验       |
| 人工确认               | confirmModelAuthorization({contextId, previewId}) 为外发范围生成模型 grant                                                                    | 本体完整 Diff 的真实人类动作与原 T01 确认入口；renderer 的 confirmed=true 或模型 grant 均不能代替。恢复与晚返不能自动确认                                                          |
| Job／提交              | Job 查询、取消、订阅、退订、恢复和模型 start 已有；固定四桥/App 文件没有本体 commit 接线                                                      | 原 T01 typed ChangeSet Job／唯一 Store.commit 的完整合同、整批原子性与预算/来源/基线复验。查询、operation.get 或 startModelExplanation 不证明存在本体写入口；不另造第二权威        |
| 项目／generation／连接 | App 已有 generation/project/stateVersion、connection epoch、迟到结果过滤和不确定状态清理，卸载退订；这些属于既有任务/模型解释                 | 对真实本体草稿、投影、preview 与确认链联验：切项目/session、revision 改变、断线/恢复、晚返、取消都不得恢复旧写资格；版本变动保留输入但禁旧预览。既有局部守卫不能冒称已覆盖新本体链 |
| 取消／响应丢失／恢复   | 历史 TaskService 的 cancel 响应是当时快照；退订不是取消；模型取消不能撤回已发内容                                                             | 使用原 operation/receipt 对账确定实际终态；恢复不自动重放确认或新建 Job。提交前取消/失败的零写与提交成功后 receipt/undo 分别验收，不拿旧快照推最终结果                             |

## 当前唯一责任与后续请求

- T01 当前独占 `apps/desktop/src/main/{index.ts,task-service.ts,jsonl.ts}` 与 `apps/desktop/src/renderer/src/task-presentation.ts`。I06 交接中历史“main／余六”不能恢复写权；T02 不写这些共享路径。
- I06 剩余桥／页面责任为 preload/index.ts、renderer/src/{env.d.ts,App.tsx,style.css} 及已获准私有模块；仍须总控对未来本体接线逐路径另授，不是本次实现或采用许可。
- 请求 root/T01 按其新固定供方单列 S1 全量投影、S2 独立复验／确认／Job／原事务 commit 与预算合同、所需 S3 metadata，以及 S4 canonical／命名 engine／当前 host scope 和 I06 入口。T02 保持纯翻译，正式 schema/adapter/采用由唯一 writer 收口，不 whole-commit 或借未批准 helper。
- 本体导入／序列化仍按 [I05 依赖矩阵](i05-static-dependency-matrix-20261022.md) 分域处理；模型草稿进入同一预览和不可自确认的 T08 接口另待固定回报。不能用任一局部交接拼成父功能已完成。

本次只增加接口文档及文档快照，未把 I06 源码复制到 C5，未安装依赖、运行产品/native/GUI 或修改 shared 路径。C5 产品 e5ad、两树 HEAD 7c52、原 130 输入及完整 R2 提交正文不变；本表不放入两审查树，不改变排队与双新审／父验收／CI／远端门。
