# 包格式、业务集合与版本闭包

本文件的角色划分和字段均为P提案。需求必需集合来自固定PRD，具体JSON/枚举/上限须格式owner与各业务owner共同冻结；不改变66cc私有检查器。

## 1. 包类型和最低集合

完整包建议以如下逻辑集合覆盖FR1000；逻辑集合不是“一角色只能一个ZIP成员”，也不能用空对象替代owner未交的数据。

| P角色                | full必需的业务内容                                                                                                                     | 恢复证明与来源                                                                         |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| project-metadata     | 名称、目标/能力问题、合法项目配置、恢复所需业务草稿/应用选择；无profile/窗口/授权状态                                                  | T01应用状态快照及字段白名单；不存在的类别须证明实际为空                                |
| definitions          | 本体、映射及身份规则、查询/范围、约束、规则、行为、场景、学习任务/完成条件/课程与清单                                                  | 各定义类型schema/版本/引用，包含全部当前保留定义，不能遗漏非本体模块                   |
| assertions           | 完整当前已提交断言集合，区分人工与映射产生；保留规范RDF词法和记录身份                                                                  | T01固定snapshot；不把推导混为断言，不按编辑后值重算初始factId                          |
| provenance-ownership | 来源对象元数据、source-row稳定身份、mapping/slot/owner、managed值、人工修改/删除墓碑、retirement及来源定位                             | 足以恢复FR304冲突；无raw时仍保留必要身份/元数据，不能附带整行原文充当metadata          |
| state-versions       | project/domain/application/learning版本、mapping generatedVersion/stale依据、当前业务指针与载荷可用性、最低reader/writer/canonical版本 | 同一次一致读；状态与来源/依赖可解析，不让模型配置冒充领域版本                          |
| recovery-closure     | 恢复当前状态、保留的合法单次撤销/快照恢复所需typed控制证据、before/after与业务快照的最小闭包                                           | T01 transfer coverage与typed引用证明，不复制源完整checkpoint或全部祖先链               |
| learning-state       | 当前任务/attempt状态及恢复其真实检查/提示/辅助分类所需最小业务证据；具体保留范围待T09/T08/T01批准                                      | 必须证明来源与覆盖；无学习状态的真实项目可有经证明的空集合，不能以供方未实现假造空状态 |

完整包的空项目不是模板的同义词：只有owner证明当前assertions、owner等集合本来为空、仍交齐必要集合/结构/coverage且支持恢复，才可按正式schema作为空的完整状态；“缺集合/缺证据”不能用零条目掩盖。

**模板的PRD确定底线**是版本、清单、可移植引用、真实范围，且不得承诺恢复当前状态。模板的最低定义集合和是否允许任何实例内容尚未穷尽于PRD：F01给出严格定义模板与受限实例模板两个方案。本提案建议模板最少包含project-metadata的非实例描述、被选definitions及所需版本/定义引用闭包，恢复当前能力恒不承诺；它仍需正式确认，不把损坏full自动视为合格template。选择full却缺必需集合时返回阻断，用户重新明确选择模板后才能按获批模板政策重新预演。

## 2. 四个可选集合

| 选项          | 被选时的实际集合                                                                     | 未选时必须缺席                                                                                    |
| ------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| rawSources    | 用户明确范围的真实已封存源文件字节、对象ID、预期长度/hash及可移植格式元数据          | 源文件正文、未选工作表/对象的原始字节；不得从目录、source-row或undo隐藏携带                       |
| derived       | 明确范围的当前推导及其输入/依据/状态；不替代assertions                               | 推导载荷及以断言包装的推导副本；结果描述/依赖可保留为恢复所需元数据但须标无载荷                   |
| history       | 已选择运行的真实固定输入/配置、行为规则版本、逐轮状态、结果及业务历史；选择粒度见F06 | 未选运行正文、输入、逐轮/日志；不能用最新项目状态替换对应旧输入                                   |
| agentSessions | 已选择业务会话文本及最小来源，始终按数据处理                                         | 未选会话正文/摘要/工具全文；当前learning辅助证明只能取已批准最小业务事件，不能换名为audit夹带会话 |

