# 单事实 typed 消费输入／输出／失败矩阵（draft）

本件细化固定fa988接续方案的单条人工事实object修改，不新增范围或实施。**以下Draft名称、条件编号和失败类别只是消费设计草案，不是公共DTO/schema、wire方法或canonical错误码。** 当前新T01供方尚无可采用pin；本件无正向supplier fixture、实际adapter／JobStore／产品验证。旧十件只引用，不复制。逐项最小供方请求见同目录 `supplier-requests.md`。

依据：C5 e5ad的真实Snapshot／Preview／BoundRdfProjection，以及固定fa988主文和三依赖矩阵；根10613B独审已全文读取并核hash。逐项身份见 `input-readback.json`。C5、原双审输入及父Goal不变。

## 接受的唯一编辑意图及可信边界

用户意图限：对**已存在individual的一条已存在dataProperty人工断言**修改object，保留subject、predicate与原fact ID。输入草稿可来自UI，不能带“已确认/可信/已计费”字段获得资格。T01受信host先取得bootstrap policy与真实issuer会话；**任何源读取、解码、物化前**已创建/取得唯一CostSession，源reader强制同会话预扣，后续不重建/替换。当前新供方决定对象/资源身份与生命周期，T02不能发行成本票或来源proof。

`change_preview(snapshot, commands=(), remove_facts=(oldFact,), add_facts=(newFact,))` 是C5已存在的纯生产入口；它先validate，最终计算candidate与RDF集合差。**Preview是普通不可变Python对象，可被直接构造；类型匹配、base_digest或客户端声明不能证明它来自真实生产调用。** 后继可信编排须从S1源及本次用户意图真实调用该入口，并由T01新S2独立重新投影/计算、原回滚预演比较，不能把外部传入的Preview当授权。

C5 `bind_rdf_projection` 只接受其固定Store2来源形状：project/projectRevision/dependencyVector/state，state含definitions/facts/mappingState，并复用批准旧Store校验；它保RDF全部支持和原ID，**不构造M元数据、public/internal关联或新S2 proof**。新M/business3供应必须给获准的完整兼容RDF读view及其与M/proof的绑定，或明确回报必要消费delta。不得由T02手造删字段snapshot来凑形状、截掉未知payload/M字段，或把旧source_ref改名当新proof。

## 概念输入（全部draft，未定序列化）

| draft概念 | 必需材料／真实来源 | 责任和拒绝边界 |
| --- | --- | --- |
| DraftTrustedScope | T01 public↔internal project绑定、当前host/engine session/authority scope、domain revision、完整dependencyVector/control、supplier/profile/policy与固定T02消费身份 | 由真实host与T01提供；UUID/摘要不创造权限。client project同字串不替映射；非当前/跨session/无许可拒绝 |
| DraftCostContext | 首次读取前已由原可信issuer建立的同一CostSession；可信bootstrap policy、固定调用profile、实际覆盖reader/阶段、spent/reserved/释放ack及失败累计状态 | T01资源owner；不接受仅costId、client计数或“已收费”布尔。超限先于实际调用，失败spent不退，reserved真实释放ack后返还；不拿wire/creation cap或worker内存代替 |
| DraftSourceBundle | 同连接一致读取的完整当前domain/RDF原记录、完整definition payload/control/mappingState、全部支持含triples下标、owner/source_row/managed_value与墓碑、显式跨层引用 | T01 S1；损坏/漏项/未知profile/不能完整投影则拒绝当前切片，不猜值。当前完整读view的source_ref与S2 proof分别解释 |
| DraftMetadataBinding | M五字段identifier/labels/definitions/synonyms/examples的真实home、完整集合/顺序/语言/缺失语义、schema/profile身份及其与source/proof的绑定 | T01 M；真实identifier缺失不派生/填localName。未改metadata也必须完整读取并保真；不要求全概念CRUD先完成，但不能少读字段或写第二metadata库 |
| DraftEditorBaseAndBinding | 从同一受信源完整投影的实际Snapshot，实际bind_rdf_projection结果；project/revision相符、全部RDF集合相等、所有支持原ID保留 | T01供应并可信编排调用C5；legacy绑定成功仅证其RDF域，不能抵M/proof授权。不能只用客户端Snapshot/hash/总数 |
| DraftFactEditIntent | 目标原fact记录的选择来源、旧S/P/O与本次新canonical object；不变的S/P、受支持dataProperty/domain/range；无entity命令 | 用户草稿不决定原ID，原ID从绑定源定位；值必须经已批准词项/模型校验。无效Unicode/N3/type固定分类，不显示解析器原文 |
| DraftActualPreview | 上述可信编排真实调用C5 change_preview所得完整Preview及原editor绑定，非手填expected/typed plan/proof | T01 S2独立复算与整域比对；初次成功不抵confirm/Job/commit再取源。new adapter不能直接裸调未校验snapshot_digest |

