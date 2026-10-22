# D2 canonical interface：字段、原codec与摘要桥接设计

本候选只把已接收的11件 fixed39a91纯事实推进为可审consumer DTO设计；未实施产品、codec、caller或测试，也未闭M02–M05/G02/G03实际门。revisionBase=`0841ffbe7a4599fbea96f4ff998808f3f4e00972`，旧176件冻结，旧覆盖事故与失败历史不改。本窗只新建两个d2-canonical-interface-design前缀，写入前核旧176保护集，首次exclusive create。

## 已收到什么、仍不是什么

11件精确ref/path/bytes/SHA由root限定接收，来源39a91、原产品事实源2cf；这里只读11纯文档，source pin仅出处数据，不授读源码。current-disposition、R1勘误和两份事实正文共同解释结构化目录；不追其索引、reader/checker、报告/proof/log、历史missing-definitions、产品/helper/resources/锁或任何actual/expected。14件T03完整v3与6件feeR4纯提案保持既有授权和原字节，不把它们当实际运行/费用/capture证书。

api-layouts的top-level ID恰12，追加return records15；“13API”历史口径不造第13或推缺API。field-codec-bridge精确列52个目录、263字段条目：12 API及其6嵌套目录、9 annotation目录、15追加记录、7段prose完整给出的helper字段目录、3种selectedFact source分支。每条保来源pointer、原注解/默认表达式、适用实例规则、owner、保全落点和缺件；注解不冒运行校验或原codec采用。Variable/Triple/Comparison/RuleSpec/BindingMatch等正文仅指向禁读索引，未给完整目录的类不据17计数补造；Number/Calendar等未给逐字段类型处明确null未知，不凭字段名猜bool/int。

## 精确DTO责任与消费顺序

新proposed-export-grammar所有定义都标 NEW-PROPOSED-NOT-ADOPTED，格式i05-canonical-interface-dto/1-proposal；不是旧产品wire，也不是既有carrier2/stream2已自动采纳的layout。它给未来owner/root审议的确定容器、精确required/类型/状态/顺序和摘要域，但不能凭新通用ClosedValue把原object/未细化tuple/dict变成封闭旧schema。

1. 后继caller先按既有门取得真实规范/源/consumer/collector/layout/根/不可变build票等批准；当前actual缺件不启动。root新接收的六键identity policy只确定receipt.runId来自先登记caller attemptId、child runId仅首受信context的角色与链接；本文只引用该精确pin和收件事实，不读正文，不把它推为其他30字段或实际registry/collector/权限通过。
2. 保完整实际raw与每个已返回原件，再按显式来源/API/codec分支选字段目录。API dict outer已知key可全列，嵌套sources按asserted/rdfs/rule分别保kind/basis/rule/inputs；是rule，不改ruleId，也不给asserted补basis。依赖类目录不足、真实新增字段或额外分支一律保已有原件并阻断完整DTO，不静默裁字段。
3. 原byte字段全部单独保全与RawSHA回核：payload_json/rows_json/source_encoded/definitions_encoded/catalog_json、material四种preimages/definition_material、所有wire/native_result/catalog/definitions/allocation、restore/capture/direct receipts及retention_owner。ProfileComputation14、Explanation继承15（version原位覆盖、direct_receipt尾加），不能只取子类本地两项。ReadonlySequence.native_kind与items都保；RootRef5字段，kind只str无enum，后四可空；默认表达式不求值、不用于补未观察actual。
4. 每字段slot区分已采用adapter的实际导出、仅保原bytes、layout-blocked、not-reached。actual None用新NoneValue；false、空tuple、未观察/未到达和阻断不是同一值。无专用旧byte wire时明确不存在，不能把新DTO重编码冒旧metadata原件；未知live object没有原bytes/获批adapter时，只能明确不能完整导出并请求owner，在未来获准生命周期内保真实引用。不能用repr/str、通用反射、getattr或__dict__补洞，也不能声称“raw存在”即已保住未知对象全部语义。
5. 原摘要和旧wire分别验证，再按后续被批准的具体adapter检查字段/类型、双方wire、共享identity域与其余exact；完整比较仍需原matches语义和独立oracle。目录完整、byte完整、原语义兼容、同issue/source权威、业务正确分别判定，不连带为true。当前全实际门false。

## existing codec 与新出口绝不合并

