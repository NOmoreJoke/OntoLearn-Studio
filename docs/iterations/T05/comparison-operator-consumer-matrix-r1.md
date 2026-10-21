# T05 比较算子、跨域及消费者矩阵 r1

**供下一次具体审定，不是实现或验收结果。** I05对D2–D5的技术答复与T05补充提案分别标记；全部值政策仍需Q6采用、规范pin及真实完整矩阵。当前规则没有值比较/多head；未批准C3不能作为T05依赖。

来源：固定I05 `ffc462b2332dfb8af7c15c91adb3ac1f7ac1b24d` 的owner-response（SHA `723368ccc8902c70dcd28939f7b4a21f7dc6d8488d39c7b981b1952caf33fc4e`），状态/路径接受见[当前决策表](owner-decisions-after-interface-facts.md)。本文不改变query/FILTER/cast，不新增公共协议或错误枚举。

## 1. 单元格含义与政策前置

- `V`：在合法、有限、预算内operand上，此操作有明确定义，返回真实true或false；**不表示结果必为true或已有运行通过**。
- `E3`：规则类型/操作不兼容，整任务失败。拟用I05已技术接受但尚未实现的新reason `RULE_COMPARISON_TYPE_MISMATCH`，在REASON/RULE/VERIFIED_USER_INPUT上下文映射现有`SEMANTIC_INPUT_INVALID {field:rule}`。
- `E1/E4/E5/E6/E8`：分别为坏定义/operand结构（M1）／非法词法（M4）／合法但未支持类型（M5）／合法非有限或舍入溢出（M6）／实际资源超限（M8），按当前M表区分处理。先完成适用的定义、类型、词法与预算校验，再对合法值判断V/E3，不能拿不合法值进入关系比较后再补false；本记号不新增adapter reason或公共错误。
- 固定技术方向：三元组join、head、graph去重仍按原term身份；值eq不能重写01/1、±0或其他原term。先验证全部定义常量与变量闭合；坏定义不因零匹配而隐藏。合法join无解成功空集合。每个完成when的binding按稳定位置校验**全部**comparisons，不因前一个false隐藏后一个错误；全真才产生全组heads。

状态标记：`I`＝I05技术接受/推荐，未Q6采用、未实施；`T`＝本轮T05补充具体提案，待I05/Q6接受。域的划分本身也是政策，不由Python类型或当前库排序推断。

## 2. 同域六算子逐格表

| 域／适用值                                                                  | 状态 | eq  | ne  | lt  | le  | gt  | ge  | 比较定义／明确拒绝点                                                                                                                                                                                                                                       |
| --------------------------------------------------------------------------- | ---- | --- | --- | --- | --- | --- | --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| N：integer、int、nonNegativeInteger、decimal、float、double；任意这六型组合 | I    | V   | V   | V   | V   | V   | V   | 严格原词法解析。整数精确、decimal精确十进有理；float/double由精确词法有理值直接按binary32/64 normal/subnormal nearest/ties-even舍入，再取实际有限表示值的精确有理数比较。禁止先binary64再binary32、禁止将整数/decimal有损提升为float。int/非负值域检查保留 |
| S：plain literal与xsd:string                                                | T    | V   | V   | V   | V   | V   | V   | 建议同一字符串值域：比较合法RDF转义解码后的Unicode标量序列，按码点字典序；不trim、大小写折叠、NFC、locale或转数值。比较文本值，不比较N3引号外壳；原term身份另保留                                                                                          |
| L[t]：rdf:langString，双方同一语言标签域t                                   | T    | V   | V   | V   | V   | V   | V   | 建议标签仅以大小写不敏感匹配划分域，不折叠en/en-US等不同标签；同域文本按S的码点规则。它不是自然语言排序。不同标签归不同域，见跨域表；此分域/排序仍待接受                                                                                                   |
| I：IRI与IRI                                                                 | T    | V   | V   | E3  | E3  | E3  | E3  | 建议eq/ne为完整IRI身份；不解引用、URL解码、大小写折叠或拼写规范化。不给IRI业务大小顺序；即使两IRI相同也不将le/ge当true                                                                                                                                     |
| B：boolean与boolean                                                         | T    | V   | V   | E3  | E3  | E3  | E3  | 建议合法true/1对应true、false/0对应false的值相等；原词法/term不合并。不给布尔大小顺序，不利用Python bool继承数字                                                                                                                                           |
| Dz：date，双方有显式offset                                                  | I    | V   | V   | V   | V   | V   | V   | 独立Gregorian日序＋精确秒；取原本地日期00:00:00起点减各自offset后比较，不采用隐含时区或声称完整date区间部分序                                                                                                                                              |
| Dl：date，双方无offset                                                      | I    | V   | V   | V   | V   | V   | V   | 同一本地日历域起点比较，不补Z或读取机器时区                                                                                                                                                                                                                |
| Tz：dateTime，双方有显式offset                                              | I    | V   | V   | V   | V   | V   | V   | 独立日序＋完整小数秒的精确有理秒，减各自offset比较；不受Python datetime微秒/年份表示截断                                                                                                                                                                   |
| Tl：dateTime，双方无offset                                                  | I    | V   | V   | V   | V   | V   | V   | 同一本地日历域比较，保留完整秒精度，不推测时区                                                                                                                                                                                                             |

