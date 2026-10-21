【candidate2 全面独立只读审查报告】
结论：当前完整oracle准备暂不通过；有三项P2需关闭，均为输入上下文/来源精确性。已核的有限RDFS、完整规则集合、40条显式匹配/head与其余阶段/reset未发现新的结论错误。可据固定candidate2解冻集中修复，再只复核实质delta；不需要重跑机制或产品。

固定输入：fixture745621B/SHA3980cfff9cbf45c9d3e069b1124e903b8ea0ea886fbbf99e1dbc512b9652eeef；doc15889B/SHA460b00d241d8076612b45d8a6b19e27bef58e35ae4d73dc402fffa2695191b8e；candidate-2-inputs.json1899B/SHAcbdd5dd881bf721ccfc27d0aa8f107e11baac396d8afe7f0bd22d2858112ef50；ZIP91439B/SHA27e99f7e183d4c6385946eff54d605aa3c7bf67b361a2c6780954721aaa180b4。10受审文件与ZIP原成员/manifest逐bytes/hash匹配，另含ZIP自身manifest共11成员，testzip正常；复核末次仍一致。

P2/R1：G13无依据选择编辑001。
精确位置：fixture /productCases/33/phases/3（phaseId=deviceB-edit）→/graphs/imported-deviceB-edit（该graph起10481行）；assemble-explicit-oracle.py:343。原cases /cases/33/steps/3只给edit-and-undo及name=设备B编辑，没有subject。当前中间图将001名称替换为该值。可复现反例不需运行引擎：完全符合原操作的实现可编辑002并undo，最终仍恢复imported全集，却会被此中间001图错误拒绝。必要修法：删去此未固定中间目标/图作为该case预期，标明selected subject及完整中间缓冲未提供；保留整个操作结束undo恢复imported的精确集合及非图验收。不要替换为空图。实际candidate2的importedSubcases.M06已经manual-same-name/imported，并未借DeviceB名称，无须回退；相应未知目标便利图/term若无获批用途建议移除以免未来遍历误用。

P2/R2：内容相同的baseline复用未绑定本例真实来源。
精确位置：/graphs/map-empty/ruleDefinitionRefs（图起9505行）及各map/imported图；/ruleDefinitions/R-risk/base/inputRef指向G-base.json/rules/0。assemble:70–84、137–145、166–177及映射G调用。实际主case baseline是G-map-empty；同字节ontology/R-risk不是来自G-base的项目快照。R06复用R05的R-next/新增类也需显式同值输入别名，不能仅以等值掩盖本例输入来源。
必要修法：保持字典内容去重可以，但补graph/case实际有效baseline/规则/ontology来源绑定，或明确的等字节alias并核G-map-empty实际pointer（R06同理核本例定义）。MAP=[B[0],B[1],B[2],B[3]]这类映射产物还应说明由哪个CSV行/固定mapping规则显式推导，不能把G-base中相同N3 occurrence当CSV来源；这里不是要求伪造原Turtle/source或producer权限。结构checker当前只验ruleRef存在/定义与所指来源相等，不能证明该来源适用于当前case，应补相应引用/alias一致性结构门。

P2/R3：已有精确操作编码，三元组未保留可核来源pointer。
精确位置：/triples/t0118（4858行，Q02 A01 Closed）、t0119（4871行，用户名称）、t0120（4888行，手工名称）等inputOccurrences=[]，只写authored文字；assemble:154–164、175及输入更新T调用。原sourceSteps中已提供真实subject/predicate/object或明确记录，整体case hash虽已绑定，仍不能逐term核对这些输入动作。必要修法：为实际提供编码的操作补对应sourceId/hash/具体pointer或authored-from-input refs，且checker逐项校验token；例如Q02 /cases/42/setup/0、A01 /cases/0/steps/1、M04 /cases/37/steps/1、M06 /cases/39/steps/2。用于补修的project/subject上下文必须来自原输入，不能把R1未知subject也补造为来源。rawImportToken=null/unavailable仍保持，其含义是导入前Turtle未知；本问题是已提供JSON/N3操作来源，不应以raw unavailable覆盖。

