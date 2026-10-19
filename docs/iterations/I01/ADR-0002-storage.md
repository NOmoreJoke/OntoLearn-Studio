# ADR-0002：事务源真相与固定输入派生视图

日期：2026-10-20。状态：S1 spike 已实现，采用决定等待本候选指定双模型审查及集成门禁；不表示 M0 或产品存储格式已发布。

## 决定及边界

SQLite（外键开启、FULL synchronous、BEGIN IMMEDIATE）是唯一可变项目源真相。正式写入只经 `Store.commit`，RDFLib 的内存图由不可变规范快照重建，不能反写数据库。此次不引入第二份可变三元组真相。

`projectRevision` 用于正式 ChangeSet 乐观并发；实际领域依赖使用独立版本向量；执行语义、引擎和依赖锁标识用于实现隔离。`kind` 是业务结果定义身份（例如 `query:Q1:asserted`），调用服务必须同时记录真实数据范围和全部实际依赖。派生结果发布必须声明非空且在输入快照中已登记的依赖（空项目也有显式 `facts:asserted` 范围）；存储层不猜测遗漏的业务依赖，完整依赖集合由 I03 能力契约强制派生。当前 API 是 Python spike 内部接口，未暴露 IPC、Agent 或 UI。后续应用服务负责业务 schema、预览及确认，不允许跳过这些步骤直接使用存储接口。

## 最小格式 v2 与接口

SQLite `user_version=2`，格式 1 是本 spike 迁移输入样例，没有发布兼容承诺。

| 表                                       | 责任                                                                                                         |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| projects / versions                      | 正式 revision；按实际依赖键的领域版本                                                                        |
| definitions                              | 本体/映射/约束/规则/行为/场景/查询/模型配置，规范 JSON；后续服务负责有限语义验证                             |
| facts                                    | 稳定事实记录、绝对主语/谓语 IRI、独立 RDF 对象词法、owner/source_row/managed_value；人工删除受管事实留下墓碑 |
| mapping_state                            | 最近成功生成的映射依赖版本；源 hash、身份规则或定义修改后，旧受管数据可显示过期                              |
| commits / commit_evidence                | operation/job、计划摘要、正式提交版本，以及同事务前后快照作为 Diff/撤销依据；此次不实现产品撤销 UI           |
| snapshots                                | 内容寻址、完整不可变输入；含定义、事实、来源、映射状态和版本                                                 |
| results / result_state / current_results | 可重建计算载荷、依赖/来源与过期码、按项目/结果定义/实现来源隔离的当前指针                                    |
| result_pins                              | 保存报告固定的结果载荷，缓存回收跳过                                                                         |
| runs / rounds / run_terminal             | 隔离运行输入/配置/实现来源、逐轮完整状态及 operation/job、一次性终态；无正式事实写入                         |

新建事实 ID 是初始三元组规范数组的 SHA-256；对象必须等于 `term(value).n3()`，统一 xsd:string/语言标签及字面量词法后派生身份，非规范别名拒绝提交；显式 `edits={factId:object}` 保持记录身份与映射基线：编辑后 ID 仍是初始内容摘要，不再等于当前值摘要；墓碑同样保留初始 ID。新来源既不能占用该保留身份，也不能接管相同有效语句；冲突返回原 owner/source_row/slot/id。不同多值不因其他值的墓碑而被整槽拒绝，不能用新增事实暗中接管所有权。`manual` 只新增，`remove` 删除手工事实或为受管事实设置墓碑。映射计划是 `{id,rows:[{row,facts}]}`，由未来业务层预先校验与预览，不能称为 CSV 映射能力已完成。

所有共享同一事实的多来源支持均拒绝；不同事实的多值关系可并存。单值声明的唯一执行格式是 ontology value 顶层的 `singleValuedPredicates` 绝对 IRI 列表，作用域为全项目并集；`properties.P.single` 等描述字段不被当作执行约束。G-behavior 已显式添加可执行列表。提交时也检查声明与既有事实是否冲突，不能引入相互矛盾的单值状态。人工修改或人工删除（墓碑）的受管记录与 `managed_value` 不符时，重跑停止，保留映射/源行/slot 定位；没有静默恢复或合并接口。恢复路径是一个新的、预览并单独确认的 ChangeSet，通过 `edits={factId:managed_value}` 显式放弃人工值或人工删除，再重新预览/提交映射；存储 API 不冒充已实现确认 UI。整个计划的显式 definition `references` 必须可解析，事实与显式 ontology `triples` 均校验绝对 IRI、规范 RDF 对象和完整三元组形状，引用形状失败也回滚；其他定义 payload 的领域语义不由本 spike 猜测；完整附录 C 业务语义属于后续能力实现。

