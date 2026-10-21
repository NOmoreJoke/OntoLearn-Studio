# I06 N0：九件源码独立对抗审查 r1

2026-10-22。结论：**固定候选存在三项本审确认的P2，须在本源码阶段修复；另有一项P3合同一致性问题。当前不能关闭源码独审。** 另已读接口独审P2-IF-01并按同一固定源码核其失败责任缺口，保持该独立意见待新候选关闭。以下全部为静态可达路径推导，未执行反例、不声称已有红/绿或目标OS结果。

## 1. 固定输入与范围

完整受审Git ref：`4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8`，工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，base为批准5f。只读取该ref产品，不将作者正在修复的工作区WIP混入首审。

此前已全文读回根授权6089B/SHA256 `fc4a74b81530197a3aa38d0bcc5027d952d83c64d7f0a6cd5be2abdd3c9ce4ee`、新树AGENTS15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。本轮全文读取九件固定源码/测试、同ref主说明 `docs/iterations/I06/native-location-N0.md`、source-text-check.json及必要平台预审。九件均独立通过Git blob实算bytes/SHA，与清单相同：

| 路径 | bytes | SHA256 |
| --- | ---: | --- |
| `packages/native-location/include/location_abi.h` | 13296 | `fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172` |
| `packages/native-location/src/capability_core.cc` | 16734 | `f90a45b5a8e50237191139a9f1e80709fe5a4e5c1eef4cf4c28dad1c9ab2e4b4` |
| `packages/native-location/src/platform_macos.cc` | 7702 | `d1e8029714a336ce7614fe1aab52069a72f504b3b6c3c8cd128e59896d4e2b29` |
| `packages/native-location/src/platform_windows.cc` | 12382 | `2a1c9d8ef75c81ccfaa965e3e4f9e31f5a12c590b59d9399e094407bbe09af02` |
| `packages/native-location/src/node_binding.cc` | 13163 | `e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383` |
| `apps/desktop/src/main/security/native-location-owner.ts` | 12496 | `e354b0830469647d70690f3e1d6e567c816f70cbbbe5c211dabba817fa7cc8d0` |
| `packages/native-location/tests/location_core_test.cc` | 23353 | `07e86432553ed0f0fe52b3d06ea656de9d55fd460dbe883a995d58a41ee906e8` |
| `packages/native-location/tests/location_child_probe.cc` | 380 | `041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c` |
| `tests/unit/i06-native-location-owner.test.ts` | 8460 | `e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04` |

本文下述行号均对应此ref。唯一新增写入为本报告；未改产品/测试/说明/AGENTS/已有报告，未提交。命令均显式cwd为本新树；实际动作只有Git/文本读取与Python stdlib的JSON/hash检查，正常exit0。没有编译或syntax-only compile，没有运行产品/测试/import/addon/native/FS/child实验，没有借其他树依赖、安装工具或GUI/模型/凭据/Goal操作。

## 2. P2-N0-01：永久pending工作耗尽全部admission后，其他原资源也失去cleanup入口

### 位置

- `capability_core.cc:43–62`：所有admission共享process-wide两槽；release/close/poll也需先取得该槽。
- `capability_core.cc:257–264`：open返回NL_RETAINED后将call.reserved置false，永久保留原inflight。
- `platform_windows.cc:130–145`：STATUS_PENDING或失败伴异常输出均返回NL_RETAINED，结果存储确实在静态opens内。
- `capability_core.cc:298–303,334–338,376–379`：已知对象release、owner close和child poll没有独立可用的cleanup admission。

### 静态反例

1. owner A已持有root及其他已知对象/child。
2. 第一次member open返回代码已明确处理的STATUS_PENDING，inflight留下1；owner资源保持unknown是正确的。
3. gate释放后，第二次新acquire仍能取得第二槽并再返回NL_RETAINED。inflight变为2，两个静态pending输出都未被错误回收。
4. 此后对任何owner调用release/close/poll，admission第一步一律NL_BUDGET。即使另一个对象已确定仍归本owner且尚未调用close，或者child已经真实退出，也没有入口完成其合法cleanup。

