# I04 原验收追踪

本表保留派发十项原验收及 I03 全部接入义务；状态证据以 [status](../../reviews/I04/status.md) 和冻结候选记录为准。最新本地、隔离运行及包内结果见 [C4 实际验证摘要](../../reviews/I04/c4-verification.json)；C2/C3 记录保留为历史检查点。C3 实际双审通过后首轮 PR CI 失败，C4 须新完整双审、真实跨平台 CI 和正常合并。

| 原要求                                             | 对应实现/有意义测试                                                          | 最终证据要求                                                                |
| -------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 常驻健康、协商、同源注册表与资源                   | EngineSupervisor / coordinator / resources；supervisor与resident_runtime测试 | 真实同PID重复health、公共例、源/包内SHA；严格v1拒绝                         |
| 真JSONL与独立限额                                  | TS jsonl / Python protocol，同源frame-fixtures                               | 每UTF8切点、粘包、重复键/深度/坏值、追加前限额、终态后chunk                 |
| request/job/operation/session/subscription/seq归属 | pending / matchesResponse / TaskService / JobStore                           | 并发乱序/旧代次/旧项目/旧订阅/缺口权威对账、完整指纹反例                    |
| 队列、并发、项目writer、各阶段超时与内存           | coordinator / worker / memory_guard；runtime_bounds / lifecycle_boundaries   | 真worker忙时心跳取消、stdin阻塞、退出等待、内存故障隔离、资源上界           |
| 唯一SQLite、同事务提交证据、确认与来源             | JobStore / Store，test_job_store                                             | 原子claim/正式marker/receipt/job、完整计划与确认、只读固定输入              |
| S1故障矩阵逐项                                     | 三种计划×八提交点×异常/磁盘注入/取消/真实退出，额外真实SQLite READONLY       | 保留前后事实/所有权/版本/失效/marker/job、原子回滚与完成后取消；fence后恢复 |
| 安全错误到UI四段式                                 | typed fault / SQLite主码 / bridge / task-presentation                        | 实际Python→主进程→preload→UI，未知来源安全、有限参数、无自动重放            |
| 窗口重建/崩溃/无响应及后台任务                     | TaskService持久查询/重订阅、i04-jobs.spec                                    | 真隔离可见聚焦/实际提示框、提交与任务保留、不重发、不因卸载取消             |
| U1身份/真实依赖/不可变稳定分页                     | job/result/current、集合摘要、SQLite cursor/list snapshot                    | 新增/删除/启停/引用变化、旧结果迟到、跨项目/页绑定/TTL/回收、原身份保全     |
| ADR采用、包内资源与继承边界                        | implementation、ADR-0003、build-engine、verify-i04-package                   | 用真实运行决定采用；不把设计通过、容器存在或静态检查当运行通过              |

F6 单独检查：真实逐轮输入/消费记录/快照/commitProgress/run_terminal/result 链路；maxRounds且有待事件、队列为空继续固定轮数；零轮和部分轮次失败/取消；最后轮无终态不能成功；完整终态后取消不倒退；摘要错run/snapshot/job、缺失、畸形、回收拒绝；稳定分页首个非游标页唯一摘要。仅关闭基础设施子项，业务 E.2/E.5/G.4/FR-704 仍未完成。

I03历史处置：R2-F1修复须真实消费者前生效并同版新双审；O1不扩新schema词汇/缺省数组上界；O2英文parameterMeanings不作UI文案；O3/R6保留开放及真实测量边界。I05/I06无产品接线，不代为完成其验收。

## C2 验证检查点（历史：0462e08）

标准 check：630 TS、1015 Python，全部通过。Linux arm64 独立容器：630 TS、1013 Python 通过，2 项仅 Darwin RSS/真实退出竞态探针按平台跳过；普通 desktop/CSP 与健康回复时序三项在源码与包内均通过。真实传输单测覆盖丢通知对账、atomic revision 隔离、首次订阅完成通知早到及安全错误。

[逐格机器证据](../../reviews/I04/matrix-evidence.json)记录实际 144 格的 setup/call/teardown、终态/版本/提交点/错误及只读数据库指纹；完整 JSONL 随 CI artifact 上传。缺格反例中原 5 个测试通过，证据插件仍返回 1，不以计数推导替代实测。

正式原子事务矩阵为 3×8×4=96 项；逐格核对完整版本/依赖/失效集合、精确事实所有权与 mappingState、claim 冻结内容及 receipt/job/marker/快照一致性、无孤立结果及重复恢复幂等。矩阵磁盘分支为 OSError 注入、取消分支为 KeyboardInterrupt 注入；真实 SQLite READONLY 与持久取消另有独立回归，不把注入称作物理磁盘故障。另有逐轮事务 0/1 已提交轮×6 提交点×4 故障=48 项。真实退出分支先等待旧进程退出，再取得 lease 并对账；异常、磁盘、取消、旧基线、响应丢失、零轮、部分轮和完整终态后取消各有状态及提交证据断言。

源应用和打包应用各通过实际协调器退出后的自动只读对账、首次手动刷新成功、已提交轮次与原子 marker 保留，以及隔离 reload/锚点终态与 native 崩溃/无响应恢复。迟到健康回复使用测试控制 IPC 交付顺序，经真实 preload 与 React UI 验证，不冒充实际引擎退出；实际退出由独立 coordinator-kill 用例覆盖。native 均有三个可见窗口、第二个窗口由外部 XGetInputFocus/可见窗口标题核对，两个真实原生提示框的窗口 ID/标题/可见性、真实 crashed/unresponsive、关闭调试器和启用 hang monitor 均记录于 JSON，任务/operation/提交点逐项不倒退。运行库为合成数据，不入库。

