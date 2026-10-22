# O 正式最小核回：首批收件独立复核

结论：**Pass，仅限本批收件的字节、身份投影、终态区分与披露边界。** 原报告有一项 observe 准确性意见，owner 已追加“不采信、未核待处置”，原报告不改；该声明不计入本批已证实事实。本结论不重签 Z 的工程实质审查，不签 MiniMax 完成、双模型 Pass、26项积压或父门通过。

## 范围与固定身份

- reviewer：`/root/projection_receiving_review_package_independent_review`。
- cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle`；审查 HEAD `8296ff75c8d839b84dbf5b371bef204ce0ab3dfc`。
- 本轮仅审 `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/official-minimal-readback/` 的首批18件材料，包含 owner 本轮追加的 README 准确性处置、`minimax-status-first-batch.json` 及 `first-batch-receipt.json`。
- 唯一新增写面是本报告。没有修改其他首批材料、原报告、冻结提示、源或 AGENTS，没有 stage/commit/GUI/网络/Goal、产品/测试/observe执行。

全文读 README、已正式收件的 Z 终态原报告、两份 accepted-user 正文、全部明确命名流副本及 safe stat 脚本；全部 JSON 完整解析，较大的 protected 清单按完整结构/条目核对，没有把截断打印当已看到全量。只为输入身份比对读取 owner 既有 preparation 冻结提示镜像。**没有访问任何原生 session 路径、`.zcode`/`.minimax`、未知 runtime 内容、任一 review workspace 其他文件。** JSON 内来源路径只作文本元数据，没有跟随读取。

不含本报告的首批18件合计247463 bytes；按文件名排序生成 `{path,bytes,sha256}` 数组，再用 `ensure_ascii=false, sort_keys=true, separators=(',',':')` 的紧凑 UTF-8 JSON 编码，其本审清单指纹为 `9f4f0c88067970f46863869060e6c2d6d47c2e56671e8a8798b2941e79431f95`。这只绑定所读副本，不代替原生活动全流的永久 hash。

## 已核事实

### 两份正式输入只少一个末尾 LF

| 本方 | accepted-user bytes / SHA256 | 冻结 bytes / SHA256 |
| --- | --- | --- |
| ZCode | 12896 / `477890e73a4b3ccecfa38b8a2a9e9d4de584d859206ea18482240b70a4d02f86` | 12897 / `887066cd54f48216215faa2096cebd5ca95e1f851f8c93569aa6beca800ff6fd` |
| MiniMax | 12945 / `9bb1f6e9aa635516a5ef9cd7a2df0e71a425d9ebf4cfd9739968746ebff88588` | 12946 / `4f585bddefe6ba504c9b5786b3b2db29078e0d07fa262da3facaed73bb04abf1` |

独立直接断言两方均为 `frozen == accepted + b'\n'`，accepted不以LF结尾，冻结版以LF结尾；未使用 strip/trim 推导。完整正文、所有内部空行、own workspace/报告映射、原完整提示及范围限制保持。

M 是已提取的 inline 本人正文，不是附件引用；本批 JSON 明示排除客户端 context，且 `native_attachment_reference_in_original_user=false`。本审的严格字节比较支持这个正文副本完整，不虚构附件 Read 覆盖链。初始 `selectedOwnUser=[]` 时点记录保留，后续正文投影补缺，没有重写初始快照。

### 首次失败、恢复未知与 Z 正式终态分开

`session_c76c854a8d2736fb809ce34b124f861b` 的初 turn `turn_55ad22cc-1f42-4a54-9875-d68601efb179` 保留真实1308额度失败及21:59:03重置原文，official `turn.failed` 时间为10:36:59.863Z。

后继 `turn_829965ac-a1f3-4a38-9992-67f71eb2995b` 首请求10:38:16.009Z，最后模型完成10:49:40.143Z/`finishReason=stop`，official事件10:49:40.361Z/`turn.completed,status=completed`。投影中的 turn ID、时间先后及两个 turn 的本人正文身份相互一致。首请求 effort/model、本人 runtime_config 的 yolo/cwd 与全局默认配置明确分开；原报告的 task/effort 未核表述没有被倒改。

恢复原因和操作者仍 unknown，不由两个 turn 的同文正文反推 owner reset、重发、付款或升级。设置投影明确源自本人首次请求/会话事件，不把它外推成对所有后续请求或全历史的独立核验。本审只核所收投影内部一致性，未回读原生全流验证其完备性。

Z 原报告副本18041 bytes，SHA256 `5545dd1e07ace009f690ace4e763245afcee0baa3691d1ebfe99cac06f2e95dc` 核同。报告全文已读，有限静态 O+两条正常命令的自签 Pass 与产品/生产/137 pending/父门无法验证分开；本批 README明确不把字节核验当逐行完整审查或26项全线通过。

### M 只有执行中观察和排队回执

M session `mvs_8262fb931cf34f3dae99b85683d65fd7`、原 turn `b4e958d9-36d6-4f18-8484-28666d030a9c` 的初始与后续投影均为 `toolUse`。追加 `minimax-status-first-batch.json` 在11:04:07.995911Z仍记录该 turn 的 toolUse，`stopRecords=[]`、`supplementNativeMatches=[]`、`formalReportRead=false`；没有据文件名、临时输出或“尚在运行”猜最终结论。

操作补充正文288 bytes/SHA256 `3e5e28499b6b1ec2d5ef184c843830a1192991d177d5a6e0675b324cc8834d6c` 独立核同。UI“1条排队中”、composer cleared 和 `modelConsumptionProven=false` 相互一致，排队不等于模型已消费。补充仅限制未知元数据为 path/lstat及unknown归属，不包含对方意见。Z补充未发送的记录与其已有终态区分；本审未向任何模型发送消息。

### 正常命令流是所收原副本，不是本审重跑

五件明确命名流的 bytes/SHA全部与 `zcode-reported-normal-command-streams.json` 相等：测试stdout为真实空文件；stderr有47条逐项ok及 `Ran 47 tests in 4.754s / OK`；check stdout有五件artifact、320datasets/417observations、280specified/137pending/wholeOracleComplete=false。前后两份hash文件各七个唯一源路径，字节完全相同。

argv/exit归属在材料中明确来自 Z 原报告，owner与本审没有重新执行。这里核的是五个明确副本和报告声明，不补造额外check.stderr、冗余重跑的exit或弃流，也不据这些副本量化产品性能或证明完整生产验收。

## 独立意见及处置

**RCV-01：Z 原报告 observe 两项表述不应作已证实事实。** `zcode-final-report.md:33` 和 `:54` 称 observe exit0，且把 setupReady=false归因为新增元数据。与前次已固定并实际审过的身份工具逻辑不符：`setupReady = phase == 'setup' and not unknown`，observe阶段本就恒false；`return 0 if not unknown else 2`，在有unknown路径的前提下不能同时采信exit0。

本审已把精确意见传给owner。owner在 README新增工具逻辑及“不采信、未核／待处置”说明，保留原报告原字节，没有为了核这两句读取旧observe产物或未知元数据，也未给M发送Z意见。**当前收件表述缺口已补，原报告这两句仍未核，不在本 Pass内。** 不把它推为新产品缺陷或伪造原命令结果。

其余已披露执行偏差继续保留：Z对`.mimosa`生成过hash及自行归属，本批owner未确认归属；一次无必要重复测试、stderr弃流、exit未登记，以及三次静态脚本错误都没有补绿或隐藏。统计快照与Z自报95件属于不同时点/不同登记范围，本审不从后续path数量差异推断是谁删除或改了文件。

owner本身一次诊断投影过宽输出M客户端reminder也已披露。共享材料仅保本人正文、必要标量及已收报告，没有把那次输出说成从未发生，也未将完整客户端/系统上下文复制为收件输入。本审未读取被排除内容。

最后追加的 first-batch-receipt已全文读并核对：绑定实际parent dispatch，Z保留首次失败/recovery unknown及原报告准确性处置，`ownerEndorsesFullStagePass=false`；M终态/全文报告均false，输入单LF关系、290/11保护、peer意见未发、dualModelCompletePass=false及父门false与本批材料相符。该receipt没有把本审意见提前填为已完成。

## safe stat 脚本与未知内容边界

`check-protected-stat-only.py` 4472 bytes，SHA256 `58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647`。全文/AST检查显示：已声明冻结源/manifest/launch成员和AGENTS走内容hash核对；未知额外路径循环仅walk/path/lstat/is_symlink等元数据操作，没有read/open/hash/resolve/JSON parse内容调用。唯一结果写面为本目录 `protected-stat-readback.json`；本审没有执行该脚本。

所收 stat record 两方各290个唯一protected记录、11件冻结launch成员，保护条目数组一致；trackedChanges只列AGENTS，indexEmpty，detached86df。Z的32个/M的36个额外路径全部只有path/bytes/mtimeNs/symlink/attribution=unknown/contentReadForThisInventory=false，无内容hash或内容字段；`wholeFilesystemFreezePass=false`。这支持“固定输入核对”和“额外路径仅stat”分门，不能签全filesystem集合冻结或归属证明。上述是本批已收记录核对，不是本审重新访问两个实际workspace。

## 验证与最终界线

本审执行的 `cat/sed/tail`、自有Python标准库JSON/hash/AST/集合断言和owner主树Git身份/状态读取均exit0；没有非零命令。一次合并打印过大而截断，之后分段补读Z报告全文、完整解析JSON并定点核其所有结构条目；不把截断打印当完整可见原流。

本批当前收件表述和可核副本为Pass；正式原生采证的真实性/完整性承接owner的明确投影来源，本审未越界追读原生会话。Z有限自签结论仍需按其真实范围使用；observe准确性意见保持未核处置项。M尚无正式终态/报告消费，不能签双Pass，也无需等待M才能完成本首批独审；后续材料必须另加并做必要delta核对。

137/417、父T05/P0、完整26项、source/issuer/capture/费用/17L、Job/Store/selected/wholeH、S1/B1/CI两OS/真人/develop均未由本报告关闭。本审仅新增本报告，落地后bytes/SHA另行交接，不自含自身hash。
