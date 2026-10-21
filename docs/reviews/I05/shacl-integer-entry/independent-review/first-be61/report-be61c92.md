# SHACL 非法整数独立入口：be61c92 首审

结论：**不通过；存在一个P2输入错误边界未闭合。** 固定产品 `be61c9284b88e0df1f3d58114bb2a3437a9d2005` 的非法IRI输入在进入Validator前抛原始库Exception，未落入新增测试要求的固定SemanticError。根完整check实际1 failed/5051 passed/44 skipped/1 warning；不能以其余新报告正确或静态边界通过替代这一失败。

本发现不表述为本次新引入的旧API regression：共享strict路径原先已有N3排序先于IRI检查的潜在问题，此次新入口/新验收向量将其实际暴露。以下只评判本最小组件入口窗口，不重审旧DAG包或257MB过程。

## 固定输入、方法与范围

唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-shacl-integer-entry`，分支 `feature/weekly-i05-shacl-integer-entry`，continuation `a15f1478e398fb3b58fd60b1421a9cad04fdb430`。全文读根4579B授权窗口（SHA `dd26f48c29bdafafaf0f0d4325bd6c8ab9141fb56fae89bba2259e2d6b3c0f3e`）、完整144行固定输入55779B（SHA `4238f8d3d8ea02eaea6c97fc69a5b6afc02ae4b87c9faab22a7e774f0fb0a975`），并逐行处理。最新操作AGENTS及common完整规则已读，四份本树raw逐字等对应根原件。操作规则更新不被冒作产品变化。

全文读固定源码diff和新增335行测试，实际恰semantic.py修改、新测试一新增；145项当前字节/候选SHA/固定Git独立核同，143只读逐采用sourceRef、sourceTree当前原件、bytes/SHA相同。旧1238过程仅核continuation与本候选Git mode/type/blob身份相同，未重复读取全包内容。完整方法与145身份在 `static-verification.json`。

| 被审成员                     | bytes | SHA-256                                                            |
| ---------------------------- | ----: | ------------------------------------------------------------------ |
| semantic.py                  | 57831 | `c485581f42ce5223e5dbb5d3ad90b59e2d627a99682b6e9876128a0e030356f3` |
| test_semantic_shacl_entry.py | 13823 | `9443d3879b569a1df73ef5a00ddcca86d08f3899e91ef2a3b26085ea218fe48d` |

本审没有import产品、运行产品/测试或修改依赖。只执行stdlib固定Git/hash/AST及既有运行记录读取。静态reader首跑因docstring从原函数保留到public facade、未复制到private helper而触发过严AST断言；首版脚本及双流已保留。修正为剔除docstring后比较执行语句，静态复核通过，未改产品或测试。

## IE-O1 / P2：非法IRI在固定错误门之前抛原始库异常

源码位置：`semantic.py:1364` 新入口解析数据，`122` 调 `_terms`，`66` 先 `sorted(graph, key=_key)`，`226–227` 对每term执行n3。原IRI检查在 `_terms:75–77`，排序完成后才到达。固定RDFLib 7.6.0的URIRef.n3在 `term.py:317` 对非法IRI抛普通Exception，包含原IRI值。

最小实际触发是新测试的 `<urn:bad|value>` 数据object，其他事实和shape均合法，data_policy为integer-illtyped-report-v1、range_policy为legacy。根01完整trace实际为：新入口→私有parser→_terms排序→_key→URIRef.n3→Exception。对应 `integer-entry-reports` 原件记录 `validatorCalls=[]`、result=null、error.type=Exception/code=null；不是预期的ABSOLUTE_IRI_REQUIRED，也不是Validator违规报告。原件及其完整SHA绑定在 `first-failure-evidence.json`。

影响：新增API的这项固定输入拒绝边界尚未完成，现有固定错误约定和验收测试失败。未进入Validator说明它没有因此放行坏IRI，但原始Exception不能等同于完成约定的安全拒绝。没有声称该独立Python API已经接IPC或发生跨进程泄露。

建议：保留该原反例/断言，不吞掉所有异常统一贴IRI标签。若采用新入口专用N3前IRI检查，需针对实际URIRef及literal datatype IRI作精确检查，再进入既有排序/terms链；旧API策略和共享调用顺序仍须保留。若决定改共享_terms的检查次序，应明确其旧路径兼容范围并固定新候选，以实际证据核验，不能在旧ref上追认修复。

## 已确认的正确边界

新 `validate_shacl_text` 的两个keyword-only policy均无默认值，exact str检查先于值分派；仅strict/integer-illtyped-report-v1及range legacy获准。未知策略使用已有SCOPE_SELECTION_TYPE_INVALID，没有改公有错误表或正式error adapter。入口返回独立版本/两项实际policy和原report，旧SEMANTICS_VERSION、旧check_shapes报告结构不变，没有cache接线或Graph认证标签。

唯一宽点在 `_terms:85–92`，同时要求私有allow、not shapes、object位置、datatype精确等xsd:integer、ill_typed is True；仍执行其后的datatype/nonfinite、RDF/type、IRI/blank-node/词汇及scope门。shape仍经strict parser与`_shapes`原门，没有通过shapes=True放宽数据，也没有捕获strict parse错误后吞错继续。未改值、删三元组或预造violation。

独立AST确认旧query/reason及其余原函数不变；原parser和原Validator执行体提取到private helpers后，除新增私有policy keyword及docstring位置外执行AST相同。所有旧调用默认False，未修改全局转换表、DAWG、parser/logger或constraint-map。正式semantic_execution和scopes都仍只读、严格；本独立API成功不能代表正式execution/Job/Store/selected支持illtyped。

date仍不在inclusive允许集，range其它选项明确拒绝；Q6未重开。未知datatype、nonfinite、外联、blank-node和shape参数保留原严格检查。IE-O1指出的是IRI检查次序导致错误分类未闭合，不否认这些其他门。

## 实际运行证据与测试审查

消费根本轮01完整stdout、stderr和终态metadata：exit1/no timeout/stderr0，TS1125及lint/format/typecheck/build/ruff通过，Python **1 failed/5051 passed/44 skipped/1 warning，141.68s**。145 sourcesBefore/After逐项等固定be61候选，没有混WIP。失败只有上述非法IRI项；decimal的“weird numerical”序列化warning另在原stdout保留，不为清日志改logger。

新增62测试产生70个独立观察：14次真实Validator调用，56次前门拒绝（其中坏IRI是错误Exception类型）。旧26shape报告仍产生9次真实Validator调用。全部观察原件已读取和记录SHA，见 `first-failure-evidence.json`；没有拿计数代替断言。

原C-illtyped宽入口实际1次调用、false、DatatypeConstraintComponent完整六字段，保留原not-an-int lexical和两条实际事实；strict入口0调用拒绝。其他坏integer lexical、合法+01 lexical/policy身份、无目标与无约束的真实true、maxCount可选value=null均有真实报告，observer只委托原Validator.run，没有供应报告。测试模块预载golden，但期望选择和比较在真实返回后，golden未送入产品输入。

宽入口后原parse/query/reason/check及再次strict入口的状态隔离断言保留；其余datatype、shape坏参数、date、外联、结构和资源项亦保留。新报告的真实raw RDF reportTriples保留实际BNode身份，断言使用规范六字段而非虚构固定报告序列化。旧测试和golden均未改。

`verify-existing-evidence.py.raw`是为成功终态预备、未执行的reader草稿；实际本候选只执行 `verify-first-failure.py.raw` 读取失败证据，没有把未执行或失败记录称为通过。后续修复和验证必须作为新ref/delta，首失败原件不能覆盖。

按根交接要求，本首审材料原字节移至 `independent-review/first-be61/`；原argv仍保留真实执行时的旧路径，不改写历史命令或声称归档后重跑。脚本与双流字节不变。上述“当前身份”指原静态/运行各自采样时刻；开始修复后本报告只绑定固定be61 Git和原件，不纳入WIP。

## 交接边界

仅写本新independent-review目录，全部脚本.py.raw；无产品/测试/其他过程/AGENTS/环境/Goal写入，无stage/commit/branch，无GUI/native/e2e/HMR/网络/模型/服务/付费。报告及成员SHA/写锁交付后停止写入。未关闭date、正式接线或父功能、指定同版双外审、CI/OS/真人、develop等门。
