# M1 独立审查初次意见（原意见保留）

Reviewer：`/root/m1_independent_review`，独立于两个作者helper，未写文件。以下据其已返回的逐项意见及最终初审记录归档；本文件保留发现当时状态，后续处置见最终复核记录，不把初审“待修”重写成“已通过”。

## 初审结论

发现1个P1、3个P2。P1已静态复核修复；建议完成P2后冻结文档。没有发现需改七quality或扩大产品权限的问题。

### P1：SHACL fixture入口不兼容

初稿11格使用standalone `sh:PropertyShape; sh:targetNode ex:s`。固定3ef `_shapes`只接受NodeShape、恰一个targetClass及其sh:property指向的PropertyShape；白名单没有targetNode，nodes也为空。因此所有11格包括numeric基线先INVALID_SHAPE，不能到达主文宣称的guard/Validator。

建议：数据补`ex:s a ex:Focus`；shape采用`ex:node a sh:NodeShape; sh:targetClass ex:Focus; sh:property ex:shape`，property部分保原约束。不能为fixture扩大产品支持。原件为`review-first-C-inputs.json`，初稿hash绑定见author-method。独审已实际静态复核修后11格支持该入口，可到达各自所列guard。

### P2：字符串源与实际表示

两个rule conclusion使用`"ok"^^xsd:string`。旧schemaVersion1验证的rdf_value→rdf_snapshot.term将其canonical为plain Literal，n3不同会报NON_CANONICAL_TERM；I05 _profile_term也canonical_string，实际Graph head/selected N3为`"ok"`。

建议只将源定义和golden完整RDF head展示改canonical plain `"ok"`，不要求binder绕过既有门。SHACL string value同样用实际canonical `"a"`，或明确按抽象term身份比，不对未canonical展示逐字符串断言。P2前输入/golden原件分别留在`review-before-P2-supplemental-graph-inputs.json`、`review-before-P2-explanation-goldens.json`。

### P2：每个head的来源定位

match级rule source不足以明确三个head各自原定义定位。建议每个headIndex绑定`/cases/0/rules/0/conclusions/{i}`，重复head保留各自索引与源，不新增运行API或持久false trace。

### P2：数学输入与golden未物理分离

486域槽、648numeric、Number/Calendar等operand仅在golden内，主文却禁止producer读golden。未来无法遵守该合同消费数学cases。

建议assembler从同一独立作者常量直接落`math-operand-inputs.json`，只含id/left/right/operator或input，不含Number/Calendar/Boolean/reason期望。expected另存，按caseId关联。不能由被测结果生成，不能prod启动时扫描golden，也不能把此文档修正当产品授权。

### date inclusive 条件预期

只写pending遗漏可独立确定的核心分支。SPARQL2013 operator mapping的<=包含numeric/simple literal/string/boolean/dateTime，没有date；§17.3.1允许仅对原type-error补额外operand rows。SHACL2017 §4.3.2中比较非true含error产生带该value的结果。

建议分别明确：unextended core→conforms=false+MinInclusiveConstraintComponent；若I05明确选择date operator扩展，同合法日期同offset等值→conforms=true。当前实际仍为入口INVALID_SHAPE，不把任何分支当actual，不擅改Q6/采用I05扩展。固定原文依据：[SPARQL mapping](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#OperatorMapping)、[operator扩展](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#operatorExtensibility)、[SHACL minInclusive](https://www.w3.org/TR/2017/REC-shacl-20170720/#MinInclusiveConstraintComponent)。

## 独立实际检查

- 31份固定原件raw/ref/SHA，26 future path旧hash及新增不存在，均核对。
- 全部486域分类槽、648numeric实例：对采用政策/手工truth rows独立核对。
- 38 Number：原十进精确Fraction与nearest-even相邻区间，含subnormal/负零/overflow，未调用产品量化器。
- 15 Calendar：January-origin日序与offset/fraction字段；5组混型关系及差值，未发现数学golden错误。
- 五个graph定义键、实际Catalog声明；domain/range/subclass-transitive/type四类finite规则的有序直接前件、depth、leaf并集正确。
- census摘录与原census同值；E.5原源e81b0d02…的E001–E016、round1–4、每轮inputSequence0–3、四条addFacts及R-risk/B-risk对应正确。alarm rdf:type不是R-risk前件的说明正确。

方法：只读文件/Git/标准库JSON/int/Fraction算式与固定W3C原文。未导入/运行产品、测试、parser、比较器、reasoner或Validator，未写文件。没有UI/worker/Store/性能/容量/平台运行结论。

独审临时Jan-origin算式首次因`else28`漏空格SyntaxError退出1，修正后退出0；无文件写，不是产品失败。作者另有同类临时算式错误及文档脚本自扫描空输出错误，分别留author-method与static-first-failure；不隐去首失败。
