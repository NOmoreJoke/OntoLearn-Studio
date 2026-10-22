# SHACL date：有限 UTC 范围政策设计

2026-10-22。**用户已采用有限 UTC date 扩展；本文件完成设计更新，尚未实施或取得真实运行证据。** 不再等待用户在core/扩展之间选择，不重问已采用Q6。依据为总控 `SHACL-date-and-SQLite-user-decisions-20261022.md` 的实际用户决定。

施工设计基线为 `7f99e9c62bed85b6fa38a8efb6be44ce3f1fba81`，其中已收件整数组件产品为91e9807。该基线的实际 `validate_shacl_text` 仍只接受range legacy；本设计不追认其已支持date。旧设计、原C输入/goldens、历史pending和首失败证据保持原字节。SQLite损坏输入保护及HOLD、先前被拒资源分析停止、未授object envelope均保持，不产生新Goal或实施授权。

## 1. 显式政策身份与复用入口

继续使用唯一独立组件API：

```python
validate_shacl_text(data_text, shapes_text, *, data_policy, range_policy)
```

两个策略关键词始终必填，exact str验证，不设置扩展默认值。拟支持的组合如下；这是未来writer目标，不是当前执行结果。

| 选择                                                                       | entryVersion                     | 行为                                                 |
| -------------------------------------------------------------------------- | -------------------------------- | ---------------------------------------------------- |
| range_policy=`legacy`，data_policy为`strict`或`integer-illtyped-report-v1` | 保持`i05-shacl-text-1`           | 原整数入口和date bound拒绝行为全部保持               |
| range_policy=`utc-date-range-v1`，相同两种data_policy                      | 新独立入口版本`i05-shacl-text-2` | 应用本文件的有限UTC date范围政策，保留原数据策略区别 |

返回仍为四键：`entryVersion`、`dataPolicy`、`rangePolicy`、真实`report`。`utc-date-range-v1`本身是独立版本的范围政策标识；range v1固定包括本文件的操作数域、检查顺序和preflight额度，后续改变这些合同必须换版。旧全局`SEMANTICS_VERSION`、规则profile/Q6/规范pin及现有legacy常量不修改。

不同policy/version的结果不得混用。当前没有正式缓存或execution接线；未来接线须另授，并将完整三元政策身份及实际输入/约束/实现身份纳入相应绑定，不能仅凭全局版本或“conforms=true”复用。

## 2. 精确支持域与约束范围

扩展的每个date操作数必须是精确datatype IRI `http://www.w3.org/2001/XMLSchema#date` 的Literal，原lexical为11个ASCII字符`YYYY-MM-DDZ`：四位年份0001–9999、两位月日、大写Z。用原lexical做full-match和公历合法性检查；闰年为能被4整除且不能被100整除，或能被400整除。拒绝无时区、任何offset（包括`+00:00`）、小写z、空白/可变宽度、0000/负年/扩展年、非法月日和其他词法。不得先截时区、转Z、补零、改datatype、转dateTime、改写Literal或删除值。

当前组件的`_SH_PREDICATES`只开放`sh:minInclusive`、`sh:maxInclusive`两种范围约束，本版只扩它们的date操作数域：

- minInclusive：date value等于或晚于date bound通过，早于bound产生真实MinInclusive违规。
- maxInclusive：date value等于或早于date bound通过，晚于bound产生真实MaxInclusive违规。
- 同一property shape同时有两个date bound时均须检查。min晚于max仍是两个合法且可能不可同时满足的约束，不交换/修正bound、不预造shape错误；实际目标值由Validator分别给出结果，无目标或无值时仍按真实约束结果处理。
- 当前exclusive输入仍是`UNSUPPORTED_SHACL`、Validator0，本版不扩白名单。用户要求保留的exclusive严格语义适用于已有其他能力或将来另授支持：相等不满足exclusive；不能把inclusive相等通过传播到exclusive。此条不是本组件已经支持exclusive的声明。

本政策只扩**date参与的范围比较**。任一对bound/value含date，另一方也必须是上述同域date；date与dateTime、数值、普通/语言字符串、IRI等不兼容混合明确拒绝，不由库的跨datatype排序碰运气。数据策略允许坏integer进入Datatype验证，不代表它可以与date比较。

不含date的既有数值族兼容比较/dateTime等路径仍按现有SHACL合同处理；不借此改写原`C-inclusive-type-error`等非date规范结果。`sh:datatype`、计数、允许值模板本身不被重新定义。范围域检查只用于实际参与date比较的数据值，不对合法但不相关的date属性另加全图时区禁令；它们仍受原全图terms门约束。

## 3. 检查阶段、target/value选择和固定错误