【已完成的实质审查与正面依据】
- 全文读推导、组装脚本、checker与源关系，实际核所有graph类别/阶段表、显式匹配及输入。组装只用pathlib/hashlib/json；AST无expected/actual/expectedRuleOutputs/expectedFirings取值访问；没有RDF库、固定点/闭包、通用when join、operator求值或队列调度。显式正告警tuple、18格真值、completed-ID表由作者列出，order_set只是按该表渲染已定status；不是第二reasoner。未运行组装脚本。
- 自行只运行 python3 docs/reviews/T05/real-executor-oracle/structure-check.py，真实exit0，输出passed-structural-only，50/54/22/106/250/93/40/1及20旧路径未变。此为结构一致性，不是产品/语义执行，不能自动发现以上上下文错误。
- 21处原case终态facts/assertedFacts与新oracle精确解引用集合逐项相等；E5 cap3/4八个commit完整事实集合也相等；22扩展完整custom集与原固定预期逐项相等。这只是交叉核对，未把原expected用来生成新oracle。
- 手工复核R-risk所有同alarm合取：A01、A04、A06、P001、transfer及AE001–016；不同告警没有拼接。R03双alarm中间图保留两匹配同结论，最终仅A04依据；未把中间数学预期说成实际infer。R04唯一type沿subclass的层1witness，公理/直接前提/叶集合及cases实际两个pointer正确；P001 rule basis展开到CriticalPump断言+公理，无其他RDFS公理可触发。G-behavior P range literal不能产literal-subject。无规则反馈/末轮RDFS，R05/06 R-next零匹配与warning保留。
- 18 integer比较真值、false when匹配仍列但零head、multi的两个原head index、disabled/missing/join零匹配均对应输入；不将22格称为全九域/全六numeric验收。未引入否定/跨alarm/NeedsInspection二阶产物。
- E5每cap四轮事件/条件冻结/行为/资源/提交图：未来事件未提前注入；工单完成不闭环告警；所有到达alarm匹配逐个保留。同结果未吞依据。G1 cap3/4各两独立重放、G2单reset、G6两独立cap3加round2续3/4，消费历史分开；非图状态/真实回放仍待原验收。
- 50主case原setup/steps106条完整引用，R02/03 stale与重算、V01坏样本/修复、B04先prime后删再探测、B05/09回滚、B06冻结条件、B10/11完整动作、M03手工note不撤回、G3/G9/G11/G13嵌套reset均未用旧结果冒充当前。R06独立重建已启用两规则再比两保存序列。G5未知晚载荷未猜；ontology-model仅四增量投影、learning-report无固定图不造空图成功；transfer-repair无规则不借ruleVersion继承R-risk，全辅助阴性不洗独立成功。这些有意边界合理。

【失败历史】initial ZIP6成员可读，SHA4b88437d61efaa45b41037fbcdc394483cc6fa149892934dac7bf4807a533e70；attempt1确为系统Python zip(strict)兼容失败。initial fixture757655B/d5e43e…与当前原字节不同，但全JSON递归差异0；组装脚本原字节相同。可说“预期JSON值未改”，不能说原fixture bytes未改/整版仅checker变（文档也有边界补充）。当前失败/原件未被覆盖，历史保全方向正确。

整体：数学结果/全部匹配与阶段方案大体成立，但本授权要求精确输入ref/hash与不逆造上下文，R1–R3修后再闭环。未写文件、未读未批源码、未调用产品/被测reasoner/matcher或GUI；未生成另一份oracle。后续仍仅独立预期准备，E1、生产来源认证、Store/Job/worker、平台、指定双审/CI/合并和完整父验收保持未通过。
