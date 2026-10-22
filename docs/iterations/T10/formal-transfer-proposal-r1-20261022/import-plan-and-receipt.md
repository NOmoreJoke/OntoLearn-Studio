# 导入预演、原子提交与receipt

P名称均为内部设计对象，不是已注册的公共协议。T10不实现第二writer、不写共享Store表、不把现有create_project/CAS/backup当完整import。

## 1. 参与者与不透明能力

| 参与者                       | 唯一职责                                                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| renderer                     | 表达导出/导入选项、显示安全摘要、用户预览与确认；不提供FS路径/原始包/任意plan或writer命令                          |
| I06/T01 main协调             | 校验可信window/mainFrame/project/request/profile代次；持有picker/输入handle/位置能力/plan ticket，绑定实际用户确认 |
| T10包适配层                  | 有界编码/信封和业务schema核验协调、清单/选项/引用完整性、错误及报告投影；只消费owner固定输入                       |
| T01业务服务/唯一Store.commit | 全部payload语义、typed引用/身份映射/CAS；一个外层事务创建新项目、状态/控制/源注册与唯一receipt                     |
| T03 source owner             | 受控附件准备/封存、字节/hash/格式证明与重关联，不根据包内路径随意打开                                              |
| I06私有与模型生命周期        | 操作能力、失效和实际新项目打开后的local上下文；导入不恢复grant或发送任务                                           |

建议P-PlanTicket仅存在main内，renderer得到不透明planId、planDigest、安全摘要与可确认状态；不能把全plan JSON往返renderer后直接执行。preview、commit、receipt lookup分别是将来待owner批准的业务方法，禁止通用invoke。

## 2. 状态机与预演

```text
selected-candidate → guarded-input → immutable-input-sealed → decoded → business-validated → preview-ready
preview-ready → user-confirmed → recovery-recorded → admission-pending → admitted → committing → committed
preview-ready → invalidated / cancelled
admission-pending → terminal-not-admitted (writer fence)
committing → not-committed / committed / commit-unknown
commit-unknown → receipt-reconciliation → committed / verified-not-committed / still-unknown
committed → optional-user-open → opened / committed-not-opened
```

1. 实际main picker选择；I06先批准候选，再实际绑定只读有界handle。取消无内容IO、无新项目、无授权。
2. 稳定handle只固定对象身份，**不保证同inode内容不可变**。必须先在受信IO能力内取得本次实际消费的有界不可变P-InputSeal：小包可由owner提供不可变字节快照，大包须有获批的封存对象/同等算法及持久pin。包digest基于该封存的完整实际字节；解码、业务预演和附件准备都只消费这个seal，不能确认后重新读原handle/路径。封存协议定义观测到源变化时的拒绝/重新选择及剩余平台保证，不能靠前后stat/旧SHA宣称任意同UID攻击下的原子文件快照。封存后有界核manifest/成员/预算/未选内容，再核业务schema/版本、owner关系、typed闭包和引用。无法保证同一封存消费则阻断。
3. T01只读预演生成P-ImportPlan：源包hash、manifest/各集合digest、schema/canonical/支持版本、kind/options、scopeDigest、完整性与缺依赖、typed重映射计划、目标“仅新项目”、预览摘要/冲突及资源证明、owner接口版本、受信上下文代次和可确认状态。
4. 目标身份由唯一owner产生，不用包内sourceProjectId。建议预演阶段取得main内未发布的identity reservation，或者用批准的符号namespace至事务内解析；两种策略由F13固定。不得在用户确认前创建可见空项目，也不能在确认后静默换目标计划或重算不同映射。
5. 预览显示实际业务范围、必需/已选/未选内容、对象/记录摘要、来源/所有权保留、类型重映射、三能力逐项结果与理由、缺依赖重关联、未支持/冲突、原子新建和既有项目不覆盖说明。详细业务值只在受控视图中按权限展示，错误消息不dump。
6. 形成绑定`inputDigest + scopeDigest + planDigest + relevantVersions + contextGeneration`的确认。任何内容/选项/目标/支持版本/来源能力或相关代次变化使旧确认失效，重新预演。不可由Agent、包内字段或“曾点过导入”代替这次用户确认。

