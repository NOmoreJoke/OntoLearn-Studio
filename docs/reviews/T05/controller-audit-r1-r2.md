# T05 总控独立输入审计 R1/R2 处理

来源：`iteration-control/2026-10-21-weekly-release/T05-controller-fr505-input-audit.md`，原报告SHA `3e9cf934899fd51ee746defebb69dd025257d4ffa790e3d8f1e05552e0439672`。已全文读回；旧报告固定16例及不充分覆盖结论保留，未将其改写为新版本通过。

## R1：算子误实现不能被原两点区分

已将fixture升级为 `T05-FR505-extension/2`，保留原12例，新增6格；现在每算子均覆盖同型score=1、2、3相对阈值2。

| 算子 | score=1 | score=2 | score=3 | 本次补格     |
| ---- | ------- | ------- | ------- | ------------ |
| eq   | false   | true    | false   | score3=false |
| ne   | true    | false   | true    | score3=true  |
| lt   | true    | false   | false   | score3=false |
| le   | true    | true    | false   | score1=true  |
| gt   | false   | false   | true    | score1=false |
| ge   | false   | true    | true    | score3=true  |

六真值签名各不相同，任意两个算子替换至少有一格可区分。新增各例具有完整输入/唯一规则/完整自定义输出预期及共同依据，均保持pending，没有actual。测试另用标量参考算术核对18格oracle；不进行图变量绑定/规则执行，不构造产品结果。

## R2：“小整数闭合P0”文案歧义

已删除该句，改为“同型整数仅作代表回归；完整FR-505及Q6支持矩阵、解释、错误、类型/取值范围和生命周期须另行实际验收”。禁止将实现限为这些小整数、仅一种类型或以22例代替完整原验收。

提案也明确bindings为私有输入表达，正式trace要经owner唯一格式规范化；单规则plan正反序不能证明多规则顺序，原R-04/05/06及V/O生命周期保持独立实际门。

## 当前处理证据

修复后本线quality定向148项通过（包含oracle结构/数学/可辨识性）；新完整check和完整独立内审结果另录 `verification.md` / `internal-review.md`。这份处理记录不替代root对新固定输入的独立复核，也不关闭公共接口、执行器或父功能验收。

## 总控固定读回关闭及恢复来源

总控随后实际全文读固定fff的独立报告 `T05-controller-fr505-r1-r2-readback.md`，SHA256 `a09694b55e7ba7c8f1f99d71fdd1af77f5d30431a00b8628123d11c3e72278f0`，明确R1/R2在输入范围关闭；本线已全文读回，不改旧审计/旧product提交。原两raw、fff四源hash、官方本聊天历史命令终态和Git恢复bundle见`fr505-r1-r2-recovery.json`及其归档，未用后续scope/UI日志替代原来源。

原raw没有开跑source hash；现保留这一限制。已通过官方read_thread实际读到原定向命令终态exit0/148与原全check终态exit0/635TS1200Py；Git源身份属于事后固定绑定，不伪造当时已有fff提交或开跑清单。归档已在空bare临时仓库获取批准5f后恢复bundle及fff四源字节；没有重跑不变产品。
