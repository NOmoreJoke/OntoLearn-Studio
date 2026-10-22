# 本次源码与后继真实验收边界

本窗口只落实两源，未执行下面的C++、ACL或fixture API。正常npm check覆盖前端、TypeScript和Python；不编译C++，缺少显式native addon时仍应skip。以下调用数量是应用源码调用点和条件路径，不是libSystem内部syscall、heap、wall硬上界，也不是实际调用记录。

## 生产metadata路径

仅同一原held FD：fresh filesec_init一次；fstatx_np一次，返回必须等于0；OWNER/GROUP/MODE各get一次并与同次stat一致；保原type、geteuid、mode、link检查；UUID、GRPUUID及ACL各query一次，存在位用非零判断。UUID值不用于授权或输出。

ACL absent只有完整前置见证成立才候选成功。present时get一次独立副本，真实owned指针才acl_valid一次；valid后acl_get_entry(FIRST)一次，仅-1/EINVAL为空。任何ACE仍DENIED；无效ACL或其他entry读取结果沿原策略拒绝，不改为成功。成功调用的残留errno不作absence/失败判据。

新API失败立即保存errno：ENOMEM为BUDGET，EACCES/EPERM为DENIED，其余失败、缺省或不一致为UNSUPPORTED。getter成功的NULL/移除哨兵不作空ACL，哨兵不传给ACL函数；getter失败却产生真实非空指针视未知所有权，RETAINED且不贸然free。已知独立副本只acl_free一次，失败RETAINED优先；filesec_free为void，只调用一次，不制造可检测返回值。只有收尾通过才写原metadata。

这是固定公开Libc commit 71bbe350ab79eef58113991d817ccc6165061a64下的保守推论。必需属性排除fresh未填、UUID/GRPUUID排除短envelope，但不证明本机libSystem版本或普适合同。见证不足保持拒绝。

## Darwin fixture源码

仅CLI main在原case前调用darwin_acl_cases。Windows源码块、28条static_assert、原case/断言及Node fixture bootstrap均逐字保持；新helpers虽可被Darwin addon编译，不由其bootstrap执行。

三个新fixture分别独占自己的anchor，使用原构造器一次empty-ACL setup及原清理方法；无扫描、旧路径操作或全局权限修改。

1. empty：同anchor独立read_acl_fixture一次。该helper一次fresh filesec/fstatx，三个标量getter和三个presence query；若present则一次独立ACL getter/valid/FIRST，若确有首entry再NEXT一次。必须标量安全且一致、完整envelope、无entry，否则测试失败。owner创建一次，比较公开ABI/kind、identity按既有小端编码、link_count、acl_checked/held_object_only；没有新增UID/mode ABI。显式owner close和fixture cleanup后输出presence。absent_observed=1才有P1实际absence证据；present且empty自然出现才覆盖P2，不能把同一次表征写成两个正例。
2. one-ace：mbr_uid_to_uuid(geteuid())一次，仅构造本fixture当前owner的qualifier，不输出UUID。acl_init(1)、acl_create_entry、ALLOW tag、qualifier、permset get/clear/add ACL_LIST_DIRECTORY/set、flagset get/clear/set、acl_valid及同anchor acl_set_fd_np各一次，已知ACL副本一次free。随后read_acl_fixture一次，必须present且只有一条有效ACE；setup或查询失败是无效测试，不算DENIED通过。被测owner创建一次，任何非零owner在状态断言前close一次；必须DENIED，清理后输出固定status/布尔。
3. invalid-fd：只在自己的input副本置borrowed_directory=-1，真实fixture FD保持用于清理；被测创建一次，任何非零owner先close，再断言INVALID。该失败位于duplicate输入门，明确不覆盖fstatx/property内部错误。

新guard在异常展开时关闭非零owner/已知ACL副本；显式关闭失败不重试，而保留失败并停止。filesec_free不虚构检查值；未知ACL指针不free。固定诊断/证明行不含路径、FD、PID、UUID、owner身份或环境，保守最长71B（含换行，int按11字节），仍有stdio成本。

## 尚未取得的证据

本轮没有C++编译/链接、实际ACL setup/read、正反fixture或native产物执行。fstatx非0、query/get失败、fresh未填、短envelope、valid位非1、allocator/free失败及异常输出所有权只作静态审查；未注入故障、未声称运行覆盖。原case保持不等于原安全门所有分支已经实际覆盖。

源码收件后，T03需另授新输入编译并固定新pair；再另授包含上述定点setup/read的精确一次CLI。旧第五pair没有本remedy，不能验证它；不自动重跑003，不沿用旧pair证明修复。若正例见证不成立，保原件和拒绝，不改环境、提权或删门。

003失败、001/002未知、旧fixture/后代/drain、EXCL全路径、Mac15/Win11、父N0、同版指定外审/CI/真人/远端门，以及公开statx内部for/realloc和ACL转换资源上界未知，全部保持。本窗没有解除T01 H/SQLite物理HOLD或重启被拒分析线。
