# I05 独立语义打包草案 R1 静态独审

结论：**当前固定候选 Fail**。有一项 P2 消费职责边界问题（R1-01）和一项 P3 接收状态元数据矛盾（R1-02）。核心生产/收据有向结构、有限闭包与原门保留已具备可审基础；本结论只针对文档可消费性和交付一致性，不把尚未构建/运行本身当作设计失败。未修改受审文件。

## 固定范围与实际核验

- 唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-build-offer-draft`，分支 `docs/I05-semantic-build-offer-draft`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；candidate/读取时HEAD `33972c5c495fcdd9af1c381c6b5d94d63117d08e`。
- 先全文读取当前 AGENTS 与外部 `I05-semantic-build-offer-draft-window.md`；AGENTS实核15852B／`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。受保护M未暂存，index空。
- 阅读主文、profile descriptor、两个schema、静态collector/schema构造源码、source/input/guard/lock/suite账本，按需读取固定2cf loader/fingerprint与6891 resources/checker代码、合同的包装/许可/采样/门禁章节、T01与source-only收件原件。完整JSON解析只用stdlib，未运行这些资料脚本或业务。
- 独立核36件payload，共1,343,411B，逐件current＝candidate Git＝candidate-manifest；manifest本身7894B／`2a4f39bd6aea2633b8c0f877ccc1083d0b8cbe8fd595556d16703e6d7da4e709`，另排自身。37条候选Git新增路径均在本窗允许两前缀。
- 独立重读106命名Git来源的blob/bytes/SHA与5命名本地来源，全部吻合。23模块/4资源/2资产/4writer恰33不同源路径；四writer当前等5f字节。由6891 builder literal重核43旧guard/30同13异；不凭先前报告代替读取。
- 从2cf实际两资产静态解析，320datasets/417observations与suite-inventory逐项一致；full集合417、两个B1集合各1，完整顺序一致。两个schema全量JSON对象键严格，local refs可解，path/Python pattern用stdlib re定点核正常/拒绝字符串；这是结构检查，不是JSONSchema库验证或消费者运行。

完整输入hash和核验摘要见 `review-r1-proof.json`。本报告及proof是本agent唯一新增写面，不stage/commit，不改candidate。

## R1-01 · P2 · 内部consumer与外部来源接收职责未完全切开

位置：主文 §4.3 frozen前置表、其后“固定caller/consumer分工”和 §4.4；schema中的 `build.stdoutReceipt/stderrReceipt`、`sourceCompilation.source`、`actualArchiveCode.extractorSource`、`archives`、`distributions`、`composition.ownerAcceptanceRecord` 等外部证据字段。

正文的正确主线是：caller持root批准的包外receipt，先核来源/目录/provenance/executable；probe不持该receipt，不增加任意外部路径/环境参数，只读bundle provenance及实际loader code；header输出digest供caller回绑，`externalReceiptStatus=external-unverified`。这一主线避免包内自证批准，也没有强迫probe读取拿不到的receipt。

但§4.3仍要求frozen consumer完成“schema exact/版本→**approvedcomposition**/23集合/4资源/2资产/lock/Python核对”；§4.4又以统一的“接收schema还必须核”要求refs实际存在、33源bytes/Gitblob、installed RECORD、完整archive、final receipt等核验，没有明确是哪个外部接收主体。按字面实施，probe要么须访问这些被禁止/不存在的外部路径，要么只信bundle自报的source/审批状态而误称核过approvedcomposition。

具体反例：一份合法onedir包只含最终exe、_internal和已批准provenance。其 `build.stdoutReceipt.path` 是批准证据前缀中的外部原始日志，`extractorSource.ref/path/gitBlob` 指T03固定源码，`ownerAcceptanceRecord` 是外部Git资料；包内没有Git对象库、原installed环境或包外receipt。probe可核这些字段的严格shape并把实际loadercode与声明指纹比较，却无法从自身知道composition已获root批准，也不能在只读bundle规则下逐项解引用全部来源。当前文字没有给实施者一个可同时满足所有句子的职责分配。

最小修正无需更改所选方案或扩大执行权：

1. 加逐字段/证据域责任表：T03生产实际编译/archive/installed/许可见证；root/外部接收方审批准来源与完整组合；caller在launch前核批准receipt、外部原件/提取器/日志/源码引用和完整目录，在launch后回绑header/provenance digest与实际runtime code结果。
2. probe仅做strict结构/版本与声明身份的关联校验、bundle内4资源/2资产/锁、实际Python/模块/函数/checker loadercode对声明指纹。其字段明确叫 `declaredCompositionRef`；内部不得宣称验证批准，也不得解引用外部日志、Gitsource、installed-file、extractor、owner记录路径。source第23 probe同样不嵌自己SHA：可发实际source bytes/loader code观测，由caller按批准组合pin核，不把自报摘要叫批准。
3. §4.4明确属于root/外部接收/caller的完整来源接收义务；schema中外部路径在probe处仅作受限语法数据。列外部预启动拒绝、probe前置/loader拒绝、启动后header回绑失败各自的稳定失败码和未启动/不完整终态，避免把外部失败改成probe业务成功。

