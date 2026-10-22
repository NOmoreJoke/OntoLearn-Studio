# 本人原生session的最小只读核回路线

供总控转交各原owner使用。本线实际验证的是**官方客户端自行落盘文件的只读路线**，不是另造网络API或app-server端点。以下形状来自本线真实记录；仅定位已知本人session/turn与本人附件。没有查询T05或其他session，没有GUI操作，也不因方法说明重跑任何审查。

## ZCode

1. 已知本人`sessionId`后，精确文件为`~/.zcode/cli/rollout/model-io-${sessionId}.jsonl`；本线实例是`model-io-session_51c6a1c550181572a24f331b9a5c5e23.jsonl`。一行一个模型请求记录，实际字段包括`sessionId/turnId/requestId/startedAt/completedAt/model/request/response`。只选本人指定turn，不扫其他session。
2. 实际逐任务模型/思考字段：`record.model.modelId/providerId`、`record.request.body.model`、`record.request.body.output_config.effort`、`record.request.body.thinking.type`。仅提取这些标量；不得输出`request.headers`、`response.headers`、`body.system`、tools描述、SDK全消息或`response.reasoningText`。
3. 真实首user和自动附件读取可在`record.request.messages`的规范化消息中定位；本线该数组含应用system，不能整数组导出，更不能把所有role=user都当成本人原文。本线首请求中，本人长文本附件被自动追加为一个携带编号Read结果的system消息。只在**含本人已知附件路径的读取块**中提取`数字\t文本`编号行，按实际行号/文本保存，周围上下文全部排除；不是复制system消息。
4. 补读调用在`record.response.toolCalls[]`，本线结构为`{id,name,input}`；实际首调用`name="Read"`、`input.file_path/offset/limit`。下一请求的`request.messages`可表现为`role="tool", content=<字符串>`；provider形状`request.body.messages[].content[]`也可能为`{type:"tool_result",tool_use_id,content:...}`，实际核本次存在的结构，不假定索引固定。只取与本人附件Read call ID相连的编号行，不能把Bash/其他Read结果混入。
5. 本线原生附件实际在`~/.zcode/tmp/paste-attachments/2026-10-22/pasted-text-20261022-181729-43cf11ba.txt`。其他owner只用本人首user/Read参数实际引用的原生路径，不猜文件名、不读其他附件。先比附件与冻结完整正文的字节/长度/SHA，再逐行核真正供给给模型的Read结果；附件存在本身不等于模型已完整读取。
6. 本线首请求自动供给1–551，首模型Read(offset552,limit2000)经第二请求供给552–667，结果还带668空行。原正文确为667行，668只为格式空尾。本线数字不能外推到T05；其他任务按其实际范围/重叠/缺口独立计数。未知自动Read的toolCall ID/参数保持null，不造调用。
7. 实际执行权限/cwd来自`~/.zcode/cli/log/zcode-YYYY-MM-DD.jsonl`中本人`bootstrap.app.startup.runtime_config.completed`事件的`context.mode/model/workingDirectory`。全局日志必须先按确切本人session字符串过滤，再解析并检查`sessionId`，只投影必要字段；不输出其他事件或整context。本线为yolo、GLM-5.3、本人隔离cwd。创建事件`zcode_protocol.session_create.started/completed`的`context.workspaceKey/workspacePath`可核对应项目；不能仅凭全局config证明当前任务权限。
8. 正式终态双核：本人turn的末模型记录`response.finishReason`，及本人官方事件`turn.completed`或`turn.failed`的`timestamp/sessionId/turnId/status`。本线为`finishReason="stop"`加`turn.completed/status=completed`；其他任务若实际失败，保其真实最小错误码/消息/原文重置时间及来源，不把UI或他task错误推成全账号终态，不因文件中出现早期error就覆盖后来正式终态。报告存在/无新输出均不替代终态。

## MiniMax Code

