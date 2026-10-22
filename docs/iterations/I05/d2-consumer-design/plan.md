# I05 D2 consumer 纯设计方案

本候选仅决定后继 consumer 的字段接收、责任、顺序、拒绝与交接方案，尚待全新独立审查；没有实施或运行 consumer。唯一工作树为 `.worktrees/I05-d2-consumer-design`，分支 `docs/I05-d2-consumer-design`，批准 base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本次未创建、重命名、完成原 Goal，未创建用户聊天，禁止 push。

## 固定依据与可复核范围

外部授权窗及27件输入清单位于 `iteration-control/2026-10-21-weekly-release/I05-d2-consumer-design-{window.md,fixed-inputs.json}`。25件 Git 设计按 repository/ref:path 读取，另2件 root closure 按原路径读取；本方 `docs/reviews/I05/d2-consumer-design/input-identity.json` 保逐件 bytes/SHA、ref/path 与固定源副本。D0 其余成员仅采用 final-manifest 中身份，没有读取其运行原流；model.py 仅静态读，保存为原字节 `.md`，未调用其中任何函数。当前主与树 AGENTS 同为15147B、SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，其政策传播是既有未暂存改动，不属于本候选，不 stage。

采用的规范身份为 D0 最终流程 `c3eb0694daad26527cc3a1eb0127ed5033f2be25`、投影最终证据 `50317c791eca95e82dfbfaa2ef71c0dfc95a9302`、完整旧合同 `ee2b30a2dad35b2d395f9c735aff80371ab41110`。D0 build-provenance/2 → build-receipt/2 → 后出 runtime-validation-receipt/2 → strict runtime-header/1，consumer 2.1.0/profile 3。箭头表示消费和绑定依赖；时间顺序中 header/raw 先于 runtime receipt，绝不从后出的 receipt 回填祖先。

`field-origin-map.json` 保四 schema 的全部1,241个显式属性，逐行保原 propertyIndex 身份、完整约束来源 pointer、实例 template、union 条件、required、producer、消费 actor、首拒 gate、未到达状态及关系规则。1,229项从 schema 根可达；其余12项是未被 `$ref` 使用的 `$defs/file`、`$defs/source`、`$defs/fingerprint` 属性，仅定义，不制造运行字段。数组 `{iN}` 指该数组实际每个下标；嵌套数组有独立变量，不能只查第0项或以总数代替集合/顺序。profile 全部具体叶值也逐项登记，37投影全字段以固定原值及每个叶 pointer 绑定；禁止只保顶层 key/count/hash摘要而删除原对象。

## 消费顺序及责任

1. root/caller 核外部可信批准记录、同一 source/composition/profile/schema/tool 身份。批准字段仍为 null/空且 executionAuthorization=false 的固定 profile 是设计输入，不是运行批准。缺批准停在 not-started，child exit/signal/raw 均 null，不 launch 后补签。
2. caller 核原 build receipt 原 bytes/SHA、完整当前 directory/executable/provenance、全 hash 绑定证据包及来源域；source 另核批准 checkout/new consumer pin。build receipt 永久 `runtimeValidation=not-executed`、runtimeEvidenceManifest=null、unapproved-produced-evidence；后续批准在独立 record。所有根由批准记录固定，alias/symlink/hardlink/escape 等真实核验留后继窗口。
3. probe 只按本域固定白名单读输入。frozen 唯一 provenance 为 `_MEIPASS/provenance/i05/source-package-parity-build.json`，上界16777216B，cap+1拒绝；strict UTF-8/无BOM/无重复key/无nonfinite/无尾数据。schema 和所有 CR 关系同时满足；schema形状通过不能降格掉来源、RECORD、完整 archive、许可或真实证据缺口。
4. 保原 resource/lock/eight-distribution/Python 前门；核23 canonical及单列 pyshacl.validator、四 function 与 resources.CONTRACT 原 checker 对象。loader class/spec/name/origin、exact CodeType、sys.modules同一canonical对象、同 co_consts 索引和完整 fingerprint/Python域逐项核；sourceSHA、同名对象、同cacheTag都不能代替code。bootstrap不计入23，第四函数不是第24 canonical。
5. header 固定18键。source 只声明前22供应 source，实际23模块都观测 source bytes/SHA；source23实际输出与loader交caller对包外新approvedConsumerPin。source 的 declaredCompositionRef/provenanceRead/declaredPython 固定null。frozen/parent 声明23来自实际读取的provenance，全部 actualSource（含distribution）及 observedSource23 固定null；不能把构建声明伪作实际观察。外部批准从不进入 probe 自证。
6. caller 全字节保存 stdout/stderr，严格唯一header→完整有序observations→唯一terminal；核原header raw→parsed headerPayload→run投影，回绑同一启动前receipt/provenance/code/Python/selector。full恰417，单B1恰1；两个单B1不能拼成full。所有尝试按原顺序保留；解析失败/半行/signal/null/false不裁剪、不补批准预期。
7. 最后才生成完整 runtime manifest 与后出 validation receipt；manifest不收自身/validation，validation不回写build票。comparison pending时三身份/三个结果均null；compared时有独立真实comparator/oracle/report，三个boolean独立可false。collectionComplete不推业务、oracle、equivalence或originalOperationPassed。

各 gate 的完整谓词、固定依据、外部证据需求和首错见 acceptance-map。每字段 strict 类型/const/enum/required/未知键规则从该字段完整 schema pointer 读取，不另造宽松 schema。有限作者 checker 仅核设计文档覆盖、指针、引用与小型合成决策，未运行JSON Schema2020-12引擎、未验证真实receipt。

