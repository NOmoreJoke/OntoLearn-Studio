# T06 行为状态

2026-10-21（Asia/Shanghai）实际启动。负责聊天：T06 行为算法与完整功能。

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior`
- 分支：`feature/weekly-t06-behavior`
- base / 启动 HEAD：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- `git status --short --branch`：仅 ` M AGENTS.md`；指南 SHA-256 为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。该保护源保持未暂存。
- 已全文读取启动与公共指令、总控交接/计划/审查、自身任务、需求/验收表、工作树 AGENTS 和 PRD FR-600–604、E.1/E.2/G.3。
- 初始独占新增路径经 `test ! -e` 核验无冲突：`packages/engine/src/ontolearn_engine/behavior/`、`packages/engine/tests/test_behavior_*.py`、`tests/fixtures/behavior/`、`docs/reviews/T06/`、`docs/iterations/T06/`。
- 已建立本聊天独立 Goal。未继承或修改 I05/I06 Goal；未写其他树或总控 state/tasks。

下一可验交付：版本化私有接口及完整输入/输出样例；事件准备、冻结推导身份校验、条件评估、写入意图、竞争检查、稳定排序与内部安全动作计划；B-04/05/06/09/10/11 精确反例与异常路径。

计划命令：`uv run --frozen pytest packages/engine/tests/test_behavior_*.py`、`npm run check`；只运行无窗口检查。独立只读 agent 内审在实现后执行，指定双模型预约后执行。

当前边界：未实现真实推理/Store 原子提交/资源阶段/Agent/UI；纯计划不作为数据库回滚或完整 B 用例通过证据。T01/T05/T00 的实际批准接口、T09 公共固定输入及指定 ZCode/MiniMax 外审资源仍需交接；精确需求写入本线接口文档。父任务保持进行中。

## 私有算法实际进展

已实现：严格事件输入、scope 绑定消费记录、内容指纹幂等、事件后推导绑定、冻结条件、完整 E.1 排序、内部 create/set/add/notify 计划、跨实例任意单值意图竞争检测、同值幂等保留通知、完整状态/轨迹/Diff，1000 动作限额与失败不返回候选。

私有反例 B-01/02/03/04/05/06/09/10/11 共 9 例完整状态及轨迹预期；均使用手工推导输入。B-07 需 T07 资源阶段，B-08 需 T08 实际 Agent，所有完整轮次及行为前推理真实验收均未关闭。

首次全仓 `npm run check`：630 TS + 1105 Python 通过（含当时 53 项行为测试）。原日志 `evidence/check-first.log` 本地保留。随后本地独立审查发现 P1 常量 create 幂等问题和 P2 完整证据缺测，原不通过报告及处置见 `local-review-1.md`。已修复，61 项私有测试通过；旧全仓结果不充当修复候选最终验证。

精确交接/外审预约需求见 `docs/iterations/T06/interface.md`。本 base 缺失 AGENTS 引用的架构计划文件，已只读全文读取主 checkout 对应真实源；未复制至本树、未改保护源。当前等待修复候选本地独立复核及新全仓检查；指定双方外审尚未预约、未执行；未 push/PR/合并。

## 当前可恢复交付

阶段：`private_implementation_validated`。产品/测试/fixture/接口冻结候选为 **`4542c5521aa96e676ab000861a65394e525b1144`**，base 与实查远端 develop 均为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。

修复候选新全仓 `npm run check` exit 0：15 个 TS 文件 / 630 项 TS 测试，1113 项 Python 测试（内含 61 项行为测试），lint/格式/类型/构建/ruff 均通过。`npm run verify:sources` exit 0，12 个归档源一致。独立 agent 对同候选全部 8 个新增文件重新完整复核通过，原 P1/P2 逐项关闭，见 `local-review-2.md`。记录与源码/本地原日志 SHA-256 见 `evidence/validation.json`。日志原件本地保留，不冒充远程 CI。

仅自有新增路径进入产品提交，AGENTS SHA 不变且未暂存；未改 Store、worker、协议、语义/resources、公共契约、锁、main/preload/UI，未使用其他树的未批准实现。

待总控交接：T01 隔离运行与同事务消费/轨迹提交接口；T05/I05 真实事件后推理与 RDF 适配；T00 业务方法及错误/权限/取消接线；T09 批准公共基线；T07 资源与完整轮次；T08 实际 B-08。接口文档已给精确字段和边界。请按本精确工作树预约指定 ZCode/MiniMax 全新独立完整审查及集成队列；当前没有取得其时段，未操作审查应用。

本聊天 Goal 保持 active。纯算法本地通过不关闭 FR-600–604 父模块，也不关闭 B-01–11 完整集成门。未推送、未创建 PR、未运行远端 CI、未合并或上线；真实依赖批准后仍在本聊天完成接线、行为页面、原验收、指定双审和后续门禁，不等待整个 M0 才做可独立推进的工作。

## 继续推进：失败解释完整性（2026-10-21）

上一目标轮属于实质进展。本轮重新核验：工作树仍只有保护 AGENTS 改动，恢复 HEAD `45624671b8974bbe0a64c44d6eb64e092a151a67`；实查远端 develop 仍 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。公共指令新增的 storage.py 单文件交接只归 T01，不扩大本线权限；总控 execution-state 仍记 T00 为提案、外审资源由 I05 预约，T09 状态尚无批准公共基线。未采用其他线未批准实现。

实质补强 FR-602/603 异常解释：原非竞争动作错误只有通用位置，无法定位具体事件/行为/动作。本线新增分阶段私有错误证据、完成前缀与部分条件、丢弃编辑/动作轨迹、输入身份，并明确无 committed candidate/consumption。修复不可编码 Unicode 输入泄漏原生编码异常的问题。没有改公共错误码或跨端契约。

`uv run --frozen pytest packages/engine/tests/test_behavior_*.py -q` 新增后 74 passed（原 61 + 13 项失败解释回归）；首跑 72 项和最终 74 项原件分别本地保留。该实现变更使旧本地完整复核仅适用于旧候选；新候选须重新全仓 check 和完整独立复核，指定双审/真实依赖/全模块验收仍未关闭。

失败解释候选 `f3f652352a5814bee95a453f608f1dd2f2fc815a` 新全仓 check exit 0（630 TS / 1126 Python）但独立完整内审不通过：P2 事件头/载荷错误缺源位置、重复 ID 冲突无法区别投递项。原报告见 `local-review-3.md`。

已补 event_validation、原始 event_index 与合法 event_sequence；事件排序采用带源位置视图，不改变 E.1 执行顺序和消费身份。新增 9 项回归，当前 83 项行为测试通过。首跑 2 failed / 81 passed 的实现漏挂字段已修复，原件 `evidence/pytest-event-source-first.log` 和修后原件 `pytest-event-source-final.log` 均保留，未改预期掩盖失败。新实现/验收须新 check 与全范围复核；本线共享责任与未验集成边界不变。

## 最新固定候选与真实下一步

当前产品/测试/fixture/接口候选 **`e81cfc973d251b76d8b9537adae150e8d2f930af`** 已通过新的完整独立 agent 复核，见 `local-review-4.md`；此前全部 P1/P2 均关闭，不覆盖或改写旧不通过结论。

新全仓 `npm run check` 实际 exit 0：15 个 TS 文件、630 TS 测试、1135 Python 测试（内含 83 行为测试），以及 lint/格式/类型/构建/ruff。受审产品路径在完整检查和审查后与固定候选 diff 为空。新证据/源码及本地首败原件哈希见 `evidence/validation-e81cfc9.json`；原 `validation.json` 仅为历史候选记录。

已形成具体 T06-S1 外审和接线请求：`review-readiness.md`，列出精确工作树/base/head、完整自有范围、指定双方新完整任务的模型和报告路径、每个依赖拥有者需交付的具体接口。该文件是请求，尚无实际预约或外审任务句柄，未操作应用或推送。

本轮通过官方 `wait_threads(timeoutMs=0)` 核验总控原线程 `01a154de-843b-7a00-8a80-51ba1c0aebce` 的真实当前 turn `01a15bc8-732c-76f0-824b-dc2ae935c08b` 为 inProgress，cursor `a6fb72bc-870a-442e-8c5f-cb4caa4b7ecb:22`。这是活跃协调句柄证据，不是依赖批准或外审预约。下一步接收总控批准交接/时段，在本聊天完成真实集成、行为页、原验收、指定双审、CI/合并；完整 Goal 保持 active，未缩小成功定义。

## T09 固定输入交接后的必要适配（2026-10-21）

本轮检查发现 T09 已提交并明确开放 T06/T07 只读输入：内容 `51cdc0e9d138c98cdd4ace865074a71883657a68`，manifest `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`。独立兼容性审计核验全部文件/来源，明确旧 e81 的动作粒度/ID/完整 RDF 投影差距，见 `baseline-compatibility-audit.md`。这是新可推进交付，不是以自动续接添加无关核心范围。

本线仅完成该必要适配：native create.initial 保持一源动作，初始单值写参与竞争；封闭 ID 模板与显式通知 ID；event-only declare；固定数据只读加载/版本/哈希核验与有界 codec/DSL；完整未提交候选投影。无复制公共 fixture、无采用 T09/I05/I06 未批准 Python 执行器、无共享路径写入。九例完整集合/顺序 probe 已通过，人工推导明确 not-executed/formal_acceptance=false。当前 116 项自包含行为单测通过；仍须新完整 check/独立全范围复核后冻结。旧 e81 的就绪/Pass仅历史，不能用于当前工作区。

已收到总控预约转交 T06 的两指定审查应用资源；这不是新候选已就绪或已开审。按根要求收敛到本轮必要适配，不追加其他核心功能；待新产品/流程 SHA、完整 diff、source manifest 和 dirty 状态实际核验后才开指定新任务。UI 新增授权仅 apps/desktop/src/renderer/src/behavior/ 与 tests/unit/t06-*.test.ts，若推进须独立 child worktree/feature/agent，不能让本线待审范围漂移。

在安全边界全文读回共同指令新增原第九节及无桌面约束。实际共同指令 SHA `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880` 匹配；原第九节传达 SHA `1f57a08e909e9d49a6e2c2d6e7012beec3e22b8e3c9e8eacad22c84dfb2d4b54`、无桌面段 `5215df2ead4745e7d74f137c4fa6ac837a54114590b5dee2d83cd16bb728551d` 随总控消息全文接收。保持原 Goal/分支/归档/指定门禁；无额度告警，不调用重置/付费/API；无排队 GUI/e2e/native/HMR。操作政策补充本身不触发产品重审，本轮重验是因为实际适配实现/验收变化。

567ab48 新全仓检查实际 exit 0（630 TS/1168 Python），固定九例 probe再次通过，但独立完整审查不通过，发现2项P2，见 local-review-5.md。已仅修本轮必要边界：投影复验展开后所有RDF身份；动态initial解析补字段索引。新增6项回归，122项通过；旧567全check不算修复版通过。修复后继续新固定候选/全check/完整独立审查，不扩张其他核心范围。

收到并实际读回新 ZCode/MiniMax 默认权限政策及外审权限证据，当前 AGENTS SHA **78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759**，共同指令 SHA **df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4**。历史db/971快照保留。默认完全访问/始终授权不改变只读/指定模型/无桌面/逐次确认边界；实际审查会话模式仍须读回。本线未改配置或操作应用；已向UI子agent透传新全文文件及政策。

UI已实际独立启动：agent /root/behavior_ui，树 /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui，feature/T06-behavior-ui，base5f910b5；仅behavior/组件与tests/unit/t06-*路径。正式managed worktree工具因本聊天根非git返回Not a git repository后，用批准repo git worktree add创建，未切换主树或影响S1。子agent已实际回执身份/公共政策/技能全文，尚未报实现/验证通过，不把创建目录当作完成。

## 当前冻结交付 61396a5

必要 T09 适配两项 P2 已修复；产品/测试/fixture/接口固定为 **61396a598b2dffc1d3d2fd4660f9af1d5c93d266**。当前新全仓 check exit 0：630 TS / 1174 Python（内含122行为），lint/格式/类型/构建/ruff均通过。完整独立复核通过，报告 local-review-6.md，全部历史问题关闭，旧失败证据不改写。批准873固定输入九例全量比较再次通过；人工gold、not-executed/formal_acceptance=false保留。

新来源/验证/完整diff清单及日志哈希为 evidence/validation-61396a5.json；review-readiness.md已重写为当前完整12项产品来源和实际门禁。两份新成功probe输出与已跟踪完整payload语义一致，记录原始字节与规范化hash后清理重复输出；原完整payload及本地运行日志保留。

指定应用独占资源已由总控转交，但须总控实查新产品/流程HEAD与dirty/source manifest后派发；未启动指定任务、未操作应用、未push/PR/CI/合并。AGENTS仍保护未暂存。UI在独立child树实质实现，desktop typecheck首跑通过，其他验证与交付尚未收齐；不在本冻结范围。完整FR父Goal保持active，真实依赖/集成与最终门禁持续开放。

## 独立 UI 固定交付与接线差距

UI 已在独立树固定 **571b4d64120c8420d527f9fda2a3cb81bbd47d3f**（base5f，feature/T06-behavior-ui），仅 10 个授权新增文件。父线实际核验 7 项产品/测试/脚本 hash 和 11 份本地证据 hash 全匹配，当前仅保护 AGENTS dirty。实际全 check 651 TS（本线 21）/1052 Python 通过，真正 headless 交互和 1440/390 布局截图通过。已启动 /root/behavior_independent_review 对该固定 UI 全部 10 文件的完整只读审查，尚未收终态。

精确双端接线差距见 ui-integration-handoff.md：完整行为集合覆盖、exists/type 与真实推理、稳定事件 version/sequence 及 RDF/对象变更、源动作粒度、scope/run/消费事务、candidate 不升级提交、受限错误及取消终态等。App/bridge/Store/真实推理/资源/Agent/UI 原验收持续开放，不擅自写公共文件。S1 产品冻结不变；指定审查仍等实际合规入口/桌面时段，没有新任务句柄。

独立复核已实际终态：**不通过，3 项 P2**。完整原文 ui-local-review-1.md，负例工具 evidence/ui-571b4d6-negative-probes.mjs。实际运行 21 vitest 通过，并在 /tmp 重定位 headless 验证，未覆盖旧证据；内存负例复现：conditions 必填一项且无 always，不能表达批准 G-behavior 的 X/B-a/B-b 无额外条件；candidate 可夹带 applied 动作/recorded 通知并被显示；payload 的自有 **proto** 键被静默丢弃，不同内容被折叠。开发 agent 已全文读报告并实际确认三项，完整终态后才在自身独立树修复。修后新候选须必要验证和完整独立复核，571 原结论保留。

## 指定审查实际派发入口核验

总控已实际完成新候选派发门（T06-S1-controller-review-preflight.json，12source/完整diff/20raw一致、远端5f），并明确准许本聊天在预约入口派发。两独立完整输入及SHA已先提交 **11c7a9bb0288fab87e6cecefcbfccbd36d550684**，只追加流程；产品613零漂移。

实际CUA只读核验为mac target；ZCode现存I05终态显示GLM5.3最高/完全访问，但不是本线新任务设置证明。两审查应用为本机native，无隔离审查browser入口。没有click/type/Raise/任务创建；两新任务均无句柄，不能记已派发。当前AGENTS要求当前桌面操作前明确时段，已通过async向用户请求仅两审查应用短时操作，仍待实际回答；预约不等于解除桌面约束。完整入口记录 round-1/dispatch-entry-check.json。等待期间UI独立无窗口工作继续，不改冻结源或重测无变化产品。

总控再次明确 S1 优先后已即时回执具体限制：不是等待 UI 或再次预约；既有独占资源已生效，实际 CUA 仍仅本机 Mac 原生入口，无已提供隔离入口/明确桌面时段，故不能合规创建。ZCode/MiniMax 两任务 created=false、handle=null、当前新任务模型与模式均未验证。未使用 CLI/私有接口绕过指定 CUA，不操作 Codex denied。两冻结输入保持 11c7a9b 原件；仅政策与流程证据继续追加。

最新共同指南 b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39 与三生效 handoff 已实际全文读回并透传，UI agent 已回执；AGENTS78df不变，详见 operating-policy-ownership-update.md。旧 df090 外审输入保留，不因责任更新无变化重测或重建 Goal。
