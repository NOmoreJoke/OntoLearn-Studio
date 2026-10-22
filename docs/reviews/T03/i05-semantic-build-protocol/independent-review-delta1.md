# D0 delta1 独立复审：F1/F2/F3 CLOSED

2026-10-22。原fresh reviewer `/root/i05_d0_independent_review`。**F1/P2、F2/P2、F3/P3 对实际后继 4a32b9540a267601a25f21d0602cda73cde2d275 CLOSED；受影响D0静态协议一致性支持，待owner/root正式收件。** 本结论不授权D1/D2/D3/E0以后，不证明实际caller、编译/归档、loader/cache、运行或任何父验收通过。首候选与首NEEDS_CHANGE全文及原始检查保持历史，不倒写成首轮通过。

## 1. 实际候选、范围与全文阅读

原base `bba31be7384a676e54cb3b64e219f14bf2a9460e`；首candidate `76c774ec7612998cdcb1079deff5c988c15053e6`；首报告process `d09f826e0f1d9b102c6ecdcf867686704d349b71`；本次候选 `4a32b9540a267601a25f21d0602cda73cde2d275`。树及branch仍为 `.worktrees/T03-i05-semantic-offer-owner-review` / `docs/T03-i05-semantic-offer-owner-review`。无新Goal/chat或外审任务。

独立核 `delta1-owner-manifest.json`：57 payload3100072B，加自身12301B，共58件3112373B；清单SHA256 `1f4b4f6264c0210d4837685f17086cef72938e02fd3d1b82e4b4bd5d7830c141`。全部当前原bytes/SHA与清单及固定Git blob相同，清单自身current=固定Git；base→candidate的精确路径集合为这58件。first-review-process→candidate恰28个受影响/新增协议与过程路径，不夹带产品、四writer、锁、CI或其它目录。两份build schema与首candidate逐字节相同；原32 invalid JSON对象逐对象相等，首报告及旧raw由完整清单固定不变。此轮未重开无变化offer47/供应源码/实际运行/包审。

本次完整读新consumer合同全部§1–6、protocol完整受影响diff、profile完整有限diff、作者delta说明/owner接收、新header schema全部字段和值、runtime receipt全部受影响字段和值及完整自检源码。runtime.headerPayload的对象core与已完整读的header严格deep-equal（只排$schema/$id/title/$comment四根描述元数据），以该精确引用替代重复显示，nullable分支也逐值核对；其余runtime完整紧凑JSON分段读完。四schema1241个显式property索引/required/shape、全部新valid及invalid关系随自检源码和数据核对，不以作者汇总或数量代正文。

synthetic基例与各新变体完整JSON解析；14个新增valid变体逐字段差异、22个新增invalid的改动值/理由全部检查；重复的大header与数组以同一base或既有变体精确JSON pointer复用。初次直接差异输出过长被截断，改为仅实际改动及精确引用后补读，未把截断display当全文。原32 invalid按首审已读且本次逐对象等值继承。所有15 synthetic header raw的utf8原bytes→manifest的bytes/SHA又独立核同；这是设计数据，不是实际运行JSONL或实际CodeType。

入口HEAD实为该候选，index空/仅保护AGENTS M；保护身份仍15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。本审只新增自己的delta报告和必要新检查原件，未改候选或首审文件；未stage/commit。

## 2. F1：失败观察与完整采集分离，CLOSED

runtime receipt升级 `/2`，contract CR-R给出四状态及全部required字段的可用性关系，原“collectionComplete=false仍强制23完整成功观察”已移除。失败留证与成功门禁采用schema shape加规范关系共同生效，不能只跑shape取代关系。

| 分支                | 当前协议与独立核对                                                                                                                                                                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| not-started         | caller尚未dispatch；child stdout/stderr/header/terminal/payload、exit/signal、所有实际观察为null/空集合，mask/observationIds空、两complete=false；failure由caller prelaunch和原三种批准/身份/目录码记录。不把拟argv当实际已执行，不造child或空child日志。 |
| pre-header-rejected | 实际child前置exit2，stdout/stderr原件必存，header/terminal absent+null，图业务未开始；invalid argv保实际数组与原受限stderr，code=null/phase=argv/reason=argv-rejected。原三exact数组依旧是consumer唯一可接受输入。                                        |
| incomplete          | 实际dispatch后的部分采集/前置观察/stream或caller回绑失败，raw始终保留；header/terminal分别absent、malformed、parsed。半行或strict shape错误的原完整bytes仍入manifest，不造parsed payload；signal非null时真实exit=null，未确认终态保null。                 |
| collected           | 实际exit0/signal=null/failure=null、完整raw与parsed header/terminal、全部身份/代码域/集合/argv关系通过；full-v1仍417唯一有序、全complete；B1各1 measurement且不是full。known rejection等业务结果不因此变成operation pass。                                |