这是一项可消费性边界修正，不要求本窗实现builder/consumer、运行包或新增通用receipt载体。修订后仅需文档delta及相关schema/descriptor一致性复核。

## R1-02 · P3 · 同一source-only接收状态在JSON中仍为旧值

位置：`input-identities.json` 的 `modules23` 最后一项（新probe）的 `owner`，以及复制该对象的 `guard-migration.json`、`profile-descriptor.draft.json`；来源为 `static-collect.py` 中该行literal。

该字段仍为 `I05; source-only R2 not root accepted`。主文§1与实际保全的 `I05-source-package-source-only-root-closure.md.raw` 已明确root限定接受2cf、final61f53的source-only交付，仍未批准运行/锁/包。因此当前JSON在同一交付中同时记“root未接收”和“root限定已接收”，读取机器账本的后继维护者会得到不同前置状态。

应仅修collector的owner/接收边界文字及三份派生JSON，写成root已source-only限定接收、维护权不转移、runtime/lock/package未接收；保固定2cf源码hash与原36payload/首审原件，不更换供应source/ref。生成新candidate与清单并复核delta，不能倒改本候选或假称产品修改。

## 已核可成立的协议与范围

1. **来源和所有权。** T03四writer由原维护者后续接收/实施，meter HOLD不被本草案解除；22供应模块不可变、四资源只限T01已批准私有读用，两asset与新probe仍I05。2cf继续5f lock/pyproject，而probe常量要求6891锁的事实已准确分列，无静默采用依赖。旧4fa只作历史offer，T03未接收本草案。
2. **闭包和资源。** 23canonical明列而非slice旧17，rule_revalidation解除独立profile旧exclude，definitions/planning与worker/Store/旧probe仍排除，不collect整engine/quality。dynamic checker使用resources.CONTRACT原对象；实际resources源码未将其注册sys.modules，此事实没有被错误升级。三JSON+registry/lock边界与禁止resource_manifest/derive_dependencies/permits_transition等保持，未借此引入fixtures/states/dependencies。
3. **代码身份域。** 固定2cf算法确是exact CodeType递归co_consts，仅归一co_filename，marshal协议4后hash，返回algorithm/sha256/cacheTag/domain四字段。schema将原sourceSHA、actual archive member bytes、normalized code fingerprint分开，且Validator.run的source已用installed-distribution-source域而非伪造Gitref。bootstrap和canonical probe分别列archive见证，模块对象/类发行身份不以同名同hash替代。源码编译/归档提取/actual loader的实际稳定性仍待独立有限实测，缺get_code/CodeType或差异拒绝，不回退sourceSHA。
4. **无循环结构。** 现有输入commit/descriptor→build/archive见证→onedir普通data后置provenance→包外完整目录manifest→包外receipt→后续process commit的有向顺序没有要求文件hash自己或预填未来process commit。provenance不进入其自己的payload hash，外部manifest另绑定该provenance；签名改字节须新receipt。R1-01所需修正是职责标明，不否定这个结构。
5. **依赖/许可。** 实查八runtime distribution、23整锁与rdflib html extra→html5rdf、wcwidth完整平台artifact记录，未从版本推许可证。installed RECORD/code/data/metadata/LICENSE/NOTICE/COPYING与runtime/Python/bootloader/动态库责任均列，缺项不生成accepted build来源。静态候选表没有被当作实际archive/插件/native闭包。
6. **完整suite/oracle。** 全417项与实际资产一致，C仍2query+11SHACL加显式policy观察；原83/106/54/50、repair77/四E5片段/五unresolved的权威与未执行状态保留。source-package全结果比较与T05独立数学oracle分判，T05新作者报告尚未审/收件、allocation/date首码pending明确，不以旧78/4/1填expected。
7. **完整采集/原门。** 完整JSONL、失败阶段真实已返回值、wire/typed/DAG/roots/全六字段/全rows、首错/unknown/半行原件、逻辑cap/physical票和cancel/stopping/实际停止均分域。12个B1 fresh纯语义试验与原12个S1 snapshot分开，parent package:dir/正式Job/Store/selected/H/全57P0/C–G/PRD10–12/六迭代/指定双模型/CI/两OS/真人/develop远端门保留，未重开被拒RSS/heap/OS方法。

## 未执行与后继界限

只用Git/文件与stdlib AST/JSON/hash/re作本报告。未import/执行产品、probe、pytest、builder/spec/reader/helper、fixture模拟或业务compile/archive解码；未读取旧binary/witness/42772index/SDK/toolpayload，未安装/网络/DB/native/GUI/计量，未借T03票，未push/PR/merge/创建Goal/用户线程。未执行JSONSchema库或真实消费者，不把schema结构解析写成协议已运行。

本独审不替代ZCode GLM-5.3最高与MiniMax M3.1-Flash xhigh同版指定双审。修R1-01/R1-02后保原Fail与候选，生成新固定文档candidate，针对职责表、状态元数据及受影响上下文做delta即可；不要重跑旧组件、扩大实施或要求T03在meter HOLD期间新执行。报告写定后停止新增写入。
