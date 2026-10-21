# 本体编辑真实供方：一致投影、Entity metadata 与原 ChangeSet 持久绑定方案

建议按 **S1真实只读源→M唯一metadata及完整原写链→S2持久来源proof→T02真实消费联验**推进。S1可独立先行，但不能用一个事实值编辑或永久missing/unsupported替代FR-200完整创建、编辑、复制、删除、Diff和undo。首选在既有ontology definition.payload中保存严格版本化Entity metadata，沿原Store/快照/plan/receipt承载；不新增metadata SQL表、第二plan、第二Job或确认账本。当前只有方案准备授权，下述代码窗口、语义profile升级和运行全部等待根分别批准。

## 1. 固定事实、授权与本轮边界

根准备原件实际6217B/SHA256 `d55528dc65449c83cc5961578f17bedeb47b0b24e0a1080593ba765e8e45a2e9` 已全文实读。T02固定4406103主方案44243B/`6b88b1f7a8e9b7b08719f6b48dda16905a3eb800a7b8baef21f4b7a26b06983c`，根审15654B/`c8c048c9d799e54d5eb4ad34324238a2ba834dcb724a7b020af50199fcb9cadc`均全文实读；最初合并工具输出被总额度截断后按bb4310/57d461/e032f5补读完整184行，没有把截断当全文。T02四模块仅从固定493及current核同后全文静态阅读，不copy/import/执行或修改其源/环境，不向T02或其他chat发消息。

T01产品唯一固定来源为 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`；5f为批准基础，C1原59交付、a33根收口、C2固定0a03539及并行dispatch新docs均只读。AGENTS15852B/78df、common17891B/e437完整第九节与无桌面规则继续。本文仅写本主说明和专属新review目录，不写产品、测试、旧方案、依赖、共享state或Goal，不stage/commit/push/PR/merge。所有函数行为是固定源码静态观察，以下测试都是将来计划；本轮产品/DB/测试/故障子进程/native/GUI/HMR/网络/模型运行新增0。

实际调查清单见本目录对应reviews下 `source-manifest.json`：69项逐current=fixed Git/bytes/SHA，其中52项为C1精确来源集合，补足原本已在5f的本地依赖、canonical资源、环境和T02四只读参考。`static-call-inventory.json`为stdlib AST静态函数/行号/调用库存，不是动态执行或包/PYZ闭包证据。初次从根cwd定位子树相对路径失败已保留工具输出并改正确cwd，不当产品失败或成功。

固定423b事实：Store.state仅definitions/facts/mappingState；definition.payload全文进入snapshot及before/after，`Store._definition`允许部分opaque对象但不验证Entity业务字段；`domain_changesets.supported:88`和canonical.changeSetOntologyValue只允许triples/singleValuedPredicates/references。T02 Entity强制非空identifier，labels/definitions为(text,language)，synonyms/examples为非RDF字段；source_projection保全部recordID/owner/source_row/managed_value/墓碑/多支持，绝不替owner生成metadata。project_host.metadata是项目级名称，不是Entity存储。

`ChangePreview.identity`只含原plan/state/control/intent等；旧envelope为preparedChangeSetVersion1，previewHash=storePreview.identity；_envelope扫描第一个匹配plan返回，confirm/accepted_plan/commit没有独立metadata/投影政策/vector proof。原机制确实需要修改，不能只包一次preview。

## 2. 阶段、树、精确采用与责任窗口

S1申请树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-ontology-projection`，branch `feature/weekly-t01-ontology-projection`，从批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 建立。逐清单52项采用423b原Git，单独adoption；不wholecommit、不采用其docs/可变HEAD/环境。清单额外已在5f的依赖保持原5f字节，采用时也逐核；不把34项T02旧manifest当本线授权。未来相对5f完整初始功能差异为52路径，S1新增2后54，不能只报两个writer。

| 阶段    | 拟产品/测试writer                                                                                                                                                                                                                                             | 前置与交付                                                                                                     |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| S1      | 新 `project/ontology_projection.py`；新 `tests/test_project_ontology_projection.py`                                                                                                                                                                           | 52输入全部只读，真实一致源及缺失材料、受限投影、原ID/全支持/引用和预算，真实只读正反例                         |
| M       | 新 `project/entity_metadata.py`；新 `tests/test_project_entity_metadata.py`；既有storage.py、project/format3.py、project/transactions.py、project/compensation.py、project/domain_changesets.py、job_store.py、project/applications.py；下述canonical精确集合 | 唯一home/字段原子写、严格读取/profile、metadata-only/复制删除Diff/undo、全快照/历史/包供应合同；不是仅新helper |
| S2      | 新 `project/ontology_changesets.py`；新 `tests/test_project_ontology_changesets.py`；既有domain_changesets.py、job_store.py、transactions.py、storage.py、format3.py、compensation.py及ontology_projection.py的精确meter/proof接点                            | 每个原事务内sourceBinding复验，原唯一plan/confirm/Job/receipt，持久增长预算；旧文件按下表逐项获准              |
| T02联验 | T02 owner新typed_changeset_adapter.py和新专属integration test；必要model/service/source_projection扩展须根另授新树精确writer                                                                                                                                  | 固定实际S1/M/S2新ref后在T02新隔离树逐项采用；T01不复制或改T02原493                                             |

M/S2未来树分别拟 `.worktrees/T01-ontology-metadata` / `feature/weekly-t01-ontology-metadata`、`.worktrees/T01-ontology-changeset-supplier` / `feature/weekly-t01-ontology-changeset-supplier`，均从根再次核准5f起；只能采用已完成独审的S1或M精确新ref/path/bytes/SHA，当前尚不存在这些产品ref，不能写假值。每阶段在根批准前提交更新manifest，列完整累计差异和writer/readonly角色。原52只读不自动转写，M/S2需要根序列化解锁下列具体路径；不能在S1窗口提前修改。

