# I06 生产位置 native 供方：精确静态方案

2026-10-21。建议选 **C++17 私有用途 broker + Node-API 控制面 + 受控 CPython `_sqlite3` 同库 capability VFS**。本方案可冻结供方/消费路径和第一实施切片；尚无生产 LocationLease，不能批准首次 SQLite/header/catalog/backup 内容 IO。真正缺口是同一物理对象从准入到 SQLite 的连续消费、跨进程实际寿命、安装 fresh/历史来源及目标文件系统耐久/持续 namespace 约束，不是再增加一份 inventory 类型。

本轮只有静态来源调查、文档与独立审查。无下载、安装、编译、产品/测试/native/子进程实验、GUI、Keychain、模型、付费、push/PR/merge、Goal 变更。下面所有代码路径、接口和实验均为**待根登记的申请**，不是本轮实现权或通过记录。T01 仍唯一 main/profile/bootstrap/engine/Store/worker/canonical 消费 owner；T03 仍唯一构建/锁/入口/打包 owner。I06 仅是私有供方设计协调者。

## 1. 固定输入、当前事实与验收边界

| 输入                     | 完整 ref / 身份                                                                                                                                                                                   | 使用范围                                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 本轮准备指令             | 仓库外 `iteration-control/2026-10-21-weekly-release/I06-native-location-supplier-plan-preparation.md`，5447B，SHA256 `15d40bf0046f68f6a1d757bc0e05ea6f38c16be16dc0e20739827c2e7a19a18f`           | 全文，只授指定新 docs                                                                                |
| 根跨模块审计             | 同目录 `controller-next-integration-readiness-audit.md`，17048B，SHA256 `6f86d84c` 前缀；完整 SHA 见 inputs.json                                                                                  | 全文；native 尚无实施 writer，不阻塞独立 T01/C2/临时机制                                             |
| B 固定方案               | `ffb55e0e694bde00b64fed400260e47392aa3554:docs/iterations/I06/project-inventory-real-owner-B-plan.md`，44238B，SHA256 `b71667de836ee2bcf8f62107f170e808200a3b4f77c264ed06d7c21e9ceed605`          | §5 控制来源，§8 消费供方，§9 实验与门                                                                |
| T01 创建/resolution 合同 | `379916267e5c36eebedb44d35a6636b9915ccd70:docs/iterations/T01/project-create-and-resolution-contract.md`，39602B，SHA256 `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3`       | 原归因、当前许可、真实 Store lifetime 三者分离                                                       |
| T01 实现                 | `423b7e4c799f188cf2ce6e8e7121893ce85624cd`                                                                                                                                                        | 12 条业务源码及 9 条构建/锁/入口固定 blob；逐路径 bytes/SHA 见 inputs.json、t01-source-static.md     |
| 位置/cohort 既有 offer   | `1f3b053d8a69d1f7ddb1e29c143f648d910fe689:docs/iterations/I06/project-location-capability-and-cohort-offer.md`，46365B，SHA256 `561ec272c07f0c0f026c9aa17b717b99d3e110e31cb4ee45f0663254e9517443` | 设计输入，非 e2c 已实现 native；该 doc 不在 e2c 产品 ref 内                                          |
| B-M 产品/证据            | `fa8f977d888712cb7127cb0095fa56dafabb37ed`，相对 5f 共64件                                                                                                                                        | 已根收口的受控临时 metadata 子集；64项原字节冻结，始终 node-observed-unfenced/production unsupported |
| B-M 根收口回执           | `6240748d83d2251664b3fe1e9808f5f67adeec41:docs/reviews/I06/real-private-metadata/root-closure.md`，3077B，SHA256 `ab10ea451b362cb9f655aacd52e692ad8c23dd3b3086f45239267af5e119e443`               | 原字节另存，仅 docs 后继，不改 fa8                                                                   |

工作树 `.worktrees/I06-real-private-metadata`，branch `feature/I06-real-private-metadata`。AGENTS 与共同指令只读身份见 inputs.json；AGENTS 的既有 dirty 保留。原 A6a38、ffb、e2c/961 和 B-M64 均不改。本轮来源调查报告是新证据，不倒写旧 evidence manifest/ZIP。

**直接源码事实：**423b main/index.ts:127 向 Supervisor 给 `userData/engine.sqlite` 路径；engine.ts:162 通过环境给 DB_PATH，:416–427 给备份路径并只建三个 stdio pipe；coordinator.py:837–839 先 mkdir 再构造 JobStore；storage.py:90 按路径 connect，之前已有 writer-lock open。format3.py:164–185 的备份先 xb、再 connect、再 rb/fsync、再 read_bytes，每次都可能重开不同对象；storage.py:1657 是另一个备份入口。固定源码没有已注册 capability VFS、显式 WAL 设置或 DB 原子 rename 发布，不能报告现有 WAL/SHM 或发布已通过。详细行号/哈希见 t01-source-static.md。

## 2. 最薄边界：谁持有事实，谁能做操作

能力不是 JSON、路径、UUID、migration_id、hash、PID、Promise 品牌或 renderer 可复制的 nonce。I06 native registry 持有实际 OS 对象与有限状态；main 只能经可信装配取得 opaque 引用，Python 只能经指定 child 通道接收该连接用途。真实 OS 调用只在供方内的命名操作执行，不提供 `run(callback)`、任意 fd/HANDLE 数值导出或通用 path opener。

