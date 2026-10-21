# M1 数学值、解释与真实输入补充合同

本轮只交可消费的独立预期、真实来源缺口和精确下一窗口，不实施产品。原83项仍为 **78成功、4资源失败、1缺规则未执行**；数学/解释补充没有使其转绿。原 T05 Goal 维持 blocked；16c/ca0990、dbb、f9af oracle、原 L、Q6、锁和七个 quality 模块均保持原件。I05 九 writer 获根授权是后续实施背景，不是这些组件已经实现或本轮获产品授权的证据。

## 1. 固定输入与交付分离

本稿在原 T05 树、`feature/weekly-t05-quality-reasoning`、base `330fcedb297792e0addd55557688509550c3b26a` 制作。唯一新增范围为本文件及 `docs/reviews/T05/profile-M1-math-explanation-input-contract/`。完整原字节/ref/SHA 绑定见该目录 `fixed-inputs.json`；所有具名 Git 输入均已逐字节对照，不把当前时间或 hash 当真实性认证。

| 固定对象           | ref / 大小 / SHA-256                                                                                                | 本轮用途                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| I05 最终方案       | a3592837d854628948ef4c468b6c839f21763273；69523B；23a4ae9f7974185db61664fb1db892586140ea20995f1bb5950943717bd0ed4c  | §1/7/12真实 producer、selected、M1边界，兼读直接相关源码与载体     |
| I05 实际83 census  | 同上；244280B；a2e7402b597e36458a1f59e8657150c2572cd0df8ef8e653dfc518d51de59d0f                                     | 原始实际结果、未执行、资源与 sourceRefs；不是重跑                  |
| I05 gap report     | 同上；27429B；cff01d1b 前缀，完整值见 manifest                                                                      | 原来源缺档与原执行边界                                             |
| 独立 oracle        | f9af899fad31ea19c7540e9624c437a189b8b5bf；767826B；87220503f9983146c974fe3e35025d520cad70e54fdd994aebfa86fb1ff7259f | 89数学图、40match、完整heads/basis及R04；只读期望，永不喂 producer |
| 根独立读回报告     | 27061B；15d204988ae49a39a512b9eaec2aae6e348abcdab7aa4376cbdef50e2da28c72                                            | C3来源修正、R04真实直接前件、未完成门                              |
| Q6 adopted profile | 16428B；9259f4ac6622857182570509378afb6c96ab5c4dc19d2e887db559c27a282427                                            | 用户已采用规则政策与规范 pin；不重问、不改政策                     |
| 纯机制固定产品     | 16c58c6d0ca56491c7134c4866f9bed5e0f722c5；证据冻结 ca0990a893a6d3af106985fe5dae5ff287b79553                         | Number/Calendar实际字段、既有机制接口的只读参照；不代真实生产链    |

`original-source-gaps.json`是固定 census 的精确摘录，保留五项失败/未执行的诊断与 sourceRefs。新 `math-operand-inputs.json`、`supplemental-graph-inputs.json`、`consumer-C-inputs.json` 是完整的**新增补充输入规格**，与 `*-goldens.json` 物理分开。后续 producer 只能读取这三个独立源文件的原输入或真实 owner 供源；禁止读取 goldens、oracle、expected、根报告构建输入/Context/Job/finish。输入没有原 Turtle token 时明确 unavailable，不从 N3 展示串逆推。

## 2. 规则数学观察：字段与可读值

独立预期由采用政策、手工关系表及标准库整数/Fraction 算式得出，没有 import/调用被测 parser、比较器、reasoner 或恢复器。`assemble-independent-goldens.py` 从独立作者常量同时落出不含expected的 `math-operand-inputs.json` 与分开的goldens，只展开已选数学常量、有限 truth rows 和十进字符串；不是通用量化器。数学producer读取math输入，按family/id从外部golden断言，绝不启动时反读golden取operand。源/数学 helper 均只读；固定稿另交第三方 agent 独审，意见和修订留存。作者临时算式的首次 SyntaxError 与修正记录在 `author-method.json`，不冒充产品失败/通过。

现有私有记录准确为：

```text
Number(numerator:int, denominator:int=1, negative_zero:bool=False)
Calendar(day:int, second:Number, explicit_offset:bool, is_datetime:bool)
ProfileValue(term, domain, value, language="")
```

