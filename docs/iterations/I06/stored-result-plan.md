# I06 既存结果可信材料阶段

2026-10-21，接续 `4ace4c4`；现场远端 develop 仍为批准的 `5f910b52`，原 Goal 工具保持 blocked，但按接续授权推进原目标，不重建。AGENTS 两处 SHA `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786` 不变。完整 scope/Goal（含第九节）和当前 parallel-coordination/state 已读回；无额度告警，不兑换或新增支付。I05 未合并源码不作为接口批准依据。

文档纠偏（2026-10-21）：保留以上接续 checkpoint 与旧证据。明确历史选择是 PRD 附录 D/F 已有语义；跨写者/socket 的持续 current lease 不是原 S3 自动前置。A-03 可用有限真实结构化 Store/worker 输出+main 可信字段模型/投影+actual receiver 字节反例证明，不要求全部 M1 CSV/单元格溯源、特定两个公共 API 或 I05 先合并。

已批准依据：coordinator `_authorize` 对 main 注入 allowedProjects 检查；`project.get` / `result.get` / `job.get` / `result.page` 是真实运行读取方法。result_get 检查实际项目，分页绑定 project/result/inputSnapshot/scope/parametersHash；producer job 返回持久成功状态、resultRef 和版本。当前 schema 没有整结果正文 hash 或字段级 provenance，scope 只是图层。当前真实 producer 只有 test-mode `test.*`，业务 producer 仍 design-only。

## 独立实施与唯一文件责任

- 根只新增 `main/model-gateway/stored-result-source.ts`、`gateway-application.ts`，必要维护同目录 gateway 的私有定向取消边界，新增专属 I06 Store/worker/receiver 测试与 I06 文档。整份结果只读材料从实际 EngineSupervisor 读取，不直接访问项目 SQLite 或新增 RPC。范围/正文/生产者不由 renderer 提供。
- 只读 independent agent 核对批准接口与之后新代码/真实探针，不修改实现。草案 agent 使用新独立 `I06-narrow-interface-draft` worktree / `feature/I06-narrow-interface-draft`（base4ace4c4），只写 narrow-interface-draft.md / narrow-interface-examples.json；不争写根源码。之后正常 merge，不 push。
- I05 继续唯一维护共享 contracts/registry/errors、Store/job、main index/preload/bridge/UI/runtime/entry/build/locks/CI。公共窄接口只是提案，不能注册或假称批准。

## 读取与外发边界

固定 main 项目上下文和 EngineSupervisor；选择输入只有结果 UUID 与 current/historical 选择。读取 project/result/producer job，验证结果引用、输入/参数/图层/定义/依赖/执行版本；默认拒绝历史/过期，显式历史选择保留真实状态。按首次 binding 固定 pageSize 读取全部分页，检查顺序/重复/循环、字节/页数边界；任何失败或回收丢弃所有片段，不能截断。读完重新检查 result/job 与引擎会话，项目关闭/取消丢弃晚到结果。

材料正文包含真实来源 metadata 与整份 rows；本地对实际复制字节计算 SHA-256，只用于内容副本比较。它不是 Store 签发的结果 hash，不授予读取或外发许可。外发范围是 main 签发的不透明整结果材料 scope，不将图层、输入 hash、resultId 或普通摘要冒充字段级授权。整结果范围不能替代 A-03 字段授权；派生输入来源并集本身也不证明任意正文来源。有限字段投影阶段须基于固定 main-owned producer shape 模型和实际完整 body rows，签发绑定模型版本/项目/结果/输入/副本的 opaque field IDs；renderer 只选 IDs。工具/历史/摘要/错误只从结构化允许字段重建，未知/嵌套/不符形状或无法证明来源的任意 text 拒绝，不做自然语言污染分析。此为实施边界，具体私有 API 待实际实现后对齐，不声明已通过。

应用服务在预览和每次 invoke 前读回完整来源，拒绝内容或选择身份变化；同一不可变来源可复用 grant。它选择的是结果/输入的不可变材料副本及“读取时状态”，不是 live-current lease。最后异步读回与最终 socket 之间不能原子观察另一个 Store 进程的变化，必须披露该窗口及实际保守拒绝行为给正式接线与指定双方。PRD 已允许明确选择不可变历史输入，发送内容需标明实际 version/read-time-state/历史，不能静默降为历史；原 FR-902/S3 没有要求所有 Store 写者与 socket 原子锁住，因此缺少持续 current lease 或历史语义的再次批准不作为原验收自动阻断。若以后承诺更强“发送瞬间始终 current”/实时撤销，才另审共享 lease/epoch 与全部写入/关闭路径协调；现有 hash/最后一次异步读不证明该更强保证。

## 真实联验与保留边界

用本 worktree 自有 Python 环境、真实 JobStore/常驻 coordinator/隔离 worker 制备 test.read 结果，经实际只读 RPC 进入新应用服务，使用实际持久 audit 和动态 loopback receiver；覆盖无授权、跨项目、完整多页、历史选择、损坏/回收/错误绑定、项目关闭/定向取消、来源并集及发送失败后的真实 Store.commit 保存。凭据只用合成 double；前阶段实际 Linux safeStorage 证据按原 hash 保留，不重复平台不变测试。本机不启动 Electron/GUI/HMR/Keychain。

整结果链验证 I04 合成基础设施结果，不能冒充查询/推理/SHACL，也不能单独算 A-03 通过。后续有限字段模块可在这条真实结构化 Store/worker 链上验证：工具返回包含选中字段与其他列的标记，actual receiver 对最终完整请求 bytes 断言其他列/其派生值零外发，同时拒绝伪造字段、跨模型/版本和任意 text。完成该实际证据即可作为 M0 A-03 的有限证明，不以全部 CSV/单元格来源或 I05 为前置；真实 I05 特有语义之后另验。正式 main→bridge→UI、可用导出日志排除及窗口失败隔离、其他平台缺口和指定双审仍按原 S3 保留；Q9 真实协议不作为本合成 S3 的自动前置条件。
