# ACL表征实验源：独立静态源码审查

结论：**最终候选未发现P1/P2阻断；本轮P3“缺security的N对照被分类unproven”已定点关闭。** 可供root按源码阶段收件，状态严格为 **NOT_BUILT / NOT_RUN**。不签编译/链接、目标接口支持、实验eligible、生产metadata修复或N0通过，不授权T03构建或CLI。

## 受审身份和范围

工作树/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0，实际HEAD/基准7ea3bfb06ff117f80f0aa770ab5f563b6b5c3b3e。本次新增源尚以工作区固定bytes/SHA审查，**基准ref不冒称包含新源**：

`packages/native-location/tests/location_metadata_contract_probe.cc`，20278B/SHA256 **6b6ff0969396c243c425dca507d0ea05732a0edb0123a264ab834cd2531690dd**。

已全文读根精确源码窗口、固定新源和七份必要SDK/Libc摘录，读本轮source-evidence、static-source-check、source-contract-and-build-input和handoff。前置设计为7ea3的15506B/55f073f1352ef7e621455a2fb70dfe92c6287e10c591459abf916ee4d532c1e7提案及既有完整合同；不重开旧17KB算法、18件包或供应历史。

最终本轮过程pins：

| 文件                                         | bytes | SHA256                                                           |
| -------------------------------------------- | ----: | ---------------------------------------------------------------- |
| I06-metadata-contract-probe-source-window.md |  4746 | 7eca703961cfafedc130d4e864ae9394f3a52d136256973614a43b73f90ec3f6 |
| source-evidence.json                         |  3621 | 5afb7c58d5154e7bd6083a5c7e7c273e15f4e6176e5f65c24758fa54a5ccb176 |
| static-source-check.json                     |  4313 | ef9e47f81135bc7485c4efebd20bbd7be286ae3645f1253e207b2a8485511c8c |
| source-contract-and-build-input.md           |  9791 | b6ffa8fb11d8236fb9d029f67ff325d67dff270397a2a6c2f302d5f30aa8db0f |
| handoff.md                                   |  2774 | b698cbc74e0a536bd29f7a4be2f78bc0bf79666cfbeebfc0cbff24ecfceed3dd |

全程shell显式cwd为本树，仅源码/文本/JSON/哈希/静态算术；未预处理、编译、加载native、import产品、测试/npm、API/ACL/FS/进程探针、fixture创建、扫描/清理/kill、GUI、Goal或提交。只写并格式化本报告。已实核九源和AGENTS当前字节与保护pins相符，不重审其逻辑。

## 本轮发现和处置

P3-01（已关闭）：在20249B/f53d11c300381c01996ecd9d6316c45d9f26c4a9e3a8727b335f886565e7d479的parse:294，security位缺失或零长无条件返回unproven。反例为前三E均合格、N-root或N-member没有security payload；源码会返回unproven/exit2，而合同将unproven用于必需empty缺证据，N对照不符应failed。此偏差不造成eligible，也不降低安全拒绝，但会误标采用/放弃证据。

最终294–295行按one区分failed与unproven，不解析占位；新说明同步。该项已静态关闭，无新增调用、输出或预算。作者自查把empty setup的acl_valid前门去除、只对两单ACE执行valid，保持原empty的init/set/free建立方式；该调整不把setup当实际ACL观察，不构成删安全门求绿。

## 解析与真实ACE证据

253–342行先核4KiB内完整长度、4字节边界、返回属性组及精确所需mask；只允许请求内字段，vol/dir/fork清零，file links只普通文件请求。固定字段顺序按mask布局读，所有访问经memcpy和Reader大小检查，没有未对齐struct强转。

实际DEVID/FILEID与同FD fstat核同，member另核创建FD记录的identity；type、uid/gid、权限位、普通文件links一致。ACCESSMASK只比较07777权限位，不取其type；目录仍用原stat nlink非零，未混用DIR_LINKCOUNT。安全门失败不继续getattrlist，缺security/零占位不能签absence。

signed attr offset在Int64相加，再核非负、buffer内、4字节对齐、固定区之后，变量区紧接固定区并恰至完整length；checked_add/mul/round避免溢出。header最小44B、magic、flags0、NOACL先判、count范围及H/H+A精确长度均有门，无借零初值补字段、扩容或fallback。E只接受明确NOACL/count0；N必须count1并进一步核sole ACE。

N的guid qualifier逐字比内部已取得owner UUID，entry_flags精确PERMIT、无继承/其它bits，rights精确目录LIST_DIRECTORY或文件READ_DATA；只有全核同才form3。SDK命名语义和固定Libc setter/perm/native export片段共同解释tag、qualifier、flags与rights映射，超出了纯数值巧合；没有声称installed系统库源码同源。四份实际SDKwhole bytes/hash及摘录源行内容已独立核对；三个Libc完整响应hash按来源记录引用，仅读必要保存片段，没有重新下载全文。

