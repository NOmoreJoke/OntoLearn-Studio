# 初版固定方案独立审查原回执

审查agent：`/root/t02_independent_review`。以下保留其最终报告；原方案固定ref不改写。

**固定方案 `64bbfe27a2191e65e8e81ab34862b9867e46a034` 内审不通过，需补清两项 P2 设计缺口。**

1. **供应证明尚未贯穿确认与提交。**
   [方案:65](/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology/docs/iterations/T02/typed-changeset-integration-plan.md:65) 只明确初次 preview 时重读完整源；95–99行随后复用原确认／Job链。固定 T01 的 `ChangePreview.identity` 和提交复验主要绑定 state/control，没有绑定独立 metadata 证明、派生政策版本及当前 dependencyVector。这不足以兑现143行要求的同 revision 漂移拒绝。

   **建议：**S2明确供应证明如何绑定原 `preparedPlanRef`／持久 envelope，并在 confirm、Job接收和 commit 的原外层事务内重新复验；列明 T01 待修改路径及各阶段漂移反例，不能依赖客户端声明。

2. **累计预算缺少执行前计费机制。**
   [方案:111](/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology/docs/iterations/T02/typed-changeset-integration-plan.md:111) 的 term、保留池和工作预算尚无明确接点。冻结 T02 的 `change_preview` 在新 adapter 收到 Preview 前已经反复调用验证、RDF 编译和 term 解析；T01分页／确认也会重新读取完整计划、blob及历史。事后检查 adapter 输出不能约束此前工作。

   **建议：**S1/S2须在每次冻结函数调用前，按固定调用图保守预扣解析次数、字节、重复验证和同时保留副本；无法外部预扣时申请必要 meter 扩展。明确分页、失败路径及持久增长的累计规则，超限先拒绝。

其余核对结果：

- 完整 FR-200–204 差距和父功能验收均保留；首切片未冒充完整本体编辑。
- 人工单值事实映射到原 `edits[record_id]`、mapped／多支持拒绝边界合理。
- identifier 派生明确待 T01 批准，未宣称已实现或获许可。
- 34项固定来源及5项控制输入大小／哈希匹配；独立 AST 核对14项本地导入闭包无缺漏。
- 完整主方案已读，未运行、import 产品或修改文件。

这是方案审查结论，不替代产品验证或指定双外审。

原行号对应64bb固定版本；当前工作树方案随后修订，不能以当前行号重新解释旧意见。
