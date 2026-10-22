# 单事实 typed 消费：最小供方请求（draft）

本文件只细化供方交付职责与未来判据，**不是公共 schema、wire 方法声明、供方采用或实现授权**。目标限于修改一条既有人工事实的 object：从真实当前全量投影和实际 T02 Preview 出发，保留原 fact ID，走原完整 Diff／人类确认／Job／唯一 writer／receipt／新 undo 链。以下 R1–R10 是 draft 职责槽，不是新类型名或接口名；实际 DTO、方法、错误码与载体由各唯一 owner 回报并由根收口。文中错误类别均为 draft 验收分类，不新增或预定 canonical 错误码。

固定依据为 `fa9881ed84c0dd2b39a7a1185a60a16f168dc9d7` 中的 [下一段方案](../../../iterations/T02/next-integration-segment-20261022.md)、[T01 固定矩阵](../../../iterations/T02/t01-static-dependency-matrix-20261022.md)、[I06 固定矩阵](../../../iterations/T02/i06-static-dependency-matrix-20261022.md)。根独立审计原件为仓库外 `iteration-control/2026-10-21-weekly-release/.private/T02-next-integration-controller-audit-20261022.md`，10613B，SHA256 `99538ee5b24fbdeeffb63747bb817933c1ff9e437ce4a559ae09541f38177f05`。本清单不复制旧十件，也不重开原源码闭包。

## 共同回单与前置层级

