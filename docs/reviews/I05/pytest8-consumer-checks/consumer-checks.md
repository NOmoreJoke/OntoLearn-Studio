# I05 固定源码消费与实际检查

当前尚未得到完整检查通过。canonical 已冻结为 `23352bacb500088367f849e53980e97c937724b3`，过程提交 `513db0056f312342a6791e2d4c7842f3726581f2`；probe 已更新22行中的 semantic 实际身份，并将固定输入的来源与运行源码身份分开。

`ASSET_SUPPLIER_REF` 保持封存输入的 `6891a5842302859a531cf82767c5a482417bc274`。`SOURCE_REF` 为当前 canonical 23352，`PROCESS_REF` 为513db。输入 manifest 的整个 versions 对象仍作严格比较，不接受任意 supplierRef；运行 header 和材料的源码身份继续指向23352。原两份输入 JSON、417项业务预期与320个数据集均未改。

## 已实际运行

| 检查               | 实际结果与边界                                                                                                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| fullcheck-01       | `npm run check` exit1；ESLint通过，Prettier在3个既有冻结/历史文件停止。后续类型、vitest、构建、Ruff与pytest未被该链运行。                                                                |
| engine-check-01    | 单独 `npm run engine:check` exit1；Ruff在5个路径报319项，格式和pytest未被该链运行。当前semantic/probe/test三个路径未报错。                                                               |
| full-pytest-01     | 单独完整pytest：1179 collected，1136 passed，12 failed，31 errors，58.20秒。新的运行引用引出输入身份耦合；31个error均包含ASSET_VERSION_INVALID，不能将12个failed未经重测一概宣告已修复。 |
| asset-ref-red-01   | 新隔离身份回归在修复前实际setup error，保留原始流。                                                                                                                                      |
| asset-ref-green-01 | 最小身份分离后，新回归及4项原有extra-key案例实际5 passed；不能替代完整pytest。                                                                                                           |
| active lint/format | 身份分离后三个活动源码实际Ruff check与format check均exit0。                                                                                                                              |

定向新回归保持当前SOURCE_REF可以不同于封存来源，同时篡改输入supplierRef仍严格拒绝。独立复核对该修复给出有限范围通过；旧 pin-refresh 静态审查没有发现后续语义耦合，其旧报告仍原样保留。检查命令、时段、退出码、分流原字节和SHA见本目录对应JSON；完整pytest JUnit在本树 `build/i05-pytest8/full-pytest-01.junit.xml`，身份见实际收据。

## 工具链接收

活动生成器由原owner在独立树整理，固定提交 `954f38fe643c4903e5819d469e6de2c56f666374`。本树已接收唯一产品generator及77份本线证据，78路径精确匹配固定提交。供方旧/新生成器各在自己的detached513副本默认运行一次，均exit0，两件运行输入逐字节等于原黄金；仅新审计manifest中的generator自身身份随真实源码变化。前审、实施/黄金复核及最终归档补审报告均已全文读取。主线没有为接收重复运行生成器。

Ruff的4个冻结checker及Prettier的3个字面路径例外由T01唯一配置owner供应；活动generator未列入例外。待精确配置提交接收并核范围后，执行一次必要完整check。已知失败链不反复重跑。接收身份与原文件保护见 `generator-supplier-reception.json`；冻结checker/活动generator逐路径规则清单见 `toolchain-debt-exact-inventory.json`。

此阶段没有新的源码/打包CLI比较、实际frozen来源验证、native或生产验收。私有provenance当前只有固定合同与接口准备，原frozen拒绝仍保留；真实reader/build/entrypoint由T03供给后另行消费。

## 第二次完整检查

T01 `a909afc369c143071025a55bc788abde0b9f40f5` 两配置已逐字接收。fullcheck-02 实际 exit1 / 20.662秒，绑定的12个源码/配置/锁身份运行前后全部不变。ESLint、Prettier、类型检查、15个Vitest文件630项测试、静态生产构建及Ruff lint通过；首次进入Ruff format后，唯一新诊断为冻结历史报告 `docs/reviews/I05/active-source-hygiene/lifecycle-review-r1/report.md` 的Python代码块空行，220文件已符合格式。pytest未在该链执行。

