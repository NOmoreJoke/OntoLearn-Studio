# 固定案例与 I04 真实通道联验内审

2026-10-21（Asia/Shanghai）。独立 agent `/root/t09_prd_audit` 只读复核；不代替指定双审。

新增测试将四套 G.0/E.5 输入经批准 JobStore 的真实 rollback-only prepare_plan → 原 I04 test.atomic stdio coordinator/实际隔离 worker → operation.get / result.page → SQLite 重开完整读回。输入/课程/manifest 与 `51cdc0e` 完全一致，未改共享 Store、协议或业务注册表。

## 首跑不通过及修复

首跑 4 失败、3 通过。提交本身已经成功，随后的 project.get 超时。开发者与独立 agent 分别复现：T09 私有 seed helper 用 `G-base:ontology` / `G-base:initial` 等包装定义 ID，造成版本向量 `ontology:G-base:ontology` 违反批准 dependencyKey 格式。Store 的内部形状接受并不能证明公开 Project DTO 合法。coordinator 真实响应校验失败并关闭会话，之前仅 Store 测试未覆盖此边界。

只修改 T09 私有 helper，将包装 ID 改为协议允许的 `G-base.ontology` / `G-base.initial` 等，不放宽共享契约。增加空项目及重开后 canonical Project DTO、完整依赖向量、预览零正式写入、收据与完整状态断言。保留首跑失败原文的字节 SHA 和无损归档。

## 修后实际结论

7 项新增真实通道测试通过；加原35项共42项专项通过。独立 agent 又实际重建四套临时项目，canonical Project 投影均通过，并明确回执：**“通过修后当前 T09 范围的独立内审，无剩余阻断项。首次失败原因已关闭，不替代指定双审。”**

覆盖四套成功输入、旧预览实际执行拒绝且保留已有用户数据、真实 worker 失败无半提交/无成功收据、产品模式拒绝 test.atomic。重复同 operation 返回原终态，不多写；最终当前事实、定义、来源源文本与摘要，以及提交前后快照全部完整读回。

这是基础设施联验证据，不能关闭正式领域执行、学习 UI、分阶段证据契约、T01 学习记录持久化、T08/T10联验、真人验收或产品上线。完整check最终结果另见本轮验证摘要。
