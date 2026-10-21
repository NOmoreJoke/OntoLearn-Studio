# I06 项目位置能力与整组生命周期合同 offer

2026-10-21，docs-only、待总控逐阶段批准。**提供独立于模型初始化的完整保护 inventory、用途限定的原生 SQLite 位置能力，以及整组关闭/重建的 cohort 合同；当前没有可供 T01 使用的真实位置能力。**961 的 metadata-eligible 不升级，contentIo 继续 unsupported。本文件是具体实施申请，不授共享文件写权、不采用未批准实现。

## 1. 固定输入与事实边界

准备指令3994B/SHA256 `b62750cedae6083ef1e51efdd132fc3801c9fcdae21dc494d65e617ad42e3f5b`；AGENTS15852B/`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；共同指令17891B/`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。本轮实际读取，原Goal不重建、不改状态。

批准消费基线仍为5f910b52c69d86a1076b2032e5d3c63e715947f3。自有产品事实固定e2c269ad78a78e1a042cadc93b1c81a874707153，docs工作起点660da44aa7ad1b3ba7dbfb3a90fef37e25763ec8，分支feature/I06-model-gateway。当前产品与e2c相同；660另有已冻结的平台证据脚本，不能说所有tests等于e2c。独立guard固定961ce77f26accd11bd1cd3ad4a9e560cd3565e37。

已从Git全文读T01固定427ba7da6cc51016e98c15347e8b91a63f2c9232的project-host-integration-next-plan.md，29575B/SHA `f7ee5b859e07f2fb37f101e089387cf6a1eb06a64073f60d43df4bfd0af6f64d`，尤其H1/H2及§4–7；只消费设计，不读其5de运行实现。采用根已定的一库多项目SQLite、库级catalog/create与单项目scope分离、既有claims/context只读对账优先。源文件broker不授数据库访问，public UUID/hash/synthetic producer均不授权限。

FR-001/002要求模型不可用仍可本地工作和可选存储位置；S3要求私有凭据不进项目/导出、已发送网络数据不可撤回。历史合同和当前路径/输入SHA见[输入清单](../../reviews/I06/project-location-capability-offer/inputs.json)。本轮只新增本文及该review目录；不读运行凭据/用户内容，不执行产品、测试、build、Keychain、模型、GUI/native/e2e/HMR或付费，不push。

## 2. 实际权威来源、现有闭合与缺口

以下行号均为e2c，都是自有未批准产品的静态事实，不能当正式依赖：

| 来源                                                                       | 实际存在                                                                                                                                                                           | 缺口与唯一责任                                                                                                                  |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| main/index.ts:69–129、初始化位置96–104                                     | main实际app.userData路径；model-gateway-private-v1/{credentials,configurations,audit}；excludedRoots只有实际DB/-wal/-shm；初始化依次打开三仓库，失败closeModels，models可undefined | 没有独立位置owner/完整inventory；初始化失败吞为模型不可用，不能推导空保护集。index现在唯一T01，后续注入须其改                   |
| private-directory.ts:162–224、246–269                                      | POSIX目录anchor及dev/ino、0700/0600、祖先/别名复验；win32固定拒绝                                                                                                                  | 无跨OS metadata registry/原子位置能力；路径复验后普通fs.open不是原子闭合。此私有模块I06                                         |
| private-directory.ts:235–243、271–277、283–323、352–418                    | 枚举包含.pending；list过滤pending但不删；最多11024目录项；发布link可能留下final+pending两同inode名字，read只认对应受控pending别名                                                  | 面向内容仓库的list不是完整inventory；不能为inventory调用read/scan或解密。需另做metadata-only观察，保留所有pending及失败发布身份 |
| configuration-repository.ts、ciphertext-repository.ts、persistent-audit.ts | 配置journal最多1024；密文新增写入阈值4096、audit追加阈值10000（两者不是恢复扫描上限）；open扫描实际内容，失败固定拒绝，历史密文/审计不随当前配置删除                               | 不能拿当前configurations[]或listBindings当FS保护全集；未引用旧文件、pending、孤儿均仍保护。没有profile迁移或retired registry    |
| PrivateOperations:428–443                                                  | 每仓库最多32实际Promise，close禁止新接纳并allSettled现有操作后关目录                                                                                                               | 无对外drain receipt、跨仓库统一revision/初始化记录；close失败不能当退役完成                                                     |
| ModelGatewayService:63–106、152–171、190–224、529–535                      | engine构造期只读；同UUID早返；serial队列32；save不确定后failed且关context；close等tail                                                                                             | 不追踪所有真实engine/network未settled；配置内容恢复与metadata完整性应分开；无cohort身份和初始化late-install fence               |
| 961 transfer-guard-core-v1                                                 | 真实对象metadata token、本地revision/fence、有界观察；无真实FS                                                                                                                     | purpose仅import/export；database角色仍保护。不能修改其purpose或回调解锁本需求                                                   |