canonical申请集合：`packages/contracts/v2/schema.json`只新增严格metadata payload union/原typed plan可表达字段；`fixtures.json`、`binding-regressions.json`加入正反例；`registry.json`更新真实同版schema绑定；`packages/contracts/src/v2.ts`、`src/index.ts`及`python/contract_v2.py`仅相应类型/严格helper/消费导出。若现生成机制证明不需改某导出，以实际diff删去申请，不能手写第二schema。errors/states/协议名默认不增；必要新code或公共版本另申。不因内部S2签名增加新RPC/main/preload/UI或通用invoke。新profile实际打包资源闭包及registryHash变化需T03独立冻结，当前不改build/锁/依赖。

## 3. S1：同一真实库的一次全新只读一致源

拟私有入口 `read_ontology_source(real_job_store, publicProjectId, *, readerLimits, costSession)`。只接可信owner已持有、完整Job-ready且actual/target3的真实JobStore与原连接，不接path/factory/currentScope=true。unknown caller事务先拒而不rollback caller；BEGIN后同连接完成全部探测/读取/核证，成功/失败均finally ROLLBACK自己开启的事务。没有snapshot/public_project/project_get/reconcile/create/commit、第二连接、迁移或schema修复。外部authorizer禁全写仍成立，保owner原callback，不把authorizer当逐行计价器。

冻结消费材料为原T02 `bind_rdf_projection(source_ref, source, editor)`所需的真实source原形：`{project:internal,projectRevision,dependencyVector,state}`及其digest；另带public/internal真实映射、当前CP身份、retirementControl、完整metadata材料、支持定位和投影政策版本。它们是仅供实际T02构造Snapshot及S2proof复验的临时私有材料，不注册第二公共DTO，不给权限/物理绑定。T02 Snapshot.project用internal，写请求projectId用public，不能靠两个字符串碰巧相同混用。

S1真实步骤：

1. 形状/identity/预算前界、拒未知事务；BEGIN，核actual header3、Store/app/Job真实schema/catalog与同版ReadLimits aggregate guard。启动Store/Job原校验早于S1预算的风险另列，不声称新服务已解决。
2. SQL先count/typeof/长度/有限rowid，再完整行费用预扣，通过后才取payload并有界解码。覆盖public_projects/projects、versions、全部definitions/facts/mapping_state/definition_retirements；完整payload、所有显式references、归属与object=NULL墓碑均保留。不先json.loads再数节点，Unicode/NUL/深度/节点先界；SQL标量存储编码与canonical UTF8分开。
3. 复用原Store state/vector/retirement与format3混合history只读validator；所有传递SQL经私有view gate，原方法self绑定view而不是透传real boundmethod，不继承/构造Store、不替换real._db、无__getattr__SQL回退。当前链head、origin、全部operations/receipts/checkpoints/引用snapshot、旧app claim/confirm、当前app状态和域marker证据也先收费。不能只计返回source却在helper内无界读历史；全库guard与目标语义闭包分别满足。
4. 验当前CP.domainSnapshotRef真实存在，snapshot完整state/vector/revision与同事务当前值完全相同。source_ref是该真实正式域快照身份，不调用写snapshot以凑一个ref；缺链/不一致不修库，有限失败。retirement control纳入proof且不添加到T02冻结source的精确四键中。
5. 从全部RDF支持构造可表示的Entity输入/Fact输入，原term同版解析；所有rdf:type/label/comment/subClassOf/domain/range与人工事实共同参与。一个RDF有多个载体时保全statementSources，不以集合去重删来源；definition ID/原triples下标/重复项顺序全部在源中保留。mapped、override、墓碑也保留；没有把它们伪装manual。
6. 扫全project的metadata namespace及其home，核本节与§4规则。未知opaque payload保原字节，但若可能携metadata/引用而未有同版解释器，报告coverage-unavailable，不能默认不存在。只有完整已知schema位置均检查过，才发版本化missing材料。
7. 输出受限constructor inputs与完整source，不自动填identifier。T02真实validate/rdf_triples/bind在共同cost预扣后消费，完整RDF必须相等；不可表示的typed label/双角色/BNode/列表等保原source并给精确有限原因，不能静默删字段后宣称投影完整。S1可成功提供真实原源+缺失报告，但没有identifier政策时不得伪造T02可编辑Snapshot。

错误有限为invalid-input/state/resource-limit/identity-conflict/unsupported-source/incomplete-source/storage-busy/storage-failure，内部材料缺失原因另含metadata-not-recorded/coverage-unavailable，不展示SQL、原异常或业务正文。门在execute/fetch/iterator先将SQLite及资源控制错误转独立Exception，穿过旧format3捕获族，不误报incomplete。BEGIN/ROLLBACK控制槽保留，耗尽业务预算仍清理；释放失败保首因并通知owner，不伪称事务关闭。没有修改C2冻结文档或把尚未实施C2代码当现成依赖。

## 4. M首选：既有ontology payload的唯一版本化metadata home

首选payload增加唯一严格namespace，不新增SQL metadata表：

```text
ontology definition.value 原triples/singleValuedPredicates/references保持
+ entityMetadata = {
    entityMetadataVersion:1,
    entities:{ <完整Entity IRI> : {
      identifier:<真实英文标识>,
      labels:[[text,language],...],
      definitions:[[text,language],...],
      synonyms:[text,...], examples:[text,...]
    }, ... }
  }
```

五字段即业务英文标识、名称、定义、同义词、示例；名称/定义允许完整多语言集合，中文name选择真实zh标签，不由IRI尾部猜。identifier遵当前T02严格模式，原序列存取，不NFC/trim/casefold，不改变Entity IRI。字段顺序/列表顺序按真实业务含义保留，重复值严格拒绝；非法Unicode/NUL/长度先界。Entity IRI是RDF身份，definition ID是存储载体身份，identifier是业务字段，三者分离；修改identifier不重命名IRI，不把v_IRIhex写成英文标识。

