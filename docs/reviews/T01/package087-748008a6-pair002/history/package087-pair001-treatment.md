# 748008a6 / package087 两份指定审查意见处置

本记录只补充原候选的事实核验与适用范围，不修改产品、测试、配置、索引、任何历史报告或外部工具记忆。不把 owner/Codex 处置当作指定模型 Pass。当前 ZCode 内部演示 PASS、MiniMax BLOCK，**整体未取得双 Pass，不推送，0/17 不变**。

## 原件与实际终态

| 审查                                         | 实际新任务                                                                            | 报告原件                                                                                                         | 实际结论                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| MiniMax M3.1-Flash / xhigh / 始终授权        | `mvs_0bd992802fe745adb4a4cab7be1cb6c2`，Review package087 full cumulative changes     | `minimax/report.md`，716 行，103590 B，SHA256 `33ff3583d12d2284ce896c79985c90427519d15bcd1a0d5e7b1906277c9bc4bb` | 内部演示 BLOCK；正式分发/跨平台 HOLD  |
| ZCode Start Plan / GLM-5.3 / 最高 / 完全访问 | `session_8a616831f1e35b238dd969450f550939`，T01 package087 748008a6 cumulative review | `zcode/report.md`，181 行，34597 B，SHA256 `12ffaff3e232502fd66920a2434b33b4a18e2f28d4e15b206058841cd79f1c48`    | 内部演示 PASS；正式分发/其他平台 HOLD |

两份报告均已实际结束并由父会话读至 EOF。审查期间没有互传本轮意见；两方获得相同历史 7d30/package085 报告与上轮处置。原报告保持原字节。本轮为 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → HEAD `748008a6a15091e8c5376b53a9348002eee7a207`，38 commits / 525 files。

受审规范源为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`，Git authority 为 `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/.git/worktrees/T01-project-transactions`。索引173116 B / `0bd0667bf2c014a604601613a2cab4ab155794777813cf01460993f1db7b119e`，AGENTS overlay15147 B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，cached diff 空；唯一未暂存项是原 AGENTS overlay。N 临时 checkout 的 UNBORN Git 不作为 authority。

## 当前范围与证据使用

采用的当前范围仍是 macOS15 arm64 未签名目录包，“非正式分发，仅限内部演示”。正式签名、公证、安装、完整 legal/_distutils、无开发环境设备、Windows/参考设备、D2、损坏 SQLite 物理 HOLD、真实 LLM 等分别保留，不能用内部包绿关闭。

最新用户续接授权要求按实际运行 → 同版指定双审 → push → PR → CI → squash merge → 远端复核执行。C4–C6 和 D8 旧记录保留；两报告沿用“D8 尚待选 A/B”的历史字段不能取代后来的明确续接授权。双 Pass 仍是推送前置；当前尚未 push/CI 是流程位置，不把后续步骤反过来变成审查前置循环。

本轮处置没有修改源码，whole087/package087/e2e087/真实运行087仍只证明原748候选，不自动产生新运行证据。若后续实际改码或改验收，必须新候选及对应必要完整重验；若只补静态证明/意见处置，保持原候选并将相同原件、原清单和本记录对称提交给**两个全新指定审查任务**重新独立判断，不续问旧任务改旧结论。

## MM §4.1 与 Z §3.2：退役回调失败及产品 ACK 恢复

### 采纳的事实与限制

`engine.ts:946–980` 的 consume 若 retire 回调抛错，会停在退款和删除之前；已完成回调逐项删除，失败项、原 receipt、原 delivery aliases 和原 holding 继续保留。`desktop-ipc.ts:135–142` 捕获 consume 异常后拒绝，未删原 deliveryId；`preload/index.ts:28–45` 只发送一次私有 ACK，失败后仍返回已经收到的业务结果。再次提交同 operation 得到新 deliveryId，不会替旧 ID 完成 ACK。因此准确条件后果为：**若该 retire 失败实际发生，当前产品路径没有自动重发原 ACK 的入口**。Z 报告“可按原 handle 稍后重试”仅在引擎 receiver API 层成立，不能当产品自动恢复已经实现。

现有 `t01-mainline-reply-lifecycle.test.ts:541–583` 人为抛回调异常并直接再 consume；`t01-mainline-real-runtime.test.ts:582–598` 一次性 spy 替换真实 budget.releaseHolding 后直接 consume 原 receipt。它们证明原责任保留和精确重试不重复退款，**不证明自然异常触发或 Electron/preload 自动重试**。首次丢回复 E2E 的故障注入在信封抵达 preload 前，不覆盖 retire failure。

### 实际复核三个报告触发条件

ROOT 按用户复杂交付规则安排独立只读 audit；本开发会话随后在固定748源码实际复核下列链，未把 agent 意见直接当模型通过：

1. **active 并发反例未成立。** `engine.ts:770–771,908–943` 在初次 job.create await 期间以 `#mainlineComputing` 拒绝另一个 receive；`service:751–797` 已有 accepted 的分支为 active++ → offer → finally active--，中间无 await，ACK 事件不能插入同步段。首次异步 job.create 返回后，设置 accepted/unknown=false、offer、finish、active--也无异步断点。job.get 的 await 只在 payload 已被最后原 ACK 成功退役之后发生；此时不再有那个 payload 的 pending retire 回调。这个排除不依赖 UI busy。
2. **pending token 缺失 / unknown / accepted 缺失反例未成立。** `service:637–659` 的新 token 注册回调后同步加入集合，只有自身回调删除。多 pending 的 ACK 各删自身，最后一个才 release；成功删 token 与 engine 删回调之间没有 await。unknown 只在首次写阶段置位并在首次 offer 前清除；accepted 仅由最后成功 retire 清空，释放异常则原值恢复。重复 ACK 由 engine consumed/IPC accepted 幂等处理。
3. **session/record 变化导致 releaseHolding 抛错反例未成立。** `engine.ts:872–883` 唯一显式拒绝是 entry 不存在或 record 不匹配，**没有 current-session 检查**，注释明确允许旧 owner 清理自己的 holding。onReplyConsumed 在 `1059–1079` 先核同 entry/record/session。payloadEntry 是 intent 私有固定对象，原 budget 捕获固定 record；holding WeakMap 只 get/set、无 delete，已释放则幂等返回。selection fence 释放另一 entry。session 失效在 IPC/consume 前置校验已拒绝，不进入该 retire 回调。