只读预演不得写领域状态或调用外部模型/网络；若需要input封存、pin或恢复日志，只能由对应唯一owner按本合同写受控操作元数据/准备对象，不得借业务snapshot()等持久化API充只读投影。大型包不通过IPC或JSONL单帧搬运，使用owner受控引用与有界分页摘要，遵守现有协议帧/错误参数上限。

## 3. 类型化身份重映射

先按正式schema枚举实体类型/身份作用域和typed引用边，再由T01生成新project及所有必要全局ID；只重写声明的引用字段。项目作用域定义/fact/source-row/owner的保留或重映射由F13指定；全局run/job/attempt/operation按owner规则生成本地历史身份，绝不接管活跃运行/旧claim。业务literal如“设备A引用项目p-old”的文字不可递归替换。

重映射后逐项验证：唯一性、跨项目/类型、悬空/重复冲突、规范RDF表示、owner/managed/tombstone关系、mapping generated版本、before/after控制范围和所有digest/引用。含project身份的快照/checkpoint/结果摘要必须重算；保存来源原digest与新digest的映射证据，不修改来源历史，也不让旧digest指向新对象。必要字节完整性、typed来源/owner关系或引用语义不成立/未知类型时阻断，不能“留待使用时再查”。**仅foreign producer/actor外部身份真实性未认证是另一条信任轴**：未签名但结构/业务完整的包不因此自动拒绝核心数据导入，而按F09保留来源主张/unverified标签，不升为本机真实学习/授权；如未来获批政策另要求认证，明确提示该政策，不能由本句偷偷引入强制PKI。

## 4. 唯一事务与附件可见性

T01在同一个外层Store.commit事务完成：

- 复验plan/确认/相关CAS、唯一request/operation与plan绑定，目标身份未占用。
- 创建新public/internal项目身份，写全部定义/断言/来源所有权/墓碑/版本、应用/learning业务状态、必要typed历史/撤销控制及新genesis/checkpoint。
- 注册已准备的不可变附件引用并核完整性，形成可见版本与映射账本。
- 同事务写唯一import receipt及commit marker；失败回滚全部可见状态。不能先create_project后多次提交拼接，也不复制旧active job/context/grant。

FS附件不是SQLite事务的一部分。建议T03/I06先在受控、对项目不可见的新对象空间从同一P-InputSeal准备并封存完整字节；但**不可变、耐久、禁止GC回收是三项不同保证**。唯一owner还须提供以下持久prepare/pin与发布协议（F14），否则不能提交附件引用：

1. P-ImportPrepare身份绑定operationId、input seal digest、plan fingerprint、精确对象集合及digest、stateVersion和持久pin generation。对象成为GC可见前或与其同时，权威registry已登记preparing状态和durable pin，跨进程/崩溃存活；准备未完成不标sealed-ready。不能仅用main内Map/WeakMap、TTL或文件存在代替。
2. 完整字节flush/耐久性与hash/身份验证后标sealed-ready；输入seal和每个导出附件均受同一prepare保护。Store新项目commit在其权威事务中核prepare/operation/fingerprint、对象集合、pin generation、sealed-ready且未被GC claim/fence。
3. **项目引用、import receipt及prepare从pin转为committed references的接管必须在同一权威可见性边界**完成。建议T01单一事务源同时持有这些registry状态；若跨服务，owner必须给等价线性化证明，不能留“引用已提交但pin已先释放”的窗口。
4. GC取得删除claim和import取得/转换pin使用同一权威排序。只有无prepare/admission/unknown pin、无committed引用且generation匹配，才能原子claim可回收；GC已claim的对象不可被随后导入引用。实际删除前重验该claim/generation与受控IO身份，不能用早先无引用查询后无限期删文件。
5. commit-unknown保留pin并按原operation对账，不按超时/TTL自动释放；资源不足时拒绝新prepare而非回收未决对象。只有writer证明终局未提交且迟到请求已fence，或committed引用已正式接管，才能按对应分支释放pin。回滚/取消按钮本身不授权释放；orphan进入独立受控GC，不递归删陌生文件。