### 2.1 新权威只在可信main注册，不从模型状态推断

申请新I06 `main/security/private-resource-inventory.ts`，由T01 main启动入口注入实际profile owner、实际数据库cohort owner及I06仓库生命周期。唯一表只存**本应用自有资源的metadata和持有事实**，不是项目/Job可变账本，不含secret、密文、endpoint正文或业务数据。engine/renderer不收保护根清单。

生命周期从 `reserved → observing → complete`；任一owner缺席/观察超限/别名或权限不明/close失败进入 `incomplete|unknown|failed`，不可返回complete+[]。在任何仓库mkdir/publish前先同步reserve已知profile位置，失败仍保留reserve。不存在的叶子以已持有父目录身份+精确组件记录prospective；只在该元数据验证成立时认定不存在，不由ENOENT任意吞错。模型加密后端不可用与metadata不完整是两件事：独立metadata观察可complete而模型仍unavailable，允许确定性本地功能；metadata未complete则拒本次新位置IO。

保护范围包含整个model-gateway-private-v1根及未来后代，不仅三个bucket；三bucket现有/未来文件、发布临时名、同inode两名字、旧未引用记录全部保护。对profile的保守设计是先reserve完整userData容器及原生profile/sessionData实际根（后者须其真实owner提供）；模型根绝不例外。当前默认userData/engine.sqlite不是任意位置选择的白名单：仅真实main bootstrap已登记的**精确DB对象和伴随文件集合**可获数据库用途能力，不能凭名称后缀在profile内新建任意“DB”。普通picker选中profile内其它位置拒绝；外部用户选择位置仍完整支持，不能把固定userData当FR-002替代。该容器/精确DB例外需总控冻结，不改变961原导入导出禁DB策略。

active/retired不是“文件删没删”。保护项记录owner实例、profileEpoch、root/祖先的实际OS身份、当前/旧物理别名、持有者和unsettled计数。profile位置变更先登记新reserve，再使旧能力失效，旧项变retired仍保护。仅全部旧owner停止接纳、实际初始化/FS/原生调用/child/句柄已settled且明确释放，才可把持有态闭合；**持久残留文件/目录仍保留保护记录**，不能因0句柄解除路径保护。不存在或身份复用不能单靠时间判断；跨应用重启先恢复受控metadata退役记录并观察旧根，来源缺失保持unknown，不扫描全盘找硬链接。该退役记录需要未来单独批准持久格式/不覆盖发布；损坏不重置空表。

元数据观察不读文件正文：按已知根持有目录枚举，记录name/role/type/volume/fileID/linkCount/handle identity；私有leaf若多链接，须在同一观察边界内证明该身份的不同已观察目录项数等于实际linkCount，且这些名字全部位于保护集合，否则unknown（例如nlink=3只见final+pending两名仍不完整）。外部候选DB/伴随文件linkCount>1先有限拒绝；不能声称枚举已找遍全盘alias。目录祖先身份与候选文件身份双查；大小写/Unicode/短名等以OS实际句柄为准，不用JS lowerCase/realpath证明。范围是防应用误选、静态别名与生命周期/路径竞态；不扩张为阻止任意恶意同UID进程、全盘DLP或沙箱。

保护项须区分 `private-deny`、`profile-container` 与 `database-managed`。前两类在持有态闭合后仍禁止任意项目用途触及；database-managed关闭后保留 `released-retained` 记录及transfer用途保护，不是永久禁止该DB再次打开。新的可信open/reopen intent只有在旧组全部actual release receipt成立、无未settled持有、重新取得同物理身份的原生writer仲裁、完整inventory/所有成员校验通过后，才能为该精确DB组签发新cohort用途能力；不恢复旧grant、project scope或票据。旧DB组仍retired/unsettled或与private-deny重合则拒绝。崩溃后无完整receipt，须单独受控恢复流程以原进程实例退出证据及实际OS锁/句柄核验闭合，不能凭PID缺席、UUID相等、文件存在或一次null替代。此流程由根/T01另批，不把retired历史删除当解除。

### 2.2 跨owner一致性

inventory有进程实例+profileEpoch+单调revision和有限owner集合；owner先同步markMutation/失效所有旧issued能力，注册预期临时对象，再允许本owner原生操作，成功/失败/unknown均发布实际观察。新revision与旧revision禁止拼快照。任何不遵守该握手的写者使completeness不成立。完整观察与能力签发由同一串行authority协调，OS操作由原生adapter同一gate互斥；观察后await再按path打开不可用。

