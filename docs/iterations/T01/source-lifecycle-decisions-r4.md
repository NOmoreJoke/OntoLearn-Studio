# T01 来源生命周期选择 r4：终态、对账与计账补充

仅设计决定，不启用 source wire、配额、GC、公共业务3或 ready。保留 [r3](source-lifecycle-decisions-r3.md) 原件；本文只消除其重复 append 的状态歧义，并落实总控复核 §4/5/7 的边界。未改实现、既有验收或 owner 责任。既有已批准写入、取消、历史保护及完整验收不减少。

已全文读取总控 `iteration-control/2026-10-21-weekly-release/source-lifecycle-r3-design-review.md`，SHA256 `e95cadb6c655749e36b64b196e0aa71185dff5213be403f80b33a3f737c51846`；r3 SHA256 为 `46c422c2b928d68aa4758601e6972979f424f3503524631f6beee03517cdcbc9`。本次共同指令 SHA256 `ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff`，不因 worker 单文件未来维护生效扩大协议、资源或其他文件授权。

## 1. 关闭 R1：逐状态处理 append

以处理该动作时同一 coordinator/writer 的权威状态及期限为准，不以发送方缓存状态或动作抵达 main 的时间代替。

| 权威状态                                                      | append 决定与可证明的回包                                                                                                                                                                 | 状态及资源影响                                                                                                                           |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| receiving，未到期且原块字节仍可核验                           | 新块仅接受 expected index/offset；旧 ordinal 只在原完整 descriptor、session/project/upload/selection/phase/代次、index/offset/decodedLength/chunkSHA 和 bytes 全等时返回原已证 append ack | 首次块耐久且进度原子登记后才确认；精确重复不重写、不再次推进、不增 pin、不延寿                                                           |
| sealed，尚未正式 accepted                                     | 不再接受 append，包括旧 ordinal；仅 status 可只读返回 sealed 的已封存身份、进度和原固定期限。需要核验封存内容时走独立受保护读消费者                                                       | 不返回可被解释成仍 receiving 的 append 成功，不重做 seal、不签发新 lease/接纳资格；被拒 append 不改 sealed 内容或寿命                    |
| released / expired / cancelled / 清理中或已清理               | append、续传及同 attempt 重新 begin/seal 均明确拒绝；status/release 可只读返回已知权威终态及清理是否 settled                                                                              | tombstone 不需要保留 raw bytes；不以 hash 相同冒称逐字节核验，不复活、不分配新 upload、不返回 append 成功                                |
| accepted / committed，或传输索引已终止但有真实 accepted claim | append 不再接收；传输 status 最多给出真实 accepted 关联或其受限状态，正式结果通过原 operation/Job/receipt 对账                                                                            | 冲突 append、重复 seal、旧 release、lease 到期及传输清理均不得撤销 durable Job/context/pin 或改写 committed；取消只能走正式 Job/提交排序 |

receiving 的冲突 descriptor/块可以按 r3 终止尚未接纳的 upload；这一决定与 admission 在同 writer 排序。若 admission 已先完成，后到冲突只能拒绝传输动作，不能再按“未接纳冲突”撤销 Job。sealed 采用上表的全 append 拒绝选择，避免把只读内容校验和活传输幂等混成一个入口。

exact duplicate 的原 ack 可能含较旧 nextIndex。main 必须先核原 request、attempt/upload、session、selection/phase/代次及 ordinal；不同 context 的迟到 ack 丢弃，同 context 的旧 ack 只结算对应未结请求，不覆盖更新的权威进度。进度不能回退，终态不能被旧 receiving/sealed ack 复活；若回包状态与已知权威状态矛盾，进入原身份 status/barrier 对账，不由客户端选较新或较方便的值。

精确重复 begin 只在仍可接收的同 attempt/原 descriptor 上返回既有登记结果，不产生新 allocation 或期限；其他状态按上表只读对账或拒绝。任意重复/status/迟到 ack 都不算有效进度。

## 2. §4：unknown、barrier、fence 与取消先到

状态回执须区分“请求尚未 dispatch”“已 dispatch 但结论 unknown”“权威从未受理且已禁止迟到受理”“accepted”“committed”“清理仍未 settled”。这些是待唯一 canonical 编码的有限逻辑分支，不在本文件私造 DTO 或错误码。