以下顺序用于新UTC分支。legacy分支保持当前调用次序和错误；新分支不能捕获严格解析失败后继续执行。

| 阶段                    | 固定行为与拒绝                                                                                                                                                                                                                                                                            | Validator |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 策略参数                | 缺任一必填keyword为Python TypeError；未知/错误类型策略为既有`SCOPE_SELECTION_TYPE_INVALID`，先于文本解析                                                                                                                                                                                  | 0         |
| 原文本解析              | 复用有界文本、offline、lossless parse_graph及新整数入口已有IRI前检。类型/Unicode/格式/外联/blank-node/未知datatype/nonfinite/资源门保留。原terms识别的illtyped date仍先`INVALID_LITERAL_LEXICAL`，不为date扩展跳过它                                                                      | 0         |
| 形状结构与bound         | 复用原named NodeShape→named PropertyShape→直接IRI path及原结构/参数门。仅UTC分支允许date inclusive参数；所有date bound不论有无target都检查本政策原lexical和公历域，出域为`INVALID_SHAPE`。同一property shape有date与非date的inclusive bounds也拒绝`INVALID_SHAPE`，不让无目标绕过参数校验 | 0         |
| 事实scope               | 保持原`FACT_SCOPE_CONTAINS_AXIOMS`门；data不能混入subClassOf/domain/range公理。仍无ontology/inference加载                                                                                                                                                                                 | 0         |
| date实际操作数preflight | 从已校验NodeShape的targetClass和property link逐一取实际focus，再沿该property shape的直接path遍历**全部**value。涉及date的每对bound/value均核同域；不兼容或原terms未判illtyped但不符合有限域的value，固定`RDF_TERM_INVALID`。多值中任一拒绝则整个调用拒绝，不删值、不返回部分报告          | 0         |
| 真验证/报告             | 全部门通过才执行一次原`Validator(...).run()`，保持原options。返回真实conforms与完整六字段；报告类型错误仍为`VALIDATION_FAILED`，不补造普通violation                                                                                                                                       | 1         |

每个date bound/value的有限域门通过后，立即核其库值是精确date而非datetime，且年月日与原lexical一致；固定库不能解释已采合法域时固定`VALIDATION_FAILED`、Validator0并保留反例，不缩域、改golden或输出普通violation。bound的该检查先于事实scope门，value的该检查在其实际比较阶段。

原解析阶段的`INVALID_LITERAL_LEXICAL`优先于后续date域门。例如库已判定坏公历日或越年域为illtyped时，观察为parse-data/parse-shapes拒绝；若库宽松接受含T等非法date spelling，新有限域门仍须拒绝。不能把这些不同前门阶段都标成Validator的普通范围违规。上述错误均是现有内部固定码，本设计不新增公有错误目录/参数；正式错误映射接线另授。

target选择必须与真实Validator一致。在当前允许域内只有targetClass/直接path；data的继承公理已被scope门拒绝，因此preflight可按实际`rdf:type targetClass`选择focus。property shape被多个NodeShape复用时取其实际关联target，不能把同path的所有主体都视为target。未来放开继承、其他target/path须重新设计，不能沿用这个等价前提。

形状参数始终校验；数据比较域只在实际target/value对上校验。无target或没有该path值时，不能凭空造date violation；有minCount时缺值仍由真实Validator产生计数报告。合法但不相干的非Z date不会仅因本政策失败；原terms本来拒绝的非法字面量仍按data_policy原门处理。

## 4. 真实库路径、原词法和报告

固定来源为当前lock的pySHACL0.30.1/RDFLib7.6.0。静态源码可见range组件经`compare_literal`调用Literal值比较；RDFLib的date parser会剥时区。**因此只在自身双侧有限域门之后复用该库，不能只给shape白名单加date。** 这不是将库默认扩展称为严格core，也不复用规则comparator、不改任何进程全局转换表/DAWG/parser/logger/constraint map。

本轮只静态阅读这些源，未导入库或探针；复用路径能否满足全部已采有限域，仍需未来真实正反验证。若发现不一致，保留输入/实际库调用/报告，回到同一owner窄修；不得后处理conforms或拼接伪造ValidationResult。

保留原Literal lexical/datatype。违规value必须来自真实report，仍以完整focus/path/value/sourceShape/component/severity及conforms比较；报告BNode ID按结构对应，不固定随机序列化ID。新政策的原C相等输入预期为true/空报告；min早于bound或max晚于bound则为相应真实普通范围违规。旧legacy对原date bound仍拒绝，旧历史pending/golden保持。

## 5. 资源和失败边界