legacy source是内存四键dict，provenance13/result5完整保留；没有在_source定义专用metadata byte wire。material _project/_encode是既有input codec。production _ProfileProjection是recordType加原字段平铺；probe _typed_value是完整模块名recordType加嵌套fields。前者bytes用hex、后者base64，int有各自integerHex；tuple/list两者都投影为array，不能从旧array反推native kind或自认无损round trip。17类计数不提供未给出的全部字段/注册/标签语法。

新SequenceValue明确list/tuple、新RecordValue明确exact owner adapter，是NEW出口可审提案；它不重定义旧ReadonlySequence.native_kind:str，也不自动允许所有旧dict为string map。每个实际旧record的目录、类型、codec和exact-class安全访问方式仍由Q01–Q04补齐并采用。ProfileFailure._safe/property、Restore/Direct/SemanticError与未定位OfflineAccessDenied不得任意反射或泄私有异常文本；公共ErrorFrame仍四键code/messageKey/params/retryable，私有diagnostic与location四字段另域。

## 原摘要与关系摘要

digest-bridge逐值保16原配方，并加已收到catalog/canonical_string/IMPLEMENTATION事实。scope JSON紧凑排序UTF8但没有显式allow_nan=False，不能把profile严格选项追认成旧scope原参数；也不把该未显式选项扩成任意JSON语言。原source/view摘要用完整排序N3 triples，selectedRules保canonical Rule id/when/then。canonical_string只对无language XSD.string作已记的窄处理，不改numeric/date/language拼写，不运行RDFLib或helper。

profile text input保原UTF8；records/source/definitions/material各自原preimage分开，payload全七键、wire四键与原catalog bytes分别保RawSHA。rows按完整payload解码后的8192 Python字符切，末片不可丢，不是8192 UTF8 bytes。手工例8194字符分8192+2，首row字节16385，仅字面数学，无API运行。

IMPLEMENTATION只有已知三键声明；dependencyLockHash表达式未求值，不跟LOCK_FILE、不填实际哈希；semantic_identity选择finite6/7/8的覆盖事实也不是producer/保存结果认证。图label原摘要不删，display contentSource与新的关系摘要独立，不反喂旧helper。

新增关系hash仅 NEW supplemental：固定ASCII前缀ontolearn/i05/canonical-interface-bridge/1-proposal、一个NUL、C(relationCore)再SHA256，C为无float的严格紧凑排序UTF8 JSON。core仅dtoFormat/recordId/factBasis/originalBlobRefs/fieldStates/bridgeState，排自身digest及未来carrier/manifest/receipt/process；原bytes先固定再DTO/关系，再carrier2/binding2/完整manifest/后出receipt3，无循环。此hash不替任何原digest，不证明同issue/issuer/权限。

## 未决接口与明确接线前置

authority-and-requests Q01–Q09列最小owner纯材料：缺失helper字段/17注册、object/tuple/dict闭合值语法、三种旧codec、各class新adapter采用、原N3/preimage依赖、既有same-issue/live verifier、实际caller/collector/layout/根、source/预算/运行许可、精确安全异常/公共catalog。只向root请求既有批准纯接口；若无则先明确新设计与接收，不追源码、actual或费用WIP。

prepare→project的本地原引用/字典相等及内部一致性检查已知，但源码明确不认证真实性；frozen dataclass不冻结内部Graph/dict。parser _issue_context不是已批准legacy verifier。必须另外有实际source/handle/owner/witness/lifetime/图域接受事实，完整bytes或session字符串不能创造权限。

未来接到carrier2需joint owner/root明确新codecId/layoutId、逐API原件与DTO关系、完整runtime manifest文件、同attempt/raw/不可变build票和原caps计账。本文不改strict18 header、四schema/1241或旧R2 null字段；未知codec旧decoder拒绝，不跳过。新编码开销与全部原件须获capture/admission预算采用，不靠旁文件绕cap、删preimage或增加物理权限。若需字段/版本变更，另出精确pointer和双向拒绝delta交原T03，不在本窗改产品。

本窗最小静态验收只核文档目录/字段/引用/字面摘要和手工例，不重跑383源检查、模型/RDF/fee算法或旧产品。一次作者docs脚本语法失败在任何语句执行前发生，实际exit1及初始工具流边界保留；不得用后续静态成功覆盖。新候选固定后交root指定独审，原176与旧覆盖事故历史保持原样，actual/full417/wholeOracle/父137/JobStorewholeH/SQLiteHOLD/平台真人/指定双审/CI/develop等原门不关闭。
