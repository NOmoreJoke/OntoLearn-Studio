# F1 精确纯规范与解释器窄授权请求（未获批；F1继续未完成）

R1结论接收：本候选只有局部公式/给定数学程序，还不是完整五operation、114输入的可计算收费提案。F2/F3与BLOCK retention可在现权限内修复；F1不能以真实issuer缺失掩盖可独立定义的技术工作。本请求将二者分开。

固定输入仍为0e42a0fe349054a92817cb4d463bccdc15f6c042两纯JSON（inputs8205267B/SHA47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa；manifest21202B/SHA0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a）。完整业务数学expected只沿3d8f4ee912f41bd03388322d29a9bfc0e7defe85独立oracle的既有pointer；不读产品算法/actual/probe/tests/generator，不读取首作者草稿或其它WIP。

## A. 必须补明的纯值绑定（影响输入是什么）

| 变量/最低输出 | 已有来源及原条款 | 为什么现有资料不足 | 最小新增纯规范及独立可验证绑定 |
| --- | --- | --- | --- |
| `materialMode[id]`、调用参数是否omitted | 每observation operation/parameters；root纯API声明仅execute_profile[_records]默认；P§4 | API默认不是fullview producer物料接收合同，Turtle行不能据此推断其规则来源 | 逐ID声明目标私有入口和真实传入参数集合；区分omitted/None/empty，不带调用结果。以observationID、inputRef、datasetPointer/projectionSHA绑定 |
| `records[id][i][S/P/O]`完整TermInput五字段 | profile83原asset是N3 triple字符串，D records族已是typed字面值；I§5/P§4/R§3 | 不能把asset source locator当实际TermInput source；无权调用现binder/reader编译它 | 选择一：供应完整typed字面物料及字段来源pointer；选择二：批准一个独立的**提案binder文法**将raw三元组字符串映为TermInput，明示这是新提案，不称现行binder事实 |
| `SourceRecord.reference/digest/revision/text`及存在位 | pure input仅`{ref,path,pointer,sha256}`定位；Q§1/P:60–66/R:93 | locator四键并非SourceRecord四字段；无独立规则决定text是原文件/原token/None、revision取何值、reference如何拼接。费用与cache key均依这些值 | 逐source occurrence供应exact四字段/None及来源，或root批准提案映射的精确字符串/framing/缺值政策；禁止由expected/graph补source。相同引用重复保原occurrence，不仅unique集合 |
| `definitions[id]` RuleSpec八字段/disabled/order | profile input definitions与D rules字面体；I:63–78/R:64 | profile JSON定义含enabled/source locator/definitionJsonValueSha等不同字段；不能默把digest/revision/constant lexical转换当已有合同 | 完整字面RuleSpec与field-level来源映射，或批准独立提案binder；definitionOrdinal/disabled和sortedID分池独立核，不发行CompiledPlan |
| `catalog[id]`有序classes/object_properties/data_properties | I:63/P:63；原ontology输入及数学expected | 规则中出现IRI不等自动声明；Catalog的来源、顺序、重复保存点影响compile bytes | 纯声明Catalog构造规范：只从何种ontology声明、哪一稳定顺序、重复保留/去重规则及逐项输入pointer；不得从规则heads自动补许可 |
| `rawInputPreimage/sourcePreimage` | P:60–66/R:35–36、49/93 | asset canonical JSON不是native物料投影前像；source/records每次重复投影不同字节 | 纯native投影schema+canonical编码文法；在上述typed物料固定后由独立编码算bytes/SHA。Turtle原UTF8直接绑定输入text；structured保持原记录/三term顺序 |

前五项中的**提案**映射可由本作者设计，并非必须真实issuer后供。问题在于当前窗口禁止业务fixture模拟/业务compile/reader，而从raw N3生成完整typed物料与目录/定义已经跨入该边界。因此请求root明确批准“只为外部charge规范生成固定字面物料”的独立binder范围，或交回已批准的纯字面物料；不请求看产品binder函数体。

## B. 本作者可以独立定义、但需明确允许计算的提案技术面

