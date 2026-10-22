# C1 信封字段与规范producer候选

所有P名和字段是可审技术形状，尚未分配公共方法、正式schema版本或格式号。严格字段表须T01同版冻结后才可实现；不产生第二canonical。

## 1. 三种身份及本机注册

1. `inputSealDigest`：受信I/O封存的完整ZIP实际字节SHA256，在包外由main持有。preview、确认、附件准备共同消费同一个seal。包内不能自报此hash充作本机核验；不做manifest自hash循环。
2. `memberByteDigest`：成员完整未压缩原字节SHA256，不证明作者/owner、语义或学习资格。
3. `collectionDigest`：owner固定canonicalRef对完整逻辑业务集合计算的digest。按catalog组装有序typed records后交唯一canonical核；不能用ZIP遍历顺序、分片concat的字节hash或源DB hash代替。重分片可改变member hashes和package hash，逻辑业务不变时collectionDigest应按同一canonical保持。

本机拥有受信格式注册快照，不从manifest加载插件/URL/代码。注册项精确匹配`formatRef + manifestSchemaRef + producerProfileRef + roleSchemaRefs + canonicalRef + scopePolicyRef`；各Ref至少含owner批准的id/version/content digest，不能只比较major/minor或minReader字符串。相同版本标签但digest不同拒绝。resourcePolicy从本机批准注册表取得，包引用只允许选择其已登记项，不能带更高limits覆盖本地。reader/writer能力和执行semantics/engine/lock分别匹配，不混为一个版本号。

C1选精确组合白名单，未知required角色/字段/版本一律拒绝；不先实现minor宽容或忽略扩展。需要兼容时由T01显式增加同版可验证注册组合/迁移链。迁移消费不可变源，输出新投影和plan/digest，用户重新确认；不改原包、不调用DB迁移充项目迁移。

## 2. manifest逻辑字段

manifest是strict UTF-8 JSON对象，无BOM、重复键、非有限数值或尾随第二值；整数计数用非负精确JSON整数并受本机预算，类型不强转。未知字段拒绝。字段序列化字节规范交唯一格式owner固定；不新增通用JSON canonical算法。

| 字段                                                              | 具体形状及校验                                                                                                                                                                                                  |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| formatRef / manifestSchemaRef / producerProfileRef / canonicalRef | 上述精确注册Ref；producer声明不证明来源身份，外部未认证仍按unverified，不偷设PKI                                                                                                                                |
| kind / scopePolicyRef                                             | kind为full/template；policyRef是本机已批准范围政策。full保七必需角色；template具体集合由尚待F01政策提供，不能让C1默认定案                                                                                       |
| selection                                                         | rawSources/derived/history/agentSessions四个必填boolean；每项附显式选中业务对象typed refs及scopeDigest；选中不等于能力验证                                                                                      |
| sourceSnapshotRef / versionSet                                    | T01一致读的业务快照和operationSequence、应用/learning等版本、角色schema及执行版本Refs；无机器路径、DB页、旧授权                                                                                                 |
| roles                                                             | 按本机批准固定角色顺序的数组，每项含roleId/schemaRef/memberIds/recordCount/collectionDigest/coverageRef。一个roleId只出现一次，集合真空需owner coverage                                                         |
| members                                                           | 按同一角色序和ordinal列出；每项memberId/path/roleId/ordinal/mediaType/compressedBytes/uncompressedBytes/memberByteDigest/recordCount/firstRecordKey/lastRecordKey；raw改用sourceObjectRef，禁止无意义record边界 |
| coverageRef / referenceIndexRef                                   | 指向受role schema管理的typed业务对象，而非可打开文件/URL；完整源族/ledger/retirement根枚举先于最小闭包，未选正文不能藏进证明                                                                                    |
| requirements                                                      | 每项业务依赖typedRef/版本/状态/安全reasonRef；不带endpoint主体/凭据/可执行grant。缺依赖不自行转template                                                                                                         |
| sourceCapabilityClaims                                            | 可选，明确是未受信来源主张；本机结果另算，不反写为工具证据                                                                                                                                                      |

