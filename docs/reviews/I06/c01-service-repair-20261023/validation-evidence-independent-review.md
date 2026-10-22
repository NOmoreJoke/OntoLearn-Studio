# 四路径修复验证证据独立收件审查

结论：本轮指定五组验证的冻结身份、before/after向量、环境、回执标量及双流原件一致，未发现收件阻断。实际stdout分别记载target **2/58/41 passed**、普通check **24 files / 1002 TS passed + 1052 Python passed**、verify **12个归档源**；五组记录child exit0、无capture error/timeout。此为非作者只读核验既有结果，**没有重跑任何验证，也不是产品平台/真实provider/父I06或指定双审通过，不关闭MF01/ZN1。**

## 范围与源身份

只读本轮输出目录 `outputs/20261023_I06_C01_service_repair` 的source-freeze、指定五组receipt/source-before/source-after/stdout/stderr、freeze明确绑定的小输入，以及为确认首失败保留所需原format-check-four receipt/双流。用stdlib作文件、SHA、JSON结构和必要raw文本核读；没有运行候选、runner、formatter、测试、编译、子进程、GUI或任何探针，没有改产品或原件。

source-freeze.json：190075B，SHA-256 `3a4eb291ffccb1dbd3135db6260968a9863c87e185f585bb0362bc94c03553a7`。

- runtimeHEAD始终是 `1f3b053d8a69d1f7ddb1e29c143f648d910fe689` **加未提交的本轮四路径工作字节**。freeze明确 `uncommittedRuntimeBytesExplicit=true`、`productCandidateCommit=NOT_YET_CREATED`；不把稍后产品commit倒填成当时运行HEAD。
- 向量948个唯一path，路径集合精确为source-before-edits的947项加授权新 `tests/unit/i06-mf02-preview-cleanup.test.ts`，新增test恰出现一次。没有以“只比较原tracked”漏掉新test。
- 五组十份before/after JSON都逐结构精确等于freeze.sourceVector；十份原件字节也都为178255B/SHA `f03d0a495f005f085660d5dc48188fa1aa66cb26563df15e7455408decb56970`。
- freeze四路径SHA对应此前最终源独审：service `be3cb0c9…f075098`，新MF02 test `3477be7b…badcfce`，格式后gateway test `e167ab5f…f4eb27`，stored test `2a2b2afc…ab376e`。没有把格式前gateway 09fc…当最终输入。

## freeze绑定实物

逐件重读bytes/SHA均匹配freeze字段：

| 对象 | bytes | SHA-256 |
|---|---:|---|
| independent-four-path-review.md | 8909 | 979f3409d0a76c8534352207f4d519e0abf50811b92024a56f205dbdd504afe4 |
| runner-static-review-r2.md | 6024 | 52b62213132302ff98b12b652fa38816895001c260a16b4cf60e154df55016de |
| independent-final-source-freeze-review.md | 4546 | 037cc3cdb03f2d288f5b9189025782a4c760df67d2e8742935ec21a27fc20032 |
| runtime-plan.json | 7277 | 5f29823dea71d08dc441987965408a90c4e412d091469154a6037a21e5c52b31 |
| runtime-environment.json | 2091 | 843f2c06aed90371644114a7ff77520d1d540eb22c7e922172be2e13a52e6833 |
| run-command.py | 7021 | de1c939e110e923bf9e0363229879af827b7d665d0878c9c83fdd83039e020f2 |

五组环境副本逐结构等于2091B实际环境，receipt环境SHA同值。receipt argv/cwd/operationalWallMs逐项等于最终plan；五组开始/结束顺序符合依赖，记录时长均小于对应operational预算。只核既存文件，不据此声称OS级硬deadline或所有后代已drain。

## 五组原始receipt和结果

五份receipt均为 `raw/<id>/attempt-001.receipt.json`，共同字段：exitCode=0、launchOrCaptureError=null、timedOut=false、captureErrors=[]、retainedHandleCleanup=[]、sourceUnchanged=true、initialFailureRetained=true；runtimeHEADBefore/After均1f3。PID是回执记录的真实Popen子PID，本轮没有重新查询历史进程或扫描PID。