16组合见option-matrix.json。四个false仍可为full；每项true也不自动承诺重跑/重放。每个选项的子范围须进入预览和scope digest，默认值由产品决定；本提案不假定历史全选或导出全部会话。

## 3. manifest与成员结构建议

建议manifest为strict UTF-8 JSON，角色记录采用受限JSONL或分段strict JSON（F03待格式owner选择），raw源保持原字节。ZIP只是传输封装，不解包执行。建议manifest概念字段：

| 字段                  | 约束                                                                                                                                      |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| formatIdentity        | 正式formatId/major/minor/schemaDigest/producerVersion；本提案不指定发布版本号                                                             |
| kind / selection      | 明确full或template，四选项及各selectedObjectIds/rangeDigest；来自确认范围，不信包内授权声明                                               |
| versions              | canonical/业务payload各schema版本、源snapshot版本、最低reader/writer与执行版本引用；不得用DB user_version当包版本                         |
| roleCatalog           | 每逻辑角色的schemaRef、成员有序集合、记录数/集合digest、必需/可选分类与coverageRef                                                        |
| members               | 唯一memberId、生成式相对path、role、ordinal、mediaType、压缩/未压缩长度、原字节SHA256、recordRange/recordCount、sourceObjectRef（如适用） |
| references / coverage | typed引用索引和最小闭包证明；不会授予本地路径/网络/私有根读取能力                                                                         |
| requirements          | 必需和可重关联依赖的种类/版本/hash/状态，不能携带endpoint凭据主体或发送grant                                                              |
| capabilityClaims      | 可选的源声明，只作未受信提示；导入侧按实际材料、版本支持和验证逐项重算，不能直接采用true                                                  |

manifest不存自己的自引用hash；包整体hash在main受信句柄外部计算，用于预演/确认绑定。成员SHA只证明对应字节一致，不能证明作者、所有权、真实性或学习掌握。

成员path由编码器生成如`members/assertions/000000.jsonl`，不采用来源文件原始路径，物理basename只作经过许可的显示元数据。严格拒绝绝对路径、盘符、NUL、重复/别名冲突、symlink/特殊文件、未列成员与未解析引用；不将成员路径拼成renderer可读FS路径。ZIP extra/目录项兼容策略见F04，不沿用“所有标准zip必不兼容”的全称；每个获批producer/参数组合以具体fixture验收。

## 4. 每角色多成员与预算

建议解除正式格式中的“一角色单成员”假设，以`(role, ordinal, memberId)`唯一和有序catalog约束。按稳定typed recordId排序分片；同一逻辑记录不得跨片拆成无法独立校验的半对象。raw对象可一对象一成员；超单对象限制时采用显式chunk index/完整对象digest或拒绝，二者由F03决定，不能悄悄截断。跨成员引用必须指向typed对象ID，不能依赖ZIP遍历顺序。

每角色至少约束：最大成员数、单成员字节、逻辑记录数、单记录/字符串/嵌套深度、角色总未压缩字节；全包约束manifest字节、成员总数、压缩输入总字节、解压总字节、解析/IO累计预算和取消检查点。先查受信文件长度/EOCD/目录数量等有界元数据，再分块解压并累计实际输出，达到预算在分配/读取超限内容前拒绝，不能信声明长度。declared count与实际目录数仍需一致；CRC、SHA、完整流结束、尾随隐藏字节及布局政策继续验证。

预算必须绑定获批`resourcePolicyRef`，由运行端校验该policy与平台实际支持，不接受包内自报更高限额。所有上限必须在发布schema中落成精确正整数及边界用例；任一未决则不能宣称正式格式可用。当前私有40MiB输入/32MiB展开/8MiB成员/64KiB manifest/256条目只是已审草案防线，**不是本提案默认产品容量**。当前合法语义最多9条目与前置256恶意输入防线分开；正式多成员方案须重新量测，不能删防线或把T03分块建议直接定为容量承诺。具体容量与参考设备属于Q5/F05。

## 5. 来源/所有权的恢复不变量

