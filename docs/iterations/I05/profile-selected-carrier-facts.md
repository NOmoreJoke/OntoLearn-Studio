# P1 真实表示：批量复核四项答复与最小申请

对照固定T05提案 `c1a616bbc8fc699ad11cd73cbf663c3692515e5f` 的 `rule-batch-revalidation-proposal.md` 全文。本答复只记当前P1私有计算事实及所需增量；新API、selected、长期载体和正式producer均未实现/批准消费。

1. **保存值与重发行。** 当前 `reason(profile=PROFILE)` 返回原 `PreparedFiring/PreparedFiringBatch` 强引用，比较值由本进程canonical T05 `parse_value` 路径签发；同child当前原对象可保持发行身份。`execute_profile`把所有groups/comparisons/heads/TermInput/source/原lexical、精确整数和机制typed bytes/digest投到有界私有JSON，JSON/rows/source/definitions分别摘要；该JSON不是已实现的反序列化器。目前不存在从保存JSON恢复exact records/重新签发的代码，不能直接喂给新checker。所需最小恢复器应严格白名单解码原TermInput/SourceRecord和全部元数据，保存ProfileValue须重新parse其原term，并逐字段核保存的domain/value/language完全相等后才使用新签发对象，不能直接构造ProfileValue或静默用重算值修复被改保存字段。相同完整TermInput（含source四字段）可在恢复阶段有界缓存一次parse，但T05编码/issuance仍对每个出现收费；恢复缓存、原子失败和计费必须独审，当前无充分上界证明。

2. **原完整matches的现状。** 当前代码的 `_finite_matches` 真正构造所有完整匹配，随后有序构造 `controlled`，包括false matches、原binding tuple顺序、有序when和全部proof leaf occurrences；一次交给同child的 `evaluate_bound_batch`。**返回对象目前只保true firings/batch，controlled没有进入返回载体，跨child不能恢复原false matches。** 不能从true groups造original_matches或重跑图补齐。最小私有增量申请是在各 `mechanismBatches` 条目保 `originalMatches: tuple[BindingMatch,...]`（实际传入evaluate的同一tuple），另保该child确切definitions（当前每启用child为单spec，空定义child为空tuple）、实际Catalog、原division limits和disabled状态。只申请当前P1临时表示/完整JSON投影，仍受每child bindings_i、整个1024 bindings、helper输入总池262144和最终8MiB JSON+rows门；复制/保留前另扣图池。此申请不授权Store字段、公共DTO或长期保留。父selected要求child退出后可用，故最终还需T01正式有界载体/窗口/撤回GC授权，未交前不得宣称selected可用。

3. **定义/来源/producer绑定的事实。** 当前原RuleSpec tuple、实际图声明生成Catalog、每spec source/revision/definition_digest、实际输入字节摘要与sidecar/proof表均在当前纯计算对象/私有结果里；child按rule_id稳定分池，原definitionOrdinal仅追溯输入数组位置，单child compile的definitions顺序不重排。它们是输入一致性，不是正式持久不可变ref或producer授权。T01现已在建有限ChangeSet，不等于rule/source/Catalog/producer/worker合同已交付；没有已批准的该正式绑定。本次请求只能保完整私有数据，不在CLI自造Job/Store/producer。未来必须T01先校成功终态、项目/快照/作用域、三字段实际implementation、定义版本/原输入与payload/rows摘要、source访问权限，再允许解码/复核；历史/unknown不可由数学图一致性升级成current。