同一事务包括：基准复验、正式数据、所有权、版本、受影响结果过期、前后快照、operation/job 标记。提交前和事务中取消/异常回滚，提交成功后才收到取消或响应丢失，不能撤销已提交事实；必须另外通过 `marker(project,operation)` 对账；异常本身不能证明事务未提交，提交后投递失败不会返回普通成功值。I03/I04 必须以持久记录协调终态，不盲目重发写入。同 operation/job/计划重试返回原标记，不重复写入；身份重复但内容不同拒绝。

`start_run` 显式绑定项目状态快照，存储形状必须含非负整数 projectRevision、合法依赖键与非负整数版本向量、definitions/facts 列表和 mappingState 字典；校验还包括定义记录/JSON/显式引用、每条规范事实及其owner/源行/映射基线、映射状态与原因记录的基本存储形状；不按当前对象复算已编辑记录的初始 ID。轮次证据不是项目输入，start_run/publish 均以 ValueError 拒绝，跨项目仍为 Conflict，身份缺失仍为 KeyError。`commit_round` 接受已由未来 E.2 执行器计算的完整轮次，不实现行为或资源模拟。轮次状态须为对象，连续、最大 1–1000、单轮快照及提交标记原子；同 operation/run/round/job/内容重试返回原快照（终态后也只返回既有证据），不同内容或跨运行复用 operation 抛 Conflict。终态后拒绝写轮次。取消保留前轮，`progress` 零轮为 null，其余提供 runId/lastCommittedRound/snapshotRef。新运行必须显式传入快照，不自动续跑。轮次、运行输入和终态有 SQL 不可变触发器；正式提交、快照同样不可改写。

## 依赖与派生结果

唯一机器规则来源是 `packages/engine/src/ontolearn_engine/invalidation-v2.json`。D.2 前八行对应八类原因，第九行 model 的原因是 null；历史、失败、取消及实现不兼容均不进入 staleReason。原因记录 dependency、before、after，可多原因并存。规则明细及九行正反例见 acceptance.md。

发布结果时在事务内复验依赖，并要求输入快照 projectRevision 等于当前正式 revision；即使领域依赖未变，旧快照迟到也只保留为历史，不覆盖当前指针。读取结果显式区分 current/stale/historical。该保守发布策略比仅复验领域依赖更严：即使某 kind 首次发布，只要计算期间正式 revision 被无关提交推进，也仅为历史，该 kind 可能暂时没有 current；必须基于新正式快照再发布。已有领域结果不因无关元数据或模型配置变化被错误失效；这与“迟到的新发布不得回退快照版本”分别处理。替换推导只替换同业务结果身份的指针，断言与历史不变。仅改模型配置或无关项目元数据不会使领域结果过期。v2 JSON 将 implementationCompatibility 与 publicationPolicy 单列（都不是 staleReason）；当前实现默认隔离不同 engine/semantics/lock；没有未经验证的兼容版本复用。

`collect_cache` 只置空未被报告 pin、未作为当前结果的可重建载荷；状态、定义、来源、输入快照仍保留。过期而未固定的派生载荷也可被回收，条目、原因、依赖与输入保留，不能承诺过期载荷无限期直接查看；已被报告固定的载荷及运行每轮状态在不可变快照中，不属于这类可回收载荷。此 spike 保守保留全部快照，没有快照 GC；用户明确删除运行、产品报告生命周期和存储压缩留待对应业务，不伪称完成 FR-705 全功能。

## 迁移与恢复

v0 建立格式 1，再在同一事务升级 v2。v1→v2 增加 mapping_state、commit_evidence 和按实现隔离的当前指针。旧格式无法证明映射生成版本时写 -1，显示过期，要求重新检查/生成；不猜测已知。旧提交缺少前后引用时保持空引用，不承诺已有撤销依据。已为当前格式时直接打开，不取得迁移写锁；需要迁移时取得事务写锁后重新读取格式版本，防止两个 opener 使用旧版本做重复 DDL。迁移 hook 贯穿提交前、中、后，覆盖新建、回填、触发器、当前指针重建、版本更新及进程退出；失败回滚 DDL/版本及数据，重开可重试。提交后注入异常时格式已经成功持久化，重开不得倒退。未来格式拒绝打开，不静默改写。`backup(newPath)` 使用 SQLite 在线备份、禁止覆盖目标，可恢复全部当前数据和所有权；它不是带范围选择的 FR-1000 导出 UI。

