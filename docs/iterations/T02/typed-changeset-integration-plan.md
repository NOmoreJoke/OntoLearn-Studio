# T02 → T01：本体编辑到唯一 typed ChangeSet 的集成方案

本方案建议先实现“一条已有人工数据事实修改值、保留原 fact ID”的真实内部链。它消费 T02 实际 `change_preview` 结果，复用 T01 原 preview、完整 Diff、确认、Job、receipt 和 undo。当前只完成静态调查与方案，尚未获得采用、供方实现或运行授权；第一切片不替代 FR-200–204 全验收。

## 1. 固定输入、当前状态与实施边界

实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology`，分支 `feature/weekly-t02-ontology`，接收 HEAD `b54bb81f431fc5a7a4b12c76952b7e15a743dbff`。Goal 工具实际读回为 blocked；本次有界方案准备不重建、不声称恢复。AGENTS 未暂存，SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；两张未跟踪截图保持原字节，见 `../../reviews/T02/typed-changeset-integration-plan/intake.json`。

只读起点为 T02 `49321221733ea927484647352e05e7d833cebc86` 与 T01 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`。T01 当前树 HEAD 是 a33cc80，不能跟随其 WIP；本方案所有源码定位按固定 423b。已逐项核对来源清单 34 项 current bytes = 固定 Git bytes；其中14项是拟内部 Job/Store/host 静态本地 import 闭包，另外列 canonical/resources、T02四模块、参考测试和批准环境。完整 path/ref/bytes/SHA 见 `../../reviews/T02/typed-changeset-integration-plan/source-manifest.json`，清单不等于采用许可或完整发行包闭包。

总控准备指令及 readiness 审计、共同指令、Q6 用户采纳回执均记录在同清单。Q6 沿用户已采纳决定：固定 RDF 1.1 Concepts 2014-02-25、SHACL 2017-07-20、SPARQL 1.1 Query 2013-03-21、XSD 1.1 Part 2 2012-04-05；不跟随 latest，不再询问。不在 T02 重实现规则比较或擅自扩大语义类型。

本轮唯一主文档是本文件，其他新文件仅在上述 review 目录；不修改旧 status、旧候选、共享路径或截图。只有格式、Git/hash、stdlib 文本/AST 静态读取；没有 import 产品、产品测试、GUI/native/HMR、模型、用户文件内容 IO、push/PR/merge。调查中首次资源路径定位失败已改用固定 Git 实际路径，不把它算产品运行失败或验证。

## 2. 实际生产者与消费者

| 固定源码切点                                    | 实际行为                                                                                                                          | 不能据此推断的能力                                                                       |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| T02 `ontology/model.py`                         | `Snapshot(project,revision,entities,facts,external_references)`；IRI作身份；Fact只含S/P/O，Entity含identifier/synonyms/examples等 | 没有原fact ID、公开project UUID、Store权限或metadata来源证明                             |
| T02 `service.py::change_preview`                | 真实命令产生 candidate、全RDF added/removed、完整Entity before/after、删除引用、base_digest；`require_current`查同版本内容        | 私有Preview不是T01持久plan/previewHash/确认凭据                                          |
| T02 `source_projection.py::bind_rdf_projection` | 同源完整RDF集合相等；保留全部factID/owner/source_row/managed_value、墓碑、definition payload digest、三元组原位置及全部支持       | 不构造可信metadata，不生成写计划；`removed_sources`不能直接删除所有记录                  |
| T01 `domain_changesets.py:88–127`               | 只允许被触及ontology payload的triples/singleValuedPredicates/references；只允许owner/source_row/managed_value全None的人工fact     | 不是全本体metadata或mapped/多支持操作能力                                                |
| T01 `transactions.py::preview/commit`           | 原Store.commit试算后回滚；绑定完整before/after及retirement control，提交前后全量核对                                              | 不能用T02布尔“已确认”直接调用底层commit                                                  |
| T01 `project_host.py::workspace_read`           | 当前项目metadata、已有checkpoint domainSnapshotRef和draft的受限只读投影                                                           | 项目metadata是名称等项目级信息，不是Entity元数据；workspace不返回完整domain/本体metadata |