4. **整次资源申请及尚缺证明。** T05的 `3W+K/2I/2O`覆盖该API内部三个池/control，**不含I05 JSON解码、重发行、原matches保留、载体/hash或进程峰值内存**。P1生产按N<=100分child，原W_i/I_i/O_i等总和不超过W/I/O。若新checker每child一律使用三份默认Budget，损坏输入的整次最坏上界会成为N倍默认池；不能把其写成整次3W。本线请求T05考虑由可信调用方传入经全局确定的原child `ProfileLimits`（或等价固定限额入口，不能让public caller任意抬高），三池沿该child上限。则各child重放/编码/issuance仍有原成功片段依据，整次为 `3*sum(W_i)+sum(K_i)`、`2*sum(I_i)`、`2*sum(O_i)`；`K_i=1+F_i+F_i*C+4*O_i+2H+2P+4`，N受100门，F_i/O_i总额固定，disabled只需有界重编译原定义且不伪造不存在的生产batch。该变化需T05自己补真实证明/测试/ref，I05不fork checker。

恢复必须另有独立整次R池和载体读回门，不能复用已耗尽生产池或把parse成本藏进3W：建议R_work不高于原整次W、R_input不高于I，JSON原字节/对象遍历另受8MiB/深度32/1M节点门。它是待证明的保守申请；“每个唯一term恢复parse对应原compile/evaluate的某次parse”及缓存/对照/解码/排序/hash逐项来源仍须核。若不能证明所有批准合法生产结果都能在这些门内恢复，必须给更精确恢复成本界/版本或明确未完成，不能为通过删source/false match/head。T01的正式child内存/timeout/保存窗口仍待实际接线，不把debit units当进程内存/毫秒上界。

以上可让root决定最小P1临时carrier增量与T05按child限额API，未把它们写成已实施。selected第六测试仍不创建，不以即时原对象复核替代跨child保存读回；生产计算及完整独立oracle接入继续。

## 临时增量后的实际状态（不改写上述申请历史）

根已按 `I05-profile-original-match-carrier-increment.md` 另行批准，本候选现保留实际传入evaluate的同一`originalMatches` tuple，含false/true及原binding/when/proof顺序；保该child实际definitions/Catalog/immutable limits/disabled。disabled编译过但matches/batch为None；空定义实际evaluate空tuple，原空batch保留。保留前扣图池，完整JSON投影仍过原8MiB门。新增真实测试核同对象与false记录、disabled/empty差异；这不是跨child/持久载体。

已全文只读T05新提案330fcedb（32769B/SHA e5fefefd78f62b4b5c989acd02aba6dc227042a3517fe3d90dc23bc0e3bae750）。新`/2` API的required原limits/disabled及definition-only语义尚未交付/批准消费，当前无import/恢复器/selected第六测试。

实际allocator固定为N=max(1,原完整规则数)，先≤100、exact tuple/RuleSpec与全id唯一性门，再按rule_id Unicode码点排序分位；每池T、位置j的限额为`T//N + (j < T%N)`。work/input/output/trace/firings/head_occurrences/bindings总池分别16777216/262144/262144/8192/1024/16384/1024。因此含disabled/空定义的全部预留之和逐池恰T，ΣF_i=1024。disabled仍用同原child有界compile，不能因未evaluate虚构batch；没有失败退回或重试发新额度逻辑。当前返回limits是该次实际Budget.limits原对象，非来自JSON。未来重检只能从批准原输入/allocator可信上下文重建额度并核保存字段相等，不能让保存JSON自报限额证明自己可信。

按新提案，revalidation界只能写`3ΣW_i+ΣK_i`、`2ΣI_i`、`2ΣO_i`；其中ΣK保N个固定入口/digest/profile开销、33ΣF_i和4ΣO_i，不能并成单K。恢复/缓存键生成比较与hash、JSON遍历/typed bytes恢复、原matches保留/读取及source/定义/载体摘要均不在此界内。原R_work≤W、R_input≤I申请仍未获得逐项来源证明：缓存能少parse，不免完整source键和重复出现扫描，保存ProfileValue全部domain/value/language必须逐项对照。未证明合法生产结果success→严格恢复→复核能在R内通过前，不提交恢复代码、不宣布selected可用。T01正式producer/作用域/保存窗口/撤回GC同样未交付。
