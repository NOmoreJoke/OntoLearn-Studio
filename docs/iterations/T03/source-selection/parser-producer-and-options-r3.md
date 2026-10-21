# T03 parser producer 与 options 事实答复 r3

结论：**固定 S1 303 没有独立声明并接入的真实 parser producer 三字段身份，也没有已冻结的 parser executionSemanticsVersion。** 不能把源码SHA、包版本或库版本拼成已经存在的完整parser身份。当前只可给来源事实与待采用的profile建议；T01机制golden继续使用明确synthetic身份。本答复不读T01候选runtime、不运行parser/test/GUI、不输出可导入实现；原Goal仍blocked。

本次只读T01固定 `b35cb4e21d375386775e5fc0431a8089a47195da` 的两份文档：

- `source-table-digest-contract-r1.md`：SHA `568cb308ec5db6b7b537b4a385958a475c200268d750cedd73bdb1e28ce65b79`。
- `source-lifecycle-decisions-r4.md`：SHA `17f34e57c503ddca2da18c1cb62eb22dab3b6fd250db5a600ce2a4c30930cb9e`。

自身事实来自 S1 固定 `30319412daf8ae4745987babf7bbed93c53b6b42` 的Git对象与既有封存记录，未启动引擎或重新计算解析表；完整Table数据仍复用已交0b74，不重复提取。

## 1. 已有事实与缺失身份

| 直接来源                                                         | 完整事实                                                                                                                                                                       | 不能据此推出                                                                                    |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `mapping/source.py`、`mapping/__init__.py`                       | 私有parser函数及说明，无parser专用semantics/version/implementation常量，也不返回三字段身份                                                                                     | 固定源码SHA不是executionSemanticsVersion，也不是运行producer认证                                |
| `packages/engine/pyproject.toml`、`ontolearn_engine/__init__.py` | 包名ontolearn-engine；包版本与 `__version__` 都是 `0.1.0`                                                                                                                      | 包版本不声明本次parser语义，不能单独认定真实解析被该producer执行                                |
| `ontolearn_engine/resources.py`                                  | 已有通用IMPLEMENTATION声明的executionSemanticsVersion为 `i04-infrastructure-v1`，engineVersion为 `0.1.0`；dependencyLockHash按实际checkout/frozen资源中的uv.lock全字节取SHA256 | 这是I04基础设施身份来源，不是已经注册/验证的parser producer profile；不应直接填为真实parser身份 |
| 固定303的完整 `uv.lock` 与既有包内锁证据                         | SHA `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e`，既有包记录同值                                                                                         | 只固定依赖原件；不能补齐缺失的parser语义声明或证明当前运行身份                                  |
| `mapping/probe.py` 及既有product-package-verification.json       | 固定probe核openpyxl `3.1.5`、et-xmlfile `2.0.0`、defusedxml `0.7.1`；既有本地包CLI记录这3值                                                                                    | 三个库版本不等于完整dependency lock，不是完整producer身份；原包CLI不证明正式worker/身份接线     |
| 固定registry的mapping.commit                                     | 仍为design-only，私有parse/inspection不是该registry中的真实parser业务执行入口                                                                                                  | 不把基础设施hello/Job或私有probe的元数据当作真实parser capability已认证                         |

上述resources字典若按固定303锁解释，其三个声明值分别为 `i04-infrastructure-v1` / `0.1.0` / `9f5b6d2b93d994a3e4f8a46ce5cccae99d4e024ea7531ab62dd8e85d6aa1152e`。这里只静态读回**已有基础设施声明**，不是新构造/宣称已存在的parser三元组；没有查询或启动当前runtime来冒充完整运行身份。真实parser producer身份此刻明确为“未提供/未接入”。

## 2. 最小稳定profile与身份冻结建议（提案）

1. 由T03描述parser语义，T01 canonical与实际worker owner确认所用producer范围；建议把专用语义标签 `t03-source-parser-v1` 作为**待采用值**，复用唯一三字段身份，满足前两字段ASCII `[A-Za-z0-9_.-]{1,128}`、锁为小写hex64。此标签当前不在S1 runtime，不是已核运行值。不新增第二份身份schema或用源码SHA塞入语义字段。
2. profile至少固定：下节5个CSV词汇与默认/显式选择、CSV方言和物理起始行号、首行/空值/重复字段/稀疏行及完整有序Table投影；XLSX显式选表、只读保存值/公式缓存、宏和缺缓存拒绝；6个观察kind及字符串文本；既有8MiB/64MiB展开/50000行/256列/32768字符防御上限与固定错误语义。具体版本修改规则须由owner冻结，不能把容量上限当Q5通过。
3. engineVersion由**实际集成并执行parser的引擎**提供并与对应构建版本核对，dependencyLockHash来自该产物真实完整frozen锁；不得默认沿用本候选0.1.0/旧锁。变化解析、编码、表投影或错误/限额语义时应更新语义版本；依赖变化仍更新完整锁身份并复验实际输出，不能只看profile标签相同。
4. 由受信main/coordinator/worker执行链认证该声明并绑定真实调用与结果；标签被hash只能绑定声明，不能自证producer真实性。按capability区分parser语义与基础设施身份，不要求T03改未交接的resources.py或盲目替换全局I04 IMPLEMENTATION。正式受控只读执行/typed结果/完整身份认证落地且获准之前，tableDigest机制golden只能标synthetic，不能填上述提案标签后称生产golden。

