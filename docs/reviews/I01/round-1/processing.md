# I01 Round 1 意见处理

受审版本：base e628f5e7b6c09e10e15644552a6171c4a9a3072e → head 6d8e4b3021b368661247c03c47f01e4d32ebf6e1。两项任务均实际完成、UI终态与完整MD已读回；报告原样保留，不改写任何一方结论。

- ZCode：任务 I01-R1-ZCode-GLM53-20261020-0015，UI最终标题“I01 S1 ADR-0002 存储spike对抗性审查”；GLM-5.3/最高；26分44秒完成；结论通过，6条P3允许延期。
- MiniMax：任务 I01-R1-MiniMax-M31Flash-20261020-0015，UI标题“审查 I01 存储与失效 spike 实现”；M3.1-Flash/xhigh；8分36秒完成；结论不通过，2阻断、4中、5低。
- 因MiniMax阻断未关闭，本轮不满足双通过门禁。以下是开发者处理决定，不替代下一轮模型对关闭状态的独立判断；GLM本轮通过不沿用。

## MiniMax

| 编号 | 决定 | 改动、依据与验证 |
| --- | --- | --- |
| F-01 阻断：旧快照迟到覆盖新当前 | 采纳 | publish在同事务复验真实依赖及projectRevision；旧快照只保存为historical，不能覆盖新指针。已有结果不因无关模型变更失效。新增 test_late_snapshot_without_domain_change_stays_history_and_cannot_displace_current，检查完整指针/状态/原因，非仅计数 |
| F-02 阻断：Unix resource破坏Windows | 采纳 | resource受保护导入，不可用RSS=null、rssAvailable=false且method明确；health惰性隔离探针导入。新增缺resource及禁止storage_probe模块的子进程导入反例，同时执行health；保持tracemalloc原始值。此处为本机模拟，实际Windows须PR CI核验，不冒称已实跑 |
| F-03 中：空/未解析依赖永不过期 | 采纳 | 依赖须非空且在输入快照定义、版本或已登记mappingState中可解析；facts:asserted为显式空项目范围。拒绝未知/非字符串键。D九行先登记真实定义再发布，不再依赖虚构键；test_unregistered_or_empty_dependencies_cannot_be_published及空来源映射回归。完整依赖集合的派生属于I03能力契约，存储登记校验不宣称能识别一切漏报 |
| F-04 中：定义级IRI/词法未校验 | 采纳 | 显式triples须完整subject/predicate/object、绝对IRI及规范RDF词法，定义references/单值列表形状一起检查；失败在commit内回滚整批。test_invalid_ontology_triples_fail_in_commit_not_later_graph_build及有效定义建图回归 |
| F-05 中：迁移故障证据单点 | 采纳 | 迁移hook贯穿事务前后；11个v1→v2点各做异常/真实进程退出，另4个v0点各两类故障。核对原数据/所有权/完整sqlite_master结构/格式版本和重开重试，提交后保持成功v2；原单点测试改为明确migration_mid，不含糊扩大范围 |
| F-06 中：当前格式开库也取写锁 | 采纳 | 已是v2直接返回，持锁写者期间新reader可打开读取；需要迁移时在事务锁内重读版本以避免TOCTOU。test_current_format_open_does_not_take_writer_lock及并发迁移确定交错回归。普通写锁/I/O错误的服务层结构化映射留I03 |
| F-07 低：提交后异常拿不到成功返回 | 部分采纳 | ADR明确必须另查marker对账、异常不等于未提交，不盲目重试；故障矩阵已验证标记与数据同事务。轮次新增同标记幂等，响应丢失后可取原快照。专用投递失败异常不在本项提前定义，I03/I04根据真实job/传输边界制定；进程退出本来也不可能靠返回异常携带标记 |
| F-08 低：墓碑重跑阻断/恢复未记录 | 采纳 | 文档明确修改和删除均为人工漂移，需新预览和单独确认，通过edits显式恢复managed_value后再重跑。新增墓碑恢复回归；不引入静默恢复或假称业务确认UI已实现 |
| F-09 低：单值并集语义/基线字段惰性 | 采纳 | ADR明确唯一执行字段是ontology顶层singleValuedPredicates，作用域全项目并集；G-behavior增加同一真实字段。提交也拒绝与既有事实冲突的新声明。properties.*.single只作定义说明，不冒称执行 |
| F-10 低：实现兼容规则未机器化 | 采纳 | 新invalidation-v2.json（schemaVersion2）保留D九行，单列implementationCompatibility与publicationPolicy；执行来源键从该契约读取，发布资格消费对应策略。实现升级/历史身份仍不生成领域staleReason；同版本无默认兼容复用 |
| F-11 低：错误面不统一/未知删除no-op | 延期并补文档 | 内部Python spike不提前实施I03/v2错误码；ADR明确Conflict/ValueError/KeyError/SQLite错误现状，重复pin/终态插入可抛唯一性错误，未知事实删除为可审计no-op。I03/I04统一受限错误映射，不能回传原始异常。该项原报告明确允许延期；跨运行round operation复用已随R2改为Conflict |

## ZCode

| 编号 | 决定 | 改动、依据与验证 |
| --- | --- | --- |
| R1 P3：operation/job类型 | 采纳 | commit强制非空字符串并拒绝bool revision；round维持字符串守卫并拒绝bool轮次；映射/源行身份形状一并明确。test_operation_and_job_identity_types_are_checked_before_write及revision/round/mapping形状回归 |
| R2 P3：轮次重试及跨运行复用 | 采纳 | 以全局round operation查询已有记录，同run/round/job/内容返回原快照，终态后也只返回已提交证据；不同内容或跨run复用Conflict，保持终态不改写。新增响应丢失后重试/跨run/内容不符/取消后对账回归 |
| R3 P3：净零事实过度失效 | 采纳 | 重复墓碑删除跳过；按提交前后事实终态内容决定facts:asserted，按owner事实与mapping定义净变化决定mapping键。手工/受管删除后原值恢复不失效；sourceHash真变仍推进映射版本。新增两组净零与真实变更反例 |
| R4 P3：迁移TOCTOU及锁错误 | 部分采纳 | 已修复当前格式写锁与迁移锁内重读，新增并发交错及故障矩阵；普通写锁竞争的裸SQLite错误按F-11延期到I03错误映射，文档明确现状，不假称已统一结构化 |
| R5 P3：映射循环重复查询/JSON解析 | 采纳 | owner IDs及项目单值集合在mapping循环外预取，槽位集合检查复用。功能回归覆盖多值/单值/人工冲突与来源替换；未实测性能改善，不给倍数承诺 |
| R6 P3：全量快照增长 | 延期 | 保留全量前后快照作为本spike正确性与撤销依据，继续保守保留历史；压缩/差分需真实规模、Q5目标及兼容性验证后评估。不以清理历史或省略证据降低增长 |

## 证据与下一候选

- 旧报告与原始Round 1 evidence保留，关联6d8e4b3；新验证写入 docs/iterations/I01/evidence/round-2。
- MiniMax报告概要一处写“14条测量”，其V9/第3.4节和实际evidence均为12条；以12条原始JSON与脚本循环为准，不修改原报告。
- 没有不采纳/私自降级其阻断项；F-01/F-02修复须由下一轮双方重新判断。所有实现、测试、配置及验收文档变化均将包含在新固定head中。
- 复审任务必须各自新建，重新核验精确路径、模型、思考，并给同一base→新head和同一套原需求；允许双方核对本处理事实和前轮问题，不互相披露下一轮结论。
