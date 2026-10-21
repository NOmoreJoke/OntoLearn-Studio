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
