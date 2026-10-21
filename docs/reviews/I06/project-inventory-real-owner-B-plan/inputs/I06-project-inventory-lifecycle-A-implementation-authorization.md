# I06 A：保护清单与整组生命周期纯模块实施授权

2026-10-21。继续原I06会话的同一功能。固定docs方案1f3b053d8a69d1f7ddb1e29c143f648d910fe689、46365B/SHA561ec272c07f0c0f026c9aa17b717b99d3e110e31cb4ee45f0663254e9517443已由根全文读，方案和owner复核保持。仅实施§6阶段A；B真实仓库、C原生能力/VFS、D宿主/Store及E公开消费均未授权。根独立审查报告须实际接收并核后才发送本授权，不将本件存在当已调度。

## 新树、固定来源和唯一范围

从实际核验批准develop 5f910b52c69d86a1076b2032e5d3c63e715947f3创建独立树 /Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-project-inventory-lifecycle，分支feature/I06-project-inventory-lifecycle。不复制e2c/660/961产品、平台脚本、环境或任何未批逻辑；不整commit/cherry-pick。最新AGENTS15852B/78df2825…a759作为受保护操作规则未stage；common17891B/e437121a…b0全文及原第九节/无桌面约束继续。

唯一四个新产品/测试路径：

- apps/desktop/src/main/security/private-resource-inventory.ts
- apps/desktop/src/main/security/project-cohort-lifecycle.ts
- tests/unit/i06-private-resource-inventory.test.ts
- tests/unit/i06-project-cohort-lifecycle.test.ts

新说明仅docs/iterations/I06/project-inventory-lifecycle-A.md，证据仅docs/reviews/I06/project-inventory-lifecycle-A/。不得改index/engine/task-service/preload/renderer/canonical/依赖/锁/build/CI/既有model-gateway/guard/旧测试/Store。若确有编译边界缺口，先交实际错误和精确路径，不通过stub/skip/复制旧业务模块绕过。可使用5f已有工具链，依赖/输出/数据独立，禁止共享可变环境。

## 阶段A可证明的内容

这是自包含的main私有数据/状态模块，不读文件/目录、不解密、不调用Keychain/网络、不持原生句柄或打开SQLite，不执行通用FS callback，不导出生产首IO能力。使用合成metadata的测试仅证机制状态：真实owner供方、持久退役恢复和原生能力尚未接入时，实际应用全保护集合仍未知，不能由空constructor、缺席owner、模型失败、rendererUUID或safe布尔值得到生产complete。不得改961 contentIo unsupported或数据库保护策略。

完整性以明确有限、由可信main未来登记的owner集合和同一次进程/profileEpoch/revision观察为范围。owner注册/观察/transition/receipt需真实私有对象身份绑定，拒克隆/结构相同/错owner/错epoch/混快照；模块返回快照和集合不可由外部变更。constructor缺owner、初始化失败、观察超限/权限/别名未知、未恢复持久retired来源均fail closed；不能complete+[]或只保护当前models/config列表。固定全部模型根/未来后代、profile-container与database-managed类别分开，不给原字段伪造来源权威。

reserved/observing/complete与incomplete/unknown/failed有准确不可逆/恢复条件。reserve必须在未来写供方开始前由其调用，但本轮只能提供机制，不声称供方已遵守。mutation同步失效旧观察/已发token再允许后续登记；prospective记录parent身份+精确组件，不能用ENOENT吞错。有限metadata含目录项/role/OS identity/links与owner实例而无secret、业务正文、endpoint、凭据；多链接闭合需同观察边界distinct名字数等linkCount且均受保护。所有权/路径/原生身份内容只是本轮输入，不从字符串或hash制造真实OS证明。

active/retired持有态与持久路径保护分别表达：旧epoch/初始化晚回/关闭失败/abort/超时不能删保护或腾实际槽；0句柄不删持久残留。database-managed的released-retained可保留记录并等待未来新可信intent+真实释放与重新仲裁，不永久阻止同库重开，也不恢复旧grant。跨重启没有持久来源实现则unknown，不伪造释放或清空registry。profile具体DB例外与真正能力签发留后批，A不得把profile-container泛放开。

cohort bookkeeping覆盖原方案全部固定engine持有链的有限owner登记与实际初始化/FS/source/network/child/Store未settled槽位，不能把包装Promise abort或pending map清空当underlying settled。若本模块接收真实Promise以追踪结算，必须绑定原owner/epoch并只在实际终态扣槽；不接受调用者自报count=0即可替代。纯测试可以受控Promise复现迟到/abort/取消，但不是实际I06/T01排空回执。原Job/operation终态权威仍T01，不建立第二main意图/幂等账本。

prepare/revoke/quiesce/drain/candidate/publish/abort状态与有界token/epoch准确；同UUID新engine必须完整transition，普通view刷新/同engine瞬断不得误触全量重建。晚成功仅收尾原实例；旧close不得清新全局。candidate未满足全部owner/release/binding条件不发布，失败不发布部分组；没有真实B/T01 ready/原生lease时只能机制层演示，不能装生产candidate。模型不可用与metadata complete分域，不能模型失败自动空保护。同步发布需要的无await约束只证本状态机，不声称接线已原子。

原方案建议有限机制门（每进程transition1、active/candidate各1、picker1、metadata/native acquire2、roots32、entries32768、角色16、depth128、路径UTF8 16384B、waiting5s/candidate30s）可在本纯阶段实现适用部分并明确不适用native部分。它们是资源拒绝上限，不是Q5产品容量决定；不截断后宣称complete。时间/计数必须有限且抗回退/重入/碰撞/ABA，序号耗尽固定失败，不能复活旧token。超时不释放实际unfinished槽；lease连接长寿命与候选TTL分开。任何更改建议界要先说明依据，不以删状态/默认无限通过。

## 验证、冻结和下一步

真实专项覆盖缺owner/失败非empty、revision混拼/ABA/结构克隆、同值重开/ordinary-refresh差别、pending/多alias闭合、跨epoch晚init、close失败、实际Promise未settled时abort/timeout占槽、0句柄持久保护、快照外部修改、计数/TTL极值及candidate原子失败。这是有意义的纯机制单测，不假OS/签名/FS/VFS/Store/producer联验。

运行受影响专项、完整npm run check和verify:sources，独立agent审四新路径/状态机真实反例；修复后最终候选复验一次。保实际argv/cwd/stdout/stderr/exit、首次失败和hash；本地commit冻结明确base/head/完整4产品+docs范围、manifest及原件包，供根核。产品冻结后不边审边改。只docs追加区分process与固定产品。

当前root授权不改变原Goal blocked状态，不新建/声称恢复Goal；不是父I06/FR-002/真实位置访问或发布通过。无GUI/native/e2e/HMR/Keychain/模型/付费/push/PR/merge，指定ZCode GLM-5.3最高与MiniMax M3.1-Flash xhigh同候选双方新审、平台、CI及正常develop合并门保持。交实际新树/分支/base/AGENTSSHA/4路径启动回执后直接推进本授权，不重复询问常规选择。
