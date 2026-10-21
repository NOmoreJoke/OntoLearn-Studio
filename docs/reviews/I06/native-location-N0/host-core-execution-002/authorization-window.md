# I06 诊断002：精确一次无窗口 CLI

2026-10-22。总控已全文读新handoff和6640B独审 `96e8732ca8655cf2538a0fcf5eb7ec05462ad1a75813dc7eb3c92563d85fbdab`，自行逐字/AST确认六位置增量及其余文本、算法、tool参数完全保持，15项准备current/Git/hash闭包通过。详见同目录 `I06-controller-second-call-six-value-proof.json`。现仅批准原I06会话执行下述调用**一次**，不授GUI、Electron、addon、平台验收或产品启用。

## 唯一固定调用与来源

原树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`；固定准备 `1151b8d03cd381100bfc1b1804d3927110621f51`，只读取其 `docs/reviews/I06/native-location-N0/host-core-run-preparation/diagnostic-second-call/exact-tool-call.preparation.json` 的arguments执行。cmd17176B/SHA256 `be0d1fc7518e281353206ec25e43f579dba9821035b46ee3161e76aac7fc2705`，stdin16976B/SHA256 `9f6f4b99b63aab6be937617aab7c9dad605a5ab5a54a1b54cfc6c33621d4c2a2`。其余workdir为原I06树、login=false、yield_time_ms=1000、max_output_tokens=1000，不自行拼cmd或加wrapper/env/timeout。

record `I06-N0-execution-002-a0e724fdf90afa98` 由本窗口此刻取得许可；固定准备中的PREPARATION_ONLY原文保持历史。独占execution-002目录，存在即停；不得复用、删除或移动旧execution-001。六位置仅三赋值与RUN/mkdir/open三目录字符串，其余控制算法沿已收件原版本。

真实新源为I06 `fc6237e8cad1a4043d46a1c7198439f1da06ad67`，T03输入d98b503ebe9c477d30d0f36d831cffbeeaf2a988/过程d51a0555e6feb062fc935173222cc142687901a5，digest a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77。core343920B/d4f5ca322146d9696860a74de4bee2ad27866a2223340669898fb82cbbfeb817、probe34120B/21928ca2b5570055fad4bebcd81fcb658016ca9a738294397a83056b662b87e8；路径只取固定CORE_PIN/PROBE_PIN。T03已冻结，不并发替换。cmd中旧result.sourceRef=b592是明确保留的历史模板字段，不能代表本次真实来源；本窗口、新pair预后实物pin与完整cmd/准备ref共同绑定本次结果，交接须同时保留此来源边界，不修改raw结果求表面一致。

## 原执行边界保持

仅现有exec_command一次dispatch，持续跟踪同一session到终态，不重复提交。仍为清环境独立-I/-S Python私有CLI，不在REPL/嵌入进程fork或起线程。CHLD默认、取消handler/空mask只限新私有父进程与其core preexec，不改现存shell/tool host/系统/全UID。原一处Popen、/dev/null、0600双流、六项env/newsession/close_fds、exact waitpid及ECHILD未知语义保持。

NOFILE64/CPU12/各流FSIZE1MiB/CORE0；receipt后15秒，超时/取消仅仍有未reap身份才一次TERM→1秒不reap→KILL→2秒收自身leader。20秒是逻辑控制票，不冒硬wall截止。三控制记录各64KiB/总256KiB，前后每pass产物合2MiB，原双流各1MiB。无通用runner、第二次cleanup或额外FS探针。旧001未知drain/残留不释放、不据新目录或进程结束签自然EOF。不得glob扫描、清理/tmp或杀未知旧PID。

实际新诊断case/status/owner_nonzero只能据本次原stderr解释；失败保原件并停止，不自动重试、第五构建、改入口/提权或扩大清理。平台/权限拒绝或preflight失败同样停止，不绕过。此CLI无GUI API许可，但不声称绝无OS自动notice，不改通知/崩溃设置。

## 交付

执行前保存本窗口原字节及真实dispatch意图。保唯一session和完整工具终态、002 intent/postflight/result/两原始流、固定新来源与cmd/pair/candidate身份，独立小manifest及原件hash。未知或缺失按实际记录，不倒填，不把控制退出0当全部原生验收通过。由独立agent只读核真实新结果再交root。

不改源码、旧准备/001/四轮构建或Goal；不push/PR/merge。成功仅有限单宿主组件case，首次根因、EXCL全路径、Mac15/Win11、完整N0/父功能、同版指定双外审/CI/真人/远端门按实际新结果分别判断，不能整体追认。
