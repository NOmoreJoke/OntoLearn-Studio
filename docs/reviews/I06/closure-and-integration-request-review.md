# I06 终态收口与剩余接口：独立复核

2026-10-21，独立 agent `/root/i06_design_review` 只读核对新增终态/恢复索引及语义、导出、format3消费请求。没有产品/平台测试、Docker操作或重复597/860/243全量审计。

| 最终输入                                                     | SHA-256                                                            |
| ------------------------------------------------------------ | ------------------------------------------------------------------ |
| recovery-index-20261021.md                                   | `401d95f49e53e10f165c1fcbdd85eb14fd0f98ec46f15bf8122fd227a77349f5` |
| evidence/e2c-terminal-root-readback-20261021.json            | `36788e69382b59c47bf2482d95eef580aae02f6967266def817a1c9a356a526c` |
| main-platform/runtime-termination-readback-20261021.md       | `681f650d8ffcabc50d855a4e99731e4b655de1ab1bf46c05813c8592d691827f` |
| main-platform/runtime-termination-readback-20261021.json     | `e52459e9731daaca6a75d08de957b8d919493c8ef913d66e7af6729d9d93ace6` |
| ../../iterations/I06/semantic-export-integration-request.md  | `f69b5ca9c5f66adf3987c72788f70fc42daf48fb83d9047339f3fae7f17baebc` |
| ../../iterations/I06/format3-consumer-integration-request.md | `1e55e54bd9f93d2ff8f8aef0c95b6f28495a1c0eb6ebb9f85802123056adac26` |

实际抽核26个selected原件逐字节等于旧archive对应成员；receipt974…、十门exit/report、唯一retry stats/hash与原receipt及新终态一致，三原inspect和新观察的id/state/finish/exit一致，三原session为final1/0/0。真实retry verified原件与crashed/unresponsive/三窗一致。没有将容器/collector0当全测试通过，也未将工件审计92864中断/69209完成算产品结果；host归档ownership与runtime身份、旧9fc与新e2c边界准确。

语义/导出请求初稿两项文案经实际源码核对后修正并关闭：

- 同次读取/发送准备的预期result/job漂移必须拒绝；合法新result/job/catalog本身不抹掉A03已证明字段scope的grant复用。整结果与字段范围分别核授权。
- excludedRoots集合open时固定，后续private I/O实际重验已登记根；尚未证明的是未来动态export/staging/unpack根及真实export入口，而不是误称现实现只在open检查。

独立复核确认format3消费C1–C6、余六路径改动条件及三个拟新增测试路径均保留待批准/实际owner边界；冷启动、受控同进程升级与普通重连分开，未将未来升级hook条件当作e2c已证实越权。必要源码证实模型服务/结果来源持有readonly engine；替换Supervisor时关联模型服务须安全重建，准确UI诊断的task-presentation.ts是额外路径，须另明确owner。

两项原意见已关闭，无剩余文档审查意见。Linux/SYS_ADMIN/defaultseccomp与跨OS未验说明、真实本地保存/导出组合待验、未批语义/format3不得消费、无安全外审桌面入口的边界均保留。不替代公共接口批准、S3完整联验或指定双审/CI/远端门。
