# MiniMax O15 原 turn 终态与原报告独立收件复核

2026-10-23，上海。**原 turn 正式 completed、原稿保全/原生写入链核验通过；原稿结论必须收为 A 九文件 delta 条件Pass、B 150全工程NotPass、C运行/打包/生产无法验证。** 本独审不将它替换为整体通过，也不签双指定对通过或父门。原稿有下列内部计数/表述错误和无法从当前原生片段独立复验的阅读/执行链，须连同原稿保留，不能只摘 A。

本次全文读取了548行原报告，仅做收件/证据边界复核，没有产品重审、GUI、oracle/observe重跑、另建模型任务或读取另一方本轮报告。

## 1. 正式终态、源与副本、原生写入

唯一SID `mvs_c28510d4b96a4ecbaea7be3f838c5110`，原turn `677c3d52-3d00-45ec-96af-2005b0a71d58`。独立以已核runtime数据库URI mode=ro、timeout1、PRAGMA query_only=ON，仅执行preservation中的固定SQL并参数化这两个标识，核到：terminal_outcome=completed，updated_at_ms=1792695033165（2026-10-22 18:50:33.165Z）。没有扫表、改journal、使用immutable或用子任务终态替代原turn。

源为 `T05-O15-minimax-review-b88be226/docs/reviews/T05/projection-R3-receiving/launch-O15/report.md`，lstat非symlink普通文件。独立两读源=owner minimax-report-original.md.raw：**59291B / SHA256 `256f7af033f4141bea9b26cc0895272e39076beeec1f39f69eda2b52ce6f2ada` / 548行**。

原生链有1次Write+7次Edit，均为同一原turn的本方报告路径，公开toolResult均isError=false。独立按序重放到内存后精确等于以上源/副本，没有修改原稿：

- 初Write `call_WXq6ZUjiMiKTfaHg7fWBwimP`：当前messages的0基record122；结果message `msg-2N4cstFDar4pqjdMO-pbLY7tQOisSBCLxcXRZmuP594`。
- 7次Edit位于record127/129/131/134/136/138/140，结果分别record128/130/132/135/137/139/141；每次old_string在重放时唯一匹配，最终字节完整吻合。

公开final为message `msg-1eq4djJ_gq4NQ0y6XUXoi7xOVkPi09_Iar6g9P_NYJY`，同原turn，stopReason=stop，timestamp1792695017772；4044B / `18c15563ec14dad8af46d308c66ee2ec13fbb5c6cc5e097280c8df46f4f8e9ce`，等于owner保全的minimax-original-turn-native-final-reply.txt。正式runtime completed另于33.165Z确认，不把public final或文件写入完成单独当正式终态。

## 2. 结论、全部15意见与新增范围问题的归属

原稿A只给本候选9文件delta **Pass（有条件）**，B给完整150 scope **NotPass**，C给运行/打包/生产 **无法验证**。新范围问题被原作者称为既存、非本delta引入，不能据A把它们抹去；本收件审亦未独立验证这些产品问题的成立性或修复方案，须由root按所有权另行triage。

原15意见：F01–F11的实施证据被M判断成立；F12–F15保持implementationDone=false，认为归root/T01/I04的处置理由成立但事项开放。**全部15条 externalReviewerOpinionClosed=false / originalOpinionPreserved=true，外部流程仍open。** 137pending、26allocation pending、wholefalse及父T05/P0/正式JobStore/selected/wholeH/S1/B1/费用/两OS CI/真人/develop/生产门均保留。

新增范围问题按原稿完整列示，而不是把它们自动转为已证产品缺陷：

| 原章节     | 原作者主张                                                                    |
| ---------- | ----------------------------------------------------------------------------- |
| §8.1       | cancelling→succeeded契约边在产品调用组合中不可达                              |
| §8.2       | 三份共享金标未独立hash锚定，存在实现/语料锁步修改风险                         |
| §8.3       | 三个IPC通道覆盖缺口及路由表never签名校验问题                                  |
| §8.4–8.5   | 弱/数量断言、CSP违规集合和dev策略测试覆盖问题                                 |
| §8.6–8.8   | 错误码发射点、默认编码、队列/TaskView预算差异等有界风险                       |
| §8.9       | a–m共13项低/信息观察，含历史探针路径、归档豁免及边界说明                      |
| §8.10–8.12 | 纯schema与semantic层边界、归档副本不可本地核验、无受检键集及代理字符/体量说明 |

严重度和汇总的内部不一致另见§6，不在本收件审擅自改级。原稿的NotPass必须完整保留，不能只把A条件Pass发布为双审通过。

## 3. 150范围与五全文缺口：方法和缺证

