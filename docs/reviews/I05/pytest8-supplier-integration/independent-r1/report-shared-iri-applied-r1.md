# I05 shared-iri-applied-r1 独立落地静态审查

结论：Limited Pass，未发现实际落地偏离v2或新增P1/P2。实际共享改动、当前两源和留存的green/Ruff产物均已按限定范围核验；本独立审查没有运行产品、Ruff或formatter。四case通过只覆盖此次回归和dict消费用例，不等于417采集或完整check通过。

## 实际落地与v2等同

当前semantic.py为66258B，SHA-256 `d6c5f5c38aec310de726f73568e1086bf4de95117cbdf664ae1384fcd6808392`。独立将当前_terms一行签名反展开为v2原三行签名后，文件精确还原66264B/`4b81da30fd3d2623bfc4cc8ee4b8789be2eb9077ed6a4fafb91e61a29d40257b`，与先前内存v2及green绑定完全相同；两版wholeAST亦相同。因此formatter只改变该签名排版，没有夹带实现变化。

v2先前已独立证明：_terms私有keyword-only预检查默认False；仅既有_parse_turtle传True；预检查位于_terms原OWL.imports全图拒绝之后、n3排序之前；使用原URIRef lexical条件和既有ABSOLUTE_IRI_REQUIRED；原sorted/原检查仍保留。此次实际字节等同该v2，故这些静态结论适用于本次落地。公共parse_turtle签名、generic异常策略、Literal datatype、新text既有_check_iris以及semantic_turtle均不由此改写。

## 两源变化的约束

probe仍为d1fb原字节102669B，SHA-256 `05f4ac85f883f40142782e9ee3943b8df9593ddf5a35e318ca35bbd6781a6dd4`。其原八依赖版本预期、两JSON资源的声明身份、417清单选择/数量预期、guard、identity与公共错误逻辑均未改。这里是源码字节不变的证据；两JSON资产实体本轮没有再次读取，不能称为本轮新验证资产字节。

当前测试75955B，SHA-256 `fec5a98a78168f9720d7224f791e95d0bd1936473646eb63b30803be7d863c39`。相对d1fb，仅有：

- 先前已审的两处原始BytesIO落盘诊断；既有full-v1调用和全部断言保留。
- 原RootRef属性假定改为两个精确tuple dict断言；保留step/ordinal0、原leaf引用和顺序，并约束映射形状。
- 一个三position参数化回归，直接调用真实semantic.parse_turtle，并要求真实SemanticError.code精确等于ABSOLUTE_IRI_REQUIRED。没有patch/fake parse、修改selector或捕获普通Exception凑通过。

独立移除新回归函数、逆转诊断与该3旧断言→2新断言改写后，整个测试AST与d1fb相同。因此原417相关断言及其上下文保持。供应商三路径的固定采纳由主 agent 另外处理，本审查未越界重新审读该施工面。

## 实际验证产物

独立全文读取green绑定及5份命令收据/全部10个stdout、stderr文件，逐一核对实际字节和收据hash：

| 主 agent 已执行项目 | 留存结果 |
| --- | --- |
| 新subject/predicate/object回归 + 原badbytes[True] | exit0，4passed/0.65s；launcher1.108914s，stderr0 |
| 三源Ruff lint | exit0，原stdout精确为`[]`，stderr0 |
| 首次三源format check | exit1，明确仅semantic.py私有签名排版需合并，另两源已格式化 |
| semantic.py format write | exit0，1file reformatted，before/after身份与独立重建吻合 |
| 第二次三源format check | exit0，3files already formatted，stderr0 |

首次format失败原样保留。三源lint记录发生于format write之前；后续排版AST不变，本报告没有伪造一次format后的新lint运行。format-check-02收据没有执行起止时间，本审查也没有补造。green时semantic为原提议排版66264B，当前66258B只改签名排版，AST等同；没有虚称当前字节另跑过green。

green选择的4case不请求full_run/B1 fixture；其结果不能代替当前已变化semantic身份对应的probe preflight、417full-v1、B1或完整原check。主 agent计划先冻结实际canonical supplier/process，再更新probe唯一semantic source pin及SOURCE/PROCESS refs；在真实身份刷新完成前，本报告不将原pin不变记成身份验收已完成，也不指示绕开identity检查。

## 保留限制

父 agent已获共享semantic.py唯一writer授权并接受普通text混合违规优先级边界；本独立审查只核落地，没有代授兼容性批准。直接Graph默认路径保原验证顺序，普通text预扫描行为修复范围保持先前v2说明。合法图性能未测，不作量化；Literal datatype不扩围。

本轮仅Git、文件/hash、stdlib AST与JSON检查，无产品/测试/Ruff/formatter执行，没有产品写入。所有旧报告保留；下一步真实source/process pin、后续完整运行及整体验收仍未关闭。
