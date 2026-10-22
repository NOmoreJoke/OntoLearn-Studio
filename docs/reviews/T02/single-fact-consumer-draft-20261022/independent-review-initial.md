# 单事实 typed 消费草案：独立初审

2026-10-22。固定候选 `db77a347a826b7b50d6ef88c5e894c365d63eefe`：**不通过，1项P2**。本结论针对纯文档草案，不是C5产品回归失败，不改既有有界S1双Pass。另有1项分页措辞歧义，已实际读回后续固定 `e976835a8a9c40cf86a07e6d5ad1cc6421a95b83` 的两行差异，确认该歧义关闭；P2在该修订仍存在。

## 核验范围与身份

全文读取本prefix三件：`consumer-matrix.md`、`supplier-requests.md`、`input-readback.json`。直接读取固定C5 `e5ad54e5762157cafe532c2a0c07c22e8dd737cb` 的 `ontology/model.py`、`service.py`、`source_projection.py`，核结构、实际函数体及来源绑定边界；引用此前已完成的fa988下一段方案与T01/I05/I06三份静态矩阵审查，不重开产品全审。

固定db77相对fa988仅新增上述三件docs。三件身份为：

| 文件 | bytes | SHA256 |
| --- | ---: | --- |
| consumer-matrix.md | 17365 | b510193a91f63a1e9265593c5f9f9cae14bd6c2198a54c15ac4df5f615b771fc |
| supplier-requests.md | 20257 | 22c7140255e4fd3ac5a1393cc13ad617a3ebd05e883e41df5e55f1bf7f090a2c |
| input-readback.json | 3191 | 93c5676b8bef44f67a0da0c85cd33a1cd8ce70b19856ead601dabb7c047eeb9d |

逐项从声明固定Git对象重读8项输入，bytes/SHA全部匹配：fa988主方案、三接口矩阵、delivery-readback，以及C5三个模块。仓库外根审计全文读取，实际10613B／`99538ee5b24fbdeeffb63747bb817933c1ff9e437ce4a559ae09541f38177f05`；没有复制或修改它。当前AGENTS实际15147B／`de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，匹配声明。这是8项固定身份核验，不冒称重跑旧34／130／825项审计或根独审的全部工作。

## P2：不得以属性range声明新增词项保存拒绝

**位置：** `consumer-matrix.md:68`（F11），以及24行“受支持dataProperty/domain/range”的潜在关联判据。

F11将“声明range不容新O”与非canonical N3、surrogate、非法词项并列，要求获准模型/decoder给错误并拒绝。这样会把RDFS range声明直接变成当前单事实段的闭世界数据校验门。

**直接依据：** PRD第688行明确“定义域/值域不得被当作必填或类型校验错误直接展示”；附录C第970行将 `rdfs:domain/rdfs:range` 定为RDFS类型推理，并明确不是数据校验错误。C5 `model.py:191–196`只限制dataProperty的range声明使用受支持datatype；197–223行对事实检查canonical词项、允许datatype、ill_typed及property/object形态，**没有比较新literal datatype与prop.range是否相同**。`service.py:145–232`的真实change_preview复用这些检查，没有额外range匹配门。

**静态可复现输入：** 已存在individual、dataProperty的range声明为 `xsd:string`，唯一人工事实原值为 `"a"`，新object为canonical `"1"^^<http://www.w3.org/2001/XMLSchema#integer>`；其余C1–C8来源、单支持、原ID及保真条件均满足。两datatype均在C5白名单，integer词法有效，真实C5模型没有以range不同拒绝该编辑；F11却预定应拒绝。此为源码推导反例，本审未执行产品。

**影响：** 将把本可表示的合法编辑错误归为词项失败，给未来供方和测试建立未经批准的保存门，且混淆RDFS与SHACL。其余合法编辑只是切片不可表示的声明，不能消除F11本身的错误语义。

**最小修订：** 输入保留原domain/range声明并纳入不变性比较；词项拒绝只按实际获准的编码、canonical N3、支持datatype、ill_typed与必要引用/形态规则。明确不能仅因声明range与新literal不同而拒绝。若未来真实SHACL报告需要影响提交，须由独立获批合同定义数据范围、policy及错误/警告语义，不能在本草案预定。重新固定修订后仅需静态核实际差异；本初Fail保留。

## 分页歧义与已读回修订

db77 `consumer-matrix.md:72`“跳页/重复”和 `supplier-requests.md:46`“重复…必须固定拒绝确认”没有清楚区分错误拼接与同页受控重取，可能误禁真实供方允许的重试；同时R2及R5又要求重试累计计费。

