# OntoLearn 验证规范（Verification 2.0）

> 本文件是 OntoLearn 仓内现行的 Verification 2.0 规范。规范于 2026-11-17 基于 Anthropic《How the Claude Code team thinks about verification》升级，适用于本地开发验证、真实运行验收与候选提交。

## 1. 确定性命令（廉价检查先行：agent 只判断 exit 0 与真实断言）

```bash
cd .worktrees/<your-worktree>
# Step 1: 廉价检查先行（必过，否则禁推 CI 或发起复核）
npm run check                  # lint / prettier / typecheck / vitest / build / ruff / pytest
npm run verify:sources         # 涉及归档资料或 docs/source-manifest.json 时必跑

# Step 2: 聚焦单测 / 属性测试
npx vitest run tests/unit/<target>.test.ts
uv run --package ontlearn-engine pytest packages/engine/tests/<target>.py

# Step 3: 真实 Electron E2E（与 MiniMax GUI 共享 Desktop Focus Mutex；Linux 用 xvfb-run -a）
npm run test:e2e -- tests/e2e/<target>.spec.ts

# Step 4: 打包及包内验证（涉及主进程/依赖/打包配置时必跑）
npm run package:dir
```

## 2. 三类防愚弄测试策略（Anti-Gaming Tests）

1. **真实运行 E2E + Feature Map 量表**：
   - 桌面/界面/恢复改动必须跑真实 Electron E2E，对照 `docs/verification/FEATURE-MAP.md` 执行；
   - 严禁用隐藏窗口、禁用 hang monitor 或 stub 原生弹窗冒充真实原生验收。
2. **属性测试（Property-based Testing）**：
   - `packages/contracts`（zod schema 边界编解码）优先使用 **`fast-check`**；
   - `packages/engine`（`Store.commit` 原子性与幂等性、RDFLib 从不可变快照重建、`format3.py` 往返解析、`invalidation-v2.json` 失效原因映射）优先使用 **`Hypothesis`**；
   - 重点覆盖四类性质：**往返守恒（Round-trip）**、**不变量（Invariants）**、**幂等性（Idempotency）**、**等价性（Equivalence）**。
3. **差分测试（Differential Testing）**：
   - 契约升级（如 v1→v2）、schema 迁移或引擎算子重构时，以旧版本或黄金快照为 Oracle 同输入比对，归一化无关字段并对合法差异建立显式白名单。

## 3. Diff 触发式历史故障防回归清单

自检与送审前，依据 `git diff --name-only <base>...HEAD` 命中以下路径时必须跑通对应检查：

| Diff 触碰路径 / 特征                                                              | 必触发专项检查                                                                                     | 关联历史事故 / PR                              |
| :-------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------- | :--------------------------------------------- |
| `apps/desktop/src/main/**`、原生崩溃恢复、`electron-builder.yml`                  | 核对包内 `require('electron')` 主进程就绪时序，跑 Linux/macOS 包内原生恢复探针                     | Q3 / CI70 / CI71 原生恢复时序故障              |
| `scripts/review-level*`、`tests/unit/review-level*`、`.github/review-policy.json` | 在**空 diff、分离 HEAD 与隔离 `GIT_*` 环境变量**下跑单测，并比对 `origin/develop` 可信基线脚本输出 | Wave 0 (`G0`) PR #25 → PR #26 空 diff 测试失败 |
| `packages/engine/src/ontolearn_engine/storage.py`、项目开库/切换生命周期          | 检查旧预览异步回调复活（stale preview resurrection）、开库 ABA 竞态与退出屏障                      | Wave 1a (`B1a`) 内部独审 ABA / 旧预览复活      |
| `apps/desktop/src/preload/**`、`apps/desktop/src/csp.ts`                          | 核对命名桥 `PERMISSION_DENIED` 拒绝边界与生产 meta / 开发 header 零 `unsafe-inline`/`unsafe-eval`  | I02 / B1a E2E 桥接与 CSP 门禁                  |

## 4. 运行与提交铁律

1. **证明单元写在 Goal**：绿 = 真实命令 exit 0 + 日志/制品绑定精确 `base/head/tree`，不是「我觉得过了」。
2. **本地自愈 3 轮熔断**：同一测试/构建失败本地连续修复 **3 轮**未果立即停机保存现场交总控升舱或汇报，严禁死循环盲改。
3. **Flaky 测试零容忍**：严禁删 SSR/图/业务断言、加 `sleep`、调大 timeout 或加 `skip`/刷重试；3 轮内找不到根因则移除/隔离该测试并写入 `weeds.md`。
4. **Commit 验证戳记**：Commit Message 尾部或 `result.json` 必须携带 `Verified: <check|verify:sources|e2e|packaged|property|diff|none (reason)>`。
5. **裁判隔离**：分级脚本与审查标准从 `origin/develop` 可信基线读取；审查意见强制标 `[Important]` / `[Nit]` / `[Pre-existing]`。
6. **Feature Map**：功能入口与 Reviewer B 评分量表见 `docs/verification/FEATURE-MAP.md`（其中 **`L1`** 垂直学习底座由 `tests/unit/learning-workspace.test.ts`、`packages/engine/tests/test_l1_learning_ledger.py`、`tests/e2e/l1-learning-vertical.spec.ts` 与 `scripts/run-l1-packaged-learning.py` 驱动，覆盖离线四级降级与 `FR-004` 引导阶段唯一检查点闭环）。
