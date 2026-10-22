# 补充窗口：指定 helper 的接口声明

本件补充 `interface-facts.md` 的首八文件库存，不覆盖其历史读取范围。新增绑定允许11个 fixed2cf helper 的指定接口/类型/返回及序列化形状，以及 resources.semantic_identity 的646B独立片段。实际清单/字节身份见 `additional-source-inputs.json`；声明索引见 reviews 的 `additional-source-index.json`。最末窄窗口只增补 IMPLEMENTATION 一项187B赋值声明与 RootRef 五字段；未读取 resources.py 其他正文/全局，未分析 ledger 算术、费率或物理预算，没有执行任何产品。

## 类型与原字段

指定 class 的源字段、注解、默认表达式和行号逐项保在声明索引。默认表达式是源码声明，不证明当前实例有效、限额已获准或资源已付。

- SourceRecord（rule_profile.py67–71）：reference/digest/revision/text，均注解 `str|None`。TermInput（75–80）：kind/lexical_form/datatype_iri/language_raw/source。InputLocation（19–23）：section/index/side/span，分别为可空str/int/str/二int tuple。
- Variable、Triple、Comparison、RuleSpec、Catalog、BindingMatch、ComparisonEvidence、HeadEvidence、PreparedFiring、PreparedFiringBatch 的全部本地字段在 rule_firing.py 的指定声明中。Catalog三项为 classes/object_properties/data_properties 的有序str tuple，不能改成同名集合再推定原bytes相同。
- Number（rule_numbers.py14–17）为 numerator/denominator/negative_zero；Calendar（rule_calendar.py28–32）为 day/second/explicit_offset/is_datetime，second注解Number。ProfileValue（rule_terms.py47–51）为 term/domain/value/language，但 value 的原注解仍是 object，不能自行把它扩成已接受的封闭union。
- ProfileFailure声明了 reason/location/classification 三个property接口，其构造存储是 `_safe`；索引保构造字段名和接口，不执行property。RestoreFailure构造字段为 reason/classification/stage/slot/domain；DirectStepsFailure为 reason/classification/stage/domain。SemanticError在所给固定模块声明code；没有找到同模块顶层class/function声明名OfflineAccessDenied。该有限定位不证明其他未读模块或alias均不存在，也不能把新数学投影的类型标签当旧实际异常class。

## 完整返回记录与继承

`additional-return-layouts.json` 保生产/恢复API返回与receipt声明。fields仅指本地注解；`staticallyExpandedInheritedFields`另按已绑定本地继承关系列全部字段，不调用产品的dataclasses.fields或实例。

- ProfileComputation（production.py34–48）有14字段：material/native_result/original_allocation/actual_definitions/actual_catalog/payload_json/rows_json/source_encoded/definitions_encoded/catalog_json/wire/capture_receipt/version/retention_owner。
- ProfileExplanationComputation（52–54）继承上述字段，重写version并增加direct_receipt。因此完整字段为15个；不是子类本地两个声明。原wire、native_result、material和全部sidecars都须保留，不能只保probe终态目前选择的子集。
- RestoreExpectation（restore.py111–124）13字段；ExplanationRestoreExpectation（128–143）14字段。input/source preimages、各digest、implementation、schema/budget/cache及解释额外direct版本均存在，不得删尾项。
- ChildAllocation三字段、OriginalAllocation四字段、RestoredChild八字段、RestoredBatchSet十二字段均有精确源声明。字段本身不授原allocation/issuer；字段注解中的tuple/object也不自动成为完整有限codec。
- ReadonlyObject保entries；ReadonlySequence保native_kind与items。RestoredProfileProjection与RestoredExplanationProjection各payload/version；RestoredProfileResult有batches/projection/rows_json/retention/version；RestoredExplanationResult另有direct_receipt共六字段。原ReadonlySequence的native_kind不能在新适配时丢弃。
- DirectStepsReceipt（directsteps.py70–80）11字段：usage/retained/peaks/caps/events/candidates/steps/key_bytes/carrier_bytes/version/retention_owner。本窗只核字段声明，没有重算其账本或验证真实支付/来源。

这些声明使字段目录更具体，但没有把native_result:dict、ProfileValue.value:object、若干未细化tuple/object变成已接收的完整schema，也不证明所有417个API的全路径运行。

## codec及摘要补充

semantic_turtle.canonical_string（20–28）只把无language且datatype为XSD.string的Literal改为 `Literal(str(term),normalize=False)`；其他term原样返回。注释明确不改numeric/date spelling或language-tagged literal，不改RDFLib全局。此事实补充首八文件里legacy规则source preimage的这一个已知helper依赖，不能扩成其他词法规范化。

parse_graph返回Graph；parse_profile_graph/profile_graph_from_records的返回形状是Graph与 `_issue_context(...)` 结果的二元tuple；bind_profile_disabled_rules返回重新取得的context。这里只记录API返回形状和字面helper指针，没有追读 `_issue_context`，更没有把其私有parser context当legacy selected/issuer/verifier权威。

production.py391的catalog_json为 `_profile_json_bytes(_ProfileProjection().value(capture.actual_catalog))`。因此它与首八文件已读的profile source/definitions字节一样使用既有ProfileProjection及严格紧凑排序JSON；catalog原摘要是该完整bytes的SHA，不改为新relation digest。Catalog具体字段已从指定声明给出；原fields/recordType包装必须按该codec保全。

resources.semantic_identity的批准片段对应原Git35–48行，只说明返回 `**IMPLEMENTATION` 并按profile/explanation选择i05-finite-6/7/8。两个选择参数必须exact bool且explanation不能脱离profile。片段明确这不是公共能力注册或producer/snapshot/saved-result认证。随后精确批准的187B片段（原28–32行）只含 IMPLEMENTATION 三键赋值：executionSemanticsVersion 的字面值 i04-infrastructure-v1、engineVersion 的字面值 0.1.0、dependencyLockHash 的源码表达式 hashlib.sha256(LOCK_FILE.read_bytes()).hexdigest()。semantic_identity 会覆盖首键为所选finite版本。没有求值表达式、追读LOCK_FILE或其他resources全局；因此只核声明布局，不声明实际锁路径、当前锁哈希或运行身份。最终两片段身份见 final-fragment-inputs.json。

## 当前仍需材料

当前结论以 `current-disposition.json` 为准；首八文件的 `missing-definitions.json` 是当时范围的请求快照。新增11接口已按绑定读取，resources只读片段，不能把旧请求表当现时“全部未收到”。最后窄窗口已收到并只读RootRef返回声明（原1120–1126含dataclass装饰器，五字段kind/reference/ordinal/firing_index/head_index，后四可空）及IMPLEMENTATION纯布局。RootRef中kind仍只注解str，不自行补enum。尚需ProfileValue.value等未封闭类型的既有纯接口，以及真实same-issue verifier/授权的独立责任材料；不猜、不执行actual、不据actual反推expected。