1. 本线精确目录为`~/.minimax/v2/sessions/2026/10/22/10-19-10-535-session_bXZzX2QzMTRjYzdhNDNjODRhNTU5ZTMxZDVkZGYzNjYzYWY3/`，官方`manifest.json.sessionId`与本人已知ID一致。目录后缀为本线ID的base64url编码；若另一owner只知本人ID，可在**已知本人创建日期目录的目录名清单**匹配`session_${base64url(本人ID)}`后，再只读该精确manifest校验。不要递归读取其他session manifest、消息或数据库；日期应以本人实际创建记录为准，不能混淆本地时间与原生目录时钟。
2. 该目录`messages.jsonl`每行真实形状为`{message_id,turn_id,message}`。本人首user是`message.role="user"`的本人指定turn记录；`message.content`为块数组，文本块`{type:"text",text:...}`。只识别/导出本人输入或本人附件引用；应用附加上下文仍不能整条外发。GUI的6000字符预览、折叠或换行归一不是完整受理证明。
3. Read调用在assistant的`message.content`中：只选`type="toolCall", name="read"`（按实际大小写）及其`id/arguments`，仅限本人原生附件路径。结果记录`message.role="toolResult"`，`message.toolCallId`与调用ID关联；文本在`message.content`的text块中。**只提取该本人附件的编号行**，不复制夹在前后的reminder，不复制assistant的thinking块、thinkingSignature或其他内容。
4. 本线原生附件路径为`~/.minimax/v2/assets/2026/10/22/18-19-10-799-asset_20261022-181910-799_a503367fc7b6_16c433d4-pasted-text.txt`；其他任务按本人首user/Read实际路径定位。本线5次Read覆盖1–123、124–238、239–450、451–587、588–667。完整读取链实际含12条消息，但可外发证据只有5个结果中的本人行与必要标识。不能把本线12条/5次/667行套到其他任务。
5. 实际模型/档位来自该session目录`llm-call.json`的`provider/model/thinkingLevel`；本线为minimax/MiniMax-M3.1-Flash/xhigh。该文件还含系统提示等内容，仅读必要标量；**禁止复制systemPrompt**。本线实际cwd标记位于`llm-call.json.systemPrompt`内的`Primary working directory`，可仅解析这一精确值并比本人隔离树，周围系统内容不保存/不打印。
6. 本线任务“始终授权”的证据是创建时该任务的实际UI回执，另由已安装应用代码核过它对应bypassPermissions。尚未证明某个通用session JSON字段能替代这份权限回执；`~/.minimax/config.yaml`全局默认不证明已有任务即时权限。若owner无实际逐任务证据，保持缺口，不猜字段/私有API，也不因本说明抢GUI。
7. 本人指定turn最后assistant记录的`message.stopReason`是实际终态依据之一。本线末条有`role="assistant"`、`stopReason="stop"`、`timestamp`毫秒值，关联`message_id/turn_id`并核报告字节/hash；中间toolUse或工具结果不当作正式完成。不把ZCode的`turn.completed`事件名虚构到MiniMax。仅导出角色、stopReason、时间、ID、实际模型等必要字段，不输出完整assistant文本/thinking或整条message。

## 完整性、错误与共享边界

编号行从实际记录建立空映射后累积，最后才与冻结正文比较；不得用expected正文预填“实际”行。核1..N无缺口、重复范围内容一致、每行与冻结字节解码文本相同。保留真实offset/limit、原生附件SHA、首user/request/message/toolCall ID与记录来源；不自行折叠空行、截断后称完整或静默改正文。若应用确有换行规范化，分别记录原稿和实际受理副本SHA及明确差异，不能冒充byte-exact。

原始全流仅私有官方原处或受限快照，目录0700/文件0600；共享版只给本人必要user行、最小设置/终态、范围与hash。文件/流hash应写明快照时点，不称活动流永久hash。窗口/额度处理仍由根指定唯一owner，本说明不授权reset、重发、新任务、GUI或支付，也不提供他人会话材料。

原功能owner按授权完整读本人已完成的最终报告、登记所有意见；采证/恢复材料不得向另一模型泄露本轮对方意见。新输入/候选/base变化仍走双方各全新完整审查，方法核回不触发不变产品重测。
