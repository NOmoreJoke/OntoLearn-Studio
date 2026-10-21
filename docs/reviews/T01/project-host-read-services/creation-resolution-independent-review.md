# 项目创建与只读 resolution 合同独立审查

结论：修订合同 `ff725f2c…a5f3` 已在合同层关闭两项 P2，当前无未解决的合同阻断，可交根作下一次精确审批输入。原问题和证据完整保留如下。创建、resolution 和位置能力仍未实施或授权；本报告不把提案、静态推演或待实施用例当作运行验收。

## 受审输入与职责

审查者为独立 agent `/root/creation_contract_audit`；未参与合同编写。唯一写入路径为本报告。不修改产品、测试、合同、共享规则或其他报告，不 stage/commit、切分支、推送，不运行产品、全套测试、构建或 GUI。

本次全文读取并逐字核验：

| 输入                                           |  字节 | SHA256                                                             |
| ---------------------------------------------- | ----: | ------------------------------------------------------------------ |
| 本树 AGENTS.md                                 | 15852 | `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` |
| developer-common-instructions.md               | 17891 | `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0` |
| 精确实施授权                                   |  7435 | `0c96119b2038b1db0d74fc8466926f321c7ebee669cb8949876e417c9e580757` |
| 初始 project-create-and-resolution-contract.md | 30208 | `d2d469acdc401f01fec3269647fcdeefb66dc0ca2ddfbf0717f663508f410675` |

