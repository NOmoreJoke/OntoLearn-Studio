# 004唯一调用结果独立窄审

结论：本次失败归档与授权、固定调用和工具终态一致，未发现需修改本次交付的P1/P2。**004实际失败，不能签ACL remedy运行通过、native drain或N0通过。** 本结论只是新结果证据收件可接受，不是新执行许可或对失败原因的认定。

## 输入与审查方式

全文读取本树AGENTS（15852B/78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759）、根共同指南（17891B/e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0）及本次根执行窗口。窗口实际文件与admin保存件逐字一致：5252B/SHA256 2e5aa0884155a4a4e4b6da38fa97c75c2504d3289e7d51341e44a5bd7eddcf92。

读取本次admin的授权准备、dispatch、原工具回执、pre-dispatch-binding、capture-manifest、preservation及最终handoff；逐件核本次五份runtime原件。仅点读固定产品1217e0f63a9c62b72e01046ef5fbc5c53434251a中测试的失败标签、首case及main调用顺序。使用Git/stdlib JSON、data-only AST字面量和SHA核验，所有shell均显式cwd为本I06树；未执行保存cmd或payload，未运行native、API/ACL/FS或进程探针、编译/npm/check、fixture扫描/清理/kill、GUI，也未重开旧算法/旧运行/构建审查。仅新增本报告。

历史工具执行是由保存的实际入参和原回执核对；本审查没有再次执行来“复证”一次性行为。preservation关于旧原件未改/无额外行为的全量历史声明未重新大审计，不能由有限文件读取证明系统全部行为不存在。

## 调用、来源和终态

固定准备e85ae88815e45aa336850b594910a524a073cc00的exact-tool-call.preparation.json Git blob与authorized-preparation.original.json逐字一致：19614B/8f9788b64b721ad60a8a1c5bf4a72287dd2519d6fcdedc82f5b681e1a8adb739。其arguments与保存的exec_command实际arguments完整相等，包括cmd、绝对workdir、login=false、yield_time_ms=1000和max_output_tokens=1000。

独立实算cmd为17176B/100ebd1ae0a8f43608146565b95d145503e014b87beaccb53182fbc5115d8781；按固定heredoc分隔提取的实际stdin含末LF为16976B/5a3fb0e4b6e273ca20c76f7ddb0567fcd0f2ce75baed151722e6b7dbebd7db92。仅以AST读取AUTHORIZATION/CORE_PIN/PROBE_PIN字面量，未执行代码；record与intent/result/manifest一致。

- 初次exec回执chunk80f169返回session66633、空output、尚无exit_code。保存的唯一后续调用是对66633的一次空write_stdin；终态chunk7b6031、exit_code=1、空output。没有第二个exec dispatch记录，也没有把session继续跟踪算作第二次native执行。
- result原件明确corePid=58416、coreReturncode=1、coreWaitStatus=256、waitOutcome=terminal、leaderState=reaped、dispatchAttempted=true；cancelSignal=0、events=[]、processApiRefusedOrWaitUnknown=false、retry=false。与capture-manifest逐值相同。
- status的通用标签FAILED_CORE_NONZERO_OR_SIGNAL与非零退出相容；本轮具体事实是coreReturncode=1，不能借通用标签声称遭信号终止。工具exit1和core exit1分别保留，没有将控制收尾成功/leader已收转换成测试成功。
- waitAndCleanupElapsedSeconds=1.138704792仅原控制字段，不代表完整工具耗时、硬时限或性能保证；15/1/2秒、构造无硬deadline及原预算均保留，没有发生timeout/取消信号收口的记录。

实际来源另绑I06产品1217e0f63a9c62b72e01046ef5fbc5c53434251a/过程9509d02790f9a79905371c5183be16cab99f5114；T03输入bfe137f371361f9fda446d5cbe6b3079c5433ee5/过程37fe056e5d1716a10237de20f79042db54aa0549；digest1526093e58aeaa43cd5c96dfc911dd032759df27c039bf3d11eacfb1e6cbfd50。pre-dispatch九源bytes/SHA与固定1217 Git blobs逐项一致。raw sourceRef=b59239f9c1ec2774c7922f95dfc67db4dc8754e8只是保留的历史模板字段，不是当前来源；本审不改写raw，不复审供应构建链。

