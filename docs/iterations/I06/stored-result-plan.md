# I06 既存结果与有限字段实施记录

2026-10-21；本页对齐固定开发提交 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6`，批准依赖仍为 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`。原 `4ace4c4`/`1911ce1` 整结果阶段记录与 source-bound 失败/验证原件保留；本页更新当前接口，不重写历史证据。完整状态由 [status](../../reviews/I06/status.md) 维护。

## 实际来源与选择

`StoredResultSource(engine,mainProjectId,producerPolicy='runtime-only')` 固定 supervisor/项目，只用批准 project.get/result.get/job.get/result.page，复用严格 V2 校验及 allowedProjects；不直接开 SQLite 或新增 RPC。逐项核对成功 producer/job/resultRef、输入/参数/定义/依赖/执行版本、current/historical 与 payloadStatus；完整固定分页、顺序/重复/循环/行字节上限检查后重读 result/job/session。任何失败丢弃片段，evicted 不重算冒充历史。

`load({resultId,selection},signal?)` 返回 main 复制的 metadata/bodyText/bodyHash/sourceFingerprint；正文包含真实整份 metadata+rows，hash 仅用于一致性。`GatewayApplication.selectStoredResult` 签发 whole-result 材料并返回实际 rowCount/byteCount。公开 `selectModelResults` 批次成功才替换，失败释放新临时材料保留旧选择；选择替换/清空会定向取消依赖旧来源的活动调用。

来源加载每实例最多 4 项，单次和整批重读各 5 秒预算；固定 64 行/页、最多 64 页/1024 行，整份实际 UTF-8 64KiB，超限拒绝不截断。选择与读取检查不授予外发；默认 local，预览真实范围后仅用户明确确认签发 grant。发送再重读完整来源，core 发送边界重检授权、配置/凭据和实际材料。

PRD D/F 已允许显式不可变历史选择，无需再次产品批准。展示实际 result/input/version、读取时 state、历史身份；检测到 current 变化保守拒绝，不静默降级 historical。最后异步读回与 socket 间存在跨 Store 观察窗口；只发送已核验所选版本副本，不声称发送瞬间仍 current。原 FR-902/S3 不要求跨全部写者/socket 原子 lease；仅新增更强持续 current 承诺时另审。

## 有限字段实现与 A-03

`StoredFieldProjector` 在实际 load 的结构化 rows 上应用可信 main 固定模型。模型精确绑定 producer/definition/kind/implementation/tag/全字段宽度，最多 16 个平坦 scalar 字段，复制冻结完整 policy，验证索引/键唯一及依赖无环并取传递闭包。未知/嵌套/不符形状拒绝。`getFieldCatalog` 对应公开 `getModelFieldCatalog` 返回 1–16 个 `{fieldId,label,type,nullable,requires}`；`selectFields` 对应公开 `selectModelFields` 仅收 main 签发 ID，重读来源并要求依赖闭包，返回实际投影 hash/行数/字节数与展示字段描述。

catalog 绑定具体 result/job/完整副本；授权 scope 另绑定完整模型 digest、项目/producer/定义/输入/参数/依赖/精确执行版本和实际有序字段值/行身份，允许第二个同源且授权字段未变的真实 worker 结果复用原 grant。最终 body 只含选中字段和允许来源摘要；用投影密集 ordinal 替代原 rowUUID/ordinal，不含未选列/派生值、完整输入/参数 hash。tool/history/summary/error 仅重建允许投影，任意 text 无法证明来源就拒绝；完整来源祖先释放取消后代调用。

当前有限模型是固定 main 合成 policy，来源是批准 test.read echo worker，privateDerived 值由合成夹具准备，dependsOn 为静态 policy，不能说成真实业务语义派生或通用生产溯源。普通生产 fieldModels=[]/runtime-only；index 只在既有可信 main 绝对 path+同值 env 的 unpackaged/test-runtime launch fixture 开启有限策略，不能由 renderer、result tag 或公共参数选模型。当前批准业务 producer 仍 design-only；不采用 I05 未批准 C1/C2 或固定其旧 executionSemanticsVersion 为最终生产来源。

原 A-03 是授权选中字段后工具返回其他列，其值及相关派生值不得进入下一次实际模型请求。有限真实 Store/worker+main 模型/投影+receiver 全 bytes 可以证明 M0 有限要求；不要求 M1 全 CSV 单元格溯源、恰好两个 API 或 I05 编号前置。whole-result/hash/random scope/self-label 不能替代。I05 特定实际材料在其新语义批准合并后另绑定与重验。

## 文件责任、验证与后续接线

根线持有 model-gateway 实现/真实来源测试及总控正式交接的精确 14 共享文件；契约、平台、文档、只读审查分别在独立 worktree 按任务唯一文件责任推进。Python Store/job/worker/protocol、build/锁/CI/CSP/恢复不在交接范围。此文档线只写 narrow-interface-draft/examples、main-integration-handoff、stored-result-plan 与自身对齐检查，不改 root、实现、状态或控制文件。

整结果阶段 [manifest](../../reviews/I06/evidence/stored-result-20261021.json) 与 [内审](../../reviews/I06/stored-result-review.md)、有限字段阶段 [manifest](../../reviews/I06/evidence/finite-fields-20261021.json) 与 [内审](../../reviews/I06/finite-fields-review.md) 按原源码 hash 保留。字段阶段真实 Store/coordinator/worker、原 grant、四种投影、完整请求字节断言、UUID/ordinal 零泄露与祖先释放取消/零 POST 有原执行记录；独立 probe 未归档成功 HTTP 原正文，不能声称独立重扫归档 body。后续正式平台测试保存仅合成完整 receiver body 和 hash 于测试忽略证据，不保存 headers/真实 key/业务数据，不进入产品日志。

本次实际检查仅同版四个 contract validators、原 35 例 ID/5 场景 ID 保全与文档格式，见 [对齐检查](../../reviews/I06/interface-alignment-review.md)。根线已有 998 TS/1052 Python/check/source12 回执按固定源归属，不由本页冒充复跑。新 main/preload/UI/safeStorage/Linux 平台线正在准备，其他平台和真实窗口/保存/日志隔离、完整 S3 同版指定双审/PR/CI/远端合并由 status 跟踪。无当前导出入口即无该项实际导出测试，不能发明 mock 通过；Q9 provider 选择不因合成链冻结。模型初始化失败隔离、单 profile owner、5 秒退出等待及严格 UTF-8 响应已接入代码，运行结论必须由新平台证据支撑。
