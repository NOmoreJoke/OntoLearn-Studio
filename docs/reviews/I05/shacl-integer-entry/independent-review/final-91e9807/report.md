# SHACL integer entry：91e9807 最小IRI修复复核

结论：**有限通过，IE-O1在新增独立文本入口内关闭；没有发现本次修复新增阻断。**被审固定产品为 `91e98074a334931648e9b7c8f58a3b5e8f93a642`。首轮be61/01不通过报告及全部原件保持冻结；本报告只复核IE-O1修复和必要运行证据，不重做旧包审计。

## 固定范围与身份

唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-shacl-integer-entry`，同feature分支；continuation仍为 `a15f1478e398fb3b58fd60b1421a9cad04fdb430`。授权、最新AGENTS/common及产品范围沿首审，不扩大writer。当前candidate145项完整处理：145当前字节等候选/固定Git身份，143只读的Git blob及SHA与首候选相同；未重复审其内容。旧1238过程仅Git mode/type/blob核同新ref，没有重读257MB。首审write-lock全部成员SHA未变。

| 修复成员                     | bytes | SHA-256                                                            |
| ---------------------------- | ----: | ------------------------------------------------------------------ |
| semantic.py                  | 58495 | `1a2bfd40bc30a7a4ba5f90ab79cba5d9e0a4311b028681d8ceced528e1982075` |
| test_semantic_shacl_entry.py | 14604 | `f86de5f1a41e186d80a0042d574e7e15ec3421966a873c930169f685bb6b63a0` |

完整身份和方法见 `static-delta-verification.json`。旧测试的全部AST逐项不变；新增唯一参数化函数产生subject/predicate/datatype/shape-path × strict/wide八个向量。原失败object IRI断言未删除、未放宽。

## IE-O1修复的源码判断

`_parse_turtle`新增私有 `_check_iris=False`。当显式启用时，在真实parse_graph和原MAX_TRIPLES检查后、任何 `_terms/_key/n3` 前调用 `_shacl_text_iris`。新helper遍历实际图：普通term检查实际URIRef，Literal检查其datatype URIRef；用原_terms相同的absolute/空白/非法N3字符边界，固定抛ABSOLUTE_IRI_REQUIRED。没有捕获任意异常改标签，没有删图或修值。

新 `validate_shacl_text` 的data和shapes两段解析显式True；shape同时保持shapes=True和illtyped默认False。新入口strict/wide两policy都得到同一IRI前门；它没有借宽数据策略放松shape参数。原public parse_turtle仍不传新flag、默认False，旧_terms及旧parser调用次序不变。私有flag不是Graph能力或来源认证。

独立AST确认相对be61只改变已有 `_parse_turtle/validate_shacl_text`、增加一个helper；旧_terms、check_shapes/query/reason、原Validator runner及全部旧测试AST均不变。新入口policy必填/精确分派、版本与完整report结构不变。date仍pending且inclusive date bound拒绝，未知/非有限/外联/blank-node/资源门不放松。错误表、正式execution/scopes/Job/Store/selected及依赖仍只读。

这项修复只对新独立文本入口关闭IE-O1，不声称改好了旧API所有坏IRI的潜在错误分类。

## 运行证据

全文读取根03完整stdout、stderr及终态metadata：exit0/no timeout/stderr0，lint/format/typecheck/build/ruff通过，TS1125通过，Python实际 **5060 passed /44 skipped /1 warning，139.33s**。原坏decimal的库warning保留，不用logger/warnings patch清除。70新实例、77DAG和26shape在同次完整check承载，不与旧专项累计。

03的145 sourcesBefore/After逐项等固定91e候选，没有混WIP。04核12归档源exit0/no timeout，05产品diff检查exit0；两者145前后同样绑定91e，补充原metadata/双流成员见 `supplemental-root-records.json`。本审自身产品/测试运行次数为0。

全部78份integer-entry观察与26份legacy-shape观察已读取，保存完整原件成员SHA及观察在 `existing-evidence-verification.json`。integer入口为14次真实Validator调用、64次前门拒绝；原object坏IRI及新增8向量全部为SemanticError/ABSOLUTE_IRI_REQUIRED、Validator0，没有普通Exception漏出该输入门。date、其它datatype/nonfinite/shape参数/外联/资源/旧API状态隔离断言保留且通过。

独立从这14次实际Validator原始RDF reportTriples定位所有sh:ValidationResult，再逐focusNode/resultPath/sourceConstraintComponent/sourceShape/可选value/resultSeverity重建规范六字段，逐行核同返回report；缺省value保持None，没有预造value。返回conforms也与真实run捕获值一致。原C-illtyped报告仍是完整DatatypeConstraintComponent违规且lexical原样；无目标/无约束仍允许真实true。旧26shape观察保持9次实际调用与17次前门拒绝。

本审只做固定Git/AST/hash及既有证据读取，没有供应Validator结果、重跑旧专项或完整check。首轮be61/01的失败报告/原始trace/报告和静态reader首失败均保持原字节，不改旧结论追认本次修复。

## 限制与交接

全部静态和记录读取脚本从创建即.py.raw，未import产品、执行产品或测试，未修改依赖。只写 `independent-review/final-91e9807/`，首审子prefix及所有其他产品/测试/过程/AGENTS/环境/Goal均未写，未stage/commit/branch；无GUI/native/e2e/HMR/网络/外部模型/付费。

本审不替预算、正式接线、date政策、父功能、指定同版双外审、CI/OS/真人或develop门签字。完成原件成员清单、显式取消ignore的文档检查及写锁后停止写入。
