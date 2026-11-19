# T08 B3 最小供给：结构化查询草稿提案

本批选择一个独立缺口：把经现有provider codec解码的模型消息转换成有明确字段、宿主范围和原输入版本的查询草稿提案。当前仅准备开发边界与验收输入，交ROOT排一次ZCode GLM-5.3／最高的实际UI创建后开发；尚未创建任务或写产品代码。现有e3产品、e61fa1bf流程及旧审查原件保持冻结。当前Goal面板与自动化不变。

## 为什么选这一项

FR-400要求配置模型后的自然语言查询草稿；FR-401要求用户能查看实际SPARQL与范围。当前T08 `query_draft(question,scope)`的领域返回仍是通用`draftType/summary/detail`，并无结构化查询编辑数据；`resolveAnswer`只允许收据、固定建议模板或不确定，不能把任意新JSON塞进去冒充已支持。现有`decodeStructuredContent`是通用结构校验器，可复用，无须重写JSON解析或再做调用预算、ID、上下文、DOM合成回归。

固定T04 507的编辑草稿有name、description、sparql、scope、capabilityQuestion、source六字段，但其draftSchema是T04私有编辑校验器，不是公共契约。本批不导入/复制T04模块，也不修改其页面；只提供T08私有、待consumer再次校验的提案。没有T02新基线依赖。B2b本体操作/ChangeSet草稿另批，不把查询文本解析当建模供给完成。

## 已刷新事实

| 来源                                                                                                    | 实际读取与结论                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| T08 e3／流程e61fa1bf                                                                                    | `deepseek-codec.ts`固定DeepSeek Chat Completions数据形状及JSON助手；`conversation.ts`在工具/答案前核宿主受测pin、响应reasoning和报告输出量；`agent-service.ts`盖project/revision/snapshot、整批工具预验、完整收据，正式确认/commit不在工具词汇。均为已有纯模块，不是本轮新验证。REQUEST_MODEL常量是源事实，不是本次确认真实服务/权重可用。                                                             |
| I06 C01 `1f3b053d8a69d1f7ddb1e29c143f648d910fe689`，修复候选 `04e1dfdf5865155c5daf2fb76fdeabb6262d0afb` | 已读main-integration-handoff、narrow-interface及实际core/app/service/policy相关源码。两候选gateway.ts／gateway-application.ts逐字相同；service修复只清理失败preview，不新增draft或DeepSeek请求面。core实际组`{model,parts}`，不接受T08最终messages/tools/thinking任意body。私有purpose包含explain/suggest/review，但公开startModelExplanation的purpose固定explain；不能从私有enum推出公开draft已就绪。 |
| I06授权／响应                                                                                           | contextId/grant/configurationVersion/principal由main维护；当前隐私词汇local/minimal/project，T08旧UIminimum是不同拼写，未来必须明确映射。outcome的completed.text是普通响应文本，不自动等于已核受测签名的DeepSeek JSON；running不是发送成功，cancelled.externalEffect=unknown。字段来源只允许main批准材料重建，任意question/history/reasoning不能自行贴标签获授权。                                     |
| 当前T01公共宿主观察 `45e6ba3955e05a4a9d15f59d561fdcc73faddb5f`                                          | 仅核固定main/index.ts与preload/index.ts及main目录模型文件名：这两叶无模型命名面/ModelGatewayService引用，不能沿用旧I06分支“12方法已接线”为当前主链路事实。未据此断言全仓不存在其他实验入口；共享壳仍归T01，不在本批写面。                                                                                                                                                                              |
| 固定T04 `5070004ec8e3219bea33960bd88f57f1976e9cf8`                                                      | draft.ts:71–80确有六字段。该版本会按其固定边缘空白集规范化name/SPARQL；T08提案先保留原文，不复制其规范化函数。正式T04接线须刷新批准基线，由原consumer校验并让用户查看编辑后最终文本。                                                                                                                                                                                                                  |

上述候选是只读来源，不等于I06已通过指定双审/获批可消费。本次没有导入供方、读取凭据、调用模型、开DB、启动probe或运行旧752TS/1052Py/DOM。

## 唯一开发写面（等待ROOT实际创建后生效）

只新增：

1. `apps/desktop/src/main/agent/query-draft/proposal.ts`：私有类型、结构schema和纯解码/封装函数。
2. `tests/unit/t08-query-draft-proposal.test.ts`：仅覆盖本批新字段与宿主盖章边界。
3. `tests/fixtures/agent/query-draft/proposal-cases.v1.json`：本批小型固定样例，可由当前文档case-vectors转为测试fixture。

不修改旧e3文件；如ZCode认为必须改旧codec/outcomeSchema/resolveAnswer，先向ROOT说明精确必要性，不擅自放宽旧可信回答。无新公共schema、方法注册、renderer/主入口、网关、Store、依赖/锁或配置修改；无T02/T04实现复制。不得把返回提案直接安装为当前DomainPort outcome，当前严格schema不接受它。

