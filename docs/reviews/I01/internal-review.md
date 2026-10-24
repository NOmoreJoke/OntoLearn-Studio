# I01 独立 agent 复核处理记录

2026-10-20，独立只读 agent `/root/i01_internal_audit`，未修改共享文件。按 AGENTS 的复杂交付要求安排，不替代指定 GLM/MiniMax 门禁。

| 意见 | 处理及证据 |
| --- | --- |
| slot 混淆导致人工新增覆盖映射/不同多值误拒绝 | 采纳；显式 edits 按事实记录身份改值，manual仅新增；不同多值并存、单值声明冲突、受管漂移保留；专项回归通过 |
| 旧实现迟到覆盖新版当前指针 | 采纳；current_results 主键纳入完整实现来源；新旧实现迟到回归通过 |
| null重放配置仍标可重放 | 采纳；类型、最大轮次范围和实现来源逐项检查；不完整记录仅能查看，replayable=false |
| manual no-op错误推进事实版本 | 采纳；完全相同人工事实跳过写入/依赖推进；专项回归通过 |
| round空operation/job | 采纳；持久标记非空校验，与正式提交一致 |
| 只有快照Turtle建图，缺规范事实adapter证据 | 采纳；rdf_snapshot 从规范事实/ontology triples建图，墓碑过滤、人工编辑及旧输入保留回归；测量改用此adapter |
| RDF N3词法等价绕过共同事实所有权 | 采纳；要求规范term(value).n3()对象，xsd:string/语言标签统一后派生身份；三引号、转义及显式xsd:string跨映射/manual反例回归 |

最终只读复核明确：此前问题均关闭，未发现新增阻断；94项S1测试通过（2.93s）。这仅覆盖冻结前工作区；完整check、实际打包和第三方同版本审查分别记录。

## Round 2 独立只读复核

同一独立agent复核首轮修复时额外发现：受管事实删除后原值恢复，净零仍推进mapping版本。已采纳，改为比较事务前后owner记录、映射定义与sourceHash；净零不推进，真实sourceHash改变仍推进。空映射的已注册依赖接受、未知依赖拒绝均有反例。

最终独立复核明确通过，未发现新增阻断；独立专项149项通过（5.73s），未修改文件。完整check为160项Python（149项S1 + 11项协议）、4项TS；UI正式双审仍需两项新任务，不沿用首轮结论。

## Round 3 独立只读复核

内部agent确认保留ID冲突修复方向，并发现初版_project_snapshot只检查列表容器，facts=[None]仍replayable=True、definitions=[None]会裸TypeError。已采纳，补齐嵌套定义/JSON/显式引用、事实及ownership/RDF、mappingState/过期原因的基本存储形状；不复算合法edited记录初始ID。新增非法记录与合法edited/tombstone相反例。

最终只读复核明确通过：刚才缺口已关闭、历史不合格输入false、合法编辑和墓碑仍可用、所有权定位不误拒多值。独立专项187 passed（5.43s），未修改文件；不替代新候选双指定模型审查或最终集成打包。
