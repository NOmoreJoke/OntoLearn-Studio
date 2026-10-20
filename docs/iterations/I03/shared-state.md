# I03 U1 项目、任务、结果和分页

契约先冻结语义，不选前端状态库。权威来源为主进程应用服务与引擎持久记录；完成度见 [status](../../reviews/I03/status.md)。六模块共用同一项目服务和以下身份，不能各自保存一个可变项目副本。

## 数据与查询 key

| 对象           | 身份/字段                                                                                                             | UI 缓存与更新规则                                                                                                                                  |
| -------------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 项目           | projectId/projectRevision/inputSnapshotId/dependencyVector/formatVersion                                              | `(projectId,revision,snapshot)`；正式 commit 成功后刷新权威投影，不把本地草稿计入正式 revision                                                     |
| 任务           | 全局 jobId、operationId、输入、参数摘要、真实依赖、实现来源、stateVersion、limits、状态/结果/错误/时间/提交进度       | `(projectId,jobId)`；按 stateVersion 单调更新。刷新/重建查 job.get，不重复 job.create                                                              |
| 结果           | 全局 resultId；project/job/kind/definition/snapshot/inputRevision/scope/parametersHash/vector/集合摘要/implementation | `(projectId,resultId,inputSnapshotId,scope,parametersHash,dependencyVector,definitionSetDigests,implementation)`，不以页码或可变 kind 代替结果身份 |
| current 指针   | `(projectId,kind,definitionId,scope,parametersHash,implementation)`                                                   | 查询需获取完整当前元数据；I04 将此逻辑键规范化哈希成 S1 内部 kind，不改 S1 历史身份                                                                |
| 编辑草稿       | projectId+baseRevision+editorId+draftId                                                                               | 仅 client store；刷新不覆盖未提交草稿，收到新 revision 显式冲突/重新预览，不静默覆盖                                                               |
| 选中/展开/过滤 | projectId+viewId                                                                                                      | 仅 client store；不伪造源真相，不影响后台任务生命周期                                                                                              |

输入参数正文保存在可校验内容寻址的 immutable blob，parametersHash 同时用于 cache key 和请求绑定。I04 必须验证 hash 对应正文及引用所属项目；不能接受一个从未保存的摘要当作真实参数。实现来源三键与 S1 一致，公开 dependencyLockHash 收紧为 SHA-256；既有测试锁字符串仅属于内部 spike，不冒充公开结果。

切项目、窗口重建或正式 revision 更新时，先增加本地 generation，撤销旧订阅；迟到更新即使 job UUID 相同也不能写当前页面。后台任务不因卸载误报取消。旧运行仍可在其输入分组查看；新 revision 下迟到的完成只能更新对应历史 job，不能用 completion 通知替换当前结果。U1 不自动重算或自动重发写操作，M1 业务流程决定用户入口。

## 真实依赖、过期与兼容

`dependencies.json` 是唯一能力选择策略，可信执行计划从 S1 不可变快照派生，客户端不提供任意 dependencyVector。`deriveDependencies` 是集合选择/显式引用闭包的纯契约算法，不是本体执行器；definitions 投影由 I04 校验快照并构造。每项实际引用必须可解析；定义有环允许去重遍历，悬空拒绝。所有正式事实依赖只能为 facts:asserted；不能虚构 facts:某主体以逃避过期。

| 能力           | 必须实际读取的依赖                                                                                                                  |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| asserted 查询  | facts:asserted、所选 query、所有 ontology 与 mapping 身份；query 显式引用闭包                                                       |
| 含推导查询     | 上述+所选实际推导的 rules/ontology/mapping/输入向量；校验 derivedResultIds 同项目/同输入/范围/实现且可用，合并真实依赖，不能只拿 ID |
| SHACL asserted | facts、所选 constraint、ontology/mapping；包含推导时再合并实际推导依赖                                                              |
| 推理           | facts、全部 ontology、mapping、受控 rule；包括启停状态，禁用规则的状态变更也需重验                                                  |
| 映射提交       | 所选 mapping 与输入/sourceHash/身份规则版本、ontology、已有 facts/所有权；正式提交仍经过 ChangeSet/预览/确认                        |
| ChangeSet      | baseRevision、完整预览计划与引用、所有用到的定义和现存 facts/所有权；保守读取所有定义集合以做引用检查；不生成领域结果               |
| 行为测试       | 显式行为、facts、ontology/rule/behavior/mapping 集合和事件/参数/输入消费记录；仅隔离副本                                            |
| 场景运行       | 所选 scenario、facts、ontology/rule/behavior/mapping 集合、显式场景初始状态/事件/资源/指标/参数；runConfig 绑定规则/行为版本        |
| 对比/报告      | 用户显式选择的各不可变结果的依赖并集与输入分组；不混合为单一 current。报告先 pin 后固定，多结果引用必须同事务成功                   |

逐定义版本不覆盖“集合中增加新定义”的变化。因此每次使用所有 ontology/rule 等集合时，保存有序完整身份列表与 `(id,version)` 内容摘要为 definitionSetDigests。空集合也保存摘要，之后新增首条规则仍可检测。规则/本体新增、删除、启停或显式引用变更，服务必须在与 Store.commit 同一事务内重验集合并标记受影响结果；这是 I04 必须新增的 Store 发布/失效入口扩展，现 S1 只处理已登记版本向量，不能单靠现有 publish 证明完整能力失效。集合摘要不是虚构的版本键，也不新增 staleReason。

