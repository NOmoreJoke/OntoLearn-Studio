# T06 私有行为计划接口 v1

依据 PRD V0.6 FR-600–604、附录 C、E.1/E.2、G.3。代码位于 `packages/engine/src/ontolearn_engine/behavior/`；所有值为脱离存储的输入副本，本模块无 Store、SQLite、worker、IPC、shell、HTTP、通知发送入口，不声明公共契约已批准。

## 调用与完整样例

`prepare_events(request) -> PreparedRound` 按 `(sequence, id)` 应用全部事件；重复 ID、相同内容是 no-op，ID 相同内容不同拒绝整批。事件 fingerprint 包含类型、版本、载荷和 edits；输入序号是投递次序，不参与内容身份。副本状态只含稳定对象 ID、显式事实和内部通知记录；属性 schema 明确单值覆盖、多值追加、literal/relation/class，值比较保留 JSON 类型差异。

`PreparedRound.reasoning_input` 返回 binding、事件后断言内容摘要、本体/规则版本及状态。批准推理服务必须基于这份事件后状态重新计算；`plan_behaviors(prepared, reasoning)` 校验全部绑定和 current 状态后冻结断言与推导的并集。手填 binding 不能证明推理发生，本线的派生输入均为手工预期；B-04 特设反向敏感性测试，重新标记旧事实会产生错误探测通知。

完整请求、人工推导输入、完整事件后/冻结/候选状态、完整条件决定集合、动作轨迹及失败预期见 `tests/fixtures/behavior/counterexamples.json`。私有基线版本 `PRD-V0.6-private-1`，作者脚本 `build_corpus.py` 不导入被测实现。不覆盖 T09 的公共 G.0 基线；这些反例不能计为真实完整轮次通过。

```sh
uv run --frozen pytest packages/engine/tests/test_behavior_planner.py -q
npm run check
```

行为包含唯一 ID、名称、说明、效果、版本、启用状态、整数优先级、触发条件、一组条件与有序动作。条件组为合取：显式 `always` 或 `has(subject, property, value)`。未记录的事实仅记为条件不满足，不解释成开放世界下已证明不存在。表达式只允许常量、`event_field`、`event_id`、`instance_id`；没有求值代码或通用路径执行。创建、单值 set、多值 add、内部 notify 是全部动作种类；无删除动作或本轮递归事件入口。

## 排序、竞争和失败

触发实例显式按 **优先级降序、行为 ID 升序、事件输入序号升序、事件 ID 升序**；实例内动作按列表序号。事件的输入排序不覆盖行为优先级。先评估所有条件，再收集所有动作意图，再检查不同实例任意动作间单值不同值冲突，再产生候选。实例内顺序覆盖允许，但其任一写入与其他实例不同值仍拒绝。

同值单值写入及相同多值追加保持状态幂等；每个实例的通知等其他动作都保留，轨迹标明 changed/unchanged。条件、完整排序、动作序号、事件关联和输入/推导版本均记录。冲突异常包含完整决定、意图、冲突对及空执行轨迹，无 candidate。异常不会返回部分状态；输入/原消费记录不变。资源阶段和事件阶段不参与行为阶段竞争检查。

每轮动作上限 1000，按实际触发实例动作数计，包括同值写入。所有输入必须为有限 JSON 值，未知字段、缺条件、重复行为 ID、静态无效对象/属性、不可用动作、缺事件载荷字段、单多值操作不匹配均拒绝。动态对象/载荷在实例解析时复验。动作仅可引用初始工作区或同实例之前创建的对象，不能依赖其他实例改变被冻结的条件。

## 事务、消费与隔离边界

请求 `scope={project_id, scenario_id, mode}`，mode 只允许 sample/scenario，拒绝 formal；这是适配器还须核验真实来源的标记，不是权限证明。`consumption={scope, events, instances}` 必须绑定完全相同 scope；events 记录 ID/fingerprint，instances 记录 event/behavior 对。成功计划只返回新消费候选，须与完整轮次的快照同事务保存。失败或取消不能保存消费候选。重放从初始空消费开始，显式续跑读取所选快照的原消费记录。

