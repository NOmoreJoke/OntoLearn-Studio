# I06 诊断003：精确一次无窗口CLI

2026-10-22。总控已全文读4397B handoff及5912B独审，实际核11项准备current/Git/hash，独立确认六值变化外的全文/AST/tool参数完全相同，新pair指纹吻合。见I06-controller-third-call-six-value-proof.json。现授权**原I06会话**执行以下精确调用一次；不授GUI、Electron、addon、平台验收或产品启用。

## 唯一调用及来源

原树/分支保持；固定准备5b78098ae8b53168fc23ec7499f240d1ede3f1c6，唯一调用为其中docs/reviews/I06/native-location-N0/host-core-run-preparation/diagnostic-third-call/exact-tool-call.preparation.json的arguments。cmd17176B/SHA256 ed84b73de7178ba8340843ed54b63d6cf45e6f683074833ad1f4a356df3aede3；stdin16976B/SHA256 a67944783c48d1fb0e888d1ce6991665873881a482a91a6673c979425c8c07d1。workdir为原I06树、login=false、yield_time_ms=1000、max_output_tokens=1000，不自行拼接或加wrapper/env/timeout。

record I06-N0-execution-003-0d5223985fcd9761由本窗口取得一次许可；准备中的PREPARATION_ONLY保历史。仅新execution-003目录，存在即停；001/002不复用、不移动删除。真实来源I06 fc9853/6fda，T03固定0514d37e32e31ae569e583bb56ec225ebc0483e6/过程8528ccb3d68de4f31ee1e10bd984084e0f7f418c，digest0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb。路径只用固定CORE_PIN/PROBE_PIN：core344096B/65cca109ce2a43b24c94fc013b5e91127548d4be3d39de5330024128ffdb8039，probe34120B/12d355d3cc43fc5c39b6e8689d7e0dabb6909b8dfd7a7deed6322f3351d80e48。T03冻结不并发替换。

raw result.sourceRef=b592继续保留为历史模板字段，不能充本次真实provenance；本窗口、完整cmd/固定准备、新pair及预后核对另绑定实际新来源，不改raw求表面一致。新stage/errno只按本轮实际stderr解释，不能追认001同分支或用metadata case label推断已进platform_metadata。

## 原边界保持

仅现有exec_command一次dispatch；若返回session，跟踪同一个session到终态，不重复提交。独立清环境-I/-S Python私有CLI，不在REPL/嵌入进程fork或起线程；CHLD/取消handler/空mask及core preexec只影响新私有父子，不改tool host/现有shell/系统/全UID。原单Popen、/dev/null、0600双流、六项env/newsession/close_fds、exact waitpid及ECHILD未知语义不变。

原NOFILE64/CPU12/各流FSIZE1MiB/CORE0，receipt后15秒；超时/取消只对仍未reap且身份成立的本次进程一次TERM→1秒不reap→KILL→2秒收自身leader，20秒仅逻辑控制票。三控制记录各64KiB/总256KiB，前后每pass产物合2MiB，原双流各1MiB；无通用runner、第二次cleanup、额外FS/OS探针或扫描/tmp。旧drain/fixture/PID未知保持，不因新目录或leader退出签自然EOF、释放旧票或删未知残留。

平台/权限拒绝、前门不匹配或真实失败均保原件并停止；不自动重试、第六构建、改入口/提权或扩大清理。此CLI不授GUI API，也不保证绝无OS自动notice，不改通知/崩溃设置。严禁顺带重启已被平台拒绝的SQLite/资源接口分析。

## 交付

执行前保存本窗口原字节和真实意图；保唯一工具终态/可能session、003 intent/postflight/result/原双流及固定来源/cmd/pair/准备身份，独立有限manifest与hash。缺失/未知据实记录，不补写或以控制退出0充全部native通过。独立agent只审实际新结果/范围后交root；不再重审原算法或旧五轮大包。

不改源码/旧准备/001/002/五轮构建或Goal，无push/PR/merge。即使本轮成功，也仅有限单宿主case；具体根因、EXCL、Mac15/Win11、完整N0/父功能、同版指定双外审/CI/真人/远端门按实际结果分别判断。
