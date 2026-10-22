# C4固定35aa独立完整复核原结论

来源：独立agent `/root/t02_independent_review` 真实终态，原T02转存。固定`35aa93fc007e92632d83747f7fe345295db340c8`，完整493→35aa本线实现/专测/harness/交接范围。

**不通过：M-P2-1仍有可复现Unicode异常边界残留。其余修复未发现阻断性回归。**

## 残留P2

model.py:101仅检查project为非空str，:151的synonyms/examples不检查Unicode可编码性；service.py:111的`ensure_ascii=False`后UTF-8编码会抛原生异常。独立agent在内存实际复现：

```python
s = Snapshot("p", 0, (Entity("urn:e", "class", "E"),))
change_preview(replace(s, project="p\ud800"))
```

project、基准synonyms、examples三路均抛`UnicodeEncodeError`。该值可由JSON转义解码产生，不依赖恶意Python自定义对象。这是原M-P2残留，非35aa新引入；当前无正式入口或写入影响。应在文本前门按固定reason/location拒绝不可编码字符串，覆盖基准和Put，不能静默替换或仅为避错改digest编码语义。

## 全部11项核对

- M-P2：六反例与常见类型守卫已修；独立440组错误类型内存探针无原生异常，但Unicode残留使整体仅部分关闭。
- M-P3-1：基准影响语义、全部引用/RDF移除集合已正确保留并标注。
- M-P3-2：死copy移除，四类型复制后完整create，不虚构持久谱系。
- M-P3-3：21项确含25对象分页、搜索、复制、新建、assert/retract、事实基准、错误和删除影响；仅合成callback呈现。
- M-P3-4：memo/索引正确，关闭无条件重算和反复全类扫描；无整体线性/性能数字承诺。
- M-P3-5：原缺16reason均有实际负例；静态42字面量reason均出现于测试不等于输入空间全部覆盖。
- Z-P3-1：小写子集保留限制，未实现全部合法RDF语言输入；未来I05/T01交换/归一化/往返仍待，不能无条件关闭。
- Z-P3-2：默认rdfs/Copy直接断言已补。
- Z-P3-3：当前集合幂等语义已完整断言，未来已有提示仍呈现选择。
- Z-P3-4：update泛型和classType显式收窄正确。
- Z-P3-5：规范示例/固定失败呈现已处置当前页面可用性，未加前端parser，正式引擎/adapter不可由合成探针替代。

## 实际证据和边界

UI六输入hash匹配35aa，21项JSON/两截图/manifest匹配，首失败保留；集成日志实际634TS/1133Py EXIT0，专项81 passed EXIT0，独立agent未重复这些检查。另独立执行400组类图旧/新差分内存探针，完整结果和顺序一致，含循环/多父/缺失/重复父；首次因无esbuild未执行，改用本树TypeScript完成。25对象可编译全部45定义三元组无遗漏，另有一条明确实例断言。来源校验未改变fact IDs/来源/多重支持/只读职责。

独立agent未改文件/GUI/重跑全仓，未发现新writer/确认/metadata授权；旧493指定Pass不传给35aa。此报告不替代后继指定双审、父验收或发布门。