保留现有每份文本1MiB、每图100000 triples、exact Graph/Memory拷贝、离线拒外联和其余既有门。本政策不承诺新的worker/native对象或耗时上界，不改变原H/物理监督。

新增date preflight拟采用私有`i05-utc-date-preflight/1`固定work cap1000000，仅UTC分支使用，不能由caller调高。每次新shape/link/target/value访问、日期字段检查及计划保留前先debit；超额复用`GRAPH_INPUT_LIMIT`，Validator0，不回退legacy。此预算只界新增preflight的显式访问，不冒充库内部CPU/对象分配证明。该额度是设计中的精确writer目标，不是当前已有运行保护。

- 先检查长度恰11及ASCII，再取有界年月日整数；不对巨大字符串先做日期解析或任意精度换算。
- 计划和focus缓存只按原图有限实体保留，不物化target×property×value笛卡尔列表；相同targetClass可共享实际focus集合，仍计引用。逐值迭代，不能先收集全部多重匹配再检查额度。重复shape关联的访问也须收费。
- date域/预算失败发生在Validator前，返回固定错误，无部分报告；不得先运行Validator再用失败结果倒作准入检查。
- 本设计不收紧legacy受理域。新显式政策有上述有限域和preflight cap；其资源拒绝属于新政策输入门，不可算规范报告通过或悄悄修改旧golden。

### 5.1 确定的顺序、计费与错误优先级

`i05-utc-date-preflight/1`从原通用形状结构门通过后开始，覆盖新增bound域门和后续date preflight；原文本解析、terms、通用结构门的既有顺序不重排。预算余额初始1000000；每次操作先扣相应整数单位，不足即`GRAPH_INPUT_LIMIT`，不执行该操作。余额用完后不继续找“更具体”的输入错误。相同输入在本政策内须得到相同首错误，不依赖Graph/set枚举顺序。

新增遍历必须使用以下稳定顺序：先按NodeShape IRI排序建立关联，按PropertyShape IRI排序核所有inclusive bound；约束固定minInclusive在maxInclusive之前。bound全部通过后，事实scope门保持原位置，再按NodeShape IRI、其PropertyShape IRI、focus IRI、value排序逐对检查；只遍历含inclusive约束的property link，但也要检查非date bound遇date value的反向混合。targetClass的focus集合必须按class IRI在本调用缓存一次，命中也须计费。value排序键固定为IRI `(0, str(term))` 或Literal `(1, str(datatype)或空串, language或空串, str(term))`；本允许域无其他term类型。不用n3序列化、库比较或date解析作排序键。一次property的min/max按上述固定顺序检查；同一值参与不同约束/关联时重新计相应访问费用。

每个集合先仅收集、保留及排序，完成前不检查其中date域或库值。收集失败直接资源拒绝；收集成功后只按稳定顺序核域。因而底层枚举先返回哪个成员只影响中间访问顺序，不改变该收集阶段的最终费用/拒绝码。缓存只能按上述遍历在首次使用时建立，不能按命中率改变算法或跳过收费；不缓存跨调用结果。

| 新增操作                                                 | 固定先付单位                                                                                                                           |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 建立一次Graph查询迭代器                                  | 1                                                                                                                                      |
| 一次`next`尝试，包括最终StopIteration                    | 1；在拉取前扣，不先读后付                                                                                                              |
| 保留一个列表/缓存/计划成员，或新增一条关联引用           | 1；在append/insert前扣                                                                                                                 |
| 从已经有序的计划读取一个shape/link/focus/value/bound引用 | 1；重复读取同样收费                                                                                                                    |
| 构造一个有界排序键                                       | 1；只取上述原term字段                                                                                                                  |
| 长度n集合的排序预约                                      | `1 + n * ceil(log2(max(2,n)))`；构造键后、排序前一次扣足，使用固定整数公式，不以实际比较次数收费                                       |
| focus缓存查找（命中/未命中相同）                         | 1；未命中另付完整收集/保留/排序费用                                                                                                    |
| 一个date原词法有限域检查                                 | 每次7：长度、ASCII、固定格式各1；年/月/日有界整数各1；公历月日/闰年检查1，按此顺序逐项扣付，前项失败即拒绝；已有检查结果不跨操作数复用 |
| 一对操作数的datatype分类/同域检查                        | 1；不兼容即`RDF_TERM_INVALID`；bound之间混合仍在前述bound阶段为`INVALID_SHAPE`                                                         |
| 一个已采date的库值类型及年月日一致性检查                 | 1；仅在有限域门后，失败`VALIDATION_FAILED`                                                                                             |

