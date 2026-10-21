# EXCL fixture 新输入唯一第三次 core 构建

本次构建成功，状态 **built-unverified / NOT_RUN**。两个新产物冻结；EXCL 文件系统行为、目标 OS、运行时、addon 及完整 N0 验收均未通过本次构建代证。

真实授权 a5849a47abadee1e27cae1270bbbd213f3e1c0aa；单文件采用 e4dc6ec726481f6b966cd82344ccdc4975591e46；锁产品 4e4af36de8353fd72f9c43c14001992a1e936060；固定新输入 15163b380035a3b402d5dbb485ab6d3d05e4e559。来源 I06 产品 b59239f9c1ec2774c7922f95dfc67db4dc8754e8／过程 e0d053b40d25e8b3b4cad135088f4b552a6108c0。仅 core_test 29706B／f1684029430f28918fd4caa062eb8d250f97d5d34aa3ab65c517e44954525037 按 Git 原字节采用；另外八源逐字等旧 b1c。锁实际仅六叶字段，CMake f2b552 与 driver ca4ef930 冻结。构建前独审通过，完整12及过程31项含self索引字节核同后固定输入。

只执行一次原 CLI `/usr/local/bin/node scripts/build-native-location.mjs --target darwin-arm64 --component core --build`，真实 driverExit 0，最终 supplier-log.0065 的13条命令均 status0／有真实PID，firstFailure null。Node 与 CMake 两门各完成42772实体核验；configure／try_compile 编译链接及两个目标构建完成。此为源变更的新输入构建，不是旧输入重试；没有第四次构建或任何产物运行。

独占目录 `build/native-location/n0/darwin-arm64/227052c230da782ca62c20600e418f52e938378bd92f2961d7543f03ac43551c/core`。旧两轮目录、超时、检查输出初始化失败、费用与原件全部保留。

| 新冻结产物 | bytes | SHA-256 |
| --- | ---: | --- |
| location_core_test | 343904 | 229faf9fcf15ccbbc9e0e8fefefb1c91c016fc2ea6fea2df92998392e14e812b |
| location_child_probe | 34120 | be916e5252b21e6671c6bd2f32301f8581c1b32ce87f78a4a7b0f8314fb2a6b2 |

新10次 file／otool／nm 实际只读调用均0，语义输出名大小写折叠后唯一，静态检查前后产物pin不变。两产物为Mach-O arm64，minos15.0／SDK27.0，导入libc++／libSystem、loader dyld、无rpath。core的nm undefined从 `_rename` 精确变为 `_renamex_np`，symbol table将后者标注from libSystem；结合实际链接exit0是新符号的静态链接解析证据，不能代替运行时加载或EXCL行为测试。core仍有11个 `_nl_*` 外部符号。

本次四depfile仍1798 tokens／877唯一归一化路径，对上次实际dep的新增／删除路径均为空。显式新增的sys/stdio.h此前已在真实依赖及固定SDK pin中（2415B／a8078ae1cba1a46a66d0de6fe7f13bbc969cdb7e78fc2d4b9a5c5cdaaf16126b），因此后验差异核不需读任何新供应记录或做42772全映射：5项当前source b592、870项既有direct witness、2项旧SDK alias catalog，未匹配0。

仅对既有pthread.h／sched.h两处执行lstat/readlink/stat：linkname、词法目标与followed regular inode/device/size均吻合原清单及已批准常规目标；后验检查未重hash或读取header内容。当前alias身份有只读观测，编译器实际open轨迹仍未独立观测。四compile argv、两link-driver命令、四显式object pin均存档；最终selected stub／archive/member／嵌入第三方与runtime闭包继续PENDING，不增加trace或重构建。

本轮外部构建目录144文件／3020856B全pin，92份原始driver流/快照、17份生成证据按字节副本保留；二进制和object留原位，不进Git。差异collector实际只调用一次并exit0，原stdout/stderr与PID/时间回执保留。前置纯文本检查曾拒绝一次不必要的内存转义变换（SyntaxError，在写collector文件/dispatch前），用原始正确脚本通过纯解析例后才首次执行；另有最初metadata算式多5000的assertion，亦在plan写入/采用/构建前更正。两者见各correction记录，未掩作构建或实际collector子进程失败。

累计账见read-account：64GiB下构建声明55068578800B，余13650897936B；实体保守256632/300000；metadata含有限收尾预留1313343/1500000。旧1100000超255及1100287关闭决定保留，原供应9745727085B独账不重置；声明／应用读预算不代表实际OS/compiler/loader IO或性能测量。未用预留未自行释放。

本轮不授运行、不新增产品runner；原I06后续需凭新pins，在独立精确CLI运行窗口及既有executor控制核实后执行。未做GUI/凭据/模型/付费/push/PR/merge/Goal变更，双外审、目标OS/真人、CI及父功能验收保留。

全量Git whitespace实检exit2：仅原始generated的62处／7文件诊断按精确path/line保留，filtered检查exit0，不修剪原件、不声称全量0。最终交付须另做Git index与当前manifest逐字节闭包。

结果独审9092B／9bba3aed3d2439cc82766997a29c21dbe571a0fb8f0a076bb91905609bdb7fbc已全文读取，未见新增归档阻塞；独审辅助核对曾误假定link row有path字段而KeyError，按target补核既存link.txt，未重hash产物或重跑大解析，原事实保在报告。独审宽访问上界10000／预付15000、应用读<10MiB／预算12MiB，未自行释放剩余预留。

首次最终索引实检0差异，但显示scope标签沿用上轮旧名；实际assert前缀已是本目录。现仅更正显示字符串，旧清单快照及更正receipt保留，并对修改后的最终清单重新实检；不改验证逻辑或产品。
