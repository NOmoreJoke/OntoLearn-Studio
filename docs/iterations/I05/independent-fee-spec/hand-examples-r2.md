# R2 完整输入、手算与失败边界

本版完整baseline和独立字面算术如下。小模型的19个原手列程序仍在hand_vectors.json，R1旧手算文档保历史；它们证明给定数学程序的边界，不冒充产品invoice。R2新增控制/累计/整BLOCK反例是另外8个独立literal程序。完整大程序只消费固定纯输入和手选数学，不运行产品。

## 1. baseline:G-base 从完整输入到2282个prefix

固定observation是`profile-83/baseline:G-base`，dataset同名，inputs projection SHA为72d43efe8cb3b3462b356eb9ee8a3ca17a752c08c9717b5fbfea3aa52d20df2d。完整raw输入由固定8,205,267B/SHA47c66ffe…输入件给出；本dataset canonical raw JSON12585B。原asserted18+ontology10=28 rows；rawTermSource occurrences=3×28=84，75个IRI、9个S；原唯一规则R-risk、when4、comparison0、head1；独立数学匹配1、firing1、head1、RDFS新增0。这里没有把“0 comparisons”推广到其它ID。

新binder完整输出保存在`charge-reference-v2/baseline-fee-material-r2.json`与`.bytes.hex`，新codec85953B/SHA5bc7b79b64ae371f95078a21eb152fb90e7884a1380764d2b9823a879bda9f8d；这是新提案typed输入，非现行payload。893个fieldOrigins逐field区分真正原值/缺省/合成。三前像：input71713B、source61981B、definitions15485B，Q=133694、D=15485、A=25315003，完整SHA在binderMeasures；N1完整17L为原固定默认，不从表的pending推导成零。

八个新data lifetime票的累计slots，按公开schema逐项计：material3747 + C0 workspace84252 + ENTRY180 + M0 9916 + G27036 + native11921 + projected12481 + wire buffers5 = **149538**。control64、receipt自己的93票不算这八个data；二者从开户起真实并持。

receipt字面长度782B；wallet五个（C0/ENTRY/G/WIRE8M/M0），child一个，F=12+12×5+20×1=92。H01整向量预付：work=92+3×8+149538+4×782=**152782**；scan=3128；hash=18+782=800；receipt保objects93/scalar1596。fixed-width receipt由独立decoder核每LP、每11域u64、17L、ordinal和末尾hash；不只核长度。

| prefix    | 操作                                      | C0累计work | 全owner live objects/scalar |
| --------- | ----------------------------------------- | ---------: | --------------------------: |
| 1         | control64                                 |          0 |                      64 / 0 |
| 2         | H01+receipt原子预付                       |     152782 |                  157 / 1596 |
| 3         | material3747/85953                        |     152782 |                3904 / 87549 |
| 4         | 提前保完整C0 arena84252/3800788           |     152782 |             88156 / 3888337 |
| 5         | 全raw12585 bytes                          |     165367 |             88156 / 3888337 |
| 6         | input encode+copy143426                   |     308793 |             88156 / 3888337 |
| 7         | input hash71713                           |     380506 |             88156 / 3888337 |
| 8         | source encode+copy123962                  |     504468 |             88156 / 3888337 |
| 9         | source hash61981                          |     566449 |             88156 / 3888337 |
| 2273      | 全rows hash                               |    3215011 |            149695 / 6819795 |
| 2274      | 顶Catalog hash439                         |    3215450 |            149695 / 6819795 |
| 2275      | 释放projected，累计不退                   |    3215450 |            137214 / 6524752 |
| 2276–2281 | material/四workspace/wire buffers逐个释放 |    3215450 |              12078 / 272422 |
| 2282      | terminal control64释放                    |    3215450 |              12014 / 272422 |

中间**全部2282个prefix**都在baseline-prefix-r2.json，每行都列本次向量、完整钱包累计/live/peak、全H live/peak、是否首拒/未执行尾段；该表是完整示范，不以这十几行摘要取代中间事件。terminal仍留native11921/270826与receipt93/1596，合12014/272422，不能拿最终小票谎称输出view已释放。

