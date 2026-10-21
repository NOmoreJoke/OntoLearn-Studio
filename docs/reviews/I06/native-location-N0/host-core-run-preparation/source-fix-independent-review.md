# Darwin fixture 无覆盖 rename 最小修复独立静态审查

2026-10-22（Asia/Shanghai）。固定完整源码候选：`b59239f9c1ec2774c7922f95dfc67db4dc8754e8`；比较基准：`b1c54c3de840e657aba07906587681f6415085d6`。只审既有 Darwin fixture root rename 的目的覆盖修复、声明闭包与失败清理路径，不扩新 fixture、生产 API、发布能力或威胁边界。

结论：普通 rename 可能替换已有空目的目录的具体问题，在新候选中以 `renamex_np(...,RENAME_EXCL)` **源码层闭合**；未发现本次最小 diff 新增的确定阻断。此结论依赖 OS/FS 实现该 exclusive flag 的真实语义，尚无新编译、链接、运行或目的冲突故障验证。旧 b657 产物已被主线标 superseded，本报告没有执行它，也不授权沿旧构建路径运行。根后续采用、重构建、精确执行窗口及完整控制交付签收仍待完成；N0 技术未通过。

## 输入及九源身份

产品由固定 ref 的 git show 读取，不采用工作区漂移；全文读取同目录 plan、source-fix-static、SDK 声明证据及精确 patch。逐项实际计算九源 bytes/hash，并对照 b1：只有 core_test 变动，其余八源相同。下表路径保持仓库相对命名便于核固定 ref，不是运行入口。

| 固定源码 | bytes | SHA-256 |
| --- | ---: | --- |
| packages/native-location/include/location_abi.h | 13296 | fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172 |
| packages/native-location/src/capability_core.cc | 17304 | eae2d2dcf4ccf1f648dbec5fdd0424c0a2dac31a94a45d493e819948f2309319 |
| packages/native-location/src/platform_macos.cc | 7675 | 28f9c736e59a24cb050b706628aca26283a513fa3c019fdf58dd14e7d3f8a5be |
| packages/native-location/src/platform_windows.cc | 12506 | bcf474ca9d9e5ce4efdf06284dd71b9504c5e69027d3a53c96fa7df56bc2b4c4 |
| packages/native-location/src/node_binding.cc | 13163 | e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383 |
| apps/desktop/src/main/security/native-location-owner.ts | 12496 | e354b0830469647d70690f3e1d6e567c816f70cbbbe5c211dabba817fa7cc8d0 |
| packages/native-location/tests/location_core_test.cc | 29706 | f1684029430f28918fd4caa062eb8d250f97d5d34aa3ab65c517e44954525037 |
| packages/native-location/tests/location_child_probe.cc | 380 | 041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c |
| tests/unit/i06-native-location-owner.test.ts | 8460 | e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04 |

| 本次辅助输入 | bytes | SHA-256 |
| --- | ---: | --- |
| sdk-rename-declaration-evidence.json | 11375 | 515325e5aef8ff49508db77061230cbf3a905726867549d465d5b88ff684baa9 |
| source-fix-static.json | 2463 | 2eccf89bce35f496c282258c0956f68b7d70cbc67805d3b8f888d0c910af89a4 |
| darwin-exclusive-rename.patch | 545 | af15f1f446df83e345ebcc1905a402794839e529c4380ddfd03ebeb28f62923f |
| plan.md | 5962 | 634b29058c214f592e91ff25777d77f639d9e3499c2232e6cdcc7f62bc43cd96 |

## 无覆盖行为与失败路径

固定 `location_core_test.cc:26` 仅在 `__APPLE__` 分支新增 sys/stdio.h；`:154-156` 保留既有 `path + "-moved"` 目标和固定失败标签，只将普通 rename 换为 renamex_np，flag 恰为 RENAME_EXCL。没有 exists/lstat 预检后普通 rename、错误后降级、重试覆盖或备用目标；精确 diff 仅这一调用与一个 include。

SDK27 本地 rename.2:139-146 表明，在支持该能力的文件系统上，目的已存在时 EXCL 令调用返回 EEXIST。本调用不设置 RENAME_SWAP，不使用会替换目的的普通 rename fallback。目标文件、目录或其他已有名称的具体实际行为仍须在未来获批环境验证，不能仅由本轮文本审查声称故障已实测。

require 对非零返回抛出，`:156` 的 `path=moved` 位于 require 之后。因此在明确的 EEXIST 拒绝路径，fixture 保留原 path，未将他人已有 `-moved` 名称接管为自己的 root。`:158-169` cleanup 仍先在持有 anchor 下 unlink 固定 member/old/alias/link 及 sub，关闭原 anchor，最后只对当前 path 作 rmdir；没有删 moved 的额外分支、glob/prefix 清扫或冲突后的目标目录遍历。所以该失败路径不会因 path 被提前更新而误 rmdir 已有目的目录。