这里的单位是固定政策工作单位，排序预约也不是库CPU/分配上界。计划构造只准用上述Graph迭代、付费保留和排序；禁止先用未计费的`list/set/dict`推导式或全量扫描得到计划。形状参数先校验，每个bound的有限域先于其库兼容检查；实际value同样先有限域后库兼容。所有bound兼容检查通过后再进行事实scope/实际value阶段。兼容检查在每个相应操作数域门后执行，全部通过才进入真实Validator。

必要验收新增一个次序反例：100个同targetClass、不同path的NodeShape及约20000个focus，只有一个path含合法但非Z date；用相同RDF内容的不同triple序列化/插入顺序，核实际错误码、阶段和费用一致。另分别构造“稳定顺序中域错误先到”和“预算先到”的输入，保持两种结果分立；不得人为将所有超域输入的预算错误改成词法错误。

## 6. 最小精确writer申请

本窗仅设计。未来另立产品窗口时，建议从该固定设计另建施工候选，不修改旧收件产品或原测试。

| 路径                                                          | 最小拟改                                                                                                                                                                                                                                  |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/engine/src/ontolearn_engine/semantic.py`            | 唯一既有writer：显式range dispatch/新UTC entry版本；私有原词法公历检查和有界target/value preflight；`_shapes/_check_shapes`私有range参数默认legacy；只在UTC局部允许date inclusive bound。原整数宽点/legacy分支/全局版本和SH谓词白名单不变 |
| 新 `packages/engine/tests/test_semantic_shacl_date_policy.py` | 新政策纯输入、真实Validator observer及完整报告/拒绝/资源/隔离验收；旧整数/shape/DAG测试不改                                                                                                                                               |
| 新授权过程prefix                                              | 固定候选、输入身份、完整双流/环境/报告及独审；T05消费者接线另授                                                                                                                                                                           |

若沿现有145受控清单，新增该唯一测试后为146受控，其中仅semantic.py既有writer，其他144既有成员只读；具体输入清单由root下一窗口固定。无需修改semantic_turtle.py、规则comparator/profile、execution/scopes、公共schema/error表、Store/Job/selected、依赖/lock或SQLite路径；不实施object envelope。

## 7. 必要的未来真实验收清单（本轮均未运行）

| 组            | 必须观察的结果                                                                                                                                                                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 原C相等输入   | 复用原只读`C-inclusive-date-entry`原件。UTC策略实际Validator1、true/空报告，按原golden已存在的扩展条件分支比较；legacy仍0调用/INVALID_SHAPE。不得改旧core条件文本、原golden或旧pending历史                                                       |
| 两种inclusive | min的before/equal/after分别false/true/true；max分别true/true/false。false须完整MinInclusive/MaxInclusive真实六字段，value保原date spelling                                                                                                       |
| 公历/边界     | 0001-01-01Z、9999-12-31Z、2000-02-29Z合法；1900-02-29、坏月/日、0000、负年/扩展年、非ASCII/宽度/空白/T/小写z均固定前门拒绝。正负输入分别置于bound和实际value两侧，不能只验shape                                                                  |
| 时区/类型     | 无TZ、+00:00、非零offset不转换，均0调用拒绝；date与dateTime/数值/字符串/语言串/IRI两侧互换均拒绝。date bound与非date bound混合的同一shape在无target时也拒绝                                                                                      |
| target/多值   | 无target、无值、minCount缺值、共享property不同targets、合法不相干非Z date分别保持实际语义；一个目标有多值时全量检查，任一超域整个调用0调用拒绝。反向date bounds不预修，真实Validator给完整结果                                                   |
| 策略与回归    | strict/整数宽入口×legacy/UTC四组合；原坏integer Datatype案例无date范围时仍给真实false，不相干target可true；不同policy身份不混用。UTC调用后旧parse/query/reason/check和legacy保持原行为；非date原规范格不被date政策改写                           |
| 拒绝与资源    | 未知/遗漏policy、坏shape/IRI/unknown datatype/外联/blank-node/nonfinite/Turtle/文本图限额保原门；exclusive当前仍unsupported。构造在原图/字节界内的重复target关联触发新preflight work上限，证明先付、0调用且无部分报告，不用小fixture成功替代边界 |
| 原件/证据     | observer仅委托原run；保存实际输入/argv/环境/exit/stage/固定错误/调用数及原始RDF report，逐完整六字段+conforms核验；固定源前后不变。新候选一次必要正常check承载原回归并另核12sources，独立审新改动/证据；具体运行另授，不以本设计算通过           |

用户政策选择已关闭；产品date支持和真实SHACL报告、T05消费者联验、正式execution/Store/Job/selected、原指定双外审、CI/平台/真人与合并门按未来实际证据关闭。SQLite和whole-worker/H等独立HOLD未改变。
