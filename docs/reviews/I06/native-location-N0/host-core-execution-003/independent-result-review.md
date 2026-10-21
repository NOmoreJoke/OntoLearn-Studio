# 诊断003唯一执行：独立结果复核

2026-10-22。仅核本次已执行结果，非根因修复、再运行或N0验收授权。

结论：授权、固定调用、新pair pre/post、runtime原件与实际工具终态一致，无新增证据问题。实际仍是 **工具退出1，core正常退出码1，003失败**。新独立诊断行支持本轮进入platform_metadata内ACL query返回nullptr分支，errno快照为2；具体原因未知，不能据此证明空ACL、缺路径或选择修复。旧001/002不得倒填同分支，native drain及父门仍未关闭。

## 授权和固定身份

已全文读实际根 `iteration-control/2026-10-21-weekly-release/I06-N0-diagnostic-003-single-host-CLI-execution-window.md`，与封存authorization-window逐字相等：3760B/SHA256 `d1570b0958caf4a5dc48601f42547bda1530c6cdfdc27027709ed09d7f01b6db`。它仅批准本次精确003一次，准备中的PREPARATION_ONLY保历史，不能代替或扩张该窗口。

唯一准备ref `5b78098ae8b53168fc23ec7499f240d1ede3f1c6`，路径 diagnostic-third-call/exact-tool-call.preparation.json；admin fixed-tool-call副本与该固定Git blob逐字一致：19615B/SHA256 `4c14304e4e4be6b041f60596aa581ed277af40e79d4499f9d2e8bf9e38d8cbe5`。完整cmd17176B/SHA256 `ed84b73de7178ba8340843ed54b63d6cf45e6f683074833ad1f4a356df3aede3`；here-doc stdin含末尾LF16976B/SHA256 `a67944783c48d1fb0e888d1ce6991665873881a482a91a6673c979425c8c07d1`，与授权及dispatch/summary身份一致。

