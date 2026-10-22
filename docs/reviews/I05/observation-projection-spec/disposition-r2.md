# R1 发现的 R2 作者处置

R1 结论 **Fail** 保留。R1 报告为 37247B / SHA256 `328944e737298722c72dae6bd6fc49d75832c8f2ce151b2772bb11f6d8e050d8`。修订起点为实际 `57c67631fab6a36f47963aca95b4036064e10777`，亲代 `6b665455a4cb88a9744c1b8d67573c5adf0c95f6`；原设计 candidate `dd3e659e9214481700275afb3f3188891e42359d` 及原 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 均不重写。作者已全文读取 R1 报告、proof、root receipt，并核完整 ref/亲代和报告 hash。

下列状态均是“已修订并完成作者纯模型验证，等待 root 指派的独立 R2 delta 审查”，不是作者自审 Pass，也不是产品/真实库通过。只修改原两 docs 前缀；R1 报告、脚本、命令、分离双流、proof、root receipt、旧 manifest/receipt、原首错和原验证原件一律不覆盖。旧20项通过仍只证明旧覆盖。

## R1-01：封闭 Unknown 的不受信 harnessStage

`model.py` 新 `safe_harness_stage` 首先检查 `type(value) is str` 和固定集合；`unknown` 与 `safe_projection` 共用此门，后者在门失败时甚至不处理 diagnostic。非字符串、str 子类、私有路径、URL、未知值、带危险方法的对象均转字面 `collection-failure`，不复制原值，不调用其属性/str/repr/equality/hash。输出固定 Unknown/INTERNAL_ERROR、complete=false；保留此前完整成功阶段，collector 将此次记录为 incomplete，不补回原 stage 文本。

schema 与私有投影版本升 `/2`：`collection-failure` 仅在 Unknown/complete=false 分支允许；合法 `check-shapes` 阶段显式登记。37 个已有精确目标不改。旧 `/1` 只在原固定 candidate 解释，不靠 key 猜版本或默许新 stage。公共四字段 ErrorFrame、registry 与错误归责政策没有变化。

新增 `test_r1_01_stage_is_closed_before_any_untrusted_operation` 使用危险属性/字符串/相等/哈希对象及 str 子类，断言方法零调用、每个输出 JSON 均 schema 合法，且没有路径/URL/未知文本。`test_r1_01_valid_stage_and_reserved_incomplete` 检查全部37合法阶段保留、Unknown不能匹配、reserved stage不能生成known complete，并核模型/schema白名单一致。

## R1-02：language identity 与跨输出唯一 BNode 双射

单图 `graph_isomorphic` 现在与 `graph/typed_graph` 一样，只对 literal.language 身份 casefold；IRI、datatype、lexical、raw/source 原文不变。新增 `identity_domain_equal/projection_layout/projection_identity_equal` 明列全 terminal RDF 槽，以一次全域双射覆盖 typed 图、N3 rdfs/rules、全部 evidence/premise/basis、scope selectedFacts/source/derivedAxioms、query cells 和 SHACL六字段（含sourceShape）。graph 模式只在 RDF 集合域比较，序列保位置、末项和重复。非 RDF 槽完整 exact，raw `_:a` 字符串不被误作引用。`matches` 先严格 schema，再做这一完整比较。

共享身份域是同一不可变 artifact 及明确消费其图的输出；实际 producer/graph→consumer 绑定仍须后继凭据，不能按同字面 label 合并独立 parse/producer。摘要不因同构被删：仍逐端对完整原 preimage核验，本模型对摘要字段 exact；未来若生成 BNode 标签导致摘要不同，需 owner另定明确关系/版本，不能伪造capture或泛化忽略变化字段。模型仍限最多8个BNode的小例域，超出不称产品限额或性能证明。

新增反例包括：合法 a/EN 对 p/en 正常同构；删尾rest、节点折叠、01/1、int/integer拒绝；typed图+N3evidence+query+SHACL sourceShape联合映射；节点数量相同但任一字段映射矛盾拒绝；独立片段分别同构而联合无双射拒绝；provenance各basis共用映射；重复premise/head序列不去重；raw语言/原文/null保持，quoted lexical `word@EN` 不被lowercase。数学联合 fixture不是合法数据BNode输入批准，也不是产品成功/capture/来源或准入证据。

## R1-03：两项前门调用与政策映射

完整核固定 ee2b 合同 SHA `d2cdc2e6017ad0257f30611d2928a60a116f4dc389cacdfc977c17efe13e2a23` 后，实际 shape 行为 **L51**、integer 行为 **L52**；R1/root提示中的相邻行号不代替实际来源。只读取已授权纯合同，没有读函数体。

- `shape/front-2` 的 `api` 为 `semantic.parse_turtle -> semantic.check_shapes`，`invocation` 逐步固定 `parse_turtle(dataText,format="turtle",shapes=False)`→`parse_turtle(shapesText,format="turtle",shapes=True)`→`check_shapes(dataGraph,shapesGraph)`。原 parameters `{}`、data/shapes文本、投影hash保持。F1目标在第二步parse-shapes，首步完整返回保留，末check未到达，不构造shapes部分视图/报告。
- `integer/other-datatype-1` 的 `api` 为 `semantic.validate_shacl_text`；显式 `data_policy="integer-illtyped-report-v1",range_policy="legacy"`。`parameters.dataPolicy→data_policy`、`parameters.rangePolicy→range_policy`逐字映射，无默认strict fallback，原camelCase参数/hash不变。

两项均 `newWrapper=null`，没有发明 `semantic.validate` wrapper。case/spec/coverage同步，owner为I05 canonical API/serializer owner；批准调用链与F1新首序提案分开。wide政策收紧为**仅data object的exact xsd:integer ill_typed**；xsd:int/nonNegativeInteger/decimal与shape侧不宽化，旧parse/query/reason/check strict不变，不改Q6/date/外联/公共registry/权限。库/API实际首错仍pending。

## 验证、原件与未解决边界

`selftest.py` 原20方法原字节保留；新 `selftest-r2.py` 加12方法，当前32方法实际exit0，分离stdout/stderr与argv在 `r2-validation.json`。第一次R2记录31方法exit0；随后增加provenance/N3数值联合反例及模型/schema枚举一致断言，第二次32方法exit0。两个实际记录分别保留，不覆写首次输出。没有新增失败被隐藏，也没有重新运行会覆写R1 proof的旧审查脚本。

全37 input parameters/datasetId/inputProjectionSha256/sourceRefs/expectedProjection/独立数学逐字段对固定R1 Git不变；`pure-sources.json`原字节不变。R1的全部原件和旧manifest/receipt/原首错等对57固定Git逐字保护，保护AGENTS不stage。新 `manifest-r2.json` 与后加实际候选回执另命名；原manifest只是原candidate的历史身份，不冒充当前修订的manifest。自排除/后加process记录明确，不写未来ref或循环自hash。

真实库分类、同次capture/expectation/allocation、预算、真实caller/producer来源、旧metadata完整编码、实际hooks/无I/O、source/package/正式Job/Store/selected/whole-H及原CI/两OS/真人/指定双审门全部pending，`wholeOracleComplete=false`。本窗仅stdlib/已授formatter/Git/docs，不运行产品、第三方、pytest/build、DB/GUI/网络/安装/探针/业务模拟，不借T03票。独立R2审者尚未给出结论。
