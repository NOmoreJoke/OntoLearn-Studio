# 累计计量 delta 独立审查

状态：审查进行中，尚无接收结论，不授执行权限。

## 访问前预扣

本报告在读取本轮规则、候选或 witness 之前独占创建。仅使用本轮作者独立票，完整预扣 **4MiB应用读取 / 6000 metadata**，不退款、不借用旧票或 owner/root 票：

- named witness 文字 schema 专项4600：64 + 5×880 =4464，余136只作本专项保守余量。最多一次读取3156859B固定文件；不整份json.loads、不深层遍历。
- 固定计量 delta 审查1100。
- 报告及收尾300。

总计6000；byte总票4194304B。若任一限制不够立即停止，不重读 witness，不用预留挪补其它专项。当前尚未读取候选或 witness、尚无验证/执行。

## 最终结论（上述“进行中”为访问前预扣的历史状态）

本次固定候选 **尚不能作为充分计量方案接收，仍 NOT_CALL_READY**。发现两项候选缺陷：capture 返回事件的反复构造/遍历未充分计量；独立新实体512票的口径及充分性未闭合。建议最小修正如下，不要求重跑或扩大源码/供应审计。

此外，**本独立审查 witness 专项也发生了上界失效和超票，不能签本次作者预算合规**。唯一一次 witness pin/schema 观察成功，与票合规是两件事。owner已收到全部事实，并明确本次停止新增读取，只用报告300票收尾；没有新增补票、追认、挪票或重读。

## 固定对象和范围

基线 `4690d9aed65f62aa635fc79e59b6eb53d2620d4b`。全文读取本轮4533B静态窗口（SHA `b852cba6adb6917c0b1dbe97b95b044d690fc864c48129c1cbd63dae3da426c7`）及1998B原准备root收件（SHA `22c9d2222fc2a2e7868e8b84e9ccd2e57cbcdbdc2846c3be578c234155695cd6`）。Q/candidate-pins.json为1305B，SHA `879ed6261673361385baa4a2e265f2118a2d18d33028b1cb09081a8d5fd27976`。八文件合73492B逐件bytes/SHA核同：

| 对象（相对D） | bytes | SHA-256 |
| --- | ---: | --- |
| run-once.py | 42725 | 125539360317d8e65be228fbef1221ad98a0d2884bda0cf4d89ad619cd07ef50 |
| call-plan.json | 9405 | a7ee58701713b7a290bd9455a9ee739febae470f1d4d2985bd9f4283c2c0aa29 |
| meter-plan.json | 727 | f4731e1d49ad11ad6dd048d882ae519e966b7fc993b669dd0ede7ed5a541c6e8 |
| meter-history.json | 729 | b978d2fbfaaba3f846da8721ac5074678e8331cccbda34be0f4c98011568ad32 |
| control-method.md | 3544 | e74f4a5702b4fb6a7e6dc36e9ebac7031fac6aaf787e6ae5d9f59afba96c54bb |
| dependency-method.md | 2489 | f8f363fe47efd6fb8545470ba10a8c572e2beaddf53c52c1ce3d5a445ed4f48a |
| budget-and-usage.json | 6473 | 5ed19e4d610608811c52b2fe0c1c9286fd5c584146e8f6c7bff6bf725f42a608 |
| meter-preparation/meter-proof.md | 7400 | 0c6a7e86c503cfca2e8504782daae6e4fa4fb47288a108774820842d6bf7f5fb |

本审是这一个固定候选的文本/控制流 delta 审，不是供方源算法、旧工具历史或SDK闭包审计。没有import/call/dry-run/verify/simulate runner，也没有抽取其函数运行；未独立运行编译器、检查器、native/API/fixture/GUI/DB、网络或工具版本命令。没有115工具payload重hash、SDK/header/42772索引或旧205包读取。源码2b724f副本及旧产品未重新读取或改变。

## 候选缺陷及最小建议

### 1. capture selector事件上界缺失