已直接读db77→e976完整prefix差异，确实只有这两行：F15改为“同一段被重复拼入文档”，明确受控同页重试按真实供方合同并计同CostSession；R5同样限定组装材料重复拼段，不预定新cursor协议。该措辞问题在e976关闭，不要求取消同页重试，也未新增公共分页协议。其余db77意见不因该两行修订自动关闭。

## 其余完整审读结论

除上述P2，未发现新的实质阻断：

- **实际C5结构与信任：** Snapshot/Entity/Fact/Preview描述吻合实际私有结构。普通不可变Preview可直接构造，类型及base_digest不证明生产来源；草案要求可信编排真实调用change_preview和T01独立重投影/重演，未把require_current变成确认token。正式adapter仍不得裸调未校验digest入口。
- **来源、metadata与支持：** C1–C8要求完整实体/M/外部引用不变、实际一删一加同S/P、唯一活动人工支持、全slot冲突检查与原factID不变。BoundRdfProjection保fact原ID/归属/墓碑、statement_sources每个原triples下标、definition payload摘要与显式引用；草案没有将RDF覆盖证明等同M来源授权。新S1的旧Store2形状兼容要求明确不能删字段凑形状；不兼容须回报真实消费delta，不由T02伪造source或identifier。
- **纯翻译与完整oracle：** 输出只在获准typed格式中按原recordId编辑object，不重算ID，不夹带metadata/proof/cost公共字段、不造第二writer。candidate及T01回滚after需完整核domain/RDF、原records、M、mapping/control与未知payload，不能只比总数或RDF。窄化为individual/dataProperty单值切片有明确不可表示边界，并保留完整CRUD、多支持及跨层删除父缺口。
- **CostSession：** R2与消费入口均把可信issuer/bootstrap policy和同CostSession放在任何源读取/解码/复制/物化之前，后续只复用不替换。所有页、重试、失败、旧plan/历史与驻留累计，spent不退、reserved真实释放ack才返还。重开历史使用当前受信查询预算，新undo是新操作并先于首读取得预算；没有借旧creation cap/worker内存或旧工程数字填已计费证明。
- **四阶段与原事务链：** R4/R6要求T01原authority持久绑定新proof并独立重演，预览保存、confirm、Job接纳、commit各在原事务重取当前源及metadata/profile/policy等；queued不等成功。原writer的domain/evidence/receipt/result/succeeded同事务，响应丢失按旧operation对账，unknown不自动改ID重放；undo是当前源新proof、完整impact、新确认和Job，历史成功与无关后续变化保留。
- **22未来case：** F01–F22覆盖错scope、M缺失、来源/profile不兼容、漏支持、伪Preview、不可表示编辑、metadata夹带、重复/mapped/墓碑、slot/ID冲突、完整after、同revision四阶段漂移、绑定/页链、真人边界、首读与累计预算、排队取消、原子失败、丢响应和undo冲突。均标未来判据，无本次执行/Pass，正向必须实际新S1→生产Preview→原T01链；合成领域反例不冒被测proof/plan/meter。词项行须按本P2修订。
- **10供方槽及层级：** R1 M home/L1；R2成本issuer；R3 S1全源；R4 S2原authority；R5完整Diff；R6确认/Job/commit；R7历史/undo；R8canonical/命名engine/current-host；R9具名bridge；R10真实App/真人，职责齐全且与消费条件相连。逐槽请求新product/process、path/blob/bytes/SHA、真实签名/固定失败、import/资源/strict-schema闭包、delta、policy及原始验证/首败，不把旧423或同名WIP冒新交付。
- **owner与门禁：** T01四基础路径和原存储/writer归其唯一owner；I06仅四壳桥及获准专测，T02页面delta另交其owner；D设计、M机制、P真实产品、F完整父验收分开，没有泛等M0/全部CRUD/Turtle/T08/T10，也没把它们从父验收删除。四P3仍按根已接收分流，未称已修。C5、旧输入、Goal冻结及新候选独审/双方全新同版指定审查/CI/合并/发布门保留。

## 未验边界

本审只读Git、文本和stdlib hash/JSON；未import产品，未执行测试/探针/SQL/JobStore/native/GUI/模型，也未读取live会话或本轮指定模型意见。未创建正向supplier fixture、adapter、公共schema、写计划或新授权；除本独立初审外未写文件、未提交。原供方API、M home、新S1/S2/CostSession、正式bridge/App/真人及原事务运行证据仍待实际交付与批准，本次草案核验不替代它们或产品指定双审。
