# Receipt identity：限定纯设计采用决定

决定：固定 carrier R2 `0841ffbe7a4599fbea96f4ff998808f3f4e00972` 的这项身份映射，可以作为现版本的纯业务采用合同，无需修改已接收 `d9c3c151614674f2c7a6e3d7f6507aa7ba81db58` 的四份 schema、field responsibility 或版本。本件提出 T03 规范作者的采用决定，须由独立静态审和总控精确接收后，外部另给 `receiptIdentityPolicyPin`；本文件存在不等于该 pin 已生效，更不授实施或运行。

这是新业务语义的明确采用，不能由 fieldIndex755 的 `producer=caller` 单独推出。该条只分配字段生产与核验责任。receipt3 的 runId 仍为 required 非空 string，最大8192字符；R2 的业务 Id 子集仍按其既有 ASCII pattern、最大2048字符执行，不放宽、不截断或重新命名真实 ID。

## 角色、唯一域与重试

| 字段/原件                                                     | 本合同的精确定义                                                                                             |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| caller 原始登记的 attemptId                                   | 真正调度尝试的身份，先于 child 结果存在；未 dispatch 的 prelaunch 尝试也有真实登记，不能为补 schema 事后编造 |
| receipt3.runs[i].runId                                        | 对应 caller attempt 的外部收据条目键，等于真实 attemptId；不是 child 身份                                    |
| carrier2.attemptId、binding2.attemptId、attemptCore.attemptId | 同一登记尝试的显式关联，全部与该收据条目一致                                                                 |
| binding2.receiptRunId                                         | 等于上述 attemptId 和 receipt row.runId，不能改成另一个 child ID                                             |
| carrier2.runId、BoundContextCore.core.runId                   | 仅为严格接受的唯一 child ContextFrame.runId，且后续 child 帧同源一致；context 前为精确 null                  |

attemptId 在同一个外部受信 caller 登记作用域内唯一，原登记顺序是序列依据，不按 ID 字符串排序。**每份 receipt 先固定一个完整的逻辑 registry/原序域**，外部 binding/manifest 必须能唯一回到该登记来源、owner 和原件。不同域分别保留完整原件，不得因同字面 ID 拼接、去重或事后改名；不得把同一域拆开以漏掉失败。多域合并须另有精确可核的登记合同，当前不能自动合并，也不向31字段里偷偷加 registryId。无法唯一限定来源域时，保留全部 capture 并拒绝兼容结论。

child ID 的有效域是该实际 attempt 中接受的 context 及其帧。跨 attempt 的同字面 child ID 不能用来去重或复用旧结果。两种角色的字符串可以偶然相等，但必须分别有真实登记与受信 context 原件；相等不证明角色相同，也不要求用人为改名使其不等。ID 是区分大小写的原值，不能 trim、归一化、改前缀或借 PID、时间、expected ID 补造。

每次真正的新调度/dispatch 或新的 prelaunch 尝试使用新的登记项和唯一 attemptId，保留前次失败与原序。读取同一已登记 attempt 的既有结果不是新调度，不制造重试行；若结果不明，先核原登记/原件，不能覆盖旧行或自动重跑。字符串本身不证明登记先后、owner、collector 或执行许可。

## null、未启动和 context 后失败

| 真实边界                                                                    | child 身份与 attemptCore                                              | receipt3 保留内容                                                                                                                                                                 |
| --------------------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| caller 在 prelaunch 阶段未 dispatch                                         | not-dispatched；carrier.runId=null；NotDispatchedCore.childRunId=null | 仍有 row.runId=真实登记 attemptId；按原 CR-R not-started 保留全部31键，原双流/exit/signal/实际观察为其允许的 null/空，两 complete=false；不造 child                               |
| 已 dispatch，尚无受信 context，包括0字节、坏/缺 header、stderr-only、signal | unavailable-before-context；carrier.runId=null；PreContextFailureCore | 双流 FileRef 均非null，即使0字节；真实 exit/signal、header范围、首错全部保留。只有满足原 CR-R 的 probe 前置 exit2 才能 pre-header-rejected，否则 incomplete；不能改称 not-started |
| 唯一合法 context 已被接受，后续完整或失败                                   | observed-context；保真实 child ID；BoundContextCore                   | 外部 row.runId 仍为 attemptId，经 binding2 关联；后续坏帧/重复 context/失败不得抹掉先前已接受的身份、stage、false 或部分观察；保持首错和 incomplete，不能升级 collected           |

未受信坏行中的词法 runId 只保原 raw，不成为身份。只有 header 合法而没有 context，也不能建立 child ID。第二个 context 必须触发原重复/次序拒绝；若第一个 context 此前已严格接受，保留其事实和后续坏行，不能为满足“唯一”而回滚成从未有身份。未启动与已 dispatch 的判定取自真实 caller 事件，不能仅由没有 child 输出推断。

