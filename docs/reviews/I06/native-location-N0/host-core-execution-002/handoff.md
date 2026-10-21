# 诊断002：唯一执行结果交接

**执行失败，已停止，无重试。** 工具和 core 实际均退出1；本次新诊断将当前失败定位为 metadata case 的 owner-create 返回 `NL_UNSUPPORTED`（status=4），且 `owner_nonzero=1`。具体为何 unsupported 仍未知，不能从该状态反推 OS/errno/ACL/权限根因，也不能把非零 owner 当成功。

## 授权、调用和真实来源

本目录 `authorization-window.md` 为根批准文原字节，4073B/SHA256 `d0739abec2a8d4d02843adeccebcaf3a7a566d9fe60ec2f38cd78f71bcc2d4c7`。执行前已保存授权及 dispatch-intent。record `I06-N0-execution-002-a0e724fdf90afa98` 仅本窗口一次有效。

只从固定准备 `1151b8d03cd381100bfc1b1804d3927110621f51` 的 exact-tool-call.preparation.json 取原 arguments 交 exec_command 一次，没有拼接 cmd、添加 wrapper/env/timeout 或修改参数；完整固定调用原件见本目录 `fixed-tool-call.preparation.json`，19350B/SHA256 `42b1f04107e3e2404ed79cdaeed4fa0ac80fea093780dafbd4b16352c3615a60`。cmd17176B/SHA256 `be0d1fc7518e281353206ec25e43f579dba9821035b46ee3161e76aac7fc2705`；stdin16976B/SHA256 `9f6f4b99b63aab6be937617aab7c9dad605a5ab5a54a1b54cfc6c33621d4c2a2`。

实际源：I06 `fc6237e8cad1a4043d46a1c7198439f1da06ad67`；T03输入 `d98b503ebe9c477d30d0f36d831cffbeeaf2a988` / 过程 `d51a0555e6feb062fc935173222cc142687901a5`；digest `a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77`。core343920B/d4f5ca322146d9696860a74de4bee2ad27866a2223340669898fb82cbbfeb817，probe34120B/21928ca2b5570055fad4bebcd81fcb658016ca9a738294397a83056b662b87e8；固定调用及实际 intent/postflight 的完整绝对path/pins一致，dev/ino也一致。

原 result.sourceRef=b592 保留不改，它只是历史模板字段，不是本次源/产物身份；真实来源须同时使用以上refs/digest/pins、固定call/准备ref与本次授权，不能改写raw以求表面一致。

## 实际终态与原始输出

exec_command 首个 receipt 直接给 exit1，chunk_id=`38d2d0`，output为空，没有 session_id。仅一次 dispatch、零 continuation、零 write_stdin；没有新 session 或重复提交。完整工具返回对象保存在 `tool-receipts.json`。

corePid88567，waitOutcome=terminal，coreReturncode=1，coreWaitStatus=256，leaderState=reaped；cancelSignal=0，events=[]，processApiRefusedOrWaitUnknown=false。没有 timeout、TERM/KILL 收口或 retry。私有控制记录 waitAndCleanupElapsedSeconds=0.669060584，仅该字段自己的时间范围，不是完整wall/性能指标，也不以工具receipt的wall_time_seconds替代它。

原五件位于 `../host-core-run-preparation/execution-002/`，实际均0600：intent1899B、postflight1135B、result517B（控制合3551B）；stdout0B、stderr88B。两条流postflight均stable=true，各自大小/SHA与实际原字节一致；stderr SHA256 `1ff7f7a01d47388a0e279da95eabc49f3f1eef45091671421f62d383e970c641`，全文：

```text
N0 owner-create case=metadata status=4 owner_nonzero=1
N0 fixture failure: owner-create
```

固定ABI location_abi.h:67定义 NL_UNSUPPORTED=4；location_core_test.cc:379–388 的原 make_owner 在非OK或零owner时输出该诊断，非零owner失败路径保留原cleanup分支和原require。这里只有状态与布尔值，没有 errno 或底层分支证据。002不改变001当时只有通用标签、phase/status未知的历史；不倒填001结果。此失败不证明后续case、EXCL、目标OS或完整N0通过，native drain和fixture残留仍unknown。

## 归档与保持边界

`capture-manifest.json` 有限覆盖五件runtime原件与六件admin来源/工具/摘要/保护记录，排除自身；原始文件未格式化、截断或替换。`preservation-check.json` 保留旧001五原件current==固定Git、旧tracked源码/准备/构建证据不变及AGENTS保护指纹。最终 `manifest.json` 以有限清单引用本目录与上述原五件，排除自身。

独立 agent 仅核此次真实结果，报告 `independent-result-review.md`；没有重审旧控制算法、API报告或构建历史。总控随后要求的最小静态候选与下一单文件诊断writer申请见 `static-candidates-and-writer-request.md`：四个候选终点，现有raw不能唯一定位；该申请未授权、未实施。最终过程ref由提交后回复给出。

本次未重建、启动GUI/Electron/addon、重跑API/FS探针、扫描/删除未知fixture、杀旧未知PID、改源码/Goal、push或PR。失败后停在原件归档；任何修复、新构建或后续运行须另授。Mac15/Win11、EXCL全路径、父N0/功能、指定同版双外审、CI和真人/远端门保持未关闭。
