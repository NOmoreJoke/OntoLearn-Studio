# N0 平台与 ABI 静态预审

2026-10-21。结论：fixture-only C ABI 的 held-object/metadata-only、失败 close 不重试号码、真实 child wait 与 pipe close 分离的方向成立；**本报告不授源码技术通过、编译通过或目标 OS 通过**。Windows 的 pipe 类型核验、固定安全描述符缓冲解析、macOS 空 ACL 返回约定和原 reaper 唯一性必须按下述精确条件实现。未读到的完整平台候选不由接口预审替代。

## 1. 输入及操作边界

全文读取根授权 `I06-native-N0-source-implementation-authorization.md`，6089B/SHA256 `fc4a74b81530197a3aa38d0bcc5027d952d83c64d7f0a6cd5be2abdd3c9ce4ee`。本树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，分支 `feature/I06-native-location-N0`，读取时 HEAD 为批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；protected AGENTS 为 15852B/SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。

初次全文读取 header 初稿；实现方同期完善接口后，全文读回 `packages/native-location/include/location_abi.h` 的 9093B/SHA `de93bab66e27f5c7936a1d391130ea7cef724a2d21f48d440d36504a624e0e63` 版本（含 child receipt、固定 byte order、Node fixture-host entry 与若干 layout assertions）。该文件正在由唯一产品 writer 修改，本报告是此接口及明确新增 API 选择的预审，不是后续全部变更的自动复审。初次查看目录时两个平台 cc 尚未存在；本报告不把其旧草稿或后续未冻结源码当最终实现。

唯一新增本文。没有修改 header/六产品/测试/构建/锁，没有编译、syntax-only compile、动态加载、产品import、native/FS/child 实验、GUI/Keychain/模型请求。官方资料只通过只读 web 读取，未下载源码、SDK或工具。T03 构建闭包及精确运行授权仍缺；本树未有 Prettier 依赖，未借其他树依赖或安装工具。

## 2. ABI、布局及所有权

### 2.1 可静态对齐的布局

以下是 64 位目标、自然对齐且未用 packing 时的**预期**，不是本轮编译器结果。T03 须在 macOS15 arm64 与 Windows11 x64 的真实工具链证明 C/C++一致；不支持32位或用 `#pragma pack` 偷改。

| 记录 | 预期 size/alignment | 关键 offsets |
| --- | --- | --- |
| nl_owner_ref | 8 / 8 | value=0 |
| nl_cap_ref | 16 / 8 | owner=0, slot=8, generation=12 |
| nl_identity | 24 / 1 | volume=0, file=8 |
| nl_metadata | 48 / 8 | version=0, kind=4, identity=8, links=32, acl=40, held-only=44 |
| nl_fixture_anchor | 32 / 8 | version=0, platform=4, borrowed=8, reserved=16 |
| nl_fixture_child | 56 / 8 | version=0, platform=4, process=8, pid=16, pipes=24, reserved=40 |
| nl_child_receipt | 24 / 4 | version=0, slot=4, wait_owned=8, terminal=12, pipes=16, reserved=20 |
| nl_snapshot | 48 / 4 | 12个uint32字段，从0到44各相隔4 |

原“全部 fixed-width”对 intptr_t 的含糊已在读回版改为两个目标恰为64位；byte order亦已明确：volume为unsigned64 LE、mac inode占file前8字节且其余清零、Windows FILE_ID_128按opaque原字节。不得memcpy含padding的整结构当身份，也不得把fileID当JS number；所有输出先初始化，reserved为0。64位HANDLE按intptr_t bits转换只在native fixture ABI内，不是可传 renderer/JSON 的能力。

读回版已加 `extern C`、NL_CALL、NL_API、NL_NOEXCEPT和静态断言，这是源码约束，不是已链接证明。C ABI不得抛C++异常；只有两个固定目标、同一header/ABI version的调用方，不宣称自动兼容未知大/小结构。后续若扩结构需独立ABI版本/明确size协商，不能在旧调用方buffer写新尾部。T03须固定符号导出、calling convention、C++17/CRT、Node-API headers与宏；detail namespace须隐藏，不能因声明在同一header而成为公开供方。

### 2.2 借用与 partial adoption