全账逐类手算（均为本提案确定ticket，不是当前实付）：

| 钱包   | 独立字面算式                                                                                                                                                                                                                                                                           |        work |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------: |
| C0     | H01 152782 + raw12585 + 三前像3×(71713+61981+15485)=447537 + binder15885 + source整扫21348/自身hash12463 + Catalog重复/排序/查找4205 + allocator31 + 28leaf全key hash4845 + 三遍联合wire1898346 + 全native/projected节点12202 + payload298403/rows334379/Catalog439三hash              | **3215450** |
| ENTRY  | 84项完整输入编码work72136（input70540+节点1596）+ raw UTF8 2752 + 75IRI检查21624 + 九S检查392 + 84独立完整fingerprint79676                                                                                                                                                             |  **176580** |
| G      | seed4845+38788+112；完整排序4845+28+88532+235；round1；predicate建1592+12764/四查251+2012；join252+328+31+8171+43+22984                                                                                                                                                                |  **185814** |
| M0     | plan compile/recheck31718；11term输入14794、raw327、IRI2552、S64、value hash15748；plan hash15598；定义/变量65；proof/binding排序733；binding1+完整typed11954B/节点work12243；全部head/完整Catalog/trace/firing791；basis输入/排序3086；facts排序183；全batch21421+独立typed hash21437 |  **140761** |
| WIRE8M | 只作原联合byte gate，output计完整632782；编码扫描已由C0收费                                                                                                                                                                                                                            |       **0** |

完整域结果：C0 scan2235007/hash800508；ENTRY input70540/scan2752/hash79676；G scan131220；M0 input=`15583+14585+15583+11954=57705`、output21421、scan3082/hash52783、binding/firing/head/trace各1。新payload298403B+rows334379B=632782≤8388608。G185814≤1000000、M0140761≤16777216、C03215450≤3240385920；这只证明本新程序分池可容纳，真实H需另有quota。

峰值按**同时活着**求和：C0 objects112563/scalar5087003 + ENTRY180/11192 + M09916/501992 + G27036/1219608 = **149695 / 6819795**。不是每种空间各取最大后忽略并持。完整prefix审计独立加每事件向量、重建holds、核peak/终态、独立第二encoder及receipt decoder，未import reference/invoice_model。

## 2. 差1、零票与首拒

原19手列数学程序的完整成功例（F14的微型receipt格式）：control64→F14→INPUT3→ITEM2→MUL(2^32,1)2→OUTPUT2→HASH2→HOLD2/5→finish。work=`14+3+2+2+2=23`，input3/output2/scan6/hash6，峰69/8、成功留3/3。cap23余0；cap22在OUTPUT2之前21、21+2>22，整个向量不扣，output0/hash仍4、后续HOLD不发生、failed live0；cap24余1。objects0/63在64 bootstrap前拒，work0/live0。该例局部cap均不高于原池，不能把23当baseline完整费用。

R2 control反例：control64 + F(1handle/1slot/2fields/3B)=10work并留receipt3objects/3scalar，再HOLD1/2。objects67时仍是control64+receipt3=67，下一票需68而拒，paid10/peak67/3、最终failed live0；objects68恰成功，peak68/5，terminal仅留receipt3/3。普通提前release control、重复release、BLOCK alias control、control在finalize后开户都在全程序静态校验阶段拒，state仍new，used/held/live/peak全部不变。不能通过early release得到“67能成功”的新余额。

累计清理证明：h0/s0、h0/s1、h1/s0配任何newhandle均在开户前拒。F(h2,s3)后HOLD(a,2)+HOLD(b,1)恰用最后handle/slot，work13，峰6/3；s2差1在任何live变更前拒。F(h2,s2)→HOLD a→RELEASE a→HOLD b恰合法work12，累计newHandles2/newSlots2；F(h1,s2)或(h2,s1)均拒；release不返名额，a名也不能重复创建，末项再new c仍拒。静态校验整程序包括尾项，不把中间valid prefix当完整程序已通过。

