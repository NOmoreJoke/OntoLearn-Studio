# N0一次性控制调用：独立静态审查

2026-10-22。结论：**固定a937存在一项需收口的P2控制结果判定问题，另有一项P3 API表述精度；当前不签具体调用无阻断。** 其他关键控制链可由源码静态对应。此审查只供根独立核验，不构成运行许可；AUTHORIZATION、两个pin仍为None，不采用准备摘要里的新供方简写或产物hash。

## 1. 固定输入及实际动作

受审完整ref：`a93733837e0611c6d5681c7efc2572a829389371`。全文读取同ref以下四件：

| 路径（concrete-call内） | bytes | SHA256 |
| --- | ---: | --- |
| `call.md` | 18014 | `5ba2758c4eedca4b441df2f808ebb16ba198e64140e652f02c78f68c8b45c91d` |
| `api-basis.md` | 10050 | `58087bd47973c377f1e4d08b7aeb33b551c7eba76fe7dc5e077fae554c28a694` |
| `local-api-evidence.json` | 4952 | `9a2e92dfece7f674a3596511ee638b0ccc9858bce74b2c331be3068ea32b1f55` |
| `static-check.json` | 572 | `f3e9fa67ebbbaccdc13ebf5cb049ebe34e7f9077b9c1d0f739c45ce28194c13f` |

以上本人实际Git读回实算。static-check的call文档hash对应；其15635B/407b918471d512589bf01e99733855b0801a4d8f4074ec68ab33ca58eeaba733对应去掉末尾LF的嵌入Python解析文本，本人按同一提取口径核符；实际here-doc送入stdin还包含该末尾LF，15636B/SHA256 `433dd1480c4c3de0d68dcb4f4988ba933f72221853f9a6cb2a54bafd4275730b`。这是字节口径区别，不是逻辑差异；AST文本hash不能替代以后补值后的完整实际cmd身份。

必要本地来源只读：Xcode Python实物、patchlevel.h、pyconfig.h、subprocess.py、signal.py的bytes/SHA均与local-api-evidence匹配；抽读subprocess析构、exec errpipe及_try_wait，signal包装。另只读官方CPython v3.9.6 signalmodule.c/PyOS_setsig原段和Python3.9 os.waitpid机制。未反汇编Apple运行库，也未认证其所有C实现与上游完全相同。

所有shell均显式cwd为本N0树。本人唯一新增为本文，不修改调用/九源/旧证据/T03 WIP/AGENTS/Goal，不提交。只做Git/文本/JSON/hash及官方网页读取，正常exit0；没有执行候选shell/Python（包括空guard）、没有exec/eval/import候选，没有调用signal/process/FS probe、编译、native加载或GUI。本文中的反例均为控制流推导，无实际发送信号或故障注入。

## 2. P2-CALL-01：postflight期间已观测取消仍可退出0，结果status也未覆盖后核失败

### 固定位置和反例

call.md:284–300及309–329。

1. wait_until取得core真实终态0，line290将status设为HOST_CASE_EXIT0；此事实应保留，不应事后改造coreReturncode。
2. line294–295读取产物/原始流期间，私有Python收到TERM或INT。handler只更新cancel_signal，故postflight继续返回。
3. line297只检查HOST_CASE_EXIT0和两流stable，不检查取消。line298令控制exit_code=0。
4. finally可记录cancelSignal非0，仍在line329 os._exit(0)。于是“控制调用成功”和“已观测取消”同时出现，等待阶段与后核阶段的取消含义不同。

另一个同段分支：raw超限或不稳定让exit_code=1，但JSON status仍HOST_CASE_EXIT0。虽然严格同时查看工具退出码的消费者可以识别失败，主status作为控制结果很容易被错当整次后核也已通过。

### 影响及最小修正

该问题不冒造core实际exit0，也没有再次dispatch或越权kill；风险在一次性运行证据的终态投影和取消执行约定不一致。应保coreReturncode/coreWaitStatus为已取得的原事实，同时让已观测控制取消得到明确cancelled/非0，后核失败得到FAILED_POSTFLIGHT而非控制通过status。不得因leader已reap再次signal旧PGID。

