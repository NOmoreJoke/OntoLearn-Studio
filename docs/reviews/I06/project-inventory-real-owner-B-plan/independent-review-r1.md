# I06 B 真实资源供方方案：独立静态首审

2026-10-21，审查者 `/root/i06_design_review`。**结论：当前冻结主方案暂不通过完整定稿；两项 P2 合同缺口需修正文案并重新固定。**两项均可在本轮docs中通过明确不支持边界/最小后续申请或bootstrap规则关闭，不要求修改冻结6a38/e2c/961或立即实施B。本审不替指定模型双方审查。

## 实际输入与范围

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-project-inventory-lifecycle`；本轮只读固定Git、文档和stdlib JSON/hash，唯一写入本报告。未import/执行产品、测试、build/install、真实metadata/FS运行、网络、native/GUI/Keychain/模型，不改Goal、产品、规则、依赖或旧证据，无commit/push。

主候选全文194行已读：`docs/iterations/I06/project-inventory-real-owner-B-plan.md`，41058B/SHA256 `d6bf752aa945711867c8362fa9e332474b03cf81e3922486c81a125bc9fd2d10`。

先全文读本轮4183B准备指令/SHA869e9c9568a52776b212238506700735b58de3b15cd709941b99d294cd8264c9、根offer复核12219B/556c6b838cf8e0c6a209a5a3633286128a1687bb208d25ce91191e56bd56647e、A最终readback13636B/b1d30ac744c97182a111dfcbdd27cfb1bc924b046a01d148e8989a51b4996eb4和closure1791B/30a4fc97d6043dc82ce76275ee684b49a9f416b90ca0ad8601610afea08ed006。1f3合同/A接口延续前轮实际全文审查，本轮另从固定6a38核本报告依赖的A代码原文。

两份源事实报告全文分别读取，长输出截断段单独重读；固定为source-metadata31796B/78cdde9eeebceb1e9e1c8764c0873363f7b49ed665266d026122b8863bf3945d，source-lifecycle23028B/6f0cb3bd6950af0ba588c7357025ae17c126a8d8b03ac0d23371e1149d1fdb4c。

实际以Git blob/本地原文件逐项计算并断言52输入bytes/hash全部匹配；inputs.json21741B/SHA45c1bd3194363a9ddbc7153007c74eb44e89d262c93ad4273e6d6ef8aa815507。review-input-r1.json的四项当前bytes/hash也全部匹配；该清单889B/SHA1d51a6c64085a2fdd849121bbc4e6e9695a7114f2aaeca092ac4dbbc69ec6658。此项是静态来源核验，不声称本审全文研究全部52份产品实现。未运行文档格式工具或产品检查。

## P2-1：同路径新incarnation并不能映射到冻结A的完整观察

**位置：**主方案§4.2第8项（91行）、§7第4项（139行）；实际A依据为6a38的private-resource-inventory.ts:147–149、213–220、382–400。

**触发：**真实文件X原identity=A；文件移除后旧记录必须保留为absent-retired。相同parent对象与components下出现新identity=B，按方案分配新incarnation id并保留旧记录。完整观察需要同时提交旧absent-retired与新present-active两项。

**实际接口矛盾：**A的locationKey只含parent OS identity和components；resources()要求该key在整个payload唯一，不按presence/incarnation分组。上述两个合法历史/当前项具有相同key，因而整体拒绝。先单独reserve新id也不能避开：后续完整observe仍须带全部旧记录，merge complete明确拒绝省略旧id。旧id又不能偷换identity。以上是固定代码静态推演，本轮未执行反例。

**影响：**B-M按现文“新id”步骤仍不能对这种常见位置复用形成完整一致投影；可能被迫永久unknown，或实施者为了通过而漏历史/改A。现§7笼统“不支持映射则unknown”应明确点名这一已知接口缺口，不能把换id写成已足够的解决办法。

**最小修法：**不动6a38。明确B-M当前遇同址换inode保持unknown，保留全部历史身份并拒绝宣称该观察完成；另列最小A扩展申请：在同location组中允许一个当前present项与有限absent-retired历史项共存，继续保全部旧身份/上限，拒两个当前present冲突、原id换identity及历史回active。扩展须独立候选、实际正反例及重新审查；本轮仅记录需求即可关闭文案问题。

## P2-2：持久控制树首次建立和journal自身追加缺少自举边界

**位置：**主方案§5（97–109行），尤其首次创建header/intents/seals的99行与“新root/将创建目标必须先有完整intent+seal”的105行。

**触发：**真实fresh控制位置尚无intents/seals目录。若按通用target mutation规则创建intents目录，也需要先持久化sealed intent；写该intent反过来需要目录。以后若每次写intent/seal本身也算同类target，则继续递归生成记录。反过来若实现任意豁免metadata写，则会绕过方案承诺的先记保护/失败保留，当前文案没有确定选择。

**影响：**B-R的首个合法步骤与有限写权限不闭合，不能仅靠exclusive create或“实现时处理”解释。该缺口是可实施合同问题，不是在本轮要求实现native耐久或真实首次安装认证。

**最小修法：**冻结固定控制metadata bootstrap/self-append协议：只有真实受信fresh流程可在预reserve后建立固定最小控制树及immutable header；此过程不能解除任何外部target准入，partial/close/sync/身份失败均unknown并保留原件。控制journal自身的固定追加由该私有协议直接自保护，明确不递归为每次自身写再生成intent；对所有其他目标仍须完整intent+seal及所需耐久确认后才执行。若实际bootstrap来源/原语未到，明确B-R实现前置未交付而不能自签fresh。不得把豁免扩大成任意FS callback、目录写权或第二项目/Job账本。

## 小项：owner计数应消除歧义

主方案19行称“不合成其他六类owner”，但§4列出的I06实际子集至少涉及private-root、credentials、configurations、audit，未给出这句仅两类的依据。建议写“不合成任何缺席owner”，或明确本子阶段实际登记哪些角色。该表述不应引导补synthetic空owner来凑全局complete。

## 其余判断及未验边界

B-M/B-R/B-L统一为候选子阶段，源agent的B1/B2/B3名称不构成合并授权。逐路径A采用、不整commit移入流程材料、不采用e2c完整网关、T01 canonical/main/Store唯一owner和T03 build责任均清楚。配置仓库经source拉入engine/canonical的闭包问题已明确，完整模型批不能以私有同名DTO/stub或any绕过；类型-only依赖也仍需获批类型闭包。

B-L明确选择本地唯一registry先预留再启动实际命名操作，不把A.track(owner,kind,alreadyStartedPromise)当先准入；A reservation只是后续独立替代申请。logicalOutcome/underlyingCompletion/永久ownershipLifetime分开，close失败、晚init、网络result先完成、audit收尾及旧/当前child聚合均未被native Promise品牌掩盖。普通同Supervisor短session恢复不被扩成清grant/全量重建。

B-R的稳定控制位置、不可覆盖记录、预算、损坏unknown、受控fresh与跨进程writer/native耐久待证边界方向正确；上述自举范围尚须点名闭合。Node观察明确unfenced，Windows与同build VFS/C未实现时首SQLite/header/catalog/backup IO仍拒绝，未以固定userData替代FR-002。

本审没有任何真实供方、持久恢复、OS释放、业务接线或生产成功的运行证据。两项P2修正文档、统一owner表述后可做定点静态回读；无需重跑冻结A/旧网关/平台，也不要求普通任务固定多轮。当前报告不授权后续产品实现或解除productionAdmission unsupported。
