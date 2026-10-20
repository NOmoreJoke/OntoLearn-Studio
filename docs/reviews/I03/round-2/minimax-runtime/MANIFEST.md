# I03 候选5 round-2 / M3.1-Flash 自建探针工件清单

审查者：MiniMax Code（MiniMax-M3.1-Flash）。本目录只放摘要、退出码、差异 JSON 与探针源码副本；完整用例语料与原始 stdout/stderr 保留在本机 `/tmp/i03-r2-minimax/`。

## 批次与计数（可从保留工件重算）

| 批次 | 输入 | 输出 | 退出码 | 计数结论 |
| --- | --- | --- | --- | --- |
| 1 | `probe/cases.json`（25742 条生成 + 77 条夹具分节） | `probe/results-ts.json`、`probe/results-py.json`、`probe/divergences.json` | 0 | 比较 25819 例，语义分歧 0，双端抛异常 0 |
| 2 | `probe/cases2.json`（游标/任务列表游标/响应/路由的逐字段变异） | `probe/results-ts2.json`、`probe/results-py2.json`、`probe/divergences2.json` | 0 | 比较 3948 例，分歧 24（全部为 Python 抛异常 vs TS 返回 false，见报告 R2-F1） |
| 3 | `probe/cases3.json`（seed=20261020 随机模糊，66 个 `$defs` × 400） | `probe/results-ts3.json`、`probe/results-py3.json`、`probe/divergences3.json` | 0 | 比较 26400 例，分歧 0，双端抛异常 0 |
| 5 | `packages/contracts/v2/errors.json` + `schema.json` | `logs/batch5-contract.*` | 1 | 34 项断言，33 PASS；唯一 FAIL 为探针构造缺陷（MAPPING_VALUE_INVALID 缺 4 个必填兄弟字段），已在 batch5b 更正 |
| 5b | 同上 + 完整兄弟参数 | `logs/batch5b-ts.*`、`logs/batch5b-py.*` | 0 | TS 53/53 枚举值被接受、未知值 53/53 拒绝、跨码误用 0；Python 同值 |
| 6c | I05 交接三件 + `I05-semantic-boundaries.md` + 公共目录 | `logs/batch6c-i05.*` | 0 | 24 项断言全部 PASS（v3 25 码集合与顺序一致、5 个退休码仅存历史表、SHAPE_PATH_UNCLASSIFIED 仅 INTERNAL_ERROR、公共目录零 I05 内部码） |
| 7 | `packages/engine/src/ontolearn_engine/storage.py` | `logs/batch7-s1.*` | 0 | 31 项断言全部 PASS（kind 守卫零写入、空白 kind 不 trim 不归并、legacy NULL kind 开库拒绝零清理、legacy 非对象 config ValueError 零副作用） |
| 8b | registry/schema/states/invalidation-v2 | `logs/batch8b-structure.*` | 0 | 17 项断言全部 PASS（14 线方法 ↔ registry ↔ schema 零错配、staleReason 8 码 == S1、状态笛卡尔积一致、无新增场景/摘要业务方法） |
| F3 | `candidate-copy/`（HEAD 导出隔离副本） | `logs/f3-*.stdout.txt`、`logs/f3-*.stderr.txt`、`logs/f3-*.exit.txt` | 0/2 | 基线 0；contracts 源注入 2（TS2322）；单测注入 2（TS2322）；desktop 对照注入 2（TS2322）；三次恢复后均 0，字节 SHA-256 与原值一致 |

累计比较量：25819 + 3948 + 26400 = **56167 例**，语义分歧 **24 例**（单一类别，见报告 §6 R2-F1）。

## 复算方式

1. `node probe/gen-cases.mjs`（在 `/tmp/i03-r2-minimax/probe/` 下）重建批次 1 输入；批次 2、3 同理（`gen-cases2.mjs` / `gen-cases3.mjs`，批次 3 使用固定种子 20261020，结果确定）。
2. TS 侧：`node --import ./register.mjs run-ts.mjs`（`hooks.mjs`/`register.mjs` 为 Node ESM loader，解析仓库真实 `packages/contracts/src/v2.ts` 与 JSON 导入）。
3. Python 侧：`uv run --frozen python run-py.py`（加载仓库真实 `packages/contracts/python/contract_v2.py`）。
4. 比对：`node compare.mjs` / `compare2.mjs`，差异写入 `divergences*.json`。
5. 批次 5/6/7/8 为直接断言脚本，退出码即结论。

## 保留工件的 SHA-256

