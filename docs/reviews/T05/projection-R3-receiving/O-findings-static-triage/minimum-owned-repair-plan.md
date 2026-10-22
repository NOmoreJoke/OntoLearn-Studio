# O 包15意见静态处置与最小修复计划

2026-10-23（上海）。**先收敛O自身的来源、权威消费与私有数据域约束，不机械修改公共契约或历史产品代码。** 本文是给总控的具体写面计划，尚未实施修复、未运行builder/产品或创建新源码候选。15条原finding逐字保存在5168c148收件包，完整矩阵另列原文段hash、限定判断、证据、唯一owner和后继。任何静态反证均不是原指定模型主动改判，最新M仍NotPass；旧Z限定Pass不能沿用。

## 固定证据与当前结果

- 原source O `77852d27a3c4e84867a42f243e0f4e0f32b8df67`；原过程`86df64a2c707355ed177d536ef5975a1986c0f0b`。终态收件父提交`5168c1480a8548217202e134073b507fd77a26ab`。两模型审查树和既有ref不变。
- final-v2为44941B/503行/SHA `9921ffe20f68b1bbf5c7938fa7d45c9b0059cd9c8ed5b0a4afcb5a6e23852df7`。原会话02d新turn completed+同turn stop是真实终态；旧c978 failed/ad UNKNOWN、56586/58279/60824旧稿全部分版保留。
- 覆盖表149唯一path与固定清单精确相等，标签L124/P20/S2/partial3只证明有账。下一**全新同候选双审**须完整阅读PRD原缺1–395/1020–1255、两份allocation guidance全文，并做两锁文件条目级审查；五项范围不能沿用旧“未读/统计”作为完成。大型JSON完整解析与源码逐行阅读仍分列。
- 本轮静态方法只有Git blob/文本/AST literal/stdlib JSON相等与hash。18件owner证据均current=固定source=固定过程；F06另核10件、F12另核16件及I01历史链，范围见两份独立专项报告。不把只读静态计算当运行验证。没有导入builder或读取产品算法生成expected。

## 15项处置摘要

| ID | 限定静态结果 | 具体后继 |
| --- | --- | --- |
| F01 | 每个decoder的list-N重置有跨图潜在域碰撞；闭合当前语料未证实际错误。不能任意扩大BNode域 | W1约束有限fixture角色和不支持合并入口，补边界自测；不发明全局blank ID或修改已定双射规则 |
| F02 | 13 golden→17 observation的交叉核对不完整；test仅覆盖golden[2:11]的报告谓词 | W1建精确分支/字段消费账，补query和选定SHACL政策关系；描述性reason及历史gap不得当安全错误码/当前红项 |
| F03 | explanation金标只pin/read，未参与本O语义交叉核对；作者身份不等于消费证明 | W1区分实际消费与reference-only；已有精确映射才接断言，不增加417外输入或伪造覆盖 |
| F04 | 七值与规范相等；DOC_PINS已能拒规范字节变化，原报告该子断言过强 | W1补规范行↔七值独立关系断言；不import产品allocator，也不称实际Budget已证 |
| F05 | 输入历史来源/expected权威不应互为子集；确有523c历史ref未进26行registry | W1分角色、规范local并保provenance-only lineage；不能读新producer或actual补expected |
| F06 | 288/25是原raw records，不是公共RDFTerm；仍有私有schema分域/专用约束缺口 | W2只改O私有声明及完整raw绑定验证，保原source/None/空串/顺序；不改public schema |
| F07 | next首basis潜在局限，当前scope各一match且所有matches仍完整，未证现有信息丢失 | W2验证闭合单basis域；未来多basis不静默截断，先拒绝等独立合同，不擅改all-proofs语义 |
| F08 | source-identities无早期pin；但更改导致sources变化会被--check发现 | W1加精确身份pin；身份拒绝与生成物比对是两道门 |
| F09 | 26行均有SHA、14行有ref；历史sourcePath不在HEAD不是本身错误 | W1明确历史地址/当前副本/规范authority角色；缺ref不猜、不用同名文件替代 |
| F10 | 固定417未证越界；未知索引必须fail-closed，不应造pending成功 | W2明确定界/ValueError及无部分产物负例，不扩417 |
| F11 | recorder已记executable，缺版本记录；旧3.9运行非3.12产品证据 | W3补版本和白名单运行元数据，旧流不重写，不做无变化解释器对照 |
| F12 | I01脚本旧wire与v2失配成立，实际51–69且UUID先拒；现行已核执行链无调用 | W3只记历史适用与现行入口，保脚本/149账；若root给当前必须执行需求，再另指唯一维护者新候选适配 |
| F13 | running/rounds先守卫、state未改名，仅证据版本+1；未证绕过取消状态边 | 无T05产品写面；根若确认合同问题，唯一路由T01，不直接改JobStore/states |
| F14 | raw Conflict存在，但已核出口只取安全code/params与opaque detail；未证跨界泄露 | 无T05写面；必要hardening由根路由唯一T01，不能新增原值日志或为假想caller扩大修复 |
| F15 | Darwin采样非硬限已显式声明；父侧确有Darwin RSS兜底，原报告反述错误 | 保报告纠错与平台限制，不改native/内存保护，不重开OS/SQLite/wholeH研究 |

