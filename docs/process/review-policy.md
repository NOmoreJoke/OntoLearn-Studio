# 代码审查分级政策（Review Tiering）

> 生效：2026-10-28 用户授权。适用于此后新建的候选；已冻结审查中的候选（含 T02/PR16）按原门禁收口，不改写其输入。
> 机器规则：[`.github/review-policy.json`](../../.github/review-policy.json)；计算工具：`npm run review:level -- [base] [head]`。

本政策只调整**模型审查的强度与触发条件**；本地检查、完整 CI（Quality/macOS/Windows）、远端合并核验、真实运行证据、FR 原条款结算和发布 HOLD 均不变。

## 1. 等级

| 等级        | 审查方式                                                                                          | 合并前置                             |
| ----------- | ------------------------------------------------------------------------------------------------- | ------------------------------------ |
| **L0 自动** | 无模型审查                                                                                        | 本地适用检查 + 完整 CI 成功          |
| **L1 单审** | 一名指定模型，非开发执行方（见 §4），审 diff，核心清单                                            | L0 前置 + 单审通过且意见处置闭合     |
| **L2 双审** | 两名指定模型**分工**：A 正确性/安全/数据完整性；B 验收覆盖/测试/真实运行证据。核心清单 + 领域模块 | L0 前置 + 双审通过且全部意见处置闭合 |

PR 等级取所有变更文件的最高等级。L0 内容应拆成独立 PR，避免被产品 PR 抬高等级。

## 2. 什么需要双审（L2）

- 主进程、preload、IPC bridge、CSP、窗口生命周期：`apps/desktop/src/main/**`、`apps/desktop/src/preload/**`
- 公共契约：`packages/contracts/**`
- 引擎核心（存储、事务、快照/撤销、任务、失效、语义推理、SHACL、查询执行）：`packages/engine/src/**`
- 打包与构建：`electron-builder.yml`、`electron.vite.config.ts`、`scripts/build-engine.mjs`
- 门禁与证据校验：`.github/workflows/**`（完整 CI workflow）、`scripts/ci-quality-schedule.py`、`scripts/run-engine-tests.py`、`scripts/verify-*`、`scripts/i04_matrix_evidence.py`、`docs/source-manifest.json`
- 需求原文 `docs/prd/**`（同时需要用户授权）
- 关键依赖（electron、electron-builder、typescript、vite、react 等）**大版本**变化；运行时依赖新增、移除或大版本变化；运行时依赖 spec 无法可靠解析（区间、浮动 tag、URL 等）时保守按 L2
- Python 依赖与包配置清单（`pyproject.toml`、`packages/engine/pyproject.toml`）任何变化，保守按 L2
- 本政策自身（`.github/review-policy.json`、`docs/process/review-policy.md`、`docs/process/review-checklist.md`、`scripts/review-level*`、`tests/unit/review-level*.test.ts`）
- **FR 结算 PR**（声称某 FR 完成）与发布候选：无论路径一律 L2，在 PR 标题或描述中标明 `FR结算`

## 3. 单审（L1）与免审（L0）

**L1**：渲染层 `apps/desktop/src/renderer/**`（不改 IPC/契约）；测试 `tests/**`、`packages/engine/tests/**`；`docs/architecture/**`、`docs/iterations/**`；示例资源 `resources/**`；其余 `scripts/**`；AGENTS.md、SECURITY.md、licenses；关键依赖次/补丁版本；开发依赖大/次版本；`package.json` 非依赖字段（scripts 等）；锁文件单独变化；未匹配任何规则的文件。

**L0**：`docs/reviews/**`、`docs/verification*`、`docs/README.md`、`docs/m0-checklist.md`、`docs/development.md`、`README.md`、`CONTRIBUTING.md`、`design/**`；非关键开发依赖补丁版本；随清单一起变化的锁文件；仓库外 `iteration-control/**` 的计划、交接、状态、回执（由总控确认，不再外部预审）；纯格式化/换行/拼写修复（工具仍按路径计算，必要时由总控在 PR 中注明后按 L0 处理）。

> 改动 AGENTS.md 或本政策以**降低**门禁时，除审查外还需要用户明确授权。

## 4. 流程规则

