# T01 固定事实与历史设计接收

根供应`T10-upstream-T01-fixed-design-inputs-20261022.json`。11项许可输入均按固定ref:path取Git原始字节，长度/SHA全部相符；8项源码只作事实出处，未取字节、未直接读取或采用实现。6份facts固定5abfc699，4历史设计固定f51a9e，现有errors目录固定423b7e。精确身份和授权层级见source-provenance.json。

只读agent`/root/t10_round2_receipt_review`全文读6facts、历史foundation/application CAS/ChangeSet计划及errors JSON；acceptance map只读第1–25、75–97及P04/P07/S01–S06相关段。下述实现原语全部归因于根允许的固定facts，不是本轮重新审源码、运行或正式采用。没有接触T01本轮外审意见。

## 1. 现有原语和不能外推的内容

| 固定facts所述对象      | 可依赖的设计事实                                                                                                                                                                                               | 不能外推                                                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Store domain state     | mappingState、definitions(layer/id/payload字符串)、facts(id/subject/predicate/object/owner/source_row/managed_value)                                                                                           | asserted事实在facts，无独立assertions槽；opaque JSON/结构校验不代表全部family已typed                                |
| snapshot/vector        | project/revision/dependencyVector/state；vector过滤缺席与retired成员                                                                                                                                           | 当前vector不是完整版本/retirement账；snapshot()还会持久化，不能直接当纯读export调用                                 |
| 删除                   | managed删除保原ID/owner/source_row/managed_value，object=NULL；manual删行                                                                                                                                      | state/snapshot没有完整retirements字段，手工删除的历史与控制依据需另外真实闭包                                       |
| application checkpoint | project身份、domainSnapshotRef/domainRevision/operationSequence、coverage/historyCoverage、application；metadata含name/templateRef/archived/mode/origin，draft含generation/present/bound_revision/payload/hash | domain/history是引用，不是完整包；learning/audit只校JSON dict，不是真实学习schema/证据；部分appJSON不代表全应用恢复 |
| 一致读                 | project_checkpoint读真实CP并核history sequence/receipt及前后domain/app；workspace含metadata、CP/domain引用与一个editor草稿                                                                                     | workspace不是全项目投影，源CP链通过不能证明裁剪后的可移植closure                                                    |
| preview/CAS            | 事务回滚预演、base revision、confirmed digest、before/after/control核验，metadata/draft CAS与combined提交原语                                                                                                  | preview_restore仅本项目已有可信snapshot/历史的域补偿，不消费外来包；逐个draft.restore不能拼完整原子导入             |
| typed ChangeSet        | ontology triples/singleValuedPredicates/references子集、manual fact/edit/remove，触及before/after须可由该子集完整表达                                                                                          | 不是全部定义family恢复器，更非跨项目导入器                                                                          |
| receipt/commit         | 唯一Store外层事务、savepoint、application同事务claim/CP/receipt；reconcile核marker/job/fingerprint/before-after/control                                                                                        | 混合project_receipt链/legacy-not-recorded不证明完整import幂等或全局claim，不能重放授权                              |
| 项目身份               | public↔internal UUID绑定                                                                                                                                                                                       | 尚无entity/definition/fact/source-row/owner/editor/attempt的typed跨项目映射与引用重写                               |

历史foundation有完整CP/coverage/CAS及辅助audit方向和最小receipt形状；application CAS明确不受理learning、辅助audit与全application restore，claim-context、resolved-plan、combined-domain三个hash不能互换；ChangeSet计划明确排除完整项目恢复。acceptance map仍保复制/导出/全恢复/跨设备/模板和缺源标签/真实学习缺口。不能把这些历史方向升级为现成供方。

## 2. 本提案请求的具体新增合同

1. **真正一致typed导出**：固定project、operationSequence、domain/CP引用及所有被纳入对象CAS；所有业务family的strict codec/字段白名单与coverage。未识别opaque载荷不能原样穿透后宣称完整。
2. **版本/retirement/undo闭包**：除当前vector外给必要版本载荷、retirement控制、managed墓碑、manual删除历史、before/after/恢复控制与可验证typed边；缺账明确阻断相应资格。
3. **typed ID作用域表**：逐类型保留/新分配规则、冲突处理、引用重写和digest重算，包括owner/source-row/editor/attempt；业务旧Job/operation历史不能变活授权。
4. **外来ImportPlan与确认**：包/manifest/集合digest、格式与来源版本、新目标、完整ID映射/闭包/缺依赖、相关CAS/上下文代次、预览与独立人确认、提交前复验和失败零发布。
5. **完整原子import receipt**：全domain/application/learning/必要历史同一次外层事务发布，新project和唯一receipt；明确operation claim/精确指纹/丢响应只读对账与原receipt重取，不直接套旧域receipt。
6. **学习保真**：真实attempt/检查/提示/辅助typed投影；恢复learningCurrent不得截断辅助账、洗白已有完整代做；JSON dict或CP coverage不证明真实来源。

相应具体形状、故障与验收在format/import/learning文档给出；是待owner批准的类别和协议设计，不声称已存在这些方法。

## 3. 错误合同复用范围

许可目录errors.json为schemaVersion=2、26固定码、maxEncodedBytes=2048及strict params。版本冲突、身份冲突、存储忙/失败、请求超时可作为语义映射起点；TIMEOUT.phase=request允许已经提交，不能以超时推未提交。项目包的格式/closure/typed重映射/import归因和receipt没有完整合同；RESOURCE_LIMIT.resource未列archive/import，NOT_FOUND.resource也未列包/导入。协议版本不兼容或DB启动格式错误不能冒充包版本错误。

本提案的PLAN_INVALIDATED等只是建议错误类别，不添加现有26码，不塞任意reason/路径/原始异常。需canonical owner逐项批准复用/新增码、messageKey和精确params/字节预算，双端共同正反例；未批准前不注册协议或写共享errors.json。

## 4. 必须拒绝的误用

- 打包opaque state/domainSnapshotRef或当前vector，hash通过但目标缺载荷/retirement仍称完整。
- 只改project UUID或递归替换全部字符串，导致owner/source-row/attempt串项目或正文被改。
- 本项目域restore+多个app CAS拼接，途中失败后称完整原子恢复。
- 旧learningCurrent覆盖后续辅助记录，把完整代做洗成独立。
- 提交后timeout另造operation重导；或先验新CAS/旧sourceproof才查receipt，使已提交精确重试被误判冲突。
- 带CP或raw hash便标可重跑/重放，忽略真实source/options、行为/规则与执行支持。

上述反例已落实到验收计划。facts原raw尾导航旧名偏差不修原件，按root-summary真实C1 identity文件定位；不因为导航误差读取其它文件或把它误记产品失败。
