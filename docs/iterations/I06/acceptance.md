# I06 验收映射与接口需求

需求不因独立阶段缩减。主开发工作树 `.worktrees/I06-model-gateway`；正式完成状态和验证结果见 [status](../../reviews/I06/status.md)。

## 已实现核心与测试对应

| 依据                              | 核心检查/实际专属反例                                                                                                                                              |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| S3、FR-902、附录 F、G.5 A-03/A-04 | 无授权、额外自由正文/headers、不同用途、跨项目 handle、scope 越界均拒绝；工具/历史/摘要/错误逐类检查；派生来源并集；正文不执行授权指令                             |
| S3、G.5 A-05                      | 完整 URL 规范化、拒绝 userinfo/query/fragment/空 query/空 fragment/反斜线/控制符；更改 URL/主体/凭据版本/模型/新配置身份拒绝旧授权；回改也不复活；同规范地址可复用 |
| FR-902、附录 F                    | 默认完全本地；预览后改模式、凭据读取期间切本地/撤销/改配置、审计 await 之后及 TCP 接收前竞态阻断；已开始连接的取消不等于撤回数据                                   |
| S3 重试/重定向                    | 动态端口本地假接收端实际 POST；301/302/303/307/308 不跟随，第二接收端零请求；503 可有界重试，切本地后不重试，上游错误正文不加到下一请求                            |
| FR-901/904                        | 密钥不在授权返回值；密文仓库适配器只接收密文；不可用/basic_text/unknown/加解密/读写异常拒绝并固定错误；metadata 字段白名单，不含业务/密钥/模型正文                 |
| FR-902/904                        | 相同 grant 两次请求完整正文与预期一致；发送前 intent 写失败零请求；内部材料/总正文、响应字节和等待时间有界                                                         |

测试只使用合成数据。端口由 server.listen(0, '127.0.0.1') 专属分配并及时关闭，不启动产品 HTTP 服务。上表原核心单测使用凭据 doubles、不启动 Electron；新增 [实际 Linux 组合探针](platform/combination-isolated-probe.md) 在独立断网容器运行真实 Electron/safeStorage/私有仓库/持久审计/transport，有单独运行产物及来源摘要。内部资源保护数值不是 Q5 容量指标。

凭据身份追加反例：仓库主体/版本篡改、交换另一条有效密文、仓库 binding 额外字段均拒绝；解密内容为旧 raw-key、坏 JSON、未来内部格式、顶层或 binding 未知字段、非法 secret 时拒绝，无宽松兼容回退。四项身份反例已在旧实现实际失败，修复后的完整严格信封测试通过；详见 [凭据绑定内审](../../reviews/I06/credential-binding-review.md)。

等待/资源反例：受控时钟验证凭据及持久审计 promise 卡住后到期拒绝且接收端零请求；凭据恢复可复用未变化授权。四个等待占满时第五个请求不增加凭据读取、取消后容量可用。持续 503 完整断言两次相同请求后失败。真实 socket 假接收端读完请求但不响应时，总时限终止且只有一次接收，没有网络异常自动重放。这里只验证基础设施故障和内部保护上限，不证明业务容量或真实模型协议。

## 已接线边界与完整验收待办