集合变化产生所属 family 的既有码：对集合前后身份并集逐项比较，不存在版本按0；新增首条需确保正式版本≥1。依赖集合变化而已有版本未变的定义变化必须随定义版本推进，不能让摘要变而原因无定位。每项原因仍为 `{code,dependency,before,after}`；集合增删对应具体新增/删除定义键，保留完整前后集合证据。I04 若做版本升级须保留旧结果历史来源并验证跨项目/新集合/空集合反例；此要求未实现前不得开放依赖集合的业务能力。

staleReason 码仅取自 S1 invalidation-v2.json：ontology/facts/mapping/constraint/rule/behavior/scenario/query 八类。模型配置变化不产生领域原因；历史、失败、取消、实现不兼容不是原因。多个真实上游可有多原因，before≠after；无关定义不应产生原因。派生载荷本身不变，当前性与过期元数据是可更新投影。

保留 S1 严格发布：新发布的 snapshot.projectRevision 必须等于最新 revision，且实际依赖与集合都未变才可成为 current；即使只发生无关元数据或模型提交，旧快照新发布仍只是 historical，该 kind 可以没有 current。已存在 current 不因无关变化失效。实现三键不一致默认隔离 current/cache，禁止未经等价性测试的兼容复用，不把实现升级标为领域过期。

结果 current/stale/historical 与任务 succeeded/failed/cancelled 分开。载荷可被回收但 resultId、输入、依赖、原因和来源保留，payloadStatus=evicted；不能返回成功空页。历史使用 historicalSelectionRequired=true，重跑/报告必须显式选择历史快照。取消/失败场景保留轮次历史但不能发布成功 current。用户明示删除历史与恢复场景属于后续业务入口，缓存维护不删除历史/定义/源真相。

## 稳定分页与游标

resultId 指向一次不可变载荷；重算必须新 ID。装载结果时固定 rowId 与 ordinal，排序为 `(ordinal,rowId)` 升序且严格唯一，重复值行也必须不同 rowId。空结果为 rows=[]/nextCursor=null，元数据证明成功可用；不要用 evicted/失败冒充空集合。单页遵守协议字节/行/格限额，遇单行无法容纳时返回受限错误/详情，不无限重试或截断成成功。

result.page 首次 cursor=null，必须带完整 binding：projectId/resultId/inputSnapshotId/scope/parametersHash/order。后续 cursor 是服务生成 UUID，查询服务端 cursorRecord（不能信客户端自造游标正文），记录同 binding、pageSize、上次稳定键和过期时间。每次先检查当前授权、项目归属、结果可用，再核对所有绑定字段及页大小；失配/篡改/未知 token→CURSOR_MISMATCH，到期→CURSOR_EXPIRED，载荷清除→PAYLOAD_EVICTED。游标记录与载荷生命周期由服务协调，不因 cursor 存在便自动 pin 历史。

下一页只取严格大于最后 `(ordinal,rowId)` 的行，并按两个上限截取；`nextCursor` 对应本页最后实际交付键，不使用不稳定 offset，不跨结果新版本。到期后从同一不可变 result 重新开始，不暗换 current。游标令牌不授予读权限。重复请求同 cursor 在载荷可用期返回同页，页大小改变拒绝。

job.list 也不能用可变状态列表作 offset：初次 `(listSnapshotId,cursor)=(null,null)` 创建有界 TTL 的不可变列表快照，按 `(createdAtMs,jobId)` 升序固定成员及当时 DTO；过滤 all/active/terminal 绑定在快照中。后续两个身份都必需，绑定项目/过滤/排序/页大小，失配/到期同上述错误。新任务或终态变化不重排已创建列表；UI 要最新状态另外 job.get 或重新 list。列表快照是只读投影，不替代 jobs 权威状态。实际 TTL/记录上限由 I04 有界资源验证决定并明示，不无限留存。

正式写任务的不可变收据采用 result.kind=receipt，只能 state=historical，不能查询为领域 current；收据引用 operation/marker 的完整持久证据，UI 显示“已提交”与 revision，而不冒充查询/推理成功。取消、页和列表响应另按原请求绑定校验；job.list 对成员项目/唯一性/过滤/稳定顺序和请求页大小均检查。jobListCursorRecord 明确绑定固定列表身份、过滤、页大小与最后(createdAtMs,jobId)，与结果 cursor 分开存储。

契约派生算法采用有界迭代遍历，最多4096个定义投影/4096个真实依赖键（包含 facts:asserted），环去重、悬空引用拒绝；不依赖语言递归栈深度。超出该安全上界由应用服务映射 RESOURCE_LIMIT，不代表 Q5 业务容量线。job/result 向量必须含 facts:asserted，空项目可为0；project.get 的正式项目版本投影仍允许空向量。staleReason 每个 dependency 最多一条，before 必须等于结果保存的输入版本；只有跟踪了对应定义集合、before=0 且 after≥1 时才允许旧向量没有该新增成员键。不得伪造无实际依赖的过期原因。
