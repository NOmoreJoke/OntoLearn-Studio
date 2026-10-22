# N0 held对象观察与ACL合同

本合同采纳根前提独审：UUID presence可替换；不要求单次原子metadata调用或installed系统库与公开源码逐字同源。仍必须实际观察同held对象、协调自有变更、拒绝非空或未知ACL，并使冻结目标环境中既定策略的受控empty正例成功。**当前源码仍不能完成该正例；本文件没有批准一个只在偶然header上成功的修复。**

基准904cc2675c37387621954bb5a39a055c09d492b3，实际产品仍1217e0f63a9c62b72e01046ef5fbc5c53434251a。根前提独审12583B/855e591907422e3d9c1ef98510d230261e4f126a4cfd0d6c982e51375f221eae和4225B精确窗口保存在本目录；源码/证据pin见evidence-and-preservation.json。本阶段不改产品、测试、ABI、锁或控制算法，不运行API、探针或构建。

## 观察范围和装配责任

N0只给本次held对象的metadata观察：production_admission始终0；acl_checked=1表示本次采用充分ACL证据并完成必要收尾，held_object_only=1不表示名字持续指向该对象。root API可返回adoption时缓存的root记录，不能把它说成每次都重新查OS。需要刷新时由既有observe/acquire重新观察；缓存、标量相等和held FD均不是权限lease或ABA不可能证明。

| 阶段              | 受信harness责任                                                                                                                                       | native现有责任及边界                                                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 建立/准备         | 独占新fixture；完成权限/ACL setup和必要子项创建，检查返回及owned对象释放；未进入观察时才可改动                                                        | 不从renderer/JSON接收路径或整数handle；borrowed对象只来自受信native harness                                                               |
| 开始adoption/观察 | 保持borrowed FD live且不关闭、复用；明确冻结该受控对象的owner/group/mode、ACL、links和自有namespace mutation，直到同步观察返回。进程不改变euid/groups | admission先预留、try-lock gate；至多一条OS观察链执行。gate只协调经native的调用，不会自动锁住harness直接syscall或整个OS                    |
| 多次查询          | 不并发执行直接chmod/chown/ACL set、link/unlink/rename或fixture cleanup；测试通过单线程阶段安排实现，不新增OS锁                                        | 始终原held FD，不path reopen；以实际返回对象身份和标量检查；遇矛盾非成功，不把多调用拼成单一原子时点                                      |
| 返回/变更下一阶段 | 观察返回后才可作原测试的rename/link/symlink/替换，下一观察必须重新核验；自有变更调度必须和native观察阶段互斥                                          | acquire保留实际opened对象，并用expected identity作拒绝filter；parent重查、普通替换/alias拒绝和no-follow保持                               |
| 撤销/晚返回/关闭  | 不抢关native已复制对象；每个非零失败owner也交原owner close；不把BUSY/RETAINED当释放                                                                   | revoke刻意可在gate外原子改epoch；adoption/acquire/observe的late active/TTL检查保持。已知FD只close一次，未知责任留原slot/owner，不重用号码 |

这里把ABI的“stable”具体化为受控观察期间的借用对象和自有metadata变更约定，**不声称现注释已自动冻结所有权限字段**。当前fixture的ACL setup在create前，one-ACE设置也在被测create前；namespace负例安排在同步API之间。未来若引入自有权限/ACL mutator，必须纳入同一调用协调，不能仅靠数值重读。此合同不是给未实现mutator预授入口。

任意恶意同UID进程和全盘DLP不属于原N0边界；对外部未知窗口不签持续许可，不给production admission。必须拒绝实际观察到的identity/type/owner/mode/link/ACL矛盾，但不能虚称已经检测所有外部ABA。无需为了采用多调用技术路线先问用户降低一个从未要求的原子性门。

## ACL状态必须是对象状态，不能只是API状态

以下为Darwin适配逻辑合同，不新增公开ABI枚举，也不把Windows的NULL DACL类推成NOACL。F表示正式接口/SDK语义；I表示特定公开实现；T表示尚待目标实测或解析实现验证。

| 观察                                                                             | 可认定的对象ACL状态        | 依据与决定                                                                                                                |
| -------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| API非成功/超时前门/权限或分配错误                                                | Error或Unknown，不是空ACL  | F：失败没有成功ACL证据；不读失败残留输出，不以errno白名单变成功。ENOMEM→BUDGET、权限→DENIED，其余未知→UNSUPPORTED为拟映射 |
| filesec query成功但ACL valid=0；或fgetattrlist缺security返回位/零长占位          | UnknownAbsence，不是Absent | I显示缺省可有多种原因；现选定正式材料没有对象级缺位=无ACL合同。setup成功、卷能力和其它标量成功都不能单独补这条语义        |
| acl_get_fd_np返回NULL，即便errno=ENOENT                                          | Error/Unknown              | F：官方acl_get手册规定NULL是失败，不是缺省ACL成功。不得吞错误或从路径ENOENT推FD对象状态                                   |
| 成功取得真实独立ACL副本，valid通过且按已冻结Darwin规则明确无entry                | EmptyValid，候选无ACE      | F支持独立working copy和释放义务；具体empty枚举规则须在目标版本验证。不得把getter哨兵或未知输出交给valid/free              |
| fgetattrlist成功，必要mask/完整长度/引用/目标ABI均验证，合法完整payload明确NOACL | AbsentProven候选           | F给结构/长度框架，SDK定义NOACL区别；I只是补充解释；T为目标实际表征及严格解析器。不能跳过有效性或把缺位当此状态            |
| 同上，但合法payload明确count0、没有未知格式/规则                                 | EmptyValid候选             | 与NOACL分别记录，不强造第二种表征；raw count0单独不构成有效ACL证明                                                        |
| 有效对象ACL含任意ALLOW或DENY ACE                                                 | AnyACE                     | 原策略DENIED，不按当前effective permission放行；setup失败不能冒充此负例                                                   |
| 短/畸形payload、非法magic/长度/flags、相对引用越界或跨响应矛盾                   | Malformed/Contradictory    | UNSUPPORTED或按原安全策略DENIED；始终非成功，不用零初值补字段                                                             |
| owned ACL释放失败或输出所有权/释放未知                                           | RetainedUnknown            | RETAINED优先；已知副本free一次，filesec_free为void不制造返回值；不能换API后忘记这次未知责任                               |

