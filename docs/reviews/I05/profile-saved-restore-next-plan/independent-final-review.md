# 下一纯恢复阶段方案：独立静态与数学审查

本报告仅审文档可实施合同，不是源码实施、运行、恢复成功或父功能通过。当前初审结论：有3项需文档修正，其中R的逐阶段费用来源是本次授权的核心要求，修正前不建议将该版作为完整费用证明收口。

## 固定被审版本与实际范围

主方案 `docs/iterations/I05/profile-saved-restore-next-plan.md`，37213B，SHA256 `214e520a006a69dd6300d0b1273c2ce6184620f4dab023c4f535aa613ccb7a4a`。固定产品0475d0ec6c486a63c7e8f62f11f35181da6b2576、新API16c58c6d0ca56491c7134c4866f9bed5e0f722c5、证据ca0990a893a6d3af106985fe5dae5ff287b79553、基线5f910b52c69d86a1076b2032e5d3c63e715947f3。

全文读3845B本轮授权、主方案（首合并工具输出有截断，缺失80–145行已单独完整补读）、两份独立准备意见、root两收口与14233B最终报告、T05 code/budget两报告；定点读取实际0475 projection/caller、semantic返回/allocator/meter.key、canonical parse/check_value，完整16c API（合并输出的一处截断已以108–184行补读）。读source-reference、future-adoption、frozen-baseline与两个stdlib静态检查JSON。没有import/执行产品、pytest、probe、安装、build或package；没有复制API、创建代码树或改Goal。

自有stdlib Git/文件/hash/整数核对：70路径=63固定继承+3待采用+4未创建，所有已定字节的ref/bytes/SHA/blob相符，4新路径确实不存在；26源码/授权/报告引用及原件副本相符；原118路径当前字节全部等冻结清单。结果见 `independent-final-review-audit.json`。这些不证明源码运行或未来70项组合成功。

## 需处置意见

### R1 [P1] 逐阶段费用清单尚不足以推出新R总界

位置：主方案115–135行，尤其121、123、125、129、132–133行。

R_parse单射、cache query/split以及整数分块的局部来源可静态核对；但新设6个wire passes、16次树访问/每节点32单位、64倍scan/copy、固定对象/保留tickets，目前仅声明上限，没有给出固定算法中每阶段、每数据域的遍历/复制/编码/hash次数和同时存活集合。准备意见第六节也明确未冻结这些新常数。仅“实现超过则改合同”不能证明原合法成功在本版R下一定容纳，特别是已有_projection/_profile_json_bytes、canonical parse与16c内部有分配/遍历，而本未来4路径范围不允许改其计费。需要说明这些委托调用是按已知输入规模事前保守预留，还是另有实际计量器，不可既不改原函数又声称其每个内部分配逐次被新ledger扣费。

建议：补固定阶段×数据域×最大visit/copy/encode/hash次数表，列每阶段委托调用前的reservation与释放、索引/allocator查找具体查询次数及保持的live集合，由表推总系数；已有canonical机制费用仍归原池，R另预留其持有/复制，避免漏计或循环证明。费用模型只证明受该固定算法合同约束的实现，不宣称已有运行/CPU/RSS容量通过。若暂不提供这份来源，应把全流程成功命题限定为额外受理/实现证明前提，明确本版R总体仍待证，不能称完整方案已收口。

### R2 [P2] 外层三字符串投影未冻结恢复后的exact tuple

位置：83行；实际source为semantic.py的meter.key及evidence/rdfsEvidence组装。

rdfs/rules本身为list，但其中每个三字符串为native tuple；evidence.result、evidence.inputs每项、rdfsEvidence.result与basis每项也来自meter.key，均为tuple。当前“三str数组”既可以被实现为list也可以tuple，与“exact native shape、字段schema补回tuple/list”要求不够精确。请明确 `list[tuple[str,str,str]]` 等每层类型，warnings/rows仍list，不做全array统一转换。完整JSON回编码相同不足以证明native容器类型已恢复。

### R3 [P2] cache header/摘要separator只给长度，未冻结实际版本字节

位置：29、93、99、117行。

8个字段各type1+length4最大40B，加source存在位1B；若“固定版本header”直接使用已命名 `i05-profile-restore-term-key/1`（30B），总framing为71B，超过64B，使S≤B+64M的来源不成立。即使实现可另选短header，当前方案也未固定这种选择。建议明确短二进制header，例如8B `b"I05RTK1\x00"`（最大framing49B），长schema版本仅操作域metadata；同时冻结具体32B SHA separator而非只给长度。None/string的marker、长度单位及source=None时四字段编码规则也一并冻结，避免一个逻辑key多种wire形式。

## 未见新增阻断的范围

