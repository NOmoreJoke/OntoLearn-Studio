# T01：私有应用 CAS 与混合事务合同

## 可执行入口与状态

显式 JobStore(target_format=3) 的 trusted-main 内部 `prepare_application` / `apply_application` 复用唯一连接、全局 operation_claims、既有 job_plans/confirmations 和 Store.commit；没有新增 writer、公共方法或协议3运行入口。默认格式2保持原路径。学习记录、辅助审计和完整应用恢复尚不受理。

已实现动作：metadata 的 name/archived/mode（guided/assisted）；draft.save/delete/restore。元数据按 project version，草稿按持久 editor generation 做 CAS；同内容保存、对空项删除仍推进 generation，删除保留 header，JSON null 与删除区分。boundDomainRevision 可以是过去真实域版本，不能指向未来。草稿恢复从已验证的先前完整 checkpoint 取内容，但推进当前 header，不能重用旧 generation。结果刷新不参与草稿写入。

## 准备、确认与受理

动作可附原 Store 域计划，形成 combined。combined 与 draft.restore 必须实际准备/确认；trusted-main 的普通元数据、自动保存/删除可直接提交，不为逐次自动保存制造 Job 或模态确认。

准备 envelope 为 `{preparedApplicationVersion:1,projectId,actor,plan}`，ref 为完整 envelope 的 canonical digest。plan 绑定 change、完整应用 before/after、声明资源前后 CAS 和可选真实域预览（base、kwargs、fingerprint、前后 state/control）。既有确认行绑定 project/ref/base/planHash/actor/write。普通 Job 域计划是另一精确形状和 ref 派生；共享表不允许凭据跨类型消费。create_job 在分配 claim 前核对类型、完整 hash/ref 和确认；重开/原任务重试使用相同验证。

apply 的全局 claim 固定 project/kind=application/job=NULL/context 及完整 context fingerprint。context 绑定 public/internal project、operation、请求、actor/permission/确认 refs 和计划。已有 operation 先核原请求，再沿真实历史链返回原 receipt，不重算当前 CAS 或新计划；换 actor、项目、动作或凭据不能接管原 operation。Job 与 application 共享全局 operation 命名空间，发现旧无 claim 的提交/round/receipt 也拒绝收养。

## 一个事务与三个哈希

应用 claim、实际域提交（如有）、声明资源 CAS、sequence、checkpoint、receipt 和 head 同一外层 SQLite 事务。combined 的原域 marker 使用真实 NULL job，只有实际 application claim 与精确原域指纹可进入该路径；旧默认2仍拒绝 NULL job。域分支不另发应用序号/receipt。纯应用变更复用 domainSnapshotRef，不动域 revision/vector/result/current。

三种哈希分别绑定不同内容，不能混用：claim fingerprint 绑定完整 context；receipt planHash 绑定 resolved 应用 plan；combined marker fingerprint 绑定原域计划。写入前核完整已确认 before，其他 editor 的后续改变会使旧完整预览拒绝；实际只写声明资源，不用旧 after 覆盖无关内容。

## 历史与读取

私有 project_operations 以 afterSequence/固定 throughSequence/limit 分页，后续新增不挤入既定上界。legacy 缺失项如实记未记录。checkpoint/receipt 从真实 origin/genesis 沿 operationSequence 连续验证，核 beforeRef 链、允许效果、CAS、真实 claim 和域 marker、收据、无多余 CP/receipt 及 live head，不能靠任意 JOIN receipt 给伪 checkpoint 洗白。draft.restore 目标必须在已验证先前链中。

故障 hooks 覆盖 claim、combined 域、state、sequence、checkpoint、receipt 及外层提交前后；四类故障包括真实子进程退出。提交前失败要求完整库不变，提交后丢响应按原 operation 重开对账。Store3 DDL/schemaHash 本轮未改。正式能力、同版 ready/hello、UI/学习/导入导出仍按状态文件推进，不由本内部合同推定。