一个project内每个IRI最多一个metadata home `(layer='ontology',definitionId,entityIRI)`，全库目标project扫描核唯一性；不同home即使内容相同也拒歧义，不first-match或合并。现有共享definition可容纳多个Entity；创建metadata时由可信owner明确选择实际ontology home，不能由IRI/localName猜definition ID。缺home时经用户明确动作选择/创建普通ontology definition载体，在同一plan内出现；保原ID。跨definition移动home是显式原子remove-old/add-new，并核全部references，不自动搬家。

该namespace是五业务字段的唯一持久权威。labels/definitions的RDF表示仍须与原rdfs:label/comment完整语句集合交叉核同；已有RDF支持不是可以随意抹掉的副本。新写同时更新metadata home及该Entity所选的全部实际label/comment载体，源支持清单与完整Diff明确显示。若部分RDF由映射/多个载体贡献而未获准如何改，先给冲突/影响，不能仅改metadata造成两种名称。业务字段保存不发明synonyms/examples RDF词汇；这些字段仅在metadata中，Turtle单独导出需metadata伴随包，不能宣称Turtle独自往返全部字段。

### 名称/定义的多语言、多值、多支持政策

本首选是payload五字段的唯一业务home，并非只把三项非RDF字段放payload。labels/definitions完整集合与RDF交叉核对，二者不是可各自修改的两套authority。若根最终改选“RDF label/comment唯一业务来源、payload仅三项”方案，必须以独立schema/projectionVersion更改本合同，不能在实现中混合两种政策。

准确predicate仅RDFS label=`http://www.w3.org/2000/01/rdf-schema#label`和comment=`http://www.w3.org/2000/01/rdf-schema#comment`，不把SKOS/自造predicate自动当同义字段。scope为当前project完整asserted source（全部ontology payload及活动fact）；推理结果/别库/当前页面子集不充authoritative。T02.labels/definitions实际是tuple集合而非只能一值，因此所有语言和值均传入，不first或按label排序挑一个。原Store term规范下语言tag小写，空语言保空；原source词法/支持仍原样保留，不声称规范化前文件词法相同。

中文主显示标签若需要单值，仅恰一个`language='zh'`候选时可作为显示选择；zh-CN/zh-Hans/无语言不隐式回退，多个zh值或只有其他语言时给`primary-name-unselected`材料：全部predicate/term/language/真实support列表，根或后续明确用户选择。T02编辑仍保全部labels/definitions，选择主显示不删除非选中值；定义同理，完整多值可以呈现，不排序取第一充“定义”。如UI/消费要求单一中文定义，另显式选择实际项并版本化该显示政策。当前模型不能表达typed label/comment时给coverage-unavailable，不把datatype丢掉；后续同版T02表示扩展由根路由，不能永久把合法原字段从FR删除。

全部非选中原RDF/support仍在sourceRef/proof/全Diff/undo/包中。同一label有manual与definition多支持时business集合只出现该值一次，support清单不折叠；编辑或删除该值必须按明确支持策略逐载体复核。跨多个home同IRI不是“多语言正常”而是权威歧义，即使文本一致也拒绝。五字段与RDF/缺失材料同一read事务取得，同一Store写事务、同一domain快照版本保存，不拼接后到metadata。

### 真正需要根选择的legacy缺失策略

| 策略                         | 读取行为与适用范围                                                                                                                   | 后续写链                                                                                    |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| L1 保真读取+显式补录（推荐） | S1保完整RDF/source与missing材料，label/comment标RDF来源；identifier/synonyms/examples保持未记录，不伪造空业务值；只读界面可显示缺失  | 完整编辑前先经原Diff/确认/Job一次真实补录metadata及RDF一致性；补录本身可撤销，不永久missing |
| L2 显式显示派生              | 仅根明确采纳后可生成displayIdentifier，标derived/version，来源IRI原字节；v_+hex仅一种可选display政策，不存identifier、不计FR英文标识 | 可做受限只读/已证明不触metadata的临时机制切片；完整FR仍先显式补录L1真实值                   |
| L3 严格metadata-first        | 缺metadata源仅保真读/报告，暂不构造T02 Entity；先完成M扩展和补录                                                                     | 首条正式编辑直接走全字段链，不绕必填identifier                                              |

默认不擅自选L2。建议根选L1，完整写入实施顺序按L3排M在S2/T02写联验前。根尚未选择前，不把该建议视为已批准政策。metadata明确存在且合法时直接真实读取；确定的空synonyms/examples与未记录不同。missing材料精确为schema/profile版本、扫描的全部ontology definition ID+payload digest、namespace不存在/Entity absent及unknown位置集合，纳sourceBinding；不接受caller metadataComplete=true。发生同revision补录/namespace或policy变化，missing材料摘要必变。

### 旧consumer安全与profile升级：不是未知字段直塞

仅把字段塞进opaque payload不足：固定Store._definition会略过未知字段，旧consumer可能开库继续写而不懂metadata，不能声称安全。申请一个**明确、根另批的metadata语义profile**，物理user_version仍3，app checkpoint形状/历史版本保持原1，既有definitions/snapshot schema不加列。

拟在既有app_format.schema_hash沿原不可变catalog中区分`legacy DDL-only hash`与`digest({ddl:原TABLES+TRIGGERS,payloadSchemas:{entityMetadata:1},readerSemantics:2})`。新hash明确是扩展payload schema/profile签名，不伪称原DDL hash；新validator双分派接受原profile1和严格profile2，旧固定validator仍按原SCHEMA_HASH严格比较，遇profile2安全拒绝。schema_version列及最终DDL仍原1，因为SQL表结构未变；新的metadata payload语义版本由签名明确标识。必须在设计批准时连同该字段扩展语义一起冻结，不能自行“随便换hash”。

旧库只读打开不自动升级，默认format2/显式3原库不被静默变更。metadata首次写之前，另行明确升级窗口消费已批准备份/lease/位置能力：同连接唯一外层事务内按实际原catalog全文核同，受控撤下并重建原immutable_app_format_UPDATE trigger以更新新签名；保migration_id/source_format/backup_hash原值，避免把C1 libraryEvidenceRef换掉而抹旧创建receipt；失败DDL/catalog均回滚。最终没有新表/列或放松trigger；非该唯一迁移函数不能改catalog。生产备份/首IO能力尚缺时只可规划/未来临时库验证，不造假路径权。