因此不采纳“正常同 operation 并发/session变化已证明可累积16次回调泄漏”的实现级 High 结论；保留**故障注入下产品恢复入口缺口**及未来内部不变量变化风险。没有排除测试替换方法、任意内部状态破坏或未来改动；这些不等于当前命名产品路径的自然触发证据。若指定复审找到遗漏的当前可达反例，按具体反例修复，不要求其预设采纳本判断。

### 不采纳的修复与后续边界

不在 retire 失败后直接退款、删 receipt 或标 consumed；那会违反已采用的“释放失败保原 receipt/holding”，也切断精确重试。不得用 FIFO、frame 销毁、session结束从16槽中无偿移出尚未解决义务，或要求16个真实未解责任存在时第17个仍获准。原128MiB/1048576objects、引用计费、origin 和 noReplay不改。

可行但当前未实施的加固方向：仍有效的原 frame/session 对**同一 deliveryId**做有界私有 ACK 重试，始终保原记录/载荷/别名/计费，不重发 commit/job.create；持续失败仍保留责任并拒绝超额。它不是消除当前已证实自然故障所必需的修改，不为清单自动扩实现；若另决定实施，将产生新候选与全链必要重验。

## MM §4.2–4.4 / Z §3.3：三项延续限制

| 项                         | 实际事实、范围与处置                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| M1 uncertain               | 同 live engine session 一次 timeout/UNKNOWN 后，原 record 无复位，`engine:712–723,1162–1167,2501,2566` 确认主 project/query 受拒。**限制未修复，不称闭合。** session失效后新client/owner可建立；`engine:1408–1515` 真实open+只读恢复以及TaskService原恢复路径仍在。原有效P的job/operation读取不经该mainlineReady；没有P的创建恢复更窄。不同意“所有只读对账或整个App永久不可用”。不能简单清uncertain/自动重放；保持现行受限恢复合同，不新增授权接口。                                       |
| M2 create/example跨session | `project_lifecycle.py:465–470,1027–1032` 原request/origin全等，新session重提创建确实冲突。**创建专属恢复限制仍在，resolution接口不冒称接入。** `job_store.py:1398–1413` 当前许可P/op的marker读取不是全局冲突。原creation合同§2/5/6（43–45,141,167,182,239行）明确新session不可重放create，恢复须重新证明原dispatch物理绑定；缺证保持UNKNOWN。稳定请求指纹/当前许可/同UUID/复制库SQL内容不能替代原物理关联。不同意删origin或新增main持久意图账本；真实目录历史展示与关闭原意图UNKNOWN分开。 |
| M3 16未ACK                 | 原frame/session无法精确ACK的责任可累计至16，届时主project/query容量拒绝；**可达耗尽限制仍在，不称已缓解。** `desktop-ipc:103–104,164` 是明确保留的未ACK责任，accepted缓存只含已消费身份，不可类比FIFO驱逐。health/tasks/job/result/operation不经该容量门。有效原ACK仍可释放；消失的frame/失效session不能凭“对象已不在”造消费证据。保持原上限与计费，不把保护改成无偿回收。                                                                                                                 |

