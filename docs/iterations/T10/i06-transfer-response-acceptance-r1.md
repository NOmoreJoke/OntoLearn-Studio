# T10 对 I06 受信转移回应的最小接受记录

2026-10-21。结论：设计方向无新增冲突；接受以下能力与证明边界。**不是guard可调用、路径已登记、实现获批或X1–X6通过**，原Goal保持blocked。本记录不改a1候选/147项清单、不修改共享或装配接口。

实际全文读取I06固定 `eabaf4dba8a36b67266e0753bbc17df255042048` 的 `docs/iterations/I06/T10-trusted-transfer-response.md`，24360字节/SHA256 `db29f3a37e281bb83232dd2a18eda0eadfa670ba65b56f25e643b68800ce6b2c`；另读固定 `b1283bce1daf7198fc6b0b62f8b0a6bbffa5a874` 的 `T01-owner-response-alignment-r1.md` §3及 `68dfd71a950bab0cda2e53776c4aa3c5e7819d5c` 的来源生命周期对齐。仅采用设计答复，不读取/消费未批准runtime。

- **guard-before-IO与实际能力：**picker只给候选；bootstrap仅有限metadata，随后实际handle/parent/member绑定，绑定成功后才内容读取/hash/正文写入。后续消费用途限定IO能力，不把lease降成path+assertSafe再自行reopen；跨await、最终发布及新位置/reopen都须按批准合同重验。engine附件亦须在首次内容IO前消费等价受信能力，不给Python私有inventory或任意路径。
- **metadata不能省略：**完整私有整根、未来后代、pending/journal及密文原件、静态硬链接别名均受保护。需I06唯一metadata owner提供profile epoch/revision/完整性、原子发布/失效屏障和退役规则；现有单bucket枚举、32在途限制、单实例锁和fault observer均不构成此机制。未知/不完整/超预算或私有服务失败不能按根为空放行；只拒绝相关transfer，本地Store/窗口照常。
- **保证边界：**Node路径复验、O_NOFOLLOW及事后fstat不等于目录相对原子confinement，不能抹去已发生open/mkdir或声称抵抗持续同UID namespace攻击。平台无可证明原语时相关IO拒绝；若仅完成metadata决策/失效核心，也不得包装成完整IO lease。生产不读取/hash私有字节找别名，不声称通用DLP。
- **真实提交与选择：**唯一writer receipt由main协调层核request/profile/项目代次、版本、新ID和明确提交状态；用户要求打开且最后await后重验才selectProject(newId,[])。迟到receipt不抢切项目；已提交后选择/回执失败保留真实提交事实并按原operation/request只读对账，不伪称未创建或重新提交。失败/不明不切项目、不恢复包内job/grant/context；模型未就绪不阻断本地打开，后续按当时实际项目初始化。
- **与T01/T03对齐：**业务白名单、一致读投影、类型化必要闭包和业务assistanceAudit保真与私有profile audit排除相容。附件需统一受信source封存/消费保护，source proof、只读消费、写确认与模型外发grant互不替代。来源分块/限额仍是提案，不自动成为T10包/附件限额或已可用传输接口。

精确调用方缺口：现有T10 `PreparedHtmlReportFile`仍自己执行FS操作，picker或fault checkpoint不能直接充当上述IO能力；获批准接口后须在T10独占路径适配实际能力消费、发布/清理及失败状态，不能只套一次路径检查即接线。此为明确的后续实现delta，不是当前设计冲突，也未在本轮实施。

I06申请的 `main/security/private-root-transfer-guard.ts` 及专属测试尚未生效，完整metadata inventory/生命周期、受控IO/平台、T01 payload/receipt/错误和真实source仍待各唯一owner及总控批准。T10不抢写、不另造registry/guard/公共协议/第二writer；X1–X6及全部父门保留，无纯文档触发的产品重测、GUI或Goal恢复。
