# T09-S1 round-1 冻结提示准备独立审查

结论：**当前准备范围通过，无未关闭阻断问题。** 双方提示、输入清单、历史索引与政策快照足以表达同一完整 S1 候选及其真实证据边界。本结论仅是静态准备审查，不是指定 GLM-5.3 / M3.1-Flash 的产品外审结果，不授予任务创建、执行租约、合并或父功能验收。

审查日期：2026-10-22（Asia/Shanghai）。审查树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines`。本次仅新增本报告；未运行产品测试、构建或浏览器，未调用 ZCode / MiniMax，未恢复父 Goal。

## 固定对象与输入完整性

| 对象 | 固定身份 / 核验结果 |
| --- | --- |
| approved shared base | `5f910b52c69d86a1076b2032e5d3c63e715947f3`；tree `0a23f708a3d59f3e2a0353d6f069169ff8e26b3f` |
| S1 产品候选 | `76596656908ed84e577e8202a602e3256d5febcc`；tree `8b646570108026a8deabe8330c548cab0280122d` |
| 既有流程证据 / 当前 HEAD | `d96924e715a1b2139a75b70aea40fc30ae1129fe` |
| 本轮 manifest | `input-manifest.json`，42846 bytes；SHA-256 `11171ff00c9ef67ad11dc55ab80384ad694e3219282dbeb654e4677a0223c774` |
| 完整产品 diff | base → product 的全部 **55** 路径与清单逐项相同，未缩为 UI 子集 |
| 产品源码、数据与测试 | 清单中的 **32** 路径逐字节等于 product commit；当前工作树无这些路径漂移 |
| 最终输入条目 | **106** 项：55 product-diff、42 existing-process-evidence、1 approved-prd-context、8 frozen-round-input；全部 bytes / SHA-256 正确，有 Git 来源者逐项核对 commit 与 blob |
| 固定 fixture | manifest SHA-256 `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`；内嵌对象与 product 原件相同，17 输入 hash 全部吻合 |
| PRD | 清单绑定完整原文 SHA-256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` |

JSON 无重复键，106 条角色 / commit / 路径组合唯一。新增全文登记快照使初稿的 105 条增加为 106 条；并非新增产品范围。manifest 本身与本报告不构成自引用条目，后续 freeze receipt 和过程提交尚待实施方生成，不能在此提前声称已冻结提交。

双方提示各 107 行，逐行比较只有标题、模型设置声明和各自唯一报告路径三处不同。其余范围、核验义务、限制与结论要求一致。双方完整提示、历史索引与相关快照已实际读取；本次检查采用静态 Git / JSON / hash / gzip / 链接核验。

## 政策、任务身份与相互独立

已实际全文读取 `inputs/agents-snapshot.txt`（15852 bytes，`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`）及 `inputs/common-instructions-snapshot.txt`（17891 bytes，`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`），包括原第九节、无桌面约束及最新责任边界。后台路线快照为 `9a2d722dc86c64d66929cadd12631cc85042bdd820aba9ec76de882fa3ed5de4`。三份快照与各自当前来源相同。

提示明确要求新建两个独立完整任务，分别使用 GLM-5.3 / max / yolo 与 M3.1-Flash / xhigh / bypassPermissions，并从真实 registry 和每个任务实际读回 provider、model、思考等级、权限、task/session ID、正文接收与原始终态；不可观测者记“无法验证”。这些仍是未来执行要求，本次未验证实际任务设置，也不存在可据此宣称的指定模型通过。

双方只能写各自 `round-1/zcode-glm53.md` 或 `round-1/minimax-m31flash.md`，禁止读取或传递对方本轮提示、报告和意见；不得改产品、测试、配置或其他流程文件。未来独立工作区的映射须另附可核验回执，保持原提示字节。候选变化须重新完整双审，不能用旧内审或另一方结论代替。