该报告全文已读，10951B / `e8687d8bf11800723b7269d3da1106b559811feef95deec3c23a2a3f8482b3a7`，current逐字等于fixed513db。报告未改；精确单路径format例外交唯一T01供应。一次发给总控的手录身份错误已立即明确作废并纠正，唯本处与实际诊断JSON身份有效。

为核验身份修复后的实际语义结果，在既有controlled完整pytest授权内单独启动full-pytest-02，保原测试选择、独占basetemp、JUnit及原始分流。此为修复后的首个完整pytest；不把启动或格式例外当运行通过。

full-pytest-02 已自然结束：1180 collected、1176 passed、4 failed、0 errors、0 skips，pytest摘要270.97秒，launcher271.556872秒，12项源码/配置绑定前后未变。4个失败中3项由shared full-v1的期限触发产生，另1项是header测试仍断言旧supplier/process身份。真实shared已218项observations、199项未开始，首失败fullview/profile-76、restore/result、COLLECTION_DEADLINE，elapsed121.103670秒。原turtle/front-5、dag/fullview/restore负例已越过原故障点；不能把未开始199项记为通过。

JUnit明确证明原真实producer故障节点、两项bad-bytes节点和B1 selector节点本轮通过。实际源码/包CLI、fresh-process、物理测量或全量417项通过不由这些节点推出。两份实际JSONL及JUnit无损保存在仓库外 `outputs/20261023_i05_full_pytest_02_preservation/manifest.json` 指向的位置；本树原build文件保留。

当前只做已有流的独立静态归因，不延长120秒或64MiB固定条件、不删case、不改变业务预期。该时段与T01另一Python检查重叠只作事实记录，不证明慢的原因。实际header中mathInputContexts为83条、82 eligibleStandaloneMathInput=true、1false；旧压缩历史概括不能用于这个域，不能据旧数减少调用。

单MD配置 `ada38a625282c1bd60be45f96def3ba81b79728e`（parent a909）已精确接收：仅pyproject新增完整历史报告format literal，配置1527B/74763669…；5033B/d1082771…独审全文已读。主树随后有限整树 `uv run --frozen ruff format --check .` 实际exit0，220文件已符合格式，历史报告原字节保持。

header测试已按独立前审的候选同步两个固定runtime ref，并新增输入provenance仍6891断言：当前76628B/d7947f3e…，Ruff check/format均0。以保存真实JSONL只提取原3个纯函数重放断言，before失败、实际应用后通过；不称为重跑pytest或完整采集通过。单次原full_run的受控验证方案已独审，等总控内部确认已管理Python重检查不并发；本线尚未启动该次调用。T03四产品也留待其自然终态后整合，避免改变归因样本。

## 单次受控采集与后继来源

获总控管理范围串行窗后，isolated-full-run-01只执行原一个节点一次，19:15:22.765597至19:17:32.017287 UTC自然exit1，没有追加重试。原417/120秒/64MiB均保持。实际383条JSONL记录包括381项observation及header/terminal，36项未开始；381项的状态为217 observed-return、162 observed-rejection、1 not-executed、1 unexpected-failure，不能将它们统称语义通过。首边界为utc-date/public-budget-43460 / semantic.validate_shacl_text / shacl-text/validate / COLLECTION_DEADLINE；最后一次调用返回后触合作检查，terminal127.175700秒，不是OS在120秒强杀。

实际运行HEAD是513db加已记录的未提交源码；结束后才将5个产品改动精确固定为553a63ce700477e288be895b33269b1d5ecbdc0f，作为计数器方案前像。运行收据记录40个beforeFiles与作者计算的前后不变布尔声明，没有独立完整afterFiles明细；独审结束后另于19:19:38逐件物理读回40项，38件与fixed553 Git相符，AGENTS为政策overlay、venv配置为非Git环境域。不将这些事实写成root亲历逐件前后监测。