已读取admin各件及五runtime，独立核capture-manifest11个列项的实际bytes/SHA及五runtime当前0600；授权标识、固定arguments内三个赋值、runtime argv/pins、summary/sourceBinding/dispatch-intent及工具receipt逐项相符。只将AST取值作数据，不eval/exec。所有命令显式cwd为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`，静态数据检查退出0。

本轮没有执行native/候选、编译、任何探针或产品检查；未重审旧控制算法/长报告/五轮供应史，未重启SQLite/资源接口被拒线，未扫/tmp、清理残留、kill旧PID、GUI或修改Goal/提交。未重读供方二进制，以本次原pre/post身份记录交叉验证固定调用。

## 原件与实际终态

| execution-003原件 | B | SHA256 |
| --- | ---: | --- |
| intent.json | 1899 | 297ebe19ef0ce89a1ff831eec4484998cafea0aacd6907e3eca0a9618da019a6 |
| postflight.json | 1136 | dbdf2f02af824b65a486f2b52c8c7da2ed57e6dd274e624c984303133b0ee2d1 |
| result.json | 517 | ef83597b27b4e298bc4b5ab6dd4c2bbd05ffa32832024cdee09c0b31fe7968bb |
| core.stdout | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core.stderr | 126 | f508e845a5ee83f12edcd0a2d0a1456f78124530b167538cea7755ae0a21c74f |

三控制记录共3552B，各低于64KiB/合计低于256KiB；原双流共126B，各低于1MiB。postflight两流stable=true，实际bytes/hash与原文件一致，只证明已保存的输出快照，不能升级为自然EOF或后代drain。

tool-receipts只有一次exec初次receipt：chunk e76c7f、exit1、output为空，没有session_id；dispatchCount=1、continuationCount=0、summary.sessionId=null相符。没有write_stdin或重提交；本次无会话号，不得从旧执行拼接session。

runtime原result：corePid12206、waitOutcome=terminal、leaderState=reaped、coreReturncode=1、coreWaitStatus=256、cancelSignal=0、events=[]、processApiRefusedOrWaitUnknown=false、retry=false。summary逐字段相同；256是原wait status、正常退出码为1，不是signal256。没有timeout/取消或组信号收口记录；空events不证明全部资源排空。0.722300709秒是原waitAndCleanup字段，不作整命令wall、性能或硬时限结论。

## 新126B诊断的有限解释

原stderr全文：

```text
N0 unsupported stage=acl-null errno=2
N0 owner-create case=metadata status=4 owner_nonzero=1
N0 fixture failure: owner-create
```

实际三行含LF为38/55/33B；新endpoint行实测38B，低于96B。此前49B是静态格式上界，不能写成此次实测长度。

仅点读固定新源 `fc9853f3521faced3a3b88ab8254310c9748a6a6` 的platform_macos.cc23–30、101–107及core_test379–388：101行调用acl_get_fd_np；只有返回nullptr才进入102–106分支，立即保存errno，记录acl-null，再返回原NL_UNSUPPORTED。helper写后恢复该error。因此按本次新源/产物绑定，独立acl-null行支持本轮走到这个ACL query空返回终点，快照数值2。

`metadata` 仍只是case标签，不是平台函数名；本轮进入platform_metadata的依据是独立acl-null行对应的固定返回路径，不能仅由case标签推断。后续owner-create原诊断status4为NL_UNSUPPORTED，owner非零仍不满足status==NL_OK且owner非零的成功条件。没有额外调用trace/API query证明为何null，不能将errno快照自动解释为空ACL、路径缺失或OS/权限根因，也不改null为成功。

001/002原raw没有该endpoint行，本次新增证据只能约束本轮，不能追认它们已命中同分支。没有据此签后续case/EXCL/目标OS/父N0通过、释放未知资源票或判断残留可删。

## 新来源与原样历史字段

真实来源另外绑定：I06产品fc9853f3521faced3a3b88ab8254310c9748a6a6/过程6fda0648299ae7e7d7d049ad5852e6d61b1618c5；T03输入0514d37e32e31ae569e583bb56ec225ebc0483e6/过程8528ccb3d68de4f31ee1e10bd984084e0f7f418c；digest0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb。

intent.preArtifacts、postflight.artifacts、summary.prePostPair完全相等，path/bytes/SHA与固定call一致：core344096B/65cca109ce2a43b24c94fc013b5e91127548d4be3d39de5330024128ffdb8039，probe34120B/12d355d3cc43fc5c39b6e8689d7e0dabb6909b8dfd7a7deed6322f3351d80e48；同dev16777232、ino66738069/66738076。每pass合378216B低于2MiB。这是本次实际预后原件对应性，不是本轮再跑或源到产物完整构建审计。

原result.sourceRef继续是b59239f9c1ec2774c7922f95dfc67db4dc8754e8，按授权原样保留，不能代表新源/产物provenance。需同时保本次授权、固定call/准备、以上新refs/digest/pair；不修改raw求表面一致，也不复用旧结果充003。

nativeDrainCertified=false、fixtureResidual unknown原样保留。preservation列旧001/002与tracked源码/准备/五轮原件不变，本轮只读该owner核验，不扩大重复旧大审计。

## 最终交接核对

已全文读冻结handoff5296B/SHA256 `7e4d05ba52f279a336730f9253c68ea7bda8a05583308eda4829debe32c5bc04`，其授权/一次终态、126B三行及38B新行、来源与旧字段边界、ACL-null定位的有限语义和未知根因/drain均准确反映已核原件。没有从case标签推出函数进入，也未将errno命名推断成根因；无新增问题。

capture-manifest2775B/SHA256 `87c07c2569c6e666601b1fca38511951f9c37937d4169045828f83ea234927e4`；summary4357B/SHA256 `bdbe7c3955508e90175483a82e762b4d28dd3fdc6f3639bdf20636fe8f2383aa`；tool-receipts295B/SHA256 `522548592803c68e17b1d2c143aabb3d9c05c8c5a6f22893ee13ec8349fd7477`。manifest自排除且未改写，本报告是新文件，不倒入旧capture身份。

本轮仅写此报告，最终bytes/SHA交出后停止修改。可关闭本次失败结果封存的独立核对，不关闭根因/完整N0；任何后续诊断、修复、构建或运行仍需另授，不替指定模型外审、CI或父门。
