# T01供方收敛记录：独立静态审查

2026-10-23。固定 `12e9c5f3ef0770506fc2cffa381113c0287542b8`：**通过，未发现实质问题；仅接收纯文档需求收敛。** 纯字段helper两文件是可最先独立申请的实施段，不是本次开工授权。f20是供方设计文档ref，不能当产品、源码或运行许可；37bd也没有被本报告升级为根已最终接收。

## 实际读取与身份

全文读本prefix两件：

| 文件 | bytes | SHA256 |
| --- | ---: | --- |
| convergence.md | 9845 | 4eab921c024e8280572333d372655840522fe6f9e2c4e4469682c8845f7db046 |
| intake.json | 5328 | d9d29ca5fab8663f9bd028746ceb01f269786f58f2e6b6bbdd86fedba9db83c3 |

直接读取根 reception JSON 的 `consumerAllowlists.T02`，根文件实际5683B／`870fab83765c73735f2dd118eba708e82c401acd8d9011359aae1a70aa5fe98a`，匹配intake。对照其7项，只从固定 `f20c2a7f39c90d5a3397821d5ea81752ff79da19` 读取允许目录中的README、input-identities、delivery-manifest、首稿23980B、修订计划25696B、初审5026B和终审3364B，**七件全文已读，逐项ref/path/bytes/SHA及许可声明均匹配**。修订计划按1–55及56–104行完整读回，首稿按1–53及54–101行完整读回，未把输出截断材料当全文。

未打开这些文档引用的P/F/A/B原件、源码/helper或T10文档，未据引用扩大读取权限。供方manifest的6项payload身份与上述允许对象相符；self manifest是第7件，不把它计入自身payload。

自有37bd三项consumerDrafts逐项固定Git身份及当前字节匹配intake。另直接字节比较确认两份消费正文逐字等于本审此前已通过的bb234版本，因此沿用其完整审读，不重读旧大稿或产品。AGENTS仍15147B／de15声明哈希。37bd→12e9的Git路径差异仅本prefix两件docs；没有新的产品实现差异。

## 具体结论

1. **第一实施段界限准确。** convergence第3、29–36行将建议限制为T01唯一writer的新 `project/entity_metadata.py` 与专属 `test_project_entity_metadata.py`；只接给定不可变有限字段、显式home/冲突范围和profile规则，不读项目、不认证provenance/全项目覆盖、不迁移激活、不发行proof。必要只读imports须先批准，旧文件delta另列。根仍需精确base/新树/分支/闭包/合同，不复用HOLD同名树或WIP。没有把合法字段单测当真实M来源或正向supplier成功。
2. **最短门序与K修订一致。** 第40–43行是helper及并行设计→可信C/reader和规则固定后非空S1→C/S1/K/最小M1/S2同版机制链→正式host/I06/App真人。K的严格内部metadata/version/proof承载必须与M1/S2共同冻结，不能推迟到App，也不要求先启用全部公开API。与供方修订计划28–35、47–51、59、81行一致。供方首稿漏K早期窗口的P2-DEP-01及原Fail仍有原件；收敛第23行明确初Fail有效，没有倒填。
3. **七输入映射完整。** 第15–21行分别覆盖TrustedScope、CostContext、SourceBundle、MetadataBinding、EditorBaseAndBinding、FactEditIntent、ActualPreview，准确区分供方设计已有内容和待唯一owner真实回报的delta。内部可信owner/context仍是机制前置，正式产品host/scope/I06后置；不是取消可信上下文或放开公开RPC。旧423、同形对象和文档HEAD都不能补新发行者。
4. **来源与M无损边界保留。** S1要求同连接真实current CP.domainSnapshotRef与state/vector/revision一致，不写snapshot凑ref；保全payload/control、全部支持原ID/归属/墓碑/retirement。C5四键RDF view的兼容与旁侧M/proof同源绑定分开，没有减字段凑形状或拿RDF覆盖证明抵M授权。unknown coverage/typed term不可保真给缺失/coverage材料并拒可编辑成功，不当空集合。已选L1、唯一home、跨四类精确identifier政策不重问；真实业务值/home仍未供，不能派生。
5. **RDFS护栏未回退。** 第20行明确完整采用消费C1–C8，保slot/目标冲突、原factID及完整M/支持/原记录/control不变；domain/range保持RDFS推理含义，不重新引入已关闭的range值匹配保存门。真实词项datatype/ill_typed校验与独立获批SHACL合同分开。
6. **费用覆盖和收尾具体。** 第16、41、48行要求可信bootstrap先于本次首读、同实际session预扣、失败/重复/跨页累计及真实释放ack；已开库读取不追认成受保护。覆盖深层helper、嵌套cleanup与独立terminal封存额度，不因业务耗尽借ownership详情侧写开未计费事务。重开查询与新undo身份/生命周期由实际合同固定，不沿旧S1局部数字或ReadLimits冒整链计费。全部仍是供方请求，没有实际meter或费用Pass声称。
7. **current/historical分派准确。** 第21、50行保精确已受理operation重试、旧receipt/undo目标的不可变历史核验；新claim和首次commit仍验current，不能用历史例外绕过首次写。四原事务重取/投影/重演、完整after/receipt/新undo与原唯一writer保留。响应丢失只对账不换operation重派；健康业务拒绝核自己事务回滚，真实I/O/cleanup故障保首因和实际持久事实，明确不保证必能close或terminal，也不循环重试或把已提交成功改失败。
8. **后续回单与owner未泛化。** 第47–51行将helper、C/S1、K、M1/S2、产品各自回单细化为实际pin/闭包/签名/错误/验证或所需delta。T01四基础路径、I06四壳桥和T02页面/两P3仍归原owner；不由这张表授整目录、公共schema或第二writer。C1共享修复仅按供方计划声明进展，不伪称已冻结；共享原文件仍累计候选串行。
9. **父缺口与当前状态真实。** 不再泛等F01/F16/Q5/工程M0或全部CRUD/Turtle/T08/T10才准备最短段；完整M、跨层删除、多支持、交换和父验收仍各自闭环。非空S1可交真实L1缺失材料但不是可编辑成功；单事实机制必须有真实非空可执行正例，不能全拒绝充供方。机制fixture确认不当真人；四P3、C5/旧原件、父Goal与后续新候选验证/指定新审、CI/合并/发布门均未关闭。

## 验证边界

实际只执行只读Git、文本和stdlib JSON/hash/字节比较；本审没有执行formatter，故不新增独立格式通过声称。未重跑34/130/825、未读取任何供方源码/helper、未import产品/测试/探针/SQL/DB/JobStore/native/GUI/网络模型，未新建fixture、adapter、schema、worktree或Goal。只新增本独立报告，未改两件原稿或旧输入，未提交。

结论限于**双方设计差异及第一实施申请的边界收敛**。实际供方产品、根逐路径采用、运行票、机制事务与真人产品证据尚未产生或未在本审验证，不能据此开工、发行或外推父功能通过。