**每个槽单独回报实际来源身份**：新 product/process 完整 SHA、本项 path/blob/bytes/SHA、对应 API 实际签名与固定失败、必要 import／资源／严格 schema 闭包和相对已知输入的 delta、profile/policy 身份、原始验证与首失败路径、精确可采用范围。回单须区分已实现、已验证与尚缺；概念同形、文档签字或方法名存在均不替代真实供方。旧 T01 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`／交接 `a1a66bde3e8078b85d5ea4d48909b96ce6417705` 只作矩阵依据，不可 import 充新 M/S1/S2/CostSession；也不建立正向 supplier fixture 来填空。旧内部 business3 链真实存在，但默认 productRuntime 仍只 health。

层级按实际依赖区分：**D 纯设计**现在可并行；**M 机制运行**须根选定精确 base／新树及逐路径采用，新同版供方与闭包齐备，真实 T02 Preview、S1/S2/CostSession、canonical／当前 host scope 形成可消费链；**P 产品闭环**再要求获准命名 engine/main、I06 壳桥、真实 App 完整 Diff 与真人动作；**F 完整父验收**另含完整概念 CRUD／多支持／跨层删除、Turtle/SHACL、T08、T10、平台及发布门。R1 的完整当前 M 五字段读取保真属于 M，不能因首段只改一个 object 而豁免；完整 M 概念 CRUD 则不自动成为首条单事实保存的全部前置。以下“返回证据”均是请求未来实际回单，本文件不填 Pass。

## R1 — M 五字段权威 home 与当前读保真

- **唯一 owner／已有依据**：T01 当前源与 M owner；T01 矩阵“S1：可信完整投影与 M metadata”“typed 写集合”，下一段方案第1槽及文件责任表。旧 strict ontology value 不容纳随意附加 metadata。
- **实际输入→输出**：真实项目当前定义与来源，经唯一权威 home 给出每个实体 identifier、labels、definitions、synonyms、examples 全值及 home／profile/policy 身份；保留原完整 payload、类声明、语言／datatype、显式跨层引用和未知材料的既定保真／拒绝政策。IRI、definition id、业务 identifier 分开；identifier 采用真实业务值，按已选 project 内跨类型精确字符串唯一，区分大小写、不 trim/NFC/casefold。L1 缺失明确返回，不能派生 identifier 或补词汇。
- **固定失败与返回证据**：缺 identifier／缺 home、冲突或未知不支持 metadata、漏语言／datatype、同 IRI 多 home 必须有供方固定失败或明确缺失结果；附真实缺失与多语言来源对照、当前读取前后全 metadata／原 payload 一致的完整集合证据，证明单事实提交及 undo 后无关字段不丢失。不能仅比 RDF 或数量。
- **来源身份／硬前置**：回报真实 home 及投影读路径的新 pin，引用旧矩阵不算交付。D 可先定合同；M 首次消费前须具备完整当前读取保真。创建、复制、删除所有概念及通用迁移的完整实现留 F，不扩大本槽。

## R2 — 首次源读之前的可信 CostSession 与生命周期

- **唯一 owner／已有依据**：T01 原可信资源 owner；下一段方案第1／2槽及 CostSession 段，根审计“初 Fail 与首次读取前计费”。
- **实际输入→输出**：可信 host/issuer 在本次任何源读取、解码、复制或物化之前创建／取得有限 CostSession。先给出 bootstrap policy/profile 如何从可信配置取得、issuer 身份与会话绑定的不可由 caller 伪造方式、适用项目／host／阶段和生命周期；不能先无预算读取领域源来决定预算。所有 reader 和 T02 bind／change_preview／纯翻译／预演／页／确认／Job／commit 复用同一受信会话，执行前预扣；跨分页、重试和失败继续累计，不在第2槽或阶段切换时换新会话清零。
- **固定失败与返回证据**：issuer/policy/session 不符、过期、无预算、超界在实际工作函数进入前拒绝；首次源读取失败／被拒的实际成本同样累计。供方明确 spent 不退、reserved 只有真实释放且收到 ack 才返还，给出 reserve／消费／释放／ack 的真实语义、并发与重试规则及覆盖 reader 清单。返回恰界／超界、失败重试、分页累计、释放未 ack 与已 ack 的原始计量轨迹和进入前拒绝证据；只 costId、client“已计费”布尔、worker 内存或 wire cap 不够。
- **来源身份／硬前置**：固定 issuer、policy/profile 与真实 meter／reader 的新同版源码、资源及闭包。D 可先定职责；M 第一次源读前必须落实。历史重新查询须显式取得／复用当前受信查询预算并关联原操作身份，和原写会话的生命周期分开，不能复用已终结写会话免计费；新 undo 是新操作预算并绑定当下源，不能回收历史 spent 或沿用旧写额度。跨重开如何取得当前受信查询／undo 会话，由供方明确，未交付前保持缺项。旧1MiB／8MiB／64MiB-work仅旧建议；creation ReadLimits 不转授。本槽不解禁 SQLite HOLD、物理研究或 whole-H/native/producer。

## R3 — S1 同连接、完整当前来源投影

- **唯一 owner／已有依据**：T01 当前源／S1 owner；下一段方案第1槽，T01 矩阵“引用／身份”“S1”。
- **实际输入→输出**：接收已取得的 R2 受信会话与获准当前项目上下文，同连接一致读取 public↔internal 项目、revision/vector/control、全部 RDF、每项支持原 ID/owner/source_row/managed_value、墓碑、完整定义 payload、M 五字段和显式跨层引用，输出绑定真实来源、profile/policy 的完整投影。完整 RDF view 与独立 M/proof 的同源对应必须能由供方重新核验，不能只对 RDF 相等就认可 metadata。读取不暗调可持久化的 Store.snapshot；原预览确需 artifact 时由原 T01 预览明确产生并计入预算。
- **C5 消费边界（draft 兼容要求）**：现有 `bind_rdf_projection` 面向批准的 Store2 只读来源形状：`project/projectRevision/dependencyVector/state`，state 含 definitions/facts/mappingState；它不是新 M/business3 全量读取器，也不是 metadata proof。新 S1 须给已批准兼容的完整 RDF view，并独立绑定完整 M／proof 与原完整源；若现有消费入口不兼容，明确回报必要 C5 消费 delta／字段来源／成本给根与 T02 owner。禁止 T02 手造减字段 snapshot 来凑旧形状、丢弃 metadata 或将旧 Store2 绑定结果冒充新来源证明。
- **固定失败与返回证据**：坏 payload、漏／替换支持、墓碑被当活事实、缺 metadata／引用、错项目或不一致读取固定拒绝；返回原记录→支持→RDF／完整 payload 的逐项对应和读取零领域写证据。对同 revision 下内容、metadata、policy 漂移提供可复验来源身份，不能只传 revision。
- **来源身份／硬前置**：固定实际 reader、真实 home、来源绑定与 issuer 连接的本项路径闭包，不能拿同形 `OntologyView`／Snapshot 或手填来源充供方。M 在 R2 之后、实际 T02 预览之前；无需等待完整 Turtle 或通用 CRUD。

## R4 — S2 原唯一 plan authority、持久 proof 与独立重演

- **唯一 owner／已有依据**：T01 S2／原 ChangeSet authority owner；下一段方案第2槽，T01 矩阵“S2”。
- **实际输入→输出**：消费 R3 来源身份和实际 T02 Preview 的纯翻译请求。可译条件完整采用 [消费矩阵 C1–C8](consumer-matrix.md)：既有 individual/dataProperty、恰一 removed／added、同 S/P、单个人工支持、slot与目标不冲突、无 entity/metadata变化，保原 fact ID；mapped、墓碑、多支持、目标已有、metadata/entity 变化或不可表示拒绝。sourceBinding、独立 ontologyPreviewHash、模型身份、metadata/profile/policy 与原 prepared plan／参数／持久 envelope／cursor／Job context 的具体绑定由同版 T01 固定，旧 previewHash 不改名冒新 proof。
- **固定失败与返回证据**：保存预览前由 T01 独立重取源／重新投影并在原 Store 事务回滚预演，完整 after 必须等于实际 T02 candidate，并比较独立绑定的完整 M/proof 与原控制/来源；不信客户端 Diff、trusted 标志或手填 plan/proof，不以旧 Store2 形状拼接的新快照绕过 S1。返回实际生产 Preview→原 ID edits→原回滚 after/control 的完整对应，以及同 revision 内容／metadata/policy 漂移、来源失效、漏支持的固定拒绝与零部分领域写证据。
- **来源身份／硬前置**：固定实际 S2 与原 authority/envelope 持久读写路径和同版模型 pin，闭包不沿用旧14项目录冒新发行闭包。M 依赖 R1–R3 与 R8 对应 canonical/host 合同；T02 adapter 不持路径/DB/Store 权限，不调用 confirm/create Job/commit，不另造 writer。

## R5 — 原完整 Diff 分页、页链和展示材料

- **唯一 owner／已有依据**：T01 原 preview／Diff owner；下一段方案第3槽、T01 矩阵“真实回滚预演与完整 Diff”“prepared plan／分页确认”。已有 changeset.preview、changeset.diff.page／JobStore.changeset_diff_page 仅作旧合同名称引用。
- **实际输入→输出**：按新同版 proof／预览身份读取原完整 Diff，各段包含 definition、fact、definition-status、metadata 与 undo-impact 的实际适用内容；保 segment、offset、rawByteLength/hash、cursor 页链及合并 UTF-8 信息，不能以 T02 RDF 差集替代原 record/control Diff。跨页／重试继续 R2 会话计费。
- **固定失败与返回证据**：缺页、错链、组装材料重复拼段、跨项目或旧 proof 页、截断、中文跨 segment 合并错误必须固定拒绝确认；同页受控重试依真实供方合同处理并计入 R2 同会话，不预定新的 cursor 协议；返回实际原完整 Diff 的全段重组对照及每类失败的原始页链和费用。末页到达不等页面已显示，更不等真人已读。
- **来源身份／硬前置**：回报实际分页/envelope/存储段与对应 strict DTO 的新 pin。M 需全页真实读取和机制确认门控；P 的可见完整 Diff 与真人动作另由 R10 验证，不能用 fixture 消费所有 cursor 宣称真人通过。

## R6 — 原确认、Job 受理、排队后 commit 的四阶段 guard

- **唯一 owner／已有依据**：T01 原事务／Coordinator／Job owner；下一段方案第4／5槽、T01 矩阵“durable Job／原 writer commit”。
- **实际输入→输出**：沿原 changeset.confirm／confirm_changeset、job.create／create_changeset_job、Coordinator.execute_changeset→commit_job→domain_changesets.commit→ProjectTransactions/Store。预览保存、confirm、Job 受理、最终 commit 各在自身原事务独立重取当前源、版本与 proof 并真实重演；确认回单与原 preparedPlanRef/inputSnapshotId/parametersHash 按同版 canonical 绑定，scope/definitionId/operation 身份不由 T02自行补造。
- **固定失败与返回证据**：分别提供四时点同 revision 内容／metadata/policy 漂移，及排队后变化、失效确认、取消、重复 operation 的固定失败／幂等语义。queued 不等成功；返回原唯一 writer 外层事务中领域版本/evidence/receipt/result/succeeded 同提交的原始原子性证据，失败无部分写，提交后响应丢失保留真实成功。不得新 SQL writer、拼多个 CAS、把 maxWorkerMemory 当计费。
- **来源身份／硬前置**：固定原 authority、Job/Coordinator/事务路径的实际升级 delta 与 guard 覆盖位置。M 依赖 R2–R5/R8；机制中的显式 fixture 确认只计机制，P 必须由 R9/R10 真实命名桥与页面动作触发，不以 renderer confirmed=true、模型 grant 或恢复逻辑代替。

## R7 — 原 operation/receipt 对账、历史与新 undo

- **唯一 owner／已有依据**：T01 原历史／undo owner；下一段方案第6槽、T01/I06 矩阵“取消／响应丢失／恢复”。
- **实际输入→输出**：沿原 job.get/result.get/result.page/operation.get 获取不可变 receipt 与终态；丢响应按原 operation 对账，不自动换 ID 重放，unknown 不视作未提交。undo 从原 changeset.preview 的 undo 意图／targetOperationId 开始，完整 undo-impact→新显式确认→新 Job；当前新 proof 与历史旧 proof 分开，重开／跨 session 仍能查真历史。
- **固定失败与返回证据**：实际提交后响应丢失／重开查询、重试对账、取消与成功竞态、undo 不相交后续变化保留、同资源／引用冲突暂停的原始回单和固定失败；不伪造反向 plan，不退审计 revision 或改历史。历史读取／分页走当前查询预算，新 undo 预算先于其首读并全链累计，返回和 R2 的会话身份／费用对应。
- **来源身份／硬前置**：回报真实历史/receipt/undo 的新同版闭包与恢复生命周期合同。M 需原机制链真实验证；P 再验证实际页面状态，不可用临时机制成功或旧 receipt 换取当前写 scope。

## R8 — T01 canonical、命名 engine、当前 host scope 与四基础文件

- **唯一 owner／已有依据**：T01 canonical／engine／main owner；下一段方案“文件唯一责任”，I06 矩阵“当前唯一责任”。T01 独占 `apps/desktop/src/main/{index.ts,task-service.ts,jsonl.ts}` 与 `apps/desktop/src/renderer/src/task-presentation.ts`，I06/T02 不写这四件。
- **实际输入→输出**：回报上述新能力的真实 strict canonical/registry/TS/Python 同版 DTO、固定失败和命名 engine 入口，当前 host/项目/session/连接 scope 的可信来源与绑定方式，以及仅为首条单事实链所需的精确采用 delta。不得在旧 additionalProperties=false 的值中塞 proof/cost/metadata，也不添加通用 invoke 或由 T02命名新 wire 方法。实际合同与路径由 T01 固定，不默认四件或所有 canonical 文件全改。
- **固定失败与返回证据**：schema/profile/policy 不匹配、非当前 host/project/session、过时代次／旧确认、未启用产品 scope 的固定拒绝和真实分派／守卫证据；区分新供方的获准机制 profile 与默认产品启用。返回产品/process、canonical/资源闭包、四基础文件逐 path 的所需 delta 或明确无需改动依据。
- **来源身份／硬前置**：以本项新 pin 给出实际 authority/engine/current host 身份，不把旧 business3 override 或 UUID 当物理 issuer/human 授权。M 先取得机制所用同版 canonical/host 合同并经根逐路径采用；P 才要求获准正式命名 engine/main 产品接线完成。无需将整个 M0/whole-H/native 一并解禁或等齐。

## R9 — I06 四壳的具名 bridge 传递合同

- **唯一 owner／已有依据**：I06 壳桥 owner；I06 矩阵的四桥责任和下一段方案 I06 行。范围为 `apps/desktop/src/preload/index.ts`、`apps/desktop/src/renderer/src/{env.d.ts,App.tsx,style.css}` 及获准专属测试；不含 R8 的 T01 四基础文件。
- **实际输入→输出**：消费 T01 冻结的具名 DTO/响应，在获准最小表面传递当前全量投影、实际 preview/proof、完整 Diff 页、人类确认、Job/receipt/undo 查询与动作。回报拟新增／复用的确切方法、路径和参数范围供根批准，本清单不先命名方法。不得把模型12方法或 confirmModelAuthorization 当本体通道，不向 renderer 暴露通用权限或成本发行权。
- **固定失败与返回证据**：错项目/session/revision/连接代次、旧页／proof／晚返、断线／恢复、卸载退订、取消与重复动作的失效规则和固定呈现合同；源头固定失败不得透出原异常。返回同版 canonical→preload/env→App 的实际传递证据、逐 path delta 与来源闭包，不以已有任务/模型生命周期守卫静态存在当新链联验。
- **来源身份／硬前置**：旧 I06 保留产品 `e2c269ad78a78e1a042cadc93b1c81a874707153`／fullsource `1f3b053d8a69d1f7ddb1e29c143f648d910fe689` 与未跟踪交接快照只作矩阵依据；新 bridge/App 供方 pin 仍待真实回单。D 可并行；P 的实际执行依赖 R8 同版命名 engine/main 及根逐路径批准，不能从 workspace HEAD 推定交付。

## R10 — I06 真实 App 完整 Diff、真人确认与终态呈现

- **唯一 owner／已有依据**：I06 App owner，负责壳页动作与代次接线；T02 页面保持其独占模块责任，不转交 T01 writer。依据下一段方案第3／4／6槽及 I06 矩阵“人工确认”“generation”。
- **实际输入→输出**：真实加载 T02 页面，展示 R1/R3 完整当前投影、实际单事实修改预览与 R5 全 Diff（含 definition-status/metadata/undo-impact），由真人实际可见页面动作进入 R6 原确认/Job 链。显示 queued、实际成功 receipt、unknown／待对账、失败和取消区别；undo 仍为新预览／完整 Diff／真人确认／Job。草稿版本变化可保留输入但禁用旧预览，切项目/session/连接 generation 与晚返不能恢复旧写资格。
- **固定失败与返回证据**：全页到达但未显示、错页／漏段／失效 proof 不得确认；旧点击／取消／恢复不得自动确认或重放。返回固定供方与实际页面构建身份、真实全 Diff 可见记录、真人动作及其回单链、代次/切项目/断线/晚返和丢响应对账的实际产品证据；人工操作证据与机制 fixture 分开。现21项合成 callback 只作页面回归，不当本项证据。
- **来源身份／硬前置**：本项新 pin 限获准四壳/页面接线与测试路径，涉及 T02 页面 delta 另列给其唯一 owner 和根，不抢写。P 依赖 R1–R9 对应实际供方与根阶段授权；不要求先完成 Turtle/T08/T10 或全部概念 CRUD，亦不因单事实 P 通过关闭这些 F 门。

## 保留四 P3 分流及未定点

四项按 fa988 原分流：digest 入口校验与 lazy localGraph 只进入未来新候选，若增加 validate 成本同步 CostSession profile，合法 digest/归一化和图节点/边/截断保持；深链祖先 Set 成本为非阻断观察，待真实数据/Q5规模与设备阈值，不量化未测性能或启动无依据优化；旧 delivery/stage 指针保历史，下一完整输入更新副本/引用，不热修 C5、不把旧文写成已修。当前材料不更改任何分流。

仍待唯一供方确定的内容是：新 product/process/source pins 与采用范围、M 真 home/L1缺失合同、CostSession bootstrap policy/issuer/生命周期与跨重开预算、S1/S2实际签名/错误和闭包、canonical/命名 engine/当前 host scope、I06本体具名表面与真实 App动作契约。这里没有代填公共字段或 wire 名称，也没有正向 supplier fixture、import、产品/GUI/模型/SQL/JobStore 测试。纯设计可继续并行；任何运行/共享文件实施须按上述对应层级收齐真实材料与根授权，而非泛等所有父模块。