输出始终 `kind=behavior_plan, committed=false`，含 base_revision、run/round、binding、输入/行为/推导版本、before/after_events/frozen/candidate、事件和条件/动作轨迹、完整 Diff 及消费候选。正式事务拥有者必须重新校验 base/operation/job、隔离运行身份与取消状态，结合资源、轮末推理和指标后调用唯一 Store 的轮次提交；本模块不发布 current、不推进项目 revision、不写正式事实，不能单独将计划记为成功轮次。

## 依赖交接和资源预约需求

- **T01 / I04**：批准的隔离 run/round 快照读取与原子提交接口，必须携带 projectId、scenarioId、runId、round、baseRevision、operationId、jobId、inputSnapshotRef、取消令牌；同事务保存完整候选/消费/逐步轨迹，失败前轮不变，提交后响应丢失以持久 marker 对账。请明确负责适配的唯一新路径；本线不改 `storage.py`、`job_store.py`、coordinator/worker。
- **T05 / I05**：批准的行为前推理入口，输入为事件后断言快照与本体/规则/执行语义/依赖版本，输出完整推导事实、规则依据、输入身份和 current/stale 状态；B-03 新增、B-04 删除依据必须真实重推。需批准的 RDF 词法/IRI ↔ 私有工作区的无损适配规则；目前 JSON 标量并非附录 C 的完整 RDF literal 编解码器。
- **T00**：接收上述成功及失败样例，批准行为验证/样本运行的业务方法、受限错误映射、分页/轨迹与取消边界，再由公共文件唯一维护者接线。私有 `BehaviorError` 及内部证据不可直接转发 renderer/Agent。
- **T09**：只读交付正式 G-base/G-behavior/E.5 的真实 fixture 路径、基线版本、完整事实/定义/输入/预期和重置入口/哈希。本线仅维护 behavior 私有反例，不写公共 fixture。
- **T07**：行为计划作为 E.2 第 4 阶段输入；本线不实现资源队列。B-07/完整轮末提交及资源产能归 T07 联验，行为产生事件若由批准模型表达，只能由轮次拥有者排到下一轮，不能重入本计划。
- **T08**：B-08 用真实失败接入 Agent；必须显示未成功，不得以本线抛异常的单测代替实际 Agent 结果。
- **总控外审预约**：纯服务内审与本地检查成熟后，请提供本精确工作树的 ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh 独立新任务资源/隔离时段及集成排队位置。本线不抢用 I05 审查应用，不在用户桌面运行 Electron/native/HMR，不在指定双方明确通过之前 push。

## 失败解释补充

私有错误保留安全结构化的 `reason/location` 文本；`evidence` 是内部诊断数据，不能当公共错误参数或模型外发白名单。失败记录分清 `event_preparation`、`definition_validation`、`condition_evaluation`、`intent_limit`、`intent_validation`、`conflict_check`、`candidate_simulation`，包含可确定的 event/behavior/condition/action/edit 序号。

条件或动作解析失败时保留已经完成的决定/意图前缀；未完成的条件只列 partial_decision，不伪造其他未评估实例的结果。局部候选模拟失败的先前动作标为 discarded_actions，事件准备失败的先前编辑标为 discarded_event_edits；始终 committed=false，无 candidate 或新 consumption。executed_actions 表示正式执行，行为计划失败时始终为空，不能将本地已丢弃模拟当成正式动作成功。绑定、输入/推导版本和 scope 附在已有合法运行身份的计划阶段错误中。

新增失败反例见 `packages/engine/tests/test_behavior_failures.py`，包括前序编辑后失败、事件身份冲突、部分条件、动态动作失效、跨实例创建碰撞、同值动作超限、静态/模板定位和不可编码 Unicode。成功计划结构与 E.1 排序/冻结/竞争规则保持既有定义。
