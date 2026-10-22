# 004精确一次执行：失败收件

本次工具终态与core均退出1，**FAILED_CORE_NONZERO_OR_SIGNAL**。仅按固定e85ae88815e45aa336850b594910a524a073cc00的JSON.arguments dispatch一次；收到session66633后只跟同session一次，已终态。没有重试、源码变更、再编译或额外ACL/API/FS探针。停止执行，保留失败原件。

## 授权、调用与真实来源

执行前已全文读取并保存根窗口原字节：I06-N0-diagnostic-004-single-host-CLI-execution-window.md，5252B/SHA256 2e5aa0884155a4a4e4b6da38fa97c75c2504d3289e7d51341e44a5bd7eddcf92。最新本树AGENTS/common已全文读取；特定一次CLI窗口覆盖旧通用native禁令，仅限该组件调用及明确fixture范围，不扩大到GUI/addon/产品启用或额外查询。

authorized-preparation.original.json是固定准备原JSON（19614B/8f9788b64b721ad60a8a1c5bf4a72287dd2519d6fcdedc82f5b681e1a8adb739），其PREPARATION_ONLY/false保留当时历史，不改raw追认。实际工具入参另存tool-dispatches.original.json，与其arguments逐值相等。cmd17176B/SHA100ebd1ae0a8f43608146565b95d145503e014b87beaccb53182fbc5115d8781；stdin16976B/SHA5a3fb0e4b6e273ca20c76f7ddb0567fcd0f2ce75baed151722e6b7dbebd7db92。workdir原I06绝对树、login=false/yield1000/max1000原样，无wrapper或环境/timeout变化。

真实I06产品1217e0f63a9c62b72e01046ef5fbc5c53434251a/过程9509d02790f9a79905371c5183be16cab99f5114；T03输入bfe137f371361f9fda446d5cbe6b3079c5433ee5/过程37fe056e5d1716a10237de20f79042db54aa0549；digest1526093e58aeaa43cd5c96dfc911dd032759df27c039bf3d11eacfb1e6cbfd50；record I06-N0-execution-004-1526093e58aeaa43。raw result.sourceRef仍为b59239f9c1ec2774c7922f95dfc67db4dc8754e8的历史字段，不能当新来源，未改写。pre-dispatch-binding/capture-manifest另绑定上述来源、窗口、准备/cmd和实际pre/post。

## 工具终态与原始记录

- 初始exec_command chunk80f169，session66633，输出空，尚无退出码；仅一次write_stdin跟踪该session。
- 终态chunk7b6031，exit_code1、输出空，无后续session。不再poll或dispatch。完整结构回执保存于tool-receipts.original.json。
- corePid58416，coreReturncode1、coreWaitStatus256、leaderState=reaped、waitOutcome=terminal；cancelSignal0、events空、processApiRefusedOrWaitUnknown=false、retry=false。原waitAndCleanupElapsedSeconds=1.138704792仅该等待/收尾字段，非端到端硬wall或性能证明。

新raw仅在host-core-run-preparation/execution-004，五件原始字节和实际0600权限保留；入库理由是固定一次执行的首失败审计原件，量小且无业务数据/凭据。capture-manifest给逐文件bytes/SHA：

| 原件            |    B | SHA256                                                           |
| --------------- | ---: | ---------------------------------------------------------------- |
| intent.json     | 1899 | 597078793508fd5d7515b83efba0d392310a492ab7d5f72c734a10062aa73cab |
| postflight.json | 1135 | 547c8dd40a709a30c323f4abf186b8a3f41d2a53816e477010aa3e7b9b88d2a3 |
| result.json     |  517 | 834187b98d7266fdf71764bf32ea0b8fabf72bf417df76c12c831fd3029dc72e |
| core.stdout     |    0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| core.stderr     |   41 | 0eebce381ace03e8f0650636b4aff2d25cb0f209e3fdb7a9e54d5c494cf41126 |

三控制记录合3551B，在原每件64KiB/总256KiB内；双流0/41B在各1MiB内。stderr仅一条固定41B行（含LF），未输出路径/FD/PID/UUID/owner身份：

```text
N0 fixture failure: acl-witness-envelope
```

pre/post两产物path/dev/ino/bytes/SHA全部一致：core362656B/17fb8b48ec3e79cfd36015edc4047bbd390ac0145dd2c40b1c20850455771f60、dev16777232/ino66899292；probe34120B/5b9978c2e7bbb8d3ee51d3d94d95ab4797ac01337654180cf121d89dc3e05b98、同dev/ino66899299。这里只读回原控制记录，不在调用后额外查询产物/fixture或进程。输出stable是快照，不是自然EOF或全部后代drain证明。

## 实际覆盖与未解决限制

仅为解释新固定标签，定点核固定1217测试源码顺序：第一个empty fixture先read_acl_fixture，OWNER/GROUP/MODE成功及安全一致检查后，两UUID query成功，再要求两presence均非零；本标签表示该合取不成立，**至少一个presence为0，无法由此区分哪一个或解释底层原因**。紧随其后的ACL presence query尚未进入，empty owner创建在helper返回之后，本次亦未进入。未新增查询查明缺少哪项，不放宽见证求绿。

所以本次没有P1明确absence、P2自然present-empty或生产metadata新路径的实际验证；stdout无empty证明行。one-owner ALLOW ACE的setup/见证/拒绝、invalid-FD及其后原metadata/child/partial/concurrency/budget均未到达，没有完成footer。不能将setup/见证失败当DENIED安全负例通过，也不能以此证明生产metadata返回了某状态或remedy已修复。原构造器setup已在此次授权范围内，析构尝试不等于清理成功签收。

nativeDrainCertified=false，fixtureResidual仍unknown; not scanned/deleted。仅leader已reap，不证明所有后代或残留已释放；不扫描/tmp、不定位/删除fixture、不杀旧PID。001/002/003和旧五轮只按固定Git父链保留，003仍失败，不倒填其根因/阶段或释放旧票。

公开实现仍非installed libSystem身份；短envelope/fresh未填、allocator/query/get/free错误、未知ownership及内部heap/系统调用/wall硬界未关闭。EXCL全路径、目标双OS、完整N0/父功能、双指定同版外审、CI/真人/远端门保持；T01 wholeH/SQLite损坏输入保护HOLD及已拒资源分析线继续停止。

九源及AGENTS保护指纹保持，未改源码/锁/旧准备/旧运行或Goal；未做无变化npm/source复测。独立agent仅审本次结果及上述范围，报告independent-result-review.md；有限manifest排除自身，固定本次过程ref在提交后交root。归档完成后停止，任何后继调查/变更/运行须由总控另给精确窗口。
