# N0 host core执行准备：独立静态审查

2026-10-22。结论：**固定b592准备合同可供根继续审议，但有一项应补的信号继承P2；当前不具备run-ready或执行批准。** 源码无覆盖rename微修静态符合用途、预算未增。新artifact/used闭包、精确现有executor、安静环境及根一次窗口仍缺；resolved argv为null，应继续不dispatch。

## 1. 固定身份与实际动作

受审ref：`b59239f9c1ec2774c7922f95dfc67db4dc8754e8`。前一预算源码ref：`b1c54c3de840e657aba07906587681f6415085d6`。只读取固定Git blobs，不读取根正在修改的signal工作区文案。

| 输入 | bytes | SHA256 |
| --- | ---: | --- |
| `host-core-run-preparation/plan.md` | 5962 | `634b29058c214f592e91ff25777d77f639d9e3499c2232e6cdcc7f62bc43cd96` |
| `host-core-run-preparation/execution-plan.json` | 6135 | `67fa19b4fd4750f4aa86560298b7d72c27b62f412a4abc407d29f7e4d722fb45` |
| `packages/native-location/tests/location_core_test.cc` | 29706 | `f1684029430f28918fd4caa062eb8d250f97d5d34aa3ab65c517e44954525037` |
| `packages/native-location/tests/location_child_probe.cc` | 380 | `041e60f57b34ec1b04157e73e2161b332acc3bc8f804d7f7fcd6baf575d34b9c` |

均为本人实际Git读回并实算。实际核九产品路径的b1→b592 diff，只有core_test的Darwin sys/stdio.h include和renamex_np(RENAME_EXCL)两处改动；八件其余产品/测试未变。此前预算全文/必要core责任链阅读沿同一固定源码使用，不再扩大平台矩阵。

本次cwd均为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。执行仅Git/文档/JSON/hash静态检查及必要官方primary网页阅读，正常exit0；没有编译、运行产品/测试/断言/runner/native/addon或FS/child实验，没有安装、GUI、用户内容/凭据/模型/Goal操作。本人唯一新增文件为本文；未修改产品、计划、已有报告、AGENTS、依赖或T03 WIP，未提交。

## 2. P2-RUN-01：环境替换和sole-waiter没有约束继承的signal disposition/mask

### 位置与触发

plan第15行及execution-plan.json的processControl/environmentReplaceNotMerge规定env替换、close_fds、新session和唯一waiter，但未明确SIGCHLD disposition、SA_NOCLDWAIT与signal mask。环境变量不携这些内核进程状态；exec也不会自动将所有忽略/屏蔽信号复原。

反例：executor传入SIGCHLD=SIG_IGN或no-cldwait语义，core的probe可以被自动回收，native对确切PID的waitpid得到ECHILD，无法提供sole-reaper收据。probe harness还可能因wait_owned=0走其旧pid失败清理；自动回收后PID可复用，不能再由该号码单独证明kill目标仍是本child。若TERM仍被ignore或mask，拟TERM宽限也不具有所描述的通常行为。这是未来执行环境条件缺失，不是声明当前已运行出该故障，也不修改已经限定可信fixture合同的native产品。

[Apple execve手册](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/execve.2.html)说明忽略与blocked状态可被继承；[Apple sigaction](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/sigaction.2.html)给出disposition/mask及no-cldwait语义；[waitpid](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/waitpid.2.html)的ECHILD不构成原child终态。网页是机制依据，不是本机实际signal状态证据。

### 最小修正

在准备文档/JSON加入执行前置：只针对本次即将执行core的子进程，在exec前建立SIGCHLD=SIG_DFL且无SA_NOCLDWAIT、显式空signal mask，TERM等本次控制所需信号为正常默认；core启动probe继承这些条件，native owner独占probe reap，外部控制器不抢wait。不能改正在服务用户的host进程、全UID或系统设置。