T02 `service.py` 7896B/SHA `fa49220fbc812f6e94f6c0c19b6ceff82cb00fa9843f1e7238f6c196f7c839cf`；source_projection 7422B/SHA `919e6f055c84ddb55de985c66093d585b53ea9f78e167c2aa85dabb224c0c8e2`；T01 domain_changesets 34728B/SHA `e38f9d58a31f3bb38dc7b2da58f3da26811d3a6cfcc2a5f43a5a10f9b71dfb9a`。这些是源码证据，本轮没有运行它们。

## 3. 逐字段来源与完整映射

所有“拟”规则均待T01供方和root批准；不在T02造第二公共DTO、Store、Job或提交入口。

| T02生产字段/概念                            | 真实T01来源与翻译规则                                                                                                                 | 边界/必要供方                                                                                                                                                                  |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| project/revision/base_digest                | `Snapshot.project`须是源快照的内部project，revision须同一当前domain revision；外部请求的projectId必须由T01实际public→internal映射取得 | 两身份不得凭相等字符串代替。源ref、dependencyVector、retirement control和metadata绑定同一次读；hash只证完整性                                                                  |
| candidate/added/removed                     | 从真实`change_preview`产生；适配器重新核 `preview.require_current`、完整RDF before/after，不能接受手填Diff                            | T01在原preview重新计算完整Store after；比较全RDF和完整records/metadata，不只比较计数或Diff长度                                                                                 |
| fact S/P                                    | 原事实记录的subject/predicate；对象值编辑不改变两者                                                                                   | 更换S/P不是同一记录值修改，后置明确删除/新增规则                                                                                                                               |
| fact object                                 | 原canonical RDF term字符串；保留完整IRI、语言标签和类型语义，以同版term规范复验                                                       | 不trim/NFC/casefold业务文本；原Store把xsd:string归simple、language转小写的既有规范不可伪称原文件词法保持。完整原source记录不被改写                                             |
| 原fact ID                                   | `BoundRdfProjection.facts`及statement_sources定位的真实record_id                                                                      | 编辑用`plan.edits[原ID]=新object`，绝不重算ID；新增才由T01原`digest([S,P,O])`规范生成。ID形状不符合typed hash时准确拒绝，不改ID迁就schema                                      |
| owner/source_row/managed_value              | 从真实快照按原记录逐字段保留，包括object=None的墓碑                                                                                   | 首切片必须全None；mapped或人工override不能伪装manual。墓碑不是RDF，也不能被重建成新事实                                                                                        |
| 多重支持                                    | statement_sources的fact或ontology-definition ID及原triples下标，完整保留同一RDF的所有支持                                             | RDF集合去重不等于唯一来源。一条语句有任意额外支持即不进入首切片；不能逐源remove或只删一个后谎报语句已移除                                                                      |
| definition ID/IRI                           | 实际(layer,id)与payload位置是权威；IRI仅RDF身份                                                                                       | 不把IRI/localName当definition ID，不猜一实体一definition；共享definition可能容纳多实体。后续修改须原payload完整read-modify-preview，不丢无关triples/顺序/重复支持              |
| kinds/class_type/parents/domain/range/types | 原type、subClassOf、domain/range公理及人工事实均可贡献；同RDF统一一个编辑入口                                                         | 保留owl:Class/rdfs:Class原声明，不把结构关系解释成必有实例或校验。重叠类声明、双角色等当前Entity不能无损表达时整体拒绝本切片，后续扩展投影                                     |
| labels/definitions                          | 所有label/comment原RDF项及其原支持，按语言完整集合进入Entity                                                                          | 原模型只支持(text,language)，typed label/comment及不可表示类型须拒绝；不能悄悄转成无类型或丢项                                                                                 |
| identifier/synonyms/examples                | 当前没有获批的Entity持久metadata schema或读取器。`project_host`项目metadata不填此洞                                                   | 必须T01定义唯一版本化字段存放/读取/写入/undo/包保留规则；T02不得发明RDF词汇或把这些编码进label/comment。metadata-only修改当前typed不可表示，整批拒绝并保持草稿，不永久删除此P0 |
| singleValuedPredicates                      | 原ontology payload集合原字节保留，由T01原Store校验slots                                                                               | 不是rdfs:range/domain的必填含义，不是SHACL maxCount替身；首切片不修改该集合                                                                                                    |
| references/external_references              | definition.references真实(layer,id)边；到实体IRI的关系须供方显式解释并返回真实来源ID                                                  | 不凭definition ID猜IRI。删除影响要覆盖mapping/constraint/rule/behavior/scenario/query，缺少可信引用覆盖则拒绝删除，而非显示“无引用”                                            |
| blank nodes/列表                            | 当前rdf_snapshot.term与T02 Triple拒绝BNode；Store当前normalized triples不支持该通用表示                                               | 附录C允许的SHACL值列表仍是父P0，不能以首切片拒绝代全实现。I05/T05/T01后续共同提供保留/模板表示、身份及原子写合同；不跳过不认识的graph后做局部相等                              |

