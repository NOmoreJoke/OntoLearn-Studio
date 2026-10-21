# I06 对 T00 格式版本提案的兼容性回执

2026-10-21。仅设计反馈，不是方案批准、路径移交或已实现接口。已全文读回 `iteration-control/2026-10-21-weekly-release/T00-project-format-version-proposal.md`，SHA-256 `c4f32d24367929d137ac49be7c3a8610135116cb70e26340a41864145a1610a4`。版本兼容事实据固定 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6` 核对；其后 `e2c269ad` 仅修App状态提示ARIA，不触协议/项目格式。批准依赖仍为 `5f910b52`，没有采用 T01/T00 或 I05 未批准实现；平台/包内各run保持原来源，验证不因本文重开。

## 判断

支持把 DB3、应用状态子版本、完整 checkpoint/包版本与业务协议3分开设计，并在实施前一次明确同版边界。当前 Project.formatVersion 为 literal 2，engine 的 selectedVersion 类型/hello 及 TS 匹配检查均固定2；只升 Store 常量或只放宽某一端 validator 都不能安全交付。保留同一份 canonical 资源及两端适配器，不新增可漂移的第二套 Project/协议真相。

bootstrap envelope 保留2、只协商业务3是可评估路线，尚未批准。它需要明确 hello 成功/失败的 version/session/hash 绑定分支；不能全局替换数字或让错误 session 通配。旧 App/engine 混版应在可用业务能力前拒绝，不能选2后发送3格式数据，也不能把格式错误吞成空项目。新公共错误如需增加，须先同源目录与 TS/Python 正反例共同冻结，不在本回执发明错误码。

## I06 必须保留的边界

1. **升级是授权生命周期边界。** 受控关闭/升级开始时应先停模型接纳，清除旧项目 context/preview/grant/material 并定向取消 pending，再按 I04 对账/排空引擎；已发送部分不能声称撤回。新引擎完成同版握手、实际格式/结构验证和项目重开后，才建立新 context，默认 local，要求用户重新选择/确认。仅 renderer generation 增长或相同 project UUID 的普通重新读取并不保证撤销，不能把它们当迁移屏障。旧异步凭据录入/确认/发送回调必须因旧 context/version 拒绝，不得在新会话复活。
2. **应用 CAS 与领域输入分开。** 同意 metadata/draft 使用独立 CAS/operationSequence；改项目名、模式或草稿不自动改变 domain snapshot/hash/vector，不制造领域 staleReason。本线材料绑定实际项目、producer、输入/参数/依赖、implementation、字段模型及值。数据库格式号不应被无条件塞进内容 scope；实际读取了 metadata/draft 作为模型输入时，才必须把真实输入及版本计入其范围。旧域 snapshot 与新完整 checkpoint 不可互换，不能因 hash 正确就接受错误种类。
3. **私有模型状态不迁入项目。** 当前密文、configuration journal、metadata-only audit 的私有格式独立于 DB 格式；不能机械随 DB3 升版本。保留历史 audit 原字节与配置/主体关联，不把内部 core configVersion 和公开持久 configurationVersion 合成同一个 UUID。不持久恢复授权；vault/config/audit、密钥、端点凭据、grant/preview 不能进入项目 checkpoint、迁移 backup 或 T10 包。数据库位置/导出覆盖变更时须重新核对实际排除根，不能只沿用旧路径名单。
4. **确认与恢复不重放。** 新 draft CAS、完整 checkpoint、throughSequence 和业务确认身份由 main 的具名接口绑定，renderer 不能提供任意 SQL、方法名、任意模型请求正文/headers 或伪造 scope。升级失败仍保留旧库/证据，不因模型不可用阻断确定性保存；窗口恢复只查询/对账，不自动迁移、重发模型请求或重放写任务。
5. **能力与来源按批准实现绑定。** 协议版本不替代真实 executionSemanticsVersion/producer/field model 校验。I05 新语义及实际字段接点只能在批准合并后绑定重验；当前有限合成 A03 不扩称通用生产 provenance。DB3 中新增的 metadata/draft 不因存在就自动可外发，新增调用能力也不因此进入 Python 模型网关。

## 最小逐路径维护计划

以下只给当前 I06 owner 的未来改动候选；实施前由总控冻结批准方案、精确文件、共同 base/head 与回退条件，不从本表推导其他文件已移交。

| 路径                                                                                                                              | 未来工作与保持项                                                                                                                                                                                                        |
| --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/contracts/v2/schema.json`、`registry.json`、`errors.json`、`fixtures.json`、`binding-regressions.json`                  | 同源定义 bootstrap/业务3、真实 Project 格式及获批新读写模型、受限错误、能力分类和混版正反例；保留 main-only/agentEligible=false 及 session/project/job/结果绑定。目录名是否变更另登记，不能同时保留两份可漂移 canonical |
| `packages/contracts/src/index.ts`、`v2.ts`                                                                                        | 从同源资源同步类型、严格校验/请求响应语义绑定；明确原12个模型主进程方法与 worker 业务协议的归属，不能把全局业务升级变成通用桥接                                                                                         |
| `apps/desktop/src/main/engine.ts`                                                                                                 | 新握手/registryHash/业务信封及混版拒绝；实际旧协调器排空与重开。仍在发送给引擎前拒绝 main-only 模型方法，不把重试扩大到迁移或写操作                                                                                     |
| `apps/desktop/src/main/task-service.ts`、`index.ts`                                                                               | 明确升级关闭/重开状态与实际项目上下文通知；先撤销模型 context，再排空/对账；重开后新 context/local。原 trusted sender/mainFrame/document、单 profile owner、模型失败隔离、退出取消边界保留                              |
| `apps/desktop/src/preload/index.ts`、`renderer/src/env.d.ts`、`App.tsx`、`style.css`                                              | 仅批准的具名方法、格式不兼容说明、真实人类确认、draft generation/CAS 与 stale callback 拒绝；UI 恢复不重放，不回显存量密钥，不自建权威业务状态                                                                          |
| 本线私有 `model-gateway/model-service.ts`、`gateway-application.ts`、`stored-result-source.ts`、必要时 `finite-fixture-policy.ts` | 检查升级生命周期与新公开结果适配；保持完整重读、历史选择、范围并集与定向取消。只有实际批准语义/来源变化才更新模型，凭据/audit 私有格式不随意改                                                                          |