Number **没有 kind/width 字段**。实际 datatype/原词法归 term，域归 ProfileValue。golden 里大整数用十进字符串存储，仅为文档期望表示；未来断言转换 exact int，不以此新增公共 codec/DTO。每项实际观察应同时给出原 term、domain、完整 Number/Calendar 数学字段、comparison Boolean或私有 reason/location，不能只看 bits、bytes、digest、计数或 eq 的最终值。任何投影必须由 I05 已有生产/strict restore/selected carrier 暴露真实值，不从 golden 回填缺字段。

### 2.1 九域、六算子与六 numeric

`domain-operator-goldens.json` 明列486个九域有序pair/operator分类槽，另明列36个 numeric 有序datatype pair×6算子的216细化槽，各取小于/等于/大于三种实例，共648条 numeric 实例。它们是预期数据量，**不是运行通过数**，也不声称穷尽无限词法值域。算子固定 `eq/ne/lt/le/gt/ge`。

| 已独立确定关系 | 六项实际 Boolean      |
| -------------- | --------------------- |
| 左小于右       | F / T / T / T / F / F |
| 相等           | T / F / F / T / F / T |
| 左大于右       | F / T / F / F / T / T |

N、S、同小写标签L、Dz、Dl、Tz、Tl同域支持全部六算子；I/B仅eq/ne。所有跨域六项均 `RULE_COMPARISON_TYPE_MISMATCH`，ne也不自动true；不同小写标签的L亦如此。合法性/支持域/原预算先校验，不允许把 NaN、坏日期或未知 datatype 当 false。

六 numeric 为 integer/int/nonNegativeInteger/decimal/float/double。值为2的六种原写法均 Number(2,1,false)，term仍不同。混型比较按各**实际精确值**，不使用 SPARQL 有损 numeric promotion：

| 原写法                                    | 数学值                               |
| ----------------------------------------- | ------------------------------------ |
| decimal `0.1`                             | 1/10                                 |
| double `0.1`                              | 3602879701896397 / 36028797018963968 |
| float `0.1`                               | 13421773 / 134217728                 |
| integer `16777217` / float同词法          | 16777217 / 16777216                  |
| integer `9007199254740993` / double同词法 | 9007199254740993 / 9007199254740992  |

float0.1 > double0.1 > decimal0.1；与decimal的正差分别为1/671088640、1/180143985094819840。上述差和全部六算子真值在 `number-goldens.json` 明列。integer/decimal `-0`为Number(0,1,false)，float/double为Number(0,1,true)，有符号零仍按相等行比较；原 lexical 不消失。

### 2.2 一次 binary32/binary64 舍入

`number-goldens.json` 固化实际十进 lexical、舍入前精确p/q、舍入后Number及逐项理由；只做原十进有理到目标宽度的一次 nearest-ties-even。32的p=24、emin=-126、emax=127，64的p=53、emin=-1022、emax=1023。q分别为2^-149、2^-1074。

| 输入数学值                              | 预期及理由                                                          |
| --------------------------------------- | ------------------------------------------------------------------- |
| 32：1+2^-24 / 1+3×2^-24                 | 1 / 4194305÷4194304，分别取偶低端/偶高端                            |
| 64：1+2^-53 / 1+3×2^-53                 | 1 / 2251799813685249÷2251799813685248                               |
| q/2 / -q/2                              | 正零 / 负零；保存negative_zero                                      |
| q / 3q/2                                | q / 2q；最小subnormal与偶数tie                                      |
| 2^emin−q/2                              | 最小normal，不能当作零或截断                                        |
| maxfinite                               | (2^p−1)×2^(emax−p+1)                                                |
| overflow midpoint−1                     | maxfinite                                                           |
| overflow midpoint=2^(emax+1)−2^(emax−p) | UNSUPPORTED_NONFINITE_LITERAL；合法词法舍入到∞，不能clamp或报词法错 |

杀死双重舍入的真实lexical为
`1.00000005960464477539062582718061255302767487140869206996285356581211090087890625`，即1+2^-24+2^-80，直接32应为8388609/8388608；若先64抹去2^-80再32会误成1。长subnormal lexical已完整落入JSON，最长约1077字符，未提高原限额。不得用宿主float、默认Decimal精度或bytes反解产出golden。

### 2.3 S、L、I、B、四日期域与错误

`term-error-goldens.json` 固定每项词法、结构与私有reason：S按XML1.1选定Char及Unicode码点序，U+10000 > U+E000；é > e+combining acute，不做NFC。L是Unicode scalar词法，标签仅RFC5646 ABNF，ASCII lower；EN-us/en-US为同标签，不做registry/alias/fallback；不能无依据给L加S的XML Char限制。I完整拼写身份、只eq/ne，不折scheme/host/percent/Unicode空白；Unicode NBSP向量以已闭dbb修复为基线。B的true/1值相等但term不同，不混入N。

