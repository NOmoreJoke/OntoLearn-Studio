# 一次性调用：API依据、状态机与剩余边界

2026-10-22。只读静态依据，未执行 call.md 的 shell/Python/guard，未做 signal、进程或 FS 探针。九源码及旧20件过程材料不改写。该调用只服务本次固定core/probe，不装为工具、产品runner、库或通用框架。

## 解释器与单线程条件

实际路径 `/Applications/Xcode.app/Contents/Developer/usr/bin/python3` 是指向 Xcode Python3.framework 的符号链接，最终实物为 `.../Versions/3.9/bin/python3.9`。直接读当前 `Headers/patchlevel.h:20-26` 得3.9.6，实物与配置/两件标准库的bytes/hash见 local-api-evidence.json。先前会话实际版本读取也为3.9.6；本轮不靠再次运行解释器验证版本，后续调用自检 `sys.version_info`、`sys.executable` realpath、isolated/no_site，漂移即停。

完整命令以 `/usr/bin/env -i` 清控制解释器入口环境，再 `python3 -I -S -`，不在持久REPL、嵌入/子解释器、用户site包或工具host里fork。导入仅已列标准库，不启动线程、后台reader、timer或watcher；主线程与Python线程数在Popen前拒绝异常。此检查不是OS原生线程枚举，根仍需认可全新CLI没有原生注入/附加线程、无外部reaper。不能确定则当前准备不解锁，不增探针。