其必要性有固定源码的可审查静态反例，而非为了版本号改canonical：Store._definition:1014仅验证认识的references/triples/singleValuedPredicates而不拒其他dict键，_snapshot_state:1283将payload json.loads后仅canonical+_definition；旧rdf_snapshot.graph_from_snapshot:49只提取triples，丢失非RDF字段的解释。旧Store.commit:659–678会将definition.value完整canonical后INSERT OR REPLACE；内部旧caller给同id仅旧triples payload即可替换未知metadata，原Store不保护namespace。旧domain_changesets.supported会拒**被触及**的未知字段，但这不是所有Store入口的保护；旧format3 domain历史只核marker/plan/CP链，并不会因payload有metadata而拒开库。故不升级catalog时旧reader可接受/展示不完整语义，低层writer可丢未知字段。这里是源码路径反例，未运行旧产品/DB；未来须用固定旧source真实重开/写前拒绝测试证明profile门，不将静态推导冒充实测。

最小保护不是改旧name/plan canonical规则：只加strict namespace校验、同版catalog profile分派及唯一显式升级函数；旧marker/snapshot/context/plan的canonical字节不重算、不迁移五字段到历史。C1 model/libraryEvidence继续由保留的migration_id得到同原引用，CP schema1保持；新metadata只是domain definitions改变。C2当前固定计划只认识423b profile1，未来实现若先固定，M升级前必须根另授C2 consumer/profile校验适配及固定回归；不能让旧C2 gate偷偷接受未知新签名，或为metadata放宽其readonly52。次序为S1读旧profile→M新reader/升级机制及相应C1/C2消费测试固定→显式升级→S2新proof签发，物理备份/位置供应未到时只做已授权临时机制，不自动迁移生产。

该profile方案是首选无新表设计的必要安全措施，须单独审批。若根不接受复用schema_hash的payload语义，应改为显式app_format catalog版本2及其真正DDL/备份迁移，逐exact path另申；不能退回无版本opaque写。只有真实多home冲突/不可携带字段/包消费者不能保留namespace的具体反例才考虑新增metadata表；那会改变state/snapshot/hash/包/迁移全链，当前不预授通用schema权。

## 5. M的原子创建、编辑、复制、删除、Diff与undo

所有M写入仍经原typed preview→完整Diff/明确确认→changeset Job→Store.commit同一外层交易，metadata不另SQL提交。新namespace严格validator既在Store.commit写前/完整最终state校验，也在_snapshot_state/load/reopen/profile历史路径运行，不让其他Store入口绕过。根批准profile2后metadata-only也是domain修订：原revision/vector/ontology:home版本、before/after快照、marker、app receipt、Job context/result均真实前进；不写project app.name来冒充Entity名称。

| 操作                          | 完整原子效果及保存边界                                                                                                                                                                                                                                                            |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 创建类/对象属性/数据属性/个体 | 原声明/关系RDF实际载体+一个唯一home的全部五字段同plan；IRI存在、identifier冲突、引用/类型不适用先拒。RDF新增事实用原规范ID，结构definition实际ID由owner明确，非IRI猜值                                                                                                            |
| 编辑                          | 原Entity IRI及未变record IDs保持；identifier/非RDF metadata-only允许产生真实Diff/receipt；label/comment/层级/关系变化改实际全部获选支持及home，保无关payload键/顺序/重复支持，不重建整图覆盖                                                                                      |
| 复制                          | 显式新IRI+真实identifier+复制定义/五字段；新home选定，指向新IRI，不复制全部实例事实、映射owner、源行、旧confirmation/receipt。新旧对象可分别修改和undo                                                                                                                            |
| 删除                          | 先全引用影响：RDF subject/predicate/object、definition.references和实体层引用、mapping/constraint/rule/behavior/scenario/query来源必须有实际覆盖证据；任何供方不完整即拒删除并列缺口。按明确选择原子移除Entity各实际支持/home entry，保同definition其他Entity，不删共享载体无关项 |
| mapped/多支持                 | 不是永久unsupported。需明确“改一支持”或“移除该语句全部支持”的用户意图与原record定位；mapped覆写/墓碑/恢复遵原owner与重跑规则，canonical补精确动作后才开放；根另批准该支持动作delta，不可用remove_facts差集偷删                                                                    |

原state_diff把整definition视一resource，原compensation也整条definition冲突，不能假称同home两个Entity互不相交undo已支持。申请transactions.py和compensation.py识别严格metadata namespace的逻辑子资源 `(entity-metadata,layer,definitionId,entityIRI,field)`：RDF triples仍按实际支持/位置资源显示，metadata五字段按真实before/after完整显示；原整definition不透明字段同时有独立完整Diff，不双算成可绕过冲突的两份资源。补偿先重建全部desired definition payload并与当前未触字段合并，然后由唯一Store._apply_compensation原子写。ABA也按这些逻辑资源与后续完整history拒绝，同字段后来改回不视无冲突；不同Entity或同Entity不相交字段可保留后续值。完整删除/创建改变home存在性，与该Entity任一后续字段相交。

Store新增完整state metadata invariant：home唯一、标识/字段合法、IRI存在/类别合法、RDF标签/定义与metadata集合一致、references目标真实，异常整体回滚。metadata-only修改不要求伪造RDF差集；T02 changed_entities/entity_changes必须真的改变。所有快照保原definitions.payload全值，checkpoint.domainSnapshotRef因domain新值正确变化；旧快照profile1没字段仍按原版本解释，不追写旧context/marker/hash。语义profile签名原位置不改migration_id，C1原历史可验证。