1. **先 CI 后审查。** 本地适用检查及完整 CI 全部成功后才发起 L1/L2 审查；CI 失败不消耗审查资源。
2. **复审只在受审补丁变化时触发。** 基线变化后先运行：

   ```bash
   git range-diff <旧base>..<旧head> <新base>..<新head>
   git diff --name-only <旧base>..<新base>
   ```

   同时满足以下三个条件才可豁免 fresh 复审（只需重跑完整 CI）：① 全部显示为 `=`（补丁未变）；② rebase 无冲突；③ `git diff --name-only <旧base>..<新base>` 未对本 PR 触碰文件路径或直接依赖的契约（`packages/contracts/**`）/引擎公开接口产生破坏性变更。有变化、有冲突或基线破坏性变更命中：**只审变化部分/冲突解决部分/受影响部分**；落在 L2 路径时按 L2 审。

3. **轮次上限 2。** 第 2 轮只审修复 diff 与对应意见。第 2 轮仍未通过时由**总控裁决**（接受并记录剩余风险 / 要求定向修复 / 退回重新设计）；只有涉及范围缩减、门禁例外、HOLD 解除或付费时才升级给用户。
4. **单审人选：** L1 由**非开发执行方**的指定模型担任，避免自审。当前开发执行方为 ZCode（`GLM-5.3`），L1 默认由 MiniMax（`MiniMax-M3.1-Flash`）担任；开发方为 MiniMax 或 GPT（Codex）时由 ZCode（`GLM-5.3`，最高推理档）担任。L2 仍为两名指定模型。模型标识统一使用可核对的规范口径（如 `GLM-5.3`、`MiniMax-M3.1-Flash`、`GPT (Codex)`）。
5. **清单按路径加载。** 原 160 项清单已拆分到 [`review-checklist.md`](review-checklist.md)：核心必审项 37 条（每次 L1/L2 必查）+ 领域模块 M1–M6 共 84 条（按 diff 路径加载，不适用模块不审）+ 本地优先单机默认不适用项 39 条及重激活条件（整组跳过，严禁为满足清单扩建 SaaS/登录/计费功能）。审查员先给出适用性判断；适用但未实检的写"无法确认"；先列最值得修的 Top N（不足 10 项不凑数）；禁止审查员修改被审业务代码。该清单与政策同受 L2 保护（见 `.github/review-policy.json` 第一条规则）。
6. **机械核对交给脚本。** base/head/tree 绑定、文件字节/SHA、manifest 一致性不再由审查员手工逐项核对。运行 `npm run review:level -- <base> <head> --json`，脚本输出 `baseSha`/`headSha`/`mergeBase`/`baseTree`/`headTree` 与 `mechanical`（含每个变更文件的 `status`/`bytes`/`sha256` 摘要，以及 `docs/source-manifest.json` 逐条 blob SHA-256 校验的 `sourceManifest.ok`/`checkedCount`/`mismatches`）；`mechanical.ok !== true` 时脚本以非 0 状态码退出。审查员只看结论与异常，并将该 JSON 附在 PR/证据中。
7. **PR 规模。** 目标单 PR ≤ 约 400 行有效变更或 30 个文件；FR 按"契约 → 实现 → 页面接线 → E2E"拆分，最终的 FR 结算 PR 做一次 L2 汇总审查。
8. **总控接收改为检查表**：等级正确、审查完成、意见闭合、CI 成功、range-diff 一致。不再对审查报告做第三层实质审查。
9. **审查不常驻 worktree。** 审查员只读固定 SHA，用 `git worktree add --detach` 临时检出，审查结束即移除，或直接在 PR diff 上审。

## 5. 使用工具

```bash
npm run review:level                      # 默认 origin/develop...HEAD
npm run review:level -- origin/develop feature/x
npm run review:level -- origin/develop HEAD --json
```

工具只计算建议等级。FR 结算、发布候选等**语义升级**判定由 owner/总控在 PR 中标注，以更高者为准；**纯格式化/换行/拼写**按 §3 的 L0 口径处理（须由总控核实并在 PR 说明），不适用"以更高者为准"。

策略合入 `develop` 后，CI 与总控脚本以**可信基线**为下限：工具从 git 对象同时读取 merge-base 与 head 的 `.github/review-policy.json`，按 `max(basePolicy, headPolicy)` 计算等级（基线为 `origin/develop`）；策略文件被删除、改写或降级均无法降低等级，且 `scripts/review-level-core.mjs` 内置不可通过 JSON 覆盖的 L2 硬底线（策略与清单文档、分级脚本及其测试、CI workflow、门禁与证据校验脚本、`packages/contracts/**`、`docs/prd/**` 等）。