| id | receipt bytes / SHA-256 | actualChildPID | 时长秒 | stdout直接所见 |
|---|---|---:|---:|---|
| target-mf02 | 1729 / ce5794fed08f988ad50b8453c2286094b0c92e7a734f3cfb03501bb5f8932749 | 47698 | 2.139 | 1 file / 2 passed |
| target-zn2 | 1713 / e44ee8225299c7bb8298fad8d5e2014061648d1e25d565dc59c652da31831784 | 48016 | 5.592 | 1 file / 58 passed |
| target-zn3 | 1721 / 5283f6c4fc58892945afb83b52fbe7eb491ee01d201e0ac38b6d4a8db826f5f6 | 48611 | 30.767 | 1 file / 41 passed，含display-name-only新case |
| ordinary-check | 1579 / 5901d1aab8d97b0b676d5b02381549e1b243de506073cee64642e7821a9574e7 | 49454 | 112.226 | lint/format/types、24files1002TS、三段build、ruff、1052pytest完成 |
| verify-sources | 1584 / c62b6770df15e1178f5c045d9e68a26427396a16b5a87f14d5b456bc1d95ce17 | 51817 | 0.293 | 已核对12个归档源文件 |

ordinary-check实际展开命令为原 `lint && format:check && typecheck && test && build && engine:check`；日志记TS全部1002 passed（没有把旧998沿用）、ruff全部checks通过和232files已格式化、pytest1052 passed in60.18s。没有只据receipt0推断这些阶段已跑，已读对应raw footer和展开文本。构建为electron-vite产物生成，不能说启动过Electron/native或已打包运行。

双流逐件实读并重算，全部与receipt中的bytes/SHA一致：

| id | stdout bytes / SHA-256 | stderr |
|---|---|---|
| target-mf02 | 518 / 4a3bf923bd4bf6e6ad38a85a14269c26aa74a475e8ace762925bc0f3243409d0 | 0B |
| target-zn2 | 736 / 557c575c7780536c89b45583d69a1ef6f029ca39f2587e4497a486a405089baf | 0B |
| target-zn3 | 6443 / a8ef399ef75479a2ced25d08ff583f7947e6f65d600c421497b447695e01a7ad | 0B |
| ordinary-check | 18550 / 6f3f7c17a2ebe9815c942c23f036aff4645345e1c4f1ce199a73b3d1764eb22f | 0B |
| verify-sources | 111 / 1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536 | 0B |

所有空stderr SHA均 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。本轮没有重写ANSI日志以求一致，计数从其原始UTF8可见文本读取。

## 首失败、修复与证据边界

原format-check-four首失败仍存在：receipt1902B/SHA `6c6495cde0d949c477ce52dfc2a435385ca41f03a40506e5b5add69d01e5b117`，child1、launchOrCaptureError=null、sourceUnchanged=true；stdout23B/SHA `ebe82dad128d5e5d8936334ceac09492f3c60bd9e0b4a16cc7fd7075513b33de`，stderr122B/SHA `bb6ddd6d2c169f730aad7f43e547ddbe76f7ced744eca9c97d8afecbc85db7c3`，原文只报gateway test格式warn。这是格式首败，不改成一次全绿；后精确格式修复由前份最终静态报告覆盖，不借本次targets0抹掉首败。

MF02两例证明的是已冻结分层生命周期回归（source/repository/credentials doubles）而非真实OS凭据。stored-result41包含既有真实受控Store/worker/HTTPSfixture及displayName新case，不是业务provider或全平台验收。普通check包含原受控I01/I04 stdio/SQLite/worker范围，不因此授N0/addon/native/API/物理研究或真实保存导出。原MF01 P1_OPEN、ZN1 T01 owner缺口、H06/H07原结论和指定同版双审/远端门保留。

这里确认结果收件与输入绑定，没有新产品修正、没有再次运行命令，也没有为收件增加运行门。主线可按原票另作本地产品/证据提交；需保留本报告的“runtimeHEAD1f3+workingfour”事实，不让后建commit覆盖运行时身份。只新增本报告，冻结后停止写入。