- **最终 dispatch guard**：main 在实际写帧切点核当前受信 scope/代次/确认，等待队列或 await 前的旧检查不够。未发送的请求可结算本地发送预留，但不能据此结算其他已 dispatch 请求。
- **unknown**：原 attempt/operation 和对应资源继续占账；not-found、超时、本地 abort 或取消意图都不证明原帧不会晚到。不补发新 begin、新 attempt 或新 operation 来绕开未知结果。
- **barrier**：覆盖同一 session、原请求标识/发送序、权威 scope 版本及处理水位。回执须分类该范围内的原请求，或明确仍 unknown；仅证明 barrier 自身排队不够。已派发 worker、暂存/落盘、seal、读消费者及清理动作须被追踪或列为未 settled，不能只清空 main→coordinator 队列就释放其资源。
- **fence**：证明旧 scope/session 此后不能新接纳或复活。fence 前已 accepted/committed 的请求返回真实关联并按正式取消/receipt 处理，不改写为“从未发生”。原进程实际结束只能排除其继续执行，不能证明磁盘字节或其他实际读者已清理。
- **清理 settled**：先撤销新消费者/新写受理资格，等实际 reader/worker/writer 结束和可回收内容删除成功，再发布清理结算依据。失败或磁盘错误保留资源账和可恢复状态，不先释放槽后继续无界后台工作。

release 先于 begin 时，只登记受信 project/session/attempt 的取消事实及已有 scope/处理序，不要求尚不存在的完整 begin descriptor。晚到 begin 可核对并补充受限审计，但不能为该已取消身份分配。descriptor 不得被补写成另一 project/scope 的取消事实。

每 session 256 条 attempt 满额后不插入第257条，也不逐出旧 tombstone；新 begin 一律拒绝。已登记身份的 status/release/barrier、健康及既有消费者仍可处理。对于确实尚未登记的先行 release，满额 session 的永久新 begin 拒绝门与覆盖原发送序的 barrier/fence 可证明不会迟到分配；不得以 not-found 假称已创建取消 tombstone。原协议 request-id 自身上界仍独立适用。

## 3. §5：已有 claim 与首次接纳分开验证

稳定内容计划、prepare/confirmation、临时 AdmissionProof 和完整 claim 各保留 r3 的独立字段集/编码；临时 upload/lease/session 不混入文件 SHA 或稳定内容 planHash。实际首次接受的完整请求和验证证据在唯一 Store 内不可变保留，或引用可恢复的不可变受信原件。不能只存一个不可取回请求的 hash 后承诺跨重开精确重试。

处理次序固定为：

1. 严格结构校验，并认证当前连接/调用者对当前项目的真实读取或请求权限。外层新连接 session 只承担本次认证，不替换原接受证据。
2. 原 operation 已有全局 claim 时，先核 project、kind 和原不可变完整请求/context/指纹。全等才返回原 Job/receipt/状态；不同请求即拒绝。该分支不重验旧 live lease、旧 main proof 对象、新来源、当前 CAS 或新人类确认。
3. 尚无 claim 而原请求仍可能迟到时，保持 unknown，按第2节取得 barrier/fence 和实际事务结论。不能把换新 lease、同 planHash 或只改外层重试字段当作原请求全等。
4. 只有已证明原请求未受理且不能再迟到受理，才允许按新的明确用户确认开始新 operation；重新预览、新来源 proof/phase 绑定及新 AdmissionProof 都须真实成立。底层内容可以核真去重，不复用旧确认冒充新接纳。
5. 首次正式受理在同一权威排序和 Store 事务中核 source 完整性、options/table/mapping、域 base/必要 CAS、有效 scope/phase 和真实确认，建立全局 claim、Job context 与 durable source pin。任何一步失败全部回滚，不留下假 accepted 或缺输入的 Job。

序列化的 AdmissionProof 是当时已验证证据的数据记录，不是可重造的旧 SourceProof 实际对象，也不是新授权。原请求含私有字段时，恢复与对账采用受限授权投影；不能为重试把原 proof 或凭据广播给 renderer。正式 Job receipt 与传输 ack/status 不互相冒充。

## 4. §7：配额、寿命、恢复与活性核算

不修改 r3 的技术预算：1 个实际未结 begin、2 个未接纳 lease、合计16MiB声明 raw、每 upload 1 个未结 chunk、30/120/600秒、每 session 256 attempt、256MiB逻辑 encoded。它们仍须同 owner/profile 接受、精确 schema 和实测，不代表 Q5、物理 disk/WAL/RSS、parser 展开或持续可用性通过。

