# I03 任务、持久记录与 S1 对账

规范字段在 schema.job/commitProgress/runConfig/changeSet；状态边唯一来源 states.json。状态进度见 [status](../../reviews/I03/status.md)。

## 唯一持久归属

协调器应用服务唯一写 job 状态，SQLite 为真相。主进程只有 pending、授权、订阅和可丢弃缓存；worker 无权判定最终发布。I04 必须在 S1 Store 内增加 job/operation 记录和事务入口，不能维护第二个 JSON 文件或另一数据库。持久表的最小约束如下：

| 记录                     | 唯一性、状态及事务约束                                                                                                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| jobs                     | jobId 全库主键；project/operation/capability/inputSnapshot/参数/真实依赖/实现/limits/createdAt 不变；stateVersion 每次状态改变严格增加；同一次事务改变 state/error/resultRef/updatedAt/finishedAt |
| operation_claims         | operationId 全库唯一；project/job/capability/planHash/base 不变。创建接受前原子登记；同身份同内容返回原 job，异项目或内容 IDENTITY_CONFLICT                                                       |
| commits/commit_evidence  | 复用 S1 正式数据事务内 marker/projectRevision/planHash/前后快照；终态可与 marker 同事务持久化或在恢复时按 marker 修复，绝不能有数据提交无 marker                                                  |
| runs/rounds/run_terminal | 复用 S1 不可变输入/逐轮快照/operation/job 标记与一次性终态；任务引用同项目 run，不能另存独立可变“已提交轮数”                                                                                      |
| subscriptions/cursors    | 传输投递身份及有限期只读游标记录；从不决定任务终态；游标/列表快照跨连接可恢复，权限每次复验；到期明确拒绝                                                                                         |

operation.get 只查当前已持久 marker，null 表示本次读未发现 marker，不证明仍在执行的事务永不会提交。重连恢复先取得相同项目的写入序列化权、确认旧 worker 已退出或 fenced，再查 marker 并恢复 job；不得在未隔离旧写者时重发。S1 commit marker 当前 project 范围、round operation 为全库；I04 operation_claims 统一全局约束，不能假定现有 S1 自带跨项目 operation 唯一性。写请求超时的 UI 显示“状态待对账”，不直接显示未保存。

## 状态机与取消线性化

| 原状态                     | 允许新状态         | 必要条件                                                                                        |
| -------------------------- | ------------------ | ----------------------------------------------------------------------------------------------- |
| queued                     | running            | 已持久接受，输入锁定，获得资源                                                                  |
| queued                     | cancelled          | 未启动/未提交，取消已持久                                                                       |
| queued                     | failed             | 接受后恢复无法安全启动或资源初始化失败；保存固定原因                                            |
| running                    | cancelling         | 取消请求已持久；仅确认受理                                                                      |
| running                    | succeeded / failed | 完整任务输出与终态证据持久后成功；故障按已提交点失败                                            |
| cancelling                 | cancelled / failed | 未提交部分已回滚或终止隔离单元，已提交点从 S1 读取；收尾失败为 failed                           |
| cancelling                 | succeeded          | 完整最终结果/提交及终态证据在线性化取消前已经持久化，恢复后才观察到取消；部分轮次不构成完整成功 |
| succeeded/failed/cancelled | 无                 | 重复 get/取消/终态写入只返回已有证据，不是新状态边；异内容冲突                                  |

schema 按状态限制 resultRef/error/finishedAt；成功 resultRef 指向同项目不可变结果（写任务可用提交收据结果，不能把收据登记为领域 current）。失败必有白名单错误，其他状态 error=null；取消不伪造 error。commitProgress.mode 是 none/atomic/rounds，能力注册表决定，不允许非轮次携带假轮次。atomic 的 marker 在未提交时 null，已提交时包含 revision/前后快照/planHash。rounds 的 committedProgress 零轮显式 null，已有轮次为 runId/lastCommittedRound/snapshotRef。job.cancel accepted 不承诺立即取消；已终态返回 alreadyTerminal 与原 state/version。超出取消收尾期限时隔离 worker 可被终止，但不能杀整个协调器或回滚已经提交的事实。

运行 schema 以内容寻址 parametersRef/eventsRef/初始快照/消费记录引用、规则/行为版本、实现来源固定重放输入。每个事件的 ID 在场景内唯一；触发实例是 eventId+behaviorId；重复事件不得重做动作。E.1/E.2 顺序和动作上限纳入 runConfig。全部条件基于同一行为前冻结快照；同阶段不同实例写单值不同值失败，同值幂等但保留各实例其他动作；同实例按动作序号、跨阶段按状态转移。行为产生事件只进下一轮。运行能否 replayable 还必须验证 blob 齐全、声明语义实际支持、输入与逐轮来源一致；只通过 schema 不足以宣称可重放。新运行需显式快照，不自动续跑。

## S1 故障逐项映射

