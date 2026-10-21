# T04 已批准读取 bridge 的客户端接入

此文件说明 `renderer/src/query/reader.ts` 的私有渲染端适配，不新增 IPC、公共 schema、项目 writer 或执行器。它直接使用批准 base 的四个命名方法：`getResult`、`getResultPage`、`getJob`、`cancelJob`；不增加 query.execute 可用声明。

## 接线责任

App/main/preload 仍属原唯一维护者。主应用取得真实 `restoreTasks()` 的 TaskView 后调用 `reader.bind(view)`；后续主应用已有的 `onTaskUpdate` 回调将原事件交给 `reader.receiveUpdate(update)`。两者均再用批准 `isTaskUpdate` 校验；不从 URL、renderer 自报 UUID 或 fixture 取得项目权限。generation、项目、输入 snapshot 或 revision 改变会废弃旧读请求；同绑定恢复仅更新原选中 job 的有效新版本，不随列表切换其他任务；不本地推断 staleReason，不把旧状态继续标 current。

`reader.snapshot()` 只是可丢弃的显示快照：每次复制、最多一页载荷。未保存查询草稿仍保留在页面/T01 草稿责任内，结果刷新不覆盖草稿。主进程和引擎持久状态始终是依据。

## 结果与分页

`read(presentation,pageSize)` 的 presentation 是内部页面元数据，含同一 pageBinding、列名、实际已执行 SPARQL（原文保留，不 trim 改写）。**必须由后续批准的查询定义/结果适配器取得，当前正式来源仍缺失**；不能把当前编辑器文本、模型文本或固定样例放进 presentation 冒充实际执行。该类型不是第二份公共结果协议。缺来源时不调用 read、不启用 App 结果流程。

读取先经 `getResult` 获取实际 query metadata，复验项目/result/snapshot/scope/parameters 的完整绑定；缓存回收时保留历史身份，不请求缺失载荷。随后仅 `getResultPage({resultId,pageSize,cursor})` 请求一页，复用批准 page schema/绑定/有序行校验。新读或切项目后的迟到响应不会发布；元数据/分页校验失败按批准 INVALID_REQUEST 的 identity/cursor 字段给受限说明，参数校验使用 params；任意原始 bridge 异常只转换为固定 INTERNAL_ERROR，不显示原文。

`nextPage(cursor)` 只接受当前页实际返回的 nextCursor；重新读取元数据后再取下一页，不能复用当前编辑器范围或自行发行 OFFSET 游标。最后非空行的 ordinal/rowId 锚点跨空页保留，跨页重复/倒退行或自循环 cursor 拒绝，客户端始终只保留一页。不替代引擎游标发行/过期/绑定和全结果正确性验收。

父组件在请求开始与完成后分别读取 snapshot 更新 React 状态，将 phase=loading 映射为 QueryPage.resultLoading；ready.result 直接映射 result。旧项目/已卸载请求返回 false 时不得给新项目套用旧 error/结果。将安全 error 用现有 explainError 展示；不要抛出 raw IPC/异常文本到 UI 或日志。

## 任务与取消

`refreshJob(jobId)` 仅接受同项目、严格有效且 capability=query.execute 的真实 job；旧 generation、旧 stateVersion、乱序选择不会覆盖新选择。`cancel(jobId)` 发送取消前再读取 job，其他能力/错项目/终态不发送取消；同一个 in-flight cancel（含 ACK 后真实任务重读阶段）不重复投递。

取消 ACK 经批准 result_job.cancel schema 与 jobId/stateVersion 检查后，只记录 cancelRequested，不将 job 改成 cancelled。当前 job 的 ACK 最低版本跨再次读取、通知及取消前查询保留，再 `getJob` 读取不早于 ACK 的真实状态；仍 running/cancelling 就等待真实终态。父组件将 cancelRequested 与同一 jobId 映射为 QueryPage.cancellationRequest，显示“已受理，等待终态”，不伪造成功/已取消。切项目/连接失效使旧回调失效，不撤销已经可能送达引擎的取消；恢复仍据真实记录。

`dispose()` 仅释放本客户端显示状态并废弃回调，不自动取消 worker、不重放查询或保存。主应用自己的订阅由其已有生命周期负责，禁止无差别取消共享订阅。

## 验证范围

`tests/unit/t04-query-reader.test.ts` 用明确标注的合成 transport 故障样例验证客户端竞态/身份/分页/取消边界，公共 DTO 来自批准 validator/fixture；不调用真实 query executor、不计真实业务集成。SSR 探针验证 loading 与绑定 job 的取消请求提示。实际 I05 query.execute、T01 保存事务、完整 Q-01/02、外联拒绝/取消/游标、App 挂载及父功能验收仍待批准依赖和共享接线。
