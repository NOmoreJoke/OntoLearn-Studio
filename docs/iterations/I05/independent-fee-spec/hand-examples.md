# 独立手算小账、边界及反例

这些数值先按下述字面算式固定，再运行外部模型。它们是**完整给定数学事件程序**的 invoice，全部程序本身在 `hand_vectors.json`，不模拟产品fixture，不声称是完整产品RuleSpec/Graph/producer成本。示例 cap 不超过原机制 work16777216/input/output262144，也不新增业务容量；scan/hash/live采用显式数学局部限额。缺真实typed/graph费用的114输入不能由小账类比成成功。

公共 finalization ticket F：最大2 data handles、累计4 data slots、2字段的小数学receipt、receipt body为三个字节 `TT\n`、domain为1B `R`。该receipt仅小账数学记号，绝非生产receipt。固定预付work=`2+2+4+2×3=14`，scan_copy=`2×3=6`，hash=`1+3=4`，reserve objects=`2+1=3`、scalar=`3`。此票同时覆盖固定counter/receipt读写和最多handles/slots释放，未用不退，因而它的exact费用是这张预付ticket，不是宣称实际释放工作等于最大值。模型事件本身不另建产品audit数组；如果未来存audit，该载体另收费。成功后留数学receipt，data/control全部释放；失败清全部引用，累计费用不退。

## A. 完整成功、差1和零余票

`complete-zero-balance`，局部work cap23、objects70、scalar30，次序不能交换：

| 事件           | 本次work / 其它域       | 已付work | live objects/scalar | 意义                     |
| -------------- | ----------------------- | -------: | ------------------- | ------------------------ |
| control64 HOLD | 0；objects64            |        0 | 64/0                | 先票后bootstrap          |
| F              | 14；scan6/hash4         |       14 | 67/3                | receipt与control并持     |
| INPUT3         | 3；input3               |       17 | 67/3                | 三原始字节               |
| ITEM2          | 2                       |       19 | 67/3                | 两字段槽                 |
| MUL(2^32,1)    | L=2×1=2                 |       21 | 67/3                | 不是因结果等于原值而免费 |
| OUTPUT2        | 2；output2              |       23 | 67/3                | 先检查两个域再整向量扣   |
| HASH2          | 0；hash2                |       23 | 67/3                | 总hash6                  |
| HOLD data(2,5) | 0                       |       23 | 69/8                | native/临时重叠峰        |
| 完整finish     | 释放control/data；F已付 |       23 | 3/3                 | 无部分返回；work剩0      |

最终费用 `work23,input3,output2,scan6,hash6`，峰 `objects69,scalar8`。work cap22时在OUTPUT2之前已有21，`21+2>22`，**首错output2/work**；INPUT3、F和先前MUL不退款，output仍0、hash仍4，未执行其后HASH/HOLD。cap23恰成功，cap24余1。cap0/63的objects bootstrap64前门拒，paid work0、峰0，不创建容器；这只复核允许的2d5局部控制票命题。

若一个OUTPUT7同时work cap20（已有14）、output cap1不足，固定域序先work；整个向量不提交，work仍14、output0。不能先扣output1或称预算失败后“重开一次”。

## B. false 后项与末项首错

`false-then-type-error`：F14；第一个comparison检查ITEM1→15；数学CMP(1,0)为一limb→16且本例结果为false；下一comparison域检查ITEM1→17；接着给定数学事件 `RULE_COMPARISON_TYPE_MISMATCH`，整程序failed，无heads。work cap17允许走到该语义首错；cap16先在later-domain-check/work拒，不能把后面的type错当首错；之前16不退。模型只计comparison整数的成本，错误标签是独立手列事件，不执行产品comparator。

`last-item-semantic-error`：F14 +前child检查4 +尾field检查1=19，随后SAVED_VALUE_MISMATCH；前child完成不产生success prefix。对真正receiver篡改，原期待摘要保持不变，通常原blob hash门更早失败；本例描述**已到字段核对**时的数学账，不谎称所有tail篡改实际走到该点。

## C. 重复comparison与全部head

`duplicate-comparisons-all-heads` 的完整事件费：F14 +binding ITEM1 +comparison ITEM2 +两次双operand各SCAN2共4 +两次一limb CMP共2 +head occurrences2 +firing1 +重复head输出3B×2=6，总 `14+1+2+4+2+2+1+6=32`。scan=`6+4=10`，output6，head_occurrences2，firing1，binding1。两个相同comparison照费；两个相同triple head照保index0/1，facts RDF去重不删除第二head票。cap31则最后head1输出前已有29，29+3>31，首错在head1 output/work，不能先返回head0。

## D. 同source、alias和cache

`alias-source-twice`：F14 +同5B原source两次INPUT=10 +wire两次COPY=10，总work34，input10，scan16，hash4。source底层一个owner持5scalar、两个引用slot，所以live峰objects=`3+2=5`/scalar=`3+5=8`；这并没有免掉第二次wire出现。若真正复制底层两份则应HOLD10scalar，不能沿本alias账。两份同内容不同source身份不一定共享owner。

完整cache key例：kind=`iri`3B、lexical=`urn:x`5B，其余六字段None，source-present=0。header8 +presence1 +8×(marker1+length4)=49，加字段8，总57B。source=None与source-present=1四None记录bytes不同；空字符串与None不同；EN与en不同。hash separator32B，故每次audit89B。

