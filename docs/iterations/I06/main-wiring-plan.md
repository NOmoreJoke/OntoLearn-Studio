# I06 正式 main / bridge / UI 接线阶段

2026-10-21。原Goal/worktree/feature继续；14文件交接已正式生效，仅批准develop5f910b52，未采用I05 C1。字段阶段固定提交a930e11及原归档独立保留，当前接线源码变更不能继承它的验证。契约69dd44d已normal merge为0ce0258；不是完整候选冻结或指定通过。

## 唯一文件责任

根负责约定main index/task-service/engine、preload、renderer App/style（env通过DesktopBridge类型继承，无无意义改动），私有model-gateway服务/配置journal与专属I06测试/文档。契约子线I06-model-contracts仅7个contracts文件及专属test/notes，69dd已交还根。平台子任务仅新tests/i06-main-platform与docs/reviews/I06/main-platform，在自己的worktree准备并等待根固定提交；不借别线可变环境、不写root共享源码。独立审查只读，不替指定双方。

其他Python/入口build/锁/CI/CSP/window-security/window-recovery未移交，必要改动先给总控精确文件/原因。当前Mac不启动GUI/native/HMR/Keychain，不使用CUA/审查应用，Linux仅本线隔离容器。

## 实现

唯一ModelGatewayService由main构造；TaskService仅提供实际选定project identity和切换通知，不使用renderer generation充当授权寿命。每次项目切换新contextId/local默认；窗口恢复仅查询相同服务ledger，绝不重发。index取得同profile单实例锁，避免多个main各持共享配置旧授权；这项仍需实际Electron验证，不把journal CAS当跨进程撤销同步。

配置、密文与metadata审计位于应用私有目录。配置journal严格无secret/授权/payload，每个序号一个固定UUID原子发布槽；实例内串行+跨实例EEXIST竞争，恢复严格链。发布/fsync失败可能已落盘，服务立即停用并取消旧请求，不继续旧grant。密钥录入绑定expected configurationVersion，发布后再检查context/实际配置，endpoint变更不继承密钥。display-only可保留接收身份版本。1024配置变更记录及32配置等硬界显式保留，不无限增长或自动删除不确定记录。

12个专名IPC沿现有main frame/document信任门；strict params/result及绑定校验。10个网关错误用唯一contracts映射，CANCELLED仅独立outcome，未知异常不回传。main methods不进入Python v2Runtime/job/hello；engine.request也主动拒绝它们。初始化失败只停模型，窗口/Store独立启动；退出先关模型/取消、再收尾私有存储、最后停任务/引擎，5秒有界，不承诺可取消同步OS提示或超时前全部写盘成功。

UI默认local；无实际项目禁用，设置不持久保存secret state，password值发出即清空，完整接收配置/主体/版本/所选结果与字段/读取状态/数量预览，明确确认后另按发送。结果仅pre纯文本，独立取消，轮询仅状态/outcome读取。新配置使用独立空串选择，定时刷新不能重置为已有项。

当前正常生产fieldModels=[]、source policy runtime-only，未知producer/字段映射拒绝。可信I04 launchfixture可合成test-runtime，明确modelFieldPolicy literal且非packaged时注入main内置finite policy（实际本应用lockHash），不接受renderer/schema/自报映射；有限A03模型在真实Store/worker+私有应用以及新的named service HTTPS测试中证明，不外推生产业务溯源或CSV全列。可用导出入口在批准基线不存在，实际排除边界只声明engine.sqlite及wal/shm，不虚构导出证明。

## 验证与审查

已完成全应用typecheck r3和46定向：37既存来源/字段、6配置journal、3实际Store/worker→named service→经证书校验HTTPS receiver。加解密为明确safeStorage double，其余密文/配置/审计真实文件；TLS信任只在测试worker内添加生成的synthetic证书，未改主机证书/浏览器安全策略。收集synthetic完整body原件/源结果/preview/grant复用/receipt，无headers或真实凭据。它不是Electron bridge/UI平台通过。

独立审查已修复journal分叉、发布后失败继续旧授权、新配置被轮询重置三项；同profile单实例锁待平台事实。r4完整check仅因React effect lint失败，改为可清理的初始只读timer；随后fixed fixture/严格UTF8/凭据form key/终态缓存完成，r9完整check exit0（998TS、1052Python），sources12/diff通过；代码固定9fcba6634d5c16983c36ef671d4ec8e79694b6d6。正式Linux接线、适用I05批准merge/真实冲突联验、平台事实披露、完整同候选指定双方新审、push/PR/CI/远端核验仍未完成。
