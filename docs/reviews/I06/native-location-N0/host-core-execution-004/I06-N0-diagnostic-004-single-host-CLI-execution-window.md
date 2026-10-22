# I06 ACL 修复004：精确一次CLI执行窗口

2026-10-22。总控全文读取5838B handoff和7976B独立窄审，实际核对固定准备10文件69108B、六值以外完整cmd/AST/非cmd参数相等，以及新pair实物指纹。证明见I06-controller-fourth-call-six-value-proof.json。现授权原I06会话在原树执行固定调用一次，限组件测试；不授GUI、addon、产品启用或平台验收。

## 唯一调用与来源

固定准备e85ae88815e45aa336850b594910a524a073cc00，父9509d02790f9a79905371c5183be16cab99f5114。唯一工具参数为该ref中docs/reviews/I06/native-location-N0/host-core-run-preparation/diagnostic-fourth-call/exact-tool-call.preparation.json的arguments，不自行拼接、加wrapper、改变环境或timeout。

调用JSON19614B/SHA256 8f9788b64b721ad60a8a1c5bf4a72287dd2519d6fcdedc82f5b681e1a8adb739；cmd17176B/100ebd1ae0a8f43608146565b95d145503e014b87beaccb53182fbc5115d8781；stdin16976B/5a3fb0e4b6e273ca20c76f7ddb0567fcd0f2ce75baed151722e6b7dbebd7db92。原I06绝对workdir、login=false、yield_time_ms=1000、max_output_tokens=1000保持。record I06-N0-execution-004-1526093e58aeaa43取得本窗口的一次许可；准备中NOT_RUN保历史。

真实来源I06产品1217e0f63a9c62b72e01046ef5fbc5c53434251a/过程9509d02790f9a79905371c5183be16cab99f5114；T03输入bfe137f371361f9fda446d5cbe6b3079c5433ee5/过程37fe056e5d1716a10237de20f79042db54aa0549；digest1526093e58aeaa43cd5c96dfc911dd032759df27c039bf3d11eacfb1e6cbfd50。只用固定CORE_PIN/PROBE_PIN绝对路径：core362656B/17fb8b48ec3e79cfd36015edc4047bbd390ac0145dd2c40b1c20850455771f60；probe34120B/5b9978c2e7bbb8d3ee51d3d94d95ab4797ac01337654180cf121d89dc3e05b98。T03继续冻结，不作第七次构建。

raw result.sourceRef=b59239f9c1ec2774c7922f95dfc67db4dc8754e8仍仅历史模板字段，不改写。另绑定本窗口、真实refs/digest/pair、准备ref/cmd和预后核对；不以raw字段当新来源。

## 此次新增Darwin fixture授权

仅固定新core中的三个新fixture及其后原case，每个持有自身anchor，原构造器empty-ACL setup和自身清理允许。无旧路径扫描、系统ACL或用户权限调整。

1. empty：同FD一次独立fresh filesec/fstatx及OWNER/GROUP/MODE一致安全门、UUID/GRPUUID和ACL presence query；present时独立ACL copy/valid/FIRST及必要NEXT。随后一次owner create、root公开metadata核验、显式close/cleanup，输出固定布尔行。只有absent_observed=1算P1明确absence；自然present-empty只算P2，不强造另一表征或删门求绿。
2. one-ACE：当前owner一次mbr_uid_to_uuid仅作qualifier；acl_init/create_entry、ALLOW、ACL_LIST_DIRECTORY最小权限及零flags、valid、同FD set/free。独立见证必须present且恰一有效ACE，再一次owner create预期DENIED。任何非零失败owner先close后断言。setup/query失败为无效测试，不能算DENIED成功；不输出UUID/FD/owner身份。
3. invalid-FD：只把自身input副本borrowed_directory设为-1，一次owner create、失败owner关闭及自身清理。仅覆盖duplicate输入门，不能称覆盖fstatx/property内部失败。随后原metadata/child/partial/concurrency/budget和原child probe保持。

这些是应用调用范围；公开Libc不是installed身份，案例不关闭allocator/query/get/free故障、fresh未填、短envelope、未知ownership或内部heap/系统调用/wall硬界。stdio成本不记零。

## 原控制边界与停止条件

仅exec_command一次dispatch；返回session时只跟踪同一session终态，不重复提交。独立清环境-I/-S Python私有CLI，六项env、单Popen、newsession/close_fds、/dev/null及0600双流、exact waitpid/ECHILD未知语义保持。CHLD/取消handler/空mask及子preexec只影响新私有父子，不改工具host、既有shell或系统/全UID。

NOFILE64、CPU12、各流FSIZE1MiB、CORE0；receipt后15秒；超时/取消仅对尚未reap且身份成立的本次进程TERM→1秒不reap→KILL→2秒收自身leader。20秒仅逻辑票，不称硬wall。三控制记录各64KiB/总256KiB、前后每pass pair合2MiB、双流各1MiB不变。仅新execution-004，存在即停；001/002/003不复用、不移动删除，不扫描/tmp、不处理旧fixture/未知PID。

平台/权限拒绝、前门不匹配、真实失败均保存原件停止。不得重试、重编译、改入口/环境、提权、扩大清理或调用额外探针。先前被平台拒绝的SQLite/资源接口分析继续停止，T01损坏输入保护HOLD不变。

## 交付与边界

执行前保存本窗口原字节；保唯一工具终态/可能session、004 intent/postflight/result/原双流和真实来源/cmd/pair/准备身份，有限独立manifest/hash。缺失和未知据实保留，控制退出0不等于native全部通过。独立agent仅审本次新结果/范围，原算法和历史构建不重新大审，交root核验后停止。

不改源码、旧准备、旧运行/构建、Goal；无push/PR/merge。003仍为失败归档。leader已收或输出稳定不证明自然EOF/全部后代drain，旧未知不释放。004即使成功也仅单宿主有限case；EXCL、Mac15/Win11、完整N0/父功能、指定双外审同版通过、CI/真人/远端合并门分别保留。
