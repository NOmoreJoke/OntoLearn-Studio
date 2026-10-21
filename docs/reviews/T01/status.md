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

## Store3 Stage A 放行与原始证据封存

纯 CAS 阶段本地恢复提交为 `c5ba35b64e17cd34feb85068e8bc03a27b95ec39`，未 push。总控正式批准现有独占文件内显式 `target_format=3` 的内部 Store-ready 基础；默认2/旧格式常量不翻转，Job-ready、公共协议和正式 capability 仍未启用。I05→T03 的四个构建文件交接已收到，T01不写这四文件；格式3所需四/八个共享路径仍单独申请中。

第二阶段12份原始日志现已完整封存于 `evidence/stage-two-raw-logs.tar.gz`，SHA256 `bcac38671240c9bd1960f7ff1076c3c9ac02a20e531ab3199d00cfa0ff9e9d01`。清单 `stage-two-raw-archive.json` 记录每份字节/hash，归档后逐成员重新读取核验，保留失败和被替代候选；不修改旧原件。更正精确失败归因：`pytest-compensation-control-evidence.log` 的 1 failed/495 passed 中，对账及精确重试已经通过，失败发生在后续 undo 的 retirement_at 只查截至目标 revision、漏掉下一提交 before capture。早期其他恢复历史缺失问题仍保留各自历史记录，不能用它们替换此原件的实际失败位置。修正后的496专用及1196 Python全仓证据不变。

## Store3 Stage A 实际完成

显式私有Store(target_format=3)现已实现同OS writer lifetime lease、备份持久化和源变化检测、0/1/2→3同一迁移事务、结构/不可变证据/完整checkpoint/receipt验证与旧入口拒绝。新域提交只经原Store.commit，no-op和幂等语义保留；旧缺历史如实partial，不补造。七类独立意见（包括锁前竞态、假receipt和MAX上限）均已修复并独立关闭，详见format3-stage-a-review.md。

最终专用483 passed/44不适用skip；全仓check实际退出0，630 TS、1699 Python、44上述skip，静态/类型/构建/ruff通过。失败及被替代候选原件按hash归档，不用旧1697替代新源码。实际私有完整JSON样例和唯一DDL入口见../../iterations/T01/format3-stage-a-contract.md及同目录sample.json。准备本地恢复提交，不push。

