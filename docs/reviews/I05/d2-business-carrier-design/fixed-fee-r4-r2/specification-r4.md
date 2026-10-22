# I05 收费规范 R4：完整元数据前门与类位置门（提案）

R4 版本为 `i05-reference-fee-program/4-proposal`。继承 R2 完整动作目录、R3 严格双 tape/IFR3/首错与生命周期规则，仅替换本文件明确列出的前门和静态类位置检查。所有 R1–R3 文件、输入、原 typed/golden 和独审 Fail 冻结。本候选待独立 delta 审查，不自认发现关闭。

## 1. 固定合同与新提案分栏

固定 integration:63 要求整次定义（含 disabled）的 RuleSpec 类型、rule_id 类型/有界字节/唯一性先全部验证，再排序和分配；integration:59 要求新 profile 的 rdf:type 类位置为已声明类 TermInput，不能用 binding 使非法语言位置成功。它们是本轮修订依据；不修改 legacy、Catalog 来源、原 cap、T05 受审候选或数学 oracle。

新 fee-codec/binder/数学图只用于收费枚举，不输出产品业务 expected 或发行对象。完整114新程序、原现行/数学字段与新提案列分别见 [per-id-r4.json](per-id-r4.json)。现行 exact/native/wire/fingerprint/plan codec、同次真实17L/issuer/usage/capture、owner H/调用许可分别 pending；原精确预测17L与数学值仍可使用，不能被 pending 抹掉。

## 2. E00：排序、分配前的整次结构门

`metadata_preflight` 位于 bind 与 allocation 之前。先以原 C0 非负公式的固定下界 A≥24MiB/N≥1 建一个分析钱包并保 control64。所有前门动作保入同一完整程序；若后来绑定成功，使用原 Q/D/N 算出的完整 C0 cap，保留已经列出的动作与累计量。严格执行状态仍在整条生命周期/receipt 静态证明以后才建立，不是运行中退款、reopen 或借新 cap 翻转已执行首错。

前门按原输入次序逐项执行，遇首个真实结构错误停止；全部元数据通过才可进入任何 Catalog 排序、rule_id 排序或 divmod 分配。后项 rule_id 无效时，前项也没有预测 child。不得先发行 child 再依赖异常 handler 擦掉坏字段；receipt 只消费这道门验证后的 ID、ordinal、disabled 与原17L预测。

| 动作                                     | 新提案精确收费与判定                                                                                                                                                                                                                                                                                      |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 外层 dataset、input mapping              | 各1 work；必须为 plain JSON object；原 dataset pointer 和可选 `/input` 原样定位                                                                                                                                                                                                                           |
| 整次规则列表/count                       | 1 work；`definitions` 与 `rules` 不得同时作为候选容器；选定容器为 list、至多100，未提供的空规则仍按既有 proposal binder 记录缺省来源                                                                                                                                                                      |
| 每 RuleSpec mapping                      | 1 work，必须 object；不把任意外层字段转成规则                                                                                                                                                                                                                                                             |
| 每 when/comparisons/heads 列表           | 各1 work，必须原 list；其三元组、比较和既有 count/闭包/TermInput 检查仍由完整 compile 收费执行                                                                                                                                                                                                            |
| rule_id 字符串                           | 1 work type guard，必须字符串；不做 str 转换。scalar/UTF8 预检收 min(字符数,16385) work，先查字符数≤16384/无 surrogate；再1 work byte guard，UTF8≤16384B后收全B work+B scan_copy。16384沿既有 term_bytes 作为新前门的具体化，不声称现行 ID exact 收费。空字符串没有额外的非空要求，不凭探索值新增语言政策 |
| 唯一性                                   | 按原次序对每个此前 ID，先收两侧完整 UTF8 长度之和 work/scan，再完整比较；重复在当前原 ordinal 的 `/rule_id` 拒绝，未排序、未分配                                                                                                                                                                          |
| revision/digest/原definitions摘要/policy | 每个固定字段均先1 work可空字符串门；非空按同一 scalar/UTF8 表收费，policy界16384、其余65536。policy原提供时必须固定PROFILE；原未提供时保持原binder的合成来源，不冒API实证                                                                                                                                 |
| definition.source 元数据形状             | 1 work；typed `rules` 的四字段 SourceRecord 与原 `definitions` 的 ref/path/pointer/sha256 locator 分开验证。locator只为输入定位，不当成SourceRecord/授权。提供的四字符串各按上表65536界收费；typed SourceRecord另保既有65536整体编码界                                                                    |
| disabled_rule_ids                        | 1 work列表门；每个提供的ID按完整16384字符串门收费，之后才可参与已验证表的disabled预测；不退款、不把disabled变成免compile                                                                                                                                                                                  |

