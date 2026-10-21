# 1316050 独立预算 delta 复核

结论：**BR-01、BR-02、BR-03的预算前票及持有来源修复可关闭；该候选整体仍待新发现的 receipt-constructor 失败清理修复。** 后者由根实际注入 MemoryError 复现，本审静态确认对应局部引用路径。不能因三条旧意见关闭而给该失败生命周期通过。

## 固定身份与实查范围

- 新 Git ref `1316050a895a787b7b94bbe18e99efcb3cd141d2`；相对首审 `bbd79c3cff88e8fef348a9c4dcb6981ab5e3cb47`，base不变。
- core：49854B / 1262行 / SHA-256 `ce157068bbcf5695606cf918d405e633a330f16046420dc7e68d201516bd311f`。
- budget：37478B / 1120行 / SHA-256 `593b2a832dd510063bb60d7b3d5526fbd6cf4dcba53ad9c513e82dbfdd77ef7f`。
- 两文件固定Git delta与全部必要上下文已逐行读；当前文件核字节等于固定ref。`RestoreLedger.begin`整个AST（含全部cap公式）与bbd79相同。candidate.json的72项逐Git bytes/hash核同，68只读项逐字等于bbd79；见 `delta-1316050-audit.json`。
- 读本次新增 nested foreign callback 及 encoder exact/差1前门测试源码。本审未重跑142专项；该数量、exit0与runs06绑定是根提供的外部运行证据，不冒充本审执行。本审本次只有Git/hash/stdlib AST/数学复核，没有新runtime或探针。首审71循环清单继续适用于未变部分；新两个嵌套ID循环、child循环由context固定块支付。
- 首审报告与原始probe保留；此次只写自有delta证据，没有core/tests/68/AGENTS/env修改，也未做GUI、付费、模型、提交或外部发布。

## 旧意见逐条处置

### BR-01 关闭：encoder实际峰值已有独立普通预留

budget:759–782：在任何delegate前先付stage，再普通scalar `retained=8*bound+64`、objects4，进入opaque后调用原writer。结果通过bound门，普通scalar只保留len(result)、objects只保留1；失败在except释放整个已持块，恢复外层finally也会处理委托前reserve失败。

固定原encoder的同时集合为chunk(str)、data(bytes)、output(bytearray)，最终bytes转换也另有结果：chunk统一4B/codepoint≤4bound，data≤bound，sink≤bound，final bytes≤bound；合≤7bound，64常量加一倍bound余量足够。这里的bound来自strict wire派生safe值的原总长度门，不能把本私有helper外部任意native值当恢复入口。首审实际3份局部峰值反例现已被普通票覆盖，不再借AST余量或opaque≤65536的小槽来源。没有改原writer或cap。

### BR-02 关闭：projection新scalar完整生命周期可见

core:961–979：objects2J先留，scalar4J失败则回滚objects；scalar成功才进入opaque/原projection。任何BaseException释放两块；正常返回时两块继续在ordinary live。

4J来源：原projection保留的新scalar只有int→hex/bytes→hex，和一次当前str.encode临时。native整数字段/bytes由strict wire对应token解出，fresh PV也已完整比对保存字段，因此单次委托累计新hex≤J；一次UTF8临时≤J，4J保守足够。不是把所有字符串假定≤65536。

实际成功释放位置1057–1059（source）、1066–1068（defs）、1074–1076（records）、1089–1091（reason/payload），均先del相应safe树/编码引用，后降scalar/object live。safe_reason与source→defs→records最多两份safe树同时在途，新增scalar≤8J；失败时栈退与decoder cleanup后统一归零，不发布半结果。

### BR-03 预算部分关闭：固定metadata前留、receipt在running内构造

- graph_budget 在新增结构前普通reserve128objects（core:673）；覆盖limits/usage/返回dict、临时ProfileLimits/kwargs；entry/usage helper另留自身票。未再后置19。
- parse setup 在values dict/ProfileLimits/Budget及其六counter map之前reserve128objects（core:769–773）；连同临时kwargs按record+slots口径保守少于80，128充足，lists及cache自身由固定metadata/原trie票覆盖。
- A16（1094–1099）在parse_usage、两list、child/caps/final tuples之前prepay A16并留固定work/live。每child parse_usage六对tuple及外tuple≤25，child record8字段+record=9，caps四pair及外tuple17，lists/结果tuple槽和局部更新后保守≤64N；固定usage/peaks快照、返回receipt、列表/tuple头、固定closure元数据保守≤128。`256N+256`对象足够。
- 首审BR-03描述“RestoredChild 9字段”计数应校正为8字段、加record才9票；旧8N+2仍没有覆盖caps/usage等，原意见不因此改变。
- 新cap/control整数及中间小整数保守≤256N+1024逻辑scalar；`1024N+1024`足够。固定结构操作128N+128 traversal与copy1024N+1024连同A16整stage预付覆盖当前固定构建。所有块保持到最终receipt后，未在普通数据构建前释放。
- 外层1222–1231在ledger仍running时构建RestoredBatchSet；`ledger.usage/peaks`求值前全部显式charge/reserve均已完成，之后只有固定receipt构造、drop/cleanup/finish，没有新增debit。快照报告的是最终抽象收费与预留峰值，不是RSS/CPU。

