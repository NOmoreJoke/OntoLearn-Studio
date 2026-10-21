# N0 固定候选平台实现窄审 R1

审查时间：2026-10-22（Asia/Shanghai）。固定完整候选为 `4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8`，所有产品引用及行号来自 `git show <该 ref>:<path>`，不是工作区后续修改。结论：未发现本范围新的确定 P1；原候选保留两项 P2 故障清理问题，以及一项应补直接声明的 macOS fixture 编译风险。不能据此宣布可编译、两目标 OS 通过或生产可用。根已通知正在修复的 WIP 不计入本报告结论。

## 输入与方法

已全文读取 N0 源码授权 `iteration-control/2026-10-21-weekly-release/I06-native-N0-source-implementation-authorization.md`。审查主对象为两平台实现及 `location_core_test.cc`，仅沿真实资源归属读取 core、ABI、child probe 和 Node fixture 清理调用点。前轮 platform-preflight 是设计资料，不作为本候选已经通过的依据。

本轮只做 Git/文本/hash 读取、官方原始文档比对和本新增文档检查；没有编译、测试、产品 import、native load、子进程或文件系统能力实验、GUI、Keychain。读取仓库源码不是执行待测 FS 能力。工作区存在 AGENTS、主说明、core、fixture 的他人 WIP，均未修改或采用；不提交。

下表路径统一以 `packages/native-location/` 为前缀，SHA 为固定 ref 的原始文件 SHA-256。

| 路径 | bytes | SHA-256 |
| --- | ---: | --- |
| include/location_abi.h | 13296 | fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172 |
| src/platform_macos.cc | 7702 | d1e8029714a336ce7614fe1aab52069a72f504b3b6c3c8cd128e59896d4e2b29 |
| src/platform_windows.cc | 12382 | 2a1c9d8ef75c81ccfaa965e3e4f9e31f5a12c590b59d9399e094407bbe09af02 |
| src/capability_core.cc | 16734 | f90a45b5a8e50237191139a9f1e80709fe5a4e5c1eef4cf4c28dad1c9ab2e4b4 |
| src/node_binding.cc | 13163 | e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383 |
| tests/location_core_test.cc | 23353 | 07e86432553ed0f0fe52b3d06ea656de9d55fd460dbe883a995d58a41ee906e8 |
| tests/location_child_probe.cc | 380 | 041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c |

## 需要处置的具体问题

### P2-1：两个 unresolved open 可耗尽所有 cleanup admission

位置：`src/platform_windows.cc:130-141`；`src/capability_core.cc:43-61,258-264,334-338`；ABI `include/location_abi.h:16-24`。

Windows 为 `NtCreateFile` 的输出句柄与 IO_STATUS_BLOCK 使用静态 `open_record`，避免异常 pending 的输出指针指向离栈内存，这是正确方向。但 core 对平台 `NL_RETAINED` 一律设置 `call.reserved=false`，不递减 process-wide inflight。第一个 unresolved open 后，新 acquire 仍可占第二个名额再发起一次 open；若同样 retained，inflight 永久达到上限 2。之后 release/poll/close 都先经过同一个 admission，返回 BUDGET，已知、与该 unresolved open 无关的 FD/HANDLE/child 也无法继续清理。这不是把未知释放当成功的问题，而是清理通路完全失去接纳机会。

最小反例是两个连续 acquire 均落在该明确保留分支，再对原 owner 的已知 root/child 调用 close/poll。同步 gate 已空闲，仍会因总 inflight 满而拒绝。当前 fixture 没有驱动此 OS 故障；本报告是分支推演，不称实际 Windows 发生。

建议第一项 unresolved work 即封住全局新 acquisition/owner/child adoption，保留原有限 cleanup 所需名额；或采用明确独立、有限且不会误销原 work 的 cleanup admission。异常 NT 错误带非空输出和真正 pending 应分别记录：前者是输出归属不明，不能叙述为仍在运行的 kernel request。原 ref 的 platform 返回值没有区分这两类。

### P2-2：ACL 释放未知连带阻止已知文件 FD 的首次 close

位置：`src/platform_macos.cc:70-80`；`src/capability_core.cc:87-94,211-216,267-274,288-293`。