影响：有限上界没有越过，但全局错误态把“保留未知操作”扩大成“所有无关原资源永久不能清理”。主说明披露可能耗尽槽，不足以替代根授权要求的原有限cleanup；这不是要求超时清槽或重新碰未知号码。

### 最小修正与需验证的条件

首次出现此类未结算native work时，同步封所有后续新owner/open/child接纳，保留剩余容量用于原资源cleanup；或者提供经根同意、仍在原两槽总预算内可证明的等价划分。不能简单增加上限、把pending减槽或允许第二次新open再耗掉cleanup槽。

还应把“真实未终态work”与“失败输出/资源归属未知”区分清楚。两者都应保unknown，但不应没有实际在途work也伪造一个永久work completion事实。本审没有复现Windows同步open实际返回pending；问题是当前显式异常分支不满足自身cleanup不变量，需源码阶段先闭合。

将来获批定点验证至少断言：第一次unknown后新接纳被封，其他明确FD/HANDLE仍能恰close一次、child仍能poll真实终态；原pending未知/静态存储/原槽保持，owner不得被签released。不能用纯注入证明真实OS pending已经发生。

## 3. P2-N0-02：把metadata unknown混同“已尝试close未知”，导致确切持有的FD永不关闭

### 位置

- `capability_core.cc:87–94`：close_object遇object.unknown立即返回false，不检查是否仍持有未尝试close的object.value。
- `platform_macos.cc:70–80`：acl_get_fd_np成功取得真实ACL working copy后，acl_free失败返回NL_RETAINED；该FD本身尚未close。
- `capability_core.cc:211–216,254–255,266–274,289–293`：root/parent/member/observe可因该metadata返回值设置unknown。

### 静态反例

root adoption或member observation取得真实FD；fstat和ACL getter已返回，唯ACL cleanup无法确认。core将对象标unknown。之后release或close_all都会在unknown提前返回，原已知FD从未收到第一次close，且以后永远没有机会。这和“close调用之后失败、号码可能已被重用，不能再碰”是两种不同状态。

影响：错误处理既不能认证ACL/owner终态，又不必要地长期持有确切FD。root失败初始化同样可触发，耗住active owner和系统对象。保留unknown是正确的，放弃该已知FD的首次有限cleanup不是必然要求。

### 最小修正与需验证的条件

分离metadata/ACL未知、尚未尝试close、close结果未知；对value!=-1且未尝试close的确切FD/HANDLE执行恰一次close。无论结果如何立即退役该号码；原metadata/ACL未知保持，不可仅因FD close成功将owner签为released。真正close未知的号码绝不重试，也不能EBADF探测回补槽。其他资源仍按各自状态继续cleanup。

将来定点验证应覆盖root/parent/member/observe中的至少代表分支，并区分“metadata未知但FD未close”与“已经close失败未知”。目前测试没有该反例；本审没有伪造acl_free真实失败。

## 4. P2-N0-03：上一个OS步骤晚返后，下一次新dispatch未复核TTL

### 位置

- `capability_core.cc:202–219`：owner create的clock先于dup/metadata；末尾只查epoch，没有最后active/TTL。
- `capability_core.cc:243–258`：acquire在入口active后可阻塞于parent metadata，下一member open前只查epoch。
- `capability_core.cc:347–374`：child真实adopt及每pipe duplicate可以晚返，下一pipe前只查epoch，全部完成后才active。

### 静态反例及合同解释

第29秒进入parent metadata，系统调用第31秒才返回。在没有别的调用触发active过期时，epoch仍为1。257行继续dispatch新的member open及metadata，到271行才返回stale。类似地，child adoption/第一pipe晚返后，下一pipe仍可被复制。owner create亦可能在完整初始化越30秒后返回OK，直到caller下一次调用才知道已过期。

单个已经dispatch的OS操作必须保留原资源直至实际返回，不能强行取消或假定五秒结束；问题是晚返回后又启动了下一项新操作。根在本轮审查沟通中明确选择保守合同：每个这种后续dispatch前重新active(owner)，owner create最终也复核active，不以整个同步链一次接纳代替这些检查。按此明确合同，本项是源码阶段必须关闭的P2，而不是把已接纳单次syscall跨TTL完成本身当错误。

