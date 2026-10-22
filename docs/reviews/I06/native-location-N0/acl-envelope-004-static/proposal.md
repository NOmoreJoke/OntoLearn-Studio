# 004 envelope失败后的静态结论与有限选项

**现有证据不足以批准最小成功修复，组件继续fail closed；不建议仅为分辨两个UUID presence而做第七构建。** 两位的任何诊断结果都不能补齐独立的完整性/absence合同。找到一个更强的公共接口候选fgetattrlist：返回字段mask、总长度和变长字段长度能证明某些响应已完整返回，但仍不能把缺失的security字段当“无ACL”。它是供root另审的有限替代设计，尚不证明当前宿主能完成完整正反验收，也不是当前源码或运行许可。

本次只新增过程文档及必要来源摘录，没有实现下面的选项、编译、调用API/探针或重跑004。基准0c20804537cca79578e0344870b4a3f24eb76998，产品仍1217e0f63a9c62b72e01046ef5fbc5c53434251a；Mac12579B/d944a4901b6d3f516f18ab436aed9ec56a78eb1bbd12d1949ebf6a6e171825ce，test37928B/2517eb970ef39f37dd99ca9945909331df937d4dd43ce53b74eb722bf47a7053。完整固定来源/行号/bytes/hash及九源保护见evidence-and-preservation.json。

## 现有关系：声明、条件推论、实际未知

| 关系                    | 已有依据                                                                                                                                       | 可以认定与不能认定                                                                                                                                                      |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| filesec公开属性和函数   | 当前SDK fcntl/stat声明有OWNER/GROUP/MODE、UUID/GRPUUID、ACL及query/get/fstatx                                                                  | 证明声明/类型存在；没有从这些声明取得独立的“响应完整”返回标志，也不证明本机支持的行为                                                                                   |
| UUID presence和扩展响应 | 固定公开Libc71bbe350ab79eef58113991d817ccc6165061a64的statx_np.c:191–214：完整kauth_filesec分支设置UUID/GRPUUID；短分支清除；两分支均可能清ACL | 这是所读实现的条件推论。完整结构也可NOACL；ACL absent不推出完整结构。不是官方跨版本语义保证，不是installed libSystem身份证明                                            |
| query的含义             | 同固定filesec.c的valid位和query；UUID setter复制值并置位                                                                                       | 位为非零才present，可能4/8/32等；查询成功与属性present是两件事。这个实现中设置一个全零UUID也会置位，不能把presence缺失解释为读到了“零UUID值”                            |
| ACL缺省                 | 同公开statx的NOACL/短响应及fresh未填反例                                                                                                       | 单独NULL、ENOENT、query valid0均不足以放行。私有RAW/ALLOCSIZE共用ACL valid位，也不形成独立完整性证据，不采用它们                                                        |
| 004到达点               | 固定stderr41B及test425–443、511–521                                                                                                            | 两UUID query成功，presence合取失败，至少一个为0；不知道哪项或底层原因。ACL presence尚未查询、owner创建和生产metadata未进入，不证明短envelope、平台/权限根因或生产返回值 |

生产metadata的UUID门和fixture的断言是两个不同决策点。前者缺见证时返回UNSUPPORTED并收尾，后者先于owner创建停止整个测试。004只实际触发后者；两者复用同一个保守假设不使其成为独立合同。当前没有理由只删除测试门让owner继续，或删除生产门换取绿色。