每条映射管理记录需保留其稳定factId、当前RDF值、mappingId/version、sourceObjectRef、sourceRowId、slot、managedValue及retired/tombstone状态。人工修改保留record身份与旧managed基线，不能在迁移中用当前值重建“干净”受管记录。人工墓碑不能复活；不同来源争同一事实不做去重接管；普通业务字符串中的数字/ID不作递归替换。

源文件未选仍需保留可移植source描述和稳定行身份以定位及重关联；不保存源机器绝对路径作为读取授权，不在metadata中附带未选原始行正文。重关联要由T03按正式source schema验证预期字节、格式/工作表、身份规则及映射版本；同名不同内容不得静默匹配。用户明确选择新源属于新的预览/确认映射运行，不能伪称原始重跑已经验证。

## 6. 版本化checkpoint和最小typed闭包

导出根不是DB页，也不是源库checkpoint全链。T01一致读返回固定domain snapshot、application/draft/learning CAS、checkpoint/operationSequence及各owner schema版本；T10只消费经T01批准的投影。closure算法建议：

1. 先由T01在同一operationSequence枚举完整必需源集合、version/retirement ledger及当前承诺保留的撤销/恢复控制根，给出各族源count/digest、覆盖范围与合法排除理由。当前dependencyVector过滤掉missing/retired，不能替代这份完整枚举；只证明已列出的边都有目标也不能证明未漏根。F07保留政策先确定所需全集，随后才能裁剪payload闭包，不能反向缩短现有承诺。普通运行历史/会话正文不自动成为根。
2. 按批准的类型表跟踪definition/assertion/provenance/ownership/mapping-state/version-ledger、before/after snapshot、业务控制证据及retirement/tombstone；对每个引用核schema、所属项目、长度/digest和版本。
3. 对含私有或未选部分的源快照，只有owner已定义的typed投影可生成新的portable对象并重算digest/引用；不得按字段名删除后沿用源hash，不通用遍历JSON猜引用。
4. 递归至固定点并验证每条边有目标；允许的业务引用环以visited集合和有界图校验处理，commit ancestry不得伪造循环或忽略顺序。
5. 生成coverage：各必需集合的源count/digest、投影count/digest、typed边集合、根集合、遗漏/冲突清单、source→portable引用映射。证明对象本身按I06白名单审计，不包含私有原文。
6. 必要闭包若只能包含未选history/session/derived/raw正文或I06私有材料，明确`SCOPE_CLOSURE_CONFLICT`提案错误并阻断full。可提示显式调整合法选项、由owner提供等价可移植最小业务证据，或由用户重新选择获批模板范围；不能暗带、丢边或自动降级。

单次ChangeSet撤销与恢复整个快照分别保留控制信息、作用范围和冲突规则。导入后需能撤销仍保留的原变更，并在后续编辑冲突时暂停；不能以只保genesis或只允许查看旧Diff替代G.6。准确保留窗口/closure保留长度由F07与T01决定；如当前用户可见撤销承诺无法保持，full验收阻断，不静默缩短。

## 7. 身份、兼容和迁移

建议对象引用形如`{type,id,versionOrDigest}`，类型表由canonical owner冻结。定义/事实/source-row/owner等项目作用域身份是否可保留，及job/run/attempt/operation的全局身份如何重映射，按批准scope表逐类型处理；来源业务历史身份可保留为origin证据，不恢复本地运行权。sourceProjectId不是新目标projectId。含项目身份的快照/结果/控制digest重算，保存original→portable→local映射和原digest证据；不得让同一个旧hash指向重写后的对象。

包格式、payload schema、canonical、DB/checkpoint/application版本、执行语义、engine及dependency lock分层。reader明确识别schemaDigest与兼容矩阵；未知major/角色/必需字段或无法安全保留的构造拒绝，不以“忽略未知”导入。minor是否允许可选扩展由F02明确，不预设兼容。迁移只能由owner提供获批的纯投影迁移链，在不可变源包上预演生成新plan，列源/目标版本和语义差异，用户确认后才提交；原包不改，不能把SQLite spike迁移函数直接作为项目包迁移。

支持判断不是靠包内minReader字符串；本机实际能力注册与批准版本表必须相容。缓存升级兼容与staleReason按唯一invalidation规则处理，不额外发明“导入”过期码；缺载荷/不支持实现是独立availability/compatibility状态。