每条原生记录绑定：broker/process/profile incarnation、root/全部持有 parent 对象、member 实际身份、purpose、connection/child owner、grant epoch、budget reservation、实际 IO/锁/map/close 集合。身份在本次持有期内使用：macOS 无损 dev+ino，Windows 完整 volume serial+128-bit fileId；跨重启只作历史拒绝线索，重新取得 OS 来源，不能复用旧 inode 为永久认证。

| 内部能力语义（尚非批准 API）   | 可消费的精确操作                                                                                                  | 明确拒绝                                                                              |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| metadata root/parent           | 已受信锚点开始的逐组件 metadata acquire/enumerate，保有目录对象；读取类型/权限/ACL/links/identity                 | 文件正文、create/truncate、renderer 根、未闭合 ancestry/alias、未知 protected history |
| open-existing                  | 原生 gate 核准已有普通文件与派生 sidecar 策略，取得并核**实际返回 handle**后才交 VFS 首 read                      | O_CREAT、mkdir、迁移或把不存在当 fresh；无授权时连 header/catalog 都不读              |
| exclusive candidate/create     | 核准 parent 内有限预登记单组件名 exclusive-create；绑定新真实 identity；SQLite 初始化按独立用途                   | 覆盖已有、复用别名、临时名可猜即有权、先写后补 intent                                 |
| migrate source + backup target | 人类已确认的既有 source 连接；独立目标候选，SQLite backup API、完整性/内容 hash/同对象 sync                       | 自动迁移、源目标同物理对象、exists→connect、以备份授权 source 任意 write              |
| publish                        | 候选真实关闭/必要 checkpoint+sync、源/目的 parent 及 candidate identity、同卷原生 no-replace 发布                 | 普通 rename 覆盖、copy-delete 跨卷降级、源名被换仍发布、未知目录耐久当成功            |
| writer + cleanup/revoke        | DB实际 identity 的应用单 writer、SQLite原锁/SHM、已登记 IO；停新接纳后仅完成已接纳事务或必需 rollback/close/unmap | 超时清槽、unlink 锁破争用、取消后恢复旧 grant、禁止 xClose 导致无法回收               |
| control bootstrap/self-append  | §7 固定 metadata 控制协议自身动作                                                                                 | 第二项目/Job/main意图账本、任意目录写、模型内容/密钥/业务正文                         |

所有等待前 reserve，实际原语启动前在 native gate 复核 epoch/purpose；已接纳操作即使撤销也保原实例资源和结果。返回到 main/child 前再次核原记录；晚返回不得发布到新 profile/新 child。候选准备预算与长寿命 lease 分开：沿既有 offer 的 transition1、active/candidate各1、picker1、acquire2、roots32、entries32768、roles16、depth128、UTF8路径16384B；准备候选 TTL30s、逻辑等待5s不杀已有 lease/未返回 syscall。任一超额拒新接纳、保 unknown，不丢旧记录。本方案不承诺每 syscall 五秒结束。

保护源必须由未来实际 native inventory + B-R 历史恢复提供，不把 B-M Node 值签成 trusted。目录名/成员/links 完整有限闭合；普通新 DB 提案 nlink=1，已知私有 inode/别名/根祖先一律拒。旧 private 根及 pending/孤儿始终 deny；未知 hardlink 范围不能靠全盘扫描补齐。同址新 inode 必须新 incarnation，旧记录保留；冻结 A 的同位置双历史限制仍 unknown，另批最小 A 扩展，不本轮改 A。

## 3. 两目标 OS 的操作链与尚不能交付的保证

官方原语及直接链接逐项见 platform-static.md §3/4。下表是本应用设计推导，非 OS 对整个合同的背书；两 OS 均未执行。

| 动作                 | macOS15 arm64 候选                                                                                                                    | Windows11 x64 候选                                                                                                       | 必须失败的分支                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| root→parent→member   | held dirFD + 单组件 openat(O_DIRECTORY/O_NOFOLLOW/O_CLOEXEC)，fstat/ACL；目标 SDK/runtime 证实后再用 O_NOFOLLOW_ANY/O_RESOLVE_BENEATH | NtCreateFile RootDirectory=held parent，单组件名；FILE_DIRECTORY_FILE/FILE_OPEN_REPARSE_POINT，取得后核 reparse/type/ACL | symlink/reparse、分隔/`.`/`..`/ADS、未知 mount/云占位/远端、权限未知、祖先不闭合；不 path reopen |
| metadata→内容 handle | 只开不读，不 truncate/create；实际返回 FD 先核身份、protected alias、type/links/ACL，然后同 FD 交 VFS                                 | 对实际 HANDLE 查 FileIdInfo/FileStandardInfo/GetSecurityInfo 后才交 VFS                                                  | pathname 双 stat 一致不能替代；未知就是零内容 IO                                                 |
| 独占建立             | held parent openat(O_CREAT                                                                                                            | O_EXCL                                                                                                                   | O_NOFOLLOW)，取得后保FD                                                                          | RootDirectory+FILE_CREATE，绑定实际 HANDLE | 冲突、links/identity/ACL漂移，不删目标重试 |
| 无覆盖发布           | 同卷 renameatx_np(RENAME_EXCL，可验证后加 RENAME_NOFOLLOW_ANY)；volume需支持                                                          | 实际候选 HANDLE 上 FileRenameInfo，held目标RootDirectory、ReplaceIfExists=false                                          | 跨卷、不支持、源名替换、share冲突/身份错配保 retained                                            |
| 数据/目录耐久        | 正确 held文件 fsync，所需时 F_FULLFSYNC；父目录项同步另证                                                                             | 文件 FlushFileBuffers；非admin父目录项持久发布契约未找到可直接承诺的完整来源                                             | 文件flush/rename/close成功不签全链durable；未知则 B-R 不放目标 mutation                          |
| 退出/取消            | 同步 syscall真实返回/自有child waitpid、所有FD/map/锁收口                                                                             | OVERLAPPED实际completion/CancelIoEx后等结果、实际hProcess signaled、全部自有mapping/HANDLE                               | Promise超时、kill返回、PID缺席不替终态                                                           |

