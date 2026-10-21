# T05 已采用规则应用 profile v1：机制实施规范

**政策已采用；代码尚未实施。** 用户2026-10-21明确回复“采用决定单的推荐规则与规范版本”。采用对象原件4698B/SHA `328a59c42ae69a5c2426c494c1c979cb629692f389cdacf591e8789738c6b4f0`，状态更新单5038B/SHA `4e82174a9d5c312dce23a02320ef9e23f9a9fc62bb22bf69bdedd6a25ed10b29`；正式回执`iteration-control/2026-10-21-weekly-release/Q6-user-adoption-receipt.json`。原字节保全位置及采用语句/hash见本线`docs/reviews/T05/q6-adoption-stage-receipt.json`。此前“Q6未采用”是当时状态；当前由本规范覆盖，不回写历史归档。

内部profile标识固定建议`OntoLearn-rule-comparison-profile/1`；只是本阶段私有机制标识，最终公共implementation/执行语义版本仍由真实owner与总控冻结。Q6不授权消费I05候选、写四semantic future路径、改Store或启动平台验证。实施范围/预算防护上限见[阶段授实施规格](q6-profile-mechanism-stage-plan.md)，需总控一次明确授阶段后施工，不再申请Q6政策。

## 1. 固定规范与实现选择

采用有日期REC正文/既定章节，不自动集成勘误、不跟随latest：RDF1.1 Concepts 2014-02-25 §3.2/3.3/5.1；SHACL 2017-07-20 §§4.1.2、4.2.1/2、4.3.2/4、4.8.3；SPARQL1.1 Query 2013-03-21 §§17.2–3；XSD1.1 Part2 2012-04-05 §§3.3.1–5、3.3.7/9、3.4.13/17/20、D.1/D.2、E.3/E.4。规范pin已采用；实现、公共身份和规范符合性证据没有因此完成。

