# T06 修复候选完整本地独立复核

审查者：`/root/behavior_independent_review`，新一轮完整只读任务。结论：**通过本次私有行为算法的完整本地只读复核**；原首版不通过保留。未发现新的实质缺陷。

- 分支：`feature/weekly-t06-behavior`
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 受审 HEAD：`4542c5521aa96e676ab000861a65394e525b1144`
- 全部 8 个新增文件与提交一致，仅 AGENTS 为已有改动。已重核 FR-600–604、E.1/E.2、G-behavior/G.3。

## 历史问题逐项关闭

1. **P1 关闭**：静态 create 仅登记后续可引用对象；实际触发实例仍经 `_edit(create)` 拒绝碰撞。新增 5 个回归覆盖重复事件、空轮次、禁用、事件不匹配及新事件再次碰撞。
2. **P2 关闭**：完整比较 B-05/B-09 的冲突对、全部意图及事件轨迹；成功反例完整 Diff 覆盖创建/覆盖/删除/通知；另有多值非空 Diff。预期来自私有人工场景及不导入被测实现的作者脚本。

全范围复核确认事件身份/消费 scope、冻结条件、四层排序键、跨实例任意单值动作竞争、同值保留其他动作、单/多值、异常与不可用动作、推导绑定、副本隔离、动作限额均与私有接口一致。

## 独立命令及结果

- `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -p no:cacheprovider packages/engine/tests/test_behavior_planner.py -q`：61 passed。
- 4 个受审 Python 文件 `ruff check --no-cache`：通过。
- 同范围 `ruff format --check --no-cache`：通过，4 files already formatted。

## 未验边界

真实推理、完整 RDF 编解码、Store 原子提交/回滚、资源、取消生命周期、公共接口、Agent、UI、完整 G.3 轮次和生产未验证。开发线须另提供新候选全仓检查。未写文件或推送，未运行 GUI/Electron/e2e/native/HMR/指定审查应用。

本次不替代 ZCode GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh 指定双方新任务审查，不表示完整 T06 验收。