包保留：T01供应完整definition payload、home索引、profile签名、payloadSchemaVersion及相关快照/receipt，定义内容原样参与T10 definitions角色；不能只导出graph或仅五字段文本。固定423b没有T10包生产者，本轮只定位到T10私有transfer/inspection.py审查路径，未将其可变WIP当固定包供应，不冒称已支持本namespace。根需向T10唯一owner冻结包版本/完整文件角色/hash/minReader/profile拒绝和导入先验全包后单事务规则；预检任何未知namespace/profile整体安全拒绝，不先吞字段。模板复制须显式保metadata home与实际IRI变换映射，保原IRIs的导入不能重写identity；完整包往返及Turtle+伴随metadata往返分别验，不把ZIP存在当成功。T10实际writer路径/新fixed ref由其owner经根返回前，该包验收未完成，不让T01猜写T10源。

## 6. S2：原job_plans内唯一持久来源绑定

申请preparedChangeSetVersion2，不新增第二plan表/receipt表。原v1精确字段继续历史只读校验，新ontology链只签v2，不把v1拼上可选proof便宽松接受。v2在原envelope新增精确字段 `sourceBinding`、`ontologyPreviewHash`、`costProfile`；原preview.pack全文保留storePreviewIdentity原语义，不改名、不把新hash写进它。

sourceBindingVersion1完整对象包括：实际public/internal、已有sourceSnapshotRef、当前revision、完整dependencyVector、retirementControl及其hash、当前CP引用、metadataProfileVersion/完整home材料hash或完整missing材料hash、projectionVersion、adapterVersion、legacyPolicyVersion、T02固定模型/适配来源版本和原constructor内容摘要。内容来自S1同事务真实源，不能由renderer自报；hash仅完整性，不证明I06物理dispatch/current scope。当前proof要逐字段核同，不以revision相同代替metadata/vector/control同值。RDF/records/支持均被完整sourceRef覆盖；metadata缺失材料和派生policy额外绑定，不仅hash客户端Snapshot。

新命名域：`ontologyPreviewHash=digest({ontologyPreviewVersion:1,storePreviewIdentity:preview.identity,sourceBinding})`。原响应previewHash字段返回该ontology hash；planRef仍digest(整个v2 envelope)。parameters改为changeSetParametersVersion2且其previewHash用ontology hash并绑定prepared命名域/version；原confirmation receipt升级changesetConfirmationReceiptVersion2，精确绑定request、sourceBindingHash、previewHash、planRef及原result。Job context仍原唯一plan=envelope，fingerprint=digest(fullContext)，input.parametersHash/preparedPlanRef沿原真实值；commit marker fingerprint继续ProjectTransactions._fingerprint(preview)，不将其冒称ontologyPreviewHash。

完整Diff manifest/documentHash及segments仍原机制；Diff文档纳metadata全字段before/after、来源/全部支持和删除影响。CURSOR_KIND新`changeset-document-v2`，binding含版本、planRef、ontologyPreviewHash、sourceBindingHash、原host/session/project/documentHash；旧v1 token不能给v2 completion，也不能给proof不同但storePreview相同的新plan。全扫描候选先计全部旧plan/detail/blob，再收集匹配的完整候选集合：0项有限冲突，>1个不同plan/proof拒歧义，不能first-match。明确相同精确重试与坏旧同hash冲突，普通INSERT OR IGNORE仍必须原行逐值核同，不能忽略坏行。

| 原真实外层事务与准确切点                                                                                                                      | 新proof/预算行为                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| domain_changesets.preview_changeset的`_application(project,'plan')`内，任何_snapshot_id/snapshot/_intern_blob/_persist_segments/plan INSERT前 | S1内部`read_current_in_transaction`只接原owner的同一受控事务token，不另BEGIN、不接受任意caller事务；核原current source/proof及真实T02candidate、原plan试算after全量相符；预算先于transactions.preview试算，预测全部artifact增长后再写 |
| confirm的原_application内、找existing或签confirmation前                                                                                       | 有existing先验证原receipt历史身份，精确重试返回原；新签必须核当前sourceBinding、完整v2cursor链、真实重新试算、metadata/完整Diff一致；currentproof不同不因已有storePreviewIdentity而签旧plan                                           |
| JobStore.create_changeset_job→create_job的原_transaction内，claim INSERT前                                                                    | 按原operation精确已受理重试先核历史context，不重新要求当前源仍旧；新接收在此同事务调用v2 accepted_plan(current=True)，完整source/proof核同再写jobs/claim。不能薄wrapper先查后跨事务create_job                                         |
| commit_job→domain_changesets.commit的原_application/Store transaction内，任何正式domain写前                                                   | 先看原已提交marker/terminal，历史幂等返回不受后续metadata变化误否定；首次提交核原confirmed v2plan历史、再S1当前源精确等proof，queued后漂移拒；真实Store commit仍唯一writer，末态全量核T02candidate/metadata/control/vector效果        |
| diff_page原事务内                                                                                                                             | 每次完整核v2plan/proof/history及预算；当前proof已过期可选择明确历史只读页但不能完成可确认token；首实现建议返回stale有限失败，不能页里假当前                                                                                           |

历史与当前分离是唯一validator的明确mode，不复制另一宽松validator：`validate_envelope(..., mode='historical'|'current')`先做同版完整immutable proof，再只在current核实际当前S1源。Job-ready/旧accepted重试/已提交receipt/undo目标用historical；新confirm/新Job接收/首次commit用current。历史proof里的source snapshot、metadata payload、absence/政策版可从原envelope/source快照完整重建核验，不能只留摘要且需当前库找旧缺失；sourceBinding保必要原材料或原immutable snapshotRefs，全部计plan/证据预算。成功后改metadata，原receipt仍真实；undo是新preview+新当前proof，旧target只作历史证据。

同request/issuedImplementation/Limits/knownJob不匹配沿原严格identity-conflict。unknown不能安全重试写，C2只读事实/正式resolution物理绑定规则不变。原scope/人类确认不是新proof的布尔副作用。

## 7. 执行前共享cost profile与实际hook

