# T09 私有多阶段证据绑定独立内审

2026-10-21，Asia/Shanghai。

## 结论与候选身份

**固定候选的私有只读验证器范围通过独立内审；发现的两项 P2 已关闭，无未关闭阻断问题。**本结论不是公共 stage 契约批准，不代表真实领域检查、学习完成账本持久化或正式接线通过，也不替代指定双模型外审。

- 审查者：T09 独立 Codex 子 agent `t09_prd_audit`。
- 当前工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-stage-evidence`。
- 分支：`feature/weekly-t09-stage-evidence`。
- 本地恢复 parent：`74b17a43fd51b0fa89d810c664d185583a140e48`。
- 实际批准 shared base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 固定受审提交：`12699cc0f536f5875e8b021349b58c2c954145cc`。
- tree：`813af592a58396bf0a90a7f9f22076a5e5862266`。

定稿前重新读取 HEAD/tree；受审三个文件从该提交到工作区差异为空。仅在新树写本报告，未写旧 `T09-learning-baselines` 冻结树、共享实现、测试、配置或总控文件。

已在安全边界全文读取最新公共指令，实际 SHA 为 `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`；本树 AGENTS SHA 为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。理解并遵守 T01/T03 新共享责任；未消费其未批准实现。未重建 Goal，未启动 GUI、Electron、native、HMR、外审应用、焦点、凭据、外发、付费或额度重置操作。

## 范围与方法

全文审查：

| 文件 | SHA-256 |
| --- | --- |
| `packages/engine/src/ontolearn_engine/learning/stages.py` | `08fd02db01aea7a31806775c5b077efd70f431b5a10da753c72cd7925e4e3955` |
| `packages/engine/tests/test_learning_stages.py` | `8cda15cf6656ef5deae6c8530b1f14cde3eaac208b5fb03452fb853bba1cc855` |
| `docs/iterations/T09/stage-evidence-contract.md` | `637daea093465952aab800e329317f31514325285077850b81589e5cdd1e4ce7` |

需求依据为 PRD FR-006、FR-102/104/105、附录 D、G.2，以及既有 T09 多阶段交接。额外只读检查本树批准 I04 的 `JobStore.result_get`、canonical result/job/page 和相关测试助手，以核对兼容性；未重新探索整个 UI。

方法为静态阅读、针对空 root 版本问题的修前与修后独立纯函数探针、逐项复核开发线负例及完整日志。未重复运行开发线正在执行的专项、完整检查或浏览器套件。独立探针使用新树自己的 `.venv`，实际导入位置位于新树 `packages/engine/src/ontolearn_engine/`。

## 已关闭问题与证据归属

| 编号 | 严重度与修前问题 | 证据与处置 | 结论 |
| --- | --- | --- | --- |
| STAGE-01 | P2：`StagePlan.root_input_version` 未校验，可为空；`plan_id` 原来仅检查真值，不能保证文本身份 | 审查者修前独立探针将根版本替换为空字符串，`bind_stages` 仍返回 receipt。固定版 `_plan_valid` 要求两者均为非空、非空白 str；新增两个字段各五种空/错误类型负例。修后独立探针实际得到 `invalid-plan-identity` | 已关闭 |
| STAGE-02 | P2：quality 前后阶段测试仅改 task 标签，仍使用 query 结果和能力，未验证 canonical validation 形态 | 审查者静态发现，未声称执行过修前 validation 探针。固定版 `validation_reader` 使用 `kind=validation`、`validation.execute`、`name-required`、对应依赖/参数和违规/修复后 rows；新增同快照 query 替换拒绝。开发线最终 80 项专项及完整检查覆盖修后版本 | 已关闭 |

完成回执方案是开发线提出、经独立审查收窄的兼容性设计，不记为上述两项独立缺陷的修前运行复现。I04 对受事实变化影响的旧结果实际返回 stale，不能要求它重新变成 historical。固定版保留该真实状态，通过单独完成证据绑定连续课程的历史前置阶段。

## 信任边界与需求核对

调用方仅提供 Context 和有序 stage/result 引用；Plan、结果、job、分页、完成回执及祖先关系均由 owner 的只读视图提供。模块没有 Store 写通道、IPC/registry 注册、学习状态提交、辅助历史清理或模型调用。

- Plan 限定实际终态 context、root/terminal 快照、有序 slots、输入与完成账本序号、精确选择签名和能力。stage 引用缺失、未知、重复、重排以及 result 重用均被拒绝。
- 每阶段精确匹配 plan/version、project/task/attempt、epoch、root、stage、输入版本、快照和序号。成功 job 与 result 的身份、resultRef、范围、参数、依赖、实现及定义相符；存在 result 不等于 job 成功。
- `StageCompletion` 经独立 `view.completion` 读取，使用可定位 UUID，并与同阶段账本身份及输入/完成序号匹配。当时 canonical 完成结果必须 current、无 stale、payload available；当前实际结果除 state/staleReason/historicalSelectionRequired 外全部字段严格 JSON 相等，不能仅检查部分 signature 或靠 createdAt 推断完成。
- 历史 slot 保留实际 canonical stale 原值，同时返回原始完成回执；不将 stale 改贴 current/historical。终态仍要求实际 current、无 stale，并绑定聚合当前输入。该私有收窄约定只覆盖连续课程，不自动定义所有事后选择历史快照的学习路径。
- 每阶段从 null 游标获取完整分页链，精确匹配 binding；缺页、驱逐、重复游标/行、错顺序和换绑拒绝。完成回执不能替代缺失载荷。返回 rows 来自实际分页，不由固定 expected 构造。
- root→阶段→terminal 及相邻阶段均核验同项目祖先关系；同快照需 Plan 明示。输入选择与完成序号严格交替，不凭 revision 大小推出祖先或时间顺序。
- 一致读视图结束后再次核完整当前 Plan；`require_current` 用于消费前复核。真正持久登记必须由 T01 在其 CAS 事务中与实际当前输入/attemptEpoch 检查原子完成，私有函数不自称解决跨事务竞争。
- Receipt 只声明绑定成立，没有领域 passed、操作完成或独立迁移成功字段。测试明确展示绑定正确的实际 rows 仍可能不符合领域预期；后续完整领域比较和 T01/T08 辅助账本仍独立必需。

Plan 的根输入版本与快照真实映射、完成回执不可变持久性、阶段归属及账本序号的真实性均是 owner 的前置责任。此原型可拒绝不一致数据，但不能证明一个会伪造整个一致视图的 resolver；文档没有将该信任假设写成已完成产品能力。

## 真实 I04 探针与合成测试边界

两项实际 JobStore 探针真实执行了测试 read 发布、事实编辑、旧结果失效、当前结果读取和 result.page，再将原始 canonical DTO 交给 binder。测试断言：前置阶段当前 result 仍为 stale，完成时保存的原始结果为 current，返回分页保留实际内容，binder 没有改写存储结果；之后再改输入会使 `require_current` 拒绝。

其中 `test.read` 只发布给定 rows，不执行 SPARQL 或 SHACL；两个探针均为基础设施兼容性证据。完成 ledger 与 Plan/祖先接口仍由测试内存对象承载，不能算 T01 持久账本、实际领域工具或产品恢复通过。canonical validation 正反例属于私有纯绑定测试，同样不等于 SHACL 执行通过。

## 验证原件与历史失败

最终完整日志已全文读取：[npm-check-stage-final.txt](evidence/npm-check-stage-final.txt)，SHA-256 为 `842822b3029753ec9a226ca79dedb184b11780b270e95a5e0d20299b240fe9a9`。开发线进程 `91637` 提供实际退出码 0 终态；审查者没有重复启动完整检查。

- lint、Prettier、TypeScript、三段构建、ruff 检查均通过。
- Vitest 648 项通过，16 项浏览器测试明确 skip；这些 skip 不计浏览器实跑。本轮仅新增 Python 验证器，原 S1 UI 源码/测试未变，未无变化重复 headless。
- pytest 1174 项通过，包含最终 80 项 stage 专项。[stage-reviewed-pytest.txt](evidence/stage-reviewed-pytest.txt) 另保留专项 80 项通过原件。

历史原件均已读取并以 gzip 无损归档保留。原始/归档 SHA-256 与原始字节数见 [stage-evidence-verification.json](evidence/stage-evidence-verification.json) 的 `priorLogs`；定稿时已核对压缩件及解压内容摘要与字节数。最终完整日志与 80 项专项日志仍为 plaintext。

- [stage-first-pytest.txt.gz](evidence/stage-first-pytest.txt.gz)：3 失败、49 通过；测试预期错误码晚于实际先触发的 job/canonical 守卫，不能写成该轮通过。
- [stage-second-pytest.txt.gz](evidence/stage-second-pytest.txt.gz)：中间版本 53 项通过。
- [stage-final-pytest.txt.gz](evidence/stage-final-pytest.txt.gz)：引入完成回执前的中间版本 57 项通过，不能代表真实 stale 路径已验证。
- [stage-completion-first-pytest.txt.gz](evidence/stage-completion-first-pytest.txt.gz)：1 失败、55 通过；根快照测试修改未同步完成回执，先触发 completion ledger 拒绝。
- [stage-completion-second-pytest.txt.gz](evidence/stage-completion-second-pytest.txt.gz)：2 失败、67 通过；实际 I04 探针错误猜测 marker 的 before/after 字段名，按批准源码修正为 before_snapshot/after_snapshot。
- [stage-completion-final-pytest.txt.gz](evidence/stage-completion-final-pytest.txt.gz)：中间版本 69 项通过。
- [npm-check-stage-first.txt.gz](evidence/npm-check-stage-first.txt.gz)：中间完整检查 pytest 1163 项通过；随后新增两项 P2 的修复与负例，另以最终 1174 项结果验收。

这些失败与中间通过均未倒写为最终成功；独立发现、开发线运行和修后复核按实际证据分别记录。

## 剩余门禁

未批准公共 stage 契约；未接入 LearningService、UI、IPC、registry、真实领域适配或 Store。T01/T00 仍须提供完成时原子持久化、不可变 ledger、正确 root/输入/epoch 恢复、实际 ancestry 与一致读、消费 CAS、分页/pin 生命周期及固定错误映射；T08 辅助来源与 T10 导出仍单独验收。

本次没有运行或证明包内资源、Electron/native、平台、真人学习验收或生产状态。指定 ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh 的同版双审、后续推送/PR/CI/合并与远端核验仍按总控门禁执行；旧 S1 冻结审查不因本私有原型自动关闭或改变。
