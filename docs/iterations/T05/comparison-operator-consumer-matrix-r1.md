# T05 比较算子、跨域及消费者矩阵 r2（文件路径保留r1）

当前状态更新（2026-10-21）：用户已明确采用Q6推荐规则及固定规范版本，采用原件SHA328a59c42ae69a5c2426c494c1c979cb629692f389cdacf591e8789738c6b4f0。下文较早“待Q6/未采用”是当时请求/答复状态，不再构成政策阻塞；实际政策与拟阶段实施以[已采用profile](q6-adopted-profile-v1.md)和[阶段规格](q6-profile-mechanism-stage-plan.md)为准。实施阶段仍待root一次授予，不改变依赖/公共格式/路径/运行验收门。

**供下一次具体审定，不是实现或验收结果。** I05对D2–D5的技术答复与T05补充提案分别标记；全部值政策仍需Q6采用、规范pin及真实完整矩阵。当前规则没有值比较/多head；未批准C3不能作为T05依赖。

来源：固定I05 `ffc462b2332dfb8af7c15c91adb3ac1f7ac1b24d` 的owner-response（SHA `723368ccc8902c70dcd28939f7b4a21f7dc6d8488d39c7b981b1952caf33fc4e`），状态/路径接受见[当前决策表](owner-decisions-after-interface-facts.md)。本文不改变query/FILTER/cast，不新增公共协议或错误枚举。r2按总控独立复核17603B/SHA70909867a8786f181639810c3c40d188f92c2849311dd148f6bf55fce044705a修正R1/R2；固定383b96c的r1保留Git，不回写其旧审查为已发现这些问题。

## 1. 单元格含义与政策前置

- `V`：在合法、有限、预算内operand上，此操作有明确定义，返回真实true或false；**不表示结果必为true或已有运行通过**。
- `E3`：规则类型/操作不兼容，整任务失败。拟用I05已技术接受但尚未实现的新reason `RULE_COMPARISON_TYPE_MISMATCH`，在REASON/RULE/VERIFIED_USER_INPUT上下文映射现有`SEMANTIC_INPUT_INVALID {field:rule}`。
- `E1/E4/E5/E6/E8`：分别为坏定义/operand结构（M1）／非法词法（M4）／合法但未支持类型（M5）／合法非有限或舍入溢出（M6）／实际资源超限（M8），按当前M表区分处理。先完成适用的定义、类型、词法与预算校验，再对合法值判断V/E3，不能拿不合法值进入关系比较后再补false；本记号不新增adapter reason或公共错误。
- 固定技术方向：三元组join、head、graph去重仍按原term身份；值eq不能重写01/1、±0或其他原term。先验证全部定义常量与变量闭合；坏定义不因零匹配而隐藏。合法join无解成功空集合。每个完成when的binding按稳定位置校验**全部**comparisons，不因前一个false隐藏后一个错误；全真才产生全组heads。

状态标记：`I`＝I05技术接受/推荐，未Q6采用、不证明实施；`T`＝尚未取得技术接受的提案。固定96fb597新回复已技术接受S/L/I-B/X，现下表同步I；来源及未实现项见[联合接受表](accepted-policy-and-q6-scope-r1.md)。规则可比域/操作是应用政策，不由Python类型或当前库排序推断；RDF1.1既有抽象term身份不是可选政策。

## 2. 同域六算子逐格表

