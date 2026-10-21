# Windows probe CLI P3 独立定点静态审查

2026-10-22（Asia/Shanghai）。受审固定完整 ref：`1b025562b1011155e07130175fdadc522185453e`，工作树 `.worktrees/I06-native-location-N0`。仅审 `packages/native-location/tests/location_core_test.cc` 新增路径文本 helper、15 条 static_assert 源码及 Windows probe 的前置调用顺序，不重开完整 N0 平台审查。

结论：原 `C:probe.exe` 被误收为绝对 artifact 的 **P3 在源码层已修正**；未发现本 diff 新增确定 P1/P2、越界读取或明显 C++17 构造错误。但若承诺“普通合法 artifact 拼写，拒 device/模糊组件”，DOS reserved basename 仍未过滤，保留下述同级 P3 文本合同建议，不能无条件宣布全部 device 歧义已关闭。未执行任何断言、编译或目标平台验证，N0 技术仍未通过；主控制独审交付尚未由本报告替代签署。

## 固定输入与范围

| 输入 | bytes | SHA-256 |
| --- | ---: | --- |
| 固定 ref 的 location_core_test.cc | 27166 | f2749e61c2455073f58d1e33d9088dd4966f1d2250947c207087b6b8caa20dc4 |
| cli-path-P3/source-static-check.json | 15375 | a12a996556df011aecc11da73d096540f604847f5ca78c04600aafdf96d0d281 |
| cli-path-P3/root-finding-and-disposition.md | 2964 | 99c703e177958afb114cd47a863987ebf6afdbe18fd3070bf0cce6d933ab54af |

产品均从固定 ref 用 git show 读取；另外全文读取上述作者意见/清单。实际逐项计算原 40 件固定 ref bytes/hash，并对照 `ff0b6ccb8541ef0dc6fef3865ca8ccde71809bca`：除明确授权变更的 core_test 外，其余 39 件相同；九件源码均与新清单匹配。相对原源码 `fa1a7e4155f3afee4a1b3409f9ab8804cc620186`，原九源只有 core_test 改动。八件未变源码、ABI header、Node 12 API 的事实不由本 CLI 小修改变。

原 P3 是测试 CLI 精度：旧 guard 只检查第二字符冒号，未要求盘符后的根分隔符；不是已观测运行漏洞，也不是 mac/core 阻断。本报告没有把可信 T03 TARGET_FILE 输入变成任意路径执行授权，且未读取/采用 T03 WIP。

## 原 P3 与路径 grammar

固定源 `location_core_test.cc:49-76` 的 helper 只接受两个根分支：ASCII 字母加冒号加分隔符，或两个反斜杠开头的普通 UNC。drive 分支从 index 3 开始要求至少一个非空组件，因此盘符当前目录 `C:`、盘符相对 `C:probe.exe`、非字母盘符和 current-drive rooted 拼写不能通过。drive 同时接受反斜杠和 CMake 常用正斜杠；没有把 `C:/` 本身当非空 artifact。

UNC 从 index 2 切分，至少三个非空组件，即 server/share/artifact。仅在普通反斜杠 separator 下接受 UNC，不容空 server、空 share、缺 artifact、重复分隔符或末尾分隔符。extended/device prefix 中问号受字符过滤，点组件受尾点过滤，因此所列 `\\?\C:` 与 `\\.\pipe` 反例无法通过。组件内冒号/引号/尖括号/pipe/通配/ASCII 控制符被拒，冒号只允许在前缀 drive 位置，ADS 反例不能借根 drive 的冒号例外通过。当前目录/父目录组件以点结尾，被同一规则拒绝；所有组件尾点或空格同样拒绝。

这些是有界 CLI 文本合同，不能据此认定文件存在、是 PE executable、身份正确、来自 T03 artifact 或获得执行权限。普通 UNC 拼写获准不代表本轮授予网络路径读取/执行，未来构建和运行输入仍须单独固定。

## 残余 P3：DOS reserved basename 未过滤

位置：`location_core_test.cc:62-75`。当前只过滤非法字符、空组件与尾点/空格，没有识别保留设备 basename。按源码分支推演，`C:\NUL.exe`、`C:\CON`、`C:\artifacts\com1.exe` 都不含被禁字符，也符合根和组件计数，会被文本 guard 接纳。官方还列 COM/LPT 的上标 ¹、²、³ 变体；同类拼写也没有被当前比较覆盖。

