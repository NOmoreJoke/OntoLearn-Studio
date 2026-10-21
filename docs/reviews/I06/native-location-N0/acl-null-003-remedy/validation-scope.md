# 必要真实正反验收范围（未执行）

当前只读方案窗口没有源码、测试、ACL修改、API/FS探针、构建或CLI许可。本表是下一窗口应批准的具体最小范围；“应通过”均为验收条件，不是已测结果。003失败与001/002未知、旧fixture/后代/drain保持，不能复用旧pair或旧运行证明新方案。

## 精确writer申请

1. 生产：仅platform_macos.cc的platform_metadata及必要私有cleanup，执行proposal.md的同FD/fstatx、必需属性一致、完整envelope存在性见证、ACL presence/entry判定和错误映射。无ABI/core/Windows/Node/TS/driver或限额改动，不用FILESEC_ACL_RAW/ALLOCSIZE，不替换目录/系统权限。
2. 测试：仅location_core_test.cc的Darwin ACL fixture小helper及定点用例，保Windows28静态断言和既有case/断言。新正反fixture均新建、仅操作自身已持有anchor FD，不碰旧运行路径；新增setup API/同FD证据读取次数和错误清理必须随源码窗口一并批准。

负例可用acl_init(1)→acl_create_entry→ACL_EXTENDED_ALLOW→acl_set_qualifier(当前owner UUID)→最小单一grant permission→acl_valid→acl_set_fd_np同anchor建立**恰一条有效ACE**。当前owner UUID拟用SDK声明的mbr_uid_to_uuid(geteuid(), uuid)，不查联系人、不改用户/组；返回非0或任何ACL setup失败均“无效测试”，不能算DENIED通过。所有ACL对象free一次且检查结果；原fixture已有同FD empty-ACL设置能力，无需chmod/setfacl工具或路径查询。本窗未执行这些API。

单grant ACE避免用DENY破坏fixture自身清理；即便ACE只给当前owner增加权限、原mode不变，生产的“任何ACE拒绝”政策仍应DENIED。不以effective permission判断来放宽政策。

## 最小真实用例

| 用例                      | 独占fixture/setup证据                                                                                                                            | 必须观测的行为                                                                                                                                                                                                                                                                                                   |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P1：明确无扩展ACL         | 原empty ACL setup成功；在许可测试内，对同FD最多一次独立fstatx及公开属性读取记录ready、extended-envelope、ACL-present，证明实际表征而非只看旧NULL | 若属性ready/identity一致且UUID/GRPUUID present、ACL absent，新owner创建OK，root公开metadata只比较kind、identity（按既有ABI编码）、link_count及acl_checked/held_object_only；uid/gid/mode及属性一致性只来自同FD fixture witness和生产内部安全门，不要求ABI新增字段/seam；最终显式owner close及fixture cleanup成功 |
| P2：有效且空的present ACL | 仅当目标FS自然保留这个表征时记录presence与entry为空；不得反复改环境强行制造                                                                      | present分支原valid/empty规则保持，清理完成后允许；若FS统一规范化为absent，记录此分支未实测，不伪造第二个正例                                                                                                                                                                                                     |
| N1：一条有效ALLOW ACE     | 上述同FD单ACE设置/valid/free均成功，setup读取确认ACL present且确有首entry                                                                        | owner-create非成功，预期DENIED；非零失败owner先按原规则close一次，再断言结果；不能借成功helper直接abort漏掉失败owner；原mode不变并仍拒绝                                                                                                                                                                         |
| N2：原安全门              | 复用既有type/UID/mode/link/no-follow/hardlink/symlink/identity更替测试及断言，不改期望                                                           | 原DENIED/STALE等保持，无字符串路径fallback；既有metadata/child/partial/concurrency/budget组件case全部按真实结果记录                                                                                                                                                                                              |
| N3：失败输入              | 仅新fixture自己独占的无效/已关闭FD，或已有明确许可的查询失败场景；不得关闭/复用未知旧FD                                                          | 明确非成功，无old-ENOENT捷径。若错误发生在duplicate前门，必须注明未覆盖新fstatx内部错误，不能把它当property层失败测试                                                                                                                                                                                            |

P1中独立fixture证据读取是**拟新增、须批准的定点测试查询**，不在本轮执行，也不加到生产成功路径；它用于区分representation。setup/被测函数之间不是持续ACL授权；持有同FD绑定对象，不承诺时序外ACL不变。任何ready/envelope见证不满足则该fixture必须UNSUPPORTED，不能删门或改期望追求通过。

每个新fixture只做一次所需setup/证据读取/被测创建与原规则清理，不扫描/tmp、不改未知旧fixture、不新增挂载卷或权限设置。必要证明行只输出固定case/布尔/状态，沿已批准行长和双流上限，不输出UUID、FD、路径或环境；确切测试文案由源码窗口审定。

## 不能冒充真实覆盖的错误分支

query/get失败、缺省envelope、allocator failure、内部realloc扩容/错误以及acl_free真实失败，不保证能在现有合法fixture自然制造。不能传伪造指针/双重free/全局low-memory设置来冒“释放失败实测”。本方案用源码反例和独审要求fail closed；若root要求这些分支的确定性运行覆盖，应另给非常窄的测试seam/故障注入窗口，当前不申请通用mock/能力框架，也不将未实测分支写成已通过。

尤其“fstatx==0且fresh属性缺省”“query valid非1”“未知短envelope”“get错误但残留输出”等需要结构审查或另授定点故障输入；P1/N1成功不能关闭这些任意故障或内部资源上界。filesec_free为void，不制造返回值测试；acl_free失败必须静态确认RETAINED优先且无第二次free，未真实触发就标未实测。

## 验证与交接顺序

- 新产品落地后仅一次必要完整npm check和12归档源核验，保存真实双流；这仍不编译C++，native addon可能skip。
- 独立source delta审查确证安全门、错误映射、所持资源与清理路径；冻结新九源/仅Mac与Darwin test差异，保护旧001/002/003及五轮原件。
- root收件源码后给T03必要新输入采用/编译窗口；实际编译/链接与目标SDK声明通过后再核新pair。不得用目前第五pair验证未来修复。
- root另授新pair的精确一次CLI及本表允许的fixture ACL setup/read范围，沿原过程/限额/stop边界。失败保原件停止，不能自动重试、改源码或扩大清理。

即使P1/N1及既有组件通过，也只关闭相应单宿主行为；不是硬heap/OS调用数/wall上界、native drain、EXCL全路径、Mac15/Win11、完整N0/父功能、同版指定外审、CI/真人/远端门的整体通过。公开source不替本机libSystem身份，本轮不新增一般平台trace或SQLite/heap分析门。
