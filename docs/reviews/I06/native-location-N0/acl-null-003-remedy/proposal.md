# ACL-null 003：定点修复方案（只读，待源码窗口）

建议用 **同一 held FD 的显式 fstatx/filesec 结果** 替代当前隐式ACL包装查询；只有完整元数据、扩展security envelope见证和ACL存在性结果一致时才允许“无扩展ACL”。`NULL+errno=2`、单独`ENOENT`、单独`query valid=0`均不放行。任意不一致/无法确认仍拒绝。此为可实施提案，未改源码/测试，未运行任何相关API。

003已固定为 `b0342c44c08441049edc7d246d201bd44ea35719`：仅证明本次acl_get_fd_np返回null后立即捕获errno2，不能唯一说明底层原因，也不倒填001/002。现有产品仍为fc9853，Mac8670B/e1fbbcd9c9b73916bd9a030da8bc237dd46230fdd8d0366f0e2424168d4cd71a。

## 证据身份与不足

Apple[acl_get官方归档手册](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/acl_get.3.html)将NULL定义为失败，ACL工作副本不参与访问控制判定。未据它把ENOENT改成功。

少量官方公开Libc源码已固定到 `71bbe350ab79eef58113991d817ccc6165061a64`，完整来源与快照hash见source-pins.json。它是公开代码语义线索，**不是本机libSystem身份/实测路径或跨版本承诺**；本方案的推论与必须做的真实验证分开。