**保留限制：constructor失败后，新的外层局部children/parse_usage/caps仍需清理，见后文。上述关闭仅指原BR-03预算前票与成功路径。**

## 新增entry context块的来源与前门

core:1204–1219先确保children是exact tuple、1≤N≤100，再begin和context预留。在`_check_expectation`进入任何ID scan/循环前，905–911核rule_ids/disabled都是exact tuple、有界、`N=max(1,len(rule_ids))`。所以不能用1个child配100个IDs领小context票后大扫描，也不会调用foreign `__len__/__iter__`。三个ID来源为rule_ids、disabled_ids、children.rule_id，各至多N个、每项先exact str/len门、后UTF8 scan；child、limits、ordinal均exact/type门后才进一步用。limits的17数值原路径仍在type int门后比较，不触发foreign equality。

普通context scalar：按最保守4B/codepoint，三组ID≤3×16384×4×N=196608N；三implementation value≤196608；六64字符摘要≤1536，固定version/domain/身份keys及17个有界limits整数为小常量/每N小量。N≥1时合小于524288N+4096。前像bytes已归raw B+Q，不双领；ctx record/tuples/refs/decoder按固定字段槽小于128N+128。现有入账字符串扫描仍按长度收费，新增128N+128 traversal支付nested固定guards和decoder建立。

gate前对已经由调用者持有但字段不合法的对象，不采用其协议、不复制大内容；例如超长exact str在长度门拒。以上票据模型约束恢复拥有/处理的bounded context，不声称控制调用者在调用前已占用的任意Python heap。

## 同时持有与原caps校核

本次没有改任何cap，也没有将费用塞入R_parse或16c三池。新增普通块有来源，不能只因cap宽宣告够用。

一个故意叠加了非同时阶段的普通scalar保守上界为：`30J+3S+65536M+526000N+32768`，其中M取版本固定131072：raw J；UTF8临时4J；AST字符串4J；native解码数/bytes≤J；两safe scalar8J；encoder块≤8J；rows text4J；term临时与cache key≤3S；fresh scalar≤65536M；context/receipt/audit digest/常量归其余项。encoded payload跨rows encoder的额外buffer由上述非同时UTF8/两safe余量覆盖。它比原scalar cap `16J+16S+16*65536M+1048576N+4096`小：即以J最大25165824、S最小8388608、N最小1取最不利差，仍正128606243152逻辑bytes。这个数字是上界代数差，不是性能/内存容量。不能跨域借票；未拿opaque付大JSON块。

objects：physical JSON值/key各至少2个wire bytes，故实际physical nodes≤J/2；AST node+slot≤2physical≤J。固定schema native/collect可按对应wire字段/容器摊≤J，structured refs临时从严≤J；两safe预留4J，总≤7J。PV ordinary16M、固定context/setup/graph/receipt等小于2048N+4096，仍在 `8J+16M+2048N+4096`内；trie nodes/slots原独立域不变。新增A16 prepay属于原16阶段中的A16，非第17遍；新增context/A16固定work仍从原N余量支付。

R_parse的同child unique full-key单射、16c同原L三池/control、key49 framing与trie256branch、wire两pass及integer limb处理没有delta，首审这些部分的有限结论保留。

## 已知新receipt失败清理：本候选尚不通过该项

core:1221 `_restore`返回tuple先绑定外层 `children,parse_usage,caps`，1222构建receipt可能抛MemoryError；1253–1259 finally只清decoder，没有清这三个外层局部。原始异常虽被替换为有限RestoreFailure，新raise产生的外层frame仍持有该children tuple；`ledger.cleanup()`已经把live置0，却未对应丢弃这组新局部strong refs。

根提供的runs07在该精确候选注入最终constructor MemoryError，观察到error traceback仍保留1个真实child、ledger failed/live0；本审未重跑该注入，但固定源码支持这个引用结论。它是本轮实际新constructor生命周期delta，不能被“原三BR预算已修”覆盖。

必要最小修复：finally清`children/parse_usage/caps`外层局部，失败时outcome也清None，并保留真实故障注入回归；成功时outcome作为唯一transfer保留。下一delta只需绑定新SHA核这些引用清理/运行证据，不应重开未变trie/scanner等探索。

本轮采集结束，可解除1316050冻结。正式整体通过仍等待该cleanup delta；指定双模型/CI/生产授权/跨OS/性能边界均未在此关闭。
