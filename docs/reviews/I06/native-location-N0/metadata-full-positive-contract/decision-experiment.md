# 有限目标表征实验提案：决定采用或放弃，不是本轮许可

**尚未创建实验源码、构建、record或运行目录，未调用任何API。** 本提案只针对已经有正式返回结构合同、但未知冻结宿主实际empty表征的fgetattrlist路线。它不学习“缺位=absence”的新规则，不承诺恢复正例，不以全部UNSUPPORTED交付N0，也不需要installed源码同源证明。

## 决策价值与唯一问题

要回答的是：在和原正例相同的root/sub/member建立及FD模式下，是否每个必需empty对象都能得到正式可判断的完整NOACL或有效empty payload，并且真实单ACE对照得到非空ACL？不是分辨UUID的两个布尔位。

预先冻结两个结论，不作环境调优或重新setup追绿：

- **采用候选进入下一设计/源码门**：全部三个empty对象均取得完整可判别无ACE响应，两个单ACE对照均得到完整恰一条ACE响应，标量/身份一致且setup和所有可检查cleanup成功。这里只证明该固定目标profile值得适配，尚不等于owner/root/acquire、撤销/关闭、异常或N0功能通过。
- **放弃此route或保留缺项**：任一必需empty对象只有security缺位/零占位，即判fgetattrlist-only方案不能完成该profile的完整正例；不做条件解析器当修复。API拒绝、畸形、未知flags/有效性、矛盾或对照不符则相应证据未取得，原件停止；只有已批准的新合同依据才可后继，不盲重跑。

若root认为当前信息不足以值得这次实验，也可继续内部补精确对象级absence合同；不要求用户降低ACL策略。实验为一次有采用/放弃后果的提案，**不是当前批准的第七产品构建或API诊断**。

## 最小实现/构建责任（均待另授）

建议独立的一次性、单用途测试源，拟I06唯一writer为`packages/native-location/tests/location_metadata_contract_probe.cc`；当前该文件没有创建。它只输出有限对象响应分类，不接收用户路径或任意API参数，不做通用runner，不链接产品owner注册表或改现有测试的期望。T03唯一维护该实验的精确输入/SDK依赖/锁/编译命令/预算，具体路径须root另窗指定；不能由I06改CMake、driver或借用他线可变环境。

独立实验避免被现有UUID断言提前终止，也避免把一次新观测冒称已执行生产metadata。不能暗改现有core main、复用旧产物或让原positive skip。若目标表征支持路线，后续产品实施仍须另授Mac metadata和Darwin witness两writer，并跑原全部case；这个私有实验源不代替产品交付。

root须先选定固定宿主/profile、目标SDK/ABI、单次可执行产物pin和捕获窗。已有host/build记录用于身份绑定；实验不额外调用系统版本、资源、DB或进程信息接口。当前不生成精确调用或新pair。

## 输入和协调：两个新fixture，最多五个样本

原构造方式建立一个empty fixture E：独占临时root、原O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC anchor，成功acl_init(0)/acl_set_fd_np并free，再按原方法mkdirat sub(0700)、openat创建member(0600)并关闭创建FD。**不给E-sub/member另设ACL来强造header**，保持原empty根下正常创建/继承的输入；若它们实际有ACE或无法证明无ACE，该正例路线不合格，不重建重试。

E全部观测合格后才创建独立对照fixture N。原root empty setup后创建sub/member；当前owner UUID只取得一次供两个对照qualifier使用，不输出值。N-member在自己创建的O_WRONLY FD关闭前建立恰一条ALLOW/ACL_READ_DATA、零flags的有效ACE；随后N-root建立恰一条ALLOW/ACL_LIST_DIRECTORY、零flags的有效ACE。每次setup的create/tag/qualifier/permset/flagset/valid/set均检查，一次free。对照不通过setup就终止，不算安全负例成功。

| 固定case id | 对象和实际观察FD模式                                              | 必需对象状态/后继                                                |
| ----------- | ----------------------------------------------------------------- | ---------------------------------------------------------------- |
| 0           | E-root，原fixture anchor                                          | 完整NOACL或有效empty；否则停止并拒绝采用route                    |
| 1           | E-sub，`O_RDONLY\|O_DIRECTORY\|O_NOFOLLOW\|O_CLOEXEC\|O_NONBLOCK` | 同上，不能跳过子目录正例                                         |
| 2           | E-member，`O_EVTONLY\|O_NOFOLLOW\|O_CLOEXEC\|O_NONBLOCK`          | 同上；必须用生产普通member的metadata-only模式，不能换read FD求绿 |
| 3           | N-root，原anchor                                                  | 完整恰一条ACE；否则停止，不当成功                                |
| 4           | N-member，和case2相同的O_EVTONLY模式                              | 同上，setup FD不代替实际观察FD                                   |

