# I06 既存结果可信材料阶段

2026-10-21，接续 `4ace4c4`；现场远端 develop 仍为批准的 `5f910b52`，原 Goal 工具保持 blocked，但按接续授权推进原目标，不重建。AGENTS 两处 SHA `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786` 不变。完整 scope/Goal（含第九节）和当前 parallel-coordination/state 已读回；无额度告警，不兑换或新增支付。I05 未合并源码不作为接口批准依据。

已批准依据：coordinator `_authorize` 对 main 注入 allowedProjects 检查；`project.get` / `result.get` / `job.get` / `result.page` 是真实运行读取方法。result_get 检查实际项目，分页绑定 project/result/inputSnapshot/scope/parametersHash；producer job 返回持久成功状态、resultRef 和版本。当前 schema 没有整结果正文 hash 或字段级 provenance，scope 只是图层。当前真实 producer 只有 test-mode `test.*`，业务 producer 仍 design-only。

## 独立实施与唯一文件责任

- 根只新增 `main/model-gateway/stored-result-source.ts`、`gateway-application.ts`，必要维护同目录 gateway 的私有定向取消边界，新增专属 I06 Store/worker/receiver 测试与 I06 文档。整份结果只读材料从实际 EngineSupervisor 读取，不直接访问项目 SQLite 或新增 RPC。范围/正文/生产者不由 renderer 提供。
- 只读 independent agent 核对批准接口与之后新代码/真实探针，不修改实现。草案 agent 使用新独立 `I06-narrow-interface-draft` worktree / `feature/I06-narrow-interface-draft`（base4ace4c4），只写 narrow-interface-draft.md / narrow-interface-examples.json；不争写根源码。之后正常 merge，不 push。
- I05 继续唯一维护共享 contracts/registry/errors、Store/job、main index/preload/bridge/UI/runtime/entry/build/locks/CI。公共窄接口只是提案，不能注册或假称批准。

## 读取与外发边界

固定 main 项目上下文和 EngineSupervisor；选择输入只有结果 UUID 与 current/historical 选择。读取 project/result/producer job，验证结果引用、输入/参数/图层/定义/依赖/执行版本；默认拒绝历史/过期，显式历史选择保留真实状态。按首次 binding 固定 pageSize 读取全部分页，检查顺序/重复/循环、字节/页数边界；任何失败或回收丢弃所有片段，不能截断。读完重新检查 result/job 与引擎会话，项目关闭/取消丢弃晚到结果。

材料正文包含真实来源 metadata 与整份 rows；本地对实际复制字节计算 SHA-256，只用于内容副本比较。它不是 Store 签发的结果 hash，不授予读取或外发许可。外发范围是 main 签发的不透明整结果材料 scope，不将图层、输入 hash、resultId 或普通摘要冒充字段级授权。派生工具/历史/摘要/错误继承原材料来源并集。

应用服务在预览和每次 invoke 前读回完整来源，拒绝内容或选择身份变化；同一不可变来源可复用 grant。它选择的是结果/输入的不可变材料副本及“读取时状态”，不是 live-current lease。最后异步读回与最终 socket 之间无法原子观察 Store 的 current/删除/权限变化；强实时撤销仍缺少共享 lease/epoch 与全部写入/关闭路径联动，必须披露给正式接线与指定审查，不自行判定为非阻断。

## 真实联验与保留边界

用本 worktree 自有 Python 环境、真实 JobStore/常驻 coordinator/隔离 worker 制备 test.read 结果，经实际只读 RPC 进入新应用服务，使用实际持久 audit 和动态 loopback receiver；覆盖无授权、跨项目、完整多页、历史选择、损坏/回收/错误绑定、项目关闭/定向取消、来源并集及发送失败后的真实 Store.commit 保存。凭据只用合成 double；前阶段实际 Linux safeStorage 证据按原 hash 保留，不重复平台不变测试。本机不启动 Electron/GUI/HMR/Keychain。

此链验证 I04 合成基础设施结果，不能冒充查询/推理/SHACL 或字段级工具结果。真实 I05 语义、正式 main→bridge→UI、可用导出日志排除及窗口失败隔离、其他平台缺口和指定双审仍按原 S3 保留；Q9 真实协议不作为本合成 S3 的自动前置条件。
