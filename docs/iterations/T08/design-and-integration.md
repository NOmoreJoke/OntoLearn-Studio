# T08 纯服务设计与待批准接线

## 决定与范围

T08 新增模块只处理文字 Chat Completions 数据、Agent 白名单调度、版本化草稿及证据展示数据。不读取密钥、不导入 HTTP/fetch、不写项目、不提供 commit/confirm/undo/restore 工具。唯一最终发送与授权、凭据、最小调用记录仍归 I06；项目唯一真相、Diff、事务和撤销仍归 T01。

`main/agent/tools.ts` 是待接线的私有适配词汇，不是第二公共注册表。默认没有领域端口，不向产品发布能力；获批后由 T00 从唯一注册表映射真实服务，并独立核对 scopeRef、对象、项目、输入版本、取消边界。不能注册 test.*、仿真查询/推理/沙盘结果作为业务端口。I06 和公共契约当前没有被导入或修改。

## 官方协议核对（2026-10-21）

- [Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)：固定首选 `https://api.deepseek.com/chat/completions`，模型 `deepseek-v4-pro`；本模块限定文字、非流式、单 choice，严格拒绝未支持字段。长度/过滤/资源中断不能产出完整答案。
- [Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)：携带 tools 时保留此前所有 assistant 的 reasoning_content，包括无工具调用的轮次。codec 检查关联并完整保留字段；不默默改为非思考模式。正式模式由真实评估后固定。
- [JSON Output](https://api-docs.deepseek.com/guides/json_mode/)：请求使用 json_object，系统提示含 json 与范例；空内容、不合法JSON和业务schema均本地拒绝。
- [Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)：函数参数必须本地校验。供应方 strict 为 beta 端点特性，此模块不设置 strict:true，不更改既定接收端点；应用端 zod.strict() 始终生效。

只读了文档；没有执行真实API探针。响应可得返回model/fingerprint/usage用于主进程评估收据；模型别名不等于不可变权重。未知服务字段会失败，后续实际协议变化必须扩schema并重新验证。

## 接口提案：I06 / T00（未经批准不接线）

需要唯一网关提供按用途的窄模型调用，而不是任意URL/HTTP入口。T08仅提供 `encodeChatRequest(input)` 生成的完整最终body；网关在编码完成之后对**实际要发送的每一字节**做既有最终字段授权、预算、端点/主体版本复验，再由I06发送。不能先检查旧parts再替换成messages/tools。

所需输入：项目/操作身份、目的、配置不透明ID和版本、实际规范化endpoint、凭据主体版本、授权决策引用、每项文本来源与真实字段溯源、已批准的最终body、AbortSignal、剩余请求/token/时间与费用硬上限。密钥不能进入T08/renderer/Python。T08的字段裁剪只是最小化助手，不构成授权；reasoning_content、工具参数、模型文本、摘要、历史、错误和JSON内嵌内容同样受最终检查，不能以“模型自己生成”自动放行。reasoning不能获准完整回传时停止并申请范围扩展或新会话，不偷偷删去必需协议字段。

成功输出：有限长度完整响应文本（交decodeChatResponse）、真实请求/响应身份、实际接收端点/主体版本与授权记录引用、时间、usage、返回model/fingerprint。失败输出：固定安全错误码、是否已发送、是否已取消本地等待、审查记录引用；不得返回provider原始错误、业务正文、路径、密钥。禁止自动跨端点重定向或自动付费重试。完全本地阻止新发送；在途取消需明确已发数据无法撤回。

2026-10-23 指定审后补明确：每笔发送还须由 I06 从唯一设置权威读取**当前隐私档位及策略版本**并在最终发送前复验，不能从模型 body、页面旧 prop 或 T08 构造时快照推断。隐私策略不是 provider 请求字段；T08 的纯 body 不能构成该判定。实际 I06 设置/最终授权接口尚未交付，本段补足接口需求，不创建第二策略存储或宣称 FR-902 已通过。

例（仅形状提案，不是公共schema或新增网关）：

```json
{
  "projectId": "p1",
  "purpose": "agent-query-draft",
  "configurationRef": "opaque-config-v1",
  "authorizationRef": "opaque-grant",
  "body": {
    "model": "deepseek-v4-pro",
    "messages": [
      { "role": "system", "content": "输出json..." },
      { "role": "user", "content": "列出设备" }
    ],
    "thinking": { "type": "enabled" },
    "reasoning_effort": "high",
    "max_tokens": 2048,
    "stream": false,
    "response_format": { "type": "json_object" }
  }
}
```

尚缺真实字段来源：T01/T02–T07对正文、选择项、工具输出、摘要/历史、错误的字段身份与scopeRef映射；T08不能根据字段名猜来源。FR-901安全存储和FR-904本地审查记录复用I06实际接口及验收，不复制实现。

## 接口提案：T01 / T02–T07 / T00

宿主建立严格 `TrustedContext`：projectId、projectRevision、inputSnapshotId、scopeRef、当前模块/导师或项目模式、选中对象。模型只能提供工具自己的参数，不能注入项目、版本、授权或确认标志。

每个 `DomainPort.execute(context,args,signal)` 必须映射获批业务命名服务；readCurrent由宿主读取当前权威视图。执行前、每个结果回收时以及答案展示时校验上下文；旧结果不会当作新项目/版本当前结果。异步有界等待、批前整组校验、同session调用ID不重用和总调用数上限；取消中断本地等待并传播signal。适配器不能因为T08停止等待就假定引擎已取消，持久job/run状态仍以I04/T01为准。行为/沙盘端口仅能使用隔离运行，不能写正式事实；具体取消/已提交轮次由其真实服务返回。

工具参数和用途：ontology_read(选中objectIds)、ontology_propose(instruction)、mapping_propose(sourceId,instruction)、query_draft(question,scope)、query_execute(sparql,scope)、quality_check(scope)、reasoning_run(scope)、behavior_test(behaviorId,sampleId)、scenario_run(scenarioId)、result_read(resultId)。scope 为 asserted / asserted-and-derived / selected-history；具体范围必须由scopeRef再次检查。SPARQL只读与禁外联由真实T04/I05执行器保证，T08不另造不完整词法检查器。

工具结果只接受：

- 草稿：kind=draft、draftType、业务摘要summary、详细建议detail。T08附生成时项目/baseRevision/snapshot、requiresHumanDiffConfirmation=true；这不是T01正式ChangeSet。query草稿必须在UI原样显示SPARQL，mapping草稿仍需真实样本核对。
- 证据：kind=evidence、projectId、inputSnapshotId、scopeRef、resultId、status(current/stale/historical/failed/cancelled)、traceRefs、有限fieldId/value集合。真实结果载荷仍从唯一领域结果读取，不复制完整可变权威；无结果/页数据需保留完整集合/分页引用，当前轻量展示形状后续由唯一维护者审核映射。
- 异常/超时转换固定failure收据，不保存原始错误文本；返回结构不合格、跨项目/范围、假current旧快照均为INVALID_EVIDENCE。

模型最终JSON只能选择已存在callIds，不能提交“查询结果”“检查通过”自由正文；宿主展示实际收据的状态/值。已有工具收据时，模型只能触发宿主完整收据展示，不能挑选成功项隐藏失败；没有收据时只允许选择固定教育/建议模板（附“模型建议，未经确定性工具验证”），禁止自由文本计算结论，无依据可选uncertain。该结构保护不代替真实模型质量评估；恶意建议内容和错误引用仍要纳入11.3评估。

T01待提供：基于上述草稿产生真实结构与引用检查的preview（基准、完整Diff、影响、预览身份），独立真人confirm入口（提交前复验+原子取消/失败）、undo（后续依赖冲突暂停）、snapshot restore（单独确认和覆盖清单）。T08无正式写入口，因此当前不能测试A-02原子回滚或撤销，不能用无写入声称通过。

## 版本化评估与接线顺序

`tests/fixtures/agent/manifest.v1.json` 固定案例列表、输入文件哈希、重置入口与真实验收清单。定向命令：`npx vitest run tests/unit/t08-*.test.ts`。每案独立session，合成端口仅验证调度与证据忠实性，根本不执行领域算法。完整预期保留状态、值、轨迹引用、字符串001和草稿基准；伪造引用或多余成功文本必须拒绝。

接线顺序：批准I06安全传输/字段溯源 → 批准T01及各真实领域服务 → T00唯一命名bridge/页面与T09离线处理 → 实际API主体/预算批准后分开连接/JSON/工具探针 → 原11.3/12.2及A系列真实路径评估 → 固定正式模式/受测返回标识/manifest → 刷新批准base、同候选指定双审及原门禁。

UI当前只有context-actions纯策略，没有页面已接线。每页不超过4个主要动作；无模型时只标已有本地handler为可用，缺服务明确unavailable；演示/项目模式标记full-assistance，交T09记录，不计独立迁移成功。模型设置页复用I06安全接口，未另建存储或配置权威。

## 纯会话往返（第二批独立实现）

`main/agent/conversation.ts` 把已存在codec和AgentSession串成纯数据会话：`prepareExchange → acceptResponse → 实际已批准工具端口 → prepareExchange → 真实收据回答`。只有最后接入I06后才存在实际发送；prepareExchange返回exchangeId/body并不授予外发权限。

2026-10-23 指定审后，构造参数必须提供宿主预先受测的 `expectedProviderSignature`（复用已有严格 signature 形状）；mode/effort 必须与该 pin 一致。响应解码后、任何领域工具或答案处理前精确比较 returnedModel/fingerprint，不同或必需指纹消失即 `PROVIDER_DRIFT`。请求别名不硬等同实际返回版本，不做首次响应自建 baseline，也不忽略版本后缀。此处只消费宿主 pin 的只读快照，不生成能力 ready、评估收据或配置权威；I06 仍须复验实时配置、端点/主体及实际发送模式。没有真实 provider 评估，不能把字符串相等当真实权重/effort 已验。

会话仅在ready时准备一笔请求，并绑定递增exchangeId；未知/旧exchangeId不能消费当前待响应笔数。已消费provider响应ID、同session工具调用ID均不可复用，异步工具执行时拒绝并行响应。当前项目/snapshot/scope变化则终止旧会话，禁止把旧结果标为新结果。所有工具输出按宿主给出的字段列表做最小化，完整正文/历史/思考/工具参数仍须I06最终字节授权。

enabled 模式收到的每个响应（含无领域端口时）必须有 string reasoning_content，缺失或 null 在工具/答案处理前失败，不伪造空串补字段或降为 disabled。字段存在仍不是实际 effort 的独立证明。请求历史规则与响应不同：携带 tools 时保留此前所有 assistant 的完整思考字段及工具 ID 关联；不带 tools 的历史按官方协议允许不回传 reasoning_content，不能据此推断请求模式退化。模型最终 JSON 仍经 AgentSession 真实收据规则解析；原始模型文本不会替代结果。

会话具有有限exchange数、每请求输出token上限、累计已请求输出token上限与工具超时；一笔请求准备时即占用上限，失败也不退还。此处是请求数量/输出token的保守本地上限，不是费用核算或输入token预算，I06仍须控制实际总token、请求时间、费用硬上限和API主体权限。providerFailed只记录安全错误，不自动重试；失败后由页面保留用户输入并通过显式重试建立新操作。取消传播至正在等待的领域端口并忽略迟到响应；真实引擎是否已取消、已提交多少轮仍由I04/T01持久记录证明。

收到 usage 时，若其 completion_tokens 超过本笔请求 maxTokens，在任何工具/答案处理前按协议矛盾拒绝；prompt_tokens/total_tokens 不与“累计已请求输出上限”混比。usage 缺失仍为 null（未知），不是零。这个响应后的检查不能撤回已发生费用，不替代 I06 发送前的真实预算闸门。失败工具投影现只附本地安全枚举 code；未知运行时 code 回退 TOOL_FAILED，草稿正文和原异常仍不投影。新增枚举分类同样须 I06 最终字节授权，不自动获得外发许可。

`state()`只暴露本地安全状态、计数、错误码与宿主答案，不暴露prompt/history/provider异常。单测使用合成响应与注入端口验证往返，不能计入真实DeepSeek或领域集成验收。对应测试：`tests/unit/t08-conversation.test.ts`。

每次新增用户问题时，仅清除该会话的当前答案收据；协议历史与全部reasoning_content仍保留，全会话usedCalls与预算不重置。新问题不能自动沿用上一问题的成功作为当前依据；需要解释既有结果时，通过本轮result_read获得真实状态和来源收据。同一用户问题内部仍强制展示全部收据，不能隐藏失败项。

`state()`另提供只读克隆localReceipts和原始inputContext，与最终answer分离。最终模型失败、下一交换预算耗尽或批次中途取消均不擦除本轮已完成工具记录；快照不会把记录改标为新版本当前结果。新问题按本轮边界清理，实际页面草稿的保留/保存仍需T01正式草稿接口，不能把内存会话当持久项目源真相。

## 私有侧栏组件（未挂载共享App）

`renderer/src/agent/AgentSidebar.tsx`复用现有React、系统字体和tokens；只接收受信context、当前会话state、隐私档位/真实能力就绪标记以及已批准命名处理器。type-only引用main的私有视图类型，不在renderer加载Node或网关。未改App/style.css/preload/contracts，最终public形状仍待T00批准；组件本身不读取window bridge/凭据、不发送网络、不授予外发权限。

显示当前项目/版本/选中对象、最多四个页面动作、真实工具字段及依据引用、明确失败/过期/历史/取消、版本化草稿详情与独立“查看真实Diff”入口。缺处理器/缺能力/完全本地时禁用模型发送，已有本地动作才有可用路由；Diff基准不符或缺真实预览处理器时禁用。没有正式确认、提交、撤销或快照恢复能力，仍经T01独立入口。父级必须为每个项目保留各自输入/草稿，并把T09辅助级别写入真实学习记录；这里不建立持久项目或学习记录副本。

输入在发送/失败后保留，异步回调错误只显示固定提示，不回显异常正文；取消与重试只调用显式宿主处理器。inputContext不匹配时持续显示先前上下文提示并禁用动作；旧快照记录不能因切页被当成当前结果。所有业务/模型字符串使用React文本节点，禁止HTML注入、自动资源加载或外链渲染。

`tests/unit/t08-sidebar.test.ts`在内存编译实际TSX并用React renderToStaticMarkup验证HTML文本安全、完整供给值（含001/0/false/null）、记录状态、错误时草稿可见、缺服务禁用和旧基准Diff拒绝。它是无窗口SSR验证，不是浏览器交互、Electron或真实页面接线验收；实际事件行为/可访问性/视觉仍须隔离环境挂载同候选验证。

## T09获准固定输入与评估v2

总控后续明确允许只读使用T09固定 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的manifest和17项输入。已逐项验证17项与PRD源，原manifest SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`，只保留本轮需要的G-base、固定查询和equipment.csv原字节到T08 fixtures；没有读取变化中HEAD作实现，也未消费T09服务/helper、没有Store写入或expected预填。

manifest.v2继承v1及其全部真实验收要求，并固定新增case/probe/输入哈希。测试专用fixed-input-probe.py使用已有锁定RDFLib7.6.0从实际18条断言建新只读内存图执行有限SELECT；Q-01返回A01，Q-02另建输入把A01改Closed后返回空。语法有效但将Open错写Closed时实际得到A02（与正确结果同数量），完整行/列比较判语义错误，不能靠计数。非法语法与查询运行错误分开安全标识。实际input/query SHA区分阶段，旧快照不能混入新阶段。该CLI只接受有限case ID，不是可接受任意查询的产品执行器。

CSV由标准库实际读取，001/002、名称和含表头物理行2/3保持；数字化丢前导零或交换名称的手工候选均不匹配实际样本。这是样本一致性评估，不是T03映射能力运行。

协议到工具收据的探针只在测试中注入真实库观测；实际执行结果流入Agent会话，手工构造模型消息不能把错误A02改成期望A01。没有真实模型调用、T04/I05正式查询适配、推理/沙盘执行或产品能力注册。Q/A正式验收和11.3/12.2仍必须用获批领域执行器及实际模型服务完成。

该输入发现query_execute原本复用instruction.trim会改写查询末尾换行；现对SPARQL仅校验非空和长度，不规范化文本，使实际执行/展示/哈希一致。原失败及SHA保留于本线evidence。此实际源码改动须新候选验证/内审，与无变化的操作政策补充无关。