BLOCK完整向量：control64+F(h1,s2)=11work/receipt3/3，BLOCK work7/scan5/hash2/temp2/5。cap(work18,objects69,scalar8)恰成功，峰69/8；objects68时在该BLOCK整向量先拒，work仍11/scan6/hash4、峰67/3。另F(h2,s3)=13，BLOCK同时temp2/5+retained1/2，共新handles2/slots3；work20/objects6/scalar10恰成功。work19或objects5或scalar9任一差1都不扣7/5/2，也不先HOLD一半；failed清全部引用、不退款、不reopen。

完整114中的一个**新提案**首拒是E.5 round4：event13367，M0:evaluate的完整binding/when/proof/source INPUT，已有input255390、work403805；请求input12342/work12631，255390+12342=267732>262144。work足够而input不足，原子不扣，本次input仍255390、output0；此前binding16/firing15/head15/trace15不退款。整个13435事件的后续只是数学需求分析，既不执行也不发布15条成功前缀；这不是现行产品的RESOURCE_LIMIT许可。

## 3. 类型、重复、disabled/dummy、restore/roots及末项错误

Horner123：三个digit mul/add共6，显式指数零Horner2、ten-power square1、最后乘1、Euclid(123,1)1、归约2，总13work；0.1 decimal为digits4+exponent2+power2+Euclid2+归约2=12。测试期Q6修订曾误把仅浮点的远指数检查2票收给integer，字面13捕获15（exit1已保），修正scope而未改golden。

IEEE字面独立值：binary32(0.1)=13421773/134217728；binary64(0.1)=3602879701896397/36028797018963968；16777217→binary32 16777216，9007199254740993→binary64 9007199254740992；1e-100000合法下溢、-0e100000直接有符号零，1e100000为非有限受限，integer -0不标binary negative_zero。Calendar字面日序：0000-03-01与-0000同day0，0000-02-29 day-1，-0001-03-01 day-366；0000-12-31T24:00:00.000Z day306/second0；0000-03-01T00:30:00+01:00 day-1/second84600。九域×六算子486分类、XML Char/语言ABNF/Q2均有独立字面测试。不是SHACL日期policy的更改。

重复source五字节两次INPUT10+两次COPY10，加微型F14得work34/input10/scan16；alias同底层只省持有，不省出现次数。完整key的无source IRI urn:x是49B frame+3(kind)+5(lexical)=57B，source absent、present四None、text空串/None、EN/en原样都不同。完整cache小账F14+两次key扫描/复制228+两次lookup2+显式parse子账5+两次saved/fresh20=269；cap268末项10B全字段核同前拒。parse5只是该独立数学程序的给定动作，**不是现行parse价格**。

实际114新程序中fullview/profile-55有B602964/Q149716/J9186/M4/U2/S3974，原child与顶重复各有PV；两miss完整Rp解析、两hit仍收fullkey/hash/全值检查。raw-aliases保8输入rows而RDF图6；不按term value合并原source occurrence。

重复comparison/两个相同head的小账work32，最后head输出3B前已有29；cap31拒最后整输出，不返head0。false后第二comparison域错的小账paid17，cap16则更早resource首拒；整批无heads。末field语义错前paid19，先前child不发布。真实wire篡改保持held摘要/bytes，因此通常更早在whole-byte门失败，不拿这个手列末field例冒实际路径。

disabled完整新程序示例extension:DISABLED-RULE-NO-OUTPUT：M0 compile work78695/input37017/hash38189，output/firing/head/binding/trace均0；它没有假空batch。零定义dummy例dag/domain-depth2：M0完整空compile+eval work1956/input1102/output89/hash671；且图仍有RDFS两步，A5/S2/E4/K534/carrier1249，全D/R/roots另列不省。disabled余额不回流；N3 sorted a,m,z 的完整余数值仍见原手算表，各17L原预测保留于逐ID。

两个独立且各有真实调用授权的微型restore：每次F14+SCAN7+COPY7=28work/hash11，重复总56/22；同Ledger第二次调用即拒，不重置票。重复roots请求[t,t]每组两个head，F14+entry2+key12+head4=32work，保两组四ref；无target不调用与显式空调用不同。新完整roots程序额外保整个restored view和返回buffer；实际恢复/17L/issuer权限仍独立pending。
