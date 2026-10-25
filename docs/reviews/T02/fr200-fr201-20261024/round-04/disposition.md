# T02 fresh R04 全部意见处置

受审实现为 `cb8c9b7a5d780544b2910901ec9141236905d65c`，base 为 `583c05c7870ba0f8f642e3eeea1d0590e5859ca2`。两指定模型均自然完成并给出本范围附条件通过；这不是无条件发布通过。原稿与更正版本见 [归档索引](artifact-manifest.json)。下表保留14个原意见位置（含撤回和未确认），不将其称为14个已证或已修缺陷。

| 原意见 | 处置                                 | 依据及实际动作                                                                                                                                                                                                                                      | 责任                  | 原源码定位                                                                         |
| ------ | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------- |
| Z-01   | 未确认观察                           | 无ORDER BY的源码事实可采；无构造性用户反例，不计已证缺陷。原作者已收紧措辞。                                                                                                                                                                        | T01                   | storage.py:1212-1215,1147-1173                                                     |
| Z-02   | 原作者撤回                           | 43692仅capture分页信封；没有capture(document)。撤回错误反例；validateV2整文档262144与16MiB manifest预算独立保持。50K完整GUI未构造/未运行，不接受静态估算为实际通过。                                                                                | T01/T02               | index.ts:989,1033,1038;v2.ts:311-315,445-461                                       |
| Z-03   | 采纳OPEN非阻断延期                   | manual/edits修复不闭合definitions.triples的所有早期异常；维持D8第24行原wire OPEN，由共享维护者接线原始triples/Agent前另行处理。                                                                                                                     | T01                   | domain_changesets.py:448-477;storage.py:1125-1129                                  |
| Z-04   | 部分采纳OPEN非阻断延期               | ownership缺类映射及通用无定位边界保留；不能说全部ownership返回INTERNAL_ERROR，_application会构造OWNERSHIP_CONFLICT。不得只补码或伪造detailRef，需保持真实witness/显式无定位合同。                                                                   | T01/T02               | storage.py:57-64;job_store.py:607-636                                              |
| Z-05   | 采纳非阻断延期                       | UI17与契约26交集10、额外7、缺16。缺集真实，但不认定全当前方法可达/不可达；后续接线按真实可产生码集同步。                                                                                                                                            | T02                   | mainline-session.ts:86-104;errors.json.codes                                       |
| Z-06   | 现有政策继续；可选政策变更待用户     | 基线ADR27已要求canonical精确输入且无diff。语法合法和可按字面提交分开；不把prompt/本报告/ROOT解释当新human决定。ROOT已明确该可选澄清不新增当前合并前置。                                                                                             | ROOT/用户             | ADR-0002-storage.md:27;D8决定单:13,40                                              |
| Z-07   | 采纳信息级建议                       | job_store2993/storage1887/e2e1748为实际行数；行数不等于正确性缺陷，未来按模块职责评估拆分，本轮不改源。                                                                                                                                             | T01/T02               | 固定cb8源码行数                                                                    |
| M-01   | 采纳文档记录缺口，按ROOT授权本次完成 | 新建docs/reviews/T02/status.md并在docs/m0-checklist.md引用。准确区分已验阶段、两方附条件非阻断与待remote/未合并；不改M0既有验收或中央三状态文件，不增加2/17。                                                                                       | ROOT                  | docs/m0-checklist.md;docs/reviews/T02;AGENTS §6                                    |
| M-02   | 核心前提不采；不删除审计原件         | uv.lock正式rdflib package段258已有SHA99fab7bd…/size2379774，不能用metadata73行得出无hash/无机制报警。历史wheel及upstream保留审计/repack来源，不采删除建议。压缩方式以ZIP元数据为准，本地3为STORED(0)，upstream为DEFLATED(8)，日期列不能作压缩证据。 | T03/T01；ROOT确认处置 | uv.lock:250-259;repack-rdflib-input-types.py;PROVENANCE.json                       |
| M-03   | 部分采纳未来边界覆盖建议             | 可接受补4299/4300应用边界的维护建议；4301已有真实new/edit及typed拒绝覆盖，不能说整个分类评估缺失。相同INVALID_REQUEST由既有canonical策略成立，不是当前需求违规；不改cap、不自动补测。                                                               | T03/T01               | test_mainline_language_input_rejection.py;notation3-input-types.patch              |
| M-04   | 保留既有OPEN；限制修复建议           | standalone EOF残余按原HOLD保留，term补点的当前输入面不可据此外推故障。不得泛捕所有IndexError为受控；未来若授权仅定位明确抛点类型化并保未知parser/Store/HOLD。                                                                                       | T03/T01               | rdf_snapshot.py:38-45;原EOF披露;D8:40                                              |
| M-05   | 部分观察；不采definitions已受控因果  | 474-477仅包supported，不包471 transactions.preview，不能证明所有definitions异常已受控。92例未触broad分支不是穷尽。未知解析失败保持HOLD是原约束，不采一概映射受控建议；原wire OPEN继续。                                                             | T01                   | domain_changesets.py:464-477;storage.py:_definition;D8:40                          |
| M-06   | 维护建议；不认定当前缺陷             | schema约束hash形状、引擎守内容身份是既有分层；当前唯一Store.commit写入口且已有真实Python Store/TS金向量测试。不能据此称无双端可测或当前可绕过；不添加编译器不支持的schema keyword/第二写入口。                                                      | T01/T02               | storage.py:484-494;schema.json;tests/unit/t02-manual-fact-id.test.ts:81-90,123-133 |
| M-07   | 信息级兼容性建议；不直接改导出       | 桶导出三模块是实际组织形式，但无当前同名冲突反例。切./v2到单模块会改变既有导出面；任何未来清理须由共享唯一维护者核消费方兼容，本轮不改。                                                                                                            | T01                   | packages/contracts/package.json;src/design-v2.ts                                   |

