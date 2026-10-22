# T11 双报告静态 triage 与最小修复计划

2026-10-23。依据原产品 `7d28fdb27c0aac39ed7df1f9fd5fa0f127b5d9f4`、两方已完成原报告及明确的总控决定。**M 的 NotPass、高/中/低严重度及 Z 的原 P4 全部保留；18项没有一项在本轮关闭。** 本轮只做静态分析与计划，无代码改动、产品测试、GUI或新审查任务。Q5待人答不阻塞这些本线问题的分析。

完整逐项证据、原级别、关联与拟验证在 [matrix.json](matrix.json)，来源字节在 [evidence-index.json](evidence-index.json)。新报告不覆盖原件；原报告中的事实或解释偏差作为owner核对结果分列，不自动改判。

## 18 项完整矩阵

| 原项/级别 | 静态核对结果                                                                                                                     | 最小处置包与关联                                       |
| --------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| M-F-A 高  | 六层非空全局应用与仅G.6文档有冲突；注释表达G.6意图但不是可验证场景。模板负向check已存在，不能把模板要求误变为restoreCurrent=true | W1：拆通用结构/G.6专项，显式case与独立pin              |
| M-F-B 中  | 硬编码与freeze缺endpoint/requestedModel绑定成立；“无批准依据”不准确，根决定已有DeepSeek首选，但材料未交给审者                    | W2：固化出处、独立pin实际服务元组；不接API/网关        |
| M-F-C 中  | 生产只逐项核baseline列出的文件；17全集/版本未显式约束。合法独立manifest SHA已间接绑定全集，改freeze是假设改变信任输入            | W2：批准profile、17路径和版本显式核验，保持唯一T09内容 |
| M-F-D 低  | PRD12.1第8步已含迁移完成，不能断言代码无依据加严；独立迁移成功必须另记                                                           | W1：保八步闭环，明确字段/矛盾拒绝，独立成功另统计      |
| M-F-E 低  | flag/默认3skip早已明确，历史“最终检查”仍可能读作默认状态                                                                         | W6：以命令/日期/候选写证据，不写措辞镜像测试           |
| M-F-F 低  | 回退留新数据副本、拒开新格式没有各自强制check                                                                                    | W5：补具名check及独立预期，不写第二恢复器              |
| M-F-G 低  | 同意/分段/示范记录只hash不解析，属于已声明外部原件核验                                                                           | W6：明确谁核哪些原件，不加无证明力布尔冒充真实性       |
| M-F-H 低  | 三子项：半成品、组件来源、PE越界；仅在解包根内不证明同安装包                                                                     | W4/W5；半成品=Z-F6，PE=Z-F5；来源单独保留              |
| M-F-I 低  | PE/koly与valid声明不等于签名链/安装器实质证明，已有原则边界但可更具体                                                            | W6；关联F-H来源与Z-F2文件处理，非同一缺陷              |
| M-F-J 低  | now取本地墙钟，覆盖freeze.now但不认证时钟正确                                                                                    | W6：注明时间信任来源/偏差，保CLI当前时间不可被任意覆盖 |
| M-F-K 低  | 多代current/active文本并存、部分已有历史标签；同updatedAt不同hash不能擅归同快照                                                  | W6：绝对日期/commit/取代关系，原JSON/外部state不追改   |
| M-F-L 中  | 总括“失败原件保留”强于首38仅摘录/transcript事实                                                                                  | W6：精确说明首缺口、其后原件和归档；不写永久丢失       |
| Z-F1 P4   | 重复safeParse成立；不是整个if不可达，finite(now)仍应保留                                                                         | W3：删重复解析，沿用行为回归                           |
| Z-F2 P4   | readBound、large/format均有stat/open或path/fd竞争；CLI也是先整读后限额                                                           | W3：同fd/fstat/有界读取；SHA不能消除先耗资源           |
| Z-F3 P4   | fail不停止循环，dest缺失分支可达；现有前置错误使最终不一致，未证虚假放行                                                         | W3：显式目标错误并停止该项绑定                         |
| Z-F4 P4   | Mac目标判断和采集有PATH依赖                                                                                                      | W4：已知系统命令绝对路径，包括OS/arch门                |
| Z-F5 P4   | DOS header/e_lfanew未先界限检查，流异常fail-closed不等于受控失败                                                                 | W4，与M-F-H③共修；Windows真实运行仍待验                |
| Z-F6 P4   | 先建目录后采集会留下半成品，标记不足                                                                                             | W4/W5，与M-F-H①共修；保失败原件、不自动清理            |