现有executor须给该准确能力与记录；若不能确认，继续PREPARATION_ONLY_BLOCKED，不新写wrapper/runner、不假定host默认干净。[Python subprocess说明](https://docs.python.org/3/library/subprocess.html)中的restore_signals只覆盖Python自己忽略的有限信号，不能替此条件；若计划用preexec_fn，也不能假定线程环境安全，官方明确提示多线程fork前后死锁风险。具体既有执行器如何满足条件需根给实件，不在本轮开发或试跑。

root已在协作中接受本项为过程文案P2，将另冻process ref。本文仍保b592原判断，未读取其WIP修正文；需新版本定点关闭。

## 3. 本main精确预算：可作为源级上界，不能冒充OS实测

| 项目 | 静态上界与推导 |
| --- | --- |
| owner | 总5个记录：metadata、child、partial child、revoke、budget各1。成功顺序最多1个nonclosed；错误断言抛出即停止后续case，不自动再创建owner |
| cap lifetime | metadata6 + child1 + partial1 + revoke(1+最多16) + budget128 = 153。root输出不再新增slot；坏组件和最后预算拒绝不reserve新cap |
| 累计component name | metadata的6+6+6+6+4，加16×3、127×3，合计最多457B。不是fixture绝对路径字节计账，也不是RSS上界 |
| child | core只启动一次；最多2次posix_spawn、3次adopt尝试（正常、重复拒绝、partial）；流程中同时至多1个本main已知未结算probe。此上界依赖固定源码及前述独占wait条件，不代替实际child census |
| thread/FD | 1个额外observer线程；源码显式父进程owned FD峰值<=5，不含0/1/2、dyld、C/C++runtime或runner内部FD；不能写为整个进程的实测FD峰值 |
| fixture | 1棵root、1个sub目录，最多member/old/alias/link四叶；regular file内容0B，symlink目标仅常量member；无DB或业务数据 |
| close循环 | 两个循环各最多1000次、每次sleep2ms，名义sleep各<=2s；真实OS调用可能阻塞，不能从循环数推出总wall time硬上界 |

计划所列这些数量与本人先前b1静态推导吻合。rename微修不新增owner/cap/spawn/文件资源；只在既有一次rename上增加目的已存在拒绝语义。

## 4. rename微修、/tmp与失败归属

Darwin include明确声明来源，renamex_np(RENAME_EXCL)替代会覆盖既有空目的目录的普通rename。require失败时path尚未更新，后续source cleanup仍指原fixture；没有exists预检竞态、普通rename fallback或替别人-moved清理。实际SDK/链接/FS flag行为仍待T03重构建及精确运行，不能用SDK27静态声明当macOS15通过。绝对source名仍不认证持续源对象围栏，计划第9行准确保留限制。

/tmp/i06-n0-XXXXXX确为固定源码常量，TMPDIR/CWD不控制它，成功后加-moved。plan第26行与JSON准确承认，未把工作目录独占0700当整个fixture被隔离。main未对外给创建目录路径/identity receipt；因此runner不能凭prefix、mtime、PID或前后差集确权，不能glob删、重开路径签身份或递归清可疑目录。

正常source cleanup只清anchor下固定成员和当次path。异常/abort/外层kill可能没有C++栈展开，目录或child未知均应保留事实；runner若无可证明的原资源身份，只能报unknown，不把“无法安全删”篡成“已清理”。计划已采取该边界，没有要求用户删除历史/业务目录或全盘扫描。

## 5. 已具备的准备合同与必须保留的控制条件

- admission为PREPARATION_ONLY_BLOCKED、artifactExecutionAttempted=false、resolvedCoreArgv=null，本人解析确认；旧b657产物明确superseded且未执行。只允许将来根批准的两个新绝对实物组成core argv，同一probe由main两次内部spawn；不单跑probe/CTest/addon，无自动重试。
- stdin明确/dev/null，两原始流独立0600、exclusive新regular file，dispatch前全部成功，保证0/1/2。这样避免pipe取得fd0、adddup2同fd后addclose关掉stdin；输出不merge/tee/filter，也不把工具截断结果当原件。既有executor还须实际落实二流1MiB各自上限与记录总量guard；本轮没有创建execution-001或输出文件。
- replace env仅列PATH/LANG/LC_ALL/TZ/HOME/TMPDIR，无DYLD/Node/代理/secret继承；signal条件另按P2补。shell=false、新session/pgroup、close_fds明确，但精确执行器代码/能力仍未交，不据这些字段声称已经隔离。
- 拟15s等待+TERM1s+KILL后wait自身core2s，logical control budget20s可作为有限控制意图；创建进程、同步FS/OS调用和写记录未被证明硬截止，计划已明示。必须用保原未reap leader的控制路径，信号间不能暗中poll/wait/context-manager自动reap。早非零已reap后不凭旧PGID补kill，避免号码复用误伤。kill返回不等于child或native owner drained。
- runner只wait自己的core，probe在receipt后仍由native sole-reaper处理。timeout/非零/信号都失败或retained_unknown，不能改为pass、自动重跑或扩大清理。exit0最多证明本宿主受控case走完原断言；原代码只核probe真实终态，不核每probe exit0，计划已明确不外推。
- NOFILE64、CPU12s、FSIZE1MiB、CORE0只拟用于本次进程exec前；不能改全UID/系统。RLIMIT_FSIZE为文件大小约束，不是loader/RSS/map或OS CrashReporter总资源边界；JSON相应RSS/loader值为null，没有伪造内存上限。

这里确认的是文档约束可审，不是执行器确实实现。若现有executor不能保证exact PGID未reap时序、signal/limits或有限原始流，就保持blocked，不能为本次临时开发新runner来绕准备范围。

## 6. abort和宿主环境门

std::abort在make_owner未知cleanup失败时可达；C/C++runtime异常或被系统resource limit终止亦可能导致signal结果。CORE0只处理core-file限制，不能证明macOS不生成系统诊断报告或弹提示。计划第30行未将CLI冒充这个强保证，也没有授权读改用户崩溃设置。

若本次要求连系统自动可见提示也零影响，根须交独立/隔离CLI环境及其适用边界；不能只说“没有Electron/AppKit调用”。本轮没有看用户桌面、触发abort或查询系统崩溃设置。既有macOS27宿主输出也不能替macOS15/Win11目标验收。

## 7. 可交根审与尚缺实件

已可交根审：固定b592源码微修/静态资源上界、仅一次dispatch的角色合同、旧artifact拒绝、独立原始流/env限制、自己的未reap进程组控制规则、不确权不删目录、失败不假签drain、无GUI代码不等于无OS提示等边界。

仍缺：P2信号合同正式修正文；T03对修复ref实际采用/重构建授权与新artifact绝对路径/bytes/SHA/inputDigest/实际used和许可闭包；现有执行器对stdio、signals、limits、未reap PGID和有界记录的准确承诺/来源；需要时真正隔离环境；根精确一次运行窗口。具体值未交，不能擅自把argvRoleContract替换为旧路径或自动寻找产物。

本报告不签run-ready、完整根批准或N0技术通过。除上述准备P2外未发现新的应改产品路径；不改八源/ABI/AGENTS/构建/依赖、不消费T03 WIP、不新增runner，保原Goal和既有产品门禁。