| 域／适用值                                                                  | 状态 | eq  | ne  | lt  | le  | gt  | ge  | 比较定义／明确拒绝点                                                                                                                                                                                                                                       |
| --------------------------------------------------------------------------- | ---- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| N：integer、int、nonNegativeInteger、decimal、float、double；任意这六型组合 | I    | V   | V   | V   | V   | V   | V   | 严格原词法解析。整数精确、decimal精确十进有理；float/double由精确词法有理值直接按binary32/64 normal/subnormal nearest/ties-even舍入，再取实际有限表示值的精确有理数比较。禁止先binary64再binary32、禁止将整数/decimal有损提升为float。int/非负值域检查保留 |
| S：RDF1.1 xsd:string抽象域；输入可省写datatype                              | I    | V   | V   | V   | V   | V   | V   | 相同lexical form的simple无lang与显式xsd:string本是同一抽象term，非待选合域。待审的是六算子/Unicode码点字典序，不trim/casefold/NFC/locale/转数值；source引号/转义/显式datatype拼写另存                                                                      |
| L[t]：rdf:langString，双方同一语言标签域t                                   | I    | V   | V   | V   | V   | V   | V   | 入口先验BCP47 well-formed；标签value为小写，建议内部/抽象表示统一小写并另保留source原拼写，待owner落实。合法同标签域文本按S比较，不同标签en/en-US不回退且六操作E3为待审规则政策，不由value比较反推join/去重已实现                                          |
| I：IRI与IRI                                                                 | I    | V   | V   | E3  | E3  | E3  | E3  | 建议eq/ne为完整IRI身份；不解引用、URL解码、大小写折叠或拼写规范化。不给IRI业务大小顺序；即使两IRI相同也不将le/ge当true                                                                                                                                     |
| B：boolean与boolean                                                         | I    | V   | V   | E3  | E3  | E3  | E3  | 建议合法true/1对应true、false/0对应false的值相等；原词法/term不合并。不给布尔大小顺序，不利用Python bool继承数字                                                                                                                                           |
| Dz：date，双方有显式offset                                                  | I    | V   | V   | V   | V   | V   | V   | 独立Gregorian日序＋精确秒；取原本地日期00:00:00起点减各自offset后比较，不采用隐含时区或声称完整date区间部分序                                                                                                                                              |
| Dl：date，双方无offset                                                      | I    | V   | V   | V   | V   | V   | V   | 同一本地日历域起点比较，不补Z或读取机器时区                                                                                                                                                                                                                |
| Tz：dateTime，双方有显式offset                                              | I    | V   | V   | V   | V   | V   | V   | 独立日序＋完整小数秒的精确有理秒，减各自offset比较；不受Python datetime微秒/年份表示截断                                                                                                                                                                   |
| Tl：dateTime，双方无offset                                                  | I    | V   | V   | V   | V   | V   | V   | 同一本地日历域比较，保留完整秒精度，不推测时区                                                                                                                                                                                                             |

D3补充：±0值相等但保留符号/term；合法subnormal和舍入下溢到有符号零按声明舍入，不一律拒绝。合法NaN/±INF（含+INF）、有限词法舍入为无穷为E6；非法拼写E4。巨大词法/指数在构造幂或大整数之前检查位长和工作预算，不能把预算错误改成词法错误。

D4补充：I05推荐pin XSD1.1词法/日历，涵盖年零/负年、闰日、合法24:00进位和offset边界；**确切规范版本/章节及fixture仍待Q6审定，本表未完成规范pin**。独立calendar-value是明示应用政策，不能仅因宿主parser可cast就宣称支持。date起点与dateTime时刻分域；无隐式互cast。