## 可翻译条件与保真oracle

下列条件必须**全部**成立；其余合法编辑仅是当前单事实段不可表示，保留草稿，不假称永久不支持或改变父FR范围。完整比较受同一CostSession执行前预扣，不能先复制/解析再检查预算。

| 条件 | 本段必须成立的精确判据 | 不能拿来替代的检查 |
| --- | --- | --- |
| C1 基准与新鲜度 | 原Preview经require_current核同一实际editor内容；bound.require_source核真实source；T01同时核当前public/internal、revision/vector/control/M/profile/policy完整proof | 私有digest/同revision/source_ref本身不证当前许可或完整M；每个事务仍须复验 |
| C2 真正一值替换 | removed与added各恰1个Triple；old.subject=new.subject，old.predicate=new.predicate，old.object≠new.object；subject为existing individual、predicate为existing dataProperty | 一个总计数或相同Diff长度；同值重提不创建空Job；改变S/P不是本切片 |
| C3 零实体变化 | commands为空；changed_entities/entity_changes/deletion_references全空；完整candidate实体按IRI键比较与base值相同，含全部多语言/文本/同义词/示例及结构字段；external_references不变 | 只看entity_changes字段；结构容器顺序可按既有canonical规则比较，但文本/metadata列表顺序不得随意排序/去重/归一化 |
| C4 唯一人工原支持 | old Triple在statement_sources的**全部支持恰1**，kind=fact且index=None；对应原fact为活动记录，S/P/O逐值核同，owner/source_row/managed_value均None | RDF集合去重后的一个元素；只挑一个manual fact忽略重复fact/definition支持；mapped override或墓碑不伪装manual |
| C5 slot与目标 | 同(S,P)全部活动fact恰该1条；new Triple在原全支持集合不存在（事实或ontology payload均查） | 只查可见页/当前选中记录；目标已存在或多值不能偷偷合并、删旧后称已替换 |
| C6 原ID可表示 | 原fact ID来自绑定源对应记录，满足新获准T01 typed格式；写入仍为该ID，即使新O使content hash不同 | 新ID=digest(newSPO)、IRI/localName/identifier充ID，或为了迁就schema换ID |
| C7 完整candidate | 完整candidate facts恰为base去old加new；全RDF对应差集；实体/外部引用/全部M保真；T01原回滚预演完整after与该candidate/RDF、完整原记录和control逐项相符 | 只比RDF/计数/hash总值，不比原records/M/映射/全部支持；unknown payload不能直接丢 |
| C8 成本与proof | 源读→投影→绑定→Preview→翻译→原预览/页/确认/Job/commit是同一成本上下文；新S2持久proof及原计划身份由T01实际核定 | 到adapter收到Preview才建预算；旧previewHash直接改名ontologyPreviewHash；client“完整/可信/已计费”声明 |

## draft输出与后续原机制

| 消费结果 | 允许产物 | 持久与授权含义 |
| --- | --- | --- |
| DraftTranslatedEdit | **唯一计划操作为原获准schema下的edits[原recordId]=new.object**；其余manual/remove/definitions等操作字段按新canonical要求缺席/空，不附带私造metadata/proof/cost字段。可伴随内部比较材料供T01独立复验，不形成第二权威账本 | 纯adapter不拿DB/路径/Store或writer权限，不confirm、不建Job、不commit；“可翻译”不等“可提交” |
| DraftRefusal | 下列draft分类＋已知存在的内部reason/location，或待T01统一映射的固定分类；保留用户草稿并失效本次可确认状态 | 不输出parser原文、输入内容或伪造canonical码；纯adapter零持久写；T01前序已成功preview/页/confirmation artifact可按原有界政策保留 |
| DraftPreparedDisplay（来自T01，非adapter签发） | 新版原planRef/previewHash/持久proof与完整Diff manifest、所有record/control/M/undo-impact段；页cursor链与合并UTF-8核验材料 | 不是当前T02 Preview字段；只有T01新同版合同定义。读到末页不等真人已读/确认 |
| DraftConfirmedSubmission（来自原确认机制） | 真人通过受信具名桥动作后，T01原confirm返回confirmationRef/preparedPlanRef/inputSnapshotId/parametersHash；后续原Job输入逐值采用这些真实返回 | renderer confirmed=true、model grant或恢复回调无确认权；queued/running不等领域写入。原commit的domain/evidence/receipt/result/succeeded同事务 |
| DraftReconciliationOrUndo | 提交不确定时读原operation/Job/result/receipt；undo是新当前源、新proof、新明确操作/预算的原preview→完整impact→确认→Job | 不改operation重放、不伪造逆plan、不把unknown当未提交；历史proof与当前proof分开。重开只读历史与新undo的budget边界由T01供方固定 |