事务提交使新项目和已准备对象引用一起可见；准备失败不发布，原项目/附件不改。若持久pin、跨GC排序或平台耐久性证明缺失，拒绝该附件导入，不能以事后补偿称原子。

事务内及提交前取消/错误=未提交并回滚；提交持久化后才收到取消、通知失败、窗口崩溃或模型错误，仍为committed。不能为满足取消按钮删除已建项目，也不把后续open失败改成“导入失败未创建”。磁盘耐久性、source准备/发布、Store receipt与cleanup的精确协议须T01/T03/I06同版批准（F14），本提案不声称Node路径复验即可实现。

## 5. receipt、幂等与不明提交

建议P-ImportReceipt包含：receiptSchema/version、requestId/operationId/planDigest/inputDigest、明确commitState、唯一newProjectId与本地checkpoint/genesis/revisions、importedScopeDigest、ID映射digest、源业务版本与本地schema版本、source对象集合digest、可安全公开的缺依赖/能力摘要。无路径、原始异常、凭据/endpoint主体或旧授权。receipt是真实Store提交记录，不由T10按expected填造。

### 5.1 首次发送前的恢复身份与writer权威账

main-only ticket只是活内存能力，不能作为崩溃后唯一恢复入口。建议唯一main协调owner在首次向writer发送受理/提交前，先耐久保存P-ImportRecovery记录：recoveryId、当前本机profile/application归属、稳定businessRequestId/operationId、input/scope/plan fingerprint、prepareId与sealed对象/计划的受控引用、targetMode、确认的历史证据引用/版本及dispatch状态。它是受限本机操作记录，不是可移植项目payload或普通日志，不含凭据/发送grant；完整业务plan如需保留也只能在受控封存对象中。崩溃前没有成功持久化就不允许发送，重开能按当前合法本机归属列出未决import，不从包hash猜operation（同包可被用户合法导入多次）。

稳定businessRequestId/operationId与每次传输的RPC requestId分开。重连可以新RPC id，但必须关联原业务身份/精确fingerprint；恢复记录不允许自动获得新的确认或外发权。

writer在**同一全局operation claim空间**持久化并原子排序：admitted（含fingerprint、prepare、计划引用、admission sequence/fence version）、committed（同项目/receipt事务）、terminal-not-committed（有负终态/fence）。lookup的unknown是尚不能查明的观察状态，不以“无receipt”生成终局未提交。新admission、commit、cancel/fence与精确重试受同一权威排序：

- 相同operation+fingerprint先查权威既有结果，committed返回原receipt，admitted只恢复该次处理/对账，不先按今天新CAS/旧proof当新写检查；不同fingerprint冲突。
- 即使请求还未admit，明确取消/判定终局未提交也必须落同operation空间的负claim及单调fence，使所有迟到admission/执行不能再commit；已committed则只能返回committed，不倒退。
- admitted执行在最终Store事务复验claim/fence/pin generation；负终态或fence胜出后拒绝迟到commit。只有证明旧执行和迟到请求均已被此机制阻断，才产生verified-not-committed。
- main崩溃后的恢复先按P-ImportRecovery和writer账查询，不靠活ticket、旧lease、旧CAS或再次确认重建事实。记录/封存计划缺失而仍可能执行时保留unknown，禁止新operation；不能凭用户重新选同包推新请求与旧请求等价。

具体恢复记录、claim/fence持久化schema及负责的唯一owner列F19，全部尚待批准；现有T01域receipt只是原语，不声称已满足上述完整import协议。

### 5.2 对账与lookup归属

幂等键由本地本次请求生成，不采用包内operationId。原operation精确重试先返回既有权威状态；已committed返回原receipt，admitted只恢复原处理/对账，负终态不重开，不重复创建；同键不同plan/digest固定冲突。跨项目同ID/跨profile读回由实际身份scope检查，不能只靠全局唯一字符串授读权。