### 可信当前投影的具体缺口

请求T01提供单次同连接一致读的私有供应服务：实际已开JobStore3、真实public/internal映射、现revision/vector/state、原事实和所有definition payload/显式引用、retirement control，以及同版完整metadata来源。使用其原验证器与实际ReadLimits先限量再物化，不把`Store.snapshot()`误当只读：该方法可能INSERT snapshots。初始只读可以读取已有checkpoint的真实快照并复验其与当前state/vector完全一致；若需要制作新的预览snapshot，只能由原T01 preview原子持久化，明确计入其plan artifacts。

当前Entity要求非空合法identifier，而metadata schema缺失。因此即使首切片不改metadata，也不能默填一个英文标识冒充真实保存值。建议T01供方对确证“无持久Entity metadata”的源，明确提供只用于本次显示的派生identifier：`v_`加完整IRI的UTF-8十六进制，标注其派生来源，不写库、不计FR-200英文标识已实现；labels等仍来自原RDF，synonyms/examples仅在完整源可证明不存在时为空。该规则是待批准的投影政策，不是现成供方。真实已存metadata须从同一受信源完整保留；未知opaque字段/无法证明缺失时整体拒绝。若T01不接受此只读派生政策，应先实施唯一metadata扩展，再启动首切片，不绕过必填字段。

T02新适配器仍使用现有Snapshot/Preview/BoundRdfProjection与T01原changeSetPlan，不另造公共DTO。派生来源/完整metadata证明如何在T01供应及复验中绑定，由T01在其单一私有合同确定；客户端不得提交“trusted=True”“metadataComplete=True”来获得权限。T01负责同版supplier内部重新投影/比较，不信任T02自述。

## 4. 首条可表示编辑与精确翻译

选取已有individual的一条人工dataProperty断言，旧值和新值为当前T02已支持的canonical字面量。首样例可用plain string；另以integer/中文换行/语言项验证当前支持的实际语义。结构定义、metadata、其他事实、映射和墓碑全部保持。

入选必须同时满足：完整源可投影；本次真实Preview恰一removed、一added；S/P相同且O不同；entity_changes、changed_entities、deletion_references均空；candidate其它字段与原完全相同；removed的所有支持恰一个人工fact，且同(S,P)活动事实只有该一条；没有ontology payload重叠支持；目标新三元组无其他支持；原ID满足typed形状。该收窄消除从无序Diff猜配对的问题。更多修改仍保留原P0后续，不把“只支持一值”当产品终态。

1. T01可信供应构造真实原Snapshot与绑定源；T02 `bind_rdf_projection`完整核对。T02从用户草稿调用真实`change_preview(snapshot,remove_facts=(oldFact,),add_facts=(newFact,))`；不预填Preview或typed plan。
2. 新适配器消费该实际Preview及原绑定，复验上述谓词与预算；由removed_sources定位原ID，但把全部支持先分类/核完整，不直接删除。唯一产出为T01原schema形状的`plan={edits:{record_id: added.object}}`，没有manual/remove/definitions。
3. T01供应服务同事务重读当前源/metadata/control，复验原ref、版本、完整内容及T02候选；使用原schema验证request，调用其原`preview_changeset(publicId,base,{projectId,baseRevision,intent:'change',plan},host_client_id,engine_session_id,limits)`。原ProjectTransactions试算仍为唯一Store委托。
4. 检查原preview的完整after：原factID/S/P/归属全不变、只O改变；其他definitions/facts/mappingState/control/metadata逐项完全相同；完整RDF恰等于T02 candidate。T02私有base_digest不能替换T01 previewHash，所有原T01哈希各自使用。

