# I05 D2 consumer 纯设计独立审查 R1

**Pass，严格限定于冻结 candidate `d2c28a2bf549f4202b6188dde7fe4efee1c8769e` 的字段接收、约束来源、分域、拒绝与后继交接设计。** 没有新增阻断该纯设计收件的 P0/P1/P2 发现。G02/G03 是候选明确保留的完整接线阻断，未被本 Pass 关闭；本候选不能称完整 runtime 规范无缺口或产品 ready。

精确10件新文档的显式格式检查为 **exit 1**，三份 review JSON 有格式警告，不能登记全格式绿。五份 owner 设计文档无该次警告。详见下文；本审未为纯格式变更冻结原件。

## 身份、范围与独立性

审者 `/root/d2_consumer_design_review_r1`；唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design`，分支 `docs/I05-d2-consumer-design`。批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；冻结 process/HEAD `e4f11058ab92fee6731737a89fc87dfc9f552569`。独立核 base→candidate→process 祖先关系及 base→process 精确38路径，均在本窗两个 docs 前缀。

27固定输入逐件独立读取25个指定 Git ref:path 和2份精确 root closure；当前副本=固定 Git/外部原件=声明 bytes/SHA。36 payload 合7,884,909B；manifest 8,352B/SHA `a70f81a78b862b0ad00a49157766097aced6ba7e6e19a7d1635f4e2bea5ea7b1`；后出 receipt 93,700B/SHA `30dda838bc46f6c8332a529e902366a73f2d46fd0672a4274e2606eb04d5a209`。38件分别核当前字节、固定 Git blob、清单及授权路径，未以目录名或作者 exit0 代身份。

全文读窗口/固定输入清单、最新版主与树 AGENTS、common及桌面政策。两份 AGENTS 均15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，既有 M 未暂存。全文静读主协议/consumer合同/投影spec与model文本/完整旧合同、相关限定独审处置、候选五owner文件和作者checker；大JSON完整解析后按独立枚举及精确pointer核所有属性和原值，不将截断展示冒全文。

没有导入或执行固定 model、作者 checker、产品或第三方函数；未读费用R2/R3/WIP、产品算法、probe/tests/generator/actual，也未展开D0清单以外旧运行流。D0其余成员仅据已授权manifest承接身份。本审仅新增自己的报告、proof、checker及JSON原件；无 stage/commit/分支切换/push/新Goal/用户聊天/外发消息。

## 字段与跨层关系的独立结果

审者另写只读 stdlib 枚举器，从四个 schema 本体重新发现属性；没有用作者 propertyIndex 生成期望集合。随后独立走根 `$ref`、每个 union arm、全部实际数组下标模板，和候选逐行比对。

| 对象           | 独立结果与意义                                                                                                                                                        |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 四schema属性   | provenance669、build receipt56、runtime receipt366、header150，共1241；逐属性完整约束原pointer、required及原职责核同                                                  |
| 可达与定义     | 1229根可达，12未引用`$defs/file/source/fingerprint`只作定义；没有编造成运行字段                                                                                       |
| 实例规则       | 全55数组规则、200对象规则及每行实例位置/完整分支链/独立嵌套下标相符；不是只查首元素或仅counts                                                                         |
| profile        | 独立递归得到483具体叶，全部精确类型/原值相等；8项批准字段仍null/空/false，三exact argv保持原值                                                                        |
| 37目标         | 每项完整case指针核原对象，1469 expected叶逐值相等；完整case仍含typed math、input refs、policy/参数、hash、preconditions、finiteRelations、pending及两项明确invocation |
| header→receipt | 对150属性独立生成raw→headerPayload及各run组的目标路径，全部精确相符；不是仅验证目标pointer“存在”                                                                      |
| 拒绝设计       | 全32规则、75声明式拒绝及4全字段mutation族语义核对；34作者detached样例另用独立有限谓词重判，6允许留证/28拒绝相符                                                       |

四层明确为 build-provenance/2→immutable build-receipt/2→后出 runtime-validation-receipt/2，header/1 与原raw先产生、后被validation绑定；consumer2.1.0/profile3不混版。receipt指完整原provenance和外部真实见证，不把producer声明变成consumer观察。原source/profile/tool→实际build见证→provenance→完整目录→build票→外部批准→真实raw/header→runtime manifest→validation的摘要preimage是单向的；manifest与validation不自收、不回填祖先。

source仅前22供应声明、全部23实际source bytes/SHA及loader观察；第23新pin由caller外置批准。source的组合/provenance/declaredPython为null。frozen/parent声明23与已读原provenance绑定，但canonical及distribution的actualSource、observedSource23均null，不能把包内声明当source原件观察。

Python完整build/cache/magic/flags等域与四字段code fingerprint分开；source SHA、archive raw SHA、compile指纹与runtime loader不得互填。E0 checker只有source↔bundle data编译，schema无runtimeLoaderCode；E1才从原resources.CONTRACT取实际loader，同canonical对象、exact CodeType、四函数的同co_consts索引、真实`function.__code__`及fresh/cold/warm/cache需真实见证。RECORD逐CSV原字节、artifact/installed/final三账、完整archive TOC/raw witness、许可与platform组件各有真实外部owner，声明true不代实物链。

## 失败保全、首错与业务比较

not-started仅未dispatch，不造child/raw/exit；真实preheader exit2保stdout/stderr即使零字节，非法argv保原数组且code=null；incomplete保完整raw、坏JSON/半行与实际partial/false/错域，signal非null时exit=null。严格shape坏是malformed/headerPayload=null；shape可解析但批准绑定错仍保存实际payload并记incomplete，不能用exit0或修正值覆盖。observedPaths必须保所有非null叶，包括false/0/空字符串，并回核原raw；值与mask同时改也不能逃过原件。

第一个已到达失败保原受限code/stage，后继not-reached/pending。完整collected仍要求23模块、单列distribution、4函数/checker、Python/code/三argv、parsed header和terminal及原序完整所选ID/outcomes。full恰417，两个单B1不能拼full；known-rejection/unsupported/missing-context/not-executed不升级业务通过。comparison pending三身份和三结果均null，compared则独立真实comparator/oracle/report与三个可各自false的boolean，完整scope报告不可由片段顶替。

37投影的完整入口保持matches语义：两端schema→各端自身全部图槽原wire表达/完整N3排序/RDF identity唯一→同artifact共享BNode双射→其余完整exact。没有以identity helper、先sort/set、跨artifact同label、raw语言casefold、数值01/1归一、datatype混同、有序重复/尾裁剪替代完整入口。最多8BNode仍仅有限数学例界，未变产品限额；label相关digest及跨artifact真实绑定仍pending。

完整旧合同13个family行的每格原文均独立与源行核同；15项旧mandatory材料另有落点或明确G02/G03缺口。所有已返回stage的完整payload/rows/typed/sidecars/原metadata保留，拒绝partialView=null不删除前序成功阶段。十四R1保持同次真实生产/独立准入/原held expectation和allocation；未发生held字节变更、重绑expected或更早费用失败不能冒A1。shape与integer入口/参数和未到达stage仍按原完整case，不借未知当前行为填默认值。

## 明确保留的缺口与非阻断观察

- G01：真实D1锁/工具/composition及新consumer23 pin/外部批准记录仍缺；设计profile不是运行授权。
- G02：旧ee2b§4.2要求runID、inventory、完整业务政策/writer/resource等，而D0 strict header仅18键。候选未加键、裁raw或假定隐式sidecar；完整版本化stage/business carrier仍须serializer/caller提出并经D0/T03/root接收，当前阻断完整业务接线。
- G03：旧reasoningSource metadata完整编码、同次handle、graph→query/SHACL真实artifact域及原label digest preimage仍未闭合；display contentSource不能替换旧metadata入参。
- G04/G05：真实canonical首错/API/serializer、独立费用准入、真实417/oracle/B1/S1/E0/E1、whole-H与后续平台/父门均pending。

P3非阻断技术字面观察：`handoff.md` 的E1行仍写`function.**code**`。单读此交接行会把属性名误读为`code`；同候选R10及固定CR-C已明确实际`function.__code__`，所以不构成本纯设计接收的实质歧义。建议owner在后续允许变更的候选统一改成行内代码字面；本审没有修改冻结文档，也不据此要求重开普通完整轮次。

## 实际命令、格式与证据边界

`independent-r1-run-03.json` 保只读独立枚举器实际exit0、stdout796534B、stderr0及其105条子Git命令的真实分流（重复Git blob输出以已逐字核同的当前固定原件引用保全）。`independent-r1-semantic-run-02.json` 保有限关系检查exit0、stdout190531B、stderr0：35项结构/语义关系、150完整header映射、34detached样例；另有16个独立小型正反例在run03。所有这些都是有限纯设计检查，不是JSON Schema2020-12引擎、真实receipt认证、完整RDF comparator或实际417采证。

作者9条validation与87条receipt命令的192条流逐件核验：118条UTF-8文本、74条已绑定当前原件引用，bytes/SHA相符；未重跑会覆写作者证据的脚本。独立base→process `git diff --check` exit0，index空；当前新增只有本审允许路径，AGENTS保护M保留。

收到root指出忽略规则可能使普通Prettier exit0跳过文件的新风险后，本审实际用指定既有formatter `--ignore-path /dev/null --check` 精确检查五owner加author-notes、author-validation、input-identity、manifest、receipt共10件，**exit1**；stderr仅列author-validation.json、input-identity.json、candidate-receipt.json三件格式警告。五owner与author-notes/manifest无该次警告。原普通--check记录不能单凭exit0证明覆盖；全10格式未绿。完整原流在`independent-r1-candidate-explicit-format.json`，没有格式化源副本/Python文本/历史流/冻结candidate。这是格式及证据口径边界，不改变本轮语义设计结论。

首失败如实保留：审者第一次错误定位不存在的本体根AGENTS，cat exit1，只读且已纠正；未分流初期读取只在工具转录，不重造双流。独立枚举器run01因审者将$ref元数据误当union keyword而KeyError，run02因审者误取case顶层kind而KeyError；首/次版脚本及完整异常双流均保留，未改候选。semantic-run01把schema的`const:null`错误预期为`type:null`而exit1，原判定/首版保留；修正审者检查后才有run02 exit0。这些是审者程序错误，不是候选Fail或重试产品换绿。前两异常前的内部Git流未被异常进程输出，不倒填；run03完整捕获独立核验。root另报告误用manifest.json的只读exit1，仅按root已披露过程边界承接，未重跑或冒本审直接见证。

无产品/模型/第三方import、pytest/npmcheck/构建/业务编译、native/caller/ABI/loader/drain/DB/probe、网络/安装/版本探针、GUI/外部模型或收费服务；无运行票。wholeOracleComplete=false；父137、417runtime、原S1、正式Job/Store/selected、SQLite损坏HOLD/whole-H、两OS/真人/指定双审/CI/develop/远端及原Goal保持开放。报告与proof最终bytes/SHA由独立seal记录及交接消息外报，不自填未来commit或自身hash。