## 测量与采用限制

真实 RDFLib 7.6.0 与 pyparsing 固定在 uv.lock。探针的 Unix resource 可选：不可用时 RSS 为 null 且 method/rssAvailable 明示，tracemalloc 仍记录；普通 health 惰性隔离探针依赖。合成图使用独立命名空间，18 / 180 三元组，固定 SELECT、稳定完整预期集合，分别保存快照加载、规范事实建图、查询及热重复的时间/内存原始值。数据/查询摘要、设备、库版本、种子、重复次数、OS cache 未控制的条件均在 evidence JSON。种子为固定元数据；生成器无随机分支。

这些小样本用于提前发现路线/打包错误，Q5 未定，不证明业务容量足够。此次仅承诺固定只读样例、规范事实重建及基础打包；完整 RDFS/规则/pySHACL、网络拒绝矩阵在 I05。无桌面/bridge 改动，不新增 renderer 能力。干净设备、无系统 Python、断网安装、签名与跨平台尚未验证。

## Round 2 接口澄清与保留限制

- `projectRevision` 对每个成功 operation 推进，事实/定义依赖版本仅在相应终态内容改变时推进；重复墓碑删除及同批删除再加回完全相同手工事实不产生领域失效。依赖是否完整仍须由后续能力契约约束，登记校验不能证明调用者没有漏报。
- history 的 replayable 只表达本 spike 对保存输入/配置/版本形状齐全的检查，不代表真实行为/沙盘执行器或重放功能已实现；当前产品正式能力仍仅 health。缺失或形状不全明确 false，后续还需核对实际执行语义支持与业务输入内容。
- 错误面保持内部 API 的现状：Conflict 表示基线/所有权/轮次身份冲突，ValueError 表示存储形状错误，KeyError 表示读取身份缺失；SQLite I/O/锁/唯一性错误可原样抛出（例如重复 pin/重复 finish_run）。移除未知事实当前为可审计 no-op，终态不可改写。I03/I04 统一转换为受限结构化错误，不向 UI 或模型转发原始业务异常。此处没有提前实施 v2 协议或错误码体系。
- 映射替换现为循环外预取 owner IDs 与项目单值集合，减少重复查询/解析；未测量性能改善，不作倍数或时延承诺。
- 完整前后快照和保守保留继续作为正确性优先的 spike 选择，存储随历史增长；Q5 未定，不宣布容量达标。压缩/差分快照留待真实负载与兼容性设计后评估，不能清理不可变历史来冒充优化。
- Round 1 原始验证保留于 evidence 根目录（关联 6d8e4b3）；新候选最终验证与打包测量单独存于 evidence/round-2，不覆盖原记录。

## Round 3 证据补强

Round 2 双方明确通过，但开发会话对照原 S1 退出条件，选择先关闭所有权定位及输入缺失标记缺口再重新双审：保留事实 ID 的冲突也可定位；项目输入形状由 start_run/publish/history 共用校验，既存不合格运行仍可查看但 replayable=false；轮次证据形状不齐同样 false。publish 的实现来源非字典统一 ValueError。完整能力依赖派生、业务输入/事件与规则版本语义仍由 I03 强制，形状通过不表示执行器已实现。

存储 G-base/G-behavior fixture 使用 JSON 定义与 urn:type 等描述谓词；它们的完整集合存储回归不是 rdf:type/RDFS/SHACL 执行验证。RDFLib 探针使用另外的 G-base 结构合成孪生（标准 rdf:type、独立命名空间），固定 SELECT 仅验证该孪生。两者身份不混用。G-map-empty 固定两行的 prepared mapping 新增完整四条类型/名称事实及来源集合和重复提交回归；仍未实现 CSV 解析/预览业务。

Round 3 最终检查、实际打包及原始测量单独保存 evidence/round-3；Round 1/2 原始报告与证据保留，不改写任一方结论。
