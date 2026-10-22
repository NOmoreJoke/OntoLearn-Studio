# T02 request B：I06 正式 App／bridge 供方核对

结论：本交接没有可批准 T02 C5 拼入的 I06 本体编辑 gateway。批准基线与保留 I06 候选的完整 preload／App 表面均未接入本体编辑；保留候选只可按固定字节只读参考，不能把模型外发授权、既有 Job 查询或 TypeScript 类型当作本体 typed ChangeSet 的写权限。此结论限定在所列 I06 固定输入，不判断未审的 T01 后续实现。

逐文件 ref／path／bytes／SHA、实际方法表与生命周期位置见 [interface-supply.json](./interface-supply.json)。原批准基线为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；保留 I06 产品 `e2c269ad78a78e1a042cadc93b1c81a874707153` 的完整源码／证据 ref 为 `1f3b053d8a69d1f7ddb1e29c143f648d910fe689`。`e2c269ad…→1f3b053d…` 的 apps/packages 差异为空；真实 Git ref 只证明材料身份，不构成采用许可。

## 实际接线

| 环节 | 固定 I06 源码实际提供 | T02 本体链尚需的正式供给 |
| --- | --- | --- |
| get | 当前项目、Job、结果／分页、operation，以及模型状态／字段目录／outcome 的命名调用 | 完整当前 domain＋metadata／全部支持／public-internal 身份的可信投影；按 ID 读取不证明权限或当前性 |
| typed proof | `DesktopBridge` 类型及 task update 校验 | T02 私有 Preview 不等于 T01 持久 planRef／previewHash／sourceBinding；不能由 TS 类型、同形对象或 hash 自授权限 |
| 确认 | `confirmModelAuthorization(contextId, previewId)` 为模型外发范围取 grant | 正式完整 Diff 的人工确认与原事务内再核；模型 grant 不可充当本体编辑确认 |
| Job | 已有 Job 查询、取消、订阅、恢复；另有模型解释 start | 接纳真实 T02 输出的原 typed ChangeSet Job；现有查询与模型 start 不证明该入口 |
| commit | 四个 I06 桥／App 文件无本体 commit 接线 | T01 原 preview／确认／Job／Store.commit 路径及 source/base/权限复验；不在 I06 新造提交权威 |

保留 I06 preload 的完整方法表在 `interface-supply.json`；新增十二个方法均为 `*Model*` 模型解释范围。App 的“本体构建”等 module 名是展示结构，不是 OntologyPage 路由。`env.d.ts` 仅声明 `Window.ontolearn?: DesktopBridge`。

## 项目、generation、取消与恢复

固定 I06 App 中已有 TaskView 的 generation／project／stateVersion 检查、connection epoch 与不确定状态清理；恢复调用 `restoreTasks`，卸载时取消订阅。结果摘要在 await 后核 generation，健康检查还核 epoch。ModelPanel 以 projectId 为 key；模型上下文／隐私／配置／选择变动清除模型 preview/grant，重选前亦先清除。模型取消只能停止本地等待，不能撤回已发送内容。以上分别是既有任务与模型解释行为，不能代替本体草稿／来源证明／确认生命周期的实测。

历史同 ref 的 T01 当前负责 main 源码也仅作为只读证据：TaskService L94–108 的可信 main `selectProject` 决定项目；L292–319 在 await 后核 generation/schema/关联 ID；L398–400 明确取消响应只是当时快照，L518–541 退订不等于取消；L724–725 的 `operation.get` 是查询。三份合同／main 原件已固定 SHA，不据此重新授予 I06 写权或采用权。

本体链应按固定 T02 计划绑定可信当前 source、public/internal project、revision/vector、metadata／完整支持、planRef 与 previewHash，在确认、Job 接纳及 commit 原事务中复验。项目／session 变更、晚返、旧页与取消不得恢复写资格；revision 变化保留输入但禁用旧预览。响应丢失按原 operation/receipt 对账，恢复不能自动确认或另建 Job。这些是接口要求，本交接未实现或运行该链。

## 可读规范与未批准实现

“request B”沿当前总控委派命名；本次未发现固定 T02 文档中同名字面标题，对应的是 typed plan 的 S4 与 interface-handoff 正式端口请求。

T02 固定 C5 为 `e5ad54e5762157cafe532c2a0c07c22e8dd737cb`。其 `docs/iterations/T02/typed-changeset-integration-plan.md` 为 44243B，SHA `6b88b1f7a8e9b7b08719f6b48dda16905a3eb800a7b8baef21f4b7a26b06983c`：L3 明确尚未取得采用、供方实现或运行授权；L19–24 区分私有 Preview 与原 T01 能力；L51–55 仍请求可信投影；L153–161 规定 S1/S2/S3/S4 及纯适配器。其建议首切片和预算不能当作已交付产品。C5 的 Unicode 诊断修复也不新增 App／bridge。

当前唯一 ownership：T01 负责 `main/index.ts`、`main/task-service.ts`、`main/jsonl.ts`、`renderer/src/task-presentation.ts`。I06 仅余 preload、env、App、style 及获准私有模块；旧文档“I06 main／余六”表述不能重新授予 shared 路径。

下一供方动作由 root/T01 固定获批 S1/S2 的完整投影、复验与预算合同及实现 ref，再单列 canonical/named engine/current host scope 与 I06 App/bridge 入口的精确采用范围。T02 保持纯翻译，不 whole-commit、不借未批准 helper、不直接引入 I06 gateway。T01 后续是否已实现，须以新的固定供方 ref 和批准记录证明，本交接不从历史材料推断。

本轮只做 Git／hash／文本静态核对；未改产品、shared 四文件或其他候选，未启动 GUI、安装依赖、运行产品／native／探针。独立复核与归档清单另附。
