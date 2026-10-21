# T01 私有服务与共享接口交接请求

基线：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。这是实现接口需求，不是批准共享改动。独占范围和状态见 [status](../../reviews/T01/status.md)。

## 已批准接口及复用方式

- `storage.py:Store.commit` 是唯一正式 writer；私有预览调用同一方法后回滚，不保存另一份可变权威。
- `marker`、前后快照和 `load_snapshot` 提供审计/补偿依据。新撤销/恢复推进正式 revision 与依赖版本，保留旧操作、运行和快照，不回拨计数。
- `JobStore.prepare_plan` 已有真实提交回滚预览、受信 actor/write 及 confirmationRef；正式接线复用该服务，不能把私有 `confirmed_preview` 摘要当成人类授权。`create_job/commit_job/operation_get` 管正式任务与全局 operation claim。
- 私有 `ProjectTransactions` 使用内部 project ID；不能把公开 UUID 与内部 ID 混用。T00 适配器必须经 `_project(public)` 绑定身份，不直接公开此 Python 类。

## 精确缺口与建议交接

1. `packages/engine/src/ontolearn_engine/storage.py`：需要单次 `Store.commit` 可表达的受信补偿计划（原始来源必须为同项目不可变快照和指定目标 operation），恢复被删的已编辑手工事实原 ID；映射人工值/墓碑及 owner/source_row/managed_value 原样保留。反例：内容 ID 为初始值 A，编辑为 B 后删除；普通 manual 重插 B 会因 ID 与内容不符被拒绝。不可绕过 `_fact` 普通新增校验。
2. 同文件 `mapping_state`：首次 mapping 的撤销不能用空 rows 表示，因为会留下 generatedVersion；恢复旧映射状态需定义在新计数下“当前/已过期”的正确语义。建议补偿计划记录 target snapshot，但版本继续递增；不能直接复制旧 generatedVersion 冒充当前。全量 restore 保留已提交历史、模型凭据边界与结果失效。
3. `marker` 仅单 operation；T00 需要正式分页 `operation.list(project, afterRevision)`，用于恢复确认展示后续操作。私有预验仅对既有 commits 表只读查询完整清单，不注册协议。列表和恢复提交须在同 base 下绑定，否则重新预览。
4. 项目 schema/迁移：FR-002 的 name/template/archive、FR-004 checkpoint 节点索引、FR-005 模式、工作台草稿与学习进度没有正式持久模型。请求明确逐文件交接 `storage.py`/新迁移唯一责任后实施。建议项目元数据/草稿 revision CAS 仍在同 SQLite，且写入经 Store.commit；不塞入 ontology/model 定义造成假领域依赖。归档不删除，删除必须独立确认，复制须新身份并保留来源和历史。
5. `packages/contracts/src/{index,v2}.ts`、`packages/contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json`、`coordinator.py`、`worker.py`、`apps/desktop/src/main/{index,task-service,engine}.ts`、`preload/index.ts`、`renderer/src/{App.tsx,env.d.ts,style.css}`：由当前唯一负责人逐文件交接。需要项目生命周期、checkpoint/restore/undo、draft CAS、cache 全库范围确认和真实 ChangeSet 预览/确认入口；共享注册前不标能力可用。
6. `Store.collect_cache` 是全库维护，已有 JobStore pin_report/cache 协调；请求 T00 保留明确全库确认、先 pin 后报告、Agent 不可调用。历史快照/逐轮状态不清理；只回收未 pin 且非 current 的可重建载荷。

## 成功与失败的固定交接样例

- preview(base=7) 返回同项目基线、真实完整 before/after Diff、planHash 与预览身份；确认到达时 revision=8 → REVISION_CONFLICT，零正式写入。
- commit 后响应丢失 → 状态待对账，先隔离旧 writer，读取同 operation/job/plan marker；存在原 marker 则返回原 revision/前后快照，不生成新 operation、不盲重发。
- undo(op-A) 只补偿 A 触及记录；无关后续 B 保留；同记录已改或引用失效 → 冲突清单/拒绝，零部分提交。
- restore(snapshot-S) 单独确认，展示 S 之后全部 operation；确认摘要及 base 任一变化均重预览。不能恢复全部来源时明确拒绝，不能降格为只恢复可见事实。
- 旧结果刷新只更新 result slot；编辑草稿内容、base、generation 不变；旧 generation 保存或接受提交回调均拒绝覆盖新编辑。

## 资源请求

请总控给出上述共享接口的实际唯一负责人及安全交接窗口，并预约同一最终候选的 ZCode GLM-5.3/最高、MiniMax Code M3.1-Flash/xhigh 新任务双审。T01 不占用 I05 当前审查应用、不操作本机桌面。独立内审和真实 Store 反例继续推进；阶段提交不 push，正式接线/父功能验收和完整发布门继续本会话。