原稿明确采用“本人逐行读核心+子线A/B/C/D”混合方法，子线输出只作证据。§3.4承认job_store.py/storage.py部分区段、entrypoint、i04_matrix_evidence.py后段等未读；若干大JSON以程序化解析/遍历读取，不能把150清单字节身份核验当作150实质阅读闭合。

五项全文要求原稿自述已读：PRD1255、两allocation159/249、package-lock6423（12连续段）、uv.lock240。但本次当前精确SID的messages首条已经是原turn:compaction的compactionSummary，history_artifact指向generation0 checkpoint；本审未复制summary/system/thinking。现存片段没有最初五全文Read和两O原始执行call，不能据此断言从未读取/执行，也不能反过来称本独审已经直接核到这些调用。

该已知session manifest声明的ledger/display/snapshot精确路径均不存在；ledger首次按声明路径打开得到FileNotFoundError后，仅stat其余两路径，没有glob、换其他会话或全局DB找历史。本项是本独审收件导航限制，非模型失败。根确认无额外已核压缩前路由，因此五全文的原始Read覆盖在本审只能保留为M自述/既有记录，不能伪造新native支撑。此前冻结dispatch的正式附件首turn输入链另已完整核回，不因后来的compaction被否定；该历史输入链也不能扩成普通命令执行链。

当前父原turn可核到四个相关task返回，status均succeeded：

| 子线task                                    | 当前父公开返回坐标（0基record）            | 本次证据边界                                                                   |
| ------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------ |
| C `bg_e2505937-31b8-4fe2-a0dd-c1376c4fd102` | call_JW9mV2bzoknz9A8XY6Ice5eT，65发/66回   | 返回truncated=true；父随后通过已声明tool-output文件Read分段消费，本审未追子raw |
| A `bg_68ba49a7-06f7-4add-b588-f24d9cb49a5c` | call_RZJrRKsVkmBv4RSQPH1cXWik，57发/58回   | 公开返回未截断；可核父收到了相关子结果，不代称子读完每行                       |
| B `bg_f4acfbc7-abab-45c2-9f3d-4cdd88193152` | call_cXcqAz7RIQozK2qDQE0abCm2，81发/82回   | 公开返回未截断；保留子结果自述的未读/未运行边界                                |
| D `bg_ed2e8118-7d71-4eab-8058-70f2b02090c6` | call_kAR5EpL7YT98WA5IRJ0PUjlL，125发/126回 | 公开返回未截断；仅核父公开投影，未查D子原流                                    |

子线输出/节点数量/完整parse可以说明方法，不能证明作者对全部文件的业务理解。报告承认的缺口与B NotPass一致，本收件不通过清单计数补齐阅读。

## 4. 两条正常O命令：原流可核，原始argv/exit配对仍有限

报告自述本方准确3.12.14 venv、cwd为本方worktree、TMPDIR在本方scratch，self-test与builder --check均exit0。owner已按原稿显名路径复制四原流；本独审直接核其当前本方源=owner副本、bytes/SHA：

| 原流                       | bytes | SHA256                                                             |
| -------------------------- | ----: | ------------------------------------------------------------------ |
| o15-test-oracle.stdout.raw |     0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| o15-test-oracle.stderr.raw |  8697 | `c0f7dbd8220f001985022901a5384973834ea1fd5a9e5e14147e77545c425e06` |
| o15-build-check.stdout.raw |  1001 | `030cabeee57f2adf1e3d03376c0f079e78a62e045c819b67f8241b356888bce5` |
| o15-build-check.stderr.raw |     0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

stderr明确Ran57tests/4.688s/OK，check stdout完整JSON为417/320、280specified/137pending、wholefalse及五产物固定hash。当前公开Bash `call_v6FxXi34XZg2tjztvGGaM3xA`（record87发/88回）又核过附件/工作树/原流hash，但它是后续静态读取，不是最初执行两命令的原始调用。

同一本原turn的公开task_query（call_DA4mSliXoqTx2JJhaf9eRXx3，record2发/3回）还包含已成功的任务卡片：bg_c0a612bd-d8d1-497e-be96-23cf04830aed，描述为Run the two authorized oracle commands，execution.status=succeeded/exitCode=0，output.rawBytes=1404/persistence=complete。它独立支持本轮存在该合并正常验证任务及成功状态，但原argv和两条命令分别的exit配对仍未在现段出现，不能从描述反推缺失的1404字节原输出。

因此本审可确认报告显名原流真实存在且内容/身份相符，**不能从当前compacted段独立证明最初argv/env/exit0的原生配对**；逐命令exit0目前归原稿自述、原流及公开合并任务状态支持，不假装是本独审重跑所得，也不以正常stdout、57OK或后续hash命令0替代原命令正式exit。没有为缺证重新执行oracle或observe。