原严重度汇总5/5/5错误，标题实际6中/4低中/3低/2低信息，原文保全；F02原新均9/13，owner曾误读旧8条未覆盖observation已更正。上述结果只用于安排必要修复，不抹去任何原意见，不自行降低NotPass或外审阻断。

## 拟实施的精确写面

**唯一实施owner：本T05 O线。** W1/W2/W3只在本owner分支后继新提交；不改原固定ref、两审树、G包sealed输入或其他线源码。计划写面为：

1. `scripts/build-i05-source-package-oracle.py`：来源角色/consumption ledger、本地身份规范化/缺证明确、source-identities pin、raw与规范term独立路径约束、闭合scope/索引的fail-closed边界。
2. `scripts/test-i05-source-package-oracle.py`：13→17关系断言、字段消费覆盖、七值规范行绑定、raw完整关系与负例、未知源/重复身份/歧义scope/非法索引等确切失败边界。预期来自固定规范、已独立golden和sealed input，不复制被测函数输出当预期。
3. `docs/reviews/T05/source-package-oracle/record-command.py`：只增加新运行的`sys.version`/`version_info`/实际executable和必要白名单env记录，继续独立stdout/stderr/exit/hash。无全env、凭据或旧记录改写。
4. `docs/iterations/T05/source-package-oracle/field-policies.md`：实际消费与reference-only、raw私有域、闭合fixture语法、历史脚本适用性、未完成父门的具体口径。已冻结guidance/raw/AGENTS/旧报告不改。
5. 正常generator的五个自有输出 `tests/fixtures/quality/i05-source-package-oracle/{oracle,coverage,sources,schema,budget-gaps}.json` 只接实际重建delta。预计主要是oracle builderSha/私有域声明/权威分支元数据、sources角色与lineage、schema私有说明；coverage/budget-gaps如字节未变不提交假delta。
6. 现有recorder默认记录根 `docs/reviews/T05/source-package-oracle/commands/` 仅新增本候选 `o15-owned-candidate-<action>-<attempt>/` tag（action仅build/test/check，首次attempt为01，必要复测递增保首失败）。具体首轮三目录为 `o15-owned-candidate-build-01/`、`o15-owned-candidate-test-01/`、`o15-owned-candidate-check-01/`。这是拟授权新增写面，旧tag与原流一律不改；recorder仍用现有默认落点，不假装它会自动写新candidate目录。
7. 新过程目录`docs/reviews/T05/projection-R3-receiving/O-owned-repair-candidate/`（拟新增）：原/新SHA清单、最小diff、逐finding处置、上述commands新tag流的精确链接/bytes/hash、首失败、独审与指定新审输入/回执；非recorder的获准完整检查日志另存在此目录。此为新写面，先交root核定；本计划不先写执行成功记录。

**明确排除的共享修改**：`packages/contracts/v2/schema.json`/states/errors/registry，JobStore、storage、coordinator、memory_guard、verify-i01历史脚本、npm/CI/依赖锁、产品源、probe/actual/collector/JSONL adapter/最终比较器、原417/320输入和旧金标、原两审tree。F12历史说明写O自有文档即可，不改共享工具。F13/F14若后续确证问题由root转T01，F15留既有I04资源owner；本T05无权跨线补修。

## 三个可复核的修复批次

### W1：来源、独立expected消费与规范绑定

