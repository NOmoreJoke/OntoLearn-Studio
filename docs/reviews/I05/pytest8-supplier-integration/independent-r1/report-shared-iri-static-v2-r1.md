# I05 shared-iri-static-v2-r1 独立前审

结论：v2 未发现静态阻断或新增 P1/P2，可供父 agent 按已取得的唯一 writer 授权实施并做 green 验证。本结论只评价提议技术范围，不代替根协调者的兼容性决定。v1 报告与提议保留为历史建议，v1 不作为本次实际实施候选。

## v2 的精确范围

v2 patch1540B，SHA-256 `7c4b46260e218dacbdc5bcc0d4d2c8595a629ef4caf81f8355d5768f18fd6b6e`；其JSON459B，SHA-256 `26b2207138a7cedb730dffbeea657faec9bfc19e45db83118920c968c8bccfa6`。只在内存中精确应用至固定2cf semantic.py，并作AST检查，未写产品：

1. _terms 新增私有keyword-only参数 `_precheck_iris=False`，已有调用方式保持可用。
2. _terms 在已有OWL.imports全图拒绝之后、原sorted之前新增 `_precheck_iris` 条件块，内层URIRef lexical条件与raise的AST和旧条件完全相同，仍用ABSOLUTE_IRI_REQUIRED。
3. 只有已有_parse_turtle到_terms的调用传 `_precheck_iris=True`；该函数原有参数传递不变。

逆转这三项后，整个semantic.py AST与固定2cf完全相同。公共parse_turtle签名不变，原sorted/原校验保留，parser try/异常转换没有扩大，没有generic Exception降级，没有改semantic_turtle。内存v2为66264B，SHA-256 `4b81da30fd3d2623bfc4cc8ee4b8789be2eb9077ed6a4fafb91e61a29d40257b`；这是提议身份，不是已经执行的green候选身份。

其他直接Graph调用_terms不传新私有参数时，预扫描不运行，仍走原校验顺序。这收窄了v1对所有_terms调用者的影响。已有new text `_check_iris`及_shacl_text_iris调用仍在原位置；其Literal datatype政策不变。没有把新的URIRef预扫描扩展到Literal datatype。

## red 实证

独立全文读了主 agent 留存的实际red收据及原stdout/stderr，并核对字节/hash：stdout4798B，SHA-256 `a64ffc0a0d40466b6bd911758dd4ceff1b44c445af65de8f1a056c04e5453917`；stderr0B。收据exit1；stdout记录3failed/0.94s，launcher记录1.456453s，两者不混用。

subject、predicate、object三个参数化用例的真实trace均为：public parse_turtle113 → _parse_turtle131 → _terms71的sorted → _key248 → rdflib.term.n3:317抛Exception，非法拼写为urn:bad iri。它为此前“在lexical guard之前n3异常逃逸”的静态链提供了直接动态栈证据，强于仅有新A/B的parse调用边界记录。

这些red记录来自新增回归，不是T03首次运行，也不是v2实施后结果。未把新trace倒填T03旧BytesIO，未宣称修复后已经通过。此独立审查没有import或执行pytest/产品；只读主 agent 的真实运行产物。

## 保留边界

普通text入口从可能泄漏普通Exception变为既有ABSOLUTE_IRI_REQUIRED，是有意行为修复。v2仍在整个text解析得到的graph上先扫描URIRef，因此同一text中多种违规的拒绝优先级可能改变；父 agent 已明确接受该局部边界，本独立审查不另行批准兼容性。其他direct Graph默认路径的顺序保持，不等于所有text混合违规顺序保持。

共享修复实施后的精确字节、对应真实source pin、green/完整check及同版验证仍由父 agent 完成。合法输入额外遍历成本未测，不量化。Literal datatype异常不在本次扩围范围；不宣称所有n3可能异常均已关闭。

此前shared-iri-static-r1报告记录了v1和相关固定API测试证据，保持原样；本轮另增v2后缀产物。没有产品写入、测试执行、重启或kill动作；没有代替根协调者分配其他共享writer。
