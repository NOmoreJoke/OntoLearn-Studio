# T01 新供方计划对照：第一实施短段需求（draft）

**建议下一张实施票先给T01纯字段校验两文件；非空S1和单事实写链分别按后续依赖闭合。** 不等F01/F16、Q5、Turtle/T08/T10或工程M0总完成；本件只是需求收敛，不是开工票。根仍须选精确base/独立树/逐路径采用和唯一writer。原C1 A/B共享修复先冻结、共享文件按累计候选串行，当前进展仅按供方计划声明，不据此声称其已冻结。

只读取根允许的T01 `f20c2a7f39c90d5a3397821d5ea81752ff79da19:docs/reviews/T01/t02-supplier-next-delivery-20261022/` 七docs，逐项Git bytes/SHA匹配，主plan25696B／`6964fa5bb767b009d9e6b3949bb53ba8f44628c29b879b4d52a9ef05083e7c6b`全文104行已读，首稿/首Fail/终审均全文读。没有继续打开其引用的源码、helper、P/F/A等另件或T10文档。精确身份见 `intake.json`，不复制七原件或旧十件。

对照本线37bd的消费矩阵/10槽请求：它们是内部静态通过的draft，按最新根消息窄审仍在收件，**不在此冒称已获根最终接收**。T01新件对接起点为旧fa988；以下补齐实际接口差异，不改两边固定原稿。所有Draft名称仍非公共schema/API或新错误码，f20亦不是可采用产品供方ref。

## 七概念输入的对齐与必要细化

以下行号均为T01固定 `plan.md.raw`。

| T02 draft输入／原请求 | T01已明确的设计（不是已实现） | 第一段仍需唯一owner回报的精确差异 |
| --- | --- | --- |
| TrustedScope；R8/R9 | 28–35、45/51行区分受信内部Store issuer与正式产品host/scope | 机制阶段需真实内部owner/context与K合同，不把生产位置/产品host/I06全部列为纯校验或受控机制的统一前置；P阶段仍需实际命名engine/main/current host和真人 |
| CostContext；R2 | 45、57、65行：bootstrap先于首读，同对象预扣、失败累计、真实释放ack；开库已发生的读不追认受保护 | 给覆盖起点/可信policy来源/跨页Job重试及重开查询、新undo身份；特别给嵌套清理与Job terminal独立封存额度，耗尽业务额度不能借ownership详情旁路侧写。数字按新真实调用图固定，不沿旧S1局部预算 |
| SourceBundle；R3 | 46/57行：同连接current CP.domainSnapshotRef真实存在且与state/vector/revision相符；全源/所有支持/墓碑/retirement；四键source旁侧保control/M/policy | 发行S1实际签名、兼容view和旁侧M/proof的同源绑定；不能把旧C5 binding成功等同M授权，也不能手造减字段来源。unknown coverage/typed term不能保真给材料并拒可编辑成功，不充空集合 |
| MetadataBinding；R1 | 18、44/48行：已选L1、五字段唯一home、跨四类精确identifier唯一、profile2；缺真实业务identifier不派生 | 纯helper只验证给定有限材料的规则/冲突，不认证真实home/provenance或项目全覆盖。S1可先报真实缺失；要构造可编辑Entity仍需真实值/home，最小持久激活/写门M1与S2共同冻结，非等完整M编辑器 |
| EditorBaseAndBinding；R3/R4 | 57/61行完整投影、源/metadata/CP/profile身份贯穿；四事务前重取/重投影/重演 | T01列实际C5消费调用点和限额/profile；若需model/service/source_projection meter或兼容delta必须逐文件申请，由T02维护新候选，不能用同形对象或旧423补新发行者 |
| FactEditIntent；R4 | 35/50行：一removed/added、同S/P、单manual原ID、零Entity变化，译原edits | 完整采用37bd的C1–C8：slot/目标不冲突、完整M/支持/原记录/控制不变。保RDFS domain/range非数据校验护栏，真实词项datatype/ill_typed检查与独立SHACL合同分开，不重新引入已关闭的range保存门 |
| ActualPreview；R4–R7 | 47/59/61/63行：K先于M1/S2；持久envelope/参数/页链/确认/Job，同writer receipt/undo；历史/current分派 | K需在共同冻结前承载真实metadata before/after及跨原参数/响应的材料；哪些proof仅存私有envelope、哪些需严格schema由T01明确，不能向旧v1追加可选字段充新版本。精确已受理operation重试/旧receipt按历史核，不重派；新claim和首次commit仍核current |

**新收口是K的时序及机制／产品host分层。** T01首Fail P2-DEP-01原件有效；修订已把K列为M1/S2共同冻结前置。37bd R8“canonical/host”在后继消费时须按上述内部合同与产品启用分开解释；此补充不是取消可信调用上下文，也不放开公开RPC。

## 真正第一张实施票：T01纯字段校验