### 最小修正与需验证的条件

parent metadata、实际child adoption及前一pipe晚返后，在下一member open/pipe dup前做active；owner create在最终返回OK前同样复核。过期后只处理原有限cleanup和责任receipt，不再发新cap或新dup。原已经承担的child wait责任和partial pipes不得因stale丢失；所有晚返回对象仍归旧owner。

当前并发revoke测试不是可确定的clock/晚返回覆盖。后续需固定时间或已授权可控阻塞的专属反例，记录新dispatch计数0及旧资源未丢；本轮禁止执行，未创建测试开关或公共fault callback。

## 5. P3-N0-04：macOS pipe用途接受socket，与已选有限合同不一致

位置：`platform_macos.cc:115–123`，最终允许S_ISFIFO或S_ISSOCK；平台预审建议仅FIFO，主说明称其核验真实pipe。

具体反例：可信fixture误把一个socket FD放进borrowed_pipes，函数dup后fstat为S_ISSOCK仍返回OK，计作child pipe。此处POSIX dup/close本身适用于socket，不能误套Windows socket需要closesocket的风险，也不构成正文或网络发送入口，所以本审不升级P2。

根已明确N0无socket需求，应收窄为FIFO。将来定点负例应验证socket不被接纳，同时借用原FD不被关闭、已有duplicate若已创建则仍按实际所有权清理；不得为凑覆盖增加socket能力或公开child API。本轮未创建或运行socket。

## 6. 接口独审P2-IF-01：不同作者发现的失败责任缺口保持待关闭

本审完成九件阅读后，另全文读了同目录 `interface-source-review-r1.md`，其固定产品输入同为4cff。此意见归该独立作者，不归称本审首先发现；本人按已读源码确认其触发链成立：

- core_test:433–447在fixture/owner创建并注册fixture hook后，直接return bind；bind在node_binding:220/223/226可在注册owner hook前早退，局部owner责任没有由fixture持续持有。
- Node cleanup:193–198只做一次revoke/close且忽略结果；fixture hook:425–428只核fixture自身cleanup。owner若BUSY/RETAINED，POSIX名字清理成功不是FD/child已收口证明，可能没有明确测试失败。
- hook注册失败的一次close结果也不能被当无资源。static registry正确保留未知，不等于测试host已闭合自己的责任。

此项应随新候选复核，不能因本审其余接口形状成立而被掩盖。fixture必须持续记原owner，在所有失败/teardown路径负责实际cleanup与未知时明确测试失败；不重试已退役号码。普通native消费者仍另需T03给实际image pin/生命周期来源，不能把同步env hook当动态库保活。本审未读取或验证工作区拟修复代码。

## 7. 其余静态判断与明确限制

### 7.1 registry/预算/epoch/partial责任

固定owner静态地址及单次发布ID不重用；cap lifetime slots不回收，generation固定1配合单owner slot不reuse，未见ABA复活路径。总owner历史32/active2、cap128/name16KiB/depth128及child2/pipe2是固定工程上界；没有caller可调限额、默认无界队列或超时减实际槽。未知close号码立即退役、其他owner不混成某owner释放的方向正确，但受前述两cleanup缺陷限制。

POSIX child采用确切可wait子进程、WNOHANG真实终态才reaped；ECHILD不是释放。Windows先验证process并比较实际kernel object，再取得受限duplicate，实际signaled后另关process handle。receipt.wait_owned在后续pipe失败时保留原责任；未见用非OK结果一律回滚成“未adopt”的路径。原借用句柄与native duplicate分开，Node不暴露adopt。测试只有未来自有child目标，没有另起业务Python。

### 7.2 OS对象与API可编译性边界

Mac held parent单组件openat、O_NOFOLLOW/CLOEXEC、fstat/extended ACL及无损dev+ino属于真实API消费，文件使用O_EVTONLY；没有正文read/write/truncate路径。ACL空集合按平台预审固定Apple返回约定处理，不把任何EINVAL单独当空；getter来源、valid、FIRST结果与保存errno均有要求。仍未证明实际macOS15 SDK/ACL/O_EVTONLY组合可以编译、链接或运行。