依据：[固定Libc statx](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/sys/statx_np.c#L191-L214)、[固定filesec](https://github.com/apple-oss-distributions/Libc/blob/71bbe350ab79eef58113991d817ccc6165061a64/gen/filesec.c#L304-L340)。两个旧Apple filesec/statx手册URL本次仍不可访问；没有将搜索不到文档写成“系统不存在合同”，也未采用第三方镜像解释。

## 为什么两布尔诊断不能解锁

可以仅在read_acl_fixture原断言前，对已有owner_uuid/group_uuid值各取是否非零，输出一次固定行；不增加或重排查询，保存并恢复errno，不输出成功遗留errno。但它的收益只有区分哪位缺失：

| 新诊断结果                | 可缩小的事实     | 对完整修复/验收路线的影响                                                            |
| ------------------------- | ---------------- | ------------------------------------------------------------------------------------ |
| 0/0                       | 两属性均缺省     | 仍没有完整响应或ACL absence证据，保持拒绝                                            |
| 0/1或1/0                  | 仅其中一属性缺省 | 仍是相同合同缺口，不能解释原因或删除另一门                                           |
| 1/1（若另一运行自然出现） | 本次旧合取可继续 | 仍不能将公开实现绑定installed合同；不能倒填004，也不能承诺后续正反用例或完整目标通过 |

所以不把“加布尔→再构建/跑”列为默认后继。若root有独立审计需求才另授该选项：唯一writer为test的read_acl_fixture、原断言之前，新增条件fprintf一次；格式为`N0 ACL witness stage=uuid-presence owner_present=%u group_present=%u\n`，两个实参仅0u/1u。新行固定67B（含LF），加原41B异常行共108B，单行低于96B、原流预算不变；早期query失败不打印此行。errno立即局部保存并在stdio后恢复，原require/异常/清理/owner顺序不变；不把fprintf失败当成功或重试。无新头/链接依赖，stdio内部成本仍未知且非零。只是诊断，不解决本任务的完整性目标。

## 公共同FD候选：fgetattrlist

只静态核一个有限候选，没有继续枚举其它实体接口或做环境实验。Apple官方XNU手册和对应SDK给出：fgetattrlist针对传入FD；ATTR_CMN_RETURNED_ATTRS报告实际字段；FSOPT_REPORT_FULLSIZE让首长度反映所需大小；PACK_INVAL可保留占位，但mask未置位时占位无效；EXTENDED_SECURITY是带相对offset/length的kauth_filesec数据。默认缓冲可能静默截断，不能把返回0当完整。这里的返回结构提供比UUID presence更直接的响应证据，不需要UUID值作为授权。

官方手册固定为XNU f6217f891ac0bb64f3d375211650a4c1ff8ca1ea（本次解析main后锁定）；见[手册](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/man/man2/getattrlist.2#L245-L402)。当前SDK声明支持这些名字，不等于目标OS/本机已支持。旧Apple归档getattrlist页缺少这些新增字段，本方案不用旧页背书新增mask合同。

已读sys/attr.h位于`__APPLE_API_UNSTABLE`条件块；公开手册和SDK结构声明不代表跨版本稳定的序列化ABI。原始kauth payload解析必须按批准目标SDK及合同独立审定，不能只凭当前header尺寸认定各目标均安全；这也是当前不能直接实施的限制。

重要限制来自同固定[security打包分支](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/vfs/vfs_attrlist.c#L2051-L2074)：只有va_acl受支持且非NULL时才打包security并置actual位；否则可只输出无效占位或省略。由此不能区分“无ACL导致没有payload”和“对象/文件系统没返回该属性”。PACK_INVAL也不能把placeholder提升成有效absence；卷级功能支持并不能自动证明本对象响应完整，本提案不增加卷探针。

SDK kauth.h定义NOACL与空ACL的区别及结构布局；完整有效返回的明确NOACL header可以成为absence的候选证据，count0则是present-empty候选；但不能保证目标文件系统会返回这种有效header。公开kernel还会把owner/group设为null GUID，进一步说明UUID值与ACL字段返回完整性应分别审视。所读公开kernel不是installed身份，不以它推定004发生过此分支。

| 候选响应（尚未实测）                                                                         | 可采用的结论/后继                                                                   | 仍不能签收的内容                                       |
| -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 所需mask齐、无截断、完整合法security header，明确NOACL或count0；原标量/identity及ACL检查一致 | 有独立的正向响应证据，可供root另审具体替代实现，后续才可能验证对应absence/empty分支 | 本机是否实际给出该表征、同版正反、异常分支及完整父目标 |
| security位缺失，即便调用返回0、length合理或占位为0                                           | UNSUPPORTED；不能当absence。不建议重复扩大buffer或换环境求绿                        | 常见无ACL输入可能仍无法完成P1，完整目标依旧未解锁      |
| header有效且任意ACE                                                                          | DENIED；setup有效后才可能作为安全负例                                               | 不能只凭拒绝证明正例可用                               |
| 缺标量/identity位、长度越界、畸形引用、矛盾或跨快照不一致                                    | 非成功、停止；不是ACL空                                                             | 不以raw字节或默认值伪造确定性                          |

这说明存在可审核的**条件路线**，但没有证明所有合法“无ACL”对象都有可证明的响应。现在既不能认定路线完全不存在，也不能把它写成已足够落地的修复。未决证据是：目标接口对无ACL对象是否提供有效明确NOACL/空header，或有独立、正式且适用于本对象的absence语义；以及增加第二次metadata响应是否满足原组件的快照语义。未知必须原样保留。

## 若root选择继续审此候选：最小边界，不是实施许可

唯一生产writer仍为platform_macos.cc的metadata及私有有限解析/cleanup；唯一配套测试writer为location_core_test.cc的Darwin witness/定点case。不是改ABI/core/Windows/Node/TS/控制算法，不能只改fixture绕开生产门。须另给精确两writer源码窗口；目前两文件均未动。

- 保留同held FD、fresh filesec、一次fstatx成功、OWNER/GROUP/MODE getter成功且与stat一致、原query返回码、安全检查及独立ACL副本ownership/错误边界。新证据若获批准替代UUID presence合取，必须先有完整security payload，不能无条件删门。原任何ACE拒绝、最终才发布metadata保持。
- 候选最多额外一次同FD fgetattrlist，应用侧固定4096B零初值buffer、固定attrlist，禁止动态扩容/重试。请求returned-mask、device/file identity、type、owner/group、permission及extended security；普通文件可加FILE_LINKCOUNT并核同原nlink。目录DIR_LINKCOUNT定义不等于stat nlink，不能直接比较替换；原目录nlink安全门仍基于原stat。无需路径、UUID、卷或额外FD请求。
- options候选为REPORT_FULLSIZE及PACK_INVAL。先核调用返回码及即时errno，再核最小前缀、完整长度不超4096、所需actual位；缺位时不信占位。按文档4字节packing，以memcpy取字段，不能用自然对齐struct强转。严格检查相对有符号offset、加法溢出、变量区起点/终点、attr_length及magic/header最小长度，禁止越界或把零长度作空ACL。
- 完整header的NOACL/count0才有候选成功可能；与原filesec ACL查询表征矛盾时拒绝。present仍必须通过原owned ACL copy/valid/明确empty规则，不能由原始count替代有效性检查。正count直接拒绝，不解析UUID或遍历所有ACE。原free一次、失败/未知ownership RETAINED优先、filesec_free void不造结果保持。
- 拟错误边界：实际ENOMEM→BUDGET，EACCES/EPERM→DENIED，其余API失败→UNSUPPORTED；超过固定响应预算→BUDGET；缺字段、畸形、矛盾或不能确认完整→UNSUPPORTED；任意ACE/原安全门不满足→DENIED；释放/未知ownership→RETAINED优先。这些是待批准增量，不在当前更改行为。
- 同一FD证明对象绑定，不证明两调用原子一致或期间无变更；数值相等也不是lease。若原验收要求单一原子metadata/ACL时点，该候选不足，不得假称保持全部语义。4096B只约束应用buffer，原statx及新接口内部heap/系统调用/wall硬界仍未知。
- 新直接头预计sys/attr.h、sys/kauth.h；unistd.h已有但需核fgetattrlist声明/符号。SDK标记和ABI、间接头/链接/符号、源pin/锁及增量预算全部交T03唯一构建owner另审，当前不改锁或共享环境，不预认预算通过或第七构建已获批。

必要反例：返回0但所需位缺失；PACK_INVAL零占位；总长度大于buffer；负offset/越界/溢出；截断header；magic/长度不符；NOACL与空ACL混同；任意ACE；identity/owner/mode矛盾；目录link语义混同；同FD跨响应并非原子；分配/释放失败及未知ownership。不能用成功用例关闭这些任意故障或内部资源未知。

先由root选择是否值得推进该接口的完整设计；若不能取得上述独立absence与快照证据，则维持组件fail closed，不以目标缩减或伪成功结案。若获源码窗，固定新源后才必要check/独审；T03另授新输入编译，新pair再另授一次CLI。当前不预建新record/运行目录、不复用004窗口，不建议为两个布尔值单独启动这条链。

## 本轮交接

本轮静态字符串/真值表核算仅证明可选诊断固定67B、非1位值按非零处理，不是C++编译或运行测试。源码/九源、旧失败/准备/控制算法和AGENTS保护指纹保持；无变化不跑npm/旧源复测。独立窄审与有限manifest随本过程固定，root收件后再决定后继；003/004失败及drain/残留未知、目标双OS/EXCL/父N0、指定同版双外审/CI/真人/远端门、T01 wholeH/SQLite损坏保护HOLD和已拒分析线均未关闭。