**物理对象绑定与持续 namespace 不变分开验收。**held parent 能防止“核 A 后按字符串读 B”的一类丢绑定，不能阻止外界把整个已持有目录移出原位置。macOS逐组件 openat、操作前后 fstat、原生单线程 gate 都不原子锁住所有祖先；renameatx_np 的 source 参数仍是名字，若源名在核验与 syscall 间被同 UID 换成其他对象，事后发现已不能撤回发布。Windows 不共享 DELETE 的 ancestry handle 可以限制相容 delete/rename，但先存 DELETE handle、ACL并发变更、sidecar自身需删除与分享模式冲突仍要逐项处理。

因此本方案**没有**把“用 C++ 做双检”改叫安全。严格要求在任意外部同 UID namespace/ACL/hardlink 并发变动下仍原子维持路径关系时，现静态来源不提供完整保证；相关 open/publish 生产用途保持 unsupported。第一切片只能取得对象级/受控临时 fixture 证据；根需收到明确 OS/权限围栏可行性结果，或正式重开保证及威胁边界，不能由 I06 自行排除该竞争者。文件被打开后再新增外部 hardlink、inode 跨删重用亦不靠一次 nlink 检查排除。精确缺口保留，不把此项模糊写“平台后续验证”。

APFS/NTFS 是首批**实验支持提案**，不是批准产品限制。大小写/Unicode/短名冲突、可挂载/云/SMB等未知语义先拒绝；若产品要求其他卷，另供原语/证据，不能静默变成 POSIX-only。当前 macOS27 unsigned 目录包不充 macOS15/Win11目标证据。

## 4. main→实际 child→SQLite 的连续传递