[Microsoft 官方 Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file) 明确保留 CON/PRN/AUX/NUL、COM1–9、LPT1–9 及上标数字变体，并指出保留名后加扩展名仍是设备别名。仅拒两种显式 namespace prefix，不能推出所有保留设备名称已拒。这与 fixture 的“普通 artifact”文字合同有差距，但不构成已证设备成功运行或正文访问；本报告未调用 CreateProcess 或任何文件 API 来验证其实际错误。

建议在同文件 bounded constexpr 组件判定中，对文件/目录组件首个点之前的 basename 作 ASCII 大小写无关保留名检查，明确支持官方列出的上标 1–3；至少补 NUL.exe、CON、混合大小写 COM1.exe、LPT 上标带扩展负例，并用 NUL-data.exe/COM10.exe 这样的非保留名字防止前缀误拒。普通 UNC 的 server/share 属命名根而非普通文件 basename，应明确是否采用更保守统一拒绝或仅对其后文件/目录组件应用，不能暗称两类语义完全相同。无需扩大到全套 Windows 名称解析器或任何 DLP/任意同 UID 对抗。

本项是 P3 小修建议，已及时回传唯一作者；保持 `1b02556` 原固定字节，后续如采用应另给新 ref 定点复核，不回写本报告为新候选通过。

## 边界读取与 C++17 静态可行性

`location_core_test.cc:50-53` 先判 null，再以最多 1024 wchar 扫描。真实 caller 提供 `wchar_t target[1024]{}`，MultiByteToWideChar 使用 -1 输入长度，成功表示包含终止符且装入同一缓冲；字面量也均是终止的真实数组。该 helper 不是带独立 buffer-size 的通用 C ABI，不能安全接任意无效地址或小于约定长度且不终止的外部数组，当前没有这样的调用点。

长度小于 4 或达到 1024 即返回，故随后 path[0..2] 在有效终止数组内。组件循环只在 `i < length` 时读内容字符；`i == length` 的分支依靠终止边界处理最后组件。`count==0` 的逻辑或短路发生在 path[i-1] 前，排除空组件时的倒退读取；非空时 i 大于 start，index i-1 有效。length 最大 1023，最后 start/i 的递增不产生无符号溢出。未见当前数组调用范围内 OOB 的具体反例。

helper 使用初始化局部整数、while/for、条件/短路、无捕获 constexpr lambda 与普通索引比较，均属于 C++17 能表达的 constexpr 函数写法；size_t 来自现有 ABI 头的 stddef.h。没有动态分配、虚调用、OS API、异常或新增库符号。放在平台宏之外意味着各目标 TU 都会解析这些纯文本源码，字符比较只涉及共同宽字面字符/整数，未依赖 wchar_t 必须恰为 16-bit。以上是语言构造静态审查，不是 C++ parser/syntax-only 或 constexpr 求值成功证据；正式编译器和 SDK 仍待 T03 固定。

## 15 条反例与调用顺序

源码 `location_core_test.cc:77-91` 保持三正十二负：drive-rooted、CMake drive-rooted、普通 UNC；drive-relative、仅盘符、非字母盘符、单根分隔符、相对名、UNC 缺 artifact、UNC 空 share、extended prefix、device prefix、父段、ADS、尾点。逐条文字与分支条件相符，没有发现反例标签与输入语义相反；但它们没有覆盖上述 DOS reserved basename，不能把既定 15 条称全 Windows 名称矩阵。本轮没有编译、求值或用脚本复刻执行 helper/断言。

真实 Windows probe `location_core_test.cc:287-292` 先 UTF-8→UTF-16 成功，再用短路与调用新 guard，最后才 CreatePipe。UTF 转换是已有 Win32 调用，新 helper 本身没有 OS dispatch；转换失败/guard 失败会由 require 抛出，管道和子进程字段仍是初始化空值。后续 CreateProcessW 仍接显式 target 和固定参数；handle-list、继承、sole-reaper、owner cleanup、预算与 production unsupported 都没有改动。此 diff 未新增 OS 调用、环境开关或权限能力。

## 检查与未验

实际完成固定 Git diff/源码读取、manifest bytes/hash 比对及本新增文档 UTF-8/换行/空白检查。没有 C++ 编译（含 syntax-only）、static_assert 求值、测试、产品 import、native load、FS/child 实验、GUI、Keychain、工具依赖安装或 T03 WIP 采用；未提交。目标 Windows/macOS 的编译、链接、运行和故障原门均保持，原 fa1/ff0 的冻结证据不被本新测试 hash 替换。