int越界、nni负数、decimal指数、外围空白/非ASCII数字、boolean True/+1/01、非法日期/offset/24点/闰秒为 `INVALID_LITERAL_LEXICAL`；合法NaN/±INF与上溢为 `UNSUPPORTED_NONFINITE_LITERAL`；未知合法datatype为 `UNSUPPORTED_LITERAL_DATATYPE`；结构矛盾/相对IRI/非法算子为 `INVALID_RULE`，非str算子为现有 `INTERNAL_ERROR`。这些是私有reason，不新造公共E3或DTO。资源错误仍按实际旧分类/location/adapter保留，不从本表发明新限额。

`calendar-goldens.json`明列15个完整Calendar，epoch=0000-03-01。独立核算采用January-origin日计数，与产品March/era实现不同。举例：

| 原lexical / 类型                                          | day             | second p/q                               | explicit_offset / is_datetime |
| --------------------------------------------------------- | --------------- | ---------------------------------------- | ----------------------------- |
| date 0000-03-01Z                                          | 0               | 0/1                                      | true / false                  |
| date 0000-03-01                                           | 0               | 0/1                                      | false / false                 |
| dateTime 0000-03-01T00:00:00Z                             | 0               | 0/1                                      | true / true                   |
| dateTime无Z同写法                                         | 0               | 0/1                                      | false / true                  |
| date 0000-03-01+14:00 / 0000-02-29-10:00                  | -1              | 36000/1                                  | true / false                  |
| dateTime 0000-03-01T00:30:00+01:00 / 0000-02-29T23:30:00Z | -1              | 84600/1                                  | true / true                   |
| dateTime 0000-02-29T24:00:00.000Z                         | 0               | 0/1                                      | true / true                   |
| dateTime 0000-03-01T00:00:00.1234567890123456789          | 0               | 1234567890123456789/10000000000000000000 | false / true                  |
| date -0000-03-01 / -0001-03-01Z                           | 0 / -366        | 0/1                                      | 见原JSON                      |
| date 0400-03-01 / 0400-02-29                              | 146097 / 146096 | 0/1                                      | false / false                 |

所有second.negative_zero=false。减去offset后floor分日，无系统TZ、DST或微秒截断。Z/+00:00/-00:00均explicit，absent不同域；date与dateTime不互cast。即使day/second相同，四域间六算子仍类型错。它只规定规则profile，不能据此改query/SHACL的时间比较。

## 3. 完整match、heads、basis、source与直接层次

`supplemental-graph-inputs.json`给五个完整独立输入，`explanation-goldens.json`另给独立预期：

1. 两个原match中s1的integer01与阈值1相等，s2的0为false。s1保留三个head occurrence，其中索引0/1为相同type triple、索引2为label；输出RDF集合只有两条，不可把head索引去重。每match的when、bindings、comparison Number、定义ordinal/source、leaf basis逐项对应。输入包含实际owl.Class/DatatypeProperty声明，Catalog从这些真实ontology三元组提取；schemaVersion1规则JSON是源定义，仍须真实T01/I05 binder转成typed RuleSpec，不是直接调用semantic.reason的参数，也不能把golden里的Catalog当生产输入。false仍在原完整originalMatches，不能通过只收accepted漏掉。
2. false后错误：绑定v=integer0、w=string1；先v>integer1为false，后w=integer1为类型错。原有全comparisons验证必须整任务失败、无成功前缀/heads/batch。**没有产品/UI源依据要求新增持久false trace**；只沿现有originalMatches与整体失败验收，不新增false ComparisonEvidence合同。
3. 直接层次：asserted x-p-y及ontology p-domain-A、A-subClassOf-B。d1以有序前件[domain公理, asserted事实]得x type A，depth1；d2以[d1, subclass公理]得x type B，depth2；d2叶basis是全部三条，不能把叶集合标成两个直接前件。这是新增补充图，原R04仍按f9af固定t0117/t0116→t0063、depth1，不回写oracle。另有range和subclass-transitive两个唯一witness小图，分别固定有序直接前件/叶basis/depth1，使四种既有finite规则都有可读预期。

source逐项绑定实际输入文件+JSON pointer，定义right与绑定left分开；原字节digest由交付manifest绑定。结构化N3展示不是导入前原token，byteSpan=null，不编字节定位或认证。后续真实生产必须观察原source revision/section/index和可得token，无法取得时显式unavailable；fixture source不代实际Store来源。