D3补充：±0值相等但保留符号/term；合法subnormal和舍入下溢到有符号零按声明舍入，不一律拒绝。合法NaN/±INF、有限词法舍入为无穷为E6；非法拼写E4。巨大词法/指数在构造幂或大整数之前检查位长和工作预算，不能把预算错误改成词法错误。

D4补充：I05推荐pin XSD1.1词法/日历，涵盖年零/负年、闰日、合法24:00进位和offset边界；**确切规范版本/章节及fixture仍待Q6审定，本表未完成规范pin**。独立calendar-value是明示应用政策，不能仅因宿主parser可cast就宣称支持。date起点与dateTime时刻分域；无隐式互cast。

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

`*` L[t]×L[t]只用于相同标签域；L[t]×L[u]（t≠u）明确为X6。将plain/xsd:string合并为S、按标签划分L、IRI/boolean只提供eq/ne均是**T05待审提案**。I05已接受的是“矩阵明示允许数值混型；其他未定义跨域/操作统一失败”，并未提前接受本轮新定义的S/L/I/B单元格。

### 下一次审定的同域／跨域见证（手工政策期望，未运行）

| 左／右示意                                                     | eq    | ne    | lt    | le   | gt    | ge    |
| -------------------------------------------------------------- | ----- | ----- | ----- | ---- | ----- | ----- |
| S：文本10／文本2                                               | false | true  | true  | true | false | false |
| S：plain文本a／xsd:string文本a（若S合域获准）                  | true  | false | false | true | false | true  |
| L[en]：a／b                                                    | false | true  | true  | true | false | false |
| L[en]：a／L[EN]：a（若标签分域政策获准）                       | true  | false | false | true | false | true  |
| L[en]：a／L[fr]：a                                             | E3    | E3    | E3    | E3   | E3    | E3    |
| I：urn:x／urn:x                                                | true  | false | E3    | E3   | E3    | E3    |
| I：urn:X／urn:x                                                | false | true  | E3    | E3   | E3    | E3    |
| B：true／boolean词法1                                          | true  | false | E3    | E3   | E3    | E3    |
| B：false／true                                                 | false | true  | E3    | E3   | E3    | E3    |
| boolean true／integer 1；IRI urn:x／字符串urn:x                | E3    | E3    | E3    | E3   | E3    | E3    |
| date无TZ／date带TZ；dateTime无TZ／dateTime带TZ；date／dateTime | E3    | E3    | E3    | E3   | E3    | E3    |

这些见证补充原22例，不替代D3数值精度边界、D4完整日历/时区/精度、所有类型及失败路径的真实完整矩阵。定义常量无匹配仍先校验；先false后坏operand、两个heads中一head失败也必须纳入验收。

## 4. 图入口、query及SHACL消费者逐格提案

`G`＝现有图的RDF结构/位置、词法、外联和schema门继续保留；现有ill_typed/宿主值转换是否足以表达新值需逐项核对。`N`＝在获批的新reason/扩展selected路径中，用同一词法值validator/comparator落实D3/D4，不全局关闭ill_typed/normalize，不改原term。`C`＝具体消费者需要新增、版本化的能力/值保真预检与真实证据；无法保真时建议明确拒绝，不交给库静默截断、排序或报告通过。C的拒绝码/producer/stage/origin仍需I05/T01按真实消费者路径审定，**不套用规则R/R/U或擅改FILTER的False丢行行为**。

下表“建议允许”均以新政策获准、同一implementation、真实consumer gate及运行证据为前提；不是本轮通过结论。建议拒绝也不是获准缩减FR505/SHACL范围；如产品要求支持，应补对应消费者而不是用拒绝关闭原验收。

