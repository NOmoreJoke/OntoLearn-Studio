# directSteps 兼容性修复预算 delta 独审

结论：固定 `8e8b5126c69534c6259d37b2d3e88f75ef935aa0` 的本次预算兼容delta通过，未发现新增阻断。此前BUD-01/02/03的实质关闭保持；本报告不将cb上的全量check失败改记通过，也不代根的新全量check终态。

## 固定范围与保全

树仍为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-directsteps`，base5f、adoption78e9原值不变。完整读cb2662→8e8b512的两源码diff：仅 `semantic_execution.py` 与 `semantic_profile_production.py`，17增/5删。根 `candidate-final.json` 的141项逐current=8e8Git=bytes/SHA，133只读=adoption；旧测试与新增42828B测试均未改。

此前 `write-lock-final.json` 封存的92件逐项hash核同；初189报告、cb预算报告、首失败、格式127与绝对Node追加通过均原样保留。新审只追加本prefix的 `compat-*` 脚本、`delta-8e8b512-*` 运行与本报告/补充锁，没有源或测试写入。

## 费用与调用时序

原 `before_projection(self)` 签名恢复，内部原C stage6、hash/普通投影预票不变。新增 `before_explanation_projection(self,native,source,rules)` 仅在exact capture的direct_ledger非None分支调用；其D enter、三个原生界遍历和3-pass整流预票是原实现块的原样移动。执行顺序仍为D预票→原C预票→唯一真实projection→原三hash，未把D费用后移到实际委托之后。

独立 `delta-8e8b512-01-hooks-and-fees` 运行真实depth2 producer，observer均调用保存的原方法，不供应结果、费用或hash。实际观察为：

| 实际节点             |  D work | C stage/hash         |
| -------------------- | ------: | -------------------- |
| 新D hook前           |  856145 | stage5               |
| 新D hook后           | 5739281 | stage5               |
| 原hook前             | 5739281 | stage5               |
| 原hook后             | 5739281 | stage6，hash33554543 |
| 唯一实际native投影前 | 5739281 | stage6，hash33554543 |

随后原三个stage6 hash delegate实际输入长度1140/46/2，三者hash票均33554543，已大于4×8388608原固定预票。投影后的carrier计数字节仍先付自身遍历，真实B仍779。该成功producer的**完整D事件链逐tuple等于此前固定ff90092成功原件**，usage/peaks与原动作一致；不是只比最终几个counter或按公式重建事件。

旧facade仅增加十个固定None槽与finally assert，调用共同operation时未传direct_ledger，不会进入新增D hook。没有按物料规模新增遍历/复制；共同operation仍拥有并清理真实对象。真实旧错误trace现在可见同名空槽，未通过放宽旧断言、删旧test或改旧C fee求绿。

## 必要验证

`delta-8e8b512-02-boundaries` 独立实际 **22 passed/76 deselected，1.23秒**：五旧C域required exact/差1及原hash monkeypatch共六项，新D producer/restore/roots四域共十二项，四个尾故障项。旧五域错误trace的十slot逐None、无异常context与原hash委托前预票均按原测试真实通过；D边界和尾故障没有只靠成功路径推断。

`delta-8e8b512-03-static` 实际核141来源、133只读、两源码实际delta与此前92件封存hash，exit0。三次运行均固定8e8b512、独占basetemp、完整clean env/argv/cwd/起止/exit/timeout、141 before/after相同；双流、真实费用事件和结束成员hash分别保存。没有因新delta重跑未变化的全部消费者/原始数学样例。

cb完整check曾有6 failed/4958 passed/44 skipped，这是根运行的已知失败而非本审通过；重复check有界终止亦不记通过。本审只确认相关六个旧兼容案例在新候选真实通过及D费用链未漂移。根的新完整check、十二源核验和来源审报告仍各按实际终态收件，不能由本报告代替。

本次不改 `_direct_stream`/3343J strict-reader预票、B计数、索引、DP、固定caps、原R opaque、版本或其他writer；原cb报告的详细算式、方法/循环覆盖及容量边界继续按精确相同源码适用。仍不承诺最大图容量、CPU/RSS改善、T/S/H租约、正式来源/Job/Store/selected/Σ或父模块/上线完成。完成本报告格式检查及追加写锁后停止写入。