缺少真实登记身份或来源无法认证时，不得伪造一个合法 receipt row 来补齐：保存所有原件和无法投影的诊断，禁止宣称完整合法的 receipt-business 对应。此规则不删去失败 attempt，不把 captured-unverified 升为 observed，也不 nullable 化 receipt.runId。

run 能表达 not-started，不等于可以省略或伪造整份 receipt 顶层必需的 buildReceipt、approvedBuildRecord 和完整 manifest。若这些合法外层来源根本没有取得，只先保登记与原件，不能用合成外层票编成合规 receipt。原5例的 detached synthetic approval 前提不能充当真实来源。

## 全31项回投影与原件闭包

`adoption-contract.json` 列出原 `receipt-projection-r2.json` 的全部31项、原 pointer、完整投影文字及当前 schema 的 required 顺序。每项完整 receivedShape 已逐值等于 d9c3 的同名 schema 子树；不复制或改写原 shape，不重跑其余未变1241字段。除本次 runId 角色明确采用外，其余30项的类型、null/partial、CR-R/CR-H、source/frozen 分域和真实来源规则继续由已接收规范约束。

所有登记尝试，包括未启动和全部失败，在原序中恰一 row/一 binding 对应；拒绝缺项、额外、重排、重复、悬空或不同作用域的错误连接。headerPayload 保原 header/2 完整严格解析值，原 raw 的错 mode/selector/ref/digest 不改成命令或批准值。caller 命令上下文与实际 header 观察分开保留，任何不匹配按原 CR-H 记失败并保持 incomplete，不由本身份合同重定义其它字段。未观察值只用 schema 已允许的 null/部分列表，false 必须进入实际 observedPaths，不能删值或改 mask。

raw header/terminal 的 FileRef 必须绑定实际提取的完整原片段及其 bytes/SHA，并与 whole stdout、RawRange 和 manifest 对回；RawRange 本身不是 FileRef。所有已 dispatch 的0字节双流仍有真实 FileRef。receipt 行没有完整 typed/stage/context 载荷，不能从31字段反建 carrier：反向核验必须读同一受信 manifest 指向的完整 binding2、carrier2、双流及 caller 原件，核 attempt、原 build 票、原 context/stage/piece、首错和全部引用。只有收到字符串 ID 或摘要不构成回投影闭合。

无环顺序保持：已接收规范/独立批准来源与原 build 票 → caller 真实登记/command/prior authorization → child 双流与 caller 后出原件 → carrier2 → binding2 → 若实际到达的 comparison → 外部完整 manifest → receipt3。binding 不引用未来 receipt；manifest 不列自身和后出 receipt；build/provenance 永久 not-executed/null，不回填。旧 carrier1/binding1 不自动升级。

## 采用边界与待采集验证

本次只采用身份关联的纯业务解释，不单独批准 stream2 全部业务语义、旧 codec、caller witness issuer/layout、collector、受控根、真实登记实现、费用或运行。实际 receiptIdentityPolicyPin、businessAdoptionPin 及所有 implementation/registry/collector/layout/root/composition/权限 pins 仍须由真实外部接收提供；本记录不包含自 hash 或未来自身 ref。总控接收后可用固定 `adoption-contract.json` 原件作为 policy pin 目标，具体 ref/path/bytes/SHA 由后出接收记录绑定，不回改 R2/d9c3。

原 T03 protocol3 规范作者已独立只读核同一10件材料并给出相同限定结论；上述单 registry 域、首次接受 context 的单调保全、完整外层票与 mode/selector 边界已纳入。其判断不是本件后续 fresh 独立静态审，也不替总控共同接收。

原 R2 两次覆盖冻结 checker 的过程事故及缺失的初稿 bytes/独立时间/部分初始分流均保留；旧113件恢复不能洗成全程合规。原5份完整合成失败例仍是 synthetic：zero-byte、bad-header、stderr-only、signal-before-context、not-dispatched。另4条 context 身份情景只是关系前提，**没有完整 post-context incomplete/collected 端到端 fixture**；本件不补造该证据，也不把下面文字反例当执行结果。

后续另授窗口仍须验证：实际登记先于结果、全部 attempt/重试原序、真实双流与0字节捕获、context接受及后继失败保全、31项双向原件核回、完整 post-context 失败/完整采集 fixture、真实 collector/owner/layout/受控根与 prior ticket、source/frozen域和各原父门。M02–M05旧 metadata/codec/recipe/verifier/return adapter、费用/issuer/usage/17L、whole-H/损坏SQLite HOLD、417/B1/S1、平台/真人/指定双审/CI/develop仍未关闭。

若后继要求把 receipt.runId 直接改为可空 child ID、在31字段增身份 union/新键、改 required/类型或改变原 CR-R/CR-H，必须由 T03 前向新 schema/consumer/责任表版本和迁移合同重新审查；本次兼容决定不覆盖这些变动。当前不执行产品、collector、fee、runtime、caller、native 或 GUI；T04 桌面资源不受影响。
