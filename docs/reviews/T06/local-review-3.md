# T06 失败解释候选完整本地独立审查

审查者 `/root/behavior_independent_review`。结论：**本轮完整性审查不通过**。核心算法及历史 P1/P2 未回归，新增错误定位有一项可复现 P2。

固定分支 `feature/weekly-t06-behavior`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，受审 HEAD `f3f652352a5814bee95a453f608f1dd2f2fc815a`；审查后 HEAD 未变，仅保护 AGENTS 有既有修改。

## P2：事件前置校验缺少阶段和源位置

原 `planner.py:307–317` 事件头/载荷校验未加上下文；原 325–335 行重复 ID 冲突无原始投递位置。

复现一：合法 E1 后追加 E2，令 E2.sequence=true，实际异常 `invalid_integer: event.sequence`，evidence 为空，无阶段、事件 ID、原始输入位置或 committed=false。payload/shape 失败同类。

复现二：同 ID、不同版本的第二次投递返回 event_preparation/event_id，却无原始位置或 sequence，难以定位重复项。

影响：输入仍正确拒绝且不变，但新增诊断完整性不足；不是新增业务规则。建议排序前保留 event_index，统一用于预校验、身份冲突、编辑失败；合法字段再附 event_id/sequence，错误文本继续安全结构常量；完整证据断言。

## 已核对

FR-600 定义唯一/实例/事件幂等及旧常量 create 五回归正常；FR-601 仅 create/set/add/notify，无外部入口；FR-602/E.1 冻结、全部意图竞争、四层排序、内部顺序、跨实例不同值及同值保留正常。FR-603 候选/轨迹/Diff 及旧完整冲突证据正常，唯上述事件定位不全。FR-604 失败路径未返回部分 candidate/consumption。

新条件/动作错误正确区分完成前缀与 partial_decision；discarded_actions 未当正式执行，异常文本无测试输入值，内部 evidence 明确不作公共参数。G.3 仍为手工推导反例，B-07/08 及完整轮次未冒充通过。

独立无缓存/无字节码行为测试 74 passed；5 个 Python 文件 ruff check/format 均通过。另用内存复现两种缺口。未运行全仓检查、未写文件或推送，未运行 GUI/Electron/e2e/native/HMR/CUA/指定审查应用。

未验证真实推理/RDF、Store 事务/回滚、资源、取消、公共接口、Agent/UI、完整 G.3、打包、远端 CI/生产。本报告不替代指定双模型。

## 开发处置（保留原不通过结论）

新增排序前 source index 与合法 sequence 的上下文；不修改原始 events 数组，单独排序带源位置的事件视图。补第二项 sequence/payload/shape/type/edits 错误、反序源数组中的编辑和重复 ID 冲突、非法 ID 元数据等 9 项精确回归。首次实现漏挂冲突分支的两个字段，测试真实失败 2/83 后修正；原件保留。修后 83 项通过，待新固定候选完整复核。
