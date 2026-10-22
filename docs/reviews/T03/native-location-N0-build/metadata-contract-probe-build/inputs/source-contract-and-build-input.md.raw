# 单用途ACL表征源：静态合同与T03输入

状态 **NOT_BUILT / NOT_RUN**。只有新增私有源 `packages/native-location/tests/location_metadata_contract_probe.cc`；既有产品/test/ABI/CMake/driver/锁均不改。源基于7ea3固定提案，不接收路径或任意API参数，不链接产品owner注册表，不建立cap/owner/child。argc不为1只失败，不创建fixture。

## 字段、语义及ABI

`sys/acl.h`的命名定义给ALLOW、READ_DATA和LIST_DIRECTORY的语义，`sys/kauth.h`给PERMIT与vnode rights/ACE布局。为避免只靠数值巧合，固定Apple Libc 71bbe350的acl_entry setter、acl_perm add/clear/set和acl_translate native export必要摘录显示：qualifier复制到ae_applicable，tag设ae_tag，permissions复制到ae_perms；native export逐字复制qualifier、组合tag-kind与非kind flags、直接复制rights。与SDK语义名称联合支持本实验精确匹配，不声称installed libSystem与该源码同源。见source-evidence.json及七个必要摘录。

编译期断言预写8-bit byte、32-bit int/unsigned、属性组五个32-bit字段、attrreference的signed32 offset/UInt32 length、GUID16及kauth各offset/H44/A24；这些断言尚未编译。目标SDK变更导致断言失败须停，不能以宏名字或数值断言代替运行验证。唯一ACE必须qualifier逐字等于内部已取得owner UUID、flags精确PERMIT且没有其它位、rights精确LIST_DIRECTORY或READ_DATA，否则form不是3且failed。

请求固定RETURNED_ATTRS、DEVID、OBJTYPE、OWNERID、GRPID、ACCESSMASK、EXTENDED_SECURITY、FILEID，file另LINKCOUNT，vol/dir/fork为0；REPORT_FULLSIZE|PACK_INVAL。长度前缀、actual mask、4-byte顺序、完整固定区、字段身份/标量及普通file links核对后才处理SEC。相对offset在Int64中相加后核界/对齐；变量区紧随唯一固定区并恰好到完整长度，无重叠、缺口或多余尾部。所有读取memcpy，payload不转未对齐struct指针。

E缺SEC位或零长为unproven，N对照缺位/零长为failed，均不解析占位。magic、collection flags0、count和H/H+A精确长度均有门；NOACL先判，再受检乘加及4字节取整。E的非零collection flags不能签语义，unproven；N不符零flags的真实对照为failed。未请求owner/group UUID不当身份依据；header内两GUID不是所观察对象owner证明，实际owner依据同FD的scalar返回与fstat。

## 精确路径与调用核算

E按原root空ACL setup及正常sub/member创建，子项不另设ACL。case0 root anchor、case1目录O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK、case2 member O_EVTONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK。E三样本均充分后才一次mbr_uid_to_uuid并创建N；N-member在原O_WRONLY创建FD上设单ACE并关闭，之后N-root设单ACE；case3/4分别用原anchor和实际EVTONLY member。每个member创建时记录一次fstat identity，之后观察FD核同。UID只取一次，单线程没有自有权限/namespace变更插入观察。