当前 `taskState` 为无真实外审任务、无 T09 lease、无 task ID、无工作区映射。后台路线明确 T06 是唯一恢复 owner，T09 不继承其租约；准备文件不能自行启动任务。官方后台路线、无 GUI / Electron / native / HMR / focus、无凭据提示、无付费或额度重置、无产品与共享源变更等限制在双方提示中保持一致。默认权限模式不扩大本次只读职责。

## S1 范围与证据措辞

提示包含离线课程 / 术语 / 四级提示 / 迁移题、固定输入与完整预期、Python reducer、reset / seed、真实批准 I04 的有界基础设施测试、独立 learning 页面及其纯测试 / headless 组件测试、全部交接和验证证据。PRD 读取范围含 FR-003、FR-100–105、9.4、11.2、12.1 与附录 C / D / E / G。明确排除后来 stage 原型及组合，不能借 `12699cc` 等后续实现补本轮 S1 能力。

历史索引保留 CONTENT-01–05、INFRA-01、UI-01–05、DOC-01–02 的问题与关闭依据，同时要求本轮审查重新判定；UI-04 准确区分修前静态推导与修后独立探针，没有声称修前独立运行。首失败和中间记录未被最终通过覆盖。

已核对当前最终日志 `npm-check-ui-final.txt` 的 664 Vitest / 1094 pytest 通过尾段及摘要，log SHA-256 为 `210d3d9bc7254e059f9bc031988226f946251f9d359a577b8a54470a996241e5`。18 学习纯测试与 16 显式 headless 的归属按既有同版摘要保留，本次未重跑。另将 12 份历史 gzip 解压至内存，逐份核对压缩 SHA、原始 SHA 与原始字节数，全部吻合。准备文件内现有 Markdown 文件链接核验无缺失目标。

默认未设 `T09_HEADLESS_UI=1` 的 skip 不算浏览器通过；显式启用而 runtime 不符属于 launch 失败。截图 viewport / 文件尺寸分别表达，sandbox 只陈述 launch 配置及成功，没有外推当次 argv、OS 状态或 binary hash。Synthetic callbacks / SyntheticTools、真实 RDF 探针、真实 I04 基础设施与业务领域输出各自分明；`test.atomic` 不代人类业务确认，固定 expected 不代真实领域结果，历史错误码和通过数量没有跨候选套用。

保留的父缺口包括实际领域工具及多阶段证据契约、T01 受信持久与跨 attempt 辅助账本、正式 bridge / App 与生命周期、课程资源入包、T08 / T10、平台 / native / CI / 真人验收等。G-list-02 的 exactFile / exactPointer 不是完整 round DTO 比较器，A-10 固定反例集不是完整指定 Agent 评估集。提示和索引未把这些门登记为关闭。

## 本次发现与关闭

首次核验发现：`operatingSources` 的登记全文 hash 为旧值 `1b9b0c…`，当时 live 来源为 `44b5ab49…`；T09-S1 摘录行始终逐字存在，未发生产品或子阶段范围变更。已先报告实施方，未自行改输入。

实施方随后将全文来源定位刷新为 `44b5ab49eb8ef1e40f83913fd2da8f169f9267eb9d455b5e294d18acbe823b55`，新增原字节 `inputs/service-stage-register-snapshot.txt`，更新摘录头部与对应清单项，并明确聚合登记后续可变、冻结摘录不随之静默变化。复核全文快照 / live 来源 / manifest 的 SHA 相同，T09-S1 行逐字命中，106 项摘要重新逐项通过。该来源可恢复性问题已关闭，无需产品重测。

最终观察到的 tracked 工作树差异仅为已存在的 `AGENTS.md` 政策覆盖，本次未写它；32 个产品源码 / 内容 / 测试路径均与 765 固定字节一致。本报告完成后仍须由实施方生成 freeze receipt、提交过程材料，并等待正式租约与指定双方新任务的实际完整终态；准备通过不替代这些步骤。
