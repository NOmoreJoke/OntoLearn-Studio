# OntoLearn 验证驱动说明（最小）

## 确定性命令（agent 只判断结果）

```bash
cd OntoLearn-Studio   # 或当前 worktree
npm run check         # 静态总门
# 图批聚焦（Q3）
npx vitest run tests/unit/t04-result-graph.test.ts
# 适用 E2E（配置已有单 worker / 零 retry；勿改 timeout）
npm run test:e2e -- tests/e2e/t04-query-variants.spec.ts
# 需要全链时再跑
npm run test:e2e -- tests/e2e/t04-query-workspace.spec.ts
```

## 规则

1. 证明单元写在 Goal；绿=真实命令 exit 0，不是「我觉得过了」
2. 失败保留日志路径与可复现断言
3. 禁止删 SSR/图断言换绿
4. Feature Map：`docs/verification/FEATURE-MAP.md`
5. 推送/CI/merge 另票；本机优先（私有 Actions 慎用）
