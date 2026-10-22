# M02–M05：固定源码中的既有接口事实

本文只记录 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64` 的八个获准文件所能证明的接口事实。源码清单和 SHA 见 `source-inputs.json`；完整 AST 定义索引见 reviews 同名目录 `source-index.json`。本分支从已核本地 develop `1b6df7a220fc9a67d7046133a340085f03f0a96c` 建立，但接口事实的输入始终是固定2cf，不是本分支的产品代码。

只做 Git 字节身份、AST 和指定函数文本读取，没有 import/exec/runpy、运行 probe/model/产品、读取输入资产/expected/actual、安装或 native/数据库/构建。未追读 imports。这里的“返回/校验”均指源码定义，未经本窗运行验证。本文不是新规范、权限或 codec 采用记录；独立静态审和总控固定接收前，不交 D2 作为已接收材料。

本文各节的“本八文件/未获准/尚未定位”是首窗口边界，后收到的11个helper和3个窄片段按 helper-interface-facts.md、final-fragment-inputs.json 和 current-disposition.json 更新；不得把历史缺件陈述当现时未收材料。

## M02：旧 scope metadata 与返回布局

`semantic_scopes.py:73` 的 `_source` 返回完整四字段字典，插入顺序是：

1. `executionSemanticsVersion`：取 `semantic.SEMANTICS_VERSION`；该固定文件第27行为 `i05-finite-6`。
2. `assertedInputSha256`：原 asserted facts 的有序 triple N3 集合摘要。
3. `ontologyInputSha256`：原 ontology 的有序 triple N3 集合摘要。
4. `selectedRulesSha256`：canonical legacy Rule 的有序定义摘要。

这与新 display `i05-scope-content-source/1` 的字段和摘要域不同，不能替换。此处的值是内存 dict，并没有在 `_source` 中发行独立 metadata byte wire。

`ValidationScope`（同文件227–231）是 frozen dataclass，字段顺序为 `facts:Graph / ontology:Graph / provenance:dict / reasoning_result:dict|None`；冻结的是记录字段，不证明其 Graph/dict 内容不可变或获得权限。`project_validation_scope`（234–298）返回该记录，完整 provenance 的13个键按构造顺序为：`scope`、上述四个 source 键、`reasoningSource`、`selectedRuleIds`、`warnings`、`selectedFacts`、`derivedAxioms`、`ontologyView`、`factViewSha256`、`ontologyViewSha256`。

asserted 分支的 `reasoningSource=None`，warnings 和 selectedRuleIds 为空；derived 分支的 `reasoningSource=dict(source)` 是新字典副本。`reasoning_result` 直接采用入参引用。selectedFacts 的每项是 `{triple,sources}`；asserted source 只有 `{kind:"asserted"}`，RDFS source 是 `{kind:"rdfs",basis}`，rule source 是 `{kind:"rule",rule,inputs,basis}`。不能把新数学投影里的 `ruleId` 或 asserted basis 倒填到这个旧布局。

legacy `semantic._legacy_reason`（551–603）返回五键，实际构造顺序为 `rdfs,warnings,rules,evidence,rdfsEvidence`。rdfs/rules 是有序 triple N3 tuple 列表；evidence 每项 `{rule,result,inputs,basis}`，rdfsEvidence 每项 `{result,basis}`。scope 的 `_selected_output`（88–223）核这五个键、列表和证明内部一致性，未承诺其来源真实性。

已有 profile 输入 codec 另属 `semantic_profile_input._project/_encode`（308–436），不能当成 legacy reasoningSource 的原 codec。它的 `_RECORDS`（22–41）明确编码 SourceRecord 的 `reference,digest,revision,text`，TermInput 的 `kind,lexical_form,datatype_iri,language_raw,source`，以及 Variable/Triple/Comparison/RuleSpec 的字段目录。`_project` 对记录用 `recordType` 加显式字段；只接受对应 exact class 和字段类型，再交 `_encode`。这些是已有输入编码规则，不发行新 source 权限。外部 class 本身的完整定义未获本八文件窗口，不能因此声称所有 canonical adapters 已完整核定。

## M03：已能定位的摘要 preimage

原字节 SHA 与 JSON 内容摘要分开。八文件中的精确公式、字段顺序要求和边界列在 `digest-recipes.json`。主要来源如下：

- scope `_digest`（42–49）对 `json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))` 的 UTF-8 bytes 做 SHA-256。这里没有额外 domain tag、LF 或 Unicode normalization；源码未显式传 `allow_nan=False`，不能把其他 codec 的选项抄进来。实际 source 构造域是 N3 字符串/数组/字典。
- scope `_source` 的 graph preimage 为 `sorted(_key(t) for t in graph)`，`semantic._key`（247–248）逐 term 调 `n3()`；规则先 `_canonical_rule`，按 id 排序，再取完整 `{id,when,then}`。`_canonical_rule`（316–323）依赖未在窗口内的 `semantic_turtle.canonical_string`；第三方 `n3()` 实现也没有在本窗重验。公式已定位，不等于其全部外部编码依赖已独立接受。
- `semantic_execution._json/_digest`（59–70）用相同紧凑/排序 JSON，且显式 `allow_nan=False`。`execute_request`（331–501）中的 constraintsHash 使用完整 constraint definition；其 payload 返回 `{payload,rows}`。`_rows`（299–328）包含实际随机 rowId，不能由内容摘要推造其原值。
- profile `_execute_profile`（626–758）分别生成 input/source/definitions preimage，payload、rows 的原字节摘要分别计算。text input 的 inputDigest 是原 UTF-8 text 的 SHA；structured input 是 `_ProfileProjection` 后的 `_profile_json_bytes`。source 和 definitions 是各自完整投影的原字节。payload 格式 /2 或 /3，七键 `format,implementation,reasoning,inputDigest,inputDigestDomain,sourceDigest,definitionsDigest`；wire 四键 `payload,rows,jsonPayloadDigest,rowsDigest`。
- `_profile_json_bytes`（593–606）是严格 UTF-8 的紧凑排序 JSON 流，显式 `allow_nan=False`。rows 按 payload 解码字符串的8192字符切片，每行一列，保持末片，之后独立编码并做 SHA；不是按 UTF-8 byte 边界重切。
- material `_encode`（397–436）编码 `_project` 结果；`_definitions`（466–510）分别保原规则投影和 `{version,rules,disabledRuleIds}` 的完整定义材料。`_prepare_profile_material`（686–783）把 input/source/definition 原字节保存在返回记录中，不应从新 display source 重新生成冒充这些原件。
- probe `_bytes_value`（709–714）只对既有完整 bytes 产生 base64/bytes/SHA包装。`_capture_expectation`（1227–1240）对本次 produced 的 payload/rows/catalog 原 bytes 分别 SHA，并取 material input/source preimage；这是源码中的捕获路径，不证明当前运行已真实发行 expectation/allocation。

尚未完整定位 production catalog codec、restore/expectation 的完整原 codec、所有副边字段、implementation 精确布局及外部 canonical 字段类型，详见缺件表。没有根据 actual 输出推导 expected，也未重算费用。

## M04：同次传值与权限验证的边界

`prepare_validation_scope`（301–326）在本地构造 source，derived 模式调用 reason，再将原 result/source 传给 project。project 会重新算 `_source` 并比较 `reasoning_source != source`；它还核 selected output 的内部一致性。该文件首段和 project docstring 明确指出：这些指纹不认证 producer、历史 selected、授权、版本或存储绑定，相关职责在 I03/I04。

probe `_scope_observation`（1162–1224）确实把 `prepared.reasoning_result` 和 `prepared.provenance["reasoningSource"]` 直接作为 project 入参，并保各 stage facts/ontology/provenance/reasoningResult。这是静态调用与保留事实，不能据此签发 live issuer/handle、同 issue 证明或真实 call count。CollectionBoundary（151–184）保留已返回 value 的真实引用至输出，但不发行 canonical authority。

本八文件没有给出可供引用的、已批准的 legacy same-issue issuer/live-handle verifier。不能把 `_selected_output`、字典相等、源码里的直接传值或已有 call hook 当作该 verifier；也不能据本窗口断言其他未读文件中绝无对应实现。M04 的来源/权限/运行 guard 保持 pending，需原责任方给精确现有接口，或另行批准新设计与实现。

## M05：已有 API、序列化与错误出口

`api-layouts.json` 记录已读源码中的返回目录、字段类型表达式和精确函数位置，不把未读 class 的注解扩成完整 schema。主要已定位：

- parse 原返回 Graph；probe `_graph_value` 用 `{triples,tripleCount}` 观察，triples 是有序 N3 triples。该导出不是新 typed RDF/BNode-domain codec。
- `semantic.query`（160–237）：ASK `{type,value}`；SELECT `{type,variables,rows}`，全部 nullable cells 保留，cell 为 N3 字符串或 None。
- legacy reason、ValidationScope 和 provenance 完整字段如 M02。
- `_check_shapes`（1566–1614）：`{conforms,violations}`；每项恰 `focus,path,constraint,sourceShape,value,severity`，value 可 None；没有返回原 Validator report Graph。
- `execute_profile/execute_profile_records` 返回上述 profile wire；`_ProfileProjection.value`（519–590）对17个显式 canonical class 作字段导出，保 int 的 integerHex、bytes 的 hex 包装；tuple/list 都投影为数组。这不是新 return-tree/1 的 tuple/list 保真定义。
- probe `_typed_value`（722–765）使用另一包装：recordType 为完整模块名，fields 为 dataclass 字段；bytes 是 base64、int 是 integerHex、tuple/list 同为数组。它与 `_ProfileProjection` 不能混称一个 codec，也不能用来证明旧 tuple/list 身份已无损保留。它的完整 approved class 集依赖已验证 modules 的实际 dataclass 定义，本窗未穷举其他文件中的全部类。
- probe `_production_observation`（1260–1343）逐项输出 wire、五种原bytes包装、actualDefinitions/actualCatalog/allocation/expectedCapture/restored/roots及capture/direct receipts；mutation分支另存坏副本/原expectation与未reissue标记。它访问的 produced/restored class 完整定义位于未获准 helper，故当前不能宣布 full417 的全部返回class/sidecar目录已审完。
- 公共 adapter `_emit`（308–322）只返回 `code,messageKey,params,retryable`；adapt（324–372）按 exact Producer/ErrorContext/Stage/Origin 和有限 reason 决定出口，不复制任意异常文本。error catalog/schema仍是 caller 提供并校验的输入，未在本窗读取 registry 或签来源权威。
- `ProfileExecutionFault` 保 `error,diagnostic`；`_profile_diagnostic`（609–623）四字段 `reason,classification,ruleId,location`，location 非null时保 `section,index,side,span`。probe `_known_failure`（1122–1159）还有 isinstance/getattr/hasattr 的现有读取分支；这不等于新 carrier 要求的全部 exact-class safe adapter 已获批准。未读 Material/Restore/Direct/Offline error 定义继续列缺，不能裁掉未知字段去符合旧有限 projection。

M05 当前是有边界的接口库存，不是 full417 完整 adapter 接收、实际采集或 oracle 通过。source/ref、code/codec/layout、原件完整保留、同次权限和业务比较仍是不同验收项。

## 后继交接

旧 D2 及新 carrier、费用 R4、retained R2 输入不改。本材料独立静态审后，供总控按精确纯文档路径接收；D2不得因文档含 source pin 而跟到未批准源码。额外 helper 仅读申请范围、先经总控绑定；不追 import、读取 actual 或执行探针填空。所有未有 verifier、codec/布局或外部权威继续明确 pending。