## 三种数据不能互代

T03 producer 值是构建声明与真实 artifact/installed/RECORD/archive/license 见证，root审核真实来源。consumer输入是批准的固定schema/profile、外部批准包、sealed纯输入及允许的固定本域文件；声明中的source/log/RECORD/witness locator只是数据，不扩大probe读面。consumer采集证据是实际loader/function/checker/Python、原raw、header/terminal、完整阶段返回和真实exit/signal；没有观察就保null/partial，不由producer的true补填。

E0 checker只比较批准source和bundle data bytes以及各自编译指纹，stage=`build-source-to-bundle-data-only`，无runtimeLoaderCode。E1才核resources.CONTRACT原对象loader及fresh/cold/warm/cache；不exec第二份、不alias、不重注册，不要求checker进PYZ。source compile/source bytes、archive raw bytes、code fingerprint、runtime loader、许可/metadata分别保完整域。

## 失败、首错与未到达

not-started、pre-header-rejected、incomplete、collected 与 header/terminal 的 absent/malformed/parsed 正交记录，按consumer §5–6条件约束。pre-header真实exit2不能伪成caller未启动；dispatch失败不猜prelaunch批准失败。incomplete保完整raw，signal非null则exit=null；未确认终态的null不能猜1/2/130。observedPaths是实际非null叶全集，包括false，须逐字段与raw核同，mask和值同时改也不成立。malformed的完整JSON/坏JSON/半行照原字节保留，headerPayload=null，不制造可解析副本。

第一个已到达失败按真实受限code/stage记录；后继未到达gate记not-reached/pending，禁止把其目标拒绝当已观察。收集完整中的known-rejection、unsupported、missing-context、not-executed仍保原状态，不能列成能力通过。R1十四restore扰动只有同次真实生产及独立资源准入先成立、确改至少一个held字节后才测A1；生产/费用先失败就记A1未到达，不接受任意RESOURCE_LIMIT顶替、不重绑expectation或换allocation。

## 37投影与完整业务材料

37项完整expectedProjection、independentTypedMath、参数、preconditions、finiteRelations、pending、inputSourceRefs在固定cases原件保全；acceptance-map逐ID/逐叶引用原值。legacy11项为10正常加1 unbound-head拒绝。唯一完整比较入口是固定model的 `matches` 所定义语义：expected schema→observed schema→各端自身全部graph槽wire表达/N3完整三元组升序/RDF identity唯一性→同artifact全域共享BNode双射→其余完整exact。后继须独立实现并验真实来源；本窗没有执行matches、模型或serializer，没有产生新golden或回灌T05。

typed facts/ontology、N3 rdfs/rules/basis、evidence result/inputs、source triple/inputs/basis、query全rows/null和SHACL六term共享同一明确artifact身份域；图槽按集合，ordered occurrence保顺序/重复/末项。language只在RDF身份casefold，raw/source/词法/datatype保持原值；integer01/1、int/integer不同。不能先sort/set修复wire，不能用identity helper冒完整入口。最多8BNode仅有限数学小例界，不是产品限额、算法容量或性能证明；跨artifact关系和label相关digest未决，不能一般删hash。

全部已返回stage的完整producer payload/rows/sidecars/typed/source metadata另保原件；拒绝partialView=null不删除此前成功阶段。shape/front-2按parse-data→parse-shapes→check_shapes，第二步目标拒绝则第三步未到达；integer/other-datatype-1显式映射dataPolicy/rangePolicy到validate_shacl_text参数，无新semantic.validate wrapper。

## 已决定与必须补齐的缺口

本窗决定完整字段覆盖、strict协议身份、作用域、顺序、拒绝/保留规则、37原值和后继责任；不是完整运行规范已全部闭环。handoff逐项列精确交付。

- G01：D1真实批准依赖/lock及D2新的source23 pin/真实composition/toolchain/外部批准记录缺失。固定profile的历史23rd baseline不得硬编码新consumer自hash。
- G02：ee2b §4.2旧header要求runID、inventory、writer/resource/业务政策等完整上下文；新D0 strict header只允许18键，不能塞额外字段或裁掉旧必留材料。后继I05 serializer/caller须提交独立版本化业务观察/完整stage carrier与字段落点，由D0/T03/root明确接收其与header/raw/receipt的绑定；本设计不自行发明已获批wire键。raw存在本身不等carrier协议已定。
- G03：scope旧真实reasoningSource metadata完整编码、同次handle、graph→query/SHACL artifact域及label相关原digest关系，仍需明确规范/接收；新display contentSource不能反喂旧helper。
- G04：F1/D1/R1/O1 canonical API/serializer delta、真实库首错/计数/no-I/O、真实producer/allocator/capture/issuer与独立费用规范尚未通过。不读费用WIP，不造17L/usage/预算或成功对象；费用只记接口等待。
- G05：完整417业务原件及独立oracle逐字段、B1两档fresh原件与原S1 snapshot/正式parent137、真实E0 archive/RECORD/license、E1 cache/loader/canonical object、native ABI/loader/drain/whole-H/owner仍待授权窗口与实证。

wholeOracleComplete=false；父137/417 runtime、两OS/真人/指定双审/CI/develop及完整产品门不在本窗关闭。独立审查由root另派全新agent，作者不得自认Pass。只在本方路径显式stage、实际cached diffcheck=0后本地提交；manifest与提交后receipt分别自排，candidate/process用实际提交后身份外报，不填未来自身hash。