独立子任务另静态复核Z六项及M-F-H/I，纠正了“F3严格不可达”和“F2只影响readBound”两处解释，见 [collector-and-io-independent-analysis.md](collector-and-io-independent-analysis.md)。这不改变原级别或M NotPass。

## W1：比较场景与用户统计

建议把T11证据比较升级到明确新版本（拟 `t11-comparison-v3`），不静默接受/转换旧v2；这只是本线审计投影，不改T01/T10项目格式或业务UI。通用结构仍强制身份、版本、完整payload、唯一id、selection/dependencies及三能力一致，但允许合法空集合；G.6专项断言另核六必需层非空。

为避免声明`current-state`绕过G.6，投影明确 `comparisonCase`，独立freeze pin恢复场景及两迁移场景，前后必须同case。**正式双向迁移的case固定为G.6人工冲突场景，不由manifest自由降级；恢复可按实际冻结用例选择通用或G.6，原崩溃/未提交/来源/撤销/人工冲突checks一个不删。** 两方向G.6仍各需完整六层、实际重关联/冲突/继续编辑/撤销及完整预期。通用恢复不能代替这两项G.6。模板仍只进入`template-not-restorable`负向报告，不能标恢复成功；不新增模板导入器。 字段建议固定为投影`comparisonCase: current-state | g6-conflict`、freeze的`recoveryComparisonCase`及`migrationComparisonCases`；正式两迁移槽的值必须是g6-conflict，缺失/未知/前后不符均拒绝。空数组仍须作为被携带的完整层存在并匹配独立源快照pin，不能把缺字段或丢数据解释为空项目。

80%按原PRD完整闭环核对：11.2第772行要求核心案例，12.1第809行明确第8步包括最小迁移任务。故保留`coreCompleted && transferCompleted`及independent/product-hints辅助限制，不能把仅前7步计成功；明确core字段涵盖8步，并对core=true/transfer=false给专门矛盾错误。FR-105第303行要求操作完成与独立迁移成功分记，11.2第774–775行继续要求修复/断言推导辨别及Agent代做反例；独立成功按transferIndependent与实际辅助记录另统计，不要求其与操作完成恒等，不虚构迁移百分比门。M-F-D的“偏严”推论未被这组条款证实，字段/统计说明仍需修，原意见和级别保持待新审处置。

拟改：`scripts/release/verify.ts`、`tests/unit/t11-release.test.ts`、`tests/fixtures/release/comparison.json`、本线README/selection-comparison/migration/user-study/acceptance。新增回归须同时覆盖通用空层、G.6六层逐一缺失、case降级/前后漂移、所有选择泄漏、零轮可重放、模板拒恢复、4/5与3/5完整八步边界、core/transfer矛盾及迁移辅助反例；不只改测试名或删拒绝例。

## W2：服务与批准基线绑定

把已存在的总控Q9决定作为有日期/哈希的引用收入新候选审查材料；它证明选择来源，不证明服务可用或API已验。服务endpoint/requestedModel采用经过URL/文本约束的字段，并在独立freeze新增相应pin；缺pin、manifest单边漂移均拒绝。freeze不得从待验清单生成。其他服务仍须原批准/评估与新候选门禁，不因字段可表示便自动支持；唯一网关不变，无API消费。

本轮T09 profile按已批准873 manifest SHA、`prd-v0.6-learning-1`及17路径集合明确约束。继续从唯一manifest读取每个内容hash，不复制17份内容/预期另造产品基线；未批manifest/版本/缺项/多项明确拒绝。未来新T09版本走显式profile更新及同版新审，不接受不明freeze替换批准范围。

拟改仅verify.ts、T11专项fixture/freeze构造、README/acceptance和新引用记录。测缺/多/改版本、缩水baseline即使测试同时改两边pin仍拒绝；原固定873全文件及50完整oracle不变。

## W3：受控文件读取与小型防御修正

在本线核验器内共用受控打开、fstat、同一fd的有界读取/流式hash/安装结构检查；CLI的manifest/freeze读取也复用边界，避免先整文件进内存再限额。大小增长、非普通文件、短读/异常均受控失败并关闭自有fd，路径与hash规则保留。平台可用的无跟随/非阻塞打开能力以实际实现/验证为准；**仅加fstat不等于解决祖先目录替换，受控取证目录不得由不可信方并发修改仍是明确条件，不能宣称所有TOCTOU消除。** 不为此引入新native caller、压力实验或SQLite损坏研究。