| S1 故障/竞态                                                   | job/operation 读取和恢复                                                                    | 禁止行为与 I04 验收                                                  |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 提交前取消/异常/磁盘失败/退出                                  | 无 marker；数据/版本/所有权/失效保持原值；取消有持久请求则收尾 cancelled，否则 failed       | 不按异常文字判断提交；fence 后复核 marker；两类正式写任务都测        |
| 事务中（data/ownership/invalidation/marker/before_commit）故障 | SQLite 全部回滚，恢复只见最后正式状态；job failed 或已确认取消                              | 不留半批；run 当前轮同样无 round/snapshot/marker 副作用              |
| 提交完成、返回前取消或响应丢失                                 | marker 和数据同时存在；同 operation/job/plan 返回原证据；全任务完成且终态已持久才 succeeded | 不能盲重发或把已提交事实说成没发生；取消后 UI 明示已完成             |
| 零轮取消                                                       | committedProgress=null、cancelled、无结果发布                                               | 不能伪造 lastRound=0/snapshot；正式事实不变                          |
| 部分轮次完成后取消/worker 崩溃                                 | 保留最后完整 round/snapshot；cancelled/failed；当前未提交轮次回滚                           | 不以“已有提交”当 succeeded、不续跑、不发布取消的运行为 current       |
| 最后一轮提交后终态尚未提交就崩溃                               | 检查 run_terminal/最终结果证据，不能仅凭 max round 或最后轮 marker 推断全任务完成           | 尚缺最终完整证据则 failed 并保留轮次；重新执行要新显式输入/operation |
| 完整最终提交+终态已持久后取消                                  | 原终态 succeeded，不倒退；cancel alreadyTerminal                                            | 对比上项，不把轮次完成等同全任务完成                                 |
| 新 revision 时旧任务迟到                                       | 结果保留 historical，即领域依赖未变化也不得盖新 current                                     | 不伪造 staleReason；同 kind 可无 current，提示基于当前重跑           |
| 依赖已变时旧任务迟到                                           | 保存旧输入、准确 staleReason；不更新 current                                                | 按实际依赖/集合重验，不能仅比 TTL 或客户端向量                       |
| 协调器退出/主进程或窗口重建                                    | 所有 pending 为传输失败，重启有限退避；查持久 job/marker 重建，不重放写任务                 | 窗口销毁不取消 job；I02 实际集成后补原生重连验收                     |

按项目串行正式写入，同一事务 Store.commit 或 Store.commit_round 受唯一协调器提交闸控制；只读任务使用不可变快照。不同项目可有界并发；有限队列满返回 QUEUE_FULL，不创建未登记或无限待处理任务。心跳/取消通道不能被 worker 计算阻塞。有限退避建议 250/500/1000ms，连续三次失败进入明确离线，用户可显式重试；I04 实测再冻结配置。

## I01 交接闭环与错误映射

| 历史意见                             | I03 处理与 I04 接入要求                                                                                                                                                                                                                                     |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| N-R3-1 / F3-01 kind=None/空/int/bool | publish/current 共用非空字符串守卫，真实 SQLite 测 results/current 零写入、合法身份只保留一个 current；既存 NULL/空键须显式拒绝并保留数据修复证据，不能假报无结果                                                                                           |
| N-R3-2 current provenance            | 同 publish 三键非空字符串守卫，非法 None/list/int/缺键抛形状错误；合法未找到才 null                                                                                                                                                                         |
| F3-02 legacy 非对象 config           | commit_round 在写前检查对象，统一 ValueError；真实旧记录反例核对完整数据库 dump 无变化；服务映射 INVALID_REQUEST field=config                                                                                                                               |
| F3-03 全库缓存/报告固定顺序          | collect_cache 是全库维护，当前不增加项目清理 API；主进程显式全库范围确认，不向 Agent 暴露。若将来增加项目清理须单独 schema/授权与跨项目反例。报告先验证可用并在同事务 pin 全部，再确认报告；并发清理先发生则 pin 返回 PAYLOAD_EVICTED，报告不能宣称保存成功 |
| F3-04 人工值删除恢复                 | before_snapshot 保留原人工值；恢复 managed_value 是放弃人工漂移。恢复人工值必须从历史读取、重新生成显式 edits、预览、确认、当前 base 复验，不是覆盖/修改旧 marker                                                                                           |
| F3-05 ChangeSet 顺序                 | 固定 definitions→remove→edits→manual→mapping，与 JSON 键顺序无关；同 fact remove+edits 净效果为 edits。预览必须以同顺序计算，mapping 冲突仍阻断整批。移除未知事实保持可审计 no-op                                                                           |
| F3-06 facts 依赖                     | 仅 facts:asserted 项目级真实依赖；范围是展示选择，不创造主语细粒度版本。新增/撤回定义集合由 shared-state 的单独摘要机制处理                                                                                                                                 |
| F-07 提交后投递失败                  | 传输失败不等于提交失败；凭 operation marker/planHash/job 恢复，不自动新 operation                                                                                                                                                                           |
| F-11 / R4 / N-07 锁与 I/O            | 只按 sqlite_errorcode 主码识别 BUSY/LOCKED→STORAGE_BUSY；IOERR/FULL/READONLY/CORRUPT→STORAGE_FAILURE。提交相关错误附可选 operationId，并先恢复对账。禁止匹配/传递 exception 文本；未知异常→INTERNAL_ERROR                                                   |
| N-06 重复 finish_run / pin           | I04 在服务事务内先查既有证据：同 run/status/evidenceHash 终态返回既有记录；异内容 INVALID_STATE。同 result/report pin 返回原固定记录；evicted→PAYLOAD_EVICTED；不同结果固定到同报告需明确报告清单，不能篡改旧固定内容。S1 内部一次性 SQL 不直接暴露         |
| R6 历史增长                          | 保留已提交历史和快照；差分/压缩/容量留真实负载/Q5，不以删除历史补齐性能                                                                                                                                                                                     |

