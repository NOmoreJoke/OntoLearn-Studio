# T06 首次本地独立只读审查

审查者：`/root/behavior_independent_review`。结论：**不通过**。此原始结论保留，不作为指定双模型审查。

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior`，分支 `feature/weekly-t06-behavior`，当时 HEAD/base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，实现未提交。全文读取 AGENTS、实现/测试/接口/状态及 PRD FR-600–604、E.1/E.2、G.3。

## 问题

1. **P1：静态创建检查破坏重复事件幂等，并阻断后续空轮次。** 原 `planner.py:452–455`（原调用在 520 行）早于触发筛选。常量 `create fixed-work` 首轮成功，将 candidate/consumption 用作下一轮，重投同事件抛 `duplicate_identity: definition.object`；无事件或禁用行为亦复现。违反 FR-600/603/E.1。建议只在实际触发实例检查已存在对象碰撞，补常量创建的重复、空轮次、不匹配、禁用及新事件再次碰撞回归。
2. **P2 缺测：冲突证据及非空 Diff 缺完整预期比较。** 原 `test_behavior_planner.py:85–114` 只核对第一冲突项事件 ID，Diff 仅核空结果；第二实例/动作序号/部分意图或差异错误可能漏检。未发现对应输出已经错误。建议固定 B-05/B-09 完整冲突对、全部意图和事件轨迹；创建/覆盖/多值/删除/通知的完整 added/removed。

## 已核对与边界

排序键完整、条件共享冻结快照、跨实例任意单值动作检查、同值保留其他通知、消费 scope、副本隔离、旧推导绑定、1000 动作限制均符合本次私有范围。文档区分人工推导和真实集成证据。

审查者运行 `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -p no:cacheprovider packages/engine/tests/test_behavior_planner.py -q`：53 passed；另用内存输入复现 P1。未修改文件或推送，未运行 GUI。

真实推理、Store 事务/回滚、资源、取消生命周期、Agent、公共方法、UI 及完整 G.3 无法由本次判定；未运行 Electron/e2e/native/HMR/审查应用。

## 开发处置（不改写上述原结论）

P1：静态 create 仅登记可供同实例引用的对象；实际 `_edit(create)` 保留碰撞拒绝。新增重复事件、空轮次、disabled、不匹配及新事件碰撞回归。

P2：私有 fixture 增加完整冲突对/意图与非空 Diff，测试逐项完整比较；另有多值 added/removed 精确反例。修复后私有测试 61 passed。修复候选须由审查者重新只读复核，之后再记录其真实结论。