## 处置与验证边界

本次唯一落实的新增动作是 M-01 的纯状态文档与引用，以及审查归档、索引和证据桥接。其余建议按事实不采纳、部分采纳或按D8原负责人延期；没有修改实现、测试、配置、依赖、锁、预算、验收标准或包。

Z原作者已撤回43692 witness字段限的错误因果、将排序问题改为未确认，并把提交数26／5更正为27／7。末次限定明确仍受262144整文档保守预算与16MiB manifest等约束，未构造／运行50K完整GUI。静态50K替代估算不作为实际通过证据。Z初终稿54252B、首更正61900B与最终66144B均保留原字节和hash。

M原78500B报告不改写。其“path wheel无hash”遗漏uv.lock正式package段258已有哈希；压缩方式应以ZIP元数据区分本地STORED与上游DEFLATED，日期列不是压缩列。后置supported catch不覆盖早期transactions.preview／Store.commit／_definition，不据此关闭原definitions wire OPEN；既有跨语言Store金向量也不因该报告遗漏而失效。详见两份独立只读处置核验。

原生engine退出UNKNOWN、named App退出UNKNOWN、unknown parser／N3／Store／坏快照／损坏SQLite保护、容量与旧失败库恢复、签名／公证／法律／_distutils／跨OS／参考设备等独立HOLD不解除。旧0e7／O027／093／text001及各控制首败保持；新绿不转移或覆盖旧失败。

既有ADR-0002第27行canonical政策继续生效。可选的未来混合大小写提交政策确认，不新增当前合并前置，也不表示已收到新human批准；改变政策须新候选门禁。

MiniMax §12.3要求逐项处置或ROOT显式接受、HOLD保持、同head实际check／GUI／包内验收齐全。七份ROOT接收原件与本轮双审、处置一并交ROOT核验。本证据提交不代ROOT确认全部条件已满足，不授权push／PR／CI／merge；当前整体合并可用仍2/17。