R2分层：RDF1.1无lang simple literal只是xsd:string的输入语法糖；相同解码lexical form即同一抽象term，不由Q6决定合并与否。RDF语言标签必须BCP47 well-formed，其标签value小写；规范允许来源表示转小写，本合同建议入口统一小写的内部表示并另留source原拼写，技术落实待owner确认。随后才选择L同标签值比较/跨标签拒绝；不能把非法标签当“合法但不同域”，也不能仅由L比较结果证明join/图集合/SHACL正确。[RDF1.1 Concepts，2014-02-25 REC §3.3](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/#section-Graph-Literal)

## 3. 跨域逐格表：每格同时列六operator结果

`A6=V/V/V/V/V/V`，`Q2=V/V/E3/E3/E3/E3`，`X6=E3/E3/E3/E3/E3/E3`，顺序固定为eq/ne/lt/le/gt/ge。矩阵对所有有序域对生效；N包括六numeric datatype的全部36个有序组合。除明确的N混型，其余不同域全部X6，不把不兼容eq/ne变成false/true。

| 左＼右 | N   | S   | L[t] | I   | B   | Dz  | Dl  | Tz  | Tl  |
| ------ | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
| N      | A6  | X6  | X6   | X6  | X6  | X6  | X6  | X6  | X6  |
| S      | X6  | A6  | X6   | X6  | X6  | X6  | X6  | X6  | X6  |
| L[t]   | X6  | X6  | A6*  | X6  | X6  | X6  | X6  | X6  | X6  |
| I      | X6  | X6  | X6   | Q2  | X6  | X6  | X6  | X6  | X6  |
| B      | X6  | X6  | X6   | X6  | Q2  | X6  | X6  | X6  | X6  |
| Dz     | X6  | X6  | X6   | X6  | X6  | A6  | X6  | X6  | X6  |
| Dl     | X6  | X6  | X6   | X6  | X6  | X6  | A6  | X6  | X6  |
| Tz     | X6  | X6  | X6   | X6  | X6  | X6  | X6  | A6  | X6  |
| Tl     | X6  | X6  | X6   | X6  | X6  | X6  | X6  | X6  | A6  |

`*` L[t]×L[t]只用于相同标签域；L[t]×L[u]（t≠u）明确为X6。S的抽象term同一性按RDF1.1固定；S六算子、L合法标签间的可比域及算子、IRI/boolean只提供eq/ne均已获固定96fb597的**I05技术接受，仍待Q6产品采用与真实实施证据**。D2失败原则及D3/D4原接受保留，不把技术答复变成整表运行通过。

### 下一次审定的同域／跨域见证（手工政策期望，未运行）

| 左／右示意                                                               | eq    | ne    | lt    | le   | gt    | ge    |
| ------------------------------------------------------------------------ | ----- | ----- | ----- | ---- | ----- | ----- |
| S：文本10／文本2                                                         | false | true  | true  | true | false | false |
| S：simple文本a／显式xsd:string文本a（同一RDF1.1 term；算子待审）         | true  | false | false | true | false | true  |
| L[en]：a／b                                                              | false | true  | true  | true | false | false |
| L：source en/EN按建议小写表示均为en，同文本a（入口表示待落实，算子待审） | true  | false | false | true | false | true  |
| L[en]：a／L[fr]：a                                                       | E3    | E3    | E3    | E3   | E3    | E3    |
| I：urn:x／urn:x                                                          | true  | false | E3    | E3   | E3    | E3    |
| I：urn:X／urn:x                                                          | false | true  | E3    | E3   | E3    | E3    |
| B：true／boolean词法1                                                    | true  | false | E3    | E3   | E3    | E3    |
| B：false／true                                                           | false | true  | E3    | E3   | E3    | E3    |
| boolean true／integer 1；IRI urn:x／字符串urn:x                          | E3    | E3    | E3    | E3   | E3    | E3    |
| date无TZ／date带TZ；dateTime无TZ／dateTime带TZ；date／dateTime           | E3    | E3    | E3    | E3   | E3    | E3    |

这些见证补充原22例，不替代D3数值精度边界、D4完整日历/时区/精度、所有类型及失败路径的真实完整矩阵。定义常量无匹配仍先校验；先false后坏operand、两个heads中一head失败也必须纳入验收。

## 4. 图入口、query及SHACL消费者逐格提案（R1修正）

`G`＝保留原RDF位置/外联/schema及入口能力门；`N`＝获批新reason/selected以同一原词法validator/comparator实现D3/D4。`C`＝须由实际owner明确该消费者支持范围、保真预检、失败入口/context及运行证据；**保真目标是消费者自己的合同，不要求query/SHACL与规则D3/D4碰巧同值**。这些是待接受合同，不是当前实现缺陷结论。

SHACL列固定以下独立目标（仅原有限模板，不承诺完整SHACL）：

- `K` 数量／成员：required以minCount等原模板表达，maxCount按选定path的value-node集合计数；allowedValues使用sh:in的RDF term成员关系。不能按数值eq折叠不同term，也不按source记录行数重复计同一个抽象term。
- `D` sh:datatype：value须为Literal、datatype **IRI精确相同**；对SPARQL1.1所支持的datatype还须不是ill-typed。仅数值同值或子类型关系不能代替精确IRI。非Literal、IRI不符或适用的非法词法产生validation result。
- `R` sh:minInclusive/maxInclusive：分别以SPARQL表达式`$minInclusive <= v`／`$maxInclusive >= v`判定；不返回true，包括false及type-error，均产生带实际`sh:value`的validation result。**不转成规则E3整任务失败，不替换成D3/D4精确比较器**。shape参数仍须满足该组件自己的语法要求。

当前能力补记（I05固定96fb597设计报告事实，非本线实测）：min/maxInclusive shape参数仅integer/int/decimal/float/double且not ill_typed，**不是任意Literal，日期shape边界尚未支持**；`sh:datatype rdf:langString`不在当前shape白名单，明确未支持。下列D/R为规范目标，不能反推这些shape已可运行；若扩展须单列范围/授权/真实shape-data证据，未支持格保留，不能缩减完整原验收。

以上规范目标见[SHACL 2017-07-20 REC §§4.1.2、4.2.1/2、4.3.2/4、4.8.3](https://www.w3.org/TR/2017/REC-shacl-20170720/)。普通违规是验证产物，不是adapter异常。真正的能力不足、资源/执行故障按真实入口/context有界失败并保留未完成格，不能伪造空报告；**不能只因规则政策与SHACL政策不同就拒绝原本可正确验证的输入**。

| 值／情形                                                      | 图入口→新reason／新selected                                       | query term匹配/投影                                                    | query值运算/FILTER                                                               | SHACL K：数量／sh:in                                              | SHACL D：sh:datatype                                                                                        | SHACL R：sh:minInclusive/maxInclusive                                                                                                |
| ------------------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| S/L/I/B普通合法term                                           | G＋N；用RDF1.1抽象term，源拼写另存；IRI位置/标签/布尔词法保留     | 按抽象term；省写xsd:string不制造新term，不由新规则value eq合并其他term | 保持既有有限query自身政策；boolean顺序等不能由规则B的E3推断                      | K；IRI也是可计数/成员value，不强制变Literal                       | D；IRI节点面对datatype约束是违规而非Internal；string与langString不因文本同文相同                            | R；数据与合法Literal边界不可比较时给违规，不能套规则I/B无顺序政策                                                                    |
| integer/int/非负/decimal，预算内                              | G＋N：精确值/值域；term词法不数值归一                             | 保持词法/datatype不同的term身份                                        | 保留query数值提升/表达式政策；与D3不同不自行变能力错误                           | K；01/1及int/integer即使数值等仍可不同term                        | D；要求integer而值为int须违规，不按D3 N域混型放行                                                           | R；按自身SPARQL关系，正常false/type-error均违规，不能强制D3跨型精确比较                                                              |
| float/double，含声明精度边界及跨型                            | G＋N：D3直接目标精度舍入，禁止二次舍入；原term保留                | C证明既有term路径无有损改写后按term处理                                | C以query既有合同检查支持/有损点；不因与D3解释不同直接拒绝，不默改其提升政策      | K；不能先量化重写lexical后计数/成员                               | D只查精确datatype及适用词法，不要求与D3比较同值；合法边界不能因库值不等就算datatype违规                     | R采用自己的SPARQL关系/提升及实际词法值域；若真实无法正确评价，C给明确缺口和补齐责任，不拿D3结果冒充                                  |
| date offset／dateTime完整小数秒，及年零/负年/大年份/24:00边界 | 原graph ill_typed/宿主范围可能先挡；N要在获批入口可达，不全局关门 | C核抽象term/源拼写保真与可判定的term用途，不以宿主日期截断代替         | 保持该query自己已声明的日期合同；真正无法支持的格明确保留，不继承D4起点/四域拒绝 | K只依赖正确的value-node集合/term，不因规则TZ域划分丢对象          | D按消费者自己的词法标准与精确IRI验证；不能仅因宿主年份/微秒不足就把合法值说成ill-typed                      | R按其SPARQL日期关系/错误语义，**不自动采用D4 date起点或带/不带TZ一律E3**；自身规范/实现不支持处列C，不能伪报通过                     |
| 合法NaN/±INF（含+INF）或新规则舍入溢出                        | 新规则按E6拒绝；原图入口限制是否先拒逐路径保留记录                | 原query图门范围不扩大，不假设表达式中间值均受此门                      | 仍按原query合同；新规则E6不自动传到所有AST/中间值                                | 若实际入口允许则K；若先拒须记入口失败与未完成消费者格，不造成功图 | 合法特殊词法不因规则E6变成D词法违规；D不比较有限性。精确datatype仍要匹配                                    | R看其关系是否true，非true给违规；不自动用规则E6终止。入口先拒或真实能力不足需记C，不能声称此格已验证                                 |
| 非法lexical、未知datatype、shape边界或资源超限                | 新规则适用E1/E4/E5/E8，保留原入口/安全门                          | 原入口/操作按真实context分类，不伪装空匹配                             | 不把所有异常改false，不用规则错误码覆盖合法FILTER行为                            | 能进入验证的对象按K；不能为成功而丢未知/坏值                      | 若数据已被入口接纳，适用非法词法/IRI不符按D给违规；超出受支持datatype的处理需C，不能泛称“所有未知IRI必非法” | syntactically合法的Literal边界/数据导致关系error仍是R违规；非Literal边界违反shape参数语法是定义问题；资源/真正执行失败另走原权威边界 |

FR504五模板、asserted与asserted+derived双范围、实际focusNode/path/value/shape/component及修复后复验保持。每个C格必须回应“支持并由谁补齐”或“明确受限并保留原验收未完成”，附原入口、consumer规范profile、实际context→DTO/用户状态；违规报告与能力失败分开。这里不授权任意公共码/路径，也不因安全拒绝登记首版完成。

### R1/R2合同见证（手工期望，未执行；不表示当前shape入口全部允许）

| 情形                                                                                 | 规则／RDF层期望                                        | SHACL自身期望                                                                                                                                                                 |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| datatype要求xsd:integer，数据为`"1"^^xsd:int`                                        | D3可与integer 1值相等，term仍不同                      | D产生datatype违规，sh:value保留该int；不靠数值相等通过                                                                                                                        |
| datatype要求xsd:integer，数据为`"bad"^^xsd:integer`或IRI                             | RDF可表达ill-typed Literal；应用入口若先拒须如实记缺口 | 若进入validator，D分别因适用词法非法／非Literal违规；不是规则M4或Internal                                                                                                     |
| minInclusive为integer 2，数据integer 1／integer 2                                    | 新规则比较是否true另验                                 | R分别违规／该组件无违规；给真实值与组件，不造整体passed                                                                                                                       |
| minInclusive为integer 2，数据字符串two；或语法允许的ill-typed Literal边界使关系error | 新规则相应比较政策不决定此结果                         | R规范关系error产生违规；不发规则E3。当前numeric shape还要求not ill_typed，故坏Literal边界会先被其入口拒绝，此格属合同见证/未支持而非当前运行结果；非Literal边界是组件语法问题 |
| maxInclusive为integer 2，数据integer 3／integer 2                                    | 同上                                                   | R分别违规／该组件无违规，独立核shape参数侧与data侧                                                                                                                            |
| sh:in列表仅integer词法1，value为integer词法01或xsd:int词法1                          | 都与列表term不同，即使D3值相等                         | K的in违规；数量保留不同term，不按值eq折叠                                                                                                                                     |
| 同focus/path有integer词法01和1，maxCount 1                                           | 两个不同抽象term                                       | value-node集合大小2，数量违规                                                                                                                                                 |
| 同focus/path源写`"a"`和`"a"^^xsd:string`，maxCount 1／in列表含后者                   | RDF1.1同一抽象term，两个源写法不造两节点               | 集合大小1；in成员相同，不因省写datatype违规                                                                                                                                   |

持久化/trace区分抽象term和来源拼写：保存可恢复的lexical form/datatype/语言及原数值/日期词法；省略datatype、引号/转义/标签大小写的原文可作source信息，不以其字面串制造新term。policy/完整implementation/原规则输入身份仍须认证；严格三字段只是新消费身份门，**不证明不同消费者已具备各自正确语义**。旧历史不重签，给定firing认证不冒称全局完备。

## 5. 下一次技术接受与Q6决定

具体请求及可填写决定单见[技术接受请求与Q6决定单r1](q6-policy-decision-request-r1.md)。I05已技术接受S/L/I-B/X与K/D/R独立目标（见联合接受表），仍须补具体C格的可达范围/新身份/异常对表与完整golden；T01包装技术边界已答复（见§6），实际context接线与新公共诊断仍待。D3/D4已有I05技术答复保留，不重置成无人回答。Q6逐项采用或改写应用profile及固定REC/勘误集；**RDF1.1 simple/xsd:string的抽象term同一性不是可选合域**。

D8 input/work/result阈值仍待真实测量，新增helper/原consumer/公共诊断均先精确路径接受。四语义路径仍future，P2/P3/P5/P6仍I05代改，worker未来唯一T01；本轮不实施、不复测。R1/R2这里只关闭文档歧义，未获Q6/当前实现验证/指定双审Pass，原完整验收保持。

## 6. T01 TA-C/Q-LIFE回复：已接受包装边界，C格待I05落实

固定T01 `b35cb4e21d375386775e5fc0431a8089a47195da:docs/iterations/T01/t05-context-wrapper-response-r2.md`（SHA `3d300cf1070adf54f97fec45d060273f78d0e29fba9bbef502403466084b8d09`）已全文读回，原f51 D6/D7/M12–16/P8接受保留。T01明确接受graph、query term/表达式、SHACL K/D/R各自获批profile；正常SHACL false/type-error违规不转规则E3整Job失败，真正能力/执行失败不包装成空成功rows。T01负责真实Job/result、project/snapshot/revision、依赖/definition digests、完整implementation、current/stale/historical、payload可用性、historicalSelectionRequired、分页绑定/hash及当前可信授权先于存在性。三字段仅分区，不证明同义；不新增第二comparator。

**仍需I05逐C格给出**真实输入/definition source、实际入口/输出形状、三字段新producer身份、有限预算/实际异常类型与安全reason、完整成功validation及失败诊断分别的golden；不能由T01猜通用异常或替执行器决定Q6。上述包装技术接受不等于当前每格实现已接通，也不批准SHACL/query支持面、公共payload或错误路由。T01只在精确context上连接真实持久身份/hash，I06负责实际main/UI入口，原owner路径保持。

M12当前仍IDENTITY_CONFLICT，未来UNSUPPORTED适配及独立诊断资源未实现未批准；定位须真实source有限section/index/reason，绑定当前授权/请求/快照/实际定义或prepared plan，不泄露operand原值/路径/stack。TA-S/L/I-B/X和Q6决定、D8阈值及实际golden/联验仍待，D3/D4原技术答复不清零。本轮无新实现、重测或修复通过证据。

## 7. I05新技术回复与联合范围

固定96fb597 owner-response/inputs已全文读回，I05技术接受新增S/L/I-B/X及K/D/R独立目标，D3/D4保留；与T01 b35 r2合并的[联合接受、未实现与Q6范围表](accepted-policy-and-q6-scope-r1.md)为最新答复状态。完整C格运行/可实施合同尚未闭合，不把日期shape或rdf:langString shape写成旧候选已支持。初始facts/ontology _terms为REASON/SYNTAX/VERIFIED_USER_INPUT，即使业务为query/validation；已核三个literal错误的精确映射与新增拒绝点待补表见联合表§3，普通SHACL违规不进adapter。source原文载体/授权/大小生命周期/公共投影尚需实际owner/T01给出，不假称S1保留全部原写法或私加DTO/重签历史。C4仍未冻结/指定双审通过，Q6未采用，四路径未生效，未实施或复测。
