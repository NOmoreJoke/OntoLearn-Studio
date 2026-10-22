# I05 shared-iri-static-r1 独立静态复核

结论：未应用提议在最短链内技术方向成立，可使已存在的 URIRef lexical 拒绝先于 n3 排序执行；未发现新增 P1/P2。该结论是有限静态审查，不是共享写入或兼容性批准。普通入口从原先可能泄漏的普通 Exception 变为既有稳定拒绝码，是明确的行为修复，须由根协调者指定唯一 writer 并裁定兼容边界。

## 固定最短链

只对固定2cf的 semantic.py 六函数（_text、_terms、parse_turtle、_parse_turtle、_shacl_text_iris、_key）、semantic_turtle.py::parse_graph，以及直接异常类型 SemanticError 作 Git/AST 抽取只读；未 import/执行这些函数，也没有跟随其他语义/生产算法。

- public parse_turtle 111–113 转发至 _parse_turtle；_check_iris 默认False。
- _parse_turtle 123–126 的 try/except 只包 parse_graph；该解析器92–99只构造/填充Graph并返回。_terms 在131行、parser try外运行。
- _terms 71行先执行 sorted(graph,key=_key)；_key 247–248直接对term.n3()求排序键；URIRef lexical拒绝在79–82才执行。
- 新 text 专用 _shacl_text_iris 135–144 已显式注释 n3 排序可能抛出包含非法拼写的未分类异常，并在排序前检查IRI（含Literal datatype）。它只有在 _check_iris=True 路径执行，不能覆盖默认普通parse入口。
- SemanticError是ValueError子类，__init__保留code并用code作消息；ABSOLUTE_IRI_REQUIRED是现有拒绝码。

上述先排序后校验、且排序异常在parser转换try之外的控制流，是足以解释已观察parse调用边界泄漏Exception的静态缺陷链。它与新A/B同首败相符，但本审查没有读front-5完整输入或取得异常栈，因此不把n3实际抛出位置冒充动态栈证据，也不补写T03首次未保留的firstFailure。

## 未应用提议精确性

原提议755B，SHA-256 `63c75cf21da84c50d4c7a2f4fa5b0f1aa7ebf9a7e923011fad48dcebc09453d1`；JSON969B，SHA-256 `e624c3f085402359ce4dfb96878f32ebae1c564a20d481a851f7805dcbb28fc0`。在内存中按提议插入7行后进行AST比较，没有写共享文件。

- 新增预扫描只针对triple中的URIRef，使用与旧检查完全相同的条件和同一SemanticError raise；两者相关If（条件及raise）AST相同。
- 去掉唯一新增预扫描For后，整个semantic.py的AST与固定原文件相同。原OWL.imports全图优先检查、原sorted顺序、原逐项校验及错误码全部保留。
- 未捕获或降级任何generic Exception；未改变Literal datatype政策；没有新增fallback、expected篡改或语义旁路。
- 当前共享semantic.py仍与固定原文件字节相同：65749B，SHA-256 `60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07`。内存提议66117B，SHA-256 `0cfc956fc65c3dd6db9aa9a5973618ee4735751d1fb54c80800ad60d08202f93`，不是已落地候选。

## 同版非法IRI测试证据

先按live *.py测试查找未命中ABSOLUTE_IRI_REQUIRED；这只描述该查找范围，不能说测试不存在。之后在固定2cf保存的同版6891原始测试归档中定位并只读相关窗口：

- test_semantic_shacl_entry.py.raw 212–228包含非法IRI对象期望ABSOLUTE_IRI_REQUIRED；231–244参数化覆盖subject/predicate/datatype/shape-path及strict/WIDE两政策，明确在n3排序前分类非法IRI。validate 44–48实际调用validate_shacl_text。
- test_semantic_shacl_date_policy.py.raw 505–531的前门拒绝用例包含`<urn:bad iri>`→ABSOLUTE_IRI_REQUIRED；reject 183–188还要求validatorCalls为空、result为None。

这支持现有稳定码及新text入口的分类意图，不能当作普通parse_turtle入口的同一回归用例已存在或已经运行。归档在固定2cf可查、文件名标记6891；本次没有运行这些测试，也没有重新认证整个归档包。

## 唯一owner必须裁定的兼容性边界

该预扫描遍历整个图后才进入原sorted循环。对所有URIRef lexical合法的图，新增检查不改变原验证/排序路径；未做性能测量，不量化额外遍历成本。

对同时存在非法URIRef与其他拒绝条件的混合图，预扫描可能使ABSOLUTE_IRI_REQUIRED先于原sorted遍历下的其他稳定拒绝码出现。尤其原lexical条件也含“没有冒号”分支，不能把所有命中都等同于n3必抛的非法字符分支。原OWL.imports全图优先检查位于预扫描之前，仍维持其原优先级；其他跨triple拒绝优先级没有全部证明不变。这是待owner裁定和回归验证的行为边界，不在缺乏公共兼容性要求时擅自记为已验证P2缺陷，也不能笼统称“所有旧错误优先级不变”。

最小验收应验证普通parse入口中非法URIRef位于subject/predicate/object时稳定拒绝、合法图排序/结果不变、parser语法错误仍走INVALID_TURTLE、OWL.imports优先拒绝保持，并按owner裁定补混合违规优先级用例。Literal datatype非法IRI不属于本提议覆盖范围；不能由此宣称所有n3异常已关闭。共享实现改变后还须真实同版source pin/供应商证据，不能跳过身份校验。

本轮没有写共享产品、修改测试或运行产品。parse修复仍未应用，兼容性、回归、真实同版身份和完整check继续由根协调者及唯一负责人完成。所有既有报告保持原样，只新增shared-iri-static-r1后缀产物。