成功时才更新为 moved，使之后正常 cleanup 定位已重命名的自有 fixture。该调用和最终 rmdir 仍按绝对名字进行，不能把整个 fixture 说成 fd-relative，也不能从 held anchor 推出持续源名称身份。成员操作在 held anchor 下和 root 名称操作须继续区分；生产 publish 仍 unsupported。

此分析只关闭“目的已存在仍被覆盖”的具体反例，不签任意 OS 错误都必然无副作用、所有异常都能清理成功、源/目标名称永不被别人替换或强同 UID 抵抗。极端错误/异常后的未知保留仍按原计划停下，不凭 prefix/目录缺席确权或追加清扫。本 diff 没有增加 rollback、耐久、源对象围栏等功能。

## 当前 SDK 声明、类型和宏门

本轮实际直接读取 SDK27 五件原始头/手册，对每件重新计算 bytes/SHA，匹配 sdk-rename-declaration-evidence；另直接读取供方既有 `metadata-optimization/sdk-records.jsonl`，逐项确认五条原记录的 path/realpath/bytes/SHA 与实际五件相符。只做文件审计，没有预处理或探测符号。

| SDK 相对路径 | bytes | SHA-256 |
| --- | ---: | --- |
| usr/include/stdio.h | 3069 | d2220614f42d3cb678ae0de176ba0ab3256e15fb45b3efdb5d17b8ac1f6a4b54 |
| usr/include/_stdio.h | 20526 | 8417242466f6df6890587974393e97bb0aeac8caeb80cdf82a4e03a97e6d4660 |
| usr/include/sys/stdio.h | 2415 | a8078ae1cba1a46a66d0de6fe7f13bbc969cdb7e78fc2d4b9a5c5cdaaf16126b |
| usr/include/sys/cdefs.h | 42609 | ac1a889ee7e6f3025e01be9981d26751489b9e63e926035201cae07ab9e6576f |
| usr/share/man/man2/rename.2 | 11674 | 896c6a278dcfd14601147661cf2a4588d85b271ec8798bbec7913c1d17967033 |

实际 SDK root 为 `/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk`。其 [sys/stdio.h:34](/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include/sys/stdio.h:34) 在 `__DARWIN_C_LEVEL >= __DARWIN_C_FULL` 下定义 RENAME_EXCL=0x00000004；同文件 :43 外层要求 C level >=200809L，:50 再核 full，:52 在 __BEGIN_DECLS/__END_DECLS 内声明 `int renamex_np(const char *, const char *, unsigned int)`，标 macOS10.12+。本调用两个 c_str 是 const char*，flag 类型可传给 unsigned int，没有引入额外 C++ overload/链接名假设。

[sys/cdefs.h:884-893](/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include/sys/cdefs.h:884) 表明 _ANSI_SOURCE 或明确 POSIX-only 选择会收窄 namespace，否则 full；证据中旧编译命令为 C++17、arm64、SDK27、deployment15.0，未显式定义上述收窄宏。__STRICT_ANSI__ 本身不是这段 namespace 选择的 _ANSI_SOURCE。stdio.h:61→_stdio.h:81 已引 sys/stdio.h，旧 depfile 也已列出它；新显式 include 消除用途对间接 include 的依赖，不改变这些条件。

这些事实支持当前记录配置下声明/flag 可见的静态判断，不能证明新 build 的实际宏全集、目标链接符号解析或执行 FS 的 EXCL 支持。若未来工具链改变 POSIX 宏、SDK、部署目标或头集，须重新核，不应通过加手写声明或悄悄回退普通 rename 解决。旧 b657 已有构建/dep 记录仅作为声明闭包参考，不能替新候选生成或认证运行产物；宿主 SDK27、min deployment15 也不等于 macOS15 运行证据。

## 范围与未验

最小 diff 无 Windows 分支/28 条纯文本 static_assert 更动；八件未变源码、ABI 和 Node12 API 不变。没有新增 fixture 接口、进程、管道、网络、生产用途、权限开关或预算。此报告不读取或修改 T03 WIP，只读取主线给定的旧固定供方记录及当前 SDK 文本；不以 metadata 清单认证完整 runtime dependency closure。

实际检查为固定 Git diff/九源 hash、五 SDK 实物与供方原记录比对、声明/手册/失败路径静态核对，以及本新增文档 UTF-8/末行/尾空白/表格/diff 检查。没有预处理、编译（含 syntax-only）、constexpr 求值、测试、产品 import、native load、FS/child 实验、GUI 或新依赖安装；未提交。

新 root 授权采用、重构建和执行均待后续精确窗口。运行时目的已存在、FS 不支持/错误返回、成功 root rename 及 cleanup 结果仍未实测，不借旧产物或源码审查宣称通过，不替根完整控制报告签收。
