# O 15项静态triage与最小修复计划：独立技术审查

**限定 Pass（最小owned修复计划的静态技术可执行性）。** 初审发现recorder实际输出目录未列入精确写面，以及F04规范单行定位偏移；root已修订计划、矩阵和格式回执，本人delta复核后关闭两项。当前没有剩余需先修改的计划阻断项。本结论不代替实施授权、运行验证、新候选双指定审查或任何父门，也不使15项原外审意见自动关闭或降级。

## 独立核验范围

全文阅读本目录6件输入：计划、15项矩阵、owner证据、文档格式回执、F06/F12两份专项报告。三个JSON完整严格解析；逐项将15个ID、原严重度、原标题及section SHA与 `5168c1480a8548217202e134073b507fd77a26ab` 保存的44941B final-v2原文核同。没有把静态反证写成指定reviewer改判；矩阵15条均implementationDone false、externalReviewerOpinionClosed false、originalOpinionPreserved true。

只读owner工作树相关固定源码/规范。合并owner证据18项、F06表10项及F12表16项的重叠后，共40个不同文件，独立以当前字节、`git show 77852d27a3c4e84867a42f243e0f4e0f32b8df67:<path>` 和 `git show 86df64a2c707355ed177d536ef5975a1986c0f0b:<path>` 比较，40/40完全相同，bytes/SHA与所列声明相同。该比较仅是40项身份核验，不声称全文逐行重审40件或全工程无变化。

实际进一步读取builder、self-test、recorder、私有field policies、allocation规范、JobStore/Storage/Coordinator/Memory guard及I01/I04验证链的相关代码位置；使用标准库JSON完整解析、集合/数组相等和AST literal抽取复算有限数据。不import或执行builder，不运行产品、测试、Pytest/npm验证、网络、GUI、Goal，不进入两份外审树或本机native/DB；没有源修复。唯一写入本报告。I01历史运行及每个历史候选的实际结果未由本次重新验证，不把专项报告的历史归档说明提升为新运行证据。

## 可执行性意见及处置

### PLAN-01：recorder真实输出目录与精确写面未闭合（初审P2，已关闭）

初审计划列出builder/self-test/recorder/field policies/五件制品及新 `O-owned-repair-candidate/` 为拟写面，并把真实验证流放新过程目录。现有 `docs/reviews/T05/source-package-oracle/record-command.py:20-21` 却固定创建 `docs/reviews/T05/source-package-oracle/commands/<tag>/`，`:26-32` 会写invocation、stdout.raw、stderr.raw和result。W3原文只拟增加版本和env字段，没有定义输出根变更，也未列这个新增commands目录。

若后续直接调用该recorder，便会产生未明确列入计划的写面；如果绕开recorder手工写candidate目录，又不能仅凭修改recorder证明新的记录功能已实际使用。已及时向root反馈：在计划中明确只新增的精确commands tag与旧记录保护，或显式设计新候选输出指向candidate目录；本次不要求改源码或执行命令。

root已在精确写面第6项列出默认commands根下仅新增 `o15-owned-candidate-<action>-<attempt>/`，action只build/test/check；首次01，必要复测递增，保首失败与旧tag。首轮三个精确目录均符合现有recorder的64字符/字符集限制。新第7项candidate目录只保上述流的链接/bytes/hash，其他另获准完整检查日志放candidate目录，不再假称recorder默认输出在此。矩阵F11同步补充，当前recorder源码仍为1933B/SHA `261842d5d6ced67fa3f25f7ff590edab4b4c8f58eb778587e3da2ee2bf3aa91d`，没有先行实施。这已消除拟写面与现有行为的歧义。

### PLAN-02：F04规范数值精确行号偏移（初审P3，已关闭）

初审矩阵F04的evidencePointers写 `allocation-integration-plan.md.raw:78`，但固定字节的七池值位于L76；L78是预留政策与保守边界。计划正文采用72–80整段，数值本身与AST literal一致，所以这不推翻triage或关系断言计划，但应把精确指针改为76，避免实现者从错误单行提取常量。restore规范七值位于L103，103–105引用范围可用。

root已将矩阵精确指针78改为76，计划正文72–80保持。本人核固定字节L76包含七值、L78为预留限制，修正与源相符；其他15项原意见标题/严重度/section hash和未关闭状态没有改变。

两项修订均已进行完整反向delta校验：将最终计划新增第6/7项恢复成原第6项，可精确恢复初版12382B/SHA `d38f63761a280ca2ded182786380bb9da4a5c5fa3c8e77ae621b69214bf5cc51`；仅反转矩阵F04指针与F11补句，可恢复初版17519B/SHA `b1cb4a541c412fa016f3148260381a06607bbb2adf927083490594d339ff330c`。格式JSON保首check exit0并追加修订后check exit0与findings/resolution，after三件bytes/SHA与最终文件一致；反转这些明示回执增量亦恢复初版2373B/SHA `44392c7b89f99b64fb2d64a9066eef56c06f4393f1a8283a36a65846c9bdb61d`。本人没有重跑格式工具，确认的是已收回执与字节绑定。