| 值／情形                                           | 图入口→新reason／新selected                                                                      | query图入口与term匹配/投影                              | query值运算/FILTER                                                                                   | SHACL required/maxCount/allowedValues等term/数量用途           | SHACL datatype／numericRange等类型/值用途                                                          |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| S/L/I/B普通合法原term                              | G＋N；I位置约束、字符串/标签/布尔词法保留                                                        | 建议在原有限query面按term处理，不由新规则值eq重写join   | 保留原query声明语义和错误传播，不宣称与新规则同义；矩阵新S/L/I/B比较不自动扩大query                  | 建议保留原有限模板的term/数量语义；不能因值相等合并01/1等term  | 原模板适用性及真实报告另验；IRI不是Literal，不能把datatype违规误报内部异常；不据图白名单宣称全支持 |
| 合法integer/int/非负/decimal，预算内               | G＋N：精确整数/有理数与值域检查；不得默认Decimal运算context舍入                                  | 建议保持原term投影；所有原词法和datatype可恢复          | 继续既有query政策；涉及混型/算术的结果不拿来冒充D3精确规则政策，若请求同义则C并另审P4                | 建议原term/数量处理；图去重与数值eq分离                        | C：要证明实际模板比较与采用的值政策一致；若不一致须支持新validator或明确拒绝，不能静默错判         |
| float/double：声明舍入值与旧Pythonfloat解释一致    | G＋N：仍按声明精度解释并记录原term                                                               | 建议原term处理，禁止将量化后词法重写为新断言            | 仍属旧query规范；“本行值一致”不证明所有表达式/跨型操作一致                                           | 建议原term/数量处理                                            | C：模板值比较逐格验证，不能只验图可载入                                                            |
| float32边界／跨型值：D3解释与旧库不同              | G不充分；必须N直接舍入，不能binary64二次舍入                                                     | 建议仅在term路径真实可保真且C可证明时允许；不改term     | 建议C在进入不保真的值用途前明确拒绝，或另经批准升级消费者；不能默用旧float64当D3                     | term用途也需C确认没有重解析/规范化损失，再建议允许             | 建议C拒绝不保真的旧值用途直至消费者获准支持；不能让旧库报告代替D3验证                              |
| date显式offset／dateTime任意秒精度，旧库表示范围内 | G保留原词法不等于值保真；N保留offset/完整秒并按域比较                                            | term用途需C确认roundtrip；可保真才建议允许              | date丢offset、aware/naive分区或精度损失的用途须C拒绝/批准升级，不能默补时区；其余query行为不自动改写 | term/数量用途需C确认原term保真                                 | C逐类型/范围核对；不保真则明确拒绝或升级，不能用宿主date/datetime直接代替D4                        |
| 年零/负年/大年份、>6位小数秒、合法24:00等D4新边界  | 原graph gate可能先拒；须获批reason/selected路径针对这些值用N，而非仅在末端补comparator或全局关门 | 建议C逐值证明纯term往返才允许；证明不足则明确拒绝       | 建议在消费者实际支持前拒绝这些值用途；支持需额外owner/矩阵，不以Python可cast作证                     | C确认保真才允许对应term/数量用途；否则明确拒绝，不能悄悄丢对象 | 建议在真实支持前明确拒绝；若SHACL双范围产品要求覆盖，须补消费者后再验收，不关闭原要求              |
| 合法NaN/±INF、有限词法声明舍入为无穷               | 新规则E6，失败且无partial current；原graph拒绝门保留                                             | 原query图门的拒绝边界不因本表扩大                       | query-only常量/表达式仍按原query能力；**不由graph NaN拒绝推导全部AST/中间值已拒绝**                  | 不能以伪造成功图传入；实际原入口限制保持                       | 不声称新规则E6等于现有全部SHACL非有限策略，真实消费者路径须明确                                    |
| 非法词法、未知datatype、预算超限                   | 分别E4/E5/E8；保持原RDF/外联/schema门                                                            | 各入口以真实类型/producer/stage分类，不伪装为合法空结果 | 不把所有异常改为FILTER false，也不更改原合法FILTER行为；新增范围需单独接受                           | 不伪装成成功验证空报告；保留实际报告/受限失败区别              | 类型/值不支持与真实约束违规分开，不能写“已通过”                                                    |

持久化/trace贯穿所有格：保留原N3 term、datatype/语言/offset/精度及生产规则/输入身份；绑定新政策与完整implementation，不保存原值的有损替代或靠consumer当前规则重签历史。T01严格三字段相等是必要门，**不证明同一引擎内旧query/SHACL已支持新规则值域**，仍需本节C门。C门只是一项待接受设计；具体拒绝路由/用户可见状态、可证明term-only用途的识别及预算都尚未实现。

## 5. 下一次审定须明确的格与证据

1. I05/Q6逐格接受或改写S/L/I/B六operator、S合域/语言标签分域及全部跨域X6；不要只回“沿RDFLib”。D2对已判不兼容的eq/ne失败要求保持。
2. Q6固定D3/D4规范版本/章节和词法/日历fixture；I05给精确舍入、subnormal/±0/溢出与日历/秒精度/offset原子失败的完整实际证据。各值进入graph、reason、selected和持久载荷的同义性分别验，不只有末端比较。
3. I05/T01接受每个consumer格的允许/拒绝或升级计划及真实context→DTO，保持query独立政策；不能通过宽泛禁止新值来宣布完整FR505/SHACL完成。
4. D8沿owner已给计费点测量input/work/result具体阈值、边界±1和源/包运行；现有caps不是新增容量证明。四路径仍future，P2/P3/P5/P6仍I05代改；新helper拆文件、query/SHACL支持面或公共诊断均需精确另行接受后实施。