- source registry把“本地固定副本身份”“输入origin lineage”“独立expected authority”“规范/接口说明”分开，不要求两来源表任意互为子集。已有origin literal只从sealed资产读取作provenance-only，保111条唯一带pointer origin记录/已有ref/path/SHA，去重仅用明确身份，不删除引用。缺原件或授权仍标未核，不读取semantic_probe等producer算法。
- source-identities加入精确pin，所有实际读取的authority都可由受控local解析到对应pin；路径归一到本evidence域并拒越界、歧义/重复冲突。历史path是origin，不尝试用本HEAD同名件伪装历史字节。
- C golden逐case映射到17观察，明确date四政策和illtyped两分支。query行、SHACL完整行、conforms/components/valueNodeCount等只核其确实适用字段；英文解释reason/derivation、旧currentEntryGap和entryAndReport分层是元说明，逐项记录消费或未消费，不假装与安全错误码完全相等。没有独立exact字段依据的仍保原pending，不从actual或旧红数猜值。
- explanation金标保原件及pin；精确同输入/同语义分支才断言。超出当前417映射的条款记录reference-only并给原因，不把“文件留在目录”写成已消费，也不移除文件隐去缺口。
- 七池与两段精确固定规范关系明确验证（input/output别名必须显式），任一常量变动而规范不变应失败；DOC pin原有身份门保留。fixture列表支持只在批准角色，未获准跨图blank情形fail-closed，不增加通用RDF支持。

### W2：私有数据域及有限输入拒绝

- 私有schema分别声明canonical RDFTerm与RawTermSourceOccurrence五键形状、类型、path作用域；raw在现有25数组上逐项绑定sealed records，包含multiplicity/末项/顺序/source null或空串/language原写法。标准身份的simple/string或语言casefold仅作用于身份，不重写raw。
- scope事实与matching heads/whenBasis做完整关系核查，当前三观察维持同一业务expected；出现多独立basis时不得静默next截尾，明确拒绝并等待独立范围决定，不先添加all-proofs业务承诺。
- 不在固定family索引集合的值明确ValueError，旧合法值输出不变；拒绝发生在写任何产物前，不把非法输入变成合法pending observation。对完整raw/source/尾项的mutations须有确定的失败断言。

### W3：记录与适用范围

- 新运行记录真实Python解释器路径及版本，不重跑无变化旧3.9/3.12对照。产品所需3.12与外部stdlib工具适用版本分列，不称3.9提供产品验收。
- I01原脚本仅保历史原件、固定适用ref和当前手动执行限制，指向现有I04验证入口。现行执行需求若后来明确，root另给唯一维护者做新候选；不加v1兼容口、不删149项。

## 验证、冻结与重新指定双审

实施前先固定新过程写面与基线，保原15finding/所有旧流/失败和137 pending、26声明缺件。按需记录每项首失败，不能用最终绿覆盖最初失败。当前本次交付只有静态triage，没有实现或运行通过。

实施后以新候选运行O实际两门：`python3 -B scripts/test-i05-source-package-oracle.py`、`python3 -B scripts/build-i05-source-package-oracle.py --check`；生成字节由明确的一次正常build产生，独立保argv/cwd/env白名单/解释器/exit/stdout/stderr/前后hash。此前原审查只准两命令的边界不暗中扩大；新实现阶段由root按现行AGENTS核定必要完整`npm run check`等对应验证及隔离资源，不能以本计划或O单测替代仓库代码变更所需检查。仅自有文档检查不格式化归档原件。

验收需同时检查：417 IDs及原顺序/320输入/原golden字节不变；原business expected与参数/contexts无非必要delta；280/137、26缺件和false whole不得被人为刷成全绿（如果发现真实错误必须逐项报root，不能硬保错误数字）；metadata-only语义字段的新旧delta明列；不新增actual-derived expected/私定scope默认/未批BlankNode域。两份旧审查树290+11冻结输入继续保原件，未知额外路径仍只stat、unknown。

所有必要修复与独立复核通过后才冻结新SHA和真实最小diff。**ZCode/GLM-5.3最高思考与MiniMax/M3.1-Flash/xhigh须全新任务、同一新候选、各自独立review tree/完整原输入，完整工程覆盖不缩到补丁。** 两模型均须补前述五项静态缺口、保全部历史意见逐条采纳/拒绝/未决及理由，分别给静态/运行/包内/生产/父门边界。旧Z Pass、当前M completed或本次triage均不可替代新同版判断。root另协调GUI；本方不因本文创建模型任务、Goal或推送合并。