Win对RootDirectory下单组件只FILE_OPEN，desired access不含正文GENERIC_READ；返回对象核type/reparse/offline/DeletePending/links/完整FileId。SD/token使用有界对齐buffer，先成功范围核再逐ACE/SID保守拒绝；只有当前principal owner-only known allow。使用pseudo token避免辅助HANDLE未追踪，thread impersonation拒绝。pipe先GetNamedPipeInfo再duplicate，已经覆盖平台预审的Windows FILE_TYPE_PIPE包含socket反例。

没有通过编译器验证NtCreateFile/SDK feature macros、CompareObjectHandles/Kernelbase、GetCurrent*Token/Advapi32、Darwin ACL声明/链接和全部ABI assertions；也没有实际加载证明。T03三新构建仅onlydocs，不能用本审静态检查填这些门。未知OS分支显式unsupported、core test返回77不等于目标通过。held对象只证明原对象，不证明持续祖先namespace；publish确实直接返回unsupported且无OS调用，未发现路径重开后签生产能力的入口。

### 7.3 Node/TS与同image

八个Node方法与TS strict表对应；external cap先比较当前binding固定token地址成员再解引用，无JS整数fd/PID或路径bootstrap。UTF16长度和surrogate先检、UTF8再限255B；identity为hex、links十进制字符串，未经double。TS own-data捕获及WeakMap只是薄投影，源码没有把任意JS表认证为native。capture异常/未知throw封本地接纳并保原cleanup；late wrapper遇reentrant revoke拒绝。生产admission始终unsupported。

native host入口及测试宏不证明同一registry/image已经实际链接。普通addon只有flags，真实fixture只有test-only模式。env hook并不self-pin库，host不得在retained时卸载的要求仍需T03装配实件。没有因当前源码存在而自动取得Python/VFS、生产bootstrap或T01共享路径写权。

### 7.4 测试可执行条件与假绿

core test普通main要求一个绝对child_probe路径；Mac spawn和Windows applicationName/引用command line与唯一--hold-until-eof相接。test-only addon模式排除main、提供bootstrap，需T03将core/platform/node/core_test四TU放进同一image，不能host和.node各复制core后传相同ID。child_probe错参64、stdin错误1、EOF0；core只认真实终态，未验证每个child正向exit code或全部故障。

TS synthetic组只证明projection，不证明OS；真实组只有显式绝对artifact才加载，缺输入skip不补fake。真实组finally要求close OK，能阻其正常方法路径的close假绿，不能替bootstrap/teardown的IF-01。core并发revoke测试已明示只是非确定竞争表征，不是确定“在途OS被撤销”覆盖。

现有测试未覆盖P2-N0-01/02/03确定边界。它们的测试源码存在不代表已经执行；缺少这些反例不应通过已有parseDiagnostics0掩盖。当前TS仅语法parse，不是完整类型检查；所有C++均未编译。未来故障注入要明确只证错误分支，不冒充真实OS失败或目标平台通过。

## 8. 处置结论

针对4cff完整九件：P2-N0-01/02/03及接口作者P2-IF-01均需新候选关闭；P3-N0-04按根已选FIFO合同收窄。唯一产品writer应保4cff与首审原文，不在本报告中追贴WIP修复为已关闭；后续给完整新ref/九件hash及实际diff再定点复核。当前无需越权编译/运行来证明源级反例。

本阶段的源码修复与后续N0构建/目标运行分开：即便上述问题静态关闭，也只得到待构建源码候选。T03固定构建来源/实际编译/完整TS类型、两OS实际metadata/alias/取消/close/child/晚返仍未通过；N1同库SQLite/VFS、跨崩溃oldholder、fresh/历史/B-R耐久、T01永久排空/dispatch/scope、公开首IO与父I06/57P0、指定双模型/CI/正常合并/远端门均原样保留。没有自动扩大为恶意同UID或全盘DLP要求。
