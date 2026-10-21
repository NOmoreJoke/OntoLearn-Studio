# T09 → T06 固定输入独立兼容性审计

审计者 `/root/baseline_compatibility_audit`。只读核验 T09 规则/PRD/JSON/manifest 与固定内容提交 `51cdc0e9d138c98cdd4ace865074a71883657a68` 字节一致；manifest SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`。T06 对照产品基准为 e81cfc9（审计中发现工作区已有改动，不把在制适配算作通过）。未导入 T09 Python、未执行推理、未改文件或 GUI。

结论：T09 输入可只读适配，旧 T06 不能直接消费。可在本线独占目录实现必要纯适配；真实推理/事务/轮次/Agent/UI仍等待批准。

主要差距：标准 RDF subject/predicate/object 与 JSON facts；源局部 ID（W:eventId 含冒号但并非外部绝对 IRI）；camelCase/整数版本/空合取；addFacts/removeAlarm；封闭模板；create-individual 的类型/属性初始化；显式通知 ID 及两条 RDF事实；0-based→1-based 轨迹；未提交计划与完整轮末 committed 状态区分。

不能把 B-risk 两个源动作拆成四个后压缩展示，否则 1000 上限和轨迹失真。应 native compound create，初始单值写入参与跨实例任意意图竞争；notify 同样一动作。消费保留原事件 ID；节点登记可含事件 IRI但不发明类型事实或行为动作。

单值仅按 singleValuedPredicates；不可将 name/level/status 全部自设单值。布尔严格解析 true/false，拒绝 bool("false") 或与整数混同；完整 RDF 政策留 T05。B-03 setup 和 B-04 事件删除 A01 的三条自身事实及入边，然后事件后重推；人工 expected 推导不算真实推理。

完整核对目标：B-01 25 条断言、仅 W:E-B01 与两动作，重投不变；B-02 22 条无工单且实际非高危原因；B-03 21 条含 A06 和关联工单；B-04 20 条、原两工单、无探测通知；B-05/09 原24条及空消费/通知/执行轨迹，准确冲突；B-06 26条、冻结 false、最终 true、一通知；B-10/11 各28条，两工单正确，两通知及四动作/消费顺序完整。数量仅辅助，必须比完整集合/顺序。

失败 decisions/intents 是计划证据，不得当持久触发消费。失败状态来自原快照；候选不等于真实回滚证明。

必须批准后才能闭合：T05 真实推理/codec；T01 同事务状态/消费/轨迹与取消/恢复；T07 E.2 六阶段/资源/指标/完整轮次；T00 公共方法/受限错误/分页/身份/权限；T08 实际工具失败表达。此报告不替代指定模型审查，不表示父 FR 完成。
