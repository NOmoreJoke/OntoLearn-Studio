# I06 e2c 终态与恢复索引

2026-10-21。原 I06 Goal/分支继续，未将政策接收或阶段回归终态当作功能完成。本次只读核对原运行并收口原件，没有启动、恢复或重跑产品检查。产品仍为 `e2c269ad78a78e1a042cadc93b1c81a874707153`；现场远端批准 develop 仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。

## 先读这些文件

1. [原运行当前终态](main-platform/runtime-termination-readback-20261021.md)及[完整机读记录](main-platform/runtime-termination-readback-20261021.json)：当前容器/原 session/宿主等待客户端/原日志定位。
2. [本线本次原件读回](evidence/e2c-terminal-root-readback-20261021.json)：原 archive/index、逐门 exit/report、243 包文件与860产品 Git blob 的实际核对；这是工件检查，不是新测试。
3. [原 ARIA/source/package 回执](main-platform/aria-regression-review.md)及[原摘要](main-platform/aria-regression-summary.json)：首败、唯一复验、构建/镜像/ASAR 和适用范围。
4. 总控独立审计 `iteration-control/2026-10-19/I06-controller-e2c-aria-regression-audit.md`，本线已全文读回、实核 SHA `35994a0675376d9dd9ac3a93491713b36ec62afff4b3ca77cd48465e1abc13d2`。其结论没有要求改产品或重跑旧未变矩阵。

## 原句柄：全部终态，勿重新 start

平台线在 UTC 01:19:47—01:23:07（北京时间09:19:47—09:23:07）只读核对：

| 运行             | 原 container ID                                                    | 原 exec session → final exit | 当前容器                                    |
| ---------------- | ------------------------------------------------------------------ | ---------------------------- | ------------------------------------------- |
| aria1 准备失败   | `469b6fae55437be19832cf5c4e471af8fe3abac7a015f8964fd34ebf8c97885c` | 96217 → 1                    | exited / Running=false / Pid=0 / ExitCode=1 |
| aria2 原十门     | `0d3a9bb534db31ec2390739b5b4e14cff47b8108bee0a80e0b3af672d73b69b4` | 62110 → 0                    | exited / Running=false / Pid=0 / ExitCode=0 |
| 唯一 native 复验 | `ecc6a6287606655422343400a08b4c86ace69bb463a6f92666f952966d4e70a1` | 5804 → 0                     | exited / Running=false / Pid=0 / ExitCode=0 |

三份 `docker top` 均明确 not running；原 session 的空输入读回均为实际 final completion，没有尚待续接的 yielded 句柄。精确容器名与 docker start/attach/wait/exec 的宿主归属筛选为0；不扩大为其他任务/全部宿主进程均空，也不将旧容器内历史 Electron PID 当宿主活进程。未取消或重分类持久化 fixture job。

本轮工件核验另有自有 session92864：卡在 Python3.9 communicate 向 Git stdin 写入，确认自有 PID43388/子 Git43428 后仅中断该核验，exit130；不属于原产品运行。改为常规文件 stdin 加30秒超时后，同一工件核验 session69209 已 exit0。两者均终态，不需续接；中断记录保留于本次机读读回，不计作产品测试通过或失败。

## 原结果及原件直接入口

**首次10门9过、source-native exit1；同 image/源码/运行文件，仅该原用例换独立新容器/新 fixture 复验1pass/0skip/exit0。** source 与新实际包的原全量各3pass/3默认fixture skip，六项 fresh fixture 原测试均实际执行；不把 skip 改记 pass，也不说一次全绿。

首败原代码每phase `Date.now()+30000`，30秒；report总13.315552秒，trace单调差约12.25秒。差异原因未明，单次复验不证明不稳定性消除。aria1 的 helper/cache 准备失败及未运行项也保留。

这些运行限隔离 Linux arm64 Docker/Xvfb/GNOME 环境，唯一额外 SYS_ADMIN、默认 seccomp；不称默认无额外权限 Docker，也不代表当前 Mac 桌面或 Windows/macOS 的真实平台通过。

根 worktree 已保存同一原 archive：

`tests/i06-main-platform/out/i06-main-e2c-aria2-native-retry1-raw.tar.gz`