| 项 | 建议最小边界／未来判据（当前未实施、未运行） |
| --- | --- |
| 唯一writer与文件 | T01独占新 `packages/engine/src/ontolearn_engine/project/entity_metadata.py` 和 `packages/engine/tests/test_project_entity_metadata.py`；只有这两文件及实际必要的已批准只读常量/import。任何额外旧文件delta先单列，T02不代写 |
| 根需先固定 | 精确base/新独立树/分支、候选只读依赖path/blob/bytes/SHA及纯字段合同；不以f20文档HEAD或旧423当新helper产品。不可复用HOLD下同名工作树或静默采用同名WIP |
| 有限输入与输出 | 给定不可变有限字段/profile-aware材料及显式home/冲突检查范围，输出校验结果或有限私有失败；不是读取项目、构造可信来源、迁移/激活profile或发行proof。空值/缺失区分，未知材料不认证为空；界限与错误名由T01固定，不在T02造公共DTO/策略数值 |
| 最小验证 | 真业务identifier缺失不派生；同IRI多home、project跨类型重复精确identifier；大小写不同不自动合并、不trim/NFC/casefold；完整语言/文本/集合顺序保真；profile1 opaque同名键不认证成profile2。检查只覆盖所给有限集合，不能凭caller“complete”证明全项目唯一home |
| 明确不做 | 无SQL/DB/Store/Job/confirm/commit、无新公共canonical/外部scope；无metadata持久成功、无S1非空源/全链费用或物理保护证明。纯helper合法字段单测不冒正向supplier fixture/真实M来源成功；RDFS声明不新增闭世界值校验 |
| 交付后往哪里走 | 新产品/process pin、必要import/资源闭包、实际专测/受影响回归及原首败。纯helper可独立冻结审查，不能沿旧方案Pass；随后作为C/S1的解释规则输入，不把它倒填为可编辑Entity或typed写链完成 |

这两文件不是新T02 adapter；本会话现在只提交上述申请。根可在明确累计base与责任后路由T01执行；共享旧writer的后续C/M1/S2仍单一T01按窗口串行，不因helper叶子可实施就抢写共享文件。

## 后续最短门序与剩余五份回单

1. **字段helper与并行设计。** 上述两文件的候选可独立申请；C的issuer/bootstrap/深层费用库存、K的严格内部合同、I06具名页面合同继续并行设计，不等供方运行ref才设计。
2. **第一份非空只读S1。** 实际C的可信内部issuer/强制session＋helper规则及同连接reader先固定；新S1返回完整非空源或真实L1缺失材料，未来用真实原API建受控领域数据、实际reader读、核全支持/CP、禁全写及caller事务未动。缺业务值时只读/缺失结果仍可交付，不能构造可编辑成功。健康TMPDB验证必须另获根精确票，不据本表解HOLD。
3. **第一条typed机制写链。** C＋S1＋K＋最小M1/S2同版共同发行，根定T02新树和逐路径C5采用后，才真实Preview→纯翻译→原preview/完整Diff→显式机制fixture确认→Job/同writer原子commit→receipt→新undo。K不能推迟到App窗；新proof不能由fixture或opaque写入造出。至少一条真实非空正向链能完成，不能“全拒绝”当可执行供方。
4. **产品命名桥/真人。** T01正式engine/main/current host与I06四壳bridge/App的批准delta、真实可见完整Diff和真人动作后置；机制fixture不当人确认。跨层完整删除、完整M CRUD、多支持编辑、Turtle/SHACL/T08/T10和父验收继续各自闭环，不挡本次短段准备。

| 下一份最小回单／owner | 对本线真正有用的内容 |
| --- | --- |
| T01 helper回单 | 两文件精确产品pin/闭包、有限输入和profile规则、错误/缺失/冲突边界及实际验证；不再询问已选L1/唯一home/identifier精确政策 |
| T01 C/S1回单 | 原owner真实bootstrap覆盖起点、同session/TTL/失败与查询/undo生命周期，完整非空reader及CP/view旁侧绑定，实际入口前预扣与cleanup/terminal封存额度；无真实发行者不能用costId/旧ReadLimits替代 |
| T01 K回单 | 最小内部strict metadata/version/proof承载面、schema/registry/fixtures/bindings/TS/Python helper的实际必要delta、旧值/默认v2保留、新旧版本及profile混用两端同判；候选路径由T01列，不等于本线获整目录权限 |
| T01 M1/S2回单 | profile升级/真实home最小写门和四原事务proof、current/historical唯一分派、真实完整after/receipt/undo；非空可执行正例及故障。健康业务拒绝核自己事务回滚；真实I/O/cleanup故障保首因和实际持久事实，不承诺必能close/terminal，不自动重试或改已提交成功 |
| T01/I06产品回单 | 各自独占的四基础文件/四壳桥逐路径delta与命名合同，页链重复拼段和合法重试分清、generation/晚返失效、完整Diff可见/真人/对账。T02两P3仍由T02新候选自管，不转交页模块写权 |

本次只按允许七docs读取和自有固定草案做静态对照；不从计划内引用继续读取源码/helper/旧大稿、不import产品/建库/测试/GUI/模型、不复制原件、不改原矩阵/十件/C5/父Goal。四P3保持原分流；未发新实现/采用票、未合并或发布。