1. T01 在首次 mkdir/lock/connect 之前请求用途；没有完整来源就不启动该次生产位置 IO。I06 先 reserve main/待启动 child/连接与通道，原生 adapter 创建**指定实际 child**，T01 Supervisor 接收并永久追踪这个 owner。现三个 stdio pipe 不是现成能力通道，不以额外 nonce 文本替实际 spawn 绑定。
2. macOS 原生受控 spawn 给 child 专用 AF_UNIX 通道 endpoint；后续仅在此通道 SCM_RIGHTS 传已登记对象。Windows 用实际 hProcess + DuplicateHandle 或 STARTUPINFOEX 的显式 HANDLE_LIST；Node 公开 spawn 不暴露通用任意 HANDLE 继承/hProcess，必须 T01 接受窄 native child-transport adapter，不访问 `_handle`/复用 PID。官方机制边界见 [Node24 child_process](https://nodejs.org/download/release/v24.0.0/docs/api/child_process.html#optionsstdio) 及 platform-static.md §5。
3. 接收 native extension 核 endpoint/本次child/epoch/用途/实际handle identity和rights；无截断 ancillary/额外handles/旧代次。只向可信 native peer 交所需 parent/member 权，不向 Python业务/renderer返回通用fd。MAC channel失联即停新接纳；Windows handle的目标整数仅在指定进程有效，文本不能生成授权。extension/OS registry处理真实对象，业务 JSON 只携已核短引用。
4. 每连接 VFS open 与 sidecar 操作通过 broker 的有限 pre-admission 协议，broker 在 dispatch 前登记，child peer在受控原生 gate 内消费并报告实际completion；撤销先关接纳，已接纳IO继续属于原槽。不存在“通道发过 revoke 即复制FD消失”。跨进程状态/通道/并发协议须第一条实际child切片实证，缺ack保unknown，不能靠JS锁或一份共享bool完成。
5. 正常 page IO在child本地已核文件对象上执行；不用每page把业务正文送main broker。必须的SHM映射在child地址空间建立，只传已登记SHM fd/mapping HANDLE，不能传main裸指针。映射不可瞬时遥控撤销；xShmLock/Map/Unmap和实际child都纳入终态。DB可选mmap先关闭，SHM不能因此消失。

跨进程协议只传必要有限 metadata/身份与ack，不发业务正文、keys或模型请求。Python worker 在423b不持DB；不下发LocationLease给worker，未来若新增其DB消费须新合同。待spawn/初始化失败/父先死/child晚收据均保原owner，不能漏入仅当前session列表。

## 5. SQLite/CPython：选定路线、精确拦截面与终态

### 5.1 路线比较及选择

| 路线                                                                 | 结论与代价                                                                                                                                        |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Node先stat/单独addon注册VFS，随后原stdlib path connect               | 拒绝：失去物理对象，另一SQLite实例registry不影响Python；没有附属IO围栏                                                                            |
| APSW或另做全套DB-API连接类                                           | 可作为另案；需T01冻结Row/cursor/异常/事务/backup/authorizer/迭代等全消费兼容面，增加依赖与维护范围，当前不是最薄                                  |
| 私有扩展探测/修改 `_sqlite3.Connection` 内存                         | 拒绝：CPython私有布局/对象寿命不构成稳定接口，不能用ctypes/dlsym猜地址补证                                                                        |
| **T03控制同一SQLite共享image，重建 `_sqlite3` + I06私有VFS注册扩展** | **优先选择**：保T01既有stdlib DB-API语义，用显式命名VFS与内部opaque URI；T03必须实际重建、打包并证明同一loaded image，不复用未知系统/uv库假定成功 |

[CPython v3.12.12 connection.c](https://github.com/python/cpython/blob/v3.12.12/Modules/_sqlite/connection.c) 实际传 `sqlite3_open_v2(..., URI可选, NULL)`，关闭走 `sqlite3_close_v2`。因而T01窄adapter可构造内部opaque URI指定受控VFS/模式，不把cap映射为真实path；URI来自供方，不接受renderer自造vfs/mode。`mode=rw`的已有库不得create，候选只消费已独占对象；即使SQLite给CREATE flags，VFS也按用途拒绝未批准创建。[SQLite VFS选择](https://sqlite.org/vfs.html) 是机制依据，不是同库证明。

在Python启动**任何DB IO之前**加载受控注册扩展；固定 `_sqlite3` 与注册扩展动态依赖同一个带私有install-name/DLL名称的SQLite image，供方显式注册，T01连接指定唯一cap VFS。Node addon不再链接另一SQLite执行SQL；renderer无加载入口。不能依赖Windows DLL搜索顺序/全局PATH或macOS系统libsqlite。T03产物记录实际依赖图、加载image路径/hash、ABI/版本/源码ID/编译选项；后续隔离实验比较注册/查询实际函数实例并证明真实VFS trace覆盖Store，而非只比相同版本字符串。没有该闭包，保持生产拒绝。

推荐**首个源码可行性候选** SQLite3.51.3，官方source ID `2026-03-13 10:38:09 737ae4a34738ffa0c3ff7f9bb18df914dd1cad163f28fd6b6e114a344fe6d618`、sqlite3.c官方SHA3-256 `32d5424f97e0a7fc5ed2f6335afbb58be4e0298bd7117a34e39d345ff13d859e`，已含WAL-reset修复；不是声称它为最新或最终生产安全版本。T03必须冻结实际源码包SHA256、完整补丁/编译选项并评估更新，版本改变独立重验。[官方发布记录](https://sqlite.org/releaselog/3_51_3.html)。当前Python声明3.12系列，B-M环境记录3.12.12只供静态兼容候选；不证明其内嵌SQLite版本或允许运行库不经维护更新。

### 5.2 真正的VFS实现面

命名VFS `i06-cap-v1` 只是内部提案，不是filename能力。内部opaque DB名及允许后缀必须映射到connection/purpose登记；未知/任意绝对名不传stock xOpen。VFS同build C层保持SQLite原锁/SHM语义，使用held parent/member adapter替换所有相关OS路径调用。**不是**包住stock xOpen后继续按路径开，也不是 `/dev/fd/N` URI。os_unix/os_win精确复用补丁仍须T03取回固定源码后逐实际syscall审，当前网络读取未得完整两文件，不虚称已审完整后端；无法安全收窄补丁则返回不可交付，不DIY一套未验证锁。

| SQLite/应用动作                      | 接受的用途与必须截获的面                                                                                                                                                                              |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 主DB open/read/header/catalog/schema | xFullPathname只产内部名；xOpen绑定已有核准对象，首xRead前完成实际身份/用途准入；xRead/Write/Truncate/FileSize均只触该对象                                                                             |
| rollback journal/WAL                 | xOpen依MAIN_JOURNAL/WAL flags与当前DB父对象派生；既有sidecar需真实身份核验，新sidecar独占建立；xAccess/xDelete须held-parent同用途，未知已有对象不读不删                                               |
| SHM                                  | os后端内部SHM open也须截获（不能仅看xOpen），xShmMap/Lock/Barrier/Unmap覆盖实际对象、映射、锁和所有连接引用；未知或改名保retained                                                                     |
| SQLite pager锁/应用writer锁          | xLock/xUnlock/xCheckReservedLock保原生协议；应用`.writer-lock`独立窄用途，现flock/msvcrt path open改为native持有，不unlink；按DB真实identity统筹别名                                                  |
| 候选/备份/hash/sync/publish          | source/target都是同build cap连接；backup API真实finish，target连接关闭/sidecar收口后对held目标hash/sync，不rb/read_bytes重开；publish见§3限制                                                         |
| temp/subjournal/super-journal        | 初始配置提案temp_store=MEMORY、禁任意ATTACH/VACUUM INTO/extension；仍枚举本build实际请求，未知NULL/temp或后缀返回明确错误，不能默认磁盘fallback。合法必需temp须另列精确用途                           |
| mmap/file-control/扩展               | 初始DB mmap_size=0、xFetch不映射而由xRead承担，SHM单列；file-control只透传确认无新path/无绕权的有限opcode；禁xSetSystemCall换入任意opener，xDlOpen失败；URI的vfs/immutable/nolock覆盖不能由caller输入 |
| sync/close失败与failed-open          | xSync实际错误有限化；xOpen部分成功后xClose仍追踪；xClose/xShmUnmap/OSclose全部真结束才终结对象，无错误吞掉                                                                                            |

该表按 [SQLite VFS object](https://sqlite.org/c3ref/vfs.html)、[io_methods](https://sqlite.org/c3ref/io_methods.html) 定义覆盖面设计；不是当前423b已请求过每个角色。不能偷偷改现有库journal_mode或用locking_mode=EXCLUSIVE/heap SHM掩盖不支持WAL；未支持模式明确拒绝并保原库。T01需冻结其真实SQL/backup面，受控trace在两目标OS证明所有实际open，包括内部SHM/临时产物。不能仅Node mock计数“xOpen调用过”。

### 5.3 单writer、撤销、crash与实际关闭

应用单writer不等于SQLite允许一个SQL writer瞬时锁；本合同要求按真实DB identity、全部aliases和长期Store owner仲裁，保现有legacy/business锁兼容，不能两个别名各一锁。macOS fcntl进程级record锁有“同inode任意FD关闭影响锁”的问题；metadata额外FD、多个connection、backup别名不能破他者锁。Windows LockFileEx锁也不是复制HANDLE即透明转给child；SHM映射锁责任不同。选择同版OS锁算法及真实多进程反例，不用JS map/自定义lock字节即宣称兼容。

撤销顺序：同步封新操作与新spawn→原用途已接纳事务的commit/rollback按T01真实结算→finalize cursor/statement/BLOB/backup→连接实际析构→所有VFS文件/SHM引用unmap/close与OS锁终态→child/stdio/channel/nativework真实结束→再终结各自名额。cleanup权限仅原对象原有限操作。普通短session恢复与永久owner drain分离，不以新session hello恢复旧lease。

[SQLite close接口](https://sqlite.org/c3ref/close.html) 明确close_v2可留zombie；故Python close返回、Store cleanup helper完成、native Promise fulfilled均不足。423b helper即使DB close失败仍尝试writer lease close；T01必须改为实际资源聚合，保持冲突新接纳关闭，实际持锁策略不能借原helper丢单writer。xClose/SHM/statement真实登记由native供方给事实，T01给所有child/worker/事务终态；不能互相用一个finished计数替代。

**main先崩溃而child仍持DB/SHM是硬反例。**安装控制锁被新main取得不证明旧child退出；named mutex abandoned/PID不存在同样不证明。单broker内存registry不足跨崩溃维持唯一writer：后续实现必须选择可核验的长期原生holder/child绑定恢复围栏，并证明main死后未收口holder仍拒冲突接纳；具体机制需与T01/T03冻结。当前尚无该供方，不声称已解决。持久intent保存旧root/未知资源，重启只恢复deny/retained，不能凭磁盘released标记复活grant或按timeoutGC。

错误对main/Python只给有限枚举（invalid-purpose、stale、denied-private、identity-changed、alias-unknown、unsupported-platform/filesystem、busy-writer、budget、durability-unknown、cleanup-unknown、internal），不透异常路径/业务内容；每个错误仍有真实资源归属，unknown不能等同可重试任意新库。

## 6. T01 的准确消费申请，交根路由

详细固定行号与12源码SHA见 t01-source-static.md。本表不给T01发任务，不动这些路径，也不新增第二Store/Job/canonical。

| 唯一T01 writer路径                                                                     | 必要delta与准入顺序                                                                                                                                                                                           |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apps/desktop/src/main/index.ts`                                                       | bootstrap实际profile/appData/安装来源；在目录/Store前取得用途；退出等真正永久drain。无fresh来源不自签                                                                                                         |
| `apps/desktop/src/main/engine.ts`                                                      | 替现仅env path/三个pipe为明确native child transport接收；保真实spawn/stdio/exit/closeowner；backup请求只给受限引用；真实stdin.write前同步核scope/epoch/原dispatch，无await空隙；request逻辑超时与后台终态分开 |
| `apps/desktop/src/main/task-service.ts`                                                | 候选/当前真实Store lifetime与project scope、operation归因；当前view generation不充库物理权                                                                                                                    |
| `packages/engine/src/ontolearn_engine/__main__.py`、`coordinator.py`                   | 生产模式无能力不mkdir/connect，不走env/default路径fallback；在JobStore前消费nativechannel与同库注册；保持worker/task真实排空，内部ready不是位置许可                                                           |
| `packages/engine/src/ontolearn_engine/storage.py`、`job_store.py`                      | `_sqlite3`唯一cap连接，先identity/use gate再header/catalog/迁移；同连接Store/Job事务保持；原生writer-lock与连接/SHM终态聚合                                                                                   |
| `packages/engine/src/ontolearn_engine/project/format3.py`                              | 把acquire_lease、目标xb/connect/rb/fsync/read_bytes每次重开换成同物理能力消费；source/target不同identity、人类迁移确认、备份真实finish/完整性/held对象hash；不把逻辑hash签物理身份                            |
| `packages/engine/src/ontolearn_engine/project/project_host.py`、`project_lifecycle.py` | 将来仅薄host接纳current_scope与原dispatch实际库binding，继续复用同连接reader/C1事务；resolution对复制A→B/旧代次/缺binding保持unknown，不从SQLclaim重建                                                        |
| `packages/engine/src/ontolearn_engine/worker.py`、`process_environment.py`             | 现worker无DB能力且不转发DB_PATH，保持；仅完整排空receipt必要delta，不能自动扩大为第二库消费者                                                                                                                 |

T01还需确定其专属新消费测试准确路径；建议新增 `packages/engine/tests/test_native_location_consumption.py`、`tests/unit/t01-native-location-transport.test.ts`，两者唯一T01 writer；实际登记前不创建。原57P0/PRD10–12、产品未决问题沿原决定表，工程支持集合不替用户选择。

## 7. B-R：稳定控制根、fresh来源及耐久缺口

固定ffb§5建议 `appData/知爻-OntoLearn-Studio/security-inventory-v1`，独立于可变userData。423b实际仅 `getPath('userData')/engine.sqlite`，所读index/builder未交付appData控制root、安装instance、fresh receipt或安装级单writer。appId和目录包不是这些来源；不存在header/ENOENT/新进程/模型不可用都不能当fresh。

| 交根的精确请求/owner                   | 必需实件；缺失策略                                                                                                                                                                         |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| T01可信bootstrap + 安装供方            | 固定产品/OS principal/多安装channel政策、真实OS appData parent/安装identity来源、迁移/历史保护位置清单与信任边界；产品appId不自行变安装instance。没有实件保持unsupported，不扫描全盘       |
| 安装/升级owner的fresh来源              | 可核验安装/升级provenance、此前历史如何交接、缺失/损坏/便携包/拷贝安装路径怎样恢复。仅可信明确无历史的独占新建立流程可bootstrap；丢来源只读保deny/unknown，不让用户删历史“重置”            |
| I06 native安装级仲裁 + T01旧holder终态 | 所有main/profile/安装共享一个实际root identity与OS锁，原锁inode不unlink；Win mutex权限/命名及实际controlroot锁须实证，abandoned只进入恢复。main死旧child存活围栏见§5.3，未闭合不发新writer |
| T03/平台耐久供方                       | 两目标OS/本地卷对文件与目录项的真实顺序/失败/掉电恢复契约；Win普通权限目录持久发布尚缺，Apple文件fullsync也不包办目录项。缺证据不授其他目标mutation                                        |

**只许原固定控制协议。**held parent/root先metadata及内存reserve；可信fresh且安装writer已取得后，exclusive建立固定root、`intents`、`seals`、immutable `header.json`。bootstrap期其他private/profile/DB目标IO0。每步create/write/sync/close/identity都真实确认后，才可进入可追加状态；partial/冲突/失败unknown保原件，不递归生意图、不重建空表。

self-append只限 `intents/<sequence20>-<recordId32hex>.json` 与 `seals/<同名>.json`，exclusive、完整写、同步、真实关闭、identity核验。intent含有限资源metadata、previous/sequence/实例、旧root/prospective/retired与未结算；seal关联精确intent bytes/digest。两者所需耐久确认完成前，不做其他目标mutation。任何未seal/孤儿/截断/重复/未知版本/超额/权限identity变化均保unknown；hash只验损坏不验OS释放。恢复先验证完整有限链再metadata重观察全部旧root，不能按PID/磁盘released开放。

沿ffb的工程提案上界：roots32/entries32768、单记录1MiB、正文总16MiB、1024对、depth128/path16384B。控制文件自己也计全局保护预算，满了拒新mutation、不截断/自动GC。没有额外项目/Job/main账本、SQL重放状态、密钥/密文/模型配置/业务正文。安装缺口不妨碍继续独立源码/临时格式设计，但阻塞真实生产B-R初始化与目标准入；不把缺口推给所有模块停工。

## 8. 精确路径与构建闭包申请

以下是拟新路径，根确认后才登记writer窗口；本轮均不创建。每个表格路径是明确集合，不能按目录泛权扩展。

| 拟新路径                                                      | 唯一writer              | 第一责任                                                                 |
| ------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------ |
| `packages/native-location/include/location_abi.h`             | I06                     | 版本化C ABI、精确用途/finite错误/真实资源终态；不通用opener              |
| `packages/native-location/src/capability_core.cc`             | I06                     | reserve/gate/实际对象/alias/epoch/撤销与有限registry                     |
| `packages/native-location/src/platform_macos.cc`              | I06                     | 逐对象/ACL/FD/受控spawn/channel/metadata及发布拒绝                       |
| `packages/native-location/src/platform_windows.cc`            | I06                     | RootDirectory/ACL/FileId/受限hProcess/HANDLE/实际completion              |
| `packages/native-location/src/node_binding.cc`                | I06                     | 仅node_api.h的控制绑定、真实async completion与cleanup                    |
| `packages/native-location/src/python_binding.cc`              | I06                     | 指定child接收peer、同image注册与有限用途接口；不自建DB-API               |
| `packages/native-location/src/sqlite_capability_vfs.cc`       | I06                     | 精确VFS/IO表及held对象消费，锁/SHM复用精确补丁设计                       |
| `packages/native-location/patches/sqlite-capability-os.patch` | I06，原始源/应用构建T03 | 固定SQLite os后端所有必要原语替换的最小可审patch；未有完整源不可预称完成 |
| `apps/desktop/src/main/security/native-location-owner.ts`     | I06                     | 私有薄装配，不接管T01Supervisor/公共协议                                 |
| `packages/native-location/tests/location_core_test.cc`        | I06                     | 有界状态和实际OS对象测试，mock只补状态非最终证据                         |
| `packages/native-location/tests/location_child_probe.cc`      | I06                     | 隔离真实child/handle/退出/未完成反例，仅测试目标                         |
| `packages/native-location/tests/test_capability_vfs.py`       | I06                     | 同build/实际VFS每角色/负例，受控临时库                                   |
| `tests/unit/i06-native-location-owner.test.ts`                | I06                     | main薄适配/实际addon契约，不用Promise品牌认证                            |
| `packages/native-location/CMakeLists.txt`                     | T03                     | 原生构建/目标/编译选项/测试入口，I06不得抢写                             |
| `packages/native-location/toolchain-lock.json`                | T03                     | 精确来源版本/完整hash/SDK编译器/许可/补丁/产物映射                       |
| `scripts/build-native-location.mjs`                           | T03                     | 离线可核验构建驱动、分架构输出与source核验                               |
| `scripts/build-capability-python.mjs`                         | T03                     | 受控CPython `_sqlite3`/同SQLiteimage重建与安装路径                       |

T03既有必要路径申请：`package.json`、`package-lock.json`、`pyproject.toml`、`uv.lock`、`packages/engine/pyproject.toml`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`、`apps/desktop/package.json`、`apps/desktop/electron-builder.yml`；源核验如需改 `scripts/verify-sources.mjs`另由T03明确登记，不把本表当已授权共享维护。当前build-engine仅PyInstaller，未建native，builder npmRebuild:false/extraResources只拷engine/contracts，不能自动包含新产物。

| 依赖/版本提案              | 精确来源与交付条件                                                                                                                                                                                                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C++17 / C ABI / Node-API   | 使用node_api.h，不用V8/node.h/内部libuv；Node声明>=24<25、Electron44.9.0、npm11.12.1来自固定package。实际Electron内嵌Node/Node-API版本须另证，Node-API目标版本冻结为所用API的最小交集；不额外引node-addon-api。Node许可/headers hash由T03登记。[ABI范围](https://nodejs.org/download/release/v24.0.0/docs/api/n-api.html#implications-of-abi-stability) |
| SQLite3.51.3源码可行性候选 | §5.1固定官方sourceID/SHA3；实际tarball/生成源码SHA256、完整patchhash、编译flags/线程/临时/扩展/mmap选项T03冻结；当前未下载。官方SQLite交付代码public-domain，构建工具许可单独核。[来源](https://sqlite.org/copyright.html)                                                                                                                              |
| CPython                    | 当前3.12系列/源码阅读v3.12.12用于兼容分析；正式pin、源码hash/安全维护/受控distribution重建、`_sqlite3`与extension实际同lib、Python ABI不得凭uv.lock推断。保PSF及实际第三方许可，不换apsw偷缩消费面。[许可](https://docs.python.org/3.12/license.html)                                                                                                   |
| 打包工具/运行库            | 固定uv.lock含PyInstaller6.22.3；CMake/Ninja/Clang/MSVC/Windows SDK/Apple SDK精确版本与hash尚未冻结，作为T03请求，不填写虚构“已安装/可用”。目标macOS15 arm64部署target与Win11x64 runtime闭包分别证明                                                                                                                                                     |

可重现构建验收：源/patch/工具链/SDK/flags/环境锁→两次干净同目标构建→可解释的产物差异及稳定payload哈希→Nodeaddon/Pythonextension/SQLiteimage实际依赖图→包内真实加载与VFStrace。分别记录构建机/目标OSbuild/架构/FS、签名状态与产物hash；签名时间导致差异不能删除原件来做伪逐字相同。不把uv.freeze/npm lock当CPython/系统SQLite/SDK锁。两OS资源及实际运行窗口由根提供，当前缺失不等价实现拒绝或产品永久不支持。

## 9. 最小第一实施阶段及后续实验请求

**N0：只做新私有native对象/元数据/真实终态切片。**根先确认§8中ABI/core/两OS/node binding/owner和前三类专属测试（VFS Python测试不在N0）、T03最小CMake/toolchain/build脚本窗口。无SQLite/用户目录/生产boot接线/持久B-R/新公共协议。以两目标OS受控临时root的真实held对象、single-component acquire、alias/替换拒绝、reserve-before-dispatch、真实FD/HANDLE/child关闭证据结束；publish只做具备真实保证的受控fixture操作，持续祖先/源rename围栏未交付仍unsupported。该阶段能独立实现有用底座，不把SQLite未通伪装已取得LocationLease。

N0开始前实际缺：根精确writer窗口、T03工具链/构建新路径接受、两目标OS隔离运行环境/授权。可先完成ABI/OS后端源码设计；编译/实验仍需后续窗口。N0完成不自动进入N1。

**N1：同库链接/VFS+真实child可行性。**T03先固定完整CPython/SQLite源与linkage；I06精确审OS层补丁、完整VFS、Pythonpeer/受控child；T01确认窄transport/DBAPI消费合同与全部actual close。只临时库，不生产fresh。若持续namespace、crash-old-holder、Win目录durability仍缺，保此三项具名block，不推进生产。

**N2：控制来源与T01真实消费。**安装fresh/历史/唯一writer/掉电恢复供方到位、B-R目标OS闭包、T01真实Store/backup/dispatch与完整scope/永久排空完成后，单独联验，再讨论主指针/公开host；B-L仓库/模型仍按各自精确窗口，不借native路径自动采用e2c整闭包。

| 将来隔离真实实验，两OS各跑 | 最小正例/负例与必须观测的原件                                                                                                                        | 层级                                                 |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 准入前零内容IO             | 未授权/私有alias/缺fresh/错epoch时，实际VFS及native read/write/header/catalog/backup计数0；系统级文件trace与原始返回相互校验，不只mock               | 无GUI隔离进程；OStrace需平台权限窗口                 |
| object/ancestry/member     | 真实根/祖先rename、member替换、symlink/reparse、hardlink、samepath新inode、ACL/volume变化；旧handle/历史保留，未能原子拒绝的窗口明确失败/unsupported | 无GUI目标OS真实FS                                    |
| create/publish/sync        | exclusive冲突、跨卷、source名被换、目标抢建、部分sync/close失败；原目标不被覆盖，未知耐久不放后续IO                                                  | 无GUI；掉电/VM重启另授权，kill不能替掉电             |
| 跨进程唯一writer           | 两真实进程争同DB/别名/同父不同名、多个connection同inode关闭干扰；只一长期writer，撤销后旧锁/SHM仍持则新接纳拒绝                                      | 无GUI真实进程/锁                                     |
| 传递/撤销/关闭             | 错child/PID复用/旧nonce/额外句柄、main先死child活、queued与runningIO、close_v2 zombie、backup未finish、SHM仍map、child晚close                        | 无GUI；真实terminal前不released，不超时删记录        |
| VFS全集/同库               | 真Store临时库覆盖主DB/journal/WAL/SHM/备份/temp实际opens，默认VFS/URI覆盖/ATTACH/extensions负例；同image依赖/源码ID/trace绑定具体二进制              | 无GUI，N1；Linux/Mac27不替两目标OS                   |
| B-R恢复                    | fresh缺失/旧迁移来源、并发main/abandoned、header/intent/seal每步中断/损坏/超额；未durable seal则其他目标IO0，旧child未知则拒新writer                 | 无GUI；耐久须真实目标平台故障窗口                    |
| dispatch/resolution        | A复制B的同UUID/hash/migration_id/claim不能解析原A；原发送前gate、当前scope、原Store物理对象三者独立。取消/响应丢失只读对账不自动重发                 | T01隔离集成，不等于正式UI/真人                       |
| 包内/桌面                  | 两OS各自包内加载同一受控库/私有addon/extension；实际app bootstrap与目录/安装升级来源、完整用户动作/57P0及目标验收                                    | 后续授权桌面/干净机/真人；当前静态与headless不能替代 |

原始证据必须保存实际argv/cwd/stdout/stderr/exit、首失败、源码ref/hash、OS/工具链/锁/产物依赖和同一受审candidate；trace不得记录业务正文/secret。注入故障仅补错误分支，不能冒充OS真实close/sync失败。通过后仅因新变化/失败/未解风险重验。当前无上表通过项，不复用B-M测试数量作native证明。

## 10. 独审、处置与冻结要求

原始平台报告主张自有CPython连接适配为优先；本方案在比较T01实际stdlib消费后选重建同库 `_sqlite3`，独立报告保原字节，差异在disposition记录，不编辑报告制造一致。该选择仍有T03构建实质代价，不写为现运行库已满足。

本轮交主方案、两份静态源报告、输入与B-M64身份、SQLite/CPython官方来源说明、独立agent对具体candidate的实质审查、逐意见处置、manifest和静态检查。主稿受审版本另保snapshot；最终修订给审查者逐条复核。manifest自排除且不自指提交hash，冻结Git ref由最终回执给出，避免假自包含。文档格式/差异检查不写为产品check/native通过。

完整父I06/57P0、指定GLM-5.3最高与M3.1-Flash xhigh对同base/head完整新审、意见关闭、目标平台/真人、CI、正常develop合并/远端门全部保持；原Goal不重建、不标父完成。根批准本方案也只得到可审实施申请，不自动授native产品writer或生产权限。