工作树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-host-read-services`。产品语义只依据固定 `5de3fff8aa02c5d6e577938660e9362936d90550`，未用本树 HEAD 的 5f 旧实现冒充 48 继承组合。以下必要源码用 `git show 固定SHA:路径` 读取，并实际比较当前文件字节相同：

| 固定源码                     |  字节 | SHA256                                                             |
| ---------------------------- | ----: | ------------------------------------------------------------------ |
| storage.py                   | 75257 | `2f8762aef48279f5d2e05fa8e27015e04a911f4fdc0748586570d194ff090776` |
| job_store.py                 | 86648 | `e40e75f28cb238575a122a35e38d108a264bddebe507cbd6d5010cb113385ad4` |
| project/format3.py           | 31010 | `20f01692000f627586cb6d1eea0c09b3e2f0190705f779e511a41655d90ee0b1` |
| project/applications.py      | 20012 | `888bac463c27156a012e08ebfe1df33769a2405c117174611b82a63576a8d90f` |
| project/domain_changesets.py | 34728 | `e38f9d58a31f3bb38dc7b2da58f3da26811d3a6cfcc2a5f43a5a10f9b71dfb9a` |

审查原件：工具输出 `619154`、`59b2bd`、`230912` 为规则、授权、合同和实际身份；`cf0ba7` 为固定 Store/Job/应用表及验证路径；`3d39ae`、`de1295` 为来源证明、当前读取预算及静态预算反例。保留完整工具结果，不只摘录 stdout。

## P2-CR-01：原 dispatch 的物理库归因尚未进入合同条件

初始位置：合同 §2 库逻辑证据、§3 resolution selector、§6“目标库不匹配/原库”及 §9.4 跨库错配验收。

静态反例：原库 A 在请求受理后被逐字复制为物理库 B。B 的 migration_id、operation claim、完整 request/context、hostClientId/engineSessionId、projectId、receipt 和 snapshot 均可与 A 相同。当前 scope 证明调用方现在获准读取 B；初始 selector 只带原 request/origin，没有原 dispatch 的物理库绑定。因此这些输入不足以区别“原操作确在当前原物理库”与“当前只是拥有同历史的复制库”，无法支撑跨库错配一定 unknown 的承诺。libraryEvidenceRef 已明确不是物理身份，不能再让它承担该证明。

最小修订：在私有调用前置条件中单列可信宿主保存或重新核验的原 dispatch 库/位置/实例及 generation 绑定，与 current_scope 分开。当前 scope 只证明现在许可；原绑定只证明原请求送向何处，两者都不能由 renderer JSON/UUID/migration_id 生成。缺原绑定、复制/替换/迁移后的对应关系无法充分证明时，保持 unknown，可展示该库真实历史但不关闭“原意图已恢复”。不要求新建 main 意图账本、不要求本阶段实现真实位置 IO；应把该条件留给 I06 实际能力合同及后续精确授权。

此项是合同信息不足的静态反例，未运行尚不存在的 resolution 服务，也未制造真实文件或位置能力。

## P2-CR-02：创建接受预算未保证现有读取服务可消费

初始位置：合同 §7 允许 name 为 1–4096 UTF-8 字节，§8 说明无需改当前 project_host.py；当前读取服务 `ReadLimits.metadata_bytes=4096`，`_row` 对完整 metadata canonical 编码执行该硬上限。

静态反例：名称由 4096 个 ASCII `x` 构成，满足初始 name 规则。按当前相同 canonical JSON 规则，完整 `{name,templateRef:null,archived:false,mode:'guided',origin:'created'}` 编码为 **4178 字节**，超过 reader 的 4096 字节。名称含引号或反斜杠还会有 JSON 转义扩张。若未来创建只验原 name 长度，新建成功后 workspace 会 limit，完整目录也可能因一个此类项目整体拒绝。

最小修订：创建在任何写入前按完整初始 metadata、目录行和必要工作区投影的实际 canonical UTF-8 大小验证与当前 reader 合同相容；名称的原始 UTF-8 上限仅为第一道界，不是充分接受条件。超额应整体 resource-limit，不能先写成功再靠读取拒绝，也不能静默截名/归一化/提高本阶段 reader 硬上限。这可以由未来 project_lifecycle.py 的既定 validator 责任覆盖，无需增加现阶段产品路径或改旧测试。完整库集合增长的 snapshot/validation 预算仍须保持明确拒绝边界，不能把单项目投影可读扩称无限目录容量。

4178 字节来自只运行 Python 标准库 JSON 编码的静态算式，工具 `de1295` exit0；没有运行产品、创建新库或声称事务实现通过。

## 可接受机制与实现条件

1. **engine UUID 与唯一事务可落在既有模型。** 固定 storage.py:259–267 已支持项目和 Store3 genesis；job_store.py:489–506 同事务接公开映射。未来 Store.commit 增互斥 creation intent 分支，在 genesis 已存在于同事务后构造真实 plan/context，不需在 Store 外预写项目。原 genesis 名称 null、metadataVersion/sequence0 保持；专属创建效果推进至 metadataVersion1/sequence1，domainRevision0、单 claim/receipt，无 Job/领域 marker，符合当前表形状。
2. **无 DDL 承载成立，但语义兼容门不可省。** JOB3_CLAIMS（job_store.py:2051–2056）允许 application+job NULL+context非NULL；app_operations 的 application 和 app_receipts JSON/FK 也足够。固定 `_validate_job3` 在 application 分支直接交旧 claim_context，后者精确旧键/tag；固定 `_history` 对 application 同样只认旧 plan/receipt，故新 namespace 必须由未来 job_store/format3 精确分派。不能以 schema hash 相同宣称旧 reader 可读，更不能放宽旧 context/hash 校验。旧3安全拒绝、新同版 reader/writer 一起启用及 capability/profile 门均需未来真实证据。
3. **现四条未来产品路径基本够，但须覆盖旧 apply 重试入口。** 固定 job_store.py:353–365 在相同 application kind/op 时直接进入旧 claim_context。若该 op 已属于创建 namespace，未来应先识别并返回 identity-conflict；不能把异操作误报普通坏 metadata 请求或意外回落。此项可在已列 job_store.py 内完成，不需修改 applications.py。Store.commit 的新参数应保持旧默认分支与旧 canonical/hash 字节不变。
4. **queued 无 marker 与未知 jobId 的完整发现有源依据。** 固定 create_job 在同一事务形成 queued DTO、完整 context 和全局 claim；operation_get 只查 marker，null 不证明未受理。按唯一 operation claim 得实际 jobId，再完整核 `_accepted_job` 的 context/snapshot/参数/prepared/确认，足以避免仅查最近 N 条或仅查 marker 的错误。新 selector 需保留完整原 request、原 implementation/limits，不能替成新值。
5. **来源记录的历史缺口被如实保留。** 固定普通 Job context 不含 host/Session。ChangeSet 的 immutable prepared envelope 在 domain_changesets.py:536–554 含 hostClientId/engineSessionId，确认原回执在 :697–718 逐项互证；accepted_plan 在 :842–872 支持历史只读验证，当前 host 校验则另有当前 base 条件。未来 resolution 必须核原 envelope/回执，不能用当前 Session 补原来源；普通旧 Job 无来源时 unknown，不改旧 hash，符合合同方向。
6. **只读与当前许可必须由实际适配落实。** `_accepted_job` 是读取现有受理，不调用 snapshot/public_project。未来 resolution 仍需 fresh read-only transaction、写 authorizer 和完整 dump 证据；现 Store._read 会加入已有事务，实施时应拒绝不明活动 writer 事务，避免返回未提交状态。当前许可与原请求归因均在内容返回前核验；跨 Session 只恢复原受理，不重放写、不切换新 generation 当前项目。
7. **预算只是 guard，不能代实测。** selector/证据/返回都有限，证据总计必须覆盖所有将解析引用、完整历史/current 校验的输入，不能先无界 `_history` 再计返回。64MiB 不表示既有启动/ChangePreview 分配问题已解决。实际 writer/reader、退出、原子性、兼容、取消和无写验证全部待实施，当前审查不将其提前通过。

## 修订读回与关闭

本独审全文读回原 docs 树修稿：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-host-contract-docs/docs/iterations/T01/project-create-and-resolution-contract.md`，**39602B**，SHA256 **`ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3`**；工具 `9b4233` exit0 完整输出并实际断言字节数/哈希。主线采纳时须逐字核同该版本；本独审不写主线合同。