## 失败输入／预期矩阵（未来判据；当前未执行、无Pass）

编号只是文档case ID；“拒绝”指阻止本次后续确认/接纳/写入，并清理相应可写资格。领域不部分写不等于所有库字节不变：原机制允许有界plan/blob/page/confirmation/Job历史；已提交成功更不能被晚到失败改写。漂移用例中由其它合法操作形成的变化保留，只要求本请求不额外写错。

| case／draft分类 | 具体输入或故障 | 精确预期与完整观察点 |
| --- | --- | --- |
| F01 无可信scope | publicId映到另一个internal project，或host/session/scope失效；客户端仍附原hash | 源reader/后续对应入口按真实授权拒绝；不以hash相同放行；没有本请求领域写 |
| F02 无M来源／缺字段 | 当前IRI没有真实identifier，或只给label未给definitions/synonyms/examples，或称unknown opaque等于空 | 整段拒绝、草稿保留；不派生identifier、不创造词汇/第二metadata home、不空集合补洞 |
| F03 来源／profile不兼容 | source损坏/摘要不匹配，或新M source不能无损进入旧C5 binding形状 | 固定来源/不兼容分类，在不可信投影使用前拒绝；交唯一owner列精确delta，不手造减字段来源 |
| F04 漏／替换支持 | 全RDF集合仍相同，但删一重复fact支持或替换一个definition原ID/triples index | 不能以RDF相等通过；完整supports/records/proof拒绝；源身份和payload全保留 |
| F05 未真实Preview | 手填Preview/candidate/changed_entities为空，但candidate暗改synonyms；或外部同形对象传入 | 受信实际调用与T01独立复算不匹配即拒绝；不靠isinstance/客户端摘要认证生产来源 |
| F06 一值条件不满足 | 0/0 noop，或2 removed/1 added，或S/P改变，或subject不是individual/predicate不是dataProperty | 当前段不可翻译；不建空Job、不拆成多个提交、不把合法更广操作永久关为unsupported |
| F07 entity/metadata夹带 | 恰1/1事实差集，同时改identifier/labels/definitions/synonyms/examples/类型/外部引用；伪造空EntityChange | 全candidate/源M比较拒绝，不只信空字段或RDF差集；原M保持 |
| F08 支持非唯一人工 | old由manual＋ontology payload重叠支持、两个fact支持、mapped/override或object=None墓碑 | 全部支持查询后拒绝，不挑其中manual、不删全部来源；所有记录/墓碑保持 |
| F09 slot／目标冲突 | 同(S,P)另一活动值；或new Triple已经由其它fact/definition支持 | 拒绝当前替换；不去重合并、不删旧保新而谎称单原ID更新 |
| F10 ID不兼容 | 原ID合法在源存在但不满足新typed形状；或candidate试图使用新content-hash ID | 固定不可表示分类；不重算/迁移ID。单条成功oracle必须核同原ID及所有归属字段 |
| F11 词项错误 | 非canonical N3、未配对surrogate、非法类型/语言、声明range不容新O | 通过获准模型/decoder给固定reason/location；不显示底层异常/原值，不替换Unicode或改digest编码 |
| F12 不完整after | 原Store回滚预演RDF正确但改了无关M、definition payload/reference、mappingState或control | 完整记录/metadata/control oracle拒绝；纯RDF核同不能替代。回滚预演不发布领域变更 |
| F13 四阶段同revision漂移 | preview保存前、confirm、Job接纳、排队后commit分别替换metadata/profile/policy/vector/control/支持，revision保持相同 | 各阶段在其原事务真实重取源拒绝，不能“包装层查过再跨await写”。已存在合法历史不修复/删除，当前新请求无部分领域写 |
| F14 绑定混淆 | 相同旧previewHash却不同新proof/planRef，跨项目复用plan，或同hash对应多个歧义plan | 新持久envelope/身份链拒绝，不选扫描第一项；旧Store preview identity不冒新proof |
| F15 Diff不完整／错页 | 少中段、跳页/同一段被重复拼入文档/错ordinal-offset、错误rawByteLength/hash、跨proof cursor、UTF-8字符恰跨segment | 原字节完整核同并合并后解码；受控同页重试依真实供方合同并计入同CostSession，不等于允许重复拼段；未完整不得确认；真实Diff保definition-status/M/undo-impact，不只渲染可见摘要 |
| F16 非真人或旧动作 | 模型grant/renderer布尔/自动恢复触发confirm；或真人点的是已切项目/版本/连接代次的旧Diff | 具名桥/原确认机制拒绝或失效；不自动重新确认/提交。仅fixture显式调用未来可验证机制，不记真人通过 |
| F17 首读预算失败 | 未有真实issuer/policy/session就调用reader；或首次源读预扣失败/reader中途失败 | 第一种不进入读取；预扣不足先拒绝；实际已执行失败成本累计，spent不退，槽2不新建/重置session。实际入口观察证明顺序，当前未运行 |
| F18 累计／驻留预算失败 | 各helper单独未超但合计超限；分页/重试/坏输入/旧plan历史消耗后再尝试；未释放却伪造reserved归还 | 同会话执行前拒绝、失败累计；真实释放ack才返还reserved。所用数值由新政策固定，不能拿旧方案工程数字填Pass |
| F19 排队／取消 | 已有真实queued Job后源漂移；queued/running取消分别在commit前与commit后到达 | 接纳不等成功，原writer门再验；提交前按原取消边界无领域写；已真实成功则保receipt/result/succeeded，晚取消不改成功 |
| F20 提交原子失败 | 在原domain/evidence/receipt/result/terminal持久阶段注入允许的事务故障 | 原事务完整rollback或完整成功，不得半条事实、半份M/receipt；失败断点由实际新T01供方/原hook固定，不另造writer或SQL |
| F21 提交后丢响应／重开 | commit成功后publish断开，恢复后当前源又合法变化；原operation查询或跨session历史读 | 保原真实成功与历史proof，按原receipt/Job/operation对账；unknown保持不确定、不换operation重放；不拿当前源变了否定旧成功 |
| F22 undo相交与非相交 | 后续改无关记录再undo；后续改同记录/形成依赖冲突再undo | 新当前proof/预算及完整undo-impact；前者只恢复原作用资源并保无关修改，后者展示冲突并拒绝。revision/history正常前进，不能要求全库回原字节 |