冻结申请`ontology-cost-profile-v1`，来源绑定本清单固定ref及新实现源码SHA，任一调用图/解析/副本/政策变化须重新独审。它是工程拒绝币，不是RSS/毫秒或SQLite opcode严格换算。上界取T02拟值、原canonical/ReadLimits、实际可信implementation/limits交集：source+metadata canonical≤1MiB、深度32、节点65536、records4096、distinctRDF4096、supports8192、references4096、单term16384B；typed plan≤65536、request≤131072及frame-1024、Diff≤1MiB/32段×32768；全链保留≤8MiB，work≤64MiB-work，term输入总bytes≤1MiB/解析次数≤12288。原ReadLimits项目256/validation_rows16384/bytes32MiB/work512MiB等不放大；页≤min(maxPageBytes,maxFrameBytes,262144)-1024，默认真实limits为page131072/frame262144，不能忽略更紧page。

共享CostSession是可信owner的有限临时资源对象，只记累计工作/term/阶段次数/当前保留，不是业务意图或权限账本，不存main JSON/localStorage。首次S1/首次T02 Snapshot前建立；同交互的S1/T02构造、validate/rdf/bind/change_preview、adapter、原preview/64次页/confirm/Job/commit/失败均消费同对象。失败不返已花work，只有实际结束的副本释放reserved；不能每helper重置1MiB或每页重新建预算。一次undo是新的明确用户操作，取新当前proof和新预算。

owner最大同时4个session、TTL≤60s、合计reserved≤8MiB；原游标同版TTL/槽继续，过期即不能签新confirm。一次preview、至多64页调用、一次成功confirm/一次新Job接收/一次首次commit；失败/重复页照扣。确认幂等读及已提交receipt读取有独立有限只读预算，不重新执行写phase。Store单writer同线程维护临时session→plan/job关联，非JSON可重造；session丢失禁止新写/签名，不从客户端plan捏造新quota。进程退出后既有reconcile_jobs按原独立生命周期处理未终态，不能恢复该session自动重派；已commit只读对账。实际Coordinator在同Store调用commit_job且在异常时fail_job，本内部机制可闭合；生产当前scope/lease/profile跨session恢复另门，不能说临时资源句柄就是dispatch能力。

计价定义（B为该调用实际将处理的canonical字节；N为完整记录/节点数；T为将解析的term数，L为其总UTF8字节；H/P为该事务将读的历史/旧plan材料总字节，含所有引用）：

- `Copy(B,k)=k*(B+64)`，每个同时存活canonical/asdict/深copy/编码缓冲在执行前reserve，真实释放才回收；排序比较预扣 `Sort(B,N)=2*(B+64)*(1+ceil(log2(max(1,N))))`。
- 每term在进入旧term parser前按其已界长度预扣 `Term(L,T)=16*L+1024*T`；这是保守工程收费，不声称所有RDF parserCPU上界。总次数/字节独立计，不拿graph去重后term数替全支持解析。
- 每次实际SQL先扣query1（总≤65536，BEGIN/最终ROLLBACK各预留1）、原raw结构guard；完整行canonical证据唯一row去重，重复实际SELECT读取工作按每次`128+fullRowBytes`累计。先count/typeof/长度探费再读正文，UTF8/UTF16收费方案可消费根批准的有限SQL probe算法；无根批准算法不得先整blob/UDF入Python后称预检。
- `Validate(B,N,T,L)=Copy(B,2)+Sort(B,N)+Term(L,T)+128*(N+1)`；`Rdf(B,N,K,LT)=Validate+Copy(B,2)+Sort(B,K)+Term(LT,K)`；`SourceBind=SnapshotShape+Rdf+Copy(B,3)+Sort(B,S)+Term(LS,S)`。SnapshotShape另收费Store._snapshot_state全definition/fact解析，不能重复引用免费执行。
- `ChangePreview`在普通无Delete分支预扣4×Validate（初始、candidate及两次rdf_triples内部）、2×Rdf的非Validate部分、1×snapshot_digest的asdict+两轮排序/编码、命令Copy及Diff集合。每个Delete的deletion_impact再加1×Validate+完整references枚举，不用“显式比较≤4”盖掉内部重复；Copy/Put构造candidate按完整上界而非实际减去字段。
- T01旧helper profile按实际材料 `Helper=8*(B+H+P+1024)*(1+Q)+Sort(B+H+P,N+S+Q)+Term(Lall,Tall)`，Q为原plans/operations/snapshots计数；这不是替代逐hook费用，而是调用前的保守phase预留。实际子调用逐项在该预留中扣，不足在进入该子调用前拒绝，不能先执行再补账。预留与实际work只扣一次，预留尚未用部分在phase成功/失败结束可以释放为未执行work；已经执行部分永不返。若静态profile不能证明包住某晚导入/分支，先新增meter hook或收紧该固定分支并给例证，不能猴补函数或假全成功。

准确必须新增的hook：S1 SQLgate在任何TEXT投影/解码前；T02 caller在Snapshot constructor/Triple constructor、validate、rdf_triples、bind_rdf_projection、change_preview、require_current/snapshot_digest前按固定内嵌调用数预留；domain_changesets在_envelope全plan/detail扫描、_verify_plan/unpack/_verify_document/_document/pack/_receipt、每页完整blob列表及confirm重试/重算前；transactions在_plan、preview真实试算、identity/diff/state_diff、preview_undo、reconcile/commit前；Store在state/load_snapshot/_project_snapshot/_snapshot_state、commit所有before/after、_invalidate全results扫描与_apply_compensation/retirement history前；format3全_history/application_state/checkpoint加载与applications.claim_context/confirmation/validate_plan前；JobStore在_accepted_job/get_job/_job_prepared_plan、_cursor/_new_cursor及Job/result/context拷贝前。历史退休/undo的递归旧CP/snapshot同样收费，不能只预留当前source。

这些真实深层接点无法由两个新S2文件自动获得。M/S2需给原writer增加显式可选私有meter参数/同owner `_cost_scope(session)`，每个实际解析/复制/SQL helper在入口先向同session预扣；不替换real._db，不猴补旧函数，不把fixture计数器当产品meter。旧调用不启新ontology链时保持原默认/hash；新profile执行中任何未登记旧helper/SQL模板先unsupported-profile，不能绕预算成功。若T02 frozenmodel内部新增分支导致caller预扣无法证明，根需另授新T02树model/service/source_projection精确meter writer及专测，原493不动；当前不假称两newT02文件永远足够。

