# T01 C1：内部空白创建事务与严格历史语义实施

2026-10-21。正式服务/host所需真实位置与原dispatch物理绑定仍未交付。本件将下一步精确拆成可独立验证的内部Store事务子阶段，不改ff725合同或其已关闭P2，不授权正式create_project_request/resolve_operation、真实scope/binding签发、首位置IO或公开接线。§8“审批前真实I06到位”适用于正式服务使用；不能被本内部机制测试冒称已满足。根独立合同报告须实际收件并全文读后才发送本授权，文件存在不等于调度。

根已全文读固定379916267e5c36eebedb44d35a6636b9915ccd70的39602B/SHAff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3合同；其parent a816读取服务受限收口2270B/ccb26cc保留，原两个树产品/证据均冻结。继续同一原T01会话/原Goal，不重建或声称恢复Goal。

## 新树与精确范围

从实际批准5f910b52c69d86a1076b2032e5d3c63e715947f3开新树 /Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-create-core，分支feature/weekly-t01-project-create-core。先按控制 T01-project-create-core-fixed-foundation-inputs.json（14299B/SHA c87fd0a1aca68c9a82ceb8aa142a5d8b6ab974d5e29d17588bd1909d64aa9726）逐50条a816固定Git原字节接收并独立adoption提交，根已逐Git bytes/SHA核同且读所有路径，不wholecommit/不拷环境或旧docs。复制最新版AGENTS15852B/78df2825…a759作为保护规则未stage，common/完整第九节和无桌面规则继续。

仅五条产品/测试writer：

- packages/engine/src/ontolearn_engine/project/project_lifecycle.py（新）
- packages/engine/src/ontolearn_engine/storage.py
- packages/engine/src/ontolearn_engine/job_store.py
- packages/engine/src/ontolearn_engine/project/format3.py
- packages/engine/tests/test_project_create_contract.py（新）

三项既有产品在初始50接收后可按本件修改，其他47项全部只读，包括project_host.py、所有旧测试、task-runtime（维护仍I05）、main/canonical/worker/coordinator等。完整相对5f产品/测试应实记52路径（50初始中三改+新增module/test2），另本线docs；不能只报五路径。新说明仅docs/iterations/T01/project-create-core-C1.md，证据仅docs/reviews/T01/project-create-core-C1/。不写applications.py/其他旧tests/依赖/锁/build/CI/协议/主renderer/preload，不注册新capability或改变startup默认格式。若最小五路径不足先交实际反例/精确差异再申请，不能默扩。

## 只实施内部事务语义

沿合同§3–5及§7真实效果/预算：Store.commit只新增互斥creation=intent私有分支，服务之外不另开writer、不先落genesis；原JobStore.create_project与既有普通domain/application/format2行为和旧hash不变。内部intent/测试origin字段只是可信调用者传给Store的业务材料，不能从精确字段或permission字面值认证用户/物理库/真人；不导出能造真实dispatch_binding、FS lease或scope的factory/布尔开关。

直接消费已开且测试实际创建、完整Job3结构已校验的真实JobStore3连接；仅target_format3或只有Store3而缺operation_claims/public_projects/Job-ready结构时，新增分支须写前明确拒绝，不隐式建Job3表或把Store-ready冒充Job-ready。在唯一外层BEGIN IMMEDIATE中先核全库operation唯一占用/原创建claim、先重试查验再分配真实engine UUID；新project/internal/public同UUID，旧公开映射不重编。精确空白request/原name、不trim/NFC/casefold、不接受客户端projectId/plan。libraryEvidenceRef仅从真实immutable app_format行逻辑引用，不是物理文件ID。核心可据已知origin/operation判断内部幂等；外部原意图归因不能由它自证。

正式持久效果全在Store.commit：projects revision0、空domain snapshot、既有seed_project(origin=created)的null-name metadata0/seq0真实origin/checkpoint、public映射；然后唯一operation_claims application/context、创建专属name与metadata1/seq1、app_operations和唯一app_receipts/aftercheckpoint，真实读回链/哈希/FK/旧后续历史。不得INSERT OR IGNORE吞冲突、补认既有空项目、半组发布、第二Job/领域marker/receipt或Store外拼写。业务receipt和context精确按ff725，plan必须真实genesis后据实生成，不能写前猜checkpoint当已存在事实。

