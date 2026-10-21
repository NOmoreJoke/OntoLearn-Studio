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

## 第二阶段：完整域补偿和稳定操作列表

- 第一阶段恢复提交：`03376dfb873a67260fd6ef426c603f3ffbe3feb1`（本地，未 push）。
- 新增 `project/compensation.py`，Store.commit 的互斥 undo/restore selector，Store 内部完整行恢复和 `operation_list` 固定 throughRevision 分页。无新 schema/依赖，不改旧快照和 marker 字节。
- 九个真实提交边界（含删旧事实后重插前、映射计数重绑后）覆盖异常、取消、模拟磁盘失败及真实子进程退出，128 项专用先通过。该候选全仓 630 TS/1180 Python 通过，但后续内审发现遗漏，因此这份通过不计修正版验收。
- 独立全范围及定点内审发现保留 ID/墓碑占位漏检、隐藏 retirement 恢复遗漏，两项均已实施修复并新增反例；前者最终逐 active 事实复用原 `_check_slot`，后者通过完整不可变提交历史重建原退休成员（含已有补偿 selector），缺证据拒绝。版本 ledger 向前，vector 只投影真实当前成员，不显示已无成员的历史计数。恢复前已退休/未退休的映射分别实际重跑拒绝/成功对照。
- 修正版 T01/Store/JobStore `485 passed`；新全仓检查、两位独立复核正在进行，不能先记最终通过。所有首跑/修复日志原件保留；早期三项失败是旧“明确拒绝”预期转成真实恢复成功后的待更新测试，后续退休集/投影失败原件亦保留。
- T00 格式提案已全文读取并反馈，支持 DB3/完整 checkpoint/协议3 的明确协作。当前没有 metadata/draft/学习权威表，未伪报格式2兼容；这些仍待逐文件共同迁移/接线，不能算 FR-001–006 全部完成。

下一可验交付为第二阶段实际冻结 SHA、全部内审意见处置和全仓原件；成熟后请总控继续安排批准基线刷新、JobStore/canonical/桌面窄接口接线、指定双审资源，不等待整个 M0。

## 第二阶段最终内部验收

- 全范围独立复核通过，累计第一/第二阶段7项历史意见全部关闭，详见 [stage-two-review](stage-two-review.md)。最终 T01/Store/JobStore 496 passed；完整 `npm run check` 实际退出0，630 TS、1196 Python 全过，静态/类型/构建/ruff通过。
- 普通提交的控制前后证据原子存于既有 immutable plan；v1缺早期历史仍可正常提交、丢响应后重开对账和幂等返回。更早无依据目标不伪造恢复。旧参数未传仍精确兼容旧hash。
- 第二阶段源码冻结并准备本地恢复提交；没有 push、指定外审、PR、远端CI/合并或业务UI/Agent正式验收。
- 后续为同一T01会话下有界“格式3基础”候选实际集成人。已全文读 T00格式提案和独立review（含按真实依赖而非I05/I06整项等待的第8节），形成 [format3-foundation-contract](../../iterations/T01/format3-foundation-contract.md) 的最小内部状态/ready/hello/CAS/sequence/checkpoint及fixture设计。它是待T00统一/独立挑战的设计，未启用metadata/未迁移数据库。storage外的所需路径仍待双方精确交接，未自行修改。

Goal保持 active：父功能FR-001–006/804全部完成、持久项目/草稿/学习、正式确认/窄桥/UI、T08/T09/T10跨功能、指定双审及最终合并仍有工作，不将内部阶段完成当作父功能或上线完成。

## 可恢复提交与格式3合同准备

第二阶段实际本地提交：`d9d7138f8838474038bd856e3cd2460af25d9eaf`。提交后产品源码/测试未再修改，工作树原只保留受保护 AGENTS 未暂存。指定双审前不push。

格式3设计首轮独立挑战提出5处具体缺失，已在合同第7节逐项补齐：迁移backup/两层ready清单、CAS/claim/receipt/代次防ABA、保留原域no-op语义、checkpoint版本coverage/不可洗白辅助审计、hello有限错误和关闭边界。完整公共JSON及受限格式启动诊断留唯一canonical/main owner统一，未手抄第二schema或假称可执行。该文档修订仅为后续设计；独立复核已确认5项处置准确、可交T00统一，补充旧端[2]仅终止诊断分支。详见format3-contract-review.md；不触发无变化产品复测。

## 续跑政策回执与私有CAS计划器

本轮续跑核验 head=`0a2a4372dc64f9f6d90a18938f9a42ddc5721af7`、分支/AGENTS SHA和独占范围不变。上一轮为实质进展，不是等待或无进展。

已全文读取总控新透传消息和更新后的共同指令，实查其SHA `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880` 匹配；第九节9条及无桌面5条实际接收生效。原Goal/候选/已归档输入不重建，不因纯操作政策重开产品审查。Codex重置仍需本人每次明确确认、阈值和幂等；不新增付费/API/外发/GUI授权，不自行消费同账号权益。无GUI/native/e2e/HMR/审查应用任务排队。本轮独立审查已附政策全文并要求实际读回新共同指令。

共享接线没有新增生效路径。本轮在原私有范围新增 `project/draft_plan.py` 的无I/O CAS计划器及 `test_project_draft_plan.py`：首次保存、删除header墓碑、重建和恢复均推进持久generation；允许旧domain来源草稿安全保存但不伪称当前；拒绝旧CAS/错project/editor/未来来源，canonical不可变输入，JSON null与删除区分。该模块不建表、不分配operation/receipt、不写库、不注册公共schema；真实并发CAS/原子持久化仍需Store3事务内重新加载并核验，未计完成。

专用首跑14 passed，ruff/格式通过。独立只读审查和新全仓检查准备进行；不能用前轮1196 Python代替本轮新增代码验证。UI易失编辑token与持久header generation分别维护，迟到保存回调不得据持久CAS擅自清空新本地编辑。

## 新默认审查权限接收与CAS阶段验证

安全边界已实际读取AGENTS追加段、共同指令追加段和 external-review-permissions.md，实算后SHA分别为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、`df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`。接收ZCode yolo/MiniMax bypassPermissions默认；逐实际审查任务核验，仍只读、指定模型和无桌面约束，不新增付费/密钥/GUI授权。两独立agent已全文透传；主内审agent已实际核验回执，设计agent等下个正常边界。保护AGENTS不stage，纯政策不重跑不变产品。

纯draft计划器修复孤立Unicode编码P2后，最终20专用和独立复核通过；完整 `npm run check` 退出0，630 TS、1216 Python，lint/格式/typecheck/构建/ruff全过。此证据只证明纯计划器及既有回归，不是Store3持久并发。准备本地恢复提交。

总控刚明确允许在已有storage.py/project/专属测试内实施私有Store3 foundation，默认协议2与公开metadata capability保持不变，原Store唯一权威与lease不绕过；未移交文件/既有17测试不写。下一步将做显式私有格式门、Store层迁移/备份/结构验证/异常回滚，不复制JOB_SCHEMA或反向导入JobStore。T09固定873输入亦获只读引用授权，已读固定manifest和根审计；未调用其未批准helper或把expected预填Store。