新JSONL46185358B/169f9223…的原行、完整381+36有序列表、确定性gzip及精确解压核验见仓库外 outputs/20261023_i05_isolated_full_run_01_preservation/manifest.json。T01/T03已管理重检查当时暂停，其他模型/backend及host负载未知；这一次更后停止不证明并发因果、性能提升或稳定容量。CPU窗已释放。

在本次自然终态后，按固定105213B/7bffd8…限定patch先apply--check再应用，精确接收T03的4产品；提交a633ef391344cce60807638ecd942d4e2183c7b4仅含这4项。随后4bb99d99620811766df38d7e29346e3174f82c8c只补入reader CONTRACT_SOURCE实际指向、原树缺失的36587B/9d97固定合同doc。最新完整源码为4bb，23352继续只作canonical22来源域。四路径及合同身份、11项保护面和空暂存区已独立静态复核，未重审或执行产品，不把Git接收当runtime通过。

计数器仍是原2996 probe中的sys.setprofile方案，frozen consumer原拒绝也保留。选择性monitoring当前只是基于官方Python3.12 API的纯设计：两个同步code入口与线程域可设计，但空tool名字不证明无残留callback/local配置，严格准入仍未证。独立设计审查中，不以caller自报clean位或放宽条件求绿。当前未执行prepare、包构建、实际frozen loader/native或source/package CLI。

工程边界后续已澄清：不要求对任意已释放监控槽的全部未知状态作只读完备证明，也不把瞬时callback交换转为新用户政策题。新的合作式提案将保留当前线程两个真实入口计数、拒绝现有profile或已占工具ID，明确有限交换检测/立即恢复并拒绝、只清理本实例确获确改资源及失败完整性；未知其他code-local状态不遍历、不清除，不使用global restart、换ID或caller洁净位。旧11051B纯设计作为历史前像保留，具体新源码提案与有限unit计划另行固定、独立审查后再按总控执行票实施；当前仍未调用monitoring API或改变计数器。

## 合作式计数器固定提案与复核

cooperative-v1 固定为11成员 manifest `3faae250576dafa862e506735f56bb4bd164e70ba867f454c23953d5c3cc95f3`。主审完整读回并核两精确未应用patch、主树4bb前像、类外AST范围及静态38case选择。独审对计数器主体给Limited Static Pass，对完整测试包给Request Changes：F1真实API测试交换后直接断言旧callback为空，失败清理可能抹掉原对象或未改状态；F2释放名字后的断言失败会跳过自身残留清理。独审报告10234B/fa272eee…原样保留，没有运行缺陷测试。

cooperative-v2 另固定14成员 manifest `bfad0bf97532b311e5e95a96cb0af45f51d90da6bcd95d89e5aa5b053cfe663f`。计数器主体、完整probe候选及probe patch与v1逐字节相同；tests候选99627B/7f030189…，只新增测试专用lease并替换两处真实测试。lease保存成功交换的真实旧对象，旧非None即恢复并拒绝；前置失败只释放本方名字。待恢复改动跨release保留，finally仅在实际free槽重申请清理自己的残留，遇active owner或counter quarantine不接管；恢复不确定保留reservation并失败。

同一独立agent复核v2，报告5883B/450d6c9b…、独审manifest `d5e8592bdbd5188c3ab8cddad2c7ffdd04a306ce3b4199ac3f8db1867135f83d` 已主审完整读回及核hash。F1/F2静态关闭，无新增阻断，结论仅Limited Static Pass。文档准确区分setup KBI成功回滚保留原类，以及callback KBI当场传播后exit可转私有完整性失败；scopeStages保留故障前部分诊断，top-level callCounts=None/terminal failed不表示各层计数完整可靠。

