# 诊断003：唯一执行结果交接

**执行失败，已停止，无重试。** 工具/core均正常给出退出码1，首次receipt已终态，没有session或continuation。新诊断实际观测到 `stage=acl-null errno=2`；对应当前Mac源码中acl_get_fd_np返回nullptr的分支，随后owner-create仍为NL_UNSUPPORTED/owner非零。具体为何返回null仍未知，errno数值不证明空ACL、缺路径或其它底层原因。

## 授权、固定调用与来源

本目录 `authorization-window.md` 为执行前保存的根批准文原字节：3760B/SHA256 `d1570b0958caf4a5dc48601f42547bda1530c6cdfdc27027709ed09d7f01b6db`。执行前已保存dispatch-intent；record为 `I06-N0-execution-003-0d5223985fcd9761`。

仅从固定准备 `5b78098ae8b53168fc23ec7499f240d1ede3f1c6` 中 diagnostic-third-call/exact-tool-call.preparation.json取完整arguments，原样交exec_command一次。没有拼cmd、添加wrapper/env/timeout或改参数。固定原JSON副本为本目录 `fixed-tool-call.preparation.json`：19615B/SHA256 `4c14304e4e4be6b041f60596aa581ed277af40e79d4499f9d2e8bf9e38d8cbe5`；cmd17176B/SHA256 `ed84b73de7178ba8340843ed54b63d6cf45e6f683074833ad1f4a356df3aede3`，stdin16976B/SHA256 `a67944783c48d1fb0e888d1ce6991665873881a482a91a6673c979425c8c07d1`。

真实I06产品 `fc9853f3521faced3a3b88ab8254310c9748a6a6` / 过程 `6fda0648299ae7e7d7d049ad5852e6d61b1618c5`；T03输入 `0514d37e32e31ae569e583bb56ec225ebc0483e6` / 过程 `8528ccb3d68de4f31ee1e10bd984084e0f7f418c`，digest `0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb`。core344096B/65cca109ce2a43b24c94fc013b5e91127548d4be3d39de5330024128ffdb8039、probe34120B/12d355d3cc43fc5c39b6e8689d7e0dabb6909b8dfd7a7deed6322f3351d80e48；完整path/bytes/SHA/dev/ino在实际intent与postflight完全一致，与固定call两pin相符。

raw result.sourceRef=b592按原授权不改，仅为历史模板字段，不能代表本次provenance。真实新来源以本授权、以上refs/digest/pair、完整cmd及固定准备共同绑定；不改raw求表面一致，不复用旧结果。

## 实际终态与原双流

exec_command初receipt：chunk_id=`e76c7f`、exit_code=1、output为空、无session_id。一次dispatch、零continuation、零write_stdin、零retry；完整工具返回对象保存在 `tool-receipts.json`。

corePid12206，waitOutcome=terminal、coreReturncode=1、coreWaitStatus=256、leaderState=reaped；cancelSignal=0、events=[]、processApiRefusedOrWaitUnknown=false。没有timeout、取消或TERM/KILL收口。waitAndCleanupElapsedSeconds=0.722300709，只是原记录自己的时间范围，不作完整wall/性能或资源drain结论；不以tool receipt的wall_time_seconds替代该字段。

原五件位于 `../host-core-run-preparation/execution-003/`，实际均0600：intent1899B、postflight1136B、result517B（控制合3552B），stdout0B、stderr126B。两流postflight均stable=true且实际bytes/SHA吻合；stderr SHA256 `f508e845a5ee83f12edcd0a2d0a1456f78124530b167538cea7755ae0a21c74f`，全文：

```text
N0 unsupported stage=acl-null errno=2
N0 owner-create case=metadata status=4 owner_nonzero=1
N0 fixture failure: owner-create
```

三行含LF分别38/55/33B；新endpoint诊断行实为38B，在96B上限内。这是本轮实测输出，不将此前49B格式上界当实测长度。

## 可据原件得出的有限定位

固定fc9853 platform_macos.cc:101–106只在acl_get_fd_np(...ACL_TYPE_EXTENDED)返回nullptr时，立即捕获errno并记录acl-null，然后返回原NL_UNSUPPORTED；helper:23–25写后恢复该errno。因此003已实际走到这个ACL query null终点，读取到的快照为2。只点读对应源码解释日志，未新增ACL/OS查询或API探针。

`metadata` 仍是测试case标签，不是平台函数名；本轮进入platform_metadata的证据来自独立的acl-null终点行，不能只据case标签判断。status4为NL_UNSUPPORTED，非零owner不满足成功条件。没有底层调用trace/额外query证明为何null，不能把它当空ACL/缺失路径或选择某个假定根因修复。

001/002旧raw没有这个终点诊断，不能倒填它们已走同一分支。此次失败不证明后续case、EXCL、目标OS或完整N0通过；nativeDrainCertified=false，fixture/后代残留仍unknown。leader已reap与输出快照稳定不等于自然EOF、后代排空或旧资源票释放。

## 归档与保持

`capture-manifest.json` 有限覆盖原五runtime及六件admin来源/工具/摘要/保护记录，排除自身；`result-summary.json` 为可读摘要，不能替代或修订原件。最终 `manifest.json` 有限覆盖本次新资料及原五件，排除自身。独立结果报告为 `independent-result-review.md`，仅核此次新结果/范围，不重审原算法、旧长报告或五轮构建大包。提交号由最终回复给出。

`preservation-check.json` 记录相对固定准备的tracked差异只有AGENTS原WIP，旧源码、准备、001/002和五轮原件均未改。没有重试/第六构建、源码或限额修改、OS/FS探针、SQLite/资源接口被拒线重启、扫描/tmp/清理未知fixture/杀旧PID、GUI或Goal变更，也没有push/PR/merge。后续诊断、修复、构建或运行均需另授；本次按失败stop边界仅完成封存与结果审查。
