# T01 项目与事务状态

## 启动回执（2026-10-21，北京时间）

- 会话：`01a15bba-0884-7401-b24f-f50c1fcf60aa`；已建立本功能独立 Goal。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`。
- 分支：`feature/weekly-t01-project-transactions`；base/head：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 实查 `git status --short` 仅 ` M AGENTS.md`；操作规则 SHA-256 为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。此文件保持未暂存。
- 已全文读启动文件、共同规则、controller-handoff/plan/review，读取 tasks.json 本项与需求/验收清单；已读 PRD FR-001–006/804、C/D/F/G.5/G.6 和批准 Store/JobStore 接口。
- 初始授权路径不存在，确认后创建；只新增 `packages/engine/src/ontolearn_engine/project/`、`packages/engine/tests/test_project_*.py`、`tests/unit/t01-*.test.ts`、`docs/reviews/T01/`、`docs/iterations/T01/`。现有共享文件、schema/迁移、worker/protocol/main/preload/UI/锁不写。

## 完整拆分与责任

| 工作 | 当前责任和依赖 | 下一可验交付 |
| --- | --- | --- |
| 私有确定性事务/Diff | 本会话；真实批准 Store.commit | 真实库预览、旧版本拒绝、失败零部分提交、响应丢失对账 |
| 单次撤销/快照 | 本会话；Store marker/前后快照 | 不覆盖无关后续编辑，冲突暂停；完整恢复接口缺口逐项交接 |
| 草稿/模式/刷新隔离 | 本会话私有纯服务；持久化待项目 schema 交接 | 草稿版本 CAS、结果刷新不覆盖草稿、模式切换不动正式数据 |
| 项目元数据/创建打开复制归档 | Store API 已有身份/备份；元数据迁移责任未生效 | 精确 schema/API 需求，不用 JSON 第二权威 |
| 示例内容/学习进度 | T09 内容；本线接入 | 版本化离线模板和事务初始化接口协作 |
| 正式确认/任务/协议/UI | T00/I04/I06 逐文件交接；T08 Agent | 不将私有内部接口计作业务注册或完整产品通过 |
| 内审/外审/交付 | 独立只读 agent；指定双审需总控预约 | 本地可恢复提交、报告及精确候选 SHA；双审前不 push |

## 验收命令与限制

启动命令：`pwd`、`git status --short`、`git branch --show-current`、`git rev-parse HEAD`、`git worktree list`、`shasum -a 256 AGENTS.md`、`rg --files` 及只读 Store/JobStore/PRD 读取，均已执行。

计划执行：`uv run --frozen pytest packages/engine/tests/test_project_*.py`；`npm run check`；新增文档 `npx prettier --check`。每次实际命令、首跑失败和结果追加证据。测试必须比较完整持久状态、版本/marker/历史，而非仅数量。新增依赖/打包配置才触发包内验证；当前没有此类改动。

本机只运行无窗口静态/单测/构建，不运行 Electron/e2e/native/HMR，不操作审查应用或用户桌面。不输出密钥，不读取其他线未批准实现为依赖。

## 待交接与门禁

正在形成精确接口差距；schema 迁移、共享接线、ZCode GLM-5.3/最高和 MiniMax M3.1-Flash/xhigh 双审资源需总控落实。仅阻塞相应集成，不停止独立实现。当前尚无实现/运行通过、外审、push、PR、合并或父功能完成证据。

## 第一阶段实际推进

- 私有 `project/transactions.py` 已实现真实 Store.commit 的回滚预览、完整记录 Diff、版本/确认摘要检查、同 operation/job/plan 对账和受限补偿撤销/快照恢复；`project/workspace.py` 实现易失草稿 CAS、迟到保存回调拒绝、结果刷新隔离和 P0 模式。
- 专用验证 `uv run --frozen pytest packages/engine/tests/test_project_*.py -q` 第三次实际通过：57 passed。包含七个提交边界的异常/存储错误/取消，以及真实子进程 `os._exit` 后重开；失败比较完整 SQLite dump。缓存测试保留全部运行、快照、提交和来源。
- 首跑失败原件：`evidence/pytest-first.log`（引用夹具误用字符串）、`evidence/pytest-second.log`（失效码预期误写）；均已修正测试，未改 Store 原行为。Ruff 格式前行长报告也保留。原始日志被仓库通用 `*.log` 忽略，仅本地保留；摘要/hash 清单入库。
- `npm run check` 第一轮正在运行，已实际完成 lint/格式/typecheck、630 项 TS 和构建；Python 全套仍在运行，不能先计通过。
- 独立 agent `/root/store_interface_audit` 完成接口核验，报告见 [independent-interface-audit](independent-interface-audit.md)；同一 agent 正在只读审查第一阶段实际实现。另一个独立只读 agent 正复核下一阶段补偿/迁移设计，不共享写文件。

## storage.py 单文件交接生效

总控已明确通知生效，且已只读核验 `execution-state.json/storageOwnershipHandoff.status=effective`。交接文件 SHA 为 `f19cfd133c17f5b1848d3f26ff6fe6843ce63a11f37db431c0b61a355d6b9398`；T01 与 I05 均已实际接受，原 storage.py SHA 为 `4abf1082f1b864eb9efa155c7cbc890ef70cb196f30e09ad12629ce7a0cf6842`。

新增唯一维护范围仅 `packages/engine/src/ontolearn_engine/storage.py`，在本树/本分支内实现补偿、内部项目元数据/schema、草稿 CAS、operation.list。其他既有测试、JobStore/worker/protocol/资源/依赖/锁/CI 和 I06 14 文件均未移交，不修改。返还须先停写、保存精确状态并经总控登记，不能双树争写。T00 提案作为设计参考，不等于批准公共接口。下一阶段扩展仍只经 Store.commit，不放宽普通新增事实 ID 校验，不回拨版本、不删除历史。

尚无指定外审/push/PR/合并或正式业务接线证据；父功能和发布门保持开放。

## 第一阶段候选复核完成

两项内审 P2 已修复并独立关闭，详见 [stage-one-review](stage-one-review.md)。新专用测试 64 passed；新全仓 `npm run check` 退出码 0，lint/格式/typecheck、630 TS、构建、ruff、1116 Python 均通过。两轮完整检查各自原件保留，日志 hash/大小见 `evidence/stage-one-logs.json`。运行范围为本机无窗口单元/引擎测试及构建，没有桌面/native/e2e、打包或生产证据。

第一阶段准备本地恢复提交；不 push。后续继续同一 Goal 实现完整 Store 补偿和稳定操作列表，元数据/草稿格式升级等待明确版本协作，正式 JobStore/canonical/桌面接线仍待逐文件交接。