正例的静态可行性不是运行通过：先选真实全字段source≤4096B、records≤8、supports≤12、term总输入≤2048B/次数≤32、旧plan+history合计≤24576B、Diff≤4096B（一段）、2次完整页调用；预留T02最多8个Validate/Rdf组及T01合计≤20个上述Helper量（S1/源复验5、preview/末态3、2页及重验4、confirm3、Job接收2、commit/发布3，内嵌重复归该组完整profile，不漏算），取Q≤8、每Helper term≤64且L≤2048B，另留32768B标量/结构余量，算得work保守申请≤60MiB、同时编码保留≤2MiB、term次数≤4096，低于64MiB/8MiB/12288。静态JSON样例positive-fixture-spec.json给真实五字段源canonical≤4096B及纯算式核对，20个Helper+8个Rdf组加32768单位余量为53529600工作单位（<64MiB-work）；并不构造Store或T02对象。这里是待实现profile的接受目标，不是独立证明实际body已经有这些上界：实施必须用同版静态计数/实际meter观察核精确组数，首完整正例真实通过才关闭门。若此组数不成立，先改profile/必要hook并给实际证据，不能测试只断言全拒绝。

## 8. 持久增长与每事务首写前总账

所有artifact增长由同一个可信budget和原连接在首INSERT/UPDATE/DDL前预测，包含原库全表实际rows/SQL字节+候选末态；预算不能只约束source入帧。采用完整typed行canonical与reader实际SQL长度两种口径分别核，库encoding必须实际探测，不能用Python UTF8冒充UTF16库CAST长度。同键已存在必须真实逐列核同，冲突不以INSERT OR IGNORE减掉预算。

| 阶段        | 需写前计入的真实材料                                                                                                                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| preview     | 真实当前snapshot若原表尚无、parameters blob、全部base64 segment blobs、job_plans完整v2 envelope、冲突undo-impact job_details及对应segments；真实Store试算产生的snapshots/marker/appCP/receipt虽回滚，也计执行工作与临时SQL增长峰值                                                    |
| page        | 每次cursor完整binding/position/previousCursor链、现有过期token清理SQL及其工作，旧64次重复页返回是否重用原token仍按实际读工作计；游标条数/TTL预检不能偷偷丢确认所需的历史链                                                                                                            |
| confirm     | job_confirmations与job_details原确认receipt两行、fresh preview试算全部临时增长、确认当前source/metadata proof读材料。无部分签名/孤儿receipt                                                                                                                                           |
| Job接收     | 完整jobs dto/context/fingerprint/run、唯一operation_claim、任何原runConfig blobs/准备材料；同operation历史已受理只读核，不新Job                                                                                                                                                       |
| commit/undo | definitions/facts/mapping_state/retirements/versions/projects末态，before/after snapshot、commits+commit_evidence、app head/checkpoint/operations/receipt、results/job_results/result_state/current_results/job_current、terminal Job DTO全部；失效会扫描/更新全results，临时峰值也计 |
| profile升级 | catalog/triggers实际迁移完整峰值/备份要求单独批准；不把它藏在一次普通preview里                                                                                                                                                                                                        |

每步按ReadLimits rows/bytes/work/schema/table/column与实际persistent增长/临时试算峰值交集拒绝，写后逐新增行/末态与候选核同，不同整事务回滚。metadata profile2当前目录/workspace投影仍有限，metadata本体新source守自己的更小界，不提高旧reader限额。原历史/receipts/已提交snapshots永久保留；job_plans/job_details/job_blobs有原immutable trigger，不能为回收预算擅删旧plan/确认。原机制没有可证明的plan垃圾清理生命周期，因此本方案明确总库有限增长后资源拒绝，成功artifact不承诺可回收；未来安全GC须另申请引用证明/trigger/历史兼容方案，不伪称TTL会删immutable plan。仅原已允许的cursor/list TTL槽与result payload cache可回收，保住receipt历史真实性。

## 9. 准确既有writer delta与不能遗漏的依赖

| 路径（engine src下除canonical）      | 必要职责与旧兼容                                                                                                                                                           |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| storage.py                           | 原commit metadata invariant、profile2写gate、state/snapshot严格读、补偿desired全量验证；资源scope/SQL/解析/复制深层hook；原默认format2和未启metadata旧plan fingerprint不变 |
| project/format3.py                   | metadata semantic catalog双profile验证/显式受控升级入口、完整历史/CP加载meter；旧CP/application schema1和migration_id/C1原创建receipt保持；旧reader真实拒新profile专项     |
| project/transactions.py              | 原_preview试算/commit/reconcile的proof同txn接点、元数据逻辑Diff/undo资源/保留工作hook；原storePreviewIdentity域不改，metadata在原state本来就会进hash                       |
| project/compensation.py              | metadata子资源/存在性/ABA与不相交undo、retirement历史所有load先收费；不另写SQL或逆plan                                                                                     |
| project/domain_changesets.py         | supported接严格namespace、v1/v2 envelope/参数/receipt/cursor全分派、歧义候选集合、历史vs当前proof、四原事务复验及所有artifact增长/旧plan/分页meter                         |
| job_store.py                         | 新接收与首次commit同真实交易proof验证、历史精确幂等、private CostSession绑定/失效、原helper深层meter、结果发布与签名两行增长；不再Job或Job context宽松fallback             |
| project/applications.py              | 旧app混合history/claim/confirmation/validate_plan的显式meter传播，默认旧validator/hash不动；不把新ontologyproof改旧namespace                                               |
| project/ontology_projection.py       | S1新供方在M后解析strict metadata、同一读源/absence及复验供S2；共享cost定义及有界gate复用，不复制S1第二权威                                                                 |
| project/entity_metadata.py（新）     | 唯一字段/home/schema版本与逻辑Diff/纯校验/合并 helper，不持SQL连接或commit权                                                                                               |
| project/ontology_changesets.py（新） | 可信来源/真实T02candidate比较和profile编排，不独立plan/receipt/SQLwriter                                                                                                   |
| coordinator.py（仅生产消费后续窗口） | 真cost session生命周期/超限安全错误与原Job收尾，当前内部临时JobStore联验不改路由；如其跨await使session过期必须有限失败，不重建权限/预算                                    |
| resources.py/canonical消费集         | 真实profile/implementation/registryHash/limits的同版来源与版本绑定。不能拿fixture IMPL当生产identity。是否打包变更由T03另定，不改依赖锁                                    |