## 5. 首失败、子线D自写验证器错误与实际设置

原稿§2.5自述在子目录以相对`.venv/bin/python`执行失败、exit127，随后改绝对路径读取成功。当前父公开task_query可核到真实失败卡片：call_DA4mSliXoqTx2JJhaf9eRXx3，record2发/record3回，精确task `bg_7c43a5df-9986-47fa-8def-9cd1d6a49c78`，描述Extract first-failure records and real errors，execution={status:failed,reason:exited,exitCode:127,message:Command exited with code 127}，output.rawBytes=55/persistence=complete。故127并非仅无依据的报告自述；但原始argv和55字节错误正文在当前段不可见，**相对解释器路径的成因及恢复动作仍归M自述，不能声称本独审已读那55字节原流**。没有追新路由或重跑，亦不将其归为产品失败。

D父公开结果提供了更具体、但仍是**D自述**的首错/恢复边界。精确call `call_kAR5EpL7YT98WA5IRJ0PUjlL`，task见上表，record125发/126回、结果message `msg-H7YWxfWoca0yNPILDXhdeZI4NBRlU06r44drtG3q4Ww`：公开text第14行认observationId/datasetId比较错；第26行认edit工具失败；第41–42行认JS Number()/cancelBoundary移植错误；第55行认scanner tuple/string key不一致；第234行声明修port不改data；第296行明确该semantic port不是TS运行时。owner保全的该D父公开返回44330B / SHA256 `1b2217117adb91d01d3f2815336521eb0473148121d2ca88157f00d9c7e6beab` 已独立比对与上述公开text的UTF8字节相等；它是父返回投影，不是子raw。它们说明自写checker须经修正，不能把首遍误报认作数据缺陷，也不能把最终port相等替代真实TS运行证据。本审未读取子raw，不能声称独立复现了子脚本每次失败/修复。

公开mavis me链可以直接核到必需标量：call `call_zyqRu6ISspc27T69eIhVTtPH` 的session get me（record112发/114回）返回SID精确、effective_model=minimax/MiniMax-M3.1-Flash、model.thinking.effort=xhigh。原稿权限来源是用户级配置，并诚实承认不足逐会话生效证明；本收件不打开config.yaml或复制其完整配置原生结果，实际始终授权归owner既有现场回执，不由全局默认推定。

原稿§10的“未创建GUI任务/setup only仍成立”只能解释本审查agent没有另建下游任务，不能否认owner已正式创建该新SID并派发；actualTerminal=null是撰稿时自身字段，不取代本次独立正式SQL completed。原稿不改，收件时双重归属须明确。

## 6. 原稿内部准确性问题（不改稿、不代改NotPass）

以下按原始548行行号：

| 原稿位置    | 原文/实据                                                    | 收件限定                                                                                                              |
| ----------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| L60 §1.2    | scope-contract写36691B；实际当前/冻结2476B，SHA757682e1…相同 | 字节数误报，不能当成换了scope或输入漂移                                                                               |
| L77 §1.3    | 称preflight内含1262条trackedPathMetadata                     | JSON实际只有trackedPathMetadataCount=1262，没有1262条tracked记录数组；该hash309823…确实匹配当前文件                   |
| L205 §4.1   | 目录数量36+27+22+16+15+5+5+2+12                              | 合计140，不是150；完整150身份表另有既有核验，摘要分组数字未闭合                                                       |
| L212 §4.2   | 1262相对1246“多28”                                           | 实为多16；source/process身份数本身不矛盾                                                                              |
| L18/§8引言  | 概括3项中等，其余低/信息                                     | §8.1–8.5共5个[中]标题（L363/371/379/387/395）；只能如实保原不一致，不能自行删两项或宣称产品已确证5缺陷                |
| L305 §6 F10 | 引用旧的mock ValueError('invalid finite index')作为当前负例  | 当前test没有该mock；实际是read_pinned的in_memory_input替换+真实construct/main拒绝。此为过时证据描述，不表示保护被移除 |

这些影响原报告的精确统计/证据表述，owner宜另给限定纠错记录并将新增范围问题路由唯一owner核实；不直接改原稿、不静默降严重度、不改候选代码。不能把A“每条均成立”的概括扩到以上错误汇总和缺证的执行/read链。

本次唯一写面为本报告。未读另一指定模型本轮内容、未产品重审或替原作者裁定产品问题真伪；未运行normal oracle/observe/GUI/安装、未展开未知metadata或子raw。M正式completed与原稿链成立，仍须完整保留B NotPass、所有意见/缺口和上述准确性边界，不能发布整体双Pass。