不在T02适配器里调用SQL、Store.commit、confirm或create_job。调用组织与复验留T01同一可信owner服务；供方尚未实现时不能把直接调用原typed API的fixture当正式授权链。

### 后续全域翻译的最小规则申请

人工事实新增用T01原manual规范；删除用原ID remove；同ID对象修改用edits；多条/换S/P的配对须显式领域编辑意图及原支持身份，由T01复验，不从RDF差集猜。类/属性/层级/label/comment更改按原支持改对应ontology payload或原人工fact，跨多个载体一次原子preview；复制只复制定义/metadata，不暗中复制所有实例事实。删实体先真实完整引用影响，确认后按获批策略处理所有引用；首切片暂不删实体。

mapped覆盖/恢复/删除必须由T01扩展supported、canonical、原owner冲突/墓碑/重跑与undo规则后才能进入。多重支持编辑要明确是改一来源还是移除语句所有支持，完整Diff必须呈现来源选择和剩余支持；没有该选择不能保存。Entity metadata扩展须在同一原Store事务/完整Diff/receipt/undo中持久化，不另建可变权威或串行第二次commit。具体格式由T01决定并经root冻结，不在本方案暗批。

## 5. FR-200–204 全覆盖与仍需完成的验收

| 原P0要求                                                         | 当前493及423b静态证据                                                         | 首切片贡献                                   | 后续实现/供方与完整验收                                                                                                                 |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| FR-200 类/对象属性/数据属性/个体创建编辑复制删除、层级与基本关系 | T02私有Put/Copy/Delete与引用影响；T01仅typed子集持久机制                      | 一条事实值编辑，不能计全部概念管理           | T02多操作到原IDs/全支持翻译；T01完整metadata/定义定位及引用投影；真实创建/编辑/复制/删除各正反例与原子保存/undo                         |
| FR-200 中文名/英文标识/定义/同义词/示例、删除影响                | label/comment及metadata Diff已有；metadata无权威持久映射，typed label等有缺口 | 完整保持或准确拒绝，派生标识不能冒充正式字段 | T01唯一metadata版本/存取/完整Diff/迁移包规则；T02完整字段与跨层影响；全量往返/metadata-only更新/撤销/缺字段拒绝                         |
| FR-201 区分结构定义与实例断言、实际RDF核对                       | T02分字段生成，原RDF来源绑定                                                  | 真实人工实例事实→typed edit→RDF/原ID核验     | domain/range/子类/type与对象/数据断言各独立编辑；不得推成必有关系，实例创建/新增/删除完整链                                             |
| FR-202 类树、表格、局部图，核心流程不依赖大图                    | 私有页面/纯view-model已有，未接正式App                                        | 内部链不增加App通过证据                      | T01可信分页读取及当前身份，I06余下四壳桥/App；实际交互、键盘、切项目/late/stale、邻域图与完整集合一致                                   |
| FR-203 支持范围Turtle导入/导出，越界拒绝不损原件                 | 私有样例非正式安全parser/支持检查器；BNode/模板列表不可表示                   | 无导入导出完成项                             | I05批准同版Turtle/capability，T05模板及T01批次原子导入，T10包metadata；合法支持/合法不支持/语法错/多语言类型/列表及主流工具固定样例往返 |
| FR-204 Agent草稿不覆盖，FR-804 Diff/确认/原子/undo               | T02Preview不是提交；T01原确认/Job链已有                                       | 临时库真实机制链，确认fixture单列            | T08真实草稿/当前源，T01当前scope/named桥/版本绑定，真人动作/取消/损坏/恢复/实际App与完整双审                                            |

上述未支持项是同一原功能的后置实现与验收，不是永久unsupported政策。完整57P0、附录C–G及第10–12节、目标Win/macOS与真人、同候选两指定新审、实际CI/正常合并/远端门均保持。