| 意见                      | 实际修订与判断                                                                                                                                                                                                                                                                                                                                                                                                                                | 结论                                           |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| P2-CR-01                  | §2/3明确 current_scope、原 origin、原 dispatch 物理绑定三条件；私有 original_dispatch_binding 不来自 JSON/SQL/migration_id，须核真实原 operation/requestHash/host/Session/generation/Store与物理身份对应。§6把该条件设为所有 resolved 共同前提，A→B复制、丢失/伪造/无法重建对应均 physical-binding-unavailable；跨Session不能恢复时继续unknown。§8把实际供方和重新证明留作 I06/根审批前置，不虚构当前句柄工厂，不建main账本。                 | 合同层关闭；供方实现与真实跨库验收仍待后续     |
| P2-CR-02                  | §3/4/7明确 name4096B只是初筛，首次写前检查完整 metadata/目录行/workspace编码、所有合法editor最坏开销、加入项目后的项目数/全库row-byte-work guard/快照/整页/保守reserve；固定page_size不自适应，须检查全部有效分组或证明上界。保留4096ASCII→4178B拒绝反例，store写后实际核候选一致，差异回滚；不调用拒writer事务的reader方法做预检，不额外连接、补snapshot、截名或提高当前reader界。§9保留±1/转义/非法完整dump不变与合法同策略可读的待验要求。 | 合同层关闭；全部写前预检与读写相容机制仍待实施 |
| 旧apply原claim跨namespace | §5和§8现明确 job_store.py 原重试入口先辨创建namespace并identity-conflict，反向亦然；不放宽旧claim_context，无额外产品路径。                                                                                                                                                                                                                                                                                                                   | 提醒已落实，四条未来产品路径保持               |
| 只读事务条件              | §6现明确全新只读事务并拒未知活动writer事务，不将未提交状态作为恢复事实。                                                                                                                                                                                                                                                                                                                                                                      | 条件已精确化，待未来authorizer/事务实证        |

本次修订扩大的是待实施合同的必要条件，未改变冻结读取服务/测试，也没有据此重复其全 check。创建时所有页大小预检及完整库预算会增加预检工作，实际代价需后续测量；原 reader 当前槽占用、留存余量、TTL和取消仍可合法有限失败，合同已保留该运行资源边界，未承诺目录永不失败。

当前没有未解决的合同层 P2。原无 DDL/严格新 namespace、原 claim 优先、唯一 Store 事务、旧3安全拒绝、充分 Job/原来源与物理归因、缺证据unknown、跨Session零重放的条件共同成立为设计；是否实现、运行通过或真实用户位置许可就绪均未获本报告证明。当前读取服务的独审和全 check 由主线及 `/root/store_interface_audit` 单独负责，本报告没有重复那些测试。

初轮本报告格式化与显式 ignore-path 检查为 `769d2b` exit0；最终仅对本报告和修订合同执行文档格式检查，结果见本独审完整末次工具记录。指定同版双模型、真实集成、CI、PR/正常 develop 合并、远端与完整父任务验收继续保留。