- anchor/pipe/Windows process的borrowed原句柄始终由harness持有，至少稳定到adopt返回；owner只关闭自己的duplicate，不DUPLICATE_CLOSE_SOURCE、不fclose/CloseHandle借用者号码。失败也不得回收或修改原FD/HANDLE。
- mac child PID不是可duplicate的对象句柄。adopt承担的是该**本进程可wait子进程的唯一wait/reap责任**；必须拒PID0、负PID、非child、已被其他reaper取走、同一live child重复adopt。Node不暴露child adoption是重要边界，可避免与libuv的既有waiter抢reap。
- 新 `nl_child_receipt.wait_owned` 正确补足partial失败交接：wait_owned=1后，即使某pipe duplicate失败，owner仍负责原child终态；为0则harness仍是唯一reaper。Windows borrowed原hProcess仍可由caller按借用合同关闭，不能混同owner duplicate与reaper责任。
- 任何dup/query以后失败、撤销/TTL越界、查询ACL出错，实际新对象仍归原owner cleanup。若close结果未知，永久保留unknown号码/槽且不再碰该号码；后续close只能处理其他资源或继续等待原child。
- `nl_owner_close` 的“nonblocking”仅针对try-lock gate。真实同步OS调用本身不承诺确定时间返回；不得把5秒逻辑等待当它已结束。N0没有async queue/maps/messages/ancillary，不能据常量0宣称已经验证这些后续资源。

## 3. macOS：metadata-only 与 ACL

### 3.1 已有原语与目标验证点

`openat`相对held parent处理一个组件，`O_NOFOLLOW`拒最后目标symlink，目录还须目录类型约束。组件先严格UTF8/长度/NUL/分隔符/点点检查；返回对象再fstat/权限/links/expected identity核对，后续observe仍用原FD而非path reopen。Apple固定 [xnu-11417.101.15 open手册](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.101.15/bsd/man/man2/open.2) 明确这些接口；不等于对所有macOS15 SDK/runtime组合已验。

`O_EVTONLY`是事件监测用途，官方还明确它不阻止volume unmount。它适合限定本轮不读正文的目标方向，**但O_EVTONLY目录FD能否用于本轮全部openat/fstat/acl_get_fd_np组合，仍须真实目标OS验证**，不能因宏存在写成已可用。借用anchor若原本权限更宽，dup会保留原open-file-description；N0只能声称自身API不读正文，不能声称dup已降为更窄内核权限。复制时用可用的原子close-on-exec策略；不对dup执行F_SETFL改O_NONBLOCK来改变借用者共享的状态。

ACL必须由held FD读取而非path getter。Apple [acl_get_fd(3)归档手册](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/acl_get_fd.3.html)区分POSIX access ACL与`acl_get_fd_np`指定类型，说明返回working-copy需要acl_free。目标应明确使用Darwin extended ACL；不把不支持/读失败当empty，不用mode700替代ACL。UID必须是实际当前受信principal；owner同UID、group/other无写只是独立必要条件。

### 3.2 固定Apple源码确认的空ACL条件

已实际只读Apple官方 `Libc-1669.0.4` 三件：