## 6. 完整Diff、确认、Job与恢复的真实链

内部临时库允许将可信调用上下文与人类点击分别标为fixture；不得声称认证真人、生产当前scope或用户位置权限。正式当前权限必须来自真实host/scope供应，不能由UUID、摘要或permission文字创造。

原preview响应的manifest/documentHash按全部segment顺序、ordinal/offset/rawByteLength/sha256/base64严格读全；UTF-8按合并后完整bytes解码（32768字节分块可切开多字节字符），核documentHash。展示原完整record Diff及T02语义before/after，附metadata/来源和删除影响；差异或不完整不得确认。只读到末页不是人类确认。

明确的人类动作绑定当前project/session、精确previewHash与末页completionCursor；T01原confirm_changeset重新校验完整cursor链、原plan、当前revision及重新试算，生成原confirmationRef/preparedPlanRef/inputSnapshotId/parametersHash。T02/Agent不得自动调用确认。临时机制测试由显式fixture步骤调用此原方法，单独报告“机制确认”，不记真人通过。

原create_changeset_job输入严格取确认结果：scope=asserted、definitionId=changeset、derivedResultIds=[]，inputSnapshotId/parametersHash/preparedPlanRef逐值原样；operationId为实际请求稳定UUID，implementation与limits须获批同版，不照抄旧测试IMPL占位值当生产身份。随后原start_job→commit_job发布原commit.receipt.v1/resultRef及operation marker，当前完整域/失效/历史由原Store/Job决定。

Job取消遵循原queued/running/committed边界；取消在提交前收尾则域无变化，已commit后取消或响应丢失不能回滚成未保存。用原operation_get/get_job/result读取及不可变confirmation receipt/context对账；跨session仅查询原Job/marker，不改operation或重签后重放。unknown不当uncommitted，缺证据不新建任务重试；生产物理归因与完整resolution尚需T01 C2/host供应，本切片内部同库对账不冒充该能力。

undo走原preview_changeset(intent='undo',targetOperationId)→完整diff/undo-impact→明确机制确认→原Job。完整读回原变化资源恢复而不相交后续修改保留；同记录/后续依赖冲突须展示完整impact且拒绝提交，不伪造逆plan或调用另一writer。revision/history/Job等审计字段合法前进，不能要求undo后全库字节等于原库。

## 7. 有限预算与拒绝边界

下列是拟首切片工程拒绝上界，待T01/root确认；不是Q5容量、毫秒/RSS测量或Q6语义收窄。最终有效上界为此表、供应方实际更紧政策及原canonical/ReadLimits的交集。bool不作整数、非法Unicode/NUL按字段规范拒绝；不截断输入、不分批偷偷提交。

| 对象/工作                | 首切片拟有限上界及计费点                                                                                                                                                                                                                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 原source/domain/metadata | 合计canonical UTF-8 ≤1MiB、嵌套深度≤32、总JSON节点≤65536；包括全部opaque payload、metadata、引用、墓碑，不先解析大payload再算长度。T01在SQL长度/行预检后逐项取有界bytes                                                                                                                                            |
| records/RDF/支持         | definitions+facts≤4096；完整RDF distinct≤4096，全部支持条目≤8192、显式references≤4096；必须先收费全部支持而不是只看去重graph。完整state不可表示或超限则整体失败                                                                                                                                                    |
| 文本/term                | 每IRI、literal及派生identifier UTF-8≤16384B；整次term解析输入总bytes≤1MiB，最多12288次受控term解析。Entity文本仍须满足原16000字符上界，bytes/JSON转义另计；不扩大现有类型/词法                                                                                                                                     |
| edit/typed request       | 首切片恰1移除+1新增事实、0 entity change；typed plan完整canonical≤65536B、完整request≤131072B并满足原frame含1024B余量。原schema4096数组上界不等于本切片允许4096编辑                                                                                                                                                |
| 预览与结果               | 原完整Diff/undo-impact文档≤1MiB（更紧于原16MiB/512×32768）；单segment保持原32768B，原page≤min(实际maxPageBytes,实际maxFrameBytes,262144)，frame余量1024不扣掉。metadata/前后/支持显示收费完整编码，不截页代完整确认                                                                                                |
| 整次保留/工作            | T02所有同时保留source、投影、supports、before/after、plan、解码页和展示编码池合计≤8MiB；复制前按完整编码预扣，释放后方可回收。工作预算：逐source记录/term/support/比较计数，再保守收 sourceBytes×(1+records+allSupports)≤64MiB-work，最多4次完整RDF比较；到限整体拒绝。此为应用计费，不证明Python对象RSS或墙钟硬界 |
| T01实际库/Job/历史       | 沿同版ReadLimits：validation_rows≤16384、validation_bytes≤33554432、validation_work≤536870912等原政策（可收紧）；原Job limits/frame/page/游标TTL和槽上限继续。需要T01写前guard把本次新plan/blob/cursor/confirmation/Job/result/历史增长计入，所有同连接完整历史扫描均先预算，不能只限入帧                          |

