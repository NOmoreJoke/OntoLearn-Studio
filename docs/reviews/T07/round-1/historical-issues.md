# 历史问题与处置索引（开发者整理）

原始独审终态见 internal-review-original-finals.jsonl，精确来源见 internal-review-sources.json。以下仅索引，历史通过限当时范围，不能预设本轮指定模型结论。

| 编号     | 触发/影响                                              | 修复与原始复核                                                                         |
| -------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| IR-01/P2 | V1历史运行展示V2当前来源、假设、产能                   | 运行独立evidence/identity；原始final第1、3条及后续复核                                 |
| IR-02/P2 | 第1轮快照接受提前消费第2轮事件，续跑漏事件             | 校验事件所属轮次/已提交消费；原始final第1、3条及后续复核                               |
| IR-03/P2 | 删除最高序号工单后复用历史ID，混淆轨迹/去重            | 历史创建身份/单调序号；原始final第1、3条及后续复核                                     |
| IR-04/P2 | 已有场景后无法再从基准项目创建                         | 显式来源选择，项目来源不传scenarioId；原始final第2、3条                                |
| IR-05/P2 | READONLY未触发时AssertionError被runner吞掉，产生假通过 | runner外断言OperationalError/SQLITE_READONLY码名，禁用注入负对照；原始final第7、8、9条 |

persistence-pytest-first.log的42项通过原件保留，其中READONLY证明已失效，不得追认。修复43项、交接样例44项是不同历史运行，按persistence-validation.json日志/hash分别阅读。最终完整check对应check-persistence-confirmed.log；ui-identity.log为空，不能独立证明退出码/成功。其他check-first、format-first、ruff-first等原始首错也全部封存，未删除/覆盖。

原始消息保留各次实际测试数与结论，不能把累计90项T07 Python/27TS拼成同一次独审运行。本次只包装原件和核哈希，没有重跑命令，没有补造独审原文。完整父领域、Job生命周期、App接线、完整E5与跨设备门仍未完成。
