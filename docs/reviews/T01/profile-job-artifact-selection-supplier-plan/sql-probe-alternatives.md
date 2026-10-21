# r2 SQL计价选择及实际权属

本文是待根批准的设计请求，不读任何S1/C2/dispatch WIP、不借用其未批算法，不把静态次数当执行日志。固定依据只取423b Store/JobStore及0a03539 C2方案：后者§5的UTF8 33项replace/160u与portable逐scalar quadratic，是方案模板，不是本轮已供应产品。

## A. 当前主提案的真实保存形态

原Store.publish(storage.py1362–1423)调用canonical(payload)写results.payload；原DDL1682–1684声明payload TEXT。新adapter的公开object rows沿该原写路径保存一份TEXT，原result_get/page/GC完整消费此副本。private payload/rows与输入源仍在新四表BLOB，不为公开wrapper改变原B/rowsDigest。origin/context/Job DTO与原不可变snapshot/参数仍有真实TEXT副本。正例K32的TEXT11453440B/BLOB14842880B上界已经逐副本计入，不把所有原TEXT变成BLOB来虚减费用。

因此旧UTF8扫描费在一遍全量最坏TEXT下超过512MiB；更换计数额度有明确业务载体理由。它不是唯一技术选择，也不是已经批准实施的最优路线。提案为新合成catalog显式版本的metadata8GiB/exact32GiB，原C2 profile1不动；完整原开库/Source/Job/发布/page/GC所有费用进入同一实际owner账户，startup另有一次明确有限owner admission，不从不存在的Job借费用。

## B. 有限次数与预付界（拟协议，非实际次数）

新catalog固定只读模板必须在实现冻结时枚举实际SQL/完整表列/PK/投影/execute位置。源历史135/19/530/41 AST库存只有原函数位置，没有未来新branch运行次数；现在不能给“原链实际执行x次SQL”证据。以下是准入上限/查询配方，若真实helper次数超它，必须先拒或另经根批准改方案，不能拿最终query65536反推已经可走通。

正常库包络≤1024完整行、每行≤32列、普通表≤64，包含本次需要收费的schema行；任何超出另交原更紧门而非截断。单批metadata/query配方最多64个count/locator、每行至多4个8列metadata SELECT（输出固定int/null/enum，每次≤32列）、每行一个完整行费用SELECT，加固定page_count/page_size/encoding共3个查询。因此全批新增探测execute上界`64+4*1024+1024+3=5187`；正文helper每个真实execute另计，不能宣称5187已含它。SQL内部UTF8每字段33项replace的扫描已由160u付，不仅付execute常数。schema正文同样经先界收费，不信caller表名或expression。

同一已付快照对(table,rowid,column)的metadata和行费用可复用；引用闭包/完整body与关系检查不能省，重复body按真实read-work收费。换任何事务失效，不借原全局read cache。每Job最多6批完整行费用覆盖（新/重复probe均按实际参与字段计），禁止第7批；6*5187=31122探测execute是保守封存上界，另保事务控制和真实helper/body份额，全体仍≤65536。不能同时把6批的query封存支出当成6次已付metadata工作：metadata另逐实际扫描付页工作，以下硬额度可能更早拒。

每批metadata在COUNT、TEXT长度/NUL/CAST或其它扫描之前预扣`16F+256*字段数`。正常F≤64MiB时，每批≤1082130432；8GiB额度最多接受7个这样的最坏批，第8前拒。通用pager硬界128MiB时每批≤2155872256，最多3个最坏批，第4前拒。实际小批按其真实已界字段/扫描范围保守支付，但不能凭WHERE选择性假称只扫描小页；没有可信索引/完整闭包证明则用整F。root需批准pager与页工作收费法；这里没有调用新native scanner。metadata耗尽仍依原独立控制票清理，不能先COUNT再报资源失败。

正常K32一次exact probe上界1965449216，6次11792695296<32GiB；通用32MiB全TEXT保守`160*33554432 +256*32768 +8*33554432 +128*1024`≤32GiB/6（BLOB再加项有意保守），故6次也可先封存有限界。portable仍按原16*(n+1)^2，在各字段预探n后、不执行quadratic前扣；没有正常UTF16已可接受的证明，超过新32GiB先有限拒，不把新额度视为修复quadratic算法。

拟分阶段要核的真实调用：admission原create_job/_dependencies/_accepted_job与snapshot/source门；一次start原状态事务；producer成功finish_read_job/_publish_job/Store.publish；consumer另有open selection一致读事务与成功发布；公开page/重开startup/GC各有原独立操作。这里不预先断言每阶段只一批：必须由实际冻结模板trace逐execute证明无重复全扫且上述phase+Tail控制都在保留额度内。parent/worker两边的C/T/Display/Graph/H费用各归原实际actor，不转成一个Store账户免除worker费用。最终实际正常全链至少一例仍是实施门；此前禁止声称上述有限式已证明全链可执行。

## C. 严格BLOB与有界扫描可作为根的替代决策

可以申请把新profile普通display也保存为严格UTF8 BLOB，或仅把同一内容唯一保存在result role由公开page按有界adapter读取。SQLite TEXT affinity本身不禁止BLOB，因此不是物理上做不到；但它改变原Store.publish canonical TEXT写入、result payload解码/读取、payloadStatus/GC/current、严格Job3 reopen/format descriptor/C2计价和历史分派，role-only还改变原page来源闭包。旧结果原TEXT必须保持历史解释，不能仅换bind参数而让旧consumer偶然json.loads(bytes)通过就称兼容。公开schema可以保持object rows不变，private B仍原bytes/digest；所有这些writer已在主表，但该保存分支需要根明选及新精确schema/reader/费用矩阵，不能凭本轮r2自动批准或拿新BLOB省费来覆盖主稿TEXT估值。

也可以保留原TEXT保存、申请一个受信有界native/codeunit scanner直接准确计canonical UTF8费用，先数字metadata与页工作预扣，再逐固定buffer读取（同时计raw/UTF8/surrogate/NUL/控制转义、malloc/峰值/statement生命周期及sqlite encoding/错误），消除33次replace与portable quadratic。它要供应真实连接句柄/statement所有权、已批准执行容器和新native代码/构建锁/包writer；不能用Python UDF先收整TEXT，也不能以SQL CAST整BLOB已生成后补len冒充先界。根主线正在评估的其他方案不算本线已供应接口，本稿不读WIP、不改其owner源码，更不绕native执行授权。

建议统一Store/C2 owner比较A的较大有限扫描票与C的更强实现工作后，明确选择唯一版本。若选择BLOB或native路线，重出真实字段保存/reader/hash/成本式及原writer最小delta，同一独审复核；不能把不同路线的低费用与不同路线的兼容证明拼起来。当前r2主稿保A作为可审方案请求，所有新增quanta仍待根批准，未获批不能运行接线。
