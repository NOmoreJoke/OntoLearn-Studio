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

| Diff 触碰路径 / 特征                                                                                                                                                            | 必触发专项检查                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 关联历史事故 / PR                                                                                  |
| :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------- |
| `apps/desktop/src/main/**`、原生崩溃恢复、`electron-builder.yml`                                                                                                                | 核对包内 `require('electron')` 主进程就绪时序，跑 Linux/macOS 包内原生恢复探针                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Q3 / CI70 / CI71 原生恢复时序故障                                                                  |
| `scripts/review-level*`、`tests/unit/review-level*`、`.github/review-policy.json`                                                                                               | 在**空 diff、分离 HEAD 与隔离 `GIT_*` 环境变量**下跑单测，并比对 `origin/develop` 可信基线脚本输出                                                                                                                                                                                                                                                                                                                                                                                                                                 | Wave 0 (`G0`) PR #25 → PR #26 空 diff 测试失败                                                     |
| `packages/engine/src/storage.py`、项目开库/切换生命周期                                                                                                                         | 检查旧预览异步回调复活（stale preview resurrection）、开库 ABA 竞态与退出屏障                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Wave 1a (`B1a`) 内部独审 ABA / 旧预览复活                                                          |
| `apps/desktop/src/preload/**`、`apps/desktop/src/csp.ts`                                                                                                                        | 核对命名桥 `PERMISSION_DENIED` 拒绝边界与生产 meta / 开发 header 零 `unsafe-inline`/`unsafe-eval`                                                                                                                                                                                                                                                                                                                                                                                                                                  | I02 / B1a E2E 桥接与 CSP 门禁                                                                      |
| `apps/desktop/src/main/model-gateway/**`                                                                                                                                        | `npx vitest run tests/unit/w3b-pre-encoded-body.test.ts tests/unit/w3b-cross-slice-before-commit-and-loopback.test.ts`；核对核准字节、越界及 local 零外发、审计和凭据隔离；总控运行 W3b 包内第二例                                                                                                                                                                                                                                                                                                                                 | W3b S2-2 网关与授权接线                                                                            |
| `apps/desktop/src/main/agent/**`                                                                                                                                                | `npx vitest run tests/unit/w3b-agent-host-composition.test.ts tests/unit/w3b-agent-ipc.test.ts tests/unit/w3b-cross-slice-before-commit-and-loopback.test.ts`；核对旧回合撤销与正式提交前检查点；总控运行 W3b 可见 E2E 两例                                                                                                                                                                                                                                                                                                        | W3b S2-2/3 会话、工具端口及检查点                                                                  |
| `packages/engine/src/ontolearn_engine/project/ontology_{turtle,import}.py`                                                                                                      | `uv run --frozen python -m pytest packages/engine/tests/test_ontology_turtle.py packages/engine/tests/test_ontology_import_rejection.py`；总控运行 W3b 可见 E2E 第一例，核对拒绝零写入、完整 Diff 与导出往返                                                                                                                                                                                                                                                                                                                       | W3b S2-3 Turtle 能力边界与往返                                                                     |
| `packages/engine/src/ontolearn_engine/project/learning_agent.py`                                                                                                                | `uv run --frozen python -m pytest packages/engine/tests/test_agent_before_commit.py packages/engine/tests/test_w3a_quality_b3.py`；核对完整代做仅随关联 ChangeSet 提交落账、未指定尝试保持 independent 及 SQLite 重开持久一致                                                                                                                                                                                                                                                                                                      | W3b R2 B05 完整代做提前落账与波及无关尝试                                                          |
| `packages/engine/src/ontolearn_engine/{mapping,behavior,scenario,transfer}/**`、`project/learning_wave4.py`                                                                     | `uv run --frozen pytest packages/engine/tests/test_w4_*.py packages/engine/tests/test_l1_learning_ledger.py -q`。核对映射第二次零差异提交、取消及精确续跑、学习缺证和 FR-901。                                                                                                                                                                                                                                                                                                                                                     | W4 T03/T06/T07/T10 与课程落账                                                                      |
| W4 Main 暂存、检查点、Agent、四工作台或 E2E 文件队列                                                                                                                            | `npx vitest run tests/unit/w4-*.test.ts`；`npx tsc --noEmit -p tsconfig-b1a-e2e.json`；`python3 -m py_compile scripts/run-w4-packaged-workspaces.py`。核对真实 stdio、恢复后运行列表、受信命名桥与 CSP，文件队列只替代选取结果。                                                                                                                                                                                                                                                                                                   | W4 真实跨层回归与桌面准备                                                                          |
| `scripts/release/**`、`apps/desktop/electron-builder.yml`、`scripts/run-w5-packaged-release-hygiene.py` 或 `.gitignore`/`eslint.config.mjs`/`.prettierignore` 中 `release` 规则 | 核对 `git check-ignore` 对 `scripts/release/**` 与 `docs/release/**` 仍**可见**（exit 1 = 未忽略），且 `npx eslint --print-config scripts/release/verify.mts` 未被忽略（返回配置）；跑通 `npx vitest run tests/unit/t11-release*.test.ts`（**0 skipped**）、`bash -n scripts/release/collect-macos.sh`、`packages/engine/tests/test_w5_release_projection.py`、以及包内 `scripts/run-w5-packaged-release-hygiene.py`（含 `licenses/electron/*` 与 `forceCodeSigning: true` 等不变量）；核验 `package:dir` 不触发本地 Keychain 弹窗 | Wave 5 (`B5/T11`) `release/` 三重忽略盲区、Electron LICENSE 缺包与 `electron-builder` 签名目标隔离 |