| 调用                                                                                                                                           | 完整五样本路径最大次数 | 路径依据                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------: | -------------------------------------------------------------------- |
| fstat                                                                                                                                          |                      7 | 两个member创建identity + 五个观察各一                                |
| fgetattrlist                                                                                                                                   |                      5 | 每观察至多一，fstat/安全门失败不调用                                 |
| geteuid / mbr_uid_to_uuid                                                                                                                      |                  1 / 1 | UID在E前，UUID只在E全部合格后                                        |
| mkdtemp / open / mkdirat                                                                                                                       |              2 / 2 / 2 | 每fixture一root、一anchor、一sub                                     |
| openat                                                                                                                                         |                      5 | 两创建FD、E-sub、E-member、N-member                                  |
| close                                                                                                                                          |                      7 | 所取得7个FD分别至多一次，失败即退役号码                              |
| unlinkat / rmdir                                                                                                                               |                  4 / 2 | 两fixture已创建member/sub和root各一次                                |
| acl_init / acl_set_fd_np / acl_free                                                                                                            |              4 / 4 / 4 | E-root空、N-root空、N-member单ACE、N-root单ACE；失败短路或未知时更少 |
| acl_valid                                                                                                                                      |                      2 | 两个单ACE；原empty setup不增加验证门                                 |
| acl_create_entry、set_tag_type、set_qualifier、get_permset、clear_perms、add_perm、set_permset、get_flagset_np、clear_flags_np、set_flagset_np |                    各2 | 每单ACE各一，前门失败后不继续                                        |
| setvbuf                                                                                                                                        |                      1 | fixture前设stdout unbuffered，失败不建fixture                        |
| snprintf / fwrite                                                                                                                              |                   各16 | 最多五样本各三行+一footer，短写不重试                                |

这些为应用源码路径核算，static-source-check.json另列实际调用点；不是实际API轨迹。短路只减少调用，无重试/重建/resize/换FD模式/API fallback。常量路径只有自有mkdtemp模板及sub/member；不扫目录、旧fixture、PID或环境。

## 所有权、输出与决策

最多五个metadata FD、一个暂态创建FD、一个ACL setup工作副本、两个各三对象fixture；一个4096B复用响应buffer，另有340B固定五条Observation记账和97B行scratch及固定标量/路径。不是libc/kernel内部heap/syscall/wall硬界。ACL entry/permset/flagset为借用，不单独free。已知ACL一次free；create_entry失败且异常改变ACL指针、或输出所有权不明为retained，不猜free。FD retire后close一次；最终统一cleanup继续收其它已知资源。已创建名称unlink/rmdir任意失败也retained，不吞ENOENT。没有析构重试、exit/abort或C++异常路径。

先完成所有已知资源cleanup，再输出固定记录。因此stdout断开/SIGPIPE不会在输出阶段绕过已知资源收尾，不需增加signal/process API。异步工具取消/强制终止仍不能保证cleanup，外层须保未知；这里只覆盖同步代码路径，不能签drain或残留清空。所有stdio错误不重试、不签eligible；retained优先于其它结果。

输出保持原三schema和四个固定token，无raw身份/路径/payload/环境/异常。整数受Int32/UInt32和有限枚举/布尔限制，静态最坏三行71/63/64B，15行加最长28B footer=1018B，每行≤96B，stderr无程序写入。line helper另硬核总量/行数，失败停止后续写入；C运行时/外层工具诊断不属于该程序schema证明。返回0=eligible、1=failed或stdio失败、2=unproven、3=retained；工具真实退出/取消仍须另行捕获。

全部五样本充分、精确ACE核同及可检查收尾均成功才eligible，且核cases=5/fstats=7/attr_reads=5；这只决定profile值得后续适配，不是N0或原case通过。任一必需E缺位/占位就unproven，停止route；API/setup/畸形/错对照failed；释放/残留未知retained。无条件跳过正例，也不凭setup或对照补写absence语义。

## T03后续单用途构建输入建议（尚未授权）

仅此一个`.cc`为entrypoint，C++17，Darwin固定目标SDK/arch/profile由root/T03另窗选定；不链接capability_core、platform_macos、Node、child probe或产品测试main，不修改原CMake/driver。直接SDK头：sys/types.h、sys/acl.h、sys/attr.h、sys/stat.h、sys/vnode.h、fcntl.h、membership.h、unistd.h、uuid/uuid.h；C++标准头见源。native符号就是上表及static-source-check.json白名单，通常由目标libSystem提供，实际link/依赖闭包与SDK头/符号适用性只能T03另授构建核定，当前不宣称通过。

T03须以最终source ref/bytes/SHA作为唯一新输入，独立产物，不复用旧004 pair；补精确SDK/头依赖闭包/符号/编译参数/累计预算及artifact pin。这里不生成命令、产物、record或运行目录，不构建。之后仍须root先授单用途构建，再授一次精确CLI/setup/read/cleanup捕获窗；本轮不能代开第七构建或新运行。