## 15项技术计划核对

| 项 | 独立核对与实施边界 |
|---|---|
| F01 | decoder L249重置计数、L265–275产生list-N，跨解析合并入口确有潜在碰撞面；field policies L9/私有FIELD_POLICIES仅批准shape-list双射且不准data blank。计划用角色/有限语法guard及未批准合并拒绝，保现有shape-list合法域，优于发明新全局blank ID；不得把顶层括号扫描当嵌套语料全部无BNode的证明。该扫描在owner证据已明确只是hint。 |
| F02 | 测试L368只遍历golden[2:11]，比较conforms及适用的完整六字段violations；13个golden与17个C观察ID复算一致。计划补精确case/分支/字段消费账合理；六字段断言不能被误述成只比两项标量，reason/currentEntryGap/derivation/entryAndReport等说明不能当安全错误码或把旧红项自动写成当前pending。旧原新标题均9/13，8条未覆盖observation是另一维度。 |
| F03 | builder L1083读取并pin explanation金标，expected_sources没有接其语义映射，作者身份与被消费须分开。保原件/pin，有同输入同语义映射才断言，否则reference-only并说明原因，能避免为制造消费强接同名但不同输入golden。不得扩417或由actual补预期。 |
| F04 | 独立AST literal七值等于两段规范；DOC_PINS及construct L1077–1080已拒规范字节变化，所以原“规范改动不会失败”过强，但并未证明常量与规范语义关系已有断言。计划加独立规范行↔七值关系合理；input/output别名明确映射，不import产品allocator或称实际Budget已证。 |
| F05 | 独立JSON复算sources26行、26SHA、14ref；sealed observations的不同origin记录111项，唯一未进source rows的ref为523c478d…，与owner证据相同。builder L1035已明确expected authority与input origin不同。分local身份、input lineage、expected authority/consumption和规范角色合理，不要求任意两表互为子集；lineage只能引用sealed literal，不能读取producer/actual算法增补expected。 |
| F06 | 独立遍历复现288项/25观察，全部在rawTermSourceOccurrences，25份完整数组与sealed datasets.records精确相等。公共schema有66个defs且无这里的RDFTerm定义；规范表示与五键raw为两个私有域。builder L823–825/L849–851保原records，现validate_oracle没有该raw逐项专用绑定。W2只补O私有exact keys/type/path及完整raw关系，保null/空串/language原写法/顺序/multiplicity，不能扩public schema或将raw作为规范身份第四分支。未证明消费者实际失败。 |
| F07 | scope_expected L792确有next；当前三个scope观察matches为0/1/1，每fact head occurrence最大0/1/1，原完整matches/whenBasis仍保。计划在有限单basis域核完整关系、对未来多独立basis先拒绝等独立合同，未擅自承诺all-proofs union。当前未触发不能反证机制普遍正确，也不能据此静默关闭原意见。 |
| F08 | source-identities不在DOC_PINS，L1213只解析；main L1297–1299仍会发现生成sources与提交字节不同。早期身份拒绝与输出可复现检查是不同门，计划补独立pin合理；不能称现有--check完全不覆盖任何身份编辑。 |
| F09 | sourcePath是历史地址，local为现存固定副本；26行既有SHA、14行有ref，不可把历史path不在HEAD直接当缺陷。反过来也不能用local内容hash认证所有历史producer身份。计划规范角色、明确缺ref/缺原件，且不伪造同名替代品，足以保持此边界。 |
| F10 | 固定输入强pin后再解析索引；代码中dictionary/list下标对未批准索引会KeyError/IndexError。计划显式family索引集合与ValueError、任何产物写入前失败，避免把非法未知索引伪造为pending成功；保原417、原合法值输出。负例应针对这个有限拒绝域，不把guard变成新规范业务支持。 |
| F11 | recorder已将sys.executable放入argv，但没有实际版本字段。补新运行的version/version_info/executable及必要env白名单合理，不改旧合并流，不做无变化双解释器对照；产品3.12与外部stdlib工具运行分开。输出落点需按PLAN-01闭合后再实施。 |
| F12 | I01健康实际L51–69发送非UUID旧id、v1且缺kind/session/params；Coordinator L168先拒id，L176再核字段，L187核版本，hello/session及能力位置亦不同。所核npm/CI/I04/pytest发现等7个执行链文件未调用该脚本，I04验证器自身明确跑resident/worker测试。仅支持“已核执行链无调用、当前特定依赖未证”；不能删149/改历史脚本或回开v1。O文档标历史适用ref与当前限制是最小处置；root若提供当前必须执行需求，再单独指定维护者新候选适配并保S1原要求。不是自动撤掉中级意见。 |
| F13 | commit_job_round L802先要求running/rounds，L836只增加stateVersion，状态名未变；现有测试定义锁2→3→4→5并取消到cancelled。静态未证绕过cancelling→succeeded状态边。保持原候选意见，由root必要时唯一路由T01核合同，本T05不写JobStore/states，避免因报告推论越权改共享实现。 |
| F14 | Storage两处Conflict确含原值诊断；Coordinator.classify只取code/params，JobStore._application持久化固定类别/授权身份并返回uuid detailRef。未证跨边界文本泄漏，不能为假想未来caller扩大修复或新增原值日志。root必要时路由唯一T01维护者，T05无共享源写面。 |
| F15 | memory_guard模块已明示Darwin非硬限/可过冲且不批准业务native工作负载；Coordinator L443–448确有Darwin父RSS采样兜底。可纠正原报告反述并保平台限制，不量化未测过冲，不改native/内存保护、不扩到OS/SQLite/wholeH；留既有I04 owner。 |