## 原始流、pair与预算

本次五件实际bytes/SHA与capture-manifest逐项相符，当前权限均0600：

| 原件            | bytes | SHA256                                                           |
| --------------- | ----: | ---------------------------------------------------------------- |
| intent.json     |  1899 | 597078793508fd5d7515b83efba0d392310a492ab7d5f72c734a10062aa73cab |
| postflight.json |  1135 | 547c8dd40a709a30c323f4abf186b8a3f41d2a53816e477010aa3e7b9b88d2a3 |
| result.json     |   517 | 834187b98d7266fdf71764bf32ea0b8fabf72bf417df76c12c831fd3029dc72e |
| core.stdout     |     0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core.stderr     |    41 | 0eebce381ace03e8f0650636b4aff2d25cb0f209e3fdb7a9e54d5c494cf41126 |

三控制件共3551B，各低于64KiB、合低于256KiB；双流0/41B各低于1MiB。postflight的两流bytes/hash与当前原件一致，stable=true仅快照稳定。stderr逐字只有下列一行（含LF共41B），无新增平台stage/errno或owner返回信息：

```text
N0 fixture failure: acl-witness-envelope
```

intent.preArtifacts与postflight.artifacts完整相等，其path/bytes/SHA与固定call的两pin相符。core为362656B/17fb8b48ec3e79cfd36015edc4047bbd390ac0145dd2c40b1c20850455771f60，dev16777232/ino66899292；probe为34120B/5b9978c2e7bbb8d3ee51d3d94d95ab4797ac01337654180cf121d89dc3e05b98，dev16777232/ino66899299；每pass合396776B，在2MiB内。本轮只核保存的pre/post及pin，没有再查询供应实物、执行probe或扫描fixture。

## 能证明的到达点与限制

固定测试location_core_test.cc:425–442中，read_acl_fixture先完成fresh对象、同FD fstatx、OWNER/GROUP/MODE getter及scalar安全一致性require，再完成UUID与GRPUUID两次query返回码检查；441行的owner_uuid != 0 && group_uuid != 0失败，触发本次标签。按此控制流，**至少一个presence结果为0，原流未区分是哪项，底层原因未知**。这不是ACL absence证明，也不证明短envelope、NULL/ENOENT、缺路径或installed libSystem具体实现。

442行ACL presence query位于失败之后；511–518行首empty case先read_acl_fixture再创建owner；main:729–733先调用darwin_acl_cases再原cases。因此本轮未到首empty owner创建/root metadata核验及empty proof输出，未实际验证生产metadata remedy路径；one-ACE setup/见证/DENIED、invalid-FD以及原metadata/child/partial/concurrency/budget均未到达。stdout为空、没有完成footer，与该顺序一致。不能把fixture见证失败当DENIED负例通过，不能签P1明确absence或P2自然present-empty，也不能据此放宽安全门求绿。

nativeDrainCertified=false、fixtureResidual=unknown; not scanned/deleted据实保留。leader已reap/流稳定不证明自然EOF、所有后代或fixture资源释放；析构尝试不是清理成功回执。不追认001/002/003的到达点或根因，不释放旧未知票。目标双OS、完整N0/父功能、指定同版外审、CI/真人/远端及其他既有门未因本次结果关闭；无新诊断、修改或重跑授权。

## 最终交接核对

已读冻结handoff：6065B/9beaa895f5f2279c7ab42d3da48090aed814d1ebbc057399a763033d47e2f3f7，其失败、未到达生产路径及未知残留表述与原件相符。其余本次关键admin pins实算：capture-manifest 3540B/fb6a1418b745d906585af92d44cd112bbda386160eccdd5518e5521cafb23b60；tool-dispatches.original 18267B/5cd2714d404969d6906fb81e408243f79b6744dc4643d417812264b2f6107a28；tool-receipts.original 337B/e573c8760494271589e1c33fba4e0f93d78e4b6a67ac12d7a5d328d1acce3174。

本次窄审没有新增阻断交接的问题；实际运行失败及未验证项保持未关闭。报告定稿后停止，不修改原件或发起后续调用。
