# T11 原会话一次短继续准备

2026-10-22。总控要求准备原 Z/M 各一次正常短继续；本记录不是 GUI grant，尚未发送。等 T05 实际释放并由总控明确交接后执行；不重建任务、不重发已核完整的 321 行原输入、不改冻结源码、不启动新复审。

## 发送前最小核对

| 项目           | ZCode                                                                      | MiniMax Code                                                                 |
| -------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 原 session     | `session_31c8c641b36907791bdab363f7473a01`                                 | `mvs_52775b8f354f485a919e2c0e8ebe6bd2`                                       |
| 唯一 workspace | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-zcode-review-7d28fdb` | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-minimax-review-7d28fdb` |
| 实际会话设置   | GLM-5.3 / 最高 max / yolo                                                  | MiniMax-M3.1-Flash / xhigh / 始终授权                                        |
| 历史终态保留   | `turn.failed`；流 idle timeout，继而 TLS 建立前断开                        | assistant `stopReason=aborted`，原因未知                                     |

实际读回原会话身份、workspace、模型/思考/权限及当前任务状态；不拿用户默认配置替代。若已自行运行或出现最终报告，不盲发继续，先记录实际状态。两审查树仍为 review HEAD `b6e57a0534c94316dd07c3a87b4b8931d5a39501`、product `7d28fdb27c0aac39ed7df1f9fd5fa0f127b5d9f4`、base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。只核本方必要身份/漂移，不重复探索；原输入完整性已有原生逐行证据。

设置符合时，各原会话只发送下述短文本一次并记录真实新 turn/时间与发送回执；任何偏差准确登记，不重建或降级模型。发送后立即释放前台，后台推理不占 GUI。没有实际失败不预设强沙箱或中止原因；遇实际错误保留原件及明确现象，由总控判断下一步，不能用未知因果无限挂起。现有产品阶段票、SQLite 损坏 HOLD、原生/collector/API/签名/付费边界仍依完整输入；正常原检查和受控临时 SQLite/worker 不因泛称 child/SQLite 一律停用。

## Z 原会话短文本

```text
请继续本原会话尚未完成的 T11 只读审查。已完整收到的321行全文及末尾执行补充继续有效，无需重发；保留此前流超时/TLS断开及失败记录，不覆盖为通过。核实仍在 T11-zcode-review-7d28fdb、review HEAD b6e57a0534c94316dd07c3a87b4b8931d5a39501，模型 GLM-5.3/max/yolo。继续原 product 7d28fdb 的全部25路径、两collector、专项测试、原acceptance和历史失败/处置；必要时运行原授权普通检查与受控worker回归，无变化验证不机械重跑。遵守全文末尾现行执行边界，不扩大特定HOLD/native/产品API/付费票；不修改实现或读取另一审者本轮材料。最终在本根 .t11-review-runtime/report/review.md 输出完整覆盖、问题、验证证据、未验边界及明确通过/不通过/无法验证结论，不预设Pass；父发布门缺口照实保留。
```

## M 原会话短文本

```text
请继续本原会话尚未完成的 T11 只读审查。已完整收到的321行全文及末尾执行补充继续有效，无需重发；保留此前aborted终态，原因未知，不覆盖为通过。核实仍在 T11-minimax-review-7d28fdb、review HEAD b6e57a0534c94316dd07c3a87b4b8931d5a39501，模型 MiniMax-M3.1-Flash/xhigh/始终授权。继续原 product 7d28fdb 的全部25路径、两collector、专项测试、原acceptance和历史失败/处置；必要时运行原授权普通检查与受控worker回归，无变化验证不机械重跑。遵守全文末尾现行执行边界，不扩大特定HOLD/native/产品API/付费票；不修改实现或读取另一审者本轮材料。最终在本根 .t11-review-runtime/report/review.md 输出完整覆盖、问题、验证证据、未验边界及明确通过/不通过/无法验证结论，不预设Pass；父发布门缺口照实保留。
```

实际发送、任务设置、新终态及全文报告另留独立回执；本准备不推断恢复成功或审查通过。两个短文本只带本方失败背景，不互传另一方本轮发现。Q5 方案仍待用户答复，不默认采用或启动 benchmark。
