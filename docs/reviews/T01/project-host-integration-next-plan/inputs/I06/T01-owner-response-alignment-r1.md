# I06 对 T01 跨 owner 答复 r1 的对接回执

2026-10-21。**接受 §2/§3 的设计方向，没有确认的相反架构决策；以下只冻结 I06 的接受与待澄清输入，不批准 runtime、公共 schema 或跨线写权。** 原 Goal 不自动恢复或完成。本轮没有采用未批准实现、接线或运行产品测试。

## 固定输入

实际从 T01 提交 f51dd38dbdfd2fbb1b9923efee666a19d5b415cc 读取完整 docs/iterations/T01/owner-interface-responses-r1.md，14185 bytes，SHA256 0f3ab7e539b9b69c6a602f4eabd089936a37afd9d842fa836748793031df6768；本回执只回应 §2/§3。其 CAS 产品独立核验由总控继续，本线不将该设计提交视为批准依赖，也未重新探索其未批准实现。

对照本线 eabaf4dba8a36b67266e0753bbc17df255042048 三份既有设计：

| 文件                                    | SHA256                                                           |
| --------------------------------------- | ---------------------------------------------------------------- |
| source-snapshot-transport-decision.md   | 2aeb824987978a83da3e94173c349e816772ffb85700a838d13232ac60239eb8 |
| source-selection-lifecycle-interface.md | 2495c4b371b6bf02519b62d1e3465422795703b4aaa110d2ac3f1dff52264a16 |
| T10-trusted-transfer-response.md        | db29f3a37e281bb83232dd2a18eda0eadfa670ba65b56f25e643b68800ce6b2c |

原固定设计保持原字节；相对名称均在本目录。

## §2：来源分块接受项及精确冻结缺口

| 项                     | I06 对接决定                                                                                                                                                                                                                                                                                                                                          |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 唯一协议与帧界         | 接受同一 canonical JSONL，raw 65536B 分块、8MiB/128块，完整 envelope 按实际 maxFrameBytes 且不提高原 MAX。复用 generic bounded decoder 不构成申请修改 protocol.py/MAX/resources。协商帧容不下 profile 时安全拒绝该能力。                                                                                                                              |
| 两段真实传输           | 接受 T01 明示的真实缺口：现 coordinator 写一帧 parameters 后关闭 worker stdin，worker 只读第一帧；仅 main 分块不能接通。需两段有界状态/背压/绑定/终止合同，worker seal 核完整 SHA/长度后才解析，输出/plan 超帧也必须冻结有界分页/分块；不得在 coordinator 事件循环重解析。该实况来自固定答复，本轮未运行或另验实现。                                  |
| blob 与 source 权限    | 接受在原同库 job_blobs 复用块/manifest 的方向。每个真实 put_blob 值/manifest 均须服从其262144字节界和有限字段预算；version/purpose、project/session/lifecycle/选项、完整SHA、归属与权威登记另核，任意 blob/hash 不升级为 source 权限。不得据复用声明已实现 source 注册。                                                                              |
| preview/确认/Job       | 接受 inspection 无 proof、真实 XLSX 枚举再选 sheet；正式预览、readForCommit 原对象 proof、真实计划/base/人类确认绑定，Job 仅处理已封存快照。未接纳 lease 不跨 session 复活；accepted 输入由原 Job/operation/pin 恢复，不按原 path 重开。                                                                                                              |
| 命名                   | 本线原 mapping.source.* 是候选名，可由 T01 在唯一 canonical 统一命名 source.*；不坚持另建 namespace，不同时注册两套，也不从提案产生可调用 bridge/Agent 能力。                                                                                                                                                                                         |
| 重复 append 的文字歧义 | T01 写“拒绝重复冲突”，未明确同字节重复；本线提案拒绝所有重复 append 并终止未接纳 upload。建议保留本线严格顺序方案，begin 才按原 attempt/descriptor 幂等；append ack 未知先按原尝试对账，不盲补发。若 T01 选择精确同块幂等，须明确全 descriptor/序号/长度/hash/bytes 比较、无覆盖/无延寿及未知对账 fixture，再同步本线文档。当前不声称已存在相反实现。 |
| 仍待 T01 精确接受      | 原 attempt 的 pending begin/取消 tombstone/状态查询与 writer barrier；未真实清理仍计账；全局1 pending begin、2个未接纳 lease/合计16MiB raw及寿命/持久quota；最终实际写帧前同步 guard 或等价 fence；durable bytes 与原 Job/claim/CAS 原子 pin、release/admit 竞争。T01 r1 的“在途/总量/回收”方向相容，但未冻结这些数值、状态或接口，不当作已全盘接受。 |