| 已读来源                                                                                                                                            | 有限事实/推论                                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [acl_file.c:76–99](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/posix1e/acl_file.c#L76-L99)        | wrapper经filesec_init→fstatx→get_property→free，未给调用者独立层级结果，NULL可能压缩多条路径                                                                                 |
| [filesec.c:148–185、304–340](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/gen/filesec.c#L148-L185) | ACL属性缺省时getter报ENOENT；query成功与valid值是两件事，valid是位值而非固定1；query只说明属性valid bit                                                                      |
| [statx_np.c:156–219](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/sys/statx_np.c#L156-L219)        | 收到security envelope且NOACL、以及没有完整envelope两条路都会清ACL属性；前者置UUID/GRPUUID valid、后者清它们。realloc失败路径还可能带error=0退出，不能把fresh filesec当已填充 |
| SDK sys/fcntl.h、sys/stat.h、sys/acl.h                                                                                                              | 已读声明含filesec_init/free/get/query、公开OWNER/GROUP/MODE/UUID/GRPUUID/ACL属性和fstatx_np的inode64别名。filesec_free返回void；ACL_MAX_ENTRIES=128不是内部buffer/循环硬上界 |

SDK只保存必要声明摘录并给原文件hash，没有编译/链接/符号探针。四个filesec/statx归档手册URL在web工具不可访问；未用它们支持结论。一次raw源码TLS读取失败后从同一固定commit的官方GitHub内容API取回statx源码，未关闭TLS验证；这是资料传输问题，不是产品/API执行失败。

## 唯一推荐的生产增量

拟仅改 `packages/native-location/src/platform_macos.cc` 的platform_metadata及必要同文件私有cleanup helper；core/ABI/Windows/Node/TS/driver/限额不动。用成功的fstatx同时提供struct stat和filesec，替代当前独立fstat及acl_get_fd_np包装，不增加字符串路径、reopen、follow-link、ACL写入、chmod、重试或系统能力框架。

以下为设计数据流，不是已安装代码：

1. 先维持原FD值校验；新建一个fresh filesec，NULL即非成功。所有属性输出局部变量先初始化，禁止复用上次对象或残留valid bit。
2. 对原同一个held FD调用一次fstatx_np(fd, &sb, fsec)。仅返回值等于0才继续（不能只检查是否-1）；失败立即保存errno。不得以失败留下的sb/属性推无ACL。
3. 读取公开FILESEC_OWNER/GROUP/MODE三属性：每次get均须成功，值分别与同次sb的uid/gid/mode完全一致。套用原类型、UID、mode、link检查；identity/link输出只取这个sb，所有检查后再发布metadata，不先置acl_checked。
4. 查询FILESEC_UUID和FILESEC_GRPUUID：query均须成功且valid均为非零，只把存在性当作已取得完整扩展envelope的保守见证，不使用UUID值做权限授权。任一缺省/失败都仍UNSUPPORTED，不能因正例不通删除该门。
5. 查询FILESEC_ACL，先查函数返回码，再看valid。valid=0仅在步骤2–4全部满足时作为候选“明确无扩展ACL”；不看errno是否0或ENOENT。依据是固定公开statx代码中完整envelope+ACL缺省对应NOACL分支，这是**实现级推论**，不是通用文档保证。未知系统若见证不足继续拒绝。
6. ACL valid非零时，get_property取真实独立ACL副本。getter失败、NULL或SDK移除哨兵均不能当空ACL；哨兵不传给acl_valid/acl_free。对合法owned ACL保持现有acl_valid、首entry与errno规则：任何ACE（ALLOW或DENY）均DENIED；只有有效且首entry明确为空才候选成功，其他读取错误不作空ACL。
7. 先保存业务status和错误快照，再按所有权收尾：若持有真实ACL副本，acl_free只调用一次，真实失败覆盖为NL_RETAINED，绝不返回OK或重试；fresh filesec始终只free一次。filesec_free是void，不能虚构可检测“成功返回0”，也不能以它证明进程/后代drain。最后仅在候选成功且全部可检查释放条件通过时写原metadata字段（包括acl_checked/held_object_only）。

若getter失败却给出与合同不符的非NULL输出，视未知所有权而非可验证空ACL，不对未知/哨兵指针贸然free或放行；保持非成功/retained语义，由固定delta审查判定实现是否与公开合同一致。清理/诊断不得覆盖决策用errno，返回前恢复所保存的主错误快照；成功调用遗留errno永远不当失败/缺省判据。

## 错误映射与所有权

| 条件                                                     | 拟返回/资源动作（须新源码窗口批准）                                                                     |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| filesec_init失败或已知分配失败                           | errno为ENOMEM时BUDGET，否则UNSUPPORTED；无fsec可free，不猜NULL原因                                      |
| fstatx返回非0                                            | errno即时快照，使用原error_status映射；errno缺失/不一致仍UNSUPPORTED；fsec free一次。任何ENOENT都非成功 |
| 必需属性缺省、不一致、query/get失败                      | 已知ENOMEM→BUDGET，EACCES/EPERM→DENIED，其余未知/缺省/不支持→UNSUPPORTED；仅缺省ACL属性不能触发OK       |
| 原类型/UID/mode/link安全检查不满足；任意非空ACE或无效ACL | DENIED，先释放本次已知owned副本/fsec；安全门不放宽                                                      |
| 满足完整证据链的无ACL，或有效且明确空ACL                 | 仅清理完成后候选OK；不接受旧NULL/ENOENT捷径                                                             |
| acl_free真实失败，或不能确认副本所有权/释放              | RETAINED优先，保持原owner未知义务/拒绝；不二次free、不改成成功                                          |
| filesec_free调用                                         | void，只能按API合同调用并记录路径；没有可查错误码，不声称额外OS资源或后代已释放                         |

相较旧ACL wrapper，部分基础设施错误将被显式分类（例如ENOMEM→BUDGET）；这也是待批准的行为差异，不能伪装成纯日志增量。所有新分类都非成功，不改变owner分配/关闭或原预算。

## 反例与有限资源边界

- NULL+ENOENT可能是wrapper的属性层缺省，也可能是别的失败；旧输出没有区分，不能白名单。
- fstatx成功但短envelope也清ACL属性；仅“query成功且ACL valid=0”会混同未知。UUID/GRPUUID见证缺省就拒绝，不把“没返回security数据”解释为没有ACE。
- 公开realloc失败的error=0路径可留下fresh filesec；必需属性读成功且与sb一致、envelope见证可排除这类未填充结果。该源码现象不证明本机存在此实现或003走了它。
- query的valid可能为32等非零位值；不能写valid==1。属性present与ACL无entry也不能混同。
- 非空DENY ACE看似收紧权限也仍违反“无ACE”政策，不能按effective permissions自动放行。

应用侧最多同时持有1个filesec、1个独立ACL副本和固定大小stack stat/标量；不加owner/cap/child/FD、队列、异步或无限应用重试。query及OWNER/GROUP/MODE getter在所读源码为本对象字段操作；ACL getter另调用转换/分配入口，本次不证明该入口内部申请次数或字节。原acl_get wrapper本来已调用同一fstatx链，显式化没有新增该内部链。

但公开statx含for(;;)/realloc，ACL_MAX_ENTRIES并不证明其内部次数、申请字节或wall硬上界，且当前公开源码不能绑定本机libSystem。**本方案只证明应用对象数量/调用点有限，不声称内部heap或OS链严格有界。** 这项既有未知须保留；若root要求新增硬字节/系统调用上界，本提案本身不足，不能以成功用例或stdio日志关闭它。当前不建议新增通用trace/资源框架或重启已拒SQLite线。

## 精确拟writer与实施顺序

生产writer仅上述Mac函数及必要私有cleanup；新测试writer仅 `packages/native-location/tests/location_core_test.cc` 的Darwin ACL fixture/对应用例（可含必要membership.h）；保护Windows28个静态断言、现有五case、core/ABI/其余源与构建三writer。测试新增范围、状态映射、SDK/library调用及诊断文案必须在root新窗口明确批准后才写。

先独立审本最小方案，再由root授准确两文件源窗口；源码delta独审/九源pin与一次必要完整check及12源核验后，由T03另授新输入构建，真实正反用例和精确CLI再另授。当前没有源码、测试、ACL设置或任何运行许可；不能借计划自动第六构建/重跑003。目标语义或见证不满足时保持UNSUPPORTED，回报具体证据，不删安全门追求绿灯。具体真实验收见validation-scope.md。
