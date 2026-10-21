# P1 唯一 profile probe 合同 v2

此唯一 probe 计算固定原始输入的数学投影，不读取独立 oracle 的 expected，也不执行 Store、行为、资源调度、恢复、current/历史或学习验收。旧单准备输入/源码及首轮输出原件另封存于 review 的 input-projection 与运行证据，不改写成完整验收。

## 入口与固定输入

源入口 `python -m ontolearn_engine.semantic_profile_probe` 不接受参数。拟包入口 `ontolearn-engine --semantic-profile-probe` 由 T03 唯一 dispatcher 移除此单 flag 后调用 canonical `main([])`。额外参数固定 stderr `PROFILE_PROBE_ARGUMENTS_INVALID`、退出2，不能落入默认服务。T03 D2 尚未批准/实施，本合同不改其入口或 build 文件。

源码仅定位 `docs/iterations/I05/profile-probe-inputs.json`；frozen 仅定位 `_MEIPASS/provenance/i05/profile-probe-inputs.json`，无 checkout/用户目录/网络 fallback。输入实际1839011B，SHA256 `6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de`，读取上限2097152B，长度/hash先核再解析，恰83 mathInputs。该资产由已批准 f9af899 原17份T09输入及22扩展的原输入字段纯投影；完整oracle只核元数据hash、不解码为生产输入。投影脚本、原版本及输入引用审计原字节另封存。最终格式化字节与agent原投影字节分开记录。

保留50 productCases、54 learningChecks、22 extensions及106原setup/step引用；这些数目不是推理调用次数或业务通过数。83条数学输入中82 eligible、79标记完整上下文，transfer-repair虽有事实但未给规则，不以空规则假装通过。4条E.5 event fragment未模拟行为/工单/资源后状态，不能当完整轮次重放；五项原始上下文缺口逐项保留。

## 实际计算与来源

每条asserted/ontology原输入以subject/predicate明确IRI及object原N3，经唯一strict `decode_profile_term`、`profile_graph_from_records`形成实际RDF Graph和发行context；规则由原定义形成唯一canonical RuleSpec。无给定绑定、第二matcher、SPARQL比较或expected回填。实际reason共享有限RDFS与join，产生原BindingMatch后才交T05 compile/evaluate；custom不反馈。

SourceRecord.reference是相对JSON Pointer `#/mathInputs/i/input/...`，digest是上述实际资产SHA，text是该投影字段的实际decoded scalar（object为已提供N3），原term revision未提供保持None。规则级revision保原值，definition_digest绑定原定义JSON值的确定编码域。相对pointer由本报告input资产定位和digest确定，既未把合成Turtle当原文，也未把inputProjectionJsonSha256伪装成原term revision。原文件ref/hash/pointer/CSV物理行和transformRefs完整保在固定资产；case保其sourceRefs及投影摘要。它们是可追溯上下文，不是来源或producer授权。原raw Turtle token/byte span未给保持None。

structured caller直接在一次issuer里绑定disabled ids，不再无条件重发相同context。全部原输入occurrence及各SourceRecord保留；Graph对同SPO去重不删occurrence。此优化不删已知source/false binding，不放大原池。默认runtime仍i04，legacy有限语义仍finite6，显式profile payload才finite7/format2，实际engine/newlock另列。

## 完整输出与边界

stdout只有一个完整 `i05-profile-probe/2` JSON。每条case success保完整payload/rows/各摘要；已知失败保四字段error和安全私有diagnostic；不eligible明确not-executed。全部83条被记录仅表示collectionComplete；acceptanceOracleCompared/lifecycleExecuted/originalRequestedOperationPassed/sourceAuthorityAuthenticated均为false。原产品/check/操作映射及未执行原因完整输出。

任何case failure或not-executed，完整采集后退出1；全部成功才退出0，亦不等于外部oracle或原业务通过。意外/输入/身份/时间/聚合超限只固定stderr `PROFILE_PROBE_FAILED`、退出1，不吐路径/原异常或半个JSON。输出不截断head、source、false match或尾行。

每次计算JSON+rows原8MiB、depth32、1M节点、rows≤10000/cell≤8192字符门不变。83条集合另有64MiB硬编码上限，单条完整编码预检后才追加，汇总前预留2MiB给元数据；最终流式编码再次逐chunk核。聚合上限与原单次上限分开，不以提高单次容量代替完整投影。实际probe10约14MB，因此旧8MiB整集合无法承载本次83条完整输出；旧probe及其合同原件保留。

图1M工作是确定性计数的最终成功门，显式triple≤100000、入口文本≤1MiB、sidecar term合计≤262144B、各scalar≤16384B；机制整次池按稳定rule_id divmod分child，不每rule默认池乘100。真实源码的issuer准备先受显式长度/条数门，再在reason登记P；这不是准备动作前预扣。全部结构/IRI/entry-values准备收费完成后，唯一entry Budget只获图池实际剩余work；连续parse_value相位无其它图扣费，call finally并入真实delta，两份剩余计数保持对齐。T05内部逐操作先扣，不需改固定Budget或每term重置；这仍不是CPU抢占、时间或进程内存上界。原六机制模块/预算身份不改。来源重复编码可能先触发input262144或child分额，是明确资源拒绝，不改报词法错误或容量通过。

整次120秒仅case/输出边界检查，不能打断单个库调用；源/包采集者必须外部硬进程超时120秒，保存实际timeout/exit/stdout/stderr。固定常量不是worker取消实现。

identity保canonical七模块名/source态实际.py SHA（frozen为null）、实际八项distribution版本、contract资源与完整uv.lock。包.pyc/PYZ不冒充原源码SHA，T03另保实际归档和构建输入。

## 当前实际结果

最终probe30完整83条：78 success（均标完整上下文）、4 resource failure（E.5片段）、1 not-executed（transfer缺规则）；进程退出1、未超时。不是P1全通过或P2通过。首probe08/09的资源失败及修订前源/输出保留；最终固定候选仍须外部完整集合/全部匹配/head/basis对照、完整check/source、独审，以及T03真实同输入同版源码/包比对。正式领域和selected所需依赖仍在原owner边界内。