最小收口可在后核返回、finally形成记录前及最终os._exit参数快照处检查已观测cancel_signal；后核超限/不稳定也更新控制失败status。记录按实际写入时刻形成快照，写后或关闭期间再取消时可以出现早记录和最终工具非0不一致，须准确说明而不重写原件。不能承诺原子捕获最后一条指令之后才到的信号，亦不需为此新增框架、runner文件或产品API。

root已接受该P2及上述状态分离方向；本文仍固定a937，不将工作区修订当已关闭。应另冻新调用身份做定点回读，不能执行本版试取消来代替静态修复。

## 3. P3-CALL-02：不重试只约束Python层收到异常后的动作

位置：call.md:149–153及api-basis的API拒绝/不重试描述。

源码确实在os.waitpid向Python抛异常后停止该API、撤销号码发信号许可，不会把ECHILD合成0。但不能据此声称所有原始syscall（尤其EINTR）绝无内部重试。[Python3.9 os.waitpid说明](https://docs.python.org/3.9/library/os.html#os.waitpid)明确signal handler不raise时可能内部重试，这是PEP475层的行为。调用的取消handler正是不raise。

建议仅改注释/API依据，明确“不重新发起已被Python层以异常拒绝的操作；CPython内部EINTR重试不由该状态机计数或禁止”。权限/平台真实拒绝后不换API、不提权、不重提工具调用的约束保持。此项不要求更换stdlib或加入native接口。

## 4. 单线程、信号、limits与stdio链

### 单线程/版本前置

全新env-i、固定Python、-I/-S、主线程/Python线程数和subprocess._active检查是明确窄前置，源码无新增线程/timer/reader。它们不能观察所有native线程；call末尾已把无原生注入/仪器线程、独立CLI且无外部reaper列为根需认可的外部条件，无法确定就不执行。这不是仅凭threading.enumerate签fork安全。

preexec函数只做信号及四项setrlimit，所有import位于父；没有在其内加日志、文件、callback框架或setsid，setsid用Popen内置。没有发现另一个必然触发的静态preexec死锁，但未运行/证明该Apple构建在目标环境下的实际行为。[Python subprocess](https://docs.python.org/3.9/library/subprocess.html#subprocess.Popen)的多线程preexec警示继续适用。

### 信号依据和私有父状态细化

本人核本地HAVE_SIGACTION/PTHREAD_SIGMASK配置、signal.py包装与同版本上游[signalmodule.c](https://github.com/python/cpython/blob/v3.9.6/Modules/signalmodule.c#L452-L473)、[PyOS_setsig](https://github.com/python/cpython/blob/v3.9.6/Python/pylifecycle.c#L2361-L2375)：SIG_DFL进入设置函数，HAVE_SIGACTION分支新context的sa_flags=0且mask清空。因此该实现路线可清NOCLDWAIT，而非用getsignal只读handler猜flags；本地wrapper本身不提供flags读回。api-basis已准确保留未观察实际内核flags、未反汇编Apple C实现的限制，根若不接受此对应推断就仍不执行，不加ctypes探针补事实。

新控制Python父进程也需要CHLD默认，避免core被自动回收；TERM/INT只置flag、空mask使后续逻辑有机会有限清理。它只细化未来新独立控制进程自己的状态，不修改当前工具host、shell或全UID。相对原“只core子进程”的约束属于需要根在具体调用中明确认可的最小前置，而不是已有运行许可。child preexec再次设置CHLD/TERM/INT默认、空mask；probe由core继承，外部不抢probe wait。

### limits与明确FD

四项limits只在新core的preexec设soft/hard同值，先检查原hard不低于请求；失败不exec、不提高权限。NOFILE64/CPU12/FSIZE1MiB/CORE0不作用全UID，亦不是父控制器、loader/RSS或OS报告的全资源硬界。core/probe各自继承CPU限制，不应把12s写作整棵进程树累计CPU实测。

先核父0/1/2存在，打开/dev/null和两份独立O_EXCL/O_NOFOLLOW/CLOEXEC regular raw，0600与owner再核；三FD均>=3，再由Popen显式映射到core0/1/2。这样固定native probe的pipe不会因原标准FD空缺拿到0。新run目录只独占建立一次、0700，不复用或删旧execution-001。env完全replace，未透传DYLD/Node/代理/密钥。

## 5. exact wait、未reap组及异常责任

本人实际读本地subprocess.py:1872–1882，_try_wait在ChildProcessError时确会合成sts=0。该调用在Popen返回以后自行exact waitpid，终态自行解码并填proc.returncode，ECHILD/异常不假造0；无wait(-1)、无对probe PID的wait。末尾os._exit避免正常析构/_cleanup/context manager再做一轮wait，前提仍是独立CLI无人额外reap。

本地1750–1809也确认Popen构造内部fork_exec和exec errpipe/失败wait可能发生在receipt之前，耗时不受15秒约束。构造抛出proc仍None时没有可用具体PID，call不会猜PID/组或再Popen。潜在未知子进程与缺记录边界被明示；不能把“一次Popen站点”误写为整个调用20秒绝对硬截止。

取得receipt后15秒WNOHANG等待；timeout/等待中取消时，cleanup_started在首signal前置true，TERM后1秒无poll/wait，随后KILL并最多2秒exact wait本core。保原leader未reap可防PID再分配，不用getpgid事后猜组。正常/非零已reap后撤销组signal许可；process API异常时也撤许可；权限/其他拒绝停止，不替换API提权。ESRCH只说明该时刻无活group，不签native drain。

全部cleanup最多启动一轮：若正常路径cleanup抛异常，外层catch再调用也被cleanup_started挡住；没有重启TERM/KILL序列。若catch内cleanup本身进一步抛出，finally仍是收据快照/FD关闭路径，未发现第二dispatch或凭旧号码补杀。异步SIGKILL/解释器崩溃可绕finally，写记录/同步OS调用亦无硬wall保证，不能事后把无记录推为已安全结束。

## 6. 证据预算、postflight与未授权门

三件控制JSON各<=64KiB、额外总guard256KiB，event最多24条固定字段，无原异常字符串/traceback或全量环境；预付payload失败不重开覆盖。raw两件各1MiB，RLIMIT_FSIZE约束子进程写文件；postflight通过held FD的pread读取，不移动与child共享的file offset。超限/不稳定/短读不能算完整成功。core或descendant未独立全收口时，稳定size/mtime/ctime只称快照，nativeDrainCertified始终false。P2修正需让控制status也一致表达这种失败。

每pre/post pass仅两个pin合计<=2MiB，hash前后核FD与名字。本人没有读取T03 WIP或用15163b3摘要装pin；call原文None保持。hash到path exec之间没有held-FD执行能力，依赖根窗口保证确切实物不并发换；后核不倒推消除这个竞态。该限制已明示，不扩成恶意同UID/DLP要求。

无/tmp fixture外部创建收据，不扫描、差分确权、glob删或失败后重开签身份。关本控制FD或kill本组不签native owner/probe drain。核心source只核child终态，不证明两个probe各exit0；macOS27宿主结果也不替macOS15/Win11或完整N0。CORE0不禁止OS自动诊断/可见提示，根需要的隔离条件未被此调用暗中解决。

输入补值就是新调用身份。仍缺正式新产物路径/manifest/实际used、根对具体Python实现与单线程/私有父状态前置的认可，以及精确一次窗口；当前None和明确禁止执行保留。工具平台拒绝就停止，不重试同一工具、换入口或升级权限。本审可指出源级控制问题，但没有执行包括guard在内的任何候选部分。

## 7. 交付结论

对a937固定原文：P2-CALL-01需修；P3-CALL-02需文字收口。未发现另一个明确P1/P2的越权dispatch、错误PGID回收或双cleanup路径；这不是对未运行环境的安全保证。待原文保全、新ref及精确diff后，仅点读修正，不为验证本次问题启动signal/process/FS实验。

本报告只供根独立核验具体调用准备，不构成实际run-ready、产物采用或运行权限；不修改九源、旧证据、构建/依赖/AGENTS/Goal，不提交。
