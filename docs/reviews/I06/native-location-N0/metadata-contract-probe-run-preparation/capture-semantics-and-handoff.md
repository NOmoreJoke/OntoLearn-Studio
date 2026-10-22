# 单产物捕获模板：静态交接

状态 **NOT_CALL_READY / PENDING_ARTIFACT**。本轮只在本新过程目录保存模板数据、相对固定e85ae888的增量证明和窄审；不运行controller payload、实验或API，不编译，不创建execution/record/fixture，不读取T03半成品或未来产物目录。源2b724与过程119a8保持冻结；根精确窗口原字节保存在本目录，根源码闭环指纹见preservation-check.json。

## 模板为何不可调用

arguments-template.json只有`argumentsTemplate`，没有最终`arguments`；声明intendedTool只是未来目标。artifactFields中的path/bytes/sha256/inputDigest/T03输入及过程ref/recordIdentity全部PENDING_ARTIFACT。payload内AUTHORIZATION和EXPERIMENT_PIN均None；原前置guard保持在其它import、目录访问和Popen之前。此处只静态parse，连guard也未运行。不能把wrapper或placeholder代入工具执行；None需要未来精确窗口才可填。

实际来源只写已收实验sourceRef `2b724f0188c233de5c8ef107d39fe0c4cb50311f`、processRef `119a8bef651a81ae80a6ef8bacdc64d4129e5373` 和20278B/6b6ff0969396c243c425dca507d0ea05732a0edb0123a264ab834cd2531690dd。尚无T03新产物身份，不能用原core/probe pair、旧digest或b592来源替填。根源码收件不是构建/运行成功。

## 相对固定004的唯一适配

控制基准是e85ae88815e45aa336850b594910a524a073cc00的diagnostic-fourth-call/exact-tool-call.preparation.json，19614B/8f9788b64b721ad60a8a1c5bf4a72287dd2519d6fcdedc82f5b681e1a8adb739；其中cmd17176B/100ebd1ae0a8f43608146565b95d145503e014b87beaccb53182fbc5115d8781。这里只继承已受限收件的算法，不重新给旧算法、内部资源或构造硬时限背书。

control-delta.patch显示19个原行的适配：AUTH/pin未赋值、去child-probe pin与argv、单pin pre/post、新BASE与三处execution-001、真实sourceRef/programKind、stream和FSIZE4096、实验退出标签及两个注释。实验argc要求1，因此intent和唯一Popen都是[EXPERIMENT_PIN["path"]]，executable同一pin；无额外参数或第二产物。

BASE只指向本新过程目录；RUN、mkdir和open未来名称均execution-001，仍O_EXCL式独占创建、存在即停，不检查/创建/复用任何执行目录。旧001–004和失败原件保持不动。

原`core.stdout`/`core.stderr`文件名及`corePid`/`coreReturncode`/`coreWaitStatus`键保留，均是此模板控制器对唯一实验leader/流的历史字段名，不是旧core、产品case或child-probe。为标签改全runner没有必要；sourceRef与programKind以及EXPERIMENT_EXIT0_REQUIRES_CAPTURE_REVIEW明确改变解读，事件/等待/退出算法不改。

资源变化只减不增：每流上限4096B，child RLIMIT_FSIZE4096B；单产物每次pre/post累计读取上限仍2097152B，总两次至多4MiB；不是提前认定产物大小。减少一个pin也减少一轮路径/fstat/hash读取，但没有测量耗时或内存。NOFILE64/CPU12/CORE0、六项清环境、private -I/-S入口、0600双流、三控制件每件64KiB/合计低于256KiB保持。

delta-static-check.json把旧AST仅按上述显式白名单适配后与新AST逐节点比较（不含行号）完全一致；所有非cmd工具参数相等。八个函数中只pin_pass的迭代对象由二变一，其余函数AST逐字结构相同；信号默认/空mask、取消、exact waitpid/ECHILD未知、15/1/2秒控制票、单Popen/不重试、原finally/收尾均未改。注释变化另由文本diff给出。未对旧17KB算法做新一轮全审。

## 实验、控制器与工具终态分开

| 子实验返回/事件                                  | 捕获与后继解读                                                                    |
| ------------------------------------------------ | --------------------------------------------------------------------------------- |
| 实验0                                            | 仅退出候选；controller标签明确仍需捕获内容复核，不能直接签eligible                |
| 实验1                                            | failed，含程序stdio失败；保首失败和原始输出，不重跑                               |
| 实验2                                            | unproven：必需E无充分ACL响应；停止该route，不补写absence语义                      |
| 实验3                                            | retained：已知释放失败/ownership或残留未知优先；不据leader回收签drain             |
| 信号、超时、取消、wait/ECHILD未知、记录/流不完整 | 未取得可接纳结果，按原控制器停止；保完整原件及未知，不新增扫描/kill旧PID/清理范围 |

原控制器对任何非零子返回最终通常退出1，或控制失败74；不能拿工具exit1推定实验一定是1。未来须从真实result中读取`coreReturncode`/waitstatus，并与Popen握手/实际exact wait、工具terminal receipt对应。若exec返回session，只能按最终另授精确空poll规则续同session；本模板不构成一次调用或poll许可。非cmd参数仍原workdir/login=false/yield1000/max_output_tokens1000。

即使控制器exit0、leader reaped且snapshot stable，也只说明已实现的捕获条件，不证明自然EOF、所有后代drain、fixture清空或完整stdout。nativeDrainCertified继续false，fixtureResidual继续unknown；原Popen构造/exec握手无硬deadline、外部SIGKILL可绕过finally等限制不抹去。

未来审eligible至少要：真实单产物前后pin一致，真实工具终态/子实验exit0无取消/超时/未知，三控制件完整且双流无预算/稳定错误，程序stdout按固定版本schema完整匹配case0–4各三行加eligible footer，stderr无程序失败证据。字段只允许原有限枚举/布尔/Int32/UInt32；正例form1或2（count分别NOACL哨兵或0），N对照form3/count1；成功记录api2/err0及全部必要判定为1。任何缺行、重复/乱序、额外或畸形文本、失败footer、stdio故障或不完整捕获不签eligible；不通过追加查询/重跑补结果。实际字节/响应与程序语义须另审，当前没有输出可验证。

eligible也只表示该固定profile值得下一步ACL适配，不是原owner/root/acquire/observe/撤销/关闭case或N0成功。原003/004失败、drain/fixture未知、内部资源/双OS/完整功能/指定同版外审/CI/真人/远端及T01 HOLD和SQLite/heap/OS拒线均保持。

## 交回与待补

有限manifest排除自身，记录模板/patch/静态证明/保护和独审，纯过程ref另交root。本轮不改实验、产品、旧模板/归档、CMake/driver/锁或Goal，不跑npm/旧测试，无GUI/DB/push/PR/merge。

待root真实收件T03单用途产物后，才按精确新窗口填artifact path/bytes/SHA/digest、T03 refs及record identity，并固定最终完整arguments、必要增量独审；最后另授一次CLI和实验setup/read/cleanup范围。当前所有这些字段继续PENDING_ARTIFACT，NOT_CALL_READY不解除。