154270058B，SHA `f13d9a6f0cb06b39703a91bfd76e85266c87583c0123f5c31a92ee8ccb1afa34`；598个regular成员，index自身加597索引项，index SHA `f29eecfe97648e650f5c896095f4a9695d64d101b873212e4408b5cb86356205`。本次逐项字节/大小/hash一致、243新包文件一致、860产品来源与e2c Git blob一致。总控独立审计另外核对881=candidate内860产品+21旧harness、实际overlay39及ASAR5；这些计数不混用，不将host归档UID501/20称runtime1106。

本线从同一归档精确复制了退出记录/报告/receipt/三份原inspect到下列ignored目录，方便直接读回，没有修改原件：

`tests/i06-main-platform/out/e2c-root-terminal-readback-20261021/selected-raw/`

- [首次 source native 退出记录](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway/tests/i06-main-platform/out/e2c-root-terminal-readback-20261021/selected-raw/e2c269ad78a7-aria2/evidence/results/regression/source-native-exit.txt)及[原报告](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway/tests/i06-main-platform/out/e2c-root-terminal-readback-20261021/selected-raw/e2c269ad78a7-aria2/evidence/results/regression/source-native-playwright.json)。
- [唯一复验退出记录](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway/tests/i06-main-platform/out/e2c-root-terminal-readback-20261021/selected-raw/e2c269ad78a7-native-retry1/evidence/results/regression/source-native-retry-exit.txt)及[原报告](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway/tests/i06-main-platform/out/e2c-root-terminal-readback-20261021/selected-raw/e2c269ad78a7-native-retry1/evidence/results/regression/source-native-retry-playwright.json)。
- 完整十门与log/trace/真实native verified原件绝对路径、hash均在上述终态JSON；完整包及其余原件继续在原 archive。

wrapper/container/session exit0只表示采集脚本结束，不代替各test/helper的exit。generic S3 binding的failed继续保留：本回归未运行它的probe/receiver/leak-scan，既不把failed重标pass，也不拿它覆盖专用e2e结果。948721a3为Docker inspect镜像身份，不是另取OCI config blob/签名证明。

## 受影响范围和真正余项

| 项                  | 当前可接受证据                                                                                                                 | 仍需完成                                                                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| e2c ARIA/原生恢复   | 新source/真正新包、十门原件与唯一复验、实际crash+hang提示/焦点；首败保留                                                       | 未明时限差异/稳定性风险保留；不因本次收口另跑旧矩阵                                                                                          |
| S3本地保存/凭据边界 | 旧9fc normal22的初始化/audit失败仍可真实Store提交，native4/pkg2的Store/ledger保持和不重发，均保留原绑定；9fc→e2c产品仅ARIA变化 | e2c该回归未运行完整S3 probe；正式语义/format3/导出组合候选的实际本地保存与取消/恢复，按真实delta联验                                         |
| 导出排除            | 当前私有目录/DB排除源码及9fc实际DB/vault/日志原件                                                                              | 批准基线无export capability；真实T10导出/导入/HTML/临时产物尚未验，不能用假exporter关闭                                                      |
| 正式语义            | 当前只读结果接口和有限合成policy已实现；production fieldModels=[]                                                              | I05实际批准语义/implementation/真实结果样例及按需正式字段来源；见[具体接口请求](../../iterations/I06/semantic-export-integration-request.md) |
| format3             | 八文件与Python/storage已交T01，原固定字节保全                                                                                  | 真实同源协议/Store/Job-ready、升级生命周期和严格绑定消费，实际批准合入后协调；不复制未批实现                                                 |
| 其他平台            | Linux受测实际后端与失败边界按原9fc回执保留                                                                                     | Windows/macOS实际安全存储/权限/锁定或不可用、干净设备/签名升级证据未由这些Linux运行提供                                                      |
| 外审/合并           | 指定模型和同候选完整门保留                                                                                                     | 暂无合规审查桌面入口/时段；不抢当前Mac。最终双方新完整只读任务、意见处置、PR/实际CI/正常merge/远端核验未完成                                 |

当前T01八文件交接正文已实读新排版快照 SHA `eea3eefe86555d585236f603b2ebb01ecac49c1350193c6d83c262b6209f1030`；原add988是先前通知/接收时快照，不改旧证据。T01共享/存储、T03四构建路径继续停未来编辑；I06余六保留，现产品代码未改。恢复顺序是消费实际批准依赖及冻结接口、协调逐文件owner并适配真实delta，而非重新启动本页已终态的容器。