manifest自身不在members中。ZIP实际成员数必须等于`1 + len(members)`且无重复；roles.memberIds与members双向一一覆盖。manifest/成员预算须来自已批resourcePolicy，缺实际数值不允许正式运行。预览摘要仅显示批准字段，不把整个manifest往返renderer作为提交能力。

## 3. JSONL分片与真空角色

C1选择每个业务角色有序strict UTF-8 JSONL分片：每行一条完整typed record，LF分隔且最后一条也有LF；无BOM/空白行/跨行记录，每行严格拒重复键、非有限常量和尾随JSON。记录的字段/schema、recordKey提取器及排序比较器由该角色owner固定；不拿Q6业务比较器或JSON文本序猜record顺序。每个recordKey在同角色全局唯一，跨片严格递增；ordinal从0连续，memberIds顺序必须相同。单条记录不得拆开，过单记录上限拒绝。

角色recordCount=0时，C1选`memberIds=[]`、无该角色成员，并以已批准canonical的空集合digest及完整源coverage证明真空；有完整role项而无owner证据仍是缺口。非零角色至少一片，各片recordCount正数，首尾key与实际一致，各片recordCount求和等于role总数。first/last只作快速核验，实际仍逐记录核全局重复/顺序和canonical集合digest。完整full必须保七个role项，即使其中经证明真空；零成员不代表省略role。

rawSource按明确选中的完整封存对象一对象一bin成员，ordinal按批准source身份顺序。C1暂不提供raw chunk重组模式：超单对象/成员/包预算显式拒绝，不能截断或转码。若后续T03/T01确定需要chunk，另行版本化精确chunk目录/offset/终态/full-object hash，不在本版reader猜拼。该编码选择不承诺任何产品容量，Q5仍未有验收线。

路径由producer生成`members/<registered-role>/<ordinal>.jsonl`或raw的`.bin`；role来自固定ASCII枚举，ordinal十进制无多余前导零，不来自用户文件名。memberId是catalog内唯一不透明ID，不当业务对象ID；typed引用指业务对象而非ZIP path。不能借path创建renderer文件权限。

## 4. 规范ZIP producer的有限范围

C1仅提出本应用规范producer profile，不新增“任意标准ZIP工具可导入”的互操作承诺。候选writer固定如下；实际格式owner应给每个字段的同版正反fixture再批准，现检查器66cc不变。

- manifest路径固定`manifest.json`，作为第一物理成员；随后members按catalog顺序。只允许生成式ASCII文件名，无目录/软链接/特殊文件，禁止重复/别名/绝对路径/盘符/NUL。
- 仅采用STORED或DEFLATE，writer固定本版具体压缩参数并纳入producerProfileRef；reader不要求重压缩得到相同字节，但核方法白名单、真实完整流/CRC/hash/实际字节预算。不支持加密、ZIP64或data descriptor；必须在本机已批profile边界内，否则明确拒绝。
- 无archive/member comment、无extra字段、无前缀/自解压stub/尾随隐藏字节。UTF-8 flag及创建系统/版本、固定时间戳和普通文件属性等元数据须列入精确producer profile；当前无获批值，不能据本表声称已有完整wire profile或实现。
- local header与central的原始name/flags/method/CRC/长度逐项一致；offset指向唯一正确成员且各数据区不重叠，无隐藏间隙；central连续并按同catalog顺序，EOCD计数/大小/位置一致且恰为文件末尾。拒多磁盘。
- reader从受信seal核物理长度，先按本机预算读有界EOCD/目录，再读有界manifest；声明不能令reader无界分配或跳过实际输出计账。压缩输入、解压输出、record/parser状态与完整catalog内存分别计账；不能以未压缩上限推内存上限。

尚缺元数据精确值是F04技术owner待冻结项，不是新用户问题；不在此自行分配实际producer版本。规范profile的限制不表示所有外部标准ZIP必失败，也不宣传已兼容任何未列工具。
