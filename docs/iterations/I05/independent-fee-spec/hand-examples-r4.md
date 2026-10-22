# R4 独立手算与完整入口小账

原R3独立手算、所有旧字面/golden、独审失败均冻结。R4的独立审计器不import reference/Ledger，按每事件重建九累计域、两live域、原子拒绝、全H峰和terminal，并独立解IFR3。以下新字面算式不由测试把模型输出再当expected。

## 1. 正常 baseline 的567 work

baseline仍28 raw rows/84term/source、1定义R-risk/4when/1head，binder85953B、三前像71713/61981/15485B；G/ENTRY、原85次C0 source验证/摘要和8data handles均不变。新E00提供字符串共7个：ID6、revision1、原定义摘要64、locator的ref40/path88/pointer8/sha25664，均ASCII，合 **271B/271字符**。每个type+byte guard共2work；另2个未提供的nullable字段各1work，outer4+mapping1+three-sequence3+source-shape1共9work。

所以新work=`271字符+271UTF8+7×2+2+9=567`，scan271/hash0；动作=`7×4+2+9=39`。C0 workspace从原第一次使用点移到前门首次ID处，其完整arena与后续共用，未新增handle/slots/峰；metadata阶段40项含这一个原有workspace动作，完整程序新增39项。

| 指标                    |           R3固定原量 |         R4新量及算式 |
| ----------------------- | -------------------: | -------------------: |
| baseline完整分析/执行项 |                 2410 |       2410+39+6=2455 |
| C0work                  |              3278484 |  3278484+567=3279051 |
| C0scan                  |              2275119 |  2275119+271=2275390 |
| C0hash                  |               823438 |               823438 |
| ENTRY/G/M0work          | 176580/185814/141562 | 176580/185814/141824 |
| h/s/receipt/H01work     |  8/149538/792/152824 |               均不变 |
| whole-H峰               |       149697/6819815 |                 不变 |
| terminal native+receipt |         12016/272442 |                 不变 |

全部2455个prefix双tape在baseline-prefix-r4.json，不能只用上表替代中间动作。RuleSpec when中的固定Equipment类还需完整Catalog四类扫描60+64+72+64=260B，加fixed-TermInput guard1和declared-reference1，总262work/260scan/6动作；M0141562+262=141824、scan3867+260=4127。其余谓词when不加此类门；head原收费动作不变。

原cap下仍正常成功；payload298403+rows334379=632782B与material85953B原长度不变，当前codec/issuer不由这些新提案字节证明。

## 2. 非string ID 与另一无效外层JSON

nonstring-rule-id的原ID为整数7，原pointer `/datasets/nonstring-rule-id/rules/0/rule_id`。真实前门支付outer mapping1+input mapping1+rule列表1+RuleSpec mapping1+ID type1=5work就拒绝；无ID UTF8、无sort、无allocation、无material/输出。只有C0，F=`14+12×1+20×0=26`，h0/s0，receipt249B，H01=`26+4×249=1022`，总已付1027work。第8项真实metadata错误，第9释放receipt、第10终态释放control，failed/live0。不存在伪造的空child或17L。

outer-input-not-mapping的独立输入为`{"input":7}`，原pointer `/datasets/outer-input-not-mapping/input`。支付dataset1/input1=2work，第5项拒绝；receipt255B，H01=`26+4×255=1046`，总1048work；共7执行项。另有根本身为[]的独立例，第4项拒绝，总work=`26+4×257+1=1055`。不是只给整数ID做一个特判。

late-invalid-rule-id先有一个合法valid-first，第二ID为list；全局门第25项失败，`validatedRuleCount=1/allocationStarted=false`，无任何child。已有workspace1handle/32slots，R252，H01=`26+3+32+4×252=1069`，metadata前缀109，总1178。duplicate ID在第29项对两完整ID额外扫描20B后拒，总1211；释放不退累计票。坏rules容器、disabled容器、revision非字符串、ID非法surrogate也各有完整invoice/pointer，不凭字符串转换修好。

UTF8边界：8192个é为16384B，ID门通过并完整成功；8193个é为16386B，在byte门第11项按结构RESOURCE_LIMIT拒，C0已付9272，未扫描/排序这个超界byte串或发行child。空ID没有已批准的非空要求，本提案保持该字符串的原可编码范围，不把审者探索值当新增业务政策。

## 3. 固定类与合法binding位置

variable-class的Catalog真实声明urn:C，仍不能使head的Variable类位置成为合法TermInput。enabled、disabled、zero-match均在compile:head拒绝，M0 INPUT为1100B：record头5+definitions部分560+Catalog96+17L部分439=`1100`；nodes101，编码work1201；其它静态检查72，合 **1273work**，scan56（变量名4+完整Catalog52），head/firing/output0。enabled/zero-match第86项拒；disabled含完整disabled-ID门，故第90项拒，不能省compile。

上述INPUT原先手估1121B被独立审计实际exit1捕获；source与失败流保留。独立第二编码按固定字段 framing重算1100B，修正的是手算/审计断言，reference和价格未因此改变。

正例固定类TermInput urn:C、Variable subject绑定IRI，完整成功，M0work11145；正例已声明data property的Variable object绑定literal，完整成功，M0work10433。两个正例均有独立手选完整custom数学集合核对，保住真正允许的binding位置，不采用全拒变量。

同一固定条款也适用于when：variable类对象enabled/disabled/零match分别在compile:when第90/94/90项拒绝。标准例plan1207B+109nodes+count3/position3/fixed-class1=1323work，完全未做join；zero-match的额外when使plan1364B+127nodes+7=1498。未声明固定类和literal类另有完整拒绝账；固定urn:C when正例完整成功，M011691，并有独立手选完整集合核对。该门不作用于普通输入RDF图，也不修改legacy。

## 4. 原六例、114与动态权威

原六纯输入不改。晚integer语义首错由27变31；false后类型错191→211；不受控head零匹配52→72、disabled52→76；非法when predicate41→65；较早ENTRY input拒53→57。变化都是其自身E00动作先发生，原错误相对次序/后错不覆盖前错保持。资源例仍已有250824+请求50202>262144，ENTRY已付502398work/input250824、无成功前缀、所有引用清零；额外4个outer guards使C0work2416695+4=2416699。原六receipt/h/s和其它池费用不变。

114逐项独立差表：E00新增work53265/scan25379/事件3928；when类门新增work30699/scan30501/事件657，其中producer M28742/28556/616，实际R16重编译1957/1945/41。hash均无增量。合计事件4585：分析231960+4585=236545，执行231899+4585=236484。113项原cap内；E.5 round4首拒13687+39+6=13732，原M0 input255390+12342=267732>262144，已有work404606+262=404868，原子不扣；分析13800/执行13739。所有正常价格变动分别在每ID明确E00与when类门项，restore重复compile单独列出，不提高原cap、不按actual拟合。

141程序（114固定+原6错误+21本轮focused正反例）两seed核分析/执行hash、金额、paidPrefix、首错及receipt全相同。现行exact与真实同次17L/issuer/usage/owner H仍分别pending；本数学小账不填这些权威字段。
