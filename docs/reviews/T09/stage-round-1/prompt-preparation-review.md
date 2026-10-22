# T09 stage-round-1 准备包独立审查

结论：**当前静态准备范围通过，无未关闭准备阻断。** 双方完整提示、manifest、验证映射、历史索引与政策快照一致，已贯彻“关键验收缺失不得给整体 Pass”。本报告不评定产品整体通过，不替代指定双模型外审，也不改变原型关键验收缺失或父 Goal 状态。

2026-10-22（Asia/Shanghai），审查者为独立 Codex 子 agent `t09_prd_audit`。实际工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-stage-evidence`，分支 `feature/weekly-t09-stage-evidence`。本次仅静态 Git / JSON / hash / gzip 核对及本报告写入；未运行产品测试、构建、服务、GUI 或模型任务，未修改 Goal。

## 固定身份与完整性

- approved shared base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- product：`12699cc0f536f5875e8b021349b58c2c954145cc`；tree `813af592a58396bf0a90a7f9f22076a5e5862266`。
- 直接 local parent：`74b17a43fd51b0fa89d810c664d185583a140e48`；继承 S1 product `76596656908ed84e577e8202a602e3256d5febcc`，不能把 local parent 记为批准 shared base。
- 当前固定 process / HEAD：`9a1baa74f2b6482106eb7c8090efef7f7ba065e2`；原验证与内审保存于 `e6519932b0b20fd1862dcd6f038a621fce8177f5`。

| 准备原件                    | bytes | SHA-256                                                            |
| --------------------------- | ----- | ------------------------------------------------------------------ |
| `input-manifest.json`       | 69466 | `267eb13144cd70b8b2cf3ad0f32f590173b21b6f59ac247c06dd7fa701112f15` |
| `zcode-glm53-input.md`      | 21362 | `46e00127c559763c9e71f7ebb4823eef71a40f3da71ff8386f20dec93b4eedf8` |
| `minimax-m31flash-input.md` | 21384 | `2801f823dbf55df65e71fe1836af567ec056940c7fdfb5101c0583d72c53bfcc` |

两份提示、manifest、`validation-and-history-map.json`、`verification-and-history-index.md` 及五份 inputs 均已读取。JSON 无重复键；168 条角色/ref/path 组合唯一，77 product-full-diff + 61 fixed-process-context + 21 approved-base-context + 9 frozen-stage-round-input 的 bytes、SHA 与已有 Git blob 逐项相符。映射中的 17 个固定引用与 Git 原件、manifest 一致。

实际 shared base→126 为完整 77 路径；local parent→126 恰为 `stages.py`、`test_learning_stages.py`、`stage-evidence-contract.md` 三文件。34 个运行源码/内容/测试及三个增量文件的当前物理字节均等于 126，product/base tree 与直接 parent 正确。61 个流程上下文恰覆盖 9a1 的全部 T09 iterations/reviews 文件，无漏项或额外路径。

新增的五条物理过程映射也已核对：handoff、learning-ui-verification、operation-policy-receipt、recovery、status 的产品 SHA 与 9a1 流程 SHA 均准确，实际物理差异集合恰为这五条。提示要求按不同角色的 commit:path 分别读取，不能以物理 HEAD 替换产品原件；未来独立工作区映射须另附不可变 hash，原提示不改。旧 S1 round-1 十一文件逐字节等于其 72aa 固定来源，本次未写它们。

## 证据与结论门

九份 stage 历史 gzip 已在内存解压，原始 SHA/bytes、归档 SHA/bytes 均吻合。首跑 49 通过/3 失败，完成回执阶段 55 通过/1 失败、67 通过/2 失败与中间 53/57/69、首次完整 1163 Py 的归属准确，没有倒写最终成功。两份最终明文原件准确对应 80 专项与 648 Vitest 通过/16 明确 skip/1174 pytest；16 skip 不计浏览器实跑，S1 原 664/1094 不代 stage 或 native 验收。本次只读原件，没有重跑这些命令。

STAGE-01 修前独立纯探针与修后拒绝、STAGE-02 修前静态发现与修后 canonical validation 测试的证据归属保留，要求指定审查重新判定；未把旧内审关闭当指定 Pass。设计回执仍只是 accept-design-alignment，没有 runtime adoption 批准。

双方提示要求全文审查三个完整增量及继承 S1 的课程、固定输入、reducer、七项 I04、UI 与必要批准 5f 上下文，明确不是新 S2、缩验收或新功能。内存 Plan/completion ledger、given rows、两个真实 I04 探针的局限和全部父门，在提示、映射及索引中一致表达：基础设施绑定不产生领域 passed、操作完成、独立迁移成功或持久账本证明。

结论门明确禁止把 T01 持久 ledger/辅助来源/真实输入与 epoch/祖先/一致读/CAS、公共合同、实际领域 adapter、正式 App/bridge/生命周期、资源入包/无模型离线、T08/T10、双 OS/包/native、真人及原 80% 标准、CI/合并/远端与 57P0 等关键缺失降为“不影响整体 Pass”的未来事项。确认必要实现或验证缺失须报告“不通过”；关键身份、来源或原件无法核实须报告“无法验证”。允许分项陈述已验证范围，禁止以“有界原型通过”或“有条件通过”覆盖整体缺口，并要求原样保留实际模型 NotPass/无法验证及终态。准备通过不预设未来模型结论，也不授权开发线将其改判。

## 独立任务与当前政策

双提示各 102 行，只有标题、指定设置和各自唯一报告路径三行不同。GLM-5.3/max/yolo 与 M3.1-Flash/xhigh/bypassPermissions 均明确是要求，须逐任务真实读回 provider/model/reasoning/permission、session/task、正文受理与终态；不以全局配置代证明。双方同固定候选各自完整新审，禁止读取或传递另一方本轮意见，只能写各自报告，不能修产品、提交或推送。完整全文报告与真实 terminal 均为必要收据，正文受理或草稿不算结束。

已全文读取 AGENTS、common、desktop policy 和 external permissions 快照，分别为 `de15f6ce…`、`567b6e70…`、`7b54d589…`、`feea1595…`，均与当前实际来源字节一致。两提示嵌入的第九节/权限段及 desktop policy 与快照逐字一致。当前非静默政策与内部短创建 lease 区分准确；本包无 T09 创建 lease、实际 task ID、设置读回或工作区映射，两份指定报告亦不存在。没有把准备授权扩大为模型任务、产品/浏览器/native/HMR/认证运行、付费或重置权限。

本次未发现须修改输入的准备缺陷。仅新增本报告；保护 AGENTS 的原政策覆盖保持只读。后续外层 freeze receipt、过程提交、实际工作区映射和指定双方真实任务仍须由原 owner 据实完成，不能由本准备审查推定。
