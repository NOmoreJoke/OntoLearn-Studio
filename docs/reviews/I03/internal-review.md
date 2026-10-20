# I03 独立内部审查记录

审查者 `/root/requirements_review`，只读独立 agent；本开发会话负责全部实现。无 GUI、无他线文件写入。审查工作区草案，不是指定外审，不以本记录替代 GLM-5.3/最高或 M3.1-Flash/xhigh。原 base 为 1b6df7a，审查时尚未冻结候选。

## 首次代码审查

审查者先完整读取 PRD 相关 FR/8.6/8.7/10.2–10.5/附录 C/D/E/G、S2/U1、I01 ADR 与三轮处理及关键原意见，给出完整需求矩阵，再独立检查实际代码与无窗口探针。当时定向 TS193 通过不能覆盖下列真实反例；全部原严重度为 P2。

| 编号 | 发现与证据 | 处置 |
| --- | --- | --- |
| I03-A1 P2 | result.current 可接受同项目另一 kind/definition/scope/参数/实现，甚至 historical 结果；双端 matchesResponse 为 true | 采纳；完整 current key、实现与 current 状态比较；公共 responses 正反例 |
| I03-A2 P2 | operation.get 可接受另一 operation marker；job.unsubscribe 可接受另一 subscriptionId | 采纳；分别绑定 operation/subscription，公共反例 |
| I03-A3 P2 | queued atomic 带另一 operationId 和已提交 marker 仍合法；cancel alreadyTerminal+running 被接受 | 采纳；嵌套 operation、queued 零提交、success 必须 marker、取消 disposition/state 联动；公共反例 |
| I03-A4 P2 | result.page 可超过 request pageSize；active job.list 可含重复 cancelled、超过页大小；同 rowId 不同 ordinal 可接受 | 采纳；请求页大小、唯一性、稳定顺序、过滤与项目绑定；新增 jobListCursorRecord 与公共游标反例 |
| I03-A5 P2 | 终态已知时，增加 seq 仍可接受同 stateVersion 的 running 反向通知 | 采纳；绑定已知 state，state 事件严格下一版/合法前状态；同版矛盾/终态/缺口拒绝应用后 get；progress 仅同版非终态 |
| I03-A6 P2 | Python name='Q1\n' 为 true，TS 为 false；尾换行正则语义分歧 | 采纳；统一全串匹配，覆盖 LF/CRLF/CR；数值2.0与孤立surrogate亦修正，两端保守数值字节预算一致 |

两项未定级设计建议全部采纳：按注册表直接验证 params_job.create/list 与完整 request 必须有相同语义；正式写任务用 receipt kind 且只可 historical，不借用 test 或领域 current。I03 自查另外补齐 job.create 响应输入与 operation 绑定、atomic success marker、legacy NULL kind 开库显式拒绝/零清理副作用。无私自降级或遗漏。

当前修订代码的独立复审正在执行。最终判断与后续修改另追加，不把现有定向通过替代审查者关闭确认。

## 修订后独立复审

审查者实际重验原六组与两建议：A1/A2/A3/A4/A6 已关闭；A5 原终态倒退反例关闭，但合法整数浮点 stateVersion=2.0 仍分歧，未算完全关闭。发现以下五项 P2，全部采纳；没有沿用“前六已关”作为新代码通过结论：

| 编号 | 独立反例 | 修订与回归 |
| --- | --- | --- |
| I03-B1 P2 | queued→running 的 version=2.0，TS route true，Python schema true但route false；permits_transition 仍只收 int | 两端统一数学整数、拒 bool/非有限/小数版本；公共数值转换场景 |
| I03-B2 P2 | 1200项合法 query 引用链，TS返回1201依赖，Python裸 RecursionError | 双端迭代闭包、环去重、悬空拒绝、4096定义/依赖上界；公共长链与越界场景 |
| I03-B3 P2 | 同一 stale reason 重复或 before 改1000，仍有效 | 依赖去重、before对应输入版本；新增集合成员仅跟踪family+before0/after≥1；公共正反例 |
| I03-B4 P2 | job/result空向量仍有效，与全部策略 facts:asserted 不符 | job/result必须含真实项目级 facts 键，project投影允许空；公共反例 |
| I03-B5 P2 | job.create 只改 definitionId/derivedResultIds，原响应仍接受；DTO未保存完整输入 | job完整input+confirmationRef持久身份、外层一致性、完整请求响应/幂等指纹绑定；公共反例 |

修订定向结果：285 TS（含原4）、299 Python（仅本契约模块）通过，contracts独立strict typecheck与ruff通过。最终针对上述变化的独立核验待取得；之后再冻结本地候选。

## 最终定向独立核验