| 变量/最低输出 | 原约束/缺口 | 拟定最小技术delta（新proposal，非现行事实） | 独立验证及禁止项 |
| --- | --- | --- | --- |
| `graphActionTape[id]`每prefix候选/索引/sort/closure/join/union事件 | I:65–80/D§2；F1图遍历只有动作名无次数 | 明确一个有限的reference charge traversal：有序输入、四finite模板、每轮稳定candidate排序/first witness、每when/partial binding扫描顺序、所有失败候选/重复键和所有heads。只输出费用事件，不发布业务图/匹配结果 | 可用独立hand-selected expected核事件覆盖和有限数学关系；不读取/复刻产品算法、不导入reasoner；不调用matcher来“找expected” |
| `typedInputBytes/typedOutputBytes/fingerprintPreimages` | Q:67/R schema；原typed编码文法未提供 | 完整新fee-codec：record标签/字段序、nullable/tuple/TermInput/source重复、canonical hex/UTF8/domain分隔，逐byte收费；现有TLV只proposalPlanDigest，不冒现行typed编码 | 两个独立编码法/手算字面向量对照；bytes仅归新proposal。原planDigest/typed bytes映射另列待纯规范，不靠actual校准 |
| `primitiveTape(term/comparison)` | Q:60–69已定值域/limb/运算前bit门，未给完整步序 | 独立纯数学历程：Horner、Euclid、bounded exponent、binary32/64直接舍入、Calendar400年商余、字符串/IRI/lang/boolean逐字符有限识别；每operand/field/bit界先票，false后不短路 | 只用stdlib exact整数/有理/自有字节编码；不发行PV，不调用业务parse/compare，不产生产品结果。若解释器被视为fixture模拟，需明确限于charge-event计算例外 |
| `wireShapeTape`、JSON native/wire各节点/whole-J长度 | R:45–51/81–89、A1…A16；P full7/15/11、D7/16/11 | 新提案固定projection/key顺序/escape/inthex/byteshex/rows切片、重复Catalog/top-child与DAG字段遍历。动态身份/摘要保shape宽度与角色声明，绝不补原usage=0；若不知字段值但仅影响长度，使用**明确上界预付ticket**，不标actual精确bytes | 独立逐field/count/UTF8字节向量；保原8MiB、32/1M native门及rows门；新预付费用可能更保守，须逐ID报告准入/拒绝，不全拒减任务 |
| `receiptVector[operation]`、`cleanupHandles/slots`、`retentionIntervals` | P§8/D§5；R1指出五operation未填 | 5operation固定receipt schema、明确有界计数编码宽度/摘要域/终态body不自包含自身hash；由reference charge traversal静态计算所有new handle/slot与typed/raw/safe/cache/DP/frame生命周期，并在任何分配前预付最终清理票 | control64持续至terminal；所有temporary BLOCK与retained输出原子预付；H01对114全部列依赖；不借别域/不提高旧cap，不声称RSS/物理界 |
| `proposalInvoice[id]`完整事件程序+prefix used/live/peak+首错 | 当前114全null；不能由真实issuer缺失拖空 | 对每ID由固定纯物料+新charge文法+字面数学expected生成有限事件序列，计算各域和保留，给exact提案预付费用/条件错误；baseline:G-base先完整示范，再82+32全表 | 不取产品输出/历史actual；同次真实原allocation/usage/issuer另列pending，不混进提案费用金额 |

B表的算法/字节/receipt细节不是“必须owner提供的真实事实”；本作者应自行完成其新proposal。请求的只是允许在本外部模型内执行该**独立charge解释器**，以免违反原窗口“不能模拟产品fixture/业务compile/reader”的明确禁令。若不允许执行解释器，至少允许将其完全文法写入文档并用纯手算baseline展开；全114自动展开仍需该窄执行许可或逐ID已手选费用tape。

## C. 只影响现行映射/真实权威，不阻止新proposal定值的项目

- 现行原typed/planDigest/fingerprint编码的精确字段顺序/标签、原Graph opaque委托到规范收费动作的映射：须纯规范/声明供方固定ref/path/bytes/SHA，不能读算法或actual反推。新fee-codec和新reference traversal可以先独立定义；现行费用仍pending。
- 同次真实17L、BudgetUsage、PV发行、actual leaf/witness产生点、actual原expected/allocation binding、producer Job/source/Store权限：必须真实发点/owner供应，数学模型无权制造。**这些缺口不妨碍proposalInvoice金额计算**，只阻断将提案账称为现行原运行已遵守。
- 当前raw输入缺失的原source正文/RuleSpec字段属于A表输入事实或待批准提案binder，不能把其费用当0。选择新映射后值和费用均是proposal域，不能替换原输入或冒正式来源。

## D. 请求的最小解释器许可边界

只在本树现有两个docs前缀新增 `charge-reference-v2/` 的纯stdlib数据/编码/数学脚本；只读本请求列出的固定纯asset、纯规范及外部独立expected，入口参数只接封存JSON值。允许独立解释上述新proposal文法、有限RDFS/when **charge traversal**、数值primitive和fullview wire形状，唯一输出为charge events/数额/逻辑live峰与coverage证明；中间数学图/绑定只作为枚举费用的局部变量，不能导出为业务结果/expected或喂产品。先静态前门、原cap、有限循环边界；不得通过全拒、增cap、改变首witness/值域/semantic version减少范围。

继续禁止产品import/执行、任何产品算法函数体/当前probe/tests/generator/历史actual、RDFLib/pyshacl/pytest/npm/build/native/DB/GUI/网络/安装、业务archive解码/Store/Job、首作者草稿、外部模型、push。禁止把新解释器命名成另一业务执行器或将其结果当T05业务oracle。需要新增纯规范时先给精确字段，不扩大源码读取。

最低回执：逐A表选择“固定字面物料”或“批准提案binder”；明确B/D窄charge解释器是否允许；若批准仅subset，列确切ID/operation和输入/输出schema。未回执前本作者只修F2/F3/BLOCK及静态分栏/H01，F1保持未完成，不将本请求当授权。