每个metadata FD从open至close归本实验所有；两个member各在创建FD关闭前额外一次fstat记内部预期identity，之后O_EVTONLY观察FD的实际identity必须核同，真实数值不输出。setup与观察都来自同一独占root，没有借用外部未知FD。观察期间不改owner/group/mode/ACL/link/namespace，不关闭或复用任何相关FD；所有自有setup和清理在同步观察之外。不是OS锁、原子snapshot或抵御任意同UID进程的协议。

只操作自己的固定root/sub/member名称，不扫描/tmp或旧fixture，不改系统ACL、用户/组或旧PID。全部相关FD已在创建/打开时取得，失败只对这些自有对象做规定收尾；不搜索残留。

## 每样本固定读法及解析前门

每个case最多一次观察fstat及一次fgetattrlist，顺序固定，不扩容、重复观察、换API或换flags；加两个member创建时的身份记录，总计最多五次fgetattrlist和七次fstat。两次创建身份记录不是重复ACL查询，必须列入另授API范围；遇先前非成功分类即停止，后续case不执行。任一创建或观察fstat失败都不继续相应fgetattrlist。

进程一次geteuid取得setup/比较的当前owner，整个实验禁止自有UID/groups变更；成员UUID仅对照前一次mbr_uid_to_uuid。每次fstat保留原type、owner==euid、mode无0022、目录nlink非零/普通文件nlink=1检查。任一安全条件不满足为fixture输入不合格，不是ACL正例失败的替代证明。

fgetattrlist请求字段固定为RETURNED_ATTRS、DEVID、OBJTYPE、OWNERID、GRPID、ACCESSMASK、EXTENDED_SECURITY、FILEID；仅普通文件另请求FILE_LINKCOUNT。vol/fork字段为0；目录不拿DIR_LINKCOUNT替代stat nlink。options为REPORT_FULLSIZE|PACK_INVAL_ATTRS，应用buffer固定4096B并置零，一次复用，绝不根据返回大小再申请或重调。

先检查返回码并立即捕获失败errno；成功遗留errno不使用。仅按正式4字节packing，以memcpy取值；检查最小前缀、完整所需长度、必要actual位、属性顺序及引用的有符号offset/加法溢出/对齐/变量区起止/attr_length。缺位占位不解析成值。DEVID/FILEID、type、uid/gid、权限位和普通file links与同FD fstat核同；ACCESSMASK只比较已定义权限位，不把其type bits当保证。

只有完整合法kauth header、magic、长度/count和flags前门全成立，才记录明确NOACL、empty或ACE。本次实验保守固定collection flags必须为0，不靠未知private位推权限规则；非零为unproven，不学习白名单。令H为目标SDK中kauth_filesec的ACL起点加kauth_acl的ACE起点，A为一个kauth_ace大小；NOACL或count0的attr_length必须等于4字节对齐后的H，对照count1必须等于对齐后的H+A。先区分NOACL常量，再做受检乘加，禁止用哨兵作条目数计算。其它count或多余尾部均不签本次预期响应，不能由raw count单独“验证”。

两个N对照还必须在同一已验证payload内核唯一ACE本体：`ace_applicable`逐字等于内部owner UUID；`ace_flags`精确为ALLOW的`KAUTH_ACE_PERMIT`编码，不含继承或其它entry flags；`ace_rights`精确等于该case设置的权限，N-root为`KAUTH_VNODE_LIST_DIRECTORY`，N-member为`KAUTH_VNODE_READ_DATA`。源码/SDK冻结前须从正式目标定义核定`ACL_EXTENDED_ALLOW`到PERMIT、`ACL_LIST_DIRECTORY`/`ACL_READ_DATA`到相应kauth rights及字段布局的映射，不能只因数值碰巧相等就假设跨版本成立。映射未知、DENY、其它qualifier/flags/rights或任何矛盾均failed/停止，不记录form3，不得eligible；只用现有buffer和内部已取得UUID，不新增API或输出身份值。count1/header合法本身不证明这条真实对照有效。

SDK布局按上述symbolic字段和顺序解析；T03源码窗须用编译时断言核uint32为4B、attribute_set五个32位组、attrreference的32位signed offset及32位length、guid和kauth字段布局，并锁目标SDK/符号。不是当前source/runtime同源证明，也不因UNSTABLE宏自动否定API。若这些ABI条件不成立，不能构建运行此提案；不以当前sizeof声称各版本安全。

若尚不能给某字段合法解释，实验不能擅自把它归为valid：输出unknown并停止；这是对象语义/解析前提待补，不是更换环境或放宽规则的理由。

## 有限输出、所有权和错误