12共享基础文件（I05四Python+I06 canonical/main八）现已逐路径双实体核验、接受、独立复核并由总控登记生效；本阶段未修改这12文件。全文读最新common SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`，AGENTS仍78df...97a759；两agent实际透传，主内审已全文核验回执，设计agent待下个正常边界。纯责任政策不重启Goal、不改变旧冻结输入。T03构建四/原I06余六、既有tests/worker/protocol/resources/CI仍不扩权。

已实际读T03/T04/T05/T07/T09/T10精确接点材料，T07三固定f9原件hash全部匹配总控；未采用其未批准实现。后续先在已生效JobStore唯一责任内统一实际job/application claim与同连接CAS/receipt/checkpoint/两层ready，再依次正式adapter。StageA只是Store-ready内部层，不是Job-ready/持久应用CAS/协议3或FR-001–006/804完成，无指定外审/push/PR/CI/合并/上线证据。Goal保持active。

## 总控逐DDL覆盖审计处置与Job schema3内部推进

4858cf178113697c1312e06cfc0ec469db31f363为StageA恢复提交。总控发现“每DDL”措辞大于原实际覆盖后，本线保留原承诺，补充显式3旧domain逐语句即时hook/四类故障和可选retirement四类；新定向172 passed526deselected、实际trace 53/29/21/30条一一对应，独立同样172通过，详见format3-ddl-coverage-review.md。不用缩小验收措辞代替实现，不重跑无变化旧矩阵。原26/16/33/2与WIP失败工具原字节另归档并给原session行/offset/hash；原8tar未改，不伪称曾包含。

Job层已实际完成有界schema3阶段：同一个Store lifetime lease、严格第二层迁移/原claim kind与context唯一演进、保留旧Job指纹和重试、公有身份原子、旧Coordinator拒3。212专项+独立含旧JobStore377通过；新增入口6及独立默认Coordinator/分页22通过，静态/格式/diff通过。尚未做新完整全仓，不沿用1699覆盖新源码；详细边界job3-schema-review.md。

本阶段恢复提交后继续真实非Job同连接Store.commit应用CAS/混合receipt/checkpoint/稳定操作sequence及reconcile/公共同版ready。不能把schema层或kind列存在算应用CAS、Job-ready或公共3完成。全文新共同指令已由两独立agent核验回执；Goal保持active，不push。

## 总控第二阶段逐DDL与原26探针归因更正

已实际读取T01-controller-ddl-coverage-and-tool-records-readback.md，确认StageA旧缺口已关闭，但Job旧claim演进的CREATE/DROP/各trigger当时仍成组hook；这属于验收粒度未全覆盖，不是已证实部分提交缺陷。现补4处即时hook及16个精确四类故障用例，保留原F3-02承诺。验证结果另记，不把212/377或旧1699当新增通过。

format3-stage-a-review.md原“26反例均拒绝”现已更正：原session第331行的26是修前pytest子集通过，旁边附加探针曾接受伪receipt；后续单独load修复及16/2等复核才关闭该缺口。原归档/原件不改，当前代码不据旧修前输出冒称仍有该漏洞。新持久应用CAS代码正在实现，尚未测试或登记ready。


## 真实持久应用 CAS 与混合历史链

私有 JobStore3 的元数据与草稿save/delete/restore、同连接combined、真实全局application claim、单次sequence/receipt/checkpoint及固定throughSequence列表已实现；详细行为与内审见 [application-cas-review](application-cas-review.md)。学习/audit/完整apprestore及公共3未开放。Job旧claim逐DDL新增16项实际与独立通过。

修前应用108项和全仓630TS/2212Python/44不适用skip虽通过，但内审发现共享prepared凭据跨类型P2，因此仅作被替代候选。已严格分开普通Job计划类型/hash/ref/确认，在claim前拒绝，补双向误用零影响可重开反例；修后本线275通过、独立2＋3定点及Job2/3探针通过，P2关闭。第二位八边界20项定点无新增阻断。修后全仓仍待实际终态；原件保留，不沿用旧通过。


修后全仓实际退出0：630 TS、2214 Python、44上述不适用skip，静态/类型/构建/ruff通过；详情与冻结源码hash见application-cas-review.md。新归档原件SHA `1f35a12250819bb74b8eda325e753815e2fdad38337c51ff23d1425924fe0fe9`，逐成员原字节回读。当前准备本地恢复提交，不push。

已全文读取T05固定412、T03 process b868、T10 b39、T09 e651的接口原件并核对hash；形成 [owner-interface-responses-r1](../../iterations/T01/owner-interface-responses-r1.md)，独立设计审查无阻断。D7严格三字段、失败定位专用资源、同协议来源分块、业务白名单/闭包/单writer新项目receipt为明确设计；worker.py未交接、真实source/学习账本/transfer投影和import receipt仍是实际缺口，未消费未批准实现。下一步继续真实学习/辅助账本与完成边界、正式canonical/ready和已授权窄接线，Goal保持active。父功能、指定双审、PR/CI/合并/发布仍未完成。

## 固定CAS候选与下一阶段设计

应用CAS恢复提交为`f51dd38dbdfd2fbb1b9923efee666a19d5b415cc`，总控正在固定候选独立原件审计，本线产品/测试保持不变。新增来源分块和学习账本设计已独立挑战并关闭两处文档缺口，详见follow-up-design-review.md。设计明确source内容不等于授权、远端受理/撤销排序、worker实际首帧缺口，以及activation CAS/完整attempt辅助覆盖/真实publisher事务；尚无对应新实现。

I05 worker唯一未来维护offer已实际接受并保存双身份回执：本方approved5f 9314B/SHA2fa848…06f2f0，对方C3 13638B/SHA3d934e…4f99d；各实际path clean。等待独立/root生效，不写worker、不采用C3、不扩protocol/resources/旧tests/build。拟新增专属test_project_source_transport.py、test_project_source_worker.py、t01-source-transport.test.ts仅为原独占prefix下计划，尚未创建。此次仅文档和接收回执，不重跑无变化产品，不push。


## worker唯一维护生效与私有来源内容阶段

已实际全文读总控固定f51证据审计，SHA23548807004be26fb1ebd338abfe832d1628a6885cd81d9d6244c23c7cd22c35；旧P2/DDL/26措辞有界关闭，明确273/20修前与后续275/2214区别，原105缺poll和封存call缺output不补造。没有新增要求修改f51产品的阻断。

worker.py唯一未来维护已于2026-10-21T10:21:19.636646+08:00由总控effective=true登记，协议63c194…450da、独立最终47e564…6423、接收019117…58581均实读。common原§9/无桌面与新增尾段实际接收，新SHAff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff，AGENTS仍78df。两内审已透传，主内审全文读并核hash。只从5f维护，不复制C3，不扩protocol/resources/语义/旧tests/build/CI；不将所有权生效当source wire/限额/公有3-ready获批。当前worker字节仍未改。

新source_content.py在原私有范围实现typed chunk/manifest、同JobStore连接不可变blob的原子intern及完整bytes验证。原私有source测试精确路径下87项实际通过，主内审6项独立探针无新阻断；未重复矩阵。新全仓check待终态，不沿用2214当新增代码通过。无新schema、writer、正式operation/receipt、授权、上传、parser或worker/public接线；内容ref不授予权限。T03固定1e8ef97回复全文读回并形成source-contract-t03-response-r2，六项缺口按设计答复，完整Table投影与pin/TTL/profile等仍待真正冻结。


来源内容阶段最终完整check实际退出0：630TS/2301Python/44原不适用skip，lint/格式/typecheck/build/ruff均通过；主内审6项独立探针无新阻断，第二位T03 r2设计复核通过。原始证据包source-cache-raw-evidence.tar.gz SHA9ef1078784b6a7c32a28a138aa44a2667c338f162190608ffc895fca5e199405逐成员回读，21对工具call/output及两完整logs可恢复。准备本地恢复提交；未push，worker仍原5f。该阶段只是严格完整性/同库不可变缓存事务，不是公共wire/source授权、真实parser、项目学习/完整restore/ready或父功能完成。


总控source固定证据审计d77f902…c3108已全文读：同版2301/87/独立6确认；E1只是87专项完成poll漏封。现仅补封原session2693/2697两完整工具行及索引，补包SHA370a055ad1ab23ba037d2efb297b78300f1389de163782fac9e538c97ef23a52，旧62633B包身份不变；无测试/产品变化。

收到I06固定b1283bc/68dfd71来源对齐回应并全文读，形成source-lifecycle-decisions-r3：选择精确同块append幂等、不重写/不推进/不延寿；接受1pending begin、2leases/16MiB及30/120/600秒候选技术预算，另提256attempt tombstone/256MiB逻辑encoded持久预算待总控接受/实测。main未dispatch guard与已dispatch同coordinator权威排序区分，unknown保留原operation及资源并对账。独立设计发现稳定计划/临时lease指纹门未明确后，已补§3与对应fixture条件：未接纳lease失效同bytes也需新preview/proof/人类确认；已有claim原请求跨session对账不要求临时lease活跃。该设计意见已独立关闭；wire/schema/预算/运行仍未批准或实现。准备纯过程恢复提交，不重复无变化check。

## business3唯一canonical校验层与接口设计补充

新增严格3分支、完整跨端corpus、实际registry hash绑定及原Job/资源/页/事件身份复用，生产仍2且coordinator拒3守卫未变；没有真实3握手/ready接线。专项196TS/195Python通过；新全check实际exit0：826TS/2496Python/44原不适用skip，静态/格式/类型/构建/ruff通过。独立只读83额外探针通过，无新增阻断，旧defs/资源旧值机器对比不变；详情见business3-validator-review.md及独立报告，不把内审当指定双审。

新原始证据包SHA4f012bb90358ee3f5d963f9ee4706d8666828033c971d513b95c1eed8c6a3594，9对原工具记录/3完整logs与实际专项、全check终态poll已逐成员回读。旧f51/ff原件保留；总控E1补封独立结论115ddd…已读，原证据缺口有界关闭。

source r4设计关闭总控P2R1（sealed/终态、accepted pin/迟到ack/满额与barrier/重建计账），独立复核无新增设计阻断，尚未实现。完整表摘要r1设计据T03实际str与canonical原implementation形状关闭两个空项，受限CSV utf-8-sig不冒称S1唯一编码，实际parser三身份仍待owner，golden只能synthetic；独立定点复核通过。T05 r2仅我方context/DTO/身份与未来诊断责任接受，Q6/新路由/新语义未批准；I05字符串term现存缺陷由原owner新候选修复，本线不消费未批准C3或新候选、不改已交worker。

本地恢复提交后继续纯表摘要助手和同版ready的真实前置，Goal仍active。无push/指定双审/PR/CI/合并/发布新证据，父功能未完成。

## b35总控审计收束与新phase合同

总控固定b35全量独立读回d1ddcc…37be7已全文接收，无新增校验层阻断；43 response有13完整正例重复，83独立断言未封完整子shell exit对象的边界如实保留。旧f51/ff/b35实现和原始证据不改、不无变化复测。本阶段仍只是validator-only，真实3-ready未启用。

总控source r4/digest独立设计9da317…8c39已全文读，r4原R1设计关闭；D1/P2现由digest r2一次有界capture/owner数据树/私有编码与Proxy/隔离边界补齐，内部独立355259…70463设计闭合。startup r1/r2及独立报告保留R1–4处置和旧SHA，内部设计项关闭，schema/有限新码/I06多层错误门/真实子进程仍待合同接受和实施。T03真实parser三身份缺失及五encoding/sheet新事实已全文接收，纯机制与正式身份/Job D7提案分开。

helper未完成准备已存私有patch，产品全部恢复b35；patch含旧两遍caller读取方案，不能直接采用，不计45拟定golden或初步静态为实现通过。下一代码须root先读回闭合具体合同、明确新phase。当前只保存纯过程提交；Goal active，无push/指定双审/PR/CI/合并/父功能完成。


## 纯表材料阶段收口与四路径维护生效

纯材料授权562be7…71a02内的三产品路径、两专属测试已经实现；完整表/精确选项/三字段身份/expected source hash/编码前总预算核定，保留owner data-only和Proxy隔离边界。独立审查P2-M1（JSON整数值预算两端接受不一致）已修复、独立定点关闭。修后126 TS/132 Python专项，最终fullcheck实际session67934 exit0：952 TS/2628 Python/44原不适用skip，lint/格式/类型/build/ruff通过。旧938/2612为被替代修前候选，原失败及修前/修后工具证据均保留。详情见[source-table-material-review](source-table-material-review.md)及独立报告。

原始包39000B、SHA e558203ff2ac79fe8948549054ab80fc1d04353d7c53238a608f6fdb1b13ec2c，14成员和五最终产品hash已逐项回读；索引SHA95f314f4821f6c716985f9b6918ca8c548a91a7f6584ade3267a0a3958020fcb。旧阶段原件均不改。本阶段未启用parser/producer/source wire/worker或runtime3-ready，内部审查不替代指定双审，不push。

四路径未来维护已由总控effective JSON 0df87b7c…03a32生效；092dfbe所留原pending接收回执作为历史保留。主线与两独立agent均已实际全文读取17891B common e437121a…971b0并核旧16317B前缀ff5f9fd0…cfaff。所有权生效不是startup实现授权；I06余四路径不转、无GUI等门不变。Q6用户采纳回执已全文读取，只确认规范已采纳，不算对应实现或验收。本线接着准备精确启动实施计划，实际实施仍须总控明确新阶段。父功能/指定双审/PR/CI/合并/发布尚未完成，Goal active。


## 纯表预算 P2 原始反例 E1 最小补封

总控独立原件审计发现，固定39000B原包的7对独立工具记录没有收入最初预算P2反例call_3c61a14c633944ed8ba46cae5eb0a099；报告叙述及source prefix hash不能替代可恢复原call/output。现另增evidence/source-table-budget-p2-supplement.tar.gz（1802B，SHA9c325c4ef0e93b43d4a09159618505daff0b6abe592698b215e519155268ab95）及json索引（2109B，SHA1fe1f9509093547a18a44eadbda040ff92904f42129f3c8ffa576edaad5b3b9d）。按原已固定prefix逐字提取1532/1535两行，保留原offset/length/hash，解包后与原字节回读相同。原wrapper仅显示stdout的边界继续保留，不补造旧exit对象；未重跑反例或产品测试。

bf04169、原包e558…ec2c/原索引95f…0fcb、独立报告及五产品hash均不改；此次只是缺原件的补证，不是新产品候选。待总控补绑核验，不提前代其登记E1关闭。


## 总控材料读回与下一启动阶段精确计划

总控source-table-material读回16336B/SHA c88aa1252e8c9b2f5b0ab835762bfbaa1e1a748f96979322b917c9a12a0428d4已实际全文读完并核hash：bf04169固定产品与27a0d17补封相符，E1由总控实际逐原字节核验关闭，纯材料阶段可收口，全部parser/producer/wire/ready/父功能/双审及发布边界不变。未重跑材料。

总控启动阶段精确预审8741B/SHA cb52ba37111d778c696a534cf34d4dda092eac98071bcc75930f42ad5904c5b8亦已实际全文读。新business3-startup-implementation-plan.md在原闭合r1–r3之上固定17产品路径及7测试路径，补Store/JobStore构造失败逐资源首因与父子移交，以及原Session/promise不可伪WeakMap提取、真实listener交付clone凭据；作者处置不代总控关闭。当前仅提交计划与独立文档，不实施startup、不启动桌面、不把未来维护生效当阶段授权。精确产品范围/有限新码/内部profile与root一次阶段授权仍待实际流程。Goal active。

## startup 实施阶段完成（固定17产品/8测试）

已依最终授权3054a5…f334实施严格五字段启动通道、四有限错误、真实两层ready/reconcile后内部显式协议3、首因清理与保守reader状态、ES私有Session/原promise/listener来源认证及跨层有限展示。默认生产2保持；原sourceTable/worker/protocol/resources/I06余四不改。旧task-runtime仅在单文件临时授权6764ab…9eb14内迁移，8项原测试语义保留，窗口待总控显式关闭。

修前错Session通知P2、根嵌套guard吞[3]P2均已修复并独立定点关闭；转义1024/1025完整原bytes同decoded pair已补齐。固定source manifest6ef218…c5b4、ZIPd39278…e86a共25源码/测试与独立回读一致，保护AGENTS78df未暂存。详见[startup实施阶段报告](startup-implementation-review.md)及[startup独立审查](startup-implementation-independent-review.md)。

最终全仓check真实exit0：1030TS、2706Python、44原不适用skip，静态/格式/类型/build/ruff全过。未签名package:dir真实exit0；新包引擎5session/9资源与实际worker原子事务、重开幂等通过，asar/main AST同源绑定通过。新main46e6b7…b9f3；完整raw stdin/stdout/stderr和所有首失败/被替代输入保留。旧main/包成功不冒充最新候选，普通wire观测不冒称私有pending Map本体。

本阶段准备本地恢复提交；不push，无指定双审/真实Electron IPC或UI/native/e2e/远端PR/CI/合并或发布新证据。原完整Goal仍active，接续剩余父功能与正式跨功能验收。

## startup根收口及下一真实业务阶段计划

startup实际本地恢复提交为`fd3944a35aed05c279d7d0c2f9a077c84d99aaf2`。根最终closure5669B/SHA`b423e436bf7e64b47452275cf084b132b18deb4fe00ecdac3663426697346642`已实际全文读并核hash：17+8固定Git/ZIP、完整check、新包/9资源/46原记录、61成员和301原工具对均经根核验，内部阶段无未解阻断。自2026-10-21T14:04:13.952488+08起旧task-runtime临时窗关闭，未来逻辑维护者I05、T01只读；消歧effective JSON3571B/SHA`c3d1fb55fe1d0e3d5b7a931fdcb43f32147c37f9a22b016332871ae859e9fa0f`亦实际全文读。fd的5a190b输入和I05 C4各保原件，不复制或再写该旧test。

按根明确docs-only指令，准备[正式ChangeSet业务服务计划](../../iterations/T01/changeset-business-service-implementation-plan.md)：复用已有changeset.commit正式Job、实际typed定义/引用与人工事实、完整Diff、独立确认、Store原子提交、选择性undo/故障重开和版本传播。申请10产品/4新测试，当前尚未实施；不改fd已验25source/test，不把test.atomic改名或用虚假metadata操作替代领域写。真实producer/完整定义语义、全项目restore、I06项目选择/完整Diff与人类UI、T08及其余44地图/FR范围保留。

独立[计划审查](changeset-business-service-plan-review.md)已关闭Diff字节/重组、确认归因与重试、两事务/取消三项初稿P2，固定最终计划SHA`5eb576f029bdf652ff2f52c82a335cf977afeb57cdf8db807d82d323832271e8`，可交根一次精确阶段决定；不是新实施授权。初稿19085B/446c4d已从原完整cat工具记录按原字节恢复为独立ZIP，保留初稿和审查历史，不重写。此次只文档/证据，不重复已通过的无变化产品检查/包；指定双审前不push，完整Goal仍active。

总控固定5eb技术审查14378B/SHA`50f6d5fcd20c883a2e9d585193f2dab32c6c6a006d54939b6e2de69413610cc9`已实际全文读并核hash，仅新增两项合同P2：确认已签丢响应遇cursor TTL/GC，以及正式undo的ABA/引用冲突完整影响读取。当前计划27888B/SHA`39ebbf378386004eb9e8654bf9dbd7465e50d5215a87c55fde01cffc258d71e1`在原10+4内明确原confirm业务请求/同事务持久回执先于临时cursor、首次签发与原回执分支、新RPC id不改业务幂等；preview ready/conflict有限分支和原page文档kind隔离，从实际不可变历史/当前refs/owner-slot完整投影影响，证据不全明确暂停。独立修订报告19255B/SHA`d4869249d713abd168a352e5ac0fe5996bcbe972ddad6ab99725f3b255aeb6a0`已实际读回新增全文并核hash，两项计划层关闭，无新增阻断，可交根仅复核delta作阶段决定。原5eb/dafe历史保留，尚未实施/测试；产品与fd完全相同，不提前称真实确认、撤销或FR完成。

## 正式 ChangeSet 业务服务阶段内部完成

根正式实施授权8818B/SHA `421f974c43975886d280386316b34b5f1e284712d68d38f338d8083beb217467` 已实际全文读回，按固定39eb计划在10产品+4新测试实施。preview/fullDiff/confirm及原changeset.commit已从显式内部3走真实typed ontology/人工RDF、唯一Store原子提交、选择undo、持久确认原请求回执、Job/operation/receipt重开；default2和原测试保持。完整影响实际列ABA B/C、后续引用、owner-slot/墓碑及retirement，缺证据暂停。host调用是受信机制测试，不是真人确认/UI验收。

独审两项P2（helper getter预算capture、同ref坏blob预览延迟拒绝）已修并原探针独立关闭；真实hello投影旧2白名单缺陷亦修复。最终14源码清单SHA `21ce587382ed854b29c1b38ad2646a573e01273b3efd4950709e0786e8518b21`、ZIP SHA `64d03db87de4523dd4c2d5e547e3e98ba0431ade82f1ebde760a747916a35d68` 反复核验未变。最终完整check实际exit0：1125TS、2789Python、44既有不适用skip，lint/格式/类型/build/ruff全过；verify:sources核12源。27真实os._exit、13SQLite authorizer和各异常/取消/持久全状态反例纳入证据。

新同候选unsigned package:dir实际exit0；包内正式3Job提交/不相交B/undo/重开对账、claims/receipt/revision/sequence各3、只保留B通过。实际asar/main逐字同源，main `fcdd498ce6084b10369648512a11fba931306f3164d88448caf7ef841776b850`，9契约资源/lock/engine实际核验；首并行build随机nonce错配与旧AST探针不识静态JSON.parse字串均保首失败，串行新包及修正纯数据探针后通过，未改产品。详情见[实施报告](changeset-business-service-implementation-review.md)和[独立审查](changeset-business-service-independent-review.md)。

本阶段准备本地恢复提交及同候选双模型完整输入；不push，尚无指定双审实际Pass/PR/CI/合并或生产/真人证据。原44项/FR-001–006/804完整Goal仍active；I06项目选择/命名bridge/完整Diff和真人UI、真实Agent/来源producer、完整学习账本、全项目restore、跨功能/双平台/native/用户验收等继续保留，不由后端服务通过删除或关闭。当前无本机GUI/Electron/e2e/native/HMR/凭据/外部审查应用操作。

原始封存163成员/281对完整工具call-output已逐原字节回读：raw包1189059B/SHA `29a3f65fdff1f7635f1595db8a6d368d26050455c719ac92c53ab733cac85c0a`、索引SHA `40ce9396152a431ad0417105ccbecaa8d7929bf01978e39d3aab6bbe1cdf1673`。最终独审30586B/SHA `3acb0305f1ece626c07f192c3ccb07af1c69907ec3a3ec816137475481e31a30` 无未解代码阻断，非指定双审替代；双模型相同完整只读输入已备，实际独立安全桌面/租约仍由总控条件调度，不假称新任务已创建。
