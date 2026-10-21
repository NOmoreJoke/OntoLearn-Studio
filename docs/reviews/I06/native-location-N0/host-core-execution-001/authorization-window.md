# I06 N0：精确一次无窗口宿主 CLI 执行窗口

2026-10-22。总控已全文读具体调用、API依据、交接/定点独审及根最终独审11562B/SHA256 `d1583ae5f2b5da52280a0aa40c0a8d17deb2b86144a060757f8134a92add4b2e`，并自行用纯JSON/AST确认精确副本只有三项赋值变化、其余逻辑/参数不变。现明确批准原I06会话执行以下**唯一一次**调用。该批准只适用当前无GUI的原生CLI单元case，不授Electron、可见原生故障、addon、目标平台或产品启用。

## 固定完整调用

I06树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，固定准备ref `b942e12cd122873109f4bd16d51e06e05ad7005d`。唯一输入为其 `docs/reviews/I06/native-location-N0/host-core-run-preparation/concrete-call/exact-tool-call.preparation.json` 的 `arguments`；必须按固定Git字节读取并核对，不执行原None版本，也不另拼调用。

完整cmd：17176B/SHA256 `2428cac0cbfa5cf9bf8906e0e1800e776b865408eece1950ff1f0029884921a6`。其余参数精确为workdir=上述I06树、login=false、yield_time_ms=1000、max_output_tokens=1000。通过现有exec_command执行一次并持续跟踪返回的唯一session，不重复提交。不增加外层timeout、wrapper、环境、线程或源代码。记录标识 `I06-N0-execution-001-227052c230da782c` 此刻由本窗口取得运行许可；副本历史NOT_GRANTED原文不改写。

新pair只取T03已收件输入15163/过程113e、digest `227052c230da782ca62c20600e418f52e938378bd92f2961d7543f03ac43551c` 的core/artifacts两个绝对路径：core343904B/SHA256 `229faf9fcf15ccbbc9e0e8fefefb1c91c016fc2ea6fea2df92998392e14e812b`，probe34120B/SHA256 `be916e5252b21e6671c6bd2f32301f8581c1b32ce87f78a4a7b0f8314fb2a6b2`。原T03已确认冻结，不并发替换。执行前后由本调用精确核实物，不另遍历供应/构建目录。

## 执行条件与边界

认可已读本地Xcode3.9.6配置/wrapper及同版官方CPython实现作为本次静态API依据，非内核flags实测。调用以清环境的全新独立 `-I -S` CLI运行，不在REPL/嵌入进程中fork、不启动线程或附加原生agent、无外部reaper。接受其仅在这个新私有父进程设置CHLD默认/取消handler/空mask的必要细化；core preexec重复默认信号/空mask与limits。不得修改tool host、现存shell、系统或全UID设置。自检条件不符即停止，不加探针找替代方式。

原调用一处Popen、显式/dev/null与0600独占双流、替换六项env/newsession/close_fds、exact waitpid及ECHILD未知、NOFILE64/CPU12/FSIZE各流1MiB/CORE0均保持。receipt后15秒等待，超时/取消只在仍有未reap身份时一次TERM→1秒不reap→KILL→2秒只收自身leader。20秒仅逻辑控制预算；构造握手、文件/系统调用无硬wall截止，不补通用runner或第二次cleanup。

三控制记录各64KiB、总闸256KiB；前后两产物每pass合计2MiB，原双流各1MiB。原raw不截断/合并/过滤，工具摘要不能代原件。控制退出、core原始退出、较早JSON快照与最终取消须分别记录；未知后代/fixture/native drain不凭kill或目录缺席变通过，不glob扫描/清理/tmp。

这是有限组件运行，不是容量/RSS硬保证、完整N0、Mac15/Win11或全部FS路径验收；不声称绝无OS自动notice。不操作任何GUI、不改通知/崩溃设置。平台拒绝、权限拒绝、preflight失败或运行失败均保原件并停止，不重试、换入口、提权、重构建或扩大清理。

## 原件收口

先将本窗口原字节保存到新执行过程，记录批准来源与真实dispatch意图，然后仅上述调用。保唯一tool session、完整工具终态，以及execution-001的intent/postflight/result和两个原始流；部分写或未知状态按实际缺失记录，不能补造。保存有限manifest及实际源/pair/cmd/版本身份，由独立agent只读复核真实结果再交根。不改九源码/旧准备/三轮构建或现有Goal，不push/PR/merge。后续任何再次运行需根依据实际新情况另授，本窗口不能复用。