## 3. 拟冻结的窄能力：不是通用FS callback

接口名是待审私有合同，不是现存API/公共DTO。T01签发可信HostIntent，I06验证真实inventory并与原生adapter产生能力；T01仍唯一Store/DB内容owner。调用者不得提交inventory/safe:boolean/raw fd/任意callback，自造同形对象或字符串不获权。

```ts
// Main-private; real object identity held in private WeakMaps.
reserveCandidate(intent: HostLocationIntent): Promise<CandidateHandle | FixedFailure>
acquireLocation(candidate: CandidateHandle): Promise<LocationLease | FixedFailure>
bindEngine(lease: LocationLease, child: ActualSpawnedChild): Promise<EngineLocationBinding>
beginDrain(lease: LocationLease, reason: TransitionReason): DrainHandle
awaitReleased(drain: DrainHandle): Promise<ReleaseReceipt | UnsettledReceipt>
```

HostLocationIntent仅由可信main picker/bootstrap流程产生，含实际窗口/frame/document、主线程intent次序、用途、profile/cohort epoch和已持有父目录/选择对象。picker候选本身无内容IO权；取消发生在acquire前不建库、不迁移；acquire后取消只承诺停止后续接纳，已独占创建事实和清理须单独报告。与ChangeSet确认、模型grant、source proof完全分离。

| 用途                     | 允许的实际能力/首IO前门                                                                                                                                                                                        | 禁止与终态                                                                                                                                           |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| project-open-existing    | 身份/完整inventory先过；持有现存regular DB，no-create/no-truncate，元数据预检后在**同持有对象**读有界SQLite header，再由同child受限VFS探测schema/catalog；当前格式才授该库session                              | 缺失/空/目录/非DB/未来格式固定失败；不mkdir、不静默迁移/降2。只读探测不自动恢复hot journal或新建SHM；需要写恢复则转明确恢复/迁移动作，不偷偷升级用途 |
| project-create-new       | 已存在可信父目录；final及伴随名原本不存在；authority仅预留父身份+final basename，不创建final占位。另以O_EXCL/CREATE_NEW独占staging DB组，同child单Store初始化真实genesis，关闭/同步后一次native no-replace发布 | 不递归创建任意父目录、不覆盖/清空已有叶子；已有库内createProject是T01库级业务授权与同库原子claim，不是再取文件create能力                             |
| project-explicit-migrate | 先在受限只读探测下确定旧格式及准确动作/备份目的，再实际人类确认；源writer排空/独占身份锁，同child取得源和备份两精确能力；备份成功耐久且核验后才迁移                                                            | “打开文件”不等于迁移确认。backup不得覆盖、不得同源/同物理alias；失败保留源/已发生备份与原错误事实，不能静默删证据或重建                              |

