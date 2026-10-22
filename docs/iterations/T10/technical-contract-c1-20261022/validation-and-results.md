# C1 校验顺序与消费结果

以下是owner批准前的算法合同，不是已注册的方法/错误码。任何阶段只产生受控内存/准备对象，不产生可见项目。既有I06 guard、input seal、持久pin/GC、recovery/claim/fence及T01单事务协议继续适用；本稿不重新实现。

## 1. 有界校验顺序

| 序  | 输入与检查                                                                                              | 失败/取消与下一步                                                                 |
| --- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| V0  | 受信main上下文及I06实际操作能力；形成同一有界不可变InputSeal，封存保护不反依赖最终plan                  | 无权/无法封存则相关内容IO前拒；不向renderer交任意路径/handle                      |
| V1  | 本机批准profile/resourcePolicy与受信输入长度；受限EOCD/目录扫描、实际计数/布局/方法/元数据白名单        | 预算在额外分配/展开前核；未批policy不借包声明放行                                 |
| V2  | 有界manifest严格解析；精确Refs注册组合、kind/scope政策、四选项、role/member双向覆盖                     | 包内Ref只索引本地注册，绝不联网或动态加载；未知拒绝，不静默降模板                 |
| V3  | 逐catalog成员有界解压；声明与实际输入/输出累计量、CRC/hash、结束/尾流、JSONL逐行/record预算/排序/重复   | 一旦读出超限证据即停止，不交业务plan；I/O/CPU/解析取消按受控owner协议收尾         |
| V4  | owner typed payload、完整源族/版本/retirement根coverage、引用闭包/owner/managed/tombstone及选项正文排除 | 成员hash全部正确仍不能跳过；不能以resolve已列边证明无漏根，无供方schema只给未就绪 |
| V5  | T01固定新项目typed重映射与digest计划、支持矩阵、三能力逐对象判断、真实学习来源/证据完整性               | source/actor未认证独立于结构有效性；合法foreign核心保unverified，不伪造本机check  |
| V6  | 生成main-only不可变plan ticket与安全摘要；绑定input/scope/plan/versions/context，真实用户确认           | 变化失效重预演；确认不授权网络或继续导入包中job/grant                             |
| V7  | 按R1持久recovery→writer claim→准备pin复验→唯一Store提交+receipt                                         | unknown只原业务身份对账；负fence后用户新预演确认可新op；不以无receipt证明未提交   |

资源policy应给：manifest/目录/成员/总压缩与总展开字节、角色和记录/字符串/深度/typed图边界、实际parser分配与CPU/IO取消检查点、准备对象/并发/进度。没有确切值/目标机证明时只可评议合同，不给正式capacity或性能提升数值。超限不是截断成功，prefix通过也不是全包通过。

## 2. 消费结果形状

建议P-TransferAssessment只供受信main持有完整对象；renderer消费单独安全摘要。字段不构成IPC JSON或可执行ticket。

| 字段                                                       | 具体语义                                                                                                                                                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| inputSealRef / inputSealDigest / formatRegistrySnapshotRef | 绑定本次不可变输入与本机固定能力注册版本；不是来源身份签名                                                                                                                                       |
| kind / scopeDigest / schemaVersionSet                      | 实际核定类型、显式选项子范围及支持版本，不直接照抄包声明                                                                                                                                         |
| structuralState                                            | 本次完整校验的valid/invalid/not-ready；valid仅在V0–V5所需真实合同均存在且全部通过，不能把本稿概念例设valid                                                                                       |
| coverageRef / identityPlanRef                              | 唯一owner生成的完整业务coverage与typed映射引用；renderer不能提供任意替代对象                                                                                                                     |
| capabilityItems                                            | 每项{capability,subjectRef,materialState,supportState,verificationState,reasonRefs}；capability限定restore-current/mapping-rerun/run-replay，subject分别为本次full/new-project计划、mapping或run |
| originTrust                                                | 来源主张/foreign unverified与本机工具验证分别保留；不按hash、ZIP producer标签或用户确认升学习资格                                                                                                |
| canConfirm / planTicketRef                                 | 仅本次全部必需合同/校验和当前合法上下文允许才true；材料就绪不等于已导入，ticket不可序列化供包/renderer伪造                                                                                       |

候选枚举：materialState=complete/missing/unknown，supportState=supported/unsupported/unknown，verificationState=not-run/verified/failed/unknown。reasonRefs只引用批准的安全定位和理由字典；最终枚举/错误映射仍由owner冻结。本轮所有例子actual为null，不签任何实际三轴值。

restore-current的subject为full目标计划而非某个run；template恒不承诺当前恢复。raw缺失可使某mapping材料缺失而不必阻断full核心；history=false的对应run没有被选重放对象，不生成“所有历史可重放”的条目。source缺依赖按实际T03重关联后新预演改变mapping项；不自动复活旧proof/确认。

验证范围必须显示：ZIP结构验证、typed语义验证、实际本机导入提交与实际重跑/逐轮重放是不同证据。restore项的verificationState=verified只能来自真实导入后批准的业务一致性验收/receipt与对应证据，不由“材料齐全”或V1–V5自动置位。支持为unknown/unsupported时不伪造执行验证。

## 3. 有限错误与owner交接

内部拒绝归因固定到stage+proposedCategory+安全reasonRef+有限计数；无路径、原始异常、字段正文或秘密。proposedCategory只作设计归类，沿现有26错误表的真实边界待T01/I03/I06注册映射；不扩现有RESOURCE_LIMIT/NOT_FOUND参数含义或把TIMEOUT当未提交。面向用户的固定messageKey仍由真实合同供给。

T01需回填：精确注册Refs/role schema/canonical排序与coverage、typed映射和plan shape、writer错误/receipt。T03需回填：source对象/编码/producer及原字节读能力。I06需回填：真实seal/位置/生命周期及准备对象能力。T07/T09/T08需回填真实run/learning证据。T10可先评议此信封和验证适配合同，不复制这些服务，不因尚缺整个模块就虚构空投影。
