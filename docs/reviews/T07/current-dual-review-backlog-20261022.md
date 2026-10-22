# T07 全量指定双审积压事实清单

2026-10-22。T07 尚无任何 ZCode/MiniMax 指定审查任务或通过记录。以下覆盖已保留实现、技术子项、纯提案、过程材料及未就绪父功能，不只登记 ready S1。`INV` 是本次盘点行号，不是新增官方阶段、独立审查拆分或运行授权。

## 实际身份和责任

- owner 聊天：`01a15bce-0706-7360-8e99-df8fe9b15ad2`；worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario`；分支：`feature/weekly-t07-scenario`。
- 实际起点/base **B**：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 首次实现提交 **I**：`791a7b2b9ea831105e3aa7ef2e95f80001942ba5`。
- 当前产品/测试候选 **P**：`f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`。
- 本次盘点前过程 HEAD **D**：`24f3703ecf4fce75e0d0375f7291ed928f083c41`；完整准备提交 **F**：`f50ebc0fb9db792aceec103e623768d585a6175d`。
- 本线唯一授权写面：`packages/engine/src/ontolearn_engine/scenario/`、`packages/engine/tests/test_scenario_*.py`、`apps/desktop/src/renderer/src/scenario/`、`tests/unit/t07-*.test.ts`、`tests/fixtures/scenario/`、`docs/iterations/T07/`、`docs/reviews/T07/`。没有共享 Store/Job/coordinator/worker、公共契约、main/preload/App、依赖锁或构建写权。

本次读取本地 T07 分支、worktree 注册及 B→D 全部7提交，只观察到这一条命名 T07 实现分支/worktree。其他 owner 的阶段体验外壳、依赖代码和审查任务不计为 T07 实现或通过。这里记录本线实际 base，不声称本次刷新了远端 develop；真实派发/集成前仍须核当时批准基线。

## 指定双审共同状态（适用于全部行）

| 项目                          | ZCode                               | MiniMax Code                           |
| ----------------------------- | ----------------------------------- | -------------------------------------- |
| 必需设置                      | GLM-5.3 / 最高，实际任务 max / yolo | M3.1-Flash / xhigh / bypassPermissions |
| T07 实际 task/session/turn ID | 无，未创建                          | 无，未创建                             |
| 实际任务级设置读回            | 无；上述为要求，不是实际回执        | 无；上述为要求，不是实际回执           |
| 实际报告/完整终态/结论        | 无；未审、没有指定 Pass             | 无；未审、没有指定 Pass                |
| 已准备正文                    | `round-1/zcode-frozen-prompt.md`    | `round-1/minimax-frozen-prompt.md`     |
| 未来报告目标（尚不存在）      | `round-1/zcode-glm53.md`            | `round-1/minimax-m31flash.md`          |

所有路径均相对本文件所在 `docs/reviews/T07/`，全树绝对位置见上。当前只准备了一个完整 **T07-S1：完整私有轮次编排/资源FIFO指标/独立场景页及现有验证**，受审单位是 **B→P 全25路径、14项实现/测试/fixture**。下列 INV-01～06 是该完整候选的技术组成，不各自缩成单项审查，不因逐项登记重复建立模型任务。root 已限定接收准备包；尚未全文批准两提示词或重新认证9条原终态来源，T07 也未取得新任务创建租约。

## 全部保留技术项和未就绪积压

| 行号/阶段或技术项                                                     | 实际版本、原 owner 写面                                                                                                                                               | 当前验收与证据                                                                                                                                                                                                                                        | 缺口、后继及可独立下一行动                                                                                                                                                |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| INV-01 不可变定义、事件、FIFO和轮次编排；已实现，属S1                 | B→I首次落盘；当前B→P，过程D。T07：`scenario/{__init__,model,runner}.py`、`test_scenario_rounds.py`                                                                    | 项目/输入/规则/行为/参数/语义/引擎/锁身份，轮次顺序、事件去重/未来事件、FIFO/历史ID、三指标、失败/取消/恢复校验。轮次文件最终46 Python；`evidence/validation.json`、原始final 1～6。领域端口为合成                                                    | 真实T05/T06和正式任务适配未接。全部保留于P，等待短创建lease后随完整S1双方新审；不因本清单重复测试                                                                         |
| INV-02 私有场景页面、view身份及headless探针；已实现，属S1             | B→I首次落盘；当前B→P，过程D。T07：renderer `scenario/{ScenarioPage.tsx,presentation.ts,scenario.css}`、`tests/unit/t07-scenario.test.ts`、`evidence/render-probe.mjs` | 项目/场景创建、结构化输入、两产能、任务/历史依据/详情、逐轮/最终比较、缺轮和受限操作禁用。27 TS；Chromium151.0.7922.34、1440×1100/390×844合成headless，`evidence/ui-probe.json`；原始final 2～4                                                       | 未挂App/bridge，无真实数据/执行/删除/恢复联验。保留于P完整S1；正式页面接线需对应owner批准，合成页面证据不替代产品                                                         |
| INV-03 批准T09输入及E5资源/指标投影；已有测试/fixture，属S1           | B→I首次落盘；当前B→P，过程D。T07：`e5.json`、`t09-e5.json`、`t09-manifest.json`及轮次测试                                                                             | 批准T09 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的17项hash及两份原字节副本；两产能工单/资源集合、消费/未来事件/指标/重放。公共告警4/8/12/16，私有零告警fixture独立。`evidence/t09-input-receipt.json`、原始final 5                                 | 未验真实 facts/inferred/actionTrace/triggeredInstances，未消费T09服务。保留于P，不把资源投影改称完整E5；随完整S1审，真实领域依赖批准后另联验                              |
| INV-04 显式Context及冻结计划/完整逐动作轨迹；已实现，属S1             | B→I首次落盘；当前B→P，过程D。T07：`runner.py`、轮次测试及私有接线提案                                                                                                 | `Context(round,phase)`贯穿并检查推理阶段；动作三元身份/eventId/behaviorId/actionIndex、数量/唯一性、冻结计划保存，1～1000轮/每轮1000动作。原始final 6，最终轮次46项包含这些用例，不能另加重复计数                                                     | 私有形状校验未代替T06真实条件、顺序、冲突、动作语义/动作间取消。保留于P完整S1，正式adapter等待精确批准接口                                                                |
| INV-05 真实批准Store故障/取消/崩溃边界；已有测试，属S1                | B→P新增，过程D。T07仅 `packages/engine/tests/test_scenario_persistence.py`，生产共享源码未改                                                                          | 最终44专项：两产能完整Round保存/重开/缓存隔离，前轮0/1×五事务阶段×异常/取消/真实READONLY，10真实子进程退出、禁注入负对照及交接一致性。最终check657 TS/1142 Python；T07共46+44=90 Python/27 TS。`evidence/persistence-validation.json`、原始final 7～9 | 首批42项READONLY证明已失效；修复后runner外严格断言OperationalError/SQLITE_READONLY码名。仅真Store＋合成领域测试，正式Job/取消/终态未验。随P完整S1新双审，不能重用失效证明 |
| INV-06 完整Round/Checkpoint投影交接样例；已有fixture/一致性测试，属S1 | B→P新增，过程D。T07：`round-projection-handoff.json`、持久化测试、交接文档                                                                                            | runner实际输出完整JSON/stateDigest相同，区分未消费全集与T09已注入pending子集；原始final 9、`persistence-validation.json` handoff段。44持久化包含此用例，不重复累计                                                                                    | operation-id权威幂等/ack-loss API是待批准提案。`test.rounds`只接toy载荷，示例job/run身份不是实际任务。样例保留于P完整S1；T01/T00冻结真实接口后联验                        |
| INV-07 正式领域/事务/契约/页面/导出接口方案；纯提案，不是产品实现     | `integration-request.md`起于I并在P扩充；`round-projection-handoff.md`于P新增，base B，过程D。T07仅文档/样例，供应实现由各唯一owner维护                                | `docs/iterations/T07/integration-request.md`、`round-projection-handoff.md`；普通独审final 8～9核过toy限制及样例/提案边界，不是供应方API批准，也没有指定Pass                                                                                          | 无单独生产实现，不伪造技术阶段完成。root按当前唯一owners路由原固定提案，确认具体源码/接口/运行窗口；旧原件与hash不改                                                      |
| INV-08 外审准备、原件封存、fresh文档核验；过程材料，非产品实现        | base B，所绑定产品P；准备F，独立文档核验D。T07仅 `docs/reviews/T07/`，旧25候选原件不改                                                                                | `round-1/`：25全路径/14身份、75归档成员、9原始final/3加密中间消息元信息、18packet封存项；`preparation-audit.md`过程核验通过，无阻断P1/P2。root限定接收不等于指定审查或新租约                                                                          | 指定两方ID/实际设置/报告/终态均缺失。完整原文及历史报告保留；派发前附当前操作政策addendum，完成root提示词/source全文审核、base/输入核验和短创建lease                      |
| INV-09 真实T05/T06领域与完整E5；未实施/未就绪父积压                   | **无产品/测试候选SHA、无实现base**；仅参考B提案，过程D。所需owner：T05推理/T06行为；T07仅其批准私有adapter                                                            | 待验：初始/事件后/资源后真实推理；冻结条件/排序/冲突/动作/取消/新事件，完整E5四类领域结果及G.4。现有合成测试不关闭此行                                                                                                                                | 依赖具体批准API/身份/错误/fixture，不能消费未批准变化代码。下一步由root精确路由供给；接口到达后唯一owner接线、必要验证、新同版完整双审                                    |
| INV-10 T01/I04正式scenario生命周期与恢复；未实施/未就绪父积压         | **无T07生产adapter候选SHA、无实现base**；仅参考B提案，过程D。T01持共享Store/Job/coordinator/worker，公共契约按现owner                                                 | 待验：业务注册、project/run/job身份、原子Round+progress、取消/最后提交/终态竞态、operation-id/expectedRound与ack-loss/崩溃对账、正式数据隔离；FR-705删除/恢复/来源合法的快照续跑                                                                      | 44真实Store测试未覆盖正式Job，toy能力不可冒用。下一步T01冻结内部API/受限错误/恢复fixture并批准，T07在私有写面适配联验，不绕过不可变触发器                                 |
| INV-11 公共契约/bridge/App真实页面与Agent依据；未实施/未就绪父积压    | **无T07正式接线候选SHA、无实现base**；参考B提案，过程D。T01 canonical/main，I06 preload/env/App/style，T08 Agent消费者；当前具体交接由root复核                        | 待验：创建/复制/运行/取消/详情/比较/删除/恢复/续跑业务方法严格校验；FR-700～704真实记录进入页面，Agent按真实依据解释。现有props/callback页面只属INV-02                                                                                                | 无正式IPC/mount/真实操作验收。下一步root确认owners与批准方法，按唯一责任接线；不因页面已做而假定App完成                                                                   |
| INV-12 完整运行依据、T10跨设备及产品/平台/发布；未实施/未就绪父积压   | **无T07完整产品/跨设备候选SHA、无实现base**；参考B提案，过程D。T07运行语义，T10包/重放，T11平台/发布及对应维护者                                                      | 待验：FR-703完整输入/配置/规则/行为/引擎/锁/语义齐全才能标可重放，跨设备实际结果核对、G.6恢复迁移、FR-700～705父验收；必要CI、两OS、真人、远端develop及发布门                                                                                         | 无完整真实运行包/跨设备/完整产品平台证据。永久保留在积压，实际adapter/包齐全后安排验证；不得用私有S1、基础I04或阶段体验包关闭父门                                         |

## 历史版本、普通内审与撤回/失效关系

完整本地链为 B → I → `833c6a1d836f76b6714d11e6a7ad2fd94049749d`（恢复点过程）→ P → `48b14dabeb769dc45e36a8e4be936d244a9c8b14`（就绪过程）→ `982e4535e864c17275e51ed67664c0b7fac367bc`（阻塞过程）→ F → D。只有I、P引入实现/测试/fixture或对应验收变化；其他为过程记录。

- I的21文件候选由P的25文件完整候选后继；I→P改9路径，新增真实Store测试/完整交接样例并更新验收和证据，私有生产代码/页面未变。I的范围全部保留于P，没有撤销或永久排除的独立实现。旧全量check657 TS/1098 Python属于I阶段；新增测试后最终657 TS/1142 Python属于P阶段，不能混作同次运行。
- 第一批未提交内审经历IR-01～04 P2修复，再补项目/引擎/锁身份、批准T09投影、Context/逐动作轨迹；后继都已落入I。内审原始final并未各自保存可寻址的Git候选SHA，因此**不为这些未提交阶段补造SHA**，保留原message ID/时间/内容hash及准确边界。
- 持久化首批未提交42项被独审发现READONLY假通过（IR-05）；该证明撤销，随后43项修复/负对照，再44项完整交接一致性，最终落入P。原始失败/旧passed日志均保留；旧42项不能因为P通过而追认。
- T07从未有指定双模型Pass，故没有“指定旧通过因变化失效”记录，也没有撤回的已审候选。普通内审的历史Pass仅限各次当时内容，不能视为最终P的指定Pass。将来实现/测试/配置/依赖/验收/base变化，仍须新候选、必要验证及双方各全新完整审查。
- 普通原始独审来自 `/root/t07_internal_review`，9条精确原始final已在 `round-1/internal-review-original-finals.jsonl`；精确message ID/时间/原session行号及SHA见 `round-1/internal-review-sources.json`。IR-01～05及每次真实计数见原文；`internal-review.md`是开发者摘要，不是原始agent报告。fresh过程审查者 `/root/t07_round1_document_audit` 的报告在 `round-1/preparation-audit.md`，只通过准备包文档范围。

## 当前操作addendum与下一步

已实际全文接收 `iteration-control/2026-10-21-weekly-release/desktop-operation-policy-20261022.md` 和最新共同指令：人类撤回静默桌面/用户时段要求，已授权任务可直接computer use，不以CLI登录、headless或隔离桌面为前置；内部资源协调仍保留。旧prompt/manifest、旧“无GUI许可”及历史阻塞文字只按历史时点解读，不改原件。

补齐双审授权不取消具体阶段写面/运行票/自动审批拒绝或SQLite损坏HOLD等原边界。T07未取得新指定任务创建lease；由root串行协调短时创建/核验，不能占整个后台推理时长，不能与当前T06两真实任务争焦点或重复建它们。T07派发时须附此当前addendum，不能把旧冻结输入中的静默文字继续当阻塞。

立即可独立完成的是本次全量事实盘点和原件/提示材料整理。下一执行门是root完成完整提示/source核验、当时base/输入确认及短lease，双方各新建同版完整S1只读任务并实际读回设置；不是让用户重复提供桌面时段。真实领域与父集成则按INV-09～12具体依赖推进，不能永久排除未ready项。全部57P0及原验收、完整终态/全文报告/全部意见、CI、两OS、真人、远端门均保留。

本次只读取Git/文档及核原件身份、检查本新增文档格式，没有产品测试/构建/GUI/模型任务、没有改Goal或旧manifest。生成结构化草稿的首个Python命令发生UTF-8解析错误、exit1，未生成文件；随后改为直接写本事实文档，不将首错伪记成功。
