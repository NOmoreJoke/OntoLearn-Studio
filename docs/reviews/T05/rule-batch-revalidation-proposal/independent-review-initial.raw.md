独立静态审查结论：三池重放方案的核心成功蕴含成立，未发现数学阻断；建议澄清一处入口检查计费歧义后冻结。此结论不授予实施或 I05 消费许可。

审查对象固定为提案 `9b3c9145…`／22912 B。已全文读取授权、提案、input-bindings、静态字节算式及收据；静态读取固定 `1e3e0ee` 的 firing、profile、terms、comparator 源码及 numbers 相关部分。未执行产品、未读取主线 oracle、未修改任何文件。

1. **三池费用来源可对应固定实现。**
   - replay 使用同一 definitions/catalog 和完整原有序 matches，执行原 compile＋evaluate；保留原 bindings 顺序能避免 `_resolve` 线性查找费用变化。输入别名逐出现收费，复制同内容对象不改变 canonical 编码或费用。
   - saved-encoding 对完整保存结果只编码一次。合法保存结果的字段、顺序、类型和 occurrence 与原最终输出一致，因此其 work/output 是原成功执行的一段。
   - saved-issuance 的每个 left/right `check_value`，对应原 `_one → compare_values` 中同一 true firing 的检查。重复引用仍逐次收费；false matches、编译期比较和其他执行工作只增加原费用。因此该池 work/input 为原费用子集。
   - 两次 payload 相等、digest/profile 相等及固定 group/comparison 遍历可由 K 覆盖；`3W+K`、`2I`、`2O` 是 debit/编码界，文档正确限制其不是耗时或进程内存界。

2. **建议澄清入口检查的精确范围。**
   算法第 1 步的“全部字符串/bytes 的长度”可能被实现为额外递归预扫描，而现 K 只计入口、group/comparison 遍历和四次相等检查。额外全结构遍历没有明确费用来源。建议明确：第 1 步仅执行顶层 exact 类型、tuple/批数及 payload/digest/profile 的常数长度检查；深层字段检查交由原 replay／付费 `_walk` 完成。若确实新增递归扫描，应列出其收费并修订成本界。实施时不能把未计费预扫描隐藏在 guard 中。

3. **静态见证算式与固定调用次数吻合。**
   compile 的常量重复 parse、evaluate 中 subject/predicate/object 的 parse 次数、`term_key → check_value` 编码及两份 source40000 group 输出均已逐项核对。`291430 > 262144` 可证明旧逐组方案的 input 下界阻断；`182041` input／`82902` output 只证明原批次字节未触顶。文档没有将其冒充原 evaluate 已运行成功，实际 witness 的 work/trace 和新 API 通过仍待未来授权测试。

4. **额外输入要求明确但尚未获证。**
   完整原 matches（包括 false matches、原 bindings 顺序和 proof occurrence）是所选重放设计的新前置，不能由保存 true firings 推断已有。文档正确要求 I05 明确真实载体、生命周期及恢复预算；缺失时必须停止该复核方案。该选择减少新算法及旧源码变更，但不是证明“所有可能接口中数据需求最少”。

5. **发行与完整性边界合理。**
   fresh compile 不接受调用方 plan/seal；保存比较值仍须由当前同模块 `parse_value` 实际发行。canonical 完整字节相等后再检查全部发行身份，可拒绝字段伪造、自算 digest、跨模块及未经当前发行的恢复值。整批最后才成功，没有局部发布。它仍不能发现调用方提供了另一份内部一致、却并非原输入的 matches，也不证明图成员、匹配穷尽或 producer 授权；文档已明确这些限制。

6. **隔离、兼容与验证计划满足本轮准备范围。**
   新预算有独立版本，旧 PROFILE／budget 身份和单组 API 保留。仅提议三个新产品路径，原 20 路径逐项保持；测试计划覆盖后项损坏、共享 source、空/false 批次、全部 heads/proofs、发行篡改及各池原子失败。没有新 matcher、第二 oracle 或公共接口扩权。

实际静态校验：6 个 manifest 对象及冻结 ZIP `f16fbcca…`／20674 B 的对应成员一致；原 20 路径的固定 Git、工作区字节及绑定 SHA 全部相等。未重跑旧机制或矩阵。I05 表示前置、真实运行、独立候选测试及原父验收门均未完成。