[Python subprocess文档](https://docs.python.org/3.9/library/subprocess.html#subprocess.Popen)明确 preexec_fn 在多线程应用中可能exec前死锁；start_new_session 由内置setsid完成，避免在preexec加这项工作。所读在线页为3.9系列当前维护页（页眉3.9.25），具体本机实现另读3.9.6本地subprocess.py，不冒称在线页就是Apple构建源码。

## 信号及限制的真实API链

本地 signal.py:56-66 只是 `_signal.signal` 和 `_signal.pthread_sigmask` 的类型包装，**不**暴露sigaction flags读回。配置 pyconfig.h 定义 HAVE_SIGACTION=1、HAVE_PTHREAD_SIGMASK=1，HAVE_BROKEN_PTHREAD_SIGMASK未定义。官方同版本 [signalmodule.c:452-473](https://github.com/python/cpython/blob/v3.9.6/Modules/signalmodule.c#L452-L473) 把SIG_DFL转为C默认handler并调用PyOS_setsig；[pylifecycle.c:2361-2375](https://github.com/python/cpython/blob/v3.9.6/Python/pylifecycle.c#L2361-L2375) 在HAVE_SIGACTION分支新建sigaction、清handler mask、sa_flags=0后安装，因此该实现路径会清SA_NOCLDWAIT。不是靠getsignal证明flags，也不以restore_signals代替它；_Py_RestoreSignals只列SIGPIPE/SIGXFZ/SIGXFSZ。

依据是实际本地wrapper/config与同版本官方C实现；本轮没有反汇编Apple `_signal`/运行库或运行sigaction验证，不能声称已观测实际内核flags。未来根若不接受此版本/实现对应依据，应保持不执行，不悄加ctypes、自编native supervisor或信号试验。

[pthread_sigmask文档](https://docs.python.org/3.9/library/signal.html#signal.pthread_sigmask)规定SIG_SETMASK替换调用线程mask；本调用在新控制进程及core preexec分别传空tuple，core的probe继承。child preexec另将CHLD/TERM/INT设DFL，再设置 [resource.setrlimit](https://docs.python.org/3.9/library/resource.html#resource.setrlimit)：NOFILE64、CPU12s、FSIZE1MiB、CORE0，soft/hard同值；父仅先读hard limit，不提升、不改父limits或全UID/系统。任何设置失败不放行exec，不补更宽limit。

父控制器也必须避免core被自动reap，因此**只在未来新创建的一次性Python进程**安装CHLD默认（同样清flags）及TERM/INT置取消标志handler、空mask。这细化旧“只core子进程”的合同，不改变已在运行的shell/tool host/系统/全UID；子preexec重复建立自身状态。若根不接受这项私有进程内操作，不能沿当前调用运行。取消handler不raise、不IO/kill/wait；真正外部SIGKILL/OS终止不受finally保证。

## 一次dispatch与唯一wait

仅一处Popen，最大调用次数1，shell=False，替换env，close_fds=True，start_new_session=True；core argv恰两个绝对实物，同probe只由既有core内部两次spawn。stdin和两个独占0600 raw regular files在dispatch前都打开，父0/1/2缺失即拒绝，避免probe pipe取得fd0的错误前提。limits用于core/probe，父记录单独预付；不改变系统日志或崩溃设置，不新增“零OS提示”的隔离硬门。

实际本地subprocess.py:1872-1883的_try_wait在ECHILD时合成status0；因此本调用不使用Popen.wait/poll/communicate/run/context manager，也不在末尾触发其__del__隐式poll。只有控制器 `os.waitpid(proc.pid,WNOHANG)`，确切终态自行解码并更新proc.returncode；ECHILD、权限或其他wait错误均unknown且撤销号码发信号许可。最终os._exit避免第二个内部wait。全程没有wait(-1)、probe PID wait或外部reaper。

本地subprocess.py:1774-1809构造会读exec errpipe，失败分支内部可能waitpid(...,0)。这发生在Popen返回精确receipt之前，**不受后续15秒保护**；单线程和短preexec减少风险但不证明硬截止。构造抛出且proc尚无值时可能存在未知子进程，不猜PID/组、不重试；保dispatchAttempted和unknown。不得把此准备合同写成整个工具调用20秒绝对上限。

## 15+1+2秒及异常分支

取得Popen成功receipt后开始15秒WNOHANG等待；成功setsid由exec握手确认PGID=确切未reap leader PID。正常终态立即撤销组信号许可；非零/信号/未知均失败，不在reap后凭旧PGID补杀。超时或取消只进入一次cleanup；TERM后1秒完全不wait/poll，然后KILL，再最多2秒只收自己的core，不由新取消提前放弃这次有界wait。期间即使leader为zombie也保其PID不复用。OS调用自身、调度和写记录没有硬截止证明。

| 触发                                    | 本调用动作与保留事实                                                                        |
| --------------------------------------- | ------------------------------------------------------------------------------------------- |
| 空授权/空pins                           | import sys后立即exit78；不文件/信号/进程操作                                                |
| 版本/线程/平台/标准FD/limits/pin不符合  | 不dispatch；不自动找目录或升级边界                                                          |
| mkdir/open存在、拒绝或部分准备失败      | 不dispatch；只关闭已持FD，保留已创建目录/原件，不复用/删除                                  |
| preexec/exec/Popen构造失败              | 不第二次Popen；没有可用确切receipt则unknown，不能杀猜测组                                   |
| wait返回确切终态                        | 记录原status和code；仅终态0可继续静态后核，不认证probe各exit0                               |
| ECHILD/其他wait异常                     | 不合成0、停止该API，不再对该号码signal，保unknown                                           |
| timeout/取消且仍保未reap身份            | 一次TERM→1秒不reap→KILL→2秒exact wait；不清fixture                                          |
| TERM/KILL权限或其他拒绝                 | 停止signal路径，不换API、不提权、不补重试；保残留unknown。ESRCH仅记录无活group，仍不签drain |
| cleanup本身抛异常                       | 外层catch仍受cleanup_started挡住，不第二轮TERM/KILL                                         |
| post-pin drift/raw超限或不稳定/读取失败 | 控制非零，不重新跑core；保现有原件及未知完整性                                              |
| 记录部分写/预算/权限失败                | 不截断、不改写、不重开同记录；控制非零，可能只剩intent/raw，不能称记录齐全                  |
| 外部SIGKILL/解释器崩溃/OS阻塞           | 无finally/硬时限保证，需承认unknown；本次不新增恢复框架                                     |

工具平台拒绝本次调用即停止，不重新提交、换入口或要求提权。运行中OS拒绝的相应操作也不重试；只对仍持有FD做必要关闭及一次可用记录，不把拒绝变成通过。

## 数据和输出预算

三件控制JSON各最多65536B，合计<=192KiB，额外总闸262144B；事件固定字段最多24条，没有traceback、原异常字符串或环境全量输出。原始stdout/stderr独立独占0600，每件1MiB，child/probe继承RLIMIT_FSIZE；不merge/tee/filter/截断。后核只从持FD以pread读各最多1MiB，避免移动共享offset；未证明所有后代退出时只能称快照，size/mtime/ctime稳定不代表完整drain或未遭强同UID篡改。

每次pre/post pin pass最多两实物合计2MiB，有精确bytes/sha与前后FD身份/名字核对；不遍历构建目录/全系统依赖。当前API没有按held FD执行此macOS二进制，hash到exec的名字竞态仍依赖根窗口内输入不被并发替换；后核不倒推消除竞态。run目录以父dirfd创建/打开并保持0700，不认证整个祖先链或任意强同UID攻击。`/tmp` fixture仍无外部身份收据，不扫描、glob或删除；kill、leader状态、目录缺席皆不签native drain。

仅准备消息报告第三次构建摘要：input简写15163b3、digest227052c230da782ca62c20600e418f52e938378bd92f2961d7543f03ac43551c；core343904B/SHA229faf9fcf15ccbbc9e0e8fefefb1c91c016fc2ea6fea2df92998392e14e812b；probe34120B/SHAbe916e5252b21e6671c6bd2f32301f8581c1b32ce87f78a4a7b0f8314fb2a6b2。**尚未采用、无精确路径/正式manifest/根窗口，故两个pin仍None。** 不读取可变产物目录冒签收，不以reported13命令0或renamex_np符号摘要代替正式证据。

检索OpenGroup sigaction页面得到HTTP403，本轮不重试、不换入口取同页；所需机制已有官方CPython源码和本地文件依据，不使用该失败页作证据。其余读取/静态检查见记录，没有预处理、编译、执行候选或任何probe。
