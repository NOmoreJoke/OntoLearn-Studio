# ADR-0003 草案：v2、任务和共享读取契约

日期：2026-10-20。状态：待指定双模型设计审查；采用状态仅在 I04 实际验证后决定。交付与审查进度见 [status](../../reviews/I03/status.md)。原 S1/S2/U1 计划逐字输入及 SHA-256 见 [sources](../../reviews/I03/inputs/sources.json)。

## 决定与理由

Python 协调器作为任务状态唯一写者，使用与 S1 相同 SQLite 事务及提交证据；Electron 主进程负责可信来源、授权、订阅和引擎监督，不另存第二份权威终态。worker 只处理不可变输入与隔离工作区，不获得独立正式数据提交入口。协调器必须验证 worker 返回值、检查取消边界并在唯一 Store 提交边界发布。

采用严格版本化 JSONL 信封、按方法参数和结果、独立 request/job/operation/session/订阅身份、固定错误码及受限定位参数。任务创建快速返回持久 job，通知只作提示，job.get 是重连权威来源；页面卸载只解除订阅。只有 registry 已实现且验证的条目可声明，业务 UI 与 Agent 从同一注册表派生窄入口，授权仍需逐次检查。

项目读取以正式 revision 和不可变 snapshot 绑定；计算结果以独立 resultId 绑定输入、范围、参数、真实依赖、实现来源，采用不可变顺序分页。定义集合增删也影响依赖，集合清单摘要与逐定义版本一起由可信快照派生。严格保留 S1 的最新 revision 发布资格，不用无关提交污染领域 staleReason。

## 交付位置

- [protocol](protocol.md)：逐方法契约、限额、握手、路由、结构化错误。
- [jobs-and-storage](jobs-and-storage.md)：状态、持久归属、S1 故障与交接逐项映射。
- [shared-state](shared-state.md)：U1 项目/任务/结果身份、真实依赖、过期、分页及草稿边界。
- `packages/contracts/v2/schema.json`：唯一规范结构；`registry.json`：唯一能力元数据；`dependencies.json`：真实依赖选择策略；`states.json`：状态边。
- TS/zod 与 Python 纯校验适配器共同消费相同 JSON 和成功/失败语料。本迭代保留现 v1 health 调用路径，v2Runtime 为空；I04 接线与实际验证后才更新。

## 拒绝的替代与后续条件

不采用“主进程和引擎各自推断终态”：进程退出或响应丢失时无法证明提交是否发生。不接受客户端自报依赖：可漏报规则、本体与来源变化。不只用 TTL 缓存或 offset 分页：无法保证版本与稳定集合。不把密钥/最终模型发送塞入 Python：I06 继续拥有主进程网关边界。

I04 必须完成 [验收映射](acceptance.md) 的运行列，包括真实 JSONL reader、常驻复用、有界队列/worker、原子 job/marker 对账与 I02 窗口联验。定义集合失效、job 表、确认计划存储和内部 S1 字段→公开 DTO 转换均须实际实现后才能开放相应注册项。未验证的参数上限是本版契约安全上界，不是容量或性能承诺；Q2/Q3/Q5/Q6/Q7/Q8/Q9 保留原决策边界。