16MiB只是未接纳 raw 配额。两段队列、base64/副本、worker RSS、解析/展开、结果/plan分页及持久存储各自须有实际预算，不将一个数字当全部内存上限。最终发送前 guard 需 T01 main/engine.ts 与 I06 宿主共同接通；调用前检查不替代排队之后的真实发送切点。

worker.py 的 I05→T01 未来维护权仍在申请，**未生效**；I06 不改该路径，也不将 T01 coordinator/canonical 责任推导成 worker/protocol/resource 写权。精确 owner 生效且同版 schema/实现 ready 后再接线，真实 CSV/XLSX→预览确认→Job→Store 与取消/重启/源包联验仍保留。

## §3：位置 lease、业务闭包与新项目授权

1. 接受固定业务白名单、唯一一致读投影及必需闭包；不复制 DB/userData/整条 claim/context。业务 assistanceAudit 按批准 schema 保真，I06 profile 私有 audit 整根排除，不能按字段名一律删。未选 history/session 与必要闭包冲突时明确拒绝，不暗带或静默裁剪。
2. 接受 guard-before-IO、bootstrap 后实际 handle/parent/member 身份绑定、跨 await/发布前复验及有限清理。完整私有根/密文/静态硬链接别名由 I06 main metadata owner/能力提供；现 excludedRoots 不等于动态 registry。完整 inventory、跨根一致性/退役规则及受控 I/O 能力仍缺，路径复验不宣称原子 confinement。未证明的平台操作保持拒绝，模型初始化失败本身不能被当作私有根为空。
3. engine 附件消费也必须在首次内容 I/O 前取得等价受信、用途限定能力；不向 Python/renderer交私有根清单，不让 Python 按包内/renderer 路径 reopen。来源注册与本节附件能力同 §2 sealed source 合同衔接，具体 source 类型/投影/receipt 尚待同版 canonical。
4. 接受唯一 writer 外层事务建立新 public/internal 身份与正式 import receipt；create_project/application CAS 不是完整 import。主进程核本次 request/profile/项目代次、支持版本、实际新 ID 和明确成功状态，用户实际要求打开后，在最后 await 后重验再 tasks.selectProject(newId, [])。包内旧 ID/job/grant 不是授权；不让迟到 receipt 抢切项目。
5. 新 ID 的现有回调选择 local 新 context、空选择/授权；同 ID select 不清旧授权，不能用于导入隔离。模型尚不可用不妨碍本地新项目保存/打开，后续模型初始化使用当时实际项目。失败或提交不明不切项目、不重放导入/模型请求；真实已提交保留事实，按同 operation/request只读对账。未打开的新项目不自动切换当前 context。

本线六共享及专属 private guard 责任不变；guard候选路径、metadata供应接口和测试范围仍按既有 T10 回应申请，不因 T01 设计接受取得额外共享写权。source.* / diagnostic.* 仍仅提案，未给 renderer/Agent 新入口；语义诊断不由本回执接线或另造错误目录。

X1–X6 与来源全链门未关闭。包格式、完整投影/闭包 JSON、import receipt、安全错误、位置能力及正式版本需同版审定。本轮只格式/diff与独立静态对照，无纯文档触发的产品/平台重测，无当前桌面操作。

## 本轮独立静态复核

/root/i06_design_review 实际读取固定 T01 全文并核原 SHA，同时核对本线 eabaf4d 三份固定设计与本回执正文，确认无阻断。重点核对重复 append 语义未定、两段传输/输出预算、未生效 worker 权属、待冻结数值/状态、metadata/平台缺口以及新项目 receipt/local context；不把方向相容扩大成完整合同接受。未读取未批准实现，未运行测试或修改产品。
