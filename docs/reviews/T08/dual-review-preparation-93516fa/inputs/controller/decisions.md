# 本轮授权后的执行决策

日期：2026-10-21（Asia/Shanghai）。用户已答复外部条件“根据你的建议处理”，产品方向“如果你有更好的建议按照你的建议调整”，并明确“发送并落实到现有总控”。据此采用以下具体方案；选择技术方向不表示已获得资源、已验收或已发布。

## 产品方向

- Q3：采用原 PRD 的学习体验优先，企业 POC 用于迁移验证。当前没有足以改变主目标的用户/市场证据；保持贯穿案例和迁移任务的完整验收。
- Q7：采用附录 E 原固定轮次情景推演及原指标，保持逐轮状态、资源处理、幂等、取消和重放要求。
- 57 项 P0、原支持深度与双指定模型审查门禁不变；Q6 最终矩阵须依真实正反例闭合，不能以新模型或日期替代。

## 首发平台

首发目标同时覆盖 **Windows 11 x64、macOS 15 Apple Silicon（arm64）**。构建/验收须固定实际系统版本、构建号、CPU、内存及应用/引擎架构；最终兼容声明按实际验证范围发布，不笼统声称“macOS 15 及所有更高版本均通过”。其他架构不自动进入当前首发兼容承诺，未来需单独验收。