响应丢失后只调用P-ReceiptLookup读取原request/operation对应权威记录；不得自动重放import或网络写。查询结果需区分：已提交并有可核receipt、能权威证明未提交且原执行不再可能提交、仍不明。仅“暂未查到”不证明未提交。仍不明时阻止新幂等身份重试并保留对账入口；允许恢复原执行时必须复用原业务身份与同plan。只有原operation已获权威负终态fence后，才可依正式政策由用户重新预演/确认产生新operation；新operation不是复活旧执行，不能自动换ID。lookup本身不得改变项目、选择或授权。

lookup以**当前合法读取权限**核原operation归属，不要求当年旧source lease/WeakMap proof、旧window generation、原CAS或再次人确认仍存活。新项目尚不存在/ID未知时，按受信main的本机profile/application归属及recoveryId/operationId匹配P-ImportRecovery和writer账受理，不能先要求读一个未知新project或持有失效ticket。receipt返回newProjectId后，实际打开另按当前项目读权限与用户操作校验。历史admission/确认只作当时证据，不反序列化为新活权限。新受理实时门与旧operation对账先分流；权威负终态fence/barrier证明原operation无论此前未受理或已admitted，都已终局未提交且不可能再受理/提交后，才可按正式策略允许新确认/新operation。

## 6. 冲突和失败矩阵

| 触发                                            | 预期行为                                     | 固定错误类别建议                                                                      |
| ----------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------- |
| 包/源对象字节变动、选项/目标变化、旧确认        | 旧plan不可提交，重新预演                     | PLAN_INVALIDATED                                                                      |
| schema/canonical/reader/writer或实际实现不支持  | 不建项目，列受限版本信息与迁移路径           | FORMAT_UNSUPPORTED / PAYLOAD_UNSUPPORTED                                              |
| 缺必需集合、owner冲突、悬空引用、闭包含未选内容 | 阻断full，指向具体安全定位；不自动降模板     | COVERAGE_INCOMPLETE / OWNERSHIP_CONFLICT / REFERENCE_INVALID / SCOPE_CLOSURE_CONFLICT |
| I06 inventory不完整、位置失效/别名相交          | 对应首次/后续IO前拒绝，只停本次transfer      | TRANSFER_LOCATION_UNAVAILABLE                                                         |
| source seal或durability不足                     | 不提交引用；保留受控准备/清理状态            | SOURCE_PREPARATION_FAILED                                                             |
| 目标冲突、同operation不同plan、事务CAS变化      | 原子拒绝，原项目不变；重新预演/对账          | IMPORT_CONFLICT                                                                       |
| Store提交中失败/取消                            | 无半新项目或半owner，原状态可读              | NOT_COMMITTED                                                                         |
| 已提交但响应/窗口/模型失败                      | receipt仍真，提示已创建未打开/待对账；不重建 | COMMITTED / COMMIT_UNKNOWN（权威结果未获时）                                          |

这是错误语义提案，最终复用I03/T01/I06批准错误表，不新增到源码；跨边界仅固定code/messageKey、受限定位/计数，不能带路径、单元格值、堆栈或私有状态。

## 7. 新项目打开与模型边界

只有可核正式receipt、真实用户要求打开且最后await后相关window/request/project代次仍有效，main才以writer返回的newProjectId打开/选择。迟到receipt不抢切项目；committed-not-opened有显式入口。包内选中jobIds一律不作为新任务恢复依据；拟沿已接受设计调用`tasks.selectProject(newId,[])`，实际API与代次适配仍由对应唯一owner批准。

新project/context/local由本机真实服务创建；I06旧grant/preview/context/endpoint授权不能继承。独立profile及同profile均须按实际接收端重新选择/预览/确认后才可发送，确认前receiver=0。模型未就绪、网络/审计故障不阻断本地项目打开和Store保存。正常同项目窗口恢复不无故清空合法现有授权，也不自动导入/续跑/重发。
