# D0 提交后独立完整审查：NEEDS_CHANGE

2026-10-22。fresh reviewer `/root/i05_d0_independent_review`。**固定候选存在 F1/P2、F2/P2 与 F3/P3；D0 当前不能作为完整可消费协议收口。** A1–A4/N-01 的核心分域设计已实际写出，且清单/保护范围一致；有限文档自检通过不关闭下面两个表示缺口。没有产品、build、loader、实际运行或正式验收结论。

## 固定范围与证据身份

- 树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-i05-semantic-offer-owner-review`，branch `docs/T03-i05-semantic-offer-owner-review`。
- base `bba31be7384a676e54cb3b64e219f14bf2a9460e`；实际提交后 candidate `76c774ec7612998cdcb1079deff5c988c15053e6`。没有审未来未提交修复。
- 新两目录的28 payload合990350B；candidate-manifest自身6138B/SHA256 `3249765fad350e0ccafa1c38512796f2b0a76890639c417af4cc04a4a4248859`。29件 current原bytes = 固定Git blob = 清单bytes/SHA；base→candidate实际路径集精确为清单28项加清单，无其它产品/验收修改。
- 入口仅AGENTS保护M，15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；index空。结束前仍同身份，未stage/commit。四writer当前bytes/SHA与base同；旧adoption12逐current/base/记录hash同。旧offer47无本候选变更，没有重新全文审47件或读其旧binary/tool/witness。

全文读取当前AGENTS、D0文档窗与limited root closure；完整读三schema所有字段和值、完整descriptor、主协议、consumer合同、自检源码、作者交付/验证记录及原owner acceptance/disposition。大schema从完整JSON buffer连续紧凑分段读完，没有以首个截断输出作全文；协议首个组合输出后补读§6–8，consumer另完整读取。原adoption A1–A4/N-01采用根限定收件和owner接收，不重开原全部供应源审计。

字段责任917行完整JSON解析，独立从三schema枚举全部显式properties指针，验证集合、无重复/缺行与每行shape子集全同；逐行职责只有已声明的三种actor组合，exact安全码18项与合同表对齐。没有把派生索引或作者摘要代三schema本体。synthetic valid全部解析并逐完整schema形状检查，归档/四函数/checker/receipt链完整对象与RECORD/映射/运行各组关系核对，32 invalid全部改动值/理由和1 valid variant逐项读；重复原子树以精确JSON pointer引用复用，不声称逐字显示全部重复base和917行索引。样例本来只相对于有限断言valid，非真实pin/CodeType/安装/许可/构建实例。

## F1 / P2：失败运行被强制写成完整、成功的身份观察

位置：`runtime-validation-receipt.schema.json` L209、233的header/terminal必为file对象；L467–563的moduleLoaders恰23且exactCodeType、singleCanonicalObject固定true；L566以后distribution/function/checker同样强制真实完整成功观察；L861的packageCodeBoundToSource固定archive-loader-consistent-with-declared-source；L865–888全字段required。`document-selfcheck.py`逐run又要求所有header/terminal存在manifest、完整canonical列表及checker等于expected。

合同§3明确hardkill半行raw仍保存/incomplete，§4明确argv/provenance非法可前置exit2；protocol§8要求保首次失败与真实exit/signal。当前schema即使collectionComplete=false仍要求全部成功观察，无法表达以下合法失败证据：

1. provenance尚未读取或strict解析失败，stdout未发header/terminal，真实exit2；Python/declaredComposition/provenance digest及23loader实际尚未观察。写null、空数组或缺字段均拒绝；若填批准预期值，就把声明冒充真实观察。
2. hard timeout/kill发生在header前或stdout半行，真实exit=null、signal保SIGKILL（仅作为synthetic示例，不声称发生过实际kill）。虽然exit/signal字段可表示，缺失header/terminal和部分loader仍使整个receipt非法；保存一个空header文件不能替代明确“未产生header”的状态。
3. 已有header但后续fresh/cold/warm或caller采集阶段失败，只留下部分loader/cache证据和无terminal；完整23/4/checker强制项仍不能如实保留。
4. 实际loader返回非exact CodeType或canonical alias不一致，必须记录观察false与相应前置拒绝；schema把这两个实际失败事实固定成true。相同问题也覆盖dynamicChecker.sameConsumerObject与packageCodeBoundToSource常量。source-mode也不应被迫自称archive-loader绑定已成功。
5. invalid argv尝试的真实raw argv需要留作拒绝记录；consumer仍只接受原三数组。不能用receipt只允许成功argv来删掉负例，也不能通过开放probe接受任意argv解决。

独立有限形状反例已实际运行于纯文档JSON：precondition-no-header-no-loader、hardkill-partial-raw、header-then-partial-loaders、observed-non-CodeType、observed-alias-mismatch均被candidate shape拒绝。完整改动/拒绝点在independent-document-check.stdout；摘要在independent-check-summary.json。它们是**应能保存的失败证据**，被schema拒绝是发现的可复核依据，不是产品测试失败或真实运行见证。

修订要求：分开“执行/观察是否发生”“实际观察值”“校验是否通过”，给所有必需字段明确可用性/不可用理由及类型分支；真实未观测值允许显式null/部分集合并标原因，观察到false/不等必须可保存；完整成功分支仍要求完整23+第四模块+四function+checker及对应证据，不能全局放宽成可随意省略。stdout/stderr原bytes始终保留，header/terminal未产生、产生但坏JSON、已解析完整三态明确。若选择独立失败attempt schema，须同一完整ordered manifest纳入并与正常run一一关联，不能藏到未列副日志。caller未launch的not-started与真实child拒绝/exit/signal分开。

验收至少增加：无header前置exit2、invalid argv拒绝记录、无header kill、header后部分观察/无terminal、非CodeType/alias/checker false、完整known-rejection的采集状态、source/frozen各自适用字段；再有invalid例保证缺必需raw、伪造fullSuiteCollectionComplete=true、缺417或terminal而标complete、以null吞掉已实际观察失败均拒绝。所有失败路径保第一原件，不重试生成替代成功证据。不得回填build receipt或放宽三argv/图业务边界。

## F2 / P2：header完整strict协议仍推迟到D2

位置：`consumer-contract.md` §3（L39附近）要求header分开“declared supplier/source identity”“actual模块/函数/checker runtime code”等，但紧接着写“未来D2精确header schema须同本合同”。本候选三个schema没有header payload定义；runtime receipt的header仅是root/path/bytes/SHA指针，field-responsibility917行也仅索引该file对象。`synthetic-design-cases.json`的header身份是1B占位，未提供一个可按完整header定义判断的synthetic header。

因此D0没有给consumer/caller双方同一份精确的header字段名全集、required/unknown属性规则、所有字段的精确类型/可空性及source/frozen/失败分支。合同里declaredCompositionRef/externalReceiptStatus等少数字面名已固定，不能补齐其余declared supplier/source组的键名、完整actual loader/function/checker对象层级、source23实际观察字段在header的准确位置和与run/provenance的逐字段映射。两个独立实现仍需在D2自行决定关键协议形状。hash绑定opaque header文件证明原件身份，不能替代header shape或绑定其语义。

本窗要求“完整可消费协议、strict shape、所有必需字段/精确类型/名称集合/可空缺失区别”，D2才授权产品实现不构成推迟D0协议定义的理由。修订可新增独立纯文档header schema，或在本地$defs完整定义并由receipt/caller合同引用；不要求现在写产品consumer。应保存原完整header能力与原失败/417/typed等范围，不能为减少定义而删原字段，也不能从现有未授权产品执行推测真实值。

验收：提供完整source/frozen synthetic header及其receipt映射；unknown/missing/null/type/bool-as-int、重复canonical/函数、错moduleBindingId/source23/checker对象、provenance digest/组合ref错绑、source与frozen不适用字段、失败header可用性均有有限反例；声明数据与实际loader观测、external-unverified与root批准明确分开。真正runtime/code/cache稳定性仍留E1实际窗口，synthetic不冒运行通过。

## F3 / P3：真实Python属性名误写为Markdown强调

`protocol.md` L62写`function.**code**`；实际合同另处为`runtime.__code__`。这里应明确字面`function.__code__`并使用行内代码，避免把不存在的`code`属性当后继consumer取值依据。只修文档拼写，不改fingerprint算法或对象绑定规则；新candidate后delta核对即可。

## 已支持的A1–A4/N-01与保留边界

A1：schema中普通最终file字段root为bundle-root常量，payload为meipass-root，bundle `_internal/`换算、唯一后置provenance排除、同真实root executable/bootloader、外部source/installed/artifact/witness/log根分域和真实containment/别名/symlink/hardlink拒绝，合同明确。不能只凭字符串pattern证明真实文件安全；此轮未访问任何实际包或安装环境。

A2：archiveId封闭三值，location严格oneOf，父carchive→pyz、深度≤2、唯一TOC/parent-first和raw witness与普通file两账明确。23canonical与额外pyshacl.validator binding、bootstrap、四function同module source及同co_consts索引，source编译与实际archive code分域；超实际布局先delta，不自动递归或总拒绝逃避功能。这些是完整静态协议支持，不证明真实工具已经产这种布局。

A2.5/N-01：build checker只Git source/bundle data/expectedBundleSourceCode；stage常量、无runtimeLoaderCode，真实resources.CONTRACT/get_code在E1/caller/header，无另exec/alias/重注册要求。fingerprint保原四字段及filename-only递归normalize、marshal4、完整Python/build/cache域，不降sourceSHA。原domain字面兼容解释在合同中，不能因此当actual loader已测。

A3：八runtime精确名字/版本与build-tool独立账、完整all-platform artifacts/selected/Requires-Dist/extras/markers、METADATA/许可/NOTICE与runtime components映射均保。RECORD原base64文件与每CSV记录原字节/三个原字段另存，安装批准根规范path、row↔installed双向映射/owner omission理由、runtime必需不得omit均明确。独立用新synthetic的9个发行/工具共36条CSV记录重解原字段核同，仅新合成数据。此轮未读或认证actual RECORD/许可证/安装/原artifact真实性。

A4：provenance→完整directory→immutable build receipt→process、后续runtime manifest→validation receipt单向。build固定not-executed/null/unapproved；root单独批准、caller前核完整固定包后绑header、probe不读包外locator、不自批准。pending/compared及三boolean false的区分已明确，valid variant证明“发生比较”不等matched。F1/F2仍阻止完整运行合同收口；不能因有单向图或所有hash存在而略过它们。

原33路径/43guard/23供应计数、完整417/独立oracle/B1/S1/parent、原默认与旧flag、完整Python优化/cache/marshal/16MiB拒绝策略、typed费用/库分类待证、SQLite损坏HOLD/wholeH/Job/selected、57P0/六迭代和指定同版双模型/CI/两OS/真人/develop均未解除。T05仅按root当前有限收件口径，不重新评新oracle或把旧快照当现在通过。

## 实际检查、原件与限制

1. 普通Git/文件/hash/JSON：29件current=Git=manifest、精确base diff、旧adoption12与四writer当前冻结、保护AGENTS/空index已实核。
2. 独立pure-document脚本`independent-document-check.py`仅stdlib，读本新JSON及必要固定Git/冻结hash，生成完整stdout49638B、stderr0；包括三synthetic shape、917完整索引、5个F1反例。它是有限关键词检查，**不是JSONSchema2020-12引擎**。未import/call任何产品、旧prepared runner/reader/helper或候选局部函数。
3. 已读源码后，另以`/usr/bin/python3 document-selfcheck.py`主入口执行本窗明确允许的外部纯文档自检一次，完整stdout3106B/SHA256 `4d722094a366d8134bb8aedf03649228e3e6fccbc2b74e147e910a767a3de258`、stderr0；1 synthetic triplet、1 valid variant、32 invalid、3本地refs。未将有限关键词/关系通过称引擎验证或所有真实协议关系证明。
4. candidate精确Git diff whitespace无诊断；结束检查记录exit0。报告及本人新增摘要JSON用已知现有formatter单独检查，实际结果在最终seal/外报；不安装/探版本。未格式化candidate、历史报告或原件。

准备原件中的worktree-local formatter首错保留。本人首个组合输出截断已分别补读关键全文；一次输出过多反例的重复23loader导致展示截断，完整raw未改，再完整解析并输出所有5例的改动字段/拒绝点，不把截断display当全文；一次functions.exec编排JS缺右括号在工具运行前被拒，修正后继续，没有candidate写入或产品运行。无自检断言失败被覆盖；5个shape拒绝是F1故意构造的文档反例。

没有JSONSchema引擎/产品/fixture模拟/pytest/业务compile/py_compile/archive解码、安装/环境版本能力探针/网络/DB/native/GUI，未读旧binary/toolSDKwitness，没有付费外审/新线程/Goal、stage/commit/push/PR/merge。仅写本新独立报告/脚本/日志/摘要。这个内部fresh审查不替指定双方同版外审。

结论仍为**NEEDS_CHANGE：F1/P2、F2/P2、F3/P3 OPEN for 76c774e**。请原owner先完整读本报告及反例，保首candidate/首报告，修订实际新candidate后再派本fresh作者作受影响delta；未授权任何执行或后继产品实现。

## Reviewer final seal

Full report readback completed before this seal. F1/P2, F2/P2 and F3/P3 remain OPEN for fixed 76c774ec7612998cdcb1079deff5c988c15053e6. Only this reviewer new report/check artifacts were written; candidate and historical originals remain unchanged. Existing Prettier write/check reported success. The earlier no-index whitespace command returned 1 with no diagnostics because a new file differs from /dev/null; this is not a whitespace failure. Final format/check exit codes, exact final report bytes/SHA and Git status are recorded externally in independent-format-record.json and sent to owner; no self hash is embedded. No further report writes after this seal.