`cache-miss-then-hit` 的独立数学子账：F14 +两次key SCAN57/COPY57共228 +lookup ITEM两次2 +给定独立parse子账work5/input3一次 +两次保存字段两侧SCAN10共20 =269。scan=`6+228+20=254`；hash=`4+2×89=182`；input3；fresh strongref objects1/scalar2与receipt并持，峰4/5。第二次hit省第二次parse，**不省key、hash、保存值核同**。这里parse5只属于显式给定数学子账，不能冒充 `parse_value(urn:x)` 的现行费用；该产品精确子账没有独立规范仍pending。

cap268时末次saved-second-allfields前已有259，需10而拒，first=该SCAN/work；不能把缓存命中当全值核过。source变化会miss，但具体parse费用须另给完整数学子账，不能复用5推断产品。

## E. 重复restore/roots和终态不可复用

`whole-stream-restore-one`：F14 +SCAN7 +COPY7=28work，scan20，hash=`4+7=11`。两个**独立、已授权且有独立有限票**的数学操作分别28/11，总work56/hash22；不是max28，也不能因samebytes第二次免费。同一个Ledger运行第二次明确ValueError reused，原paid不变。F本身work cap13在第一事件拒；失败Ledger再次运行也拒。正式同consumer Job禁止借“新ledger”重试；跨Job身份/授权仅T01真实来源供应，小账不制造它。

`repeated-roots-targets`：F14 +两个target entry2 +相同6B key逐次SCAN共12 +每target两个head roots共4 =32work，scan18，hash4。请求 `[t,t]`保两个结果组，每组引用head0/head1，4个root occurrence；不去重目标或heads。没有任何target且caller按合同不调用roots就没有这次账；若实际显式空调用，entry/finalization仍需付。roots借view意味着H整个view，不以4roots乘固定小票替其保留。

## F. 并持、D固定费及receipt不漏

`overlap-success`：F已持3objects/3scalar，old2/5→live5/8，temporary2/7→live7/15，峰7/15；完成后3/3。objects cap6时第二HOLD前5+2=7>6，先拒，峰只有5/8、费用仍F14/6/4、failed live0。不能以最终只留3/3证明cap6足够。

`dag-fixed-plus-whole-actions`：F14 +两candidate(包括一个最终落选)8×2=16 +一个step32 +三个index字节(16traversal+2scan work)×3=54 +COPY2/SCAN2=4 +link ITEM1 =121work；scan=`6+2×3+4=16`，hash4。它是此完整**数学事件程序**账；真实DAG还需旧graph/C0/R0/DP/全部keys/whole-J，不能拿121当任何114输入invoice。D分析子界不另开钱包；重复候选不能把16减到8。

## G. 稳定allocator全小账与16c

原定义数组 `[z(enabled),a(disabled),m(enabled)]`，sorted=`a,m,z`，原ordinal=`1,2,0`。

| 七池             |       a |       m |       z |     合计 |
| ---------------- | ------: | ------: | ------: | -------: |
| work             | 5592406 | 5592405 | 5592405 | 16777216 |
| input_bytes      |   87382 |   87381 |   87381 |   262144 |
| output_bytes     |   87382 |   87381 |   87381 |   262144 |
| trace_items      |    2731 |    2731 |    2730 |     8192 |
| firings          |     342 |     341 |     341 |     1024 |
| head_occurrences |    5462 |    5461 |    5461 |    16384 |
| bindings         |     342 |     341 |     341 |     1024 |

十结构项对每个child仍是term16384/source65536/digits4096/integer_bits16384/temporary32768/rules100/when16/comparisons32/heads16/variables64，合成完整17L。disabled a依然拿多1，完整compile后不evaluate、无虚假空saved batch；z不能拿其余额。原数组ordinal0的z没有余数奖。N2时七总池均整除：work各8388608、input/output各131072、trace4096、F/bindings512、heads8192，余数0。

N0使用一个dummy：id/ordinal=None，完整七默认池+十结构门，空compile核Catalog、空evaluate得到真实空batch；它和disabled的None有区别。预测这些字段不产生原capture、planDigest、issuer或usage。

N3的 `k_a=203+33×342+4×87382=361017`，`k_m=k_z=203+33×341+4×87381=360980`，Σk=1082977；16c总work cap=`3×16777216+1082977=51414625`，input/output各524288。N1 dummy时k=1082571、总work51414219。这里是精确cap算式，**不是实付usage**；disabled实际definition-only费用由原API发点决定，不能以cap倒填usage。compile与eval共原child票、不重置、未用不回流，独立R_parse/恢复/16c三个域互不抵扣。

独立算术补例：GCD(48,18)的余数链48→18→12→6→0，非零除数有3步，各一limb乘一limb，F14+3=17；Horner十进123从0起，每digit一次乘10和加digit，共6个一limb动作，F14+6=20。它们是本提案的数学primitive schedule，未声称现行产品parse按此步数执行。

D的16K是固定traversal子界；合同另要求scan同时进work。本提案将独立2K扫描另计work，故index3B实际此子账work54/scan6，完整给定程序121。没有把fixed16K子界误当总work；若owner证明16K已包含该2K扫描，需要明确替代映射才能避免重计，不在本窗猜测。