每个已到达case最多三条固定行，共最多15行；无raw payload、路径/FD/PID/UID/GID/UUID/owner实际身份或环境输出。下列为拟冻结schema，布尔只0/1，case只0–4，api/form是有限枚举；err只在API失败使用即时errno，其余为0，bytes/count仅在相应有效前门后有意义：

```text
N0 ACL obs case=%u api=%u err=%d bytes=%u attrs=%u sec=%u
N0 ACL obj case=%u known=%u same=%u type=%u owner=%u mode=%u links=%u
N0 ACL val case=%u ref=%u magic=%u form=%u flags=%u count=%u
```

api仅0=未进入读调用、1=fstat、2=fgetattrlist；成功或解析失败记最后已执行的调用，err仅调用失败有值。form仅0=未知、1=NOACL、2=有效empty、3=唯一ACE的tag/qualifier/flags/rights全部核同。attrs/sec/ref/magic/flags和known/same/type/owner/mode/links均为判定布尔值；flags表示集合flags已核为0，不输出原始位值。known表示观察fstat成功，same包含member创建身份和两读调用身份一致。未到达或尚未通过前门的字段写0；bytes只在成功且长度前缀可安全读取后记录完整所需长度，count只在合法header后记录UInt32条目值，NOACL哨兵原值按UInt32输出，不用于乘加。

另输出一条固定`N0 ACL disposition=<token>`行，token仅eligible、unproven、failed或retained，不输出任意异常文本。输出预算stdout4096B/stderr4096B、每行不超过96B；字符串/最大整数宽度静态核算须随源码冻结。stdio失败不重试、不伪造成功记录，成本非零；原外层单次控制预算不自动变更。

应用侧最多五个长期metadata FD、一个短暂创建FD、一个ACL setup工作副本和一个4096B响应buffer，两个新fixture各三个自有FS对象。该数字只是应用资源清单，不证明kernel/libc内部heap/调用/wall硬界；不开展资源接口分析。没有cap/owner/child adoption，因此实验不产生非零native owner；未来产品测试仍须关闭任何非零失败owner。

每个已知ACL setup副本只free一次；free失败或未知ownership优先retained/停止，不重试释放。每个自有FD只close一次，失败即退役号码并保留未知。清理只对新fixture固定名称按既定顺序进行；不把析构尝试、leader回收或输出稳定当drain证明。setup/查询/解释不合格后仍执行规定的自有收尾，收尾失败覆盖“完整捕获”结论。

私有实验disposition不使用“产品通过”：eligible仅全部五case及清理达到上述条件，表示可进入适配设计；unproven表示至少一个必需正例无充分语义；failed表示API/setup/畸形或对照不符；retained表示释放未知。只要不是eligible就停止该路线本次推进，保完整首失败，不复测。外层工具退出与实验disposition分别归档，即便捕获完整也不等于原core测试通过。

## 结果到行动：不以观测补写合同

| 一次实验结果                                                                 | 下一动作                                                                                                                           | 禁止的推论                                                                               |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 三E均完整明确NOACL/有效empty；两N的唯一ACE本体精确核同；安全/一致/清理全满足 | 冻结目标profile、选择唯一权威读路由及精确parser；再申请两writer源码、T03输入和原正反case验证                                       | 不宣布N0已完成、异常分支已覆盖或所有文件系统都支持                                       |
| 任一E缺security位/零占位，或只有另一些E可解释                                | 放弃当前fgetattrlist-only接纳路线；精确缺项为该对象的正式absence语义。可内部补官方合同/适用版本，未补前不得实现conditional成功适配 | 不因empty setup已知或N对照有ACE，就将缺位白名单为absence；不把少数header成功代替完整正例 |
| E无法用于原O_EVTONLY等FD模式，API失败或目标不支持                            | 当前profile路线不满足N0；停止并保边界                                                                                              | 不换成更强read FD、换卷/权限/环境追绿                                                    |
| N响应无ACE、setup/ABI/flags/长度/identity矛盾                                | 实验或路线前提不成立；停止并补具体静态合同，不能签负例                                                                             | 不把返回失败或数据丢失当DENIED安全成功                                                   |
| 释放/收尾未知或工具取消/超时                                                 | 保原件/未知，按本次精确控制窗口停止                                                                                                | 不重试、kill旧PID、清理未知残留或发起其它探针                                            |

这是对**实际表征**缺口的一次决策实验，不是解决缺失mask语义的经验训练。若它落入unproven，进一步工作仍可在现有威胁/功能目标内内部完成：取得精确正式对象absence条款或目标适用说明，再另审技术路线；不能以本实验替代该语义，也不能让用户为实现字段降门。

只有root另授实验源码/构建/精确一次CLI及setup/read/cleanup范围后才可实施；旧004许可已消耗，旧pair不能执行新实验。本文件不创建新record/目录、不改变旧算法/限额，不授第七构建或自动后继。
