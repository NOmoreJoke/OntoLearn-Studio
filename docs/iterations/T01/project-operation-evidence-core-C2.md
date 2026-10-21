# C2：同一真实 JobStore3 上的有限 operation 事实读取

这是内部读取核心，不是正式 resolution/恢复或业务权限入口。仅新增 `project/operation_evidence.py` 与专测；52 个继承产品/test 输入全部保持 C1 固定 `423b7e4c799f188cf2ce6e8e7121893ce85624cd` 原字节。指定树从批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 独立采用，adoption 为 `f927f4188fc2d285b405f55ff7ca03f675340af2`。

## 实现边界

`read_operation_evidence(owner, selector, *, maxEvidenceBytes, maxSelectorBytes, maxReturnBytes, readerLimits)` 只接可信 owner 已持有的 JobStore3 和其原连接。selector 精确沿 ff725 合同的 `resolutionVersion:1`；原 request、issued Implementation/Limits 及 original origin 不从当前默认值补造。

在复制/编码 selector 之前逐 scalar 计 UTF-8 canonical 字节、深度和节点。拒未知 caller 活动事务，不回滚 caller。自开一次 BEGIN，全部原 validator 绑定私有 EvidenceView，通过同一连接的固定 SQL gate 读取；成功/失败均尝试自己的 ROLLBACK。没有 Store 子类/第二连接、real._db 替换、动态方法 fallback、写 snapshot、public_project、project_get、reconcile 或业务重放。

原 Store/schema、app catalog、Job3 catalog 与原 ReadLimits aggregate guard 保留。gate 先有限 rowid/类型/长度/NUL/count 探测，再预留 probe work、精确 scalar 费用及完整实际行证据费，之后才物化正文。完整行费用包含所有固定列名及原 SQL typed 值；TEXT 中的 JSON 文本仍按原字符串计算，不先解码重序列化。唯一 `(table,rowid)` 在同 snapshot 只收一次证据费，重复读取工作照收。metadata/SQL 原列值的 UTF-8 与数据库实际 UTF-16 编码分别处理。

批准的固定拒绝界未放大：evidence ≤67108864、selector ≤262144、return ≤131072；probe/read work 各536870912、总 query ≤65536（BEGIN/ROLLBACK 各封存1）。UTF-8 probe 为每 TEXT `256+160*(u+1)`，UTF-16 为 `256+16*(n+1)^2`；SQL 精确费用扫描在预留后执行。未知 SQL 模板安全拒绝，cleanup 不向耗尽的业务额度再次申请。

## 实际核证的关系

创建沿原 `creation_context` 核 claim、真实 origin/seq1 operation/receipt，再用原 `format3.receipt_for` 验至当前 head 的完整混合历史及当前状态；后续名称、域或草稿变化不重算原 createResult。

Job 沿原 `_accepted_job/get_job` 核唯一 operation claim、完整原 request/context/fingerprint/snapshot/parameters/prepared plan。ChangeSet 使用原 `accepted_plan(host=None)`，保全部 segments 和确认 detail 验证，另核原 envelope host/session。普通 Job 原记录未持久化这两项，只返回 `originEvidence:not-recorded`。

终态补核原 helper 之外的关系：始终反查 `rounds WHERE job=?`，包括 run=NULL；有 run 时双向核所有 rounds、连续轮次、实际 snapshot/归属/config blob/原 implementation/progress。合法未开 run 或已开 run 零轮非成功状态保持可读。成功 rounds 核完整 terminal evidence、末轮 pending/consumed 与整个消费 blob；cache 正文存在时再核 summary/audit。atomic 核 marker/commit_evidence、原计划 fingerprint、原 before snapshot、DTO marker 和完整 app history。成功结果双向核唯一 job_results、results 全行、原依赖/manifest/projection/kind/cache_key；payload 行 ID 与 ordinal 各自唯一，receipt/summary/audit 使用 canonical 严格比较，防止 Python `True == 1` 混淆。

真实 `collect_cache` 可使 results.payload=NULL，包括 receipt。此时保留原受理/提交事实，仍核不可变证据，不补正文、不修库。缺 claim 仅 `no-evidence`，不是未受理；坏引用/结构仅 `incomplete-evidence`。SQLite execute/fetch/iteration 错误在旧 ValueError/sqlite3.DatabaseError 包装之前转为独立控制异常，BUSY/LOCKED 与其他存储失败分别映射；资源/存储错误不伪装缺证。cleanup 失败保首因及有限 cleanup_failed 标志。

## 验证与未关闭门

验证采用本树独立锁定环境和真实临时 JobStore3。专项已覆盖真实 UTF-8/UTF-16LE/UTF-16BE 各普通受理、runNULL 和零轮阳性，逐次保存完整 audit ledger，并用独立完整 typed 行 canonical oracle 核证据/probe/query/read 总账。受控 driver 注错不代表真实 OS 磁盘故障；超原 writer 上限的大字段只作明确持久损坏反例，不作合法 Job 阳性。

最终固定产品为 `256b7f1f1abd51b7cabfdfe9fd2e5013f4e8cd8c`（parent 为上述 adoption，仅两个新增 writer）。129 项专项通过；正常 `npm run check` 实际完成 1125 项 Vitest、3098 项 pytest，44 项继承跳过，lint/格式/类型/build/ruff 同命令通过；独立 `npm run verify:sources` 核对 12 件原归档源。独立代码审查的五项 P2 与 cleanup/guard 观察均经真实反例和修订闭环，无未解内部审查阻断。完整原日志、逐件 54 项 manifest、修前源及处置在专属 `docs/reviews/T01/project-operation-evidence-core-C2/`；原早期候选检查不冒充覆盖本最终产品。

没有 GUI/Electron/e2e/native/Keychain/模型/付费/打包、push/PR/merge。该核心只证明所接真实库的局部事实；A→B 复制后也不证明原物理绑定。I06 原 dispatch/位置重证明、当前 read scope、真实 profile/envelope、正式 canonical 路由及恢复供方仍待交付。启动 Store 原全库校验早于本预算，未被本核心解决。父 FR/57P0、双 OS/真人、指定 GLM-5.3 最高和 M3.1-Flash xhigh 同版双审、CI/正常 develop 合并均未因此关闭。