外部配套仍由现 owner 负责：T01 的 `storage.py`；I05 的 `job_store.py`、Python canonical adapter、protocol/coordinator/worker/resources、入口/build/锁/CI。TS canonical 与 Python/engine 必须在同一已定义候选集成，不能只交付一端即让 DB3 对外可打开。确需源码移交时逐新旧路径 ack；T00 当前仅提案，不取得这14文件。

## 批准后最小兼容证据

- 新旧 App × engine × DB 的成功/拒绝矩阵；hello 无交集、混 canonical/hash、旧 session、握手前操作、bootstrap 错误 version/session 均双端同判，拒绝前不获得可用能力。
- 真实生产连接/任务排空、同 lease 迁移；已打开原始 SQLite reader 不会因 user_version 自行失效，须明确不支持并行。逐迁移故障/进程退出由 T01/I05 证明，I06 验证其准确公开错误与本地数据保留，不用 UI mock 代替 Store。
- metadata/draft 提交的域 hash/current 不变、应用 CAS/sequence 正确；旧域快照缺完整 coverage 的恢复拒绝，旧异步回调不能覆盖新 draft 或恢复旧授权。
- 升级前 pending/旧 grant/旧凭据回调在关闭后失效；重开为新 context/local，普通窗口恢复仍只读、不产生新 POST。模型不可用下的真实 Store 提交仍成功。
- 源码与实际包内 executable/engine/canonical 同版，真实不兼容库安全拒绝；T10 有实际导出入口后，再以原件核对凭据/审计/授权排除和导入，不把当前“无入口”当已测。

建议总控先确定版本边界与实际批准依赖，再安排最终同候选指定双审。本线当前正常22项、native4与包内增量分别保存固定来源的事实；不把阶段证明当作新协议3或完整首版通过。本文未运行测试、未改源码或总控状态。

独立只读复核：`/root/i06_interface_docs` 对照固定提案和9fc相关实现，未发现阻断性兼容或责任越界；“正文/headers”已按意见限定为任意模型请求，允许未来具名/schema/CAS约束的合法draft编辑。该复核未执行测试或更改实现，不替代T00总控挑战审查。