当 `acl_free` 非零，platform_metadata 返回 RETAINED；core 随即把 object 标 unknown，而 close_object 在第一行就返回 false。该 unknown 原因属于 ACL working-storage 的释放结果，并不表示先前已经成功获得的 FD 编号不确定。当前分支会保留这个已知 FD，连一次合法 close 都不尝试；后续关闭同样被 unknown 挡住。

建议分别表达“附属 metadata allocation 未确认”和“文件 handle 的关闭状态”：已知 FD 仍 close 一次，结果无论如何不重试编号；原 ACL unknown 保留且不得因此签 owner drained/unload。不要把已有 FD 关闭成功签成 ACL 释放成功。

限制：Apple 固定 [Libc-1669.0.4 acl.c:46-55](https://raw.githubusercontent.com/apple-oss-distributions/Libc/Libc-1669.0.4/posix1e/acl.c) 的 acl_free 实现总返回 0。本项是候选显式故障分支的归属缺陷，不是声称该固定 Libc 已可自然触发真实 free 失败；运行验证应精确区分实际平台事实与注入。

### 编译风险 C-1：fixture 使用 kill，但没有直接包含其声明头

位置：`tests/location_core_test.cc:20-27,135-138`。此 TU 的 mac 分支包含 sys/wait.h、unistd.h 等，未直接 include signal.h，却使用 kill 与 SIGKILL。

官方固定 [Libc-1669.0.4 signal.h:74-84](https://raw.githubusercontent.com/apple-oss-distributions/Libc/Libc-1669.0.4/include/signal.h) 声明 kill。固定 [xnu-11417.101.15 sys/wait.h:88-105](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.101.15/bsd/sys/wait.h) 只为 siginfo_t 引入 sys/signal.h，并警告不要依赖其他符号的传递暴露；[sys/signal.h](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.101.15/bsd/sys/signal.h) 提供 SIGKILL，未提供 kill 声明；同版 [Libc unistd.h](https://raw.githubusercontent.com/apple-oss-distributions/Libc/Libc-1669.0.4/include/unistd.h) 未见 kill 声明。

建议在 mac 分支显式 include signal.h，不依赖 C++ 标准库或 spawn.h 的偶然传递声明。未取得所选最终 SDK spawn.h 的完整 include 闭包，也没有编译，因此本项不写作“已观测编译失败”。须由固定目标工具链验证所有非模板函数体，包括 fixture cleanup 的异常路径。

## 已具体核对的调用与资源归属

### macOS 实现

- `platform_duplicate_anchor:35-41` 先初始化 out，F_DUPFD_CLOEXEC 成功即把副本交 core；后续 metadata 拒绝仍有 owner。成员 `openat:43-56` 使用 held parent、单组件、NOFOLLOW/CLOEXEC/NONBLOCK；目录为 O_RDONLY/O_DIRECTORY，普通 leaf 为 O_EVTONLY，随后 fstat 类型/uid/mode/nlink 过滤。没有正文 read 或绝对路径 reopen。SDK 对 O_EVTONLY 与 ACL getter 的实际组合仍须目标验证；不因字符串 flags 就声称权限完全正确。
- `platform_metadata:58-86` 的 ACL entry 返回值符合固定 Apple 实现：[acl_entry.c:109-136](https://raw.githubusercontent.com/apple-oss-distributions/Libc/Libc-1669.0.4/posix1e/acl_entry.c) 对 entry 返回 0，对有效空 ACL 的 FIRST 返回 -1/EINVAL。此版先 acl_valid，再清 errno、取 FIRST，free 后核结果，没有把 Linux 的 0/1 惯例误搬到 Apple。它只接受空 extended ACL，不认可未知 ACL；[Apple acl_get_fd 文档](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/acl_get_fd.3.html) 说明 getter 返回独立 working copy，需要 acl_free。
- `platform_close:88-91` 成功才 confirmed；core 随即退休编号，失败不再 close 同编号，符合本 ABI 的保守 unknown 策略。未实际注入 EINTR/EIO，不给运行通过。
- `platform_duplicate_child:98-113` 使用确切自有 waitable PID 与 WNOHANG；ECHILD 在未接管前拒绝，其他错误仍保留 wait responsibility。`platform_poll_child:125-139` 只在 waitpid 返回该 PID 且 exited/signaled 后 terminal；0/ECHILD/未知错误不签结束。已 reaped 后 pid 归零，不再 wait 复用号码。原借用约定要求其他 reaper 已停止，native 本身不能验证所有外部线程都遵守。
- `platform_duplicate_pipe:115-123` 先保存 dup，再 fstat；非管道拒绝时 core 仍持这个副本，后续 cleanup 可 close。当前也允许 S_ISSOCK；POSIX FD 可正常 close socket，因此不是 Windows closesocket 归属错误，但若最终 fixture 合同只允许匿名管道，应明确收窄类型。现 fixture 真正提供 pipe，没有 socket 正向证明。

### Windows 实现

- `duplicate:42-48` 的目标与源都是当前进程，FALSE inheritance、没有 CLOSE_SOURCE，借用句柄保持调用方所有；[DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle) 允许不同权限副本，也明确禁止用它复制 sockets。本候选不把 token pseudo-handle 送进 duplicate，也不关闭 token pseudo-handle。
- `fixture_acl:50-104` 用对齐的固定 1024B descriptor/256B token 缓冲；失败/超限拒绝，owner/DACL/SID/ACE 范围逐项核查；缺 DACL/null DACL/默认或继承/非允许或非当前 SID ACE 均拒绝。线程 impersonation 查询只接受 ERROR_NO_TOKEN；查询 token 不产生 owned HANDLE。[GetCurrentThreadToken](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentthreadtoken) 的 pseudo-handle 正是线程 impersonation token，不应 duplicate/close。此固定缓冲是保守容量拒绝，不承诺全部合法 Windows ACL 都通过。
- `platform_open_member:114-146` 为有效 UTF-8 的单组件构造 UTF-16/UNICODE_STRING，长度以 bytes 表示且有界；RootDirectory 为 held handle；FILE_OPEN 不创建；同步 NONALERT 与 SYNCHRONIZE 同用；REPARSE_POINT 后又在 metadata 拒 reparse。签名参数与 [NtCreateFile](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile) 类型对应。未带 share-delete 有意使某些 rename/delete 拒绝，不应把这当持续 namespace fence。目录 flag 组合及固定 SDK 的声明/链接仍未实编。
- `platform_metadata:147-166` 只接受 DISK；按实际 HANDLE 查询 FileIdInfo/StandardInfo/AttributeTagInfo，拒 reparse/offline/deletepending/零 links 和普通文件多 links。身份复制 exact 128-bit file ID，volume 用 ABI 规定 LE；未把 path 字符串/case 当身份。
- `child_matches/duplicate_child:171-190` 先 GetProcessId 验过程对象，再 CompareObjectHandles 拒同 kernel object 重复接管和 current process；不同 borrowed handle 数字不绕过比较。PROCESS_QUERY_LIMITED_INFORMATION 与 SYNCHRONIZE 是后续 GetProcessId/Wait 所需权限。Windows 没有在此证明“由该 harness 创建”或“无其他 waiter”；这是 native trusted fixture 前置条件，不是 API 证明。
- `platform_duplicate_pipe:192-201` 在稳定 borrowed source 上同时核 FILE_TYPE_PIPE 与 GetNamedPipeInfo，然后仅复制 SYNCHRONIZE。FILE_TYPE_PIPE 单独可能包含 socket，本版第二个查询关闭了该类型混淆；fixture 交读端 output，满足 [GetNamedPipeInfo](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-getnamedpipeinfo) 的读权限要求，也可用于 CreatePipe 匿名管道。不能把此方法扩展成任意仅有 SYNCHRONIZE 的 borrowed source 都能通过查询。
- `poll/close_child:203-216` WaitForSingleObject(...,0) 仅 OBJECT_0 为 terminal，TIMEOUT 仍 pending，其余 retained；signaled 后仍需 CloseHandle，关闭失败退休编号并保 unknown。普通 handle close 同样不重试编号。没有把进程 exit code、kill 返回或超时当释放。

### fixture/child 及跨平台收尾

`location_core_test.cc` mac fixture:45-92 使用 mkdtemp 自有根，设置空 ACL、0700 子目录及 0600 leaf；所有实际 fixture 创建/替换/alias/清理均留在测试 TU。成员链接负例是真 linkat/symlinkat，非模拟返回。根 rename 后 publish 仍 UNSUPPORTED，不把 held root 当持续名称许可。mac child:93-143 显式关闭 child 中原 pipe 两端并 dup stdin；不运行 shell；仅未转交 wait responsibility 的 child 才由 harness kill/wait。

Windows fixture:145-221 用当前 SID 的 protected 显式 DACL，CREATE_NEW leaf；link/reparse 用真实 CreateHardLink/CreateSymbolicLink。CreateSymbolicLink 的开发者模式/权限若不足，当前会使 fixture 失败（固定错误标签），不能报告 reparse 负例已通过或偷偷忽略。root rename 可以实际成功，也允许由于 held handle 的共享限制被拒；这两种不能在未来 raw 合并成“rename 成功”。

Windows child:222-294 的 CreateProcess 使用实际 absolute executable、显式 handle-list、仅继承 read_input/write_output。hProcess/hThread 与四 pipe ends 均有字段归属；spawn 后立刻关闭 child ends 和 thread；constructor 失败走 cleanup。借用原 hProcess 即使接管成功仍属 harness，cleanup 可 CloseHandle 原副本，但不得再次 wait/reap；owner 持自己的 duplicate。fixture 只把读端 output 送 native，harness 保留 stdin write end 到 end_input。

`capability_core.cc:113-129` 明确先关 objects 和所有 owned pipes，再 poll child。因此 mac input_record 送 stdin 写端副本不会形成“等 child exit 才关写端”的循环等待；只调用 poll_children 在 end_input 前确实保持 pending，也正是 fixture 检查。`nl_owner_revoke:305-308` 只改原子 epoch、不持 gate，故不能仅凭 acquire 的 try_lock 就断言 `location_core_test.cc:385-404` 并发 revoke 必然 BUSY。该用例自身也明确不证明 OS syscall 期间被撤销，后续不能抬高覆盖。

失败清理：C fixture 的 require 抛错最终 main 返回 1；不能用析构器尽力清理或进程结束等同 owner drained。child 已转交时析构器不再 kill/reap；若 owner 仍 retained，须保存失败与未结状态，不能记成功。Node fixture 的 harness cleanup 先注册、owner hook 后注册，目标为 LIFO owner-first；但这并不证明所有绑定失败/异常已经完全释放，库仍禁止在 retained owner 下卸载。此处只核平台交界归属，不替代完整 Node binding 审查。

## 可编译性及下一固定候选验证边界

源码可见布局为固定 64-bit intptr_t、显式 C ABI/noexcept/calling convention/输出初始化，header 的 size/offset/align 静态断言覆盖 records；这些断言尚未经过 macOS15 arm64/Windows11 x64 编译器验证。C++17 标准库 mutex/thread/atomic 与 OS headers 必须使用同一确定目标配置。

T03 还须固定 mac SDK/部署目标，核 O_EVTONLY、F_DUPFD_CLOEXEC、openat/ACL 声明和 libc 链接；Windows 明确 _WIN32_WINNT/NTDDI/SDK 与 CRT，验证 NtCreateFile/Ntdll、ACL/Advapi32、普通 Kernel32 API，以及 [CompareObjectHandles 的 Kernelbase.lib](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-compareobjecthandles)。不能仅链接 Kernel32 就推断全部符号解决，不能以手写未知结构代替 SDK 声明。NL_NODE_FIXTURE_HOST 必须与 NL_WITH_NODE、实际 Node-API 头和唯一 registry 链接一致；fixture host 与 addon 不得各自再编一份 core。

本审没有发现额外确定的 API 参数类型错误，但没有目标编译证据，尤其 C-1 声明闭包和 NtCreateFile directory/reparse flags 应作为精确目标检查。后续需新固定 ref 验证两 P2 修复；不能将根口头 WIP 修正倒贴到 4cff。目标 OS 下的正向空 ACL/严格 DACL、真实 alias、部分 child adoption、pending→实际终态、close 未确认、撤销后晚返及工具链链接仍未验。N0 无 SQLite/VFS/SHM、无内容 IO、无发布源围栏、production admission 恒 unsupported；本审不引入新 DLP 或任意同 UID 持续攻击保证。
