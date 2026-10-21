# 作者修订处置：r1 → r2（待独审复核）

原55720B/765515主稿及四配套已按原字节保存在revisions/r1/，snapshot-manifest逐bytes/SHA，ddbc99断言主稿匹配。本文记录作者处置，不自行关闭独审意见或登记方案通过；原意见由create_budget_review独立报告保留。

| 意见                                                     | 固定实际证据                                                                                                                         | r2具体处置                                                                                                                                                                                                                                                                                                                         | 状态       |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| P2-01 profile1未知namespace可合法存在/形似新字段不可冒认 | Store._definition只查已知键；原_snapshot_state仅canonical+_definition；原entityMetadata='legacy-note'可opaque，ddbc99/867eea静态补读 | §4新增profile1原opaque/coverage-unavailable、schema定位全当前及历史碰撞先界预检、任意形态碰撞有限拒升级原件不变，禁止全局strict误拒旧库或自动认证形似v1；profile-aware入口与升级激活界、包来源也列明                                                                                                                               | 待独审定点 |
| P2-02 _application失败回滚外ownership详情侧写            | JobStore:427真实except ownership后另BEGIN INSERT job_details，ddbc99全文                                                             | §7新ontology scope在except侧写前转固定私有冲突，不造detailRef、不落旧路径；无scope旧默认保留。§9精确writer delta、§10真实dump/trace矩阵补齐；已有Job受控状态交易与详情侧写分开                                                                                                                                                     | 待独审定点 |
| Job failure/cancel尾部预算                               | fail_job/cancelled_job/_finish_unsuccessful/_transition/_save真实DTO写；有run会写run_terminal，ddbc99/867eea                         | 接收前TailReservation最大合法DTO候选/SQL bytes及Wtail实际成本、最低262144且上界8MiB，64控制槽包含在总额度；业务过期/耗尽仍有限独立控制收尾。atomic changeset Job必须run NULL，异常run不进入未预算round terminal。startup reconcile另guard，无权恢复原写；active tail写准入，未知writer写前拒，显式申请并记录对旧业务启用期间的约束 | 待独审定点 |
| 正例算式/缺SnapshotShape                                 | Reviewer核Sort参数多1024造成每Helper+12288；源码snapshot shape逐payload parse及manual/mapped term，867eea                            | 明列SnapshotShape/IRI次数与成本，SourceBind额外项和tail不隐零；JSON按正文逐式重算，叫staticAccountedSubtotal，不叫已证整链上界。20/8组数、H/P与tail仅实施目标，必须实际旧callee计数和首全字段链正例后才能关闭可执行性门                                                                                                            | 待独审定点 |

profile升级碰撞拒绝不是永久删除FR：旧源仍按profile1可保真读取/导出；碰撞需要根另批准带原opaque/provenance/逐历史解释的保真迁移策略，本轮不猜。M真实写消费依赖S2同版本plan/proof/原确认链激活，不用M内部fixture token冒充正式成功。namespace旧→新改变/删除在Store原write gate也需同事务真实prepared proof，不能仅凭新payload合法绕低层保护。

额外显式约束请独审评估：新ontology ownership错误只返回私有finite reason，公开OWNERSHIP_CONFLICT仍强制detailRef，不伪造schema；active tail时未知旧writer需资源拒绝，否则可挤掉已受理Job控制headroom，故该调度/增长影响须root批准，不能声称无条件零旧行为变化。真实存储full/I/O仍可阻止终态，必须报告未收尾事实，不承诺必成功或安全重试。

本轮仍只文档/静态源码/AST/Git/hash/格式，未产品import、DB、测试、故障子进程或实际模型；未动任何产品/C1/C2/dispatch原件。新稿交原独审者实际触发定点复核，所有意见保持待审状态。

## r2 → r3追加：待独审定点

r2主71515B/21c163和当时三个配套已原字节快照在revisions/r2/，b26359核同，不改r1/独审原文。

- Terminal floor：F_terminal与一次S_start/C_cancel份额隔离，实际helper/probe/全部控制槽三份先算且合计≤64；重复cancel、重复start、幂等/非法失败先用独立有限retry读份额或入口拒，不碰F。唯一owner finalize单用票不受retry耗尽阻断，可用F直接核当前Job和执行一次合法终态；真实I/O尝试花掉的work不退款、不自动重试。尚需实现专项证明重复调用后F不变，不自称已运行。
- 嵌套savepoint：固定Store._transaction完整正文b26359确认异常会ROLLBACK TO+RELEASE，而成功RELEASE出错还需两步清理。外层入层前保最多3槽，内层最多4，phase最多16次总入层（不等于最大深度）/深度8，总phase封存63控制槽及16128work；所有真实控制语句计65536且不被业务额度/未知模板阻断。每层生成名/owner栈/token精确核同，未知caller交易仍拒。固定序列逐步尽力清理/保首因，真实I/O失败不假称in_transaction=False。
- 正例配套再加8个业务phase的控制工作129024，总staticAccountedSubtotal63854272<67108864，tail的控制已在原4MiB示例内不双计；仍非真实完整body/组数/次数证明。矩阵补内层耗尽/未知模板完整清理与terminal floor隔离。

以上均作者具体处置，等待create_budget_review实际复核；没有产品/DB/测试运行，也未改其他方案或产品。

实际交review：作者已向root交r3身份/改动行；followup_task(create_budget_review)真实返回agent thread limit reached，live列表为root/create_core_review/dispatch_plan_author/store_interface_audit。故该次未触发独审，已报root调度，不能登记r3复审通过；等待真实独立结论再冻结。