同一独立 agent 已确认 B1–B5 全部关闭，针对改动没有新的阻断：整数浮点通知双端一致且 bool/小数/非有限拒绝；1200/4095链成功、4096/4097总键越界拒绝；stale关系/facts依赖/完整输入绑定均实证关闭。独立实际TS281（只本契约）、Python3.12.12的本契约299项通过，补充边界探针通过。最终完整 check 的285TS/497Python由开发会话另行实跑通过。本记录只关闭内部项，指定双外审仍未创建，不声明 I03 完成。


## 首次冻结后的修订核验

首次本地候选ad9756e尚未创建外审任务。冻结复核后明确6处JSON读取UTF-8编码，避免平台locale影响；独立agent核对仅编码参数变化，无其他逻辑变化。全check重新通过285TS/497Python、contracts strict类型与sources12通过。总控随后交付I06的11类错误需求，本线记录为安全兜底/下一版精确语义承接，protocol明确retryable不是自动重放授权；独立agent确认11类无漏项、未误称schema批准、不混淆取消、未削弱新候选/双审/真实接线门禁。生成新本地候选，旧未审候选与预备稿保留在candidates/candidate-1，不沿用旧通过。

## I05 语义契约修订独立审查

审查者仍为 `/root/requirements_review`，只读检查本次新增契约、公共样例和30码处置，并实际运行定向校验；未改文件、未操作GUI或启动Electron。首次指出两项P2，全部采纳：

| 编号 | 独立反例 | 修订与回归 |
| --- | --- | --- |
| I03-C1 P2 | 根constraintDefinitionId可改为另一合法ID，而原constraintsRef元数据仍接受，未绑定具体已存定义 | 资源binding必须有constraintDefinitionId；constraints角色与根一致，其他层必须null。公共根ID错配、资源ID错配、其他层冒充3反例；真实接入仍须核对job.input和实际命名模板 |
| I03-C2 P2 | I05的UNSUPPORTED_SHACL_PATH也用于targetClass/datatype非IRI，表格一律映射path不支持会误分类 | 按合法范围外路径、已确认非法模板项、可信违约/未知来源三分支；必须在来源产生typed reason，不能仅按合码猜测 |

最终定向独立复审确认两项均关闭、无残余阻断，实际TS405/Python424通过。开发会话完整npm run check另实跑409TS/622Python通过，contracts strict typecheck、sources12及diff检查通过。本次没有执行真实RDFS/SHACL或分层图投影；它们由I05/I04提供真实执行与接线证据。新候选须重新进行指定双外审，不能沿用旧候选或本内部结论。

### 冻结前收到的I05 v3细码更新

总控转交typed-reasons-v3.md后，本线保存第二份逐字快照与SHA，并将25项当前来源细码置于历史30码之前；退休合码仅留审计。独立agent定向文档复核确认25/25无漏项、重复、误分类，SHAPE_PATH_UNCLASSIFIED仅INTERNAL_ERROR，双快照逐字及SHA一致；未把I05未冻结源码或123项定向交接声明当作全量/包内通过，未新增公共方法。hash回归覆盖两份快照后，开发会话最终完整check仍409TS/622Python通过，contracts strict类型、sources12、diff检查通过；原始日志与hash已更新。未重跑不变的语义探针，指定外审仍未创建。

## I02合并后新基线独立兼容审查

总控授权同步已合并develop后，以可追踪merge合入c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3，merge为0ec24b7e12c9ffaee5895e461800649a04bfff2f，无冲突，旧候选3的36份受审文件与未提交证据逐字保留。requirements_review重新实际审查新base→merge的全部I03差异及I02 desktop/构建/CI交互，未沿用旧结论。

实际加载确认desktop仍仅用contracts根v1的PROTOCOL_VERSION/healthSchema；独立v2入口可加载且v2Runtime为空，未接入health/preload/renderer。I02未改storage、engine protocol或I03契约；恢复模块不承担job或存储提交。独立无窗口TS420项及Python435项（v2/边界守卫/原v1协议）通过，无新增阻断。开发会话新基线完整check420TS/622Python、contracts strict类型、sources12及diff检查通过。未运行Electron/e2e/native/HMR/产物，不把I02继承报告当作I03运行验证；指定双模型须审新固定base→head全范围。

## 候选5有限修订独立审查

/root/requirements_review 静态审查F1/F2/F3/F4/F6及Z防漂移项，发现P2：零轮成功摘要与succeeded要求已提交轮次冲突。已改成功至少一轮；零提交失败/取消仅状态与null进度，复核明确闭合。八个摘要单元可由既有row/paging承载，无新增方法/提前停止。其余有限变化未发现新问题；独立审查未运行命令/GUI，不替代指定双模型新轮。开发会话恢复后的完整check424TS/626Python通过，真实类型注入两处均标准入口exit2+TS2322且字节恢复。