选择依据：覆盖已确认的 Windows/macOS 两个平台，先固定两个明确组合，避免在尚无任何正式安装证据时承诺所有架构。Electron 44 的 macOS 框架最低要求为 13，不等于本产品已支持该版本；原 `macos-latest/windows-latest` CI 也不等于上述精确平台的干净设备验收。见 [Electron 官方变更说明](https://www.electronjs.org/docs/latest/breaking-changes)。

T11 负责落实各目标系统隔离环境，固定构建/安装/离线/凭据/异常恢复/跨设备迁移流程。引擎在对应平台构建，与 Electron 架构一致；用户设备不要求 Node/Python。见 [PyInstaller 官方运行模式说明](https://pyinstaller.org/en/stable/operating-mode.html)。

签名/公证优先使用现有有效身份。macOS 交付需核对 Developer ID、Hardened Runtime、嵌入 Python/动态库签名、公证与最终下载产物；Windows 安装包签名及目标设备安装证据同样保留。身份元数据可检查，私钥不导出、不在聊天中显示。没有身份、公证权限或签名资源时记具体发布阻塞，不能用未签名目录包冒充正式上线。见 [Apple 官方公证说明](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)。本轮没有授权购买新证书/账号或支付费用。

## 首选真实模型服务

Q9 的首选技术方向为 **DeepSeek 官方 API + Chat Completions + `deepseek-v4-pro`**，Base URL 为 `https://api.deepseek.com`。官方本轮资料将其列为 DeepSeek-V4-Pro-0813，提供 JSON Output、Tool Calls 与思考/非思考模式。服务别名不是不可变权重或 snapshot 保证；必须记录实际受测日期、endpoint、请求模型、返回标识、可得服务版本与模式，发现漂移重验。见 [官方模型表](https://api-docs.deepseek.com/quick_start/pricing/)。

这是适配器与验收准备的选型，不自动配置、启用或调用服务。先由总控核验既有 API 主体/权限、批准的可消费额度与网络条件；ChatGPT/ZCode/MiniMax 订阅不当作该服务 API 权限。不得搜索/打印密钥或擅自开户、充值、购买；新增费用有具体金额与上限后才可授权。若现有授权资源缺失，先完成适配和合成探针，保留真实服务验收阻塞，不假称已打通。

正式思考模式通过原版本化评估集验证后固定。非思考模式可用于最小协议探针，不能因为节省实现时间就宣称等效质量。若只有思考模式满足原质量门槛，正确实现其多轮工具字段/取消后保留该模式。能力探测包括连接、结构化输出和工具调用，JSON/schema 由应用端严格校验；空内容/不合法工具参数/异常/超时不产生正式写入。不得把 JSON Output 或 Beta strict schema 当作取消应用端校验的理由。见 [JSON Output](https://api-docs.deepseek.com/guides/json_mode/) 与 [Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)。

模型选择不改变确定性引擎、工具白名单、用户确认 Diff、最终字段授权和零伪造固定评估要求。模型结果不决定业务计算真值。

## 用户验收与资源安排

采用 10 月 24 日周六安排至少 5 名未参与开发、缺乏本体经验的真人新用户完成原测试方案；至少 80% 依靠产品引导完成核心案例，分别记录独立、部分提示、完整示范、迁移任务与 Agent 代做路径。AI/开发者不得代替真人验收或将辅助完成计入独立成功。

总控现在准备脚本、数据重置、用户说明、观察表、时间窗口与招募名单需求。当前尚无实际测试者名单、预约或真人结果；不能记为资源已落实。向外发邀请/联络需明确发送授权与具体收件人，费用亦须有金额授权。本轮不自动向任何人发送邀请。

## 当前责任和证据边界

原执行总控 `01a154de-843b-7a00-8a80-51ba1c0aebce` 已实际收到计划，并回执确认新范围、继续 I05/I06 与开始派发不争写的准备任务。真实任务/负责人/分支和验收脚本仍以其进一步回执及状态为准。

上述技术推荐经独立 agent `/root/release_decisions_review` 只读复核，使用官方资料；未修改产品实现、未启动 GUI、未读取凭据、未发模型请求或付款。已决定的是目标矩阵、首选协议/服务和验收安排；尚待证明的是资源可用与全部实际验收。

## 来源传输的工程保护值（总控技术采用，非 Q5 容量结论）

依据固定T01 33a5590来源生命周期r3及独立[source生命周期审查](source-lifecycle-r3-design-review.md)（SHAe95cadb6c655749e36b64b196e0aa71185dff5213be403f80b33a3f737c51846），总控在工程保护范围采用256个attempt记录（含tombstone）和256MiB source逻辑encoded载荷预算；原1个未结begin、2个未接纳lease/16MiB raw、30秒idle/120秒total/600秒sealed方向保留。数值尚未实测，不回答PRD Q5、目标机体验或物理disk/WAL/RSS达标。

采用条件是唯一canonical/owner固定完整状态、有限错误、预留/实账/回收与重启重建；unknown、清理未settled、accepted/pinned和必需历史均计账，满额仍可status/release/barrier及服务既有消费者，不通过重建对象逃账或删除历史。展开表/结果/元数据与物理副本另有明确保护，不用该数字替代。终态字节已清理只能回权威终态/拒绝，不能伪造逐bytes核验成功ack；该R1已实际交T01修订。已有claim先当前项目认证并匹配原完整请求，精确只读对账不要求旧lease今天活跃；首次新admission继续有效proof/确认/CAS。公共source方法及业务ready未由此启用，完整实际验证/指定双审/CI/merge门保持。

## Q6 用户正式采用

2026-10-21T11:39:10.143678+08:00，用户对已独立审查的具体决定单明确回复“采用决定单的推荐规则与规范版本”。采用原 SHA 328a59c42ae69a5c2426c494c1c979cb629692f389cdacf591e8789738c6b4f0 的完整规则与固定 REC pin；原字节保全、实际问题来源和回执见 Q6-user-adoption-receipt.json。新增规则应用 profile 与 query/SHACL 各自合同分开；未支持格、原 FR-504/505、完整解释/生命周期、真实来源/包内/双审/CI/合并验收均保留。实施仍按原 owner 精确文件责任与分阶段验证推进，不从采用决定推导实现或运行通过。

## 2026-10-22：SHACL date与SQLite输入域

用户明确选择保留损坏数据库物理资源保护，维持HOLD；不采用仅受控物理良构库的A合同，也未授权B/C实施。SHACL date按推荐采用有限UTC扩展：合法`YYYY-MM-DDZ`、年份0001–9999，inclusive相等通过，其他时区或不兼容混合类型明确拒绝。该选择独立于已采用Q6，不改变其规则或规范pin。完整设计边界及原答复见[本次决定](SHACL-date-and-SQLite-user-decisions-20261022.md)；设计选择已确认，产品实现与验收仍按原owner和实际证据推进。