S1阶段只新projection与专测，不需上述M/S2旧writer。M/S2具体diff若能证明某路径无改动则移出窗口并留理由；不能反向以“期望不改”跳过实际深层调用。rdf_snapshot.py的Q6 term语义不改，纯调用前费用由父meter预扣；若需parser内部meter新delta必须根另申。引用覆盖I05/I06/T03/T05/T08/T10维护权不转移，S1只实读definitions.references，不能把未到的IRI目标映射供方当“全引用为零”。

## 10. 真实临时JobStore→T02→Diff→确认→Job→undo矩阵

本轮未执行。获批后每阶段独立新树/独立环境，以实际JobStore(target_format=3)、同版canonical和实际供应源码构造临时库；fixture建立可用原Store，但被测编辑必须真实T02 change_preview产出，不手填plan/Preview或假supplier。确认用显式机制fixture，真人/current_scope/位置/跨OS不混记。

| 组            | 必须真实证明                                                                                                                                                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1零写        | authorizer禁全写、完整dump不变、trace恰BEGIN→读→ROLLBACK、未知caller事务不rollback；当前source/ref/vector/control/所有support与已有CP一致；超额body未读取/未解析，失败重开零修复                                                                              |
| metadata/home | 真实五字段持久/重开、同IRI跨home同值也歧义拒绝、不同IRI同identifier按获批冲突政策拒绝、unknown namespace不当missing、same revision补录/缺失材料漂移；L1补录全Diff/确认/Job及undo                                                                              |
| 完整FR200     | 四类分别创建/编辑/复制/删除；metadata-only、中文多语言/定义/同义词/示例全量读回、identifier变而IRI不变、同definition多Entity不丢字段；copy不复制实例事实；删除全引用影响/不完整拒绝                                                                           |
| 真整链        | 实际S1源→真实T02 Snapshot/rdf/bind/change_preview→typed adapter→v2原preview→读全Diff/metadata/支持→显式fixture确认→真实queued/running/commit→全域/metadata/原IDs/vector/control/receipt读回→原undo全链                                                        |
| 支持/RDF      | 原fact对象变后ID保持（含合法非内容hash原ID）、多载体/重复triples/typed label/语言/映射墓碑/人工override逐项保真；不可表示不截断；获批多支持动作选择影响每个真实来源，不delete全部误报                                                                         |
| 四事务漂移    | preview保存、confirm、createJob claim、queued后commit各自同revision改metadata/absence/policy/vector/control/ref，旧proof均拒且该事务零部分artifact/域写；wrapper前检查后跨事务漂移反例必须失败                                                                |
| 版本/分页     | v1历史完整读与v2新写安全拒绝/接受，v1 cursor不能确认v2；same storePreview不同proof/hash、歧义plan、坏segment/最后一页/多字节切段/跳页/重放/expiry/cancel不可签；完整Diff而非末页标记当真人                                                                    |
| 历史/undo     | 已提交后metadata/current source变仍真实历史receipt；新undo用当前proof、target用历史proof；不同Entity/字段不相交修改保留，同资源ABA/后续引用/单值冲突完整impact拒；缺旧metadata/home/plan/confirm/CP不修复                                                     |
| 预算          | 所有bytes/records/supports/term次数/深度/节点/pool/work/query/page/profile/持久增长各±1；第一次旧函数尚未进入、重复失败不退款、第65页拒；共享snapshot免唯一行bytes但重复SQL/parse照扣；至少完整全字段正例真通过                                               |
| 原子/响应     | profile catalog/triggers、preview snapshot/blob/plan、confirm两行、Job claim/context、commit域/metadata/CP/receipt/result/terminal每边界异常/真实SQLite拒写/授权后的自有退出，完整dump判零部分或完整commit；commit后响应丢失仅原operation/receipt对账，不重派 |
| 包/端         | T10实际同版包全字段/home/profile/历史往返、Turtle+metadata伴随文件、unknown最小reader拒绝及旧consumer拒新profile；正式位置I06/named桥/T08草稿/真人Win/macOS/实际App另owner独立证据                                                                            |

静态方案通过之后仍必须由根分别发精确S1/M/S2/T02代码窗口；复杂实现按固定最终候选独立agent审查、实际check/verify:sources及指定GLM-5.3最高/M3.1-Flash xhigh两个全新真实同版外审、CI/正常develop/远端核验继续。FR200–204、57P0/C–G/PRD10–12与完整Goal没有因本内部机制或单一切片关闭。

## 11. read-ready交付与根选择

本轮交付主方案、69项固定来源manifest、静态调用库存和调查说明；独立审查由根另派其他agent，本文不自行写独审通过。建议根先选择legacy L1并确认metadata payload唯一home与semantic profile路径，再只批准S1两个newwriter；S1读实源固定后批准M完整写链与必要canonical/reader安全delta，再批准S2持久proof/meter与T02真正消费联验。若根暂不选择legacy，不阻本轮文档和S1保真缺失报告设计，但阻必填identifier的正式编辑；不擅自默认v_IRIhex。

尚缺供方明确为：Entity业务identifier唯一性范围/legacy选择、metadata profile升级备份与I06位置用途、跨层引用到IRI完整映射、T10实际包版本、新scope/named桥及真实人类动作。它们应由根路由真实owner，不能由T01私有hash/permission文字代造，也不把最终目标改成永远unknown。该方案申请可审查具体实现路径，当前没有新树、产品、DB或测试运行许可。