header预算建议100字节（[SQLite固定header](https://sqlite.org/fileformat.html#the_database_header)），metadata-only无正文读取；任何SQLite连接即可能内容IO，必须在gate之后。catalog/Store/backup也必须同能力，不能先construct Store再补验证。源库WAL存在时header不等于一致格式证明，T01须在真实受限SQLite事务中再验；不靠hash代替授权。

### 3.1 真正跨到SQLite的adapter与fence

选定**原生位置broker + 同build SQLite capability VFS**路线，尚未实现。broker持有经过metadata gate的目录/文件句柄和精确角色表；T01实际child通过受控继承IPC/句柄获得绑定，不通过stdout/普通RPC/renderer传路径或capability bearer。main校验实际spawn对象、PID/进程实例、二进制/资源身份及cohort，先完成绑定再启动Store。mac用受控继承FD/本地socketpair的句柄传递，Windows用实际child process handle的DuplicateHandle及受限继承列表/受ACL保护的本地控制通道；传输细节须原生小阶段实证，不把猜测PID或pipe名当认证。

受限VFS必须注册在**该Python sqlite3连接实际使用的同一SQLite库实例**，绑定不透明库名到既持有句柄；不可加载另一个SQLite副本后假设Python连接受管。默认VFS回退、任意URI/ATTACH/extension、新文件路径/系统temp逃逸均拒绝；正式SQL仍经T01原Store/Coordinator，VFS不是第二写入入口。无法证明ABI/实例一致时固定unsupported，不上生产。SQLite官方定义VFS的xOpen/xDelete/xAccess等OS入口，不能只拦sqlite3.connect字符串。[VFS](https://sqlite.org/vfs.html)、[接口](https://sqlite.org/c3ref/vfs.html)

具体接入候选是启动时受信CPython扩展向已装载SQLite实例注册具名VFS，T01的location_binding.py只生成内部不透明库名及固定mode/vfs参数，Store使用该受控连接工厂；不向普通RPC开放URI。先由ABI小阶段核Python/_sqlite3实际动态库、sqlite3_sourceid/build清单和注册后实际连接的VFS/OS调用轨迹；仅比较版本字符串不够。若当前包静态链接/隐藏符号不能共用实例，须build owner精确批准重建同一_sqlite3与扩展的链接安排，不能另装第二SQLite或APSW后声称原Store受保护。

这一路线利用Python的uri连接和SQLite具名vfs参数，但ABI/打包可用性是待证明的设计推论。[Python sqlite3](https://docs.python.org/3.12/library/sqlite3.html)、[SQLite URI](https://www.sqlite.org/uri.html)。受限实现首版关闭DB mmap（mmap_size=0且xFetch不交出业务页映射），避免映射后读取绕过逐操作fence；WAL的SHM映射仍按SQLite要求保留到实际连接关闭，不能因撤销提前unmap导致进程访问悬空指针。[文件方法](https://sqlite.org/c3ref/io_methods.html)

原生gate将authority revision/lease状态、进程/用途/对象身份和该次OS操作入口序列化；打开后使用同一verified handle进行读取/写入/同步/锁，不check后另按path reopen。异步等待回来先复验epoch，再在native互斥下进入下一步；已入内核的操作先于撤销可以完成，必须计入事实。新位置签发、连接、备份目的发布及候选cohort发布前分别核lease，不能只核一次。目录项替换被拒或检测为stale；已持有旧对象不会变成另一内容对象。能力撤销后旧namespace不能用于新open/publish。

保持SQLite同平台原生锁语义，不能用unix-none、win32-none、纯path writer-lock或只有JS map。native VFS的xLock/xUnlock/xCheckReservedLock及WAL xShmMap/xShmLock/xShmBarrier/xShmUnmap须基于固定SQLite版本的原生实现适配句柄；不是写几行自造锁协议。需保留T01 writer lease并按真实物理库身份仲裁两路径别名；外部非本应用SQLite client仍依赖兼容SQLite锁，不声称应用lease能管任意进程。

### 3.2 DB文件组、备份和发布

能力中每项都是明确role，不授整个目录写入：main-db、wal、shm、rollback-journal、writer-lock；备份/创建候选拥有各自独立精确DB组。对尚不存在的伴随文件绑定父句柄+精确basename，第一次创建同步登记fileID再IO；已存在的每一项先查类型、链接、保护alias和原生锁。DB或任一成员与private-deny（含其retired）、未释放DB组、别的活库或备份相同身份均拒绝；已获released-retained的DB组仅按下述新用途再获取规则处理；两个main-db也不能共享同WAL/锁名。大小写/Unicode/Windows short-name/volume alias归一需原生身份验证。

不靠suffix白名单无限生成文件。SQLite可能用rollback/super-journal、statement/temp、VACUUM等文件；首阶段禁ATTACH、VACUUM INTO/任意扩展，temp_store=MEMORY且VFS拒任何未登记磁盘temp；内存超限明确失败，不暗落系统tmp。确有必要的journal角色逐项批准。未知现存journal不unlink“修复”；hot journal/WAL按受控恢复用途和SQLite规则处理。[临时文件](https://sqlite.org/tempfiles.html)

同库单writer身份锁在首header读取前取得，目录/文件OS句柄存活期间保持；mac锚定DB inode并处理POSIX进程锁close副作用，Windows用volume+fileID和原生byte-range锁。create目标尚无fileID时在authority预留精确父对象+最终名并对本应用所有进程仲裁；这不是OS已保留final名字，外部仍可抢占。另独占创建staging DB组，最终native no-replace是唯一胜负点；成功后将同一fileID连同名预留一起原子升级为active DB仲裁，不先释放再抢。锁文件本身也有身份和权限检查，不删除陌生/旧锁解忙。DB/WAL/SHM在迁移前必须所有自有连接/worker drain，不能仅等一条RPC终态。

backup选SQLite backup API，在受信源连接及exclusive新目的连接之间复制一致快照，不用读main DB裸拷贝漏WAL；该API会覆盖目的内容，因此目的必须由独占能力证明为本次新对象。迁移确认取消前零backup内容IO；取消后依实际阶段保存可恢复事实。[Backup](https://sqlite.org/backup.html)

create/backup最终发布选同卷受控parent，不覆盖原子publish；final从未由本流程放占位，不unlink或replace占位来发布。若最终名被外部抢占，发布失败并保留本次staging及真实冲突/unknown证据，不把authority名预留说成OS排他保证；先关闭候选SQLite连接、完成checkpoint并核无未闭合候选WAL/journal、同步必要文件后执行native no-replace publish，再同步受影响父目录并核验发布后对象身份与耐久结果，持有原fileID后续重开仍由VFS绑定。rename已成功但随后sync失败属于“已发布、耐久未确认”，不能当未发布重新publish或删除final；保留事实并进入unknown只读对账。不能在活跃WAL时只rename DB；跨卷不伪称原子，另提受控复制/恢复设计。失败后只清本次明确拥有且identity未变的未发布对象；namespace变更/不确定已发布则保留并unknown。崩溃后靠T01现claim/receipt和native持有记录只读对账，不造main提交账本，不自动重放create。

### 3.3 限额、寿命与撤销

以下是建议冻结的机制预算，不是Q5或产品容量承诺：一个进程最多1个transition、1个实际未settled picker、2个实际未settled metadata/native acquire、1个active和1个candidate DB组；每组精确角色最多16、备用目的1个；持有root最多32、metadata条目32768、组件深度128、输入路径UTF-8最多16384B（Windows另外核UTF-16限制）。超限completeness失败，不截断后报complete。该上界需原生/目标OS验证后才能采用。

候选metadata签发等待单调5秒、未兑换候选30秒硬TTL；acquire超时/abort返回固定失败但实际native操作继续占槽。成功连接lease不以30秒到期硬关SQLite，而绑定child/库/cohort/profileEpoch，直到显式drain/exit；每次实际操作仍经native gate。初始化/drain对UI可以5秒返回unsettled，但资源槽/retired identity不释放；重建不能重置计数。无自动续期或旧ticket复活。

状态 `reserved→issued→bound→quiescing→draining→released`，失败可到unknown-retained；revoke同步阻止新业务IO和未派发动作，已进入内核/SQLite事务的动作不假撤回。drain只允许既有精确句柄上的必要rollback/checkpoint/sync/close，不再读新业务/创建非既有角色，防止直接断掉所有xWrite导致半事务无法恢复；超过期限保留unknown与原件，不能报告released。只有实际操作settled、child close已观察且自有handle/lease释放齐，receipt才released。

固定私有失败reason建议 `invalid|busy|incomplete|unsupported|stale|cancelled|expired|conflict|unsettled|io-failed`，对外由唯一canonical另冻结映射；不透路径、OS错误正文、SQLite异常、root/fileID或用户内容。没有本轮新公共错误码授权。

## 4. 两个目标OS的实际原语与限制

**本轮未做任何OS探针。**平台支持是要实施并证明的合同；未知只阻塞相应能力，不能永久把Windows改成POSIX-only，或用Linux代替两个首发目标。

| 目标          | 具体adapter要求                                                                                                                                                                                                                                               | 限制/必须拒绝或补证                                                                                                                                                                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| macOS15 arm64 | 原生openat/fstatat逐组件相对dirfd，O_NOFOLLOW/O_DIRECTORY、fstat dev/ino/卷身份，exclusive create；基于同句柄pread/pwrite/fsync/兼容SQLite锁和SHM；同卷不覆盖发布及耐久确认                                                                                   | Node现path+fs API不提供本合同整体原子性。O_NOFOLLOW只保护该次末组件，必须逐祖先；APFS大小写敏感/不敏感和Unicode实际测。inode可能复用，保留handle+生命周期，不靠ino永久身份。本地APFS为首个实现目标，非本地/不明卷有限unsupported；不能把未测HFS+/外置盘假通过                        |
| Windows11 x64 | 原生CreateFile/NtCreateFile受控根相对组件打开、FILE_FLAG_OPEN_REPARSE_POINT/BACKUP_SEMANTICS、FileIdInfo及VolumeSerialNumber、reparse tag/属性/links、CREATE_NEW；DuplicateHandle绑定child；LockFileEx及SQLite win32兼容锁/映射；不覆盖发布与FlushFileBuffers | 最终组件OPEN_REPARSE_POINT不解决祖先junction；需逐组件原生relative handle方案并证明rename/share-delete限制。NTFS为首目标；UNC/网络卷、ADS、device路径、非本地/未知reparse拒绝；不是永久禁止Windows。case/短名/长路径实际验证，fileID只在卷/对象存活上下文比较；不把Node权限mode当ACL |

具体平台合同补充（均未实测）：

- mac原生发布使用持有parent fd+单组件名的renameatx_np，候选flags为RENAME_EXCL | RENAME_NOFOLLOW_ANY；Apple固定XNU11215.1.10头文件具有这些定义。卷不支持exclusive rename/身份未知时拒绝，绝不降为普通rename；实际macOS15/APFS仍需编译和冲突反例。[Apple固定头文件](https://github.com/apple-oss-distributions/xnu/blob/xnu-11215.1.10/bsd/sys/stdio.h)、[卷能力](https://developer.apple.com/documentation/foundation/urlresourcevalues/volumesupportsexclusiverenaming)
- mac同步区分fsync与F_FULLFSYNC，后者用于更严格的驱动器缓存顺序；不能从文档推出本方案的APFS rename/目录项掉电耐久已成立。native阶段要逐项核发布前后失败与同步可用性；发布后同步失败保留已发布事实。[Apple fsync](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fsync.2.html)
- Windows按实际HANDLE查FileIdInfo的VolumeSerialNumber+完整128-bit FileId、FileStandardInfo的NumberOfLinks/DeletePending/Directory及重解析tag；任一不可得则拒绝，不截断ID。NtCreateFile以RootDirectory逐组件打开，不能只靠最终叶子的OPEN_REPARSE_POINT。[身份](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info)、[标准信息](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_standard_info)、[NtCreateFile](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntcreatefile)
- Windows父anchor、active DB/sidecar、publish-source分别冻结access/share/delete策略；拒share-delete的旧HANDLE可能阻断本方发布，不能通过释放身份fence再path reopen解锁。发布候选用原受控源HANDLE经SetFileInformationByHandle/FILE_RENAME_INFO、受控目标RootDirectory及ReplaceIfExists=false；实际NTFS共享、重复句柄/SHM关闭与发布耐久仍实测，不声称等价POSIX目录fsync。[共享规则](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)、[不覆盖改名](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)
- Windows CancelIoEx只请求调用进程的I/O取消，成功或ERROR_NOT_FOUND均不代表settled；OVERLAPPED/buffer保留到原完成通道终态，main重复HANDLE不能取消证明child的在途IO。同步acquire/create/rename等真实调用返回后才减槽；CancelSynchronousIo也不是完成回执。[CancelIoEx](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex)、[GetOverlappedResult](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getoverlappedresult)、[同步取消](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelsynchronousio)

原生细节和官方链接的独立只读复核原文另保存在review中；选择最小adapter后必须同build锁版本审查，不靠文档存在声称能力已落地。ACL/ownership与原始祖先可信度须目标平台真实验证；Windows私有仓库当前主动拒绝，只能由后续精确Windows私有存储/metadata实现补齐。OS沙箱、任意同UID敌对写者不在本边界，仍需对普通rename/reparse/静态硬链接及应用自己并发做反例。

## 5. 固定engine持有者及cohort hooks

| 固定持有者/真实动作（e2c）                                                    | 当前完成含义/缺口                                                                                                                                 | 候选处理                                                                                                                 |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| index的supervisor/tasks/models全局；initializeModels/closeModels:69–129       | closeModels吞close失败并清全局；当前只初始化一次并检查quitting，若引入重复初始化则缺防旧结果install的cohort fence；before-quit5秒race不是排空证明 | T01宿主把candidate资源存在局部cohort，晚回只关闭自己的实例；新全局发布一次原子指针交换，不能旧close清新全局              |
| TaskService.engine:87、两个订阅91–92、dispose150–155                          | dispose取消recovery/view并unsubscribe、回调null；不等全部engine请求/child                                                                         | T01新实例，先阻接纳再dispose旧；晚unsubscribe绑定旧session，不能向新engine发；重建后重新从可信Job事实恢复                |
| ModelGatewayService.engine:72；open82–106；selectProject152–171；close529–535 | 同UUID早返；close关context等serial tail，但并非所有网络/source请求settled                                                                         | I06关旧后新建service，绝不改readonly engine或靠同UUID select重绑；非秘密配置可重新载入，不复活grant                      |
| GatewayApplication.source及projector、active:310–383                          | close abort、source/projector close、core.closeProject、清材料/preview；close返回void不代表underlying结束                                         | 新drain hook跟踪实际completion；core不直接持engine但随整个service/context关闭；field projector持source，不能漏重建       |
| StoredResultSource.engine:50、active48、request89–105、finally249–252         | abort可先reject包装Promise，底层engine.request可能未settled；active集合删除不是实际RPC排空                                                        | 新实际underlying promise registry独立于逻辑abort，真实settle才减槽；旧结果不得装入新context                              |
| EngineSupervisor.session.child/pending、finish201–238、stop240–245            | stop永久；finish reject清pending并kill，实际close更晚                                                                                             | T01提供真实stopAndDrain/child exit receipt，不改同实例restart；Worker/Store连接由T01回执覆盖，不以pending.size=0证明释放 |

兼容局部探针 `engine.ts:530–535 readEngineHealth()` 会临时创建Supervisor并finally stop；固定desktop调用图未接入它。未来项目/health路由禁止绕cohort调用此工厂，若正式启用也须纳入child实际close/drain。

Credentials boundary持仓库/加密adapter无engine；三个Repository持PrivateDirectory、PrivateOperations；ModelGatewayCore持credential/audit及grant/material，无engine；transport持实际socket/request。它们是资源持有链，必须纳入drain，但不假称都是直接engine holder。createElectronCredentialBoundary只核main/app-ready，实际backend在credential store/read才检查；初始化成功不证明Keychain/backend可用。现原生同步加密提示不能被JS abort中断；本轮不触发提示。

### 5.1 拟供T01消费的私有hook实件

```ts
prepareTransition(oldCohort, trustedIntent): TransitionToken // synchronous revoke/admission fence
quiesceModels(token): Promise<ModelDrainReceipt> // stop new calls; actual unfinished stays accounted
prepareModelCohort(candidateEngine, candidateIdentity): Promise<PreparedModels>
publishModelCohort(token, prepared, verifiedHostBinding): ModelBindingReceipt // synchronous
abortPrepared(prepared): Promise<DrainReceipt>
```

这些hook仅真实owner构造的对象可调用；receipt含owner/cohort对象身份、epoch、state和分类unsettled计数，不含secret/路径。T01仍持项目/库级scope、Job/claims；I06不给用户写任务授权。生命周期registry不保存第二份Job终态或新main幂等账本。hook失败不安装部分候选；ModelDrainReceipt不能替T01 Worker/StoreDrainReceipt，三者独立。

精确顺序：

1. picker未定只保留候选，不关闭当前项目；取消不复活之前已撤销票据。可信意图确定后宿主串行设transition，撤销旧preview/dispatch资格；停止模型新接纳，旧context设local并关闭application/source/projector/core grants/material，所有epoch先失效。
2. 旧确认/写请求未dispatch明确零派发；已dispatch保原operation/完整context进入unknown或按真实claim对账。T01先处理现claims/context，只读恢复优先，不从null猜未受理、不换op重放。取消source、取消模型、取消Job分别记录；过去已发送网络数据不可撤回。
3. 等I06实际初始化/密文/config/audit/source/network排空回执、picker/FS原生真实未settled计数及T01 worker/Store连接/child退出回执。任何unsettled保留旧retired保护和槽，不签同库新writer。可以保留最后视图为待恢复，不能假回到旧已授权context。
4. 候选位置完整inventory gate→执行能力→绑定实际新Supervisor/child。由这个child的唯一Store打开/创建/迁移，真实Store-ready、Job-ready/reconcile和同源协商hello后才transport-ready；此时尚不对外发布候选可操作项目。
5. 库级catalog/select解析实际UUID，T01安装最窄当前项目scope并核project.get/结构、域状态和批准协议；I06以新Supervisor构造全部固定引用、建立新context/local。若模型加密/配置不可用，可返回**已fence且无活跃旧引用的disabled-model binding**供本地确定性项目发布；inventory仍必须complete。不能用models=[]隐藏不完整inventory。
6. 同一主线程无await地核token/current profile+cohort、lease native fence、scope/真实project及I06 binding，完成候选指针发布；再安装新view generation，才对renderer显示可操作。两层ready是必要但不充分条件。晚IPC/配置/密文/来源/hello一律只归原对象/epoch；失败候选关闭保存证据，不抢切新项目。

同UUID主动重开、显式close后open、DB位置/格式迁移、新Supervisor替换均走完整transition，不靠UUID相等判断。普通renderer刷新/窗口恢复只换view epoch，普通同Supervisor transport瞬断沿既有只读恢复与grant政策，不能为未来切换扩大到“所有重连清授权”；换engine对象则不得遗漏重建。retired资源的迟到成功只可收尾原操作，不能发布新cohort或恢复授权。

## 6. 可批准的最小实施阶段/路径

**下列均为申请，当前只写docs。**每阶段单独冻结base/head/精确路径/测试/依赖，由根决定独立树，不在660/e2c/961原冻结树修产品。

| 阶段/owner                          | 精确候选路径                                                                                                                                                                                                                                                                                                                          | 独立产物与退出门                                                                                                                                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A I06纯inventory/生命周期           | 新`apps/desktop/src/main/security/private-resource-inventory.ts`、`project-cohort-lifecycle.ts`；新tests/unit/i06-private-resource-inventory.test.ts、i06-project-cohort-lifecycle.test.ts                                                                                                                                            | 合成metadata仅验证完整性/实际对象/epoch/retired/未settled状态机，不声称OS能力；不导出通用FS action                                                                                                  |
| B I06实际仓库供方                   | 既有model-gateway/{private-directory,configuration-repository,ciphertext-repository,persistent-audit,model-service,gateway-application,stored-result-source,stored-field-projector}.ts；必要时gateway/transport逐项另列                                                                                                               | 独立metadata-only owner与初始化reserve、publish登记、真实drain registry；这些旧路径需根明确窗口，不能借新增目录授权全改；测试新增i06-private-resource-owner.test.ts、i06-model-cohort-drain.test.ts |
| C 原生位置能力，I06供方/T01内容消费 | 建议新`apps/desktop/src/main/security/project-location-authority.ts`；原生候选`packages/location-native/src/{authority,macos-location,windows-location}.cc`；T01消费候选`packages/engine/src/ontolearn_engine/project/location_binding.py`、`packages/location-native/src/sqlite-capability-vfs.cc`（T01内容/VFS owner；I06仅broker） | 必须先原生adapter/ABI spike决定最少路径与唯一owner。native包清单/编译脚本/依赖锁/CI由真实build owner另提精确批准，当前不获写权；不假称TS模块能独立完成                                              |
| D T01宿主/Store接线                 | main/index.ts/engine.ts/task-service.ts及T01项目host、新Store open模式/VFS绑定精确路径                                                                                                                                                                                                                                                | 本轮只接口申请，T01实际实现另批；原有writer/Store唯一性、claims/context/真实scope/两层ready全部验证；不回收已交文件                                                                                 |
| E I06公开消费                       | preload/index.ts、renderer App.tsx；env.d.ts条件零diff、style仅获批布局                                                                                                                                                                                                                                                               | 当前四路径owner仍I06；真实named DTO/可信UI动作另批，未允许generic IPC或renderer路径；无UI实施授权                                                                                                   |

持久retired inventory记录格式/写路径、原生库/包内资源、共享canonical/错误、Supervisor child drain/dispatch guard、T01 Store连接注入均须根另冻结具体delta。它们是明确前置，不要求整个父功能完成才实施A/B。T03文件broker及其build四文件不随本offer转；C若需构建改动先向其owner提准确diff。

## 7. 分层验收计划与交根条件

当前全部是**未执行计划**；不把旧961/旧e2c数量贴给新能力，也不以独立agent替指定模型。

| 层                  | 必须反例/真实证明                                                                                                                                                                                                                                                                                                                                                   | 证据边界                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| 纯状态机A           | missing/failed init不为空；revision混拼/同值重开/ABA/晚init；active+retired/pending；clone/错owner/用途拒绝；abort不放实际槽；0句柄不删持久保护                                                                                                                                                                                                                     | 合成单测只证明机制                                              |
| 真实临时目录B/C     | 仅受控新目录，无用户数据/密钥：根/祖先rename、symlink/hardlink、prospective别名、final+pending同inode、损坏退役记录、close失败/发布后失败、目录项超限；各OS fileID/ACL/reparse/短名/大小写/Unicode；APFS发布前后sync失败/冲突，NTFS自身HANDLE共享冲突                                                                                                               | 必须真实FS，Node stub不替代native                               |
| 真实SQLite/VFS/进程 | gate前SQLite/header/catalog/backup IO计数0；no-create/no-migrate；两路径同库single writer；WAL/SHM/journal冲突；hot恢复需显式；取消/超时未settled、child kill/close、main重复句柄和child I/O分开；取消请求成功但原操作正常完成/ERROR_NOT_FOUND/仍pending，跨await撤销；临时文件/ATTACH/默认VFS绕过拒绝；备份不漏WAL/不覆盖；create发布各断电等价故障点及unknown收尾 | 要实际Python同库VFS/真实进程和故障原件，合成receipt不算         |
| cohort与main联验    | 同UUID重开vs普通刷新/瞬断对照；所有固定engine持有者替换；旧frame/epoch/晚密文/source不装新组；已dispatch对账不重放；模型不可用但complete metadata本地可用；inventory失败首IO0                                                                                                                                                                                       | 必须T01+I06同候选实际接线，旧原件保留                           |
| 目标OS/native/包    | macOS15 arm64与Windows11 x64分别真实adapter、SQLite锁/映射、进程退出/句柄继承、签名/权限与包内ABI；真实picker取消/位置/可操作发布/迁移确认                                                                                                                                                                                                                          | 远程/隔离获批环境，Linux不能替代，本机本轮不运行                |
| 发布                | 受影响专项、完整check/sources、实际unsigned包、目标OS与必要真人；同版GLM-5.3最高/M3.1-Flash xhigh双方全新全范围审查、CI/正常合并/远端                                                                                                                                                                                                                               | 候选/依赖变化重验重审；维护责任/设计通过不等于父I06或FR-002完成 |

提交给根的是固定输入清单、独立审查原文/逐项处置及本文Git blob；下一步根可先批准A、再定B/C原生验证窗口。未获得真实inventory owner/同build VFS和OS能力时，任何首次位置内容IO仍明确拒绝；这不是永久取消可选位置，而是把缺口变成可独立实施、验收和授权的阶段。