### 3.1 I05直接步骤的唯一真实切点

固定3ef `semantic.py::_finite_closure` L385–448只有一次闭包，候选按result key及ordered input keys稳定排序。L426–446的`if triple not in closure`首次插入旁仍有本次实际选中`inputs`，随后只union叶basis并存proofs。这里是I05将真实direct edge、finite rule kind、result、ordered direct refs及depth一起capture的唯一建议切点；不能解释时第二次reason、重扫图构造另一套proof，不能从leaf union倒推，也不要求枚举全部alternative proofs。

建议在原loop内传递小型候选rule标记，只在实际新triple首次插入时保存一个witness。原asserted/ontology leaf depth0；新step深度1+max直接前件depth，引用此前已存在的leaf/step；用单调step ordinal禁止循环，不按结果词典序假定拓扑。当前四个finite规则每步两个直接前件（subclass传播、subclass传递、domain、range）；不是任意RDFS全规范。capture开关/返回结构需由I05明确迁移全部消费者，不能直接破坏旧`return closure,proofs`兼容。

当前`_profile_reason` L1059–1072的rdfsEvidence只有result/basis/proofLeaves；`semantic_scopes.py` L91–98旧selected严格五key；纯Number/Calendar字段已足够数学解释，但direct-step不是现有字段。建议新载体候选名 `i05-direct-rdfs-steps/1`（**提案未采用**），由I05在新production/fullview/codec/strictrestore/selected同步版本：结果、每步有序ref、depth、叶source与basis都保持；不得塞进3ef旧strict schema、重签历史或在现有i05-finite-7下冒充兼容新增。公共执行/implementation版本仍归I05/T01/根冻结，不在本稿自行决定。

预算建议只作为精确供应窗口：capture前分别核步数、两条直接边/步、term原字节、source、编码、解码与保留live量；新增step数≤实际新增closure triple数、边数≤2×step数，但source/term字节及重复occurrence不能据此省略。C实际捕获、T传输、各R_j/聚合restore、S投影、H活跃/退役保留分别预留/计费；失败不退累计费、无半发布。深度/refs严格校验不重reason；source长度/保留生命周期由owner给真实上限。**不把新扫描/解释费用塞进旧L，不改变原profile/batch预算**，也没有RSS/耗时性能证明。

## 4. query 与 SHACL 各自的 C 格及实际入口缺口

