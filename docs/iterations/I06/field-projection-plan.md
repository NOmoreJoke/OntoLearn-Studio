# I06 有限结构化字段投影阶段

2026-10-21；原会话/Goal/worktree/feature不变，接续1911ce1，批准develop仍5f910b52。两处protected AGENTS hash仍db1fb184；完整Goal含第九节及最新scope/state/parallel-coordination已接收。无额度告警，不消费重置或付费。本机不启动窗口/凭据提示，不操作审查应用；本轮不新增平台测试。

## 原需求与边界纠正

FR-902/S3要求每次最终授权、载荷和实际接收配置检查；PRD D/F允许明确选中不可变历史版本。选定版本、读取时状态、历史标记与实际失效策略必须真实；不承诺发送瞬间仍current。只有另行作出持续current增强承诺时，Store/socket lease才是候选方案，不把它或历史语义重新批准列为原S3自动阻断。

A-03必须在真实链证明选中字段授权后，工具其他列及其不允许派生值不进入下一请求。它不要求整个M1 CSV追踪，也不要求必须I05或恰好两项新API。当前批准I04的真实 result/job/全页 rows 与主进程固定有限字段模型足以建立本阶段可信映射；所有模型只由可信main构造，不来自renderer或工具自报。

## 可行接口和唯一责任

- 根新增 `main/model-gateway/stored-field-projector.ts`，维护同目录 `gateway-application.ts` 及确有需要的 source 私有接口；专属I06测试/fixture/文档。source仍只调用批准 project.get/result.get/job.get/result.page，复用真实 coordinator/worker/Store，不加RPC、不直接读项目DB。
- 模型先按固定producer capability、definitionId、result kind、完整implementation匹配唯一main策略，tag只校验形状；模型版本和完整内容摘要绑定字段scope，严格列数。每个静态字段声明index/type/label及有限依赖。未知模型、歧义、列数/tag不符、非scalar、额外结构/超限或未知依赖整体拒绝，不推断自然语言“是否干净”。
- `getFieldCatalog({resultId,selection})` 从实际source.load建立main拥有的catalog；`selectFields({catalogId,fieldIds})` 只接受目录中的身份，重读并重建允许字段字节。目录绑定具体result/job及完整来源；字段范围绑定实际项目/资源定义/输入版本/参数/实现/固定模型与该字段实际值及依赖，可在同源同版本且同值的新工具结果复用授权。普通hash只是比较，不代替这组真实映射和读取许可。
- 任意 `deriveFromMaterials({text})` 不能用于字段材料；`projectFromFields({inputs,kind})` 不收text，只从已证明允许的结构化投影重建tool/history/summary/error。输出不得带完整结果正文/摘要、未选列label/value或未选字段派生值；外发只包含有限来源身份、读取时状态、已选字段和值。依赖字段未明确选择时拒绝相应派生字段。
- 文档agent在独立I06-field-scope-docs/feature分支（base1911），唯一维护narrow-interface-draft/examples、main-integration-handoff、stored-result-plan的范围纠正；不写根实现/status。独立只读agent审查设计/实现/真实反例。总控已通知精确14文件交接生效，见shared-owner-acceptance-20261021.md；I06负责约定contracts/main/preload/UI文件的S3接线。其余Python Store/job/worker、入口build、锁/CI/安全恢复仍未移交。

## 验收

合成fixture先经实际I04 worker写入同时含public/private/private-derived三类标记的结构化Store结果；main只选择public field并明确确认。之后实际第二次worker工具返回完整列，同源同版本允许字段投影复用原grant，实际receiver检查完整请求bytes中private及private-derived标记零出现。覆盖tool/history/summary/error固定重建与混合任意text拒绝、额外字段/whole-result扩权拒绝、端点/配置变化、local-only、取消/释放、受影响重试及重定向；全部失败保留来源与哈希。

本阶段是M0有限字段工程证明，不外推所有producer/CSV/任意业务语义。正式main/窄bridge/UI、真实产品保存/可用导出日志排除/窗口失败隔离、适用I05语义、平台事实披露与指定双方同版全范围审查仍保留；不将本阶段结束当整个S3完成。