## 3. 固定S1已有CSV encoding及sheet边界

`source.py`的 `ENCODINGS` 有且仅有以下5个精确词汇，`parse_csv(..., encoding="utf-8-sig")` 为真实默认。broker 8c的CsvEncoding列表和默认与此一致。

| 精确词汇    | 当前行为/选择                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------------- |
| `utf-8-sig` | 默认；直接使用Python3.12相应严格decoder，去除首BOM（若有），无BOM亦可；不是自动编码猜测                 |
| `utf-8`     | 显式选择；相应严格decoder，不能在摘要/adapter中悄改为utf-8-sig；二者对BOM可能有不同字段值               |
| `gb18030`   | 已支持显式选择，既有source测试有该编码的固定输入；非法解码拒绝                                          |
| `big5`      | 已支持显式选择；本轮未运行或扩称新的Big5端到端验收                                                      |
| `utf-16`    | 已支持显式选择；使用该精确Python decoder的既有行为，不据此新增utf-16-le/utf-16-be/任意alias或猜端序能力 |

非枚举词汇触发ENCODING_UNSUPPORTED；非法解码不替换成问号继续导入。这里的“已支持”指固定parser/选择接口已有能力事实，不把全部编码升级为新正式worker/目标平台通过。

- CSV的caller options应显式保存 `format=csv`、实际枚举encoding、`sheet=null`；Table.sheet则固定为 `CSV`，两者不能合并或在重试时替换原请求。编码没有保存在Table字段内，必须另行绑定。用户选非默认编码后不得强制以utf-8-sig运行或只改标签。
- XLSX的caller options为 `format=xlsx`、`encoding=null`、实际选中sheet；Table.sheet为相同真实名字。parser `parse_xlsx`要求非空str且实际存在；broker初选sheet=null仅为inspection，必须真实枚举并configure之后才能预览。broker还有限256 UTF-8字节及NUL拒绝的私有sheet选项限制；这不是parser自身已存在的公共sheet schema。
- digest r1只选择csv/utf-8-sig/null，是**受限新profile**，不等于S1只支持一种encoding。建议canonical在正式CSV接线前将encoding扩为上述5个精确词汇并按实际选项入hash，保持其他Table与转义规则不变；相关tag/version/兼容规则由唯一owner明确。如果先实施utf-8-sig受限profile，必须标明阶段范围，保留其他4个原有显式编码为待接线验收，不能删掉或把受限阶段算完整FR-300。禁止静默转码；用户明确转换将产生不同源bytes/SHA和新预览/确认链。

## 4. r4与proof接口的具体衔接

未发现r4的状态选择与冻结broker必然冲突，但适配器须保留下列顺序，否则会产生具体错误：

- receiving才可按完整descriptor+bytes精确重复；sealed拒所有append、已清理终态只返终态/拒绝，均不影响独立受保护的inspection/preview读消费者。broker的“可再次读取真实文件”不等于旧upload可续传或返旧成功ack；T03不实现传输ack/TTL/pin。
- `readForCommit`必须收到实际WeakMap登记的同scope/代次proof，返回复验快照；它没有lease TTL，也不是一次性人类确认。未admit lease失效后，即使本地旧proof尚可调用，也必须走新预览/新proof绑定/新人类确认；不能据同bytes/planHash复活远端授权。若原operation受理仍unknown，先保持原身份并通过barrier/fence查清；只有已证明原请求未受理且不可能迟到受理，才可由新的真实确认产生新operation，不能只因本地lease失效换operation重放。
- **已有claim的只读对账必须先分流**：认证当前项目读权限并匹配原完整请求/context，不能先总调用readForCommit、要求旧proof对象仍在、旧lease今天有效、当前域base/CAS再次成立或新人类确认；否则关项目/重启或域后续变化后将无法读回真实已受理结果。封存的AdmissionProof是当时证据数据，不可重造/反序列化为新的SourceProof对象或新写授权。
- 首次写受理仍需真实proof复验及最终dispatch guard；复验返回后到实际受理间的revoke/accept先后由coordinator权威排序与事务决定。本地cancel/新generation不证明远端零Job；受理先发生则按原Job/receipt正式取消/对账，不以旧append/release/TTL撤销已受理pin或已提交状态。

r4已明确关闭终态append歧义的设计范围；并未运行其fixture或证明runtime落实。原6项合同、真实producer/完整options摘要、typed worker结果、实际CSV/XLSX→预览确认→Store、配额/TTL/GC/unknown、同候选指定双审/CI/正常merge和父验收全部保留。256attempt/256MiB等已由总控技术采用也不改变这些证据边界。