- `probe/cases.json` a877964d7028a3664e534467ac29a232a1a3c215a57dba2e6b4483f3842e47f1
- `probe/cases2.json` ac688ca325e216c6bcee1a3a064c160c8a9367efdc250001c792a3de61d89194
- `probe/cases3.json` edce734209a294ea84071adb16eaeacc62e0b04a840b1c882ff1bddbcb4bd19c
- `probe/divergences.json` 804a39c774db238aa997279e7d03e871f3601e859355623560cecc547d72b15d
- `probe/divergences2.json` 18ebfc97d60520394030f6e815183281cd35093fdb2b8e312ffa134e6c064b85
- `probe/divergences3.json` efc3e6276fcb7a19e8d7024ae27eb1a656ac078f56bb2b58c55f14e248d2cbc1
- `probe/results-ts.json` daa4ab05bce46a9bbddbcb15e64ad045ef0b5537be21428495ca6836d6b299e4
- `probe/results-py.json` 82d45fc8593ca6a1d709b97530176b47009eabc11405668a6fdda5c8bd581157
- `probe/results-ts2.json` 2f3fbf28a34398467a418cfcf2bfabc0b8f0a5cfc4e8f839b79d0767797c8b8c
- `probe/results-py2.json` 555b766725f03c7c718e3d8f3e4d0c68b33f12765c10b14a86d0d0d5bb7837b8
- `probe/results-ts3.json` c0009fe2344ad8039937d150acaba7857b0b1ea9f1969e0181021b33e03b7591
- `probe/results-py3.json` a3d3582dd8ae99cfbc4e41fd306466bfa5afe9039bab33592090b4dda9e94453

## 命令退出码（原始记录见 `logs/*.exit.txt`）

| 命令 | 退出码 | 运行位置 |
| --- | --- | --- |
| `npm run typecheck` | 0 | 被审 worktree |
| `npm test` | 0（424/424） | 被审 worktree 与副本 |
| `npm run engine:check` | 0（626/626，ruff 119 文件） | 被审 worktree |
| `npm run verify:sources` | 0（12 个归档源） | 被审 worktree |
| `npm run lint` | 0 | 被审 worktree 与副本 |
| `npm run format:check` | 0（**不含** `docs/reviews`，该目录在 `.prettierignore` 中） | 被审 worktree 与副本 |
| `npm run check`（含 build） | 0 | 副本 `/tmp/i03-r2-minimax/candidate-copy`（共享 build/out 由另一任务独占时） |
| `npm run check`（含 build，**共享资源释放后的原位补验**） | 0 | **受审 worktree 本身**；stdout `logs/worktree-recheck-full-check.stdout.txt`（105 行）、stderr `logs/worktree-recheck-full-check.stderr.txt`（0 字节）、exit `logs/worktree-recheck-full-check.exit.txt`（0） |
| `git diff --check`（排除 `docs/reviews/I03/**/*.diff`） | 0 | 被审 worktree |

## 副本（candidate-copy）的依赖边界 —— 更正

派发方指出副本**并非完全独立依赖环境**，实测确认：

- `candidate-copy/node_modules/` 为真实目录，但其下**各包与 `.bin` 均为指回受审 worktree `node_modules/` 的符号链接**（`typescript`、`vitest`、`vite`、`electron-vite`、`zod`、`eslint` 等 317 项 + `.bin`）。
- **本地真实目录**：`node_modules/@ontolearn/{contracts,desktop}` 指向副本自身 `packages/`、`apps/`（工作区源码解析为副本自身）；`apps/desktop/out`（构建产物）；`node_modules/.vite`（vitest 缓存）；`.venv`（uv 现场创建、装 14 包）。
- 副本构建期间在被审 worktree 的 `node_modules/.vite-temp` 留下**一个空目录**（0 项内容，`.gitignore` 覆盖），**未写入任何包内容**。

结论：副本 = **源码与产物隔离、依赖包与工具链共享**。副本内取得的 exit 0 / 424 / 626 / 注入 exit 2 + TS2322 事实**全部按原样保留**，其证据强度依赖"同一编译器 + 同一依赖集合 + 候选源码逐字一致"；共享 build/out 释放后已在**受审 worktree 原位**补跑标准 `npm run check`（exit 0）以消除该依赖。

`ruff format --check` 计数差异（副本 119 / worktree 123）：worktree 含候选开发线自己的 **git-ignored** `build/I03-validation/` 脚本（4 个 `.py`），副本为 `git archive` 导出不含该目录。**仅影响计数，不影响任何检查结论**。

## 候选哈希复核（补验后）

- `git rev-parse HEAD` = `30c10d8ad1b9156b1fa5317c6b41b179f927c761`，补验前后一致。
- `git diff --stat base head` = 101 files changed, 26214 insertions(+), 11 deletions(-)，与补验前一致。
- `docs/reviews/I03/candidate.json` 记录的 **101 份候选文件**逐份重算 SHA-256：**100/101 一致、0 缺失**；唯一不一致为 `docs/reviews/I03/status.md`（流程追加小节「候选5第二轮实际创建（仅流程追加）」），**不含契约/实现/测试/依赖/验收内容**。

## 报告原字节与 diff

- `report-before-worktree-recheck.md` —— 补充前原字节，SHA-256 `f1d1446684026c2d68aafbcc4737fa5b19ba4a3b6f0a0d352563d771117782ad`（229 行）。
- `report-worktree-recheck.diff` —— 补充写入的完整 unified diff（76 行，raw 逐字保留空上下文前缀空格）。