## 固定输入与输出（T08私有提案设计）

函数建议名`decodeQueryDraftProposal(message, hostInput)`；message仅是现有codec解码后的AssistantMessage，既有响应pin/模式验证仍由实际调用链负责，本函数不授予这层证明。

模型content必须是严格JSON对象，仅接受：

```json
{
  "kind": "query-draft",
  "name": "设备查询",
  "description": "查看设备标识",
  "sparql": "SELECT ?s WHERE { ?s a <urn:Equipment> }\n",
  "capabilityQuestion": "有哪些设备？"
}
```

hostInput必须显式给出`inputContext:TrustedContext`和`queryScope:'asserted'|'asserted+derived'`。queryScope由未来main选择权威供给，不能从模型、scopeRef字符串或默认值猜测；historical选择与snapshot权限也不由本函数签发。hostInput仅接受这两个键，复用既有contextSchema核完整context形状，不接受多余host键；inputContext只作原输入标记，不能把克隆快照当当前授权。

输出形状：

```ts
{
  kind: 'query-draft-proposal',
  inputContext: /* 原宿主context的独立副本 */,
  draft: {
    name, description, sparql,
    scope: /* hostInput.queryScope */,
    capabilityQuestion,
    source: 'model'
  },
  requiresHumanReview: true
}
```

模型不能给projectId/revision/snapshot/scope/source/grant/confirmation/execute或结果字段；多键一律拒绝。不能从旧summary/detail猜SPARQL或用模型说明补缺字段。name/SPARQL非空且非全空白，保持原字符串不trim、不补prefix、不改换行；原始UTF-16上限沿当前编辑边界为128/65536，description/capabilityQuestion上限4096；四个字符串拒绝孤立surrogate。该检查仅是T08提案形状/边界，不代T04的最终draftSchema或I05 SPARQL语义门。允许的提案形状不表示查询可执行，SERVICE/更新等文本不能触发任何执行，也不能用关键词黑名单冒充只读判断。

复用现有`decodeStructuredContent`及既有Zod；坏模型JSON/形状用固定INVALID_JSON，坏host形状用INVALID_PROTOCOL；不回传Zod issues、原异常或正文。结果不含运行状态、job/resultId、通过结论、写入或确认收据。调用方在显示/查看/保存/执行时仍须复核当前项目版本；本批不实现跨异步生命周期或第二权威。

## 验收与适用测试

`case-vectors.json`是待实施验收输入/输出，不是已跑测试。只新增这些边界：五字段模型对象到六字段draft的确切映射；原始SPARQL尾换行/001/Unicode保真；宿主显式scope及context盖章；模型越权键、缺字段/错kind/自由成功文案拒绝；各字段长度/孤立surrogate拒绝；输出与输入互不反写。T04再次规范化/语义解析/保存/执行是后续真实consumer验收，不在本批伪造。

当前共26个固定验收vector，覆盖空值/全空白、精确原长度上限成功、超限拒绝、坏host context/多余host键和四字段孤立surrogate；它们只是待实施输入输出。

新代码后按AGENTS跑定向新用例、格式/类型及原npm run check；不是无变化重跑e3。主进程目录新增所需原test:e2e由ROOT按T02优先串行安排，壳层e2e不能记为真实模型草稿端到端。未接线的pure module不触发API调用，不用receiver替身或旧合成绿冒充真实Agent。冻结新代码候选后按当前门禁做同候选指定审查；ZCode/MiniMax新审须附完整20261024审查清单及EOF证据。当前没有开发/审查任务ID、没有实际运行结果。

## I06／主应用接线前最小缺件

1. I06给出已批准、真实支持draft/suggest的具体main入口及源版本：用户question、选中上下文、历史/工具/reasoning的来源规则；最终DeepSeek消息体由谁构造、何处逐字节授权、如何纳入现有配置/主体/当前privacy与审计。不能把T08 body塞当前parts接口或另造fetch。
2. I06给出受测signature/模式/effort与实时config/principal的关联，返回原provider响应与invocation/context/exchange的绑定及取消/失败语义；本函数不从completed文本反推这些事实。Q9真实服务与Q5费用仍不默认。
3. T00/T01给出main签发TrustedContext、queryScope与actual selection/snapshot的映射；T04在其真实合并基线上接modelDraft查看，并负责保存/execute命名回调与原定义/参数blob/Job绑定。此批不依赖该基线即可完成纯模块验收，集成单独排队。
4. T01仍唯一负责任何正式ChangeSet/确认/原子提交/撤销；提案不是写入授权。B2b本体typed operations另设有界批次，本次不借query提案扩写。

## 当前交付边界

只提交这一份开发准备、固定case输入输出和一份delivery-index。保留原成果，不复制旧全量审查包、不重新审计整仓。没有实际开发文件或新功能完成计数；交ROOT安排后续ZCode创建与实现，T02继续独占优先桌面/CI。当前普通回合不改Goal/自动化，不push、不合并develop。