XSD允许的实现选择在此固定：S采用其所引用[XML1.1 2006-08-16 Char生产式](https://www.w3.org/TR/2006/REC-xml11-20060816/#charsets)，即U+0001–D7FF、E000–FFFD、10000–10FFFF；不额外套XML文档RestrictedChar/行尾归一。L按RDF语言字符串的Unicode lexical处理，不无依据加XML Char限制。标签仅做[RFC5646 2009-09 ABNF well-formed](https://www.rfc-editor.org/rfc/rfc5646.html#section-2.1)，不做IANA registry-valid、preferred-value替换或valid层额外重复筛选。这些是固定规范允许的机制选择，不另改变已采用政策。

## 2. 输入与term/source契约

纯机制接收已解码的私有结构化`TermInput`，不解析Turtle/N3/XML，不访问URL/文件/Store。IRI输入为实际RDF入口已验证的绝对IRI；机制只比较完整字符串身份，不新增另一套RDF/IRI parser。阶段仅用标准库做与批准5f约定一致的scheme/禁用字符最小结构检查（不import其RDF模块），**不把该门宣称为完整RFC3987符合性**；完整RDF语法/位置/IRI合法性及原始转义解码仍归后续真实I05入口，须联验。错误IRI不能通过标记自报获得授权。

| 私有字段                    | 精确含义／边界                                                                                                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| kind                        | 仅iri或literal；变量另用Variable，不把`?x`字符串当literal；blank node不属于本规则operand/head语言                                                                                                                   |
| lexical_form                | Unicode字符串；surrogate/非str为结构非法。保留原RDF lexical form，不做strip/collapse、NFC、大小写/数值规范化。它不是N3引号/转义外壳                                                                                 |
| datatype_iri / language_raw | 无lang且省略datatype按xsd:string抽象term；有lang时datatype须省略或rdf:langString，反向rdf:langString须有标签。结构矛盾为INVALID_RULE；未知但合法datatype为UNSUPPORTED_LITERAL_DATATYPE                              |
| term_key                    | IRI为完整IRI；literal为原lexical form＋抽象datatype IRI＋内部小写语言标签。simple与同lexical显式string同key；integer01/1、true/1、日期offset等不同原lexical仍不同key，不能按值eq去重                                |
| source                      | 私有可空SourceRecord：原source引用/原字节digest/真实原定义revision或prepared-plan摘要，真实section/index/可选左右operand与原字节span；若真实原写法可得，保留原token/source字节。不由term逆推原文，不造索引/摘要认证 |

纯层只保留caller实际提供且有界的数据，不认证source/actor。S1 canonical事实不证明每个导入前写法已有；缺失source应显式unavailable，不填假原文。真实source owner/T01仍须给当前授权、有界大小/保留生命周期/公共投影/诊断载体；本阶段不加DTO、数据库、字段注册或重签历史。fixture的source是真实本例输入文本/索引，不冒充生产来源。

## 3. 每类型的精确词法与值

下列regex是对**原lexical完整匹配**的ASCII语法简写，D=`[0-9]`；不使用Python `\d`。不做XSD pre-lexical whiteSpace collapse；因此带外层空格/tab的数字、boolean、日期不在此原lexical映射，按词法错；S保留空白。依据[XSD2012 §2.3/4.1.4](https://www.w3.org/TR/2012/REC-xmlschema11-2-20120405/)，XML schema-validity的pre-lexical处理不等于此RDF原词法清洗。

| 类型               | 合法原lexical／值域及处理                                                                                                                                                                                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IRI                | 已经真实RDF入口验证的绝对IRI；机制不URL解码、不折叠scheme/host、不解引用，无自动相对解析。不同拼写按完整身份不同                                                                                                                                                                              |
| S xsd:string       | 满足选定XML1.1 Char*，空串允许；NUL、BMP U+FFFE/U+FFFF为INVALID_LITERAL_LEXICAL；RDF可表达的lexical不等于一定是合法S值。按Unicode码点序比较，不按UTF16 code unit；U+10000大于U+E000                                                                                                           |
| L rdf:langString   | lexical为Unicode scalar序列，空文本可；语言标签非空ASCII完整ABNF。支持langtag（language/extlang/script/region/variant/extension/privateuse）、privateuse和RFC固定grandfathered全集；internal仅ASCII lower，不做登记有效性/别名/回退。仅ABNF不排除的重复variant/singleton不能偷偷按valid层拒绝 |
| boolean            | 仅`true`、`false`、`1`、`0`；分别映true/false；`True/+1/01`非法。B不入N；保留原term                                                                                                                                                                                                           |
| integer            | `[+-]?D+`，精确带符号整数；前导零/+号/-0合法并保留term，value的-0为0；不接小数/指数/下划线/非ASCII数字                                                                                                                                                                                        |
| int                | integer同语法，值须在-2147483648…2147483647，越界为词法/值域错误，不是资源或隐式大integer                                                                                                                                                                                                     |
| nonNegativeInteger | integer同语法，值≥0，故`-0`合法；负值非法                                                                                                                                                                                                                                                     |
| decimal            | `DECIMAL_FINITE`，无指数；`1/1./.1/+01.00`等各自合法写法映精确十进有理；单独`.`非法。斜线仅分隔例子，非分数语法。无float/Decimal context中转                                                                                                                                                  |
| float/double       | 有限语法`FLOAT_FINITE`；另合法`INF/+INF/-INF/NaN`。`+NaN/-NaN/inf/nan`非法。合法非有限或有限词法目标舍入为∞→UNSUPPORTED_NONFINITE_LITERAL；合法subnormal/下溢有符号零保留。由原精确十进有理直接量化，见§4                                                                                     |
| date               | `Y-MM-DD TZ?`（无空格）；Y为`YEAR`，不接年+号，>4位不接前导0；month01–12，day按该年Gregorian合法月日。`0000/-0000`均year0（1 BCE），`-0001`为2 BCE；原词法不同仍不同term                                                                                                                      |
| dateTime           | `Y-MM-DDTHH:MM:SS(.D+)? TZ?`（无空格），日期同上。HH00–23、MM/SS00–59；另仅24:00:00且fraction全0合法，进次日；不接闰秒60、空fraction、lowercase t/z、缺秒、非零24点                                                                                                                           |

表中三个含分支的语法用独立代码块固定，避免Markdown表格将分支分隔符误作列：

```text
D = [0-9]
DECIMAL_FINITE = [+-]?(D+(\.D*)?|\.D+)
FLOAT_FINITE = [+-]?(D+(\.D*)?|\.D+)([eE][+-]?D+)?
YEAR = -?([1-9]D{3,}|0D{3})
```

TZ为大写Z或`[+-]HH:MM`：00:00…13:59或14:00，最大±14:00；±14:01/分钟60非法。Z/+00:00/-00:00都显式offset0，来源拼写保留；无TZ是absent，不能当offset0。年份、fraction、指数长度受阶段预算，超限为RESOURCE_LIMIT而非“标准非法”。未知datatype与上述已识别类型的非法lexical分开。

## 4. 精确数值与直接binary舍入算法

1. 先完整词法检查/预算，再分段（每段≤9位）构造整数，不调进程全局int位数限制；decimal系数/小数位形成有理p/q，归约由有界整数GCD，禁float/默认Decimal运算context。
2. float/double：保留sign，取非负精确系数及10进指数；全零系数直接目标有符号零。指数先扫描/有界比较，不先构造巨大10幂。令有效非零系数去前导零后有m位、原小数位f、指数E，科学计数阶D=m-1+E-f；E用符号/去前导零文本与小阈值有界比较，只有确需且有界时才转int。按D进行**有数学安全余量的远界判定**：binary32 D≥50必溢出，D≤-61必舍入零；binary64 D≥400必溢出，D≤-401必零。这只省去无意义分配，近边界仍走精确算法；不能在常用308/38附近粗判。
3. 需精确量化的范围内以原有理p/q求`e=floor(log2(p/q))`，用bit_length差与整数比较修正，禁止宿主log/float。binary32参数(pbits,emin,emax)=(24,-126,127)，binary64=(53,-1022,1023)。
4. 统一量子`step=2^k`，`k=max(e,emin)-(pbits-1)`。对`(p/q)/2^k`用整数divmod得商n/余r/除数d；2r<d下取，>d上取，=d取偶n。移位/乘法/除法前计预算。舍入进位跨binade后重新确认有限性；结果≥2^(emax+1)为∞受限失败，不能夹到max finite。
5. 输出恰好可表示的有限值n×2^k，再转精确有理以供六算子；subnormal→normal、最小subnormal半值→有符号零、max finite溢出中点各有独立oracle。±0比较相等，negative_zero另存，不改变原term。不同数值类型比较各实际值，无整数/decimal有损提升。

比较有理数先符号/零，再对受限位长交叉乘积精确比较；所有乘/除/GCD/shift/十进转换计费且先查限。远界合法下溢不因“指数大”一律拒绝；原词法本身超长度/扫描预算仍可先资源失败。双重舍入反例`1+2^-24+2^-80`（fixture用精确十进展开）直接binary32为`0x3f800001`，经binary64会错到`0x3f800000`，必须杀死该替换。

## 5. 独立Gregorian key

按XSD1.1天文年号直接解析（允许-0000），leap=`y mod4=0 and (y mod100!=0 or y mod400=0)`，数学floor/mod用于负年。验证月日后用下式有界整数日序，epoch=0000-03-01：`ya=y-(m<=2)`；`era=floor(ya/400)`；`yoe=ya-era*400`；`mp=m+(-3 if m>2 else9)`；`doy=floor((153mp+2)/5)+d-1`；`serial=era*146097+yoe*365+floor(yoe/4)-floor(yoe/100)+doy`。不得用datetime、系统TZ、DST、微秒截断。

date取日00:00:00；dateTime取完整有理秒（先处理合法24点进日）。显式offset时减offset分钟×60，规范化为`(serial_day, second_num/second_den)`且日内秒∈[0,86400)；无TZ保持local。**day与秒分数分离**，先比day再比同day精确秒，不把巨大year乘fraction分母。date与dateTime、显式与absent在比较前分域，绝不隐式cast或按XSD部分序跨域比较；这是用户已采用的更严格应用政策。date起点key不是将date本体改为dateTime/完整区间运算。

## 6. 完整六算子×域

`A6=V/V/V/V/V/V`、`Q2=V/V/E3/E3/E3/E3`、`X6=E3/E3/E3/E3/E3/E3`，顺序eq/ne/lt/le/gt/ge；V为合法值返回实际Boolean，非必true。E3整任务类型/操作不兼容，ne也不能自动true。N=六numeric，S=无lang string，L[t]=同合法小写标签，I=IRI，B=boolean，Dz/Dl=date显式/absent，Tz/Tl=dateTime显式/absent。

| 左\右 | N   | S   | L[t] | I   | B   | Dz  | Dl  | Tz  | Tl  |
| ----- | --- | --- | ---- | --- | --- | --- | --- | --- | --- |
| N     | A6  | X6  | X6   | X6  | X6  | X6  | X6  | X6  | X6  |
| S     | X6  | A6  | X6   | X6  | X6  | X6  | X6  | X6  | X6  |
| L[t]  | X6  | X6  | A6*  | X6  | X6  | X6  | X6  | X6  | X6  |
| I     | X6  | X6  | X6   | Q2  | X6  | X6  | X6  | X6  | X6  |
| B     | X6  | X6  | X6   | X6  | Q2  | X6  | X6  | X6  | X6  |
| Dz    | X6  | X6  | X6   | X6  | X6  | A6  | X6  | X6  | X6  |
| Dl    | X6  | X6  | X6   | X6  | X6  | X6  | A6  | X6  | X6  |
| Tz    | X6  | X6  | X6   | X6  | X6  | X6  | X6  | A6  | X6  |
| Tl    | X6  | X6  | X6   | X6  | X6  | X6  | X6  | X6  | A6  |

*L[t]×L[u]当t≠u为X6，无回退。N的每个有序datatype对都A6：

| 左\右              | integer | int | nonNegativeInteger | decimal | float | double |
| ------------------ | ------- | --- | ------------------ | ------- | ----- | ------ |
| integer            | A6      | A6  | A6                 | A6      | A6    | A6     |
| int                | A6      | A6  | A6                 | A6      | A6    | A6     |
| nonNegativeInteger | A6      | A6  | A6                 | A6      | A6    | A6     |
| decimal            | A6      | A6  | A6                 | A6      | A6    | A6     |
| float              | A6      | A6  | A6                 | A6      | A6    | A6     |
| double             | A6      | A6  | A6                 | A6      | A6    | A6     |

先词法/支持域/资源校验再判V/E3，不让未知datatype、NaN或坏日期混进false。486分类槽/216数值细化不是通过数；标签是参数族，不声称有限样例穷尽无限值域。

## 7. 与其他消费者的边界

只实现这份新规则profile。query继续自身有限SPARQL合同，SHACL K数量/in、D精确datatype/适用词法、R自身SPARQL关系非true含type-error产生正常违规；不共用本profile改写它们。当前I05报告numeric shape参数仅integer/int/decimal/float/double且not ill_typed，日期shape边界与sh:datatype rdf:langString未支持，仍须原owner补齐/列未证，不因Q6采用就变成已支持或缩减FR504五模板/双scope。普通SHACL违规不进入adapter。本阶段无Turtle/Graph匹配/RDFS/SHACL/Store/Job/IPC/worker/main/UI入口，不能以局部机制通过关闭原FR。
