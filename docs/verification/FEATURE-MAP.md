# OntoLearn Feature Map（最小 · 查询工作台）

> pstack「手眼与地图」落地骨架。禁止每票重建世界：命令以本文件 + `VERIFY.md` 为准。  
> 维护：T04 相关变更后更新本表；日更优先改「驱动方式」列。

| Feature             | 用户怎么到              | 驱动/证明                                                        | 陷阱                              |
| ------------------- | ----------------------- | ---------------------------------------------------------------- | --------------------------------- |
| 查询工作台打开      | 桌面 app → 查询页       | `npm run check`；E2E `tests/e2e/t04-query-workspace.spec.ts`     | 勿改 Store/contracts 冒充接线     |
| 空结果说明（Q1+Q2） | 空 SELECT / Closed 后空 | 已合 develop；回归勿回滚                                         | 空成功 vs 验证空                  |
| 同快照图（Q3）      | 结果面板图区            | 单测 `t04-result-graph.test.ts`；E2E `t04-query-variants` 图增量 | 勿整文件盖 Panel；禁删 SSR/图断言 |
| 保存→重开           | 保存查询定义后重开      | E2E 保存重开链                                                   | 恢复旧结果 ≠ 新 Job               |
| CSP/窗口生命周期    | 启动/崩溃恢复           | `csp-lifecycle` / native-driver（历史证伪，非本轮门）            | 勿绑进 Q3 门禁                    |

**禁重建世界**：不要为单票另写 Playwright 脚手架；复用仓库现有 e2e 与 `npm run check`。