未来正向输入应由真实新S1给全源/M/issuer上下文，可信调用真实C5生产Preview，T01独立预演并沿其原确认/Job链完成；本件故意不给可以冒充真实供方的正向对象/返回值。合成领域数据可用于未来反例，不能手填被测typed plan/proof/meter或直接构造Preview代生产路径。所有失败case和成功完整oracle都待同版真实供方、明确新树/采用/写面后执行。

## 记录、责任与后继

T02仅提出上述消费条件/比较和draft分类；canonical、issuer、M home、原writer/确认/Job及固定错误由T01收口，I06只在其四壳桥路径接入批准命名表面并证明真实App/真人。未批准pin不import旧423或同名WIP充新发行者。完整M概念CRUD/多支持/跨层删除、I05完整Turtle/T08/T10不是**准备此矩阵**的前置；当前完整M读取保真和新S1/S2/成本/授权合同仍是**实际单事实链**的前置。

四P3继续原分流：digest入口边界与localGraph门控/memo在未来正式adapter新候选；深链Set为非阻断观察等真实Q5/设备条件；旧交付指针留历史，下次完整输入更新引用，不称旧文已修。C5、旧十件、根状态、父Goal及全部原验收/双新审/CI/正常合并/远端发布门均保持。本次无产品/SQL/JobStore/GUI/模型运行、无新公共schema、无第二writer或供方fixture。
