# 诊断002唯一执行：独立结果复核

2026-10-22。只读核对本次已执行结果，不是原因定位、修复或再运行授权。

## 结论

本次失败封存的授权、固定call、pre/post新pair、runtime原件与工具终态相互一致，无新增证据问题。实际结论为 **工具退出1，core正常退出码1，002宿主case失败**；新诊断只将失败收窄到标签为 `metadata` 的测试用例中 owner-create 返回 `NL_UNSUPPORTED` 且 owner非零，不能据此判断具体unsupported原因、OS/ACL/errno或整体native能力。

原件没有被改成通过。owner非零不是成功或drain证据；此前失败根因、目标OS/EXCL全路径、完整N0及父门仍未关闭。不得用本报告授权重试、构建或探针。

## 实际读取及授权身份

已全文读取根 `iteration-control/2026-10-21-weekly-release/I06-N0-diagnostic-002-single-host-CLI-execution-window.md`，与封存authorization-window逐字相等：4073B/SHA256 `d0739abec2a8d4d02843adeccebcaf3a7a566d9fe60ec2f38cd78f71bcc2d4c7`。该窗口明确仅授权1151固定调用一次002，不借用旧001许可；准备JSON内历史PREPARATION_ONLY保持并不代替这份新许可。

固定准备 `1151b8d03cd381100bfc1b1804d3927110621f51`，路径 `docs/reviews/I06/native-location-N0/host-core-run-preparation/diagnostic-second-call/exact-tool-call.preparation.json`。admin内fixed-tool-call副本与该固定Git blob逐字一致：19350B/SHA256 `42b1f04107e3e2404ed79cdaeed4fa0ac80fea093780dafbd4b16352c3615a60`。其cmd为17176B/SHA256 `be0d1fc7518e281353206ec25e43f579dba9821035b46ee3161e76aac7fc2705`，here-doc stdin含末尾LF为16976B/SHA256 `9f6f4b99b63aab6be937617aab7c9dad605a5ab5a54a1b54cfc6c33621d4c2a2`。与窗口、dispatch-intent和summary一致；未另拼调用。

实际读取admin各件、五runtime原件，独立核manifest列出的11项actual bytes/SHA及五runtime当前mode0600；交叉比较授权标识、arguments内pins、runtime argv/pre/post、summary/sourceBinding/dispatch-intent、receipt各字段，均一致。工具参数为本I06绝对workdir、login=false、yield_time_ms=1000、max_output_tokens=1000。未重审旧17KB控制算法或11562报告、历史来源大闭包；没有重读二进制或供应目录。