T02私有纯适配器拒绝时零持久写。原T01 preview/分页/confirm可持久化其有界plan、snapshot、blob、cursor及确认记录，不能宣传“任何预览全库不变”；domain revision/definitions/facts/mapping/control在正式Job commit前不得变。异常回滚按对应事务断点证明：单次失败事务没有部分新artifact，先前成功preview artifact可保留且须有界清理/过期；旧历史和原receipt不得删除。完整返回publish失败按原对账规则处理。

跨整个请求的suppliers、原支持枚举、JSON编码/解析和图比较都要共享累计预算，不能每个helper各重置1MiB；任何适配外工作若不在所列上界中，先提交精确预算扩展请求，不默认无限。

## 8. root协调的供方请求与拟实施路径

| 请求                                 | 唯一owner与精确变更                                                                                                                                                      | 首切片所需交付/后置                                                                                                                                            |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1 当前完整domain+metadata投影       | T01；建议新增 `project/ontology_projection.py` 和 `test_project_ontology_projection.py`，复用其既有project_host/ReadLimits/Store验证；是否改已有project_host由root另批准 | 同连接原ID/全支持/引用/public-internal/retirement/metadata缺失与派生政策，完整预算和损坏拒绝。先冻结同版来源清单；T02不代写                                    |
| S2 T02输出的独立复验及原链组织       | T01；建议新增 `project/ontology_changesets.py`、`test_project_ontology_changesets.py`，仅包住原唯一domain_changesets/Job机制                                             | 受信当前投影→原计划复验→全after一致；确认不自动，复用原DTO/receipt。若需改domain_changesets/Job预算guard，逐路径经root批准并T01独占；不在T02目录造第二服务权威 |
| S3 完整Entity metadata与来源支持操作 | T01 canonical/schema、domain_changesets、Store及其专属新测试（具体delta由T01回报后root冻结）                                                                             | metadata唯一编码/迁移/引用/全量Diff/undo/包保留，mapped覆盖/墓碑/重跑、全支持选择。首切片不改这些，但缺少S1 metadata可信策略仍阻开工；不是永久不实现           |
| S4 正式页面/人类动作/当前许可        | T01 canonical/named engine；I06仅余下preload/env/App/style；T08真实草稿；root串行路由                                                                                    | 新named接口/实际host当前scope及App入口另申请，不把临时库机制升级生产权限，不直接复用通用invoke                                                                 |
| S5 Turtle/模板与可移植保留           | I05语义/Turtle、T05模板、T10包；T03锁/build仍唯一                                                                                                                        | 完整FR203/metadata包/blanknode模板及Q6同版类型供方后续，各自新候选与完整联验                                                                                   |