仅AbsentProven或EmptyValid、原type/当前UID/mode/link及实际identity检查全通过、所有可检查收尾成功，才允许acl_checked=1及NL_OK。Unknown/错误/释放未知永远不能用于生产许可。反之，**把全部合法empty输入都分类Unknown，不算完成N0可用性**。

## 正式合同、实现解释和目标证据分开

1. [Apple acl_get官方手册](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/acl_get_link_np.3.html)给成功working copy、NULL错误和acl_free责任。它没有给“NULL+ENOENT是absence”的FD成功分支。
2. 固定XNU f6217f891ac0bb64f3d375211650a4c1ff8ca1ea的getattrlist手册，已有必要摘录证明同FD、实际返回mask、REPORT_FULLSIZE、4字节packing及attrreference；足以核验实际返回payload。SDK声明宏本身不自动证明不可用；目标ABI/版本绑定由正常静态编译和目标验证取得，不要求系统库源码身份证明。
3. 同固定security packing在va_acl支持且非NULL才置security位，其余可省略/占位。这解释缺位歧义，但不是installed行为认定或通用absence合同。不能据此否定所有公共API路线。
4. 精确filesec/fstatx absence正式条款仍未取得：本次一个官方目录定位请求遭HTTP403 rate limit即停止，未重试或认证；两个精确官方raw手册路径404、一个Apple归档页不可访问。它们是定位/访问失败，不是合同不存在。未大搜其它API，也未扩展SQLite/heap/OS资源线。

本合同不再把UUID presence或installed源码同源作为独立交付门；若有充分正式语义即可替换它。单次原子snapshot也不是阻断理由。现在真正缺的是**受控empty目标对象的可判别ACL响应**：在所选接口里，empty setup后到底走可证明Absent/Empty，还是仍只有歧义缺位。源码片段和声明都不能替代这个目标证据。

## 完整正例路线与当前结论

必须覆盖原controlled root、sub目录、普通member以及替换后新member的正常owner/root/acquire/observe和关闭；普通文件仍nlink=1，目录nlink非零，当前UID且无group/other写，真实ACL无ACE。操作系统可规范化empty表征，但适配路线必须接纳冻结环境的这些必需输入，不能让它们全部UNSUPPORTED或skip。

正式接纳路线应是固定目标profile的一条权威ACL读路由：例如经充分合同和实测选定fstat+fgetattrlist，或已证实的owned ACL getter。不得在某API失败后动态换一种读法直到成功，也不能因已知setup而省略实际ACL观察。若选定路由不产生这些必需正例的充分证据，就放弃该路由、保持模块未完成，而不是缩小正例域到罕见header。

当前没有可直接进入产品源码窗的完整路线。建议仅将decision-experiment.md作为**另行审批的有限目标表征实验提案**：对原样empty cohort和有真实ACE的对照，用固定同FD调用，预先约定全部正例必须得到充分响应；任何正例缺位/占位就停止并判该路由不可采用。它不是修复或完整测试通过，且本窗口没有执行。

若实验显示全部必需empty对象均有正式可判别NOACL/有效empty，同时对照明确有ACE，才值得冻结该目标profile和解析/ownership细节，申请最小两writer实现、T03新输入构建及真实原case验收。若仍缺对象级absence语义，可继续内部补精确官方合同或目标版本依据；不需用户为UUID字段、原子调用或源码同源降低门槛。真正改变威胁边界、目标OS或ACL政策才需要明确的新决定；当前不提这种降门。

任何后继适配最小writer为Mac platform_metadata/私有有界解析与Darwin fixture witness两路径；ABI/core/Windows/Node/TS和原gate/epoch/TTL/关闭规则不扩大。若新接口仅使用应用buffer、不创建ACL工作副本，就没有相应acl_free对象，但不能忽略已经创建副本的释放失败；FD和owner责任不变。进一步源码设计必须冻结精确mask、packing、有效性、有限错误与budget，并分别处理缺位和明确NOACL，不沿用“未知即成功”。

本阶段完成的是可审合同和准确缺项，**N0功能仍未完成**。003/004失败、drain/fixture未知、内部资源硬界、目标双OS、完整父功能、指定同版外审/CI/真人/远端及T01损坏保护HOLD保持，不因本设计关闭。