复用原表，无DDL/新kind/迁移/新可变账本；JOB3_SCHEMA/HASH、app schema_hash、user_version3/默认FORMAT_VERSION2不撒谎改变。只精确扩job3/format3 semantic dispatcher识别projectCreateContextVersion1，旧applicationContextVersion1与Job完整原validator不放宽，不混标签/宽松回落；旧apply_application同op遇新create namespace先identity-conflict，反向亦然。旧格式3reader遇新语义应实证安全拒绝，不能宣称双向兼容。新/旧消费者与未来能力版本绑定仍是正式启用前置，本子阶段不接wire。

保合同§7完整写前预算：不仅name自身≤4096，而是完整metadata/目录行/所有page_size与offset完整页/初始workspace所有合法editor最坏编码、完整库新增全部genesis/public/claim/checkpoint/receipt行数与SQL字节/validation_work/完整目录snapshot和可行留存预算。只读消费同版实际ReadLimits，不复制可独立漂移政策、不改reader放宽。首次INSERT前完整候选计费并在真实写后逐值核同，任何差异回滚。事务中不调用拒writer事务的catalog_start/workspace、不新开连接/补snapshot。4096 ASCII名完整metadata4178B写前拒绝与转义扩张反例必须保留。若任一界无法可靠写前推导，精确交问题，不先写后证明或删字段取绿。

同op同request/origin内部重试返回原receipt，当前项目后续变动不重算原receipt、不再检查仍空/仍同名；异request/kind/origin/UUID或孤儿/坏hash拒绝不修。COMMIT后失响应/等待取消不删除成功项目；前失败全组回滚。此内部结果不是正式服务在复制库/新Session上已关闭unknown的许可，服务仍缺I06实际binding/current_scope，不能接成自动replay。

## 未实施部分与真实测试

不新增test_project_operation_resolution.py，不实施正式create薄适配、resolve_operation/任何resolved结果或物理归因接口、不改Job context格式补旧origin。可在已有内部validator核完整相关claim/history，但不能借此声称queued无marker已安全归因、跨Session resolved或已获当前许可。ff725其余正式resolution/首IO/人类选择/I06供方/host/RPC全部保前置，后续独立精确阶段再做。

新增测试只用真实临时SQLite/Store3/JobStore3的可信fixture和受控origin/intent证事务：原子genesis/publicUUID/唯一claim/receipt、合法reader在同政策资源可用下catalog/workspace可读、同名/碰撞、每写边界异常/SQLite失败与真实自有子进程退出/重开、commit后失响应重试、后续history推进仍返回原receipt、旧format2/旧hash/旧reader拒新namespace/跨namespace冲突、坏原件零修复、完整预算±1/转义/页/workspace/全库边界及dump不变。test内fault hook/子进程只作用本线临时DB，不加生产fault env、不触用户文件/当前桌面。

这些fixture仅证内部机制，不能假I06物理绑定/真实scope/人类点击或生产API。运行受影响新/旧专项、完整npm run check、verify:sources，逐命令独立保存真实exit（避免npm后另Python使末shell0冒充子exit）、完整stdout/stderr/首失败。复杂事务与兼容要独立agent审查同固定candidate及所有采用/改动路径；修复后最终重验，冻结产品后不边审边改。提交产品SHA、完整52+docs清单、47只读逐hash和原件安全包，根读回再收口。

无实际用户位置文件IO、native/VFS/Keychain/模型/GUI/Electron/e2e/HMR/付费/push/PR/merge。完整FR/44与57P0、两个目标OS/真人/父Goal、指定GLM-5.3最高/M3.1-Flash xhigh双方同版新任务/真实Pass、CI与正常develop合并/远端门保留。原读取和合同树继续只读，C1无DDL或公开使用放行含义。先交实际新树/branch/5f/50adoption与47只读/唯一5writer启动回执，再按本授权推进，不重复问常规许可。
