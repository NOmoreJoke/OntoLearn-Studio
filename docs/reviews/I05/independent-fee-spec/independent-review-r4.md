# I05 费用独立规范 R4 独立 delta 审查

结论：**Pass，限定于获准的提案规范、完整错误入口和费用数学。** R3-F1/P1、R3-F2/P2 在冻结 R4 中已处置；本轮未发现新的 P 级问题。本结论不签发实际权限、不认可真实产品收费或打包，也不解除尚未具备的实施与发布门。

## 对象与证据边界

审查树为 `I05-independent-fee-spec`，revisionBase `6bb1c1e5a4250468f894033e42864d480ccdb815`，candidate `f6b886208839037aeae93947549d32fc3ddc6b89`，process/HEAD `29705204c9f8274d7ab17433bd6ac3094461244b`。核心 `charge-reference-v4/reference.py` SHA-256 为 `bc47b16bf528b973aeebcc0be4a103bf00acbf0f351485f5370510817bf1467c`。

独立逐件核了 manifest 的 267 个成员及 manifest、作者 process receipt，共 **269 件 current bytes = process Git blob = 声明 SHA**；revisionBase 的原 **203 件逐字节不变**，delta 仅两个获准文档前缀下的 66 个新增文件。manifest 为 55,402 B / `a3b6d25cfc6541dfea96cfc29659db440b6394b1f143ebe6574410587ccd8516`；作者 receipt 为 106,221 B / `6f7f53ced437ce874d00707287b66906622c2175950a02ea997d427319d44562`。隔离 raw 只作 opaque bytes/hash 核验，没有解码正文。

