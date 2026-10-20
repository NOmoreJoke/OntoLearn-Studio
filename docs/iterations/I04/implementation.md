# I04 S2 实施与验证边界

采用已合并 I03（e45e6038）作为设计基线；唯一目标为常驻协调器和 ExecutionJob 基础设施。完整派发输入与门禁来自仓库外总控 I04-launch-prompt.md，执行进度、失败和候选身份见 [status](../../reviews/I04/status.md)。

## 实际职责

- Electron EngineSupervisor 管理一个常驻 stdio 子进程、hello、原始 registry 字节 SHA、pending/代次/控制心跳与有限退避。主进程应用服务掌握当前授权项目及可丢视图上下文，preload 仅有业务命名方法；renderer 无任务创建、路径或通用 invoke。
- Python 单协调器持有 OS 排他 writer lease。JobStore 与 S1 使用同一个 SQLite 和事务；worker 没有数据库或正式提交入口，只返回隔离计算输出。父死亡守卫避免旧 worker 占用资源继续运行；新协调器取得 lease 后再按持久 marker/round/terminal 对账，不续跑或重发写入。
- 主进程和协调器分别用显式最小 OS 环境启动 Python 和 worker，不继承宿主凭据、代理、loader/Python 注入变量；DB、项目授权和测试模式只由主进程可信配置生成，worker 不继承这些权限变量。真实自造 sentinel 与包内启动均有验证。
- operation claim 全局唯一，完整项目/能力/input/confirmation/plan/参数内容/依赖/实现/limits 固定；公开项目身份通过持久双向唯一映射与旧内部 ID 对齐。正式 receipt 为历史结果，不能成为领域 current。
- 队列、并发、项目 writer、请求/总量/启动/握手/心跳/取消收尾、帧/页/游标记录与内存分别有界。总期限包含排队、启动、stdin 写入、计算、等待退出与提交前复验，不由心跳延长。单任务取消仅终止对应 worker。
- 结果及列表使用 SQLite 持久的不可变载荷/固定集合与 UUID 游标；每次复验项目/输入/范围/参数/页大小/TTL/载荷，过期与回收不返回成功空页。依赖与定义集合由可信快照派生，发布/失效与正式提交同事务。

## 契约修订

I03 未握手错误设计需要非 hello 的 null-session 错误响应，而旧 schema 仅 hello 允许 null。新增一条严格分支，仅 HANDSHAKE_REQUIRED 或 VERSION_INCOMPATIBLE；所有成功、其他错误及通知的身份约束未放宽。未握手门在已知方法的 params 校验之前；未知/畸形 method、重复 ID 和坏原始帧关闭会话，不反射未知信封。公共双端正反例覆盖 null 成功、null 内部错误、null 参数错误拒绝。

R2-F1 在双端校验 trusted binding 的完整身份、数值类型/范围和合法状态，缺字段不默认值、不逃出 KeyError/TypeError。保留原24个内部 binding 变异，与合法公共通知及合法控制组分开。共享原始帧语料覆盖 UTF-8 每个拆分点、粘包/CRLF、嵌套重复/转义同名键、深度、数值、非法 Unicode、追加前限制、终止后丢弃；已完成帧先于坏帧的边界保留。

唯一规范与 Python 适配器显式纳入 PyInstaller，锁来源也以实际 uv.lock 原字节打包；主进程读取同源 registry 预期并核验返回 SHA。资源清单和公共例 CLI 在临时工作目录执行，不能借源码 checkout 找回资源。I05 未合并 hooks 不提前复制，后续其 probe/collect-all/metadata/inventory/license 必须与本线 hooks 合并承接。

## 安全错误与 UI

只接受本地 ServiceFault/JobFault/结构化 S1 Conflict，SQLite 按真实 errorcode 主码分类；未知来源异常统一 INTERNAL_ERROR，不能自报 code/params 或借异常文本归责。普通入口初始化异常也只有固定有界 stderr。四字段 DTO 保留至窄 bridge，UI 用固定本地模板组成“发生什么/原因/修复/相关知识”；retryable 不触发自动重放。取消、失败、状态待对账、历史、过期与不支持分别表达。

## 测试任务与未完成业务

仅显式可信测试启动可创建 test.read/test.atomic/test.rounds，hello/productRuntime 不宣称测试任务或未实现业务能力。rounds 是真实 worker、真实 Job/Store/轮次快照/消费证据和 result.get/page 的基础设施负载，使用 I04-test-rounds-v1，不能当 E.2 全阶段执行器、E.5/G.4 工单集合/产能/指标/重放或 FR-704 业务结果页完成。

F6 摘要从最后持久轮次及完整终态产生，队列为空仍跑至配置 maxRounds，不另加提前停止规则。零轮失败/取消不造成功摘要；部分轮次保留为失败/取消历史。摘要只在首个非游标页，缺失/矛盾/畸形/回收均不能显示全部完成。

## 平台资源边界

Linux 使用 RLIMIT_AS，Windows 使用 JobObject 进程内存限制；Darwin 本机实测不能使用这些 rlimit，采用 libproc RSS 采样与受控分配前预算。Darwin 不是硬分配上限，存在采样间超量边界，仅支持当前有界测试负载，不批准未来语义原生库。各平台测试结果必须分别记录。

用户 Mac 桌面不运行 Electron/native/HMR；开发包生成不自动启动。Linux Docker 虚拟显示可执行真实可见、焦点、崩溃/无响应和实际提示框，不禁 sandbox/hang monitor、不 stub 提示。arm64 容器不冒充 CI x64，也不代替签名、干净设备或生产验证。I01 R6 历史增长原等级开放/延期，未引入无证据优化或性能提升承诺。