## 计划的实施与再审门

现计划把事实与未来实现/验证分开：矩阵没有completed或外审closed，原NotPass不因历史适用、当前闭合语料或静态反证下降；137 pending、26 allocation与原输入/golden保持，真实业务错误需逐项报root，不能为刷绿硬保错误数字或悄悄换expected。

W1/W2/W3的拟源写面限定在O自有builder/test/recorder/field policies及五个正常生成输出；旧ref、两审树、public contracts/JobStore/Storage/Coordinator/Memory guard/历史I01脚本、产品源/actual/collector/adapter均明确排除。F12历史适用性只写O说明；F13/14/15由既有唯一owner决定，不给并行维护者抢写。

实施后正常build、两条O门、新真实分流记录及适用完整仓库check均是未来验证计划，本次没有运行，也没有创建新候选。生成五件实际delta、417ID/顺序、320输入及原golden字节、业务expected/参数/context变化须可审查；不提交无变化coverage/budget-gaps假delta。独立复核通过后再冻结新SHA，完整工程同版全新ZCode/GLM-5.3最高思考与MiniMax/M3.1-Flash/xhigh两新任务/独立树，不沿用旧Z Pass或本轮M终态。PRD原缺两区、两allocation guidance全文及两锁文件条目级审查这五个静态缺口门都保留；大JSON解析与逐行源码阅读仍分列。该要求没有扩成额外父门或产品总体判断。

## 实际检查与局限

本次JSON/AST/字节/静态链检查通过；F06完整raw关系、C13→17 ID、26/111来源账、七池literal、scope 0/1/1已独立复算，未调用任何受审函数。40件current/source/process身份相等检查只用于本计划定位。格式回执只覆盖其中三件新owner文档，不证明源实现/运行正确；专项原件不需为本轮格式化重写。现行脚本执行链的“无I01调用”限定于所读文件，未证明仓库外/未来人工命令绝无依赖。

最终计划可按其精确owned写面进入root后续实施核定；PLAN-01/02关闭只涉及计划准确性和可执行性。W1/W2/W3没有实施，验证没有运行，新源码候选未创建；指定模型原NotPass及全部15意见仍待新候选和正式门禁处理。本次没有作额外父门或产品总体判断。

## 最终6件输入指纹

6 inputs, 68968 bytes; fingerprint `168dbd679b66d037a531bf74fdb1e19cd2a1bbd393707f9ad1df0ce87f6a46c9`. Algorithm: sort by filename, concatenate UTF-8 `name<TAB>bytes<TAB>sha256<LF>` for all inputs, then SHA-256. This review and any later delivery manifest are excluded.

| Input file | bytes | SHA-256 |
|---|---:|---|
| `all-15-static-triage-matrix.json` | 17689 | `b6777fa496c0d4bf5e505f4a822f19442deddf36e7395e3b0f2c20f5b744a91c` |
| `document-format-verification.json` | 3470 | `e5d9b5d5d0aafd3880e2b18da88ac9ae9f689b58af9fc2a70b5896bbb91827bf` |
| `f06-domain-review.md` | 12022 | `f3ed9aa8fed211ecb7678fa2b70db18c8862d01b958f8dd7ab0f70afb6c5ffd1` |
| `f12-history-dependency-review.md` | 13907 | `24d040f948dc278d99c899b9b17849b2b3b3130c611df0f0dd81e702b5e943e0` |
| `minimum-owned-repair-plan.md` | 12978 | `de89f35dee8ab2d9a13ebe25d5aff7f1b02013728e1cdd919739bb765a1bf290` |
| `owner-static-evidence.json` | 8902 | `68b9920ce2e268e74f4cd4d311d19c77aa81085d4637a8e1322943a332f1502d` |

