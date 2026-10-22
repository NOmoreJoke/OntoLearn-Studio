# C5处置与新指定审查入口

**当前产品候选e5ad54e5762157cafe532c2a0c07c22e8dd737cb，已通过内部独立复核；尚无此候选的指定双审。** 批准base5f不变。完整R1十一项处置见`disposition-c4.md`表；C4原不通过见`independent-c4-review.md`，不改旧结论。

C5只对model.py及`test_ontology_input_boundaries.py`补不可UTF-8文本拒绝和31项具体测试；project、Entity IRI、Triple三个术语、labels/definitions、synonyms/examples、external source均在进入摘要/解析前用固定诊断拒绝未配对surrogate。字符串不替换、不归一化、digest编码不改。C4剩余P2的三实际反例（project/synonyms/examples）先在旧实现真实失败，完整原流`test-results/t02-s1-c5/streams/unicode-c4-first-failure.log`保留EXIT1；C5全部新增用例和合法中文/emoji/分解重音原文正例通过。

最后完整`npm run check`真实exit0：634TS/1164Py，ontology112passed；本次新代码后已完整验证，不以C4结果替代。UI/harness/TS/service/source_projection未再变化，六UI输入与35aa逐字节相同，沿用其21项合成callback headless证据；不重复无变化UI，不作为Store/IPC/e2e证明。准确源hash/输入/命令/流及恢复见`c5-evidence-manifest.json`，C5四份原始流包1799B/SHA `0bb43ca61c22fc89a583d13e44c988d369c8f2b4f2150c57ce35fff66b841e6f`，逐成员读回一致；C4的84份首失败/成功/截图/构建仍完整封存，不覆盖。

独立C5复核实际通过，报告`independent-c5-review.md`；其额外Unicode内存探针与owner全仓日志证据分开记。C4 Fail仅对其固定版本，C5新结果不回写C4。M-P2仅关闭本轮真实发现的缺口，不保证任意Python对象/无限输入空间。

R1其余十项事实和处置保留：基准引用说明、可编辑模板复制后create、25对象分页与事实等UI行为、树计算、实际负例、默认类及幂等事实、字段值类型已处理；**Z-P3-1小写语言子集仍延期正式adapter，Z-P3-5完整前置parser未实现**，不得借“处置”改成完整语言导入/正式parser通过。全部延期/部分接受理由连同原意见必须交两个全新指定任务判断，不能由owner自行降低级别或删验收。

原验收、公共契约、Store/Job/main/preload/App、依赖/锁/CI均无变化。当前20产品/测试/fixture+5harness完整范围，原19全保留并新增一个专属边界测试文件；所有历史C1/C2/C3/C4、原首失败/报告、纯typed方案及全父缺口继续作为审查输入。任何后继代码/测试/验收或基线变化仍新候选、必要验证、双方全新同版完整审。未push/PR/merge，未完成父功能或原Goal。