`consumer-C-inputs.json`给13个完整Turtle/query/shape规格，独立 `consumer-C-goldens.json`区分规范预期和当前入口拒绝。规则的exact rational类型政策不能改写query/SHACL。SPARQL采用其operator mapping及numeric promotion，query FILTER错误剔除该行；SHACL inclusive对自身SPARQL比较不为true时产生普通validation result。来源为固定[SPARQL2013 §17.2](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#OperatorMapping)及[SHACL2017 §4.3.2/4](https://www.w3.org/TR/2017/REC-shacl-20170720/#MinInclusiveConstraintComponent)。

| C格                                    | 独立预期                                                     | 固定I05现状/不能替代                                           |
| -------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| query integer16777217 = float同词法    | numeric promotion后选中s；规则profile则false                 | 需实际query观察，不借rule结果                                  |
| query string a < integer1              | 空rows                                                       | FILTER类型错不是规则Job失败                                    |
| datatype xsd:int数据、xsd:integer约束  | DatatypeConstraintComponent违规                              | datatype IRI精确相等，不做subtype推断                          |
| datatype rdf:langString                | 合法@en数据应conforms                                        | `_DATATYPES`不含rdf:langString，L1226–27先UNSUPPORTED_DATATYPE |
| maxCount1，integer01及integer1两个term | 2个value node，MaxCount违规                                  | 值相等不能去重RDF term                                         |
| sh:in仅integer1、实际integer01         | In违规                                                       | membership按RDF term身份                                       |
| min/maxInclusive integer2等于界        | conforms                                                     | 自身inclusive规则                                              |
| nni minInclusive合法界                 | conforms                                                     | inclusive白名单未含nni，当前INVALID_SHAPE                      |
| 显式offset dateTime等值双inclusive     | conforms                                                     | dateTime合法界先过_terms，随后numeric-only白名单INVALID_SHAPE  |
| dateTime比min小一秒                    | MinInclusive违规                                             | 同上，未到Validator不能算违规已证                              |
| string数据、numeric minInclusive       | 普通MinInclusive违规                                         | 不是adapter错误；前提为合法图到达Validator                     |
| date合法minInclusive                   | 当前INVALID_SHAPE；后续需单独冻结query/date operator支持政策 | profile Dz相等不能证明SHACL date conforms，未虚构规范结论      |
| illtyped integer数据                   | SHACL直接规范为Datatype违规；现_terms先拒绝                  | 两种入口事实分开，不虚称正常report已生成                       |

datatype exact identity、count及in的依据分别为[SHACL §4.1.2](https://www.w3.org/TR/2017/REC-shacl-20170720/#DatatypeConstraintComponent)、[§4.2.2](https://www.w3.org/TR/2017/REC-shacl-20170720/#MaxCountConstraintComponent)、[§4.8.3](https://www.w3.org/TR/2017/REC-shacl-20170720/#InConstraintComponent)。本表未要求拿规则比较器替换Validator。

精确静态切点：`semantic.py::_terms` L53–97允许合法数据lang literal；ill_typed date/numeric、非有限和unsupported literal datatype可能在此先拒绝。`_shapes` L1171先_terms，L1226 datatype名单拒langString，L1235–1240 inclusive名单只integer/int/decimal/float/double且notilltyped。有效date/dateTime参数不是在_terms被拒，而是在该白名单被拒；不要统称lang/date都被前置阻断。`check_shapes` L1254继续真实Validator，no inference/no ontology。最小修改仅归I05入口与相应合法/非法分组测试；当前FR504五模板/双scope的完整原验收仍未关闭。

后续report比完整focusNode/resultPath/value/sourceShape/component/severity与conforms；report bnode只按结构对应，不发明固定内部ID/序列化。[SPARQL §17.3.1 operator extensibility](https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#operatorExtensibility)允许把原type-error扩为额外类型关系；本稿独立列出date两分支，I05须在实际入口中绑定自己的固定政策。date支持政策及真实source未给时继续明确未证，不能改成永久unsupported来关闭M1。

## 5. 原83项与真实补源责任

原实际成功49/89数学图、24/40match=15true+9false、16head refs；计划51 eligible图不是实际成功49。40未成功关联图分为9行为提交、24E5 event/behavior/commit、2取消、2导入、1course增量、2repair。原18比较extension全为integer；本稿矩阵不改其覆盖事实。

| 缺口                   | 原源文件/pointer（f9af，approved-T09-873c8c0内）                                                    | 供方与必须发生的真实操作                                                                                                          |
| ---------------------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| e001–e016              | tests/fixtures/product-baselines/E.5.json，/initialFacts/0、/rules/0、/events/0…15/payload/addFacts | T06/T07实际事件注入→规则→行为→capacity/resource→commit；T01供Job/version/队列/消费/触发状态；I05逐debit定位原失败，不猜热点       |
| ontology-model         | content/learning/course.json /tasks/0                                                               | T02/原owner给真实prior完整project snapshot和四条实际增量，不从oracle补base                                                        |
| transfer:repair        | content/learning/transfer-inputs.json /repair                                                       | T09/T05/T02原owner确认规则本来不存在还是缺档，并给实际SHACL shape/修复/前后asserted graph。ruleVersion不推出R-risk，不空rules造绿 |
| learning-report        | content/learning/checks.json /checks/learning-report                                                | T10给真实RDF项目/version/生命周期输入和实际报告；此处原件仅expected输出flags                                                      |
| G-list-13中间编辑/undo | tests/fixtures/product-baselines/cases.json /cases/33/steps/3                                       | T02/T01路由实际selected subject、最后确认edit/ChangeSet，再实际undo；不能编equipment001或整库重置                                 |
| G-list-05迟到V1        | 同cases /cases/25                                                                                   | T06/T07执行owner与T01 Job/worker给真实V1完成轮次、历史payload/terminal/token，不能用V2/current/expected反推                       |

五项originalInputContext缺口与四个E5资源失败是不同清单。完整source SHA及每失败case原sourceRefs见 `original-source-gaps.json`；owner细化及逐事件mapping见 `source-supply-and-windows.json`。E5源169895B/e81b0d02…，e001–004属r1、005–008属r2、009–012属r3、013–016属r4。每match前件为同一Equipment事实和对应alarm的High、Open、alarm link，alarm rdf:type不算R-risk前件；16个match可以共享同一head，不能用一个head顶16次真实运行。

原probe只是initialFacts加累计4/8/12/16事件facts的四个fragment，fullOriginalInputContext=false。r1/r2实际 `RULE_INPUT_BUDGET`、ruleIdR-risk、semanticInput；r3/r4 `WORK_LIMIT`、ruleIdnull、semanticWork。原probe/checker均exit1，没有定位到单一debit热点，不据此提高L或承诺性能。repair为缺rules未执行，合法SHACL修复的真实产品入口必须补证。

## 6. 可申请的最小实施/验证窗口

本轮没有写下列未来产品路径。`source-supply-and-windows.json`列完整ref/旧SHA/最小delta；新增路径oldSHA=null并核不存在，existing若根的新I05九writer候选已漂移，必须由根按新固定SHA重列，不能拿旧SHA直接覆盖。

| owner / future路径                                                                                                                               | 最小delta与验收                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| T05新fixture `tests/fixtures/quality/profile-M1-math-explanation-inputs.json`                                                                    | 采用本轮独立输入/expected分离规格；扩nine-domain/sixnumeric typed observations、完整head/source，不修改f9af原oracle                             |
| T05新test `packages/engine/tests/test_profile_M1_math_explanation.py`                                                                            | 从真实I05获准producer输出观察Number/Calendar及完整解释；独立expected只用于断言，拒绝expected→production依赖；当前不存在，不在本轮创建           |
| I05 semantic.py，旧52609B/SHA5a3a53fc…                                                                                                           | closure首次插入capture一步direct witness；langString/nni/dateTime合法shape guard；date政策独立冻结；保四finite规则/firstwitness及旧入口错误边界 |
| I05 semantic_execution.py / semantic_scopes.py / semantic_profile_restore.py；新production/selected writer                                       | 新typed/fullview carrier含directstep，capture→codec→strictrestore→selected一版同步；T01物料/source真供应，不改旧schema签名                      |
| I05 test_semantic.py / test_semantic_lexical.py                                                                                                  | query promotion/FILTER与SHACL合法入口、普通违规、前置拒绝分组，不导rule comparator                                                              |
| I05 test_semantic_rdfs_basis_determinism.py                                                                                                      | depth2真实steps、ordered refs、leaf union各自完整比对，保原stable witness/seed顺序                                                              |
| I05 test_semantic_profile_restore.py / test_semantic_selected_projection.py / test_semantic_execution.py / test_semantic_scopes.py及其已授新测试 | 最后Calendar/Number/source/step/depth篡改拒绝、restore与selected完整值无损、真实单目标裁剪、预算差1无半发布                                     |

T05七quality模块的所有权和16c原件维持；没有证据需要改其数学机制，因此本轮建议该七模块delta=0。`semantic_profile_restore_budget.py`同样只读；若新R载体确实需扩预算，应由I05另列该文件精确最小diff向根申请，不隐含授写。T01 Store/受理/owned worker/canonical和T03锁/构建均无本轮delta。

下一实施窗口只需根按上述固定路径授I05真实directstep+shape入口/新carrier和T05新增fixtures/tests，并先落实缺源owner；复用其已经获准九writer任务，避免另开全链方案。下一验证窗口的最小实际证据为：

1. 在获准真实内部Job/原Store/owned worker链上，用**输入文件**生产一次，观察完整typed数学值、false后错误整批失败、全部heads/basis/source。通过真实producer保存→关闭重开→新worker strictrestore→同consumer selected读取，goldens只供外部独立断言。
2. 按486分类槽、216numeric细化槽及648关系实例逐ID记录actual，不只汇总；舍入/Calendar/term边界单独列，query/SHACL13C格按自身规范与实际入口状态分别列。date政策未定格明确pending，不伪成功。
3. directstep源、序、depth、basis、Number/Calendar任一尾字段损坏均有限失败、无成功前缀；C/T/各R_j及聚合/S/H实际分池上限exact/差1，不借原L或缓存清账。只验本次最小delta与对应原回归，旧check结果不当新组合运行。
4. 原83单独维持逐ID状态；补齐E5/repair/中间状态后才允许真实运行并读回，保原失败原件。新数学输入从不替原场景，也不提前关闭FR501–505、57P0、UI/平台/性能/指定双审/CI/merge等父门。

上述运行均为**后续根精确授权窗口**，本轮仅静态文档/JSON/Git/哈希/格式检查与独立文档算式审查，不import/运行产品、不新建worker、不GUI/native/HMR/模型/付费/构建/包/push/PR/merge，不操作Goal状态。最终固定ref、manifest和独审处置见本目录交付回执。