- [posix1e/acl_entry.c:109–136](https://raw.githubusercontent.com/apple-oss-distributions/Libc/Libc-1669.0.4/posix1e/acl_entry.c)：FIRST映射index0；index不在实际entries范围则返回-1并设EINVAL；实际取到entry返回0。
- [posix1e/acl.c:81–86](https://raw.githubusercontent.com/apple-oss-distributions/Libc/Libc-1669.0.4/posix1e/acl.c)：acl_valid调用内部validate宏后返回0，留有XXX；不是完整语义/内存验证器。
- [posix1e/aclvar.h:104–110](https://raw.githubusercontent.com/apple-oss-distributions/Libc/Libc-1669.0.4/posix1e/aclvar.h)：所用validate失败设置EINVAL；内部主要判特殊指针/对象magic。源仅用作语义核对，不复制其私有struct布局进产品。

据此，**只对由本轮OS fd-getter实际取得、非NULL、由当前调用独占未改的working ACL**，可以采用以下源码级推导：先要求acl_valid==0；清errno；FIRST返回-1且立即保存errno为EINVAL，才解释为该实现下empty；FIRST返回0就是存在entry，绝不能把它当空。其他结果全部拒绝。先保存errno再acl_free，避免cleanup覆盖判据；无论分支都释放真实ACL副本。

这不是把所有EINVAL解释为empty，也不是接受调用方传来的任意acl_t。无效ACL同样可EINVAL，故“真实getter成功+独占working-copy+valid”前提不能省。若实现无法保持该前提，则unknown拒绝。N0为保持正向空ACL可用，可选择仅接受上述empty extended ACL，非空一律保守拒绝；若要接受owner-only ACE，应完整冻结Darwin返回约定、权限集合/qualifier/继承语义，不套用Linux的1/0/-1迭代模式。固定Libc tag不自动等于目标macOS15的实际libc二进制，正/负ACL及O_EVTONLY组合仍待目标测试。

### 3.3 close与child

Apple [close(2)固定手册](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.101.15/bsd/man/man2/close.2)列EINTR/EIO等失败；本轮不从失败推测号码仍归自己，保持unknown且不retry原编号正确。它也意味着槽不会因后续EBADF或同号新FD而释放。

按 [Apple waitpid(2)](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/waitpid.2.html)，实际poll采用确切自有PID与WNOHANG；返回0仍pending，返回确切PID且是exited/signaled终态才记录reaped。ECHILD、未知错误或外部SIGCHLD/reaper策略导致不可wait是unknown，不能把PID消失当完成。不能用PID通配符或wait任意child。原PID一旦真实reap，后续不再wait该号码，也不把号码复用的另一进程当原child。

## 4. Windows：API、访问权与缓冲

### 4.1 held metadata可行性

[NtCreateFile官方页](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile)支持ObjectAttributes.RootDirectory相对held目录打开；FILE_OPEN_REPARSE_POINT是打开reparse自身，不是批准穿越。每个返回对象都应检查FileAttributeTagInfo/reparse、FileStandardInfo的类型/links/DeletePending、完整FileIdInfo identity；取得信息失败即拒绝，不降级Node dev/ino或pathname。

用途建议保持实现方所定的metadata access：`FILE_READ_ATTRIBUTES | READ_CONTROL | SYNCHRONIZE`；目录再按需要加入FILE_TRAVERSE。不要用GENERIC_READ（包含FILE_READ_DATA）或MAXIMUM_ALLOWED，不开备份/提权intent。SYNCHRONIZE不等于已完成任何IO；child采用实际process wait，metadata handle不拿来代替异步IO completion。

同步模式应另明确`FILE_SYNCHRONOUS_IO_NONALERT`与所需SYNCHRONIZE配对；仅请求SYNCHRONIZE访问权并不设置该CreateOptions模式。不能用宽泛NT_SUCCESS数值判断代替实际完成语义。官方NtCreateFile页说明同步flags但未列STATUS_PENDING，本轮没有复现其pending返回；若后续选择任何可pending的NT调用，IO_STATUS_BLOCK/输出缓冲和原槽须活到实际完成，不得因逻辑等待返回就销毁。

FILE_CREATE/OPEN_IF/TRUNCATE/OVERWRITE均不属于N0；只用已有对象的FILE_OPEN。RootDirectory输入必须是已验证parent、child名是单组件，禁ADS/分隔/绝对路径/点点/非法Unicode；普通成员替换只能导致新实际对象/expected mismatch或unknown，不能宣称持续namespace锁。share-delete策略、开前既有DELETE handle和目录rename仍须目标证明，不从ACL快照签持续许可。

### 4.2 固定SD/token缓冲是可实施的保守guard

[GetKernelObjectSecurity](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-getkernelobjectsecurity)接受caller buffer和长度，返回self-relative security descriptor及所需bytes；owner+DACL需READ_CONTROL。file属于Windows kernel object，[官方对象表](https://learn.microsoft.com/en-us/windows/win32/sysinfo/kernel-objects)列出file/pipe/process及其不同关闭函数。因此对已核file/directory HANDLE用该API读取owner/DACL是合理候选；无需改用按路径GetFileSecurity。

固定1024B SD、256B TokenUser是本轮工程拒绝上界，不是Win API承诺任意合法ACL都能放入。调用失败、needed超过界或异常长度必须拒绝且不能解析未填充buffer，不动态加大上界。buffer用适当alignas，TOKEN_USER包含指针，不能依赖char数组偶然对齐。使用返回内容前校验descriptor/ACL及其范围、ACE类型/大小、SID有效性/长度；只读取buffer内实际成功返回的working-copy。

[GetSecurityDescriptorDacl](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-getsecuritydescriptordacl)明确DaclPresent=false与pDacl=NULL均不能作为空ACL遍历成功；NULL DACL允许所有访问，必须拒绝。[GetTokenInformation](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation)允许caller有界buffer，TokenUser需TOKEN_QUERY。

仅支持owner SID与当前TokenUser一致、已知allow ACE全部为该owner且无继承/其他ACE类型的极保守策略可接受为fixture-only范围；这比“无额外可写ACE”更严格，会拒绝常见继承SYSTEM/Administrators条目，必须给harness显式安全fixture，不得把普通Windows临时目录默认DACL当正例必过。未知callback/object ACE、SID、generic mask或flags不得忽略；不得仅扫描几个write bits而漏DELETE/WRITE_DAC/WRITE_OWNER/目录delete-child。此处不做通用Windows AccessCheck或任意同UID攻击者证明。

辅助token HANDLE也属于真实资源。如果为取principal调用OpenProcessToken，真实关闭失败不能丢在metadata helper内；可用 [GetCurrentProcessToken](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentprocesstoken) 的Win8+query pseudo-handle避免新增real handle，它不需要close、不可duplicate。N0仍须明确不支持thread impersonation或保持一致有效principal，不能拿process TokenUser替代另一个正在生效的thread token而声称相同身份。

### 4.3 duplication/process比较

[DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle)可按用途降权、不继承，不能带DUPLICATE_CLOSE_SOURCE，不能无条件DUPLICATE_SAME_ACCESS。复制失败不转借用原handle的所有权；返回duplicate之后的错误都需owner跟踪。anchor/member按上述metadata权，process按`SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION`，pipe只需关闭/持有时可收窄为SYNCHRONIZE。

[CompareObjectHandles](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-compareobjecthandles)比较实际kernel object，不要求额外object-specific权限，可用于拒同进程对象重复adopt，即使原两个handle数值不同。也可用于识别current-process pseudo对象误传。它不能证明harness创建了该child或独占其wait责任，后者仍是native fixture调用约定。官方Requirements明确Win10+、handleapi.h、**Kernelbase.lib/Kernelbase.dll**；此前消息暂提OneCore.lib已纠正，不能当已验证链接配置。

process poll仅`WaitForSingleObject(hProcess, 0)`真实返回signaled才终态；WAIT_TIMEOUT为pending，WAIT_FAILED/其他结果unknown；不得拿STILL_ACTIVE或某exitCode值判断，更不得在CloseHandle后继续wait。process signaled后还需分别确认owner自身duplicate hProcess和pipes实际close；borrowed原句柄与其他进程引用不由此宣称全部释放。[WaitForSingleObject官方页](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)、[CloseHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle)。

## 5. 必须处置的pipe类型反例

**P1-N0-PLATFORM-01，平台实现选择待落实**：若`platform_duplicate_pipe`只检查GetFileType==FILE_TYPE_PIPE，就会把socket也当管道。官方 [GetFileType](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfiletype) 明确PIPE包括socket/named/anonymous pipe；[DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle)又明确不要用它复制socket，可能干扰内部引用计数。socket需closesocket而非管道CloseHandle；不能先复制后才发现类型不支持，否则新增对象本身已经需要独立正确关闭。

可审最小修正候选：在稳定borrowed原handle仍有权限时，先用 [GetNamedPipeInfo](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-getnamedpipeinfo) 做真正named/anonymous pipe的metadata核验，再duplicate成SYNCHRONIZE。它不读正文，但官方要求读端GENERIC_READ或写端GENERIC_WRITE加FILE_READ_ATTRIBUTES，所以不能对仅SYNCHRONIZE duplicate调用并假设会成功。借用输入权限不足则unknown/unsupported拒绝，harness应给满足精确契约的两pipe。禁止为核验而读取/丢弃正文、WSA初始化/另建socket、等待EOF或扩大公开capability。另一精确原生分类方案若被选择，须有官方依据并单独验，不把FILE_TYPE_PIPE本身当充分证据。

POSIX可在稳定borrowed FD上fstat并要求S_ISFIFO，拒S_ISSOCK和其他类型；N0只持有/关闭自身dup，不读取管道数据。两个borrowed entries若是同一pipe的重复handle，是否允许/如何计所有实际dup必须写清；不得仅因一个terminal child就把所有pipe计数直接归零。

该项在初期API消息中已发给唯一实现方；此报告不擅自关闭意见。之后若实现已补，只能依据其固定新源码/必要后续验证由独审确认，不能把本预审版本当产品bug已验修复。

## 6. T03编译/ABI前置清单（本轮全部未执行）

- macOS15 arm64：实际SDK中O_EVTONLY/openat/nofollow/F_DUPFD_CLOEXEC及DarwinACL声明，适用availability/feature macros；ACL_ENTRY返回语义及errno；实际clock monotonic选型，size/offset/alignment assertions；libc及必要ACL链接来源。
- Windows11 x64：明确_WIN32_WINNT/NTDDI/SDK版本；NtCreateFile声明与ntdll导入/受控解析方式及NTSTATUS调用约定；不是把LONG status套GetLastError。FILE_ID_INFO/FILE_ATTRIBUTE_TAG_INFO等SDK类型、权限/flags、Advapi32安全API、Kernel32基础handle/wait、Kernelbase CompareObjectHandles链接；不能用手写不明布局替缺失SDK定义。
- C ABI：C和C++17相同布局/版本、全部输出初始化、reserved校验、有限状态、不可抛异常；只公开批准符号，私有detail不导出。未经新ABI版本不兼容未知struct尺寸。
- Node：NL_WITH_NODE的fixture-host C入口仅native harness可调用；JS无raw fd/HANDLE/create/adoptchild入口。NAPI headers/目标版本、环境生命周期与唯一owner持有关系须T03固定；当前没有真实addon加载或Node-host正例，TS假binding不是它的证据。
- 资源计费：GetKernelObjectSecurity caller buffer不产生需LocalFree的输出allocation；Darwin ACL working copy、可能的real token handle、dup、pending child、pipe均须计责任。library卸载/进程结束不倒称unknown close已证。

## 7. 后续最小目标OS正反例

本轮仅列待批准验证，不运行，也不以B-M、Linux或macOS27代替：

1. 正向held目录/普通文件metadata：内容read/write syscall为0；Mac真实empty extended ACL、Windows current-user显式DACL；O_EVTONLY目录FD的逐组件取得/ACL可用性；两OS实际identity lossless与expected mismatch。
2. symlink/reparse/普通文件多link/未知类型/目录与file错配/当前principal或ACL变更；unknown不path reopen、不转allow。目录nlink不作为普通文件alias数；ACL/owner取值失败与超1024B、TokenUser预算均拒绝。
3. Windows socket作为借用pipe应在duplicate前拒绝；真pipe（含适用读/写端权限）能只持有/close；两pipe partial失败必须保正确wait_owned及已dup资源，输入原handle不被关。
4. 自有child alive→真实0-timeout pending→真实终态；Mac不可wait/ECHILD与其他reaper、同child重复adopt；Win不同handle同对象、pseudo/nonprocess输入、wait失败；原child/handle仍活时不得按TTL清槽。
5. close失败仅注入测试与实际OS失败明确分开；失败编号不retry，另资源继续cleanup；取消/TTL与gate竞争的late metadata结果归原owner，30秒TTL不释放实际持有。
6. 两OS各自固定source/header/build/toolchain/产物hash与C ABI布局证明；T03未给之前不syntaxcompile、不手写替代build。完整N0 source candidate仍需独审，不由本文替代。

本文没有声称无阻断、技术通过、生产位置许可或完整两OS安全闭包。已被读回版header吸收的布局/byte order/partial receipt问题与仍须处置的pipe/ACL/工具链项分别列明；当前职责到只读平台/ABI预审和唯一独立文档为止。