真实dispatch/执行器失败必须与未dispatch的prelaunch拒绝区分：不能套not-started的批准缺失码/空raw假装没有尝试；记录实际caller首错和实际取得的capture原件，未知child终态保持null，不凭harness错误补造child exit1/2或signal。当前这项是caller真实证据职责，D0只审可表达的数据与状态，不声称已运行/实现某个spawn异常路径。真实OS执行与停止/readerjoin仍在后继窗口。

具体合成数据已覆盖原首审的五种反例并增加相关边界：无header的provenance拒绝、invalid argv拒绝、无header kill、17B坏JSON/半行、header后2个loader且无terminal、非CodeType时exactCodeType=false且fingerprint=null、alias false、checker.sameConsumerObject=false、Python3.13/optimize1前置拒绝、caller not-started。它们现在都能作为失败记录保存，未填预期值冒观察。source/frozen适用域另分，不再强迫source自称archive绑定成功。

observedPaths针对原始观察派生的全部非null叶值，false明确是观察；重复/越界/指null或遗漏false均拒绝。其JSON内一致性不足以证明真实观察，caller还必须从完整raw/header/首错逐字段核同。合成false吞null反例保原mask和raw，不能通过；同时改值和mask也仍需过原raw→payload→run关系，不能因为两份声明一致就逃过原件。fresh/cache与firstEvidence引用入同一完整manifest，不能藏未列旁日志。

完整collected保23有序canonical、单列pyshacl.validator、四function、resources.CONTRACT checker；CodeType/同canonical对象/同consumer对象为true，全部fingerprint、函数same co_consts索引及完整Python同批准域。null loader/缺terminal/raw、重复canonical/function、416冒417、partial伪full、错argv/错ref/digest/域都不被规范接受。known-rejection、unsupported、missing-context、not-executed是完整采集的业务状态，完整采集不能自推三项外部比较结果，originalOperationPassed尤其不能从missing-context/not-executed升真。

`R-parsed-header-binding-mismatch`保完整23/4、child exit字段为0和完整parsed header/terminal，但实际ref/digest为错误值，run仍incomplete/两complete=false、failure=HEADER_PROVENANCE_BINDING_MISMATCH；反例再把它升collected会拒绝。故exit0或完整shape不抵消实际批准回绑差异。F1在本D0静态规范范围关闭；不是实际运行成功证书。

## 3. F2：完整header与source/frozen分域，CLOSED

新增 `runtime-header.schema.json` 26824B，format=`i05-semantic-runtime-header/1`、ID=`urn:ontolearn:i05:runtime-header:1`。18个顶层键以及所有嵌套required/type/null/enum/const/additionalProperties=false完整写定：kind、format、profileId、mode、selector、externalReceiptStatus、declaredCompositionRef、provenanceRead、declaredSupplierSources、declaredPython、observedPython、moduleLoaders、distributionModuleLoader、functionCodes、dynamicChecker、observedSource23、packageCodeBoundToSource、sourceCodeBoundToSource。D2现在只实现固定协议，未再留“未来D2决定exact header schema”。

receipt.headerPayload完整同形core，与独立header schema deep-equal；raw原bytes/SHA先核，再strict JSON解析到完整payload，再向run逐字段映射。不能通过重序列化替代原hash。unknown/缺字段/错误类型/bool作int/错kind等严格shape失败，仍保原raw作为malformed而非造payload；shape合法但wrong mode/selector/组合ref/digest/对象等实际值可保incomplete，成功collected才逐字段强制批准映射。parsed不等已批准。

source：declaredCompositionRef/provenanceRead/declaredPython为null；declaredSupplierSources仅前22供应声明，不把第23自身SHA嵌入声明。23实际source bytes/SHA、实际loader和observedSource23一致，由caller对批准新consumer pin/实际composition在包外绑定；source不为填header读取frozen provenance、receipt、安装根或编译器。source绑定状态独立，package状态null。此规范不让source自批准自身pin。

frozen-independent/parent：declaredSupplierSources按23与已读provenance相同，组合ref与唯一白名单provenance实际原bytes/SHA、完整declaredPython分列；actualSource模块值及observedSource23为null，不能声称看过未收source原件。这里“模块值”覆盖23canonical和单列distribution module；本次完整frozen示例的两组actualSource实际均null。probe只核本域loader/declaration，不读外部locator。package绑定状态与source状态分开。

