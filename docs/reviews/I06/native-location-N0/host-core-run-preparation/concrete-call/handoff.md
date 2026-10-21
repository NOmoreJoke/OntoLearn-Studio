# 本次一次性控制调用交接

2026-10-22。仅准备，未执行调用、空guard、core/probe、signal/process/FS探针或GUI；未改九源码、旧20件过程证据、依赖、AGENTS、系统/全UID状态或Goal。

可逐行审查原文：call.md；完整机器可读工具参数：tool-call.preparation.json。当前固定调用候选 `cc1fc11d1537c36cb9de948802c08a5af940fad2`，前稿 `a93733837e0611c6d5681c7efc2572a829389371`。源码仍 `b59239f9c1ec2774c7922f95dfc67db4dc8754e8`。当前call.md为19048B/SHA256 `1188378bf9dca71e76c2e32b5dd31130d8c84531533716c9c76db3b0356876f4`；嵌入Python仅做AST解析，未exec/eval/import。

解释器为Xcode `/Applications/Xcode.app/Contents/Developer/usr/bin/python3`，实物Python3.framework/Versions/3.9/bin/python3.9；当前版本头为3.9.6。实际本地wrapper/config/subprocess证据、官方API和同版本CPython源码依据见api-basis.md及local-api-evidence.json。没有把上游同版本源码冒充Apple二进制反汇编或已观测内核flags。

具体调用固定独立 `env -i` + `-I -S` CLI，条件性单线程preexec；私有控制进程须先建自身CHLD默认/取消handler/空mask，core preexec重复CHLD/TERM/INT默认、空mask及四项limits。该私有父状态操作是旧准备合同必要细化，须根逐行核准，不作用于tool host、现存shell或全UID。不能确认无原生附加线程/外部reaper就不解锁，不以线程枚举作强保证。

一处Popen、无重跑、显式stdin及0600双流、替换env/new session/close_fds；exact waitpid区分ECHILD，不合成0。receipt后15秒，超时/取消仅一次TERM→1秒不reap→KILL→2秒自己的leader wait；已reap/失去身份/平台process拒绝后不凭旧PGID追杀。Popen构造握手/preexec/文件和系统调用没有硬wall截止，不能称整个命令20秒上界。三件记录各64KiB、总闸256KiB，两原始流各1MiB；pread不移动共享offset。未知fixture/child残留不扫描或删除，控制退出和kill都不签native drain。

首审指出后核取消可误让控制返回0的P2及EINTR重试表述P3，修订保持coreReturncode事实，后核/记录前/最终返回快照查已观察取消，控制非0；raw不稳定/超限明确FAILED_POSTFLIGHT。写后取消可使工具非0而JSON仍为早快照，不重写原件；最终参数快照后到达的信号无原子捕获保证。仅Python层已抛出异常不重试，不否认CPython PEP475内部重试。处置见disposition.md；独立首审和定点跟进按原件另存。

首轮api-basis格式检查exit1，原文和修正后exit0保留；AST、JSON、格式和保护范围检查都属于静态，不代表控制调用运行通过。独立首审independent-review.md为11788B/SHA256 `89b4eb2706092cfda74b9a6efdff70cba926b2888a8cb7f6c4d13cd68db0a9a7`；固定cc1fc11定点复核independent-followup.md为5869B/SHA256 `fb696c9cd347f0d25adba9829736dd7b32c69b6f0b8ac63ffef80633b39b6366`，P2/P3静态关闭，未发现新增阻断，不是运行许可。

原call.md/tool-call.preparation.json仍保三项None、与cc1fc11逐字相同；它们不能用后来补值副本覆盖。

根随后已接受T03固定输入15163b380035a3b402d5dbb485ab6d3d05e4e559/过程113e324d7420ec06c885ca2d8a634e68f2d85c9e为built-unverified/NOT_RUN，并精确授权**仅补三赋值准备副本**。据根控制T03-third-core-build-root-closure.md及精确消息，新增exact-call.md、exact-tool-call.preparation.json，完整cmd为17176B/SHA256 `2428cac0cbfa5cf9bf8906e0e1800e776b865408eece1950ff1f0029884921a6`；实际here-doc stdin含末LF16976B/SHA256 `38081f9c963ae11adb40a1f1ad6232f72cb2e101a003184039414437afd827c4`。只有命令第4–6行三赋值变更，AST归一化三值后逐字结构同一，其他四项参数不变，见exact-three-assignments.patch与exact-fill-check.json。

**精确副本仍禁止执行：三值已非None，技术guard不再阻止误执行；AUTHORIZATION字符串仅record identity，不是最终运行授权。** 根还须独立核验整个新调用及给唯一一次CLI窗口。本轮没有运行窗口，未读取可变产物目录、未运行任何候选（含原None guard）或探针。工具平台拒绝即停止不重提；不造“零OS提示”新硬门，不改崩溃设置。