原创建合同 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-host-read-services/docs/iterations/T01/project-create-and-resolution-contract.md`，39602 B / SHA256 `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3`。其未来供方前置不能当当前产品能力。

## 其余意见逐项登记

两报告所有清单项、无法确认项及下述观察均通过原件完整保留。登记不表示每一条已独立运行验证，也不把“未在Top10”当删除。当前未做新测试/构建/产品运行/网络advisory扫描。

| MM项 / Z项   | 处置                                                                                                                                                                                                                                                                                                                    |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MM4.5 / Z1–2 | 正式签名/公证/dir与wholeAPP legal/_distutils欠项保留；内部演示已授权，不采购/改builder。机械包身份不等于正式发布。                                                                                                                                                                                                      |
| MM4.6        | profile缺失模块现不可达，保留维护风险与其降级依据，不删除死分支或实现新能力。                                                                                                                                                                                                                                           |
| MM4.7 / Z6   | 用户备份恢复、损坏SQLite物理HOLD保留，不把迁移备份当恢复实测，不碰库。PRD FR-002项目导出、FR-203 Turtle导入导出、FR-300 CSV/XLSX确是原P0条款；当前未完成，留到相应owner/里程碑，不能把本轮内部子链审查冒称完整MVP。                                                                                                     |
| MM4.8 / Z7   | 跨平台/参考设备/D2/容量未验，不用243行E2E代负载或本机代老设备。                                                                                                                                                                                                                                                         |
| MM4.9 / Z9   | FR-804只要求撤销本次ChangeSet；独立redo/历史选择器未要求，不自动扩功能。undo-of-undo有真实引擎语义，但不称独立redo UI。                                                                                                                                                                                                 |
| MM4.10 / Z10 | 开发nonce编入生产造成字节不复现，生产不启用；测试语料随包、workspace星号、超大文件维护项留账，不为本轮清理。语料内容未逐字安全审查，仍未知。                                                                                                                                                                            |
| MM11 / Z5    | 本体整表+渲染切片与T04服务端查询分页分开；性能/深页容量未知，不扩服务端分页。                                                                                                                                                                                                                                           |
| MM12         | 两处SinkParser无局部1MiB检查的观察保留，不能仅从未调用_parse_turtle推出当前无界外部输入。semantic_scopes接推导分支；query worker固定scope asserted/selected null，query请求有transport总界，_term也在真实query路径使用。尚未证明当前命名入口可传超过上游允许大小的单term，不伪称已证资源攻击；交语义/规模边界后续核验。 |
| MM13–15      | Darwin咨询式RSS、退出75分类、首帧后安装护栏的限制留账；不虚称硬内存隔离/未发生故障。                                                                                                                                                                                                                                    |
| MM16         | 事务内IF NOT EXISTS DDL的schema锁观察留账；无量化性能结论。                                                                                                                                                                                                                                                             |
| MM17 / MM35  | workspace测试专属机制、旧客户端Diff未接生产；保留潜在误接风险，不当当前持久draft或权威Diff。                                                                                                                                                                                                                            |
| MM18         | 渲染投影的影响提示不能替代引擎权威undo-impact/完整Diff；当前提交仍经原权威链，不据提示存在推定写入失真。UX权威性观察留账。                                                                                                                                                                                              |
| MM19         | 历史页替换且无上一页的UX限制留账，不改导航范围。                                                                                                                                                                                                                                                                        |
| MM20         | 当前页CSV防护与N3数据形状、字节界限观察保留；FR-402大数据导出不属普通查询，FR-403要求结果导出，不能推定必须全量/JSON/XLSX。                                                                                                                                                                                             |
| MM21         | action.finally无条件busy=false属实；但同controller的busy仅构造初值/action设置，disconnect不清busy，旧action结束前不能启动新action。当前未证明“旧finally清掉另一个写action的busy”反例，不标已发生并发写；保留未来改动风险。                                                                                              |
| MM22         | 每项目controller Map不清理，长期保留历史风险留账；不能无条件删掉未解决原写责任。                                                                                                                                                                                                                                        |
| MM23–24 / Z8 | 焦点/播报/aria/a11y与错误可行动性欠项保留，无合同/实测不称合规。                                                                                                                                                                                                                                                        |
| MM25–27      | NaN文案、stale read无反馈、无AbortController观察留账；晚响应围栏不等于底层取消，不量化浪费。                                                                                                                                                                                                                            |
| MM28         | 测试profile临时目录保留观察属测试卫生，证据profile不随意删除，不动其他任务进程/文件。                                                                                                                                                                                                                                   |
| MM29–31      | 墓碑/硬删除语义、65536请求id上限、内部异常原值潜在泄露留账；跨边界固定码不被说成已泄露。                                                                                                                                                                                                                                |
| MM32         | 原operation幂等与新operation再撤销不同，ABA/后续编辑冲突保留，不改无条件no-op。                                                                                                                                                                                                                                         |
| MM33–34      | createIntent仅内存限制/内部probe直写潜在误用保留，不建立持久意图账本或扩公开调用。                                                                                                                                                                                                                                      |
| MM36–38      | retired session全局book更新、单飞拒绝、撤销扫描观察保留；未证跨项目错写或量化性能。不改无限排队。                                                                                                                                                                                                                       |
| MM39–41      | changelog/terms/privacy/命名、Python手工冻结升级、弱断言模式观察留账；grep命中弱断言不等于整例无语义断言，不自动批量重写测试/升级依赖。                                                                                                                                                                                 |
| MM42         | 首次丢回复注入在IPC返回腿，不覆盖所有engine→main丢行/主进程崩溃窗口；已获绿只在实际覆盖范围成立，不虚称完整故障空间。                                                                                                                                                                                                   |
| Z5（索引）   | 无显式CREATE INDEX与性能风险留账；“仅主键隐式索引”过窄，format3.py:76,86有UNIQUE(project,event_id)/UNIQUE(project,operation)，SQLite也会为这些约束建隐式索引。不能从无CREATE INDEX断言全部查询无索引；D2需执行计划与规模实测。                                                                                          |

MM§6完整160引用行、20未核项和Z§5各类全部留在报告，不将不适用当已具备。账户/支付/邮件/云/SaaS/模型条目不自动扩成当前功能；人员组织事实不从仓库推断。静态加密/设备失窃、恢复演练、DLQ、保留期、i18n、全屏/表单/导航、advisory、分支保护设置等未核仍未核。MM审查自述做过ls-remote，不能同时称完全无外部请求；报告只读性质与是否发生外部请求分开记录。

## 证据表述更正与外部执行偏离

1. **MM §5 native时间混用。** `03:36:41.542Z/03:36:41.650Z` 是coordinator-exit清理，不是native。真正native原件为 `../20261024_t01_package087_real_runtime_actual_001/frozen-original/native-lifecycle/actual-native.json`，11713 B / `e152a3462ac10b24eb34607015d86ed7fa9b40f7b12778897b438fb27fc611e9`：before-quit seq4 `03:39:00.131Z`、windowclosed seq5/willquit seq6 `03:39:00.143Z`、engine pid33058 exit0 seq7/close0 seq8 `03:39:00.185Z`。由该raw、APP/driver自然0和真实CUA0/0/1/Cmd-Q证明本轮native；历史085 UNKNOWN不改写。
2. **086 count表述。** trace不记录count返回值；pending.count非零依据调用序列与源控制流推断，不能冒称trace直接记录该值。旧tool output ID 8217a5/b5f5a7是会话证据标识，不是缺失文件路径。context关闭时挂起textContent报错不等于关闭动作本身报错。保留旧086 UI未采样/实际失败，不以DB成功代UI通过；748原双谓词/预算未放宽。新增的是evaluateAll回调内显式重复region检测；原locator.textContent本身也有严格多匹配拒绝，没有放宽该验收。
3. **Z“唯一报告写入”与实际UI不符。** 报告写出后，外部ZCode自行写其 `.zcode` 项目memory note（+17）及MEMORY.md（+1），终态UI显示3文件+201。父会话未读/改/删这些memory；产品源/index/规则保护面未变。该执行偏离单列保留，不改原报告自述。后续fresh任务优先用官方可关闭记忆控制或新干净项目容器，仍绑定同规范源并对称提供全部历史；若平台无法关闭则准确声明，不假称唯一写入。
4. **Z whole087子lane失败。** 实际UI两次Explore因并发上限失败，其工作由主会话核验；报告未显式披露该失败。记录此限制，不把failed子lane当完成，也不因此抹掉主会话真实核验。

## 当前决定

产品源码继续固定748；本处置不实施无已证自然触发反例的ACK重试加固，不放宽未ACK/UNKNOWN、origin、计费或noReplay。M1/M2/M3明确仍为现状限制，并非“修好”。其他能力/发布欠项保持原owner与范围。接下来按相同原候选、原运行证据、原清单全文、双方所有已完成历史报告及本处置，交两个fresh独立指定任务重新判断；不把旧MM BLOCK改写为PASS，不用内部agent替代指定模型。