UTF8 最宽结果在编码前保 `workspace-C0`，objects32、scalar `8×字符数+4096` 的临时界；此 workspace 与既有 C0 arena 为同一 lifetime，最终完整静态程序把其全程最大值放在首次访问前。不能先编码任意长 metadata 再补票。正常 baseline 已有更大的 C0 arena，故没有新增data handle或并持峰；新门的动作/scan仍全收。

前门只认可原输入 pointer，不把坏 rule_id 值塞进诊断或 receipt。`entryMetadata` 给 checking/validated/rejected、已验证规则数、是否开始allocation、原 sourceRulePointer/failurePointer；拒绝时 material/native/payload 未构造，明确 `None` 而不是零。无效 metadata 的 allocation 为空：F 使用 N=0，不虚构 dummy或17L；零定义的**合法**输入则仍在前门成功后走原合法dummy路径。二者不能混淆。

## 3. 有界错误账不二次使用坏字段

`MetadataFailure` 只持有限错误分类和原始 JSON pointer。完整入口捕获同一真实前门失败，沿原H01规则先证明所有实际生成的handle/累计slots及有限receipt，再严格执行前缀。IFR3格式、hash域与固定宽度不变；header和钱包名来自已验证/固定字段，child只来自完整通过的元数据。因此整数ID、坏外层容器、后项坏ID或坏revision都不能再从receipt长度/编码路径逸出同一个异常。

非string ID在type门就拒绝，未做任何ID encode/sort/allocation；invoice仍有5 work真实结构检查、H01、receipt、control终态清理。不是抓第二个异常输出空假账。较晚坏ID可已有元数据workspace，但仍没有child；所有已付检查不退，失败所有引用清零，无成功前缀。binder在元数据通过后因原始term拼写失败时，原完整ASCII输入 guard scan保持，不因新前门而省掉旧发生点。

原R3全静态生命周期/receipt票、严格全向量原子预付、稳定更早resource/semantic首错、末项错误/cleanup、失败不退不重开均继承。未知或未执行尾段不能补0，分析 tape不能称已执行。H01不足时仍必须标H01Paid=false；本轮未更改该执行器，不靠旧通过覆盖新元数据门。

## 4. RuleSpec when/head 的固定类门

integration:59未将类位置要求限定为head，:64明确任何匹配前预检全部when/comparison/head/引用。因此本门适用于同一新RuleSpec的when和head，不扩展到普通输入RDF图的rdf:type三元组；这是完成已采用条款，不是采纳新业务规则。

head仍先收3 work位置检查、逐Catalog声明完整扫描、1 work受控引用检查。在同一已有检查动作中，rdf:type object 必须是固定、kind=iri、且在输入Catalog已声明的类 TermInput；Variable即使未来binding为该类也在compile失败。enabled、disabled、零匹配全部执行此门，不进入join再“修好”语言。该修订没有给正常合法head增加动作或单价。

when沿原3work位置检查路径，再以1work要求固定IRI类TermInput；Variable/literal在此拒绝。固定IRI则对Catalog.classes每个完整声明收两侧UTF8长度之和work/scan，再1work确认已声明；未声明在该参考门拒绝。此检查在每个实际compile发生，包括完整restore的R16-child重新compile；held-byte先拒路径不收费未执行的R16。

仅原语言允许的位置延迟binding值校验：合法Variable subject在实际head检查时必须为IRI；合法object/data property的Variable object在实际binding后检查相应IRI/literal kind。新正例保这些路径，不能以全拒绝变量规避类位置门。legacy不在本纯收费解释器中重新实现，也不改变其原模式。

## 5. SourceRecord发生点与每ID差异

C0原逐occurrence SourceRecord条款严格指 **record-term.source** 与 **definition.source**；baseline84+1=85次完整验证/85次合成text摘要，61420 scan与35383 hash不变。定义内部常量TermInput.source的完整输入/解析/指纹另由M0原动作支付；R4不把“每个term”扩大成额外C0发生点。E00检查原definition locator元数据是另一明确动作，既不发行真实SourceRecord，也不补Catalog许可。

[metadata-delta-r4.json](charge-reference-v4/metadata-delta-r4.json)为114每项独立算术差表：从固定纯输入按本节E00表重新计算新增work/scan/eventShift，再逐项与R3金额、cap、峰与首错序号交叉。正常114新增C0元数据门，以及M-child和实际R16-child重编译的when类门；逐项独立验证hash及其它钱包金额/17L、cap、whole-H峰保持；每项依据不套baseline统一价格，也不按actual调价。

完整v4 source、baseline双tape、27完整入口正反程序、114可重建配方、独立无reference import的replay/IFR3/第二encoder/手算审计及141两seed证据均另名保留。未重跑无改动numeric/Q6或旧小Ledger；其旧范围结论不外推本次前门。产品实施delta仍需把本前门和类位置门接到真实同次预算、capture、receipt/cleanup与发点，当前代码合规与否未证明，T05候选不修改。
