# T11 全新指定审查准备：独立文档 preflight

2026-10-23。独立 agent `/root/t11_independent_review`。

结论：本次固定准备包未发现实质缺口，可供总控接收和后续协调派发。此为静态准备内审，不是指定模型工程审查、实际应用任务创建、设置读回或 Pass；不授予 GUI、API、发布或其他新执行权限。

## 固定输入与边界

- 准备提交：`6e63e078a4f0923a6ee3d7ade9c1a4ba988494f7`，只读主树 Git 对象，未 checkout 或修改主树。
- 受审候选及两 review HEAD：`036d7172ddba8502fe81e6e7ce375ce09ef7fa1c`；受验实现/测试：`33894063fcf17bc865f4c91556a8ca01845812e7`。
- 完整阅读准备包 15 件中的共同提示、两角色封面、README、manifest、roots、setup 与四份日志；两份 892 条 source-setup 逐项解析并核对 Git 和实体 hash。未重复阅读完整源码正文或重做实现评审。
- 仅做文档/固定 Git/文件字节与元数据核对，未运行测试、构建、安装、产品、collector、数据库、GUI/native、网络/API或模型任务。不读本轮活动审查意见、状态、全局应用资料或密钥。
- 唯一新增文件为本报告；本审查树 AGENTS 政策修改保持未暂存。

## 核对结果

| 项目               | 实际静态核对                                                                                                                                                                                                                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 准备包索引         | preparation-index 的全部 14 个 payload 逐项 bytes/SHA256 匹配固定 Git 字节；index 明示 excludesSelf，无自哈希循环。                                                                                                                                                                                    |
| 共同正文和角色提示 | 两份 full-prompt 均以完整 25780B 共同正文为精确后缀，SHA256 为 `ce5d35a8318d3269409230560e23c78b203c5d3912db3feaa84caca2cc3f5b16`；差异仅角色封面。共同正文全文阅读，内嵌最新 AGENTS 与两树实体政策字节完全相同。                                                                                      |
| 指定身份           | Z 封面为 GLM-5.3 / 最高(max) / yolo，M 为 M3.1-Flash / xhigh / bypassPermissions。两方分别指定唯一物理 cwd 和自己的最终 report/review.md；尚无实际 task/session/turn/settings 事实，没有把准备值当实际收据。                                                                                           |
| 全范围 manifest    | 56 个 requiredFiles 全部 bytes/hash 匹配 036；集合恰为 sourceGroups 去重并集。原 25 产品路径和原 8 流程路径分别与旧 round-1 固定 manifest 完全匹配，25 也匹配 base5f→product7d28 Git 差异；本轮 23 路径匹配 repairBase692→036 完整 Git 差异。两 collector、PE helper、两专项测试及全部验收文档均包含。 |
| 固定交接身份       | deliveryIndex、finalOwnerMainReport、finalOwnerVerification、independentImplementationReview 的精确路径/bytes/hash 全部核对 036 字节一致；未把准备 manifest 当生产 TRUSTED_FREEZE 或第二产品基线。                                                                                                     |
| 历史意见/失败继承  | 显式包括上一轮两份完整原报告、收件记录、18 项矩阵/计划及两代 raw；要求逐项覆盖与处置，M 原 NotPass、高1/中3/低8及 Z P4 六项保留。首38缺独立完整 raw、后续48归档、本轮14日志和首败2项/failed full/格式首败边界清楚；不以重跑造原首失败。                                                                |
| 两棵源码实体       | 两树各 892 个受控文件与 source-setup 逐项比对 mode/Git blob/bytes/Git SHA256/physical SHA256/equalsGit；均为 891 个等 036，唯一 AGENTS 政策差异 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。HEAD 均为 detached 036，状态仅 AGENTS M 和本方 runtime 未跟踪增长。                |
| 本方 runtime 副本  | 两方 metadata/setup.json、source-setup.json 分别等于归档；input 只有自己的 full-prompt.md、共同正文、handoff-manifest.json，三者均匹配固定准备 Git 字节；未含 peer 当前提示/收据。四份 raw setup 日志与归档副本一致。                                                                                  |
| 独立环境           | node_modules 和 .venv 都非 symlink，实体目录 inode 分别匹配 roots 记录且双方不同；tmp/raw/report/metadata/input 目录分别存在于各自根。未使用或探查报告内容。                                                                                                                                           |
| Setup 证据         | npm 日志为离线 ci、ignore-scripts 的依赖安装输出，警告保留；uv 日志为本方根 editable 依赖 setup。setup JSON 各记录两次 exit0、UV_OFFLINE=1/frozen。该包准确称环境准备，未冒充产品测试/构建、Electron postinstall 或真实功能通过；本审者没有重执行安装或认证过去进程的外部行为。                        |

## 执行与独立性边界

共同提示保留原 57 P0、G50/唯一17文件、1000轮/每轮1000实际触发实例动作、完整八步80%、双向 G.6、恢复/回退/来源、签名/渠道、真人/模型、CI/正常合并/远端等全部父门。owner 的 109/739/1052、四探针及 oracle actual 均与亲跑/真实产品证据区分；Mac 仅 bash-n/静态、Windows PowerShell 与目标运行未验如实披露。

未来实际获派后允许按疑点使用既有普通检查、受控 Node/Python CLI、worker 和临时 SQLite 原 suite，不以 child/SQLite 关键词泛禁，也不机械重跑全部历史；同时禁止扩张 e2e/install/package、真实 collector/native/凭据/签名/API、新 native caller/producer、压力/内存及 SQLite 损坏 HOLD 等票。F01/F16/Q5 不代答。缺依赖/被 HOLD 的具体调用须报根，不把所有检查泛暂停。

两方明确禁止读取 peer 本轮 prompt/receipt/report/state/metadata，即使位于本方 Git 或索引；范围等价由 owner 事前核，显式历史两报告允许全文处置。只写本方 runtime 报告，metadata 生长不删/ignore/exclude 求绿，不修改实现、测试、配置、锁或旧报告。真实任务的模型/effort/permission/cwd 仍须创建后读回，文件存在不作模型完成。

T05 与后继 helper e93 是准备包记录的最新根调度；本次未扫描或独立认证活跃 GUI 队列。036 handoff 中 T03 明确作为当时历史，准备件未借此申请/消费 T11 创建票。后继须总控明确接收并协调实际创建，分别开两个全新完整任务，不能续旧 completed session 或只做 18 项 delta。

本报告只确认上述固定准备材料及被授权实体的静态一致性；不关闭原18项，不改变 M NotPass 或双指定模型/真实发布门。