Conflict 的基线/身份/所有权类别必须由 I04 结构化内部异常分类得出，不能把含原值的消息解析为 DTO。KeyError→NOT_FOUND 使用固定 resource 枚举；ValueError→INVALID_REQUEST 仅经调用上下文选择固定 field；其他 SQLite constraint 先验证幂等身份，未分类者 INTERNAL_ERROR。I03 的内部守卫仍抛固定 ValueError，不提前将 storage.py 变成协议处理器；真实 Python→主进程→bridge→UI 链路错误传播在 I04 完成并验证。

job DTO 还完整保存不可变 `input` 与 `confirmationRef`。input 包含 definitionId、derivedResultIds、preparedPlanRef、snapshot/scope/parametersHash；外层重复字段必须与 input 一致。job.create 成功响应逐字段绑定完整 input 与确认身份，不仅比较参数摘要。operation_claims 的幂等指纹覆盖完整 input、确认、capability、project/base 和计划；同 operation 更换查询定义、派生输入或准备计划必须拒绝，不能返回另一次输入的 job。

## 运行结束与未处理事件（E.2 / FR-701 / FR-704 / G.4）

`job.succeeded` 表示运行已按选定规则结束且最终证据持久化，不表示所有事件已经处理。达到 `maxRounds` 且仍有待消费事件可以正常结束，但必须显示“存在未处理事件”；动作超限、冲突或执行失败须按 E.2 失败，保留此前已提交轮次，不能用正常达到轮次上限掩盖失败。

I04 将终态摘要纳入 `scenario` 不可变结果 payload，沿已有 `job.resultRef → result.get → result.page` 读取，无需新增业务方法。该 payload 的第一行保留为 `run.summary.v1` 摘要，cells 按固定顺序为 `["run.summary.v1", runId, lastCommittedRound, snapshotRef, reachedMaxRounds, hasUnprocessedEvents, pendingEventCount, eventConsumptionRef]`，均使用既有 row 的标量值类型。成功场景摘要的 lastCommittedRound 至少为1，snapshotRef 与最后已提交快照一致。零提交失败/取消只显示已有状态与 committedProgress=null，不生成成功摘要、不增加零轮成功或提前停止规则。eventConsumptionRef 指向该次运行锁定输入及已消费记录的内容寻址引用，不能使用任意路径或业务正文。摘要必须与同项目持久 run/round/terminal、job.commitProgress 和结果来源一致，不能从进度百分比或 UI 缓存推算。

`pendingEventCount` 是最后已提交状态下的待消费事件队列长度，`hasUnprocessedEvents` 必须等于 count>0；不是工单 backlog、未解决告警数或业务成功率。reachedMaxRounds 依据该次冻结 runConfig 和持久终态原因。UI 在 pending=true 时显示“运行已结束·存在未处理事件”；pending=false 只说明该队列为空，不能声称所有业务问题解决。failed/cancelled 的 job.resultRef 为 null，按已有状态及 committedProgress 展示保留轮次，不能假定 pending=0 或发布成功 current。该摘要是未来场景 payload 的保留布局；I03 通用 row/schema 校验器只检查结构及上界，当前并未实现场景执行、摘要生成、引用真实性或页面业务解码。

I04 接入验收须实际覆盖：maxRounds 到达且仍有事件、队列耗尽正常结束、零提交失败/取消与 committedProgress=null、失败/取消保留已提交轮次、摘要与 job/run/snapshot 不一致、摘要缺失或畸形、payload 被清理。缺失/畸形/矛盾摘要视为不可用结果，不展示“全部处理完成”；已清理 payload 按 PAYLOAD_EVICTED，不伪造摘要。分页读取仍绑定原不可变 resultId，摘要只在首个非游标页面出现，其后页面不得插入第二份摘要。未选择的提前停止规则不在此添加。

内部 S1 kind 仍按既有非空字符串身份保存。I04 从内部 kind 到公开有限枚举须显式白名单映射或拒绝未知值；不 trim、大小写归并或合并既存身份，避免把不同 current 键静默改写。全库 legacy-kind 扫描保留；I01 R6 历史增长及其原等级维持开放/延期，真实负载测量、修复政策和任何存储优化另由 I04/Q5 承接，不宣称已有性能问题或收益。