macOS arm64 与 Linux arm64 package:dir 及包内同样例通过：321 规范、11 路由、30 响应、9 结果游标、7 列表游标、41 binding、51 raw-frame 例，以及相同12项真实 runtime。资源 SHA 与源码一致，临时 cwd 不依赖 checkout 寻址。Windows 的真实 CI 和三个平台最终 CI 仍是合并前必备证据；未验证签名、干净设备安装或领域业务。

新增实际边界验证：未知总量任务由真实协调器发送计算阶段，源码/包内 UI 显示“阶段：计算”且无伪造百分比；结果页真实 210 行按 200+10 读取，201 拒绝，显式较小运行预算生效。会话真实接受 65,536 个唯一请求（含 hello/ping），下一请求及重复 ID 安全关闭；父 stdin 保持开启时退出码 0、stderr 空，随后新进程保留原子 marker/receipt/历史，并将未提交在途任务对账为 ENGINE_EXITED。该有限生命周期及写入不重放规则见 ADR。

## C3 修订与实际结果

修复握手绝对期限只在空 inbox 检查的缺陷：每次循环处理下一帧前检查原截止时间，拒绝的握手前请求不续期；及时协商成功后继续原会话，不把握手预算变成会话寿命。原默认5秒真实反例、空闲对照和修后真实源/包内记录见 [握手证据](../../reviews/I04/c3-handshake-evidence.json)。新增三项精确定时测试使用真实 serve/JSONL/SQLite，仅控制局部时钟和输入字节，不降低 LIMITS，也不冒充实际默认时长；旧实现两红、正常对照一绿，修后全绿。

采纳 R2-N1：新增 Darwin 父侧采样不可用的在树回归，以实际目标 PID 注入故障，断言目标 failed/INTERNAL_ERROR、无成功结果/operation；兄弟真实 worker 成功且结果行精确，两个进程回收。既有真实 ESRCH 分类、资源上限和 worker 自身监测故障回归保持。

C3 最新完整 check 为 macOS 630 TS/1020 Python；Linux arm64 630 TS/1017 Python+3 Darwin 专属跳过。两平台已重新打包，随后各通过公共例与13项包内 runtime。新增默认时长 stdio 用例保持调用方 stdin 开启，验证自然退出0、stderr空、精确安全响应和线程回收；相同测试随包内验证入口进入三平台 CI。有限输入在快速消费者上可能提前排空，因此该用例只证明默认预算的真实传输存活边界与清理；忙 inbox 的精确反例由独立真实默认探针和三项局部时钟测试另外证明。

新增第13项只改变宿主侧测试文件，生产/应用/构建/配置/依赖字节及两平台引擎包哈希未变。此前 C3 的1019/1016+3完整检查、12项包内记录和来源归档作为历史检查点保留，新完整检查及13项记录使用独立路径。源码及包内各六项隔离桌面/健康/CSP/reload/协调器退出/native 验收已重新通过；144 格矩阵两平台重新逐格通过，完整新 JSONL 与旧详细组件证据的来源一致性另行关联，不因仅新增测试重复执行既有绿色 GUI。实际原始值/哈希和边界均在 C3 摘要中；新候选双方新完整审查与真实三平台 CI 仍须完成。

## C4：实际 CI 失败后的修复与复验

首轮 PR CI 的 Linux Quality 成功；Windows engine:check 为39失败、978通过、3跳过；macOS 因 hosted runner 未取得而在无任何 step 的情况下取消。原日志及平台诊断见 [CI 触发记录](../../reviews/I04/c4-ci-trigger.json)，不能记三平台全绿或 Windows 包内成功。

修复帧测试与包内公共例 JSON 的缺省代码页依赖，显式使用 UTF-8，资源原始字节及原精确解析断言保留。独立审查发现第一版 cp1252 模拟在 UTF-8 mode 下失效；修正到 Path.read_text 的默认参数入口，普通与 UTF-8 mode 均复现旧36失败、新51帧及2回归通过。stderr 测试仍精确检查固定有界消息及本机原生换行；仅已退出 Windows peer 的 finally 管道清理容忍 EINVAL，原自然退出、时限、响应和 stderr 断言不放宽。

worker 在读取请求前建立实际协调器身份监控：私有 PID，Windows 创建时间及固定句柄；非法、已死、复用或 API/线程失败均闭口退出73。原实际父死亡用例保留3秒断言，并由实际协调器打印身份后精确终止它。Win32 doubles 用于签名、身份与失败策略反例；当前 Mac/Linux source 与 onedir 真实运行另列，不能据此代替 Windows native 或断言原 CI 完整亲缘链已复现。

完整 C4 check：macOS 630 TS/1052 Python；Linux arm64 630 TS/1049 Python+3 Darwin 专属跳过。两平台新包均通过相同公共例及17项真实 runtime：保留原13项，再验证真实协调器启动 frozen worker 后精确父死亡3秒退出，以及 stdin 保持开启时对缺失、已死和身份不符 owner 的三项读前拒绝。Windows 身份反例使用真实活 PID 及错误创建时间。两平台各144格矩阵重新逐格通过，Linux recorder 通过本次 Git bundle 的提交校验源字节。124个最终运行输入与实际根目录及容器均逐项同源。Linux 源码及打包应用各六项桌面/健康/CSP/reload/协调器退出/native 验收通过；后续仅三个宿主验证文件变化，生产字节、包哈希及矩阵输入未变，不重跑已绿 GUI。实际窗口、外部 X 焦点、原生提示框、任务及提交点证据使用 C4 独立路径。C3 原完整包及旧失败、C4 原13/16项检查点均未覆盖。C4 双指定新完整审查、之后的三平台 CI 和合并门禁继续保留。