新增21函数/34参数case，加原四函数静态预计25函数/38case。精确选择含--maxfail=1、禁止xdist，不依赖full_run/B1模块fixture；其中一个真实worker thread仅验证owner过滤，invalid-entry在首个业务dispatch前拒绝。尚未collect-only、调用API、启动线程、运行pytest或应用产品补丁。已把固定件、正式独审和具体两路径实施/定向格式检查/单次38case计划交总控独立接收，等待既定具体票；当前仍NotPass，不重跑旧full417。

v1共16件与v2共19件的确定性gzip归档和逐件解压原字节核验分别在counter-monitoring-cooperative-v1、counter-monitoring-cooperative-v2目录；原件仍在仓库外outputs。原v1缺陷及报告不改写，过程证据仍未提交。

共享8.3维护权已按总控请求明示：仅packages/contracts/src/index.ts与apps/desktop/src/preload/index.ts的未来维护释放给T01。两者在4bb实际字节分别为4881B/e105ebcf…与1230B/727e1ff1…，逐路径status为空且workingEqualsHEAD；本线无未提交或拟修改。保留已冻候选旧字节，不扩转其他源码、锁、入口或GUI权限。

## 计数器实际实施与有限运行

总控已直接逐项接收v2，并发固定实施票3831B/58e100ba…，仅授权当前4bb两产品patch、定向Ruff和唯一38case进程。01 launcher由本方把保护清单的generator路径手录为不存在的scripts/generate-semantic-probe-inputs.py，真实固定路径为scripts/generate-i05-source-package-inputs.py。失败发生在任何child之前，commands为空、actualPytestRun=false，两产品未改；原receipt、launcher与错误补记保留。此launcher traceback只在工具transport输出留存，不冒充另有原始双流文件。总控明确允许更正这次未进入产品的前置拼写错误并继续同一未消费票，不改原票；不是产品失败重试。

02 launcher静态比对仅更正一个保护路径、使用独立02证据目录及补充异常采证后执行。原票载pytest argv/basetemp未变。git apply --check、apply、own Ruff format、Ruff check及format --check全部exit0，格式前后AST逐项相同。唯一pytest PID89371于2026-10-22T20:01:12.738160Z至20:01:13.826673Z实际exit0，162collected、124deselected、38selected，38passed，pytest摘要0.67秒，launcher1.088524秒。该时间只描述本次有限命令，不能量化产品收益。

实施收据22477B/10380080…包含6命令原argv/cwd/解释器/overlay/PID/UTC/exit、12份原始双流与前后身份；各流已读回核hash。JUnit6607B/3da06ca0…实际38testcase，无failure/error/skip。14项保护面逐件前后不变，包含AGENTS overlay、T03四品/合同、锁/配置、generator及两已释放共享路径。格式后probe109443B/63a6b4a6…、test99672B/0185e7b0…，测试后原字节不变；尚待实施后独立实际delta审，再精确两产品冻结。

此有限结果只证明本次选定unit，未重跑full417/fullpytest/npm check，未做产品打包、真实frozen reader/native、source/package CLI或benchmark；原120/64MiB/417及完整工程NotPass保持，frozen guard尚未接入。原01手误与v1 Request Changes不改写。总控后继仅授权private consumer guard的最小未应用patch和有限计划纯准备/独审，未授consumer apply/import或其他运行。

实施后独立actual审已完成：6751B/1651d120…报告全文读回，2成员manifest6caa1b62…逐件核符。两文件与批准v2 AST同义，真实38名单和顺序与静态参数展开精确一致；6命令/12双流及outer stream、14保护面均核符。结论仅本次两路径与有限gate通过，异常fault-double不冒充真实audit/OOM全态证据。

随后精确冻结counter候选 `ae118d2a2b4fe267991522cbcc457d7d33f7ce8b`（parent4bb），只含probe/test两产品；实际cached--check为0、暂存名称及commit名称均exact2、index空，AGENTS未stage、未push。完整源码候选与canonical22来源23352、过程513和封存输入6891分别记域；本次不改它们求绿。后继本方过程提交只归档证据，不宣告整体通过。