所有只读命令显式cwd为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0`。仅Git/stdlib数据读取、AST取三个赋值作为数据、hash/字段比较；静态核对命令exit0。未执行候选/native、任何探针、构建或产品检查，未扫/tmp、kill旧PID、GUI、修改Goal或提交。

## 原五输出与终态

| execution-002原件 | B | SHA256 |
| --- | ---: | --- |
| intent.json | 1899 | c90ccd429912cb8b08975586bbe5c6a9153e4d69b9b087005c0f4ccdb3ba50fd |
| postflight.json | 1135 | 8b7d9245e88fe6654462a32548b701a731e12746ce1338b489c547f062e4ac49 |
| result.json | 517 | f0350f684b7c75f872766cdc927d1a8c80e3e69d7de4ad15f49658fd8c1d89f1 |
| core.stdout | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core.stderr | 88 | 1ff7f7a01d47388a0e279da95eabc49f3f1eef45091671421f62d383e970c641 |

三runtime控制JSON合计3551B，各低于64KiB/合计低于256KiB；原双流合88B，各低于1MiB。postflight两流stable=true与实际原字节/hash相符，只是输出快照完整性，不升级为后代/资源drain。

封存工具receipt仅一次exec：初次receipt直接终态chunk38d2d0/exit1/output空，未返回session_id。summary.sessionId=null、continuationCount=0与之相符，不应另造会话号或write_stdin跟踪。dispatchCount=1、retryCount=0；本次不是借旧001的跟踪或重复调用。

原result为corePid88567、waitOutcome=terminal、leaderState=reaped、coreReturncode=1、coreWaitStatus=256、cancelSignal=0、events=[]、processApiRefusedOrWaitUnknown=false、retry=false；summary逐字段相等。256是原wait status，正常退出码为1，不是signal256。未记录超时、组信号或取消；不从空events推导所有后代退出。

记录的waitAndCleanupElapsedSeconds=0.669060584与工具receipt的wall_time_seconds=0.612136333为不同记录字段；不以它们推端到端性能、硬限时或资源drain，也不据该数值推失败原因。

## 两行诊断的有限解释

实际88B stderr为：

```text
N0 owner-create case=metadata status=4 owner_nonzero=1
N0 fixture failure: owner-create
```

只点读真实新源 `fc6237e8cad1a4043d46a1c7198439f1da06ad67` 的ABI64–68行及core_test379–388行：ABI67规定4为NL_UNSUPPORTED；helper打印同次create返回的status及owner是否非零，随后保留原失败cleanup/require。成功require要求status==NL_OK且owner非零，因此此次非零owner不能抵消status4。`metadata` 是固定case标签，不是原生函数名；这份raw没有证明已进入或由 `platform_metadata` 返回。该raw只证明这一case中所观测的owner-create状态；没有记录具体unsupported分支或errno，不能猜ACL、平台版本、环境或native实现根因。未将新诊断当作后续case通过、整个函数成功、部分资源一定释放或实际EXCL验收。

## 新来源与旧sourceRef严格分开

新授权/dispatch明确绑定：I06源fc6237e8cad1a4043d46a1c7198439f1da06ad67，T03输入d98b503ebe9c477d30d0f36d831cffbeeaf2a988、过程d51a0555e6feb062fc935173222cc142687901a5，digest a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77。

runtime intent.preArtifacts、postflight.artifacts、summary.prePostPair完全相等，且其path/bytes/SHA与固定call两pin一致：core343920B/d4f5ca322146d9696860a74de4bee2ad27866a2223340669898fb82cbbfeb817，probe34120B/21928ca2b5570055fad4bebcd81fcb658016ca9a738294397a83056b662b87e8；同dev16777232、ino66596754/66596825。每pass合378040B，低于2MiB。此为原运行前后身份核对的对应性，本轮不重新执行或读实物。

raw result.sourceRef仍是b59239f9c1ec2774c7922f95dfc67db4dc8754e8。授权明确这是未改的历史模板字段，不能代表本次fc新源或新pair；summary与dispatch的独立新来源绑定是必要上下文，不得为求表面一致改raw，也不得把002误贴旧产物/001结果。

`nativeDrainCertified=false`、fixtureResidual unknown原样保留；无残留扫描/删除或旧PID处理。preservation记录旧001及旧tracked材料不变，本轮仅阅读该owner核验，不重复旧矩阵或大审计。

当前capture-manifest2779B/SHA256 `88985e945b2b575f322c28236135ee00cbc44c1981b49fb378aad2745cc6fab6`；summary3809B/SHA256 `43a81612174b1bbb2b30ff06ed17a9f6cbbc5388f4dc3bc5976b9e3c8e990c4c`；tool-receipts295B/SHA256 `04bbfd54dd1a021bbb8324d8ed04884c434a1888ddd566f4734ea9dfdffc28e4`。manifest自排除且未改写；本独审为新文件，不能伪装成原capture内容。

最终补读冻结 `handoff.md`（4687B/SHA256 `f3a27388a12809c334e4a241fdfe60f1d2a50ebc1e0fd638b5b44905796da3be`），其授权/固定call、一次dispatch且无session、tool/core各1、两行原始诊断、pre/post新来源与保留旧b592、未知根因/drain及后续另授边界，均准确反映已核原件。它将metadata限定为case，并未证明进入platform_metadata。其指向的静态候选/writer申请属于主线另行推论与未授权申请，本独审未读取或背书该文，也不扩展原因定位。此步只读handoff，不复测或重读产物。

本轮唯一写入为本报告，不修改原件/receipt或源码。独审仅可关闭本次失败结果封存核对，不替指定模型、CI、目标OS或任何后续根授权。
