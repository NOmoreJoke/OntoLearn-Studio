# O 原审查终态补充包独立收件复核

结论：**限定 Pass（只覆盖已收副本完整性、投影内部一致性及收件表述边界）**。IAR-01 初审发现的机器可读状态歧义已由 owner 更正，并经本人 delta 复核关闭。18 件已收静态副本的字节绑定、11 条意见全文登记、Z 完成阶段设置、M 原审查 stop 与后继新 user 的区分、三份命令流及保护快照的限定表述均通过核对。此结论不裁定 F-01–F-11 的技术真伪，不表示产品缺陷已修，也不签完整工程审查、双 Pass 或任何父门。

## 范围与方法

基于授权所给主树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle` 与基线标识 `9c36b3f2be054ea96d2e3f316b4feadc0076f7c7`。基线标识来自任务与收件 receipt；本次未调用 Git 或另外追验 HEAD。

全文阅读本目录 README、56586B/390 行原报告、全部意见登记以及三份正常命令合并流、288B 实际操作补充、4472B checker 源文。其余 JSON 均完整读入并以标准库严格解析（拒绝重复键与非有限常量），逐项检查必要标量、引用副本哈希、ID 与时间关系；较大保护快照和 Z 请求设置采用完整解析遍历而非声称逐字人读。共 18 件输入、311936B；11 个 JSON 全部严格解析通过。

仅另对照同级 `official-minimal-readback` 中四份已收副本：`operation-supplement-receipt.json`、`own-input-and-terminal-projection.json`、`protected-stat-readback.json`、`check-protected-stat-only.py`。未打开任何 JSON 中声明的 source 路径，未进入 `.zcode`/`.minimax` 原生记录、模型工作区、未知元数据或全局配置，未使用 GUI、网络、产品、测试、observe、Goal 或 Git 变更。本报告是唯一写入。

## 准确性意见与处置

### IAR-01：11 条 `sourceFixed:true` 的未定义语义与未修源状态存在歧义（已更正并独立复核关闭）

`all-minimax-original-opinions-register.json` 第20/29/38/47/56/65/74/83/92/101/110行，每条都写 `sourceFixed: true`。同条 `ownerDisposition` 为 `reported-open-awaiting-adjudication; no source fix or rejection inferred`；README 第9行明确本轮不修源；handoff receipt 的 `opinionsAdjudicatedOrFixed:false` 和 `sourceOrFrozenInputEdited:false` 亦如此。

初审时包内未定义 `sourceFixed` 指“来源字节已固定”还是“源缺陷已修复”。本人未推断发生修复，及时向 owner 反馈机器消费歧义。owner 随后将11处旧字段改为 `originalReportByteIdentityFixed:true` 与 `productSourceFixedByThisIntake:false`，并在 README 插入准确性处置段。

本人只 delta 复核两件：将最终登记的11组新字段反向还原为旧字段并重序列化，完整22220B/SHA恢复初审登记 `a70d1188e2571c191180f7eee32f15c41094c63c01fb6dc61528cc8dda243cfd`；从最终 README 仅去掉新增准确性段，完整6345B/SHA恢复初审 README `ec7f40c2ca923ee74354f4f59e034d42452e15f9d13508c50e702a0c3df896b2`。这证明只有明示字段更名/拆分与说明段插入，11条其余原文、位置、严重度和待裁定状态均未变。最终登记22957B/SHA `b5111c7ce0bcfb4ae13725c54eaf53923afe19f7dce7e94a84733d8fdfec8905`；README6687B/SHA `f178b35f0a20553d6234aa44118c69c7650fba542899af9607c394fc5f44f155`。本项关闭仅指字段准确性，不涉及 M 技术意见裁定或产品修复。首次发现及处置在此保留，本人未修改其他原件。

### IAR-02：原报告数量、等级概述矛盾，保留为报告准确性限制

原报告第11行写“1 项中等级 + 5 项中低等级”，第20行把 F-11 列中、F-05并入较低组；实际 §6 标题为 F-01–F-05 中5项、F-06–F-07 低-中2项、F-08–F-10 低3项、F-11 低-信息1项。登记表精确采用逐条标题且保留原概述矛盾，README 已明确解释。处置：保全原报告，不把概述当准确计数，不替 M 改判；本项无需修写原件才能保全收件。

### IAR-03：原报告“全部工具调用均未被权限门拦截”与真实拒绝投影冲突

原报告第52行有上述断言。首命令拒绝副本保留本 session/原 turn 下 `msg-2yBhfE0D2HiDXfT9OhEFI8aqyNj3b0s60BZtDIg68YU`、`call_01a16338326970b68a949dd3`、timestamp `1792665992823`、`isError:true`，精确错误行以 `srm (secure delete, irrecoverable)` 为自动拒绝理由，组合命令内含 `uname -srm`。这证明收件投影记录了一次审批拒绝；不证明发生过删除。README 已指出矛盾并声明未重跑/绕过。处置：原断言不得作为事实采用，后续成功流不覆盖首错，本人不追验原生记录。

### IAR-04：额外执行与权限自述不得由免责声明消账

原报告 §4.2 名称为“两条授权命令”但表内列三条，包括额外 `python3.12`；§4.4 自报 `importlib` 加载固定 builder 并调用 `read_pinned()`，字面超出两条精确 argv。原报告还自报读取用户 global config；这不能证明当前任务权限，且与第52行“未执行任何超出授权的动作”的绝对表述不能合并成全面合规证明。README/登记表明确保留这些事实及未核状态；两解释器同结果不消除 argv 偏差。处置：保留报告自述，不访问配置、不替其消账；不裁定当时产品技术行为。

### IAR-05：原报告部分章节指针错误，仅作导航限制

原报告第19、240、343行将七池规范逐条比对指向 §5.3，实际该表位于 §5.4；§9.1 第358行指向 §5.4 正确。处置：保全原件，读者以实际章节标题定位；不据此改变 F-04 或七池模型的技术结论。

### IAR-06：正式 root stop 与完整覆盖、后继终态严格分开

原报告第175、361、388行明确其余约55产品文件未逐行完成，产品只读子审定稿时仍运行。原报告首尾出现“完整 O”措辞，不能覆盖这份具体限制。README/handoff 已明确 `minimaxFullEngineeringReviewComplete:false`、子审完成未证、完整双 Pass 未成立。后续报告字节变化也未完整收读。处置：原 root stop 只确立该 turn 终态；不得升级为所有子审/后继 turn 均停止、完整工程审查完毕或双 Pass。

### IAR-07：owner 首次投影写入失败已保留

`owner-extraction-first-write-error.json` 报首次缺显式 cwd 导致 `FileNotFoundError`、exit1，读取成功但目标写入失败；后在显式 cwd 重做同一投影 exit0。README 与之一致。处置：如实保留采证错误与纠正，不以成功副本抹除首错；不解释为产品失败或源修改。

## 逐项完整性核对

1. **11 条意见无遗漏。** 将 §6 每个 heading 至下一 heading/分隔符之间的全文（仅排除段间空白分隔行）与 `verbatimFinding` 精确比较，11/11相等；ID、title、reportedSeverity、originalReportLine 全相等。原行号依次210、219、227、235、243、254、262、270、278、286、294。每条触发、影响、证据、建议均在原文副本内。§7完整历史表随原报告保留，未转为本人消账结论。
2. **原报告指纹闭合。** 副本56586B、390行、SHA `b145d9cbc74fd39182bff3d87fb5a5553094ff4a98a7b4be81a5e4dcd7b881e1` 与 register、terminal projection、handoff 一致；不采纳后来58279B版本为新终稿。
3. **Z 完成设置。** session `session_c76c854a8d2736fb809ce34b124f861b`、完成 turn `turn_829965ac-a1f3-4a38-9992-67f71eb2995b`，59个 requestId 唯一；逐项 modelId/bodyModel 均GLM-5.3、providerId均`account:bigmodel-individual-coding-plan`、effort均max、thinkingType均enabled。每请求开始不晚于完成，按序不重叠；58个tool-calls，最后stop。首10:38:16.009Z，末10:49:40.143Z；末requestId `feb34775-dbc5-4e56-9031-2ab8e8161730` 与首批终态投影相同，官方turn.completed时间10:49:40.361Z。该补证不等于权限/恢复原因新证明；首批首错和RCV-01限制未被本包撤回。
4. **M 原终态与新补充分离。** session `mvs_8262fb931cf34f3dae99b85683d65fd7`，原turn `b4e958d9-36d6-4f18-8484-28666d030a9c` 的原stop为11:10:28.973Z；新user `msg-user-v1-NB8Lhpa-XhAyYk_6FZoxRyT8GMKDzhoB6sYk4bGDzDg` 属新turn `turn_514d9775-9ba0-4431-9196-0c9e7206ddcd`，11:11:04.881Z，晚35.908秒。三份状态投影内原stop的ID、时间及stopReason一致。报告mtime先于原stop；后继mtime晚于新user，顺序无矛盾。
5. **补充全文一致。** 实际288B副本与首批operation receipt的`uiSubmission.text.encode()`逐字节相等；SHA均`3e5e28499b6b1ec2d5ef184c843830a1192991d177d5a6e0675b324cc8834d6c`。full-body receipt中的新user/turn/timestamp、bytes/hash与终态projection一致。只支持排队后实际成为新user的收件关系，不倒推原审已消费，不证明后续每行为遵守。
6. **后继仍非终态。** status/observation中新操作turn为toolUse；新增`turn_task_delivery_e7ed5d7a9fcf4986ad7d458a14a26c4f`也为toolUse。变化报告58279B/SHA `d93c7603b520a94af1792b097bfcc4149bc45e9afe11a4caf3c81293a93ef511`，mtimeNs `1792667582579709773`仅是已收字节身份声明，未读/采纳其正文。不能根据turn名称推断子审已完整交付。
7. **三份正常流完整保全。** 两份测试流分别有47个`... ok`条目、`Ran 47 tests`、`OK`、`EXIT=0`；时间4.754s/3.593s，版本3.9.6/3.12.12，与原报告一致。build流完整JSON含5件artifact，417 observations/320 datasets/pending137/specified280/wholeOracleComplete false，末EXIT=0；5件bytes/hash逐项在原报告出现。三文件bytes/hash与stream manifest一致。本人只核已有流，未重跑，也未把生成器测试通过当产品/语义验收。
8. **safe checker与快照边界。** checker与首批4472B脚本逐字节相等、SHA `58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647`。静态读码确认其保护项断言/未知路径lstat分开；未执行脚本。快照两模型各290条唯一保护path、11冻结launch成员；290项与首批及两模型之间完全相等。保护记录bytes非负且SHA格式有效。快照报detached86df、index空、tracked仅AGENTS；Z额外32项、M37项均只有path/stat等字段、attribution unknown、contentReadForThisInventory false，wholeFilesystemFreezePass均false。不能用此快照证明全FS冻结、未知内容身份或后台全部停止。
9. **handoff边界闭合。** receipt明确owner无产品/oracle执行、未改源与冻结输入、未裁定/修复11意见、未完成完整工程双审、137不变、父T05/P0未闭。IAR-01更正后，其核心状态与README及相关投影相容。本人没有核验任何原生源真伪或当前生产状态。

## 输入指纹清单

以下为本次实际读取的18件输入，报告本身不计入输入。总指纹算法：按文件名升序，将每件 `name<TAB>bytes<TAB>sha256<LF>` 的UTF-8字节拼接再SHA256，结果 `81a582931707bed5395e81427cd4acec609b98512bd926e249fa7de5850ccbc3`。

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `README.md` | 6687 | `f178b35f0a20553d6234aa44118c69c7650fba542899af9607c394fc5f44f155` |
| `all-minimax-original-opinions-register.json` | 22957 | `b5111c7ce0bcfb4ae13725c54eaf53923afe19f7dce7e94a84733d8fdfec8905` |
| `check-protected-stat-only.py` | 4472 | `58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647` |
| `minimax-first-command-rejection-projection.json` | 2426 | `5b4806a1bafc0fb2f0610b048f2c74bbc1e1c7518587cc03c9130d8ddec73425` |
| `minimax-normal-command-streams.json` | 1194 | `ee4271b9504f80e917bf580f5e6ce69c222cfe1fc1ad5d61b9cfd104282ad82b` |
| `minimax-o-run-build-check-python3.txt` | 1443 | `0e0fffb8a411143b6d994cb79ada480e6beb48422e27f52e1ff972ea316c48ea` |
| `minimax-o-run-test-python3.txt` | 4744 | `d64de94e429331c0cfd76cc1f83eecd33321d2b07b9964260c94be8a735c9f36` |
| `minimax-o-run-test-python312.txt` | 7333 | `98baa2d3a22ca49fe9946d3a45be787ea710000ea160e7b4951bee2cb67a9736` |
| `minimax-operation-supplement-actual.txt` | 288 | `3e5e28499b6b1ec2d5ef184c843830a1192991d177d5a6e0675b324cc8834d6c` |
| `minimax-operation-supplement-full-body-receipt.json` | 696 | `25a042a94ebddc3fcdb20b9c56f8e493f40810cdcc2773dff1d39d1a3d1588db` |
| `minimax-original-final-report.md` | 56586 | `b145d9cbc74fd39182bff3d87fb5a5553094ff4a98a7b4be81a5e4dcd7b881e1` |
| `minimax-original-terminal-and-followup-projection.json` | 1698 | `31a0c2959a4eb9f055ec6bbbd9c2677cd542920f2adce371b3b29833d912a5f3` |
| `minimax-post-original-observation.json` | 1627 | `96bb34d0273e6a6715b67d050f9fa53d18c2f7ccfe63484c306814b6f45897b6` |
| `minimax-status-after-original-stop.json` | 773 | `3ae3ffa3815dead3b9e475c305bb901477fb060ddcaf28afa212e831cbac1c82` |
| `original-terminal-handoff-receipt.json` | 1681 | `46891b6ea6d0135c5ec7b3f819f021261c27c164e4809c3c2dba20ec323568de` |
| `owner-extraction-first-write-error.json` | 479 | `a248642e16a221554a38e46e19ed2e4d835ff7fe552eeb4b837c35b10d2dbe22` |
| `protected-stat-readback.json` | 173858 | `d0e970904e09f8c044e8195adcf26c646bf7479f1055bb407095683afe219b0b` |
| `zcode-completed-turn-settings.json` | 22994 | `65217bc61a9feca40f5b1e845198ff6f685421f3a8ba33a2fb21a64a13c7807d` |

对照的首批已收副本指纹：

| official-minimal-readback 文件 | bytes | SHA-256 |
|---|---:|---|
| `operation-supplement-receipt.json` |1261|`507f34def5dbaa81d6dd04d322118e2033c9bb7f0bf8894243ddbe87690f4e7f`|
| `own-input-and-terminal-projection.json` |3441|`c51d67c7fd6b1057c02975faf801edf0996822561ddf951ebe1667b5e4534ac6`|
| `protected-stat-readback.json` |173576|`c7feecf47bac94d2869614540dc0f2ebe6ca5e289d3018e0d5ec5cf2e0b24787`|
| `check-protected-stat-only.py` |4472|`58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647`|

最终限定 Pass 仅确认已收副本的上述完整性、投影内部一致性与收件表述边界。IAR-01已关闭；IAR-02–IAR-07所述原报告准确性/覆盖限制和真实首错继续保全。F-01–F-11全部仍待裁定，137 pending与26 allocation缺件不变；完整工程双审、后继后台终态及父T05/P0/生产门均未由本收件复核签署。