现行 AGENTS 为 15,147 B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`；其既有未暂存变动属于已授权政策传播，未由审者修改。原设计窗、binder/收费数学 amendment、Q6 纯文本权限边界继续适用；新增桌面 guidance 不扩大本窗。

全文审阅本轮 specification、handoff、手算、disposition、revision record、v3→v4 完整 diff 与新增脚本，静读 import、AST、写入范围后才运行只读测试、审计和自己的数学核验。未运行作者生产/封存脚本或旧审查脚本；未读取产品算法/actual、完整 2d5、隔离 raw 正文、D2/WIP。未运行产品、普通 pytest/npm/build、GUI、数据库、网络、安装、版本或模型探针。

## R3 发现处置

| 旧发现                                                      | 独立复核结果                                                                                                                                                                                                                                                                           | 结论       |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| R3-F1/P1：JSON `rule_id=7` 先分配后编码抛错，错误载体再抛错 | E00 在 bind、排序、allocation 前逐条检查外层容器、ID 精确类型、UTF-8 字节上限与唯一性、RuleSpec 元数据及 disabled IDs。原整数 ID 和其他非法前门现均返回完整分析/执行 tape、首错、paid prefix、H01、失败清理与 IFR3；未完成绑定时 allocation 为 `[]`、无 native/payload、无 dummy 17L。 | 本窗已关闭 |
| R3-F2/P2：`rdf:type` object Variable 被当作可延后绑定       | when 与 head 均在 compile 要求固定、已声明的 Class TermInput；enabled、disabled、零匹配均先检查并收费。合法 Variable subject、普通 ObjectProperty 的 Variable object 与一般输入 RDF 图不被扩大禁用。                                                                                   | 本窗已关闭 |

F1 的义务来自既定 JSON 输入/规则元数据前门及完整错误账本要求，不是要求支持任意 Python 对象。检查不以 `str()` 偷换 ID，也不把 raw locator 变成 typed SourceRecord 或权限。新造第三条 `rule_id=False`（前两条合法）在事件 42 拒绝，`validatedRuleCount=2`、尚未分配；dataset `review/a~b/third-bool-id-before-bad-term` 的 pointer 正确转义为 `/datasets/review~1a~0b~1third-bool-id-before-bad-term/rules/2/rule_id`。第三条 `source.reference=7` 在事件 59 定位到原字段；disabled IDs 后项 bool、双规则容器和缺失 heads 容器也都有完整载体。再在 record 放入非法 scalar，仍由更早的元数据错误拒绝，没有进入 binder 后被尾错误覆盖。

错误载体的分析证明与执行事实分别核对：分析 tape 可以记录被执行资源拒绝截断后的语义结论，执行 tape 的 firstError/paidPrefix 才决定实际首拒及费用。独立降低同一输入的纯数学 C0 work cap 至 1,063（H01 + 2）时，在事件 5 的序列门先因 `used=1063, requested=1, cap=1063` 拒绝；更晚事件 42 的非法 ID 未被执行、`semanticAnalysis.reachedByExecution=false`。H01 已付、失败 live refs 清零，无成功发布前缀。此人为降 cap 仅是独立边界反例，冻结候选的原 caps 未改。

F2 的边界来自批准 integration 文本的全规则 Triple 门，适用 when/head，不扩大为一般 RDF 图门。独立新增 Variable、literal、未声明 IRI object 的 when/head 完整入口反例，覆盖 enabled/disabled/zero-match；均在对应 compile 阶段拒绝且未先 join。另以已声明 Class、Variable subject、普通 property 的 Variable object 作正例，确实完成。没有仅补 head 或依匹配是否发生而跳过静态权限扫描。

## 完整数学与回归证据

自己的 verifier 从固定纯输入重算 114 项，并重算作者 27 个完整入口，共 **141 项 × seed 1、2**；两次均实际 exit 0，全部字段与冻结程序一致，两 seed 的逐项摘要完全相等。每项均由独立实现 replay 分析与执行 tape，并独立解码 IFR3、验证 footer 自 hash、字段数、首拒 ordinal、执行 hash、paid 九域、live/peak、allocation 七项 divmod 及十项结构限额、H01 预付量与失败清理。

replay 不只数事件：逐 prefix 重建 used/live/peak、whole-H、holding handle 生命周期、累计 slot 不回流、atomic 向量首拒、control 保留至 terminal、拒绝后未执行尾与清理、失败返回引用为零。IFR3 解码没有调用 reference 的编码器；该审计证明的是提案 wire 数学，不能冒充当前产品 codec 或真实同 issue 17L。

114 项合计分析事件 **236,545**、执行事件 **236,484**。baseline 为 **2,455** 项，C0 work **3,279,051**、scan **2,275,390**、hash **823,438**；M0 work **141,824**（when 增 262）、scan **4,127**（增 260）；ENTRY **176,580**、G **185,814**。输入材料仍 **85,953 B**；receipt **792 B**、H01 work **152,824**；h8/s **149,538**、全峰 **149,697 objects / 6,819,815 scalar bytes** 保持。

逐 ID 独立从原字段计算 E00，以及从声明类集合和 when 的完整 IRI 计算 compile 扫描，涵盖实际 R16 重复 compile；与 metadata-delta 及 v3→v4 所有 wallet/domain 差额一致。全 114 的 E00 增量为 **53,265 work / 25,379 scan / 3,928 events**，when 增量 **30,699 work / 30,501 scan / 657 events**。不是给各 ID 统一套 baseline 差价；所有 caps 与 whole-H 峰值逐项不变。

固定 114 中仍仅 E.5 round4 为资源首拒：事件 **13,732**，input 已付 **255,390** 加请求 **12,342** 超过 **262,144**；此前 M0 work 已付 **404,868**。binding/firing/head/trace 累计不回流，未执行尾不收费、不发布；资源拒绝不被分析尾的语义错误替换。

另执行作者 6 个 focused 方法和只读 execution audit，均实际 exit 0。原六错误输入、occurrence source 验证与共享对象/JSON 读回差异均在完整 141 重算与审计中保留；alias 不能省掉逐 occurrence 验证。旧 numeric/Q6 与小 Ledger 的未改部分继承先前审查适用范围，本轮未无意义重跑，也未把继承结论说成新产品实测。

## 新造边界与未扩大之处

独立新增 **25 次完整入口调用：21 个预期拒绝、4 个成功**，全部双 tape replay 与 IFR3 断言通过，未有异常逃出入口。上述第三后项元数据和资源优先外，还检查了：

- U+10000 重复 4,096 次的 ID 恰为 **16,384 UTF-8 bytes**，可完成；4,097 次为 16,388 bytes，在 E00 的 byte guard 资源拒绝。未用字符数冒充字节数。
- `é` 与 `e` + combining acute 是两个不同完整字节 ID，均保留且按实际字节顺序分配，没有新增归一化规则。
- raw definition 的 `{ref,path,pointer,sha256}` locator 正例可完成；将其塞进 typed rule.source，或将 `{reference,digest,revision,text}` 塞进 raw locator 均稳定拒绝。合法 locator 仍只是位置，不是 source body 或 Catalog/执行授权。
- when/head 的 type object 限制覆盖 fixed literal 与未声明 IRI；普通 property object 变量与一般输入图仍可用。

definition 常量 source 属 M0 已付域；C0 逐 occurrence 的新增措辞按 record term.source 与 definition.source 的实际适用域解释。本轮不把该措辞无证扩成新 P 级问题。

## 过程保全与最终边界

作者旧四次 exit 1（locator 域误判、plan 字面 1121/独立 1100、审计漏 bare IRI、漏 R16）、查询 exit 2、旧 135 项仅 head 门的中间范围，及未知退出的补丁工具均保留原证据；没有重跑旧失败版本改写其结论。早期 driver exit 0 只表示生成完成，不能推成其当时语义成功。

本轮独审记录中唯一实际非零子命令是 v3/v4 `git diff --no-index` 的 **exit 1（存在差异）**，为预期证据，不是测试失败。所有实际命令分离流保留 UTF-8/base64、bytes 和 SHA；一次直接 `pwd` 的工具边界仅返回 combined output，按实际能力单列，未补造双流。终检只核新审查文件、冻结 269/203 的完整性与 Git 状态，不再扩测试。

**仍 pending：**当前真实 codec、真实同 issue 的 17L/issuer/usage/capture、Catalog 与 source 实际权限、owner H、JobStore/平台 runtime、417 与父门等。提案 fee graph、纯数学 output、source locator、Catalog 提案或 receipt 自洽均不能代替这些证据。本轮没有调整实际费率、抬旧业务 cap、扩大政策，也没有 blanket resource reject 合法请求。

机器证据见同目录 `independent-proof-r4.json`、`independent-r4-integrity.json`、两份 `independent-r4-recompute-*.json`、`independent-r4-boundaries.json`、命令日志与 final-check。最终 bytes/SHA、准确新增文件清单、HEAD/index/status 由 final-check 固定；报告和 proof 不写自引用 hash。
