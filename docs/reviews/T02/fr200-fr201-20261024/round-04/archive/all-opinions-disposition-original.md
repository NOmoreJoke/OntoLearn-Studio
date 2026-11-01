# T02 cb8c9b7a fresh R04 全部原意见事实处置

两方真实结论均为本授权范围有条件通过；不是无条件发布通过。ZCode原稿与两份原作者更正自然终稿、MiniMax原稿均封存。此处只作逐意见事实处置，不修改两方结论、不把Fail改Pass、不通过源码变动规避审查。14个原意见位置逐项如下，包含已撤回项/未确认项，不能称14个已证缺陷或已修复。

| 原意见 | 处理状态 | 依据与动作边界 | 责任 | 源码/材料定位 |
|---|---|---|---|---|
|Z-01|未确认观察|无ORDER BY的源码事实可采；无构造性用户反例，不计已证缺陷。原作者已收紧措辞。|T01|storage.py:1212-1215,1147-1173|
|Z-02|原作者撤回|43692仅capture分页信封；没有capture(document)。撤回错误反例；validateV2整文档262144与16MiB manifest预算独立保持。50K完整GUI未构造/未运行，不接受静态估算为实际通过。|T01/T02|index.ts:989,1033,1038;v2.ts:311-315,445-461|
|Z-03|采纳OPEN非阻断延期|manual/edits修复不闭合definitions.triples的所有早期异常；维持D8第24行原wire OPEN，由共享维护者接线原始triples/Agent前另行处理。|T01|domain_changesets.py:448-477;storage.py:1125-1129|
|Z-04|部分采纳OPEN非阻断延期|ownership缺类映射及通用无定位边界保留；不能说全部ownership返回INTERNAL_ERROR，_application会构造OWNERSHIP_CONFLICT。不得只补码或伪造detailRef，需保持真实witness/显式无定位合同。|T01/T02|storage.py:57-64;job_store.py:607-636|
|Z-05|采纳非阻断延期|UI17与契约26交集10、额外7、缺16。缺集真实，但不认定全当前方法可达/不可达；后续接线按真实可产生码集同步。|T02|mainline-session.ts:86-104;errors.json.codes|
|Z-06|现有政策继续；可选政策变更待用户|基线ADR27已要求canonical精确输入且无diff。语法合法和可按字面提交分开；不把prompt/本报告/ROOT解释当新human决定。ROOT已明确该可选澄清不新增当前合并前置。|ROOT/用户|ADR-0002-storage.md:27;D8决定单:13,40|
|Z-07|采纳信息级建议|job_store2993/storage1887/e2e1748为实际行数；行数不等于正确性缺陷，未来按模块职责评估拆分，本轮不改源。|T01/T02|固定cb8源码行数|
|M-01|部分采纳流程建议；交ROOT|T02/status.md及m0清单FR条目缺失的事实交ROOT统一状态维护。当前T02未合并，不能提前标已交付；本T02不改中央状态或在冻结候选新增文档源叶。|ROOT|docs/m0-checklist.md;docs/reviews/T02;AGENTS §6|
|M-02|核心前提不采；不删除审计原件|uv.lock正式rdflib package段258已有SHA99fab7bd…/size2379774，不能用metadata73行得出无hash/无机制报警。历史wheel及upstream保留审计/repack来源，不采删除建议。压缩方式以ZIP元数据为准，本地3为STORED(0)，upstream为DEFLATED(8)，日期列不能作压缩证据。|T03/T01；ROOT确认处置|uv.lock:250-259;repack-rdflib-input-types.py;PROVENANCE.json|
|M-03|部分采纳未来边界覆盖建议|可接受补4299/4300应用边界的维护建议；4301已有真实new/edit及typed拒绝覆盖，不能说整个分类评估缺失。相同INVALID_REQUEST由既有canonical策略成立，不是当前需求违规；不改cap、不自动补测。|T03/T01|test_mainline_language_input_rejection.py;notation3-input-types.patch|
|M-04|保留既有OPEN；限制修复建议|standalone EOF残余按原HOLD保留，term补点的当前输入面不可据此外推故障。不得泛捕所有IndexError为受控；未来若授权仅定位明确抛点类型化并保未知parser/Store/HOLD。|T03/T01|rdf_snapshot.py:38-45;原EOF披露;D8:40|
|M-05|部分观察；不采definitions已受控因果|474-477仅包supported，不包471 transactions.preview，不能证明所有definitions异常已受控。92例未触broad分支不是穷尽。未知解析失败保持HOLD是原约束，不采一概映射受控建议；原wire OPEN继续。|T01|domain_changesets.py:464-477;storage.py:_definition;D8:40|
|M-06|维护建议；不认定当前缺陷|schema约束hash形状、引擎守内容身份是既有分层；当前唯一Store.commit写入口且已有真实Python Store/TS金向量测试。不能据此称无双端可测或当前可绕过；不添加编译器不支持的schema keyword/第二写入口。|T01/T02|storage.py:484-494;schema.json;tests/unit/t02-manual-fact-id.test.ts:81-90,123-133|
|M-07|信息级兼容性建议；不直接改导出|桶导出三模块是实际组织形式，但无当前同名冲突反例。切./v2到单模块会改变既有导出面；任何未来清理须由共享唯一维护者核消费方兼容，本轮不改。|T01|packages/contracts/package.json;src/design-v2.ts|

所有建议均不在本冻结候选直接实施。原作者纠正只改本方报告，原54252B与61900B两版不覆盖；末次66144B版本明确无43692 witness字段界、仍有262144整文档预算及16MiB manifest、未实测50K GUI。其静态替代链不作为实际运行证据。其余无法确认/容量/原native engine UNKNOWN、named App UNKNOWN、parser/N3/Store/坏快照/损坏库物理保护、签名/公证/法律/_distutils/crossOS/reference设备等独立HOLD均不解除。

MM附条件第12.3节要求逐项处置或由ROOT显式接受、保持HOLD、同head实际check/GUI/包内验收；这些同版运行已由七份ROOT原始接收票承接。本次不复跑产品、不新制造包。逐意见处置与原报告一并交ROOT审结，不先行宣称合并条件已全部满足，不push/PR/CI/merge，整体合并可用仍2/17。

事实勘误另记：Z原计数26/5已由原作者更正为27/7；M清单对“无2000行引擎文件/最大storage”的未核断言不采，固定cb8 job_store2993。M的库纯计算探针/临时tsc编译与委派证据重算按其原稿自报保留，不冒作开发方重新执行，既有raw重算不等于新的GUI/包内运行。
