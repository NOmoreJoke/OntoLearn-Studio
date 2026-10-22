# T06-S1 固定输入适配 v1 与私有动作 v2

本轮唯一新增范围是补齐 T09 已发布输入的必要适配差距，不把数据候选当真实执行器。源数据由 T09 在 handoff 中明确开放只读，内容提交 `51cdc0e9d138c98cdd4ace865074a71883657a68`，manifest SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`。未复制或改写公共 fixture，未导入 T09 Python，未读取未批准 I05/I06 实现。

## 必要差距与实现

- 源 create-individual 同时指定类型/初始属性，是一个行为动作。私有 create 新增有序 initial 字段，作为一动作验证/计数/轨迹，所有初始单值写入仍加入跨实例竞争检查；不能拆成多个动作后再压缩轨迹。
- 固定工单 W:eventId 和通知 N:eventId:behaviorId 不用 hash 替换。封闭 event_template 只允许 eventId/behaviorId 占位，一次替换，不解释插入值或任意路径；notify 可带明确内部记录 ID。原默认 ID 保持可用。私有 semantics_version 进为 E.1-private-v2，PRD E.1 业务语义不变。
- RDF 事件追加可重复声明同一稳定节点。event-only declare 是幂等节点登记，不添加虚构类型，不计行为动作，行为定义禁止 declare。原 create 碰撞仍拒绝。
- 属性基数只来自 singleValuedPredicates；rdf:type、多值关系和非单值字面量追加保持集合语义。保留原 equipment→alarm 关系，不使用私有反例的简化反向关系。
- 固定 codec 只承诺当前数据使用的 IRI、字符串、true/false Boolean；拒绝未知类型、语言与会损失词法的信息，不冒充附录 C 完整 RDF codec。正式推理输入/编码由 T05 批准后接入。
- 动作中的属性值按已声明动作的原样 JSON 标量保留，不在动作编译阶段自动解释成 RDF literal 词法或执行通用 RDF 解码；不得把这一有限适配扩大为附录 C 的完整值语义。

## 只读输入与投影

baseline_adapter.load_bundle 读取调用者显式给定的源 root 和固定 manifest hash，核对 PRD及 manifest 所有文件，拒绝越出 root；解析已核验的同一份字节。Bundle 的 JSON 返回副本，不保存第二权威。

adapt_case 只编译零产能单轮固定 DSL，显式空 conditions 映射 always，缺失字段仍拒绝。输入序号取源事件数组顺序；原 case 版本和 manifest/adapter 版本随来源记录。addFacts 转成显式 edits；remove-alarm 仅按该明确指令删除告警自身事实和入边。既不计算规则，也不把 expected 当实际领域结果。

project_candidate 输出完整断言事实集合、工单、通知、1-based 源动作轨迹和消费集合；notify 的两条 RDF 陈述只投影一次逻辑通知动作。保持 committed=false，正式提交仍归 T01/T07。重投时需显式传入先前工单顺序，不凭本轮空轨迹猜测历史队列。

## 实际命令

```sh
uv run --frozen pytest packages/engine/tests/test_behavior_*.py -q
uv run --frozen python docs/iterations/T06/probe_t09_baselines.py \
  --source-root /Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines \
  --manifest-sha aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e \
  --output docs/reviews/T06/evidence/t09-candidate-probe.json
npm run check
```

九例 B-01/02/03/04/05/06/09/10/11 按完整事实/工单/通知/有序动作/消费/实例比较，不只核数量；B-01 真正重复调用计划器并核全状态/Diff 不变，B-04 拒绝旧绑定，B-05/09 比较完整冲突。推导事实是明确标注的人工 gold 输入，不能算真实推理或完整轮次验收。B-07 资源、B-08 Agent 及真实 Store/取消/UI 等继续待批准接线。

当前固定数据适配不是公共 IPC 契约或生产权限；不关闭父 FR。源 fixture 或代码变化须刷新输入哈希并重新运行相应验证和完整审查。
