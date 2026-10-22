# MiniMax S1 原件与意见处置

原报告 `minimax-m31flash.md` 25539B/SHA `1404505d57ec6310f1a0d62646f63441a03913afd895aaa5772c0166be1f90b5` 已全文读取并原字节归档。原session `mvs_a864253984c3453f982eeaa1cdfb43d8`、turn `04fe413a-9d81-433c-84ac-a16030e1f1aa` 的真正final stop、turn_completed、finished、DONE及外层stream-done齐全，正式GET为idle0。原结论是 **Pass with Conditions，2P2、4P3**，不是明确无阻断通过。两项P2保留，不沿用旧ZCode Pass推送。

## 可恢复证据与实际边界

evidence/minimax-original-tool-evidence-20261022.tar.gz 为629906B/SHA `c68ba2b7663b2533f87e729030e04e5292e7533cd503a90560ac32db001298bc`。父线已读取全部184个regular成员，与来源字节一致，其中182数据件均与包内manifest逐项长度/SHA匹配；另两件为manifest和SHA256SUMS。包括172次工具业务记录、99份自有后台输出、24最终探针和25初始版本、完整final/终态/连续流边界、实际派发与原冻结两版输入、真实model/permission读回。私有raw思考/系统/headers及内置persona完整返回不入Git包。

重要事实口径见 evidence/minimax-original-facts-and-differences-20261022.json，原报告不因owner核对而改写：

- 报告引用5096382b…是原冻结输入；实际唯一15831B派发正文为a795b582…。AGENTS78df是开始快照，现de15属于后续授权政策更新，12产品来源无漂移。
- 原check本身pipe tail -40，仅保留3135B尾部及CHECK_EXIT=0、1174 Python汇总；630 TS来自另一次npm test/VITEST_EXIT=0，不能说完整check stdout已保留。122专项也仅保留命令tail返回；运行时argv缺口不倒推。
- 50 initial性能输入为同一status=S1槽重复50次，并非50不同属性；346MB是开启tracemalloc时Python traced peak，10.7秒也在开启tracemalloc时测得，不是RSS或无跟踪生产时延。
- 原探针API/输入错误、首败和修正全部保留。probe15后半两次unhashable dict；probe16才提供修正的_put表。probe18先action_limit、改不匹配trigger才得到矩阵数据。probe22打印部分键/trace后KeyError，不能说整个脚本成功；probe23只有header，实际竞争失败证据来自24。probe13被主动取消，无已记录数字exit。
- 无pipefail的管道外壳exit0不能证明上游Python成功；原始完整命令、输出与失败链已保留，不用最后成功结果覆盖首败。
- 全部172个显式工具请求未见hook-state/.mimosa内容读取，只有目录元数据、本任务来源/T09固定Git、原12hash及自身settings等；这不能证明隐式hook上下文或memory绝对隔离，也没有据memory启用直接断言意见污染。

## 逐项处置

独立静态处置全文 `resource-remediation-independent-review-20261022.md`，方案 `resource-remediation-plan-20261022.md`。两P2仍开放：修复可避免的全对扫描、全事实序列化和逐动作全状态复制/比较；完整B×E输出成本另列，PRD Q5无数值阈值，不擅加配额/分页/删矩阵。源动作1000不是事实/字节容量限制，不能将initial遵守源动作计数误称绕过既定上限。

四P3按既有合同澄清：有序initial单值后写覆盖、create身份碰撞拒绝、成功源位置未在现合同承诺、diff为before→candidate。新增拒绝、幂等create、消费schema位置字段或分段Diff均不能借优化引入；尤其frozen含推导，不能把frozen→candidate误称行为删除。仅在后继候选补必要文字，原报告及旧候选不改写。

下一步在原独占路径形成保语义新候选，针对实际变化验证、完整独立审查，双方全新同版完整指定审查。未据本次原件封存关闭父FR、真实接线、资源/Agent、native两OS、包内/真人、CI或发布门。