以下接口以 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6` 为基线；当前产品 `e2c269ad78a78e1a042cadc93b1c81a874707153` 仅修改模型提示 ARIA。批准依赖仍为 develop `5f910b52`，不采用未批准 I05 候选；已实现、静态检查及分版运行证据分别记录。

- 当前共享契约已注册 12 个 main-only 专名方法、严格 params/result/reply 和请求响应身份绑定，owner=main、agentEligible=false，不进入 Python 方法表。scope 由 main 的实际整结果或有限字段模型建立；私有 zod 不充当第三份公共协议。有限模型为固定合成 policy + 批准 test.read echo worker，static dependsOn 不是生产溯源，普通生产 models=[]/runtime-only，未知 shape 拒绝。
- 早期 11 类需求见 [公共错误映射交接](public-error-requirements.md)，保留其历史；当前开发契约已落为 10 个固定 GATEWAY_* 错误和独立 cancelled 结果。公开 configurationVersion 为持久配置/UI/录入 CAS 版本，内部 core configVersion 为 grant/preview/audit 绑定版本，两者独立生成，不能写成同一 UUID。
- 已基于批准 I04 真实只读接口实现 StoredResultSource/GatewayApplication 与有限字段投影：材料来源必须从实际项目/结果/版本和完整重读派生。工具隐式读取、跨项目缓存、历史/摘要完整上下文不能自报降权；任意 text 无法证明字段来源即拒绝，失败/过期/缺失依据传安全事实。公共能力注册表不把凭据/发送塞入 Python。A-03 私有链按原 source hash 保全，9fc 正式 main source normal22 的实际字段授权/复用/完整 public-only body 已在 [source 回执](../../reviews/I06/main-platform/source-and-native-review.md) 核验；不外推 e2c 的模型完整平台链。
- main 已复用 I02/I04 可信 sender/mainFrame/document 与固定命名桥接，持有项目 context/有限调用 ledger，UI 重建只查询结果，不自动确认或重放。精确 14 文件责任已交接并完成开发接线；9fc normal22/native4/pkg2 各自限定范围通过；实际依赖批准合并后的刷新/冲突处理与完整同候选指定双方新审仍需完成。
- 已完成私有 POSIX 密文仓库、持久 metadata-only 审计、实际 Electron factory 和隔离 Linux 组合；开发分支已接入产品 main 初始化/退出和设置/录入 UI。9fc 正式 source/包内的项目与普通日志扫描、停止后存储原件读回按对应 receipt 范围验证，不把原件子集称为重扫全部对象或贴给 e2c；当前无导出入口，不能虚构导出测试。Linux 受测 backend/失败边界以组合证据为准；其他平台/Windows ACL/锁定/签名升级/干净设备不扩大通过。
- FR-806：私有链已有同 coordinator 的真实 Store 保存证据；模型初始化失败隔离、单 profile owner 和 5 秒退出等待已接线，9fc normal22 已实际验证 audit/初始化失败不阻断真实 Store 提交，native4/pkg2 的 crash 恢复核对 Store/ledger/outcome 不变且不重发；各自限定回执不替代 e2c 全矩阵，也不用 mock 保存代替。
- FR-006/304/703/705/804、附录 C/D/E/G：不改领域失效、原子 ChangeSet、历史和场景语义；正式接入核对模型配置只撤销外发授权，不产生领域 staleReason。显式历史选择已被 PRD 允许，current 不静默降级；完整重读到 socket 仍有跨 Store 观察窗口，原 S3 不要求全写者/socket 原子 live-current lease。只有真实语义特定材料依赖 I05 新语义实际批准合并，不因其编号阻塞无关模块；有限 A-03 不要求全 M1 CSV 溯源或恰好两个公共 API。
- 当前合成 `{model,parts}` 与响应经过严格 UTF-8/实际字节上限检查，再以纯文本向 UI 展示，不声明真实 provider、结构化输出或工具调用成功。Q9 真实 provider 协议选择另验，不作为既定合成 S3 的自动前置。
- 当前桌面禁用 GUI/native/HMR/外部审查应用自动点击。9fc [normal22/native4](../../reviews/I06/main-platform/source-and-native-review.md) 和 [真正包内 pkg2](../../reviews/I06/main-platform/packaged-and-regression-review.md) 在独立 Linux 容器完成，唯一额外 SYS_ADMIN/default seccomp 环境不称默认 Docker。e2c 全量 check 为 998 TS/1052 Python、sources12 通过；新构建 source/package 原 e2e 各 3pass/3默认 fixture skip，六项独立 fresh-fixture 定向原用例实际执行。aria2 首次 10 门 9 过，source native 首次超时失败后仅一次同 image/新容器/新 fixture 原用例复验通过；原 phase=30 秒、trace≈12.25 秒差异原因未知，不称一次全绿。详见 [ARIA 回执](../../reviews/I06/main-platform/aria-regression-review.md)。旧9fc模型/凭据专项不贴新代码；其他平台、I05实际批准/新语义绑定、完整指定双审、PR/CI/远端合并仍待完成。

## 内审意见处置

独立 agent `/root/i06_design_review` 第一轮设计审查（只读）提出八类边界：材料可信来源、冻结字节、socket竞态、审计持久失败、凭据身份、派生来源、重试/撤销、平台验证。采纳前七类形成代码/专属测试与上述集成条件；第八类在该早期记录中仅完成适配器和反例测试；之后已有按各自 source hash 固定的私有 Linux、9fc 正式 normal/native/包内专项及 e2c ARIA 回归证据；上述限定结果不等于完整 S3 或指定双审通过。实现复核发现无关配置全局取消与旧审计目标丢失，均采纳修复；最终只读复核明确两项关闭、未发现新增阻断，实际重跑网关 50/50。详细来源与边界见 [内审记录](../../reviews/I06/internal-review.md)，不替代指定双审。