W3b 可见桌面验证由总控在已获 Desktop Focus Mutex 的桌面运行 `npm run test:e2e -- tests/e2e/w3b-agent-and-b2.spec.ts`。打包后运行 `python3 scripts/run-w3b-packaged-agent.py <release> <output>`；Linux 在专用显示环境设置 `B1A_NATIVE_ISOLATED=1`。核对 `launch.json`、`summary.json` 中恰好两项通过与归属进程清理结果。

W4 可见桌面验证由总控在 Desktop Focus Mutex 下运行 `npm run test:e2e -- tests/e2e/w4-workspaces-and-transfer.spec.ts`。打包后运行 `python3 scripts/run-w4-packaged-workspaces.py <release> <output>`，Linux 使用专用显示环境并设置 `B1A_NATIVE_ISOLATED=1`。检查 `launch.json` 的可执行文件和 ASAR 指纹、`summary.json` 的唯一通过用例和进程清理、`report.json` 的无重试与跳过证据。

W4 文件队列经显式环境变量和隔离 profile 启用。该例验证可见窗口及选取后的正式暂存和发布链路。系统原生对话框与包内原生恢复由总控另行实测。

## 4. 运行与提交铁律

1. **证明单元写在 Goal**：绿 = 真实命令 exit 0 + 日志/制品绑定精确 `base/head/tree`，不是「我觉得过了」。
2. **本地自愈 3 轮熔断**：同一测试/构建失败本地连续修复 **3 轮**未果立即停机保存现场交总控升舱或汇报，严禁死循环盲改。
3. **Flaky 测试零容忍**：严禁删 SSR/图/业务断言、加 `sleep`、调大 timeout 或加 `skip`/刷重试；3 轮内找不到根因则移除/隔离该测试并写入 `weeds.md`。
4. **Commit 验证戳记**：Commit Message 尾部或 `result.json` 必须携带 `Verified: <check|verify:sources|e2e|packaged|property|diff|none (reason)>`。
5. **裁判隔离**：分级脚本与审查标准从 `origin/develop` 可信基线读取；审查意见强制标 `[Important]` / `[Nit]` / `[Pre-existing]`。
6. **Feature Map**：功能入口与 Reviewer B 评分量表见 `docs/verification/FEATURE-MAP.md`。
