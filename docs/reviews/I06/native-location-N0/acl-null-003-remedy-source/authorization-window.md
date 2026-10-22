# I06 ACL-null003精确源码修复窗口

2026-10-22。继续原I06聊天/Goal、原.worktrees/I06-native-location-N0及feature/I06-native-location-N0，从固定3cc158e0a62b154d110a6fc80e3ddf171cea0098接续。总控全文读11272B proposal、7910B独审、8269B真实验证范围及handoff，实际核17个新增文档current/Git/hash和两源旧pin；设计层受限收件，见I06-controller-acl003-design-direct-proof.json。003失败及全部旧原件不动，不创建替代Goal。

## 仅两writer

1. packages/native-location/src/platform_macos.cc：旧8670B/SHA e1fbbcd9c9b73916bd9a030da8bc237dd46230fdd8d0366f0e2424168d4cd71a。仅platform_metadata及同文件必要cleanup/error helper，落实固定proposal同FD fresh filesec→一次fstatx==0→OWNER/GROUP/MODE成功且与同次stat一致→UUID/GRPUUID存在性见证→成功ACL presence查询→明确absence或present有效空ACL。NULL/ENOENT/query valid0单独均非成功；任意ACE拒绝；getter哨兵/未知所有权不贸然free；已知owned ACL只free一次，真实释放失败RETAINED优先，filesec_free void不伪造返回证据。最后才发布原metadata。原type/UID/mode/link/no-follow/identity与owner/关闭义务保持。
2. packages/native-location/tests/location_core_test.cc：旧30037B/SHA 4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319。仅Darwin局部fixture helper和定点正反case源码，含必要membership.h：当前owner UUID仅用同fixture单ACE setup，不输出UUID；按validation-scope的P1/N1、自然可有的P2、原安全门及有限失败输入设计。保Windows28静态断言及所有原case/断言。被测调用失败的非零owner也须依原规则关闭，不能断言abort漏清理。

其他七源、ABI/core/Windows/Node/TS、CMake/driver/lock、限额与001/002/003/旧五轮过程只读。新过程仅docs/reviews/I06/native-location-N0/acl-null-003-remedy-source/。不增加通用runner、故障seam、API框架或第二种路径授权。若准确实现需要第三writer，先给具体路径/原因，不抢写。

## 已采用的有限技术边界

采用的是固定公开Libc实现下的保守absence证据链供本组件源码和后续实测，不是证明本机libSystem同源或跨平台通用合同。已读公开commit71bbe350ab79eef58113991d817ccc6165061a64的推论前提必须保留；见证不足仍UNSUPPORTED，不为正例取绿删门。公开statx内部for/realloc和ACL getter的heap/次数/wall上界仍未知，应用侧固定对象/调用点不代内部硬界；本窗不关闭该限制或任何T01 H/SQLite物理HOLD。

明确批准proposal的非成功错误分类增量：已知ENOMEM→BUDGET、权限→DENIED，其余失败/缺省/不一致→UNSUPPORTED；acl_free/未知拥有释放问题RETAINED优先。fstatx非0均不得成功，保存即时错误；成功遗留errno不作失败或absence依据。安全拒绝/诊断不输出路径/FD/PID/UUID/实际owner或环境；新增固定行≤96B，stdio成本不称零。

## 本阶段验证与后继

先核实际树、最新AGENTS/common、两旧pin与其余七源；修改后固定九源/两writer最小diff。独立agent审全部新决策、短envelope/fresh未填反例、valid非1、失败所有权/清理、原安全回归及Darwin fixture有效性。一次必要正常npm run check和12sources；如既有native addon skip据实保留，这些不编译C++。首失败保原件，不删用例或改期望求绿。

交固定product/process、九源前后pin、完整命令/双流/退出、必要有限manifest/独审及精确新API/fixture验证范围。旧过程只用Git身份冻住，不重审五轮大供应池。

**不授实际ACL setup/查询、FS/OS探针、native产物运行、第六构建或源码后自动重跑003。** 新fixture这时仅写源码。总控核源码后T03另授新输入编译；再按新pair另授精确一次CLI，包含限定的同FD fixture setup/read，才能取得正反实际证据。正例不满足保拒绝和反例，不试环境/提权/改ACL政策。

无GUI/e2e/HMR/凭据/外部模型/付费/push/PR/merge或Goal变更，不扫描删除旧fixture、不杀旧PID。先前平台拒绝的SQLite资源分析继续停止。本窗不关闭003根因、drain、EXCL全路径、目标OS/父N0、同版指定外审/CI/真人/远端门。