`capture` 中 `sel.select(...)` 生成/返回的 key/event 集合及后续 `for key, events` 是可反复访问的记录，不都能归为免费byte/OS I/O。16MiB捕获cap只约束字节；不能假定每read满64KiB。短read、空唤醒和BlockingIOError都可令事件/调用次数远高于固定每command48。600s/0.1s也不能代记录计数，因此目前control静态10634及runtime89000的完整充分性结论未成立。

最小建议：六调用共用一个固定select调用计数器。每次调用前检查cap128并预扣8，覆盖仅登记stdout/stderr两fd时至多2条返回事件、每条保守4单位；空返回也不退款。还需在对应受认可stdlib语义中确认没有额外注册、单fd单次至多一条返回记录。先扣后select，不能返回后才收费。该建议最多128次select/256个事件，新增1024；原control10634→11658，仍在12000内，89000/103000总phase票无需因此扩大。

事件/调用cap可能早于600s或16MiB触发，必须保存UNKNOWN/incomplete、停止且不重试，不能称可持续等待600s或以产物完整推断日志完整。16MiB生产端总cap及65536紧急预留保持。这里是静态建议，没有模拟事件、调用selector或测量最坏时间。owner确认将在本报告后统一最小修正；本报告不预签尚未出现的修订字节。

### 2. future entity512的定义与充分性未闭合

候选只列独立新实体512，未充分解释它与117身份行的前后metadata、module候选、880旧记录、最多1024当前路径和SDK候选之间的计票关系。不能将“新未知SDK路径≤64”或物理去重数当全部候选访问上界，亦不能借旧8192票。metadata与实体cap须共同适用。

建议将口径明确为保守候选实体/身份访问票，提出独立新4096而非应用512，并把可能重复的前后身份、module及依赖路径访问显式列入其证明；这不是声称发生4096次物理SDK访问。当前实体521456/600000，余78544，若root另接受4096，算术变为525552、余74448，可行且不涨guard。是否将只作opaque历史文字的880行计入实体票也须先明示；不得事后改分类。owner已接受修正方向，当前候选未改，不由本审直接应用。

## 其它静态计量观察

PhaseMeter只用固定scalar账；emergency3000在输入前保留，preflight20000、control12000、dependency54000进入时预扣，失败不退款；主phase预留89000与四phase相加一致。snapshot不扫描历史账，明确actualLogicalVisits=null。固定work费与phase reservation分别记录，不将upperWorkDebits冒作实测访问。

输入decode在native json.loads前收费3×unit_cap+8并先作有界文字结构扫描；cap含容器、字段、数组成员，深度12，固定六输入cap和3548。输出改为仅支持builtin dict/list的有界编码器，在容器迭代前take预算，json.dumps仅接收标量，不做sort_keys、hook或完整容器第二次序列化。解释器native内部收费模型及单位仍需root显式接受，不能说库内工作实测为零或已穷尽其内部实现；本审没有读取解释器payload或动态检验decoder。

descriptor/pins使用一次path映射和单遍验证/物理sum，不再重复线性next；module明确512及先扣3×512，post117先扣12×117。token每次append前收费、3073前停止；normalize/dedup先扣3×rawTokens，使用插入顺序，无排序；旧map和SDK候选单列费用，未知第65条在append前停。深层prior references/approvedWitness不构建JSON对象、不复制进输出；输出仅固定witness SHA+ordinal。source-evidence仍须3621B固定SHA再有界解码，七候选与四带path对象不同，不再只计四次遍历。

proof的书面分项算式：preflight19372/20000；dependency53035/54000；control10634/12000；emergency2208/3000。前两项及错误输出/构造的收费意图可对应当前代码；但control上述遗漏使全成功路径充分性不能签收。错误/取消路径需继续保首因、close/control/terminal persistence分离；error_info进入emergency，超大/过深/不可序列化上下文明确INCOMPLETE，不因meter运行时拒绝就声称构建前已证明充分。没有运行任何失败注入或取消实验。

