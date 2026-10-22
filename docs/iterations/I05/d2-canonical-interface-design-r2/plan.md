# Canonical interface R2：已收17类86字段的窄增量

本轮纳入总控正式接收的 d6ecbc887e1bf9acd5e98b18237d6740d2e61796 两纯文档，完整现有注解目录17类/86本地字段。原176+原canonical设计29=205件@6b94c152a8fca0f0e26d377b0e4d79ff4d64b8b5冻结；原candidate eb5d401…仍为历史。R1已由root正式通知IR1-P2-01两触发；只按正式通知作本轮修订，不读其WIP、不猜其他意见。新根收件文件已按唯一指定路径单次读回，完整原流/实际exit见review controller-reception-read.json；未扫描或追其引用。

## 目录层的实际变化

revision-delta按固定Git/path/bytes/SHA引用原八设计，不重新打包原11事实/原流。原field-codec-bridge的52目录263行中，7个prose helper目录27行由新精确声明细化；其中14条此前未知注解现在有精确类型。另新增10个helper目录59行。新type-field-map完整保17/86的class/source pin、decorator/base原语法、field顺序、annotationSyntax、defaultSyntax、sourceLine与精确pureFactPointer；有效视图为64目录325行，原其余236行逐值保持原文件引用。不能把本地声明86当全产品字段总数，或把17当production/probe/material approvedSet。

SourceRecord、TermInput、InputLocation、ProfileLimits、Variable、Triple、Comparison、RuleSpec、Catalog、BindingMatch、ComparisonEvidence、HeadEvidence、PreparedFiring、PreparedFiringBatch、ProfileValue、Number、Calendar的字段目录部分现已收到。因此Q01原“缺少指定类字段/type/default/顺序”的子项记收到，不再重复索取这些17/86；Q01原投影注册/recordType精确标签部分仍pending。其他Q02–Q09不因注解齐而关闭，已存在字段语义/合法enum与域关系另需原owner纯接口。

## 具体导出蓝图与边界

proposed-type-records为每类提供17个逐处NEW-PROPOSED-NOT-ADOPTED的记录蓝图，requiredFields按原声明顺序完整86项。它只附加到原NEW FieldSlot/ClosedValue提案；所有actual adapter pin和原wire discriminator仍null。sourcePath/className是源码定位，不是旧recordType tag。int/str/bool/bytes和nullable/typed tuple/union只按原注解列出结构线索，不执行constructor、不反射实例、不凭名称补类型；str不补enum，不从profile/term/operator/domain字段猜合法词表。

原记录实例即使字段有默认表达式，导出时该字段仍必留。defaultSyntax=null代表该声明未给默认语法；字符串None/False/1/()/PROFILE/数字/空字符串引号是源文本，不求值、不补actual、不当收费cap/物理票。Number.denominator的1不准补丢失值，也不能从int注解签非零、有理数规范性；ProfileLimits17项默认不等实际已付/已批预算。Calendar.second:Number及negative_zero:bool现有注解已知，不证明数学/域合法性。

ProfileValue.value依然object，domain依然str；二者闭合关系没有收到，故ProfileValue.value阻断传递到ComparisonEvidence.left/right、PreparedFiring.comparisons、PreparedFiringBatch.firings等完整adapter。native_result:dict以及原receipt/ReadonlySequence.items等未细化tuple/dict/object没有由本补件封闭。无法完整导出时继续保原完整byte/preimage/sidecar及明确layout-blocked；没有旧专用wire时不得制造raw或用null假完成，未知值不得经通用getattr/**dict**/repr/str反射裁成子集。

## 原codec、摘要及接线原样继承

旧12API、15return记录、ProfileComputation14/Explanation继承15、RootRef5 kind:str无enum、ReadonlySequence.native_kind与所有sidecars仍按原固定设计。production recordType平铺原字段与probe完整模块recordType+嵌套fields、material原input codec、legacy source4/provenance13/result5继续分开；新17目录不证明这些codec已收全部注册或无损round trip，不能用同一个17计数替approvedSet。

原16配方及catalog/canonical_string/IMPLEMENTATION、原rows8192 Python字符与末片、scope未显式allow_nanFalse和profile严格JSON选项均不改。annotation/default文字不是旧preimage；不从新字段目录重算旧source/definitions/payload/rows/catalog摘要，不求值锁表达式或追资源/LOCK_FILE。原新relationCore/tag无变化，无新自环、无新增digest替旧值。

已接收共同identity角色/链接仅沿原六键外部pin引用：receipt.runId来自真实先登记caller attemptId，child ID只首受信context。policy正文不读，原R2/T03冻结null不回填，另30字段仍CR-R/CR-H；registry/collector/layout/source/issuer/17L/运行权仍缺。旧1241、header18、四schema与source/依赖集合不改。

## 采用与静态验收

authority-requests-update将Q01目录子项与注册/tag残余分列；Q02闭值/domain/native_result、Q03旧codec、Q04新adapter、Q05真实旧preimage、Q06live verifier、Q07真实collector、Q08权限预算、Q09安全异常仍具体请求，不沿pin读source-index/源码/方法/算法/actual/expected/probe_inputs或retained外审内容。

只对本增量做指定Python stdlib JSON/纯文本校核：2输入SHA、17/86逐字段逐值、27交集和14注解细化、有效64/325且236原行引用不变、17新蓝图全标提案/default不fallback/全门false、手工例与声明反例。未重跑原已通过的codec/行切片/摘要等范围，更未执行产品/旧codec/原model/103源检查或JSONSchema引擎。首轮原语法Fail仍在旧205，不修改。

稿件和真实checker结果先交root，由root统一转正式R1意见；不读独审WIP。独立意见若需本轮改动只在新prefix形成明确补充/版本，旧205保持冻结。仅在root协调封口后显式stage本方新路径，读取实际cachedcheck0再本地candidate/process；无AGENTS/push/Goal/GUI/网络/安装/build/native/DB/runtime。设计目录层收件不关闭M02–M05/G02G03实际接线、fee/capture/issuer/17L/full417/wholeOracle/父137/JobStorewholeH/SQLiteHOLD/平台真人/指定双审/CI/develop任何门。

## 正式IR1-P2-01的独立修订

root正式通知的P2与17/86收件分开登记于revision-disposition。原R1为Fail，949结构核过仍发现两处语义目录遗漏；本稿未读独审WIP，正式报告及独审receipt已由root授权全文只读并匹配bytes/SHA，精确pin见revision-disposition；其余附件未读。selectedFacts每项新增triple/sources两行及sources[j]到三已知分支的完整父子实例链接；production observation另增known optional mutation一行/目录，原13必需键不改。实际有效目录64=52-7+17+2，行325=263-27+86+3；原其余236行仍固定引用。

mutation absent不补None；present完整保留原值；present null仅作为原值保留，内部合法性/nullable语法未知，不给产品接受或拒绝expected。非空selectedFacts与mutation有/无/null手工例只检查目录及原值保全，不以空数组绕过。已知key目录完整不代表值grammar/旧codec/live authority封闭；未知内部仍pending，raw/sidecars/原preimages不能裁。

正式报告11122B/SHA35b1d913c4baf3bbe07d3a582ae16fd9ed76479d77841e865b89b0ec5efc5b11与独审receipt5188B/SHA59e20cd2a31de65a0f4a220b20eafcf565cb2ca27295aef21900fc0e6b7da600均已全文只读并保全readback。两者尚待root另行Git封存，本作者不stage14个独审文件，不把949结构断言0转为原R1coveragePass。