| 账目               | 占用、转账和释放的可判定边界                                                                                                                                                                       |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| begin / chunk 请求 | 真实 dispatch/异步工作未结或 ack unknown 都占用；经匹配 ack 或覆盖该请求及后续工作的权威 status/barrier 分类后才结算。begin 请求结算不等于 receiving/sealed lease 已释放。重复不生成第二队列或副本 |
| lease / raw 预留   | pending、receiving、sealed、admission-unknown、取消/清理未 settled 均计入；0B 仍占槽，内容去重不免声明长度预留。main/engine 分别保守执行相同全局限制，不能相加称可允许4个 lease                    |
| accepted 转账      | 必须有权威 claim/Job/context/durable pin 及安全输入移交依据，不能凭 UI accepted 标记减账。残留临时副本、读者或清理工作仍占其实际类别；转账不使持久内容免费，也不解除历史必需引用                   |
| 逻辑 encoded 存储  | 同一 source 命名空间内计所有块、manifest 和未实际清理的暂存/孤儿，accepted/pinned 同计；在昂贵编码/写入前保守预留，落盘核真后转实账。实际编码口径须包括选定封装，而不是仅 raw 长度或DB行数         |
| 去重 / GC          | 只有核真既有完整成员和引用后才能结算共享存储，不能仅按 caller hash 减账。GC 仅回收无 reader、pin 和必需引用者；删除及清理成功后才发布释放结算。损坏/未知成员保守占账，不伪报去重或无引用           |

raw 与 encoded 若实际同时保留，profile 必须说明两份暂存的计费/预留和物理副本清理；不能只计一份后称两份已消失。控制记录、descriptor、ack/status/barrier 的字段和字符串均须有限预算；具体计费公式/上界随唯一 profile 冻结，不以256条或256MiB数字本身代替它们。logical quota 不足与真实磁盘故障分别处理。

期限表：pending 的总120秒从权威 begin 原子登记/预留时开始；进入 receiving 时起算 idle 30秒，只有新块真实耐久并登记的新进度可重置 idle，总120秒不重置。首次有效 seal 在传输期限内完成后，建立固定600秒未接纳期限；重复 seal 不重建期限。每个 owner 使用自己的单调时钟，检查采用 now >= deadline 即到期；不把 main/engine 的单调时间戳直接互比为同一个绝对时刻。到期撤销新接纳资格，不能提前删除在用字节；accepted 的 durable Job/pin 不再由传输 TTL 决定。

重启恢复须先 fence 旧进程/许可并处理实际 worker/读者，再从真实 claim、Job、pin、source成员及清理依据重建资源账。旧活 lease 不自动复活，旧 accepted/committed 记录及必需输入不删除；遗留 temp/孤儿在受控清理 settled 前继续计存储账。新 session 的 attempt 容量不是抹除持久 charge 的方法，重建对象也不刷新旧期限。无法证明的状态保持 unknown/占账并可对账，不能默认当不存在。

满256 attempt 时可以拒新来源并继续 status/release/barrier/健康和既有工作；如需受控新 session，先完成 fence、任务/输入交接或取消对账和配额重建，不为新增来源无条件杀掉已接受工作。256MiB全被不可回收引用占用时明确拒新来源；不得暗删历史或以无限重启逃账。此安全降级不等于持续导入体验已达标。

## 5. 冻结及验证边界

唯一 canonical 后续冻结各状态/有限错误、原请求持久载体、barrier/fence/settled 回执、预算计费和跨 session 分支；worker 责任生效不代替这些合同。T03 已交完整 Table 投影，r3 中“仍等待该投影”的历史描述不再作为重提同一资料的前置；精确 tableDigest、typed worker 完整结果、parser 适配及真实接线仍各按实际证据完成。

必验新增反例：receiving 原块 ack 丢失后精确重试；sealed 旧/新 ordinal 均不续传；到期清理后仅 tombstone 时拒旧块；admission 与冲突 append/release/expiry 两种先后；迟到小 nextIndex 不回退进度；满256时既有 status/release/barrier 可用及未知 release 不超表；unknown/worker/落盘/清理未结不减账；accepted 转 pin、重启重建及共享成员 GC；S1 accepted 后 S2 当前授权下按原请求对账，不要求旧 lease 存活。

本页没有运行上述 fixture、parser、配额/GC或产品，也不声称当前私有 content intern 已实现上传生命周期。真实 CSV/XLSX→inspection/preview→确认→Job/Store、取消/TTL/崩溃恢复、同版源码/包、指定双审/CI和父验收保持原门禁。