authority要求实际runner/plan/pins/descriptor/meter-plan/history/proof SHA及source ref/hash，并接受fresh89000 runtime/103000总metadata及128MiB分票。历史owner实际UNKNOWN，旧1000/root4000/16628/256MiB及所有失败、unknown、255保留且不可复用，原preparedPreflightDebitUpper/1467/8055条件已删。当前没有创建执行authority。

旧单源、一次compiler+五检查、parallel1、无产物执行、单次attempt、独占owned输出、0600原流、首因/cleanup分离、当前Popen leader限定控制和未知descendant drain边界保留，没有新增locator、索引读取、产品源或API fallback。selector缺口修正不得放宽这些控制。

## 当前与future账算

本轮准备12MiB/20000只加一次：owner6MiB/10000、作者4MiB/6000、root另2MiB/4000，互不借票。当前build109027642408/137438953472B，余28411311064；combined118773369493/147184680557B；metadata2145263/2250000，余104737；实体521456/600000，余78544。旧消费、预留和UNKNOWN不退。

fresh future只是proposal：128MiB=owner64+author32+root32；helper40=输入8+record/source输出8+artifact8+capture16，owner外部closure另24。metadata103000=89000+7000+7000。若另授，metadata2248263余1737、build109161860136余28277093336、combined118907587221，算术均在当前余量内；不能因此称已经获执行许可或以1737余量弥补未计量工作。实体512当前候选不足证明；建议4096须另被root接受并同步修改proof/plan/auth，不从旧池借用。

## 本审唯一witness读取：观察通过、专项预算失败

访问前已在本报告独占预写4600专项票；随后实际一次读取named sixth used-dependencies.json，**3156859B / SHA c7a1c91c0d6cbb0e9f1daf087c79413c65973d5cc2c128b03a22c2196b2d3357**，pin相符。未重读、未whole-json.loads；仅scalar normalizedPath用JSON字符串解码。

独立文字范围covered为byte区间[2416,3156692)。观察880个固定缩进outer row、880唯一绝对normalizedPath；每行外层字段顺序为normalizedPath/references/approvedWitness，path scalar及delimiter、approvedWitness对象检查均0失败。未深层访问references或approvedWitness，也未据此读取任何header。该观察支持候选限定covered范围的文字schema，不是执行候选parser的测试，不是库内部、物理header或完整来源闭包验证。owner此前一次regex范围断言失败、整6400票保留且不再owner读，不能被本次成功覆盖。

但本独立辅助脚本用了 `re.findall` 生成每行三个字段名，又以列表相等比较三个成员。按宽口径这两个库记录遍历最低已 **(3+3)×880=5280**，超过原专项4600至少680；还未计outer row、path scalar、set等其它访问。原64+5×880=4464证明失效，完整实际逻辑量**UNKNOWN/未闭合**，不能冒称总作者≤6000。4600、delta1100、报告300全部保留不退款，不能用其它专项余量挪补或将该项改记免费文字字节。owner已认领所建议4600上界亦不足，并要求保事实交总控；当前未补票、未追认当时合规。

发现后立即停止新增规则/候选/witness读取；没有为补数重读或重遍历buffer。delta1100及报告300仍各自独立，报告只记已有观察/缺陷，不延长审查或预签修订。此作者计量失败属于交付限制，应与候选event/entity缺陷分别处置，不能互相掩盖。

## 读取与交付边界

本轮文件payload读取已知3324942B（两规则、有限candidate/8文件、runner文本分段复核及唯一witness），收尾仅再读本报告一次计算真实SHA。含报告读写的保守应用文件payload上界取 **3.5MiB**，低于4MiB；没有OS/cache/磁盘I/O实测或RSS/解释器峰值内存证明。metadata本审失败如上，不给虚假的合规上界或剩余票；6000整票保留且各子票不互借。没有读取owner/root票下材料作为免费消费。

唯一写入为本报告；未改runner/proof/产品/源/锁/他人证据、未提交、未联系其它thread。owner随后最小修订、disposition及manifest/index闭包不在本固定候选报告预签范围。未关闭原指定同版双模型、两目标OS、真人/CI/父N0/远端门及T01 HOLD/已拒绝操作停止线。