删除第二次expected schema解析，保finite(now)；迁移dest缺失显式fail并停止该项绑定，不用undefined略过资产pin。拟改verify.ts/verify-release.mjs，必要新增`tests/unit/t11-release-io.test.ts`，用小文件、确定性fs替换/增长与异常模拟验证可观察拒绝边界，不做无关性能量化或函数调用次数镜像测试。

## W4/W5：collector与恢复证据

Mac已知系统命令改绝对路径，覆盖最前的OS/arch门。Windows先核DOS header最小长度、PE签名读取长度、`offset <= length-6`，错误固定且不回显原异常。必要时将PE读取纯函数移到本线`pe-machine.ps1`，便于获批Windows以原生PowerShell、无新Pester依赖做小文件表驱动测试；不修改共享npm/CI配置。

两collector开始即记录pending/step，成功末尾写明确complete，失败写有限failed/step/退出状态；失败原件不删除、不覆盖，重跑仍需新目录。marker只证明采集流程结束，不能代表原生/签名/发布通过。新增具名`collector-complete`、`installed-components-match-package`证据check，以及回退`rollback-retain-new-version-copy`、`rollback-refuse-incompatible-format`两项；独立expected要包含相关安装资产/组件hash及完整状态，缺项或actual不符拒绝。

Installer/AppExe/EngineExe来源不能靠同目录证明。T11可以先补显式证据要求与“未绑定则未验证”说明；真实安装/解包结果与T03唯一包内清单就绪后再对照，同包证明未落实不得关闭F-H②。**这个外部接口只限制真实包来源验证，不冻结PE/路径/标记/核验器自身的修复。** 不造第二builder、签名器或项目迁移器，不接管T03配置。

验证分开：本地Mac脚本仅bash-n/静态；真实Mac15与Windows11的成功、首步/中途失败、无complete、防覆盖及PE边界须在获批目标环境执行。单测/替身不算collector真实运行。无目标设备时准确留未验，不能删Windows或以默认skip关门。

## W6：文档与信任边界

同步README、user-study、migration、acceptance与当前status：明确签名链/安装器实质格式、同意/逐段/示范计数、组件来源、墙钟信任的外部原件核验责任。CLI仍覆盖freeze.now，不提供任意生产`--now`规避时间门。首38缺完整raw与其后原件分列；当前状态用日期、commit及取代关系，旧原生终态/报告/JSON回执/hash原样保留，外部state和Goal不改。

历史双值不靠批量替换消除；同updatedAt的不同source hash只登记各自观察，不编造观察时刻或把两份当同一原件。现有默认3skip/显式flag已有正文，补精确引用即可，不增加只验证措辞的测试。

## 执行顺序、验证和 fresh 双审

1. W1/W2/W3/W4按本线唯一作者实施、合并一个新候选；共享verify.ts避免多人并写。W5补check与fixture，W6同步同一语义。当前只是计划，没有开始修改。
2. 先新专项与IO定向回归，再显式`T11_FIXED_BASELINE_PROBE=1 npx vitest run tests/unit/t11-*.test.ts`、`T11_FIXED_BASELINE_PROBE=1 npm run check`、显式release lint/format、`bash -n`与差异检查。source归档未改不机械跑sources；一旦改归档则按AGENTS补verify:sources。检查可能产生自身metadata格式失败时保原件/exit，不删ignore再宣称完整通过。计数按真实新结果，不预填65/695。
3. 涉及collector的目标运行、实际组件来源，以及所有父P0/双平台/签名/模型/真人/CI/远端门仍各按真实票和资源完成；本次不申请额外硬件/API/费用，不benchmark，不更改57P0或1000轮/每轮1000动作。
4. 新代码/测试/验收/证据格式变化后冻结新SHA，准备两棵新的独立review树/环境、实际设置收据、全部原工程及新增变更、18项历史处置与失败原件；不复用已completed任务继续审新候选。Z/M各全新完整同版任务，真实终态/全文/全部意见处理，之后才有原CI/合并门。
5. 新派发明确：**只读本轮自己的receipt；禁止读本轮peer的prompt/receipt/report/state/metadata，即使文件列在本树Git或索引；不得展开peer当前提示来做scope等价。** scope等价由owner事前核；指定归档的上一轮两报告及18项矩阵作为历史允许读，不混淆当前独立性。321正文/322含空尾等口径按实际新字节采证，不沿用旧计数。现Z过程限制原样保留，不杜撰peer泄露或声称绝对合规。

**闭合标准：**逐项有改动或明确证据边界、对应验证及新审者处置；owner静态分类/本计划通过都不关闭M NotPass或任何原发布门。Q5人类答复与真实资源另行等待，工具自身工作可以按本线授权推进。