编译期ABI断言覆盖byte/int宽度、五属性组、signed32 offset/UInt32 length、GUID16及H44/A24/字段位置，但**断言预写不是编译通过**。头暴露、平台声明、C++17、符号/链接闭包与实际目标响应仍交T03另授核验；本审没有用手工解释冒充编译器或运行结果。

## 路径、预算和一次收尾

main先E-root/sub/member，保持root原anchor、子目录O_RDONLY和member O_EVTONLY；不另给E子项设置ACL。全部E合格后才一次mbr_uid_to_uuid并建立独立N；N-member先在创建FD设置单ACE再关闭，观察仍另用EVTONLY，N-root另设目录ACE。setup与观察单线程分阶段，没有插入自有metadata/namespace mutation；没有路径参数、产品owner/cap/child或动态API路线。

完整最大路径的人工控制流核算与调用点表相符：

- fstat为E创建1+E观察3+N创建1+N观察2=7；fgetattrlist至多5；geteuid一次、mbr_uid_to_uuid最多一次且在E合格后。
- mkdtemp/open/mkdirat各2；openat为两创建FD加E-sub/E-member/N-member，共5；共7个取得FD各close至多一次，unlinkat至多4、rmdir至多2。
- ACL setup四轮（E空root、N空root、N-member单ACE、N-root单ACE）：init/set/free各至多4；两单ACE各create/tag/qualifier/get/clear/add/set权限/get/clear/set flags，valid至多2。前门失败短路，不重试或重复释放。

应用资源最多五长期metadata FD、一个暂态创建FD、一个setup ACL副本、两个三对象fixture、一个4096B复用buffer；另340B五条Observation记账、97B行scratch。该清单与源码相符，只约束应用路径，不能签libc/kernel内部资源或wall硬界。

close_once在close前退役slot，失败保retained；cleanup继续处理其它已知FD及已创建自有名称。ACL entry/permset/flagset是借用，只有工作副本free一次；create_entry失败若异常改变ACL指针或成功输出所有权不明则retained，不猜free。所有同步早返回最终到main的两fixture cleanup；没有C++异常/abort/exit分支绕过已知资源收尾。unlink/rmdir失败也retained，不吞ENOENT或搜索残留。

异步取消/强制终止仍可能中断，代码没有证明自然EOF、后代drain或fixture清空；这些必须在未来真实控制窗口保留未知。只操作自身固定名称不是持续namespace许可或任意恶意同UID防护。

## 输出、决策与交接

Observation[5]在收尾后统一输出，避免stdout断开/SIGPIPE于输出阶段跳过已知资源收尾，不新增signal API；未知责任并未因此变成已释放。setvbuf失败不建fixture；snprintf/fwrite失败停止输出、返回非成功，retained优先。输出前无程序stdio写入，源码没有stderr写入；C运行时或外层工具诊断不属于此schema承诺。

静态最坏三行71/63/64B，每样本至多三行、五样本加最长28B disposition为1018B；line helper硬核96B/16行/1018B，buffer 97B，未输出原始UUID/UID/GID/路径/FD/payload或任意异常。有限api/form/布尔、Int32 errno和UInt32 bytes/count保持，NOACL哨兵只展示不参与乘加。

最终先cleanup，再核cases=5/fstats=7/attr_reads=5，全部充分且可检查收尾成功才eligible/exit0；E缺证据unproven/2、API/setup/畸形/错N对照failed/1、释放未知retained/3，stdout失败不能成功。即使未来eligible，也只表示目标profile值得后续适配，不等于原owner/root/acquire/撤销/关闭case执行或产品功能通过。

我的首次文本调用点regex（ed0fa8）把numeric_limits的min/max误纳入全局native清单，静态断言exit1；随后显式排除此C++模板限定名（bbb865）清单核对exit0。前一轮SDK哈希/源行检查已完成；没有运行C++或API。该提取器失误不改源码、不冒充测试失败或程序验证通过。

source-contract与handoff准确保持NOT_BUILT/NOT_RUN、单用途entrypoint、无产品链接及T03唯一构建责任；构建输入闭包/累计预算、产物pin与一次CLI仍待root分别另授。旧003/004失败、未知资源、目标双OS/完整N0/指定同版外审/CI/真人/远端及T01 HOLD和SQLite/heap/OS拒线不关闭。最终源码阶段无剩余阻断，报告冻结交出后停止改写。
