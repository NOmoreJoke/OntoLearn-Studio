# 七池声明分配的外部 oracle delta

本轮从已限定接收的 `0cb1a37fe2a68e671d241721cede80621545dfd8` 接续，只细化声明分配。原实现 `3d8f4ee`、R1、101 件旧交付、命令及 manifest 在各原 Git 提交永久保留；旧报告和清单原字节不改。新的当前清单另列七个获准 writer 的新版本。

独立依据是 de37ff6 的 integration plan L72–80 和 851e624 的 saved-restore plan L103–109，全文副本先核原 bytes/SHA，模型只取这些分配条款。6891 的 first-fixed-inputs 原件记录 139 项选择性来自 6c，`/files/51` 和 `/files/56` 是 semantic/restore 的初始 write-existing 项；随后 writer 字节已变化。该清单不证明规范 ref 为 Git 祖先，不外推整树或后来 writer 未修改。授权、原件身份、精确指针与限制均在 `guidance/allocation-source-receipt.json`。

新增 `declaredAllocationPolicy` 与每 observation 的 `declaredAllocationExpectation`，以及有限关系 `declared-seven-pool-allocation`。这是本 oracle 的语义对象，不冻结未来 JSONL 字段。非相关 301 ID 的该字段为 null；相关 116 ID 的完整有序分类在 coverage.json 的 declaredAllocation，分为：

- 88 specified：82 eligible profile 和 6 fullview/profile；完整定义序、原 ordinal、enabled 与显式 disabled 一致，因而可独立给七域声明额度。
- 26 pending：25 records 输入虽有明确 rules，但未显式声明完整 disabled_rule_ids；包含空 rules 的案例也不私定 caller 默认值或 dummy disabled 身份。另 1 fullview Turtle 没有完整显式规则 universe/disabled/ordinal，不能把图中未见规则当成空 RuleSpec 集合。这些项仅保已知 metadata，不捏造 slot 或额度。
- 2 not-invoked：repair 原 profile 不执行；DAG Turtle 先 structured-material-required 拒绝，不调分配。

规则 ID 按完整 Unicode 码点稳定排序；不 NFC／截断／strip。每个原定义包括 disabled 占一槽，N=max(1,n)≤100；各域总额 T 按排序位置 j 分 `T//N + (j<T%N)`。原 ordinal 仅保来源位置，不决定余数。七域是 work16777216、input_bytes262144、output_bytes262144、trace_items8192、firings1024、head_occurrences16384、bindings1024；各域分别守恒，不跨域借额。输入列表重排只改变原 ordinal；disabled 不移除槽、不回流未用额或增加其他 child。原 compile/evaluate 必须共用原 Budget 且不重置，这只是需满足的合同，不由声明 JSON 认证其对象身份。

纯公式的空输入自测按批准的匿名 dummy：ruleId/ordinal=None、空 definitions/matches，要求真实空 batch，不能编造 rule_id、disabled 标志或真实 batch 对象。完整实际 RuleSpec 类型、17L、planDigest、budgetUsage、opaque 发行身份、真实同次 allocation/capture、全部 C/R/D 账单与首错仍各自待证。声明相等、各池总计相等、可计算上限均不能代这些见证。

新增自测包括三规则七域的手写精确余数值，1..100 槽守恒／相差≤1，重排与全 disabled，非 ASCII／跨 BMP 码点和无 Unicode 归一化，空 dummy，ID exact type／重复／非法 Unicode／字符与 UTF8 cap、disabled 外来／重复／缺失，以及尾项／字段／bool-int／余数错误归属／假 capture／重分配负例。没有模拟产品成功，也没有导入产品工厂／decoder。

构建实际按字段重新统计，整体仍 280 specified／137 pending／wholeOracleComplete=false；并非为了维持旧计数硬编码状态。新增声明缺件都落在本已存在完整 typed/capture/费用缺口的生产项内；88 声明完整项也不能关闭原预算准入 pending。独立 Git/JSON delta 核验全部417的业务 expected、原参数／投影／上下文／状态和完整原 context ledger 与 0cb1a37 完全相等，只有声明命名空间、其来源／字段缺口及预算缺口关联增加。

本轮仅外部 oracle build/check/自身 stdlib tests 与 Git/AST/JSON/hash；旧输入/手选 goldens、RDF/query/SHACL/math、不执行的原操作、所有父门不变。legacy DTO、错误投影、新费用规范 WIP、collector／JSONL／最终比较器均不在本 delta。
