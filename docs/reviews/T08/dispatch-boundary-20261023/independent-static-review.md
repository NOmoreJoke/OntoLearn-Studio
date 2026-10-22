# T08 本轮独立静态增量复核

来源：现有独立 agent `/root/t08_internal_review` 对当前 WIP 的最终回复；owner按原回复归档，非指定模型外审。该agent没有写文件或运行验证。

> 当前增量静态复核通过，未发现新的具体缺陷。

- 固定字段 tuple 覆盖完整上下文，保留选择顺序；属性插入顺序不影响 key。
- 旧异步回调捕获原 key，函数式合并最新状态，不会覆盖 B 的输入或后来编辑的 A 输入。
- 同 key 同步防重入；取消入口检查上下文，但未被 busy 锁死。
- AgentSession 紧邻端口调用复验及 authority 错误净化保持有效。

实际读取的 SHA-256：

| 文件                           | SHA-256                                                            |
| ------------------------------ | ------------------------------------------------------------------ |
| agent-service.ts               | `15fa3d3f5eaab97ea4e5ad14cdeb9b8067b62c601db8bdb974aa4eb401cec3c3` |
| AgentSidebar.tsx               | `7b31550aafada0c0f3e2848fdfbcbe8a9b6a9a6ad2d3889acef394936120c98d` |
| sidebar-presentation.ts        | `af60f73edc09266e30bebf9cc02875bd40ba6fa4eef4a5c420c2b7fafba3e90a` |
| t08-review-regressions.test.ts | `61d2a5b6909635c1585a9cf18ca3e5a1a0a74cdecc9ae031401684fe828442b0` |
| t08-sidebar.test.ts            | `9bb19e9aade9959b3a44437b233881f5be2fa61071b8b8996762ec448caa695e` |

状态隔离限于同一挂载实例；测试仍是纯状态与 SSR 证据。未运行验证或写文件，原 P2-6、指定 NotPass 与真实 DOM 验收保持开放。