拟获批后另建 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-typed-changeset-integration`，分支 `feature/weekly-t02-typed-changeset-integration`，从再次核实的批准develop5f建立；本轮不创建。只逐ref/path/bytes/SHA采用清单中必要T02四模块与T01静态闭包/资源，保原候选；reference tests/docs不作为helper复制，不wholecommit，不借T01环境。若T01新supplier未包含在423b，须先取得其固定新ref/闭包并重新独审采用差异；不能先写假supplier。

T02唯一拟新代码路径 `packages/engine/src/ontolearn_engine/ontology/typed_changeset_adapter.py`，唯一新专属测试 `packages/engine/tests/test_ontology_typed_changeset_integration.py`，案例仅由该测试构造；不改旧model/service/source_projection/测试、canonical/Store/Job/桥/App/锁/构建。若必须修改原T02模型，先由root精确扩权、解除相应新树范围并生成新候选，不偷改冻结493。新适配器只做纯翻译/条件与预算校验，返回原changeSetPlan，不收路径/DB/写权限，不自动确认。

## 9. 获批后的真实临时JobStore3验收矩阵

以下全部是将来必跑，当前未运行。临时库在新测试专用目录，与用户库/他树环境隔离；以实际JobStore(target_format=3)和同版canonical载入。建立案例只用原批准Store/Job机制，输入数据独立给定；被测编辑计划必须来自T02真实生产调用，不能把手工typed plan或expected送入适配器。

| 场景           | 真正驱动与完整核验                                                                                                                                                                                                                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 正向整链       | 实际原事实含稳定ID；从T01真实当前投影→T02 change_preview→适配→原preview/读全Diff→显式fixture确认→原Job queued/running/commit→完整读回/undo。核全部RDF、全部metadata/缺失来源、原factID/全部支持、definition payload/control/vector、Job/result/operation历史 |
| 值修改身份     | 新O使content hash不同但原ID保持；人工fact owner等仍None；不新增新ID残留，不改变无关S/P或字段。另验证已有非content-hash原ID且符合typed形状仍保留                                                                                                              |
| 来源/内容漂移  | 原版本变更、同revision改domain/metadata/vector/control、原快照hash不匹配、错误public/internal、同IRI不同原record、篡改Preview/candidate、原source被替换，原preview与commit各边界均拒绝且不产生部分域写                                                       |
| 支持/不可表示  | mapped、override、墓碑、ontology重叠/重复triples、同RDF多支持、同slot多值、目标已存在、不可表示metadata、metadata-only、typed label/comment、BNode列表、未知payload缺证据全量拒绝；若它们是无关但完整可投影数据须保持，不能一概删掉                          |
| 项目/会话/交互 | 切项目、旧/late读页与预览、session变更、过期/伪造/跳页/重放cursor、未读全Diff或没有明确确认，不能得到有效确认/Job；fixture不当真人                                                                                                                           |
| 取消/失败      | 预览前取消不调用写；queued/running取消按原状态收尾。原preview/blob/confirm/claim/commit mid_data/receipt/result/terminal前后故障，逐事务dump+全域对照；已提交响应丢失仍只原receipt对账，不自动重放                                                           |
| undo/历史      | 后续不相交修改保留；同资源/引用/单值冲突显示真实完整impact；缺原marker/plan/context/confirmation/receipt/历史损坏拒绝且零修复；重开同临时库读回原Job/receipt，只证明内部同库                                                                                 |
| 预算/拒绝      | 每一bytes/records/supports/terms/plan/page/result/pool/work预算恰界与±1，Unicode/转义、跨segment多字节、同去重graph大量支持、opaque payload、深度/节点、多helper累计及库历史增长均有真实反例；超限不截断不部分发布                                           |

成功读回完整记录与指定正反例，而非数量即通过。正式产品/测试/采用变化后按AGENTS执行check及必要sources/构建，若依赖/打包实际变化再由T03协调；隔离原生/目标OS/App/真人另列，不在本机运行GUI/native/e2e/HMR或模型。不重测无变化旧S1。

## 10. 静态交付与下一批准点

当前可交付的是此完整映射、FR差距、S1–S5精确供方请求、拟路径/只读采用闭包、预算与真实验收规范。来源清单每项可从固定Git恢复；独立agent只读方案审查与意见处置保留在review目录，最终docs ref及逐项manifest由交付索引固定。

下一动作由root选择并协调：先冻结T01 S1/S2投影及复验合同（含metadata派生政策/缺失证明和所有增长预算）；供方固定后精确批准新树、逐路径采用与T02两个新writer，再实际运行本矩阵。S3–S5及完整FR后续不关闭。当前准备授权不等于上述实现批准，不向其他聊天擅发任务、不push/PR/merge，也不改变原Goal工具状态。