- 已以实际16c API为依据；一次compile/evaluate完整matches、三个原L池与控制K公式正确。ΣK在N100/F1024/O262144时为1102668；整体机制work/input/output关系与供方合同一致，恢复R没有偷借三池。
- 严格schema覆盖现批准record全部字段，所有保存PV仅canonical parse发行，再逐出现核domain/value/language，弱发行强引用持有、false matches/全部head/source保全、disabled与真实空batch区分合理。R_parse只对保存比较值不同完整TermInput重parse的单射范围合理，没有扩大为整次R≤W/I。
- S上界在framing确实≤64条件下、压缩字节trie的257(S+M)条件与2U+N节点界成立，split512明确仅引用复制，额外分配/update单列；SHA仅审计而不用作完整键相等，未假设无碰撞。
- 分blob保留原8MiB域，native投影与physical JSON计数分域，完整保存字段不能认证原L/原matches/producer的边界有明确披露。Turtle缺原前像、structured可逆路径、独立同次捕获与真实跨进程验证没有混成正式T01授权。
- 70项范围和原字节采用边界明确；施工尚待授权，selected/Store/worker/长期字段、正式producer/权限/生命周期及父出口均未被本方案关闭。

本报告不把未见阻断项目变成实现通过；上述3项关闭后须固定新plan bytes/SHA并作针对修改的静态读回。原始初审意见保留，不改写为首版全绿。

## 修订delta最终读回

主开发保留初版原件 `plan-before-review-fixes.md.raw`，37213B/SHA214e520a006a69dd6300d0b1273c2ce6184620f4dab023c4f535aa613ccb7a4a；本审逐实际unified diff读取修订，最后固定主方案 **45463B / SHA256 `3f72f07ba535983ca324226be769de2c157303b35b723aa107bf4e6252a1f41b`**。中间88b040版45146B、f7a750版45343B为修订过程；最终明确JSON encoder转义chunk费用范围及subprocess exec全新解释器，不能用继承父issuer内存的fork快照。本结论只绑定最终3f72。

**最终结论：本次3项方案意见已关闭，在固定纯阶段设计、抽象debit与逻辑持有模型范围内未见剩余P0/P1/P2方案阻断，可交root决定是否另发精确施工授权。** 这不是已经实现的恢复R通过，不是任意未来实现均满足这些常数，也不是整机CPU/RSS证明。已有源码只读，未运行产品或测试。

| 意见 | 实际修订与独立核对 | 最终处置 |
| --- | --- | --- |
| R1 | 新6.0明确A1–A16固定算法、每数据域累计访问与copy上限、六次wire读取、各hash调用、live集合及不可改canonical委托预付；自己代码逐操作debit，canonical函数调用前按静态块预付并预留峰值，不再假称有内部hook。rule查找限排序N/disabled N/top F/入口1，child按ordinal直索引；Catalog只top编码一次，重复wire出现仍全核。 | 文档层已关闭；未来真实源码必须逐循环/调用/同时存活集合映回该表，超出即不符合本预算版本，不能靠增池/删字段发布。 |
| R2 | rdfs/rules及evidence/rdfsEvidence内每个三字符串明确为exact tuple；外list、basis与proof tuple分别明确。与实际meter.key返回和生产组装相符。 | 已关闭。 |
| R3 | header精确8B `I05RTK1`+NUL，8个marker/4B长度字段、source存在位与source=None规则固定；最大framing49≤64；SHA separator精确8B `I05RKEY1`+24NUL=32B。 | 已关闭，S≤B+64M条件满足；hash不参与cache等价。 |

R1的数学读回：16×32=512与16×4=64分别对应固定visit/copy合同；wire调度实际4(B+Q)+B+Q=5(B+Q)，不超过6(B+Q)；hash清单合计≤6B+2Q+S+32M+65536N，不超过所列32B+8Q+S+32M+65536N。cache/整数/R_parse/T05各子域原独立推导保留，没有拿这些新费用塞入T05三池。

持有范围已区分普通native/AST/safe/records集合、PV/cache强引用与opaque canonical临时。typed/数字原生标量的64帧×64槽×(65536+4096)=285212672<2^29只作为逻辑载荷保守预留；不是C库、regex、Python header/allocator或RSS核验。源码AST的参数/Store绑定名自有重算最大30<64；初读辅助表的check_ints漏计*values（列2，完整计3），不影响最大值，供方辅助表随后已修正为3，最后自有重算与修后表完全一致（audit differences=[]）。这支持固定槽模型，但不单独证明完整栈/RSS。JSON encoder的escaped chunk确实可超过65536：65536个NUL约393216B；最终文本已把这些chunk/sink交A11–A15普通B/Q buffer预留，不再借小槽界。typed sink与本地replay另按I/O预留，成功保留结果转普通live、临时解除预留；失败finally清理，不返还已用work。

本次delta没有改70项采用表与原引用，最后再次逐118当前文件bytes/SHA核冻结清单全部相等。自有audit记录最终hash、初版保留hash、数学式与AST核对。依然没有源码、跨进程恢复、tight R、GC、性能或包的运行结果；独立源码/预算审查和完整真实跨进程矩阵是施工后仍必须完成的条件，正式T01/selected/父出口保持未关闭。