observedPython只保实际运行解释器可观察的字段；compilerExecutable/dontInherit属于声明编译域和caller实物链，frozen declaredPython及run.python仍保，不要求probe去读安装根。run→header投影只去除这两项外部字段；module/checker只去除外部freshColdWarmEvidence。四function/code索引等实际层级完整相同。success要求完整域同一，失败仍保存真实非3.12/非CPython/优化错误等值而非改成批准域。

新增source/frozen完整synthetic header及15 raw例有实际合成文本bytes/SHA；type/missing/unknown、重复名称/函数、错误binding/source23、错provenance/组合、source非法声称读frozen、frozen缺第23声明等有限反例已检查。无真实source/loader/cache witness。F2关闭的是完整strict合同表示缺口，不是E1稳定性或caller实施。

## 4. F3：字面属性修正，CLOSED

protocol现为2.1.0，原L62误写已改为行内代码`function.__code__`；profile格式升级3、四schema ID和外部delta/final manifest身份来源同步。未改fingerprint算法、filename-only规范化、四function绑定或CodeType域。两份build schema保持首候选原bytes/版本，build receipt仍not-executed/null/unapproved，无runtime回填。F3关闭。

## 5. 实际检查、非穷尽边界和未解除门

- 本审普通Git/文件/JSON/hash核了完整58件current/Git/清单、精确base路径集、原32 invalid等值、两build schema不变及headerCore精确相等；15 raw header另独立逐utf8 bytes/SHA对manifest核同。没有把Git blob ID单独当current hash证明。
- 全文读当前有限文档自检源码后，仅主入口实际执行一次：`/usr/bin/python3 document-selfcheck.py`，exit0，stdout5251B/SHA256 `1471417a510039cdaccec606a5a8725e4cb891777ae6568c202e3ebd291f449c`，stderr0；4schema、1241完整property指针、3本地refs、1合成triplet、15valid variants、54invalid。新原件为 `independent-delta1-selfcheck.stdout/.stderr`，独立检查摘要为 `independent-delta1-check.json`。
- 这明确是有限关键词/关系自检，非JSONSchema2020-12引擎，也非后继完整validator。源码未穷尽所有规范：例如成功full417的真实资产原序/完整业务JSONL、三项比较真值各自业务证明、frozen单列distribution actualSource、actual approval/original evidence真实性等不能只凭该脚本通过。完整CR-S/A1/A2/C/A3/A4/R/H仍共同约束，后继实现必须逐规则处理；规范已明示的要求不能因finite脚本未专设一个反例而降低，也不把有限脚本的既有边界冒称新阻断。
- 所有新valid/invalid与raw都是synthetic design data；其余原件身份有设计占位，未证明真实417 payload、typed结果、实际安装/许可/code/archive/loader/cache、费用或库分类。此轮未重跑无变化产品或重读原冻结binary/tool/SDK/witness。

既有Prettier仅对本新delta报告/新摘要格式化检查，精确结果在最终seal/外报；没有改候选格式或历史原件。首审/本次工具输出截断均保真实边界并补读，未以截断输出当全读；没有新的自检断言失败或隐藏产品重试。

无产品/probe/builder/spec/reader/helper/局部函数执行、产品fixture/pytest/业务compile/py_compile/archive解码、安装/环境版本能力探针/网络/DB/native/GUI、付费外审、stage/commit/push/PR/merge；无新Goal/聊天。仅本窗明确允许的外部纯document自检，不借native票、不读取其它树或新caller目录。

最终局部结论：**F1/P2、F2/P2、F3/P3 CLOSED for 4a32b954；D0静态协议一致性支持，待owner/root收件。** 实际D1/D2/D3/E0+、source23新pin、真实composition/installer/artifact/RECORD/许可、归档/代码域/loader/cache、完整417与独立oracle、B1/S1/parent/SQLite损坏HOLD/wholeH/Job/selected、指定双模型/CI/两OS/真人/develop及57范围/六迭代原门均未由本审关闭。

## Delta1 reviewer final seal

完整报告已readback。F1/P2、F2/P2、F3/P3对固定4a32b9540a267601a25f21d0602cda73cde2d275关闭，仅支持D0静态协议一致性，owner/root收件及全部后继实际证据门仍后置。现有formatter只写本人新报告/摘要；本seal后停止报告写入。最终新报告format check、whitespace解释、current HEAD/index/保护身份及最终bytes/SHA由独立外报independent-delta1-format-record.json记录，不在报告嵌自身hash或未来commit。没有执行产品、变更候选或stage/commit。
